# OPEN_ISSUES — 未解决问题与阻塞项

> 本档只登记跨顶/研发面事项;专项台账原处维护(指针),防双头:
> 数据缺口 = `../P2_DATA_GAP_LEDGER.md`;历史遗留 = `../REMAINING_ISSUES.md`;
> 轮次合同/审批 = `~/agent-loop/contracts`、`~/agent-loop/PENDING-APPROVALS.md`。

## 用户保留卡点(硬阻塞,须用户亲自批)

1. **① 封版合并 main** — 含章程初始化分支 `dev/autonomous-rd-charter`(未推未并)。
2. **② 新数据源凭证/付费** — HY_OAS 族 = ICE BofA 源端 3 年授权窗,现如实注记,不绕付费墙。
3. **③ LIVE 部署** — 阿里云仍跑 v0.7.1 面,v0.8/v0.9 面升级待批。

## 观察钟/日历门

- **F 补证轮**: 2026-12-05 观察钟满,引擎自动触发(勿手工提前)。
- **机构观点六标签**: 全库 INSUFFICIENT(库龄函数),首验窗 2026-12。

## 技术待办(不阻塞)

- 注册表覆盖: 000300.SH/000905.SH/000852.SH 取回未入,每次快照告警(REMAINING P1-1)。
- 深市全市场成交额精确口径待 Tushare 配额确认(P1-2)。
- 旧锚点无 obs_date 仅影响历史回溯核验(P1-3)。
- series_store 历史深度随采集累积,元旦附近 60 日窗样本不足(P1-4)。
- FRED SP500 偶发近月空段,外部核验已自动回退最近可得日(P1-5)。
- CODEX 外部核验通道 NOT_VERIFIED 现状,能力建设待议。

## 环境注意(非本仓缺陷)

- AI内容库内 `🤖_AI投资项目/每周宏观追踪/investment-agent` = 历史副本,其工作区有未提交
  删除/改动(用户侧遗留)。**勿在其上开发**;权威开发树 = `~/investment-agent-dev`。
