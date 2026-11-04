#!/usr/bin/env python3
"""IA-P0-2-W3-FIX4 联合验收测试(Markdown代码围栏上下文)。

对应指令IA-P0-2-W3-FIX4-DEV-v1.0 §八A~F+§九正式联合E2E:
  A 解析器代码围栏(三/四+反引号/波浪/缩进/长度匹配/未关闭/围栏后正常新闻)
  B 模型引用校验(仅围栏B失败/A+围栏B通过A认证/无合法引用/重试回退/围栏虚构ID)
  C 周报过滤(板块内围栏/合法格式ID/伪造板块标题/板块前围栏/跨日独立/
    未关闭围栏/围栏后正常新闻——围栏内假新闻不得被过滤洗白)
  D 真实来源可信链(A正常+B围栏,双档案真实存在,A双重认证/B位置即拒)
  E 历史安全回归(行首/正文夹带/独立合法/虚构ID/档案缺失/SHA损坏/
    GLM回退/Finnhub降级/同秒批次)
  F 负向敏感性(去围栏上下文/恢复先sanitize后解析顺序/围栏ID泄入legal_ids)
  E2E 正式研究链: 合法采集归档认证→摘要含围栏B→周报过滤与严格解析→
    B不成为正式引用+A进输入→新闻全败降级+Gate A/B+已发布保护+状态保护
真实模块(news_provenance围栏识别与解析/来源核验/news_collector.
validate_summary_citations/generate_news_summary/report_generator.
load_news_summary/正式研究入口);Finnhub/RSS/GLM全Mock,零真实API,
隔离临时目录。
"""
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
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
import data_assembler as da                    # noqa: E402
import news_collector as nc                    # noqa: E402
import feedparser                              # noqa: E402

PASS_N, FAIL_N = 0, 0
_TMPD = tempfile.mkdtemp(prefix='w3fix4-')
EPOCH_OK = calendar.timegm((2026, 10, 28, 12, 0, 0, 0, 0, 0))


def check(name, cond, detail=''):
    global PASS_N, FAIL_N
    if cond:
        PASS_N += 1
        print(f"  ✅ {name}")
    else:
        FAIL_N += 1
        print(f"  ❌ {name}  {detail}")


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def dt_mock():
    return mock.patch.object(
        rg, 'datetime', type('DT', (), {'now': staticmethod(
            lambda tz=None: datetime(2026, 10, 30, 8))}))


# ═══════════════════ 外部源Mock(Finnhub/RSS/GLM,同FIX3契约) ═════════

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


class FakeGLMText:
    """固定文本GLM Mock(可编程文本/异常;记录每次prompt)。"""

    def __init__(self, text):
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


def glm_err():
    g = FakeGLMText('')
    g.error = RuntimeError('GLM unavailable')
    return g


def run_collector(tmp, market=None, company=None, rss=None, glm=None,
                  now='2026-10-30T05:30:00Z', watch=None):
    """在隔离DATA_DIR下真实执行nc.run(),返回(glm, news目录)。"""
    nc.DATA_DIR = os.path.join(tmp, 'data')
    rss = rss or {}
    feed_by_url = {}
    for name, url in nc.RSS_FEEDS.items():
        v = rss.get(name, [])
        feed_by_url[url] = (FakeFeed(err=v) if isinstance(v, Exception)
                            else FakeFeed(entries=v))
    glm = glm or glm_err()
    with mock.patch.object(nc, 'fh_client', FakeFH(market, company)), \
            mock.patch.object(feedparser, 'parse',
                              lambda u: feed_by_url[u].parse(u)), \
            mock.patch.object(nc, 'WATCH_SYMBOLS', watch or ['NVDA']), \
            mock.patch.object(nc, 'OpenAI', glm()), \
            contextlib.redirect_stdout(io.StringIO()):
        nc.run(now_utc=now)
    return glm, os.path.join(nc.DATA_DIR, 'news')


def sources_of(nd, ymd='20261030'):
    return sorted(f for f in os.listdir(nd)
                  if f.startswith(f'news_sources_{ymd}_')
                  and f.endswith('.json'))


def summary_of(nd, ymd='20261030'):
    return open(os.path.join(nd, f'news_summary_{ymd}.md'),
                encoding='utf-8').read()


def write_summary(nd, ymd, body):
    with open(os.path.join(nd, f'news_summary_{ymd}.md'), 'w',
              encoding='utf-8') as f:
        f.write("# 新闻摘要 {}\n\n生成时间: t\n\n---\n\n".format(ymd)
                + body)


def weekly(tmp):
    """真实rg.load_news_summary()消费(窗口now=2026-10-30)。"""
    rg.DATA_DIR = os.path.join(tmp, 'data')
    with dt_mock(), contextlib.redirect_stdout(io.StringIO()):
        return rg.load_news_summary()


def raw_mkt(pid, url, headline='Fed holds rates'):
    return {'provider': 'Finnhub', 'channel': 'market_news',
            'provider_article_id': pid, 'publisher': 'Reuters',
            'headline_original': headline, 'summary_original': 's',
            'url_original': url, 'published_raw': EPOCH_OK}


