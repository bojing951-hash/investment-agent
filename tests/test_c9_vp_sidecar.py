#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter9 P0-2 VP sidecar 测试(假设级验证链+六标签+装载校验+页③渲染)。

锁定面(裁定④+P0-2 工单):
① 六标签最保守聚合优先级表(本套件=锁定版):
   全CONTRADICTED→CONTRADICTED;任一CONTRADICTED→MIXED;
   全NOT_YET_TESTABLE→NOT_YET_TESTABLE;全SUPPORTED→SUPPORTED;
   任一SUPPORTED→PARTIALLY_SUPPORTED;其余→INSUFFICIENT_EVIDENCE;空=INSUFFICIENT
② mode C verdict→标签机械映射(supports/against/NOT_YET_TESTABLE 通道保真,
   机器不可判四态+neutral→INSUFFICIENT_EVIDENCE 不升不降)
③ sidecar 独立性: 不动 views v1.1(TOP_REQUIRED 无验证字段);目录缺席=未验证
   如实(干净 clone 面)
④ 交叉校验: ref 索引界内/digest 前缀/metric_refs 形/label 枚举/
   view_label 必须与引擎聚合一致(写入方不得自带聚合)
⑤ 页③渲染修复: mechanism_steps/evidence_cited 进单份详情(此前遗漏)+
   VP 徽标面(app.py 源结构断言,与 SKILL.md 断言同款模式)
全合成 tmp 目录,零真实 data/ 依赖。
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


import view_store as vs         # noqa: E402
import view_plausibility as vpl  # noqa: E402

print("═" * 60)
print("[1] 六标签聚合优先级表(裁定④,本套件锁定)")
print("═" * 60)
R = vpl.rollup_view_label
check("全CONTRADICTED→CONTRADICTED",
      R(['CONTRADICTED', 'CONTRADICTED']) == 'CONTRADICTED')
check("任一CONTRADICTED→MIXED(其余SUPPORTED)",
      R(['SUPPORTED', 'CONTRADICTED']) == 'MIXED')
check("任一CONTRADICTED→MIXED(其余NOT_YET_TESTABLE)",
      R(['NOT_YET_TESTABLE', 'CONTRADICTED']) == 'MIXED')
check("全NOT_YET_TESTABLE→NOT_YET_TESTABLE",
      R(['NOT_YET_TESTABLE', 'NOT_YET_TESTABLE']) == 'NOT_YET_TESTABLE')
check("全SUPPORTED→SUPPORTED",
      R(['SUPPORTED', 'SUPPORTED']) == 'SUPPORTED')
check("任一SUPPORTED(其余NOT_YET_TESTABLE)→PARTIALLY_SUPPORTED",
      R(['SUPPORTED', 'NOT_YET_TESTABLE']) == 'PARTIALLY_SUPPORTED')
check("任一SUPPORTED(其余INSUFFICIENT)→PARTIALLY_SUPPORTED",
      R(['INSUFFICIENT_EVIDENCE', 'SUPPORTED']) == 'PARTIALLY_SUPPORTED')
check("NOT_YET+INSUFFICIENT 混合(无S/无C)→INSUFFICIENT_EVIDENCE",
      R(['NOT_YET_TESTABLE', 'INSUFFICIENT_EVIDENCE']) == 'INSUFFICIENT_EVIDENCE')
check("空序列→INSUFFICIENT_EVIDENCE(未验证面)", R([]) == 'INSUFFICIENT_EVIDENCE')
check("未知标签不参与聚合(容错不猜)",
      R(['SUPPORTED', 'bogus']) == 'SUPPORTED')

print("═" * 60)
print("[2] mode C verdict → 标签机械映射")
print("═" * 60)
M = vpl.verdict_to_label
check("supports→SUPPORTED", M('supports') == 'SUPPORTED')
check("against→CONTRADICTED", M('against') == 'CONTRADICTED')
check("NOT_YET_TESTABLE→NOT_YET_TESTABLE", M('NOT_YET_TESTABLE')
      == 'NOT_YET_TESTABLE')
for v in ('UNPARSEABLE_HORIZON', 'NOT_MACHINE_VERIFIABLE',
          'INSUFFICIENT_DATA', 'LEVEL_TARGET', 'neutral'):
    check(f"{v}→INSUFFICIENT_EVIDENCE(机器不可判不升不降)",
          M(v) == 'INSUFFICIENT_EVIDENCE')
check("未知 verdict→INSUFFICIENT_EVIDENCE(禁猜)", M('whatever')
      == 'INSUFFICIENT_EVIDENCE')

