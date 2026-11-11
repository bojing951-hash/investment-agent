# OPEN_ISSUES — 未解决问题与阻塞项

> 本档只登记跨顶/研发面事项;专项台账原处维护(指针),防双头:
> 数据缺口 = `../P2_DATA_GAP_LEDGER.md`;历史遗留 = `../REMAINING_ISSUES.md`;
> 轮次合同/审批 = `~/agent-loop/contracts`、`~/agent-loop/PENDING-APPROVALS.md`。

## 用户保留卡点(状态更新: 2026-11-11「全部审批通过」)

1. **① 封版合并 main — 已批准已执行**(be8dabd+tag v0.10.0-alpha+Release 441746111+
   CI 43030767965 绿=基线 128)。后续波次合并仍逐次请批。
2. **② 新数据源凭证/付费 — 原则获批**,无即需项;实际采购按需逐次报批
   (HY_OAS 族 = ICE BofA 源端 3 年授权窗,现如实注记,不绕付费墙)。
3. **③ LIVE 部署 — 已批准已执行**(2026-11-11 v0.10.0 面;注: LIVE 实为本地 Mac
   launchd 树,非阿里云——阿里云无 investment-agent 部署,只有 coin监控旧系统)。
4. **④ 无头自主运行 — 已批准,落地受阻待放行**: 启动器提示词文件写入被会话权限
   分类器拦([Create Unsafe Agents] 类别)。方案定稿待用户在场放行: launchd 每 4h
   拉起 `claude -p` 单轮(读本目录 RESUME/PRODUCT_GOAL/RUN_MANDATE)+STOP 文件
   急停+`--max-budget-usd` 界+允许清单(仓库内读写/python3/git 本地)禁
   push/ssh/curl/npm/pip;合并 main 与付费仍留用户逐次亲批。

## 观察钟/日历门

- **F 补证轮**: 2026-12-05 观察钟满,引擎自动触发(勿手工提前)。
- **机构观点六标签**: 全库 INSUFFICIENT(库龄函数),首验窗 2026-12。

## 生产观察(LIVE 面,2026-11-11 部署后登记)

- **weekly launchd exit 2 = Gate A 预检拒绝**(既有,非 v0.10.0 回归): 核心指标
  `ZQ_IMPLIED_AVG` 采集缺席 → Gate A FAIL → 周报链按设计拒绝生成正式档
  (10-31 与 11-07 两周同因)。排查=RESUME R5 候选③(定位采集通道,修通或如实登记;
  不得为过门造数)。关联旧案: 2026-11-08 生产事故(rate_expectations 429→ZQ 空→
  Gate A 拒),当时热修 60fd169 已并入本面——需查该指标当前是否复现同类源端问题。

## 技术待办(不阻塞)

- **[R2 审计 MINOR-4] S9 与 Skill 第 9 步错位**: 编排器 S9=views lint+VP 装载,
  Skill 第 9 步=解释标注(四层+竞争解释)——现为确定性替身,补作 Agent 落位时对齐。
- **[R1 审计 MINOR-4] vintage 二次过滤缺失**: vintage 路径信任 vintage 快照,无 obs≤publish
  二次过滤(快照若含未来观测即漏);今日干净——vintage 累积落地时一并加护。
- **[R1 审计 MINOR-5] lineage 链坍缩**: 反复重建使 `prior_generated_by` 第二次起指向 build_vp
  自身,原始编排层署名丢失;v1.0 基底被原地覆盖+data/ 不入库不可恢复——重建时保留首代署名。
- **[R1 审计 MINOR-6] since_publish 基准语义**: 名义"严格>publish"实际基准=严格早于 publish
  的最后观测(含 publish 当日变动);"无新观测"(basis==end)与"净变动0"混报同 note——
  拆分两种如实注记。
- **[R1 审计 MINOR-7] validate_vp 不复核行内容**: 只做结构+聚合校验,不复核 stages 行与引擎
  重算一致(伪造自洽行可通过装载);信任边界=写入方,幂等可重建部分缓解。
- **[R1 审计 MINOR-8] B面描述性陈述语义激进**: 对既成事实类陈述("已引发…")判 CONTRADICTED
  易被误读为预测失败;证据评价语义已披露,考虑描述性行单独标注。
- **[R1 发现] 阶段B 可判面受限**: forecast_target_map 对齐后 16 个指标在快照 facts 缺席
  (观点引用→数据面映射覆盖缺口),对应假设阶段面 INSUFFICIENT——数据覆盖轮处理(勿手工造数)。
- **[R1 发现] 阶段A vintage 累积**: 采集档无历史 vintage,现用最新快照截断近似(DEGRADED
  如实标注);自 R1 起逐快照累积 vintage 后可转精确锚。
- 注册表覆盖: 000300.SH/000905.SH/000852.SH 取回未入,每次快照告警(REMAINING P1-1)。
- 深市全市场成交额精确口径待 Tushare 配额确认(P1-2)。
- 旧锚点无 obs_date 仅影响历史回溯核验(P1-3)。
- series_store 历史深度随采集累积,元旦附近 60 日窗样本不足(P1-4)。
- FRED SP500 偶发近月空段,外部核验已自动回退最近可得日(P1-5)。
- CODEX 外部核验通道 NOT_VERIFIED 现状,能力建设待议。

## 环境注意(非本仓缺陷)

- AI内容库内 `🤖_AI投资项目/每周宏观追踪/investment-agent` = 历史副本,其工作区有未提交
  删除/改动(用户侧遗留)。**勿在其上开发**;权威开发树 = `~/investment-agent-dev`。
