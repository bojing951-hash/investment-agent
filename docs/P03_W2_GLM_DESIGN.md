# P03-W2 GLM 研究结论层 架构设计(DESIGN)

> 包: R019 · IA-P03-W2-GLM-DESIGN(P0-3 第 2 包,docs-only 零代码)
> 基线: `f1fe593faa0f1754e6a6ab14c39f39fc0848550a`(`dev/p03-e2eb-design` 尖端)
> 设计分支: `dev/p03-w2-glm-design`(自基线切出)
> 事实依据: `docs/P03_W2_GLM_INVENTORY.md`(下称 INVENTORY;行级引用以该 checkout 实码为准)
> 状态: 架构设计定稿候选;§七验收要点为**草案**(正式 AC 由主 Agent 后续轮拟定,本包不冻结)

**数值标注约定(全文适用,二选一)**: **[实取]**=读自本 checkout 真实文件或实测命令所得(随注 file:line 或命令+日期);**[示意·非实取]**=候选值/设计假设示例,显式标注。**注入基线**=本轮执行提示词注入的摘要(非工作树实读),一律随注。schema 示例中的 ID 字符串(如 `HY-20261102-001`)为标识符非数据值。设计规则中的数量要求(如「至少两个」)为合同/本设计的规范性要求,非对仓库事实的计数陈述。

---

## §一 目标与边界

**本层目标**: 在 v2 六层架构的 L5 位置建立**GLM 研究结论层**——以研究快照与装配产物为唯一数值输入,生成结构化的**竞争性解释**(对同一现象的多个相互竞争假设)与**可反驳结论**(每个假设附可程序核验的失效条件),经 Gate B 程序门禁裁决后进入研究状态保护(论点/观点/预测)与 append-only 研究档案。服务两种研究模式: 模式 A 自主研究(异常→任务→竞争性解释→可反驳结论→持续跟踪)与模式 B 用户自然语言研究(查询→接地计算→GLM 解释装配)。

**显式边界声明**:
1. **GLM 产出地位 = 研究辅助输入,非事实源**。事实唯一来源=研究快照/标准化产物(fact_engine 口径);GLM 的一切数值主张必须溯源到输入证据包中的快照事实,输出校验器对无法溯源的数值一律拒收(§三(b))。此边界有既有实现先例: 现行周报链中 GLM 状态迁移提议须经程序门禁裁决方可落盘,不满足即降级为提案留档(INVENTORY §一面③ B5/B6/B10)[实取: report_generator.py L1163-1167, 2026-11-02]。
2. **禁止事项**: 本层不产出交易信号、仓位建议、收益承诺;不直接写任何长期研究状态(一切状态变更走 Gate B 门禁提案);不作为数据源(缺席指标不得由 GLM 补值)。
3. **执行段零调用**: 本包为设计(docs-only);设计对象≠设计手段,调用面以字段表/机制描述交付,本轮零 GLM/LLM API 调用、零凭证读取、零付费操作(合同 AC-07(a))。

**In-scope**: 输入契约/调用面/输出契约三面架构;竞争性解释生成机制;可反驳条件推导规则与 Gate B/任务档案对接;模式 A/B 接入差异;实现包拆解。
**Out-of-scope**: GLM Prompt 终稿与真实调优、E2E-A/E2E-B 实现、模型选型/费用/凭证终局裁断(均为 DP 或后续包)、任何代码改动。

---

## §二 盘点引用与决策点

### 2.1 盘点引用(全部指向 INVENTORY,行级可核)

- GLM 报告层现状(真实调用链在场/结论层结构化能力缺席): INVENTORY §一面①(G1-G6)
- 装配层输出面与喂给报告层现行接口: INVENTORY §一面②(A1-A7)
- Gate B 论点/观点/预测状态保护实现面: INVENTORY §一面③(B1-B10)
- 快照读取面与禁直读现行约束面: INVENTORY §一面④(S1-S5)
- E2E-B 设计三件与模式 B 对接基线: INVENTORY §一面⑤
- E2E-A 任务 schema 注入抄录与时序解耦论证: INVENTORY §二 2.1(注入基线 · E2E-A 未执行)
- P1 设计跨分支登记: INVENTORY §二 2.2(`dev/p1-design`@`049ec978523dec659ba47f140bf41669604de24f`)
- 凭证与配额现状(不在场/仅环境变量机制): INVENTORY §三
- GLM 结论层缺口 GG-01~GG-07: INVENTORY §四

### 2.2 登记型决策点(DP;每个含四要素: 名/候选/推荐+理由/生效条件;不预设终局)

