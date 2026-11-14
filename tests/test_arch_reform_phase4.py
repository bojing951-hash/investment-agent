#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""阶段四: 判定档契约(Agent Native 统一判定验证)回归。

覆盖:
  V4 双向面 — R24 修订版判定档须 VERIFIED;审计前错误版须被拦截
      (含两真实 MAJOR: HY_OAS「处年内低位」实为95.6百分位;2s10s「倒挂」
      叙事 vs 面内2024-09-05后无负值)。
  类B — 统计结论独立复算(钉死公式),每族正/误双探针。
  六查 — 合成通过/失败逐项。
  两路一致 — 同一 L3 数值断言走 check_text 与 claim_verifier.verify_claim
      两路,verdict 必须一致(PHASE4 设计完成条件)。
  机构归因式豁免 — vp_sidecar 域引用的未绑数值不记 unbound。
  tc-v3-judgment 增量 — 复合代码指标/2026 年/L1S3S4/斜杠枚举/趋平/
      带符号水平歧义消解。

判定: 全 PASS 方绿;V4 双向任一失守=阶段四验收失败,禁合并。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

from research_contract import text_consistency as tc        # noqa: E402
from research_contract import claim_factory as cf           # noqa: E402
from research_contract import claim_verifier as cv          # noqa: E402
from research_contract import judgment_contract as jc       # noqa: E402

FIX = os.path.join(HERE, 'fixtures', 'v4')
FACE = json.load(open(os.path.join(FIX, 'evidence_face.json')))
JR = json.load(open(os.path.join(FIX, 'judgment_revised.json')))
JP = json.load(open(os.path.join(FIX, 'judgment_pre_audit.json')))
THR = cf.thresholds_by_metric(cf.load_thresholds())
RESULTS = []


def check(name, ok, detail=''):
    RESULTS.append((name, bool(ok), detail))
    print(f"  {'✅' if ok else '❌'} {name}" + (f"  [{detail}]"
                                                if detail and not ok else ''))


def has(chk_list, family, status, metric=None):
    for c in chk_list:
        if c.get('family') == family and c.get('status') == status and \
                (metric is None or c.get('metric') == metric or
                 c.get('metric_id') == metric):
            return c
    return None


def run_tc(text):
    return tc.check_text(text, snapshot=FACE, thresholds=THR)


# ── V4 双向面(冻结夹具;R24 E2E 真实报告) ─────────────────────────
print("== V4 双向面 ==")
res_r = jc.verify_judgment(JR, None, face=FACE)
res_p = jc.verify_judgment(JP, None, face=FACE)
check('V4-1 修订版 VERIFIED',
      res_r['verdict'] == 'VERIFIED',
      f"{res_r['verdict']} {res_r['stats']}")
check('V4-2 修订版零未绑零六查失败',
      res_r['stats']['unbound'] == 0 and res_r['stats']['six_fail'] == 0,
      str(res_r['stats']))
check('V4-3 审计前错误版 CONTRADICTED(整体降级)',
      res_p['verdict'] == 'CONTRADICTED', f"{res_p['verdict']}")
maj1 = has(res_p['verdicts'], 'stat_band_claim', 'CONTRADICTED', 'HY_OAS')
check('V4-4 MAJOR-V2-1 被拦: 「处年内低位」vs 百分位95.6',
      maj1 is not None and abs(maj1.get('expected') - 95.6) < 0.05,
      str(maj1))
check('V4-5 MAJOR-V2-2 被拦: 「倒挂」叙事方向',
      has(res_p['verdicts'], 'narrative_direction', 'CONTRADICTED')
      is not None,
      str([c for c in res_p['verdicts']
           if c['family'] == 'narrative_direction']))
maj1_r = has(res_r['verdicts'], 'stat_band_claim', 'VERIFIED', 'HY_OAS')
check('V4-6 修订版统计断言全 VERIFIED(样本n/百分位/月低点/区间/'
      '前值/无倒挂/最平端)',
      all(has(res_r['verdicts'], fam, 'VERIFIED') for fam in (
          'stat_sample_n', 'stat_percentile', 'stat_month_低',
          'stat_year_range', 'stat_prev_obs', 'stat_no_inversion',
          'stat_extreme_end', 'stat_widening_from_low')),
      str(sorted({c['family'] for c in res_r['verdicts']})))
