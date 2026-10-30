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

序列化与摘要规则(W3-03 §7.3,确定性):
  * record_sha256 = SHA-256( json.dumps(record剔除record_sha256/batch_id/
    retrieved_at_utc后, sort_keys=True, ensure_ascii=False,
    separators=(',',':')) )——文档化于 RECORD_DIGEST_EXCLUDE;
  * 档案文件整体SHA-256由清单记录(file_sha256),对档案文件字节计算;
  * 摘要在**归档写入前**生成并随记录持久化,清单为独立文件(单独批次清单)。
"""

import calendar
import hashlib
import json
import os
import re
from datetime import datetime, timezone

SCHEMA_VERSION = 1

# 进入record_sha256的字段集=规范化记录全体字段,除下列运行期字段
RECORD_DIGEST_EXCLUDE = ('record_sha256', 'batch_id', 'retrieved_at_utc')

# 稳定引用ID提取模型/报告文本中的 [art_xxxxxxxxxxxxxxxx]
CITATION_RE = re.compile(r'\[(art_[0-9a-f]{16})\]')


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


def save_batch(raw_records, news_dir, retrieved_at_utc=None,
               source_status=None, now_utc=None):
    """原始来源归档(采集→归档→分类→GLM→输出;GLM失败不丢原始档案)。

    返回 (batch_id, archive文件路径, records)。同日重跑产生新批次,
    旧批次与清单条目永不删除。source_status: 各来源通道成败披露
    (部分源失败保留其余真实来源,明确披露失败源)。
    """
    retrieved = retrieved_at_utc or now_utc_iso()
    now = now_utc or now_utc_iso()
    ymd = _ymd_of(now)
    batch_id = now.replace('-', '').replace(':', '').replace('T', '')[8:14] \
        + 'Z' + f'r{len(raw_records)}'
    os.makedirs(news_dir, exist_ok=True)

    records = [normalize_record(r, retrieved_at_utc=retrieved)
               for r in raw_records]
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
    apath = archive_path(news_dir, ymd, batch_id)
    with open(apath, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    file_sha = _file_sha256(apath)

    # 独立日清单(追加式): 档案文件SHA-256入册,档案自改可被verify检出
    mpath = manifest_path(news_dir, ymd)
    manifest = {'schema_version': SCHEMA_VERSION, 'ymd': ymd, 'batches': []}
    if os.path.exists(mpath):
        try:
            with open(mpath, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            if isinstance(loaded, dict) and isinstance(loaded.get('batches'),
                                                       list):
                manifest = loaded
        except Exception:
            pass  # 清单损坏不阻断归档;verify/索引构建会如实披露
    if not any(b.get('batch_id') == batch_id for b in manifest['batches']):
        manifest['batches'].append({
            'batch_id': batch_id, 'file': os.path.basename(apath),
            'file_sha256': file_sha, 'count': len(records),
            'created_at_utc': now,
        })
    with open(mpath, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
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
    """从文本提取实际引用的article_id(去重保序)。"""
    seen, out = set(), []
    for m in CITATION_RE.finditer(text or ''):
        aid = m.group(1)
        if aid not in seen:
            seen.add(aid)
            out.append(aid)
    return out


def verify_citation(article_id, refs_index):
    """引用认证: article_id必须存在于确定性代码构造的来源索引。"""
    return article_id in (refs_index.get('articles') or {})


def build_refs_index(news_dir, ymd=None, now_utc=None):
    """构造某日(或来源中最新日)来源索引: article_id→可核验来源信息。

    同日多批次按article_id去重(重跑不产生虚假重复来源身份);
    逐批次做完整性验证,失败批次如实计入integrity,不标记为已验证。
    """
    if ymd is None:
        ymd = _latest_sources_ymd(news_dir)
        if ymd is None:
            return None
    records = load_day_records(news_dir, ymd)
    articles, failed_batches, checked = {}, [], 0
    for fname in sorted(os.listdir(news_dir or '')) \
            if os.path.isdir(news_dir) else []:
        if fname.startswith(f'news_sources_{ymd}_') and fname.endswith('.json'):
            checked += 1
            ok, _ = verify_archive(os.path.join(news_dir, fname), news_dir)
            if not ok:
                failed_batches.append(fname)
    for r in records:                      # 批次时间序→首见为准
        aid = r['article_id']
        if aid in articles:
            continue
        url = r.get('url_original')
        articles[aid] = {
            'article_id': aid,
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
    return {
        'schema_version': SCHEMA_VERSION,
        'kind': 'news_refs_index',
        'ymd': ymd,
        'built_at_utc': now_utc or now_utc_iso(),
        'integrity': {'checked_batches': checked,
                      'failed_batches': failed_batches},
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


def summarize_for_prompt(refs_index, cited_ids):
    """确定性来源索引说明(代码构造,非模型生成)——供周报/摘要消费端。

    模型或加工文本引用了索引中不存在的article_id时,如实标注未通过
    来源认证(K: 虚构引用不可被认作有效来源)。无URL来源明确标记
    不可提供直接链接,不编造外部链接。
    """
    arts = refs_index.get('articles') or {}
    lines = []
    for aid in cited_ids:
        a = arts.get(aid)
        if a is None:
            lines.append(f'- [{aid}] ⚠️未通过来源认证(来源索引中不存在,'
                         '不得作为已引用来源)')
            continue
        url = a['url_original'] if a['url_available'] \
            else '无直接文章链接(不可提供)'
        pub = a['published_at_utc'] or '发布时间UNKNOWN(未造假)'
        lines.append(f"- [{aid}] {a['publisher']}({a['provider']}/"
                     f"{a['channel']}) | {a['headline_original']} | {url} | "
                     f"发布:{pub} | 完整性:{a['provenance_status']}")
    integ = refs_index.get('integrity') or {}
    head = '#### 来源索引(确定性代码构造,非模型生成;引用经来源档案核验)'
    if integ.get('failed_batches'):
        head += (f"\n⚠️ 完整性告警: {len(integ['failed_batches'])}个来源批次"
                 '未通过完整性验证,其记录不作为已认证来源')
    return head + '\n' + '\n'.join(lines)
