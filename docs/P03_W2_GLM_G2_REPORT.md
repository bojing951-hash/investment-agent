# IA-P03-W2-GLM-WP-G2 执行报告(结构化输出契约与校验器)

> 工作包: IA-P03-W2-GLM-WP-G2(G 族第 2 包: WP-G2 结构化输出契约与校验器)
> 分支: `dev/p03-w2-glm-g2`(自基线 `f5dc79fc5b86f70e98b10753acfd9b45845e52ea` 切出,纯线性,本包无并入步)
> 冻结合同: IA-P03-W2-GLM-WP-G2-AC-v1.0(2026-11-05 02:1x HKT 冻结生效;本报告为合同 §零登记制落点)
> 边界声明: 本包**零真实 GLM/LLM 调用、零凭证、零付费、零网络出站**(设计对象≠设计手段;DESIGN L224「不含真实调用(以确定性样例驱动)」;真实调用属 WP-G4,执行前置=用户批准凭证/费用,PENDING 未批)。日期/SHA/结构编号/档键成分按合同边界出圈登记: 本文日期时刻均为 UTC(另注明者除外);SHA 一律全值;HY-/RT-/QB- 前缀=标识符非数据值。

---

## §零 规格抄录与交付面登记(合同 AC-01 落点;开工首步)

### 0.1 WP-G2 行四要素逐字抄录(实读 `docs/P03_W2_GLM_DESIGN.md` §七,基线工作树实况)

以下为 DESIGN §七 WP-G2 行**逐字抄录**(无增删改字;行号=基线 f5dc79f 工作树实读行号,审计对照允许偏差≤3行):

- **L222**: `**WP-G2 结构化输出契约与校验器**`
- **L223**: `- 目标: 落地§三(c) 七字段 schema+§四竞争性/反方证据/区分性校验+§三(b) 失败三径。`
- **L224**: `- 范围: 输出 schema 定义+校验器+假设-证据映射表构建;不含真实调用(以确定性样例驱动)。`
- **L225**: `- 依赖: WP-G1(输入契约)。`
- **L226**: `- 验收要点草案: ①schema 正向用例(工件: 测试文件) ②负向敏感性用例: counter_evidence 空/数值不在输入证据包/竞争假设无区分性判据/缺席未承接——各须被拒(工件: 测试文件) ③阈值取值约束测试: 编造 target 被拒,三合法来源通过(工件: 测试文件+registry 引用) ④失败三径状态机测试: 重试→降级→缺席登记全路径(工件: 测试文件) ⑤CI 零回归(工件: run ID)。`

四要素齐备(目标/范围/依赖/验收要点),无缺失。**冲突自查(合同 §零(iv))**: 要素齐备可推导 ✓;范围明示「不含真实调用(以确定性样例驱动)」——与 WP-G4 分层一致,不要求真实 GLM 调用/网络/新数据源凭证 ✓;依赖列「WP-G1(输入契约)」与基线实况一致(基线 f5dc79f=WP-G1 最终交付尖端,`scripts/glm_input_assembler.py` 在场,实读接口见 §一)✓,不要求并入他支(本包无并入步,合同 §零 定值)✓ → 无情形(d)冲突,合法开工。

### 0.2 交付文件清单(登记制白名单,k=4;推导逐条附 DESIGN 依据)

DESIGN L224 范围列为**模块级**(「输出 schema 定义+校验器+假设-证据映射表构建」=单一校验器模块的三项能力,DESIGN L222 包名「结构化输出契约与校验器」单数)而非文件级 → 按合同 §零(ii) 固定推导规则生成:

| # | 路径 | 类型 | DESIGN 依据 | 推导规则 |
|---|---|---|---|---|
| 1 | `scripts/glm_output_validator.py` | 代码(校验器模块) | DESIGN L223「落地§三(c) 七字段 schema+§四竞争性/反方证据/区分性校验+§三(b) 失败三径」+ L224「范围: 输出 schema 定义+校验器+假设-证据映射表构建」 | 每个代码模块 = `scripts/` 下恰 1 文件 |
| 2 | `tests/test_p03_w2_glm_g2.py` | 测试 | DESIGN L226 要点①-④工件「测试文件」 | 含代码则必含本文件(合同固定名) |
| 3 | `docs/P03_W2_GLM_G2_REPORT.md` | 文档(本件) | DESIGN L226 工件面(要点逐条证据映射/参数登记落点);合同必含件 | 必含 REPORT |
| 4 | `docs/P03_W2_GLM_G2_DELIVERY.md` | 文档(交付说明) | DESIGN L254 交付说明惯例(参照 GLM 设计交付件与 G1 先例);合同必含件 | 必含 DELIVERY |

