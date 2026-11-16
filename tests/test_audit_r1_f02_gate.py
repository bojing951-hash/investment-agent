#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R1 F02 + Audit-R2 条目1/2 回归: 独立审查四态门(生成≠校验≠审查≠可交付)。

外审复现的缺陷: report 段 L3/L4 produced=true + semantic_review.required=true
且 verdict=REVISE 时仍返回 ok=true、warnings 空——「已生成」冒充「可交付」。

Audit-R2 三审新增面(条目1/2):
  F. 内容绑定同源: content_digest=canonical(report.json)+judgment——
     只改 report.json 的 L3/事实/run_ok 即失效旧裁决(反例①);
  G. 裁决顺序与非法记录: 内容序(revision/recorded_at)非 mtime——
     旧 PASS+新 REVISE 拒绝;最新档损坏拒绝(不回退旧 PASS);
     revision 重复拒绝;调换 mtime 结果不变(反例②③④);
  H. 多副本一致与当前运行态: report.md 与 report.json 渲染不同版=
     拒绝交付;attach 后 run_ok 翻 False=拒绝交付(不沿用旧 attach
     成功);重绑(内容未变摘要口径迁移)机器可验。

本套件锁(Audit-R1 原面):
  A. 四态分立: generated / machine_verified / review / deliverable;
  B. required 且审查缺席/REVISE/未绑定哈希(过期)→ ok=false + warnings
     非空 + exit 1;VERIFIED+fresh → ok=true;
  C. 修订链: 正文修订→旧裁决 fresh=False→复验新档→verdicts_n 累计,
     旧失败档不覆盖;
  D. 降级分级: critical_zero_evidence 旗标不放行;optional_data_missing
     须旗标且放行后落 validation 阶段(不再 run_ok 拦);
  E. produced=False → 不 required,但 machine_verified=False 仍不可交付。
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import agent_judgment as aj          # noqa: E402
import research_orchestrator as ro   # noqa: E402

PASS, FAIL = 0, 0
_RUN_SEQ = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    print(f"  {'✅' if cond else '❌'} {name}" + (f" — {detail}" if detail and not cond else ''))
    PASS, FAIL = PASS + (1 if cond else 0), FAIL + (0 if cond else 1)