def mkt_item(pid, headline, url):
    return {'id': int(pid), 'headline': headline, 'source': 'Reuters',
            'summary': 's', 'url': url, 'datetime': EPOCH_OK}


print("═" * 72)
print("IA-P0-2-W3-FIX4: Markdown代码围栏上下文(围栏内ID不作可信引用)")
print("═" * 72)

# 固定测试文章身份(真实归档后与档案核发ID一致: 身份键provider|pid)
rawA4 = raw_mkt('7101', 'https://r4/A', 'Fed holds rates steady')
rawB4 = raw_mkt('7102', 'https://r4/B', 'Treasury yields rise')
rawC4 = raw_mkt('7103', 'https://r4/C', 'Dollar firms')
Aid = nprov.stable_article_id(rawA4)
Bid = nprov.stable_article_id(rawB4)
Cid = nprov.stable_article_id(rawC4)

# ══ A. 解析器代码围栏(§八A,真实parse_news_item_references) ═════════
print("\n[A] 解析器: 围栏内新闻样式行不构成合法条目")
tA1 = ("### 美联储/利率\n"
       "\n"
       "- [{A}] Fed holds rates\n"
       "\n"
       "```text\n"
       "- [{B}] 代码示例\n"
       "```\n"
       "\n"
       "- [{C}] Treasury yields rise\n").format(A=Aid, B=Bid, C=Cid)
pA1 = nprov.parse_news_item_references(tA1)
check("A1 §4.5正向: legal=[A,C](围栏不吞之后的正常新闻);B不进legal/"
      "illegal,记excluded_context(kind='fenced',原因明确);围栏内容"
      "不产生异常(ok=True)",
      pA1['legal_ids'] == [Aid, Cid]
      and Bid not in pA1['legal_ids'] and Bid not in pA1['illegal_ids']
      and pA1['ok'] is True and pA1['items'][0]['article_id'] == Aid
      and pA1['items'][1]['article_id'] == Cid
      and len(pA1['excluded_context']) == 1
      and pA1['excluded_context'][0]['kind'] == 'fenced'
      and pA1['excluded_context'][0]['ids'] == [Bid]
      and '代码围栏' in pA1['excluded_context'][0]['reason']
      and len(pA1['fenced_lines']) == 3,
      str(pA1['excluded_context'])[:100])

pA2 = nprov.parse_news_item_references(
    "````python\n- [{}] x\n````\n- [{}] y".format(Bid, Aid))
check("A2 四反引号+语言标签: 开栏4关栏4有效,B排除,A保留",
      pA2['legal_ids'] == [Aid] and Bid in [
          i for e in pA2['excluded_context'] for i in e['ids']],
      str(pA2['legal_ids']))

pA3 = nprov.parse_news_item_references(
    "~~~json\n- [{}] x\n~~~\n- [{}] y".format(Bid, Aid))
check("A3 波浪围栏(带语言标签): 同样排除B,保留A",
      pA3['legal_ids'] == [Aid]
      and not pA3['illegal_ids'] and pA3['ok'] is True,
      str(pA3['legal_ids']))

pA4 = nprov.parse_news_item_references(
    " ```\n - [{}] x\n ```\n- [{}] y".format(Bid, Aid))
pA4b = nprov.parse_news_item_references(
    "    ```\n- [{}] x\n- [{}] y".format(Bid, Aid))
check("A4 Markdown缩进: 1空格缩进开栏有效(B排除);4空格缩进不构成"
      "围栏(属缩进代码块,B行首条目按普通文本行处理,不入围栏)",
      pA4['legal_ids'] == [Aid]
      and pA4b['legal_ids'] == [Bid, Aid]
      and pA4b['fenced_lines'] == [],
      str((pA4['legal_ids'], pA4b['legal_ids'])))

pA5 = nprov.parse_news_item_references(
    "```\n- [{}] x\n````\n- [{}] y".format(Bid, Aid))
pA5b = nprov.parse_news_item_references(
    "````\n- [{}] x\n```\n- [{}] y".format(Bid, Aid))
pA5c = nprov.parse_news_item_references(
    "```\n- [{}] x\n~~~\n- [{}] y".format(Bid, Aid))
check("A5 关栏匹配: 关栏长度≥开栏有效(3开4关→B排除A保留);关栏更短"
      "不算关(4开3关→围栏未关闭吞掉A);字符不匹配不算关(```开~~~关→"
      "未关闭吞掉A)——围栏状态如实持续",
      pA5['legal_ids'] == [Aid]
      and pA5b['legal_ids'] == [] and pA5c['legal_ids'] == [],
      str((pA5['legal_ids'], pA5b['legal_ids'], pA5c['legal_ids'])))

pA6 = nprov.parse_news_item_references(
    "- [{}] y\n```\n- [{}] x".format(Aid, Bid))
