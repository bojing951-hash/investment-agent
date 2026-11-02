# P03-W2 GLM 研究结论层 盘点(INVENTORY)— L5/L6 现状

> 包: R019 · IA-P03-W2-GLM-DESIGN(P0-3 第 2 包,GLM 解释/竞争性假设/可反驳结论 · 架构设计,docs-only 零代码)
> 基线: `f1fe593faa0f1754e6a6ab14c39f39fc0848550a`(`dev/p03-e2eb-design` 尖端,E2E-B 设计定稿终态)
> 盘点分支: `dev/p03-w2-glm-design`(自基线切出)
> 盘点时点: 2026-11-02(UTC) · 全部行级引用以本 checkout 实码为准,实测方法逐处注明
> 用途: 为 GLM 研究结论层(L5 研究结论生成面)的架构设计提供**事实层依据**;缺口清单供 DESIGN §七承接

**数值标注约定(全文适用,二选一)**: **[实取]**=读自本 checkout 真实文件或于本 checkout 实测命令所得(随注 file:line 或命令+日期);**[示意·非实取]**=非实取示例/候选值,显式标注。**注入基线**=本轮执行提示词注入的摘要信息(非工作树实读),一律随注「注入基线」。本文无 [示意·非实取] 数值(如有候选值仅出现在文字描述中且不形似仓库统计)。

---

## §一 L5/L6 现状盘点(五面)

### 面① GLM 报告层现状(真实调用链在场;研究结论层结构化能力缺席)

**结论先行**: 基线上**存在真实外部 GLM 调用链**(周报/月报/季报生成,非模板占位);但本包设计对象——GLM **研究结论层**(竞争性假设/可反驳结论的结构化生成)**不在场**,现有调用为周报散文生成,输出契约中无 hypothesis/竞争假设/反方证据槽位的任何结构化实体。

在场入口(全部实读):

| # | 实体名 | 位置 | 行号区间 | 形态 |
|---|---|---|---|---|
| G1 | `_call_glm(system_prompt, user_prompt, max_tokens=32000, timeout=900)` | scripts/report_generator.py | L574-605 | 真实智谱 GLM 调用: OpenAI 兼容客户端(paas/v4)+流式+`reasoning_effort=low`(L594);`temperature=0.3`(L593)[实取: report_generator.py L574-605, 2026-11-02] |
| G2 | `generate_report(...)` | scripts/report_generator.py | L377-571 | 周报 prompt 装配+调用+重试: `max_attempts=3`(L553),失败间隔 `attempt*15` 秒(L562-568),返回<500 字符视为截断(L557-558)[实取: report_generator.py L553-571, 2026-11-02] |
| G3 | GLM 身份配置 `GLM_API_KEY/GLM_BASE_URL/GLM_MODEL` | env_config.py | L14-29 | `GLM_MODEL="glm-5.3"`(L29),`GLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4"`(L28);key 经环境变量+本机回退路径(见§三)[实取: env_config.py L28-29, 2026-11-02] |
| G4 | 月报/季报复用同一调用链 | scripts/monthly_review.py L342/L351;scripts/quarterly_outlook.py L228/L238 | — | `from report_generator import load_prompt, _call_glm`,单一调用实现三处消费[实取: 两文件 import/call 行, 2026-11-02] |
| G5 | 真实 GLM 冒烟测试 | tests/test_glm_live.py | L31-33, L85 | 默认跳过(`RUN_GLM_LIVE=1` 才运行,L31-33);真实调用+门禁确定性断言(评级变更/星级封顶/台账只含验证通过项,L95-150)[实取: tests/test_glm_live.py, 2026-11-02] |
| G6 | 提示词外置热加载 | scripts/report_generator.py L44-56;config/prompts/ | — | `load_prompt` 缺失即硬中断;config/prompts/ 下 4 个文件: system_prompt.md/style_constraints.md/monthly_review_prompt.md/quarterly_outlook_prompt.md[实取: report_generator.py L46-56 + ls config/prompts/, 2026-11-02] |

