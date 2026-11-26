# s10d_gap.py <snap> <rep> <cal> <reg> <aj> <out>  -- sections 11/12/13 + refs + diag for 14/13'
import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
snap, rep, cal, reg, aj, out = sys.argv[1:7]
c = Ctx(snap, rep, cal, reg, aj, out)
A = c.asof; RP = c.rep['research_plan']; RUN = c.rep['run']
n, t, e, o = c.num, c.txt, c.eq, c.ok
EA = 'EA_HICP_YOY'; JP = 'JP_CPI_YOY'; TK = 'JP_CPI_TOKYO_YOY'; PR = 'JP_POLICY_RATE'
RM_ = c.aj['reader_map']; GA = c.snap['gate_a']
W0, W1 = '2026-10-23', '2026-11-20'
def ent(eid):
    return [x for x in c.cal['entries'] if x['entry_id'] == eid][0]
JT = ent('RC-JP-BOJ-TARGET-2026-09'); JM = ent('RC-JP-BOJ-MAINT-2026-10')
def det(m):
    d = GA.get('noncore_missing_detail')
    if isinstance(d, dict):
        return str(d.get(m, ''))
    for x in (d or []):
        if m in json.dumps(x, ensure_ascii=False):
            return json.dumps(x, ensure_ascii=False)
    return ''
# ---------- (11) honest absences ----------
NM = GA['noncore_missing']
e('⑪', 'gate_a.status', GA['status'], 'DEGRADED')
c.has_text('⑪', '判断档文字(Gate A 降级披露)', '当日快照 Gate A 将该两序列列于降级名单')
for m in ['BUND_10Y', 'BUND_2Y', 'EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY', 'JP_CPI_TOKYO_YOY']:
    e('⑪', 'gate_a.noncore_missing 含 ' + m, m in NM, True)
    e('⑪', 'facts 无 ' + m + ' 行', c.fact(m), None)
e('⑪', 'series_store 无 BUND_10Y/BUND_2Y', [m in c.S for m in ('BUND_10Y', 'BUND_2Y')], [False, False])
e('⑪', 'series_store 有 EA/JP GDP 与东京序列', [m in c.S for m in ('EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY', 'JP_CPI_TOKYO_YOY')], [True, True, True])
for m, v in [('EA_REAL_GDP_YOY', 1.28), ('JP_REAL_GDP_YOY', 1.16)]:
    e('⑪', 'series_store.' + m + ' 末观测', c.last(m), ('2026-07-01', v))
c.has_text('⑪', '判断档文字: GDP 序列面至 2026-07', '序列面存有至 2026-07 期读数(欧元区一点二八、日本一点一六),按 Gate A 不取用')
c.has_text('⑪', '判断档文字: GDP 缺席', 'EA_REAL_GDP_YOY、JP_REAL_GDP_YOY 在册,但当日快照 Gate A 列于缺席名单(事实行缺席,注记=采集器已取到而事实未生成')
c.diag.append('noncore_missing_detail 类型: ' + type(GA.get('noncore_missing_detail')).__name__)
o('⑪', 'missing_detail: 东京=来源文件在场而指标缺席', '来源文件在场而指标缺席' in det('JP_CPI_TOKYO_YOY'), det('JP_CPI_TOKYO_YOY')[:90])
o('⑪', 'missing_detail: BUND=子源缺席、非采集遗漏', all('子源缺席' in det(m) and '非采集遗漏' in det(m) for m in ('BUND_10Y', 'BUND_2Y')), det('BUND_10Y')[:90])
o('⑪', 'missing_detail: EA/JP GDP=采集器已取到而事实未生成', all('采集器已取到而事实未生成' in det(m) for m in ('EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY')), det('EA_REAL_GDP_YOY')[:90])
c.has_text('⑪', '判断档文字: BUND 注记', 'BUND_10Y、BUND_2Y 在册,当日快照 Gate A 列于缺席名单(子源缺席,源端不可得或未采,非采集遗漏)')
c.has_text('⑪', '判断档文字: 东京都注记', '该序列在当日快照 Gate A 列于 noncore_missing(来源文件在场而指标缺席)')
for m, v in [('JGB2Y', 1.853), ('JGB5Y', 2.235), ('JGB10Y', 2.87)]:
    f = c.fact(m)
    e('⑪', 'facts.' + m + ' value/observation_date/quality_status', (f['value'], f['observation_date'], f['quality_status']), (v, '2026-11-19', 'PASS'))
    e('⑪', 'series_store 无 ' + m, m in c.S, False)
