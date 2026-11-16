# AUDIT_R2_REPORT — 第二轮外部审计修复报告(2026-11-16)

> 审计对象: PR #1(github.com/bojing951-hash/investment-agent)分支 `dev/audit-fix-r1`,
> 受审基线 commit `06e90c18970bb23536af47666e03b6d0047c824c`(Audit-R1 冻结尖)。
> 本轮指令: MVP 收尾修复八项(§二),反例优先验证(§三),七件交付(§四)。
> 边界遵守: 未并 main / 未合并 PR / 未部署 / 未改远端权限 / 未瘦身
> (CODEBASE_SIMPLIFICATION 保持 DEFERRED)/ 不另开重复 PR / 无付费调用。
> 既有声明(「十项全关闭」「五门全通过」)不作为本轮验收依据——本轮
> 一切判定以下列可复核证据为准,无法验证处显式标 NOT_VERIFIED。

## 一、逐项关闭表(§二 八项)

| # | 项 | 状态 | 代码/工件位置 | 复验结果 |
|---|---|---|---|---|
| 1 | 审查绑定实际交付内容 | ✅关闭 | `scripts/agent_judgment.py`(content_digest v2=canonical(report.json 剥 semantic_review)+canonical(agent_judgment 剥 semantic_review),裁决档 content_sha256 绑定);`ia_cli.py:1576-1594`(copies_consistent=report.md 必须=report.json 当前渲染;当前 run_ok=False 不得沿用旧 attach) | F02 套件反例①(F1 只改 L1 事实值→旧裁决失效)、F2(attach 后 run_ok 翻 False→拒交付)、H1(只改渲染视图→copies_consistent=False 拒)全绿;套件 **33/0** |
| 2 | 裁决顺序与非法记录 | ✅关闭 | `scripts/agent_judgment.py:414-471`(record_semantic_verdict: revision/recorded_at 内容序+predecessor 链+必填字段落档即抛+**席位词表 fail-closed** SEAT_VERDICT_VOCAB);`_verdict_sort_key` 不读 mtime | F02 G1(旧 PASS+新 REVISE 拒)/G2(最新档损坏=corrupt_latest 不回退)/G3(缺字段)/G4(revision 重复=duplicate_revision)/G5(调换 mtime 结果不变)/H3-H5(生产写档+必填抛+越表词抛)全绿 |
| 3 | 清除错误统计及传播 | ✅关闭 | `docs/autonomous-rd/phase4/BLIND/`: blind_calc2.py(i=0 环绕修复+严格三桶)、judgment_mvp.json(五处数值更正,标记无数字形制)、report/FULL_REPORT/evidence_pack 三副本同步、BIGFILES.sha256 重出、MANIFEST.md v5 修订记录 | 全部自冻结序列重算(不复用开发报告值);更正后契约门 VERIFIED 11/0/0(unbound=0)+重挂链(digest `6178d550…`);**独立新席(blind-r2-reviewer,未参与修复,自写复算代码,无预期值)全量复算逐项吻合**→`audit/semantic_review/20261116/VERDICT-20261116T053623Z-02.json`(overall UPHELD,原席词 VERIFIED 按 R32 词表映射,档内注记;三项不阻断观察在档);旧 -01 失效保留(fresh=False);report 段四态=**deliverable=True, mvp_complete=True**, verdicts_n=2 |
| 4 | 可独立重放证据(F10) | ✅关闭 | `docs/autonomous-rd/phase4/F10/`: data_slice/(**原始输入切片**,schema 形状逐值拷贝,BRENT_F n=2515/WTI_F n=2514/BEI_10Y n=2498/BEI_5Y n=2498)、f10_calc.py(IA_ENGINE_ROOT 环境变量可配)、f10_replay.sh(一条命令)、REPLAY.md(三层版本记录: 编排=06e90c1 受审面/引擎树=ad2f6e4/数据=双 sha256) | **干净目录一条命令重放已验证 PASS**(输出 sha256 `6e5fcf4a…` 与归档逐字节一致);.gitignore `data/` 锚根(切片此前会被误剪出库,已修);计算脚本吃切片不吃计算输出(防冒充) |
| 5 | pytest 单文件入口 | ✅关闭 | `tests/conftest.py`+`pytest.ini`(三入口: 目录/单文件/-k;失败传播;rc 语义);`tests/test_pytest_entry_fix.py` | 本机(系统 py3.9)三入口直验;**候选 021092f 双口径: 直跑 176 件 176 绿 / pytest 目录跑绿**(数字见 §四);py3.11/3.12 矩阵=CI 面(R1 F04 既设,本轮未改动,云端结果见 §四) |
| 6 | 一次输入到最终归档 | ✅关闭(Audit-R1 F09+本轮链档强化) | `ia_cli.py` research-one 三段式+`--stage auto`(暂停恢复同 run 不重 plan);归档对象=终审受审版(裁决链与归档同摘要) | `tests/test_audit_r2_chain_archive.py` **12/0**(链档反例: 修订失效/归档一致性/裁决-归档同版绑定) |
| 7 | 中国任务缺失数据分级 | ✅关闭 | `scripts/research_orchestrator.py`(plan 段**采集前冻结** data_requirements: 问题词面命中=required;outcome 采集后评,不改判)+`scripts/agent_judgment.py:640-700`(attach 三级 blocked_class: critical_zero_evidence>required_data_missing>optional_data_missing;默认阻塞,--allow-failed-run 显式越过随档)+渲染披露「数据需求(运行前冻结)/任务目标缺口」 | F02 I1(必要缺席→required_data_missing 默认阻塞)/I2(旗标=过此级至校验层,不豁免校验)/I3(必要已满足不冤枉)/I4(披露行在场)**全绿**;不把 run_ok=false 永久拒发(critical 才无条件拒),不缩任务目标 |
| 8 | 治理与迁移边界 | ✅关闭(如实登记) | `scripts/gate_b_parallel_harness.py`(_input_face: sha256+bytes+自述 input_id/as_of;anchors_face;units_basis=metric_registry sha256);`tests/test_pc_phase2_gate_b_parallel.py` §D | **main 分支保护实测未配置**(认证 API 404 "Branch not protected"——治理发现,见 §六;未改远端权限);同源比较三件套+单位基随行 **27/0**;「全同才同源,任一不同=跨版本对照降级」注记在档;MC2 迁移保持 **PENDING**(裁定前不迁) |

