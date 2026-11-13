#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R25: R24 审计 3 NIT 收口 + DFF 日频史接线回归锁。

  §1 NIT V1-1: report.md 步骤台账语义标签按步骤性质三分——
     信封步(semantic_ok 在场)语义✔/✗/诚实拒答;编排内部步(无信封键)
     「不适用」;未执行「—」。方向保守: FAIL 不藏(进程面 tag 照渲)。
  §2 NIT V1-2: attach blocked 路径(run_ok_false)同样重渲 report.md——
     md/json 两视图同步是 attach 不变式(旧 md 不再滞留拦截前状态)。
  §3 NIT V2-5: falsification 增可选 secondary_metric_ids(schema v1.1)——
     复合证伪条件副指标机器锚;缺席不违规(单指标);1-3 条逐条在册;
     非法形态显式拒收。
  §4 DFF 日频史接线(R23 E2E S4_history_DFF 诚实 FAIL 根治的离线面):
     registry v2.8.5 history_source 字段+macro_collector 接线+
     normalize_macro 事实权威门(防双通道双事实)+rhq/wd 历史通道解析。
     网络面(真实拉取)=操作者轮,本套件全离线(合成 macro 档)。

全合成报告/档面;真实 registry;CI 干净 clone 可跑。
"""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f'  ✅ {name}')
    else:
        FAIL += 1
        print(f'  ❌ {name} {detail}')


def section(title):
    print('═' * 64)
    print(f'[{title}]')
    print('═' * 64)


import workbench_data as wd            # noqa: E402
import agent_judgment as aj            # noqa: E402
import research_orchestrator as ro     # noqa: E402
import research_history_query as rhq   # noqa: E402
import fact_engine as fe               # noqa: E402
import snapshot_builder as sb          # noqa: E402
import macro_collector as mc           # noqa: E402

REG = wd.load_registry(ROOT)
REG_JSON = json.load(open(os.path.join(ROOT, 'config', 'metric_registry.json'),
                          encoding='utf-8'))
MIDS = sorted({m['metric_id'] for m in (REG.get('metrics') or [])
               if m.get('metric_id')})
MID_A, MID_B = MIDS[0], MIDS[1]
EV_REFS = {'FACT_A@2026-01-10', 'FACT_B@2026-01-10', 'VP-VIEW-20260101-001'}


def base_judgment():
    """合规 judgment 母本(schema v1.1;与 R24 套件同构)。"""
    return {
        'schema_version': '1.1',
        'agent_declaration': {'attribution': 'ai_inferred',
                              'note': '编排层 Agent 研判'},
        'l3': {
            'contradictions': [{
                'id': 'CON-1',
                'statement': '合成矛盾陈述(测试母本)',
                'basis': '基于证据索引的推断',
                'competing_explanations': ['解释一(基准)', '解释二(反例)'],
                'evidence_refs': ['FACT_A@2026-01-10',
                                  'VP-VIEW-20260101-001']}],
            'mechanism_chains': [{
                'id': 'MECH-1', 'name': '合成链',
                'links': [
                    {'step': 1, 'text': 'E1 环(引擎可验证)',
                     'evidence_level': 'E1',
                     'evidence_refs': ['FACT_A@2026-01-10']},
                    {'step': 3, 'text': 'E3 环(纯叙事)',
                     'evidence_level': 'E3',
                     'falsification_metric': MID_A}]}]},
        'l4': {
            'scenarios': [
                {'id': 'SCN-A', 'role': '基准', 'rows': {
                    'scenario': '情景A(假设非预测): 合成基准情景',
                    'asset_direction': {'direction': '上行',
                                        'confidence_tier': '有相关证据',
                                        'text': '合成方向判断',
                                        'evidence_refs': ['FACT_A@2026-01-10']},
                    'sensitive_variables': [MID_A],
                    'falsification': {'metric_id': MID_B,
                                      'threshold': '突破合成阈值 X'},
                    'trigger': {'condition': '合成可观测条件',
                                'deadline': '2027-06-30'}}},
                {'id': 'SCN-B', 'role': '反例', 'rows': {
                    'scenario': '情景B(假设非预测): 合成反例情景',
                    'asset_direction': {'direction': '区间',
                                        'confidence_tier': '纯逻辑推理',
                                        'text': '合成反例方向',
                                        'evidence_refs': []},
                    'sensitive_variables': [MID_B],
                    'falsification': {'metric_id': MID_A,
                                      'threshold': '跌破合成阈值 Y'},
                    'trigger': {'condition': '合成反例条件',
                                'deadline': '2027-06-30'}}}]},
    }


def codes(res):
    return {x['code'] for x in res['violations']}


def synth_report(run_ok=True):
    return {
        'schema_version': '2.0', 'pipeline_version': ro.PIPELINE_VERSION,
        'run': {'question': '合成问题', 'ts_utc': '20260101T000000Z',
                'archive_requested': False, 'git_head': None},
        'steps': [], 'fanout': {'requested': False},
        'layers': {
            'L1_事实层': {'available': True, 'snapshot_id': 'SYNTH',
                          'target_date': '2026-01-10', 'n_facts_total': 2,
                          'rows': [], 'note': None},
            'L2_机构观点层': {'views': {'available': True, 'n': 1, 'rows': [],
                                        'n_bad_quarantined': 0}, 'note': '合成'},
            'L3_AI推断层': {'produced': False, 'note': '零模型管线: 不代写'},
            'L4_条件情景层': {'produced': False, 'note': '零模型管线: 不代写'}},
        'evidence_index': [
            {'ref': 'FACT_A@2026-01-10', 'kind': 'snapshot_fact',
             'metric_id': MID_A},
            {'ref': 'FACT_B@2026-01-10', 'kind': 'snapshot_fact',
             'metric_id': MID_B},
            {'ref': 'VP-VIEW-20260101-001', 'kind': 'vp_sidecar',
             'view_label': '合成观点'}],
        'notes': [], 'run_ok': run_ok}


def ledger_line(step):
    """从 _render_md 提取该步骤的台账行(步骤台账节)。"""
    md = ro._render_md({'schema_version': '2.0',
                        'pipeline_version': ro.PIPELINE_VERSION,
                        'run': {'question': 'q', 'ts_utc': 'x',
                                'archive_requested': False, 'git_head': None},
                        'steps': [step], 'fanout': {'requested': False},
                        'layers': synth_report()['layers'],
                        'evidence_index': [], 'notes': [], 'run_ok': True})
    for ln in md.splitlines():
        if ln.startswith(f"- [") and step['step'] in ln:
            return ln
    return ''


# ══════════════════════════════════════════════════════════════════
section('1 NIT V1-1 步骤台账语义标签三分(信封步/非信封步/未执行)')
# ══════════════════════════════════════════════════════════════════
internal = {'step': 'S1_decompose', 'executed': True, 'ok': True,
            'deterministic_face': {}, 'agent_face_note': '合成'}
ln = ledger_line(internal)
check('编排内部步(无信封键,ok=True)渲「不适用」(旧: 恒「语义✗」噪音)',
      '|不适用]' in ln, ln)
check('内部步「不适用」不混入语义✗/✔',
      '语义✗' not in ln and '语义✔' not in ln, ln)

env_ok = {'step': 'S2_doctor', 'executed': True, 'ok': True,
          'semantic_ok': True, 'envelope': {'ok': True}}
ln = ledger_line(env_ok)
check('信封步 semantic_ok=True 渲「语义✔」(原行为保持)',
      '|语义✔]' in ln, ln)

env_bad = {'step': 'S3_changes', 'executed': True, 'ok': True,
           'semantic_ok': False, 'envelope': {'ok': False}}
ln = ledger_line(env_bad)
check('信封步 semantic_ok=False 渲「语义✗」(失败不藏)',
      '|语义✗]' in ln, ln)

env_ref = {'step': 'S6_analog', 'executed': True, 'ok': False,
           'semantic_ok': False, 'honest_refusal': True,
           'envelope': {'ok': False}}
ln = ledger_line(env_ref)
check('信封步 honest_refusal 渲「诚实拒答」(原行为保持)',
      '|诚实拒答]' in ln, ln)

skip = {'step': 'S4_history', 'executed': False, 'ok': True,
        'skipped_reason': '合成跳过', 'envelope': None}
ln = ledger_line(skip)
check('未执行步渲「—」(原行为保持)', '|—]' in ln, ln)

# 保守面: 超时/启动失败步(_run_proc 无 semantic_ok 键,ok=False)——
# 进程面 FAIL 照渲,语义面「不适用」(无信封可判语义,不再误标语义✗)
crash = {'step': 'S5_compare', 'executed': True, 'ok': False,
         'exit_code': None, 'note': '超时(>180s)', 'envelope': None}
ln = ledger_line(crash)
check('超时/启动失败步: FAIL tag 照渲+语义「不适用」(失败不藏)',
      ln.startswith('- [FAIL|不适用]'), ln)

# ══════════════════════════════════════════════════════════════════
section('2 NIT V1-2 blocked 路径 md/json 两视图同步')
# ══════════════════════════════════════════════════════════════════
tmp = tempfile.mkdtemp(prefix='r25n2-')
try:
    rd = os.path.join(tmp, 'run')
    os.makedirs(rd)
    rep = synth_report(run_ok=False)
    with open(os.path.join(rd, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    stale_md = '# STALE MD(拦截前旧视图)\n'
    with open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(stale_md)
    jp = os.path.join(tmp, 'judgment.json')
    with open(jp, 'w', encoding='utf-8') as f:
        json.dump(base_judgment(), f, ensure_ascii=False, indent=2)
    res = aj.attach_judgment(rd, jp, root=ROOT)
    check('run_ok=False 默认 blocked(MINOR-4 原行为保持)',
          res['attached'] is False and res['blocked'] == 'run_ok_false')
    with open(os.path.join(rd, 'report.json'), encoding='utf-8') as f:
        rep2 = json.load(f)
    check('blocked 拦截记录已随 report.json 落档',
          rep2.get('agent_judgment', {}).get('blocked') == 'run_ok_false')
    with open(os.path.join(rd, 'report.md'), encoding='utf-8') as f:
        md_now = f.read()
    check('blocked 路径重渲 report.md(旧: 滞留拦截前旧视图)',
          md_now != stale_md and md_now == ro._render_md(rep2))
    # R25 审计 Mi-1: agent_judgment 面入 md——md-only 读者可见拦截
    check('Mi-1: md 渲 blocked 拦截节(门槛拦截可见)',
          '## Agent 判断落位: 未落位(门槛拦截)' in md_now
          and 'blocked=run_ok_false' in md_now, md_now[-400:])
    check('blocked 后 L3/L4 仍 produced=False(不半落位)',
          rep2['layers']['L3_AI推断层']['produced'] is False
          and rep2['layers']['L4_条件情景层']['produced'] is False)
    # Mi-1 对侧面: 成功 attach 后 md 渲 attached 节
    rep3 = synth_report(run_ok=True)
    rd2 = os.path.join(tmp, 'run2')
    os.makedirs(rd2)
    with open(os.path.join(rd2, 'report.json'), 'w', encoding='utf-8') as f:
        json.dump(rep3, f, ensure_ascii=False, indent=2)
    with open(os.path.join(rd2, 'report.md'), 'w', encoding='utf-8') as f:
        f.write(ro._render_md(rep3))
    res3 = aj.attach_judgment(rd2, jp, root=ROOT)
    with open(os.path.join(rd2, 'report.md'), encoding='utf-8') as f:
        md3 = f.read()
    check('Mi-1 对侧: 成功 attach 后 md 渲 attached 节(violations 计数)',
          res3['attached'] is True
          and '## Agent 判断落位' in md3
          and 'attached=True(schema 1.1;violations=0)' in md3, md3[-300:])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# ══════════════════════════════════════════════════════════════════
section('3 NIT V2-5 falsification.secondary_metric_ids(schema v1.1)')
# ══════════════════════════════════════════════════════════════════
check('schema 版本升 v1.1(v1.0 判 SCHEMA 违规)',
      aj.JUDGMENT_SCHEMA_VERSION == '1.1')
j_old = base_judgment()
j_old['schema_version'] = '1.0'
check('v1.0 judgment 显式拒收(单版本纪律)',
      'SCHEMA' in codes(aj.validate_judgment(j_old, EV_REFS, set(MIDS))))

j = base_judgment()
check('母本(无 secondary_metric_ids=v1.0 单指标形态)不违规(向后兼容)',
      aj.validate_judgment(j, EV_REFS, set(MIDS))['passed'])

j = base_judgment()
j['l4']['scenarios'][1]['rows']['falsification']['secondary_metric_ids'] = [
    MID_B]
res = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('复合证伪条件: 合法副指标(在册 1 条)通过',
      res['passed'], str(res['violations'][:2]))

j = base_judgment()
j['l4']['scenarios'][1]['rows']['falsification']['secondary_metric_ids'] = [
    MID_A, MID_B]
res = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('合法副指标多条(在册 2 条)通过', res['passed'])

j = base_judgment()
j['l4']['scenarios'][1]['rows']['falsification']['secondary_metric_ids'] = [
    'NOT_A_METRIC']
res = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('副指标不在注册表→SCN-FALS2 拒收',
      'SCN-FALS2' in codes(res), str(res['violations'][:2]))

j = base_judgment()
j['l4']['scenarios'][1]['rows']['falsification']['secondary_metric_ids'] = 'X'
res = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('副指标错型(str 非 list)→SCN-FALS2 拒收',
      'SCN-FALS2' in codes(res))

j = base_judgment()
j['l4']['scenarios'][1]['rows']['falsification']['secondary_metric_ids'] = []
res = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('副指标空 list(应省略而非空表)→SCN-FALS2 拒收',
      'SCN-FALS2' in codes(res))

j = base_judgment()
j['l4']['scenarios'][1]['rows']['falsification']['secondary_metric_ids'] = [
    MID_A, MID_B, MIDS[2], MIDS[3]]
res = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('副指标超上限(4 条>3)→SCN-FALS2 拒收',
      'SCN-FALS2' in codes(res))

# 主锚纪律不放松: metric_id 仍必须(副指标不顶替主锚)
j = base_judgment()
del j['l4']['scenarios'][1]['rows']['falsification']['metric_id']
j['l4']['scenarios'][1]['rows']['falsification']['secondary_metric_ids'] = [
    MID_A]
res = aj.validate_judgment(j, EV_REFS, set(MIDS))
check('主锚 metric_id 缺席仍拒收(副指标不顶替主锚)',
      'SCN-FALS' in codes(res))

# ══════════════════════════════════════════════════════════════════
section('4 DFF 日频史接线(registry v2.8.5+权威门+history_source 解析)')
# ══════════════════════════════════════════════════════════════════
check('registry 版本 v2.8.5(R25 DFF history_source;曾升2.8.4 R12 japan source_key补接/2.8.3 R11注记细化/2.8.2 R6-D1换源/2.8.0 数据批1)',
      REG_JSON['version'] == '2.8.5', REG_JSON['version'])
dff = REG['by_id'].get('DFF') or {}
check('DFF 事实权威通道不变(source=rate_expectations)',
      dff.get('source') == 'rate_expectations', str(dff.get('source')))
check('DFF 新增 history_source=macro_collector(历史序列通道解耦)',
      dff.get('history_source') == 'macro_collector',
      str(dff.get('history_source')))
check('DFF criticality=core 不变(事实面零变动)',
      dff.get('criticality') == 'core')

check('macro_collector FRED_SERIES 接线 DFF(同 FED_FUNDS/SOFR/WALCL 先例)',
      mc.FRED_SERIES.get('DFF') == 'DFF', str(mc.FRED_SERIES.get('DFF')))
check('SERIES_FREQ[DFF]=daily', mc.SERIES_FREQ.get('DFF') == 'daily')
check('SERIES_UNITS[DFF]=(rate,%)(利率语义)',
      mc.SERIES_UNITS.get('DFF') == ('rate', '%'),
      str(mc.SERIES_UNITS.get('DFF')))

# ── 4b normalize_macro 事实权威门(防双通道双事实) ──────────────────
AS_OF = '2026-01-10T23:59:59+08:00'
macro_data = {
    'DFF': {'value': 4.33, 'date': '2026-01-09',
            'series': {'dates': ['2026-01-07', '2026-01-08', '2026-01-09'],
                       'values': [4.33, 4.33, 4.33]}},
    'UST_10Y': {'value': 4.4, 'date': '2026-01-09',
                'series': {'dates': ['2026-01-08', '2026-01-09'],
                           'values': [4.39, 4.4]}},
}
facts = fe.normalize_macro(macro_data, AS_OF, 'macro_20260110.json')
mids_out = [f.get('metric_id') for f in facts]
check('权威门: macro 档含 DFF 序列但不立 DFF 事实(权威=rate 通道)',
      'DFF' not in mids_out, str(mids_out))
check('权威门: 既有 macro 指标(UST_10Y)事实照立(零回归)',
      'UST_10Y' in mids_out)
check('权威门: 未注册键仍 FAIL 事实如实(原行为保持)',
      any(f.get('quality_status') == 'FAIL' for f in
          fe.normalize_macro({'NOT_REGISTERED': {'value': 1, 'date': 'x'}},
                             AS_OF, 'macro_20260110.json')))

# ── 4c rhq.load_metric_series: history_source 解析走 macro 接入点 ──
root4 = tempfile.mkdtemp(prefix='r25n4-')
td4 = os.path.join(root4, 'daily')
os.makedirs(td4)
with open(os.path.join(td4, 'macro_20260110.json'), 'w',
          encoding='utf-8') as f:
    json.dump({'data': macro_data}, f, ensure_ascii=False)
try:
    ser = rhq.load_metric_series('DFF', '20260110', data_dir=td4,
                                 trusted_root=root4)
    check('load_metric_series(DFF) 经 history_source 走 macro 接入点',
          ser['metric_id'] == 'DFF'
          and ser['source']['access_point'] == rhq.ACCESS_POINTS['macro'],
          str(ser.get('source')))
    check('DFF 序列值逐位回读(3 观测,首末 2026-01-07/09)',
          ser['dates'] == ['2026-01-07', '2026-01-08', '2026-01-09']
          and ser['values'] == [4.33, 4.33, 4.33],
          str((ser['dates'], ser['values'])))
    check('DFF 序列载荷 unit/frequency 自注册表(percent/daily)',
          ser['unit'] == 'percent' and ser['frequency'] == 'daily')
    check('权威门一致性: 序列载荷不带 macro 事实面(fact 缺席=None)',
          ser['quality_status'] is None and ser['value'] is None)
finally:
    shutil.rmtree(root4, ignore_errors=True)

# ── 4d 拉取前诚实缺席(操作者轮未跑,macro 档无 DFF 键) ──────────────
root4e = tempfile.mkdtemp(prefix='r25n4e-')
td4e = os.path.join(root4e, 'daily')
os.makedirs(td4e)
with open(os.path.join(td4e, 'macro_20260110.json'), 'w',
          encoding='utf-8') as f:
    json.dump({'data': {'UST_10Y': macro_data['UST_10Y']}}, f,
              ensure_ascii=False)
try:
    ser = rhq.load_metric_series('DFF', '20260110', data_dir=td4e,
                                 trusted_root=root4e)
    check('拉取前: macro 档无 DFF 键→空序列如实(不造数不炸)',
          ser['dates'] == [] and ser['values'] == [])
finally:
    shutil.rmtree(root4e, ignore_errors=True)

# ── 4e wd.metric_series 真链 e2e(R25 审计 Mi-2: 镜像断言→执行覆盖) ──
# FIX7 信任边界=采集档须在可信项目根内: fixture 置 ROOT/data 下
# (gitignored,不在 data/daily 不污染兄弟套件 glob;finally 清理),
# 伪根内自备 config/metric_registry.json+data/daily/macro_*.json,
# metric_series(root=伪根) 全链走通(前缀解析+glob+rhq 接入点)。
fake_root = tempfile.mkdtemp(prefix='r25-e2e-', dir=os.path.join(ROOT, 'data'))
try:
    os.makedirs(os.path.join(fake_root, 'config'))
    shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
                os.path.join(fake_root, 'config', 'metric_registry.json'))
    os.makedirs(os.path.join(fake_root, 'data', 'daily'))
    with open(os.path.join(fake_root, 'data', 'daily',
                           'macro_20260110.json'), 'w',
              encoding='utf-8') as f:
        json.dump({'data': macro_data}, f, ensure_ascii=False)
    got, err = wd.metric_series('DFF', snapshot=None, root=fake_root)
    check('Mi-2: wd.metric_series(DFF) 真链 e2e 取到序列'
          '(history_source 前缀解析,变异可红)',
          got is not None
          and got['dates'] == ['2026-01-07', '2026-01-08', '2026-01-09']
          and 'macro_20260110' in (got.get('source') or ''),
          str((got, err)))
finally:
    shutil.rmtree(fake_root, ignore_errors=True)

# 前缀解析回归面(表达式层): 无 history_source 回落 source;flat 通道不支持
ust = REG['by_id'].get('UST_10Y') or {}
ust_prefix = wd.SERIES_SOURCE_PREFIX.get(
    ust.get('history_source') or ust.get('source'))
check('wd 前缀解析: 无 history_source 指标回落 source(UST_10Y→macro_)',
      ust_prefix == 'macro_', str(ust_prefix))
jpn = REG['by_id'].get('JP_POLICY_RATE') or {}
jpn_prefix = wd.SERIES_SOURCE_PREFIX.get(
    jpn.get('history_source') or jpn.get('source'))
check('wd 前缀解析: flat 单点通道(japan_rate)仍无前缀=如实不支持',
      jpn_prefix is None)

# ── 4f registry 校验面(R25 审计 Mi-3: history_source 受通道枚举约束) ──
import registry_semantics as rs  # noqa: E402
probs = rs.validate_registry(REG_JSON)
check('Mi-3: 真实 registry 过校验(零 R-HISTORYSOURCE 违规)',
      not [p for p in probs if 'HISTORYSOURCE' in str(p.get('rule', ''))],
      str(probs[:3]))
bad_reg = json.loads(json.dumps(REG_JSON))
bad_reg['metrics'][0]['history_source'] = 'not_a_channel'
probs2 = rs.validate_registry(bad_reg)
check('Mi-3: history_source 错值→R-HISTORYSOURCE-ENUM error(晚拒变早拒)',
      any(p.get('rule') == 'R-HISTORYSOURCE-ENUM' for p in probs2))
bad_reg2 = json.loads(json.dumps(REG_JSON))
bad_reg2['metrics'][0]['history_source'] = 123
probs3 = rs.validate_registry(bad_reg2)
check('Mi-3: history_source 错型(int)→R-HISTORYSOURCE-TYPE error',
      any(p.get('rule') == 'R-HISTORYSOURCE-TYPE' for p in probs3))

# ══════════════════════════════════════════════════════════════════
print('═' * 64)
print(f"RESULT: PASS={PASS} FAIL={FAIL}")
sys.exit(0 if FAIL == 0 else 1)
