#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据批1(P2 台账待裁定项落地,2026-11-10,dev/data-batch1-v1)接线测试。

覆盖(独立期望值手算,零网络零真实数据目录):
  [1] 注册表 v2.8.0: SPX_EPS/M2SL 新条目结构+DAX/CAC40 转正(通道归属
      global)+语义校验零 error+四条目均非 core(缺席=noncore_missing 披露)。
  [2] global 通道: WATCHLIST ^GDAXI/^FCHI+TOPIX 不入(免费不可得不登记)
      +normalize_global 端到端 DAX 事实(合成档)。
  [3] M2SL: macro 三表接线+compute_series_changes 月频手算(mom/yoy/pct)
      +normalize_macro 事实+单位校准锁(billion_usd=FRED原始单位,与
      WALCL 校准纪律同源)。
  [4] CN 指数深窗: cn_window_start 纯函数(ytd/10y/max/1mo/闰日)
      +_ytd_base_close 纯函数(深窗YTD基准=当年首个收盘)
      +CN_INDEX_HISTORY_PERIOD 解析(env/非法回落/默认10y)。
  [5] 通道纪律: ea 零依赖(DAX 移 global 后 ea 不引入 yfinance)
      +DFF 归 rate_expectations(登记通道不可混)+ledger 数据批1登记在场。

