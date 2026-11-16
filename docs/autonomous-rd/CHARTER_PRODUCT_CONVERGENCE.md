# CHARTER — Product Convergence(产品能力收敛与一键研究MVP验收)

> 用户总指令原文接收于 2026-11-16 晨(本档为登记件,原文以用户指令为准)。
> 任务名: **Product Convergence — 产品能力收敛与一键研究MVP验收**。
> 唯一核心成功标准: **真实产品能力经过独立验证**(不以版本号/Commit 数/测试数/轮次数为标准)。

## 一、最终产品目标依据

`PRODUCT_GOAL.md`(AC1-AC10,§八)为最高目标,不得缩小、不得降阈值。`FINAL_ACCEPTANCE.md` 现矩阵(2026-11-12 用户落章: 九 PASS+AC3 PARTIAL 日历门)是既有资产,本章程不修改该矩阵——本章程增设 **G0-G4 MVP 门**(下文),两套并存: AC=最终目标全景,G=本轮 MVP 验收。

## 二、本轮 MVP 范围

美/中+相关全球金融资产完整宏观研究闭环(增长/通胀/就业/货币政策/利率曲线/信用/汇率/股市/大宗)。优先验证流程真工作,不求指标补齐。其他经济体=后续扩展。

## 三、架构(保留现有基础)

```
USER QUESTION → RESEARCH PLANNER → DATA & EVIDENCE → DETERMINISTIC RESEARCH
→ AGENT REASONING → VERIFICATION → DELIVERY
```
复用: 采集器/指标注册表/快照/机构观点库/追溯系统/research_contract/ia_cli research-run(确定性)/research-attach(Agent Native L3/L4 落位)/analog 引擎/周报与工作台。禁新增第二套管理系统。

## 四、工程硬约束(Policy as Code + Protected Acceptance + Independent Evaluation)

1. **目标完整性检查**(G0): PRODUCT_GOAL/FINAL_ACCEPTANCE/ACCEPTANCE_CRITERIA 哈希登记+CI 校验未授权变更;变更须用户批准。仓库内哈希≠真权限保护——外部权限项明确列「待用户授权」。
2. **Git/CI 约束**: main 保护/Ruleset/必需检查=外部权限项,先备好可自主配置件+报告唯一需用户操作清单;CI 文件存在≠强制门。
3. **验收隔离**: Development Tests(tests/)/Regression(历史故障回归)/Product Acceptance(净克隆从可信基线跑)/Independent Evaluation(独立席)。
4. **复杂度增长控制**: 禁无必要新增框架/系统/重复模型;新增须证明不可复用;登记成本。本轮不瘦身,只产 `CODEBASE_SIMPLIFICATION_BACKLOG`(DEFERRED)。

## 五、阶段

- **Phase 0** 现状审计(产出=PRODUCT_CONVERGENCE_PHASE0_AUDIT.md: 能力真值表+基线证据)
- **Phase 1** 工程硬约束落地(目标完整性守卫+验收隔离runner+CI保护准备件+复杂度基线)
- **Phase 2** 关键验证修复(research_contract/data_validator/report_generator/agent_judgment;真实周报误报——**与引擎席 R44 A 族碎片泄漏硬化分工: 引擎修检查器,本席接手残余评估+新旧Gate B并行框架**;结构化断言→确定性验证→渲染为主,自由文本为辅)
- **Phase 3** 一键研究 MVP 单入口(自然语言→规划→research-run→Agent L3/L4 真生成→research-attach→验证→完整报告;复用 Agent Native/Skill,**L3/L4 必须真 produced,禁改 produced 字段造假**)
- **Phase 4** 三项真实任务(A 美宏观+利率传导/B 中国宏观+信用股市传导/C 跨经济体跨资产)+至少一项**盲测**(独立验收者选未优化问题;无真隔离条件则如实标注,不称盲测通过)
- **Phase 5** 独立审计(独立席读码/复算/找反例/查假L3L4;同Agent换名≠独立;无真独立环境标 NOT_VERIFIED)
- **Phase 6** G0-G4 验收+持久化
- **Phase 7** 简化 backlog(只登记不执行)

## 六、G0-G4 验收门(开发前固定,禁降标)

- **G0 Engineering Integrity**: 标准测试执行无隐藏错误/CI 可复核/目标与验收契约未擅改/研发状态与 Git 一致/净环境可跑核心系统。
- **G1 Financial Correctness**: 数值/时间口径/单位正确;无未披露前视;已知正确报告不误杀;错误数据能拦;未验证事实不放行。
- **G2 Complete Research**: 一次自然语言输入实际完成数据+机构观点+历史研究+L3推理+L4情景+完整报告。
- **G3 Research Quality**: 关键数值可独立复算/观点可追溯/解释有证据支持/存在竞争性解释/反对证据被处理/情景可证伪。
- **G4 Real-World Acceptance**: 三项真实任务(如上)+至少一项独立选定的未优化问题。

失败处理: 存证据→根因→最小修复→回归→重跑真实研究→再独立审计。禁改验收标准制造通过。

## 七、研究质量十二问(每份完整研究必答,§7.5)

发生什么/为何/关键驱动/机构怎么看/机构依据/证据支持反对/历史可比/传导机制/市场已计价什么/预期差在哪/什么改变判断/什么推翻结论。答不出=明确披露,禁编造。

## 八、权限边界(本轮从严)

用户授权=现有开发权限内完成产品收敛/必要代码/测试/**候选版本准备**。未经明确授权不得: 合并 main/推送公开仓库/改生产环境/付费API/新付费数据源/删重要数据/真实交易/泄密/绕保护/降验收标准。既有 IA 波次合并授权(R系)不适用于本章程交付物——本章程产出停在 dev 分支待用户外部审计。引擎席(R44+)按其既有授权独立续行,两席互不代行。

## 九、执行机制

Single Orchestrator(操作者席)+现有工具+独立审计席。每轮: PRODUCT GAP→ROOT CAUSE→MINIMAL CHANGE→TEST→REAL PRODUCT RUN→INDEPENDENT AUDIT→CAPABILITY UPDATE。自主推进不逐阶段请示;真实阻塞(权限/资源/预算/外部数据)存状态转其他工作,全阻塞才停。连续两轮未解同一问题=重审根因,禁补丁堆叠。

## 十、登记

- 工作树: `/Users/cast/investment-agent-product`(分支 dev/product-convergence-mvp,基点 main@a589095)
- 阶段文档: PRODUCT_CONVERGENCE_PHASE0_AUDIT.md(Phase 0 产出)及后续各阶段报告
- 引擎席并行: R44=A 族碎片泄漏硬化(Charter §6.2 主刀在引擎),本席 Phase 2 待其落地面做残余评估
- 轮次登记: 沿用 ITERATION_LOG(双行制: 主行 |11-16|R4x| 入 finalize 正则),R45 起=本章程轮次(与引擎席续号互斥,先到先取,RESUME 队列为准)
