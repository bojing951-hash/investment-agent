#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter9 P4 研究地图测试(research-map 确定性扇出+提名原料+编排层文件面)。

锁定面(P4 工单+协调增量【1】):
① 十问扇出: 每问=章程§五原文+五层归属+确定性数据面+既有能力命令清单;
   AI 层问题(RQ3/RQ9)只给 agent_judgment 面(引擎不产出判断,归编排层
   明示 attribution)
② 提名原料(04/05 节问题集=Agent 规则非引擎硬编码): conflicts=forecast
   经 target_map 映射+方向可解析后同指标多空机构对撞;pseudo_consensus=
   主题恰 1 家机构覆盖(与页③ subject_coverage 同源);不可映射/点位型
   不入对撞面(禁猜)
③ ART-M/ART-FALS/观察钟=编排层文件面: 缺席如实 present:false;在场透传
   (引擎绝不代触发)
④ ia_cli research-map 信封(--views-dir 注入缝;warnings 提示对撞/单源/
   ART 未文件化/观察钟未建)
⑤ 页1刷新按钮(显式点击才运行)/页4研究地图面板/页3单源伪共识标注
⑥ SKILL 编排层纪律在册(观察钟/ART-M/ART-FALS/04-05 提名/SCN 覆盖如实)
全合成沙箱(views/归档/编排层文件注入);questions 用 tracked config。
"""
import io
import json
import os
import subprocess
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
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


import workbench_data as wd   # noqa: E402
import research_map as rm     # noqa: E402
import fixt_c8_archive as fixt  # noqa: E402

TD = tempfile.mkdtemp(prefix='c9rmap_')
SANDBOX_ROOT = os.path.join(TD, 'engine')
os.makedirs(SANDBOX_ROOT)


def mk_view(vid, inst, subjects, forecasts, publish='2026-10-01'):
    return {
        'schema_version': '1.1', 'view_id': vid,
        'institution': {'name': inst, 'type': 'investment_bank',
                        'department': 'Research'},
        'authors': [], 'report_title': 'T ' + vid,
        'source_url': 'https://example.com/' + vid,
        'source_type': 'official_site', 'publish_date': publish,
        'fetch_date': '2026-11-10', 'access_level': 'public_full',
        'view_horizon': '6m', 'subjects': subjects,
        'core_views': [{'statement': '看法。', 'attribution':
                        'institution_stated', 'basis': 'paraphrase'}],
        'forecasts': forecasts, 'key_assumptions': [], 'evidence_cited': [],
        'mechanism_steps': [], 'risk_factors': [], 'falsification_conditions': [],
        'revisions': [], 'completeness_notes': '', 'copyright_note': 'meta+link',
    }


VIEWS_TD = os.path.join(TD, 'views')
os.makedirs(VIEWS_TD)
DOCS = [
    mk_view('VIEW-20261001-001', 'Alpha Bank', ['US_rates', 'fixed_income'],
            [{'target': '美债10年', 'value_or_direction': '上行',
              'horizon': '6m', 'attribution': 'institution_stated'}]),
    mk_view('VIEW-20261001-002', 'Beta Bank', ['US_rates'],
            [{'target': '美债10年', 'value_or_direction': '下行',
              'horizon': '6m', 'attribution': 'institution_stated'},
             {'target': '恒生国企指数', 'value_or_direction': '上行',
              'horizon': '6m', 'attribution': 'institution_stated'},
             {'target': '美债2年', 'value_or_direction': '到 3.8% 附近',
              'horizon': '2027-03', 'attribution': 'institution_stated'}]),
    # commodities 恰 1 家(单源伪共识);credit 零覆盖(非伪共识)
    mk_view('VIEW-20261001-003', 'Gamma House', ['commodities'], []),
]
for d in DOCS:
    with open(os.path.join(VIEWS_TD, d['view_id'] + '.json'), 'w',
              encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False)

print("═" * 60)
print("[1] 十问扇出结构")
print("═" * 60)
with tempfile.TemporaryDirectory() as arch_td:
    _arch = fixt.build_archive(arch_td)
    m = rm.build_map(root=SANDBOX_ROOT, views_dir=VIEWS_TD,
                     archive_dir=_arch)
check("十问齐备+id 连续", len(m['questions']) == 10
      and [q['id'] for q in m['questions']] == [f'RQ{i}' for i in range(1, 11)])
q1 = m['questions'][0]
check("RQ1 快照面在场(沙箱无快照→available False 如实)",
      q1['data_faces'][0]['kind'] == 'snapshot'
      and q1['data_faces'][0]['available'] is False, str(q1['data_faces']))
q3 = m['questions'][2]
check("RQ3(AI推断)只给 agent_judgment 面(引擎不产判断)",
      q3['data_faces'][0]['kind'] == 'agent_judgment'
      and 'ai_inferred' in q3['data_faces'][0]['note'])
q5 = m['questions'][4]
check("RQ5 views 面+research-map 命令", q5['data_faces'][0]['kind'] == 'views'
      and any('research-map' in c for c in q5['commands']))
q7 = m['questions'][6]
check("RQ7 归档面(fixture 2 档)", q7['data_faces'][0]['kind'] == 'archive'
      and q7['data_faces'][0]['n_records'] == 2, str(q7['data_faces']))
q8 = m['questions'][7]
check("RQ8 传导面(沙箱无边档→available False 如实)",
      q8['data_faces'][0]['kind'] == 'transmission'
      and q8['data_faces'][0]['available'] is False)
check("零模型声明在册", any('零模型' in n for n in m['notes']))

print("═" * 60)
print("[2] 提名原料(04/05 节=Agent 规则,引擎只产确定性原料)")
print("═" * 60)
ni = m['nomination_inputs']
cf = ni['conflicts']
check("对撞恰 1 组(美债10年): Alpha 上行 vs Beta 下行",
      len(cf) == 1 and cf[0]['metric_id'] == 'UST_10Y'
      and cf[0]['bull'] == ['Alpha Bank(VIEW-20261001-001)']
      and cf[0]['bear'] == ['Beta Bank(VIEW-20261001-002)'], str(cf))
check("不可映射 target(恒生国企指数)不入对撞(禁猜)",
      all(c['metric_id'] != 'HSCEI' for c in cf))
check("点位型(到 3.8% 附近)不入对撞(方向不可解析)",
      all('Beta' not in ' '.join(c['bull']) or c['metric_id'] != 'UST_2Y'
          for c in cf))
check("单源伪共识=fixed_income+commodities(credit 零覆盖不入)",
      ni['pseudo_consensus_subjects'] == ['fixed_income', 'commodities'],
      str(ni['pseudo_consensus_subjects']))
check("提名归 Agent 声明在册", '提名' in ni['note'] and '编排层' in ni['note'])

print("═" * 60)
print("[3] 编排层文件面(ART/观察钟透传,缺席如实)")
print("═" * 60)
check("沙箱无 ART-M/FALS→present False 如实",
      m['art']['m_table']['present'] is False
      and m['art']['falsification']['present'] is False)
check("沙箱无观察钟→present False+不代触发声明",
      m['observation_clock']['present'] is False
      and '不代触发' in m['observation_clock']['note'])
os.makedirs(os.path.join(SANDBOX_ROOT, 'data', 'research'), exist_ok=True)
with open(os.path.join(SANDBOX_ROOT, 'data', 'research',
                       'observation_clock.json'), 'w', encoding='utf-8') as f:
    json.dump({'entries': [{'id': 'CLK-1', 'metric_id': 'SOFR',
                            'trigger': 'SOFR>4.6%', 'deadline': '2026-12-05',
                            'status': 'watching'}]}, f, ensure_ascii=False)
with open(os.path.join(SANDBOX_ROOT, 'data', 'research', 'art_m.json'), 'w',
          encoding='utf-8') as f:
    json.dump({'entries': [{'id': 'M-1', 'claim': 'x', 'status': 'active'}]},
              f, ensure_ascii=False)
m2 = rm.build_map(root=SANDBOX_ROOT, views_dir=VIEWS_TD)
check("观察钟在场→透传条目(引擎仍不代触发)",
      m2['observation_clock']['present'] is True
      and m2['observation_clock']['entries'][0]['id'] == 'CLK-1'
      and '不代触发' in m2['observation_clock']['note'])
check("ART-M 在场→透传计数",
      m2['art']['m_table']['present'] is True
      and m2['art']['m_table']['ids'] == ['M-1'])

print("═" * 60)
print("[4] 页③ subject_coverage(单源伪共识矩阵面)")
print("═" * 60)
vm = wd.views_matrix(views_dir=VIEWS_TD)
cov = vm['subject_coverage']
check("commodities 单源=True( Gamma House)",
      cov['commodities']['pseudo_consensus_risk'] is True
      and cov['commodities']['n_institutions'] == 1, str(cov['commodities']))
check("US_rates 双源=False", cov['US_rates']['pseudo_consensus_risk'] is False
      and cov['US_rates']['n_institutions'] == 2)
check("credit 零覆盖=非伪共识(缺席≠单源)",
      cov['credit']['pseudo_consensus_risk'] is False
      and cov['credit']['n_institutions'] == 0)

print("═" * 60)
print("[5] ia_cli research-map 信封")
print("═" * 60)
proc = subprocess.run(
    [sys.executable, os.path.join(ROOT, 'ia_cli.py'), 'research-map',
     '--views-dir', VIEWS_TD],
    capture_output=True, text=True, timeout=300)
env = json.loads(proc.stdout)
check("rc=0+ok+capability", proc.returncode == 0 and env['ok']
      and env['capability'] == 'research-map')
d = env['data']
check("信封内十问+对撞+单源同面",
      len(d['questions']) == 10
      and d['nomination_inputs']['conflicts'][0]['metric_id'] == 'UST_10Y'
      and d['nomination_inputs']['pseudo_consensus_subjects']
      == ['fixed_income', 'commodities'])
warns = ' '.join(env.get('warnings') or [])
check("warnings 提示对撞+单源+ART/观察钟",
      '对撞' in warns and '单源' in warns and 'ART-M' in warns
      and '观察钟' in warns, warns[:200])

print("═" * 60)
print("[6] 页面入口(app.py 源结构)+SKILL 编排纪律")
print("═" * 60)
src = open(os.path.join(ROOT, 'app.py'), encoding='utf-8').read()
pp = src[src.index('def page_panorama'):src.index('def page_transmission')]
check("页1 刷新按钮(显式点击才运行 run_weekly)",
      'run_weekly.py' in pp and 'st.button' in pp and 'subprocess' in pp
      and '点击才运行' in pp)
pv3 = src[src.index('def page_views'):src.index('def page_research')]
check("页3 单源伪共识标注(subject_coverage 消费)",
      'subject_coverage' in pv3 and '伪共识' in pv3)
pv4 = src[src.index('def page_research'):src.index('def page_about')]
check("页4 研究地图面板(research_map 同引擎)",
      'research_map' in pv4 and '研究地图' in pv4 and 'nomination_inputs' in pv4)
skill = open(os.path.join(ROOT, '.agents', 'skills', 'global-macro-research',
                          'SKILL.md'), encoding='utf-8').read()
check("SKILL 十一个能力速查(research-map 在册)",
      '十一个能力速查' in skill and 'research-map' in skill)
check("SKILL 观察钟纪律(编排层+引擎不代触发)",
      '观察钟' in skill and '绝不代触发' in skill)
check("SKILL ART-M/ART-FALS 文件化纪律", 'ART-M' in skill
      and 'ART-FALS' in skill)
check("SKILL 04/05 提名规则(Agent 非引擎硬编码)",
      '自动提名' in skill and '非引擎硬编码' in skill)
check("SKILL SCN 覆盖如实披露(有/无情景列明)",
      '情景覆盖' in skill and '哪些 M 有情景' in skill)
cli_doc = open(os.path.join(ROOT, '.agents', 'skills', 'global-macro-research',
                            'references', 'cli-contract.md'), encoding='utf-8').read()
check("cli-contract research-map 负载契约在册", 'research-map' in cli_doc
      and 'nomination_inputs' in cli_doc)
# 装机副本(.claude/skills)不入库(.gitignore)——干净 clone 无此面:
# 本地在场时锁定同步(install_skill --force 后一致);缺席显式 SKIP。
INSTALLED = os.path.join(ROOT, '.claude', 'skills', 'global-macro-research',
                         'SKILL.md')
if os.path.isfile(INSTALLED):
    check("装机副本同步(install_skill --force 后一致)",
          open(INSTALLED, encoding='utf-8').read() == skill)
else:
    print("  ⏭️ SKIP[CI]: 装机副本缺席(.claude/ 不入库;本地 install_skill "
          "--target project --force 后在场)")

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
