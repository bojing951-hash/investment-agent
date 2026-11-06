# IA-P1-DESIGN-COMP 执行报告(REPORT)

> 包: IA-P1-DESIGN-COMP(P1 收口链设计补全轮=#19 跨经济体比较视图+#20 常态监测 规格定稿·docs-only,R064)
> 合同: IA-P1-DESIGN-COMP-AC-v1.0(FROZEN 2026-11-06 20:3x HKT,操作者代批;提示词附录A内嵌传递)
> 分支: `dev/p1-design-comp`(自 BASE-COMP=`64ce40c25409bdb0a3d9fecc4c5f0f5df74dd902` 切出,纯线性,零 merge)
> 编制: 2026-11-06(UTC) | 执行Agent(Agent 3)
>
> **数值标注纪律(全文)**: 逐值 `[实取·来源: 文件:行号 或 ls-remote/实测时刻]` 或 `[示意·非实取]`。日期/SHA/结构编号(§4a 层编号/工作包编号/GAP-DP 编号)/档键成分按合同 §三.2 出圈(头部声明此边界);本 REPORT 与新增规格文本中一切 `文件:行号` 引用均为基线工作树(BASE-COMP=64ce40c)实读,偏差≤3 行可复核。凡引 handover §4a 块内容一律标「注入摘要(2026-11-06),非工作树实读」。
> **零运行产物声明**: 本包=docs-only 设计轮,零代码/零测试/零 workflow 改动;`data/daily/`、`data/research/`、既有快照零写入;本地 CI 实测仅为验证 docs-only 零测试面变更(§六对照),非本包运行产物。

---

## §零 白名单登记(开工首步;登记后即本合同白名单实体)

| 类 | 文件 | 说明 |
|---|---|---|
| A1 | `docs/P1_DESIGN_COMP_REPORT.md` | 本件(纯新增;`git ls-files` 零重合 [实取·2026-11-06 ls 核对]) |
| A2 | `docs/P1_DESIGN_COMP_DELIVERY.md` | 交付说明(纯新增;`git ls-files` 零重合 [实取·同上]) |
| M1 | `docs/P1_DESIGN.md` | **M 面实际触碰集=恰 1 件**(⊆授权三件集合且必含 P1_DESIGN.md,满足;P1_DELIVERY.md/P1_DATA_NEEDS_INVENTORY.md 不触碰);diff=纯追加零删改(插入 §六 两行+文档尾 §八 规格节,既有行零触碰,R047 纯插入先例) |

- 白名单外一切路径零变更;D=0。
- 行号登记(编辑后实测复核,见 §一): `docs/P1_DESIGN.md` §六 新增两行=**L174-L175**(WP-P1-F 行 L174/WP-P1-G 行 L175,插于既有 WP-P1-E 行 L173 之后、空行 L176 之前;红线筛查行原 L175→现 L177,零内容改动仅行号平移+2);§八 规格节=**L188 起**(§八.1=L192/§八.2=L225;文档尾追加,原末行 L182(现 L184)零内容改动仅行号平移;编辑前估值「L184 起」按实测更正登记)。

## §零.1 开篇核验实录(AC-01 ①-⑥;命令输出原样留存证据包③)

| # | 核验项 | 实测 | 判定 |
|---|---|---|---|
| ① | BASE-COMP 复核 | `git ls-remote origin main`=`64ce40c25409bdb0a3d9fecc4c5f0f5df74dd902`=`git rev-parse HEAD`(切支后),与合同 §零 全值一致 | 过 |
| ② | 开工前 `git status` | clean(On branch main, nothing to commit),UTC 2026-11-06T15:06:06Z | 过 |
| ③ | 分支自 BASE-COMP 切出且此前不存在 | `git checkout -b dev/p1-design-comp 64ce40c…` 成功;此前 `git ls-remote origin dev/p1-design-comp` 无输出(不存在);首提交父=BASE-COMP [实取·git log 复核,见 §一] | 过 |
| ④ | 049ec978 祖先可达 | `git merge-base --is-ancestor 049ec978523dec659ba47f140bf41669604de24f HEAD` exit 0 | 过 |
| ⑤ | 设计三件在场+blob 登记 | 三件在基线工作树在场;blob 哈希逐一登记: `P1_DATA_NEEDS_INVENTORY.md`=`df79c06f66c368d93159b7a3b46852b6fcb9b196`、`P1_DELIVERY.md`=`314c2644a51f2f575a90253580cb56346e2f93b6`、`P1_DESIGN.md`=`13b263cf3139d420e01bf1e154b03ce85a35db4c`;与 049ec978 侧 `git ls-tree` 逐一**等值**(双侧同 blob id)→登记「等值」,无归因义务触发 | 过 |
| ⑥ | `dev/p1-design` 尖端全值复核 | ls-remote=`049ec978523dec659ba47f140bf41669604de24f` 逐字一致(禁锚 c9626633 未混入) | 过 |

**BRANCH-SET 对照(§五.4 前置)**: 开工时点 `git ls-remote --heads origin` 全表 **47 支** [实取·2026-11-06T15:06Z,快照存证据包③ `/tmp/p1-design-comp-evidence/ls-remote-frozen-check.txt`],与冻结章补遗 47 支全表逐支前12位比对一致(既有分支尖端一律不变;唯一缺席=`dev/p1-design-comp`,应然——冻结派发前不得创建,创建=执行段第一步)。

(§一及以后=实现登记;编辑完成后续写。)

## §一 规格落位登记(AC-02;行式对齐依据+落位+挂接)

**§六行式对齐依据**: 既有 WP-P1-A..E 五行实读 [实取·docs/P1_DESIGN.md L169-L173],五列式样=`| 包名+短述 | 目标 | 范围 | 依赖 | 验收要点草案(①②③+【工件类】标注) |`;新两行逐列仿写(包名+挂靠编号/目标短句/范围枚举+互斥划界/依赖+锚指针/①-⑤要点+【测试】【测试/CI】【PENDING】标注),行式可对齐判定=**可行**(无情形(d)触发)。

**落位登记**:

| 项 | 落位 | 行号 [实取·编辑后 grep -n] |
|---|---|---|
| §六 新行1(WP-P1-F,挂靠 §4a#19) | 插于 WP-P1-E 行 L173 之后 | **L174** |
| §六 新行2(WP-P1-G 候选名,挂靠 §4a#20) | 同上 | **L175** |
| §八 规格节头(含互斥划界/#21 衔接注记/红线承接/W4-W5 不入链) | 文档尾追加(原末行 L182→现 L184 零内容改动) | **L188-L190** |
| §八.1 四要素+DP 节 | 目标 **L194**/范围 **L196-L210**/依赖 **L202-L210**/验收要点 **L212-L217**/DP 节 **L219-L223** | 见左 |
| §八.2 四要素+DP 节 | 目标 **L227**/范围 **L229-L235**/依赖 **L237-L240**/验收要点 **L242-L249**/DP 节 **L251-L256** | 见左 |

(注: §八.1 范围节起 L196,依赖节起 L202——两节行号区间如上;四要素逐要素可寻。)

**挂接登记**: 两行均显式挂靠 §4a 编号(#19/#20,行内「(§4a#19)」「(§4a#20)」)=「每个新工作包必须挂到上表某层某编号」纪律承接 [注入摘要,handover §4a L164,非工作树实读]。

**可区分性登记**: ①新行 vs A..E 行: A..E=经济体底图层行(registry+采集/引擎+快照/评分+装配/查询+档案/CN 修复,实读 L169-L173),新两行=收口链消费/运行面(比较视图=横向并置消费;常态监测=持续运行监测)——功能不同构;②两新行互不同构+互斥划界显式: #19 行内「不含持续运行监测面(=#20,互斥)」/#20 行内「不含按需比较视图(=#19 前件,互斥)」+§八 头部「#19=按需横向比较消费面 / #20=持续运行监测面」。

**#21 面不下放登记**: §八 头部明文「#21(P1 验收+终裁+封版)不在本节: 终验/封版/用户确认面由 #21 合同事承载(本节仅衔接注记)」;两规格节内 #21 仅以衔接注记出现(§八.1 范围4/§八.2 范围5),零终裁/封版/用户确认条款。

## §二 溯源表(AC-03.1;锚源三族: 甲=§4a 注入行/乙=设计三件既有节/丙=上游在场交付件)

> 甲族标注: 「注入摘要(2026-11-06),非工作树实读」+注入行号;乙/丙族=BASE-COMP 工作树实读 file:line(2026-11-06)。

### §八.1 WP-P1-F(§4a #19)逐要素溯源

| 要素 | 实质主张 | 锚源 |
|---|---|---|
| 目标-需求源 | 跨经济体比较视图=§4a 第二层 #19 路线级意图展开 | 甲: 注入摘要 handover §4a L138「19-20. 跨经济体比较视图+常态监测…」 |
| 目标-四经济体 | US/CN/JP/EA 四经济体构成 | 乙: INVENTORY a.1 DP-1 L13-L24(默认候选,确认留用户) |
| 目标-比较用例形态 | W-1 型 US×EA 政策分化=比较视图支撑场景 | 乙: P1_DESIGN §三(d) W-1 L88-L100(结论形态 L100) |
| 目标-纯消费面 | 零新数据源/不重做底图/快照唯一入口 | 乙: P1_DESIGN §一 In scope/Out of scope L16-L18;§四衔接设计 L141 |
| 范围1-装配面 | economy_scorecard_{econ}_ 并置+经济体观察节复用+DISCLAIMER | 丙: macro_scorecard.py L40/L487-L488;data_assembler.py L277-L301;macro_scorecard.py L32-L33 |
| 范围2-事实面 | series_store+跨域对比较呈现 | 丙: snapshot_builder.py L427-L471;correlation_calculator.py L28/L49/L51/L60/L90 |
| 范围3-查询面 | economy 过滤比较用例(W-1/W-2 型) | 丙: research_history_query.py L184-L201/L337;乙: P1_DESIGN §三(d) W-2 L102-L113 |
| 范围4-互斥 | 不含持续运行监测面 | 甲: 注入摘要 L138(#19/#20 同行两能指分立);本文 §八 头部划界 |
| 依赖-层序前置 | 第一层已关闭+A..E+GAP08 在场 | 甲: 注入摘要 L162-L163(层序规则);丙: 各包交付件在场(§四能力面清单) |
| 依赖-锚列 | macro_scorecard/data_assembler/correlation/snapshot/fact_engine/registry/rhq/qir 各锚 | 丙: 逐条 file:line 见 §八.1 依赖列(L202-L210)+§四 |
| 要点①-零直读 | 比较视图零直读采集档 | 乙: P1_DESIGN §四 L130(禁直读约束覆盖 jp_/ea_);§七 L179 |
| 要点②-缺席如实 | DATA_INSUFFICIENT/「无数据」不填0 | 乙: P1_DESIGN §三(c)4 L84;丙: macro_scorecard.py L30/L36-L38 |
| 要点③-US 零回归 | W-3 基准路径行为零回归 | 乙: P1_DESIGN §三(d) W-3 L115-L118 |
| 要点④-DP 纪律 | 先登记后运行/禁回改 | 甲: 注入摘要 DP 分类纪律(R020-D5 承接);AC-07.1 |
| 要点⑤-PENDING | 真实调用/凭证/付费→DP/PENDING | 甲: 注入摘要 L164-L165(数据卡点处置序+付费报批) |
| DP-F1/F2/F3 | 落位形态/并置最小集/配对新增三决策 | 乙: P1_DESIGN §二 DP 表式样 L26-L31(登记型式样承接);选项值 [示意·非实取] |

### §八.2 WP-P1-G(§4a #20)逐要素溯源

| 要素 | 实质主张 | 锚源 |
|---|---|---|
| 目标-需求源 | 常态监测=「让 P0-3 验证的研究流程更大范围长期跑」 | 甲: 注入摘要 handover §4a L138 |
| 目标-P0-3 流程构成 | E2E-A/E2E-B/GLM 竞争性假设/报告生成+档案 | 甲: 注入摘要(P1 已交付面段);丙: 在场件见 §四 |
| 范围1-链路监测 | 13 步流水线台账+sources_status/Gate A+新鲜度(月频 60 天) | 丙: run_weekly.py L126-L157/L12/L217-L238;snapshot_builder.py L382-L385;config/metric_registry.json CPI 条目 freshness(json.load 实测 2026-11-06);乙: P1_DESIGN §三(c)2 L82 |
| 范围2-异常扩展 | detect_divergence 为 US 单一对;扩展形态=DP-G2 | 丙: anomaly_detector.py L29-L32/L60 |
| 范围3-任务衔接+状态保护 | build_task/SCHEMA_MIN_FIELDS/falsifiable/append-only;状态机+台账放行 | 丙: research_task_manager.py L36-L37/L64/L79/L139/L165-L189;report_generator.py L985;run_weekly.py L211-L216;乙: P1_DESIGN §四 L132/L143 |
| 范围4-回溯查询 | rhq economy 过滤=监测回溯消费面 | 丙: research_history_query.py L184-L201;乙: P1_DESIGN §四 L130 |
| 范围5-互斥+#21 注记 | 不含比较视图(=#19 前件);#21 衔接注记 | 甲: 注入摘要 L138/L162-L163;本文 §八 头部 |
| 范围6-部署边界 | LIVE 部署=用户保留卡点③ | 甲: 注入摘要 L166(用户三保留卡点) |
| 依赖-#19 前件 | #20 登记 #19 前件(层内收口链) | 甲: 注入摘要 L138(#19-20 同层收口链);AC-02.4 |
| 依赖-P0-3 链锚列 | anomaly/rtm/rhq/archive/report_gen/validator 各锚 | 丙: 逐条 file:line 见 §八.2 依赖列(L237-L240)+§四 |
| 依赖-底图锚列 | run_weekly/snapshot/registry 各锚 | 丙: 同上+§四 |
| 要点①-零直读零新通道 | 监测面=台账/快照/事实层消费 | 乙: P1_DESIGN §七 L179(快照+门禁不可绕开) |
| 要点②-断点如实 | MISSING/越限如实列示,与 Gate A 语义一致 | 乙: P1_DESIGN §三(c)1 L81/(c)3 L83 |
| 要点③-append-only+schema | 可增不可减/falsifiable 语义不变/状态仅经状态机 | 丙: research_task_manager.py L7/L36-L37;report_generator.py L985;乙: P1_DESIGN §四 L132 |
| 要点④-套件零回归 | 套件数以实现包 BASE 实取为准 | 丙: 本包 75 槽对照先例 [实取·ls tests/test_*.py=75,2026-11-06];AC-06.1 |
| 要点⑤-DP 纪律 | 先登记后运行/禁回改 | 甲: 注入摘要 DP 分类纪律;AC-07.1 |
| 要点⑥-部署 PENDING | LIVE 部署与通知面=确认型 DP·PENDING·确认权留用户 | 甲: 注入摘要 L166(保留卡点③);AC-07.1 确认型 |
| 要点⑦-GLM PENDING | 真实 GLM 调用面=PENDING·用户实批前置 | 甲: 注入摘要(零真实调用边界,设计对象≠设计手段);AC-07.2 |
| DP-G1/G2/G3 | 回溯窗/异常扩展形态/新鲜度口径 | 乙: P1_DESIGN §二 DP 表式样 L26-L31;提案值 [示意·非实取] |
| DP-G4/G5(确认型) | 运行宿主/通知形态=确认权留用户+PENDING | 甲: 注入摘要 L166(保留卡点③);L164-L165(凭证报批) |

**零源断言自检**: 上表覆盖两规格节全部实质主张;每主张至少一锚;无零源断言。

## §三 DP 登记节(AC-07.1;计数: 登记型 6/确认型 2,确认型全部 PENDING)

| DP | 决策点 | 选项≥2 | 推荐 | 影响 | 分类 |
|---|---|---|---|---|---|
| DP-F1 | 比较视图落位形态 | ①数据包新节 ②独立模块 ③报告模板章节 | ② [示意·非实取] | 实现包白名单与 US 零回归面 | 登记型 |
| DP-F2 | 并置指标最小集 | ①总分+regime ②+关键事实行 ③全量表 | ② [示意·非实取] | 视图信息结构与缺席断言面 | 登记型 |
| DP-F3 | 跨经济体配对新增 | ①零新增 ②候选对(SPX×SHCOMP 类) ③更广集 | ① [示意·非实取] | series_store 消费面与相关性输出 | 登记型 |
| DP-G1 | 常态健康回溯窗 | ①7日 ②14日 ③30日 | ② [示意·非实取] | 监测视图数据面与断言构造窗 | 登记型 |
| DP-G2 | 异常检测经济体扩展形态 | ①规则族参数化泛化 ②新规则模块 ③regime 变化候选 | ① [示意·非实取] | 检测面与任务生成量 | 登记型 |
| DP-G3 | 新鲜度监测口径 | ①逐条监测 ②分层(月频 60 天窗沿既有+日频 MISSING 回溯) ③仅核心 | ② [示意·非实取] | 越限断言面与误报率 | 登记型 |
| DP-G4 | 常态监测运行宿主与部署面 | ①LIVE launchd ②手动触发 ③DEV 演练先行 | (登记不裁断) | #20 实现包交付面范围 | **确认型·确认权留用户·PENDING**(LIVE 部署=用户保留卡点③) |
| DP-G5 | 监测结果通知形态 | ①零通知 ②终端摘要 ③外部通知(涉个人流程/凭证) | ① [示意·非实取] | #20 实现包通知面有无 | **确认型·确认权留用户·PENDING**(涉用户个人流程;选项③另涉凭证=PENDING 报批) |

(#19 规格节确认型=无,如实登记 [实取·§八.1 DP 节 L223];#20 确认型 2 项全 PENDING。)

## §四 能力面清单(步骤6 实读;上游在场交付件锚=AC-02.4 依赖列支撑+AC-04 引用清单)

**A..E 各包交付件对照同源**(以各包 REPORT §零 登记清单为源,工作树在场核对 [实取·2026-11-06]):
- WP-P1-A [实读·docs/P1_WP_D_REPORT.md §零.2 L45]: scripts/jp_market_collector.py、scripts/ea_market_collector.py、config/metric_registry.json(economy 三字段+条目)在场;
- WP-P1-B [实读·同上 L46]: scripts/fact_engine.py(normalize_jp/normalize_ea/build_all)在场;
- WP-P1-C [实读·同上 L47]: scripts/macro_scorecard.py、scripts/data_assembler.py、scripts/correlation_calculator.py 在场;
- WP-P1-D [实读·同上 L48]: scripts/e2eb_query_ir.py、scripts/e2eb_query_mapper.py、scripts/research_archive.py、scripts/e2eb_query_executor.py 在场;
- WP-P1-E [实读·docs/P1_WP_E_REPORT.md §零.3 L52-L53]: scripts/china_market_collector.py、config/metric_registry.json(v2.3.0 CN 宏观八条)在场;
- GAP08 [实读·docs/P1_GAP08_REPORT.md §零.3 L49-L50]: scripts/snapshot_builder.py、scripts/research_provenance.py、scripts/research_task_manager.py、scripts/research_history_query.py 接线在场。

**关键实现面锚(全部 grep/Read 实取,2026-11-06,BASE-COMP 工作树)**:

| 面 | 锚 |
|---|---|
| 评分经济体维度 | macro_scorecard.py: score_growth L99/score_inflation L200(economy 参数)/save_scorecard L414-L417/DATA_INSUFFICIENT L30/DISCLAIMER L32-L33/ECONOMY_NAMES L39/ECONOMY_SCORECARD_PREFIX L40/非US economy 键+档名 L483-L488 |
| 数据包经济体节 | data_assembler.py: economy_scorecard L91/build_markdown L146/「经济体观察」节 L272-L301 |
| 相关性 | correlation_calculator.py: PAIRS L28(NIKKEI225×USDJPY L49/DAX×EURUSD L51)/paired_returns L60/compute_all L90 |
| 快照通道+接线 | snapshot_builder.py: resolve_inputs L47/build_snapshot L266/jp/ea/japan 接线 L335-L350/Gate A 重算 L382-L385/series_store L427-L471 |
| 事实引擎 | fact_engine.py: compute_period_returns L81/normalize_jp L523/normalize_ea L566/validate_fact L641/cross_metric_checks L789/build_all L837 |
| registry | config/metric_registry.json: version=2.3.0/metrics=102/economy 计数 US49/CN18/EA11/JP8/HK4/GLOBAL12/active101+deprecated1/CPI 条目 freshness.max_calendar_lag_days=60(均 json.load 实测 2026-11-06) |
| 查询过滤 | research_history_query.py: ECONOMIES L77/load_metric_series L100/query_window(economy) L184-L201/--economy L337;e2eb_query_ir.py: ECONOMIES L53/IR_KEYS L67/economy 校验 L287-L288 |
| 流水线与台账 | run_weekly.py: steps 13 步 L126-L157/放行标志 L211-L216/台账原子写 L217-L238/台账档名 L12 |
| 异常检测 | anomaly_detector.py: 阈值登记 L29-L32(CORR_THRESHOLD=0.30/RATE_BP_THRESHOLD=25.0/GOLD_PCT_THRESHOLD=2.0)/detect_divergence L60 |
| 研究任务与档案 | research_task_manager.py: SCHEMA_MIN_FIELDS L36-L37/_task_economy L64/build_task L79/falsifiable_conditions L139/append-only 落档 L165-L189;research_archive.py: validate_id_conventions L67/validate_query_record L191 |
| 报告与门禁 | report_generator.py: generate_report L377/verify_research_inputs L612/update_thesis_status L985;data_validator.py: forbidden_phrases_in L238/validate_report(Gate B) L755 |
| 架构纪律 | docs/ARCHITECTURE_V2.md: v2六层 L26-L49(L3 快照 L38/L5 当日纪律 L48/L6 Gate B L49) |

## §五 §5.3 提交前数值标注六项自检清单(AC-03.2/03.4;清单成件入证据包⑥)

**扫描方法**: 对 `docs/P1_DESIGN.md` 新增部分(L174-L175/L184-L257)+本 REPORT+DELIVERY 全文,逐数值清点三态标注(A=已标实取/B=已标示意/C=出圈/D=疑似失实)。

| # | 值 | 三态 | 来源/处置 |
|---|---|---|---|
| 1 | 四经济体(US/CN/JP/EA) | A | INVENTORY a.1 L13-L24;macro_scorecard.py L39 [实取] |
| 2 | registry v2.3.0 | A | config/metric_registry.json json.load 2026-11-06 |
| 3 | 102 条目 | A | 同上 len(metrics)=102 |
| 4 | US49/CN18/EA11/JP8/HK4/GLOBAL12 | A | 同上 Counter 实测 |
| 5 | 13 步流水线 | A | run_weekly.py L126-L157 实读 2026-11-06(R015 时点 11 步=INVENTORY L159 时点值,已陈旧,新规格一律用 13) |
| 6 | 月频窗 60 天 | A | registry CPI 条目 freshness json.load 复核 2026-11-06;P1_DESIGN L82 |
| 7 | 0.30/25.0/2.0(异常阈值) | A | anomaly_detector.py L29-L31 |
| 8 | 7/14/30 日(回溯窗) | B | [示意·非实取](DP-G1 提案值) |
| 9 | 两跨域对(NIKKEI225×USDJPY/DAX×EURUSD) | A | correlation_calculator.py L49/L51 |
| 10 | 75 套件 | A | ls tests/test_*.py \| wc -l=75,2026-11-06;=BASE-COMP-CI-SUITES 冻结章实值 |
| 11 | 47 支分支 | A | ls-remote --heads 2026-11-06T15:06Z 实取 |
| 12 | 74 插入/0 删除 | A | git diff --numstat docs/P1_DESIGN.md(提交前终值以证据包③为准) |
| 13 | 登记型 DP 6/确认型 2 | A | 新增规格 DP 节清点(§八.1 3 项+§八.2 5 项) |
| 14 | R044-R048/R061/R064/R015/R017/R019/R020/R047 等轮号 | C | 结构编号出圈(头部边界声明) |
| 15 | #19/#20/#21、§4a、WP-P1-A..G、G-P1/GAP-P1/K-1..K-6、DP-F/G、QB-/RT- | C | 结构编号/档键成分出圈 |
| 16 | 日期(2026-11-02/06 等)与 SHA | C | 日期/SHA 出圈(头部边界声明;SHA 均全值) |
| 17 | ①②③…要点序号、L 行号 | C | 档内序号/行号成分出圈(行号=实取引用) |
| 18 | 疑似失实项 | D | **无**(编辑前估值「§八=L184 起」已按实测更正为 L188,见 §零) |

## §六 逐 AC 自评素材指针(正式自评=DELIVERY §三+stdout 第四段)

- AC-01 → §零/§零.1+证据包③ git 取证;
- AC-02 → §一(行号/对齐/挂接/互斥)+P1_DESIGN.md L174-L175/L188-L257 直读;
- AC-03 → §二溯源表+§五扫描清单;
- AC-04 → §二/§四(全部引用=工作树实读或显式注入标注;跨支引用=零;交付依赖零引擎路径);
- AC-05 → git 取证(证据包③)+M 面零删行取证+LIVE grep(证据包③);
- AC-06 → 本地 CI 记录(证据包④)+证据包 zip+DELIVERY 五节+stdout 四段;
- AC-07 → §三 DP 登记+新增规格 DP 节直读+零网络/零调用声明。

## §七 如实登记与声明

1. **零运行产物**: 本包 docs-only,零代码/零测试/零 workflow/零配置;`data/` 全域零写入;本地 CI 实测=对照 AC-06.1 的 docs-only 零测试面论证(测试面与基线逐字节一致),非本包运行产物。
2. **零网络/零真实调用/零凭证/零付费**: 本包全程零网络出站(唯一网络面=git ls-remote/push 与 GitHub 通信,合同明示的取证与交付通道);零真实 GLM/LLM 调用;零凭证;零付费。
3. **LIVE 零写入**: LIVE 路径本轮零写入;LIVE grep 标记(`R064|P1-DESIGN-COMP|IA-P1-DESIGN-COMP`)零命中(取证证据包③);LaunchAgents 零改动。
4. **偏差登记**: 见 DELIVERY §四(如实偏差节);截至 REPORT 定稿零触发情形(d)/(b)/(c)。

