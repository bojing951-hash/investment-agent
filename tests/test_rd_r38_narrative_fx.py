#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R38: 叙事方向检查器覆盖面表驱动扩展——日元/英镑族接入(RDG-20261115-010)。

缺陷(T8-R2 遗留⑤): _check_narrative_direction 仅美元/欧元/2s10s 三族,
日元/英镑方向叙事零检查。真实复现(main 基线亲证): era 20261114 快照含
USDJPY(周+1.51%),句「本周日元升值,美元兑日元159.88(+1.51%)」判 VERIFIED
零 check——日元升值叙事与序列+1.51%(日元实际贬值)方向相反而放行。

修法: ①FX 族规格表 _NARR_FX_ROWS(DXY/EURUSD 原样迁入行为保持;GBPUSD
直读;USDJPY 主体=日元反序[报价对先例]+对名直读行单列防误读);②前瞻/
历史语境族级守卫 _NARR_FORWARD_RE(预测句不对当前周窗核方向;真实实例=
20261113T005117Z 资产方向句);③真句嵌入(3 份真实档原文句)+变异自证。

判定: PASS 计数=全绿;机制族失败=扩展失效,禁合并。
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
snap08, prior08, _ = load_era('20261108')    # USDJPY 周+0.39 / GBPUSD 周+0.58
RESULTS = []


def run(text, sn=None, pr=None):
    return tc.check_text(text, snapshot=sn or snap, thresholds=thr,
                         prior_anchors=pr or prior)


def nd_checks(r):
    return [c for c in r['checks'] if c['family'] == 'narrative_direction']


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), detail))
    print(f"  {'✅' if ok else '❌'} {name}" + (f"  [{detail}]"
                                                if detail and not ok else ''))


def contra_tokens(r):
    return {c['token'] for c in nd_checks(r) if c['status'] == 'CONTRADICTED'}


print("== R38-T1 真句嵌入(3 份真实档原文句,新族零误杀) ==")
# 出处①: output/weekly/weekly_report_20261108_UNVALIDATED.md L40(era 同期)
REAL_1108 = ('【推断】日经−9.25%为本周主要股指中最大跌幅，且与USDJPY+0.39%'
             '（日元走弱）同向出现——按“日经225 vs 美元/日元”20日相关+0.30，'
             '日元贬值与日经下跌在统计上同向（描述统计非因果）；'
             '日元贬值未能对冲股市下跌，此为【假设】。')
r = run(REAL_1108, sn=snap08, pr=prior08)
check('T1a 11-08 周报真句(日元走弱/贬值×3 处,周+0.39% 一致)零误杀',
      not any(c['status'] == 'CONTRADICTED' for c in nd_checks(r)),
      str(nd_checks(r)))
# 出处②: output/research_runs/20261113T005117Z_*/report.md L66(预测句)
REAL_FCST = ('资产方向判断: USDJPY 下行(日元升值)(置信: 纯逻辑推理) '
             '利差收窄的汇率反应幅度与节奏无本引擎可验证证据')
r = run(REAL_FCST)
check('T1b 20261113T005117Z 资产方向句(预测)前瞻守卫零 fire',
      not nd_checks(r), str(nd_checks(r)))
# 出处③: audit/r27_gateb_repro/weekly_report_20261114_UNVALIDATED.md L125
REAL_1114 = ('USDJPY 159.88（+1.51%），测试160。【推断】利差扩张方向与'
             '日元贬值方向一致。')
r = run(REAL_1114)
check('T1c 11-14 周报真句(日元贬值,周+1.51% 一致)零误杀',
      not any(c['status'] == 'CONTRADICTED' for c in nd_checks(r)),
      str(nd_checks(r)))

print("== R38-T2 新覆盖拦截(复现+真句变异+双 era 方向矩阵) ==")
r = run('本周日元升值,套息交易延续;美元兑日元159.88(+1.51%)。')
n = nd_checks(r)
check('T2a R38 开轮复现句转 CONTRA(日元升值 vs 周+1.51%)',
      len(n) == 1 and n[0]['status'] == 'CONTRADICTED'
      and n[0]['metric'] == 'USDJPY' and n[0]['token'] == '日元升值'
      and n[0]['expected'] == '<0' and r['verdict'] == 'CONTRADICTED',
      str(n))
