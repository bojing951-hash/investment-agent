#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P0-3 单位感知统计回归套件(批2 WI5,2026-11-09)。

覆盖(全部合成数据;预期值一律**独立手算/测试内独立公式**,禁止用被测模块自算):
① 利率 4.00→5.00 必出 +1.00pp,绝不出现 25% 口径(利率×价格混算缺陷核心);
② 价格对 pct 口径;
③ 利率×价格混合 → change_basis 各自 pp/pct,pearson 在单位感知变化序列上;
④ count 族标注(basis=pct + family=count + ia_cli 侧近似警示);
⑤ other 族 → incomparable_units 结构化拒绝 rc=1(与无序列拒绝同语义);
⑥ None/零基丢弃计数 + 双侧联合零基过滤(修复两侧独立过滤的错位配对);
⑦ mixed_frequency / date_gap / sample_insufficient 三警告;
⑧ 对齐块 off-by-one: n_common_observations=len(common)(原为 len(common)-1),
   水平窗/变化窗字段并存;
⑨ compute_all 12 对回归(全价格族,合成快照,无一缺口)。
"""
import contextlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

import ia_cli                    # noqa: E402
import correlation_calculator as cc  # noqa: E402
import workbench_data as wd      # noqa: E402

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


def ref_pearson(xs, ys):
    """测试内独立参考实现(与被测 cc.pearson 分开写,防同源自证)。"""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    return cov / (vx ** 0.5 * vy ** 0.5)


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    code = None
    real_argv = sys.argv
    sys.argv = ['ia_cli.py', *argv]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                ia_cli.main()
            except SystemExit as e:
                code = e.code
    finally:
        sys.argv = real_argv
    return code, out.getvalue(), err.getvalue()


def synth_snapshot(series_map, **extra):
    snap = {'snapshot_id': 'research_snapshot_20990131',
            'target_date': '2099-01-31', 'research_as_of': '2099-01-31T18:00:00+08:00',
            'gate_a': {'status': 'PASS', 'core_missing': [], 'noncore_missing': [],
                       'noncore_missing_detail': {}, 'noncore_degraded': []},
            'sources_status': {}, 'facts': [], 'series_store': dict(series_map)}
    snap.update(extra)
    return snap


def with_context(snap, reg):
    ia_cli.load_context = lambda: (snap, reg, '')


REAL_REG = wd.load_registry(ROOT)

print("═" * 60)
print("① 利率 pp 口径 / ② 价格 pct 口径(unit_change 单元)")
print("═" * 60)
check("rate 4.00→5.00 = +1.00pp",
      cc.unit_change(4.00, 5.00, 'rate') == 1.00,
      str(cc.unit_change(4.00, 5.00, 'rate')))
check("rate 口径绝不出现 25%(旧缺陷口径)",
      cc.unit_change(4.00, 5.00, 'rate') != 25.0)
check("price 100→110 = +10.0 pct",
      abs(cc.unit_change(100.0, 110.0, 'price') - 10.0) < 1e-12)
check("count 200→210 = +5.0 pct(近似)",
      abs(cc.unit_change(200.0, 210.0, 'count') - 5.0) < 1e-12)
check("other → None(不可比)",
      cc.unit_change(1.0, 2.0, 'other') is None)
check("None 输入 → None", cc.unit_change(None, 2.0, 'rate') is None)

print("═" * 60)
print("③ 利率×价格混合: paired_unit_changes 基础口径")
print("═" * 60)
dates = ['2099-01-01', '2099-01-02', '2099-01-03', '2099-01-04', '2099-01-05']
ust = [4.00, 4.20, 4.50, 4.80, 5.00]           # pp 变化: +0.20 +0.30 +0.30 +0.20
spx = [100.0, 101.0, 99.0, 102.0, 104.0]        # pct 变化: +1.0 -1.9802 +3.0303 +1.9608
res, common = cc.paired_unit_changes(
    {'dates': dates, 'values': ust}, 'rate',
    {'dates': dates, 'values': spx}, 'price')
exp_a = [0.20, 0.30, 0.30, 0.20]
exp_b = [(spx[i] / spx[i - 1] - 1) * 100 for i in range(1, 5)]
check("basis_a=pp basis_b=pct",
      res['basis_a'] == 'pp' and res['basis_b'] == 'pct')
check("变化序列=手算 pp 序列", all(abs(a - e) < 1e-12 for a, e in zip(res['changes_a'], exp_a)),
      str(res['changes_a']))
check("变化序列=手算 pct 序列", all(abs(b - e) < 1e-9 for b, e in zip(res['changes_b'], exp_b)))
check("pearson(独立参考)与被测一致",
      abs(cc.pearson(res['changes_a'], res['changes_b'])
          - ref_pearson(exp_a, exp_b)) < 1e-12)
check("共同观测<3 → (None, common)",
      cc.paired_unit_changes({'dates': ['2099-01-01'], 'values': [1.0]}, 'price',
                             {'dates': ['2099-01-01'], 'values': [1.0]}, 'price')[0] is None)

print("═" * 60)
print("⑥ None/零基丢弃 + 双侧联合零基过滤")
print("═" * 60)
# A 在第3观测为 None;A 前值 0 出现在第2→第3步(被 None 先行拦截另计);
# B 正常——旧代码 A 侧独立跳过会造成 ra/rb 错位,新代码该对两侧同弃。
da = [1.0, 2.0, None, 4.0, 5.0, 6.0]
db = [10.0, 20.0, 30.0, 40.0, 0.0, 60.0]   # B 前值0 出现在第5→第6步(联合丢弃)
dts = [f'2099-02-0{i}' for i in range(1, 7)]
res2, _ = cc.paired_unit_changes(
    {'dates': dts, 'values': da}, 'price', {'dates': dts, 'values': db}, 'price')
# 手算: 步1(1→2,10→20)✓ 步2(2→None)drop_null 步3(None→4)drop_null
#      步4(4→5,40→0)✓(前值非0;到达值0不拦) 步5(5→6,0→60)前值B=0→zero_base
check("dropped_null=2(None 观测对)", res2['dropped_null'] == 2, str(res2['dropped_null']))
check("zero_base_dropped=1(双侧联合)", res2['zero_base_dropped'] == 1,
      str(res2['zero_base_dropped']))
check("两侧变化序列等长(修复错位配对)",
      len(res2['changes_a']) == len(res2['changes_b']) == 2)
exp_a2 = [(2.0 / 1.0 - 1) * 100, (5.0 / 4.0 - 1) * 100]
exp_b2 = [(20.0 / 10.0 - 1) * 100, (0.0 / 40.0 - 1) * 100]
check("联合过滤后变化值=手算", all(abs(a - e) < 1e-9 for a, e in zip(res2['changes_a'], exp_a2))
      and all(abs(b - e) < 1e-9 for b, e in zip(res2['changes_b'], exp_b2)))
# 旧 paired_returns 同纪律(双侧联合+None 跳过)
pr_pair, _dates = cc.paired_returns({'dates': dts, 'values': da},
                                    {'dates': dts, 'values': db})
check("paired_returns 同获等长序列(联合过滤)",
      len(pr_pair[0]) == len(pr_pair[1]) == 2)
try:
    cc.paired_unit_changes({'dates': dts, 'values': da}, 'other',
                           {'dates': dts, 'values': db}, 'price')
    check("other 族进 paired_unit_changes → ValueError fail-loud", False)
except ValueError:
    check("other 族进 paired_unit_changes → ValueError fail-loud", True)

print("═" * 60)
print("⑤ other → incomparable_units rc=1 / ④ count 标注(ia_cli compare)")
print("═" * 60)
reg = {'metrics': [], 'by_id': dict(REAL_REG['by_id'])}
reg['by_id']['ZZTEST_OTHER'] = {'metric_id': 'ZZTEST_OTHER', 'display_name': '异单位测试',
                                'unit': 'weird_unit_xyz', 'frequency': 'daily',
                                'identity': {}, 'calc': None}
ser_map = {'UST_10Y': {'dates': dates, 'values': ust},
           'SPX': {'dates': dates, 'values': spx},
           'ZZTEST_OTHER': {'dates': dates, 'values': [1.0, 2.0, 3.0, 4.0, 5.0]},
           'NFP': {'dates': dates, 'values': [1000.0, 1010.0, 1020.0, 1030.0, 1040.0]}}
with_context(synth_snapshot(ser_map), reg)
_real_load_registry = wd.load_registry
wd.load_registry = lambda root=None: reg   # fixture 注入: 真实注册表+虚构异单位指标
try:
    code, out, _ = run_cli('compare', '--metrics', 'ZZTEST_OTHER,SPX')
finally:
    wd.load_registry = _real_load_registry
d = json.loads(out)
check("other → rc=1 + error.kind=incomparable_units",
      code == 1 and d['ok'] is False and d['error']['kind'] == 'incomparable_units',
      f"rc={code} err={d.get('error')}")
check("hint 披露单位族", 'other' in json.dumps(d['error'], ensure_ascii=False))
code, out, _ = run_cli('compare', '--metrics', 'UST_10Y,SPX')
d = json.loads(out)
data = d['data']
check("混合对 rc=0 + change_basis={a:pp,b:pct}",
      code == 0 and d['ok'] and data['change_basis'] == {'a': 'pp', 'b': 'pct'})
check("pearson=单位感知变化上的独立参考值",
      abs(data['pearson_returns'] - ref_pearson(exp_a, exp_b)) < 1e-9,
      str(data['pearson_returns']))

print("═" * 60)
print("⑧ off-by-one 对齐块 / ⑦ 三警告")
print("═" * 60)
check("n_common_observations=len(common)=5(修复原 len(common)-1)",
      data['alignment']['n_common_observations'] == 5)
check("n_level_observations=5 与 n_change_pairs=4 并存",
      data['alignment']['n_level_observations'] == 5
      and data['alignment']['n_change_pairs'] == 4)
check("数据层 n_change_pairs=实际参与对数",
      data['n_change_pairs'] == 4 and data['dropped_null'] == 0
      and data['zero_base_dropped'] == 0)
warns = json.dumps(d.get('warnings') or [], ensure_ascii=False)
check("sample_insufficient(<30) 警示在场", '样本不足' in warns and '<30' in warns)
check("sample_note 随行", data.get('sample_note') and '30' in data['sample_note'])

# mixed_frequency + date_gap: NFP(真实注册表 count 族,monthly)vs SPX(daily)
# + 共同观测中间断 13 天(03-02→03-15)
# 批2 W9 语义更新: 日×月对走 month_grid 聚合(单月样本→变化对不足,13 天日间隔
# 不再是断点口径);date_gap>7 改由日×日对(阈值不归一)承担本断言。
gap_dates = ['2099-03-01', '2099-03-02', '2099-03-15', '2099-03-16', '2099-03-17']
with_context(synth_snapshot({
    'SPX': {'dates': gap_dates, 'values': spx},
    'NFP': {'dates': gap_dates, 'values': [1000.0, 1010.0, 1020.0, 1030.0, 1040.0]},
    'UST_10Y': {'dates': gap_dates, 'values': ust}}), REAL_REG)
code, out, _ = run_cli('compare', '--metrics', 'SPX,NFP')
d2 = json.loads(out)
w2 = json.dumps(d2.get('warnings') or [], ensure_ascii=False)
check("mixed_frequency 警示(daily vs monthly)", 'mixed_frequency' in w2)
check("count 族 pct 近似警示", 'count' in w2 and '近似' in w2)
check("W9: 日×月默认 month_grid 聚合(高频侧披露)",
      d2['data']['alignment']['mode'] == 'month_grid'
      and any('month_grid' in (s.get('aggregation') or '')
              for s in d2['data']['sides']))
check("count 侧 change_basis=pct",
      d2['data']['change_basis']['b'] == 'pct')
# date_gap: 日×日(UST_10Y daily)阈值仍 7 天,13 天断点照报(频率归一只在月频参与时)
code, out, _ = run_cli('compare', '--metrics', 'SPX,UST_10Y')
w3 = json.dumps(json.loads(out).get('warnings') or [], ensure_ascii=False)
check("date_gap 警示(日×日最大间隔13天>7,阈值归一不影响同频对)",
      'date_gap' in w3 and '13' in w3 and '>7' in w3)

print("═" * 60)
print("⑨ compute_all 12 对回归(合成快照,全价格族)")
print("═" * 60)
ids = sorted({p['a'] for p in cc.PAIRS} | {p['b'] for p in cc.PAIRS})
d10 = [f'2099-04-{i:02d}' for i in range(1, 11)]
store = {}
for k, mid in enumerate(ids):
    store[mid] = {'dates': d10,
                  'values': [100.0 + k + (i * (1 if k % 2 == 0 else -1))
                             for i in range(10)]}
results, missing = cc.compute_all(synth_snapshot(store))
check("12 对全产出零缺口", len(results) == 12 and missing == [],
      f"{len(results)}对 missing={missing[:2]}")
first = results[0]
exp_ra = [(store[first['a']]['values'][i] / store[first['a']]['values'][i - 1] - 1)
          for i in range(1, 10)]
exp_rb = [(store[first['b']]['values'][i] / store[first['b']]['values'][i - 1] - 1)
          for i in range(1, 10)]
check("首对 corr_60d=独立参考值(价格 pct 口径不变)",
      first['corr_60d'] is not None
      and abs(first['corr_60d'] - ref_pearson(exp_ra, exp_rb)) < 1e-9)
check("窗口披露字段在场(变化窗=首变化日,不含基期观测)",
      first['window_first'] == d10[1] and first['window_last'] == d10[-1],
      f"{first['window_first']}~{first['window_last']}")

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
