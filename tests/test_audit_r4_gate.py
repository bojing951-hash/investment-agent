#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R4 回归: 裁决链 fail-closed + 审查覆盖全部交付输入 + 跨日归档 +
必要/可选数据贯通(六项发现的机器锁定面)。

锁的面(反例均先在受审基线 5fc5df8 复现误放行,修复后必须阻断):
  J. R4-01 裁决损坏与缺字段不得放行: 写入序定序(损坏档不降代)+
     逐档读取端校验(必填/目标 run/词表/revision/predecessor)+ mtime
     无关 + 复审恢复(更高 revision 新档,损坏历史保留);
  K. R4-02 审查覆盖全部实际交付输入: views_digest 入摘要(v3)+
     FULL_REPORT 内容段视图一致性 + 裁决推进不误伤(质量节不入比对);
  L. R4-04 跨日归档保留完整裁决历史: 日目录__basename 唯一名+
     冲突预检 + manifest 链关系/逐档哈希/数量唯一核对;
  M. R4-05 必要/可选数据规则贯通: insufficient_coverage=必要缺口
     (单点≠历史分析) → report 拒交付;仅可选缺失+显式旗标+有效独立
     审查 → 可交付;critical 恒拒。
全部裁决链由生产写档函数(record_semantic_verdict)生成。
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
_RUN_SEQ = 200


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS, FAIL = PASS + (1 if cond else 0), FAIL + (0 if cond else 1)


def make_run(tmp, name, *, run_ok=True, l1_rows=2, produced=True,
             req_items=None, allow_flag=False):
    """合成已挂判定 run(结构面与生产 attach 后同形)。

    req_items: run.data_requirements.items 覆写(M 块分级面);
    allow_flag: agent_judgment.allow_failed_run=True(M2 显式旗标随档)。
    """
    global _RUN_SEQ
    _RUN_SEQ += 1
    run_ts = '20261117T06%04dZ' % _RUN_SEQ
    rd = os.path.join(tmp, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(l1_rows)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': 'Audit-R4 回归合成问题', 'ts_utc': run_ts,
                'git_head': 'synthetic', 'degradation_policy': {}},
        'steps': [], 'fanout': {},
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


def state_of(rd, engine_root):
    rj = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    return aj._semantic_review_state(rj, engine_root, rd)


def move_to_day(root, path, day):
    """把生产写出的裁决档移入指定日目录(模拟跨日写入;文件本体不动)。"""
    d = os.path.join(root, 'audit', 'semantic_review', day)
    os.makedirs(d, exist_ok=True)
    dst = os.path.join(d, os.path.basename(path))
    shutil.move(path, dst)
    return dst


print('═' * 64)
print('Audit-R4: 裁决链 fail-closed / 审查覆盖 / 跨日归档 / 数据分级贯通')
print('═' * 64)

tmp = tempfile.mkdtemp(prefix='r4gate_')
eroot = os.path.join(tmp, 'engine')
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

# ══ J. R4-01 裁决损坏与缺字段不得放行(生产写档链) ══════════════════
section = 'J'
rdJ = make_run(tmp, 'j1')
p1 = aj.record_semantic_verdict(eroot, rdJ, 'REVISE', 'R4-SEAT')
p2 = aj.record_semantic_verdict(eroot, rdJ, 'UPHELD', 'R4-SEAT')
s = state_of(rdJ, eroot)
check('J1 链健全基线: rev2 UPHELD fresh',
      s['verdict'] == 'UPHELD' and s['fresh'] is True and s['verdicts_n'] == 2,
      str(s))

p3 = aj.record_semantic_verdict(eroot, rdJ, 'REVISE', 'R4-SEAT')
open(p3, 'w').write('{"overall": "REVI')          # 截断=半写损坏
s = state_of(rdJ, eroot)
d = stage_report(rdJ, eroot)
check('J2 截断最新档(rev3) → corrupt_latest 阻断,不回退旧 UPHELD',
      s['verdict'] is None and s['error'] == 'corrupt_latest'
      and d['deliverable'] is False,
      f"state={s.get('error')} deliverable={d.get('deliverable')}")