r = run(REAL_1108.replace('日元走弱', '日元升值').replace(
    '日元贬值与日经下跌', '日元升值与日经下跌').replace(
    '日元贬值未能对冲', '日元升值未能对冲'), sn=snap08, pr=prior08)
check('T2b 11-08 真句变异(日元方向全翻转,周+0.39%)必红',
      '日元升值' in contra_tokens(r), str(nd_checks(r)))
r = run('本周英镑走强,英镑兑美元1.32(-1.67%)。')
n = nd_checks(r)
check('T2c 英镑升值 vs GBPUSD 周−1.67%(era 11-14)CONTRA',
      len(n) == 1 and n[0]['token'] == '英镑升值'
      and n[0]['metric'] == 'GBPUSD' and n[0]['expected'] == '>0', str(n))
r = run('本周英镑贬值压力加大(era 11-08 面)。', sn=snap08, pr=prior08)
n = nd_checks(r)
check('T2d 英镑贬值 vs GBPUSD 周+0.58%(era 11-08)CONTRA',
      len(n) == 1 and n[0]['token'] == '英镑贬值'
      and n[0]['metric'] == 'GBPUSD' and n[0]['expected'] == '<0', str(n))
r = run('本周美元兑日元下行,出口股承压。')
n = nd_checks(r)
check('T2e 对名直读(美元兑日元下行 vs 周+1.51%)CONTRA',
      len(n) == 1 and n[0]['token'] == '美元兑日元下行'
      and n[0]['expected'] == '<0', str(n))
r = run('本周美元/日元走强,套息活跃。')
check('T2f 对名一致(美元/日元走强 vs 周+1.51%)不误杀',
      not nd_checks(r), str(nd_checks(r)))
r = run('The yen appreciated sharply this week.')
n = nd_checks(r)
check('T2g 英文主体(yen appreciated vs 周+1.51%)CONTRA',
      len(n) == 1 and n[0]['token'] == '日元升值', str(n))

print("== R38-T3 守卫与防误读(不误杀面) ==")
r = run('预计日元升值,利差交易或重启。')
check('T3a 预测句守卫(预计+紧邻方向词)零 fire',
      not nd_checks(r), str(nd_checks(r)))
r = run('历史上日元升值常伴波动放大。')
check('T3b 历史泛述守卫零 fire', not nd_checks(r), str(nd_checks(r)))
r = run('本周美元兑日元走弱,干预传闻再起。')
n = nd_checks(r)
check('T3c 对名防误读(美元兑日元走弱=序列降,周+1.51% 应红在对名行非主体行)',
      len(n) == 1 and n[0]['token'] == '美元兑日元下行'
      and '日元贬值' not in contra_tokens(r), str(n))
r = run('美元兑日元159.88(+1.51%),测试160。')
check('T3d 纯数值句(无方向词)零 fire', not nd_checks(r), str(nd_checks(r)))
r = run('此前一日收于158.40,100日元回落形态未现。')
check('T3e 货币金额后缀(N日元)不触主体句', not nd_checks(r),
      str(nd_checks(r)))
r = run('本周美元走弱、欧元升值：DXY 103.41（+1.09%），EURUSD 1.11'
        '（-1.59%）。')
n = nd_checks(r)
check('T3f DXY/EURUSD 旧行为保持(EN-1a 同款双 CONTRA)',
      len(n) >= 2 and all(c['status'] == 'CONTRADICTED' for c in n)
      and {c['token'] for c in n} == {'美元走弱', '欧元升值'}, str(n))
r = run('欧元贬值压力延续：EURUSD 1.11（-1.59%）。')
check('T3g 方向一致不误杀(EN-1c 同款)', not nd_checks(r),
      str(nd_checks(r)))
r = run('WTI期货从上期的103.44美元回落至本期88.92美元。')
check('T3h 货币后缀不触美元叙事(EN-1d 同款)', not nd_checks(r),
      str(nd_checks(r)))
r = run('2s10s 0.27%（-0.08pp），曲线倒挂加深，信号强化。')
n = nd_checks(r)
check('T3i 2s10s 倒挂族旧行为保持(EN-1b 同款)',
      len(n) == 1 and n[0]['token'] == '倒挂', str(n))

