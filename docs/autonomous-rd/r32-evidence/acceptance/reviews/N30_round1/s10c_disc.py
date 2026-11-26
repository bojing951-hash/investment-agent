# s10c_disc.py <snap> <rep> <cal> <reg> <aj> <out>  -- sections 10/11/12/13 + evidence refs
import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
snap, rep, cal, reg, aj, out = sys.argv[1:7]
c = Ctx(snap, rep, cal, reg, aj, out)
A = c.asof; RP = c.rep['research_plan']; RUN = c.rep['run']
n, t, e, o = c.num, c.txt, c.eq, c.ok
EA = 'EA_HICP_YOY'; JP = 'JP_CPI_YOY'; TK = 'JP_CPI_TOKYO_YOY'; PR = 'JP_POLICY_RATE'
RM_ = c.aj['reader_map']; HC = RM_['headline_conclusion']; GA = c.snap['gate_a']
W0, W1 = '2026-10-23', '2026-11-20'
def ent(eid):
    return [x for x in c.cal['entries'] if x['entry_id'] == eid][0]
JT = ent('RC-JP-BOJ-TARGET-2026-09'); JM = ent('RC-JP-BOJ-MAINT-2026-10')

# ---------- (10) headline / walk / face-off ----------
c.has_text('⑩', 'headline_conclusion', '日本与欧元区通胀与政策环境呈「方向同、水平分化、证据面不对称」')
c.has_text('⑩', 'headline_conclusion', '证据不足六项')
for k in ['日本宣布值口径序列不可得(注册表无 JP_POLICY_TARGET)', '欧央行序列止于 2026-09-16', '通胀公布时间均为推定规则非实录', '事后回顾修订口径', '增长与核心通胀背景对照缺席', '两地国债收益率期限结构对照不对称']:
    c.has_text('⑩', 'headline 六项与 C3 ①–⑥ 同题', k)
for k in ['①日本政策目标宣布值口径不可得', '②欧央行序列止于最近一次变更日', '③本窗月度通胀读数的公布时间为推定规则非实录', '④欧元区 HICP 与日本全国 CPI 月度数值为事后回顾口径', '⑤增长与核心通胀背景对照缺席', '⑥两地国债收益率期限结构对照不对称']:
    c.has_text('⑩', 'C3 六项编号在场', k)
