# Audit-R5 第五轮审计验收收尾报告

- 仓库: https://github.com/bojing951-hash/investment-agent(PR #1,分支 dev/audit-fix-r1)
- 受审基线: 49fb58303a69d53e663fc2717c15cfc166635786
- 收尾波次尖: 82b9398(波1) / 待补(波2)
- CI: 波1=run 44014788431 绿(gates+tests 3.11+3.12 三 job 全 success,job 133809993440/667/747) / 待补(波2)
- 日期: 2026-11-17

## 一、五项任务关闭表

| # | 任务 | 状态 | 关闭证据 |
|---|------|------|----------|
| 1 | 摘要迁移绕过审查 | ✅关闭 | `scripts/agent_judgment.py`: `_rebind_trusted_proofs`(manifest verdict_chain sha16 绑定源档+最早 git blob 双通道)+`rebind_verdict_digest` 对 v1/v2 未覆盖输入(`report.json`/`views_digest.json`)要求可信未变证明,不可证明=ValueError 拒绝继承;`uncovered_inputs_proof`+`from_algorithm` 随迁移档。测试 `tests/test_audit_r5_gate.py` §P(P1 无证明拒/P2 manifest 证明可迁移且交付/P3 篡改 vs manifest 拒/P4 v1 未覆盖集=双件/P5 旧裁决无效拒) |
| 2 | 数据门误放行 | ✅关闭 | `blocked_class_of` 重构: 必要零证据(critical_zero_evidence)与必要覆盖缺口(required_data_missing)**不论 run_ok 先判**(关 2A);run_ok=False 非拒答失败步→critical_step_failure 新阻断级(关 2B);仅 optional_data_missing 旗标降级;`ia_cli.py` deliverable=机器验证∧审查∧副本一致∧非阻断类,attach/report/archive 同判。必要观测下界按问题范围×频率族(`_question_range_years`×`_OBS_PER_YEAR_BY_FREQ`),规格记 frequency/window/coverage_observed/min_observations_basis。测试 §Q(Q1 2A 阻断+归档拒/Q2 2B S10 阻断/Q3 正常可选降级正例保留/Q4 未知失败类阻断/Q5 进程失败/Q6 归档正例)+§S(规格推导 S1-S6) |
| 3 | 新 E2E 报告修正+重审 | ✅关闭 | 三争点独立复算确认(操作者席+独立复审席双重复算): r=0.3383→r²≈0.114(约11.4%方差,同期相关非先行/因果,两镜像处);se 0.678/0.256→**0.686/0.259**;段终点 2022-05-26→**2022-05-25**(窗末05-26 r=-0.0148 已转负)+t 末位 +4.5→**+4.4**;口径披露补强(五序列交集 vs 金/美元对齐对2511)。判断JSON/运行JSON/报告正文/归档四副本同步。独立复审席(未参与修复,自写实现 /tmp/sr5r3/recompute.py,抽核30项: 28一致+2必修)→REVISE(rev2)→修订→闭环 **UPHELD**(rev3);旧裁决因内容变化自然失效(rev1 在链保留)。重放包 `docs/autonomous-rd/e2e-corrected-20261116T222254Z/`(研究脚本仓内固化版+独立复算脚本+七序列同版切片双 sha256+空目录一条命令);新归档 `research_archive/20261117T_修正后_…/`(链 UPHELD→REVISE→UPHELD,旧档 append-only 保留) |
| 3.9 | BLIND 文档勘误 | ✅关闭 | `docs/autonomous-rd/phase4/BLIND/REPLAY.md` 数值规范行勘误注: -0.557483 三位小数=**-0.557**,系进位错误,不应归为 sum/fsum 浮点噪声;非阻断(2dp 结论带不受影响) |
| 4 | 裁决格式与链校验 | ✅关闭 | 写入端 `format_version=2`+`digest_algorithm='digest_v3'` 显式;读取端 `_verdict_record_error`: 未知格式=invalid;revision 缺失仅容写位 0(位>0=删除 revision 冒充 legacy);predecessor 必填且=严格前一档(拒自指/后续/越位/跨任务);`_legacy_era_error` 锚=现行 v3 口径=降级攻击指纹阻断;历史失败档保留可经有效复审恢复。测试 §R(六形态 a-f+跨任务 g+隔离 h+生产写档三日链 i+legacy 头+rebind 混合链 j) |
| 5 | 中国任务 B | ✅关闭 | 数据层✅(§四)+研究层全链✅: 真实运行→attach(契约门两轮: 首轮 CONTRADICTED 正当拦截→措辞规约修订→VERIFIED 6/0/0)→**独立审查席 r5-b-review**(自写复算实现,抽核 99 项=96 一致+5 必修: MF-1 极值月相位归属 MAJOR/MF-2 PMI 边界两义混用 MAJOR/MF-3 贷款族 t 断言+格数/MF-4 方差派生/MF-5 时间框)→REVISE(rev1)→必要修订(判定档 18 处+研究席脚本相位块 5 处严格化源头修+冻结输出 v2 重生成+机制链字段渲染修;契约门复验 VERIFIED 6/0/0)→操作者席独立复算 57 项全 PASS→同一独立席闭环复验 **UPHELD**(rev2,24/24 复算吻合,旧错误串 14 串清零,周边统计逐字节不变)→归档 `research_archive/20261117T035814Z_中国宏观…/`(链 REVISE→UPHELD,run==archive==裁决锚三处一致);复算重放包 `docs/autonomous-rd/cn-task-b-20261117T035814Z/`(被审原件快照+两席复算脚本+输入哈希+空目录一条命令) |