# 缺字段(可解析但缺 reviewer)
json.dump({'overall': 'REVISE', 'run_ts': 'x'}, open(p3, 'w'))
s = state_of(rdJ, eroot)
check('J3 缺必填字段(reviewer) → corrupt_latest',
      s['error'] == 'corrupt_latest' and s['verdict'] is None, str(s))

# 恢复: 复审新档(更高 revision)→ 交付恢复,损坏史保留
p4 = aj.record_semantic_verdict(eroot, rdJ, 'UPHELD', 'R4-SEAT-RE')
rev4 = json.load(open(p4))['revision']
s = state_of(rdJ, eroot)
d = stage_report(rdJ, eroot)
check('J4 复审恢复: 新档 revision 跳过不可读档(>3)且交付恢复',
      rev4 >= 4 and s['verdict'] == 'UPHELD' and s['fresh'] is True
      and d['deliverable'] is True and s['verdicts_n'] == 4,
      f"rev4={rev4} state={s['verdict']}/{s['fresh']} "
      f"deliverable={d.get('deliverable')}")
check('J4b 损坏历史保留: record_health 披露截断档',
      any('corrupt' in v for v in s['record_health'].values())
      and len(s['prior_verdicts']) == 3, str(s['record_health']))

# 跨日: 前两日两档+当日一档(生产写+移日模拟),截断当日档
rdJ2 = make_run(tmp, 'j2')
q1 = aj.record_semantic_verdict(eroot, rdJ2, 'REVISE', 'R4-SEAT')
q2 = aj.record_semantic_verdict(eroot, rdJ2, 'UPHELD', 'R4-SEAT')
q1 = move_to_day(eroot, q1, '20261115')
q2 = move_to_day(eroot, q2, '20261116')
# Audit-R5 条目4: predecessor=写入时路径;移日模拟须同步改写 pred 使链
# 与生产写入形一致(生产 append-only 不移档,链面本就自洽)
_d = json.load(open(q2))
_d['predecessor'] = os.path.relpath(q1, eroot)
json.dump(_d, open(q2, 'w'), ensure_ascii=False)
q3 = aj.record_semantic_verdict(eroot, rdJ2, 'REVISE', 'R4-SEAT')
open(q3, 'w').write('')
s = state_of(rdJ2, eroot)
check('J5 跨日截断当日最新档 → corrupt_latest(不回退前日 UPHELD)',
      s['verdict'] is None and s['error'] == 'corrupt_latest'
      and s['verdicts_n'] == 3, str(s))

# 重复 revision(改档模拟冲突)
rdJ3 = make_run(tmp, 'j3')
r1 = aj.record_semantic_verdict(eroot, rdJ3, 'REVISE', 'R4-SEAT')
r2 = aj.record_semantic_verdict(eroot, rdJ3, 'UPHELD', 'R4-SEAT')
_doc2 = json.load(open(r2))
_doc2['revision'] = 1                       # 与 rev1 撞号
json.dump(_doc2, open(r2, 'w'), ensure_ascii=False)
s = state_of(rdJ3, eroot)
check('J6 revision 撞号 → duplicate_revision 阻断',
      s['error'] == 'duplicate_revision' and s['verdict'] is None, str(s))

# 错误 run(档面 run_ts 与文件名键不符)
rdJ4 = make_run(tmp, 'j4')
t1 = aj.record_semantic_verdict(eroot, rdJ4, 'UPHELD', 'R4-SEAT')
_tdoc = json.load(open(t1))
_tdoc['run_ts'] = '20200101T000000Z'
json.dump(_tdoc, open(t1, 'w'), ensure_ascii=False)
s = state_of(rdJ4, eroot)
check('J7 错误 run 档(run_ts 字段≠文件名键) → invalid_record 阻断',
      str(s['error']).startswith('invalid_record')
      and s['verdict'] is None, str(s))

# 越表裁决词(新格式档)
rdJ5 = make_run(tmp, 'j5')
u1 = aj.record_semantic_verdict(eroot, rdJ5, 'UPHELD', 'R4-SEAT')
_udoc = json.load(open(u1))
_udoc['overall'] = 'PASS'
json.dump(_udoc, open(u1, 'w'), ensure_ascii=False)
s = state_of(rdJ5, eroot)
check('J8 新格式档越表裁决词(PASS) → invalid_record 阻断',
      str(s['error']).startswith('invalid_record'), str(s))

