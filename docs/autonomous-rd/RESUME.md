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

## 下一步(2026-11-15 R33 收口后 · 引擎轨道余留+席位真跑首验)

> **唯一队列入口**(Charter 10 §3.1/§3.3)。已完成任务只进「下一步存档」与 ITERATION_LOG,永不回到本节。
> 恢复第一步: 读本节检查点块 → `git merge-base --is-ancestor <块commit> HEAD` 亲核(块 commit 以机器盖章为准,勿信任何手写 sha);不成立=状态可疑,先对账再动工。

R33=席位 runtime 接入三件(T-R33-1;首审席 narr-facts 建议移交毕,§8 过渡条款收口)。队列按优先级:

1. **R34+ 引擎轨道续行**: 引擎树 dev/arch-reform-p3-t1 自走;操作者/引擎任意席续行。**席位接入真跑首验**: 下一份带 L3/L4 的 research-run 应见「语义审查」节+编排层读 semantic_review.required 唤席(首例闭环=VERDICT 档落 audit/semantic_review/)。整改余留(终报告非阻断清单): T8-R2 七项①-⑦/「利差」裸别名歧义升披露/round.sh 资源双上限硬接线=LIVE 部署时。
2. **日历门(勿手工提前)**: F 补证轮 2026-12-05 观察钟满/六标签首验窗+金油比 2026-12 引擎自动触发(§八:算法正确性验收不等日历门)。六标签首验窗含 R26 重贴的 007/010 hyp0 NOT_YET_TESTABLE 两行(到期 2026-12-31 后窗口)。

- 每轮开始答「当前最重要产品能力缺口」,结束答「本轮提升了哪项真实研究能力」(§七,写进 ITERATION_LOG 行)。
- [低优先候选] HK 双通道脆弱面/china 子源失败落盘/R13 审计 2 NIT/R25 审计 Ni-2~5/OPEN_ISSUES 按需取用。

<!-- RD-CHECKPOINT v1: json {"round": 32, "date": "2026-11-15 13:02 HKT", "branch": "main", "commit": "16bc7effccbfc97d0b1224ea54b0923c397a78ac", "baseline": "16bc7effccbfc97d0b1224ea54b0923c397a78ac", "goal_sha": "7535a141b2339a13", "completed_ids": ["T-R32-1"], "next_task": "R33: 引擎轨道续行(席位 runtime 接入三件: 自动唤起+披露开关/gate_a 披露行/S3 信封入索引;T8-R2 七项/利差歧义随轮)", "next_round": 33} -->

## 下一步存档(2026-11-15 R33 收口后版)

- [已毕·R33] **席位 runtime 接入三件**(T-R33-1;首审席 narr-facts 建议,SEMANTIC-AUDIT-SEAT §8 过渡条款收口): ①semantic_review 状态面+md 披露开关 ②gate_a 披露行 ③S3 信封入证据索引;新套件 14/14+全库 156/156;详见 ITERATION_LOG R33 行。

## 下一步存档(2026-11-15 R32 收口后版)

- [已毕·R32] **语义审计席开启+首审修订闭环**(T-R32-1;终报告遗留「真实模型语义审计席 NOT_VERIFIED 占位」项): 用户 2026-11-15 授权「开」;席位=docs/autonomous-rd/SEMANTIC-AUDIT-SEAT.md;首审 R24 真跑档=REVISE 三必修零剔除,修订闭环 VERIFIED 23/23;归档=audit/semantic_review/20261115/。
- [已毕·R28~R31] R28 收口后版三项全部落地: ①引擎轨道续行(R29 复审 322/0+R30 对账 160/0+R31 盖章毕,其树自走) ②LIVE 翻面 v0.24.0(2026-11-15 用户令执行,七步绿+核验毕) ③日历门外其余余留移交上方队列(R33 项)。

## 下一步存档(2026-11-15 R28 收口后版)

1. [已毕·R28] **架构转型与工程整改·六阶段(T-R28-1,用户工程令 2026-11-14)**: 阶段三 T1-T8 契约六接口落地(thresholds v1.0 SIGNED+G1-G4/series_store/claim 六型/六状态验证/确定性渲染/新旧对照零误杀/迁移门 T8-R2 PASS,轮一 FAIL 如实在档)→阶段四 Agent Native 统一(jc-v1.0-phase4,V4 双向验收 57/0,错误版两 MAJOR 被拦)→阶段五 RDG 根因决策门+①-⑦状态语义一致门(登记簿六条)→阶段六真实面验收(A 金融数值/B 研究结论/D 研发可靠全绿+C-det R24 结构面)→收口修复波(全库 154 套件 154 绿,RDG-005)→终报告 ARCH-REFORM-FINAL-REPORT.md(§十二九项)。分支 dev/arch-reform-p3 26 提交 96d265e→3c8b5d4;用户 2026-11-15 批准并轨→v0.24.0-alpha。台账 T-R28-1 收口。
2. [已毕·R28] **C-real 未优化新问题真跑**: 用户令执行 WALCL×SOFR×DXY(20261115T014829Z)六判据全过(15 步 run_ok/WALCL WARN=周频滞后如实/事实区 3 查全 VERIFIED 零未映射/L3L4 诚实不产出);判定面两缺口正道修(3c8b5d4;RDG-006 登记,RDG-004 闭环);跑台脚本+判据=docs/autonomous-rd/phase6c/。
3. [已毕·R28·带外] **HK 采集三路增量修复(T-R28-2,另一操作者会话)**: 腾讯 320 小窗+持久化兜底+按需回补(治 11-12 HSI/HSCEI 双源失),经用户批准并入 main(merge=4d5da02,纯克隆 145/145 零红);按台账注记随本轮收口一并移出存档。

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
