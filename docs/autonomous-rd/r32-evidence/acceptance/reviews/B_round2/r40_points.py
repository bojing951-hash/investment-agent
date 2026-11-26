# -*- coding: utf-8 -*-
# r40_points.py — I 情景 / K 渲染一致性与引擎渲染表
# 用法: /usr/bin/python3 -I r40_points.py <RUN_DIR> <SNAPSHOT_JSON> <OUT_JSON> <MD_DUMP_TXT>
import sys, os, json, re, math, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r00_common import *

RUN, SNAP, OUT, MDD = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
sn = Snap(load(SNAP))
rep = load(os.path.join(RUN, 'report.json'))
aj = load(os.path.join(RUN, 'agent_judgment.json'))
rp = rep['research_plan']
PTS = []
EX = {}
CAT = ['']
mdump = open(MDD, 'w', encoding='utf-8')


def cat(c):
    CAT[0] = c


def P(pid, where, key, comp, rep_, note='', tol=None):
    disp = round(comp, 6) if isinstance(comp, float) else comp
    ok = same(comp, rep_, tol)
    PTS.append({'id': pid, 'cat': CAT[0], 'where': where, 'key': key, 'computed': disp,
                'reported': rep_, 'ok': bool(ok), 'note': note})
    print('%s|%s|%s|comp=%s|rep=%s|%s|%s' % ('OK' if ok else 'XX', pid, CAT[0], disp, rep_, where, note))
    return ok


cells = rp['point_values']['cells']
RULE = {}
for c in cells:
    m = re.search(r'\+(\d+)天', c['anchors']['3个月前'].get('publication_rule', ''))
    RULE[c['metric_id']] = int(m.group(1)) if m else None


reg = load(os.path.join(RUN, 'root_overlay', 'config', 'metric_registry.json'))
FREQ = {m.get('metric_id'): m.get('frequency') for m in reg['metrics']}


def pubdate(sid, obs):
    return period_end(obs, quarterly=(FREQ.get(sid) == 'quarterly')) + dt.timedelta(days=RULE[sid])