# mtime 无关
rdJ6 = make_run(tmp, 'j6')
v1 = aj.record_semantic_verdict(eroot, rdJ6, 'REVISE', 'R4-SEAT')
v2 = aj.record_semantic_verdict(eroot, rdJ6, 'UPHELD', 'R4-SEAT')
before = state_of(rdJ6, eroot)
old = time.time() - 86400
os.utime(v1, (old, old))
os.utime(v2, (time.time(), time.time()))
after = state_of(rdJ6, eroot)
check('J9 调换 mtime → 状态面不变', before == after,
      f"{before.get('verdict')}/{after.get('verdict')}")

# ══ K. R4-02 审查覆盖全部实际交付输入 ═══════════════════════════════
rdK = make_run(tmp, 'k1')
aj.record_semantic_verdict(eroot, rdK, 'UPHELD', 'R4-SEAT')
d0 = stage_report(rdK, eroot)
check('K1 基线: 完整链 deliverable=True',
      d0['deliverable'] is True and d0['review']['fresh'] is True)
vd = json.load(open(os.path.join(rdK, 'views_digest.json'),
                    encoding='utf-8'))
vd['views'][0]['institution_name'] = '篡改机构'
vd['views'][0]['report_title'] = '篡改标题'
json.dump(vd, open(os.path.join(rdK, 'views_digest.json'), 'w',
                   encoding='utf-8'), ensure_ascii=False)
d1 = stage_report(rdK, eroot)
full = open(os.path.join(rdK, 'FULL_REPORT.md'), encoding='utf-8').read()
check('K2 只改 views_digest 机构/标题 → 旧裁决失效+拒交付'
      '(渲染输入已变而摘要未变=反例闭合)',
      d1['deliverable'] is False and d1['review']['fresh'] is False
      and '篡改机构' in full, f"deliverable={d1['deliverable']} "
      f"fresh={d1['review']['fresh']}")

# FULL_REPORT 内容段篡改
rdK2 = make_run(tmp, 'k2')
aj.record_semantic_verdict(eroot, rdK2, 'UPHELD', 'R4-SEAT')
stage_report(rdK2, eroot)
fp = os.path.join(rdK2, 'FULL_REPORT.md')
txt = open(fp, encoding='utf-8').read().replace('机构A', '手改机构X')
open(fp, 'w', encoding='utf-8').write(txt)
d2 = stage_report(rdK2, eroot)
check('K3 FULL_REPORT 内容段被单改 → 拒交付(视图一致性)',
      d2['deliverable'] is False and d2['copies_consistent'] is False
      and any('FULL_REPORT' in w for w in d2.get('_warnings') or []),
      str(d2.get('_warnings')))

# 裁决推进不误伤(质量节合法变化不入内容段比对)
rdK3 = make_run(tmp, 'k3')
dx = stage_report(rdK3, eroot)             # 尚无裁决: 不可交付
aj.record_semantic_verdict(eroot, rdK3, 'UPHELD', 'R4-SEAT')
dy = stage_report(rdK3, eroot)             # 裁决落档后重跑
check('K4 裁决推进后重跑 report → copies 不误伤(内容段未变)',
      dy['deliverable'] is True and dy['copies_consistent'] is True,
      f"{dy.get('deliverable')}/{dy.get('copies_consistent')}")

# ══ L. R4-04 跨日归档保留完整裁决历史 ═══════════════════════════════
rdL = make_run(tmp, 'l1')
w1 = aj.record_semantic_verdict(eroot, rdL, 'REVISE', 'R4-SEAT')
w1 = move_to_day(eroot, w1, '20261115')
w2 = aj.record_semantic_verdict(eroot, rdL, 'REVISE', 'R4-SEAT')
w2 = move_to_day(eroot, w2, '20261116')
w3 = aj.record_semantic_verdict(eroot, rdL, 'UPHELD', 'R4-SEAT')  # 当日
arcL = os.path.join(tmp, 'arcL')
r = subprocess.run(
    [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'archive',
     '--report-dir', rdL, '--engine-root', eroot, '--archive-dir', arcL],
    cwd=ROOT, capture_output=True, text=True, timeout=180)
