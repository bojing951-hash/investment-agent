#!/usr/bin/env python3
"""IA-P0-2-W3-FIX5 联合验收测试(围栏开闭语法两处CommonMark修正)。

对应指令IA-P0-2-W3-FIX5-DEV-v1.0 §七A~F:
  A 围栏开栏(真实_fence_open): 合法波浪号info含波浪号/多波浪/含反引号/
    普通波浪围栏;反引号info含反引号仍拒(CommonMark限制);<3同字符非围栏;
    0~3前导空格既有规则保持
  B 围栏关闭(真实_fence_close): 尾随TAB合法/波浪关栏+TAB/尾随空格TAB
    混合/关栏后非法文字拒/前导TAB拒/长度与字符不匹配拒/0~3前导空格与
    尾随普通空格继续允许
  C 两组真实固定反例(真实save_batch/verify_archive/load_trusted_articles_
    since+真实load_news_summary): 合法波浪号info围栏/合法尾随TAB关栏——
    B不入合法集合与附录,A保留并正常认证,A URL正确
  D 模型摘要校验(真实validate_summary_citations): 仅围栏B失败/围栏B后
    正常A通过且B不获引用资格/普通合法新闻不回归
  E 历史回归(FIX3正文夹带/普通反引号围栏/普通波浪围栏/未关闭围栏/跨日
    独立/七天去重与裁剪/GLM安全回退/全败非关键降级/档案完整性)
  F 负向敏感性(恢复错误波浪info禁令→反例A必败;恢复旧strip(' ')→反例B
    必败;错误整行strip(' \\t')→非法前导TAB被接受;周报层面B被认证或A
    丢失→真实load_news_summary测试必败)
真实模块(news_provenance._fence_open/_fence_close/markdown_fence_map/
strip_code_fences/parse_news_item_references/save_batch/verify_archive/
load_trusted_articles_since;news_collector.validate_summary_citations/
run;report_generator.load_news_summary);Finnhub/RSS/GLM全Mock,零真实
API,隔离临时目录;不复制围栏实现到测试自证。
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

import news_provenance as nprov                # noqa: E402
import report_generator as rg                  # noqa: E402
import news_collector as nc                    # noqa: E402
import feedparser                              # noqa: E402

PASS_N, FAIL_N = 0, 0
_TMPD = tempfile.mkdtemp(prefix='w3fix5-')
EPOCH_OK = calendar.timegm((2026, 10, 28, 12, 0, 0, 0, 0, 0))


def check(name, cond, detail=''):
    global PASS_N, FAIL_N
    if cond:
        PASS_N += 1
        print(f"  ✅ {name}")
    else:
        FAIL_N += 1
        print(f"  ❌ {name}  {detail}")


def dt_mock():
    return mock.patch.object(
        rg, 'datetime', type('DT', (), {'now': staticmethod(
            lambda tz=None: datetime(2026, 10, 30, 8))}))


# ═══════════════════ 外部源Mock(Finnhub/RSS/GLM,同FIX3/FIX4契约) ══════

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
print("IA-P0-2-W3-FIX5: 围栏开闭语法两处CommonMark修正")
print("═" * 72)

# 固定测试文章身份(真实归档后与档案核发ID一致: 身份键provider|pid)
rawA5 = raw_mkt('7201', 'https://r5/A', 'Fed holds rates steady')
rawB5 = raw_mkt('7202', 'https://r5/B', 'Treasury yields rise')
Aid = nprov.stable_article_id(rawA5)
Bid = nprov.stable_article_id(rawB5)

# ══ A. 围栏开栏(§七A,真实_fence_open) ═══════════════════════════════
print("\n[A] 开栏: 波浪号info按CommonMark允许含波浪号与反引号")
real_open = nprov._fence_open

check("A1 合法波浪号info含波浪号('~~~ python ~edition')→('~',3);"
      "反引号围栏语言标签保持",
      real_open('~~~ python ~edition') == ('~', 3)
      and real_open('```python') == ('`', 3))

check("A2 波浪号info含多个波浪号('~~~ python ~ ~')→('~',3)",
      real_open('~~~ python ~ ~') == ('~', 3))

check("A3 波浪号info含反引号(CommonMark规范示例'~~~ aa ``` ~~'形态)"
      "→('~',3),不受反引号限制",
      real_open('~~~ aa ``` ~~') == ('~', 3)
      and real_open('~~~ py`x') == ('~', 3))

check("A4 普通波浪号围栏('~~~json')与带空格info('~~~ json')均有效",
      real_open('~~~json') == ('~', 3)
      and real_open('~~~ json') == ('~', 3))

check("A5 反引号围栏info含反引号→仍拒(CommonMark限制保持);波浪围栏"
      "不受此限(两字符规则不再对称)",
      real_open('``` py`x') is None
      and real_open('~~~ py`x') == ('~', 3))

check("A6 开栏<3个连续相同字符不是围栏;0~3前导空格既有规则保持"
      "(1/3空格有效,4空格=缩进代码块不构成围栏)",
      real_open('~~python') is None
      and real_open('``python') is None
      and real_open(' ```') == ('`', 3)
      and real_open('   ~~~') == ('~', 3)
      and real_open('    ```') is None)

# ══ B. 围栏关闭(§七B,真实_fence_close) ═════════════════════════════
print("\n[B] 关栏: 行首缩进与行尾空白独立处理,尾随TAB合法")
real_close = nprov._fence_close

check("B1 三个反引号后接实际TAB→合法关栏('```\\t'关闭(`,3)围栏)",
      real_close('```\t', '`', 3) is True)

check("B2 波浪号关栏后接实际TAB→合法关栏('~~~\\t'关闭(~,3)围栏)",
      real_close('~~~\t', '~', 3) is True)

check("B3 尾随多个空格与TAB混合合法;尾随普通空格继续合法;更长关栏"
      "(≥开栏长度)合法",
      real_close('```  \t \t', '`', 3) is True
      and real_close('``` ', '`', 3) is True
      and real_close('````', '`', 3) is True)

check("B4 关闭标记后含非空白文字→不是关栏(围栏继续)",
      real_close('``` tail', '`', 3) is False
      and real_close('```py', '`', 3) is False)

check("B5 前导TAB缩进的关闭标记→拒绝(TAB不是合法围栏缩进)",
      real_close('\t```', '`', 3) is False
      and real_close('   \t```', '`', 3) is False)

check("B6 长度短于开栏→不是关栏;开闭字符不匹配→不是关栏;0~3前导"
      "空格的关栏继续合法",
      real_close('```', '`', 4) is False
      and real_close('```', '~', 3) is False
      and real_close('  ```', '`', 3) is True)

# ══ C. 两组真实固定反例(§七C,真实档案链+真实load_news_summary) ═════
print("\n[C] 固定反例A(波浪info)与反例B(尾随TAB关栏): 全链路验收")
tC = tempfile.mkdtemp(prefix='f5C-', dir=_TMPD)
ndC = os.path.join(tC, 'data', 'news')
os.makedirs(ndC, exist_ok=True)
nprov.save_batch([rawA5, rawB5], ndC, now_utc='2026-10-30T05:00:00Z')

docsC = [json.load(open(os.path.join(ndC, f), encoding='utf-8'))
         for f in sources_of(ndC)]
idsC = {r['article_id'] for d in docsC for r in d['records']}
trustedC = nprov.load_trusted_articles_since(ndC, '20261023')
check("C0 前提(§六.8): A/B真实归档(代码核发ID与预计算一致),逐批次"
      "verify_archive通过,二者均在可信原始文章集合——B档案存在不构成"
      "后续放行理由,档案完整性验证继续生效",
      idsC == {Aid, Bid}
      and all(nprov.verify_archive(os.path.join(ndC, f), ndC)[0]
              for f in sources_of(ndC))
      and Aid in trustedC['articles'] and Bid in trustedC['articles']
      and not trustedC['integrity']['failed_batches'], str(sorted(idsC)))

# ── 反例A: 合法波浪号info(§四强制反例全文形态) ──
txtCA = "~~~ python ~edition\n- [{}] 代码示例\n~~~\n- [{}] 合法新闻" \
    .format(Bid, Aid)
fmapCA = nprov.markdown_fence_map(txtCA)
stripCA = nprov.strip_code_fences(txtCA)
pCA = nprov.parse_news_item_references(txtCA)
check("CA1 反例A解析链(§六1~5): 开栏成功/fence_map前3行True栏外False/"
      "strip仅剔除围栏3行/legal_ids仅[A],B在excluded_context",
      fmapCA == [True, True, True, False]
      and stripCA == "- [{}] 合法新闻".format(Aid)
      and pCA['legal_ids'] == [Aid]
      and Bid not in pCA['legal_ids'] and Bid not in pCA['illegal_ids']
      and [i for e in pCA['excluded_context'] for i in e['ids']] == [Bid],
      str(pCA['legal_ids']))

write_summary(ndC, '20261030',
              "### 美联储/利率\n"
              "~~~ python ~edition\n"
              "- [{B}] 代码示例\n"
              "~~~\n"
              "- [{A}] 合法金融新闻\n".format(B=Bid, A=Aid))
outCA = weekly(tC)
appCA = outCA.partition('#### 来源索引')[2]
parsedCA = nprov.parse_news_item_references(outCA)
check("CA2 反例A周报(§六6~7): B不进合法新闻集合(B整行/B URL不出现在"
      "输出任何位置),A保留并正常进入可信来源附录(A行+A URL),没有因"
      "围栏误判删除A",
      f'- [{Bid}]' not in outCA and '代码示例' not in outCA
      and 'https://r5/B' not in outCA
      and parsedCA['legal_ids'] == [Aid]
      and f'- [{Aid}]' in outCA and f'- [{Aid}]' in appCA
      and 'https://r5/A' in appCA, appCA[:100])

# ── 反例B: 合法尾随TAB关栏(§五强制反例全文形态,实际TAB字符) ──
txtCB = "```python\n- [{}] 代码示例\n```\t\n- [{}] 合法新闻" \
    .format(Bid, Aid)
fmapCB = nprov.markdown_fence_map(txtCB)
stripCB = nprov.strip_code_fences(txtCB)
pCB = nprov.parse_news_item_references(txtCB)
check("CB1 反例B解析链: '```'+TAB合法关栏/fence_map前3行True/strip仅"
      "剔除围栏3行/legal_ids仅[A]——不能错误丢失A",
      fmapCB == [True, True, True, False]
      and stripCB == "- [{}] 合法新闻".format(Aid)
      and pCB['legal_ids'] == [Aid]
      and Bid not in pCB['legal_ids'], str(pCB['legal_ids']))

tCB = tempfile.mkdtemp(prefix='f5CB-', dir=_TMPD)
ndCB = os.path.join(tCB, 'data', 'news')
os.makedirs(ndCB, exist_ok=True)
nprov.save_batch([rawA5, rawB5], ndCB, now_utc='2026-10-30T05:00:00Z')
write_summary(ndCB, '20261030',
              "### 美联储/利率\n"
              "```python\n"
              "- [{B}] 代码示例\n"
              "```\t\n"
              "- [{A}] 合法金融新闻\n".format(B=Bid, A=Aid))
outCB = weekly(tCB)
appCB = outCB.partition('#### 来源索引')[2]
parsedCB = nprov.parse_news_item_references(outCB)
check("CB2 反例B周报: 关闭标记合法→B被排除(B行/B URL不出现),A保留并"
      "正常进入可信来源附录(A行+A URL)——不因尾随TAB误判吞掉A",
      f'- [{Bid}]' not in outCB and '代码示例' not in outCB
      and 'https://r5/B' not in outCB
      and parsedCB['legal_ids'] == [Aid]
      and f'- [{Aid}]' in outCB and f'- [{Aid}]' in appCB
      and 'https://r5/A' in appCB, appCB[:100])

# ══ D. 模型摘要校验(§七D,真实validate_summary_citations) ═══════════
print("\n[D] 校验: 两种新合法围栏形态下,B不取得引用资格")
okD1a, probsD1a = nc.validate_summary_citations(
    "~~~ python ~edition\n- [{}] 代码示例\n~~~".format(Bid), {Aid, Bid})
okD1b, probsD1b = nc.validate_summary_citations(
    "```\n- [{}] 代码示例\n```\t".format(Bid), {Aid, Bid})
check("D1 仅围栏内B(且B∈允许集;波浪info形态与尾随TAB关栏形态): 整篇"
      "无合法行首引用→校验失败('合法引用槽位为空')",
      okD1a is False and okD1b is False
      and any('合法引用槽位为空' in p for p in probsD1a)
      and any('合法引用槽位为空' in p for p in probsD1b),
      str(probsD1a))

okD2a, probsD2a = nc.validate_summary_citations(
    "- [{}] 正常摘要。\n~~~ python ~edition\n- [{}] 示例\n~~~"
    .format(Aid, Bid), {Aid, Bid})
okD2b, probsD2b = nc.validate_summary_citations(
    "- [{}] 正常摘要。\n```\n- [{}] 示例\n```\t".format(Aid, Bid),
    {Aid, Bid})
check("D2 围栏B后正常A(两形态): 通过——A正常认证,B不因围栏取得来源"
      "资格也不单独致败",
      okD2a is True and probsD2a == []
      and okD2b is True and probsD2b == [], str((probsD2a, probsD2b)))

okD3, probsD3 = nc.validate_summary_citations(
    "### 美联储/利率\n- [{}] 普通合法新闻摘要。".format(Aid), {Aid, Bid})
check("D3 普通合法新闻(无围栏): 不回归,正常通过",
      okD3 is True and probsD3 == [], str(probsD3))

# ══ E. 历史回归(§七E,真实模块路径) ═════════════════════════════════
print("\n[E] 历史安全: FIX1~FIX4语义零回归")
pE1 = nprov.parse_news_item_references(
    "- [{A}] Fed holds rates [{B}]".format(A=Aid, B=Bid))
check("E1 FIX3正文夹带: A合法/B=body_extra_ids入illegal_ids(保持)",
      pE1['legal_ids'] == [Aid] and Bid in pE1['illegal_ids']
      and pE1['ok'] is False, str(pE1['anomalies'])[:80])

pE2 = nprov.parse_news_item_references(
    "```text\n- [{}] x\n```\n- [{}] y".format(Bid, Aid))
check("E2 FIX4普通反引号围栏: B排除A保留(保持)",
      pE2['legal_ids'] == [Aid] and pE2['fenced_lines'] == [1, 2, 3],
      str(pE2['legal_ids']))

pE3 = nprov.parse_news_item_references(
    "~~~json\n- [{}] x\n~~~\n- [{}] y".format(Bid, Aid))
check("E3 普通波浪号围栏: B排除A保留(保持)",
      pE3['legal_ids'] == [Aid] and pE3['ok'] is True,
      str(pE3['legal_ids']))

pE4 = nprov.parse_news_item_references(
    "- [{}] y\n```\n- [{}] x".format(Aid, Bid))
check("E4 未关闭围栏: 持续到文档结束(围栏后B排除,围栏前A保留)",
      pE4['legal_ids'] == [Aid] and len(pE4['fenced_lines']) == 2,
      str(pE4['legal_ids']))

tE5 = tempfile.mkdtemp(prefix='f5E5-', dir=_TMPD)
ndE5 = os.path.join(tE5, 'data', 'news')
os.makedirs(ndE5, exist_ok=True)
nprov.save_batch([rawA5, rawB5], ndE5, now_utc='2026-10-29T05:00:00Z')
write_summary(ndE5, '20261029',
              "### 美联储/利率\n- [{A}] Day1 normal\n```\n"
              "- [{B}] unclosed swallow".format(A=Aid, B=Bid))
write_summary(ndE5, '20261030',
              "### 美联储/利率\n- [{B}] Day2 real news\n".format(B=Bid))
outE5 = weekly(tE5)
check("E5 跨日期文件独立状态: Day1未关闭围栏只吞Day1其后内容,Day2真实"
      "B条目保留且经档案正常认证(legal==[A,B])",
      'unclosed swallow' not in outE5
      and nprov.parse_news_item_references(outE5)['legal_ids'] == [Aid, Bid]
      and 'https://r5/A' in outE5 and 'https://r5/B' in outE5,
      outE5.partition('#### 来源索引')[2][:80])

# E6: 七天窗口+跨天去重+超长裁剪(保新弃旧)
tE6 = tempfile.mkdtemp(prefix='f5E6-', dir=_TMPD)
ndE6 = os.path.join(tE6, 'data', 'news')
os.makedirs(ndE6, exist_ok=True)
write_summary(ndE6, '20261022',
              "### 美联储/利率\n- [{}] 窗口外旧闻\n".format(Aid))
write_summary(ndE6, '20261029',
              "### 美联储/利率\n- [{B}] 跨天重复新闻\n".format(B=Bid))
write_summary(ndE6, '20261030',
              "### 美联储/利率\n- [{B}] 跨天重复新闻\n"
              "- [{A}] 当日新条目\n".format(B=Bid, A=Aid))
outE6 = weekly(tE6)
check("E6 七天窗口+跨天去重: 窗口外(20261022<截止20261023)旧闻不加载;"
      "同一行跨两天只出现一次(保留首次);当日新条目保留",
      '窗口外旧闻' not in outE6
      and outE6.count('- [{}] 跨天重复新闻'.format(Bid)) == 1
      and '- [{}] 当日新条目'.format(Aid) in outE6, outE6[-100:])

tE6b = tempfile.mkdtemp(prefix='f5E6b-', dir=_TMPD)
ndE6b = os.path.join(tE6b, 'data', 'news')
os.makedirs(ndE6b, exist_ok=True)
longA = '- [{}] '.format(Aid) + '旧日超长' + '很' * 5200
longB = '- [{}] '.format(Bid) + '新日超长' + '很' * 5200
write_summary(ndE6b, '20261029', "### 美联储/利率\n" + longA + "\n")
write_summary(ndE6b, '20261030', "### 美联储/利率\n" + longB + "\n")
outE6b = weekly(tE6b)
check("E6b 超长裁剪(保新弃旧): 两日合计>9000→丢弃最旧一天,新日条目"
      "保留、旧日条目不出现(9000上限与丢弃顺序保持)",
      '新日超长' in outE6b and '旧日超长' not in outE6b, '')

tE7 = tempfile.mkdtemp(prefix='f5E7-', dir=_TMPD)
glmE7r, ndE7 = run_collector(
    tE7, market=[mkt_item(7201, 'Fed holds rates steady', 'https://r5/E7')])
sumE7 = summary_of(ndE7)
check("E7 GLM安全回退: 一次调用即异常→确定性标题回退(代码核发真实ID)",
      len(glmE7r.prompts) == 1 and '- [' in sumE7 and '## ' in sumE7,
      sumE7[:60])

tE8 = tempfile.mkdtemp(prefix='f5E8-', dir=_TMPD)
glmE8r, ndE8 = run_collector(tE8, market=RuntimeError('Finnhub down'),
                             company={'NVDA': RuntimeError('down')})
sumE8 = summary_of(ndE8)
check("E8 新闻源全部失败: 非关键降级(不建批次零news_sources档案,固定"
      "降级披露明示非模型生成)",
      not sources_of(ndE8) and '采集失败' in sumE8
      and '非模型生成' in sumE8, sumE8[:60])

tE9 = tempfile.mkdtemp(prefix='f5E9-', dir=_TMPD)
ndE9 = os.path.join(tE9, 'data', 'news')
os.makedirs(ndE9, exist_ok=True)
nprov.save_batch([rawA5], ndE9, now_utc='2026-10-30T05:00:00Z')
write_summary(ndE9, '20261030',
              '### 美联储/利率\n- [{}] Fed holds rates\n'.format(Aid))
with open(os.path.join(ndE9, sources_of(ndE9)[0]), 'a',
          encoding='utf-8') as f:
    f.write(' ')
outE9 = weekly(tE9)
check("E9 档案完整性验证继续生效: SHA-256损坏→'未通过来源认证'+完整性"
      "告警,不虚构URL",
      '未通过来源认证' in outE9 and '完整性告警' in outE9
      and 'https://r5/A' not in outE9, outE9[-100:])

# ══ F. 负向敏感性(§七F,退化必须被真实模块检出) ═════════════════════
print("\n[F] 负向敏感性: 恢复错误实现→反例A/B断言必失败")


def banned_tilde_open(line):
    """FIX4错误形态: 恢复'波浪info含波浪号→拒'禁令。"""
    r = real_open(line)
    if r and r[0] == '~':
        s = str(line or '')
        m = nprov.FENCE_OPEN_RE.match(s)
        if m and '~' in s[m.end():].strip():
            return None
    return r


with mock.patch.object(nprov, '_fence_open', banned_tilde_open):
    pF1 = nprov.parse_news_item_references(txtCA)
    outF1 = weekly(tC)
check("F1 恢复错误的if ch=='~' and '~' in info→反例A必败: 围栏不再开栏,"
      "B被当普通条目进入legal_ids;真实周报将B洗白认证(B URL入附录)"
      "——CA1/CA2断言对此必失败",
      Bid in pF1['legal_ids']
      and 'https://r5/B' in outF1, str(pF1['legal_ids']))


def space_only_close(line, ch, length):
    """FIX4错误形态: 恢复旧body=s.strip(' ')(漏尾随\\t)。"""
    s = str(line or '')
    n_lead = len(s) - len(s.lstrip(' '))
    if n_lead > 3:
        return False
    body = s.strip(' ')
    return (body != '' and set(body) == {ch} and len(body) >= length)


with mock.patch.object(nprov, '_fence_close', space_only_close):
    pF2 = nprov.parse_news_item_references(txtCB)
    outF2 = weekly(tCB)
check("F2 恢复旧strip(' ')→反例B必败: '```'+TAB不再关栏,围栏吞掉其后"
      "全部内容→A丢失(legal为空);真实周报无A条目无A URL——CB1/CB2"
      "断言对此必失败",
      pF2['legal_ids'] == []
      and f'- [{Aid}]' not in outF2.partition('#### 来源索引')[0]
      and 'https://r5/A' not in outF2, str(pF2['legal_ids']))


def whole_strip_close(line, ch, length):
    """禁止形态: 整行strip(' \\t')——错误移除行首制表符。"""
    s = str(line or '')
    body = s.strip(' \t')
    return bool(body) and set(body) == {ch} and len(body) >= length


tabFence = "```\nx\n\t```\ny"
with mock.patch.object(nprov, '_fence_close', whole_strip_close):
    fmapF3 = nprov.markdown_fence_map(tabFence)
    pF3 = nprov.parse_news_item_references(
        "```\n- [代码示例]x\n\t```\n- [{}]".format(Bid))
check("F3 错误使用整行strip(' \\t')→非法前导TAB测试必败: 前导TAB的"
      "'\\t```'被错误当作关栏(fence_map在TAB行提前关闭,其后行False;"
      "关栏后的B行逃出围栏被当普通条目入legal)——正确实现中该行不是"
      "关栏,围栏持续到EOF且B在栏内",
      fmapF3 == [True, True, True, False]
      and Bid in pF3['legal_ids']
      and nprov.markdown_fence_map(tabFence) == [True] * 4,
      str(fmapF3))

# ═══════════════════ 汇总 ══════════════════════════════════════════
print()
print("═" * 72)
print(f"W3-FIX5 结果: {PASS_N}通过 / {FAIL_N}失败")
print("═" * 72)
sys.exit(1 if FAIL_N else 0)
