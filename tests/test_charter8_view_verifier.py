#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Charter8 观点确定性验证器测试(交付③)——合成快照/注册表/映射,零网络。

锁面:
① 窗口起点: horizon_start 自然月回退(月末钳制/闰年/1y/5y)
② 证据表: 快照事实+interval_change 区间变动(与 compare 自配对同一实现,
   workbench_data.metric_window_changes 唯一口径处);单位族分桶随 unit
③ 方向关系: 仅显式 directions 机械计算(supports/against/neutral);
   未传=不做语义判断;directions 映射外指标→notes 披露不越权
④ 缺席如实: 无事实→missing+原因;无序列→available=False 不回退 0
⑤ 隔离件 verify 拒绝(view_store 联动)
⑥ 映射完整性: 真实 view_metric_map.json 全部 id 在真实注册表且 active
"""
import json
import os
import sys
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


import workbench_data as wd  # noqa: E402
import view_verifier as vv   # noqa: E402

print("═" * 60)
print("[1] horizon_start 自然窗起点")
print("═" * 60)
check("20261110 1m→2026-10-10", wd.horizon_start('20261110', '1m') == '2026-10-10')
check("20261110 3m→2026-08-10", wd.horizon_start('20261110', '3m') == '2026-08-10')
check("20261110 1y→2025-11-10", wd.horizon_start('20261110', '1y') == '2025-11-10')
check("20261110 5y→2021-11-10", wd.horizon_start('20261110', '5y') == '2021-11-10')
check("月末钳制 20260331 −1m→2026-02-28", wd.horizon_start('20260331', '1m') == '2026-02-28')
check("闰日锚 20240229 1y→2023-02-28", wd.horizon_start('20240229', '1y') == '2023-02-28')
try:
    wd.horizon_start('20261110', '7m')
    check("未知窗口 raise", False)
except ValueError:
    check("未知窗口 raise", True)

# ── 合成注册表/映射/快照(结构对照真实引擎;数值刻意中性) ──────────────
SYN_REG = {'metrics': [
    {'metric_id': 'SPX', 'display_name': '标普500', 'unit': 'index_point',
     'status': 'active', 'asset_class': 'equity_index', 'economy': 'US',
     'source': 'synthetic'},
    {'metric_id': 'UST_10Y', 'display_name': '美债10年', 'unit': 'percent',
     'status': 'active', 'asset_class': 'rate', 'economy': 'US',
     'source': 'synthetic'},
    {'metric_id': 'NFP', 'display_name': '非农就业', 'unit': 'thousands',
     'status': 'active', 'asset_class': 'macro', 'economy': 'US',
     'source': 'synthetic'},
    {'metric_id': 'DEAD_METRIC', 'display_name': '已退役', 'unit': 'index_point',
     'status': 'deprecated', 'asset_class': 'equity_index', 'economy': 'US',
     'source': 'synthetic'},
    {'metric_id': 'DXY', 'display_name': '美元指数', 'unit': 'index_point',
     'status': 'active', 'asset_class': 'fx_index', 'economy': 'US',
     'source': 'synthetic'},
], 'by_id': {}}
SYN_REG['by_id'] = {m['metric_id']: m for m in SYN_REG['metrics']}

SYN_MAP = {'schema_version': '1.0', 'subjects': {
    'US_growth': {'note': '合成', 'metrics': ['SPX', 'UST_10Y', 'NFP', 'DEAD_METRIC']},
    'fx': {'note': '合成空subject(映射在册但快照零事实→missing)', 'metrics': ['DXY']},
}}


def day(i):
    import datetime
    return (datetime.date(2025, 11, 10) + datetime.timedelta(days=i)).isoformat()


# 基准日 2025-11-09(严格早于 1y 窗起点 2025-11-10)→ 年内 +10%/+0.5pp
DATES = [day(i) for i in range(-1, 365)]         # 2025-11-09 → 2026-11-09
LEVELS = [100.0 + 10.0 * (i + 1) / 365 for i in range(-1, 365)]
RATES = [4.0 + 0.5 * (i + 1) / 365 for i in range(-1, 365)]

SYN_SNAP = {
    'snapshot_id': 'research_snapshot_20261110_syn', 'target_date': '20261110',
    'research_as_of': '2026-11-10T20:00:00+08:00',
    'gate_a': {'status': 'DEGRADED', 'noncore_missing': ['DXY'],
               'noncore_missing_detail': {'DXY': '来源断连(合成)'}},
    'facts': [
        {'metric_id': 'SPX', 'display_name': '标普500', 'value': 110.0,
         'unit': 'index_point', 'observation_date': '2026-11-10',
         'quality_status': 'PASS'},
        {'metric_id': 'UST_10Y', 'display_name': '美债10年', 'value': 4.5,
         'unit': 'percent', 'observation_date': '2026-11-10',
         'quality_status': 'PASS'},
    ],
    'series_store': {
        'SPX': {'dates': DATES, 'values': LEVELS},
        'UST_10Y': {'dates': DATES, 'values': RATES},
    },
}

print("═" * 60)
print("[2] 证据表: 事实+区间变动+单位族(合成快照直算)")
print("═" * 60)
with tempfile.TemporaryDirectory() as td:
    tab = vv.metric_evidence_table(['US_growth', 'fx'], SYN_SNAP, SYN_REG, SYN_MAP)
    ev = {e['metric_id']: e for e in tab['evidence']}
    check("SPX 证据行在场", 'SPX' in ev)
    spx = ev['SPX']
    check("SPX 单位族=price", spx['unit_family'] == 'price')
    y1 = spx['changes']['1y']
    check("SPX 1y pct≈+10%(interval_change 同链路)",
          abs(y1['pct_change'] - 10.0) < 0.05, str(y1))
    u = ev['UST_10Y']
    check("UST_10Y 单位族=rate", u['unit_family'] == 'rate')
    check("UST_10Y 1y pp≈+0.5", abs(u['changes']['1y']['pp_change'] - 0.5) < 0.005,
          str(u['changes']['1y']))
    check("1m/3m 窗口键齐备", all(h in spx['changes'] for h in ('1m', '3m')))
    miss = {m['metric_id']: m for m in tab['missing']}
    check("NFP 无事实→missing(默认原因如实)", 'NFP' in miss
          and miss['NFP']['reason'] == '快照无该指标事实', str(miss.get('NFP')))
    check("DEAD_METRIC 非active→missing(映射完整性联动)", 'DEAD_METRIC' in miss)
    check("DXY(映射在册零事实)→missing+Gate A 明细原因", 'DXY' in miss
          and '断连' in miss['DXY']['reason'], str(miss.get('DXY')))

print("═" * 60)
print("[3] 方向关系: 显式 directions 机械计算")
print("═" * 60)
with tempfile.TemporaryDirectory() as td:
    tab = vv.metric_evidence_table(
        ['US_growth', 'fx'], SYN_SNAP, SYN_REG, SYN_MAP,
        directions={'SPX': 'up', 'UST_10Y': 'down', 'DXY': 'up', 'NFP': 'up'})
    ev = {e['metric_id']: e for e in tab['evidence']}
    check("SPX 上涨 hint 与 +10% 同向→supports",
          ev['SPX']['relation'] == 'supports', ev['SPX']['relation_note'])
    check("UST_10Y 下跌 hint 与 +0.5pp 反向→against",
          ev['UST_10Y']['relation'] == 'against')
    check("无序列指标(DXY 映射外/missing)不入证据表→relation 缺席即未机械判断",
          'DXY' not in ev and 'NFP' not in ev)
    check("directions 指标缺席→notes 披露未判方向(如实)",
          any('DXY' in n or 'NFP' in n for n in tab['notes']), str(tab['notes']))
    tab2 = vv.metric_evidence_table(['US_growth'], SYN_SNAP, SYN_REG, SYN_MAP)
    check("未传 directions→relation=None+零语义判断",
          all(e['relation'] is None for e in tab2['evidence'])
          and all('归 Agent' in e['relation_note'] for e in tab2['evidence']))

print("═" * 60)
print("[4] verify 全链 + 隔离件拒绝(view_store 联动)")
print("═" * 60)
GOOD_VIEW = {
    'schema_version': '1.1', 'view_id': 'VIEW-20261110-001',
    'institution': {'name': 'Synthetic Bank', 'type': 'investment_bank',
                    'department': 'Research'},
    'authors': [], 'report_title': 'Syn', 'source_url': 'https://example.com/x',
    'source_type': 'official_site', 'publish_date': '2026-11-01',
    'fetch_date': '2026-11-10', 'access_level': 'public_full',
    'view_horizon': '6m', 'subjects': ['US_growth'],
    'core_views': [{'statement': '看多。', 'attribution': 'institution_stated',
                    'basis': 'paraphrase'}],
    'forecasts': [], 'key_assumptions': [], 'evidence_cited': [],
    'mechanism_steps': [], 'risk_factors': [], 'falsification_conditions': [],
    'revisions': [], 'completeness_notes': '合成', 'copyright_note': 'meta+link',
}
BAD_VIEW = dict(GOOD_VIEW, schema_version='1.0', view_id='VIEW-20261110-002')
with tempfile.TemporaryDirectory() as td:
    for doc in (GOOD_VIEW, BAD_VIEW):
        with open(os.path.join(td, doc['view_id'] + '.json'), 'w',
                  encoding='utf-8') as f:
            json.dump(doc, f, ensure_ascii=False)
    out = vv.verify('VIEW-20261110-001', SYN_SNAP, SYN_REG, SYN_MAP, views_dir=td,
                    directions={'SPX': 'up'})
    check("verify ok=True(隔离件不入装载面)", out['ok'] is True)
    check("信封: 机构/发布日/快照/Gate A 随行",
          out['institution'] == 'Synthetic Bank' and out['publish_date'] == '2026-11-01'
          and out['snapshot_id'] == SYN_SNAP['snapshot_id']
          and out['gate_a'] == 'DEGRADED')
    check("n_supports=1(SPX) n_against=0", out['n_supports'] == 1
          and out['n_against'] == 0)
    check("missing 2 项如实(NFP/DEAD_METRIC;view subjects=US_growth 不含 fx→DXY 不入面)",
          out['n_missing'] == 2, str(out['n_missing']))
    check("零 AI 判断声明随行", '零 AI 判断' in out['determinism_note'])
    out2 = vv.verify('VIEW-20261110-002', SYN_SNAP, SYN_REG, SYN_MAP, views_dir=td)
    check("隔离件 verify 拒绝(kind=view_not_found_or_quarantined)",
          out2['ok'] is False and out2['error']['kind'] == 'view_not_found_or_quarantined')

print("═" * 60)
print("[5] 映射完整性(真实文件): 全部 id 在真实注册表且 active")
print("═" * 60)
real_map = json.load(open(os.path.join(ROOT, 'config', 'view_metric_map.json'),
                          encoding='utf-8'))
real_reg = wd.load_registry(ROOT)
bad = []
n_ids = 0
for subj, spec in real_map['subjects'].items():
    check_ids = spec.get('metrics', [])
    check(f"subject {subj} 映射非空", len(check_ids) > 0)
    n_ids += len(check_ids)
    for mid in check_ids:
        m = real_reg['by_id'].get(mid)
        if m is None or m.get('status') != 'active':
            bad.append(f"{subj}:{mid}")
check(f"全部映射 id({n_ids} 个)在注册表且 active", not bad, str(bad))
check("11 主题齐备(章程 subject 枚举)",
      sorted(real_map['subjects']) == sorted(vv_vs := [
          'US_rates', 'US_growth', 'CN_macro', 'EA_macro', 'JP_macro', 'HK_macro',
          'equities', 'fixed_income', 'fx', 'commodities', 'credit']))

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
