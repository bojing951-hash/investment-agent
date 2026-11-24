# 复算点逐点表(比对点 403, 辅助点 27; 由 s17a_data.py 重建)

| 编号 | 出处(只读面: 文件 · 面/键) | 复算项(序列ID@观测日/月 或 字段) | 直算值 | 受审稿值 | 判定 |
|---|---|---|---|---|---|
| E01 | research_snapshot_20261123.json series_store | WTI_F 锚 obs | 2026-08-21 | 2026-08-21 | 一致 |
| E02 | research_snapshot_20261123.json series_store | WTI_F@2026-08-21 | 87.06 | 87.06 | 一致 |
| E03 | research_snapshot_20261123.json series_store | WTI_F@2026-10-30 | 104.12 | 104.12 | 一致 |
| E04 | research_snapshot_20261123.json series_store | WTI_F 10-30 vs 锚 % | 19.60 | 19.6 | 一致 |
| E05 | research_snapshot_20261123.json series_store | WTI_F@2026-11-23 | 82.02 | 82.02 | 一致 |
| E06 | research_snapshot_20261123.json series_store | WTI_F 11-23 vs 锚 % | -5.79 | -5.79 | 一致 |
| E07 | research_snapshot_20261123.json series_store | WTI_F 11-23 vs 10-30 % | -21.23 | -21.23 | 一致 |
| E08 | research_snapshot_20261123.json series_store | BRENT_F 锚 obs 2026-08-21 | 94.39 | 94.39 | 一致 |
| E09 | research_snapshot_20261123.json series_store | BRENT_F@2026-10-30 | 117.64 | 117.64 | 一致 |
| E10 | research_snapshot_20261123.json series_store | BRENT_F 10-30 vs 锚 % | 24.63 | 24.63 | 一致 |
| E11 | research_snapshot_20261123.json series_store | BRENT_F@2026-11-23 | 88.19 | 88.19 | 一致 |
| E12 | research_snapshot_20261123.json series_store | BRENT_F 11-23 vs 锚 % | -6.57 | -6.57 | 一致 |
| E13 | research_snapshot_20261123.json series_store | BRENT_F 11-23 vs 10-30 % | -25.03 | -25.03 | 一致 |
| E14 | research_snapshot_20261123.json series_store | WTI_SPOT_M@2026-08 | 83.9 | 83.9 | 一致 |
| E15 | research_snapshot_20261123.json series_store | WTI_SPOT_M@2026-10 | 102.07 | 102.07 | 一致 |
| E16 | research_snapshot_20261123.json series_store | WTI_SPOT_M 10月 vs 8月 % | 21.66 | 21.66 | 一致 |
| E17 | research_snapshot_20261123.json series_store | WTI_F 2026-08 自然月均值 | 82.45 | 82.45 | 一致 |
| E18 | research_snapshot_20261123.json series_store | WTI_F 2026-10 自然月均值 | 96.94 | 96.94 | 一致 |
| E19 | research_snapshot_20261123.json series_store | WTI_F@2026-09-16 | 102.43 | 102.43 | 一致 |
| E20 | research_snapshot_20261123.json series_store | WTI_F 09-16 vs 锚 % | 17.65 | 17.65 | 一致 |
| E21 | research_snapshot_20261123.json series_store | WTI_F@2026-09-18 | 100.30 | 100.3 | 一致 |
| E22 | research_snapshot_20261123.json series_store | WTI_F 09-18 vs 锚 % | 15.21 | 15.21 | 一致 |
| E23 | research_snapshot_20261123.json series_store | WTI_F 2026-09-01..2026-10-31 全部观测 > 锚 87.06 (n=43, min=88.28) | True | True | 一致 |
| E24 | research_snapshot_20261123.json series_store | WTI_F 11-02 起首个跌破锚的观测日 | 2026-11-09 | 2026-11-09 | 一致 |
| E25 | research_snapshot_20261123.json series_store | WTI_F 2026-11-09..11-23 全部 < 锚(受审稿『11-09 起再度跌破该锚』的字面持续性; 实测 11 个观测中 9 个低于锚, 11-12=88.74、11-13=88.56 回到锚上方) | False | True | 偏离 |
| E26 | research_snapshot_20261123.json series_store | WTI_F 2026-11-02..11-06(跌破前) 全部 > 锚 | True | True | 一致 |
| E27 | research_snapshot_20261123.json series_store | WTI_F 8 月底(锚后至 8-31)有短暂低于锚的观测 | True | True | 一致 |
| E28 | research_snapshot_20261123.json series_store | WTI_SPOT_M 末观测月 | 2026-10 | 2026-10 | 一致 |
| E29 | research_snapshot_20261123.json series_store | WTI_F 2026-09-01..2026-10-31 观测全部 > 锚(受审稿『期货 9 月初至 10 月底的观测全部高于三个月前锚』) | True | True | 一致 |
| P01 | research_snapshot_20261123.json series_store | DFEDTARU@<=2026-08-23 (obs 2026-08-23) | 3.75 | 3.75 | 一致 |
| P02 | research_snapshot_20261123.json series_store | DFEDTARU anchor obs date | 2026-08-23 | 2026-08-23 | 一致 |
| P03 | research_snapshot_20261123.json series_store | DFEDTARU@<=2026-11-23 (obs 2026-11-23) | 4.00 | 4.0 | 一致 |
| P04 | research_snapshot_20261123.json series_store | DFEDTARU latest obs date | 2026-11-23 | 2026-11-23 | 一致 |
| P05 | research_snapshot_20261123.json series_store | DFEDTARU 上限变动(bp)=(b-a)*100 | 25 | 25 | 一致 |
| P06 | research_snapshot_20261123.json series_store | DFEDTARU 窗内变动点1 日期(生效) | 2026-09-17 | 2026-09-17 | 一致 |
| P07 | research_snapshot_20261123.json series_store | DFEDTARU 变动点1 from | 3.75 | 3.75 | 一致 |
| P08 | research_snapshot_20261123.json series_store | DFEDTARU 变动点1 to | 4.00 | 4.0 | 一致 |
| P09 | research_snapshot_20261123.json series_store | DFEDTARU 变动点1 幅度(bp) | 25 | 25 | 一致 |
| P10 | research_snapshot_20261123.json series_store | 决议日=生效日前一日 | 2026-09-16 | 2026-09-16 | 一致 |
| P11 | research_snapshot_20261123.json series_store | DFEDTARU 窗内变动点0 日期(生效) | 2025-12-11 | 2025-12-11 | 一致 |
| P12 | research_snapshot_20261123.json series_store | DFEDTARU 变动点0 from | 4.00 | 4.0 | 一致 |
| P13 | research_snapshot_20261123.json series_store | DFEDTARU 变动点0 to | 3.75 | 3.75 | 一致 |
| P14 | research_snapshot_20261123.json series_store | DFEDTARU 变动点0 幅度(bp) | -25 | -25 | 一致 |
| P15 | research_snapshot_20261123.json series_store | 决议日=生效日前一日 | 2025-12-10 | 2025-12-10 | 一致 |
| P16 | research_snapshot_20261123.json series_store | DFEDTARU 近一年窗变动点数=2 | True | True | 一致 |
| P17 | research_snapshot_20261123.json series_store | DFEDTARU 近一年净变动(bp) | 0 | 0 | 一致 |
| P18 | research_snapshot_20261123.json series_store | DFF 三个月前锚 obs(发布=观测日+1 ≤ 2026-08-23 的最后观测) | 2026-08-22 | 2026-08-22 | 一致 |
| P19 | research_snapshot_20261123.json series_store | DFF@2026-08-22 | 3.63 | 3.63 | 一致 |
| P20 | research_snapshot_20261123.json series_store | DFF 最新 obs(发布=观测日+1 ≤ 2026-11-23 的最后观测) | 2026-11-19 | 2026-11-19 | 一致 |
| P21 | research_snapshot_20261123.json series_store | DFF@2026-11-19 | 3.88 | 3.88 | 一致 |
| P22 | research_snapshot_20261123.json series_store | DFF@2026-09-16 | 3.63 | 3.63 | 一致 |
| P23 | research_snapshot_20261123.json series_store | DFF@2026-09-17 | 3.88 | 3.88 | 一致 |
| P24 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2025-11 | 0.478 | 0.478 | 一致 |
| P25 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2025-12 | 0.557 | 0.557 | 一致 |
| P26 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2026-04 | 0.727 | 0.727 | 一致 |
| P27 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2026-07 | 0.978 | 0.978 | 一致 |
| P28 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2026-08 | 0.977 | 0.977 | 一致 |
| P29 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2026-09 | 1.043 | 1.043 | 一致 |
| P30 | research_snapshot_20261123.json series_store | JP_POLICY_RATE@2026-10 | 1.227 | 1.227 | 一致 |
| P31 | research_snapshot_20261123.json series_store | JP_POLICY_RATE 三个月净变动(bp)=(10月-7月)*100 | 25 | 25 | 一致 |
| P32 | research_snapshot_20261123.json series_store | JP_POLICY_RATE 近12个月净变动(bp) | 75 | 75 | 一致 |
| P33 | research_snapshot_20261123.json series_store | JP_POLICY_RATE 自窗内首观测起算(bp) | 67 | 67 | 一致 |
| P34 | research_snapshot_20261123.json series_store | JP_POLICY_RATE 12月窗变动点=6 个且幅度=[8,17,11,14,7,18] | True | True | 一致 |
| P35 | research_snapshot_20261123.json series_store | JP_POLICY_RATE 2026-07 - 2026-04 (pp) | 0.251 | 0.251 | 一致 |
| P36 | release_calendar.json entries[*] | 存在日本央行 2026-09 目标条目 (决议 2026-09-18) | True | True | 一致 |
| P37 | release_calendar.json entries[*] | 生效 2026-09-24 | True | True | 一致 |
| P38 | release_calendar.json entries[*] | 目标水平 1.25 | True | True | 一致 |
| P39 | release_calendar.json entries[*] | 2026-10-30 维持条目 | True | True | 一致 |
| P40 | release_calendar.json entries[*] | 维持条目无生效日 | True | True | 一致 |
| P43 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 两决议同一 ISO 周 | True | True | 一致 |
| P44 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 两决议相隔天数 | 2 | 2 | 一致 |
| P45 | research_snapshot_20261123.json series_store | CN_LPR_1Y 锚 obs | 2026-08-20 | 2026-08-20 | 一致 |
| P46 | research_snapshot_20261123.json series_store | CN_LPR_1Y@2026-08-20 | 3.00 | 3.0 | 一致 |
| P47 | research_snapshot_20261123.json series_store | CN_LPR_1Y 最新 obs | 2026-11-20 | 2026-11-20 | 一致 |
| P48 | research_snapshot_20261123.json series_store | CN_LPR_1Y@2026-11-20 | 3.00 | 3.0 | 一致 |
| P49 | research_snapshot_20261123.json series_store | CN_LPR_1Y 序列末观测 | 2026-11-20 | 2026-11-20 | 一致 |
| P50 | research_snapshot_20261123.json series_store | CN_LPR_1Y 2026-08-20..2026-11-20 全部观测均为 3.0 (n=4) | True | True | 一致 |
| P51 | release_calendar.json entries[RC-CN-LPR-2026M11] | 日期 2026-11-20 / 09:00 | True | True | 一致 |
| P52 | release_calendar.json entries | 无 2026-08 LPR 实录条目(锚发布日属官方惯例) | True | True | 一致 |
| P53 | research_snapshot_20261123.json series_store | CN_OMO_7D 锚 obs | 2026-08-21 | 2026-08-21 | 一致 |
| P54 | research_snapshot_20261123.json series_store | CN_OMO_7D@2026-08-21 | 1.40 | 1.4 | 一致 |
| P55 | research_snapshot_20261123.json series_store | CN_OMO_7D 末观测 | 2026-10-30 | 2026-10-30 | 一致 |
| P56 | research_snapshot_20261123.json series_store | CN_OMO_7D@2026-10-30 | 1.40 | 1.4 | 一致 |
| P57 | research_snapshot_20261123.json series_store | CN_OMO_7D 末观测滞后天数(=2026-11-23-末观测) | 24 | 24 | 一致 |
| P58 | research_snapshot_20261123.json series_store | CN_OMO_7D 2026-08-21 之后全部观测=1.4 (n=34) | True | True | 一致 |
| P59 | research_snapshot_20261123.json series_store | CN_POLICY_OVERNIGHT 首观测 | 2026-11-02 | 2026-11-02 | 一致 |
| P60 | research_snapshot_20261123.json series_store | CN_POLICY_OVERNIGHT 末观测 | 2026-11-23 | 2026-11-23 | 一致 |
| P61 | research_snapshot_20261123.json series_store | CN_POLICY_OVERNIGHT@末观测 | 1.25 | 1.25 | 一致 |
| P62 | research_snapshot_20261123.json series_store | CN_POLICY_OVERNIGHT 在 2026-08-23 前无观测 | True | True | 一致 |
| P63 | research_snapshot_20261123.json series_store | series_store 无 EA_REAL_GDP_YOY | True | True | 一致 |
| P64 | research_snapshot_20261123.json series_store | series_store 无 EA_HICP_YOY | True | True | 一致 |
| P65 | research_snapshot_20261123.json series_store | series_store 无 ECB_MRO | True | True | 一致 |
| P66 | research_snapshot_20261123.json series_store | series_store 无 ECB_DFR | True | True | 一致 |
| P67 | research_snapshot_20261123.json series_store | series_store 无 BUND_10Y | True | True | 一致 |
| P68 | research_snapshot_20261123.json series_store | series_store 无 BUND_2Y | True | True | 一致 |
| P69 | research_snapshot_20261123.json series_store | series_store 无 JP_POLICY_TARGET | True | True | 一致 |
| P70 | metric_registry.json metrics[*].metric_id | 注册表无 JP_POLICY_TARGET | True | True | 一致 |
| P71 | release_calendar.json entries[*].id/kind | 冻结日历无美国政策条目、无 FOMC 纪要条目(条目 id 仅 2025SHUTDOWN 数据发布/EA-HICP/JP-BOJ/CN-LPR) | True | True | 一致 |
| P72 | report.json research_plan.policy_doc_facts | FOMC-MINUTES-2026-10 发布 2026-11-18, basis=user_directive | True | True | 一致 |
| G01 | research_snapshot_20261123.json series_store | US_REAL_GDP@2026-07 | 24611.077 | 24611.077 | 一致 |
| G02 | research_snapshot_20261123.json series_store | US_REAL_GDP@2026-04 | 24408.011 | 24408.011 | 一致 |
| G03 | research_snapshot_20261123.json series_store | US_REAL_GDP 同比 2026-07 (基期 2025-07) % | 2.07 | 2.07 | 一致 |
| G04 | research_snapshot_20261123.json series_store | US_REAL_GDP 同比 2026-04 (基期 2025-04) % | 2.19 | 2.19 | 一致 |
| G05 | research_snapshot_20261123.json series_store | US_REAL_GDP 末观测季 | 2026-07 | 2026-07 | 一致 |
| G06 | research_snapshot_20261123.json series_store | UNEMPLOYMENT@2026-07 | 4.1 | 4.1 | 一致 |
| G07 | research_snapshot_20261123.json series_store | UNEMPLOYMENT@2026-10 | 4.1 | 4.1 | 一致 |
| G08 | research_snapshot_20261123.json series_store | UNEMPLOYMENT 末观测月 | 2026-10 | 2026-10 | 一致 |
| G09 | research_snapshot_20261123.json series_store | INDPRO@2026-10 | 103.3954 | 103.3954 | 一致 |
| G10 | research_snapshot_20261123.json series_store | INDPRO@2026-07 | 103.1675 | 103.1675 | 一致 |
| G11 | research_snapshot_20261123.json series_store | INDPRO 同比 2026-10 % | 2.15 | 2.15 | 一致 |
| G12 | research_snapshot_20261123.json series_store | INDPRO 同比 2026-07 % | 1.25 | 1.25 | 一致 |
| G13 | research_snapshot_20261123.json series_store | INDPRO 末观测月 | 2026-10 | 2026-10 | 一致 |
| G14 | research_snapshot_20261123.json series_store | CN_PMI_MFG@2026-07 | 49.2 | 49.2 | 一致 |
| G15 | research_snapshot_20261123.json series_store | CN_PMI_MFG@2026-10 | 49.3 | 49.3 | 一致 |
| G16 | research_snapshot_20261123.json series_store | JP_REAL_GDP_YOY@2026-04 | 0.80 | 0.8 | 一致 |
| G17 | research_snapshot_20261123.json series_store | JP_REAL_GDP_YOY@2026-07 | 1.16 | 1.16 | 一致 |
| G18 | research_snapshot_20261123.json series_store | JP_REAL_GDP_YOY 末观测季 | 2026-07 | 2026-07 | 一致 |
| G19 | research_snapshot_20261123.json series_store | 两期 PMI 均在荣枯线下方(49.2、49.3 < 50) | True | True | 一致 |
| I01 | research_snapshot_20261123.json series_store | JP_CPI_YOY@2026-07 | 1.97 | 1.97 | 一致 |
| I02 | research_snapshot_20261123.json series_store | JP_CPI_YOY@2026-10 | 2.44 | 2.44 | 一致 |
| I03 | research_snapshot_20261123.json series_store | JP_CPI_YOY 末观测月 | 2026-10 | 2026-10 | 一致 |
| I04 | research_snapshot_20261123.json series_store | JP_CPI_TOKYO_YOY@2026-07 | 1.85 | 1.85 | 一致 |
| I05 | research_snapshot_20261123.json series_store | JP_CPI_TOKYO_YOY@2026-10 | 2.73 | 2.73 | 一致 |
| I06 | research_snapshot_20261123.json series_store | JP_CPI_TOKYO_YOY@2026-06 | 1.6 | 1.6 | 一致 |
| I07 | research_snapshot_20261123.json series_store | JP_CPI_TOKYO_YOY@2026-09 | 2.69 | 2.69 | 一致 |
| I08 | research_snapshot_20261123.json series_store | 东京都同比 2026-09 - 2026-06 (pp) | 1.09 | 1.09 | 一致 |
| I10 | research_snapshot_20261123.json series_store | CPI@2026-10 | 337.476 | 337.476 | 一致 |
| I11 | research_snapshot_20261123.json series_store | CPI@2026-07 | 332.813 | 332.813 | 一致 |
| I12 | research_snapshot_20261123.json series_store | CPI 无 2025-10 观测(同比基期缺) | True | True | 一致 |
| I13 | research_snapshot_20261123.json series_store | CPI 同比 2026-09 (基期 2025-09) % | 3.72 | 3.72 | 一致 |
| I14 | research_snapshot_20261123.json series_store | CPI 同比 2026-07 (基期 2025-07) % | 3.30 | 3.3 | 一致 |
| I15 | research_snapshot_20261123.json series_store | CPI 2026-10 为最新月且其同比不可得、2026-09 为最近有效同比 | True | True | 一致 |
| I16 | research_snapshot_20261123.json series_store | CORE_CPI@2026-10 | 339.9 | 339.9 | 一致 |
| I17 | research_snapshot_20261123.json series_store | CORE_CPI@2026-07 | 336.789 | 336.789 | 一致 |
| I18 | research_snapshot_20261123.json series_store | CORE_CPI 无 2025-10 观测 | True | True | 一致 |
| I19 | research_snapshot_20261123.json series_store | CORE_CPI 同比 2026-09 % | 2.57 | 2.57 | 一致 |
| I20 | research_snapshot_20261123.json series_store | CORE_CPI 同比 2026-07 % | 2.47 | 2.47 | 一致 |
| I21 | research_snapshot_20261123.json series_store | CORE_PCE@2026-09 | 130.902 | 130.902 | 一致 |
| I22 | research_snapshot_20261123.json series_store | CORE_PCE@2026-06 | 129.969 | 129.969 | 一致 |
| I23 | research_snapshot_20261123.json series_store | CORE_PCE 同比 2026-06 % | 3.04 | 3.04 | 一致 |
| I24 | research_snapshot_20261123.json series_store | CORE_PCE 同比 2026-09 % | 3.12 | 3.12 | 一致 |
| I25 | research_snapshot_20261123.json series_store | CORE_PCE 末观测月 | 2026-09 | 2026-09 | 一致 |
| I26 | research_snapshot_20261123.json series_store | CN_CPI_YOY@2026-07 | 0.5 | 0.5 | 一致 |
| I27 | research_snapshot_20261123.json series_store | CN_CPI_YOY@2026-10 | 0.7 | 0.7 | 一致 |
| I28 | research_snapshot_20261123.json series_store | CN_PPI_YOY@2026-07 | 3.5 | 3.5 | 一致 |
| I29 | research_snapshot_20261123.json series_store | CN_PPI_YOY@2026-10 | 5.7 | 5.7 | 一致 |
| I30 | research_snapshot_20261123.json series_store | CN_CPI_YOY@2026-10 序列日期(=点值格观测日 2026-10-01; 证据索引标签 2026-10-31 为期末口径, 受审稿已披露两口径不同) | 2026-10-01 | 2026-10-01 | 一致 |
| I30b | report.json evidence_index[*].ref | 证据索引对 CN_CPI_YOY/CN_PPI_YOY 最新一期的引用标签(期末口径) | CN_CPI_YOY@2026-10-31,CN_PPI_YOY@2026-10-31 | CN_CPI_YOY@2026-10-31,CN_PPI_YOY@2026-10-31 | 一致 |
| I31 | research_snapshot_20261123.json series_store | 剪刀差 2026-07 = PPI-CPI (pp) | 3.0 | 3.0 | 一致 |
| I32 | research_snapshot_20261123.json series_store | 剪刀差 2026-10 = PPI-CPI (pp) | 5.0 | 5.0 | 一致 |
| I33 | research_snapshot_20261123.json series_store | 美国 CPI 同比 3.72(2026-09) > 3.30(2026-07) | True | True | 一致 |
| I34 | research_snapshot_20261123.json series_store | 美国核心CPI同比 2.57(2026-09) > 2.47(2026-07) | True | True | 一致 |
| I35 | research_snapshot_20261123.json series_store | 美国核心PCE同比 3.12(2026-09) > 3.04(2026-06) | True | True | 一致 |
| I36 | research_snapshot_20261123.json series_store | 日本 2.44>1.97、东京 2.73>1.85、中国CPI 0.7>0.5、PPI 5.7>3.5 | True | True | 一致 |
| T01 | research_snapshot_20261123.json series_store | CORE_CPI 同比 2026-05 % | 2.8229 | 2.8229 | 一致 |
| T02 | research_snapshot_20261123.json series_store | CORE_CPI 同比 2026-08 % | 2.4462 | 2.4462 | 一致 |
| T03 | research_snapshot_20261123.json series_store | CORE_CPI 同比 2026-09 % | 2.5658 | 2.5658 | 一致 |
| T04 | research_snapshot_20261123.json series_store | 核心CPI同比 所引两位四位小数之差 2026-08 − 2026-05 (pp)(未舍入差 -0.376779, 四舍五入为 -0.3768) | -0.3767 | -0.3767 | 一致 |
| T04b | report.json research_plan.turning_candidates.candidates[CORE_CPI].delta | 引擎候选面 CORE_CPI delta(受审稿『三个月回落 0.3767 个百分点』) | -0.3767 | -0.3767 | 一致 |
| T05 | research_snapshot_20261123.json series_store | CPI 同比 2026-02 % | 2.434 | 2.434 | 一致 |
| T06 | research_snapshot_20261123.json series_store | CPI 同比 2026-05 % | 4.1666 | 4.1666 | 一致 |
| T07 | research_snapshot_20261123.json series_store | CN_CPI_YOY@2026-01 | 0.2 | 0.2 | 一致 |
| T08 | research_snapshot_20261123.json series_store | CN_CPI_YOY@2026-04 | 1.2 | 1.2 | 一致 |
| T09 | research_snapshot_20261123.json series_store | INDPRO 同比 2025-11 % | 1.7543 | 1.7543 | 一致 |
| T10 | research_snapshot_20261123.json series_store | INDPRO 同比 2026-02 % | 0.7972 | 0.7972 | 一致 |
| T11 | research_snapshot_20261123.json series_store | INDPRO 同比 2026-02 - 2025-11 (pp) | -0.9571 | -0.9571 | 一致 |
| T12 | research_snapshot_20261123.json series_store | CN_PMI_MFG@2026-02 | 49.0 | 49.0 | 一致 |
| T13 | research_snapshot_20261123.json series_store | CN_PMI_MFG@2026-05 | 50.0 | 50.0 | 一致 |
| T14 | research_snapshot_20261123.json series_store | CN_PMI_MFG 同比 2026-02 % | -2.3904 | -2.3904 | 一致 |
| T15 | research_snapshot_20261123.json series_store | CN_PMI_MFG 同比 2026-05 % | 1.0101 | 1.0101 | 一致 |
| T16 | report.json research_plan.turning_candidates.candidates | 候选池 9 项 | True | True | 一致 |
| T17 | report.json turning_candidates | 候选池 9 项的指标与窗口与正文所述一致 | True | True | 一致 |
| T20 | report.json turning_candidates | 除三项所取转折外, 其余 6 项窗口终点 ≤ 2026-05 | True | True | 一致 |
| V01 | report.json research_plan.point_values.cells | 按引擎所载发布规则独立重算: 35 个 status=ok 锚格的(观测日,值)=『发布日≤锚日的最后观测』且逐位一致 (35/35) | True | True | 一致 |
| V01b | report.json research_plan.point_values.cells | CN_POLICY_OVERNIGHT 三个月前锚: 发布日≤2026-08-23 的观测不存在(独立重算) | True | True | 一致 |
| V02 | agent_judgment.json reader_map.regions[*].anchor_echo | anchor_echo 35 项: 值与观测月=『发布日≤锚日的最后观测』(独立按发布规则重算), 逐位一致 | True | True | 一致 |
| V03 | report.json research_plan.point_values.cells | 点值格 18 格 + 缺席 4 格 | True | True | 一致 |
| V04 | report.json research_plan.point_values.cells | CORE_PCE 锚=2026-06(2026-07 发布晚于锚) | True | True | 一致 |
| V05 | report.json research_plan.point_values.cells | US_REAL_GDP 锚=2026-04(Q3 发布 2026-10-29 晚于锚) | True | True | 一致 |
| V06 | report.json research_plan.point_values.cells | JP_REAL_GDP_YOY 锚=2026-04 | True | True | 一致 |
| A01 | research_snapshot_20261123.json series_store | SPX@2026-10-23 | 7623.680176 | 7623.680176 | 一致 |
| A02 | research_snapshot_20261123.json series_store | SPX 引擎窗终点观测日 | 2026-11-23 | 2026-11-23 | 一致 |
| A03 | research_snapshot_20261123.json series_store | SPX 引擎窗(10-23→末观测) 变动% | -5.51 | -5.51 | 一致 |
| A04 | research_snapshot_20261123.json series_store | SPX 收盘窗(10-23→11-20) 变动% | -9.36 | -9.36 | 一致 |
| A05 | research_snapshot_20261123.json series_store | NIKKEI225@2026-10-23 | 62693.160000 | 62693.16 | 一致 |
| A06 | research_snapshot_20261123.json series_store | NIKKEI225 引擎窗终点观测日 | 2026-11-20 | 2026-11-20 | 一致 |
| A07 | research_snapshot_20261123.json series_store | NIKKEI225 引擎窗(10-23→末观测) 变动% | -9.98 | -9.98 | 一致 |
| A08 | research_snapshot_20261123.json series_store | NIKKEI225 收盘窗(10-23→11-20) 变动% | -9.98 | -9.98 | 一致 |
| A09 | research_snapshot_20261123.json series_store | SHCOMP@2026-10-23 | 3690.475300 | 3690.4753 | 一致 |
| A10 | research_snapshot_20261123.json series_store | SHCOMP 引擎窗终点观测日 | 2026-11-23 | 2026-11-23 | 一致 |
| A11 | research_snapshot_20261123.json series_store | SHCOMP 引擎窗(10-23→末观测) 变动% | -4.11 | -4.11 | 一致 |
| A12 | research_snapshot_20261123.json series_store | SHCOMP 收盘窗(10-23→11-20) 变动% | -4.25 | -4.25 | 一致 |
| A13 | research_snapshot_20261123.json series_store | DAX@2026-10-23 | 25181.650391 | 25181.650391 | 一致 |
| A14 | research_snapshot_20261123.json series_store | DAX 引擎窗终点观测日 | 2026-11-23 | 2026-11-23 | 一致 |
| A15 | research_snapshot_20261123.json series_store | DAX 引擎窗(10-23→末观测) 变动% | 0.11 | 0.11 | 一致 |
| A16 | research_snapshot_20261123.json series_store | DAX 收盘窗(10-23→11-20) 变动% | -1.50 | -1.5 | 一致 |
| A17 | research_snapshot_20261123.json series_store | VIX@2026-10-23 | 19.450001 | 19.450001 | 一致 |
| A18 | research_snapshot_20261123.json series_store | VIX 引擎窗终点观测日 | 2026-11-23 | 2026-11-23 | 一致 |
| A19 | research_snapshot_20261123.json series_store | VIX 引擎窗(10-23→末观测) 变动% | 38.87 | 38.87 | 一致 |
| A20 | research_snapshot_20261123.json series_store | VIX 收盘窗(10-23→11-20) 变动% | 84.52 | 84.52 | 一致 |
| A21 | research_snapshot_20261123.json series_store | NIKKEI225 序列末观测 | 2026-11-20 | 2026-11-20 | 一致 |
| A22 | research_snapshot_20261123.json series_store | NIKKEI225 在 2026-11-23 无观测 | True | True | 一致 |
| A23 | research_snapshot_20261123.json series_store | DAX@2026-11-23 | 25209.45 | 25209.45 | 一致 |
| A24 | research_snapshot_20261123.json series_store | VIX@2026-11-20 | 35.89 | 35.89 | 一致 |
| A25 | research_snapshot_20261123.json series_store | SPX 11-23 vs 11-20 % | 4.25 | 4.25 | 一致 |
| A26 | research_snapshot_20261123.json series_store | VIX 11-23 vs 11-20 % | -24.74 | -24.74 | 一致 |
| A27 | research_snapshot_20261123.json series_store | DAX 11-23 vs 11-20 % | 1.64 | 1.64 | 一致 |
| A28 | research_snapshot_20261123.json series_store | CAC40 收盘窗 % | 1.86 | 1.86 | 一致 |
| A29 | research_snapshot_20261123.json series_store | DXY 收盘窗 % | 1.96 | 1.96 | 一致 |
| A30 | research_snapshot_20261123.json series_store | DXY 引擎窗 % | 2.23 | 2.23 | 一致 |
| A31 | research_snapshot_20261123.json series_store | 引擎窗 NIKKEI225 与 SPX 跌幅落差绝对值(pp)(受审稿『两者跌幅相差四点四七个百分点』) | 4.47 | 4.47 | 一致 |
| A32 | research_snapshot_20261123.json series_store | 引擎窗 SPX 与 SHCOMP 落差(pp) | 1.40 | 1.4 | 一致 |
| A33 | research_snapshot_20261123.json series_store | 收盘窗 SPX 与 SHCOMP 落差(pp) | 5.11 | 5.11 | 一致 |
| A34 | research_snapshot_20261123.json series_store | USDJPY@2026-10-23 | 156.494 | 156.494 | 一致 |
| A35 | research_snapshot_20261123.json series_store | USDJPY@2026-11-23 | 159.347 | 159.347 | 一致 |
| A36 | research_snapshot_20261123.json series_store | USDJPY 引擎窗 % | 1.82 | 1.82 | 一致 |
| A37 | research_snapshot_20261123.json series_store | USDCNY@2026-10-23 | 6.6779 | 6.6779 | 一致 |
| A38 | research_snapshot_20261123.json series_store | USDCNY@2026-11-23 | 6.6542 | 6.6542 | 一致 |
| A39 | research_snapshot_20261123.json series_store | USDCNY 引擎窗 % | -0.35 | -0.35 | 一致 |
| A40 | research_snapshot_20261123.json series_store | 受审稿『同窗 USDJPY 156.494→159.347』两端值=引擎月窗 2026-10-23→2026-11-23 的观测(非 10-20→11-19 共同交易日窗; 该窗为 158.523→159.381, 见 out_s05_extra.txt) | True | True | 一致 |
| A44 | research_snapshot_20261123.json series_store | USDJPY 在三窗(10-20→11-19 / 10-23→11-23 / 10-23→11-20)均为美元对日元走强(方向稳健) | True | True | 一致 |
| A45 | research_snapshot_20261123.json series_store | USDCNY 在三窗均未走强(方向稳健) | True | True | 一致 |
| C01 | 直算(算术; 输入=已比对的两端值) | DFEDTARU 4.0 + 标准步长 0.25 | 4.25 | 4.25 | 一致 |
| C02 | 直算(算术; 输入=已比对的两端值) | JP_POLICY_RATE 1.227 + 0.05 后上取整到分位 | 1.28 | 1.28 | 一致 |
| C03 | 直算(算术; 输入=已比对的两端值) | CN_LPR_1Y 3.0 - 0.10 | 2.90 | 2.9 | 一致 |
| C04 | research_snapshot_20261123.json series_store | 截止日 DFEDTARU 4.0 未达 4.25 | True | True | 一致 |
| C05 | research_snapshot_20261123.json series_store | 截止日 JP_POLICY_RATE 1.227 < 1.28 | True | True | 一致 |
| C06 | research_snapshot_20261123.json series_store | 截止日 CN_LPR_1Y 3.0 > 2.90 | True | True | 一致 |
| C08 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 研究截止 2026-11-23 + 3 个日历月(年月进位后日取 23) | 2027-02-23 | 2027-02-23 | 一致 |
| N01 | report.json steps[S6_analog].envelope.data.candidates | scanned | 1871 | 1871 | 一致 |
| N02 | report.json steps[S6_analog].envelope.data.candidates | valid | 74 | 74 | 一致 |
| N03 | report.json steps[S6_analog].envelope.data.candidates | dropped_insufficient | 1785 | 1785 | 一致 |
| N04 | report.json steps[S6_analog].envelope.data.candidates | dropped_overlap | 12 | 12 | 一致 |
| N05 | report.json steps[S6_analog].envelope.data.candidates | valid+insufficient+overlap = scanned | 1871 | 1871 | 一致 |
| N06 | report.json steps[S6_analog].envelope.data.top[*].candidate_month | TOP-5 顺序 | 2025-03,2022-06,2023-10,2021-02,2020-01 | 2025-03,2022-06,2023-10,2021-02,2020-01 | 一致 |
| N07 | report.json steps[S6_analog].envelope.data.sort_basis | 排序依据=缺席特征数优先、其后距离 | True | True | 一致 |
| N08 | report.json steps[S6_analog].envelope.data.state_vector.growth.coverage | coverage growth | 0.17 | 0.17 | 一致 |
| N09 | report.json steps[S6_analog].envelope.data.state_vector.inflation.coverage | coverage inflation | 0.33 | 0.33 | 一致 |
| N10 | report.json steps[S6_analog].envelope.data.state_vector.rates.coverage | coverage rates | 0.75 | 0.75 | 一致 |
| N11 | report.json steps[S6_analog].envelope.data.state_vector.credit.coverage | coverage credit | 0.50 | 0.5 | 一致 |
| N12 | report.json steps[S6_analog].envelope.data.state_vector.volatility.coverage | coverage volatility | 1.00 | 1.0 | 一致 |
| N13 | report.json steps[S6_analog].envelope.data.state_vector.valuation.coverage | coverage valuation | 0.50 | 0.5 | 一致 |
| N14 | report.json steps[S6_analog].envelope.data.top[0].dims.volatility.contribution_share | 首位候选贡献份额 pct volatility | 42.13 | 42.13 | 一致 |
| N15 | report.json steps[S6_analog].envelope.data.top[0].dims.rates.contribution_share | 首位候选贡献份额 pct rates | 40.66 | 40.66 | 一致 |
| N16 | report.json steps[S6_analog].envelope.data.top[0].dims.inflation.contribution_share | 首位候选贡献份额 pct inflation | 10.54 | 10.54 | 一致 |
| N17 | report.json steps[S6_analog].envelope.data.top[0].dims.valuation.contribution_share | 首位候选贡献份额 pct valuation | 6.67 | 6.67 | 一致 |
| N18 | report.json steps[S6_analog].envelope.data.top[0].dims.credit.contribution_share | 首位候选贡献份额 pct credit | 0.00 | 0.0 | 一致 |
| N19 | report.json steps[S6_analog].envelope.data.top[0].dims.growth.contribution_share | 首位候选贡献份额 pct growth | 0.00 | 0.0 | 一致 |
| N20 | report.json steps[S6_analog].envelope.data.features_dropped_at_anchor | 锚点月缺席特征数 | 12 | 12 | 一致 |
| N21 | report.json steps[S6_analog].envelope.data.features_dropped_at_anchor | 缺席特征名单(排序) | CORE_CPI_yoy,CPI_yoy,FED_FUNDS_d12m,FED_FUNDS_level,GDP_yoy,HY_IG_gap_d12m,HY_OAS_d12m,INDPRO_yoy,NFP_3m_chg,RSAFS_yoy,SPX_PE_TTM_level,UNEMPLOYMENT_level | CORE_CPI_yoy,CPI_yoy,FED_FUNDS_d12m,FED_FUNDS_level,GDP_yoy,HY_IG_gap_d12m,HY_OAS_d12m,INDPRO_yoy,NFP_3m_chg,RSAFS_yoy,SPX_PE_TTM_level,UNEMPLOYMENT_level | 一致 |
| N22 | report.json steps[S6_analog].envelope.data.features_dropped_at_anchor | HY_IG_gap_d12m/HY_OAS_d12m 属历史长度不足 | True | True | 一致 |
| N23 | report.json steps[S6_analog].envelope.data.features_dropped_at_anchor | CORE_CPI_yoy/CPI_yoy/GDP_yoy/SPX_PE_TTM_level 属序列止于锚前两个月 | True | True | 一致 |
| N24 | report.json steps[S6_analog].envelope.data.features_dropped_at_anchor | FED_FUNDS_*/INDPRO_yoy/NFP_3m_chg/RSAFS_yoy/UNEMPLOYMENT_level 属锚点月无观测(止于锚前一月) | True | True | 一致 |
| N25 | report.json steps[S6_analog].envelope.data.top[0].aftermath | 事后表现四项 | SPX,UST_10Y,DXY,GOLD_F | SPX,UST_10Y,DXY,GOLD_F | 一致 |
| N26 | report.json steps[S6_analog].envelope.data.research_mode_gate | 描述性可用/事件研究被阻断 | True | True | 一致 |
| N27 | report.json steps[S6_analog].envelope.data.anchor_month | anchor_month | 2026-11 | 2026-11 | 一致 |
| N28 | report.json steps[S6_analog].envelope.data.feature_window_months | feature_window_months | 12 | 12 | 一致 |
| R01 | research_snapshot_20261123.json series_store | 名义=实际+盈亏平衡 @2026-11-19 残差(bp) | 0.0 | 0.0 | 一致 |
| R02 | research_snapshot_20261123.json series_store | UST_10Y@2026-10-20 在场 | yes | yes | 一致 |
| R03 | research_snapshot_20261123.json series_store | TIPS_10Y@2026-10-20 在场 | yes | yes | 一致 |
| R04 | research_snapshot_20261123.json series_store | BEI_10Y@2026-10-20 在场 | yes | yes | 一致 |
| R05 | research_snapshot_20261123.json series_store | 近一月窗 UST_10Y 变动(bp) | -8.0 | -8.0 | 一致 |
| R06 | research_snapshot_20261123.json series_store | 近一月窗 TIPS_10Y 变动(bp) | 11.0 | 11.0 | 一致 |
| R07 | research_snapshot_20261123.json series_store | 近一月窗 BEI_10Y 变动(bp) | -19.0 | -19.0 | 一致 |
| R08 | research_snapshot_20261123.json series_store | 近一月窗恒等残差(bp) | 0.0 | 0.0 | 一致 |
| R09 | research_snapshot_20261123.json series_store | 12月窗 UST_10Y 变动(bp) | 91.0 | 91.0 | 一致 |
| R10 | research_snapshot_20261123.json series_store | 12月窗 TIPS_10Y 变动(bp) | 102.0 | 102.0 | 一致 |
| R11 | research_snapshot_20261123.json series_store | 12月窗 BEI_10Y 变动(bp) | -11.0 | -11.0 | 一致 |
| R12 | research_snapshot_20261123.json series_store | 12月窗恒等残差(bp) | 0.0 | 0.0 | 一致 |
| R13 | research_snapshot_20261123.json series_store | BEI_10Y 序列末观测日 | 2026-11-20 | 2026-11-20 | 一致 |
| R14 | research_snapshot_20261123.json series_store | BEI_10Y@末观测 | 2.15 | 2.15 | 一致 |
| R15 | research_snapshot_20261123.json series_store | TIPS_10Y 序列末观测日 | 2026-11-19 | 2026-11-19 | 一致 |
| R16 | research_snapshot_20261123.json series_store | UST_10Y 序列末观测日 | 2026-11-19 | 2026-11-19 | 一致 |
| R17 | research_snapshot_20261123.json series_store | UST_10Y@2026-10-23 | 5.00 | 5.0 | 一致 |
| R18 | research_snapshot_20261123.json series_store | 近一月共同交易日窗内(10-20→11-19)DFEDTARU 无变动 | True | True | 一致 |
| R19 | research_snapshot_20261123.json series_store | 近一月窗实际利率为名义利率的唯一上行分量 | True | True | 一致 |
| R20 | research_snapshot_20261123.json series_store | 12月窗实际利率为主导分量(\|+102\|>\|−11\|) | True | True | 一致 |
| R21 | research_snapshot_20261123.json series_store | 近一月窗盈亏平衡降幅(19bp)大于实际上行幅度(11bp) | True | True | 一致 |
| R_BEI_10Y_1 | research_snapshot_20261123.json series_store | BEI_10Y@2026-11-19 | 2.16 | 2.16 | 一致 |
| R_TIPS_10Y_1 | research_snapshot_20261123.json series_store | TIPS_10Y@2026-11-19 | 2.88 | 2.88 | 一致 |
| R_UST_10Y_1 | research_snapshot_20261123.json series_store | UST_10Y@2026-11-19 | 5.04 | 5.04 | 一致 |
| D01 | agent_judgment.json 全文日期扫描 | 晚于研究截止日 2026-11-23 的日期(应仅为情景期限) | 2027-02-23,2027-02-28 | 2027-02-23,2027-02-28 | 一致 |
| D02 | research_snapshot_20261123.json series_store | 受审稿所用 34 条序列的末观测日均 ≤ 2026-11-23 | True | True | 一致 |
| D03 | research_snapshot_20261123.json research_as_of | research_as_of | 2026-11-23T22:58:11+08:00 | 2026-11-23T22:58:11+08:00 | 一致 |
| D04 | report.json research_plan.cutoff | cutoff | 2026-11-23 | 2026-11-23 | 一致 |
| D05_Berlin | research_snapshot_20261123.json research_as_of + IANA 时区换算 | 法兰克福 当地时刻 | 15:58:11 | 15:58:11 | 一致 |
| D05_New_York | research_snapshot_20261123.json research_as_of + IANA 时区换算 | 纽约 当地时刻 | 09:58:11 | 09:58:11 | 一致 |
| D05_Shanghai | research_snapshot_20261123.json research_as_of + IANA 时区换算 | 上海 当地时刻 | 22:58:11 | 22:58:11 | 一致 |
| D05_Tokyo | research_snapshot_20261123.json research_as_of + IANA 时区换算 | 东京 当地时刻 | 23:58:11 | 23:58:11 | 一致 |
| D06 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 研究截止 2026-11-23 - 3 个日历月(日取 23) | 2026-08-23 | 2026-08-23 | 一致 |
| D07 | report.json research_plan.point_values.cells | 三个月前锚 as_of 全部 = 2026-08-23 | True | True | 一致 |
| D08 | report.json research_plan.point_values.cells | 最新一期锚 as_of 全部 = 2026-11-23 | True | True | 一致 |
| D09 | report.json research_plan.point_anchors | 点锚定义: 3个月前=2026-08-23, 最新一期=2026-11-23 | True | True | 一致 |
| K04 | report.json contract_verification.verdicts[*](status=STALE) | STALE 项的指标 | CORE_PCE,US_REAL_GDP | CORE_PCE,US_REAL_GDP | 一致 |
| K05 | report.json contract_verification.verdicts[*] | STALE 两项数值直读一致(value==expected) | True | True | 一致 |
| K06 | report.json contract_verification | n_contradictions=4 | True | True | 一致 |
| K07 | agent_judgment.json l3.mechanism_chains | 机制链条数 | 2 | 2 | 一致 |
| K08 | agent_judgment.json l4.scenarios | 情景数 | 2 | 2 | 一致 |
| K09 | agent_judgment.json reader_map.transmission[*].links | 传导链条数/环数 | 1 | 1 | 一致 |
| K10 | agent_judgment.json reader_map.transmission[0].links | 传导环数 | 3 | 3 | 一致 |
| K11 | agent_judgment.json reader_map.transmission[0].links[*].face_off_verdict | 三环裁定均为『尚不能区分』 | True | True | 一致 |
| K12 | agent_judgment.json reader_map.transmission[0].links[*].distinguishing_metric | 区分指标 | TIPS_10Y,BEI_10Y,VIX | TIPS_10Y,BEI_10Y,VIX | 一致 |
| K13 | agent_judgment.json l3.contradictions[*].competing_explanations | 四条矛盾陈述各含 2 种并列解释且均带【假设】 | True | True | 一致 |
| K14 | agent_judgment.json reader_map.history_periods | 历史类比取零段 | True | True | 一致 |
| K15 | agent_judgment.json reader_map.turnings | 转折数 | 3 | 3 | 一致 |
| K16 | agent_judgment.json reader_map.turnings[*] | 三转折为不同指标-月且跨两维度(通胀×2+政策×1) | True | True | 一致 |
| K17 | agent_judgment.json l4.scenarios[*] | 两情景互斥(A 需 DFEDTARU≥4.25, B 需 ≤4) | True | True | 一致 |
| Q01 | research_snapshot_20261123.json gate_a.status | status | DEGRADED | DEGRADED | 一致 |
| Q02 | research_snapshot_20261123.json gate_a.core_missing | core_missing 项数 | 0 | 0 | 一致 |
| Q03 | research_snapshot_20261123.json gate_a.noncore_missing | 非核心缺口 10 项(排序) | BUND_10Y,BUND_2Y,CN_OMO_7D,CN_POLICY_OVERNIGHT,EA_HICP_YOY,EA_REAL_GDP_YOY,ECB_DFR,ECB_MRO,JP_CPI_TOKYO_YOY,JP_REAL_GDP_YOY | BUND_10Y,BUND_2Y,CN_OMO_7D,CN_POLICY_OVERNIGHT,EA_HICP_YOY,EA_REAL_GDP_YOY,ECB_DFR,ECB_MRO,JP_CPI_TOKYO_YOY,JP_REAL_GDP_YOY | 一致 |
| Q04 | research_snapshot_20261123.json gate_a.noncore_degraded | 非核心降级 6 项(排序) | CN_SF_FLOW,JTSJOL,M2SL,SPX_EPS,SPX_PE_TTM,US_REAL_GDP | CN_SF_FLOW,JTSJOL,M2SL,SPX_EPS,SPX_PE_TTM,US_REAL_GDP | 一致 |
| Q07 | research_snapshot_20261123.json quality.counts | PASS 计数 | 72 | 72 | 一致 |
| Q08 | research_snapshot_20261123.json quality.counts | DEGRADED 计数 | 7 | 7 | 一致 |
| Q09 | research_snapshot_20261123.json quality.counts | FAIL 计数 | 0 | 0 | 一致 |
| Q10 | research_snapshot_20261123.json quality.missing_core | missing_core 项数 | 0 | 0 | 一致 |
| Q11 | report.json evidence_index | 证据索引行数 | 69 | 69 | 一致 |
| Q12 | research_snapshot_20261123.json gate_a.noncore_missing | 被列入缺口的 CN_OMO_7D/CN_POLICY_OVERNIGHT/JP_CPI_TOKYO_YOY/JP_REAL_GDP_YOY 在 series_store 有存量观测 | True | True | 一致 |
| Q13 | research_snapshot_20261123.json gate_a.noncore_missing | 六项欧元区序列在 series_store 缺席且 sources_status.ea 含 MISSING | True | True | 一致 |
| Q14 | report.json evidence_index[*].metric_id | 受审稿称『不在本轮证据索引』: JP_CPI_TOKYO_YOY | True | True | 一致 |
| Q15 | report.json evidence_index[*].metric_id | 受审稿称『不在本轮证据索引』: JP_REAL_GDP_YOY | True | True | 一致 |
| Q16 | report.json evidence_index[*].metric_id | 受审稿称『不在本轮证据索引』: CN_OMO_7D | True | True | 一致 |
| Q17 | report.json evidence_index[*].metric_id | 受审稿称『不在本轮证据索引』: CN_POLICY_OVERNIGHT | True | True | 一致 |
| Q18 | report.json evidence_index[*].metric_id | 受审稿称『不在本轮证据索引』: WTI_SPOT_M | True | True | 一致 |
| Q19 | report.json evidence_index × agent_judgment evidence_refs | L3/L4 全部 evidence_refs 的指标均在证据索引内 (n_refs=46) | True | True | 一致 |
| U01 | report.json research_plan.point_values.cells | US_REAL_GDP[anc].publication_date(=2026-07-29; 规则季末+29天自 period_end 2026-06-30 重算=2026-07-29) | 2026-07-29 | 2026-07-29 | 一致 |
| U02 | report.json research_plan.point_values.cells | US_REAL_GDP[lat].publication_date(=2026-10-29; 规则季末+29天自 period_end 2026-09-30 重算=2026-10-29) | 2026-10-29 | 2026-10-29 | 一致 |
| U03 | report.json research_plan.point_values.cells | UNEMPLOYMENT[anc].publication_date(=2026-08-05; 规则月末+5天自 period_end 2026-07-31 重算=2026-08-05) | 2026-08-05 | 2026-08-05 | 一致 |
| U04 | report.json research_plan.point_values.cells | UNEMPLOYMENT[lat].publication_date(=2026-11-05; 规则月末+5天自 period_end 2026-10-31 重算=2026-11-05) | 2026-11-05 | 2026-11-05 | 一致 |
| U05 | report.json research_plan.point_values.cells | INDPRO[anc].publication_date(=2026-08-15; 规则月末+15天自 period_end 2026-07-31 重算=2026-08-15) | 2026-08-15 | 2026-08-15 | 一致 |
| U06 | report.json research_plan.point_values.cells | INDPRO[lat].publication_date(=2026-11-15; 规则月末+15天自 period_end 2026-10-31 重算=2026-11-15) | 2026-11-15 | 2026-11-15 | 一致 |
| U07 | report.json research_plan.point_values.cells | CPI[anc].publication_date(=2026-08-13; 规则月末+13天自 period_end 2026-07-31 重算=2026-08-13) | 2026-08-13 | 2026-08-13 | 一致 |
| U08 | report.json research_plan.point_values.cells | CPI[lat].publication_date(=2026-11-13; 规则月末+13天自 period_end 2026-10-31 重算=2026-11-13) | 2026-11-13 | 2026-11-13 | 一致 |
| U09 | report.json research_plan.point_values.cells | CORE_CPI[anc].publication_date(=2026-08-13; 规则月末+13天自 period_end 2026-07-31 重算=2026-08-13) | 2026-08-13 | 2026-08-13 | 一致 |
| U10 | report.json research_plan.point_values.cells | CORE_CPI[lat].publication_date(=2026-11-13; 规则月末+13天自 period_end 2026-10-31 重算=2026-11-13) | 2026-11-13 | 2026-11-13 | 一致 |
| U11 | report.json research_plan.point_values.cells | CORE_PCE[anc].publication_date(=2026-07-30; 规则月末+30天自 period_end 2026-06-30 重算=2026-07-30) | 2026-07-30 | 2026-07-30 | 一致 |
| U12 | report.json research_plan.point_values.cells | CORE_PCE[lat].publication_date(=2026-10-30; 规则月末+30天自 period_end 2026-09-30 重算=2026-10-30) | 2026-10-30 | 2026-10-30 | 一致 |
| U13 | report.json research_plan.point_values.cells | DFF[anc].publication_date(=2026-08-23; 规则观测日+1天自 period_end 2026-08-22 重算=2026-08-23) | 2026-08-23 | 2026-08-23 | 一致 |
| U14 | report.json research_plan.point_values.cells | DFF[lat].publication_date(=2026-11-20; 规则观测日+1天自 period_end 2026-11-19 重算=2026-11-20) | 2026-11-20 | 2026-11-20 | 一致 |
| U15 | report.json research_plan.point_values.cells | CN_PMI_MFG[anc].publication_date(=2026-07-30; 规则月末-1天自 period_end 2026-07-31 重算=2026-07-30) | 2026-07-30 | 2026-07-30 | 一致 |
| U16 | report.json research_plan.point_values.cells | CN_PMI_MFG[lat].publication_date(=2026-10-30; 规则月末-1天自 period_end 2026-10-31 重算=2026-10-30) | 2026-10-30 | 2026-10-30 | 一致 |
| U17 | report.json research_plan.point_values.cells | CN_CPI_YOY[anc].publication_date(=2026-08-09; 规则月末+9天自 period_end 2026-07-31 重算=2026-08-09) | 2026-08-09 | 2026-08-09 | 一致 |
| U18 | report.json research_plan.point_values.cells | CN_CPI_YOY[lat].publication_date(=2026-11-09; 规则月末+9天自 period_end 2026-10-31 重算=2026-11-09) | 2026-11-09 | 2026-11-09 | 一致 |
| U19 | report.json research_plan.point_values.cells | CN_PPI_YOY[anc].publication_date(=2026-08-09; 规则月末+9天自 period_end 2026-07-31 重算=2026-08-09) | 2026-08-09 | 2026-08-09 | 一致 |
| U20 | report.json research_plan.point_values.cells | CN_PPI_YOY[lat].publication_date(=2026-11-09; 规则月末+9天自 period_end 2026-10-31 重算=2026-11-09) | 2026-11-09 | 2026-11-09 | 一致 |
| U21 | report.json research_plan.point_values.cells | JP_REAL_GDP_YOY[anc].publication_date(=2026-08-14; 规则季末+45天自 period_end 2026-06-30 重算=2026-08-14) | 2026-08-14 | 2026-08-14 | 一致 |
| U22 | report.json research_plan.point_values.cells | JP_REAL_GDP_YOY[lat].publication_date(=2026-11-14; 规则季末+45天自 period_end 2026-09-30 重算=2026-11-14) | 2026-11-14 | 2026-11-14 | 一致 |
| U23 | report.json research_plan.point_values.cells | JP_CPI_YOY[anc].publication_date(=2026-08-20; 规则月末+20天自 period_end 2026-07-31 重算=2026-08-20) | 2026-08-20 | 2026-08-20 | 一致 |
| U24 | report.json research_plan.point_values.cells | JP_CPI_YOY[lat].publication_date(=2026-11-20; 规则月末+20天自 period_end 2026-10-31 重算=2026-11-20) | 2026-11-20 | 2026-11-20 | 一致 |
| U25 | report.json research_plan.point_values.cells | JP_CPI_TOKYO_YOY[anc].publication_date(=2026-07-30; 规则月末-1天自 period_end 2026-07-31 重算=2026-07-30) | 2026-07-30 | 2026-07-30 | 一致 |
| U26 | report.json research_plan.point_values.cells | JP_CPI_TOKYO_YOY[lat].publication_date(=2026-10-30; 规则月末-1天自 period_end 2026-10-31 重算=2026-10-30) | 2026-10-30 | 2026-10-30 | 一致 |
| U27 | report.json research_plan.point_values.cells | JP_POLICY_RATE[anc].publication_date(=2026-08-05; 规则月末+5天自 period_end 2026-07-31 重算=2026-08-05) | 2026-08-05 | 2026-08-05 | 一致 |
| U28 | report.json research_plan.point_values.cells | JP_POLICY_RATE[lat].publication_date(=2026-11-05; 规则月末+5天自 period_end 2026-10-31 重算=2026-11-05) | 2026-11-05 | 2026-11-05 | 一致 |
| U29 | report.json research_plan.point_values.cells | 所引发布日(锚格)全部 ≤ 2026-08-23 | True | True | 一致 |
| U30 | report.json research_plan.point_values.cells | 所引发布日(最新一期)全部 ≤ 2026-11-23 | True | True | 一致 |
| U31 | report.json research_plan.point_values.cells | 锚格观测日全部 ≤ 2026-08-23 | True | True | 一致 |
| U32 | report.json research_plan.point_values.cells | 最新一格观测日全部 ≤ 2026-11-23 | True | True | 一致 |
| U33 | report.json research_plan.point_values.cells | 受审稿所称『引擎推定规则、非日历实录』: 除 CN_LPR_1Y 最新一期外, 所引发布日的 publication_basis 不含 calendar: | True | True | 一致 |
| U34 | report.json research_plan.point_values.cells | 东京都CPI/美国GDP 发布口径含『官方实测锚』 | True | True | 一致 |
| U35 | report.json research_plan.point_values.cells | DFEDTARU 发布口径=决议日当日公布、观测日=序列打印日(2026-08-23 / 2026-11-23) | True | True | 一致 |
| X04 | scripts/research_contract/text_consistency.py ALIASES | 文本一致性别名表未收录 JP_CPI_*、JP_REAL_GDP_YOY、EA_* (受审稿引擎缺口披露①) | True | True | 一致 |
| X05 | scripts/research_contract/text_consistency.py ALIASES | 别名表含美国『CPI』『GDP』别名(JP_CPI_*/JP_REAL_GDP_YOY 子串会被绑定到美国同名序列) | True | True | 一致 |
| X06 | MAP_REPORT.md / FULL_REPORT.md / report.md | verdict_note 字段出现次数(受审稿引擎缺口披露⑤: 不进渲染) | 0,0,0 | 0,0,0 | 一致 |
| X07 | MAP_REPORT.md | 读者所见裁定为 face_off_verdict 标签(『尚不能区分』渲染 ≥3 处) | True | True | 一致 |
| X08 | report.json steps[S7_mode_gate].envelope.gate | 类比研究模式门: 描述性可用、事件研究被阻断(受审稿历史零段注记) | True | True | 一致 |
| X09 | report.json steps[S6_analog].envelope.data.sort_basis | 类比排序依据=缺席特征数优先、其后距离, 名次非纯距离序 | True | True | 一致 |
| X10 | report.json research_plan.as_of_declared.bare_year_month | 问句含显式日历月(受审稿引擎缺口披露④) | 2026年11月 | 2026年11月 | 一致 |
| X11 | report.json notes[0] | 计划注记『地图计划指标缺数』所列指标数(受审稿: 十九) | 19 | 19 | 一致 |
| X12 | report.json notes[0] × research_plan.point_values.cells | 其中在点值格有值的指标数(受审稿: 十五) | 15 | 15 | 一致 |
| X13 | release_calendar.json version | 冻结发布日历版本(受审稿: v1.5.0) | 1.5.0 | 1.5.0 | 一致 |
| X14 | report.json research_plan.regions×point_values.cells × scripts/agent_judgment.py BLOCKING_BLOCKED_CLASSES | 交付门: 地区×维度组零 ok 格(map_core_dimension_missing 属阻断类)——受审稿『引擎交付门以核心维度缺数判为不可交付』 | True | True | 一致 |
| X15 | scripts/research_map_planner.py 并项补选口径 × MAP_REPORT.md | 引擎并项规则=同维度且观测窗重叠的转折计同一轮; 补选行标注『引擎补选』(受审稿转折取舍注记) | True | True | 一致 |
| X18 | research_snapshot_20261123.json series_store.VIX@2026-11-23 | VIX 引擎窗末值(受审稿『VIX +38.87%(19.45→27.01)』) | 27.01 | 27.01 | 一致 |
| X20 | metric_registry.json / report.json research_plan (含『换锚』字样的引擎注记) | 隔夜利率注记含 2026-11-02 换锚后的操作目标锚(受审稿转述) | True | True | 一致 |
| X19 | report.json research_plan.point_values.cells[CN_OMO_7D].anchors[最新一期].freshness* | 七天逆回购最新一格: freshness=stale、freshness_lag_days=24、freshness_window_days=10(受审稿『引擎注记为过期: 末观测滞后二十四天、超出十天发布频率窗口』) | True | True | 一致 |
| X25 | research_snapshot_20261123.json series_store.CORE_CPI 2026-08 观测 | CORE_CPI 2026-08 观测日(受审稿『窗口终点 2026-08-01 略早于三个月前锚』) | 2026-08-01 | 2026-08-01 | 一致 |
| X26 | research_snapshot_20261123.json series_store.CORE_PCE 末观测 | CORE_PCE 最新水平观测日(受审稿『观测 2026-09-01』/证据索引引用 CORE_PCE@2026-09-01) | 2026-09-01 | 2026-09-01 | 一致 |
| X27 | report.json research_plan.us_rates_trio.window.from | 共同交易日三利率窗起(受审稿『近一月共同交易日窗(2026-10-20→2026-11-19)』) | 2026-10-20 | 2026-10-20 | 一致 |
| X28 | report.json research_plan.us_rates_trio.window_12m.from | 12 个月窗起(受审稿『12 个月窗(2025-11-19→2026-11-19)』) | 2025-11-19 | 2025-11-19 | 一致 |
| X29 | report.json research_plan.asset_moves.window_rule | 资产月窗规则含 2026-10-23 与 2026-11-23(受审稿『引擎近一月窗(2026-10-23→2026-11-23)』) | True | True | 一致 |
| X30 | report.json research_plan.policy_doc_facts[0].published_on | FOMC 2026年10月会议纪要发布日(受审稿『2026-11-18 发布』) | 2026-11-18 | 2026-11-18 | 一致 |
| X31 | report.json run.ts_utc | 运行标识(受审稿『降级面开放问句 20261123T235101Z』) | 20261123T235101Z | 20261123T235101Z | 一致 |
| X32 | report.json run.evidence_gate.source_snapshot_id | 证据门源快照(受审稿『全部取自本工单冻结快照 research_snapshot_20261123』) | research_snapshot_20261123 | research_snapshot_20261123 | 一致 |
| X34 | research_snapshot_20261123.json series_store.VIX@2026-10-23 | VIX 引擎窗起值两位小数(受审稿『19.45→27.01』『19.45→35.89』) | 19.45 | 19.45 | 一致 |
| X35 | release_calendar.json entries[RC-JP-BOJ-TARGET-2026-09].decision* | 日本央行 2026-09 决议日(受审稿『2026-09-18 决议』) | 2026-09-18 | 2026-09-18 | 一致 |
| X36 | release_calendar.json entries[RC-JP-BOJ-TARGET-2026-09].effective* | 日本央行 2026-09 生效日(受审稿『2026-09-24 生效』) | 2026-09-24 | 2026-09-24 | 一致 |
| X37 | MAP_REPORT.md『政策一年窗路径』面板 × snapshot.series_store.JP_POLICY_RATE | 引擎『政策一年窗路径』面板载有日本无担保隔夜拆借利率窗路径(受审稿称 +75bp 与该面板同口径); 独立复算 2025-11 月均 0.478→2026-10 月均 1.227 = +74.9bp | True | True | 一致 |
| X38 | metric_registry.json metrics[JP_REAL_GDP_YOY].frequency | 日本实际 GDP 同比为季频(受审稿『JP_REAL_GDP_YOY 仅季频』) | True | True | 一致 |
| X39 | AGENT_SEAT_ENVELOPE.json reader_map_contract | 契约对历史类比段数设 0..3 上限(受审稿『契约允许 0..3 段』) | True | True | 一致 |
| X40 | report.json agent_judgment.schema_version | 研判档 schema 版本(受审稿 schema_version 1.1) | 1.1 | 1.1 | 一致 |
| X21 | report.json research_plan.point_values.cells[CN_CPI_YOY].anchors[3个月前].observation_date × snapshot.series_store.CN_CPI_YOY(按引擎发布规则月末+9天独立重算) | CN_CPI_YOY 三个月前锚观测日(受审稿『观测 2026-07-01』; 按『发布日≤锚日』重算; 若仅按观测日≤锚日会误取 2026-08-01, 即 2026-08-01) | 2026-07-01 | 2026-07-01 | 一致 |
| X22 | report.json research_plan.point_values.cells[CN_PPI_YOY].anchors[3个月前].observation_date × snapshot.series_store.CN_PPI_YOY(按引擎发布规则月末+9天独立重算) | CN_PPI_YOY 三个月前锚观测日(受审稿『观测 2026-07-01』; 按『发布日≤锚日』重算; 若仅按观测日≤锚日会误取 2026-08-01, 即 2026-08-01) | 2026-07-01 | 2026-07-01 | 一致 |
| X23 | report.json research_plan.point_values.cells[UNEMPLOYMENT].anchors[3个月前].observation_date × snapshot.series_store.UNEMPLOYMENT(按引擎发布规则月末+5天独立重算) | UNEMPLOYMENT 三个月前锚观测日(受审稿『观测 2026-07-01』; 按『发布日≤锚日』重算; 若仅按观测日≤锚日会误取 2026-08-01, 即 2026-08-01) | 2026-07-01 | 2026-07-01 | 一致 |
| X24 | report.json research_plan.point_values.cells[CN_PMI_MFG].anchors[3个月前].observation_date × snapshot.series_store.CN_PMI_MFG(按引擎发布规则月末-1天独立重算) | CN_PMI_MFG 三个月前锚观测日(受审稿『观测 2026-07-01』; 按『发布日≤锚日』重算; 若仅按观测日≤锚日会误取 2026-08-01, 即 2026-08-01) | 2026-07-01 | 2026-07-01 | 一致 |
| X33 | report.json evidence_index[*].kind × steps[S3_*].envelope.snapshot_id | 证据索引 69 行 = snapshot_fact 44 行 + s3_envelope 25 行, 且 S3 步信封源快照 = research_snapshot_20261123(与受审稿『全部取自本工单冻结快照』相容) | True | True | 一致 |
| X41 | research_snapshot_20261123.json gate_a.noncore_missing_detail | 缺口明细四组归类与受审稿数据面注记逐指标一致(ea:MISSING×6 / 注册表未登记×2 / 档内无记录×1 / FRED_JP_GDP×1) | True | True | 一致 |
| X43 | report.json research_plan.point_values.cells[CN_CPI_YOY].anchors[3个月前].observation_date | CN_CPI_YOY 点值格三个月前锚观测日(引擎面直读) | 2026-07-01 | 2026-07-01 | 一致 |
| X44 | report.json research_plan.point_values.cells[CN_PPI_YOY].anchors[3个月前].observation_date | CN_PPI_YOY 点值格三个月前锚观测日(引擎面直读) | 2026-07-01 | 2026-07-01 | 一致 |
| X45 | report.json research_plan.point_values.cells[UNEMPLOYMENT].anchors[3个月前].observation_date | UNEMPLOYMENT 点值格三个月前锚观测日(引擎面直读) | 2026-07-01 | 2026-07-01 | 一致 |
| X46 | report.json research_plan.point_values.cells[CN_PMI_MFG].anchors[3个月前].observation_date | CN_PMI_MFG 点值格三个月前锚观测日(引擎面直读) | 2026-07-01 | 2026-07-01 | 一致 |
| X47 | report.json | research_plan.point_values.cells 数量(与信封 reader_map_contract.engine_faces.point_values_cells 同值); 受审稿 agent_declaration.basis: 点值格(18格 | 18 | 18 | 一致 |
| X48 | report.json | research_plan.point_values.absent 数量(与信封 point_values_absent 同值: EA_REAL_GDP_YOY/EA_HICP_YOY/ECB_MRO/ECB_DFR); 受审稿: 另4格序列缺席 | 4 | 4 | 一致 |
| X49 | snapshot.series_store | JP_POLICY_RATE 2025-12 月均→2026-10 月均 变动(bp); 受审稿 quality_gate_notes[6]: 仅自窗内首观测(2025-12 月均 0.557)起算为 +67bp | 67.0 | 67 | 一致 |
| X50 | report.json | S6_analog.features_dropped_at_anchor 的 HY_IG_gap_d12m/HY_OAS_d12m 均含『hist_25<36点(=36个月史…)』且 normalization.min_history_months=36; 受审稿 history_zero_case_note: 历史长度不足 36 个月——HY_IG_gap_d12m、HY_OAS_d12m | True | True | 一致 |

## 辅助核对点

| 编号 | 出处(只读面: 文件 · 面/键) | 复算项(序列ID@观测日/月 或 字段) | 直算值 | 受审稿值 | 判定 |
|---|---|---|---|---|---|
| P41 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2026-09-16 星期 | Wednesday | Wednesday | 辅助(不计入) |
| P42 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2026-09-18 星期 | Friday | Friday | 辅助(不计入) |
| I09 | research_snapshot_20261123.json series_store | JP_CPI_TOKYO_YOY 序列首观测 | 2026-01 | 2026-01 | 辅助(不计入) |
| T18 | research_snapshot_20261123.json series_store | CN_PPI_YOY@2026-02 / @2026-05 (与引擎候选面 value_before/value_after) | 0.0 | 0.0 | 辅助(不计入) |
| T19 | research_snapshot_20261123.json series_store | JP_CPI_YOY@2026-02 | 1.27 | 1.27 | 辅助(不计入) |
| A41 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2026-11-20 星期 | Friday | Friday | 辅助(不计入) |
| A42 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2026-11-23 星期 | Monday | Monday | 辅助(不计入) |
| A43 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2026-08-23 星期 | Sunday | Sunday | 辅助(不计入) |
| C07 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2027-02-28 合法日期/星期 | Sunday | Sunday | 辅助(不计入) |
| C09 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 2026-11-23→2027-02-28 天数 | 97 | 97 | 辅助(不计入) |
| K01 | report.json agent_judgment.contract_verification.stats | checks | 17 | 17 | 辅助(不计入) |
| K02 | report.json agent_judgment.contract_verification.stats | verified | 15 | 15 | 辅助(不计入) |
| K03 | report.json agent_judgment.contract_verification.stats | contradicted | 0 | 0 | 辅助(不计入) |
| Q05 | research_snapshot_20261123.json gate_a.core_fail | core_fail 项数 | 0 | 0 | 辅助(不计入) |
| Q06 | research_snapshot_20261123.json gate_a.noncore_fail | noncore_fail 项数 | 0 | 0 | 辅助(不计入) |
| U_wd_2026-11-05 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 推定发布日 2026-11-05 星期 | Thursday | Thursday | 辅助(不计入) |
| U_wd_2026-11-09 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 推定发布日 2026-11-09 星期 | Monday | Monday | 辅助(不计入) |
| U_wd_2026-11-13 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 推定发布日 2026-11-13 星期 | Friday | Friday | 辅助(不计入) |
| U_wd_2026-11-14 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 推定发布日 2026-11-14 星期 | Saturday | Saturday | 辅助(不计入) |
| U_wd_2026-11-15 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 推定发布日 2026-11-15 星期 | Sunday | Sunday | 辅助(不计入) |
| U_wd_2026-11-20 | 直算(日历算术; 输入=受审稿所载日期与 report.json research_plan.cutoff / research_as_of) | 推定发布日 2026-11-20 星期 | Friday | Friday | 辅助(不计入) |
| X01 | MAP_REPORT.md(引擎渲染面)『TIPS_10Y 引擎当前面: 近30日 2.66→2.88, 上升22bp』× snapshot.series_store.TIPS_10Y | 渲染面『近30日』窗 2026-10-23→2026-11-19 实际利率变动(bp) | 22.0 | 22.0 | 辅助(不计入) |
| X02 | research_snapshot_20261123.json series_store.TIPS_10Y@2026-10-23 | 渲染面所引窗起值 2.66 | 2.66 | 2.66 | 辅助(不计入) |
| X03 | MAP_REPORT.md | 渲染面确含『近30日2.66→2.88,上升22bp』字样 | True | True | 辅助(不计入) |
| X16 | report.json run_ok / steps[*].ok / steps[S8_grounded_qa].envelope | run_ok=true 且 66 步 step 级 ok 全为 true(62 已执行+4 未执行); S8_grounded_qa 信封含 unmapped(地图问句不属其支持的问题类型, 非失败步骤) | True | True | 辅助(不计入) |
| X17 | research_snapshot_20261123.json series_store.UST_10Y/TIPS_10Y/BEI_10Y | 10-23→11-19 窗三利率恒等残差=0(+4 = +22 − 18) | True | True | 辅助(不计入) |
| X51 | AGENT_SEAT_ENVELOPE.json | frozen_inputs 三项 sha256 前16位与实测文件一致(完整性前提; 受审稿无对应文字) | True | True | 辅助(不计入) |