**输出契约现状(与本包设计对象的差距)**: 现行 GLM 输出=周报八节散文+三个机器状态块(THESIS_STATUS L496-507 / ALLOCATION_STATUS L509-526 / PREDICTION_STATUS L528-540,均 HTML 注释包裹供脚本解析)[实取: report_generator.py L493-540, 2026-11-02]。状态块字段(如 `{"id","status","confidence","note","evidence":[...]}`)是**论点/观点/预测**的状态迁移载体,**不含** hypothesis_id/statement/counter_evidence/falsifiable_conditions(任务级)/limitations 结构;「核心矛盾」节(L476-478)仅是 prompt 要求列举 2-3 个矛盾[实取: report_generator.py L476-478, 2026-11-02],无相互竞争假设的结构化生成与反方证据强制机制。研究结论层能力=**不在场**(如实登记,DESIGN §三-§五为其首个设计)。

### 面② 装配层输出面(评分/相关性/数据包→报告层的现行接口)

在场入口:

| # | 实体名 | 位置 | 行号区间 | 产出结构与喂给报告层的方式 |
|---|---|---|---|---|
| A1 | `load_snapshot(date_str=None)` | scripts/data_assembler.py | L37-44 | 经 R1(`rp.select_snapshot`)读取快照,不自动构建[实取: data_assembler.py L37-44, 2026-11-02] |
| A2 | `build_markdown(snapshot, ymd, ...)` | scripts/data_assembler.py | L123-306 | 快照→`data_pack_{ymd}.md`(GLM 唯一数值输入载体): 数据源状态/降级披露(L164-174)/全球市场/汇率与商品/利率与信用/宏观月频/中国市场/联邦基金期货/对账/相关性上下文/评分卡/新闻摘要各节[实取: data_assembler.py L123-306, 2026-11-02] |
| A3 | `scorecard_state(ymd, ...)` | scripts/data_assembler.py | L68-79 | 评分卡当日性判定;仅当日评分=本期有效研究(L73 注释),报告入口按 pack meta 拒绝非当日评分[实取: data_assembler.py L68-79 + report_generator.py L697-703, 2026-11-02] |
| A4 | 数据包 meta sidecar | scripts/data_assembler.py | L338-352 | `source=snapshot`+`snapshot_id/digest`+`pack_digest`+`scorecard_*` 绑定;报告侧 `verify_research_inputs` 逐项核验[实取: data_assembler.py L338-352, 2026-11-02] |
| A5 | 宏观体制评分卡 | scripts/macro_scorecard.py | M1 `DATA_INSUFFICIENT` L30;`load_snapshot` L39-50;体制映射/两周确认 L271-334(行号沿 E2E-B INVENTORY 层⑤登记)[实取: macro_scorecard.py 实读行号+E2E-B INVENTORY L135-144, 2026-11-02] | 评分卡 md 装入数据包(当日/历史参考两态,A2);`DATA_INSUFFICIENT`=数据不足不可判,不填 0 |
| A6 | 跨资产相关性 | scripts/correlation_calculator.py | `PAIRS` L28-46(实测 10 对,字典式定义,不含任何 USDJPY 配对);`compute_all` L83-106(序列缺失→missing 披露清单) | 相关性 md 作为研究上下文滞后挂入数据包(A2 L269-275)[实取: correlation_calculator.py L28-46 计数+E2E-B INVENTORY 层⑤, 2026-11-02] |
| A7 | 锚点与锚点 prompt | scripts/snapshot_builder.py `build_anchors` L121-231;scripts/data_validator.py `generate_anchor_prompt_block` L1020 | — | 锚点源自快照事实(兼容桥,snapshot_builder.py 文档串 L9-12);报告入口在数据包前拼接当日 `anchor_prompt_{ymd}.md`(report_generator.py L1393-1401)[实取: 两文件实读行号, 2026-11-02] |

**喂给报告层的现行接口形态**: GLM 输入=「锚点 prompt + 数据包 md + 框架 md + 论点文本块 + 上期报告摘要 + 技术面笔记 + 脱敏新闻 + 观点块渲染」的纯文本拼接(report_generator.py `generate_report` user_prompt 装配 L390-547 + `generate_weekly_report` 第 0-1.5 步 L1335-1401)[实取: report_generator.py L377-547 与 L1335-1401, 2026-11-02];数值面唯一权威=数据包(当日纪律: 缺当日包即失败不回退旧包,L183-213,尤其 L200-201)[实取: report_generator.py L183-213, 2026-11-02]。

### 面③ Gate B(论点/观点/预测状态保护实现面)