c.has_text('⑪', '判断档文字: JGB 三值', '2026-11-19 为 1.853、2.235、2.87,质量状态 PASS')
EIM = {x['ref']: x for x in c.rep['evidence_index']}
for m in ['BUND_10Y', 'BUND_2Y', 'JGB2Y', 'JGB5Y', 'JGB10Y']:
    o('⑪', '证据索引不含 ' + m, not any(r.startswith(m + '@') for r in EIM), m)
c.has_text('⑪', '判断档文字: 五条序列均不在本问证据索引', '但五条序列均不在本问证据索引')
o('⑪', '注册表 JP/EA 面无核心通胀序列', not any(('CORE' in k.upper()) and c.RM[k].get('economy') in ('JP', 'EA') for k in c.RM), [k for k in c.RM if 'CORE' in k.upper() and c.RM[k].get('economy') in ('JP', 'EA')])
c.has_text('⑪', '判断档文字: 注册表无两地核心通胀序列', '注册表无两地核心通胀序列(检索范围=注册表 economy=JP/EA 面)')
o('⑪', '注册表无 JP_POLICY_TARGET 且 series_store 无', 'JP_POLICY_TARGET' not in c.RM and 'JP_POLICY_TARGET' not in c.S, 'ok')
c.has_text('⑪', '判断档文字: 注册表无 JP_POLICY_TARGET', '注册表无 JP_POLICY_TARGET(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)')
e('⑪', '注册表 JP 通胀面指标', sorted(k for k in c.RM if c.RM[k].get('economy') == 'JP' and 'CPI' in k), ['JP_CPI_TOKYO_YOY', 'JP_CPI_YOY'])
JPE = [x for x in c.cal['entries'] if x['entry_id'].startswith('RC-JP')]
EAE = [x for x in c.cal['entries'] if x.get('metric_id') == 'EA_HICP_YOY']
e('⑪', '日历 JP 条目数', len(JPE), 2)
e('⑪', '日历 ECB 条目数', len([x for x in c.cal['entries'] if 'ECB' in x['entry_id'].upper() or x.get('metric_id') in ('ECB_MRO', 'ECB_DFR')]), 0)
e('⑪', '日历 EA HICP 条目数/观测月', (len(EAE), sorted(x['obs_from'][:7] for x in EAE)), (3, ['2021-05', '2022-06', '2025-03']))
c.has_text('⑪', '判断档文字: 日历日欧面覆盖', '冻结日历实录于日欧面仅覆盖日本政策目标两条与三条历史期 EA HICP 快报/终值实录,观测月 2021-05、2022-06、2025-03,均不覆盖本窗月份')
e('⑪', 'JP target entry basis/decision/effective/target', (JT['basis'], JT['decision_date'], JT['effective_on'], JT['target_value']), ('user_directive', '2026-09-18', '2026-09-24', 1.25))
e('⑪', 'JP maint entry basis/decision/kind', (JM['basis'], JM['decision_date'], JM['kind']), ('user_directive', '2026-10-30', 'policy_maintenance'))
o('⑪', 'JP target entry 无前值字段', not any(k in JT for k in ('previous_value', 'prev_value', 'prior_value', 'from_value', 'old_value')), sorted(JT.keys()))
c.has_text('⑪', '判断档文字: 均 user_directive', '均 user_directive 基础')
e('⑪', '日历 version/updated', (c.cal['version'], c.cal['updated']), ('1.5.0', '2026-11-21'))
c.has_text('⑪', '判断档文字: v1.5.0', '发布日历实录(v1.5.0,2026-11-21 更新)')
e('⑪', 'noncore_degraded 含 ECB_DFR/ECB_MRO', [m in GA['noncore_degraded'] for m in ('ECB_DFR', 'ECB_MRO')], [True, True])
for m in ('ECB_MRO', 'ECB_DFR'):
    e('⑪', 'facts.' + m + ' quality_status', c.fact(m)['quality_status'], 'DEGRADED')
    e('⑪', 'facts.' + m + ' observation_date', c.fact(m)['observation_date'], '2026-09-16')
    e('⑪', 'series_store.' + m + ' 末观测日', c.last(m)[0], '2026-09-16')