def make_run(tmp, name, *, run_ok=True, l1_rows=2, produced=True,
             validation_passed=True, run_ts=None, attach_meta=True):
    global _RUN_SEQ
    if run_ts is None:
        # 裁决匹配按 run.ts_utc 键控——每个合成 run 须独立 ts 命名空间,
        # 否则他 run 的裁决档泄入本 run 的 verdicts_n/修订链
        _RUN_SEQ += 1
        run_ts = '20261116T12%04dZ' % _RUN_SEQ
    rd = os.path.join(tmp, name)
    os.makedirs(rd, exist_ok=True)
    rows = [{'metric_id': 'TEST_M%d' % i, 'value': 1.0 * i, 'unit': 'x',
             'observation_date': '2026-11-09', 'quality_status': 'OK',
             'source': {'id': 'src%d' % i, 'kind': 'synthetic'}}
            for i in range(l1_rows)]
    report = {
        'schema_version': '2.0', 'pipeline_version': 't',
        'run': {'question': '审计回归合成问题', 'ts_utc': run_ts,
                'git_head': 'synthetic',
                'degradation_policy': {
                    'critical_zero_evidence': 'L1=0 拒收,旗标不放行',
                    'optional_data_missing': 'L1 在场+诚实拒答须旗标'}},
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
        'notes': [], 'run_ok': run_ok}
    if attach_meta:
        report['agent_judgment'] = {
            'attached': True, 'judgment_file': 'judgment.json',
            'validation': {'passed': validation_passed, 'violations': []},
            'run_ok_at_attach': True if run_ok else True}
    json.dump(report, open(os.path.join(rd, 'report.json'), 'w',
                           encoding='utf-8'), ensure_ascii=False)
    json.dump({'schema_version': aj.JUDGMENT_SCHEMA_VERSION,
               'agent_declaration': {'role': 'synthetic'},
               'l3': {'claims': []}, 'l4': {'scenarios': []}},
              open(os.path.join(rd, 'agent_judgment.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    # Audit-R2 条目1: report.md=report.json 的真实渲染(生产不变式
    # _write_report 两视图一原子语义;copies_consistent 门按此核)
    open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8').write(
        ro._render_md(report))
    return rd


def write_verdict(root, rd, overall, sha=None, run_ts=None, legacy=False,
                  revision=None, recorded_at=None):
    if run_ts is None:
        # 与生产一致: 裁决档文件名内嵌该 run 的 ts_utc(匹配键)
        run_ts = json.load(open(os.path.join(rd, 'report.json'),
                                encoding='utf-8'))['run']['ts_utc']
    day = '20261116'
    d = os.path.join(root, 'audit', 'semantic_review', day)
    os.makedirs(d, exist_ok=True)
    seq = len([f for f in os.listdir(d) if run_ts in f]) + 1
    doc = {'overall': overall, 'reviewer': 'SYNTH-SEAT', 'notes': '',
           'run_ts': run_ts,
           'recorded_at': recorded_at or '2026-11-16T12:00:00Z'}
    if revision is not None:
        doc['revision'] = revision
    if not legacy:
        doc['content_sha256'] = sha or aj.content_digest(rd)
    p = os.path.join(d, 'VERDICT-%s-%02d.json' % (run_ts, seq))
    json.dump(doc, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    return p


def report_stage(rd, engine_root):
    return subprocess.run(
        [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'report',
         '--report-dir', rd, '--engine-root', engine_root],
        cwd=ROOT, capture_output=True, text=True, timeout=120)


def attach_stage(rd, engine_root, allow=False):
    j = os.path.join(rd, 'agent_judgment.json')
    argv = [sys.executable, 'ia_cli.py', 'research-one', '--stage', 'attach',
            '--report-dir', rd, '--judgment', j,
            '--engine-root', engine_root]
    if allow:
        argv.append('--allow-failed-run')
    return subprocess.run(argv, cwd=ROOT, capture_output=True, text=True,
                          timeout=120)


print('═' * 64)
print('F02 独立审查四态门回归')
print('═' * 64)

tmp = tempfile.mkdtemp(prefix='f02_')
eroot = os.path.join(tmp, 'engine')
os.makedirs(eroot, exist_ok=True)
# attach 放行路径会真调 validate_judgment → 读 engine_root 指标注册表
# (合成引擎根补真注册表副本;裁决档仍只落合成根,不污染仓库)
os.makedirs(os.path.join(eroot, 'config'), exist_ok=True)
shutil.copy(os.path.join(ROOT, 'config', 'metric_registry.json'),
            os.path.join(eroot, 'config', 'metric_registry.json'))

# ── A/B: required+缺席 → 不可交付 ──
rd1 = make_run(tmp, 'r1')
r = report_stage(rd1, eroot)
e1 = json.loads(r.stdout)
check('A1 required+审查缺席 → ok=false+exit1',
      e1['ok'] is False and r.returncode == 1)
check('A2 warnings 非空且指明审查缺席',
      e1['warnings'] and '缺席' in e1['warnings'][0])
check('A3 四态齐(generated/machine_verified/review/deliverable)',
      e1['data']['generated'] is True and e1['data']['machine_verified'] is True
      and e1['data']['review']['required'] is True
      and e1['data']['deliverable'] is False)

# ── B: REVISE → 不可交付 ──
rd2 = make_run(tmp, 'r2')
write_verdict(eroot, rd2, 'REVISE')
e2 = json.loads(report_stage(rd2, eroot).stdout)
check('B1 verdict=REVISE → ok=false+deliverable=false',
      e2['ok'] is False and e2['data']['deliverable'] is False)
check('B2 warning 点名 REVISE',
      any('REVISE' in w for w in e2['warnings']))

# ── B: VERIFIED+fresh → 可交付 ──
rd3 = make_run(tmp, 'r3')
write_verdict(eroot, rd3, 'VERIFIED')
e3 = json.loads(report_stage(rd3, eroot).stdout)
check('B3 VERIFIED+绑定哈希匹配 → ok=true+exit0',
      e3['ok'] is True and e3['data']['deliverable'] is True)
check('B4 mvp_complete 与 deliverable 同步',
      e3['data']['mvp_complete'] is True)

# ── C: 修订链(正文修订→旧裁决过期→复验新档) ──
# Audit-R2 反例①: 修订=只改 report.json 的 L3 结论(渲染源)——旧裁决
# 必须失效(md/judgment 均不动,旧口径下这正是漏放行的绕行面)
rd4 = make_run(tmp, 'r4')
write_verdict(eroot, rd4, 'VERIFIED')
rj4 = json.load(open(os.path.join(rd4, 'report.json'), encoding='utf-8'))
rj4['layers']['L3_AI推断层']['note'] = '修订: L3 结论变更(旧裁决应失效)'
json.dump(rj4, open(os.path.join(rd4, 'report.json'), 'w', encoding='utf-8'),
          ensure_ascii=False)
open(os.path.join(rd4, 'report.md'), 'w', encoding='utf-8').write(
    ro._render_md(rj4))   # 连渲染视图一起改=最高对抗面,摘要仍须失效
e4a = json.loads(report_stage(rd4, eroot).stdout)
check('C1 只改 report.json 的 L3 → 旧 VERIFIED 过期(fresh=False)',
      e4a['ok'] is False and e4a['data']['review']['fresh'] is False)
check('C2 过期 warning 在档', any('过期' in w for w in e4a['warnings']))
write_verdict(eroot, rd4, 'VERIFIED')
e4b = json.loads(report_stage(rd4, eroot).stdout)
check('C3 复验新档 → 可交付+修订链计数=2+旧档不覆盖',
      e4b['ok'] is True and e4b['data']['review']['verdicts_n'] == 2
      and len(e4b['data']['review'].get('prior_verdicts', [])) == 1)

# ── B: 旧档无绑定键(legacy) → 在场不冒充新鲜 ──
rd5 = make_run(tmp, 'r5')
write_verdict(eroot, rd5, 'VERIFIED', legacy=True)
e5 = json.loads(report_stage(rd5, eroot).stdout)
check('B5 legacy 裁决无哈希绑定 → fresh=None 不可交付',
      e5['ok'] is False and e5['data']['review']['fresh'] is None)

# ── D: 降级分级 ──
rd6 = make_run(tmp, 'r6', run_ok=False, l1_rows=0)
d6 = json.loads(attach_stage(rd6, eroot, allow=True).stdout)['data']
check('D1 critical_zero_evidence: 旗标亦不放行',
      d6.get('attached') is False
      and d6.get('blocked_class') == 'critical_zero_evidence')
rd7 = make_run(tmp, 'r7', run_ok=False, l1_rows=2)
d7a = json.loads(attach_stage(rd7, eroot, allow=False).stdout)['data']
check('D2 optional: 无旗标拦截', d7a.get('attached') is False
      and d7a.get('blocked_class') == 'optional_data_missing')
d7b = json.loads(attach_stage(rd7, eroot, allow=True).stdout)['data']
check('D3 optional: 有旗标放行至校验层(不再 run_ok 拦)',
      d7b.get('blocked') is None and d7b.get('validation_passed') is False)

# ── E: produced=False → 不 required 但仍不可交付 ──
rd8 = make_run(tmp, 'r8', produced=False)
e8 = json.loads(report_stage(rd8, eroot).stdout)
check('E1 produced=False → required=false 但 ok=false(L3/L4 未全)',
      e8['data']['review']['required'] is False and e8['ok'] is False)

# ══ Audit-R2 条目1/2 反例面 ══════════════════════════════════════

# ── F: 内容绑定同源(只改事实值/run_ok 同样失效;改渲染视图单独拦) ──
rd9 = make_run(tmp, 'r9')
write_verdict(eroot, rd9, 'VERIFIED')
rj9 = json.load(open(os.path.join(rd9, 'report.json'), encoding='utf-8'))
rj9['layers']['L1_事实层']['rows'][0]['value'] = 999.0   # 改事实值
json.dump(rj9, open(os.path.join(rd9, 'report.json'), 'w', encoding='utf-8'),
          ensure_ascii=False)
e9 = json.loads(report_stage(rd9, eroot).stdout)
check('F1 只改 L1 事实值 → 旧裁决失效+不可交付',
      e9['data']['review']['fresh'] is False
      and e9['data']['deliverable'] is False)

rd10 = make_run(tmp, 'r10')
write_verdict(eroot, rd10, 'VERIFIED')
rj10 = json.load(open(os.path.join(rd10, 'report.json'),
                      encoding='utf-8'))
rj10['run_ok'] = False    # 运行态翻失败(attach 元数据不动)
json.dump(rj10, open(os.path.join(rd10, 'report.json'), 'w',
                     encoding='utf-8'), ensure_ascii=False)
e10 = json.loads(report_stage(rd10, eroot).stdout)
check('F2 attach 后 run_ok 翻 False → 不可交付(不沿用旧 attach 成功)',
      e10['data']['machine_verified'] is False
      and e10['data']['deliverable'] is False
      and e10['data']['review']['fresh'] is False)

# ── G: 裁决顺序与非法记录(内容序,非 mtime) ──
# G1 旧 PASS + 新 REVISE(新档 recorded_at 更晚)→ 拒绝交付
rd11 = make_run(tmp, 'r11')
write_verdict(eroot, rd11, 'VERIFIED', recorded_at='2026-11-16T10:00:00Z')
write_verdict(eroot, rd11, 'REVISE', recorded_at='2026-11-16T11:00:00Z')
e11 = json.loads(report_stage(rd11, eroot).stdout)
check('G1 旧 PASS+新 REVISE → verdict=REVISE 拒绝交付',
      e11['data']['review']['verdict'] == 'REVISE'
      and e11['data']['deliverable'] is False)

# G2 最新档损坏(不可解析)→ 拒绝,不回退旧 PASS
rd12 = make_run(tmp, 'r12')
write_verdict(eroot, rd12, 'VERIFIED', recorded_at='2026-11-16T10:00:00Z')
day_dir = os.path.join(eroot, 'audit', 'semantic_review', '20261116')
ts12 = json.load(open(os.path.join(rd12, 'report.json'),
                      encoding='utf-8'))['run']['ts_utc']
bad = os.path.join(day_dir, 'VERDICT-%s-99.json' % ts12)
open(bad, 'w', encoding='utf-8').write('{ 损坏 JSON')
e12 = json.loads(report_stage(rd12, eroot).stdout)
check('G2 最新档损坏 → error=corrupt_latest 拒绝(不回退旧 PASS)',
      e12['data']['review'].get('error') == 'corrupt_latest'
      and e12['data']['review']['verdict'] is None
      and e12['data']['deliverable'] is False)

# G3 最新档缺 overall(可解析但缺字段)→ 同样拒绝
rd13 = make_run(tmp, 'r13')
write_verdict(eroot, rd13, 'VERIFIED', recorded_at='2026-11-16T10:00:00Z')
ts13 = json.load(open(os.path.join(rd13, 'report.json'),
                      encoding='utf-8'))['run']['ts_utc']
nofield = os.path.join(day_dir, 'VERDICT-%s-98.json' % ts13)
json.dump({'reviewer': 'SYNTH-SEAT', 'run_ts': ts13,
           'recorded_at': '2026-11-16T12:00:00Z'},
          open(nofield, 'w', encoding='utf-8'), ensure_ascii=False)
e13 = json.loads(report_stage(rd13, eroot).stdout)
check('G3 最新档缺 overall → corrupt_latest 拒绝',
      e13['data']['review'].get('error') == 'corrupt_latest'
      and e13['data']['deliverable'] is False)

# G4 revision 同号重复 → 冲突拒绝
rd14 = make_run(tmp, 'r14')
write_verdict(eroot, rd14, 'VERIFIED', revision=1,
              recorded_at='2026-11-16T10:00:00Z')
write_verdict(eroot, rd14, 'VERIFIED', revision=1,
              recorded_at='2026-11-16T11:00:00Z')
e14 = json.loads(report_stage(rd14, eroot).stdout)
check('G4 revision 重复 → duplicate_revision 拒绝',
      e14['data']['review'].get('error') == 'duplicate_revision'
      and e14['data']['deliverable'] is False)

# G5 调换 mtime → 结果不变(VERIFIED 在前 REVISE 在后,把 REVIEV 档
# mtime 拨早/VERIFIED 拨晚,裁决仍=最新内容序的 REVISE)
rd15 = make_run(tmp, 'r15')
p15a = write_verdict(eroot, rd15, 'VERIFIED',
                     recorded_at='2026-11-16T10:00:00Z')
p15b = write_verdict(eroot, rd15, 'REVISE',
                     recorded_at='2026-11-16T11:00:00Z')
os.utime(p15a, (2000000000, 2000000000))   # 旧档 mtime 拨到未来
os.utime(p15b, (1000000000, 1000000000))   # 新档 mtime 拨到过去
e15 = json.loads(report_stage(rd15, eroot).stdout)
check('G5 调换 mtime 结果不变(内容序 REVISE 仍胜)',
      e15['data']['review']['verdict'] == 'REVISE'
      and e15['data']['review'].get('error') is None
      and e15['data']['deliverable'] is False)

# ── H: 多副本一致 + 重绑迁移 ──
# H1 只改渲染视图(report.md)不改源 → 摘要可 fresh 但副本不一致=拒绝
rd16 = make_run(tmp, 'r16')
write_verdict(eroot, rd16, 'VERIFIED')
open(os.path.join(rd16, 'report.md'), 'a', encoding='utf-8').write(
    '\n篡改段: 只改渲染视图。\n')
e16 = json.loads(report_stage(rd16, eroot).stdout)
check('H1 report.md 单独改动 → copies_consistent=False 拒绝交付',
      e16['data']['review']['fresh'] is True
      and e16['data'].get('copies_consistent') is False
      and e16['data']['deliverable'] is False)

# H2 重绑迁移: 内容未变 → 重绑成功恢复 fresh;内容已变 → 拒绝机械重绑
rd17 = make_run(tmp, 'r17')
legacy_sha = aj.content_digest_v1(rd17)
write_verdict(eroot, rd17, 'UPHELD', sha=legacy_sha,
              recorded_at='2026-11-16T10:00:00Z')
e17a = json.loads(report_stage(rd17, eroot).stdout)
check('H2a v1 锚在 v2 口径下不新鲜(fresh=False 不可交付)',
      e17a['data']['review']['fresh'] is False
      and e17a['data']['deliverable'] is False)
rebind_p = aj.rebind_verdict_digest(
    eroot, rd17, 'Audit-R2 摘要口径迁移回归')
e17b = json.loads(report_stage(rd17, eroot).stdout)
check('H2b 内容未变重绑 → fresh=True 可交付+rebind 档在场',
      os.path.isfile(rebind_p)
      and e17b['data']['review']['fresh'] is True
      and e17b['data']['deliverable'] is True)
rj17 = json.load(open(os.path.join(rd17, 'report.json'),
                      encoding='utf-8'))
rj17['layers']['L3_AI推断层']['note'] = '内容已变(重绑必须拒绝)'
json.dump(rj17, open(os.path.join(rd17, 'report.json'), 'w',
                     encoding='utf-8'), ensure_ascii=False)
open(os.path.join(rd17, 'report.md'), 'w', encoding='utf-8').write(
    ro._render_md(rj17))
try:
    aj.rebind_verdict_digest(eroot, rd17, '不应成功')
    g = False
except ValueError:
    g = True
check('H2c 内容已变 → 机械重绑抛 ValueError(须独立复验)', g)

# H3 生产写档面: record_semantic_verdict 带 revision/predecessor 续链
# (席位词表: 放行词=UPHELD;VERIFIED 是四态门词,席位档不认——H5 反例)
rd18 = make_run(tmp, 'r18')
pa = aj.record_semantic_verdict(eroot, rd18, 'REVISE', 'SYNTH-SEAT')
pb = aj.record_semantic_verdict(eroot, rd18, 'UPHELD', 'SYNTH-SEAT')
da = json.load(open(pa, encoding='utf-8'))
db = json.load(open(pb, encoding='utf-8'))
e18 = json.loads(report_stage(rd18, eroot).stdout)
check('H3 生产裁决档 revision 续链+predecessor 指前档+最新档胜出',
      da['revision'] == 1 and db['revision'] == 2
      and db['predecessor'] == os.path.relpath(pa, eroot)
      and e18['data']['review']['verdict'] == 'UPHELD'
      and e18['data']['deliverable'] is True)
try:
    aj.record_semantic_verdict(eroot, rd18, '', 'SYNTH-SEAT')
    g2 = False
except ValueError:
    g2 = True
check('H4 裁决必填字段缺失 → 落档即抛(损坏档不落盘)', g2)
try:
    aj.record_semantic_verdict(eroot, rd18, 'VERIFIED', 'SYNTH-SEAT')
    g3 = False
except ValueError:
    g3 = True
check('H5 越表裁决词(VERIFIED≠席位词表) → 落档即抛(词表合规收口)', g3)

# ══ Audit-R2 条目7: 运行前冻结的数据需求分级 ════════════════════════

def _inject_reqs(rd, items):
    """合成 run 注入 plan 段冻结的 data_requirements(生产=采集前落档)。"""
    rj = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
    rj['run']['data_requirements'] = {
        'frozen_at': 'plan(采集前冻结;分类不随采集结果改判)',
        'items': items, 'optional_face': {}}
    json.dump(rj, open(os.path.join(rd, 'report.json'), 'w', encoding='utf-8'),
              ensure_ascii=False)
    open(os.path.join(rd, 'report.md'), 'w', encoding='utf-8').write(
        ro._render_md(rj))
    return rj

_REQ_MISS = [{'metric_id': 'TEST_M0', 'tier': 'required',
              'basis': '问题词面命中(任务目标)', 'outcome': 'missing',
              'outcome_basis': 'L1/S3/快照序列均缺席'}]

# I1 必要指标缺席(问题命中,运行前声明)→ 新分级 required_data_missing
rd19 = make_run(tmp, 'r19', run_ok=False, l1_rows=2)
_inject_reqs(rd19, _REQ_MISS)
d19a = json.loads(attach_stage(rd19, eroot, allow=False).stdout)['data']
check('I1 必要缺席 → blocked_class=required_data_missing(默认阻塞)',
      d19a.get('attached') is False
      and d19a.get('blocked_class') == 'required_data_missing')
d19b = json.loads(attach_stage(rd19, eroot, allow=True).stdout)['data']
check('I2 显式 --allow-failed-run → 过此级至校验层(与 D3 同语义,'
      '旗标越过不等于免校验)',
      d19b.get('blocked') is None and d19b.get('blocked_class') is None
      and d19b.get('validation_passed') is False)

# I3 必要项在场且满足 → 不得因「声明过必要」而阻塞(分级看 outcome)
rd20 = make_run(tmp, 'r20', run_ok=False, l1_rows=2)
_inject_reqs(rd20, [dict(_REQ_MISS[0], outcome='satisfied',
                         outcome_basis='L1 行在场')])
d20 = json.loads(attach_stage(rd20, eroot, allow=False).stdout)['data']
check('I3 必要项已满足 → 仍 optional_data_missing(分级不冤枉)',
      d20.get('attached') is False
      and d20.get('blocked_class') == 'optional_data_missing')

# I4 报告面披露: 运行前冻结声明+任务目标缺口逐条在场(不事后缩减)
md19 = open(os.path.join(rd19, 'report.md'), encoding='utf-8').read()
check('I4 渲染披露 数据需求(运行前冻结)+任务目标缺口逐条',
      '数据需求(运行前冻结)' in md19
      and '任务目标缺口: TEST_M0' in md19
      and '未事后缩减' in md19)

print(f"\nF02 判定: {PASS} PASS / {FAIL} FAIL")
sys.exit(0 if FAIL == 0 else 1)
