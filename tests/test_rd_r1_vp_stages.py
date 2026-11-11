#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1(autonomous-rd 2026-11-11): VP v1.1 三型证据落库验收套件。

覆盖面:
[1] 阶段关系机械规则(_stage_relation_a/_stage_relation_b 单元表)
[2] 机构明示方向提取(_hypothesis_directions: 词表/映射对齐/不猜纪律)
[3] 阶段标签(_stage_label: 有判行映射/零判行=INSUFFICIENT)
[4] validate_vp v1.1 合同(结构/聚合一致/1.0 兼容/坏档拒绝)
[5] research_map QUESTION_COMMANDS 可执行性(ia_cli build_parser 实解析;
    含 R1 修复回归: --metric-a/--metric-b/analog --metric 禁再出现)
[6] 真实数据集成(build_vp on 真仓;CI 干净 clone 无 data/daily 快照时
    按既有惯例 SKIP 并说明——真实面在本机全量套件执行)
纪律: 预期值不经被测函数自算;C 层契约(view_label/label)不变性是断言对象。
"""
import io
import json
import os
import shlex
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL, SKIP = 0, 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def skip(name, why):
    global SKIP
    SKIP += 1
    print(f"  ⏭ {name} {why}")


import view_plausibility as vpl  # noqa: E402
import view_verifier as vv       # noqa: E402

print("═" * 60)
print("[1] 阶段关系机械规则(假设证据评价,非预测验证)")
print("═" * 60)
ra = vpl._stage_relation_a
check("A: 无方向→None+不判",
      ra({'1y': {'pct_change': 2.0}}, None)[0] is None)
check("A: hint=up 窗口1y升→supports",
      ra({'1y': {'pct_change': 2.0}}, 'up')[0] == 'supports')
check("A: hint=up 窗口全降→against",
      ra({'1y': {'pct_change': -2.0}, '3m': {'pct_change': -0.5}},
         'up')[0] == 'against')
check("A: 无可用变动→None(诚实缺席)",
      ra({}, 'up')[0] is None and ra({'1m': {'available': False}}, 'up')[0] is None)
check("A: 净变动=0→neutral(无判别力)",
      ra({'1y': {'pct_change': 0.0}}, 'up')[0] == 'neutral')

rb = vpl._stage_relation_b
check("B: 无方向→None", rb({'pp_change': 0.25}, None)[0] is None)
check("B: available=False→None+原因",
      rb({'available': False, 'reason': '无序列'}, 'up')[0] is None)
check("B: pp +0.25 hint up→supports",
      rb({'pp_change': 0.25}, 'up')[0] == 'supports')
check("B: pct -1.2 hint up→against",
      rb({'pct_change': -1.2}, 'up')[0] == 'against')
check("B: 净0→neutral", rb({'abs_change': 0}, 'up')[0] == 'neutral')

print("═" * 60)
print("[2] 机构明示方向提取(确定性,零AI判断)")
print("═" * 60)
VIEW_FIX = {
    'view_id': 'VIEW-20261110-099', 'publish_date': '2026-10-28',
    'forecasts': [
        {'target': '美国工业产出', 'value_or_direction': '下半年低于趋势下行',
         'horizon': '6m'},
        {'target': '美国GDP', 'value_or_direction': '2.1%', 'horizon': '12m'},
        {'target': '未映射目标', 'value_or_direction': '走弱', 'horizon': '3m'}]}
TMAP_FIX = {'targets': {'美国工业产出': 'INDPRO', '美国GDP': 'US_REAL_GDP'}}
hyp = {'metric_refs': [{'metric_id': 'INDPRO', 'direction': None,
                        'segment': 'publish→horizon_end'}],
       'evidence': {'mode': 'C', 'linked_forecasts': [0, 1]}}
dirs, prov = vpl._hypothesis_directions(hyp, VIEW_FIX, TMAP_FIX)
check("方向词表解析: '下行'→down 且只落在对齐 metric",
      dirs == {'INDPRO': 'down'}, str(dirs))
check("provenance 带引文+机构明示标记",
      prov.get('INDPRO', {}).get('attribution') == 'institution_stated'
      and '低于' in prov.get('INDPRO', {}).get('quote', ''))
check("点位型('2.1%')不产方向(不猜)", 'US_REAL_GDP' not in dirs)
hyp2 = {'metric_refs': [{'metric_id': 'INDPRO', 'direction': 'up',
                         'segment': 'x'}],
        'evidence': {}}
dirs2, _ = vpl._hypothesis_directions(hyp2, VIEW_FIX, TMAP_FIX)
check("metric_ref 显式方向优先(不被 forecast 覆盖)",
      dirs2 == {'INDPRO': 'up'})
hyp3 = {'metric_refs': [{'metric_id': 'X', 'direction': None, 'segment': 'x'}],
        'evidence': {'linked_forecasts': [2]}}
dirs3, _ = vpl._hypothesis_directions(hyp3, VIEW_FIX, TMAP_FIX)
check("方向词但目标未映射→不采用(防错配)", dirs3 == {})
check("linked_forecasts 越界容忍(1-based 兼容不崩)",
      isinstance(vpl._hypothesis_directions(
          {'metric_refs': [], 'evidence': {'linked_forecasts': [99]}},
          VIEW_FIX, TMAP_FIX)[0], dict))

print("═" * 60)
print("[3] 阶段标签(有判行映射/零判行=INSUFFICIENT)")
print("═" * 60)
sl = vpl._stage_label
check("supports+against→MIXED(最保守聚合复用)",
      sl([{'relation': 'supports'}, {'relation': 'against'}])[0] == 'MIXED')
check("全supports→SUPPORTED",
      sl([{'relation': 'supports'}])[0] == 'SUPPORTED')
check("零判行→INSUFFICIENT_EVIDENCE(不猜)",
      sl([{'relation': None}, {'relation': 'neutral'}])[0]
      == 'INSUFFICIENT_EVIDENCE')

print("═" * 60)
print("[4] validate_vp v1.1 合同")
print("═" * 60)
GOOD_VIEW = {'view_id': 'VIEW-20261110-099',
             'core_views': [{'statement': '美国经济将温和放缓'}],
             'key_assumptions': []}


def mk11(stage_a=('SUPPORTED',), stage_b=('INSUFFICIENT_EVIDENCE',),
         summary_a=None, ver='1.1'):
    hyps = [{'ref': {'kind': 'core_view', 'index': 0,
                     'statement_digest': '美国经济将温和放缓'},
             'metric_refs': [{'metric_id': 'INDPRO', 'direction': 'up',
                              'segment': 'publish→horizon_end'}],
             'label': 'NOT_YET_TESTABLE',
             'evidence': {'mode': 'C', 'verdict': 'NOT_YET_TESTABLE'},
             'stages': {'A': {'rows': [], 'n_rows': 0, 'n_judged': 0},
                        'B': {'rows': [], 'n_rows': 0, 'n_judged': 0}},
             'stage_labels': {'A': stage_a[0], 'B': stage_b[0]}}]
    sa = summary_a if summary_a is not None else stage_a[0]
    return {'schema_version': ver, 'view_id': 'VIEW-20261110-099',
            'generated_by': 'engine:test', 'as_of': '20261111',
            'hypotheses': hyps,
            'view_label': vpl.rollup_view_label([h['label'] for h in hyps]),
            'stage_summary': {'A': sa, 'B': stage_b[0],
                              'C': vpl.rollup_view_label(
                                  [h['label'] for h in hyps])}}


ok, errs = vpl.validate_vp(mk11(), GOOD_VIEW)
check("v1.1 合规档通过(含 stages/stage_labels/stage_summary)", ok, str(errs))
# 1.0 兼容: 老档(无 stages)仍按旧合同通过
doc10 = {'schema_version': '1.0', 'view_id': 'VIEW-20261110-099',
         'generated_by': 'agent_orchestration', 'as_of': '20261110',
         'hypotheses': [dict(mk11()['hypotheses'][0],
                             stages=None, stage_labels=None)],
         'view_label': 'NOT_YET_TESTABLE'}
for h in doc10['hypotheses']:
    h.pop('stages'), h.pop('stage_labels')
ok, errs = vpl.validate_vp(doc10, GOOD_VIEW)
check("v1.0 老档兼容通过(无 stages 不校验新面)", ok, str(errs))
ok, errs = vpl.validate_vp(mk11(summary_a='SUPPORTEDxxx'), GOOD_VIEW)
check("stage_summary 与聚合不符→拒绝", not ok and any(
    'stage_summary' in e for e in errs), str(errs))
bad = mk11()
bad['stage_summary']['C'] = 'SUPPORTED'
ok, errs = vpl.validate_vp(bad, GOOD_VIEW)
check("stage_summary.C≠view_label→拒绝(C 契约不变)", not ok, str(errs))
bad2 = mk11()
bad2['hypotheses'][0]['stage_labels']['A'] = 'PROBABLY'
ok, errs = vpl.validate_vp(bad2, GOOD_VIEW)
check("stage_labels 越六标签→拒绝", not ok, str(errs))
ok, errs = vpl.validate_vp(mk11(ver='1.2'), GOOD_VIEW)
check("schema 1.2→拒绝", not ok, str(errs))

print("═" * 60)
print("[5] research_map 命令清单可执行性(实解析 ia_cli parser)")
print("═" * 60)
import ia_cli                     # noqa: E402
import research_map as rm         # noqa: E402
parser = ia_cli.build_parser()
n_cmd, n_bad = 0, 0
for rq, cmds in rm.QUESTION_COMMANDS.items():
    for c in cmds:
        if not c.startswith('ia_cli.py'):
            continue
        n_cmd += 1
        try:
            with redirect_stdout(io.StringIO()):
                parser.parse_args(shlex.split(c)[1:])
        except SystemExit:
            n_bad += 1
            print(f"  ❌ {rq}: {c} 无法解析")
check(f"全部 ia_cli 命令实解析通过({n_cmd} 条)", n_bad == 0)
all_cmds = ' '.join(c for cs in rm.QUESTION_COMMANDS.values() for c in cs)
check("R1 修复回归: --metric-a/--metric-b 不再出现",
      '--metric-a' not in all_cmds and '--metric-b' not in all_cmds)
check("R1 修复回归: analog 不再带不存在的 --metric",
      'analog --metric ' not in all_cmds)

print("═" * 60)
print("[6] 真实数据集成(build_vp;CI 无快照时按惯例跳过)")
print("═" * 60)
import workbench_data as wd      # noqa: E402
if os.environ.get('RD_R1_SKIP_INTEGRATION') == '1':
    snap = None
else:
    snap, _ = wd.latest_snapshot(ROOT)
if snap is None:
    skip("真实面(本机全量套件执行)", "干净 clone 无 data/daily 快照——"
         "CI 面只跑合成面案例(套件[1]-[5] 已全绿)")
else:
    VID = 'VIEW-20261110-002'
    view_doc, _ = __import__('view_store').get_view(VID)
    publish = view_doc['publish_date']
    tmp = tempfile.mkdtemp()
    vp_tmp = os.path.join(tmp, 'vp')
    shutil.copytree(os.path.join(ROOT, 'data', 'institutions',
                                 'verification'), vp_tmp)
    try:
        base = json.load(open(os.path.join(vp_tmp, f'VP-{VID}.json')))
        base_labels = [h['label'] for h in base['hypotheses']]
        base_view_label = base['view_label']
        with redirect_stdout(io.StringIO()):
            r1 = vpl.build_vp(VID, root=ROOT, vp_dir=vp_tmp)
            r2 = vpl.build_vp(VID, root=ROOT, vp_dir=vp_tmp)
        check("build_vp ok+落盘", r1.get('ok') and r2.get('ok'))
        doc = json.load(open(os.path.join(vp_tmp, f'VP-{VID}.json')))
        check("schema 1.1+lineage 留痕(原 basis 不丢)",
              doc['schema_version'] == '1.1'
              and doc.get('lineage', {}).get('prior_generation_basis'))
        check("C 契约零变动: view_label 不变",
              doc['view_label'] == base_view_label
              == 'INSUFFICIENT_EVIDENCE')
        check("C 契约零变动: 假设级 label 逐条不变",
              [h['label'] for h in doc['hypotheses']] == base_labels)
        check("三阶段面齐备: 每假设 stages.A/B+stage_labels",
              all(isinstance(h.get('stages', {}).get('A'), dict)
                  and isinstance(h.get('stages', {}).get('B'), dict)
                  and h.get('stage_labels', {}).get('A') in vpl.LABELS
                  and h.get('stage_labels', {}).get('B') in vpl.LABELS
                  for h in doc['hypotheses']))
        ok, errs = vpl.validate_vp(doc, view_doc)
        check("写后自校验+交叉校验通过", ok, str(errs))
        obs_bad = [row['metric_id'] for h in doc['hypotheses']
                   for row in h['stages']['A'].get('rows') or []
                   if str(row.get('observation_date') or '')[:10] > publish]
        check("无前视: 阶段A 全部 level 观测日≤publish",
              not obs_bad, str(obs_bad))
        check("锚点披露随行(approx 截断=DEGRADED 标注)",
              any(h['stages']['A'].get('anchor', {}).get('degraded')
                  for h in doc['hypotheses']))
        check("幂等: 两次 build stage_summary 一致",
              r1.get('stage_summary') == r2.get('stage_summary'))
        # R4(NIT-10 补强): 幂等以全档为准——两次 build 后逐字节比对
        doc2 = json.load(open(os.path.join(vp_tmp, f'VP-{VID}.json')))
        check("幂等: 两次 build 全档逐键一致(非仅 summary)",
              doc == doc2)
        rows_bad = [row['metric_id'] for h in doc['hypotheses']
                    for row in h['stages']['A'].get('rows') or []
                    if row.get('direction') and not
                    (row.get('direction_provenance') or {}).get(
                        'attribution')]
        check("判行方向全部带机构明示 provenance",
              not rows_bad, str(rows_bad))
        # --build-all 面(临时目录全量重建,不动真档)
        with redirect_stdout(io.StringIO()):
            outs = io.StringIO()
            import contextlib
            with contextlib.redirect_stdout(outs):
                rc = vpl.main(['--build-all', '--vp-dir', vp_tmp])
        lines = json.loads(outs.getvalue())
        n_vp = len([f for f in os.listdir(os.path.join(ROOT, 'data',
                     'institutions', 'verification'))
                    if f.startswith('VP-') and f.endswith('.json')])
        check(f"--build-all 全量重建({lines.get('n')} 份)全 ok",
              rc == 0 and lines.get('n_ok') == lines.get('n')
              and lines.get('n') == n_vp, str(lines.get('n_ok')))
        # R4(NIT-10 补强): 无前视集成断言扩到全量档——逐份逐假设核
        # 阶段A 观测日≤publish(原断言只测 1 份)
        import view_store as vs_mod
        look_bad = []
        for fn in sorted(os.listdir(vp_tmp)):
            if not (fn.startswith('VP-') and fn.endswith('.json')):
                continue
            d = json.load(open(os.path.join(vp_tmp, fn)))
            vd, _ = vs_mod.get_view(d['view_id'])
            pub = vd['publish_date']
            for h in d['hypotheses']:
                for row in h['stages']['A'].get('rows') or []:
                    if str(row.get('observation_date') or '')[:10] > pub:
                        look_bad.append(f"{d['view_id']}:{row.get('metric_id')}")
        check("无前视: 全量档阶段A 观测日≤publish(逐份核)",
              not look_bad, str(look_bad[:6]))
    finally:
        shutil.rmtree(tmp)

# ══════════ [7] R1.1 修复回归(E席审计 2026-11-11) ═══════════════════
print("═" * 60)
print("[7] R1.1 修复回归(E席审计: MAJOR-1 日期封顶/MAJOR-2 定基/词表护栏)")
print("═" * 60)
import research_history_query as rhq_mod
import view_verifier as vv_mod

_d = ['2026-01-05', '2026-06-02', '2026-10-01']
_v = [100.0, 102.0, 105.0]
_r = rhq_mod.interval_change(_d, _v, 'index_point', end='20260601')
check("MAJOR-1: 无横线端锚封顶生效(修复前越锚返回 2026-10-01)",
      _r.get('end_date') == '2026-01-05', str(_r.get('end_date') or _r.get('reason')))
_r2 = rhq_mod.interval_change(_d, _v, 'index_point', start='20260501', end='20261006')
check("MAJOR-1: 无横线 start 基准=严格早于窗起的最后观测",
      _r2.get('basis_date') == '2026-01-05' and _r2.get('end_date') == '2026-10-01'
      and abs((_r2.get('pct_change') or 0) - 5.0) < 1e-9,
      f"{_r2.get('basis_date')}→{_r2.get('end_date')} "
      f"pct={_r2.get('pct_change')}")
_r3 = rhq_mod.interval_change(['20251231', '20260602', '20261001'], _v,
                              'index_point', start='20260105', end='20261006')
check("MAJOR-1: 序列侧紧凑日期同归一(混合格式不再整年错序)",
      _r3.get('end_date') == '2026-10-01'
      and _r3.get('basis_date') == '2025-12-31',
      f"{_r3.get('basis_date')}→{_r3.get('end_date')}")

_tmap = vv_mod.load_forecast_target_map()
_tgt, _mid = next(iter(_tmap['targets'].items()))
_fdoc = {'forecasts': [
    {'value_or_direction': '维持不变', 'target': _tgt},
    {'value_or_direction': '继续加息', 'target': _tgt}]}
_dirs, _prov = vpl._hypothesis_directions({'evidence': {'linked_forecasts': [2]}},
                                          _fdoc, _tmap)
check("MAJOR-2: linked=[2] 按 1-based 取第 2 条(0-based 会取'维持不变'→None)",
      _dirs.get(_mid) == 'up'
      and (_prov.get(_mid) or {}).get('forecast_index_basis') == '1-based',
      f"dirs={_dirs} prov={_prov}")
check("MAJOR-2: 越界序号(0)如实不采用",
      vpl._hypothesis_directions({'evidence': {'linked_forecasts': [0]}},
                                 _fdoc, _tmap)[0] == {})

for txt, want in [('不再加息', None), ('no further cuts', None),
                  ('supply-driven', None), ('继续加息', 'up'),
                  ('Rate cut expected', 'down'), ('Higher for longer', 'up')]:
    got = vv_mod._parse_direction(txt)
    check(f"词表护栏: {txt!r} → {want}", got == want, f"got {got}")

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败 / {SKIP}按设计跳过")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
