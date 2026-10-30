"""
新闻原始来源档案模块(IA-P0-2-W3)
================================

W3目标: 任何进入新闻摘要或周报引用链的真实文章,都能追溯到实际采集的
原始来源记录;原始数据不被脱敏/分类/截断/模型摘要污染。

职责(W3-01/W3-03):
  * 来源记录规范化(normalize_record)——字段显式区分,不得互相代替;
  * 稳定 article_id(确定性SHA-256,同文章重跑同ID,幂等);
  * 批次身份与归档(save_batch)——news_sources_YYYYMMDD_HHMMSS.json,
    同日重跑新批次,旧批次永不覆盖/删除;
  * 独立日清单(news_sources_manifest_YYYYMMDD.json,追加式)——档案文件
    SHA-256记入清单,档案自改可被检出(自我认证不可作为唯一依据);
  * 逐记录确定性SHA-256(record_sha256)与档案完整性验证(verify_archive);
  * 来源记录读取(load_day_records/load_records_since);
  * 来源引用验证(verify_citation/extract_citations);
  * 周报来源索引构造与写入(build_refs_index/write_refs_index);
  * 派生展示视图(derive_display)——截断只允许发生在派生副本。

时间语义(W3-02 §6.3):
  * Finnhub datetime 为Unix纪元秒(UTC语义)→ datetime.fromtimestamp(
    epoch, tz=timezone.utc),与进程本地时区无关;
  * RSS published_parsed(feedparser)为UTC结构化时间 → calendar.timegm
    (按UTC解释),严禁 time.mktime(按本地时区解释,结果随时区漂移);
  * 缺发布时间 → published_at_utc=None + published_status='UNKNOWN',
    绝不用采集时间/当前时间冒充,不造假时间。

本模块只用Python标准库,不导入网络客户端/密钥——离线测试可直接使用。

IA-P0-2-W3-FIX1(独立验收失败后增量整改):
  * FIX1-01 批次不可覆盖: 批次身份追加全局唯一段(uuid4),档案文件排他
    创建('x'=O_CREAT|O_EXCL),碰撞→换新身份重试,绝不覆盖;日清单在
    flock排他锁下读取-修改-写入并以tmp+os.replace原子落盘;清单损坏→
    先原样保全为.corrupt-*副本再重建(记recovery_note),绝不静默当空
    清单覆盖;清单阶段失败→保留已写档案并抛明确诊断,不自动销毁批次。
  * FIX1-02 引用以原始档案为可信根: verify_citation降级为索引成员诊断;
    新增verify_citation_trusted/load_trusted_articles_since——消费时逐
    批次实际核验(档案存在→清单条目→文件SHA-256→逐记录摘要→ID映射),
    仅通过认证的记录进入可信来源集合;build_refs_index同样验证门控
    (坏批次记录不进入articles,不只留告警)。索引是派生视图非原始证据。
  * FIX1-05 跨通道同文章关联: 新增logical_article_id(供应商文章ID>URL,
    标题不参与防误并);article_id规则不变(旧引用不失效),新字段纯增量。
  * FIX1-06 模型可见派生文本数据化: sanitize_model_text只作用于发往
    模型的派生副本(标题/发布方/URL),原始档案永不处理。

序列化与摘要规则(W3-03 §7.3,确定性):
  * record_sha256 = SHA-256( json.dumps(record剔除record_sha256/batch_id/
    retrieved_at_utc后, sort_keys=True, ensure_ascii=False,
    separators=(',',':')) )——文档化于 RECORD_DIGEST_EXCLUDE;
  * 档案文件整体SHA-256由清单记录(file_sha256),对档案文件字节计算;
  * 摘要在**归档写入前**生成并随记录持久化,清单为独立文件(单独批次清单)。
"""

import calendar
import fcntl
import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone

SCHEMA_VERSION = 1

# 进入record_sha256的字段集=规范化记录全体字段,除下列运行期字段
RECORD_DIGEST_EXCLUDE = ('record_sha256', 'batch_id', 'retrieved_at_utc')

# 稳定引用ID提取模型/报告文本中的 [art_xxxxxxxxxxxxxxxx]
CITATION_RE = re.compile(r'\[(art_[0-9a-f]{16})\]')

