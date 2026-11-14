# RESUME — 新会话恢复指令

> 新会话仅凭仓库文件即可恢复工作,不依赖任何历史聊天记录。开场即按本档执行。

## 恢复步骤

1. 读根目录 `CLAUDE.md`(红线与启动纪律)。
2. 读 `PRODUCT_GOAL.md`(最高目标;锚句「全球宏观经济与金融市场研究」「最终产品目标」
   须完整)。**若该文件不存在 = 总指令未落位**: 向用户索取原文,不得自行代拟。
3. 读本档「下一步」节顶部 **RD-CHECKPOINT 块**(机器检查点): 记下 round/next_task/commit。
4. **核对真实 Git,不盲信文档**: `git rev-parse HEAD`;检查点 commit 须存在且为 HEAD 祖先
   (`git merge-base --is-ancestor <commit> HEAD`);不成立 = 状态可疑,**禁止开发,先对账**
   (跑 `python3 scripts/rd_state_consistency.py` 定位五项中哪项失同步)。
5. 读 `CURRENT_STATE.md` 权威快照节(唯一当前态;含任务台账)→ `OPEN_ISSUES.md`(卡点)
   → `CAPABILITY_MATRIX.md`(差距)→ `ITERATION_LOG.md` 末行(最近一轮)。
6. 台账/「下一步」队列即当前工作;**已入 ITERATION_LOG 的轮次任务严禁重做**(§3.3)。
7. 在 `dev/*` 分支工作;未经授权不合 main、不推送、不付费、不碰生产。
   轮**开**: 手工在台账加 `T-R<n>-<seq>` 行+队列项挂 `[进行中·R<n>]`;
   轮**收口**: 人工 prose(日志行/台账移出/快照 prose/队列归档)先写好 →
   `python3 scripts/rd_checkpoint.py --finalize ...` 机器盖章+六项门
   (检查点块/baseline 机器行勿手写;无日志行管线拒盖章=防先称毕)。

## 下一步(2026-11-14 R26 检查点后 · 排队面续)

> **唯一队列入口**(Charter 10 §3.1/§3.3)。已完成任务只进「下一步存档」与 ITERATION_LOG,永不回到本节。
> 恢复第一步: 读本节检查点块 → `git merge-base --is-ancestor <块commit> HEAD` 亲核(块 commit 以机器盖章为准,勿信任何手写 sha);不成立=状态可疑,先对账再动工。

R26=排队面候选①(VP 旧库 LABEL_DRIFT 对账毕,审计两轮闭)。队列按优先级:

1. **[进行中·R28·T-R28-1] 架构转型与工程整改·阶段三纵向切片开工(用户新工程令 2026-11-14,六阶段,唯一优先队列)**: 章程原文=docs/autonomous-rd/CHARTER_ARCH_REFORM.md;进度=阶段一/二毕(故障基线含 A-1/A-2/A-3/B/C;契约设计 v1.2 金融席+审计席双放行);实施工单=docs/autonomous-rd/ARCH_REFORM_PHASE3_PLAN.md(T1 S1 六项落地→T2 thresholds v1.0+G1-G4 CI 门→T3 series_store 补 HY_OAS/CURVE→T4 claim_factory 六型→T5 claim_verifier 六状态→T6 确定性渲染 C1→T7 新旧并行对照→T8 迁移门审计席裁决)。工程面=分支 **dev/arch-reform-p3**(基点=R27 修后 main),worktree=**~/investment-agent-reform**(持久位,勿用 /tmp);实现席=引擎轮次或专项子代理(工单 §2);**整改分支未经用户授权不并 main 不动生产;旧路径全程只读可恢复;QA 资产(V5/V6+封存件)留操作者面 ~/agent-loop/ARCH-REFORM/QA/ 禁入本仓(封存面禁读)**。
2. **R28+ 排队(整改六阶段内)**: 阶段四 Agent Native 统一(周报切片过后复用 Fact→Evidence→Claim→Verification 契约改造 agent_judgment.py 编排接口)→阶段五研发机制(根因决策门/优先级=影响×严重×复发×根因×成本/能力验收六问/状态语义一致门,只加严不放松)→阶段六真实产品验收(Real-World Acceptance Suite 四面)。旧 R27 候选② NIT 余留(Ni-2~5/MW-V1 P2-2)降级排整改期后(P2-2 叙述一致性防线由阶段三 text_consistency+语义席取代)。

- 每轮开始答「当前最重要产品能力缺口」,结束答「本轮提升了哪项真实研究能力」(§七,写进 ITERATION_LOG 行)。
- [日历门不变] F 补证轮 2026-12-05/六标签首验窗+金油比 2026-12 引擎自动触发,勿手工提前(§八:算法正确性验收不等日历门)。六标签首验窗现含 R26 重贴的 007/010 hyp0 NOT_YET_TESTABLE 两行(到期 2026-12-31 后窗口)。
- [低优先候选] HK 双通道脆弱面/china 子源失败落盘/R13 审计 2 NIT/OPEN_ISSUES 按需取用。

