#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""analog_engine — 历史相似结构检索(Charter6 块4, Afin_charter6_methodology §1)。

纯确定性引擎: 输入=序列字典{metric_id:{dates,values}}+注册表,输出=结构化
结果(单dict);零网络零模型,全部数值由本模块机械计算(Afin 硬约束1)。

六维状态向量(月度网格=宏观时钟,月末快照;§1.1):
  growth     UNEMPLOYMENT_level / NFP_3m_chg / INDPRO_yoy / RSAFS_yoy /
             GDP_yoy(季→季末月对齐) / ICSA_4w_avg(周→月末4周均值)
  inflation  CORE_CPI_yoy / CPI_yoy / BEI_10Y_level
  rates      FED_FUNDS·UST_10Y·TIPS_10Y·CURVE_2S10S 的 level+d12m(pp)
  credit     HY_OAS level+d12m / HY_IG_gap(HY−IG月末差) level+d12m
  volatility VIX_level / SPX_rv21(21日已实现波动,月末窗)
  valuation  SPX_CAPE_level / SPX_PE_TTM_level(Charter6-P2 起;序列缺席=
             维度整体缺席如实标注,不以任何推导值填补——泄漏规则6)

变换纪律(§1.1 变换规则,拒绝项不得私自更换):
  - 水平值仅限跨年代天然可比量(利率/利差/失业率/VIX/通胀同比/估值比率);
    价格/指数类水平一律不用(信息经同比/Δ12m/z 进入);
  - 每特征统一 expanding z: z=(x−μ_≤t)/σ_≤t,μ/σ 只用 t≤各自锚点月末观测
    (泄漏规则1: 全样本统计=泄漏);σ=总体标准差(ddof=0),hist 含当期;
  - min_history=36 个月: 不足→该特征在该候选弃用(features_dropped),
    有效维度<4/6→候选整体无效;锚点自身不满足→拒答 insufficient_history,
    不降门槛硬算;
  - 同比须整 12 个月(t 与 t−12 都在网格上),不足→弃用不缩短窗口冒充。

相似度(§1.2): 加权 z 距离 D=sqrt(Σ w_i·(z_i^anchor−z_i^cand)²),求和仅
over双方都有效特征,权重按有效特征重新归一(归一事实随行);报告 D+距离分位
(分位=严格小于该 D 的候选数/(N2−1)×100)。不得更换为分位数映射/DTW/马氏。

检索(§1.3): 锚点=最新完整月(≥80%已启用维度有数据的最后一个月,--anchor
可回放);候选=锚点前全部有效候选月,排除特征窗重叠者(候选月 M≤M0−12,
泄漏规则3);事后演变(§1.5 aftermath)单独计算单独标注,永不进入相似度
(泄漏规则4)。

拒答阈值(§1.6, 勿放宽): N2≥24 正常;8≤N2<24 警示;N2<8 拒答
insufficient_candidates。当前短历史数据下必然拒答=正确行为(§1.6 现状预判)。

