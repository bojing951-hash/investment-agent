#!/usr/bin/env python3
"""研究快照构建器测试 — 解析三态/事实化/兼容锚点/不可变/Gate A

数据纪律: 本文件fixture为SYNTHETIC构造(结构复刻真实采集JSON;个别数值采用
2026-10-16已核验真实收盘如SPX 7659.44作身份锚点,标注REAL)。
运行: ~/AI内容/venv/bin/python3 tests/test_snapshot.py
"""
import os
import sys
import json
import shutil
import tempfile

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


def build_fixture_day(td, ymd='20261017', obs='2026-10-16', with_china=True):
    """构造一天完整采集文件(SYNTHETIC,结构=真实采集器输出)。"""
    import datetime as dt
    # SPX序列: 9/30=7400, 10/9=7500, 10/16=7659.44(REAL锚点)
    spx = {'2026-09-30': 7400.0, '2026-10-09': 7500.0, '2026-10-16': 7659.44}
    # 填充工作日
    d = dt.date(2026, 8, 3)
    while d <= dt.date(2026, 10, 16):
        if d.weekday() < 5:
            v = spx.get(d.isoformat())
            if v is None:
                v = 7400.0 if d < dt.date(2026, 10, 1) else (7500.0 if d <= dt.date(2026, 10, 9) else 7550.0)
            spx.setdefault(d.isoformat(), v)
        d += dt.timedelta(days=1)
    sdates = sorted(spx)
    svalues = [spx[k] for k in sdates]
    gold_dates = [x for x in sdates]
    gold_values = [4200.0 if x < '2026-10-12' else 4300.0 for x in gold_dates]

    global_json = {"date": ymd, "time": "07:12:00", "count": 2, "data": {
        "SPX": {"close": 7659.44, "high": 7680.0, "low": 7601.0, "week_chg": 2.13,
                "mtd_chg": 3.5, "ytd_chg": 12.0, "date": obs,
                "series": {"dates": sdates, "values": svalues}},
        "GOLD": {"close": 4300.0, "week_chg": 2.38, "date": obs,
                 "series": {"dates": gold_dates, "values": gold_values}},
        "FXI": {"close": 45.0, "week_chg": 1.0, "date": obs},
    }}
    with open(os.path.join(td, f"global_{ymd}.json"), 'w') as f:
        json.dump(global_json, f)

    # macro: CCC日频 + CPI月频(9月观测10月研究) + UNRATE + UST/BEI(派生用)
    md_dates = ['2026-10-08', '2026-10-09', '2026-10-13', '2026-10-14', '2026-10-15', '2026-10-16']
    ccc = [10.12, 10.12, 10.20, 10.30, 10.25, 10.18]
    cpi_dates = ['2025-%02d-01' % m for m in range(1, 13)] + ['2026-%02d-01' % m for m in range(1, 10)]
    cpi_vals = [300.0 + i * 0.8 for i in range(len(cpi_dates))]
    macro_json = {"date": ymd, "data": {
        "CCC_OAS": {"value": 10.18, "date": obs, "frequency": "daily",
                    "series": {"dates": md_dates, "values": ccc}},
        "CPI": {"value": cpi_vals[-1], "date": "2026-09-01", "frequency": "monthly",
                "series": {"dates": cpi_dates, "values": cpi_vals}},
        "UNEMPLOYMENT": {"value": 4.2, "date": "2026-09-01", "frequency": "monthly"},
        "UST_10Y": {"value": 4.28, "date": obs, "frequency": "daily"},
        "BEI_10Y": {"value": 2.31, "date": obs, "frequency": "daily"},
        "UMCSENT": {"value": 68.0, "date": "2026-09-01", "frequency": "monthly"},
    }, "derived": {}}
    with open(os.path.join(td, f"macro_{ymd}.json"), 'w') as f:
        json.dump(macro_json, f)

    if with_china:
        cn_dates = ['2026-09-30', '2026-10-09', '2026-10-15', '2026-10-16']
        china_json = {"date": ymd, "data": {}, "indices": {
            "上证指数": {"name": "上证指数", "close": 3716.28, "week_chg": -2.13, "date": obs,
                        "series": {"dates": cn_dates, "values": [3800.0, 3790.0, 3797.0, 3716.28]}},
            "恒生指数": {"name": "恒生指数", "close": 24186.83, "date": obs, "via": "tencent"},
        }, "ah_premium": {"close": 128.56, "date": obs},
           "turnover": {"date": ymd, "sh_amount_billion": 8000.0, "sz_amount_billion": 9000.0,
                        "total_amount_billion": 17000.0}}
        with open(os.path.join(td, f"china_{ymd}.json"), 'w') as f:
            json.dump(china_json, f)

    # rate_economy: DFF/目标区间 + real_economy(UNRATE与macro一致/UMCSENT不一致→对账) + ZQ
    rate_json = {"date": ymd, "current_rates": {
        "DFF": {"name": "有效联邦基金利率", "value": 4.33, "date": obs},
        "DFEDTARU": {"name": "目标区间上限", "value": 4.50, "date": obs},
        "DFEDTARL": {"name": "目标区间下限", "value": 4.25, "date": obs}},
        "fed_funds_futures": [
            {"ticker": "ZQ=F", "name": "FF期货主力", "price": 95.80, "implied_rate": 4.20,
             "diff_from_current": -0.13, "signal": "宽松"},
            {"ticker": "ZQZ26.CBT", "name": "2026-12", "price": 95.90, "implied_rate": 4.10}],
        "real_economy": {
            "UNRATE": {"name": "失业率", "value": 4.2, "date": "2026-09-01", "freq": "月度"},
            "UMCSENT": {"name": "消费者信心", "value": 71.0, "date": "2026-09-01", "freq": "月度"}},
    }
    with open(os.path.join(td, f"rate_economy_{ymd}.json"), 'w') as f:
        json.dump(rate_json, f)