check('V4-7 夹具完整性(55事实/4序列/21证据索引/17观点)',
      len(FACE['facts']) == 55 and
      {k: len(v['dates']) for k, v in FACE['series_store'].items()} ==
      {'CURVE_2S10S': 2498, 'HY_OAS': 784, 'SPX': 2513, 'VIX': 2515} and
      len(FACE['evidence_index']) == 21 and len(FACE['views']) == 17,
      f"facts={len(FACE['facts'])} eidx={len(FACE.get('evidence_index'))}"
      f" views={len(FACE.get('views') or [])}")

# ── 类B: 钉死公式独立复算(正/误双探针) ────────────────────────────
print("== 类B 统计复算(钉死口径 100×count(v<cur)/n) ==")
HY = '高收益债利差 HY_OAS 3.34pp,'
r = run_tc('')  # noqa: F841  (占位: 保证 tc 面/阈值装载)
b, _ = jc._class_b(HY + '2026 年内共 225 个观测。', FACE)
check('B1a n=225 VERIFIED',
      b and b[0]['status'] == 'VERIFIED' and b[0]['expected'] == 225,
      str(b))
b, _ = jc._class_b(HY + '2026 年内共 227 个观测。', FACE)
check('B1b n=227 超±1容差 CONTRA',
      b and b[0]['status'] == 'CONTRADICTED', str(b))
b, _ = jc._class_b(HY + '处于当年第 95.6 百分位。', FACE)
check('B2a 百分位95.6 VERIFIED',
      b and b[0]['status'] == 'VERIFIED' and
      abs(b[0]['expected'] - 95.6) < 0.05, str(b))
b, _ = jc._class_b(HY + '处于当年第 25.0 百分位。', FACE)
check('B2b 百分位25.0 CONTRA',
      b and b[0]['status'] == 'CONTRADICTED', str(b))
b, _ = jc._class_b(HY + '8 月低点 2.60@08-28。', FACE)
check('B3a 8月低点2.60 VERIFIED',
      b and b[0]['status'] == 'VERIFIED' and
      b[0]['family'] == 'stat_month_低', str(b))
b, _ = jc._class_b(HY + '8 月低点 2.70@08-28。', FACE)
check('B3b 低点2.70 CONTRA',
      b and b[0]['status'] == 'CONTRADICTED', str(b))
b, _ = jc._class_b(HY + '2026 年内区间 2.60–3.48。', FACE)
check('B5a 年内区间[2.60,3.48] VERIFIED',
      b and b[0]['status'] == 'VERIFIED', str(b))
b, _ = jc._class_b(HY + '2026 年内区间 2.60–3.40。', FACE)
check('B5b 区间上界3.40 CONTRA',
      b and b[0]['status'] == 'CONTRADICTED', str(b))
b, _ = jc._class_b('2s10s 曲线 CURVE_2S10S 0.25pp,2024-09-05 后无倒挂。',
                   FACE)
check('B6a 2024-09-05后无倒挂 VERIFIED',
      b and b[0]['status'] == 'VERIFIED' and
      b[0]['family'] == 'stat_no_inversion', str(b))
b, _ = jc._class_b('2s10s 曲线 CURVE_2S10S 0.25pp,2024-06-01 后无倒挂。',
                   FACE)
check('B6b 2024-06-01后仍有负值 CONTRA',
      b and b[0]['status'] == 'CONTRADICTED', str(b))
b, _ = jc._class_b('2s10s 曲线 CURVE_2S10S 0.25pp,自 0.32pp 趋平。', FACE)
check('B7a 前值0.32趋平 VERIFIED',
      b and b[0]['status'] == 'VERIFIED' and
      b[0]['family'] == 'stat_prev_obs', str(b))
b, _ = jc._class_b('2s10s 曲线 CURVE_2S10S 0.25pp,自 0.30pp 趋平。', FACE)
check('B7b 前值0.30 CONTRA',
      b and b[0]['status'] == 'CONTRADICTED', str(b))
