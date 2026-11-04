# IA-P03-E2EB-WP-B5 REPORT — E2E-B场景端到端验收(接地强制渲染+走查固化)

> 包: IA-P03-E2EB-WP-B5(E2E-B 第 5 实现包·B 族末包)
> 基线: `ac01d0726228f4c2196a0618218332717829575f`(dev/p03-e2eb-b4 最终交付尖端,R024 审计 PASS)
> 分支: `dev/p03-e2eb-b5`(自基线切出,纯线性开发,本包无并入步)
> 开工时刻(UTC): 2026-11-04T23:21:09Z(git status clean 实取)
> 边界声明(REPORT 头部,§5.3 第5项): 本文日期/时刻一律 UTC(另标注者除外);SHA 一律全值;档键成分(如 QB-20261102-001)为标识符非数据值。

---

## §零 规格抄录与交付面登记(开工首步,AC-01)

### (i) DESIGN §六 WP-B5 行四要素逐字抄录

实读 `docs/P03_E2EB_DESIGN.md`(基线工作树,设计在场核验通过后),WP-B5 行位于 L234-238,逐字抄录如下:

```text
L234: **WP-B5 E2E-B场景端到端验收(接地强制渲染+走查固化)**
L235: - 目标: 回答渲染层: 接地强制(§三(b),无源数值fail-closed)、缺席文本化、质量披露;把§三(d)走查固化为端到端黄金用例(问题→IR→执行→接地答案)。
L236: - 范围: 渲染/校验模块+端到端测试;含GAP-05的write=False快照测试范式固化。
L237: - 依赖: WP-B1/B2(必),WP-B4(查询历史记录)。
L238: - 验收要点草案: ①无provenance数值注入→渲染fail-closed负向测试(工件: 测试文件) ②端到端黄金用例: DEV授权副本上全链路,断言美端值+日端「无数据」+OP-1 NO_DATA(工件: 测试文件+数据档引用) ③WP-B3完成后同用例升级为双端闭合版(工件: 测试+新数据档) ④CI零回归(工件: run ID)。
```

四要素齐备(目标/范围/依赖/验收要点),无缺失。依赖列核验: WP-B1/B2/B4 均已在基线工作树落地交付(§一实读: scripts/e2eb_query_ir.py+e2eb_query_mapper.py / scripts/e2eb_query_executor.py / scripts/research_archive.py 在场);B3 非本包硬依赖(冻结合同 §0 生效前置段: 「依 DESIGN §六 WP-B5 依赖列(=WP-B1/B2 必+WP-B4),B3 非本包硬依赖」);依赖列不要求并入他支、不含 GLM/网络/新数据源凭证要求 → 无情形(d)停止条件。要点③=DESIGN 原文「WP-B3完成后同用例升级为双端闭合版」=**B3 条件款**: B3 三段(d)停泊中(v1.3 处置待用户),本包按冻结合同 §0 处置=要点①②④照常交付(日端「无数据」如实=当前事实),要点③按情形(c)如实登记「升级版待 B3 落定,由后续轮承接」(REPORT §四映射表+§七.2),禁静默跳过、不构成情形(d)。

