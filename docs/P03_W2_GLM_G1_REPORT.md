# IA-P03-W2-GLM-WP-G1 执行报告(结论层输入装配器)

> 工作包: IA-P03-W2-GLM-WP-G1(G 族首包: WP-G1 结论层输入装配器)
> 分支: `dev/p03-w2-glm-g1`(自基线 `a6d086b8b184067d530815e0bf8963d959275743` 切出 + 指定并入步 merge `0c8de3c3`)
> 冻结合同: IA-P03-W2-GLM-WP-G1-AC-v1.0(2026-11-05 00:5x HKT 冻结;本报告为合同 §零登记制落点)
> 边界声明: 本包**零真实 GLM/LLM 调用、零凭证、零付费、零网络出站**(设计对象≠设计手段;真实调用属 WP-G4,执行前置=用户批准凭证/费用,PENDING 未批)。日期/SHA/结构编号/档键成分按合同边界出圈登记: 本文日期时刻均为 UTC(另注明者除外);SHA 一律全值。

---

## §零 规格抄录与交付面登记(合同 AC-01 落点;开工首步)

### 0.1 WP-G1 行四要素逐字抄录(实读 `docs/P03_W2_GLM_DESIGN.md` §七,并入后工作树实况)

以下为 DESIGN §七 WP-G1 行**逐字抄录**(无增删改字;行号=并入后工作树实读行号,审计对照允许偏差≤3行):

- **L216**: `**WP-G1 结论层输入装配器**`
- **L217**: `- 目标: 落地§三(a) \`GLMResearchInput\` 装配(模式 A/B 双形态)+缺席登记+禁直读机制。`
- **L218**: `- 范围: 新增装配器模块;不改 fact_engine/snapshot_builder/data_assembler 既有签名。`
- **L219**: `- 依赖: 无硬依赖(快照读取面 R1/R3 既有);模式 B 形态依赖 E2E-B WP-B1/B2 的 IR 与执行器产物(未落地前该形态按缺席登记路径处理,不影响模式 A 形态交付)。`
- **L220**: `- 验收要点草案: ①输入契约字段级校验单测(工件: tests/test_p03_g1*.py) ②禁直读负向测试: 断言装配产物零原始档路径引用+Gate A FAIL 拒绝装配(工件: 测试文件) ③缺席登记测试: 构造缺席指标→absent_registry 如实登记非零值(工件: 测试文件) ④快照绑定核验: 篡改快照后装配拒绝(工件: 测试+R5 机制引用) ⑤CI 零回归(工件: GitHub Actions run ID)。`

四要素齐备(目标/范围/依赖/验收要点),无缺失。**冲突自查(合同 §零(iv))**: 要素齐备可推导 ✓;范围不含真实 GLM 调用/网络/新数据源凭证 ✓;依赖列「无硬依赖(快照读取面 R1/R3 既有)」与基线实况一致(research_provenance.py R1/R3 在场)✓,不要求并入他支(指定并入步=0c8de3c3,合同 §零 定值)✓ → 无情形(d)冲突,合法开工。

### 0.2 交付文件清单(登记制白名单,k=4;推导逐条附 DESIGN 依据)

DESIGN L218 范围列为**模块级**(「新增装配器模块」)而非文件级 → 按合同 §零(ii) 固定推导规则生成:

| # | 路径 | 类型 | DESIGN 依据 | 推导规则 |
|---|---|---|---|---|
| 1 | `scripts/glm_input_assembler.py` | 代码(装配器模块) | DESIGN L217「落地§三(a) `GLMResearchInput` 装配」+ L218「范围: 新增装配器模块」 | 每个代码模块 = `scripts/` 下恰 1 文件 |
| 2 | `tests/test_p03_w2_glm_g1.py` | 测试 | DESIGN L220 要点①-④工件「tests/test_p03_g1*.py / 测试文件」 | 含代码则必含本文件(合同固定名) |
| 3 | `docs/P03_W2_GLM_G1_REPORT.md` | 文档(本件) | DESIGN L220 工件面(要点逐条证据映射/参数登记落点);合同必含件 | 必含 REPORT |
| 4 | `docs/P03_W2_GLM_G1_DELIVERY.md` | 文档(交付说明) | DESIGN L254 交付说明惯例(参照 GLM/E2E-B 设计交付件);合同必含件 | 必含 DELIVERY |