b, _ = jc._class_b(HY + '处年内高位区。', FACE)
check('B8a 高位区@95.6 VERIFIED',
      b and b[0]['status'] == 'VERIFIED' and
      b[0]['family'] == 'stat_band_claim', str(b))
b, _ = jc._class_b(HY + '处年内低位。', FACE)
check('B8b 低位@95.6 CONTRA(MAJOR-V2-1 同构)',
      b and b[0]['status'] == 'CONTRADICTED', str(b))
b, _ = jc._class_b('2s10s 曲线 CURVE_2S10S 0.25pp,处年内最平端。', FACE)
check('B9a 最平端 frac≤1/3 VERIFIED',
      b and b[0]['status'] == 'VERIFIED' and
      b[0]['family'] == 'stat_extreme_end', str(b))
b, _ = jc._class_b('2s10s 曲线 CURVE_2S10S 0.25pp,处年内最陡端。', FACE)
check('B9b 最陡端 CONTRA',
      b and b[0]['status'] == 'CONTRADICTED', str(b))
b, _ = jc._class_b(HY + '自 8 月低点 2.60pp 走阔 +0.74pp。', FACE)
w10 = [c for c in b if c['family'] == 'stat_widening_from_low']
check('B10a 走阔算术 3.34−2.60=0.74 VERIFIED',
      w10 and w10[0]['status'] == 'VERIFIED', str(b))
b, _ = jc._class_b(HY + '自 8 月低点 2.60pp 走阔 +0.80pp。', FACE)
w10 = [c for c in b if c['family'] == 'stat_widening_from_low']
check('B10b 走阔0.80 CONTRA',
      w10 and w10[0]['status'] == 'CONTRADICTED', str(b))
b, _ = jc._class_b('高收益债利差 HY_OAS 3.34pp,处当年第 95.6 百分位;'
                   '自 8 月低点 2.60pp 走阔 +0.74pp。', FACE)
tgt = [c for c in b if c['family'] in ('stat_percentile',
                                       'stat_widening_from_low')]
check('B11 承前指标(分号切句主语在上句)',
      len(tgt) == 2 and all(c['metric_id'] == 'HY_OAS' for c in tgt)
      and all(c['status'] == 'VERIFIED' for c in tgt), str(b))

# ── 六查(合成通过/失败逐项) ─────────────────────────────────────
print("== 六查(合成面) ==")
MF = {
    'facts': [{'metric_id': 'HY_OAS', 'fact_id': 'HY_OAS@d', 'value': 3.34,
               'unit': 'percentage_point',
               'derived': {'week': {'pp_change': -0.08}}}],
    'series_store': {'HY_OAS': {'dates': ['2026-01-02'],
                                'values': [3.2]}},
    'views': [{'view_id': 'V1', 'view_label': 'SUPPORTING'},
              {'view_id': 'V2', 'view_label': 'INSUFFICIENT_EVIDENCE'}],
    'evidence_index': [
        {'ref': 'FACT-HY', 'kind': 'snapshot_fact', 'metric_id': 'HY_OAS'},
        {'ref': 'VP-V1', 'kind': 'vp_sidecar', 'ref_id': 'V1'},
        {'ref': 'VP-V2', 'kind': 'vp_sidecar', 'ref_id': 'V2'}],
    'research_as_of': '2026-11-13',
}


def six(judgment):
    return {s['check']: s for s in jc._six_checks(judgment, MF)}


def con(item=None, decl=None):
    base = {'id': 'CON-1', 'statement': 'HY_OAS 周再收 0.08pp。',
            'evidence_refs': ['FACT-HY'], 'competing_explanations':
            ['供给压缩解释', '需求韧性解释']}
    if item:
        base.update(item)
    j = {'l3': {'contradictions': [base]}, 'l4': {'scenarios': []}}
    if decl:
        j['agent_declaration'] = decl
    return j


s = six(con())
check('S1a relevant 引用可解析 VERIFIED',
      s['relevant']['status'] == 'VERIFIED', str(s.get('relevant')))
