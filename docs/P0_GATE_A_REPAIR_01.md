# IA-P0-1-FIX1 整改开发报告(Gate A 审计阻断项修复)

- 任务编号: IA-P0-1-FIX1(第一轮整改/P0-1第二轮)
- 契约: IA-P0-1-AC-v1.0(固定,未改动) + IA-P0-1-FIX1-AC-v1.0(本轮补充契约)
- 交付: 实现 Commit A = `68edefb170466dd698b40c712e06624c1390f53d`
- 本文档 Commit B: 见 `git log` 本文件首次提交(以最终 main HEAD 为下一轮验收基线)
- 开发日期: 2026-10-27
- 声明: 开发者自检不等于独立验收。本文所有"通过"均为本地离线运行的实际结果,
  命令与计数可复现(§8);CI未建立(§9),不宣称CI通过。

---

## 1. 本轮开发基线

| 项 | 值 |
|---|---|
| 本轮起点(第一轮实现) | `25ff6f81c7783dd7ac4735369b61e128063c7918`(round-1开发提交) |
| 原始审计基线 | `844fd3b`(P0-1验收结论所对照的代码态) |
| 推送前远端状态 | `origin/main = 25ff6f8`(fetch确认,无远端新提交,无需rebase) |
| 实现 Commit A | `68edefb`(代码+测试+CI定义文件,21文件 +1614/−188) |
| 文档 Commit B | 本文件(记录A的真实SHA,不预填) |
| 推送方式 | 非强推(`git push origin main`,25ff6f8..68edefb fast-forward) |
| 开发环境 | macOS(Darwin 24.6.0), `/tmp/inv-dev`克隆;基线对照用原始worktree `/tmp/inv-base@25ff6f8` |
| 测试解释器 | `~/AI内容/venv/bin/python3` = Python 3.9.6 |
| 依赖 | 被测模块全部仅Python标准库(无第三方包,见§9 CI说明) |

第一轮验收结论(1 PASS/10 FAIL/2 NOT VERIFIED;4/14 E2E场景违规)对应的
8项确认缺陷 IA-DEF-001~008,逐项修复情况见§2。

## 2. IA-DEF-001~008 实际修复情况

### IA-DEF-001(→FIX-01) 报告输入只验meta声明、未验实际内容 — IMPLEMENTED

问题: 第一轮的数据包/锚点/prompt核验只比对sidecar **声明的**摘要,改文件内容后
同步改meta声明即可逃逸。

修复(三层,全部"重算而非信任"):
1. **摘要重算**: 新增 `rp.digest_file(path)`(research_provenance.py:206,
   实际字节sha256[:16]);`verify_anchor_batch`第4环(research_provenance.py:336)
   将锚点文件实际字节摘要与meta声明比对——meta里的 `anchors_digest` 只是对照物,
   不再是信任源。
2. **确定性重建比对(锚点/prompt)**: `build_anchors(snapshot, ymd)` 与
   `generate_anchor_prompt_block(anchors)` 均为纯函数,核验时从**当日确定性选择的
   权威快照**重算锚点/锚点prompt,与磁盘实际内容canonical比对
   (research_provenance.py:339-356 / 359-377)。改锚点数值、增删残留指标、
   版本混用、prompt数字替换全部失配→拒绝。
3. **确定性重建比对(数据包)**: 本轮新增——`build_markdown(snapshot, ymd)` 为
   权威快照纯函数(data_assembler.py:92,已核实 `main` 落盘内容恰为其输出,
   data_assembler.py:266 旁挂pack_digest),`verify_research_inputs` 用它重算
   整个数据包内容与实际文件逐字节比对(report_generator.py:604-607)。
   改包内数字后**连meta摘要一起改**也逃逸不了(测试场景1b)。

证据: test_p01_fix1 §1(数据包数字改变,含改meta同步摘要变体)、§2(锚点数字
改变,含同步摘要变体)、§3(prompt内容替换)、§4(meta摘要被修改)全部拒绝,
且预检在GLM调用之前完成(GLM调用计数=0)。

### IA-DEF-002(→FIX-02) 失败报告可能覆盖既有合格报告 — IMPLEMENTED

问题: 第一轮生成失败/校验失败路径与正式发布路径交织,存在覆盖已合格周报的窗口。

修复(候选-先行事务, report_generator.py:1122 `generate_weekly_report`):
- 报告一律先写 `weekly_report_{ymd}_CANDIDATE.md`(save_candidate_report,
  report_generator.py:711);正式文件名只在最后一步 `os.replace` 原子发布。
