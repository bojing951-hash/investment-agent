# -*- coding: utf-8 -*-
# r60_analog.py — ⑧ 历史相似结构表独立复算(本席按引擎文档化方法自写实现, 不导入/不调用引擎)
#                + Y 记号覆盖闭合点(前轮记号审计中未被已录点覆盖的数字逐个直算)
# 用法: /usr/bin/python3 -I r60_analog.py <RUN_DIR> <SNAPSHOT_JSON> <OUT_JSON>
import sys, os, json, re, math, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r00_common import *

RUN, SNAP, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sn = Snap(load(SNAP))
rep = load(os.path.join(RUN, 'report.json'))
aj = load(os.path.join(RUN, 'agent_judgment.json'))
PTS, EX = [], {}
CAT = ['']


def cat(c):
    CAT[0] = c


def P(pid, where, key, comp, rep_, note='', tol=None):
    disp = round(comp, 6) if isinstance(comp, float) else comp
    ok = same(comp, rep_, tol)
    PTS.append({'id': pid, 'cat': CAT[0], 'where': where, 'key': key, 'computed': disp,
                'reported': rep_, 'ok': bool(ok), 'note': note})
    print('%s|%s|%s|comp=%s|rep=%s|%s|%s' % ('OK' if ok else 'XX', pid, CAT[0], disp, rep_, where, note))
    return ok


def pick(d, *names, **kw):
    default = kw.get('default', None)
    for n in names:
        if isinstance(d, dict) and n in d:
            return d[n]
    return default


