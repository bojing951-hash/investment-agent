# Product Convergence — Phase 0 现状审计(2026-11-16)

> 席位: 操作者(章程 Single Orchestrator)。基线: main@a589095(R43 章,CI 43796128559 绿)。
> 方法: 亲读仓库实况+本轮刚完成的双口径终验证据;不以历史文档 PASS 代替核验。
> 章程: CHARTER_PRODUCT_CONVERGENCE.md(同日登记)。

## 1. 工程基线(G0 前置事实)

| 项 | 实况 | 证据 |
|---|---|---|
| Git HEAD | main=a589095(净,CI 绿 43796128559);dev/product-convergence-mvp 基点=同尖 | git log/Actions API 亲查 |
| 测试执行口径 | **双口径全绿**: exit/CI 口径 166 件 red=0;pytest 逐件口径 166 件 red=0(首度全零);pytest 目录整跑=设计性不适用(线性件尾退出习语 60+件,rc 语义有效: 绿0/红3,INTERNALERROR 打印=噪音) | R43 净克隆终验 /tmp/r43_final_verify.log;RDG-012 注记 |
| 章程审计背景项A「脚本式测试过但pytest错」 | **已解决**(R42 聚合器吞错+R43 四件套 argv 收口),非待办 | RDG-20261116-012+残余⑦闭项 |
| 状态真实性 | rd_checkpoint 七项门 7/7(基线/RESUME/台账/AC矩阵/日志-台账/目标sha/验收如实),状态与 Git 绑定 | R43 章 a589095 亲验 |
| 隐藏错误防护 | 聚合器测级异常计退出码+守卫 23 判+双口径终验自此标配 | R42/R43 |
| CI | 每推送 main 自动跑(历史全绿);**无 main 保护/Ruleset**=外部权限项(Phase 1 出准备件) | GitHub API 亲查 |

## 2. 产品入口与能力真值表(章程§三章架构映射)

| 架构层 | 现有资产(亲核) | 状态 | MVP 差距 |
|---|---|---|---|
| 用户交互/Planner | ia_cli 13 子命令;research-map=确定性扇出证据包(零模型);Claude Skill global-macro-research(十步工作流) | PARTIAL | **无自然语言→自动规划的统一单入口**(用户须自行组织 research-run→attach 两步);Phase 3 主刀 |
| Data & Evidence | 指标注册表 v2.8.4(110 指标全带 source/symbol);快照 v2(Gate A 权威);机构观点库 17 档/15 机构 schema1.1(attribution 硬拦截);sha256 逐数证据链;采集管线 run_weekly+15 采集器 | PASS(AC1/AC2 用户落章) | 诚实缺口在档: BUND_10Y/2Y 源端封锁/JP_CPI_TOKYO 用户裁定缺席/CN_SF_FLOW 滞后~7月/HK 双通道脆弱——**不虚构填补**,如实披露即可过 G 门 |
| Deterministic Research | scorecard(阈值注册表+G1-G4门)/analog 六维类比(expanding z+四判据)/compare/history/changes;research_contract(claim_factory→verifier→render_hook) | PASS(AC4 落章) | 无(复用) |
| Agent Reasoning(L3/L4) | research-attach=Agent Native 判断落位+纪律机器校验;R23 E2E/R24 真实未优化题(HY_OAS×SPX×VIX×CURVE_2S10S 全链+审计抓2MAJOR→修订闭环)/R34 runtime 五环首例(DXY×GOLD_F→REVISE→VERIFIED) | PARTIAL | **L3/L4 由 agent 真生成仅在被手动编排时发生**;research-run 恒 declared-not-produced(诚实设计)。Phase 3=单入口内编排 agent 席真产出,禁改 produced 造假 |
| Verification | Gate A(数据完整性)/Gate B(旧自由文本+新 text_consistency 并行)/claim_verifier/agent_judgment 纪律校验/semantic_review 席 | PARTIAL | **新验证器真实周报误报=A 族碎片泄漏 154/326=47%**(R41 定性),引擎席 R44 主刀硬化中;本席 Phase 2 接残余评估+新旧并行迁移框架(达标才迁,不提前替换生产 Gate B) |
| Delivery | report_generator/周报管线(published 转正)/工作台四页(零模型纪律)/research_archive(QB 档) | PASS(AC6/AC7 落章) | 完整研究报告由 Phase 3 单入口产出后走既有交付 |
| 模型能力 | Agent Native(本席=Claude Code 真工具调用);LIVE GLM sidecar(MODEL_* 三参,v0.4 起模型无关)已部署授权 | PASS | 不购新 API;L3/L4 由 Agent Native 席承担 |
| 独立审计环境 | 子代理独立席先例(R32 语义审计/R34 独立 REVISE 席);净克隆验收先例 | PARTIAL | 无真权限隔离→章程§九: 能标多准标多,不足处如实 NOT_VERIFIED,不换名充独立 |

## 3. 章程需求→已有→不重复开发清单

- §五.A 测试执行口径: 已解决(R42/R43),不重做。
- §五.B 状态真实性: rd_checkpoint 门制在役,不重建。
- §一.8「代码复杂度偏高」: Phase 7 只产 backlog(DEFERRED),不瘦身。
- AC 矩阵(FINAL_ACCEPTANCE)九 PASS+AC3 PARTIAL(2026-12 日历门): 既有资产,本轮不触碰;G0-G4 为增设门。
- R24 已做一项「未优化真实问题」验收: 可作 G4 盲测先例形态参考,但 G4 三任务(A/B/C)本轮重做。

## 4. 两席分工(避撞车)

- **引擎席**(launchd,既有授权): R44=A 族碎片泄漏硬化(=章程§6.2 误报主刀)+T8-R2④⑥⑦+GUARD_FILES 扩容;其合并发布按既有 R 系授权。
- **操作者席**(本章程): Phase 1 工程硬约束→Phase 2 残余评估(待 R44 落地)→Phase 3 单入口 MVP→Phase 4 真实任务→Phase 5 独立审计→Phase 6 G 门验收→Phase 7 backlog。产出停 dev/product-convergence-mvp,**不 push 不并 main,待用户外部审计**(章程§八从严)。

## 5. Phase 0 出口判据自检

「知道当前系统真实具备什么/缺什么/如何客观判断成功」——**满足**: 真值表§2 逐层有资产指针+差距定位;G0-G4 门已固定于章程(开发前);MVP 差距收敛为两件硬货: ①单入口编排(L3/L4 真产出)②验证误报残余(依赖 R44)。可以进 Phase 1。

## 6. 阻塞/待用户项(先登记)

- main 分支保护/Ruleset/必需检查: 需仓库所有者在 GitHub 操作(Phase 1 出配置清单+证据)。
- 真独立权限边界(外部审计环境): 不具备→按章程标 NOT_VERIFIED 边界。
- 付费类: 无新增需求(不购)。
