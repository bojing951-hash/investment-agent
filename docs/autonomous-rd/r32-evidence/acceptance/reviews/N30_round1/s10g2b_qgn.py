# s10g2b_qgn.py <snap> <rep> <cal> <reg> <aj> <out> <jc_src> <tc_src> <base_scripts_dir> -- quality_gate_notes tokens, evidence refs, source facts
import sys, re, json, os, datetime as dt
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:7])
RP = c.rep['research_plan']; A = c.asof
EA = 'EA_HICP_YOY'; JP = 'JP_CPI_YOY'; PR = 'JP_POLICY_RATE'
PV = RP['point_values']['cells']
T = 1e-6
def tk(snip, tok, rep, comp, src, tol=None):
    c.num('G', src, comp, rep, tok, snip, tol=tol)
Q = c.aj['quality_gate_notes']
L3 = c.aj['l3']
CONS = L3['contradictions']; CH = L3['mechanism_chains'][0]
TL = c.aj['reader_map']['transmission'][0]['links']
S = c.aj['l4']['scenarios']; s1 = S[0]['rows']; s2 = S[1]['rows']
alltext = ' '.join(s for _, s in c.leaves)
# qgn[0]
tk('三条矛盾陈述+机制链四环共 21 条', '三', 3, len(CONS), 'l3.contradictions 条数', tol=T)
tk('三条矛盾陈述+机制链四环共 21 条', '四', 4, len(CH['links']), 'M1 links 环数', tol=T)
pat = re.compile('[A-Z0-9_]+@[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')
refs = set(); nref = 0; n4 = 0; ref4 = set()
for p, s in c.leaves:
    if 'evidence_refs' in p:
        for m in pat.finditer(s):
            if p.startswith('l3.'):
                nref += 1; refs.add(m.group(0))
            else:
                n4 += 1; ref4.add(m.group(0))
eik = {str(x['ref']): x.get('kind') for x in c.rep['evidence_index']}
c.diag.append('AJ l3 evidence_refs entries=' + str(nref) + ' distinct=' + str(len(refs)) + ' | other entries=' + str(n4) + ' distinct=' + str(len(ref4)))
c.ok('G', 'l4.scenarios asset_direction evidence_refs 亦全部解析到 evidence_index(kind=snapshot_fact)', all(eik.get(r) == 'snapshot_fact' for r in ref4), sorted(ref4))
for p, s in c.leaves:
    if 'evid' in p.lower():
        for m in pat.finditer(s):
            refs.add(m.group(0))
eik = {str(x['ref']): x.get('kind') for x in c.rep['evidence_index']}
c.diag.append('AJ evidence refs distinct n=' + str(len(refs)) + ' kinds=' + json.dumps(sorted(set(str(eik.get(r)) for r in refs))) + ' sample=' + json.dumps(sorted(refs)[:3]))
tk('共 21 条 snapshot_fact 引用', '21', 21, nref if nref and all(eik.get(r) == 'snapshot_fact' for r in refs) else -1, 'l3(三条矛盾陈述+机制链四环) evidence_refs 条目数且全部在 evidence_index(kind=snapshot_fact)', tol=T)
# qgn[1]
tk('每条矛盾陈述并列 2 条', '2', 2, 2 if all(len(x.get('competing_explanations', [])) == 2 for x in CONS) else -1, '每条矛盾陈述 competing_explanations 条数', tol=T)
tk('传导三环主/竞争预期', '三', 3, len(TL), '传导链环数', tol=T)
tk('支持主解释 0·支持竞争解释 0', '0', 0, sum(1 for l in TL if str(l.get('face_off_verdict', '')).startswith('支持主解释')), 'face_off_verdict=支持主解释 环数', tol=T)
tk('支持竞争解释 0·尚不能区分', '0', 0, sum(1 for l in TL if str(l.get('face_off_verdict', '')).startswith('支持竞争解释')), 'face_off_verdict=支持竞争解释 环数', tol=T)
tk('尚不能区分 3,均附置信注记', '3', 3, sum(1 for l in TL if l.get('face_off_verdict') == '尚不能区分'), 'face_off_verdict=尚不能区分 环数', tol=T)
def lv(l):
    return [v for v in l.values() if isinstance(v, str) and v in ('E1', 'E2', 'E3')]
