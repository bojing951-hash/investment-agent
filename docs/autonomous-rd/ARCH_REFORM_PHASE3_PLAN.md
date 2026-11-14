# 阶段三实施工单(2026-11-14 操作者席拟,用户「批准,继续」授权开工链)

> 依据: 章程§五(最小纵向切片)+PHASE2-CONTRACT-DESIGN.md v1.2(§3/§5/律1-8)+thresholds-adjudication.md(S1 六项+终签生效条件)+QA/(V5/V6/迁移标准草案)。
> 纪律: 整改分支=dev/arch-reform-p3,**未经用户授权不并 main 不动生产**;旧路径全程可恢复(新件一律新增模块,旧 Gate B 只读对照);每 PASS 须执行证据;封存件禁读(哈希冻结)。

## 0. 分支与基线

- 基点=**R27 合并后的 main**(对照路径必须是 R27 修后 Gate B,否则新旧对比不公平)。
- worktree=**/Users/cast/investment-agent-reform**(持久位,勿用 /tmp——R9 清理教训);`git -C ~/investment-agent-dev worktree add -b dev/arch-reform-p3 <path> <post-R27-main>`。
- 开工前置断言: 基点 CI 绿+六项一致性门绿;fixtures 哈希=HELDOUT-MANIFEST 记录值。

## 1. 任务序(每任务=实现→自测→操作者席验证→记账;fin 席仅涉注册表)

| # | 任务 | 内容 | 验收 |
|---|---|---|---|
| T1 | S1 六项落地 | framework.md 三处(BEI 双级注/INDPRO 第四项+漂移注/失业率 3m 补行左开右闭/±1~+3 笔误);macro_scorecard BEI 显示串低侧 1.5 误写 2 修正+硬编码阈值改读注册表;data_validator 数值字典整族退役(含非农 L228-237 max_value_K=1000)改读 registry;A股词汇规则显式保留注记 | 旧行为 diff 审;无行为漂移项(BEI 显示串=真修)逐条列;全量测试绿 |
| T2 | thresholds.json v1.0 落盘 | SIGNED-v0.2 内容+signed_by/signed_at/adjudication_ref;CI G1-G4 门(quote 双向锚无孤儿/代码常量集↔族键集双空差/概念隔离静态断言/字典退役断言);元规则=门红禁例外白名单 | G1-G4 本地全绿;篡改一值必红(变异自证) |
| T3 | series_store 补通道 | HY_OAS/CURVE_2S10S 进周报路径序列库(Agent Native S4→series_store 键;源窗与滞后如实注记) | 两序列可查询+新鲜度窗判定真实跑 |
| T4 | claim_factory 六型 | level/change/comparison/threshold/threshold_distance/observation_lag 全确定性派生自 Fact+S4+registry;谓词语法(percentile_rank 公式钉死/sign_flip_date/last_crossing/crossing_count/AND);单位代数三元组;pp↔bp=×100,percent→pp 无基底禁换 | 每型≥3 真实快照用例;零模型调用断言 |
| T5 | claim_verifier | 六状态;evidence_refs 必带值;CONTRADICTED=断言级修订;STALE 分级;model_inferred 数值→强制 SEMANTIC_REVIEW;NOT_VERIFIABLE 仅确定性断言可发布带披露 | 注入违例每状态≥1 反例咬住 |
| T6 | 确定性渲染模板(C1 载重墙) | 模板产全部数值单元格/表+manifest;模型=叙事消费 VERIFIED 断言;text_consistency 律8 修后版(映射主体=claim 角色+值,后缀仅否定排除);白名单=注册表+日期,新增须 fin 席签 | 渲染文本数值 token 100% 可映射或显式披露;禁模型自报 manifest |
| T7 | 新旧并行对照 | 同输入双路(旧 Gate B[R27 修后] vs 新验证器);指标=章程 5.2 七项;fixtures=V1-V4/V7 真实+V5 30+V6 20 公开面;封存面由审计席执行非开发席 | 对照表+逐条判定落档;序列依赖条目复跑至终态 |
| T8 | 迁移门呈报 | 对照结果 vs 迁移标准草案→**审计席裁决**(真子代理);结论措辞只准「合成注入+改写变体留出通过」;V1/V2 五处真实误杀值复位 VERIFIED 核验 | 审计席 PASS/FAIL+理由;迁移与回滚方案随附 |

## 2. 分工与验证

- 实现席=引擎轮次或专项子代理(开工时按可用性定);操作者席逐任务验证(不吸实现席上下文);fin 席仅注册表变动;QA 席管 fixtures 冻结与启封监督;审计席独裁 T8。
- 每任务毕落 PHASE3-LOG.md(执行证据=命令+输出摘录,禁只写结论)。

## 3. 出口条件(章程 5.3 原文映射)

已知正确全过/已知错误全拦/身份单位零混淆/未验证不静默发布/无重大回归(枚举事件类)/留出达标→审计席裁决通过→**才**提交用户裁定是否渐进替换旧路径并申请并 main。

## 4. 边界重申

不动生产部署;不删历史研究数据;不产生新增付费 API 费用;密钥零接触;旧系统在新系统过验收前保持可恢复(新模块全增量,旧件只读)。
