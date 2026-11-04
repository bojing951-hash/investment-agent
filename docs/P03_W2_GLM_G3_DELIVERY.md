# IA-P03-W2-GLM-WP-G3 交付说明(DELIVERY)

> 工作包: IA-P03-W2-GLM-WP-G3(WP-G3 可反驳条件推导与门禁对接+档案衔接)· 分支 `dev/p03-w2-glm-g3`
> 基线: 2f03be1fd77677b43d3afb7946af07c725625a2a(WP-G2 最终交付尖端;纯线性切出,无并入步)
> 证据包: `/tmp/p03-w2-glm-g3-evidence/IA-P03-W2-GLM-WP-G3-EVIDENCE.zip`(zip sha256 见 §二)
> 边界: 零真实 GLM/LLM 调用、零凭证、零付费、零网络出站(真实调用属 WP-G4,PENDING);零运行产物(依据见 REPORT §0.3)。

---

## §一 改动(交付清单,k=4,与 REPORT §0.2 登记一致)

| 文件 | 形态 | 摘要 |
|---|---|---|
| `scripts/glm_conclusion_integrator.py` | 新增(结论整合模块,703 行) | §五(1) 推导规则四步: `variableize_claim`(在场/缺席/注册未入输入三分类)→`legal_thresholds_for`(三来源逐源[证据包 per-metric 保序/注册表点名两族/先验触发器 target])→`derive_falsifiable_conditions`(规格化 spec 五键+窗口缺省=task 窗;无合法阈值如实分流不编造;步4 区分性 trace 登记 deferred-to-g2-validator 禁复制分叉)→`apply_derived_conditions`(四元组去重合入+non_spec→limitations);`extract_prior_trigger_targets`(G2 预留来源(iii) 结构化注入面);§五(2) Gate B 三态提案: `build_gate_b_proposal`(数值校验前置双层=gov.validate_output 零容差×rp.combine_gates B4→FAIL blocked)+`evaluate_gate_b`(五类提案与现行门禁同构[终态=invalidation/upgrade 触发器或≥MIN_EVIDENCE_FOR_RATING_CHANGE;确信度≤star_max;评级 suspend/resume 放宽 1,方向复用 ae._change_direction;预测候选 spec 完整性,初始 not_yet_triggered])+`record_rejected_proposal`(复用调用 ae._record_proposal 同向 21 天去重);§五(3) `build_conclusion_record`(CR-YYYYMMDD-NNN;交叉引用必携 task_id或origin_query_id;HY-/RT-/QB-/CR- 格式族校验;outcome∈G2 三结局透传;output_digest sha256 前 16;gate_b_verdicts 含被拒轮次)+`append_conclusion_record`(幂等跳过/新版本 __v{N} 追加原记录不动)+`mutate_conclusion_record`(恒 raise ArchiveImmutable);§五(4) `E2EA_FIELD_MAP` 9 行静态登记+`build_e2ea_projection`(task_id 透传/echo 只读回显/history 追加行/evidence 方向化挂载[direction 三值枚举完整承接= G2 留 G3]/可规格化子集并入/pred_* 预测候选/conclusions 子结构/状态推进=提案制/模式 B 裁剪);echo_params() 全参数回显 |
| `tests/test_p03_w2_glm_g3.py` | 新增(专项测试,857 行) | 61 用例: T0 fixture 自检 2+T1 推导规则 16+T2 门禁提案 19+T3 结论档案 10+T4 E2E-A 映射契约 12+T5 echo 1+T6 源码边界锁 1;全合成 fixture 唯一数据源(注册表/触发器 monkeypatch 注入合成集);预期值字面量硬编码;集成闭环=fixture 过 G2 真实管线(`run_conclusion_pipeline` 合成桩) |
| `docs/P03_W2_GLM_G3_REPORT.md` | 新增(执行报告) | §零 规格抄录(DESIGN L228-232 逐字)+白名单登记 k=4+零运行登记;§一 前置实读 file:line;§二 参数登记(先登记后运行);§三 逐要点映射;§四 git 取证;§五 数值标注自检 |
| `docs/P03_W2_GLM_G3_DELIVERY.md` | 新增(本件) | 五节+漂移维护策略专节+fixture→预期值映射 |

改动总量=纯新增 4 文件,零修改既有文件(diff --name-status 基线..尖端=恰 4 行 A,零 M/D,零第二类)。

## §二 证据