在场入口(全部实读):

| # | 实体名 | 位置 | 行号区间 | 保护语义 |
|---|---|---|---|---|
| B1 | `validate_report(report_path, anchors)` | scripts/data_validator.py | L755 起 | 报告数值全量核验(re.finditer 逐处,非首处即止;身份解析/前值拦截/bp 归一;不可核验→待复核)[实取: data_validator.py L755 起+文件头注释, 2026-11-02] |
| B2 | `classify_result(has_anchors, anchors_same_day, warnings, numeric_errors)` | scripts/data_validator.py | L378 起 | PASS/DEGRADED/FAIL 分级;FAIL=无锚点/非同日/数值类错误[实取: data_validator.py L378 起, 2026-11-02] |
| B3 | `validate_generated_report(md_path, ...)` | scripts/report_generator.py | L1243-1302 | 生成后同日锚点校验,结果落 logs/validation_*.log 并附注报告尾部[实取: report_generator.py L1243-1302, 2026-11-02] |
| B4 | `combine_gates(gate_a, gate_b)` | scripts/research_provenance.py | L1533 | Gate A×Gate B 合成最终质量(任一 FAIL→FAIL;无 FAIL 有 DEGRADED→DEGRADED)[实取: research_provenance.py L1533, 2026-11-02] |
| B5 | 论点状态回写 `update_thesis_status(...)` | scripts/report_generator.py | L985-1241 | 解析 THESIS_STATUS 块回写 thesis.json;终态门禁(→已失效/已验证 须触发器引擎核验已触发或≥2 项新增独立支持证据,L1137-1168)、终态退出门禁(L1070-1136)、确信度上调不得超过程序星级(L1177-1188)、history 追加式且每论点只留最近 12 条(L1216-1227)[实取: report_generator.py L985-1241, 2026-11-02] |
| B6 | 观点状态回写 `update_allocation_status(...)` | scripts/allocation_engine.py | L1199 起 | 评级变更门禁: 引擎核验已触发的同向触发器,或≥2 项通过程序验证的新增结构化证据(`MIN_EVIDENCE_FOR_RATING_CHANGE=2` L139);被拒提案入 proposals 留档(`_record_proposal` L1170)[实取: allocation_engine.py L1199/L139/L1170, 2026-11-02] |
| B7 | 证据分级 v2 程序核验 | scripts/allocation_engine.py | `verify_evidence_items` L364;`split_evidence_direction` L571;`star_level_from_evidence` L592;`STAR_RULES` L130-136;机制类别 `MECHANISM_CATEGORIES` L104(实测 7 类) | 证据逐项对照锚点验证;星级门槛 1★1 项/…/5★5 项且 3 类机制且 3 观察期;未解释重大反证封顶 3★(L137)[实取: allocation_engine.py L104/L130-139/L364/L571/L592, 2026-11-02] |
| B8 | 预测全生命周期 | scripts/allocation_engine.py | `record_observations` L726;`evaluate_predictions` L895;预测五态 L73;`daily_prediction_observer.py`(不调 GLM,文档串 L11) | 引擎客观裁决>GLM 附证据裁决;终态预测不可重开(文件头 P0-2,L8-10);expiry 只认结算日当日观测[实取: allocation_engine.py L73/L726/L895+daily_prediction_observer.py L1-38, 2026-11-02] |
| B9 | FAIL 阻断一切长期状态回写 | scripts/report_generator.py | `apply_status_updates` L1310-1324 | 校验分级 FAIL → 论点+观点两类回写均跳过[实取: report_generator.py L1310-1324, 2026-11-02] |
| B10 | 候选→发布事务 | scripts/report_generator.py | L1409-1519(候选保存 L909-921/校验 L1432/合成 L1440/发布 L1473-1510) | 报告先落候选文件,Gate B+状态记录成功后才原子发布;失败路径不触碰既有合格报告[实取: report_generator.py L909-921/L1409-1519, 2026-11-02] |

**GLM 产出受 Gate B 覆盖的现行机制**: GLM 的一切状态迁移提议(论点状态/观点评级/预测裁决)均以机器状态块形式输出、由 B5/B6/B8 的程序门禁裁决后落盘;模型判断不满足门禁→降级为提案留档(如 report_generator.py L1163-1167 `ae._record_proposal` 调用)[实取: report_generator.py L1163-1167, 2026-11-02]。这是「GLM 产出=研究辅助输入,非事实源」治理边界的**既有实现先例**,本包设计沿用该模式(DESIGN §五②)。