c.has_text('⑪', '判断档文字: L1 事实行 quality_status=DEGRADED', 'L1 事实行 quality_status=DEGRADED')
o('⑪', 'Gate A 注记「不得进入研究结论」在场', '不得进入研究结论' in GA.get('note', ''), GA.get('note', '')[:90])
for m in ('JP_CPI_YOY', 'EA_HICP_YOY'):
    f = c.fact(m)
    e('⑪', 'facts.' + m + ' quality_status', f['quality_status'], 'WARN')
    e('⑪', 'facts.' + m + ' issues 类别', sorted(set(i['category'] for i in f['issues'])), ['release'])
c.has_text('⑪', '判断档文字: WARN 与 WARN', '两条全国/全区最新读数 L1 quality_status 分别为 WARN 与 WARN')
# ---------- (12) cutoff-day intraday ----------
e('⑫', 'snapshot.research_as_of', c.snap['research_as_of'], '2026-11-23T22:53:47+08:00')
c.has_text('⑫', '判断档文字: 采集时点', '快照采集于 2026-11-23T22:53:47+08:00(纽约 09:53、柏林 15:53、东京 23:53、上海 22:53)')
for m in ['SPX', 'VIX', 'DAX', 'CAC40', 'EURUSD', 'USDJPY', 'DXY']:
    e('⑫', 'series_store.' + m + ' 末观测日=截止日', c.last(m)[0], A)