数据纪律: 全部合成 fixture;真实拉取验证=会话内实跑+台账登记,不入测试。
运行: ~/AI内容/venv/bin/python3 tests/test_data_batch1.py
"""
import json
import os
import sys
from datetime import date

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


print("=" * 72)

REG_JSON = json.load(open(os.path.join(ROOT, 'config', 'metric_registry.json'),
                          encoding='utf-8'))
REG = {m['metric_id']: m for m in REG_JSON['metrics']}
BY_ID = REG

import fact_engine as fe            # noqa: E402
import macro_collector as mc         # noqa: E402
import global_market_collector as gmc  # noqa: E402
import registry_semantics as rsem    # noqa: E402
import research_provenance as rp     # noqa: E402

# ══ [1] 注册表 v2.8.0 结构(版本锁随升 v2.8.1, R6-D1 源切换) ═════════
print("\n[1] 注册表(数据批1面: +SPX_EPS/M2SL,DAX/CAC40 转正;锁随升 v2.8.1)")
_n80 = [n for n in REG_JSON['notes'] if n.startswith('v2.8.0')]
check("版本 v2.8.1+数据批1注记仍在册",
      REG_JSON['version'] == '2.8.1'
      and len(_n80) == 1 and 'SPX_EPS' in _n80[0] and 'M2SL' in _n80[0],
      REG_JSON['version'])
check("110项/108活跃(数据批1 +2)",
      len(REG_JSON['metrics']) == 110
      and sum(1 for m in REG_JSON['metrics'] if m['status'] == 'active') == 108,
      str(len(REG_JSON['metrics'])))
probs = rsem.validate_registry(REG_JSON)
new_errs = [p for p in probs if p.get('severity') == 'error'
            and p.get('metric_id') in ('SPX_EPS', 'M2SL', 'DAX', 'CAC40')]
check("新/转正四条目零结构 error", not new_errs, str(new_errs[:2]))
core_ids = rp.core_metric_ids()
check("四条目均 important 非 core(缺席=noncore_missing 如实,不改 FAIL 语义)",
      all(BY_ID[m]['criticality'] == 'important' for m in
          ('SPX_EPS', 'M2SL', 'DAX', 'CAC40'))
      and not ({'SPX_EPS', 'M2SL', 'DAX', 'CAC40'} & set(core_ids)))

# SPX_EPS 结构(独立期望: 同 CAPE/PE 家族字段面)
e = BY_ID['SPX_EPS']
check("SPX_EPS: shiller/E列/月频/calendar_month/usd/US",
      e['source'] == 'shiller_collector' and e['source_symbol'] == 'ie_data.xls!E'
      and e['frequency'] == 'monthly'
      and e['observation_period_kind'] == 'calendar_month'
      and e['unit'] == 'usd' and e['economy'] == 'US'
      and e['freshness']['max_calendar_lag_days'] == 75,
      str({k: e.get(k) for k in ('source', 'source_symbol', 'unit')}))
check("SPX_EPS: 量程[0,500]容1871(≈0.4)~当前(≈300)名义EPS",
      e['validation']['range'] == [0, 500], str(e['validation']['range']))
check("SPX_EPS: 与CAPE同vintage披露(latest_vintage_asof_collected)",
      'latest_vintage_asof_collected' in e['release_semantics'])

# M2SL 结构
e = BY_ID['M2SL']
check("M2SL: macro_collector/FRED M2SL/月频/calendar_month/US",
      e['source'] == 'macro_collector' and e['source_symbol'] == 'M2SL'
      and e['frequency'] == 'monthly'
      and e['observation_period_kind'] == 'calendar_month'
      and e['economy'] == 'US', str({k: e.get(k) for k in ('source',
                                                           'source_symbol')}))
check("M2SL 单位校准锁: billion_usd=FRED 原始单位(M2SL官方=十亿美元;与"
      "WALCL校准纪律同源——单位描述原始值,零换算)",
      e['unit'] == 'billion_usd' and e['validation']['range'] == [8000, 40000],
      f"unit={e['unit']} range={e['validation']['range']}")

# DAX/CAC40 转正
for mid, sym in (('DAX', '^GDAXI'), ('CAC40', '^FCHI')):
    e = BY_ID[mid]
    check(f"{mid}: source=global_market_collector+symbol={sym}(PENDING 转正)",
          e['source'] == 'global_market_collector'
          and e['source_symbol'] == sym
          and e['source_symbol'] != 'PENDING',
          str((e['source'], e['source_symbol'])))
    check(f"{mid}: economy=EA/calendar=ea/index_point 保持(身份面零变化)",
          e['economy'] == 'EA' and e['calendar'] == 'ea'
          and e['unit'] == 'index_point'
          and e['identity'] == {'instrument': 'index', 'adjustment': 'none'})
check("TOPIX 未登记(Yahoo 免费无 ^TPX 实测,宁缺毋假)",
      'TOPIX' not in BY_ID and all('TOPIX' not in m['metric_id']
                                   for m in REG_JSON['metrics']))

# ══ [2] global 通道接线 ════════════════════════════════════════════
print("\n[2] global 通道 DAX/CAC40")
check("WATCHLIST: DAX=^GDAXI/CAC40=^FCHI/TOPIX 不入",
      gmc.WATCHLIST.get('DAX') == '^GDAXI'
      and gmc.WATCHLIST.get('CAC40') == '^FCHI'
      and 'TOPIX' not in gmc.WATCHLIST)
GLB = {'time': '07:00:00',
       'data': {'DAX': {'close': 26559.83, 'date': '2026-11-10',
                        'high': 26620.0, 'low': 26401.7,
                        'series': {'dates': ['2026-11-03', '2026-11-04',
                                             '2026-11-05', '2026-11-06',
                                             '2026-11-07', '2026-11-10'],
                                   'values': [26301.0, 26380.5, 26415.2,
                                              26500.1, 26480.3, 26559.83]}}}}
facts = fe.normalize_global(GLB, '2026-11-10T07:30:00+08:00',
                            'global_20261110.json')
fmap = {f['metric_id']: f for f in facts}
check("normalize_global: DAX 事实生成(值/观测日/序列随行/非FAIL)",
      'DAX' in fmap and fmap['DAX']['value'] == 26559.83
      and fmap['DAX']['observation_date'] == '2026-11-10'
      and fmap['DAX']['source']['collector'] == 'global_market_collector'
      and fmap['DAX']['quality_status'] != 'FAIL',
      str([(f.get('metric_id'), f.get('quality_status')) for f in facts]))
check("DAX 事实身份: instrument=index+unit=index_point(注册表贯通)",
      (fmap['DAX'].get('identity') or {}).get('instrument') == 'index'
      and fmap['DAX']['unit'] == 'index_point')
wk = (fmap['DAX'].get('derived') or {}).get('week')
check("DAX 周收益=26559.83/26480.3−1≈+0.2996%(价格族口径)",
      wk is not None and abs(wk.get('pct_change', 9)
                             - (26559.83 / 26480.3 - 1) * 100) < 1e-3,
      str(wk))

# ══ [3] M2SL 采集器接线 ════════════════════════════════════════════
print("\n[3] M2SL 三表接线+月频变化口径")
check("macro_collector: FRED_SERIES/SERIES_FREQ/SERIES_UNITS 三表",
      mc.FRED_SERIES.get('M2SL') == 'M2SL'
      and mc.SERIES_FREQ.get('M2SL') == 'monthly'
      and mc.SERIES_UNITS.get('M2SL', (None,))[0] == 'index'
      and '十亿美元' in mc.SERIES_UNITS['M2SL'][1])
# 月频手算: 13个月, yoy 基=同月上年(窗口内 12 个月前最近观测)
m_d = ['2025-10-01', '2025-11-01', '2025-12-01', '2026-01-01', '2026-02-01',
       '2026-03-01', '2026-04-01', '2026-05-01', '2026-06-01', '2026-07-01',
       '2026-08-01', '2026-09-01', '2026-10-01']
m_v = [23000.0, 23050.0, 23100.0, 23120.0, 23150.0, 23180.0, 23200.0,
       23220.0, 23250.0, 23280.0, 23300.0, 23350.0, 23413.9]
ch = mc.compute_series_changes(m_d, m_v, 'monthly', unit=mc.SERIES_UNITS['M2SL'])
check("M2SL mom_chg=+63.9(23413.9−23350)+mom_pct 手算",
      abs(ch.get('mom_chg', 9) - 63.9) < 1e-6
      and abs(ch.get('mom_pct', 9) - (23413.9 / 23350.0 - 1) * 100) < 1e-4,
      json.dumps({k: v for k, v in ch.items() if k.startswith(('mom', 'yoy'))},
                 ensure_ascii=False))
check("M2SL yoy=既有月频机制基点(约12个月前最近观测=2025-11-01,23050):"
      "yoy_chg=+363.9+yoy_pct≈+1.5787%",
      ch.get('yoy_chg_from') == '2025-11-01'
      and abs(ch.get('yoy_chg', 9) - 363.9) < 1e-6
      and abs(ch.get('yoy_pct', 9) - (23413.9 / 23050.0 - 1) * 100) < 1e-4,
      json.dumps({k: v for k, v in ch.items() if k.startswith('yoy')},
                 ensure_ascii=False))
MAC = {'data': {'M2SL': {'value': 23413.9, 'date': '2026-09-01',
                         'frequency': 'monthly',
                         'series': {'dates': m_d, 'values': m_v}}}}
mfacts = fe.normalize_macro(MAC, '2026-11-10T08:00:00+08:00',
                            'macro_20261110.json')
mmap = {f['metric_id']: f for f in mfacts}
check("normalize_macro: M2SL 事实(值/观测月/单位/非FAIL)",
      'M2SL' in mmap and mmap['M2SL']['value'] == 23413.9
      and mmap['M2SL']['observation_date'] == '2026-09-01'
      and mmap['M2SL']['unit'] == 'billion_usd'
      and mmap['M2SL']['quality_status'] != 'FAIL',
      str([(f.get('metric_id'), f.get('quality_status'),
            [i.get('message', '')[:60] for i in f.get('issues', [])[:2]])
           for f in mfacts]))

# ══ [4] CN 指数深窗 ════════════════════════════════════════════════
print("\n[4] CN 指数深窗参数化(台账#10)")
import china_market_collector as cmc  # noqa: E402
ws = cmc.cn_window_start
check("cn_window_start('ytd')=当年0101(旧行为精确保留)",
      ws('ytd', date(2026, 11, 10)) == '20260101')
check("cn_window_start('10y')=20161110(默认深窗)",
      ws('10y', date(2026, 11, 10)) == '20161110')
check("cn_window_start('max')=上证基日19901219(源端实际可得为准)",
      ws('max', date(2026, 11, 10)) == '19901219')
check("cn_window_start('1mo')=自然日31天(2026-03-31→02-28)",
      ws('1mo', date(2026, 3, 31)) == '20260228')
check("闰日回退: 2028-02-29 的 10y 窗→2018-02-28(不崩,近端语义)",
      ws('10y', date(2028, 2, 29)) == '20180228')
env_tests = [('CN_INDEX_HISTORY_PERIOD', 'ytd', 'ytd'),
             ('CN_INDEX_HISTORY_PERIOD', 'banana', '10y')]
for var, val, expect in env_tests:
    old = os.environ.get(var)
    os.environ[var] = val
    got = cmc.cn_index_history_period()
    if old is None:
        os.environ.pop(var, None)
    else:
        os.environ[var] = old
    check(f"CN_INDEX_HISTORY_PERIOD={val!r}→{expect}", got == expect, got)
old = os.environ.pop('CN_INDEX_HISTORY_PERIOD', None)
check("CN_INDEX_HISTORY_PERIOD 未设→默认 10y(数据批1深窗缺口修复)",
      cmc.cn_index_history_period() == '10y')
yb = cmc._ytd_base_close
check("_ytd_base_close: 深窗YTD基准=当年首个收盘(非序列首根)",
      yb(['20241231', '20250102', '20250310', '20260105', '20260106',
          '20261110'],
         [3000.0, 3050.0, 3100.0, 3200.0, 3210.0, 3300.0], '20261110')
      == 3200.0)
check("_ytd_base_close: 传入年末观测日而序列无该年行→退回序列首根"
      "(调用方护栏,非完整YTD如实)",
      yb(['20241231', '20251128'], [3000.0, 3100.0], '20260102') == 3000.0)
check("_ytd_base_close: 空序列→None(不猜)", yb([], [], '20260102') is None)
check("61s 限流闸门未动(窗口加宽不增调用次数)",
      cmc.INDEX_DAILY_MIN_INTERVAL_SECONDS == 61)

# ══ [5] 通道纪律+台账 ══════════════════════════════════════════════
print("\n[5] 通道纪律与台账登记")
ea_src = open(os.path.join(ROOT, 'scripts', 'ea_market_collector.py'),
              encoding='utf-8').read()
check("ea 通道零依赖保持(DAX 移 global 后不引入 yfinance import;"
      "docstring/告警中的'yfinance不入依赖面'字样=纪律注记非依赖)",
      'import yfinance' not in ea_src)
check("DFF 通道归属=rate_expectations(登记通道不可混,数据批1复核)",
      BY_ID['DFF']['source'] == 'rate_expectations'
      and BY_ID['ZQ_F1_PRICE']['source'] == 'rate_expectations')
check("REAL_10Y/HY_IG_DIFF=事实层派生(非采集通道)",
      BY_ID['REAL_10Y']['source'] == 'fact_engine(derived)'
      and BY_ID['HY_IG_DIFF']['source'] == 'fact_engine(derived)')
LEDGER = os.path.join(ROOT, 'docs', 'P2_DATA_GAP_LEDGER.md')
ledger = open(LEDGER, encoding='utf-8').read()
check("台账: 数据批1首跑登记在场(逐项 n/首末观测日/源端限制)",
      '数据批1' in ledger and 'SPX_EPS' in ledger and 'M2SL' in ledger
      and '^GDAXI' in ledger)

print("\n" + "=" * 72)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 72)
sys.exit(0 if FAIL == 0 else 1)
