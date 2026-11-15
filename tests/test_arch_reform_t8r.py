#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T8 整改轮机制回归(每族一合成变体+启封条目常备面)。

覆盖: EA-1距离路由/EA-2时长换算/EA-4贡献集/EA-5枚举前向窗口/EA-6常量路由/
EC-1带标签/EC-2评分卡/EC-3概率和/EC-4目标区间/EN-1叙事方向/HC-1时代面/
HC-2前情链延展/prior 反噬防护(本期X(旧日期口径))。
判定: 36 PASS / 0 FAIL 方绿;机制族失败=整改失效,禁合并。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from migration_matrix import load_era                    # noqa: E402
from research_contract import text_consistency as tc     # noqa: E402

snap, prior, thr = load_era('20261114')
snap08, prior08, _ = load_era('20261108')
RESULTS = []


def run(text, sn=None, pr=None):
    return tc.check_text(text, snapshot=sn or snap, thresholds=thr,
                         prior_anchors=pr or prior)


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), detail))
    print(f"  {'✅' if ok else '❌'} {name}" + (f"  [{detail}]" if detail
                                                and not ok else ''))


def has(r, family, status, value=None):
    for c in r['checks']:
        if c['family'] == family and c['status'] == status and \
                (value is None or abs((c.get('value') or 0) - value)
                 < 1e-9):
            return c
    return None


print("== EA-1 距离值路由(值=|fact−阈值|, 不绑指标水平) ==")
r = run('DXY 103.41，距104强势阈值0.59点，仍在中性区间内。')
check('EA-1a CN 距离形态 VERIFIED',
      has(r, 'threshold_distance', 'VERIFIED', 0.59),
      str([(c['family'], c['status']) for c in r['checks']]))
check('EA-1b 0.59 不作 DXY 水平误杀',
      r['verdict'] == 'VERIFIED', r['verdict'])
r = run('The dollar index sits at 103.41, just 0.59 points below '
        'the 104 strong-dollar threshold.')
check('EA-1c EN below 形态 VERIFIED',
      has(r, 'threshold_distance', 'VERIFIED', 0.59) and
      r['verdict'] == 'VERIFIED', r['verdict'])
r = run('30Y UST 5.25%，在5%红线上方0.25pp，压力未解。', sn=snap08, pr=prior08)
check('EA-1d 红线上方25bp 时代面 VERIFIED',
      has(r, 'threshold_distance', 'VERIFIED', 0.25) and
      r['verdict'] == 'VERIFIED', r['verdict'])

print("== EA-2 时长换算复述 ==")
r = run('SPX_EPS 数据滞后约166天（约5个半月），引用须注明。')
check('EA-2a N个半月=N+0.5 月',
      has(r, 'lag_duration', 'VERIFIED'), str(r['checks']))
r = run('SPX_EPS 数据滞后约166天（约4个半月），引用须注明。')
check('EA-2b 错误换算 CONTRA',
      has(r, 'lag_duration', 'CONTRADICTED') and
      r['verdict'] == 'CONTRADICTED', r['verdict'])

print("== EA-4 分解贡献集(贡献标记之后;等式括注排除) ==")
r = run('名义10Y +0.24pp的分解：实际利率贡献+0.23pp、BEI贡献+0.01pp'
        '（0.23+0.01=0.24）。')
check('EA-4a 正确恒等式 VERIFIED',
      has(r, 'additivity', 'VERIFIED') and r['verdict'] == 'VERIFIED',
      r['verdict'])
r = run('名义10Y +0.24pp的分解：实际利率贡献+0.20pp、BEI贡献+0.01pp'
        '（0.20+0.01=0.21）。')
check('EA-4b 贡献和断裂 CONTRA',
      has(r, 'additivity', 'CONTRADICTED') and
      r['verdict'] == 'CONTRADICTED', r['verdict'])

print("== EA-5 枚举前向窗口/前向别名 ==")
r = run('通胀：10月CPI同比+4.08%、环比+0.35%、核心CPI同比+2.87%。')
c_m12 = has(r, 'change/m12', 'VERIFIED') or has(r, 'level', 'VERIFIED')
check('EA-5a 顿号枚举全 VERIFIED(0.35 归环比)',
      r['verdict'] == 'VERIFIED' and len(r['unbound']) == 0, r['verdict'])
