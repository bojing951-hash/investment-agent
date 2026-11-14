# -*- coding: utf-8 -*-
"""确定性断言工厂(六型)— 架构整改阶段三 T4(2026-11-14,PHASE3-PLAN 工单T4)。

契约权威: docs/autonomous-rd/ARCH_REFORM_PHASE2_CONTRACT.md §2(律3 单位代数)
+§3(六型+谓词文法)——设计冲突以契约为准,本模块禁自行发明语义。

六型(level/change/comparison/threshold/threshold_distance/observation_lag)
全部确定性派生自 **Fact 层(snapshot facts)+series_store[T3 macro 通道]+
thresholds 注册表+metric_registry**,零模型调用/零网络/零随机/零环境变量/
零自由文本输入: generate_claims_bundle(snapshot, 两注册表) = 纯函数。

单位代数(律3,对齐 Fact 层既成事实,不另造):
  - pp↔bp = ×100 精确双向;canonical 字符串=Fact 层既成名
    percentage_point/basis_point(不出现 pp/bp 缩写名);
  - percent↔pp 无基准禁换算(禁的是变化量↔水平跨维换算);
  - 「400bp=4.00%」两 token 映射同一 threshold claim(bp 别名+显示形态);
  - 渲染后缀不得反推单位(本模块只产结构值,后缀语义=律8[T6] 面);
  - 跨指标差(spread/diff)同单位校验,异单位拒;
  - 变化双轨跟随 Fact 层(spec §4.4): 价格类→pct_change(relative/percent);
    利率利差类→pp_change+bp_change(absolute/percentage_point+basis_point 别名);
    计数类→abs_change(absolute/原单位)。

谓词文法(§3 逐字): percentile_rank=100×(严格小于+0.5×并列)/n,窗界=前一
年度末观测含当期,min-n 门 n<20→INSUFFICIENT_EVIDENCE,月频 ytd 禁用;
sign_flip_date/last_crossing/crossing_count(序列遍历+min-n 门)/AND 组合。
谓词产出的证据不足态=事实性派生字段(gate),验证状态机=T5职权,本波不产。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
_SCRIPTS_DIR = os.path.dirname(_PKG_DIR)          # scripts/
_ROOT = os.path.dirname(_SCRIPTS_DIR)             # 仓根
for _p in (_SCRIPTS_DIR, _PKG_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fact_engine as fe                            # noqa: E402  单一权威: 单位族
from research_contract import claim_bundle as cb    # noqa: E402

THRESHOLDS_PATH = os.path.join(_ROOT, 'config', 'thresholds.json')

# ── 单位代数(律3) ──────────────────────────────────────────────────
CANONICAL_PP = 'percentage_point'   # Fact 层既成 canonical 名
CANONICAL_BP = 'basis_point'
RATE_UNIT_FAMILY = ('percent', CANONICAL_PP)
_ALGEBRA_DECIMALS = 6               # ×100/÷100 浮点尾噪声归零位


class UnitAlgebraError(ValueError):
    """单位代数违例(跨单位运算/无基准换算/换算值不精确)。"""


# ── 联合统计量(契约§2 statistic 型;T6a 补全) ────────────────────
# 配对口径=correlation_calculator.py 镜像(全价格对日收益率;共同观测日内连接;
# None 跳过/零基双侧联合丢弃/NaN 浮点如实传播——EZU 采集 FAIL 周窗含 NaN→
# 相关=nan 即本镜像语义,与 LIVE correlation_20261114.md 输出一致)。
# 镜像纪律: 两处算法须保持逐句等价;T6 测试用真实冻结档
# correlation_20261114.md 数值(-0.33/-0.41 等)锁定一致性。
STATISTIC_PAIRS = (
    {'a': 'SPX', 'b': 'TLT', 'label': '标普500 vs 20+年国债ETF'},
    {'a': 'SPX', 'b': 'GOLD_F', 'label': '标普500 vs 黄金期货'},
    {'a': 'DXY', 'b': 'SPX', 'label': '美元指数 vs 标普500'},
    {'a': 'DXY', 'b': 'GOLD_F', 'label': '美元指数 vs 黄金期货'},
    {'a': 'WTI_F', 'b': 'TLT', 'label': 'WTI期货 vs 国债ETF'},
    {'a': 'WTI_F', 'b': 'EEM', 'label': 'WTI期货 vs 新兴市场ETF'},
    {'a': 'SPX', 'b': 'EZU', 'label': '标普500 vs 欧元区ETF'},
    {'a': 'SPX', 'b': 'FXI', 'label': '标普500 vs 中国大盘ETF'},
    {'a': 'VIX', 'b': 'HYG', 'label': 'VIX vs 高收益债ETF'},
    {'a': 'BTC', 'b': 'NDX', 'label': '比特币 vs 纳斯达克100'},
    {'a': 'NIKKEI225', 'b': 'USDJPY', 'label': '日经225 vs 美元/日元'},
    {'a': 'DAX', 'b': 'EURUSD', 'label': '德国DAX vs 欧元/美元'},
)
STATISTIC_WINDOWS = (20, 60)
STATISTIC_TOL = 0.005               # 文本 2dp 展示值↔全精度复算容差


def _is_nan(v) -> bool:
    """NaN 判定(float nan;JSON 'NaN' token 解析态)。None≠nan(缺席≠失败)。"""
    return isinstance(v, float) and v != v


def _nan_ledger(scope, mid, where):
    return {'scope': scope, 'metric_id': mid,
            'reason': 'source_value_nan(采集失败,本期值不可知→' + where +
                      '不产数值断言=如实缺席;文本载具体数=对 nan 源伪造)'}


def paired_daily_returns(series_a: dict, series_b: dict):
    """共同观测日日收益率对(镜像 correlation_calculator.paired_returns)。

    纪律: None 观测跳过;前值任一侧==0 丢整对;NaN 浮点**不跳**——如实传播
    (源采集 FAIL 窗→统计量=nan,是可验证事实而非缺席)。
    """
    da = {str(d)[:10]: v for d, v in zip(series_a.get('dates', []),
                                         series_a.get('values', []))}
    db = {str(d)[:10]: v for d, v in zip(series_b.get('dates', []),
                                         series_b.get('values', []))}
    common = sorted(set(da) & set(db))
    if len(common) < 3:
        return None, common
    ra, rb = [], []
    for i in range(1, len(common)):
        a0, a1 = da[common[i - 1]], da[common[i]]
        b0, b1 = db[common[i - 1]], db[common[i]]
        if a0 is None or a1 is None or b0 is None or b1 is None:
            continue
        if a0 == 0 or b0 == 0:
            continue
        ra.append(a1 / a0 - 1.0)
        rb.append(b1 / b0 - 1.0)
    return (ra, rb), common[1:]


def pearson(xs, ys):
    """皮尔逊相关(镜像 correlation_calculator.pearson;n<3 或零方差→None)。

    NaN 传播: 输入含 NaN→输出 NaN(vx<=0 对 NaN 恒 False,与 LIVE 同路);
    调用方须以 math.isnan 判 nan 语义,不得把 NaN 当 None 缺席。
    """
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    return cov / (vx ** 0.5 * vy ** 0.5)


def pp_to_bp(v: float) -> float:
    """percentage_point→basis_point = ×100 精确(尾噪声归零后往返相等)。"""
    r = round(v * 100.0, _ALGEBRA_DECIMALS)
    if round(r / 100.0, _ALGEBRA_DECIMALS) != round(v, _ALGEBRA_DECIMALS):
        raise UnitAlgebraError(f'pp→bp 非精确往返: {v}→{r}')
    return r


def bp_to_pp(v: float) -> float:
    """basis_point→percentage_point = ÷100 精确。"""
    r = round(v / 100.0, _ALGEBRA_DECIMALS)
    if round(r * 100.0, _ALGEBRA_DECIMALS) != round(v, _ALGEBRA_DECIMALS):
        raise UnitAlgebraError(f'bp→pp 非精确往返: {v}→{r}')
    return r


def is_exact_pp_bp_pair(pp: float, bp: float) -> bool:
    """pp/bp 两值是否互为精确换算(错值对=假;工厂别名与校验共用一判)。"""
    try:
        return round(pp, _ALGEBRA_DECIMALS) == bp_to_pp(bp) \
            and pp_to_bp(pp) == round(bp, _ALGEBRA_DECIMALS)
    except UnitAlgebraError:
        return False


def forbid_percent_to_pp(value: float, *, basis: float = None):
    """律3: percent↔pp 无基准禁换算——唯一合法通道=显式给基准(水平重述)。

    相对变化(pct_change,percent)无基准值时**不存在** percentage_point 表述;
    本函数=该禁令的可执行形态: 无 basis 一律抛 UnitAlgebraError。
    """
    if basis is None:
        raise UnitAlgebraError(
            f'percent→pp 无基准禁换算(契约律3): {value!r} 相对变化无基准值,'
            '不存在 pp 维度表述')
    return round(value, _ALGEBRA_DECIMALS)


def bp_alias(unit: str, value: float):
    """为 pp/bp 系 claim 值产 canonical 别名(pp↔bp 精确对);他单位无别名。"""
    if unit == CANONICAL_PP:
        return {CANONICAL_BP: pp_to_bp(value)}
    if unit == CANONICAL_BP:
        return {CANONICAL_PP: bp_to_pp(value)}
    return None


def threshold_token_matches(claim: dict, token_value: float,
                            token_unit: str) -> bool:
    """「400bp=4.00%」两 token 映射同一 threshold claim(契约律3)。

    token 侧单位串: 'basis_point'/'bp'→按 ×100 精确代数折回 pp 对值;
    '%'→裸后缀不携带单位信息(律8),按值+claim 角色数值相等判定
    (OAS「4.00%」=percentage_point 水平的显示形态)。
    """
    if claim.get('claim_type') not in ('threshold', 'threshold_distance'):
        return False
    u = (token_unit or '').strip().lower()
    if u in ('bp', 'basis_point'):
        if claim['unit'] != CANONICAL_PP:
            return False
        return round(bp_to_pp(token_value), _ALGEBRA_DECIMALS) == \
            round(claim['threshold_ref']['value'], _ALGEBRA_DECIMALS)
    if u in ('%', 'percent-sign', 'display-percent'):
        # 裸 % 不反推单位(否定性用法): pp 水平/percent 水平显示形态均为数值同值
        return round(token_value, _ALGEBRA_DECIMALS) == \
            round(claim['threshold_ref']['value'], _ALGEBRA_DECIMALS)
    if u == 'percent':
        return claim['unit'] == 'percent' and \
            round(token_value, _ALGEBRA_DECIMALS) == \
            round(claim['threshold_ref']['value'], _ALGEBRA_DECIMALS)
    return False


# ── 谓词文法(§3 逐字对齐) ─────────────────────────────────────────
MIN_N = 20                          # 契约钉死: n<20→INSUFFICIENT_EVIDENCE
GATE_OK = 'OK'
GATE_INSUFFICIENT = 'INSUFFICIENT_EVIDENCE'


def _side(v: float, level: float = 0.0) -> int:
    return (v > level) - (v < level)


def percentile_rank(values, current=None, *, min_n: int = MIN_N) -> dict:
    """分位公式钉死: 100×(严格小于+0.5×并列)/n(并列半权,含当期自身)。"""
    vals = list(values)
    if not vals:
        return {'predicate': 'percentile_rank', 'error': 'empty_series'}
    x = vals[-1] if current is None else current
    n = len(vals)
    strictly_less = sum(1 for v in vals if v < x)
    ties = sum(1 for v in vals if v == x)
    pct = 100.0 * (strictly_less + 0.5 * ties) / n
    return {
        'predicate': 'percentile_rank',
        'n': n,
        'strictly_less': strictly_less,
        'ties': ties,
        'percentile': round(pct, 4),
        'min_n': min_n,
        'gate': GATE_OK if n >= min_n else GATE_INSUFFICIENT,
        'formula': '100×(严格小于+0.5×并列)/n',
    }


def ytd_percentile(dates, values, *, frequency=None, min_n: int = MIN_N) -> dict:
    """ytd 窗分位: 窗界=前一年度末观测(含当期,与 derived.ytd basis 约定一致)。

    月频 ytd 禁用(契约§3 逐字)→ refused;窗=前一年最后观测(含)→当期(含)。
    """
    if frequency == 'monthly':
        return {'predicate': 'percentile_rank', 'window': 'ytd',
                'refused': 'monthly_ytd_forbidden(契约§3: 月频 ytd 禁用)'}
    ds, vs = list(dates), list(values)
    if not ds:
        return {'predicate': 'percentile_rank', 'window': 'ytd', 'error': 'empty_series'}
    end_d = ds[-1]
    year = int(str(end_d)[:4])
    # 前一年度末观测=最后一个 date < 当年1月1日 的观测(含其自身入窗)
    b = None
    for i in range(len(ds) - 1, -1, -1):
        if str(ds[i])[:4] != str(year) and str(ds[i]) < f'{year}-01-01':
            b = i
            break
    lo = b if b is not None else 0
    window_d, window_v = ds[lo:], vs[lo:]
    r = percentile_rank(window_v, min_n=min_n)
    r.update({
        'window': 'ytd(年内至今)',
        'window_first_date': window_d[0],
        'window_end_date': end_d,
        'current_value': window_v[-1],
    })
    if b is None:
        r['window_note'] = '序列无前一年度观测,窗起点=序列首观测'
    return r


def sign_flip_date(dates, values, *, level: float = 0.0) -> dict:
    """符号翻转日=从末端回扫,最后一个与当期异侧观测的日期。

    契约例: CURVE_2S10S 倒挂→回正,sign_flip_date=2024-09-05(最后负值日,
    即「该日之后无倒挂」);first_current_side_date=首个当期侧观测日。
    """
    ds, vs = list(dates), list(values)
    if not vs:
        return {'predicate': 'sign_flip_date', 'error': 'empty_series'}
    cur = _side(vs[-1], level)
    if cur == 0:
        return {'predicate': 'sign_flip_date', 'level': level,
                'error': 'current_value_at_level(末观测恰在阈值上,无侧可判)'}
    j = None
    for i in range(len(vs) - 1, -1, -1):
        if _side(vs[i], level) not in (0, cur):
            j = i
            break
    if j is None:
        return {'predicate': 'sign_flip_date', 'level': level,
                'sign_flip_date': None,
                'note': '窗内无另一侧观测(全窗同侧或仅零值)'}
    k = j + 1
    while k < len(vs) and _side(vs[k], level) == 0:
        k += 1
    return {
        'predicate': 'sign_flip_date',
        'level': level,
        'sign_flip_date': ds[j],
        'last_opposite_value': vs[j],
        'first_current_side_date': ds[k] if k < len(vs) else None,
        'current_side': 'above' if cur > 0 else 'below',
        'formula': '自末端回扫最后异侧观测;「该日后无翻转」语义',
    }


def last_crossing(dates, values, level: float) -> dict:
    """最后穿越=最末一次严格跨过 level 的相邻观测对(触而不越不算穿越)。

    crossing_date=新侧首个观测日(since 语义=当期关系自该日成立);
    from_date=旧侧最后观测日(契约例「2024-09-05 后无倒挂」的表述锚)。
    """
    ds, vs = list(dates), list(values)
    for i in range(len(vs) - 1, 0, -1):
        a, b = _side(vs[i - 1], level), _side(vs[i], level)
        if a != 0 and b != 0 and a != b:
            return {
                'predicate': 'last_crossing',
                'level': level,
                'crossing_date': ds[i],
                'from_date': ds[i - 1],
                'from_value': vs[i - 1],
                'to_value': vs[i],
                'direction': 'up' if b > 0 else 'down',
                'side_now': 'above' if b > 0 else 'below',
            }
    return {'predicate': 'last_crossing', 'level': level,
            'crossing_date': None,
            'note': '窗内无严格穿越(同侧/触而未越/单侧数据)'}


def crossing_count(dates, values, level: float, *, since: str = None,
                   min_n: int = MIN_N) -> dict:
    """穿越计数=窗内严格跨过 level 的相邻观测对遍历计数(上穿/下穿分列)。

    min-n 门(契约§3): 窗内 n<20→gate=INSUFFICIENT_EVIDENCE(计数仍如实
    产出=事实性派生字段;状态机处置=T5)。
    """
    ds, vs = list(dates), list(values)
    if since is not None:
        idx = [i for i, d in enumerate(ds) if str(d) >= str(since)]
        ds = [ds[i] for i in idx]
        vs = [vs[i] for i in idx]
    n = len(vs)
    up = down = 0
    events = []
    for i in range(1, n):
        a, b = _side(vs[i - 1], level), _side(vs[i], level)
        if a != 0 and b != 0 and a != b:
            if b > 0:
                up += 1
            else:
                down += 1
            events.append({'date': ds[i], 'direction': 'up' if b > 0 else 'down'})
    return {
        'predicate': 'crossing_count',
        'level': level,
        'since': since,
        'n_in_window': n,
        'window_first_date': ds[0] if ds else None,
        'window_last_date': ds[-1] if ds else None,
        'count': up + down,
        'up': up,
        'down': down,
        'events': events,
        'min_n': min_n,
        'gate': GATE_OK if n >= min_n else GATE_INSUFFICIENT,
    }


def and_combine(*components: dict) -> dict:
    """AND 组合(契约§3: 如 Sell America 三条件)——组件须各带 holds 布尔。"""
    for comp in components:
        if not isinstance(comp, dict) or not isinstance(comp.get('holds'), bool) \
                or 'name' not in comp:
            raise ValueError('AND 组件须为 {name,holds,...}(holds 由谓词+比较器产出)')
    holds = all(c['holds'] for c in components)
    return {
        'predicate': 'AND',
        'n_components': len(components),
        'holds': holds,
        'components': list(components),
    }


# ── 注册表装载(指纹随 bundle 入档;内容=仓内注册表,确定性) ──────────

def _sha256_file(path: str) -> str:
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_thresholds(path: str = None) -> dict:
    with open(path or THRESHOLDS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def thresholds_by_metric(thresholds: dict) -> dict:
    by = {}
    for e in thresholds.get('entries', []):
        by.setdefault(e.get('metric_id'), []).append(e)
    return by


def registry_fingerprints(thresholds: dict) -> dict:
    return {
        'thresholds': {
            'sha256': _sha256_file(THRESHOLDS_PATH),
            'status': thresholds.get('status'),
            'signed_at': thresholds.get('signed_at'),
            'n_entries': len(thresholds.get('entries', [])),
        },
        'metric_registry': {
            'sha256': _sha256_file(fe.REGISTRY_PATH),
            'version': fe.load_registry().get('version'),
        },
    }


# ── 确定性配置表(非自由文本输入;逐条带出处) ────────────────────────
# 跨指标对(契约§4 STALE 行:「美日利差=新鲜DFF−滞后74天JP利率」;信用对=
# Fact 层既成 derived_spread HY_IG_DIFF,周报信用利差对)。
COMPARISON_SPECS = (
    {'name': 'us_jp_rate_spread', 'left': 'DFF', 'right': 'JP_POLICY_RATE',
     'subtype': 'spread',
     'provenance': 'PHASE2-CONTRACT §4 STALE 行「美日利差=新鲜DFF−滞后74天JP利率」'},
    {'name': 'hy_ig_oas_spread', 'left': 'HY_OAS', 'right': 'IG_OAS',
     'subtype': 'spread', 'cross_check_metric': 'HY_IG_DIFF',
     'provenance': 'Fact 层既成 derived_spread=HY_IG_DIFF(周报信用利差对)'},
)
# 区间带 fact 对(契约§2 level band 例「3.75–4.00%」;Fed 目标带=target_band 事实对)。
BAND_FACT_SPECS = (
    {'name': 'fed_funds_target_band', 'low': 'DFEDTARL', 'high': 'DFEDTARU',
     'provenance': 'PHASE2-CONTRACT §2 level band 子结构例「3.75–4.00%」'
                   '(Fact 层 target_band 事实对)'},
)
RANK_ASSET_CLASS = 'equity_index'      # 排名族=注册表 asset_class(数据驱动)
RANK_KEY = 'derived.week.pct_change'   # 排名依据=周相对变化(Fact 层既成)


# ── 内部工具 ────────────────────────────────────────────────────────

def _fact_ref(fact: dict, role: str = None) -> dict:
    r = {'ref': fact['fact_id'], 'kind': 'snapshot_fact',
         'value': fact['value'], 'unit': fact['unit'],
         'observation_date': fact['observation_date']}
    if role:
        r['role'] = role
    return r


def _series_shape_ref(metric_id: str, series: dict, role: str = None) -> dict:
    r = {'ref': f'series:{metric_id}', 'kind': 'series_ref',
         'value': len(series['dates']), 'unit': 'observation_count',
         'span': [series['dates'][0], series['dates'][-1]]}
    if role:
        r['role'] = role
    return r


def _basis_ref(metric_id: str, basis_date: str, basis_value, unit: str) -> dict:
    return {'ref': f'{metric_id}@{basis_date}', 'kind': 'series_ref',
            'value': basis_value, 'unit': unit, 'role': 'basis'}


def _claim(claim_type, subtype, metric_id, value, unit, observation_date,
           as_of, evidence_refs, basis, formula, *, metric_ids=None, **extra):
    c = {
        'claim_id': None,            # 装配终段统一编号(确定性序)
        'claim_type': claim_type,
        'subtype': subtype,
        'metric_id': metric_id,
        'metric_ids': metric_ids,
        'value': value,
        'unit': unit,
        'window': extra.pop('window', None),
        'observation_date': observation_date,
        'as_of': as_of,
        'evidence_refs': evidence_refs,
        'threshold_ref': None,
        'attribution': 'deterministic',
        'derivation': {'basis': basis, 'formula': formula},
    }
    c.update(extra)
    return c


# ── 六型构建器(纯函数) ─────────────────────────────────────────────

def build_level_claims(snapshot, thresholds_by, registry) -> tuple:
    claims, ledger = [], []
    for fact in snapshot.get('facts', []):
        if _is_nan(fact['value']):
            ledger.append(_nan_ledger('level', fact['metric_id'], '水平断言'))
            continue
        claims.append(_claim(
            'level', 'point', fact['metric_id'], fact['value'], fact['unit'],
            fact['observation_date'], snapshot['research_as_of'],
            [_fact_ref(fact)], [fact['fact_id']],
            'Fact 层值直读(零改写;快照 fact.value)'))
    facts_by = {f['metric_id']: f for f in snapshot.get('facts', [])}

    # band ①: fact 对(如 Fed 目标带 3.75–4.00)
    for spec in BAND_FACT_SPECS:
        lo_f, hi_f = facts_by.get(spec['low']), facts_by.get(spec['high'])
        if not (lo_f and hi_f):
            continue
        if lo_f['unit'] != hi_f['unit']:
            continue    # 单位不一致=不产(同单位校验同律)
        claims.append(_claim(
            'level', 'band', None, {'low': lo_f['value'], 'high': hi_f['value']},
            lo_f['unit'], max(lo_f['observation_date'], hi_f['observation_date']),
            snapshot['research_as_of'],
            [_fact_ref(lo_f, role='band_low'), _fact_ref(hi_f, role='band_high')],
            [lo_f['fact_id'], hi_f['fact_id']],
            f'带对象两数[{lo_f["value"]},{hi_f["value"]}]({spec["name"]};'
            f'{spec["provenance"]})', metric_ids=[spec['low'], spec['high']],
            band_source='fact_pair'))

    # band ②: 注册表 band_edge 对(同指标一下缘一上缘,如 DXY 100–104)
    for mid, entries in thresholds_by.items():
        if mid not in facts_by:
            continue
        below = [e for e in entries if e.get('direction') == 'below']
        above = [e for e in entries if e.get('direction') == 'above']
        band_edge = [e for e in entries if 'band_edge' in (e.get('level') or [])]
        below = [e for e in below if e in band_edge]
        above = [e for e in above if e in band_edge]
        if len(below) == 1 and len(above) == 1 and \
                below[0]['unit'] == above[0]['unit'] == facts_by[mid]['unit']:
            band_evid = [_fact_ref(facts_by[mid])]
            if mid in snapshot.get('series_store', {}):
                band_evid.append(_series_shape_ref(mid, snapshot['series_store'][mid]))
            claims.append(_claim(
                'level', 'band', mid,
                {'low': below[0]['value'], 'high': above[0]['value']},
                facts_by[mid]['unit'], facts_by[mid]['observation_date'],
                snapshot['research_as_of'],
                band_evid,
                [facts_by[mid]['fact_id'],
                 f'thresholds:{below[0]["stable_key"]}', f'thresholds:{above[0]["stable_key"]}'],
                f'带对象两数[{below[0]["value"]},{above[0]["value"]}]'
                f'(注册表 band_edge 对;契约§2 例「100-104」)',
                metric_ids=[mid],
                threshold_refs=[
                    {'name': below[0]['stable_key'], 'value': below[0]['value'],
                     'unit': below[0]['unit'],
                     'provenance': _threshold_provenance(below[0], snapshot)},
                    {'name': above[0]['stable_key'], 'value': above[0]['value'],
                     'unit': above[0]['unit'],
                     'provenance': _threshold_provenance(above[0], snapshot)}],
                band_source='thresholds_registry'))
    return claims, ledger


def build_change_claims(snapshot, registry) -> tuple:
    """变化双轨直读 Fact 层 derived(禁合成另一轨;律2 必带 window+基准)。"""
    claims, ledger = [], []
    for fact in snapshot.get('facts', []):
        mid = fact['metric_id']
        if _is_nan(fact['value']):
            ledger.append(_nan_ledger('change', mid, '变化断言'))
            continue
        for win in cb.WINDOWS:
            rec = (fact.get('derived') or {}).get(win)
            if not isinstance(rec, dict) or 'basis_date' not in rec:
                continue
            bd, bv = rec['basis_date'], rec.get('basis_value')
            evid = [_fact_ref(fact),
                    _basis_ref(mid, bd, bv, fact['unit'])]
            basis = [fact['fact_id'], f'{mid}@{bd}']
            formula = rec.get('formula', f'{win} 窗变化')
            if 'pct_change' in rec:
                claims.append(_claim(
                    'change', 'relative', mid, rec['pct_change'], 'percent',
                    fact['observation_date'], snapshot['research_as_of'],
                    evid, basis, formula, window=win,
                    basis_date=bd, basis_value=bv))
            if 'pp_change' in rec:
                bp = rec.get('bp_change')
                if bp is not None and not is_exact_pp_bp_pair(rec['pp_change'], bp):
                    raise UnitAlgebraError(
                        f'{mid} {win} pp/bp 非精确对: {rec["pp_change"]} vs {bp}')
                claims.append(_claim(
                    'change', 'absolute', mid, rec['pp_change'], CANONICAL_PP,
                    fact['observation_date'], snapshot['research_as_of'],
                    evid, basis, formula, window=win,
                    basis_date=bd, basis_value=bv,
                    unit_aliases=bp_alias(CANONICAL_PP, rec['pp_change'])))
            if 'abs_change' in rec:
                claims.append(_claim(
                    'change', 'absolute', mid, rec['abs_change'], fact['unit'],
                    fact['observation_date'], snapshot['research_as_of'],
                    evid, basis, formula, window=win,
                    basis_date=bd, basis_value=bv))
    return claims, ledger


def build_comparison_claim(spec, left_fact, right_fact, as_of) -> dict:
    """spread/diff 单对构建(同单位校验;异单位=UnitAlgebraError 拒)。"""
    if left_fact['unit'] != right_fact['unit']:
        raise UnitAlgebraError(
            f'跨指标差同单位校验拒: {left_fact["metric_id"]}({left_fact["unit"]})'
            f' vs {right_fact["metric_id"]}({right_fact["unit"]})')
    val = round(left_fact['value'] - right_fact['value'], _ALGEBRA_DECIMALS)
    evid = [_fact_ref(left_fact, role='left'),
            _fact_ref(right_fact, role='right')]
    basis = [left_fact['fact_id'], right_fact['fact_id']]
    extra = {}
    if spec.get('cross_check_metric'):
        extra['cross_check_note'] = (
            f"与 Fact 层既成 {spec['cross_check_metric']} 对账(见测试断言)")
    return _claim(
        'comparison', spec['subtype'], None, val, left_fact['unit'],
        max(left_fact['observation_date'], right_fact['observation_date']),
        as_of, evid, basis,
        f"{left_fact['value']}−{right_fact['value']}={val} {left_fact['unit']}"
        f"({spec['name']};{spec['provenance']})",
        metric_ids=[left_fact['metric_id'], right_fact['metric_id']],
        comparison_name=spec['name'],
        unit_aliases=bp_alias(left_fact['unit'], val), **extra)


def build_rank_claims(snapshot, registry) -> list:
    """排名族=注册表 asset_class 数据驱动;依据=周 pct_change(Fact 层既成)。"""
    members = []
    for fact in snapshot.get('facts', []):
        m = fe.metric(fact['metric_id'])
        wk = (fact.get('derived') or {}).get('week') or {}
        if m and m.get('asset_class') == RANK_ASSET_CLASS and 'pct_change' in wk \
                and not _is_nan(wk['pct_change']) and not _is_nan(fact['value']):
            members.append((fact, wk['pct_change']))
    if len(members) < 2:
        return []
    members.sort(key=lambda t: (-t[1], t[0]['metric_id']))
    claims = []
    mids = [f['metric_id'] for f, _ in members]
    prev_pct, prev_rank = None, None
    for i, (fact, pct) in enumerate(members, start=1):
        rank = prev_rank if pct == prev_pct else i    # 同值并列同秩
        prev_pct, prev_rank = pct, rank
        claims.append(_claim(
            'comparison', 'rank', None, rank, 'rank_position',
            fact['observation_date'], snapshot['research_as_of'],
            [_fact_ref(f, role='ranked') for f, _ in members],
            [f['fact_id'] for f, _ in members] + [RANK_KEY],
            f'周pct_change 降序第{rank}/{len(members)}'
            f'({fact["metric_id"]}={pct} percent;族=asset_class:{RANK_ASSET_CLASS})',
            metric_ids=list(mids), rank_key=RANK_KEY, window='week',
            rank_of=len(members)))
    return claims


def build_comparison_claims(snapshot, registry) -> tuple:
    claims, ledger = [], []
    facts_by = {f['metric_id']: f for f in snapshot.get('facts', [])}
    for spec in COMPARISON_SPECS:
        lf, rf = facts_by.get(spec['left']), facts_by.get(spec['right'])
        if not (lf and rf):
            ledger.append({'scope': 'comparison', 'name': spec['name'],
                           'reason': 'input_fact_absent(快照缺成员事实=诚实缺席)'})
            continue
        if _is_nan(lf['value']) or _is_nan(rf['value']):
            ledger.append({'scope': 'comparison', 'name': spec['name'],
                           'reason': 'source_value_nan(成员采集失败→配对断言'
                                     '不产=如实缺席)'})
            continue
        claims.append(build_comparison_claim(spec, lf, rf, snapshot['research_as_of']))
    claims.extend(build_rank_claims(snapshot, registry))
    return claims, ledger


def _threshold_provenance(entry, snapshot) -> str:
    return (f"thresholds-registry:{entry['stable_key']}"
            f"@{entry.get('curated_at', 'v1')}(stable key,非行号;"
            f"quote 已锚 {entry.get('provenance', {}).get('doc', 'config/framework.md')})")


def build_threshold_claims(snapshot, thresholds_by, registry) -> tuple:
    """threshold 型: relation+since_date(持续性=last_crossing 谓词派生)。

    指标无注册表条目→不产(诚实缺席入台账,不造阈值);序列缺席→since_date
    =None(如实);序列在→last_crossing/crossing_count 事实入 persistence。
    """
    claims, ledger = [], []
    store = snapshot.get('series_store', {})
    facts_by = {f['metric_id']: f for f in snapshot.get('facts', [])}
    for mid, entries in thresholds_by.items():
        fact = facts_by.get(mid)
        if not fact:
            continue
        if _is_nan(fact['value']):
            ledger.append(_nan_ledger('threshold', mid, '阈值断言'))
            continue
        for e in entries:
            if e['unit'] != fact['unit']:
                # 派生率视图条目分流(T6a 全量快照首跑暴露): scorecard 表
                # (framework §一 通胀/就业维度)与累计增益条目以率/变动口径
                # 表述,正当消费面=评分卡引擎/派生视图,非水平阈值面——显式
                # 入台账(诚实缺席),非静默跳过;无结构标记的真单位违约仍炸。
                view = None
                if '.scorecard.' in e['stable_key']:
                    view = 'scorecard_rate_view'
                elif '_cumulative_gain' in e['stable_key']:
                    view = 'derived_cumulative_view'
                if view:
                    ledger.append({
                        'scope': 'threshold', 'metric_id': mid,
                        'reason': f'{view}(条目单位 {e["unit"]} 属派生率/'
                                  f'累计视图口径,非水平阈值;水平门不消费='
                                  f'诚实缺席,消费面=评分卡引擎[既有])',
                        'stable_key': e['stable_key']})
                    continue
                raise UnitAlgebraError(
                    f'阈值单位({e["unit"]})与指标 canonical 单位({fact["unit"]})'
                    f'不一致: {e["stable_key"]}(注册表单位策略违约,禁静默换算)')
            tv = e['value']
            lv = fact['value']
            relation = 'above' if lv > tv else ('below' if lv < tv else 'at')
            evid = [_fact_ref(fact)]
            persistence = None
            since_date = None
            since_note = None
            if mid in store:
                s = store[mid]
                evid.append(_series_shape_ref(mid, s))
                lc = last_crossing(s['dates'], s['values'], tv)
                cc = crossing_count(s['dates'], s['values'], tv)
                persistence = {'last_crossing': lc, 'crossing_count_full_window': cc}
                if lc.get('crossing_date') and lc['side_now'] == relation:
                    since_date = lc['crossing_date']
                elif not lc.get('crossing_date'):
                    since_date = s['dates'][0]
                    since_note = 'since_limited_by_window(序列全窗同侧,最早仅可追溯至窗首)'
                else:
                    since_note = ('series_end_side_mismatch_fact(序列末端侧与事实水平侧'
                                  '不一致,since 不派生=如实空)')
            else:
                since_note = 'series_absent(序列不在 store,since_date 不可派生=如实空)'
            claims.append(_claim(
                'threshold', 'edge_relation', mid, lv, fact['unit'],
                fact['observation_date'], snapshot['research_as_of'],
                evid, [fact['fact_id'], f'thresholds:{e["stable_key"]}'],
                f'{lv} {fact["unit"]} vs {tv} {e["unit"]}→relation={relation}'
                f'({e["stable_key"]})',
                relation=relation, since_date=since_date, since_note=since_note,
                persistence=persistence,
                threshold_ref={'name': e['stable_key'], 'value': tv,
                               'unit': e['unit'],
                               'provenance': _threshold_provenance(e, snapshot)},
                unit_aliases=bp_alias(fact['unit'], tv)))
    for mid in facts_by:
        if mid not in thresholds_by:
            ledger.append({'scope': 'threshold', 'metric_id': mid,
                           'reason': 'no_threshold_entries(指标在 thresholds 注册表'
                                     '无条目→无 threshold/distance claim=诚实缺席,不造阈值)'})
    return claims, ledger


def build_threshold_distance_claims(snapshot, thresholds_by, registry) -> list:
    claims = []
    facts_by = {f['metric_id']: f for f in snapshot.get('facts', [])}
    for mid, entries in thresholds_by.items():
        fact = facts_by.get(mid)
        if not fact:
            continue
        if _is_nan(fact['value']):
            continue    # 距离断言同 nan 分流(不产;threshold 台账已记该指标)
        for e in entries:
            if e['unit'] != fact['unit']:
                continue    # build_threshold_claims 已抛;此处防御性跳过(不重复抛)
            d = round(abs(fact['value'] - e['value']), _ALGEBRA_DECIMALS)
            side = 'above' if fact['value'] > e['value'] else (
                'below' if fact['value'] < e['value'] else 'at')
            claims.append(_claim(
                'threshold_distance', 'absolute_distance', mid, d, fact['unit'],
                fact['observation_date'], snapshot['research_as_of'],
                [_fact_ref(fact)],
                [fact['fact_id'], f'thresholds:{e["stable_key"]}'],
                f'|{fact["value"]}−{e["value"]}|={d} {fact["unit"]}'
                f'({e["stable_key"]})',
                side=side,
                threshold_ref={'name': e['stable_key'], 'value': e['value'],
                               'unit': e['unit'],
                               'provenance': _threshold_provenance(e, snapshot)},
                unit_aliases=bp_alias(fact['unit'], d)))
    return claims


def build_observation_lag_claims(snapshot, registry) -> list:
    """observation_lag: as_of−observation_date 自然日天数(律4 数据日期分离)。"""
    from datetime import date
    claims = []
    for fact in snapshot.get('facts', []):
        as_of_d = str(fact.get('as_of') or snapshot['research_as_of'])[:10]
        obs_d = str(fact['observation_date'])[:10]
        days = (date.fromisoformat(as_of_d) - date.fromisoformat(obs_d)).days
        claims.append(_claim(
            'observation_lag', 'as_of_minus_observation', fact['metric_id'],
            days, 'calendar_day', obs_d, snapshot['research_as_of'],
            [_fact_ref(fact)], [fact['fact_id']],
            f'as_of({as_of_d})−observation_date({obs_d})={days} 自然日',
            as_of_date=as_of_d))
    return claims


# ── 谓词台账(事实性派生字段;状态机=T5) ─────────────────────────────

def build_predicate_ledger(snapshot, registry) -> list:
    out = []
    for mid, s in sorted(snapshot.get('series_store', {}).items()):
        m = fe.metric(mid)
        freq = (m or {}).get('frequency')
        r = ytd_percentile(s['dates'], s['values'], frequency=freq)
        r['metric_id'] = mid
        out.append(r)
        vals = s['values']
        if any(_side(v, 0.0) > 0 for v in vals) and any(_side(v, 0.0) < 0 for v in vals):
            sf = sign_flip_date(s['dates'], vals)
            sf['metric_id'] = mid
            out.append(sf)
    return out


def build_statistic_claims(snapshot: dict, pairs=None) -> tuple:
    """statistic.correlation 型(契约§2 十型补全,T6a)。

    双成员配对日收益率皮尔逊;窗=STATISTIC_WINDOWS(20/60)。三态如实:
    - 序列缺席任一侧 → 不产 claim,ledger 诚实缺席(通道未闭合);
    - 共同观测<3 → 同上;
    - 窗含 NaN → **产 claim,value=None+nan_reason**(通道闭合但统计量不可
      计算=可验证事实;文本载具体数即对不上→CONTRADICTED,防 V5-012 型伪造)。
    """
    pairs = pairs if pairs is not None else STATISTIC_PAIRS
    store = snapshot.get('series_store', {})
    claims, ledger = [], []
    for p in pairs:
        a, b = p['a'], p['b']
        sa, sb = store.get(a), store.get(b)
        if not sa or not sb:
            ledger.append({'scope': 'statistic', 'metric_ids': [a, b],
                           'reason': f'series_absent({a if not sa else b} 不在 '
                                     f'series_store→配对统计不可产=诚实缺席)'})
            continue
        pair, _common = paired_daily_returns(sa, sb)
        if not pair:
            ledger.append({'scope': 'statistic', 'metric_ids': [a, b],
                           'reason': 'common_observations_lt3(共同观测日不足)'
                                    })
            continue
        ra, rb = pair
        for w in STATISTIC_WINDOWS:
            r = pearson(ra[-w:], rb[-w:])
            evid = [_series_shape_ref(a, sa, role='leg_a'),
                    _series_shape_ref(b, sb, role='leg_b')]
            formula = (f'pearson(日收益率[-{w}:],{a},{b});共同观测日内连接;'
                       f'n={min(w, len(ra))}')
            if r is None:
                ledger.append({'scope': 'statistic', 'metric_ids': [a, b],
                               'reason': f'zero_variance_or_lt3(window={w}d)'
                                         '(零方差/样本不足→统计量不可产)'})
                continue
            nan_reason = None
            value = r
            if isinstance(r, float) and r != r:          # NaN(propagate 语义)
                value, nan_reason = None, 'nan_in_window(窗内源含 NaN→相关' \
                                          '不可计算,如实 None;文本载具体数=伪造)'
            obs_date = str(sa['dates'][-1])[:10]
            claims.append(_claim(
                'statistic', 'correlation', None, value, 'dimensionless',
                obs_date, snapshot['research_as_of'],
                evid, [f'series:{a}', f'series:{b}'], formula,
                metric_ids=[a, b], corr_window_days=w,
                pair_label=p.get('label'),
                nan_reason=nan_reason,
                disclosure=p.get('disclosure', '')))
    return claims, ledger


# ── 总装(纯函数) ───────────────────────────────────────────────────

def generate_claims_bundle(snapshot: dict, *, thresholds: dict = None,
                           registry: dict = None) -> dict:
    """输入(快照+两注册表)→输出(claims bundle)纯函数。

    确定性: 同输入必同输出(零随机/零时钟/零环境);claim_id 按稳定序统一编号。
    """
    thresholds = thresholds if thresholds is not None else load_thresholds()
    if registry is None:
        fe.load_registry(force=False)
    th_by = thresholds_by_metric(thresholds)

    claims = []
    ledger = []
    lvl, lvl_ledger = build_level_claims(snapshot, th_by, registry)
    chg, chg_ledger = build_change_claims(snapshot, registry)
    cmp_, cmp_ledger = build_comparison_claims(snapshot, registry)
    thr, thr_ledger = build_threshold_claims(snapshot, th_by, registry)
    dist = build_threshold_distance_claims(snapshot, th_by, registry)
    lag = build_observation_lag_claims(snapshot, registry)
    stat, stat_ledger = build_statistic_claims(snapshot)
    # 稳定序: 型序固定;型内=构建序(facts 序/注册表序,均为输入确定序)
    claims.extend(lvl + chg + cmp_ + thr + dist + lag + stat)
    ledger.extend(lvl_ledger + chg_ledger + cmp_ledger + thr_ledger
                  + stat_ledger)

    ymd = str(snapshot['target_date'])
    for i, c in enumerate(claims, start=1):
        c['claim_id'] = f'CLM-{ymd}-{i:04d}'

    return cb.make_bundle(
        snapshot_id=snapshot.get('snapshot_id', ''),
        target_date=snapshot['target_date'],
        research_as_of=snapshot['research_as_of'],
        claims=claims,
        coverage_ledger=ledger,
        predicate_ledger=build_predicate_ledger(snapshot, registry),
        registry_fingerprints=registry_fingerprints(thresholds),
    )


def build_from_snapshot_file(path: str, *, thresholds: dict = None) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        snap = json.load(f)
    return generate_claims_bundle(snap, thresholds=thresholds)


# ── CLI(操作者验证用;零模型/零网络) ────────────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description='确定性六型 claims 工厂(架构整改 T4;零模型调用)')
    ap.add_argument('snapshot', help='研究快照 JSON 路径')
    ap.add_argument('--out', default=None,
                    help='bundle 输出目录(默认=快照旁挂同目录)')
    args = ap.parse_args(argv)
    bundle = build_from_snapshot_file(args.snapshot)
    out_dir = args.out or os.path.dirname(os.path.abspath(args.snapshot))
    path = cb.write_bundle(bundle, out_dir)
    print(f'bundle={bundle["bundle_id"]} claims={len(bundle["claims"])} '
          f'→ {path}')
    print('counts:', json.dumps(bundle['counts'], ensure_ascii=False))
    print('coverage_ledger:', len(bundle['coverage_ledger']), '条诚实缺席')
    print('predicate_ledger:', len(bundle['predicate_ledger']), '条')
    return 0


if __name__ == '__main__':
    sys.exit(main())
