# 完整研究报告(一键研究 MVP)

- 问题: 中国宏观信用与制造业景气: CN_NEW_LOANS 新增贷款与 CN_PMI_MFG 制造业PMI 对 CHINEXT 创业板指与 FXI 中国大盘股的影响
- run_ok: False | 证据行: 65

## L1 事实层(引擎确定性产出)

| 指标 | 值 | 单位 | 观测日 | 质量 | 证据 ref |
|---|---|---|---|---|---|
| FXI | 33.92 | usd | 2026-11-11 | PASS | FXI@2026-11-11 |
| CHINEXT | 2572.0672 | index_point | 2026-11-11 | PASS | CHINEXT@2026-11-11 |
| CN_PMI_MFG | 49.3 | index_point | 2026-10-01 | WARN | CN_PMI_MFG@2026-10-01 |
| CN_NEW_LOANS | 12734.0 | cny_100m | 2026-09-01 | DEGRADED | CN_NEW_LOANS@2026-09-01 |

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=True n=17 隔离=0
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)
  - VIEW-20261110-001 · International Monetary Fund · 2026-10-13 · World Economic Outlook, October 2026: Resilience Under Strain, Urgent Choices
  - VIEW-20261110-002 · Federal Reserve (Board of Governors / FOMC) · 2026-10-28 · Federal Reserve issues FOMC statement (October 28, 2026)
  - VIEW-20261110-003 · PIMCO · 2026-10-06 · Cyclical Outlook: Growth Holds, Risks Widen
  - VIEW-20261110-004 · Goldman Sachs · 2026-09-23 · Can AI Investment Drive S&P 500 Earnings Even Higher?
  - VIEW-20261110-005 · European Central Bank · 2026-10-29 · Monetary policy decisions (29 October 2026)
  - VIEW-20261110-006 · Bank of Japan · 2026-10-30 · Statement on Monetary Policy (October 30, 2026)
  - VIEW-20261110-007 · World Bank · 2026-07-01 · China Economic Update, July 2026: Rebalancing Growth
  - VIEW-20261110-008 · BlackRock · 2026-11-04 · U.S. midterms: what they mean for investors (Bulletin)
  - VIEW-20261110-009 · Morgan Stanley Investment Management (MSIM) · 2026-09-18 · A Firmer Fed — Global Fixed Income Bulletin
  - VIEW-20261110-010 · International Energy Agency (IEA) · 2026-10-14 · Oil Market Report - October 2026
  - VIEW-20261110-011 · Morgan Stanley Investment Management (MSIM) · 2026-09-22 · Big Picture: Mapping Europe's Barbell
  - VIEW-20261111-001 · 中国人民银行 (People's Bank of China) · 2026-08-12 · 2026年第二季度中国货币政策执行报告(内容摘要)
  - VIEW-20261111-002 · 经济合作与发展组织 (OECD) · 2026-09-23 · OECD Economic Outlook Interim Report, September 2026 — Weathering Successive Shocks (官方新闻稿)
  - VIEW-20261111-003 · 国际清算银行 (Bank for International Settlements) · 2026-09-14 · BIS Quarterly Review, September 2026 — Overview: Yields climb, yet risk appetite holds firm
  - VIEW-20261111-004 · UBS · 2026-11-09 · House View Briefcase: How will Fed rate hikes impact markets?
  - VIEW-20261111-005 · Vanguard · 2026-10-23 · Active Fixed Income Perspectives, Q4 2026: Looking through the fog
  - VIEW-20261111-006 · Morgan Stanley Investment Management (MSIM) · 2026-10-16 · Real Rates Take the Lead — Global Fixed Income Bulletin (Macro Insight, October 2026)

## L3 AI 推断层(Agent 席真产)

- produced=True attribution=ai_inferred
- 判断原文: report.md L3 节 + agent_judgment.json 归档副本

## L4 条件情景层(Agent 席真产)

- produced=True attribution=ai_inferred
- 情景五行齐备面: report.md L4 节 + agent_judgment.json 归档副本

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;
L3/L4 内容归 Agent 席与独立审计,本段不代写。
