# -*- coding: utf-8 -*-
"""Audit-R20 真实面冒烟: 引擎树(/tmp/r20_real)重建快照后,以截止
2026-11-18 复现验收指令回归锚+12组36格+CN PMI+VIX 月窗+三利率分解。
只读真实采集档,零写入 LIVE。"""
import json
import os
import sys

ROOT = '/tmp/r20_real'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import research_map_planner as rmp   # noqa: E402
import snapshot_builder as sb        # noqa: E402
import workbench_data as wd          # noqa: E402

Q = ('给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、'
     '3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年'
     '最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制'
     '是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，'
     '当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？')

fails = []


def ck(name, ok, detail=''):
    print(('  ✅ ' if ok else ' ❌ ') + name + (f' — {str(detail)[:170]}' if detail else ''))
    if not ok:
        fails.append(name)


dd = os.path.join(ROOT, 'data', 'daily')
sb.build_snapshot(target_ymd='20261119', data_dir=dd, out_dir=dd,
                  as_of='2026-11-19T09:30:00+08:00', trusted_root=ROOT)
snap = json.load(open(os.path.join(dd, 'research_snapshot_20261119.json')))
ss = snap.get('series_store') or {}
need = ['JP_CPI_YOY', 'JP_CPI_TOKYO_YOY', 'JP_REAL_GDP_YOY', 'EA_HICP_YOY',
        'EA_REAL_GDP_YOY', 'ECB_MRO', 'ECB_DFR', 'CN_CPI_YOY', 'CN_PPI_YOY',
        'CN_OMO_7D', 'CN_LPR_1Y', 'DFEDTARU', 'DFEDTARL', 'SHCOMP', 'VIX',
        'SPX', 'JP_POLICY_RATE']
ck('快照 series_store 携带 R20 全部新指标+资产序列',
   all(k in ss for k in need),
   str([k for k in need if k not in ss]))

reg = wd.load_registry(ROOT)
plan = rmp.plan_map(Q, {'economies': ['US', 'CN', 'EA', 'JP']},
                    reg.get('by_id') or {}, '2026-11-18')
pv = rmp.point_values(plan, snap, ROOT)
cells = {(c['region'], c['dimension'], c['metric_id']): c
         for c in pv.get('cells') or []}
gdp = (cells.get(('US', 'growth', 'US_REAL_GDP')) or {}).get('anchors') or {}
ck('回归锚①: 2025-11-18 美国只见 Q2 GDP(obs 2025-04-01;Q3 停摆 11-19 首发)',
   (gdp.get('12个月前') or {}).get('observation_date') == '2025-04-01',
   json.dumps(gdp.get('12个月前'), ensure_ascii=False)[:150])
une = (cells.get(('US', 'growth', 'UNEMPLOYMENT')) or {}).get('anchors') or {}
u12 = une.get('12个月前') or {}
ck('回归锚②: 12个月前失业率=8月 4.3(9月停摆被日历排除)',
   u12.get('observation_date') == '2025-08-01' and u12.get('value') == 4.3,
   json.dumps(u12, ensure_ascii=False)[:150])
ok_m = {}
for c in pv.get('cells') or []:
    for lbl, a in (c.get('anchors') or {}).items():
        if a.get('status') == 'ok':
            ok_m.setdefault((c['region'], c['dimension']), set()).add(lbl)
planned = {(e, d) for e in ('US', 'CN', 'EA', 'JP')
           for d in ('growth', 'inflation', 'policy')}
full = {k for k, v in ok_m.items()
        if v == {'12个月前', '3个月前', '最新一期'}}
ck('12组×3锚全 ok(36 时点格)', planned <= full,
   '缺: ' + str(sorted(planned - full)))
s, _e = wd.metric_series('CN_PMI_MFG', root=ROOT)
mm = dict(zip(s['dates'], s['values']))
ck('CN PMI: 2026-05=50.0 / 2026-09=50.1',
   mm.get('2026-05-01') == 50.0 and mm.get('2026-09-01') == 50.1,
   f"05={mm.get('2026-05-01')} 09={mm.get('2026-09-01')}")
trio = rmp.us_rates_trio_face(snap, ROOT)
chg = trio.get('chg_bp') or {}
_res = trio.get('identity_residual_bp')
ck('三利率共同交易日分解 ok(名义=实际+盈亏平衡+残差)',
   trio.get('status') == 'ok'
   and _res is not None
   and abs((chg.get('UST_10Y') or 0) - (chg.get('TIPS_10Y') or 0)
           - (chg.get('BEI_10Y') or 0) - _res) < 1e-6
   and abs(_res) < 2.0,
   json.dumps(trio, ensure_ascii=False)[:190])
am = rmp.asset_move_face(snap, ROOT, cutoff='2026-11-18')
vix = next((x for x in am.get('rows') or []
            if x.get('metric_id') == 'VIX'), {})
ck('VIX 月涨幅+计算窗口(读者可核)',
   vix.get('chg_pct') is not None and (vix.get('window') or {}).get('from'),
   json.dumps(vix, ensure_ascii=False))
dfed = (cells.get(('US', 'policy', 'DFEDTARU')) or {})
pdt = ((dfed.get('anchors') or {}).get('最新一期') or {}).get('policy_dates') or {}
ck('政策三日期(DFEDTARU 决议=生效=观测日)',
   pdt.get('decision') and pdt.get('decision') == pdt.get('effective'),
   json.dumps(pdt, ensure_ascii=False)[:140])
print('\n冒烟判定: %d PASS / %d FAIL' % (7 - len(fails), len(fails)))
sys.exit(1 if fails else 0)