- 发布顺序 = Gate B通过 → `write_report_status`(published=False, 先落盘status,
  report_generator.py:658) → `os.replace` 发布 → status刷新为published=True。
  任何一步失败走 `_quarantine_candidate`(report_generator.py:1204): 候选改名
  `weekly_report_{ymd}_UNVALIDATED.md`,**不触碰既有正式报告与其status**。
- 四类失败路径全部隔离: Gate B FAIL / 校验器**异常**(按FAIL分类)/ status写入
  失败 / 发布OSError → exit 3,既有合格报告字节不变。
- status侧防御: 对FAIL结果,若当日已存在published的PASS/DEGRADED status,
  `write_report_status` 把失败记录重定向到 `report_status_{ymd}_UNVALIDATED.json`
  (report_generator.py:679),失败记录的 `report_file` 只指向真实存在的文件。

证据: test_p01_fix1 §11(合格PASS报告→FAIL重跑: 正式文件字节不变、_UNVALIDATED
生成、主status仍PASS/published、失败status指向真实文件、无状态回写、exit 3)、
§12(校验器抛异常: 同上隔离)、§13(status写入异常: 不发布正式报告、候选隔离、
无回写;已有合格报告时同样不被触碰)。

### IA-DEF-003(→FIX-03) 关键采集失败未传导、旧文件自动放行 — IMPLEMENTED

问题: 第一轮采集步骤失败后,下游正式步骤依赖判定不完整;旧采集文件存在即被
当作当日数据使用,无新鲜度边界与披露。

修复:
- **依赖图重审**: run_weekly.py 11步依赖全部重新核对(快照构建无依赖,由Gate A
  裁决;步骤7/8/9依赖快照+4个关键采集器;步骤10加data_assembler;观察器
  step11无依赖,保持独立安全诊断R17语义)。关键采集失败→下游正式步骤SKIPPED
  且`skip_reason`指名上游(如"上游失败: 全球市场采集"),不静默跳过。
- **退出码**: 关键失败→exit 1(run_weekly.py:main),run_daily.sh透传。
- **观察器不被无理阻断**: 观察器自身依赖为空,采集失败日仍可对既有锚点执行
  观察核验(测试§9断言observer步骤执行)。
- **回退窗口与披露**: `resolve_inputs`(snapshot_builder.py:47)回退取旧文件仅限
  各源新鲜度窗口内(`lag <= window`, snapshot_builder.py:66),sources_status记
  `FALLBACK`+`lag_days`,build_markdown渲染披露"不得当作当日观测";
  **超窗→MISSING**,核心源缺失→`core_missing`→Gate A FAIL——旧文件存在不再
  自动放行(测试§9f: 11天旧global文件超窗→MISSING→SPX入core_missing→FAIL)。

证据: test_p01_fix1 §9(global/macro/china关键采集器失败参数化×3: exit 1、快照
仍执行、正式步骤SKIPPED带上游名、台账字段完整、allow=False;news非关键失败:
exit 0正式流程照跑;全成功+DEGRADED快照: exit 0+allow=True+快照身份入台账;
Gate A FAIL快照: allow=False;有效回退: FALLBACK+lag_days=3+披露入包;无效回退:
超窗MISSING+core_missing+FAIL)。

### IA-DEF-004(→FIX-04) 预测观察仅表层检查、无meta旧格式放行 — IMPLEMENTED

问题: 第一轮观察器仅校验通过即把预测写入长期观察,质量门禁没有下沉到写入引擎;
无meta/legacy批次曾按"兼容"放行。

修复(共享原语+双侧防御):
- 新增 `rp.anchor_quality_problem(info)`(research_provenance.py:220)统一口径:
  quality缺失→拒绝(不默认合格)/非法值→拒绝/FAIL→拒绝;
  PASS/DEGRADED(已验证+披露)/WARN(轻度提示)按既有规则处理。
- **观察器侧**: `_metric_problem`(daily_prediction_observer.py:87-96)对每个指标
  先过质量门禁;批次核验`verify_anchor_batch`(daily_prediction_observer.py:145)
  要求meta存在且source=snapshot——**无meta/legacy一律FAIL**(旧"兼容放行"行为
  已按FIX-04契约收紧,理由见§7末尾)。
- **引擎侧防御**: `allocation_engine.record_observations`
  (allocation_engine.py:578,质量检查:606/635)在前提激活与观测记录两条写入路径
  上再次执行同口径检查——绕过观察器直调引擎也无法把无效数据写入长期状态。
- 幂等/观测日/高低收/触达/过期/final等生命周期语义未改动;
  无效指标仅影响自身预测(批次内其余有效指标照常记录)。

证据: test_p01_fix1 §10(引擎直调: 缺quality/非法值/FAIL拒绝, WARN/DEGRADED
正常记录;观察器无meta→关键FAIL且观察历史文件字节不变;混合批次: 无效指标
被隔离、有效指标PARTIAL记录)。test_gate_chain_p01 §8共5项观察器子测试。