## 二、复现与回归纪律(每项先复现再修)

- 基线复现工作树 `/tmp/audit_r5/baseline/`(49fb583): 条目1 迁移绕过、条目2A run_ok+覆盖缺口放行、条目2B S10 失败归可选、条目4 链缺陷——四路在基线**误放行/误接受证实**,修复面全部阻断(证据 `/tmp/audit_r5/evidence_baseline_49fb583.txt`+四个 repro 脚本)。
- 修复后回归: `tests/test_audit_r5_gate.py` 29/0;相邻套件夹具对齐生产写档形(VERIFIED→UPHELD 映射+revision/predecessor/fv/algo): r1_f02 34/0、r2_chain 12/0、r4_gate 29/0;全电池仅 phase6-D3(干净树门)提交前红=设计行为,提交后 **29 PASS/0 FAIL**。
- 真实面复验: 既有五个归档链(A/C/BLIND/F10/旧E2E)在新校验下全链有效(legacy 头=正当历史,不回溯破坏);E2E 修正后走完整真实链(修正→attach→独立审→REVISE→修→闭环→交付→归档)。

## 三、条目3 数字勘误明细(修正前→后)

| 位置 | 修正前 | 修正后 | 依据 |
|------|--------|--------|------|
| mech[0].links[0] | 「约三成方差与油价同向,供给冲击是BEI上行的可观测先行载体」 | 「r²≈0.114,即油价日变动仅能解释BEI日变动的约11.4%方差(含截距一元线性回归口径);同期(当日对当日)统计关联,不构成先行关系,也不能解释为供给冲击的因果贡献」 | r=0.3383²=0.1145;同期相关非先行;统计非因果 |
| contradictions[1] | se0.678 / se0.256 | **se0.686 / se0.259**(t 末位 +4.5→+4.4,精确4.4489) | 经典标准误 df=n−k;β/R² 原值复核吻合 |
| contradictions[0]+mech[2] | 最长非负段 55窗 ..2022-05-26 | **..2022-05-25**(窗末05-26 r=-0.0148 已转负) | 逐窗复算;独立席交叉确认 |
| 口径披露 | 全样本与滚动窗对齐集未区分 | 五序列交集(n=2493)/金美元对齐对(2511→2449窗)分别标注 | 两数各自正确但口径未披露 |
| 随修(次要) | 「油跌日(n=24)」「BRENT_F,n=2514」 | 「油未涨日(收益≤0,n=24)」「GOLD_F/DXY,n=2514;BRENT_F,n=2515」 | 独立席复算建议,随修 |

## 四、条目5 中国任务 B

**数据层(必要历史补齐)**: CN_PMI_MFG/CN_NEW_LOANS 经既有 R25
`history_source: macro_collector` 机制接入 **226 个月全史(2008-01..2026-10)**,
零加载器代码改动;来源/定义/单位/频率/观测日锚/发布时点/修订口径全部登记于
`config/metric_registry.json` calc+`macro_20261117.json cn_history_addendum`。
锚点核验: PMI 2026-10=49.3 与统计局一致;贷款累计 2026-10=109149 亿与央行
「前十个月对实体 10.91 万亿」逐位一致;**口径诚实标注=对实体经济人民币贷款
(社融口径),非全口径新增贷款**(全口径对照数字入注记),未用最新单点冒充、
未改必要为可选、未换题。

