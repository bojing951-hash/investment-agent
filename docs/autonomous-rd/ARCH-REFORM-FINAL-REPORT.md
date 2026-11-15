# 架构整改最终交付报告(章程§十二九项)

> 依据: ~/agent-loop/CHARTER-ARCH-REFORM-2026-11-14.md §十二/§十三。
> 分支: dev/arch-reform-p3(main=aae0fe0 基点;26 提交 96d265e→3c8b5d4;
> 用户 2026-11-15 批准并轨→合并发 v0.24.0-alpha)。
> 结论行: 六阶段全毕+收口修复波;全库 154 套件 154 绿;真实面验收 A/B/D
> 全绿,C-real 未优化新问题真跑已毕(用户令执行,六判据全过)。

---

## 1. 架构根因报告

原始三故障(PHASE1-FAULT-BASELINE.md)+整改过程新证,按 Bug/架构/流程分类:

**架构缺陷(根因=语义非一等可验证数据对象)**
- 「文本猜义」类: 状态漂移(工作树状态档滞留)、Gate B 误杀(ZQ_IMPLIED_AVG
  提取器缺陷——R27 已修,本轮迁移门复位验证)、周报旧校验器「编号存在性
  冒充内容一致性」(R23 前的 validate_judgment 两 MAJOR 放行=RDG-002)。
- 「显示值冒充权威值」类: claim 端值锚误锚舍入位(RDG-001,T4/T5 首版
  9 条假红;与 T1/T2 设计裁决同因族,跨两模块)。
- 判例登记: RDG-REGISTRY.md 六条(001 端值锚/002 判定档脱钩/003 状态档
  滞留·证据不足类/004 分类器拦截·证据不足类·C-real 真跑后闭环/005 收口全库
  回归破旧·流程类/006 C-real 判定面两缺口·架构类)。

**Bug(局部修不复发)**
- ⑦a 首版越界扫描(交叉映射 AC 行误伤)——收口修复波修(与④同界)。
- p0 等价锁 worktree `==1` 环境假设(R28 引擎工作树加入即红,基线同红,
  非本轮引入)——改回落套件前基线。

**研发流程缺陷**
- 收口门缺「全库回归」步: 阶段四/五验收只跑整改新套件+代表旧套件,
  五旧套件破而未知(RDG-005;已纳入收口步,全库 154 复跑绿)。
- 双轨并轨状态面同步步骤缺位(RDG-003,单例,待第二实例定级)。

## 2. 新架构设计(六接口)

PHASE2-CONTRACT-DESIGN v1.2(律1-8)+PHASE4 设计档,落 docs/ARCHITECTURE_V2.md 底座之上:

| 接口 | 契约 | 实现 |
|---|---|---|
| 数据 | 快照/序列库(身份=metric_id@date,单位注册表权威) | series_store/registry |
| 证据 | 自包含证据面(55 事实+4 序列+17 观点+21 索引) | jc.build_face |
| 断言 | 统一 claim 六型(level/point/change±/statistic),tol=0.0 | claim_factory |
| AI 研究 | 判定档三类内容分派(客观事实→tc.check_text;统计结论→类B独立复算;经济解释→六查) | judgment_contract jc-v1.0-phase4 |
| 验证 | 六状态(VERIFIED/CONTRADICTED/NOT_VERIFIED/…)双向可判 | claim_verifier+tc-v3 |
| 交付 | attach 门控(契约非 VERIFIED→attached=False+blocked 落档) | agent_judgment 钩子 |

纯度律: research_contract 仅 stdlib+契约内件,零模型/零环境/零网络/零随机/零时钟。

## 3. 可运行实现

- scripts/research_contract/ 七件(thresholds/text_consistency/claim_factory/
  claim_verifier/judgment_contract/render_hook/__init__),scripts/thresholds_gate.py
  (G1-G4 三方对账),scripts/rd_state_consistency.py(①-⑦检查门),agent_judgment
  attach 钩子(+26 行,独立于 schema 层)。
- 提交: 96d265e(T1)→803c492(T2)→2936e5a(T1+T2 套件)→53a0508(S4b)→
  0f10022/56fb2df(T3)→f65b28c(T4)→09ed83e(T5)→ce13174/2565d66/0d7395e/
  6fe9794(T6a/b/c)→0fbd812(T7)→841e7c9/aafa350/5feba7f/3206565/e81d363(T8+
  整改+独立审计)→15359e8(阶段四)→f935947(阶段五)→37b31b8(阶段六)→
  a6a7a70(收口修复波)。共 24 提交,62 文件,+278723/−503(含 fixtures)。

## 4. 新旧系统对照(真实案例+失败案例)

- **旧链真实误杀**: T7 真实面双向定性——旧门对 V3 真实报告跨指标误杀
  (2/3 误杀),新链零误杀+FK-1..8 叙事面误报全拦(t7_results.json 在档)。
- **失败案例复位**: Gate B 五缺陷 45 判(R27 面)全复位;V1/V2 真实历史
  故障样本迁移复位(T8R 31 判)。
- **诚实记录——迁移门 T8 轮一 FAIL**: 真实面 0/3 定性(引擎容差与门零容差
  冲突),未降标,整改轮 12 项机制修复后 T8-R2 PASS @3206565。迁移结论
  唯一口径: 「**合成注入+改写变体集(含留出面)在预固定数值标准下通过,
  真实历史故障样本(V1/V2)复位验证通过**」。
