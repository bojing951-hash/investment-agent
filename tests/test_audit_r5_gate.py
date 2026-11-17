#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R5 第五轮审计修复回归: 摘要迁移可信旧证/数据门分级/裁决链格式。

§P(R5-1): rebind_verdict_digest 迁移不绕过审查——旧口径未覆盖输入须
          可信旧证(归档 manifest copies_sha16),无证/已变均拒;
          未变且证据完整才可迁移(正例)。
§Q(R5-2): 数据门分级——run_ok=true 不豁免必要缺口(2A);关键步骤失败
          (S10 自检/未知 kind/进程失败)不归可选降级(2B);可选缺失
          显式旗标降级交付正例保留;report 与 archive 两门同判。
§R(R5-4): 裁决链格式与链校验——删 revision 冒充 legacy(单档/链中)、
          非首档缺 pred、pred 指向自己/后续/跨任务、未知 format_version
          均阻断;生产链与 legacy 头+rebind 混合链(真 A/BLIND 形)正例。
§S(R5-2.5): 必要数据规格——问题限定时间范围按 N 年×频率年观测数推导
          (不得统一 12 替代任务范围);未限定用频率族兜底;资产名
          (十年期美债)不误配;spec 含形态/窗口/频率/质量/覆盖。

全部经生产写档函数构造(record_semantic_verdict/rebind_verdict_digest/
ia_cli research-one 阶段真跑);判定=逐 check 打印+exit code。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import agent_judgment as aj          # noqa: E402
import research_orchestrator as ro   # noqa: E402

PASS, FAIL = 0, 0
_RUN_SEQ = 300


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS = PASS + (1 if cond else 0)
    FAIL = FAIL + (0 if cond else 1)


