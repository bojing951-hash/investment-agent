# IA-P03-W2-GLM-WP-G3 执行报告(可反驳条件推导与门禁对接+档案衔接)

> 工作包: IA-P03-W2-GLM-WP-G3(G 族第 3 包: WP-G3 可反驳条件推导与门禁对接+档案衔接)
> 分支: `dev/p03-w2-glm-g3`(自基线 `2f03be1fd77677b43d3afb7946af07c725625a2a` 切出,纯线性,本包无并入步)
> 冻结合同: IA-P03-W2-GLM-WP-G3-AC-v1.0(2026-11-05 03:3x HKT 冻结生效;本报告为合同 §零登记制落点)
> 边界声明: 本包**零真实 GLM/LLM 调用、零凭证、零付费、零网络出站**(设计对象≠设计手段;真实调用属 WP-G4,执行前置=用户批准凭证/费用,PENDING 未批)。日期/SHA/结构编号/档键成分按合同边界出圈登记: 本文日期时刻均为 UTC(另注明者除外);SHA 一律全值;HY-/RT-/QB- 前缀=标识符非数据值。

---

## §零 规格抄录与交付面登记(合同 AC-01 落点;开工首步)

### 0.1 WP-G3 行四要素逐字抄录(实读 `docs/P03_W2_GLM_DESIGN.md` §七,基线工作树实况)

以下为 DESIGN §七 WP-G3 行**逐字抄录**(无增删改字;行号=基线 2f03be1 工作树实读行号,审计对照允许偏差≤3行):

- **L228**: `**WP-G3 可反驳条件推导与门禁对接+档案衔接**`
- **L229**: `- 目标: 落地§五(1)推导规则、(2)Gate B 三态提案路径、(3)append-only 结论记录与 ID 交叉引用。`
- **L230**: `- 范围: 条件推导校验+门禁提案适配层+共享档案结论集合;预测候选落 allocation_views 侧沿既有门禁。`
- **L231**: `- 依赖: WP-G2;任务字段映射以 E2E-A schema 字段集为契约(注入基线;E2E-A 未落地时以契约测试固化映射表,实现落地后按登记型修订承接)。`
- **L232**: `- 验收要点草案: ①推导规则四步用例(可规格化/不可规格化分流)(工件: 测试文件) ②门禁提案测试: 无触发器且新增证据不足→提案被拒+留档(与现行门禁同构断言)(工件: 测试文件+allocation_engine 机制引用) ③append-only 测试: 结论记录改写被拒+交叉引用字段校验(工件: 测试文件) ④E2E-A 字段映射契约测试(工件: 测试文件+注入摘要引用) ⑤CI 零回归(工件: run ID)。`

四要素齐备(目标/范围/依赖/验收要点),无缺失。**冲突自查(合同 §零(iv))**: 要素齐备可推导 ✓;范围=确定性结构(条件推导校验+门禁提案适配层+档案结论集合),不含真实 GLM 调用/网络/新数据源凭证(与 WP-G4 分层一致)✓;依赖列「WP-G2」与基线实况一致(基线 2f03be1=WP-G2 最终交付尖端,`scripts/glm_output_validator.py` 在场,实读接口见 §一)✓,不要求并入他支(本包无并入步,合同 §零 定值)✓;依赖列「E2E-A schema 字段集为契约(注入基线;E2E-A 未落地时以契约测试固化映射表,实现落地后按登记型修订承接)」——E2E-A 已落地于基线谱系(`scripts/research_task_manager.py` 在场,`SCHEMA_MIN_FIELDS` 实读=10 字段,见 §一.1),按该行明示的登记型修订承接路径,映射契约以工作树实读 schema 为准+契约测试固化(无冲突: 实读字段集与 DESIGN §五(4) 表字段集相容,登记 §二.3)✓ → 无情形(d)冲突,合法开工。

### 0.2 交付文件清单(登记制白名单,k=4;推导逐条附 DESIGN 依据)

DESIGN L230 范围列为**模块级**(「条件推导校验+门禁提案适配层+共享档案结论集合」=单一结论整合模块的三项能力,「预测候选落 allocation_views 侧沿既有门禁」=该模块的第四项输出面而非新模块——allocation_views 侧落档沿既有回写链,不改 allocation_engine)而非文件级 → 按合同 §零(ii) 固定推导规则生成:

| # | 路径 | 类型 | DESIGN 依据 | 推导规则 |
|---|---|---|---|---|
| 1 | `scripts/glm_conclusion_integrator.py` | 代码(结论整合模块) | DESIGN L229「落地§五(1)推导规则、(2)Gate B 三态提案路径、(3)append-only 结论记录与 ID 交叉引用」+ L230「范围: 条件推导校验+门禁提案适配层+共享档案结论集合;预测候选落 allocation_views 侧沿既有门禁」 | 每个代码模块 = `scripts/` 下恰 1 文件 |
| 2 | `tests/test_p03_w2_glm_g3.py` | 测试 | DESIGN L232 要点①-④工件「测试文件」 | 含代码则必含本文件(合同固定名) |
| 3 | `docs/P03_W2_GLM_G3_REPORT.md` | 文档(本件) | DESIGN L232 工件面(要点逐条证据映射/参数登记落点);合同必含件 | 必含 REPORT |
| 4 | `docs/P03_W2_GLM_G3_DELIVERY.md` | 文档(交付说明) | DESIGN L254 交付说明惯例(参照 GLM 设计交付件与 G1/G2 先例);合同必含件 | 必含 DELIVERY |

