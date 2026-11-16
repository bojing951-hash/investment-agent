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

## 下一步(2026-11-16 R43 收口后 · 引擎轨道余留)

> **唯一队列入口**(Charter 10 §3.1/§3.3)。已完成任务只进「下一步存档」与 ITERATION_LOG,永不回到本节。
> 恢复第一步: 读本节检查点块 → `git merge-base --is-ancestor <块commit> HEAD` 亲核(块 commit 以机器盖章为准,勿信任何手写 sha);不成立=状态可疑,先对账再动工。

R42=测试聚合器吞错修复已毕+R43=A 族碎片泄漏硬化已毕(引擎席;真实面 326→283 六类构造物根除+pytest 四件套随批收;tid 见存档与 ITERATION_LOG)。队列按优先级:

1. **R44+ 引擎轨道续行**: ①**B 族评分卡分值列/表内碎片硬化首位候选**(R43 后 283 CONTRA 中 B 族=评分卡 `| +2 |` 分值列绑行指标水平+散文总分 `增长总分0、通胀总分+3` 形态居首;每任务先过 RDG 门)②T8-R2 ④era base_anchor_set 必填+⑥重封留出+⑦变异压力轮(下次启封随批)③round.sh 双上限=LIVE 部署时④R41 审计登记项(MINOR-1 S3 饱和值敏感度+NIT-3~5)⑤R43 审计登记项(MINOR-2 表内序号 `| 1. x |`+NIT-2 未闭合注释远端吞+NIT-5 r1_vp_stages>120s CI 时间面)⑥FX 族再暴露交叉盘/对名误读形态则升「主体锚=别名表驱动」(RDG-010 尾注)⑦新聚合模板套件须入守卫 GUARD_FILES(RDG-012 NIT-A)。
2. **日历门(勿手工提前)**: F 补证轮 2026-12-05 观察钟满/六标签首验窗+金油比 2026-12 引擎自动触发(§八:算法正确性验收不等日历门)。六标签首验窗含 R26 重贴的 007/010 hyp0 NOT_YET_TESTABLE 两行(到期 2026-12-31 后窗口)。

- 每轮开始答「当前最重要产品能力缺口」,结束答「本轮提升了哪项真实研究能力」(§七,写进 ITERATION_LOG 行)。
- [低优先候选] HK 双通道脆弱面/china 子源失败落盘/R13 审计 2 NIT/OPEN_ISSUES 按需取用。

<!-- RD-CHECKPOINT v1: json {"round": 43, "date": "2026-11-16 09:22 HKT", "branch": "dev/rd-r43-fragment-hardening", "commit": "88ccfe01b74ce8a73607e7263b7fb6b9742f67b1", "baseline": "88ccfe01b74ce8a73607e7263b7fb6b9742f67b1", "goal_sha": "7535a141b2339a13", "completed_ids": ["T-R43-1"], "next_task": "R44: 引擎轨道=B 族评分卡分值列/表内碎片硬化首位候选(R43 后 283 CONTRA 中居首: | +2 | 分值列绑行指标水平+散文总分 增长总分0、通胀总分+3 形态)+T8-R2 ④⑥⑦ 启封随批+R43 审计登记 MINOR-2 表内序号/NIT-2 未闭合注释/NIT-5 r1_vp_stages+R41 审计登记 MINOR-1+NIT-3~5+round.sh 双上限(LIVE 部署时);日历门 F=2026-12-05 勿手工提前", "next_round": 44} -->

## 下一步存档(2026-11-16 R43 收口后版)