### 面④ 快照读取面(报告输入经快照/标准化层的现行机制)

在场入口:

| # | 实体名 | 位置 | 行号区间 | 机制 |
|---|---|---|---|---|
| S1 | `verify_research_inputs(ymd=None)` | scripts/report_generator.py | L612-737 | **调 GLM 之前**的前置核验: ①当日权威快照+Gate A∈{PASS,DEGRADED}(L639-648) ②数据包存在+meta 来源=snapshot+snapshot_id/digest/target_date 绑定+内容摘要重算+确定性重建比对(L650-703) ③锚点批次核验+数量≥20(L707-721) ④锚点 prompt 从已核验锚点确定性重建比对(L723-730);任一失败→不调 GLM、exit 2(L1355-1362)[实取: report_generator.py L612-737 与 L1355-1362, 2026-11-02] |
| S2 | `select_snapshot(ymd, daily_dir)` | scripts/research_provenance.py | L1243 起(R1) | 确定性版本选择: 同日多版取最高修订版;候选损坏/身份冲突→拒绝[实取: research_provenance.py L1243, 2026-11-02] |
| S3 | `gate_status` / `gate_allows_formal_research` | scripts/research_provenance.py | L1101 起 / L1183 起(R2/R3) | 下游复算 Gate A;PASS/DEGRADED 放行正式研究,FAIL/None 拒绝[实取: research_provenance.py L1101/L1183, 2026-11-02] |
| S4 | `digest_snapshot(snapshot)` | scripts/research_provenance.py | L1297 起(R5) | 快照内容指纹(sha256 前 16 位),包↔快照内容级绑定[实取: research_provenance.py L1297, 2026-11-02] |
| S5 | 快照构建不可变语义 | scripts/snapshot_builder.py | `build_snapshot` L236 起(S1)/`resolve_inputs` L47-101(S2) | 同日已存在→拒绝覆盖,`--allow-revision`→`_v2` 修订版留原因,原版保留(模块文档串 L14-15)[实取: snapshot_builder.py L1-19/L47-101/L236 起, 2026-11-02] |

**现行约束面(新模块禁直读原始采集档)**: 数据包数值面唯一权威=快照渲染产物(A2/S1);报告入口对数据包/锚点均做「meta 声明+实际内容摘要+确定性重建」三重核验(S1),改包内数字→拒;锚点为快照事实的兼容桥拍平(A7),非独立数据源。E2E-A 注入摘要的 `research_history_query`「禁直读 data/daily 原始采集档,必须经快照历史序列或 fact_engine 标准化产出」约束与该现行面同构[注入基线 · E2E-A 未执行]。v2 六层架构明文: 「新研究模块必须走快照+门禁,禁止绕开直读原始文件」[注入基线;工作树侧同义表述见 docs/ARCHITECTURE_V2.md L48-54[实取: ARCHITECTURE_V2.md L48-54, 2026-11-02]]。

### 面⑤ E2E-B 设计三件(docs/ 下 P03_E2EB 前缀,逐件在场核对)

`ls docs/` 实读取文件名(基线分支在场)与三件结构摘要[实取: ls docs/ +逐件通读, 2026-11-02]。
**表级覆盖声明**: 本表结构摘要中出现的计数/行号类数值(E1-E17、S1-S5、R1-R7、A1-A5、M1-M7、C1-C6、G-01~G-08、GAP-01~08、WP-B1~B5、D1-D7、81 指标、53/53、py3.9.6/3.11)全表[实取: 所述 P03_E2EB_* 三件对应登记(工作树在场文档逐处可核)+registry 实测, 2026-11-02]:

