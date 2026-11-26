# Audit-R21 任务5 — 全新会话一问验收(隔离环境)

**运行编号: 20261119T120815Z** · 最终裁决: **UPHELD**(裁决链两轮: 首轮 REVISE[4 MAJOR+5 MINOR+4 NIT] → Agent 席修订 13 处 → 复裁 UPHELD;两轮全文存 verdicts/PROSE-20261119T120815Z-01.md)·
归档 content_sha256 = `5916b8dc72ff018ec80afd4bda1c17b2f85024f7b33e1e4675285585501a0103`

## 验收协议(按指令)

- **运行代码**: commit `9667e8df0be26513be6eb85d1041711f4f130d16`(先提交修复代码,再从该干净提交起会话)
- **隔离目录**: `/tmp/r21_accept` = 该提交 `git archive` + 20261119 通道 + pboc 缓存,快照由该提交代码在通道面上自建(CN_OMO_7D 201 观测零值根修+CN_POLICY_OVERNIGHT 14 观测断言过);**零同题归档、零预填判断**(research_archive 空、r17/r18/r19/r20-evidence/phase4/cn-task-b 历史运行档全部不入场)
- **全新会话**: 独立 headless Claude Code 会话(独立进程独立上下文),只收到 `run_question_verbatim.txt` 原文一次+程序性规程(走正式入口/独立复核/必要修订/归档;零研究内容指示)
- **现有入口**: 全链经 `ia_cli.py research-one` 现有入口(plan → AGENT_SEAT_ENVELOPE → attach → report → archive),判断内容 100% 由 Agent 席基于工单证据生成
- **独立复核**: 零共享上下文审查席复算(22 格三时点锚值/同比派生/政策事件日期逐位对照 ia_cli history 原值+三段历史类比 45 个事后数字按锚月末→锚+N 月复算);首裁抓出 4 MAJOR(近一月利率分解符号自相矛盾/2025-03 中国 PPI 贴错月/查询截距冒充序列起点/2022-06 CAPE z 误引)→修订 13 处→复裁 UPHELD(13 项处置逐条过,新文本复算一致,审查席自正其首轮 JP_POLICY_RATE 起点截距伪影)
- **契约**: attach 迭代三轮,曾拦截 6 处数值口径错误,终态 VERIFIED

## 归档九件套

`20261119T120815Z_…/`: AGENT_SEAT_ENVELOPE / ARCHIVE_MANIFEST / FULL_REPORT / **MAP_REPORT(读者版)** / MAP_REPORT.sha256 / agent_judgment / evidence_index / report.json+md / verdicts。三方核对: manifest=verdicts=裁决锚 均 UPHELD@5916b8dc。

## 36 格覆盖表

research_plan.point_values: 22 指标×3 锚=66 格,**63 ok + 3 诚实缺席**(CN_POLICY_OVERNIGHT 12m/3m=锚前无发布观测、JP_CPI_TOKYO_YOY 12m=锚前无发布观测,均为可见性门如实输出);**12 组(4 地区×3 维度)×3 锚=36 核心格全覆盖**。