e = json.loads(r.stdout)
man = json.load(open(os.path.join(arcL, 'ARCHIVE_MANIFEST.json'),
                     encoding='utf-8'))
vfiles = sorted(os.listdir(os.path.join(arcL, 'verdicts')))
check('L1 跨日三档(两日 -01/-02 撞名) → 归档三档全保留(唯一名)',
      e['ok'] is True and len(vfiles) == 3 and len(set(vfiles)) == 3
      and man['verdicts_n'] == 3,
      f"ok={e['ok']} files={vfiles}")
check('L2 唯一名含日目录(basename 冲突消解)',
      all('__' in f and f.startswith(('20261115', '20261116', '20261117'))
          for f in vfiles), str(vfiles))
import hashlib as _hl
_sha_ok = all(
    e2['sha256'] == _hl.sha256(open(
        os.path.join(eroot, e2['source_rel']), 'rb').read()
    ).hexdigest()[:16] for e2 in man['verdict_chain'])
_pred_ok = all(
    e2['predecessor'] is None or e2['predecessor'] in
    {x['source_rel'] for x in man['verdict_chain']}
    for e2 in man['verdict_chain'])
_revs = [e2['revision'] for e2 in man['verdict_chain']]
check('L3 manifest 链: 逐档 sha256 对原件+predecessor 可解析+revision 递增',
      _sha_ok and _pred_ok and _revs == sorted(_revs) and len(_revs) == 3,
      f"sha={_sha_ok} pred={_pred_ok} revs={_revs}")
check('L4 终裁=UPHELD 且归档摘要三处一致',
      man['verdict'] == 'UPHELD'
      and man['content_sha256'] == aj.content_digest(rdL)
      == aj.content_digest(arcL), man['verdict'])

# ══ M. R4-05 必要/可选数据规则贯通 ═════════════════════════════════
_req_bad = [{'metric_id': 'GOLD', 'tier': 'required',
             'basis': '问题词面命中', 'spec': {'form': 'series',
             'min_observations': 12},
             'outcome': 'insufficient_coverage',
             'outcome_basis': '快照序列 n=1 < 最低覆盖12'}]
_req_ok = [{'metric_id': 'GOLD', 'tier': 'required',
            'basis': '问题词面命中', 'spec': {'form': 'series',
            'min_observations': 12},
            'outcome': 'satisfied', 'outcome_basis': '快照序列(n=120)'}]

# M1: 必要覆盖不足 → report 拒交付(即便旗标随档——attach 的显式越过
# 只把判断落到 degraded 档,交付门不认;机器面用合成挂态,真 attach
# 校验面由 F02/contract 套件锁定)
rdM1 = make_run(tmp, 'm1', run_ok=False, req_items=_req_bad,
                allow_flag=True)
d = stage_report(rdM1, eroot)
check('M1 必要覆盖不足(单点≠历史分析) → required_data_missing,'
      'report 拒交付(旗标不是万能放行)',
      d['deliverable'] is False and d['blocked_class']
      == 'required_data_missing',
      f"report={d.get('blocked_class')}/{d.get('deliverable')}")

# M2: 仅可选缺失+显式旗标 → 经独立审查可交付
rdM2 = make_run(tmp, 'm2', run_ok=False, req_items=_req_ok,
                allow_flag=True)
aj.record_semantic_verdict(eroot, rdM2, 'UPHELD', 'R4-SEAT')
d = stage_report(rdM2, eroot)
check('M2 仅可选缺失+旗标+有效独立审查 → 可交付(降级披露)',
      d['deliverable'] is True and d['blocked_class']
      == 'optional_data_missing' and d['degraded_ok'] is True
      and any('降级交付' in w for w in d.get('_warnings') or []),
      f"{d.get('deliverable')}/{d.get('blocked_class')}/"
      f"{d.get('degraded_ok')}")

# M3: 无旗标的可选缺失 → attach 拒
rdM3 = make_run(tmp, 'm3', run_ok=False, req_items=_req_ok,
                allow_flag=False)
res = aj.attach_judgment(
    rdM3, os.path.join(rdM3, 'agent_judgment.json'), root=eroot)
