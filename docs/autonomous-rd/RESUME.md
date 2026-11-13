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

## 下一步(2026-11-13 R22 检查点后 · Charter 10 整改队列)

> **唯一队列入口**(Charter 10 §3.1/§3.3)。已完成任务只进「下一步存档」与 ITERATION_LOG,永不回到本节。
> 恢复第一步: 读本节检查点块 → `git merge-base --is-ancestor <块commit> HEAD` 亲核(块 commit 以机器盖章为准,勿信任何手写 sha);不成立=状态可疑,先对账再动工。

按 CHARTER_10_RECTIFICATION.md §十一 阶段执行:

1. **阶段五 真实E2E+独立验收(当前最重要产品能力缺口)**: 未优化过的真实宏观问题(research-run→Agent 研判→research-attach→归档全链,§6.4 十章产出齐全);独立审计查结论-证据绑定;受影响 AC 重验按实标 PASS/PARTIAL/FAIL/NOT_VERIFIED。R23 遗留小项顺带: agent_judgment MINOR-1(矛盾陈述零引用放行,拟要求≥1 可解析引用或明示免锚)/MINOR-4(attach 不看 run_ok 拟加门槛提示)/MINOR-5(md L1 行渲 quality_status)+NIT(scenario 行类型锁)。
2. **阶段六 状态更新+自动入下一轮**。
3. **操作者席待办(R23 移交)**: R23 合并发布(dev/rd-r23-agent-loop,盖章=分支最后一笔合规);R22 席遗留(worktree /private/tmp/r21-wt 清理+钩子包 ops/hooks-candidate/ 安装+LIVE 观察 11-14 周六=ZQ 族观察钟)。

- 每轮开始答「当前最重要产品能力缺口」,结束答「本轮提升了哪项真实研究能力」(§七,写进 ITERATION_LOG 行)。
- [日历门不变] F 补证轮 2026-12-05/六标签首验窗+金油比 2026-12 引擎自动触发,勿手工提前(§八:算法正确性验收不等日历门)。
- [低优先候选] HK 双通道脆弱面/china 子源失败落盘/R13 审计 2 NIT/OPEN_ISSUES 按需取用。

<!-- RD-CHECKPOINT v1: json {"round": 23, "date": "2026-11-13 09:23 HKT", "branch": "dev/rd-r23-agent-loop", "commit": "29d046eb91128b533727c2273beaaa38e0f83d5f", "baseline": "29d046eb91128b533727c2273beaaa38e0f83d5f", "goal_sha": "7535a141b2339a13", "completed_ids": ["T-R23-1"], "next_task": "阶段五 真实E2E+独立验收: 未优化过的真实宏观问题(research-run→Agent 研判→research-attach→归档全链,§6.4 十章产出);独立审计查结论-证据绑定;受影响 AC 按实重验;顺带 agent_judgment 余留 MINOR-1/4/5+NIT", "next_round": 24} -->

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
