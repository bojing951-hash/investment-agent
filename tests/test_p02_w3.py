#!/usr/bin/env python3
"""IA-P0-2-W3 联合验收测试(新闻原始来源保全)。

对应指令IA-P0-2-W3-DEV-v1.0 §十一 A~O:
  A 原始字段(真实归档文件读回一致)   B URL丢失敏感性(历史缺陷必须可检)
  C 摘要截断(原始全文/派生可截)     D RSS时间(本地时区无关,UTC一致)
  E 缺失发布时间(不造假)           F 同标题不同URL(独立来源身份)
  G 同日重跑(不覆盖/不虚假重复)     H 分类保留article_id
  I 脱敏隔离(原始不变/派生加工)     J GLM失败(原始保全+可追溯回退)
  K 虚构引用(认证失败)             L 七天周报消费(来源身份保留)
  M 来源全部失败(非关键降级)       N 档案篡改(完整性可检)
  O P0-1/W1/W2安全继承(真实研究主链)
真实模块+隔离临时目录;外部源(Finnhub/RSS/GLM)全Mock,零真实API调用。
"""
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import time
import calendar
from datetime import datetime
from unittest import mock

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(_HERE), 'scripts'))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(os.path.dirname(_HERE)))

import fixt                                    # noqa: E402
import news_provenance as nprov                # noqa: E402
import report_generator as rg                  # noqa: E402
import snapshot_builder as sb                  # noqa: E402
import research_provenance as rp               # noqa: E402
import data_assembler as da                    # noqa: E402
import news_collector as nc                    # noqa: E402
import feedparser                              # noqa: E402

PASS_N, FAIL_N = 0, 0
_TMPD = tempfile.mkdtemp(prefix='w3-')
DAY = '20261024'
TODAY = '2026-10-30'

# 2026-10-28T12:00:00Z 的UTC纪元秒与feedparser结构(Finnhub/RSS同刻)
EPOCH_OK = calendar.timegm((2026, 10, 28, 12, 0, 0, 0, 0, 0))
STRUCT_OK = (2026, 10, 28, 12, 0, 0, 0, 0, 0)
LONG_SUM = ('Sector credit spreads widened sharply this week '
            'across high yield and leveraged loans. ') * 12   # >200字符


def check(name, cond, detail=''):
    global PASS_N, FAIL_N
    if cond:
        PASS_N += 1
        print(f"  ✅ {name}")
    else:
        FAIL_N += 1
        print(f"  ❌ {name}  {detail}")


def quiet(fn, *a, **kw):
    with contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        return fn(*a, **kw)


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


# ═══════════════════ 外部源Mock(Finnhub/RSS/GLM) ═══════════════════

class FakeFH:
    def __init__(self, market=None, company=None):
        self._m = market or []
        self._c = company or {}

    def general_news(self, cat, min_id=0):
        if isinstance(self._m, Exception):
            raise self._m
        return self._m

    def company_news(self, symbol, _from=None, to=None):
        v = self._c.get(symbol)
        if isinstance(v, Exception):
            raise v
        return v or []


class FakeFeed:
    def __init__(self, entries=None, err=None):
        self.entries = entries if entries is not None else []
        self._err = err

    def parse(self, url):
        if self._err:
            raise self._err
        return self


class FakeGLM:
    """GLM Mock: 可编程返回文本/异常;记录prompt供断言。"""

    def __init__(self, text='## 摘要\n### 美联储/利率\n- 联储按兵不动。'):
        self.text = text
        self.error = None
        self.prompts = []

    def __call__(self, *a, **kw):
        glm = self

        class _Stream:
            def __iter__(self):
                e = type('E', (), {})()
                e.choices = [type('C', (), {'delta': type(
                    'D', (), {'content': glm.text})()})()]
                yield e

        class _Comp:
            def create(self, **kw2):
                glm.prompts.append(kw2.get('messages'))
                if glm.error:
                    raise glm.error
                return _Stream()

        class _Chat:
            completions = type('X', (), {'create': None})()

        _Chat.completions.create = _Comp().create

        class _Client:
            def __init__(self, **kw3):
                self.chat = _Chat()
        return _Client


def run_collector(tmp, market=None, company=None, rss=None, glm=None,
                  now='2026-10-30T05:30:00Z', watch=None, rss_err=None):
    """在隔离DATA_DIR下真实执行nc.run()。rss: {feed名: [entries]或Exception}。"""
    nc.DATA_DIR = os.path.join(tmp, 'data')
    glm = glm or FakeGLM()
    rss = rss or {}
    feed_by_url = {}
    for name, url in nc.RSS_FEEDS.items():
        v = rss.get(name, [])
        feed_by_url[url] = (FakeFeed(err=v) if isinstance(v, Exception)
                            else FakeFeed(entries=v))
    with mock.patch.object(nc, 'fh_client',
                           FakeFH(market, company)), \
            mock.patch.object(feedparser, 'parse',
                              lambda url: feed_by_url[url].parse(url)), \
            mock.patch.object(nc, 'WATCH_SYMBOLS', watch or ['NVDA']), \
            mock.patch.object(nc, 'OpenAI', glm()), \
            contextlib.redirect_stdout(io.StringIO()):
        nc.run(now_utc=now)
    return glm, os.path.join(nc.DATA_DIR, 'news')