巧合判据(§1.7, 机械触发进 warnings): 单维主导(>0.6)/事后分歧(一致率
<0.6,n≥3)/维度缺席(<6)/TOP-1 不分离(与中位差<10%)。
"""
import math

__all__ = ['DIMENSIONS', 'FEATURE_SPECS', 'AFTERMATH_ASSETS', 'run',
           'month_grid', 'feature_grids', 'z_at', 'weighted_distance']

DIMENSIONS = ('growth', 'inflation', 'rates', 'credit', 'volatility',
              'valuation')
DIM_LABELS = {'growth': '增长', 'inflation': '通胀', 'rates': '利率',
              'credit': '信用', 'volatility': '波动', 'valuation': '估值'}

MIN_HISTORY = 36          # expanding z 最小历史月数(§1.1, 勿放宽)
MIN_VALID_DIMS = 4        # 候选有效维度下限(<4/6 → 候选无效)
MIN_CANDIDATES = 8        # N2 拒答阈值(§1.6, 勿放宽)
WARN_CANDIDATES = 24      # 样本不稳警示阈值
FEATURE_WINDOW = 12       # 特征窗月数(重叠排除窗, §1.3)
ANCHOR_COMPLETE_RATIO = 0.8   # 完整月判定(≥80% 已启用维度有数据)
AFTERMATH_HORIZONS = ('1m', '3m', '6m', '12m')
AFTERMATH_ASSETS = ('SPX', 'UST_10Y', 'DXY', 'GOLD_F')

DISCLOSURE = [
    '相似≠因果, 更非预测: TOP-N 是历史状态距离最近的时期, 当时之后的演变只是历史记录',
    '特征为最新修订口径的描述性对齐, 不代表当时市场信息集(research_mode_gate)',
    '距离分位=该候选在全部有效候选中的相对位置, 不是概率',
]
AFTERMATH_LABEL = ('事后(候选锚点后 1/3/6/12 月, 非预测, 不参与相似度)')
REVISION_NOTE = '当时市场所见状态可能与修订后档案值不同'

# (feature_key, dim, metric_ids, transform)
# transform ∈ level|yoy|d12m|chg_3m_mean|mean_4w|rv21|diff_level|diff_d12m
FEATURE_SPECS = [
    ('UNEMPLOYMENT_level', 'growth', ('UNEMPLOYMENT',), 'level'),
    ('NFP_3m_chg', 'growth', ('NFP',), 'chg_3m_mean'),
    ('INDPRO_yoy', 'growth', ('INDPRO',), 'yoy'),
    ('RSAFS_yoy', 'growth', ('RSAFS',), 'yoy'),
    ('GDP_yoy', 'growth', ('US_REAL_GDP',), 'yoy'),        # 季→季末月对齐在网格层
    ('ICSA_4w_avg', 'growth', ('ICSA',), 'mean_4w'),
    ('CORE_CPI_yoy', 'inflation', ('CORE_CPI',), 'yoy'),
    ('CPI_yoy', 'inflation', ('CPI',), 'yoy'),
    ('BEI_10Y_level', 'inflation', ('BEI_10Y',), 'level'),
    ('FED_FUNDS_level', 'rates', ('FED_FUNDS',), 'level'),
    ('FED_FUNDS_d12m', 'rates', ('FED_FUNDS',), 'd12m'),
    ('UST_10Y_level', 'rates', ('UST_10Y',), 'level'),
    ('UST_10Y_d12m', 'rates', ('UST_10Y',), 'd12m'),
    ('TIPS_10Y_level', 'rates', ('TIPS_10Y',), 'level'),
    ('TIPS_10Y_d12m', 'rates', ('TIPS_10Y',), 'd12m'),
    ('CURVE_2S10S_level', 'rates', ('CURVE_2S10S',), 'level'),
    ('CURVE_2S10S_d12m', 'rates', ('CURVE_2S10S',), 'd12m'),
    ('HY_OAS_level', 'credit', ('HY_OAS',), 'level'),
    ('HY_OAS_d12m', 'credit', ('HY_OAS',), 'd12m'),
    ('HY_IG_gap_level', 'credit', ('HY_OAS', 'IG_OAS'), 'diff_level'),
    ('HY_IG_gap_d12m', 'credit', ('HY_OAS', 'IG_OAS'), 'diff_d12m'),
    ('VIX_level', 'volatility', ('VIX',), 'level'),
    ('SPX_rv21', 'volatility', ('SPX',), 'rv21'),
    ('SPX_CAPE_level', 'valuation', ('SPX_CAPE',), 'level'),
    ('SPX_PE_TTM_level', 'valuation', ('SPX_PE_TTM',), 'level'),
]
FEATURE_METRICS = sorted({m for _, _, ms, _ in FEATURE_SPECS for m in ms})
# other 族别名序列(BRENT/GOLD/SILVER/WTI/CNY=X/JPY=X/GBPUSD=X 等)不在
# FEATURE_SPECS/AFTERMATH_ASSETS 任何一处——结构上不可能进计算路径(§0)


# ══ 月算术 ═════════════════════════════════════════════════════════
def _mkey(d):
    return str(d)[:7]


def _m_add(mkey, k):
    y, m = int(mkey[:4]), int(mkey[5:7])
    idx = y * 12 + (m - 1) + k
    return '%04d-%02d' % (idx // 12, idx % 12 + 1)


def _months_between(a, b):
    """b−a 的月数(整月)。"""
    return (int(b[:4]) * 12 + int(b[5:7])) - (int(a[:4]) * 12 + int(a[5:7]))


# ══ 序列→月网格(§1.1 聚合规则) ═══════════════════════════════════
def month_grid(dates, values, mode):
    """按 transform 需求聚合到 YYYY-MM 网格。

    mode: 'last'(月内末值——月/日频 level·yoy·d12m·chg_3m 源网格)
          'mean4'(月末4周均值=≤月末最后4观测的均值, ICSA)
          'quarter'(季→季末月, 值=季内末值, GDP)
    返回 {month_key: value}(升序无关,dict)。"""
    if not dates:
        return {}
    pairs = sorted(zip([str(d)[:10] for d in dates],
                       [float(v) for v in values]))
    if mode == 'mean4':
        # 遍历观测序: 每个观测作为月末界,取其前(含)最后4个的均值
        grid = {}
        buf = []
        last_m = None
        for d, v in pairs:
            mk = _mkey(d)
            if mk != last_m:
                if last_m is not None and len(buf) >= 4:
                    grid[last_m] = sum(buf[-4:]) / 4.0
                last_m = mk
            buf.append(v)
        if last_m is not None and len(buf) >= 4:
            grid[last_m] = sum(buf[-4:]) / 4.0
        return grid
    grid = {}
    if mode == 'quarter':
        for d, v in pairs:
            m = int(d[5:7])
            qm = 3 * ((m - 1) // 3) + 3          # 季末月 3/6/9/12
            mk = '%s-%02d' % (d[:4], qm)
            grid[mk] = v                          # 升序遍历→季内末值自然覆盖
        return grid
    for d, v in pairs:                            # 'last'
        grid[_mkey(d)] = v                        # 升序遍历→月内末值
    return grid


def _rv21_grid(dates, values):
    """SPX 日频→月末 21 日已实现波动率网格(收盘对数差标准差×√252)。

    每月取月内末观测为界,需其前(含)≥22 个日观测构成 21 个对数收益;
    不足→该月无值(不缩窗冒充)。"""
    if len(dates) < 2:
        return {}
    pairs = sorted(zip([str(d)[:10] for d in dates],
                       [float(v) for v in values]))
    grid = {}
    last_m, last_i = None, None
    for i, (d, _v) in enumerate(pairs):
        mk = _mkey(d)
        if mk != last_m:
            if last_i is not None and last_i >= 21:
                rets = [math.log(pairs[j][1] / pairs[j - 1][1])
                        for j in range(last_i - 20, last_i + 1)]
                mu = sum(rets) / len(rets)
                var = sum((r - mu) ** 2 for r in rets) / len(rets)
                grid[last_m] = math.sqrt(var) * math.sqrt(252.0)
            last_m, last_i = mk, i
        last_i = i
    if last_i is not None and last_i >= 21:
        rets = [math.log(pairs[j][1] / pairs[j - 1][1])
                for j in range(last_i - 20, last_i + 1)]
        mu = sum(rets) / len(rets)
        var = sum((r - mu) ** 2 for r in rets) / len(rets)
        grid[last_m] = math.sqrt(var) * math.sqrt(252.0)
    return grid


_GRID_MODE = {
    'ICSA': 'mean4', 'US_REAL_GDP': 'quarter',
}


def _metric_grid(mid, dates, values, m):
    if m.get('frequency') == 'quarterly' or mid == 'US_REAL_GDP':
        return month_grid(dates, values, 'quarter')
    if mid == 'ICSA':
        return month_grid(dates, values, 'mean4')
    return month_grid(dates, values, 'last')


# ══ 特征网格(§1.1 变换) ═══════════════════════════════════════════
def feature_grids(series_map, registry):
    """全部特征的 {feature_key: {month: value}}(按 FEATURE_SPECS 机械推导)。

    序列缺席的特征→键不出现(缺席=缺席);diff 特征两源都须在场。"""
    by_id = (registry or {}).get('by_id') or {}
    grids = {}
    for key, _dim, mids, tr in FEATURE_SPECS:
        srcs = []
        ok = True
        for mid in mids:
            s = (series_map or {}).get(mid)
            if not s or not s.get('dates'):
                ok = False
                break
            srcs.append(_metric_grid(mid, s['dates'], s['values'],
                                     by_id.get(mid) or {}))
        if not ok:
            continue
        g = {}
        if tr == 'level':
            g = dict(srcs[0])
        elif tr in ('yoy', 'd12m'):
            for mk, v in srcs[0].items():
                prev = srcs[0].get(_m_add(mk, -12))
                if prev is None:
                    continue                      # 不足整12个月→弃用(§1.1)
                if tr == 'yoy':
                    if prev == 0:
                        continue
                    g[mk] = (v / prev - 1.0) * 100.0
                else:
                    g[mk] = v - prev
        elif tr == 'chg_3m_mean':
            for mk, v in srcs[0].items():
                need = [_m_add(mk, -k) for k in (1, 2, 3)]
                if any(srcs[0].get(n) is None for n in need):
                    continue
                diffs = [v - srcs[0][need[0]]]
                diffs += [srcs[0][need[i]] - srcs[0][need[i + 1]]
                          for i in range(2)]
                g[mk] = sum(diffs) / 3.0
        elif tr == 'mean_4w':
            g = dict(srcs[0])                     # 聚合已在网格层完成
        elif tr == 'rv21':
            s = series_map[mids[0]]
            g = _rv21_grid(s['dates'], s['values'])
        elif tr in ('diff_level', 'diff_d12m'):
            a, b = srcs[0], srcs[1]
            for mk in a:
                if mk not in b:
                    continue
                d0 = a[mk] - b[mk]
                if tr == 'diff_level':
                    g[mk] = d0
                else:
                    pa, pb = a.get(_m_add(mk, -12)), b.get(_m_add(mk, -12))
                    if pa is None or pb is None:
                        continue
                    g[mk] = d0 - (pa - pb)
        if g:
            grids[key] = g
    return grids


# ══ expanding z(泄漏规则1) ════════════════════════════════════════
def z_at(grid, mkey):
    """特征在 mkey 的 expanding z;hist=≤mkey 全部观测(含当期)。

    返回 (z, hist_n) 或 (None, hist_n);None=不足 MIN_HISTORY 或 σ=0
    (退化序列无信息,弃用不硬算)。"""
    h = sorted(m for m in grid if m <= mkey)
    n = len(h)
    if n < MIN_HISTORY:
        return None, n
    vals = [grid[m] for m in h]
    mu = sum(vals) / n
    var = sum((v - mu) ** 2 for v in vals) / n
    if var <= 0.0:
        return None, n
    return (grid[mkey] - mu) / math.sqrt(var), n


def weighted_distance(zs_a, zs_c, weights_by_feature):
    """加权 z 距离(§1.2): 双方都有效特征求和,权重按有效特征重新归一。

    返回 (D, norm_factor, per_feature_terms);norm_factor=原始权重和
    (归一事实随行);无共同特征→(None, 0.0, {})。"""
    common = [k for k in zs_a if k in zs_c and k in weights_by_feature]
    if not common:
        return None, 0.0, {}
    wsum = sum(weights_by_feature[k] for k in common)
    if wsum <= 0:
        return None, 0.0, {}
    terms = {}
    sq = 0.0
    for k in common:
        w = weights_by_feature[k] / wsum
        gap = zs_a[k] - zs_c[k]
        terms[k] = {'w': w, 'gap': gap, 'w_gap2': w * gap * gap}
        sq += w * gap * gap
    return math.sqrt(sq), wsum, terms


def _dims_valid(zs):
    return len({next(d for k, d, _m, _t in FEATURE_SPECS if k == f)
                for f in zs})


def _refuse(kind, message, hint):
    return {'ok': False, 'data': {}, 'warnings': [], 'error': (kind,
                                                               message, hint)}


# ══ 主入口 ════════════════════════════════════════════════════════
def run(series_map, registry, anchor=None, top=5, weights=None,
        include_aftermath=True, vn_available=False):
    """历史相似结构检索(只读确定性计算)。

    series_map: {metric_id: {'dates':[...], 'values':[...]}}(快照 store ∪
      采集档序列,由调用方装配;引擎不碰文件不碰网络);
    registry: 注册表(fe.load_registry() 形态,须含 by_id);
    anchor: 'YYYY-MM'(回放历史锚点,合法)或 None(=最新完整月);
    top: TOP-N(≥1);weights: {'growth':w,...} 六维非负和=1 或 None(等权);
    include_aftermath: 事后演变块开关(关闭不影响排序——排序与事后严格分离);
    vn_available: 是否存在 _vN 历史版本(research_mode_gate 第三态)。
    """
    # ── 权重(§1.1: 默认六维等权;覆盖仅维度级,六个非负数和为1) ──
    if weights is None:
        wdim = {d: 1.0 / len(DIMENSIONS) for d in DIMENSIONS}
    else:
        bad = (set(weights) != set(DIMENSIONS)
               or any((not isinstance(v, (int, float))
                       or isinstance(v, bool) or v < 0)
                      for v in weights.values())
               or abs(sum(weights.values()) - 1.0) > 1e-6)
        if bad:
            return _refuse('bad_weights',
                           f'权重须为六维(growth,inflation,rates,credit,'
                           f'volatility,valuation)非负数且和为1,收到: {weights}',
                           '--weights g,i,r,c,v,val 顺序给六个非负数,和=1')
        wdim = {d: float(weights[d]) for d in DIMENSIONS}
    if not isinstance(top, int) or isinstance(top, bool) or top < 1:
        return _refuse('bad_top', f'top 须为≥1 整数,收到: {top!r}', None)

    grids = feature_grids(series_map, registry)
    if not grids:
        return _refuse('insufficient_history',
                       '无任何特征序列可用(输入序列为空或全部缺席)',
                       '先运行采集,或检查 series_map 是否包含特征所需指标')

    # 已启用维度=该维度≥1特征在任何月份有值
    dim_of = {k: d for k, d, _m, _t in FEATURE_SPECS}
    spec_keys = [k for k, _d, _m, _t in FEATURE_SPECS if k in grids]
    enabled_dims = sorted({dim_of[k] for k in spec_keys})
    all_months = sorted({m for k in spec_keys for m in grids[k]})

    def _data_dims(m):
        return sum(1 for d in enabled_dims
                   if any(grids[k].get(m) is not None
                          for k in spec_keys if dim_of[k] == d))

    # ── 锚点(§1.3: 最新完整月=≥80%已启用维度有数据的最后一个月) ──
    if anchor is not None:
        if not (isinstance(anchor, str) and len(anchor) == 7
                and anchor[4] == '-' and anchor[:4].isdigit()
                and anchor[5:7].isdigit()
                and 1 <= int(anchor[5:7]) <= 12):
            return _refuse('bad_anchor', f'anchor 须为 YYYY-MM(01-12月),'
                           f'收到: {anchor!r}',
                           '如 --anchor 2026-09')
        m0 = anchor
        if m0 not in all_months or _data_dims(m0) < 2:
            return _refuse('anchor_not_complete',
                           f'锚点 {m0} 无有效数据(<2 维度在场)',
                           '换 --anchor,或不带该参数用最新完整月')
    else:
        m0 = None
        for m in reversed(all_months):
            if _data_dims(m) >= max(2, math.ceil(
                    ANCHOR_COMPLETE_RATIO * len(enabled_dims))):
                m0 = m
                break
        if m0 is None:
            return _refuse('anchor_not_complete',
                           '无完整月(任何月份已启用维度数据覆盖均<80%)',
                           '检查序列覆盖,或 --anchor 显式回放')

    # ── 锚点特征 z(泄漏规则2: 只用 t≤锚点月末) ──
    zs_anchor = {}
    hist_n = {}
    dropped_anchor = {}
    for k in spec_keys:
        if grids[k].get(m0) is None:
            continue
        z, n = z_at(grids[k], m0)
        if z is None:
            dropped_anchor[k] = ('hist_%d<%d' % (n, MIN_HISTORY)
                                 if n < MIN_HISTORY else 'sigma_0')
        else:
            zs_anchor[k] = z
            hist_n[k] = n
    valid_dims_anchor = _dims_valid(zs_anchor)
    if valid_dims_anchor < 2:
        return _refuse('insufficient_history',
                       f'锚点 {m0} 有效维度 {valid_dims_anchor}<2'
                       f'(expanding z 需 {MIN_HISTORY} 个月历史;弃用特征: '
                       f'{sorted(dropped_anchor) or spec_keys})',
                       '扩展采集窗至≥%d 个月后重试(现状短历史下拒答=正确行为,'
                       '勿降门槛硬算)' % MIN_HISTORY)

    # ── 候选扫描(§1.3: 排除特征窗重叠 M≤M0−12, 泄漏规则3) ──
    cutoff = _m_add(m0, -FEATURE_WINDOW)
    cand_months, dropped_overlap, dropped_insufficient = [], 0, 0
    for m in all_months:
        if not any(grids[k].get(m) is not None for k in spec_keys):
            continue
        if m > cutoff:
            dropped_overlap += 1
            continue
        zs_c = {}
        for k in spec_keys:
            if grids[k].get(m) is None:
                continue
            z, _n = z_at(grids[k], m)
            if z is not None:
                zs_c[k] = z
        if _dims_valid(zs_c) >= MIN_VALID_DIMS:
            cand_months.append((m, zs_c))
        else:
            dropped_insufficient += 1
    n2 = len(cand_months)
    if n2 < MIN_CANDIDATES:
        return _refuse('insufficient_candidates',
                       f'有效候选 {n2} 个(<{MIN_CANDIDATES}, "最相似"无统计'
                       '意义,宁缺毋滥)',
                       f'扩展采集窗(候选需各自 {MIN_HISTORY} 个月 z 历史+'
                       f'与锚点窗不重叠),当前 scanned={len(all_months)} 月')

    # ── 权重展开到特征级(§1.1: 每特征 w=维度权/该维特征数;特征数=规格表
    #    全定义数,与数据在场与否无关——权重确定透明零调参;某特征在具体
    #    候选上缺席由距离层的重归一吸收,缺席事实经 features_dropped 随行)──
    n_spec_per_dim = {d: sum(1 for _k, dd, _m, _t in FEATURE_SPECS if dd == d)
                      for d in DIMENSIONS}
    feat_w = {}
    for k, d in dim_of.items():
        if n_spec_per_dim[d]:
            feat_w[k] = wdim[d] / n_spec_per_dim[d]

    # ── 距离+分位(§1.2) ──
    dists = []
    for m, zs_c in cand_months:
        d_val, wsum, terms = weighted_distance(zs_anchor, zs_c, feat_w)
        if d_val is None:
            continue
        dists.append({'month': m, 'D': d_val, 'terms': terms})
    dists.sort(key=lambda x: (x['D'], x['month']))
    ds = [x['D'] for x in dists]
    for i, x in enumerate(dists):
        x['pct'] = (sum(1 for d0 in ds if d0 < x['D']) / (len(ds) - 1)
                    * 100.0) if len(ds) > 1 else 0.0

    warnings = []
    if n2 < WARN_CANDIDATES:
        warnings.append(f'候选仅 {n2} 个(<{WARN_CANDIDATES}), '
                        '相似排名与分位不稳, 结论弱')
    if len(dists) < MIN_CANDIDATES:
        warnings.append(f'共同特征距离可算候选仅 {len(dists)} 个——分位不稳')

    # ── 维度贡献(§1.5 dims) ──
    topn = dists[:top]
    for x in topn:
        contrib = {}
        for d in DIMENSIONS:
            w2 = sum(t['w_gap2'] for k, t in x['terms'].items()
                     if dim_of[k] == d)
            contrib[d] = {'contribution_share': (w2 / (x['D'] ** 2))
                          if x['D'] > 0 else 0.0,
                          'z_gap': math.sqrt(w2) if w2 > 0 else 0.0}
        x['dims'] = contrib
        x['features_detail'] = {k: {'anchor_z': zs_anchor[k],
                                    'cand_z': (next(
                                        zz for mm, zz in cand_months
                                        if mm == x['month'])).get(k),
                                    'gap': t['gap']}
                                for k, t in x['terms'].items()}

    # ── 巧合判据(§1.7 机械 flag) ──
    for x in topn:
        dom = max(x['dims'].items(), key=lambda kv: kv[1]['contribution_share'])
        if dom[1]['contribution_share'] > 0.6:
            warnings.append(
                f"{x['month']}: 相似性由单一维度主导, 跨维度结构印证弱, "
                f"巧合可能性高({DIM_LABELS[dom[0]]} contribution_share="
                f"{dom[1]['contribution_share']:.2f})")
    if len(dists) >= 3:
        d1, dmed = dists[0]['D'], dists[len(dists) // 2]['D']
        if dmed > 0 and (dmed - d1) / dmed < 0.10:
            warnings.append('TOP-1 未与候选分布分离, '
                            '"最相似"表述降级为"处于相似簇"')
    if valid_dims_anchor < len(DIMENSIONS):
        warnings.append('未覆盖维度可能是共同驱动(缺变量), 相似性解释力受限')

    # ── 锚点状态向量(§1.5) ──
    sv = {}
    for d in DIMENSIONS:
        ks = [k for k, dd, _m, _t in FEATURE_SPECS if dd == d]
        feats = {}
        for k in ks:
            if k in zs_anchor:
                feats[k] = {'value': grids[k][m0], 'z': zs_anchor[k],
                            'hist_n': hist_n[k]}
        cov = (len(feats) / len(ks)) if ks else 0.0
        node = {'features': feats, 'coverage': round(cov, 4)}
        if cov == 0.0:
            node['note'] = f'无{DIM_LABELS[d]}数据, 维度缺席(如实)'
            if d == 'valuation':
                node['note'] = '无估值数据, 维度缺席(如实)'
        sv[d] = node
        if 0.0 < cov < 0.5:
            warnings.append(f'锚点维度 {DIM_LABELS[d]}({d}) 覆盖率 '
                            f'{cov:.2f}(<0.5), 该维特征部分弃用')

    # ── research_mode_gate(§1.4 规则5, 继承 compare 语义) ──
    by_id = (registry or {}).get('by_id') or {}
    feat_mids = sorted({m for k, _d, ms, _t in FEATURE_SPECS
                        if k in zs_anchor for m in ms})
    release_known = [bool(by_id.get(m, {}).get('release_date_available'))
                     for m in feat_mids]
    rmg = {
        'descriptive': 'available',
        'event_study': ('available' if (release_known and all(release_known))
                        else 'blocked: 存在无发布日特征指标(月度宏观发布日'
                             '不可得), 不得按发布日对齐/不得声称事件研究'),
        'realtime_info_set': ('available(经 select_snapshot 点时取版)'
                              if vn_available
                              else 'blocked: 无历史版本, 修订值≠当时值'),
        'note': REVISION_NOTE,
    }

    # ── aftermath(§1.5/泄漏规则4: 独立块,不参与排序) ──
    aftermath_blocks = {}
    if include_aftermath:
        for x in topn:
            blk = {'label': AFTERMATH_LABEL,
                   'unavailable_horizons': {}}   # 按资产各自如实(非全局清单)
            for a in AFTERMATH_ASSETS:
                s = (series_map or {}).get(a)
                horizons = {}
                unavail = []
                if s and s.get('dates'):
                    pairs = sorted(zip([str(d)[:10] for d in s['dates']],
                                       [float(v) for v in s['values']]))
                    # 起点严格用 t>候选锚点月末的首个观测(泄漏规则4:
                    # 事后窗不得回吸锚点月内数据)——月末界=次月首日
                    next_first = _m_add(x['month'], 1) + '-01'
                    i0 = next((i for i, (d0, _v) in enumerate(pairs)
                               if d0 >= next_first), None)
                    if i0 is None:
                        horizons = {h: None for h in AFTERMATH_HORIZONS}
                        unavail = list(AFTERMATH_HORIZONS)
                    else:
                        for h in AFTERMATH_HORIZONS:
                            k = int(h[:-1])
                            end = _m_add(x['month'], k) + '-31'
                            idx = [i for i, (d0, _v) in enumerate(pairs)
                                   if d0 <= end]
                            i_end = idx[-1] if idx else -1
                            if i_end <= i0:
                                # 无窗内末观测(或仅起点自身)→该 horizon
                                # unavailable: 不以缩短窗/0值冒充"无变动"
                                horizons[h] = None
                                unavail.append(h)
                                continue
                            v0, v1 = pairs[i0][1], pairs[i_end][1]
                            unit = (by_id.get(a) or {}).get('unit', '')
                            is_rate = _is_rate(unit)
                            horizons[h] = round(
                                (v1 - v0) if is_rate
                                else (v1 / v0 - 1.0) * 100.0, 6)
                else:
                    horizons = {h: None for h in AFTERMATH_HORIZONS}
                    unavail = list(AFTERMATH_HORIZONS)
                blk[a] = horizons
                blk[a + '_unit'] = 'pp' if _is_rate(
                    (by_id.get(a) or {}).get('unit', '')) else 'pct'
                blk['unavailable_horizons'][a] = sorted(set(unavail))
            aftermath_blocks[x['month']] = blk
        # 分歧判据(§1.7-2)
        for a in AFTERMATH_ASSETS:
            for h in AFTERMATH_HORIZONS:
                vals = [aftermath_blocks[x['month']][a][h]
                        for x in topn if x['month'] in aftermath_blocks]
                vals = [v for v in vals if v is not None]
                if len(vals) >= 3:
                    npos = sum(1 for v in vals if v > 0)
                    agree = max(npos, len(vals) - npos) / len(vals)
                    if agree < 0.6:
                        warnings.append(
                            f'{a} {h}: 相似期事后走向分歧, 提示结局依赖相似期'
                            '之外的条件, 不支持确定性路径推演'
                            f'(方向一致率 {agree:.2f})')

    # ── dispersion(§1.5) ──
    dispersion = {'topN_aftermath_sign_agreement': {}}
    for a in AFTERMATH_ASSETS:
        for h in AFTERMATH_HORIZONS:
            vals = [aftermath_blocks[x['month']][a][h]
                    for x in topn if x['month'] in aftermath_blocks]
            vals = [v for v in vals if v is not None]
            if vals:
                npos = sum(1 for v in vals if v > 0)
                dispersion['topN_aftermath_sign_agreement'][f'{a}_{h}'] = round(
                    max(npos, len(vals) - npos) / len(vals), 4)

    data = {
        'anchor_month': m0,
        'feature_window_months': FEATURE_WINDOW,
        'state_vector': sv,
        'normalization': {'method': 'expanding z (t≤各自锚点月末; '
                                    'μ/σ=含当期历史均值/总体标准差σ)',
                          'min_history_months': MIN_HISTORY},
        'weights': {d: round(wdim[d], 6) for d in DIMENSIONS},
        'candidates': {'scanned': len(all_months), 'valid': n2,
                       'dropped_overlap': dropped_overlap,
                       'dropped_insufficient': dropped_insufficient},
        'top': [{'rank': i + 1, 'candidate_month': x['month'],
                 'distance': round(x['D'], 6),
                 'distance_percentile': round(x['pct'], 4),
                 'dims': {d: {'contribution_share': round(v['contribution_share'], 6),
                              'z_gap': round(v['z_gap'], 6)}
                          for d, v in x['dims'].items()},
                 'features_detail': x['features_detail'],
                 'aftermath': aftermath_blocks.get(x['month'])}
                for i, x in enumerate(topn)],
        'dispersion': dispersion,
        'research_mode_gate': rmg,
        'disclosure': list(DISCLOSURE),
        'features_dropped_at_anchor': dropped_anchor,
    }
    return {'ok': True, 'data': data, 'warnings': warnings, 'error': None}


def _is_rate(unit):
    try:
        import fact_engine as fe
        return unit in fe.RATE_UNITS
    except Exception:  # noqa: BLE001 —— 引擎常量不可用时按注册表单位名兜底
        return unit in ('percent', 'pct', 'pp', 'ratio_point')