e('⑫', 'series_store.NIKKEI225 末观测日', c.last('NIKKEI225')[0], W1)
c.has_text('⑫', '判断档文字: 盘中非收盘', 'SPX/VIX/DAX/CAC40 的截止日值与外汇/DXY 值均为盘中快照、非收盘价')
c.has_text('⑫', '判断档文字: 统一 11-20 同日收盘口径', '席位跨地区对照统一采用 2026-11-20 同日收盘口径')
o('⑫', '2026-11-20 为周五', wd(W1) == '周五', wd(W1))
o('⑫', '2026-11-23 为周一', wd(A) == '周一', wd(A))
o('⑫', 'SPX/VIX/DAX/CAC40 在 11-20 后、11-23 前无观测', all(not any(W1 < d < A for d in c.S[m]['dates']) for m in ['SPX', 'VIX', 'DAX', 'CAC40']), 'ok')
c.has_text('⑫', 'C2 文字: 均为 2026-11-23 盘中快照、非收盘价', '均为 2026-11-23 盘中快照、非收盘价')
e('⑫', 'C2 引用三值 USDJPY/SPX/VIX@11-23 (四舍五入 2 位)', (round(c.at('USDJPY', A), 2), round(c.at('SPX', A), 2), round(c.at('VIX', A), 2)), (159.35, 7203.85, 27.01))
e('⑫', 'facts USDJPY/SPX/VIX@11-23 值', (c.fact('USDJPY')['value'], c.fact('SPX')['value'], c.fact('VIX')['value']), (159.35, 7203.85, 27.01))
e('⑫', 'facts USDJPY/SPX/VIX 观测日', (c.fact('USDJPY')['observation_date'], c.fact('SPX')['observation_date'], c.fact('VIX')['observation_date']), (A, A, A))
e('⑫', 'M1 环3 USDJPY@11-23 三位小数 159.347 / EURUSD 1.0940 / DXY 104.079', (round(c.at('USDJPY', A), 3), round(c.at('EURUSD', A), 4), round(c.at('DXY', A), 3)), (159.347, 1.094, 104.079))
e('⑫', 'M1 环3 DXY/EURUSD 窗起值 101.81 / 1.1221', (round(c.at('DXY', W0), 2), round(c.at('EURUSD', W0), 4)), (101.81, 1.1221))
e('⑫', 'M1 环3 至 11-20 收盘 EURUSD 1.0970 / USDJPY 159.707 / DXY 103.81', (round(c.at('EURUSD', W1), 4), round(c.at('USDJPY', W1), 3), round(c.at('DXY', W1), 2)), (1.097, 159.707, 103.81))
e('⑫', 'M1 环3 窗起 USDJPY 156.494', round(c.at('USDJPY', W0), 3), 156.494)
# ---------- (13) contract + evidence refs ----------
CV = c.rep['agent_judgment']['contract_verification']
e('⑬', 'contract_verification.verdict', CV['verdict'], 'VERIFIED')
VS = CV['verdicts']
c.diag.append('contract verdicts: ' + json.dumps(VS, ensure_ascii=False)[:1200])
ST = [v for v in VS if v.get('status') != 'VERIFIED']
e('⑬', '契约非 VERIFIED 项数', len(ST), 1)
e('⑬', '契约非 VERIFIED 项指标', [v.get('metric') for v in ST], ['ECB_DFR'])
e('⑬', '契约 verdicts 总数', len(VS), 5)
e('⑬', 'STALE 项 token/value/expected', (ST[0].get('token'), ST[0].get('value'), ST[0].get('expected')), ('2.5%', 2.5, 2.5))
o('⑬', 'STALE 项 note=Fact 直读 ECB_DFR@2026-09-16=2.5 与快照一致', ST[0].get('note') == 'recompute:Fact 直读 ECB_DFR@2026-09-16=2.5' and c.fact('ECB_DFR')['value'] == 2.5, ST[0].get('note'))
e('⑬', '其余 VERIFIED 项 metric/token', [(v.get('metric'), v.get('token')) for v in VS if v.get('status') == 'VERIFIED'], [('JP_POLICY_RATE', '1.227%'), ('USDJPY', '159.35'), ('SPX', '7203.85'), ('VIX', '27.01')])
c.diag.append('agent_judgment 其他键: ' + json.dumps({k: v for k, v in c.rep['agent_judgment'].items() if k not in ('contract_verification',)}, ensure_ascii=False)[:900])
c.diag.append('AJ validation 域: ' + json.dumps({k: v for k, v in c.aj.items() if k not in ('l3', 'l4', 'reader_map', 'quality_gate_notes', 'agent_declaration')}, ensure_ascii=False)[:1500])
c.diag.append('rep.notes: ' + json.dumps(c.rep.get('notes'), ensure_ascii=False)[:1200])
c.diag.append('semantic_review: ' + json.dumps(c.rep.get('semantic_review'), ensure_ascii=False)[:600])
c.diag.append('run_ok/pipeline_version: ' + str((c.rep.get('run_ok'), c.rep.get('pipeline_version'))))
c.diag.append('run.question: ' + str(RUN.get('question'))[:300])
c.diag.append('frozen_inputs: ' + json.dumps(RUN.get('frozen_inputs'), ensure_ascii=False)[:900])
c.has_text('⑬', '判断档文字: STALE 披露', '引擎契约验证对本档水平对照所引存款便利利率数值串记状态 STALE——数值一致、观测滞后六十八天')
o('⑬', '「观测滞后六十八天」= days(2026-09-16→2026-11-23)', days('2026-09-16', A) == 68, days('2026-09-16', A))
refs = []
for x in c.aj['l3']['contradictions']:
    refs += [(x['id'], r) for r in x['evidence_refs']]