| # | 决策点名 | 候选选项 | 推荐+理由 | 生效条件 |
|---|---|---|---|---|
| DP-1 | 模型选型 | (a)`glm-5.3`(现行周报链实值[实取: env_config.py L29, 2026-11-02]) (b)智谱其他型号 (c)其他 OpenAI 兼容通道模型 | (a) 起步——与现行调用链同通道(结构化输出风险低,流式/reasoning 经验已踩坑备案于 `_call_glm` 注释[实取: report_generator.py L577-582, 2026-11-02]);结构化输出由校验器兜底,不依赖模型自觉 | 用户确认模型与通道;WP-G4(§七)启动前 |
| DP-2 | 温度与采样参数 | 温度候选 0.1/0.2/0.3[示意·非实取];`reasoning_effort` 候选 low/medium[示意·非实取];现行周报实值 temperature=0.3+reasoning_effort=low+max_tokens=32000[实取: report_generator.py L574/L593-594, 2026-11-02] | 结论层建议低温档(候选 0.1-0.2[示意·非实取])——结构化假设生成重一致性低于发散性,竞争性由机制保证(§四)而非靠采样温度 | 用户或后续实现包确认;WP-G4 首次真实调用前冻结初值 |
| DP-3 | 费用上限与调用频率 | 单次 token 预算上限/日-月度调用次数上限/超限熔断策略(候选值均[示意·非实取]) | 登记机制而非数值: 每次调用记录用量,超限→熔断并按缺席登记路径处理(§三(b)三径),不静默重试放大费用 | 用户批准费用额度后生效;WP-G4 PENDING 项 |
| DP-4 | 凭证来源 | (a)环境变量 `GLM_API_KEY`(现行机制[实取: env_config.py L14-26, 2026-11-02]) (b)密钥管理工具 (c)废除 `_load_glm_key` 的本机 `~/.claude/settings.json` 回退读取路径(INVENTORY §三登记项) | (a)+(c)——环境变量为唯一生产来源(不落盘先例已立[实取: env_config.py L3 注释, 2026-11-02]);本机回退路径语义含混(智谱 key 与 ANTHROPIC_API_KEY 字段名对应关系属部署约定),建议实现包废除或显式改名,消除隐性依赖 | 用户批准;WP-G4 接线前完成(需用户批准/PENDING) |

(决策点数=四个,与合同 AC-07(b) 指定面一一对应: 模型选型/温度与采样/费用上限/凭证来源;每包涉凭证/费用处在 §七显式 PENDING。)

---

## §三 GLM 报告层架构(三面)

### (a) 输入契约(GLM 输入数据结构,逐字段: 字段名+类型+语义)

输入装配器(唯一写者,WP-G1 落地)产出 `GLMResearchInput`,字段级 schema:

| 字段名 | 类型 | 语义 |
|---|---|---|
| `contract_version` | string | 输入契约版本号(标识符,如 `gri-1.0`;非数据值) |
| `mode` | string | `"A"`(自主研究任务)/`"B"`(自然语言查询解释装配) |
| `snapshot_binding` | object | 快照绑定: `{snapshot_id, snapshot_digest, gate_a, research_as_of}`——值=经 R1 选择+R3 门禁放行的权威快照(select_snapshot/gate_allows_formal_research[实取: research_provenance.py L1243/L1183, 2026-11-02]);digest 为内容级绑定(R5 同款[实取: research_provenance.py L1297, 2026-11-02]) |
| `task_ref` | object \| null | 模式 A: `{task_id, phenomenon, indicators[], window{start,end}, detection, history_tail[]}`——字段名与 E2E-A 任务 schema 最低字段集一一对应(INVENTORY §二 2.1 注入抄录;E2E-B 同款 ID 格式 `RT-YYYYMMDD-NNN`[实取: P03_E2EB_DESIGN.md L183, 2026-11-02]);模式 B 为 null |
| `query_ref` | object \| null | 模式 B: `{query_id, question_text, as_of, metric_bindings_digest, derived_ops_digest}`——来自 E2E-B StructuredResearchQuery IR 的引用摘要(不作数值载体,数值在 evidence_pack)[实取: P03_E2EB_DESIGN.md §三(a) L55-107, 2026-11-02];模式 A 为 null |
| `evidence_pack` | object | 结构化证据包(唯一数值载体): `facts[]`(每项 `{metric_id, fact_id, value, unit, observation_date, quality_status, derived}`——字段与快照事实/make_fact 产物同构[实取: fact_engine.py L210-214, 2026-11-02]);`scorecard_summary`(当日评分卡摘要或 DEGRADED/缺失状态);`correlation_ref`(相关性产物文件标识+滞后天数);`news_index_ref`(经来源认证的新闻引用索引标识,沿 news_provenance 机制[实取: report_generator.py L305-345, 2026-11-02]) |
| `absent_registry` | list | 缺席登记: 每项 `{metric_id/指称, level, reason}`,level 取 E2E-B 四级缺席枚举(ABSENT_REGISTRY/ABSENT_SOURCE/ABSENT_DATA/ABSENT_WINDOW)[实取: P03_E2EB_DESIGN.md L118-129, 2026-11-02]——**数据不足不填 0 的输入侧落地**: 缺席如实进输入,GLM 须在输出 limitations 中承接 |
| `prior_knowledge` | object | 研究先验: `theses_block`(论点库渲染,沿现行 load_theses 文本形态[实取: report_generator.py L79-124, 2026-11-02])、`views_block`(观点块,沿 render_views_block[实取: allocation_engine.py L1035, 2026-11-02])、`prior_conclusions[]`(同 task_id/query 关联的历史结论记录索引) |
| `prompt_contract` | object | 输出纪律声明(随输入下发): `{language, output_schema_version, counter_evidence_required: true, min_competing_hypotheses: 2, numeric_grounding_required: true}`——`min_competing_hypotheses: 2` 为合同级设计规则(§四),枚举值属规则参数非仓库统计 |