- **本地逐套件**: 60 份套件记录 `/tmp/p03-w2-glm-g3-evidence/09-local-ci/`(59 跑+1 合同排除 test_glm_live)=58 绿+1 既有红(test_p4_fixes: 39 通过/4 失败 monthly_review 数据块,基线既有归因[与 G1/G2 同款登记],与本包零导入关系——本包不 import monthly_review);新增套件恰 1(test_p03_w2_glm_g3,61 用例 OK)→ CI 预期 58+1=59 零回归(合同口径)。
- **负向敏感性**: 4 注入全红后回绿(日志 `07-negative-sensitivity/`,README+8 log): D1 常量复制分叉→T6 红 1/D2 append 原地改写→T3 红 1/D3 编造阈值→T1 红 2/D4 交叉引用校验移除→T3 红 1;每次还原后模块 sha256 逐字节一致=基线 `c3a61348…ed79`,零注入标记残留。
- **零触碰**: `data/` 全量 27 文件(24 daily+3 research)sha256 快照 `05-zero-touch/datapath-zero-touch-snapshot.txt`,与 G2 证据包基线快照 diff 逐字节一致(IDENTICAL-TO-G2-BASELINE);本包无真实运行面→零运行产物(REPORT §0.3 依据);LIVE 路径 grep(`R028|GLM-WP-G3|IA-P03-W2-GLM-WP-G3`)=零命中。
- **git 取证**: 原样输出于证据包成员③(name-status/rev-parse/log/reflog/ls-remote+设计在场核验输出[merge-base 可达+六件 blob 等值])。
- **CI**: 操作者 CHECKPOINT dispatch(执行Agent 禁自行触发);登记件将落 `rounds/028/GLM-WP-G3-CI-dispatch-evidence.md`(引擎侧,本包引用其路径)。
- **zip 整体 sha256**: 见证据包 SHA256SUMS 头注与 stdout 终述(本文件不预写,以装配后实测为准;自指豁免同 G1/G2 先例——zip 内任何文件不可内含 zip 自身哈希,实测值以封装后追加行落档,终态见 zip 外 `08-sidecar/final-state.txt`)。装配后实测追加登记(任务步骤12「落 DELIVERY 与自述」): `ad5fa7f201b55270d11dc5e9fd6147beeda877f075e0fedecbb522474fad0ce4`(98 成员/309545 字节)。自指豁免处理: zip 内 DELIVERY 副本(成员①②)=7f845d16 版无本行,固定点不可内含自身哈希,故实测值以封装后追加行落档;终态 SHA 与最终 ls-remote 见证据目录 `08-sidecar/final-state.txt`(zip 外)。

## §三 逐 AC 自评

| AC | 自评 | 指引 |
|---|---|---|
| AC-01 规格抄录与登记 | PASS(自评) | REPORT §0.1 逐字抄录+行号(DESIGN L228-232 实读);清单 k=4 逐条附依据(模块级范围=单模块四能力面的推导登记);结构约束核验(§0.2,基线 git ls-files 零重合);无命名偏差(DESIGN L232 工件名=泛称「测试文件」) |
| AC-02 逐要点映射 | PASS(本地)(自评) | REPORT §三 五要点全映射(①四步+双流 ②被拒+留档+同构 ③改写拒+交叉引用 ④9 行契约+三值枚举 ⑤本地预演+远端待 dispatch);参数登记=常量=echo(T5) |
| AC-03 测试与确定性 | PASS(自评) | 61 用例全绿;零网络/零新依赖/全合成 fixture/字面量硬编码;漂移维护策略专节(§五)+fixture→预期值映射(§六);GLM 调用面=本包不含(集成输入=本地合成 fixture 过 G2 管线合成桩,attempts 注入面沿 G2 桩纪律) |
| AC-04 引用真实性 | PASS(自评) | REPORT/DELIVERY file:line 逐条可寻(±3);设计六件=基线工作树实读(blob 等值已核,步骤5);G1/G2 交付件引用以其 REPORT §零登记清单为对照同源;注入摘要引用显式标注「注入摘要,非工作树实读」(REPORT §一.3) |
| AC-05 范围/分支/隔离 | PASS(自评) | diff=恰 4 行 A 零 M/D 零第二类;纯线性零 merge;ls-remote 实取(尖端数登记 §四);E2E-A 六文件/G1 四文件/G2 四文件/设计六件/主流水线/registry/workflow 零改动;LIVE 零写入/launchd 零触碰/档案不 commit/.gitignore 不改 |
| AC-06 CI 与证据包 | 部分 NOT VERIFIED(如实) | 证据包八类最低集已装配+SHA256SUMS(清单自身显式豁免);CI dispatch=操作者动作,本轮未发生→conclusion 待 CHECKPOINT;五节齐备+stdout 四段=自述 |
| AC-07 研究纪律 | PASS(自评) | 禁编造(三来源外数值零产生,D3 负向实证);缺值不填0(缺席/non_specifiable→limitations 声明义务);状态永不直写(三态全提案制,append-only 档案,改写恒拒);零真实调用/凭证/付费(T6 源码锁);白名单外需求零实施(发现登记: 见 §四) |

