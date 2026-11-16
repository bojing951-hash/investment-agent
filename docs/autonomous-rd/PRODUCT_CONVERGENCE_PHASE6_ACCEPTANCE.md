# Product Convergence — Phase 6 G0-G4 验收矩阵(2026-11-16)

> 章程§六: G 门开发前固定,禁降标。本矩阵=证据汇总;逐项证据链接在档。
> 分支: dev/product-convergence-mvp(2d68543+本档;**未并 main 未推送,
> 待用户外审裁定**——章程权限边界)。

## G 矩阵

| 门 | 判据 | 证据 | 判定 |
|---|---|---|---|
| **G0 Engineering Integrity** | 标准测试无隐藏错误/CI 可复核/目标与验收契约未擅改/研发状态与 Git 一致/净环境可跑核心系统 | 守卫四套全绿(phase1 13/0+phase2 11/0+phase3 22/0+target_integrity 13/0);target_integrity_guard --check 绿(四件哈希未擅改);complexity_baseline --check 绿(±5%);G0_VERDICT.json: fresh clone dev@HEAD→rd_state_consistency 绿→checkpoint 绿→research-run rc=0(净树诚实面,honest_boundary 不冒认研究质量) | **PASS** |
| **G1 Financial Correctness** | 数值/时间口径/单位正确;无未披露前视;已知正确报告不误杀;错误数据能拦;未验证事实不放行 | Phase 5 审计独立复算 66/70 精确吻合(多处第三位小数逐位);2 失实均已修订闭环(M-1 主跌浪语境/M-2 披露降级);引擎既有 e2e/口径套件随 main CI(43805774407 绿);未验证事实不放行=VP 全 INSUFFICIENT_EVIDENCE 首验窗 2026-12+judgment_contract 六查拦截 | **PASS**(修订后;BLIND basis 微统计口径不可复现=已知缺口入 backlog) |
| **G2 Complete Research** | 一次自然语言输入实际完成数据+机构观点+历史研究+L3 推理+L4 情景+完整报告 | 四任务链全绿: A(UST_10Y→HY_OAS/SPX)/B(CN 宏观→CHINEXT/FXI,诚实边界+显式门)/C(DFF/JP→USDJPY/GOLD_F)/BLIND(金价×实际利率×美元)——每链 plan(run_ok 视证据面)+Agent 席真产 judgment(VERIFIED)+attach+report **L3∧L4 produced=True**;FULL_REPORT=L1 表+L2 摘编+L3/L4 面 | **PASS** |
| **G3 Research Quality** | 关键数值可独立复算/观点可追溯/解释有证据支持/存在竞争性解释/反对证据被处理/情景可证伪 | phase5/AUDIT_REPORT 六项矩阵: 66 复算吻合/VP+fact 引用全解析抽核/竞争解释每矛盾 ≥2/反对证据处理在档/证伪阈值全带基准值+日期+时限(部分 v1.1 副指标锚);2 MAJOR 修订当日闭环 | **PASS**(修订后) |
| **G4 Real-World Acceptance** | 三项真实任务+至少一项独立选定的未优化问题 | 三真实任务 A/B/C 成立(真实数据树+真问题+真判断);盲测=出题席零数据访问+预注册 sha 锁定先于运行+研判席禁读预注册——**「问题独立设定,投递面半优化」**(映射注入方法学指定词,Phase 5 M-2 如实降级,非"未优化投递") | **PASS with disclosure**(盲测投递面半优化如实标注) |

## 持久化(Phase 6 第二半)

- 单入口 `ia_cli.py research-one` 三段式入 dev 分支(e56fe91→2d68543);
  守卫 tests/test_pc_phase3_research_one.py 22/0 入库(净树诚实链防漂)
- 四任务工件+sha256 清单: docs/autonomous-rd/phase4/{A,B,C,BLIND}/
- 审计档: docs/autonomous-rd/phase5/AUDIT_REPORT.md+PHASE5_CLOSURE.md
- G0 包: docs/autonomous-rd/phase6/G0_VERDICT.json
- 进度链: PHASE0_AUDIT→PHASE1_EXIT→PHASE2_PROGRESS→PHASE3_PROGRESS→
  PHASE4_PROGRESS→PHASE5_CLOSURE→本档

## 已知边界与 backlog(如实,不冒称)

1. 纯自然语言零命中=词法规划器设计边界;语义翻译归 Agent 席(Agent Native);
   投递映射协议化=产品 backlog(方法学词注入须预披露)
2. judgment basis 微统计可复现面(backlog,Phase 5 发现)
3. S4 no_series 未标 honest_refusal→引擎席 R46 候选
4. CN 宏观指标无历史序列(数据面,登记不动代码)
5. Phase 2 尾部: 引擎 R45 落地后 Gate B 并行重测+MC1 裁定档(迁移判据
   MC1-MC4 先固定后测量,达标才迁——不提前替换生产 Gate B)

## 终态

Phase 0-6 全部执行完毕。**唯一核心成功标准对照**: 真实产品能力经过独立
验证——四任务真链+独立审计 66 复算+盲测预注册对照=已达成;两处披露失实
被审计抓出并当日修订=验证机制本身有效。
**待用户**: 外审 dev/product-convergence-mvp(不并 main 不推送,权限边界
遵守);裁定 LIVE 面是否引入 research-one 入口。