check("A6 未关闭围栏: 持续到文档结束,围栏后的B被排除(围栏前A保留)",
      pA6['legal_ids'] == [Aid]
      and len(pA6['fenced_lines']) == 2
      and pA6['excluded_context'][0]['ids'] == [Bid],
      str(pA6['legal_ids']))

mF1 = nprov.markdown_fence_map("```\nx\n```\ny")
mF2 = nprov.markdown_fence_map("- normal")
check("A7 共享markdown_fence_map: 开栏/内容/关栏行True,栏外False;"
      "文档级状态(未关闭围栏不泄漏到下一段独立文本)",
      mF1 == [True, True, True, False] and mF2 == [False], str(mF1))

# ══ B. 模型引用校验(§六FIX4-03,真实validate_summary_citations) ═════
print("\n[B] 校验: 围栏内引用不构成合法新闻引用(共用同一上下文规则)")
okB1, probsB1 = nc.validate_summary_citations(
    "```text\n- [{}] 代码示例\n```".format(Bid), {Aid, Bid})
check("B1 仅围栏内B(且B∈允许集): 整篇无合法行首引用→校验失败"
      "('合法引用槽位为空'),不因B是真实允许ID放行",
      okB1 is False
      and any('合法引用槽位为空' in p for p in probsB1), str(probsB1))

okB2, probsB2 = nc.validate_summary_citations(
    "### 美联储/利率\n- [{}] 正常摘要。\n```text\n- [{}] 示例\n```"
    .format(Aid, Bid), {Aid, Bid})
check("B2 A正常条目+B围栏(均∈允许集): 通过——A正常认证,B不因围栏"
      "取得来源资格也不单独致败",
      okB2 is True and probsB2 == [], str(probsB2))

okB3, probsB3 = nc.validate_summary_citations(
    "- [{}] a\n```\n- [art_deadbeefdeadbeef] x\n```".format(Aid), {Aid})
check("B3 围栏内虚构ID(不在允许集): 仍拒绝('含不允许的引用ID')——虚构"
      "检测覆盖全文,围栏不是藏匿处",
      okB3 is False and any('不允许' in p for p in probsB3), str(probsB3))

tB4 = tempfile.mkdtemp(prefix='f4B-', dir=_TMPD)
glmB4 = FakeGLMText('### 美联储/利率\n```text\n- [{}] 仅有代码示例\n```'
                    .format(Aid))
glmB4r, ndB4 = run_collector(
    tB4, market=[mkt_item(7101, 'Fed holds rates steady', 'https://r4/B4')],
    glm=glmB4)
sumB4 = summary_of(ndB4)
check("B4 真实generate_news_summary: 仅围栏引用输出两次未过→一次受控"
      "重试→确定性回退(模型原文不入摘要文件)",
      len(glmB4r.prompts) == 2
      and '【重要修正】' in glmB4r.prompts[1][1]['content']
      and '仅有代码示例' not in sumB4
      and '未通过来源引用校验' in sumB4 and '- [' in sumB4, sumB4[:60])

# ══ C. 周报过滤(§八C,真实load_news_summary) ═══════════════════════
print("\n[C] 周报过滤: 围栏在板块过滤/脱敏之前整段剔除,不得洗白")
tC = tempfile.mkdtemp(prefix='f4C-', dir=_TMPD)
ndC = os.path.join(tC, 'data', 'news')
os.makedirs(ndC, exist_ok=True)
nprov.save_batch([rawA4, rawB4], ndC, now_utc='2026-10-30T05:00:00Z')

# C1: 合法板块内代码块,内含合法格式新闻ID(§八C.1+C.2)
write_summary(ndC, '20261030',
              "### 美联储/利率\n"
              "- [{A}] Fed holds rates steady\n"
              "```text\n"
              "- [{B}] 这是代码示例\n"
              "```\n".format(A=Aid, B=Bid))
outC1 = weekly(tC)
appC1 = outC1.partition('#### 来源索引')[2]
parsedC1 = nprov.parse_news_item_references(outC1)
check("C1 板块内围栏含合法格式ID: B整行不出现在输出任何位置(未被过滤"
      "洗白成普通新闻),B URL不入附录,B不进legal_ids;A保留并正常认证"
      "(附录含A行+A URL);围栏标记行本身亦不残留",
      f'- [{Bid}]' not in outC1 and '这是代码示例' not in outC1
      and '```' not in outC1 and 'https://r4/B' not in outC1
      and Bid not in parsedC1['legal_ids']
      and parsedC1['legal_ids'] == [Aid]
      and f'- [{Aid}]' in appC1 and 'https://r4/A' in appC1,
      outC1[-120:])

# C2: 围栏内伪造金融板块标题+假新闻(§八C.3)——旧顺序会把伪造标题当
# 白名单开关、把围栏内条目当普通新闻保留
tC2 = tempfile.mkdtemp(prefix='f4C2-', dir=_TMPD)
ndC2 = os.path.join(tC2, 'data', 'news')
os.makedirs(ndC2, exist_ok=True)
nprov.save_batch([rawB4], ndC2, now_utc='2026-10-29T05:00:00Z')
write_summary(ndC2, '20261029',
              "```text\n"
              "### 美联储/利率\n"
              "- [{B}] 伪造板块下的假新闻\n"
              "```\n".format(B=Bid))