check('M3 可选缺失无旗标 → attach 默认拒(blocked=run_ok_false)',
      res.get('attached') is False and res.get('blocked') == 'run_ok_false'
      and res.get('blocked_class') == 'optional_data_missing',
      str(res.get('blocked_class')))

# M4: critical 恒拒(L1=0)
rdM4 = make_run(tmp, 'm4', run_ok=False, l1_rows=0, req_items=[],
                allow_flag=True)
res = aj.attach_judgment(
    rdM4, os.path.join(rdM4, 'agent_judgment.json'), root=eroot,
    allow_failed_run=True)
d = stage_report(rdM4, eroot)
check('M4 critical_zero_evidence → 旗标也不放行',
      res.get('blocked_class') == 'critical_zero_evidence'
      and res.get('attached') is False and d['deliverable'] is False,
      f"{res.get('blocked_class')}/{d.get('deliverable')}")

# M5: 分类唯一规范源(blocked_class_of)
rjM = json.load(open(os.path.join(rdM1, 'report.json'), encoding='utf-8'))
check('M5 blocked_class_of 单源: M1 档复算=required_data_missing',
      aj.blocked_class_of(rjM) == 'required_data_missing',
      str(aj.blocked_class_of(rjM)))

# ══ §N: outcome 判定数据源序(R4-06 波内缺陷回归——仅查快照会把采集档 ══
#    序列误判「仅最新单点」, 抽函数 _evaluate_data_requirements 可测化)
print('§N outcome 判定数据源序(快照→S4 信封→L1/S3 单点→缺席)')


def _s4_step(mid, n, ok=True, source='采集档 macro_20261114.json'):
    env = {'data': {'series': {'n': n, 'source': source}}} if ok else None
    return {'step': f'S4_history_{mid}', 'ok': ok, 'envelope': env}


N_snap = {'series_store': {'GOLD_F': {'dates': ['d'] * 2514,
                                       'values': [1.0] * 2514}}}
N_steps = [_s4_step('BEI_10Y', 2499), _s4_step('CN_PMI_MFG', 1),
           {'step': 'S4_history_DEAD', 'ok': False, 'envelope': None}]
N_l1 = [{'metric_id': 'CN_PMI_MFG'}, {'metric_id': 'DEAD_M'}]
items_n = {i['metric_id']: i for i in ro._evaluate_data_requirements(
    ['GOLD_F', 'BEI_10Y', 'CN_PMI_MFG', 'DEAD_M', 'NOWHERE_M'],
    N_steps, N_snap, N_l1)}
check('N1 快照序列 n≥min → satisfied(源=研究快照)',
      items_n['GOLD_F']['outcome'] == 'satisfied'
      and '研究快照' in items_n['GOLD_F']['outcome_basis'],
      str(items_n['GOLD_F']))
check('N2 快照缺席+S4 信封 n=2499 → satisfied(BEI 回归案: 源=采集档)',
      items_n['BEI_10Y']['outcome'] == 'satisfied'
      and '采集档' in items_n['BEI_10Y']['outcome_basis'],
      str(items_n['BEI_10Y']))
check('N3 S4 信封 n=1 → insufficient_coverage(单点/短序列)',
      items_n['CN_PMI_MFG']['outcome'] == 'insufficient_coverage',
      str(items_n['CN_PMI_MFG']))
check('N4 S4 失败但 L1 单点在场 → insufficient_coverage(点≠历史)',
      items_n['DEAD_M']['outcome'] == 'insufficient_coverage',
      str(items_n['DEAD_M']))
check('N5 全源缺席 → missing',
      items_n['NOWHERE_M']['outcome'] == 'missing',
      str(items_n['NOWHERE_M']))
check('N6 规格冻结面(spec 四键+min_observations=12)',
      items_n['GOLD_F']['spec'].get('min_observations') == 12
      and set(items_n['GOLD_F']['spec']) >= {'form', 'window', 'quality'},
      str(items_n['GOLD_F']['spec']))

# ══ 汇总 ═══════════════════════════════════════════════════════════
print('═' * 64)
print(f'Audit-R4 判定: {PASS} PASS / {FAIL} FAIL')
print('═' * 64)
sys.exit(1 if FAIL else 0)