print("== R38-T4 合成快照(USDJPY 负周矩阵,era 夹具双正周补全) ==")
syn = {'facts': [{'metric_id': 'USDJPY', 'value': 157.0,
                  'observation_date': '2026-11-14',
                  'derived': {'week': {'pct_change': -0.8}}}]}
r = run('本周日元升值,避险买盘主导。', sn=syn)
check('T4a 日元升值 vs 周−0.8% 一致不误杀', not nd_checks(r),
      str(nd_checks(r)))
r = run('本周日元贬值,风险偏好回升。', sn=syn)
n = nd_checks(r)
check('T4b 日元贬值 vs 周−0.8% CONTRA',
      len(n) == 1 and n[0]['token'] == '日元贬值'
      and n[0]['expected'] == '>0', str(n))
r = run('本周美元兑日元上行,再创阶段新高。', sn=syn)
n = nd_checks(r)
check('T4c 对名上行 vs 周−0.8% CONTRA',
      len(n) == 1 and n[0]['token'] == '美元兑日元上行', str(n))
r = run('本周美元兑日元走弱。', sn=syn)
check('T4d 对名走弱 vs 周−0.8% 一致不误杀', not nd_checks(r),
      str(nd_checks(r)))

print("== R38-T5 一审审计形态冻结(3 MAJOR+2 MINOR 回归用例) ==")
r = run('本周美元对日元上涨1.51%,与套息活跃同向。')
check('T5a FP1/FP2 「美元对日元」一致句(对名=序列升,周+1.51%)零误杀',
      not nd_checks(r), str(nd_checks(r)))
r = run('本周美元对日元走低,出口承压。')
n = nd_checks(r)
check('T5b MAJOR-1 镜像 「美元对日元走低」真矛盾必红(对名行出手)',
      len(n) == 1 and n[0]['token'] == '美元兑日元下行'
      and '日元升值' not in contra_tokens(r), str(n))
r = run('欧元兑英镑走强,交叉盘波动加大。')
check('T5c FP12 交叉盘(欧元兑英镑)GBP 行零误杀',
      not nd_checks(r), str(nd_checks(r)))
r = run('本周美元走弱，市场预期降息;DXY 103.41（+1.09%）。')
n = nd_checks(r)
check('T5d FN9 真阳性恢复(同句后段预期词不连杀,main 行为)',
      len(n) == 1 and n[0]['token'] == '美元走弱'
      and n[0]['metric'] == 'DXY', str(n))
r = run('日元兑美元贬值,套息平仓压力上升。')
check('T5e FP7 交叉盘内嵌「美元贬值」DXY 行零误杀(守卫回灌旧行)',
      not any(c['metric'] == 'DXY' for c in nd_checks(r)),
      str(nd_checks(r)))
r = run('美元兑欧元升值,欧洲出口受益。')
check('T5f 交叉盘内嵌「欧元升值」EURUSD 行零误杀',
      not any(c['metric'] == 'EURUSD' for c in nd_checks(r)),
      str(nd_checks(r)))
r = run('美元兑日元本周走低,干预传闻再起。')
n = nd_checks(r)
check('T5g MINOR-1 对名+时间状语(本周介入)仍出手',
      len(n) == 1 and n[0]['token'] == '美元兑日元下行', str(n))
r = run('USDJPY本周走低。')
n = nd_checks(r)
check('T5h MINOR-1 变体 USDJPY+本周+方向词仍出手',
      len(n) == 1 and n[0]['token'] == '美元兑日元下行', str(n))
r = run('本周 yen 升值,避险资金流入。')
n = nd_checks(r)
check('T5i MINOR-2 中英混排(yen 升值)出手',
      len(n) == 1 and n[0]['token'] == '日元升值', str(n))
r = run('日元升值的预期升温。')
check('T5j 后缀守卫(的预期=预期对象非事实断言)零 fire',
      not nd_checks(r), str(nd_checks(r)))
r = run('资产方向判断: USDJPY 下行(日元升值)(置信: 纯逻辑推理)。')
check('T5k 括注继承宿主模态(方向判断括注)零 fire',
      not nd_checks(r), str(nd_checks(r)))

n_pass = sum(1 for _, ok, _ in RESULTS if ok)
print(f"\nR38 判定: {n_pass} PASS / {len(RESULTS) - n_pass} FAIL")
sys.exit(0 if n_pass == len(RESULTS) else 1)
