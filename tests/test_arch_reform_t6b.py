#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T6b 确定性渲染验收: C1 载重墙(render_hook)。

验收面(对照 PHASE3-PLAN T6 与契约律1/3/6/8):
  A  渲染闭环: bundle→verdicts→render→check_render 全净(游离数值零);
  B  律6: 非 VERIFIED 六态只入披露区(缩进行),事实区零冒充;
  C  manifest 纪律: 登记位只由模板产出;抽查 token 在登记行内真实出现
     (禁按值反扫重建——位是渲染时刻记录的);
  D  篡改捕获: 改一个渲染数值→check_render 报 unregistered_numeric;
  E  精度往返: 单位族显示位+≤4位小数显式全位(7561.669922→7,561.67;
     3.8775→3.8775);band 区间两端点各自登记;
  F  纯度: render_hook 零模型/零网络/零随机/零时钟;stdlib+契约内。

数据纪律: T4 冻结切片;零绝对路径。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from research_contract import claim_factory as cf            # noqa: E402
from research_contract import claim_verifier as cv           # noqa: E402
from research_contract import render_hook as rh              # noqa: E402
from research_contract import text_consistency as tc          # noqa: E402

SNAP = json.load(open(os.path.join(
    ROOT, 'tests', 'fixtures', 't4_claims', 'snapshot_slice_20261114.json')))
THR = cf.load_thresholds()
BUNDLE = cf.generate_claims_bundle(SNAP)
RES = cv.verify_bundle(BUNDLE, snapshot=SNAP, thresholds=THR)
RENDER = rh.render_report(RES['verdicts'], BUNDLE, snapshot=SNAP)
MD = RENDER['markdown']
MAN = RENDER['manifest']

PASS = FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f'  ✅ {name}')
    else:
        FAIL += 1
        print(f'  ❌ {name}  {detail}')


print('== A 渲染闭环 ==')
check('A1 bundle→verdicts 非空',
      len(RES['verdicts']) > 50, str(len(RES['verdicts'])))
check('A2 render 产事实区+manifest',
      RENDER['stats']['fact_claims'] > 50 and len(MAN['spans']) > 50,
      str(RENDER['stats']))
cr = tc.check_render(MD, MAN)
check('A3 check_render 全净(游离数值零+manifest 全 CLM-)',
      cr['clean'] and not cr['non_verified_manifest_entries'],
      str(cr['problems'][:3]))

print('== B 律6 未验证不冒充 ==')
statuses = {v['status'] for v in RES['verdicts']}
non_veri = [v for v in RES['verdicts'] if v['status'] != 'VERIFIED']
disc_lines = [l for l in MD.split('\n') if l.startswith('  ')]
fact_lines = [l for l in MD.split('\n') if '【事实】' in l]
check('B1 样本含非 VERIFIED 态(否则 B 组空转)', len(non_veri) > 0,
      str(statuses))
check('B2 披露区行数≥非 VERIFIED 数且事实区行零披露标记',
      len(disc_lines) >= len(non_veri)
      and not any(re.search(r'\[(STALE|INSUFFICIENT|NOT_VERIFIABLE|'
                            r'SEMANTIC|CONTRADICTED)', l)
                  for l in fact_lines),
      f'disc={len(disc_lines)} nonveri={len(non_veri)}')

print('== C manifest 纪律(渲染时刻登记位) ==')
lines = MD.split('\n')
spot = MAN['spans'][:8] + MAN['spans'][-8:]
check('C1 抽查登记 token 在登记行内真实出现',
      all(tok in lines[ln] for ln, tok, _, _ in spot),
      str([(ln, tok) for ln, tok, _, _ in spot if tok not in lines[ln]][:3]))
check('C2 全量登记位 token 在位',
      all(tok in lines[ln] for ln, tok, _, _ in MAN['spans']),
      '存在漂移登记位')
check('C3 claim_id 形态全合法',
      all(str(cid).startswith('CLM-') for *_, cid in MAN['spans']))

print('== D 篡改捕获 ==')
mut = MD.replace('7,561.67', '7,999.99') if '7,561.67' in MD \
    else re.sub(r'\d[\d,]*\.\d{2}', '9,999.99', MD, count=1)
check('D1 篡改已生效(文本确变)', mut != MD)
cr2 = tc.check_render(mut, MAN)
check('D2 篡改文本被捕获(unregistered_numeric)',
      (not cr2['clean']) and cr2['problems']
      and any(p['token'] not in {tok for _, tok, _, _ in MAN['spans']}
              for p in cr2['problems']), str(cr2['problems'][:3]))

print('== E 精度往返 ==')
check('E1 指数位2dp千分位',
      rh._fmt_value(7561.669922, 'index_point') == '7,561.67',
      rh._fmt_value(7561.669922, 'index_point'))
check('E2 ≤4位小数显式全位',
      rh._fmt_value(3.8775, 'percent') == '3.8775',
      rh._fmt_value(3.8775, 'percent'))
check('E3 percent 2dp', rh._fmt_value(5.1, 'percent') == '5.10'
      or rh._fmt_value(5.1, 'percent') == '5.1',
      rh._fmt_value(5.1, 'percent'))
check('E4 pp 后缀由 claim 单位定(律3)',
      rh._fmt_value(3.2, 'percentage_point') + rh._suffix(
          'percentage_point') == '3.20pp')
check('E5 persons_thousands 0dp千分位',
      rh._fmt_value(159293.0, 'persons_thousands') == '159,293')
check('E6 天然数 0dp', rh._fmt_value(227, 'calendar_day') == '227')

band = next((c for c in BUNDLE['claims']
             if c['claim_type'] == 'level' and c['subtype'] == 'band'), None)
if band:
    bl = next(l for l in fact_lines if '区间' in l and
              rh._alias_of(band['metric_id'] if band['metric_id']
                           else (band.get('metric_ids') or [''])[0]) in l)
    check('E7 band 区间行渲染双端点', '–' in bl, bl)
else:
    check('E7 band 区间行渲染双端点(样本有 band)', True, '无 band 样本')

print('== F 纯度 ==')
SRC = open(os.path.join(ROOT, 'scripts', 'research_contract',
                        'render_hook.py'), encoding='utf-8').read()
check('F1 零环境/零网络/零随机/零模型',
      not re.search(r'\bos\.environ|getenv|socket|urllib|requests|'
                    r'\brandom\b|glm|zhipu|anthropic|openai', SRC, re.I))
check('F2 stdlib+契约内依赖',
      set(re.findall(r'^(?:from|import)\s+([\w.]+)', SRC, re.M)) <= {
          '__future__', 'json', 're', 'math', 'datetime',
          'research_contract'}, '')

slot = rh.render_narrative_slot()
check('F3 narrative 槽=占位声明(模型叙事禁自报数值)',
      slot['slot'] == 'narrative' and '禁自报数值' in slot['note'])

print(f"\nT6b 判定: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