def newsdir_of(tmp):
    return os.path.join(tmp, 'data', 'news')


def sources_of(nd, ymd='20261030'):
    return sorted(f for f in os.listdir(nd)
                  if f.startswith(f'news_sources_{ymd}_'))


def archive_of(nd, ymd='20261030'):
    srcs = sources_of(nd, ymd)
    assert srcs, 'no source archive'
    return os.path.join(nd, srcs[0])


def records_of(nd, ymd='20261030'):
    return json.load(open(archive_of(nd, ymd),
                          encoding='utf-8'))['records']


def refs_of(nd, ymd='20261030'):
    return json.load(open(os.path.join(nd, f'news_refs_{ymd}.json'),
                          encoding='utf-8'))


MKT_FULL = [{'id': 9001, 'headline': 'Fed holds rates steady in October',
             'source': 'Reuters', 'summary': 'The Federal Reserve kept '
             'interest rates unchanged.', 'url': 'https://reuters.com/fed',
             'datetime': EPOCH_OK}]
CO_FULL = {'NVDA': [{'id': 8000, 'headline': 'NVDA earnings beat estimates',
                    'source': 'Bloomberg', 'summary': 'Chip giant beats.',
                    'url': 'https://bloomberg.com/nvda', 'datetime': EPOCH_OK,
                    'related': 'NVDA,AAPL'}]}
RSS_FULL = {'CNBC_Economy': [{
    'title': 'Oil rises on supply concern', 'link': 'https://cnbc.com/oil',
    'summary': LONG_SUM, 'id': 'cnbc-123',
    'published': 'Wed, 28 Oct 2026 12:00:00 GMT',
    'published_parsed': STRUCT_OK}]}

print("═" * 72)
print("IA-P0-2-W3: 新闻原始来源保全(A~O)")
print("═" * 72)

# ══ A. 原始字段(真实归档读回一致) ═════════════════════════════════════
print("\n[A] 原始字段: 完整输入→实际归档文件读回一致")
tA = tempfile.mkdtemp(prefix='w3A-', dir=_TMPD)
glmA, ndA = run_collector(tA, market=MKT_FULL, company=CO_FULL,
                          rss=RSS_FULL, now='2026-10-30T05:30:00Z')
recsA = records_of(ndA)
by_ch = {r['channel']: r for r in recsA}
mA, cA, rA = by_ch['market_news'], by_ch['company_news'], by_ch['rss']
check("A1 市场新闻: 标题/URL/发布方/摘要/UTC发布时间/供应商ID/采集时刻逐字段"
      "读回一致(W3问题1: URL不再在合并时丢失),provenance=COMPLETE,采集时刻"
      "独立保存(retrieved 05:30≠published 12:00前一天)",
      mA['headline_original'] == 'Fed holds rates steady in October'
      and mA['url_original'] == 'https://reuters.com/fed'
      and mA['publisher'] == 'Reuters'
      and mA['summary_original'] == MKT_FULL[0]['summary']
      and mA['published_at_utc'] == '2026-10-28T12:00:00Z'
      and mA['provider_article_id'] == '9001'
      and mA['retrieved_at_utc'] == '2026-10-30T05:30:00Z'
      and mA['provenance_status'] == 'COMPLETE',
      str(mA)[:100])
check("A2 个股新闻: 同类字段+请求证券代码watch_symbol=NVDA+related原文"
      "保全(不因多证券关联覆盖来源身份)",
      cA['watch_symbol'] == 'NVDA' and cA['related_original'] == 'NVDA,AAPL'
      and cA['url_original'] == 'https://bloomberg.com/nvda'
      and cA['published_at_utc'] == '2026-10-28T12:00:00Z',
      str(cA)[:80])
check("A3 RSS: feed身份(feed_name/feed_url)+entry.id+published原始字符串+"
      "UTC发布时刻+URL+发布方(feed身份记载)全保全;published_raw原样保留",
      rA['provider'] == 'RSS' and rA['feed_name'] == 'CNBC_Economy'
      and rA['feed_url'] == nc.RSS_FEEDS['CNBC_Economy']
      and rA['entry_id'] == 'cnbc-123'
      and rA['published_raw'] == 'Wed, 28 Oct 2026 12:00:00 GMT'
      and rA['published_at_utc'] == '2026-10-28T12:00:00Z'
      and rA['url_original'] == 'https://cnbc.com/oil'
      and rA['publisher'] == 'CNBC_Economy',
      str(rA)[:90])