**数据来源限定与「禁直读原始采集档」的输入侧落地机制**(明示):
1. **装配器是唯一写者,读取面封闭**: 输入装配器只经 S1-S5 机制取数(R1 快照选择+R3 门禁放行+装配产物 meta 绑定核验),复用 `verify_research_inputs` 的「meta 声明+内容摘要重算+确定性重建比对」三重核验模式[实取: report_generator.py L612-737, 2026-11-02];装配器代码中不存在对 `data/daily/{channel}_*.json` 原始采集档的任何读取路径。
2. **披露与读取分离**: `evidence_pack.facts[].source_file` 类信息仅作披露字符串从快照事实透传(E2E-B D1 同款纪律[实取: P03_E2EB_DESIGN.md L41+L171, 2026-11-02]),不构成 GLM 或下游的读取通道。
3. **负向测试固化**(WP-G1 验收要点): 测试断言输入装配产物中不存在绕开快照的原始档路径引用(除披露槽位),并断言 Gate A FAIL 时装配器拒绝产出正式输入(沿数据装配器拒绝语义[实取: data_assembler.py L323-329, 2026-11-02])。
4. **数值零旁路**: 输入中一切数值均可溯源至 `snapshot_id+fact_id`;装配器不做任何算术(派生值一律取快照事实的 derived 字段或装配产物既有计算,沿「数值表全部程序确定性生成」纪律[实取: data_assembler.py L19, 2026-11-02])。

### (b) 调用面(结构化输出格式+失败处置三径+参数=DP)

**调用形态**: 沿用现行单一调用实现 `_call_glm`(OpenAI 兼容+流式;INVENTORY §一面① G1),结论层调用=同一函数族的新调用点,不另建通道;月报/季报复用先例证明该函数可多消费方共享[实取: monthly_review.py L342/L351, 2026-11-02]。

**结构化输出格式**: 要求 GLM 返回**单一 JSON 对象**(HypothesisSet,§三(c) schema),外层可包裹于 HTML 注释块以沿现行「机器状态块与散文隔离」纪律[实取: data_validator.py 文件头注释/Gate B 描述, ARCHITECTURE_V2.md L52-53, 2026-11-02];解析器容忍围栏/注释包裹,但不容忍字段缺失(校验失败走三径)。

**失败处置三径**(与「数据不足不填 0」口径一致,逐径定义):
1. **重试**(瞬态失败: 网络/风控/流式中断/JSON 解析失败)——重试上限候选值 3 次+线性退避[示意·非实取](现行周报链实值 3 次/间隔递增[实取: report_generator.py L553/L562-568, 2026-11-02],作为基线候选);重试时把解析错误回注 prompt 修正(如「counter_evidence 缺失」),仍失败→降级径 2。
2. **降级**(部分缺席/质量降级继续产出): Gate A=DEGRADED 时输入已附降级披露(INVENTORY §一面② A2 同款[实取: data_assembler.py L164-174, 2026-11-02]),输出**必须**在 limitations 中逐项承接降级与 absent_registry,涉及缺席指标的假设降置信;任何字段不得以 0 或编造值填充缺席。
3. **缺席登记**(结构性失败: 连续重试失败/校验不过/费用熔断): 本轮**无 GLM 结论**——不部分产出、不静默跳过;落一条缺席事件记录(含 task_id/query_id、快照绑定、失败原因),任务状态不因此推进;与 E2E-B「回答文本对缺席项显式声明无数据」同口径[实取: P03_E2EB_DESIGN.md L129, 2026-11-02]。

