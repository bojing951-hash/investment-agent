#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R35 利差辖域披露升位(RDG-20261115-008)+自对算术守卫(RDG-20261115-009)

判死红线:
  1. 真实静默吞句(研究运行报告 20261113T005117Z / 周报 20261009 真句)
     修后必须落 spread_ambiguous 披露(INSUFFICIENT_EVIDENCE),禁零检查零未映射。
  2. 真实可算对(DFF−JP_POLICY_RATE 亲算句)必须仍 VERIFIED 且零误披露。
  3. 自对句(高收益债利差 HY_OAS 同指标双别名)必须零 CONTRADICTED
     (main 基线=假红 |v−v|=0,RDG-009)。
  4. 变异自证: 披露分支摘除→红1复现;相异守卫摘除→红3复现。
语料出处(真句嵌入,R27 惯例):
  - output/research_runs/20261113T005117Z_美联储政策利率_DFF_与日本政策利率_
    JP_POLICY_RATE_之差_US/report.md L59(情景句)/L41(CON-2 亲算句)
  - tests/fixtures/e2e/reports/weekly_report_20261009.md L15(周报真句)
  - tests/test_arch_reform_phase4.py L99(R24/R32 判定句形态)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from research_contract import claim_factory as cf            # noqa: E402
from research_contract import text_consistency as tc         # noqa: E402

FIX = os.path.join(ROOT, 'tests', 'fixtures', 't6')
SNAP = json.load(open(os.path.join(FIX, 'snapshot_20261114_v2.json')))
THR = cf.load_thresholds()

PASS = FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f'  ✅ {name}')
    else:
        FAIL += 1
        print(f'  ❌ {name}  {detail}')


def ct(text):
    return tc.check_text(text, snapshot=SNAP, thresholds=THR)


def fams(r, family='spread_ambiguous'):
    return [c for c in r['checks'] if c['family'] == family]


print('== A 披露升位(RDG-20261115-008) ==')

# A1 真实缺陷句(research run L59 情景句派生;修前=零检查零未映射静默吞)
SENT_ADP = '美日政策利差至 2027H1 维持 ≥2.5pp(情景假设,非预测)。'
r = ct(SENT_ADP)
d = fams(r)
check('A1 真句静默吞→披露在场(token=2.5pp)',
      len(d) == 1 and d[0]['token'] == '2.5pp'
      and d[0]['status'] == 'INSUFFICIENT_EVIDENCE',
      str(d))
check('A1b 披露≠未映射(unbound 仍 0,披露进 checks 面)',
      r['stats']['unbound'] == 0 and r['unbound'] == [],
      str(r['stats']))

# A2 周报真句(weekly_report_20261009 L15;修前=3.35%/3.15% 双 token 全静默吞)
SENT_WK = 'HY OAS 3.35%,前值3.15%,利差快速走阔。'
r = ct(SENT_WK)
d = fams(r)
check('A2 周报真句双 token 披露(3.35%/3.15%)',
      sorted(x['token'] for x in d) == ['3.15%', '3.35%']
      and all(x['status'] == 'INSUFFICIENT_EVIDENCE' for x in d),
      str(d))
check('A2b 周报真句零 CONTRADICTED(披露不判错)',
      r['stats']['contradicted'] == 0, str(r['stats']))

# A3 判决中性: 同文 VERIFIED 面+歧义面→verdict 不被披露拉低
r = ct('SPX 本周+2.51%，收于7,561.67。' + SENT_ADP)
check('A3 披露中性不改判(VERIFIED 保持)',
      r['verdict'] == 'VERIFIED' and len(fams(r)) == 1
      and r['stats']['contradicted'] == 0,
      f'{r["verdict"]} {r["stats"]}')

# A4 非利差辖域词不触发(范围收紧: 仅利差族,其他 owned_ctx 词维持既有语义)
r = ct('美元指数站上104关口。')
check('A4 非利差辖域词零 spread_ambiguous',
      fams(r) == [] and r['stats']['unbound'] == 0, str(r['checks']))

# A5 无数值利差段零披露(利差快速走阔: 无 token 可披露)
r = ct('HY OAS 走阔,利差快速走阔。')
check('A5 无数值利差段零披露', fams(r) == [], str(r['checks']))

print('== B 可算对不误伤(零容差放宽红线) ==')