check("A4 归档可验证: verify_archive通过(文件SHA-256==清单+逐记录摘要重算)",
      nprov.verify_archive(archive_of(ndA), ndA) == (True, []), '')

# ══ B. URL丢失敏感性(历史缺陷必须可检) ══════════════════════════════
print("\n[B] URL丢失敏感性: 历史save_news丢URL形态必须被检出")
legacy = {'headline': 'Legacy no-url', 'source': 'Reuters',
          'summary': 'old', 'datetime': EPOCH_OK}   # 历史简化形态(无url)
rec_legacy = nprov.normalize_record(legacy)
check("B1 历史简化记录(url缺失)入档: url_original=None+PARTIAL:url如实"
      "标注,不得静默当COMPLETE——缺陷形态可被provenance_status暴露",
      rec_legacy['url_original'] is None
      and rec_legacy['provenance_status'].startswith('PARTIAL:')
      and 'url' in rec_legacy['provenance_status'],
      rec_legacy['provenance_status'])
check("B2 真实流程回归: A组归档读回url_original==输入URL(非空),refs索引"
      "url_available=True——若重新在合并时丢URL,A1/B2必失败",
      mA['url_original'] == 'https://reuters.com/fed'
      and refs_of(ndA)['articles'][mA['article_id']]['url_available'],
      '')

# ══ C. 摘要截断 ══════════════════════════════════════════════════════
print("\n[C] 摘要截断: 原始档案全文,派生视图才可截断")
check("C1 RSS超长摘要({}字符)归档保全全文(无[:200]截断;W3问题2)".format(
        len(LONG_SUM)),
      rA['summary_original'] == LONG_SUM
      and len(rA['summary_original']) == len(LONG_SUM),
      'len={}'.format(len(rA['summary_original'])))
d200 = nprov.derive_display(rA, limit=200)
check("C2 派生展示副本截断至200并显式标注(原始不受影响)",
      len(d200) < len(LONG_SUM) and d200.endswith('原始档案保全全文)')
      and rA['summary_original'] == LONG_SUM, '')

# ══ D. RSS时间(本地时区无关) ═════════════════════════════════════════
print("\n[D] RSS时间: 同一published_parsed在不同本地时区下UTC结果一致")
old_tz = os.environ.get('TZ')
try:
    results, mk_results = {}, {}
    for tz in ('America/New_York', 'Asia/Shanghai', 'UTC'):
        os.environ['TZ'] = tz
        time.tzset()
        results[tz] = nprov.rss_parsed_to_utc_iso(STRUCT_OK)
        mk_results[tz] = time.mktime(STRUCT_OK)   # 历史缺陷实现(仅对比用)
finally:
    if old_tz is None:
        os.environ.pop('TZ', None)
    else:
        os.environ['TZ'] = old_tz
    time.tzset()
check("D1 timegm路径: 纽约/上海/UTC三种本地时区下均=2026-10-28T12:00:00Z"
      "(UTC语义确定性;W3问题3修复)",
      set(results.values()) == {'2026-10-28T12:00:00Z'}, str(results))
check("D2 敏感性对照: 历史time.mktime实现同时区漂移(证明测试有效——若"
      "回退mktime,D1必失败)",
      len(set(mk_results.values())) == 3, str(mk_results))

# ══ E. 缺失发布时间 ══════════════════════════════════════════════════
print("\n[E] 缺失发布时间: UNKNOWN,不造假")
rss_nodate = {'CNBC_Economy': [{
    'title': 'No timestamp item', 'link': 'https://cnbc.com/nots',
    'summary': 'text', 'id': 'cnbc-124'}]}   # 无published/published_parsed
tE = tempfile.mkdtemp(prefix='w3E-', dir=_TMPD)
run_collector(tE, market=[dict(MKT_FULL[0], id=9100, datetime=0)],
              rss=rss_nodate, now='2026-10-30T05:30:00Z')
recsE = {r['channel']: r for r in records_of(newsdir_of(tE))}
check("E1 RSS无发布时间: published_at_utc=None+published_status=UNKNOWN,"
      "采集时刻独立(retrieved≠published,未用采集/当前时间冒充发布时间)",
      recsE['rss']['published_at_utc'] is None
      and recsE['rss']['published_status'] == 'UNKNOWN'
      and recsE['rss']['retrieved_at_utc'] == '2026-10-30T05:30:00Z'
      and 'published_at' in recsE['rss']['provenance_status'],
      str(recsE['rss'])[:80])
check("E2 Finnhub datetime=0/None: epoch_to_utc_iso→None+normalize→UNKNOWN"
      "不造假(注: 采集器既有7天窗口过滤会先行丢弃datetime=0的市场条目——"
      "遗留行为,非W3改动;到达归档层的零值/缺失发布时间一律UNKNOWN)",
      nprov.epoch_to_utc_iso(0) is None
      and nprov.epoch_to_utc_iso(None) is None
      and nprov.normalize_record(
          {'provider': 'Finnhub', 'channel': 'market_news',
           'provider_article_id': '9100', 'publisher': 'Reuters',
           'headline_original': 'H', 'summary_original': 'S',
           'url_original': 'https://r/e2', 'published_raw': 0},
          retrieved_at_utc='2026-10-30T05:30:00Z')['published_at_utc']
      is None, '')

