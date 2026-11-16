#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F10 独立研究席只读复算脚本(Audit-R1 F10 受测席, 方法自选留痕).

研究问题(逐字): 布伦特原油价格的大幅波动,还会传导到美国长期通胀预期
(10年期盈亏平衡通胀率 BEI_10Y)吗?近年有时油价暴涨、长期通胀预期明显
跟着走高,有时油价暴跌、预期却似乎纹丝不动——这种传导究竟是在减弱、
已被「锚定」,还是本来就时有时无?

数据(只读, 引擎树 ~/investment-agent-dev/data/daily/):
- BRENT_F / WTI_F: research_snapshot_20261112_v2.json series_store(日频)
- BEI_10Y / BEI_5Y: macro_20261112.json data.<id>.series(日频;复审更正: 钉版与运行面同源——旧脚本误用 macro_20261114 致锚点/样本数版本混用,即独立验收 F10-3)

口径自选(全部留痕, 纯 stdlib, 零模型零网络):
M1 对齐: 日期内连接; 日变化对=(连续共同日的 pct 变化, 差分 pp)。
M2 全窗统计: pearson + OLS slope(ΔBEI_pp ~ ΔBRENT_%)。
M3 分年: 逐年 pearson + slope——「减弱?」的频率维度。
M4 60日滚动相关: 负窗/近零窗(|r|<0.1)/高窗(r≥0.3)占比与范围,
   逐月末末值——「时有时无?」的强度维度。
M5 事件研究: 单日 |chg|≥4%/≥6% 涨跌分组: 当日 ΔBEI 与前向
   5/10/20 日累计 ΔBEI(事件日->h 日后的 BEI 累计变化)——不对称性。
M6 月度聚合: 共同日历月内日变化累计(油=复利乘积,BEI=逐日差求和,等价于上月末至本月末的月度变化;复审更正: 旧注『月首末观测』与实现不符,即独立验收 F10-2), 涨/跌 ≥8% 大月分组;
   前段窗(2016-2021) vs 后段窗(2022-2026)大涨月「每10%油价 BEI 响应」
   ——「锚定?」的幅度维度; 2022+ 涨/跌不对称比。
M7 锚定波动检验: BEI_10Y 水平 60日滚动 std 三段均值
   (pre-2019 / 2024+ / 2026)——锚定是否表现为长期预期波动压缩。
M8 稳健性: WTI_F 代 BRENT_F 与 BEI_5Y 代 BEI_10Y 的分年相关。
M9 锚点数字: BEI_10Y 2026 年内 min/max/当前值钉死百分位
   (100×count(v<cur)/n, 与 judgment_contract 同口径);
   BRENT_F 2026 年内 min/max; 2026 年逐月两序列月变化。

诚实边界(如实, 禁编造):
- 相关与 OLS slope 均为统计描述, 相关≠因果(纪律 7)。
- 按统计期对齐, 不代表当时市场信息集(descriptive, 纪律 5)。
- BRENT_F 为主力连续期货(引擎 identity 注记「含展期跳空可能」),
  现货口径或略异。
- BEI_10Y=名义-实际利差, 含通胀风险溢价与 TIPS 流动性溢价,
  非纯预期; 引擎无流动性调整序列, 该分解不可做。
- 布伦特与 BEI 无发布日事件面, 事件研究为统计期口径, 不作
  「当时市场反应」声明(研究模式门: event_study 类声明回避)。