**结构约束核验(iii)**:
- 与 `git ls-files` 零重合: 上述 4 路径在基线 2f03be1 工作树**不存在**(开工时全仓库 grep `glm_conclusion_integrator|test_p03_w2_glm_g3|P03_W2_GLM_G3` 零命中,`git ls-files` 基线计数 269 文件,取证见 §四)✓;
- 必含 DELIVERY ✓(#4);含 `.py` 实现(#1)则必含对应 tests(#2)✓。

DESIGN L232 工件名为泛称「测试文件」,与合同固定推导名 `tests/test_p03_w2_glm_g3.py` 无冲突(无 glob 级偏差;对照 G1 命名偏差先例,本包无此项)。要点④工件含「注入摘要引用」=DESIGN L231 依赖行明示的注入基线承接,落 REPORT §一.2 引用登记(标注「注入摘要,非工作树实读」)+测试内 fixture 注释。

### 0.3 运行产物边界登记

WP-G3 验收要点①-④工件=**测试文件**(离线合成 fixture 驱动,确定性样例),要点⑤工件=GitHub Actions run ID(操作者 CHECKPOINT dispatch)。结论整合模块**无编排入口/无真实运行要求**(对照 E2E-A `--run-e2e` 先例: 其合同要点明文要求真实回放,WP-G3 行无此要素;与 G1/G2 同款)→ 本包登记「**零运行产物**」: `data/research/` 无新增运行档案,`data/daily/` 与既有快照全程只读零触碰。依据=DESIGN L232 逐要点工件清单(实读,见 §0.1 抄录)。档案落档函数(`append_conclusion_record`)为注入面 API(archive 由调用方注入,测试用合成档案;生产落 `data/research/` 属编排层 WP-G4 范围,本包零调用)。

---

## §一 前置实读登记(数据接入点与机制引用,file:line 为基线 2f03be1 工作树实读)

### 1.1 依赖模块接口(依赖行「WP-G2」+E2E-A schema 契约落点;复用调用,禁复制分叉)

| 机制 | 落点(file:line) | 用途 |
|---|---|---|
| G2 登记清单(合同 AC-05.5 对照同源) | `docs/P03_W2_GLM_G2_REPORT.md:24`(§0.2 k=4) | G2 交付文件对照面(本包零改动其 4 文件) |
| G2 输出契约校验 `validate_output` | `scripts/glm_output_validator.py:234` | 门禁提案数值校验前置复用(结构化面数值接地,数值校验前置第一层;复用调用) |
| G2 合法阈值并集 `legal_target_numbers` | `scripts/glm_output_validator.py:186` | 推导步2 阈值三来源并集(复用调用;`prior_trigger_targets` 参数=G2 预留给 G3 编排层的结构化触发值注入面,G2 REPORT §二.3 登记) |
| G2 阈值来源(ii)字段族 | `scripts/glm_output_validator.py:57`(`REGISTRY_THRESHOLD_KEYS`) | 推导步2 来源(ii) 提取字段集同源(复用引用,禁复制分叉) |
| G2 派生窗口值字段族 | `scripts/glm_output_validator.py:58`(`_DERIVED_VALUE_KEYS`) | 推导步2 来源(i) per-metric 在场值字段集同源(复用引用,禁复制分叉) |
| G2 spec 枚举 | `scripts/glm_output_validator.py:42-43`(`SPEC_OPS`/`SPEC_MODES`) | 推导步3 规格化 op/mode 枚举(与现行预测规格对齐;复用引用) |
| G2 假设-证据映射表 `build_hypothesis_evidence_map` | `scripts/glm_output_validator.py:521` | 投影层 evidence 方向化挂载输入(复用调用;direction 枚举三值完整性承接点,§二.3) |
| G2 不可规格化标记 | `scripts/glm_output_validator.py:46`(`NON_SPECIFIABLE_MARKER='不可程序裁决'`) | 推导分流 limitations 声明标记同源(DESIGN L161 原文) |
| E2E-A 任务 schema 最低字段集 `SCHEMA_MIN_FIELDS` | `scripts/research_task_manager.py:36`(10 字段: task_id/created_at/phenomenon/status/indicators/window/detection/evidence/falsifiable_conditions/history) | 映射契约同源(复用导入,禁复制分叉;DESIGN L231 登记型修订承接,§二.3) |
| E2E-A 状态机 `STATUS_FLOW` | `scripts/research_task_manager.py:39`(pending→active→concluded→tracking,实现至 active) | 映射表末行「任务状态推进」语义对齐(提案制,不直接改状态) |
| E2E-A 档案重放规则 `REPLAY_POLICY` | `scripts/research_task_manager.py:40`(幂等跳过/新版本追加/原档不动) | 结论档案重放策略先例(本包同款登记,§二.3) |
| G1 登记清单(对照同源) | `docs/P03_W2_GLM_G1_REPORT.md:24`(§0.2 k=4) | G1 交付文件对照面(本包零改动其 4 文件) |
| G1 输入契约 `validate_input` | `scripts/glm_input_assembler.py:293` | 集成入口输入合法性核验(经 G2 管线已复用;本包集成测试经 G2 `run_conclusion_pipeline` 侧承接,不重复调用) |

### 1.2 现行门禁机制(DESIGN §五(2) 引用面;与现行门禁同构=复用常量/机制引用)

| 机制 | 落点(file:line) | 用途 |
|---|---|---|
| 评级变更最少新增证据 `MIN_EVIDENCE_FOR_RATING_CHANGE=2` | `scripts/allocation_engine.py:139` | 论点终态/观点评级门禁阈值(复用调用 `ae.MIN_EVIDENCE_FOR_RATING_CHANGE`;与现行门禁同构断言的对象) |
| 观点评级门禁实现(触发器或≥2) | `scripts/allocation_engine.py:1262-1269`(fired 同向触发器 或 `new_support>=min_ev`;suspend/resume 放宽 `min_ev=1`) | 门禁判定语义同构基准(适配层按同构语义实现,方向语义复用 `ae._change_direction`) |
| 被拒提案留档 `_record_proposal` | `scripts/allocation_engine.py:1170`(同向 21 天去重/`proposals` 留档) | 提案被拒留档复用调用(DESIGN L175「沿 `_record_proposal` 模式」→ 直接调用非复制) |
| 观点评级枚举 `ALLOWED_RATINGS` | `scripts/allocation_engine.py:63` | view_rating 提案变更值域校验(复用引用) |
| 论点终态门禁(触发器或≥2 新增独立支持证据) | `scripts/report_generator.py:1137-1168`(invalidation/upgrade 触发器 fired 或 `len(new_support)>=2`,否则 `ae._record_proposal` 留档) | 论点终态判定语义同构基准;终态方向映射={'已失效':'invalidation','已验证':'upgrade'}(L1139) |
| 论点确信度门禁(上调不得超过程序星级) | `scripts/report_generator.py:1177-1188`(`conf > star_max` → 拒+留档) | thesis_confidence 提案判定同构基准 |
| 数值校验 FAIL 阻断回写 `apply_status_updates` | `scripts/report_generator.py:1310-1324`(FAIL→两类回写均跳过) | 数值校验前置的阻断语义(B9;适配层 blocked 路径同构) |
| Gate 合成 `combine_gates` | `scripts/research_provenance.py:1533`(任一 FAIL→FAIL;无 FAIL 有 DEGRADED→DEGRADED;全 PASS→PASS) | 数值校验前置第二层 Gate 合成(B4;复用调用) |
| Gate B 数值校验链 B1-B4 定义 | `docs/P03_W2_GLM_INVENTORY.md:54-57`(B1 validate_report/B2 classify_result/B3 validate_generated_report/B4 combine_gates) | 链语义登记: B1-B3=md 报告+锚点面,结构化 HypothesisSet 的等价数值核验=G2 validate_output(DESIGN L18/L99/L247 数值接地,零容差);适配层=B2 结构化等价(G2 校验)×B4 合成(rp 复用),B1/B3 md 面不适用(判定依据登记) |
| 预测五态 `PRED_STATUSES` | `scripts/allocation_engine.py:73`(not_yet_triggered/observing/hit/miss/inconclusive) | 预测候选初始态与终态语义(候选=not_yet_triggered 起;终态不可重开=既有引擎语义,候选构造不触碰) |
| 预测规格先例 pred_* 字段族 | `scripts/report_generator.py:525-526`(pred_metric/pred_op/pred_target/pred_mode;expiry 默认/touch) | 预测候选 spec 字段名对齐(DESIGN L158/L186;复用语义非复制实现) |
| 触发器评估行结构 | `scripts/allocation_engine.py:276`(`{trig_id, direction, status, detail, consec, sustain}`,status∈triggered/not_triggered/unverifiable/sustaining) | 提案判定 trigger_rows 注入面契约(测试合成注入) |
| G2 预留承接登记 | `docs/P03_W2_GLM_G2_REPORT.md:137`(§二.3「来源(iii) 生产由 G3/G4 编排层传结构化触发值」)+`:142`(「neutral 登记不发(枚举完整性留 G3)」) | 本包承接: ①`extract_prior_trigger_targets` 结构化触发器→数值集(喂 G2 注入面);②投影层 direction 三值枚举完整校验(support/counter/neutral,§二.3) |

### 1.3 设计依据实读(`docs/P03_W2_GLM_DESIGN.md`,基线工作树=blob c72d41a1 与 0c8de3c3 侧等值,步骤4 已核)

- §五(1) 推导规则四步: `:154-161`(步1 主张变量化 L156;步2 阈值三来源 L157;步3 条件规格化 L158;步4 区分性检查 L159;不可规格化→limitations 声明 L161);
- §五(2) Gate B 状态保护: `:163-169`(总原则永不直接写状态 L165;论点终态门禁 L166;观点评级门禁 L167;预测候选 L168;数值校验前置 L169);
- §五(3) append-only 衔接: `:171-175`(结论记录字段 L173;同 task_id 重放二选一登记 L174;被拒提案留档 L175);
- §五(4) E2E-A 字段映射表: `:177-190`(9 行映射,task_id L181/echo L182/history L183/evidence L184/条件并入 L185/spec→预测候选 L186/confidence·limitations L187/hypothesis_id→conclusions L188/状态推进提案 L189;实数=9 行——`created_at` 无本层映射行,由任务档自身权威,§二.3 契约承接登记);
- §六 ID 族与交叉引用: `:205-208`(HY-/RT-/QB- 同日序列独立计数 L207;结论记录必携 task_id 或 origin_query_id 之一 L207;共享可信事实同源 L208);
- §一 边界与 §八 红线: `:17-23` / `:244-250`(GLM 产出非事实源 L18/L247;禁交易/仓位/收益承诺 L19/L246;禁直读原始档 L73/L248);
- INVENTORY GG-04/GG-05(WP-G3 承接缺口): `docs/P03_W2_GLM_INVENTORY.md:129-130`;
- E2E-A 注入基线(INVENTORY §二 2.1 抄录): `docs/P03_W2_GLM_INVENTORY.md:96-104`(**注入摘要,非工作树实读**——DESIGN L231 依赖行所指「注入基线」的仓库内抄录件;E2E-A 已落地,以 §一.1 工作树实读为权威,注入抄录件作对照)。

---

## §二 实现参数登记(登记制纪律: 先登记后运行,运行后禁回改)

### 2.1 契约常量(DESIGN 明示值/G2/E2E-A 登记值沿用)

| 参数 | 登记值 | 依据 |
|---|---|---|
| `DERIVATION_STEPS` | `('variableize', 'threshold', 'specification', 'distinctiveness')` | DESIGN L154-159 四步(步4 承接形态见 §二.3) |
| `THRESHOLD_SOURCES` | `('evidence_pack', 'registry', 'prior_triggers')` | DESIGN L157 三来源((i)证据包/(ii)注册表/(iii)先验触发器) |
| `SPEC_KEYS` | `(metric, op, target, mode, window)` | DESIGN L111/L158(G2 SPEC_FIELDS 同集,复用引用) |
| `SPEC_OPS`/`SPEC_MODES` | 复用 `gov.SPEC_OPS`/`gov.SPEC_MODES` | G2 登记(glm_output_validator.py:42-43;与现行预测规格对齐) |
| `NON_SPECIFIABLE_MARKER` | 复用 `gov.NON_SPECIFIABLE_MARKER`(='不可程序裁决') | DESIGN L161 原文(G2 同源) |
| `PROPOSAL_KINDS` | `(thesis_status, thesis_confidence, view_rating, view_confidence, prediction_candidate)` | DESIGN L165-168 三态(论点/观点/预测)+确信度门禁面(L166/L167 各含确信度条款) |
| `THESIS_TERMINAL_STATES` | `('已失效', '已验证')` | report_generator.py:1137 终态语义(DESIGN L166「进入已验证/已失效」) |
| `THESIS_TRIGGER_DIRECTIONS` | `{'已失效': 'invalidation', '已验证': 'upgrade'}` | report_generator.py:1139(want_dir 映射) |
| `RATING_CHANGE_MIN_EVIDENCE` | 复用 `ae.MIN_EVIDENCE_FOR_RATING_CHANGE`(=2) | allocation_engine.py:139(DESIGN L167 明示) |
| `PROPOSAL_DEDUP_DAYS` | 复用 `ae.PROPOSAL_DEDUP_DAYS`(=21) | allocation_engine.py:142(_record_proposal 语义) |
| `PRED_INITIAL_STATUS` | `'not_yet_triggered'` | allocation_engine.py:73 五态之首(候选构造不触碰终态) |
| `PRED_CANDIDATE_SPEC_KEYS` | `(pred_metric, pred_op, pred_target, pred_mode)` | report_generator.py:525-526 pred_* 字段名对齐(DESIGN L158/L186) |
| `CONCLUSION_ID_PREFIX`/`DIRECTIONS` | `'CR-'` / 复用 `gov.DIRECTIONS`(support/counter/neutral) | §六 L207 ID 族扩展(结论记录标识,登记型);L139 方向枚举三值完整承接(G2 留 G3,§一.2) |
| `E2EA_MAP_ROWS` | `9` | DESIGN §五(4) 表 L181-189 行数(实数=9;`created_at` 无映射行,任务侧自身权威) |

### 2.2 实现登记值(DESIGN 未定值,本包登记)

| 参数 | 登记值 | 登记理由 |
|---|---|---|
| `DEFAULT_DERIVE_OP` | `'>='` | 推导参数非猜测: 反驳方向判定属 NLP 面(留编排层/GLM),推导器 op 由参数给定,缺省取枚举首元(与现行预测规格枚举族对齐,gov.SPEC_OPS) |
| `DEFAULT_DERIVE_MODE` | `'expiry'` | report_generator.py:526「expiry(截止日达到,默认)」同缺省(DESIGN L158「窗口默认与 task_ref.window 一致」) |
| `THRESHOLD_SOURCE_PRECEDENCE` | `('evidence_pack', 'registry', 'prior_triggers')` | DESIGN L157 来源列举序;auto 模式下每 metric 按此优先序取第一个非空来源 |
| `_DERIVED_WINDOW_ORDER` | `('week', 'mtd', 'ytd')` | 来源(i) per-metric 派生窗口取值固定序(fact_engine 窗口族 DESIGN L67/L146 语义;确定性需要) |
| `CONDITIONS_PER_METRIC` | `1` | 每 metric 默认产 1 条条件(最小必要;多阈值场景调用方显式传 threshold_source) |
| `CONCLUSION_FINGERPRINT_KEYS` | `(conclusion_id, output_digest)` | 档案重放指纹(E2E-A `_fingerprint_params` 同构;幂等判定用) |
| `ARCHIVE_REPLAY_POLICY` | `'idempotent-skip on identical fingerprint; new record appended on different fingerprint; existing records never rewritten'` | DESIGN L174 二选一登记: 取**幂等跳过**(沿 E2E-A rtm.REPLAY_POLICY 先例,rtm.py:40);指纹不一致→新记录追加(不覆盖) |
| `GATE_B_BLOCKED_CLASSIFICATION` | `'FAIL'` | 数值校验前置失败→阻断提案(apply_status_updates FAIL 语义同构,report_generator.py:1316-1318) |
| `OUTPUT_DIGEST_LEN` | `16` | 输出全文摘要 digest(sha256 前 16 位;G1 REF_DIGEST_LEN/R5 digest_snapshot 同风格) |
| `E2EA_CONCLUSIONS_KEY` | `'conclusions'` | DESIGN L188「实现包可增设 conclusions 子结构承接(登记型扩展)」落点键名 |
| `PRIOR_TRIGGER_KEYS` | `(trig_id, metric, op, target)` | 结构化触发器注入面字段集(G2 预留「G3/G4 编排层传结构化触发值」的最小契约;阈值来源(iii) 提取=取 target 数值) |

### 2.3 登记型行为决策(实现路径抉择,运行后禁回改)

| 决策点 | 登记决策 | 依据/理由 |
|---|---|---|
| 推导器形态 | `derive_falsifiable_conditions(hypothesis, inp, *, op, mode, threshold_source, registry_metrics, prior_triggers, task_window)` 纯函数: 步1 statement 变量化(在场 metric_id 子串扫描,保 facts 序)→步2 阈值(per-metric 三来源,`legal_thresholds_for` 逐源带标记)→步3 规格化(cond_text+spec 五键,window 缺省=task_ref.window)→步4 登记于 trace 并由 G2 校验器承接(集成断言)。**方向(op)不猜**: NLP 面留编排层,推导器参数化 | DESIGN L154-159 规则为约束性规则(禁编造阈值/禁引入 absent 外指标),非猜测引擎;步4 G2 已落四元组判据(glm_output_validator.py:482-493),G3 禁复制分叉→集成闭环断言 |
| 可规格化/不可规格化分流 | 步1 分流: statement 中**在场** metric→推导 spec 条件;**缺席**(absent_registry)metric 主张→non_specifiable(转 limitations 声明义务);**既不在场亦非登记缺席**的注册表指标出现在 statement→登记 derivation_notes(不产条件不引入);`apply_derived_conditions(hypothesis, derivation)` 把分流落回假设(条件合入+non_specifiable 逐条转 limitations 声明条目,含不可程序裁决标记) | DESIGN L156「不在场指标→该条件不可推导,转 limitations 声明;不得引入 absent_registry 之外的指标」+L161 |
| 无合法阈值的在场 metric | 该 metric 主张计 non_specifiable(在场但三来源无可取阈值→不可规格化,如实分流,不编造) | DESIGN L157「三个来源之外的数值=编造,校验器拒绝」的推导侧镜像 |
| prior_triggers 结构化注入面 | `extract_prior_trigger_targets(prior_triggers)`→数值集,喂 G2 `legal_target_numbers(prior_trigger_targets=…)`;本包测试注入合成触发器列表;生产读取 thesis.json/allocation_views.json 触发器结构属 WP-G4 编排(本包零 config 读取) | G2 REPORT §二.3 预留(G2 委托 G3/G4 传结构化触发值);G1 §二.3「装配器不读 config」同纪律 |
| 门禁提案数值校验前置 | `build_gate_b_proposal` 前置双层: ①`gov.validate_output`(G2 结构化数值接地,零容差)=B1-B3 的结构化等价(B1-B3=md 报告+锚点面,对象为 md 文件,结构化 HypothesisSet 无 md 载体——判定依据);②`rp.combine_gates(gate_a, gate_b)`(B4 复用调用,gate_b=①有问题→'FAIL',无问题→按 gate_a 合成)。FAIL→`blocked` 提案(不进门禁判定,不产状态变更) | DESIGN L169「先过 Gate B 数值校验链(B1-B4)…FAIL→阻断回写」+L18/L247 数值接地=结构化面 |
| 门禁判定与现行同构 | `evaluate_gate_b`: thesis_status 终态→invalidation/upgrade 触发器 fired 或 `new_support>=ae.MIN_EVIDENCE_FOR_RATING_CHANGE`;thesis_confidence→上调须 `conf<=star_max`;view_rating→同向触发器 fired 或新增证据足额(suspend/resume 放宽 1,方向复用 `ae._change_direction`);view_confidence→同 thesis_confidence;prediction_candidate→spec 完整性校验(metric 在场/target∈三来源/op·mode 枚举),初始 not_yet_triggered,不裁决不触碰终态。判定常量全部复用 `ae.*` 引用(禁复制字面量) | DESIGN L165-168;同构断言=测试断言本模块引用与 `ae.MIN_EVIDENCE_FOR_RATING_CHANGE` 同一对象+行为等价(≥2 门槛/触发器放行/suspend-resume 放宽,report_generator.py:1137-1168 与 allocation_engine.py:1262-1269 语义) |
| 提案被拒留档 | `record_rejected_proposal` 复用调用 `ae._record_proposal(target_state, to, reason, evidence_summary, today_iso)`(同向 21 天去重/proposals 留档,与现行周报链同一函数) | DESIGN L175「沿 `_record_proposal` 模式」→ 直接复用调用(report_generator.py:1080/1163 先例: 论点侧同样调用 ae._record_proposal) |
| 结论记录构造 | `build_conclusion_record(inp, result, *, gate_b_results, today_iso)`: 字段={conclusion_id(CR-YYYYMMDD-NNN,同日序列), hypothesis_ids[], task_id/origin_query_id(必携其一,模式 A/B 分取), snapshot_id+snapshot_digest(自输入绑定透传), outcome(ACCEPTED/ACCEPTED_DOWNGRADED/ABSENT_REGISTERED,G2 三结局透传), output_digest(输出全文摘要 sha256 前 16), gate_b_verdicts[](逐提案裁决结果), falsifiable_spec_count, created_at};**含被拒提案的轮次同样落档**(门禁裁决结果= rejected 登记) | DESIGN L173 记录字段逐项(hypothesis_id/task_id/query_id/快照绑定/输出全文摘要/门禁裁决结果)+L207(必携其一)+L175(被拒提案不删除) |
| append-only 档案 | 纯注入面: `append_conclusion_record(record, archive)`(archive={'conclusions': [], …} dict 或注入路径经调用方持久化——本包零文件写入,测试合成档案);幂等: 指纹(CONCLUSION_FINGERPRINT_KEYS)一致→`skipped-idempotent`;不一致→**新记录追加**(conclusion_id 同但内容异→新版本序号 N+1,不改写);改写面 `mutate_conclusion_record` 显式 `raise ArchiveImmutable`(append-only 写入后不可改不可删) | DESIGN L173「写入后不可改不可删」+L174 二选一登记(§二.2 ARCHIVE_REPLAY_POLICY)+E2E-A rtm.save_task 同构(rtm.py:135-156) |
| 交叉引用字段校验 | 每条记录必携 `task_id` 或 `origin_query_id` 之一(两者皆缺→`InvalidConclusionRecord` 拒);hypothesis_ids 逐项过 `HY-YYYYMMDD-NNN` 正则;CR- 同日序列;task_id 形态 `RT-*`/origin_query_id 形态 `QB-*`(前缀族登记,不硬校验 E2E-A 哈希后缀形态——RT- 实现含 `RT-{start}~{end}-…` 形态,rtm.py:53,前缀校验容之) | DESIGN L207「结论记录必携 task_id 或 origin_query_id 之一(锚定产生语境)」+§六 ID 族 |
| E2E-A 映射契约 | `E2EA_FIELD_MAP` 静态登记 DESIGN §五(4) 9 行(本层字段→任务字段→映射语义三元组);`build_e2ea_projection(inp, validated_output, *, evidence_map, proposals, gate_results)` 产出投影: task_id 透传/task_ref 其余字段 echo 不回写/history_append_lines(statement+confidence+limitations 属性)/evidence_refs(方向化挂载: fact_id/snapshot_id/quality_status,自 G2 映射表透传)/falsifiable_conditions_merge(可规格化子集)/prediction_candidates(spec→pred_* 候选)/conclusions 子结构/status_proposal(提案制)。契约测试: `rtm.SCHEMA_MIN_FIELDS` 10 字段中 9 个有映射行承接+`created_at` 由任务侧自身权威(登记断言);E2EA_FIELD_MAP 行数=9=DESIGN 表行数 | DESIGN L177-190 映射表逐行+L231 依赖行「以契约测试固化映射表」;E2E-A 已落地→登记型承接: 实读 SCHEMA_MIN_FIELDS(rtm.py:36)与 DESIGN 表相容(created_at/status 由任务档自身权威,映射表 L189 状态推进=提案) |
| neutral 枚举完整性承接(G2 留 G3) | 投影层 evidence_refs.direction 值域=`gov.DIRECTIONS` 三值完整校验(support/counter/neutral;unknown→拒);G2 映射表只发 support/counter,neutral 分支在投影层合法在场(如编排层补充的中性观测) | G2 REPORT §二.3「neutral 登记不发(输出无中性向证据字段,枚举完整性留 G3)」+DESIGN L139 枚举定义 |
| 预测候选落 allocation_views 侧 | 本包只构造候选(PRED_CANDIDATE_SPEC_KEYS 对齐 pred_* 字段名+window+source_hypothesis_id),**零写 allocation_views.json**(落档沿既有回写链/编排层 WP-G4;「沿既有门禁」=候选裁决与生命周期由既有引擎 B8 承担) | DESIGN L230「预测候选落 allocation_views 侧沿既有门禁」+L186;AC-05.5 主流水线/registry 零改动 |
| echo 纪律 | `echo_params()` 返回 §二.1/§二.2 全部登记参数;测试断言 echo=常量=本登记表(R011 三方一致) | R011 纪律沿用(G1/G2 §二.3 同款) |

---

## §三 逐要点证据映射表(合同 AC-02;要点→实现落点→证据指针→自检结论)

实现件: `scripts/glm_conclusion_integrator.py`(703 行,17 函数+2 异常+2 常量区);测试件: `tests/test_p03_w2_glm_g3.py`(857 行,**61 用例**=T0 fixture 自检 2+T1 推导规则 16+T2 门禁提案 19+T3 结论档案 10+T4 E2E-A 映射契约 12+T5 echo 1+T6 源码边界锁 1)。专项套件实测 `python3 -m unittest tests.test_p03_w2_glm_g3` = **61 用例全绿**(2026-11-05,见 07-negative-sensitivity/D*-restore-green.log 与 09-local-ci/)。

### 要点① 推导规则四步用例(可规格化/不可规格化分流)——工件: 测试文件 ✓

- **实现落点**: §五(1) 四步=glm_conclusion_integrator.py:167-346(`variableize_claim`:169 / `legal_thresholds_for`:201 / `derive_falsifiable_conditions`:248 含步4 trace:315-318 / `apply_derived_conditions`:329 分流落回);先验触发器注入面 `extract_prior_trigger_targets`:153(G2 预留承接)。
- **证据指针**: T1_DerivationRules 16 用例(tests/test_p03_w2_glm_g3.py:199-361)——步1 三分类(:205 在场/缺席/注册未入输入)、步2 三来源逐源(:212 证据包 per-metric 保序[值→派生 week/mtd/ytd×_DERIVED_VALUE_KEYS 字段族]/:220 注册表 range 端点+max_week_pct_move/:226 先验触发器 target)、步3 规格化(:236 spec 五键+窗口缺省=task 窗/:248 op·mode 枚举外拒)、步4 区分性由 G2 承接的 trace 登记(:256);分流=不可规格化两流(:263 缺席指标流/:273 在场无合法阈值流)+不编造断言(:282)+注册未入输入只登记不引入(:304);落回=四元组去重合入(:313)+non_spec→limitations(:329);**集成闭环**(:340 推导+落回后的整体输出过 G2 `validate_output` 零问题);注入面(:353)。
- **自检结论**: 四步各有对应用例;可规格化(spec 条件)/不可规格化(non_specifiable→limitations)双流闭合;步4 未复制分叉(trace 登记 deferred+集成断言托底)。**PASS**。

### 要点② 门禁提案测试(无触发器且新增证据不足→提案被拒+留档;与现行门禁同构断言)——工件: 测试文件+allocation_engine 机制引用 ✓

- **实现落点**: §五(2)=glm_conclusion_integrator.py:348-493(`build_gate_b_proposal`:350 数值校验前置双层[①`gov.validate_output` 零容差 ②`rp.combine_gates` B4]→FAIL blocked / `evaluate_gate_b`:391 五类提案同构门禁 / `record_rejected_proposal`:482 复用调用 `ae._record_proposal`)。
- **证据指针**: T2_GateBProposals 19 用例(tests/test_p03_w2_glm_g3.py:363-529)——核心验收句=**无触发器且新增证据不足→被拒+留档**(:408 拒+理由含「终态判定」「≥2」+:415 留档复用 `ae._record_proposal` 实调用,`proposals[0].to='已失效'`);同构断言=常量复用身份(:489 `gci.RATING_CHANGE_MIN_EVIDENCE==ae.MIN_EVIDENCE_FOR_RATING_CHANGE==2`+源码边界锁 T6 强制 `ae.MIN_EVIDENCE_FOR_RATING_CHANGE` 复用标记在场)+行为等价(:425 ≥2 放行/:431 触发器放行/:473 suspend-resume 放宽 1+`ae._change_direction` 方向语义);数值校验前置(:378 接地 FAIL→blocked 不进门禁/:394 DEGRADED 合成不阻断);确信度星级门禁(:444/:450/:454 star 缺失 fail-closed);预测候选 spec 完整性(:510 缺 pred_target 拒/:518 完整受纳初始 not_yet_triggered);留档去重语义(:499 同向重提 repeat 累计单条目——**断言时序修正登记**: `ae._record_proposal` 返回留档条目本体,去重命中原地累加 repeat,故 repeat=1 断言置于第二次调用前,首测版序错误属测试自身缺陷,非容忍度放宽);kind 枚举校验(:527)。
- **自检结论**: 验收句正反两侧(不足拒+足额/触发器放行)齐备;同构=复用调用非复制(T6 源码锁+D1 负向注入实证: 常量改字面量→T6 红)。**PASS**。

### 要点③ append-only 测试(结论记录改写被拒+交叉引用字段校验)——工件: 测试文件 ✓

- **实现落点**: §五(3)=glm_conclusion_integrator.py:495-601(`build_conclusion_record`:502 交叉引用必携其一:514+ID 格式族校验:518-529+outcome∈G2 三结局:530 / `validate_conclusion_record`:555 / `append_conclusion_record`:567 幂等跳过:576-579+新版本追加:580-592 / `mutate_conclusion_record`:595 恒 `raise ArchiveImmutable`)。
- **证据指针**: T3_ConclusionArchive 10 用例(tests/test_p03_w2_glm_g3.py:531-659)——集成前置(:549 fixture 过 G2 真实管线=ACCEPTED_DOWNGRADED);改写被拒(:587 `mutate_conclusion_record` raise ArchiveImmutable);交叉引用(:595 两者皆缺拒/:604 RT-/QB- 前缀族反例/:619 HY- 格式/:628 CR- 格式);append 语义(:554 written/:561 幂等跳过/:569 同 id 异指纹→`__v2` 追加且原记录逐键不动);记录字段与绑定(:636 snapshot_id/digest 透传+gate_b_verdicts 登记+outcome 透传)。
- **自检结论**: 改写被拒+交叉引用校验+幂等/新版本三态齐备;D2 负向注入实证(原地改写→T3 红)、D4 实证(必携校验移除→T3 红)。**PASS**。

### 要点④ E2E-A 字段映射契约测试——工件: 测试文件+注入摘要引用 ✓

- **实现落点**: §五(4)=glm_conclusion_integrator.py:603-703(`E2EA_FIELD_MAP` 9 行静态登记+`build_e2ea_projection`:605)。
- **证据指针**: T4_E2EAFieldMapContract 12 用例(tests/test_p03_w2_glm_g3.py:661-787)——契约同源(:664 `rtm.SCHEMA_MIN_FIELDS` 实读字面量比对/:670 E2EA_FIELD_MAP 9 行=DESIGN §五(4) 表逐行三元组);投影逐承接面(:687 task_id 透传/:690 echo 只读回显/:699 history 追加行/:707 evidence 方向化挂载/:719 **direction 三值枚举完整校验**(G2 留 G3 承接: support/counter/neutral 皆合法,非枚举拒)/:735 可规格化子集并入/:744 pred_* 预测候选/:759 状态推进=提案制/:767 模式 B 裁剪);**最低字段集覆盖断言**(:777 `rtm.SCHEMA_MIN_FIELDS` 10 字段中 9 个有映射行承接+`created_at` 任务侧自身权威——DESIGN L231「以契约测试固化映射表」落点)。注入摘要引用=REPORT §一.3 末行(INVENTORY §二 2.1 抄录件,标注「注入摘要,非工作树实读」,与工作树实读对照登记)。
- **自检结论**: 9 行映射+三值枚举+模式 B 裁剪+提案制全覆盖;E2E-A 已落地→按 DESIGN L231 登记型修订承接路径以工作树实读 schema 为契约权威。**PASS**。

### 要点⑤ CI 零回归——工件: run ID(操作者 CHECKPOINT dispatch,本步登记本地全量预演) ✓

- **实现落点/证据指针**: 本地全量预演=09-local-ci/(60 文件=59 套件实跑+1 合同排除 test_glm_live;逐套件退出码清单);预期 58 绿+1 既有红(test_p4_fixes,基线归因)。远端 run ID 由操作者于 CHECKPOINT 按登记文件 `rounds/028/GLM-WP-G3-CI-dispatch-evidence.md` dispatch 后回填,**执行 Agent 不自 dispatch**(合同 AC-06 纪律)。
- **自检结论**: 本地预演零回归(既有红=基线归因非本包引入,git 取证 §四);远端 run ID=PENDING 操作者动作。**本地 PASS/远端待操作者**。

### 负向敏感性(R022;DESIGN 验收要点外延,合同 §3 实现纪律)

四注入全红→还原→绿,还原后模块 sha256 逐字节一致(基线 `c3a613…ed79`),证据=07-negative-sensitivity/(README+8 log): D1 常量复制分叉→T6 红;D2 append 原地改写→T3 红;D3 编造阈值→T1 红×2;D4 交叉引用校验移除→T3 红。**PASS**。

---

## §四 git 取证与自检(装配时刻回填;最终尖端以 zip 外 sidecar 为准——自指豁免,G1/G2 同款)

- **分支/线性**: `dev/p03-w2-glm-g3` 自基线 2f03be1fd77677b43d3afb7946af07c725625a2a 纯线性切出;`git log --merges 基线..尖端`=空输出(零 merge 提交);reflog 干净(成员③ reflog.txt)。装配时刻 git 尖端=**本提交**(sha 实取见证据包 03-git-forensics/rev-parse-HEAD.txt;本提交之前的推送实取=ls-remote-POST-push.txt[实现提交 a1f0cfbd8686fc2a5e5107726ea468ad3325d76b 已在 origin]);装配之后的终态(DELIVERY 追加行提交与最终 ls-remote)以 zip 外 `08-sidecar/final-state.txt` 为准——固定点(证据包)不可内含其后提交的哈希,自指豁免同 G1/G2 先例。
- **diff 范围**: `git diff --name-status 基线..尖端` = 恰 4 行 A(docs/P03_W2_GLM_G3_DELIVERY.md / docs/P03_W2_GLM_G3_REPORT.md / scripts/glm_conclusion_integrator.py / tests/test_p03_w2_glm_g3.py),零 M/D,零第二类(成员③ diff-name-status 文件;与 §0.2 白名单 k=4 逐行一致)。
- **设计在场**: `git merge-base --is-ancestor dev/p03-w2-glm-design HEAD` exit=0(设计支可达);设计六件 blob 等值核验=设计支 vs 基线 HEAD 全等(GLM 族: P03_W2_GLM_DESIGN.md=c72d41a12eee3c24610bbf3b7078759d7c1895d2 / P03_W2_GLM_INVENTORY.md=5cb643a1aea4ca39f5c8ee32f6a2240b89c0168d / P03_W2_GLM_DELIVERY.md=772ad4cd20ac64db28923c38e30a26b1537f0578;E2EB 族: P03_E2EB_DESIGN.md=89de7de9…/P03_E2EB_DELIVERY.md=5e0eb558…/P03_E2EB_QUERY_SURFACE_INVENTORY.md=9306e68b…;成员③ 06a/06b 文件原样输出)。
- **远端实取**: 实现提交推送后 `git ls-remote origin`=31 支(30[G2 终态=冻结 29+dev/p03-w2-glm-g2]+唯一新增 `dev/p03-w2-glm-g3`→a1f0cfbd8686fc2a5e5107726ea468ad3325d76b);既有 30 支尖端零变动(含 dev/p03-w2-glm-g2=2f03be1 基线不动)。最终 ls-remote(追加行提交后)见 sidecar。
- **LIVE/隔离**: LIVE 路径 grep(`R028|GLM-WP-G3|IA-P03-W2-GLM-WP-G3`)=0 命中;launchd 零触碰;`data/` 27 文件与 G2 基线快照逐字节一致(diff IDENTICAL);.gitignore 零改动(diff 白名单外零文件);证据档案(zip)不 commit(仅存 /tmp)。成员③ LIVE-isolation-checks.txt。
- **白名单外零改动自检**: 工作树 `git status` 全程仅白名单 4 文件出现(实现提交前 untracked 恰 3+DELIVERY 落笔后恰 4,提交后 clean);E2E-A 六文件/G1 四文件/G2 四文件/主流水线 scripts/registry/workflows 均在 diff 零改动面内(4 行 A 之外无任何路径)。

---

## §五 提交前数值标注六项自检清单(合同 §5.3;双文档=本件+DELIVERY 全文扫描)

边界声明(第5项): 本文日期时刻=UTC(另注明除外);SHA 一律全值或合同冻结值;行号/结构编号(L228-232 等)=基线 2f03be1 工作树实读;档键成分(RT-/QB-/HY-/CR- 前缀)=标识符非数据值。

| # | 数值 | 标注 |
|---|---|---|
| 1 | 交付文件 k=4 | [实取·来源: REPORT §0.2 清单=git ls-files(269 文件)对照零重合,4 路径均为本包新增] |
| 2 | git ls-files 基线计数 269 | [实取·来源: `git ls-files \| wc -l` 实测(265[G2 开工值]+4[G2 交付]=269,与 G2 交付后谱系一致)] |
| 3 | 专项测试 61 用例(2+16+19+10+12+1+1) | [实取·来源: 本地运行 "Ran 61 tests ... OK"(09-local-ci/test_p03_w2_glm_g3.log+07-negative-sensitivity/D*-restore-green.log)+§三 类别计数复算] |
| 4 | 负向敏感性 D1红1/D2红1/D3红2/D4红1/每次还原后 61 绿 | [实取·来源: 07-negative-sensitivity/ 四注入红 log+四还原绿 log;还原后模块 sha256=基线 c3a61348…ed79 逐字节一致] |
| 5 | 本地全量 60 文件=59 跑+1 合同排除(test_glm_live)=58 绿+1 既有红(test_p4_fixes「39通过/4失败」) | [实取·来源: 09-local-ci/per-suite-results.txt(total files=60 green=58 red=1 excluded=1)+test_p4_fixes.log 尾部;既有红=G1/G2 同款基线归因,零导入关系] |
| 6 | CI 预期 58 基线套件+本包新增 1=59;run ID | [登记·来源: 合同冻结口径(58+1=59);run ID=PENDING 操作者 CHECKPOINT dispatch(rounds/028/GLM-WP-G3-CI-dispatch-evidence.md)] |
| 7 | data 27 文件(24 daily+3 research) | [实取·来源: 05-zero-touch/datapath-zero-touch-snapshot.txt 计数;与 G2 证据包基线快照 diff 逐字节一致] |
| 8 | §二 登记参数(E2EA_MAP_ROWS=9/RATING_CHANGE_MIN_EVIDENCE=2[ae 复用]/PROPOSAL_DEDUP_DAYS=21[ae 复用]/CONDITIONS_PER_METRIC=1/OUTPUT_DIGEST_LEN=16/DEFAULT_DERIVE_OP='>='/DEFAULT_DERIVE_MODE='expiry' 等) | [登记值·本包登记(§二);echo=常量=登记三方一致(T5 实测)] |
| 9 | 锚点值 2.93/4186.7/2.20/0.73/73.0/4161.7/3.7/3.5/4300.0/1000/30000/25 | [合成 fixture 字面量·非实取](E2E-A 登记窗终值语义的合成复用;注册表/触发器注入值全合成,不代表真实配置) |
| 10 | 基线 2f03be1fd77677b43d3afb7946af07c725625a2a/设计支 0c8de3c3bece78dd2d9f0d8928a817b597e3104e/六件 blob 哈希 6 枚(GLM 族 3+E2EB 族 3,设计支与基线全等值) | [实取·来源: ls-remote/merge-base/ls-tree 实测(§四+证据包成员③)] |
| 11 | DESIGN 引用行号(L154-161/L163-175/L177-190/L205-208/L228-232 等) | [实取·来源: 基线工作树 docs/P03_W2_GLM_DESIGN.md 实读(blob c72d41a1,与 0c8de3c3 侧等值)] |
| 12 | 既有模块引用行号(gov:42-58/186/234/521/582;gia:293;ae:73/139/142/1170-1184/1262-1269;rg:525-526/1137-1188/1310-1324;rp:1533;rtm:36-40) | [实取·来源: 基线工作树实读 §一.1/§一.2/§一.3 登记] |
| 13 | 开工时刻 2026-11-04T18:10:41Z(会话首录) | [实取·来源: 会话记录首条时间戳;本表落笔 2026-11-04T18:39:42Z(date -u 实测)] |

第3项复核: 逐个 [实取] 项已回工作树/命令输出复核一遍(2026-11-04T18:39Z);未发现失实项;第6项为合同冻结口径+PENDING run ID,已显式标注。本清单自身成件入证据包(成员①附带)。