r = run('通胀：10月CPI同比+4.08%、环比+0.35%、核心CPI同比+2.99%。')
check('EA-5b 枚举末位错值 CONTRA(2.99 归核心CPI)',
      r['verdict'] == 'CONTRADICTED', r['verdict'])

print("== EA-6 注册表常量路由(阈值语境整数值) ==")
r = run('WTI期货回落至88.92美元，跌破90美元阈值。')
check('EA-6a 90=wti p90 常量不误绑水平',
      has(r, 'threshold_constant', 'VERIFIED') and
      r['verdict'] == 'VERIFIED', r['verdict'])
r = run('沪深两市成交额12245.39亿元，高于1万亿/日底部确认阈值。')
check('EA-6b 1万亿=cn_turnover 常量',
      has(r, 'threshold_constant', 'VERIFIED') and
      r['verdict'] == 'VERIFIED', r['verdict'])

print("== EC-1 带标签 ==")
r = run('HY OAS 3.20%（-0.22pp），仍处恐慌区（>500bp），压力极端。')
check('EC-1a 恐慌区错标 CONTRA',
      has(r, 'band_label', 'CONTRADICTED') and
      r['verdict'] == 'CONTRADICTED', r['verdict'])
r = run('HY OAS 3.20%，距400bp警告线0.80个百分点，尚在警告带下沿之内。')
check('EC-1b 警告带下沿之内=低于该带 VERIFIED',
      has(r, 'band_label', 'VERIFIED') and r['verdict'] == 'VERIFIED',
      r['verdict'])

print("== EC-2 评分卡总分 ==")
r = run('体制评分卡：增长总分+0、通胀总分+2，映射衰退。')
check('EC-2a 正确总分+映射 VERIFIED',
      has(r, 'scorecard_total', 'VERIFIED') and
      has(r, 'regime_mapping', 'VERIFIED'), str(r['checks']))
r = run('体制评分卡：通胀总分+3，映射维持滞胀。')
check('EC-2b 错误总分 CONTRA',
      has(r, 'scorecard_total', 'CONTRADICTED') and
      has(r, 'regime_mapping', 'CONTRADICTED'), str(r['checks']))

print("== EC-3 概率和 ==")
r = run('情景矩阵（概率和=100%）：衰退35%｜滞胀35%（基准）｜类滞胀20%｜'
        '尾部10%。')
check('EC-3a 和=100 VERIFIED',
      has(r, 'probability_sum', 'VERIFIED'), str(r['checks']))
r = run('情景矩阵（概率和=100%）：衰退35%｜滞胀35%（基准）｜类滞胀25%｜'
        '金发姑娘15%｜尾部5%。')
check('EC-3b 和=115 CONTRA',
      has(r, 'probability_sum', 'CONTRADICTED') and
      r['verdict'] == 'CONTRADICTED', r['verdict'])

print("== EC-4 当前目标区间 ==")
r = run('美联储当前目标区间为3.75–4.00%。')
check('EC-4a 正确区间 VERIFIED',
      has(r, 'target_range', 'VERIFIED'), str(r['checks']))
r = run('美联储当前目标区间为4.07–4.32%（对应2026-12/2027-01期货隐含）。')
check('EC-4b 现行区间冒充 CONTRA',
      has(r, 'target_range', 'CONTRADICTED'), str(r['checks']))
r = run('2026-12期货隐含目标区间为4.07–4.32%。')
check('EC-4c 前瞻口径不核(跳过)',
      not any(c['family'] == 'target_range' for c in r['checks']),
      str(r['checks']))

print("== EN-1 叙事-数值方向 ==")
r = run('本周美元走弱、欧元升值：DXY 103.41（+1.09%），EURUSD 1.11'
        '（-1.59%）。')
nd = [c for c in r['checks'] if c['family'] == 'narrative_direction']
check('EN-1a 双向叙事反转 CONTRA',
      len(nd) >= 2 and all(c['status'] == 'CONTRADICTED' for c in nd) and
      r['verdict'] == 'CONTRADICTED', str(nd))