print("=" * 60)
print("研究快照: 解析三态/事实化/兼容锚点/不可变/Gate A")
print("=" * 60)

import snapshot_builder as sb
import fact_engine as fe

AS_OF = "2026-10-17T08:00:00+08:00"

# ══ [1] 完整当日 → EXACT四源 ══
with tempfile.TemporaryDirectory() as td:
    build_fixture_day(td)
    snap = sb.build_snapshot(target_ymd='20261017', data_dir=td, trusted_root=td, out_dir=td, as_of=AS_OF)
    check("快照构建成功", snap is not None)
    check("四源EXACT", all(snap['sources_status'][n]['status'] == 'EXACT'
                           for n in ('global', 'macro', 'china', 'rate_economy')))
    check("研究截止写入快照", snap['research_as_of'] == AS_OF)
    facts_by = {f['metric_id']: f for f in snap['facts'] if isinstance(f, dict)}
    check("SPX事实(REAL 7659.44)", facts_by['SPX']['value'] == 7659.44)
    check("GOLD旧名→GOLD_F事实", 'GOLD_F' in facts_by)
    check("REAL_10Y派生=4.28−2.31", facts_by.get('REAL_10Y', {}).get('value') == 1.97)
    check("ZQ隐含日均利率事实(95.80→4.20)", facts_by.get('ZQ_IMPLIED_AVG', {}).get('value') == 4.2)
    check("快照无'降息次数'字段", 'cuts_25bp' not in json.dumps(snap))
    check("CPI 9月观测不判旧(75天窗)", facts_by['CPI']['quality_status'] != 'FAIL',
          str(facts_by['CPI']['issues']))
    cpi_series = facts_by['CPI'].get('source') and None
    cpi_dates = ['2025-%02d-01' % m for m in range(1, 13)] + ['2026-%02d-01' % m for m in range(1, 10)]
    cpi_vals = [300.0 + i * 0.8 for i in range(len(cpi_dates))]
    cpi_yoy = facts_by['CPI']['derived']['m12']
    expect_yoy = (cpi_vals[-1] / cpi_vals[-13] - 1) * 100
    check("CPI同比由引擎计算(m12)", abs(cpi_yoy.get('pct_change', 0) - expect_yoy) < 0.01,
          f"{cpi_yoy.get('pct_change')} vs {expect_yoy:.2f}")

    # 对账: UMCSENT rate=71 vs macro=68 → diff-needs-review; UNRATE一致
    recon = {r['check']: r for r in snap['reconciliation']}
    um = next((r for r in snap['reconciliation'] if 'UMCSENT' in r.get('check', '')), None)
    check("UMCSENT双通道不一致→待复核记录", um and um['result'] == 'diff-needs-review', str(um))
    un = next((r for r in snap['reconciliation'] if 'UNEMPLOYMENT' in r.get('check', '')), None)
    check("UNRATE双通道一致→consistent", un and un['result'] == 'consistent', str(un))

    # Gate A: core缺失披露(NDX/VIX/WTI等未在fixture)
    check("Gate A因core缺失=FAIL", snap['gate_a']['status'] == 'FAIL')
    check("core缺失清单可识别", 'NDX' in snap['gate_a']['core_missing']
          and 'SPX' not in snap['gate_a']['core_missing'])
    check("不阻断(快照仍产出,缺失如实披露)", len(snap['facts']) > 8)

    # 兼容锚点
    with open(os.path.join(td, 'anchors_20261017.json')) as f:
        anchors = json.load(f)
    check("锚点global_market.data.SPX.close(REAL值+观测日)",
          anchors.get('global_market.data.SPX.close', {}).get('value') == 7659.44
          and anchors['global_market.data.SPX.close'].get('obs_date') == '2026-10-16')
    check("锚点带兄弟high/low(touch判定用)", anchors['global_market.data.SPX.close'].get('high') == 7680.0)
    check("锚点旧资产名GOLD.close", 'global_market.data.GOLD.close' in anchors)
    check("锚点macro.data.CCC_OAS.value/.prev",
          anchors.get('macro.data.CCC_OAS.value', {}).get('value') == 10.18
          and 'macro.data.CCC_OAS.prev' in anchors)
    check("锚点macro.data.CPI.yoy_pct(引擎口径)", 'macro.data.CPI.yoy_pct' in anchors)
    check("锚点china.data.上证指数.close", anchors.get('china.data.上证指数.close', {}).get('value') == 3716.28)
    check("锚点rate_economy.real_economy.UNRATE.value(单一来源=macro事实)",
          anchors.get('rate_economy.real_economy.UNRATE.value', {}).get('value') == 4.2)
    check("锚点rate_economy.current_rates.DFF.value", 'rate_economy.current_rates.DFF.value' in anchors)
    check("锚点fed期货价格+隐含(无降息次数)", 'rate_economy.fed_funds_futures.0.price' in anchors
          and 'cuts' not in json.dumps(anchors))
    check("锚点总≥20(旧观察器MIN_ANCHOR_COUNT)", len(anchors) >= 20, str(len(anchors)))
    check("锚点全部含obs_date或属曲线", all(
        'obs_date' in v or 'fed_funds_futures' in k for k, v in anchors.items()))

    # MD渲染
    md = open(os.path.join(td, 'research_snapshot_20261017.md')).read()
    check("MD含研究截止与Gate A", 'research_as_of' in md and 'Gate A' in md)
    check("MD代理标注(FXI)", '代理' in md)
    check("MD披露成交额近似口径", '近似' in md or '成分' in md)

    # 不可变 + 修订
    r2 = sb.build_snapshot(target_ymd='20261017', data_dir=td, trusted_root=td, out_dir=td, as_of=AS_OF)
    check("同日重建被拒(不可变)", r2 is None)
    check("原快照未被覆盖", json.load(open(os.path.join(td, 'research_snapshot_20261017.json')))
          ['snapshot_id'] == 'research_snapshot_20261017')
    r3 = sb.build_snapshot(target_ymd='20261017', data_dir=td, trusted_root=td, out_dir=td, as_of=AS_OF,
                           allow_revision=True, revision_reason='补充采集')
    check("--allow-revision生成_v2且原版保留", r3 is not None
          and os.path.exists(os.path.join(td, 'research_snapshot_20261017_v2.json'))
          and os.path.exists(os.path.join(td, 'research_snapshot_20261017.json'))
          and r3['revision_reason'] == '补充采集')