**参数=登记型决策点**: 温度/采样/reasoning 档/max_tokens/重试策略初值全部落 DP-2(候选值[示意·非实取]),不预设实值;现行周报链参数仅作候选参考[实取: report_generator.py L574/L593-594, 2026-11-02]。

### (c) 输出契约(GLM 产出物字段级 schema;七个必备字段)

`HypothesisSet`(模式 A 全量;模式 B 裁剪规则见§六):

| 字段名 | 类型 | 语义 |
|---|---|---|
| `hypothesis_id` | string | 假设标识符,格式 `HY-YYYYMMDD-NNN`(同日序列;标识符非数据值) |
| `statement` | string | 假设陈述: 对 phenomenon 的一条解释性主张(机制+方向+涉及指标),须可被证据支持或反驳 |
| `supporting_evidence` | list | 支持证据引用: 每项 `{fact_id, metric_id, direction_note}`——**只允许引用输入 evidence_pack 中在场的事实**(输出校验器核对 fact_id 在输入中在场且数值未被改写) |
| `counter_evidence` | list | 反方证据引用: 结构同上,指向对**本假设不利**的输入事实;机制层强制条款见§四 |
| `falsifiable_conditions` | list | 可反驳条件: 每项 `{cond_text, spec}`——spec 为可程序核验规格(推导规则见§五①;不可规格化的条件须在 limitations 声明「不可程序裁决」) |
| `confidence` | string | 置信标注(**登记定义**): 三档枚举 `high`/`medium`/`low`——`high`=支持与反方证据均已装配、无未解释冲突、可反驳条件全部可程序核验;`medium`=存在已解释反证或部分条件不可程序核验;`low`=证据单侧/缺席相关指标/仅机制推演。**口径声明**: 此为 GLM 自评的**辅助标注**,不进入任何门禁判定,与程序星级核验(STAR_RULES[实取: allocation_engine.py L130-136, 2026-11-02])相互独立、不可互换 |
| `limitations` | list | 局限声明: 至少承接 ①输入 absent_registry 全部条目 ②Gate A 降级影响面 ③本假设未覆盖的替代解释指针(指向竞争假设) ④不可程序核验的条件清单 |

JSON schema 骨架(设计层表述,实现包落地为可执行 schema):

```json
{"hypotheses": [{"hypothesis_id": "HY-…-001", "statement": "…",
  "supporting_evidence": [{"fact_id": "UST_10Y@2026-10-29", "metric_id": "UST_10Y", "direction_note": "…"}],
  "counter_evidence": [{"fact_id": "…", "metric_id": "…", "direction_note": "…"}],
  "falsifiable_conditions": [{"cond_text": "…", "spec": {"metric": "…", "op": ">=", "target": null, "mode": "expiry", "window": "…"}}],
  "confidence": "medium", "limitations": ["…"]}],
 "phenomenon_echo": "…(任务/查询现象复述,防答非所问)",
 "absent_ack": ["…(逐项复述输入 absent_registry)"]}
```
(schema 中 ID/数值为标识符与占位示例[示意·非实取];`target` 在推导规则约束下取值,见§五①。)

---

## §四 竞争性解释机制

**(1) 生成路径(设计层面: Prompt/模板要素清单)**

模式 A 调用时,Prompt 结构强制包含以下要素(逐项为模板槽位,WP-G2 固化):