**研究层**: 真实运行 20261117T035814Z(S4 四必要指标全 satisfied: FXI n=2513/
CHINEXT n=2427/CN_PMI_MFG n=226/CN_NEW_LOANS n=226)→研究席判断档
(9 claims/4 chains/3 contradictions/4 scenarios,E1=4/E2=4/E3=3,诚实弱/零发现:
40 格先行相关网格全 |r|≤0.176、相位组间不显著、双重收缩同态反号)→attach
契约门首轮 CONTRADICTED(验证器正当拦截: 条件统计被误绑客观事实)→措辞规约
修订(等式括注/概率辖域/日期锚形,数字零改动)→VERIFIED 6/0/0→生产写挂载。

**独立审查→必要修订→闭环→归档**(审查链全程):
- **独立审查席 r5-b-review**(未参与研究,自写复算实现零引用研究席代码,
  `/tmp/sr5b/recompute.py`,仓内副本 cn-task-b 包 review_seat/): 抽核 99 项=
  96 一致+**5 必修**——MF-1(MAJOR) 极值月相位归属错误(两个 -23.0% 月在
  k=1 信号相位下属 PMI>50 信号组,『同相位内并存』仅在未披露的 k=0 口径成立);
  MF-2(MAJOR) 『PMI<50』边界两义跨块混用(相位块=≤50 含 3 个 PMI=50.0 月,
  MW/截尾=严格 <50,同句并列两样本);MF-3 贷款族『全部 |t|<1.6』失实
  (max=1.86,p=0.066)+先行格数 36-40 实为 30+n 区间;MF-4 『2/3 方差互不
  共享』应为 1-r²≈88%;MF-5 『2026 年内』含 2025-08 自相矛盾。→ **REVISE**
  (verdict 链 rev1,`audit/semantic_review/20261117/VERDICT-20261117T035814Z-01.json`,
  被审原件快照=包内 prerevision/)。
- **必要修订**: MF-2 采纳严格 <50 全文统一并**源头修**——研究席脚本相位块
  边界改严格两侧(PMI=50.0 持平月 3 个不入组,ΔPMI/CI 相位块同根因一并
  严格化),冻结输出 v2 重生成(与 v1 差异仅限两个 PMI 相位块,闭环席逐字节
  核);判定档 18 处修订(CON-1/CL-2/CL-3/CL-4/MC-1/MC-3/CTR-1/CTR-2/
  SCN-1/3/4+caliber 声明);随修两件=CON-1 竞争性解释 3 残留 p=0.350(闭环席
  先于协调方补充声明独立发现)与机制链环节字段 statement→text(B 判定档原用
  statement 致 report.md 机制链渲染为 None,按 E2E 先例与渲染器口径改名,
  11 环节纯改名);契约门复验 VERIFIED 6/0/0,生产 re-attach 通过。
- **操作者席独立复算**(cn-task-b 包 independent_recompute.py,修订后口径):
  **57 项全 PASS**(含严格组全部新数字、MW 同口径 p=0.120、贷款族 t 网格
  max=1.86、1-r²=0.876、持平月 3 个、截尾/FXI 端)。
- **闭环复验**(同一独立席,只核修处): 五项必修逐项 PASS,24/24 复算吻合,
  无新必修,旧错误串 14 串判定层清零,周边统计不变,结论方向未变 →
  **UPHELD**(rev2,`VERDICT-20261117T035814Z-02.json`,predecessor=rev1;
  闭环脚本 review_seat/closure_check.py)。
- **归档**: `research_archive/20261117T035814Z_中国宏观信用与制造业景气_CN_NEW_LOANS_
  新增贷款与_CN_PMI_M/`(7 件+verdicts/ 两档,ARCHIVE_MANIFEST
  content_sha256=2c6dd413…==rev2 绑定,run==archive==裁决锚三处一致)。
- 复算重放包: `docs/autonomous-rd/cn-task-b-20261117T035814Z/`(研究席脚本 v2
  逐字节重放+两席独立复算脚本+4 输入切片 sha256+被审原件快照+审查链全档)。

## 五、最终版本全量测试

- **净克隆直跑口径**(波2 尖 09e4ebb 本地净克隆,178 件逐件): 175 绿+3 红——
  3 红(test_arch_reform_phase6/test_rd_r20_state_checkpoint/test_rd_r20_state_
  consistency)同根因=**R20 门②正道拦截**(波2 提交含 R49 日志行但检查点块
  仍 round 48,「日志越过检查点」)——系波2 收口漏跑 `rd_checkpoint.py
  --finalize`,非代码缺陷;gates/tests×2/phase6 D1+D4 三 job 五面全指同一
  检查(CI run 44023144279 红)。**正道修复**: 按 Charter10 §3.2 对账恢复
  (CURRENT_STATE 权威快照 R49 版+RESUME 活动区/存档+finalize 机器盖章
  round 49),修复后净克隆复验全绿(下方)。
