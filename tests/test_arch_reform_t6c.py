#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T6c 文本一致性验收: 断言绑定引擎 check_text + 迁移矩阵公开面。

验收面(对照 PHASE3-PLAN T6 与 MIGRATION-CRITERIA P1/P2 公开面):
  A  绑定单元: 别名就近/承前句 carry/前值角色位置式/窗口词/方向词/
     显示位对齐(2dp 与约数有效位)/滞后仅 day 型;
  B  语义族检查器: 距离(常量 token 判别+无字面常量回退)/常量复述跳过
     距离值/带关系承前句/区间端点遮蔽/排名/相关(含 nan 诚实);
  C  夹具矩阵: V5 公开 21 条全 CONTRADICTED(P2 公开面≥95%+
     六族地板 100%),V6 公开 14 条全 VERIFIED(P1 零误杀公开面);
  D  防伪纪律: 逐 V5 条至少一条 CONTRA 命中其故障族机制(非歪打正着);
  E  纯度: 零环境/零网络/零随机/零模型调用(源码静态扫描);
  F  结构纪律: 数字遮罩序(日期>区间>别名;ISO 日期尾不被区间模式吞)。

数据纪律: t6 快照/锚链/qa 公开集=仓内冻结副本(LIVE 只读拷贝先例);
封存 heldout 不入仓(T8 独立审计席专属,本套件零引用)。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from research_contract import claim_factory as cf            # noqa: E402
from research_contract import text_consistency as tc          # noqa: E402

FIX = os.path.join(ROOT, 'tests', 'fixtures', 't6')
QA = os.path.join(ROOT, 'tests', 'fixtures', 'qa')
SNAP = json.load(open(os.path.join(FIX, 'snapshot_20261114_v2.json')))
PRIOR = {'2026-11-08': json.load(open(os.path.join(FIX, 'anchors_20261108.json'))),
         '2026-11-14': json.load(open(os.path.join(FIX, 'anchors_20261114.json')))}
THR = cf.load_thresholds()
V5 = json.load(open(os.path.join(QA, 'V5-INJECTIONS.json')))['items']
V6 = json.load(open(os.path.join(QA, 'V6-PARAPHRASES.json')))['items']

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
    return tc.check_text(text, snapshot=SNAP, thresholds=THR,
                         prior_anchors=PRIOR)


def fact_status(text, want_family_prefix=None):
    r = ct(text)
    hits = [c for c in r['checks']
            if want_family_prefix is None
            or c['family'].startswith(want_family_prefix)]
    return r, hits


print('== A 绑定单元 ==')

# A1 承前句 carry: 无别名句的环比 token 绑定前句指标(V5-006 机制)
r, _ = fact_status('就业：10月失业率4.10%（前值4.20%），环比下降0.10%')
fams = {(c['family'], c.get('metric')) for c in r['checks']
        if c['status'] == 'CONTRADICTED'}
check('A1 承前句环比绑定→0.10% 捕获(unit_confusion 形态)',
      r['verdict'] == 'CONTRADICTED'
      and ('level', 'UNEMPLOYMENT') in fams, str(fams))

# A2 显示位对齐: 2dp 显示值不误杀(+2.51 vs 2.5053)
r, hits = fact_status('SPX 本周+2.51%，收于7,561.67。', 'change/')
check('A2 显示位对齐 2dp→VERIFIED',
      hits and all(c['status'] == 'VERIFIED' for c in hits)
      and any('显示位对齐' in (c.get('note') or '') for c in hits),
      str([(c['family'], c['status'], c.get('note')) for c in hits]))

# A3 约数有效位: 约1.22万亿 vs 12245.39→不误杀
r, hits = fact_status('沪深两市成交额12,245.39亿元，约1.22万亿元。', 'level')
lv = [c for c in hits if c.get('metric') == 'CN_TOTAL_TURNOVER']
check('A3 约数有效位对齐→VERIFIED',
      lv and all(c['status'] == 'VERIFIED' for c in lv),
      str([(c['token'], c['status']) for c in lv]))

# A4 滞后仅 day 型: 滞后字样+percent 不产 lag 假阳性
r, _ = fact_status('日本无担保隔夜拆借利率1.04%（2026-09，滞后）。')
check('A4 percent 型禁产 observation_lag',
      not any(c['family'] == 'observation_lag' for c in r['checks']))

# A5 水平标记: climbed to/至 后的数=水平(非变化)
r, hits = fact_status('US initial claims climbed to 200K in the week of '
                      '2026-11-07.', 'level')