## §四 如实偏差与登记发现

1. **test_p4_fixes 本地红 4 项**(既有,非本包): 基线归因沿袭(monthly_review 数据块,39 通过/4 失败;G1/G2 REPORT 同款登记);本包与其零导入关系。
2. **AC-06 CI 侧 NOT VERIFIED**: dispatch 权在操作者(合同纪律),执行Agent 禁自行触发;补 CI 证据=CHECKPOINT 动作,非本包整改项。
3. **测试断言时序修正(先登记后运行阶段自捕)**: `test_rejected_proposal_dedup_repeat` 首版将 repeat=1 断言置于第二次留档调用之后——`ae._record_proposal` 返回的是留档条目本体(去重命中原地累加 repeat),第二次调用后 e1 视图随之=2;修正=断言移至第二次调用前(语义不变,预期值仍字面量 1/2/单条目)。发生于套件首跑红 1 → 定位 → 修复 → 61 全绿,如实登记。
4. **白名单外需求发现登记(不实施)**: ①预测候选落 allocation_views.json 的持久化与裁决沿既有回写链(本包只构造候选,零写文件——编排层 WP-G4 范围);②prior_triggers 生产读取(thesis.json quant_triggers/allocation_views.json triggers)属 WP-G4 编排(本包 `extract_prior_trigger_targets` 已留注入面,测试注入合成集);③模式 B promoted_to_task_id 升级路径(§六 L200)属 E2E-B 链,本包投影仅承接裁剪版;④`build_e2ea_projection` 的 falsifiable_conditions_merge 为「可规格化子集并入」——任务档既有条件的合并去重策略(全量并集 vs 本假设子集)留编排层决策,本包登记=子集并入(不覆盖任务档既有条目)。
5. **UTC 时刻**: 开工时刻与提交时刻以 git 取证输出为准(§四 REPORT);本文件落笔 2026-11-05(UTC),实测值见证据包。

## §五 漂移维护策略(AC-03 专节,三要素)

1. **测试预期值唯一来源=仓库内版本化合成 fixture**: `tests/test_p03_w2_glm_g3.py` 内 `build_input`/`build_output`/`TIPS_FACT`/`GOLD_FACT`/`REG_SYN`/`TRIG_SYN`/`TRIGGER_FIRED`(全部内联合成,数值锚点 2.93/4186.7/3.5/4300.0 等为 E2E-A 登记窗终值语义的合成复用);断言期望值均硬编码字面量(阈值序[2.93,0.73,73.0,2.20]/[4186.7,3.7,4161.7]、conclusion_id 'CR-20261105-001'、新版本 '__v2'、ECHO_LITERAL 整字典、问题消息子串),不从被测模块导入计算(自证恒真是 F 反例);注册表/触发器经 monkeypatch 注入合成集,真实 `config/metric_registry.json`、`config/thesis.json`、`data/allocation_views.json` 永不入测试。
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: 若合成 fixture 结构/锚点变更,受影响断言(阈值序字面量、E2EA 投影比对、ECHO_LITERAL)与 fixture 定义在同一提交内同步修改;本包交付后任何此类变更走登记型修订(新工作包/合同修订),禁散点改。
3. **真实数据档永不进入测试预期值来源**: 测试零读取 `data/daily/`/`data/research/`(源码级: 测试仅内联合造对象;T6 源码锁同时断言被测模块禁用模式零命中[data/daily 等]);fixture 自检(T0)只断言合成输入经 G1/G2 既有契约校验回读合法,不锚定真实交易日数据;集成用例走 G2 `run_conclusion_pipeline` 合成桩,零真实 GLM 出站。

## §六 fixture→预期值映射登记(AC-03;逐断言组可追溯)