- **CI 波2**: 首推 run 44023144279 红(上述单根因);对账恢复 docs 尖重推后
  run=终笔回填。
- **修复后净克隆双口径**(收口尖): 直跑 178/178 绿+pytest 目录
  178 passed/0 failed(终笔随 CI 一并核对)。

## 六、项目状态与恢复说明

- **五项任务全部关闭**(§一);条目5 审查链全程落档(§四)。
- 分支 `dev/audit-fix-r1`(PR #1),波1 尖 `82b9398`,波2 尖=本提交;未并 main、
  未合并 PR、未部署、未改远端权限;治理发现维持(Audit-R2 §六: main 保护未
  配置,建议合并前启用)。
- 引擎 R 队列与本轮独立轨道互不干扰(工作树/暂存引擎根分离);本轮暂存引擎
  `/tmp/audit_r5/engine_cn` 与仓树存在已知渲染器漂移(早于波1 条目2 改动的
  rsync 基面),仅影响 report.md 视图渲染不影响数据/判定,B 归档前已用仓内
  当前生产渲染器重渲并通过 copies_consistent 门——后续暂存引擎重建应从波2
  尖 rsync。
- 恢复入口=本报告+`docs/autonomous-rd/cn-task-b-20261117T035814Z/`(重放包)
  +归档 `research_archive/20261117T035814Z_中国宏观…/`(B)+`20261117T_修正后_…`
  (E2E)+其余六档;裁决链 `audit/semantic_review/20261117/`(B 两档+E2E 三档)。
- **当前状态: 五项任务收口完毕,停止在「等待外部审计」;不自行宣称最终验收
  通过。**

## 七、七项最终交付

1. **HEAD/分支/PR/双版本 CI**: 分支 `dev/audit-fix-r1`(PR #1,受审基线
   49fb583);波1=82b9398,CI run 44014788431 绿(gates+tests 3.11+3.12,
   job 133809993440/667/747);波2=本提交,CI=§五回填。
2. **五项任务关闭表**: §一(五项全 ✅)。
3. **A/B/C/BLIND/F10 及修正后 E2E/中国任务 B 报告与归档状态**: 既有五链
   (A/C/BLIND/F10/旧E2E)在 R5 新校验下全链有效(§二,旧档 append-only 保留);
   修正后 E2E=`research_archive/20261117T_修正后_美国盈亏…/`(链
   UPHELD→REVISE→UPHELD);中国任务 B=`research_archive/20261117T035814Z_
   中国宏观…/`(链 REVISE→UPHELD,本波新增,§四)。
4. **重放入口与输入哈希**:
   - BLIND: `docs/autonomous-rd/phase4/BLIND/REPLAY.md`(冻结输出拼接
     sha256=feaa1536dc19404fd316cebada87caa8076884b106dd5b6426c379b93dee1c23;
     切片源 research_snapshot_20261112_v2/macro_20261112 哈希在该档)。
   - 修正后 E2E: `docs/autonomous-rd/e2e-corrected-20261116T222254Z/`
     (data_slice.json provenance 载七序列同版 sha256;两脚本空目录一条命令)。
   - 中国任务 B: `docs/autonomous-rd/cn-task-b-20261117T035814Z/`(4 输入
     切片 sha256 全载于 README §输入哈希;研究席脚本逐字节重放+两席独立
     复算;净克隆实测见 §四审查链)。
5. **独立审查记录及完整修订历史**: E2E=audit/semantic_review/20261117/
   VERDICT-20261116T222254Z-01/02/03(UPHELD→REVISE→UPHELD,修订明细
   AUDIT_R5 §三);B=VERDICT-20261117T035814Z-01/02(REVISE→UPHELD,五必修
   与逐项闭环结论在档,被审原件快照+两席复算脚本随 cn-task-b 包);操作者席
   独立复算=B 包 independent_recompute.py 57 项全 PASS。
6. **最终版本全量测试结果**: §五。
7. **项目状态与恢复说明**: §六。

> 没有证据的项目标记 NOT_VERIFIED。本报告完成时停止在「等待外部审计」,不自行宣称最终验收通过。