## 二、候选分支与变更摘要(§四.2)

- 分支: `dev/audit-fix-r1`(覆盖推送至既有 PR #1,未另开)。
- 修复链 commit: `021092f02c52afedf8532fd2b677ca5123110309`(32 文件,
  +41370/-175,增量主体=F10 data_slice 两件原始输入切片入库)。
- 变更摘要: 八项修复(表§一)+ 收口配套三件——裁决词表 fail-closed
  (越表词落档即抛,本轮独立席档即被此守卫族正名的映射先例收口)、
  复杂度基线漂移登记(test_files +5.1%=审计回归面 9 件,非新框架,
  依章程§四.4 登记后重定)、F09 断言随装配面更新(节题扩「+Audit-R2 绑定面」)。
- 报告/台账 commit: 本件+ITERATION_LOG R47 行+CURRENT_STATE 快照(docs-only)。

## 三、A/B/C/F10 报告状态与重放入口(§四.3)

| 档 | 状态 | 入口 |
|---|---|---|
| A/B/C(PC Phase 4 三型验证) | 本轮未触碰其判断内容;机器面随全量套件绿(176 件);R1 独立席终审裁定继续在档;**本轮未重跑独立席终审(非指令范围),不重复声称** | `docs/autonomous-rd/phase4/{A,B,C}/` |
| BLIND | **修正闭环完成**: 数值更正→契约门 VERIFIED→重挂链→独立新席全量复算→UPHELD(-02)→四态 deliverable=True/mvp_complete=True→三副本同步 | `docs/autonomous-rd/phase4/BLIND/`(MANIFEST.md v5 修订记录) |
| F10 | **重放包完备**: 一条命令干净目录复算,输出与归档逐字节一致 | `sh docs/autonomous-rd/phase4/F10/f10_replay.sh`(期望 `F10 REPLAY PASS: 6e5fcf4a…`) |

## 四、测试与 CI(§四.4)

- 直跑口径: 候选 `021092f` 全量 `tests/test_*.py` **176 件全部 rc=0**。
- pytest 目录口径: 同候选 **绿**(本机系统 py3.9;详细计数以推送后 CI 为准)。
- 套件级增量: F02 28→**33**(条目 1/2 反例面+I 块+H5);gate_b §D **27/0**;
  F09 **20/0**;semantic seat **10/0**;phase6 **29/0**(提交后净树全绿)。
- CI: 推送后 PR #1 云端跑(R1 既设矩阵 py3.11/3.12);**结果栏在推送后回填**
  ——若红,以红为准继续修,不以本报告先行为准。

## 五、G0-G4 真实判定(§四.5)

不引用既有「五门全通过」声明作为依据。本轮如实分层:

| 门 | 本轮状态 | 依据 |
|---|---|---|
| G0 工程面可复核 | **机器面 PASS(操作者自跑,非独立席)** | 候选双口径 176/176 绿;F10 重放 PASS;净树守卫(phase6 D3)绿 |
| G1 判断面受约束 | 承 R1 独立席裁定(06e90c1 面);本轮增量=BLIND 修正档**独立新席复算 UPHELD**、四档+BLIND 契约门全 VERIFIED | -02 裁决档+契约门输出 |
| G2 链路真实可跑 | 承 R1 裁定;本轮增量=BLIND 全链真跑(attach→复审→复挂→交付四态绿) | §一.3 |
| G3 终审不走过场 | 本轮实证=独立席抓出并更正五处真实数值错误(NEW-2/NEW-3),且旧裁决按规则失效重裁——门有牙的正例 | §一.3 |
| G4 独立性 | BLIND 复审席=未参与修复的新鲜 general-purpose 席,自写代码、冻结数据起点、零预期值;三项不阻断观察如实保留 | -02 档 notes(复算方法全披露) |

**终裁=等待用户外部审计**(本报告不 self-certify G0-G4 整体通过)。

## 六、外部阻塞最小动作清单(§四.6)

1. **main 分支保护未配置**(认证 API 实测 404 "Branch not protected")——
   治理发现。建议用户在合并 PR #1 前启用(require PR+CI 绿);本轮未改
   远端任何权限(边界)。
2. **PR #1 合并裁定**: 候选就绪,等外部审计结论;合并=用户动作。
3. (非阻塞披露)py3.12 浮点末位: CI 矩阵在 R1 已分离处理;本轮本机无
   py3.12 解释器,该面以 CI 云端为准,本地标 NOT_VERIFIED。

## 七、恢复状态更新(§四.7)

- 产品仓: ITERATION_LOG.md 增 R47 双行(独立轨道,不入引擎 R 队列,
  承 R46 同制);CURRENT_STATE.md 权威快照换 R47(旧快照降历史区)。
- 引擎侧(~/agent-loop): 未动——审计轨道不写引擎 STATE(R46 先例)。
- 停点: **等待用户外部审计**。CODEBASE_SIMPLIFICATION=DEFERRED(未动)。