c.has_text('⑩', 'C3 「引擎可核者六项」', '引擎可核者六项')
n('⑩', 'headline JP target_value (calendar)', JT['target_value'], 1.25, '1.25', '日本央行目标 1.25%(2026-09-18 决议、2026-09-24 生效,2026-10-30 确认维持;发布日历实录)')
t('⑩', 'headline JP decision_date', JT['decision_date'], '2026-09-18', '2026-09-18', '日本央行目标 1.25%(2026-09-18 决议')
t('⑩', 'headline JP effective_on', JT['effective_on'], '2026-09-24', '2026-09-24', '2026-09-24 生效,2026-10-30 确认维持')
t('⑩', 'headline JP maintenance decision_date', JM['decision_date'], '2026-10-30', '2026-10-30', '2026-10-30 确认维持;发布日历实录)')
n('⑩', 'headline ECB_MRO last', c.last('ECB_MRO')[1], 2.65, '2.65', '后主要再融资利率 2.65%/存款便利利率 2.5%')
n('⑩', 'headline ECB_DFR last', c.last('ECB_DFR')[1], 2.5, '2.5', '2.65%/存款便利利率 2.5%')
n('⑩', 'headline JP_POLICY_RATE 6m anchor', c.mv(PR, '2026-04'), 0.727, '0.727', '月均口径六个月锚间由 0.727 升至 1.227')
n('⑩', 'headline JP_POLICY_RATE latest', c.mv(PR, '2026-10'), 1.227, '1.227', '由 0.727 升至 1.227')
n('⑩', 'headline EA 2025-10', c.mv(EA, '2025-10'), 2.1, '2.1', '欧元区高于去年同月(2025-10 为 2.1)')
n('⑩', 'headline JP 2025-10', c.mv(JP, '2025-10'), 2.99, '2.99', '日本低于去年同月(2025-10 为 2.99)')
n('⑩', 'headline EA latest', c.mv(EA, '2026-10'), 4.0, '4.0', '欧元区 HICP 同比 4.0%(观测 2026-10,发布 2026-11-16,推定规则)')
n('⑩', 'headline JP latest', c.mv(JP, '2026-10'), 2.44, '2.44', '日本全国 CPI 同比 2.44%(观测 2026-10,发布 2026-11-20,推定规则)')
o('⑩', 'headline 方向词: EA 同比上升(4.0>2.1)、JP 同比下降(2.44<2.99)', c.mv(EA, '2026-10') > c.mv(EA, '2025-10') and c.mv(JP, '2026-10') < c.mv(JP, '2025-10'), 'ok')
o('⑩', 'headline 方向词: 两地通胀均上行(六个月锚间)', c.mv(EA, '2026-10') > c.mv(EA, '2026-04') and c.mv(JP, '2026-10') > c.mv(JP, '2026-04'), (c.mv(EA, '2026-04'), c.mv(JP, '2026-04')))
o('⑩', 'headline 方向词: 政策均收紧(ECB DFR 2.0→2.5; JP 月均 0.727→1.227; JP 目标实录无前值)', c.last('ECB_DFR')[1] > 2.0 and c.mv(PR, '2026-10') > c.mv(PR, '2026-04'), (c.last('ECB_DFR')[1], c.mv(PR, '2026-10')))
o('⑩', 'headline「欧央行宣布值口径两次合计五十个基点」=2×25bp', round((c.last('ECB_MRO')[1] - c.mv('ECB_MRO', '2025-06')) * 100) == 50 and round((c.last('ECB_DFR')[1] - c.mv('ECB_DFR', '2025-06')) * 100) == 50, (round((c.last('ECB_MRO')[1] - c.mv('ECB_MRO', '2025-06')) * 100), round((c.last('ECB_DFR')[1] - c.mv('ECB_DFR', '2025-06')) * 100)))
o('⑩', 'headline「日本月均口径六个月锚间净变动约五十个基点」', round((c.mv(PR, '2026-10') - c.mv(PR, '2026-04')) * 100) == 50, round((c.mv(PR, '2026-10') - c.mv(PR, '2026-04')) * 100, 2))
c.has_text('⑩', 'headline「距截止 六十八 天」', '距截止 六十八 天,Gate A 列 degraded')
c.has_text('⑩', 'headline 回看窗', '窗起 2026-05-23 至研究截止 2026-11-23')
c.has_text('⑩', 'headline 请求月末未到', '问句请求月末 2026-11-30 未到,研究截止取实际覆盖日 2026-11-23')
TR = RM_['transmission'][0]['links']; ML = c.aj['l3']['mechanism_chains'][0]['links']
e('⑩', 'transmission 三环 face_off_verdict', [x['face_off_verdict'] for x in TR], ['尚不能区分'] * 3)
e('⑩', 'transmission 环数', len(TR), 3)
e('⑩', 'transmission 各环字段齐备', all(all(k in x for k in ('observed_fact', 'causal_hypothesis', 'competing_explanation', 'distinguishing_metric', 'main_predicts', 'competing_predicts', 'face_off_verdict', 'verdict_note')) for x in TR), True)
e('⑩', 'transmission distinguishing_metric', [x['distinguishing_metric'] for x in TR], ['EA_HICP_YOY', 'EURUSD', 'VIX'])
EIM = {x['ref']: x for x in c.rep['evidence_index']}
o('⑩', '区分指标在证据索引在场(EA_HICP_YOY/EURUSD/VIX)', all(any(r.startswith(m + '@') for r in EIM) for m in ['EA_HICP_YOY', 'EURUSD', 'VIX']), 'ok')
e('⑩', 'l3.contradictions 条数', len(c.aj['l3']['contradictions']), 3)
e('⑩', 'l3.mechanism_chains 条数', len(c.aj['l3']['mechanism_chains']), 1)
e('⑩', '每条矛盾陈述 2 条竞争解释', [len(x['competing_explanations']) for x in c.aj['l3']['contradictions']], [2, 2, 2])
o('⑩', '矛盾陈述竞争解释均以【假设】起头', all(y.startswith('【假设】') for x in c.aj['l3']['contradictions'] for y in x['competing_explanations']), 'ok')
e('⑦', 'M1 四环 evidence_level', [x['evidence_level'] for x in ML], ['E1', 'E1', 'E2', 'E2'])
o('⑦', 'E2 环3 以「传导【假设】」起头,含【假设】标注与「尚不能区分」', ML[2]['text'].startswith('传导【假设】') and '尚不能区分' in ML[2]['text'], ML[2]['text'][:10])
o('⑦', 'E2 环4 归因句带【假设·归因】且结论「单一归因于两地政策不可证」', ML[3]['text'].count('【假设·归因】') >= 2 and '单一归因于两地政策不可证' in ML[3]['text'], ML[3]['text'].count('【假设·归因】'))
o('⑦', '传导三环 causal_hypothesis/competing_explanation 均以【假设】起头(非事实位措辞)', all(x['causal_hypothesis'].startswith('【假设】') and x['competing_explanation'].startswith('【假设】') for x in TR), 'ok')
o('⑦', 'E2 环均有 missing_link_note', all('missing_link_note' in x and x['missing_link_note'] for x in ML[2:]), [x['missing_link_note'][:30] for x in ML[2:]])
o('⑦', '对质表「尚不能区分」与各行观测一致: 环1 n=2 且反向观察在场; 环2 预期未分立; 环3 仅一个盘中回落观测', all(x['face_off_verdict'] == '尚不能区分' for x in TR) and 'n=2' in TR[0]['verdict_note'] and '预期未分立' in TR[1]['verdict_note'] and '仅有一个盘中观测' in TR[2]['verdict_note'], 'ok')
e('⑩', '情景条数/各环五行齐备', (len(c.aj['l4']['scenarios']), all(all(k in x['rows'] for k in ('scenario', 'asset_direction', 'sensitive_variables', 'falsification', 'trigger')) for x in c.aj['l4']['scenarios'])), (2, True))
e('⑩', 'S1/S2 sensitive_variables', [x['rows']['sensitive_variables'] for x in c.aj['l4']['scenarios']], [['EA_HICP_YOY', 'JP_CPI_YOY']] * 2)
e('⑩', 'S1/S2 confidence_tier', [x['rows']['asset_direction']['confidence_tier'] for x in c.aj['l4']['scenarios']], ['有相关证据', '纯逻辑推理'])
c.save('c')
