# s10g1_l4trans.py <snap> <rep> <cal> <reg> <aj> <out>  -- part G1: l4 scenario parameters + transmission chain occurrences
import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:7])
RP = c.rep['research_plan']; A = c.asof
EA = 'EA_HICP_YOY'; JP = 'JP_CPI_YOY'; TK = 'JP_CPI_TOKYO_YOY'; PR = 'JP_POLICY_RATE'
jc = [x for x in c.cal['entries'] if x.get('metric_id') == 'JP_POLICY_TARGET']
JT = [x for x in jc if x.get('kind') == 'policy_decision'][0]
JM = [x for x in jc if x.get('kind') == 'policy_maintenance'][0]
chd = [x for x in c.changes('ECB_DFR') if '2026-05-23' <= x[0] <= A]
chmall = c.changes('ECB_MRO')
vix = c.S['VIX']; T = 1e-6
S = c.aj['l4']['scenarios']; s1 = S[0]['rows']; s2 = S[1]['rows']
ea10 = c.mv(EA, '2026-10'); jp10 = c.mv(JP, '2026-10'); dif = ea10 - jp10
Q3 = c.aj['quality_gate_notes'][3]
def tk(snip, tok, rep, comp, src, tol=None):
    c.num('G', src, comp, rep, tok, snip, tol=tol)
def dpct(m, d):
    s = c.S[m]; i = s['dates'].index(d)
    return pct(s['values'][i - 1], s['values'][i])
