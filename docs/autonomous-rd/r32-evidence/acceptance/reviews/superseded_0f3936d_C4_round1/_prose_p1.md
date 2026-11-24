# Audit-R32 正式使用验收 · 工单 C4 · 独立语义审查席位 · Round-1

- 席位: semantic-audit-seat（reviewer = independent-zero-context-seat-r32-c4-round1）
- 裁决词: **REVISE**
- 复算计数: recompute_points = 297，recompute_mismatches = 3（MAJOR 1 条、MINOR 2 条）
- MAJOR 条数: 1
- 另有「引擎面自洽 / 渲染观察 / 对照事实」7 项检查，按规程不计入判断档的命中与偏离计数（其中渲染观察 2 项，见第 8 节）
- 审查日期: 2026-11-24
- 规程: /tmp/r32-accept/review4/C4_round1/_protocol.md
- 配套裁决档: /tmp/r32-accept/review4/C4_round1/VERDICT-round1.json

## 1. 程序性声明

1. 只读: 受审运行目录、隔离安装树、冻结输入未写入、未移动、未删除任何文件。本席位全部脚本、中间产出与两件产出只写在 /tmp/r32-accept/review4/C4_round1/ 下。
2. 未联网；未运行 ia_cli.py 的任何子命令（写操作与只读子命令均未运行）；未调用 agent_judgment.record_semantic_verdict。
3. 未读取规程第 2 节列出的任何目录（树内 docs/、/tmp/r32-accept/out/、/tmp/r32-accept/scripts/、/tmp/r32-accept/replay/、/tmp/r32-accept/install*、/tmp/r32-accept/final*（只读安装树本体除外）、其他运行目录、/tmp/r32-accept/review/、review3/、review4/ 下本席产出目录以外的目录、research_archive/、~/investment-agent-product）。未与研判席、其他席位、操作者通信；未索取、推测或依赖任何预审内容；未委派子代理，全部复算由本席亲自完成。
4. 复算方式: 自写脚本以 `/usr/bin/python3 -I <脚本> <路径参数…>` 运行，路径全部作参数传入；本轮没有调用树内引擎模块，也没有使用隔离安装树的解释器。
5. 主脚本与运行命令（工作目录取中性目录 /tmp）:
   - 脚本: /tmp/r32-accept/review4/C4_round1/s10_recompute.py
   - 命令: `/usr/bin/python3 -I /tmp/r32-accept/review4/C4_round1/s10_recompute.py <快照 research_snapshot_20261123.json> <report.json> <root_overlay/config/release_calendar.json> <root_overlay/config/metric_registry.json> <agent_judgment.json> <evidence_index.json> <AGENT_SEAT_ENVELOPE.json> <MAP_REPORT.md> <FULL_REPORT.md> <report.md> out_s10_table.txt out_s10_summary.json out_s10_appendix.txt`
   - 旁证脚本: s14_vintage.py（锚格修订口径）、s15_confirm.py（三条偏离的独立复算，不依赖主脚本辅助函数）、s16_engine_obs.py / s17_contract_probe.py / s18_sr_probe.py / s19_p6_check.py（第 8 节引擎面观察的事实核对）、s20_num_check.py（第 7 节问题清单所引数字的独立回贴）。
   - 辅助脚本（不接触证据面）: s21_redact.py（席位自有中间产物里的环境键名与厂商兼容语遮蔽）、s22_verdict.py（按规程第 6 节生成裁决档，计数与偏离明细读自 out_s10_summary.json）、s23_assemble.py（装配本件）。早期探查脚本 s00–s13 及其输出 out_s01–out_s13 同目录留存。
   - 输出: out_s10_table.txt（逐点清单）、out_s10_summary.json（计数与偏离明细）、out_s10_appendix.txt（情景真值表、契约、数值溯源普查）。
6. 口径约定:
   - series_store 序列值保留 4 位小数，派生同比容差 0.0006。
   - 月频序列以 YYYY-MM-01 为键；中国月度事实的引用标签为月末（如 CN_CPI_YOY@2026-10-31），取值按「精确日 → 同月回退」处理。
   - 锚格规则: 取锚日当日或之前已发布的最新观测；发布日按注册表规则、冻结日历实录、引擎政策事件簇分别复算。
   - 美国三利率恒等式: 名义 = 实际(TIPS_10Y) + 盈亏平衡(BEI_10Y)，窗口取三者共同交易日。
   - 资产窗两口径: 引擎窗 = 2026-10-23 → 各序列末观测（2026-11-23 为盘中快照；NIKKEI225 止于 2026-11-20 收盘）；收盘口径 = 2026-10-23 → 2026-11-20。
   - 「相近」的判定尺度采用判断档自身在传导第 3 环给出的尺度: 美中落差 1.40 个百分点被称为「落差不足两个百分点、排序弱化」。