1. **现象复述槽**(必填): task_ref.phenomenon 原文+window+indicators——防答非所问(输出侧以 phenomenon_echo 回显校验)。
2. **机制族提示槽**(必填): 给出机制类别清单作为假设多样性提示——直接复用证据分级 v2 的机制类别(增长/通胀/利率与流动性/信用/避险与估值/供应与库存/资金流,实测 7 类[实取: allocation_engine.py L104, 2026-11-02]),要求假设至少覆盖两个不同机制族(设计规则)。
3. **竞争性强制槽**(必填): 明示要求产出**至少两个相互竞争假设**——竞争性判定标准(写入 prompt 与校验器双处): 假设间对同一指标组合给出**可区分的预测方向或机制路径**,或各自的可反驳条件中至少有一条判据能区分彼此(「区分性判据」);仅措辞不同而无判据区分=不构成竞争(校验器拒绝)。
4. **反方证据强制槽**(必填): 每个假设必须附 counter_evidence 非空引用——见下(3)。
5. **数值接地槽**(必填): 一切数值只能取自输入 evidence_pack,禁止推算新数值(派生引用只允许引用快照事实 derived 字段的既有值);输出校验器逐数值核对(§三(c))。
6. **缺席承接槽**(必填): absent_registry 逐项进入输出的 absent_ack 与相关假设 limitations。

**(2) 假设-证据映射表结构**(装配期由校验器构建,入研究档案):

| 列 | 类型 | 语义 |
|---|---|---|
| `hypothesis_id` | string | 假设标识 |
| `fact_id` / `metric_id` | string | 证据指针(快照事实级) |
| `direction` | enum | `support` / `counter` / `neutral`(对**该假设**的方向) |
| `quality_status` | enum | 事实质量(PASS/DEGRADED/WARN/FAIL,自快照事实透传[实取: fact_engine.py make_fact 产物字段, INVENTORY §一面④, 2026-11-02]) |
| `snapshot_id`+`snapshot_digest` | string | 内容级绑定(E2E-B §4.1 同款约定[实取: P03_E2EB_DESIGN.md L182, 2026-11-02]) |

**(3) 反方证据强制条款**(机制层面安排,非结果承诺):

- **机制一·Prompt 结构强制**: 模板槽位(1)之 4——counter_evidence 为 schema 必填数组;空数组→结构校验失败→失败三径(重试修正→仍失败→缺席登记),**不存在无反方证据的合法输出**。
- **机制二·输入侧双窗装配**: 输入装配器对任务 indicators 集合,一律同时装配可双向解读的窗口事实(week/MTD/YTD 等既有 derived 窗口[实取: fact_engine.py L81-174, 2026-11-02]),不预筛「顺向」证据——反方证据的**检索面**在机制上恒在场(GLM 是否引用由输出校验兜底)。
- **机制三·区分性反证提示**: prompt 明示「若证据与假设相悖,必须列为 counter_evidence 而非省略或重新解释为支持」;未解释反证在置信口径上压档(§三(c) confidence 定义)。
- 条款落点为**机制设计**(槽位/装配/校验),不承诺「GLM 必产出高质量反证」——产出质量缺陷由校验器与后续审计承接,机制缺席才是设计缺陷(合同§十 8 同款语义)。

---

## §五 可反驳结论与任务对接

**(1) `falsifiable_conditions` 推导规则**(从假设陈述到可反驳条件,可操作四步):

1. **主张变量化**: 从 statement 提取可观测主张——映射为输入在场的 metric_id(不在场指标→该条件不可推导,转 limitations 声明;不得引入 absent_registry 之外的指标)。
2. **阈值取值约束**: 条件阈值 `target` 只允许三个来源之一——(i)输入证据包中**在场数值**(某事实的 value/derived 窗口值);(ii)注册表既有校验阈值(`validation.range`/`max_week_pct_move` 等字段族[实取: config/metric_registry.json 条目字段 schema(SPX 首条 L28-54), 2026-11-02]);(iii)先验知识中论点/观点既有触发器阈值(thesis.json quant_triggers/allocation_views.json triggers,thesis.json 实测 9 论点中 5 个带 quant_triggers[实取: config/thesis.json 实测, 2026-11-02])。三个来源之外的数值=编造,校验器拒绝。
3. **条件规格化**: 每条件写成可程序核验 spec `{metric, op, target, mode, window}`——op/mode 枚举与现行预测规格对齐(`pred_metric/pred_op/pred_target/pred_mode` 及 touch/expiry 语义[实取: report_generator.py L525-526, 2026-11-02]);窗口默认与 task_ref.window 一致。
4. **区分性检查**: 至少一条条件在竞争假设间产生**不同裁决结果**(区分性判据,§四(1)之 3);全部条件对两个假设裁决结果恒同=竞争性不足,校验器拒绝重生成。

不可规格化的条件(如制度变化类叙述): 允许存在但必须显式列于 limitations「不可程序裁决」清单——如实区分可核验与不可核验,不伪装可核验。

**(2) Gate B 状态保护对本层产出的应用**(论点/观点/预测三态如何覆盖 GLM 产出):

