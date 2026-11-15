#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R40: 叙事方向守卫残余登记三项收口(R38 独立审计二轮附条件;RDG-010 回看)。

①MAJOR-3b 前置近距标记连杀当前周事实(漏报向回退残余): 前看窗内标记与
命中之间出现当前周锚(本周/当周/周内)→豁免前瞻豁免,恢复方向核验。
冻结回归: G5「通胀预期回落的同时,本周美元走弱」/G7「市场料将迎来拐点,
本周美元走弱」/B2「(此前预期落空的背景下)本周美元走弱」三句 main 正确
拦截、R38 版全漏;锚在标记前(「本周市场预期美元走弱」)仍属预期句不豁免。
②MINOR-3: 「日内」入对名行时间状语白名单+「英镑对美元」GBP 行容
(与 USDJPY 对名行对称;冻结 F5b)+「USD-JPY」连字形态。
③NIT-3: 「yen 大幅升值」非紧邻混排(幅度副词介入)。

注: 「日内」形态入检查面后与既有口径一致按周窗核方向(检查器既有简化,
如实注记)。全合成+era 夹具;CI 干净 clone 可跑。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from migration_matrix import load_era                    # noqa: E402
from research_contract import text_consistency as tc     # noqa: E402

snap, prior, thr = load_era('20261114')      # USDJPY 周+1.51 / GBPUSD 周−1.67
syn = {'facts': [{'metric_id': 'DXY', 'value': 104.0,
                  'observation_date': '2026-11-14',
                  'derived': {'week': {'pct_change': 0.8}}}]}
RESULTS = []


def run(text, sn=None):
    return tc.check_text(text, snapshot=sn or snap, thresholds=thr,
                         prior_anchors=prior)


def nd(r):
    return [c for c in r['checks'] if c['family'] == 'narrative_direction']


def contra(r):
    return {c['token'] for c in nd(r) if c['status'] == 'CONTRADICTED'}


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok)))
    print(('PASS ' if ok else 'FAIL ') + name
          + (f'  [{detail}]' if detail and not ok else ''))


print('== R40-§1 MAJOR-3b 当前周锚豁免(合成 DXY 周+0.8;G5/G7/B2 冻结) ==')
r = run('通胀预期回落的同时,本周美元走弱。', sn=syn)
check('G5 冻结: 标记后当前周锚→恢复拦截(CONTRA 美元走弱)',
      contra(r) == {'美元走弱'}, str(nd(r)))
r = run('市场料将迎来拐点,本周美元走弱。', sn=syn)
check('G7 冻结: 料将+本周锚→恢复拦截',
      contra(r) == {'美元走弱'}, str(nd(r)))
r = run('(此前预期落空的背景下)本周美元走弱。', sn=syn)
check('B2 冻结: 括注内标记+锚在括外命中前→恢复拦截',
      contra(r) == {'美元走弱'}, str(nd(r)))
r = run('本周市场预期美元走弱。', sn=syn)
check('锚在标记前(本周市场预期…)仍属预期句不豁免',
      not contra(r), str(nd(r)))
r = run('市场预期美元走弱。', sn=syn)
check('纯前瞻句照旧豁免(R38 行为保持)',
      not contra(r), str(nd(r)))
r = run('本周美元走弱。', sn=syn)
check('无标记当前周句照旧拦截(R38 行为保持)',
      contra(r) == {'美元走弱'}, str(nd(r)))

print('== R40-§2 MINOR-3 三形态(era 20261114: USDJPY +1.51/GBPUSD −1.67) ==')
r = run('英镑对美元走强。')
check('F5b 冻结: 「英镑对美元走强」vs 周−1.67 CONTRA(GBP 行容「对美元」)',
      contra(r) == {'英镑升值'}, str(nd(r)))
r = run('英镑对美元走弱。')
check('F5b 一致形态零误杀(「英镑对美元走弱」)',
      not contra(r), str(nd(r)))
r = run('英镑兑美元走强。')
check('「兑美元」旧形态保持(CONTRA)',
      contra(r) == {'英镑升值'}, str(nd(r)))
r = run('USD-JPY 日内走低。')
check('「USD-JPY 连字+日内」双新形态 vs +1.51 CONTRA',
      contra(r) == {'美元兑日元下行'}, str(nd(r)))
r = run('USD-JPY 走低。')
check('「USD-JPY」连字独立形态 CONTRA',
      contra(r) == {'美元兑日元下行'}, str(nd(r)))
r = run('USDJPY 日内走高。')
check('「日内」一致形态零误杀',
      not contra(r), str(nd(r)))

print('== R40-§3 NIT-3 yen 幅度副词介入(era 20261114: +1.51) ==')
r = run('yen 大幅升值,避险情绪主导。')
check('「yen 大幅升值」非紧邻混排 vs +1.51 CONTRA(反序族)',
      contra(r) == {'日元升值'}, str(nd(r)))
r = run('yen 大幅贬值,风险偏好回升。')
check('「yen 大幅贬值」一致零误杀',
      not contra(r), str(nd(r)))
r = run('yen 升值。')
check('「yen 升值」紧邻原形态保持(CONTRA)',
      contra(r) == {'日元升值'}, str(nd(r)))

print('== R40-§4 行为保持 spot(era 真句复用 R38 T1b/T1c) ==')
r = run('资产方向判断: USDJPY 下行(日元升值)(置信: 纯逻辑推理) '
        '利差收窄的汇率反应幅度与节奏无本引擎可验证证据')
check('预测句括注宿主守卫保持(零 fire)',
      not nd(r), str(nd(r)))
r = run('USDJPY 159.88（+1.51%），测试160。【推断】利差扩张方向与'
        '日元贬值方向一致。')
check('11-14 周报真句零误杀保持',
      not contra(r), str(nd(r)))

n_pass = sum(1 for _, ok in RESULTS if ok)
n_fail = len(RESULTS) - n_pass
print('═' * 64)
print(f'结果: PASS={n_pass} FAIL={n_fail}')
print('═' * 64)
sys.exit(0 if n_fail == 0 else 1)