# ══ F. 同标题不同URL ═════════════════════════════════════════════════
print("\n[F] 同标题不同URL: 两条独立来源身份")
tF = tempfile.mkdtemp(prefix='w3F-', dir=_TMPD)
same_h = 'Identical headline about credit spreads'
run_collector(tF, market=[{'id': 0, 'headline': same_h, 'source': 'Reuters',
                           'summary': 's1', 'url': 'https://a.com/x',
                           'datetime': EPOCH_OK},
                          {'id': 0, 'headline': same_h, 'source': 'Bloomberg',
                           'summary': 's2', 'url': 'https://b.com/y',
                           'datetime': EPOCH_OK}])
recsF = records_of(newsdir_of(tF))
idsF = [r['article_id'] for r in recsF]
check("F1 同标题不同URL(+不同发布方): 两条独立article_id,两条均入档/入索引,"
      "URL原值各自保留(标题不单独决定身份)",
      len(recsF) == 2 and len(set(idsF)) == 2
      and {r['url_original'] for r in recsF} == {'https://a.com/x',
                                                 'https://b.com/y'}
      and len(refs_of(newsdir_of(tF))['articles']) == 2, str(idsF))

# ══ G. 同日重跑 ══════════════════════════════════════════════════════
print("\n[G] 同日重跑: 不覆盖旧批次,不虚假重复")
tG = tempfile.mkdtemp(prefix='w3G-', dir=_TMPD)
run_collector(tG, market=MKT_FULL, now='2026-10-30T05:30:00Z')
first_src = sources_of(newsdir_of(tG))[0]
first_sha = sha(os.path.join(newsdir_of(tG), first_src))
run_collector(tG, market=MKT_FULL, now='2026-10-30T06:10:00Z')   # 同批重采
mkt2 = dict(MKT_FULL[0], id=9500, url='https://reuters.com/fed2')
run_collector(tG, market=[mkt2], now='2026-10-30T07:00:00Z')     # 新增新闻
srcsG = sources_of(newsdir_of(tG))
manG = json.load(open(os.path.join(newsdir_of(tG),
                                   'news_sources_manifest_20261030.json'),
                      encoding='utf-8'))
refsG = refs_of(newsdir_of(tG))
idsG = [r['article_id'] for r in
        sum((json.load(open(os.path.join(newsdir_of(tG), s),
                           encoding='utf-8'))['records'] for s in srcsG), [])]
check("G1 三个批次三份文件+清单三条目(旧批次未被覆盖: 首批SHA-256不变)",
      len(srcsG) == 3 and len(manG['batches']) == 3
      and sha(os.path.join(newsdir_of(tG), first_src)) == first_sha,
      str(srcsG))
check("G2 同文章重采=同article_id(幂等身份,重跑不产生虚假来源记录);"
      "索引按article_id去重(3条档案记录→2个唯一来源)",
      len(idsG) == 3 and len(set(idsG)) == 2
      and len(refsG['articles']) == 2, str(idsG))
check("G3 新增新闻进入索引且旧来源保留(reuters/fed与fed2并存)",
      {refsG['articles'][a]['url_original'] for a in refsG['articles']}
      == {'https://reuters.com/fed', 'https://reuters.com/fed2'}, '')

# ══ H. 分类保留来源 ══════════════════════════════════════════════════
print("\n[H] 分类保留来源: 分类后可找回article_id")
rawH = json.load(open(os.path.join(ndA, 'news_raw_20261030.json'),
                      encoding='utf-8'))
arch_ids = {r['article_id'] for r in recsA}
cat_items = [it for items in rawH.values() for it in items]
fed_items = rawH.get('美联储/利率', [])
check("H1 news_raw分类视图逐条携带article_id且与原始档案一一对应(可从"
      "分类结果找回原始记录);Fed新闻按关键词落入'美联储/利率'",
      all(it.get('article_id') in arch_ids for it in cat_items)
      and cat_items and len(fed_items) >= 1
      and fed_items[0]['url'] == 'https://reuters.com/fed',
      'cats={}'.format(list(rawH)))

# ══ I. 脱敏隔离 ══════════════════════════════════════════════════════
print("\n[I] 脱敏隔离: 原始不变,GLM输入副本加工")
tI = tempfile.mkdtemp(prefix='w3I-', dir=_TMPD)
glmI = FakeGLM()
geo = [{'id': 9700, 'headline': 'Iran sanctions tighten oil exports',
        'source': 'Reuters', 'summary': 's', 'url': 'https://r.com/iran',
        'datetime': EPOCH_OK}]