"""
import json
import math
import os
import sys
from collections import OrderedDict, defaultdict

ENGINE = os.path.expanduser('~/investment-agent-dev')
SNAP = os.path.join(ENGINE, 'data/daily/research_snapshot_20261112_v2.json')
MACRO = os.path.join(ENGINE, 'data/daily/macro_20261112.json')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'f10_calc_output.json')


def load_series():
    snap = json.load(open(SNAP))
    macro = json.load(open(MACRO))
    out = {}
    for mid in ('BRENT_F', 'WTI_F'):
        s = snap['series_store'][mid]
        out[mid] = dict(zip(s['dates'], s['values']))
    for mid in ('BEI_10Y', 'BEI_5Y'):
        s = macro['data'][mid]['series']
        out[mid] = dict(zip(s['dates'], s['values']))
    return out


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return float('nan')
    mx = sum(xs) / n
    my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return float('nan')
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def ols_slope(xs, ys):
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return float('nan')
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


def mean(a):
    return sum(a) / len(a) if a else float('nan')


def change_pairs(X, Y):
    """连续共同日的(日期, X_pct_chg, Y_pp_chg)对。"""
    common = sorted(set(X) & set(Y))
    pairs = []
    for a, b in zip(common, common[1:]):
        if None in (X[a], X[b], Y[a], Y[b]):
            continue
        pairs.append((b, (X[b] / X[a] - 1) * 100.0, Y[b] - Y[a]))
    return common, pairs


def main():
    S = load_series()
    R = {'method_note': __doc__}

    # M1/M2: BRENT_F vs BEI_10Y
    common, pairs = change_pairs(S['BRENT_F'], S['BEI_10Y'])
    xs = [p[1] for p in pairs]
    ys = [p[2] for p in pairs]
    R['alignment'] = {
        'n_common_days': len(common), 'first': common[0], 'last': common[-1],
        'n_change_pairs': len(pairs)}
    R['full_window'] = {
        'pearson_dchg': round(pearson(xs, ys), 4),
        'ols_slope_pp_per_pct': round(ols_slope(xs, ys), 5),
        'ols_slope_pp_per_10pct': round(ols_slope(xs, ys) * 10, 4)}

    # M3: 分年
    byyear = defaultdict(list)
    for d, px, py in pairs:
        byyear[d[:4]].append((px, py))
    R['by_year'] = {}
    for y in sorted(byyear):
        arr = byyear[y]
        R['by_year'][y] = {
            'n': len(arr),
            'pearson': round(pearson([a[0] for a in arr],
                                     [a[1] for a in arr]), 4),
            'slope': round(ols_slope([a[0] for a in arr],
                                     [a[1] for a in arr]), 5)}

    # M4: 60日滚动
    W = 60
    rolls = []
    for i in range(W, len(pairs)):
        win = pairs[i - W:i]
        rolls.append((pairs[i][0], pearson([w[1] for w in win],
                                           [w[2] for w in win])))
    n = len(rolls)
    R['rolling60'] = {
        'n_windows': n,
        'share_negative': round(100.0 * sum(1 for _, r in rolls if r < 0) / n, 1),
        'share_abs_lt_0.1': round(100.0 * sum(1 for _, r in rolls
                                              if abs(r) < 0.1) / n, 1),
        'share_ge_0.3': round(100.0 * sum(1 for _, r in rolls if r >= 0.3) / n, 1),
        'min': round(min(r for _, r in rolls), 3),
        'max': round(max(r for _, r in rolls), 3),
        'month_end': {d[:7]: round(r, 2) for d, r in rolls}}

    # M5: 事件研究
    idx = {p[0]: i for i, p in enumerate(pairs)}
    R['events'] = {}
    for TH in (4.0, 6.0):
        ev = {}
        for side, sel in (('up', lambda p: p[1] >= TH),
                          ('down', lambda p: p[1] <= -TH)):
            grp = [p for p in pairs if sel(p)]
            stats = {'n': len(grp), 'sameday_pp': round(mean([p[2] for p in grp]), 4)}
            for h in (5, 10, 20):
                fwd = []
                for p in grp:
                    i = idx[p[0]]
                    if i + h < len(pairs):
                        fwd.append(S['BEI_10Y'][pairs[i + h][0]]
                                   - S['BEI_10Y'][p[0]])  # 真累计: 水平 t+h 减 t(复审更正: 旧实现为两单日变化之差=差分口径)
                stats['fwd_%dd_pp' % h] = round(mean(fwd), 4)
            ev[side] = stats
        R['events']['abs_ge_%.0fpct' % TH] = ev

    # M6: 月度聚合
    bym = OrderedDict()
    for d, bp, ip in pairs:
        bym.setdefault(d[:7], [1.0, 0.0])
        bym[d[:7]][0] *= (1 + bp / 100.0)
        bym[d[:7]][1] += ip
    mm = [(m, (v[0] - 1) * 100.0, v[1]) for m, v in bym.items()]
    R['monthly'] = {'all_months': {m: [round(o, 2), round(i, 3)]
                                   for m, o, i in mm}}
    early_up = [x for x in mm if x[0] < '2022' and x[1] >= 8]
    late_up = [x for x in mm if x[0] >= '2022' and x[1] >= 8]
    late_dn = [x for x in mm if x[0] >= '2022' and x[1] <= -8]
    R['monthly']['big_up_2016_2021'] = {
        'n': len(early_up),
        'mean_oil_pct': round(mean([x[1] for x in early_up]), 1),
        'mean_bei_pp': round(mean([x[2] for x in early_up]), 4),
        'per_10pct_bei_pp': round(mean([x[2] / (x[1] / 10.0)
                                        for x in early_up]), 4)}
    R['monthly']['big_up_2022_2026'] = {
        'n': len(late_up),
        'mean_oil_pct': round(mean([x[1] for x in late_up]), 1),
        'mean_bei_pp': round(mean([x[2] for x in late_up]), 4),
        'per_10pct_bei_pp': round(mean([x[2] / (x[1] / 10.0)
                                        for x in late_up]), 4)}
    R['monthly']['big_down_2022_2026'] = {
        'n': len(late_dn),
        'mean_oil_pct': round(mean([x[1] for x in late_dn]), 1),
        'mean_bei_pp': round(mean([x[2] for x in late_dn]), 4),
        'per_10pct_bei_pp': round(mean([x[2] / (x[1] / 10.0)
                                        for x in late_dn]), 4)}

    # M7: BEI 60日滚动 std(锚定波动检验)
    levels = [(d, S['BEI_10Y'][d]) for d in sorted(S['BEI_10Y'])
              if S['BEI_10Y'][d] is not None]
    stds = []
    for i in range(W, len(levels)):
        win = [v for _, v in levels[i - W:i]]
        m = mean(win)
        stds.append((levels[i][0],
                     math.sqrt(sum((v - m) ** 2 for v in win) / len(win))))
    R['bei_60d_std'] = {
        'pre_2019_mean': round(mean([s for d, s in stds if d < '2019-01-01']), 4),
        'y2024_plus_mean': round(mean([s for d, s in stds
                                       if d >= '2024-01-01']), 4),
        'y2026_mean': round(mean([s for d, s in stds if d >= '2026-01-01']), 4)}

    # M8: 稳健性(WTI 代 BRENT / BEI_5Y 代 BEI_10Y)
    for xname, yname, key in (('WTI_F', 'BEI_10Y', 'robust_wti'),
                              ('BRENT_F', 'BEI_5Y', 'robust_bei5')):
        _, pp = change_pairs(S[xname], S[yname])
        byy = defaultdict(list)
        for d, px, py in pp:
            byy[d[:4]].append((px, py))
        R[key] = {y: round(pearson([a[0] for a in arr],
                                   [a[1] for a in arr]), 4)
                  for y, arr in sorted(byy.items())}

    # M9: 锚点数字
    bei26 = sorted([(d, v) for d, v in S['BEI_10Y'].items()
                    if d.startswith('2026') and v is not None])
    vals = [v for _, v in bei26]
    cur = S['BEI_10Y'][max(S['BEI_10Y'])]
    br26 = sorted([(d, v) for d, v in S['BRENT_F'].items()
                   if d.startswith('2026') and v is not None])
    bh = max(br26, key=lambda t: t[1])
    bl = min(br26, key=lambda t: t[1])
    R['anchors_2026'] = {
        'BEI_10Y': {
            'n': len(bei26),
            'min': min(vals), 'min_date': min(bei26, key=lambda t: t[1])[0],
            'max': max(vals), 'max_date': max(bei26, key=lambda t: t[1])[0],
            'last': cur, 'last_date': max(S['BEI_10Y']),
            'pinned_pct_100_count_lt_cur_over_n': round(
                100.0 * sum(1 for v in vals if v < cur) / len(vals), 1)},
        'BRENT_F': {'max': bh[1], 'max_date': bh[0],
                    'min': bl[1], 'min_date': bl[0],
                    'last': br26[-1][1], 'last_date': br26[-1][0]}}

    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(R, f, ensure_ascii=False, indent=1)
    print('written:', OUT)
    print(json.dumps({k: v for k, v in R.items()
                      if k in ('full_window', 'by_year', 'rolling60',
                               'events', 'monthly', 'bei_60d_std',
                               'anchors_2026')},
                     ensure_ascii=False, indent=1)[:3000])


if __name__ == '__main__':
    main()