# ======================= ⑧ 历史相似结构表独立复算 =======================
cat('AN 历史相似结构表独立复算')
DIMS = ('growth', 'inflation', 'rates', 'credit', 'volatility', 'valuation')
SPECS = [
    ('UNEMPLOYMENT_level', 'growth', ('UNEMPLOYMENT',), 'level'),
    ('NFP_3m_chg', 'growth', ('NFP',), 'chg_3m_mean'),
    ('INDPRO_yoy', 'growth', ('INDPRO',), 'yoy'),
    ('RSAFS_yoy', 'growth', ('RSAFS',), 'yoy'),
    ('GDP_yoy', 'growth', ('US_REAL_GDP',), 'yoy'),
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
DIM_OF = {k: d for k, d, _m, _t in SPECS}
N_SPEC = {d: sum(1 for _k, dd, _m, _t in SPECS if dd == d) for d in DIMS}
MIN_HIST, MIN_DIMS, FEAT_WIN, CLUSTER = 36, 4, 12, 12


def madd(m, k):
    y, mo = int(m[:4]), int(m[5:7])
    idx = y * 12 + (mo - 1) + k
    return '%04d-%02d' % (idx // 12, idx % 12 + 1)


def mb(a, b):
    return (int(b[:4]) * 12 + int(b[5:7])) - (int(a[:4]) * 12 + int(a[5:7]))


def g_last(pairs):
    return {d.strftime('%Y-%m'): v for d, v in sorted(pairs)}


def g_mean4(pairs):
    g, buf, last = {}, [], None
    for d, v in sorted(pairs):
        mk = d.strftime('%Y-%m')
        if mk != last:
            if last is not None and len(buf) >= 4:
                g[last] = sum(buf[-4:]) / 4.0
            last = mk
        buf.append(v)
    if last is not None and len(buf) >= 4:
        g[last] = sum(buf[-4:]) / 4.0
    return g


def g_quarter(pairs):
    g = {}
    for d, v in sorted(pairs):
        g['%04d-%02d' % (d.year, 3 * ((d.month - 1) // 3) + 3)] = v
    return g


def g_rv21(pairs):
    pairs = sorted(pairs)
    g, st = {}, {'last_m': None, 'last_i': None}

    def put():
        i = st['last_i']
        rets = [math.log(pairs[j][1] / pairs[j - 1][1]) for j in range(i - 20, i + 1)]
        mu = sum(rets) / len(rets)
        g[st['last_m']] = math.sqrt(sum((x - mu) ** 2 for x in rets) / len(rets)) * math.sqrt(252.0)
    for i, (d, v) in enumerate(pairs):
        mk = d.strftime('%Y-%m')
        if mk != st['last_m']:
            if st['last_i'] is not None and st['last_i'] >= 21:
                put()
            st['last_m'], st['last_i'] = mk, i
        st['last_i'] = i
    if st['last_i'] is not None and st['last_i'] >= 21:
        put()
    return g


def metric_grid(mid):
    if not sn.has(mid):
        return None
    s = sn.series(mid)
    if not s:
        return None
    if mid == 'US_REAL_GDP':
        return g_quarter(s)
    if mid == 'ICSA':
        return g_mean4(s)
    return g_last(s)


GRIDS = {}
for key, dim, mids, tr in SPECS:
    srcs = [metric_grid(m) for m in mids]
    if any(s is None for s in srcs):
        continue
    g = {}
    if tr == 'level' or tr == 'mean_4w':
        g = dict(srcs[0])
    elif tr in ('yoy', 'd12m'):
        for mk, v in srcs[0].items():
            prev = srcs[0].get(madd(mk, -12))
            if prev is None or (tr == 'yoy' and prev == 0):
                continue
            g[mk] = (v / prev - 1.0) * 100.0 if tr == 'yoy' else v - prev
    elif tr == 'chg_3m_mean':
        for mk, v in srcs[0].items():
            need = [madd(mk, -k) for k in (1, 2, 3)]
            if any(srcs[0].get(n) is None for n in need):
                continue
            g[mk] = (v - srcs[0][need[2]]) / 3.0
    elif tr == 'rv21':
        g = g_rv21(sn.series(mids[0]))
    elif tr in ('diff_level', 'diff_d12m'):
        a, b = srcs[0], srcs[1]
        for mk in a:
            if mk not in b:
                continue
            d0 = a[mk] - b[mk]
            if tr == 'diff_level':
                g[mk] = d0
            else:
                pa, pb = a.get(madd(mk, -12)), b.get(madd(mk, -12))
                if pa is None or pb is None:
                    continue
                g[mk] = d0 - (pa - pb)
    if g:
        GRIDS[key] = g


def z_at(g, mk):
    ks = sorted(g)
    step = 1
    if len(ks) >= 2:
        gaps = sorted(mb(ks[i - 1], ks[i]) for i in range(1, len(ks)))
        step = max(1, gaps[len(gaps) // 2])
    req = max(1, int(math.ceil(MIN_HIST / float(step))))
    h = [m for m in ks if m <= mk]
    n = len(h)
    if n < req:
        return None, n, req
    vals = [g[m] for m in h]
    mu = sum(vals) / n
    var = sum((v - mu) ** 2 for v in vals) / n
    if var <= 0.0:
        return None, n, req
    return (g[mk] - mu) / math.sqrt(var), n, req


spec_keys = [k for k, _d, _m, _t in SPECS if k in GRIDS]
enabled = sorted({DIM_OF[k] for k in spec_keys})
all_months = sorted({m for k in spec_keys for m in GRIDS[k]})


def data_dims(m):
    return sum(1 for d in enabled if any(GRIDS[k].get(m) is not None for k in spec_keys if DIM_OF[k] == d))


m0 = None
for m in reversed(all_months):
    if data_dims(m) >= max(2, math.ceil(0.8 * len(enabled))):
        m0 = m
        break
zs_a, hn, dropped = {}, {}, {}
for k in spec_keys:
    g = GRIDS[k]
    if g.get(m0) is None:
        dropped[k] = 'no_value_at_anchor'
        continue
    z, n, req = z_at(g, m0)
    if z is None:
        dropped[k] = 'hist_%d<%d' % (n, req)
    else:
        zs_a[k], hn[k] = z, n
U = sorted(zs_a)
cutoff = madd(m0, -FEAT_WIN)
cands, n_over, n_ins = [], 0, 0
for m in all_months:
    if m > cutoff:
        n_over += 1
        continue
    zc, miss = {}, {}
    for k in U:
        if GRIDS[k].get(m) is None:
            miss[k] = 'no_value'
            continue
        z, n, req = z_at(GRIDS[k], m)
        if z is None:
            miss[k] = 'hist<36'
        else:
            zc[k] = z
    if len({DIM_OF[k] for k in zc}) >= MIN_DIMS:
        cands.append((m, zc, miss))
    else:
        n_ins += 1
feat_w = {k: (1.0 / 6.0) / N_SPEC[DIM_OF[k]] for k in DIM_OF}
W_U = sum(feat_w[k] for k in U)
dists = []
for m, zc, miss in cands:
    sq, per = 0.0, {d: 0.0 for d in DIMS}
    for k in U:
        if k in zc:
            t = (feat_w[k] / W_U) * (zs_a[k] - zc[k]) ** 2
            sq += t
            per[DIM_OF[k]] += t
    dists.append({'month': m, 'D': math.sqrt(sq), 'missing': miss, 'per': per})
dists.sort(key=lambda x: (len(x['missing']), x['D'], x['month']))
ds = [x['D'] for x in dists]
for x in dists:
    x['pct'] = (sum(1 for d0 in ds if d0 < x['D']) / (len(ds) - 1) * 100.0) if len(ds) > 1 else 0.0
reps = []
for x in dists:
    owner = next((r for r in reps if mb(min(r['month'], x['month']), max(r['month'], x['month'])) < CLUSTER), None)
    if owner is None:
        x['cluster'] = [x['month']]
        reps.append(x)
    else:
        owner['cluster'].append(x['month'])
EX['analog_rep_dropped_at_anchor'] = dropped
EX['analog_rep_sorted_head'] = [(x['month'], round(x['D'], 6), len(x['missing']), round(x['pct'], 2), sorted(x['missing'])) for x in dists[:14]]
EX['analog_rep_cluster_sizes'] = [len(r['cluster']) for r in reps]
EX['analog_rep_first_last_candidate'] = [min(c[0] for c in cands), max(c[0] for c in cands)]
print('DROPPED@anchor', dropped)
print('HEAD', json.dumps(EX['analog_rep_sorted_head'], ensure_ascii=False))
print('CLUSTERS', EX['analog_rep_cluster_sizes'], 'first/last cand', EX['analog_rep_first_last_candidate'])

s6 = next(s for s in rep['steps'] if 'analog' in str(s.get('step', '')))['envelope']['data']
print('S6 keys', sorted(s6.keys()))
ck = pick(s6, 'candidates', 'candidate_counts', 'counts', default={})
print('candidates keys', sorted(ck.keys()) if isinstance(ck, dict) else type(ck))
fs = pick(s6, 'feature_set', default={})
print('feature_set keys', sorted(fs.keys()) if isinstance(fs, dict) else type(fs))
print('top[0] keys', sorted(s6['top'][0].keys()))
print('state_vector keys', sorted(s6['state_vector'].keys()), '| growth keys', sorted(list(s6['state_vector'].values())[0].keys()))
if s6['top'][0].get('dims'):
    print('top[0].dims', json.dumps(s6['top'][0]['dims'], ensure_ascii=False)[:600])
P('AN01', '引擎面 scanned(特征网格出现过的月份总数)', '本席复算 len(all_months)', len(all_months), pick(ck, 'scanned'))
P('AN02', '引擎面 valid(有效候选月数: 不与锚点 12 个月特征窗重叠且 U 内有效维度≥4)', '本席复算 len(cands)', len(cands), pick(ck, 'valid'))
P('AN03', '引擎面 dropped_overlap', '本席复算', n_over, pick(ck, 'dropped_overlap'))
P('AN04', '引擎面 dropped_insufficient', '本席复算', n_ins, pick(ck, 'dropped_insufficient'))
P('AN05', '锚点准入特征集 U(13 特征)与引擎 feature_set 逐一相同', '本席复算 U', ','.join(U), ','.join(sorted(pick(fs, 'features', 'admitted', default=[]))))
P('AN06', '统一分母 W_U(锚点准入特征权重和)', '本席复算 Σ (1/6)/维内特征数', W_U, pick(fs, 'wsum', 'W_U', 'w_total'), tol=1e-6)
P('AN07', '锚点月(最新完整月)与引擎一致', '本席复算 m0', m0, pick(s6, 'anchor_month', 'anchor'))
svf = {}
for d, blk in s6['state_vector'].items():
    for f, rec in pick(blk, 'features', default={}).items():
        svf[f] = rec
n = 0
for k in U:
    n += 1
    rr = svf.get(k, {})
    P('AN%02d' % (10 + 2 * n - 1), '锚点状态向量 %s 原始值' % k, 'series_store 月网格(月内末值/派生) @%s' % m0, GRIDS[k].get(m0), pick(rr, 'value'), tol=1e-9)
    P('AN%02d' % (10 + 2 * n), '锚点状态向量 %s expanding z(史≤锚点月末, 总体σ, 含当期)' % k, '本席复算 z', zs_a[k], pick(rr, 'z'), tol=1e-9, note='hist_n 本席 %s / 引擎 %s' % (hn[k], pick(rr, 'hist_n', 'n')))
base = 10 + 2 * len(U)
for j, r in enumerate(reps[:5]):
    t = s6['top'][j]
    b = base + 14 * j
    cm = pick(t, 'candidate_month', 'month')
    P('A%02d' % (b + 1), '相似结构表第 %d 行候选月' % (j + 1), '本席复算(排序=缺席数,距离,月份; <12 月同簇去重取首)', r['month'], cm)
    P('A%02d' % (b + 2), '相似结构表第 %d 行距离' % (j + 1), '本席复算 D=sqrt(Σ(w/W_U)·gap²)', r['D'], pick(t, 'distance', 'D'), tol=1e-6)
    P('A%02d' % (b + 3), '相似结构表第 %d 行缺席特征数' % (j + 1), '本席复算', len(r['missing']), pick(t, 'n_missing', 'missing'))
    P('A%02d' % (b + 4), '相似结构表第 %d 行距离分位' % (j + 1), '本席复算 严格小于该D的候选数/(N−1)×100', r['pct'], pick(t, 'distance_percentile', 'percentile', 'pct'), tol=1e-3)
    P('A%02d' % (b + 5), '相似结构表第 %d 行簇成员数' % (j + 1), '本席复算', len(r['cluster']), len(pick(t, 'cluster_members', 'cluster', default=[])))
    td = pick(t, 'dims', default={})
    for q, dname in enumerate(DIMS):
        mine = r['per'][dname] / (r['D'] ** 2) if r['D'] else 0.0
        theirs = pick(td.get(dname, {}), 'contribution_share', 'share', 'contrib')
        P('A%02d' % (b + 6 + q), '相似结构表第 %d 行 %s 维贡献份额' % (j + 1, dname), '本席复算 Σ(w/W_U)gap²[维]/D²', mine, theirs, tol=1e-5)
    EX['analog_top%d_missing' % (j + 1)] = sorted(r['missing'])
for i, fn in enumerate(('report.md', 'FULL_REPORT.md')):
    rows = re.findall(r'^\|\s*(\d+)\s*\|\s*(\d{4}-\d{2})\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|', open(os.path.join(RUN, fn), encoding='utf-8').read(), flags=re.M)
    for j, t in enumerate(s6['top']):
        rk = (j < len(rows) and int(rows[j][0]) == pick(t, 'rank', default=j + 1) and rows[j][1] == pick(t, 'candidate_month', 'month')
              and abs(float(rows[j][2]) - pick(t, 'distance')) <= 5e-7 and abs(float(rows[j][3]) - pick(t, 'distance_percentile')) <= 5e-5)
        P('A%02d' % (base + 70 + i * 5 + j), '%s 相似结构表第 %d 行(名次|候选月|距离|距离分位) = 引擎面 S6 top[%d]' % (fn, j + 1, j),
          '渲染表行 %s' % ('|'.join(rows[j]) if j < len(rows) else '缺行'), rk, True,
          note='引擎面 %s|%s|%.6f|%.4f; 渲染共 %d 行' % (pick(t, 'rank', default=j + 1), pick(t, 'candidate_month', 'month'), pick(t, 'distance'), pick(t, 'distance_percentile'), len(rows)))

# ======================= Y 记号覆盖闭合 =======================
cat('Y 记号覆盖闭合')
ea = {d.strftime('%Y-%m'): v for d, v in sn.series('EA_HICP_YOY')}
rowsx = [(m, v, yoy(sn, 'CPI', m + '-01')) for m, v in sorted(ea.items())]
gt = [m for m, v, c in rowsx if c is not None and v > c]
prev_gt = [m for m in gt if m < '2026-09']
EX['ea_gt_us_months'] = gt
P('Y01', 'C1「为 2023-09 以来首个高于美国的可比月份」', 'series_store EA_HICP_YOY 与 CPI 同比逐月比较: 2026-09 之前最后一个 EA>US 月', prev_gt[-1], '2023-09')
P('Y02', 'C1「2022-07 至 2023-09 曾持续高于美国」(连续 15 个月)', '2022-07..2023-09 内 EA>US 月数', sum(1 for m in gt if '2022-07' <= m <= '2023-09'), 15)
P('Y03', 'C1 同句隐含: 2023-10 至 2026-08 无 EA>US 月份', '2023-10..2026-08 内 EA>US 月数', sum(1 for m in gt if '2023-10' <= m <= '2026-08'), 0)
EX['ea_minus_us_2026_09'] = ea.get('2026-09') - sn.val('CPI', '2026-09-01') if sn.val('CPI', '2026-09-01') is not None else None
cpid = dict((d.strftime('%Y-%m'), v) for d, v in sn.series('CPI'))
P('Y04', 'C1「2025-10 为序列库缺采」(美国 CPI 同比基期缺席)', 'series_store.CPI 2025-10 在场性(0=缺采)', (1 if '2025-10' in cpid else 0), 0, note='相邻月 2025-09=%s 2025-11=%s' % (cpid.get('2025-09'), cpid.get('2025-11')))
cc = dict((d.strftime('%Y-%m'), v) for d, v in sn.series('CORE_CPI'))
P('Y05', '核心 CPI 2026-10 同比同样缺上年同月基期', 'series_store.CORE_CPI 2025-10 在场性(0=缺采)', (1 if '2025-10' in cc else 0), 0)
jp = [(d.strftime('%Y-%m'), v) for d, v in sn.series('JP_POLICY_RATE')]
jpm = dict(jp)
flat = ['2026-02', '2026-03', '2026-04', '2026-05', '2026-08']
P('Y06', 'C3「2026-02 至 2026-05 与 2026-08 的相邻月均差均不超过 0.001」', 'series_store.JP_POLICY_RATE 各月与前一月之差最大绝对值', max(abs(jpm[m] - jpm[madd(m, -1)]) for m in flat), 0.001, tol=1e-12, note='逐月差=%s' % ['%s:%+.1fbp' % (m, diff_bp(jpm[madd(m, -1)], jpm[m])) for m in flat])
order = [m for m, v in jp if '2025-11' <= m <= '2026-10']
steps = [(order[i], diff_bp(jpm[order[i - 1]], jpm[order[i]])) for i in range(1, len(order))]
P('Y07', 'C3「已见台阶均不小于 0.066」', '政策窗内正台阶最小值(bp)/100', min(s for m, s in steps if s > 1) / 100.0, 0.066, tol=1e-12)
P('Y08', 'C3 带宽「1.197 至 1.257(两位小数显示约 1.20 至 1.26)」', '1.227∓0.03 及两位小数', '%.3f/%.3f→%.2f/%.2f' % (jpm['2026-10'] - 0.03, jpm['2026-10'] + 0.03, jpm['2026-10'] - 0.03, jpm['2026-10'] + 0.03), '1.197/1.257→1.20/1.26')
P('Y09', 'C3「本次 2026-10 月均 1.227 较目标水平 1.25 低 0.023」', '1.25 − series_store.JP_POLICY_RATE 2026-10', round(1.25 - jpm['2026-10'], 3), 0.023, tol=1e-12)
P('Y10', '传导环1「12 个月窗(2025-11-19→2026-11-19)」窗启日', '2026-11-19 减 12 个月', add_months(dt.date(2026, 11, 19), -12).isoformat(), '2025-11-19')
P('Y11', '传导环1 BEI_10Y 12 个月窗窗启值 2.27', sn.key('BEI_10Y', '2025-11-19'), sn.val('BEI_10Y', '2025-11-19'), 2.27)
P('Y12', '传导环1「12 个月窗变动 -11bp」', 'series_store.BEI_10Y 2025-11-19→2026-11-19', diff_bp(sn.val('BEI_10Y', '2025-11-19'), sn.val('BEI_10Y', '2026-11-19')), -11.0)
P('Y13', '传导环1 BEI_10Y 三个月窗窗启值 2.30(2026-08-19)', sn.key('BEI_10Y', '2026-08-19'), sn.val('BEI_10Y', '2026-08-19'), 2.30)
P('Y14', '传导环1 BEI_10Y 最新值 2.16(2026-11-19)', sn.key('BEI_10Y', '2026-11-19'), sn.val('BEI_10Y', '2026-11-19'), 2.16)
P('Y15', '传导环1「三个月窗变动 -14bp」', 'series_store.BEI_10Y 2026-08-19→2026-11-19', diff_bp(sn.val('BEI_10Y', '2026-08-19'), sn.val('BEI_10Y', '2026-11-19')), -14.0)
P('Y16', '传导环1「更早的通胀上行段 BEI_10Y 自 2026-02-27 的 2.25」', sn.key('BEI_10Y', '2026-02-27'), sn.val('BEI_10Y', '2026-02-27'), 2.25)
P('Y17', '传导环1「升至 2026-05-04 的 2.50」', sn.key('BEI_10Y', '2026-05-04'), sn.val('BEI_10Y', '2026-05-04'), 2.50)
w = sn.win('BEI_10Y', dt.date(2026, 2, 1), dt.date(2026, 5, 31))
EX['bei_feb_may'] = {'first': [w[0][0].isoformat(), w[0][1]], 'last': [w[-1][0].isoformat(), w[-1][1]],
                     'min': [min(w, key=lambda x: x[1])[0].isoformat(), min(x[1] for x in w)], 'max': [max(w, key=lambda x: x[1])[0].isoformat(), max(x[1] for x in w)],
                     'endpoint_chg_bp': diff_bp(w[0][1], w[-1][1])}
print('BEI feb-may', EX['bei_feb_may'])
P('Y18', '传导环1 BEI_10Y 近一月窗启值 2.35(2026-10-20)', sn.key('BEI_10Y', '2026-10-20'), sn.val('BEI_10Y', '2026-10-20'), 2.35)
P('Y19', '传导环1/C1 竞争解释「近一月共同交易日窗(2026-10-20→2026-11-19)变动 -19bp」', 'series_store.BEI_10Y 2026-10-20→2026-11-19', diff_bp(sn.val('BEI_10Y', '2026-10-20'), sn.val('BEI_10Y', '2026-11-19')), -19.0)
P('Y20', '传导环1「布伦特 2026-08-19 报 91.62」', sn.key('BRENT_F', '2026-08-19'), sn.val('BRENT_F', '2026-08-19'), 91.62)
P('Y21', '传导环1「先升至 2026-10-23 的 116.72」', sn.key('BRENT_F', '2026-10-23'), sn.val('BRENT_F', '2026-10-23'), 116.72)
P('Y22', '传导环1「较窗启 +27.40%」', 'BRENT_F 2026-08-19→2026-10-23', pct(sn.val('BRENT_F', '2026-08-19'), sn.val('BRENT_F', '2026-10-23')), 27.40)
P('Y23', '传导环2「美国十年期名义利率 2026-11-19 报 5.04%」', sn.key('UST_10Y', '2026-11-19'), sn.val('UST_10Y', '2026-11-19'), 5.04)
P('Y24', '传导环2 TIPS_10Y 近一月窗启值 2.77(2026-10-20)', sn.key('TIPS_10Y', '2026-10-20'), sn.val('TIPS_10Y', '2026-10-20'), 2.77)
P('Y25', '传导环2 TIPS_10Y 2026-10-23 值 2.66', sn.key('TIPS_10Y', '2026-10-23'), sn.val('TIPS_10Y', '2026-10-23'), 2.66)
P('Y26', '传导环2 TIPS_10Y 最新值 2.88(2026-11-19)', sn.key('TIPS_10Y', '2026-11-19'), sn.val('TIPS_10Y', '2026-11-19'), 2.88)
P('Y27', 'M1 环3「USDJPY 当前报 159.35」(2026-11-23)', sn.key('USDJPY', '2026-11-23'), round(sn.val('USDJPY', '2026-11-23'), 2), 159.35)
P('Y28', 'M1 环3 USDJPY 三个月窗窗启值 159.55(2026-08-19)', sn.key('USDJPY', '2026-08-19'), round(sn.val('USDJPY', '2026-08-19'), 2), 159.55)
P('Y29', 'M1 环3「近一月(2026-10-23→2026-11-23)不降反升 1.82%」', 'series_store.USDJPY 2026-10-23→2026-11-23', pct(sn.val('USDJPY', '2026-10-23'), sn.val('USDJPY', '2026-11-23')), 1.82)
P('Y30', 'M1 环3「三个月 2026-08-19→2026-11-23 为 -0.13%」', 'series_store.USDJPY 2026-08-19→2026-11-23', pct(sn.val('USDJPY', '2026-08-19'), sn.val('USDJPY', '2026-11-23')), -0.13)
P('Y31', 'M1 环3「按 3 个月前锚 2026-08-23 的最近观测 2026-08-21 起算为 +0.29%」', 'series_store.USDJPY ≤2026-08-23 最近观测→2026-11-23', pct(sn.le('USDJPY', '2026-08-23')[1], sn.val('USDJPY', '2026-11-23')), 0.29, note='最近观测日 %s 值 %s' % (sn.le('USDJPY', '2026-08-23')[0].isoformat(), sn.le('USDJPY', '2026-08-23')[1]))
P('Y32', '披露③「美联储目标区间上限 3.75→4.00 于 2026-09-17」', 'series_store.DFEDTARU 2026-09-16→2026-09-17', '%s→%s' % (('%g' % sn.val('DFEDTARU', '2026-09-16')), ('%g' % sn.val('DFEDTARU', '2026-09-17'))), '3.75→4')
es = sn.series('ECB_DFR')
_i0 = max(i for i, (a, b) in enumerate(es) if a <= dt.date(2026, 9, 10))
_ch = next(((es[i][0], es[i - 1][1], es[i][1]) for i in range(_i0 + 1, len(es)) if es[i][1] != es[i - 1][1]), None)
EX['ecb_dfr_change'] = [_ch[0].isoformat(), _ch[1], _ch[2]] if _ch else None
P('Y33', '披露③「欧央行存款便利利率 2.25→2.50 于 2026-09-16」', 'series_store.ECB_DFR 2026-09 内首次变动(观测日,前值→新值)', '%s|%s→%s' % (_ch[0].isoformat(), ('%g' % _ch[1]), ('%g' % _ch[2])) if _ch else 'NA', '2026-09-16|2.25→2.5', note='2026-08-01..2026-10-15 观测=%s' % [(a.isoformat(), b) for a, b in sn.win('ECB_DFR', dt.date(2026, 8, 1), dt.date(2026, 10, 15))])
P('Y34', '总判断「距上次调整按生效日 60 天、按决议日 66 天」及「其后至截止日的 24 天」', '日历日差(2026-11-23 减 2026-09-24 / 2026-09-18 / 2026-10-30)', '%d/%d/%d' % ((dt.date(2026, 11, 23) - dt.date(2026, 9, 24)).days, (dt.date(2026, 11, 23) - dt.date(2026, 9, 18)).days, (dt.date(2026, 11, 23) - dt.date(2026, 10, 30)).days), '60/66/24')
P('Y35', 'C3 竞争解释「2026-09-24 生效,落在 2026-09 最后一周」', '2026-09-24 距 9 月末天数', (dt.date(2026, 9, 30) - dt.date(2026, 9, 24)).days, 6)
tc = rep['research_plan']['turning_candidates']
pool = pick(tc, 'candidates', 'pool', default=[])
print('turning_candidates keys', sorted(tc.keys()), '| pool[0] keys', sorted(pool[0].keys()) if pool else None)
dkey = 'delta' if 'delta' in pool[0] else sorted(pool[0].keys())[0]
mkey = 'dimension' if 'dimension' in pool[0] else sorted(pool[0].keys())[0]
P('Y36', 'turnings[0]「为候选池内最大单段变动」(CPI 2026-02→2026-05, +1.7326)', '候选池 |delta| 最大者', max(pool, key=lambda c: abs(c[dkey]))[dkey], 1.7326, tol=1e-9)
P('Y37', 'turnings[1]「增长维候选池内最大的三个月变化」(INDPRO -0.9571)', '候选池 growth 维 |delta| 最大者', max((c for c in pool if c[mkey] == 'growth'), key=lambda c: abs(c[dkey]))[dkey], -0.9571, tol=1e-9)
P('Y38', '转折行数 3 = 引擎面 top_n_expected', 'report.json research_plan.turning_candidates.top_n_expected / len(turnings)', '%s/%d' % (pick(tc, 'top_n_expected', 'top_n', default=None), len(pick(aj['reader_map'], 'turnings', default=[]))), '3/3')
st26 = [(m, s) for m, s in steps if m.startswith('2026') and s > 1 and m <= '2026-07']
P('Y39', 'turnings[2]「为 2026 年内第三个上行月均台阶(此前: 2026-01 +17bp、2026-06 +11bp)」', '2026-01..2026-07 正台阶序', ','.join('%s%+.0fbp' % x for x in st26), '2026-01+17bp,2026-06+11bp,2026-07+14bp')
cal = load(os.path.join(RUN, 'root_overlay', 'config', 'release_calendar.json'))
ents = cal['entries']
print('calendar version', cal.get('version'), 'n entries', len(ents), '| entry keys', sorted(ents[0].keys()))
print('calendar entry kinds', sorted({str(pick(e, 'kind', 'event_kind', 'category', 'entry_type')) for e in ents}))
pol = [e for e in ents if 'POLICY' in str(pick(e, 'kind', 'event_kind', 'category', 'entry_type')).upper()]
P('Y40', 'turnings[2]「发布日历政策条目仅 2 条、均为日本央行实录」', 'release_calendar.json kind 含 POLICY 的条目', ','.join(sorted(pick(e, 'entry_id', 'id') for e in pol)), 'RC-JP-BOJ-MAINT-2026-10,RC-JP-BOJ-TARGET-2026-09')
P('Y41', 'turnings[2]「政策事件簇为空」', 'report.json research_plan.policy_event_clusters.clusters 长度', len(pick(rep['research_plan'].get('policy_event_clusters') or {}, 'clusters', default=[])), 0)
dfs = rep['research_plan']['policy_doc_facts']
print('policy_doc_facts[0] keys', sorted(dfs[0].keys()) if dfs else None)
P('Y42', '披露「FOMC 2026年10月会议纪要 2026-11-18 发布」(引擎文档事实面)', 'report.json research_plan.policy_doc_facts[0]', '%s|%s' % (pick(dfs[0], 'doc_id', 'fact_id', 'id'), pick(dfs[0], 'published_on', 'publish_date', 'date')), 'FOMC-MINUTES-2026-10|2026-11-18')
fpk = 'first_publish_on_or_after' if 'first_publish_on_or_after' in ents[0] else None
inwin = sorted('%s@%s' % (pick(e, 'entry_id', 'id'), e.get(fpk)) for e in ents if fpk and '2026-10-30' < str(e.get(fpk))[:10] <= '2026-11-23')
EX['cal_entries_published_after_1030'] = inwin
EX['cal_policy_entries_in_window'] = [pick(e, 'entry_id', 'id') for e in pol if fpk and '2026-10-30' < str(e.get(fpk))[:10] <= '2026-11-23']
P('Y43', '信息项: 总判断「日历核验覆盖止于 2026-10-30,其后至截止日的 24 天引擎日历无条目」——期内发布日历条目数 / 其中日本央行条目数', 'release_calendar.json first_publish∈(2026-10-30,2026-11-23]', '%d/%d' % (len(inwin), len(EX['cal_policy_entries_in_window'])), '%d/%d' % (len(inwin), len(EX['cal_policy_entries_in_window'])),
  note='期内条目=%s; 另有引擎文档事实 FOMC-MINUTES-2026-10(2026-11-18); 受审句字面为「无条目」' % inwin)
trio = rep['research_plan']['us_rates_trio']['window']
P('Y44', '传导环2「近一月共同交易日窗(2026-10-20→2026-11-19)」= 引擎面窗口', 'report.json research_plan.us_rates_trio.window', '%s→%s' % (trio['from'], trio['to']), '2026-10-20→2026-11-19', note='calendar_days_between=%s' % trio.get('calendar_days_between'))
reg = load(os.path.join(RUN, 'root_overlay', 'config', 'metric_registry.json'))
FREQ = {m.get('metric_id'): m.get('frequency') for m in reg['metrics']}
RULE = {}
for c in rep['research_plan']['point_values']['cells']:
    mm = re.search(r'\+(\d+)天', c['anchors']['3个月前'].get('publication_rule', ''))
    RULE[c['metric_id']] = int(mm.group(1)) if mm else None
vis = []
m = dt.date(2026, 11, 1)
while m <= dt.date(2027, 6, 1):
    pd0 = period_end(m, quarterly=(FREQ.get('CORE_PCE') == 'quarterly')) + dt.timedelta(days=RULE.get('CORE_PCE') or 0)
    if pd0 <= D('2027-02-15'):
        vis.append('%s→%s' % (m.isoformat()[:7], pd0.isoformat()))
    m = add_months(m, 1)
P('Y45', 'S1 触发指标 CORE_PCE 同比在期限 2027-02-15 内可观测(规则发布日 ≤ 期限 的观测月)', 'CORE_PCE 月末+30天', ','.join(vis), '2026-11→2026-12-30,2026-12→2027-01-30')
ev = rep['evidence_index']
evs = ev if isinstance(ev, list) else pick(ev, 'entries', 'items', default=[])
ids = sorted({pick(e, 'metric_id', 'series_id', 'id') for e in evs if isinstance(e, dict)})
jpin = [i for i in ids if i and ('JP' in i and ('CPI' in i))]
EX['evidence_index_ids_n'] = len(ids)
EX['evidence_index_jp_inflation'] = jpin
jpc = {d.strftime('%Y-%m'): v for d, v in sn.series('JP_CPI_YOY')} if sn.has('JP_CPI_YOY') else {}
EX['jp_cpi_yoy_store'] = {k: jpc.get(k) for k in ('2026-02', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10')} if jpc else None
P('Y46', '信息项: 转折面「日本端…未在通胀维同步」——本问证据索引内日本通胀序列数 / 序列库内 JP_CPI_YOY 2026-02→2026-05 变动(pp)', 'report.json evidence_index / series_store.JP_CPI_YOY(证据索引外)', '%d/%s' % (len(jpin), ('%+.2f' % (jpc['2026-05'] - jpc['2026-02'])) if '2026-05' in jpc and '2026-02' in jpc else 'NA'),
  '%d/%s' % (len(jpin), ('%+.2f' % (jpc['2026-05'] - jpc['2026-02'])) if '2026-05' in jpc and '2026-02' in jpc else 'NA'), note='证据索引 %d 条; JP_CPI_YOY 月值=%s' % (len(ids), EX['jp_cpi_yoy_store']))


# ---- 调试: 受审稿中含待定记号的句子(供后续逐个落点) ----
def walk(o, path, out):
    if isinstance(o, str):
        out.append((path, o))
    elif isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + '.' + k, out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, '%s[%d]' % (path, i), out)
STRS = []
walk(aj, '$', STRS)
for tok in ('EURUSD', '2.30', 'TIPS_10Y', '159.55', '116.72'):
    for p, s in STRS:
        if tok in s:
            for m in re.finditer(re.escape(tok), s):
                a, b = max(0, m.start() - 70), min(len(s), m.end() + 90)
                print('TOK[%s] %s: …%s…' % (tok, p, s[a:b].replace('\n', ' ')))
json.dump({'points': PTS, 'extra': EX}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('POINTS', len(PTS), 'MISMATCH', sum(1 for p in PTS if not p['ok']))