### IA-DEF-005(→FIX-05) Gate A声明与实际事实可矛盾、核心圈定口径不一 — IMPLEMENTED

问题: 第一轮Gate A以声明值为准,声明PASS但core_fail非空/核心事实实际FAIL等
矛盾不被发现;核心指标集合由各调用方自行圈定。

修复:
- **注册表为权威**: 新增 `rp.core_metric_ids()`(research_provenance.py:39,
  惰性缓存frozenset, registry中criticality=core且active);快照分级
  (snapshot_builder.py:267-277)与Gate A声明复核共用此口径。注册表加载失败→
  空集→得不到"核心"判定,**宁可无法证明,不可虚报**。未降低任何指标的
  criticality或校验阈值。
- **声明一致性裁决**(gate_status, research_provenance.py:58-102):
  声明PASS但core_fail/core_missing非空→拒;声明PASS但核心事实实际FAIL→拒;
  声明PASS但quality.overall非PASS→拒;声明DEGRADED但core_fail/core_missing
  非空→拒(core问题必须判FAIL);缺gate_a/状态非法/非对象→None(不得默认PASS)。
- **非核心单指标FAIL≠全局FAIL**: UMCSENT(非核心)事实FAIL→Gate A=DEGRADED
  (披露降级,可继续);SPX(核心)事实FAIL→Gate A=FAIL(阻断)。以真实
  `build_snapshot`全核心fixture验证(32核心指标全量采集)。

证据: test_p01_fix1 §7(声明矛盾×6变体全部拒绝/正确分级)、§8(真实build_snapshot:
PASS基线/非核心失败→DEGRADED+noncore_fail/核心失败→FAIL+core_fail/合法DEGRADED)。

### IA-DEF-006(→FIX-06) 快照修订身份核验缺口(文件名↔内部ID可冲突) — IMPLEMENTED

问题: 第一轮版本选择不核对文件名版本与内部snapshot_id一致性;同日重复版本号
静默覆盖;修订后旧批次锚点可续用。

修复(select_snapshot, research_provenance.py:150-196):
- 文件名解析出的版本 ↔ 内部`snapshot_id`(必须为`research_snapshot_{ymd}[_vN]`
  对应值) ↔ `target_date` 三者互相匹配,冲突候选→**整日拒绝**(不猜测回退)。
- **同日重复版本号**(`_v2.json`与`_v02.json`都解析为v2)→无法确定性选择→
  整日拒绝(research_provenance.py:184-187,本轮新增守卫)。
- `_v0`等非法版本→拒绝;JSON不可解析/缺snapshot_id→拒绝。
- 合法多版本: `_v3 > _v2 > base`确定性取最高修订版;**修订发布后**,
  绑定旧版本(base)的锚点批次在`verify_anchor_batch`第2环因snapshot_id失配
  被拒——旧批次不得续用。快照不可变性未改动(build_snapshot仅新增修订版本,
  不覆写既有文件)。

证据: test_p01_fix1 §6(_v2自称base ID→拒; 重复v2→拒; _v0→拒; target_date
冲突→拒; 合法v2+v3→选v3; 修订后旧base锚点→拒)。

### IA-DEF-007(→FIX-07) 月报/季报绕过质量门禁、与合格产物不可区分 — IMPLEMENTED

问题: 第一轮月报/季报入口直读历史原始采集序列生成输出,文件名与合格周报体系
无区分,存在覆盖合格月报/索引混入风险。

修复:
- 输出文件名显式 `monthly_review_{ym}_UNVALIDATED.md`
  (monthly_review.py:356) / `quarterly_outlook_{q}_UNVALIDATED.md`
  (quarterly_outlook.py:246),顶部HTML注释+可见横幅
  `⚠️ **UNVALIDATED 研究草稿**: 数据来源为历史原始采集序列直读…未经Gate A/B`
  (monthly_review.py:361 / quarterly_outlook.py:251)。
- 不覆盖任何既有合格文件(输出名含_UNVALIDATED不可能与合格名撞车);
  **不回写任何长期状态**(月报/季报路径无status/观察写入);
  周报glob(monthly_review.py:212)与季报索引(quarterly_outlook.py:169)
  过滤排除`_UNVALIDATED`。
- 历史分析能力保留: dry-run/期次完结判定/monthly_data/quarterly_data数据块
  构建逻辑未删减。

证据: test_p01_fix1 §14(草稿文件名+可见横幅<400字符内、合格月报不被覆盖、
monthly_data/quarterly_data块保留、季报索引排除_UNVALIDATED)。

### IA-DEF-008(→FIX-08) 台账/状态可追溯性缺口 — IMPLEMENTED