def make_run(tmp, name, *, run_ok=True, l1_rows=2, produced=True,
             req_items=None, allow_flag=False, steps=None):
    """合成已挂判定 run(结构面与生产 attach 后同形;steps 覆写=失败步面)。"""
    global _RUN_SEQ
    _RUN_SEQ += 1
    run_ts = '20261117T15%04dZ' % _RUN_SEQ
    rd = os.path.join(tmp, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(l1_rows)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': 'Audit-R5 回归合成问题', 'ts_utc': run_ts,
                'git_head': 'synthetic', 'degradation_policy': {}},
        'steps': steps if steps is not None else [], 'fanout': {},
        'layers': {
            'L1_事实层': {'rows': rows, 'available': l1_rows > 0,
                         'n': l1_rows, 'note': '合成: 无事实行'},
            'L2_机构观点层': {'views': {'available': False, 'n': 0,
                                        'note': '合成: 观点库缺席'}},
            'L3_AI推断层': {'produced': produced, 'attribution': 'ai_inferred',
                           'note': '合成: L3 注记'},
            'L4_条件情景层': {'produced': produced, 'attribution': 'ai_inferred',
                           'note': '合成: L4 注记'}},
        'evidence_index': [{'kind': 'metric', 'ref': 'TEST_M0@2026-11-09'},
                           {'kind': 'metric', 'ref': 'TEST_M1@2026-11-09'}
                           ][:max(l1_rows, 0)],
        'notes': [], 'run_ok': run_ok,
        'agent_judgment': {
            'attached': True, 'judgment_file': 'judgment.json',
            'validation': {'passed': True, 'violations': []},
            'run_ok_at_attach': True if run_ok else False,
            'allow_failed_run': bool(allow_flag and not run_ok)}}
    if req_items is not None:
        report['run']['data_requirements'] = {
            'frozen_at': 'plan(采集前冻结;分类与规格不随采集结果改判)',
            'items': req_items,
            'optional_face': {'tier': 'optional'}}
    json.dump(report, open(os.path.join(rd, 'report.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False)
    json.dump({'schema_version': aj.JUDGMENT_SCHEMA_VERSION,
               'agent_declaration': {'role': 'synthetic'},
               'l3': {'claims': []}, 'l4': {'scenarios': []}},
              open(os.path.join(rd, 'agent_judgment.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8').write(
        ro._render_md(report))
    json.dump({'n': 1, 'note': 'views 库在场', 'views': [
        {'view_id': 'V-2026-001', 'institution_name': '机构A',
         'publish_date': '2026-11-01', 'report_title': '标题',
         'core_views': ['主张'], 'forecasts': [], 'risk_factors': []}]},
        open(os.path.join(rd, 'views_digest.json'), 'w', encoding='utf-8'),
        ensure_ascii=False)
    return rd


def stage_report(rd, engine_root):
    r = subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'report',
         '--report-dir', rd, '--engine-root', engine_root],
        cwd=ROOT, capture_output=True, text=True, timeout=180)
    e = json.loads(r.stdout)
    d = e['data']
    d['_warnings'] = e.get('warnings') or []
    return d


def stage_archive(rd, engine_root, arc):
    return subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'archive',
         '--report-dir', rd, '--engine-root', engine_root,
         '--archive-dir', arc],
        cwd=ROOT, capture_output=True, text=True, timeout=180)


def state_of(rd, engine_root):
    rj = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    return aj._semantic_review_state(rj, engine_root, rd)


def rewrite(path, **over):
    d = json.load(open(path, encoding='utf-8'))
    for k, v in list(over.items()):
        if v is DELETE:
            d.pop(k, None)
        else:
            d[k] = v
    json.dump(d, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    return d


class _Del:
    pass


DELETE = _Del()


def plant_manifest(engine_root, run_dir, verdict_path, *, tamper=None):
    """在 engine 根落归档 manifest 快照(verdict_chain 绑旧档字节+
    copies_sha16=当前未覆盖面字节;tamper=覆写某输入的旧证哈希)。"""
    arc = os.path.join(engine_root, 'research_archive', 'trusted_arc')
    shutil.rmtree(arc, ignore_errors=True)
    os.makedirs(arc, exist_ok=True)
    copies = {'report.json': aj._sha16_of_file(
        os.path.join(run_dir, 'report.json'))}
    vd = os.path.join(run_dir, 'views_digest.json')
    if os.path.isfile(vd):
        copies['views_digest.json'] = aj._sha16_of_file(vd)
    if tamper:
        copies.update(tamper)
    run_ts = json.load(open(os.path.join(run_dir, 'report.json'),
                            encoding='utf-8'))['run']['ts_utc']
    json.dump({'run_ts': run_ts,
               'verdict_chain': [{'source_rel': os.path.relpath(
                   verdict_path, engine_root),
                   'sha256': aj._sha16_of_file(verdict_path)}],
               'copies_sha16': copies},
              open(os.path.join(arc, 'ARCHIVE_MANIFEST.json'), 'w',
                   encoding='utf-8'), ensure_ascii=False)
    return arc


print('═' * 64)
print('Audit-R5: 迁移可信旧证 / 数据门分级 / 裁决链格式')
print('═' * 64)

tmp = tempfile.mkdtemp(prefix='r5gate_')
eroot = os.path.join(tmp, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

# ══ §P: R5-1 摘要迁移绕过审查 ═══════════════════════════════════════
print('§P rebind 迁移可信旧证(R5-1)')

# P1 反例冻结: v2 时代混合形+篡改 views → 无证拒绝(基线曾误放行)
rdP1 = make_run(tmp, 'p1')
aj.record_semantic_verdict(eroot, rdP1, 'UPHELD', 'R5-SEAT')
vP1 = aj._verdicts_for_run(eroot, json.load(open(os.path.join(
    rdP1, 'report.json')))['run']['ts_utc'])[0][0]
rewrite(vP1, content_sha256=aj.content_digest_v2(rdP1))   # 时代垫片(v2 锚)
vd = json.load(open(os.path.join(rdP1, 'views_digest.json'), encoding='utf-8'))
vd['views'][0]['report_title'] = '被篡改标题'
json.dump(vd, open(os.path.join(rdP1, 'views_digest.json'), 'w',
                   encoding='utf-8'), ensure_ascii=False)
try:
    aj.rebind_verdict_digest(eroot, rdP1, 'P1')
    gP1 = False
except ValueError as e:
    gP1 = ('views_digest.json' in str(e))
check('P1 v2 锚+篡改 views+无可信旧证 → 迁移拒绝(基线反例冻结)', gP1)

# P2 有可信旧证(归档 manifest 快照与当前一致)→ 未变且证据完整可迁移
rdP2 = make_run(tmp, 'p2')
aj.record_semantic_verdict(eroot, rdP2, 'UPHELD', 'R5-SEAT')
vP2 = aj._verdicts_for_run(eroot, json.load(open(os.path.join(
    rdP2, 'report.json')))['run']['ts_utc'])[0][0]
rewrite(vP2, content_sha256=aj.content_digest_v2(rdP2))
plant_manifest(eroot, rdP2, vP2)
pP2 = aj.rebind_verdict_digest(eroot, rdP2, 'P2 可信迁移')
dP2 = json.load(open(pP2, encoding='utf-8'))
eP2 = stage_report(rdP2, eroot)
check('P2 可信旧证一致 → 迁移成功+未覆盖面证明随档+可交付',
      dP2.get('overall') == 'UPHELD'
      and 'views_digest.json' in (dP2.get('rebind') or {}).get(
          'uncovered_inputs_proof', {})
      and eP2.get('deliverable') is True,
      str((dP2.get('rebind') or {}).get('uncovered_inputs_proof')))

# P3 旧证在场但 views 已变 → 拒绝(新增范围被修改)
rdP3 = make_run(tmp, 'p3')
aj.record_semantic_verdict(eroot, rdP3, 'UPHELD', 'R5-SEAT')
vP3 = aj._verdicts_for_run(eroot, json.load(open(os.path.join(
    rdP3, 'report.json')))['run']['ts_utc'])[0][0]
rewrite(vP3, content_sha256=aj.content_digest_v2(rdP3))
plant_manifest(eroot, rdP3, vP3,
               tamper={'views_digest.json': 'deadbeefdeadbeef'})
try:
    aj.rebind_verdict_digest(eroot, rdP3, 'P3')
    gP3 = False
except ValueError as e:
    gP3 = '已被修改' in str(e)
check('P3 旧证与当前 views 不符 → 迁移拒绝(新增范围被修改)', gP3)

# P4 v1→v3 未覆盖面含 report.json(机器推导,边界与 report/archive 一致)
rdP4 = make_run(tmp, 'p4')
aj.record_semantic_verdict(eroot, rdP4, 'UPHELD', 'R5-SEAT')
vP4 = aj._verdicts_for_run(eroot, json.load(open(os.path.join(
    rdP4, 'report.json')))['run']['ts_utc'])[0][0]
rewrite(vP4, content_sha256=aj.content_digest_v1(rdP4))
plant_manifest(eroot, rdP4, vP4)
pP4 = aj.rebind_verdict_digest(eroot, rdP4, 'P4')
dP4 = json.load(open(pP4, encoding='utf-8'))
check('P4 v1 口径未覆盖面={report.json,views_digest} 逐项有证',
      set((dP4.get('rebind') or {}).get('uncovered_inputs_proof', {})
          ) == {'report.json', 'views_digest.json'}
      and (dP4.get('rebind') or {}).get('from_algorithm') == 'digest_v1',
      str((dP4.get('rebind') or {}).get('uncovered_inputs_proof')))

# P5 旧裁决本身无效(越表词)→ 不得继承
rdP5 = make_run(tmp, 'p5')
aj.record_semantic_verdict(eroot, rdP5, 'UPHELD', 'R5-SEAT')
vP5 = aj._verdicts_for_run(eroot, json.load(open(os.path.join(
    rdP5, 'report.json')))['run']['ts_utc'])[0][0]
rewrite(vP5, content_sha256=aj.content_digest_v2(rdP5), overall='PASS')
plant_manifest(eroot, rdP5, vP5)
try:
    aj.rebind_verdict_digest(eroot, rdP5, 'P5')
    gP5 = False
except ValueError as e:
    gP5 = '旧裁决档不合法' in str(e)
check('P5 旧裁决越表词(PASS)→ 迁移拒绝(先验旧裁决合法有效)', gP5)

# ══ §Q: R5-2 数据门分级 ═════════════════════════════════════════════
print('§Q 数据门分级(run_ok 不豁免必要缺口;关键失败不归可选)')

REQ_INSUFFICIENT = [{
    'metric_id': 'TEST_M0', 'tier': 'required',
    'basis': '问题词面命中(任务目标)',
    'spec': {'form': 'series', 'window': 'max_available',
             'frequency': 'daily', 'quality': 'snapshot 序列(OK 行)',
             'min_observations': 60},
    'outcome': 'insufficient_coverage',
    'outcome_basis': '历史序列 n=1 < 最低覆盖 60(单点≠历史分析需求)'}]
REQ_OK_DAILY = [{
    'metric_id': 'TEST_M0', 'tier': 'required',
    'basis': '问题词面命中(任务目标)',
    'spec': {'form': 'series', 'window': 'max_available',
             'frequency': 'daily', 'quality': 'snapshot 序列(OK 行)',
             'min_observations': 60},
    'outcome': 'satisfied', 'outcome_basis': '历史序列 n=2499(采集档)'}]
S10_FAIL = [{'step': 'S10_selfcheck', 'executed': True, 'ok': False,
             'note': '缺来源行: [TEST_M0]',
             'selfcheck': {'n_evidence_rows': 2, 'n_rows_missing_ref': 1,
                           'ok': False}}]
UNKNOWN_FAIL = [{'step': 'S4_history_X', 'executed': True, 'ok': False,
                 'exit_code': 3,
                 'envelope': {'ok': False,
                              'error': {'kind': 'weird_new_kind',
                                        'message': '未知失败'}}}]
PROC_FAIL = [{'step': 'S8_grounded_qa', 'executed': True, 'ok': False,
              'exit_code': None, 'note': '进程启动失败:boom',
              'envelope': None}]
OPT_NOSERIES = [{'step': 'S4_history_OPT_M', 'executed': True, 'ok': False,
                 'exit_code': 1,
                 'envelope': {'ok': False,
                              'error': {'kind': 'no_series',
                                        'message': '该指标无历史序列'}}}]

# Q1(=2A): run_ok=true + 必要 insufficient → 阻断
rdQ1 = make_run(tmp, 'q1', run_ok=True, req_items=REQ_INSUFFICIENT)
aj.record_semantic_verdict(eroot, rdQ1, 'UPHELD', 'R5-SEAT')
dQ1 = stage_report(rdQ1, eroot)
check('Q1 run_ok=true+必要 insufficient → required_data_missing 拒交付',
      dQ1.get('deliverable') is False
      and dQ1.get('blocked_class') == 'required_data_missing',
      f"bc={dQ1.get('blocked_class')} deliv={dQ1.get('deliverable')}")
rQ1 = stage_archive(rdQ1, eroot, os.path.join(tmp, 'arc_q1'))
check('Q1b archive 门同判拒归(非 deliverable 不归档)',
      rQ1.returncode != 0 and not os.path.exists(
          os.path.join(tmp, 'arc_q1', 'ARCHIVE_MANIFEST.json')))

# Q2(=2B): S10 失败+旗标+有效裁决 → critical_step_failure 拒交付
rdQ2 = make_run(tmp, 'q2', run_ok=False, steps=S10_FAIL,
                req_items=REQ_OK_DAILY, allow_flag=True)
aj.record_semantic_verdict(eroot, rdQ2, 'UPHELD', 'R5-SEAT')
dQ2 = stage_report(rdQ2, eroot)
check('Q2 S10 失败+旗标+UPHELD → critical_step_failure 拒交付',
      dQ2.get('deliverable') is False
      and dQ2.get('blocked_class') == 'critical_step_failure',
      f"bc={dQ2.get('blocked_class')}")
rQ2 = stage_archive(rdQ2, eroot, os.path.join(tmp, 'arc_q2'))
check('Q2b archive 门同判拒归', rQ2.returncode != 0)

# Q3 正例保留: 仅可选 no_series 诚实拒答 → 降级交付仍可行
rdQ3 = make_run(tmp, 'q3', run_ok=False, steps=OPT_NOSERIES,
                req_items=REQ_OK_DAILY, allow_flag=True)
aj.record_semantic_verdict(eroot, rdQ3, 'UPHELD', 'R5-SEAT')
dQ3 = stage_report(rdQ3, eroot)
check('Q3 可选 no_series+旗标+UPHELD → optional 降级交付保留',
      dQ3.get('deliverable') is True
      and dQ3.get('blocked_class') == 'optional_data_missing',
      f"bc={dQ3.get('blocked_class')} deliv={dQ3.get('deliverable')}")

# Q4 未知失败 kind 不归可选
rdQ4 = make_run(tmp, 'q4', run_ok=False, steps=UNKNOWN_FAIL,
                req_items=REQ_OK_DAILY, allow_flag=True)
check('Q4 未知 error kind → critical_step_failure(未知失败不归可选)',
      aj.blocked_class_of(json.load(open(os.path.join(
          rdQ4, 'report.json'), encoding='utf-8')))
      == 'critical_step_failure')

# Q5 进程失败(无信封)不归可选
rdQ5 = make_run(tmp, 'q5', run_ok=False, steps=PROC_FAIL,
                req_items=REQ_OK_DAILY, allow_flag=True)
check('Q5 进程失败无信封 → critical_step_failure',
      aj.blocked_class_of(json.load(open(os.path.join(
          rdQ5, 'report.json'), encoding='utf-8')))
      == 'critical_step_failure')

# Q6 归档正例: Q3 降级交付 → 归档 ok+manifest 在场
rQ6 = stage_archive(rdQ3, eroot, os.path.join(tmp, 'arc_q3'))
check('Q6 optional 降级交付 → archive 放行+manifest 在场',
      rQ6.returncode == 0 and os.path.exists(
          os.path.join(tmp, 'arc_q3', 'ARCHIVE_MANIFEST.json')),
          rQ6.stdout[-120:] if rQ6.returncode else '')

# ══ §R: R5-4 裁决链格式与链校验 ═════════════════════════════════════
print('§R 裁决链格式与链校验(R5-4)')


def chain_face(name, mutate):
    rd = make_run(tmp, 'r_' + name)
    p1 = aj.record_semantic_verdict(eroot, rd, 'REVISE', 'R5-SEAT')
    p2 = aj.record_semantic_verdict(eroot, rd, 'UPHELD', 'R5-SEAT')
    mutate(p1, p2)
    s = state_of(rd, eroot)
    check(f'R-{name} → invalid_record 阻断',
          bool(s.get('error')) and str(s.get('error')).startswith(
              'invalid_record'),
          f"error={s.get('error')}")


chain_face('a 单档删revision',
           lambda p1, p2: (rewrite(p2, revision=DELETE, predecessor=DELETE),
                           os.remove(p1)))
chain_face('b 链中删revision', lambda p1, p2: rewrite(p2, revision=DELETE))
chain_face('c 非首档缺pred', lambda p1, p2: rewrite(p2, predecessor=DELETE))
chain_face('d pred指向自己',
           lambda p1, p2: rewrite(p2, predecessor=os.path.relpath(
               p2, eroot)))
chain_face('e 首档指向后续',
           lambda p1, p2: rewrite(p1, predecessor=os.path.relpath(
               p2, eroot)))
chain_face('f 未知format_version',
           lambda p1, p2: rewrite(p2, format_version=99))

# R-g 跨任务 pred: 指向另一 run 的在档裁决(不在本 run_paths)
rdX = make_run(tmp, 'rx')
pX1 = aj.record_semantic_verdict(eroot, rdX, 'REVISE', 'R5-SEAT')
pX2 = aj.record_semantic_verdict(eroot, rdX, 'UPHELD', 'R5-SEAT')
rdY = make_run(tmp, 'ry')
pY1 = aj.record_semantic_verdict(eroot, rdY, 'REVISE', 'R5-SEAT')
pY2 = aj.record_semantic_verdict(eroot, rdY, 'UPHELD', 'R5-SEAT')
rewrite(pY2, predecessor=os.path.relpath(pX2, eroot))
sY = state_of(rdY, eroot)
check('R-g pred 指向其他任务档 → invalid_record 阻断',
      str(sY.get('error')).startswith('invalid_record'), str(sY.get('error')))
sX = state_of(rdX, eroot)
check('R-h 被指向的他任务链不受污染(链身份隔离)',
      sX.get('error') is None and sX.get('verdict') == 'UPHELD')

# R-i 正例: 生产链 3 档健全(分三日)
rdI = make_run(tmp, 'ri')
psI = [aj.record_semantic_verdict(eroot, rdI, ovl, 'R5-SEAT')
       for ovl in ('REVISE', 'REVISE', 'UPHELD')]
# 先全部写入(同日 -01/-02/-03)再整批移日+同步改写 pred=新路径
# (生产 append-only 不移档;此处模拟三档分三日写入的最终形)
daysI = ('20261115', '20261116', '20261117')
dstsI = []
for p, day in zip(psI, daysI):
    d = os.path.join(eroot, 'audit', 'semantic_review', day)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, os.path.basename(p))
    shutil.move(p, dst)
    dstsI.append(dst)
for p, dst, prev in zip(psI, dstsI, [None] + dstsI[:-1]):
    v = json.load(open(dst, encoding='utf-8'))
    v['predecessor'] = (os.path.relpath(prev, eroot)
                        if prev else None)
    json.dump(v, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
sI = state_of(rdI, eroot)
check('R-i 生产链跨日 3 档 → 健全(UPHELD fresh)',
      sI.get('verdict') == 'UPHELD' and sI.get('fresh') is True
      and sI.get('verdicts_n') == 3 and sI.get('error') is None, str(sI))

# R-j 正例: legacy 头(v1 锚)+rebind 混合链(真 A/BLIND 形)仍合法
rdJ = make_run(tmp, 'rj')
vLegacy = aj.record_semantic_verdict(eroot, rdJ, 'UPHELD', 'R5-SEAT')
rewrite(vLegacy, content_sha256=aj.content_digest_v1(rdJ),
        revision=DELETE, predecessor=DELETE,
        format_version=DELETE, digest_algorithm=DELETE)
plant_manifest(eroot, rdJ, vLegacy)
aj.rebind_verdict_digest(eroot, rdJ, 'R-j legacy 头+rebind 混合链')
sJ = state_of(rdJ, eroot)
check('R-j legacy 头(v1 锚)+rebind 档 → 健全(UPHELD fresh, n=2)',
      sJ.get('verdict') == 'UPHELD' and sJ.get('fresh') is True
      and sJ.get('verdicts_n') == 2 and sJ.get('error') is None, str(sJ))

# ══ §S: R5-2.5 必要数据规格(任务范围推导) ═══════════════════════════
print('§S 必要数据规格(问题范围×频率推导,不统一 12 替代)')


def s4(mid, n, ok=True, freq=None):
    env = {'data': {'series': {'n': n, 'source': '采集档',
                               'frequency': freq}}} if ok else None
    return {'step': f'S4_history_{mid}', 'ok': ok, 'envelope': env}


q3y = '近三年 TEST_M0 与 TEST_M1 的关系'
items3y = {i['metric_id']: i for i in ro._evaluate_data_requirements(
    ['TEST_M0'], [s4('TEST_M0', 250, freq='daily')], {}, [],
    question=q3y)}
check('S1 问题限定近三年+日频 → min=3×252=756, n=250 不足',
      items3y['TEST_M0']['spec']['min_observations'] == 756
      and items3y['TEST_M0']['outcome'] == 'insufficient_coverage'
      and items3y['TEST_M0']['spec']['window'] == 'question_range:3年',
      str(items3y['TEST_M0']['spec']))
items3y_ok = ro._evaluate_data_requirements(
    ['TEST_M0'], [s4('TEST_M0', 800, freq='daily')], {}, [], question=q3y)
check('S2 n=800≥756 → satisfied(任务范围内满足)',
      items3y_ok[0]['outcome'] == 'satisfied')

items5y_m = ro._evaluate_data_requirements(
    ['PM_M'], [s4('PM_M', 59, freq='monthly')], {}, [],
    question='过去五年 PM_M 走势')
check('S3 月频+过去五年 → min=60, n=59 不足',
      items5y_m[0]['spec']['min_observations'] == 60
      and items5y_m[0]['outcome'] == 'insufficient_coverage',
      str(items5y_m[0]['spec']))

items_nr = ro._evaluate_data_requirements(
    ['TEST_M0'], [s4('TEST_M0', 100, freq='daily')], {}, [],
    question='TEST_M0 与 TEST_M1 的关系')
check('S4 未限定范围+日频 → 频率族兜底 60, n=100 满足',
      items_nr[0]['spec']['min_observations'] == 60
      and items_nr[0]['outcome'] == 'satisfied'
      and items_nr[0]['spec']['window'] == 'max_available',
      str(items_nr[0]['spec']))

check('S5 资产名(十年期美债)不误配任务范围',
      ro._question_range_years('UST_10Y 十年期美债利率上行的传导') is None
      and ro._question_range_years('近十年 UST_10Y 与 SPX') == 10
      and ro._question_range_years('过去3年 GOLD_F 表现') == 3)

spec_keys = items_nr[0]['spec']
check('S6 spec 含形态/窗口/频率/质量/覆盖五面',
      {'form', 'window', 'frequency', 'quality', 'coverage_observed'}
      <= set(spec_keys) and 'min_observations_basis' in spec_keys,
      str(sorted(spec_keys)))

# ══ 汇总 ═══════════════════════════════════════════════════════════
print('═' * 64)
print(f'Audit-R5 判定: {PASS} PASS / {FAIL} FAIL')
print('═' * 64)
sys.exit(1 if FAIL else 0)
