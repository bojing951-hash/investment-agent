# 完整研究报告(一键研究 MVP)

- 问题: 2026年11月,美、欧、中、日四地的宏观环境相比三个月前,哪些经济体之间出现了明显分化?分化主要体现在哪些维度?请给出具体数据和各数据的公布时间,并说明哪些维度证据不足以下结论。
- run_ok: True | 证据行: 46 | run.ts_utc: 20261121T074415Z

## L1 事实层(引擎确定性产出)

| 指标 | 值 | 单位 | 观测日 | 质量 | 证据 ref |
|---|---|---|---|---|---|

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=False n=None 隔离=None
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)

## L3 AI 推断层(Agent 席真产·全文内联)

- produced=False attribution=None
- (未落位: 判断原文不在场,见 report.md/agent_judgment.json)

## L4 条件情景层(Agent 席真产·全文内联)

- produced=False attribution=None
- (未落位: 情景原文不在场,见 report.md/agent_judgment.json)

## 证据索引

| # | kind | ref | 说明 |
|---|---|---|---|
| 1 | s3_envelope | SPX@2026-11-20 |  |
| 2 | s3_envelope | NDX@2026-11-20 |  |
| 3 | s3_envelope | RUT@2026-11-20 |  |
| 4 | s3_envelope | SHCOMP@2026-11-20 |  |
| 5 | s3_envelope | SZCI@2026-11-20 |  |
| 6 | s3_envelope | CHINEXT@2026-11-20 |  |
| 7 | s3_envelope | HSI@2026-11-20 |  |
| 8 | s3_envelope | HSCEI@2026-11-20 |  |
| 9 | s3_envelope | NIKKEI225@2026-11-20 |  |
| 10 | s3_envelope | DAX@2026-11-20 |  |
| 11 | s3_envelope | CAC40@2026-11-20 |  |
| 12 | s3_envelope | VIX@2026-11-20 |  |
| 13 | s3_envelope | NVDA@2026-11-20 |  |
| 14 | s3_envelope | AAPL@2026-11-20 |  |
| 15 | s3_envelope | MSFT@2026-11-20 |  |
| 16 | s3_envelope | TLT@2026-11-20 |  |
| 17 | s3_envelope | IEF@2026-11-20 |  |
| 18 | s3_envelope | SHY@2026-11-20 |  |
| 19 | s3_envelope | HYG@2026-11-20 |  |
| 20 | s3_envelope | LQD@2026-11-20 |  |
| 21 | s3_envelope | DXY@2026-11-20 |  |
| 22 | s3_envelope | EURUSD@2026-11-20 |  |
| 23 | s3_envelope | GBPUSD@2026-11-20 |  |
| 24 | s3_envelope | USDJPY@2026-11-20 |  |
| 25 | s3_envelope | USDCNY@2026-11-21 |  |
| 26 | s3_envelope | GOLD_F@2026-11-20 |  |
| 27 | s3_envelope | SILVER_F@2026-11-20 |  |
| 28 | s3_envelope | WTI_F@2026-11-20 |  |
| 29 | s3_envelope | BRENT_F@2026-11-20 |  |
| 30 | s3_envelope | GLD@2026-11-20 |  |
| 31 | s3_envelope | USO@2026-11-20 |  |
| 32 | s3_envelope | EEM@2026-11-20 |  |
| 33 | s3_envelope | EZU@2026-11-20 |  |
| 34 | s3_envelope | FEZ@2026-11-20 |  |
| 35 | s3_envelope | EWU@2026-11-20 |  |
| 36 | s3_envelope | EWG@2026-11-20 |  |
| 37 | s3_envelope | EWJ@2026-11-20 |  |
| 38 | s3_envelope | INDA@2026-11-20 |  |
| 39 | s3_envelope | FXI@2026-11-20 |  |
| 40 | s3_envelope | BTC@2026-11-19 |  |
| 41 | s3_envelope | HY_OAS@2026-11-19 |  |
| 42 | s3_envelope | BB_OAS@2026-11-19 |  |
| 43 | s3_envelope | B_OAS@2026-11-19 |  |
| 44 | s3_envelope | CCC_OAS@2026-11-19 |  |
| 45 | s3_envelope | IG_OAS@2026-11-19 |  |
| 46 | s3_envelope | HY_IG_DIFF@2026-11-19 |  |

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2022-06 | 0.937493 | 0.0 | rates 37.0%、volatility 30.8% |
| 2 | 2025-03 | 0.971202 | 1.3699 | volatility 67.6%、rates 22.8% |
| 3 | 2020-10 | 1.288514 | 28.7671 | rates 88.6%、valuation 5.3% |
| 4 | 2023-10 | 1.298078 | 32.8767 | volatility 73.7%、valuation 14.0% |
| 5 | 2019-10 | 1.694433 | 94.5205 | volatility 41.1%、rates 35.1% |

> 相似≠因果, 更非预测: TOP-N 是历史状态距离最近的时期, 当时之后的演变只是历史记录
> 特征为最新修订口径的描述性对齐, 不代表当时市场信息集(research_mode_gate)
> 距离分位=该候选在全部有效候选中的相对位置, 不是概率


## 质量状态(Audit-R1 F02 四态+Audit-R2 绑定面+Audit-R4 贯通面)

- generated: true(FULL_REPORT 完整装配: L1+L2+L3/L4 全文内联+证据索引)
- machine_verified: False(L3∧L4 produced+纪律校验过+底座非降级或 optional 级显式降级随档)
- run 门(Audit-R4 条目5): blocked_class=critical_zero_evidence degraded_ok=False
- review: required=False seat_invoked=False verdict=None fresh=None error=None 修订链档数=0
- copies_consistent(多副本一致): True(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前确定性装配)
- deliverable(可交付): False
- 内容绑定(Audit-R4 条目2): content_sha256=canonical(report.json 剥离 semantic_review)+canonical(agent_judgment.json)+canonical(views_digest.json)——机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。