<!-- RD-CHECKPOINT v1: json {"round": 27, "date": "2026-11-14 20:23 HKT", "branch": "dev/rd-r27-gateb-extractor", "commit": "286c0c6afea0d835bdbd6dada4e3502b11813498", "baseline": "286c0c6afea0d835bdbd6dada4e3502b11813498", "goal_sha": "7535a141b2339a13", "completed_ids": ["T-R27-1"], "next_task": "R28: 架构转型与工程整改·阶段三纵向切片开工(用户工程令唯一优先队列;分支 dev/arch-reform-p3+worktree ~/investment-agent-reform;工单 T1 S1六项落地起步)", "next_round": 28} -->

## 下一步存档(2026-11-14 R27 收口后版)

1. [已毕·R27] **Gate B 提取器误杀修复(T-R27-1,两期实例 11-08+11-14)**: 正道修五缺陷零容差放宽——(辛)英文 ticker 别名标识符边界(SPX_EPS 前缀不再当 SPX,166 天滞后不当价格)/(壬)天数计数守卫(值后紧跟「天」=时长非水平)/(癸)带符号百分数=变化断言(利率/利差/失业率/信心捕获组前加符号 lookbehind,DXY+1.09% 不再当 UST_10Y 水平)/(距离)「距离」入 _SPEC_CONTEXT_RE(0.80pp 距警告线不再当 HY_OAS 水平)/(子)语境前视不跨小句边界(邻句 bleed 不再误跳真阳性)。套件 test_rd_r27_gateb_extractor.py 45 判(真实隔离报告句嵌入 audit/r27_gateb_repro/+当日真实锚点副本;判死红线=三误杀句嵌入零数值错误+真错值句照常❌);两期真实报告全文复验 errors=0。台账 T-R27-1 已毕。
2. [已毕·R27·操作者席] **独立验证+新工程令落地**: 四项复核全绿(专属 45/45+真实报告全文 errors=0+锚点取证[11-08 复现=v1 原始晨批=事故同基]+干净克隆全仓 143/143)+六门 6/6;验证记录=~/agent-loop/ARCH-REFORM/R27-OPERATOR-VERIFY.md。用户 2026-11-14 下**架构转型与工程整改新工程令**(六阶段,原文落仓 docs/autonomous-rd/CHARTER_ARCH_REFORM.md),阶段一/二当日毕(故障基线+契约设计 v1.2 两席放行),阶段三工单落仓 ARCH_REFORM_PHASE3_PLAN.md;R28 起引擎转向整改队列。

## 下一步存档(2026-11-14 R26 收口后版)

1. [已毕·R26] **VP 旧库 5 行 LABEL_DRIFT 对账(排队面候选①)**: 根因=v1.0 构建面旧词汇 no_forecast 存量 vs 现行引擎 UNPARSEABLE_HORIZON/NOT_YET_TESTABLE 分化,R22"重建即消"预期不成立(build_vp C 层零变动);reconcile_label_drift 可见重贴(三层留痕+violation 拒写+判定标签默认拒+原子写幂等)+真实 17 档对账(133 OK/0 漂移/0 违规,view_label 零变动,007/010 标签精度提升 NOT_YET_TESTABLE);独立审计四维 PASS 0 BLOCKER 0 MAJOR(4 NIT,3 随修;前态法证逆向重构 sha256 双向吻合);新套件 31 判+全仓 143/143 两遍。台账 T-R26-1 待合并。对账单=audit/R26_LABEL_DRIFT_RECONCILIATION.md。

## 下一步存档(2026-11-14 R25 收口后版)

1. [已毕·R25] **R24 审计 3 NIT 收口+DFF 日频史接线**: V1-1 台账语义三分/V1-2 blocked md 重渲(_write_report 不变式)/V2-5 schema v1.1 secondary_metric_ids;DFF=registry v2.8.5 history_source+macro FRED_SERIES+normalize_macro 权威门+rhq/wd 解析(真实拉取=操作者轮,拉取前诚实 no_series)。独立审计六维 PASS 0 BLOCKER 0 MAJOR(3 MINOR+5 NIT→Mi-1/2/3+Ni-1 随修 8006b9d,二轮复核四项闭死无新引入=整体可并入;余 Ni-2/3/4/5 排队 R26)。新套件 44 判+全仓 142/142 两遍。台账 T-R25-1 待合并。

## 下一步存档(2026-11-13 R24 收口后版)