修复:
- **流水线台账** `logs/pipeline_run_{ymd}.json`(run_weekly.py:174-218):
  `run_at/run_date/duration_sec/steps[{name,ok,critical,skipped,skip_reason}]/
  success_count` + `ledger_provenance{research_target_date, snapshot_id,
  snapshot_file, snapshot_digest, gate_a, gate_a_reason |
  snapshot_unavailable_reason, allow_formal_report, allow_state_writeback}`。
  allow两标志 = 快照身份存在 ∧ gate_a∈(PASS,DEGRADED) ∧ 汇总打包步骤ok ∧
  校验锚点步骤ok(run_weekly.py:199-203)。
- **报告status**: `report_status_{ymd}.json` 记录真实文件路径+**重算的**内容
  摘要+Gate A/Gate B+最终质量+失败原因列表;status从不指向不存在的文件
  (quarantine路径的report_file指向实际存在的_UNVALIDATED文件);
  合格status不被失败尝试覆盖(§2 IA-DEF-002的UNVALIDATED重定向);
  诊断类写失败绝不静默标成功(write_report_status返回bool, False→exit 3)。

证据: test_p01_fix1 §9(台账字段逐项断言)、§11/§12/§13(status真实文件指向、
合格status保持、写失败不标成功)。

## 3. 代码路径(本轮改动)

| 文件 | 改动(行号为Commit A态) |
|---|---|
| scripts/research_provenance.py | `core_metric_ids`:39 / `gate_status`声明一致性:58 / `select_snapshot`身份+重复版本守卫:150,184 / `digest_file`:206 / `anchor_quality_problem`:220 / `verify_anchor_batch`五环核验:300 / `verify_anchor_prompt`:359 |
| scripts/report_generator.py | `verify_research_inputs`数据包确定性重建:604 / `write_report_status`失败重定向+摘要重算:658,679 / `save_candidate_report`:711 / `apply_status_updates`:1104 / `generate_weekly_report`候选-先行事务+四失败路径隔离:1122 / `_quarantine_candidate`:1204 |
| run_weekly.py | 依赖图重审:64(`run_pipeline`) / 台账ledger_provenance+allow标志:174-218 / `main` exit码:101 |
| scripts/daily_prediction_observer.py | 批次核验前置:145 / `_metric_problem`质量门禁:87-96 / 观察历史保护:168-178 |
| scripts/allocation_engine.py | `record_observations`双侧引擎防御:578(检查点606/635) |
| scripts/snapshot_builder.py | `resolve_inputs`回退窗口:47,66 / `build_anchors`:93 / `build_snapshot`分级:201(核心分级267-277) |
| scripts/data_assembler.py | `build_markdown`纯函数化确认+pack_digest:92,266 / `main`:241 |
| scripts/monthly_review.py | UNVALIDATED输出+横幅:356,361 / 索引过滤:212 |
| scripts/quarterly_outlook.py | UNVALIDATED输出+横幅:246,251 / 索引过滤:169 |
| scripts/data_validator.py / scripts/fact_engine.py | 锚点schema携带quality/批次标注配合改动(小改) |
| .github(未激活) | CI工作流定义移存 `docs/github_actions_tests.yml`(原因见§9) |

## 4. 测试路径

| 文件 | 角色 |
|---|---|
| tests/test_p01_fix1.py(**新增**, 81断言) | 14个强制对抗场景+FIX-03扩展(§7/§8);全部离线fixture+GLM mock,实际运行并核验文件副作用 |
| tests/test_gate_chain_p01.py(85断言) | §8观察器子测试重写为真实批次fixture;无meta期望按FIX-04收紧(§7末尾) |
| tests/test_round3_p0/round4/round5/round6/e2e_four_weeks/p2_fixes/round3_adversarial.py | fixture补锚点`quality:'PASS'`对齐新schema(见§7末尾,断言语义不变) |
| docs/github_actions_tests.yml | CI工作流定义(未激活,待workflow scope凭据) |

test_p01_fix1.py 场景→断言映射: §1数据包数字(1a仅改包/1b改包+同步改meta摘要)
§2锚点数字(2a/2b) §3prompt替换(数字交换+追加伪造行) §4meta摘要篡改
(anchors_digest/snapshot_digest) §5残留旧指标键(预检+观察器双侧) §6身份冲突
六变体+合法多版本+修订失效 §7Gate A声明矛盾六变体+四类非法/缺失声明
§8注册表权威(真实build_snapshot×4) §9采集失败传导×8 §10质量门禁双侧×8
§11合格报告保护 §12校验异常 §13status写异常 §14月报季报UNVALIDATED。

## 5. 旧AC-01~13自检(IA-P0-1-AC-v1.0,未改动)

