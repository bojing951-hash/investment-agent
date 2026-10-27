#!/usr/bin/env python3
"""第七轮金融事实引擎测试 — 指标注册表/统一收益引擎/校验12类/派生/对账/分级

数据纪律(spec §18): 合成fixture序列仅测引擎数学正确性(显式标注SYNTHETIC);
真实锚点值为2026-10-16已双重核验的收盘(标注REAL), 只做身份/量级断言。
运行: ~/AI内容/venv/bin/python3 tests/test_fact_engine.py
"""
import os
import sys
from datetime import date, timedelta

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


print("=" * 60)
print("事实引擎: 注册表/收益引擎/校验/派生/对账")
print("=" * 60)

import fact_engine as fe
import trading_calendar as tc

# ══ [1] 注册表 ════════════════════════════════════════════════════
print("\n[1] 指标注册表")
reg = fe.load_registry(force=True)
by_id = reg['by_id']
check("80指标唯一注册", len(by_id) >= 80)
check("WTI双身份分离(期货vs现货月均)", 'WTI_F' in by_id and 'WTI_SPOT_M' in by_id
      and by_id['WTI_F']['source_symbol'] == 'CL=F' and by_id['WTI_SPOT_M']['source_symbol'] == 'WTISPLC')
check("REAL_SHORT已弃用并指明替代", by_id['REAL_SHORT']['status'] == 'deprecated'
      and 'REAL_5Y' in str(by_id['REAL_SHORT'].get('notes')))
check("REAL_5Y期限匹配(5Y−5Y)", 'UST_5Y−BEI_5Y' in str(by_id['REAL_5Y']['source_symbol']))
check("FXI标注代理身份", by_id['FXI']['identity'].get('is_proxy') is True
      and 'A股' in by_id['FXI']['identity']['proxy_of'])
check("黄金期货标注非现货", '非现货' in by_id['GOLD_F']['calc'])
check("ZQ禁止换算降息次数写入注册表", '不得' in by_id['ZQ_IMPLIED_AVG']['calc'])
check("NFP存量与月差双注册", by_id['NFP']['value_type'] == 'level'
      and by_id['NFP_MOM_K']['asset_class'] == 'macro_count_derived')
check("沪深成交额近似口径显式proxy", by_id['CN_TOTAL_TURNOVER']['identity'].get('is_proxy') is True)
check("深证成指标注非全市场", '非深市全市场' in by_id['SZCI'].get('notes', '') + by_id['SZ_COMPONENT_AMOUNT'].get('notes', ''))
check("日频/月频新鲜度窗区分", by_id['SPX']['freshness']['max_calendar_lag_days'] == 5
      and by_id['CPI']['freshness']['max_calendar_lag_days'] == 45)

# ══ [2] 统一收益引擎(合成序列) ════════════════════════════════════
print("\n[2] 统一收益引擎 — SYNTHETIC序列验证数学口径")


def synth_daily(start, days, f, calendar='us_equity'):
    """生成遵循日历的合成序列(显式SYNTHETIC,仅测引擎)。"""
    d, dates, values = date.fromisoformat(start), [], []
    while len(dates) < days:
        if tc.is_trading_day(d, calendar):
            dates.append(d.isoformat())
            values.append(f(d, len(dates)))
        d += timedelta(days=1)
    return dates, values


# 场景A: YTD必须用上一年末收盘作基准(修复旧缺陷: 旧代码用当年首日)
# 2025-12-31收盘=100(年末), 2026-01-02首日=110, 2026-10-16=121
def fa(d, i):
    if d.year == 2025:
        return 100.0
    if d <= date(2026, 1, 10):
        return 110.0
    return 121.0
ds_a, vs_a = synth_daily('2025-11-01', 240, fa)
r = fe.compute_period_returns(ds_a, vs_a, 'index_point', 'us_equity', as_of='2026-10-16')
check("YTD基准=上一年末收盘(2025-12-31,非2026首日)",
      r['ytd']['basis_date'] == '2025-12-31' and r['ytd']['basis_value'] == 100.0,
      f"got basis={r['ytd'].get('basis_date')}/{r['ytd'].get('basis_value')}")