- **判定档闭环**: V4 双向验收——错误版(pre_audit)7 CONTRA(两 MAJOR:
  「处年内低位」exp=95.6 百分位;「倒挂」叙事无所指),修订版 24 查全绿
  (test_arch_reform_phase4 57/0)。

## 5. 完整回归测试

- 整改新套件: t1t2/t3/t4(115)/t5(46)/t6a(28)/t6b(20)/t6c(26)/t7/t8r(31)/
  phase4(57)/phase6(26+C-real PENDING)/R20 扩展(15)。
- **全库清单**: 154 套件 154 绿(收口修复波后;证据=PHASE3-LOG 收口节
  for-loop 空输出+逐套件 tail 行)。
- 门: rd_state_consistency 7/7;thresholds_gate G1-G4 69 键 SIGNED;
  V5 21/21+V6 14/14 unmapped=0;公开面清洗(glm 族零)维持。
- CI: 分支未推 origin(整改分支不推=章程纪律);并轨后跑 CI=动作项。

## 6. 真实研究验收

- **真实宏观周报**: LIVE 周报面(2026-11-14 published:true,11-15 凌晨转正)
  ——v0.23.0 面,真实数据+真实拉取。
- **开放式 Agent Native 研究**: R24 真实 E2E 运行(HY_OAS×SPX×VIX×
  CURVE_2S10S,15 步 run_ok,agent 判定 attach+审计两 MAJOR→修订闭环,
  errors=0)——阶段六 C-det 结构面全绿(报告/judgment 原件在 dev 树,
  副本+MANIFEST.sha256 入 tests/fixtures/v4/)。
- **C-real(未优化新问题 WALCL×SOFR×DXY)**: 已毕(2026-11-15 用户令操作者
  会话执行)——15 步 run_ok;WALCL WARN=周频滞后如实;事实区 3 查全
  VERIFIED 零矛盾零未映射;L3/L4 诚实 declared-not-produced;六判据全过
  (机核=tests/test_arch_reform_phase6.py C4/C5)。真跑暴露判定面两缺口
  (面构建/别名表按周报语料口径,research-run 事实表未覆盖)→正道修并入
  3c8b5d4+RDG-006 登记;RDG-004(分类器拦截)随之闭环。跑台脚本+判据
  持久化=docs/autonomous-rd/phase6c/(仓内权威,/tmp 为易失副本)。

## 7. 自主研发机制整改有效性

- 根因决策门(RDG)并入任务准入: 登记簿 5 条(2 追认+3 生效线后),⑦b
  硬门负探针咬住(C12/C13);生效线后任务节全部引用在册编号。
- 验收如实: ⑦a 裸 PASS 禁标(收口修复波修界后交叉映射行不误伤)。
- 状态恢复: R20 恢复套件 5/0;检查点过期/悬空提交拒。
- 独立审计: T8 独立审计席(启封裁决)+T8-R2 独立复验(PASS);引擎侧
  R29 独立复审整改波 T2-T6a 322/0(双线分歧审计,引擎分支在档)。
- 机制自身吃狗粮: RDG-003(工作树状态档滞留)即⑦b 生效后首例——机制
  抓到自己工作面的失同步。

## 8. 迁移与回滚说明

- attach 钩子独立于 schema 层: 契约验证异常→NOT_VERIFIED 诚实降级,
  不影响旧校验路径;回滚=去钩子一行级。
- 阈值/契约版本钉死(thresholds v1.0-SIGNED/jc-v1.0-phase4/tc-v3-judgment),
  升版=新版本号+迁移注记,不改旧档语义。
- 整改分支未并 main: main 面零改动,回滚=弃分支,零影响;LIVE 全程跑
  旧管线未受触碰。
- 并轨后 LIVE 翻面脚本仍走用户终端亲跑先例(与 /tmp/deploy_v0230_live.py
  同模式)。

## 9. Git 提交与完整证据

- 24 提交(§3 列全),每 PASS 的执行证据: PHASE3-LOG 逐任务节(T1→收口
  节,命令+输出摘录,重放同结果=D8 证据重放判);QB 档真路径=dev 树
  research_archive 双重嵌套在案。
- 本报告+收口波= a6a7a70 后一笔 docs-only。

---

## 非阻断遗留清单(如实登记,不藏)

T8-R2 ①real-face 0/3 定性 ②band_label 双报 ③_check_score_total 硬编码
维度 ④era base_anchor_set 必填字段(下次启封随⑥⑦)⑤narrative checker
仅 3 指标 ⑥重封留出 ⑦变异压力轮;阶段四: 裸「利差」别名歧义吞 token
(零检查零未映射,登记待升披露)、真实模型语义审计席=NOT_VERIFIED 占位
(待用户授权);阶段五: 双轨并轨状态同步步骤(待第二实例)、引擎侧
round.sh 硬接线(LIVE 部署时);阶段六: C-real 已毕(六判据全过);
阶段二 T7 V4/V7 哈希冻结=DEFERRED(已注记)。

## 用户待办(2026-11-15 更新)

1. **C-real**: ~~用户终端亲跑~~ → 已毕(用户令操作者会话执行,六判据全过,
   见 §6;跑台脚本+判据已入仓 docs/autonomous-rd/phase6c/)。
2. **并轨裁定**: 已批准(2026-11-15「2,批准」)→ 合并发 v0.24.0-alpha;
   余下 LIVE 翻面仍走用户终端亲跑先例(/tmp/deploy_v0240_live.py)。