- [已毕·R43] **A 族碎片泄漏硬化**(T-R43-1;RDG-20261116-013;R41 定性治面+RDG-012 残余⑦随批): 检查面预处理(HTML 注释/报告头元数据行/独立 JSON provenance 行,保守保留未闭合/坏行)+遮罩表四行(art_ 引用ID/#N 序号/紧凑 ISO 日期窗/子句首序号)+月-日日组必选根治小数误切分;真实面 **326→283**(removed 50 全实+added 7 token 全 verbatim 修复位升格,bad_added 0);独立审计四维终判**可并入**(MAJOR-1 N月D-D日裸日号新泄漏当场追修 _DATE_RE D[–—-]D日;MINOR-2/NIT-2/3/5 登记);随批 run_weekly.main(argv) 四件套 pytest 收集口径 IMPORT-OK 4/4;新套件 23/0+全库 165 OK+1 红(波中记账面);**R41 A=154 口径如实更正=簇级归因上界**;分支 dev/rd-r43-fragment-hardening;详见 ITERATION_LOG R43 双行与 t7_realface_r43.json。**操作者席: 合并发布+并轨尖重盖章(R32 判例)**。

## 下一步存档(2026-11-16 R42 收口后版)

- [已毕·R42] **测试聚合器吞错修复**(T-R42-1;RDG-20261116-012;R41 收口链 pytest 口径独立验暴露): 四套件 _run_case 测级异常计退出码(负证注入红)+TH fail-closed(缺键→RuntimeError 带键名)+t1t2/t4 两潜伏测复活+守卫套件 15/0;两潜伏错 main 同态既有(~14 轮),R41 盖章语口径误报如实更正;分支 dev/rd-r42-agg-error-leak;详见 ITERATION_LOG R42 双行。

## 下一步存档(2026-11-16 R41 收口后版)

- [已毕·R41] **T8-R2 余留①②③收口**(T-R41-1;RDG-20261116-011): ①真实面定性(诊断实验)=复跑 T7 三份真实周报 326 token 全簇裁定**全误报零真错**,contra/veri/unbound 与基线 e81d363 逐位零漂移,A 族碎片泄漏 154(47%)居首=硬化首位登记;真实面 0/3 维持/Gate B 继续值守(T7 原判)②band_label 双报 co_anchor 派生标记(状态零变动)③scorecard_spec 单源规格表(tc 表驱动+macro_scorecard 35 键推导+G2 门锚随迁强度不降);独立审计四维 PASS 0 B 0 M **可并入**(MINOR-1+NIT-3~5 登记);新套件 20/0+受影响面绿+全库 164 件(红仅 phase6 波中记账面);分支 dev/rd-r41-t8r2-leftovers;详见 ITERATION_LOG R41 双行与 R41_T8R2_LEFTOVERS_REPORT.md。**操作者席: 合并发布+并轨尖重盖章(R32 判例)**。

## 下一步存档(2026-11-16 R40 收口后版)

- [已毕·R40] **叙事方向守卫残余登记三项收口**(T-R40-1;R38 独立审计二轮附条件兑现,RDG-010 残余登记全闭): ①MAJOR-3b 当前周锚豁免(标记后锚→恢复核验,冻结 G5/G7/B2;锚在标记前不豁免)②MINOR-3 日内/英镑对美元(F5b)/USD-JPY③NIT-3 yen 幅度副词;新套件 test_rd_r40_narrative_guards 17/0+r38 回归 34/0;分支 dev/rd-r40-narrative-guards;详见 ITERATION_LOG R40 双行。

## 下一步存档(2026-11-15 R39 收口后版)

- [已毕·R39] **步骤台账跳过步 executed 优先判**(T-R39-1;R25 审计预存观察收口,NIT+观察全清): skipped_step ok=True 数据契约保留,两处台账(主+扇出)改 executed 优先判——跳过步渲 [SKIP|—]+skipped_reason 随行,SKIP 死码复活;新套件 test_rd_r39_skip_ledger 7/0+受影响 r2/r33/席位绿;分支 dev/rd-r39-skip-ledger(码波 cfc3128,净克隆 161/161 零红预验);操作者双收口链第二波(引擎 R38 并轨后紧接);详见 ITERATION_LOG R39 双行。

## 下一步存档(2026-11-15 R38 收口后版)

- [已毕·R38] **叙事方向检查器覆盖面表驱动扩展**(T-R38-1;引擎轨道余留 T8-R2 遗留⑤): RDG-20261115-010(接口或架构缺陷,五因子队列首位;开轮复现=「本周日元升值,美元兑日元159.88(+1.51%)」VERIFIED 零检查)——_NARR_FX_ROWS 表驱动(DXY/EURUSD 逐字迁入+GBPUSD 直读+USDJPY 主体反序+对名直读行)+逐命中前瞻守卫(前看窗 14/括注宿主窗 20/后缀预期对象)+交叉盘守卫 (?<![兑/对]) 全族回灌(main 既存「日元兑美元贬值」误读一并修);独立审计两轮=一审三 MAJOR(对名「对」/GBP 交叉盘/FN9 守卫连杀)→修 93364ce→二轮**可并入(附登记条件)**(残余 MAJOR-3b/MINOR-3/NIT-3 已登记队列);新套件 34/0+变异自证 4/4+受影响 11 套件绿+全库两遍 161 件(红仅 phase6 D3 波中记账面,净树复验 29/0);分支 dev/rd-r38-narrative-coverage;详见 ITERATION_LOG R38 双行。**操作者席: 合并发布+并轨尖重盖章(R32 判例)**。

## 下一步存档(2026-11-15 R37 收口后版)

- [已毕·R37] **coverage 审计序列权威 history_source 优先**(T-R37-1;R25 审计余留 Ni-5 收口,四 NIT 全清): 审计原按 source 声明通道判序列权威——DFF 10 年日频序列(n=3650,macro 通道)全判非权威=保守低报;修=auth_series_of(序列=history_source 优先,点=source)+authority_channel 同口径+可读性双流归并(任一权威通道不可读即 input_degraded,w4 b18 语义保持);新套件 test_rd_r37_history_source_auth 11/0+受影响 w4 族/p1_wp_a/r25 绿;分支 dev/rd-r37-history-source-auth;详见 ITERATION_LOG R37 双行。

## 下一步存档(2026-11-15 R36 收口后版)

- [已毕·R36] **R25 审计余留 NIT 三修·操作者紧凑波**(T-R36-1;引擎 19:xx 开班窗前直跑): Ni-3 三写点原子写(_atomic_write_text 临时+os.replace;_write_report 先渲 md 后落盘,渲染异常两文件都不动)/Ni-2 attach_history 追加链(≤5 轮,换代不抹旧,blocked+成功双路径)/Ni-4 副指标重复 SCN-FALS2 契约明示拒;附带=r25 旧夹具漏洞期望按新契约更新+契约数值绑定拦「R36 母本」装饰文案实证;新套件 tests/test_rd_r36_attach_nits 23/0+受影响 r23/r24/r25/r33 绿;分支 dev/rd-r36-attach-nits;详见 ITERATION_LOG R36 双行。

## 下一步存档(2026-11-15 R35 收口后版)

- [已毕·R35] **利差辖域披露升位+自对算术守卫**(T-R35-1;引擎轨道余留「利差裸别名歧义升披露」项): RDG-20261115-008(tc 利差辖域静默吞违反律8/T6 披露律→spread_ambiguous 披露+律8 辖域不豁免注记+consumed 被裁集机制)+RDG-20261115-009(_check_spread 相异指标守卫,自对 |v−v|=0 假红歼灭+真对取对顺修);独立审计两轮=一审 MAJOR-1(句级抑制吞)→修→二轮闭死四维 PASS 可并入;新套件 18/0+受影响七套件绿+全库两遍 157/158(红=phase6 D3 波中记账面,净树复验);分支 dev/rd-r35-engine-track;详见 ITERATION_LOG R35 双行。**操作者席: 合并发布+并轨尖重盖章(R32 判例)**。

## 下一步存档(2026-11-15 R34 收口后版)

- [已毕·R34] **席位接入真跑首验**(T-R34-1): 真跑 DXY×GOLD_F 全链五环贯通(披露→唤席→REVISE 裁决→归档→翻面);席位真拦下 SCN-A 越界标签=席位存在理由第二证;归档=audit/semantic_review/20261115/;详见 ITERATION_LOG R34 行。

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