check("YTD=21%(121/100−1)", abs(r['ytd']['pct_change'] - 21.0) < 1e-6, str(r['ytd'].get('pct_change')))
check("旧口径(首日基准)将错算为10%(回归防护)", abs(r['ytd']['pct_change'] - 10.0) > 1e-6)

# 场景B: MTD用前一自然月末; 周变化用ISO周边界
# 9月末=200, 10月每周五+5: 10/2=205,10/9=210,10/16=215
def fb(d, i):
    if d < date(2026, 10, 1):
        return 200.0
    weeks = {2: 205.0, 9: 210.0, 16: 215.0, 23: 220.0}
    for k, v in weeks.items():
        if abs((d - date(2026, 10, k)).days) <= 3:
            return v
    return 205.0
ds_b, vs_b = synth_daily('2026-07-01', 80, fb)
r2 = fe.compute_period_returns(ds_b, vs_b, 'index_point', 'us_equity', as_of='2026-10-16')
check("MTD基准=9月末(200)", r2['mtd']['basis_date'] == '2026-09-30' and r2['mtd']['basis_value'] == 200.0,
      f"got {r2['mtd'].get('basis_date')}/{r2['mtd'].get('basis_value')}")
check("MTD=7.5%(215/200−1)", abs(r2['mtd']['pct_change'] - 7.5) < 1e-6)
check("周基准=上一ISO周五(10-09,210)", r2['week']['basis_date'] == '2026-10-09',
      f"got {r2['week'].get('basis_date')}")
check("周变化≈2.38%(215/210−1)", abs(r2['week']['pct_change'] - (215 / 210 - 1) * 100) < 0.01)

# 场景C: 利率类→pp/bp, 不产pct; 计数类→绝对差
ds_c = ds_b
vs_c = [v / 100 for v in vs_b]  # 2.00→2.05→2.10→2.15 (利率)
r3 = fe.compute_period_returns(ds_c, vs_c, 'percent', 'us_rates', as_of='2026-10-16')
check("利率周变化以bp计(2.15−2.10=5bp)", r3['week'].get('bp_change') == 5.0
      and r3['week'].get('pp_change') == 0.05, str(r3['week']))
check("利率不产百分比变化", 'pct_change' not in r3['week'])
r3c = fe.compute_period_returns(ds_c, [v * 1000 for v in vs_c], 'persons', 'us_rates', as_of='2026-10-16')
check("计数类绝对变化", r3c['week'].get('abs_change') == 50.0 and 'pct_change' not in r3c['week'])

# 场景D: 数据不足→available:false,绝不回退0.0
r4 = fe.compute_period_returns(['2026-10-12', '2026-10-15', '2026-10-16'], [1.0, 2.0, 3.0],
                               'index_point', 'us_equity', as_of='2026-10-16')
check("短序列周变化不可用(非0.0)", r4.get('week', {}).get('available') is False
      or 'reason' in r4.get('week', {}))
check("短序列YTD不可用", r4.get('ytd', {}).get('available') is False)
check("m3不足提示", r4.get('m3', {}).get('available') is False)
r4b = fe.compute_period_returns([], [], 'index_point', 'us_equity')
check("空序列整体不可用", r4b.get('available') is False)

# 场景E: m1/m3/m6日历月锚定(会话收敛)
r5 = fe.compute_period_returns(ds_a, vs_a, 'index_point', 'us_equity', as_of='2026-10-16')
check("m3基准=7月中最后观测", r5['m3']['basis_date'].startswith('2026-07'), str(r5['m3'].get('basis_date')))
check("每个返回记录附公式", 'formula' in r5['week'] and 'formula' in r5['ytd'])
check("窗口附预期交易时段数", r5['week'].get('expected_sessions', 0) >= 4)