| 断言组 | fixture 定义处(tests/test_p03_w2_glm_g3.py) | 预期值形态 |
|---|---|---|
| fixture 自检(T0) | `build_input`(合成 GLMResearchInput 模式A)/`build_output`(合成 HypothesisSet) | `gia.validate_input(...)==[]`+`gov.validate_output(...)==[]`(权威=G1/G2 既有校验器,复用非复制) |
| 步1 变量化(T1) | `TIPS_FACT`/`GOLD_FACT`(statement 含 TIPS_10Y/GOLD_F)/JGB_10Y(登记缺席)/DXY_10Y(注册未入输入) | 三分类集合字面量(present/absent/registered_not_in_input) |
| 步2 阈值三来源(T1) | TIPS 派生族(basis 2.20/pp 0.73/bp 73.0)/`REG_SYN`{range:[1000,30000],max_week_pct_move:25}/`TRIG_SYN`[3.5,4300.0] | 逐源列表字面量: 证据包序=[2.93,0.73,73.0,2.20](value→派生固定序)/注册表=[1000,30000,25]/先验=[3.5,4300.0];auto 优先序取首 |
| 步3 规格化+步4 trace(T1) | `build_input`(task_ref.window) | spec 五键整字典+窗口缺省=WIN{2026-10-20~2026-11-02}+op/mode 枚举外 ValueError+trace deferred-to-g2-validator 字面量 |
| 不可规格化双流(T1) | JGB_10Y(absent_registry)/在场无来源变体 | non_specifiable declaration 含「不可程序裁决」标记字面量;apply 后 limitations 条目断言 |
| 集成闭环(T1) | derive+apply 后整体输出 | `gov.validate_output(...)==[]`(步4 承接托底) |
| 注入面(T1) | `TRIG_SYN` | `extract_prior_trigger_targets`→{3.5,4300.0} 字面量 |
| 数值前置+阻断(T2) | statement 篡改 2.94(不在证据包)/`build_input(gate='DEGRADED')` | blocked=True+combined='FAIL'/DEGRADED 不阻断(gate_a 合成语义) |
| 门禁同构(T2) | `TRIGGER_FIRED`(invalidation 触发)/new_support 1 项/2 项 | 拒理由子串(「终态判定」「≥2」)+放行理由子串(「新增独立支持证据2项」「invalidation触发器」「INV-1」)+`gci.RATING_CHANGE_MIN_EVIDENCE==ae.MIN_EVIDENCE_FOR_RATING_CHANGE==2` |
| 星级门禁(T2) | star_max=3 变体(4/3/None) | 「不足以授予4★」拒/受纳/None fail-closed |
| 留档复用(T2) | `_proposal()`(change_to='已失效') | `ae._record_proposal` 实调用语义: 首登 repeat=1(第二次调用前断言)→重提 repeat=2 单条目+proposals[0].to='已失效' |
| 预测候选(T2) | pred_* 四键(缺 pred_target/齐全) | 拒理由含「['pred_target']」/受纳含'not_yet_triggered' |
| 记录构造(T3) | `run_fixture_pipeline`(G2 真实管线,ACCEPTED_DOWNGRADED) | 字段整表: conclusion_id='CR-20261105-001'/snapshot 绑定透传/outcome 透传/falsifiable_spec_count/gate_b_verdicts |
| 交叉引用(T3) | task_ref/query_ref 剥离变体+畸形 ID 变体 | InvalidConclusionRecord 消息子串(「必携 task_id 或 origin_query_id」/RT-/QB-/HY-/CR- 格式) |
| append 三态(T3) | 同指纹重放/异指纹(out 篡改 statement)/全新 | 'skipped-idempotent'/'CR-20261105-001__v2' 追加+原记录逐键不动/'written'+ArchiveImmutable |
| 9 行契约+投影(T4) | `E2EA_FIELD_MAP`/`build_e2ea_projection`(`build_input`/`build_output`) | SCHEMA_MIN_FIELDS 实读字面量+9 行三元组整表+投影逐承接面(task_id 透传/echo 回显/history 行/evidence_refs 方向化/direction 三值[support/counter/neutral]/可规格化子集/pred_* 候选/status_proposal/模式 B 裁剪键集) |
| echo(T5) | 纯产品结构 | `ECHO_LITERAL` 整字典=REPORT §二.1/§二.2 登记值 |
| 源码锁(T6) | 被测模块源文件 | 禁用模式清单(http/requests/socket/urllib/os.environ/API_KEY/open(/glob(/data//launchd/subprocess)零命中+复用标记断言(ae._record_proposal/ae.MIN_EVIDENCE_FOR_RATING_CHANGE/gov.SPEC_OPS 等) |

## 参考

- 冻结合同: IA-P03-W2-GLM-WP-G3-AC-v1.0(提示词内嵌;引擎存档路径执行Agent 不可达)
- 设计: docs/P03_W2_GLM_DESIGN.md §五(1)-(4)/§六/§七 WP-G3 行(blob c72d41a1,与设计支 0c8de3c3 侧等值)
- G2 对齐: scripts/glm_output_validator.py(数值校验前置/合法阈值/枚举 复用)/docs/P03_W2_GLM_G2_REPORT.md(§二.3 预留承接登记)
- 同构基准: scripts/allocation_engine.py:139/1170-1184/1262-1269 + scripts/report_generator.py:525-526/1137-1188/1310-1324
- E2E-A 契约: scripts/research_task_manager.py:36-40(SCHEMA_MIN_FIELDS/STATUS_FLOW/REPLAY_POLICY)
- 执行报告(细节): docs/P03_W2_GLM_G3_REPORT.md