check('A5 to/至 水平标记→level VERIFIED',
      hits and all(c['status'] == 'VERIFIED' for c in hits),
      str([(c['family'], c['status']) for c in hits]))

# A6 前值角色位置式: from X 的 X=前值;to X 的 X=本期(V6-013 机制)
r, _ = fact_status('the unemployment rate edged down to 4.10% from 4.20%')
lv = [c for c in r['checks'] if c['family'] == 'level'
      and c.get('metric') == 'UNEMPLOYMENT']
check('A6 to=本期水平 VERIFIED + from=前值辖域',
      lv and all(c['status'] == 'VERIFIED' for c in lv)
      and not any(c['family'] == 'level' and c['token'] == '4.20%'
                  and c['status'] == 'CONTRADICTED' for c in r['checks']),
      str([(c['family'], c['token'], c['status']) for c in r['checks']]))

print('== B 语义族检查器 ==')

# B1 距离: 字面常量在场(距警告线400bp仅0.80pp)
r, hits = fact_status('HY OAS 3.20%，距警告线400bp仅0.80pp。', 'threshold_')
check('B1 距离检查器(常量 token 判别)',
      any(c['family'] == 'threshold_distance' and c['status'] == 'VERIFIED'
          for c in hits), str([(c['family'], c['status']) for c in hits]))

# B2 距离: 无字面常量回退(距警告线80bp→|3.2−4.0|=0.8)
r, hits = fact_status('HY OAS 3.20%，距警告线80bp。', 'threshold_')
check('B2 距离无字面常量回退',
      any(c['family'] == 'threshold_distance' and c['status'] == 'VERIFIED'
          and abs(c['value'] - 0.8) < 1e-9 for c in hits),
      str([(c['family'], c['value'], c['status']) for c in hits]))

# B3 常量复述跳过距离值(V6-002 词序变体)
r, hits = fact_status('HY OAS 3.20%，距400bp警告线0.80个百分点。',
                      'threshold_constant')
check('B3 常量检查器跳过距离值',
      not hits or all(c['token'] != '0.80个百分点' for c in hits),
      str([(c['token'], c['status']) for c in hits]))

# B4 带关系承前句(V5-016 机制: 突破104 当实为103.41)
r, hits = fact_status('DXY 103.41（+1.09%）。本周突破104强势阈值、'
                      '进入强势区间，构成系统性压制。', 'band_relation')
check('B4 带关系承前句捕获',
      hits and all(c['status'] == 'CONTRADICTED' for c in hits),
      str([(c['family'], c['status']) for c in hits]))

# B5 区间端点遮蔽(100-104 不入断言域)
r, _ = fact_status('DXY 103.41，处100-104中性区间上沿；若后续站上104将转为强势区间。')
unb = [u for u in r['unbound'] if re.match(r'^\d', u['raw'] or '')]
check('B5 区间端点遮蔽→无数值孤儿绑定',
      not any(u['raw'].startswith(('100', '104')) for u in r['unbound'])
      and r['verdict'] != 'CONTRADICTED',
      str([(u['raw'], u['ctx']) for u in r['unbound']]))

# B6 相关 nan 诚实: nan 字面 vs 窗含 nan 源→同义互证 VERIFIED
r, hits = fact_status('SPX-EZU的20日相关为nan（窗含采集失败源）。', 'statistic')
check('B6 相关 nan 同义互证',
      hits and all(c['status'] == 'VERIFIED' for c in hits),
      str([(c['token'], c['status'], c.get('note')) for c in hits]))

# B7 相关符号(V5-011 机制)
r, hits = fact_status('美元-黄金的20日相关系数为+0.33。', 'statistic')
check('B7 相关符号翻转→CONTRADICTED',
      hits and any(c['status'] == 'CONTRADICTED' for c in hits),
      str([(c['token'], c['status']) for c in hits]))

print('== C 夹具矩阵(公开面) ==')

v5_bad = []
for it in V5:
    r = ct(it['text'])
    if r['verdict'] != 'CONTRADICTED':
        v5_bad.append((it['id'], r['verdict']))
check('C1 V5 公开 21/21 CONTRADICTED(P2 公开面地板)',
      len(v5_bad) == 0, str(v5_bad))

v6_bad = []
for it in V6:
    r = ct(it['text'])
    if r['verdict'] != 'VERIFIED':
        v6_bad.append((it['id'], r['verdict']))