r = run('2s10s 0.27%（-0.08pp），曲线倒挂加深，信号强化。')
check('EN-1b 非负值言倒挂 CONTRA',
      has(r, 'narrative_direction', 'CONTRADICTED'), str(r['checks']))
r = run('欧元贬值压力延续：EURUSD 1.11（-1.59%）。')
check('EN-1c 方向一致不误杀',
      r['verdict'] == 'VERIFIED' and not
      any(c['family'] == 'narrative_direction' for c in r['checks']),
      str(r['checks']))
r = run('WTI期货从上期的103.44美元回落至本期88.92美元。')
check('EN-1d 货币后缀(N美元回落)不触美元叙事',
      not any(c['family'] == 'narrative_direction' for c in r['checks']),
      str(r['checks']))

print("== HC-1 时代面(同句异时代须异判) ==")
txt = '30Y UST回落6bp至5.25%，仍在5%红线上方25bp（0.25pp）。'
r_ok = run(txt, sn=snap08, pr=prior08)
r_bad = run(txt)                     # 11-14 面 UST_30Y≠5.25
check('HC-1a 11-08 面 VERIFIED',
      r_ok['verdict'] == 'VERIFIED', r_ok['verdict'])
check('HC-1b 同句在 11-14 面 CONTRA(时代敏感实证)',
      r_bad['verdict'] == 'CONTRADICTED', r_bad['verdict'])

print("== HC-2 前情链延展(10-24/10-31 入链) ==")
r = run('WTI期货上期103.44美元（2026-10-23口径，上期报告引用），'
        '本期回落至88.92美元。')
check('HC-2a 上期103.44 命中 10-24 锚',
      has(r, 'prior_reference', 'VERIFIED') and
      r['verdict'] == 'VERIFIED', r['verdict'])

print("== prior 反噬防护(上期X回升至本期Y) ==")
r = run('WTI期货从上期的103.44美元回落至本期88.92美元（2026-11-13口径），'
        '地缘溢价回吐。')
check('PR-1a 正向表述 VERIFIED',
      r['verdict'] == 'VERIFIED', str(r['checks']))
r = run('WTI期货从上期的88.92美元回升至本期103.44美元（2026-10-23口径），'
        '地缘溢价重新注入。')
lv = [c for c in r['checks']
      if c['family'] == 'level' and c['status'] == 'CONTRADICTED']
check('PR-1b 本期错值归主循环 CONTRA',
      r['verdict'] == 'CONTRADICTED' and lv, str(r['checks']))

print("== 启封条目常备面(9+6 全数入回归) ==")
QA = '/Users/cast/agent-loop/ARCH-REFORM/QA/heldout-sealed'
if not os.path.isdir(QA):
    # 六层区分: 封存件=操作者面工件,CI 干净克隆不在场→显式 SKIP 不计判
    # (t1t2 签字稿同款守卫;本机路径在场=本地全判,CI 面=诚实降面)。
    print("  ⏭️ 启封条目 15 判 [QA 封存件不在本机(CI 面)——"
          "登记 PHASE3-LOG T8 节;不以离线面冒充留出验收]")
else:
    n_ok = 0
    for fn, want in (('V5-HELDOUT.json', 'CONTRADICTED'),
                     ('V6-HELDOUT.json', 'VERIFIED')):
        for it in json.load(open(os.path.join(QA, fn)))['items']:
            era = it.get('base_anchor_set', '20261114')
            s, p, _ = load_era(era)
            rr = tc.check_text(it['text'], snapshot=s, thresholds=thr,
                               prior_anchors=p)
            good = rr['verdict'] == want and not rr['unbound']
            n_ok += good
            if not good:
                check(f'heldout {it["id"]}', False, rr['verdict'])
    check(f'启封条目 {n_ok}/15', n_ok == 15)

n_pass = sum(1 for _, ok, _ in RESULTS if ok)
print(f"\nT8R 判定: {n_pass} PASS / {len(RESULTS) - n_pass} FAIL")
sys.exit(0 if n_pass == len(RESULTS) else 1)