# FIX3-01: 正式新闻条目行首引用槽位——单行以'- [art_xxx]'开头且ID后
# 紧跟空白或行尾(^\s*不允许:条目必须顶格;ID后必须断词)
NEWS_ITEM_RE = re.compile(r'^-\s+\[(art_[0-9a-f]{16})\](?=\s|$)')


# ───────────────────────── 时间语义(UTC确定性) ─────────────────────────

def now_utc_iso():
    """当前UTC时刻(ISO8601 Z后缀)。仅用于批次/采集时间戳。"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def epoch_to_utc_iso(epoch):
    """Finnhub Unix纪元秒(UTC语义)→ISO Z。非法/0/None→None(不造假)。"""
    try:
        epoch = int(epoch or 0)
    except (TypeError, ValueError):
        return None
    if epoch <= 0:
        return None
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime(
        '%Y-%m-%dT%H:%M:%SZ')


def rss_parsed_to_utc_iso(parsed):
    """feedparser published_parsed(UTC结构化时间)→ISO Z。

    calendar.timegm 按 UTC 解释 struct_time——正确;time.mktime 按进程
    本地时区解释同一结构,结果随TZ漂移(W3问题3根因),禁止使用。
    """
    if not parsed:
        return None
    try:
        return datetime.fromtimestamp(calendar.timegm(parsed),
                                      tz=timezone.utc).strftime(
            '%Y-%m-%dT%H:%M:%SZ')
    except (TypeError, ValueError):
        return None


# ───────────────────────── W3-01 记录规范化 ─────────────────────────

def normalize_record(raw, retrieved_at_utc=None):
    """采集原始字典 → 规范化来源记录(显式字段,不得互相代替)。

    raw 约定(采集层产出,字段保全 W3-02):
      provider: 'Finnhub'|'RSS' (数据供应商/渠道)
      channel:  'market_news'|'company_news'|'rss'
      publisher:            原新闻发布方(Finnhub source)
      feed_name/feed_url:   RSS Feed身份(仅RSS)
      entry_id:             RSS entry.id/guid(仅RSS,如提供)
      watch_symbol:         请求证券代码(仅个股新闻)
      provider_article_id:  供应商文章ID(如提供)
      related:              供应商related原文(如提供)
      headline_original/summary_original/url_original/published_raw
    """
    provider = raw.get('provider') or 'UNKNOWN'
    channel = raw.get('channel') or 'UNKNOWN'
    headline = raw.get('headline_original', '') or ''
    summary = raw.get('summary_original', '') or ''   # 归档前禁止截断
    url = (raw.get('url_original') or '').strip() or None
    # RSS条目通常无独立发布方字段——Feed身份即原发布方(CNBC/Bloomberg)，
    # 以feed_name作为发布方记载(显式可追溯,不冒充Finnhub式source字段)。
    publisher = (raw.get('publisher') or '').strip() or \
        ((raw.get('feed_name') or '').strip() if provider == 'RSS' else '')

    # 发布时间: 来源实际发布时刻(独立保存),缺失→UNKNOWN
    if provider == 'RSS':
        published_at = raw.get('published_parsed_utc') or None
    else:
        published_at = epoch_to_utc_iso(raw.get('published_raw'))
    published_status = 'UTC' if published_at else 'UNKNOWN'

    missing = []
    if not url:
        missing.append('url')
    if not headline:
        missing.append('headline')
    if not publisher:
        missing.append('publisher')
    if published_status != 'UTC':
        missing.append('published_at')
    provenance_status = 'COMPLETE' if not missing \
        else 'PARTIAL:' + ','.join(missing)

    rec = {
        'schema_version': SCHEMA_VERSION,
        'article_id': stable_article_id(raw),
        'logical_article_id': logical_article_id(raw),
        'provider': provider,
        'channel': channel,
        'publisher': publisher,
        'feed_name': raw.get('feed_name') or '',
        'feed_url': raw.get('feed_url') or '',
        'entry_id': raw.get('entry_id') or '',
        'watch_symbol': raw.get('watch_symbol') or '',
        'provider_article_id': str(raw.get('provider_article_id') or ''),
        'headline_original': headline,
        'summary_original': summary,
        'url_original': url,
        'published_raw': raw.get('published_raw'),      # 来源原始时间值原样
        'published_at_utc': published_at,
        'published_status': published_status,
        'retrieved_at_utc': retrieved_at_utc or now_utc_iso(),
        'provenance_status': provenance_status,
    }
    if raw.get('related') is not None:
        rec['related_original'] = raw.get('related')
    return rec


def _identity_key(raw):
    """稳定身份键: 供应商ID > URL > (发布方+标题+原始发布时间)。

    同一文章重跑得同一article_id(幂等);同标题不同URL是两条独立来源
    (F: URL参与身份,标题不单独决定身份)。
    """
    provider = raw.get('provider') or 'UNKNOWN'
    channel = raw.get('channel') or 'UNKNOWN'
    pid = str(raw.get('provider_article_id') or '')
    url = (raw.get('url_original') or '').strip()
    if pid:
        return f'{provider}|{channel}|pid:{pid}'
    if url:
        return f'{provider}|{channel}|url:{url}'
    return (f'{provider}|{channel}|gen:'
            f'{(raw.get("publisher") or "").strip()}|'
            f'{raw.get("headline_original") or ""}|'
            f'{raw.get("published_raw")}')


def stable_article_id(raw):
    """确定性稳定引用ID: art_+SHA-256(身份键)前16位十六进制。"""
    h = hashlib.sha256(_identity_key(raw).encode('utf-8')).hexdigest()
    return 'art_' + h[:16]


def logical_article_id(raw):
    """跨通道底层文章身份(FIX1-05): lart_+SHA-256(逻辑键)[:16]。

    逻辑键: 供应商文章ID > URL(均含provider前缀);**标题不参与**(防同题
    误并)。同一Finnhub文章从market_news与company_news两通道返回时,
    article_id(含通道,不变)不同但logical_article_id相同→确定性关联;
    不同真实文章(不同pid/URL)不会误并。无pid且无URL→None(不强行关联)。
    """
    provider = raw.get('provider') or 'UNKNOWN'
    pid = str(raw.get('provider_article_id') or '')
    url = (raw.get('url_original') or '').strip()
    if pid:
        key = f'{provider}|pid:{pid}'
    elif url:
        key = f'{provider}|url:{url}'
    else:
        return None
    return 'lart_' + hashlib.sha256(key.encode('utf-8')).hexdigest()[:16]


# ──────────── FIX1-06: 模型可见派生文本的数据化处理 ────────────

_TAG_RE = re.compile(r'<[^>]{0,200}>')
_CTRL_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
# FIX2-01: str.splitlines()覆盖LF/CR/CRLF/VT/FF/NEL(U+0085)/U+2028/U+2029
# 及U+001C~001E等一切Python行边界——换行折叠不逐个枚举字符,直接用
# 语言级行语义,避免"只处理\n漏掉\r与Unicode换行"的枚举遗漏。


def sanitize_model_text(s):
    """不可信来源文本→安全单行派生文本(FIX1-06+FIX2-01)。

    仅作用于发往模型的派生内容(标题/发布方/URL行)与确定性回退/来源
    附录,**原始档案永不处理**:
      * 行边界折叠: 一切实际换行与Unicode换行(LF/CR/CRLF/VT/FF/NEL/
        U+2028/U+2029…)先归一为单空格——不可信字段永远只能派生**一条
        物理行**,不允许标题内部伪造第二条新闻行/Markdown标题/代码围栏;
      * 剥离控制字符与HTML标签(不执行、不渲染);
      * '[' ']'→'(' ')'——阻断伪造[art_]引用编号/Markdown链接语法;
      * 反引号→单引号,剥行首Markdown结构符(#/>/-),折叠空白串;
    供本机审计的原始档案保持逐字原样,二者严格分离。
    """
    s = ' '.join(str(s or '').splitlines())     # FIX2-01: 单行化
    s = _CTRL_RE.sub('', s)
    s = _TAG_RE.sub('', s)
    s = s.replace('[', '(').replace(']', ')').replace('`', "'")
    s = re.sub(r'^[#>\-]{1,10}\s*', '', s)
    s = re.sub(r'[ \t]{2,}', ' ', s)
    return s.strip()


def record_digest(record):
    """逐记录确定性SHA-256(文档化字段集与序列化规则,见模块docstring)。"""
    payload = {k: v for k, v in record.items()
               if k not in RECORD_DIGEST_EXCLUDE}
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'))
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()


# ───────────────────────── W3-03 归档与清单 ─────────────────────────

def archive_path(news_dir, ymd, batch_id):
    return os.path.join(news_dir, f'news_sources_{ymd}_{batch_id}.json')


def manifest_path(news_dir, ymd):
    return os.path.join(news_dir, f'news_sources_manifest_{ymd}.json')


def _ymd_of(ts_iso):
    return ts_iso[:10].replace('-', '')


def _batch_identity(now_iso, count):
    """批次身份: HHMMSSZr{N}x{uuid8}(FIX1-01)。

    时间段保留可读性;追加uuid4全局唯一段——同秒同记录数的两次采集
    批次身份不同,文件名不碰撞(历史实现仅HHMMSS+r{N},同秒同数量即覆盖)。
    """
    hhmmss = now_iso.replace('-', '').replace(':', '').replace('T', '')[8:14]
    return f'{hhmmss}Zr{count}x{uuid.uuid4().hex[:8]}'


def save_batch(raw_records, news_dir, retrieved_at_utc=None,
               source_status=None, now_utc=None):
    """原始来源归档(采集→归档→分类→GLM→输出;GLM失败不丢原始档案)。

    FIX1-01不可覆盖保证:
      * 档案文件以排他模式'x'(O_CREAT|O_EXCL)创建——命名碰撞(同秒同
        记录数)→换新批次身份重试(≤8次),**绝不覆盖既有档案**;仍碰撞→
        明确失败且原文件保留;
      * 日清单flock排他锁下读取-修改-写入,tmp+os.replace原子落盘
        (并发批次不丢失登记、不互相覆盖);
      * 清单损坏→先原样保全为manifest.corrupt-*.json副本再重建,
        recovery_note记录经过,绝不静默当空清单覆盖;
      * 清单阶段失败→保留已写档案并抛RuntimeError明确诊断(未登记档案
        可由verify_archive检出),不自动销毁任何批次。

    返回 (batch_id, archive文件路径, records)。同日重跑产生新批次,
    旧批次与清单条目永不删除。source_status: 各来源通道成败披露。
    """
    retrieved = retrieved_at_utc or now_utc_iso()
    now = now_utc or now_utc_iso()
    ymd = _ymd_of(now)
    os.makedirs(news_dir, exist_ok=True)

    records = [normalize_record(r, retrieved_at_utc=retrieved)
               for r in raw_records]

    apath = None
    batch_id = None
    for _attempt in range(8):
        batch_id = _batch_identity(now, len(records))
        apath = archive_path(news_dir, ymd, batch_id)
        for r in records:
            r['batch_id'] = batch_id
            r['record_sha256'] = record_digest(r)
        doc = {
            'schema_version': SCHEMA_VERSION,
            'kind': 'news_sources_batch',
            'batch_id': batch_id,
            'ymd': ymd,
            'created_at_utc': now,
            'source_status': source_status or {},
            'records': records,
        }
        try:
            with open(apath, 'x', encoding='utf-8') as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
            break
        except FileExistsError:
            continue   # 命名碰撞: 换新批次身份重试,不覆盖既有档案
    else:
        raise RuntimeError(
            f'批次命名冲突: 8次排他创建均碰撞({apath});已放弃,未覆盖任何'
            '既有档案——请检查目录写入状态后重试')

    file_sha = _file_sha256(apath)

    # 独立日清单: flock排他锁下原子更新;损坏先保全再重建(FIX1-01)
    mpath = manifest_path(news_dir, ymd)
    lock_path = mpath + '.lock'
    entry = {'batch_id': batch_id, 'file': os.path.basename(apath),
             'file_sha256': file_sha, 'count': len(records),
             'created_at_utc': now}
    with open(lock_path, 'w', encoding='utf-8') as lf:
        fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
        try:
            manifest, recovery = None, None
            if os.path.exists(mpath):
                try:
                    with open(mpath, 'r', encoding='utf-8') as f:
                        loaded = json.load(f)
                    if isinstance(loaded, dict) and isinstance(
                            loaded.get('batches'), list):
                        manifest = loaded
                    else:
                        recovery = '清单结构异常(非{batches:[…]}对象)'
                except Exception as e:
                    recovery = f'清单JSON损坏({e})'
                if recovery:
                    keep = (mpath[:-5]
                            + f'.corrupt-{uuid.uuid4().hex[:8]}.json')
                    os.replace(mpath, keep)
                    recovery += (f';原损坏清单已原样保全为'
                                 f'{os.path.basename(keep)}(不静默丢弃)')
            if manifest is None:
                manifest = {'schema_version': SCHEMA_VERSION, 'ymd': ymd,
                            'batches': []}
                if recovery:
                    manifest['recovery_note'] = recovery
            if not any(b.get('batch_id') == batch_id
                       for b in manifest['batches']):
                manifest['batches'].append(entry)
            tmp = mpath + f'.tmp-{uuid.uuid4().hex[:8]}'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=1)
            os.replace(tmp, mpath)
        except Exception as e:
            raise RuntimeError(
                f'档案已写入但清单更新失败(未销毁档案,不自动删除批次): '
                f'{apath};清单={mpath};错误={e};该未登记批次可由'
                f'verify_archive检出(清单中无此批次条目),可事后补登记'
            ) from e
        finally:
            fcntl.flock(lf.fileno(), fcntl.LOCK_UN)
    return batch_id, apath, records


def _file_sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def verify_archive(apath, news_dir):
    """档案完整性验证: 文件SHA-256 vs 清单 + 逐记录摘要重算。

    返回 (ok, problems)。损坏档案不得被标记为通过完整性验证(W3-06):
    只报告事实,不修改任何文件。
    """
    problems = []
    base = os.path.basename(apath)
    ymd = base[len('news_sources_'):].split('_')[0]
    mpath = manifest_path(news_dir, ymd)
    entry = None
    if os.path.exists(mpath):
        try:
            with open(mpath, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            entry = next((b for b in manifest.get('batches', [])
                          if b.get('file') == base), None)
        except Exception as e:
            problems.append(f'清单损坏: {e}')
    else:
        problems.append('清单不存在')
    if entry is None:
        problems.append('清单中无此批次条目')
    else:
        actual = _file_sha256(apath)
        if actual != entry.get('file_sha256'):
            problems.append('档案文件SHA-256与清单不符(档案被改动或损坏)')
    try:
        with open(apath, 'r', encoding='utf-8') as f:
            doc = json.load(f)
    except Exception as e:
        return False, problems + [f'档案JSON损坏: {e}']
    for r in doc.get('records', []):
        claimed = r.get('record_sha256')
        recomputed = record_digest(r)
        if claimed != recomputed:
            problems.append(f"记录摘要不符: {r.get('article_id')}")
    return not problems, problems


def load_day_records(news_dir, ymd):
    """读取某日全部批次记录(按批次时间序),供索引构建/消费端。"""
    records = []
    for b in _day_batches(news_dir, ymd):
        records.extend(b.get('records', []))
    return records


def _day_batches(news_dir, ymd):
    batches = []
    if not os.path.isdir(news_dir):
        return batches
    for fname in sorted(os.listdir(news_dir)):
        if not (fname.startswith(f'news_sources_{ymd}_')
                and fname.endswith('.json')):
            continue
        try:
            with open(os.path.join(news_dir, fname), 'r',
                      encoding='utf-8') as f:
                batches.append(json.load(f))
        except Exception:
            continue
    return batches


def load_records_since(news_dir, cutoff_ymd):
    """读取cutoff_ymd(含)以来的全部来源记录(周报7天窗口消费)。"""
    records = []
    if not os.path.isdir(news_dir):
        return records
    for fname in sorted(os.listdir(news_dir)):
        m = re.match(r'news_sources_(\d{8})_', fname)
        if not m or m.group(1) < cutoff_ymd:
            continue
        records.extend(load_day_records(news_dir, m.group(1)))
    return records


# ───────────────────────── W3-05 引用与来源索引 ─────────────────────────

def extract_citations(text):
    """【诊断级宽松文本搜索,非认证】从全文任意位置提取[art_]ID(去重保序)。

    FIX3-01起明确限定: 本函数**不区分引用位置**——正文/标题/不合格条目行
    中的ID同样被搜出,因此**不得作为正式周报可信引用判定入口**(FIX3-03),
    也不得用于模型摘要格式校验(FIX3-02)。正式判定必须用
    parse_news_item_references(严格行首引用槽位);可信认证用
    verify_citation_trusted(以原始档案为可信根实时核验)。
    """
    seen, out = set(), []
    for m in CITATION_RE.finditer(text or ''):
        aid = m.group(1)
        if aid not in seen:
            seen.add(aid)
            out.append(aid)
    return out


def _uniq_ids(seq):
    """ID列表去重且保序(确定性,供解析器内部使用)。"""
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def parse_news_item_references(text):
    """FIX3-01: 正式新闻条目引用位置解析器(严格行首引用槽位,逐行解析)。

    合法新闻条目=单行顶格以'- [art_xxx]'开头且ID后紧跟空白或行尾:
        - [art_aaaaaaaaaaaaaaaa] Fed holds rates
    仅该行首槽位ID取得新闻引用资格;以下位置的ID**不取得**引用资格:
      * 类别标题/普通正文(如'### 美联储/利率 [art_b]'或叙述句);
      * 不合格条目行的行内任意位置(如'- Fed holds rates [art_b]');
      * 合法条目的正文夹带(如'- [art_a] Fed holds rates [art_b]'→
        A合法/B为body_extra_ids,§4.3固定反例)。
    生成端(news_collector.validate_summary_citations)与正式消费端
    (report_generator.load_news_summary)共用本判定基础;不引入数据库,
    不改变新闻原始档案结构。
    返回dict:
      items        逐条目{line_no,line,article_id,body,extra_body_ids,
                   status('ok'|'body_extra_ids')}
      legal_ids    合法槽位ID(去重保序)
      illegal_ids  非法位置ID(正文夹带+非槽位行,去重保序)
      anomalies    逐异常{line_no,kind('body_extra_ids'|'illegal_position'),
                   ids,reason,line,action}
      ok           无任何异常(严格格式口径)
    """
    items, anomalies = [], []
    for lineno, raw in enumerate(str(text or '').splitlines(), 1):
        line = raw.rstrip()
        if not line.strip():
            continue
        m = NEWS_ITEM_RE.match(line)
        if m:
            aid = m.group(1)
            body = line[m.end():].lstrip()
            extras = _uniq_ids(CITATION_RE.findall(body))
            items.append({
                'line_no': lineno,
                'line': line,
                'article_id': aid,
                'body': body,
                'extra_body_ids': extras,
                'status': 'ok' if not extras else 'body_extra_ids',
            })
            if extras:
                anomalies.append({
                    'line_no': lineno, 'kind': 'body_extra_ids',
                    'article_id': aid, 'ids': extras,
                    'reason': ('条目正文夹带额外[art_]ID(仅行首槽位为合法'
                               '引用位置): ') + ','.join(extras),
                    'line': line[:80],
                    'action': ('夹带ID不取得引用资格;模型输出校验按格式'
                              '失败,正式消费端仅认证行首ID'),
                })
            continue
        loose = _uniq_ids(CITATION_RE.findall(line))
        if loose:
            anomalies.append({
                'line_no': lineno, 'kind': 'illegal_position',
                'ids': loose,
                'reason': ('ID不在新闻条目行首引用槽位(标题/正文/不合格'
                           '条目行中的ID不取得引用资格): ') + ','.join(loose),
                'line': line[:80],
                'action': '不作为可信引用认证,仅确定性诊断记录',
            })
    return {
        'items': items,
        'legal_ids': _uniq_ids([it['article_id'] for it in items]),
        'illegal_ids': _uniq_ids([i for a in anomalies for i in a['ids']]),
        'anomalies': anomalies,
        'ok': not anomalies,
    }


def verify_citation(article_id, refs_index):
    """【诊断级,非认证】article_id是否为索引成员(FIX1-02降级限定)。

    仅证明ID存在于传入索引字典——不证明档案存在/清单一致/摘要匹配,
    **不得作为可信来源认证使用**。可信认证必须用verify_citation_trusted
    (以原始档案为可信根实时核验)。
    """
    return article_id in (refs_index.get('articles') or {})


def _article_view(r):
    """原始记录→索引/可信集合的来源视图(article_id→可核验来源信息)。"""
    url = r.get('url_original')
    return {
        'article_id': r['article_id'],
        'logical_article_id': r.get('logical_article_id'),
        'provider': r.get('provider'),
        'channel': r.get('channel'),
        'publisher': r.get('publisher') or '(发布方缺失)',
        'headline_original': r.get('headline_original'),
        'url_original': url,
        'url_available': bool(url),
        'url_note': None if url else '来源未提供直接文章链接(不可提供,不编造)',
        'published_at_utc': r.get('published_at_utc'),
        'published_status': r.get('published_status'),
        'retrieved_at_utc': r.get('retrieved_at_utc'),
        'provenance_status': r.get('provenance_status'),
        'batch_id': r.get('batch_id'),
    }


def _verified_batches(news_dir, day_filter=None, cutoff_ymd=None):
    """枚举并逐批次实际核验(FIX1-02可信链: 档案→清单→文件SHA→记录摘要)。

    返回 (verified_docs, failed, problems, checked)。day_filter='20261030'
    限定单日;cutoff_ymd='20261023'取≥该日全部。坏批次只进failed/problems,
    其记录一概不进入verified_docs(不得先入articles再仅留告警)。
    """
    verified, failed, problems, checked = [], [], {}, 0
    if not os.path.isdir(news_dir):
        return verified, failed, problems, checked
    for fname in sorted(os.listdir(news_dir)):
        m = re.match(r'news_sources_(\d{8})_', fname)
        if not m or not fname.endswith('.json'):
            continue
        if day_filter is not None and m.group(1) != day_filter:
            continue
        if cutoff_ymd is not None and m.group(1) < cutoff_ymd:
            continue
        checked += 1
        path = os.path.join(news_dir, fname)
        ok, probs = verify_archive(path, news_dir)
        if not ok:
            failed.append(fname)
            problems[fname] = probs
            continue
        try:
            with open(path, 'r', encoding='utf-8') as f:
                verified.append(json.load(f))
        except Exception as e:
            failed.append(fname)
            problems[fname] = [f'重读失败: {e}']
    return verified, failed, problems, checked


def load_trusted_articles_since(news_dir, cutoff_ymd):
    """FIX1-02: 消费时从原始档案实时重建可信来源集合(不信任历史索引)。

    链路: 原始档案→清单核验→文件SHA-256→逐记录摘要→文章ID映射。
    仅通过认证批次的记录进入articles(按article_id去重,批次序首见为准);
    失败批次进integrity.failed_batches+batch_problems。news_refs_*.json
    是派生视图——即使其integrity声称通过,也不作为认证依据。
    """
    verified, failed, problems, checked = _verified_batches(
        news_dir, cutoff_ymd=cutoff_ymd)
    articles = {}
    for doc in verified:
        for r in doc.get('records', []):
            aid = r.get('article_id')
            if not aid or aid in articles:
                continue
            articles[aid] = _article_view(r)
    return {'articles': articles,
            'integrity': {'checked_batches': checked,
                          'failed_batches': failed,
                          'batch_problems': problems}}


def verify_citation_trusted(article_id, news_dir, cutoff_ymd):
    """FIX1-02可信引用认证: 以原始档案为根实时核验,非索引成员判断。"""
    trusted = load_trusted_articles_since(news_dir, cutoff_ymd)
    return article_id in trusted['articles']


def build_refs_index(news_dir, ymd=None, now_utc=None):
    """构造某日(或来源中最新日)来源索引: article_id→可核验来源信息。

    FIX1-02验证门控: 逐批次实际核验(档案/清单/文件SHA/记录摘要),
    **仅通过认证批次的记录进入articles**;坏批次只进integrity.failed_
    batches+batch_problems(不得先入articles再仅留告警)。同日多批次按
    article_id去重(重跑不产生虚假重复来源身份)。
    """
    if ymd is None:
        ymd = _latest_sources_ymd(news_dir)
        if ymd is None:
            return None
    verified, failed, problems, checked = _verified_batches(
        news_dir, day_filter=ymd)
    articles = {}
    for doc in verified:
        for r in doc.get('records', []):
            aid = r.get('article_id')
            if not aid or aid in articles:
                continue
            articles[aid] = _article_view(r)
    return {
        'schema_version': SCHEMA_VERSION,
        'kind': 'news_refs_index',
        'ymd': ymd,
        'built_at_utc': now_utc or now_utc_iso(),
        'integrity': {'checked_batches': checked,
                      'failed_batches': failed,
                      'batch_problems': problems},
        'articles': articles,
    }


def _latest_sources_ymd(news_dir):
    best = None
    if not os.path.isdir(news_dir):
        return None
    for fname in os.listdir(news_dir):
        m = re.match(r'news_sources_(\d{8})_', fname)
        if m and (best is None or m.group(1) > best):
            best = m.group(1)
    return best


def write_refs_index(news_dir, ymd=None, now_utc=None):
    idx = build_refs_index(news_dir, ymd=ymd, now_utc=now_utc)
    if idx is None or not idx.get('articles'):
        return None   # 零来源不写索引(全败降级不产生虚假有效索引)
    path = os.path.join(news_dir, f"news_refs_{idx['ymd']}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(idx, f, ensure_ascii=False, indent=1)
    return path


def load_refs_indexes_since(news_dir, cutoff_ymd):
    """读取cutoff以来的全部来源索引(周报消费窗口)。"""
    out = {}
    if not os.path.isdir(news_dir):
        return out
    for fname in sorted(os.listdir(news_dir)):
        m = re.match(r'news_refs_(\d{8})\.json', fname)
        if not m or m.group(1) < cutoff_ymd:
            continue
        try:
            with open(os.path.join(news_dir, fname), 'r',
                      encoding='utf-8') as f:
                out[m.group(1)] = json.load(f)
        except Exception:
            continue
    return out


def derive_display(record, limit=200):
    """派生展示副本: 截断只发生在这里,原始档案summary_original不截断。"""
    s = (record.get('summary_original') or '').strip()
    if limit and len(s) > limit:
        return s[:limit] + '…(截断于派生视图,原始档案保全全文)'
    return s


def summarize_for_prompt(trusted, cited_ids):
    """确定性来源索引说明(代码构造,非模型生成)——供周报/摘要消费端。

    FIX1-02: 入参trusted应为load_trusted_articles_since产物(以原始档案
    为可信根实时核验)——引用了可信集合外的article_id时,如实标注未通过
    来源认证(原始来源档案缺失或未通过完整性验证),不得计为有效来源。
    FIX1-06: 本文本进入模型输入——标题/发布方/URL经sanitize_model_text
    数据化(原始档案保持逐字原样,仅派生副本处理,恶意标题不得借附录
    绕过模型输入保护)。无URL来源明确标记不可提供,不编造外部链接。
    """
    arts = trusted.get('articles') or {}
    lines = []
    for aid in cited_ids:
        a = arts.get(aid)
        if a is None:
            lines.append(f'- [{aid}] ⚠️未通过来源认证(原始来源档案缺失或'
                         '未通过完整性验证,不得作为已引用来源)')
            continue
        url = (sanitize_model_text(a['url_original'])
               if a['url_available'] else '无直接文章链接(不可提供)')
        pub = a['published_at_utc'] or '发布时间UNKNOWN(未造假)'
        lines.append(f"- [{aid}] {sanitize_model_text(a['publisher'])}"
                     f"({a['provider']}/{a['channel']}) | "
                     f"{sanitize_model_text(a['headline_original'])} | "
                     f"{url} | 发布:{pub} | 完整性:{a['provenance_status']}")
    integ = trusted.get('integrity') or {}
    head = ('#### 来源索引(确定性代码构造,非模型生成;引用经原始来源'
            '档案完整性核验)')
    if integ.get('failed_batches'):
        head += (f"\n⚠️ 完整性告警: {len(integ['failed_batches'])}个来源批次"
                 '未通过完整性验证,其记录不作为已认证来源')
    return head + '\n' + '\n'.join(lines)