- **总原则**: GLM 假设**永不直接写状态**;一切落盘走既有程序门禁,模型判断不满足门禁→提案留档(现行先例[实取: report_generator.py L1163-1167, 2026-11-02])。
- **论点(thesis,四态: 进行中/待观察/已验证/已失效)**: 假设升级为论点候选须过终态门禁语义——进入已验证/已失效须触发器引擎核验已触发或至少两个新增独立支持证据;确信度上调不得超过程序星级(现行门禁[实取: report_generator.py L1065-1067/L1177-1188, 2026-11-02]);假设级 confidence 不参与该判定。
- **观点(view,四档评级+星级门禁)**: 假设不得直接提议评级变更;评级变更门禁=同向触发器已触发或至少两个通过程序验证的新增证据(`MIN_EVIDENCE_FOR_RATING_CHANGE=2`[实取: allocation_engine.py L139, 2026-11-02])。
- **预测(prediction,五态: not_yet_triggered/observing/hit/miss/inconclusive[实取: allocation_engine.py L73, 2026-11-02])**: 假设的 falsifiable_conditions 中可规格化条件→预测候选(带完整 spec 者到期由程序按观察记录自动裁决[实取: report_generator.py L526, 2026-11-02]);终态不可重开、引擎裁决优先于 GLM 附证据裁决(现行语义[实取: allocation_engine.py 文件头 L8-10/L45-46, 2026-11-02])。
- **数值校验前置**: 本层输出文本进入任何回写前,先过 Gate B 数值校验链(B1-B4,INVENTORY §一面③)——结论中数值与锚点不符→FAIL→阻断回写(`apply_status_updates` FAIL 语义[实取: report_generator.py L1310-1324, 2026-11-02])。

**(3) append-only 衔接**(结论入研究档案的方式,与 E2E-A `history` 字段追加式一致):

- 每轮结论产出(含被门禁拒绝的提案)追加一条结论记录到共享研究档案(E2E-B §4.1 档案载体约定[实取: P03_E2EB_DESIGN.md L185, 2026-11-02]): 记录含 `hypothesis_id`、`task_id`/`origin_query_id`、`snapshot_id`+`snapshot_digest`、输出全文摘要、门禁裁决结果;写入后不可改不可删(append-only,E2E-A `history` 同语义)。
- 同 task_id 重放=新版本追加或幂等跳过(二选一由实现包登记;E2E-A 注入摘要同款规则[注入基线])。
- 被拒提案不删除、进 proposals 留档(沿 `_record_proposal` 模式[实取: allocation_engine.py L1170, 2026-11-02])。

**(4) 与 E2E-A 任务 schema 的字段映射表**(本层产出字段 ↔ 任务字段;E2E-A schema=注入基线,INVENTORY §二 2.1):

| 本层产出字段 | E2E-A 任务字段 | 映射语义 |
|---|---|---|
| `task_ref.task_id` | `task_id` | 回写外键(标识符透传) |
| `task_ref` 其余字段 | `phenomenon`/`indicators`/`window`/`detection` | 只读回显(echo),不回写——防参数漂移(anomaly_detector echo 三方一致纪律同款[注入基线]) |
| `statement` | `history`(追加记录文本) | 假设陈述作为结论记录追加进任务历史 |
| `supporting_evidence` / `counter_evidence` | `evidence`(证据引用: 数据接入点/快照或标准化产物标识/计算结果指针/数据质量状态) | 证据引用方向化挂载;快照标识=fact_id/snapshot_id,数据质量状态=quality_status 透传——与该字段的四个子语义逐一兼容 |
| `falsifiable_conditions`(可规格化子集) | `falsifiable_conditions`(非空) | 假设级条件并入任务级条件集(任务级非空约束由首个升级的假设满足) |
| `falsifiable_conditions`.spec | (无对应最低字段;预测候选落 allocation_views 侧 predictions) | 条件规格→预测候选,经预测门禁独立落档 |
| `confidence` / `limitations` | `history`(追加记录属性) | 辅助标注随结论记录入档,不参与门禁 |
| `hypothesis_id` | (无对应最低字段;「可增不可减」条款允许实现期增设) | 结论记录标识;实现包可增设 `conclusions` 子结构承接(登记型扩展) |
| 任务状态推进(pending→active→concluded→tracking) | `status` + `history` | 本层证据装配完成=任务 active 的组成部分(E2E-A 实现至 active=证据装配完毕[注入基线]);反驳条件触发→concluded/tracking 的**提案**(经门禁,不直接改状态) |

---

## §六 模式 A/B 接入差异(逐点对照+共享档案衔接)