print("═" * 60)
print("[3] sidecar 装载(目录缺席/缺文件/损坏/正常)+独立性")
print("═" * 60)
check("views v1.1 未增验证字段(sidecar 独立,不动 schema)",
      'hypotheses' not in vs.TOP_REQUIRED
      and 'view_label' not in vs.TOP_REQUIRED
      and not any('verif' in k for k in vs.TOP_REQUIRED))
TD = tempfile.mkdtemp(prefix='c9vp_')
VPDIR = os.path.join(TD, 'verification')
d_none, r_none = vpl.load_vp('VIEW-20261110-001', vp_dir=VPDIR)
check("目录缺席→(None,未验证如实;干净clone面)", d_none is None
      and '不存在' in r_none, r_none)
os.makedirs(VPDIR)
d_miss, r_miss = vpl.load_vp('VIEW-20261110-001', vp_dir=VPDIR)
check("缺文件→(None,未经验证链)", d_miss is None and '无 VP sidecar' in r_miss)
with open(os.path.join(VPDIR, 'VP-VIEW-20261110-099.json'), 'w',
          encoding='utf-8') as f:
    f.write('{not json')
docs, bad = vpl.load_all(vp_dir=VPDIR)
check("损坏 JSON→隔离不入面(load_all rejected)", docs == []
      and len(bad) == 1 and '不可读' in bad[0][1], str(bad))

print("═" * 60)
print("[4] 交叉校验(ref界内/digest/枚举/聚合一致)")
print("═" * 60)
GOOD_VIEW = {
    'schema_version': '1.1', 'view_id': 'VIEW-20261110-001',
    'institution': {'name': 'Synthetic Bank', 'type': 'investment_bank',
                    'department': 'Research'},
    'authors': [], 'report_title': 'Syn', 'source_url': 'https://example.com/x',
    'source_type': 'official_site', 'publish_date': '2026-11-01',
    'fetch_date': '2026-11-10', 'access_level': 'public_full',
    'view_horizon': '6m', 'subjects': ['US_rates'],
    'core_views': [{'statement': '美联储年内不再加息。', 'attribution':
                    'institution_stated', 'basis': 'verbatim_quote',
                    'quote': 'no more hikes this year'}],
    'forecasts': [], 'key_assumptions': [
        {'statement': '核心通胀维持回落。', 'attribution': 'institution_stated',
         'basis': 'paraphrase'}],
    'evidence_cited': [], 'mechanism_steps': [], 'risk_factors': [],
    'falsification_conditions': [], 'revisions': [],
    'completeness_notes': '', 'copyright_note': 'meta+link',
}


def mk_vp(hyps, view_label=None, view_id='VIEW-20261110-001'):
    return {'schema_version': '1.0', 'view_id': view_id,
            'generated_by': 'agent_orchestration', 'as_of': '20261110',
            'hypotheses': hyps,
            'view_label': view_label if view_label is not None
            else vpl.rollup_view_label([h['label'] for h in hyps])}


HYP_OK = [
    {'ref': {'kind': 'core_view', 'index': 0,
             'statement_digest': '美联储年内不再加息'},
     'metric_refs': [{'metric_id': 'DFEDTARU', 'direction': 'flat',
                      'segment': 'publish→horizon_end'}],
     'label': 'NOT_YET_TESTABLE',
     'evidence': {'mode': 'C', 'forecast_index': 1,
                  'verdict': 'NOT_YET_TESTABLE'}},
    {'ref': {'kind': 'key_assumption', 'index': 0},
     'metric_refs': [{'metric_id': 'CORE_PCE', 'direction': 'down',
                      'segment': 'publish→2026-12-31'}],
     'label': 'INSUFFICIENT_EVIDENCE',
     'evidence': {'mode': 'C', 'forecast_index': None,
                  'verdict': 'NOT_MACHINE_VERIFIABLE'}},
]
ok, errs = vpl.validate_vp(mk_vp(HYP_OK), GOOD_VIEW)
check("合法 sidecar 校验通过", ok, str(errs))
bad_lbl = mk_vp([dict(HYP_OK[0], label='bogus')])
ok2, errs2 = vpl.validate_vp(bad_lbl, GOOD_VIEW)
check("label 越枚举→拒", not ok2 and any('六标签' in e for e in errs2))
ok3, errs3 = vpl.validate_vp(mk_vp([dict(HYP_OK[0],
                                          ref={'kind': 'core_view',
                                               'index': 5})]), GOOD_VIEW)
check("ref.index 越界→拒", not ok3 and any('越界' in e for e in errs3))
ok4, errs4 = vpl.validate_vp(mk_vp([dict(HYP_OK[0],
                                          ref={'kind': 'vibe',
                                               'index': 0})]), GOOD_VIEW)