check('C2 V6 公开 14/14 VERIFIED(P1 零误杀公开面)',
      len(v6_bad) == 0, str(v6_bad))

fams_covered = {it['fault_family'] for it in V5 if ct(it['text'])['verdict']
                == 'CONTRADICTED'}
all_fams = {it['fault_family'] for it in V5}
check('C3 V5 六族以上地板 100%(全族捕获)',
      fams_covered == all_fams and len(all_fams) >= 6,
      f'{len(fams_covered)}/{len(all_fams)}')

# C4/P5: V6 未映射数值 token=0(manifest 复核+游离扫描口径)
v6_unmapped = []
for it in V6:
    r = ct(it['text'])
    v6_unmapped += [(it['id'], u['raw']) for u in r['unbound']]
check('C4 V6 未映射数值 token=0(P5)', not v6_unmapped, str(v6_unmapped))

# C5/P5 对偶: V5 未映射也须为 0(拦截不靠 unbound 兜底)
v5_unmapped = []
for it in V5:
    r = ct(it['text'])
    v5_unmapped += [(it['id'], u['raw']) for u in r['unbound']]
check('C5 V5 未映射数值 token=0', not v5_unmapped, str(v5_unmapped))

print('== D 防伪纪律(命中机制族内) ==')

D_MAP = {
    'identity_confusion': ('level', 'comparison'),
    'value_collision': ('threshold_constant', 'threshold_distance', 'level'),
    'observation_lag_error': ('observation_lag',),
    'window_confusion': ('change/',),
    'unit_confusion': ('change/', 'level'),
    'level_vs_change': ('change/', 'level'),
    'sign_flip': ('change/', 'level'),
    'additivity_break': ('additivity',),
    'additivity_break+stale_value': ('additivity',),
    'correlation_error': ('statistic',),
    'nan_fabrication': ('statistic', 'change/'),
    'count_error': ('consecutive_periods', 'compound_condition_count'),
    'band_threshold_error': ('band_relation',),
    'ranking_error': ('ranking', 'change/'),
    'prior_reference_error': ('prior_reference', 'level'),
    'rounding_error': ('spread_arithmetic', 'level'),
    'digit_error': ('level',),
    'neighbor_attribution': ('change/', 'level'),
}
d_bad = []
for it in V5:
    r = ct(it['text'])
    contra_fams = {c['family'] for c in r['checks']
                   if c['status'] == 'CONTRADICTED'}
    exp = D_MAP.get(it['fault_family'])
    if not exp or not contra_fams.intersection(
            tuple(f if f.endswith('/') else f + ';' for f in exp)) and \
            not any(any(cf_.startswith(e) for cf_ in contra_fams)
                    for e in exp):
        d_bad.append((it['id'], it['fault_family'], sorted(contra_fams)))
check('D1 逐条命中机制在故障族内(非歪打正着)', len(d_bad) == 0, str(d_bad))

print('== E 纯度 ==')

SRC = open(os.path.join(ROOT, 'scripts', 'research_contract',
                        'text_consistency.py'), encoding='utf-8').read()
check('E1 零环境读取', not re.search(r'\bos\.environ|getenv', SRC))
check('E2 零网络', not re.search(r'\b(socket|urllib|requests|http)', SRC))
check('E3 零随机', not re.search(r'\brandom\b', SRC))
check('E4 零模型客户端', not re.search(r'glm|zhipu|bigmodel|anthropic|'
      'openai', SRC, re.I))
check('E5 stdlib+契约内依赖',
      set(re.findall(r'^(?:from|import)\s+([\w.]+)', SRC, re.M)) <= {
          're', 'json', 'math', 'datetime', 'research_contract'}, '')

print('== F 结构纪律 ==')

m = tc._masked_clause('10月新增人民币贷款-5,846亿元（2026-10-01，WARN）',
                      tc._find_alias('10月新增人民币贷款-5,846亿元'
                                     '（2026-10-01，WARN）'))
toks = [t['raw'] for t in tc._extract_tokens(m)]
check('F1 ISO 日期尾不被区间模式吞(无 2026 孤儿)',
      not any(t.strip().startswith('2026') for t in toks), str(toks))

m2 = tc._masked_clause('DXY中性区间100-104。', tc._find_alias('DXY中性区间100-104。'))
toks2 = [t['raw'] for t in tc._extract_tokens(m2)]
check('F2 数值区间端点全遮蔽', not toks2, str(toks2))

print(f"\nT6c 判定: {PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