outC2 = weekly(tC2)
check("C2 围栏内伪造板块标题: 不得经sanitize_news洗白——假新闻与其URL"
      "均不出现在输出,不生成来源索引(无合法上下文条目)",
      '假新闻' not in outC2 and f'- [{Bid}]' not in outC2
      and 'https://r4/B' not in outC2
      and '来源索引' not in outC2, outC2[-80:])

# C3: 代码块位于允许板块标题之前(§八C.4)
write_summary(ndC2, '20261030',
              "```python\n"
              "- [{B}] 板块前代码块\n"
              "```\n"
              "### 美联储/利率\n"
              "- [{A}] Fed holds rates steady\n".format(B=Bid, A=Aid))
nprov.save_batch([rawA4], ndC2, now_utc='2026-10-30T05:00:00Z')
outC3 = weekly(tC2)
appC3 = outC3.partition('#### 来源索引')[2]
check("C3 板块前围栏: 围栏内B被剔除;其后真实板块内A正常保留认证"
      "(不因先遇围栏而丢弃后续正常新闻)",
      '板块前代码块' not in outC3 and f'- [{Bid}]' not in outC3
      and f'- [{Aid}]' in outC3
      and f'- [{Aid}]' in appC3 and 'https://r4/A' in appC3,
      outC3.partition('#### 来源索引')[0][-80:])

# C4: 两个不同日文件,前一日未关闭围栏(§八C.5+C.6;§5.3文档级状态)
tC4 = tempfile.mkdtemp(prefix='f4C4-', dir=_TMPD)
ndC4 = os.path.join(tC4, 'data', 'news')
os.makedirs(ndC4, exist_ok=True)
nprov.save_batch([rawA4, rawB4], ndC4, now_utc='2026-10-29T05:00:00Z')
write_summary(ndC4, '20261029',
              "### 美联储/利率\n"
              "- [{A}] Day1 normal news\n"
              "```\n"
              "- [{B}] unclosed swallow".format(A=Aid, B=Bid))
write_summary(ndC4, '20261030',
              "### 美联储/利率\n"
              "- [{B}] Day2 real news\n".format(B=Bid))
outC4 = weekly(tC4)
appC4 = outC4.partition('#### 来源索引')[2]
parsedC4 = nprov.parse_news_item_references(outC4)
check("C4 跨日独立: Day1未关闭围栏只吞Day1其后内容(unclosed行不出现),"
      "未关闭状态不带入Day2(Day2真实B条目保留且经档案正常认证)——"
      "每个news_summary文件独立处理围栏",
      'unclosed swallow' not in outC4
      and f'- [{Aid}]' in outC4 and f'- [{Bid}]' in outC4
      and parsedC4['legal_ids'] == [Aid, Bid]
      and 'https://r4/A' in appC4 and 'https://r4/B' in appC4,
      appC4[:100])

# C5: 正常新闻位于已关闭围栏之后(§八C.7,§4.5消费端对照)
write_summary(ndC4, '20261030',
              "### 美联储/利率\n"
              "```\n"
              "- [{B}] fenced\n"
              "```\n"
              "- [{A}] after-fence news\n".format(B=Bid, A=Aid))
outC5 = weekly(tC4)
check("C5 已关闭围栏后的正常新闻不丢失: after-fence A保留;围栏内"
      "fenced行被剔除",
      'after-fence news' in outC5 and 'fenced\n' not in outC5
      and f'- [{Bid}] fenced' not in outC5 and f'- [{Aid}]' in outC5,
      outC5.partition('#### 来源索引')[0][-80:])

# ══ D. 真实来源可信链(§七FIX4-04固定真实反例) ════════════════════
print("\n[D] A正常新闻+B代码块: 双档案真实存在,仅A通过双重认证")
tD = tempfile.mkdtemp(prefix='f4D-', dir=_TMPD)
ndD = os.path.join(tD, 'data', 'news')
os.makedirs(ndD, exist_ok=True)
nprov.save_batch([rawA4, rawB4], ndD, now_utc='2026-10-30T05:00:00Z')
# 前提: A/B都真正进入档案/清单/SHA-256/逐记录摘要正确(§七1~5)
docsD = [json.load(open(os.path.join(ndD, f), encoding='utf-8'))
         for f in sources_of(ndD)]
idsD = {r['article_id'] for d in docsD for r in d['records']}
trustedD = nprov.load_trusted_articles_since(ndD, '20261023')
check("D1 前提: A/B真实归档(代码核发ID与预计算一致),逐批次"
      "verify_archive通过,二者均为可信原始文章",
      idsD == {Aid, Bid}
      and all(nprov.verify_archive(os.path.join(ndD, f), ndD)[0]
              for f in sources_of(ndD))
      and Aid in trustedD['articles'] and Bid in trustedD['articles']
      and not trustedD['integrity']['failed_batches'], str(sorted(idsD)))