| 维度 | 模式 A(自主研究) | 模式 B(自然语言研究) |
|---|---|---|
| 触发源 | anomaly_detector 异常事件→research_task_manager 建 `RT-*` 任务[注入基线] | 用户自然语言问题→`QB-*` 查询 IR[实取: P03_E2EB_DESIGN.md L57/L183, 2026-11-02] |
| 输入契约主体 | `task_ref` 在场+任务档案先验(prior_conclusions 承接往轮结论) | `query_ref` 在场+接地计算结果(evidence_pack 取查询执行器产出的绑定事实) |
| 输出契约 | 全量 HypothesisSet(七字段) | 裁剪版: 解释装配(phenomenon_echo+grounded 解释+absent_ack);**数值不得新增**——回答中的数值只能是查询执行器已接地的值(接地强制规则沿 E2E-B §三(b),无源数值 fail-closed[实取: P03_E2EB_DESIGN.md L111-116, 2026-11-02]) |
| `falsifiable_conditions` | 强制(任务级非空,§五(1)推导) | 默认不带(查询记录无预测语义,E2E-B §四要素五分歧先例[实取: P03_E2EB_DESIGN.md L175, 2026-11-02]);用户显式升级为研究任务(`promoted_to_task_id`)后承接模式 A 全义务 |
| 竞争性假设 | 强制(§四机制全量) | 可选轻量(解释候选可给「替代解释」而非完整竞争假设集;升级为任务时补全) |
| 状态落档 | 经 Gate B 三态门禁提案→论点/观点/预测(§五(2)) | 查询历史 append-only[实取: P03_E2EB_DESIGN.md L47/L176, 2026-11-02];不触发状态回写,除非升级 |
| 失败三径 | 同§三(b)(三径统一,两模式不另设) | 同左 |

**共享档案衔接(快照 ID/任务 ID 引用约定)**:
1. **快照引用**: 两模式一切结论/查询/任务记录引用快照必须用完整 `snapshot_id`+`snapshot_digest` 内容级绑定(E2E-B §4.1 约定原文承接[实取: P03_E2EB_DESIGN.md L182, 2026-11-02])。
2. **ID 族与交叉引用**: `RT-YYYYMMDD-NNN`(模式 A 任务)/`QB-YYYYMMDD-NNN`(模式 B 查询)/`HY-YYYYMMDD-NNN`(本层假设;同日序列独立计数);交叉引用字段沿 E2E-B 约定 `origin_query_id`/`promoted_to_task_id`[实取: P03_E2EB_DESIGN.md L184, 2026-11-02],本层新增: 结论记录必携 `task_id` 或 `origin_query_id` 之一(锚定产生语境),append-only 写入后不可改。
3. **共享可信事实**: 两模式 GLM 输入的数值面同源——同一权威快照+装配产物(§三(a) 唯一数值载体),模式 B 的接地计算结果即快照事实的查询视图;不存在第二事实入口。

---

## §七 实现包拆解(验收要点=草案;正式 AC 由主 Agent 后续轮拟定)

> 共同红线(每包验收必查): 禁 LIVE 部署/禁 launchd 改动/禁交易与收益承诺/新模块走快照+门禁禁直读原始档;涉 GLM 真实调用的包另须 DP 决议齐备。

**WP-G1 结论层输入装配器**
- 目标: 落地§三(a) `GLMResearchInput` 装配(模式 A/B 双形态)+缺席登记+禁直读机制。
- 范围: 新增装配器模块;不改 fact_engine/snapshot_builder/data_assembler 既有签名。
- 依赖: 无硬依赖(快照读取面 R1/R3 既有);模式 B 形态依赖 E2E-B WP-B1/B2 的 IR 与执行器产物(未落地前该形态按缺席登记路径处理,不影响模式 A 形态交付)。
- 验收要点草案: ①输入契约字段级校验单测(工件: tests/test_p03_g1*.py) ②禁直读负向测试: 断言装配产物零原始档路径引用+Gate A FAIL 拒绝装配(工件: 测试文件) ③缺席登记测试: 构造缺席指标→absent_registry 如实登记非零值(工件: 测试文件) ④快照绑定核验: 篡改快照后装配拒绝(工件: 测试+R5 机制引用) ⑤CI 零回归(工件: GitHub Actions run ID)。