s = six(con(item={'evidence_refs': ['FACT-GHOST']}))
check('S1b 幽灵引用 NOT_VERIFIED',
      s['relevant']['status'] == 'NOT_VERIFIED', str(s.get('relevant')))
s = six(con(item={'evidence_refs': ['VP-V1']}))
check('S1c 零实据未声明纯逻辑档 NOT_VERIFIED',
      s['relevant']['status'] == 'NOT_VERIFIED', str(s.get('relevant')))
s = six(con(item={'evidence_refs': ['VP-V1']},
            decl={'attribution': 'logic_only'}))
check('S1d 纯逻辑档披露豁免 VERIFIED',
      s['relevant']['status'] == 'VERIFIED', str(s.get('relevant')))
s = six(con())
check('S2a supports 实据对得上 VERIFIED',
      s['supports']['status'] == 'VERIFIED', str(s.get('supports')))
s = six(con(item={'evidence_refs': ['VP-V2']},
            decl={'attribution': 'logic_only'}))
check('S2b INSUFFICIENT标签+非归因式 NOT_VERIFIED',
      s['supports']['status'] == 'NOT_VERIFIED', str(s.get('supports')))
s = six(con(item={'evidence_refs': ['VP-V2'],
                  'statement': 'HY_OAS 走阔系机构记述观点,归因引用。'},
            decl={'attribution': 'logic_only'}))
check('S2c INSUFFICIENT标签+归因式引用 VERIFIED',
      s['supports']['status'] == 'VERIFIED', str(s.get('supports')))
s = six(con())
check('S3a competing ≥2 VERIFIED',
      s['competing']['status'] == 'VERIFIED', str(s.get('competing')))
s = six(con(item={'competing_explanations': ['唯一解释']}))
check('S3b 单解释 NOT_VERIFIED',
      s['competing']['status'] == 'NOT_VERIFIED', str(s.get('competing')))
s = six(con(item={'competing_explanations': [
    'HY_OAS 走阔反映风险偏好恶化', '供需技术面解释']}))
check('S4a 现时方向相左(走阔 vs −0.08) NOT_VERIFIED',
      s['opposing']['status'] == 'NOT_VERIFIED', str(s.get('opposing')))
s = six(con(item={'competing_explanations': [
    '若风险偏好恶化,HY_OAS 将走阔', '供需技术面解释']}))
check('S4b 条件式跳过现时核 VERIFIED',
      s['opposing']['status'] == 'VERIFIED', str(s.get('opposing')))


def scen(rows):
    return {'l3': {'contradictions': []},
            'l4': {'scenarios': [{'id': 'SCN-A', 'rows': rows}]}}


good_rows = {
    'narrative': '假设供给冲击持续,若 HY_OAS 升破 3.5pp 则风险偏好恶化。',
    'asset_direction': {'confidence_tier': '纯逻辑推理', 'dir': 'risk-off'},
    'falsification': {'metric_id': 'HY_OAS', 'threshold':
                      '>25bp 自 3.34pp 升破 3.59pp'},
    'trigger': {'condition': '连续2日', 'deadline': '2026-12-31'}}
s = six(scen(good_rows))
check('S5a 纯逻辑档条件式框架 VERIFIED',
      s['overreach']['status'] == 'VERIFIED', str(s.get('overreach')))
bad_rows = dict(good_rows)
bad_rows['narrative'] = '假设成立时,HY_OAS 必将走阔。'
s = six(scen(bad_rows))
check('S5b 纯逻辑档必然性措辞 NOT_VERIFIED',
      s['overreach']['status'] == 'NOT_VERIFIED', str(s.get('overreach')))
s = six(scen({**good_rows, 'narrative': 'HY_OAS 走阔,风险偏好恶化。'}))
check('S5c 纯逻辑档缺条件式 NOT_VERIFIED',
      s['overreach']['status'] == 'NOT_VERIFIED', str(s.get('overreach')))
s = six(scen({**good_rows, 'falsification': None}))
check('S6a 证伪条件为空 NOT_VERIFIED',
      s['falsifiable']['status'] == 'NOT_VERIFIED',
      str(s.get('falsifiable')))