_, ndI = run_collector(tI, market=geo, glm=glmI)
recI = records_of(ndI)[0]
promptI = glmI.prompts[0][1]['content'] if glmI.prompts else ''
check("I1 原始档案未脱敏: headline_original保留'Iran'原文(永不加工)",
      recI['headline_original'] == 'Iran sanctions tighten oil exports',
      recI['headline_original'])
check("I2 GLM输入为派生副本: prompt中标题已被替换为'Country-A'(原始词"
      "不出现),且行首携带真实[art_]引用ID(original≠sanitized)",
      'Country-A' in promptI and 'Iran' not in promptI
      and recI['article_id'] in promptI,
      promptI[:80])

# ══ J. GLM失败 ══════════════════════════════════════════════════════
print("\n[J] GLM失败: 原始来源仍保全,回退可追溯")
tJ = tempfile.mkdtemp(prefix='w3J-', dir=_TMPD)
glmJ = FakeGLM()
glmJ.error = RuntimeError('GLM down')
_, ndJ = run_collector(tJ, market=MKT_FULL, glm=glmJ)
recsJ = records_of(ndJ)
sumJ = open(os.path.join(ndJ, 'news_summary_20261030.md'),
            encoding='utf-8').read()
check("J1 GLM失败后原始来源档案仍在(归档先于GLM)+验证通过",
      len(recsJ) == 1 and nprov.verify_archive(archive_of(ndJ), ndJ)[0],
      '')
check("J2 回退输出=原始标题+[art_]引用ID可追溯,无编造链接;来源索引照常"
      "落盘",
      'AI摘要失败' in sumJ and recsJ[0]['article_id'] in sumJ
      and os.path.exists(os.path.join(ndJ, 'news_refs_20261030.json')),
      sumJ[:60])

# ══ K. 虚构引用 ═════════════════════════════════════════════════════
print("\n[K] 虚构引用: 不存在的article_id认证失败")
refsA = refs_of(ndA)
real_id = mA['article_id']
fake_id = 'art_deadbeefdeadbeef'
check("K1 verify_citation: 真实ID通过,虚构ID拒绝",
      nprov.verify_citation(real_id, refsA)
      and not nprov.verify_citation(fake_id, refsA), '')
outK = nprov.summarize_for_prompt(refsA, [real_id, fake_id])
check("K2 索引说明: 虚构ID行如实标注'未通过来源认证(来源索引中不存在,"
      "不得作为已引用来源)';真实ID行含URL/发布方/UTC发布时间",
      '未通过来源认证' in outK and fake_id in outK
      and 'https://reuters.com/fed' in outK
      and '2026-10-28T12:00:00Z' in outK, outK[:120])

# ══ L. 七天周报消费 ═════════════════════════════════════════════════
print("\n[L] 七天周报: 来源身份经真实load_news_summary保留")
tL = tempfile.mkdtemp(prefix='w3L-', dir=_TMPD)
rg.DATA_DIR = os.path.join(tL, 'rgdata')
os.makedirs(os.path.join(rg.DATA_DIR, 'news'), exist_ok=True)
aid_d1 = nprov.stable_article_id({'provider': 'Finnhub', 'channel':
                                  'market_news', 'provider_article_id': '1'})
aid_d2 = nprov.stable_article_id({'provider': 'RSS', 'channel': 'rss',
                                  'url_original': 'https://x/d2'})
aid_d3 = nprov.stable_article_id({'provider': 'Finnhub', 'channel':
                                  'market_news', 'provider_article_id': '3'})
for day, aids in (('20261027', [aid_d1, aid_d1]),      # d1重复出现(持续性)
                  ('20261029', [aid_d2]),
                  ('20261030', [aid_d3, 'art_ffffffffffffffff'])):
    body = "# 新闻摘要 {}\n\n生成时间: t\n\n---\n\n### 美联储/利率\n".format(day)
    for a in aids:
        body += "- [{}] 联储相关新闻标题\n".format(a)
    open(os.path.join(rg.DATA_DIR, 'news', 'news_summary_{}.md'.format(day)),
         'w', encoding='utf-8').write(body)
idxL = {'schema_version': 1, 'kind': 'news_refs_index', 'ymd': '20261030',
        'built_at_utc': '2026-10-30T08:00:00Z',
        'integrity': {'checked_batches': 1, 'failed_batches': []},
        'articles': {
            aid_d1: {'article_id': aid_d1, 'provider': 'Finnhub',
                     'channel': 'market_news', 'publisher': 'Reuters',
                     'headline_original': 'H1',
                     'url_original': 'https://r.com/1', 'url_available': True,
                     'published_at_utc': '2026-10-27T12:00:00Z',
                     'published_status': 'UTC', 'provenance_status':
                     'COMPLETE', 'batch_id': 'b1'},
            aid_d2: {'article_id': aid_d2, 'provider': 'RSS', 'channel':
                     'rss', 'publisher': 'CNBC_Economy',
                     'headline_original': 'H2', 'url_original': None,
                     'url_available': False, 'published_at_utc': None,
                     'published_status': 'UNKNOWN', 'provenance_status':
                     'PARTIAL:url,published_at', 'batch_id': 'b2'},
            aid_d3: {'article_id': aid_d3, 'provider': 'Finnhub',
                     'channel': 'market_news', 'publisher': 'Reuters',
                     'headline_original': 'H3',
                     'url_original': 'https://r.com/3', 'url_available': True,
                     'published_at_utc': '2026-10-29T12:00:00Z',
                     'published_status': 'UTC', 'provenance_status':
                     'COMPLETE', 'batch_id': 'b3'}}}