# 场景F: A股日历(国庆长假跳过,周窗口跨节正确)
def f_cn(d, i):
    if d < date(2026, 9, 25):
        return 3000.0
    if d <= date(2026, 9, 30):
        return 3100.0
    return 3300.0  # 节后10-09起
ds_f, vs_f = synth_daily('2026-08-01', 50, f_cn, calendar='cn')
# as_of=10-09: 该ISO周(10-05起)的基准=长假前最后真实交易日09-30(3100),周变化=3300/3100−1
r6 = fe.compute_period_returns(ds_f, vs_f, 'index_point', 'cn', as_of='2026-10-09')
check("A股国庆周基准=节前最后交易日(09-30)",
      r6['week']['basis_date'] == '2026-09-30' and r6['week']['basis_value'] == 3100.0,
      f"got {r6['week'].get('basis_date')}/{r6['week'].get('basis_value')}")
check("长假周收益率标注窗口实际日期", 'window' in r6['week'])

# ══ [3] 规范化(真实收盘锚点) ═════════════════════════════════════
print("\n[3] 采集JSON规范化 — REAL 2026-10-16已核验收盘锚点")
AS_OF = "2026-10-17T08:00:00+08:00"
gdata = {"time": "07:12:00", "data": {
    "SPX": {"close": 7659.44, "date": "2026-10-16"},
    "GOLD": {"close": 4300.0, "date": "2026-10-16"},          # 旧资产名→GOLD_F映射
    "WTI": {"close": 99.04, "date": "2026-10-16"},
    "JPY=X": {"close": 155.0, "date": "2026-10-16"},           # →USDJPY
    "UNKNOWN_X": {"close": 1.0, "date": "2026-10-16"},         # 未注册→FAIL
}}
gf = fe.normalize_global(gdata, AS_OF, "global_20261017.json")
gby = {f.get('metric_id'): f for f in gf}
check("SPX事实含REAL收盘7659.44", gby['SPX']['value'] == 7659.44 and gby['SPX']['unit'] == 'index_point')
check("旧名GOLD→GOLD_F身份映射", 'GOLD_F' in gby and gby['GOLD_F']['display_name'].startswith('COMEX黄金期货'))
check("JPY=X→USDJPY且标注方向语义", 'USDJPY' in gby and '美元升值' in gby['USDJPY']['calc'])
check("未注册资产判FAIL(identity)", gby['UNKNOWN_X']['quality_status'] == 'FAIL'
      and any(i['category'] == 'identity' for i in gby['UNKNOWN_X']['issues']))
check("事实绑定as_of", all(f.get('as_of') == AS_OF for f in gf[:2]))

mdata = {"data": {
    "UST_10Y": {"value": 4.28, "date": "2026-10-16", "frequency": "daily"},
    "BEI_10Y": {"value": 2.31, "date": "2026-10-16", "frequency": "daily"},
    "CPI": {"value": 322.1, "date": "2026-09-01", "frequency": "monthly"},
    "ICSA": {"value": 260000, "date": "2026-10-10", "frequency": "weekly"},
}}
mf = fe.normalize_macro(mdata, AS_OF, "macro_20261017.json")
mby = {f.get('metric_id'): f for f in mf}
check("CPI月频事实带发布语义披露", 'release_note' in mby['CPI'] and '10月发布属正常' in mby['CPI']['release_note'])
check("月频观测滞后不判错(9月观测10月研究)", mby['CPI']['quality_status'] == 'PASS', str(mby['CPI']['issues']))

# china成交额口径(§4.5)
cdata = {"indices": {"上证指数": {"close": 3716.28, "date": "2026-10-16"},
                      "深证成指": {"close": 11800.0, "date": "2026-10-16"},
                      "恒生指数": {"close": 24186.83, "date": "2026-10-16", "via": "tencent"}},
         "ah_premium": {"close": 128.56, "date": "2026-10-16"},
         "turnover": {"date": "20261016", "sh_amount_billion": 8000.0, "sz_amount_billion": 9000.0,
                      "total_amount_billion": 17000.0, "scope": "沪深两市"}}
