#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter9 P3 页面结构测试(页②单边详情+验证徽标;页④研究十问)。

锁定面(裁定⑤+P3 工单):
① config/research_questions.json=章程§五原文十条(文本逐字锁定——裁定⑤
   给定文本,工程不得改写),五层齐备各至少一问,draws 不越枚举
② wd.research_questions FAIL-LOUD(恰10问/RQ1..RQ10连续/层枚举/覆盖;
   破损 config→ValueError 非静默降级)
③ wd.edge_verification_badge: source_verifier 四状态接线(fixture 归档
   VERIFIED/目录缺席 PARTIAL 如实/不在册 MISSING)
④ app.py 页②单边详情面板(行选择+qb_source 徽标)与页④十问面板在册
   (源结构断言,与 SKILL.md 断言同款模式——streamlit 页不进 CI 运行面)
零真实 data/ 依赖(fixture 归档注入;research_questions 为 tracked config)。
"""
import json
import os
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
import fixt_c8_archive as fixt  # noqa: E402

print("═" * 60)
print("[1] 研究十问: 章程§五原文十条(裁定⑤文本逐字锁定)")
print("═" * 60)
rq = wd.research_questions()
check("恰 10 问", rq['n'] == 10 and len(rq['questions']) == 10)
check("id RQ1..RQ10 连续", [q['id'] for q in rq['questions']]
      == [f'RQ{i}' for i in range(1, 11)])
TEXTS = ['当前全球经济处于什么环境?', '当前最重要的宏观变化是什么?',
         '当前的主要矛盾是什么?', '主要机构如何理解当前环境?',
         '机构之间存在哪些分歧?', '客观证据支持什么判断?',
         '历史上有哪些相似时期?', '传导机制如何运作?',
         '条件情景如何推演?', '哪些数据会推翻当前判断?']
check("十问文本=章程§五原文(裁定⑤逐字,工程不得改写)",
      [q['text'] for q in rq['questions']] == TEXTS,
      str([q['text'] for q in rq['questions']]))
check("五层枚举齐备(客观事实/机构观点/AI推断/历史统计/条件情景)",
      rq['layers'] == ['客观事实', '机构观点', 'AI推断', '历史统计', '条件情景'])
check("五层各至少一问(by_layer 全非空)",
      all(rq['by_layer'][l] for l in rq['layers']), str(rq['by_layer']))
check("层注记在册(归因纪律: ai_inferred 不冒充机构观点)",
      'ai_inferred' in rq['layer_note'])
check("AI推断层问题(RQ3)兼取客观事实+机构观点",
      rq['questions'][2]['primary_layer'] == 'AI推断'
      and set(rq['questions'][2]['draws']) == {'客观事实', '机构观点'})

print("═" * 60)
print("[2] research_questions FAIL-LOUD")
print("═" * 60)
with tempfile.TemporaryDirectory() as td:
    bad_path = os.path.join(td, 'bad.json')
    for name, mutate in (
            ('9 问', lambda c: c.update(questions=c['questions'][:9])),
            ('id 断号', lambda c: c['questions'][3].update(id='RQ99')),
            ('primary_layer 越枚举',
             lambda c: c['questions'][0].update(primary_layer='玄学')),
            ('层覆盖缺失(全挤一层)',
             lambda c: [q.update(primary_layer='客观事实')
                        for q in c['questions']])):
        cfg = json.load(open(os.path.join(ROOT, 'config',
                                          'research_questions.json'),
                             encoding='utf-8'))
        mutate(cfg)
        json.dump(cfg, open(bad_path, 'w', encoding='utf-8'), ensure_ascii=False)
        try:
            wd.research_questions(path=bad_path)
            check(f"破损 config({name})→ValueError", False)
        except ValueError as e:
            check(f"破损 config({name})→ValueError", True)

print("═" * 60)
print("[3] 边验证徽标(source_verifier 四状态接线)")
print("═" * 60)
with tempfile.TemporaryDirectory() as td:
    arch = fixt.build_archive(td)
    b = wd.edge_verification_badge(fixt.Q22, archive_dir=arch)
    check("在册+sidecar→VERIFIED/源已核验", b['state'] == 'VERIFIED'
          and '源已核验' in b['badge'], str(b))
    b2 = wd.edge_verification_badge(fixt.Q23, archive_dir=arch)
    check("在册无正文→PARTIAL/部分核验", b2['state'] == 'PARTIAL', str(b2))
    b3 = wd.edge_verification_badge('QB-20990101-999', archive_dir=arch)
    check("不在册→MISSING/悬空引用", b3['state'] == 'MISSING'
          and '悬空' in b3['badge'], str(b3))
    empty = os.path.join(td, 'no_archive')
    b4 = wd.edge_verification_badge(fixt.Q22, archive_dir=empty)
    check("归档目录缺席(干净clone)→PARTIAL 如实非通过",
          b4['state'] == 'PARTIAL' and '干净clone' in b4['detail'], str(b4))

print("═" * 60)
print("[4] app.py 页面结构(页②详情面板/页④十问面板)")
print("═" * 60)
src = open(os.path.join(ROOT, 'app.py'), encoding='utf-8').read()
pt = src[src.index('def page_transmission'):src.index('def page_views')]
check("页②单边详情(行选择 selectbox+实线/虚线前缀)",
      '单边详情' in pt and 'selectbox' in pt and '实线' in pt)
check("页②验证徽标接线(edge_verification_badge+source_verifier 指引)",
      'edge_verification_badge' in pt and 'source_verifier.py' in pt)
pr = src[src.index('def page_research'):src.index('def page_about')]
check("页④十问面板(research_questions 驱动+五层图标)",
      'research_questions' in pr and '研究十问' in pr
      and '条件情景' in pr)
check("页④十问失败面如实(warning 非静默)", '研究十问配置不可用' in pr)
check("Agent 引导含 --mode A|B|C 三型说明", '--mode A|B|C' in pr)

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