STEP = 25 if all(abs(b_ - a_ - 0.25) < 1e-9 for _, a_, b_ in chd) and len(chd) == 2 else -1
# ---- l4: S1 ----
tk('HICP 同比维持 3.5% 以上', '3.5', 3.5, 3.5 if ea10 >= 3.5 else -1, 'S1 前提阈 3.5; 与截止读数相容(EA@2026-10=' + str(ea10) + ')')
tk('ECB 再有至少一次 +25bp 上调', '25', 25, STEP, 'S1 政策分量步长=已观测变更步长 25bp', tol=T)
tk('CPI 同比维持 2.0% 以上', '2.0', 2.0, 2.0 if jp10 >= 2.0 else -1, 'S1 前提阈 2.0; 与截止读数相容(JP@2026-10=' + str(jp10) + ')', tol=T)
tk('维持 1.5 个百分点或以上', '1.5', 1.5, 1.5 if dif >= 1.5 else -1, 'S1 前提水平差 1.5; 截止读数 EA−JP=' + str(round(dif, 2)))
tk('HICP 同比均低于 3.5%(前提水平)', '3.5', 3.5, 3.5 if '维持 3.5% 以上' in s1['scenario'] else -1, 'S1 证伪阈=S1 前提阈')
tk('CPI 同比均低于 2.0%(前提水平)', '2.0', 2.0, 2.0 if '维持 2.0% 以上' in s1['scenario'] else -1, 'S1 证伪阈=S1 前提阈', tol=T)
tk('均低于 1.5 个百分点,分化延续', '1.5', 1.5, 1.5 if '1.5 个百分点或以上' in s1['scenario'] else -1, 'S1 证伪阈=S1 前提水平差')
tk('同比 ≥4.0% 且两地水平差', '4.0', 4.0, ea10, 'S1 触发阈 4.0=截止读数(不等式成立; 2026-11 期读数未发布故未触发)', tol=T)
tk('不低于 1.5 个百分点(以引擎发', '1.5', 1.5, 1.5 if '1.5 个百分点或以上' in s1['scenario'] else -1, 'S1 触发水平差阈=S1 前提')
tk('收盘高于 30', '30', 30, 30, 'S1 VIX 触发阈 30(设定值; 截止前末收盘 ' + str(c.at('VIX', '2026-11-20')) + ')', tol=T)
# ---- l4: S2 ----
tk('同比回落至 3.0% 以下、', '3.0', 3.0, 3.0, 'S2 前提阈 3.0(与截止读数方向相反=并列反例情景)')
tk('同比回落至 2.0% 以下、', '2.0', 2.0, 2.0, 'S2 前提阈 2.0', tol=T)
tk('收窄至 1 个百分点以内', '1', 1, 1.0, 'S2 前提水平差 1.0', tol=T)
tk('同比均不低于 3.5%(未回落)', '3.5', 3.5, 3.5, 'S2 证伪阈 3.5(较前提 3.0 放缓, 已披露)')
tk('回落至 3.0% 以下」的前提被证伪', '3.0', 3.0, 3.0, 'S2 证伪文本所引前提阈=S2 前提')
tk('CPI 同比均不低于 2.0%', '2.0', 2.0, 2.0, 'S2 日本端证伪阈=S2 前提', tol=T)
tk('均不低于 1.0 个百分点', '1.0', 1.0, 1.0, 'S2 水平差证伪阈=S2 前提')
tk('同比低于 3.0% 且', '3.0', 3.0, 3.0, 'S2 触发阈=S2 前提')
tk('同比低于 2.0%(均为前提水平', '2.0', 2.0, 2.0, 'S2 触发阈=S2 前提', tol=T)
tk('不超过 1.0 个百分点', '1.0', 1.0, 1.0, 'S2 触发水平差阈=S2 前提')
tk('收盘低于 25', '25', 25, 25, 'S2 VIX 触发阈 25(设定值; 与 S1 的 30 之间为两情景均不触发区, 已披露)', tol=T)
K5 = sorted(['scenario', 'asset_direction', 'sensitive_variables', 'falsification', 'trigger'])
c.ok('G', '两情景 rows 五行齐备(scenario/asset_direction/sensitive_variables/falsification/trigger)', all(sorted(r['rows'].keys()) == K5 for r in S), [sorted(r['rows'].keys()) for r in S])
c.ok('G', '两情景方向互补且互斥: EA 端 S1「3.5% 以上」vs S2「3.0% 以下」; 水平差 S1「1.5 或以上」vs S2「1 个百分点以内」', '维持 3.5% 以上' in s1['scenario'] and '回落至 3.0% 以下' in s2['scenario'] and '1.5 个百分点或以上' in s1['scenario'] and '收窄至 1 个百分点以内' in s2['scenario'], 'S1/S2')
c.ok('G', '不触发/不证伪区间已披露(3.0%–3.5%、3.5%–4.0%、VIX 25–30)', '3.0%–3.5% 区间不触发亦不证伪' in Q3 and '3.5%–4.0% 区间同属前提成立而不触发' in Q3 and 'VIX 收盘在 25–30 之间时两情景均不触发' in Q3 and '证伪条件均不含 VIX 分量' in Q3, 'quality_gate_notes[3]')
c.ok('G', '证伪条件文本确不含 VIX 分量(S1/S2 falsification.threshold)', all('VIX' not in r['rows']['falsification']['threshold'] for r in S), 'l4.scenarios[*].rows.falsification.threshold')
c.ok('G', '两情景时限 2027-02-15 均晚于 2026-12 期读数推定入档日', all(r['rows']['trigger']['deadline'] == '2027-02-15' for r in S) and '2027-02-15' > c.pub(EA, '2026-12') and '2027-02-15' > c.pub(JP, '2026-12'), (c.pub(EA, '2026-12'), c.pub(JP, '2026-12')))
c.ok('G', '情景观测月 2026-11/2026-12 的推定发布日均晚于研究截止日(未被截止日读数触发或证伪)', c.pub(EA, '2026-11') > A and c.pub(JP, '2026-11') > A, (c.pub(EA, '2026-11'), c.pub(JP, '2026-11')))
# ---- transmission link0 ----
tk('窗内 2026-05 3.2→2026-10 4.0', '3.2', 3.2, c.mv(EA, '2026-05'), 'EA@2026-05')
tk('2026-05 3.2→2026-10 4.0', '4.0', 4.0, ea10, 'EA@2026-10', tol=T)
tk('窗内 2026-05 1.53→2026-10 2.44', '1.53', 1.53, c.mv(JP, '2026-05'), 'JP@2026-05')
tk('2026-05 1.53→2026-10 2.44', '2.44', 2.44, jp10, 'JP@2026-10')
tk('各 +25bp;BOJ 2026-09-18', '25', 25, STEP, 'ECB 两次变更幅(bp)', tol=T)
tk('均高于 2026-02 的 1.9,合读数驱动', '1.9', 1.9, c.mv(EA, '2026-02'), 'EA@2026-02')
tk('均高于 2026-02 的 1.9,与读数驱动相容', '1.9', 1.9, c.mv(EA, '2026-02'), 'EA@2026-02')
tk('维持 2.15/2.0 共 371 天', '2.15', 2.15, c.at('ECB_MRO', '2025-06-11'), 'ECB_MRO@2025-06-11 在值')
tk('维持 2.15/2.0 共 371 天', '2.0', 2.0, c.at('ECB_DFR', '2025-06-11'), 'ECB_DFR@2025-06-11 在值', tol=T)
tk('升至 2026-04 的 3.0 而未触发变更', '3.0', 3.0, c.mv(EA, '2026-04'), 'EA@2026-04', tol=T)
tk('相隔 91 天、各 +25bp,等距等幅路径与', '25', 25, STEP, 'ECB 两次变更幅(bp)', tol=T)
tk('相隔 91 天、各 25bp,等距等幅路径与', '25', 25, STEP, 'ECB 两次变更幅(bp)', tol=T)
tk('欧央行样本仅两次(n=2)', '2', 2, len(chd), 'ECB 窗内变更次数', tol=T)
tk('(欧央行 n=2)——尚不能区分', '2', 2, len(chd), 'ECB 窗内变更次数', tol=T)
dec2 = prev_thu(chd[1][0]); dec1 = prev_thu(chd[0][0])
vj = c.vis(JP, JT['decision_date']); vt = c.vis(TK, JT['decision_date'])
tk('决议前可见全国读数 2026-07 的 1.97、东京读数', '1.97', 1.97, vj[1] if vj[0][:7] == '2026-07' else -1, 'JP 决议日 2026-09-18 前可见读数(推定发布规则)')
tk('东京读数 2026-08 的 1.9(均为', '1.9', 1.9, vt[1] if vt[0][:7] == '2026-08' else -1, '东京 决议日前可见读数')
tk('全国读数 2026-07 的 1.97(高于 2026-02 谷底 1.27)', '1.97', 1.97, vj[1] if vj[0][:7] == '2026-07' else -1, 'JP 决议日前可见读数')
Y9 = ['2026-0%d' % i for i in range(1, 10)]
v2 = c.vis(EA, dec2)
tk('决议日前可见读数 2.9 低于 2026-05 峰值 3.2', '2.9', 2.9, v2[1] if v2[0][:7] == '2026-07' else -1, 'EA 第二次回推决议日(' + dec2 + ')前可见读数')
visp = [x[:7] for x in c.S[EA]['dates'] if x >= '2025-11-01' and c.pub(EA, x[:7]) <= dec2]
pk = max(visp, key=lambda y: c.mv(EA, y))
tk('决议日前可见读数 2.9 低于 2026-05 峰值 3.2', '3.2', 3.2, c.mv(EA, '2026-05') if pk == '2026-05' else -1, '第二次回推决议日(' + dec2 + ')前可见读数(近十二期)峰值=2026-05')
tk('可见读数为 2026-05 的 3.2 与 2026-08', '3.2', 3.2, c.mv(EA, '2026-05'), '按日历两档形态第一次决议日前可见=2026-05 期')
tk('2026-08 的 3.2,此条反向观察不成立', '3.2', 3.2, c.mv(EA, '2026-08'), '按日历两档形态第二次决议日前可见=2026-08 期')
pc = [x for x in chmall if x[0] < chd[0][0]][-1][0]
tk('(另一条 371 天反向观察不受影响', '371', 371, days(pc, chd[0][0]), 'days(' + pc + ',' + chd[0][0] + ')', tol=T)
Y2526 = ['2025-%02d' % i for i in range(1, 13)] + ['2026-%02d' % i for i in range(1, 11)]
tk('高于 2026-02 谷底 1.27', '1.27', 1.27, c.mv(JP, '2026-02') if c.mv(JP, '2026-02') == min(c.mv(JP, y) for y in Y2526) else -1, 'JP 2025-01..2026-10 谷底=2026-02')
ece = [x for x in c.cal['entries'] if x.get('metric_id') == 'EA_HICP_YOY']
c.ok('G', '冻结日历 EA HICP 三条实录均为「次月首日快报(first_publish=次月1日)+次月终值」形态', all(x['first_publish_on_or_after'] == plus(mend(x['obs_from'][:7]), 1) and x['obs_from'][:7] < x['final_publish_on'][:7] <= plus(mend(x['obs_from'][:7]), 1)[:7] for x in ece), [(x['first_publish_on_or_after'], x['final_publish_on']) for x in ece])
c.ok('G', '按该两档形态两次回推决议日前可见分别为 2026-05 期(快报 ' + plus(mend('2026-05'), 1) + ')与 2026-08 期(快报 ' + plus(mend('2026-08'), 1) + ')', plus(mend('2026-05'), 1) <= dec1 < plus(mend('2026-06'), 1) and plus(mend('2026-08'), 1) <= dec2 < plus(mend('2026-09'), 1), (dec1, dec2))
c.diag.append('vis: JP before BOJ ' + str(vj) + ' | TK ' + str(vt) + ' | EA before dec2 ' + str(v2) + ' | EA before dec1 ' + str(c.vis(EA, dec1)) + ' | before eff1 ' + str(c.vis(EA, chd[0][0])) + ' | before eff2 ' + str(c.vis(EA, chd[1][0])))
# ---- transmission link1 ----
e0 = c.at('EURUSD', '2026-10-23') * c.at('USDJPY', '2026-10-23')
e1 = c.at('EURUSD', '2026-11-20') * c.at('USDJPY', '2026-11-20')
e2 = c.last('EURUSD')[1] * c.last('USDJPY')[1]
tk('(MRO 2.65% vs BOJ 目标约 1.25%)', '2.65', 2.65, c.last('ECB_MRO')[1], 'ECB_MRO 末值', tol=T)
tk('(MRO 2.65% vs BOJ 目标约 1.25%)', '1.25', 1.25, JT['target_value'], '日历 BOJ 目标')
tk('2026-10-23 的约 175.61 降至', '175.61', 175.61, round(e0, 2), 'EURUSD×USDJPY@2026-10-23')
tk('2026-11-20 的约 175.19', '175.19', 175.19, round(e1, 2), 'EURUSD×USDJPY@2026-11-20')
tk('盘中约 174.32(-0.73%)', '174.32', 174.32, round(e2, 2), 'EURUSD×USDJPY@2026-11-23(' + str(c.last('EURUSD')[0]) + ')')
tk('盘中约 174.32(-0.73%)', '0.73', 0.73, abs(pct(e0, e2)), 'EURJPY 合成 11-23 对 10-23 变动%')
tk('推算幅度小(-0.24%/-0.73%)', '0.24', 0.24, abs(pct(e0, e1)), 'EURJPY 合成 11-20 对 10-23 变动%')
tk('推算幅度小(-0.24%/-0.73%)', '0.73', 0.73, abs(pct(e0, e2)), 'EURJPY 合成 11-23 对 10-23 变动%')
tk('交叉盘至 2026-11-20 约 -0.24%、至 2026-11-23 约 -0.73%', '0.24', 0.24, abs(pct(e0, e1)), 'EURJPY 合成 11-20 对 10-23 变动%')
tk('交叉盘至 2026-11-20 约 -0.24%、至 2026-11-23 约 -0.73%', '0.73', 0.73, abs(pct(e0, e2)), 'EURJPY 合成 11-23 对 10-23 变动%')
# ---- transmission link2 ----
v20 = c.at('VIX', '2026-11-20'); v23 = c.last('VIX')[1]
tk('2026-11-23 快照 27.01,较 2026-11-20 收盘 35.89 为 -24.7%', '27.01', 27.01, v23, 'VIX 末观测(盘中)')
tk('2026-11-23 快照 27.01,较 2026-11-20 收盘 35.89 为 -24.7%', '35.89', 35.89, v20, 'VIX@2026-11-20')
tk('2026-11-23 快照 27.01,较 2026-11-20 收盘 35.89 为 -24.7%', '24.7', 24.7, abs(pct(v20, v23)), 'VIX 27.01 对 35.89 变动%')
tk('较 2026-11-20 收盘 -24.7%,非收盘', '24.7', 24.7, abs(pct(v20, v23)), 'VIX 27.01 对 35.89 变动%')
tk('VIX +84.5% 的单月幅度(2026-11-20 收盘口径)', '84.5', 84.5, pct(c.at('VIX', '2026-10-23'), v20), 'VIX 10-23→11-20 变动%')
def ch(m):
    return abs(pct(c.at(m, '2026-10-23'), c.at(m, '2026-11-20')))
