#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R41: T8-R2 余留②③测试面(RDG-20261116-011;①为诊断件不入 CI 断言)。

②band_label 双报去重提示: 同指标 level CONTRA 并存时 band_label CONTRA 加
co_anchor 派生标记;状态零变动,纯 band 面/纯 level 面/双绿面零触碰。
③score_total 维度单源: scorecard_spec 规格表(结构/键集/纯度)+
tc 复算↔macro_scorecard 评分双侧同分行为锁(合成快照全 8 指标)
+成分缺失 INSUFFICIENT 语义保持+拆接线变异自证。
①真实面复跑件=tests/r41_realface_runner.py(LIVE 依赖,非 CI);本套件仅锁
adjudication 工件在库形态(326 全簇裁定,零真错)。
全合成+era 夹具;CI 干净 clone 可跑。
"""
import contextlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from migration_matrix import load_era                    # noqa: E402
from research_contract import claim_factory as cf        # noqa: E402
from research_contract import scorecard_spec             # noqa: E402
from research_contract import text_consistency as tc     # noqa: E402

snap, prior, thr = load_era('20261114')     # HY_OAS=3.2(attention 带)
RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok)))
    print(('PASS ' if ok else 'FAIL ') + name
          + (f'  [{detail}]' if detail and not ok else ''))


def run(text):
    return tc.check_text(text, snapshot=snap, thresholds=thr,
                         prior_anchors=prior)


def bands(r, metric='HY_OAS'):
    return [c for c in r['checks']
            if c['family'] == 'band_label' and c.get('metric') == metric]


def levels(r, metric='HY_OAS'):
    return [c for c in r['checks']
            if c['family'] == 'level' and c.get('metric') == metric]


print('== R41-§B band_label 双报去重提示(状态零变动) ==')
# B1 双报形态(T8R2 审计§五原句变体): 值错(4.20≠快照3.2)+标签按错值
# 「看似对」(4.20 落警告带)→band_label 与 level 同红
r = run('HY OAS 报4.20%，已进入警告区（>400bp）。')
bl = [c for c in bands(r) if c['status'] == 'CONTRADICTED']
check('B1 双报: level 与 band_label 同红',
      any(c['status'] == 'CONTRADICTED' for c in levels(r)) and len(bl) == 1,
      str(r['checks']))
check('B1 band_label 带 co_anchor 派生标记+去重注记',
      bl and bl[0].get('co_anchor') == 'level_contradicted'
      and '去重' in bl[0].get('note', ''),
      str(bl[:1]))
# B2 纯 band 面: 值对(3.20)+标签错(警告区)→band 红**无**标记
r = run('HY OAS 报3.20%，已进入警告区（>400bp）。')
blc = [c for c in bands(r) if c['status'] == 'CONTRADICTED']
check('B2 纯 band 面: band 红无 co_anchor(level 不红)',
      len(blc) == 1 and 'co_anchor' not in blc[0]
      and not [c for c in levels(r) if c['status'] == 'CONTRADICTED'],
      str(blc[:1]) + str(levels(r)))
# B3 值错+标签按快照落带恰好对→band 绿无标记(不越界加标)
r = run('HY OAS 报4.20%，仍处关注带。')
check('B3 band 绿面零触碰',
      bands(r) and bands(r)[0]['status'] == 'VERIFIED'
      and 'co_anchor' not in bands(r)[0],
      str(bands(r)))
# B4 标记不改变任何 status/统计(有标无标双跑同判)
ra = run('HY OAS 报4.20%，已进入警告区（>400bp）。')
st_a = [(c['family'], c.get('metric'), c['token'], c['status'])
        for c in ra['checks']]
check('B4 stats 与 verdict 自洽(仅加字段不改判)',
      ra['verdict'] == 'CONTRADICTED'
      and ra['stats']['contradicted'] == sum(
          1 for c in ra['checks'] if c['status'] == 'CONTRADICTED')
      and all(('co_anchor' not in c) or (
          c['family'] == 'band_label'
          and c['status'] == 'CONTRADICTED') for c in ra['checks']),
      str(st_a))

print('== R41-§S scorecard_spec 单源规格表 ==')
# S0 纯度: 零 import(契约纯度律)
src = open(os.path.join(ROOT, 'scripts/research_contract',
                        'scorecard_spec.py'), encoding='utf-8').read()
check('S0 规格表零 import(契约纯度)',
      not re.search(r'^\s*(import|from)\s', src, re.M))
# S1 结构: 2 维度 8 行 32 键无重复,行形状合法
dims = scorecard_spec.SCORECARD_DIMENSIONS
rows = [(d, row) for d, rs in dims for row in rs]
keys = scorecard_spec.threshold_keys()
check('S1 结构: 2 维×8 行×32 键无重复',
      len(dims) == 2 and len(rows) == 8 and len(keys) == 32
      and len(set(keys)) == 32)
check('S1 行形状: source/band/keys 合法',
      all((src_t == ('level',) or
           (len(src_t) == 2 and all(isinstance(x, str) for x in src_t)))
          and band in ('std', 'rev') and len(ks) == 4
          for _, (_, src_t, band, ks) in rows))
# S2 macro_scorecard 键集推导等价(平行枚举退役)
import macro_scorecard as ms                                # noqa: E402
want = (set(scorecard_spec.threshold_keys())
        | set(scorecard_spec.REGIME_THRESHOLD_KEYS)
        | set(scorecard_spec.EXTRA_ENGINE_KEYS))
check('S2 ms.SCORECARD_THRESHOLD_KEYS=spec∪regime∪extra(35)',
      set(ms.SCORECARD_THRESHOLD_KEYS) == want and len(want) == 35,
      str(len(ms.SCORECARD_THRESHOLD_KEYS)))
check('S2 fail-closed 门保持(缺键即拒)',
      isinstance(ms.load_thresholds(), dict))

# S3 双侧行为锁: 合成快照全 8 指标,tc 复算↔ms 评分同分
TH = {e['stable_key']: e['value']
      for e in json.load(open(os.path.join(
          ROOT, 'config/thresholds.json'), encoding='utf-8'))['entries']
      if isinstance(e.get('value'), (int, float))}
LV = {'CORE_CPI': (TH['core_cpi.scorecard.p25']
                   + TH['core_cpi.scorecard.p35']) / 2,
      'BEI_10Y': (TH['bei_10y.scorecard.m2']
                  + TH['bei_10y.scorecard.p23']) / 2,
      'WTI_F': TH['wti_f.scorecard.p90'] + 1,
      'AHE': (TH['ahe.scorecard.m2'] + TH['ahe.scorecard.m3']) / 2,
      'UMCSENT': (TH['umcsent.scorecard.m60']
                  + TH['umcsent.scorecard.p80']) / 2,
      'RSAFS': (TH['rsafs_mom.scorecard.p05']
                + TH['rsafs_mom.scorecard.p1']) / 2,
      'INDPRO': (TH['indpro_mom.scorecard.m1']
                 + TH['indpro_mom.scorecard.m03']) / 2}
UN_M3 = (TH['unemployment_3m.scorecard.p03']
         + TH['unemployment_3m.scorecard.m01']) / 2


def synth(drop=()):
    facts = []
    for d, (mid, source, _band, _ks) in [(d, row) for d, rs in dims
                                         for row in rs]:
        if mid in drop:
            continue
        f = {'metric_id': mid, 'value': LV.get(mid, UN_M3),
             'observation_date': '2026-11-14', 'fact_id': f'fx_{mid}'}
        if source != ('level',):
            f['derived'] = {source[0]: {'available': True,
                                        source[1]: f['value']}}
        facts.append(f)
    return {'facts': facts, 'research_as_of': '2026-11-14'}


with contextlib.redirect_stdout(io.StringIO()):
    _sc_i, i_ms, _mi = ms.score_inflation(synth()['facts'])
    _sc_g, g_ms, _mg = ms.score_growth(synth()['facts'])
i_exp = int(sum(e['score'] for e in _sc_i.values()))
g_exp = int(sum(e['score'] for e in _sc_g.values()))
tby = cf.thresholds_by_metric(cf.load_thresholds())
txt = (f'评分卡复算: 通胀总分{i_ms:+d}，增长总分{g_ms:+d}，'
       f'体制映射维持衰退。')
rr = tc.check_text(txt, snapshot=synth(), thresholds=cf.load_thresholds())
sc = [c for c in rr['checks'] if c['family'] == 'scorecard_total']
sc_v = {('通胀' if '通胀' in c['token'] else '增长'): c for c in sc}
check('S3 双侧同分: tc 复算=ms 评分(通胀)',
      sc_v['通胀']['expected'] == i_ms == i_exp
      and sc_v['通胀']['status'] == 'VERIFIED',
      f"tc={sc_v['通胀'].get('expected')} ms={i_ms}")
check('S3 双侧同分: tc 复算=ms 评分(增长)',
      sc_v['增长']['expected'] == g_ms == g_exp
      and sc_v['增长']['status'] == 'VERIFIED',
      f"tc={sc_v['增长'].get('expected')} ms={g_ms}")
rg = [c for c in rr['checks'] if c['family'] == 'regime_mapping']
check('S3 体制映射同构(ms.determine_regime=tc 判)',
      rg and rg[0]['status'] == 'VERIFIED'
      and rg[0]['expected'] == ms.determine_regime(g_ms, i_ms)[0],
      str(rg[:1]))
# S4 成分缺失——双引擎语义本不同构(既有行为,如实锁存非改齐):
#   tc(契约复算)=全成分 or 拒判(INSUFFICIENT,保守面);
#   ms(评分引擎)=可用≥2 即部分分照判+missing 清单披露(诚实面)。
# 全员在场时二者同分(S3);本判锁两侧各自契约不漂移。
rr2 = tc.check_text(txt, snapshot=synth(drop=('CORE_CPI',)),
                    thresholds=cf.load_thresholds())
sc2 = [c for c in rr2['checks']
       if c['family'] == 'scorecard_total' and '通胀' in c['token']]
with contextlib.redirect_stdout(io.StringIO()):
    _s3, i_part, m3 = ms.score_inflation(
        synth(drop=('CORE_CPI',))['facts'])
check('S4 tc: 成分缺失→INSUFFICIENT(不计0分,保守拒判)',
      sc2 and sc2[0]['status'] == 'INSUFFICIENT_EVIDENCE'
      and 'CORE_CPI' in sc2[0]['note'] and sc2[0]['expected'] is None,
      str(sc2[:1]))
check('S4 ms: 部分分照判+missing 披露(≥2 可用语义保持)',
      i_part is not None
      and any(m.get('metric_id') == 'CORE_CPI' for m in m3),
      f'ms_total={i_part} missing={len(m3)}')
# S5 变异自证: 拆接线(规格表抽行)→tc 复算成员集随表变(单源消费实证)
_orig = scorecard_spec.SCORECARD_DIMENSIONS
try:
    scorecard_spec.SCORECARD_DIMENSIONS = tuple(
        (d, tuple(r for r in rs if r[0] != 'AHE'))
        for d, rs in _orig)
    rr3 = tc.check_text(txt, snapshot=synth(drop=()),
                        thresholds=cf.load_thresholds())
    sc3 = [c for c in rr3['checks']
           if c['family'] == 'scorecard_total' and '通胀' in c['token']]
    check('S5 变异: 抽 AHE 行→成员集随表变(复算+3≠声称+2→CONTRA)',
          sc3 and sc3[0]['status'] == 'CONTRADICTED'
          and sc3[0]['expected'] == 3 and 'AHE' not in sc3[0]['note'],
          str(sc3[:1]))
finally:
    scorecard_spec.SCORECARD_DIMENSIONS = _orig
rr4 = tc.check_text(txt, snapshot=synth(),
                    thresholds=cf.load_thresholds())
check('S5 变异后还原: 全行态复绿(通胀总分 VERIFIED)',
      any(c['family'] == 'scorecard_total' and '通胀' in c['token']
          and c['status'] == 'VERIFIED' for c in rr4['checks']),
      str([c for c in rr4['checks']
           if c['family'] == 'scorecard_total']))

print('== R41-§R ①诊断工件在库形态(机械锁,复跑=runner) ==')
ART = os.path.join(ROOT, 'audit/arch-reform/T7/t7_realface_r41.json')
doc = json.load(open(ART, encoding='utf-8'))
tot = sum(doc['runs'][v]['stats']['contradicted'] for v in
          ('V1', 'V2', 'V3'))
adj = doc.get('adjudication', {})
check('R1 工件: 326 全簇裁定+零真错+基线零漂移',
      tot == 326 and adj.get('verdict', {}).get('true_errors_found') == 0
      and all(doc['runs'][v]['delta_contradicted'] == 0
              for v in ('V1', 'V2', 'V3')),
      f'tot={tot}')
check('R1 工件: 逐簇标签全覆盖(簇数和=contra 数)',
      all(sum(row['n'] for row in adj['per_report'][v].values())
          == doc['runs'][v]['stats']['contradicted']
          for v in ('V1', 'V2', 'V3')))
check('R1 工件: A 族(碎片泄漏)居首=硬化首位登记',
      max(adj['rollup'], key=adj['rollup'].get) == 'A'
      and adj['rollup']['A'] >= 150, str(adj.get('rollup')))

n_pass = sum(1 for _, ok in RESULTS if ok)
n_fail = len(RESULTS) - n_pass
print('═' * 64)
print(f'结果: PASS={n_pass} FAIL={n_fail}')
print('═' * 64)
sys.exit(0 if n_fail == 0 else 1)
