# -*- coding: utf-8 -*-
"""
Charter6-P1 缺失补齐 回归测试(2026-11-09;A2 §2#1/#2/#3+P1#5-7 规格对应)

覆盖五块:
  一、GDPC1 登记面(FRED_SERIES/频率/单位)+季频变化计算逐值手算
     (QoQ 基准=上一季观测,YoY 基准=首个自然日滞后∈[330,400]的观测)
  二、japan_rate_collector fredgraph 全行解析(升序全量/'.'与空行跳过/非法行
     告警)+ build_payload series 节(data/observations 口径不变)
  三、ea_market_collector: DFR/MRO startPeriod=1999 + SDMX 全行入 series 节
     (BUND 不入=诚实边界)+ BBK 重试/退避(网络层异常重试,HTTPError 不重试,
     ECB 源单次)
  四、snapshot_builder.merge_series_sections: 权属守卫(别名行/未登记键/
     形态非法不入;既有池先占不覆盖)
  五、注册表/freshness/词汇面: US_REAL_GDP 条目字段逐项+版本 2.5.0+
     registry_semantics 零error零review+freshness quarterly 合法
全部离线(合成字节注入,零网络);期望值手算,禁用被测函数自算自身答案。
运行: python3 tests/test_charter6_p1_missing_series.py(脚本式,与CI一致)
"""
import io
import json
import os
import sys
import urllib.error
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS = 0
FAIL = 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


print("=" * 64)
print("一、GDPC1 登记面 + 季频变化计算(手算)")
print("=" * 64)
import macro_collector as mc  # noqa: E402

check("FRED_SERIES += US_REAL_GDP→GDPC1", mc.FRED_SERIES.get('US_REAL_GDP') == 'GDPC1')
check("SERIES_FREQ: US_REAL_GDP=quarterly",
      mc.SERIES_FREQ.get('US_REAL_GDP') == 'quarterly')
check("SERIES_UNITS: US_REAL_GDP=(index,十亿美元(2017年链式,SAAR))",
      mc.SERIES_UNITS.get('US_REAL_GDP') == ('index', '十亿美元(2017年链式,SAAR)'))

# 20 个季度观测(i=0..19): i0=2021-12-31,季度轮转 12→3→6→9→12;
# 末值 i19=2026-09-30;v_i = 20000+60i(手算: v18=21080, v19=21140, v15=20900)
_LAST_DAY = {3: 31, 6: 30, 9: 30, 12: 31}
q_dates, y, mth = [], 2021, 12
for _i in range(20):
    q_dates.append(date(y, mth, _LAST_DAY[mth]))
    if mth == 12:
        y += 1
    mth = {12: 3, 3: 6, 6: 9, 9: 12}[mth]
q_dates_iso = [d.isoformat() for d in q_dates]
check("fixture: 末观测=2026-09-30(第20季)", q_dates_iso[-1] == '2026-09-30',
      q_dates_iso[-1])
check("fixture: 次末观测=2026-06-30", q_dates_iso[-2] == '2026-06-30',
      q_dates_iso[-2])
check("fixture: 4季前=2025-09-30", q_dates_iso[15] == '2025-09-30',
      q_dates_iso[15])
q_vals = [20000.0 + 60.0 * i for i in range(20)]
out = mc.compute_series_changes(q_dates_iso, q_vals, 'quarterly',
                                unit=('index', '十亿美元(2017链式,SAAR)'))
# 手算: prev=21080; qoq=21140−21080=60; qoq_pct=60/21080×100=0.2846;
#       yoy 基准=2025-09-30(滞后365∈[330,400]首个,v15=20900);
#       yoy=240; yoy_pct=240/20900×100=1.1483
check("季频: prev=21080(手算)", out.get('prev') == 21080, out.get('prev'))
check("季频: qoq_chg=60点(手算)", out.get('qoq_chg') == 60, out.get('qoq_chg'))
check("季频: qoq_pct=0.2846(手算 60/21080)",
      out.get('qoq_pct') == 0.2846, out.get('qoq_pct'))
check("季频: qoq基准=2026-06-30", out.get('qoq_chg_from') == '2026-06-30')
check("季频: yoy_chg=240点(手算 21140−20900)",
      out.get('yoy_chg') == 240, out.get('yoy_chg'))
check("季频: yoy_pct=1.1483(手算 240/20900)",
      out.get('yoy_pct') == 1.1483, out.get('yoy_pct'))