cf = fe.normalize_china(cdata, AS_OF, "china_20261017.json")
cby = {f.get('metric_id'): f for f in cf}
check("沪/深成交额拆分为两指标", 'SH_AMOUNT' in cby and 'SZ_COMPONENT_AMOUNT' in cby)
check("深证成指成分口径被WARN标注(非深市)", cby['SZ_COMPONENT_AMOUNT']['quality_status'] in ('PASS', 'WARN')
      and any('成分' in i.get('message', '') for i in cby['SZ_COMPONENT_AMOUNT']['issues']), str(cby['SZ_COMPONENT_AMOUNT']['issues']))
check("两市合计标近似口径", any('近似' in i.get('message', '') for i in cby['CN_TOTAL_TURNOVER']['issues']))
check("akshare降级仅沪市→DEGRADED披露",
      (lambda f: f and f['quality_status'] == 'DEGRADED')(
          next(iter(fe.normalize_china(
              {"turnover": {"date": "20261016", "total_amount_billion": 8000.0}}, AS_OF)), None)))

# ══ [4] 派生指标 ══════════════════════════════════════════════════
print("\n[4] 派生计算(期限匹配/质量传导)")
facts_all = gf + mf + cf
derived = fe.compute_derived(facts_all, AS_OF)
dby = {f['metric_id']: f for f in derived}
check("REAL_10Y=4.28−2.31=1.97", dby.get('REAL_10Y', {}).get('value') == 1.97, str(dby.get('REAL_10Y')))
check("REAL_10Y附公式与期限说明", '期限匹配' in dby['REAL_10Y']['calculation_ref'])
check("REAL_SHORT不再由引擎产出", 'REAL_SHORT' not in dby)
check("输入缺失时REAL_5Y不产(无UST_5Y)", 'REAL_5Y' not in dby)
check("ZQ价格存在时产隐含日均利率",
      (lambda: (facts_all.extend([{'metric_id': 'ZQ_F1_PRICE', 'value': 95.5, 'observation_date': '2026-10-16', 'quality_status': 'PASS'}]),
                'ZQ_IMPLIED_AVG' in {f['metric_id'] for f in fe.compute_derived(facts_all, AS_OF)})[1])())

# 质量传导
gf_bad = fe.normalize_global({"data": {"UST_10Y": {"close": 99.9, "date": "2026-10-16"}}}, AS_OF)
gf_bei = fe.normalize_global({"data": {"BEI_10Y": {"close": 2.31, "date": "2026-10-14"}}}, AS_OF)
dbad = fe.compute_derived(gf_bad + gf_bei, AS_OF)
rbad = next((f for f in dbad if f['metric_id'] == 'REAL_10Y'), None)
check("输入FAIL(区间外)→派生FAIL传导", rbad is not None and rbad['quality_status'] == 'FAIL',
      str(rbad and rbad['issues']))

# ══ [5] 12类校验 ═════════════════════════════════════════════════
print("\n[5] 校验规则(时间/离群/发布限制)")
f_fut = fe.normalize_global({"data": {"SPX": {"close": 7700.0, "date": "2026-10-20"}}}, AS_OF)
check("未来观测日→FAIL(time)", f_fut[0]['quality_status'] == 'FAIL'
      and any(i['category'] == 'time' for i in f_fut[0]['issues']))
f_rng = fe.normalize_global({"data": {"SPX": {"close": 99999.0, "date": "2026-10-16"}}}, AS_OF)
check("超区间→FAIL(outlier)", f_rng[0]['quality_status'] == 'FAIL'
      and any(i['category'] == 'outlier' for i in f_rng[0]['issues']))
# 月频当月月初观测→release-limit WARN
m_early = fe.normalize_macro({"data": {"UNEMPLOYMENT": {"value": 4.1, "date": "2026-10-01", "frequency": "monthly"}}},
                             "2026-10-05T08:00:00+08:00")
check("当月月初月频观测→发布限制WARN", any(i['category'] == 'release-limit' for i in m_early[0]['issues']),
      str(m_early[0]['issues']))