**结构约束核验(iii)**:
- 与 `git ls-files` 零重合: 上述 4 路径在基线 f5dc79f 工作树**不存在**(开工时 `git ls-files` 实测对照=265 文件零命中,取证见 §四)✓;
- 必含 DELIVERY ✓(#4);含 `.py` 实现(#1)则必含对应 tests(#2)✓。

DESIGN L226 工件名为泛称「测试文件」,与合同固定推导名 `tests/test_p03_w2_glm_g2.py` 无冲突(无 glob 级偏差;对照 G1 命名偏差先例,本包无此项)。

### 0.3 运行产物边界登记

WP-G2 验收要点①-④工件=**测试文件**(离线合成 fixture 驱动,确定性样例),要点⑤工件=GitHub Actions run ID(操作者 CHECKPOINT dispatch)。校验器模块**无编排入口/无真实运行要求**(DESIGN L224「以确定性样例驱动」;对照 E2E-A `--run-e2e` 先例: 其合同要点明文要求真实回放,WP-G2 行无此要素)→ 本包登记「**零运行产物**」: `data/research/` 无新增运行档案,`data/daily/` 与既有快照全程只读零触碰。依据=DESIGN L226 逐要点工件清单(实读,见 §0.1 抄录)。

---

## §一 前置实读登记(数据接入点与机制引用,file:line 为基线 f5dc79f 工作树实读)

### 1.1 WP-G1 在场交付件接口(依赖行「WP-G1(输入契约)」落点;复用调用,禁复制分叉)

| 机制 | 落点(file:line) | 用途 |
|---|---|---|
| G1 登记清单(合同 AC-05.5 对照同源) | `docs/P03_W2_GLM_G1_REPORT.md:24`(§0.2 k=4) | G1 交付文件对照面(本包零改动其 4 文件) |
| 输入契约校验 `validate_input` | `scripts/glm_input_assembler.py:293` | 管线入口复用(G1 九字段契约判定,入参非法 fail-closed 拒绝) |
| `MIN_COMPETING_HYPOTHESES` | `scripts/glm_input_assembler.py:55` | 竞争假设数下限(合同级设计规则;运行权威=输入 prompt_contract.min_competing_hypotheses,G1 装配落点 `:287`) |
| `MODE_ENUM` | `scripts/glm_input_assembler.py:45` | 模式 A/B 分支判据(输出契约裁剪分支,DESIGN §六) |
| `OUTPUT_SCHEMA_VERSION_DEFAULT='hs-1.0'` | `scripts/glm_input_assembler.py:64` | 输出 schema 版本沿用(G1 登记明示「WP-G2 落地 schema 后沿用或经登记修订」;本包沿用,登记 §二.1) |

### 1.2 设计依据实读(`docs/P03_W2_GLM_DESIGN.md`,基线工作树=blob c72d41a1 与 0c8de3c3 侧等值,步骤4 已核)

- §三(b) 调用面/失败三径: `:78-89`(三径定义 径1重试 L85/径2降级 L86/径3缺席登记 L87;参数=DP L89;结构化输出格式=单一 JSON 对象+围栏/注释容忍 L82);
- §三(c) 输出契约七字段+骨架: `:91-116`(七字段表 L95-103;JSON 骨架 L107-115;phenomenon_echo L113/absent_ack L114;证据引用只允许在场事实+数值未改写核对 L99);
- §四 竞争性解释机制: `:120-148`(六槽位 L122-131,竞争性判定+区分性判据 L128,反方证据强制 L129;(2)假设-证据映射表结构 L133-141;(3)反方证据三机制 L143-148,机制一「空数组→结构校验失败→失败三径」L145);
- §五(1) 推导规则: `:154-161`(阈值三来源 L157;spec 规格化与 op/mode 对齐 L158;区分性检查 L159;不可规格化→limitations 声明 L161);
- §六 模式 A/B 差异: `:193-208`(模式 B 裁剪版=phenomenon_echo+grounded 解释+absent_ack+数值不得新增 L199;falsifiable_conditions 模式 A 强制 L200;ID 族 HY-/RT-/QB- 与交叉引用 L207);
- §八 红线: `:244-250`(禁交易/收益承诺 L246;GLM 产出非事实源+数值接地 L247)。

### 1.3 既有机制复用引用(对齐=复用调用,禁复制分叉)

| 机制 | 落点(file:line) | 用途 |
|---|---|---|
| 预测规格 op/mode 枚举先例 | `scripts/report_generator.py:525-526`(pred_op 比较符>=/<=/>/<;pred_mode expiry/touch) | SPEC_OPS/SPEC_MODES 枚举对齐(DESIGN L158 明示「与现行预测规格对齐」) |
| 重试基线 3 次 | `scripts/report_generator.py:553`(max_attempts=3) | MAX_RETRIES=3 登记依据(DESIGN L85「现行周报链实值 3 次」) |
| VERIFY_MODES | `scripts/allocation_engine.py:77`({'touch','expiry'}) | SPEC_MODES 二次对齐佐证 |
| 注册表访问 | `scripts/research_provenance.py:91`(active_registry_metrics) | 合法来源(ii) 注册表阈值提取(复用调用;测试以 monkeypatch 注入合成注册表,真实 config 不入测试预期值) |
| 事实形态基准 | `scripts/fact_engine.py:210-238`(fact_id=`{metric_id}@{od}` L211;derived=compute_period_returns L225) | 证据引用 fact_id 形态+derived 窗口值字段族(pct/pp/bp/abs_change;L81-174 窗口语义) |
| E2E-A/G1 设计承接 | `docs/P03_W2_GLM_INVENTORY.md:127/128/131`(GG-02/GG-03/GG-06→WP-G2) | 本包承接缺口对照(GG-06 模式 B 输出侧=裁剪版校验落本包) |

---

## §二 实现参数登记(登记制纪律: 先登记后运行,运行后禁回改)

### 2.1 契约常量(DESIGN 明示值/G1 登记值沿用)

| 参数 | 登记值 | 依据 |
|---|---|---|
| `OUTPUT_SCHEMA_VERSION` | `'hs-1.0'` | G1 登记(`glm_input_assembler.py:64`);G1 REPORT §二.2 明示 WP-G2 沿用 |
| `HYPOTHESIS_FIELDS` | `(hypothesis_id, statement, supporting_evidence, counter_evidence, falsifiable_conditions, confidence, limitations)` | DESIGN L95-103 七字段(逐行对应) |
| `TOP_LEVEL_FIELDS` | `(hypotheses, phenomenon_echo, absent_ack)` | DESIGN L107-115 骨架 |
| `MODE_B_FIELDS` | `(phenomenon_echo, explanation, absent_ack)` | DESIGN L199 裁剪版三件(phenomenon_echo+grounded 解释+absent_ack) |
| `EVIDENCE_REF_FIELDS` | `(fact_id, metric_id, direction_note)` | DESIGN L99/L100 |
| `CONDITION_FIELDS` | `(cond_text, spec)` | DESIGN L101 |
| `SPEC_FIELDS` | `(metric, op, target, mode, window)` | DESIGN L111/L158 |
| `SPEC_OPS` | `('>', '>=', '<', '<=')` | report_generator.py:526 比较符族(DESIGN L158「与现行预测规格对齐」) |
| `SPEC_MODES` | `('touch', 'expiry')` | report_generator.py:526 / allocation_engine.py:77 |
| `CONFIDENCE_ENUM` | `('high', 'medium', 'low')` | DESIGN L102 三档枚举 |
| `DIRECTIONS` | `('support', 'counter', 'neutral')` | DESIGN §四(2) L139 枚举(G2 仅发 support/counter,neutral 登记不发,见 §二.3) |
| `NON_SPECIFIABLE_MARKER` | `'不可程序裁决'` | DESIGN L161 声明标记原文 |
| `TRANSIENT_ERROR_KINDS` | `('network', 'risk_control', 'stream_interrupted')` | DESIGN L85 瞬态失败类列举 |
| `COST_BREAKER_KIND` | `'cost_breaker'` | DESIGN L87 费用熔断 |
| 三结局常量 | `ACCEPTED` / `ACCEPTED_DOWNGRADED` / `ABSENT_REGISTERED` | 径1成功/径2降级受纳/径3缺席登记(DESIGN L84-87 三径) |

### 2.2 实现登记值(DESIGN 未定值,本包登记)

| 参数 | 登记值 | 登记理由 |
|---|---|---|
| `MAX_RETRIES` | `3` | DESIGN L85 候选基线=现行周报链实值 3 次(report_generator.py:553);径1重试上限 |
| `BACKOFF_LINEAR_BASE` | `1.0`(秒) | DESIGN L85「线性退避[示意·非实取]」候选;登记: 退避**计划表记录不实际休眠**(离线确定性,零 wall-clock) |
| `DEGRADED_ACK_MARKERS` | `('DEGRADED', '降级')` | 径2义务承接标记(DESIGN L86「limitations 中逐项承接降级」;双语标记容中英产出) |
| `REGISTRY_THRESHOLD_KEYS` | `('range', 'max_week_pct_move')` | DESIGN L157(ii) 点名字段族(validation.range/max_week_pct_move;「等字段族」不扩展——只取点名两族,禁越界引入) |
| `_DERIVED_VALUE_KEYS` | `(value, pct_change, pp_change, bp_change, abs_change, basis_value)` | 合法来源(i)「value/derived 窗口值」(DESIGN L157);basis_value=窗口基准值亦为在场数值;sessions 计数类**不入**合法集(非窗口值语义) |
| 数值抽取豁免族 | ID 族(HY/RT/QB-YYYYMMDD-NNN)、fact_id 形态(`ident@ISO日期`)、ISO 日期、8 位紧缩日期、`(19|20)\d\d年`、`1-12月` | 标识符/日历类非数据值(DESIGN L62/L97「标识符非数据值」同原则);测试直测抽取函数(§三 T2x) |
| 数值抽取单位后缀 | `bps/bp/pp/%` 连缀消费 | 「+73bp」「3.7%」取 73/3.7;千分位逗号归一(4,186.7→4186.7);Unicode 减号(U+2212)归一为 ASCII |
| 数值成员判定 | 浮点严格相等(零容差) | 执行纪律「禁放宽容差」;文本 2.94 vs 在场 2.93=接地失败(DESIGN L99「数值未被改写」核对的落地形态) |

### 2.3 登记型行为决策(实现路径抉择,运行后禁回改)

| 决策点 | 登记决策 | 依据/理由 |
|---|---|---|
| 模式分支 | 校验器按 `inp.mode` 分支: A=七字段全量;B=裁剪三字段(explanation 为单一非空字符串字段) | DESIGN L93「模式 A 全量;模式 B 裁剪规则见§六」+ L199;GG-06(INVENTORY L131)输出侧落本包 |
| 闭合 schema(额外字段拒绝) | 顶层/假设/证据引用/条件/spec 各级键集闭合,额外字段=校验问题 | 防 GLM 经未校验字段旁路数值接地(fail-closed);DESIGN L82「不容忍字段缺失」的对称面;G1 对**输入**容额外字段(前向兼容)系装配侧语义,输出侧不沿用 |
| 证据引用核验 | fact_id 须在输入 evidence_pack 在场且 metric_id 与该事实一致;direction_note 内数值须∈证据包在场数值集 | DESIGN L99「只允许引用输入 evidence_pack 中在场的事实(核对 fact_id 在场且数值未被改写)」 |
| 数值接地分层 | statement/direction_note/limitations/explanation→∈证据包数值集(DESIGN L130「一切数值只能取自输入 evidence_pack」);cond_text→∈三合法来源并集(条件文本携带阈值原文,§五(1)之2);spec.target→∈三合法来源并集;phenomenon_echo/absent_ack=输入复述槽**豁免**接地扫描(其源=输入侧文本,由复述规则约束) | DESIGN L130 与 L157 分层承接;L113/L114 echo/ack 为复述槽 |
| 竞争性区分性判据(确定性实现) | 假设两两配对: 每对须存在可规格条件对 (c_a,c_b) 其 (metric,op,target,mode) 四元组**不全同**→可产生不同裁决=有区分性;任一对全同(或某假设无可规格条件)→「竞争性不足(仅措辞不同而无判据区分)」拒绝 | DESIGN L128/L159;四元组任一异→存在能区分彼此的判据(观测赋值可使两条件裁决相异);机制路径可区分性属 NLP 面,确定性校验器以判据对为唯一可判形态,fail-closed |
| 每假设≥1 可规格条件 | 区分性判据的必要条件: 无可规格条件的假设无法与任何假设区分→拒 | DESIGN L159 推论;模式 A falsifiable_conditions 强制(L200) |
| counter_evidence 空数组 | 一律拒绝(任何 confidence 档) | DESIGN L145 机制一「不存在无反方证据的合法输出」(schema 级硬条款) |
| supporting_evidence 空 | 仅容 confidence='low'(证据单侧) | DESIGN L102 low 定义「证据单侧/缺席相关指标/仅机制推演」 |
| confidence=high 前置 | 须同时: 全条件可规格(无 null target/无 spec=null)+实质字段不涉缺席指标+支持证据非空;违反=拒 | DESIGN L102 high 定义可程序判定子集(「可反驳条件全部可程序核验」/「缺席相关指标」);fail-closed 只罚可证违例,medium/low 自评面不做 NLP 判定 |
| 涉缺席指标降置信的判定面 | 「涉及」=缺席 metric_id 出现于**实质字段**(statement/direction_note/cond_text);limitations 内的缺席承接披露**不算**涉及(披露义务与机制涉及分离,否则承接义务自相矛盾) | DESIGN L86「涉及缺席指标的假设降置信」×L103①「limitations 至少承接 absent_registry 全部条目」的调和 |
| limitations 四义务(可程序判定形态) | ①每假设 limitations 覆盖全部缺席 metric_id(子串在场);②gate_a=DEGRADED 时每假设含降级标记;③每假设含≥1 其他 hypothesis_id(替代解释指针);④每个不可规格条件的 cond_text 子串或「不可程序裁决」标记在场 | DESIGN L103①-④/L86 |
| absent_ack 逐项复述 | 每个缺席 metric_id 须在≥1 条 ack 中在场;absent_registry 空→ack 须空列表(空进空出) | DESIGN L114「逐项复述输入 absent_registry」 |
| phenomenon_echo 复述规则 | 非空;模式 A 须包含 task_ref.phenomenon 原文子串,模式 B 须包含 query_ref.question_text 原文子串 | DESIGN L113「任务/查询现象复述,防答非所问」+ L126 现象复述槽 |
| hypothesis_id 纪律 | 格式 `HY-YYYYMMDD-NNN`(3 位序列);集内唯一;同日(YYYYMMDD 全集一致) | DESIGN L97「同日序列」+ §六 L207「同日序列独立计数」;序列连续性未指定→不强制(最小必要) |
| spec.window | 缺省→默认与 task_ref.window 一致;在场→字符串或 {start,end} 对象 | DESIGN L158「窗口默认与 task_ref.window 一致」 |
| spec.metric 在场约束 | 须∈输入在场指标集(不在场→该条件不可推导,应转 limitations 声明而非产条件) | DESIGN L156「不在场指标→该条件不可推导,转 limitations 声明;不得引入 absent_registry 之外的指标」 |
| target=null/非数值 | 该条件计为不可程序核验→须 limitations 声明(同 spec=null);不计入区分性判据池 | DESIGN L111 骨架 target 可 null 示意+L161 |
| 阈值三来源注入面 | 来源(ii)缺省=`registry_legal_targets()` 经 rp.active_registry_metrics() 复用实取;来源(iii)=`prior_trigger_targets` 注入参数(生产由 G3/G4 编排层传结构化触发值;G1 先验装配面只携渲染文本,无数值通道);测试一律注入合成集(确定性) | DESIGN L157(ii)(iii);G1 REPORT §二.3「装配器不读 config,接受注入」同纪律;R014-D3 漂移防护 |
| 失败三径状态机形态 | `run_conclusion_pipeline(inp, attempts, ...)`: attempts=注入尝试序列(每项 `{'raw': text}` 或 `{'error': msg, 'kind': …}`)——**GLM 调用面桩注入点**;径1=瞬态/解析/校验失败→反馈记录+线性退避计划表(不实际休眠)→重试至上限;径2=校验通过且(gate_a=DEGRADED 或 absent_registry 非空)→`ACCEPTED_DOWNGRADED`(义务经校验器强制),否则 `ACCEPTED`;径3=重试耗尽/费用熔断(kind=cost_breaker 即时)/未知失败类(fail-closed)→缺席事件记录,无部分产出,`task_status_advanced=False` | DESIGN L84-87 三径逐径;L82「校验失败走三径」;L85 重试回注;L87「不部分产出、不静默跳过;任务状态不因此推进」 |
| attempts 语义 | attempts=注入的完整尝试计划;序列耗尽仍未成功→径3(attempts_used=实际消费数≤max_retries) | 确定性样例驱动(DESIGN L224);零真实出站 |
| 管线入口 fail-closed | 入参先过 `gia.validate_input`(G1 契约复用),非空问题→`InvalidResearchInput` 拒绝(不进入任何径) | 依赖行「WP-G1(输入契约)」落地;禁复制分叉 |
| 解析容忍面 | 围栏(``` 及 ```json)与 HTML 注释包裹剥壳后 json.loads;顶层须单一 dict;解析失败=瞬态→径1 | DESIGN L82「解析器容忍围栏/注释包裹,但不容忍字段缺失」 |
| 假设-证据映射表 | `build_hypothesis_evidence_map`(模式 A;公共 API 先复校验,问题非空→`InvalidOutput` 拒绝): 行={hypothesis_id, fact_id, metric_id, direction(support/counter), quality_status(自输入事实透传), snapshot_id, snapshot_digest(自输入绑定)};neutral 登记不发(输出无中性向证据字段,枚举完整性留 G3);模式 B→None(无假设集) | DESIGN L133-141(2)表结构;L140「自快照事实透传」;L141 内容级绑定 |
| 缺席事件记录字段 | {event_type, task_id(模式A)/origin_query_id(模式B), snapshot_id, snapshot_digest, failure_reason, attempts_used, task_status_advanced: False, conclusion_produced: False} | DESIGN L87「含 task_id/query_id、快照绑定、失败原因」+ §六 L207「必携 task_id 或 origin_query_id 之一」 |
| echo 纪律 | `echo_params()` 返回 §二.1/§二.2 全部登记参数;测试断言 echo=常量=本登记表(R011 三方一致) | R011 纪律沿用(G1 §二.3 同款) |

---

## §三 逐要点证据映射表(合同 AC-02;要点→实现落点→证据指针→自检结论)

DESIGN L226 五条验收要点逐条映射(要点文本见 §0.1 抄录;工件=测试文件+CI run):

| 要点 | (a) 实现落点 | (b) 证据指针 | (c) 自检结论 |
|---|---|---|---|
| ①schema 正向用例 | 模式A七字段: `scripts/glm_output_validator.py:33`(HYPOTHESIS_FIELDS 常量)+`:266`(_validate_mode_a);模式B裁剪三字段: `:37`(MODE_B_FIELDS)+`:496`(_validate_mode_b);顶层骨架: `:36`(TOP_LEVEL_FIELDS);解析容忍(围栏/注释): `:111`(parse_hypothesis_set);映射表: `:521`(build_hypothesis_evidence_map,4 行字面量比对);用例 T1 族 6 条+T1b 解析 7 条 | 本地套件日志 `local-ci/test_p03_w2_glm_g2.log`(76 用例 OK);fixture 经 G1 契约回读自检(T0 2 条,复用 gia.validate_input) | 过——模式 A/B 正反向齐,预期值全字面量硬编码(映射表整字典比对 EVIDENCE_MAP_LITERAL) |
| ②负向敏感性: counter_evidence 空 | `scripts/glm_output_validator.py:329`(空即拒,§四(3)机制一);用例 `T2_NegativeSensitivity.test_counter_evidence_empty_rejected` | `local-ci/test_p03_w2_glm_g2.log`;负向敏感性 D1 注入红 4 条 `negative-sensitivity/D1-counter-removed.log` | 过——任何 confidence 档均拒 |
| ②数值不在输入证据包 | 接地分层落点: `:136`(extract_numeric_tokens 豁免族)+`:154`(collect_evidence_numbers 来源(i))+`:317`(statement)/direction_note/limitations/explanation 逐字段核对(数值被改写同拒);用例 `test_statement_value_not_in_evidence_pack_rejected`/`test_direction_note_rewritten_value_rejected`/`test_mode_b_ungrounded_number_rejected`+T5 抽取直测 3 条 | 同上;T2 族 34 条中接地类逐条 | 过——2.94 改写 2.93 即拒(零容差) |
| ②竞争假设无区分性判据 | `scripts/glm_output_validator.py:492`(两两配对四元组全同→「仅措辞不同而无判据区分」拒)+`:439`(每假设≥1 可规格条件);用例 `test_no_distinctiveness_rejected`/`test_single_hypothesis_rejected` | 同上;D3 注入红 1 条 `negative-sensitivity/D3-distinctiveness-removed.log` | 过——判据四元组(metric,op,target,mode)可区分性为确定性判定 |
| ②缺席未承接 | absent_ack 逐项复述: `scripts/glm_output_validator.py:230`(缺指标即拒);limitations 四义务: `:266` 内(`未承接缺席指标`/`未承接Gate A降级影响面`/`缺未覆盖替代解释指针`/`未声明不可程序裁决条件`);用例 `test_absent_not_acked_rejected`/`test_absent_not_in_limitations_rejected`/`test_nonspec_without_declaration_rejected` 等 | 同上;D4 注入红 1 条 `negative-sensitivity/D4-absent-ack-removed.log` | 过——ack 与 limitations 双层承接各被拒形态直测 |
| ③阈值取值约束: 编造 target 被拒 | `scripts/glm_output_validator.py:429`(非三合法来源即拒);用例 `T3.test_fabricated_target_rejected`;D2 注入红 1 条佐证 | `negative-sensitivity/D2-target-legal-removed.log` | 过 |
| ③三合法来源通过 | 来源(i)证据包: `:154`;来源(ii)注册表: `:170`(registry_legal_targets,经 rp.active_registry_metrics 复用,字段族=REGISTRY_THRESHOLD_KEYS 点名两族);来源(iii)先验触发器: `:186`(prior_trigger_targets 注入面);用例 `test_source_i_evidence_value_allowed`/`test_source_ii_registry_allowed`/`test_source_iii_prior_trigger_allowed`+注册表提取 2 条(monkeypatch 合成注册表,真实 config 不入预期值) | `local-ci/test_p03_w2_glm_g2.log`;registry 引用=rp 复用调用(源码锁 T7 断言 `rp.active_registry_metrics` 在场) | 过——三来源逐一通过,编造即拒 |
| ④失败三径状态机 | `scripts/glm_output_validator.py:582`(run_conclusion_pipeline: 径1瞬态/解析/校验失败→反馈回注[`:617`/`:626`/`:634`]+线性退避计划表记录不实际休眠;径2降级受纳=gate DEGRADED 或缺席在场→ACCEPTED_DOWNGRADED;径3 `:561`(_absent_event: 重试耗尽 `:648`/`:612` 费用熔断即时/未知类 fail-closed));用例 T4 族 13 条(重试后受纳/纯受纳/降级受纳/耗尽登记/持续校验不过/熔断/未知类/上限截断/短序列耗尽/模式B缺席事件/模式B受纳/入口拒绝) | `local-ci/test_p03_w2_glm_g2.log`;trace 断言含 backoff 计划表(1.0/2.0)与反馈回注内容 | 过——三径全路径+缺席事件字段(task_id/origin_query_id/快照绑定/失败原因/task_status_advanced=False)逐一断言 |
| ⑤CI 零回归 | 无代码落点(工件=run ID);本地全量=59 文件(58 跑+1 合同排除)=57 绿+1 既有红(test_p4_fixes: 39 通过/4 失败,monthly_review 数据块,基线既有归因,与本包零导入关系);新增套件恰 1(test_p03_w2_glm_g2)=57+1=58 预期 | 本地逐套件日志 `local-ci/`(59 份 summary+日志);CI dispatch=操作者 CHECKPOINT,登记件将落 `rounds/027/GLM-WP-G2-CI-dispatch-evidence.md` | 本地过(新增套件 76 用例绿+零回归);CI 侧=NOT VERIFIED(待操作者 dispatch,执行Agent 禁自行触发) |

辅助登记(非要点,如实): T0 fixture 自检 2 条(合成输入经 gia.validate_input 回读=G1 合法契约,复用非复制);T5 数值抽取豁免族直测 3 条;T6 echo 三方一致 4 条(含 gov.gia is gia 复用身份断言);T7 源码边界锁 1 条(零网络/零凭证/零文件读取/零原始档字样+复用导入标记);合计 76 用例(2+6+7+34+6+13+3+4+1)。

---

## §四 git 取证与自检(提交时回填;最终尖端以 ls-remote 为准)

- 开工时序: 2026-11-04T17:17:35Z(UTC)git status clean@main;分支 `dev/p03-w2-glm-g2` 自 f5dc79fc5b86f70e98b10753acfd9b45845e52ea 切出(§3 步骤3 实测 rev-parse=基线全值)。
- 设计在场核验(§3 步骤4 原样输出入证据包成员③): merge-base --is-ancestor 0c8de3c3…HEAD exit 0(收工复测同 exit 0,`git-forensics/06a-merge-base.txt`;设计支为基线祖先经 e67f710 并入,merge-base(基线,设计支)=设计支自身);设计六件 ls-tree 双侧 blob 逐一相同(GLM 三件 5cb643a1/c72d41a1/772ad4cd;E2E-B 三件 9306e68b/89de7de9/5e0eb558;收工复测 `git-forensics/06c-design-docs-blob-equality.txt` 全等值=PASS;另附依赖六件[设计文档+G1模块+四个被复用既有件]核验 `06b-design-blob-equality.txt`: glm_input_assembler 为 G1 交付物晚于设计支诞生@933ec66,断言改 blob(基线)==blob(HEAD)=True,其余五件三方等值)。
- 开发提交: 纯线性零 merge(基线..尖端 `--merges` 空,`git-forensics/03b-log-merges-empty.txt`;提交信息见 `03-log-range.txt`);reflog 无 reset/amend(`04-reflog.txt`);不 force push;不碰 main;除本分支外零分支创建。
- 交付文件双源一致性: git 尖端版 vs 工作树版交叉哈希见证据包成员②。
- LS-REMOTE 尖端+29 支对照: 见证据包成员③(原样输出;冻结 BRANCH-SET=29 支,唯一新增预期=dev/p03-w2-glm-g2)。实取: 远端恰 30 支=冻结 29+新增 dev/p03-w2-glm-g2(装配时刻尖端=467a74ecd252cf6d13cc643fb46daad3a9174190,`git-forensics/05-ls-remote-heads.txt`);终态尖端(含 DELIVERY 追加行提交后)以 zip 外 sidecar `08-sidecar/final-state.txt` 为准(固定点不可内含自身之后状态,G1 同款自指豁免)。
- data/ 零触碰锚定: 27 文件(24 daily+3 research)sha256 快照 `datapath-zero-touch-snapshot.txt`(锚定时刻 2026-11-04T17:5xZ;研究档案 03b4fd7d… 与 E2E-A Run2 登记值一致)。

---

## §五 提交前数值标注六项自检清单(合同 §5.3;双文档=本件+DELIVERY 全文扫描)

边界声明(第5项): 本文日期时刻=UTC(另注明除外);SHA 一律全值或合同冻结值;行号/结构编号(L222-226 等)=基线 f5dc79f 工作树实读;档键成分(gri-1.0/hs-1.0/RT-/QB-/HY- 前缀)=标识符非数据值。

| # | 数值 | 标注 |
|---|---|---|
| 1 | 交付文件 k=4 | [实取·来源: REPORT §0.2 清单=git ls-files(265 文件)对照零重合,4 路径均为本包新增] |
| 2 | git ls-files 基线计数 265 | [实取·来源: `git ls-files | wc -l` 开工实测 2026-11-04T17:2xZ] |
| 3 | 专项测试 76 用例(2+6+7+34+6+13+3+4+1) | [实取·来源: 本地运行 "Ran 76 tests ... OK"(local-ci/test_p03_w2_glm_g2.log)+unittest loader 分类计数复算] |
| 4 | 负向敏感性 D1红4/D2红1/D3红1/D4红1/回绿 exit=0 | [实取·来源: negative-sensitivity/*.log 四份注入+还原后 OK 输出] |
| 5 | 本地全量 59 文件=58 跑+1 排除=57 绿+1 既有红(test_p4_fixes「39通过/4失败」) | [实取·来源: local-ci/summary.txt(total=59 green=57 red=1 skipped=1)+test_p4_fixes.log 尾部] |
| 6 | CI 基线 57 套件/run 41873412615 | [实取·来源: 注入快照(合同冻结章 2026-11-05 02:1x HKT),非工作树实读] |
| 7 | data 27 文件(24 daily+3 research) | [实取·来源: datapath-zero-touch-snapshot.txt 计数 2026-11-04T17:5xZ] |
| 8 | MAX_RETRIES=3/SPEC_OPS 4 元/SPEC_MODES 2 元/BACKOFF_LINEAR_BASE=1.0 等 §二 登记参数 | [登记值·本包登记(§二);echo=常量=登记三方一致(T6 实测)] |
| 9 | 锚点值 2.93/4186.7/2.20/0.73/73.0/4161.7/3.7/4.5/4300/1000/30000/25 | [合成 fixture 字面量·非实取](E2E-A 登记窗终值语义的合成复用;注册表/触发器注入值全合成,不代表真实配置) |
| 10 | 基线 f5dc79fc…/设计支 0c8de3c3…/六件 blob 哈希 6 枚 | [实取·来源: ls-remote/merge-base/ls-tree 开工实测(§四+证据包成员③)] |
| 11 | DESIGN 引用行号(L82-161/L199/L222-226 等) | [实取·来源: 基线工作树 docs/P03_W2_GLM_DESIGN.md 实读(blob c72d41a1,与 0c8de3c3 侧等值)] |
| 12 | G1/既有模块引用行号(gia:293/55/64/45;rg:525-526/553;ae:77;rp:91;fe:210-238) | [实取·来源: 基线工作树实读 §一.1/§一.3 登记] |
| 13 | 开工时刻 2026-11-04T17:17:35Z | [实取·来源: date -u 开工实测] |

第3项复核: 逐个 [实取] 项已回工作树/命令输出复核一遍(2026-11-04T18:0xZ);未发现失实项;第6项为注入快照引用,已显式标注非工作树实读。本清单自身成件入证据包(成员①附带)。