# B1 真双指标对取对(别名+自指+第三指标: 旧码取前两别名可同指标/取错对)
r = ct('高收益债利差 HY OAS 与投资级OAS 利差 2.85pp。')
sp = fams(r, 'spread_arithmetic')
check('B1 真双指标对取前两相异指标(|3.2−0.89|=2.31 咬 2.85 假值)',
      len(sp) == 1 and sp[0]['status'] == 'CONTRADICTED'
      and '3.2−0.89' in sp[0].get('note', ''),
      str(sp))

# B2 同句真值 VERIFIED(2.31=|3.2−0.89|)
r = ct('高收益债利差 HY OAS 与投资级OAS 利差 2.31pp。')
sp = fams(r, 'spread_arithmetic')
check('B2 真值 2.31pp→VERIFIED',
      len(sp) == 1 and sp[0]['status'] == 'VERIFIED', str(sp))
check('B2b 价差已裁→零冗余披露(spread_fired 抑制)',
      fams(r) == [], str(r['checks']))

# B3 真实亲算句(research run L41 形态)仍 VERIFIED 零冗余披露
SENT_CALC = ('美日政策利差约 +2.84pp'
             '(DFF 3.88% − JP_POLICY_RATE 1.043%, 两绑定事实亲算)。')
r = ct(SENT_CALC)
sp = fams(r, 'spread_arithmetic')
check('B3 真实亲算句 spread_arithmetic VERIFIED',
      len(sp) == 1 and sp[0]['status'] == 'VERIFIED'
      and '|3.88−1.043|=2.837' in sp[0].get('note', ''), str(sp))
check('B3b 已裁句零冗余披露', fams(r) == [], str(r['checks']))

print('== C 自对假阳性歼灭(RDG-20261115-009) ==')

# C1 R24/R32 判定句形态(别名+metric_id 自指同指标;main 基线=假红 |3.2−3.2|=0)
SENT_SELF = '高收益债利差 HY_OAS 3.34pp,处当年第 95.6 百分位。'
r = ct(SENT_SELF)
check('C1 自对句零 CONTRADICTED(main 基线假红歼灭)',
      r['stats']['contradicted'] == 0
      and fams(r, 'spread_arithmetic') == [], str(r['checks']))
check('C1b 自对句落诚实披露(3.34pp INSUFFICIENT_EVIDENCE)',
      len(fams(r)) == 1 and fams(r)[0]['token'] == '3.34pp', str(r['checks']))

print('== D 变异自证(摘除修复=对应判必红) ==')


def mutated_tc(replacements):
    """源面变异: 对 text_consistency.py 源码做文本替换后 exec 为新模块。"""
    src_path = os.path.join(ROOT, 'scripts', 'research_contract',
                            'text_consistency.py')
    src = open(src_path, encoding='utf-8').read()
    for old, new in replacements:
        assert old in src, f'变异锚缺失: {old[:40]}'
        src = src.replace(old, new)
    ns = {'__name__': 'tc_mutated', '__file__': src_path}
    exec(compile(src, src_path, 'exec'), ns)
    return ns


# M1 摘除披露分支→A1 复现(静默吞回归)
mut = mutated_tc([("if (_spread_ctx in seg_scoped",
                   "if (False and _spread_ctx in seg_scoped")])
rm = mut['check_text']
r1 = rm(SENT_ADP, snapshot=SNAP, thresholds=THR)
d1 = [c for c in r1['checks'] if c['family'] == 'spread_ambiguous']
check('M1 摘除披露分支→真句复现静默吞(0 检查)',
      len(d1) == 0 and r1['stats']['checks'] == 0, str(r1['stats']))

# M2 摘除相异守卫(回退旧长度门+取前两别名)→C1 复现(自对假红回归)
mut2 = mutated_tc([
    ('if len(distinct) < 2:\n        return []\n    a, b = distinct[0][0], distinct[1][0]',
     'if len(mids) < 2:\n        return []\n    a, b = mids[0][0], mids[1][0]')])
rm2 = mut2['check_text']
r2 = rm2(SENT_SELF, snapshot=SNAP, thresholds=THR)
check('M2 摘除相异守卫→自对假红复现',
      r2['stats']['contradicted'] == 1, str(r2['stats']))

print(f'\n== R35 结果: {PASS} PASS / {FAIL} FAIL ==')
sys.exit(0 if FAIL == 0 else 1)