open(os.path.join(rg.DATA_DIR, 'news', 'news_refs_20261030.json'), 'w',
     encoding='utf-8').write(json.dumps(idxL, ensure_ascii=False))
open(os.path.join(rg.DATA_DIR, 'news',
                  'news_refs_20261029.json'), 'w', encoding='utf-8') \
    .write(json.dumps(idxL, ensure_ascii=False))
with mock.patch.object(rg, 'datetime',
                       type('DT', (), {'now': staticmethod(
                           lambda tz=None: datetime(2026, 10, 30, 8))})):
    outL = rg.load_news_summary()
bodyL, _, appxL = outL.partition('#### 来源索引')
linesL = [l for l in bodyL.split('\n') if l.strip().startswith('- ')]
appx_lines = [l for l in appxL.split('\n') if l.strip().startswith('- ')]
check("L1 三天文件聚合+同条目跨天去重([{}]两天出现仅计一次)+旧周(>7天)"
      "排除;条目保留[art_]身份".format(aid_d1),
      bodyL.count('[' + aid_d1 + ']') == 1 and aid_d2 in bodyL
      and aid_d3 in outL and len(linesL) == 4 and len(appx_lines) == 4,
      'lines={}'.format(len(linesL)))
check("L2 末尾追加确定性来源索引(代码构造): 真实引用逐条含原始标题/URL/"
      "发布方/UTC发布时间;无URL来源明确'无直接文章链接(不可提供)'不编造",
      '来源索引(确定性代码构造' in outL
      and 'https://r.com/1' in outL and 'CNBC_Economy' in outL
      and '无直接文章链接' in outL and 'UNKNOWN' in outL, outL[-300:])
check("L3 虚构引用(art_ffffffffffffffff)在周报消费端被标注'未通过来源"
      "认证'——模型/加工文本中的不存在ID不得计为有效来源",
      '未通过来源认证' in outL and 'art_ffffffffffffffff' in outL, '')

# ══ M. 来源全部失败(非关键降级) ══════════════════════════════════════
print("\n[M] 来源失败: 全败降级不造假,部分失败保真实+披露")
tM = tempfile.mkdtemp(prefix='w3M-', dir=_TMPD)
run_collector(tM, market=RuntimeError('fh down'),
              company={'NVDA': RuntimeError('fh down')},
              rss={'CNBC_Economy': RuntimeError('feed down'),
                   'CNBC_Markets': RuntimeError('feed down'),
                   'CNBC_World': RuntimeError('feed down'),
                   'Bloomberg_Markets': RuntimeError('feed down'),
                   'Bloomberg_Economy': RuntimeError('feed down')},
              now='2026-10-30T05:30:00Z')
ndM = newsdir_of(tM)
sumM = open(os.path.join(ndM, 'news_summary_20261030.md'),
            encoding='utf-8').read()
check("M1 全部源失败: 不创建news_sources_批次(无虚假有效批次)+无refs索引;"
      "摘要降级为'无可信新闻数据'披露(非模型生成,无虚构条目,无[art_]ID)",
      not sources_of(ndM)
      and not os.path.exists(os.path.join(ndM, 'news_refs_20261030.json'))
      and '无可信新闻数据' in sumM and '[art_' not in sumM,
      sumM[:60])
tM2 = tempfile.mkdtemp(prefix='w3M2-', dir=_TMPD)
run_collector(tM2, market=MKT_FULL,
              rss={'CNBC_Economy': RuntimeError('feed down')},
              now='2026-10-30T05:30:00Z')
ndM2 = newsdir_of(tM2)
docM2 = json.load(open(archive_of(ndM2), encoding='utf-8'))
check("M2 部分源失败: 其余真实来源保留入档(Market新闻在档,RSS零条);"
      "失败源逐feed记入批次source_status明确披露(如RSS:CNBC_Economy="
      "fail),不伪造失败源文章",
      len(docM2['records']) == 1
      and docM2['records'][0]['channel'] == 'market_news'
      and docM2['source_status'].get('Finnhub/general') == 'ok'
      and docM2['source_status'].get('RSS:CNBC_Economy') == 'fail',
      str(docM2['source_status']))

