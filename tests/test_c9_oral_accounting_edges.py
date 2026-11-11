#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter9 P0-4 口径边界测试(C席复现×D席审计交叉确认项的回归锁)。

锁定面(C9_D_AUDIT_AND_DESIGN §4.2 边界清单+C席附加发现):
① 历史走势图窗切片=日历日期截取(旧缺陷: 固定观测数 252/126/63/21,
   月频序列"1年"实显 21 年——C席 CONFIRMED);
② horizon_start 6m(新增)/闰年 2-29/跨年窗口;
③ interval_change 价格类负基数拒算(语义反转护)/零基数/利率负水平 pp 安全;
④ 市场多窗口表纳入利率族 rates_yield/policy_rate/curve_slope
   (C席附加发现: 旧集合过滤→UST/BUND/JGB/2s10s 零显示,页①答不了美债 3m);
⑤ 序列首末 caption 族感知(利率 pp/价格 pct/计数绝对差——C席 CONFIRMED 旧版
   一律水平百分变化,失业率 4.7→4.1 显示 -12.77%);
⑥ 月频单月缺测不插值(common window 如实)。
全合成 fixture,零真实 data/ 依赖(CI 干净 clone 可跑)。
"""
import datetime as dt
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


import workbench_data as wd                     # noqa: E402
import research_history_query as rhq            # noqa: E402
import fact_engine as fe                        # noqa: E402

RATE_U = next(iter(sorted(fe.RATE_UNITS)))
PRICE_U = next(iter(sorted(fe.PRICE_LIKE_UNITS)))
COUNT_U = next(iter(sorted(fe.COUNT_UNITS)))

print("═" * 60)
print("[1] 图窗日历截取: 月频'1年'≠21 年(C席 CONFIRMED 缺陷回归锁)")
print("═" * 60)
m_dates = [(dt.date(2005, 1, 1) + dt.timedelta(days=30 * i)).isoformat()
           for i in range(0, 265)]               # 月频≈22 年(SPX_CAPE 形)
m_dates = sorted(set(m_dates))
m_vals = [100.0 + i for i in range(len(m_dates))]
d_out, v_out, note = wd.slice_series_window(m_dates, m_vals, '1年',
                                           end_date=m_dates[-1])
span_days = (dt.date.fromisoformat(d_out[0])
             - dt.date.fromisoformat(d_out[-1])).days
check(f"月频'1年'窗内观测数≈12-14(实测{len(d_out)}),非 252",
      10 <= len(d_out) <= 16, f"n={len(d_out)}")
check("月频'1年'窗口跨度≤400 天(非 21 年)", abs(span_days) <= 400,
      f"span={span_days}天")
d_out5, _, _ = wd.slice_series_window(m_dates, m_vals, '5年',
                                      end_date=m_dates[-1])
check(f"月频'5年'窗内观测数≈60-66(实测{len(d_out5)})", 55 <= len(d_out5) <= 70,
      f"n={len(d_out5)}")
dd = [(dt.date(2025, 11, 1) + dt.timedelta(days=i)).isoformat()
      for i in range(0, 400)]                    # 日频
dv = [float(i) for i in range(len(dd))]
d_outd, _, _ = wd.slice_series_window(dd, dv, '1年', end_date=dd[-1])
check(f"日频'1年'窗内≈365 观测(实测{len(d_outd)})", 350 <= len(d_outd) <= 380,
      f"n={len(d_outd)}")
a_all, _, n_all = wd.slice_series_window(m_dates, m_vals, '全部')
check("'全部'原样返回", len(a_all) == len(m_dates) and '全部观测' in n_all)
d_outz, v_outz, notez = wd.slice_series_window(
    ['2019-01-01', '2019-02-01'], [1.0, 2.0], '1个月', end_date='2020-02-01')
check("窗口内无观测→空+如实说明", not d_outz and '无观测' in notez, notez)

print("═" * 60)
print("[2] horizon_start: 6m 新增/闰年 2-29/跨年")
print("═" * 60)
check("6m 自然月回退(20261111→2026-05-11)",
      wd.horizon_start('20261111', '6m') == '2026-05-11')
check("闰年 2-29 −1y → 2023-02-28(钳制)",
      wd.horizon_start('20240229', '1y') == '2023-02-28')
check("跨年窗口(20270115 −1y → 2026-01-15)",
      wd.horizon_start('20270115', '1y') == '2026-01-15')
check("月末钳制(2026-03-31 −1m → 2026-02-28)",
      wd.horizon_start('20260331', '1m') == '2026-02-28')

print("═" * 60)
print("[3] interval_change 边界: 负基数/零基数/利率负水平")
print("═" * 60)
neg = rhq.interval_change(['2026-01-01', '2026-06-01'], [-100.0, -90.0],
                          PRICE_U, start='2026-03-01', end='2026-06-01')
check("价格类负基准→拒算+原因(语义反转护,不回退)",
      neg.get('available') is False and '负' in neg.get('reason', ''),
      str(neg))
zero = rhq.interval_change(['2026-01-01', '2026-06-01'], [0.0, 5.0],
                           PRICE_U, start='2026-03-01', end='2026-06-01')
check("价格类零基准→拒算(既有行为不回归)",
      zero.get('available') is False and '0' in zero.get('reason', ''))
neg_rate = rhq.interval_change(['2026-01-01', '2026-06-01'], [-0.50, -0.40],
                               RATE_U, start='2026-03-01', end='2026-06-01')
check("利率负水平(DFR −0.5→−0.4 era)→pp=+0.10 正确",
      abs(neg_rate.get('pp_change', 99) - 0.10) < 1e-9, str(neg_rate))

print("═" * 60)
print("[4] 多窗口表利率族纳入(C席附加发现修复)")
print("═" * 60)
SYN_REG = {'metrics': [
    {'metric_id': 'SPX', 'display_name': '标普500', 'unit': PRICE_U,
     'status': 'active', 'asset_class': 'equity_index', 'economy': 'US',
     'source': 'synthetic'},
    {'metric_id': 'UST_10Y', 'display_name': '美债10年', 'unit': RATE_U,
     'status': 'active', 'asset_class': 'rates_yield', 'economy': 'US',
     'source': 'synthetic'},
    {'metric_id': 'DFEDTARU', 'display_name': '目标区间上限', 'unit': RATE_U,
     'status': 'active', 'asset_class': 'policy_rate', 'economy': 'US',
     'source': 'synthetic'},
    {'metric_id': 'CURVE_2S10S', 'display_name': '2s10s斜率', 'unit': RATE_U,
     'status': 'active', 'asset_class': 'curve_slope', 'economy': 'US',
     'source': 'synthetic'},
    {'metric_id': 'NFP', 'display_name': '非农', 'unit': COUNT_U,
     'status': 'active', 'asset_class': 'macro_count', 'economy': 'US',
     'source': 'synthetic'},
], 'by_id': {}}
SYN_REG['by_id'] = {m['metric_id']: m for m in SYN_REG['metrics']}
sdates = ['2025-10-01', '2025-11-01', '2026-08-01', '2026-11-01']
SYN_SNAP = {
    'snapshot_id': 'research_snapshot_20261101_syn', 'target_date': '20261101',
    'facts': [{'metric_id': m, 'value': 4.0 if m != 'SPX' else 5000.0,
               'unit': SYN_REG['by_id'][m]['unit'],
               'observation_date': '2026-11-01', 'quality_status': 'PASS'}
              for m in ('SPX', 'UST_10Y', 'DFEDTARU', 'CURVE_2S10S')],
    'series_store': {m: {'dates': sdates, 'values': [3.8, 3.9, 4.1, 4.0]}
                     for m in ('UST_10Y', 'DFEDTARU', 'CURVE_2S10S')} | {
        'SPX': {'dates': sdates, 'values': [4600.0, 4700.0, 4900.0, 5000.0]}},
}
rows = wd.market_window_rows(SYN_SNAP, SYN_REG, root=ROOT)
by_id = {r['ID']: r for r in rows}
check("利率族三席全入多窗口表(rates_yield/policy_rate/curve_slope)",
      {'UST_10Y', 'DFEDTARU', 'CURVE_2S10S'} <= set(by_id), str(sorted(by_id)))
check("美债 3m 变化可答(UST_10Y 3m列=pp 值)",
      by_id['UST_10Y']['3m变化'].endswith('pp'), str(by_id['UST_10Y']['3m变化']))
check("资产类仍在(SPX)", 'SPX' in by_id)
check("非资产非利率族不入表(macro_count NFP)", 'NFP' not in by_id)
rows_nr = wd.market_window_rows(SYN_SNAP, SYN_REG, root=ROOT, include_rates=False)
check("include_rates=False→旧口径(利率族不入,兼容开关)",
      'UST_10Y' not in {r['ID'] for r in rows_nr})

print("═" * 60)
print("[5] 序列 caption 族感知(C席 CONFIRMED 旧版一律水平%)")
print("═" * 60)
cap_r = wd.series_change_caption(RATE_U, 4.7, 4.1)
check("失业率 4.7→4.1 → -0.60pp(利率口径,非 -12.77%)",
      cap_r['family'] == 'rate' and '-0.60pp' in cap_r['text'], cap_r['text'])
cap_p = wd.series_change_caption(PRICE_U, 100.0, 110.0)
check("价格 100→110 → +10.00%", '+10.00%' in cap_p['text'], cap_p['text'])
cap_z = wd.series_change_caption(PRICE_U, 0.0, 5.0)
check("价格零基准→caption 如实不可定义",
      '不可定义' in cap_z['text'], cap_z['text'])
cap_n = wd.series_change_caption(PRICE_U, -100.0, -90.0)
check("价格负基准→caption 如实不可用", '不可用' in cap_n['text'], cap_n['text'])
cap_c = wd.series_change_caption(COUNT_U, 200000.0, 210000.0)
check("计数 200k→210k → 绝对差", '绝对差' in cap_c['text'], cap_c['text'])

print("═" * 60)
print("[6] 月频单月缺测: common window 如实,不插值")
print("═" * 60)
g_dates = ['2025-06-01', '2025-08-01', '2025-10-01', '2025-12-01']  # 缺 7/9/11 月
g_vals = [1.0, 2.0, 3.0, 4.0]
node = rhq.interval_change(g_dates, g_vals, RATE_U, start='2025-11-01',
                           end='2025-12-01')
check("缺测月后基准取实际前一观测(2025-10-01),不插值",
      node.get('basis_date') == '2025-10-01', str(node))
check("pp=末值−实际基准(4.0−3.0=+1.00)",
      abs(node.get('pp_change', 99) - 1.0) < 1e-9, str(node))

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