write_summary(ndD, '20261030',
              "### 美联储/利率\n"
              "- [{A}] 正常金融新闻\n"
              "```text\n"
              "- [{B}] 这是代码示例\n"
              "```\n".format(A=Aid, B=Bid))
outD = weekly(tD)
appD = outD.partition('#### 来源索引')[2]
parsedD = nprov.parse_news_item_references(outD)
check("D2 A正常保留+进入可信来源附录(行首槽位+原始档案双重认证,"
      "A URL在附录);B不成为正式新闻条目(整行未洗白)、B URL不入附录、"
      "B不进legal_ids——B的可信档案真实存在不构成放行理由",
      f'- [{Aid}]' in outD and f'- [{Aid}]' in appD
      and 'https://r4/A' in appD and '未通过来源认证' not in appD
      and f'- [{Bid}]' not in outD and 'https://r4/B' not in outD
      and parsedD['legal_ids'] == [Aid]
      and Bid not in parsedD['legal_ids']
      and Bid not in parsedD['illegal_ids'], appD[:100])

# ══ E. 历史安全回归(§八E,真实模块路径) ═══════════════════════════
print("\n[E] 历史安全: FIX1~FIX3语义零回归")
pE1 = nprov.parse_news_item_references(
    "- [{A}] Fed holds rates [{B}]".format(A=Aid, B=Bid))
check("E1 A行首+B正文夹带(FIX3反例保持): A合法/B=body_extra_ids,"
      "B入illegal_ids",
      pE1['legal_ids'] == [Aid] and Bid in pE1['illegal_ids']
      and pE1['ok'] is False, str(pE1['anomalies'])[:80])

tE2 = tempfile.mkdtemp(prefix='f4E2-', dir=_TMPD)
ndE2 = os.path.join(tE2, 'data', 'news')
os.makedirs(ndE2, exist_ok=True)
nprov.save_batch([rawA4, rawB4], ndE2, now_utc='2026-10-30T05:00:00Z')
write_summary(ndE2, '20261030',
              "### 美联储/利率\n- [{A}] a\n- [{B}] b\n".format(
                  A=Aid, B=Bid))
outE2 = weekly(tE2)
appE2 = outE2.partition('#### 来源索引')[2]
check("E2 两条独立合法新闻: 均正常认证(FIX3§6.4保持)",
      sorted(nprov.parse_news_item_references(outE2)['legal_ids'])
      == sorted([Aid, Bid])
      and 'https://r4/A' in appE2 and 'https://r4/B' in appE2, '')

okE3, probsE3 = nc.validate_summary_citations(
    '- [art_deadbeefdeadbeef] 摘要。', {Aid})
check("E3 模型虚构ID: 拒绝(FIX1-03保持)",
      okE3 is False and any('不允许' in p for p in probsE3), '')

tE4 = tempfile.mkdtemp(prefix='f4E4-', dir=_TMPD)
ndE4 = os.path.join(tE4, 'data', 'news')
os.makedirs(ndE4, exist_ok=True)
write_summary(ndE4, '20261030',
              '### 美联储/利率\n- [{}] Fed holds rates\n'.format(Aid))
outE4 = weekly(tE4)
check("E4 来源档案缺失: '未通过来源认证',不虚构URL",
      '未通过来源认证' in outE4 and 'https://r4/A' not in outE4,
      outE4.partition('#### 来源索引')[2][:80])

tE5 = tempfile.mkdtemp(prefix='f4E5-', dir=_TMPD)
ndE5 = os.path.join(tE5, 'data', 'news')
os.makedirs(ndE5, exist_ok=True)
nprov.save_batch([rawA4], ndE5, now_utc='2026-10-30T05:00:00Z')
write_summary(ndE5, '20261030',
              '### 美联储/利率\n- [{}] Fed holds rates\n'.format(Aid))
with open(os.path.join(ndE5, sources_of(ndE5)[0]), 'a',
          encoding='utf-8') as f:
    f.write(' ')
outE5 = weekly(tE5)
check("E5 档案SHA-256损坏: 不得认证+完整性告警",
      '未通过来源认证' in outE5 and '完整性告警' in outE5, outE5[-100:])

tE6 = tempfile.mkdtemp(prefix='f4E6-', dir=_TMPD)
glmE6r, ndE6 = run_collector(
    tE6, market=[mkt_item(7101, 'Fed holds rates steady', 'https://r4/E6')])
sumE6 = summary_of(ndE6)
check("E6 GLM异常安全回退: 一次调用即异常→确定性标题回退(代码核发"
      "真实ID,无模型文本入摘要)",
      len(glmE6r.prompts) == 1 and '- [' in sumE6
      and '## ' in sumE6, sumE6[:60])