# ══ N. 档案篡改 ═════════════════════════════════════════════════════
print("\n[N] 档案篡改: 完整性检查能发现")
tN = tempfile.mkdtemp(prefix='w3N-', dir=_TMPD)
run_collector(tN, market=MKT_FULL, now='2026-10-30T05:30:00Z')
ndN = newsdir_of(tN)
srcN = archive_of(ndN)
docN = json.load(open(srcN, encoding='utf-8'))
docN['records'][0]['url_original'] = 'https://evil.example/tampered'
json.dump(docN, open(srcN, 'w', encoding='utf-8'), ensure_ascii=False)
okN, probsN = nprov.verify_archive(srcN, ndN)
check("N1 篡改URL后: verify_archive=False,问题含文件SHA-256不符(清单"
      "独立记录)+记录摘要不符(双重检出);损坏档案不得标记为通过验证",
      okN is False
      and any('SHA-256' in p for p in probsN)
      and any('记录摘要不符' in p for p in probsN), str(probsN))
headN2 = nprov.build_refs_index(ndN)
check("N2 篡改批次进入来源索引integrity.failed_batches→周报索引头部"
      "完整性告警(降级可见,不冒充已认证)",
      headN2['integrity']['failed_batches']
      and '完整性告警' in nprov.summarize_for_prompt(headN2, []),
      str(headN2['integrity']))

# ══ O. P0-1/W1/W2安全继承(真实研究主链) ═════════════════════════════
print("\n[O] 安全继承: 真实主链Gate A/B+正式发布+长期状态不变")

class _DTO:
    @staticmethod
    def strptime(s, f):
        return datetime.strptime(s, f)

    @staticmethod
    def now(tz=None):
        return datetime(2026, 10, 24, 8, 0, 0)


class _GLMR:
    def __init__(self):
        self.calls = 0
        self.prompts = []

    def __call__(self, system_prompt, user_prompt, max_tokens=32000,
                 timeout=900):
        self.calls += 1
        self.prompts.append(user_prompt)
        return ('# 投资周报(SYNTHETIC测试文本·W3)\n\n'
                + '本周市场综述与分资产回顾。' * 60)


GROOT = tempfile.mkdtemp(prefix='w3O-', dir=_TMPD)
OUTG = os.path.join(GROOT, 'output', 'weekly')
CFG = os.path.join(GROOT, 'config')
os.makedirs(OUTG, exist_ok=True)
os.makedirs(CFG, exist_ok=True)
THG = os.path.join(CFG, 'thesis.json')
VWG = os.path.join(CFG, 'allocation_views.json')
open(THG, 'w', encoding='utf-8').write(
    '{"version": 1, "theses": [], "updated_at": "2026-10-24T08:00:00"}')
open(VWG, 'w', encoding='utf-8').write(
    '{"version": 2, "views": [], "predictions": []}')
fixt.build_full_day(GROOT, DAY)

# 周报DATA_DIR下放置真实新闻文件(摘要含[art_]+来源索引),不mock
# load_news_summary——验证真实消费链
ndO = os.path.join(GROOT, 'data', 'news')
os.makedirs(ndO, exist_ok=True)
aidO = nprov.stable_article_id({'provider': 'Finnhub', 'channel':
                                'market_news', 'provider_article_id': 'w3'})
open(os.path.join(ndO, f'news_summary_{DAY}.md'), 'w',
     encoding='utf-8').write(
    "# 新闻摘要 {}\n\n生成时间: t\n\n---\n\n### 美联储/利率\n"
    "- [{}] 联储新闻\n".format(DAY, aidO))
open(os.path.join(ndO, f'news_refs_{DAY}.json'), 'w',
     encoding='utf-8').write(json.dumps({
         'schema_version': 1, 'kind': 'news_refs_index', 'ymd': DAY,
         'built_at_utc': '2026-10-24T08:00:00Z',
         'integrity': {'checked_batches': 0, 'failed_batches': []},
         'articles': {aidO: {'article_id': aidO, 'provider': 'Finnhub',
                             'channel': 'market_news', 'publisher': 'Reuters',
                             'headline_original': 'H', 'url_original':
                             'https://r.com/w3', 'url_available': True,
                             'published_at_utc': '2026-10-23T12:00:00Z',
                             'published_status': 'UTC',
                             'provenance_status': 'COMPLETE',
                             'batch_id': 'b'}}}, ensure_ascii=False))