# 周变动超限→DEGRADED(序列驱动)
big = fe.normalize_global({"data": {"SPX": {"close": 9000.0, "date": "2026-10-16",
    "series": {"dates": ['2026-10-08', '2026-10-09', '2026-10-12', '2026-10-13', '2026-10-14', '2026-10-15', '2026-10-16'],
                "values": [7000, 7000, 7000, 7000, 7000, 7000, 9000]}}}}, AS_OF)
check("周跳变超25%→DEGRADED(outlier须复核)", big[0]['quality_status'] == 'DEGRADED'
      and any('超阈值' in i.get('message', '') for i in big[0]['issues']))

# ══ [6] 跨指标与对账 ═════════════════════════════════════════════
print("\n[6] 跨指标逻辑与来源对账")
batch = fe.normalize_global({"data": {"WTI": {"close": 99.04, "date": "2026-10-16"},
                                       "HY_OAS": {"close": 4.5, "date": "2026-10-16"}}}, AS_OF) + mf + cf
batch += [{"metric_id": "DFEDTARL", "value": 4.75, "observation_date": "2026-10-16", "quality_status": "PASS"},
          {"metric_id": "DFEDTARU", "value": 4.50, "observation_date": "2026-10-16", "quality_status": "PASS"},
          {"metric_id": "IG_OAS", "value": 5.2, "observation_date": "2026-10-16", "quality_status": "PASS"},
          {"metric_id": "TIPS_10Y", "value": 1.95, "observation_date": "2026-10-16", "quality_status": "PASS"},
          {"metric_id": "WTI_SPOT_M", "value": 97.0, "observation_date": "2026-09-01", "quality_status": "PASS"}]
batch += fe.compute_derived(batch, AS_OF)   # 产REAL_10Y供对账
recon = fe.cross_metric_checks(batch)
rc = {r['check']: r for r in recon}
check("目标区间下限>上限被拦截", rc.get('目标区间次序', {}).get('result') == 'violation')
check("IG>HY评级-利差次序被拦截", rc.get('评级-利差次序', {}).get('result') == 'violation')
check("REAL_10Y vs TIPS_10Y对账记录", 'REAL_10Y' in rc.get('REAL_10Y(名义−BEI) vs TIPS_10Y(市场)', {}).get('check', ''))
check("WTI期货vs现货口径差异披露不判错", rc.get('WTI_F(期货日频) vs WTI_SPOT_M(现货月均)', {}).get('result') == 'info')

# ══ [7] 快照分级 ═════════════════════════════════════════════════
print("\n[7] 快照整体分级")
g9 = fe.snapshot_quality_grade(gf)
check("core缺失可识别(SPX在但NDX/VIX等缺)", 'NDX' in g9['missing_core'] or 'VIX' in g9['missing_core'],
      str(g9['missing_core'][:5]))
g10 = fe.snapshot_quality_grade(gf + mf + cf + derived)
check("无注册表active FAIL(仅未注册UNKNOWN_X诊断)→overall=PASS(诊断不冒充研究事实)",
      g10['overall'] == 'PASS')
# FIX4-01: 注册表active指标的合法FAIL照旧计入分级(未注册FAIL诊断不计)
umc_fail = fe.normalize_macro({"data": {"UMCSENT": {"value": "N/A", "date": "2026-09-01",
                                                    "frequency": "monthly"}}},
                              AS_OF, "macro_20261017.json")
g11 = fe.snapshot_quality_grade(gf + mf + cf + derived + umc_fail)
check("含FAIL→整体DEGRADED以上(注册指标合法FAIL计入)", g11['overall'] in ('DEGRADED', 'FAIL'))

# ══ [8] build_all一站式 ══════════════════════════════════════════
facts, recon = fe.build_all(global_data=gdata, macro_data=mdata, china_data=cdata, as_of=AS_OF)
check("build_all汇合三类采集", len(facts) >= 10 and len(recon) >= 0)
check("全部事实有quality_status", all(isinstance(f, dict) and f.get('quality_status') for f in facts))

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
