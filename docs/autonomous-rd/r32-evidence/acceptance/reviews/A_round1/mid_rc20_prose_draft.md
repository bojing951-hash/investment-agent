# Audit-R32 独立语义审查 · A 席 Round-1 · 复算清单 / 六查 / 反方攻击 / 问题清单

- 席位: independent-zero-context-seat-r32-a-round1(语义审查席, 零上下文, 未委派子代理)
- 审查日: 2026-11-24; 受审代码印章: 36499bb78a18dea1ff2b027074088b0ba404c3b8
- 裁决: **UPHELD**(MAJOR 0 条; MINOR 4 条; NIT 11 条)
- 复算点: 比对 925 点, 偏离 0 点, 另有登记项(NA) 8 条; 台账记录共 933 条(points.jsonl)
- 产出: PROSE-round1.md、VERDICT-round1.json(全部复核完成后一次性写出, 写出后不改写)

## 0 受审对象与版本核对

- 受审运行目录: 20261123T235103Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_日本在12个月前_3个月前和最
- 工单原文(逐字): 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 受审对象: agent_judgment.json 全文(schema_version 1.1; l3 矛盾陈述 3 条、机制链 2 条(环数 4+2); l4 情景 2 条; reader_map 键: headline_conclusion、regions、transmission、turnings、history_periods、rates_decomposition、asset_returns_echo、turning_supplement; quality_gate_notes 6 条)与 MAP_REPORT.md / FULL_REPORT.md / report.md 中的判断文字。
- 代码印章(report.json run.git_head): 36499bb78a18dea1ff2b027074088b0ba404c3b8; MAP_REPORT.md sha256: ad7b4cd00975b8b5429d8ee6e1f9f4e146910fada2e3c09dc525dfa66b7a001d(与 MAP_REPORT.sha256 一致); 冻结快照 sha256 前缀 2d650f1128cdd356(安装树副本与运行目录 overlay 副本逐字节一致); 冻结日历 version 1.5.0、entries 18 条。
- 受审文件修改时间(均早于席位首文件 2026-11-24 08:21:16):

| 文件 | 修改时间 |
|---|---|
| MAP_REPORT.md | 2026-11-24 08:20:53 |
| FULL_REPORT.md | 2026-11-24 08:20:53 |
| report.md | 2026-11-24 08:04:11 |
| agent_judgment.json | 2026-11-24 08:04:11 |
| report.json | 2026-11-24 08:04:11 |
| evidence_index.json | 2026-11-24 07:51:03 |
| views_digest.json | 2026-11-24 07:51:03 |
| AGENT_SEAT_ENVELOPE.json | 2026-11-24 07:51:03 |
| question_verbatim.txt | 2026-11-24 08:20:53 |
| MAP_REPORT.sha256 | 2026-11-24 08:20:53 |
| release_calendar.json | 2026-11-24 07:50:34 |
| research_snapshot_20261123.json | 2026-11-23 22:53:48 |

- 复核中途一次接口速率限制中断; 续算前复核上述印章、sha256 与修改时间均与中断前一致。
- 本席未读取任何预审内容或其他席产出; 运行目录三份报告中的「语义审查(席位待唤起)」(0 / 0 / 1 处)与「独立语义审查待裁」(1 / 0 / 0 处)为规程所述的预期文字。
- BUND_10Y / BUND_2Y 在判断档中只出现于 quality_gate_notes(序列库无此二序列), 未进入任何结论句。

## 1 方法与判读规则

- 只读面: 冻结快照 series_store(92 序列)/facts/gate_a、冻结日历、注册表、report.json 引擎面(点值格、三时点面板、相似检索面、契约验证)与受审文本; 全部数值由自写脚本直算后与受审稿文字比对。
- 判读: 显示精度取半单位容差; 「约」按正负 50% 以内判读; 发布日以冻结日历条目优先、其次注册表/引擎规则(CPI 13 天、CORE_PCE 30 天、EA_HICP_YOY 16 天、JP_CPI_YOY 20 天等), 欧元区 HICP 另按引擎历史面两级口径对照(见 MINOR-1); 月末取自然月末; 决议日惯例: 美联储=生效日前一日, 欧央行=生效日前上一个周四(【推断】), 日本央行 / 中国=当日。
- 台账 points.jsonl 每行一点(字段: section / src=出处键 / computed=直算值 / reported=报告值 / ok / note / where), 行号从 0 起计, 本文件以 #行号 引用; ok=True 计入比对点, ok=NA 为登记项(不计入比对点), ok=False 为偏离。
- 席位脚本(同目录, 供操作席复核): rc03_cells.py、rc04_paths.py、rc05_daily_dump.py、rc06_windows.py、rc07_sync.py、rc08_paths_points.py、rc09_daily_analog.py、rc10_supplement.py、rc11_sync_narr.py、rc12_hicp_rules.py、rc13_final_checks.py、rc14_sweep.py、rc14b_sweep_loc.py、rc15_final_supplement.py、rc16_ledger_patch.py、rc20_gen_outputs.py、rc20_inspect.py、rc_clean.py、rc_clean_mark.py、rc_dedupe.py、rc_lib.py、rc_mism.py、rc_points.py、x01_struct.py、x02_plan_keys.py、x03_dump_cells.py、x04_snap_struct.py、x05_snap_more.py、x06_gatea.py、x07_calendar.py、x08_steps.py、x09_faces.py、x10_where.py、x11_final_diag.py。
- 脚本运行方式: cd /tmp && /usr/bin/python3 -I <脚本> <路径参数…>; 本文件与 JSON 由 rc20_gen_outputs.py 一次性生成(draft 模式只写 mid_rc20_* 草稿并自检, write 模式在零问题且两件产出尚不存在时写出)。

## 2 复算清单(逐点: 出处键 / 直算值 / 报告值 / 一致与否)

| 分节 | 记录 | 一致 | NA |
|---|---|---|---|
| ②/⑬点值格 | 143 | 143 | 0 |
| ⑧同步面/当时可知 | 102 | 102 | 0 |
| ⑧历史事后窗 | 110 | 109 | 1 |
| ⑦传导环数字 | 31 | 31 | 0 |
| ⑤资产窗 | 14 | 14 | 0 |
| ①③同比路径(月频) | 83 | 82 | 1 |
| ⑥转折路径 | 12 | 12 | 0 |
| 杂项(引用/日历/结构) | 33 | 32 | 1 |
| ⑪诚实缺席 | 5 | 5 | 0 |
| ④政策面 | 58 | 56 | 2 |
| ⑧历史类比面 | 137 | 136 | 1 |
| ⑤三利率分解/资产窗 | 8 | 8 | 0 |
| ⑫时点标注 | 6 | 6 | 0 |
| ⑨情景阈值/期限 | 10 | 9 | 1 |
| ⑧历史事后窗(细表) | 82 | 82 | 0 |
| ⑩走位/转折叙述 | 36 | 36 | 0 |
| ②/⑬FULL_REPORT-L1事实表 | 48 | 48 | 0 |
| ⑦日度相关 | 1 | 1 | 0 |
| ⑩报告间文本一致 | 9 | 8 | 1 |
| ⑪诚实缺席/GateA | 5 | 5 | 0 |

### 2.1 ②/⑬点值格(记录 143 / 一致 143 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #0 | ②/⑬点值格 | snapshot.series_store.US_REAL_GDP + release_calendar.entries + 注册表发布规则 | {"obs": "2025-04-01", "value": 23884.563, "pub": "2025-07-29", "pub_basis": "rule:BEA/Eurostat/CabinetOffice", "yoy": 2.4206, "yoy_status": "2024-04-01", "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-04-01", "value": 23884.563, "pub": "2025-07-29", "yoy": 2.42, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[US_REAL_GDP].anchors[12个月前] |
| #1 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[12个月前\|US_REAL_GDP] | {"value": 23884.563, "observation_month": "2025-04"} | {"value": 23884.563, "observation_month": "2025-04"} | 一致 | 判断档 anchor_echo |
| #2 | ②/⑬点值格 | snapshot.series_store.US_REAL_GDP + release_calendar.entries + 注册表发布规则 | {"obs": "2026-04-01", "value": 24408.011, "pub": "2026-07-29", "pub_basis": "rule:BEA/Eurostat/CabinetOffice", "yoy": 2.1916, "yoy_status": "2025-04-01", "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-04-01", "value": 24408.011, "pub": "2026-07-29", "yoy": 2.19, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[US_REAL_GDP].anchors[3个月前] |
| #3 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[3个月前\|US_REAL_GDP] | {"value": 24408.011, "observation_month": "2026-04"} | {"value": 24408.011, "observation_month": "2026-04"} | 一致 | 判断档 anchor_echo |
| #4 | ②/⑬点值格 | snapshot.series_store.US_REAL_GDP + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 24611.077, "pub": "2026-10-29", "pub_basis": "rule:BEA/Eurostat/CabinetOffice", "yoy": 2.0657, "yoy_status": "2025-07-01", "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 24611.077, "pub": "2026-10-29", "yoy": 2.07, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[US_REAL_GDP].anchors[最新一期] |
| #5 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[最新一期\|US_REAL_GDP] | {"value": 24611.077, "observation_month": "2026-07"} | {"value": 24611.077, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #6 | ②/⑬点值格 | snapshot.series_store.UNEMPLOYMENT + release_calendar.entries + 注册表发布规则 | {"obs": "2025-09-01", "value": 4.4, "pub": "2025-11-20", "pub_basis": "calendar:RC-2025SHUTDOWN-UNEMP-SEP", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-09-01", "value": 4.4, "pub": "2025-11-20", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[UNEMPLOYMENT].anchors[12个月前] |
| #7 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[12个月前\|UNEMPLOYMENT] | {"value": 4.4, "observation_month": "2025-09"} | {"value": 4.4, "observation_month": "2025-09"} | 一致 | 判断档 anchor_echo |
| #8 | ②/⑬点值格 | snapshot.series_store.UNEMPLOYMENT + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 4.1, "pub": "2026-08-05", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 4.1, "pub": "2026-08-05", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[UNEMPLOYMENT].anchors[3个月前] |
| #9 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[3个月前\|UNEMPLOYMENT] | {"value": 4.1, "observation_month": "2026-07"} | {"value": 4.1, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #10 | ②/⑬点值格 | snapshot.series_store.UNEMPLOYMENT + release_calendar.entries + 注册表发布规则 | {"obs": "2026-10-01", "value": 4.1, "pub": "2026-11-05", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-10-01", "value": 4.1, "pub": "2026-11-05", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[UNEMPLOYMENT].anchors[最新一期] |
| #11 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[最新一期\|UNEMPLOYMENT] | {"value": 4.1, "observation_month": "2026-10"} | {"value": 4.1, "observation_month": "2026-10"} | 一致 | 判断档 anchor_echo |
| #12 | ②/⑬点值格 | snapshot.series_store.INDPRO + release_calendar.entries + 注册表发布规则 | {"obs": "2025-08-01", "value": 101.6247, "pub": "2025-09-15", "pub_basis": "rule", "yoy": 1.1887, "yoy_status": "2024-08", "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-08-01", "value": 101.6247, "pub": "2025-09-15", "yoy": 1.19, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[INDPRO].anchors[12个月前] |
| #13 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[12个月前\|INDPRO] | {"value": 101.6247, "observation_month": "2025-08"} | {"value": 101.6247, "observation_month": "2025-08"} | 一致 | 判断档 anchor_echo |
| #14 | ②/⑬点值格 | snapshot.series_store.INDPRO + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 103.1675, "pub": "2026-08-15", "pub_basis": "rule", "yoy": 1.2498, "yoy_status": "2025-07", "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 103.1675, "pub": "2026-08-15", "yoy": 1.25, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[INDPRO].anchors[3个月前] |
| #15 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[3个月前\|INDPRO] | {"value": 103.1675, "observation_month": "2026-07"} | {"value": 103.1675, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #16 | ②/⑬点值格 | snapshot.series_store.INDPRO + release_calendar.entries + 注册表发布规则 | {"obs": "2026-10-01", "value": 103.3954, "pub": "2026-11-15", "pub_basis": "rule", "yoy": 2.1497, "yoy_status": "2025-10", "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-10-01", "value": 103.3954, "pub": "2026-11-15", "yoy": 2.15, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[INDPRO].anchors[最新一期] |
| #17 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[最新一期\|INDPRO] | {"value": 103.3954, "observation_month": "2026-10"} | {"value": 103.3954, "observation_month": "2026-10"} | 一致 | 判断档 anchor_echo |
| #18 | ②/⑬点值格 | snapshot.series_store.CPI + release_calendar.entries + 注册表发布规则 | {"obs": "2025-09-01", "value": 324.245, "pub": "2025-10-24", "pub_basis": "calendar:RC-2025SHUTDOWN-CPI-SEP", "yoy": 3.0226, "yoy_status": "2024-09", "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-09-01", "value": 324.245, "pub": "2025-10-24", "yoy": 3.02, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CPI].anchors[12个月前] |
| #19 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[12个月前\|CPI] | {"value": 324.245, "observation_month": "2025-09"} | {"value": 324.245, "observation_month": "2025-09"} | 一致 | 判断档 anchor_echo |
| #20 | ②/⑬点值格 | snapshot.series_store.CPI + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 332.813, "pub": "2026-08-13", "pub_basis": "rule", "yoy": 3.3039, "yoy_status": "2025-07", "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 332.813, "pub": "2026-08-13", "yoy": 3.3, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CPI].anchors[3个月前] |
| #21 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[3个月前\|CPI] | {"value": 332.813, "observation_month": "2026-07"} | {"value": 332.813, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #22 | ②/⑬点值格 | snapshot.series_store.CPI + release_calendar.entries + 注册表发布规则 | {"obs": "2026-10-01", "value": 337.476, "pub": "2026-11-13", "pub_basis": "rule", "yoy": null, "yoy_status": "no_same_period_base", "latest_valid_yoy": {"ym": "2026-09", "yoy": 3.72}} | {"status": "ok", "obs": "2026-10-01", "value": 337.476, "pub": "2026-11-13", "yoy": null, "yoy_status": "no_same_period_base", "latest_valid": {"observation_date": "2026-09-01", "yoy_pct": 3.72}} | 一致 | report.json:research_plan.point_values.cells[CPI].anchors[最新一期] |
| #23 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[最新一期\|CPI] | {"value": 337.476, "observation_month": "2026-10"} | {"value": 337.476, "observation_month": "2026-10"} | 一致 | 判断档 anchor_echo |
| #24 | ②/⑬点值格 | snapshot.series_store.CORE_CPI + release_calendar.entries + 注册表发布规则 | {"obs": "2025-09-01", "value": 330.418, "pub": "2025-10-24", "pub_basis": "calendar:RC-2025SHUTDOWN-CORECPI-SEP", "yoy": 3.02, "yoy_status": "2024-09", "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-09-01", "value": 330.418, "pub": "2025-10-24", "yoy": 3.02, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CORE_CPI].anchors[12个月前] |
| #25 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[12个月前\|CORE_CPI] | {"value": 330.418, "observation_month": "2025-09"} | {"value": 330.418, "observation_month": "2025-09"} | 一致 | 判断档 anchor_echo |
| #26 | ②/⑬点值格 | snapshot.series_store.CORE_CPI + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 336.789, "pub": "2026-08-13", "pub_basis": "rule", "yoy": 2.4665, "yoy_status": "2025-07", "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 336.789, "pub": "2026-08-13", "yoy": 2.47, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CORE_CPI].anchors[3个月前] |
| #27 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[3个月前\|CORE_CPI] | {"value": 336.789, "observation_month": "2026-07"} | {"value": 336.789, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #28 | ②/⑬点值格 | snapshot.series_store.CORE_CPI + release_calendar.entries + 注册表发布规则 | {"obs": "2026-10-01", "value": 339.9, "pub": "2026-11-13", "pub_basis": "rule", "yoy": null, "yoy_status": "no_same_period_base", "latest_valid_yoy": {"ym": "2026-09", "yoy": 2.57}} | {"status": "ok", "obs": "2026-10-01", "value": 339.9, "pub": "2026-11-13", "yoy": null, "yoy_status": "no_same_period_base", "latest_valid": {"observation_date": "2026-09-01", "yoy_pct": 2.57}} | 一致 | report.json:research_plan.point_values.cells[CORE_CPI].anchors[最新一期] |
| #29 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[最新一期\|CORE_CPI] | {"value": 339.9, "observation_month": "2026-10"} | {"value": 339.9, "observation_month": "2026-10"} | 一致 | 判断档 anchor_echo |
| #30 | ②/⑬点值格 | snapshot.series_store.CORE_PCE + release_calendar.entries + 注册表发布规则 | {"obs": "2025-08-01", "value": 126.646, "pub": "2025-09-30", "pub_basis": "rule", "yoy": 2.8513, "yoy_status": "2024-08", "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-08-01", "value": 126.646, "pub": "2025-09-30", "yoy": 2.85, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CORE_PCE].anchors[12个月前] |
| #31 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[12个月前\|CORE_PCE] | {"value": 126.646, "observation_month": "2025-08"} | {"value": 126.646, "observation_month": "2025-08"} | 一致 | 判断档 anchor_echo |
| #32 | ②/⑬点值格 | snapshot.series_store.CORE_PCE + release_calendar.entries + 注册表发布规则 | {"obs": "2026-06-01", "value": 129.969, "pub": "2026-07-30", "pub_basis": "rule", "yoy": 3.0412, "yoy_status": "2025-06", "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-06-01", "value": 129.969, "pub": "2026-07-30", "yoy": 3.04, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CORE_PCE].anchors[3个月前] |
| #33 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[3个月前\|CORE_PCE] | {"value": 129.969, "observation_month": "2026-06"} | {"value": 129.969, "observation_month": "2026-06"} | 一致 | 判断档 anchor_echo |
| #34 | ②/⑬点值格 | snapshot.series_store.CORE_PCE + release_calendar.entries + 注册表发布规则 | {"obs": "2026-09-01", "value": 130.902, "pub": "2026-10-30", "pub_basis": "rule", "yoy": 3.1212, "yoy_status": "2025-09", "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-09-01", "value": 130.902, "pub": "2026-10-30", "yoy": 3.12, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CORE_PCE].anchors[最新一期] |
| #35 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[最新一期\|CORE_PCE] | {"value": 130.902, "observation_month": "2026-09"} | {"value": 130.902, "observation_month": "2026-09"} | 一致 | 判断档 anchor_echo |
| #36 | ②/⑬点值格 | snapshot.series_store.DFEDTARU + release_calendar.entries + 注册表发布规则 | {"obs": "2025-11-23", "value": 4.0, "pub": "2025-11-23", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-11-23", "value": 4.0, "pub": "2025-11-23", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[DFEDTARU].anchors[12个月前] |
| #37 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[12个月前\|DFEDTARU] | {"value": 4.0, "observation_month": "2025-11"} | {"value": 4.0, "observation_month": "2025-11"} | 一致 | 判断档 anchor_echo |
| #38 | ②/⑬点值格 | snapshot.series_store.DFEDTARU + release_calendar.entries + 注册表发布规则 | {"obs": "2026-08-23", "value": 3.75, "pub": "2026-08-23", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-08-23", "value": 3.75, "pub": "2026-08-23", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[DFEDTARU].anchors[3个月前] |
| #39 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[3个月前\|DFEDTARU] | {"value": 3.75, "observation_month": "2026-08"} | {"value": 3.75, "observation_month": "2026-08"} | 一致 | 判断档 anchor_echo |
| #40 | ②/⑬点值格 | snapshot.series_store.DFEDTARU + release_calendar.entries + 注册表发布规则 | {"obs": "2026-11-23", "value": 4.0, "pub": "2026-11-23", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-11-23", "value": 4.0, "pub": "2026-11-23", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[DFEDTARU].anchors[最新一期] |
| #41 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[最新一期\|DFEDTARU] | {"value": 4.0, "observation_month": "2026-11"} | {"value": 4.0, "observation_month": "2026-11"} | 一致 | 判断档 anchor_echo |
| #42 | ②/⑬点值格 | snapshot.series_store.DFF + release_calendar.entries + 注册表发布规则 | {"obs": "2025-11-22", "value": 3.88, "pub": "2025-11-23", "pub_basis": "rule:DFF次日(注册表)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-11-22", "value": 3.88, "pub": "2025-11-23", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[DFF].anchors[12个月前] |
| #43 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[12个月前\|DFF] | {"value": 3.88, "observation_month": "2025-11"} | {"value": 3.88, "observation_month": "2025-11"} | 一致 | 判断档 anchor_echo |
| #44 | ②/⑬点值格 | snapshot.series_store.DFF + release_calendar.entries + 注册表发布规则 | {"obs": "2026-08-22", "value": 3.63, "pub": "2026-08-23", "pub_basis": "rule:DFF次日(注册表)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-08-22", "value": 3.63, "pub": "2026-08-23", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[DFF].anchors[3个月前] |
| #45 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[3个月前\|DFF] | {"value": 3.63, "observation_month": "2026-08"} | {"value": 3.63, "observation_month": "2026-08"} | 一致 | 判断档 anchor_echo |
| #46 | ②/⑬点值格 | snapshot.series_store.DFF + release_calendar.entries + 注册表发布规则 | {"obs": "2026-11-19", "value": 3.88, "pub": "2026-11-20", "pub_basis": "rule:DFF次日(注册表)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-11-19", "value": 3.88, "pub": "2026-11-20", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[DFF].anchors[最新一期] |
| #47 | ②/⑬点值格 | agent_judgment.reader_map.regions[US].anchor_echo[最新一期\|DFF] | {"value": 3.88, "observation_month": "2026-11"} | {"value": 3.88, "observation_month": "2026-11"} | 一致 | 判断档 anchor_echo |
| #48 | ②/⑬点值格 | snapshot.series_store.CN_PMI_MFG + release_calendar.entries + 注册表发布规则 | {"obs": "2025-10-01", "value": 49.0, "pub": "2025-10-30", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-10-01", "value": 49.0, "pub": "2025-10-30", "yoy": -2.2, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_PMI_MFG].anchors[12个月前] |
| #49 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[12个月前\|CN_PMI_MFG] | {"value": 49.0, "observation_month": "2025-10"} | {"value": 49.0, "observation_month": "2025-10"} | 一致 | 判断档 anchor_echo |
| #50 | ②/⑬点值格 | snapshot.series_store.CN_PMI_MFG + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 49.2, "pub": "2026-07-30", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 49.2, "pub": "2026-07-30", "yoy": -0.2, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_PMI_MFG].anchors[3个月前] |
| #51 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[3个月前\|CN_PMI_MFG] | {"value": 49.2, "observation_month": "2026-07"} | {"value": 49.2, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #52 | ②/⑬点值格 | snapshot.series_store.CN_PMI_MFG + release_calendar.entries + 注册表发布规则 | {"obs": "2026-10-01", "value": 49.3, "pub": "2026-10-30", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-10-01", "value": 49.3, "pub": "2026-10-30", "yoy": 0.61, "yoy_status": "ok", "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_PMI_MFG].anchors[最新一期] |
| #53 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[最新一期\|CN_PMI_MFG] | {"value": 49.3, "observation_month": "2026-10"} | {"value": 49.3, "observation_month": "2026-10"} | 一致 | 判断档 anchor_echo |
| #54 | ②/⑬点值格 | snapshot.series_store.CN_CPI_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2025-10-01", "value": 0.2, "pub": "2025-11-09", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-10-01", "value": 0.2, "pub": "2025-11-09", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_CPI_YOY].anchors[12个月前] |
| #55 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[12个月前\|CN_CPI_YOY] | {"value": 0.2, "observation_month": "2025-10"} | {"value": 0.2, "observation_month": "2025-10"} | 一致 | 判断档 anchor_echo |
| #56 | ②/⑬点值格 | snapshot.series_store.CN_CPI_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 0.5, "pub": "2026-08-09", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 0.5, "pub": "2026-08-09", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_CPI_YOY].anchors[3个月前] |
| #57 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[3个月前\|CN_CPI_YOY] | {"value": 0.5, "observation_month": "2026-07"} | {"value": 0.5, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #58 | ②/⑬点值格 | snapshot.series_store.CN_CPI_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-10-01", "value": 0.7, "pub": "2026-11-09", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-10-01", "value": 0.7, "pub": "2026-11-09", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_CPI_YOY].anchors[最新一期] |
| #59 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[最新一期\|CN_CPI_YOY] | {"value": 0.7, "observation_month": "2026-10"} | {"value": 0.7, "observation_month": "2026-10"} | 一致 | 判断档 anchor_echo |
| #60 | ②/⑬点值格 | snapshot.series_store.CN_PPI_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2025-10-01", "value": -2.1, "pub": "2025-11-09", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-10-01", "value": -2.1, "pub": "2025-11-09", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_PPI_YOY].anchors[12个月前] |
| #61 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[12个月前\|CN_PPI_YOY] | {"value": -2.1, "observation_month": "2025-10"} | {"value": -2.1, "observation_month": "2025-10"} | 一致 | 判断档 anchor_echo |
| #62 | ②/⑬点值格 | snapshot.series_store.CN_PPI_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 3.5, "pub": "2026-08-09", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 3.5, "pub": "2026-08-09", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_PPI_YOY].anchors[3个月前] |
| #63 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[3个月前\|CN_PPI_YOY] | {"value": 3.5, "observation_month": "2026-07"} | {"value": 3.5, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #64 | ②/⑬点值格 | snapshot.series_store.CN_PPI_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-10-01", "value": 5.7, "pub": "2026-11-09", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-10-01", "value": 5.7, "pub": "2026-11-09", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_PPI_YOY].anchors[最新一期] |
| #65 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[最新一期\|CN_PPI_YOY] | {"value": 5.7, "observation_month": "2026-10"} | {"value": 5.7, "observation_month": "2026-10"} | 一致 | 判断档 anchor_echo |
| #66 | ②/⑬点值格 | snapshot.series_store.CN_POLICY_OVERNIGHT + release_calendar.entries + 注册表发布规则 | {"obs": null, "value": null, "pub": null, "pub_basis": null, "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "no_published_observation_on_or_before_anchor", "obs": null, "value": null, "pub": null, "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_POLICY_OVERNIGHT].anchors[12个月前] |
| #67 | ②/⑬点值格 | snapshot.series_store.CN_POLICY_OVERNIGHT + release_calendar.entries + 注册表发布规则 | {"obs": null, "value": null, "pub": null, "pub_basis": null, "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "no_published_observation_on_or_before_anchor", "obs": null, "value": null, "pub": null, "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_POLICY_OVERNIGHT].anchors[3个月前] |
| #68 | ②/⑬点值格 | snapshot.series_store.CN_POLICY_OVERNIGHT + release_calendar.entries + 注册表发布规则 | {"obs": "2026-11-23", "value": 1.25, "pub": "2026-11-23", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-11-23", "value": 1.25, "pub": "2026-11-23", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_POLICY_OVERNIGHT].anchors[最新一期] |
| #69 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[最新一期\|CN_POLICY_OVERNIGHT] | {"value": 1.25, "observation_month": "2026-11"} | {"value": 1.25, "observation_month": "2026-11"} | 一致 | 判断档 anchor_echo |
| #70 | ②/⑬点值格 | snapshot.series_store.CN_OMO_7D + release_calendar.entries + 注册表发布规则 | {"obs": "2025-11-14", "value": 1.4, "pub": "2025-11-14", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-11-14", "value": 1.4, "pub": "2025-11-14", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_OMO_7D].anchors[12个月前] |
| #71 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[12个月前\|CN_OMO_7D] | {"value": 1.4, "observation_month": "2025-11"} | {"value": 1.4, "observation_month": "2025-11"} | 一致 | 判断档 anchor_echo |
| #72 | ②/⑬点值格 | snapshot.series_store.CN_OMO_7D + release_calendar.entries + 注册表发布规则 | {"obs": "2026-08-21", "value": 1.4, "pub": "2026-08-21", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-08-21", "value": 1.4, "pub": "2026-08-21", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_OMO_7D].anchors[3个月前] |
| #73 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[3个月前\|CN_OMO_7D] | {"value": 1.4, "observation_month": "2026-08"} | {"value": 1.4, "observation_month": "2026-08"} | 一致 | 判断档 anchor_echo |
| #74 | ②/⑬点值格 | snapshot.series_store.CN_OMO_7D + release_calendar.entries + 注册表发布规则 | {"obs": "2026-10-30", "value": 1.4, "pub": "2026-10-30", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-10-30", "value": 1.4, "pub": "2026-10-30", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_OMO_7D].anchors[最新一期] |
| #75 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[最新一期\|CN_OMO_7D] | {"value": 1.4, "observation_month": "2026-10"} | {"value": 1.4, "observation_month": "2026-10"} | 一致 | 判断档 anchor_echo |
| #76 | ②/⑬点值格 | snapshot.series_store.CN_LPR_1Y + release_calendar.entries + 注册表发布规则 | {"obs": "2025-11-20", "value": 3.0, "pub": "2025-11-20", "pub_basis": "calendar:RC-CN-LPR-2025M11", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-11-20", "value": 3.0, "pub": "2025-11-20", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_LPR_1Y].anchors[12个月前] |
| #77 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[12个月前\|CN_LPR_1Y] | {"value": 3.0, "observation_month": "2025-11"} | {"value": 3.0, "observation_month": "2025-11"} | 一致 | 判断档 anchor_echo |
| #78 | ②/⑬点值格 | snapshot.series_store.CN_LPR_1Y + release_calendar.entries + 注册表发布规则 | {"obs": "2026-08-20", "value": 3.0, "pub": "2026-08-20", "pub_basis": "rule:obs=publish day(20日)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-08-20", "value": 3.0, "pub": "2026-08-20", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_LPR_1Y].anchors[3个月前] |
| #79 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[3个月前\|CN_LPR_1Y] | {"value": 3.0, "observation_month": "2026-08"} | {"value": 3.0, "observation_month": "2026-08"} | 一致 | 判断档 anchor_echo |
| #80 | ②/⑬点值格 | snapshot.series_store.CN_LPR_1Y + release_calendar.entries + 注册表发布规则 | {"obs": "2026-11-20", "value": 3.0, "pub": "2026-11-20", "pub_basis": "calendar:RC-CN-LPR-2026M11", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-11-20", "value": 3.0, "pub": "2026-11-20", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[CN_LPR_1Y].anchors[最新一期] |
| #81 | ②/⑬点值格 | agent_judgment.reader_map.regions[CN].anchor_echo[最新一期\|CN_LPR_1Y] | {"value": 3.0, "observation_month": "2026-11"} | {"value": 3.0, "observation_month": "2026-11"} | 一致 | 判断档 anchor_echo |
| #82 | ②/⑬点值格 | snapshot.series_store.EA_REAL_GDP_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2025-07-01", "value": 1.11, "pub": "2025-11-04", "pub_basis": "rule:BEA/Eurostat/CabinetOffice", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-07-01", "value": 1.11, "pub": "2025-11-04", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[EA_REAL_GDP_YOY].anchors[12个月前] |
| #83 | ②/⑬点值格 | agent_judgment.reader_map.regions[EA].anchor_echo[12个月前\|EA_REAL_GDP_YOY] | {"value": 1.11, "observation_month": "2025-07"} | {"value": 1.11, "observation_month": "2025-07"} | 一致 | 判断档 anchor_echo |
| #84 | ②/⑬点值格 | snapshot.series_store.EA_REAL_GDP_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-04-01", "value": 1.19, "pub": "2026-08-04", "pub_basis": "rule:BEA/Eurostat/CabinetOffice", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-04-01", "value": 1.19, "pub": "2026-08-04", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[EA_REAL_GDP_YOY].anchors[3个月前] |
| #85 | ②/⑬点值格 | agent_judgment.reader_map.regions[EA].anchor_echo[3个月前\|EA_REAL_GDP_YOY] | {"value": 1.19, "observation_month": "2026-04"} | {"value": 1.19, "observation_month": "2026-04"} | 一致 | 判断档 anchor_echo |
| #86 | ②/⑬点值格 | snapshot.series_store.EA_REAL_GDP_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 1.28, "pub": "2026-11-04", "pub_basis": "rule:BEA/Eurostat/CabinetOffice", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 1.28, "pub": "2026-11-04", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[EA_REAL_GDP_YOY].anchors[最新一期] |
| #87 | ②/⑬点值格 | agent_judgment.reader_map.regions[EA].anchor_echo[最新一期\|EA_REAL_GDP_YOY] | {"value": 1.28, "observation_month": "2026-07"} | {"value": 1.28, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #88 | ②/⑬点值格 | snapshot.series_store.EA_HICP_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2025-10-01", "value": 2.1, "pub": "2025-11-16", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-10-01", "value": 2.1, "pub": "2025-11-16", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[EA_HICP_YOY].anchors[12个月前] |
| #89 | ②/⑬点值格 | agent_judgment.reader_map.regions[EA].anchor_echo[12个月前\|EA_HICP_YOY] | {"value": 2.1, "observation_month": "2025-10"} | {"value": 2.1, "observation_month": "2025-10"} | 一致 | 判断档 anchor_echo |
| #90 | ②/⑬点值格 | snapshot.series_store.EA_HICP_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 2.9, "pub": "2026-08-16", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 2.9, "pub": "2026-08-16", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[EA_HICP_YOY].anchors[3个月前] |
| #91 | ②/⑬点值格 | agent_judgment.reader_map.regions[EA].anchor_echo[3个月前\|EA_HICP_YOY] | {"value": 2.9, "observation_month": "2026-07"} | {"value": 2.9, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #92 | ②/⑬点值格 | snapshot.series_store.EA_HICP_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-10-01", "value": 4.0, "pub": "2026-11-16", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-10-01", "value": 4.0, "pub": "2026-11-16", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[EA_HICP_YOY].anchors[最新一期] |
| #93 | ②/⑬点值格 | agent_judgment.reader_map.regions[EA].anchor_echo[最新一期\|EA_HICP_YOY] | {"value": 4.0, "observation_month": "2026-10"} | {"value": 4.0, "observation_month": "2026-10"} | 一致 | 判断档 anchor_echo |
| #94 | ②/⑬点值格 | snapshot.series_store.ECB_MRO + release_calendar.entries + 注册表发布规则 | {"obs": "2025-06-11", "value": 2.15, "pub": "2025-06-11", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-06-11", "value": 2.15, "pub": "2025-06-11", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[ECB_MRO].anchors[12个月前] |
| #95 | ②/⑬点值格 | agent_judgment.reader_map.regions[EA].anchor_echo[12个月前\|ECB_MRO] | {"value": 2.15, "observation_month": "2025-06"} | {"value": 2.15, "observation_month": "2025-06"} | 一致 | 判断档 anchor_echo |
| #96 | ②/⑬点值格 | snapshot.series_store.ECB_MRO + release_calendar.entries + 注册表发布规则 | {"obs": "2026-06-17", "value": 2.4, "pub": "2026-06-17", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-06-17", "value": 2.4, "pub": "2026-06-17", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[ECB_MRO].anchors[3个月前] |
| #97 | ②/⑬点值格 | agent_judgment.reader_map.regions[EA].anchor_echo[3个月前\|ECB_MRO] | {"value": 2.4, "observation_month": "2026-06"} | {"value": 2.4, "observation_month": "2026-06"} | 一致 | 判断档 anchor_echo |
| #98 | ②/⑬点值格 | snapshot.series_store.ECB_MRO + release_calendar.entries + 注册表发布规则 | {"obs": "2026-09-16", "value": 2.65, "pub": "2026-09-16", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-09-16", "value": 2.65, "pub": "2026-09-16", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[ECB_MRO].anchors[最新一期] |
| #99 | ②/⑬点值格 | agent_judgment.reader_map.regions[EA].anchor_echo[最新一期\|ECB_MRO] | {"value": 2.65, "observation_month": "2026-09"} | {"value": 2.65, "observation_month": "2026-09"} | 一致 | 判断档 anchor_echo |
| #100 | ②/⑬点值格 | snapshot.series_store.ECB_DFR + release_calendar.entries + 注册表发布规则 | {"obs": "2025-06-11", "value": 2.0, "pub": "2025-06-11", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-06-11", "value": 2.0, "pub": "2025-06-11", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[ECB_DFR].anchors[12个月前] |
| #101 | ②/⑬点值格 | agent_judgment.reader_map.regions[EA].anchor_echo[12个月前\|ECB_DFR] | {"value": 2.0, "observation_month": "2025-06"} | {"value": 2.0, "observation_month": "2025-06"} | 一致 | 判断档 anchor_echo |
| #102 | ②/⑬点值格 | snapshot.series_store.ECB_DFR + release_calendar.entries + 注册表发布规则 | {"obs": "2026-06-17", "value": 2.25, "pub": "2026-06-17", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-06-17", "value": 2.25, "pub": "2026-06-17", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[ECB_DFR].anchors[3个月前] |
| #103 | ②/⑬点值格 | agent_judgment.reader_map.regions[EA].anchor_echo[3个月前\|ECB_DFR] | {"value": 2.25, "observation_month": "2026-06"} | {"value": 2.25, "observation_month": "2026-06"} | 一致 | 判断档 anchor_echo |
| #104 | ②/⑬点值格 | snapshot.series_store.ECB_DFR + release_calendar.entries + 注册表发布规则 | {"obs": "2026-09-16", "value": 2.5, "pub": "2026-09-16", "pub_basis": "obs=publish(市场/日频序列)", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-09-16", "value": 2.5, "pub": "2026-09-16", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[ECB_DFR].anchors[最新一期] |
| #105 | ②/⑬点值格 | agent_judgment.reader_map.regions[EA].anchor_echo[最新一期\|ECB_DFR] | {"value": 2.5, "observation_month": "2026-09"} | {"value": 2.5, "observation_month": "2026-09"} | 一致 | 判断档 anchor_echo |
| #106 | ②/⑬点值格 | snapshot.series_store.JP_REAL_GDP_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2025-07-01", "value": 0.63, "pub": "2025-11-14", "pub_basis": "rule:BEA/Eurostat/CabinetOffice", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-07-01", "value": 0.63, "pub": "2025-11-14", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[JP_REAL_GDP_YOY].anchors[12个月前] |
| #107 | ②/⑬点值格 | agent_judgment.reader_map.regions[JP].anchor_echo[12个月前\|JP_REAL_GDP_YOY] | {"value": 0.63, "observation_month": "2025-07"} | {"value": 0.63, "observation_month": "2025-07"} | 一致 | 判断档 anchor_echo |
| #108 | ②/⑬点值格 | snapshot.series_store.JP_REAL_GDP_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-04-01", "value": 0.8, "pub": "2026-08-14", "pub_basis": "rule:BEA/Eurostat/CabinetOffice", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-04-01", "value": 0.8, "pub": "2026-08-14", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[JP_REAL_GDP_YOY].anchors[3个月前] |
| #109 | ②/⑬点值格 | agent_judgment.reader_map.regions[JP].anchor_echo[3个月前\|JP_REAL_GDP_YOY] | {"value": 0.8, "observation_month": "2026-04"} | {"value": 0.8, "observation_month": "2026-04"} | 一致 | 判断档 anchor_echo |
| #110 | ②/⑬点值格 | snapshot.series_store.JP_REAL_GDP_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 1.16, "pub": "2026-11-14", "pub_basis": "rule:BEA/Eurostat/CabinetOffice", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 1.16, "pub": "2026-11-14", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[JP_REAL_GDP_YOY].anchors[最新一期] |
| #111 | ②/⑬点值格 | agent_judgment.reader_map.regions[JP].anchor_echo[最新一期\|JP_REAL_GDP_YOY] | {"value": 1.16, "observation_month": "2026-07"} | {"value": 1.16, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #112 | ②/⑬点值格 | snapshot.series_store.JP_CPI_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2025-10-01", "value": 2.99, "pub": "2025-11-20", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-10-01", "value": 2.99, "pub": "2025-11-20", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[JP_CPI_YOY].anchors[12个月前] |
| #113 | ②/⑬点值格 | agent_judgment.reader_map.regions[JP].anchor_echo[12个月前\|JP_CPI_YOY] | {"value": 2.99, "observation_month": "2025-10"} | {"value": 2.99, "observation_month": "2025-10"} | 一致 | 判断档 anchor_echo |
| #114 | ②/⑬点值格 | snapshot.series_store.JP_CPI_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 1.97, "pub": "2026-08-20", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 1.97, "pub": "2026-08-20", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[JP_CPI_YOY].anchors[3个月前] |
| #115 | ②/⑬点值格 | agent_judgment.reader_map.regions[JP].anchor_echo[3个月前\|JP_CPI_YOY] | {"value": 1.97, "observation_month": "2026-07"} | {"value": 1.97, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #116 | ②/⑬点值格 | snapshot.series_store.JP_CPI_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-10-01", "value": 2.44, "pub": "2026-11-20", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-10-01", "value": 2.44, "pub": "2026-11-20", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[JP_CPI_YOY].anchors[最新一期] |
| #117 | ②/⑬点值格 | agent_judgment.reader_map.regions[JP].anchor_echo[最新一期\|JP_CPI_YOY] | {"value": 2.44, "observation_month": "2026-10"} | {"value": 2.44, "observation_month": "2026-10"} | 一致 | 判断档 anchor_echo |
| #118 | ②/⑬点值格 | snapshot.series_store.JP_CPI_TOKYO_YOY + release_calendar.entries + 注册表发布规则 | {"obs": null, "value": null, "pub": null, "pub_basis": null, "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "no_published_observation_on_or_before_anchor", "obs": null, "value": null, "pub": null, "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[JP_CPI_TOKYO_YOY].anchors[12个月前] |
| #119 | ②/⑬点值格 | snapshot.series_store.JP_CPI_TOKYO_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 1.85, "pub": "2026-07-30", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 1.85, "pub": "2026-07-30", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[JP_CPI_TOKYO_YOY].anchors[3个月前] |
| #120 | ②/⑬点值格 | agent_judgment.reader_map.regions[JP].anchor_echo[3个月前\|JP_CPI_TOKYO_YOY] | {"value": 1.85, "observation_month": "2026-07"} | {"value": 1.85, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #121 | ②/⑬点值格 | snapshot.series_store.JP_CPI_TOKYO_YOY + release_calendar.entries + 注册表发布规则 | {"obs": "2026-10-01", "value": 2.73, "pub": "2026-10-30", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-10-01", "value": 2.73, "pub": "2026-10-30", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[JP_CPI_TOKYO_YOY].anchors[最新一期] |
| #122 | ②/⑬点值格 | agent_judgment.reader_map.regions[JP].anchor_echo[最新一期\|JP_CPI_TOKYO_YOY] | {"value": 2.73, "observation_month": "2026-10"} | {"value": 2.73, "observation_month": "2026-10"} | 一致 | 判断档 anchor_echo |
| #123 | ②/⑬点值格 | snapshot.series_store.JP_POLICY_RATE + release_calendar.entries + 注册表发布规则 | {"obs": "2025-10-01", "value": 0.477, "pub": "2025-11-05", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2025-10-01", "value": 0.477, "pub": "2025-11-05", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[JP_POLICY_RATE].anchors[12个月前] |
| #124 | ②/⑬点值格 | agent_judgment.reader_map.regions[JP].anchor_echo[12个月前\|JP_POLICY_RATE] | {"value": 0.477, "observation_month": "2025-10"} | {"value": 0.477, "observation_month": "2025-10"} | 一致 | 判断档 anchor_echo |
| #125 | ②/⑬点值格 | snapshot.series_store.JP_POLICY_RATE + release_calendar.entries + 注册表发布规则 | {"obs": "2026-07-01", "value": 0.978, "pub": "2026-08-05", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-07-01", "value": 0.978, "pub": "2026-08-05", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[JP_POLICY_RATE].anchors[3个月前] |
| #126 | ②/⑬点值格 | agent_judgment.reader_map.regions[JP].anchor_echo[3个月前\|JP_POLICY_RATE] | {"value": 0.978, "observation_month": "2026-07"} | {"value": 0.978, "observation_month": "2026-07"} | 一致 | 判断档 anchor_echo |
| #127 | ②/⑬点值格 | snapshot.series_store.JP_POLICY_RATE + release_calendar.entries + 注册表发布规则 | {"obs": "2026-10-01", "value": 1.227, "pub": "2026-11-05", "pub_basis": "rule", "yoy": null, "yoy_status": null, "latest_valid_yoy": null} | {"status": "ok", "obs": "2026-10-01", "value": 1.227, "pub": "2026-11-05", "yoy": null, "yoy_status": null, "latest_valid": null} | 一致 | report.json:research_plan.point_values.cells[JP_POLICY_RATE].anchors[最新一期] |
| #128 | ②/⑬点值格 | agent_judgment.reader_map.regions[JP].anchor_echo[最新一期\|JP_POLICY_RATE] | {"value": 1.227, "observation_month": "2026-10"} | {"value": 1.227, "observation_month": "2026-10"} | 一致 | 判断档 anchor_echo |
| #885 | ②/⑬点值格 | snapshot.series_store.UST_10Y 截止日前最近观测(值/观测日) + C1.evidence_refs 标签日期 + 规则发布日 | {"obs_date": "2026-11-19", "value": 5.04, "ref_label": "2026-11-19", "pub_date": "2026-11-19", "basis": "obs=publish(市场/日频序列)"} | {"value": 5.04, "ref_label": "2026-11-19", "obs_upto": "2026-11-23"} | 一致 | agent_judgment.l3.contradictions[0].statement 证据面最新水平清单 / MAP_REPORT 主线综合 |
| #886 | ②/⑬点值格 | snapshot.series_store.TIPS_10Y 截止日前最近观测(值/观测日) + C1.evidence_refs 标签日期 + 规则发布日 | {"obs_date": "2026-11-19", "value": 2.88, "ref_label": "2026-11-19", "pub_date": "2026-11-19", "basis": "obs=publish(市场/日频序列)"} | {"value": 2.88, "ref_label": "2026-11-19", "obs_upto": "2026-11-23"} | 一致 | agent_judgment.l3.contradictions[0].statement 证据面最新水平清单 / MAP_REPORT 主线综合 |
| #887 | ②/⑬点值格 | snapshot.series_store.BEI_10Y 截止日前最近观测(值/观测日) + C1.evidence_refs 标签日期 + 规则发布日 | {"obs_date": "2026-11-20", "value": 2.15, "ref_label": "2026-11-20", "pub_date": "2026-11-20", "basis": "obs=publish(市场/日频序列)"} | {"value": 2.15, "ref_label": "2026-11-20", "obs_upto": "2026-11-23"} | 一致 | agent_judgment.l3.contradictions[0].statement 证据面最新水平清单 / MAP_REPORT 主线综合 |
| #888 | ②/⑬点值格 | snapshot.series_store.VIX 截止日前最近观测(值/观测日) + C1.evidence_refs 标签日期 + 规则发布日 | {"obs_date": "2026-11-23", "value": 27.01, "ref_label": "2026-11-23", "pub_date": "2026-11-23", "basis": "obs=publish(市场/日频序列)"} | {"value": 27.01, "ref_label": "2026-11-23", "obs_upto": "2026-11-23"} | 一致 | agent_judgment.l3.contradictions[0].statement 证据面最新水平清单 / MAP_REPORT 主线综合 |
| #889 | ②/⑬点值格 | snapshot.series_store.HY_OAS 截止日前最近观测(值/观测日) + C1.evidence_refs 标签日期 + 规则发布日 | {"obs_date": "2026-11-19", "value": 3.52, "ref_label": "2026-11-19", "pub_date": "2026-11-19", "basis": "obs=publish(市场/日频序列)"} | {"value": 3.52, "ref_label": "2026-11-19", "obs_upto": "2026-11-23"} | 一致 | agent_judgment.l3.contradictions[0].statement 证据面最新水平清单 / MAP_REPORT 主线综合 |
| #890 | ②/⑬点值格 | snapshot.series_store.USDJPY 截止日前最近观测(值/观测日) + C1.evidence_refs 标签日期 + 规则发布日 | {"obs_date": "2026-11-23", "value": 159.347, "ref_label": "2026-11-23", "pub_date": "2026-11-23", "basis": "obs=publish(市场/日频序列)"} | {"value": 159.35, "ref_label": "2026-11-23", "obs_upto": "2026-11-23"} | 一致 | agent_judgment.l3.contradictions[0].statement 证据面最新水平清单 / MAP_REPORT 主线综合 |
| #891 | ②/⑬点值格 | snapshot.series_store.DFF 截止日前最近观测(值/观测日) + C1.evidence_refs 标签日期 + 规则发布日 | {"obs_date": "2026-11-19", "value": 3.88, "ref_label": "2026-11-19", "pub_date": "2026-11-20", "basis": "rule:DFF次日(注册表)"} | {"value": 3.88, "ref_label": "2026-11-19", "obs_upto": "2026-11-23"} | 一致 | agent_judgment.l3.contradictions[0].statement 证据面最新水平清单 / MAP_REPORT 主线综合 |
| #892 | ②/⑬点值格 | snapshot.series_store.JP_POLICY_RATE 截止日前最近观测(值/观测日) + C1.evidence_refs 标签日期 + 规则发布日 | {"obs_date": "2026-10-01", "value": 1.227, "ref_label": "2026-10-01", "pub_date": "2026-11-05", "basis": "rule"} | {"value": 1.227, "ref_label": "2026-10-01", "obs_upto": "2026-11-23"} | 一致 | agent_judgment.l3.contradictions[0].statement 证据面最新水平清单 / MAP_REPORT 主线综合 |
| #893 | ②/⑬点值格 | snapshot.series_store.CN_PPI_YOY 截止日前最近观测(值/观测日) + C1.evidence_refs 标签日期 + 规则发布日 | {"obs_date": "2026-10-01", "value": 5.7, "ref_label": "2026-10-31", "pub_date": "2026-11-09", "basis": "rule"} | {"value": 5.7, "ref_label": "2026-10-31", "obs_upto": "2026-11-23"} | 一致 | agent_judgment.l3.contradictions[0].statement 证据面最新水平清单 / MAP_REPORT 主线综合 |
| #894 | ②/⑬点值格 | snapshot.series_store.CN_CPI_YOY 截止日前最近观测(值/观测日) + C1.evidence_refs 标签日期 + 规则发布日 | {"obs_date": "2026-10-01", "value": 0.7, "ref_label": null, "pub_date": "2026-11-09", "basis": "rule"} | {"value": 0.7, "ref_label": null, "obs_upto": "2026-11-23"} | 一致 | agent_judgment.l3.contradictions[0].statement 证据面最新水平清单 / MAP_REPORT 主线综合 |
| #895 | ②/⑬点值格 | snapshot.series_store.CN_PMI_MFG 截止日前最近观测(值/观测日) + C1.evidence_refs 标签日期 + 规则发布日 | {"obs_date": "2026-10-01", "value": 49.3, "ref_label": null, "pub_date": "2026-10-30", "basis": "rule"} | {"value": 49.3, "ref_label": null, "obs_upto": "2026-11-23"} | 一致 | agent_judgment.l3.contradictions[0].statement 证据面最新水平清单 / MAP_REPORT 主线综合 |
| #901 | ②/⑬点值格 | snapshot.series_store.CN_PPI_YOY 截止日前最近观测(值/观测日) | ["2026-10-01", 5.7] | [5.7, "2026-10"] | 一致 | agent_judgment.l3.contradictions[2].statement 最新读数括注 |
| #902 | ②/⑬点值格 | snapshot.series_store.CN_CPI_YOY 截止日前最近观测(值/观测日) | ["2026-10-01", 0.7] | [0.7, "2026-10"] | 一致 | agent_judgment.l3.contradictions[2].statement 最新读数括注 |
| #903 | ②/⑬点值格 | snapshot.series_store.CN_PMI_MFG 截止日前最近观测(值/观测日) | ["2026-10-01", 49.3] | [49.3, "2026-10"] | 一致 | agent_judgment.l3.contradictions[2].statement 最新读数括注 |

### 2.2 ⑧同步面/当时可知(记录 102 / 一致 102 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #129 | ⑧同步面/当时可知 | snapshot.series_store.US_REAL_GDP @2024-07-01 与 @2024-10-01 | {"v0": 2.947873378867638, "v1": 2.641872076237606, "chg": -0.306, "dir": "down"} | {"v0": 2.9479, "v1": 2.6419, "chg": -0.306, "label": "基准"} | 一致 | MAP_REPORT 历史段 2025-03 地区×维度同步面表(增长/US) |
| #130 | ⑧同步面/当时可知 | snapshot.series_store.CPI @2024-11 与 @2025-02 | {"v0": 2.719472461284833, "v1": 2.8015834477613355, "chg": 0.0821, "dir": "up"} | {"v0": 2.7195, "v1": 2.8016, "chg": 0.0821, "label": "基准"} | 一致 | MAP_REPORT 历史段 2025-03 地区×维度同步面表(通胀/US) |
| #131 | ⑧同步面/当时可知 | snapshot.series_store.DFEDTARU @2024-12-31 与 @2025-03-31 | {"v0": 4.5, "v1": 4.5, "chg": 0.0, "dir": "flat"} | {"v0": 4.5, "v1": 4.5, "chg": 0.0, "label": "基准"} | 一致 | MAP_REPORT 历史段 2025-03 地区×维度同步面表(政策/US) |
| #132 | ⑧同步面/当时可知 | snapshot.series_store.CN_PMI_MFG @2024-12 与 @2025-03 | {"v0": 50.1, "v1": 50.5, "chg": 0.4, "dir": "up"} | {"v0": 50.1, "v1": 50.5, "chg": 0.4, "label": "分化"} | 一致 | MAP_REPORT 历史段 2025-03 地区×维度同步面表(增长/CN) |
| #133 | ⑧同步面/当时可知 | snapshot.series_store.CN_CPI_YOY @2024-11 与 @2025-02 | {"v0": 0.2, "v1": -0.7, "chg": -0.9, "dir": "down"} | {"v0": 0.2, "v1": -0.7, "chg": -0.9, "label": "分化"} | 一致 | MAP_REPORT 历史段 2025-03 地区×维度同步面表(通胀/CN) |
| #134 | ⑧同步面/当时可知 | snapshot.series_store.CN_LPR_1Y @2024-12-20 与 @2025-03-20 | {"v0": 3.1, "v1": 3.1, "chg": 0.0, "dir": "flat"} | {"v0": 3.1, "v1": 3.1, "chg": 0.0, "label": "同步"} | 一致 | MAP_REPORT 历史段 2025-03 地区×维度同步面表(政策/CN) |
| #135 | ⑧同步面/当时可知 | snapshot.series_store.EA_REAL_GDP_YOY @2024-07-01 与 @2024-10-01 | {"v0": 1.31, "v1": 1.56, "chg": 0.25, "dir": "up"} | {"v0": 1.31, "v1": 1.56, "chg": 0.25, "label": "分化"} | 一致 | MAP_REPORT 历史段 2025-03 地区×维度同步面表(增长/EA) |
| #136 | ⑧同步面/当时可知 | snapshot.series_store.EA_HICP_YOY @2024-12 与 @2025-02 | {"v0": 2.4, "v1": 2.3, "chg": -0.1, "dir": "down"} | {"v0": 2.4, "v1": 2.3, "chg": -0.1, "label": "分化"} | 一致 | MAP_REPORT 历史段 2025-03 地区×维度同步面表(通胀/EA) |
| #137 | ⑧同步面/当时可知 | snapshot.series_store.ECB_MRO @2024-12-18 与 @2025-03-12 | {"v0": 3.15, "v1": 2.65, "chg": -0.5, "dir": "down"} | {"v0": 3.15, "v1": 2.65, "chg": -0.5, "label": "分化"} | 一致 | MAP_REPORT 历史段 2025-03 地区×维度同步面表(政策/EA) |
| #138 | ⑧同步面/当时可知 | snapshot.series_store.JP_REAL_GDP_YOY @2024-07-01 与 @2024-10-01 | {"v0": 1.11, "v1": 1.01, "chg": -0.1, "dir": "down"} | {"v0": 1.11, "v1": 1.01, "chg": -0.1, "label": "同步"} | 一致 | MAP_REPORT 历史段 2025-03 地区×维度同步面表(增长/JP) |
| #139 | ⑧同步面/当时可知 | snapshot.series_store.JP_CPI_YOY @2024-11 与 @2025-02 | {"v0": 2.92, "v1": 3.66, "chg": 0.74, "dir": "up"} | {"v0": 2.92, "v1": 3.66, "chg": 0.74, "label": "同步"} | 一致 | MAP_REPORT 历史段 2025-03 地区×维度同步面表(通胀/JP) |
| #140 | ⑧同步面/当时可知 | snapshot.series_store.JP_POLICY_RATE @2024-11 与 @2025-02 | {"v0": 0.227, "v1": 0.478, "chg": 0.251, "dir": "up"} | {"v0": 0.227, "v1": 0.478, "chg": 0.251, "label": "分化"} | 一致 | MAP_REPORT 历史段 2025-03 地区×维度同步面表(政策/JP) |
| #141 | ⑧同步面/当时可知 | 同步面表同步格计数(由上 9 格标签直算) | 3 | 3 | 一致 | agent_judgment.history_periods[2025-03].other_regions_sync |
| #142 | ⑧同步面/当时可知 | snapshot.series_store.US_REAL_GDP @2021-10-01 与 @2022-01-01 | {"v0": 5.818236961988643, "v1": 3.975354840109646, "chg": -1.8429, "dir": "down"} | {"v0": 5.8182, "v1": 3.9754, "chg": -1.8428, "label": "基准"} | 一致 | MAP_REPORT 历史段 2022-06 地区×维度同步面表(增长/US) |
| #143 | ⑧同步面/当时可知 | snapshot.series_store.CPI @2022-02 与 @2022-05 | {"v0": 7.937278766517819, "v1": 8.538171195642065, "chg": 0.6009, "dir": "up"} | {"v0": 7.9373, "v1": 8.5382, "chg": 0.6009, "label": "基准"} | 一致 | MAP_REPORT 历史段 2022-06 地区×维度同步面表(通胀/US) |
| #144 | ⑧同步面/当时可知 | snapshot.series_store.DFEDTARU @2022-03-31 与 @2022-06-30 | {"v0": 0.5, "v1": 1.75, "chg": 1.25, "dir": "up"} | {"v0": 0.5, "v1": 1.75, "chg": 1.25, "label": "基准"} | 一致 | MAP_REPORT 历史段 2022-06 地区×维度同步面表(政策/US) |
| #145 | ⑧同步面/当时可知 | snapshot.series_store.CN_PMI_MFG @2022-03 与 @2022-06 | {"v0": 49.5, "v1": 50.2, "chg": 0.7, "dir": "up"} | {"v0": 49.5, "v1": 50.2, "chg": 0.7, "label": "分化"} | 一致 | MAP_REPORT 历史段 2022-06 地区×维度同步面表(增长/CN) |
| #146 | ⑧同步面/当时可知 | snapshot.series_store.CN_CPI_YOY @2022-02 与 @2022-05 | {"v0": 0.9, "v1": 2.1, "chg": 1.2, "dir": "up"} | {"v0": 0.9, "v1": 2.1, "chg": 1.2, "label": "同步"} | 一致 | MAP_REPORT 历史段 2022-06 地区×维度同步面表(通胀/CN) |
| #147 | ⑧同步面/当时可知 | snapshot.series_store.CN_LPR_1Y @2022-03-21 与 @2022-06-20 | {"v0": 3.7, "v1": 3.7, "chg": 0.0, "dir": "flat"} | {"v0": 3.7, "v1": 3.7, "chg": 0.0, "label": "分化"} | 一致 | MAP_REPORT 历史段 2022-06 地区×维度同步面表(政策/CN) |
| #148 | ⑧同步面/当时可知 | snapshot.series_store.EA_REAL_GDP_YOY @2021-10-01 与 @2022-01-01 | {"v0": 5.68, "v1": 5.58, "chg": -0.1, "dir": "down"} | {"v0": 5.68, "v1": 5.58, "chg": -0.1, "label": "同步"} | 一致 | MAP_REPORT 历史段 2022-06 地区×维度同步面表(增长/EA) |
| #149 | ⑧同步面/当时可知 | snapshot.series_store.EA_HICP_YOY @2022-03 与 @2022-05 | {"v0": 7.4, "v1": 8.1, "chg": 0.7, "dir": "up"} | {"v0": 7.4, "v1": 8.1, "chg": 0.7, "label": "同步"} | 一致 | MAP_REPORT 历史段 2022-06 地区×维度同步面表(通胀/EA) |
| #150 | ⑧同步面/当时可知 | snapshot.series_store.ECB_MRO @2019-09-18 与 @2019-09-18 | {"v0": 0.0, "v1": 0.0, "chg": 0.0, "dir": "flat"} | {"v0": 0.0, "v1": 0.0, "chg": 0.0, "label": "分化"} | 一致 | MAP_REPORT 历史段 2022-06 地区×维度同步面表(政策/EA) |
| #151 | ⑧同步面/当时可知 | snapshot.series_store.JP_REAL_GDP_YOY @2021-10-01 与 @2022-01-01 | {"v0": 2.8, "v1": 1.15, "chg": -1.65, "dir": "down"} | {"v0": 2.8, "v1": 1.15, "chg": -1.65, "label": "同步"} | 一致 | MAP_REPORT 历史段 2022-06 地区×维度同步面表(增长/JP) |
| #152 | ⑧同步面/当时可知 | snapshot.series_store.JP_CPI_YOY @2022-02 与 @2022-05 | {"v0": 0.95, "v1": 2.46, "chg": 1.51, "dir": "up"} | {"v0": 0.95, "v1": 2.46, "chg": 1.51, "label": "同步"} | 一致 | MAP_REPORT 历史段 2022-06 地区×维度同步面表(通胀/JP) |
| #153 | ⑧同步面/当时可知 | snapshot.series_store.JP_POLICY_RATE @2022-02 与 @2022-05 | {"v0": -0.018, "v1": -0.018, "chg": 0.0, "dir": "flat"} | {"v0": -0.018, "v1": -0.018, "chg": 0.0, "label": "分化"} | 一致 | MAP_REPORT 历史段 2022-06 地区×维度同步面表(政策/JP) |
| #154 | ⑧同步面/当时可知 | 同步面表同步格计数(由上 9 格标签直算) | 5 | 5 | 一致 | agent_judgment.history_periods[2022-06].other_regions_sync |
| #155 | ⑧同步面/当时可知 | snapshot.series_store.US_REAL_GDP @2023-04-01 与 @2023-07-01 | {"v0": 2.7359665588717164, "v1": 3.1838716955916224, "chg": 0.4479, "dir": "up"} | {"v0": 2.736, "v1": 3.1839, "chg": 0.4479, "label": "基准"} | 一致 | MAP_REPORT 历史段 2023-10 地区×维度同步面表(增长/US) |
| #156 | ⑧同步面/当时可知 | snapshot.series_store.CPI @2023-06 与 @2023-09 | {"v0": 3.070617072997095, "v1": 3.687206638119256, "chg": 0.6166, "dir": "up"} | {"v0": 3.0706, "v1": 3.6872, "chg": 0.6166, "label": "基准"} | 一致 | MAP_REPORT 历史段 2023-10 地区×维度同步面表(通胀/US) |
| #157 | ⑧同步面/当时可知 | snapshot.series_store.DFEDTARU @2023-07-31 与 @2023-10-31 | {"v0": 5.5, "v1": 5.5, "chg": 0.0, "dir": "flat"} | {"v0": 5.5, "v1": 5.5, "chg": 0.0, "label": "基准"} | 一致 | MAP_REPORT 历史段 2023-10 地区×维度同步面表(政策/US) |
| #158 | ⑧同步面/当时可知 | snapshot.series_store.CN_PMI_MFG @2023-07 与 @2023-10 | {"v0": 49.3, "v1": 49.5, "chg": 0.2, "dir": "up"} | {"v0": 49.3, "v1": 49.5, "chg": 0.2, "label": "同步"} | 一致 | MAP_REPORT 历史段 2023-10 地区×维度同步面表(增长/CN) |
| #159 | ⑧同步面/当时可知 | snapshot.series_store.CN_CPI_YOY @2023-06 与 @2023-09 | {"v0": 0.0, "v1": 0.0, "chg": 0.0, "dir": "flat"} | {"v0": 0.0, "v1": 0.0, "chg": 0.0, "label": "分化"} | 一致 | MAP_REPORT 历史段 2023-10 地区×维度同步面表(通胀/CN) |
| #160 | ⑧同步面/当时可知 | snapshot.series_store.CN_LPR_1Y @2023-07-20 与 @2023-10-20 | {"v0": 3.55, "v1": 3.45, "chg": -0.1, "dir": "down"} | {"v0": 3.55, "v1": 3.45, "chg": -0.1, "label": "分化"} | 一致 | MAP_REPORT 历史段 2023-10 地区×维度同步面表(政策/CN) |
| #161 | ⑧同步面/当时可知 | snapshot.series_store.EA_REAL_GDP_YOY @2023-01-01 与 @2023-04-01 | {"v0": 1.22, "v1": 0.48, "chg": -0.74, "dir": "down"} | {"v0": 1.22, "v1": 0.48, "chg": -0.74, "label": "分化"} | 一致 | MAP_REPORT 历史段 2023-10 地区×维度同步面表(增长/EA) |
| #162 | ⑧同步面/当时可知 | snapshot.series_store.EA_HICP_YOY @2023-07 与 @2023-10 | {"v0": 5.3, "v1": 2.9, "chg": -2.4, "dir": "down"} | {"v0": 5.3, "v1": 2.9, "chg": -2.4, "label": "分化"} | 一致 | MAP_REPORT 历史段 2023-10 地区×维度同步面表(通胀/EA) |
| #163 | ⑧同步面/当时可知 | snapshot.series_store.ECB_MRO @2023-06-21 与 @2023-09-20 | {"v0": 4.0, "v1": 4.5, "chg": 0.5, "dir": "up"} | {"v0": 4.0, "v1": 4.5, "chg": 0.5, "label": "分化"} | 一致 | MAP_REPORT 历史段 2023-10 地区×维度同步面表(政策/EA) |
| #164 | ⑧同步面/当时可知 | snapshot.series_store.JP_REAL_GDP_YOY @2023-01-01 与 @2023-04-01 | {"v0": 2.06, "v1": 1.17, "chg": -0.89, "dir": "down"} | {"v0": 2.06, "v1": 1.17, "chg": -0.89, "label": "分化"} | 一致 | MAP_REPORT 历史段 2023-10 地区×维度同步面表(增长/JP) |
| #165 | ⑧同步面/当时可知 | snapshot.series_store.JP_CPI_YOY @2023-06 与 @2023-09 | {"v0": 3.3, "v1": 3.05, "chg": -0.25, "dir": "down"} | {"v0": 3.3, "v1": 3.05, "chg": -0.25, "label": "分化"} | 一致 | MAP_REPORT 历史段 2023-10 地区×维度同步面表(通胀/JP) |
| #166 | ⑧同步面/当时可知 | snapshot.series_store.JP_POLICY_RATE @2023-06 与 @2023-09 | {"v0": -0.066, "v1": -0.054, "chg": 0.012, "dir": "up"} | {"v0": -0.066, "v1": -0.054, "chg": 0.012, "label": "分化"} | 一致 | MAP_REPORT 历史段 2023-10 地区×维度同步面表(政策/JP) |
| #167 | ⑧同步面/当时可知 | 同步面表同步格计数(由上 9 格标签直算) | 1 | 1 | 一致 | agent_judgment.history_periods[2023-10].other_regions_sync |
| #168 | ⑧同步面/当时可知 | snapshot.series_store.CPI@2025-02(当时可知面; 规则发布日 2025-03-13) | 319.679 | 319.679 | 一致 | MAP_REPORT 历史段 2025-03 当时可知面表 |
| #169 | ⑧同步面/当时可知 | snapshot.series_store.CORE_PCE@2025-02(当时可知面; 规则发布日 2025-03-30) | 125.002 | 125.002 | 一致 | MAP_REPORT 历史段 2025-03 当时可知面表 |
| #170 | ⑧同步面/当时可知 | snapshot.series_store.INDPRO@2025-02(当时可知面; 规则发布日 2025-03-15) | 101.0993 | 101.099 | 一致 | MAP_REPORT 历史段 2025-03 当时可知面表 |
| #171 | ⑧同步面/当时可知 | snapshot.series_store.UNEMPLOYMENT@2025-02(当时可知面; 规则发布日 2025-03-05) | 4.2 | 4.2 | 一致 | MAP_REPORT 历史段 2025-03 当时可知面表 |
| #172 | ⑧同步面/当时可知 | snapshot.series_store.US_REAL_GDP@2024-10-01(当时可知面; 规则发布日 2025-01-29) | 23641.759 | 23641.8 | 一致 | MAP_REPORT 历史段 2025-03 当时可知面表 |
| #173 | ⑧同步面/当时可知 | snapshot.series_store.CN_PPI_YOY@2025-02(当时可知面; 规则发布日 2025-03-09) | -2.2 | -2.2 | 一致 | MAP_REPORT 历史段 2025-03 当时可知面表 |
| #174 | ⑧同步面/当时可知 | snapshot.series_store.CN_CPI_YOY@2025-02(当时可知面; 规则发布日 2025-03-09) | -0.7 | -0.7 | 一致 | MAP_REPORT 历史段 2025-03 当时可知面表 |
| #175 | ⑧同步面/当时可知 | snapshot.series_store.EA_HICP_YOY@2025-02(当时可知面; 规则发布日 2025-02-28) | 2.3 | 2.3 | 一致 | MAP_REPORT 历史段 2025-03 当时可知面表 |
| #176 | ⑧同步面/当时可知 | snapshot.series_store.JP_CPI_YOY@2025-02(当时可知面; 规则发布日 2025-03-20) | 3.66 | 3.66 | 一致 | MAP_REPORT 历史段 2025-03 当时可知面表 |
| #177 | ⑧同步面/当时可知 | snapshot.series_store.CPI@2022-05(当时可知面; 规则发布日 2022-06-13) | 291.298 | 291.298 | 一致 | MAP_REPORT 历史段 2022-06 当时可知面表 |
| #178 | ⑧同步面/当时可知 | snapshot.series_store.CORE_PCE@2022-05(当时可知面; 规则发布日 2022-06-30) | 113.571 | 113.571 | 一致 | MAP_REPORT 历史段 2022-06 当时可知面表 |
| #179 | ⑧同步面/当时可知 | snapshot.series_store.INDPRO@2022-05(当时可知面; 规则发布日 2022-06-15) | 101.3335 | 101.334 | 一致 | MAP_REPORT 历史段 2022-06 当时可知面表 |
| #180 | ⑧同步面/当时可知 | snapshot.series_store.UNEMPLOYMENT@2022-05(当时可知面; 规则发布日 2022-06-05) | 3.6 | 3.6 | 一致 | MAP_REPORT 历史段 2022-06 当时可知面表 |
| #181 | ⑧同步面/当时可知 | snapshot.series_store.US_REAL_GDP@2022-01-01(当时可知面; 规则发布日 2022-04-29) | 21945.682 | 21945.7 | 一致 | MAP_REPORT 历史段 2022-06 当时可知面表 |
| #182 | ⑧同步面/当时可知 | snapshot.series_store.CN_PPI_YOY@2022-05(当时可知面; 规则发布日 2022-06-09) | 6.4 | 6.4 | 一致 | MAP_REPORT 历史段 2022-06 当时可知面表 |
| #183 | ⑧同步面/当时可知 | snapshot.series_store.CN_CPI_YOY@2022-05(当时可知面; 规则发布日 2022-06-09) | 2.1 | 2.1 | 一致 | MAP_REPORT 历史段 2022-06 当时可知面表 |
| #184 | ⑧同步面/当时可知 | snapshot.series_store.EA_HICP_YOY@2022-05(当时可知面; 规则发布日 2022-05-31) | 8.1 | 8.1 | 一致 | MAP_REPORT 历史段 2022-06 当时可知面表 |
| #185 | ⑧同步面/当时可知 | snapshot.series_store.JP_CPI_YOY@2022-05(当时可知面; 规则发布日 2022-06-20) | 2.46 | 2.46 | 一致 | MAP_REPORT 历史段 2022-06 当时可知面表 |
| #186 | ⑧同步面/当时可知 | snapshot.series_store.CPI@2023-09(当时可知面; 规则发布日 2023-10-13) | 307.276 | 307.276 | 一致 | MAP_REPORT 历史段 2023-10 当时可知面表 |
| #187 | ⑧同步面/当时可知 | snapshot.series_store.CORE_PCE@2023-09(当时可知面; 规则发布日 2023-10-30) | 120.053 | 120.053 | 一致 | MAP_REPORT 历史段 2023-10 当时可知面表 |
| #188 | ⑧同步面/当时可知 | snapshot.series_store.INDPRO@2023-09(当时可知面; 规则发布日 2023-10-15) | 101.0211 | 101.021 | 一致 | MAP_REPORT 历史段 2023-10 当时可知面表 |
| #189 | ⑧同步面/当时可知 | snapshot.series_store.UNEMPLOYMENT@2023-09(当时可知面; 规则发布日 2023-10-05) | 3.7 | 3.7 | 一致 | MAP_REPORT 历史段 2023-10 当时可知面表 |
| #190 | ⑧同步面/当时可知 | snapshot.series_store.US_REAL_GDP@2023-07-01(当时可知面; 规则发布日 2023-10-29) | 22828.796 | 22828.8 | 一致 | MAP_REPORT 历史段 2023-10 当时可知面表 |
| #191 | ⑧同步面/当时可知 | snapshot.series_store.CN_PPI_YOY@2023-09(当时可知面; 规则发布日 2023-10-09) | -2.5 | -2.5 | 一致 | MAP_REPORT 历史段 2023-10 当时可知面表 |
| #192 | ⑧同步面/当时可知 | snapshot.series_store.CN_CPI_YOY@2023-09(当时可知面; 规则发布日 2023-10-09) | 0.0 | 0.0 | 一致 | MAP_REPORT 历史段 2023-10 当时可知面表 |
| #193 | ⑧同步面/当时可知 | snapshot.series_store.EA_HICP_YOY@2023-10(当时可知面; 规则发布日 2023-10-31) | 2.9 | 2.9 | 一致 | MAP_REPORT 历史段 2023-10 当时可知面表 |
| #194 | ⑧同步面/当时可知 | snapshot.series_store.JP_CPI_YOY@2023-09(当时可知面; 规则发布日 2023-10-20) | 3.05 | 3.05 | 一致 | MAP_REPORT 历史段 2023-10 当时可知面表 |
| #195 | ⑧同步面/当时可知 | snapshot.series_store.CPI@2025-03 + 发布规则/日历(直算发布日 2025-04-13) | {"value": 319.785, "pub": "2025-04-13"} | {"value": 319.785, "pub": "2025-04-13"} | 一致 | MAP_REPORT 历史段事后段表 |
| #196 | ⑧同步面/当时可知 | snapshot.series_store.CPI@2025-11 + 发布规则/日历(直算发布日 2025-12-18) | {"value": 325.063, "pub": "2025-12-18"} | {"value": 325.063, "pub": "2025-12-18"} | 一致 | MAP_REPORT 历史段事后段表 |
| #197 | ⑧同步面/当时可知 | snapshot.series_store.CORE_PCE@2025-03 + 发布规则/日历(直算发布日 2025-04-30) | {"value": 125.144, "pub": "2025-04-30"} | {"value": 125.144, "pub": "2025-04-30"} | 一致 | MAP_REPORT 历史段事后段表 |
| #198 | ⑧同步面/当时可知 | snapshot.series_store.CORE_PCE@2025-10 + 发布规则/日历(直算发布日 2026-01-22) | {"value": 127.165, "pub": "2026-01-22"} | {"value": 127.165, "pub": "2026-01-22"} | 一致 | MAP_REPORT 历史段事后段表 |
| #199 | ⑧同步面/当时可知 | snapshot.series_store.INDPRO@2025-03 + 发布规则/日历(直算发布日 2025-04-15) | {"value": 101.0404, "pub": "2025-04-15"} | {"value": 101.04, "pub": "2025-04-15"} | 一致 | MAP_REPORT 历史段事后段表 |
| #200 | ⑧同步面/当时可知 | snapshot.series_store.INDPRO@2025-09 + 发布规则/日历(直算发布日 2025-12-03) | {"value": 101.668, "pub": "2025-12-03"} | {"value": 101.668, "pub": "2025-12-03"} | 一致 | MAP_REPORT 历史段事后段表 |
| #201 | ⑧同步面/当时可知 | snapshot.series_store.UNEMPLOYMENT@2025-03 + 发布规则/日历(直算发布日 2025-04-05) | {"value": 4.2, "pub": "2025-04-05"} | {"value": 4.2, "pub": "2025-04-05"} | 一致 | MAP_REPORT 历史段事后段表 |
| #202 | ⑧同步面/当时可知 | snapshot.series_store.UNEMPLOYMENT@2025-09 + 发布规则/日历(直算发布日 2025-11-20) | {"value": 4.4, "pub": "2025-11-20"} | {"value": 4.4, "pub": "2025-11-20"} | 一致 | MAP_REPORT 历史段事后段表 |
| #203 | ⑧同步面/当时可知 | snapshot.series_store.UNEMPLOYMENT@2025-11 + 发布规则/日历(直算发布日 2025-12-16) | {"value": 4.5, "pub": "2025-12-16"} | {"value": 4.5, "pub": "2025-12-16"} | 一致 | MAP_REPORT 历史段事后段表 |
| #204 | ⑧同步面/当时可知 | snapshot.series_store.US_REAL_GDP@2025-07 + 发布规则/日历(直算发布日 2025-12-23) | {"value": 24112.966, "pub": "2025-12-23"} | {"value": 24113, "pub": "2025-12-23"} | 一致 | MAP_REPORT 历史段事后段表 |
| #205 | ⑧同步面/当时可知 | snapshot.series_store.CN_PPI_YOY@2025-03 + 发布规则/日历(直算发布日 2025-04-09) | {"value": -2.5, "pub": "2025-04-09"} | {"value": -2.5, "pub": "2025-04-09"} | 一致 | MAP_REPORT 历史段事后段表 |
| #206 | ⑧同步面/当时可知 | snapshot.series_store.CN_CPI_YOY@2025-03 + 发布规则/日历(直算发布日 2025-04-09) | {"value": -0.1, "pub": "2025-04-09"} | {"value": -0.1, "pub": "2025-04-09"} | 一致 | MAP_REPORT 历史段事后段表 |
| #207 | ⑧同步面/当时可知 | snapshot.series_store.EA_HICP_YOY@2025-03 + 发布规则/日历(直算发布日 2025-04-01) | {"value": 2.2, "pub": "2025-04-01"} | {"value": 2.2, "pub": "2025-04-01"} | 一致 | MAP_REPORT 历史段事后段表 |
| #208 | ⑧同步面/当时可知 | snapshot.series_store.JP_CPI_YOY@2025-03 + 发布规则/日历(直算发布日 2025-04-20) | {"value": 3.62, "pub": "2025-04-20"} | {"value": 3.62, "pub": "2025-04-20"} | 一致 | MAP_REPORT 历史段事后段表 |
| #209 | ⑧同步面/当时可知 | snapshot.series_store.CPI@2022-06 + 发布规则/日历(直算发布日 2022-07-13) | {"value": 294.957, "pub": "2022-07-13"} | {"value": 294.957, "pub": "2022-07-13"} | 一致 | MAP_REPORT 历史段事后段表 |
| #210 | ⑧同步面/当时可知 | snapshot.series_store.CORE_PCE@2022-06 + 发布规则/日历(直算发布日 2022-07-30) | {"value": 114.273, "pub": "2022-07-30"} | {"value": 114.273, "pub": "2022-07-30"} | 一致 | MAP_REPORT 历史段事后段表 |
| #211 | ⑧同步面/当时可知 | snapshot.series_store.INDPRO@2022-06 + 发布规则/日历(直算发布日 2022-07-15) | {"value": 101.018, "pub": "2022-07-15"} | {"value": 101.018, "pub": "2022-07-15"} | 一致 | MAP_REPORT 历史段事后段表 |
| #212 | ⑧同步面/当时可知 | snapshot.series_store.UNEMPLOYMENT@2022-06 + 发布规则/日历(直算发布日 2022-07-05) | {"value": 3.6, "pub": "2022-07-05"} | {"value": 3.6, "pub": "2022-07-05"} | 一致 | MAP_REPORT 历史段事后段表 |
| #213 | ⑧同步面/当时可知 | snapshot.series_store.CN_PPI_YOY@2022-06 + 发布规则/日历(直算发布日 2022-07-09) | {"value": 6.1, "pub": "2022-07-09"} | {"value": 6.1, "pub": "2022-07-09"} | 一致 | MAP_REPORT 历史段事后段表 |
| #214 | ⑧同步面/当时可知 | snapshot.series_store.CN_CPI_YOY@2022-06 + 发布规则/日历(直算发布日 2022-07-09) | {"value": 2.5, "pub": "2022-07-09"} | {"value": 2.5, "pub": "2022-07-09"} | 一致 | MAP_REPORT 历史段事后段表 |
| #215 | ⑧同步面/当时可知 | snapshot.series_store.EA_HICP_YOY@2022-06 + 发布规则/日历(直算发布日 2022-07-01) | {"value": 8.6, "pub": "2022-07-01"} | {"value": 8.6, "pub": "2022-07-01"} | 一致 | MAP_REPORT 历史段事后段表 |
| #216 | ⑧同步面/当时可知 | snapshot.series_store.JP_CPI_YOY@2022-06 + 发布规则/日历(直算发布日 2022-07-20) | {"value": 2.35, "pub": "2022-07-20"} | {"value": 2.35, "pub": "2022-07-20"} | 一致 | MAP_REPORT 历史段事后段表 |
| #217 | ⑧同步面/当时可知 | snapshot.series_store.CPI@2023-10 + 发布规则/日历(直算发布日 2023-11-13) | {"value": 307.696, "pub": "2023-11-13"} | {"value": 307.696, "pub": "2023-11-13"} | 一致 | MAP_REPORT 历史段事后段表 |
| #218 | ⑧同步面/当时可知 | snapshot.series_store.CORE_PCE@2023-10 + 发布规则/日历(直算发布日 2023-11-30) | {"value": 120.321, "pub": "2023-11-30"} | {"value": 120.321, "pub": "2023-11-30"} | 一致 | MAP_REPORT 历史段事后段表 |
| #219 | ⑧同步面/当时可知 | snapshot.series_store.INDPRO@2023-10 + 发布规则/日历(直算发布日 2023-11-15) | {"value": 100.4689, "pub": "2023-11-15"} | {"value": 100.469, "pub": "2023-11-15"} | 一致 | MAP_REPORT 历史段事后段表 |
| #220 | ⑧同步面/当时可知 | snapshot.series_store.UNEMPLOYMENT@2023-10 + 发布规则/日历(直算发布日 2023-11-05) | {"value": 3.9, "pub": "2023-11-05"} | {"value": 3.9, "pub": "2023-11-05"} | 一致 | MAP_REPORT 历史段事后段表 |
| #221 | ⑧同步面/当时可知 | snapshot.series_store.US_REAL_GDP@2023-10 + 发布规则/日历(直算发布日 2024-01-29) | {"value": 23033.25, "pub": "2024-01-29"} | {"value": 23033.2, "pub": "2024-01-29"} | 一致 | MAP_REPORT 历史段事后段表 |
| #222 | ⑧同步面/当时可知 | snapshot.series_store.CN_PPI_YOY@2023-10 + 发布规则/日历(直算发布日 2023-11-09) | {"value": -2.6, "pub": "2023-11-09"} | {"value": -2.6, "pub": "2023-11-09"} | 一致 | MAP_REPORT 历史段事后段表 |
| #223 | ⑧同步面/当时可知 | snapshot.series_store.CN_CPI_YOY@2023-10 + 发布规则/日历(直算发布日 2023-11-09) | {"value": -0.2, "pub": "2023-11-09"} | {"value": -0.2, "pub": "2023-11-09"} | 一致 | MAP_REPORT 历史段事后段表 |
| #224 | ⑧同步面/当时可知 | snapshot.series_store.JP_CPI_YOY@2023-10 + 发布规则/日历(直算发布日 2023-11-20) | {"value": 3.32, "pub": "2023-11-20"} | {"value": 3.32, "pub": "2023-11-20"} | 一致 | MAP_REPORT 历史段事后段表 |
| #225 | ⑧同步面/当时可知 | snapshot.series_store.CPI@2025-10(事后段表记"数据不可得") | null | null | 一致 | MAP_REPORT 2025-03 事后段表 |
| #226 | ⑧同步面/当时可知 | snapshot.series_store.UNEMPLOYMENT@2025-10(事后段表记"数据不可得") | null | null | 一致 | MAP_REPORT 2025-03 事后段表 |
| #870 | ⑧同步面/当时可知 | history_periods[2025-03].other_regions_sync "截至2025-03-31已发布数据显示,…同比YYYY-MM为V" 四项: (叙述观测月, 序列值, 截止前可见最新观测月, 可见值) | [["2025-02", 2.3, "2025-02", 2.3], ["2025-02", 3.66, "2025-02", 3.66], ["2025-02", -2.2, "2025-02", -2.2], ["2025-02", -0.7, "2025-02", -0.7]] | [["2025-02", 2.3, "2025-02", 2.3], ["2025-02", 3.66, "2025-02", 3.66], ["2025-02", -2.2, "2025-02", -2.2], ["2025-02", -0.7, "2025-02", -0.7]] | 一致 | agent_judgment.history_periods[2025-03].other_regions_sync / MAP_REPORT 历史段 "当时同步性" |
| #871 | ⑧同步面/当时可知 | history_periods[2022-06].other_regions_sync "截至2022-06-30已发布数据显示,…同比YYYY-MM为V" 四项: (叙述观测月, 序列值, 截止前可见最新观测月, 可见值) | [["2022-05", 8.1, "2022-05", 8.1], ["2022-05", 2.46, "2022-05", 2.46], ["2022-05", 6.4, "2022-05", 6.4], ["2022-05", 2.1, "2022-05", 2.1]] | [["2022-05", 8.1, "2022-05", 8.1], ["2022-05", 2.46, "2022-05", 2.46], ["2022-05", 6.4, "2022-05", 6.4], ["2022-05", 2.1, "2022-05", 2.1]] | 一致 | agent_judgment.history_periods[2022-06].other_regions_sync / MAP_REPORT 历史段 "当时同步性" |
| #872 | ⑧同步面/当时可知 | policy narrative: 美国上行<中文数位>个基点、三地持平(三地=CN_LPR_1Y/ECB_MRO/JP_POLICY_RATE, 发布纪律下截止前可见观测) | [125, 125, [0, 0, 0]] | [125, 125, [0, 0, 0]] | 一致 | history_periods[2022-06].other_regions_sync 政策维 |
| #873 | ⑧同步面/当时可知 | history_periods[2023-10].other_regions_sync "截至2023-10-31已发布数据显示,…同比YYYY-MM为V" 四项: (叙述观测月, 序列值, 截止前可见最新观测月, 可见值) | [["2023-10", 2.9, "2023-10", 2.9], ["2023-09", 3.05, "2023-09", 3.05], ["2023-09", -2.5, "2023-09", -2.5], ["2023-09", 0.0, "2023-09", 0.0]] | [["2023-10", 2.9, "2023-10", 2.9], ["2023-09", 3.05, "2023-09", 3.05], ["2023-09", -2.5, "2023-09", -2.5], ["2023-09", 0.0, "2023-09", 0.0]] | 一致 | agent_judgment.history_periods[2023-10].other_regions_sync / MAP_REPORT 历史段 "当时同步性" |

### 2.3 ⑧历史事后窗(记录 110 / 一致 109 / NA 1)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #227 | ⑧历史事后窗 | snapshot.series_store.DFEDTARU(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 0.0 | 0.0 | 一致 | agent_judgment.history_periods[2025-03].ex_post.3m |
| #228 | ⑧历史事后窗 | snapshot.series_store.DFEDTARU(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | -0.25 | -0.25 | 一致 | agent_judgment.history_periods[2025-03].ex_post.6m |
| #229 | ⑧历史事后窗 | snapshot.series_store.DFEDTARU(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | -0.75 | -0.75 | 一致 | agent_judgment.history_periods[2025-03].ex_post.12m |
| #230 | ⑧历史事后窗 | snapshot.series_store.UNEMPLOYMENT(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -0.1 | -0.1 | 一致 | agent_judgment.history_periods[2025-03].ex_post.3m |
| #231 | ⑧历史事后窗 | snapshot.series_store.UNEMPLOYMENT(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 0.2 | 0.2 | 一致 | agent_judgment.history_periods[2025-03].ex_post.6m |
| #232 | ⑧历史事后窗 | snapshot.series_store.UNEMPLOYMENT(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 0.1 | 0.1 | 一致 | agent_judgment.history_periods[2025-03].ex_post.12m |
| #233 | ⑧历史事后窗 | snapshot.series_store.CPI(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 0.516 | 0.52 | 一致 | agent_judgment.history_periods[2025-03].ex_post.3m |
| #234 | ⑧历史事后窗 | snapshot.series_store.CPI(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 1.3947 | 1.39 | 一致 | agent_judgment.history_periods[2025-03].ex_post.6m |
| #235 | ⑧历史事后窗 | snapshot.series_store.CPI(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 3.286 | 3.29 | 一致 | agent_judgment.history_periods[2025-03].ex_post.12m |
| #236 | ⑧历史事后窗 | snapshot.series_store.INDPRO(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 0.4336 | 0.43 | 一致 | agent_judgment.history_periods[2025-03].ex_post.3m |
| #237 | ⑧历史事后窗 | snapshot.series_store.INDPRO(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 0.6211 | 0.62 | 一致 | agent_judgment.history_periods[2025-03].ex_post.6m |
| #238 | ⑧历史事后窗 | snapshot.series_store.INDPRO(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 0.6861 | 0.69 | 一致 | agent_judgment.history_periods[2025-03].ex_post.12m |
| #239 | ⑧历史事后窗 | snapshot.series_store.SPX(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 10.5687 | 10.57 | 一致 | agent_judgment.history_periods[2025-03].ex_post.3m |
| #240 | ⑧历史事后窗 | snapshot.series_store.SPX(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 19.1846 | 19.18 | 一致 | agent_judgment.history_periods[2025-03].ex_post.6m |
| #241 | ⑧历史事后窗 | snapshot.series_store.SPX(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 16.3345 | 16.33 | 一致 | agent_judgment.history_periods[2025-03].ex_post.12m |
| #242 | ⑧历史事后窗 | snapshot.series_store.NIKKEI225(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 13.6726 | 13.67 | 一致 | agent_judgment.history_periods[2025-03].ex_post.3m |
| #243 | ⑧历史事后窗 | snapshot.series_store.NIKKEI225(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 26.153 | 26.15 | 一致 | agent_judgment.history_periods[2025-03].ex_post.6m |
| #244 | ⑧历史事后窗 | snapshot.series_store.NIKKEI225(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 43.3667 | 43.37 | 一致 | agent_judgment.history_periods[2025-03].ex_post.12m |
| #245 | ⑧历史事后窗 | snapshot.series_store.DAX(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 7.8784 | 7.88 | 一致 | agent_judgment.history_periods[2025-03].ex_post.3m |
| #246 | ⑧历史事后窗 | snapshot.series_store.DAX(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 7.748 | 7.75 | 一致 | agent_judgment.history_periods[2025-03].ex_post.6m |
| #247 | ⑧历史事后窗 | snapshot.series_store.DAX(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 2.3306 | 2.33 | 一致 | agent_judgment.history_periods[2025-03].ex_post.12m |
| #248 | ⑧历史事后窗 | snapshot.series_store.SHCOMP(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 3.258 | 3.26 | 一致 | agent_judgment.history_periods[2025-03].ex_post.3m |
| #249 | ⑧历史事后窗 | snapshot.series_store.SHCOMP(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 16.3991 | 16.4 | 一致 | agent_judgment.history_periods[2025-03].ex_post.6m |
| #250 | ⑧历史事后窗 | snapshot.series_store.SHCOMP(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 16.6714 | 16.67 | 一致 | agent_judgment.history_periods[2025-03].ex_post.12m |
| #251 | ⑧历史事后窗 | snapshot.series_store.GOLD_F(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 5.921 | 5.92 | 一致 | agent_judgment.history_periods[2025-03].ex_post.3m |
| #252 | ⑧历史事后窗 | snapshot.series_store.GOLD_F(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 24.0297 | 24.03 | 一致 | agent_judgment.history_periods[2025-03].ex_post.6m |
| #253 | ⑧历史事后窗 | snapshot.series_store.GOLD_F(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 48.828 | 48.83 | 一致 | agent_judgment.history_periods[2025-03].ex_post.12m |
| #254 | ⑧历史事后窗 | snapshot.series_store.DXY(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -7.0339 | -7.03 | 一致 | agent_judgment.history_periods[2025-03].ex_post.3m |
| #255 | ⑧历史事后窗 | snapshot.series_store.DXY(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | -6.1798 | -6.18 | 一致 | agent_judgment.history_periods[2025-03].ex_post.6m |
| #256 | ⑧历史事后窗 | snapshot.series_store.DXY(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | -4.0783 | -4.08 | 一致 | agent_judgment.history_periods[2025-03].ex_post.12m |
| #257 | ⑧历史事后窗 | snapshot.series_store.UST_10Y(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 0.01 | 0.01 | 一致 | agent_judgment.history_periods[2025-03].ex_post.3m |
| #258 | ⑧历史事后窗 | snapshot.series_store.UST_10Y(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | -0.07 | -0.07 | 一致 | agent_judgment.history_periods[2025-03].ex_post.6m |
| #259 | ⑧历史事后窗 | snapshot.series_store.UST_10Y(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 0.07 | 0.07 | 一致 | agent_judgment.history_periods[2025-03].ex_post.12m |
| #260 | ⑧历史事后窗 | snapshot.series_store.DFEDTARU(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 1.5 | 1.5 | 一致 | agent_judgment.history_periods[2022-06].ex_post.3m |
| #261 | ⑧历史事后窗 | snapshot.series_store.DFEDTARU(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 2.75 | 2.75 | 一致 | agent_judgment.history_periods[2022-06].ex_post.6m |
| #262 | ⑧历史事后窗 | snapshot.series_store.DFEDTARU(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 3.5 | 3.5 | 一致 | agent_judgment.history_periods[2022-06].ex_post.12m |
| #263 | ⑧历史事后窗 | snapshot.series_store.UNEMPLOYMENT(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -0.1 | -0.1 | 一致 | agent_judgment.history_periods[2022-06].ex_post.3m |
| #264 | ⑧历史事后窗 | snapshot.series_store.UNEMPLOYMENT(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | -0.1 | -0.1 | 一致 | agent_judgment.history_periods[2022-06].ex_post.6m |
| #265 | ⑧历史事后窗 | snapshot.series_store.UNEMPLOYMENT(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 0.0 | 0.0 | 一致 | agent_judgment.history_periods[2022-06].ex_post.12m |
| #266 | ⑧历史事后窗 | snapshot.series_store.CPI(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 0.4719 | 0.47 | 一致 | agent_judgment.history_periods[2022-06].ex_post.3m |
| #267 | ⑧历史事后窗 | snapshot.series_store.CPI(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 1.3138 | 1.31 | 一致 | agent_judgment.history_periods[2022-06].ex_post.6m |
| #268 | ⑧历史事后窗 | snapshot.series_store.CPI(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 3.0706 | 3.07 | 一致 | agent_judgment.history_periods[2022-06].ex_post.12m |
| #269 | ⑧历史事后窗 | snapshot.series_store.INDPRO(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 0.271 | 0.27 | 一致 | agent_judgment.history_periods[2022-06].ex_post.3m |
| #270 | ⑧历史事后窗 | snapshot.series_store.INDPRO(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | -1.239 | -1.24 | 一致 | agent_judgment.history_periods[2022-06].ex_post.6m |
| #271 | ⑧历史事后窗 | snapshot.series_store.INDPRO(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | -0.8893 | -0.89 | 一致 | agent_judgment.history_periods[2022-06].ex_post.12m |
| #272 | ⑧历史事后窗 | snapshot.series_store.SPX(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -5.2771 | -5.28 | 一致 | agent_judgment.history_periods[2022-06].ex_post.3m |
| #273 | ⑧历史事后窗 | snapshot.series_store.SPX(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 1.4297 | 1.43 | 一致 | agent_judgment.history_periods[2022-06].ex_post.6m |
| #274 | ⑧历史事后窗 | snapshot.series_store.SPX(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 17.5676 | 17.57 | 一致 | agent_judgment.history_periods[2022-06].ex_post.12m |
| #275 | ⑧历史事后窗 | snapshot.series_store.NIKKEI225(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -1.7271 | -1.73 | 一致 | agent_judgment.history_periods[2022-06].ex_post.3m |
| #276 | ⑧历史事后窗 | snapshot.series_store.NIKKEI225(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | -1.1311 | -1.13 | 一致 | agent_judgment.history_periods[2022-06].ex_post.6m |
| #277 | ⑧历史事后窗 | snapshot.series_store.NIKKEI225(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 25.7492 | 25.75 | 一致 | agent_judgment.history_periods[2022-06].ex_post.12m |
| #278 | ⑧历史事后窗 | snapshot.series_store.DAX(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -5.2364 | -5.24 | 一致 | agent_judgment.history_periods[2022-06].ex_post.3m |
| #279 | ⑧历史事后窗 | snapshot.series_store.DAX(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 8.9162 | 8.92 | 一致 | agent_judgment.history_periods[2022-06].ex_post.6m |
| #280 | ⑧历史事后窗 | snapshot.series_store.DAX(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 26.3156 | 26.32 | 一致 | agent_judgment.history_periods[2022-06].ex_post.12m |
| #281 | ⑧历史事后窗 | snapshot.series_store.SHCOMP(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -11.0111 | -11.01 | 一致 | agent_judgment.history_periods[2022-06].ex_post.3m |
| #282 | ⑧历史事后窗 | snapshot.series_store.SHCOMP(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | -9.1025 | -9.1 | 一致 | agent_judgment.history_periods[2022-06].ex_post.6m |
| #283 | ⑧历史事后窗 | snapshot.series_store.SHCOMP(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | -5.7833 | -5.78 | 一致 | agent_judgment.history_periods[2022-06].ex_post.12m |
| #284 | ⑧历史事后窗 | snapshot.series_store.GOLD_F(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -7.4863 | -7.49 | 一致 | agent_judgment.history_periods[2022-06].ex_post.3m |
| #285 | ⑧历史事后窗 | snapshot.series_store.GOLD_F(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 1.0458 | 1.05 | 一致 | agent_judgment.history_periods[2022-06].ex_post.6m |
| #286 | ⑧历史事后窗 | snapshot.series_store.GOLD_F(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 6.7559 | 6.76 | 一致 | agent_judgment.history_periods[2022-06].ex_post.12m |
| #287 | ⑧历史事后窗 | snapshot.series_store.DXY(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 7.0971 | 7.1 | 一致 | agent_judgment.history_periods[2022-06].ex_post.3m |
| #288 | ⑧历史事后窗 | snapshot.series_store.DXY(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | -1.1176 | -1.12 | 一致 | agent_judgment.history_periods[2022-06].ex_post.6m |
| #289 | ⑧历史事后窗 | snapshot.series_store.DXY(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | -1.7003 | -1.7 | 一致 | agent_judgment.history_periods[2022-06].ex_post.12m |
| #290 | ⑧历史事后窗 | snapshot.series_store.UST_10Y(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 0.85 | 0.85 | 一致 | agent_judgment.history_periods[2022-06].ex_post.3m |
| #291 | ⑧历史事后窗 | snapshot.series_store.UST_10Y(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 0.9 | 0.9 | 一致 | agent_judgment.history_periods[2022-06].ex_post.6m |
| #292 | ⑧历史事后窗 | snapshot.series_store.UST_10Y(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 0.83 | 0.83 | 一致 | agent_judgment.history_periods[2022-06].ex_post.12m |
| #293 | ⑧历史事后窗 | snapshot.series_store.DFEDTARU(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 0.0 | 0.0 | 一致 | agent_judgment.history_periods[2023-10].ex_post.3m |
| #294 | ⑧历史事后窗 | snapshot.series_store.DFEDTARU(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 0.0 | 0.0 | 一致 | agent_judgment.history_periods[2023-10].ex_post.6m |
| #295 | ⑧历史事后窗 | snapshot.series_store.DFEDTARU(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | -0.5 | -0.5 | 一致 | agent_judgment.history_periods[2023-10].ex_post.12m |
| #296 | ⑧历史事后窗 | snapshot.series_store.UNEMPLOYMENT(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -0.2 | -0.2 | 一致 | agent_judgment.history_periods[2023-10].ex_post.3m |
| #297 | ⑧历史事后窗 | snapshot.series_store.UNEMPLOYMENT(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 0.0 | 0.0 | 一致 | agent_judgment.history_periods[2023-10].ex_post.6m |
| #298 | ⑧历史事后窗 | snapshot.series_store.UNEMPLOYMENT(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 0.2 | 0.2 | 一致 | agent_judgment.history_periods[2023-10].ex_post.12m |
| #299 | ⑧历史事后窗 | snapshot.series_store.CPI(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 0.6506 | 0.65 | 一致 | agent_judgment.history_periods[2023-10].ex_post.3m |
| #300 | ⑧历史事后窗 | snapshot.series_store.CPI(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 1.7313 | 1.73 | 一致 | agent_judgment.history_periods[2023-10].ex_post.6m |
| #301 | ⑧历史事后窗 | snapshot.series_store.CPI(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 2.5788 | 2.58 | 一致 | agent_judgment.history_periods[2023-10].ex_post.12m |
| #302 | ⑧历史事后窗 | snapshot.series_store.INDPRO(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -1.2408 | -1.24 | 一致 | agent_judgment.history_periods[2023-10].ex_post.3m |
| #303 | ⑧历史事后窗 | snapshot.series_store.INDPRO(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | -0.2244 | -0.22 | 一致 | agent_judgment.history_periods[2023-10].ex_post.6m |
| #304 | ⑧历史事后窗 | snapshot.series_store.INDPRO(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | -0.9947 | -0.99 | 一致 | agent_judgment.history_periods[2023-10].ex_post.12m |
| #305 | ⑧历史事后窗 | snapshot.series_store.SPX(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 15.5432 | 15.54 | 一致 | agent_judgment.history_periods[2023-10].ex_post.3m |
| #306 | ⑧历史事后窗 | snapshot.series_store.SPX(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 20.0746 | 20.07 | 一致 | agent_judgment.history_periods[2023-10].ex_post.6m |
| #307 | ⑧历史事后窗 | snapshot.series_store.SPX(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 36.0449 | 36.04 | 一致 | agent_judgment.history_periods[2023-10].ex_post.12m |
| #308 | ⑧历史事后窗 | snapshot.series_store.NIKKEI225(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 17.5893 | 17.59 | 一致 | agent_judgment.history_periods[2023-10].ex_post.3m |
| #309 | ⑧历史事后窗 | snapshot.series_store.NIKKEI225(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 24.4559 | 24.46 | 一致 | agent_judgment.history_periods[2023-10].ex_post.6m |
| #310 | ⑧历史事后窗 | snapshot.series_store.NIKKEI225(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 26.6452 | 26.65 | 一致 | agent_judgment.history_periods[2023-10].ex_post.12m |
| #311 | ⑧历史事后窗 | snapshot.series_store.DAX(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 14.1349 | 14.13 | 一致 | agent_judgment.history_periods[2023-10].ex_post.3m |
| #312 | ⑧历史事后窗 | snapshot.series_store.DAX(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 21.0787 | 21.08 | 一致 | agent_judgment.history_periods[2023-10].ex_post.6m |
| #313 | ⑧历史事后窗 | snapshot.series_store.DAX(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 28.8123 | 28.81 | 一致 | agent_judgment.history_periods[2023-10].ex_post.12m |
| #314 | ⑧历史事后窗 | snapshot.series_store.SHCOMP(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -7.6264 | -7.63 | 一致 | agent_judgment.history_periods[2023-10].ex_post.3m |
| #315 | ⑧历史事后窗 | snapshot.series_store.SHCOMP(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 2.8506 | 2.85 | 一致 | agent_judgment.history_periods[2023-10].ex_post.6m |
| #316 | ⑧历史事后窗 | snapshot.series_store.SHCOMP(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 8.6477 | 8.65 | 一致 | agent_judgment.history_periods[2023-10].ex_post.12m |
| #317 | ⑧历史事后窗 | snapshot.series_store.GOLD_F(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | 2.7127 | 2.71 | 一致 | agent_judgment.history_periods[2023-10].ex_post.3m |
| #318 | ⑧历史事后窗 | snapshot.series_store.GOLD_F(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | 15.4741 | 15.47 | 一致 | agent_judgment.history_periods[2023-10].ex_post.6m |
| #319 | ⑧历史事后窗 | snapshot.series_store.GOLD_F(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | 37.8579 | 37.86 | 一致 | agent_judgment.history_periods[2023-10].ex_post.12m |
| #320 | ⑧历史事后窗 | snapshot.series_store.DXY(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -3.1783 | -3.18 | 一致 | agent_judgment.history_periods[2023-10].ex_post.3m |
| #321 | ⑧历史事后窗 | snapshot.series_store.DXY(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | -0.4125 | -0.41 | 一致 | agent_judgment.history_periods[2023-10].ex_post.6m |
| #322 | ⑧历史事后窗 | snapshot.series_store.DXY(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | -2.5127 | -2.51 | 一致 | agent_judgment.history_periods[2023-10].ex_post.12m |
| #323 | ⑧历史事后窗 | snapshot.series_store.UST_10Y(月末口径: 候选月末最后观测→候选月+3月末最后观测; pp) | -0.89 | -0.89 | 一致 | agent_judgment.history_periods[2023-10].ex_post.3m |
| #324 | ⑧历史事后窗 | snapshot.series_store.UST_10Y(月末口径: 候选月末最后观测→候选月+6月末最后观测; pp) | -0.19 | -0.19 | 一致 | agent_judgment.history_periods[2023-10].ex_post.6m |
| #325 | ⑧历史事后窗 | snapshot.series_store.UST_10Y(月末口径: 候选月末最后观测→候选月+12月末最后观测; pp) | -0.6 | -0.6 | 一致 | agent_judgment.history_periods[2023-10].ex_post.12m |
| #874 | ⑧历史事后窗 | 事后窗注记「两口径数值可差约1个百分点」: \|月末口径−引擎事后块口径\| 逐格(受审稿逐窗叙述的三段×3窗×资产/美债序列) | {"n_cells": 36, "max_pp": 1.4144, "max_cell": ["2023-10", "SPX", "12m"], "n_cells_gt_1.05": 6, "n_cells_gt_0.5": 9, "median": 0.3514} | 可差约1个百分点 | 一致 | history_periods[*].ex_post.{3m,6m,12m} 句末括注 / MAP_REPORT 历史段 "随后N个月" 行 |
| #875 | ⑧历史事后窗 | 同注记对 TOP-5 第4/5名(2021-02/2020-01, 受审稿无逐窗月末叙述)的口径差: \|月末口径−引擎事后块口径\| | {"n_cells": 24, "max_pp": 2.7576, "max_cell": ["2021-02", "SPX", "6m"], "median": 0.3845} | 受审稿未引用该两段的月末口径数值 | NA(登记) | report.json steps[S6_analog].top[3..4].aftermath |
| #908 | ⑧历史事后窗 | series_store.SPX 月末口径 2022-06→2022-09 (%) | [-5.28, "2022-06-30", "2022-09-30"] | [-5.28, "月末口径"] | 一致 | agent_judgment.l4.scenarios[SCN1].rows.asset_direction.direction |
| #909 | ⑧历史事后窗 | series_store.GOLD_F 月末口径 2022-06→2022-09 (%) | [-7.49, "2022-06-30", "2022-09-30"] | [-7.49, "月末口径"] | 一致 | agent_judgment.l4.scenarios[SCN1].rows.asset_direction.direction |
| #910 | ⑧历史事后窗 | series_store.DXY 月末口径 2022-06→2022-09 (%) | [7.1, "2022-06-30", "2022-09-30"] | [7.1, "月末口径"] | 一致 | agent_judgment.l4.scenarios[SCN1].rows.asset_direction.direction |
| #911 | ⑧历史事后窗 | series_store.SPX 月末口径 2022-06→2023-06 (%) | [17.57, "2022-06-30", "2023-06-30"] | [17.57, "月末口径"] | 一致 | agent_judgment.l4.scenarios[SCN1].rows.asset_direction.direction |
| #912 | ⑧历史事后窗 | series_store.GOLD_F 月末口径 2025-03→2026-03 (%) | [48.83, "2025-03-31", "2026-03-31"] | [48.83, "月末口径"] | 一致 | agent_judgment.l4.scenarios[SCN2].rows.asset_direction.direction |
| #913 | ⑧历史事后窗 | series_store.DXY 月末口径 2025-03→2026-03 (%) | [-4.08, "2025-03-31", "2026-03-31"] | [-4.08, "月末口径"] | 一致 | agent_judgment.l4.scenarios[SCN2].rows.asset_direction.direction |
| #914 | ⑧历史事后窗 | series_store.SPX 月末口径 2025-03→2026-03 (%) | [16.33, "2025-03-31", "2026-03-31"] | [16.33, "月末口径"] | 一致 | agent_judgment.l4.scenarios[SCN2].rows.asset_direction.direction |
| #915 | ⑧历史事后窗 | report.json steps[S6_analog].envelope.data.top[0](2025-03).dims.*.contribution_share (%) | {"growth": 0.0, "inflation": 10.5, "rates": 40.7, "credit": 0.0, "volatility": 42.1, "valuation": 6.7} | [42.1, 40.7] | 一致 | agent_judgment.l4.scenarios[SCN2].rows.asset_direction.direction |
| #916 | ⑧历史事后窗 | 2025-03 段十二个月事后窗(至 2026-03-31) 与本轮研究窗(2025-11-23 起)的重叠日数 | 129 | 事后窗与本轮早段重叠 | 一致 | agent_judgment.l4.scenarios[SCN2].rows.asset_direction.direction |

### 2.4 ⑦传导环数字(记录 31 / 一致 31 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #326 | ⑦传导环数字 | snapshot.series_store.SPX(2025-11-19→2026-11-19) | 8.03 | 8.03 | 一致 | TR1.step3 观察事实(12个月窗对照) |
| #327 | ⑦传导环数字 | snapshot.series_store.NIKKEI225(2025-11-19→2026-11-19) | 22.47 | 22.47 | 一致 | TR1.step3 观察事实(12个月窗对照) |
| #328 | ⑦传导环数字 | snapshot.series_store.DAX(2025-11-19→2026-11-19) | 9.93 | 9.93 | 一致 | TR1.step3 观察事实(12个月窗对照) |
| #329 | ⑦传导环数字 | snapshot.series_store.SPX(2026-10-20→2026-11-19) | -6.96 | -6.96 | 一致 | TR1.step3 观察事实(窗口对照) |
| #330 | ⑦传导环数字 | snapshot.series_store.SPX(2026-08-19→2026-11-19) | -6.9 | -6.9 | 一致 | TR1.step3 观察事实(窗口对照) |
| #331 | ⑦传导环数字 | snapshot.series_store.USDCNY(2025-11-19→2026-11-19) | {"from": ["2025-11-19", 7.1075], "to": ["2026-11-19", 6.6676], "chg_pct": -6.19} | {"from": 7.1075, "to": 6.6676, "chg_pct": -6.19} | 一致 | L3 C3 解释C 汇率腿 |
| #345 | ⑦传导环数字 | snapshot.series_store.SPX×USDJPY 逐日(2026-10-26..2026-11-23) | {"n_days": 21, "corr": 0.19, "same_dir": 16, "spx_down_days": 12, "down&uj_down": 9, "down&uj_up": 3, "spx_up_days": 9, "up&uj_up": 7, "uj_comp_on_down": 0.16, "uj_comp_on_up": 1.66, "top4_drops": [["2026-11-05", -4.36, -0.07], ["2026-11-20… | {"n_days": 21, "corr": 0.19, "same_dir": 16, "spx_down_days": 12, "down&uj_down": 9, "down&uj_up": 3, "spx_up_days": 9, "up&uj_up": 7, "uj_comp_on_down": 0.16, "uj_comp_on_up": 1.66, "top4_drops": [["2026-11-05", -0.07], ["2026-11-20", 0.2]… | 一致 | TR2.step1 观察事实/对质注记(逐日面) |
| #346 | ⑦传导环数字 | snapshot.series_store.USDJPY(2026-10-23→2026-11-23) | {"from": ["2026-10-23", 156.494003], "to": ["2026-11-23", 159.347], "chg": 1.82} | {"from": 156.49, "to": 159.35, "chg": 1.82} | 一致 | TR2.step1 观察事实 |
| #498 | ⑦传导环数字 | 日历日 2026-10-23→2026-11-20 | 28 | 28 | 一致 | TR1.step2 "28 个日历日" |
| #499 | ⑦传导环数字 | HY_OAS 最新读数在库内百分位(<=口径, n=786) | 92 | 92 | 一致 | M1.step4 "处引擎三年历史约第 92 百分位" |
| #500 | ⑦传导环数字 | HY_OAS 库内上一次不低于最新读数的观测 | ["2025-05-09", 3.53] | ["2025-05-09", 3.53] | 一致 | M1.step4 "预警级=升破 2025-05-09 的 3.53(库内上一次不低于最新读数)" / TR1.step3 "为 2025-05-09 以来最高" |
| #501 | ⑦传导环数字 | HY_OAS 序列高点距最新读数 (bp) | 109 | 109 | 一致 | M1.step4 "距最新读数 109 个基点" |
| #502 | ⑦传导环数字 | HY_OAS 近1周 ISO周口径(基准 2026-11-13) pp | 0.29 | 0.29 | 一致 | TR1.step3 |
| #503 | ⑦传导环数字 | HY_OAS 严格7日口径(2026-11-12→11-19) pp | 0.32 | 0.32 | 一致 | TR1.step3 |
| #504 | ⑦传导环数字 | HY_OAS 近12个月(2025-11-19→2026-11-19) pp | 0.35 | 0.35 | 一致 | TR1.step3 |
| #505 | ⑦传导环数字 | HY_OAS 2026-11-13 为星期五(ISO周基准) | 5 | 5 | 一致 | TR1.step3 "ISO 周口径，基准 2026-11-13" |
| #506 | ⑦传导环数字 | HY_OAS 2026-11-19 距 2026-11-12 为 7 日 | 7 | 7 | 一致 | TR1.step3 "严格 7 日口径" |
| #507 | ⑦传导环数字 | BRENT_F 月末 2026-02→2026-05 % | 27.0 | 27.0 | 一致 | TR1.step1 "首尾 +27.00%" |
| #516 | ⑦传导环数字 | series_store.BEI_10Y@2026-02-27 → @2026-05-04 | [2.25, 2.5] | [2.25, 2.5] | 一致 | TR1.step2 "收紧前(2026-02-27→2026-05-04)自 2.25 升至 2.50" |
| #517 | ⑦传导环数字 | series_store.BEI_10Y@2026-06-10 / @2026-10-23 | [2.34, 2.34] | [2.34, 2.34] | 一致 | TR1.step2 "首次加息决议前日 2026-06-10 已回落至 2.34 / 2026-10-23 2.34" |
| #518 | ⑦传导环数字 | series_store.BEI_10Y 2026-06-17..2026-11-20 区间 | [2.15, 2.4] | [2.15, 2.4] | 一致 | TR1.step2 "收紧后(2026-06-17 起)区间 2.15–2.40" |
| #519 | ⑦传导环数字 | series_store.VIX@2026-10-23 → @2026-11-23 | [19.450001, 27.01] | [19.45, 27.01] | 一致 | M1.step4 / TR1.step3 "VIX 19.45→27.01" |
| #520 | ⑦传导环数字 | series_store.DFF 三时点锚值 @2025-11-22/@2026-08-22/@2026-11-19 | [3.88, 3.63, 3.88] | [3.88, 3.63, 3.88] | 一致 | TR1.step2 "(DFF 3.88→3.63→3.88)" |
| #522 | ⑦传导环数字 | series_store.HY_OAS 最新观测 | ["2026-11-19", 3.52] | ["2026-11-19", 3.52] | 一致 | M1.step4 / TR1.step3 "3.52pp@2026-11-19" |
| #523 | ⑦传导环数字 | series_store.HY_OAS 序列高点 | ["2025-04-07", 4.61] | ["2025-04-07", 4.61] | 一致 | M1.step4 "2025-04-07 序列高点 4.61" |
| #524 | ⑦传导环数字 | series_store.HY_OAS 序列起点 | 2023-11-21 | 2023-11-21 | 一致 | TR1.step3 "引擎序列(自 2023-11-21 起)" / M1.step4 "三年历史" |
| #525 | ⑦传导环数字 | series_store.BRENT_F 月末 2026-02 / 2026-03 / 2026-05 / 2026-06 | [72.480003, 118.349998, 92.050003, 72.919998] | [72.48, 118.35, 92.05, 72.92] | 一致 | TR1.step1 "月末 2026-02 72.48→2026-03 118.35→2026-05 92.05 / 至 2026-06 月末 72.92" |
| #526 | ⑦传导环数字 | BRENT_F 月末口径: 各月末最后观测距自然月末天数(≤4 天=周末/节假日缺口) | 2 | 4 | 一致 | TR1.step1 "月末" 口径(观测日 [('2026-02', '2026-02-27', 1), ('2026-03', '2026-03-31', 0), ('2026-05', '2026-05-29', 2), ('2026-06', '2026-06-30', 0)]) |
| #527 | ⑦传导环数字 | series_store.BRENT_F@2026-11-23 / @2026-10-23 | [88.190002, 116.720001] | [88.19, 116.72] | 一致 | TR1.step1 "BRENT_F 水平88.19@2026-11-23 / 近30日 116.72→88.19" |
| #528 | ⑦传导环数字 | BRENT_F 当月至今(2026-10月末→2026-11-23) % | -25.03 | -25.03 | 一致 | TR1.step1 "当月至今-25.03%" |
| #546 | ⑦传导环数字 | CORE_CPI 同比 2026-02 / 2026-05 | [2.4724624767640258, 2.8229420636110225] | [2.47, 2.82] | 一致 | TR1.step1 "核心CPI同比同窗 2.47→2.82" |

### 2.5 ⑤资产窗(记录 14 / 一致 14 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #332 | ⑤资产窗 | snapshot.series_store.SPX(2026-10-23→2026-11-20 同日收盘口径) | -9.36 | -9.36 | 一致 | TR1.step3 观察事实 / quality_gate_notes(同日收盘口径对照) |
| #333 | ⑤资产窗 | snapshot.series_store.DAX(2026-10-23→2026-11-20 同日收盘口径) | -1.5 | -1.5 | 一致 | TR1.step3 观察事实 / quality_gate_notes(同日收盘口径对照) |
| #334 | ⑤资产窗 | snapshot.series_store.CAC40(2026-10-23→2026-11-20 同日收盘口径) | 1.86 | 1.86 | 一致 | TR1.step3 观察事实 / quality_gate_notes(同日收盘口径对照) |
| #335 | ⑤资产窗 | snapshot.series_store.NIKKEI225(2026-10-23→2026-11-20 同日收盘口径) | -9.98 | -9.98 | 一致 | TR1.step3 观察事实 / quality_gate_notes(同日收盘口径对照) |
| #336 | ⑤资产窗 | snapshot.series_store.VIX(2026-10-23→2026-11-20 同日收盘口径) | 84.52 | 84.52 | 一致 | TR1.step3 观察事实 / quality_gate_notes(同日收盘口径对照) |
| #337 | ⑤资产窗 | snapshot.series_store.SPX(2026-10-23→2026-11-23) | -5.51 | -5.51 | 一致 | agent_judgment.asset_returns_echo / TR1.step3 观察事实 |
| #338 | ⑤资产窗 | snapshot.series_store.SHCOMP(2026-10-23→2026-11-23) | -4.11 | -4.11 | 一致 | agent_judgment.asset_returns_echo / TR1.step3 观察事实 |
| #339 | ⑤资产窗 | snapshot.series_store.DAX(2026-10-23→2026-11-23) | 0.11 | 0.11 | 一致 | agent_judgment.asset_returns_echo / TR1.step3 观察事实 |
| #340 | ⑤资产窗 | snapshot.series_store.NIKKEI225(2026-10-23→2026-11-20) | -9.98 | -9.98 | 一致 | agent_judgment.asset_returns_echo / TR1.step3 观察事实 |
| #341 | ⑤资产窗 | snapshot.series_store.VIX(2026-10-23→2026-11-23) | 38.87 | 38.87 | 一致 | agent_judgment.asset_returns_echo / TR1.step3 观察事实 |
| #342 | ⑤资产窗 | snapshot.series_store.DXY(2026-10-23→2026-11-23) | 2.23 | 2.23 | 一致 | agent_judgment.asset_returns_echo / TR1.step3 观察事实 |
| #343 | ⑤资产窗 | snapshot.series_store.GOLD_F(2026-10-23→2026-11-23) | -8.05 | -8.05 | 一致 | agent_judgment.asset_returns_echo / TR1.step3 观察事实 |
| #344 | ⑤资产窗 | snapshot.series_store.UST_10Y(2026-10-23→2026-11-19) % | 0.8 | 0.8 | 一致 | agent_judgment.asset_returns_echo[UST_10Y] |
| #899 | ⑤资产窗 | series_store SPX/NIKKEI225/GOLD_F/DXY/VIX 2026-10-23→截止日前最近观测 | {"SPX": [["2026-10-23", 7623.680176], ["2026-11-23", 7203.850098], -5.51], "NIKKEI225": [["2026-10-23", 62693.16], ["2026-11-20", 56436.65], -9.98], "GOLD_F": [["2026-10-23", 4007.899902], ["2026-11-23", 3685.199951], -8.05], "DXY": [["2026… | SPX 与 NIKKEI225 与 GOLD_F 近月收缩而 DXY 与 VIX 走高 | 一致 | agent_judgment.l3.contradictions[0].statement |

### 2.6 ①③同比路径(月频)(记录 83 / 一致 82 / NA 1)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #347 | ①③同比路径(月频) | snapshot.series_store.CPI 水平严格同月去年比 2025-09 | 3.0226 | 3.02 | 一致 | US from_to / M1.step1-2 / turnings[0] |
| #348 | ①③同比路径(月频) | snapshot.series_store.CPI 水平严格同月去年比 2026-02 | 2.434 | 2.434 | 一致 | US from_to / M1.step1-2 / turnings[0] |
| #349 | ①③同比路径(月频) | snapshot.series_store.CPI 水平严格同月去年比 2026-04 | 3.7792 | 3.78 | 一致 | US from_to / M1.step1-2 / turnings[0] |
| #350 | ①③同比路径(月频) | snapshot.series_store.CPI 水平严格同月去年比 2026-05 | 4.1666 | 4.1666 | 一致 | US from_to / M1.step1-2 / turnings[0] |
| #351 | ①③同比路径(月频) | snapshot.series_store.CPI 水平严格同月去年比 2026-07 | 3.3039 | 3.3 | 一致 | US from_to / M1.step1-2 / turnings[0] |
| #352 | ①③同比路径(月频) | snapshot.series_store.CPI 水平严格同月去年比 2026-08 | 3.353 | 3.35 | 一致 | US from_to / M1.step1-2 / turnings[0] |
| #353 | ①③同比路径(月频) | snapshot.series_store.CPI 水平严格同月去年比 2026-09 | 3.7173 | 3.72 | 一致 | US from_to / M1.step1-2 / turnings[0] |
| #356 | ①③同比路径(月频) | CPI 同比 2026-09 vs 一年前(2025-09): 3.72 > 3.02 | {"2025-09": 3.02, "2026-09": 3.72} | 较一年前走高 | 一致 | C1 "CPI…同比较一年前走高" |
| #357 | ①③同比路径(月频) | CPI 2026-10 同比基期 2025-10 观测 | {"2025-10_obs": null, "2025-11_obs": 325.063, "2025-12_obs": 326.031} | {"2025-10_obs": null, "2025-11_obs": "在场", "2025-12_obs": "在场"} | 一致 | from_to "最新2026-10缺2025-10基期" / SCN1 "2026-11 起同比不受此缺基期影响" |
| #358 | ①③同比路径(月频) | CPI 同比 2026-02→2026-03 增量(受审稿无数字, 仅直算登记) | 0.85 | 同月大幅跳升(无数字) | NA(登记) | turnings[0] "2026-03 同月大幅跳升" |
| #359 | ①③同比路径(月频) | snapshot.series_store.CORE_CPI 同比 2026-02 | 2.47 | 2.47 | 一致 | TR1.step1 |
| #360 | ①③同比路径(月频) | snapshot.series_store.CORE_CPI 同比 2026-05 | 2.82 | 2.82 | 一致 | TR1.step1 |
| #363 | ①③同比路径(月频) | snapshot.series_store.CORE_PCE 同比 2025-08 | 2.85 | 2.85 | 一致 | US from_to / M1.step1 |
| #364 | ①③同比路径(月频) | snapshot.series_store.CORE_PCE 同比 2026-05 | 3.16 | 3.16 | 一致 | US from_to / M1.step1 |
| #365 | ①③同比路径(月频) | snapshot.series_store.CORE_PCE 同比 2026-06 | 3.04 | 3.04 | 一致 | US from_to / M1.step1 |
| #366 | ①③同比路径(月频) | snapshot.series_store.CORE_PCE 同比 2026-07 | 3.0 | 3.0 | 一致 | US from_to / M1.step1 |
| #367 | ①③同比路径(月频) | snapshot.series_store.CORE_PCE 同比 2026-09 | 3.12 | 3.12 | 一致 | US from_to / M1.step1 |
| #368 | ①③同比路径(月频) | CORE_PCE 同比 2026-05 为高点且其后未再越过 | {"max_2026-05..10": 3.161709771256893, "max_after_2026-05": ["2026-09", 3.12]} | {"max_2026-05..10": 3.16, "not_exceeded": true} | 一致 | "2026-05 见顶后回落、未再越过高点" |
| #369 | ①③同比路径(月频) | snapshot.series_store.INDPRO 同比 2025-08 | 1.1887 | 1.19 | 一致 | US from_to / turnings[1] |
| #370 | ①③同比路径(月频) | snapshot.series_store.INDPRO 同比 2025-11 | 1.7543 | 1.7543 | 一致 | US from_to / turnings[1] |
| #371 | ①③同比路径(月频) | snapshot.series_store.INDPRO 同比 2026-02 | 0.7972 | 0.7972 | 一致 | US from_to / turnings[1] |
| #372 | ①③同比路径(月频) | snapshot.series_store.INDPRO 同比 2026-03 | 0.6861 | 0.69 | 一致 | US from_to / turnings[1] |
| #373 | ①③同比路径(月频) | snapshot.series_store.INDPRO 同比 2026-07 | 1.2498 | 1.25 | 一致 | US from_to / turnings[1] |
| #374 | ①③同比路径(月频) | snapshot.series_store.INDPRO 同比 2026-10 | 2.1497 | 2.15 | 一致 | US from_to / turnings[1] |
| #376 | ①③同比路径(月频) | snapshot.series_store.UNEMPLOYMENT 2025-09 | 4.4 | 4.4 | 一致 | US from_to |
| #377 | ①③同比路径(月频) | snapshot.series_store.UNEMPLOYMENT 2026-07 | 4.1 | 4.1 | 一致 | US from_to |
| #378 | ①③同比路径(月频) | snapshot.series_store.UNEMPLOYMENT 2026-10 | 4.1 | 4.1 | 一致 | US from_to |
| #379 | ①③同比路径(月频) | snapshot.series_store.EA_HICP_YOY 2025-10 | 2.1 | 2.1 | 一致 | EA from_to / M1.step1-2 / turnings[0] |
| #380 | ①③同比路径(月频) | snapshot.series_store.EA_HICP_YOY 2026-01 | 1.7 | 1.7 | 一致 | EA from_to / M1.step1-2 / turnings[0] |
| #381 | ①③同比路径(月频) | snapshot.series_store.EA_HICP_YOY 2026-02 | 1.9 | 1.9 | 一致 | EA from_to / M1.step1-2 / turnings[0] |
| #382 | ①③同比路径(月频) | snapshot.series_store.EA_HICP_YOY 2026-04 | 3.0 | 3.0 | 一致 | EA from_to / M1.step1-2 / turnings[0] |
| #383 | ①③同比路径(月频) | snapshot.series_store.EA_HICP_YOY 2026-05 | 3.2 | 3.2 | 一致 | EA from_to / M1.step1-2 / turnings[0] |
| #384 | ①③同比路径(月频) | snapshot.series_store.EA_HICP_YOY 2026-06 | 2.8 | 2.8 | 一致 | EA from_to / M1.step1-2 / turnings[0] |
| #385 | ①③同比路径(月频) | snapshot.series_store.EA_HICP_YOY 2026-07 | 2.9 | 2.9 | 一致 | EA from_to / M1.step1-2 / turnings[0] |
| #386 | ①③同比路径(月频) | snapshot.series_store.EA_HICP_YOY 2026-08 | 3.2 | 3.2 | 一致 | EA from_to / M1.step1-2 / turnings[0] |
| #387 | ①③同比路径(月频) | snapshot.series_store.EA_HICP_YOY 2026-10 | 4.0 | 4.0 | 一致 | EA from_to / M1.step1-2 / turnings[0] |
| #389 | ①③同比路径(月频) | HICP 月度增量 2026-07 | 0.1 | 0.1 | 一致 | EA from_to "7月的 +0.1" |
| #390 | ①③同比路径(月频) | HICP 月度增量 2026-08/09/10 | [0.3, 0.6, 0.2] | [0.3, 0.6, 0.2] | 一致 | EA from_to "2026-08至10月度增量 +0.3/+0.6/+0.2" |
| #391 | ①③同比路径(月频) | HICP 2026-01→2026-05 连续上行 | true | 连续上行 | 一致 | EA from_to "自2026-01低点1.7连续上行至2026-05的3.2" |
| #392 | ①③同比路径(月频) | HICP 月度增量 2025-12→2026-01 … 2026-04→2026-05 | [-0.3, 0.2, 0.7, 0.4, 0.2] | [-0.3, 0.2, 0.7, 0.4, 0.2] | 一致 | EA from_to "2026-03起加速"(2026-02→03 跃升 0.7, 其前增量 -0.3/+0.2) |
| #393 | ①③同比路径(月频) | HICP 2026-10=4.0 为近 36 个月(2023-11..2026-10)最高; 此前最后一次 >=4.0 的月份 | {"max_36m": 4.0, "argmax_36m": "2026-10", "last_ge_4.0_before": "2023-09", "window_max": 4.0} | {"max_36m": 4.0, "argmax_36m": "2026-10", "window_max": 4.0} | 一致 | C1 "EA_HICP_YOY 升至本轮最高" |
| #394 | ①③同比路径(月频) | snapshot.series_store.CN_PPI_YOY 2025-10 | -2.1 | -2.1 | 一致 | CN from_to / M1.step1 / turnings[0] |
| #395 | ①③同比路径(月频) | snapshot.series_store.CN_PPI_YOY 2026-02 | -0.9 | -0.9 | 一致 | CN from_to / M1.step1 / turnings[0] |
| #396 | ①③同比路径(月频) | snapshot.series_store.CN_PPI_YOY 2026-05 | 3.9 | 3.9 | 一致 | CN from_to / M1.step1 / turnings[0] |
| #397 | ①③同比路径(月频) | snapshot.series_store.CN_PPI_YOY 2026-06 | 4.1 | 4.1 | 一致 | CN from_to / M1.step1 / turnings[0] |
| #398 | ①③同比路径(月频) | snapshot.series_store.CN_PPI_YOY 2026-07 | 3.5 | 3.5 | 一致 | CN from_to / M1.step1 / turnings[0] |
| #399 | ①③同比路径(月频) | snapshot.series_store.CN_PPI_YOY 2026-10 | 5.7 | 5.7 | 一致 | CN from_to / M1.step1 / turnings[0] |
| #402 | ①③同比路径(月频) | CN_PPI_YOY 2026-10=5.7 为本轮新高(上一次 >=5.7 的月份; 2023 年以来最低) | {"last_ge_5.7_before": "2022-06", "trough_since_2023": ["2023-06", -5.4], "window_max": 5.7} | {"last_ge_5.7_before": "<2023-01", "trough_since_2023": "深负值", "window_max": 5.7} | 一致 | C1 "CN_PPI_YOY 自负转正并续创本轮新高" / C3 "自深负值区间升至本轮高点" |
| #403 | ①③同比路径(月频) | snapshot.series_store.CN_CPI_YOY 2025-10 | 0.2 | 0.2 | 一致 | CN from_to |
| #404 | ①③同比路径(月频) | snapshot.series_store.CN_CPI_YOY 2026-07 | 0.5 | 0.5 | 一致 | CN from_to |
| #405 | ①③同比路径(月频) | snapshot.series_store.CN_CPI_YOY 2026-10 | 0.7 | 0.7 | 一致 | CN from_to |
| #406 | ①③同比路径(月频) | CN_CPI_YOY 2026-02..05 同窗区间 | [1.0, 1.3] | [1.0, 1.3] | 一致 | "中国CPI同比同窗持平于一点零至一点三" |
| #407 | ①③同比路径(月频) | 四地 12 个月窗价格摆动(最高-最低) | {"US_CPI": 1.78, "EA_HICP": 2.3, "CN_PPI": 7.9, "CN_PPI_since_trough": 11.1, "JP_CPI": 1.63} | {"largest": "CN_PPI"} | 一致 | C3 "四大经济体最大价格摆动" / CN from_to "为四地最大价格摆动" |
| #408 | ①③同比路径(月频) | snapshot.series_store.CN_PMI_MFG 2025-10 | 49.0 | 49.0 | 一致 | CN from_to |
| #409 | ①③同比路径(月频) | snapshot.series_store.CN_PMI_MFG 2026-07 | 49.2 | 49.2 | 一致 | CN from_to |
| #410 | ①③同比路径(月频) | snapshot.series_store.CN_PMI_MFG 2026-10 | 49.3 | 49.3 | 一致 | CN from_to |
| #411 | ①③同比路径(月频) | CN_PMI_MFG 指数水平同比 2025-10 | -2.2 | -2.2 | 一致 | CN from_to "同比口径…-2.2→-0.2→0.6%" |
| #412 | ①③同比路径(月频) | CN_PMI_MFG 指数水平同比 2026-07 | -0.2 | -0.2 | 一致 | CN from_to "同比口径…-2.2→-0.2→0.6%" |
| #413 | ①③同比路径(月频) | CN_PMI_MFG 指数水平同比 2026-10 | 0.6 | 0.6 | 一致 | CN from_to "同比口径…-2.2→-0.2→0.6%" |
| #414 | ①③同比路径(月频) | CN_PMI_MFG 同月指数点差 | [-1.1, -0.1, 0.3] | [-1.1, -0.1, 0.3] | 一致 | CN from_to "相差约 -1.1、-0.1、+0.3 个指数点" |
| #415 | ①③同比路径(月频) | CN_PMI_MFG 2025-11..2026-10 站上荣枯线的月份 | ["2025-12", "2026-03", "2026-04", "2026-06", "2026-09"] | ["2025-12", "2026-03", "2026-04", "2026-06", "2026-09"] | 一致 | C1 "共五个月站上荣枯线" |
| #416 | ①③同比路径(月频) | CN_PMI_MFG 五个月读数 | [50.1, 50.4, 50.3, 50.3, 50.1] | [50.1, 50.4, 50.3, 50.3, 50.1] | 一致 | CN from_to "(50.1/50.4/50.3/50.3/50.1)" |
| #417 | ①③同比路径(月频) | CN_PMI_MFG 其余月份: 2026-05 持平于 50.0; 余在 49.0–49.8 | {"2026-05": 50.0, "others_min": 49.0, "others_max": 49.8} | {"2026-05": 50.0, "others_min": 49.0, "others_max": 49.8} | 一致 | C1 / CN from_to |
| #419 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_YOY 2025-01 | 4.03 | 4.03 | 一致 | JP from_to / turnings[2] / M1.step2 |
| #420 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_YOY 2025-11 | 2.9 | 2.9 | 一致 | JP from_to / turnings[2] / M1.step2 |
| #421 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_YOY 2025-12 | 2.13 | 2.13 | 一致 | JP from_to / turnings[2] / M1.step2 |
| #422 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_YOY 2026-01 | 1.51 | 1.51 | 一致 | JP from_to / turnings[2] / M1.step2 |
| #423 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_YOY 2026-02 | 1.27 | 1.27 | 一致 | JP from_to / turnings[2] / M1.step2 |
| #424 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_YOY 2026-03 | 1.46 | 1.46 | 一致 | JP from_to / turnings[2] / M1.step2 |
| #425 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_YOY 2026-04 | 1.38 | 1.38 | 一致 | JP from_to / turnings[2] / M1.step2 |
| #426 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_YOY 2026-07 | 1.97 | 1.97 | 一致 | JP from_to / turnings[2] / M1.step2 |
| #427 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_YOY 2026-10 | 2.44 | 2.44 | 一致 | JP from_to / turnings[2] / M1.step2 |
| #428 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_YOY 2025-10 | 2.99 | 2.99 | 一致 | JP from_to / turnings[2] / M1.step2 |
| #429 | ①③同比路径(月频) | 日本CPI 2025-09、2025-10 小幅回升(月度增量) | {"2025-09": 0.19, "2025-10": 0.08} | {"2025-09": ">0", "2025-10": ">0"} | 一致 | turnings[2] |
| #433 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_TOKYO_YOY 2026-06 | 1.6 | 1.6 | 一致 | JP from_to / turning_supplement |
| #434 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_TOKYO_YOY 2026-07 | 1.85 | 1.85 | 一致 | JP from_to / turning_supplement |
| #435 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_TOKYO_YOY 2026-08 | 1.9 | 1.9 | 一致 | JP from_to / turning_supplement |
| #436 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_TOKYO_YOY 2026-09 | 2.69 | 2.69 | 一致 | JP from_to / turning_supplement |
| #437 | ①③同比路径(月频) | snapshot.series_store.JP_CPI_TOKYO_YOY 2026-10 | 2.73 | 2.73 | 一致 | JP from_to / turning_supplement |
| #898 | ①③同比路径(月频) | series_store UST_10Y/TIPS_10Y/BEI_10Y @2025-11-19→@2026-11-19 | {"UST_10Y": [4.13, 5.04], "TIPS_10Y": [1.86, 2.88], "BEI_10Y": [2.27, 2.16]} | UST_10Y 与 TIPS_10Y 上行而 BEI_10Y 回落 | 一致 | agent_judgment.l3.contradictions[0].statement |
| #900 | ①③同比路径(月频) | CPI/CORE_PCE 同比: 2026-09 vs 一年前(2025-09); 2026-05 值; 2026-05 之后各观测月最大值; 2026-10 同比 | {"CPI_2026-09": 3.72, "CPI_2025-09": 3.02, "CPI_2026-05": 4.1666, "CPI_after_max": 3.7173, "PCE_2026-09": 3.12, "PCE_2025-09": 2.82, "PCE_2026-05": 3.16, "PCE_after_max": 3.12, "CPI_2026-10": null} | 同比较一年前走高(2026-05 见顶后回落、未再越过高点) | 一致 | agent_judgment.l3.contradictions[0].statement / regions[US].from_to |
| #906 | ①③同比路径(月频) | CN_PPI_YOY 最新 − CN_CPI_YOY 最新 (pp) | 5.0 | PPI 与 CPI 剪刀差大 | 一致 | agent_judgment.l3.contradictions[2].competing_explanations[0] |
| #907 | ①③同比路径(月频) | CPI 同比 2026-05 直算值 → 保留两位 | [4.1666, 4.17] | [4.1666, 4.17] | 一致 | agent_judgment.l3.mechanism_chains[0].links[1].text / reader_map.transmission[0].links[1] |

### 2.7 ⑥转折路径(记录 12 / 一致 12 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #354 | ⑥转折路径 | CPI 同比 12 个月窗(2025-11..2026-10)低点月 | 2026-01 | 2026-01 | 一致 | turnings[0] "美国 CPI 同比…低点均在 2026-01" |
| #355 | ⑥转折路径 | CPI 同比 12 个月窗高点月 | 2026-05 | 2026-05 | 一致 | M1.step2 "2026-05 高点 4.17" |
| #375 | ⑥转折路径 | INDPRO 同比 12 个月窗低点月 | {"min_month": "2026-03", "value": 0.69} | {"min_month": "2026-03", "value": 0.69} | 一致 | turnings[1] "序列同比低点为 2026-03 的 0.69" |
| #388 | ⑥转折路径 | HICP 12 个月窗低点月 | 2026-01 | 2026-01 | 一致 | turnings[0] "欧元区 HICP 低点在 2026-01" |
| #400 | ⑥转折路径 | CN_PPI_YOY 12 个月窗低点月 | 2025-11 | 2025-11 | 一致 | turnings[0] "中国 PPI 低点在 2025-11" |
| #401 | ⑥转折路径 | CN_PPI_YOY 自 2025-11 低点至 2026-10 的回落月 | ["2026-07"] | ["2026-07"] | 一致 | turnings[0] "其间仅 2026-07 由 4.1 回落至 3.5" |
| #418 | ⑥转折路径 | CN_PMI_MFG 候选窗 2026-02→2026-05 同比(引擎候选面原值) | [-2.3904, 1.0101] | [-2.3904, 1.0101] | 一致 | turnings[1] |
| #430 | ⑥转折路径 | 日本CPI 2025-11→2026-02 逐月下行 | true | true | 一致 | turnings[2] "月末路径 2.9→2.13→1.51→1.27" |
| #431 | ⑥转折路径 | 日本CPI 12 个月窗低点 | 2026-02 | 2026-02 | 一致 | turnings[2] "2026-02 低点 1.27" |
| #432 | ⑥转折路径 | 日本CPI 2026-03..2026-10 中未逐月上行的月份间隔 | ["2026-03→2026-04"] | ["2026-03→2026-04"] | 一致 | turnings[2] "持续回升自 2026-05 起" / supplement "回升起点(2026-03)" |
| #929 | ⑥转折路径 | series_store JP_CPI_YOY 2025-01..2026-02: 高点月/值; 低点月/值; 其间逐月上行的月份 | {"high_ym": "2025-01", "high": 4.03, "low_ym": "2026-02", "low": 1.27, "mom_up_months": ["2025-09", "2025-10"]} | {"high_ym": "2025-01", "high": 4.03, "low_ym": "2026-02", "low": 1.27, "mom_up_months": ["2025-09", "2025-10"]} | 一致 | agent_judgment.reader_map.turnings[2].first_mover |
| #930 | ⑥转折路径 | CPI 同比/EA_HICP_YOY/CN_PPI_YOY: 2026-02..2026-05 逐月是否上行; 2026-03 月度增量; 该增量在序列全部历史月度增量绝对值中的百分位 | {"paths": {"CPI": {"2026-01": 2.3912, "2026-02": 2.434, "2026-03": 3.286, "2026-04": 3.7792, "2026-05": 4.1666}, "EA_HICP_YOY": {"2026-01": 1.7, "2026-02": 1.9, "2026-03": 2.6, "2026-04": 3.0, "2026-05": 3.2}, "CN_PPI_YOY": {"2026-01": -1.4… | 2026-02 起三序列同向上行、2026-03 同月大幅跳升 | 一致 | agent_judgment.reader_map.turnings[0].first_mover |

### 2.8 杂项(引用/日历/结构)(记录 33 / 一致 32 / NA 1)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #361 | 杂项(引用/日历/结构) | CORE_CPI 同比 2026-05→2026-08 四位小数端点差 | -0.3767 | -0.3767 | 一致 | quality_gate_notes ⑧(显示层舍入) |
| #362 | 杂项(引用/日历/结构) | CORE_CPI 同比 2026-05→2026-08 未舍入差 | -0.3768 | -0.3768 | 一致 | quality_gate_notes ⑧(未舍入差) |
| #468 | 杂项(引用/日历/结构) | 发布规则值的星期(6-13 星期六 / 9-13 星期日 / 8-30 星期日) | {"2026-06-13": 6, "2026-09-13": 7, "2026-08-30": 7} | {"2026-06-13": "星期六", "2026-09-13": "星期日", "2026-08-30": "星期日"} | 一致 | M1.step2 / turning_supplement |
| #469 | 杂项(引用/日历/结构) | 发布规则 CPI 观测 2026-04 | 2026-05-13 | 2026-05-13 | 一致 | M1.step2 / turning_supplement "推定发布" |
| #470 | 杂项(引用/日历/结构) | 发布规则 CPI 观测 2026-07 | 2026-08-13 | 2026-08-13 | 一致 | M1.step2 / turning_supplement "推定发布" |
| #471 | 杂项(引用/日历/结构) | 发布规则 CPI 观测 2026-08 | 2026-09-13 | 2026-09-13 | 一致 | M1.step2 / turning_supplement "推定发布" |
| #472 | 杂项(引用/日历/结构) | 发布规则 CPI 观测 2026-05 | 2026-06-13 | 2026-06-13 | 一致 | M1.step2 / turning_supplement "推定发布" |
| #473 | 杂项(引用/日历/结构) | 发布规则 CORE_PCE 观测 2026-07 | 2026-08-30 | 2026-08-30 | 一致 | M1.step2 / turning_supplement "推定发布" |
| #474 | 杂项(引用/日历/结构) | 发布规则 EA_HICP_YOY 观测 2026-04 | 2026-05-16 | 2026-05-16 | 一致 | M1.step2 / turning_supplement "推定发布" |
| #475 | 杂项(引用/日历/结构) | 发布规则 EA_HICP_YOY 观测 2026-07 | 2026-08-16 | 2026-08-16 | 一致 | M1.step2 / turning_supplement "推定发布" |
| #476 | 杂项(引用/日历/结构) | 发布规则 EA_HICP_YOY 观测 2026-08 | 2026-09-16 | 2026-09-16 | 一致 | M1.step2 / turning_supplement "推定发布" |
| #477 | 杂项(引用/日历/结构) | 发布规则 JP_CPI_YOY 观测 2026-07 | 2026-08-20 | 2026-08-20 | 一致 | M1.step2 / turning_supplement "推定发布" |
| #478 | 杂项(引用/日历/结构) | 发布规则 JP_CPI_TOKYO_YOY 观测 2026-09 | 2026-09-29 | 2026-09-29 | 一致 | M1.step2 / turning_supplement "推定发布" |
| #479 | 杂项(引用/日历/结构) | 发布规则 JP_CPI_TOKYO_YOY 观测 2026-08 | 2026-08-30 | 2026-08-30 | 一致 | M1.step2 / turning_supplement "推定发布" |
| #494 | 杂项(引用/日历/结构) | CN_NEW_LOANS 最新观测月 | 2026-10 | 2026-10 | 一致 | C3 |
| #521 | 杂项(引用/日历/结构) | series_store.DFF 变动点实际值 2025-12-10→2025-12-11→2026-09-17 | [3.89, 3.64, 3.88] | 受审稿括注 3.88→3.63→3.88 | NA(登记) | TR1.step2 口径注记(MINOR 候选) |
| #534 | 杂项(引用/日历/结构) | L3 证据引用条数 / 去重项数 | [41, 20] | [41, 20] | 一致 | quality_gate_notes "L3 证据引用共 41 条" |
| #535 | 杂项(引用/日历/结构) | L3+L4 证据引用条数 / 去重项数 | [50, 20] | [50, 20] | 一致 | quality_gate_notes "连同 L4 共 50 条、去重 20 项" |
| #536 | 杂项(引用/日历/结构) | L3+L4 引用全部在证据索引(72行)内 | [] | [] | 一致 | evidence_refs ↔ evidence_index.json |
| #537 | 杂项(引用/日历/结构) | L3+L4 引用全部在快照 facts 内 | [] | [] | 一致 | evidence_refs ↔ snapshot.facts(fact_id) |
| #538 | 杂项(引用/日历/结构) | 证据索引行数 | 72 | 72 | 一致 | agent_declaration / quality_gate_notes |
| #539 | 杂项(引用/日历/结构) | 引用 fact 值 = series_store 同日(或同观测月内最近)观测值 逐条 | [] | [] | 一致 | snapshot.facts[*].value 回贴 series_store |
| #540 | 杂项(引用/日历/结构) | 三条矛盾陈述并列解释数 | [3, 2, 3] | [3, 2, 3] | 一致 | quality_gate_notes "L3 三条矛盾陈述各并列 3、2、3 种解释" |
| #541 | 杂项(引用/日历/结构) | L3 机制链条数 / 链内环数(M1=4,M2=2) ; 传导面对质环数(TR1=3,TR2=1) | [2, 6, 4] | [2, 6, 4] | 一致 | quality_gate_notes "传导面 4 环" |
| #542 | 杂项(引用/日历/结构) | 传导面 4 环均给出主/竞争两侧预期+区分指标+裁定 | [true, ["BRENT_F", "BEI_10Y", "BEI_10Y", "USDJPY"]] | [true, ["BRENT_F", "BEI_10Y", "BEI_10Y", "USDJPY"]] | 一致 | quality_gate_notes "传导面 4 环均给出主/竞争两侧对同一区分指标的不同预期" |
| #543 | 杂项(引用/日历/结构) | 对质裁定序列 | ["支持主解释", "尚不能区分", "尚不能区分", "支持竞争解释"] | ["支持主解释", "尚不能区分", "尚不能区分", "支持竞争解释"] | 一致 | quality_gate_notes "第1环…支持主解释、第2环与第3环…尚不能区分、竞争链第4环…支持竞争解释" |
| #544 | 杂项(引用/日历/结构) | 被点名的区分指标(BRENT_F/BEI_10Y/USDJPY)在证据面在场 | ["BEI_10Y", "BRENT_F", "USDJPY"] | ["BEI_10Y", "BRENT_F", "USDJPY"] | 一致 | TR1.step1/2/3, TR2.step1 distinguishing_metric 可观测性 |
| #545 | 杂项(引用/日历/结构) | CORE_CPI 同比 2026-05→2026-08 四位小数端点差 / 未舍入差 | [-0.3767, -0.3768] | [-0.3767, -0.3768] | 一致 | quality_gate_notes ⑧ |
| #878 | 杂项(引用/日历/结构) | metric_registry.metrics[EA_HICP_YOY].release_semantics 含「次月中旬终值」/「保守标注」; 受审稿历史段(2023-10)含「月末快报口径,当日可见」 | ["Eurostat月度HICP(次月中旬终值);R20 注意: HICP流程对近月含回溯修订(2025-12 值1.9→2.0),按观测月+滞后窗口保守标注,revision_semantics=latest_vintage_asof_collected", true, true] | ["Eurostat月度HICP(次月中旬终值); …保守标注", true, true] | 一致 | root_overlay/config/metric_registry.json / history_periods[2023-10].other_regions_sync |
| #879 | 杂项(引用/日历/结构) | history_periods[2023-10].other_regions_sync "欧元区HICP同比2023-10为2.9(月末快报口径,当日可见…)" 两级规则: 快报日=2023-10-31 <= 截止 2023-10-31 | {"value_2023-10": 2.9, "flash_rule_date": "2023-10-31", "cutoff": "2023-10-31", "visible": true} | {"value_2023-10": 2.9, "flash_rule_date": "2023-10-31", "cutoff": "2023-10-31", "visible": true} | 一致 | agent_judgment.reader_map.history_periods[2023-10].other_regions_sync / MAP_REPORT 历史段 2023-10 当时可知面 |
| #884 | 杂项(引用/日历/结构) | 受审稿 M1.step2 含「2026-08 观测 3.2 按引擎规则推定发布于 2026-09-16、决议时点尚未可见」与「对美联储与欧央行的动机环证据减弱」 | [true, true] | [true, true] | 一致 | agent_judgment.l3.mechanism_chains[0].links[1].text |
| #931 | 杂项(引用/日历/结构) | CORE_CPI 同比 2026-05/2026-08 未舍入差 与 四位小数端点相减 | {"yoy_2026-05": 2.8229420636110225, "yoy_2026-08": 2.4461631786472537, "unrounded_diff": -0.3768, "rounded_endpoints_diff": -0.3767} | {"candidate_delta": -0.3767, "unrounded_diff": -0.3768} | 一致 | agent_judgment.quality_gate_notes[5]⑧ / report.json turning_candidates CORE_CPI |
| #932 | 杂项(引用/日历/结构) | evidence_index.json 中 CN_PPI_YOY/CN_CPI_YOY/CPI/EA_HICP_YOY/JP_POLICY_RATE 的引用标签日期 vs series_store 最新观测日 | {"CN_PPI_YOY": ["2026-10-31", "2026-10-01"], "CN_CPI_YOY": ["2026-10-31", "2026-10-01"], "CPI": ["2026-10-01", "2026-10-01"], "EA_HICP_YOY": ["2026-10-01", "2026-10-01"], "JP_POLICY_RATE": ["2026-10-01", "2026-10-01"]} | {"CN_PPI_YOY": ["2026-10-31", "2026-10-01"], "CN_CPI_YOY": ["2026-10-31", "2026-10-01"]} | 一致 | agent_judgment.quality_gate_notes[5]④ / C1/C3 evidence_refs |

### 2.9 ⑪诚实缺席(记录 5 / 一致 5 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #438 | ⑪诚实缺席 | JP_CPI_TOKYO_YOY 首个观测月(12个月前锚 2025-11-23 前无已发布观测) | ["2026-01-01", 1.6] | ["2026-01-01", 1.6] | 一致 | JP from_to |
| #454 | ⑪诚实缺席 | CN_POLICY_OVERNIGHT 在 12个月前/3个月前锚日前无观测 | [null, null] | [null, null] | 一致 | CN from_to "12个月前与3个月前锚日前无已发布观测" |
| #492 | ⑪诚实缺席 | series_store 不含 JGB 收益率历史序列 | [] | [] | 一致 | M2.step1 "JGB 收益率历史序列不在引擎(单点观测)" |
| #493 | ⑪诚实缺席 | series_store 不含中国利率预期/资本流动序列 | ["CN_CPI_YOY", "CN_LPR_1Y", "CN_NEW_LOANS", "CN_OMO_7D", "CN_PMI_MFG", "CN_POLICY_OVERNIGHT", "CN_PPI_YOY"] | no CN rate-expectation / capital-flow series | 一致 | C3 "引擎面无中国利率预期序列…无中国资本流动序列" |
| #495 | ⑪诚实缺席 | JP_POLICY_TARGET 不在序列库 | false | false | 一致 | JP from_to "计划指标 JP_POLICY_TARGET 不在注册表" |

### 2.10 ④政策面(记录 58 / 一致 56 / NA 2)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #439 | ④政策面 | snapshot.series_store.JP_POLICY_RATE 月均 2025-10 | 0.477 | 0.477 | 一致 | JP from_to / M2.step1 |
| #440 | ④政策面 | snapshot.series_store.JP_POLICY_RATE 月均 2025-11 | 0.478 | 0.478 | 一致 | JP from_to / M2.step1 |
| #441 | ④政策面 | snapshot.series_store.JP_POLICY_RATE 月均 2025-12 | 0.557 | 0.557 | 一致 | JP from_to / M2.step1 |
| #442 | ④政策面 | snapshot.series_store.JP_POLICY_RATE 月均 2026-07 | 0.978 | 0.978 | 一致 | JP from_to / M2.step1 |
| #443 | ④政策面 | snapshot.series_store.JP_POLICY_RATE 月均 2026-10 | 1.227 | 1.227 | 一致 | JP from_to / M2.step1 |
| #444 | ④政策面 | JP_POLICY_RATE 月度步进(bp) 2025-12..2026-10 | [7.9, 17.1, 0.0, 0.0, -0.1, 0.0, 11.4, 13.7, -0.1, 6.6, 18.4] | [7.9, 17.1, 0.0, 0.0, -0.1, 0.0, 11.4, 13.7, -0.1, 6.6, 18.4] | 一致 | M2.step1 "+8/+17/+11/+14/+7/+18; 2026-04 与 2026-08 各约0.1bp" |
| #445 | ④政策面 | JP_POLICY_RATE 步进(取整bp, 舍入步记0) | [8, 17, 0, 0, 0, 0, 11, 14, 0, 7, 18] | [8, 17, 0, 0, 0, 0, 11, 14, 0, 7, 18] | 一致 | M2.step1 |
| #446 | ④政策面 | JP_POLICY_RATE 窗内净变动 2025-11→2026-10 (bp, 取整) | 75 | 75 | 一致 | JP from_to "净 +75 个基点"(0.478→1.227=74.9bp) |
| #447 | ④政策面 | JP_POLICY_RATE 自 2025-12 起 (bp) | 67.0 | 67.0 | 一致 | JP from_to "自 2025-12 月均 0.557 起 +67bp" |
| #448 | ④政策面 | JP_POLICY_RATE 窗内(>2025-11-19)首个观测月 | 2025-12 | 2025-12 | 一致 | quality_gate_notes "自窗内首个观测起算的另一口径 +67bp" |
| #449 | ④政策面 | CN_OMO_7D 末观测/滞后天数/三锚值 | {"last": ["2026-10-30", 1.4], "lag_days": 24, "distinct": [1.4], "after_last": []} | {"last": ["2026-10-30", 1.4], "lag_days": 24, "distinct": [1.4], "after_last": []} | 一致 | CN from_to "末观测2026-10-30滞后24天" / C1 "其后缺观测" |
| #450 | ④政策面 | CN_OMO_7D 锚日前最近观测 12个月前 | ["2025-11-14", 1.4] | ["2025-11", 1.4] | 一致 | CN from_to "7天逆回购利率 1.4→1.4→1.4(观测 2025-11→2026-08→2026-10)" |
| #451 | ④政策面 | CN_OMO_7D 锚日前最近观测 3个月前 | ["2026-08-21", 1.4] | ["2026-08", 1.4] | 一致 | CN from_to "7天逆回购利率 1.4→1.4→1.4(观测 2025-11→2026-08→2026-10)" |
| #452 | ④政策面 | CN_OMO_7D 锚日前最近观测 最新 | ["2026-10-30", 1.4] | ["2026-10", 1.4] | 一致 | CN from_to "7天逆回购利率 1.4→1.4→1.4(观测 2025-11→2026-08→2026-10)" |
| #453 | ④政策面 | CN_POLICY_OVERNIGHT 首观测/末观测/取值 | {"first": ["2026-11-02", 1.25], "last": ["2026-11-23", 1.25], "distinct": [1.25], "n": 16} | {"first": ["2026-11-02", 1.25], "last": ["2026-11-23", 1.25], "distinct": [1.25]} | 一致 | CN from_to "隔夜逆回购利率…最新 1.25@2026-11-23(持平于首个观测值)" / quality_gate_notes ② |
| #455 | ④政策面 | CN_LPR_1Y 锚日前最近观测 2025-11-23 | ["2025-11-20", 3.0] | ["2025-11-20", 3.0] | 一致 | CN from_to "LPR_1Y 3.0→3.0→3.0(观测 2025-11→2026-08→2026-11)" |
| #456 | ④政策面 | CN_LPR_1Y 锚日前最近观测 2026-08-23 | ["2026-08-20", 3.0] | ["2026-08-20", 3.0] | 一致 | CN from_to "LPR_1Y 3.0→3.0→3.0(观测 2025-11→2026-08→2026-11)" |
| #457 | ④政策面 | CN_LPR_1Y 锚日前最近观测 2026-11-23 | ["2026-11-20", 3.0] | ["2026-11-20", 3.0] | 一致 | CN from_to "LPR_1Y 3.0→3.0→3.0(观测 2025-11→2026-08→2026-11)" |
| #458 | ④政策面 | CN_LPR_1Y 窗内取值集合(窗内持平) | [3.0] | [3.0] | 一致 | CN from_to "窗内持平" |
| #459 | ④政策面 | ECB_DFR 窗内(>=2025-11-19)变动点 | [["2026-06-17", 2.0, 2.25], ["2026-09-16", 2.25, 2.5]] | [["2026-06-17", 2.0, 2.25], ["2026-09-16", 2.25, 2.5]] | 一致 | M1.step2 / EA from_to |
| #460 | ④政策面 | ECB_MRO 窗内变动点 | [["2026-06-17", 2.15, 2.4], ["2026-09-16", 2.4, 2.65]] | [["2026-06-17", 2.15, 2.4], ["2026-09-16", 2.4, 2.65]] | 一致 | EA from_to "主要再融资利率 2.15→2.65" |
| #461 | ④政策面 | ECB_DFR 锚日前最近观测 2025-11-23 | 2.0 | 2.0 | 一致 | EA from_to "存款便利利率 2.0→2.25→2.5" |
| #462 | ④政策面 | ECB_DFR 锚日前最近观测 2026-08-23 | 2.25 | 2.25 | 一致 | EA from_to "存款便利利率 2.0→2.25→2.5" |
| #463 | ④政策面 | ECB_DFR 锚日前最近观测 2026-11-23 | 2.5 | 2.5 | 一致 | EA from_to "存款便利利率 2.0→2.25→2.5" |
| #464 | ④政策面 | ECB_DFR 窗启时在值(2025-11-19) | ["2025-06-11", 2.0] | ["2025-06-11", 2.0] | 一致 | EA from_to "窗启时在值 2.0，2025-06-11 起生效" |
| #465 | ④政策面 | ECB_DFR 自窗内首个观测起算净变动(bp) | 25.0 | 25.0 | 一致 | EA from_to "另一口径为 +25bp" |
| #466 | ④政策面 | ECB 两条序列末观测与滞后 | {"DFR": ["2026-09-16", 2.5], "MRO": ["2026-09-16", 2.65], "lag": 68} | {"DFR": ["2026-09-16", 2.5], "MRO": ["2026-09-16", 2.65], "lag": 68} | 一致 | EA from_to "止于 2026-09-16(滞后68天)" |
| #467 | ④政策面 | 决议日=生效日惯例核对(星期) | {"2025-12-10": 3, "2025-12-11": 4, "2026-09-16": 3, "2026-09-17": 4, "2026-06-11": 4, "2026-06-17": 3, "2026-09-10": 4, "2026-09-18": 5, "2026-09-24": 4} | {"Fed 决议=生效前一日": "12-10→12-11 / 09-16→09-17", "ECB 决议=生效前上一个周四": "06-11(周四)→06-17(周三) / 09-10(周四)→09-16(周三)", "BOJ": "09-18→09-24"} | 一致 | M1.step2 / EA from_to / 证伪面(决议日回推惯例) |
| #480 | ④政策面 | CPI 决议时点(发布纪律)最近可见观测 2026-06-11 | {"obs": "2026-04-01", "yoy": 3.78, "pub": "2026-05-13"} | {"obs": "2026-04-01", "yoy": 3.78} | 一致 | M1.step2 |
| #481 | ④政策面 | CPI 决议时点(发布纪律)最近可见观测 2026-09-10 | {"obs": "2026-07-01", "yoy": 3.3, "pub": "2026-08-13"} | {"obs": "2026-07-01", "yoy": 3.3} | 一致 | M1.step2 |
| #482 | ④政策面 | CPI 决议时点(发布纪律)最近可见观测 2026-09-16 | {"obs": "2026-08-01", "yoy": 3.35, "pub": "2026-09-13"} | {"obs": "2026-08-01", "yoy": 3.35} | 一致 | M1.step2 |
| #483 | ④政策面 | CPI 决议时点(发布纪律)最近可见观测 2026-09-18 | {"obs": "2026-08-01", "yoy": 3.35, "pub": "2026-09-13"} | {"obs": "2026-08-01", "yoy": 3.35} | 一致 | M1.step2 |
| #484 | ④政策面 | CORE_PCE 决议时点(发布纪律)最近可见观测 2026-09-16 | {"obs": "2026-07-01", "value": 3.0, "pub": "2026-08-30"} | {"obs": "2026-07-01", "value": 3.0} | 一致 | M1.step2 / turning_supplement |
| #485 | ④政策面 | EA_HICP_YOY 决议时点(发布纪律)最近可见观测 2026-06-11 | {"obs": "2026-04-01", "value": 3.0, "pub": "2026-05-16"} | {"obs": "2026-04-01", "value": 3.0} | 一致 | M1.step2 / turning_supplement |
| #486 | ④政策面 | EA_HICP_YOY 决议时点(发布纪律)最近可见观测 2026-09-10 | {"obs": "2026-07-01", "value": 2.9, "pub": "2026-08-16"} | {"obs": "2026-07-01", "value": 2.9} | 一致 | M1.step2 / turning_supplement |
| #487 | ④政策面 | JP_CPI_YOY 决议时点(发布纪律)最近可见观测 2026-09-18 | {"obs": "2026-07-01", "value": 1.97, "pub": "2026-08-20"} | {"obs": "2026-07-01", "value": 1.97} | 一致 | M1.step2 / turning_supplement |
| #488 | ④政策面 | JP_CPI_TOKYO_YOY 决议时点(发布纪律)最近可见观测 2026-09-18 | {"obs": "2026-08-01", "value": 1.9, "pub": "2026-08-30"} | {"obs": "2026-08-01", "value": 1.9} | 一致 | M1.step2 / turning_supplement |
| #489 | ④政策面 | DFEDTARU 窗内(>=2025-11-19)变动点 | [["2025-12-11", 4.0, 3.75], ["2026-09-17", 3.75, 4.0]] | [["2025-12-11", 4.0, 3.75], ["2026-09-17", 3.75, 4.0]] | 一致 | US from_to |
| #490 | ④政策面 | DFF 2025-12 降息前台阶(2025-12-10 当日或之前) | ["2025-12-10", 3.89] | ["2025-12-10", 3.89] | 一致 | C1 "DFF 回到 2025-12 降息前的台阶附近(现 3.88)" |
| #491 | ④政策面 | DFEDTARU 按(含)锚日填充 2025-11-23/2026-08-23/2026-11-23 | [4.0, 3.75, 4.0] | [4.0, 3.75, 4.0] | 一致 | US from_to 渲染注记 |
| #877 | ④政策面 | DFF 三时点锚值(2025-11-22/2026-08-22/2026-11-19) 与 变动点值(2025-12-10→2025-12-11; 2026-09-16→2026-09-17) | {"anchors": [3.88, 3.63, 3.88], "change_points": [3.89, 3.64, 3.63, 3.88], "dec_bp_cut": -25, "dec_bp_hike": 25} | ["3.88→3.63→3.88(括注, 未标口径)", null, null, null, -25, 25] | 一致 | M1.step2 / TR1.step2 "(DFF 3.88→3.63→3.88)" / MAP_REPORT L196 |
| #880 | ④政策面 | EA_HICP_YOY 决议时点最近可见观测——注册表口径(月末+16天; 受审稿所述口径) | ["2026-04", 3.0, "2026-05-16"] | ["2026-04", 3.0, "2026-05-16"] | 一致 | M1.step2 / TR1.step2 / turning_supplement 决议 2026-06-11 |
| #881 | ④政策面 | EA_HICP_YOY 决议时点最近可见观测——引擎历史面两级发布规则口径(快报=观测月末当日可见,推定) | ["2026-05", 3.2, "2026-05-31", "rule:推定(快报月末)"] | ["2026-04", 3.0, "2026-05-16", "rule(月末+16)"] | NA(登记) | M1.step2 / TR1.step2 决议 2026-06-11(两级规则对照) |
| #882 | ④政策面 | EA_HICP_YOY 决议时点最近可见观测——注册表口径(月末+16天; 受审稿所述口径) | ["2026-07", 2.9, "2026-08-16"] | ["2026-07", 2.9, "2026-08-16"] | 一致 | M1.step2 / TR1.step2 / turning_supplement 决议 2026-09-10 |
| #883 | ④政策面 | EA_HICP_YOY 决议时点最近可见观测——引擎历史面两级发布规则口径(快报=观测月末当日可见,推定) | ["2026-08", 3.2, "2026-08-31", "rule:推定(快报月末)"] | ["2026-07", 2.9, "2026-08-16", "rule(月末+16)"] | NA(登记) | M1.step2 / TR1.step2 决议 2026-09-10(两级规则对照) |
| #896 | ④政策面 | ECB_DFR 一年窗(2025-11-23..2026-11-23)内上调变动点 | [["2026-06-17", 2.0, 2.25, 25], ["2026-09-16", 2.25, 2.5, 25]] | ECB_DFR 两度上调 | 一致 | agent_judgment.l3.contradictions[0].statement |
| #897 | ④政策面 | JP_POLICY_RATE 月均 2025-11..2026-10 逐月变动(bp) 最小值/上调月数/舍入级微降处 | {"min_bp": -0.1, "n_up_ge_1bp": 6, "rounding_dips": [["2026-04-01", -0.1], ["2026-08-01", -0.1]]} | JP_POLICY_RATE 持续上行 | 一致 | agent_judgment.l3.contradictions[0].statement |
| #904 | ④政策面 | CN_POLICY_OVERNIGHT 全序列观测数/首末观测日/取值集合 | [16, "2026-11-02", "2026-11-23", [1.25]] | ["新锚持平于其首个观测水平", "2026-11-02", 1.25] | 一致 | agent_judgment.l3.contradictions[2].statement / quality_gate_notes[4]② |
| #905 | ④政策面 | CN_LPR_1Y 一年窗内观测数/取值集合 + 截止日前最近观测 | [12, [3.0], ["2026-11-20", 3.0]] | CN_LPR_1Y …窗内持平 | 一致 | agent_judgment.l3.contradictions[2].statement / evidence_refs CN_LPR_1Y@2026-11-20 |
| #918 | ④政策面 | series_store.DFEDTARU 一年窗内变动点(date, from, to, delta_bp) | [["2025-12-11", 4.0, 3.75, -25], ["2026-09-17", 3.75, 4.0, 25]] | [["2025-12-11", 4.0, 3.75, -25], ["2026-09-17", 3.75, 4.0, 25]] | 一致 | agent_judgment.reader_map.regions[US].from_to / turnings[*].follow_or_diverge / headline_conclusion |
| #919 | ④政策面 | DFEDTARU 变动点生效日的上一个日历日(引擎惯例: 决议日=生效日前一日) 与其星期 | [["2025-12-11", "2025-12-10", 3], ["2026-09-17", "2026-09-16", 3]] | [["2025-12-11", "2025-12-10", 3], ["2026-09-17", "2026-09-16", 3]] | 一致 | agent_judgment.reader_map.regions[US].from_to / M1.step2 |
| #920 | ④政策面 | series_store.ECB_DFR 一年窗: 变动点之和(bp) / 窗启时在值(窗内首观测的前值) / 窗内首观测值→窗末观测值(bp) | {"net_change_points_bp": 50, "window_start_value": 2.0, "alt_first_obs_to_last_bp": 25, "n_change_points": 2} | {"panel_net_bp": 50, "alt_bp": 25, "start_value": 2.0} | 一致 | agent_judgment.quality_gate_notes[4] / EA from_to 口径注记 / JP from_to / M2.step1 |
| #921 | ④政策面 | series_store.ECB_MRO 一年窗: 变动点之和(bp) / 窗启时在值(窗内首观测的前值) / 窗内首观测值→窗末观测值(bp) | {"net_change_points_bp": 50, "window_start_value": 2.15, "alt_first_obs_to_last_bp": 25, "n_change_points": 2} | {"panel_net_bp": 50, "alt_bp": 25, "start_value": 2.15} | 一致 | agent_judgment.quality_gate_notes[4] / EA from_to 口径注记 / JP from_to / M2.step1 |
| #922 | ④政策面 | series_store.JP_POLICY_RATE 一年窗: 变动点之和(bp) / 窗启时在值(窗内首观测的前值) / 窗内首观测值→窗末观测值(bp) | {"net_change_points_bp": 75, "window_start_value": 0.478, "alt_first_obs_to_last_bp": 67, "n_change_points": 8} | {"panel_net_bp": 75, "alt_bp": 67, "start_value": 0.478} | 一致 | agent_judgment.quality_gate_notes[4] / EA from_to 口径注记 / JP from_to / M2.step1 |
| #923 | ④政策面 | root_overlay/config/release_calendar.json entries[RC-JP-BOJ-TARGET-2026-09 / RC-JP-BOJ-MAINT-2026-10]: decision_date/effective_on/target_value/kind | ["2026-09-18", "2026-09-24", 1.25, "policy_decision", "2026-10-30", "policy_maintenance", 1.25] | ["2026-09-18", "2026-09-24", 1.25, "policy_decision", "2026-10-30", "policy_maintenance", 1.25] | 一致 | agent_judgment.l3.mechanism_chains[1].links[0].text / quality_gate_notes[2] / regions[JP].from_to / turnings[2] / turning_supplement |
| #924 | ④政策面 | release_calendar.json: 政策类条目(kind=policy_decision/policy_maintenance)清单; 其中 metric 属美联储/欧央行(DFEDTARU/DFF/ECB_MRO/ECB_DFR)的条目数; 数据发布类条目数(美国停摆批次/HICP/LPR) | {"policy_entries": [["RC-JP-BOJ-TARGET-2026-09", "JP_POLICY_TARGET"], ["RC-JP-BOJ-MAINT-2026-10", "JP_POLICY_TARGET"]], "fed_ecb_policy_entries": [], "release_entries": {"US_shutdown": 11, "EA_HICP": 3, "CN_LPR": 2, "total": 16}} | 冻结发布日历无美联储与欧央行实录条目 | 一致 | agent_judgment.quality_gate_notes[2] / l4.scenarios[*].rows.trigger.condition |
| #925 | ④政策面 | ECB 第二次决议 2026-09-10 与 BOJ 决议 2026-09-18 的先后(决议日粒度) | 8 | ECB 09-10 早于 BOJ 09-18 | 一致 | agent_judgment.reader_map.turning_supplement[0].follow_or_diverge |
| #926 | ④政策面 | 2026 年 9 月收紧决议计数: EA(2026-06-17/2026-09-16 生效 +25bp)、US(2026-09-17 生效 +25bp)、JP(日历 2026-09-18 决议) | {"EA": ["2026-06-17", "2026-09-16"], "US": ["2026-09-17"], "JP_calendar": ["2026-09-18"]} | 2026-09 三次收紧决议 | 一致 | agent_judgment.l3.mechanism_chains[0].links[1].text |

### 2.11 ⑧历史类比面(记录 137 / 一致 136 / NA 1)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #496 | ⑧历史类比面 | HY_OAS 截至 2025-03-31 的月度观测数(候选月 2025-03) | 17 | 17 | 一致 | history_periods[0].difference "HY序列历史17个月<36" |
| #497 | ⑧历史类比面 | HY_OAS 首个观测日(2022-06/2023-10 候选月无 HY 观测) | 2023-11-21 | >2023-10 | 一致 | history_periods[1..2].difference "信用维候选月无HY观测" |
| #556 | ⑧历史类比面 | 有效候选数 | 74 | 74 | 一致 | history_periods[0].period_label "74个有效候选" / similarity |
| #557 | ⑧历史类比面 | TOP-N 独立簇数 | 5 | 5 | 一致 | period_label "TOP-5独立簇" |
| #558 | ⑧历史类比面 | report.json steps[analog].top[0].distance | 0.727212 | 0.7272 | 一致 | history_periods[0].period_label |
| #559 | ⑧历史类比面 | top[0].distance_percentile | 0.0 | 0.0 | 一致 | history_periods[0].period_label |
| #560 | ⑧历史类比面 | top[0].rank ↔ "TOP-5独立簇第N" | 1 | 1 | 一致 | history_periods[0].period_label |
| #561 | ⑧历史类比面 | top[0].dims 贡献份额(%, 舍入1位; <0.5% 维不列) | {"通胀": 10.5, "利率": 40.7, "波动": 42.1, "估值": 6.7} | {"波动": 42.1, "利率": 40.7, "通胀": 10.5, "估值": 6.7} | 一致 | history_periods[0].similarity |
| #562 | ⑧历史类比面 | top[0].features_detail \|gap\|>1 清单(完整性/方向/数值/降序) | [["CURVE_2S10S 12月变化", "候选期高于当前", 1.51], ["TIPS_10Y 12月变化", "当前高于候选期", 1.3], ["UST_10Y 12月变化", "当前高于候选期", 1.07]] | [["CURVE_2S10S 12月变化", "候选期高于当前", 1.51], ["TIPS_10Y 12月变化", "当前高于候选期", 1.3], ["UST_10Y 12月变化", "当前高于候选期", 1.07]] | 一致 | history_periods[0].difference "差异>1σ逐维点名" |
| #563 | ⑧历史类比面 | top[0].missing_features ↔ 信用维缺席注记 | ["hist_17<36"] | ["hist_17<36"] | 一致 | history_periods[0].difference 信用维注记 |
| #564 | ⑧历史类比面 | history_periods[0].match_window / aftermath_obs_months / judgment_cutoff_ym | [{"start_ym": "2024-04", "end_ym": "2025-03"}, ["2025-06", "2025-09", "2026-03"], "2025-03"] | [{"start_ym": "2024-04", "end_ym": "2025-03"}, ["2025-06", "2025-09", "2026-03"], "2025-03"] | 一致 | history_periods[0] (特征窗=锚前12个月) |
| #565 | ⑧历史类比面 | report.json steps[analog].top[1].distance | 0.791806 | 0.7918 | 一致 | history_periods[1].period_label |
| #566 | ⑧历史类比面 | top[1].distance_percentile | 1.3699 | 1.37 | 一致 | history_periods[1].period_label |
| #567 | ⑧历史类比面 | top[1].rank ↔ "TOP-5独立簇第N" | 2 | 2 | 一致 | history_periods[1].period_label |
| #568 | ⑧历史类比面 | top[1].dims 贡献份额(%, 舍入1位; <0.5% 维不列) | {"通胀": 11.4, "利率": 51.9, "波动": 3.0, "估值": 33.6} | {"利率": 51.9, "估值": 33.6, "通胀": 11.4, "波动": 3.0} | 一致 | history_periods[1].similarity |
| #569 | ⑧历史类比面 | top[1].features_detail \|gap\|>1 清单(完整性/方向/数值/降序) | [["TIPS_10Y 12月变化", "候选期高于当前", 1.74], ["CURVE_2S10S 12月变化", "当前高于候选期", 1.43], ["CURVE_2S10S水平", "当前高于候选期", 1.25], ["SPX CAPE", "当前高于候选期", 1.17]] | [["TIPS_10Y 12月变化", "候选期高于当前", 1.74], ["CURVE_2S10S 12月变化", "当前高于候选期", 1.43], ["CURVE_2S10S水平", "当前高于候选期", 1.25], ["SPX CAPE", "当前高于候选期", 1.17]] | 一致 | history_periods[1].difference "差异>1σ逐维点名" |
| #570 | ⑧历史类比面 | top[1].missing_features ↔ 信用维缺席注记 | ["no_value_at_candidate_month"] | ["no_value_at_candidate_month"] | 一致 | history_periods[1].difference 信用维注记 |
| #571 | ⑧历史类比面 | history_periods[1].match_window / aftermath_obs_months / judgment_cutoff_ym | [{"start_ym": "2021-07", "end_ym": "2022-06"}, ["2022-09", "2022-12", "2023-06"], "2022-06"] | [{"start_ym": "2021-07", "end_ym": "2022-06"}, ["2022-09", "2022-12", "2023-06"], "2022-06"] | 一致 | history_periods[1] (特征窗=锚前12个月) |
| #572 | ⑧历史类比面 | report.json steps[analog].top[2].distance | 1.054168 | 1.0542 | 一致 | history_periods[2].period_label |
| #573 | ⑧历史类比面 | top[2].distance_percentile | 30.137 | 30.14 | 一致 | history_periods[2].period_label |
| #574 | ⑧历史类比面 | top[2].rank ↔ "TOP-5独立簇第N" | 3 | 3 | 一致 | history_periods[2].period_label |
| #575 | ⑧历史类比面 | top[2].dims 贡献份额(%, 舍入1位; <0.5% 维不列) | {"通胀": 7.7, "利率": 11.0, "波动": 60.1, "估值": 21.2} | {"波动": 60.1, "估值": 21.2, "利率": 11.0, "通胀": 7.7} | 一致 | history_periods[2].similarity |
| #576 | ⑧历史类比面 | top[2].features_detail \|gap\|>1 清单(完整性/方向/数值/降序) | [["SPX 21日已实现波动", "当前高于候选期", 1.57], ["VIX水平", "当前高于候选期", 1.37], ["SPX CAPE", "当前高于候选期", 1.24], ["CURVE_2S10S 12月变化", "候选期高于当前", 1.01]] | [["SPX 21日已实现波动", "当前高于候选期", 1.57], ["VIX水平", "当前高于候选期", 1.37], ["SPX CAPE", "当前高于候选期", 1.24], ["CURVE_2S10S 12月变化", "候选期高于当前", 1.01]] | 一致 | history_periods[2].difference "差异>1σ逐维点名" |
| #577 | ⑧历史类比面 | top[2].missing_features ↔ 信用维缺席注记 | ["no_value_at_candidate_month"] | ["no_value_at_candidate_month"] | 一致 | history_periods[2].difference 信用维注记 |
| #578 | ⑧历史类比面 | history_periods[2].match_window / aftermath_obs_months / judgment_cutoff_ym | [{"start_ym": "2022-11", "end_ym": "2023-10"}, ["2024-01", "2024-04", "2024-10"], "2023-10"] | [{"start_ym": "2022-11", "end_ym": "2023-10"}, ["2024-01", "2024-04", "2024-10"], "2023-10"] | 一致 | history_periods[2] (特征窗=锚前12个月) |
| #579 | ⑧历史类比面 | state_vector 维度覆盖 growth/inflation/rates/credit/volatility/valuation | {"growth": 0.1667, "inflation": 0.3333, "rates": 0.75, "credit": 0.5, "volatility": 1.0, "valuation": 0.5} | {"growth": 0.17, "inflation": 0.33, "rates": 0.75, "credit": 0.5, "volatility": 1.0, "valuation": 0.5} | 一致 | sample_note "增长维覆盖0.17/通胀0.33/信用0.5" |
| #580 | ⑧历史类比面 | 特征窗月数 / 锚月 | [12, "2026-11"] | [12, "2026-11"] | 一致 | sample_note "当前特征窗(2025-12至2026-11)" |
| #581 | ⑧历史类比面 | TOP-N 事后符号一致率=1.0 的键 | ["GOLD_F_12m", "GOLD_F_6m", "SPX_12m", "SPX_6m"] | ["GOLD_F_12m", "GOLD_F_6m", "SPX_12m", "SPX_6m"] | 一致 | sample_note "GOLD_F 与 SPX 六个月与十二个月窗符号一致" |
| #582 | ⑧历史类比面 | TOP-N 事后符号一致率: 其余各窗取值集合 | [0.6, 0.8] | [0.6, 0.8] | 一致 | sample_note "其余各窗零点六至零点八" |
| #583 | ⑧历史类比面 | 一致率面序列集合 | ["DXY", "GOLD_F", "SPX", "UST_10Y"] | ["DXY", "GOLD_F", "SPX", "UST_10Y"] | 一致 | sample_note "一致率面仅含 DXY、GOLD_F、SPX、UST_10Y 四类" |
| #584 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2025-03: 2025-04-01→2025-04-30 | -1.136321 | -1.136321 | 一致 | report.json steps[analog].top[2025-03].aftermath.SPX.1m |
| #585 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2025-03: 2025-04-01→2025-06-30 | 10.152197 | 10.152197 | 一致 | report.json steps[analog].top[2025-03].aftermath.SPX.3m |
| #586 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2025-03: 2025-04-01→2025-09-30 | 18.735613 | 18.735613 | 一致 | report.json steps[analog].top[2025-03].aftermath.SPX.6m |
| #587 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2025-03: 2025-04-01→2026-03-31 | 15.896309 | 15.896309 | 一致 | report.json steps[analog].top[2025-03].aftermath.SPX.12m |
| #588 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2025-03: 2025-04-01→2025-04-30 | 0.0 | 0.0 | 一致 | report.json steps[analog].top[2025-03].aftermath.UST_10Y.1m |
| #589 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2025-03: 2025-04-01→2025-06-30 | 0.07 | 0.07 | 一致 | report.json steps[analog].top[2025-03].aftermath.UST_10Y.3m |
| #590 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2025-03: 2025-04-01→2025-09-30 | -0.01 | -0.01 | 一致 | report.json steps[analog].top[2025-03].aftermath.UST_10Y.6m |
| #591 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2025-03: 2025-04-01→2026-03-31 | 0.13 | 0.13 | 一致 | report.json steps[analog].top[2025-03].aftermath.UST_10Y.12m |
| #592 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2025-03: 2025-04-01→2025-04-30 | -4.594284 | -4.594284 | 一致 | report.json steps[analog].top[2025-03].aftermath.DXY.1m |
| #593 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2025-03: 2025-04-01→2025-06-30 | -7.078462 | -7.078462 | 一致 | report.json steps[analog].top[2025-03].aftermath.DXY.3m |
| #594 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2025-03: 2025-04-01→2025-09-30 | -6.224827 | -6.224827 | 一致 | report.json steps[analog].top[2025-03].aftermath.DXY.6m |
| #595 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2025-03: 2025-04-01→2026-03-31 | -4.124307 | -4.124307 | 一致 | report.json steps[analog].top[2025-03].aftermath.DXY.12m |
| #596 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2025-03: 2025-04-01→2025-04-30 | 5.502228 | 5.502228 | 一致 | report.json steps[analog].top[2025-03].aftermath.GOLD_F.1m |
| #597 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2025-03: 2025-04-01→2025-06-30 | 5.139859 | 5.139859 | 一致 | report.json steps[analog].top[2025-03].aftermath.GOLD_F.3m |
| #598 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2025-03: 2025-04-01→2025-09-30 | 23.115065 | 23.115065 | 一致 | report.json steps[analog].top[2025-03].aftermath.GOLD_F.6m |
| #599 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2025-03: 2025-04-01→2026-03-31 | 47.730454 | 47.730454 | 一致 | report.json steps[analog].top[2025-03].aftermath.GOLD_F.12m |
| #600 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2022-06: 2022-07-01→2022-07-29 | 7.972121 | 7.972121 | 一致 | report.json steps[analog].top[2022-06].aftermath.SPX.1m |
| #601 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2022-06: 2022-07-01→2022-09-30 | -6.266386 | -6.266386 | 一致 | report.json steps[analog].top[2022-06].aftermath.SPX.3m |
| #602 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2022-06: 2022-07-01→2022-12-30 | 0.370424 | 0.370424 | 一致 | report.json steps[analog].top[2022-06].aftermath.SPX.6m |
| #603 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2022-06: 2022-07-01→2023-06-30 | 16.339761 | 16.339761 | 一致 | report.json steps[analog].top[2022-06].aftermath.SPX.12m |
| #604 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2022-06: 2022-07-01→2022-07-29 | -0.21 | -0.21 | 一致 | report.json steps[analog].top[2022-06].aftermath.UST_10Y.1m |
| #605 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2022-06: 2022-07-01→2022-09-30 | 0.95 | 0.95 | 一致 | report.json steps[analog].top[2022-06].aftermath.UST_10Y.3m |
| #606 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2022-06: 2022-07-01→2022-12-30 | 1.0 | 1.0 | 一致 | report.json steps[analog].top[2022-06].aftermath.UST_10Y.6m |
| #607 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2022-06: 2022-07-01→2023-06-30 | 0.93 | 0.93 | 一致 | report.json steps[analog].top[2022-06].aftermath.UST_10Y.12m |
| #608 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2022-06: 2022-07-01→2022-07-29 | 0.722849 | 0.722849 | 一致 | report.json steps[analog].top[2022-06].aftermath.DXY.1m |
| #609 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2022-06: 2022-07-01→2022-09-30 | 6.638771 | 6.638771 | 一致 | report.json steps[analog].top[2022-06].aftermath.DXY.3m |
| #610 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2022-06: 2022-07-01→2022-12-30 | -1.540805 | -1.540805 | 一致 | report.json steps[analog].top[2022-06].aftermath.DXY.6m |
| #611 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2022-06: 2022-07-01→2023-06-30 | -2.120977 | -2.120977 | 一致 | report.json steps[analog].top[2022-06].aftermath.DXY.12m |
| #612 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2022-06: 2022-07-01→2022-07-29 | -2.142658 | -2.142658 | 一致 | report.json steps[analog].top[2022-06].aftermath.GOLD_F.1m |
| #613 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2022-06: 2022-07-01→2022-09-30 | -7.188454 | -7.188454 | 一致 | report.json steps[analog].top[2022-06].aftermath.GOLD_F.3m |
| #614 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2022-06: 2022-07-01→2022-12-30 | 1.371077 | 1.371077 | 一致 | report.json steps[analog].top[2022-06].aftermath.GOLD_F.6m |
| #615 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2022-06: 2022-07-01→2023-06-30 | 7.099641 | 7.099641 | 一致 | report.json steps[analog].top[2022-06].aftermath.GOLD_F.12m |
| #616 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2023-10: 2023-11-01→2023-11-30 | 7.785532 | 7.785532 | 一致 | report.json steps[analog].top[2023-10].aftermath.SPX.1m |
| #617 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2023-10: 2023-11-01→2024-01-31 | 14.34191 | 14.34191 | 一致 | report.json steps[analog].top[2023-10].aftermath.SPX.3m |
| #618 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2023-10: 2023-11-01→2024-04-30 | 18.82625 | 18.82625 | 一致 | report.json steps[analog].top[2023-10].aftermath.SPX.6m |
| #619 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2023-10: 2023-11-01→2024-10-31 | 34.630459 | 34.630459 | 一致 | report.json steps[analog].top[2023-10].aftermath.SPX.12m |
| #620 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2023-10: 2023-11-01→2023-11-30 | -0.4 | -0.4 | 一致 | report.json steps[analog].top[2023-10].aftermath.UST_10Y.1m |
| #621 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2023-10: 2023-11-01→2024-01-31 | -0.78 | -0.78 | 一致 | report.json steps[analog].top[2023-10].aftermath.UST_10Y.3m |
| #622 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2023-10: 2023-11-01→2024-04-30 | -0.08 | -0.08 | 一致 | report.json steps[analog].top[2023-10].aftermath.UST_10Y.6m |
| #623 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2023-10: 2023-11-01→2024-10-31 | -0.49 | -0.49 | 一致 | report.json steps[analog].top[2023-10].aftermath.UST_10Y.12m |
| #624 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2023-10: 2023-11-01→2023-11-30 | -3.162422 | -3.162422 | 一致 | report.json steps[analog].top[2023-10].aftermath.DXY.1m |
| #625 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2023-10: 2023-11-01→2024-01-31 | -3.37762 | -3.37762 | 一致 | report.json steps[analog].top[2023-10].aftermath.DXY.3m |
| #626 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2023-10: 2023-11-01→2024-04-30 | -0.617511 | -0.617511 | 一致 | report.json steps[analog].top[2023-10].aftermath.DXY.6m |
| #627 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2023-10: 2023-11-01→2024-10-31 | -2.713318 | -2.713318 | 一致 | report.json steps[analog].top[2023-10].aftermath.DXY.12m |
| #628 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2023-10: 2023-11-01→2023-11-30 | 2.545911 | 2.545911 | 一致 | report.json steps[analog].top[2023-10].aftermath.GOLD_F.1m |
| #629 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2023-10: 2023-11-01→2024-01-31 | 3.064146 | 3.064146 | 一致 | report.json steps[analog].top[2023-10].aftermath.GOLD_F.3m |
| #630 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2023-10: 2023-11-01→2024-04-30 | 15.869177 | 15.869177 | 一致 | report.json steps[analog].top[2023-10].aftermath.GOLD_F.6m |
| #631 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2023-10: 2023-11-01→2024-10-31 | 38.329562 | 38.329562 | 一致 | report.json steps[analog].top[2023-10].aftermath.GOLD_F.12m |
| #632 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2021-02: 2021-03-01→2021-03-31 | 1.821453 | 1.821453 | 一致 | report.json steps[analog].top[2021-02].aftermath.SPX.1m |
| #633 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2021-02: 2021-03-01→2021-05-28 | 7.747405 | 7.747405 | 一致 | report.json steps[analog].top[2021-02].aftermath.SPX.3m |
| #634 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2021-02: 2021-03-01→2021-08-31 | 15.912064 | 15.912064 | 一致 | report.json steps[analog].top[2021-02].aftermath.SPX.6m |
| #635 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2021-02: 2021-03-01→2022-02-28 | 12.099991 | 12.099991 | 一致 | report.json steps[analog].top[2021-02].aftermath.SPX.12m |
| #636 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2021-02: 2021-03-01→2021-03-31 | 0.29 | 0.29 | 一致 | report.json steps[analog].top[2021-02].aftermath.UST_10Y.1m |
| #637 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2021-02: 2021-03-01→2021-05-28 | 0.13 | 0.13 | 一致 | report.json steps[analog].top[2021-02].aftermath.UST_10Y.3m |
| #638 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2021-02: 2021-03-01→2021-08-31 | -0.15 | -0.15 | 一致 | report.json steps[analog].top[2021-02].aftermath.UST_10Y.6m |
| #639 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2021-02: 2021-03-01→2022-02-28 | 0.38 | 0.38 | 一致 | report.json steps[analog].top[2021-02].aftermath.UST_10Y.12m |
| #640 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2021-02: 2021-03-01→2021-03-31 | 2.405538 | 2.405538 | 一致 | report.json steps[analog].top[2021-02].aftermath.DXY.1m |
| #641 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2021-02: 2021-03-01→2021-05-28 | -1.109405 | -1.109405 | 一致 | report.json steps[analog].top[2021-02].aftermath.DXY.3m |
| #642 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2021-02: 2021-03-01→2021-08-31 | 1.746481 | 1.746481 | 一致 | report.json steps[analog].top[2021-02].aftermath.DXY.6m |
| #643 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2021-02: 2021-03-01→2022-02-28 | 6.228029 | 6.228029 | 一致 | report.json steps[analog].top[2021-02].aftermath.DXY.12m |
| #644 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2021-02: 2021-03-01→2021-03-31 | -0.53395 | -0.53395 | 一致 | report.json steps[analog].top[2021-02].aftermath.GOLD_F.1m |
| #645 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2021-02: 2021-03-01→2021-05-28 | 10.417876 | 10.417876 | 一致 | report.json steps[analog].top[2021-02].aftermath.GOLD_F.3m |
| #646 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2021-02: 2021-03-01→2021-08-31 | 5.519441 | 5.519441 | 一致 | report.json steps[analog].top[2021-02].aftermath.GOLD_F.6m |
| #647 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2021-02: 2021-03-01→2022-02-28 | 10.313404 | 10.313404 | 一致 | report.json steps[analog].top[2021-02].aftermath.GOLD_F.12m |
| #648 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2020-01: 2020-02-03→2020-02-28 | -9.070705 | -9.070705 | 一致 | report.json steps[analog].top[2020-01].aftermath.SPX.1m |
| #649 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2020-01: 2020-02-03→2020-04-30 | -10.35698 | -10.35698 | 一致 | report.json steps[analog].top[2020-01].aftermath.SPX.3m |
| #650 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2020-01: 2020-02-03→2020-07-31 | 0.68331 | 0.68331 | 一致 | report.json steps[analog].top[2020-01].aftermath.SPX.6m |
| #651 | ⑧历史类比面 | series_store.SPX 引擎事后块口径 2020-01: 2020-02-03→2021-01-29 | 14.3223 | 14.3223 | 一致 | report.json steps[analog].top[2020-01].aftermath.SPX.12m |
| #652 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2020-01: 2020-02-03→2020-02-28 | -0.41 | -0.41 | 一致 | report.json steps[analog].top[2020-01].aftermath.UST_10Y.1m |
| #653 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2020-01: 2020-02-03→2020-04-30 | -0.9 | -0.9 | 一致 | report.json steps[analog].top[2020-01].aftermath.UST_10Y.3m |
| #654 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2020-01: 2020-02-03→2020-07-31 | -0.99 | -0.99 | 一致 | report.json steps[analog].top[2020-01].aftermath.UST_10Y.6m |
| #655 | ⑧历史类比面 | series_store.UST_10Y 引擎事后块口径 2020-01: 2020-02-03→2021-01-29 | -0.43 | -0.43 | 一致 | report.json steps[analog].top[2020-01].aftermath.UST_10Y.12m |
| #656 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2020-01: 2020-02-03→2020-02-28 | 0.337417 | 0.337417 | 一致 | report.json steps[analog].top[2020-01].aftermath.DXY.1m |
| #657 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2020-01: 2020-02-03→2020-04-30 | 1.247438 | 1.247438 | 一致 | report.json steps[analog].top[2020-01].aftermath.DXY.3m |
| #658 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2020-01: 2020-02-03→2020-07-31 | -4.406958 | -4.406958 | 一致 | report.json steps[analog].top[2020-01].aftermath.DXY.6m |
| #659 | ⑧历史类比面 | series_store.DXY 引擎事后块口径 2020-01: 2020-02-03→2021-01-29 | -7.382414 | -7.382414 | 一致 | report.json steps[analog].top[2020-01].aftermath.DXY.12m |
| #660 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2020-01: 2020-02-03→2020-02-28 | -0.830584 | -0.830584 | 一致 | report.json steps[analog].top[2020-01].aftermath.GOLD_F.1m |
| #661 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2020-01: 2020-02-03→2020-04-30 | 6.784175 | 6.784175 | 一致 | report.json steps[analog].top[2020-01].aftermath.GOLD_F.3m |
| #662 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2020-01: 2020-02-03→2020-07-31 | 24.448397 | 24.448397 | 一致 | report.json steps[analog].top[2020-01].aftermath.GOLD_F.6m |
| #663 | ⑧历史类比面 | series_store.GOLD_F 引擎事后块口径 2020-01: 2020-02-03→2021-01-29 | 17.125292 | 17.125292 | 一致 | report.json steps[analog].top[2020-01].aftermath.GOLD_F.12m |
| #664 | ⑧历史类比面 | 事后块实际起止观测日落于引擎窗口界内 | [] | [] | 一致 | report.json top[*].aftermath.*_window |
| #665 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) SPX_1m | 0.6 | 0.6 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #666 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) SPX_3m | 0.6 | 0.6 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #667 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) SPX_6m | 1.0 | 1.0 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #668 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) SPX_12m | 1.0 | 1.0 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #669 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) UST_10Y_1m | 0.8 | 0.8 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #670 | ⑧历史类比面 | 同格严格符号口径(0 不计入任一侧) UST_10Y_1m | 0.6 | 0.8 | NA(登记) | report.json dispersion.topN_aftermath_sign_agreement |
| #671 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) UST_10Y_3m | 0.6 | 0.6 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #672 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) UST_10Y_6m | 0.8 | 0.8 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #673 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) UST_10Y_12m | 0.6 | 0.6 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #674 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) DXY_1m | 0.6 | 0.6 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #675 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) DXY_3m | 0.6 | 0.6 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #676 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) DXY_6m | 0.8 | 0.8 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #677 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) DXY_12m | 0.8 | 0.8 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #678 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) GOLD_F_1m | 0.6 | 0.6 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #679 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) GOLD_F_3m | 0.8 | 0.8 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #680 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) GOLD_F_6m | 1.0 | 1.0 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #681 | ⑧历史类比面 | TOP-5 独立簇事后符号一致率独立重算(引擎规则: 恰为0计非正侧) GOLD_F_12m | 1.0 | 1.0 | 一致 | report.json dispersion.topN_aftermath_sign_agreement |
| #682 | ⑧历史类比面 | TOP-5 候选月两两相差(月) ≥12 | [13, 16, 16, 17, 29, 32, 33, 45, 49, 62] | null | 一致 | candidates.cluster_dedup "候选月相差<12 个月=同簇"  TOP-5=['2025-03', '2022-06', '2023-10', '2021-02', '2020-01'] |
| #683 | ⑧历史类比面 | 起点观测差(价格类 SPX/DXY/GOLD_F, 候选3期): 月末口径起点(候选月末最后观测) vs 引擎起点(锚后首个观测) 最大绝对差 % | 1.06 | 约1个百分点 | 一致 | history_periods[*].ex_post.{3m,6m,12m} 括注 "引擎事后块起点为锚后首个观测,两口径数值可差约1个百分点"(起点差) |
| #684 | ⑧历史类比面 | 起点观测差(UST_10Y, 候选3期, pp) | [-0.06, -0.1, -0.11] | [-0.06, -0.1, -0.11] | 一致 | history_periods[*].ex_post 括注(起点差; 利率类) |
| #685 | ⑧历史类比面 | 受审稿月末口径与引擎事后块口径之差: SPX/UST_10Y/DXY/GOLD_F×3期×3窗=36 格收益/变动差 最大绝对差 (pp; 约=正负50%量级容差) | 1.41 | 约1个百分点 | 一致 | history_periods[*].ex_post 括注 "两口径数值可差约1个百分点"(结果数值差; 超过1.05pp的格数=6/36: [('2023-10', '12m', 'SPX', 1.41), ('2023-10', '6m', 'SPX', 1.24), ('2022-06', '12m', 'SPX… |
| #686 | ⑧历史类比面 | C2 "2022-06段股指三个月窗普遍收缩(DAX、SHCOMP、SPX、NIKKEI225 均为负)而十二个月窗除 SHCOMP 外转正" | true | true | 一致 | C2.statement |
| #687 | ⑧历史类比面 | C2 "2025-03、2023-10段风险资产与 GOLD_F 多数窗走强(2023-10段上证三个月窗为负，属例外)而 DXY 走弱" | true | true | 一致 | C2.statement |
| #852 | ⑧历史类比面 | report.json steps[analog].top[3]: candidate_month/distance/distance_percentile/前2贡献维(%, 舍入1位) | ["2021-02", 1.284945, 69.863, [["rates", 72.0], ["volatility", 18.4]]] | ["2021-02", 1.284945, 69.863, [["rates", 72.0], ["volatility", 18.4]]] | 一致 | FULL_REPORT.md 历史相似结构(读者版) rank 4 |
| #853 | ⑧历史类比面 | report.json steps[analog].top[4]: candidate_month/distance/distance_percentile/前2贡献维(%, 舍入1位) | ["2020-01", 1.357685, 71.2329, [["rates", 68.3], ["volatility", 14.6]]] | ["2020-01", 1.357685, 71.2329, [["rates", 68.3], ["volatility", 14.6]]] | 一致 | FULL_REPORT.md 历史相似结构(读者版) rank 5 |
| #864 | ⑧历史类比面 | agent_declaration "TOP-5独立簇": 前5名候选月两两间隔≥12个月; 引擎 dispersion.n_independent_clusters | [true, 5] | [true, 5] | 一致 | MAP_REPORT.md 历史段标题("TOP-5独立簇第N") / agent_declaration.basis |

### 2.12 ⑤三利率分解/资产窗(记录 8 / 一致 8 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #508 | ⑤三利率分解/资产窗 | series_store.UST_10Y@2025-11-19 / @2026-11-19 | [4.13, 5.04] | [4.13, 5.04] | 一致 | M1.step3 "十年期美债名义+91bp"(端点) |
| #509 | ⑤三利率分解/资产窗 | series_store.TIPS_10Y@2025-11-19 / @2026-11-19 | [1.86, 2.88] | [1.86, 2.88] | 一致 | M1.step3 "实际(TIPS_10Y) 2.88" |
| #510 | ⑤三利率分解/资产窗 | series_store.BEI_10Y@2025-11-19 / @2026-11-19 / @2026-11-20 | [2.27, 2.16, 2.15] | [2.27, 2.16, 2.15] | 一致 | M1.step3 "BEI_10Y 2.16@2026-11-19(最新 2.15@2026-11-20)" / TR1.step2 "2.27→2.16" |
| #511 | ⑤三利率分解/资产窗 | 12个月窗 2025-11-19→2026-11-19 名义/实际/盈亏平衡 (bp) | [91, 102, -11] | [91, 102, -11] | 一致 | M1.step3 / TR1.step3 / C1 "名义+91bp=实际+102bp+盈亏平衡-11bp" |
| #512 | ⑤三利率分解/资产窗 | 恒等残差 名义-实际-盈亏平衡 (bp) | 0 | 0 | 一致 | M1.step3 "恒等残差0" |
| #513 | ⑤三利率分解/资产窗 | 近1个月 2026-10-20→2026-11-19 名义/实际/盈亏平衡 (bp) | [-8, 11, -19] | [-8.0, 11.0, -19.0] | 一致 | reader_map.rates_decomposition(nominal_bp/real_bp/bei_bp) / TR1.step3 "实际+11个基点、盈亏平衡-19个基点" |
| #514 | ⑤三利率分解/资产窗 | rates_decomposition 窗口字段 | ["2026-10-20", "2026-11-19"] | ["2026-10-20", "2026-11-19"] | 一致 | reader_map.rates_decomposition.window_from/window_to |
| #515 | ⑤三利率分解/资产窗 | series_store.TIPS_10Y 2026-08-19→2026-11-19 (bp) | 53 | 53 | 一致 | M1.step4 / TR1.step3 "2026-08-19→2026-11-19 +53bp" |

### 2.13 ⑫时点标注(记录 6 / 一致 6 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #529 | ⑫时点标注 | 盘中/近24小时品种末观测日=截止日 2026-11-23 | {"SPX": "2026-11-23", "DAX": "2026-11-23", "CAC40": "2026-11-23", "VIX": "2026-11-23", "GOLD_F": "2026-11-23", "DXY": "2026-11-23", "BRENT_F": "2026-11-23", "USDJPY": "2026-11-23"} | {"SPX": "2026-11-23", "DAX": "2026-11-23", "CAC40": "2026-11-23", "VIX": "2026-11-23", "GOLD_F": "2026-11-23", "DXY": "2026-11-23", "BRENT_F": "2026-11-23", "USDJPY": "2026-11-23"} | 一致 | quality_gate_notes "SPX、DAX、CAC40、VIX 及近 24 小时交易品种(GOLD_F、DXY、BRENT_F)与外汇的当日值为盘中快照" |
| #530 | ⑫时点标注 | 末观测日 SHCOMP / NIKKEI225 | ["2026-11-23", "2026-11-20"] | ["2026-11-23", "2026-11-20"] | 一致 | quality_gate_notes "NIKKEI225 止于 2026-11-20 收盘、SHCOMP 为 2026-11-23 收盘" |
| #531 | ⑫时点标注 | 末观测日 UST_10Y/TIPS_10Y/DFF/HY_OAS / BEI_10Y | ["2026-11-19", "2026-11-19", "2026-11-19", "2026-11-19", "2026-11-20"] | ["2026-11-19", "2026-11-19", "2026-11-19", "2026-11-19", "2026-11-20"] | 一致 | M1.step3 "共同交易日 2025-11-19→2026-11-19" / 口径注记 |
| #532 | ⑫时点标注 | research_as_of 换算 纽约(EST)/法兰克福(CET)/东京(JST) | ["2026-11-23T22:53:47+08:00", "09:53", "15:53", "23:53"] | ["2026-11-23T22:53:47+08:00", "09:53", "15:53", "23:53"] | 一致 | quality_gate_notes "纽约 09:53、法兰克福 15:53、东京 23:53、上海 22:53" |
| #533 | ⑫时点标注 | 截止日 2026-11-23 星期(1=周一) | 1 | 1 | 一致 | 截止时点东京 23:53 JST 已过当日收盘; 纽约 09:53 EST 与法兰克福 15:53 CET 常规时段内 |
| #876 | ⑫时点标注 | NIKKEI225 截止日 2026-11-23(周一)无观测的原因面: 序列内 2016..2023 年落在工作日的 11-23 无观测年数 / 同日 SHCOMP、DAX 有观测年数 | {"nikkei_weekday_1123_missing": "7/7", "shcomp_obs": 7, "dax_obs": 7, "last_nikkei_obs": "2026-11-20", "cutoff_tokyo": "2026-11-23 23:53 JST(周一)"} | ["NIKKEI225 止于 2026-11-20 收盘(未说明 11-23 无观测的原因)", null, null, "2026-11-20", "2026-11-23"] | 一致 | quality_gate_notes[0] / TR1.step3 "NIKKEI225 止于 2026-11-20 收盘" |

### 2.14 ⑨情景阈值/期限(记录 10 / 一致 9 / NA 1)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #547 | ⑨情景阈值/期限 | series_store.BEI_10Y 库内最近一次低于 1.8 | ["2020-11-30", 1.77] | ["2020-11-30", 1.77] | 一致 | SCN2 证伪阈值依据 |
| #548 | ⑨情景阈值/期限 | BEI_10Y 最新 2.15 较 1.77 (bp) | 38 | 38 | 一致 | SCN2 "低 38 个基点" |
| #549 | ⑨情景阈值/期限 | BEI_10Y 最新 2.15 较阈值 1.8 (bp) | 35 | 35 | 一致 | SCN2 "高 35 个基点" |
| #550 | ⑨情景阈值/期限 | 两情景期限 | ["2027-02-28", "2027-02-28"] | ["2027-02-28", "2027-02-28"] | 一致 | quality_gate_notes "期限均为 2027-02-28" |
| #551 | ⑨情景阈值/期限 | SCN1 触发/证伪所涉观测的规则发布日均早于期限 2027-02-28 | {"CPI@2026-12": "2027-01-13", "CORE_PCE@2026-12": "2027-01-30", "CPI@2027-01": "2027-02-13"} | CPI 2026-12 / CORE_PCE 2026-12 / CPI 2027-01 | 一致 | SCN1 触发(2026-11或2026-12月CPI)/证伪(CPI<2.5 且 CORE_PCE<2.8 持续两个月)可观测性 |
| #552 | ⑨情景阈值/期限 | SCN1 触发(CPI同比继续≥3.5)/证伪(CPI<2.5 且 CORE_PCE<2.8) 与截止日读数相容(未证伪; 触发所涉 2026-11/12 观测尚未发布) | [3.72, 3.0, 3.12] | [3.72, 3.0, 3.12] | 一致 | SCN1 trigger/falsification ↔ TR1.step1 "2026-07 3.00 → 2026-09 3.12" / TR1.step2 "2026-09 观测回升至 3.72" |
| #553 | ⑨情景阈值/期限 | SCN2 证伪(BEI_10Y<1.8) 在截止日未成立; 触发所涉 2025-10 基期缺席 | [2.15, "no_same_period_base"] | [2.15, "no_same_period_base"] | 一致 | SCN2 "(2026-10 同比待 2025-10 基期补齐)" |
| #554 | ⑨情景阈值/期限 | SCN1 注 "2026-10 同比待 2025-10 基期补齐；2026-11 起同比不受此缺基期影响": CPI 基期 2025-10 缺席 / 2025-11、2025-12 在场 | [null, true, true] | [null, true, true] | 一致 | SCN1 falsification.threshold / SCN2 trigger.condition |
| #555 | ⑨情景阈值/期限 | 两情景方向互补 | ["SCN1: 股指承压/GOLD_F 受压/DXY 偏强/VIX 抬升", "SCN2: 股指修复/GOLD_F 走强/DXY 转弱"] | SCN1=承压·DXY偏强 / SCN2=修复·DXY转弱 | 一致 | L4 两情景资产方向互补(文字核对) |
| #917 | ⑨情景阈值/期限 | SCN1 前提/触发/证伪阈值(CPI>3 / ≥3.5 / <2.5 且 CORE_PCE<2.8)与 SCN2 证伪阈值(BEI_10Y<1.8): 席位自设参数, 无数据真值; 与截止日读数的相容性见 #552/#553 | {"CPI_2026-09": 3.72, "CORE_PCE_2026-09": 3.12, "BEI_10Y_2026-11-20": 2.15} | [3, 3.5, 2.5, 2.8, 1.8] | NA(登记) | agent_judgment.l4.scenarios[SCN1\|SCN2].rows |

### 2.15 ⑧历史事后窗(细表)(记录 82 / 一致 82 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #688 | ⑧历史事后窗(细表) | series_store.DFEDTARU(候选2025-03, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 4.5, "2025-06-30", 4.5, 0.0] | ["2025-03-31", 4.5, "2025-06-30", 4.5, 0.0] | 一致 | MAP_REPORT.md 行411 逐窗并列细表 |
| #689 | ⑧历史事后窗(细表) | series_store.UNEMPLOYMENT(候选2025-03, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-01", 4.2, "2025-06-01", 4.1, -0.1] | ["2025-03-01", 4.2, "2025-06-01", 4.1, -0.1] | 一致 | MAP_REPORT.md 行412 逐窗并列细表 |
| #690 | ⑧历史事后窗(细表) | series_store.CPI(候选2025-03, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-01", 319.785, "2025-06-01", 321.435, 0.515972] | ["2025-03-01", 319.785, "2025-06-01", 321.435, 0.516] | 一致 | MAP_REPORT.md 行413 逐窗并列细表 |
| #691 | ⑧历史事后窗(细表) | series_store.INDPRO(候选2025-03, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-01", 101.0404, "2025-06-01", 101.4785, 0.433589] | ["2025-03-01", 101.04, "2025-06-01", 101.478, 0.4336] | 一致 | MAP_REPORT.md 行414 逐窗并列细表 |
| #692 | ⑧历史事后窗(细表) | series_store.SPX(候选2025-03, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 5611.850098, "2025-06-30", 6204.950195, 10.568709] | ["2025-03-31", 5611.85, "2025-06-30", 6204.95, 10.5687] | 一致 | MAP_REPORT.md 行415 逐窗并列细表 |
| #693 | ⑧历史事后窗(细表) | series_store.UST_10Y(候选2025-03, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 4.23, "2025-06-30", 4.24, 0.01] | ["2025-03-31", 4.23, "2025-06-30", 4.24, 0.01] | 一致 | MAP_REPORT.md 行416 逐窗并列细表 |
| #694 | ⑧历史事后窗(细表) | series_store.DXY(候选2025-03, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 104.209999, "2025-06-30", 96.879997, -7.033876] | ["2025-03-31", 104.21, "2025-06-30", 96.88, -7.0339] | 一致 | MAP_REPORT.md 行417 逐窗并列细表 |
| #695 | ⑧历史事后窗(细表) | series_store.GOLD_F(候选2025-03, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 3122.800049, "2025-06-30", 3307.699951, 5.920965] | ["2025-03-31", 3122.8, "2025-06-30", 3307.7, 5.921] | 一致 | MAP_REPORT.md 行418 逐窗并列细表 |
| #696 | ⑧历史事后窗(细表) | series_store.NIKKEI225(候选2025-03, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 35617.56, "2025-06-30", 40487.39, 13.672554] | ["2025-03-31", 35617.6, "2025-06-30", 40487.4, 13.6726] | 一致 | MAP_REPORT.md 行419 逐窗并列细表 |
| #697 | ⑧历史事后窗(细表) | series_store.DFEDTARU(候选2025-03, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 4.5, "2025-09-30", 4.25, -0.25] | ["2025-03-31", 4.5, "2025-09-30", 4.25, -0.25] | 一致 | MAP_REPORT.md 行425 逐窗并列细表 |
| #698 | ⑧历史事后窗(细表) | series_store.UNEMPLOYMENT(候选2025-03, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-01", 4.2, "2025-09-01", 4.4, 0.2] | ["2025-03-01", 4.2, "2025-09-01", 4.4, 0.2] | 一致 | MAP_REPORT.md 行426 逐窗并列细表 |
| #699 | ⑧历史事后窗(细表) | series_store.CPI(候选2025-03, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-01", 319.785, "2025-09-01", 324.245, 1.394687] | ["2025-03-01", 319.785, "2025-09-01", 324.245, 1.3947] | 一致 | MAP_REPORT.md 行427 逐窗并列细表 |
| #700 | ⑧历史事后窗(细表) | series_store.INDPRO(候选2025-03, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-01", 101.0404, "2025-09-01", 101.668, 0.621138] | ["2025-03-01", 101.04, "2025-09-01", 101.668, 0.6211] | 一致 | MAP_REPORT.md 行428 逐窗并列细表 |
| #701 | ⑧历史事后窗(细表) | series_store.SPX(候选2025-03, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 5611.850098, "2025-09-30", 6688.459961, 19.18458] | ["2025-03-31", 5611.85, "2025-09-30", 6688.46, 19.1846] | 一致 | MAP_REPORT.md 行429 逐窗并列细表 |
| #702 | ⑧历史事后窗(细表) | series_store.UST_10Y(候选2025-03, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 4.23, "2025-09-30", 4.16, -0.07] | ["2025-03-31", 4.23, "2025-09-30", 4.16, -0.07] | 一致 | MAP_REPORT.md 行430 逐窗并列细表 |
| #703 | ⑧历史事后窗(细表) | series_store.DXY(候选2025-03, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 104.209999, "2025-09-30", 97.769997, -6.179831] | ["2025-03-31", 104.21, "2025-09-30", 97.77, -6.1798] | 一致 | MAP_REPORT.md 行431 逐窗并列细表 |
| #704 | ⑧历史事后窗(细表) | series_store.GOLD_F(候选2025-03, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 3122.800049, "2025-09-30", 3873.199951, 24.029713] | ["2025-03-31", 3122.8, "2025-09-30", 3873.2, 24.0297] | 一致 | MAP_REPORT.md 行432 逐窗并列细表 |
| #705 | ⑧历史事后窗(细表) | series_store.NIKKEI225(候选2025-03, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 35617.56, "2025-09-30", 44932.63, 26.153027] | ["2025-03-31", 35617.6, "2025-09-30", 44932.6, 26.153] | 一致 | MAP_REPORT.md 行433 逐窗并列细表 |
| #706 | ⑧历史事后窗(细表) | series_store.DFEDTARU(候选2025-03, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 4.5, "2026-03-31", 3.75, -0.75] | ["2025-03-31", 4.5, "2026-03-31", 3.75, -0.75] | 一致 | MAP_REPORT.md 行439 逐窗并列细表 |
| #707 | ⑧历史事后窗(细表) | series_store.UNEMPLOYMENT(候选2025-03, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-01", 4.2, "2026-03-01", 4.3, 0.1] | ["2025-03-01", 4.2, "2026-03-01", 4.3, 0.1] | 一致 | MAP_REPORT.md 行440 逐窗并列细表 |
| #708 | ⑧历史事后窗(细表) | series_store.CPI(候选2025-03, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-01", 319.785, "2026-03-01", 330.293, 3.285958] | ["2025-03-01", 319.785, "2026-03-01", 330.293, 3.286] | 一致 | MAP_REPORT.md 行441 逐窗并列细表 |
| #709 | ⑧历史事后窗(细表) | series_store.INDPRO(候选2025-03, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-01", 101.0404, "2026-03-01", 101.7336, 0.686062] | ["2025-03-01", 101.04, "2026-03-01", 101.734, 0.6861] | 一致 | MAP_REPORT.md 行442 逐窗并列细表 |
| #710 | ⑧历史事后窗(细表) | series_store.SPX(候选2025-03, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 5611.850098, "2026-03-31", 6528.52002, 16.33454] | ["2025-03-31", 5611.85, "2026-03-31", 6528.52, 16.3345] | 一致 | MAP_REPORT.md 行443 逐窗并列细表 |
| #711 | ⑧历史事后窗(细表) | series_store.UST_10Y(候选2025-03, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 4.23, "2026-03-31", 4.3, 0.07] | ["2025-03-31", 4.23, "2026-03-31", 4.3, 0.07] | 一致 | MAP_REPORT.md 行444 逐窗并列细表 |
| #712 | ⑧历史事后窗(细表) | series_store.DXY(候选2025-03, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 104.209999, "2026-03-31", 99.959999, -4.078303] | ["2025-03-31", 104.21, "2026-03-31", 99.96, -4.0783] | 一致 | MAP_REPORT.md 行445 逐窗并列细表 |
| #713 | ⑧历史事后窗(细表) | series_store.GOLD_F(候选2025-03, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 3122.800049, "2026-03-31", 4647.600098, 48.827976] | ["2025-03-31", 3122.8, "2026-03-31", 4647.6, 48.828] | 一致 | MAP_REPORT.md 行446 逐窗并列细表 |
| #714 | ⑧历史事后窗(细表) | series_store.NIKKEI225(候选2025-03, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2025-03-31", 35617.56, "2026-03-31", 51063.72, 43.366699] | ["2025-03-31", 35617.6, "2026-03-31", 51063.7, 43.3667] | 一致 | MAP_REPORT.md 行447 逐窗并列细表 |
| #715 | ⑧历史事后窗(细表) | series_store.DFEDTARU(候选2022-06, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 1.75, "2022-09-30", 3.25, 1.5] | ["2022-06-30", 1.75, "2022-09-30", 3.25, 1.5] | 一致 | MAP_REPORT.md 行535 逐窗并列细表 |
| #716 | ⑧历史事后窗(细表) | series_store.UNEMPLOYMENT(候选2022-06, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-01", 3.6, "2022-09-01", 3.5, -0.1] | ["2022-06-01", 3.6, "2022-09-01", 3.5, -0.1] | 一致 | MAP_REPORT.md 行536 逐窗并列细表 |
| #717 | ⑧历史事后窗(细表) | series_store.CPI(候选2022-06, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-01", 294.957, "2022-09-01", 296.349, 0.471933] | ["2022-06-01", 294.957, "2022-09-01", 296.349, 0.4719] | 一致 | MAP_REPORT.md 行537 逐窗并列细表 |
| #718 | ⑧历史事后窗(细表) | series_store.INDPRO(候选2022-06, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-01", 101.018, "2022-09-01", 101.2918, 0.271041] | ["2022-06-01", 101.018, "2022-09-01", 101.292, 0.271] | 一致 | MAP_REPORT.md 行538 逐窗并列细表 |
| #719 | ⑧历史事后窗(细表) | series_store.SPX(候选2022-06, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 3785.379883, "2022-09-30", 3585.620117, -5.277139] | ["2022-06-30", 3785.38, "2022-09-30", 3585.62, -5.2771] | 一致 | MAP_REPORT.md 行539 逐窗并列细表 |
| #720 | ⑧历史事后窗(细表) | series_store.UST_10Y(候选2022-06, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 2.98, "2022-09-30", 3.83, 0.85] | ["2022-06-30", 2.98, "2022-09-30", 3.83, 0.85] | 一致 | MAP_REPORT.md 行540 逐窗并列细表 |
| #721 | ⑧历史事后窗(细表) | series_store.DXY(候选2022-06, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 104.690002, "2022-09-30", 112.120003, 7.097145] | ["2022-06-30", 104.69, "2022-09-30", 112.12, 7.0971] | 一致 | MAP_REPORT.md 行541 逐窗并列细表 |
| #722 | ⑧历史事后窗(细表) | series_store.GOLD_F(候选2022-06, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 1807.300049, "2022-09-30", 1672.0, -7.486308] | ["2022-06-30", 1807.3, "2022-09-30", 1672.0, -7.4863] | 一致 | MAP_REPORT.md 行542 逐窗并列细表 |
| #723 | ⑧历史事后窗(细表) | series_store.NIKKEI225(候选2022-06, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 26393.04, "2022-09-30", 25937.21, -1.727084] | ["2022-06-30", 26393.0, "2022-09-30", 25937.2, -1.7271] | 一致 | MAP_REPORT.md 行543 逐窗并列细表 |
| #724 | ⑧历史事后窗(细表) | series_store.DFEDTARU(候选2022-06, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 1.75, "2022-12-31", 4.5, 2.75] | ["2022-06-30", 1.75, "2022-12-31", 4.5, 2.75] | 一致 | MAP_REPORT.md 行549 逐窗并列细表 |
| #725 | ⑧历史事后窗(细表) | series_store.UNEMPLOYMENT(候选2022-06, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-01", 3.6, "2022-12-01", 3.5, -0.1] | ["2022-06-01", 3.6, "2022-12-01", 3.5, -0.1] | 一致 | MAP_REPORT.md 行550 逐窗并列细表 |
| #726 | ⑧历史事后窗(细表) | series_store.CPI(候选2022-06, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-01", 294.957, "2022-12-01", 298.832, 1.313751] | ["2022-06-01", 294.957, "2022-12-01", 298.832, 1.3138] | 一致 | MAP_REPORT.md 行551 逐窗并列细表 |
| #727 | ⑧历史事后窗(细表) | series_store.INDPRO(候选2022-06, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-01", 101.018, "2022-12-01", 99.7664, -1.238987] | ["2022-06-01", 101.018, "2022-12-01", 99.7664, -1.239] | 一致 | MAP_REPORT.md 行552 逐窗并列细表 |
| #728 | ⑧历史事后窗(细表) | series_store.SPX(候选2022-06, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 3785.379883, "2022-12-30", 3839.5, 1.429714] | ["2022-06-30", 3785.38, "2022-12-30", 3839.5, 1.4297] | 一致 | MAP_REPORT.md 行553 逐窗并列细表 |
| #729 | ⑧历史事后窗(细表) | series_store.UST_10Y(候选2022-06, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 2.98, "2022-12-30", 3.88, 0.9] | ["2022-06-30", 2.98, "2022-12-30", 3.88, 0.9] | 一致 | MAP_REPORT.md 行554 逐窗并列细表 |
| #730 | ⑧历史事后窗(细表) | series_store.DXY(候选2022-06, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 104.690002, "2022-12-30", 103.519997, -1.11759] | ["2022-06-30", 104.69, "2022-12-30", 103.52, -1.1176] | 一致 | MAP_REPORT.md 行555 逐窗并列细表 |
| #731 | ⑧历史事后窗(细表) | series_store.GOLD_F(候选2022-06, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 1807.300049, "2022-12-30", 1826.199951, 1.045753] | ["2022-06-30", 1807.3, "2022-12-30", 1826.2, 1.0458] | 一致 | MAP_REPORT.md 行556 逐窗并列细表 |
| #732 | ⑧历史事后窗(细表) | series_store.NIKKEI225(候选2022-06, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 26393.04, "2022-12-30", 26094.5, -1.131132] | ["2022-06-30", 26393.0, "2022-12-30", 26094.5, -1.1311] | 一致 | MAP_REPORT.md 行557 逐窗并列细表 |
| #733 | ⑧历史事后窗(细表) | series_store.DFEDTARU(候选2022-06, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 1.75, "2023-06-30", 5.25, 3.5] | ["2022-06-30", 1.75, "2023-06-30", 5.25, 3.5] | 一致 | MAP_REPORT.md 行563 逐窗并列细表 |
| #734 | ⑧历史事后窗(细表) | series_store.UNEMPLOYMENT(候选2022-06, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-01", 3.6, "2023-06-01", 3.6, 0.0] | ["2022-06-01", 3.6, "2023-06-01", 3.6, 0.0] | 一致 | MAP_REPORT.md 行564 逐窗并列细表 |
| #735 | ⑧历史事后窗(细表) | series_store.CPI(候选2022-06, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-01", 294.957, "2023-06-01", 304.014, 3.070617] | ["2022-06-01", 294.957, "2023-06-01", 304.014, 3.0706] | 一致 | MAP_REPORT.md 行565 逐窗并列细表 |
| #736 | ⑧历史事后窗(细表) | series_store.INDPRO(候选2022-06, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-01", 101.018, "2023-06-01", 100.1196, -0.889346] | ["2022-06-01", 101.018, "2023-06-01", 100.12, -0.8893] | 一致 | MAP_REPORT.md 行566 逐窗并列细表 |
| #737 | ⑧历史事后窗(细表) | series_store.SPX(候选2022-06, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 3785.379883, "2023-06-30", 4450.379883, 17.56759] | ["2022-06-30", 3785.38, "2023-06-30", 4450.38, 17.5676] | 一致 | MAP_REPORT.md 行567 逐窗并列细表 |
| #738 | ⑧历史事后窗(细表) | series_store.UST_10Y(候选2022-06, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 2.98, "2023-06-30", 3.81, 0.83] | ["2022-06-30", 2.98, "2023-06-30", 3.81, 0.83] | 一致 | MAP_REPORT.md 行568 逐窗并列细表 |
| #739 | ⑧历史事后窗(细表) | series_store.DXY(候选2022-06, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 104.690002, "2023-06-30", 102.910004, -1.700256] | ["2022-06-30", 104.69, "2023-06-30", 102.91, -1.7003] | 一致 | MAP_REPORT.md 行569 逐窗并列细表 |
| #740 | ⑧历史事后窗(细表) | series_store.GOLD_F(候选2022-06, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 1807.300049, "2023-06-30", 1929.400024, 6.755933] | ["2022-06-30", 1807.3, "2023-06-30", 1929.4, 6.7559] | 一致 | MAP_REPORT.md 行570 逐窗并列细表 |
| #741 | ⑧历史事后窗(细表) | series_store.NIKKEI225(候选2022-06, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2022-06-30", 26393.04, "2023-06-30", 33189.04, 25.749213] | ["2022-06-30", 26393.0, "2023-06-30", 33189.0, 25.7492] | 一致 | MAP_REPORT.md 行571 逐窗并列细表 |
| #742 | ⑧历史事后窗(细表) | series_store.DFEDTARU(候选2023-10, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 5.5, "2024-01-31", 5.5, 0.0] | ["2023-10-31", 5.5, "2024-01-31", 5.5, 0.0] | 一致 | MAP_REPORT.md 行643 逐窗并列细表 |
| #743 | ⑧历史事后窗(细表) | series_store.UNEMPLOYMENT(候选2023-10, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-01", 3.9, "2024-01-01", 3.7, -0.2] | ["2023-10-01", 3.9, "2024-01-01", 3.7, -0.2] | 一致 | MAP_REPORT.md 行644 逐窗并列细表 |
| #744 | ⑧历史事后窗(细表) | series_store.CPI(候选2023-10, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-01", 307.696, "2024-01-01", 309.698, 0.650642] | ["2023-10-01", 307.696, "2024-01-01", 309.698, 0.6506] | 一致 | MAP_REPORT.md 行645 逐窗并列细表 |
| #745 | ⑧历史事后窗(细表) | series_store.INDPRO(候选2023-10, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-01", 100.4689, "2024-01-01", 99.2223, -1.240782] | ["2023-10-01", 100.469, "2024-01-01", 99.2223, -1.2408] | 一致 | MAP_REPORT.md 行646 逐窗并列细表 |
| #746 | ⑧历史事后窗(细表) | series_store.SPX(候选2023-10, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 4193.799805, "2024-01-31", 4845.649902, 15.543186] | ["2023-10-31", 4193.8, "2024-01-31", 4845.65, 15.5432] | 一致 | MAP_REPORT.md 行647 逐窗并列细表 |
| #747 | ⑧历史事后窗(细表) | series_store.UST_10Y(候选2023-10, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 4.88, "2024-01-31", 3.99, -0.89] | ["2023-10-31", 4.88, "2024-01-31", 3.99, -0.89] | 一致 | MAP_REPORT.md 行648 逐窗并列细表 |
| #748 | ⑧历史事后窗(细表) | series_store.DXY(候选2023-10, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 106.660004, "2024-01-31", 103.269997, -3.17833] | ["2023-10-31", 106.66, "2024-01-31", 103.27, -3.1783] | 一致 | MAP_REPORT.md 行649 逐窗并列细表 |
| #749 | ⑧历史事后窗(细表) | series_store.GOLD_F(候选2023-10, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 1994.300049, "2024-01-31", 2048.399902, 2.712724] | ["2023-10-31", 1994.3, "2024-01-31", 2048.4, 2.7127] | 一致 | MAP_REPORT.md 行650 逐窗并列细表 |
| #750 | ⑧历史事后窗(细表) | series_store.NIKKEI225(候选2023-10, +3个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 30858.85, "2024-01-31", 36286.71, 17.589314] | ["2023-10-31", 30858.8, "2024-01-31", 36286.7, 17.5893] | 一致 | MAP_REPORT.md 行651 逐窗并列细表 |
| #751 | ⑧历史事后窗(细表) | series_store.DFEDTARU(候选2023-10, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 5.5, "2024-04-30", 5.5, 0.0] | ["2023-10-31", 5.5, "2024-04-30", 5.5, 0.0] | 一致 | MAP_REPORT.md 行657 逐窗并列细表 |
| #752 | ⑧历史事后窗(细表) | series_store.UNEMPLOYMENT(候选2023-10, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-01", 3.9, "2024-04-01", 3.9, 0.0] | ["2023-10-01", 3.9, "2024-04-01", 3.9, 0.0] | 一致 | MAP_REPORT.md 行658 逐窗并列细表 |
| #753 | ⑧历史事后窗(细表) | series_store.CPI(候选2023-10, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-01", 307.696, "2024-04-01", 313.023, 1.731254] | ["2023-10-01", 307.696, "2024-04-01", 313.023, 1.7313] | 一致 | MAP_REPORT.md 行659 逐窗并列细表 |
| #754 | ⑧历史事后窗(细表) | series_store.INDPRO(候选2023-10, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-01", 100.4689, "2024-04-01", 100.2434, -0.224448] | ["2023-10-01", 100.469, "2024-04-01", 100.243, -0.2244] | 一致 | MAP_REPORT.md 行660 逐窗并列细表 |
| #755 | ⑧历史事后窗(细表) | series_store.SPX(候选2023-10, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 4193.799805, "2024-04-30", 5035.689941, 20.074638] | ["2023-10-31", 4193.8, "2024-04-30", 5035.69, 20.0746] | 一致 | MAP_REPORT.md 行661 逐窗并列细表 |
| #756 | ⑧历史事后窗(细表) | series_store.UST_10Y(候选2023-10, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 4.88, "2024-04-30", 4.69, -0.19] | ["2023-10-31", 4.88, "2024-04-30", 4.69, -0.19] | 一致 | MAP_REPORT.md 行662 逐窗并列细表 |
| #757 | ⑧历史事后窗(细表) | series_store.DXY(候选2023-10, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 106.660004, "2024-04-30", 106.220001, -0.412529] | ["2023-10-31", 106.66, "2024-04-30", 106.22, -0.4125] | 一致 | MAP_REPORT.md 行663 逐窗并列细表 |
| #758 | ⑧历史事后窗(细表) | series_store.GOLD_F(候选2023-10, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 1994.300049, "2024-04-30", 2302.899902, 15.474093] | ["2023-10-31", 1994.3, "2024-04-30", 2302.9, 15.4741] | 一致 | MAP_REPORT.md 行664 逐窗并列细表 |
| #759 | ⑧历史事后窗(细表) | series_store.NIKKEI225(候选2023-10, +6个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 30858.85, "2024-04-30", 38405.66, 24.455902] | ["2023-10-31", 30858.8, "2024-04-30", 38405.7, 24.4559] | 一致 | MAP_REPORT.md 行665 逐窗并列细表 |
| #760 | ⑧历史事后窗(细表) | series_store.DFEDTARU(候选2023-10, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 5.5, "2024-10-31", 5.0, -0.5] | ["2023-10-31", 5.5, "2024-10-31", 5.0, -0.5] | 一致 | MAP_REPORT.md 行671 逐窗并列细表 |
| #761 | ⑧历史事后窗(细表) | series_store.UNEMPLOYMENT(候选2023-10, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-01", 3.9, "2024-10-01", 4.1, 0.2] | ["2023-10-01", 3.9, "2024-10-01", 4.1, 0.2] | 一致 | MAP_REPORT.md 行672 逐窗并列细表 |
| #762 | ⑧历史事后窗(细表) | series_store.CPI(候选2023-10, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-01", 307.696, "2024-10-01", 315.631, 2.578844] | ["2023-10-01", 307.696, "2024-10-01", 315.631, 2.5788] | 一致 | MAP_REPORT.md 行673 逐窗并列细表 |
| #763 | ⑧历史事后窗(细表) | series_store.INDPRO(候选2023-10, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-01", 100.4689, "2024-10-01", 99.4695, -0.994736] | ["2023-10-01", 100.469, "2024-10-01", 99.4695, -0.9947] | 一致 | MAP_REPORT.md 行674 逐窗并列细表 |
| #764 | ⑧历史事后窗(细表) | series_store.SPX(候选2023-10, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 4193.799805, "2024-10-31", 5705.450195, 36.044887] | ["2023-10-31", 4193.8, "2024-10-31", 5705.45, 36.0449] | 一致 | MAP_REPORT.md 行675 逐窗并列细表 |
| #765 | ⑧历史事后窗(细表) | series_store.UST_10Y(候选2023-10, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 4.88, "2024-10-31", 4.28, -0.6] | ["2023-10-31", 4.88, "2024-10-31", 4.28, -0.6] | 一致 | MAP_REPORT.md 行676 逐窗并列细表 |
| #766 | ⑧历史事后窗(细表) | series_store.DXY(候选2023-10, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 106.660004, "2024-10-31", 103.980003, -2.512658] | ["2023-10-31", 106.66, "2024-10-31", 103.98, -2.5127] | 一致 | MAP_REPORT.md 行677 逐窗并列细表 |
| #767 | ⑧历史事后窗(细表) | series_store.GOLD_F(候选2023-10, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 1994.300049, "2024-10-31", 2749.300049, 37.857894] | ["2023-10-31", 1994.3, "2024-10-31", 2749.3, 37.8579] | 一致 | MAP_REPORT.md 行678 逐窗并列细表 |
| #768 | ⑧历史事后窗(细表) | series_store.NIKKEI225(候选2023-10, +12个月; 起止=候选月末/+N月末或之前最近观测) | ["2023-10-31", 30858.85, "2024-10-31", 39081.25, 26.645193] | ["2023-10-31", 30858.8, "2024-10-31", 39081.2, 26.6452] | 一致 | MAP_REPORT.md 行679 逐窗并列细表 |
| #769 | ⑧历史事后窗(细表) | MAP 历史段逐窗并列细表行数(3段×3窗×9行) | 81 | 81 | 一致 | MAP_REPORT.md 历史段细表 |

### 2.16 ⑩走位/转折叙述(记录 36 / 一致 36 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #770 | ⑩走位/转折叙述 | series_store.US_REAL_GDP(2025-04-01/2026-04-01/2026-07-01) | [23884.563, 24408.011, 24611.077] | [23884.563, 24408.011, 24611.077] | 一致 | MAP_REPORT 美国走位 "水平 23884.563→24408.011→24611.077 十亿美元" |
| #771 | ⑩走位/转折叙述 | release_calendar.entries[RC-2025SHUTDOWN-GDP-Q3](obs_from, first_publish_on_or_after) | ["2025-07-01", "2025-12-23"] | ["2025-07-01", "2025-12-23"] | 一致 | 美国走位 "2025 年第三季度 GDP 因 2025 年联邦政府停摆延至 2025-12-23 首发" |
| #772 | ⑩走位/转折叙述 | 12个月前锚 2025-11-23 按发布纪律可见的最新季度观测日: US / EA / JP | ["2025-04-01", "2025-07-01", "2025-07-01"] | ["2025Q2=2025-04-01", "2025Q3=2025-07-01", "2025Q3=2025-07-01"] | 一致 | 美国走位 "12个月前锚前最新已发布季度为 2025Q2…较欧元区、日本同锚早一个季度" |
| #773 | ⑩走位/转折叙述 | CN_PMI_MFG 指数点差(本月水平−去年同月水平) 2025-10/2026-07/2026-10 | [-1.1, -0.1, 0.3] | [-1.1, -0.1, 0.3] | 一致 | 中国走位 "即相差约 -1.1、-0.1、+0.3 个指数点" |
| #774 | ⑩走位/转折叙述 | CN_PMI_MFG 2025-11..2026-10 站上荣枯线(>50)的月份与读数 | [["2025-12", 50.1], ["2026-03", 50.4], ["2026-04", 50.3], ["2026-06", 50.3], ["2026-09", 50.1]] | [["2025-12", 50.1], ["2026-03", 50.4], ["2026-04", 50.3], ["2026-06", 50.3], ["2026-09", 50.1]] | 一致 | 中国走位/C1 "2025-12、2026-03、2026-04、2026-06、2026-09 共五个月站上荣枯线(50.1/50.4/50.3/50.3/50.1)" |
| #775 | ⑩走位/转折叙述 | CN_PMI_MFG 2025-11..2026-10 持平于 50.0 的月份 | [["2026-05", 50.0]] | [["2026-05", 50.0]] | 一致 | 中国走位 "2026-05 持平于 50.0" |
| #776 | ⑩走位/转折叙述 | CN_PMI_MFG 2025-11..2026-10 其余(<50)月份的读数范围与窗内月数 | [49.0, 49.8, 12] | [49.0, 49.8, 12] | 一致 | 中国走位 "其余月份落在 49.0–49.8 之间" |
| #777 | ⑩走位/转折叙述 | CN_POLICY_OVERNIGHT 序列: 首观测日/末观测日/取值集合/观测数 | ["2026-11-02", "2026-11-23", [1.25], 16] | ["2026-11-02", "2026-11-23", [1.25], 16] | 一致 | 中国走位 "12个月前与3个月前锚日前无已发布观测,最新 1.25@2026-11-23(换锚后持平于首个观测值)" |
| #778 | ⑩走位/转折叙述 | CN_POLICY_OVERNIGHT 锚日(2025-11-23/2026-08-23)当日及之前观测数 | [0, 0] | [0, 0] | 一致 | 同上(锚日前无观测) |
| #779 | ⑩走位/转折叙述 | CN_OMO_7D 一年窗(2025-11-23..2026-11-23)内取值集合/窗内观测数/末观测日 | [[1.4], 199, "2026-10-30"] | [[1.4], 199, "2026-10-30"] | 一致 | 中国走位/C1 "7天逆回购利率…窗内无变动…末观测 2026-10-30、其后缺观测" |
| #780 | ⑩走位/转折叙述 | CN_LPR_1Y 一年窗内取值集合/窗启时在值(2025-11-20) | [[3.0], ["2025-11-20", 3.0]] | [[3.0], ["2025-11-20", 3.0]] | 一致 | 中国走位 "LPR_1Y 3.0→3.0→3.0 窗内持平" |
| #781 | ⑩走位/转折叙述 | EA_HICP_YOY 2026-01..2026-10 | [1.7, 1.9, 2.6, 3.0, 3.2, 2.8, 2.9, 3.2, 3.8, 4.0] | [1.7, 1.9, 2.6, 3.0, 3.2, 2.8, 2.9, 3.2, 3.8, 4.0] | 一致 | 欧元区走位 "自2026-01低点1.7连续上行至2026-05的3.2，2026-06回落至2.8后自2026-07再度上行…最新4.0" |
| #782 | ⑩走位/转折叙述 | EA_HICP_YOY 月度增量 2026-07..2026-10 | {"2026-07": 0.1, "2026-08": 0.3, "2026-09": 0.6, "2026-10": 0.2} | {"2026-07": 0.1, "2026-08": 0.3, "2026-09": 0.6, "2026-10": 0.2} | 一致 | 欧元区走位 "2026-08至10月度增量 +0.3/+0.6/+0.2，均高于7月的 +0.1" |
| #783 | ⑩走位/转折叙述 | EA_HICP_YOY: 窗内(2025-11..2026-10)低点月 / 2026-01→05 逐月上行 / 03增量 vs 02增量 | ["2026-01", true, 0.7, 0.2] | ["2026-01", true, 0.7, 0.2] | 一致 | 欧元区走位 "低点1.7…(2026-03起加速)" / 转折表 "HICP 低点在 2026-01" |
| #784 | ⑩走位/转折叙述 | JP_POLICY_RATE 月均(受审稿逐个引用的月份) | {"2025-10": 0.477, "2025-11": 0.478, "2025-12": 0.557, "2026-01": 0.728, "2026-05": 0.727, "2026-06": 0.841, "2026-07": 0.978, "2026-08": 0.977, "2026-09": 1.043, "2026-10": 1.227} | {"2025-10": 0.477, "2025-11": 0.478, "2025-12": 0.557, "2026-01": 0.728, "2026-05": 0.727, "2026-06": 0.841, "2026-07": 0.978, "2026-08": 0.977, "2026-09": 1.043, "2026-10": 1.227} | 一致 | 日本走位/传导链2/政策一年窗路径(0.477/0.478/0.557/0.728/0.727/0.841/0.978/0.977/1.043/1.227) |
| #785 | ⑩走位/转折叙述 | JP_POLICY_RATE 窗内步进(四舍五入后 bp≠0 的月份) | [["2025-12", 8], ["2026-01", 17], ["2026-06", 11], ["2026-07", 14], ["2026-09", 7], ["2026-10", 18]] | [["2025-12", 8], ["2026-01", 17], ["2026-06", 11], ["2026-07", 14], ["2026-09", 7], ["2026-10", 18]] | 一致 | 传导链2 "月度步进 +8/+17/+11/+14/+7/+18 个基点，分别落在 2025-12、2026-01、2026-06、2026-07、2026-09、2026-10" |
| #786 | ⑩走位/转折叙述 | JP_POLICY_RATE 舍入级微变月份(\|Δ\|<1bp) | [["2026-04", -0.1], ["2026-08", -0.1]] | [["2026-04", -0.1], ["2026-08", -0.1]] | 一致 | 传导链2 "另有 2026-04 与 2026-08 各约零点一个基点的舍入变动" |
| #787 | ⑩走位/转折叙述 | JP_POLICY_RATE 净变动: 2025-11→2026-10 / 2025-12→2026-10 / 窗内是否存在 ≤-1bp 的步进 / 首个上调步进月 | [75, 67, false, "2025-12"] | [75, 67, false, "2025-12"] | 一致 | 日本走位/传导链2 "净 +75 个基点(自 2025-12 起 +67bp)…在美欧通胀同窗回升(2026-02起)之前已开始上调、窗内未回撤" |
| #788 | ⑩走位/转折叙述 | JGB: series_store 内序列数 / facts 内单点事实(指标@观测日) | [0, ["JGB10Y@2026-11-19", "JGB2Y@2026-11-19", "JGB5Y@2026-11-19"]] | [0, ["JGB10Y@2026-11-19", "JGB2Y@2026-11-19", "JGB5Y@2026-11-19"]] | 一致 | 传导链2 "JGB 收益率历史序列不在引擎(单点观测)" |
| #789 | ⑩走位/转折叙述 | JP_CPI_YOY(受审稿逐个引用的月份) | {"2025-01": 4.03, "2025-09": 2.91, "2025-10": 2.99, "2025-11": 2.9, "2025-12": 2.13, "2026-01": 1.51, "2026-02": 1.27, "2026-03": 1.46, "2026-04": 1.38, "2026-05": 1.53, "2026-07": 1.97, "2026-10": 2.44} | {"2025-01": 4.03, "2025-09": 2.91, "2025-10": 2.99, "2025-11": 2.9, "2025-12": 2.13, "2026-01": 1.51, "2026-02": 1.27, "2026-03": 1.46, "2026-04": 1.38, "2026-05": 1.53, "2026-07": 1.97, "2026-10": 2.44} | 一致 | 转折表 "月末路径 2025-11 2.9→2025-12 2.13→2026-01 1.51→2026-02 1.27…2026-03 1.46、2026-04 1.38…2026-07 1.97→2026-10 2.44" / "自 2025-01 高点 4.03" |
| #790 | ⑩走位/转折叙述 | JP_CPI_YOY 2025-01..2026-02 段内高点月/低点月; 2025-09、2025-10 是否环比回升; 2024-01..2026-10 最小值 | ["2025-01", "2026-02", true, 1.27] | ["2025-01", "2026-02", true, 1.27] | 一致 | 转折表 "自 2025-01 高点 4.03 至 2026-02 低点 1.27 总体下行，其间 2025-09、2025-10 小幅回升" |
| #791 | ⑩走位/转折叙述 | JP_CPI_TOKYO_YOY(受审稿逐个引用的月份) | {"2026-05": 1.3, "2026-06": 1.6, "2026-07": 1.85, "2026-08": 1.9, "2026-09": 2.69, "2026-10": 2.73} | {"2026-05": 1.3, "2026-06": 1.6, "2026-07": 1.85, "2026-08": 1.9, "2026-09": 2.69, "2026-10": 2.73} | 一致 | 日本走位/转折表 "东京CPI 1.85→2.73…2026-06→09 自1.6升至2.69…2026-08 的1.9" |
| #792 | ⑩走位/转折叙述 | JP_CPI_TOKYO_YOY 规则发布日: 2026-09 观测 / 2026-08 观测(及 2026-08-30 星期) | ["2026-09-29", "2026-08-30", 7] | ["2026-09-29", "2026-08-30", "星期日"] | 一致 | 转折表 "东京CPI 2026-09值推定首发于 2026-09-29…2026-08 的1.9，推定发布 2026-08-31 前后；规则值 2026-08-30 为星期日" |
| #793 | ⑩走位/转折叙述 | CN_PPI_YOY(受审稿逐个引用的月份) | {"2025-10": -2.1, "2025-11": -2.2, "2026-02": -0.9, "2026-05": 3.9, "2026-06": 4.1, "2026-07": 3.5, "2026-10": 5.7} | {"2025-10": -2.1, "2025-11": -2.2, "2026-02": -0.9, "2026-05": 3.9, "2026-06": 4.1, "2026-07": 3.5, "2026-10": 5.7} | 一致 | 中国走位/转折表 "-2.1→3.5→5.7…-0.9→3.9…2026-07 由 4.1 回落至 3.5" |
| #794 | ⑩走位/转折叙述 | 三序列窗内(2025-11..2026-10)低点月: CPI同比 / HICP / PPI; PPI 自低点后环比回落的月份 | ["2026-01", "2026-01", "2025-11", ["2026-07"]] | ["2026-01", "2026-01", "2025-11", ["2026-07"]] | 一致 | 转折表 "美国 CPI 同比与欧元区 HICP 低点均在 2026-01、中国 PPI 低点在 2025-11…其间仅 2026-07 由 4.1 回落至 3.5" |
| #795 | ⑩走位/转折叙述 | 三序列(CPI同比/HICP/PPI)自 2026-01 至 2026-05 是否逐月上行("2026-02 起同向上行") / 2026-03 同月环比增量 | [[true, true, true], [0.85, 0.7, 1.4]] | [[true, true, true], [0.85, 0.7, 1.4]] | 一致 | 转折表 "2026-02 起三序列同向上行、2026-03 同月大幅跳升" |
| #796 | ⑩走位/转折叙述 | CPI 同比窗内高点月 | 2026-05 | 2026-05 | 一致 | 多处 "2026-05 高点 4.17/4.1666" |
| #797 | ⑩走位/转折叙述 | CN_CPI_YOY 2026-02..2026-05 取值范围(同窗持平于一点零至一点三) | [1.0, 1.3] | [1.0, 1.3] | 一致 | C1/传导链1 "中国CPI同比同窗持平于一点零至一点三" |
| #798 | ⑩走位/转折叙述 | 转折候选面 CN_PMI_MFG 2026-02→2026-05 同比%(基期=去年同月) 及 Δ | [-2.3904, "2025-02", 1.0101, "2025-05", 3.4005] | [-2.3904, "2025-02", 1.0101, "2025-05", 3.4005] | 一致 | 转折表/候选面 "同比%口径 -2.3904→1.0101 (Δ 3.4005)" |
| #799 | ⑩走位/转折叙述 | 转折候选面 CN_CPI_YOY 2026-01→2026-04 及 Δ | [0.2, 1.2, 1.0] | [0.2, 1.2, 1.0] | 一致 | 候选面 "CN_CPI_YOY 2026-01..2026-04 0.2→1.2 (Δ 1.0)" |
| #800 | ⑩走位/转折叙述 | BRENT_F 2026-10-23→2026-11-23: 指数点差 / % | [-28.53, -24.44] | [-28.53, -24.44] | 一致 | 传导链1/对质表 "近30日116.72→88.19,-28.53 指数点(-24.44%)" |
| #801 | ⑩走位/转折叙述 | 四地价格摆动幅度对照(pp): 是否 PPI 最大 | {"PPI(3个月前→最新)": 2.2, "PPI(12个月前→最新)": 7.800000000000001, "CPI同比(12个月前→窗内高点)": 1.47, "HICP(12个月前→最新)": 1.9, "JP_CPI(12个月前→窗内低点→最新)": -1.63} | PPI 最大(12个月前→最新 7.8pp) | 一致 | 中国走位 "为四地最大价格摆动" |
| #802 | ⑩走位/转折叙述 | 四地消费价格同比最新有效读数: HICP 4.0 / CPI 3.72(2026-09) / CN 0.7 / JP全国 2.44 / 东京 2.73 | [4.0, 3.72, 0.7, 2.44, 2.73] | [4.0, 3.72, 0.7, 2.44, 2.73] | 一致 | 欧元区走位 "最新4.0为四地消费价格通胀的最高读数" |
| #803 | ⑩走位/转折叙述 | release_calendar.entries: ECB_DFR/ECB_MRO 实录条目数 / 截止日后才发布的 Fed·ECB 决议条目数 / 日历版本 | [0, 0, "1.5.0"] | [0, 0, "v1.5.0"] | 一致 | 欧元区走位/传导链1 "冻结发布日历无欧央行实录条目" / 情景表 "冻结发布日历暂无两家实录条目" |
| #927 | ⑩走位/转折叙述 | report.json research_plan.turning_candidates.candidates: 增长维按\|delta\|排序 / 全体首位 / 美欧最大 | {"growth_rank": [["CN_PMI_MFG", 3.4005], ["INDPRO", -0.9571]], "top_all": ["CN_PPI_YOY", 4.8], "top_US_EA": ["CPI", 1.7326]} | {"growth_rank1": ["CN_PMI_MFG", 3.4], "top_all": ["CN_PPI_YOY", 4.8], "top_US_EA": ["CPI", 1.7326]} | 一致 | agent_judgment.reader_map.turnings[1].first_mover / turnings[0].first_mover |
| #928 | ⑩走位/转折叙述 | series_store EA_REAL_GDP_YOY / JP_REAL_GDP_YOY @2025-07/2026-04/2026-07; UNEMPLOYMENT 2025-09→2026-10; INDPRO 同比 2025-08/2026-07/2026-10 | {"EA": [1.11, 1.19, 1.28], "JP": [0.63, 0.8, 1.16], "UNEMP": [4.4, 4.1], "INDPRO_yoy": [1.19, 1.25, 2.15]} | {"EA": [1.11, 1.19, 1.28], "JP": [0.63, 0.8, 1.16], "UNEMP": [4.4, 4.1], "INDPRO_yoy": [1.19, 1.25, 2.15]} | 一致 | agent_judgment.reader_map.turnings[1].follow_or_diverge / regions[US\|EA\|JP].from_to |

### 2.17 ②/⑬FULL_REPORT-L1事实表(记录 48 / 一致 48 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #804 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[SPX@2026-11-23](value/observation_date/quality_status) | [7203.85, "2026-11-23", "PASS"] | [7203.85, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行11 |
| #805 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[NDX@2026-11-23](value/observation_date/quality_status) | [26672.85, "2026-11-23", "PASS"] | [26672.85, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行12 |
| #806 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[RUT@2026-11-20](value/observation_date/quality_status) | [2581.79, "2026-11-20", "PASS"] | [2581.79, "2026-11-20", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行13 |
| #807 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[DXY@2026-11-23](value/observation_date/quality_status) | [104.08, "2026-11-23", "PASS"] | [104.08, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行14 |
| #808 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[EURUSD@2026-11-23](value/observation_date/quality_status) | [1.09, "2026-11-23", "PASS"] | [1.09, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行15 |
| #809 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[GOLD_F@2026-11-23](value/observation_date/quality_status) | [3685.2, "2026-11-23", "PASS"] | [3685.2, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行16 |
| #810 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[SILVER_F@2026-11-23](value/observation_date/quality_status) | [43.88, "2026-11-23", "PASS"] | [43.88, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行17 |
| #811 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[BRENT_F@2026-11-23](value/observation_date/quality_status) | [88.19, "2026-11-23", "PASS"] | [88.19, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行18 |
| #812 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[VIX@2026-11-23](value/observation_date/quality_status) | [27.01, "2026-11-23", "PASS"] | [27.01, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行19 |
| #813 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[DAX@2026-11-23](value/observation_date/quality_status) | [25209.45, "2026-11-23", "PASS"] | [25209.45, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行20 |
| #814 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[CAC40@2026-11-23](value/observation_date/quality_status) | [8022.62, "2026-11-23", "PASS"] | [8022.62, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行21 |
| #815 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[USDJPY@2026-11-23](value/observation_date/quality_status) | [159.35, "2026-11-23", "PASS"] | [159.35, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行22 |
| #816 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[USDCNY@2026-11-23](value/observation_date/quality_status) | [6.65, "2026-11-23", "PASS"] | [6.65, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行23 |
| #817 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[HY_OAS@2026-11-19](value/observation_date/quality_status) | [3.52, "2026-11-19", "PASS"] | [3.52, "2026-11-19", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行24 |
| #818 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[BB_OAS@2026-11-19](value/observation_date/quality_status) | [2.1, "2026-11-19", "PASS"] | [2.1, "2026-11-19", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行25 |
| #819 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[B_OAS@2026-11-19](value/observation_date/quality_status) | [3.8, "2026-11-19", "PASS"] | [3.8, "2026-11-19", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行26 |
| #820 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[CCC_OAS@2026-11-19](value/observation_date/quality_status) | [13.61, "2026-11-19", "PASS"] | [13.61, "2026-11-19", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行27 |
| #821 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[IG_OAS@2026-11-19](value/observation_date/quality_status) | [0.94, "2026-11-19", "PASS"] | [0.94, "2026-11-19", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行28 |
| #822 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[UST_2Y@2026-11-19](value/observation_date/quality_status) | [4.76, "2026-11-19", "PASS"] | [4.76, "2026-11-19", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行29 |
| #823 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[UST_10Y@2026-11-19](value/observation_date/quality_status) | [5.04, "2026-11-19", "PASS"] | [5.04, "2026-11-19", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行30 |
| #824 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[UST_30Y@2026-11-19](value/observation_date/quality_status) | [5.4, "2026-11-19", "PASS"] | [5.4, "2026-11-19", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行31 |
| #825 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[TIPS_5Y@2026-11-19](value/observation_date/quality_status) | [2.64, "2026-11-19", "PASS"] | [2.64, "2026-11-19", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行32 |
| #826 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[TIPS_10Y@2026-11-19](value/observation_date/quality_status) | [2.88, "2026-11-19", "PASS"] | [2.88, "2026-11-19", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行33 |
| #827 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[BEI_5Y@2026-11-20](value/observation_date/quality_status) | [2.18, "2026-11-20", "PASS"] | [2.18, "2026-11-20", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行34 |
| #828 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[BEI_10Y@2026-11-20](value/observation_date/quality_status) | [2.15, "2026-11-20", "PASS"] | [2.15, "2026-11-20", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行35 |
| #829 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[CURVE_2S10S@2026-11-20](value/observation_date/quality_status) | [0.29, "2026-11-20", "PASS"] | [0.29, "2026-11-20", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行36 |
| #830 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[CPI@2026-10-01](value/observation_date/quality_status) | [337.476, "2026-10-01", "WARN"] | [337.476, "2026-10-01", "WARN"] | 一致 | FULL_REPORT.md L1 事实层 行37 |
| #831 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[CORE_PCE@2026-09-01](value/observation_date/quality_status) | [130.902, "2026-09-01", "DEGRADED"] | [130.902, "2026-09-01", "DEGRADED"] | 一致 | FULL_REPORT.md L1 事实层 行38 |
| #832 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[UNEMPLOYMENT@2026-10-01](value/observation_date/quality_status) | [4.1, "2026-10-01", "WARN"] | [4.1, "2026-10-01", "WARN"] | 一致 | FULL_REPORT.md L1 事实层 行39 |
| #833 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[CORE_CPI@2026-10-01](value/observation_date/quality_status) | [339.9, "2026-10-01", "WARN"] | [339.9, "2026-10-01", "WARN"] | 一致 | FULL_REPORT.md L1 事实层 行40 |
| #834 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[UST_5Y@2026-11-19](value/observation_date/quality_status) | [4.86, "2026-11-19", "PASS"] | [4.86, "2026-11-19", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行41 |
| #835 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[INDPRO@2026-10-01](value/observation_date/quality_status) | [103.3954, "2026-10-01", "WARN"] | [103.3954, "2026-10-01", "WARN"] | 一致 | FULL_REPORT.md L1 事实层 行42 |
| #836 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[US_REAL_GDP@2026-07-01](value/observation_date/quality_status) | [24611.077, "2026-07-01", "DEGRADED"] | [24611.077, "2026-07-01", "DEGRADED"] | 一致 | FULL_REPORT.md L1 事实层 行43 |
| #837 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[SHCOMP@2026-11-23](value/observation_date/quality_status) | [3538.948, "2026-11-23", "PASS"] | [3538.948, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行44 |
| #838 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[HSI@2026-11-23](value/observation_date/quality_status) | [22383.74, "2026-11-23", "PASS"] | [22383.74, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行45 |
| #839 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[CN_LPR_1Y@2026-11-20](value/observation_date/quality_status) | [3.0, "2026-11-20", "WARN"] | [3.0, "2026-11-20", "WARN"] | 一致 | FULL_REPORT.md L1 事实层 行46 |
| #840 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[CN_CPI_YOY@2026-10-31](value/observation_date/quality_status) | [0.7, "2026-10-31", "WARN"] | [0.7, "2026-10-31", "WARN"] | 一致 | FULL_REPORT.md L1 事实层 行47 |
| #841 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[CN_PPI_YOY@2026-10-31](value/observation_date/quality_status) | [5.7, "2026-10-31", "WARN"] | [5.7, "2026-10-31", "WARN"] | 一致 | FULL_REPORT.md L1 事实层 行48 |
| #842 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[CN_PMI_MFG@2026-10-01](value/observation_date/quality_status) | [49.3, "2026-10-01", "WARN"] | [49.3, "2026-10-01", "WARN"] | 一致 | FULL_REPORT.md L1 事实层 行49 |
| #843 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[DFF@2026-11-19](value/observation_date/quality_status) | [3.88, "2026-11-19", "PASS"] | [3.88, "2026-11-19", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行50 |
| #844 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[DFEDTARU@2026-11-23](value/observation_date/quality_status) | [4.0, "2026-11-23", "PASS"] | [4.0, "2026-11-23", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行51 |
| #845 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[NIKKEI225@2026-11-20](value/observation_date/quality_status) | [56436.65, "2026-11-20", "PASS"] | [56436.65, "2026-11-20", "PASS"] | 一致 | FULL_REPORT.md L1 事实层 行52 |
| #846 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[JP_CPI_YOY@2026-10-01](value/observation_date/quality_status) | [2.44, "2026-10-01", "WARN"] | [2.44, "2026-10-01", "WARN"] | 一致 | FULL_REPORT.md L1 事实层 行53 |
| #847 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[ECB_DFR@2026-09-16](value/observation_date/quality_status) | [2.5, "2026-09-16", "DEGRADED"] | [2.5, "2026-09-16", "DEGRADED"] | 一致 | FULL_REPORT.md L1 事实层 行54 |
| #848 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[ECB_MRO@2026-09-16](value/observation_date/quality_status) | [2.65, "2026-09-16", "DEGRADED"] | [2.65, "2026-09-16", "DEGRADED"] | 一致 | FULL_REPORT.md L1 事实层 行55 |
| #849 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[EA_HICP_YOY@2026-10-01](value/observation_date/quality_status) | [4.0, "2026-10-01", "WARN"] | [4.0, "2026-10-01", "WARN"] | 一致 | FULL_REPORT.md L1 事实层 行56 |
| #850 | ②/⑬FULL_REPORT-L1事实表 | snapshot.facts[JP_POLICY_RATE@2026-10-01](value/observation_date/quality_status) | [1.227, "2026-10-01", "WARN"] | [1.227, "2026-10-01", "WARN"] | 一致 | FULL_REPORT.md L1 事实层 行57 |
| #851 | ②/⑬FULL_REPORT-L1事实表 | FULL_REPORT L1 事实表行数(行11-57) | 47 | 47 | 一致 | FULL_REPORT.md L1 事实层 |

### 2.18 ⑦日度相关(记录 1 / 一致 1 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #854 | ⑦日度相关 | series_store.US_REAL_GDP(环比%)×UNEMPLOYMENT(差分) 在共同观测日上的 pearson(共同窗 2017-01..2026-07) | [-0.8936, 37, "2017-01", "2026-07"] | [-0.8936, 37, "2017-01", "2026-07"] | 一致 | FULL_REPORT.md 日度相关(引擎确定性面·读者版) |

### 2.19 ⑩报告间文本一致(记录 9 / 一致 8 / NA 1)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #855 | ⑩报告间文本一致 | agent_judgment.l3 正文类字符串字段(不含 title 标签)在 FULL_REPORT.md 中逐字出现: 字段数/未出现数 | [59, 0] | [59, 0] | 一致 | FULL_REPORT.md 内联的 l3 文本 |
| #856 | ⑩报告间文本一致 | agent_judgment.l4 正文类字符串字段(不含 title 标签)在 FULL_REPORT.md 中逐字出现: 字段数/未出现数 | [17, 0] | [17, 0] | 一致 | FULL_REPORT.md 内联的 l4 文本 |
| #857 | ⑩报告间文本一致 | agent_judgment.l3 正文类字符串字段(不含 title 标签)在 report.md 中逐字出现: 字段数/未出现数 | [59, 0] | [59, 0] | 一致 | report.md 内联的 l3 文本 |
| #858 | ⑩报告间文本一致 | agent_judgment.l4 正文类字符串字段(不含 title 标签)在 report.md 中逐字出现: 字段数/未出现数 | [17, 0] | [17, 0] | 一致 | report.md 内联的 l4 文本 |
| #859 | ⑩报告间文本一致 | agent_judgment.reader_map 正文类字符串字段(不含 title 标签)在 MAP_REPORT.md 中逐字出现: 字段数/未出现数 | [75, 0] | [75, 0] | 一致 | MAP_REPORT.md 内联的 reader_map 文本 |
| #860 | ⑩报告间文本一致 | agent_judgment.quality_gate_notes 六条注记在三份报告中逐字渲染条数(观察项, 非数值比对) | 0 | 非比对项 | NA(登记) | MAP_REPORT.md / FULL_REPORT.md / report.md(注记仅存于 agent_judgment.json) |
| #861 | ⑩报告间文本一致 | agent_judgment 的 title 标签字段: 总数 / 逐字出现在任一报告的数量 | [5, 0] | [5, 0] | 一致 | 标签字段(非正文); 未渲染者=['l3.mechanism_chains[0].title', 'l3.mechanism_chains[1].title', 'reader_map.transmission[0].title', 'reader_map.transmission[0].links[2].title'… |
| #862 | ⑩报告间文本一致 | agent_declaration.basis "证据索引(72行)": evidence_index.json 行数 / 工单 evidence_index_rows | [72, 72] | [72, 72] | 一致 | agent_judgment.agent_declaration.basis |
| #863 | ⑩报告间文本一致 | agent_declaration.basis "点值格(22格)": MAP 三时点表数据行数 / 工单 point_values_cells | [22, 22] | [22, 22] | 一致 | 同上 |

### 2.20 ⑪诚实缺席/GateA(记录 5 / 一致 5 / NA 0)

| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |
|---|---|---|---|---|---|---|
| #865 | ⑪诚实缺席/GateA | quality_gate_notes "非核心缺口 七 项(…)": 项数与清单 ↔ snapshot.gate_a.noncore_missing | [7, ["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"]] | [7, ["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"]] | 一致 | agent_judgment.quality_gate_notes(数据面) / MAP_REPORT 数据门行 |
| #866 | ⑪诚实缺席/GateA | quality_gate_notes "非核心降级 八 项(…)": 项数与清单 ↔ snapshot.gate_a.noncore_degraded | [8, ["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"]] | [8, ["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"]] | 一致 | 同上 |
| #867 | ⑪诚实缺席/GateA | quality_gate_notes "核心缺口 零 项" ↔ snapshot.gate_a.core_missing; gate_a.status | [0, "DEGRADED"] | [0, "DEGRADED"] | 一致 | 同上 |
| #868 | ⑪诚实缺席/GateA | quality_gate_notes "缺口指标中 五 项在序列库内有存量观测(…)": 清单 ↔ gate_a.noncore_missing ∩ series_store | [["CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"], 5] | [["CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"], 5] | 一致 | 同上(存量观测引用的过期/降级披露) |
| #869 | ⑪诚实缺席/GateA | MAP_REPORT 数据门行 非核心缺席/非核心降级 清单 ↔ snapshot.gate_a | [["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"], ["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"]] | [["BUND_10Y", "BUND_2Y", "CN_OMO_7D", "CN_POLICY_OVERNIGHT", "EA_REAL_GDP_YOY", "JP_CPI_TOKYO_YOY", "JP_REAL_GDP_YOY"], ["CN_SF_FLOW", "ECB_DFR", "ECB_MRO", "JTSJOL", "M2SL", "SPX_EPS", "SPX_PE_TTM", "US_REAL_GDP"]] | 一致 | MAP_REPORT.md 数据门(Gate A)行 |

## 3 登记项(NA, 不计入比对点; 共 8 条)

- #358 [①③同比路径(月频)] 出处键: CPI 同比 2026-02→2026-03 增量(受审稿无数字, 仅直算登记); 直算: 0.85; 受审稿: 同月大幅跳升(无数字); 说明: ; 位置: turnings[0] "2026-03 同月大幅跳升"
- #521 [杂项(引用/日历/结构)] 出处键: series_store.DFF 变动点实际值 2025-12-10→2025-12-11→2026-09-17; 直算: [3.89, 3.64, 3.88]; 受审稿: 受审稿括注 3.88→3.63→3.88; 说明: [rc09] 变动点实际值 3.89→3.64→3.88; 受审稿括注与三时点锚值一致、与变动点值相差 1bp(EFFR 日度波动); 位置: TR1.step2 口径注记(MINOR 候选)
- #670 [⑧历史类比面] 出处键: 同格严格符号口径(0 不计入任一侧) UST_10Y_1m; 直算: 0.6; 受审稿: 0.8; 说明: [rc09] 恰为0的事后块在严格口径下不计入一致侧; 受审稿 "其余各窗零点六至零点八" 在两种口径下均成立; 位置: report.json dispersion.topN_aftermath_sign_agreement
- #860 [⑩报告间文本一致] 出处键: agent_judgment.quality_gate_notes 六条注记在三份报告中逐字渲染条数(观察项, 非数值比对); 直算: 0; 受审稿: 非比对项; 说明: [rc10] ; 位置: MAP_REPORT.md / FULL_REPORT.md / report.md(注记仅存于 agent_judgment.json)
- #875 [⑧历史事后窗] 出处键: 同注记对 TOP-5 第4/5名(2021-02/2020-01, 受审稿无逐窗月末叙述)的口径差: \|月末口径−引擎事后块口径\|; 直算: {"n_cells": 24, "max_pp": 2.7576, "max_cell": ["2021-02", "SPX", "6m"], "median": 0.3845}; 受审稿: 受审稿未引用该两段的月末口径数值; 说明: [rc13] 登记项: 第4/5名仅进入符号一致率与簇数, 不进入逐窗叙述; 两口径在该两段差值最大 2.7576pp; 位置: report.json steps[S6_analog].top[3..4].aftermath
- #881 [④政策面] 出处键: EA_HICP_YOY 决议时点最近可见观测——引擎历史面两级发布规则口径(快报=观测月末当日可见,推定); 直算: ["2026-05", 3.2, "2026-05-31", "rule:推定(快报月末)"]; 受审稿: ["2026-04", 3.0, "2026-05-16", "rule(月末+16)"]; 说明: [rc12] 口径分歧登记(非数值比对): 两级规则下决议 2026-06-11 前最近可见为 2026-05 观测 3.2(快报推定 2026-05-31), 与受审稿(注册表口径 2026-04 观测 3.0)不同; 该值处上行段(与受审稿对首次决议「处上行段」的方向判断一致, 仅观测月/数值不同)。序列值为最新修订值,当时快报值不可回溯。; 位置: M1.step2 / TR1.step2 决议 2026-06-11(两级规则对照)
- #883 [④政策面] 出处键: EA_HICP_YOY 决议时点最近可见观测——引擎历史面两级发布规则口径(快报=观测月末当日可见,推定); 直算: ["2026-08", 3.2, "2026-08-31", "rule:推定(快报月末)"]; 受审稿: ["2026-07", 2.9, "2026-08-16", "rule(月末+16)"]; 说明: [rc12] 口径分歧登记(非数值比对): 两级规则下决议 2026-09-10 前最近可见为 2026-08 观测 3.2(快报推定 2026-08-31), 与受审稿(注册表口径 2026-07 观测 2.9)不同; 该值持平 2026-05 高点 3.2——受审稿「低于 2026-05 高点」的欧央行一腿在此口径下不成立。序列值为最新修订值,当时快报值不可回溯。; 位置: M1.step2 / TR1.step2 决议 2026-09-10(两级规则对照)
- #917 [⑨情景阈值/期限] 出处键: SCN1 前提/触发/证伪阈值(CPI>3 / ≥3.5 / <2.5 且 CORE_PCE<2.8)与 SCN2 证伪阈值(BEI_10Y<1.8): 席位自设参数, 无数据真值; 与截止日读数的相容性见 #552/#553; 直算: {"CPI_2026-09": 3.72, "CORE_PCE_2026-09": 3.12, "BEI_10Y_2026-11-20": 2.15}; 受审稿: [3, 3.5, 2.5, 2.8, 1.8]; 说明: [rc15] 登记项(参数性数字, 非数据读数): 各阈值在截止日读数(CPI 3.72 / CORE_PCE 3.12 / BEI_10Y 2.15)与高点(CPI 4.17 / CORE_PCE 3.16)之间的位置合理, 可观测; 不计入比对点; 位置: agent_judgment.l4.scenarios[SCN1\|SCN2].rows

## 4 规程第 3 节覆盖面 ①–⑮ 逐项结论

(规程第 3 节末项在原文中重复编号为⑬, 本文件按顺序记为⑮。)最低要求 120 点, 实际比对 925 点。

- **①** 截止日: 受审稿自称研究截止日 2026-11-23 与快照 research_as_of(2026-11-23T22:53:47+08:00)/target_date(20261123)一致; 受审稿所引观测日、规则发布日、决议日、生效日均不晚于截止日; 冻结日历内无「决议日≤截止日而生效日>截止日」的待生效决定(0 条); 历史类比的事后段均以「事后」身份标注、未被写成预测; 时点标注(盘中快照/收盘/末观测日/时区)与快照时间戳相容。台账 『①③同比路径(月频)』83 条(#347–#353、#356–#360、#363–#374、#376–#387、#389–#399 等)、#529–#533。
- **②** 点值锚格: 工单四地×维度×三锚(12 个月前 / 3 个月前 / 最新)中被引用的格逐格自 series_store 直算(值 / 观测日 / 同比 / 缺席理由)并与 report.json 引擎点值格比对, 全部一致; 缺席格如实标缺席。台账 『②/⑬点值格/②/⑬FULL_REPORT-L1事实表』191 条(#0–#128、#804–#851、#885–#895、#901–#903)。
- **③** 同比: 凡称「同比」的月频数值均以去年同月为基期自水平序列直算(季度以同季为基期); 2026-10 美国 CPI 同比因 2025-10 基期缺席不可得, 受审稿如实标「缺基期不可得」而未以相邻月份替代; 「最近有效同比」的月份与数值一致。台账 『①③同比路径(月频)』83 条(#347–#353、#356–#360、#363–#374、#376–#387、#389–#399 等)、#354–#357。
- **④** 政策面: 决议日 / 生效日 / 步长 / 目标值逐项与冻结日历条目和序列变更日核对; 官方目标(冻结日历所载日本央行目标水平)、政策利率序列(DFF、ECB_DFR、CN_LPR_1Y)与月均值(JP_POLICY_RATE 无担保隔夜拆借月均)各口径分列、未互相冒充; 无待生效决定; 中国换锚(7 天逆回购→隔夜逆回购)分列。台账 『④政策面』58 条(#439–#453、#455–#467、#480–#491、#877、#880–#883、#896–#897、#904–#905、#918–#926)、#919、#920–#922。
- **⑤** 三利率分解与资产月窗: 12 个月窗名义 +91 = 实际 +102 + 盈亏平衡 -11 个基点, 恒等残差 0; 近 1 个月 -8 = +11 - 19; 窗口端点日期(2025-11-19 / 2026-11-19 共同交易日; 2026-10-23 至 2026-11-19、11-20、11-23)与端点值逐一直算; 资产月窗(同日收盘口径与近 1 个月口径)逐项一致。台账 #508–#515、#332–#344、#898。
- **⑥** 转折判断与候选面: 三个转折(CPI@2026-05、INDPRO@2026-02、JP_CPI_YOY@2026-02)的前值→后值 / 窗口 / 谁先变与引擎转折候选面及排序一致; 「先后」主张均有时间分辨率支撑(美联储 2026-09-16 决议、欧央行回推 2026-09-10【推断】、日本央行 2026-09-18 决议; 通胀转折月至 2026-05)。台账 『⑥转折路径』12 条(#354–#355、#375、#388、#400–#401、#418、#430–#432、#929–#930)、#927、#928。
- **⑦** 传导链各环: 两条机制链 4+2 环的 evidence_level 标注(E1/E2/E3)与该环实际证据相称; E2/E3 环均含字面「假设」、未以事实位措辞出现; 环内数字可回贴引擎面; 读者面传导链 3+1 环以【假设】【竞争解释】字面区分事实与假设。台账 『⑦传导环数字/⑦日度相关』32 条(#326–#331、#345–#346、#498–#507、#516–#520、#522–#528、#546、#854)。
- **⑧** 历史类比: 三段(2025-03、2022-06、2023-10)的距离 / 分位 / 维度构成、当时可知面与事后段的划分、随后 3 / 6 / 12 个月事后结果数字逐窗自冻结序列直算; 事后结果均以「事后」措辞呈现, 未被表述成预测; 同步面逐格一致。台账 『⑧同步面/当时可知/⑧历史事后窗/⑧历史类比面/⑧历史事后窗(细表)』431 条(#129–#325、#496–#497、#556–#769、#852–#853、#864、#870–#875、#908–#916)、#686–#687、#581–#583。
- **⑨** 情景: 两情景互为对照、方向互补; 触发条件 / 证伪阈值均为数字且指标在场; 与截止日读数相容(CPI 3.72、CORE_PCE 3.12、BEI_10Y 2.15 均在未证伪一侧), 无已触发或已被证伪而仍列为待验证的前提; 期限 2027-02-28。台账 『⑨情景阈值/期限』10 条(#547–#555、#917)。
- **⑩** 总判断 / 走位 / 对质表: 首页结论、四地走位、对质表四行的方向词 / 单位 / 精度 / 关系词与数值一致; 对质表四行裁定(支持主解释、尚不能区分、尚不能区分、支持竞争解释)与该行观测一致(见 5.6)。台账 『⑩走位/转折叙述/⑩报告间文本一致』45 条(#770–#803、#855–#863、#927–#928)、#544。
- **⑪** 诚实缺席项: 受审稿声明的每个缺口(序列缺席 / 缺基期 / 过期 / 降级)经序列级证实属实, 无以相邻口径冒充; Gate A=DEGRADED(核心缺口 0、非核心缺口 7、非核心降级 8)与快照 gate_a 一致, MAP 数据门行逐项一致。台账 『⑪诚实缺席/⑪诚实缺席/GateA』10 条(#438、#454、#492–#493、#495、#865–#869)、#490–#495。
- **⑫** 截止日当日标注的日频观测: 2026-11-23 的 SPX、USDJPY、GOLD_F、DXY、VIX 标为盘中快照, SHCOMP 标为当日收盘, 与快照 research_as_of(2026-11-23T22:53:47+08:00)相容; NIKKEI225 止于 2026-11-20 属实。台账 『⑫时点标注』6 条(#529–#533、#876)。
- **⑬** 契约验证结果: report.json agent_judgment.contract_verification verdict=VERIFIED; 逐项 verdicts 15 项, six_checks 16 项、map_checks 7 项全部通过, unresolved_unbound 0 项 → 无非 VERIFIED 项(含 STALE), 无需判断档另作披露。
- **⑭** 交付门相关缺口: 判断档对 Gate A 非核心缺口 7 项 / 非核心降级 8 项的披露与快照 gate_a 逐项一致; 其中 5 项在序列库内有存量观测, 受审稿所列与序列面一致; 无把缺席写成「无变化」(见 MINOR-3 的序列级核实), 无把序列值写成官方宣布目标(中国两工具与日本月均拆借利率均标口径); 缺官方记录处(美联储 / 欧央行决议)以【推断】标注。缺口披露未入读者报告记 MINOR-3。台账 #865–#869。
- **⑮** 地图问句三时点对照与工单四问: MAP 三时点对照表(22 行)各格(值 / 观测日 / 状态)与引擎点值格(22 格)逐格直算一致, FULL_REPORT L1 事实表 48 项一致; 工单四问——三个转折(turnings 3 条)、谁先变 / 跟进或背离(转折候选面与政策面)、证据最充分的传导机制 / 其他解释 / 区分指标(mechanism_chains 2 条, 每环并列竞争解释与证伪指标)、历史上结构最像的时期 / 当时其他经济体是否同步 / 随后 3、6、12 个月实际走势(history_periods 3 条)——各有对应内容且与工单相称。台账 『②/⑬点值格/②/⑬FULL_REPORT-L1事实表』191 条(#0–#128、#804–#851、#885–#895、#901–#903)、『⑩走位/转折叙述/⑩报告间文本一致』45 条(#770–#803、#855–#863、#927–#928)、#863。

Gate A 缺口 / 降级指标与判断档引用情况(序列级; 「提及」= 判断档 l3/l4/reader_map 正文出现该指标代码或别名):

| 指标 | Gate A 类别 | 序列库观测数 | 末观测日 | 判断档正文提及 |
|---|---|---|---|---|
| BUND_10Y | 非核心缺口 | 0 | — | — |
| BUND_2Y | 非核心缺口 | 0 | — | — |
| CN_OMO_7D | 非核心缺口 | 201 | 2026-10-30 | CN_OMO_7D、7天逆回购 |
| CN_POLICY_OVERNIGHT | 非核心缺口 | 16 | 2026-11-23 | CN_POLICY_OVERNIGHT、隔夜逆回购、隔夜利率 |
| EA_REAL_GDP_YOY | 非核心缺口 | 123 | 2026-07-01 | EA_REAL_GDP_YOY、欧元区GDP同比 |
| JP_CPI_TOKYO_YOY | 非核心缺口 | 10 | 2026-10-01 | JP_CPI_TOKYO_YOY、东京CPI |
| JP_REAL_GDP_YOY | 非核心缺口 | 127 | 2026-07-01 | JP_REAL_GDP_YOY、日本GDP同比 |
| CN_SF_FLOW | 非核心降级 | 0 | — | — |
| ECB_DFR | 非核心降级 | 69 | 2026-09-16 | ECB_DFR、DFR、存款便利利率 |
| ECB_MRO | 非核心降级 | 48 | 2026-09-16 | ECB_MRO、MRO、主要再融资 |
| JTSJOL | 非核心降级 | 119 | 2026-09-01 | — |
| M2SL | 非核心降级 | 119 | 2026-09-01 | — |
| SPX_EPS | 非核心降级 | 1869 | 2026-09-01 | — |
| SPX_PE_TTM | 非核心降级 | 1869 | 2026-09-01 | — |
| US_REAL_GDP | 非核心降级 | 40 | 2026-07-01 | US_REAL_GDP |


## 5 规程第 4 节: 六查 + 证伪(逐条矛盾陈述、逐条机制链)
六查项: ① 证据相关性 ② 支持度 ③ 竞争解释(须为同证据可容纳、且在点名区分指标上预言方向不同的真正竞争, 非稻草人) ④ 反对证据(有无未披露的反向事实) ⑤ 结论是否超出证据 ⑥ 证伪条件可观测性(被点名的区分指标须在证据面在场, 两解释在其上的预言方向须确实不同)。每条至少一次反方攻击, 攻击记录见 5.8(与 VERDICT JSON 的 counterexamples_sought 逐条对应)。
### 5.1 矛盾陈述 C1(主线综合 / 增长担忧 / 跨境溢出·技术面)
**受审主张(摘要)**: 主线综合: 过去12个月(至2026-11-23)四地证据面呈现『通胀再加速→政策再收紧→实际利率上行→风险资产收缩』的同向共动(其中资产收缩一腿属于近月窗口的事实，全年窗口内股指并未下行，窗口对照披露见机制链资产环)——CPI 与 CORE_PCE 同比较一年前走高(2026-05 见顶后回落、未再越过高点)、EA_HICP_YOY 升至本轮最高、CN_PPI_YOY 自负转正并续创本轮新高、CN_PMI_MFG 于 2025-12 及 2026-03、2026-04、2026-06、2026-09 共五个月站上荣枯线、其余月份不高于荣枯线(2026-05 持平于五十，余在四十九点零至四十九点八之间)、DFF 回到 2025-12 降息前的台阶附近(…(下略)
**竞争解释(受审稿原文摘要)**: 解释A(主链): 通胀再加速(2026-02至2026-05美欧消费价格与中国生产价格同窗共振)迫使央行再收紧,名义利率上行由实际利率主导(12个月实际+102bp),高实际利率压制风险资产估值并推升 DXY、压低 GOLD_F——若成立,BEI_10Y 应大体稳定而 TIPS_10Y 续升 | 解释B(增长担忧): 风险资产收缩主要由增长预期下修驱动(美国工业同比一度折半、GDP 同比放缓),利率变化是结果而非原因——若成立,BEI_10Y 应主导性下行(衰退定价)而 TIPS_10Y 转平或回落;近1个月分解(实际+11bp、盈亏平衡-19bp)与该解释的盈亏平衡一腿相容、与实际利率一腿相左, 整体仅部分相容 | 解释C(跨边境溢出/技术面): JP_POLICY_RATE 全年步进式正常化经由套息与久期渠道放大全球资产波动,或仓位/流动性技术因素主导近月收缩——若成立,USDJPY 与风险资产的波动应在时间上更紧地耦合,且 HY_OAS 应保持平稳(非信用事件)；同窗核验(见传导面竞争链): 该解释的套息平仓一腿未获区分指标面支持，技术面一腿不可
**① 证据相关性**: 17 条 evidence_refs 与『证据面最新水平』清单 11 项逐一核对, 取值、观测日、引用标签日期、规则发布日均取自冻结快照且不晚于截止日 2026-11-23; 其中 CN_PPI_YOY、CN_CPI_YOY 的引用标签为月末日期而观测日为月初(同月), 受审稿质量注记已披露。台账 #885–#895、#932。
**② 支持度**: 事实面逐环成立——通胀端 CPI 同比 2026-02→2026-05 2.434→4.1666、EA_HICP_YOY 1.9→3.2、CN_PPI_YOY -0.9→3.9, 2026-05 后回落未再越过高点(#927、#354–#357、#900); 政策端 ECB_DFR 两度各 +25 个基点、JP_POLICY_RATE 一年窗净 +75 个基点、DFF 一降一升净变 0(#896、#897、#920–#922、#918); 利率端 12 个月窗名义 +91 = 实际 +102 + 盈亏平衡 -11 个基点、残差 0(#508–#515); 资产端近 1 个月 SPX、NIKKEI225、GOLD_F 收缩而 DXY、VIX 走高(#899、#332–#344)。资产收缩一腿只在近窗成立: 12 个月窗 SPX +8.03%、NIKKEI225 +22.47%、DAX +9.93% 与实际利率同向上行(#326–#328、#329–#330)——受审稿在 C1 括注(资产收缩一腿属于近月窗口的事实、全年窗口内股指并未下行)与机制链资产环明示。
**③ 竞争解释**: 主链、增长担忧、跨境溢出·技术面三解在同一证据下均可容纳, 且在点名的区分指标(BEI_10Y、TIPS_10Y、HY_OAS、USDJPY)上预言方向不同 → 真正竞争, 非稻草人。
**④ 反对证据**: 对主链——近 1 个月 BEI_10Y -19 个基点而名义 -8、实际 +11 个基点, 与主链『盈亏平衡大体稳定』一腿相左, 受审稿已写入并据此只给『部分相容』(#508–#515); 对跨境溢出·技术面——同窗 USDJPY 156.49→159.35(+1.82%)与 SPX -5.51% 并存, 套息平仓一腿未获支持, 受审稿已写入(#345–#346)。未发现未披露的反向事实。
**⑤ 结论是否超出证据**: 裁定『不足以裁决』并把共动与因果分开, 未超出。
**⑥ 证伪条件可观测性**: 四项区分指标均在本轮证据面在场, 最新观测日不早于 2026-11-19(#544); 两解释在其上的预言方向相反(见 5.6)。
**反方攻击**: 5.8 第 1–3 条。**小结**: 无 MAJOR; NIT-10。
### 5.2 矛盾陈述 C2(历史相似段的事后路径分歧 / 相似度低维覆盖)
**受审主张(摘要)**: 历史相似段的证据冲突: 三个最相似候选(2025-03、2022-06、2023-10)的事后路径分歧明显——2022-06段股指三个月窗普遍收缩(DAX、SHCOMP、SPX、NIKKEI225 均为负)而十二个月窗除 SHCOMP 外转正;2025-03、2023-10段风险资产与 GOLD_F 多数窗走强(2023-10段上证指数三个月窗为负，属例外)而 DXY 走弱;TOP-N事后符号一致率: GOLD_F 与 SPX 六个月与十二个月窗符号一致(一致率面仅含 DXY、GOLD_F、SPX、UST_10Y 四类)，其余各窗零点六至零点八。据此『当前状态可外推某一段事后路径』的主张不成立: 历史段只作结构对照与情景校准,不作预测(相似≠因果≠预测,分歧出现=结论降级为描述性)。所附四项引用为四项资产的当前水平锚点(供对照，不承载历史段数字)；历史段事后数字取自相似检索面事后块，按自然月末口径，事后结果≠预测。
**竞争解释(受审稿原文摘要)**: 解释A: 三段事后差异主要由各自独有的政策与冲击环境造成(2022-06 处加息中段、2023-10 处高利率平台期、2025-03 处波动冲击后修复)——事件叙述均为【假设】,引擎面不含事件因果数据 | 解释B: 差异由相似度量本身的低维覆盖造成(状态向量 growth 覆盖0.17、inflation 0.33、credit 0.5,信用维在多数候选月缺席),距离最近的时期未必在未覆盖维上可比——若如此,任何单段外推都缺失维度证据
**① 证据相关性**: 4 条 evidence_refs 为四项资产的当前水平锚点(受审稿自述不承载历史段数字); 历史段的逐窗数字、当时可知面与同步性格逐格取自冻结序列重算, 全部一致(台账 『⑧历史事后窗』110 条(#227–#325、#874–#875、#908–#916)、『⑧历史事后窗(细表)』82 条(#688–#769)、『⑧同步面/当时可知』102 条(#129–#226、#870–#873))。
**② 支持度**: 2022-06 段三个月窗 DAX、SHCOMP、SPX、NIKKEI225 均为负而十二个月窗除 SHCOMP 外转正; 2025-03、2023-10 段风险资产与 GOLD_F 多数窗走强、DXY 走弱(例外 2023-10 段上证指数三个月窗为负, 受审稿已披露)(#686–#687); 逐窗数字所在记录 ##272、#275、#278、#281、#283、#314、#908; TOP-N 事后符号一致率 GOLD_F、SPX 六/十二个月窗为 1.0, 其余各窗 0.6–0.8(#581–#583); 状态向量维度覆盖 growth 0.17、inflation 0.33、credit 0.5 为引擎面原值(#579)。
**③ 竞争解释**: 『各段独有政策/冲击环境』(标【假设】)与『相似度量低维覆盖』相容且均为真竞争。
**④ 反对证据**: 与『分歧明显』方向相反的事实是 GOLD_F 与 SPX 六/十二个月窗在全部 TOP-5 段符号一致(1.0)——受审稿同句如实列出; 2025-03 段十二个月事后窗(至 2026-03-31)与本轮研究窗重叠 129 天、样本非独立——受审稿已披露(#916); 未发现未披露的反向事实。
**⑤ 结论是否超出证据**: 只作结构对照与情景校准、不作预测, 未超出。
**⑥ 证伪条件可观测性**: 本条为描述性登记, 未设区分指标; 情景段另设数字阈值(见 5.7)。
**历史段同步性(规程第 4 节专项)**: 三段九格的同步/分化主张与引擎地区×维度同步面逐格一致; 当时可知面数值(如 2025-02 欧元区 HICP 2.3、日本 CPI 3.66、中国 PPI -2.2、中国 CPI -0.7)经发布纪律核对一致, 无『面为缺证而叙述称同步』或叙述与面冲突的情形(『⑧同步面/当时可知』102 条(#129–#226、#870–#873)、#870–#873)。
**反方攻击**: 5.8 第 4–6 条。**小结**: 无 MAJOR; NIT-4、NIT-11。
### 5.3 矛盾陈述 C3(中国: PPI 上行而政策利率未上调)
**受审主张(摘要)**: 中国政策与美欧日方向的背离未被解释定案: CN_PPI_YOY 自深负值区间升至本轮高点(四大经济体最大价格摆动)而 CN_LPR_1Y 与 7天逆回购利率窗内持平(7天逆回购末观测 2026-10-30，其后缺观测)、政策利率锚于2026-11-02切换为隔夜利率工具后新锚持平于其首个观测水平,即生产价格大幅上行而政策利率未上调。引擎面无中国利率预期序列;信贷/内需侧仅有 CN_NEW_LOANS(月频，最新观测月 2026-10)等少量事实，不足以在三种解释间裁决,三种解释不可区分,标注【尚未验证】。(最新读数: CN_PPI_YOY 为 5.7、CN_CPI_YOY 为 0.7、CN_PMI_MFG 为 49.3;观测月均为 2026-10)。
**竞争解释(受审稿原文摘要)**: 解释A: 价格上行主要为输入型/供给驱动(PPI 与 CPI 剪刀差大),内需(CN_CPI_YOY 仅0.7)不足以支持收紧——若如此,背离是合理的政策反应 | 解释B: 内需不足制约政策空间(增长侧 CN_PMI_MFG 最新49.3处荣枯线下),即便价格上行也不敢收紧——若如此,背离反映的是增长约束而非价格判断 | 解释C: 汇率/资本流动目标约束政策选择——引擎面无中国资本流动序列,该解释当前不可裁决,标注【尚未验证】；汇率腿的可见事实: USDCNY 12 个月 -6.19%(7.1075→6.6676，共同口径 2025-11-19→2026-11-19)，人民币窗内升值，不支持『贬值/外流压力制约加息』的读法
**① 证据相关性**: 4 条 evidence_refs(CN_PPI_YOY、CN_CPI_YOY 2026-10 观测, CN_LPR_1Y 2026-11-20, USDCNY 2026-11-23)逐值核对(#901–#903、#905、#331)。
**② 支持度**: CN_PPI_YOY 自 2025-11 窗内低点 -2.2 升至 2026-10 的 5.7(2026-07 曾回落至 3.5), 为四地 12 个月窗最大价格摆动; CN_CPI_YOY 最新 0.7, 与 PPI 剪刀差 5.0 个百分点(#400–#407、#901–#903、#906); CN_LPR_1Y 一年窗内 12 个观测均为 3.0(最新 2026-11-20), CN_OMO_7D 一年窗内 199 个观测均为 1.4(末观测 2026-10-30), 隔夜逆回购利率 2026-11-02 起 16 个观测均为 1.25, CN_PMI_MFG 最新 49.3(#905、#779、#449–#454、#904)。
**③ 竞争解释**: 输入型/供给、内需不足、汇率/资本流动(【尚未验证】)三解同证据可容纳; 引擎无中国利率预期与资本流动序列, 第三解不可裁决, 受审稿如实标注(#490–#495)。
**④ 反对证据**: USDCNY 12 个月 -6.19%(7.1075→6.6676)与『贬值/外流压力』读法相反——受审稿已写入解释 C(#331); 7 天逆回购末观测距截止日 24 天、其后缺观测, 换锚后仅 16 个交易日观测——受审稿逐处披露(#449–#454); Gate A 缺口披露未渲染入报告(MINOR-3)。
**⑤ 结论是否超出证据**: 『三种解释不可区分』与证据相称, 未下因果结论。
**⑥ 证伪条件可观测性**: 三解未被赋予可观测区分指标。本条在判断档登记为『尚未验证』的矛盾陈述而非机制链, 受审稿未对其作出可被证伪的因果断言, 故不按『证伪条件不可观测』计 MAJOR; 建议后续为解释 A/B 指定区分指标(如 PPI-CPI 剪刀差与 CN_CPI_YOY 的后续走向)。
**反方攻击**: 5.8 第 7–8 条。**小结**: 无 MAJOR; MINOR-3(披露位置)。
### 5.4 机制链 M1『通胀再加速→政策再收紧→实际利率上行→风险资产承压』(四环)
**环 1 冲击环(E1)**: 事实——美欧通胀与中国生产价格 2026-02→2026-05 同窗回升; 布伦特原油月末 2026-02 72.48→2026-03 118.35→2026-05 92.05(首尾 +27.00%), 2026-06 月末 72.92, 截止日 88.19(盘中快照)、当月至今 -25.03%; 美国核心 CPI 同比 2026-02 2.47→2026-05 2.82(#507、#525–#528、#546)。对质(区分指标 BRENT_F, 预注册窗 2026-02 至 2026-05): 主解释『同窗显著上行』获支持, 竞争解释『大体持平』未获支持; 核心通胀同窗上行对两解释均相容(受审稿自述不构成区分观测)。
**环 2 政策环(E3: 时序为事实、动机为假设)**: 时序——政策变动月(2026-06 起)晚于通胀转折月(至 2026-05): 美联储 2025-12-10 决议、12-11 生效 -25 个基点, 2026-09-16 决议、09-17 生效 +25 个基点(决议日=生效日前一日惯例); 欧央行生效日 2026-06-17、2026-09-16 各 +25 个基点(决议日按『生效日前上一个周四』回推 2026-06-11、2026-09-10, 标【推断】); 日本央行 2026-09-18 决议、09-24 生效(冻结日历实录)(#918、#919、#923、#924、#925、#926)。决议时点可见数据(注册表发布规则)——美国 CPI: 欧央行首次决议前可见 2026-04 观测 3.78(处上行段), 第二次决议前 2026-07 观测 3.30、美联储与日本央行决议前 2026-08 观测 3.35(均低于 2026-05 高点 4.17); 核心 PCE 2026-07 观测 3.00 低于 2026-05 高点 3.16; 欧元区 HICP 2026-07 观测 2.9 低于 2026-05 高点 3.2; 日本 CPI 2026-07 观测 1.97 处回升段。本席自快照直算复核: CPI 同比 2026-04 3.7792 / 2026-07 3.3039 / 2026-08 3.3530, CORE_PCE 同比 2026-05 3.1617 / 2026-07 2.9953; EA_HICP_YOY 2026-06 2.8 / 2026-07 2.9 / 2026-08 3.2(出处: research_snapshot_20261123.json series_store.CORE_PCE(同比=观测月水平/前一年同月水平-1); series_store.EA_HICP_YOY; series_store.CPI)。动机环标【假设】, 证伪指标 CPI 在场。唯欧元区 HICP 发布规则在引擎内有双口径, 受审稿此环只按注册表口径立论(MINOR-1; 台账 #878–#884)。
**环 3 利率环(E1)**: 12 个月窗(2025-11-19→2026-11-19 共同交易日)名义 +91 = 实际 +102 + 盈亏平衡 -11 个基点, 恒等残差 0; 水平 UST_10Y 5.04、TIPS_10Y 2.88、BEI_10Y 2.16@2026-11-19(最新 2.15@2026-11-20)(#508–#515、#898)。
**环 4 资产环(E2: 缺环为假设)**: 近 1 个月资产窗、同日收盘口径、TIPS/SPX 窗口对照、HY_OAS 水平 3.52(约第 92 百分位; 序列高点 4.61@2025-04-07; 上一次不低于最新读数为 2025-05-09 的 3.53)全部一致(#332–#344、#498–#506、#522–#524、#329–#330)。
**六查**: ① 四环 evidence_refs 均为本轮冻结快照事实, 标签日期与观测日关系同 C1。② E1 两环(冲击、利率)为纯事实且逐位一致; E3、E2 两环以【假设】字面标明不可验证的环节。③ 竞争解释——环 1『需求过热或基数效应主导』、环 2『收紧另有动机(金融稳定/汇率/正常化独立进程)』、环 4『增长担忧主导』——均与同证据相容, 且在区分指标上预言方向不同(BRENT_F 大体持平 vs 显著上行; BEI_10Y 与政策节奏脱钩 vs 收紧前上行段; BEI_10Y 明显下行且 TIPS_10Y 转平 vs TIPS_10Y 续升而 BEI_10Y 稳定), 属真正竞争。④ 反对证据——油价尖峰为暂时性(2026-06 月末回到 72.92)而通胀此后仍升; 决议前可见通胀已自高点回落; 12 个月窗内实际利率与股指同向上行——三项均由受审稿自己写入并据此限定结论(支持度限于预注册窗、动机环降为假设、资产环标 E2 并写共动方向随窗口而异); 无未披露的反向事实。⑤ 结论未超出: 每环都写明不可验证之处, 未把时序先后或共动写成因果。⑥ 证伪可观测: 环 2 证伪指标 CPI(阈值 2.5 为数字; 2026-10 同比缺基期已披露, 2026-11 起可算), 环 4 证伪指标 HY_OAS(预警级 3.53、失效级 4.61, 均为库内可观测水平)。
**反方攻击**: 5.8 第 9–12 条。**小结**: 无 MAJOR; MINOR-1、MINOR-2。
### 5.5 机制链 M2『日本持续正常化→全球期限溢价/套息渠道(竞争性全球机制)』(两环)
**环 1(E1)**: JP_POLICY_RATE(无担保隔夜拆借月均)自 2025-11 的 0.478 步进升至 2026-10 的 1.227(窗内净 +75 个基点; 步进 +8/+17/+11/+14/+7/+18 落在 2025-12、2026-01、2026-06、2026-07、2026-09、2026-10; 2026-04 与 2026-08 各有约 0.1 个基点的舍入级变动; 自 2025-12 的 0.557 起为 +67 个基点, 另一口径并记); 冻结日历载日本央行 2026-09-18 决议、2026-09-24 生效、目标 1.25, 及 2026-10-30 确认维持; USDJPY 159.35@2026-11-23(盘中快照)(#897、#920–#922、#923)。
**环 2(E3: 整环假设)**: 引擎无 JGB 收益率历史序列, 整环不可验证; 证伪指标 USDJPY 在场(#490–#495)。
**六查**: ① 引用为冻结快照事实与冻结日历实录。② 环 1 事实逐位一致; 环 2 无可验证事实, 已标明。③ 竞争解释『近月风险资产收缩源于美国国内利率/增长定价』与证据相容, 在 USDJPY 上预言相反(时间上解耦 vs 同现)。④ 反对证据——同窗(2026-10-23→2026-11-23)SPX -5.51% 而 USDJPY +1.82%(156.49→159.35), 主解释『风险资产收缩与日元走强同现』的预期未获支持; 逐日面 21 个交易日相关系数 0.19、同向 16 日, 仅弱同向耦合——受审稿在传导链 TR2 第一环已裁定主解释的同窗预期未获支持, 并说明竞争解释的字面预期未获完全确认(#345–#346); 无未披露的反向事实。⑤ 结论未超出: 机制链定位为竞争性全球机制、整环假设。⑥ 证伪可观测: USDJPY 在场, 条件含可判形态(风险资产再次收缩时 USDJPY 是否同步走低)。
**反方攻击**: 5.8 第 13–15 条。**小结**: 无 MAJOR; NIT-3、NIT-8。
### 5.6 对质环(读者面传导链 TR1 三环、TR2 一环)
TR1-1(BRENT_F): 主解释『同窗显著上行』 vs 竞争解释『大体持平而核心通胀上行』 → 月末 72.48→92.05(首尾 +27.00%, 2026-03 冲至 118.35), 裁定『支持主解释』与数据一致(#507、#525–#528)。
TR1-2(BEI_10Y): 主解释『收紧前处上行段且高位』 vs 竞争解释『政策续紧而 BEI_10Y 不升』 → 2026-02-27 2.25→2026-05-04 2.50(上行段成立), 首次加息决议前日 2026-06-10 为 2.34, 收紧后(2026-06-17 起)区间 2.15–2.40, 近一个月(2026-10-23→2026-11-20)2.34→2.15(竞争解释的形态亦在) → 裁定『尚不能区分』如实(#516–#518)。
TR1-3(BEI_10Y、HY_OAS): 主解释『TIPS_10Y 续升而 BEI_10Y 稳定、HY_OAS 不升破高点』 vs 竞争解释『BEI_10Y 明显下行且 TIPS_10Y 转平/回落、HY_OAS 走阔』 → TIPS_10Y 12 个月 +102、近 1 个月 +11 个基点(未转平), BEI_10Y -11 / -19 个基点(下行但幅度有限), HY_OAS 3.52 未破 3.53 → 『尚不能区分』如实(#508–#515、#522–#524)。
TR2-1(USDJPY): 主解释『风险资产收缩与日元走强(USDJPY 走低)同现』 vs 竞争解释『时间上解耦』 → 同窗 USDJPY +1.82% 而 SPX -5.51% → 裁定『支持竞争解释』与区分指标面一致(逐日面弱同向的保留意见受审稿已附注)(#345–#346)。
四环的区分指标均在证据面在场(#544), 两解释预言方向相反; 无『证伪条件不可观测』情形。
### 5.7 情景(L4: SCN1、SCN2)
两情景互为对照、方向互补(台账 #547–#555、#908–#911、#912–#914)。证伪条件均为数字阈值且指标在场: SCN1——美国 CPI 同比回落至 2.5 以下且 CORE_PCE 回落至 2.8 以下并持续两个月(截止日读数 CPI 3.72@2026-09、CORE_PCE 3.12@2026-09, 未成立); SCN2——BEI_10Y 跌破 1.8(最新 2.15@2026-11-20, 较阈值高 35 个基点; 库内最近一次低于 1.8 为 2020-11-30 的 1.77, 较最新读数低 38 个基点; 未成立)。期限 2027-02-28, 所涉观测的规则发布日均早于期限(台账 #917 为参数性数字的登记项, 不计入比对点)。截止日无已被证伪而仍列为前提的内容; 阈值(CPI 3 / 3.5 / 2.5, CORE_PCE 2.8, BEI_10Y 1.8)落在截止日读数与高点之间, 可观测。
**反方攻击(情景)**: 指控情景阈值系为免于被证伪而事后选定 → 阈值均为数字、指标在场、期限早于所涉观测的规则发布日, 截止日读数均在未证伪一侧而触发所涉 2026-11/12 观测尚未发布; 未发现证伪条件不可观测(5.8 第 20 条)。

### 5.8 反方攻击记录(与 VERDICT JSON 的 counterexamples_sought 逐条对应)

1. 反方攻击 1(矛盾陈述 C1·同向共动): 指控四环链条以窗口选择拼成——资产收缩一腿只在近月窗成立(SPX 近 1 个月 -5.51%), 12 个月窗股指与实际利率同向上行(TIPS_10Y +102 个基点同期 SPX +8.03%、NIKKEI225 +22.47%、DAX +9.93%)→ 受审稿在同一句括注与机制链资产环明示共动方向随窗口而异, 三解的区分指标不依赖资产腿符号; 攻击不成立为 MAJOR, 仅留行文限定(NIT-10)。
2. 反方攻击 2(矛盾陈述 C1·解释降级): 指控增长担忧一解被过快降级——若盈亏平衡主导下行则该解应获更多支持 → 近 1 个月 BEI_10Y -19 个基点(名义 -8、实际 +11)确与该解的盈亏平衡一腿相容, 但 12 个月窗 BEI_10Y -11、TIPS_10Y +102 个基点与其『TIPS 转平』相左; 受审稿裁定『部分相容』与两窗数据一致, 未过快降级。
3. 反方攻击 3(矛盾陈述 C1·政策面): 指控『DFF 回到降息前台阶』掩盖政策取向 → 一年窗内 -25/+25 个基点净变 0, 最新 3.88 与 2025-11-22 锚值 3.88 相同(变动点值 3.89→3.64、3.63→3.88 相差 1 个基点), 表述成立; 仅括注未标观测日(MINOR-2)。
4. 反方攻击 4(矛盾陈述 C2·低维覆盖): 指控相似度低维覆盖被夸大或被隐去 → 覆盖 0.17/0.33/0.5 为引擎 state_vector 原值且受审稿明示; 2025-03 段相似度构成(波动 42.1%、利率 40.7%)亦与引擎面一致。
5. 反方攻击 5(矛盾陈述 C2·自相矛盾): 指控『事后路径分歧明显』与『GOLD_F、SPX 六/十二个月窗符号一致率 1.0』不能并存 → 分歧在股指三个月窗与 DXY, 一致在黄金与股指中长窗, 受审稿两句并列披露, 无隐匿。
6. 反方攻击 6(矛盾陈述 C2·口径): 指控按自然月末口径重算的历史段数字与引擎事后块矛盾 → 逐格两口径差中位约 0.35、最大 1.41 个百分点, 无符号翻转; 受审稿注记『可差约1个百分点』对上界偏低(NIT-4)。
7. 反方攻击 7(矛盾陈述 C3·相邻口径): 指控『政策利率未上调』以相邻口径冒充(7 天逆回购→隔夜逆回购换锚)并依赖过期观测 → 受审稿分列两工具并披露末观测 2026-10-30 与其后缺观测; 一年窗内 199 个 7 天逆回购观测均为 1.4, LPR 3.0 现行至 2026-11-20 且不在 Gate A 名单, 新锚 16 个交易日均为 1.25; 披露属实, 唯 Gate A 缺口披露未入报告(MINOR-3)。
8. 反方攻击 8(矛盾陈述 C3·汇率): 指控以 USDCNY 12 个月 -6.19% 否定汇率/资本流动解释属超出 → 受审稿只称不支持贬值/外流压力读法并保留【尚未验证】, 且自陈三解不可区分, 未超出。
9. 反方攻击 9(机制链 M1·冲击环): 指控油价尖峰为暂时性(2026-06 月末回到 72.92)而通胀此后仍升, 冲击→通胀因果不成立 → 受审稿把支持度限定在预注册窗 2026-02 至 2026-05(月末 72.48→92.05, 首尾 +27.00%)并只用『时序与幅度相容』, 明写能源价格向消费价格的因果传导不可由引擎验证, 未称因果成立。
10. 反方攻击 10(机制链 M1·政策环): 指控『央行因通胀再加速而收紧』与决议前可见数据(通胀已自高点回落)相左 → 受审稿自身已披露(CPI 3.30/3.35 低于 4.17, CORE_PCE 3.00 低于 3.16, HICP 2.9 低于 3.2)并据此把动机环降为 E3【假设】; 唯欧元区 HICP 发布规则双口径未在该处注明(MINOR-1)。
11. 反方攻击 11(机制链 M1·资产环): 指控『实际利率上行→风险资产收缩』不可识别(12 个月窗同向上行) → 受审稿标 E2、写明引擎只有共动事实无因果识别并给出窗口对照; 证伪指标 HY_OAS 在场(3.52, 预警级 3.53, 失效级 4.61)。
12. 反方攻击 12(机制链 M1·阈值): 指控 HY_OAS 预警级阈值 3.53 距最新 3.52 仅 1 个基点、近乎必然触发 → 属阈值松紧的判断选择; 受审稿标明两级阈值与库内依据(2025-05-09 的 3.53、2025-04-07 的 4.61), 可观测, 未把未发生之事写成事实。
13. 反方攻击 13(机制链 M2·同窗反证): 指控套息平仓渠道的同窗预期已被数据否定(USDJPY 156.49→159.35 即 +1.82% 而 SPX -5.51%, 逐日相关 0.19)而受审稿仍列为主解释 → 受审稿在 TR2 裁定主解释的同窗预期未获支持、支持竞争解释; 唯机制链第二环文本只写未来式证伪条件, 未就地写入该形态(NIT-8)。
14. 反方攻击 14(机制链 M2·口径): 指控以月均拆借利率(市场口径)冒充政策目标 → 受审稿明写序列为无担保隔夜拆借月均, 政策决议与目标水平取自冻结日历实录(2026-09-18 决议、2026-09-24 生效、目标 1.25; 2026-10-30 确认维持), 未冒充。
15. 反方攻击 15(机制链 M2·未回撤): 指控『窗内未回撤』被月均序列的微降证伪 → 2026-04、2026-08 各约 0.1 个基点的舍入级变动(0.728→0.727、0.978→0.977), 受审稿已并记; 首次上调月 2025-12 早于美欧通胀同窗回升起点 2026-02。
16. 反方攻击 16(对质环 TR1-1, BRENT_F): 主解释预言同窗显著上行、竞争解释预言大体持平 → 月末 72.48→92.05(2026-03 冲至 118.35), 裁定『支持主解释』与数据一致。
17. 反方攻击 17(对质环 TR1-2, BEI_10Y): 主解释预言收紧前处上行段且高位, 竞争解释预言政策续紧而 BEI_10Y 不升 → 2026-02-27 2.25→2026-05-04 2.50(前者成立), 2026-06-17 起政策续紧而 BEI_10Y 处于 2.15–2.40 区间未升(后者形态亦在) → 『尚不能区分』如实。
18. 反方攻击 18(对质环 TR1-3, BEI_10Y+HY_OAS): 利率主导预言 BEI_10Y 稳定、TIPS_10Y 续升、HY_OAS 不升破高点; 增长主导预言 BEI_10Y 明显下行、TIPS_10Y 转平、HY_OAS 走阔 → BEI_10Y 12 个月 -11、近 1 个月 -19 个基点, TIPS_10Y +102 / +11 个基点, HY_OAS 3.52 未破 3.53, 两侧各有相容观测 → 『尚不能区分』如实。
19. 反方攻击 19(对质环 TR2-1, USDJPY): 主解释预言风险资产收缩与日元走强同现 → 同窗 USDJPY +1.82% 而 SPX -5.51% → 裁定『支持竞争解释』与区分指标面一致。
20. 反方攻击 20(情景 SCN1/SCN2): 指控阈值系为免于被证伪而设 → 阈值均为数字、指标在场、期限 2027-02-28 早于所涉观测的规则发布日; 截止日读数(CPI 3.72、CORE_PCE 3.12、BEI_10Y 2.15)均在未证伪一侧, 触发所涉 2026-11/12 观测尚未发布; 可观测。

## 6 问题清单(按 MAJOR / MINOR / NIT)

### 6.1 MAJOR(0 条)

无: 未发现数字 / 日期 / 方向错误, 缺基期同比, 相邻口径冒充, 事后信息冒充当时可知, 无标注的超证据结论, 或不可观测的证伪条件。

### 6.2 MINOR(4 条; 口径/披露可改进但不改变结论, 不构成阻断)

- **MINOR-1(甲)** 位置: agent_judgment.json l3.mechanism_chains[0].links[1].text; FULL_REPORT.md 第 80 行; report.md 第 90 行
  - 原句: 欧央行 2026-09-10 决议前最近可见 HICP 为 2026-07 观测 2.9，自 2026-06 的 2.8 回升、低于 2026-05 高点 3.2
  - 建议改句(非必修): 欧央行 2026-09-10 决议前最近可见 HICP: 按注册表保守口径(终值=观测月末+16 天)为 2026-07 观测 2.9，自 2026-06 的 2.8 回升、低于 2026-05 高点 3.2；按引擎历史面两级口径(快报=观测月末当日可见，推定)则 2026-08 观测的快报已于 2026-08-31 可见、其月值为 3.2 持平 2026-05 高点(当时快报值不可回溯)——「决议前可见读数低于高点」对美联储成立，对欧央行仅在前一口径下成立
  - 说明: MINOR-1(甲) 口径未并列: 引擎内欧元区 HICP 发布规则有双口径。注册表保守口径(终值=观测月末+16 天)下, 决议时点(回推 2026-09-10【推断】)前最近可见为 2026-07 观测 2.9(规则发布日 2026-08-16), 2026-08 观测 3.2 推定发布 2026-09-16、决议时点尚未可见——受审句数值全部成立。但引擎历史面与受审稿自身历史段使用两级口径(快报=观测月末当日可见): 据此 2026-08 观测的快报已于 2026-08-31 可见, 序列该月值 3.2 持平 2026-05 高点 3.2, 「决议前可见读数低于高点」对欧央行一腿在此口径下不成立(当时快报值不可回溯, 属【推断】)。该环已标 E3【假设】并自述动机不可验证, 结论方向(动机环证据减弱)不变, 故计 MINOR、不计 MAJOR。出处: research_snapshot_20261123.json series_store.EA_HICP_YOY(2026-05 3.2 / 2026-06 2.8 / 2026-07 2.9 / 2026-08 3.2); root_overlay/config/metric_registry.json(metric EA_HICP_YOY release_semantics: 次月中旬终值、保守标注); root_overlay/config/release_calendar.json 内 EA_HICP_YOY 条目 3 条; 台账 #878–#884。
- **MINOR-1(乙)** 位置: agent_judgment.json reader_map.transmission[0].links[1].causal_hypothesis; MAP_REPORT.md 第 197 行
  - 原句: 且决议时点前已可见的美国 CPI 与核心 PCE 同比、以及欧元区 HICP 均低于各自 2026-05 高点(见观察事实)，对美联储决议与欧央行第二次决议的动机环证据减弱
  - 建议改句(非必修): 且决议时点前已可见的美国 CPI 与核心 PCE 同比均低于各自 2026-05 高点，欧元区 HICP 按注册表保守口径亦低于 2026-05 高点(按引擎历史面两级口径则 2026-08 观测已可见、持平高点)(见观察事实)，对美联储决议的动机环证据减弱，对欧央行第二次决议的同类证据减弱仅在前一口径下成立
  - 说明: MINOR-1(乙) 与甲同源: 「欧元区 HICP 低于 2026-05 高点」只在注册表保守发布口径下成立(2026-07 观测 2.9、规则发布 2026-08-16); 引擎历史面两级口径下 2026-08 观测(月值 3.2)已于 2026-08-31 可见、持平高点。该环为 E3【假设】且本句以「证据减弱」措辞自限, 结论不变, 计 MINOR。出处: series_store.EA_HICP_YOY; 台账 #878–#884。
- **MINOR-2** 位置: agent_judgment.json reader_map.transmission[0].links[1].observed_fact; MAP_REPORT.md 第 81、196 行
  - 原句: (DFF 3.88→3.63→3.88)
  - 建议改句(非必修): (DFF 三时点锚值 3.88→3.63→3.88，观测 2025-11-22 / 2026-08-22 / 2026-11-19；变动点 2025-12-11 自 3.89 降至 3.64、2026-09-17 自 3.63 升至 3.88，步长 -25 / +25 个基点)
  - 说明: MINOR-2: 括注三值是三时点面板锚值(观测 2025-11-22 / 2026-08-22 / 2026-11-19), 未标观测日; 实际变动点为 2025-12-11 的 3.64(前值 2025-12-10 的 3.89)、2026-09-17 的 3.88(前值 2026-09-16 的 3.63)(各与括注值相差 1 个基点, 属日频有效利率逐日波动); 步长 -25/+25 个基点与窗内净变 0 成立, 结论不变。出处: series_store.DFF; report.json research_plan 三时点面板; 台账 #520、#877。
- **MINOR-3** 位置: agent_judgment.json reader_map.headline_conclusion; MAP_REPORT.md 第 12 行; MAP_REPORT.md 第 6 行
  - 原句: 中国未跟进加息(7天逆回购利率与LPR窗内无变动——7天逆回购末观测2026-10-30、其后至截止日缺观测；2026-11-02起政策利率锚切换为隔夜逆回购利率)(背离)
  - 建议改句(非必修): 中国未跟进加息(7天逆回购利率与LPR窗内无变动——7天逆回购末观测2026-10-30、其后至截止日缺观测；2026-11-02起政策利率锚切换为隔夜逆回购利率)(背离)〔口径加注: 7天逆回购利率与隔夜逆回购利率均为 Gate A 非核心缺口指标, 本句按序列库存量观测引用(7天逆回购一年窗内 199 个观测均为 1.4、末观测 2026-10-30; 隔夜逆回购 2026-11-02 起 16 个交易日均为 1.25); LPR 3.0 现行至 2026-11-20、不在 Gate A 名单)〕; 并把 quality_gate_notes 六条渲染入 MAP_REPORT.md 读者面
  - 说明: MINOR-3 披露位置: 首页结论与 C3 按存量观测引用 Gate A 非核心缺口指标(CN_OMO_7D、CN_POLICY_OVERNIGHT、EA_REAL_GDP_YOY、JP_CPI_TOKYO_YOY、JP_REAL_GDP_YOY), 判断档另引用非核心降级指标(ECB_DFR、ECB_MRO、US_REAL_GDP)。逐项口径只存于 agent_judgment.json quality_gate_notes[3、5](Gate A) 与 [3、5](存量观测), 六条质量注记在三份报告中逐字渲染 0 条(台账 #860); 读者报告侧只有两处概括: C1 陈述内的「缺口指标中有五项在序列库内仍有存量观测并被本档按存量观测引用」(agent_judgment.json l3.contradictions[0].statement; FULL_REPORT.md 第 67 行; report.md 第 74 行)与 MAP_REPORT 数据门行「缺席/降级数据不得进入研究结论」(MAP_REPORT.md 第 6 行); MAP_REPORT 首页句与传导链在使用处不带缺口标记, 与数据门行的表述未对齐。经序列级核实披露内容属实、不属于把缺席写成无变化: 7 天逆回购一年窗内 199 个观测均为 1.4(末观测 2026-10-30), LPR 3.0 现行至 2026-11-20 且不在 Gate A 名单, 隔夜逆回购 2026-11-02 起 16 个交易日均为 1.25(台账 #865–#869、#779、#905、#904)。

### 6.3 NIT(11 条; 行文)

- **NIT-1** 位置: agent_judgment.json reader_map.turning_supplement[0].first_mover; MAP_REPORT.md 第 237 行
  - 原句: 全国口径的回升起点(2026-03)
  - 建议改句(非必修): 全国口径自 2026-03 起自低点回升(2026-04 小幅回落后自 2026-05 起连续回升)
  - 说明: NIT-1 措辞: 日本 CPI 同比 2026-02 为 1.27(窗内低点)→2026-03 升至 1.46, 2026-04 回落至 1.38, 自 2026-05(1.53)起逐月回升至 2026-09 的 2.16; 「回升起点」指低点后首月, 因 2026-04 回落一词有歧义。出处: series_store.JP_CPI_YOY; 台账 #929、#930、#430–#438。
- **NIT-2** 位置: agent_judgment.json reader_map.turnings[0].first_mover; MAP_REPORT.md 第 235 行
  - 原句: 中国 PPI 低点在 2025-11
  - 建议改句(非必修): 中国 PPI 本轮窗内低点在 2025-11
  - 说明: NIT-2 限定词: -2.2 为本轮 12 个月窗内低点; 序列全史低点为 -8.22@2009-07, 2023 年以来低点为 -5.4@2023-06。出处: series_store.CN_PPI_YOY; 台账 #400–#407。
- **NIT-3** 位置: agent_judgment.json reader_map.transmission[1].links[0].causal_hypothesis; MAP_REPORT.md 第 207 行
  - 原句: 对质表判断记『支持竞争解释』
  - 建议改句(非必修): 对质表判断记『主解释同窗预期未获支持, 倾向竞争解释(逐日面仅弱耦合)』
  - 说明: NIT-3 语气: 同窗美元兑日元 +1.82%(156.49→159.35)对标普500指数 -5.51% 方向相反, 但逐日面相关系数 0.19(21 个交易日、同向 16 日)只属弱同向耦合; 受审稿已附「竞争解释的字面预期未获完全确认」, 判断与数据一致。出处: series_store.USDJPY、SPX; 台账 #345–#346。
- **NIT-4** 位置: agent_judgment.json reader_map.history_periods[0].ex_post.3m、reader_map.history_periods[0].ex_post.6m、reader_map.history_periods[0].ex_post.12m、reader_map.history_periods[1].ex_post.3m、reader_map.history_periods[1].ex_post.6m; MAP_REPORT.md 第 400、401、402、524、525、526 行
  - 原句: 两口径数值可差约1个百分点
  - 建议改句(非必修): 两口径数值可差约 0.35 个百分点(中位)、最大约 1.41 个百分点, 无符号翻转
  - 说明: NIT-4 精度: 两口径逐格差中位约 0.35 个百分点、最大 1.41 个百分点(2023-10 段标普500指数十二个月窗), 无符号翻转; 「约1个百分点」对上界略偏低。出处: series_store 四项资产月末序列与 report.json 相似检索面; 台账 #874。
- **NIT-5** 位置: agent_judgment.json reader_map.transmission[0].links[0].competing_explanation; MAP_REPORT.md 第 194 行
  - 原句: 若如此,BRENT_F 应大体平稳而 CORE_CPI/CORE_PCE 独立走高
  - 建议改句(非必修): 若如此,BRENT_F 应大体平稳而 CORE_CPI/CORE_PCE 独立走高(需求过热情形下油价与核心通胀亦可同涨, 须另以需求侧指标区分)
  - 说明: NIT-5 竞争预言只在基数效应或供给因素主导的情形下才有约束力: 需求过热情形下油价与核心通胀可同涨, 该预言对其偏弱; 受审稿已自述核心通胀同窗上行不构成区分观测, 裁定为「尚不能区分」未受影响。出处: series_store.BRENT_F、CORE_CPI; 台账 #507、#525–#528、#546。
- **NIT-6** 位置: agent_judgment.json l3.contradictions[0].statement; FULL_REPORT.md 第 67 行; report.md 第 74 行
  - 原句: 逐项见质量注记
  - 建议改句(非必修): 逐项见 MAP_REPORT 数据门行与本档 quality_gate_notes(建议渲染入读者报告)
  - 说明: NIT-6 悬空指引: 所指 quality_gate_notes 六条在三份报告中逐字渲染 0 条(台账 #860); 该句渲染于 agent_judgment.json l3.contradictions[0].statement; FULL_REPORT.md 第 67 行; report.md 第 74 行, 读者按指引找不到逐项口径; 与 MINOR-3 同源。
- **NIT-7** 位置: agent_judgment.json reader_map.transmission[0].links[2].observed_fact、quality_gate_notes[0]; MAP_REPORT.md 第 81、200 行
  - 原句: NIKKEI225 止于 2026-11-20 收盘
  - 建议改句(非必修): NIKKEI225 止于 2026-11-20 收盘(2026-11-23 该序列无观测, 为每年重复出现的非观测日, 非采集滞后)
  - 说明: NIT-7 原因未写: 属实——2026-11-23 该序列无观测(2016–2023 年中 11 月 23 日为交易日的 7 年当日均无该序列观测; 同日上证指数、DAX 有观测), 属每年重复出现的非观测日而非采集滞后。台账 #876。
- **NIT-8** 位置: agent_judgment.json l3.mechanism_chains[1].links[1].text; FULL_REPORT.md 第 86 行; report.md 第 95 行
  - 原句: 证伪指标=USDJPY
  - 建议改句(非必修): 证伪指标=USDJPY(近窗首次对质见传导链 TR2: 同窗美元兑日元 +1.82% 对标普500指数 -5.51%, 主解释同窗预期未获支持); 若风险资产再次收缩而 USDJPY 未同步走低/日元未走强,套息平仓渠道的分量应被下调
  - 说明: NIT-8 就地引述缺位: 机制链第二环只写未来式证伪条件, 未就地写入近窗对质(同窗美元兑日元 +1.82% 对标普500指数 -5.51%, 主解释同窗预期未获支持); 该对质已在传导链 TR2 完成并披露, 无隐匿。台账 #345–#346。
- **NIT-9** 位置: agent_judgment.json quality_gate_notes[2]
  - 原句: 冻结发布日历无美联储与欧央行实录条目
  - 建议改句(非必修): 冻结发布日历无美联储与欧央行政策决议实录条目(其决议日按生效日惯例回推【推断】)
  - 说明: NIT-9 范围词: 冻结日历 18 条中有数据发布条目(美国 11 条、HICP 3 条、LPR 2 条), 缺的是美联储与欧央行政策决议实录而非全部实录。出处: release_calendar.json entries; 台账 #924。
- **NIT-10** 位置: agent_judgment.json l3.contradictions[0].statement; FULL_REPORT.md 第 67 行; report.md 第 74 行
  - 原句: 四地证据面呈现『通胀再加速→政策再收紧→实际利率上行→风险资产收缩』的同向共动
  - 建议改句(非必修): 美欧日三地证据面呈现『通胀再加速→政策再收紧→实际利率上行』的同向共动, 近月窗口内叠加风险资产收缩(中国未跟进加息)
  - 说明: NIT-10 首页句缺限定词: 政策再收紧只适用于美欧日(中国未跟进加息), 风险资产收缩只在近月窗成立(12 个月窗股指与实际利率同向上行); 受审稿在同句括注与机制链资产环已逐项限定, 结论不变。台账 #326–#328、#899。
- **NIT-11** 位置: agent_judgment.json l3.contradictions[1].statement; FULL_REPORT.md 第 71 行; report.md 第 79 行
  - 原句: 历史段事后数字取自相似检索面事后块，按自然月末口径
  - 建议改句(非必修): 历史段事后数字按自然月末口径自冻结序列重算(引擎相似检索面事后块为锚后首个观测口径; 两口径差中位约 0.35 个百分点、最大 1.41 个百分点, 无符号翻转)
  - 说明: NIT-11 口径说明可更明确: 引擎相似检索面事后块为锚后首个观测口径, 受审稿数字按自然月末口径; 两口径差中位约 0.35、最大 1.41 个百分点, 无符号翻转。台账 #874、#686–#687。

### 6.4 引擎面观察(非判断档问题, 不计入裁决, 供操作席参考)

- 台账 #670: 同格严格符号口径(0 不计入任一侧) UST_10Y_1m｜[rc09] 恰为0的事后块在严格口径下不计入一致侧; 受审稿 "其余各窗零点六至零点八" 在两种口径下均成立
- 台账 #861: agent_judgment 的 title 标签字段: 总数 / 逐字出现在任一报告的数量｜[rc10] 
- 台账 #932: evidence_index.json 中 CN_PPI_YOY/CN_CPI_YOY/CPI/EA_HICP_YOY/JP_POLICY_RATE 的引用标签日期 vs series_store 最新观测日｜[rc15] quality_gate_notes[5]④「证据索引对 CN_PPI_YOY、CN_CPI_YOY 的引用标签日期为观测月末(2026-10-31)而序列观测日为月初(2026-10-01)」属实(同一观测两个日期标签, 同月)

## 7 过程留痕

- 全部复算由本席亲自完成, 未委派子代理; 全部脚本以 /usr/bin/python3 -I 运行, 路径作参数传入, 解释器不在数据目录内启动; 只读规程第 1 节列明的只读面, 未读取第 2 节禁止路径, 未联网, 未运行任何写操作命令。
- 席位侧自纠(均不改变任何比对结论, 台账与脚本同步留痕): (a) 早期对 MAP 报告表格的即席核对出现 5 个旗标, 经复查均为席位自身解析伪影(列错位/全半角), 已消除; (b) rc12 一条记录的 note 模板写错, 已更正; (c) 清理 10 条完全重复的台账记录; (d) rc15 两处过严判据更正(#923 日历关键词计数、#930「2026-03 同月大幅跳升」判据); (e) rc16 对 3 条中国 7 天逆回购锚值记录(#450–#452)的 reported 字面与 1 条空 where(#879)作描述性勘误, 勘误前备份 points.jsonl.bak-pre-rc16; (f) rc08 脚本第 192 行与上述口径对齐; (g) 复核中途一次接口速率限制(HTTP 429)中断, 续算前复核受审版本(代码印章、MAP_REPORT sha256、快照 sha256、受审文件修改时间)与中断前一致; (h) 产出草稿阶段剔除了本席预列的一条行文项(情景触发句「自 2026-11 观测月起连续两个月回落」在受审稿同句括注内已自带缺基期说明, 经复核不成立), 未列入问题清单。
- 数字全量清扫(中间结果 mid_rc14_out.txt / mid_rc14b_out.txt): 字符串字段数 447 数字token总数 2504 台账数值集合大小 871; 第二遍 116 行, 未直接命中的仅为日期分量、「3个月前」类时点标签、指数名「标普500」与已核值在别处的重复出现。

## 8 裁决

**UPHELD**——MAJOR 0 条、偏离 0 点。MINOR 与 NIT 如实列于第 6 节与 VERDICT JSON items, 不构成阻断; must_fix 为空数组。