| 文件 | 行数 | 在场核对 | 结构摘要(设计角色) |
|---|---|---|---|
| docs/P03_E2EB_QUERY_SURFACE_INVENTORY.md | 184 行[实取: wc -l, 2026-11-02] | 在场 | **模式 B 查询面事实层盘点**: 五层查询入口全量行级登记(层① fact_engine E1-E17/层② 注册表 v2.0.0 实测 81 指标+日本侧零命中/层③ 快照构建 S1-S5+读取 R1-R7/层④ data/daily 四通道字段与时区/层⑤ 装配 A1-A5+评分 M1-M7+相关性 C1-C6)+已知缺口 G-01~G-08+跨分支工具登记 2 条——为 GLM 结论层提供模式 B 侧输入面的事实依据(本文§一多处以行级引用承接) |
| docs/P03_E2EB_DESIGN.md | 253 行[实取: wc -l, 2026-11-02] | 在场 | **模式 B 架构设计定稿**(七节): 目标边界/决策点 D1-D7/NL→查询映射(StructuredResearchQuery IR 字段级 schema+接地规则+四级缺席路径+美日 USDJPY 端到端走查)/E2E-A 八要素对齐+共享档案衔接(QB-/RT-/origin_query_id/snapshot_id+digest)/差距 GAP-01~08/工作包 WP-B1~B5/红线四条——GLM 结论层的模式 B 接入差异(DESIGN §六)以其 §三§四为对接基线 |
| docs/P03_E2EB_DELIVERY.md | 52 行[实取: wc -l, 2026-11-02] | 在场 | **E2E-B 交付说明**(五节): 交付清单/内容摘要/证据指针(CI 同构 53/53 全绿·情形 a)/偏离如实声明(本地 py3.9.6 vs CI 3.11 等)/后续建议——提供该包验收状态与证据链的索引 |

---

## §二 上游接口登记

### 2.1 E2E-A 任务 schema 最低字段集(注入基线 · E2E-A 未执行)

以下按本轮执行提示词注入的《E2E-A 接口注入摘要》(源自 R011 冻结草案 `IA-P03-W1-E2EA-AC-v1.0` §三,该包停泊未执行)**原文抄录**,标注: **注入基线 · E2E-A 未执行**(非工作树实读;若日后 E2E-A 实现与本摘要冲突,由登记型修订承接,不构成本包阻断):