tE7 = tempfile.mkdtemp(prefix='f4E7-', dir=_TMPD)
glmE7r, ndE7 = run_collector(tE7, market=RuntimeError('Finnhub down'),
                             company={'NVDA': RuntimeError('down')})
sumE7 = summary_of(ndE7)
check("E7 Finnhub失败降级: 全败不建批次(零news_sources档案),固定降级"
      "披露(明示非模型生成,无虚构条目)",
      not sources_of(ndE7)
      and '采集失败' in sumE7 and '非模型生成' in sumE7, sumE7[:60])

tE8 = tempfile.mkdtemp(prefix='f4E8-', dir=_TMPD)
ndE8 = os.path.join(tE8, 'data', 'news')
os.makedirs(ndE8, exist_ok=True)
nprov.save_batch([rawA4], ndE8, now_utc='2026-10-30T05:00:00Z')
nprov.save_batch([rawB4], ndE8, now_utc='2026-10-30T05:00:00Z')
check("E8 同秒批次不可覆盖: 两次save_batch两个独立批次文件,均通过"
      "verify_archive(W3/FIX1保持)",
      len(sources_of(ndE8)) == 2
      and all(nprov.verify_archive(os.path.join(ndE8, f), ndE8)[0]
              for f in sources_of(ndE8)), str(sources_of(ndE8)))

# ══ F. 负向敏感性(§八F,退化必须被真实模块检出) ═══════════════════
print("\n[F] 负向敏感性: 三种退化下新断言必失败")
real_parse = nprov.parse_news_item_references

# F1: 去掉解析器围栏上下文(围栏映射恒False=FIX3解析器形态)
with mock.patch.object(nprov, 'markdown_fence_map', lambda text: [
        False] * len(str(text or '').splitlines())):
    pF1 = nprov.parse_news_item_references(
        "```text\n- [{}] x\n```".format(Bid))
    outF1 = weekly(tD)
check("F1 解析器去围栏上下文→围栏内B直接进入legal_ids且经周报错误认证"
      "(B URL入附录)——C1/D2断言对此必失败",
      pF1['legal_ids'] == [Bid]
      and Bid in nprov.extract_citations(
          outF1.partition('#### 来源索引')[2])
      and 'https://r4/B' in outF1, pF1['legal_ids'])

# F2: 周报恢复旧顺序(先sanitize_news(content)再解析,无预剔除)
with mock.patch.object(nprov, 'strip_code_fences', lambda text: text):
    outF2 = weekly(tD)
check("F2 恢复'sanitize_news(原文)→解析'旧顺序→围栏标记行被丢、围栏内"
      "B行被洗白成普通新闻且被正式解析认证(B URL入附录)——C1/D2断言"
      "对此必失败",
      f'- [{Bid}]' in outF2.partition('#### 来源索引')[0]
      and 'https://r4/B' in outF2, outF2[-120:])


# F3: 消费端把围栏内ID并入legal_ids(误将排除上下文当合法引用)
def parse_leak_fenced(text):
    p = real_parse(text)
    extra = [i for e in (p.get('excluded_context') or [])
             for i in (e.get('ids') or [])]
    if extra:
        p = dict(p)
        p['legal_ids'] = nprov._uniq_ids(list(p['legal_ids']) + extra)
    return p


# F3a解析器级: 泄入包装下,真实parse对含围栏输入的legal_ids即含B
with mock.patch.object(nprov, 'parse_news_item_references',
                       parse_leak_fenced):
    pF3a = nprov.parse_news_item_references(
        "```text\n- [{}] x\n```".format(Bid))
# F3b消费级: 泄入包装+原文直通(双重退化)→真实周报把B当合法引用认证
with mock.patch.object(nprov, 'parse_news_item_references',
                       parse_leak_fenced), \
        mock.patch.object(nprov, 'strip_code_fences', lambda text: text):
    outF3 = weekly(tD)
check("F3 围栏ID泄入legal_ids→解析器级legal含B;真实周报将B当合法引用"
      "认证(B行+URL入附录)——C1/D2断言对此必失败",
      pF3a['legal_ids'] == [Bid]
      and f'- [{Bid}]' in outF3.partition('#### 来源索引')[2]
      and 'https://r4/B' in outF3, pF3a['legal_ids'])

# ══ E2E. 正式联合E2E(§九12项) ═════════════════════════════════════
print("\n[E2E] 合法采集归档→摘要含围栏B→周报严格解析→Gate/保护")


class _DTO:
    @staticmethod
    def strptime(s, f):
        return datetime.strptime(s, f)

    @staticmethod
    def now(tz=None):
        return datetime(2026, 10, 24, 8, 0, 0)


class _GLMR:
    def __init__(self, tag):
        self.calls = 0
        self.prompts = []
        self._tag = tag

    def __call__(self, system_prompt, user_prompt, max_tokens=32000,
                 timeout=900):
        self.calls += 1
        self.prompts.append(user_prompt)
        return ('# 投资周报(SYNTHETIC测试文本·W3-FIX4-{})\n\n'.format(
            self._tag) + '本周市场综述与分资产回顾。' * 60)