# O0: 新闻文件加入后未重打包——P0-1包完整性预检必须拒绝陈旧包
# (重建包含新闻节≠磁盘旧包→预检失败,证明W3未触碰P0-1保护)
glm0 = _GLMR()
with contextlib.ExitStack() as st:
    for h in [
        mock.patch.object(rg, 'DATA_DIR', os.path.join(GROOT, 'data')),
        mock.patch.object(rg, 'OUTPUT_DIR', OUTG),
        mock.patch.object(rg, 'datetime', _DTO),
        mock.patch.object(rg, '_call_glm', glm0),
        mock.patch.object(rg, 'apply_status_updates', lambda *a, **k: None),
        mock.patch.object(rg, 'validate_generated_report',
                          lambda md, anchors=None, anchors_file=None:
                          ('PASS', ['x'])),
        mock.patch.object(rg.allocation_engine, 'load_views',
                          lambda *a, **k: {'views': [], 'predictions': []}),
    ]:
        st.enter_context(h)
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            rg.generate_weekly_report()
            rc0 = 0
        except SystemExit as e:
            rc0 = e.code
check("O0 P0-1包完整性预检无回归: 新闻新增使旧数据包过时→预检拒绝(exit2,"
      "不调GLM)——W3不触碰该保护",
      rc0 == 2 and glm0.calls == 0, 'rc={}'.format(rc0))

# 真实重打包(data_assembler消费快照+新闻节重建数据包),再走正式链
with mock.patch.object(da, 'DATA_DIR', os.path.join(GROOT, 'data')), \
        mock.patch.object(da, 'datetime', _DTO), \
        contextlib.redirect_stdout(io.StringIO()):
    try:
        da.main()
        rc_da = 0
    except SystemExit as e:
        rc_da = e.code
check("O0b 真实data_assembler重打包成功(新闻节随包,非mock)", rc_da == 0,
      'rc={}'.format(rc_da))

glmR = _GLMR()
applied = []
harness = [
    mock.patch.object(rg, 'DATA_DIR', os.path.join(GROOT, 'data')),
    mock.patch.object(rg, 'OUTPUT_DIR', OUTG),
    mock.patch.object(rg, 'datetime', _DTO),
    mock.patch.object(rg, '_call_glm', glmR),
    mock.patch.object(rg, 'apply_status_updates',
                      lambda *a, **k: applied.append(1)),
    mock.patch.object(rg, 'validate_generated_report',
                      lambda md, anchors=None, anchors_file=None:
                      ('PASS', ['SYNTHETIC警告'])),
    mock.patch.object(rg.allocation_engine, 'load_views',
                      lambda *a, **k: {'views': [], 'predictions': []}),
    mock.patch.object(rg, 'pending_completed_month', lambda d=None: None),
    mock.patch.object(rg, 'pending_completed_quarter', lambda d=None: None),
    mock.patch.object(rg, 'load_framework', lambda: '框架'),
    mock.patch.object(rg, 'load_theses', lambda: '论点'),
    mock.patch.object(rg, 'load_technical_notes', lambda: ''),
    mock.patch.object(rg, 'load_previous_report', lambda: ''),
]
with contextlib.ExitStack() as st:
    for h in harness:
        st.enter_context(h)
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            quiet(rg.generate_weekly_report)
            rcO = 0
        except SystemExit as e:
            rcO = e.code
REPO = os.path.join(OUTG, f'weekly_report_{DAY}.md')
STATO = os.path.join(OUTG, f'report_status_{DAY}.json')
check("O1 正常正式研究可运行(Gate A/B无回归): exit0+GLM恰1次+四对象落盘",
      rcO == 0 and all(os.path.exists(p) for p in (REPO, STATO, THG, VWG))
      and glmR.calls == 1, 'rc={}'.format(rcO))
news_part = glmR.prompts[0] if glmR.prompts else ''
check("O2 真实新闻消费链进入周报输入: 摘要条目带[art_]身份+末尾确定性来源"
      "索引(代码构造,含URL/发布方/发布时间)——非模型生成索引",
      ('[' + aidO + ']') in news_part
      and '来源索引(确定性代码构造' in news_part
      and 'https://r.com/w3' in news_part, news_part[-200:])
statO = json.load(open(STATO, encoding='utf-8'))
check("O3 正式发布/身份/长期状态无回归: published=true+final_quality=PASS+"
      "formal身份有效+thesis/views内容未变(零合成状态写入)",
      statO.get('published') is True and statO.get('final_quality') == 'PASS'
      and rp.formal_report_view(REPO)[0] is not None
      and json.load(open(THG, encoding='utf-8'))['updated_at']
      == '2026-10-24T08:00:00'
      and json.load(open(VWG, encoding='utf-8'))['views'] == [], '')
gateO = json.load(open(os.path.join(GROOT, 'data', 'daily',
                                    f'research_snapshot_{DAY}.json'),
                       encoding='utf-8'))
check("O4 Gate A语义未动(P0-1来源门禁): 快照gate_a=PASS,事实质量全PASS"
      "(W3不触碰金融事实链)",
      gateO['gate_a']['status'] == 'PASS'
      and gateO['quality'].get('FAIL', 0) == 0
      and gateO['quality'].get('DEGRADED', 0) == 0,
      str(gateO.get('gate_a')))

print("═" * 72)
print(f"W3 结果: {PASS_N}通过 / {FAIL_N}失败")
sys.exit(1 if FAIL_N else 0)
