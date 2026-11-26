| # | 中间表 | 复算点 | 出处(文件+键) | 直算值 | 受审稿值 | 一致 |
|---|---|---|---|---|---|---|
| 1 | 01_cutoff | A1-研究截止日=快照 research_as_of 日期 | root_overlay/data/daily/research_snapshot_20261123.json:research_as_of | True | True | 一致 |
| 2 | 01_cutoff | A1-研究截止日=快照 target_date | root_overlay/data/daily/research_snapshot_20261123.json:target_date | True | True | 一致 |
| 3 | 01_cutoff | A1-快照 series_store 无晚于截止日的观测 | root_overlay/data/daily/research_snapshot_20261123.json:series_store[*].dates | True | True | 一致 |
| 4 | 01_cutoff | A1-SPX 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.SPX.dates | "2026-11-23" | "≤2026-11-23" | 一致 |
| 5 | 01_cutoff | A1-VIX 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.VIX.dates | "2026-11-23" | "≤2026-11-23" | 一致 |
| 6 | 01_cutoff | A1-GOLD_F 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.GOLD_F.dates | "2026-11-23" | "≤2026-11-23" | 一致 |
| 7 | 01_cutoff | A1-DXY 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.DXY.dates | "2026-11-23" | "≤2026-11-23" | 一致 |
| 8 | 01_cutoff | A1-EURUSD 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EURUSD.dates | "2026-11-23" | "≤2026-11-23" | 一致 |
| 9 | 01_cutoff | A1-USDJPY 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.USDJPY.dates | "2026-11-23" | "≤2026-11-23" | 一致 |
| 10 | 01_cutoff | A1-BRENT_F 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F.dates | "2026-11-23" | "≤2026-11-23" | 一致 |
| 11 | 01_cutoff | A1-NIKKEI225 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.NIKKEI225.dates | "2026-11-20" | "≤2026-11-23" | 一致 |
| 12 | 01_cutoff | A1-UST_10Y 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UST_10Y.dates | "2026-11-19" | "≤2026-11-23" | 一致 |
| 13 | 01_cutoff | A1-TIPS_10Y 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y.dates | "2026-11-19" | "≤2026-11-23" | 一致 |
| 14 | 01_cutoff | A1-BEI_10Y 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y.dates | "2026-11-20" | "≤2026-11-23" | 一致 |
| 15 | 01_cutoff | A1-DFEDTARU 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.DFEDTARU.dates | "2026-11-23" | "≤2026-11-23" | 一致 |
| 16 | 01_cutoff | A1-ECB_DFR 截止日前最新观测日 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.ECB_DFR.dates | "2026-09-16" | "≤2026-11-23" | 一致 |
| 17 | 01_cutoff | A2-US_REAL_GDP@2026-04-01 推定发布日 | 规则=期末(2026-06-30)+29天 | "2026-07-29" | "2026-07-29" | 一致 |
| 18 | 01_cutoff | A2-US_REAL_GDP@2026-07-01 推定发布日 | 规则=期末(2026-09-30)+29天 | "2026-10-29" | "2026-10-29" | 一致 |
| 19 | 01_cutoff | A2-UNEMPLOYMENT@2026-07-01 推定发布日 | 规则=期末(2026-07-31)+5天 | "2026-08-05" | "2026-08-05" | 一致 |
| 20 | 01_cutoff | A2-UNEMPLOYMENT@2026-10-01 推定发布日 | 规则=期末(2026-10-31)+5天 | "2026-11-05" | "2026-11-05" | 一致 |
| 21 | 01_cutoff | A2-INDPRO@2026-07-01 推定发布日 | 规则=期末(2026-07-31)+15天 | "2026-08-15" | "2026-08-15" | 一致 |
| 22 | 01_cutoff | A2-INDPRO@2026-10-01 推定发布日 | 规则=期末(2026-10-31)+15天 | "2026-11-15" | "2026-11-15" | 一致 |
| 23 | 01_cutoff | A2-CPI@2026-07-01 推定发布日 | 规则=期末(2026-07-31)+13天 | "2026-08-13" | "2026-08-13" | 一致 |
| 24 | 01_cutoff | A2-CPI@2026-10-01 推定发布日 | 规则=期末(2026-10-31)+13天 | "2026-11-13" | "2026-11-13" | 一致 |
| 25 | 01_cutoff | A2-CORE_CPI@2026-10-01 推定发布日 | 规则=期末(2026-10-31)+13天 | "2026-11-13" | "2026-11-13" | 一致 |
| 26 | 01_cutoff | A2-CORE_PCE@2026-06-01 推定发布日 | 规则=期末(2026-06-30)+30天 | "2026-07-30" | "2026-07-30" | 一致 |
| 27 | 01_cutoff | A2-CORE_PCE@2026-09-01 推定发布日 | 规则=期末(2026-09-30)+30天 | "2026-10-30" | "2026-10-30" | 一致 |
| 28 | 01_cutoff | A2-EA_REAL_GDP_YOY@2026-04-01 推定发布日 | 规则=期末(2026-06-30)+35天 | "2026-08-04" | "2026-08-04" | 一致 |
| 29 | 01_cutoff | A2-EA_REAL_GDP_YOY@2026-07-01 推定发布日 | 规则=期末(2026-09-30)+35天 | "2026-11-04" | "2026-11-04" | 一致 |
| 30 | 01_cutoff | A2-EA_HICP_YOY@2026-07-01 推定发布日 | 规则=期末(2026-07-31)+16天 | "2026-08-16" | "2026-08-16" | 一致 |
| 31 | 01_cutoff | A2-EA_HICP_YOY@2026-10-01 推定发布日 | 规则=期末(2026-10-31)+16天 | "2026-11-16" | "2026-11-16" | 一致 |
| 32 | 01_cutoff | A2-JP_POLICY_RATE@2026-07-01 推定发布日 | 规则=期末(2026-07-31)+5天 | "2026-08-05" | "2026-08-05" | 一致 |
| 33 | 01_cutoff | A2-JP_POLICY_RATE@2026-10-01 推定发布日 | 规则=期末(2026-10-31)+5天 | "2026-11-05" | "2026-11-05" | 一致 |
| 34 | 01_cutoff | A2-CORE_PCE@2026-07 推定发布日晚于 3 个月前锚日(故锚=2026-06) | 规则=期末(2026-07-31)+30天 | True | True | 一致 |
| 35 | 01_cutoff | A2-US_REAL_GDP@2026-07 推定发布日晚于 3 个月前锚日(故锚=2026-04) | 规则=期末(2026-09-30)+29天 | True | True | 一致 |
| 36 | 02_anchors | B-US_REAL_GDP 3个月前锚值@2026-04-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.US_REAL_GDP.values[dates==2026-04-01] | 24408.011 | 24408.011 | 一致 |
| 37 | 02_anchors | B-US_REAL_GDP 最新一期值@2026-07-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.US_REAL_GDP.values[dates==2026-07-01] | 24611.077 | 24611.077 | 一致 |
| 38 | 02_anchors | B-US_REAL_GDP 最新一期=截止日前最新观测 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.US_REAL_GDP.dates | "2026-07-01" | "2026-07-01" | 一致 |
| 39 | 02_anchors | B-US_REAL_GDP 3个月前锚同比(基期=2025-04) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.US_REAL_GDP (2026-04 / 2025-04 - 1) | 2.191575 | 2.19 | 一致 |
| 40 | 02_anchors | B-US_REAL_GDP 最新一期同比(基期=2025-07) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.US_REAL_GDP (2026-07 / 2025-07 - 1) | 2.065739 | 2.07 | 一致 |
| 41 | 02_anchors | B-UNEMPLOYMENT 3个月前锚值@2026-07-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT.values[dates==2026-07-01] | 4.1 | 4.1 | 一致 |
| 42 | 02_anchors | B-UNEMPLOYMENT 最新一期值@2026-10-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT.values[dates==2026-10-01] | 4.1 | 4.1 | 一致 |
| 43 | 02_anchors | B-UNEMPLOYMENT 最新一期=截止日前最新观测 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT.dates | "2026-10-01" | "2026-10-01" | 一致 |
| 44 | 02_anchors | B-INDPRO 3个月前锚值@2026-07-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO.values[dates==2026-07-01] | 103.1675 | 103.1675 | 一致 |
| 45 | 02_anchors | B-INDPRO 最新一期值@2026-10-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO.values[dates==2026-10-01] | 103.3954 | 103.3954 | 一致 |
| 46 | 02_anchors | B-INDPRO 最新一期=截止日前最新观测 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO.dates | "2026-10-01" | "2026-10-01" | 一致 |
| 47 | 02_anchors | B-INDPRO 3个月前锚同比(基期=2025-07) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO (2026-07 / 2025-07 - 1) | 1.249828 | 1.25 | 一致 |
| 48 | 02_anchors | B-INDPRO 最新一期同比(基期=2025-10) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO (2026-10 / 2025-10 - 1) | 2.149685 | 2.15 | 一致 |
| 49 | 02_anchors | B-CPI 3个月前锚值@2026-07-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI.values[dates==2026-07-01] | 332.813 | 332.813 | 一致 |
| 50 | 02_anchors | B-CPI 最新一期值@2026-10-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI.values[dates==2026-10-01] | 337.476 | 337.476 | 一致 |
| 51 | 02_anchors | B-CPI 最新一期=截止日前最新观测 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI.dates | "2026-10-01" | "2026-10-01" | 一致 |
| 52 | 02_anchors | B-CPI 3个月前锚同比(基期=2025-07) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI (2026-07 / 2025-07 - 1) | 3.303856 | 3.3 | 一致 |
| 53 | 02_anchors | B-CPI 最新一期同比不可得(缺基期) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI (2026-10 与 2025-10) | True | True | 一致 |
| 54 | 02_anchors | B-CPI 基期 2025-10 在序列库缺席 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI.dates | null | null | 一致 |
| 55 | 02_anchors | B-CPI 最近有效同比 2026-09 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI (2026-09 / 2025-09 - 1) | 3.717251 | 3.72 | 一致 |
| 56 | 02_anchors | B-CPI 最近有效同比月份 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI | "2026-09" | "2026-09" | 一致 |
| 57 | 02_anchors | B-CORE_CPI 3个月前锚值@2026-07-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI.values[dates==2026-07-01] | 336.789 | 336.789 | 一致 |
| 58 | 02_anchors | B-CORE_CPI 最新一期值@2026-10-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI.values[dates==2026-10-01] | 339.9 | 339.9 | 一致 |
| 59 | 02_anchors | B-CORE_CPI 最新一期=截止日前最新观测 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI.dates | "2026-10-01" | "2026-10-01" | 一致 |
| 60 | 02_anchors | B-CORE_CPI 3个月前锚同比(基期=2025-07) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI (2026-07 / 2025-07 - 1) | 2.466518 | 2.47 | 一致 |
| 61 | 02_anchors | B-CORE_CPI 最新一期同比不可得(缺基期) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI (2026-10 与 2025-10) | True | True | 一致 |
| 62 | 02_anchors | B-CORE_CPI 基期 2025-10 在序列库缺席 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI.dates | null | null | 一致 |
| 63 | 02_anchors | B-CORE_CPI 最近有效同比 2026-09 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI (2026-09 / 2025-09 - 1) | 2.565841 | 2.57 | 一致 |
| 64 | 02_anchors | B-CORE_CPI 最近有效同比月份 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI | "2026-09" | "2026-09" | 一致 |
| 65 | 02_anchors | B-CORE_PCE 3个月前锚值@2026-06-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE.values[dates==2026-06-01] | 129.969 | 129.969 | 一致 |
| 66 | 02_anchors | B-CORE_PCE 最新一期值@2026-09-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE.values[dates==2026-09-01] | 130.902 | 130.902 | 一致 |
| 67 | 02_anchors | B-CORE_PCE 最新一期=截止日前最新观测 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE.dates | "2026-09-01" | "2026-09-01" | 一致 |
| 68 | 02_anchors | B-CORE_PCE 3个月前锚同比(基期=2025-06) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE (2026-06 / 2025-06 - 1) | 3.041234 | 3.04 | 一致 |
| 69 | 02_anchors | B-CORE_PCE 最新一期同比(基期=2025-09) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE (2026-09 / 2025-09 - 1) | 3.12116 | 3.12 | 一致 |
| 70 | 02_anchors | B-EA_REAL_GDP_YOY 3个月前锚值@2026-04-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_REAL_GDP_YOY.values[dates==2026-04-01] | 1.19 | 1.19 | 一致 |
| 71 | 02_anchors | B-EA_REAL_GDP_YOY 最新一期值@2026-07-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_REAL_GDP_YOY.values[dates==2026-07-01] | 1.28 | 1.28 | 一致 |
| 72 | 02_anchors | B-EA_REAL_GDP_YOY 最新一期=截止日前最新观测 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_REAL_GDP_YOY.dates | "2026-07-01" | "2026-07-01" | 一致 |
| 73 | 02_anchors | B-EA_HICP_YOY 3个月前锚值@2026-07-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY.values[dates==2026-07-01] | 2.9 | 2.9 | 一致 |
| 74 | 02_anchors | B-EA_HICP_YOY 最新一期值@2026-10-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY.values[dates==2026-10-01] | 4.0 | 4.0 | 一致 |
| 75 | 02_anchors | B-EA_HICP_YOY 最新一期=截止日前最新观测 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY.dates | "2026-10-01" | "2026-10-01" | 一致 |
| 76 | 02_anchors | B-JP_POLICY_RATE 3个月前锚值@2026-07-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE.values[dates==2026-07-01] | 0.978 | 0.978 | 一致 |
| 77 | 02_anchors | B-JP_POLICY_RATE 最新一期值@2026-10-01 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE.values[dates==2026-10-01] | 1.227 | 1.227 | 一致 |
| 78 | 02_anchors | B-JP_POLICY_RATE 最新一期=截止日前最新观测 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE.dates | "2026-10-01" | "2026-10-01" | 一致 |
| 79 | 02_anchors | B-CPI 2025-08..2026-01 缺采月=仅 2025-10 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI.dates | ["2025-10"] | ["2025-10"] | 一致 |
| 80 | 02_anchors | B-CORE_CPI 2025-08..2026-01 缺采月=仅 2025-10 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI.dates | ["2025-10"] | ["2025-10"] | 一致 |
| 81 | 03_yoy | C-CPI 同比 2026-02 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI (2026-02/2025-02-1) | 2.434004 | 2.434 | 一致 |
| 82 | 03_yoy | C-CPI 同比 2026-05 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI (2026-05/2025-05-1) | 4.166615 | 4.1666 | 一致 |
| 83 | 03_yoy | C-CPI 同比 2026-09 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI (2026-09/2025-09-1) | 3.717251 | 3.72 | 一致 |
| 84 | 03_yoy | C-CPI 同比 2026-07 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI (2026-07/2025-07-1) | 3.303856 | 3.3 | 一致 |
| 85 | 03_yoy | C-CORE_CPI 同比 2026-02 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI (2026-02/2025-02-1) | 2.472462 | 2.4725 | 一致 |
| 86 | 03_yoy | C-CORE_CPI 同比 2026-05 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI (2026-05/2025-05-1) | 2.822942 | 2.8229 | 一致 |
| 87 | 03_yoy | C-CORE_CPI 同比 2026-08 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI (2026-08/2025-08-1) | 2.446163 | 2.4462 | 一致 |
| 88 | 03_yoy | C-CORE_CPI 同比 2026-09 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI (2026-09/2025-09-1) | 2.565841 | 2.5658 | 一致 |
| 89 | 03_yoy | C-CORE_CPI 同比 2026-07 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI (2026-07/2025-07-1) | 2.466518 | 2.47 | 一致 |
| 90 | 03_yoy | C-CORE_CPI 同比 2026-09 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI (2026-09/2025-09-1) | 2.565841 | 2.57 | 一致 |
| 91 | 03_yoy | C-CORE_PCE 同比 2026-06 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE (2026-06/2025-06-1) | 3.041234 | 3.04 | 一致 |
| 92 | 03_yoy | C-CORE_PCE 同比 2026-09 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE (2026-09/2025-09-1) | 3.12116 | 3.12 | 一致 |
| 93 | 03_yoy | C-INDPRO 同比 2025-11 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO (2025-11/2024-11-1) | 1.754312 | 1.7543 | 一致 |
| 94 | 03_yoy | C-INDPRO 同比 2026-02 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO (2026-02/2025-02-1) | 0.797236 | 0.7972 | 一致 |
| 95 | 03_yoy | C-INDPRO 同比 2026-07 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO (2026-07/2025-07-1) | 1.249828 | 1.25 | 一致 |
| 96 | 03_yoy | C-INDPRO 同比 2026-10 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO (2026-10/2025-10-1) | 2.149685 | 2.15 | 一致 |
| 97 | 03_yoy | C-US_REAL_GDP 同比 2026-04 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.US_REAL_GDP (2026-04/2025-04-1) | 2.191575 | 2.19 | 一致 |
| 98 | 03_yoy | C-US_REAL_GDP 同比 2026-07 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.US_REAL_GDP (2026-07/2025-07-1) | 2.065739 | 2.07 | 一致 |
| 99 | 03_yoy | C-CPI 同比 2026 年内高点月=2026-05(约 4.17) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI | [4.166614684049641, "2026-05"] | ["2026-05", 4.17] | 一致 |
| 100 | 03_yoy | C-美欧可比同月: 2026-09 为 2023-09 以来首个 EA>US 月份 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY + CPI(同比派生) | {"2026-09": [3.8, 3.7173], "max EA>US month before 2026-09": "2023-09", "months 2023-10..2026-08 with EA>US": []} | "2023-09 以来首个; 2026-09 EA 略高" | 一致 |
| 101 | 03_yoy | C-2022-07..2023-09 EA 持续高于 US(逐月) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY + CPI | True | True | 一致 |
| 102 | 03_yoy | C-2025-01..2026-08 逐月 EA<=US(可比月) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY + CPI | [] | [] | 一致 |
| 103 | 03_yoy | C-EA_HICP_YOY 2026-02 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-02] | 1.9 | 1.9 | 一致 |
| 104 | 03_yoy | C-EA_HICP_YOY 2026-05 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-05] | 3.2 | 3.2 | 一致 |
| 105 | 03_yoy | C-EA_HICP_YOY 2026-06 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-06] | 2.8 | 2.8 | 一致 |
| 106 | 03_yoy | C-EA_HICP_YOY 2026-07 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-07] | 2.9 | 2.9 | 一致 |
| 107 | 03_yoy | C-EA_HICP_YOY 2026-10 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-10] | 4.0 | 4.0 | 一致 |
| 108 | 03_yoy | C-EA_HICP 2026-10=年内新高 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY | ["2026-10", 4.0] | ["2026-10", 4.0] | 一致 |
| 109 | 03_yoy | C-HICP 三个月上行幅度(pp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-10]-[2026-07] | 1.1 | 1.1 | 一致 |
| 110 | 03_yoy | C-INDPRO 2026-10 环比(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO[2026-10]/[2026-09]-1 | -0.43372 | -0.43 | 一致 |
| 111 | 03_yoy | C-INDPRO 2025-07→2025-10 基数变化(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO[2025-10]/[2025-07]-1 | -0.661962 | -0.66 | 一致 |
| 112 | 03_yoy | C-INDPRO 水平 2026-07→2026-10 变化(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO[2026-10]/[2026-07]-1 | 0.220903 | 0.22 | 一致 |
| 113 | 03_yoy | C-INDPRO 同比三个月变动(pp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO 同比 2026-10 − 2026-07 | 0.899856 | 0.9 | 一致 |
| 114 | 03_yoy | C-UNEMPLOYMENT 2026-07 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2026-07] | 4.1 | 4.1 | 一致 |
| 115 | 03_yoy | C-UNEMPLOYMENT 2026-09 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2026-09] | 4.2 | 4.2 | 一致 |
| 116 | 03_yoy | C-UNEMPLOYMENT 2026-10 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2026-10] | 4.1 | 4.1 | 一致 |
| 117 | 03_yoy | C-UNEMPLOYMENT 2026-08 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2026-08] | 4.1 | 4.1 | 一致 |
| 118 | 03_yoy | C-UNEMPLOYMENT 2025-11 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2025-11] | 4.5 | 4.5 | 一致 |
| 119 | 03_yoy | C-UNEMPLOYMENT 2026-02 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2026-02] | 4.4 | 4.4 | 一致 |
| 120 | 03_yoy | C-UNEMPLOYMENT 2026-05 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2026-05] | 4.3 | 4.3 | 一致 |
| 121 | 03_yoy | C-US_REAL_GDP 2026-04 水平 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.US_REAL_GDP[2026-04] | 24408.011 | 24408.011 | 一致 |
| 122 | 03_yoy | C-EA_REAL_GDP_YOY 2026-04 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_REAL_GDP_YOY[2026-04] | 1.19 | 1.19 | 一致 |
| 123 | 03_yoy | C-EA_REAL_GDP_YOY 2026-07 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_REAL_GDP_YOY[2026-07] | 1.28 | 1.28 | 一致 |
| 124 | 04_policy | D1-RC-JP-BOJ-TARGET-2026-09 在场且 kind=policy_decision | root_overlay/config/release_calendar.json:entries[entry_id=RC-JP-BOJ-TARGET-2026-09] | "policy_decision" | "policy_decision" | 一致 |
| 125 | 04_policy | D1-决议日 decision_date | root_overlay/config/release_calendar.json:RC-JP-BOJ-TARGET-2026-09.decision_date | "2026-09-18" | "2026-09-18" | 一致 |
| 126 | 04_policy | D1-生效日 effective_on | root_overlay/config/release_calendar.json:RC-JP-BOJ-TARGET-2026-09.effective_on | "2026-09-24" | "2026-09-24" | 一致 |
| 127 | 04_policy | D1-目标水平 target_value(约一点二五) | root_overlay/config/release_calendar.json:RC-JP-BOJ-TARGET-2026-09.target_value | 1.25 | 1.25 | 一致 |
| 128 | 04_policy | D1-公告可见日 first_publish_on_or_after=决议日 | root_overlay/config/release_calendar.json:RC-JP-BOJ-TARGET-2026-09.first_publish_on_or_after | "2026-09-18" | "2026-09-18" | 一致 |
| 129 | 04_policy | D1-决议日≤截止日(可引用) | root_overlay/config/release_calendar.json:RC-JP-BOJ-TARGET-2026-09 | True | True | 一致 |
| 130 | 04_policy | D2-RC-JP-BOJ-MAINT-2026-10 在场且 kind=policy_maintenance | root_overlay/config/release_calendar.json:entries[entry_id=RC-JP-BOJ-MAINT-2026-10] | "policy_maintenance" | "policy_maintenance" | 一致 |
| 131 | 04_policy | D2-确认维持日 2026-10-30 | root_overlay/config/release_calendar.json:RC-JP-BOJ-MAINT-2026-10.decision_date | "2026-10-30" | "2026-10-30" | 一致 |
| 132 | 04_policy | D2-维持条目目标水平 | root_overlay/config/release_calendar.json:RC-JP-BOJ-MAINT-2026-10.target_value | 1.25 | 1.25 | 一致 |
| 133 | 04_policy | D2-维持条目无生效日(正文不为其挂生效日) | root_overlay/config/release_calendar.json:RC-JP-BOJ-MAINT-2026-10 | False | False | 一致 |
| 134 | 04_policy | D3-距上次调整(按生效日 2026-09-24→截止日)天数 | root_overlay/config/release_calendar.json:RC-JP-BOJ-TARGET-2026-09.effective_on ; 快照 research_as_of | 60 | 60 | 一致 |
| 135 | 04_policy | D3-距上次调整(按决议日 2026-09-18→截止日)天数 | root_overlay/config/release_calendar.json:RC-JP-BOJ-TARGET-2026-09.decision_date | 66 | 66 | 一致 |
| 136 | 04_policy | D3-距确认维持(2026-10-30→截止日)天数=24(其后日历无条目) | root_overlay/config/release_calendar.json:RC-JP-BOJ-MAINT-2026-10.decision_date | 24 | 24 | 一致 |
| 137 | 04_policy | D4-日历政策条目共 2 条且均为日本央行实录; 维持后无新条目 | root_overlay/config/release_calendar.json:entries(kind=policy_*) | ["RC-JP-BOJ-TARGET-2026-09", "RC-JP-BOJ-MAINT-2026-10"] | ["RC-JP-BOJ-TARGET-2026-09", "RC-JP-BOJ-MAINT-2026-10"] | 一致 |
| 138 | 04_policy | D4-冻结日历无美欧决议/生效实录条目 | root_overlay/config/release_calendar.json:entries | ["JP_POLICY_TARGET"] | ["JP_POLICY_TARGET"] | 一致 |
| 139 | 04_policy | D4-冻结日历版本 v1.5.0 | root_overlay/config/release_calendar.json:version | "1.5.0" | "1.5.0" | 一致 |
| 140 | 04_policy | D5-JP_POLICY_RATE 月均 2025-11..2026-10 逐月值 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE | [["2025-10", 0.477], ["2025-11", 0.478], ["2025-12", 0.557], ["2026-01", 0.728], ["2026-02", 0.728], ["2026-03", 0.728], ["2026-04", 0.727], ["2026-05", 0.727], ["2026-06", 0.841], ["2026-07", 0.978], ["2026-08", 0.977], ["2026-09", 1.043], ["2026-10", 1.227]] | {"2025-11": 0.478, "2025-12": 0.557, "2026-01": 0.728, "2026-06": 0.841, "2026-07": 0.978, "2026-09": 1.043, "2026-10": 1.227, "2026-08": 0.977, "2026-04": 0.727} | 一致 |
| 141 | 04_policy | D5-月均相邻变动点(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE(相邻月差) | [["2025-11", 0.477, 0.478, 0.1], ["2025-12", 0.478, 0.557, 7.9], ["2026-01", 0.557, 0.728, 17.1], ["2026-02", 0.728, 0.728, 0.0], ["2026-03", 0.728, 0.728, 0.0], ["2026-04", 0.728, 0.727, -0.1], ["2026-05", 0.727, 0.727, 0.0], ["2026-06", 0.727, 0.841, 11.4], ["2026-07", 0.841, 0.978, 13.7], ["2026-08", 0.978, 0.977, -0.1], ["2026-09", 0.977, 1.043, 6.6], ["2026-10", 1.043, 1.227, 18.4]] | "2025-12 +8; 2026-01 +17; 2026-06 +11; 2026-07 +14; 2026-09 +7; 2026-10 +18" | 一致 |
| 142 | 04_policy | D5-12 个月政策窗净变动(bp): 2025-11 月均→2026-10 月均 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-10]-[2025-11] | 74.9 | 75 | 一致 |
| 143 | 04_policy | D5-仅自窗内首观测 2025-12 月均起算(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-10]-[2025-12] | 67.0 | 67 | 一致 |
| 144 | 04_policy | D5-净变动=窗内六个变动点之和(按所述整数 bp 精度) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE(变动点求和) | {"六点整数bp之和": 75, "变动点数": 6, "端点差取整": 75} | {"sum": 75, "n": 6} | 一致 |
| 145 | 04_policy | D5-注记: 六点两位小数直和 75.1bp vs 端点差 74.9bp(阈值下漂移) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE | {"六点两位小数直和(bp)": 75.1, "端点差(bp)": 74.9, "阈值下漂移(bp)": [["2025-11", 0.1], ["2026-04", -0.1], ["2026-08", -0.1]]} | "恒等仅在整数 bp 显示精度成立" | 一致 |
| 146 | 04_policy | D5-2026-02→05 与 2026-07→08 相邻月均差均 ≤0.001(=0.1bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE | [["2026-03", 0.0], ["2026-04", -0.1], ["2026-05", 0.0], ["2026-08", -0.1]] | True | 一致 |
| 147 | 04_policy | D5-2026 年内上行月均台阶: 01/06/07 为头三个(2026-07 为第三个) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE | ["2026-01", "2026-06", "2026-07", "2026-09", "2026-10"] | ["2026-01", "2026-06", "2026-07", "2026-09", "2026-10"] | 一致 |
| 148 | 04_policy | D5-2026-04→2026-07 锚 0.727→0.978(经 2026-06 0.841) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-04],[2026-06],[2026-07] | [0.727, 0.841, 0.978] | [0.727, 0.841, 0.978] | 一致 |
| 149 | 04_policy | D5-最近一级台阶=2026-09→2026-10(其后无更新观测) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE.dates | "2026-10" | "2026-10" | 一致 |
| 150 | 04_policy | D6-DFEDTARU 变动日与前后值 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.DFEDTARU | [["2026-09-17", 3.75, 4.0]] | ["2026-09-17", 3.75, 4.0] | 一致 |
| 151 | 04_policy | D6-ECB_DFR 变动日与前后值 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.ECB_DFR | [["2026-06-17", 2.0, 2.25], ["2026-09-16", 2.25, 2.5]] | ["2026-09-16", 2.25, 2.5] | 一致 |
| 152 | 04_policy | D6-DFEDTARU/ECB_DFR 不在本问证据索引(63 行) | evidence_index.json | [] | [] | 一致 |
| 153 | 04_policy | D7-注册表无 JP_POLICY_TARGET | root_overlay/config/metric_registry.json:metrics[metric_id=JP_POLICY_TARGET] | False | False | 一致 |
| 154 | 04_policy | D7-注册表 economy=JP 面 | root_overlay/config/metric_registry.json:metrics[economy=JP] | ["EWJ", "JGB10Y", "JGB2Y", "JGB5Y", "JP_CPI_TOKYO_YOY", "JP_CPI_YOY", "JP_POLICY_RATE", "JP_REAL_GDP_YOY", "NIKKEI225", "USDJPY"] | "含 JP_POLICY_RATE, 不含政策目标序列" | 一致 |
| 155 | 04_policy | D7-快照 series_store 无 JP_POLICY_TARGET | root_overlay/data/daily/research_snapshot_20261123.json:series_store | False | False | 一致 |
| 156 | 04_policy | D7-JP_POLICY_RATE 注册表口径=无担保隔夜拆借利率月均(非目标宣布值) | root_overlay/config/metric_registry.json:metrics[JP_POLICY_RATE].calc/value_type | ["monthly_avg_rate", "FRED系列IRSTCI01JPM156N最新观测(日本无担保隔夜拆借利率月均,"] | "monthly_avg_rate / 日本无担保隔夜拆借利率月均" | 一致 |
| 157 | 04_policy | D8-FOMC-MINUTES-2026-10 发布日 2026-11-18 | report.json:research_plan.policy_doc_facts[0] | [["FOMC-MINUTES-2026-10", "2026-11-18", "minutes"]] | [["FOMC-MINUTES-2026-10", "2026-11-18", "minutes"]] | 一致 |
| 158 | 04_policy | D8-政策事件簇为空 | report.json:research_plan.policy_event_clusters.clusters | [] | [] | 一致 |
| 159 | 05a_rates | A0-UST_10Y 序列末端观测日/值 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UST_10Y | ["2026-11-19", 5.04, 2497, "2016-11-23"] | "利率三序列止于 2026-11-19(BEI_10Y 止于 2026-11-20)" | 一致 |
| 160 | 05a_rates | A0-TIPS_10Y 序列末端观测日/值 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y | ["2026-11-19", 2.88, 2497, "2016-11-23"] | "利率三序列止于 2026-11-19(BEI_10Y 止于 2026-11-20)" | 一致 |
| 161 | 05a_rates | A0-BEI_10Y 序列末端观测日/值 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y | ["2026-11-20", 2.15, 2498, "2016-11-23"] | "利率三序列止于 2026-11-19(BEI_10Y 止于 2026-11-20)" | 一致 |
| 162 | 05a_rates | A1-近一月窗名义 UST_10Y 变动(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UST_10Y[2026-10-20..2026-11-19] | -8.0 | -8 | 一致 |
| 163 | 05a_rates | A2-近一月窗实际 TIPS_10Y 变动(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y[2026-10-20..2026-11-19] | 11.0 | 11 | 一致 |
| 164 | 05a_rates | A3-近一月窗盈亏平衡 BEI_10Y 变动(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[2026-10-20..2026-11-19] | -19.0 | -19 | 一致 |
| 165 | 05a_rates | A4-近一月窗名义=实际+盈亏平衡 残差(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UST_10Y/TIPS_10Y/BEI_10Y | 0.0 | 0 | 一致 |
| 166 | 05a_rates | A5-期末水平 UST_10Y@2026-11-19 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UST_10Y[2026-11-19] | 5.04 | 5.04 | 一致 |
| 167 | 05a_rates | A6-期末水平 TIPS_10Y@2026-11-19 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y[2026-11-19] | 2.88 | 2.88 | 一致 |
| 168 | 05a_rates | A7-期末水平 BEI_10Y@2026-11-19 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[2026-11-19] | 2.16 | 2.16 | 一致 |
| 169 | 05a_rates | A8-最新 BEI_10Y@2026-11-20 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[2026-11-20] | 2.15 | 2.15 | 一致 |
| 170 | 05a_rates | A9-名义水平=实际+盈亏平衡(同日 2026-11-19) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UST_10Y/TIPS_10Y/BEI_10Y[2026-11-19] | True | True | 一致 |
| 171 | 05a_rates | A10-三个月窗名义 UST_10Y 变动(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UST_10Y[2026-08-19..2026-11-19] | 39.0 | 39 | 一致 |
| 172 | 05a_rates | A10-三个月窗实际 TIPS_10Y 变动(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y[2026-08-19..2026-11-19] | 53.0 | 53 | 一致 |
| 173 | 05a_rates | A10-三个月窗盈亏平衡 BEI_10Y 变动(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[2026-08-19..2026-11-19] | -14.0 | -14 | 一致 |
| 174 | 05a_rates | A11-三个月窗 BEI_10Y 窗启水平 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[2026-08-19] | 2.3 | 2.3 | 一致 |
| 175 | 05a_rates | A12-三个月窗 BEI_10Y 窗末水平 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[2026-11-19] | 2.16 | 2.16 | 一致 |
| 176 | 05a_rates | A13-三个月窗恒等残差(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UST_10Y/TIPS_10Y/BEI_10Y | -0.0 | 0 | 一致 |
| 177 | 05a_rates | A14-三个月窗「名义上行由实际利率主导」(实际分量幅度>名义变动) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y/UST_10Y[2026-08-19..2026-11-19] | True | True | 一致 |
| 178 | 05a_rates | A15-12个月窗名义 UST_10Y 变动(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UST_10Y[2025-11-19..2026-11-19] | 91.0 | 91 | 一致 |
| 179 | 05a_rates | A15-12个月窗实际 TIPS_10Y 变动(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y[2025-11-19..2026-11-19] | 102.0 | 102 | 一致 |
| 180 | 05a_rates | A15-12个月窗盈亏平衡 BEI_10Y 变动(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[2025-11-19..2026-11-19] | -11.0 | -11 | 一致 |
| 181 | 05a_rates | A16-12个月窗恒等残差(bp) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UST_10Y/TIPS_10Y/BEI_10Y | 0.0 | 0 | 一致 |
| 182 | 05a_rates | A17-12个月窗「名义上行由实际利率主导」(实际分量幅度>名义变动) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y/UST_10Y[2025-11-19..2026-11-19] | True | True | 一致 |
| 183 | 05a_rates | A18-三窗同为「实际上行、盈亏平衡回落」 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y/BEI_10Y 三窗 | True | True | 一致 |
| 184 | 05a_rates | A19-同窗 TIPS_10Y 窗启 2026-10-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y[2026-10-23] | 2.66 | 2.66 | 一致 |
| 185 | 05a_rates | A20-同窗 TIPS_10Y 变动(bp, 2026-10-23→2026-11-19) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y[2026-10-23..2026-11-19] | 22.0 | 22 | 一致 |
| 186 | 05a_rates | A21-BEI_10Y 最新 2.15(2026-11-20)为 12 个月窗(2025-11-20..2026-11-20)最低 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[2025-11-20..2026-11-20] | True | True | 一致 |
| 187 | 05a_rates | A21b-BEI_10Y 最新值为 12 个月窗(2025-11-23..2026-11-23)最低 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[2025-11-23..2026-11-23] | True | True | 一致 |
| 188 | 05a_rates | A22-BEI_10Y 2026-02-27 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[2026-02-27] | 2.25 | 2.25 | 一致 |
| 189 | 05a_rates | A23-BEI_10Y 2026-05-04 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[2026-05-04] | 2.5 | 2.5 | 一致 |
| 190 | 05a_rates | A24-更早通胀上行段 BEI_10Y 上行(2026-02-27→2026-05-04) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[2026-02-27, 2026-05-04] | True | True | 一致 |
| 191 | 05b_assets | B1-SPX 窗启值 2026-10-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.SPX[2026-10-23] | 7623.680176 | 7623.68 | 一致 |
| 192 | 05b_assets | B2-SPX 窗末值 2026-11-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.SPX[2026-11-23] | 7203.850098 | 7203.85 | 一致 |
| 193 | 05b_assets | B3-SPX 近一月变动(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.SPX[2026-10-23..2026-11-23] | -5.506921 | -5.51 | 一致 |
| 194 | 05b_assets | B4-SPX 序列末观测=2026-11-23(截止日前最后观测) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.SPX | True | True | 一致 |
| 195 | 05b_assets | B1-NIKKEI225 窗启值 2026-10-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.NIKKEI225[2026-10-23] | 62693.16 | 62693.16 | 一致 |
| 196 | 05b_assets | B2-NIKKEI225 窗末值 2026-11-20 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.NIKKEI225[2026-11-20] | 56436.65 | 56436.65 | 一致 |
| 197 | 05b_assets | B3-NIKKEI225 近一月变动(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.NIKKEI225[2026-10-23..2026-11-20] | -9.979574 | -9.98 | 一致 |
| 198 | 05b_assets | B4-NIKKEI225 序列末观测=2026-11-20(截止日前最后观测) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.NIKKEI225 | True | True | 一致 |
| 199 | 05b_assets | B1-GOLD_F 窗启值 2026-10-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.GOLD_F[2026-10-23] | 4007.899902 | 4007.9 | 一致 |
| 200 | 05b_assets | B2-GOLD_F 窗末值 2026-11-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.GOLD_F[2026-11-23] | 3685.199951 | 3685.2 | 一致 |
| 201 | 05b_assets | B3-GOLD_F 近一月变动(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.GOLD_F[2026-10-23..2026-11-23] | -8.051597 | -8.05 | 一致 |
| 202 | 05b_assets | B4-GOLD_F 序列末观测=2026-11-23(截止日前最后观测) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.GOLD_F | True | True | 一致 |
| 203 | 05b_assets | B1-DXY 窗启值 2026-10-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.DXY[2026-10-23] | 101.809998 | 101.81 | 一致 |
| 204 | 05b_assets | B2-DXY 窗末值 2026-11-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.DXY[2026-11-23] | 104.079002 | 104.079 | 一致 |
| 205 | 05b_assets | B3-DXY 近一月变动(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.DXY[2026-10-23..2026-11-23] | 2.228665 | 2.23 | 一致 |
| 206 | 05b_assets | B4-DXY 序列末观测=2026-11-23(截止日前最后观测) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.DXY | True | True | 一致 |
| 207 | 05b_assets | B1-VIX 窗启值 2026-10-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.VIX[2026-10-23] | 19.450001 | 19.45 | 一致 |
| 208 | 05b_assets | B2-VIX 窗末值 2026-11-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.VIX[2026-11-23] | 27.01 | 27.01 | 一致 |
| 209 | 05b_assets | B3-VIX 近一月变动(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.VIX[2026-10-23..2026-11-23] | 38.868887 | 38.87 | 一致 |
| 210 | 05b_assets | B4-VIX 序列末观测=2026-11-23(截止日前最后观测) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.VIX | True | True | 一致 |
| 211 | 05b_assets | B5-SPX 共同交易日窗 2026-10-23→2026-11-19 变动(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.SPX[2026-10-23, 2026-11-19] | -5.874461 | -5.87 | 一致 |
| 212 | 05b_assets | B6-同日收盘口径 SPX 2026-10-23→2026-11-20 变动(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.SPX[2026-10-23, 2026-11-20] | -9.356243 | -9.36 | 一致 |
| 213 | 05b_assets | B7-同日收盘口径 VIX 2026-10-23→2026-11-20 变动(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.VIX[2026-10-23, 2026-11-20] | 84.524407 | 84.52 | 一致 |
| 214 | 05b_assets | B8-三个月收盘口径 SPX 2026-08-19→2026-11-20 变动(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.SPX[2026-08-19, 2026-11-20] | -10.347586 | -10.35 | 一致 |
| 215 | 05b_assets | B9-三个月收盘口径 VIX 2026-08-19→2026-11-20 变动(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.VIX[2026-08-19, 2026-11-20] | 141.034244 | 141.03 | 一致 |
| 216 | 05b_assets | B10-三个月收盘口径 VIX 窗启 2026-08-19 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.VIX[2026-08-19] | 14.89 | 14.89 | 一致 |
| 217 | 05b_assets | B11-三个月收盘口径 VIX 窗末 2026-11-20 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.VIX[2026-11-20] | 35.889999 | 35.89 | 一致 |
| 218 | 05b_assets | B12-VIX 窗启 2026-10-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.VIX[2026-10-23] | 19.450001 | 19.45 | 一致 |
| 219 | 05b_assets | B13-VIX 窗末 2026-11-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.VIX[2026-11-23] | 27.01 | 27.01 | 一致 |
| 220 | 05b_assets | B14-「同窗 TIPS_10Y +53bp(三个月收盘口径, 利率序列止于 2026-11-19)」 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y[2026-08-19, 2026-11-19] | True | True | 一致 |
| 221 | 05b_assets | B15-股金同跌、美元与波动率齐升(近一月窗) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.SPX/GOLD_F/DXY/VIX/NIKKEI225 | True | True | 一致 |
| 222 | 05b_assets | B16-S2 所述「共同交易日窗 2026-10-20→2026-11-19 实际利率 +11bp 而风险资产回落」 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.SPX[2026-10-20, 2026-11-19] | True | True | 一致 |
| 223 | 05c_fx | C1-USDJPY 2026-11-23 水平 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.USDJPY[2026-11-23] | 159.347 | 159.35 | 一致 |
| 224 | 05c_fx | C2-USDJPY 近一月变动(%)(2026-10-23→2026-11-23) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.USDJPY[2026-10-23, 2026-11-23] | 1.823071 | 1.82 | 一致 |
| 225 | 05c_fx | C3-USDJPY 三个月变动(%)(2026-08-19→2026-11-23) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.USDJPY[2026-08-19, 2026-11-23] | -0.127235 | -0.13 | 一致 |
| 226 | 05c_fx | C4-USDJPY 12 个月窗内百分位≈71 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.USDJPY[2025-11-23..2026-11-23] | {"n": 259, "leq_frac": 71.04247104247105, "lt_frac": 70.65637065637065, "midrank": 70.84942084942085, "rank_m1": 70.93023255813954} | "约第 71 百分位" | 一致 |
| 227 | 05c_fx | C5-USDJPY 序列库全史百分位≈96.6 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.USDJPY[全史≤2026-11-23] | {"n": 2601, "leq_frac": 96.57823913879278, "lt_frac": 96.53979238754326, "midrank": 96.559015763168, "rank_m1": 96.57692307692308, "first": "2016-11-23", "last": "2026-11-23"} | "约第 96.6 百分位(全史 2016-11-23 起)" | 一致 |
| 228 | 05c_fx | C6-USDJPY 序列库首观测日=2016-11-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.USDJPY[0] | True | True | 一致 |
| 229 | 05c_fx | C7-USDJPY「近一月不降反升」 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.USDJPY[2026-10-23, 2026-11-23] | True | True | 一致 |
| 230 | 05c_fx | C8-EURUSD 2026-11-23 水平 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EURUSD[2026-11-23] | 1.093972 | 1.093972 | 一致 |
| 231 | 05c_fx | C9-EURUSD 三个月变动(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EURUSD[2026-08-19, 2026-11-23] | -5.524538 | -5.52 | 一致 |
| 232 | 05c_fx | C10-EURUSD 2026-11-23 为近 12 个月窗(2025-11-23..2026-11-23)最低 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EURUSD[2025-11-23..2026-11-23] | True | True | 一致 |
| 233 | 05d_oil | D1-BRENT_F 2026-08-19 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-08-19] | 91.620003 | 91.62 | 一致 |
| 234 | 05d_oil | D2-BRENT_F 2026-11-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-11-23] | 88.190002 | 88.19 | 一致 |
| 235 | 05d_oil | D3-BRENT_F 近三个月变动(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-08-19, 2026-11-23] | -3.743725 | -3.74 | 一致 |
| 236 | 05d_oil | D4-BRENT_F 2026-10-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-10-23] | 116.720001 | 116.72 | 一致 |
| 237 | 05d_oil | D5-BRENT_F 2026-10-23 较窗启(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-08-19, 2026-10-23] | 27.395762 | 27.4 | 一致 |
| 238 | 05d_oil | D6-BRENT_F 近一月变动(%)(2026-10-23→2026-11-23) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-10-23, 2026-11-23] | -24.443111 | -24.44 | 一致 |
| 239 | 05d_oil | D7-BRENT_F 近 12 个月变动(%)(窗启 2025-11-19, 与三利率 12 个月窗同口径) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2025-11-19, 2026-11-23] | 38.86003 | 38.86 | 一致 |
| 240 | 05d_oil | D8-BRENT_F 窗内高点 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-08-19..2026-11-23] | 117.639999 | 117.64 | 一致 |
| 241 | 05d_oil | D9-BRENT_F 窗内高点日=2026-10-30 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-08-19..2026-11-23] | True | True | 一致 |
| 242 | 05d_oil | D10-BRENT_F 窗内观测数=68 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-08-19..2026-11-23] | True | True | 一致 |
| 243 | 05d_oil | D11-BRENT_F 窗内不低于窗启值 91.62 的观测数=61 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-08-19..2026-11-23] | True | True | 一致 |
| 244 | 05d_oil | D12-BRENT_F 日值月均 2026-07 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-07 日值均] | 84.512273 | 84.51 | 一致 |
| 245 | 05d_oil | D13-BRENT_F 日值月均 2026-09 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-09 日值均] | 102.256666 | 102.26 | 一致 |
| 246 | 05d_oil | D14-BRENT_F 日值月均 2026-10 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-10 日值均] | 108.337272 | 108.34 | 一致 |
| 247 | 05d_oil | D15-BRENT_F 日值月均 2025-10 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2025-10 日值均] | 63.953913 | 63.95 | 一致 |
| 248 | 05d_oil | D16-BRENT_F 月均 2026-07→2026-09(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[月均 2026-07, 2026-09] | 20.996232 | 21.0 | 一致 |
| 249 | 05d_oil | D17-BRENT_F 月均 2026-07→2026-10(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[月均 2026-07, 2026-10] | 28.191171 | 28.2 | 一致 |
| 250 | 05d_oil | D18-BRENT_F 月均 2026-10 较 2025-10(%) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[月均 2025-10, 2026-10] | 69.398974 | 69.4 | 一致 |
| 251 | 05d_oil | D19-各发布日当日 BRENT_F 最低(字面读法 A) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[各发布日]; report.json:research_plan.point_values.cells[*].anchors.最新一期.publication_rule(月末+N天,推定) | {"最低": [92.440002, "2026-11-16", "2026-11-16"], "发布日数": 5} | 92.44 | 一致 |
| 252 | 05d_oil | D20-各发布日当日 BRENT_F 最高(字面读法 A) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[各发布日] | {"最高": [117.639999, "2026-10-30", "2026-10-30"]} | 117.64 | 一致 |
| 253 | 05d_oil | D21-各发布日当日 BRENT_F 全部不低于窗启值 91.62(字面读法 A) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[各发布日] | True | True | 一致 |
| 254 | 05d_oil | D20b-发布日跨度端点=2026-10-13 与 2026-11-16(九月/十月通胀读数, 引擎推定规则月末+N天) | x_research_plan.json:research_plan.point_values.cells[*].anchors.最新一期.publication_rule(月末+N天,推定) | True | True | 一致 |
| 255 | 05d_oil | D22-「窗内先升至 2026-10-23 的 116.72」「窗末急跌」: 窗末值低于窗启且低于 2026-10-23 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F[2026-08-19, 2026-10-23, 2026-11-23] | True | True | 一致 |
| 256 | 06_turnings | T1-CPI 候选窗 2026-02→2026-05 与独立重算最大段一致 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI(3 个月滚动差; 窗端点发布纪律过滤) | True | True | 一致 |
| 257 | 06_turnings | T2-CPI 候选 value_before | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI[2026-02] | 2.434004 | 2.434 | 一致 |
| 258 | 06_turnings | T3-CPI 候选 value_after | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI[2026-05] | 4.166615 | 4.1666 | 一致 |
| 259 | 06_turnings | T4-CPI 候选 delta(=四位小数端点之差, 引擎面口径) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI[2026-02..2026-05] | 1.7326 | 1.7326 | 一致 |
| 260 | 06_turnings | T1-CORE_CPI 候选窗 2026-05→2026-08 与独立重算最大段一致 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI(3 个月滚动差; 窗端点发布纪律过滤) | True | True | 一致 |
| 261 | 06_turnings | T2-CORE_CPI 候选 value_before | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI[2026-05] | 2.822942 | 2.8229 | 一致 |
| 262 | 06_turnings | T3-CORE_CPI 候选 value_after | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI[2026-08] | 2.446163 | 2.4462 | 一致 |
| 263 | 06_turnings | T4-CORE_CPI 候选 delta(=四位小数端点之差, 引擎面口径) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI[2026-05..2026-08] | -0.3767 | -0.3767 | 一致 |
| 264 | 06_turnings | T1-CORE_PCE 候选窗 2025-11→2026-02 与独立重算最大段一致 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE(3 个月滚动差; 窗端点发布纪律过滤) | True | True | 一致 |
| 265 | 06_turnings | T2-CORE_PCE 候选 value_before | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE[2025-11] | 2.721209 | 2.7212 | 一致 |
| 266 | 06_turnings | T3-CORE_PCE 候选 value_after | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE[2026-02] | 2.959153 | 2.9592 | 一致 |
| 267 | 06_turnings | T4-CORE_PCE 候选 delta(=四位小数端点之差, 引擎面口径) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE[2025-11..2026-02] | 0.238 | 0.238 | 一致 |
| 268 | 06_turnings | T1-INDPRO 候选窗 2025-11→2026-02 与独立重算最大段一致 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO(3 个月滚动差; 窗端点发布纪律过滤) | True | True | 一致 |
| 269 | 06_turnings | T2-INDPRO 候选 value_before | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO[2025-11] | 1.754312 | 1.7543 | 一致 |
| 270 | 06_turnings | T3-INDPRO 候选 value_after | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO[2026-02] | 0.797236 | 0.7972 | 一致 |
| 271 | 06_turnings | T4-INDPRO 候选 delta(=四位小数端点之差, 引擎面口径) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO[2025-11..2026-02] | -0.9571 | -0.9571 | 一致 |
| 272 | 06_turnings | T1-UNEMPLOYMENT 候选窗 2026-05→2026-08 与独立重算最大段一致 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT(3 个月滚动差; 窗端点发布纪律过滤) | True | True | 一致 |
| 273 | 06_turnings | T2-UNEMPLOYMENT 候选 value_before | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2026-05] | 4.3 | 4.3 | 一致 |
| 274 | 06_turnings | T3-UNEMPLOYMENT 候选 value_after | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2026-08] | 4.1 | 4.1 | 一致 |
| 275 | 06_turnings | T4-UNEMPLOYMENT 候选 delta(=四位小数端点之差, 引擎面口径) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2026-05..2026-08] | -0.2 | -0.2 | 一致 |
| 276 | 06_turnings | T1-EA_HICP_YOY 候选窗 2026-02→2026-05 与独立重算最大段一致 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY(3 个月滚动差; 窗端点发布纪律过滤) | True | True | 一致 |
| 277 | 06_turnings | T2-EA_HICP_YOY 候选 value_before | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-02] | 1.9 | 1.9 | 一致 |
| 278 | 06_turnings | T3-EA_HICP_YOY 候选 value_after | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-05] | 3.2 | 3.2 | 一致 |
| 279 | 06_turnings | T4-EA_HICP_YOY 候选 delta(=四位小数端点之差, 引擎面口径) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-02..2026-05] | 1.3 | 1.3 | 一致 |
| 280 | 06_turnings | T1-JP_POLICY_RATE 候选窗 2026-04→2026-07 与独立重算最大段一致 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE(3 个月滚动差; 窗端点发布纪律过滤) | True | True | 一致 |
| 281 | 06_turnings | T2-JP_POLICY_RATE 候选 value_before | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-04] | 0.727 | 0.727 | 一致 |
| 282 | 06_turnings | T3-JP_POLICY_RATE 候选 value_after | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-07] | 0.978 | 0.978 | 一致 |
| 283 | 06_turnings | T4-JP_POLICY_RATE 候选 delta(=四位小数端点之差, 引擎面口径) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-04..2026-07] | 0.251 | 0.251 | 一致 |
| 284 | 06_turnings | T5-引擎候选池条数=7(与受审稿「候选池7」一致) | report.json:research_plan.turning_candidates.candidates | True | True | 一致 |
| 285 | 06_turnings | T6-候选池按 ｜delta｜ 降序 = CPI 1.7326 > EA_HICP_YOY 1.3 > INDPRO 0.9571 > CORE_CPI 0.3767 > JP_POLICY_RATE 0.251 > CORE_PCE 0.238 > UNEMPLOYMENT 0.2 | report.json:research_plan.turning_candidates.candidates[*].delta | True | True | 一致 |
| 286 | 06_turnings | T7-受审稿 top3 所述「CPI 2.434→4.1666 为候选池内最大单段变动」 | report.json:research_plan.turning_candidates.candidates | True | True | 一致 |
| 287 | 06_turnings | T8-受审稿「INDPRO 为增长维候选池内最大的三个月变化」 | report.json:research_plan.turning_candidates.candidates[dimension=growth] | True | True | 一致 |
| 288 | 06_turnings | T9-top_n_expected=3 且转折表 3 项(与受审稿「top3」/三转折一致) | report.json:research_plan.turning_candidates.top_n_expected; agent_judgment.json:reader_map.turnings | True | True | 一致 |
| 289 | 06_turnings | T10-转折表三项指标(CPI/INDPRO/JP_POLICY_RATE)均在候选池内且分属通胀/增长/政策三维(不同事件) | agent_judgment.json:reader_map.turnings[*].metric_id; report.json:…candidates[*].dimension | True | True | 一致 |
| 290 | 06b_turning_numbers | N1-CPI 同比 2026-02 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI[2026-02-01, 2025-02-01] | 2.434004 | 2.434 | 一致 |
| 291 | 06b_turning_numbers | N2-CPI 同比 2026-05 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI[2026-05-01, 2025-05-01] | 4.166615 | 4.1666 | 一致 |
| 292 | 06b_turning_numbers | N3-EA_HICP_YOY 2026-05 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-05-01] | 3.2 | 3.2 | 一致 |
| 293 | 06b_turning_numbers | N4-EA_HICP_YOY 2026-06 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-06-01] | 2.8 | 2.8 | 一致 |
| 294 | 06b_turning_numbers | N5-EA_HICP_YOY 2026-07 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-07-01] | 2.9 | 2.9 | 一致 |
| 295 | 06b_turning_numbers | N6-EA_HICP_YOY 2026-10 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-10-01] | 4.0 | 4.0 | 一致 |
| 296 | 06b_turning_numbers | N7-「2026-10 的 4.0 越过 2026-05 的 3.2」 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-05-01, 2026-10-01] | True | True | 一致 |
| 297 | 06b_turning_numbers | N8-CORE_CPI 同比 2026-02 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI[2026-02-01, 2025-02-01] | 2.472462 | 2.4725 | 一致 |
| 298 | 06b_turning_numbers | N9-CORE_CPI 同比 2026-05 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI[2026-05-01, 2025-05-01] | 2.822942 | 2.8229 | 一致 |
| 299 | 06b_turning_numbers | N10-「同窗核心涨幅小于 headline」 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI/CPI[2026-02, 2026-05] | True | True | 一致 |
| 300 | 06b_turning_numbers | N11-CORE_CPI 同比 2026-08 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI[2026-08-01, 2025-08-01] | 2.446163 | 2.4462 | 一致 |
| 301 | 06b_turning_numbers | N12-CORE_CPI 同比 2026-09(四位) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_CPI[2026-09-01, 2025-09-01] | 2.565841 | 2.5658 | 一致 |
| 302 | 06b_turning_numbers | N13-EA_HICP_YOY 同窗上行(百分点) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-02-01, 2026-05-01] | 1.3 | 1.3 | 一致 |
| 303 | 06b_turning_numbers | N14-INDPRO 同比 2025-11 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO[2025-11-01, 2024-11-01] | 1.754312 | 1.7543 | 一致 |
| 304 | 06b_turning_numbers | N15-INDPRO 同比 2026-02 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO[2026-02-01, 2025-02-01] | 0.797236 | 0.7972 | 一致 |
| 305 | 06b_turning_numbers | N16-INDPRO 三个月变化(百分点) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO[2025-11..2026-02] | -0.957076 | -0.9571 | 一致 |
| 306 | 06b_turning_numbers | N17-失业率 2025-11 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2025-11-01] | 4.5 | 4.5 | 一致 |
| 307 | 06b_turning_numbers | N18-失业率 2026-02 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2026-02-01] | 4.4 | 4.4 | 一致 |
| 308 | 06b_turning_numbers | N19-「就业端未同向走弱」(同窗失业率下降) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2025-11-01, 2026-02-01] | True | True | 一致 |
| 309 | 06b_turning_numbers | N20-「2026-03 见底后回升」: INDPRO 同比 2026 年内低点=2026-03, 其后各月均高于低点 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO[2026-01..2026-10] | True | True | 一致 |
| 310 | 06b_turning_numbers | N21-INDPRO 同比 2026-10 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.INDPRO[2026-10-01, 2025-10-01] | 2.149685 | 2.15 | 一致 |
| 311 | 06b_turning_numbers | N22-JP_POLICY_RATE 2026-04 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-04-01] | 0.727 | 0.727 | 一致 |
| 312 | 06b_turning_numbers | N23-JP_POLICY_RATE 2026-07 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-07-01] | 0.978 | 0.978 | 一致 |
| 313 | 06b_turning_numbers | N24-JP_POLICY_RATE 2026-06(过渡) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-06-01] | 0.841 | 0.841 | 一致 |
| 314 | 06b_turning_numbers | N25-「2026 年内第三个上行月均台阶(此前 2026-01 +17bp、2026-06 +11bp)」 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2025-09..2026-10] | True | True | 一致 |
| 315 | 06b_turning_numbers | N26-JP_POLICY_RATE 2026-09 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-09-01] | 1.043 | 1.043 | 一致 |
| 316 | 06b_turning_numbers | N27-JP_POLICY_RATE 2026-10 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-10-01] | 1.227 | 1.227 | 一致 |
| 317 | 06b_turning_numbers | N28-台阶 2026-09 变动(bp, 整数) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-08-01, 2026-09-01] | 6.6 | 7 | 一致 |
| 318 | 06b_turning_numbers | N29-台阶 2026-10 变动(bp, 整数) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-09-01, 2026-10-01] | 18.4 | 18 | 一致 |
| 319 | 07_facts | J1-「快照事实面仅有 2026-11-19 点值 JGB 2/5/10 年 1.853/2.235/2.87」 | root_overlay/data/daily/research_snapshot_20261123.json:facts[JGB2Y/JGB5Y/JGB10Y] | True | True | 一致 |
| 320 | 07_facts | J2-「序列库无历史」: series_store 无 JGB 序列 | root_overlay/data/daily/research_snapshot_20261123.json:series_store(键) | True | True | 一致 |
| 321 | 07_facts | J3-「未入证据索引」: 证据索引无 JGB 条目 | evidence_index.json[*].ref | True | True | 一致 |
| 322 | 07_facts | J4-注册表 economy=JP 面含 JGB2Y/5Y/10Y(在册)但快照无序列 →「序列库无历史」表述准确 | root_overlay/config/metric_registry.json:economy=JP | True | True | 一致 |
| 323 | 07_facts | J5-「本引擎无日本套息持仓…序列」: series_store 无套息持仓类序列 | root_overlay/data/daily/research_snapshot_20261123.json:series_store(键) | True | True | 一致 |
| 324 | 07_facts | J6-「无日美利差序列」: series_store 无利差/spread 类日美序列 | root_overlay/data/daily/research_snapshot_20261123.json:series_store(键) | True | True | 一致 |
| 325 | 07_facts | J7-「美联储目标区间上限…欧央行存款便利利率…未纳入本问证据索引」: DFEDTARU/ECB_DFR 不在证据索引 | evidence_index.json[*].ref | True | True | 一致 |
| 326 | 07_facts | J8-「本问计划指标面未纳入美欧政策利率序列」: plan.metrics 无 DFEDTARU/ECB_DFR | report.json:research_plan.metrics | True | True | 一致 |
| 327 | 07_facts | J9-「政策事件簇为空」 | report.json:research_plan.policy_event_clusters.clusters | True | True | 一致 |
| 328 | 07_facts | J10-「发布日历政策条目仅 2 条、均为日本央行实录」 | root_overlay/config/release_calendar.json:entries[*].decision_date/metric_id | True | True | 一致 |
| 329 | 07_facts | J11-「发布日历政策条目仅 2 条」条数 | root_overlay/config/release_calendar.json:entries[*].decision_date | 2 | 2 | 一致 |
| 330 | 07_facts | J12-「证据索引 63 行」行数 | evidence_index.json | 63 | 63 | 一致 |
| 331 | 07_facts | J13-「本问计划指标面」9 个指标 | report.json:research_plan.metrics | 9 | 9 | 一致 |
| 332 | 08_history | H1-reader_map.history_periods 为空数组 | agent_judgment.json:reader_map.history_periods | True | True | 一致 |
| 333 | 08_history | H2-history_zero_case_note 非空且写明「事后结果≠当时可知」「相似≠因果≠预测」 | agent_judgment.json:reader_map.history_zero_case_note | True | True | 一致 |
| 334 | 08_history | H3-引擎 analog 候选面在场(S6_analog 执行 ok, top 候选月非空)且受审稿全文未引用任何候选月 | report.json:steps[S6_analog].ok/.envelope.data.top[*].candidate_month; agent_judgment.json(全文) | True | True | 一致 |
| 335 | 09_scenarios | S0-截止日前已发布 EA_HICP_YOY 最新观测月 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY; 规则月末+16天 | 202610 | 202610 | 一致 |
| 336 | 09_scenarios | S0b-EA_HICP_YOY 最新值 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-10-01] | 4.0 | 4.0 | 一致 |
| 337 | 09_scenarios | S0c-截止日前已发布 CORE_PCE 同比最新值 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE[2026-09-01 同比] | 3.12116 | 3.12 | 一致 |
| 338 | 09_scenarios | S0d-TIPS_10Y 最新值 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.TIPS_10Y[≤2026-11-23] | 2.88 | 2.88 | 一致 |
| 339 | 09_scenarios | S0e-BEI_10Y 最新值 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BEI_10Y[≤2026-11-23] | 2.15 | 2.15 | 一致 |
| 340 | 09_scenarios | S1-EA_HICP_YOY 观测月 2026-11 的规则发布日 | report.json:research_plan.point_values.cells[EA_HICP_YOY].anchors.最新一期.publication_rule(月末+16天,推定) | "2026-12-16" | "2026-12-16" | 一致 |
| 341 | 09_scenarios | S1-EA_HICP_YOY 观测月 2026-12 的规则发布日 | report.json:research_plan.point_values.cells[EA_HICP_YOY].anchors.最新一期.publication_rule(月末+16天,推定) | "2027-01-16" | "2027-01-16" | 一致 |
| 342 | 09_scenarios | S1-EA_HICP_YOY 观测月 2027-01 的规则发布日 | report.json:research_plan.point_values.cells[EA_HICP_YOY].anchors.最新一期.publication_rule(月末+16天,推定) | "2027-02-16" | "2027-02-16" | 一致 |
| 343 | 09_scenarios | S2-「2027-01 观测月的规则发布日 2027-02-16 晚于期限 2027-02-15」 | agent_judgment.json:l4.scenarios[S1].rows.scenario; 规则月末+16天 | True | True | 一致 |
| 344 | 09_scenarios | S3-「规则发布日 2026-12-16、2027-01-16,均不晚于期限 2027-02-15」 | agent_judgment.json:l4.scenarios[S1].rows.falsification.threshold | True | True | 一致 |
| 345 | 09_scenarios | S4-两情景期限均为 2027-02-15 | agent_judgment.json:l4.scenarios[*].rows.trigger.deadline | True | True | 一致 |
| 346 | 09_scenarios | S5-S1 触发条件(EA≥4.2% 且 CORE_PCE≥3.2% 且 TIPS_10Y>3.0%)在截止日读数下未触发 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY/CORE_PCE/TIPS_10Y | True | True | 一致 |
| 347 | 09_scenarios | S6-S2 触发条件(EA≤3.4% 且 BEI_10Y<2.0%)在截止日读数下未触发 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY/BEI_10Y | True | True | 一致 |
| 348 | 09_scenarios | S7-S1 证伪线(连续两月 <3.0%)在截止日读数下未触发(最新 4.0≥3.0) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY[2026-10-01] | True | True | 一致 |
| 349 | 09_scenarios | S8-S2 证伪所需的 2026-11/2026-12 观测月在截止日已发布数(前瞻条件, 截止日尚不可判=相容) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY; 规则月末+16天 | 0 | 0 | 一致 |
| 350 | 09_scenarios | S9-S1 情景陈述界(EA≥3.5%、CORE_PCE≥3.0%)与截止日读数相容 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_HICP_YOY/CORE_PCE | True | True | 一致 |
| 351 | 09_scenarios | S10-两情景在区分指标 EA_HICP_YOY 上的预言方向相反(S1≥3.5% 对 S2<3.0%) | agent_judgment.json:l4.scenarios[*].rows.scenario | True | True | 一致 |
| 352 | 09_scenarios | S11-S1 证伪线 3.0% 在陈述与证伪两处一致; 缓冲带 3.0–3.5% | agent_judgment.json:l4.scenarios[S1] | True | True | 一致 |
| 353 | 09_scenarios | S12-S2 触发线 3.4%/证伪线 4.0%/陈述界 3.0% 在三处一致 | agent_judgment.json:l4.scenarios[S2] | True | True | 一致 |
| 354 | 09_scenarios | S13-两情景缓冲带互不重叠地定义了「既未触发也未证伪」区间(S1: 3.0–3.5; S2: 3.0–4.0) | agent_judgment.json:l4.scenarios[*].rows.falsification.threshold | True | True | 一致 |
| 355 | 09_scenarios | S14-情景点名的区分/敏感指标(EA_HICP_YOY/CORE_PCE/TIPS_10Y/BEI_10Y/JP_POLICY_RATE/SPX)均在冻结 series_store 在场 | root_overlay/data/daily/research_snapshot_20261123.json:series_store | True | True | 一致 |
| 356 | 09_scenarios | S15-S2 所述「与近一月观察(实际利率 +11bp 而风险资产回落)相反」: S2 方向为实际利率回落/风险资产修复, 与观察相反 | agent_judgment.json:l4.scenarios[S2].rows.asset_direction.direction; series_store.TIPS_10Y(+11bp)/SPX(回落) | True | True | 一致 |
| 357 | 09_scenarios | S16-S1/S2 资产方向预言相反(利率敏感资产: 走弱 对 修复; 美元: 偏强 对 走弱) | agent_judgment.json:l4.scenarios[*].rows.asset_direction.direction | True | True | 一致 |
| 358 | 09_scenarios | S17-引擎契约 six_checks: 两情景 overreach/falsifiable 均 VERIFIED | x_agent_judgment_meta.json:contract_verification.six_checks[item=S1/S2] | True | True | 一致 |
| 359 | 10_consistency | K1-agent_declaration「点值格(9格)」 | report.json:research_plan.point_values.cells | True | True | 一致 |
| 360 | 10_consistency | K2-agent_declaration「证据索引(63行)」 | evidence_index.json | True | True | 一致 |
| 361 | 10_consistency | K3-走位 anchor_echo 全部取值/观测月与点值格逐项一致 | agent_judgment.json:reader_map.regions[*].anchor_echo; report.json:…point_values.cells | True | True | 一致 |
| 362 | 10_consistency | K4-rates_decomposition 回贴=引擎三利率分解(-8/+11/-19, 窗 2026-10-20→2026-11-19) | agent_judgment.json:reader_map.rates_decomposition; report.json:research_plan.us_rates_trio | True | True | 一致 |
| 363 | 10_consistency | K5-asset_returns_echo 五行=引擎资产月窗(SPX/NIKKEI225/GOLD_F/DXY/VIX) | agent_judgment.json:reader_map.asset_returns_echo; report.json:research_plan.asset_moves.rows | True | True | 一致 |
| 364 | 10_consistency | K6-对质表裁定序列=[支持竞争解释, 尚不能区分, 支持主解释] 与 quality_gate_notes「支持主解释×1/支持竞争解释×1/尚不能区分×1」一致 | agent_judgment.json:reader_map.transmission[*].links[*].face_off_verdict | True | True | 一致 |
| 365 | 10_consistency | K7-机制链三环证据分级=[E1,E2,E2] 与 quality_gate_notes「E1/E2/E2」一致 | agent_judgment.json:l3.mechanism_chains[0].links[*].evidence_level | True | True | 一致 |
| 366 | 10_consistency | K8-「L3 三条矛盾陈述各并列 2 种解释」 | agent_judgment.json:l3.contradictions[*].competing_explanations | True | True | 一致 |
| 367 | 10_consistency | K9-链1 裁定「支持竞争解释」: 主解释预期 BEI_10Y 走高/高位, 竞争预期走低/持平; 在场三窗 BEI_10Y 均回落 → 与裁定方向一致 | agent_judgment.json:reader_map.transmission[0].links[0]; series_store.BEI_10Y(⑤-A18: -19/-14/-11bp) | True | True | 一致 |
| 368 | 10_consistency | K10-链3 裁定「支持主解释」: 主解释预期 TIPS_10Y 上行与 SPX 走弱同现, 竞争预期 TIPS_10Y 走低; 在场 TIPS_10Y +22bp、SPX -5.51% → 与裁定方向一致 | agent_judgment.json:reader_map.transmission[0].links[2]; series_store.TIPS_10Y/SPX(⑤-A20/⑤-B3) | True | True | 一致 |
| 369 | 10_consistency | K11-链2 两解释在 TIPS_10Y 上预期方向不分立而裁定「尚不能区分」(未冒充支持任一侧) | agent_judgment.json:reader_map.transmission[0].links[1] | True | True | 一致 |
| 370 | 10_consistency | K12-总判断「距上次调整…(日历核验覆盖止于 2026-10-30,其后至截止日的 24 天引擎日历无条目)」: 2026-11-23−2026-10-30=24 天 | root_overlay/config/release_calendar.json:entries[RC-JP-BOJ-MAINT-2026-10].decision_date | True | True | 一致 |
| 371 | 10_consistency | K13-走位 US「中间 2026-09 为 4.2」 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.UNEMPLOYMENT[2026-09-01] | True | True | 一致 |
| 372 | 10_consistency | K14-走位 EA「三个月上行 1.1 个百分点」(HICP 2.9→4.0) | root_overlay/data/daily/research_snapshot_20261123.json.EA_HICP_YOY[2026-07-01, 2026-10-01] | 1.1 | 1.1 | 一致 |
| 373 | 10_consistency | K14b-「为两地通胀面最大变化」: EA +1.1 大于美国 headline/核心 CPI/核心 PCE 同窗三个月变动 | root_overlay/data/daily/research_snapshot_20261123.json.EA_HICP_YOY/CPI/CORE_CPI/CORE_PCE(同比, 两锚同窗) | True | True | 一致 |
| 374 | 10_consistency | K15-总判断「通胀…欧元区幅度更大」在 headline/核心/核心PCE 三口径同向(三个月变动 EA 均最大) | 同 K14b | True | True | 一致 |
| 375 | 10b_render | R1-判断正文串(陈述/并列解释/机制链/情景/走位/传导/类比注记)在读者报告(MAP_REPORT/FULL_REPORT/report)逐字在场条数 | agent_judgment.json(l3/l4/reader_map) ↔ MAP_REPORT.md/FULL_REPORT.md/report.md | 59 | 59 | 一致 |
| 376 | 10b_render | R3-美国走位段(渲染面)未含 CORE_PCE(83 天/60 天)与 US_REAL_GDP(145 天/120 天)的契约 STALE 滞后披露(该披露仅在 quality_gate_notes[3]) | agent_judgment.json:reader_map.regions[US].from_to; quality_gate_notes[3] | True | True | 一致 |
| 377 | 10b_render | R2-「verdict_note 字段与转折面 narrative 字段不进渲染」: 该类串在三个渲染文件中均不出现 | agent_judgment.json:reader_map.transmission[*].links[*].verdict_note; reader_map.turnings[*].narrative | True | True | 一致 |
| 378 | 12_time | Z0-快照 research_as_of=2026-11-23T22:53:47+08:00(与受审稿所写一致) | root_overlay/data/daily/research_snapshot_20261123.json:research_as_of | True | True | 一致 |
| 379 | 12_time | Z1-截止时点 纽约 本地时间 | root_overlay/data/daily/research_snapshot_20261123.json:research_as_of; IANA 时区库 America/New_York | "09:53" | "09:53" | 一致 |
| 380 | 12_time | Z1-截止时点 法兰克福 本地时间 | root_overlay/data/daily/research_snapshot_20261123.json:research_as_of; IANA 时区库 Europe/Berlin | "15:53" | "15:53" | 一致 |
| 381 | 12_time | Z1-截止时点 东京 本地时间 | root_overlay/data/daily/research_snapshot_20261123.json:research_as_of; IANA 时区库 Asia/Tokyo | "23:53" | "23:53" | 一致 |
| 382 | 12_time | Z1-截止时点 上海 本地时间 | root_overlay/data/daily/research_snapshot_20261123.json:research_as_of; IANA 时区库 Asia/Shanghai | "22:53" | "22:53" | 一致 |
| 383 | 12_time | Z2-截止时点纽约 09:30–16:00 常规交易时段进行中(美股盘中) | research_as_of → America/New_York | True | True | 一致 |
| 384 | 12_time | Z3-截止时点法兰克福 09:00–17:30 常规交易时段进行中(德法股指盘中) | research_as_of → Europe/Berlin | True | True | 一致 |
| 385 | 12_time | Z4-「NIKKEI225 止于 2026-11-20 收盘」: 序列末观测日=2026-11-20(周五) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.NIKKEI225.dates[-1] | True | True | 一致 |
| 386 | 12_time | Z5-SPX 序列末观测日=2026-11-23(截止日当日值, 受审稿标注为盘中快照) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.SPX.dates[-1] | True | True | 一致 |
| 387 | 12_time | Z5-VIX 序列末观测日=2026-11-23(截止日当日值, 受审稿标注为盘中快照) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.VIX.dates[-1] | True | True | 一致 |
| 388 | 12_time | Z5-GOLD_F 序列末观测日=2026-11-23(截止日当日值, 受审稿标注为盘中快照) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.GOLD_F.dates[-1] | True | True | 一致 |
| 389 | 12_time | Z5-DXY 序列末观测日=2026-11-23(截止日当日值, 受审稿标注为盘中快照) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.DXY.dates[-1] | True | True | 一致 |
| 390 | 12_time | Z5-USDJPY 序列末观测日=2026-11-23(截止日当日值, 受审稿标注为盘中快照) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.USDJPY.dates[-1] | True | True | 一致 |
| 391 | 12_time | Z5-EURUSD 序列末观测日=2026-11-23(截止日当日值, 受审稿标注为盘中快照) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EURUSD.dates[-1] | True | True | 一致 |
| 392 | 12_time | Z5-BRENT_F 序列末观测日=2026-11-23(截止日当日值, 受审稿标注为盘中快照) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.BRENT_F.dates[-1] | True | True | 一致 |
| 393 | 12_time | Z6-全库 92 条序列无晚于截止日 2026-11-23 的观测(无事后信息混入) | root_overlay/data/daily/research_snapshot_20261123.json:series_store[*].dates[-1] | True | True | 一致 |
| 394 | 13_stale | E1-契约 verdicts 中非 VERIFIED 项恰为 CORE_PCE 与 US_REAL_GDP 两处 STALE | report.json:agent_judgment.contract_verification.verdicts | [["C1-INFL-SYNC.statement", "CORE_PCE", "130.902", "STALE", "recompute:Fact 直读 CORE_PCE@2026-09-01=130.902"], ["C2-GROWTH-STABLE.statement", "US_REAL_GDP", "24611.077", "STALE", "recompute:Fact 直读 US_REAL_GDP@2026-07-01=24611.077"]] | "CORE_PCE 130.902 / US_REAL_GDP 24611.077 两处 STALE" | 一致 |
| 395 | 13_stale | E1-契约 STALE 项数值一致(value==expected) | report.json:agent_judgment.contract_verification.verdicts | [["CORE_PCE", 130.902, 130.902], ["US_REAL_GDP", 24611.077, 24611.077]] | True | 一致 |
| 396 | 13_stale | E1-CORE_PCE 观测 2026-09-01 距截止日 83 天 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE.dates[-1] ; research_as_of | 83 | 83 | 一致 |
| 397 | 13_stale | E1-US_REAL_GDP 观测 2026-07-01 距截止日 145 天 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.US_REAL_GDP.dates[-1] | 145 | 145 | 一致 |
| 398 | 13_stale | E1-注册表最大日历滞后: CORE_PCE=60 / US_REAL_GDP=120 / EA_REAL_GDP_YOY=120 | root_overlay/config/metric_registry.json:metrics[*].freshness.max_calendar_lag_days | {"CORE_PCE": 60, "US_REAL_GDP": 120, "EA_REAL_GDP_YOY": 120} | {"CORE_PCE": 60, "US_REAL_GDP": 120, "EA_REAL_GDP_YOY": 120} | 一致 |
| 399 | 13_stale | E1-CORE_PCE 倍数 83/60(报告 1.4) | 83 天 / 注册表 60 天 | 1.383333 | 1.4 | 一致 |
| 400 | 13_stale | E1-US_REAL_GDP 倍数 145/120(报告 1.2) | 145 天 / 注册表 120 天 | 1.208333 | 1.2 | 一致 |
| 401 | 13_stale | E1-STALE 项均为该序列截止日前最新已发布观测 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CORE_PCE/US_REAL_GDP.dates | ["2026-09-01", "2026-07-01"] | ["2026-09-01", "2026-07-01"] | 一致 |
| 402 | 13_stale | E1-EA_REAL_GDP_YOY 最新观测 2026-07-01 距截止日 145 天(与 US_REAL_GDP 同龄同倍数) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_REAL_GDP_YOY.dates[-1] | [145, 120] | [145, 120] | 一致 |
| 403 | 14_gate | F1-Gate A 状态 DEGRADED | root_overlay/data/daily/research_snapshot_20261123.json:gate_a.status | "DEGRADED" | "DEGRADED" | 一致 |
| 404 | 14_gate | F1-核心缺口 0 项 | root_overlay/data/daily/research_snapshot_20261123.json:gate_a.core_missing | [] | [] | 一致 |
| 405 | 14_gate | F1-非核心缺口七项(名单一致) | root_overlay/data/daily/research_snapshot_20261123.json:gate_a.noncore_missing | ["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"] | ["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"] | 一致 |
| 406 | 14_gate | F1-非核心降级八项(名单一致) | root_overlay/data/daily/research_snapshot_20261123.json:gate_a.noncore_degraded | ["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"] | ["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"] | 一致 |
| 407 | 14_gate | F1-EA_REAL_GDP_YOY 在非核心缺口清单内但序列库有存量观测 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.EA_REAL_GDP_YOY | [true, 123, ["2026-07-01", 1.28]] | [true, "有存量观测, 最新 2026-07-01"] | 一致 |
| 408 | 14_gate | F1-EA_REAL_GDP_YOY 在事实面缺席(facts 无该指标) | root_overlay/data/daily/research_snapshot_20261123.json:facts[metric_id=EA_REAL_GDP_YOY] | [] | [] | 一致 |
| 409 | 14_gate | F2-任务窗 2026-11-01..11-30 内 9 个计划指标观测数均为 0 | root_overlay/data/daily/research_snapshot_20261123.json:series_store[US_REAL_GDP,UNEMPLOYMENT,INDPRO,CPI,CORE_CPI,CORE_PCE,EA_REAL_GDP_YOY,EA_HICP_YOY,JP_POLICY_RATE].dates | {"US_REAL_GDP": 0, "UNEMPLOYMENT": 0, "INDPRO": 0, "CPI": 0, "CORE_CPI": 0, "CORE_PCE": 0, "EA_REAL_GDP_YOY": 0, "EA_HICP_YOY": 0, "JP_POLICY_RATE": 0} | "all 0" | 一致 |
| 410 | 14_gate | F3-证据引用计数: 矛盾陈述/机制链/情景 | agent_judgment.json:l3.contradictions[*].evidence_refs; l3.mechanism_chains[*].links[*].evidence_refs; l4.scenarios[*].rows | {"contradictions": 11, "mechanism": 4, "scenarios_all": 9, "scenarios_unique": 5, "total(c+m+uniq_s)": 20} | {"contradictions": 10, "mechanism": 4, "scenarios": 5, "total": 19} | 偏离 |
| 411 | 14_gate | F3-矛盾陈述+机制链 evidence_refs 全部解析到证据索引 | evidence_index.json[*].ref | [] | [] | 一致 |
| 412 | 17_sync | Y1-「美欧通胀同月抬升」: 候选面 CPI 与 EA_HICP_YOY 的最大变动窗同为 2026-02..2026-05 | report.json:research_plan.turning_candidates.candidates[metric_id=CPI｜EA_HICP_YOY] | True | True | 一致 |
| 413 | 17_sync | Y2-同窗内美欧同比逐月同向(2026-03..05 各月相对窗启 2026-02 均上行)→「同月抬升」与序列面一致 | root_overlay/data/daily/research_snapshot_20261123.json:series_store.CPI(同比直算)/EA_HICP_YOY[2026-02..2026-05] | True | True | 一致 |
| 414 | 17_sync | Y3-「美欧通胀环境较 3 个月前同步走高」: 通胀维四格(美 CPI/核心 CPI/核心 PCE、欧 HICP)两锚间全部上行, 且格内同比与 series_store 直算一致 | report.json:research_plan.point_values.cells[metric_id].anchors; series_store 直算 | True | True | 一致 |
| 415 | 17_sync | Y4-增长维两锚方向(美 GDP 同比微降/失业率持平/工业生产同比回升;欧 GDP 同比不降)→「大体平稳」与序列面不相左(各变动<0.9pp 且正负互见) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.US_REAL_GDP/UNEMPLOYMENT/INDPRO[2026-07→2026-10]、US_REAL_GDP/EA_REAL_GDP_YOY[2026-04→2026-07] | True | True | 一致 |
| 416 | 17_sync | Y6-受审稿未对美欧政策维下同步/分化断言(表述为「不可判」),且引擎政策事件簇为空(无跨国同步面可供引用) | report.json:research_plan.policy_event_clusters.clusters; agent_judgment.json:reader_map.turnings | True | True | 一致 |
| 417 | 17_sync | Y7-引擎 dimension_gaps 恰为 JP_POLICY_TARGET registry_absent 一条,与受审稿的官方目标缺席披露一致 | report.json:research_plan.dimension_gaps; agent_judgment.json:l3.contradictions[C3-JP-POLICY] | True | True | 一致 |
| 418 | 17_sync | Y8-引擎 dimension_gaps 条数 | report.json:research_plan.dimension_gaps | 1 | 1 | 一致 |
| 419 | 17_sync | Y9-C3 竞争解释容差依据「2026-02 至 2026-05 与 2026-08 的相邻月均差均不超过 0.001」(月均台阶按落入月计: 2026-08 档=2026-07→2026-08) | root_overlay/data/daily/research_snapshot_20261123.json:series_store.JP_POLICY_RATE[2026-02..2026-05,2026-07,2026-08] | True | True | 一致 |