> 三模块: `research_history_query`(历史查询,**禁直读 data/daily 原始采集档**,经快照历史序列或 fact_engine 标准化产出)/ `anomaly_detector`(背离检测;日志参数 echo=代码常量=报告登记值三者一致)/ `research_task_manager`(研究任务与档案);
> **任务 schema 最低字段集(可增不可减)**: `task_id`、`created_at`(UTC)、`phenomenon`(现象描述)、`status`、`indicators`(指标 ID 列表)、`window`(起止日期)、`detection`(规则 ID+冻结参数+触发统计)、`evidence`(证据引用: 数据接入点/快照或标准化产物标识/计算结果指针/**数据质量状态**)、`falsifiable_conditions`(可反驳条件,非空)、`history`(状态迁移记录,追加式);
> 状态机: pending→active→concluded→tracking(E2E-A 实现至 active=证据装配完毕);档案 `data/research/` **append-only**,同 task_id 重放=新版本追加或幂等跳过(规则登记二选一)。

**本设计与 E2E-A 实现时序解耦的理由**: 对接层以 **schema 字段集为契约**而非以实现为契约——①字段集条款「可增不可减」保证 E2E-A 落地时字段只会增不会减,本层按最低字段集建立的映射(DESIGN §五④)天然前向兼容;②本层产出物(假设记录)自带 `task_id`/`snapshot_id` 外键,不依赖 E2E-A 内部实现细节;③模式 B 侧已有同构先例(E2E-B DESIGN §四按注入摘要对齐并以登记型修订承接冲突,P03_E2EB_DESIGN.md L167-178[实取: P03_E2EB_DESIGN.md §四表, 2026-11-02]),本设计沿用该对齐模式。

### 2.2 P1 设计跨分支登记(不承担行级引用义务)

四经济体研究能力设计定稿于分支 `dev/p1-design`@`049ec978523dec659ba47f140bf41669604de24f`(R015+R017 整体 PASS 定稿;注入基线登记,不在本包基线分支内)。其四经济体(美/中/日/欧)指标覆盖缺口与候选源清单属数据线责任面;本设计仅在其「候选指标进入注册表」后自动受益(结论层输入以注册表+快照为准,不因经济体扩展而改契约)。沿 R015 合同 AC-01(c) 跨分支登记先例,不承担行级引用义务,禁编造其内容细节。

---

## §三 凭证与配额现状(只读实查)

- **仓库内凭证在场状态: 不在场(仅环境变量读取机制)**。env_config.py L3-8 注释明示「API Keys — 全部从环境变量读取,不落盘(开源版已移除原作者的真实 key)」;实现为 `os.environ.get("GLM_API_KEY", ...)` 等空默认读取(L9-11, L15)[实取: env_config.py L3-11, 2026-11-02]。
- **硬编码密钥模式扫描: 零命中**。对 scripts/ config/ tests/ .github/ docs/ 目录 grep `sk-[a-zA-Z0-9]{20,}` 模式,零命中[实取: grep 实测, 2026-11-02]。
- **本机回退读取路径(登记,非仓库内凭证)**: `_load_glm_key` 在环境变量缺席时尝试读 `~/.claude/settings.json` 的 `env.ANTHROPIC_API_KEY`(env_config.py L14-26)[实取: env_config.py L14-26, 2026-11-02]——这是对本机用户目录的**读取路径**(仓库外),本轮**零读取零使用**;该回退语义(智谱 key 与该字段名的对应关系)属部署约定,登记为设计期注意事项(DESIGN §二 DP-4 候选之一: 保留或废除该回退)。
- **未发现任何真实凭证**: 本轮实查范围内无可复制/移动/使用的真实 key;无需触发 AC-01(c) 的凭证处置条款。**建议 PENDING 项**(非凭证发现,属常规治理): 实现包接线前,凭证来源与费用额度需用户批准(DESIGN §二 DP-3/DP-4,§七 WP-G4 显式「需用户批准/PENDING」)。
- **配额现状**: 本轮零 GLM/LLM 调用、零数据配额消费(合同§零;自述声明互证)。

---

## §四 GLM 结论层缺口清单(供 DESIGN §七工作包承接)

| 编号 | 缺口 | 实测依据 | 承接包(DESIGN §七) |
|---|---|---|---|
| GG-01 | 无研究结论层输入装配器: 现行 GLM 输入=周报散文拼接(面① G2/A7),无任务上下文(task_ref)/缺席登记结构化输入 | 面① 面② | WP-G1 |
| GG-02 | 无结构化输出契约: 现行输出=散文+论点/观点/预测状态块,无 hypothesis_id/statement/counter_evidence/falsifiable_conditions(任务级)/limitations 字段 | 面① 输出契约现状 | WP-G2 |
| GG-03 | 无竞争性假设机制: prompt 仅要求列 2-3 个矛盾[实取: report_generator.py L477, 2026-11-02],无相互竞争假设结构化生成路径与反方证据强制条款 | 面① | WP-G2 |
| GG-04 | 无假设级可反驳条件推导规则: falsifiable 能力现存于论点 invalidation_rules(thesis.json 9 论点中 5 个带 quant_triggers[实取: config/thesis.json 实测, 2026-11-02])与预测 spec(report_generator.py L525-526),但均为人工/周报路径维护,无从 GLM 假设陈述推导的规则化路径 | 面③ B5/B8 | WP-G3 |
| GG-05 | 无 GLM 产出与 E2E-A 任务 schema 的字段映射/append-only 档案衔接(E2E-A 本身未执行,注入基线) | §2.1 | WP-G3 |
| GG-06 | 模式 B 侧 GLM 解释装配层缺席(E2E-B DESIGN §六 WP-B5 只覆盖接地渲染,GLM 解释装配为 out-of-scope 显式留待后续,P03_E2EB_DESIGN.md L21[实取: P03_E2EB_DESIGN.md L21, 2026-11-02]) | 面⑤ | WP-G1/WP-G2(模式 B 差异见 DESIGN §六) |
| GG-07 | 温度/模型/费用/凭证参数无登记型决策点(现行值散在代码: temperature=0.3/reasoning_effort=low/max_tokens=32000 均硬编码于 _call_glm 调用参数[实取: report_generator.py L574/L593-594, 2026-11-02],面① G1) | 面① | DP-1~DP-4(DESIGN §二) |

---

*本盘点为设计输入事实层;判断与方案见 `docs/P03_W2_GLM_DESIGN.md`;交付说明见 `docs/P03_W2_GLM_DELIVERY.md`。本文 docs-only,未改任何代码/测试/配置。*
