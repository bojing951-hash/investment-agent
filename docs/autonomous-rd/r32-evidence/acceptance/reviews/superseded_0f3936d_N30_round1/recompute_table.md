# 复算清单(Audit-R32 N30 Round-1 独立语义审查席;只读直算后比对)

列: # | 类别 | 出处键(只读面) | 直算值 | 报告/判断档值 | 一致 | 位置 | 备注

| 1 | ①截止日 | snapshot.research_as_of | "2026-11-23" | "2026-11-23" | 一致 | agent_declaration.basis |  |
| 2 | ①截止日 | snapshot.target_date | "20261123" | "20261123" | 一致 | MAP_REPORT 头部 |  |
| 3 | ①截止日 | report.json research_plan.cutoff | "2026-11-23" | "2026-11-23" | 一致 | MAP_REPORT 头部 |  |
| 4 | ①截止日 | report.json run.evidence_asof | "2026-11-23" | "2026-11-23" | 一致 | agent_declaration.basis |  |
| 5 | ①截止日 | series_store[*].dates[-1] (17 cited series) | "2026-11-23" | "≤2026-11-23" | 一致 | 全档 | latest per series: EA_HICP_YOY=2026-10-01, JP_CPI_YOY=2026-10-01, JP_CPI_TOKYO_YOY=2026-10-01, JP_POLICY_RATE=2026-10-01, ECB_DFR=2026-09-16, ECB_MRO=2026-09-16, SPX=2026-11-23, NIKKEI225=2026-11-20, DAX=2026-11-23, CAC40=2026-11-23, VIX=2026-11-23, EURUSD=2026-11-23, USDJPY=2026-11-23, DXY=2026-11-23, UST_10Y=2026-11-19, TIPS_10Y=2026-11-19, BEI_10Y=2026-11-20 |
| 6 | ①截止日 | series_store obs + registry/engine 推定规则(月末+16/+20/−1/+5) | "2026-11-20" | "≤2026-11-23" | 一致 | C1/C2 公布日 | max presumed pub among obs 2025-10..latest of the four monthly series |
| 7 | ①截止日 | 冻结日历条目 + 序列变更日(决议/生效/维持) | "2026-10-30" | "≤2026-11-23" | 一致 | C2/M1 |  |
| 8 | ①截止日 | agent_judgment.json 全文正则 YYYY-MM-DD > 截止日 | [["2026-11-24", ".agent_declaration.written_at"], ["2026-11-30", ".agent_declaration.basis"], ["2026-11-30", ".quality_gate_notes[4]"], ["2026-11-30", ".reader_map.headline_conclusion"], ["2027-02-15", ".l4.scenarios"], ["2027-02-15", ".quality_gate_notes[3]"]] | "仅 written_at 时间戳 / 请求月末(披露未到) / 情景期限" | 一致 | l4.scenarios 触发期限 / agent_declaration | 2026-11-24=agent_declaration.written_at(成稿时间戳); 2026-11-30=请求月末(披露未到、已取实际覆盖日); 2027-02-15=情景期限 |
| 9 | ①截止日 | agent_judgment.json 全文正则 YYYY-MM > 2026-11 | ["2026-12", "2027-01"] | ["2026-12", "2027-01"] | 一致 | l4.scenarios | 2026-12=情景观测月(未发布,非已知值); 2027-01=入档月 |
| 10 | ②锚格 | series_store[EA_HICP_YOY] latest obs with (presumed) pub ≤ 2026-05-23 | "2026-04-01=3.0" | "2026-04-01=3.0" | 一致 | reader_map.regions/anchor_echo | engine cell={"value": 3.0, "observation_date": "2026-04-01", "publication_date": "2026-05-16"} |
| 11 | ②锚格 | series_store[EA_HICP_YOY] latest obs with (presumed) pub ≤ 2026-11-23 | "2026-10-01=4.0" | "2026-10-01=4.0" | 一致 | reader_map.regions/anchor_echo | engine cell={"value": 4.0, "observation_date": "2026-10-01", "publication_date": "2026-11-16"} |
| 12 | ②锚格 | series_store[ECB_MRO] latest obs with (presumed) pub ≤ 2026-05-23 | "2025-06-11=2.15" | "2025-06-11=2.15" | 一致 | reader_map.regions/anchor_echo | engine cell={"value": 2.15, "observation_date": "2025-06-11", "publication_date": "2025-06-11"} |
| 13 | ②锚格 | series_store[ECB_MRO] latest obs with (presumed) pub ≤ 2026-11-23 | "2026-09-16=2.65" | "2026-09-16=2.65" | 一致 | reader_map.regions/anchor_echo | engine cell={"value": 2.65, "observation_date": "2026-09-16", "publication_date": "2026-09-16"} |
| 14 | ②锚格 | series_store[ECB_DFR] latest obs with (presumed) pub ≤ 2026-05-23 | "2025-06-11=2.0" | "2025-06-11=2.0" | 一致 | reader_map.regions/anchor_echo | engine cell={"value": 2.0, "observation_date": "2025-06-11", "publication_date": "2025-06-11"} |
| 15 | ②锚格 | series_store[ECB_DFR] latest obs with (presumed) pub ≤ 2026-11-23 | "2026-09-16=2.5" | "2026-09-16=2.5" | 一致 | reader_map.regions/anchor_echo | engine cell={"value": 2.5, "observation_date": "2026-09-16", "publication_date": "2026-09-16"} |
| 16 | ②锚格 | series_store[JP_CPI_YOY] latest obs with (presumed) pub ≤ 2026-05-23 | "2026-04-01=1.38" | "2026-04-01=1.38" | 一致 | reader_map.regions/anchor_echo | engine cell={"value": 1.38, "observation_date": "2026-04-01", "publication_date": "2026-05-20"} |
| 17 | ②锚格 | series_store[JP_CPI_YOY] latest obs with (presumed) pub ≤ 2026-11-23 | "2026-10-01=2.44" | "2026-10-01=2.44" | 一致 | reader_map.regions/anchor_echo | engine cell={"value": 2.44, "observation_date": "2026-10-01", "publication_date": "2026-11-20"} |
| 18 | ②锚格 | series_store[JP_CPI_TOKYO_YOY] latest obs with (presumed) pub ≤ 2026-05-23 | "2026-04-01=1.42" | "2026-04-01=1.42" | 一致 | reader_map.regions/anchor_echo | engine cell={"value": 1.42, "observation_date": "2026-04-01", "publication_date": "2026-04-29"} |
| 19 | ②锚格 | series_store[JP_CPI_TOKYO_YOY] latest obs with (presumed) pub ≤ 2026-11-23 | "2026-10-01=2.73" | "2026-10-01=2.73" | 一致 | reader_map.regions/anchor_echo | engine cell={"value": 2.73, "observation_date": "2026-10-01", "publication_date": "2026-10-30"} |
| 20 | ②锚格 | series_store[JP_POLICY_RATE] latest obs with (presumed) pub ≤ 2026-05-23 | "2026-04-01=0.727" | "2026-04-01=0.727" | 一致 | reader_map.regions/anchor_echo | engine cell={"value": 0.727, "observation_date": "2026-04-01", "publication_date": "2026-05-05"} |
| 21 | ②锚格 | series_store[JP_POLICY_RATE] latest obs with (presumed) pub ≤ 2026-11-23 | "2026-10-01=1.227" | "2026-10-01=1.227" | 一致 | reader_map.regions/anchor_echo | engine cell={"value": 1.227, "observation_date": "2026-10-01", "publication_date": "2026-11-05"} |
| 22 | ②锚格 | anchor_echo(12 格) vs 快照各序列「已发布≤锚日」最新观测 | "12/12" | "12/12" | 一致 | reader_map.regions[*].anchor_echo |  |
| 23 | ②锚格 | 截止日 2026-11-23 − 6 个自然月 | "2026-05-23" | "2026-05-23" | 一致 | headline_conclusion | engine question_window={"months": 6, "from": "2026-05-23", "to": "2026-11-23", "source": "最近六个月"} |
| 24 | ③同比对照 | series_store[EA_HICP_YOY] 2025-10 | 2.1 | 2.1 | 一致 | headline/EA from_to |  |
| 25 | ③同比对照 | series_store[JP_CPI_YOY] 2025-10 | 2.99 | 2.99 | 一致 | headline/JP from_to |  |
| 26 | ③同比对照 | EA 2026-10 − 2025-10 | 1.9 | 1.9 | 一致 | C1/EA from_to |  |
| 27 | ③同比对照 | JP 2026-10 − 2025-10 | -0.55 | -0.55 | 一致 | C1/JP from_to |  |
| 28 | ③同比对照 | EA 2026-10 − JP 2026-10 | 1.56 | 1.56 | 一致 | C1 |  |
| 29 | ③同比对照 | series_store[JP_CPI_TOKYO_YOY].dates[0] | "2026-01-01" | "2026-01-01(去年同月不在序列)" | 一致 | C1/JP from_to | n=10, last=2026-10-01 |
| 30 | ③同比对照 | EA latest − EA 6m anchor | 1.0 | 1.0 | 一致 | C1 |  |
| 31 | ③同比对照 | JP latest − JP 6m anchor | 1.06 | 1.06 | 上下文(不计入) | C1 | JP 1.38→2.44 = +1.06pp ("约一个百分点") |
| 32 | ③同比对照 | series_store[JP_POLICY_RATE] 2025-11 | 0.478 | 0.478 | 一致 | JP from_to |  |
| 33 | ③同比对照 | (JP_POLICY_RATE 2026-10 − 2025-11)×100 | 74.9 | 75 | 一致 | JP from_to |  |
| 34 | ③同比对照 | (JP_POLICY_RATE 2026-10 − 2026-04)×100 | 50.0 | 50 | 一致 | JP from_to/C2 |  |
| 35 | ③同比对照 | JP_POLICY_RATE first obs≥2025-11-23 → 2026-10 (引擎窗首尾口径) | 67.0 | 67 | 一致 | JP from_to | window start obs=2025-12-01=0.557; engine policy_window_path.net_bp=67 (窗首尾观测差口径,不含窗启前 2025-11-01→2025-12-01 的 +8bp) |
| 36 | ③同比对照 | engine policy_window_path(JP_POLICY_RATE).events (date, from, to, seriesΔbp, engineΔbp) | [["2025-12-01", 0.478, 0.557, 8, 8], ["2026-01-01", 0.557, 0.728, 17, 17], ["2026-06-01", 0.727, 0.841, 11, 11], ["2026-07-01", 0.841, 0.978, 14, 14], ["2026-09-01", 0.977, 1.043, 7, 7], ["2026-10-01", 1.043, 1.227, 18, 18]] | "seriesΔbp == engineΔbp for all 6 events" | 一致 | JP from_to | Σ engine delta_bp=75 (窗内事件合计,引擎 net_bp=67 为窗首尾观测差); engine events=[["2025-12-01", 0.478, 0.557, 8], ["2026-01-01", 0.557, 0.728, 17], ["2026-06-01", 0.727, 0.841, 11], ["2026-07-01", 0.841, 0.978, 14], ["2026-09-01", 0.977, 1.043, 7], ["2026-10-01", 1.043, 1.227, 18]]; 判断档三口径(+50/+75/+67)各自正确 |
| 37 | ③同比对照 | report.json policy_window_path(JP_POLICY_RATE).window | "[\"2025-11-23\", \"2026-11-23\"]" | "2025-11-23..2026-11-23" | 一致 | JP from_to | engine face |
| 38 | ③同比对照 | ECB 六个月锚间: MRO 2.65−2.15, DFR 2.5−2.0 | [0.5, 0.5] | [0.5, 0.5] | 一致 | headline | 两次各 25bp 合计 50bp |
| 39 | ③同比对照 | DFR 2.5 − 日历 JP_POLICY_TARGET 1.25 | 1.25 | 1.25 | 一致 | C2 |  |
| 40 | ④政策面 | series_store[ECB_DFR] 2026 变更点 | ["2026-06-17", 2.0, 2.25] | ["2026-06-17", 2.0, 2.25] | 一致 | C2/M1 step2 | all 2026 change points=[('2026-06-17', 2.0, 2.25), ('2026-09-16', 2.25, 2.5)] |
| 41 | ④政策面 | series_store[ECB_DFR] 2026 变更点 | ["2026-09-16", 2.25, 2.5] | ["2026-09-16", 2.25, 2.5] | 一致 | C2/M1 step2 |  |
| 42 | ④政策面 | series_store[ECB_MRO] 2026 变更点 | ["2026-06-17", 2.15, 2.4] | ["2026-06-17", 2.15, 2.4] | 一致 | M1 step2 |  |
| 43 | ④政策面 | series_store[ECB_MRO] 2026 变更点 | ["2026-09-16", 2.4, 2.65] | ["2026-09-16", 2.4, 2.65] | 一致 | M1 step2 |  |
| 44 | ④政策面 | number of ECB change points in 2026 (two series) | [2, 2] | [2, 2] | 一致 | C2 |  |
| 45 | ④政策面 | (to−from)×100 for the four change points | [25, 25, 25, 25] | [25, 25, 25, 25] | 一致 | C2/M1 step2 |  |
| 46 | ④政策面 | weekday(2026-06-17) / 上一个周四 | "周三/2026-06-11" | "周三/2026-06-11" | 一致 | C2 | engine cell policy_dates.decision=2026-09-10 |
| 47 | ④政策面 | weekday(2026-09-16) / 上一个周四 | "周三/2026-09-10" | "周三/2026-09-10" | 一致 | C2 | engine cell policy_dates.decision=2026-09-10 |
| 48 | ④政策面 | weekday(2025-06-11) / 上一个周四 | "周三/2025-06-05" | "周三/2025-06-05" | 一致 | MAP_REPORT 政策口径四分面 | engine cell 6个月前 policy_dates.decision=2025-06-05 |
| 49 | ④政策面 | 2026-09-16 − 2026-06-17 | 91 | 91 | 一致 | link1 verdict_note |  |
| 50 | ④政策面 | 2026-06-17 − 2025-06-11; obs strictly between | [371, 0] | [371, 0] | 一致 | link1 verdict_note | ECB_MRO likewise 0 obs between |
| 51 | ④政策面 | 2026-11-23 − ECB last obs 2026-09-16 | 68 | 68 | 一致 | C3② |  |
| 52 | ④政策面 | registry[ECB_MRO/ECB_DFR].freshness.max_calendar_lag_days | {"ECB_MRO": 10, "ECB_DFR": 10} | {"ECB_MRO": 10, "ECB_DFR": 10} | 一致 | C3② |  |
| 53 | ④政策面 | snapshot.gate_a.noncore_degraded ⊇ {ECB_DFR, ECB_MRO} | [true, true] | [true, true] | 一致 | C3② |  |
| 54 | ④政策面 | snapshot.facts[ECB_*@2026-09-16].quality_status / issue msg | ["DEGRADED", "DEGRADED", true] | ["DEGRADED", "DEGRADED", true] | 一致 | C3② |  |
| 55 | ④政策面 | report.json layers.L1_事实层.rows[ECB_*].quality_status | ["DEGRADED", "DEGRADED"] | ["DEGRADED", "DEGRADED"] | 一致 | C3② |  |
| 56 | ④政策面 | release_calendar.entries[metric_id startswith ECB] | 0 | 0 | 一致 | C2/C3② |  |
| 57 | ④政策面 | release_calendar RC-JP-BOJ-TARGET-2026-09 | ["2026-09-18", "2026-09-24", 1.25, "user_directive"] | ["2026-09-18", "2026-09-24", 1.25, "user_directive"] | 一致 | C2/M1 step2 |  |
| 58 | ④政策面 | release_calendar RC-JP-BOJ-MAINT-2026-10 | ["2026-10-30", 1.25] | ["2026-10-30", 1.25] | 一致 | C2/M1 step2 |  |
| 59 | ④政策面 | release_calendar JP_POLICY_TARGET entries (count) | 2 | 2 | 上下文(不计入) | C3③ | calendar also holds 3 EA_HICP_YOY historical entries (2021M05/2022M06/2025M03) not covering the window |
| 60 | ④政策面 | calendar JP_POLICY_TARGET entries with effective_on > cutoff (待生效) | 0 | 0 | 一致 | EA from_to |  |
| 61 | ④政策面 | 2026-11-23 − 2026-09-24 (按生效日) | 60 | 60 | 一致 | MAP_REPORT 政策官方记录面 |  |
| 62 | ④政策面 | 2026-11-23 − 2026-09-18 (按决议日) | 66 | 66 | 一致 | MAP_REPORT 政策官方记录面 |  |
| 63 | ④政策面 | 2026-11-23 − 2026-10-30 (距维持) | 24 | 24 | 一致 | MAP_REPORT 政策官方记录面 |  |
| 64 | ④政策面 | registry metric ids / snapshot series_store contain JP_POLICY_TARGET? | [false, false] | [false, false] | 一致 | C2/C3① |  |
| 65 | ④政策面 | registry[JP_POLICY_RATE].value_type | "monthly_avg_rate" | "monthly_avg_rate" | 一致 | C2 |  |
| 66 | ④政策面 | 决议→生效 days (ECB ×2) | [6, 6] | [6, 6] | 一致 | MAP_REPORT 事件簇 |  |
| 67 | ④政策面 | 2026-09-18 (BOJ 决议) − 2026-09-16 (ECB 生效) | 2 | 2 | 一致 | C2 节奏对照 | mixed calibre (ECB effective vs BOJ decision); like-for-like: effective↔effective=8d, decision↔decision=8d |
| 68 | ④政策面 | like-for-like 2026-09-24 (BOJ 生效) − 2026-09-16 (ECB 生效) | 8 | "(未述; 同口径=8天)" | 上下文(不计入) | C2 节奏对照 | ctx: same-kind distance is 8 days; judgment text gives both BOJ dates so ordering is unaffected |
| 69 | ④政策面 | series_store[JP_POLICY_RATE] 2026-05→2026-06 | [0.727, 0.841] | [0.727, 0.841] | 一致 | M1 step2 |  |
| 70 | ④政策面 | series_store[JP_POLICY_RATE] 2026-06→2026-07 | [0.841, 0.978] | [0.841, 0.978] | 一致 | M1 step2 |  |
| 71 | ④政策面 | series_store[JP_POLICY_RATE] 2026-08→2026-09 | [0.977, 1.043] | [0.977, 1.043] | 一致 | M1 step2 |  |
| 72 | ④政策面 | series_store[JP_POLICY_RATE] 2026-09→2026-10 | [1.043, 1.227] | [1.043, 1.227] | 一致 | M1 step2 |  |
| 73 | ④政策面 | Σ four JP monthly steps ×100 | 50.1 | 50 | 一致 | M1 step2 |  |
| 74 | ④政策面 | no-look-ahead: EA_HICP_YOY obs 2026-05 presumed pub vs anchor 2026-05-23 | "2026-06-16" | "> 2026-05-23 (锚取 2026-04 期)" | 一致 | 锚格 | next-month reading not yet public at the 6-month anchor → anchor uses 2026-04 obs |
| 75 | ④政策面 | no-look-ahead: JP_CPI_YOY obs 2026-05 presumed pub vs anchor 2026-05-23 | "2026-06-20" | "> 2026-05-23 (锚取 2026-04 期)" | 一致 | 锚格 | next-month reading not yet public at the 6-month anchor → anchor uses 2026-04 obs |
| 76 | ④政策面 | no-look-ahead: JP_CPI_TOKYO_YOY obs 2026-05 presumed pub vs anchor 2026-05-23 | "2026-05-30" | "> 2026-05-23 (锚取 2026-04 期)" | 一致 | 锚格 | next-month reading not yet public at the 6-month anchor → anchor uses 2026-04 obs |
| 77 | ④政策面 | no-look-ahead: JP_POLICY_RATE obs 2026-05 presumed pub vs anchor 2026-05-23 | "2026-06-05" | "> 2026-05-23 (锚取 2026-04 期)" | 一致 | 锚格 | next-month reading not yet public at the 6-month anchor → anchor uses 2026-04 obs |
| 78 | ④政策面 | JP_POLICY_RATE 2026-08 (0.978→0.977 非上行台阶) | [0.978, 0.977] | [0.978, 0.977] | 一致 | turnings[1].narrative |  |
| 79 | ④政策面 | JP step month of 0.977→1.043 vs ECB effective month | ["2026-09", "2026-09"] | "同月" | 一致 | C2 节奏对照 | JP_POLICY_RATE obs 2026-09-01 (0.977→1.043); ECB effective 2026-09-16 |
| 80 | ④政策面 | snapshot.facts USDJPY/SPX/VIX @2026-11-23 | [159.35, 7203.85, 27.01] | [159.35, 7203.85, 27.01] | 一致 | C2 末句 |  |
| 81 | ④政策面 | report.json L1 rows JP_CPI_YOY / EA_HICP_YOY quality_status | ["WARN", "WARN"] | ["WARN", "WARN"] | 一致 | C1 |  |
| 82 | ④政策面 | ECB last obs date == last change date (两序列) | ["2026-09-16", "2026-09-16"] | ["2026-09-16", "2026-09-16"] | 一致 | C2 |  |
| 83 | ⑤利率分解 | series_store[UST_10Y] 2026-10-20 → 2026-11-19 | [5.12, 5.04] | [5.12, 5.04] | 一致 | rates_decomposition |  |
| 84 | ⑤利率分解 | series_store[TIPS_10Y] 2026-10-20 → 2026-11-19 | [2.77, 2.88] | [2.77, 2.88] | 一致 | rates_decomposition |  |
| 85 | ⑤利率分解 | series_store[BEI_10Y] 2026-10-20 → 2026-11-19 | [2.35, 2.16] | [2.35, 2.16] | 一致 | rates_decomposition |  |
| 86 | ⑤利率分解 | Δ nominal bp | -8.0 | -8.0 | 一致 | rates_decomposition |  |
| 87 | ⑤利率分解 | Δ real bp | 11.0 | 11.0 | 一致 | rates_decomposition |  |
| 88 | ⑤利率分解 | Δ breakeven bp | -19.0 | -19.0 | 一致 | rates_decomposition |  |
| 89 | ⑤利率分解 | nominal − (real + breakeven) at to-date | 0.0 | 0 | 一致 | rates_decomposition | levels 5.04 / 2.88 / 2.16 |
| 90 | ⑤利率分解 | Δbp identity: −8 − (11 + −19) | 0.0 | 0 | 一致 | rates_decomposition |  |
| 91 | ⑤利率分解 | trio window / calendar days | ["2026-10-20", "2026-11-19", 30] | ["2026-10-20", "2026-11-19", 30] | 一致 | rates_decomposition |  |
| 92 | ⑤利率分解 | series_store[UST_10Y] 2025-11-19 → 2026-11-19 (12m, ≤窗端最后观测) | 91.0 | 91.0 | 一致 | MAP_REPORT 美债三利率分解(年度窗) | engine chg_bp_12m |
| 93 | ⑤利率分解 | series_store[TIPS_10Y] 2025-11-19 → 2026-11-19 (12m, ≤窗端最后观测) | 102.0 | 102.0 | 一致 | MAP_REPORT 美债三利率分解(年度窗) | engine chg_bp_12m |
| 94 | ⑤利率分解 | series_store[BEI_10Y] 2025-11-19 → 2026-11-19 (12m, ≤窗端最后观测) | -11.0 | -11.0 | 一致 | MAP_REPORT 美债三利率分解(年度窗) | engine chg_bp_12m |
| 95 | ⑤资产月窗 | series_store[SPX] 2026-10-23 → 2026-11-23 | -5.51 | -5.51 | 一致 | asset_returns_echo / M1 step4 | engine row chg_pct=-5.51 |
| 96 | ⑤资产月窗 | series_store[NIKKEI225] 2026-10-23 → 2026-11-20 | -9.98 | -9.98 | 一致 | asset_returns_echo / M1 step4 | engine row chg_pct=-9.98 |
| 97 | ⑤资产月窗 | series_store[DAX] 2026-10-23 → 2026-11-23 | 0.11 | 0.11 | 一致 | asset_returns_echo / M1 step4 | engine row chg_pct=0.11 |
| 98 | ⑤资产月窗 | series_store[VIX] 2026-10-23 → 2026-11-23 | 38.87 | 38.87 | 一致 | asset_returns_echo / M1 step4 | engine row chg_pct=38.87 |
| 99 | ⑤资产月窗 | reader_map.asset_returns_echo vs engine asset_moves.rows | "4/4" | "4/4" | 一致 | asset_returns_echo |  |
| 100 | ⑦传导·环2/3汇率 | series_store[EURUSD] 2026-10-23 → 2026-11-20 | [1.122146, 1.096972, -2.24] | [1.1221, 1.097, -2.24] | 一致 | M1 step3 / link2 |  |
| 101 | ⑦传导·环2/3汇率 | series_store[USDJPY] 2026-10-23 → 2026-11-20 | [156.494003, 159.707001, 2.05] | [156.494, 159.707, 2.05] | 一致 | M1 step3 / link2 |  |
| 102 | ⑦传导·环2/3汇率 | series_store[DXY] 2026-10-23 → 2026-11-20 | [101.809998, 103.809998, 1.96] | [101.81, 103.81, 1.96] | 一致 | M1 step3 / link2 |  |
| 103 | ⑦传导·环2/3汇率 | series_store[EURUSD] 2026-10-23 → 2026-11-23 | [1.122146, 1.093972, -2.51] | [1.1221, 1.094, -2.51] | 一致 | M1 step3 / link2 |  |
| 104 | ⑦传导·环2/3汇率 | series_store[USDJPY] 2026-10-23 → 2026-11-23 | [156.494003, 159.347, 1.82] | [156.494, 159.347, 1.82] | 一致 | M1 step3 / link2 |  |
| 105 | ⑦传导·环2/3汇率 | series_store[DXY] 2026-10-23 → 2026-11-23 | [101.809998, 104.079002, 2.23] | [101.81, 104.079, 2.23] | 一致 | M1 step3 / link2 |  |
| 106 | ⑦传导·环2/3汇率 | direction: EURUSD Δ<0, USDJPY Δ>0, DXY Δ>0 (两口径) | [true, true, true] | [true, true, true] | 一致 | link2 |  |
| 107 | ⑦传导·环4资产 | series_store[SPX] 2026-10-23 → 2026-11-20 (同日收盘) | -9.36 | -9.36 | 一致 | M1 step4 / link3 |  |
| 108 | ⑦传导·环4资产 | series_store[DAX] 2026-10-23 → 2026-11-20 (同日收盘) | -1.5 | -1.5 | 一致 | M1 step4 / link3 |  |
| 109 | ⑦传导·环4资产 | series_store[CAC40] 2026-10-23 → 2026-11-20 (同日收盘) | 1.86 | 1.86 | 一致 | M1 step4 / link3 |  |
| 110 | ⑦传导·环4资产 | series_store[NIKKEI225] 2026-10-23 → 2026-11-20 | -9.98 | -9.98 | 一致 | M1 step4 |  |
| 111 | ⑦传导·环4资产 | VIX 2026-10-23 → 2026-11-20 | [19.450001, 35.889999, 84.52] | [19.45, 35.89, 84.5] | 一致 | M1 step4 |  |
| 112 | ⑦传导·环4资产 | series_store[VIX] 2026-11-13 | 19.299999 | 19.3 | 一致 | M1 step4 VIX 路径 |  |
| 113 | ⑦传导·环4资产 | series_store[VIX] 2026-11-16 | 22.91 | 22.91 | 一致 | M1 step4 VIX 路径 |  |
| 114 | ⑦传导·环4资产 | series_store[VIX] 2026-11-17 | 25.459999 | 25.46 | 一致 | M1 step4 VIX 路径 |  |
| 115 | ⑦传导·环4资产 | series_store[VIX] 2026-11-18 | 24.559999 | 24.56 | 一致 | M1 step4 VIX 路径 |  |
| 116 | ⑦传导·环4资产 | series_store[VIX] 2026-11-19 | 28.440001 | 28.44 | 一致 | M1 step4 VIX 路径 |  |
| 117 | ⑦传导·环4资产 | series_store[VIX] 2026-11-20 | 35.889999 | 35.89 | 一致 | M1 step4 VIX 路径 |  |
| 118 | ⑦传导·环4资产 | VIX 2026-11-20 close → 2026-11-23 snapshot | -24.74 | -24.7 | 一致 | M1 step4 / link3 |  |
| 119 | ⑦传导·环4资产 | 2026-11-13 − 2026-10-30 | 14 | 14 | 一致 | link3 verdict_note |  |
| 120 | ⑦传导·环4资产 | 2026-11-13 − 2026-09-16 | 58 | 58 | 一致 | link3 verdict_note |  |
| 121 | ⑦传导·环4资产 | VIX closes strictly after 2026-11-13 up to 2026-11-20 | 5 | 5 | 一致 | M1 step4 |  |
| 122 | ⑬窗·逐月路径/转折 | series_store[EA_HICP_YOY] 2026-05 | 3.2 | 3.2 | 一致 | M1 step1 / EA from_to |  |
| 123 | ⑬窗·逐月路径/转折 | series_store[EA_HICP_YOY] 2026-06 | 2.8 | 2.8 | 一致 | M1 step1 / EA from_to |  |
| 124 | ⑬窗·逐月路径/转折 | series_store[EA_HICP_YOY] 2026-07 | 2.9 | 2.9 | 一致 | M1 step1 / EA from_to |  |
| 125 | ⑬窗·逐月路径/转折 | series_store[EA_HICP_YOY] 2026-08 | 3.2 | 3.2 | 一致 | M1 step1 / EA from_to |  |
| 126 | ⑬窗·逐月路径/转折 | series_store[EA_HICP_YOY] 2026-09 | 3.8 | 3.8 | 一致 | M1 step1 / EA from_to |  |
| 127 | ⑬窗·逐月路径/转折 | series_store[EA_HICP_YOY] 2026-10 | 4.0 | 4.0 | 一致 | M1 step1 / EA from_to |  |
| 128 | ⑬窗·逐月路径/转折 | series_store[JP_CPI_YOY] 2026-05 | 1.53 | 1.53 | 一致 | M1 step1 / JP from_to |  |
| 129 | ⑬窗·逐月路径/转折 | series_store[JP_CPI_YOY] 2026-06 | 1.67 | 1.67 | 一致 | M1 step1 / JP from_to |  |
| 130 | ⑬窗·逐月路径/转折 | series_store[JP_CPI_YOY] 2026-07 | 1.97 | 1.97 | 一致 | M1 step1 / JP from_to |  |
| 131 | ⑬窗·逐月路径/转折 | series_store[JP_CPI_YOY] 2026-08 | 1.98 | 1.98 | 一致 | M1 step1 / JP from_to |  |
| 132 | ⑬窗·逐月路径/转折 | series_store[JP_CPI_YOY] 2026-09 | 2.16 | 2.16 | 一致 | M1 step1 / JP from_to |  |
| 133 | ⑬窗·逐月路径/转折 | series_store[JP_CPI_YOY] 2026-10 | 2.44 | 2.44 | 一致 | M1 step1 / JP from_to |  |
| 134 | ⑬窗·逐月路径/转折 | min/max of (EA − JP) 2026-05..2026-10 | [0.93, 1.67] | [0.93, 1.67] | 一致 | M1 step1 | gaps={'2026-05': 1.67, '2026-06': 1.13, '2026-07': 0.93, '2026-08': 1.22, '2026-09': 1.64, '2026-10': 1.56} |
| 135 | ⑬窗·逐月路径/转折 | EA 2026-06 < 2026-05 (非逐月单调) | true | true | 一致 | M1 step1 |  |
| 136 | ⑬窗·逐月路径/转折 | JP 2026-05..2026-10 strictly increasing | true | true | 一致 | M1 step1 |  |
| 137 | ⑬窗·逐月路径/转折 | JP_CPI_YOY 2026-09 − EA_HICP_YOY 2026-09 | -1.64 | -1.64 | 一致 | turnings[2].narrative |  |
| 138 | ⑬窗·逐月路径/转折 | JP_CPI_TOKYO_YOY 2026-09 − EA_HICP_YOY 2026-09 | -1.11 | -1.11 | 一致 | turnings[2].narrative |  |
| 139 | ⑬窗·逐月路径/转折 | EA_HICP_YOY last obs == max(last 12 obs) | [4.0, 4.0] | [4.0, 4.0] | 一致 | EA from_to |  |
| 140 | ⑬窗·逐月路径/转折 | JP_CPI_YOY max over 2025-01..latest | ["2025-01", 4.03] | ["2025-01", 4.03] | 一致 | JP from_to |  |
| 141 | ⑬窗·逐月路径/转折 | JP_CPI_YOY min over 2025-01..latest | ["2026-02", 1.27] | ["2026-02", 1.27] | 一致 | JP from_to |  |
| 142 | ⑬窗·逐月路径/转折 | JP_CPI_YOY 2025-01→2026-02 monotonic non-increasing? | false | "「持续回落」(隐含单调)" | 上下文(不计入) | JP from_to | ctx: upticks strictly inside the decline (2025-01→2026-02) at ['2025-09', '2025-10'] |
| 143 | ⑬窗·逐月路径/转折 | Tokyo 2026-10 > 2026-09 and national 2026-10 > 2026-09 | [true, true] | [true, true] | 一致 | C1 |  |
| 144 | ⑬窗·逐月路径/转折 | EA 2026-01 / 2026-02 / 2026-05 | [1.7, 1.9, 3.2] | [1.7, 1.9, 3.2] | 一致 | turnings[0] |  |
| 145 | ⑬窗·逐月路径/转折 | EA 2026-05 − 2026-02 | 1.3 | 1.3 | 一致 | turnings[0] |  |
| 146 | ⑬窗·逐月路径/转折 | EA trough month over 2025-01..latest | "2026-01" | "2026-01" | 一致 | turnings[0].follow_or_diverge |  |
| 147 | ⑬窗·逐月路径/转折 | JP 2026-02 → 2026-05 | [1.27, 1.53] | [1.27, 1.53] | 一致 | turnings[0].follow_or_diverge |  |
| 148 | ⑬窗·逐月路径/转折 | JP_POLICY_RATE 2026-04 / 2026-06 / 2026-07 | [0.727, 0.841, 0.978] | [0.727, 0.841, 0.978] | 一致 | turnings[1] |  |
| 149 | ⑬窗·逐月路径/转折 | Tokyo 2026-06 → 2026-09 (Δ) | [1.6, 2.69, 1.09] | [1.6, 2.69, 1.09] | 一致 | turnings[2] |  |
| 150 | ⑬窗·逐月路径/转折 | JP_CPI_YOY 2026-06 → 2026-08 | [1.67, 1.98] | [1.67, 1.98] | 一致 | turnings[2].narrative |  |
| 151 | ⑬窗·逐月路径/转折 | monthly obs strictly inside window 2026-05-23..2026-11-23 (EA/JP/Tokyo/JP_POLICY_RATE) | [5, 5, 5, 5] | "6 值(2026-05..2026-10)称「窗内」(观测日在窗内=5)" | 上下文(不计入) | M1 step1 ("窗内 2026-05..2026-10 月度值") | ctx/NIT: by observation date 2026-05-01 lies before window start 2026-05-23 (only its presumed publication 06-05..06-20 falls inside); engine n_in_window=5 (2026-06..2026-10); 月份已在括号内写明,无数值影响 |
| 152 | ①④公布日·可见性 | month_end(2026-04) + rule me+16 | "2026-05-16" | "2026-05-16" | 一致 | C1/C2/regions |  |
| 153 | ①④公布日·可见性 | month_end(2026-10) + rule me+16 | "2026-11-16" | "2026-11-16" | 一致 | C1/C2/regions |  |
| 154 | ①④公布日·可见性 | month_end(2026-04) + rule me+20 | "2026-05-20" | "2026-05-20" | 一致 | C1/C2/regions |  |
| 155 | ①④公布日·可见性 | month_end(2026-10) + rule me+20 | "2026-11-20" | "2026-11-20" | 一致 | C1/C2/regions |  |
| 156 | ①④公布日·可见性 | month_end(2026-10) + rule me-1 | "2026-10-30" | "2026-10-30" | 一致 | C1/C2/regions |  |
| 157 | ①④公布日·可见性 | month_end(2026-04) + rule me-1 | "2026-04-29" | "2026-04-29" | 一致 | C1/C2/regions |  |
| 158 | ①④公布日·可见性 | month_end(2026-09) + rule me-1 | "2026-09-29" | "2026-09-29" | 一致 | C1/C2/regions |  |
| 159 | ①④公布日·可见性 | month_end(2026-08) + rule me-1 | "2026-08-30" | "2026-08-30" | 一致 | C1/C2/regions |  |
| 160 | ①④公布日·可见性 | month_end(2026-10) + rule me+5 | "2026-11-05" | "2026-11-05" | 一致 | C1/C2/regions |  |
| 161 | ①④公布日·可见性 | month_end(2026-04) + rule me+5 | "2026-05-05" | "2026-05-05" | 一致 | C1/C2/regions |  |
| 162 | ①④公布日·可见性 | 2026-11-20 − 2026-11-16 | 4 | 4 | 一致 | C1 |  |
| 163 | ①④公布日·可见性 | last EA_HICP_YOY obs with presumed pub < 2026-06-11 | ["2026-04-01", 3.0] | ["2026-04-01", 3.0] | 一致 | link1 main_predicts/verdict_note | pub=2026-05-16 |
| 164 | ①④公布日·可见性 | last EA_HICP_YOY obs with presumed pub < 2026-06-17 | ["2026-05-01", 3.2] | ["2026-05-01", 3.2] | 一致 | link1 main_predicts/verdict_note | pub=2026-06-16 |
| 165 | ①④公布日·可见性 | last EA_HICP_YOY obs with presumed pub < 2026-09-10 | ["2026-07-01", 2.9] | ["2026-07-01", 2.9] | 一致 | link1 main_predicts/verdict_note | pub=2026-08-16 |
| 166 | ①④公布日·可见性 | last EA_HICP_YOY obs with presumed pub ≤ 2026-09-16 | ["2026-08-01", 3.2] | ["2026-08-01", 3.2] | 一致 | link1 main_predicts/verdict_note | pub=2026-09-16 |
| 167 | ①④公布日·可见性 | last JP_CPI_YOY obs with presumed pub < 2026-09-18 | ["2026-07-01", 1.97] | ["2026-07-01", 1.97] | 一致 | link1 main_predicts/verdict_note | pub=2026-08-20 |
| 168 | ①④公布日·可见性 | last JP_CPI_TOKYO_YOY obs with presumed pub < 2026-09-18 | ["2026-08-01", 1.9] | ["2026-08-01", 1.9] | 一致 | link1 main_predicts/verdict_note | pub=2026-08-30 |
| 169 | ①④公布日·可见性 | presumed pub of EA 2026-08 obs | "2026-09-16" | "2026-09-16" | 一致 | link1 |  |
| 170 | ①④公布日·可见性 | min(readings visible before each ECB change) > EA 2026-02 (1.9) | true | true | 一致 | link1 verdict_note |  |
| 171 | ①④公布日·可见性 | EA 2026-01 → 2026-04 | [1.7, 3.0] | [1.7, 3.0] | 一致 | link1 verdict_note |  |
| 172 | ①④公布日·可见性 | EA max over 2026-01..2026-07 / value at 2026-05 | [3.2, 3.2] | [3.2, 3.2] | 一致 | link1 verdict_note |  |
| 173 | ⑨情景 | presumed pub of 2026-12 obs (EA me+16 / JP me+20) | ["2027-01-16", "2027-01-20"] | "<2027-02-15" | 一致 | l4.scenarios |  |
| 174 | ⑨情景 | EA latest vs S1 前提 3.5% | 4.0 | "≥3.5" | 一致 | S1 | premise compatible with cutoff; 2026-11/2026-12 obs not yet published at cutoff → not already triggered |
| 175 | ⑨情景 | EA latest vs S2 前提 (<3.0) | 4.0 | "not yet <3.0" | 一致 | S2 |  |
| 176 | ⑨情景 | JP latest vs S1 前提 (≥2.0) / S2 (<2.0) | [true, true] | [true, true] | 一致 | S1/S2 |  |
| 177 | ⑨情景 | gap at cutoff vs S1 前提 (≥1.5) | 1.56 | "≥1.5" | 一致 | S1 |  |
| 178 | ⑨情景 | S1 trigger level-conditions at cutoff (EA≥4.0 / gap≥1.5 / VIX close>30) on latest available readings | [true, true, true] | "trigger binds to 2026-11/2026-12 readings (unpublished at cutoff)" | 上下文(不计入) | S1/S2 | ctx: all three level conditions already hold on 2026-10 readings + 2026-11-20 close; the trigger is formally tied to unpublished 2026-11/2026-12 readings → still 待验证, but a no-change path would fire it (persistence scenario by design) |
| 179 | ⑨情景 | distinguishing/falsification metrics in registry | [true, true, true, true] | [true, true, true, true] | 一致 | l4 |  |
| 180 | ⑨情景 | two scenarios direction-complementary (S1 维持 vs S2 回落) | [true, true] | [true, true] | 一致 | l4.scenarios |  |
| 181 | ⑨情景 | S1: all three numeric scenario components present in falsification threshold | [true, true, true] | [true, true, true] | 一致 | l4 S1 |  |
| 182 | ⑨情景 | scenario deadlines equal and after presumed archival of 2026-12 readings | ["2027-02-15", "2027-02-15"] | ["2027-02-15", "2027-02-15"] | 一致 | l4.scenarios |  |
| 183 | ⑨情景 | S2 trigger: each below 2026-11 observation month (requires 2026-11 reading, unpublished at cutoff) | true | "not determinable at cutoff" | 一致 | l4 S2 | 2026-11 readings presumed pub 2026-12-16(EA)/2026-12-20(JP) > cutoff → trigger not yet determinable |
| 184 | ⑨情景 | S2: which scenario components appear in trigger / falsification | {"scenario_components": ["EA<3.0", "JP<2.0", "gap≤1.0"], "trigger_has": ["低于 3.0%", "低于 2.0%"], "falsification_has": ["3.5%"]} | "S1: 三分量在证伪阈值中齐全" | 上下文(不计入) | l4 S2 | ctx/MINOR: S2 证伪阈值只覆盖 EA 分量(两月均≥3.5%);日本<2.0% 与水平差≤1.0pp 两分量既不在触发条件(仅 EA<3.0% 且 JP<2.0%;无水平差)也无对应证伪——与 S1 不对称 |
| 185 | ⑪诚实缺席 | snapshot.gate_a.noncore_missing ∋ JP_CPI_TOKYO_YOY | true | true | 一致 | C1/JP from_to |  |
| 186 | ⑪诚实缺席 | snapshot.gate_a.noncore_missing_detail[JP_CPI_TOKYO_YOY] | true | true | 一致 | C1 |  |
| 187 | ⑪诚实缺席 | snapshot.facts with metric_id JP_CPI_TOKYO_YOY (count) | 0 | 0 | 一致 | C1 |  |
| 188 | ⑪诚实缺席 | report.json L1 rows with metric_id JP_CPI_TOKYO_YOY (count) | 0 | 0 | 一致 | C1 |  |
| 189 | ⑪诚实缺席 | snapshot.gate_a.noncore_missing ⊇ {EA_REAL_GDP_YOY, JP_REAL_GDP_YOY} | [true, true] | [true, true] | 一致 | C3⑤ |  |
| 190 | ⑪诚实缺席 | series_store[EA/JP_REAL_GDP_YOY] last obs / value / n | {"EA_REAL_GDP_YOY": ["2026-07-01", 1.28, 123], "JP_REAL_GDP_YOY": ["2026-07-01", 1.16, 127]} | "序列在场(至 2026-07-01)" | 上下文(不计入) | C3⑤ | ctx: series ARE present in series_store (facts absent / Gate A noncore_missing) — gap is at fact level, not series level |
| 191 | ⑪诚实缺席 | registry economy=JP/EA ids containing CORE | [] | [] | 一致 | C3⑤/C1 competing | JP=['EWJ', 'JGB10Y', 'JGB2Y', 'JGB5Y', 'JP_CPI_TOKYO_YOY', 'JP_CPI_YOY', 'JP_POLICY_RATE', 'JP_REAL_GDP_YOY', 'NIKKEI225', 'USDJPY']; EA=['BUND_10Y', 'BUND_2Y', 'CAC40', 'DAX', 'EA_HICP_YOY', 'EA_REAL_GDP_YOY', 'ECB_DFR', 'ECB_MRO', 'EURUSD', 'EWG', 'EZU', 'FEZ'] |
| 192 | ⑪诚实缺席 | registry JP/EA headline inflation ids | ["EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_CPI_YOY"] | ["EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_CPI_YOY"] | 一致 | C1 competing |  |
| 193 | ⑪诚实缺席 | snapshot.gate_a.status | "DEGRADED" | "DEGRADED" | 一致 | headline |  |
| 194 | ⑪诚实缺席 | ECB obs strictly after 2026-09-16 (two series) | [0, 0] | [0, 0] | 一致 | C3② |  |
| 195 | ⑪诚实缺席 | report.json research_plan.dimension_gaps | [["JP_POLICY_TARGET", "registry_absent"]] | [["JP_POLICY_TARGET", "registry_absent"]] | 一致 | C3①/MAP_REPORT 缺数格说明 |  |
| 196 | ⑪诚实缺席 | report.json run.data_requirements.items outcome | [["EA_HICP_YOY", "satisfied"], ["ECB_MRO", "insufficient_coverage"], ["ECB_DFR", "insufficient_coverage"], ["JP_CPI_YOY", "satisfied"], ["JP_CPI_TOKYO_YOY", "satisfied"], ["JP_POLICY_RATE", "satisfied"]] | "ECB_MRO/ECB_DFR = insufficient_coverage" | 一致 | C3② | gaps=null |
| 197 | ⑪诚实缺席 | MAP_REPORT/report.md: absent cell rendered as 数据不可得 (not 无变化) | true | true | 一致 | MAP_REPORT 缺数格说明 | report.md 亦载「JP_POLICY_TARGET … 该格以「数据不可得」呈现…不以相邻口径冒充」 |
| 198 | ⑪诚实缺席 | judgment: BOJ target 1.25 attributed to calendar; JP_POLICY_RATE never called 宣布值 | true | true | 一致 | C2 |  |
| 199 | ⑫截止日盘中 | snapshot.research_as_of → zoneinfo local times | {"纽约": "09:53", "柏林": "15:53", "东京": "23:53", "上海": "22:53"} | {"纽约": "09:53", "柏林": "15:53", "东京": "23:53", "上海": "22:53"} | 一致 | quality_gate_notes |  |
| 200 | ⑫截止日盘中 | snapshot.facts[*].observation_date == cutoff for SPX/VIX/DAX/CAC40/EURUSD/USDJPY/DXY | ["2026-11-23", "2026-11-23", "2026-11-23", "2026-11-23", "2026-11-23", "2026-11-23", "2026-11-23"] | ["2026-11-23", "2026-11-23", "2026-11-23", "2026-11-23", "2026-11-23", "2026-11-23", "2026-11-23"] | 一致 | quality_gate_notes |  |
| 201 | ⑫截止日盘中 | series_store[NIKKEI225] last obs | "2026-11-20" | "2026-11-20" | 一致 | M1 step4 | no 2026-11-23 observation for NIKKEI225 → cutoff-day cross-region comparison anchored on 2026-11-20 close |
| 202 | ⑬契约 | report.json agent_judgment.contract_verification verdicts with status≠VERIFIED | [["ECB_DFR", 2.5, "STALE"]] | [["ECB_DFR", 2.5, "STALE"]] | 一致 | C3②/headline | n numeric verdicts=5 |
| 203 | ⑬契约 | STALE item value == expected (value right, freshness stale) | true | true | 一致 | C3② | note=recompute:Fact 直读 ECB_DFR@2026-09-16=2.5 |
| 204 | ⑬契约 | contract_verification six_checks + map_checks statuses | ["VERIFIED"] | ["VERIFIED"] | 一致 | 全档 | date_order note=日期次序主张一致: 2026-09-18<2026-09-29(晚于,1 处) |
| 205 | ⑬契约 | contract_verification.verdict / stats | ["VERIFIED", 5, 0] | ["VERIFIED", 5, 0] | 一致 | report.json |  |
| 206 | ⑬'窗口 | month_end(2026-11) | "2026-11-30" | "2026-11-30" | 一致 | agent_declaration.basis |  |
| 207 | ⑬'窗口 | report.json as_of_declared | ["2026-11-30", true, "2026-11-23"] | ["2026-11-30", true, "2026-11-23"] | 一致 | headline |  |
| 208 | ⑬'窗口 | coverage_date == snapshot research_as_of date | true | true | 一致 | headline |  |
| 209 | ⑬'窗口 | report.json question_window | ["2026-05-23", "2026-11-23"] | ["2026-05-23", "2026-11-23"] | 一致 | headline |  |
| 210 | ⑦⑧引用/类比/工单面 | l3 evidence_refs count / all resolve to evidence_index | [21, true] | [21, true] | 一致 | quality_gate_notes[0] |  |
| 211 | ⑦⑧引用/类比/工单面 | steps[S6_analog].envelope.data.candidates.scanned | 1871 | 1871 | 一致 | history_zero_case_note |  |
| 212 | ⑦⑧引用/类比/工单面 | steps[S6_analog]…candidates.valid | 74 | 74 | 一致 | history_zero_case_note |  |
| 213 | ⑦⑧引用/类比/工单面 | steps[S6_analog]…top[0].candidate_month | "2025-03" | "2025-03" | 一致 | history_zero_case_note |  |
| 214 | ⑦⑧引用/类比/工单面 | steps[S6_analog]…top[0].distance | 0.727 | 0.727 | 一致 | history_zero_case_note |  |
| 215 | ⑦⑧引用/类比/工单面 | len(history_periods) / history_zero_case_note present | [0, true] | [0, true] | 一致 | reader_map |  |
| 216 | ⑦⑧引用/类比/工单面 | len(evidence_index.json) | 60 | 60 | 一致 | agent_declaration.basis |  |
| 217 | ⑩对质表/标注 | transmission links face_off_verdict tally | [0, 1, 2] | [0, 1, 2] | 一致 | quality_gate_notes[1] |  |
| 218 | ⑩对质表/标注 | competing_explanations per contradiction | [2, 2, 2] | [2, 2, 2] | 一致 | l3 |  |
| 219 | ⑩对质表/标注 | mechanism chain evidence levels / E2 steps carry 【假设】 (text or missing_link_note) | [["E1", "E1", "E2", "E2"], [false, false, true, true]] | [["E1", "E1", "E2", "E2"], [false, false, true, true]] | 一致 | l3.mechanism_chains |  |
| 220 | ⑩对质表/标注 | step4 inline label: literal 【假设】 in step-4 text? | false | "否(标签在 missing_link_note 与对质表因果/竞争解释行)" | 上下文(不计入) | l3.mechanism_chains[0].links[3] | step-4 text is an observation block whose attribution sentence has no inline label; the E2 tag + missing_link_note 「归因环节为【假设】」 carry it |
| 221 | ⑩对质表/标注 | registry JP/EA metrics vs no BOJ statement text series; policy_doc_facts | [1] | [1] | 一致 | C2 competing |  |
| 222 | ⑩对质表/标注 | engine point_values_cells / dimension gaps | [6, 0] | [6, 0] | 一致 | agent_declaration.basis |  |
| 223 | ⑩对质表/标注 | calendar version / updated | ["1.5.0", "2026-11-21"] | ["1.5.0", "2026-11-21"] | 一致 | C2/JP from_to |  |
| 224 | 反方攻击·上下文(不计入) | VIX 2026-11-04 close → 2026-11-05 close → 2026-11-11 close | [16.610001, 28.18, 69.66, 17.49, -37.93] | "(判断档未披露)" | 上下文(不计入) | link3 | in-window earlier spike and fast full reversal (close-based), relevant to competing explanation's 快速回落 |
| 225 | 反方攻击·上下文(不计入) | presumed inflation release days inside the VIX jump window: VIX day change on 2026-11-16 (EA_HICP 2026-10, me+16) / 2026-11-20 (JP_CPI 2026-10, me+20) | [18.7, 26.2] | "(判断档只量到决议日 2026-10-30/生效日 2026-09-16,未检验读数发布日)" | 上下文(不计入) | link3 verdict_note (b) | ctx/MINOR: 两个最大单日跳升日与两条推定通胀发布日重合;跨地区复核见下一行 |
| 226 | 反方攻击·上下文(不计入) | cross-region check on release days: close-to-close 2026-11-13→2026-11-20 and day changes on 11-16 / 11-20 | {"window_11-13_to_11-20": {"SPX": -8.61, "DAX": -7.28, "CAC40": -5.27, "NIKKEI225": -7.7}, "day_11-16_/_11-20": {"SPX": [-1.92, -3.7], "DAX": [-0.57, -2.6], "CAC40": [-0.2, -1.89], "NIKKEI225": [-2.42, -5.06], "EURUSD": [-0.23, -0.02], "USDJPY": [-0.06, 0.2]}} | "读数发布主因?(未述)" | 上下文(不计入) | link3 verdict_note (b) | ctx: 跳升窗内四地股指跌幅均不大于美股(SPX 最深);发布日当日同日收盘跨时区不同步(东京<欧洲<纽约),不构成地区特异性证据→结论不变 |
| 227 | 反方攻击·上下文(不计入) | SPX / NIKKEI225 2026-11-04 → 2026-11-05 | [-4.36, -1.79] | "(判断档未披露)" | 上下文(不计入) | link3 | earlier in-window risk-off episode |
| 228 | 反方攻击·上下文(不计入) | release_calendar EA_HICP_YOY entries (obs month, first_publish, final) | [["2021-05", "2021-06-01", "2021-06-17"], ["2022-06", "2022-07-01", "2022-07-19"], ["2025-03", "2025-04-01", "2025-04-16"]] | "日历实录仅覆盖日本政策目标两条" | 上下文(不计入) | C3③ | two-tier (flash/final) 实录 exists for EA_HICP_YOY, outside the window |
| 229 | 反方攻击·上下文(不计入) | MAP_REPORT header line: 研究时点口径 … 研究截止日 | true | "2026-11-23 (elsewhere in header)" | 上下文(不计入) | MAP_REPORT 头部(引擎渲染) | engine template line says cutoff 2026-11-30 while lines 4/6 say 2026-11-23 |
| 230 | ⑥转折 | turnings[0] (EA_HICP_YOY 2026-02→2026-05) vs report.json turning_candidates & series_store | ["2026-02", "2026-05", [1.9, 3.2]] | ["2026-02", "2026-05", [1.9, 3.2]] | 一致 | reader_map.turnings | candidate face: 4 candidates; judgment picked 3 distinct metrics |
| 231 | ⑥转折 | turnings[1] (JP_POLICY_RATE 2026-04→2026-07) vs report.json turning_candidates & series_store | ["2026-04", "2026-07", [0.727, 0.978]] | ["2026-04", "2026-07", [0.727, 0.978]] | 一致 | reader_map.turnings | candidate face: 4 candidates; judgment picked 3 distinct metrics |
| 232 | ⑥转折 | turnings[2] (JP_CPI_TOKYO_YOY 2026-06→2026-09) vs report.json turning_candidates & series_store | ["2026-06", "2026-09", [1.6, 2.69]] | ["2026-06", "2026-09", [1.6, 2.69]] | 一致 | reader_map.turnings | candidate face: 4 candidates; judgment picked 3 distinct metrics |
| 233 | ⑥转折 | turning dates strictly increasing and within 12 months before cutoff | ["2026-05", "2026-07", "2026-09"] | "递增、均在窗内" | 一致 | reader_map.turnings |  |
| 234 | ⑥转折 | three turnings use three distinct metrics | 3 | 3 | 一致 | reader_map.turnings | engine basis: 三转折须为不同事件 |
| 235 | ⑦传导·区分指标 | 环1 distinguishing_metric EA_HICP_YOY: in registry / in evidence_index(snapshot_fact) | [true, true] | [true, true] | 一致 | reader_map.transmission |  |
| 236 | ⑦传导·区分指标 | 环2 distinguishing_metric EURUSD: in registry / in evidence_index(snapshot_fact) | [true, true] | [true, true] | 一致 | reader_map.transmission |  |
| 237 | ⑦传导·区分指标 | 环3 distinguishing_metric VIX: in registry / in evidence_index(snapshot_fact) | [true, true] | [true, true] | 一致 | reader_map.transmission |  |
| 238 | 质量注记[5]引擎缺口披露属实性 | judgment_contract.py _map_checks 锚标签硬编码「12个月前/3个月前/最新一期」 | true | true | 一致 | quality_gate_notes[5]① | source lines with tuple: [1274, 1322] |
| 239 | 质量注记[5]引擎缺口披露属实性 | text_consistency.ALIASES 未覆盖五指标 / 含别名 CPI | [5, true] | [5, true] | 一致 | quality_gate_notes[5]② | ALIASES has 72 keys; missing=['JP_CPI_YOY', 'EA_HICP_YOY', 'JP_CPI_TOKYO_YOY', 'JP_POLICY_TARGET', 'ECB_MRO'] |
| 240 | 反方攻击·上下文(不计入) | engine cell vintages per metric (事后回顾 vs as_collected) | {"EA_HICP_YOY": ["事后回顾(最新修订值,非当时首发值)"], "ECB_MRO": ["as_collected(采集时点值)"], "ECB_DFR": ["as_collected(采集时点值)"], "JP_CPI_YOY": ["事后回顾(最新修订值,非当时首发值)"], "JP_CPI_TOKYO_YOY": ["as_collected(采集时点值)"], "JP_POLICY_RATE": ["as_collected(采集时点值)"]} | "C3④「月度数值为事后回顾口径」(全称)" | 上下文(不计入) | C3④ / quality_gate_notes[4] 末句 | ctx/NIT: 仅 EA_HICP_YOY、JP_CPI_YOY 标「事后回顾」;东京 CPI 与月均拆借利率为 as_collected(采集时点值)——④的全称表述偏宽(偏保守方向) |
| 241 | 反方攻击·上下文(不计入) | facts[JP_CPI_YOY@2026-10-01].calc 抽验句 | "抽验一致(2026-09=2.16 vs 官方2.1)" | "(判断档未述两位小数为采集端由指数水平直算)" | 上下文(不计入) | C1 | ctx/NIT: 序列值为采集端由物价指数水平直算的两位小数,官方公布为一位小数;判断档以两位小数陈述并写「约」,方向不受影响 |
| 242 | 反方攻击·上下文(不计入) | implied EURJPY = EURUSD×USDJPY (2026-10-23 → 2026-11-20) | [175.609, 175.194, -0.24] | "(判断档称 EURJPY 交叉盘不在证据面、不可直接检验)" | 上下文(不计入) | link2 / step3 | ctx: 交叉盘可由证据面两条序列相乘推出(窗内约 −0.2%%,量级很小);判断档「不可直接检验」偏保守,不改变「支持竞争解释」的倾向 |
| 243 | 反方攻击·上下文(不计入) | momentum (Δ to 2026-10) by alternative start month [EA, JP] | {"2026-04": [1.0, 1.06], "2026-05": [0.8, 0.91], "2026-06": [1.2, 0.77], "2026-07": [1.1, 0.47]} | "C1「窗内动量不分化」(锚=2026-04 期: +1.0 / +1.06)" | 上下文(不计入) | C1 | ctx/反方攻击: 「动量相近」依赖起点取 2026-04 期;自 2026-06 起算为 +1.2 / +0.77、自 2026-07 为 +1.1 / +0.47(欧元区更快),自 2026-05 为 +0.8 / +0.91(日本更快)——陈述已限定锚点,不构成错误,结论对起点敏感 |
| 244 | 反方攻击·上下文(不计入) | level gap by ECB rate chosen: DFR 2.5−1.25 / MRO 2.65−1.25 | [1.25, 1.4] | "C2 用 DFR→约 1.25pp;step3/环2 用 MRO 2.65 vs 1.25" | 上下文(不计入) | C2 / step3 / link2 | ctx/NIT: 两处水平差所用欧央行利率不同(均已写明利率名),量级差 0.15pp,不改变「欧元区高于日本」的方向 |
| 245 | 反方攻击·上下文(不计入) | judgment long text blocks rendered verbatim (MAP / FULL / neither) | {"MAP": 24, "FULL": 17, "neither": [".reader_map.transmission[0].links[0].verdict_note", ".reader_map.transmission[0].links[1].verdict_note", ".reader_map.transmission[0].links[2].verdict_note", ".reader_map.turnings[0].narrative", ".reader_map.turnings[1].narrative", ".reader_map.turnings[2].narrative"]} | "渲染文字与判断档逐字一致" | 上下文(不计入) | 读者报告 | ctx(范围外观察): 渲染出的判断文字均逐字一致;未渲染=三条 verdict_note 与三条 turnings.narrative(对质理由与逐月叙述未进读者面) |
| 246 | ⑩走位文字 | EA_HICP_YOY 2026-05..2026-10: dip month(s) | [1] | "2026-06 回落至 2.8,非逐月单调" | 一致 | M1 step1 |  |
| 247 | ⑩走位文字 | JP_CPI_YOY 2026-02 → 2026-10 (此后总体回升) | [1.27, 2.44] | [1.27, 2.44] | 一致 | JP from_to | non-monotonic: 2026-04 1.38 < 2026-03 1.46 (「总体」措辞如实) |
| 248 | ⑩走位文字 | step4 levels: DAX 2026-11-23 / NIKKEI225 2026-11-20 | [25209.449219, 56436.65] | [25209.45, 56436.65] | 一致 | M1 step4 |  |
| 249 | ⑩走位文字 | UST_10Y latest obs / value | ["2026-11-19", 5.04] | ["2026-11-19", 5.04] | 一致 | link2 verdict_note |  |

统计: 计入比对点数=228, 偏离=0, 上下文点(不计入)=21, snip 未命中=0