check("季频: yoy基准=2025-09-30", out.get('yoy_chg_from') == '2025-09-30')
check("季频: 不产 week_chg/mom_chg(口径不存在)",
      'week_chg' not in out and 'mom_chg' not in out)

print("=" * 64)
print("二、japan fredgraph 全行解析 + series 节")
print("=" * 64)
import japan_rate_collector as jrc  # noqa: E402

# 手造 fredgraph CSV(行序=升序;含'.'缺失/空值/列数不符/非法数值四种噪声行)
JP_CSV = (b'observation_date,IRSTCI01JPM156N\n'
          b'1974-01-01,.\n'
          b'1974-02-01,0.1\n'
          b'1974-03-01,\n'
          b'bad-line-only-one-cell\n'
          b'1974-04-01,0.2\n'
          b'1974-05-01,abc\n'
          b'1974-06-01,0.3\n')
dates, values, alerts = jrc.fetch_fred_policy_rate_series(JP_CSV)
check("全行解析: dates=3个有效观测(手写期望)",
      dates == ['1974-02-01', '1974-04-01', '1974-06-01'], dates)
check("全行解析: values=[0.1,0.2,0.3]", values == [0.1, 0.2, 0.3], values)
check("全行解析: 非法数值行告警恰1条(1974-05-01 abc)",
      len(alerts) == 1 and '1974-05-01' in alerts[0], alerts)
obs, val, alerts2 = jrc.fetch_fred_policy_rate(JP_CSV)
check("旧接口兼容: 最新期=(1974-06-01,0.3)",
      (obs, val) == ('1974-06-01', 0.3) and len(alerts2) == 1, (obs, val))
dates_e, values_e, _ = jrc.fetch_fred_policy_rate_series(
    b'observation_date,IRSTCI01JPM156N\n')
check("空历史(仅表头): 不可用哨兵", dates_e is None and values_e is None)

# MOF 合成档(纯ASCII,shift_jis 可解码;列头期限映射 2Y/10Y)
MOF_CSV = (b'jgbcme all data,csv\n'
           b'Date,1Y,2Y,5Y,10Y,20Y,30Y,40Y\n'
           b'2026/11/4,0.41,0.51,0.71,1.01,1.71,2.11,2.41\n'
           b'2026/11/5,0.40,0.50,0.70,1.00,1.70,2.10,2.40\n')
payload, n = jrc.build_payload(run_date=date(2026, 11, 6),
                               mof_raw=MOF_CSV, fred_raw=JP_CSV)
check("payload: data 四系列(JGB×3+政策利率)",
      n == 4 and payload['data']['JP_POLICY_RATE'] == 0.3
      and payload['data']['JGB2Y'] == 0.50 and payload['data']['JGB10Y'] == 1.00)
check("payload: 观测日披露口径不变(最新期)",
      payload['observations']['JP_POLICY_RATE'] == '1974-06-01'
      and payload['observations']['JGB2Y'] == '2026-11-05')
check("payload: series 节=全史3观测(手写期望)",
      payload.get('series', {}).get('JP_POLICY_RATE') ==
      {'dates': ['1974-02-01', '1974-04-01', '1974-06-01'],
       'values': [0.1, 0.2, 0.3]},
      payload.get('series'))
payload2, _ = jrc.build_payload(
    run_date=date(2026, 11, 6), mof_raw=MOF_CSV,
    fred_raw=b'observation_date,IRSTCI01JPM156N\n1974-01-01,.\n')
check("payload: FRED全缺→series 节键不出现+缺席告警",
      'series' not in payload2
      and any('JP_POLICY_RATE缺席' in a for a in payload2['alerts']))

print("=" * 64)
print("三、ea: startPeriod=1999 + SDMX 全行 series + BBK 重试")
print("=" * 64)
import ea_market_collector as ea  # noqa: E402

check("ECB_DFR_URL startPeriod=1999-01-01",
      'startPeriod=1999-01-01' in ea.ECB_DFR_URL)
check("ECB_MRO_URL startPeriod=1999-01-01",
      'startPeriod=1999-01-01' in ea.ECB_MRO_URL)

DFR_CSV = (b'TIME_PERIOD,OBS_VALUE\n'
           b'1999-01-04,3.0\n'
           b'2001-05-10,4.0\n'
           b'2023-09-20,3.75\n'
           b'2024-06-12,3.75\n'
           b'2025-06-11,2.0\n')
MRO_CSV = (b'TIME_PERIOD,OBS_VALUE\n'
           b'1999-01-04,4.5\n'
           b'2025-06-11,2.15\n')