s = six(scen({**good_rows, 'falsification': {
    'metric_id': 'GHOST_X', 'threshold': '>25bp'}}))
check('S6b 证伪指标不在面 NOT_VERIFIED',
      s['falsifiable']['status'] == 'NOT_VERIFIED',
      str(s.get('falsifiable')))
s = six(scen({**good_rows, 'falsification': {
    'metric_id': 'HY_OAS', 'threshold': '大幅走阔'}}))
check('S6c 阈值无数字形态 NOT_VERIFIED',
      s['falsifiable']['status'] == 'NOT_VERIFIED',
      str(s.get('falsifiable')))
s = six(scen({**good_rows, 'falsification': {
    'metric_id': 'HY_OAS', 'threshold': '>40bp 自 3.34pp 升破 3.59pp'}}))
check('S6d 阈值算术断裂(3.59−3.34=25bp≠40bp) NOT_VERIFIED',
      s['falsifiable']['status'] == 'NOT_VERIFIED',
      str(s.get('falsifiable')))
s = six(scen(good_rows))
check('S6e 指标+数字阈值+算术自洽 VERIFIED',
      s['falsifiable']['status'] == 'VERIFIED', str(s.get('falsifiable')))

# ── 两路一致(同一断言,双通道 verdict 必须一致) ───────────────────
print("== 两路一致(check_text vs claim_verifier) ==")
hyf = next(f for f in FACE['facts'] if f['metric_id'] == 'HY_OAS')
wk = hyf['derived']['week']
spxf = next(f for f in FACE['facts'] if f['metric_id'] == 'SPX')


def fact_ref(f):
    return {'ref': f['fact_id'], 'kind': 'snapshot_fact',
            'value': f['value'], 'unit': f['unit'],
            'observation_date': f['observation_date']}


def basis_ref(f):
    w = f['derived']['week']
    return {'ref': f"{f['metric_id']}@{w['basis_date']}",
            'kind': 'series_ref', 'value': w['basis_value'],
            'unit': f['unit'], 'role': 'basis'}


def b_path(claim_type, subtype, metric, f, value):
    refs = [fact_ref(f)]
    if claim_type == 'change':
        refs.append(basis_ref(f))
    c = {'claim_id': 'P4X', 'claim_type': claim_type, 'subtype': subtype,
         'metric_id': metric, 'metric_ids': None, 'value': value,
         'unit': f['unit'], 'window': 'week',
         'observation_date': f['observation_date'],
         'as_of': FACE['research_as_of'],
         'evidence_refs': refs,
         'threshold_ref': None, 'attribution': 'deterministic',
         'derivation': {'basis': '两路一致实验', 'formula': 'pinned'}}
    return cv.verify_claim(c, snapshot=FACE, thresholds_by=THR, bundle={})


for label, text, path in (
        ('HY_OAS 水平 3.34 对', f"HY_OAS {hyf['value']}pp。",
         b_path('level', 'point', 'HY_OAS', hyf, hyf['value'])),
        ('HY_OAS 水平 3.10 误',
         f"HY_OAS {hyf['value'] - 0.24:.2f}pp。",
         b_path('level', 'point', 'HY_OAS', hyf,
                round(hyf['value'] - 0.24, 2))),
        ('HY_OAS 周变 −0.08 对',
         f"HY_OAS {hyf['value']}pp（周 {wk['pp_change']:+.2f}pp）。",
         b_path('change', 'absolute', 'HY_OAS', hyf, wk['pp_change'])),
        ('HY_OAS 周变 −0.20 误',
         f"HY_OAS {hyf['value']}pp（周 -0.20pp）。",
         b_path('change', 'absolute', 'HY_OAS', hyf, -0.20)),
        ('SPX 周变 +3.16% 对',
         f"SPX {spxf['value']}（周 +{spxf['derived']['week']['pct_change']}"
         f"%）。",
         b_path('change', 'relative', 'SPX', spxf,
                spxf['derived']['week']['pct_change'])),
        ('SPX 周变 +2.00% 误', f"SPX {spxf['value']}（周 +2.00%）。",
         b_path('change', 'relative', 'SPX', spxf, 2.00))):
    ra = run_tc(text)
    a_contra = ra['verdict'] == 'CONTRADICTED'
    b_contra = path['status'] == 'CONTRADICTED'
    want_contra = '误' in label
    check(f'TW[{label}] A={ra["verdict"]}/B={path["status"]} 一致',
          a_contra == b_contra == want_contra and
          (not want_contra or ra['verdict'] == 'CONTRADICTED') and
          (want_contra or (ra['verdict'] == 'VERIFIED' and
                           path['status'] == 'VERIFIED')),
          f"A={ra['verdict']} B={path['status']} "
          f"reasons={path['reasons'][:2]}")