1. [已毕·R24] **阶段五 真实E2E+独立验收+阶段六状态更新(Charter 10 收官)**: 未优化真实宏观问题(HY_OAS×SPX×VIX×CURVE)全链——run 15 步 run_ok=True/attach 0 violations/QB-20261113-002/OC-003/004/ART-M+ART-FALS 首建;§6.4 十章产出逐章映射齐;**独立审计绑定核查首跑抓 2 真 MAJOR(判断内容定性错配被运行自采 S4 序列证伪)→修订 v2 重 attach→二轮复核可并入**(更正评注 QB-20261113-002-C1);顺带 agent_judgment MINOR-1/4/5+NIT 硬化(0824331);全仓 141/141;AC6 完整重验收按实通过(终判维持用户落章)。台账 T-R24-1 待合并。报告=R24_STAGE5_FULL_ACCEPTANCE.md。

## 下一步存档(2026-11-13 R23 收口后版)

1. [已毕·R23] **阶段四 一键AI研究闭环(Agent Native)**: L3/L4 真完成——校验器零生成零改写+attach 合并+research-attach 命令+Skill 闭环工作流;真实 E2E 一次任务全链首例(QB-20261113-001+观察钟首建);独立审计四维 PASS 0 BLOCKER 0 MAJOR(MINOR-2/3 本轮已修,余登记);新套件 43 判+全仓 140/140;报告=R23_AGENT_NATIVE_E2E.md。台账 T-R23-1 待合并。

## 下一步存档(2026-11-13 R22 收口后版)

1. [已毕·R22] **阶段三 金融正确性**: 四案先复现后修全毕(5.1 方向语义/5.2 到期新鲜度门/5.3 标签-证据绑定/5.4 vintage 二次过滤;R1-MINOR-4 收口)——新套件 test_rd_r22_fin_correctness.py 53 判+受影响六套件全绿;生产面 VP 17 档 --build-all 重建字节不变+绑定扫描 128 OK/5 LABEL_DRIFT/0 违规;AC3 机器防线落地,真实已到期样本首验留 2026-12 六标签首验窗(日历门)。收口由后继会话补完(前会话中断)+独立复验一致。台账 T-R22-1 已合并(v0.18.0-alpha)。

## 下一步存档(2026-11-12 R21 收口后版)

1. [已毕·R21] **阶段二 持续执行验证**: §4.4 七项矩阵全实查 6 PASS+1 PARTIAL(无头压缩恢复无实例子面,零冒认);防死循环顾问 rd_progress_watch.py(漂移/返工预警,finalize 随行+CI 非阻塞)+finalize 事故弧回归锁 18 判+候选钩子包 ops/hooks-candidate/(待操作者安装);报告=R21_CONTINUOUS_EXECUTION_AUDIT.md。台账 T-R21-1 待合并。

## 下一步存档(2026-11-12 R20 收口后版)

1. [已毕·R20] **阶段一 状态管理整改**: 唯一权威状态+任务台账(唯一ID/状态/Git证据)+六项一致性检查门(rd_state_consistency.py,CI 硬门)+检查点管线(rd_checkpoint.py --finalize,机器盖章取实际Git)+真实恢复验收测试(无上下文新Agent从文件恢复,核HEAD,不重做已完成)——三套件 62 判全绿;台账 T-R20-1 已毕移出。

## 下一步存档(2026-11-12 R8 验证+合并后版)

1. [已毕·R7+R8] AC7 首跑+独立验证+合并: R8 七面零 BLOCKER(数值单项 FAIL
   ZQ−DFF 0.295→0.305 已出更正评注 C1,结论不变);merge=825eb4f+R8 记账
   033a869(docs-only 不另发 tag);R8 全文=R8_AC7_VERIFICATION.md。
2. [已毕·R9] 采集缺口波(见上第 1 条)。

## 下一步存档(2026-11-11 四卡点批准后版)

1. [已毕] R1-R4 全链 + 用户「全部审批通过」四卡点执行:
   ①合并毕(main=be8dabd,v0.10.0-alpha);③LIVE 部署毕(v0.10.0 面);
   ②原则获批无即需项;④无头自主运行=后被用户放行落地(R5 首轮)。
2. [已毕] R5 候选③诊断(ZQ_IMPLIED_AVG 采集恢复,周六 11-14 weekly 应自动
   恢复,零代码改动)。
3. [已毕·R5] 候选①数据覆盖盘点→升级为四类缺陷分解+引擎修复(见上)。

## 快照纪律

- 轮次收口 = 人工 prose 先行(日志行/台账移出/快照 prose/队列归档)→
  `scripts/rd_checkpoint.py --finalize` 机器盖章(检查点块+baseline+goal_sha)+
  六项一致性门;盖章与 prose 同落一个 docs 提交。
- 上下文过半: 更新 `CURRENT_STATE.md` + 本档「下一步」→ 继续工作。
- 上下文将尽/会话将终: 立即停止开新任务,先完成完整检查点
  (实际进度/测试与审计结果/能力差距修订/分支与 Commit/下一步),再收尾。
