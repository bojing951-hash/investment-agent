#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T6a 契约补全验收: statistic 型(联合统计量)+ nan 源分流 + 派生视图阈值路由。

验收面(对照 PHASE3-PLAN T6 前置与 MIGRATION-CRITERIA P1/P2):
  A  镜像纪律: paired_daily_returns/pearson 与 LIVE correlation_calculator
     逐句等价(冻结档 correlation_20261114.frozen.md 数值锁定);
  B  工厂面: statistic claims 落 bundle 全过 schema;nan 源三态如实
     (缺席台账/None+nan_reason/数值);
  C  验证器: 符号翻=CONTRADICTED(V5-011 型);nan 窗载具体数=CONTRADICTED
     (V5-012 型);2dp 展示值=VERIFIED;序列缺席=INSUFFICIENT_EVIDENCE;
  D  nan 采集失败分流: 水平/变化/排名/配对不产+台账;lag 可算保留;
     nan↔nan 证据同态(非不符);
  E  派生视图阈值路由: .scorecard./_cumulative_gain 分流台账不炸;
     无结构标记真单位违约仍 fail-loud;
  F  纯度: 新码零环境/零网络/零随机(源码静态扫描)。

数据纪律: 冻结切片+冻结 md=LIVE 树只读拷贝(T4 既定先例;出处随档);
零绝对路径/零模型调用/零网络。
"""
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from research_contract import claim_factory as cf          # noqa: E402
from research_contract import claim_bundle as cb           # noqa: E402
from research_contract import claim_verifier as cv         # noqa: E402

FIX = os.path.join(ROOT, 'tests', 'fixtures', 't6')
SLICE = json.load(open(os.path.join(FIX, 'corr_series_slice_20261114.json')))
FROZEN_MD = open(os.path.join(FIX, 'correlation_20261114.frozen.md'),
                 encoding='utf-8').read()

PASS = FAIL = 0
def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f'  ✅ {name}')
    else:
        FAIL += 1
        print(f'  ❌ {name}  {detail}')


print('== A 镜像纪律(冻结档数值锁定) ==')

# A1/A2: 确定性小样本
sa = {'dates': ['2026-01-0%d' % d for d in range(1, 7)],
      'values': [100, 101, 100.5, 102, 101.5, 103]}
sb = {'dates': sa['dates'], 'values': [200, 202, 201, 204, 203, 206]}
pair, common = cf.paired_daily_returns(sa, sb)
r = cf.pearson(pair[0], pair[1])
check('A1 完全同向两序列相关≈1', r is not None and r > 0.999, f'r={r}')
sb2 = {'dates': sa['dates'], 'values': [200, 198, 199, 196, 197, 194]}
pair2, _ = cf.paired_daily_returns(sa, sb2)
r2 = cf.pearson(pair2[0], pair2[1])
check('A2 完全反向相关≈-1', r2 is not None and r2 < -0.999, f'r={r2}')

# A3: None 跳过(共同观测内连接)
sa3 = {'dates': ['d1', 'd2', 'd3', 'd4', 'd5'],
       'values': [100, 101, 102, 103, None]}
sb3 = {'dates': sa3['dates'], 'values': [50, 51, 52, 53, None]}
p3, _ = cf.paired_daily_returns(sa3, sb3)
check('A3 None 观测对跳过(d5 双侧缺→存活 3 对)',
      p3 is not None and len(p3[0]) == 3,
      f'n={len(p3[0]) if p3 else None}')

# A4: 零基双侧联合丢弃
sa4 = {'dates': ['d1', 'd2', 'd3', 'd4', 'd5'],
       'values': [100, 0, 101, 102, 103]}
sb4 = {'dates': sa4['dates'], 'values': [50, 51, 52, 53, 54]}
p4, _ = cf.paired_daily_returns(sa4, sb4)
check('A4 前值零基丢整对(n=3 非 4)', p4 is not None and len(p4[0]) == 3)

# A5: NaN 如实传播(不跳)
sa5 = {'dates': ['d1', 'd2', 'd3', 'd4', 'd5'],
       'values': [100, float('nan'), 101, 102, 103]}
sb5 = {'dates': sa5['dates'], 'values': [50, 51, 52, 53, 54]}
p5, _ = cf.paired_daily_returns(sa5, sb5)
r5 = cf.pearson(p5[0], p5[1])
check('A5 NaN 传播→pearson=nan(非 None)', r5 is not None and math.isnan(r5),
      f'r5={r5}')

# A6: 冻结档锁步(LIVE correlation_20261114.md 数值)
b_slice = cf.generate_claims_bundle(SLICE)
stat = {(tuple(c['metric_ids']), c['corr_window_days']): c
        for c in b_slice['claims'] if c['claim_type'] == 'statistic'}
frozen_vals = {}
for m in re.finditer(
        r'\| ([^|]+) \| ([-+][\d.]+|[-+]nan) \| \d+ \| ([-+][\d.]+|[-+]nan) \|',
        FROZEN_MD):
    label, c20, c60 = m.group(1).strip(), m.group(2), m.group(3)
    frozen_vals[label] = (c20, c60)
check('A6a 冻结档解析出 12 对', len(frozen_vals) == 12, f'n={len(frozen_vals)}')
label_map = {p['label']: (p['a'], p['b']) for p in cf.STATISTIC_PAIRS}
agree = disagree = 0
for label, (c20, c60) in frozen_vals.items():
    key = label_map.get(label)
    if not key:
        continue
    for w, txt in ((20, c20), (60, c60)):
        c = stat.get((key, w))
        if txt.endswith('nan'):
            ok = bool(c is not None and c['value'] is None
                      and c.get('nan_reason'))
        else:
            ok = (c is not None and c['value'] is not None
                  and abs(c['value'] - float(txt)) <= 0.005 + 1e-9)
        agree += ok
        disagree += (not ok)
check('A6b 12对×2窗 与冻结档逐格一致(nan 格=claim None+nan_reason)',
      disagree == 0 and agree >= 20, f'agree={agree} disagree={disagree}')
# A6c 关键对点名(V5-011 真值)
c = stat.get((('DXY', 'GOLD_F'), 20))
check('A6c DXY×GOLD_F 20d=-0.33±0.005(V5-011 真值)',
      c and c['value'] is not None and abs(c['value'] - (-0.33)) <= 0.005,
      f'v={c and c["value"]}')
c = stat.get((('SPX', 'EZU'), 20))
check('A6d SPX×EZU 20d=None+nan_reason(V5-012 真值=nan)',
      c and c['value'] is None and 'nan_in_window' in (c.get('nan_reason') or ''))


print('== B 工厂面 ==')
check('B1 statistic claims 全过 bundle schema',
      cb.validate_bundle(b_slice) is None,
      'validate_bundle raised')
check('B2 切片 statistic 数=可计算对数(16 序列全在→24 条中 nan 对产 None claim)',
      len(stat) == 24, f'n={len(stat)}')
led = [l for l in b_slice['coverage_ledger'] if l.get('scope') == 'statistic']
check('B3 序列全在→statistic 台账零缺席', len(led) == 0, f'n={len(led)}')
# B4: 序列缺席台账
snap_miss = dict(SLICE, series_store={k: v for k, v
                                      in SLICE['series_store'].items()
                                      if k not in ('TLT', 'EEM')})
b_miss = cf.generate_claims_bundle(snap_miss)
led_miss = [l for l in b_miss['coverage_ledger']
            if l.get('scope') == 'statistic' and 'series_absent' in l['reason']]
check('B4 成员序列缺席→台账 series_absent(按对记,诚实缺席非静默)',
      len(led_miss) == 3, f'n={len(led_miss)}')  # SPX×TLT, WTI×TLT, WTI×EEM


print('== C 验证器(statistic 裁决) ==')
res = cv.verify_bundle(b_slice, snapshot=SLICE)
verd = {v['claim_id']: v for v in res['verdicts']}
stat_ok = all(verd[c['claim_id']]['status'] in ('VERIFIED', 'STALE')
              for c in b_slice['claims'] if c['claim_type'] == 'statistic')
check('C1 工厂 statistic 面 clean 零假杀', stat_ok)

def tamper(metric_ids, w, value):
    bb = json.loads(json.dumps(
        {**b_slice, 'claims': b_slice['claims']}))
    # rebuild verdicts fresh each time
    for c in bb['claims']:
        if c['claim_type'] == 'statistic' and \
                tuple(c['metric_ids']) == metric_ids and \
                c['corr_window_days'] == w:
            c['value'] = value
            return bb
    raise AssertionError('claim not found')

# C2: V5-011 型符号翻(DXY×GOLD_F 20d 真值-0.33→+0.33)
r2v = cv.verify_bundle(tamper(('DXY', 'GOLD_F'), 20, 0.33), snapshot=SLICE)
tgt = next(c for c in tamper(('DXY','GOLD_F'),20,0.33)['claims']
           if c['claim_type']=='statistic' and tuple(c['metric_ids'])==('DXY','GOLD_F')
           and c['corr_window_days']==20)
st2 = {v['claim_id']: v for v in r2v['verdicts']}[tgt['claim_id']]['status']
check('C2 V5-011 符号翻→CONTRADICTED', st2 == 'CONTRADICTED', f'st={st2}')

# C3: V5-012 型 nan 窗载具体数(SPX×EZU 20d=None→+0.72)
tgt3 = next(c for c in tamper(('SPX','EZU'),20,0.72)['claims']
            if c['claim_type']=='statistic' and tuple(c['metric_ids'])==('SPX','EZU')
            and c['corr_window_days']==20)
r3v = cv.verify_bundle(tamper(('SPX','EZU'),20,0.72), snapshot=SLICE)
st3 = {v['claim_id']: v for v in r3v['verdicts']}[tgt3['claim_id']]['status']
check('C3 V5-012 nan 窗载具体数→CONTRADICTED(伪造)', st3 == 'CONTRADICTED',
      f'st={st3}')

# C4: 2dp 展示值=VERIFIED(-0.33 vs 全精度 -0.3256)
tgt4 = next(c for c in tamper(('DXY','GOLD_F'),20,-0.33)['claims']
            if c['claim_type']=='statistic' and tuple(c['metric_ids'])==('DXY','GOLD_F')
            and c['corr_window_days']==20)
r4v = cv.verify_bundle(tamper(('DXY','GOLD_F'),20,-0.33), snapshot=SLICE)
st4 = {v['claim_id']: v for v in r4v['verdicts']}[tgt4['claim_id']]['status']
check('C4 文本 2dp 值(-0.33)→VERIFIED(容差±0.005)', st4 == 'VERIFIED', f'st={st4}')

# C5: None 冒充(真值数值而 claim=None)
tgt5 = next(c for c in tamper(('DXY','GOLD_F'),20,None)['claims']
            if c['claim_type']=='statistic' and tuple(c['metric_ids'])==('DXY','GOLD_F')
            and c['corr_window_days']==20)
r5v = cv.verify_bundle(tamper(('DXY','GOLD_F'),20,None), snapshot=SLICE)
st5 = {v['claim_id']: v for v in r5v['verdicts']}[tgt5['claim_id']]['status']
check('C5 统计量缺席冒充(复算有值而 claim None)→CONTRADICTED',
      st5 == 'CONTRADICTED', f'st={st5}')

# C6: 序列缺席→INSUFFICIENT_EVIDENCE
snap6 = dict(SLICE, series_store={k: v for k, v
                                  in SLICE['series_store'].items() if k != 'TLT'})
b6 = cf.generate_claims_bundle(snap6)
# 从完整 bundle 借一条 SPX×TLT claim 验证缺席面
borrow = json.loads(json.dumps(next(
    c for c in b_slice['claims'] if c['claim_type'] == 'statistic'
    and tuple(c['metric_ids']) == ('SPX', 'TLT') and c['corr_window_days'] == 20)))
r6 = cv.verify_bundle({**b6, 'claims': b6['claims'] + [borrow]}, snapshot=snap6)
st6 = {v['claim_id']: v for v in r6['verdicts']}[borrow['claim_id']]['status']
check('C6 序列缺席→INSUFFICIENT_EVIDENCE(通道未闭合如实,非 CONTRADICTED)',
      st6 == 'INSUFFICIENT_EVIDENCE', f'st={st6}')


print('== D nan 采集失败分流 ==')
nan_fact = {'fact_id': 'ETFX@2026-11-13', 'metric_id': 'ETFX', 'unit': 'usd',
            'value': float('nan'), 'observation_date': '2026-11-13',
            'as_of': '2026-11-14T09:00:00+08:00', 'value_type': 'close',
            'source': 't', 'derived': {'week': {'basis_date': '2026-11-06',
                                                'basis_value': 100.0,
                                                'pct_change': float('nan')}}}
snapD = {'snapshot_id': 'd', 'target_date': '20261114',
         'research_as_of': '2026-11-14T09:00:00+08:00',
         'facts': [nan_fact], 'series_store': {}}
bD = cf.generate_claims_bundle(snapD)
typesD = {c['claim_type'] for c in bD['claims']}
ledD = [l for l in bD['coverage_ledger'] if 'source_value_nan' in l['reason']]
check('D1 nan 事实: 水平/变化断言零产出',
      'level' not in typesD and 'change' not in typesD, f'types={typesD}')
check('D2 nan 事实: 台账 source_value_nan×2(水平+变化)', len(ledD) == 2)
check('D3 lag 可算保留(采集失败日仍为观测日)', 'observation_lag' in typesD)
rD = cv.verify_bundle(bD, snapshot=snapD)
check('D4 nan 面 clean 零 CONTRADICTED(nan↔nan 证据同态)',
      rD['summary']['CONTRADICTED'] == 0, json.dumps(rD['summary']))
# D5: rank nan 成员剔除
factsR = []
for i, (mid, pct) in enumerate([('IDX_A', 2.0), ('IDX_B', float('nan')),
                                ('IDX_C', -1.0)]):
    factsR.append({'fact_id': f'{mid}@d', 'metric_id': mid, 'unit': 'index_pt',
                   'value': 100.0 + i, 'observation_date': '2026-11-13',
                   'as_of': '2026-11-14', 'value_type': 'close', 'source': 't',
                   'derived': {'week': {'basis_date': '2026-11-06',
                                        'basis_value': 100.0, 'pct_change': pct}}})
_reg_backup = cf.fe._REGISTRY_CACHE
cf.fe._REGISTRY_CACHE = {**(_reg_backup or {})}
cf.fe._REGISTRY_CACHE['by_id'] = dict(cf.fe._REGISTRY_CACHE.get('by_id') or {})
for f in factsR:
    cf.fe._REGISTRY_CACHE['by_id'][f['metric_id']] = {
        'metric_id': f['metric_id'], 'unit': 'index_pt',
        'asset_class': cf.RANK_ASSET_CLASS}
try:
    bR = cf.generate_claims_bundle({'snapshot_id': 'r', 'target_date': '20261114',
                                    'research_as_of': '2026-11-14', 'facts': factsR,
                                    'series_store': {}})
    import re as _re
    ranks = set()
    for c in bR['claims']:
        if c['claim_type'] == 'comparison' and c['subtype'] == 'rank':
            mid = _re.search(r'\(([A-Z_]+)=', c['derivation']['formula'])
            ranks.add((mid.group(1) if mid else None, c['value']))
    check('D5 排名族 nan 成员剔除(2 成员 A=1 C=2)',
          ranks == {('IDX_A', 1), ('IDX_C', 2)}, f'ranks={ranks}')
finally:
    cf.fe._REGISTRY_CACHE = _reg_backup


print('== E 派生视图阈值路由 ==')
thE = {'entries': [
    {'stable_key': 'test.scorecard.m1', 'metric_id': 'IDX_A', 'value': 1.0,
     'unit': 'percent', 'level': ['band_edge'], 'direction': 'below',
     'provenance': {'doc': 'x', 'quote': 'q'}},
    {'stable_key': 'test.plain_break', 'metric_id': 'IDX_A', 'value': 50.0,
     'unit': 'percent', 'level': ['headline'], 'direction': 'above',
     'provenance': {'doc': 'x', 'quote': 'q'}}], 'curated_at': 'test'}
snapE = {'snapshot_id': 'e', 'target_date': '20261114',
         'research_as_of': '2026-11-14', 'facts': factsR[:1], 'series_store': {}}
# registry 单位对齐 index_pt
cf.fe._REGISTRY_CACHE = {**(_reg_backup or {})}
cf.fe._REGISTRY_CACHE['by_id'] = dict(cf.fe._REGISTRY_CACHE.get('by_id') or {})
cf.fe._REGISTRY_CACHE['by_id']['IDX_A'] = {'metric_id': 'IDX_A',
                                           'unit': 'index_pt',
                                           'asset_class': cf.RANK_ASSET_CLASS}
try:
    try:
        cf.generate_claims_bundle(snapE, thresholds=thE)
        raised = False
    except cf.UnitAlgebraError as ue:
        raised = 'test.plain_break' in str(ue)
    check('E1 无结构标记真违约仍 fail-loud', raised)
    thE2 = {'entries': [thE['entries'][0]], 'curated_at': 'test'}
    bE = cf.generate_claims_bundle(snapE, thresholds=thE2)
    ledE = [l for l in bE['coverage_ledger']
            if l.get('stable_key') == 'test.scorecard.m1']
    check('E2 .scorecard. 率视图条目→台账分流(不炸不产)', len(ledE) == 1)
finally:
    cf.fe._REGISTRY_CACHE = _reg_backup


print('== F 纯度(新码静态扫描) ==')
src = open(os.path.join(ROOT, 'scripts', 'research_contract',
                        'claim_factory.py'), encoding='utf-8').read()
new_part = src[src.index('STATISTIC_PAIRS'):]
check('F1 statistic 新码零 os.environ/urllib/random',
      not re.search(r'environ|urllib|requests\b|random\.', new_part))
src_v = open(os.path.join(ROOT, 'scripts', 'research_contract',
                          'claim_verifier.py'), encoding='utf-8').read()
new_v = src_v[src_v.index('if ct == \'statistic\''):]
check('F2 verifier statistic 分支零环境/网络', not re.search(
    r'environ|urllib|requests\b|random\.', new_v))

print('=' * 70)
print(f'结果: {PASS}通过 / {FAIL}失败')
sys.exit(1 if FAIL else 0)
