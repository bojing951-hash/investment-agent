# Audit-R32 · N30 · Round-1 独立语义审查席纪要(PROSE)

- 席位: semantic-audit-seat / independent-zero-context-seat-r32-n30-round1(零上下文;与研判席、操作席及其他审查席之间无任何通信,全部产出仅为文件)
- 受审运行: `20261123T193232Z_2026年11月_日本和欧元区最近六个月的通胀与政策环境有什么不同_哪些方面分化`
- 代码印章: `0f3936dd7eb74c557a2350e400d58e10a09c5139`(MAP_REPORT 头部第 4 行)
- 受审对象: agent_judgment.json 全文(l3/l4/reader_map/quality_gate_notes/agent_declaration,schema 1.1)与读者报告(MAP_REPORT.md / FULL_REPORT.md / report.md)中的判断文字
- 裁决: **UPHELD**(MAJOR 0 / MINOR 7 / NIT 10;must_fix 空)
- 复算: 计入比对点 **228**,偏离 **0**;上下文点 21 个(不计入);逐点出处键见下表

## 0. 独立性与只读声明

- 未联网;未运行引擎 plan/attach/report/archive/replay/update 等任何写操作;未调用 record_semantic_verdict;未委派子代理。
- 未读取规程 §2 禁区: research_archive/、树内 docs/、/tmp/r32-accept/out|scripts|replay|install*|final*(只读安装树内两份引擎源码文件除外)、其他运行目录、review 目录下除本席产出目录以外的任何目录、~/investment-agent-product。
- 只读取的只读面: 受审运行目录下 report.json、agent_judgment.json、MAP_REPORT.md、FULL_REPORT.md、report.md、evidence_index.json、views_digest.json、AGENT_SEAT_ENVELOPE.json、question_verbatim.txt、root_overlay/config/release_calendar.json、root_overlay/config/metric_registry.json、root_overlay/data/daily/research_snapshot_20261123.json;以及只读安装树内 scripts/research_contract/judgment_contract.py 与 text_consistency.py(仅用于核验 quality_gate_notes[5]①② 的属实性,以路径参数只读打开)。
- 未使用记忆或常识补数;本纪要引用的每个数字均来自上述只读面并注明出处键(复算表行号 #n 对应表内「出处键」列;日频收盘类数字出处为 series_store[<metric_id>].dates/values)。
- 自写脚本与中间表全部在本席目录 /tmp/r32-accept/review4/N30_round1/;受审运行目录与安装树未写入任何文件。

## 1. 复算方法与计数

- 逐点先从冻结快照 series_store、冻结日历、report.json 引擎面直算,再与报告/判断档文字比对;每条「报告值」均经字面片段守卫(确认该转述确实存在于判断档或读者报告原文,未命中 0 条)。
- 锚格规则: 月频序列以「引擎推定发布日 ≤ 锚日」的最新观测为锚(EA HICP 月末+16 天、日本全国 CPI 月末+20 天、东京 CPI 月末−1 天、BOJ 月均 月末+5 天;与点值格 publication_date 及规则串一致);六个月前锚(2026-05-23)因此取 2026-04 期,无前视(复算表 #10–#22、#74–#77)。
- 单位约定: 1 个百分点 = 100bp;「bp」换算按 (差)×100。
- 分档: 「一致」计入命中;「上下文(不计入)」为席位补充检验(反方攻击、敏感性、范围外观察),不计入命中/偏离。
- 分类计数(计入点): ④政策面=41; ⑬窗·逐月路径/转折=28; ①④公布日·可见性=21; ③同比对照=15; ⑦传导·环4资产=15; ②锚格=14; ⑪诚实缺席=13; ⑤利率分解=12; ⑨情景=10; ①截止日=9; ⑦⑧引用/类比/工单面=7; ⑦传导·环2/3汇率=7; ⑩对质表/标注=6; ⑤资产月窗=5; ⑥转折=5; ⑩走位文字=4; ⑬'窗口=4; ⑬契约=4; ⑦传导·区分指标=3; ⑫截止日盘中=3; 质量注记[5]引擎缺口披露属实性=2
- 分类计数(上下文点,不计入): 反方攻击·上下文(不计入)=12; ④政策面(上下文(不计入))=2; ⑨情景(上下文(不计入))=2; ⑬窗·逐月路径/转折(上下文(不计入))=2; ③同比对照(上下文(不计入))=1; ⑩对质表/标注(上下文(不计入))=1; ⑪诚实缺席(上下文(不计入))=1

## 2. 复算清单(逐点: 出处键 / 直算值 / 报告值 / 一致与否)

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

## 3. 六查逐项结论(证据相关性 / 支持度 / 竞争解释 / 反对证据 / 结论是否超出证据 / 证伪条件可观测性)

### C1-INFL-DIVERGE(水平与同比方向分化、窗内动量不分化)

- **证据相关性**: 相关。证据引用 JP_CPI_YOY@2026-10-01、EA_HICP_YOY@2026-10-01 均在证据索引;水平差 1.56、同比对照(2025-10: 2.1/2.99,同比差 +1.9/−0.55)、欧元区锚间动量 +1.0 全部由 series_store 直算一致(复算表 #24–#28、#30);日本锚间动量 +1.06 为上下文点(#31,判断档写「均约一个百分点」)。
- **支持度**: 「约一点五六」「均约一个百分点」为限定措辞,与证据强度相称;东京序列只作同月方向佐证,并披露 Gate A noncore_missing、无 L1 事实行、缺去年同月基期(#29、#143、#185–#188)。
- **竞争解释**: 两条(能源/进口传导 vs 需求与政策组合)均标【假设】,并写明引擎无分项构成与核心通胀序列、不可在引擎面验证——真正竞争且同证据可容纳,非稻草人。
- **反对证据**: 动量结论对起点敏感(自 2026-06 期起算欧元区 +1.2 对日本 +0.77,见 #243)而未加注——陈述已限定锚点,列 NIT;无其他未披露反向事实。
- **结论是否超出证据**: 未超出。缺基期处(东京)如实拒答同比,未以相邻月替代。
- **证伪条件可观测性**: C1 的两条竞争解释均自陈不可在引擎面验证、未设证伪阈值,如实并列,不以单侧证据裁;可观测的证伪面由 L4 两情景承担(见情景节)。

### C2-POLICY-SYNC-LEVEL-GAP(同向收紧、累计幅度相近、水平分化、口径基础不对称)

- **证据相关性**: 相关。六个证据引用全在索引;DFR/MRO 变更日与幅度(2026-06-17、2026-09-16,各 +25bp)、BOJ 日历两条(09-18 决议/09-24 生效/目标 1.25;10-30 维持)、月均台阶(0.727→1.227,+50bp)、68 天、水平差 1.25 由 series_store 与冻结日历直算一致(#39–#45、#51、#57–#58、#69–#73、#82)。
- **支持度**: 「累计幅度相近」附口径声明(宣布值口径 vs 月均市场口径,仅作量级对照);欧央行决议日标【推断】;总判断写「其后决议面不可判【尚未验证】」。措辞与证据强度相称。
- **竞争解释**: 读数驱动 vs 正常化/汇率-金融稳定驱动,后者写明引擎无央行表态文本序列、月频不可区分——真正竞争。
- **反对证据**: (1)「相隔两天」两端口径不对称,同口径 8 天(#67–#68);(2)水平差用 DFR(1.25)而环3 用 MRO(1.40),见 #244。均不改变「欧元区在前/高于日本」方向 → MINOR + NIT。
- **结论是否超出证据**: 未超出;「口径基础不对称」与引擎 dimension_gaps(JP_POLICY_TARGET=registry_absent)一致(#195),数据需求面 ECB_MRO/ECB_DFR=insufficient_coverage 如实披露(#196)。
- **证伪条件可观测性**: 由传导环1 的对质承担(读数可见性 vs 程序驱动),区分指标 EA_HICP_YOY 在证据面(#235);两解释在其上的预期方向不同(决议前读数已抬升 / 无稳定先后关系)。

### C3-EVIDENCE-GAPS(证据不足五项)

- **证据相关性**: 相关。五项逐一对应问句「哪些证据不足」。
- **支持度**: 「引擎可核者五项」逐项序列级证实: ①注册表与 series_store 均无 JP_POLICY_TARGET(#64);②末观测 2026-09-16、距截止 68 天>注册表新鲜度阈 10 天、L1 quality_status=DEGRADED(#51–#55);③月度公布日为引擎推定规则(点值格 publication_date 附规则串,#152–#161);④仅 EA_HICP_YOY、JP_CPI_YOY 为「事后回顾」(#240);⑤Gate A noncore_missing 含两 GDP 序列、注册表 JP/EA 面无核心通胀(#189–#192)。
- **竞争解释**: 两条(此后无新决议 vs 有新决议)标【假设】,指明须官网核对、引擎外、待授权——如实并列。
- **反对证据**: ③漏计三条历史期 EA HICP 两档实录(#228);⑤与总判断把「事实行缺席」写成「序列缺席」(#190)→ 2 MINOR;④全称偏宽、①「实录单条」与③「两条」并置 → 2 NIT。
- **结论是否超出证据**: 未超出。契约 STALE 项(ECB_DFR@2026-09-16=2.5)披露一致(#202–#203);缺席格写「数据不可得」而非「无变化」(#197);BOJ 目标 1.25 归属日历实录,未把月均序列值写成官方目标(#198)。
- **证伪条件可观测性**: 竞争解释的裁定路径在引擎外(官网核对),已标注「须单独标注,待用户授权」,未冒充引擎可核。

### M1-DIVERGE-TRANSMIT(通胀读数→政策决议→汇率→风险资产,四环+三环对质)

- **证据相关性**: 相关。环1 六个月两条路径(#122–#136)、环2 四个欧央行变更点与日本月均台阶(#40–#45、#69–#73)、环3 两口径汇率窗(#100–#106)、环4 同日收盘口径与 VIX 路径(#107–#121)全部回贴一致;四环证据引用均在索引(#210)。
- **支持度**: 环1/环2 标 E1,文字为「观察:」;环3 标 E2 且行内「传导【假设】」;环4 标 E2,归因句无行内标签而 missing_link_note 写明「归因环节为【假设】」(NIT)。对质裁定「尚不能区分/支持竞争解释/尚不能区分」均附置信注记(n=2、单月窗、交叉盘缺席)。
- **竞争解释**: 四环各有竞争解释且同证据可容纳: 程序驱动、美元全局主导、全局冲击主导——非稻草人;MAP_REPORT 逐环渲染「因果假设/竞争解释」两行(均带【假设】)。
- **反对证据**: (1)环4 漏列同窗 11-05→11-11 收盘口径快涨快回落先例(#224、#227);(2)环4 时点论证未检验两条推定读数发布日(#225–#226);(3)环1 对质注记「2.9 低于峰值 3.2」对发布规则敏感(#228)。三项经席位补检均不改变裁定 → 3 MINOR。
- **结论是否超出证据**: 未超出。环2「支持竞争解释」与该行观测一致(EURUSD -2.51%、USDJPY +1.82%、DXY +2.23%,两货币同对美元走弱);环3「尚不能区分」在时点上倾向竞争解释而幅度判据不足,保守可辩。
- **证伪条件可观测性**: 被点名的区分指标 EA_HICP_YOY、EURUSD、VIX 均在注册表与证据索引(#235–#237);两解释在其上的预言方向确实不同(决议前读数抬升/无稳定关系;对美元方向分立/同向随美元;与政策日历联动且回落慢/独立于日历且快回落)。

### L4 情景 S1-DIVERGE-PERSIST / S2-CONVERGE

- **证据相关性**: 敏感变量 EA_HICP_YOY/JP_CPI_YOY 与证伪指标在册(#179);S1 前提(≥3.5/≥2.0/水平差≥1.5)与截止日读数相容(4.0/2.44/1.56,#174–#177),S2 前提(<3.0)未被证伪(#175)。
- **支持度**: 两情景均标「【假设·非预测】」,资产方向标「方向性推演,非幅度预测」;置信档「有相关证据/纯逻辑推理」分记。
- **竞争解释**: 两情景方向互补(S1 维持 vs S2 回落,#180),非孤证。
- **反对证据**: S1 三项触发水平条件在截止日可得读数上已全部成立(#178),触发绑定未发布的 2026-11/2026-12 期读数——形式上未触发,信息量偏低但属延续情景设计使然;S2 证伪只覆盖欧元区分量(MINOR-5)。
- **结论是否超出证据**: 未超出;情景与近一月观察的关系已写明(S2「属并列反例情景」)。
- **证伪条件可观测性**: 期限 2027-02-15 晚于 2026-12 期读数推定入档日(2027-01-16 欧元区/2027-01-20 日本,#173、#182);S1 证伪阈值覆盖三分量(#181),S2 仅覆盖欧元区分量(#184);政策分量「以决议实录核验」中欧央行端在冻结日历无实录(NIT)。

### 历史类比(0 段)与总判断/走位/对质表

- **证据相关性**: 历史类比 0 段如实写明;引擎 analog 执行数字(扫描 1871/有效 74/TOP1 2025-03 距离 0.727)与 S6 步面一致(#211–#215)。
- **支持度**: 一句总判断的每个数字(4.0/2.44/2.1/2.99/2.65/2.5/1.25/0.727→1.227/+50bp/68 天)均回贴一致;四地三时点 anchor_echo 12/12(#10–#22)。
- **竞争解释**: 对质表三行裁定计数 0·1·2 与 quality_gate_notes[1] 一致(#217);每条矛盾陈述并列 2 条竞争解释(#218)。
- **反对证据**: 三转折未说明未采用幅度最大候选的理由(MINOR-7);「先后未定」措辞与月频分辨率相称,「相隔两天」口径不对称(MINOR-2)。
- **结论是否超出证据**: 未超出;「方向同、水平分化、证据面不对称」三项均有对应数字。
- **证伪条件可观测性**: 已渲染的 41 个长文本块与判断档逐字一致(#245);未渲染的三条对质理由与逐月叙述见「范围外观察」。

## 4. 反方攻击记录(每条 L3 陈述与机制链至少一条;共 13 条)

- 反方攻击 1(C1): 「窗内动量不分化」是否依赖起点——改自 2026-06 期起算为欧元区 +1.2 对日本 +0.77、自 2026-05 期为 +0.8 对 +0.91(快慢互换)→ 陈述已明写锚=六个月前锚(2026-04 期: +1.0 对 +1.06,series_store 直算一致),不构成错误;列 NIT 建议加敏感性注。
- 反方攻击 2(C1): 东京都 CPI 佐证是否可靠(该序列 Gate A 列 noncore_missing、仅 10 个月、单一基期文件)→ 判断档已披露缺席状态并只用于同月方向(东京 2.69→2.73 与全国 2.16→2.44 同向上行),未用于同比;攻击不成立。
- 反方攻击 3(C1): 「同比对照方向相反」是否把日本连续回升写成「回落」造成误导→ 判断档分列「同比对照」(较 2025-10 的 2.99 低 0.55)与「窗内动量」(1.38→2.44),两口径均有数字支撑并已标明;攻击不成立。
- 反方攻击 4(C2): 「累计幅度相近」是否以月均市场口径冒充宣布值口径→ 已写明「口径不同仅作量级对照」,宣布值/月均/官方目标分列;攻击不成立。但「相隔两天」取欧央行生效日对日央行决议日,同口径(生效对生效、决议对决议)均为 8 天→ 排序不变,列 MINOR。
- 反方攻击 5(C2): 欧央行决议日为惯例回推,排序是否依赖未证日期→ 「在前/在后」在生效日对生效日(09-16 先于 09-24)与决议日对决议日(回推 09-10 先于实录 09-18)两口径下同向,且判断档明写回推日不参与排序;攻击不成立。
- 反方攻击 6(C3): 五项缺口是否全部属实、有无多报或少报→ ①②经注册表/序列/新鲜度阈(10 天)/Gate A 证实;③漏计三条历史期 EA HICP 两档实录;④全称偏宽(仅两条序列为事后回顾);⑤与总判断把「事实行缺席(采集器已取到而事实未生成)」写成「序列缺席」,序列面实有至 2026-07 期读数(EA 1.28/JP 1.16);①「实录单条」与③「两条」不一(日历实为两条: 目标值决议+维持确认)→ 结论不变,列 2 MINOR + 2 NIT。
- 反方攻击 7(链环1,E1): 窗内月度路径是否前视或错月→ 六个月值逐月回贴 series_store 一致;「窗内 2026-05」期观测日(05-01)在窗前、仅推定发布日在窗内(引擎 n_in_window=5)→ 无数值影响,列 NIT。
- 反方攻击 8(链环2,E1): 「各 25bp」「合计 +50bp」与月均台阶是否可加总→ 四个变更点 (to−from)×100=25/25/25/25;日本四级台阶 11.4+13.7+6.6+18.4=50.1bp(2026-08 为 -0.1bp,未列为台阶),一致;攻击不成立。
- 反方攻击 9(链环3,E2): 「EURJPY 交叉盘不在证据面、不可直接检验」是否放过可做检验——以 EURUSD×USDJPY 直算 175.609(10-23)→175.194(11-20,-0.24%)→174.321(11-23,-0.73%),欧元未相对日元走强→ 与「支持竞争解释」一致;美元端利率未纳入已在注记自陈;攻击不成立,列 NIT 建议补推算值。
- 反方攻击 10(链环4,E2): 「快速回落仅有一个盘中观测」是否漏反向事实——同窗 2026-11-04→11-05 VIX 16.61→28.18(+69.66%),四个交易日内回落至 11-11 的 17.49(-37.93%),SPX 11-05 -4.36%、NIKKEI225 11-05/11-06 -1.79%/-5.96%→ 存在一条未披露的收盘口径「快涨快回落」先例,支持竞争解释的预期;裁定「尚不能区分」本已保守,方向不变,列 MINOR。
- 反方攻击 11(链环4,E2): 「VIX 跳升不与政策日历对齐」是否漏检读数发布日——两个最大单日跳升日恰为推定通胀发布日(11-16 欧元区 4.0: VIX +18.70%;11-20 日本 2.44: +26.20%);跨地区复核: 跳升窗 11-13→11-20 四地股指 SPX -8.61%、NIKKEI225 -7.70%、DAX -7.28%、CAC40 -5.27%(均不深于美股),两日 EURUSD/USDJPY 变动不超过 0.23%→ 未出现地区特异性读数冲击证据,结论不变,列 MINOR(补注)。
- 反方攻击 12(链环1 对质,读数驱动 vs 程序驱动): 「2.9 低于 2026-05 峰值 3.2」的反向观察是否依赖发布规则——若按日历三条 EA HICP 实录的「次月 1 日快报+月中终值」两档形态,两次决议日前可见读数为 2026-05=3.2、2026-08=3.2,该条反向观察不成立;另一条(2025-06-11→2026-06-17 共 371 天维持 2.15/2.0 而读数由 1.7 升至 3.0)仍在,n=2→ 裁定「尚不能区分」不变,列 MINOR(披露敏感性)。
- 反方攻击 13(情景 S1/S2): 截止日是否已触发/已证伪、证伪指标是否可观测——S1 三项水平条件(≥4.0/水平差≥1.5/VIX 收盘>30)在截止日可得读数上已全部成立(4.0/1.56/35.89),但触发绑定尚未发布的 2026-11/2026-12 期读数,形式上未触发(延续情景信息量偏低,设计使然);S2 前提(欧元区<3.0)未被证伪;证伪指标 EA_HICP_YOY/JP_CPI_YOY 在册,2026-12 期推定入档 2027-01-16/2027-01-20 早于期限 2027-02-15;S2 证伪只覆盖欧元区分量→ 不构成「不可观测」,列 MINOR。

## 5. 问题清单(MAJOR 0 / MINOR 7 / NIT 10)

### MAJOR(无)

未发现数字/日期/方向错误、缺基期给同比、相邻口径冒充、事后信息冒充当时可知、未标注的超证据结论或不可观测的证伪条件。

### MINOR(7)

1. **MINOR-1** 位置: agent_judgment.json l3.contradictions[2].statement(C3⑤);reader_map.headline_conclusion
   - 问题: 「增长与核心通胀背景序列缺席(GDP 两序列在册但快照缺席)」把「事实行缺席」写成「序列缺席」: 冻结快照 gate_a.noncore_missing 含 EA_REAL_GDP_YOY/JP_REAL_GDP_YOY,detail=「来源文件在场且子源FRED_EA_GDP/FRED_JP_GDP取数成功而指标缺席(采集遗漏——采集器已取到而事实未生成)」,而 series_store 两序列均有至 2026-07-01 期读数(EA 1.28,n=123;JP 1.16,n=127)。与同为 noncore_missing 却取序列面值并披露的东京 CPI 处理不一致;按 Gate A「缺失数据不得进入研究结论」不取用本身合规,结论不变。
   - 原句: 「⑤增长与核心通胀背景缺席: EA_REAL_GDP_YOY、JP_REAL_GDP_YOY 在册但列于快照缺席名单,两地「政策环境」无法对照增长背景;注册表亦无两地核心通胀序列。」
   - 改句: 「⑤增长与核心通胀背景对照缺席: EA_REAL_GDP_YOY、JP_REAL_GDP_YOY 在册,但当日快照 Gate A 列于缺席名单(事实行缺席,注记=采集器已取到而事实未生成;序列面存有至 2026-07 期读数 EA 1.28%/JP 1.16%,按 Gate A 不取用),两地「政策环境」无法对照增长背景;注册表亦无两地核心通胀序列。」
2. **MINOR-2** 位置: agent_judgment.json l3.contradictions[1].statement(C2 节奏对照)
   - 问题: 「相隔两天」=欧央行生效日 2026-09-16 对日央行决议日 2026-09-18,两端口径不对称;同口径距离为生效日对生效日(09-16→09-24)8 天、决议日对决议日(回推 09-10→实录 09-18)8 天。「在前/在后」排序不受影响。
   - 原句: 「欧央行第二次变更 2026-09-16 生效在前、日央行 2026-09-18 决议即 2026-09-24 生效在后,相隔两天,日级日期可排」
   - 改句: 「欧央行第二次变更 2026-09-16 生效在前、日央行 2026-09-18 决议(2026-09-24 生效)在后,同口径相隔八天(生效日对生效日;决议日对决议日亦八天),日级日期可排」
3. **MINOR-3** 位置: agent_judgment.json reader_map.transmission[0].links[2].verdict_note;l3.mechanism_chains[0].links[3].text
   - 问题: 称竞争解释的「快速回落」预期「仅有一个盘中观测」,漏列同窗收盘口径先例: VIX 2026-11-04 收盘 16.61→11-05 28.18(+69.66%),四个交易日内回到 11-11 的 17.49(较 11-05 -37.93%);同期 SPX 11-05 -4.36%、NIKKEI225 11-05/11-06 -1.79%/-5.96%(series_store[VIX/SPX/NIKKEI225] 日频收盘)。该未披露事实支持竞争解释的预期;裁定「尚不能区分」本已偏保守,方向不变。
   - 原句: 「但其『快速回落』预期仅有一个盘中观测(2026-11-23 快照 27.01,较 2026-11-20 收盘 -24.7%,非收盘)」
   - 改句: 「但其『快速回落』预期在本跳升上仅有一个盘中观测(2026-11-23 快照 27.01,较 2026-11-20 收盘 -24.7%,非收盘);同窗另有一次收盘口径先例: 2026-11-04→11-05 VIX 16.61→28.18(+69.7%),至 11-11 回落至 17.49(四个交易日,较 11-05 -37.9%),同期 SPX 11-05 -4.36%、NIKKEI225 11-05/11-06 -1.79%/-5.96%——与「冲击主导、快速回落」相容」
4. **MINOR-4** 位置: agent_judgment.json l3.contradictions[2].statement(C3③);牵动 reader_map.transmission[0].links[0].verdict_note 的敏感性披露
   - 问题: 冻结日历除日本政策目标两条外另有三条 EA_HICP_YOY 实录(RC-EA-HICP-2021M05/2022M06/2025M03),呈「次月 1 日快报+月中终值」两档;均不覆盖本窗月份。按该两档形态,两次欧央行变更决议日前可见读数应为 2026-05=3.2、2026-08=3.2,环1 注记「2.9 低于 2026-05 峰值 3.2」这一条反向观察不成立(另一条 371 天反向观察仍在,n=2),裁定不变。
   - 原句: 「日历实录仅覆盖日本政策目标两条」
   - 改句: 「本窗月度通胀读数无日历实录(日历仅有日本政策目标两条与三条历史期 EA HICP 快报/终值实录 2021M05、2022M06、2025M03);若按该两档形态(次月 1 日快报)计,两次欧央行变更决议日前可见读数为 2026-05=3.2、2026-08=3.2,环1「2.9 低于峰值」一象不成立,裁定不变」
5. **MINOR-5** 位置: agent_judgment.json l4.scenarios[1].rows.falsification.threshold 与 trigger.condition(S2-CONVERGE)
   - 问题: S2 情景含欧元区<3.0%、日本<2.0%、水平差≤1.0 个百分点三分量,证伪阈值只覆盖欧元区分量(两月均不低于 3.5%),日本端与水平差分量无对应证伪,触发条件亦缺水平差分量;S1 三分量齐全,两情景不对称。
   - 原句: 「若观测月 2026-11 与 2026-12 两月 EA_HICP_YOY 同比均不低于 3.5%(未回落),「以一次性因素为主、回落至 3.0% 以下」的前提被证伪;政策分量(按兵不动)不设数值触发,以决议实录核验」
   - 改句: 「若观测月 2026-11 与 2026-12 两月 EA_HICP_YOY 同比均不低于 3.5%(未回落),「以一次性因素为主、回落至 3.0% 以下」的前提被证伪;或两月日本全国 CPI 同比均不低于 2.0%,或两月两地水平差(欧元区减日本)均不低于 1.0 个百分点,收敛情景的日本端/水平差分量被证伪;政策分量(按兵不动)不设数值触发,以决议实录核验(触发条件同步补「且两地水平差不超过 1.0 个百分点」)」
6. **MINOR-6** 位置: agent_judgment.json reader_map.transmission[0].links[2].verdict_note((b) 时点论证);l3.mechanism_chains[0].links[3].text
   - 问题: 时点论证只量到政策决议日(2026-10-30、2026-09-16),未检验链条首环的读数发布日: 引擎推定发布日 2026-11-16(欧元区 4.0)与 2026-11-20(日本 2.44)均落在跳升窗内,且为窗内两个最大单日跳升日(VIX +18.70%/+26.20%)。席位跨地区复核(series_store 日频收盘): 跳升窗 11-13→11-20 SPX -8.61%、NIKKEI225 -7.70%、DAX -7.28%、CAC40 -5.27%(均不深于美股),两日 EURUSD/USDJPY 变动幅度不超过 0.23%——未出现地区特异性读数冲击证据,「尚不能区分」不变,但应补注。
   - 原句: 「(b)『VIX 与政策日历联动』在时点上不成立: VIX 跳升集中于 2026-11-13→2026-11-20(19.30→35.89),距最近政策日 2026-10-30(BOJ 维持决议,无变更)14 天、距 ECB 最近生效日 2026-09-16 58 天。」
   - 改句: 「(b)『VIX 与政策日历联动』在时点上不成立: VIX 跳升集中于 2026-11-13→2026-11-20(19.30→35.89),距最近政策日 2026-10-30(BOJ 维持决议,无变更)14 天、距 ECB 最近生效日 2026-09-16 58 天;跳升窗内含两条推定读数发布日(2026-11-16 欧元区 4.0、2026-11-20 日本 2.44,当日 VIX +18.7%/+26.2%),但窗内四地股指跌幅均不深于美股(SPX -8.61%、NIKKEI225 -7.70%、DAX -7.28%、CAC40 -5.27%),两日欧元、日元汇率变动幅度不超过 0.23%,读数发布主因未获跨地区支持。」
7. **MINOR-7** 位置: agent_judgment.json reader_map.turnings(三转折);MAP_REPORT「过去一年的三个转折」及其候选面折叠表
   - 问题: 引擎候选面(report.json research_plan.turning_candidates)4 条,三转折采用其中 3 条,未说明为何不采用幅度最大的日本全国 CPI 2025-11→2026-02(2.9→1.27,Δ-1.63)候选(其变动主要发生在六个月窗之前,谷底 2026-02 的 1.27 已在 turnings[0] 写明);读者报告并排展示候选表,宜补一句取舍理由。
   - 原句: 「(缺句——候选面首行为: JP | inflation | JP_CPI_YOY | 2025-11..2026-02 | 2.9→1.27 | -1.63,三转折节无对应说明)」
   - 改句: 「于三转折节补注: 引擎候选面另列日本全国 CPI 2025-11→2026-02(2.9→1.27,Δ-1.63)为幅度最大候选,因该回落主要发生在六个月窗(起 2026-05-23)之前、且谷底已在两地走位中写明,不列入三转折。」

### NIT(10)

1. **NIT-1** 位置: agent_judgment.json l3.mechanism_chains[0].links[3].text(环4,E2)
   - 问题: 环4 归因句无行内【假设】标注(环3 有「传导【假设】」);标注只在 missing_link_note 与对质表因果/竞争解释行。
   - 原句: 「VIX 跳升时点(2026-11-13→2026-11-20)不与政策日历对齐、欧元区股指不弱于美股,两点不利于紧缩主因,单一归因于两地政策不可证。」
   - 改句: 「该组合与「紧缩+通胀粘性压制估值」与「全局风险/流动性冲击」两种叙事均相容【假设·归因】;VIX 跳升时点…不与政策日历对齐、欧元区股指不弱于美股,两点不利于紧缩主因,单一归因于两地政策不可证。」
2. **NIT-2** 位置: agent_judgment.json l3.contradictions[2].statement(C3④);quality_gate_notes[4] 末句
   - 问题: 「月度数值为事后回顾口径」全称偏宽: 引擎点值格(research_plan.point_values.cells)仅 EA_HICP_YOY、JP_CPI_YOY 标「事后回顾(最新修订值,非当时首发值)」,东京 CPI 与 JP_POLICY_RATE 标「as_collected(采集时点值)」。
   - 原句: 「④月度数值为事后回顾口径(最新修订值,非当时首发值),当时信息集不可重构。」
   - 改句: 「④欧元区 HICP 与日本全国 CPI 月度数值为事后回顾口径(最新修订值,非当时首发值),东京 CPI 与月均拆借利率为采集时点值(是否首发值未核),当时信息集不可重构。」
3. **NIT-3** 位置: agent_judgment.json reader_map.regions[1].from_to(日本走位)
   - 问题: 「持续回落」非单调: series_store[JP_CPI_YOY] 2025-01 4.03→2025-08 2.72 后 2025-09 2.91、2025-10 2.99 两月回升,再降至 2026-02 的 1.27。
   - 原句: 「自 2025-01 高点 4.03 持续回落至 2026-02 的 1.27,此后总体回升。」
   - 改句: 「自 2025-01 高点 4.03 总体回落(2025-09、2025-10 两月小幅回升至 2.91、2.99)至 2026-02 的 1.27,此后总体回升。」
4. **NIT-4** 位置: agent_judgment.json l3.mechanism_chains[0].links[0].text(环1)
   - 问题: 「窗内(2026-05..2026-10 月度值)」含 2026-05 期(观测日 05-01 早于窗起 2026-05-23,仅推定发布日在窗内);引擎点值格 n_in_window=5。
   - 原句: 「窗内(2026-05..2026-10 月度值)」
   - 改句: 「窗内及其锚后月度值(2026-05..2026-10;2026-05 期观测日在窗前、推定发布日在窗内)」
5. **NIT-5** 位置: agent_judgment.json turnings[2].follow_or_diverge、C1、C3③(东京 CPI 推定发布日)
   - 问题: 引擎东京 CPI 推定规则「月末−1天」给出 2026-08-30(周日)与 2026-06-29,而引擎规则串自列官方实录锚为 2026-06-26、2026-10-30(均为当月最后一个周五);按「最后一个周五」计(8 月 08-28、9 月 09-25),决议前可见的最近东京读数仍为 2026-08 期、2026-09 期仍晚于 09-18 决议,结论不变。
   - 原句: 「决议前可见的最近东京读数为 2026-08 的 1.9(推定发布 2026-08-30)。」
   - 改句: 「决议前可见的最近东京读数为 2026-08 的 1.9(推定发布 2026-08-30;该推定规则与引擎自列官方实录锚 2026-06-26、2026-10-30 不完全一致,可见性结论不受影响)。」
6. **NIT-6** 位置: agent_judgment.json l4.scenarios[*].rows(政策分量);quality_gate_notes[3]
   - 问题: 「以决议实录核验」: 冻结日历对欧央行零条实录,欧央行分量在引擎面暂不可核验,须待日历补录;日本端有两条实录可核。
   - 原句: 「政策分量(再上调)不设数值触发,以决议实录核验」
   - 改句: 「政策分量(再上调)不设数值触发,以决议实录核验(欧央行分量须待发布日历补录 ECB 实录后方可核验)」
7. **NIT-7** 位置: agent_judgment.json l3.contradictions[0].statement(C1「窗内动量不分化」)
   - 问题: 「动量相近」依赖起点取六个月前锚(2026-04 期: 欧元区 +1.0 对日本 +1.06);自 2026-06 起算为 +1.2 对 +0.77、自 2026-05 为 +0.8 对 +0.91,快慢互换。陈述已限定锚点,建议加敏感性注。
   - 原句: 「均约一个百分点——「水平与同比方向分化、窗内动量不分化」。」
   - 改句: 「均约一个百分点(起点=六个月前锚;自 2026-06 期起算则为欧元区 +1.2 对日本 +0.77)——「水平与同比方向分化、窗内动量不分化」。」
8. **NIT-8** 位置: agent_judgment.json l3.mechanism_chains[0].links[2].text;transmission[0].links[1].observed_fact
   - 问题: 交叉盘可由证据面两条序列相乘推出: EURUSD×USDJPY=175.609(10-23)→175.194(11-20,-0.24%)→174.321(11-23,-0.73%),欧元未相对日元走强,与「支持竞争解释」一致;可补推算值。
   - 原句: 「EURJPY 交叉盘不在证据面,利差渠道不可直接检验」
   - 改句: 「EURJPY 交叉盘不在证据面(以 EURUSD×USDJPY 推算: 175.61→175.19(至 11-20 收盘,-0.24%),欧元未相对日元走强),利差渠道仅可间接检验」
9. **NIT-9** 位置: agent_judgment.json l3.contradictions[1].statement(C2 水平对照)与环3/transmission[0].links[1]
   - 问题: 水平差两处所用欧央行利率不同: C2 用 DFR(2.5−1.25=1.25 个百分点),环3/环2 用 MRO(2.65−1.25=1.40 个百分点);均已写明利率名,方向一致,宜统一或并列。
   - 原句: 「最新政策利率欧元区高于日本约一点二五个百分点(DFR 二点五 vs BOJ 目标约一点二五)。」
   - 改句: 「最新政策利率欧元区高于日本: 按 MRO 计约一点四零、按 DFR 计约一点二五个百分点(2.65/2.5 vs BOJ 目标约一点二五)。」
10. **NIT-10** 位置: agent_judgment.json l3.contradictions[2].statement(C3①,与同一陈述③互指)
   - 问题: C3① 写「发布日历实录单条(user_directive 基础)」,而同一陈述③写「日本政策目标两条」;冻结日历 JP_POLICY_TARGET 实为两条(均为 user_directive): RC-JP-BOJ-TARGET-2026-09(决议 2026-09-18/生效 2026-09-24/目标 1.25)与 RC-JP-BOJ-MAINT-2026-10(2026-10-30 确认维持 1.25)。目标值条目确为一条,但「单条」与「两条」并置易生歧义。
   - 原句: 「对照以月均市场口径替代+发布日历实录单条(user_directive 基础)。」
   - 改句: 「对照以月均市场口径替代+发布日历实录两条(目标值决议一条、维持确认一条,均 user_directive 基础)。」

## 6. 范围外观察(引擎渲染/交付面;不计入裁决,供操作席参考)

- MAP_REPORT.md 第 5 行「研究时点口径: …按月末时点化为研究截止日 2026-11-30…本报告全部窗口/锚点/政策面绑定该时点(数据=当时已发布面,后来发布的数据不回填)」与第 4/6 行(研究截止日=2026-11-23)相抵,且与本运行实际口径(report.json run.evidence_gate.publication_basis=snapshot_presence、点值格标「事后回顾」)不符——引擎模板文字;判断档自身的截止日披露(总判断首句、quality_gate_notes[4])一致无误。
- MAP_REPORT.md 第 8 行「三个对照时点=日历点锚(截止日−12月/−3月/最新一期)」与本问实际锚(6个月前/最新一期,见「四地三时点环境对照」表)不符——判断档 quality_gate_notes[5]① 已登记该硬编码标签缺口。
- 判断档三条 transmission[*].verdict_note(对质理由,如「共 371 天…未触发变更」)与三条 turnings[*].narrative(逐月叙述)、六条 quality_gate_notes 均未渲染进 MAP_REPORT.md/FULL_REPORT.md/report.md;已渲染的 41 个长文本块与判断档逐字一致(复算表 #245)。读者面只见裁定词、不见对质理由。
- MAP_REPORT.md「政策一年窗路径」对欧央行两序列写「净变动 +25bp(2.25→2.5)」,而同句列出窗内两个 +25bp 变更点(2026-06-17、2026-09-16): 引擎 net_bp 取「窗首尾观测差」,窗内首个观测即为 06-17 变更后的 2.25,致读者面净变动与窗内事件合计(+50bp)不闭合;判断档未引用该数,用的是六个月锚间 +50bp(复算表 #38)。

## 7. 席位补检用上下文数字(extra_ctx.txt 原文;只读直算,不计入复算点)

```
== cross-region index returns inside the VIX jump window (close 2026-11-13 -> close 2026-11-20) ==
SPX: 7561.67 -> 6910.39 = -8.61%
DAX: 26749.95 -> 24802.78 = -7.28%
CAC40: 8368.91 -> 7927.75 = -5.27%
NIKKEI225: 61142.35 -> 56436.65 = -7.70%
== month window (2026-10-23 -> 2026-11-20) ==
SPX: 7623.68 -> 6910.39 = -9.36%
DAX: 25181.65 -> 24802.78 = -1.50%
CAC40: 7782.82 -> 7927.75 = +1.86%
NIKKEI225: 62693.16 -> 56436.65 = -9.98%
== presumed inflation release days vs same-day closes (non-synchronous: Tokyo < Europe < New York) ==
SPX | 11-16 vs 11-13 -1.92% ; 11-17 vs 11-16 -1.03% ; 11-19 vs 11-18 -2.02% ; 11-20 vs 11-19 -3.70%
DAX | 11-16 vs 11-13 -0.57% ; 11-17 vs 11-16 -2.08% ; 11-19 vs 11-18 -1.06% ; 11-20 vs 11-19 -2.60%
CAC40 | 11-16 vs 11-13 -0.20% ; 11-17 vs 11-16 -1.62% ; 11-19 vs 11-18 -0.81% ; 11-20 vs 11-19 -1.89%
NIKKEI225 | 11-16 vs 11-13 -2.42% ; 11-17 vs 11-16 -1.34% ; 11-19 vs 11-18 +0.71% ; 11-20 vs 11-19 -5.06%
EURUSD | 11-16 vs 11-13 -0.23% ; 11-17 vs 11-16 -0.24% ; 11-19 vs 11-18 -0.19% ; 11-20 vs 11-19 -0.02%
USDJPY | 11-16 vs 11-13 -0.06% ; 11-17 vs 11-16 -0.16% ; 11-19 vs 11-18 -0.08% ; 11-20 vs 11-19 +0.20%
VIX | 11-16 vs 11-13 +18.70% ; 11-17 vs 11-16 +11.13% ; 11-19 vs 11-18 +15.80% ; 11-20 vs 11-19 +26.20%
== earlier in-window spike episode (closes) ==
VIX 11-04 16.61 ; 11-05 28.18 ; 11-06 25.64 ; 11-09 19.92 ; 11-10 19.46 ; 11-11 17.49
SPX 11-04 7688.62 ; 11-05 7353.73 ; 11-06 7376.86 ; 11-09 7549.94 ; 11-10 7520.93 ; 11-11 7619.38
NIKKEI225 11-04 62188.63 ; 11-05 61077.90 ; 11-06 57434.77 ; 11-09 58775.50 ; 11-10 60459.58 ; 11-11 61248.59
VIX 2026-11-04 -> 11-05: +69.66% ; 11-05 -> 11-11: -37.93%
== implied EURJPY = EURUSD x USDJPY ==
2026-10-23 EURUSD 1.122146 x USDJPY 156.494 = 175.609
2026-11-20 EURUSD 1.096972 x USDJPY 159.707 = 175.194
2026-11-23 EURUSD 1.093972 x USDJPY 159.347 = 174.321
10-23 -> 11-20: -0.24% ; 10-23 -> 11-23: -0.73%
== JP_CPI_YOY path 2025-01..2026-02 (for 「持续回落」 wording) ==
2025-01 4.03 ; 2025-02 3.66 ; 2025-03 3.62 ; 2025-04 3.56 ; 2025-05 3.49 ; 2025-06 3.27 ; 2025-07 3.10 ; 2025-08 2.72 ; 2025-09 2.91 ; 2025-10 2.99 ; 2025-11 2.90 ; 2025-12 2.13 ; 2026-01 1.51
== JP_POLICY_RATE 2026-04..2026-10 and steps (bp) ==
2026-04 0.727 ; 2026-05 0.727 ; 2026-06 0.841 ; 2026-07 0.978 ; 2026-08 0.977 ; 2026-09 1.043
steps bp: ['2026-05 +0.0', '2026-06 +11.4', '2026-07 +13.7', '2026-08 -0.1', '2026-09 +6.6'] sum +31.6
== EA/JP momentum from alternative start months to 2026-10 (pp) ==
2026-04 EA +1.00 (from 3.00) JP +1.06 (from 1.38)
2026-05 EA +0.80 (from 3.20) JP +0.91 (from 1.53)
2026-06 EA +1.20 (from 2.80) JP +0.77 (from 1.67)
2026-07 EA +1.10 (from 2.90) JP +0.47 (from 1.97)
2026-08 EA +0.80 (from 3.20) JP +0.46 (from 1.98)
== snapshot top-level keys == ['snapshot_id', 'research_as_of', 'target_date', 'timezone', 'sources_status', 'fed_futures_curve', 'facts', 'reconciliation', 'quality', 'gate_a', 'notes', 'series_store', 'series_store_notes', 'series_provenance', 'series_store_clean']
gate_a keys: ['status', 'core_missing', 'core_fail', 'noncore_fail', 'noncore_missing', 'note', 'noncore_missing_detail', 'noncore_degraded', 'illegal_quality']
gate_a noncore_missing_detail: {"JP_CPI_TOKYO_YOY": "来源文件在场而指标缺席(采集遗漏或子源缺席——档内无该指标子源状态记录,不可区分)", "BUND_10Y": "子源缺席(ea档记录:BBK_WU3146=READ_FAIL——源端不可得/未采,非采集遗漏)", "BUND_2Y": "子源缺席(ea档记录:BBK_WU3141=READ_FAIL——源端不可得/未采,非采集遗漏)", "CN_OMO_7D": "来源文件在场而指标缺席(采集遗漏或子源缺席——注册表未登记该指标子源状态键,不可区分)", "CN_POLICY_OVERNIGHT": "来源文件在场而指标缺席(采集遗漏或子源缺席——注册表未登记该指标子源状态键,不可区分)", "EA_REAL_GDP_YOY": "来源文件在场且子源FRED_EA_GDP取数成功而指标缺席(采集遗漏——采集器已取到而事实未生成)", "JP_REAL_GDP_YOY": "来源文件在场且子源FRED_JP_GDP取数成功而指标缺席(采集遗漏——采集器已取到而事实未生成)"}
gate_a degraded/noncore lists: {"status": "DEGRADED", "core_missing": [], "core_fail": [], "noncore_fail": [], "noncore_missing": ["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"], "note": "缺失/失败数据已披露,不得进入研究结论;单个资产缺失不阻断其余研究;非核心FAIL按降级披露(注册表criticality为权威)", "noncore_degraded": ["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"], "illegal_quality": []}
```

## 8. 席位脚本与中间表(同目录,供复核)

- recompute_n30.py → recompute_table.md、recompute_summary.json(复算主体)
- extract_*.py → *_dump.txt(只读面转储: engine_face / l1_contract / snapshot / calendar_registry / l3_l4 / steps / misc / regions)
- peek_daily.py、peek_jppath.py、peek_daily_window.py、extra_ctx.py → daily_tails.txt、daily_window_nov.txt、extra_ctx.txt(日频与上下文补检)
- build_outputs.py → 本文件与 VERDICT-round1.json
