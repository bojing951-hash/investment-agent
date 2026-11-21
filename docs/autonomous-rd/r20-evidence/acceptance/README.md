# Audit-R20 任务4 — 全新会话一问验收(隔离环境)

**运行编号: 20261119T060058Z** · 最终裁决: **UPHELD**(裁决链 2 档: -01 REVISE → 修订 → -02 UPHELD) ·
归档 content_sha256 = `5b1d1fddef8de97fc390f69f03aa769a61503211f9ae2fca8e3425587de4c3c2`

## 验收协议(按指令逐条)

- **隔离目录**: `/tmp/r20_accept` = 修复后代码副本 + 最小数据面(channels/引擎数据树副本),
  **零同题归档、零预填判断**——目录内无 research_archive、无既有 MAP_REPORT、无 judgment 草稿。
- **全新会话**: 独立操作者会话(非本审计会话)只收到 `run.question` 原文一次
  (run_question_verbatim.txt,与归档 report.json 的 run.question 逐字一致),无其他指示。
- **现有入口**: 全链经 `ia_cli.py research-one --stage auto/--stage archive` 现有入口完成,
  零新脚本介入判断环节;judgment 由 AGENT_SEAT_ENVELOPE 席生成,attach 契约 VERIFIED。
- **独立复核**: 独立语义审查席(独立上下文)读 FULL_REPORT+series_store 复算约 180 数;
  首裁 REVISE 四必修 → 操作者修订正文四处 → 契约重挂 VERIFIED → 复裁 UPHELD(rev=2)。
- **归档**: deliverable=true 后 `--stage archive` 直归,九件套+verdicts/ 落 research_archive。

## 裁决链

| 档 | overall | 绑定摘要 | 时间 | 要点 |
|---|---|---|---|---|
| VERDICT-…-01 (rev=1) | REVISE | d5ab6897… | 06:39:11Z | 抽核约 180 数全对;必修4: ①INDPRO 低点月错(实为 2026-03=0.6861,文写 2026-02) ②CN PMI 荣枯线表征不实(多月在 50 上方非单调,仅三锚格<50) ③BEI 日期-数值错置(11-18 实测 2.19,2.21 为 11-17 窗末日) ④共同交易日计数 10→22(10=最近清单长度) |
| VERDICT-…-02 (rev=2) | UPHELD | 5b1d1fdd… | 06:46:45Z | 四必修逐位复算吻合;50 锚值+三利率分解+8 资产回报+事后窗回归抽查零漂移;无新增越位 |

修订仅改正文四处事实表述,结构化字段未动——旧裁决 -01 因内容摘要变化自动过期(fresh=false),
链上 -02 为现行有效裁决,与归档摘要三处核对(run=归档=裁决锚)一致。

## 新 MAP_REPORT.md 逐项检查(指令五项)

1. **首页总判断**: 一句总判断点名 2026-Q2 全球再通胀转折(中国 PPI −0.9→3.9→5.7、
   美国 CPI 2.434→4.1666)、政策三紧一松、共同交易日分解、三段历史类比——首屏可读。
2. **四地对照表**: 四地三时点环境对照 22 行,12 组×3 锚全覆盖,逐格数值/单位/观察月;
   缺数格带说明+检索范围(东京都 12 个月前格、JP_POLICY_TARGET 诚实缺席);仅最新修订值
   来源标 Δ事后回顾;关键数字与来源表另列实际观测日+发布日期(日历实录/规则推定分标)。
3. **传导图**: 5 环文字传导链(中国生产端再通胀→美欧通胀→央行再紧缩→实际利率→资产重定价),
   逐环=引擎事实+因果假设+竞争解释+能区分解释的指标;修订后 BEI 三日分挂正确。
4. **三个转折**: 按日期表(2026-02 INDPRO / 2026-05 CN_PPI / 2026-05 CPI),每行前值→后值+
   谁先变+跟进/背离;修订后 INDPRO 低点=2026-03(0.6861)与三月窗终点分层表述;
   引擎确定性候选面九行折叠在档。
5. **历史事后表现**: 三段(2025-03/2022-06/2023-10),各含相似点/关键差异/其他经济体是否同步/
   随后 3-6-12 月资产+经济面;修正确认 2022-06 段 −6.27% 等事后窗与引擎事后面逐位一致。

## 诚实披露(隔离面已知缺口)

隔离数据面未携 rate_economy 通道 → Gate A core_missing 6 项披露放行(缺 HIGH_YIELD_SPREAD 族),
judgment 与正文均未引用该族数值;正式引擎数据树(冒烟面)该族在场。入口路径实测修一处:
数据树无快照时 orchestrator 截止日回退曾产 `20261119T0`(紧凑时间戳切片非日期)致
`int('T0')` 崩,已改真 ISO 日期回退(修复表 F5 外补,见 AUDIT_R20_REPORT §七)。

## 文件清单

- `run_question_verbatim.txt` — 用户侧唯一输入(run.question 原文)
- `run/` — 归档九件套(AGENT_SEAT_ENVELOPE/FULL_REPORT/MAP_REPORT+sha256/agent_judgment/
  evidence_index/report.json/report.md/views_digest)+ ARCHIVE_MANIFEST + verdicts/(双档)
- `semantic_review/` — 裁决链双档(-01 REVISE / -02 UPHELD,append-only,predecessor 链)