| AC | 结论 | 本轮证据 |
|---|---|---|
| AC-01 Gate A三态语义 | PASS(强化) | gate_status新增声明一致性裁决(§2 DEF-005);test_p01_fix1 §7;既有套件§1回归通过 |
| AC-02 流水线关键失败/依赖 | PASS(强化) | 依赖图重审+台账allow标志(§2 DEF-003/008);test_p01_fix1 §9;round5 R17回归通过 |
| AC-03 装配器不得绕过Gate A | **PASS(本轮补全证据)** | 第一轮为NOT VERIFIED。现证据: (a)源码: data_assembler.py:241 `main`在gate不通过时exit 2不产包(逻辑在Commit A中,行241起); (b)行为: test_gate_chain_p01 §4既有断言(FAIL/缺字段→exit 2且无pack产出,无快照→exit 1)本轮回归通过; (c)auto-build移除在round-1已交付且本轮未回退(grep无auto-build路径) |
| AC-04 可验证来源绑定 | PASS(强化) | 从"声明绑定"升级为"实际内容绑定"(§2 DEF-001/006);test_p01_fix1 §1-§6 |
| AC-05 独立周报入口预检 | PASS(强化) | 预检扩展数据包确定性重建(§2 DEF-001);10种缺陷场景拒绝+GLM=0回归通过,新增场景1-6全部在GLM之前拒绝 |
| AC-06 Gate A+B正确合成 | **PASS(保持)** | combine_gates未改动;test_gate_chain_p01 §6十二组合穷举(含未知按FAIL)本轮回归通过(85/0) |
| AC-07 FAIL报告不冒充合格 | PASS(强化) | 候选-先行事务后,四失败路径全部_UNVALIDATED(§2 DEF-002);test_p01_fix1 §11-§13 |
| AC-08 长期状态保护 | PASS(强化) | 双侧质量门禁(§2 DEF-004);test_p01_fix1 §10;未清空/重置任何历史状态 |
| AC-09 遗留入口 | PASS | legacy批次显式拒绝(不再放行,见§7末尾);daily_report_generator声明未动 |
| AC-10 DEGRADED降级能力 | PASS | 非核心失败→DEGRADED继续+披露(§2 DEF-005 §8);test_p01_fix1 §8b/§9d |
| AC-11 状态/来源/跳过可追溯 | PASS(强化) | 台账ledger_provenance+SKIPPED指名上游(§2 DEF-008);test_p01_fix1 §9 |
| AC-12 核心功能无回归 | **PASS(本轮补全证据)** | 第一轮为NOT VERIFIED。现证据: §8完整回归——18个离线套件947断言0失败,逐套件命令与计数在§8;无测试被删除(test文件数只增不减;唯一期望修正见§7末尾,方向为收紧);test_phase4等日期腐坏修复未回退 |
| AC-13 测试/提交/交付证据 | PASS | 新套件test_p01_fix1(81断言)+CI定义文件;真实命令与计数见§8;本文件即交付证据;A/B两笔SHA见§1 |

## 6. 新补充契约(IA-P0-1-FIX1-AC-v1.0)自检

