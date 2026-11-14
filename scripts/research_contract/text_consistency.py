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

纯度: stdlib+research_contract 只读;零模型/零网络/零随机/零时钟。
"""
import json
import math
import re

from research_contract import claim_factory as cf
from research_contract import claim_verifier as cv

TEXT_CONSISTENCY_VERSION = 'tc-v1'

# ── 指标别名表(绑定优先级=模式特异性降序;别名冲突取最长匹配) ──────
ALIASES = {
    'UST_30Y': ['30Y UST', '30年期美债', '30Y'],
    'UST_10Y': ['10Y UST', '10年期美债', '10Y', '10年期'],
    'UST_5Y': ['5Y UST', '5年期美债'],
    'UST_2Y': ['2Y UST', '2年期美债', '2Y'],
    'CURVE_2S10S': ['2s10s', '2s10s期限利差', '期限利差'],
    'HY_OAS': ['HY OAS', 'HY_OAS', '高收益债OAS', '高收益债利差'],
    'CCC_OAS': ['CCC OAS', 'CCC_OAS', 'CCC级OAS'],
    'IG_OAS': ['IG OAS', '投资级OAS'],
    'BB_OAS': ['BB OAS', 'BB级OAS'],
    'B_OAS': ['B级OAS'],
    'REAL_10Y': ['10Y实际利率', '10年期实际利率', '实际利率'],
    'TIPS_10Y': ['TIPS_10Y', '10年期TIPS'],
    'BEI_10Y': ['BEI', '通胀预期'],
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
    'MARGIN_BAL': ['两融余额', '两融'],
    'SB_FLOW': ['南向净流入', '南向资金', '南向'],
    'SH_AMOUNT': ['沪市成交额'],
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
                      r'|L\d{2,3}|\d+日|\d{4}-\d{2}-\d{2}')
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
    re.compile(r'\d{1,2}月(\d{1,2}日?)?'),          # 10月/10月CPI
    re.compile(r'第\s*\d+\s*周'),                    # 连续第5周
    re.compile(r'\d{1,2}日(?=相关|-?day)'),           # 20日/60日相关
    re.compile(r'\d{1,2}-?day'),
    re.compile(r'(?:19|20)\d{2}年'),                  # 年份
    # 数值区间端点(85-100/100-104/4.5-4.8):双侧 1-3 位数字+可选小数;
    # (?<![\d.]) 挡 ISO 日期片段(2026-11),(?![\d-]) 挡区间右缘续数字
    re.compile(r'(?<![\d.])(?:\d{1,3}(?:\.\d+)?)\s?[–—-]\s?'
               r'(?:\d{1,3}(?:\.\d+)?)(?![\d-])'),
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


def _window_of(clause, token):
    """窗口词→derived 键(环比=m1/同比=m12/周=week;默认 None=水平)。"""
    ctx = token['ctx']
    if re.search(r'环比|mom|环比下降|环比上升', ctx, re.I):
        return 'm1'
    if re.search(r'in\s+(?:January|February|March|April|May|June|July|'
                 r'August|September|October|November|December)', ctx, re.I):
        return 'm1'
    if re.search(r'同比|yoy', ctx, re.I):
        return 'm12'
    if re.search(r'w/w|wow', ctx, re.I):
        return 'week'
    if re.search(r'周|week|weekly', ctx, re.I) and \
            not re.search(r'上周|前一周|prior week|上一周', ctx, re.I):
        return 'week'
    return None


_PRIOR_MARK_RE = re.compile(
    r'上期|前期|前值|上月|prior|previous|上一交易日|上周|前一周|from',
    re.I)


def _prior_role(clause, token):
    """上期/前值角色标记(位置式: 标记须在 token 之前方算前值;
    「from X」的 X 在标记后=前值,「to X from Y」的 X 非前值)。"""
    for m in _PRIOR_MARK_RE.finditer(clause):
        if m.end() <= token['start'] + 1 and \
                token['start'] - m.end() <= 28:
            return 'prior'
    return None


def _direction_of(clause):
    neg = re.search(r'回落|下跌|下行|走低|下降|降至|降到|净减少|跌|fell|'
                    r'falling|decline|dropped|edged down|down \d', clause, re.I)
    pos = re.search(r'回升|上涨|上行|走高|上升|升至|净增加|涨|rose|rising|'
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

def _mcl_is_distance(mcl, t, snapshot, thresholds_by, gpos=None):
    """token 在遮蔽域中为「|level−阈值|」距离值(距…警告线X 形态)则真。"""
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
    mids = _find_alias(mcl)
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
    mcl = _masked_clause(clause, _find_alias(clause))
    for word, _kw in THRESHOLD_KIND_WORDS:
        for m in re.finditer(re.escape(word), clause):
            seg = clause[m.end():m.end() + 40]
            for t in _extract_tokens(seg):
                if t['kind'] in ('percent', 'pp'):
                    # 距标记后缀跳过(…仅0.80pp)
                    before = seg[:t['start']]
                    if re.search(r'(距|距离|缓冲|仅|余)[^0-9]{0,4}$', before):
                        continue      # 距离值非常量复述
                    tv = t['value']
                    hit = any(
                        abs(e['value'] - tv) <= 0.005 + 1e-9
                        for mid, es in thresholds_by.items() for e in es
                        if e['unit'] in ('percent', cf.CANONICAL_PP))
                    if not hit and _mcl_is_distance(
                            mcl, t, snapshot, thresholds_by,
                            gpos=m.end() + t['start']):
                        continue      # 距离值复述(距400bp警告线0.80形态)
                    checks.append({
                        'family': 'threshold_constant', 'token': t['raw'],
                        'value': tv, 'expected_group': 'thresholds-registry',
                        'status': 'VERIFIED' if hit else 'CONTRADICTED',
                        'note': f'{word}{t["raw"]} vs 注册表常量'})
    return checks


def _check_distance(clause, snapshot, thresholds_by):
    """距离/距…缓冲: |level−threshold|≈token(pp/bp/index)。"""
    checks = []
    m = re.search(r'(距离?|缓冲)[^0-9+\-−]{0,12}', clause)
    if not m:
        return checks
    mids = _find_alias(clause)
    mid = mids[0][0] if mids else _CTX_STATE.get('carry_mid')
    if not mid:
        return checks
    fact = _fact_of(snapshot, mid)
    if not fact or not _is_num(fact['value']):
        return checks
    reg_vals = [e['value'] for es in thresholds_by.values() for e in es]
    mcl = _masked_clause(clause, _find_alias(clause))
    toks = [t for t in _extract_tokens(mcl)
            if t['kind'] in ('percent', 'pp', 'plain')]
    # 阈值常量 token = 与任一注册表常量同值者(400bp=4.00/104/5.0)
    tv = None
    for t in toks:
        if any(abs(t['value'] - rv) <= 0.005 + 1e-9 for rv in reg_vals):
            tv = t['value']
            break
    # 距离 token = 距 标记之后、非常量、非水平本身的第一个候选
    # (m.start 对齐: mcl 与 clause 等长,遮蔽不位移)
    dt = None
    for t in toks:
        if t['start'] < m.start() or \
                (tv is not None and abs(t['value'] - tv) <= 0.005 + 1e-9) or \
                abs(t['value'] - fact['value']) <= 0.01:
            continue
        dt = t
        break
    if dt is None:
        return checks
    if tv is None:
        # 无常量 token: 取使 |fact−rv| 与距离 token 最相符的注册表阈值
        best = None
        for rv in reg_vals:
            miss = abs(abs(fact['value'] - rv) - dt['value'])
            if best is None or miss < best[0]:
                best = (miss, rv)
        if best is None or best[0] > 0.005 + 1e-9:
            return checks
        tv = best[1]
    exp = abs(fact['value'] - tv)
    ok = _value_matches(dt['value'], round(exp, 4), dt['approx']) or \
        _display_aligned(dt['raw'], dt['value'], exp)
    checks.append({'family': 'threshold_distance', 'token': dt['raw'],
                   'value': dt['value'], 'expected': round(exp, 4),
                   'status': 'VERIFIED' if ok else 'CONTRADICTED',
                   'note': f'|{fact["value"]}−{tv}|={exp:.4g}'})
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
    if len(mids) < 2:
        return []
    a, b = mids[0][0], mids[1][0]
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
    """可加性: 总变化=贡献A+贡献B / 名义=实际+BEI 恒等式。"""
    checks = []
    # 形态一: X+Y(贡献)与总token
    contribs = []
    for m in re.finditer(r'(贡献|加总|构成|分解)', clause):
        seg = clause[max(0, m.start() - 60):m.start()]
        for t in _extract_tokens(seg)[-2:]:
            if t['kind'] == 'pp':
                contribs.append(t)
    if len(contribs) >= 2:
        total_tok = None
        for m in re.finditer(r'(分解|构成|加总)', clause):
            seg_after = clause[m.end():m.end() + 30]
            for t in _extract_tokens(seg_after):
                if t['kind'] == 'pp':
                    total_tok = t
                    break
        if total_tok is None:
            # 总=句首第一个 pp(名义端)
            toks = [t for t in _extract_tokens(clause) if t['kind'] == 'pp']
            if toks:
                total_tok = toks[0]
        if total_tok:
            s = round(sum(t['value'] for t in contribs[:2]), 4)
            ok = _value_matches(round(total_tok['value'], 4), s)
            checks.append({'family': 'additivity', 'token': total_tok['raw'],
                           'value': total_tok['value'], 'expected': s,
                           'status': 'VERIFIED' if ok else 'CONTRADICTED',
                           'note': f'贡献和={s:g} vs 总{total_tok["raw"]}'})
    # 形态二: A与B加总构成 C(水平恒等式)
    m = re.search(r'加总构成|恒等', clause)
    if m:
        mids = _find_alias(clause)
        if len(mids) >= 3:
            vals = []
            for mid, s, e in mids[:3]:
                f = _fact_of(snapshot, mid)
                vals.append((mid, f['value'] if f else None))
            nums = [t for t in _extract_tokens(clause)
                    if t['kind'] in ('percent', 'pp')]
            if len(vals) == 3 and len(nums) >= 3 and \
                    all(_is_num(v) for _, v in vals):
                a, b, c = [v for _, v in vals]
                ok = abs((a + b) - c) <= 0.005 + 1e-9 and \
                    _value_matches(nums[0]['value'], a) and \
                    _value_matches(nums[1]['value'], b) and \
                    _value_matches(nums[2]['value'], c)
                checks.append({'family': 'additivity_identity',
                               'token': '/'.join(n['raw'] for n in nums[:3]),
                               'value': [n['value'] for n in nums[:3]],
                               'expected': [a, b, c],
                               'status': 'VERIFIED' if ok else 'CONTRADICTED',
                               'note': f'{a}+{b}={"✓" if abs(a+b-c)<=0.005 else "✗"}{c}'})
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
    if not mids:
        return []
    mid = mids[0][0]
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


# ── 主检: migration mode ────────────────────────────────────────────

SPECIAL_CHECKERS = [
    _check_threshold_constant, _check_distance, _check_corr, _check_rank,
    _check_spread, _check_additivity, _check_consecutive,
    _check_compound_count, _check_band_relation, _check_prior_reverse,
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
    checks = []
    unbound = []
    facts_zone = bool(_FACT_ZONE_RE.search(text))
    owned_ctx = re.compile(
        r'相关|距离|距警告|警告线|恐慌线|红线|强势阈值|警戒线|正常线上限|'
        r'连续第|周收于|利差|贡献|反推|加总构成|已满足|中性区间|区间上沿|'
        r'区间下沿|带下沿|带上沿|关口|站上')
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
        for fn in SPECIAL_CHECKERS:
            try:
                for ch in fn(clause, snapshot, thresholds_by) or []:
                    checks.append(ch)
            except Exception:      # 检查器异常不吞主流程;记录后继续
                checks.append({'family': getattr(fn, '__name__', '?'),
                               'token': '', 'value': None, 'expected': None,
                               'status': 'INSUFFICIENT_EVIDENCE',
                               'note': 'checker_error(检查器异常降级)'})
        masked = _masked_clause(clause, mids_in)
        for t in _extract_tokens(masked):
            seg_start = clause.rfind('，', 0, t['start']) + 1
            seg_end_i = clause.find('，', t['end'])
            seg_scoped = clause[seg_start:seg_end_i if seg_end_i > 0
                                else len(clause)]
            if owned_ctx.search(seg_scoped):
                continue            # 语义族检查器辖域(同逗号段)
            t = dict(t, ctx=clause[max(0, t['start'] - 24):t['end'] + 24])
            mid, best_d = None, 1e9
            for m2, s0, e0 in mids_in:
                d = 0 if (t['start'] < e0 and t['end'] > s0 - 4) else \
                    min(abs(t['start'] - e0), abs(s0 - t['end']))
                if d < best_d:
                    mid, best_d = m2, d
            if mid is None and carry_mid is not None and (
                    (t['kind'] in ('percent', 'pp')
                     and (_window_of(clause, t) or _direction_of(clause)))
                    or (t['kind'] in ('亿', 'plain', 'K', 'thousands')
                        and re.search(r'净减少|净增加|新增|减少|增加',
                                      t['ctx']))):
                mid = carry_mid          # 承前句指标(环比下降0.10%/净减少X 形态)
            if mid is None or (mids_in and best_d > 34):
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
            if _prior_role(clause, t):
                continue            # 前值/上期=prior_reference 辖域
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
            elif t['kind'] in ('percent', 'pp'):
                if (signed or win or direction) and not level_mark:
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