def e2e_harness(groot, outd, cfg, glmr):
    return [
        mock.patch.object(rg, 'DATA_DIR', os.path.join(groot, 'data')),
        mock.patch.object(rg, 'OUTPUT_DIR', outd),
        mock.patch.object(rg, 'datetime', _DTO),
        mock.patch.object(rg, '_call_glm', glmr),
        mock.patch.object(rg, 'apply_status_updates', lambda *a, **k: None),
        mock.patch.object(rg, 'validate_generated_report',
                          lambda md, anchors=None, anchors_file=None:
                          ('PASS', ['SYNTHETIC警告'])),
        mock.patch.object(rg.allocation_engine, 'load_views',
                          lambda *a, **k: {'views': [], 'predictions': []}),
        mock.patch.object(rg, 'pending_completed_month', lambda d=None: None),
        mock.patch.object(rg, 'pending_completed_quarter',
                          lambda d=None: None),
        mock.patch.object(rg, 'load_framework', lambda: '框架'),
        mock.patch.object(rg, 'load_theses', lambda: '论点'),
        mock.patch.object(rg, 'load_technical_notes', lambda: ''),
        mock.patch.object(rg, 'load_previous_report', lambda: ''),
    ]


DAY = '20261024'
# ── E2E-A: 合法新闻成功链+围栏B(§九1~8,10~12) ──
GA = tempfile.mkdtemp(prefix='f4E2EA-', dir=_TMPD)
OUTA, CFG = os.path.join(GA, 'output', 'weekly'), os.path.join(
    GA, 'config')
os.makedirs(OUTA, exist_ok=True)
os.makedirs(CFG, exist_ok=True)
THA, VWA = os.path.join(CFG, 'thesis.json'), os.path.join(
    CFG, 'allocation_views.json')
open(THA, 'w', encoding='utf-8').write(
    '{"version": 1, "theses": [], "updated_at": "2026-10-24T08:00:00"}')
open(VWA, 'w', encoding='utf-8').write(
    '{"version": 2, "views": [], "predictions": []}')
fixt.build_full_day(GA, DAY)
rawEa = raw_mkt('7301', 'https://r4/e2eA', 'Fed holds rates steady')
rawEb = raw_mkt('7302', 'https://r4/e2eB', 'Treasury yields rise')
AidE = nprov.stable_article_id(rawEa)
BidE = nprov.stable_article_id(rawEb)
# GLM新闻摘要: 真实合法A引用+代码块中嵌入真实B ID(§九5)
glmN = FakeGLMText(
    '### 美联储/利率\n- [{}] 美联储政策立场稳定,市场关注未来路径。\n'
    '```text\n- [{}] 代码示例\n```\n'.format(AidE, BidE))
glmN_r, ndE = run_collector(
    GA, market=[mkt_item(7301, 'Fed holds rates steady', 'https://r4/e2eA'),
                mkt_item(7302, 'Treasury yields rise', 'https://r4/e2eB')],
    glm=glmN, now='2026-10-24T05:30:00Z')
with mock.patch.object(da, 'DATA_DIR', os.path.join(GA, 'data')), \
        mock.patch.object(da, 'datetime', _DTO), \
        contextlib.redirect_stdout(io.StringIO()):
    try:
        da.main()
    except SystemExit:
        pass
glmR = _GLMR('A')
with contextlib.ExitStack() as st:
    for h in e2e_harness(GA, OUTA, CFG, glmR):
        st.enter_context(h)
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            rg.generate_weekly_report()
            rcE = 0
        except SystemExit as e:
            rcE = e.code
statE = json.load(open(os.path.join(OUTA, f'report_status_{DAY}.json'),
                       encoding='utf-8'))
gateE = json.load(open(os.path.join(GA, 'data', 'daily',
                                    f'research_snapshot_{DAY}.json'),
                       encoding='utf-8'))
trustedE = nprov.load_trusted_articles_since(ndE, '20261017')
check("E2E-A1 合法采集→原始档案保存→完整性认证→GLM成功恰1次(合法A引用"
      "+围栏B示例通过校验并保存摘要);A/B均入可信集合",
      rcE == 0 and len(glmN_r.prompts) == 1
      and AidE in trustedE['articles'] and BidE in trustedE['articles']
      and not trustedE['integrity']['failed_batches']
      and '- [' + AidE + ']' in summary_of(ndE, DAY), f'rc={rcE}')
promptA = glmR.prompts[0]
# 提示词中B行的合法存在形态=数据包"研究上下文"对原始摘要文件的逐字
# 内嵌(data_assembler既有通道,围栏原样保留);判定标准=每个B行都必须
# 仍处于Markdown围栏内,且不出现在认证附录/新闻输入区块
linesA = promptA.split('\n')
fmapA = nprov.markdown_fence_map(promptA)
b_rows_ok = all(
    fmapA[i] for i, l in enumerate(linesA) if l.strip().startswith(
        '- [' + BidE + ']'))