7. 本席未能核实、因而不作认定的事项:
   - 美国决议日 2026-09-16: 冻结日历无美国政策条目，只能核对「生效日前一日」推定规则与 DFEDTARU 变更日 2026-09-17。
   - 类比面: 只核 TOP-5 的距离与份额恒等、覆盖率、排序键与计数自洽（1871 − 1785 − 74 = 12），未独立重扫 1871 个候选月。
   - 「日本 2026-11-23 休市」: 判断档已自标未经本轮证据面核实，本席同样无法核实。

## 2. 受审对象

运行目录（只读）: /tmp/r32-accept/final4-degraded/output/research_runs/20261123T193254Z_2026年11月_美_欧_中_日四地的宏观环境相比三个月前_哪些经济体之间出现了

- 判断档: agent_judgment.json 全文（quality_gate_notes 10 条、L3 四条矛盾陈述 C1–C4、两条机制链 M1/M2、L4 两个情景、reader_map）。
- 读者报告中的判断文字: MAP_REPORT.md（304 行）、FULL_REPORT.md、report.md。
- 只读证据面: root_overlay/data/daily/research_snapshot_20261123.json（series_store 88 条序列、facts、gate_a、quality、sources_status）、report.json 引擎面（research_plan.point_values 35 锚格、us_rates_trio、asset_moves、turning_candidates、policy_doc_facts、policy_event_clusters、steps 信封、契约验证 17 判定）、evidence_index.json（69 行）、AGENT_SEAT_ENVELOPE.json、root_overlay/config/release_calendar.json（v1.5.0，18 条）、root_overlay/config/metric_registry.json。

## 3. 复算覆盖与结果总览

计数点 297（规程最低 90），偏离 3。逐点清单见附录 A（出处键 / 直算值 / 报告值 / 一致与否）。按类别:

| 类别 | 点数 | 偏离 |
|---|---|---|
| ① 截止日（含时区 4 点） | 10 | 0 |
| ⑫ 盘中标签 | 3 | 0 |
| ② 锚格值 / 回贴 / 发布纪律 / 公布口径分类 | 108 | 0 |
| ③ 同比基期 | 23 | 0 |
| ④ 政策面（含日历 6、来源 3、披露 1、四口径 1、决议日 1） | 28 | 1 |
| ⑤ 利率窗（含恒等式 2、最新值 3） | 12 | 1 |
| ⑤ 资产窗（引擎窗 8、收盘口径 7、盘中 3、最新值 1、排序 2、美日相近 1） | 22 | 1 |
| ⑩ 渲染（C4 陈述进入读者面） | 1 | 0 |
| ⑥ 转折候选与取舍（含补选 1） | 23 | 0 |
| ⑦ 证据引用与证据分级 | 4 | 0 |
| ⑪ 诚实缺席 | 14 | 0 |
| ⑧ 历史类比（零段） | 13 | 0 |
| ⑨ 情景 | 8 | 0 |
| ⑩ 读者面 | 16 | 0 |
| ⑬ 契约 | 3 | 0 |
| ⑭ 交付门 | 4 | 0 |
| ⑮ 开放问句 | 5 | 0 |
| 合计 | 297 | 3 |

不计入的 7 项: 引擎面自洽 3 项（TOP-5 距离与份额恒等、Σ权重×覆盖率 = 0.541667、d12m 三特征）全部一致；引擎面渲染观察 2 项（转折 narrative 0/3 进入 MAP 与 FULL；十项质量门口径注记 0/10 进入三份报告，见第 8 节）；对照事实 2 项（转折先后、锚格修订口径，见第 5.8 节与第 7 节）。

说明: 逐点均先从 series_store、冻结日历、report.json 引擎面直算，再与判断档文字比对；不采信判断档转述。数值溯源普查另扫出判断档文字中 24 个阿拉伯数字未被机器归入已知来源池，已逐个人工溯源，全部可回贴到序列值或引擎面（9.98、84.52、42.13、40.66、2.5658、0.9571、2.3904、19.45、35.89），无一存疑。
