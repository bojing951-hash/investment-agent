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
4. **④ 无头自主运行 — 已批准已落地**(2026-11-11 用户放行后 launchd 拉起;
   R5=首个无头自主轮,分支 dev/rd-r5-stage-coverage)。硬边界如方案:
   允许清单禁 push/ssh/curl/npm/pip;合并 main 与付费留用户逐次亲批;
   `~/agent-loop/` 读写在本会话权限面外(如 rounds/index 追加受限=如实记录)。

## 观察钟/日历门

- **F 补证轮**: 2026-12-05 观察钟满,引擎自动触发(勿手工提前)。
- **机构观点六标签**: 全库 INSUFFICIENT(库龄函数),首验窗 2026-12。

## 生产观察(LIVE 面,2026-11-11 部署后登记;同日诊断收口)

- **weekly launchd exit 2 = Gate A 预检拒绝**(既有,非 v0.10.0 回归)。**同日诊断毕**:
  `ZQ_IMPLIED_AVG` 采集已恢复(2026-11-08 热修 60fd169 生效;11-09 起每日快照在场,
  11-11=4.175%),10-31/11-07 两周失败=热修前旧态。四件套依赖(当日快照 Gate A∈
  {PASS,DEGRADED}+data_pack+anchors+anchor_prompt)自 11-08 起逐日产出的当日
  链恢复;**2026-11-11 实测 `verify_research_inputs('20261111')` 预检 PASS**→
  周六 11-14 08:00 weekly 应自动恢复正式周报(首期 v0.10.0 面周报)。零代码改动,
  无需人工动作。
- 残余非核心缺席(11-11 快照 noncore_missing 6 项,Gate A=DEGRADED 如实降级不阻塞):
  BUND_10Y/BUND_2Y(BBK 源站 RemoteDisconnected)、ECB_MRO(ECB 504)、CN_OMO_7D、
  CN_SF_FLOW(社融 SSL 缺席)、JP_CPI_TOKYO_YOY。源端问题如实缺席=设计行为;
  数据缺口台账另行维护(`../P2_DATA_GAP_LEDGER.md`)。

## 技术待办(不阻塞)

- ~~**[R5-D1,P0 观察] CN_CPI_YOY/CN_PPI_YOY 陈旧值被证据引擎采信**~~
  **[R6-D1 已修(2026-11-11,dev/rd-r6-collection-fixes)]**: 采集器 G-P1-15
  金十通道(停更后持续写 2025-08 旧值)→tushare pro 换源: `cn_cpi.nt_yoy`
  **真实拉取验证**(202609=0.9,月末观测日),registry v2.8.0→2.8.1
  (source_symbol 同步);`cn_ppi.ppi_yoy` 源已接线但**本 token 权限档不足**
  (服务端拒,卡点②候选报批项)→ 批前 ppi_yoy 如实缺席,下次快照起
  CN_CPI_YOY 转新鲜。**[R5-D2→R6-D2 已核]** CN_OMO_7D=四路免费源全阻
  (tushare 无接口/央行 502/akshare 零端点/东财 cookie 门)→登记
  source-blocked 不造数(台账 `../P2_DATA_GAP_LEDGER.md` 三之四)。

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
- ~~**[R1 发现] 阶段B 可判面受限: 16 指标快照 facts 缺席**~~ **[R5 已分解收口
  (2026-11-11,dev/rd-r5-stage-coverage)]**: 四类缺陷——①假设引用超出观点 subjects
  映射面+③mode A 事实面截断过杀=引擎覆盖面缺口**已修**(证据面=subjects∪假设
  metric_refs;截断序列尾值近似+DEGRADED 披露;重建 17 份=既有行零变动+新增
  64 行+7 假设 INSUFFICIENT→有判;`audit/R5_STAGE_COVERAGE_INVENTORY.md`);
  ②CPI_YOY 语义层 id 错配+④CN_OMO_7D/BUND_10Y 真缺席=数据面,转台账
  `../P2_DATA_GAP_LEDGER.md` 三之四节(R5-D1/2/3)。
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