# 附录段=新闻块内'#### 来源索引'起至下一区块'## 本周市场数据'止
# (其后数据包以"研究上下文"逐字内嵌原始摘要文件,B行合法存在于其中
# 的围栏内——不属认证附录)
appA_in_prompt = promptA.partition('#### 来源索引')[2].partition(
    '## 本周市场数据')[0]
check("E2E-A2 周报过滤与严格位置解析: 围栏B不成为正式新闻引用——B行"
      "仅以数据包研究上下文的围栏内代码示例形态存在(全部处于围栏区),"
      "认证附录无B行/无B URL;合法A正常进入周报新闻输入(来源索引+A的"
      "认证URL)",
      glmR.calls == 1
      and ('- [' + BidE + ']') in promptA and b_rows_ok
      and '- [' + BidE + ']' not in appA_in_prompt
      and 'https://r4/e2eB' not in promptA
      and '#### 来源索引' in promptA
      and 'https://r4/e2eA' in promptA,
      appA_in_prompt[:80])
check("E2E-A3 Gate A/B不回归+发布成功(published,digest==正式文件摘要)",
      gateE['gate_a']['status'] == 'PASS'
      and gateE['quality'].get('FAIL', 0) == 0
      and statE.get('published') is True
      and statE.get('gate_b') == 'PASS'
      and statE.get('report_digest') == sha(
          os.path.join(OUTA, f'weekly_report_{DAY}.md'))[:16], '')
check("E2E-A4 已发布报告保护: 无_UNVALIDATED残留,正式文件在档",
      not any('_UNVALIDATED' in f for f in os.listdir(OUTA))
      and os.path.exists(os.path.join(OUTA, f'weekly_report_{DAY}.md')),
      '')
check("E2E-A5 长期状态保护(thesis/views未变)",
      json.load(open(THA, encoding='utf-8'))['updated_at']
      == '2026-10-24T08:00:00'
      and json.load(open(VWA, encoding='utf-8'))['views'] == [], '')

# ── E2E-B: 新闻源全部失败→非关键降级(§九9) ──
GB = tempfile.mkdtemp(prefix='f4E2EB-', dir=_TMPD)
OUTB, CFG2 = os.path.join(GB, 'output', 'weekly'), os.path.join(
    GB, 'config')
os.makedirs(OUTB, exist_ok=True)
os.makedirs(CFG2, exist_ok=True)
open(os.path.join(CFG2, 'thesis.json'), 'w', encoding='utf-8').write(
    '{"version": 1, "theses": [], "updated_at": "2026-10-24T08:00:00"}')
open(os.path.join(CFG2, 'allocation_views.json'), 'w',
     encoding='utf-8').write(
    '{"version": 2, "views": [], "predictions": []}')
fixt.build_full_day(GB, DAY)
ndEB = os.path.join(GB, 'data', 'news')
os.makedirs(ndEB, exist_ok=True)
open(os.path.join(ndEB, f'news_summary_{DAY}.md'), 'w',
     encoding='utf-8').write(
    "# 新闻摘要 {}\n\n生成时间: t\n\n---\n\n## 本周无可信新闻数据\n\n"
    "(全部/关键新闻来源采集失败,未创建新闻来源批次;本段为降级披露,"
    "非模型生成,不含任何虚构新闻条目。失败通道: Finnhub/general=ERROR)"
    .format(DAY))
with mock.patch.object(da, 'DATA_DIR', os.path.join(GB, 'data')), \
        mock.patch.object(da, 'datetime', _DTO), \
        contextlib.redirect_stdout(io.StringIO()):
    try:
        da.main()
    except SystemExit:
        pass
glmR2 = _GLMR('B')
with contextlib.ExitStack() as st:
    for h in e2e_harness(GB, OUTB, CFG2, glmR2):
        st.enter_context(h)
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            rg.generate_weekly_report()
            rcE2 = 0
        except SystemExit as e:
            rcE2 = e.code
statE2 = json.load(open(os.path.join(OUTB, f'report_status_{DAY}.json'),
                        encoding='utf-8'))
gateE2 = json.load(open(os.path.join(GB, 'data', 'daily',
                                     f'research_snapshot_{DAY}.json'),
                        encoding='utf-8'))
check("E2E-B1 新闻源全部失败: 维持非关键降级(正式研究链exit0+GLM恰1次"
      "+published+Gate A/B PASS+无[art_]认证)——金融事实门禁不因新闻改变",
      rcE2 == 0 and glmR2.calls == 1
      and statE2.get('published') is True
      and gateE2['gate_a']['status'] == 'PASS'
      and statE2.get('gate_b') == 'PASS'
      and '[art_' not in glmR2.prompts[0]
      and '来源索引' not in glmR2.prompts[0], f'rc={rcE2}')

print("═" * 72)
print(f"W3-FIX4 结果: {PASS_N}通过 / {FAIL_N}失败")
sys.exit(1 if FAIL_N else 0)