ML = c.aj['l3']['mechanism_chains'][0]['links']
for i, lk in enumerate(ML):
    refs += [('M1/link' + str(i), r) for r in lk['evidence_refs']]
e('⑬', 'L3 引用总数', len(refs), 21)
e('⑬', '矛盾陈述引用数', [len(x['evidence_refs']) for x in c.aj['l3']['contradictions']], [2, 6, 3])
e('⑬', '机制链各环引用数', [len(x['evidence_refs']) for x in ML], [2, 2, 2, 4])
o('⑬', '21 条引用全部在证据索引且 kind=snapshot_fact', all(r in EIM and EIM[r].get('kind') == 'snapshot_fact' for _, r in refs), [(w, r) for w, r in refs if r not in EIM or EIM[r].get('kind') != 'snapshot_fact'])
c.has_text('⑬', '判断档文字: 21 条', '三条矛盾陈述+机制链四环共 21 条 snapshot_fact 引用,全部解析到本报告证据索引;零悬空引用')
c.has_text('⑬', '判断档文字: 对质计数', '支持主解释 0·支持竞争解释 0·尚不能区分 3')
def allrefs(o, path=''):
    res = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k == 'evidence_refs' and isinstance(v, list):
                res += [(path + '.' + k, x) for x in v]
            else:
                res += allrefs(v, path + '.' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            res += allrefs(v, path + '[' + str(i) + ']')
    return res
AR = allrefs(c.aj)
e('⑬', '判断档全部 evidence_refs 数(含情景)', len(AR), 25)
o('⑬', '全部 evidence_refs 均在证据索引', all(r in EIM for _, r in AR), [r for _, r in AR if r not in EIM])
c.diag.append('evidence_index row0: ' + json.dumps(c.rep['evidence_index'][0], ensure_ascii=False)[:500])
bad = []
for r, x in EIM.items():
    m, d = r.split('@')
    if m in c.S and d in c.S[m]['dates'] and 'value' in x:
        if not close(x['value'], c.at(m, d), tol=1e-6):
            bad.append((r, x['value'], c.at(m, d)))
o('⑬', '证据索引各行 value 与 series_store 同日值一致(在序列面者)', not bad, bad[:6])
c.diag.append('evidence_index kinds: ' + str(sorted(set(str(x.get('kind')) for x in c.rep['evidence_index']))))
c.diag.append('evidence_index 指标集: ' + str(sorted(set(r.split('@')[0] for r in EIM))))
# ---------- diag for (14) / (13') ----------
c.diag.append('run.evidence_gate: ' + json.dumps(RUN.get('evidence_gate'), ensure_ascii=False)[:1000])
c.diag.append('run keys: ' + str(list(RUN.keys())))
c.diag.append('RP.as_of_declared: ' + json.dumps(RP.get('as_of_declared'), ensure_ascii=False)[:700])
c.diag.append('RP.cutoff: ' + json.dumps(RP.get('cutoff'), ensure_ascii=False)[:700])
c.diag.append('RP.question_window: ' + json.dumps(RP.get('question_window'), ensure_ascii=False)[:1300])
c.diag.append('RP.point_values.absent: ' + json.dumps(RP['point_values'].get('absent'), ensure_ascii=False)[:500])
c.diag.append('RP.dimension_gaps: ' + json.dumps(RP.get('dimension_gaps'), ensure_ascii=False)[:900])
c.diag.append('top keys: ' + str(list(c.rep.keys())))
c.diag.append('AJ l4 keys: ' + str(list(c.aj['l4'].keys())))
DR = RUN['data_requirements']['items']
c.diag.append('data_requirements items(ECB): ' + json.dumps([x for x in DR if x['metric_id'] in ('ECB_MRO', 'ECB_DFR')], ensure_ascii=False)[:1700])
c.diag.append('data_requirements items 概览: ' + json.dumps([(x['metric_id'], x.get('tier'), x.get('outcome')) for x in DR], ensure_ascii=False)[:2500])
c.save('d')