| 契约要求 | 结论 | 证据 |
|---|---|---|
| FIX-01 实际内容绑定(包数字/锚点数字/prompt数字/锚点meta摘要/残留指标/快照内部身份;摘要重算;确定性重建;失配→拒绝正式研究) | IMPLEMENTED | §2 DEF-001;test_p01_fix1 §1-§6(GLM=0前置拒绝) |
| FIX-02 合格报告保护(候选先行;FAIL/校验异常/status写失败/发布异常不触碰既有合格;失败记录指向真实文件) | IMPLEMENTED | §2 DEF-002;test_p01_fix1 §11-§13 |
| FIX-03 关键采集失败传导(11步依赖重审;正式阻断或证据化降级;SKIPPED指名上游;旧文件不自动放行;退出码;仅验证回退+披露;观察器不被无理阻断) | IMPLEMENTED | §2 DEF-003;test_p01_fix1 §9(8子场景) |
| FIX-04 预测观察验证(质量PASS进/DEGRADED记录/FAIL·缺失·非法拒;无meta·legacy拒;引擎写入路径同检;幂等/生命周期保持;无效指标仅影响自身) | IMPLEMENTED | §2 DEF-004;test_p01_fix1 §10;test_gate_chain_p01 §8 |
| FIX-05 Gate A真语义(注册表criticality权威;核心缺/败→FAIL;非核心败≠全局FAIL;缺质量不默认PASS;声明矛盾拒;不降criticality/阈值) | IMPLEMENTED | §2 DEF-005;test_p01_fix1 §7-§8(真实build_snapshot);注册表/阈值零改动(diff核查) |
| FIX-06 修订身份(文件名↔target_date↔snapshot_id↔revision↔digest↔meta全匹配;重复/非法拒;修订使旧包/锚点失效;不可变性保持) | IMPLEMENTED | §2 DEF-006;test_p01_fix1 §6 |
| FIX-07 月报季报旁路(UNVALIDATED标注;不可区分性消除;不覆盖;不回写长期状态;历史分析能力保留) | IMPLEMENTED | §2 DEF-007;test_p01_fix1 §14 |
| FIX-08 台账/可追溯(流水线台账字段全;报告status真实路径+摘要+门禁+质量+失败原因;不指向不存在文件;合格不被覆盖;诊断写失败不静默成功) | IMPLEMENTED | §2 DEF-008;test_p01_fix1 §9/§11-§13 |
| 14个强制对抗测试(实际运行+文件副作用,不接受源码字符串匹配) | IMPLEMENTED | test_p01_fix1 §1-§14(见§7表;断言对象为运行结果与磁盘文件字节/JSON内容) |
| 完整回归(逐套件命令/断言数/通过失败跳过;不许只给总数) | IMPLEMENTED | §8表 |
| 测试预期修正须解释且不降低原始标准 | COMPLIED | §7末尾(一处收紧+fixture对齐,零降低) |
| 不删除失败测试 | COMPLIED | 套件数19(18离线+1 live),文件零删除,仅新增1 |
| 独立复核证据(命令/版本/依赖/fixture/日志/代码路径) | IMPLEMENTED | §1/§3/§4/§8;日志为测试内嵌断言输出 |
| CI(可选) | **未建立(如实说明)** | 推送令牌缺workflow scope,GitHub拒绝创建.github/workflows/文件;定义已存docs/github_actions_tests.yml附启用步骤;**不宣称CI通过** |
| 技术约束(13项禁止) | COMPLIED | 无多Agent/无新Web服务/无DB迁移/模型未换/阈值未降/指标未删/历史状态未清/生产数据未改/launchd未动/未强推/无API Key提交/无付费调用(测试全mock)/未扩P0-2·P1 |
| 保留清单(81指标注册表/事实引擎/快照不可变/Gate A·B/评分卡/相关性/9论点/9配置视图/预测生命周期/周报8节/月季报能力/launchd/测试体系) | COMPLIED | diff仅触及§3所列模块的核验与事务逻辑;grep核查81指标与9论点完整 |

## 7. 原E2E-01~14测试结果

**诚实声明(必须先读)**: 验收指令引用的"E2E-01~14"原始编号定义留存于第一轮
验收方的验收材料中,**本仓库与开发侧留档均未保留其逐条编号文本**,本轮无法
按原始编号逐条自检——不伪造编号映射。验收指令同时给出了**14个强制对抗场景**
(其文字定义完整留存),两者系同一流水线链路的两套描述。下表按14个强制场景
逐条给出实际测试结果(全部实际运行、断言文件副作用,非源码字符串匹配);
**请验收方将其对应回原始E2E编号**重新核对,若某原始E2E场景不在下表覆盖内,
即为验收缺口,我方接受据此判NOT VERIFIED。