# ---------------- I 情景 ----------------
cat('I 情景可观测性')
P('I01', 'S1 falsification「规则发布日 2026-12-16、2027-01-16」(2026-11 观测月)', 'EA_HICP_YOY 规则 2026-11-30 + 16天', pubdate('EA_HICP_YOY', dt.date(2026, 11, 1)).isoformat(), '2026-12-16')
P('I02', '同上(2026-12 观测月)', 'EA_HICP_YOY 规则 2026-12-31 + 16天', pubdate('EA_HICP_YOY', dt.date(2026, 12, 1)).isoformat(), '2027-01-16')
P('I03', 'S1 scenario「2027-01 观测月的规则发布日 2027-02-16」', 'EA_HICP_YOY 规则 2027-01-31 + 16天', pubdate('EA_HICP_YOY', dt.date(2027, 1, 1)).isoformat(), '2027-02-16')
P('I04', '「晚于期限 2027-02-15」', '2027-02-16 > 2027-02-15', (D('2027-02-16') > D('2027-02-15')), True)
P('I05', '「均不晚于期限 2027-02-15」(2026-12-16、2027-01-16)', 'max ≤ 2027-02-15', (max(D('2026-12-16'), D('2027-01-16')) <= D('2027-02-15')), True)
ea10 = sn.val('EA_HICP_YOY', '2026-10-01')
pce = yoy(sn, 'CORE_PCE', '2026-09-01')
tips = sn.val('TIPS_10Y', '2026-11-19')
bei = sn.val('BEI_10Y', '2026-11-20')
ea09 = sn.val('EA_HICP_YOY', '2026-09-01')
P('I06', 'S1 截止日未被证伪(最新 EA_HICP_YOY ≥ 证伪线 3.0)', 'series_store.EA_HICP_YOY 2026-10-01', (ea10 >= 3.0), True, note='EA=%s' % ea10)
P('I07', 'S1 触发条件截止日未满足(≥4.2 且 CORE_PCE ≥3.2 且 TIPS_10Y >3.0)', 'EA_HICP_YOY 2026-10 / CORE_PCE 同比 2026-09 / TIPS_10Y 2026-11-19', (ea10 < 4.2 and pce < 3.2 and tips <= 3.0), True, note='EA=%s PCE=%.4f TIPS=%s' % (ea10, pce, tips))
P('I08', 'S2 截止日未证伪亦未落空(2026-09 为 %s <4.0, 单月不构成两月证伪)' % ea09, 'series_store.EA_HICP_YOY 2026-09-01', (ea09 < 4.0), True)
P('I09', 'S2 触发条件截止日未满足(最新 ≤3.4 且 BEI_10Y <2.0)', 'EA_HICP_YOY 2026-10-01 / BEI_10Y 2026-11-20', (ea10 > 3.4 and bei >= 2.0), True, note='EA=%s BEI=%s' % (ea10, bei))
t1 = diff_bp(sn.val('TIPS_10Y', '2026-10-20'), sn.val('TIPS_10Y', '2026-11-19'))
s1 = pct(sn.val('SPX', '2026-10-23'), sn.val('SPX', '2026-11-23'))
P('I10', 'S2「该方向与近一月观察(共同交易日窗 2026-10-20→2026-11-19 实际利率 +11bp 而风险资产回落)相反」之前提在场', 'TIPS_10Y 近一月 >0 且 SPX 近一月 <0', (t1 > 0 and s1 < 0), True, note='TIPS=%+.0fbp SPX=%.2f%%' % (t1, s1))
P('I11', 'S1「日本月均中枢不低于当前台阶」之当前台阶', 'series_store.JP_POLICY_RATE 2026-10-01', sn.val('JP_POLICY_RATE', '2026-10-01'), 1.227)
s1r = aj['l4']['scenarios'][0]['rows']
s2r = aj['l4']['scenarios'][1]['rows']
P('I12', 'S1 内部一致: 证伪线 3.0 < 情景界 3.5 < 触发线 4.2', '阈值序', ('3.0' in s1r['falsification']['threshold'] and '3.5%' in s1r['scenario'] and '4.2%' in s1r['trigger']['condition']), True)
P('I13', 'S2 内部一致: 情景界 3.0 < 触发线 3.4 < 证伪线 4.0', '阈值序', ('3.0%' in s2r['scenario'] and '3.4%' in s2r['trigger']['condition'] and '4.0%' in s2r['falsification']['threshold']), True)
P('I14', '两情景期限均为 2027-02-15', 'S1/S2 trigger.deadline', '%s/%s' % (s1r['trigger']['deadline'], s2r['trigger']['deadline']), '2027-02-15/2027-02-15')
P('I15', '两情景敏感变量均为序列库在场序列(EA_HICP_YOY、CORE_PCE)', 'series_store 在场性', all(sn.has(m) for m in s1r['sensitive_variables'] + s2r['sensitive_variables']), True)
P('I16', '两情景区分/触发指标(TIPS_10Y、BEI_10Y)为序列库在场序列', 'series_store 在场性', (sn.has('TIPS_10Y') and sn.has('BEI_10Y')), True)
_obs = []
_m = dt.date(2026, 11, 1)
while _m <= dt.date(2027, 6, 1):
    if pubdate('EA_HICP_YOY', _m) <= D('2027-02-15'):
        _obs.append(_m.isoformat()[:7])
    _m = add_months(_m, 1)
P('I17', 'S2「连续两个月回落」在期限内可观测: 截止期限前恰有两个 EA_HICP_YOY 发布日(2026-12-16、2027-01-16)', '规则发布日 ≤ 2027-02-15 的 EA_HICP_YOY 观测月(2026-11 起)', ','.join(_obs), '2026-11,2026-12')