# 边界披露(非判分): 「HY_OAS 3.3pp」=3.34 的 1dp 显示舍入位 — A 路
# 按文本显示精度契约(±0.05)VERIFIED;B 路 claim 携 4dp 全精度、
# tol=0(工厂口径)载 3.3 即 CONTRA。灰区=恰一个显示步;工厂 claim
# 全精度生成,不落入灰区——两契约在各自权威域内不冲突。
ra = run_tc(f"HY_OAS {hyf['value']:.1f}pp。")
pb = b_path('level', 'point', 'HY_OAS', hyf, float(f"{hyf['value']:.1f}"))
print(f"  ⚠ 边界披露: 1dp显示位 A={ra['verdict']} / B={pb['status']}"
      f"(显示精度 vs 全精度契约差,记录非判分)")

# ── 机构归因式豁免 ───────────────────────────────────────────────
print("== 机构归因式豁免 ==")
r = run_tc('MSIM 还认为 2027 年初或将降息至 3.90%。')
check('EX-1 机构引用未绑数值豁免(不计 unbound)',
      not r['unbound'] or all('MSIM' in u['ctx'] or '认为' in u['ctx']
                              or '预计' in u['ctx'] for u in r['unbound']),
      str(r['unbound']))

# ── tc-v3-judgment 增量回归 ──────────────────────────────────────
print("== tc-v3-judgment 增量 ==")
r = run_tc('名义 UST_10Y 4.88% 可分解为 REAL_10Y 2.68% 与 BEI_10Y 2.20%。')
check('TC-1 复合代码指标不漏数(恒等式分解 VERIFIED)',
      r['verdict'] == 'VERIFIED' and not r['unbound'],
      f"{r['verdict']} {r['unbound']}")
r = run_tc('SPX 2026 年初以来累计上涨 11.16%。')
check('TC-2 「2026 年」日期掩码不产生伪 token',
      not any(u['raw'].strip('+−-') in ('2026', '26') for u in r['unbound']),
      str(r['unbound']))
r = run_tc('证据分层 L1/S3/S4 均已归档,矛盾编号 CON-1。')
check('TC-3 L1/S3/S4 层级枚举掩码',
      not any(u['raw'].strip('+−-') in ('1', '3', '4') for u in r['unbound']),
      str(r['unbound']))
r = run_tc('SPX 7609.63/+3.16%/VIX 17.74。')
check('TC-4 斜杠枚举 SPX/VIX 双绑定',
      r['verdict'] == 'VERIFIED' and not r['unbound'],
      f"{r['verdict']} {[(c['family'], c['status']) for c in r['checks']]} "
      f"{r['unbound']}")
r = run_tc('2s10s +0.25pp 回正,处于年内最平端。')
lv = [c for c in r['checks'] if c['family'] == 'level']
check('TC-5 带符号水平歧义消解(+0.25 绑水平而非周变)',
      any(c['status'] == 'VERIFIED' and
          abs((c.get('value') or 0) - 0.25) < 1e-9 for c in lv) and
      not any(c['family'] == 'change' and
              c['status'] == 'CONTRADICTED' for c in r['checks']),
      str([(c['family'], c.get('value'), c['status']) for c in r['checks']]))

n_pass = sum(1 for _, ok, _ in RESULTS if ok)
print(f"\nPHASE4 判定: {n_pass} PASS / {len(RESULTS) - n_pass} FAIL")
sys.exit(0 if n_pass == len(RESULTS) else 1)
