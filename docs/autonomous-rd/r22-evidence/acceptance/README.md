# Audit-R22 任务5 — 全新会话一问验收(隔离环境)

**运行编号: 20261119T153709Z** · 最终裁决: **UPHELD**(零共享上下文独立审查席 Round-1 即通过,约 350 点复算零 MAJOR;1 MINOR+2 NIT 在档记录不阻断)·
归档 content_sha256 = `cd3e173213a53c3e79cf…`(ARCHIVE_MANIFEST = 裁决档 = 登记摘要三处逐位一致)

## 验收协议(按指令)

- **运行代码**: commit `b45b810f92e3a44a4c40064e67910a948ebbb36d`(先提交修复代码,再从该干净提交起会话;CODE_VERSION.json 印章绑定)
- **隔离目录**: `/tmp/r22` = 该提交 `git archive` + 20261119 通道面;快照由该提交代码在通道面上自建;**零同题归档**(仓内 8 件旧档全为其他问句,未读、未触)
- **全新会话**: 独立零上下文判断席(Seat-A 子会话)只收到 `run_question_verbatim.txt` 原文一次+程序性规程(走正式入口/独立复核/必要修订/归档;零研究内容指示);原文与 R21 原工单 run.question 逐字节一致(sha256 前 16=409eef0c8cec2aa0)
- **现有入口**: 全链经 `ia_cli.py research-one`(plan → AGENT_SEAT_ENVELOPE → attach → report → archive),判断内容 100% 由判断席基于工单证据生成
- **attach 契约**: 3 轮迭代——第 1/2 轮 blocked=contract_contradicted(正文内嵌序列 ID 数字 CN_OMO_7D/UST_10Y/TIPS_10Y/BEI_10Y 的 7/10 被扫描器当裸数字绑邻面值),判断席改正文表述后第 3 轮全 VERIFIED(0 contradicted/0 unbound/0 map_fail/0 six_fail)
- **独立复核**: 判断席规程文件零判断内容;审查席(VSCode claude 二进制,独立进程,只读)复算约 350 点 → **UPHELD**(Round-1);MINOR=政策一年窗净变动基点口径(引擎渲染面,公式内联披露+事件全列);NIT×2=JP_CPI 2.35 舍入边界/JP 月均亚基点取整。经引擎公开接口 record_semantic_verdict 登记 revision=1
- **溯源**: report.run.git_head = MAP_REPORT 头「代码: b45b810f…」= ARCHIVE_MANIFEST.run_code_git_head 三处同值(印章源=code_version_stamp)

## 交付物(20261119T153709Z_…/)

九件套+verdicts: AGENT_SEAT_ENVELOPE / ARCHIVE_MANIFEST / FULL_REPORT / **MAP_REPORT(读者版)** / MAP_REPORT.sha256(对账一致) / agent_judgment / evidence_index / report.json+md / verdicts(20261120__VERDICT-20261119T153709Z-01.json,UPHELD rev=1)。

## 读者面新件(R22 任务4,实测在文)

- 首页三件: 一句总判断(年度美债分解打头: Δ+97bp=实际+104bp+盈亏平衡−7bp,窗 2025-11-17..2026-11-17)+四地三时点表+证据最充分传导速览(区分指标观测在场评分)
- 主解释 vs 竞争解释对质表(main_predicts/competing_predicts/face_off_verdict;预期未分立=尚不能区分诚实缺省)
- 政策口径四分面: 决议日≠生效日分记(Fed 次日×3 例含 2022-07 决议 07-27→生效 07-28 七月末上限 2.50;ECB 决议后首个周三;PBOC 即时)+跨国政策事件簇(Fed 09-16+ECB 09-10 合并=同一全球政策事件,逐事件决议→生效间隔 1/6 日)+FOMC 十月纪要 11-18 发布可见
- 关键数字表带实际观测日+发布日期+**发布批次**(BLS-CPI-2025M09-REL 同批 CORE_CPI+CPI@2025-09 对账)+修订口径注记
- 历史类比逐窗并列面(经济指标×资产,起止期/数值/单位/来源;随后 N 月=锚+N 方向修正后口径)

## 36 格覆盖

research_plan.point_values: 22 指标×3 锚=66 格,**63 ok + 3 诚实缺席**(可见性门如实);**12 组×3 锚=36 核心格全覆盖**(recheck_36cells.py 23/23 PASS)。