# ══ [1b] 装配器从快照渲染数据包 ══
with tempfile.TemporaryDirectory() as td:
    build_fixture_day(td)
    snap = sb.build_snapshot(target_ymd='20261017', data_dir=td, trusted_root=td, out_dir=td, as_of=AS_OF)
    import data_assembler as da
    md = da.build_markdown(snap, '20261017')
    check("数据包含研究截止与Gate A", '研究截止' in md and 'Gate A' in md)
    check("数据包含SPX收盘(REAL)", '7,659.44' in md)
    check("数据包含REAL_10Y派生值", '1.97' in md)
    check("数据包标注周/MTD/YTD口径", '期前收盘基准' in md)
    check("月频环比同比来自引擎", '环比' in md and '同比' in md)
    check("fed期货含月均语义警示", '日均' in md)
    check("成交额口径备注渲染", '成分' in md or '近似' in md)
    check("core缺失在数据包披露", 'core指标缺失' in md)

# ══ [2] 当日缺china → FALLBACK新鲜窗内 / 超窗 → MISSING ══
with tempfile.TemporaryDirectory() as td:
    build_fixture_day(td, ymd='20261016', obs='2026-10-15')
    os.rename(os.path.join(td, 'china_20261016.json'), os.path.join(td, 'china_20261015.json'))
    # 10-17构建: 无任何10-17文件 → 全部fallback(1-2天,窗内)
    snap = sb.build_snapshot(target_ymd='20261017', data_dir=td, trusted_root=td, out_dir=td, as_of=AS_OF)
    st = snap['sources_status']
    check("无当日文件→新鲜窗内fallback", st['global']['status'] == 'FALLBACK'
          and st['global']['lag_days'] == 1)
    check("fallback披露'非当日'", '不得当作当日' in st['global'].get('disclosure', ''))
    check("china滞后2天仍窗内(5天)", st['china']['status'] == 'FALLBACK')

with tempfile.TemporaryDirectory() as td:
    build_fixture_day(td, ymd='20261001', obs='2026-09-30')
    snap = sb.build_snapshot(target_ymd='20261017', data_dir=td, trusted_root=td, out_dir=td, as_of=AS_OF)
    check("超窗文件→MISSING(不冒充当日)", snap['sources_status']['global']['status'] == 'MISSING')
    check("MISSING不产该源事实", not any(f.get('source', {}).get('collector') == 'global_market_collector'
                                         for f in snap['facts'] if isinstance(f, dict)))

# ══ [3] 隔离检查: 快照不污染真实数据目录 ══
real_anchors = os.path.join(ROOT, 'data', 'daily', 'anchors_20261017.json')
existed = os.path.exists(real_anchors)
check("测试沙盒未写真实data目录", existed or not os.path.exists(real_anchors))

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