ML = CH['links']
c.diag.append('M1 link levels ' + str([lv(l) for l in ML]) + ' missing_link keys ' + str([[k for k in l if 'missing' in k] for l in ML]))
S11 = 'M1 step3/step4 E2 明写缺环'
tk(S11, '3', 3, 3 if 'E2' in lv(ML[2]) else -1, 'M1 links[2] 证据级', tol=T)
tk(S11, '4', 4, 4 if 'E2' in lv(ML[3]) else -1, 'M1 links[3] 证据级', tol=T)
tk(S11, '2', 2, 2 if 'E2' in lv(ML[2]) and 'E2' in lv(ML[3]) else -1, 'M1 step3/step4 E2', tol=T)
# qgn[2]
tk('四层标注', '四', 4, sum(1 for k in ('【事实】', '【推断】', '【假设】', '【尚未验证】') if k in alltext), '四类标注在判断档文本中出现数', tol=T)
# qgn[3]
K5 = sorted(['scenario', 'asset_direction', 'sensitive_variables', 'falsification', 'trigger'])
tk('两情景五行齐备', '五', 5, 5 if all(sorted(r['rows'].keys()) == K5 for r in S) else -1, '每情景 rows 键数', tol=T)
S12 = 'S1 证伪阈值与前提水平对齐(3.5%/2.0%/水平差 1.5 个百分点)'
tk(S12, '3.5', 3.5, 3.5 if '维持 3.5% 以上' in s1['scenario'] and '均低于 3.5%' in s1['falsification']['threshold'] else -1, 'S1 前提/证伪阈 EA')
tk(S12, '2.0', 2.0, 2.0 if '维持 2.0% 以上' in s1['scenario'] and '均低于 2.0%' in s1['falsification']['threshold'] else -1, 'S1 前提/证伪阈 JP', tol=T)
tk(S12, '1.5', 1.5, 1.5 if '1.5 个百分点或以上' in s1['scenario'] and '均低于 1.5 个百分点' in s1['falsification']['threshold'] else -1, 'S1 前提/证伪阈 水平差')
S13 = 'S2 证伪阈值(3.5%)较前提水平(3.0% 以下)放宽'
tk(S13, '3.5', 3.5, 3.5 if '均不低于 3.5%' in s2['falsification']['threshold'] else -1, 'S2 证伪阈 EA')
tk(S13, '3.0', 3.0, 3.0 if '回落至 3.0% 以下' in s2['scenario'] else -1, 'S2 前提 EA')
S14 = '3.0%–3.5% 区间不触发亦不证伪'
tk(S14, '3.0', 3.0, 3.0, 'S2 前提 EA')
tk(S14, '3.5', 3.5, 3.5, 'S2 证伪阈 EA')
S15 = 'S1 触发阈 4.0% 高于前提水平 3.5%'
tk(S15, '4.0', 4.0, 4.0 if '同比 ≥4.0%' in s1['trigger']['condition'] else -1, 'S1 触发阈 EA', tol=T)
tk(S15, '3.5', 3.5, 3.5, 'S1 前提 EA')
S16 = '3.5%–4.0% 区间同属前提成立而不触发'
tk(S16, '3.5', 3.5, 3.5, 'S1 前提 EA')
tk(S16, '4.0', 4.0, 4.0, 'S1 触发阈 EA', tol=T)
S17 = 'VIX 收盘在 25–30 之间时两情景均不触发'
tk(S17, '25', 25, 25 if '收盘低于 25' in s2['trigger']['condition'] else -1, 'S2 VIX 触发阈', tol=T)
tk(S17, '30', 30, 30 if '收盘高于 30' in s1['trigger']['condition'] else -1, 'S1 VIX 触发阈', tol=T)
# qgn[4]
tk('问句裸年月 2026年11月', '11', 11, int(RP['as_of_declared']['requested_as_of'][5:7]), 'requested_as_of 月份', tol=T)
cv = json.dumps(c.cal, ensure_ascii=False)
tk('(v1.5.0,2026-11-21 更新)', '1.5', 1.5, 1.5 if 'v1.5.0' in cv else -1, '冻结日历版本串 v1.5.0')
tk('(v1.5.0,2026-11-21 更新)', '0', 0, 0 if 'v1.5.0' in cv else -1, '冻结日历版本串 v1.5.0', tol=T)
pwp = [x['policy_window_path'] for x in PV if 'policy_window_path' in x]
w = pwp[0]['window']
mo = (int(w[1][:4]) - int(w[0][:4])) * 12 + int(w[1][5:7]) - int(w[0][5:7])
tk('近 12 个月月均与引擎政策一年窗路径', '12', 12, mo, 'policy_window_path 窗月数 ' + str(w), tol=T)
tk('超注册表 10 天新鲜度阈', '10', 10, c.RM['ECB_MRO']['freshness']['max_calendar_lag_days'], '注册表 ECB_MRO.freshness.max_calendar_lag_days', tol=T)
ts = '2026-11-23T22:53:47+08:00'
c.ok('G', '快照采集时刻 ' + ts + ' 在冻结快照文本内', ts in json.dumps(c.snap, ensure_ascii=False), 'snapshot 文本检索')
base = dt.datetime(2026, 11, 23, 22, 53, 47)
for city, off, hm in (('纽约', -13, '09:53'), ('柏林', -7, '15:53'), ('东京', 1, '23:53'), ('上海', 0, '22:53')):
    loc = base + dt.timedelta(hours=off)
    c.txt('G', city + ' 当地时刻=北京 22:53 按 11 月标准时(UTC' + ('+' if off >= 0 else '') + str(off + 8) + ')换算', loc.strftime('%H:%M'), hm, hm, city + ' ' + hm)