| # | 强制场景 | 测试(实际运行) | 结果 |
|---|---|---|---|
| 1 | 数据包数字改变 | test_p01_fix1 §1a(改包数字,meta未动→摘要重算失配拒);§1b(改包数字**并同步改meta摘要**→权威快照重建比对失配拒) | ✅ 双变体均拒绝,exit 2,GLM=0 |
| 2 | 锚点数字改变 | §2a(改锚点值→实际字节摘要失配拒);§2b(改值+同步改meta摘要→确定性重建失配拒) | ✅ 双变体均拒绝 |
| 3 | Prompt内容替换 | §3a(锚点prompt数字交换→重建比对拒);§3b(追加伪造指标行→重建比对拒) | ✅ 均拒绝 |
| 4 | 锚点摘要被修改 | §4a(anchors_digest改→与实际字节不符拒);§4b(snapshot_digest改→与权威快照不符拒) | ✅ 均拒绝 |
| 5 | 锚点残留旧指标 | §5a(锚点文件多残留键→预检重建比对拒+detail点名残留键);§5b(观察器路径同样拒,观察历史文件字节不变) | ✅ 双侧拒绝 |
| 6 | 快照文件名与内部身份冲突 | §6a(_v2文件自称base snapshot_id→拒);§6b(同日重复v2(_v2+_v02)→整日拒);§6c(_v0非法→拒);§6d(target_date≠文件名→拒);§6e(合法v2+v3→确定性选v3);§6f(修订_v3发布后,绑base的旧锚点→批次失配拒) | ✅ 六变体行为全部正确 |
| 7 | Gate A声明与实际事实冲突 | §7a(PASS+core_fail非空→拒);§7b(PASS+core_missing非空→拒);§7c(PASS+核心事实实际FAIL→拒);§7d(PASS+quality.overall=FAIL→拒);§7e(DEGRADED+core_fail→拒);§7f(非核心事实FAIL不触发核心复核误拒) | ✅ 六变体正确 |
| 8 | 非核心单指标失败 | §8b(真实build_snapshot, UMCSENT失败→DEGRADED+noncore_fail=[UMCSENT],继续);§8c(SPX失败→FAIL+core_fail=[SPX],阻断) | ✅ 注册表权威分级 |
| 9 | 关键采集失败后下游依赖 | §9a-§9c(global/macro/china失败×3→exit 1,快照仍建,步骤7-10 SKIPPED带上游名,台账allow=False,观察器step11仍执行);§9e(news非关键→exit 0正式流程照跑);§9f(超窗旧文件→MISSING→core_missing→Gate A FAIL) | ✅ 传导+不自动放行 |
| 10 | 缺少质量字段的预测观察 | §10a-c(引擎直调: 缺quality/非法值/FAIL→拒写入;WARN/DEGRADED→记录);§10d(观察器无meta批次→关键FAIL,历史文件不变);§10h(混合批次→无效隔离,有效PARTIAL记录) | ✅ 双侧同口径 |
| 11 | 既有正式报告被新失败报告尝试覆盖 | §11(先PASS发布→同日FAIL重跑: 正式报告字节不变;_UNVALIDATED生成;主status仍PASS/published;失败status写入UNVALIDATED侧车且指向真实文件;无状态回写;exit 3) | ✅ 合格报告受保护 |
| 12 | Gate B校验异常 | §12(validate_generated_report抛异常→按FAIL分类,exit 3,候选隔离,合格报告不动,status指向真实_UNVALIDATED文件) | ✅ 异常不炸毁事务 |
| 13 | 报告状态写入异常 | §13(status目录只读→write_report_status False→exit 3,不发布正式报告,候选隔离,无回写;预存合格报告仍不动) | ✅ 写失败不静默成功 |
| 14 | 无质量门禁的月报季报独立入口 | §14(输出`monthly_review_{ym}_UNVALIDATED.md`/`quarterly_outlook_{q}_UNVALIDATED.md`+可见横幅;合格月报不被覆盖;monthly_data/quarterly_data块保留;季报索引排除_UNVALIDATED) | ✅ 草稿不可区分性消除 |

### 测试预期修正说明(契约要求解释,并证明未降低原始验收标准)

1. **test_gate_chain_p01 §8 无meta锚点: 旧期望"放行(兼容)"→新期望"关键FAIL"**。
   原因: FIX-04契约明文"无meta/legacy批次拒绝进入正式观察",第一轮的兼容放行
   正是IA-DEF-004确认缺陷。此修正是**收紧**(原先允许的写入现在被拒绝),
   方向与验收标准一致,非降低。断言同时核验观察历史文件字节不变(无副作用)。
2. **7个旧套件fixture补锚点`quality:'PASS'`**(round3_p0/round4/round5/round6/
   e2e_four_weeks/p2_fixes/round3_adversarial)。原因: FIX-04使锚点schema新增
   quality字段,旧fixture无该字段即按新门禁=拒绝,触发81/22等失败。修正方式是
   给fixture补合法quality(模拟真实快照链生成的锚点本就携带quality),
   **断言语义零改动**。已用原始基线worktree(/tmp/inv-base@25ff6f8)对照运行
   确认: 这些套件在基线上通过、在我的引擎改动后失败、在fixture对齐后恢复通过
   ——证明失败源于schema对齐而非规则弱化。无任何断言被删除或放宽。
3. 无其他期望修正;无测试文件删除。

## 8. 完整回归测试结果(逐套件,非总数)

环境: `~/AI内容/venv/bin/python3`(Python 3.9.6,stdlib-only,无第三方依赖安装)。
命令模板: `cd /tmp/inv-dev && ~/AI内容/venv/bin/python3 tests/<套件>.py`(逐套件
独立进程;退出码全部为0,另跑一轮`|| echo NONZERO-EXIT`核验无输出)。