json.dump({'points': PTS, 'extra': EX}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('POINTS', len(PTS), 'MISMATCH', sum(1 for p in PTS if not p['ok']))
mdump.close()
sys.exit(0)


def pubdate2(sid, obs):  # 未用(保留占位)
    return period_end(obs) + dt.timedelta(days=RULE[sid])


# ---------------- K 渲染一致性(已移至 r50_render.py) ----------------
cat('K 渲染一致性')


def norm(s):
    s = s.replace('−', '-').replace('–', '-').replace('—', '-').replace('\\', '').replace('*', '').replace('“', '"').replace('”', '"').replace('`', '')
    return re.sub(r'\s+', '', s)


mds = {}
for fn in ('report.md', 'MAP_REPORT.md', 'FULL_REPORT.md'):
    p = os.path.join(RUN, fn)
    if os.path.exists(p):
        mds[fn] = norm(open(p, encoding='utf-8').read())
EX['md_sizes'] = {k: len(v) for k, v in mds.items()}


def strs(o, out):
    if isinstance(o, str):
        if len(o) >= 12:
            out.append(o)
    elif isinstance(o, dict):
        for k, v in o.items():
            if k in ('produced_by', 'basis'):
                continue
            strs(v, out)
    elif isinstance(o, list):
        for v in o:
            strs(v, out)


texts = []
strs(aj['l3'], texts)
strs(aj['l4'], texts)
strs(aj['reader_map'], texts)
texts += aj.get('quality_gate_notes', [])
texts = [t for t in texts]
EX['md_texts_n'] = len(texts)
for fn, md in mds.items():
    miss = [t for t in texts if norm(t) not in md]
    EX['md_missing_' + fn] = [m[:90] for m in miss]
    P('K01 %s' % fn, '受审稿 agent_judgment.json 全文串(L3/L4/reader_map/质量门注记)在 %s 中逐串在场' % fn, 'len(缺失串)', len(miss), 0, note='共 %d 串' % len(texts))
# MAP_REPORT.sha256
sha_p = os.path.join(RUN, 'MAP_REPORT.sha256')
if os.path.exists(sha_p):
    import hashlib
    rec = open(sha_p, encoding='utf-8').read().split()[0]
    got = hashlib.sha256(open(os.path.join(RUN, 'MAP_REPORT.md'), 'rb').read()).hexdigest()
    P('K02', 'MAP_REPORT.sha256 与 MAP_REPORT.md 现文件一致(受审版本同一性)', 'sha256(MAP_REPORT.md)', got, rec)
    P('K03', 'report.json semantic_review.map_report_sha256 与 MAP_REPORT.md 一致(Round-1 所审文本与本次受审文本同一性待核: 不同则为修订后版本)', 'sha256(MAP_REPORT.md) vs report.semantic_review.map_report_sha256', got, rep['semantic_review'].get('map_report_sha256'), note='不同=受审稿已在 Round-1 后修订(预期)')

# ---------------- 引擎渲染表复算 ----------------
cat('L 引擎渲染表')
for ym, v in [('2025-03', 0.727212), ('2022-06', 0.791806), ('2023-10', 1.054168), ('2021-02', 1.284945), ('2020-01', 1.357685)]:
    P('L01 %s' % ym, 'FULL_REPORT 相似候选 %s 月 JP_POLICY_RATE 值' % ym, sn.key('JP_POLICY_RATE', D(ym + '-01')), sn.val('JP_POLICY_RATE', D(ym + '-01')), v)
g = sn.series('US_REAL_GDP')
u = dict(sn.series('UNEMPLOYMENT'))
common = [(d, v, u[d]) for d, v in g if d in u]


def pearson(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


v1 = pearson([c[1] for c in common], [c[2] for c in common])
qm = [(d, v, (u.get(d) or 0, u.get(add_months(d, 1)), u.get(add_months(d, 2)))) for d, v in g]
EX['pearson_variants'] = {'exact_common_n%d' % len(common): round(v1, 4), 'common_dates_missing_in_unemp': [d.isoformat() for d, v in g if d not in u]}
mdump.write('PEARSON exact-common n=%d r=%.4f\n' % (len(common), v1))
for fn in ('MAP_REPORT.md', 'FULL_REPORT.md', 'report.md'):
    p = os.path.join(RUN, fn)
    if not os.path.exists(p):
        continue
    for i, line in enumerate(open(p, encoding='utf-8').read().split('\n')):
        if any(k in line for k in ('pearson', 'Pearson', '0.727212', '1.357685', '0.791806', '1.054168', '1.284945', '净变动', '距上次调整', '一年窗', '核验覆盖', '相似', 'analog', 'top3', '候选池')):
            mdump.write('%s:%d: %s\n' % (fn, i + 1, line[:700]))
mdump.close()

json.dump({'points': PTS, 'extra': EX}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('POINTS', len(PTS), 'MISMATCH', sum(1 for p in PTS if not p['ok']))
print('MD missing counts', {k: len(v) for k, v in EX.items() if k.startswith('md_missing_')})
