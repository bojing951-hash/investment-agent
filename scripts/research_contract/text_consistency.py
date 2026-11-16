#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""text_consistency(契约§5 五小模块之五;T6c)

两副面孔,同一纪律——数值必可追溯到 claim:

  1) 渲染复核(render mode): 确定性模板产出的 body+manifest 对照——体内每个
     数值 token 须落在 manifest 登记位(禁按值反扫重建 manifest;对照=复核)。
  2) 迁移门检(migration mode): T7 对照面——给定文本+基准快照(+前情锚链),
     逐 token 绑定指标身份,按工厂 claim 形态构造瞬态 claim,交 claim_verifier
     独立复算;语义族检查器(排名序/可加性/持续性计数/复合条件计数/价差算术/
     先后值角色/方向词)对纯语义错误补位。裁决聚合: 任一硬不符=CONTRADICTED。
     辖域跳过≠披露豁免(律8/T6,RDG-20261115-008): 检查器辖域内未被消费的
     数值 token 禁静默吞——利差歧义族先落 spread_ambiguous 披露。

纯度: stdlib+research_contract 只读;零模型/零网络/零随机/零时钟。
"""
import json
import math
import re

from research_contract import claim_factory as cf
from research_contract import claim_verifier as cv
from research_contract import scorecard_spec

TEXT_CONSISTENCY_VERSION = 'tc-v3-judgment'

# ── 指标别名表(绑定优先级=模式特异性降序;别名冲突取最长匹配) ──────
ALIASES = {
    'UST_30Y': ['30Y UST', '30年期美债', '30Y', 'UST_30Y', 'UST 30Y'],
    'UST_10Y': ['10Y UST', '10年期美债', '10Y', '10年期', 'UST_10Y',
                'UST 10Y'],
    'UST_5Y': ['5Y UST', '5年期美债', 'UST_5Y', 'UST 5Y'],
    'UST_2Y': ['2Y UST', '2年期美债', '2Y', 'UST_2Y', 'UST 2Y'],
    'CURVE_2S10S': ['2s10s', '2s10s期限利差', '期限利差', 'CURVE_2S10S'],
    'HY_OAS': ['HY OAS', 'HY_OAS', '高收益债OAS', '高收益债利差'],
    'CCC_OAS': ['CCC OAS', 'CCC_OAS', 'CCC级OAS'],
    'IG_OAS': ['IG OAS', '投资级OAS'],
    'BB_OAS': ['BB OAS', 'BB级OAS'],
    'B_OAS': ['B级OAS'],
    'REAL_10Y': ['10Y实际利率', '10年期实际利率', '实际利率', 'REAL_10Y',
                 'REAL 10Y'],
    'TIPS_10Y': ['TIPS_10Y', '10年期TIPS'],
    'BEI_10Y': ['BEI', '通胀预期', 'BEI_10Y', 'BEI 10Y'],
    'DFF': ['有效联邦基金利率', '联邦基金有效利率', 'EFFR', 'DFF'],
    'ZQ_IMPLIED_AVG': ['期货隐含', '联邦基金期货隐含'],
    'SOFR': ['SOFR', '担保隔夜融资利率'],
    'DXY': ['美元指数', 'DXY'],
    'EURUSD': ['欧元兑美元', 'EURUSD', 'EUR/USD'],
    'USDJPY': ['美元兑日元', '美元/日元', 'USDJPY', 'USD/JPY'],
    'USDCNY': ['美元兑人民币', 'USDCNY'],
    'GOLD_F': ['黄金期货', 'COMEX黄金', '黄金', 'GOLD', '金价'],
    'SILVER_F': ['白银'],
    'WTI_F': ['WTI期货', 'WTI原油期货', 'WTI_F', 'WTI'],
    'BRENT_F': ['布伦特', 'BRENT'],
    'SPX': ['标普500', 'S&P 500', 'SPX', '标普'],
    'NDX': ['纳斯达克100', '纳指100', 'NDX', '纳指'],
    'RUT': ['罗素2000', '罗素', 'RUT'],
    'TLT': ['TLT', '长债ETF TLT'],
    'VIX': ['VIX', '波动率指数', '恐慌指数'],
    'NIKKEI225': ['日经225', '日经', 'NIKKEI'],
    'DAX': ['德国DAX', 'DAX'],
    'CAC40': ['法国CAC40', 'CAC40', 'CAC'],
    'HSI': ['恒生指数', '恒指'],
    'HSCEI': ['恒生中国企业指数', '国企指数'],
    'SHCOMP': ['上证指数', '上证'],
    'SZCI': ['深证成指'],
    'CHINEXT': ['创业板指'],
    'BTC': ['比特币', 'BTC'],
    'CN_TOTAL_TURNOVER': ['沪深两市成交额', '两市成交额', '两市成交'],
    'SZ_COMPONENT_AMOUNT': ['深证成指成分', '深市成交额'],
    'MARGIN_BAL': ['两融余额', '两融'],
    'SB_FLOW': ['南向净流入', '南向资金', '南向'],
    'SH_AMOUNT': ['沪市成交额', '沪市'],
    'UNEMPLOYMENT': ['失业率', 'unemployment rate'],
    'NFP': ['非农就业人数', '非农就业', 'nonfarm payrolls', 'NFP存量',
            '新增非农', '非农新增', '非农月新增', '新增就业'],
    'ICSA': ['initial claims', '初请失业金', '初请', 'initial jobless claims', 'jobless claims'],
    'RSAFS': ['零售销售', '零售', 'retail'],
    'INDPRO': ['工业生产'],
    'JTSJOL': ['职位空缺', 'JOLTS'],
    'UMCSENT': ['密歇根消费者信心', '密歇根信心', '密歇根'],
    'US_REAL_GDP': ['实际GDP', 'GDP'],
    'CPI': ['CPI物价指数', 'CPI'],
    'CORE_CPI': ['核心CPI'],
    'CORE_PCE': ['核心PCE'],
    'AHE': ['平均时薪', '时薪'],
    'CN_CPI_YOY': ['中国CPI', '国内CPI'],
    'CN_PPI_YOY': ['PPI'],
    'CN_PMI_MFG': ['制造业PMI', 'PMI'],
    'CN_SF_FLOW': ['社会融资规模增量', '社会融资增量', '社融增量', '社融'],
    'CN_NEW_LOANS': ['新增人民币贷款', '人民币贷款', '新增贷款'],
    'CN_LPR_1Y': ['LPR 1年期', 'LPR1Y'],
    'CN_LPR_5Y': ['LPR 5年期', 'LPR5Y'],
    'JP_POLICY_RATE': ['日本无担保隔夜拆借利率', '日本隔夜拆借利率',
                       '无担保隔夜拆借'],
    'JGB10Y': ['10年期日债', '日债10Y'],
    'JGB2Y': ['2年期日债'],
    'ECB_DFR': ['欧央行存款便利利率', '存款便利利率'],
    'SPX_EPS': ['SPX_EPS', '每股收益', 'SPX EPS'],
    'SPX_PE_TTM': ['PE_TTM', 'SPX_PE_TTM', '市盈率'],
    'SPX_CAPE': ['CAPE', '席勒CAPE'],
    'SH_PE': ['上证市盈率'],
    'WALCL': ['美联储总资产', '总资产'],
    'M2SL': ['M2货币供应', 'M2'],
}
# metric_id 自指补全: 别名表原为周报中文语料口径,research-run 事实表用
# id 形态(C-real 实证: WALCL 行零绑定);逐项补 id,重叠去重保最长
# (BB_OAS⊇B_OAS 子串场景由 _find_alias 占位去重处理)。
for _mid in list(ALIASES):
    if _mid not in ALIASES[_mid]:
        ALIASES[_mid].append(_mid)

# 统计配对面孔(相关语境)
PAIR_ALIASES = [
    (('DXY', 'GOLD_F'), ['美元-黄金', '美元–黄金', 'DXY-GOLD', 'DXY×GOLD']),
    (('SPX', 'GOLD_F'), ['SPX-黄金', '标普-黄金', 'SPX-GOLD']),
    (('SPX', 'EZU'), ['SPX-EZU', '标普-EZU']),
    (('SPX', 'TLT'), ['SPX-TLT', '股债']),
    (('BTC', 'NDX'), ['比特币-纳指', 'BTC-NDX']),
    (('NIKKEI225', 'USDJPY'), ['日经-美元/日元', '日经-USDJPY', '日经-日元']),
    (('DAX', 'EURUSD'), ['DAX-欧元']),
]

# 阈值语境词→注册表方向/名称线索(常量复述面)
THRESHOLD_KIND_WORDS = [
    ('恐慌线', ['panic', '恐慌']),
    ('警告线', ['warn', '警告']),
    ('警戒线', ['alert', '警戒']),
    ('红线', ['red', '红线']),
    ('强势阈值', ['strong', '强势']),
    ('正常线上限', ['normal', '正常']),
]

# 复合条件集(框架具名;确定性评估)
CONDITION_SETS = {
    'sell_america': {
        'names': ['Sell America', 'sell america', '卖出美国'],
        'conditions': [
            {'label': '股跌', 'metric': 'SPX', 'window': 'week',
             'kind': 'pct', 'op': '<', 'ref': 0.0},
            {'label': '债收益率升', 'metric': 'UST_10Y', 'window': 'week',
             'kind': 'pp', 'op': '>', 'ref': 0.0},
            {'label': '美元跌', 'metric': 'DXY', 'window': 'week',
             'kind': 'pct', 'op': '<', 'ref': 0.0},
        ],
    },
}

# 数值 token 正则: 符号/千分位/小数/百分号/pp/bp/千/K/亿/万亿/天/nan
_NUM_RE = re.compile(
    r'(?P<approx>约)?(?P<sign>[+−−-]?)(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.?\d*)'
    r'\s*(?P<unit>%|pp|个百分点|percentage points?|bp|千|K|亿元|亿港元|亿美元|亿|万亿|天|days?)?',
    re.IGNORECASE)
_DATE_RE = re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{4}[-/]\d{1,2}(?![-\d])'
                      r'|L\d{2,3}|\d+(?:\s*[–—-]\s*\d+)?\s*日'
                      r'|\d{4}-\d{2}-\d{2}')
_CJK_NUM = {'一': 1, '两': 2, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6,
            '七': 7, '八': 8, '九': 9, '十': 10}

_FACT_ZONE_RE = re.compile(r'【(事实|数据已证实)】')
_INF_ZONE_RE = re.compile(r'【(推断|方向性|假设)】')


# ── 基础工具 ────────────────────────────────────────────────────────

def _strip_num(s):
    return float(s.replace(',', ''))


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _nan(v):
    return isinstance(v, float) and v != v


def _tol_for(expected, approx):
    """容差: 整数面 0.5;常规 2dp 显示 0.005;约数=放宽 max(10×,2%|·|)。"""
    if not _is_num(expected):
        return 0.005
    base = 0.5 if float(expected).is_integer() else 0.005
    if approx:
        return max(base * 10, abs(expected) * 0.02)
    return base


def _display_decimals(raw):
    m = re.search(r'\d+\.(\d+)', raw or '')
    return len(m.group(1)) if m else 0


def _display_aligned(raw, val, computed, approx=False):
    """显示位对齐: 文本按所示小数位显示,与复算值的差不超过末位半格
    (2.51 vs 2.5053 ✓;2.48 vs 2.84 ✗;11245.39 vs 12245.39 ✗)。
    approx(约): 按所示有效数字半格(约1.22万亿 vs 12245.39 ✓)。"""
    import math
    if not (_is_num(val) and _is_num(computed)):
        return False
    if approx:
        digits = len(re.sub(r'[^\d]', '', raw).lstrip('0'))
        if digits == 0:
            return False
        mag = math.floor(math.log10(abs(float(computed)))) if \
            float(computed) else 0
        tol = 0.5 * (10 ** (mag - digits + 1)) + 1e-9
        return abs(float(val) - float(computed)) <= tol
    dec = _display_decimals(raw)
    tol = 0.5 * (10 ** -dec) + 1e-9
    return abs(float(val) - float(computed)) <= tol


def _value_matches(token_value, expected, approx=False):
    if expected is None:
        return token_value is None
    if token_value is None:
        return False
    if _nan(expected):
        return False              # nan 期望→载具体数=不符(伪造面)
    return abs(float(token_value) - float(expected)) <= \
        _tol_for(expected, approx) + 1e-9


def _clause_split(text):
    """分句: 顿号/分号/句号/换行/表格行=独立断言域。"""
    parts = re.split(r'[。；;\n]|(?<=[)）])\s*[，,]', text)
    return [p for p in (s.strip() for s in parts) if p]


# ── 检查面预处理(RDG-20261116-013: 非散文构造物不进断言域) ──────────

_CHECKFACE_COMMENT_RE = re.compile(r'<!--.*?-->', re.DOTALL)
# 报告头元数据行(生成头;RDG-013 A 族): 标题行 `# 投资周报 20261102–20261108`
# 与 `生成时间：…（数据截至…/08数据包，Gate A: PASS）`——日期/时间/包序号
# 非断言值(「/08」碎片曾绑指标)
_CHECKFACE_META_LINE_RE = re.compile(
    r'^[ \t]*(?:#{1,6}[ \t]*(?:投资)?周报\b[^\n]*|生成时间[:：][^\n]*)$',
    re.MULTILINE)


def _is_json_object_line(line):
    """独立行可解析 JSON 对象(provenance 附件判定;数组/坏行不触发)。"""
    s = line.strip()
    if not (s.startswith('{') and s.endswith('}')):
        return False
    try:
        obj = json.loads(s)
    except Exception:
        return False
    return isinstance(obj, dict)


def _checkface_preprocess(text):
    """检查面预处理(R43/RDG-20261116-013;R41 定性 A 族 47% 误报治面)。

    ① HTML 注释整体剥离(生成头 `<!-- 生成: … | 模型名 | … -->`/
       校验头 `<!-- 校验…FAIL(10项警告)…-->`: 16:22:44/5.3/10 等
       机写数字承前绑指标=误报;未闭合注释不匹配=保守保留);
    ② 报告头元数据行置换为空白(标题行 `# 投资周报 20261102–20261108`
       与 `生成时间：…`: 生成头行形态,日期窗/时间/包序号非断言);
    ③ 独立行可解析 JSON 对象置换为空白(报告内嵌 provenance 行
       `{"id":1,…,"confidence":1,…,"value":2.6,…}`: id/confidence/
       value 机写数值非散文断言)。
    换行结构保持(子句域不变形);不可解析行原样保留(诚实保守)。
    """
    text = _CHECKFACE_COMMENT_RE.sub(' ', text)
    text = _CHECKFACE_META_LINE_RE.sub(' ', text)
    return '\n'.join(
        ' ' if _is_json_object_line(ln) else ln
        for ln in text.split('\n'))


def _find_alias(clause, aliases=None):
    """子句内指标身份(最长别名匹配;返回 [(metric, start, end)] 按位置)。"""
    hits = []
    for mid, pats in (aliases or ALIASES).items():
        for pat in pats:
            for m in re.finditer(re.escape(pat), clause, re.IGNORECASE):
                hits.append((mid, m.start(), m.end()))
    # 去重叠: 同位置取最长
    hits.sort(key=lambda h: (h[1], -(h[2] - h[1])))
    out, occupied = [], []
    for mid, s, e in hits:
        if any(not (e <= s0 or s >= e0) for s0, e0 in occupied):
            continue
        out.append((mid, s, e))
        occupied.append((s, e))
    out.sort(key=lambda h: h[1])
    return out


# ── token 提取 ──────────────────────────────────────────────────────

def _extract_tokens(clause):
    """数值 token(排除日期/行号/窗口日数等结构性数字)。"""
    masked = clause
    for m in _DATE_RE.finditer(clause):
        masked = masked[:m.start()] + ' ' * (m.end() - m.start()) + masked[m.end():]
    tokens = []
    for m in _NUM_RE.finditer(masked):
        raw = m.group(0)
        if raw.strip() in ('', '约'):
            continue
        val = _strip_num(m.group('num'))
        if m.group('sign') in ('-', '−', '−'):
            val = -val
        unit = (m.group('unit') or '').lower()
        approx = bool(m.group('approx'))
        # 单位换算到断言层
        if unit == 'bp':
            value, ukind = val / 100.0, 'pp'
        elif unit in ('pp', '个百分点', 'percentage points', 'percentage point'):
            value, ukind = val, 'pp'
        elif unit == '%':
            value, ukind = val, 'percent'
        elif unit == '千':
            value, ukind = val, 'thousands'
        elif unit == 'k':
            value, ukind = val, 'K'
        elif unit == '万亿':
            value, ukind = val * 10000.0, '亿'
        elif unit.startswith('亿'):
            value, ukind = val, '亿'
        elif unit in ('天', 'days', 'day'):
            value, ukind = val, 'day'
        else:
            value, ukind = val, 'plain'
        tokens.append({'raw': raw, 'value': value, 'kind': ukind,
                       'approx': approx, 'start': m.start(), 'end': m.end(),
                       'ctx': clause[max(0, m.start() - 24):m.end() + 24]})
    # nan 字面
    for m in re.finditer(r'(?<![a-zA-Z])nan(?![a-zA-Z])', clause, re.IGNORECASE):
        tokens.append({'raw': m.group(0), 'value': None, 'kind': 'nan',
                       'approx': False, 'start': m.start(), 'end': m.end(),
                       'ctx': clause[max(0, m.start() - 24):m.end() + 24]})
    return tokens


# ── 断言域遮罩(别名内数字/结构数字非断言) ──────────────────────────

_STRUCT_PATTERNS = [
    # 10月/10月15日/9 月(空格容差);日组须带「日」——RDG-013: `日?` 可选
    # 时「11月3.8775%」吞「11月3」余碎片「8775%」(小数误切分 A 族)
    re.compile(r'\d{1,2}\s*月(?:\d{1,2}\s*日)?'),
    re.compile(r'第\s*\d+\s*周'),                    # 连续第5周
    re.compile(r'\d{1,2}日(?=相关|-?day)'),           # 20日/60日相关
    re.compile(r'\d{1,2}-?day'),
    re.compile(r'(?:19|20)\d{2}\s*年'),              # 年份(2026 年/2026年)
    # 信封编号(L1/S3/S4 信封):层引用非断言值
    re.compile(r'[LS]\d(?:\s*[/／]\s*[LS]\d)+'),
    # 时长换算复述(约166天(约5个半月)):N个半月/N个月=滞后者换算面,
    # 非独立断言(换算核验走 lag_duration)
    re.compile(r'约?\d+(?:\.\d+)?\s*个半?月'),
    # 年-月形态(2026-12/2027-01 期货隐含):月份引用非断言值
    re.compile(r'(?<!\d)(?:19|20)\d{2}[-/](?:0?[1-9]|1[0-2])'
               r'(?![\d-])'),
    # 等式括注(0.23+0.01=0.24 ✓ / 概率和=100%):算式自证域,非独立断言
    re.compile(r'[（(][^()（）]*=[^()（）]*[)）]'),
    # 数值区间端点(85-100/100-104/4.5-4.8):双侧 1-3 位数字+可选小数;
    # (?<![\d.]) 挡 ISO 日期片段(2026-11),(?![\d-]) 挡区间右缘续数字
    re.compile(r'(?<![\d.])(?:\d{1,3}(?:\.\d+)?)\s?[–—-]\s?'
               r'(?:\d{1,3}(?:\.\d+)?)(?![\d-])'),
    # 观测计数(225 个观测):样本量=统计结论域(judgment_contract 复算),
    # 非指标水平断言
    re.compile(r'\d+\s*个(?:观测|样本|数据点)'),
    # 百分位断言(第 95.6 百分位):统计结论域(judgment_contract 复算)
    re.compile(r'第\s*\d+(?:\.\d+)?\s*百分位'),
    # 前值复述-趋平形(自 0.32 单日趋平):judgment_contract 对照序列
    # 前观测复算;此处遮罩防误绑当期水平
    re.compile(r'自\s*\d+(?:\.\d+)?\s*(?:pp|点|%)?[\s个单日]*'
               r'(?:趋平|走平)'),
    # 编号引用(CON-1/VP-VIEW-20261110-002/QB-xxx 及裸层号 S6/E1/L2):
    # 档案编号非断言值
    re.compile(r'[A-Z]{2,8}(?:-[A-Za-z0-9]+)+'),
    re.compile(r'(?:^|[^A-Za-z0-9])[ELS]\d(?![\w.-])'),
    # 引用ID([art_9456078c93b846df] 形态;RDG-013 A 族): 证据引用附件
    # 非断言值(裸 9456078 曾承前绑 DXY)
    re.compile(r'art_[0-9A-Za-z]{6,}'),
    # 内部引用序号(论点#3/预测#2;RDG-013 A 族): 观点档案引用非断言值
    re.compile(r'(?:论点|预测|假设|条件|观点)\s*#\s*\d+'),
    # 紧凑 ISO 日期窗(20261102–20261108;RDG-013 A 族生成头残形):
    # 8 位日期对非断言值(松散日期已由 _DATE_RE 面;en-dash 窗不受其辖)
    re.compile(r'(?<!\d)\d{8}\s*[–—-]\s*\d{8}(?!\d)'),
    # 子句首列表序号(1./2./3.;RDG-013 A 族): 枚举结构非断言值;
    # 点后须空白(3.5%/3.8775% 类小数不吞=反误杀边界)
    re.compile(r'^\d{1,2}\.\s+'),
]


def _mask_spans(clause, spans):
    out = list(clause)
    for s0, e0 in spans:
        for i in range(s0, min(e0, len(out))):
            out[i] = ' '
    return ''.join(out)


def _masked_clause(clause, mids_in):
    masked = clause
    for m in _DATE_RE.finditer(masked):   # 日期最先(区间模式勿吞日期尾)
        masked = _mask_spans(masked, [(m.start(), m.end())])
    for pat in _STRUCT_PATTERNS:          # 结构数字次之(10月/第5周/100-104)
        for m in pat.finditer(masked):
            masked = _mask_spans(masked, [(m.start(), m.end())])
    spans = []
    for mid, s0, e0 in mids_in:           # 别名跨遮蔽区重定位
        m2 = re.search(re.escape(clause[s0:e0]), masked)
        if m2:
            spans.append((m2.start(), m2.end()))
    return _mask_spans(masked, spans)


def _scale_k(value, kind, fact):
    """K/千 按指标单位族换算(persons→×1000; *_thousands→原值)。"""
    if kind not in ('K', 'thousands'):
        return value
    u = (fact.get('unit') or '')
    if u.endswith('thousands'):
        return value
    return value * 1000.0


_LEVEL_MARK_RE = re.compile(
    r'(至|到|at|收于|报|printed at|为|是|持平|=)\s*$')


# ── 瞬态 claim 构造(工厂形态;证据=snapshot 事实/序列) ─────────────

def _anchor_facts(anc):
    """anchors 双形态归一: {'facts':[...]} 或 {key:{metric_id,value,...}}。"""
    if isinstance(anc, dict) and isinstance(anc.get('facts'), list):
        return anc['facts']
    out = []
    if isinstance(anc, dict):
        for v in anc.values():
            if isinstance(v, dict) and v.get('metric_id') is not None:
                out.append(v)
    return out


_CTX_STATE = {'carry_mid': None}   # check_text 逐句更新(单线程跑台)


def _fact_of(snapshot, mid):
    for f in snapshot.get('facts', []):
        if f['metric_id'] == mid:
            return f
    return None


_WINDOW_PATTERNS = [
    ('m1', re.compile(r'环比|mom', re.I)),
    ('m1', re.compile(
        r'in\s+(?:January|February|March|April|May|June|July|'
        r'August|September|October|November|December)', re.I)),
    ('m12', re.compile(r'同比|yoy', re.I)),
    ('week', re.compile(r'w/w|wow', re.I)),
    ('week', re.compile(r'周|week|weekly', re.I)),
    ('ytd', re.compile(r'年内|年初以来|ytd|year.to.date', re.I)),
]


def _window_of(clause, token):
    """窗口词→derived 键(环比=m1/同比=m12/周=week;默认 None=水平)。

    仅扫 token 之前缀(clause[:start])取**最近**窗口词——枚举句
    「同比+4.08%、环比+0.35%、同比+2.87%」中每个值取紧邻其前的
    窗口词,后随窗口词不得反向殖民前值(EA-5)。
    """
    prefix = clause[:token['start']]
    best_key, best_pos = None, -1
    for key, pat in _WINDOW_PATTERNS:
        for m in pat.finditer(prefix):
            if m.start() >= best_pos:
                best_key, best_pos = key, m.start()
    if best_key == 'week':
        # 上周/前一周/上一周=prior 标记,_PRIOR_ROLE 管,不作窗口
        tail = prefix[max(0, best_pos - 3):best_pos + 4]
        if re.search(r'上周|前一周|上一周|prior week', tail, re.I):
            return None
    return best_key


_PRIOR_MARK_RE = re.compile(
    r'上期|前期|前值|上月|prior|previous|上一交易日|上周|前一周|from',
    re.I)


def _prior_role(clause, token, observation_date=None):
    """上期/前值角色标记(位置式: 标记须在 token 之前方算前值;
    「from X」的 X 在标记后=前值;「in the week of <早于观测日的日期>」
    =上期引用;标记与 token 之间出现 本期/当前 =角色反转,不算前值)。"""
    for m in _PRIOR_MARK_RE.finditer(clause):
        if m.end() <= token['start'] + 1 and \
                token['start'] - m.end() <= 28:
            if re.search(r'本期|当前|current|this week',
                         clause[m.end():token['start']], re.I):
                continue        # 「上期的X回升至本期Y」: Y=本期值归主循环
            return 'prior'
    if observation_date:
        # 日期限定语后随形态: 「printed at 189K in the week of <旧日期>」
        # ——日期在 token 之后 20 字内=该值的上期身份;其后的变化 token
        # (rising 6K)不受此日期株连;「本期X（旧日期口径）」的 本期 标记
        # 优先于旧日期注 → 不算前值(V5-018 换向家族)
        if re.search(r'本期|当前|current', clause[:token['start']], re.I):
            return None
        for dm in _DATE_RE.finditer(clause):
            d = str(dm.group(0))[:10]
            if len(d) == 10 and d < str(observation_date)[:10] and \
                    0 <= dm.start() - token['end'] <= 20:
                return 'prior'
    return None


def _direction_of(clause):
    neg = re.search(r'回落|下跌|下行|走低|下降|降至|降到|净减少|跌|挫|'
                    r'收窄|微收|再收|fell|'
                    r'falling|decline|dropped|edged down|down \d', clause, re.I)
    pos = re.search(r'回升|上涨|上行|走高|上升|升至|净增加|涨|走阔|拓宽|'
                    r'rose|rising|'
                    r'increase|climbed|up \d', clause, re.I)
    if neg and pos:
        return 0
    return (-1 if neg else 0) or (1 if pos else 0)


def _change_field(fact, window):
    """窗口 derived 记录(相对/绝对随单位族)。"""
    rec = (fact.get('derived') or {}).get(window) or {}
    return rec


def _build_level_claim(token, mid, fact, snapshot):
    c = cf._claim(
        'level', 'point', mid, token['value'], fact['unit'],
        fact['observation_date'], snapshot['research_as_of'],
        [cf._fact_ref(fact)], [fact['fact_id']], '迁移门瞬态(文本水平)')
    return c


def _build_change_claim(token, mid, fact, snapshot, window, kind):
    rec = _change_field(fact, window)
    if not rec or 'basis_date' not in rec:
        return None
    fam = (cf.fe.metric(mid) or {}).get('unit_family')
    is_rate = fact['unit'] in ('percent', cf.CANONICAL_PP)
    if kind == 'percent':
        if 'pct_change' not in rec:
            return None
        subtype, unit = 'relative', 'percent'
    elif kind == 'pp':
        if 'pp_change' not in rec:
            return None
        subtype, unit = 'absolute', cf.CANONICAL_PP
    else:
        if 'abs_change' not in rec:
            return None
        subtype, unit = 'absolute', fact['unit']
    return cf._claim(
        'change', subtype, mid, token['value'], unit,
        fact['observation_date'], snapshot['research_as_of'],
        [cf._fact_ref(fact),
         cf._basis_ref(mid, rec['basis_date'], rec.get('basis_value'),
                       fact['unit'])],
        [fact['fact_id'], f"{mid}@{rec['basis_date']}"],
        f'迁移门瞬态(文本变化 {window}/{kind})', window=window,
        basis_date=rec['basis_date'], basis_value=rec.get('basis_value'))


def _verify_claims(claims, snapshot, thresholds=None):
    """瞬态 claims → verify_bundle 裁决。"""
    if not claims:
        return {}
    bundle = {'snapshot_id': 'migration', 'target_date': '20260101',
              'research_as_of': snapshot['research_as_of'],
              'claims': claims, 'coverage_ledger': [], 'counts': {}}
    res = cv.verify_bundle(bundle, snapshot=snapshot, thresholds=thresholds)
    return {v['claim_id']: v for v in res['verdicts']}


# ── 语义族检查器 ────────────────────────────────────────────────────

def _mcl_is_distance(mcl, t, snapshot, thresholds_by, gpos=None,
                     alias_mids=None):
    """token 在遮蔽域中为「|level−阈值|」距离值(距…警告线X 形态)则真。

    alias_mids: 未遮蔽句的别名命中(遮蔽域内别名已抹除,须由调用方传入)。
    """
    mt = None
    for tt in _extract_tokens(mcl):
        if gpos is not None:
            if abs(tt['start'] - gpos) <= 1:
                mt = tt
                break
        elif abs(tt['start'] - t['start']) <= 1:
            mt = tt
            break
    if mt is None:
        return False
    mids = alias_mids or _find_alias(mcl)
    mid = mids[0][0] if mids else _CTX_STATE.get('carry_mid')
    if not mid:
        return False
    fact = _fact_of(snapshot, mid)
    if not fact or not _is_num(fact['value']):
        return False
    reg_vals = [e['value'] for es in thresholds_by.values() for e in es
                if e['unit'] in ('percent', cf.CANONICAL_PP)]
    if not reg_vals:
        return False
    return any(abs(abs(fact['value'] - rv) - mt['value'])
               <= 0.005 + 1e-9 for rv in reg_vals)

def _check_threshold_constant(clause, snapshot, thresholds_by):
    """阈值常量复述(警告线400bp=4.00% 等)对照注册表。"""
    checks = []
    alias_mids = _find_alias(clause)
    mcl = _masked_clause(clause, alias_mids)
    for word, _kw in THRESHOLD_KIND_WORDS:
        for m in re.finditer(re.escape(word), clause):
            seg = clause[m.end():m.end() + 40]
            for t in _extract_tokens(seg):
                if t['kind'] in ('percent', 'pp'):
                    # 距标记后缀/上下方偏移跳过(…仅0.80pp/红线上方25bp)
                    before = seg[:t['start']]
                    if re.search(r'(距|距离|缓冲|仅|余)[^0-9]{0,4}$', before) \
                            or re.search(r'(?:上方|下方|above|below|points)'
                                         r'[^0-9+\-−]{0,4}$', before):
                        continue      # 距离值非常量复述
                    tv = t['value']
                    hit = any(
                        abs(e['value'] - tv) <= 0.005 + 1e-9
                        for mid, es in thresholds_by.items() for e in es
                        if e['unit'] in ('percent', cf.CANONICAL_PP))
                    if not hit and _mcl_is_distance(
                            mcl, t, snapshot, thresholds_by,
                            gpos=m.end() + t['start'], alias_mids=alias_mids):
                        continue      # 距离值复述(距400bp警告线0.80形态)
                    checks.append({
                        'family': 'threshold_constant', 'token': t['raw'],
                        'value': tv, 'expected_group': 'thresholds-registry',
                        'status': 'VERIFIED' if hit else 'CONTRADICTED',
                        'note': f'{word}{t["raw"]} vs 注册表常量'})
    return checks


_DIST_TRIGGER_RE = re.compile(
    r'距离?|缓冲|'
    r'(?:红线|警戒线|警告线|恐慌线|阈值|门槛|关口|强弱势?边界|边界)'
    r'(?:之?上|之?下)\s*方?|'
    r'points?\s+(?:above|below)|(?:above|below)\s+the', re.I)


def _check_distance(clause, snapshot, thresholds_by):
    """距离族: |level−threshold|≈distance token(pp/bp/index)。

    配对式(中英双向): 常量 token(=注册表阈值)与距离 token 无论先后
    (「距警告线400bp…0.80pp」/「0.59 points below the 104」),
    任一 (常量,距离) 对满足 |fact−常量|≈距离 → VERIFIED 并消费两者
    (含紧随的单位复述 25bp(0.25pp))。
    """
    checks = []
    if not _DIST_TRIGGER_RE.search(clause):
        return checks
    mids = _find_alias(clause)
    mid = mids[0][0] if mids else _CTX_STATE.get('carry_mid')
    if not mid:
        return checks
    fact = _fact_of(snapshot, mid)
    if not fact or not _is_num(fact['value']):
        return checks
    reg_vals = [e['value'] for es in thresholds_by.values() for e in es]
    mcl = _masked_clause(clause, mids)
    toks = [t for t in _extract_tokens(mcl)
            if t['kind'] in ('percent', 'pp', 'plain')]
    used = set()
    for i, ct in enumerate(toks):
        if ct['start'] in used:
            continue
        if not any(abs(ct['value'] - rv) <= 0.005 + 1e-9 for rv in reg_vals):
            continue
        exp = abs(fact['value'] - ct['value'])
        if exp <= 0.01:
            continue
        for dt in toks:
            if dt['start'] in used or dt is ct:
                continue
            if abs(dt['value'] - fact['value']) <= 0.01 or \
                    any(abs(dt['value'] - rv) <= 0.005 + 1e-9
                        for rv in reg_vals):
                continue
            ok = _value_matches(dt['value'], round(exp, 4), dt['approx']) \
                or _display_aligned(dt['raw'], dt['value'], exp)
            if not ok:
                continue          # 非该常量的距离 → 试下一对
            used.update({ct['start'], dt['start']})
            note = f'|{fact["value"]}−{ct["value"]}|={exp:.4g}'
            toks_join = [ct['raw'], dt['raw']]
            # 单位复述(25bp(0.25pp)): 同值紧随 token 一并消费
            for rt in toks:
                if rt['start'] in used:
                    continue
                if abs(rt['value'] - dt['value']) <= 1e-9 and \
                        0 < rt['start'] - dt['end'] <= 6:
                    used.add(rt['start'])
                    toks_join.append(rt['raw'])
                    break
            checks.append({'family': 'threshold_distance',
                           'token': '、'.join(toks_join),
                           'value': dt['value'], 'expected': round(exp, 4),
                           'status': 'VERIFIED',
                           'note': note})
            break
    # 声明距离但句内无常量 token(距警告线80bp): 与注册表最近阈值复算
    # 须句内具名线/阈值词,防止「距前期高点X」类非注册表锚距离被误杀
    if not checks and re.search(r'线|阈值|threshold', clause, re.I):
        m = re.search(r'(?:距离?|缓冲)[^0-9+\-−约]{0,6}(约)?\s*'
                      r'([+\-−]?\d[\d,]*\.?\d*)\s*(pp|bp|个百分点|点|'
                      r'index points?)?', clause)
        if m:
            dtv = _strip_num(m.group(2))
            if (m.group(3) or '') in ('bp',):
                dtv = dtv / 100.0
            if abs(dtv - fact['value']) > 0.01:
                best = None
                for rv in reg_vals:
                    miss = abs(abs(fact['value'] - rv) - dtv)
                    if best is None or miss < best[0]:
                        best = (miss, rv)
                if best is not None:
                    ok = best[0] <= 0.005 + 1e-9
                    checks.append({
                        'family': 'threshold_distance',
                        'token': m.group(0).strip(), 'value': dtv,
                        'expected': round(abs(fact['value'] - best[1]), 4),
                        'status': 'VERIFIED' if ok else 'CONTRADICTED',
                        'note': f'最近阈值{best[1]:g}距离'
                                f'={abs(fact["value"] - best[1]):.4g}'
                                f' vs 文本{dtv:g}'})
    return checks


def _check_corr(clause, snapshot, thresholds_by=None):
    """相关系数: 配对面孔+窗口日数+token(+nan)。"""
    checks = []
    for pair_keys, pats in PAIR_ALIASES:
        pm = None
        for pat in pats:
            pm = re.search(re.escape(pat), clause)
            if pm:
                break
        if not pm:
            continue
        store = snapshot.get('series_store', {})
        sa, sb = store.get(pair_keys[0]), store.get(pair_keys[1])
        wms = list(re.finditer(r'(\d{1,2})日相关|(\d{1,2})-?day', clause))
        if not wms and re.search(r'相关性|相关(?!非因果)', clause):
            # 无窗口词的相关性断言: 以 nan 字面或单值对照全部默认窗
            toks = [t for t in _extract_tokens(clause)
                    if t['kind'] in ('plain', 'nan')]
            for t in toks[:1]:
                for w in cf.STATISTIC_WINDOWS:
                    claim = cf._claim(
                        'statistic', 'correlation', None,
                        (t['value'] if t['kind'] != 'nan' else None),
                        'dimensionless', '2026-01-01',
                        snapshot['research_as_of'],
                        ([cf._series_shape_ref(pair_keys[0], sa, role='leg_a'),
                          cf._series_shape_ref(pair_keys[1], sb, role='leg_b')]
                         if (sa and sb) else []),
                        [f'series:{pair_keys[0]}', f'series:{pair_keys[1]}'],
                        '迁移门瞬态(文本相关)',
                        metric_ids=list(pair_keys), corr_window_days=w)
                    verd = _verify_claims([claim], snapshot)
                    v = verd.get(claim['claim_id'])
                    checks.append({
                        'family': 'statistic', 'token': t['raw'],
                        'value': claim['value'],
                        'expected': (v or {}).get('computed'),
                        'status': (v or {}).get('status', 'NOT_VERIFIABLE'),
                        'note': ';'.join((v or {}).get('reasons', [])[:2])})
            continue
        for wm in wms:
            w = int(wm.group(1) or wm.group(2))
            seg = clause[wm.end():wm.end() + 24]
            toks = [t for t in _extract_tokens(seg)
                    if t['kind'] in ('plain', 'nan', 'percent')]
            t = toks[0] if toks else None
            claim = cf._claim(
                'statistic', 'correlation', None,
                (t['value'] if t and t['kind'] != 'nan' else None),
                'dimensionless', '2026-01-01', snapshot['research_as_of'],
                ([cf._series_shape_ref(pair_keys[0], sa, role='leg_a'),
                  cf._series_shape_ref(pair_keys[1], sb, role='leg_b')]
                 if (sa and sb) else []),
                [f'series:{pair_keys[0]}', f'series:{pair_keys[1]}'],
                '迁移门瞬态(文本相关)',
                metric_ids=list(pair_keys), corr_window_days=w)
            if not (sa and sb):
                checks.append({'family': 'statistic', 'token':
                               (t or {'raw': '?'})['raw'], 'value': None,
                               'expected': None,
                               'status': 'INSUFFICIENT_EVIDENCE',
                               'note': '序列缺席(通道未闭合)'})
                continue
            verd = _verify_claims([claim], snapshot)
            v = verd.get(claim['claim_id'])
            checks.append({'family': 'statistic', 'token':
                           (t or {'raw': '?'})['raw'],
                           'value': claim['value'],
                           'expected': (v or {}).get('computed'),
                           'status': (v or {}).get('status', 'NOT_VERIFIABLE'),
                           'note': ';'.join((v or {}).get('reasons', [])[:2])})
    return checks


def _check_rank(clause, snapshot, thresholds_by=None):
    """排名序: 领涨/次之/垫底/最大涨幅+多(别名,%)对。"""
    if not re.search(r'领涨|次之|垫底|最大涨幅|最小涨幅|涨幅居前|涨幅最小', clause):
        return []
    pairs = []
    for mid, s0, e0 in _find_alias(clause):
        seg = clause[e0:e0 + 44]
        for t in _extract_tokens(seg):
            if t['kind'] == 'percent':
                pairs.append((mid, t['value'], t['raw'], e0))
                break
    if len(pairs) < 2:
        return []
    order_by_val = sorted(pairs, key=lambda p: -p[1])
    rank_of = {p[0]: i + 1 for i, p in enumerate(order_by_val)}
    ok, detail = True, []
    for mid, v, raw, e0 in pairs:
        seg = clause[max(0, e0 - 70):e0 + 60]
        if re.search(r'领涨|最大涨幅', seg):
            if rank_of[mid] != 1:
                ok = False
                detail.append(f'{mid} 称领涨但周涨幅排第{rank_of[mid]}')
        elif re.search(r'垫底|最小涨幅', seg):
            if rank_of[mid] != len(pairs):
                ok = False
                detail.append(f'{mid} 称垫底但排第{rank_of[mid]}/共{len(pairs)}')
    return [{'family': 'ranking', 'token': '/'.join(p[2] for p in pairs),
             'value': None, 'expected': f'降序 {[p[0] for p in order_by_val]}',
             'status': 'VERIFIED' if ok else 'CONTRADICTED',
             'note': '; '.join(detail) or '排名语义一致'}]


def _check_spread(clause, snapshot, thresholds_by=None):
    """价差算术: A vs B——利差/差 X(约数含)。"""
    if not re.search(r'利差|vs\.?|—|对比', clause):
        return []
    mids = _find_alias(clause)
    # 相异指标守卫(RDG-20261115-009): 别名+metric_id 自指可同指一指标
    # (高收益债利差 HY_OAS),自对算术 |v−v|=0 对任何非零利差复述必假红
    seen_m, distinct = set(), []
    for m in mids:
        if m[0] not in seen_m:
            seen_m.add(m[0])
            distinct.append(m)
    if len(distinct) < 2:
        return []
    a, b = distinct[0][0], distinct[1][0]
    fa, fb = _fact_of(snapshot, a), _fact_of(snapshot, b)
    if not (fa and fb) or not (_is_num(fa['value']) and _is_num(fb['value'])):
        return []
    m = re.search(r'(利差|差)[^0-9+\-−约]{0,10}(约)?\s*([+\-−]?\d[\d,]*\.?\d*)'
                  r'\s*(pp|个百分点|%)?', clause)
    if not m:
        return []
    tv = _strip_num(m.group(3))
    if (m.group(4) or '') == '%':
        tv = tv          # percent 直读(利差语境同 pp 数值面)
    exp = round(abs(fa['value'] - fb['value']), 4)
    approx = bool(m.group(2)) or bool(re.search(r'约', m.group(0)))
    ok = _value_matches(tv, exp, approx)
    return [{'family': 'spread_arithmetic', 'token': m.group(0).strip(),
             'value': tv, 'expected': exp,
             'status': 'VERIFIED' if ok else 'CONTRADICTED',
             'note': f'|{fa["value"]}−{fb["value"]}|={exp:g}'}]


def _check_additivity(clause, snapshot, thresholds_by=None):
    """可加性: 总变化=贡献A+贡献B / 流量总=部分A+部分B / 名义=实际+BEI 恒等式。"""
    checks = []
    # 等式括注/日期遮蔽后再取 token(0.23+0.01=0.24 复述不算独立贡献)
    mcl = _masked_clause(clause, _find_alias(clause))
    # 形态一: 总token(分解/构成标记之前) 与各「贡献」标记之后的 pp 贡献
    if re.search(r'分解|加总|构成|贡献', clause):
        contribs = []
        for m in re.finditer(r'贡献', mcl):
            for t in _extract_tokens(mcl[m.end():m.end() + 24]):
                if t['kind'] == 'pp':
                    contribs.append(t)
                    break
        if len(contribs) >= 2:
            total_tok = None
            m0 = re.search(r'分解|构成|加总', mcl)
            if m0:
                for t in reversed(_extract_tokens(
                        mcl[max(0, m0.start() - 60):m0.start()])):
                    if t['kind'] == 'pp':
                        total_tok = t
                        break
            if total_tok is None:
                toks = [t for t in _extract_tokens(mcl)
                        if t['kind'] == 'pp']
                if toks:
                    total_tok = toks[0]
            if total_tok is not None:
                s = round(sum(t['value'] for t in contribs), 4)
                ok = _value_matches(round(total_tok['value'], 4), s)
                join = ([t['raw'] for t in contribs] if ok else
                        [total_tok['raw']] + [t['raw'] for t in contribs])
                checks.append({
                    'family': 'additivity',
                    'token': '、'.join(join),
                    'value': total_tok['value'], 'expected': s,
                    'status': 'VERIFIED' if ok else 'CONTRADICTED',
                    'note': f'贡献和={s:g} vs 总{total_tok["raw"]}'
                            f'{"(总归主循环节点复核)" if ok else ""}'})
    # 形态三: 流量可加(总额=A亿+B亿, 成交额/合计 语境; 排除注册表常量)
    if re.search(r'成交额|合计|总量', clause):
        toks = [t for t in _extract_tokens(mcl) if t['kind'] == '亿']
        reg_cny = [e['value'] for es in (thresholds_by or {}).values()
                   for e in es if e.get('unit') == 'cny_100m']
        parts = [t for t in toks
                 if not any(abs(t['value'] - rv) <= 0.005 + 1e-9
                            for rv in reg_cny)]
        if len(parts) >= 3:
            mtot = re.search(r'成交额|合计|总量', mcl)
            after = [t for t in parts
                     if 0 <= t['start'] - mtot.end() <= 30]
            total_tok = after[0] if after else max(
                parts, key=lambda t: t['value'])
            rest = [t for t in parts if t is not total_tok]
            s = round(sum(t['value'] for t in rest), 4)
            ok = _value_matches(round(total_tok['value'], 4), s)
            join = ([t['raw'] for t in rest] if ok else
                    [total_tok['raw']] + [t['raw'] for t in rest])
            checks.append({
                'family': 'additivity_flow',
                'token': '、'.join(join),
                'value': total_tok['value'], 'expected': s,
                'status': 'VERIFIED' if ok else 'CONTRADICTED',
                'note': f'部分和={s:g} vs 总{total_tok["raw"]}'
                        f'{"(总归主循环节点复核)" if ok else ""}'})
    # 形态二: A与B加总构成 C(水平恒等式;亦含减恒等 实际=名义−通胀预期)
    m = re.search(r'加总构成|恒等', clause)
    if m:
        mids = _find_alias(clause)
        if len(mids) >= 3:
            vals = []
            for mid, s, e in mids[:3]:
                f = _fact_of(snapshot, mid)
                vals.append((mid, f['value'] if f else None))
            nums = [t for t in _extract_tokens(mcl)
                    if t['kind'] in ('percent', 'pp')]
            if len(vals) == 3 and len(nums) >= 3 and \
                    all(_is_num(v) for _, v in vals):
                a, b, c = [v for _, v in vals]
                ok_sum = abs((a + b) - c) <= 0.005 + 1e-9
                ok_diff = abs((a - b) - c) <= 0.005 + 1e-9
                ok = (ok_sum or ok_diff) and \
                    _value_matches(nums[0]['value'], a) and \
                    _value_matches(nums[1]['value'], b) and \
                    _value_matches(nums[2]['value'], c)
                op = '+' if ok_sum else ('−' if ok_diff else '±')
                checks.append({'family': 'additivity_identity',
                               'token': '/'.join(n['raw'] for n in nums[:3]),
                               'value': [n['value'] for n in nums[:3]],
                               'expected': [a, b, c],
                               'status': 'VERIFIED' if ok else 'CONTRADICTED',
                               'note': f'{a}{op}{b}={c}'})
    return checks


def _check_consecutive(clause, snapshot, thresholds_by=None):
    """持续性: 连续第N周收于阈值上/下方(周格收敛计数)。"""
    m = re.search(r'连续第\s*(\d+)\s*周', clause)
    if not m:
        return []
    claimed = int(m.group(1))
    mids = _find_alias(clause)
    mid = mids[0][0] if mids else _CTX_STATE.get('carry_mid')
    if not mid:
        return []
    store = snapshot.get('series_store', {})
    s = store.get(mid)
    fact = _fact_of(snapshot, mid)
    if not fact:
        return []
    if not s and _CTX_STATE.get('prior_obs') and \
            _CTX_STATE['prior_obs'].get(mid):
        # 序列缺席→前情锚链周值回退(锚日观测=该周代表值)
        import datetime as _dt
        wk = {}
        for d, v in sorted(_CTX_STATE['prior_obs'][mid]):
            try:
                wk[_dt.date.fromisoformat(str(d)[:10]).isocalendar()[:2]] = v
            except ValueError:
                continue
        wk[_dt.date.fromisoformat(str(fact['observation_date'])[:10])
          .isocalendar()[:2]] = fact['value']
        seq = sorted(wk.items(), key=lambda kv: kv[0])
    elif not s:
        return [{'family': 'consecutive_periods', 'token': m.group(0),
                 'value': claimed, 'expected': None,
                 'status': 'INSUFFICIENT_EVIDENCE', 'note': '序列缺席'}]
    else:
        import datetime as _dt
        weeks = {}
        for d, v in zip(s['dates'], s['values']):
            if v is None or _nan(v):
                continue
            try:
                dt = _dt.date.fromisoformat(str(d)[:10])
            except ValueError:
                continue
            weeks[dt.isocalendar()[:2]] = v
        seq = sorted(weeks.items(), key=lambda kv: kv[0])
    # 阈值: 句内常量(红线5%/5.0/104)或注册表首要
    tv = None
    for t in _extract_tokens(clause):
        if t['kind'] in ('percent', 'pp', 'plain') and \
                abs(t['value'] - fact['value']) > 0.01:
            tv = t['value']
            break
    if tv is None:
        return []
    if not seq:
        return []
    side_now = 1 if seq[-1][1] > tv else (-1 if seq[-1][1] < tv else 0)
    n = 0
    for _, v in reversed(seq):
        s_side = 1 if v > tv else (-1 if v < tv else 0)
        if s_side == side_now and side_now != 0:
            n += 1
        else:
            break
    ok = n >= claimed
    return [{'family': 'consecutive_periods', 'token': m.group(0),
             'value': claimed, 'expected': n,
             'status': 'VERIFIED' if ok else 'CONTRADICTED',
             'note': f'周格连续同侧={n}周(阈值{tv}) vs 文本第{claimed}周'}]


def _check_compound_count(clause, snapshot, thresholds_by=None):
    """复合条件计数: 已满足N条/两条+具名条件集。"""
    m = re.search(r'已满足\s*([一两二三四五六七八九十\d])\s*条', clause)
    if not m:
        return []
    tok = m.group(1)
    claimed = int(tok) if tok.isdigit() else _CJK_NUM.get(tok)
    if claimed is None:
        return []
    set_key = None
    for key, spec in CONDITION_SETS.items():
        for nm in spec['names']:
            if nm.lower() in clause.lower():
                set_key = key
                break
    if not set_key:
        return []
    spec = CONDITION_SETS[set_key]
    sat = 0
    detail = []
    for cond in spec['conditions']:
        f = _fact_of(snapshot, cond['metric'])
        rec = _change_field(f or {}, cond['window'])
        v = rec.get('pct_change') if cond['kind'] == 'pct' \
            else rec.get('pp_change')
        if not _is_num(v):
            detail.append(f'{cond["label"]}:无可算变化')
            continue
        hit = (v < cond['ref']) if cond['op'] == '<' else (v > cond['ref'])
        sat += hit
        detail.append(f'{cond["label"]}={v:+g}{"✓" if hit else "✗"}')
    ok = sat == claimed
    return [{'family': 'compound_condition_count', 'token': f'满足{claimed}条',
             'value': claimed, 'expected': sat,
             'status': 'VERIFIED' if ok else 'CONTRADICTED',
             'note': '; '.join(detail)}]


def _check_band_relation(clause, snapshot, thresholds_by=None):
    """带关系断言: 突破X/站上X/进入强势区间/已处恐慌区(条件句除外)。"""
    if re.search(r'若|如果|将转为|后续|一旦|预期', clause):
        return []
    checks = []
    mids = _find_alias(clause)
    mid = mids[0][0] if mids else _CTX_STATE.get('carry_mid')
    if not mid:
        return checks
    fact = _fact_of(snapshot, mid)
    if not fact or not _is_num(fact['value']):
        return checks
    for m in re.finditer(r'(突破|站上|越过|升至…上方|收于?…?上方|已处)', clause):
        seg = clause[m.end():m.end() + 30]
        toks = [t for t in _extract_tokens(seg)
                if t['kind'] in ('percent', 'pp', 'plain')]
        if not toks:
            continue
        tv = toks[0]['value']
        claim_above = '上方' in clause or '突破' in m.group(1) or \
            '站上' in m.group(1) or '越过' in m.group(1)
        if m.group(1) == '已处':
            claim_above = '上方' not in clause[m.end():m.end() + 12]
        actual_above = fact['value'] > tv
        ok = (claim_above == actual_above)
        checks.append({'family': 'band_relation', 'token': toks[0]['raw'],
                       'value': tv, 'expected': fact['value'],
                       'status': 'VERIFIED' if ok else 'CONTRADICTED',
                       'note': f'断言{"上方" if claim_above else "下方"}'
                               f'({tv}) vs 实际{fact["value"]:g}'
                               f'{"上方" if actual_above else "下方"}'})
    return checks


def _check_prior_reverse(clause, snapshot, thresholds_by=None):
    """反推恒等式: 上一交易日口径约X，由Y%反推 → X≈level/(1+pct)。"""
    if '反推' not in clause:
        return []
    mids = _find_alias(clause)
    mid = mids[0][0] if mids else _CTX_STATE.get('carry_mid')
    if not mid:
        return []
    fact = _fact_of(snapshot, mid)
    if not fact or not _is_num(fact['value']):
        return []
    toks = _extract_tokens(clause)
    pct = next((t for t in toks if t['kind'] == 'percent'), None)
    lvl = next((t for t in toks if t['kind'] in ('plain', 'K', 'thousands')),
               None)
    if not (pct and lvl):
        return []
    prior = fact['value'] / (1.0 + pct['value'] / 100.0)
    ok = _value_matches(lvl['value'], round(prior, 4), True)
    return [{'family': 'prior_reverse_identity', 'token': lvl['raw'],
             'value': lvl['value'], 'expected': round(prior, 4),
             'status': 'VERIFIED' if ok else 'CONTRADICTED',
             'note': f'{fact["value"]:g}/(1{pct["value"]:+g}%)={prior:.4g}'}]


# ── 语义族检查器(T8 整改轮新增) ────────────────────────────────────

_BAND_LABEL_WORDS = [
    (re.compile(r'恐慌(区|带|段)'), 'panic'),
    (re.compile(r'警告(区|带|段)|警戒(区|带|段)'), 'warning'),
    (re.compile(r'关注(区|带|段)|注意(区|带|段)'), 'attention'),
]


def _check_band_label(clause, snapshot, thresholds_by=None):
    """带标签断言: 「仍处恐慌区(>500bp)」对照注册表带位(值实际落入哪档)。"""
    checks = []
    mids = _find_alias(clause)
    mid = mids[0][0] if mids else _CTX_STATE.get('carry_mid')
    if not mid:
        return checks
    fact = _fact_of(snapshot, mid)
    if not fact or not _is_num(fact['value']):
        return checks
    bands = sorted([(e['kind'], e['value'])
                    for e in (thresholds_by or {}).get(mid, [])
                    if e.get('kind') in ('attention', 'warning', 'panic')
                    and _is_num(e.get('value'))], key=lambda kv: kv[1])
    if len(bands) < 2:
        return checks
    actual = None
    for i, (kind, v) in enumerate(bands):
        upper = bands[i + 1][1] if i + 1 < len(bands) else None
        if fact['value'] >= v and (upper is None or fact['value'] < upper):
            actual = kind
            break
    if actual is None:
        return checks
    for pat, want_kind in _BAND_LABEL_WORDS:
        m = pat.search(clause)
        if not m:
            continue
        band_kinds = [k for k, _ in bands]
        want_idx = band_kinds.index(want_kind) if want_kind in band_kinds \
            else None
        if want_idx is None:
            continue
        # 否定/边界语境: 「尚在警告带下沿之内/未达X区」=声称低于该带
        below_ctx = bool(re.search(
            r'下沿之内|下缘之内|下方|以下|未达|未进入|低于|之外|以内',
            clause[m.end():m.end() + 10]))
        above_ctx = bool(re.search(
            r'上沿之上|上方|以上|超过|之上', clause[m.end():m.end() + 10]))
        if below_ctx or above_ctx:
            eff_idx = want_idx - 1 if below_ctx else want_idx + 1
            if eff_idx < 0 or eff_idx >= len(bands):
                # 声称越出带表之外(如低于最低带)→ 与带表核对
                checks.append({
                    'family': 'band_label', 'token': m.group(0),
                    'metric': mid, 'value': fact['value'],
                    'expected': bands[want_idx][0],
                    'status': 'CONTRADICTED'
                    if (below_ctx and fact['value'] >= bands[0][1]) or
                       (above_ctx and fact['value'] <= bands[-1][1])
                    else 'VERIFIED',
                    'note': f'带表{bands} vs 值{fact["value"]:g}'})
                continue
            ok = (band_kinds.index(actual) == eff_idx)
            note = (f'值{fact["value"]:g}实际处[{actual}]带 vs '
                    f'声称{"低于" if below_ctx else "高于"}'
                    f'[{want_kind}]带(应处[{band_kinds[eff_idx]}])')
        else:
            ok = (actual == want_kind)
            note = (f'值{fact["value"]:g}实际处[{actual}]带 '
                    f'vs 标签[{want_kind}]')
        checks.append({
            'family': 'band_label', 'token': m.group(0), 'metric': mid,
            'value': fact['value'],
            'expected': '/'.join(f'{k}≥{v:g}' for k, v in bands),
            'status': 'VERIFIED' if ok else 'CONTRADICTED',
            'note': note})
    return checks


def _score_band4(v, m1, m2, p1, p2):
    """macro_scorecard 同构带链(左开右闭): v< m1→-2 … v≥p2→+2。"""
    if v < m1:
        return -2
    if v < m2:
        return -1
    if v < p1:
        return 0
    if v < p2:
        return 1
    return 2


def _score_band_rev(v, p05, p03, m01, m03):
    """失业率3月反向带链(macro_scorecard 同构): 升=负分。"""
    if v > p05:
        return -2
    if v > p03:
        return -1
    if v > m01:
        return 0
    if v > m03:
        return 1
    return 2


def _check_score_total(clause, snapshot, thresholds_by=None):
    """评分卡总分断言: 「通胀总分+3」按快照事实+签字阈值注册表独立复算。

    维度组成=scorecard_spec 单源规格表(RDG-20261116-011,与
    macro_scorecard 同源;新增指标只改规格表+签字注册表,禁此处平行枚举)。
    """
    if '总分' not in clause:
        return []
    th = {e['stable_key']: e['value']
          for es in (thresholds_by or {}).values() for e in es
          if e.get('stable_key') and _is_num(e.get('value'))}
    facts = {f['metric_id']: f for f in snapshot.get('facts', [])}

    def _lv(mid):
        f = facts.get(mid)
        return f['value'] if f and _is_num(f.get('value')) else None

    def _dv(mid, win, field):
        f = facts.get(mid)
        v = ((f or {}).get('derived') or {}).get(win, {}).get(field)
        return v if _is_num(v) else None

    def _score_row(metric, source, band_kind, keys):
        """行打分: 取数(source)→带链(std/rev);值或键缺→None(不计0分)。"""
        v = _lv(metric) if source == ('level',) \
            else _dv(metric, source[0], source[1])
        ks = [th.get(k) for k in keys]
        if v is None or any(k is None for k in ks):
            return None
        return _score_band4(v, *ks) if band_kind == 'std' \
            else _score_band_rev(v, *ks)

    dim_parts = {dim: [(metric, _score_row(metric, src, band, keys))
                       for metric, src, band, keys in rows]
                 for dim, rows in scorecard_spec.SCORECARD_DIMENSIONS}
    dim_total = {dim: (sum(s for _, s in parts)
                       if all(s is not None for _, s in parts) else None)
                 for dim, parts in dim_parts.items()}
    i_total = dim_total.get('通胀')
    g_total = dim_total.get('增长')

    checks = []
    for dim, parts in dim_parts.items():
        total = dim_total[dim]
        m = re.search(dim + r'总分\s*([+\-−]?\d+)', clause)
        if not m:
            continue
        claimed = int(m.group(1))
        if total is None:
            miss = [mid for mid, s in parts if s is None]
            checks.append({'family': 'scorecard_total',
                           'token': m.group(0), 'value': claimed,
                           'expected': None,
                           'status': 'INSUFFICIENT_EVIDENCE',
                           'note': f'成分缺失不计0分: {miss}'})
            continue
        ok = claimed == total
        detail = '+'.join(f'{mid}{s:+d}' for mid, s in parts)
        checks.append({'family': 'scorecard_total', 'token': m.group(0),
                       'value': claimed, 'expected': total,
                       'status': 'VERIFIED' if ok else 'CONTRADICTED',
                       'note': f'{detail}={total:+d}'})
    # 体制映射(滞胀/类滞胀/再通胀/衰退; determine_regime 同构)
    if i_total is not None and g_total is not None and \
            re.search(r'映射|维持|切换|体制', clause):
        m = re.search(r'类滞胀|滞胀|再通胀|衰退|过热', clause)
        if m:
            floor = th.get('regime.inflation_total.stagflation_floor')
            zero = th.get('regime.growth_total.zero')
            if floor is not None and zero is not None:
                if i_total >= floor:
                    regime = '类滞胀' if g_total > zero else '滞胀'
                else:
                    regime = '再通胀' if g_total > zero else '衰退'
                claimed_r = m.group(0)
                ok = (claimed_r == regime)
                checks.append({'family': 'regime_mapping',
                               'token': claimed_r, 'value': claimed_r,
                               'expected': regime,
                               'status': 'VERIFIED' if ok
                               else 'CONTRADICTED',
                               'note': f'i={i_total:+d},g={g_total:+d}'
                                       f'→{regime} vs 声称{claimed_r}'})
    return checks


def _check_probability_sum(clause, snapshot, thresholds_by=None):
    """情景概率和: 枚举概率项之和=100%(竖线/顿号枚举或显式「概率和」)。"""
    if not re.search(r'概率|机率|probability', clause, re.I):
        return []
    if not re.search(r'概率和|[｜|]', clause):
        return []          # 非枚举语境(孤立概率词)不整句求和
    mcl = _masked_clause(clause, _find_alias(clause))
    toks = [t for t in _extract_tokens(mcl)
            if t['kind'] == 'percent' and 0 < t['value'] <= 100]
    if len(toks) < 3:
        return []
    s = round(sum(t['value'] for t in toks), 4)
    ok = abs(s - 100.0) <= 0.05 + 1e-9
    return [{'family': 'probability_sum',
             'token': '、'.join(t['raw'] for t in toks),
             'value': s, 'expected': 100.0,
             'status': 'VERIFIED' if ok else 'CONTRADICTED',
             'note': f'{len(toks)}项概率和={s:g}% vs 100%'}]


def _check_target_range(clause, snapshot, thresholds_by=None):
    """当前目标区间断言: 「当前目标区间4.07–4.32%」对照 DFEDTARL/U。

    前瞻口径(期货隐含/下月, 无「当前/现行」限定)不属事实区间,跳过。
    """
    if not re.search(r'目标区间|target range', clause, re.I):
        return []
    forward = bool(re.search(r'期货隐含|隐含|预期|下月|次月|对应\d{4}', clause))
    current = bool(re.search(r'当前|现行|目前|currently', clause, re.I))
    if forward and not current:
        return []
    fl = _fact_of(snapshot, 'DFEDTARL')
    fu = _fact_of(snapshot, 'DFEDTARU')
    if not (fl and fu and _is_num(fl.get('value')) and _is_num(fu.get('value'))):
        return []
    m = re.search(r'(\d{1,2}(?:\.\d+)?)\s*[–—-]\s*(\d{1,2}(?:\.\d+)?)\s*%'
                  , clause)
    if not m:
        return []
    lo, hi = float(m.group(1)), float(m.group(2))
    ok = abs(lo - fl['value']) <= 0.005 + 1e-9 and \
        abs(hi - fu['value']) <= 0.005 + 1e-9
    return [{'family': 'target_range', 'token': m.group(0),
             'value': [lo, hi], 'expected': [fl['value'], fu['value']],
             'status': 'VERIFIED' if ok else 'CONTRADICTED',
             'note': f'快照区间[{fl["value"]:g},{fu["value"]:g}]% '
                     f'vs 文本[{lo:g},{hi:g}]%'}]


# ── 叙事-数值方向后置检查(别名免依赖) ────────────────────────────────

# 前瞻/历史语境守卫(R38/RDG-20261115-010;一审 MAJOR-3 改逐命中粒度):
# 预测句/历史泛述不对当前周窗核方向;取向=宁漏报不误杀,与 T8R2 审计
# 「不误杀但也不拦」哲学同向;全族一致(DXY/EURUSD/GBPUSD/USDJPY/
# CURVE_2S10S)。粒度=逐正则命中(非整句,防真阳性被同句异段预期词连带杀,
# 一审 FN9 实锤: 「本周美元走弱，市场预期降息」)。
_NARR_FORWARD_RE = re.compile(
    r'预计|预期|预测|展望|前瞻|料将|或将|有望|方向判断|纯逻辑|逻辑推理'
    r'|置信|历史上|历年|历来|曾'
    r'|expect|forecast|project\b|likely', re.I)
_NARR_SUFFIX_RE = re.compile(r'(?:的)?(?:预期|预测|展望|概率|押注|期望)')
_NARR_BEFORE_WIN = 14    # 前瞻/历史标记回看窗(字符)
_NARR_HOST_WIN = 20      # 括注宿主窗(括注内命中回看开括号前文,窗可更宽)
# R40 MAJOR-3b(RDG-010 残余): 当前周锚——标记与命中之间出现锚=语句
# 重新锚定当前周窗,豁免前瞻豁免(G5/G7/B2 恢复 main 拦截)。
_NARR_CURWEEK_RE = re.compile(r'本周|当周|周内')


def _narr_is_forward(clause, m):
    """该叙事命中是否处前瞻/历史语境(不对当前周窗核方向)。

    判据: ①命中点前 14 字符窗内有标记;②命中点在括注内且开括号前 20
    字符窗内有标记(括注继承宿主句模态;真实实例 20261113T005117Z
    「资产方向判断: USDJPY 下行(日元升值)」的括注);③命中点紧跟
    「(的)预期/预测/展望/概率/押注」(「日元升值的预期升温」=预期对象
    非事实断言)。
    R40 MAJOR-3b: 判据①加当前周锚豁免——标记与命中之间(标记之后)
    出现「本周/当周/周内」→语句已重新锚定当前周,按当前周窗核方向
    (「通胀预期回落的同时,本周美元走弱」=G5 当前周事实,非预期句)。
    锚须在标记之后: 锚在标记前(「本周市场预期美元走弱」)仍是预期句,
    不豁免。
    """
    before = clause[max(0, m.start() - _NARR_BEFORE_WIN):m.start()]
    fm = _NARR_FORWARD_RE.search(before)
    if fm and not _NARR_CURWEEK_RE.search(before[fm.end():]):
        return True
    if _NARR_SUFFIX_RE.match(clause, m.end()):
        return True
    depth = 0
    for i in range(m.start() - 1, max(0, m.start() - 40) - 1, -1):
        if clause[i] in '）)':
            depth += 1
        elif clause[i] in '（(':
            if depth == 0:
                host = clause[max(0, i - _NARR_HOST_WIN):i]
                return bool(_NARR_FORWARD_RE.search(host))
            depth -= 1
    return False


# FX 族规格表(RDG-20261115-010 表驱动;覆盖扩展=加行,不改控制流):
#   (metric_id, 主体升叙事正则, 主体降叙事正则, 叙事升⇔序列升?, 升token, 降token)
# - 叙事主体=基准货币(欧元/英镑)⇒直读;USDJPY 叙事主体=计价货币日元⇒反序
#   (日元升⇔USDJPY 降,direction_semantics 报价对先例)。
# - 主体锚守卫(全族含 DXY/EURUSD 回灌,一审 MAJOR-2/FP7): (?<![兑/对])
#   防「美元兑/对日元…」「欧元兑英镑…」「日元兑美元贬值(内嵌美元贬值)」
#   等交叉盘/对名短语把方向词误锚到非主体币;(?<![\d.,，。])防货币金额
#   后缀(N美元回落=油价跌/N日元)。
# - USDJPY 对名直读行(「美元兑/对日元/USDJPY(汇率/本周…)?+方向词」作用
#   于序列值本身)单列,防「美元兑日元走弱」(=对名走弱=序列降)被主体行
#   反序误读;时间状语(本周/当周/周内)容许介入(一审 MINOR-1)。
# - DXY/EURUSD 中文正则与 token 原样迁入(行为保持);英文子正则原样
#   (=单空格,一审 NIT-1 校正);EURUSD 词汇面较窄为既有口径,新族词汇
#   宽度随 DXY 口径;yen/pound 加中英混排(yen 升值,一审 MINOR-2)。
_NARR_FX_ROWS = (
    ('DXY',
     r'(?<![\d.,，。])(?<![兑/对])美元(?:指数)?(?:走强|升值|走高|回升)'
     r'|dollar(?: index)?\s+(?:strengthen|firm)',
     r'(?<![\d.,，。])(?<![兑/对])美元(?:指数)?(?:走弱|贬值|走低|回落)'
     r'|dollar(?: index)?\s+(?:weaken|soft)',
     True, '美元走强', '美元走弱'),
    ('EURUSD',
     r'(?<![兑/对])欧元(?:升值|上涨|走强)'
     r'|euro\s+(?:appreciat|strengthen|rising)',
     r'(?<![兑/对])欧元(?:贬值|下跌|走弱)'
     r'|euro\s+(?:depreciat|weaken|falling)',
     True, '欧元升值', '欧元贬值'),
    ('GBPUSD',
     r'(?<![\d.,，。])(?<![兑/对])英镑(?:兑美元|对美元)?(?:升值|上涨|走强|回升|走高)'
     r'|pound(?:\s+sterling)?\s+(?:appreciat|strengthen|rising|升值|走强)',
     r'(?<![\d.,，。])(?<![兑/对])英镑(?:兑美元|对美元)?(?:贬值|下跌|走弱|回落|走低)'
     r'|pound(?:\s+sterling)?\s+(?:depreciat|weaken|falling|贬值|走弱)',
     True, '英镑升值', '英镑贬值'),
    ('USDJPY',
     r'(?<![\d.,，。])(?<![兑/对])日元(?:兑美元)?(?:升值|上涨|走强|回升|走高)'
     r'|(?<![\d.,，。])yen\s+(?:大幅|明显|显著|温和|小幅)?\s*'
     r'(?:appreciat|strengthen|rising|升值|走强)',
     r'(?<![\d.,，。])(?<![兑/对])日元(?:兑美元)?(?:贬值|下跌|走弱|回落|走低)'
     r'|(?<![\d.,，。])yen\s+(?:大幅|明显|显著|温和|小幅)?\s*'
     r'(?:depreciat|weaken|falling|贬值|走弱)',
     False, '日元升值', '日元贬值'),
    ('USDJPY',
     r'(?:美元兑日元|美元对日元|美元/日元|USD\s*/\s*JPY|USD\s*-\s*JPY|USDJPY)'
     r'(?:汇率)?\s*(?:本周|当周|周内|日内)?\s*'
     r'(?:上行|走高|上涨|回升|走强|升值)',
     r'(?:美元兑日元|美元对日元|美元/日元|USD\s*/\s*JPY|USD\s*-\s*JPY|USDJPY)'
     r'(?:汇率)?\s*(?:本周|当周|周内|日内)?\s*'
     r'(?:下行|走低|下跌|回落|走弱|贬值)',
     True, '美元兑日元上行', '美元兑日元下行'),
)


def _check_narrative_direction(text, snapshot):
    """叙事方向词与数值事实相反 → CONTRA(美元走弱 vs DXY 周涨)。

    R38(RDG-20261115-010)表驱动: FX 族规格=_NARR_FX_ROWS(扩展=加行);
    前瞻/历史语境逐命中守卫(_narr_is_forward,全族一致);2s10s 倒挂族
    语义独异(倒挂/加深/缓解+解除语境排除)保持专段。
    """
    checks = []

    def _wk(mid, field):
        f = _fact_of(snapshot, mid)
        if not f:
            return None
        v = ((f.get('derived') or {}).get('week') or {}).get(field)
        return v if _is_num(v) else None

    def _unguarded(clause, pat):
        """首个非前瞻/历史语境命中(逐命中守卫,一审 MAJOR-3 粒度修)。"""
        for m in re.finditer(pat, clause, re.I):
            if not _narr_is_forward(clause, m):
                return m
        return None

    for clause in _clause_split(text):
        wk_cache = {}
        for mid, up_re, dn_re, up_is_up, up_tok, dn_tok in _NARR_FX_ROWS:
            if mid not in wk_cache:
                wk_cache[mid] = _wk(mid, 'pct_change')
            chg = wk_cache[mid]
            if chg is None:
                continue
            if up_is_up:      # 直读族: 主体升叙事⇔序列应升
                up_contra, up_exp = chg < -0.05, '>0'
                dn_contra, dn_exp = chg > 0.05, '<0'
            else:             # 反序族(USDJPY 主体=日元): 主体升⇔序列应降
                up_contra, up_exp = chg > 0.05, '<0'
                dn_contra, dn_exp = chg < -0.05, '>0'
            # (?<![\d.,，。]) 挡货币后缀形态(N美元回落=油价跌,非美元叙事)
            if up_contra and _unguarded(clause, up_re):
                checks.append({'family': 'narrative_direction',
                               'token': up_tok, 'metric': mid,
                               'value': chg, 'expected': up_exp,
                               'status': 'CONTRADICTED',
                               'note': f'叙事{up_tok} vs {mid}周{chg:+g}%'})
            if dn_contra and _unguarded(clause, dn_re):
                checks.append({'family': 'narrative_direction',
                               'token': dn_tok, 'metric': mid,
                               'value': chg, 'expected': dn_exp,
                               'status': 'CONTRADICTED',
                               'note': f'叙事{dn_tok} vs {mid}周{chg:+g}%'})
        curve = _fact_of(snapshot, 'CURVE_2S10S')
        m_inv = re.search(r'倒挂', clause)
        if curve and _is_num(curve.get('value')) and m_inv and \
                not _narr_is_forward(clause, m_inv) and not re.search(
                    r'不再倒挂|脱离倒挂|告别倒挂|无倒挂|没有倒挂|后无倒挂|'
                    r'倒挂(?:解除|结束|消失|修复)',
                    clause):
            v = curve['value']
            pp = _wk('CURVE_2S10S', 'pp_change')
            if v >= 0:
                checks.append({'family': 'narrative_direction',
                               'token': '倒挂', 'metric': 'CURVE_2S10S',
                               'value': v, 'expected': '<0',
                               'status': 'CONTRADICTED',
                               'note': f'叙事倒挂 vs 2s10s={v:g}pp(非负)'})
            elif pp is not None:
                if re.search(r'加深|恶化|更陡', clause) and pp > 0:
                    checks.append({'family': 'narrative_direction',
                                   'token': '倒挂加深', 'metric': 'CURVE_2S10S',
                                   'value': pp, 'expected': '<0',
                                   'status': 'CONTRADICTED',
                                   'note': f'叙事加深 vs 周变化{pp:+g}pp(转浅)'})
                if re.search(r'缓解|收窄|转浅|陡峭化', clause) and pp < 0:
                    checks.append({'family': 'narrative_direction',
                                   'token': '倒挂缓解', 'metric': 'CURVE_2S10S',
                                   'value': pp, 'expected': '>0',
                                   'status': 'CONTRADICTED',
                                   'note': f'叙事缓解 vs 周变化{pp:+g}pp(加深)'})
    return checks


def _check_slash_enum(clause, snapshot, thresholds_by=None):
    """斜杠枚举值列(SPX +3.1554/VIX −30.8112/HY_OAS −0.08 形,引擎信封 basis):

    ≥2 对「别名+紧随值」且对间仅隔斜杠→枚举列;逐对按指标面单位族核对周窗
    变化(percent/percentage_point→pp,其余→pct;显式 % 后缀强制 pct)。
    孤立值不走此器(留主循环),防误吞普通叙述。
    """
    checks = []
    hits = _find_alias(clause)
    pairs = []
    for i, (mid, s, e) in enumerate(hits):
        m = re.match(r'\s*(?P<sg>[+−\-])?(?P<num>\d[\d,]*(?:\.\d+)?)'
                     r'\s*(?P<u>%|pp|个百分点)?', clause[e:e + 18])
        if not m:
            continue
        vs = e + (m.start('sg') if m.group('sg') else m.start('num'))
        pairs.append({'mid': mid, 'i': i, 'v': _strip_num(m.group('num')),
                      'neg': (m.group('sg') or '') in ('-', '−', '−'),
                      'unit': m.group('u'), 'vs': vs,
                      've': e + (m.end('u') if m.group('u')
                                 else m.end('num'))})
    seen = set()
    for a, b in zip(pairs, pairs[1:]):
        between = clause[a['ve']:hits[b['i']][1]]
        if not re.fullmatch(r'\s*[/／]\s*', between):
            continue
        for p in (a, b):
            if (p['mid'], p['vs']) in seen:
                continue
            seen.add((p['mid'], p['vs']))
            mid, fact = p['mid'], _fact_of(snapshot, p['mid'])
            if not fact:
                continue
            val = -p['v'] if p['neg'] else p['v']
            wk = (fact.get('derived') or {}).get('week') or {}
            if p['unit'] == '%':
                exp = wk.get('pct_change')
            elif p['unit'] in ('pp', '个百分点'):
                exp = wk.get('pp_change')
            elif fact.get('unit') in ('percent', 'percentage_point'):
                exp = wk.get('pp_change')
            else:
                exp = wk.get('pct_change')
            if not _is_num(exp):
                continue
            ok = _value_matches(val, exp)
            checks.append({
                'family': 'slash_enum', 'token': clause[p['vs']:p['ve']],
                'metric': mid, 'value': val, 'expected': exp,
                'status': 'VERIFIED' if ok else 'CONTRADICTED',
                'note': f'枚举周窗 {mid} {exp:+g}'})
    return checks


# ── 主检: migration mode ────────────────────────────────────────────

_CONST_UNIT_FAMILY = {
    'percent': ('percent', cf.CANONICAL_PP),
    'pp': ('percent', cf.CANONICAL_PP),
    'plain': ('index_point', 'usd_per_barrel', 'score_point'),
    '亿': ('cny_100m',),
}


def _registry_const_hit(t, thresholds_by):
    """token 值=注册表某阈值(单位族相容)→ (metric_id, entry);无则 None。"""
    fams = _CONST_UNIT_FAMILY.get(t['kind'])
    if not fams or t['value'] is None:
        return None
    for mid, es in (thresholds_by or {}).items():
        for e in es:
            if e.get('unit') in fams and _is_num(e.get('value')) and \
                    abs(t['value'] - e['value']) <= 0.005 + 1e-9:
                return mid, e
    return None


SPECIAL_CHECKERS = [
    _check_threshold_constant, _check_distance, _check_corr, _check_rank,
    _check_spread, _check_additivity, _check_consecutive,
    _check_compound_count, _check_band_relation, _check_prior_reverse,
    _check_band_label, _check_score_total, _check_probability_sum,
    _check_target_range, _check_slash_enum,
]


def check_text(text, *, snapshot, thresholds=None, prior_anchors=None,
               _zonal=None):
    """迁移门检: 文本→逐断言裁决。

    返回 {'verdict', 'checks', 'unbound', 'stats'}: verdict ∈
    CONTRADICTED / VERIFIED / INSUFFICIENT_EVIDENCE。
    prior_anchors: {date_str: anchors_dict} 前情锚链(上期引用面)。
    """
    thresholds_by = cf.thresholds_by_metric(
        thresholds if thresholds is not None else cf.load_thresholds())
    # 检查面预处理(RDG-20261116-013): HTML 注释/JSON provenance 行=
    # 非散文构造物,不进子句域(全下游消费点共用此 text)
    text = _checkface_preprocess(text)
    checks = []
    unbound = []
    facts_zone = bool(_FACT_ZONE_RE.search(text))
    owned_ctx = re.compile(
        r'相关|距离|距警告|警告线|恐慌线|红线|强势阈值|警戒线|正常线上限|'
        r'连续第|周收于|利差|贡献|反推|加总构成|已满足|中性区间|区间上沿|'
        r'区间下沿|带下沿|带上沿|关口|站上|概率|总分|目标区间|恐慌区|'
        r'警告区|警戒区|关注带')
    # 利差辖域披露面(RDG-20261115-008): 检查器未消费的 percent/pp token
    # 落 spread_ambiguous 披露,禁静默吞(契约律8: 未映射须显式披露)
    _spread_ctx = '利差'
    prior_obs = {}
    if prior_anchors:
        for date, anc in sorted(prior_anchors.items()):
            for f in _anchor_facts(anc):
                if f.get('metric_id') is not None and _is_num(f.get('value')):
                    prior_obs.setdefault(f['metric_id'], []).append(
                        (str(date), f['value']))
    _CTX_STATE['prior_obs'] = prior_obs
    carry_mid = None
    for clause in _clause_split(text):
        mids_in = _find_alias(clause)
        if mids_in:
            carry_mid = mids_in[0][0]
            _CTX_STATE['carry_mid'] = carry_mid
        # 语义族检查器先跑(各自消费专属 token;原始子句)
        consumed = set()           # 检查器已裁决 token(主循环跳过+不落 unbound)
        for fn in SPECIAL_CHECKERS:
            try:
                for ch in fn(clause, snapshot, thresholds_by) or []:
                    checks.append(ch)
                    for part in re.split(r'[/、,，]', str(ch.get('token') or '')):
                        if part.strip():
                            consumed.add(part.strip())
                    # 价差算术命中值入 consumed(RDG-008 审计修: token 字段
                    # 为整段匹配串,裸数值 token 须并入被裁集;句级抑制会
                    # 吞同句异段无关利差数值=MAJOR-1,故弃 flag 用被裁集)
                    if ch.get('family') == 'spread_arithmetic':
                        for t2 in _extract_tokens(str(ch.get('token') or '')):
                            consumed.add(t2['raw'].strip())
            except Exception:      # 检查器异常不吞主流程;记录后继续
                checks.append({'family': getattr(fn, '__name__', '?'),
                               'token': '', 'value': None, 'expected': None,
                               'status': 'INSUFFICIENT_EVIDENCE',
                               'note': 'checker_error(检查器异常降级)'})
        masked = _masked_clause(clause, mids_in)
        for t in _extract_tokens(masked):
            if t['raw'].strip() in consumed:
                continue            # 检查器已裁决(如 反推恒等/相关)
            seg_start = clause.rfind('，', 0, t['start']) + 1
            seg_end_i = clause.find('，', t['end'])
            seg_scoped = clause[seg_start:seg_end_i if seg_end_i > 0
                                else len(clause)]
            # 注册表常量路由: 值=注册表阈值 且 句段带阈值语境词 → 常量复述
            # (104/90/5%/500bp/1万亿 类;防叙事整数值误绑指标水平)
            if t['kind'] in ('percent', 'pp', 'plain', '亿'):
                reg_hit = _registry_const_hit(t, thresholds_by)
                if reg_hit and re.search(
                        r'阈值|threshold|红线|警戒线|警告线|恐慌线|恐慌区|'
                        r'底部确认|scorecard|评分', seg_scoped, re.I):
                    _mid_r, e_r = reg_hit
                    checks.append({
                        'family': 'threshold_constant', 'token': t['raw'],
                        'metric': _mid_r, 'value': t['value'],
                        'expected': e_r['value'], 'status': 'VERIFIED',
                        'note': f'{e_r["stable_key"]}常量复述'})
                    continue
            if owned_ctx.search(seg_scoped):
                # 辖域跳过≠披露豁免(律8/T6;RDG-20261115-008): 利差歧义族
                # 未被检查器消费的数值 token 落披露面(INSUFFICIENT_EVIDENCE
                # =契约「须披露可发布」档;不判错不改判聚合)
                if (_spread_ctx in seg_scoped
                        and t['kind'] in ('percent', 'pp')):
                    checks.append({
                        'family': 'spread_ambiguous', 'token': t['raw'],
                        'metric': None, 'value': t['value'],
                        'expected': None,
                        'status': 'INSUFFICIENT_EVIDENCE',
                        'note': '利差语境数值未验证(非价差算术裁决面: '
                                '无相异指标对/派生利差不在别名表/'
                                '算术操作数复述);披露不判错'})
                continue            # 语义族检查器辖域(同逗号段)
            # 前值角色先行(标记式;不依赖绑定): prior_reference 后置核
            if _prior_role(clause, t):
                continue
            t = dict(t, ctx=clause[max(0, t['start'] - 24):t['end'] + 24])
            # 别名绑定: 前向优先(token 之前的最近别名;枚举句 EA-5),
            # 无前向别名才回退全域最近
            mid, best_d = None, 1e9
            prec = [(m2, abs(t['start'] - e0))
                    for m2, s0, e0 in mids_in if e0 <= t['start'] + 4]
            if prec:
                mid, best_d = min(prec, key=lambda h: h[1])
            else:
                for m2, s0, e0 in mids_in:
                    d = 0 if (t['start'] < e0 and t['end'] > s0 - 4) else \
                        min(abs(t['start'] - e0), abs(s0 - t['end']))
                    if d < best_d:
                        mid, best_d = m2, d
            if mid is None and carry_mid is not None and (
                    (t['kind'] in ('percent', 'pp')
                     and (_window_of(clause, t) or _direction_of(clause)))
                    or (t['kind'] in ('亿', 'plain', 'K', 'thousands')
                        and re.search(r'净减少|净增加|新增|减少|增加|'
                                      r'rising|rose|climbed|falling|fell|'
                                      r'dropped|decline|上升|下降|回落|回升',
                                      t['ctx']))
                    or (t['approx'] and _fact_of(snapshot, carry_mid)
                        and _display_aligned(
                            t['raw'], t['value'],
                            _fact_of(snapshot, carry_mid)['value'],
                            approx=True))):
                mid = carry_mid          # 承前句指标(环比下降0.10%/净减少X/
                                        # 约数复述约1.22万亿 形态)
            if mid is not None and mids_in and best_d > 34:
                # 句内远距: 合格 token(约数对齐/方向/窗口)回退绑句内首选别名
                fm = _fact_of(snapshot, mid)
                if not (fm and (
                        (t['approx'] and _display_aligned(
                            t['raw'], t['value'], fm['value'], approx=True))
                        or (t['kind'] in ('percent', 'pp')
                            and (_window_of(clause, t)
                                 or _direction_of(clause)))
                        or re.search(r'净减少|净增加|新增|减少|增加|rising|'
                                     r'rose|climbed|falling|fell|dropped|'
                                     r'decline|上升|下降|回落|回升', t['ctx']))):
                    mid = None
            if mid is None:
                if t['kind'] != 'nan':
                    unbound.append({'raw': t['raw'], 'ctx': t['ctx'][:40],
                                    'zone_fact': facts_zone})
                continue
            fact = _fact_of(snapshot, mid)
            if not fact:
                unbound.append({'raw': t['raw'], 'ctx': t['ctx'][:40],
                                'zone_fact': facts_zone, 'reason':
                                f'{mid} 不在快照'})
                continue
            if _prior_role(clause, t, fact.get('observation_date')):
                continue            # 上期日期限定形态(week of <旧日期>)
            val = _scale_k(t['value'], t['kind'], fact)
            signed = bool(re.search(r'[+\-−]', t['raw'].strip()[:1])) or \
                t['raw'].strip().startswith(('+', '-', '−'))
            direction = _direction_of(clause)
            win = _window_of(clause, t)
            level_mark = bool(re.search(
                r'(?:至|到|收于|报|为|是|持平|to|at)\s*$', clause[:t['start']]))
            claim, fam = None, None
            if t['kind'] == 'day':
                claim = cf._claim(
                    'observation_lag', 'as_of_minus_observation', mid,
                    int(val), 'calendar_day',
                    fact['observation_date'], snapshot['research_as_of'],
                    [cf._fact_ref(fact)], [fact['fact_id']],
                    '迁移门瞬态(滞后)',
                    as_of_date=str(snapshot['research_as_of'])[:10])
                fam = 'observation_lag'
                # 换算复述(约166天(约5个半月)): 月数一致性(约数容差)
                dm = re.search(r'约?(\d+(?:\.\d+)?)\s*(个)?半?月', clause)
                if dm:
                    months = val / 30.4375
                    mv = float(dm.group(1))
                    if '半' in dm.group(0):
                        mv += 0.5     # N个半月 = N+0.5 月
                    ok_d = abs(months - mv) <= max(0.3, 0.06 * abs(mv))
                    checks.append({'family': 'lag_duration',
                                   'token': dm.group(0), 'metric': mid,
                                   'value': mv, 'expected': round(months, 2),
                                   'status': 'VERIFIED' if ok_d
                                   else 'CONTRADICTED',
                                   'note': f'{val:g}天≈{months:.2f}月 '
                                           f'vs {dm.group(0)}'})
            elif t['kind'] in ('percent', 'pp'):
                # 值后紧邻处位动词(处/位于/落在/为/是)=水平断言(+0.25pp
                # 处年内最平端:符号为正负性标注而非变化方向)
                post_level = bool(re.match(
                    r'\s{0,2}(?:处|位于|落在|为|是)',
                    clause[t['end']:t['end'] + 8]))
                # 混向子句(同句走阔+微收)取 token 前邻局部方向词
                if not direction:
                    direction = _direction_of(
                        clause[max(0, t['start'] - 12):t['start']]) or 0
                if (signed or win or direction) and not level_mark \
                        and not post_level:
                    # 带符号+无窗口词+无方向词+值与水平显示位对齐=水平复述
                    # (CURVE_2S10S +0.25pp(L1 事实…):符号为正负性标注)
                    if signed and not win and not direction:
                        f_lv = _fact_of(snapshot, mid)
                        if f_lv is not None and _value_matches(
                                val, f_lv['value'], t['approx']):
                            claim = _build_level_claim(
                                dict(t, value=val), mid, f_lv, snapshot)
                            fam = 'level'
                    if claim is None:
                        w = win or 'week'
                        kind = 'percent' if t['kind'] == 'percent' else 'pp'
                        tv = val
                        if not signed and direction:
                            tv = val * (1 if direction > 0 else -1)
                        claim = _build_change_claim(
                            dict(t, value=tv), mid, fact, snapshot, w, kind)
                        fam = f'change/{w}'
                if claim is None:
                    claim = _build_level_claim(dict(t, value=val), mid, fact,
                                               snapshot)
                    fam = 'level'
            else:
                tv = val
                if not signed and direction and t['kind'] != 'plain':
                    tv = val * (1 if direction > 0 else -1)
                if (signed or (direction and not level_mark)) and re.search(
                        r'新增|净减少|减少|increase|rose|climbed|up|下降|上升|回落|回升|涨|跌',
                        t['ctx'], re.I):
                    for w in (win, 'week', 'm1'):
                        if not w:
                            continue
                        claim = _build_change_claim(
                            dict(t, value=tv), mid, fact, snapshot, w, 'abs')
                        if claim is not None:
                            fam = f'change/{w}'
                            break
                if claim is None:
                    claim = _build_level_claim(dict(t, value=tv), mid, fact,
                                               snapshot)
                    fam = 'level'
            if claim is None:
                unbound.append({'raw': t['raw'], 'ctx': t['ctx'][:40],
                                'zone_fact': facts_zone,
                                'reason': f'{mid} 无 {win or "level"} 通道'})
                continue
            verd = _verify_claims([claim], snapshot, thresholds)
            v = verd.get(claim['claim_id'], {})
            status = v.get('status', 'NOT_VERIFIABLE')
            if fam.startswith('change') and status == 'VERIFIED' and direction:
                exp = claim['value']
                if (direction > 0 and exp < 0) or (direction < 0 and exp > 0):
                    status = 'CONTRADICTED'
                    v = dict(v, reasons=(v.get('reasons') or []) +
                             [f'direction_word:方向词与{exp:+g}矛盾'])
            if status == 'CONTRADICTED' and \
                    _display_aligned(t['raw'], claim['value'],
                                     v.get('computed'), approx=t['approx']):
                status = 'VERIFIED'
                note_add = '显示位对齐(文本显示位与复算差≤末位半格)'
            else:
                note_add = ''
            checks.append({'family': fam, 'token': t['raw'],
                           'metric': mid, 'value': val,
                           'expected': v.get('computed'),
                           'status': status,
                           'note': ';'.join((v.get('reasons') or [])[-2:])
                           + note_add})
    # 上期引用(锚链+derived 基准值)
    if prior_anchors:
        for clause in _clause_split(text):
            if not re.search(r'上期|前值|上一交易日|prior|上周|前一周|'
                             r'week of', clause, re.I):
                continue
            mids_in = _find_alias(clause)
            if not mids_in:
                continue
            mid = mids_in[0][0]
            fact = _fact_of(snapshot, mid)
            prior_vals = []
            for date, anc in sorted(prior_anchors.items(), reverse=True):
                for f in _anchor_facts(anc):
                    if f.get('metric_id') == mid and _is_num(f.get('value')):
                        prior_vals.append((date, f['value']))
            if fact:
                for w_rec in (fact.get('derived') or {}).values():
                    bv = (w_rec or {}).get('basis_value')
                    if _is_num(bv):
                        prior_vals.append(('derived_basis', bv))
            if not prior_vals:
                continue
            masked = _masked_clause(clause, mids_in)
            for t in _extract_tokens(masked):
                if t['kind'] not in ('plain', 'percent', 'K', 'thousands',
                                     'pp'):
                    continue
                val = t['value']
                if fact:
                    val = _scale_k(val, t['kind'], fact)
                is_cur = fact and _value_matches(val, fact['value'],
                                                 t['approx'])
                if is_cur:
                    continue
                hit = any(_value_matches(val, v, t['approx'])
                          for _, v in prior_vals)
                checks.append({'family': 'prior_reference',
                               'token': t['raw'], 'metric': mid,
                               'value': val,
                               'expected': [v for _, v in prior_vals][:4],
                               'status': 'VERIFIED' if hit
                               else 'CONTRADICTED',
                               'note': f'锚链/基准 {[v for _, v in prior_vals][:4]}'})
                break
    # 叙事-数值方向(后置: 别名免依赖的叙事词 vs 数值事实方向)
    try:
        checks.extend(_check_narrative_direction(text, snapshot) or [])
    except Exception:
        checks.append({'family': 'narrative_direction', 'token': '',
                       'value': None, 'expected': None,
                       'status': 'INSUFFICIENT_EVIDENCE',
                       'note': 'checker_error(检查器异常降级)'})
    # band_label 双报去重提示(T8-R2 遗留②,RDG-20261116-011): 文本值错
    # (level CONTRA)+标签按快照落带(band_label CONTRA)同指标并存时,带
    # 判定与 level 判定同锚——加派生标记供报告层去重渲染;状态零变动
    # (「宁多报不漏报」取向保持,不弱化任一检查)。
    _lvl_contra_mids = {c.get('metric') for c in checks
                        if c.get('family') == 'level'
                        and c.get('status') == 'CONTRADICTED'}
    for c in checks:
        if (c.get('family') == 'band_label'
                and c.get('status') == 'CONTRADICTED'
                and c.get('metric') in _lvl_contra_mids):
            c['co_anchor'] = 'level_contradicted'
            c['note'] = (str(c.get('note') or '') +
                         ';同指标 level 已另报,带判定按快照落带(可去重渲染)')
    # 聚合
    hard = [c for c in checks if c['status'] == 'CONTRADICTED']
    ok = [c for c in checks if c['status'] == 'VERIFIED']
    if hard:
        verdict = 'CONTRADICTED'
    elif ok:
        verdict = 'VERIFIED'
    else:
        verdict = 'INSUFFICIENT_EVIDENCE'
    return {'verdict': verdict, 'checks': checks, 'unbound': unbound,
            'version': TEXT_CONSISTENCY_VERSION,
            'stats': {'checks': len(checks), 'contradicted': len(hard),
                      'verified': len(ok), 'unbound': len(unbound)}}


# ── 渲染复核: render mode ───────────────────────────────────────────

def check_render(body, manifest):
    """body 内数值 token ↔ manifest 登记位对照(禁反扫重建,只对照)。

    manifest: render_hook 输出 {'spans': [(line_no, token_str, value,
    claim_id)], 'disclosure_spans': [...]}。
    """
    reg = {}
    for line_no, tok, value, cid in manifest.get('spans', []):
        reg.setdefault(line_no, []).append((tok, value, cid))
    disc = {}
    for line_no, tok, value, cid in manifest.get('disclosure_spans', []):
        disc.setdefault(line_no, []).append((tok, value, cid))
    problems = []
    lines = body.split('\n')
    for i, line in enumerate(lines):
        in_disc = line.startswith(' ') or line.startswith('-') and \
            any(d in line for d in ('STALE', 'INSUFFICIENT', 'NOT_VERIFIABLE',
                                    'SEMANTIC'))
        mline = _masked_clause(line, _find_alias(line))
        for t in _extract_tokens(mline):
            pool = disc.get(i) if in_disc else reg.get(i)
            hit = any(t['raw'].strip() == tok or
                      _value_matches(t['value'], v if _is_num(v) else None)
                      for tok, v, _ in (pool or []))
            if not hit:
                problems.append({'line': i, 'token': t['raw'],
                                 'kind': 'unregistered_numeric'})
    non_verified = [cid for _, _, _, cid in manifest.get('spans', [])
                    if not str(cid).startswith('CLM-')]
    return {'problems': problems, 'non_verified_manifest_entries':
            non_verified, 'clean': not problems and not non_verified}