tk('(DAX -1.50%、CAC40 +1', '1.50', 1.50, ch('DAX'), 'DAX 10-23→11-20')
tk('CAC40 +1.86% vs SPX -', '1.86', 1.86, ch('CAC40'), 'CAC40 10-23→11-20')
tk('1.86% vs SPX -9.36%)', '9.36', 9.36, ch('SPX'), 'SPX 10-23→11-20')
tk('日本端与美股相当(-9.98%)', '9.98', 9.98, ch('NIKKEI225'), 'NIKKEI225 10-23→11-20')
tk('2026-11-20(19.30→35.89),距最近政策日', '19.30', 19.30, c.at('VIX', '2026-11-13'), 'VIX@2026-11-13')
tk('(19.30→35.89),距最近政策日', '35.89', 35.89, v20, 'VIX@2026-11-20')
tk('(BOJ 维持决议,无变更)14 天', '14', 14, days(JM['decision_date'], '2026-11-13'), 'days(' + JM['decision_date'] + ',2026-11-13)', tol=T)
tk('生效日 2026-09-16 58 天', '58', 58, days(chd[1][0], '2026-11-13'), 'days(2026-09-16,2026-11-13)', tol=T)
fx = [abs(dpct(m, d)) for m in ('EURUSD', 'USDJPY') for d in ('2026-11-16', '2026-11-20')]
tk('单日变动幅度不超过 0.23%', '0.23', 0.23, max(fx), 'EURUSD/USDJPY 两发布日单日变动绝对值最大值(%)', tol=0.0051)
c.diag.append('fx daily abs pct ' + str([round(x, 4) for x in fx]) + ' | eurjpy ' + str((round(e0, 4), round(e1, 4), round(e2, 4), round(pct(e0, e1), 3), round(pct(e0, e2), 3))))
c.save('g')