### (ii) 交付文件清单(k=4,登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据 |
|---|---|---|
| 1 | `scripts/e2eb_answer_renderer.py` | DESIGN L235「回答渲染层」+L236「渲染/校验模块」恰 1 个代码模块+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」;DESIGN L115「渲染校验(WP-B5工件)」/L248「实现于WP-B5渲染层」为该模块机制落点;文件名依 B2 先例(其 REPORT §零(iii): 「依固定推导规则与 B1 命名族(e2eb_*)命名」)取 e2eb_ 命名族 |
| 2 | `tests/test_p03_e2eb_b5.py` | DESIGN L238①②③工件「测试文件」+合同附录A §零(ii)「含代码则必含 tests/test_p03_e2eb_b5.py」;L236「端到端测试」 |
| 3 | `docs/P03_E2EB_B5_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P03_E2EB_B5_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L238④「CI 零回归」证据落点=DELIVERY §五(沿 B4 先例) |

### (iii) 结构约束核验

- 与 `git ls-files` 输出零重合: 4 路径均为纯新增(开工时实读 `git ls-files scripts/ tests/ docs/` 无一存在;B1 交付件=e2eb_query_ir.py/e2eb_query_mapper.py/test_p03_e2eb_b1.py/P03_E2EB_B1_*.md,B2 交付件=e2eb_query_executor.py/test_p03_e2eb_b2.py/P03_E2EB_B2_*.md,B4 交付件=research_archive.py/test_p03_e2eb_b4.py/P03_E2EB_B4_*.md,E2E-A 六件与 G1-G3 交付件均与本清单零重合)✓
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p03_e2eb_b5.py)✓
- 推导无越界: 范围列「渲染/校验模块」=恰 1 个代码模块(DESIGN L115 机制名「渲染校验」单数落点;对照 B1「新增IR定义模块+映射器」=2 模块的并列写法,本行「/」为同模块职能复指非两模块并列)→ scripts/ 恰 1 文件;「+端到端测试」→恰 1 tests 文件;未引入 DESIGN 依据外文件 ✓

### (iv) 运行产物边界登记

WP-B5 验收要点(L238①-④)工件全部为离线测试文件/CI run 登记类;范围列(L236)为渲染/校验模块+端到端测试,DESIGN 未为 WP-B5 指定编排入口或真实运行要求(要点②「DEV授权副本上全链路」的测试数据源处理=冻结合同 AC-03 合成 fixture 唯一数据源纪律,沿 B2 §七.1 审计 PASS 先例,差异如实登记于 §七.1)→ 本包登记「**零运行产物**」: data/research/ 零真实写入(测试全合成 fixture 写 tempdir,见 §六 D-B5-14),data/daily 与既有快照零读取零写入。全链路可离线验证面由 tests/test_p03_e2eb_b5.py 覆盖(§四映射表)。

---

## §一 前置实读登记(file:line)

(实现前实读,全部为基线工作树(ac01d072)实取,非注入摘要)

| 对象 | 登记 |
|---|---|
| DESIGN §三(a) IR schema | docs/P03_E2EB_DESIGN.md:53-107(MetricBinding L70-79/Provenance L81-89/DerivedOperation L91-100) |
| DESIGN §三(b) 接地规则 | 同文件:111-116(来源标识三形态 L113;派生必附 calculation_ref L114;**渲染 fail-closed L115**;质量传导 L116) |
| DESIGN §三(c) 缺席四级 | 同文件:118-129(A1-A4 措辞 L124-127;NO_DATA 不部分计算+显式「无数据」L129) |
| DESIGN §三(d) E2E-B 走查 | 同文件:131-163(黄金问题文本 L134;接地作答样例骨架 L158-161;「不得推断日端」L161) |
| DESIGN §四 E2E-A 对齐 | 同文件:167-185(§4.1 ID 引用约定 L180-185;行6 query_history append-only L176) |
| DESIGN §五 差距清单 | 同文件:189-200(**GAP-05→WP-B5 L197**;GAP-08→WP-B5 L200) |
| DESIGN §六 WP-B5 行 | 同文件:234-238(§零(i) 逐字抄录) |
| DESIGN §七 红线 | 同文件:244-249(L246 快照纪律;L247 LIVE 禁写;**L248 禁交易/收益承诺「回答模板禁止投资建议措辞(实现于WP-B5渲染层)」**;L249 数据不足不填0) |
| B1 IR 模块(承接) | scripts/e2eb_query_ir.py:32-68(常量: PROVENANCE_KEYS L64-65/FACT_ID_RE L54/SNAPSHOT_ID_RE L55/ISO_DATE_PREFIX_RE L56/ANSWER_CONSTRAINTS L42-43)/94-123(_validate_provenance)/248-304(validate_ir 双阶段) |
| B1 映射器(承接) | scripts/e2eb_query_mapper.py:35-39(**OUT_OF_SCOPE_PATTERNS 21词**——B5 守卫复用面)/57-103(CONCEPT_RULES 恰4条;黄金问题触发规则1/2/3)/163-322(map_question;OOS 拦截 L189-199) |
| B2 执行器(承接) | scripts/e2eb_query_executor.py:70-73(_refusal 四键结构)/119-131(_mark_resolved: provenance 七字段装配)/267-359(execute_query;返回结构 docstring L279-283: {ir,values,snapshot_id,gate_status} 或 refusal;主入口 L358-359) |
| B4 档案(承接) | scripts/research_archive.py:164-186(build_answer_summary)/293-344(append_query_record 八步链;execution 一致性 L311-312)/349-377(load_query_record/verify_query_record: digest 复算对照 L371-375) |
| B1 参数登记(承接) | docs/P03_E2EB_B1_REPORT.md:122-159(§六 D-B1-01..13;D-B1-07 OOS 词表) |
| B2 参数登记(承接) | docs/P03_E2EB_B2_REPORT.md:166-189(§六 D-B2-01..14;D-B2-03 refusal/D-B2-05 provenance 装配) |
| B4 参数登记(承接) | docs/P03_E2EB_B4_REPORT.md:148-172(§六 D-B4-01..12;D-B4-05 append 语义) |
| S1 快照构建入口 | scripts/snapshot_builder.py:236-438(**write=False 早退 L384-385**;GAP-05 范式落点) |
| R3 门禁放行判定 | scripts/research_provenance.py:1183-1188(PASS/DEGRADED 放行;FAIL/None 拒绝) |
| R5 快照内容指纹 | scripts/research_provenance.py:1297-1301(digest_snapshot=canonical JSON sha256 前16位) |
| E2E-A 任务管理器接口(§四行3 对齐认知) | scripts/research_task_manager.py:36-38(SCHEMA_MIN_FIELDS 含 falsifiable_conditions)/40-42(REPLAY_POLICY)/48-53(make_task_id=RT-{start}~{end}-{rule}-{hash8} 实况形态;B5 无调用面,升级路径属 E2E-A) |
| E2E-A 档案机制先例 | data/research/ 在场档(RT-*.json/detection_series_*.json;data/ gitignored;B5 零写入) |
| B2 测试范式(参照) | tests/test_p03_e2eb_b2.py:41-82(合成 fixture 注册表)/159-243(write_day_files 生成器)/302-308(quiet_build=write=False 范式)——**结构参照非复制对象,B5 自建独立 fixture(§六 D-B5-14)** |
| B1 黄金 IR 字面量(参照) | tests/test_p03_e2eb_b1.py:341-414(golden IR 全量字面量: MB-1..MB-11/OP-1..OP-3 形态锚) |

---

## §二 实现(逐文件)

(实现后回填;见 §五 commit 链)

---

## §三 测试与本地CI

(实现后回填)

---

## §四 逐要点证据映射表(AC-02)

(实现后回填)

---

## §五 模块SHA登记

(实现后回填)

---

## §六 实现参数与决策点登记(先登记后运行,运行后禁回改)

| # | 决策点 | 登记内容 |
|---|---|---|
| D-B5-01 | 模块与命名 | 渲染/校验模块=恰 1 个代码模块 `scripts/e2eb_answer_renderer.py`(e2eb_ 命名族沿 B1/B2 先例);职责=接地校验(fail-closed)+缺席文本化+质量披露+禁投资建议文案守卫;**不含**取数(B2 产出为唯一输入面)/映射(B1)/档案写入(B4——测试链复用调用演示);公共 API 白名单: `GroundingError`/`validate_value_node`/`validate_derived_node`/`assert_no_advice`/`render_answer` |
| D-B5-02 | 接地标识三形态(DESIGN L113) | 进入回答的数值节点必携**至少一种完整**形态: ①`metric_id`(非空str)+`fact_id`(qir.FACT_ID_RE 匹配,复用禁复制)②`snapshot_id`(qir.SNAPSHOT_ID_RE 匹配)+快照字段路径(非空str;level=`facts[].value`/derived_window=`facts[].derived.{window}.{field}`,L113 例式)③`source_file`(非空str)+`observation_date`(qir.ISO_DATE_PREFIX_RE 匹配);校验独立于 qir.validate_ir 纵深防御(渲染层不信任上游自行复验) |
| D-B5-03 | 派生值接地(DESIGN L114) | 派生/计算数值节点(COMPUTED op)必附 `calculation_ref`(非空str)**且**全部 operand 绑定 provenance 在场(逐 operand 至少一种完整形态);输入观测日已在 calculation_ref 内(B2 D-B2-09 保证) |
| D-B5-04 | fail-closed 语义(DESIGN L115) | 任一数值节点接地校验失败→抛 `GroundingError`(ValueError 子类),**零部分输出、不降级为无源输出**;渲染函数无「尽力而为」路径;refusal 输入(无数值行)不触发 |
| D-B5-05 | 质量披露模板(DESIGN L116) | RESOLVED 事实 quality_status≠"PASS" 进入回答→该数值行追加 ` | 质量披露: {status}(非PASS降级披露,A4纪律)` |
| D-B5-06 | 缺席文本化措辞(DESIGN L124-127 逐字) | A1=`该指标不在注册表(无身份定义),无法取数`;A2=`指标已注册但当日采集缺失`;A3=`本期无该指标事实`;A4=absence_reason 原样转述(A4 行=「{reason}(引擎原因原样转述)」);缺席行恒含「无数据」字样(L129) |
| D-B5-07 | NO_DATA 措辞 | 派生 NO_DATA 行=`{op_id} {formula}: 不可计算(NO_DATA,operand缺席不部分计算)`;不部分计算不近似(L129) |
| D-B5-08 | 禁投资建议守卫(DESIGN §七3/L248) | `assert_no_advice(lines)`: 对**数值行/派生行/缺席行/头部行**逐行扫描 **复用** `eqm.OUT_OF_SCOPE_PATTERNS`(B1 D-B1-07 词表,复用调用禁复制)命中→GroundingError fail-closed;**豁免行(kind 白名单登记)**: `unresolved`(其职责=如实引用超界指称原文,L60/L102-106 原样保留语义;B1 NOTE_OUT_OF_SCOPE 自身含「不构成投资建议」措辞)与 `footer`(标准免责声明行「不构成投资建议(§七3)」自身含词表词);渲染模板结构性不产建议措辞+守卫防御纵深 |
| D-B5-09 | refusal 渲染(B2 D-B2-03 消费面) | execution 携 `refusal` 键→kind="refusal",answer_text=`无法作答: {refusal}`+footer;零数值行(无接地校验对象);守卫照常扫描 |
| D-B5-10 | 行格式与确定性顺序 | 行序=头部→绑定行(IR 序)→派生行(IR 序)→未解析行→footer;模板(逐字登记): 头部=`【接地作答\|模式B】query_id={qid};研究截止as_of={as_of};快照={snapshot_id};门禁={gate_status}`;数值行=`{bid} {metric_id}{window_part} = {value} @{observation_date}(fact {fact_id};源 {source_file};快照 {snapshot_id})`(window_part 仅 derived_window=`[{window}.{field}]`;derived_window 追加 ` 口径: {calculation_ref}`);缺席行=`{bid}: 无数据——{phrase}`(A1/A2/A3)或 `{bid}: 无数据——{reason}(引擎原因原样转述)`(A4)+`(登记: {absence_reason})`(A4 不重复);COMPUTED 行=`{op_id} {formula} = {result} {unit}({calculation_ref})`;未解析行=`未解析指称: 「{mention}」({mapping_status}): {note}`;footer=`缺席摘要: 无数据{n_absent}项/不可计算{n_nodata}项;缺席如实登记,不以相近指标冒充、不内插、不填0(§三(c))。本回答为接地研究信息,不构成投资建议(§七3)。`;**绑定行不显示单位**(单位=注册表面,渲染层单一数据依赖原则=execution result;例外=op.unit IR 自带);渲染前防御断言 answer_constraints.grounding_required is True(schema 恒真,纵深防御) |
| D-B5-11 | 数值类型守卫 | bool 非数值(`isinstance((int,float)) and not isinstance(bool)`,qir._is_number 同语义);字符串数字不算;缺席/NO_DATA 行零 result 数值 |
| D-B5-12 | 零文件IO/零网络 | 模块纯函数: 零 open()/零 glob/零 os.listdir/零网络 import/零墙钟;依赖面=qir(B1)+eqm(仅 OUT_OF_SCOPE_PATTERNS 复用)恰 2 个项目模块 |
| D-B5-13 | B4 查询历史衔接 | 渲染产出 dict: `{kind, answer_text, lines, value_nodes, absent, no_data, n_grounded_values, quality_disclosures, gate_status, snapshot_id}`;B4 衔接=测试链复用调用 `ra.append_query_record(ir, snapshot, execution)`(executed IR+执行结果落 query_history)+`ra.verify_query_record`(digest 复算);渲染器自身零档案写入 |
| D-B5-14 | 黄金走查固化形态(DESIGN §三(d)) | 端到端黄金用例=问题文本(L134 逐字复用 B1 GOLDEN_Q)→B1 `map_question`(fixture 注册表)→B2 `execute_query`(注入 S1 write=False 快照或 daily_dir 自取)→B5 `render_answer`→断言: 美端值(**本包独立发明 fixture 字面量**,经引擎原语预演核验誊写)+日端「无数据」(MB-8/MB-9 ABSENT_REGISTRY)+OP-1 NO_DATA;**不复制** DESIGN L145-156 走查实测值(其为 2026-11-02 时点实取,B5 fixture 为独立发明场景;B3 停泊期日端缺席=当前事实);fixture 自建(结构复刻采集档格式,数值全发明,与 B2 测试文件互不导入——零跨测试文件耦合) |
| D-B5-15 | GAP-05 write=False 范式固化 | 黄金 e2e+专项范式用例断言: ①执行后数据目录零 `research_snapshot_*.json` 持久化文件(write=False 语义,S1 L384-385 早退)②空目录起跑→R1 无既有快照→S1 离线构建(executor daily_dir 路径,B2 D-B2-01)③同输入双跑确定一致;B4 verify 用快照 JSON 由**测试侧**写独立 snapshot_dir(非 S1 持久化),数据目录保持零持久化 |
| D-B5-16 | 要点③ B3 条件款处置 | 要点③=「WP-B3完成后同用例升级为双端闭合版」=B3 条件款;B3 三段(d)停泊中→本包**登记不实施**: §四映射表要点③行自检=情形(c)「升级版待 B3 落定,由后续轮承接」;渲染层 COMPUTED 数值行通用能力由黄金 OP-3 覆盖(非双端闭合版实现);日端「无数据」如实=当前事实(要点②断言面) |

(登记时刻 UTC 2026-11-04T23:5xZ;此后任何参数变更=违约,除非按 §七如实登记为新尝试)

---

## §七 偏离与如实声明

(实现后回填)

---

## §八 合同逐条自检(AC-01~AC-07)

(实现后回填)

---

## §九 提交前数值标注六项自检清单(§5.3,强制)

(实现后回填)