BBK10_CSV = b'TIME_PERIOD,OBS_VALUE\n2026-11-06,2.28\n2026-11-07,2.30\n'
BBK2_CSV = b'TIME_PERIOD,OBS_VALUE\n2026-11-06,2.24\n2026-11-07,2.26\n'
BBK10_META = b'"...Restlaufzeit von uber 9 bis 10 Jahren..."'
BBK2_META = b'"...Restlaufzeit von uber 1 bis 2 Jahren..."'
ep, en = ea.build_payload(run_date=date(2026, 11, 8),
                          ecb_dfr_raw=DFR_CSV, ecb_mro_raw=MRO_CSV,
                          bbk10_raw=BBK10_CSV, bbk2_raw=BBK2_CSV,
                          bbk10_meta_raw=BBK10_META, bbk2_meta_raw=BBK2_META)
check("ea: 末值/次新值口径不变(DFR value=2.0 prev=3.75)",
      ep['policy_rates']['ECB_DFR'] == {'value': 2.0, 'unit': 'percent',
                                        'date': '2025-06-11',
                                        'prev_value': 3.75},
      ep['policy_rates'].get('ECB_DFR'))
check("ea: series 节 DFR=5观测升序(手写期望)",
      ep['series']['ECB_DFR'] ==
      {'dates': ['1999-01-04', '2001-05-10', '2023-09-20', '2024-06-12',
                 '2025-06-11'],
       'values': [3.0, 4.0, 3.75, 3.75, 2.0]},
      ep.get('series', {}).get('ECB_DFR'))
check("ea: series 节 MRO=2观测(手写期望)",
      ep['series']['ECB_MRO'] ==
      {'dates': ['1999-01-04', '2025-06-11'], 'values': [4.5, 2.15]})
check("ea: BUND 不入 series 节(历史化=A2 P2#12,本轮只修源故障)",
      'BUND_10Y' not in ep.get('series', {})
      and 'BUND_2Y' not in ep.get('series', {}))
check("ea: BUND 末值照常在节(BBK 重试修复的产出面)",
      ep['bund']['BUND_10Y']['value'] == 2.30
      and ep['bund']['BUND_2Y']['value'] == 2.26)

# BBK 重试(注入替身 _open_url;手算调用序列)
class _Flaky:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def __call__(self, url, headers):
        self.calls.append(url)
        o = self.outcomes.pop(0)
        if isinstance(o, Exception):
            raise o
        return o


sleeps = []
ea._sleep = lambda s: sleeps.append(s)   # 退避可注入(不真睡)
orig_open = ea._open_url
try:
    fl = _Flaky([ConnectionResetError('RemoteDisconnected'),
                 ConnectionResetError('RemoteDisconnected'), b'ok-bytes'])
    ea._open_url = fl
    got = ea._http_get('https://api.bundesbank.de/x', 'bbk')
    check("BBK重试: 两连断后第3次成功取回", got == b'ok-bytes' and len(fl.calls) == 3,
          (got, len(fl.calls)))
    check("BBK重试: 退避序列=[2,5]秒(手写期望)", sleeps == [2, 5], sleeps)
    sleeps.clear()
    fl2 = _Flaky([urllib.error.HTTPError('u', 403, 'forbidden', None, None)])
    ea._open_url = fl2
    raised = False
    try:
        ea._http_get('https://api.bundesbank.de/x', 'bbk')
    except urllib.error.HTTPError:
        raised = True
    check("BBK重试: HTTPError 不重试(1次即抛)", raised and len(fl2.calls) == 1,
          len(fl2.calls))
    fl3 = _Flaky([ConnectionResetError('drop')])
    ea._open_url = fl3
    raised2 = False
    try:
        ea._http_get('https://data-api.ecb.europa.eu/x', 'ecb')
    except ConnectionResetError:
        raised2 = True
    check("ECB源: 保持单次不重试(请求面不放大)", raised2 and len(fl3.calls) == 1
          and sleeps == [])
finally:
    ea._open_url = orig_open
    del ea._sleep

print("=" * 64)
print("四、snapshot merge_series_sections 权属守卫")
print("=" * 64)
import snapshot_builder as sb  # noqa: E402
import fact_engine as fe  # noqa: E402