**WP-G2 结构化输出契约与校验器**
- 目标: 落地§三(c) 七字段 schema+§四竞争性/反方证据/区分性校验+§三(b) 失败三径。
- 范围: 输出 schema 定义+校验器+假设-证据映射表构建;不含真实调用(以确定性样例驱动)。
- 依赖: WP-G1(输入契约)。
- 验收要点草案: ①schema 正向用例(工件: 测试文件) ②负向敏感性用例: counter_evidence 空/数值不在输入证据包/竞争假设无区分性判据/缺席未承接——各须被拒(工件: 测试文件) ③阈值取值约束测试: 编造 target 被拒,三合法来源通过(工件: 测试文件+registry 引用) ④失败三径状态机测试: 重试→降级→缺席登记全路径(工件: 测试文件) ⑤CI 零回归(工件: run ID)。

**WP-G3 可反驳条件推导与门禁对接+档案衔接**
- 目标: 落地§五(1)推导规则、(2)Gate B 三态提案路径、(3)append-only 结论记录与 ID 交叉引用。
- 范围: 条件推导校验+门禁提案适配层+共享档案结论集合;预测候选落 allocation_views 侧沿既有门禁。
- 依赖: WP-G2;任务字段映射以 E2E-A schema 字段集为契约(注入基线;E2E-A 未落地时以契约测试固化映射表,实现落地后按登记型修订承接)。
- 验收要点草案: ①推导规则四步用例(可规格化/不可规格化分流)(工件: 测试文件) ②门禁提案测试: 无触发器且新增证据不足→提案被拒+留档(与现行门禁同构断言)(工件: 测试文件+allocation_engine 机制引用) ③append-only 测试: 结论记录改写被拒+交叉引用字段校验(工件: 测试文件) ④E2E-A 字段映射契约测试(工件: 测试文件+注入摘要引用) ⑤CI 零回归(工件: run ID)。

**WP-G4 真实调用接线(需用户批准/PENDING)**
- 目标: 以 DP-1~DP-4 冻结值接线真实 GLM 调用,冒烟测试沿 test_glm_live 模式(门禁确定性与模型遵从性双测[实取: tests/test_glm_live.py L1-16, 2026-11-02])。
- 范围: 调用点接入+费用/用量记录+熔断;不含生产部署与 launchd。
- 依赖: WP-G1/G2/G3;**GLM 凭证与费用=用户保留事项——需用户批准/PENDING**(DP-3/DP-4 决议齐备前本包不得启动;零凭证状态下其余三包均可完整交付与验收)。
- 验收要点草案: ①真实调用冒烟: 结构化输出过校验器+数值接地核对(工件: 测试运行记录+凭证使用登记,默认跳过门控沿 RUN_GLM_LIVE 模式[实取: tests/test_glm_live.py L31-33, 2026-11-02]) ②费用熔断测试(工件: 测试文件) ③调用日志与用量记录落盘(工件: 日志文件) ④CI 零回归且真实调用用例默认跳过不破坏离线套件(工件: run ID)。

(包数=四 ≥ 二;GG-01~GG-07 全部有承接: GG-01→WP-G1,GG-02/03/06→WP-G2,GG-04/05→WP-G3,GG-07→DP-1~4+WP-G4;每包四要素齐备;每条验收要点含可核验工件;唯一涉凭证/费用依赖的 WP-G4 已显式 PENDING。)

---

## §八 红线遵守声明

1. **不交易、不管理真实仓位、不承诺收益**: 本层输出为研究解释与可反驳条件,§一显式禁止交易信号/仓位建议/收益承诺类产出;模式 B 的 out_of_scope 拦截沿 E2E-B 设计[实取: P03_E2EB_DESIGN.md L104/L248, 2026-11-02]。
2. **GLM 产出=研究辅助输入,非事实源**: 事实唯一来源=快照/标准化产物;§三(a) 输入侧禁直读四机制+§三(c) 输出侧数值接地校验双落地。
3. **新模块走快照+门禁,禁止绕开直读原始档**: 输入装配器唯一写者+读取面封闭(§三(a));一切状态变更经 Gate B 程序门禁(§五(2))。
4. **W4/W5 侧边验收工具不接入生产链**: 本层设计对象为主流水线 L5,不含 W4/W5 工具接线。
5. **执行段纪律**: 本包 docs-only 零代码;零 GLM/LLM API 调用、零凭证读取/使用、零付费操作、零数据配额消费;LIVE 路径与 launchd 零触碰;registry/data/daily/既有 docs 只读。

---

*设计依据事实见 INVENTORY;交付说明与逐 AC 自评见 `docs/P03_W2_GLM_DELIVERY.md`。本设计 docs-only,未改任何代码/测试/配置。*
