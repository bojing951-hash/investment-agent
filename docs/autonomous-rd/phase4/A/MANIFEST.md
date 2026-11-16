# Phase 4 Task A — 美宏观利率传导(UST_10Y→HY_OAS/SPX)

- 执行: 2026-11-16,操作者席+独立 Agent 研究席(subagent,54 工具调用)
- 入口: `ia_cli.py research-one` 三段式(plan→Agent 席→attach→report)
- 数据根: 引擎树注入(engine_root=~/investment-agent-dev,快照 20261112_v2+
  views 库 17 份)
- 问题: UST_10Y 十年期美债利率上行的宏观传导: 对 HY_OAS 高收益债利差与
  SPX 股市估值的影响

## 链结果

| 段 | 结果 |
|---|---|
| plan | run_ok=True,L1=3 行(SPX 7609.63/HY_OAS 3.34pp/UST_10Y 4.88%),evidence=64 行(47 事实+17 VP) |
| Agent 席 | judgment schema 1.1,attribution=ai_inferred;validate_judgment passed=True 零违规;verify_judgment VERIFIED(23 checks,attach 前自修 3 处契约拦截+R34 判例区间锚定) |
| attach | attached=True,violations=[];report.md 重渲 L3/L4 节 |
| report | **ok=True,L3_produced=True ∧ L4_produced=True(G2 链全绿)** |

## 判断面概要

- L3 矛盾 3: 利率→利差传导条件性(4-8 月利率升利差反收紧,9 月加息月才单月
  走阔 0.49pp)/折现率通道在股票维未兑现(UST_10Y +0.70pp 同期 SPX +11.16%,
  日度相关仅 +0.1067)/HY 复合 vs 分层分裂(CCC +4.26pp ≫ B +0.49 > BB
  +0.31 > IG +0.12)
- 机制链 2(各 E1→E2→E3): 折现率通道(UST_10Y→SPX)/信用溢价通道
  (UST_10Y→HY_OAS 分层)
- L4 情景 2(基准+反例): SCN-A 证伪=HY_OAS 单月走阔 >50bp(自 3.34pp@
  2026-11-09 升破 3.84pp)连续 5 日,时限 2027-03-31;SCN-B 复合证伪(主锚
  UST_10Y 次锚 HY_OAS,v1.1 secondary_metric_ids),时限 2027-06-30
- 证据缺口(E2 假设面): SPX 估值序列缺席(CAPE 止 2026-10/PE_TTM 止 2026-06)/
  HY_OAS×UST_10Y 相关渠道缺(S5 本运行仅 SPX×UST_10Y)/分层领先滞后与违约率
  序列缺/17 份 VP 全 INSUFFICIENT_EVIDENCE(库龄,首验窗 2026-12)

## 工件

入库(本目录): FULL_REPORT.md / report.md / judgment_mvp.json /
AGENT_SEAT_ENVELOPE.json / BIGFILES.sha256
大件(运行目录,sha256 在档): report.json(754KB)/views_digest.json(84KB)/
evidence_index.json/agent_judgment.json
运行目录: /tmp/mvp_run4/20261116T045959Z_UST_10Y_十年期美债利率上行的宏观传导_对_HY_OAS_高收益债利差与_
(tmp 会被系统清理;大件以 sha256 为凭,如需原件由 Phase 4 后续任务
--archive 正式归档重产)