check("ref.kind 未知→拒", not ok4 and any('ref.kind' in e for e in errs4))
ok5, errs5 = vpl.validate_vp(
    mk_vp([dict(HYP_OK[0], ref={'kind': 'core_view', 'index': 0,
                                'statement_digest': '完全不相干的陈述'})]),
    GOOD_VIEW)
check("statement_digest 前缀不符→拒(防错挂)", not ok5
      and any('digest' in e for e in errs5))
ok6, errs6 = vpl.validate_vp(mk_vp([dict(HYP_OK[0],
                                          metric_refs=[{'metric_id': 'X',
                                                        'direction': 'sideways'}])]),
                             GOOD_VIEW)
check("metric_refs.direction 非法→拒", not ok6
      and any('direction' in e for e in errs6))
ok7, errs7 = vpl.validate_vp(mk_vp(HYP_OK, view_label='SUPPORTED'), GOOD_VIEW)
check("自带聚合与引擎不符→拒(写入方须用 rollup)", not ok7
      and any('最保守聚合' in e for e in errs7))
ok8, errs8 = vpl.validate_vp(mk_vp(HYP_OK, view_id='VIEW-20261110-777'),
                             GOOD_VIEW)
check("view_id 与 views 档不符→拒", not ok8
      and any('不符' in e for e in errs8))

print("═" * 60)
print("[5] 徽标行+CLI")
print("═" * 60)
rows = vpl.vp_badge_rows(mk_vp(HYP_OK))
check("徽标行: 观点1/假设1 命名+指标链+判定依据",
      rows[0]['ref'] == '观点1' and rows[1]['ref'] == '假设1'
      and 'DFEDTARU' in rows[0]['指标链'] and 'mode C' in rows[0]['判定依据'],
      str(rows))
with open(os.path.join(VPDIR, 'VP-VIEW-20261110-001.json'), 'w',
          encoding='utf-8') as f:
    json.dump(mk_vp(HYP_OK), f, ensure_ascii=False)
# CLI 交叉校验走 vs.get_view→VIEWS_DIR: 注入合成 views 沙箱(与
# test_c9_verifier_modes 同款),避免真实档 digest/索引面干扰
VIEWS_TD = os.path.join(TD, 'views')
os.makedirs(VIEWS_TD)
with open(os.path.join(VIEWS_TD, 'VIEW-20261110-001.json'), 'w',
          encoding='utf-8') as f:
    json.dump(GOOD_VIEW, f, ensure_ascii=False)
_real_vdir = vs.VIEWS_DIR
vs.VIEWS_DIR = VIEWS_TD
with redirect_stdout(io.StringIO()) as buf:
    rc = vpl.main(['VIEW-20261110-001', '--vp-dir', VPDIR])
out = json.loads(buf.getvalue())
vs.VIEWS_DIR = _real_vdir
check("CLI 装载 ok+NOT_YET+INSUFFICIENT混合→INSUFFICIENT_EVIDENCE(全NOT_YET才NOT_YET)",
      rc == 0 and out['ok'] and out['view_label'] == 'INSUFFICIENT_EVIDENCE',
      str(out.get('view_label')))
with redirect_stdout(io.StringIO()) as buf:
    rc = vpl.main(['--list', '--vp-dir', VPDIR])
outl = json.loads(buf.getvalue())
check("CLI --list 1 份+rejected 1(损坏档隔离披露)",
      rc == 0 and outl['n'] == 1 and len(outl['rejected']) == 1)
with redirect_stdout(io.StringIO()) as buf:
    rc = vpl.main(['bogus'])
check("CLI 用法错→rc=2", rc == 2)
with redirect_stdout(io.StringIO()) as buf:
    rc = vpl.main(['VIEW-20261110-888', '--vp-dir', VPDIR])
check("CLI 缺 sidecar→rc=1", rc == 1)

print("═" * 60)
print("[6] 页③渲染修复(app.py 源结构: mechanism/evidence/VP 面)")
print("═" * 60)
src = open(os.path.join(ROOT, 'app.py'), encoding='utf-8').read()
pv = src[src.index('def page_views'):src.index('def page_research')]
check("mechanism_steps 进单份详情(此前遗漏)", 'mechanism_steps' in pv
      and '传导机制' in pv)
check("evidence_cited 进单份详情(此前遗漏)", 'evidence_cited' in pv
      and '引用证据' in pv)
check("VP 徽标面(验证标签+sidecar 路径披露)",
      'view_plausibility' in pv and '验证标签' in pv
      and 'VP sidecar' in pv)
check("校验失败不入面(warning 面)", '校验失败' in pv)

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