**结构约束核验(iii)**:
- 与 `git ls-files` 零重合: 上述 4 路径在基线 a6d086b8 与并入后工作树均**不存在**(纯新增;开工时 `git ls-files` 实测对照,见 §四取证)✓;
- 必含 DELIVERY ✓(#4);含 `.py` 实现(#1)则必含对应 tests(#2)✓。

**命名偏差登记(如实,非冲突)**: DESIGN L220 工件 glob `tests/test_p03_g1*.py` 与合同固定推导规则指定名 `tests/test_p03_w2_glm_g1.py` 不同名(合同名不匹配该 glob)。处置: **以合同固定规则名为准**(冻结合同为白名单权威;DESIGN 工件行为依据,单测试文件承接要点①-④全部工件语义),此处登记偏差,不构成 §零(iv) 冲突类型(要素齐备/可推导/结构约束成立)。固定推导规则下 k 恰为 4,不引入第二测试文件(否则违反「每个代码模块=scripts/ 下恰 1 文件+必含 1 tests」推导闭合,且 CI 套件数预期=56+1=57 将失准)。

### 0.3 运行产物边界登记

WP-G1 验收要点①-④工件=**测试文件**(离线合成 fixture 驱动),要点⑤工件=GitHub Actions run ID(操作者 CHECKPOINT dispatch)。装配器模块**无编排入口/无真实运行要求**(对照 E2E-A `--run-e2e` 先例: E2E-A 合同要点明文要求真实回放,WP-G1 行无此要素)→ 本包登记「**零运行产物**」: `data/research/` 无新增运行档案,`data/daily/` 全程只读零触碰。依据=DESIGN L220 逐要点工件清单(实读,见 §0.1 抄录)。

---

## §一 前置实读登记(数据接入点与机制引用,file:line 为并入后工作树实读)

### 1.1 快照读取面与门禁机制(复用调用,禁复制分叉)

| 机制 | 落点(file:line) | 用途 |
|---|---|---|
| R1 确定性快照版本选择 `select_snapshot` | `scripts/research_provenance.py:1243` | 装配器 R1 壳入口取当日权威快照(只 glob `research_snapshot_*.json` 标准化产物) |
| R2 Gate A 事实重算 `gate_status` | `scripts/research_provenance.py:1101` | 装配前复算 Gate A(声明↔重算一致性;纯历史重验口径不传 data_dir) |
| R3 门禁放行 `gate_allows_formal_research` | `scripts/research_provenance.py:1183` | PASS/DEGRADED 放行,FAIL/None 拒绝装配(复用,不另立放行集) |
| R5 快照内容指纹 `digest_snapshot` | `scripts/research_provenance.py:1297` | snapshot_binding.snapshot_digest 内容级绑定(sha256 前16位,canonical JSON) |
| E2E-A 任务 schema 最低字段集 `SCHEMA_MIN_FIELDS` | `scripts/research_task_manager.py:36` | task_ref 字段契约(复用导入,禁复制分叉) |
| 事实结构基准 `make_fact` 产物字段 | `scripts/fact_engine.py:210-238` | evidence_pack.facts[] 同构投影基准(fact_id=metric_id@观测日) |
| 三重核验模式参照 `verify_research_inputs` | `scripts/report_generator.py:612` | 「meta 声明+内容摘要重算+确定性重建比对」模式沿用(DESIGN §三(a) 机制1 明示) |
| 拒绝语义参照(Gate A FAIL 拒装配) | `scripts/data_assembler.py:323-329` | 沿数据装配器拒绝语义(DESIGN §三(a) 机制3 明示) |
| 通道规范文件身份 `SOURCE_FILE_RULES`/`_SOURCE_TO_INPUT` | `scripts/research_provenance.py:111-159` | classify_absence 判 ABSENT_SOURCE 的通道映射复用 |

### 1.2 设计依据实读

- DESIGN §三(a) 输入契约九字段+禁直读四机制: `docs/P03_W2_GLM_DESIGN.md:56-76`;
- DESIGN §三(b)/(c)、§四、§五、§六、§八: 本包仅 §三(a)+§六(A/B 差异)相关面承接(`docs/P03_W2_GLM_DESIGN.md:78-209`);
- E2E-B IR schema(模式 B query_ref 对接契约): `docs/P03_E2EB_DESIGN.md:55-107`;四级缺席枚举: `docs/P03_E2EB_DESIGN.md:118-129`;
- INVENTORY 面④(S1-S5)与 GG-01(WP-G1 承接缺口): `docs/P03_W2_GLM_INVENTORY.md:67-79` / `:126`。

### 1.3 禁直读机制落地(DESIGN §三(a) 机制1-4 → 实现落点)

1. **装配器唯一写者+读取面封闭**: 装配器数值输入唯一来源=入参 snapshot(经 R1 选择)+注入引用;模块内**零 `open()`、零 glob、零网络**;唯一文件读取经 `rp.select_snapshot`(R1,只碰 `research_snapshot_*.json` 标准化产物,豁免标记 `ACCESS_POINT_EXEMPT` 单处,沿 E2E-A research_history_query 先例);
2. **披露与读取分离**: `evidence_pack.facts[].source_file` 仅作披露字符串从快照事实 `source.file` 逐字透传(规范 basename,不含路径成分),不构成读取通道;
3. **负向测试固化**: 装配产物全字符串扫描零原始档路径引用(除 facts[].source_file 披露槽位)+ Gate A FAIL/None 拒绝装配(T3/T2 用例,见 §三映射表);
4. **数值零旁路**: 装配器零算术——evidence_pack.facts 数值与快照事实逐位相等(投影非计算;T1b 用例断言字面量相等)。

---

## §二 实现参数登记(登记制纪律: 先登记后运行,运行后禁回改)

### 2.1 契约常量(DESIGN 明示值)

| 参数 | 登记值 | 依据 |
|---|---|---|
| `CONTRACT_VERSION` | `'gri-1.0'` | DESIGN L62(标识符示例值,标识符非数据值) |
| `MODE_ENUM` | `('A', 'B')` | DESIGN L63 |
| `ABSENT_LEVELS` | `('ABSENT_REGISTRY', 'ABSENT_SOURCE', 'ABSENT_DATA', 'ABSENT_WINDOW')` | DESIGN L68 / E2E-B DESIGN L118-129 四级枚举 |
| `EVIDENCE_FACT_FIELDS` | `(metric_id, fact_id, value, unit, observation_date, quality_status, derived, source_file)` | DESIGN L67 字段集 + L74 source_file 披露槽位 |
| `TASK_REF_FIELDS` | `(task_id, phenomenon, indicators, window{start,end}, detection, history_tail)` | DESIGN L65(与 E2E-A schema 一一对应) |
| `QUERY_REF_FIELDS` | `(query_id, question_text, as_of, metric_bindings_digest, derived_ops_digest)` | DESIGN L66(引用摘要,非数值载体) |
| `MIN_COMPETING_HYPOTHESES` | `2` | DESIGN L70(合同级设计规则) |
| `COUNTER_EVIDENCE_REQUIRED` | `True` | DESIGN L70 |
| `NUMERIC_GROUNDING_REQUIRED` | `True` | DESIGN L70 |
| `PROMPT_CONTRACT_KEYS` | `(language, output_schema_version, counter_evidence_required, min_competing_hypotheses, numeric_grounding_required)` | DESIGN L70 |

### 2.2 实现登记值(DESIGN 未定值,本包登记)

| 参数 | 登记值 | 登记理由 |
|---|---|---|
| `PROMPT_LANGUAGE_DEFAULT` | `'zh'` | DESIGN L70 language 未定值;系统工作语言(周报/设计文档中文) |
| `OUTPUT_SCHEMA_VERSION_DEFAULT` | `'hs-1.0'` | DESIGN L70 output_schema_version 未定值;HypothesisSet(DESIGN §三(c))初始契约标识符,WP-G2 落地 schema 后沿用或经登记修订 |
| `HISTORY_TAIL_MAX` | `5` | DESIGN L65 history_tail 未定长;取任务 history 最近 5 条(状态迁移尾部足够定位语境) |
| `REF_DIGEST_LEN` | `16` | 与 R5 `digest_snapshot` 同风格(sha256 前 16 位,`research_provenance.py:1297-1301`);query_ref 双 digest 同式 |
| `MISSING_REF_STATUS` | `{'status': 'MISSING', 'reason': '<字段名>未提供(装配期如实登记缺席)'}` | DESIGN L67「scorecard_summary(当日评分卡摘要或 DEGRADED/缺失状态)」——缺失=合法显式状态,非空缺 |
| `GATE_ALLOWED`(放行集) | 不另立常量,**调用复用** `rp.gate_allows_formal_research` | AC-05.5 对齐=复用调用禁复制分叉;此处仅登记语义= ('PASS','DEGRADED') |

### 2.3 登记型行为决策(实现路径抉择,运行后禁回改)

| 决策点 | 登记决策 | 依据/理由 |
|---|---|---|
| 模式 A 缺席分级 | `classify_absence(metric_id, snapshot, required_window=None)` 纯函数四级全实现;模式 A 装配调用时不带 required_window → 产物面仅 REGISTRY/DATA 可达 | task indicators 为指标 ID 无派生窗语义(DESIGN L65);SOURCE/WINDOW 级由纯函数直接用例覆盖(四级枚举完整性) |
| 模式 A ABSENT_SOURCE 可达性 | 当前注册表拓扑下(4 通道均含核心指标,`research_provenance.py:111-117`+registry 实测 32 核心)**Gate 放行态内 ABSENT_SOURCE 不可达**: 任一通道 MISSING/READ_FAIL → 该通道核心缺失 → Gate A FAIL → 拒绝装配(上游正确行为)。如实登记,非实现缺口 | recompute_gate_a 语义(`research_provenance.py:1059-1064` 核心缺失→FAIL)+通道核心分布实测 |
| 模式 B query=None | `AssemblyRefused`(查询 IR 缺席,E2E-B WP-B1 未落地;「按缺席登记路径处理」=**绑定级**缺席透传,查询级无上下文即拒绝,不产空壳输入) | DESIGN L219 依赖行 + §六模式 B 触发源;fail-closed 优先 |
| 模式 B RESOLVED 绑定接地 | binding.provenance.fact_id 必须在权威快照 facts 在场**且** provenance.snapshot_id==snapshot.snapshot_id,任一不满足 → `AssemblyRefused`(接地 fail-closed,无数值进入无法溯源) | DESIGN §三(a) 机制4 数值零旁路 + E2E-B §三(b) 接地强制 L111-116 |
| 模式 B ABSENT_* 绑定 | 逐条透传进 absent_registry:{metric_id, level=binding.status, reason=binding.absence_reason},不取数不补零 | E2E-B 四级缺席(表 L124-127)+DESIGN L68 |
| task_ref 回显纪律 | task_ref 六字段自任务档逐字透传(只读回显,不改写不重算);window 仅取 {start,end} 两键 | DESIGN §五④映射表 L182(echo 三方一致纪律) |
| prior_knowledge 来源 | 装配器不读 config(thesis.json/allocation_views.json),接受注入的 {theses_block, views_block, prior_conclusions};缺省 None/None/[] | 读取面封闭(DESIGN §三(a) 机制1);渲染属既有模块职能,注入边界保持装配器纯函数性 |
| scorecard_summary/correlation_ref/news_index_ref 来源 | 接受注入;缺省= `MISSING_REF_STATUS` 显式缺席(非 None 隐藏) | DESIGN L67 三引用面;缺席如实登记 |
| expected_snapshot_digest | 可选参数: 调用方携先验声明 digest(如任务档/研究记录绑定)→ 装配时重算比对,失配拒绝;缺省不比对(装配时 R5 重算值仍入 snapshot_binding) | 三重核验模式之「meta 声明+内容摘要重算」(DESIGN §三(a) 机制1) |
| echo 纪律 | `echo_params()` 返回 §2.1/§2.2 全部登记参数;测试断言 echo=常量=本登记表(R011 三方一致) | R011 纪律沿用 |

---

## §三 逐要点证据映射表(合同 AC-02;要点→实现落点→证据指针→自检结论)

DESIGN L220 五条验收要点逐条映射(要点文本见 §0.1 抄录;工件=测试文件+CI run):

| 要点 | (a) 实现落点 | (b) 证据指针 | (c) 自检结论 |
|---|---|---|---|
| ①输入契约字段级校验单测 | `scripts/glm_input_assembler.py:293`(validate_input,九字段逐项);装配末步自检 `scripts/glm_input_assembler.py:472`/`:544`;用例 `tests/test_p03_w2_glm_g1.py` T1(`T1_ModeAInputContract`)/T1c(validate_input 负向6条) | 本地套件日志 `local-ci/test_p03_w2_glm_g1.log`(33用例 OK);负向敏感性 D4 注入红3条 | 过——九字段正反向用例齐,字面量断言(gri-1.0/hs-1.0/2/True/True) |
| ②禁直读负向测试: 装配产物零原始档路径引用 | 产物层: `T2b_NoRawArchivePaths`(全字符串扫描,唯一例外=facts[].source_file 规范 basename 披露槽位,DESIGN L74 机制2);源码层: `T2c_SourceBoundaryLock`(零 open(/零glob/零网络/零凭证/零原始档目录字样+单处 ACCESS_POINT_EXEMPT);机制1落点 `scripts/glm_input_assembler.py:555`(rp.select_snapshot 唯一接入点) | 负向敏感性 D3 红证 `negative-sensitivity/D3-absent-suppress.log` | 过——产物+源码双层负向 |
| ②Gate A FAIL 拒绝装配 | `scripts/glm_input_assembler.py:98`(_gate_check,R2 复算+R3 放行复用);用例 `T2_GateRefusal`(FAIL 拒绝+声明矛盾 None 拒绝) | `local-ci/test_p03_w2_glm_g1.log`;D1 注入红3条 `negative-sensitivity/D1-gate-bypass.log` | 过——fail-closed,沿 data_assembler.py:323-329 拒绝语义 |
| ③缺席登记: 构造缺席指标→absent_registry 如实登记 | `scripts/glm_input_assembler.py:159`(classify_absence 四级纯函数)+装配落点 `:453`;用例 `T3_AbsentRegistry`(JGB_10Y→ABSENT_REGISTRY,SILVER_F→ABSENT_DATA,零填0断言)+`T3b_ClassifyAbsenceFourLevels`(四级枚举直测) | `local-ci/test_p03_w2_glm_g1.log`;D3 红证 | 过——缺席如实登记非零值,产物中缺席指标零数值形态出现 |
| ④快照绑定核验: 篡改快照后装配拒绝 | R5 层: `scripts/glm_input_assembler.py:109`(_snapshot_binding,expected_snapshot_digest 比对);R2/R3 层: `_gate_check`(98)声明↔重算矛盾→None→拒绝;用例 `T4_SnapshotBindingTamper`(值篡改摘要失配拒/声明说谎无声明亦拒);R5 机制引用=research_provenance.py:1297(登记 §1.1) | `local-ci/test_p03_w2_glm_g1.log`;D2 红证 `negative-sensitivity/D2-digest-bypass.log` | 过——双层核验,篡改三形态(值/声明/计数)全拒 |
| ⑤CI 零回归 | 无代码落点(工件=run ID);本地全量=58文件(57跑+1合同排除)=56绿+1既有红(test_p4_fixes,4项 monthly_review 数据块,基线 a6d086b 既有归因,与本包零导入关系);新增套件恰 1(test_p03_w2_glm_g1)=56+1=57 预期 | 本地逐套件日志 `local-ci/`(58份);CI dispatch=操作者 CHECKPOINT,登记件将落 `rounds/026/GLM-WP-G1-CI-dispatch-evidence.md` | 本地过(新增套件绿+零回归);CI 侧=NOT VERIFIED(待操作者 dispatch,执行Agent 禁自行触发) |

模式 B 形态(DESIGN L219 依赖行「未落地前按缺席登记路径处理」落点,非独立要点): `assemble_mode_b`(`scripts/glm_input_assembler.py:478`)+`_query_ref`(`:238`);用例 T5 族 6 条(装配/接地失败拒/快照失配拒/身份不符拒/无IR拒/目标失配拒)。自检: 过——绑定级缺席透传+查询级 fail-closed,与登记决策(§二.3)一致。

辅助登记(非要点,如实): FixtureSanity 2 条为 fixture 自检(合成快照经既有权威机制 rp.gate_status 回读期望态,非被测模块断言);T6 R1 壳 2 条(标准化层选择同构+无快照拒绝);T7 schema 契约 2 条;T8 echo 三方一致 1 条;合计 33 用例。

---

## §四 git 取证与自检(提交时回填;最终尖端以 ls-remote 为准)

- 指定并入步: merge 提交 `e67f710`(merge --no-ff 0c8de3c3,"merge GLM design (R019 PASS)"),带入设计六件恰 6 行 A、零 M/D(`git diff --name-status a6d086b..HEAD` 并入后实测);merge-base=`1ddfb65`(实测,与合同 §零 预期一致)。
- 开发提交: 线性(见 `git log --oneline`,提交信息逐条登记范围);reflog 无 reset/amend;不 force push;不碰 main。
- 交付文件双源一致性: git 尖端版 vs 工作树版交叉哈希见证据包成员②。
- LS-REMOTE 尖端+28 支对照: 见证据包成员③(原样输出)。

---

## §五 提交前数值标注六项自检清单(合同 §5.3;双文档=本件+DELIVERY 全文扫描)

边界声明(第5项): 本文日期时刻=UTC(另注明除外);SHA 一律全值或合同冻结值;行号/结构编号(L216-220 等)=并入后工作树实读;档键成分(gri-1.0/hs-1.0/RT-/QB-/HY- 前缀)=标识符非数据值。

| # | 数值 | 标注 |
|---|---|---|
| 1 | 交付文件 k=4 | [实取·来源: REPORT §0.2 清单=git ls-files 对照零重合,4 路径均为本包新增] |
| 2 | 设计六件=6 行 A | [实取·来源: git diff --name-status a6d086b..e67f710 并入后实测(§四)] |
| 3 | 核心指标 32/active 80/4 通道 | [实取·来源: python 实测 config/metric_registry.json+rp.active_registry_metrics()/core_metric_ids(),2026-11-04T16:3xZ] |
| 4 | 专项测试 33 用例(2+3+6+2+1+1+1+4+2+6+2+2+1) | [实取·来源: 本地运行输出 "Ran 33 tests ... OK"(local-ci/test_p03_w2_glm_g1.log)] |
| 5 | 负向敏感性 D1红3/D2红1/D3红1/D4红3/回绿 exit=0 | [实取·来源: negative-sensitivity/*.log 五份] |
| 6 | 本地全量 58 文件=57 跑+1 排除=56 绿+1 红(test_p4_fixes 4 项) | [实取·来源: local-ci/ 58 份日志+test_p4_fixes.log「39通过/4失败」] |
| 7 | CI 基线 56 套件/run 41862875466 | [实取·来源: 注入快照(合同冻结章,2026-11-05 00:5x HKT),非工作树实读] |
| 8 | data 27 文件(24 daily+3 research) | [实取·来源: datapath-zero-touch-snapshot.txt 计数,2026-11-04T16:4xZ] |
| 9 | HISTORY_TAIL_MAX=5 等 §二 登记参数 | [登记值·本包登记(§二);非仓库既有统计;echo=常量=登记三方一致(T8 实测)] |
| 10 | 锚点值 2.93/4186.7 | [合成 fixture 字面量·非实取](E2E-A 登记窗终值语义的合成复用,不代表本包真实数据) |
| 11 | merge e67f710/merge-base 1ddfb65/基线 a6d086b8…/0c8de3c3… | [实取·来源: git log/merge-base/ls-remote 实测(§四+证据包成员③)] |
| 12 | 开工时刻 2026-11-04T16:27:04Z | [实取·来源: date -u 开工实测] |

第3项复核: 逐个 [实取] 项已回工作树/命令输出复核一遍(2026-11-04T16:5xZ);未发现失实项;第7项为注入快照引用,已显式标注非工作树实读。本清单自身成件入证据包(成员①附带)。
