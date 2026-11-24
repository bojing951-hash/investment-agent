# Audit-R32 正式使用验收 · B · Round-1 · 独立语义审查记录

- 席位: semantic-audit-seat(零上下文;reviewer=independent-zero-context-seat-r32-b-round1);裁决日 2026-11-24。
- **裁决: REVISE** — MAJOR 1 条 / MINOR 6 条 / NIT 10 条。
- 复算规模: 独立复算 **302 点 / 偏离 0**(另有 14 项结构性自检全部一致,不计入;中间表共 316 行)。
- 受审对象: 受审运行目录下 agent_judgment.json 全文(l3 / l4 / reader_map / quality_gate_notes / agent_declaration)与读者报告 MAP_REPORT.md / FULL_REPORT.md 中的判断文字。
- 只读面: 冻结快照 research_snapshot_20261123.json(series_store 92 条序列;research_as_of 2026-11-23T22:53:47+08:00)、冻结日历 release_calendar.json v1.5.0(18 条)、metric_registry.json、report.json 引擎面、evidence_index.json(63 条);代码印章 19638e1487e1e5729b9645ce621c3435d0635d08。
- 方法: 自写脚本 s10_recompute.py(/usr/bin/python3 -I,路径作参数传入)按注册表发布节奏与日历条目优先规则重建锚点、同比、发布日,从 series_store 直算三利率分解与资产月窗,再与判断档字面/锚格回显/引擎面比对;原句一律按路径取自受审判断档并断言在场。未联网、未运行任何写操作、未委派子代理;未读取规程 §2 所列任何目录。
- 脚本与中间表(同目录,供操作席复核): s00–s09b/s11/s12(只读结构探查与引擎面抽取)、s10_recompute.py(主复算)、s13_jstruct.py/s14_render_check.py/s15_calendar.py/s16_run_keys.py(结构与渲染核对)、s18_policy_series.py(政策利率序列攻击探针)、s17_write_outputs.py(本件装配);work/recompute_points.json(逐点)、work/recompute_probes.json(探针)、work/policy_series_probe.json(攻击探针)、work/render_check.json、work/face_*.json 与 work/env_*.json(引擎面抽取)。

## 一、复算清单(逐点)

出处键图例: `series_store.*` / `snapshot.*` = research_snapshot_20261123.json(series_store 指该文件顶层 series_store);`calendar …` / `release_calendar.json …` = root_overlay/config/release_calendar.json;`metric_registry …` = root_overlay/config/metric_registry.json;`report.json …` / `research_plan.*` / `contract_verification.*` / `run.*` = report.json;`agent_judgment.json …` / `l3.*` / `l4.*` / `reader_map.*` = agent_judgment.json;「字面」=受审判断档或读者报告中的原字面;「锚格回显/引擎格」=reader_map.regions[*].anchor_echo 的值或引擎点值格。

分项: 截止日 12、锚格 85、同比 28、政策面 21、三利率 28、资产月窗 27、转折候选 40、机制链 19、情景相容 9、缺席披露 8、契约STALE 14、证据引用 11。

⑧历史类比: 判断档 history_periods 为空(零段呈现,history_zero_case_note 已说明),不适用;⑫截止日当日日频观测的时点说明并入 ①/⑤ 核对;⑩ 见第三节,⑭ 见第二节末。


**①截止日** — 独立复算 12 点(偏离 0)

| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |
|---|---|---|---|---|---|---|
| P001 | 研究截止时间戳 research_as_of | snapshot.research_as_of | 2026-11-23T22:53:47+08:00 | 2026-11-23T22:53:47+08:00；字面「2026-11-23T22:53:47+08:00」 | 等值比较 | 一致 |
| P002 | 快照 target_date(=研究截止日) | snapshot.target_date | 2026-11-23 | 2026-11-23；字面「研究截止日=快照版本日 2026-11-23」 | 等值比较 | 一致 |
| P003 | 引擎 cutoff | report.json research_plan.cutoff | 2026-11-23 | 2026-11-23 | 等值比较 | 一致(结构性自检,不计入) |
| P004 | 引擎 evidence_asof | report.json run.evidence_asof | 2026-11-23 | 2026-11-23 | 等值比较 | 一致(结构性自检,不计入) |
| P005 | 引擎 ts_utc(运行号) | report.json run.ts_utc | 20261123T145819Z | 20261123T145819Z | 等值比较 | 一致(结构性自检,不计入) |
| P006 | 代码印章 run.git_head | report.json run.git_head | 19638e1487e1e5729b9645ce621c3435d0635d08 | 19638e1487e1e5729b9645ce621c3435d0635d08 | 等值比较 | 一致(结构性自检,不计入) |
| P007 | 安装树 CODE_VERSION.git_head | CODE_VERSION.json git_head | 19638e1487e1e5729b9645ce621c3435d0635d08 | 19638e1487e1e5729b9645ce621c3435d0635d08 | 等值比较 | 一致(结构性自检,不计入) |
| P008 | 截止时点当地时间·纽约 | snapshot.research_as_of → zoneinfo America/New_York | 09:53 | 09:53；字面「纽约 09:53」 | 等值比较 | 一致 |
| P009 | 截止时点当地时间·法兰克福 | snapshot.research_as_of → zoneinfo Europe/Berlin | 15:53 | 15:53；字面「法兰克福 15:53」 | 等值比较 | 一致 |
| P010 | 截止时点当地时间·东京 | snapshot.research_as_of → zoneinfo Asia/Tokyo | 23:53 | 23:53；字面「东京 23:53」 | 等值比较 | 一致 |
| P011 | 截止时点当地时间·上海 | snapshot.research_as_of → zoneinfo Asia/Shanghai | 22:53 | 22:53；字面「上海 22:53」 | 等值比较 | 一致 |
| P012 | 判断档全文中晚于截止日的日期集合(只允许情景期限) | agent_judgment.json 全文正则 | 2027-02-15 | 2027-02-15 | 等值比较 | 一致 |
| P013 | 判断档引用的最大观测日 | agent_judgment.json 全文正则 | 2026-11-23 | 2026-11-23 | 等值比较 | 一致 |
| P014 | FOMC 纪要文档事实发布日 | report.json research_plan.policy_doc_facts[0].published_on | 2026-11-18 | 2026-11-18；字面「2026-11-18 发布」 | 等值比较 | 一致 |
| P015 | FOMC 纪要文档事实 doc_id | research_plan.policy_doc_facts[0].doc_id | FOMC-MINUTES-2026-10 | FOMC-MINUTES-2026-10；字面「FOMC-MINUTES-2026-10」 | 等值比较 | 一致 |
| P016 | 纪要发布日≤截止日 | policy_doc_facts[0].published_on vs cutoff | True | True | 精确 | 一致 |
| P017 | 政策事件簇为空 | research_plan.policy_event_clusters.clusters | 0 | 0；字面「政策事件簇为空」 | 四舍五入一致(差 0) | 一致 |


**②锚格** — 独立复算 85 点(偏离 0)

| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |
|---|---|---|---|---|---|---|
| P041 | 锚「3个月前」as_of | research_plan.point_anchors | 2026-08-23 | 2026-08-23 | 等值比较 | 一致(结构性自检,不计入) |
| P042 | 锚「最新一期」as_of | research_plan.point_anchors | 2026-11-23 | 2026-11-23 | 等值比较 | 一致(结构性自检,不计入) |
| P043 | 锚点数=2(无 12 个月前锚) | research_plan.point_anchors | 2 | 2 | 四舍五入一致(差 0) | 一致(结构性自检,不计入) |
| P044 | 点值格数 | research_plan.point_values.cells | 9 | 9；字面「点值格(9格)」 | 四舍五入一致(差 0) | 一致 |
| P045 | US_REAL_GDP·3个月前·观测日 | series_store.US_REAL_GDP + 发布纪律(锚 2026-08-23) | 2026-04-01 | 2026-04-01；锚格回显/引擎格=2026-04-01；注: 判断档 anchor_echo.observation_month=2026-04 | 等值比较 | 一致 |
| P046 | US_REAL_GDP·3个月前·值 | series_store.US_REAL_GDP[2026-04-01] | 24408 | 24408；字面「GDP 水平 24408.011→24611.077」；锚格回显/引擎格=24408 | 四舍五入一致(差 0) | 一致 |
| P047 | US_REAL_GDP·3个月前·发布日(规则 29) | period_end+rule, 日历条目优先 | 2026-07-29 | 2026-07-29 | 等值比较 | 一致 |
| P048 | US_REAL_GDP·3个月前·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P049 | US_REAL_GDP·3个月前·同比 | series_store.US_REAL_GDP 同比(基期 2025-04-01) | 2.19157 | 2.19；注: 同比数字在判断档正文中的字面比对见 ③同比 | 四舍五入一致(差 0.00157) | 一致 |
| P050 | US_REAL_GDP·最新一期·观测日 | series_store.US_REAL_GDP + 发布纪律(锚 2026-11-23) | 2026-07-01 | 2026-07-01；锚格回显/引擎格=2026-07-01；注: 判断档 anchor_echo.observation_month=2026-07 | 等值比较 | 一致 |
| P051 | US_REAL_GDP·最新一期·值 | series_store.US_REAL_GDP[2026-07-01] | 24611.1 | 24611.1；字面「最新报 24611.077(观测 2026-07 季)」；锚格回显/引擎格=24611.1 | 四舍五入一致(差 0) | 一致 |
| P052 | US_REAL_GDP·最新一期·发布日(规则 29) | period_end+rule, 日历条目优先 | 2026-10-29 | 2026-10-29 | 等值比较 | 一致 |
| P053 | US_REAL_GDP·最新一期·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P054 | US_REAL_GDP·最新一期·同比 | series_store.US_REAL_GDP 同比(基期 2025-07-01) | 2.06574 | 2.07；注: 同比数字在判断档正文中的字面比对见 ③同比 | 四舍五入一致(差 0.00426) | 一致 |
| P055 | UNEMPLOYMENT·3个月前·观测日 | series_store.UNEMPLOYMENT + 发布纪律(锚 2026-08-23) | 2026-07-01 | 2026-07-01；锚格回显/引擎格=2026-07-01；注: 判断档 anchor_echo.observation_month=2026-07 | 等值比较 | 一致 |
| P056 | UNEMPLOYMENT·3个月前·值 | series_store.UNEMPLOYMENT[2026-07-01] | 4.1 | 4.1；字面「其 3 个月前锚前值为 4.1(观测 2026-07)」；锚格回显/引擎格=4.1 | 四舍五入一致(差 0) | 一致 |
| P057 | UNEMPLOYMENT·3个月前·发布日(规则 5) | period_end+rule, 日历条目优先 | 2026-08-05 | 2026-08-05 | 等值比较 | 一致 |
| P058 | UNEMPLOYMENT·3个月前·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P059 | UNEMPLOYMENT·最新一期·观测日 | series_store.UNEMPLOYMENT + 发布纪律(锚 2026-11-23) | 2026-10-01 | 2026-10-01；锚格回显/引擎格=2026-10-01；注: 判断档 anchor_echo.observation_month=2026-10 | 等值比较 | 一致 |
| P060 | UNEMPLOYMENT·最新一期·值 | series_store.UNEMPLOYMENT[2026-10-01] | 4.1 | 4.1；字面「UNEMPLOYMENT 最新报 4.1(观测 2026-10)」；锚格回显/引擎格=4.1 | 四舍五入一致(差 0) | 一致 |
| P061 | UNEMPLOYMENT·最新一期·发布日(规则 5) | period_end+rule, 日历条目优先 | 2026-11-05 | 2026-11-05 | 等值比较 | 一致 |
| P062 | UNEMPLOYMENT·最新一期·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P063 | INDPRO·3个月前·观测日 | series_store.INDPRO + 发布纪律(锚 2026-08-23) | 2026-07-01 | 2026-07-01；锚格回显/引擎格=2026-07-01；注: 判断档 anchor_echo.observation_month=2026-07 | 等值比较 | 一致 |
| P064 | INDPRO·3个月前·值 | series_store.INDPRO[2026-07-01] | 103.168 | 103.168；字面「3 个月前锚前值为 103.1675(观测 2026-07)」；锚格回显/引擎格=103.168 | 四舍五入一致(差 0) | 一致 |
| P065 | INDPRO·3个月前·发布日(规则 15) | period_end+rule, 日历条目优先 | 2026-08-15 | 2026-08-15 | 等值比较 | 一致 |
| P066 | INDPRO·3个月前·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P067 | INDPRO·3个月前·同比 | series_store.INDPRO 同比(基期 2025-07-01) | 1.24983 | 1.25；注: 同比数字在判断档正文中的字面比对见 ③同比 | 四舍五入一致(差 0.000172) | 一致 |
| P068 | INDPRO·最新一期·观测日 | series_store.INDPRO + 发布纪律(锚 2026-11-23) | 2026-10-01 | 2026-10-01；锚格回显/引擎格=2026-10-01；注: 判断档 anchor_echo.observation_month=2026-10 | 等值比较 | 一致 |
| P069 | INDPRO·最新一期·值 | series_store.INDPRO[2026-10-01] | 103.395 | 103.395；字面「INDPRO 报 103.3954(观测 2026-10)」；锚格回显/引擎格=103.395 | 四舍五入一致(差 0) | 一致 |
| P070 | INDPRO·最新一期·发布日(规则 15) | period_end+rule, 日历条目优先 | 2026-11-15 | 2026-11-15 | 等值比较 | 一致 |
| P071 | INDPRO·最新一期·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P072 | INDPRO·最新一期·同比 | series_store.INDPRO 同比(基期 2025-10-01) | 2.14968 | 2.15；注: 同比数字在判断档正文中的字面比对见 ③同比 | 四舍五入一致(差 0.000315) | 一致 |
| P073 | CPI·3个月前·观测日 | series_store.CPI + 发布纪律(锚 2026-08-23) | 2026-07-01 | 2026-07-01；锚格回显/引擎格=2026-07-01；注: 判断档 anchor_echo.observation_month=2026-07 | 等值比较 | 一致 |
| P074 | CPI·3个月前·值 | series_store.CPI[2026-07-01] | 332.813 | 332.813；字面「3 个月前锚前值 332.813,观测 2026-07」；锚格回显/引擎格=332.813 | 四舍五入一致(差 0) | 一致 |
| P075 | CPI·3个月前·发布日(规则 13) | period_end+rule, 日历条目优先 | 2026-08-13 | 2026-08-13 | 等值比较 | 一致 |
| P076 | CPI·3个月前·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P077 | CPI·3个月前·同比 | series_store.CPI 同比(基期 2025-07-01) | 3.30386 | 3.3；注: 同比数字在判断档正文中的字面比对见 ③同比 | 四舍五入一致(差 0.00386) | 一致 |
| P078 | CPI·最新一期·观测日 | series_store.CPI + 发布纪律(锚 2026-11-23) | 2026-10-01 | 2026-10-01；锚格回显/引擎格=2026-10-01；注: 判断档 anchor_echo.observation_month=2026-10 | 等值比较 | 一致 |
| P079 | CPI·最新一期·值 | series_store.CPI[2026-10-01] | 337.476 | 337.476；字面「最新报 337.476(观测 2026-10」；锚格回显/引擎格=337.476 | 四舍五入一致(差 0) | 一致 |
| P080 | CPI·最新一期·发布日(规则 13) | period_end+rule, 日历条目优先 | 2026-11-13 | 2026-11-13 | 等值比较 | 一致 |
| P081 | CPI·最新一期·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P082 | CPI·最新一期·同比 | series_store.CPI 同比(基期 2025-10-01) | — | —；注: 同比数字在判断档正文中的字面比对见 ③同比 | 等值比较 | 一致 |
| P083 | CPI·最新一期·同比缺基期状态 | series_store.CPI 基期 2025-10-01 在场? | no_same_period_base | no_same_period_base；字面「同比派生口径 2026-10 因缺上年同月基期观测不可得」 | 等值比较 | 一致 |
| P084 | CORE_CPI·3个月前·观测日 | series_store.CORE_CPI + 发布纪律(锚 2026-08-23) | 2026-07-01 | 2026-07-01；锚格回显/引擎格=2026-07-01；注: 判断档 anchor_echo.observation_month=2026-07 | 等值比较 | 一致 |
| P085 | CORE_CPI·3个月前·值 | series_store.CORE_CPI[2026-07-01] | 336.789 | 336.789；字面「指数水平 336.789→339.9」；锚格回显/引擎格=336.789 | 四舍五入一致(差 0) | 一致 |
| P086 | CORE_CPI·3个月前·发布日(规则 13) | period_end+rule, 日历条目优先 | 2026-08-13 | 2026-08-13 | 等值比较 | 一致 |
| P087 | CORE_CPI·3个月前·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P088 | CORE_CPI·3个月前·同比 | series_store.CORE_CPI 同比(基期 2025-07-01) | 2.46652 | 2.47；注: 同比数字在判断档正文中的字面比对见 ③同比 | 四舍五入一致(差 0.00348) | 一致 |
| P089 | CORE_CPI·最新一期·观测日 | series_store.CORE_CPI + 发布纪律(锚 2026-11-23) | 2026-10-01 | 2026-10-01；锚格回显/引擎格=2026-10-01；注: 判断档 anchor_echo.observation_month=2026-10 | 等值比较 | 一致 |
| P090 | CORE_CPI·最新一期·值 | series_store.CORE_CPI[2026-10-01] | 339.9 | 339.9；字面「CORE_CPI 报 339.9(观测 2026-10)」；锚格回显/引擎格=339.9 | 四舍五入一致(差 0) | 一致 |
| P091 | CORE_CPI·最新一期·发布日(规则 13) | period_end+rule, 日历条目优先 | 2026-11-13 | 2026-11-13 | 等值比较 | 一致 |
| P092 | CORE_CPI·最新一期·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P093 | CORE_CPI·最新一期·同比 | series_store.CORE_CPI 同比(基期 2025-10-01) | — | —；注: 同比数字在判断档正文中的字面比对见 ③同比 | 等值比较 | 一致 |
| P094 | CORE_CPI·最新一期·同比缺基期状态 | series_store.CORE_CPI 基期 2025-10-01 在场? | no_same_period_base | no_same_period_base | 等值比较 | 一致 |
| P095 | CORE_PCE·3个月前·观测日 | series_store.CORE_PCE + 发布纪律(锚 2026-08-23) | 2026-06-01 | 2026-06-01；锚格回显/引擎格=2026-06-01；注: 判断档 anchor_echo.observation_month=2026-06 | 等值比较 | 一致 |
| P096 | CORE_PCE·3个月前·值 | series_store.CORE_PCE[2026-06-01] | 129.969 | 129.969；字面「指数水平 129.969→130.902」；锚格回显/引擎格=129.969 | 四舍五入一致(差 0) | 一致 |
| P097 | CORE_PCE·3个月前·发布日(规则 30) | period_end+rule, 日历条目优先 | 2026-07-30 | 2026-07-30 | 等值比较 | 一致 |
| P098 | CORE_PCE·3个月前·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P099 | CORE_PCE·3个月前·同比 | series_store.CORE_PCE 同比(基期 2025-06-01) | 3.04123 | 3.04；注: 同比数字在判断档正文中的字面比对见 ③同比 | 四舍五入一致(差 0.00123) | 一致 |
| P100 | CORE_PCE·最新一期·观测日 | series_store.CORE_PCE + 发布纪律(锚 2026-11-23) | 2026-09-01 | 2026-09-01；锚格回显/引擎格=2026-09-01；注: 判断档 anchor_echo.observation_month=2026-09 | 等值比较 | 一致 |
| P101 | CORE_PCE·最新一期·值 | series_store.CORE_PCE[2026-09-01] | 130.902 | 130.902；字面「CORE_PCE 报 130.902(观测 2026-09)」；锚格回显/引擎格=130.902 | 四舍五入一致(差 0) | 一致 |
| P102 | CORE_PCE·最新一期·发布日(规则 30) | period_end+rule, 日历条目优先 | 2026-10-30 | 2026-10-30 | 等值比较 | 一致 |
| P103 | CORE_PCE·最新一期·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P104 | CORE_PCE·最新一期·同比 | series_store.CORE_PCE 同比(基期 2025-09-01) | 3.12116 | 3.12；注: 同比数字在判断档正文中的字面比对见 ③同比 | 四舍五入一致(差 0.00116) | 一致 |
| P105 | EA_REAL_GDP_YOY·3个月前·观测日 | series_store.EA_REAL_GDP_YOY + 发布纪律(锚 2026-08-23) | 2026-04-01 | 2026-04-01；锚格回显/引擎格=2026-04-01；注: 判断档 anchor_echo.observation_month=2026-04 | 等值比较 | 一致 |
| P106 | EA_REAL_GDP_YOY·3个月前·值 | series_store.EA_REAL_GDP_YOY[2026-04-01] | 1.19 | 1.19；字面「2026Q2 为 1.19%」；锚格回显/引擎格=1.19 | 四舍五入一致(差 0) | 一致 |
| P107 | EA_REAL_GDP_YOY·3个月前·发布日(规则 35) | period_end+rule, 日历条目优先 | 2026-08-04 | 2026-08-04 | 等值比较 | 一致 |
| P108 | EA_REAL_GDP_YOY·3个月前·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P109 | EA_REAL_GDP_YOY·最新一期·观测日 | series_store.EA_REAL_GDP_YOY + 发布纪律(锚 2026-11-23) | 2026-07-01 | 2026-07-01；锚格回显/引擎格=2026-07-01；注: 判断档 anchor_echo.observation_month=2026-07 | 等值比较 | 一致 |
| P110 | EA_REAL_GDP_YOY·最新一期·值 | series_store.EA_REAL_GDP_YOY[2026-07-01] | 1.28 | 1.28；字面「2026Q3 为 1.28%」；锚格回显/引擎格=1.28 | 四舍五入一致(差 0) | 一致 |
| P111 | EA_REAL_GDP_YOY·最新一期·发布日(规则 35) | period_end+rule, 日历条目优先 | 2026-11-04 | 2026-11-04 | 等值比较 | 一致 |
| P112 | EA_REAL_GDP_YOY·最新一期·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P113 | EA_HICP_YOY·3个月前·观测日 | series_store.EA_HICP_YOY + 发布纪律(锚 2026-08-23) | 2026-07-01 | 2026-07-01；锚格回显/引擎格=2026-07-01；注: 判断档 anchor_echo.observation_month=2026-07 | 等值比较 | 一致 |
| P114 | EA_HICP_YOY·3个月前·值 | series_store.EA_HICP_YOY[2026-07-01] | 2.9 | 2.9；字面「HICP 同比 2.9%(2026-07)→4.0%(2026-10)」；锚格回显/引擎格=2.9 | 四舍五入一致(差 0) | 一致 |
| P115 | EA_HICP_YOY·3个月前·发布日(规则 16) | period_end+rule, 日历条目优先 | 2026-08-16 | 2026-08-16 | 等值比较 | 一致 |
| P116 | EA_HICP_YOY·3个月前·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P117 | EA_HICP_YOY·最新一期·观测日 | series_store.EA_HICP_YOY + 发布纪律(锚 2026-11-23) | 2026-10-01 | 2026-10-01；锚格回显/引擎格=2026-10-01；注: 判断档 anchor_echo.observation_month=2026-10 | 等值比较 | 一致 |
| P118 | EA_HICP_YOY·最新一期·值 | series_store.EA_HICP_YOY[2026-10-01] | 4 | 4；字面「HICP 同比 2.9%(2026-07)→4.0%(2026-10)」；锚格回显/引擎格=4 | 四舍五入一致(差 0) | 一致 |
| P119 | EA_HICP_YOY·最新一期·发布日(规则 16) | period_end+rule, 日历条目优先 | 2026-11-16 | 2026-11-16 | 等值比较 | 一致 |
| P120 | EA_HICP_YOY·最新一期·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P121 | JP_POLICY_RATE·3个月前·观测日 | series_store.JP_POLICY_RATE + 发布纪律(锚 2026-08-23) | 2026-07-01 | 2026-07-01；锚格回显/引擎格=2026-07-01；注: 判断档 anchor_echo.observation_month=2026-07 | 等值比较 | 一致 |
| P122 | JP_POLICY_RATE·3个月前·值 | series_store.JP_POLICY_RATE[2026-07-01] | 0.978 | 0.978；字面「3 个月前锚(2026-07)为 0.978%」；锚格回显/引擎格=0.978 | 四舍五入一致(差 0) | 一致 |
| P123 | JP_POLICY_RATE·3个月前·发布日(规则 5) | period_end+rule, 日历条目优先 | 2026-08-05 | 2026-08-05 | 等值比较 | 一致 |
| P124 | JP_POLICY_RATE·3个月前·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |
| P125 | JP_POLICY_RATE·最新一期·观测日 | series_store.JP_POLICY_RATE + 发布纪律(锚 2026-11-23) | 2026-10-01 | 2026-10-01；锚格回显/引擎格=2026-10-01；注: 判断档 anchor_echo.observation_month=2026-10 | 等值比较 | 一致 |
| P126 | JP_POLICY_RATE·最新一期·值 | series_store.JP_POLICY_RATE[2026-10-01] | 1.227 | 1.227；字面「最新一期(2026-10)为 1.227%」；锚格回显/引擎格=1.227 | 四舍五入一致(差 0) | 一致 |
| P127 | JP_POLICY_RATE·最新一期·发布日(规则 5) | period_end+rule, 日历条目优先 | 2026-11-05 | 2026-11-05 | 等值比较 | 一致 |
| P128 | JP_POLICY_RATE·最新一期·发布日≤锚日 | pub vs as_of | True | True | 精确 | 一致 |


**③同比** — 独立复算 28 点(偏离 0)

| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |
|---|---|---|---|---|---|---|
| P129 | CPI 同比@2026-07 | series_store.CPI 同比 | 3.30386 | 3.3；字面「CPI 同比 3.3%(2026-07)」 | 四舍五入一致(差 0.00386) | 一致 |
| P130 | CPI 同比@2026-09(最近有效) | series_store.CPI 同比 | 3.71725 | 3.72；字面「最近有效 3.72%(2026-09」 | 四舍五入一致(差 0.00275) | 一致 |
| P131 | CPI 最近有效同比月份 | series_store.CPI + 发布纪律 | 2026-09-01 | 2026-09-01；字面「最近有效 3.72%(2026-09」 | 等值比较 | 一致 |
| P132 | CPI 同比@2026-02 | series_store.CPI 同比 | 2.434 | 2.434；字面「由 2.434 升至 4.1666」 | 四舍五入一致(差 4.11e-06) | 一致 |
| P133 | CPI 同比@2026-05(4位) | series_store.CPI 同比 | 4.16661 | 4.1666；字面「由 2.434 升至 4.1666」 | 四舍五入一致(差 1.47e-05) | 一致 |
| P134 | CPI 同比@2026-05(2位) | series_store.CPI 同比 | 4.16661 | 4.17；字面「2026-05 高点 4.17」 | 四舍五入一致(差 0.00339) | 一致 |
| P135 | CPI 三个月上行幅度(2026-02→2026-05) | series_store.CPI 同比差 | 1.73261 | 1.7326；字面「三个月上行 1.7326 个百分点」 | 四舍五入一致(差 1.06e-05) | 一致 |
| P136 | CPI 同比 2026 年内高点月份 | series_store.CPI 同比(argmax 2026) | 2026-05-01 | 2026-05-01；字面「2026-05 高点」 | 等值比较 | 一致 |
| P137 | CPI 同比@2026-10 不可得(2025-10 基期缺席) | series_store.CPI[2025-10-01] | False | False；字面「2026-10 同比因缺上年同月基期观测不可得」 | 精确 | 一致 |
| P138 | CPI「回升」: 2026-09 > 2026-08 | series_store.CPI 同比 | True | True；字面「美国 CPI 同比 2026-09 回升至 3.72」 | 精确 | 一致 |
| P139 | CORE_CPI 同比@2026-07 | series_store.CORE_CPI 同比 | 2.46652 | 2.47；字面「核心 CPI 同比 2.47%(2026-07)」 | 四舍五入一致(差 0.00348) | 一致 |
| P140 | CORE_CPI 同比@2026-09(最近有效) | series_store.CORE_CPI 同比 | 2.56584 | 2.57；字面「→2.57%(2026-09」 | 四舍五入一致(差 0.00416) | 一致 |
| P141 | CORE_CPI 最近有效同比月份 | series_store.CORE_CPI + 发布纪律 | 2026-09-01 | 2026-09-01；字面「2.57%(2026-09」 | 等值比较 | 一致 |
| P142 | CORE_CPI 同比@2026-02 | series_store.CORE_CPI 同比 | 2.47246 | 2.4725；字面「同比自 2.4725 升至 2.8229」 | 四舍五入一致(差 3.75e-05) | 一致 |
| P143 | CORE_CPI 同比@2026-05 | series_store.CORE_CPI 同比 | 2.82294 | 2.8229；字面「同比自 2.4725 升至 2.8229」 | 四舍五入一致(差 4.21e-05) | 一致 |
| P144 | CORE_CPI 同比@2026-08 | series_store.CORE_CPI 同比 | 2.44616 | 2.4462；字面「同比自 2.8229 回落至 2.4462」 | 四舍五入一致(差 3.68e-05) | 一致 |
| P145 | CORE_CPI 同比@2026-09(4位) | series_store.CORE_CPI 同比 | 2.56584 | 2.5658；字面「其后 2026-09 回升至 2.5658」 | 四舍五入一致(差 4.08e-05) | 一致 |
| P146 | CORE_CPI 同比@2026-10 基期缺席 | series_store.CORE_CPI[2025-10-01] | False | False | 精确 | 一致 |
| P147 | CORE_PCE 同比@2026-06 | series_store.CORE_PCE 同比 | 3.04123 | 3.04；字面「核心 PCE 同比 3.04%(2026-06)」 | 四舍五入一致(差 0.00123) | 一致 |
| P148 | CORE_PCE 同比@2026-09 | series_store.CORE_PCE 同比 | 3.12116 | 3.12；字面「→3.12%(2026-09」 | 四舍五入一致(差 0.00116) | 一致 |
| P149 | INDPRO 同比@2026-07 | series_store.INDPRO 同比 | 1.24983 | 1.25；字面「工业生产同比 1.25%(2026-07)」 | 四舍五入一致(差 0.000172) | 一致 |
| P150 | INDPRO 同比@2026-10 | series_store.INDPRO 同比 | 2.14968 | 2.15；字面「→2.15%(2026-10)」 | 四舍五入一致(差 0.000315) | 一致 |
| P151 | US_REAL_GDP 同比@2026-04(Q2) | series_store.US_REAL_GDP 同比(去年同季) | 2.19157 | 2.19；字面「实际 GDP 同比 2026Q2 为 2.19%」 | 四舍五入一致(差 0.00157) | 一致 |
| P152 | US_REAL_GDP 同比@2026-07(Q3) | series_store.US_REAL_GDP 同比(去年同季) | 2.06574 | 2.07；字面「2026Q3 为 2.07%」 | 四舍五入一致(差 0.00426) | 一致 |
| P153 | US_REAL_GDP 同比文字(2.19→2.07) | series_store.US_REAL_GDP 同比 | 2.19→2.07 | 2.19→2.07；字面「(2.19→2.07,引擎派生口径)」 | 等值比较 | 一致 |
| P154 | INDPRO 同比文字(1.25→2.15) | series_store.INDPRO 同比 | 1.25→2.15 | 1.25→2.15；字面「(1.25→2.15,引擎派生口径)」 | 等值比较 | 一致 |
| P155 | US_REAL_GDP Q2 同比基期=去年同季(2025Q2)且在场 | series_store.US_REAL_GDP[2025-04-01] | True | True；注: 基期值 23884.563 | 精确 | 一致 |
| P156 | US_REAL_GDP Q3 同比基期=去年同季(2025Q3)且在场 | series_store.US_REAL_GDP[2025-07-01] | True | True；注: 基期值 24112.966 | 精确 | 一致 |


**④政策面** — 独立复算 21 点(偏离 0)

| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |
|---|---|---|---|---|---|---|
| P018 | 日历版本 | release_calendar.json version | 1.5.0 | 1.5.0；字面「冻结发布日历 v1.5.0」 | 等值比较 | 一致 |
| P019 | 政策类日历条目数 | release_calendar.json entries[kind∈policy_*] | 2 | 2；字面「发布日历政策条目仅 2 条、均为日本央行实录」 | 四舍五入一致(差 0) | 一致 |
| P020 | 政策类条目全部为日本央行(JP_POLICY_TARGET) | entries[kind∈policy_*].metric_id | JP_POLICY_TARGET | JP_POLICY_TARGET | 等值比较 | 一致 |
| P021 | 无美欧决议/生效实录条目 | entries[kind∈policy_*] 是否含 US/EA 指标 | False | False；字面「冻结日历无美欧决议/生效实录条目」 | 精确 | 一致 |
| P022 | 日本央行决议日 | calendar RC-JP-BOJ-TARGET-2026-09.decision_date | 2026-09-18 | 2026-09-18；字面「2026-09-18 决议」 | 等值比较 | 一致 |
| P023 | 日本央行生效日 | calendar RC-JP-BOJ-TARGET-2026-09.effective_on | 2026-09-24 | 2026-09-24；字面「2026-09-24 生效」 | 等值比较 | 一致 |
| P024 | 日本央行目标水平 | calendar RC-JP-BOJ-TARGET-2026-09.target_value | 1.25 | 1.25；字面「官方政策目标利率约 1.25(2026-09-18 决议」 | 四舍五入一致(差 0) | 一致 |
| P025 | 日本央行目标水平(判断档中文数字写法) | calendar target_value vs 判断档「约一点二五」 | 1.25 | 1.25；字面「日本央行政策目标利率约一点二五,2026-09-18 决议、2026-09-24 生效」 | 四舍五入一致(差 0) | 一致 |
| P026 | 维持会议日期 | calendar RC-JP-BOJ-MAINT-2026-10.decision_date | 2026-10-30 | 2026-10-30；字面「2026-10-30 会议确认维持不变(RC-JP-BOJ-MAINT-2026-10)」 | 等值比较 | 一致 |
| P027 | 维持条目目标值不变 | calendar RC-JP-BOJ-MAINT-2026-10.target_value | 1.25 | 1.25；字面「2026-10-30 会议确认维持不变」 | 四舍五入一致(差 0) | 一致 |
| P028 | 维持条目无生效日 | calendar RC-JP-BOJ-MAINT-2026-10.effective_on | — | —；字面「维持条目无生效日」 | 等值比较 | 一致 |
| P029 | 决议条目 first_publish=决议日 | calendar RC-JP-BOJ-TARGET-2026-09.first_publish_on_or_after | 2026-09-18 | 2026-09-18 | 等值比较 | 一致(结构性自检,不计入) |
| P030 | 距上次调整·按生效日(天) | 截止日 − RC-JP-BOJ-TARGET-2026-09.effective_on | 60 | 60；字面「距上次调整按生效日 60 天」 | 四舍五入一致(差 0) | 一致 |
| P031 | 距上次调整·按决议日(天) | 截止日 − decision_date | 66 | 66；字面「按决议日 66 天」 | 四舍五入一致(差 0) | 一致 |
| P032 | 距上次调整·按生效日(中文数字写法) | 截止日 − effective_on | 60 | 60；字面「距上次调整按生效日六十天、按决议日六十六天」 | 四舍五入一致(差 0) | 一致 |
| P033 | 距上次调整·按决议日(中文数字写法) | 截止日 − decision_date | 66 | 66；字面「按决议日六十六天」 | 四舍五入一致(差 0) | 一致 |
| P034 | 距维持会议(天) | 截止日 − RC-JP-BOJ-MAINT-2026-10.decision_date | 24 | 24；字面「\| 日本 \| 1.25 \| — \| 2026-09-18 \| 2026-09-24 \| 2026-10-30 \| 2026-1…」 | 四舍五入一致(差 0) | 一致 |
| P035 | 生效日落在 2026-09 最后一周 | calendar effective_on 所在月余天数 | 7 | 7；字面「落在 2026-09 最后一周」 | 四舍五入一致(差 0) | 一致 |
| P036 | 决议生效后首个整月=2026-10 | calendar effective_on → 下一整月 | 2026-10 | 2026-10；字面「次月为决议生效后首个整月」 | 等值比较 | 一致 |
| P037 | JP_POLICY_TARGET 不在注册表 | metric_registry.json metrics | False | False；字面「宣布目标序列 JP_POLICY_TARGET 在引擎注册表不可得」 | 精确 | 一致 |
| P038 | JP_POLICY_TARGET 不在 series_store | snapshot.series_store | False | False；字面「不以相邻口径冒充」 | 精确 | 一致 |
| P039 | JP_POLICY_RATE 口径=月均(非目标宣布值) | metric_registry JP_POLICY_RATE.value_type | monthly_avg_rate | monthly_avg_rate；字面「该序列为无担保隔夜拆借利率月均口径,非政策目标宣布值」 | 等值比较 | 一致 |
| P040 | JP_POLICY_TARGET 缺口=registry_absent | research_plan.dimension_gaps | registry_absent | registry_absent | 等值比较 | 一致(结构性自检,不计入) |


**⑤三利率** — 独立复算 28 点(偏离 0)

| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |
|---|---|---|---|---|---|---|
| P216 | UST_10Y 期末水平@2026-11-19 | series_store.UST_10Y[2026-11-19] | 5.04 | 5.04；字面「美国十年期名义利率 2026-11-19 报 5.04%」；锚格回显/引擎格=5.04 | 四舍五入一致(差 0) | 一致 |
| P217 | TIPS_10Y 期末水平@2026-11-19 | series_store.TIPS_10Y[2026-11-19] | 2.88 | 2.88；字面「TIPS_10Y 2.66→2.88」；锚格回显/引擎格=2.88 | 四舍五入一致(差 0) | 一致 |
| P218 | BEI_10Y 期末水平@2026-11-19 | series_store.BEI_10Y[2026-11-19] | 2.16 | 2.16；字面「自 2.30 回落至 2.16(-14bp)」；锚格回显/引擎格=2.16 | 四舍五入一致(差 0) | 一致 |
| P219 | BEI_10Y@2026-11-20 | series_store.BEI_10Y[2026-11-20] | 2.15 | 2.15；字面「BEI_10Y 水平为 2.15(观测 2026-11-20)」 | 四舍五入一致(差 0) | 一致 |
| P220 | 期末水平恒等 名义=实际+盈亏平衡@2026-11-19 | series_store 三序列[2026-11-19] | 0 | 0 | 四舍五入一致(差 0) | 一致 |
| P221 | 近一月窗 名义 Δbp(2026-10-20→2026-11-19) | series_store.UST_10Y | -8 | -8；字面「变动 -8bp」；锚格回显/引擎格=-8 | 四舍五入一致(差 7.11e-15) | 一致 |
| P222 | 近一月窗 实际 Δbp | series_store.TIPS_10Y | 11 | 11；字面「(TIPS_10Y)+11bp」；锚格回显/引擎格=11 | 四舍五入一致(差 1.24e-14) | 一致 |
| P223 | 近一月窗 盈亏平衡 Δbp | series_store.BEI_10Y | -19 | -19；字面「(BEI_10Y)-19bp」；锚格回显/引擎格=-19 | 四舍五入一致(差 7.11e-15) | 一致 |
| P224 | 近一月窗 恒等残差 名义−(实际+盈亏平衡) | series_store 三序列 | -1.77636e-15 | 0 | 四舍五入一致(差 1.78e-15) | 一致 |
| P225 | 近一月窗 端点恒等(两日各自 名义=实际+BEI) | series_store 三序列@2026-10-20 | 0 | 0；注: 窗起日 2026-10-20 三序列同日在场且恒等成立 | 四舍五入一致(差 0) | 一致 |
| P226 | 三个月窗 名义 Δbp(2026-08-19→2026-11-19) | series_store.UST_10Y | 39 | 39；字面「名义 +39bp」 | 四舍五入一致(差 2.84e-14) | 一致 |
| P227 | 三个月窗 实际 Δbp | series_store.TIPS_10Y | 53 | 53；字面「实际 +53bp」 | 四舍五入一致(差 2.13e-14) | 一致 |
| P228 | 三个月窗 盈亏平衡 Δbp | series_store.BEI_10Y | -14 | -14；字面「盈亏平衡 -14bp」 | 四舍五入一致(差 3.2e-14) | 一致 |
| P229 | 三个月窗 恒等残差 名义−(实际+盈亏平衡) | series_store 三序列 | -4.26326e-14 | 0；字面「(残差 0)」 | 四舍五入一致(差 4.26e-14) | 一致 |
| P230 | 三个月窗 端点恒等(两日各自 名义=实际+BEI) | series_store 三序列@2026-08-19 | 4.44089e-16 | 0；注: 窗起日 2026-08-19 三序列同日在场且恒等成立 | 四舍五入一致(差 4.44e-16) | 一致 |
| P231 | 12个月窗 名义 Δbp(2025-11-19→2026-11-19) | series_store.UST_10Y | 91 | 91；字面「名义 +91bp」；锚格回显/引擎格=91 | 四舍五入一致(差 1.42e-14) | 一致 |
| P232 | 12个月窗 实际 Δbp | series_store.TIPS_10Y | 102 | 102；字面「实际 +102bp」；锚格回显/引擎格=102 | 四舍五入一致(差 1.42e-14) | 一致 |
| P233 | 12个月窗 盈亏平衡 Δbp | series_store.BEI_10Y | -11 | -11；字面「盈亏平衡 -11bp」；锚格回显/引擎格=-11 | 四舍五入一致(差 1.24e-14) | 一致 |
| P234 | 12个月窗 恒等残差 名义−(实际+盈亏平衡) | series_store 三序列 | 1.42109e-14 | 0；字面「(残差 0)」 | 四舍五入一致(差 1.42e-14) | 一致 |
| P235 | 12个月窗 端点恒等(两日各自 名义=实际+BEI) | series_store 三序列@2025-11-19 | -4.44089e-16 | 0；注: 窗起日 2025-11-19 三序列同日在场且恒等成立 | 四舍五入一致(差 4.44e-16) | 一致 |
| P236 | BEI_10Y 窗起值@2026-10-20 | series_store.BEI_10Y[2026-10-20] | 2.35 | 2.35；注: 期末水平 2.16 − 判断档变动 −19bp 的反推端点值 | 四舍五入一致(差 0) | 一致 |
| P237 | TIPS_10Y 窗起值@2026-10-20 | series_store.TIPS_10Y[2026-10-20] | 2.77 | 2.77 | 四舍五入一致(差 0) | 一致 |
| P238 | UST_10Y 窗起值@2026-10-20 | series_store.UST_10Y[2026-10-20] | 5.12 | 5.12 | 四舍五入一致(差 0) | 一致 |
| P239 | BEI_10Y 三个月窗起值 2.30@2026-08-19 | series_store.BEI_10Y[2026-08-19] | 2.3 | 2.3；字面「自 2.30 回落至 2.16(-14bp)」 | 四舍五入一致(差 0) | 一致 |
| P240 | TIPS_10Y@2026-10-23 | series_store.TIPS_10Y[2026-10-23] | 2.66 | 2.66；字面「同窗 TIPS_10Y 2.66→2.88(+22bp」 | 四舍五入一致(差 0) | 一致 |
| P241 | TIPS_10Y 10-23→11-19 Δbp | series_store.TIPS_10Y | 22 | 22；字面「2.66→2.88(+22bp」 | 四舍五入一致(差 2.49e-14) | 一致 |
| P242 | BEI_10Y@2026-02-27 | series_store.BEI_10Y[2026-02-27] | 2.25 | 2.25；字面「BEI_10Y 自 2026-02-27 的 2.25 升至 2026-05-04 的 2.50」 | 四舍五入一致(差 0) | 一致 |
| P243 | BEI_10Y@2026-05-04 | series_store.BEI_10Y[2026-05-04] | 2.5 | 2.5；字面「BEI_10Y 自 2026-02-27 的 2.25 升至 2026-05-04 的 2.50」 | 四舍五入一致(差 0) | 一致 |


**⑤资产月窗** — 独立复算 27 点(偏离 0)

| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |
|---|---|---|---|---|---|---|
| P244 | SPX 近一月涨跌幅(2026-10-23→2026-11-23) | series_store.SPX | -5.50692 | -5.51；字面「SPX 下跌 5.51%」；锚格回显/引擎格=-5.51 | 四舍五入一致(差 0.00308) | 一致 |
| P245 | SPX 窗末日=2026-11-23 | series_store.SPX.dates[-1] / 引擎窗 | 2026-11-23 | 2026-11-23；锚格回显/引擎格=2026-11-23 | 等值比较 | 一致 |
| P246 | SPX 窗起日=2026-10-23 | series_store.SPX[2026-10-23] 在场 | True | True | 精确 | 一致 |
| P247 | NIKKEI225 近一月涨跌幅(2026-10-23→2026-11-20) | series_store.NIKKEI225 | -9.97957 | -9.98；字面「NIKKEI225 下跌 9.98%」；锚格回显/引擎格=-9.98 | 四舍五入一致(差 0.000426) | 一致 |
| P248 | NIKKEI225 窗末日=2026-11-20 | series_store.NIKKEI225.dates[-1] / 引擎窗 | 2026-11-20 | 2026-11-20；锚格回显/引擎格=2026-11-20 | 等值比较 | 一致 |
| P249 | NIKKEI225 窗起日=2026-10-23 | series_store.NIKKEI225[2026-10-23] 在场 | True | True | 精确 | 一致 |
| P250 | GOLD_F 近一月涨跌幅(2026-10-23→2026-11-23) | series_store.GOLD_F | -8.0516 | -8.05；字面「GOLD_F 下跌 8.05%」；锚格回显/引擎格=-8.05 | 四舍五入一致(差 0.0016) | 一致 |
| P251 | GOLD_F 窗末日=2026-11-23 | series_store.GOLD_F.dates[-1] / 引擎窗 | 2026-11-23 | 2026-11-23；锚格回显/引擎格=2026-11-23 | 等值比较 | 一致 |
| P252 | GOLD_F 窗起日=2026-10-23 | series_store.GOLD_F[2026-10-23] 在场 | True | True | 精确 | 一致 |
| P253 | DXY 近一月涨跌幅(2026-10-23→2026-11-23) | series_store.DXY | 2.22867 | 2.23；字面「DXY 上涨 2.23%」；锚格回显/引擎格=2.23 | 四舍五入一致(差 0.00133) | 一致 |
| P254 | DXY 窗末日=2026-11-23 | series_store.DXY.dates[-1] / 引擎窗 | 2026-11-23 | 2026-11-23；锚格回显/引擎格=2026-11-23 | 等值比较 | 一致 |
| P255 | DXY 窗起日=2026-10-23 | series_store.DXY[2026-10-23] 在场 | True | True | 精确 | 一致 |
| P256 | VIX 近一月涨跌幅(2026-10-23→2026-11-23) | series_store.VIX | 38.8689 | 38.87；字面「VIX 上涨 38.87%」；锚格回显/引擎格=38.87 | 四舍五入一致(差 0.00111) | 一致 |
| P257 | VIX 窗末日=2026-11-23 | series_store.VIX.dates[-1] / 引擎窗 | 2026-11-23 | 2026-11-23；锚格回显/引擎格=2026-11-23 | 等值比较 | 一致 |
| P258 | VIX 窗起日=2026-10-23 | series_store.VIX[2026-10-23] 在场 | True | True | 精确 | 一致 |
| P259 | VIX 窗起值 19.45 | series_store.VIX[2026-10-23] | 19.45 | 19.45；字面「(19.45→27.01」 | 四舍五入一致(差 1e-06) | 一致 |
| P260 | VIX 窗末值 27.01 | series_store.VIX[2026-11-23] | 27.01 | 27.01；字面「(19.45→27.01」 | 四舍五入一致(差 0) | 一致 |
| P261 | 同日收盘口径 SPX 10-23→11-20 | series_store.SPX | -9.35624 | -9.36；字面「标普500指数 -9.36%」 | 四舍五入一致(差 0.00376) | 一致 |
| P262 | 同日收盘口径 VIX 10-23→11-20 | series_store.VIX | 84.5244 | 84.52；字面「VIX +84.52%」 | 四舍五入一致(差 0.00441) | 一致 |
| P263 | 三个月收盘口径 SPX 08-19→11-20 | series_store.SPX | -10.3476 | -10.35；字面「标普500指数 -10.35%」 | 四舍五入一致(差 0.00241) | 一致 |
| P264 | 三个月收盘口径 VIX 08-19→11-20 | series_store.VIX | 141.034 | 141.03；字面「VIX +141.03%(14.89→35.89)」 | 四舍五入一致(差 0.00424) | 一致 |
| P265 | VIX 三个月窗起值 14.89 | series_store.VIX[2026-08-19] | 14.89 | 14.89；字面「VIX +141.03%(14.89→35.89)」 | 四舍五入一致(差 0) | 一致 |
| P266 | VIX 三个月窗末值 35.89 | series_store.VIX[2026-11-20] | 35.89 | 35.89；字面「VIX +141.03%(14.89→35.89)」 | 四舍五入一致(差 1e-06) | 一致 |
| P267 | SPX 11-23 值为序列末观测(盘中) | series_store.SPX.dates[-1] | 2026-11-23 | 2026-11-23；字面「11-23 值为盘中快照(非收盘价)」 | 等值比较 | 一致 |
| P268 | rates_decomposition.nominal_bp | reader_map.rates_decomposition vs 直算 | -8 | -8 | 四舍五入一致(差 7.11e-15) | 一致 |
| P269 | rates_decomposition.real_bp | reader_map.rates_decomposition vs 直算 | 11 | 11 | 四舍五入一致(差 1.24e-14) | 一致 |
| P270 | rates_decomposition.bei_bp | reader_map.rates_decomposition vs 直算 | -19 | -19 | 四舍五入一致(差 7.11e-15) | 一致 |
| P271 | rates_decomposition 窗端点 | reader_map.rates_decomposition vs 引擎 us_rates_trio.window | 2026-10-20→2026-11-19 | 2026-10-20→2026-11-19 | 等值比较 | 一致(结构性自检,不计入) |


**⑥转折候选** — 独立复算 40 点(偏离 0)

| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |
|---|---|---|---|---|---|---|
| P157 | 候选池规模 | research_plan.turning_candidates.candidates | 7 | 7；字面「候选池7、top3」 | 四舍五入一致(差 0) | 一致 |
| P158 | top_n_expected | research_plan.turning_candidates.top_n_expected | 3 | 3；字面「候选池7、top3」 | 四舍五入一致(差 0) | 一致 |
| P159 | CPI 候选前值@2026-02 | series_store.CPI | 2.434 | 2.434；字面「由 2.434 升至 4.1666」；注: 候选面(引擎确定性); 判断档引用该段 | 四舍五入一致(差 4.11e-06) | 一致 |
| P160 | CPI 候选后值@2026-05 | series_store.CPI | 4.16661 | 4.1666；字面「由 2.434 升至 4.1666」；注: 判断档引用该段 | 四舍五入一致(差 1.47e-05) | 一致 |
| P161 | CPI 候选变动幅 | series_store.CPI 后值−前值 | 1.73261 | 1.7326 | 四舍五入一致(差 1.06e-05) | 一致 |
| P162 | EA_HICP_YOY 候选前值@2026-02 | series_store.EA_HICP_YOY | 1.9 | 1.9；字面「由 1.9 升至 3.2」；注: 候选面(引擎确定性); 判断档引用该段 | 四舍五入一致(差 0) | 一致 |
| P163 | EA_HICP_YOY 候选后值@2026-05 | series_store.EA_HICP_YOY | 3.2 | 3.2；字面「由 1.9 升至 3.2」；注: 判断档引用该段 | 四舍五入一致(差 0) | 一致 |
| P164 | EA_HICP_YOY 候选变动幅 | series_store.EA_HICP_YOY 后值−前值 | 1.3 | 1.3 | 四舍五入一致(差 2.22e-16) | 一致 |
| P165 | INDPRO 候选前值@2025-11 | series_store.INDPRO | 1.75431 | 1.7543；注: 候选面(引擎确定性), 判断档未引用该段数字 | 四舍五入一致(差 1.18e-05) | 一致 |
| P166 | INDPRO 候选后值@2026-02 | series_store.INDPRO | 0.797236 | 0.7972；注: 候选面(引擎确定性) | 四舍五入一致(差 3.6e-05) | 一致 |
| P167 | INDPRO 候选变动幅 | series_store.INDPRO 后值−前值 | -0.957076 | -0.9571 | 四舍五入一致(差 2.42e-05) | 一致 |
| P168 | CORE_CPI 候选前值@2026-05 | series_store.CORE_CPI | 2.82294 | 2.8229；字面「同比自 2.8229 回落至 2.4462」；注: 候选面(引擎确定性); 判断档引用该段 | 四舍五入一致(差 4.21e-05) | 一致 |
| P169 | CORE_CPI 候选后值@2026-08 | series_store.CORE_CPI | 2.44616 | 2.4462；字面「同比自 2.8229 回落至 2.4462」；注: 判断档引用该段 | 四舍五入一致(差 3.68e-05) | 一致 |
| P170 | CORE_CPI 候选变动幅 | series_store.CORE_CPI 后值−前值 | -0.376779 | -0.3767 | 截断/舍入容差内(差 7.89e-05) | 一致 |
| P171 | JP_POLICY_RATE 候选前值@2026-04 | series_store.JP_POLICY_RATE | 0.727 | 0.727；字面「2026-04 0.727→2026-07 0.978」；注: 候选面(引擎确定性); 判断档引用该段 | 四舍五入一致(差 0) | 一致 |
| P172 | JP_POLICY_RATE 候选后值@2026-07 | series_store.JP_POLICY_RATE | 0.978 | 0.978；字面「2026-04 0.727→2026-07 0.978」；注: 判断档引用该段 | 四舍五入一致(差 0) | 一致 |
| P173 | JP_POLICY_RATE 候选变动幅 | series_store.JP_POLICY_RATE 后值−前值 | 0.251 | 0.251 | 四舍五入一致(差 0) | 一致 |
| P174 | CORE_PCE 候选前值@2025-11 | series_store.CORE_PCE | 2.72121 | 2.7212；注: 候选面(引擎确定性), 判断档未引用该段数字 | 四舍五入一致(差 9.14e-06) | 一致 |
| P175 | CORE_PCE 候选后值@2026-02 | series_store.CORE_PCE | 2.95915 | 2.9592；注: 候选面(引擎确定性) | 四舍五入一致(差 4.73e-05) | 一致 |
| P176 | CORE_PCE 候选变动幅 | series_store.CORE_PCE 后值−前值 | 0.237944 | 0.238 | 截断/舍入容差内(差 5.65e-05) | 一致 |
| P177 | UNEMPLOYMENT 候选前值@2026-05 | series_store.UNEMPLOYMENT | 4.3 | 4.3；注: 候选面(引擎确定性), 判断档未引用该段数字 | 四舍五入一致(差 0) | 一致 |
| P178 | UNEMPLOYMENT 候选后值@2026-08 | series_store.UNEMPLOYMENT | 4.1 | 4.1；注: 候选面(引擎确定性) | 四舍五入一致(差 0) | 一致 |
| P179 | UNEMPLOYMENT 候选变动幅 | series_store.UNEMPLOYMENT 后值−前值 | -0.2 | -0.2 | 四舍五入一致(差 1.67e-16) | 一致 |
| P180 | 候选池内最大单段变动=CPI | turning_candidates.candidates argmax\|delta\| | CPI | CPI；字面「为候选池内最大单段变动」 | 等值比较 | 一致 |
| P181 | 候选池内最大单段变动幅 | turning_candidates.candidates max\|delta\| | 1.7326 | 1.7326 | 四舍五入一致(差 0) | 一致 |
| P182 | CPI 与 EA_HICP 候选同窗(2026-02→2026-05) | turning_candidates | True | True；字面「美欧通胀同月抬升、月频证据先后未定」 | 精确 | 一致 |
| P183 | JP 候选窗=2026-04→2026-07 | turning_candidates | 2026-04→2026-07 | 2026-04→2026-07；字面「2026-04 0.727→2026-07 0.978」 | 等值比较 | 一致 |
| P184 | CORE_CPI 候选窗=2026-05→2026-08 | turning_candidates | 2026-05→2026-08 | 2026-05→2026-08；字面「2026-05→2026-08 同比自 2.8229 回落至 2.4462」 | 等值比较 | 一致 |
| P185 | EA_HICP_YOY@2026-02 | series_store.EA_HICP_YOY | 1.9 | 1.9；字面「自 2026-02 的 1.9 抬升至 2026-05 的 3.2」 | 四舍五入一致(差 0) | 一致 |
| P186 | EA_HICP_YOY@2026-05 | series_store.EA_HICP_YOY | 3.2 | 3.2；字面「自 2026-02 的 1.9 抬升至 2026-05 的 3.2」 | 四舍五入一致(差 0) | 一致 |
| P187 | EA_HICP_YOY@2026-06 | series_store.EA_HICP_YOY | 2.8 | 2.8；字面「2026-06 回落至 2.8」 | 四舍五入一致(差 0) | 一致 |
| P188 | EA_HICP_YOY 三个月上行(2.9→4.0) | series_store.EA_HICP_YOY | 1.1 | 1.1；字面「三个月上行 1.1 个百分点」 | 四舍五入一致(差 0) | 一致 |
| P189 | EA_HICP_YOY 2026-02→2026-05 上行 | series_store.EA_HICP_YOY | 1.3 | 1.3；字面「三个月上行 1.3 个百分点」 | 四舍五入一致(差 2.22e-16) | 一致 |
| P190 | EA_HICP_YOY 2026 年内新高月份=2026-10 | series_store.EA_HICP_YOY argmax(2026) | 2026-10-01 | 2026-10-01；字面「读数为年内新高」 | 等值比较 | 一致 |
| P191 | EA_HICP_YOY 2026-10 越过 2026-05 的 3.2 | series_store.EA_HICP_YOY | True | True；字面「越过 2026-05 的 3.2」 | 精确 | 一致 |
| P192 | 「为美欧两地最高水平」同月成立: EA(2026-09) > US CPI 同比(2026-09) | series_store EA_HICP_YOY vs CPI 同比 | True | True；字面「为美欧两地最高水平」；注: EA 最新为 2026-10, 其同月美国同比不可得(缺 2025-10 基期), 同月对照只能做到 2026-09; 逐月同月对照见探针 | 精确 | 一致 |
| P193 | 「读数水平低于欧元区」对最新有效同月成立: US CPI 同比(2026-09) < EA(2026-09) | series_store CPI 同比 vs EA_HICP_YOY | True | True；字面「但读数水平低于欧元区」 | 精确 | 一致 |
| P194 | EA_REAL_GDP_YOY@2026-04 | series_store.EA_REAL_GDP_YOY | 1.19 | 1.19；字面「2026Q2 为 1.19%」 | 四舍五入一致(差 0) | 一致 |
| P195 | EA_REAL_GDP_YOY@2026-07 | series_store.EA_REAL_GDP_YOY | 1.28 | 1.28；字面「2026Q3 为 1.28%」 | 四舍五入一致(差 0) | 一致 |
| P196 | EA_REAL_GDP_YOY 序列末观测=2026-07-01 | series_store.EA_REAL_GDP_YOY.dates[-1] | 2026-07-01 | 2026-07-01；字面「最新观测 2026-07-01」 | 等值比较 | 一致 |


**⑦机制链** — 独立复算 19 点(偏离 0)

| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |
|---|---|---|---|---|---|---|
| P197 | JP_POLICY_RATE 月均@2025-11 | series_store.JP_POLICY_RATE[2025-11-01] | 0.478 | 0.478；字面「自 2025-11 的 0.478」 | 四舍五入一致(差 0) | 一致 |
| P198 | JP_POLICY_RATE 月均@2025-12 | series_store.JP_POLICY_RATE[2025-12-01] | 0.557 | 0.557；字面「经 2025-12 的 0.557 抬升至 2026-10 的 1.227」 | 四舍五入一致(差 0) | 一致 |
| P199 | JP_POLICY_RATE 月均@2026-01 | series_store.JP_POLICY_RATE[2026-01-01] | 0.728 | 0.728；字面「2026-01 0.728」 | 四舍五入一致(差 0) | 一致 |
| P200 | JP_POLICY_RATE 月均@2026-04 | series_store.JP_POLICY_RATE[2026-04-01] | 0.727 | 0.727；字面「2026-04 0.727→2026-07 0.978」 | 四舍五入一致(差 0) | 一致 |
| P201 | JP_POLICY_RATE 月均@2026-06 | series_store.JP_POLICY_RATE[2026-06-01] | 0.841 | 0.841；字面「2026-06 0.841」 | 四舍五入一致(差 0) | 一致 |
| P202 | JP_POLICY_RATE 月均@2026-07 | series_store.JP_POLICY_RATE[2026-07-01] | 0.978 | 0.978；字面「3 个月前锚前值为 0.978(观测 2026-07)」 | 四舍五入一致(差 0) | 一致 |
| P203 | JP_POLICY_RATE 月均@2026-08 | series_store.JP_POLICY_RATE[2026-08-01] | 0.977 | 0.977；字面「2026-09 月均 0.977→1.043 仅 +7bp」 | 四舍五入一致(差 0) | 一致 |
| P204 | JP_POLICY_RATE 月均@2026-09 | series_store.JP_POLICY_RATE[2026-09-01] | 1.043 | 1.043；字面「2026-09 月均 0.977→1.043 仅 +7bp」 | 四舍五入一致(差 0) | 一致 |
| P205 | JP_POLICY_RATE 月均@2026-10 | series_store.JP_POLICY_RATE[2026-10-01] | 1.227 | 1.227；字面「JP_POLICY_RATE 月均最新一期(观测 2026-10)报 1.227%」 | 四舍五入一致(差 0) | 一致 |
| P206 | 政策一年窗内首观测=2025-12-01 | series_store.JP_POLICY_RATE 窗[2025-11-23..2026-11-23] | 2025-12-01 | 2025-12-01；字面「自 2025-12 月均起算」 | 等值比较 | 一致 |
| P207 | 政策窗净变动·引擎口径(窗首尾观测差) | (J[2026-10]−J[2025-12])×100 | 67 | 67；字面「净变动 +67bp」 | 四舍五入一致(差 0) | 一致 |
| P208 | 政策窗净变动·窗启时在值口径 | (J[2026-10]−J[2025-11])×100 | 74.9 | 75；字面「为 +75bp」 | 四舍五入一致(差 0.1) | 一致 |
| P209 | 政策窗净变动·中文数字写法(六十) | (J[2026-10]−J[2025-12])×100 | 67 | 67；字面「为正六十七个基点」 | 四舍五入一致(差 0) | 一致 |
| P210 | 政策窗净变动·中文数字写法(七十五) | (J[2026-10]−J[2025-11])×100 | 74.9 | 75；字面「为正七十五个基点」 | 四舍五入一致(差 0.1) | 一致 |
| P211 | 窗启时在值(中文数字写法零点四七八) | series_store.JP_POLICY_RATE[2025-11-01] | 0.478 | 0.478；字面「2025-11 月均零点四七八」 | 四舍五入一致(差 0) | 一致 |
| P212 | USDJPY@2026-11-23 | series_store.USDJPY[2026-11-23] | 159.347 | 159.35；字面「USDJPY 水平为 159.35(观测 2026-11-23」 | 四舍五入一致(差 0.003) | 一致 |
| P213 | USDJPY@2026-11-23(机制链) | series_store.USDJPY[2026-11-23] | 159.347 | 159.35；字面「USDJPY 最新报 159.35(观测 2026-11-23」 | 四舍五入一致(差 0.003) | 一致 |
| P214 | NIKKEI225 近一月涨跌幅(10-23→11-20) | series_store.NIKKEI225 | -9.97957 | -9.98；字面「NIKKEI225 近一月(2026-10-23→2026-11-20)下跌 9.98%」 | 四舍五入一致(差 0.000426) | 一致 |
| P215 | NIKKEI225 序列末观测=2026-11-20 | series_store.NIKKEI225.dates[-1] | 2026-11-20 | 2026-11-20；字面「NIKKEI225 止于 2026-11-20 收盘」 | 等值比较 | 一致 |


**⑨情景相容** — 独立复算 9 点(偏离 0)

| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |
|---|---|---|---|---|---|---|
| P308 | S1 触发: EA_HICP_YOY 4.0 未达阈值 4.2 | series_store.EA_HICP_YOY[2026-10-01] | False | False；字面「EA_HICP_YOY 同比 ≥4.2%」 | 精确 | 一致 |
| P309 | S1 触发: CORE_PCE 同比 3.12 未达阈值 3.2 | series_store.CORE_PCE 同比@2026-09 | False | False；字面「CORE_PCE 同比 ≥3.2%」 | 精确 | 一致 |
| P310 | S1 触发: TIPS_10Y 2.88 未高于 3.0 | series_store.TIPS_10Y[2026-11-19] | False | False；字面「TIPS_10Y 高于 3.0%」 | 精确 | 一致 |
| P311 | S1 证伪: EA 近两月未连续低于 3.0 | series_store.EA_HICP_YOY[2026-09,2026-10] | False | False；字面「连续两个月低于 3.0%」 | 精确 | 一致 |
| P312 | S2 触发: EA 未连续两月回落 | series_store.EA_HICP_YOY[2026-08..2026-10] | False | False；字面「EA_HICP_YOY 同比连续两个月回落」 | 精确 | 一致 |
| P313 | S2 触发: BEI_10Y 2.15 未低于 2.0 | series_store.BEI_10Y[2026-11-20] | False | False；字面「BEI_10Y 低于 2.0%」 | 精确 | 一致 |
| P314 | S2 证伪阈值所用月份(2026-12/2027-01)在截止日后=可观测未决 | series_store.EA_HICP_YOY.dates[-1] | 2026-10-01 | 2026-10-01；字面「2026-12 与 2027-01 两月 EA_HICP_YOY 同比均不低于 4.0%」 | 等值比较 | 一致 |
| P315 | S1 所需 CORE_PCE 后续同比基期(2025-10/2025-11)在场=可观测 | series_store.CORE_PCE[2025-10-01,2025-11-01] | True | True | 精确 | 一致 |
| P316 | S2 所述方向与近一月观察相反(实际利率 +11bp) | series_store.TIPS_10Y 10-20→11-19 | 11 | 11；字面「实际利率 +11bp 而风险资产回落」 | 四舍五入一致(差 1.24e-14) | 一致 |


**⑪缺席披露** — 独立复算 8 点(偏离 0)

| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |
|---|---|---|---|---|---|---|
| P272 | Gate A 状态 | snapshot.gate_a.status | DEGRADED | DEGRADED；字面「Gate A=DEGRADED」 | 等值比较 | 一致 |
| P273 | 核心缺口项数 | snapshot.gate_a.core_missing | 0 | 0；字面「核心缺口 零 项」 | 四舍五入一致(差 0) | 一致 |
| P274 | 非核心缺口清单(逐项一致) | snapshot.gate_a.noncore_missing | True | True；字面「非核心缺口 七 项(BUND_10Y、BUND_2Y、CN_OMO_7D、CN_POLICY_OVERNIGHT、EA_REAL_GDP_Y…」 | 精确 | 一致 |
| P275 | 非核心降级清单(逐项一致) | snapshot.gate_a.noncore_degraded | True | True；字面「非核心降级 八 项(CN_SF_FLOW、ECB_DFR、ECB_MRO、JTSJOL、M2SL、SPX_EPS、SPX_PE_TTM、US…」 | 精确 | 一致 |
| P276 | 判断档引用的非核心缺口指标集合 | agent_judgment(点值回显+证据引用) ∩ gate_a.noncore_missing | ["EA_REAL_GDP_YOY"] | ["EA_REAL_GDP_YOY"]；字面「本档引用的非核心缺口指标 一 项(EA_REAL_GDP_YOY)在序列库内有存量观测」 | 等值比较 | 一致 |
| P277 | EA_REAL_GDP_YOY 在 series_store 有存量观测 | snapshot.series_store.EA_REAL_GDP_YOY | True | True；字面「在序列库内有存量观测」 | 精确 | 一致 |
| P278 | 非核心缺口七项中不在 series_store 的序列 | snapshot.series_store | ["BUND_10Y", "BUND_2Y"] | ["BUND_10Y", "BUND_2Y"]；注: 其余五项在库内有存量观测(判断档披露块④已概括披露该引擎缺口), 见探针 | 等值比较 | 一致 |
| P279 | 计划指标中 US_REAL_GDP 属非核心降级 | snapshot.gate_a.noncore_degraded | True | True | 精确 | 一致 |


**⑬契约STALE** — 独立复算 14 点(偏离 0)

| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |
|---|---|---|---|---|---|---|
| P280 | STALE 项指标集合 | report.json agent_judgment.contract_verification.verdicts[status=STALE… | ["CORE_PCE", "US_REAL_GDP"] | ["CORE_PCE", "US_REAL_GDP"]；字面「引擎契约对两处引用标注 STALE」 | 等值比较 | 一致 |
| P281 | 契约 STALE 项数值与期望一致 | contract_verification.verdicts[STALE].value==expected | True | True；字面「数值一致」 | 精确 | 一致 |
| P282 | 契约面非 VERIFIED 项恰 2 项(与判断档「对两处引用标注 STALE」的项数一致) | contract_verification.verdicts 中非 VERIFIED 项数 | 2 | 2；字面「引擎契约对两处引用标注 STALE」 | 四舍五入一致(差 0) | 一致 |
| P283 | CORE_PCE 观测日 | series_store.CORE_PCE.dates[-1] | 2026-09-01 | 2026-09-01；字面「CORE_PCE(观测 2026-09-01，距截止日 83 天」 | 等值比较 | 一致 |
| P284 | CORE_PCE 观测距截止日天数 | 截止日 − 2026-09-01 | 83 | 83；字面「距截止日 83 天」 | 四舍五入一致(差 0) | 一致 |
| P285 | CORE_PCE 注册表最大日历滞后 | metric_registry CORE_PCE.max_calendar_lag_days | 60 | 60；字面「最大日历滞后 60 天的 1.4 倍」 | 四舍五入一致(差 0) | 一致 |
| P286 | CORE_PCE 滞后倍数 | 83/60 | 1.38333 | 1.4；字面「60 天的 1.4 倍」 | 四舍五入一致(差 0.0167) | 一致 |
| P287 | US_REAL_GDP 观测日 | series_store.US_REAL_GDP.dates[-1] | 2026-07-01 | 2026-07-01；字面「US_REAL_GDP(观测 2026-07-01，距截止日 145 天」 | 等值比较 | 一致 |
| P288 | US_REAL_GDP 观测距截止日天数 | 截止日 − 2026-07-01 | 145 | 145；字面「距截止日 145 天」 | 四舍五入一致(差 0) | 一致 |
| P289 | US_REAL_GDP 注册表最大日历滞后 | metric_registry US_REAL_GDP.max_calendar_lag_days | 120 | 120；字面「最大日历滞后 120 天的 1.2 倍」 | 四舍五入一致(差 0) | 一致 |
| P290 | US_REAL_GDP 滞后倍数 | 145/120 | 1.20833 | 1.2；字面「120 天的 1.2 倍」 | 四舍五入一致(差 0.00833) | 一致 |
| P291 | CORE_PCE 最新观测=截止日前最新已发布(发布日 2026-10-30≤截止日) | series_store.CORE_PCE + 发布纪律 | 2026-10-30 | 2026-10-30；字面「两者均为该序列在截止日前的最新已发布观测」 | 等值比较 | 一致 |
| P292 | US_REAL_GDP 发布日 | series_store.US_REAL_GDP + 发布纪律(季末+29) | 2026-10-29 | 2026-10-29 | 等值比较 | 一致 |
| P293 | CORE_PCE 2026-10 观测不在序列(故最新为 2026-09) | series_store.CORE_PCE[2026-10-01] | False | False | 精确 | 一致 |


**证据引用** — 独立复算 11 点(偏离 0)

| 编号 | 复算点 | 出处键 | 直算值 | 报告值/受审字面 | 比对方式 | 结果 |
|---|---|---|---|---|---|---|
| P294 | 证据索引行数 | evidence_index.json | 63 | 63；字面「证据索引(63行)」 | 四舍五入一致(差 0) | 一致 |
| P295 | 证据引用总数 | agent_judgment.json 全部 evidence_refs | 19 | 19；字面「证据引用共 19 条」 | 四舍五入一致(差 0) | 一致 |
| P296 | 矛盾陈述证据引用数 | l3.contradictions[*].evidence_refs | 10 | 10；字面「(矛盾陈述 10、机制链 4、情景 5)」 | 四舍五入一致(差 0) | 一致 |
| P297 | 机制链证据引用数 | l3.mechanism_chains[*].links[*].evidence_refs | 4 | 4；字面「(矛盾陈述 10、机制链 4、情景 5)」 | 四舍五入一致(差 0) | 一致 |
| P298 | 情景证据引用数 | l4.scenarios[*].asset_direction.evidence_refs | 5 | 5；字面「(矛盾陈述 10、机制链 4、情景 5)」 | 四舍五入一致(差 0) | 一致 |
| P299 | 全部引用均在证据索引 | agent_judgment evidence_refs vs evidence_index.json | [] | []；字面「全部解析到本轮冻结快照」 | 等值比较 | 一致 |
| P300 | 全部引用观测日≤截止日 | agent_judgment evidence_refs | [] | [] | 等值比较 | 一致 |
| P301 | 全部引用在 series_store 该日有值 | agent_judgment evidence_refs vs snapshot.series_store | [] | [] | 等值比较 | 一致 |
| P302 | 机制链证据级标注 | l3.mechanism_chains[0].links[*].evidence_level | E1/E2/E2 | E1/E2/E2；字面「机制链三环证据分级 E1/E2/E2」 | 等值比较 | 一致 |
| P303 | 各矛盾陈述并列解释数 | l3.contradictions[*].competing_explanations | 2/2/2 | 2/2/2；字面「各并列 2、2、2 种解释」 | 等值比较 | 一致 |
| P304 | 情景数 | l4.scenarios | 2 | 2 | 四舍五入一致(差 0) | 一致(结构性自检,不计入) |
| P305 | 情景期限 | l4.scenarios[*].rows.trigger.deadline | 2027-02-15/2027-02-15 | 2027-02-15/2027-02-15；字面「期限均为 2027-02-15」 | 等值比较 | 一致 |
| P306 | 历史段数=0 | reader_map.history_periods | 0 | 0 | 四舍五入一致(差 0) | 一致(结构性自检,不计入) |
| P307 | 转折数 | reader_map.turnings | 3 | 3 | 四舍五入一致(差 0) | 一致(结构性自检,不计入) |

## 二、工单专项核验(规程 §3 末项)与交付门缺口(⑭)

| 对象 | 3 个月前锚 | 最新一期锚 | 变化方向 | 出处 |
|---|---|---|---|---|
| 美国·增长 | 实际 GDP 同比 2.19%@2026Q2(水平 24408.011);失业率 4.1@2026-07;工业生产同比 1.25%@2026-07(水平 103.1675) | 2.07%@2026Q3(24611.077);4.1@2026-10;2.15%@2026-10(103.3954) | GDP 同比微降;失业率持平;工业同比回升(水平端点 +0.22%) | series_store.US_REAL_GDP / UNEMPLOYMENT / INDPRO |
| 美国·通胀 | CPI 同比 3.30%@2026-07(指数 332.813);核心 CPI 同比 2.47%@2026-07(336.789);核心 PCE 同比 3.04%@2026-06(129.969) | 3.72%@2026-09(指数 337.476@2026-10,同比缺基期);2.57%@2026-09(339.9@2026-10);3.12%@2026-09(130.902) | 同向上行 | series_store.CPI / CORE_CPI / CORE_PCE |
| 欧元区·增长 | 实际 GDP 同比 1.19%@2026Q2 | 1.28%@2026Q3 | 微升 | series_store.EA_REAL_GDP_YOY |
| 欧元区·通胀 | HICP 同比 2.9%@2026-07 | 4.0%@2026-10 | 上行 1.1 个百分点 | series_store.EA_HICP_YOY |
| 日本·政策利率 | 月均 0.978@2026-07 | 月均 1.227@2026-10;官方目标 1.25(2026-09-18 决议、2026-09-24 生效、2026-10-30 确认维持) | 上行;距上次调整 60 天(按生效日)/66 天(按决议日)/距维持 24 天 | series_store.JP_POLICY_RATE;calendar RC-JP-BOJ-TARGET-2026-09 / RC-JP-BOJ-MAINT-2026-10 |

日本政策利率水平的口径分列核对: 官方目标(JP_POLICY_TARGET,注册表与 series_store 均无,仅见冻结日历 target_value=1.25)与市场月均(JP_POLICY_RATE,value_type=monthly_avg_rate)在判断档与读者报告政策四分面表中分列,无相邻口径冒充;待生效决定=无(日历政策类条目仅 2 条,生效日均不晚于截止日)。

交付门: FULL_REPORT.md 载「run 门(Audit-R4 条目5): blocked_class=None degraded_ok=False」,report.json run_ok=true、semantic_review.required=true(理由 l3_qualitative_inference / l4_conditional_scenarios)且 seat_invoked=false、verdict=null——即裁决缺席状态,无草稿判定。判断档对相关缺口的披露与序列面/冻结日历一致: 缺数(9 个计划指标 11 月窗口覆盖不足→引擎 notes 列为「地图计划指标缺数(披露不阻断)」);缺官方记录(JP_POLICY_TARGET 注册表缺席 P037/P038,冻结日历无美欧决议条目 P019–P021);过期(契约 STALE 2 项=CORE_PCE 83 天/上限 60 天、US_REAL_GDP 145 天/上限 120 天,P280–P290);降级(Gate A=DEGRADED,核心缺口 0、非核心缺口 7、非核心降级 8,逐项一致 P272–P275)。未发现把缺席写成「无变化」、或把序列值写成官方宣布目标的情形(JP 月均 1.227 与官方目标 1.25 分列)。

补充(攻击探针,不计入复算点): 冻结快照内美欧政策利率序列 series_store.DFEDTARU/DFEDTARL 于 2026-09-17 由 3.75/3.50 升至 4.00/3.75,ECB_DFR/ECB_MRO 于 2026-09-16 由 2.25/2.40 升至 2.50/2.65(变更点直算);12 个月窗端点 2025-11-19→2026-11-19 DFEDTARU 4.00→4.00 净变动 0,三个月窗 2026-08-19→2026-11-19 +25bp。该两组序列不在本问 9 个计划指标内(读者报告转折候选面载「本问计划指标面未纳入美欧政策利率序列」)。

## 三、六查逐项结论(规程 §4)

**C1-INFL-SYNC**

- 证据相关性: 相符。EA_HICP_YOY、CPI、CORE_CPI、CORE_PCE、BEI_10Y 均为问句「通胀环境」的在册序列;5 条证据引用全部解析到冻结快照(P296/P299–P301)。
- 支持度: 「同步走高、欧元区幅度更大」与直算相符(欧元区 +1.1 个百分点;美国 CPI 同比 +0.41、核心 CPI +0.10、核心 PCE +0.08 个百分点);「为美欧两地最高水平」属跨月比较(MINOR);「headline 强于核心」相符(3.72 对 2.57)。
- 竞争解释: 2 条,均为【假设】条件式(成本/进口持续传导 对 一次性基数/扰动),对「同比是否自行回落」给出不同预期,属真正竞争;第 2 条已纳入近一月 BEI_10Y -19bp 的反向事实。
- 反对证据: 美国 2026-10 同比缺基期(已披露);BEI_10Y 三窗下行(已在竞争解释与传导链第 1 环披露)。
- 结论是否超出证据: 否。
- 证伪条件可观测性: 由情景 S1/S2 承担,指标在册、阈值可观测(见情景项)。

**C2-GROWTH-STABLE**

- 证据相关性: 相符。US_REAL_GDP、UNEMPLOYMENT、INDPRO 为问句「增长环境」的在册序列;3 条证据引用全部解析(P296/P299–P301)。
- 支持度: 「大体平稳、并非主导变化」相符(美国 GDP 同比 2.19%→2.07%、欧元区 1.19%→1.28%,变动在 0.1 个百分点量级,远小于通胀端欧元区 +1.1 个百分点)。
- 竞争解释: 2 条(制造业周期回暖 对 基数效应/单月波动),方向相反,属真正竞争。
- 反对证据: INDPRO 2026-10 环比 -0.43% 与同比基期下行未在正文披露(仅以竞争解释(2)的假设形式出现)→ MINOR。
- 结论是否超出证据: 否。
- 证伪条件可观测性: 描述性陈述,不适用。

**C3-JP-POLICY**

- 证据相关性: 相符。JP_POLICY_RATE 月均在册;官方目标仅见冻结日历条目,判断档已分列且不以相邻口径冒充(走位文字明写「不以相邻口径冒充宣布值」)。
- 支持度: 目标 1.25、决议/生效/维持三日期、60/66/24 天、+67/+75bp 全部直算一致;「官方目标与市场口径相互印证」成立(1.25 对月均 1.227)。
- 竞争解释: 2 条——(1) 月均台阶含均值效应与季节性;(2) 须以决议日历为准、下月是否有新决议未验证。是对「月均读数=连续上调」读法的有效约束,属真正竞争。
- 反对证据: 决议后 USDJPY 上行(+2.06%)已在机制链第 3 环披露;无未披露的反向事实。
- 结论是否超出证据: 否。
- 证伪条件可观测性: 「下月是否有新决议尚未验证」可由冻结日历后续条目观测。

**机制链 M1-JP-RATE-PATH**

- 证据级: E1/E2/E2 标注与内容相称(第 1 环全为月均序列直算值;第 2 环明写【假设】与缺环注记;第 3 环为资产面观测+条件推断,并附多因子缺环注记)。
- 环内数字: 第 1 环 0.478/0.557/0.728/0.841/0.978/1.043/1.227、+67/+75bp,第 3 环 USDJPY 159.35、NIKKEI225 -9.98%,全部回贴一致(P197–P199、P201–P208、P212–P215);另核判断档他处所引 0.727(2026-04,转折候选面)与 0.977(2026-08,C3 竞争解释),一致(P200/P203)。
- 竞争解释/反对证据: 「若加息传导单一成立,应见 USDJPY 走低」被 USDJPY 高位(决议日以来 +2.06%)否定,链结论如实收为「混合态、证据不单一」。
- 结论是否超出证据: 否。
- 证伪条件可观测性: 链内给出可观测对照(USDJPY 方向与股指),未单设情景。

**传导链 CH-INFL-RATES-RISKOFF(读者对质面)**

- 第 1 环(BEI_10Y): 预期分立(走高/高位 对 走低/持平),观测在场;本问三窗同向合竞争解释,更早 2026-02→2026-05 段合主解释;裁定「尚不能区分」保守、首句措辞与行内观测部分不符(MINOR),未超出证据。
- 第 2 环(TIPS_10Y 对名义利率): 预期不分立(竞争解释原文同样容纳「通胀走高而盈亏平衡回落」);主解释前件本环未举证(快照内美欧政策利率序列 2026-09 各 +25bp 可作支持,但 12 个月窗 DFEDTARU 净变动 0);裁定「支持主解释」超出证据 → MAJOR。
- 第 3 环(TIPS_10Y 对 SPX): 预期分立(TIPS 上行 对 走低),观测在场(TIPS_10Y: 本月窗 +22bp(2026-10-23→2026-11-19)、近一月窗 +11bp(2026-10-20→2026-11-19)、三个月窗 +53bp(2026-08-19→2026-11-19);SPX 同起点窗: 2026-10-23→2026-11-23 为 -5.51%、2026-10-23→2026-11-19 为 -5.87%、2026-08-19→2026-11-20 为 -10.35%),流动性叠加已标注;裁定成立。

**情景 S1-INFL-STICKY / S2-INFL-FADE**

- 两情景方向互补(延续 对 回落),非孤证;阈值指标 EA_HICP_YOY/CORE_PCE/BEI_10Y/TIPS_10Y 均在册;期限 2027-02-15 在截止日后(P305)。
- 与截止日读数相容: 均未触发、亦未被证伪(见反方攻击 11);S1 所需核心 PCE 后续同比基期在场=可观测(P315)。
- S2 的置信档标「纯逻辑推理」偏保守(三窗 BEI_10Y 下行实为其相关证据),无害。

## 四、反方攻击记录

- **反方攻击 1(C1-INFL-SYNC)** 美国 CPI 2026-10 同比是否以相邻月基期凑数冒充? → 否。判断档明写「因缺上年同月基期观测不可得」;series_store.CPI 无 2025-10-01 观测(P137);若以相邻基期硬算为 4.08(基期取 2025-09)或 3.82(基期取 2025-11),判断档中均无此二数;所引最近有效同比 3.72=series_store 直算 3.7173(2026-09,P130)。
- **反方攻击 2(C1-INFL-SYNC)** 「欧元区为两地最高水平」是否与序列相左? → 部分成立。同月口径 2026-07(欧元区 2.9/美国 3.30)与 2026-08(3.2/3.35)美国更高,仅 2026-09(3.8/3.72)起欧元区居首;原句未注明跨月与窗内交叉→列 MINOR,非 MAJOR(最新读数位次属实)。
- **反方攻击 3(C1-INFL-SYNC)** 「同步走高、欧元区幅度更大」是否只成立于一侧? → 否。欧元区 2.9→4.0(+1.1 个百分点,2026-07→2026-10),美国 CPI 同比 3.30→3.72(+0.41,2026-07→2026-09)、核心 CPI 2.47→2.57(+0.10)、核心 PCE 3.04→3.12(+0.08,2026-06→2026-09);成立。
- **反方攻击 4(C2-GROWTH-STABLE)** 增长面是否实际走弱而被写成平稳? → 否。美国实际 GDP 同比 2.19→2.07、水平 2026Q3 较 Q2 +0.83%,失业率 4.1→4.1(其间 2026-09 为 4.2),欧元区 GDP 同比 1.19→1.28;「大体平稳」成立。但 INDPRO 2026-10 环比 -0.43%、同比抬升含基数效应(基期 2025-07→2025-10 -0.66%),「工业回升」披露不足→列 MINOR。
- **反方攻击 5(C3-JP-POLICY)** 官方目标 1.25 是否为序列值冒充?距上次调整天数是否按错日起算? → 否。JP_POLICY_TARGET 不在注册表与 series_store(P037/P038),1.25 仅出自冻结日历 RC-JP-BOJ-TARGET-2026-09.target_value(P024);生效日 2026-09-24→截止日 60 天、决议日 2026-09-18→66 天、维持会 2026-10-30→24 天(P030/P031/P034),逐日直算一致;月均口径 1.227 另列并注明非宣布值(P039/P205)。
- **反方攻击 6(C3-JP-POLICY)** 12 个月净变动 +67bp/+75bp 是否与月均序列不符? → 否。2025-12 0.557→2026-10 1.227=+67.0bp(P207);2025-11 0.478→1.227=+74.9bp(P208);六级台阶(引擎变动点记法 +8/+17/+11/+14/+7/+18bp)与月均序列逐月差(7.9/17.1/11.4/13.7/6.6/18.4bp)取整一致。
- **反方攻击 7(机制链 M1-JP-RATE-PATH)** 加息后日元是否走强而与「USDJPY 仍处高位」相左?E2 环是否以事实位措辞出现? → 否。USDJPY 决议日 2026-09-18 156.129→2026-11-23 159.347(+2.06%),与判断档「USDJPY 仍处高位」一致;第 2、3 环归 E2 并明写【假设】与缺环注记(引擎无融资成本/套息序列);链结论「传导方向证据不单一」与 USDJPY 上行、NIKKEI225 -9.98%(P214)的组合相称。
- **反方攻击 8(传导链第 1 环 BEI_10Y)** 「尚不能区分」是否掩盖了本问三窗一致合竞争解释? → 部分成立:三窗 -19/-14/-11bp(P223/P228/P233)同向且 2.15 为 12 个月窗最低;「各窗方向不一致」措辞不准确,更早上行段端点取极值点(+25bp,月对齐替代端点约 +3~+14bp)→列 MINOR(裁定方向保守,未超出证据)。
- **反方攻击 9(传导链第 2 环 TIPS_10Y 对名义利率)** 竞争预期是否稻草人、主解释前件是否有证据? → 成立:竞争解释原文同样容纳「通胀走高而盈亏平衡回落」组合,预注册的「无稳定主导关系」非其推论;冻结日历无美欧决议条目(P019–P021)、政策事件簇为空(P017);快照内美欧政策利率序列显示 2026-09-17、2026-09-16 各 +25bp(前件有支持,但本环未引用)→裁定「支持主解释」超出证据,列 MAJOR。
- **反方攻击 10(传导链第 3 环 TIPS_10Y 对 SPX)** 同现是否等于因果、窗口是否错配? → 竞争解释原文对「增长担忧」与「仓位/流动性冲击」两变体均预期 TIPS_10Y 走低,与观测 +22bp(2026-10-23→2026-11-19,P241)/+11bp(P222)/+53bp(P227)相反,预期分立且观测在场,裁定成立;SPX 取同日收盘口径(2026-10-23→2026-11-19)为 -5.87%,方向不变;流动性叠加的限定已在 observed_fact 写明。无 MAJOR。
- **反方攻击 11(情景 S1/S2)** 触发条件在截止日是否已触发或前提已被证伪? → 否。EA_HICP_YOY 2026-10=4.0 未达 S1 触发 4.2(P308),CORE_PCE 同比 3.12 未达 3.2(P309),TIPS_10Y 2.88 未高于 3.0(P310);S1 证伪条件(连续两月低于 3.0)未满足(P311);S2 触发(连续两月回落且 ≤3.4、BEI_10Y<2.0)未满足(P312/P313);S2 证伪所需 2026-12/2027-01 两月尚未发布(P314);期限 2027-02-15 在截止日后=待决(P305)。
- **反方攻击 12(总判断/读者报告)** 判断文字在读者报告中是否被改动,或与数值面冲突? → 52 个判断文字字段逐字核对:MAP_REPORT.md 35 个、FULL_REPORT.md 17 个在位,未发现改写;6 个未渲染(3 个 verdict_note=判断档已披露;3 个 turnings.narrative=未披露,属引擎渲染面)。对质表第 2 行「支持主解释」即 MAJOR 所在;头条结论的数值与方向均与复算一致。
- **反方攻击 13(对本席 MAJOR 的反向检验·传导链第 2 环)** 美欧央行若在窗内加息,主解释是否即获支持、裁定应否成立? → 前件有支持: 快照内 DFEDTARU/DFEDTARL 2026-09-17 +25bp、ECB_DFR/ECB_MRO 2026-09-16 +25bp(三个月窗 DFEDTARU +25bp);但 12 个月窗 DFEDTARU 4.00→4.00 净变动 0 而同窗 TIPS_10Y +102bp,且前件成立并不使两侧在区分指标上的预期分立——MAJOR 结论不变;本席初稿「前件在证据面无记录」的表述经此检验更正为「本环未引用」。

## 五、问题清单

### MAJOR(1)

1. **agent_judgment.json reader_map.transmission[CH-INFL-RATES-RISKOFF].links[1](区分指标 TIPS_10Y)的 face_off_verdict / competing_predicts / observed_fact 末段 / verdict_note;连带 quality_gate_notes[1];读者面 MAP_REPORT.md「主解释 vs 竞争解释(对质表)」TIPS_10Y 第 1 行**

   - 对质裁定「支持主解释」超出证据(规程 §4:竞争解释须在列且真正竞争、同证据可容纳、非稻草人,且两解释在区分指标上的预言方向须确实不同;§3⑩:对质表判断须与该行观测及报告自述口径一致)。
   - ①同环竞争解释原文「若名义利率走势主要由增长前景、期限溢价或财政供给主导,则实际分量与通胀读数可以背离(通胀走高而盈亏平衡回落即属此类组合)。
   - 」——按名义=实际+盈亏平衡的恒等关系,「通胀走高而盈亏平衡回落」而名义利率上行时,上行只能来自实际分量,即该解释对区分指标 TIPS_10Y 的推论同样是实际上行主导;预注册的竞争预期「竞争解释(期限溢价/供给主导)预期 TIPS_10Y 与 BEI_10Y 组合无稳定主导关系」不是该解释文字的推论,属稻草人。
   - 判断档自己在同环注中写明「「通胀走高而盈亏平衡回落」的组合与竞争解释的文字描述亦相容，该描述不构成两侧的区分预期，裁定只针对预注册的区分预期。
   - 」——即承认两解释预期未分立,却仍依自设的「预注册区分预期」作单侧裁定。
   - ②读者报告自述裁定口径(MAP_REPORT.md「判断口径」行):「判断口径: 预期分立(两解释对同一指标给出不同预期)且引擎面观测在场才可裁;观测缺席或预期未分立=**尚不能区分**(诚实缺省,不以单侧证据裁)。
   - 」——本环预期未分立,按该口径只能是尚不能区分。
   - ③主解释前件(央行紧缩偏向)本环未举证,但证据面对其并非空白:冻结快照 series_store.DFEDTARU/DFEDTARL 于 2026-09-17 由 3.75/3.50 升至 4.00/3.75(+25bp),ECB_DFR/ECB_MRO 于 2026-09-16 由 2.25/2.40 升至 2.50/2.65(+25bp);读者报告政策表注亦载「Fed…2026-09 决议 09-16→生效 09-17」「ECB…2026-09 决议 09-10→生效 09-16」,另载「本问计划指标面未纳入美欧政策利率序列」;且 12 个月窗端点(2025-11-19→2026-11-19)DFEDTARU 4.00→4.00 净变动为 0(其间 2025-12-11 降至 3.75)而同窗 TIPS_10Y +102bp——该窗对主解释并无独特支持。
   - 前件成立与否都不改变①②:两解释在区分指标上预期未分立,单侧裁定不成立。
   - ④三窗数字本身直算无误(近一月 2026-10-20→2026-11-19 实际 +11bp/盈亏平衡 -19bp/名义 -8bp;三个月 2026-08-19→2026-11-19 +53/-14/+39bp;12 个月 2025-11-19→2026-11-19 +102/-11/+91bp;出处 series_store.TIPS_10Y/BEI_10Y/UST_10Y),问题只在裁定与竞争预期的写法;verdict_note 称「主导关系稳定」亦未计入单月窗名义变动由盈亏平衡主导(-19bp 对 +11bp)。
   - ⑤连带 quality_gate_notes[1]「3 环均给出…不同预期」与计数「尚不能区分 ×1、支持主解释 ×2」随之不实。

   必修(原句 → 改句):

   1. 【传导链第 2 环 face_off_verdict】原句: 「支持主解释」 → 改句: 「尚不能区分」
   2. 【传导链第 2 环 competing_predicts】原句: 「竞争解释(期限溢价/供给主导)预期 TIPS_10Y 与 BEI_10Y 组合无稳定主导关系」 → 改句: 「竞争解释(增长前景/期限溢价/财政供给主导)同样预期 TIPS_10Y 上行主导名义利率变动、可与盈亏平衡回落并存，两解释在区分指标 TIPS_10Y 上预期方向不分立」
   3. 【传导链第 2 环 observed_fact 末段】原句: 「三个月、近一月、12 个月三窗均为「实际利率上行、盈亏平衡回落」，不合竞争解释「无稳定主导关系」的预期，这是「实际利率为名义利率主导上行分量」的证据来源；单月窗内名义利率下行、盈亏平衡变动幅度大于实际利率，单看单月窗不足以支持该主张。注: 「通胀走高而盈亏平衡回落」的组合与竞争解释的文字描述亦相容，该描述不构成两侧的区分预期，裁定只针对预注册的区分预期。」 → 改句: 「三个月、近一月、12 个月三窗均为「实际利率上行、盈亏平衡回落」(实际 +53/+11/+102bp、盈亏平衡 -14/-19/-11bp)，名义利率上行由实际利率分量主导；但增长前景/期限溢价/财政供给主导同样预期 TIPS_10Y 上行，两解释在区分指标 TIPS_10Y 上的预期方向不分立(单月窗名义 -8bp 由盈亏平衡 -19bp 主导，亦不构成任一侧的区分证据)——尚不能区分。」
   4. 【传导链第 2 环 verdict_note(与裁定同步)】原句: 「三个月窗实际 +53bp 主导名义 +39bp、12 个月窗实际 +102bp 主导名义 +91bp，合主解释；三窗均为实际上行、盈亏平衡回落，主导关系稳定；单月窗 TIPS_10Y +11bp 为唯一上行分量但幅度小于盈亏平衡 -19bp(名义 -8bp)，单月窗不足以单独支持——裁定基于三个月窗与 12 个月窗，单月窗证据有限。」 → 改句: 「三个月窗实际 +53bp 主导名义 +39bp、12 个月窗实际 +102bp 主导名义 +91bp，名义上行确由实际利率分量主导；但期限溢价/财政供给/增长前景主导同样预期该组合，两解释在 TIPS_10Y 上预期方向不分立——尚不能区分；单月窗名义 -8bp(实际 +11bp、盈亏平衡 -19bp)不构成任一侧的区分证据。」
   5. 【quality_gate_notes[1]】原句: 「传导面 3 环均给出主/竞争两侧对同一区分指标的不同预期，判断=尚不能区分 ×1、支持主解释 ×2」 → 改句: 「传导面 3 环均列出主/竞争两侧预期，其中贴现率渠道环(区分指标 TIPS_10Y 相对 SPX)两侧预期分立且有在场观测，判断=支持主解释 ×1；另 2 环(BEI_10Y、TIPS_10Y 对名义利率)判断=尚不能区分 ×2」

### MINOR(6)

1. **agent_judgment.json reader_map.transmission[0].links[0](区分指标 BEI_10Y) observed_fact 首段与 face_off_verdict** — 「区分指标 BEI_10Y 在各窗方向不一致」与本问三窗不符:近一月(2026-10-20→2026-11-19)-19bp、三个月(2026-08-19→2026-11-19)-14bp、12 个月(2025-11-19→2026-11-19)-11bp 方向一致向下(series_store.BEI_10Y),最新 2.15(2026-11-20)为 12 个月窗内最低(截至最新观测的 365 天窗 2025-11-20..2026-11-20 内 251 个有效观测,区间 2.15–2.50,中位 2.32);「不一致」只在与本问窗口之外的 2026-02→2026-05 段(2026-02-27 2.25→2026-05-04 2.50,+25bp)并列时出现,且该段两端取的是局部低点与 12 个月高点(按月对齐的替代端点:2026-02-02→2026-05-29 约 +3bp、2026-01-30→2026-04-30 约 +10bp、2026-02-27→2026-05-29 约 +13bp、2026-02-27→2026-05-27 约 +14bp)。按预注册两侧预期(主=走高或维持高位;竞争=走低或持平),本问三窗均合竞争解释;「尚不能区分」所依据的另一根支柱是 L3 竞争解释中「同比数月内自行回落」一半尚未兑现——那是关于通胀读数而非区分指标的预期。裁定偏保守、未超出证据,但与第 2 环的裁定尺度不对称(两处不对称均有利于主解释)。不改变头条结论,列 MINOR。
   - 原句: 「区分指标 BEI_10Y 在各窗方向不一致」
   - 改句: 「区分指标 BEI_10Y 在本问三窗方向一致向下(近一月 -19bp、三个月 -14bp、12 个月 -11bp，最新 2.15 为 12 个月窗最低)，均合竞争解释「走低或持平」;更早的 2026-02→2026-05 上行段(2.25→2.50)合主解释——尚不能区分」
2. **agent_judgment.json l3.contradictions[C1-INFL-SYNC].statement** — 「为美欧两地最高水平」是跨月比较:欧元区 EA_HICP_YOY 取 2026-10(4.0),美国 CPI 同比最近有效为 2026-09(3.7173,2026-10 缺基期)。同月口径下 2026-09 为 3.8 对 3.72(成立,差 0.08 个百分点),但 2026-07 为 2.9 对 3.30、2026-08 为 3.2 对 3.35(美国更高)(series_store.EA_HICP_YOY 与 CPI 同比直算)——该位次是三个月窗内才发生的交叉,建议注明口径。
   - 原句: 「欧元区 EA_HICP_YOY 最新读数明显走高、为美欧两地最高水平(数值与观测月见走位对照)」
   - 改句: 「欧元区 EA_HICP_YOY 最新读数明显走高、水平高于美国(数值与观测月见走位对照;两地最新可比同月 2026-09: 欧元区 3.8、美国 3.72;2026-07 与 2026-08 美国更高,位次在窗内交叉)」
3. **agent_judgment.json reader_map.headline_conclusion 与 regions[US].from_to(「工业回升」/「工业动能回升」);l3.contradictions[C2-GROWTH-STABLE]** — 「工业回升」依赖同比(1.25→2.15)而水平端点仅 +0.22%(INDPRO 2026-07 103.1675→2026-10 103.3954),其中 2026-09→2026-10 环比 -0.43%(103.8458→103.3954),且同比基期同期下行(2025-07 101.894→2025-10 101.2195,-0.66%),同比抬升含基数效应(series_store.INDPRO);判断档仅在 C2 竞争解释(2)中以假设形式提及。结论「增长面大体平稳」不受影响。
   - 原句: 「工业回升」
   - 改句: 「工业生产同比回升(水平较 3 个月前 +0.22%，2026-10 环比回落 0.43%，同比抬升含基数效应)」
4. **agent_judgment.json quality_gate_notes(数据面披露块)** — report.json run.data_requirements.items 显示 9 个计划指标对任务窗口 2026-11-01..2026-11-30 的 spec.window.n_in_window 均为 0、outcome 均为 insufficient_coverage(截止日 2026-11-23 尚无 11 月观测);读者报告页眉已披露「该月末完整结果须待数据覆盖后重跑」,但判断档 6 条披露注均未提及。建议补一句。
   - (原句: 无,属应补未补的披露)
   - 改句: 「补充: 「任务窗口 2026年11月 的 9 个计划指标在截止日窗内观测数为 0(均为覆盖不足)，本档以截止日前最新已发布观测与 3 个月前锚作答，11 月完整结果须待数据覆盖后重跑」」
5. **agent_judgment.json l3.contradictions[C3-JP-POLICY].competing_explanations[1]** — 「2026-09 月均 0.977→1.043 仅 +7bp」中 0.977 是 2026-08 月均(series_store.JP_POLICY_RATE[2026-08-01]=0.977;[2026-09-01]=1.043),写法沿用了引擎政策路径面板的变动点记法(MAP_REPORT.md 政策一年窗路径行「2026-09-01: 0.977→1.043(+7bp)」)。数值与 +7bp 无误,月份标注易误读为 9 月月均自 0.977 变至 1.043。
   - 原句: 「2026-09 月均 0.977→1.043 仅 +7bp」
   - 改句: 「2026-08 月均 0.977→2026-09 月均 1.043 仅 +7bp」
6. **agent_judgment.json quality_gate_notes(数据面/契约 STALE 披露);reader_map.regions[EA].from_to** — 披露不对称两项:①EA_REAL_GDP_YOY 最新观测 2026-07-01 距截止日 145 天,注册表 freshness.max_calendar_lag_days=120(约 1.2 倍),与按 STALE 披露的 US_REAL_GDP(同为 2026-07-01 观测、145 天、上限 120 天)同龄同倍数,但判断档只在 Gate A 非核心缺口清单中提及该指标,未按同一过期口径披露;②「2026-10 同比不可得(缺 2025-10 基期)」只对 CPI 披露,CORE_CPI 同样缺 2025-10 观测(series_store.CORE_CPI dates: 2025-09-01 之后直接为 2025-11-01),走位文字只以「最近有效 2026-09」带过。
   - 原句: 「美国 CPI 2026-10 同比缺 2025-10 基期(当月同比不可得)」
   - 改句: 「美国 CPI 与核心 CPI 2026-10 同比均缺 2025-10 基期(当月同比不可得)」

### NIT(10)

1. **agent_judgment.json reader_map.turnings[EA_HICP_YOY].narrative(该字段不进读者报告渲染)** — 「其间 2026-06 回落至 2.8」:2026-06 在 2026-02→2026-05 上行段之后,应为「其后」(同条 follow_or_diverge 的写法正确;series_store.EA_HICP_YOY[2026-06-01]=2.8)。
   - 原句: 「其间 2026-06 回落至 2.8 后再度上行」
   - 改句: 「其后 2026-06 回落至 2.8 后再度上行」
2. **agent_judgment.json l3.contradictions[C2-GROWTH-STABLE].competing_explanations[1]** — INDPRO 为物量指数,「价格与基数效应」中的「价格」不适用。
   - 原句: 「价格与基数效应或单月波动」
   - 改句: 「基数效应或单月波动」
3. **agent_judgment.json l3.contradictions[C2-GROWTH-STABLE].competing_explanations[0]** — 该条无【假设】标记(其余 5 条并列解释均有);「2026 年三季度后段」而所引最新读数为 2026-10(四季度)。
   - 原句: 「增长动能在 2026 年三季度后段重新加速」
   - 改句: 「【假设】…增长动能重新加速(所引最新读数为 2026-10)」
4. **agent_judgment.json reader_map.transmission[0].links[2].verdict_note(该字段不进渲染)** — verdict_note 写「本月窗口 TIPS_10Y +11bp 与 SPX -5.51% 同现」:+11bp 是 2026-10-20→2026-11-19 窗,SPX -5.51% 是 2026-10-23→2026-11-23 窗;observed_fact 用的是同窗起点的 +22bp(2026-10-23→2026-11-19)。两数各自无误,窗口不同。
   - 原句: 「本月窗口 TIPS_10Y +11bp 与 SPX -5.51% 同现」
   - 改句: 「本月窗口 TIPS_10Y +22bp(2026-10-23→2026-11-19)与 SPX -5.51%(2026-10-23→2026-11-23)同现」
5. **读者报告渲染(引擎面,供操作席参考,非判断档缺陷)** — reader_map.turnings[*].narrative 三个字段在 MAP_REPORT.md / FULL_REPORT.md / report.md 均未渲染(逐字段字面核对 52 个判断文字字段:MAP 35 个、FULL 17 个、两份皆无 6 个=3 个 verdict_note+3 个 narrative);判断档披露注⑤③只说明 verdict_note 不进渲染。narrative 中的限定语因此到不了读者。
6. **agent_judgment.json l4.scenarios(S1 触发条件与 S2 证伪阈值)** — S1 用发布月口径(「2026-12 或 2027-01 发布的」),S2 用裸月份(「2026-12 与 2027-01 两月」);建议统一为发布月或观测月并写明。
   - 原句: 「2026-12 或 2027-01 发布的 / 2026-12 与 2027-01 两月」
7. **agent_judgment.json reader_map.regions[US].from_to** — 「核心 CPI 同比 2.47%(2026-07)→2.57%(2026-09;指数水平 336.789→339.9)」括注的指数水平是 2026-07→2026-10(anchor_echo),与同比的 2026-09 不同月,建议标注月份。
   - 原句: 「→2.57%(2026-09;指数水平 336.789→339.9)」
   - 改句: 「→2.57%(2026-09;指数水平 2026-07 336.789→2026-10 339.9)」
8. **agent_judgment.json reader_map.regions[JP].from_to** — 「预计次月初前后公布」在冻结日历无对应条目(18 条中无 JP_POLICY_RATE 发布节奏条目),属未经证据面支撑的预期;无害,建议删去或标【假设】。
   - 原句: 「预计次月初前后公布」
9. **agent_judgment.json reader_map.transmission[0].links[1].observed_fact** — 美国利率环内插入「JP_POLICY_RATE 月均…日本亦处政策利率抬升通道」与本环区分指标无关。
   - 原句: 「JP_POLICY_RATE 月均 2026-09 1.043→2026-10 1.227,日本亦处政策利率抬升通道」
10. **agent_judgment.json l3.contradictions[C3-JP-POLICY].statement** — 关键数字用中文数字(一点二五/六十天/六十六天/正六十七个基点/正七十五个基点/零点四七八),不在契约面 9 个阿拉伯数字 token 之列(contract_verification.stats checks=9),只能人工复算(本席已逐个复算一致:P025/P032/P033/P209–P211);判断档披露注⑤②只自述了文本一致性别名表的缺口,未说明中文数字写法不被绑定。

## 六、裁决

**REVISE**(MAJOR 1 条)。数值/日期/方向层面 302 点独立复算零偏离,两锚、同比基期、政策面口径与天数、三利率恒等、资产月窗、Gate A 与 STALE 披露均属实;但传导链第 2 环的对质裁定「支持主解释」建立在稻草人式的竞争预期之上(竞争解释原文与观测相容、两解释在 TIPS_10Y 上预期未分立),违反读者报告自述的「预期未分立=尚不能区分」口径,属结论超出证据。按「只改必修句」原则给出 5 处原句→改句,改句中的数字(三窗实际 +53/+11/+102bp、盈亏平衡 -14/-19/-11bp、名义 -8bp)均取自只读证据面。MINOR/NIT 如实列出,不构成阻断。