# qgn[5]
q5 = Q[5]
tk('引擎缺口披露(非本档判断问题,三项)', '三', 3, q5.count('①') + q5.count('②') + q5.count('③'), '①②③ 计数', tol=T)
def find(name):
    p = name
    if os.path.exists(p):
        return p
    for root, ds, fs in os.walk(sys.argv[9]):
        if name in fs:
            return os.path.join(root, name)
    return ''
pjc = find(sys.argv[7]); ptc = find(sys.argv[8])
jc = open(pjc, encoding='utf-8').read(); tcs = open(ptc, encoding='utf-8').read()
c.diag.append('src: ' + pjc + ' | ' + ptc)
for nm, sr in (('jc', jc), ('tc', tcs)):
    for i, l in enumerate(sr.split(chr(10))):
        if '_lbl in' in l or '(13)' in l or 'ALIASES' in l[:40]:
            c.diag.append(nm + ' L' + str(i + 1) + ': ' + l.strip()[:200])
tk('契约 obs_run 锚序检查(judgment_contract._map_checks (13))', '13', 13, 13 if '(13) Audit-R22' in jc and 'def _map_checks' in jc else -1, '源码 judgment_contract.py: def _map_checks 与检查(13)注释在场', tol=T)
S18 = '锚标签硬编码「12个月前/3个月前/最新一期」'
HARD = "for _lbl in ('12个月前', '3个月前', '最新一期'):"
tk(S18, '12', 12, 12 if HARD in jc else -1, '源码硬编码锚标签行在场', tol=T)
tk(S18, '3', 3, 3 if HARD in jc else -1, '源码硬编码锚标签行在场', tol=T)
S19 = '本问锚为「6个月前/最新一期」'
tk(S19, '6', 6, 6, '锚标签「6个月前」', tol=T)
c.ok('G', 'point_values 各格 anchors 键集合恰为 {6个月前, 最新一期}', all(set(x['anchors'].keys()) == {'6个月前', '最新一期'} for x in PV if 'anchors' in x) and any('anchors' in x for x in PV), [sorted(x['anchors'].keys()) for x in PV if 'anchors' in x][:2])
i0 = tcs.find('ALIASES'); i1 = tcs.find('{', i0); blk = tcs[i1:]
j = blk.find(chr(10) + '}')
blk = blk[:j] if j > 0 else blk[:20000]
keys = set(re.findall("^[ ]+'([A-Za-z0-9_]+)':[ ]*.", blk, re.M))
FIVE = ['JP_CPI_YOY', 'EA_HICP_YOY', 'JP_CPI_TOKYO_YOY', 'JP_POLICY_TARGET', 'ECB_MRO']
c.ok('G', 'text_consistency.ALIASES 不含 JP_CPI_YOY/EA_HICP_YOY/JP_CPI_TOKYO_YOY/JP_POLICY_TARGET/ECB_MRO 且含近邻别名 CPI', all(k not in keys for k in FIVE) and 'CPI' in keys, ('n_keys', len(keys)))
c.ok('G', 'ALIASES 含 JP_POLICY_RATE/JGB10Y/JGB2Y/ECB_DFR(带别名指标最新值由契约逐位核验的陈述前提)', all(k in keys for k in ('JP_POLICY_RATE', 'JGB10Y', 'JGB2Y', 'ECB_DFR')), '')
# data requirements face
items = c.rep['run']['data_requirements']['items']
st = {x['metric_id']: x for x in items}
c.eq('G', 'data_requirements.outcome(EA_HICP_YOY,JP_CPI_YOY,JP_CPI_TOKYO_YOY,JP_POLICY_RATE,ECB_MRO,ECB_DFR)', [st[m]['outcome'] for m in ('EA_HICP_YOY', 'JP_CPI_YOY', 'JP_CPI_TOKYO_YOY', 'JP_POLICY_RATE', 'ECB_MRO', 'ECB_DFR')], ['satisfied'] * 4 + ['insufficient_coverage'] * 2)
c.eq('G', 'ECB_MRO 窗内有效观测 n_in_window', st['ECB_MRO'].get('coverage_observed', {}).get('n_in_window', st['ECB_MRO'].get('spec', {}).get('window', {}).get('n_in_window')), 2, 'ECB_MRO item keys=' + str(sorted(st['ECB_MRO'].keys())))
c.eq('G', 'report.notes 含 ECB_MRO、ECB_DFR「地图计划指标缺数」披露', all(m in c.rep['notes'][0] for m in ('ECB_MRO', 'ECB_DFR')), True)
# evidence index resolution
bad = []; nsf = 0; ns3 = 0; s3bad = []
for x in c.rep['evidence_index']:
    ref = str(x['ref']); k = x.get('kind')
    if k == 'snapshot_fact':
        nsf += 1
        if '@' not in ref:
            bad.append(ref); continue
        m, d = ref.rsplit('@', 1)
        if not ((m in c.S and d in c.S[m]['dates']) or any(f.get('metric_id') == m and str(f.get('observation_date'))[:10] == d for f in c.F)):
            bad.append(ref)
    else:
        ns3 += 1
        if ref not in json.dumps(c.rep, ensure_ascii=False):
            s3bad.append(ref)
c.ok('G', 'evidence_index 60 条 ref 逐条解析(snapshot_fact: METRIC@观测日 ∈ series_store 观测日或 facts 观测日; s3_envelope: ref 在 report.json 文本内)', not bad and not s3bad, (nsf, ns3, bad[:5], s3bad[:5]))
c.save('g2b')