| 套件 | 断言 | 通过 | 失败 | 跳过 |
|---|---|---|---|---|
| tests/test_datafix_20261017.py | 13 | 13 | 0 | 0 |
| tests/test_e2e_four_weeks.py | 59 | 59 | 0 | 0 |
| tests/test_fact_engine.py | 59 | 59 | 0 | 0 |
| tests/test_gate_chain_p01.py | 85 | 85 | 0 | 0 |
| tests/test_p01_fix1.py(**新增**) | 81 | 81 | 0 | 0 |
| tests/test_p0_fixes.py | 22 | 22 | 0 | 0 |
| tests/test_p1_fixes.py | 36 | 36 | 0 | 0 |
| tests/test_p2_fixes.py | 82 | 82 | 0 | 0 |
| tests/test_p4_fixes.py | 43 | 43 | 0 | 0 |
| tests/test_p7_fixes.py | 30 | 30 | 0 | 0 |
| tests/test_phase3.py | 47 | 47 | 0 | 0 |
| tests/test_phase4.py | 20 | 20 | 0 | 0 |
| tests/test_round3_adversarial.py | 24 | 24 | 0 | 0 |
| tests/test_round3_p0.py | 91 | 91 | 0 | 0 |
| tests/test_round4.py | 94 | 94 | 0 | 0 |
| tests/test_round5.py | 64 | 64 | 0 | 0 |
| tests/test_round6.py | 51 | 51 | 0 | 0 |
| tests/test_snapshot.py | 46 | 46 | 0 | 0 |
| tests/test_glm_live.py | — | — | — | 整套跳过(需`RUN_GLM_LIVE=1`,真实GLM付费调用,按约束不进入本轮;见§9) |
| **合计(18离线套件)** | **947** | **947** | **0** | **0** |

阻断性失败: **无**。

## 9. 尚未验证的行为(如实列出)

1. **CI未建立,未运行,不宣称CI通过**。原因: 推送凭据(PAT)缺少`workflow`
   scope,GitHub拒绝以该令牌创建`.github/workflows/`文件(push被remote rejected,
   非强推保护生效的正常行为)。工作流定义已交付于`docs/github_actions_tests.yml`
   (ubuntu-latest + Python 3.11 + 逐套件循环,排除test_glm_live,零密钥/零网络/
   零付费),文件头附一键启用步骤;待持workflow scope凭据激活。§8全部结果为
   本地离线运行。
2. **真实GLM端到端未运行**: 按约束"未经允许不得调用付费模型",本轮所有GLM
   调用点均为mock(test_p01_fix1的_GLMRecorder校验prompt实际含锚点数字)。
   真实GLM生成→Gate B真实校验的组合留待验收方决定是否放行test_glm_live。
3. **launchd真实调度未验证**: 未触碰launchd配置(约束);修复后的run_weekly
   退出码/台账行为在测试中验证,但生产定时任务的实际运行日志未采集。
4. **生产目录同步后首跑未执行**: §10的同步清单已交付,但按约束未修改真实
   生产数据/状态,首跑观察留待用户/验收方执行。
5. **E2E-01~14原始编号映射**: 见§7诚实声明,需验收方复核映射。

## 10. 生产部署及历史文件兼容说明

**同步范围**(代码属同步,数据/状态/日志/密钥一律不动):
`scripts/{research_provenance, report_generator, daily_prediction_observer,
allocation_engine, snapshot_builder, data_assembler, data_validator,
fact_engine, monthly_review, quarterly_outlook}.py` + `run_weekly.py`。
`scripts/env_config.py`(密钥)与`data/ output/ logs/`**排除**。

历史文件影响(重要):

1. **旧锚点文件(无quality字段/无meta)**: FIX-04后**不再能进入正式观察**——
   这是IA-DEF-004的整改目标本身(来源不可证明的批次不得写入长期状态),不是
   回归。影响: 观察器对这类历史日期报关键FAIL并跳过,不损坏既有观察历史。
   处理: 需要正式观察的日期应经新流水线重建快照→锚点(自动携带quality+meta)。
2. **人工编辑过的数据包**: FIX-01的确定性重建比对会拒绝与权威快照不符的包
   (含手工修正数字的包)。处理: 修正应作用于上游采集/快照,包由流水线重生成。
3. **同日重复版本号快照**(如历史遗留_v2+_v02并存): 整日拒绝,需人工清理
   保留唯一合法版本后重跑。
4. **既有合格周报/status/观察历史**: 零影响——本轮所有失败路径均隔离至
   _UNVALIDATED,合格产物只读保护(test_p01_fix1 §11-§13即为该性质的行为锁定)。
5. **旧月报/季报**: 合格文件不动;新输出一律_UNVALIDATED命名,索引自动排除。
6. **launchd**: 配置未动,沿用既有调度;run_weekly退出码语义见§2(关键失败=1,
   预检失败=2,报告最终FAIL/隔离=3,成功=0),如外层脚本对非零退出码有告警
   联动,属预期增强而非故障。

---

*本报告为开发者自检,不等于独立验收。下一轮验收基线 = 本文档Commit B
(最终main HEAD)。*