assert fe.metric('JP_POLICY_RATE')['source'] == 'japan_rate_collector'
assert fe.metric('ECB_DFR')['source'] == 'ea_market_collector'
raw = {'japan': {'series': {
           'JP_POLICY_RATE': {'dates': ['1974-02-01', '2026-09-01'],
                              'values': [0.1, 0.3]}},
       'data': {}, 'observations': {}},
       'ea': {'series': {
           'ECB_DFR': {'dates': ['1999-01-04', '2025-06-11'],
                       'values': [3.0, 2.0]},
           'BRENT': {'dates': ['2026-01-02'], 'values': [70.0]},
           'NOT_REGISTERED': {'dates': ['2026-01-02'], 'values': [1.0]},
           'ECB_MRO': {'dates': ['a', 'b'], 'values': [1.0]}}}}
store = sb.merge_series_sections({}, raw)
check("lift: 恰入 JP_POLICY_RATE+ECB_DFR",
      sorted(store) == ['ECB_DFR', 'JP_POLICY_RATE'], sorted(store))
check("lift: 值零改写直通",
      store['ECB_DFR']['values'] == [3.0, 2.0]
      and store['JP_POLICY_RATE']['dates'][0] == '1974-02-01')
check("lift: 别名行(BRENT,权属=global)不入计算面", 'BRENT' not in store)
check("lift: 未登记键不入", 'NOT_REGISTERED' not in store)
check("lift: 形态非法(dates/values不等长)不入", 'ECB_MRO' not in store)
pre = {'JP_POLICY_RATE': {'dates': ['X'], 'values': [0.0]}}
store2 = sb.merge_series_sections(pre, raw)
check("lift: 既有池先占不覆盖", store2['JP_POLICY_RATE']['dates'] == ['X'])
store3 = sb.merge_series_sections({}, {'japan': {}, 'ea': {}})
check("lift: 节缺席=诚实缺席零动作", store3 == {})

print("=" * 64)
print("五、注册表/词汇/freshness 面")
print("=" * 64)
reg = json.load(open(os.path.join(ROOT, 'config', 'metric_registry.json'),
                     encoding='utf-8'))
by = {m['metric_id']: m for m in reg['metrics']}
check("版本=2.8.1(R6-D1 CPI/PPI换源;数据批1曾升2.8.0)", reg['version'] == '2.8.1', reg['version'])
check("指标数=110(数据批1: +SPX_EPS/M2SL)", len(reg['metrics']) == 110,
      len(reg['metrics']))
g = by.get('US_REAL_GDP') or {}
check("US_REAL_GDP 字段逐项",
      g.get('source') == 'macro_collector' and g.get('source_symbol') == 'GDPC1'
      and g.get('frequency') == 'quarterly' and g.get('unit') == 'billion_usd'
      and g.get('calendar') == 'us_rates' and g.get('economy') == 'US'
      and g.get('status') == 'active' and g.get('criticality') == 'important'
      and g.get('value_type') == 'level', {k: g.get(k) for k in (
          'source', 'source_symbol', 'frequency', 'unit', 'calendar')})
check("US_REAL_GDP: observation_period_kind 不登记(枚举无calendar_quarter,"
      "按纪律缺键=未登记)", 'observation_period_kind' not in g)
check("US_REAL_GDP: release_semantics 含滞后窗口与修订口径",
      '25-30' in g.get('release_semantics', '')
      and 'latest_vintage_asof_collected' in g.get('release_semantics', ''))
check("US_REAL_GDP: freshness 窗=120天(季频+发布滞后)",
      g.get('freshness', {}).get('max_calendar_lag_days') == 120)
check("notes 登记修订口径披露(A2 §3.1)",
      any('latest_vintage_asof_collected' in x for x in reg.get('notes', [])))
import registry_semantics as rsem  # noqa: E402
check("registry_semantics: 零 error", rsem.registry_semantic_errors(reg) == [])
check("registry_semantics: 零 review", rsem.registry_semantic_reviews(reg) == [])
check("FREQUENCY_VALUES 含 quarterly", 'quarterly' in rsem.FREQUENCY_VALUES)
import freshness_policy as fpol  # noqa: E402
import fact_engine  # noqa: E402
check("fact_engine.load_registry 通过(freshness quarterly 合法)",
      len(fact_engine.load_registry(force=True)['metrics']) == 110)  # 数据批1 +2
check("billion_usd 入价格类单位族(变化=百分比口径)",
      'billion_usd' in fact_engine.PRICE_LIKE_UNITS)

print("=" * 64)
if FAIL == 0:
    print(f"✅ 全部通过: {PASS} 项")
else:
    print(f"❌ 失败 {FAIL} 项 / 通过 {PASS} 项")
    sys.exit(1)
