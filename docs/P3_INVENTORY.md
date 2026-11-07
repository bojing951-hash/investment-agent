# P3 长期积累与成果整合盘点(INVENTORY)

> 包: R030 · IA-P3-DESIGN(P3 收尾层 · 设计线第1包,docs-only 零代码)
> 基线: `f8ed401f4274e158c06a9404149d41260e5cc0ad`(dev/p2-design 尖端;开工时 `git ls-remote origin dev/p2-design` 实取一致,前7位 `f8ed401` 校验通过)
> 盘点分支: `dev/p3-design`(自基线切出)
> 盘点时点: 2026-11-03(UTC) · 全部行级引用以本 checkout 实码为准,实测方法逐处注明
> 用途: 为 P3「长期积累与成果整合」的设计提供**事实层依据**;已知缺口清单(P3-G-*)供 DESIGN §7 承接

---

## 数值标注约定(全文适用,二选一)

- **[实取·来源: 文件:行号 或 实测命令,2026-11-03]** = 直接读自本 checkout 真实文件或本包实测命令所得;
- **[示意·非实取]** = 非实取示例/设计提案值;
- 跨支值(读自 dev/p1-design / dev/p03-w2-glm-design 等另支)标 **[实取·跨支只读: git show FETCH_HEAD,分支@尖端全SHA,2026-11-03]**(尖端均经 `git ls-remote` 当日实取比对;行号属该支该文件,非本工作树);未实读的跨支内容标 **[示意·非实取·跨支登记 分支@尖端全SHA]** 或「注入摘要」;
- 注入引擎提示词的内容一律标「注入摘要(2026-11-03),非工作树实读」;
- 日期、SHA、版本字符串(如 registry `2.0.0`、thesis `2.0`、views `3.0`)、结构编号(如 P3-G-01、WP-P3-A)、档键成分(ID 格式字符串)按合同 AC-03 边界出圈,不强制标注(DESIGN 头部另有声明)。

---

## 面(a) 长期积累基础设施现状(逐项: 载体(文件:行号)或「不存在」)

### a.1 论点与资产观点状态 — 在场

| 载体 | 位置 | 说明 |
|---|---|---|
| 论点状态文件 | `config/thesis.json` L2(version 2.0)、L5-378(`theses` 数组,9 条 [实取·本表清点,2026-11-03]) | 逐论点字段: id/name/status/confidence/direction/core_logic/key_data/related_theses/relation_notes/invalidation_rules(L19-26)/upgrade_trigger(L27)/history(L28-33)/quant_triggers(L34-60);现行在场状态值 = 待观察 3 条 + 进行中 6 条 [实取·本文件逐条清点,2026-11-03],词表 4 值(进行中/待观察/已验证/已失效)以 `scripts/report_generator.py` L501 为权威 [实取·词表计数 4=同 L501 原文,2026-11-03] |
| 资产观点状态文件 | `config/allocation_views.json` L2(version 3.0)、L17-391(`views` 数组,9 条 [实取·本表清点,2026-11-03])、L392-428(`predictions` 数组,2 条 [实取·同上]) | L4 治理注记原文在场: 评级变更须过门禁(引擎同向触发器"已触发"或≥2项程序验证 evidence)、被拒提案留档于各 view.proposals、quant_triggers 支持 all/any 复合与 sustain_weeks 持续确认、证据分级 v2 程序校验、预测全生命周期(premise→observe_from→observations→touch/expiry 双模式裁决,截止日不顺延);评级量表 4 级 L5-10 [实取·`config/allocation_views.json` L5-10,2026-11-03];现行在场评级 = 标配 4/低配 3/观望 1/超配 1 [实取·逐条清点,2026-11-03] |
| 门禁保护(提示词侧) | `scripts/report_generator.py` L503(状态终态门禁)/L504(终态退出门禁,含"不得改写原论点历史结论")/L505(确信度门禁)/L522(评级变更门禁,提案留档)/L523(确信度门禁) | 模型判断不满足门禁 → 降级为提案留档,不直接改状态 |
| 门禁保护(引擎侧) | `scripts/allocation_engine.py` L32(模块 docstring: 不满足时保留原评级,候选提案记入 proposals 留档,同向提案 21 天内去重)、L1171-1183(被拒提案留档实现;留最近 20 条,L1183)[实取·21 天/20 条=同文件 L32/L1183 原文常量,2026-11-03] | 引擎侧程序核验;`evaluate_quant_triggers` 触发器核验状态 4 标(✅已触发/⬜未触发/❓待验证/⏳持续确认中)在同文件 L1052-1053 [实取·状态 4 标=L1052-1053 原文,2026-11-03] |
| 论点回写入口 | `scripts/report_generator.py` L985(`update_thesis_status`) | 回写调度见 a.5 门禁 |

### a.2 预测观察与裁决 — 在场

| 载体 | 位置 | 说明 |
|---|---|---|
| 每日观察器 | `scripts/daily_prediction_observer.py` L2-38(模块 docstring: 接入每日流水线,按观测日去重幂等;P0-1 验证与写入隔离;P1-2 关键/非关键失败分级)、L122-205(`observe`,FAIL=关键失败今日不写任何观察)、L235(exit 0=正常含部分跳过/2=关键失败) | 只记录不裁决: L11"不调用GLM — 裁决仍由周报路径的引擎/受核验GLM执行,本脚本只做数据记录" |
| 观察记录写入(实义定义处) | **`scripts/allocation_engine.py` L726(`def record_observations`)** | **R020-D1 归属修正重申: `record_observations` 实义定义于 allocation_engine.py L726;`scripts/daily_prediction_observer.py` L191 为调用处(`ae.record_observations(...)`),以 daily_prediction_observer.py 为定义处引用 = 失实**。功能: 前提程序判定兑现→转观察中+盖 observe_from(L766-771);观察中预测记录 observations(按观测日去重)+防御校验(L774 起) |
| 预测状态口径 | 五态展示 `scripts/allocation_engine.py` L1066(未触发/观察中/已命中/已证伪/无法裁决);裁决回写词表 4 值 `scripts/report_generator.py` L534(hit/miss/inconclusive/not_yet_triggered);裁决纪律 L536-540(证据+观测日强制/窗口内数据/引擎已裁决不得覆盖/前提未兑现不得判 hit)[实取·五态/4 值词表计数=L1066/L534 原文,2026-11-03] | 两处口径并存: 展示层五态(含"未触发"前提态细分),回写层 4 值;预测规格字段(pred_metric/pred_op/pred_target/pred_mode expiry|touch/pred_basis/pred_premise_*)`scripts/report_generator.py` L525-526 |
| 现行在场预测 | `config/allocation_views.json` L392-428: pred_id 1(status=not_yet_triggered,L401;premise_text L411)/pred_id 2(status=observing,L421) | 2 条 [实取·清点,2026-11-03];observations 字段现值均为空数组(L409/L425) |

### a.3 研究档案与来源追溯 — 部分在场(快照级档案在场;跨任务共享研究档案=设计停泊)

| 载体 | 位置 | 说明 |
|---|---|---|
| 来源链与质量门禁原语 | `scripts/research_provenance.py` L2-54(模块 docstring: 快照→数据包→锚点→报告的可验证来源链)、L1243(`select_snapshot` 确定性版本选择)、L1297(`digest_snapshot` 内容指纹)、L1336(`provenance_of`)、L1366(`write_meta` 侧挂)、L1580(`verify_anchor_batch`) | 纯本地文件实现,不引入数据库/服务(L53"设计约束") |
| 周报档案与正式性 | `scripts/research_provenance.py` L1402(`weekly_report_files`)/L1429(`formal_report_view`)/L1493(`scan_formal_weekly_reports`)/L1505/L1515(最新正式/归档周报);发布事务注释 L1391 | 周报产物按发布状态认定正式性(`scripts/monthly_review.py` L29 同口径引用) |
| Gate 合成 | `scripts/research_provenance.py` L1533(`combine_gates`);L1101(`gate_status`)/L1183(`gate_allows_formal_research`) | 任一 FAIL→FAIL;双 PASS→PASS |
| 共享研究档案(跨任务) | **不存在(实现载体)**;设计定稿 = E2E-B DESIGN §4.1(集合族 research_tasks/anomaly_events/query_history,档案载体=E2E-B WP-B4,实现停泊) [实取·`docs/P2_DESIGN.md` L57 登记该衔接,2026-11-03;E2E-B 内部 schema 属设计定稿/契约草案,实现停泊] | P2 深研任务模型挂同一档案族(同上 L57-58) |

### a.4 报告制度 — 在场

| 载体 | 位置 | 说明 |
|---|---|---|
| 周报生成与发布 | `scripts/report_generator.py` L36(`OUTPUT_DIR = output/weekly`)、L909-924(候选→Gate B→状态→原子发布)、L1351-1354(生成前置核验四件套: 权威快照/Gate A/数据包绑定/锚点批次+锚点 prompt [实取·"四件套"为 L1352 原文用语,2026-11-03])、L1310-1324(`apply_status_updates`) | GLM 调用链 L574(`_call_glm`);报告模板含 THESIS_STATUS/ALLOCATION_STATUS/PREDICTION_STATUS 三机器状态块(L496/L511/L530)[实取·状态块 3 处=L496/L511/L530 实读,2026-11-03] |
| 月度复盘 | `scripts/report_generator.py` L1543-1552(周报流程尾触发 subprocess);`scripts/monthly_review.py` L29-33(`OUTPUT_DIR = output/monthly`) | 月度完结判定 `pending_completed_month` `scripts/report_generator.py` L957 |
| 季度展望 | `scripts/report_generator.py` L1555-1564;`scripts/quarterly_outlook.py` 在场(`ls scripts` 实测,2026-11-03) | 季度完结判定 L965 |
| 数据包(装配) | `scripts/data_assembler.py` L5-10(docstring: 读取当日研究快照渲染,经 `research_provenance.select_snapshot` 确定性版本选择)、L31、L128 | 快照渲染为唯一数据源 |
| 表述纪律先例 | `scripts/macro_scorecard.py` L30-31(DATA_INSUFFICIENT="数据不足不可判";每维度至少 2 个可用指标 L31 [实取·MIN_AVAILABLE_PER_DIM=2 常量,同文件 L31,2026-11-03])/L32-33(DISCLAIMER="评分卡=内部模型观点…非客观事实") | P3 表述纪律沿此先例 |

### a.5 回写门禁 + 快照纪律 — 在场

| 载体 | 位置 | 说明 |
|---|---|---|
| 校验分级与禁回写 | `scripts/data_validator.py` L373-375(注释: PASS/DEGRADED/FAIL 三级;**FAIL → 禁止一切长期状态回写(thesis/allocation/prediction)**)、L378(`classify_result`)、L755(`validate_report`) | 回写调度侧执行: `scripts/report_generator.py` L1316-1318(classification==FAIL → 跳过 thesis.json 与 allocation_views.json 回写) |
| 不可变快照 | `scripts/snapshot_builder.py` L8(research_snapshot_YYYYMMDD.json + 人读版 .md)、L14(同日已存在拒绝覆盖,退出码 3;--allow-revision 生成 _v2 并留修订原因)[实取·退出码 3=同文件 L14 原文,2026-11-03]、L236(`build_snapshot`)、L390-398(不可变执行/版本递增)、L411+L420(锚点产出+meta 侧挂 source=snapshot) | 快照含 gate_a(L354);Gate A 重算 `scripts/research_provenance.py` L853(`recompute_gate_a`) |

### a.6 P3 特有新能力面 — 逐项「不存在」(如实登记)

| P3 能力面 | 现状 | 取证 |
|---|---|---|
| 跨档案检索索引(关键词/多维度检索接口) | **不存在** | `grep -rn "错误模式\|error_pattern\|版本链\|version_chain\|自动关联\|auto_assoc\|知识库\|knowledge_base\|倒排\|检索接口\|search_" scripts/` 零功能载体命中;命中串均为模块名/注释等无关引用(如 research_provenance 模块名) [实取·grep,2026-11-03];`scripts/monthly_review.py` L29 的"周报索引"仅指按发布状态认定正式性,非检索索引 [实取·同文件,2026-11-03] |
| 研究结论级版本管理(结论版本链/历史结论修正记录) | **不存在**(注意区分: **快照级**版本管理在场且成熟 = a.5 `_v2`/revision_reason/select_snapshot;论点级仅有 history 散记数组与"不得改写原论点历史结论"纪律 L504,无结构化版本链) | 同上 grep;`config/thesis.json` L28-33(history 为字符串数组散记,非版本记录结构) [实取,2026-11-03] |
| 新证据↔旧观点自动关联(触发/匹配/呈现) | **不存在**(现行最接近物 = 量化触发器**人工登记**+引擎核验(a.1);P2 S-3"跟踪触发的再研究入口"为设计定稿、实现停泊 [实取·`docs/P2_DESIGN.md` L41,2026-11-03]) | 同上 grep |
| 预测错误模式复盘(归类/统计/反馈闭环) | **不存在**(现行裁决留痕 = predictions[].observations/resolved_note + 论点 history 散记,无跨预测统计载体) | 同上 grep;`config/allocation_views.json` L392-428 无统计字段 [实取,2026-11-03] |
| 报告质量持续优化循环(跨期评价维度+反馈) | **不存在**(现行 = Gate B 数值校验**即时门禁**(a.5),非跨期质量统计与优化循环) | 同上 grep |

---

## 面(b) 前序设计在场件(BASE 自带,本 checkout `docs/` 实读定位)

### b.1 E2E-B 设计三件(R014+R016 整体 PASS;前缀 P03_E2EB)

| 文件 | 用途(对本包) |
|---|---|
| `docs/P03_E2EB_QUERY_SURFACE_INVENTORY.md` | 五层查询入口行级盘点(fact_engine 17 个可查询实体 E1-E17 [实取·`docs/P03_E2EB_DELIVERY.md` L22 登记,2026-11-03];registry/快照/装配各层,该文件 L21 起实测表)——P3 检索面设计(DESIGN §3)的查询形态先例 |
| `docs/P03_E2EB_DESIGN.md` | 模式B架构设计: IR 字段级 schema/接地规则/四级缺席路径(ABSENT_REGISTRY/SOURCE/DATA/WINDOW)/共享档案衔接(query_id=QB-YYYYMMDD-NNN 等档键约定 §四)——P3 检索与关联的档键/缺席路径直接承接 |
| `docs/P03_E2EB_DELIVERY.md` | 交付与证据留档先例(双源副本/逐套件 CI 记录);实现包 WP-B1~B5(共 5 包 [实取·该文件 L23,2026-11-03])**停泊未执行** |

### b.2 P2 设计三件(R020 PASS;BASE=dev/p2-design 自带)

| 文件 | 用途(对本包) |
|---|---|
| `docs/P2_INVENTORY.md` | 深研基础设施五面盘点(快照/Gate A/装配/Gate B/状态保护)+缺口 P2-G-01~08(共 8 项 [实取·该文件 §已知缺口表清点,2026-11-03])——P3 多处引用其行级锚点 |
| `docs/P2_DESIGN.md` | §六 可反驳性与跟踪(L148-186;**结论状态机 L172-185**: 未裁决→部分支持/部分证伪→终态 CONFIRMED/FALSIFIED/EXPIRED_UNRESOLVED/INCONCLUSIVE+证伪后处置 3 条 L182-185)= **P3 §3 版本管理/结论状态机承接对象**;§七 实现包 4 包(WP-P2-A~D [实取·L189-217,2026-11-03])停泊未执行;§八红线 L221-228 |
| `docs/P2_DELIVERY.md` | 交付说明(R020 终态登记) |

### b.3 E2E-A(实现包停泊;引用一律注入摘要)

E2E-A 契约草案要点: 三模块 = 研究历史查询(只读对齐,禁直读原始档)/异常检测器(参数 echo=常量=登记三者一致)/研究任务管理器(schema 最低字段集含 falsifiable_conditions,append-only);回放纪律 = 真实历史双次运行;零网络。[全部为「注入摘要(2026-11-03),非工作树实读」;其实现包停泊,无交付件可引,本包不作实现级引用]

### b.4 GLM 研究结论层设计(R019 PASS;另支)

见面(d)。

---

## 面(c) 数据与积累面可得性

### c.1 registry / fact_engine 实读

- `config/metric_registry.json` L26(`"metrics"` 数组起): 指标总数 **81** [实取·`json.load` 后 `len(metrics)`=81 + `grep -c '"metric_id"'`=81,2026-11-03];criticality 分布 core 32/important 48/context 1(合计 81)[实取·python Counter,2026-11-03];status 分布 active 80/deprecated 1(合计 81)[实取·同上]。
- `scripts/fact_engine.py` L81-91(`compute_period_returns`): 全系统唯一收益口径,week/mtd/ytd/m1/m3/m6/m12 七窗口(基准=期前有效观测)[实取·七窗口=L84-88 及 L164-165(m12)枚举,2026-11-03];单位纪律 L89(价格→pct/利率→pp+bp/计数→绝对差);L90"数据不足→{"available": false, …},绝不回退0.0"。架构定位 v2 六层 L2 [实取·`docs/ARCHITECTURE_V2.md` L26-55,2026-11-03]。

### c.2 长期状态与档案数据面现行形态(实读)

| 数据面 | 现行形态 | 取证 |
|---|---|---|
| data/daily(DEV 副本) | 18 个文件 [实取·`ls data/daily \| wc -l`,2026-11-03] = 4 采集通道(china/global/macro/rate_economy)× 3 日(20261101/20261102/20261103)JSON 12 份 + global/rate_economy 两通道各 3 份人读 .md(每交易日 1 份,共 6 份,12+6=18 [实取·`ls` 逐项清点,2026-11-03]);**无 research_snapshot_*.json、无 anchors_*.json 于 DEV 工作树** | `data/` 整体 gitignored [实取·`.gitignore` L1 + `git check-ignore data/daily/china_20261103.json` 命中,2026-11-03];快照/锚点产出格式以 `scripts/snapshot_builder.py` L344-423 为准,长期积累于生产侧 LIVE(本包禁写) |
| research_snapshot 输出形态 | 结构 = snapshot_id/target_date/gate_a/facts/series_store 等(L344-382);同日修订 = _vN + revision_reason(L390-398) | [实取·`scripts/snapshot_builder.py`,2026-11-03] |
| thesis 状态结构要点 | 见 a.1(id/status/confidence/quant_triggers/history 等 13 类字段 [实取·`config/thesis.json` L6-60 逐字段清点,2026-11-03]) | history=字符串数组散记(L28-33),非结构化版本记录 |
| allocation_views 结构要点 | views: rating/confidence/evidence_for/evidence_against/triggers/quant_triggers(含 sustain_weeks)/invalidation/related_theses/history/key_metrics/proposals(引擎写入留档);predictions: pred_id/date_made/asset/direction/horizon_weeks/deadline/trigger/status/metric/comparator/target/evidence_ref/resolved_note/note/verify_mode/observations/data_source/premise_text(18 字段 [实取·`config/allocation_views.json` L393-412 逐字段清点,2026-11-03]) | [实取·同文件,2026-11-03] |

### c.3 P1 数据需求(跨支登记;另支,非工作树在场)

- 分支尖端: `dev/p1-design`@`049ec978523dec659ba47f140bf41669604de24f` [实取·`git ls-remote origin dev/p1-design`,2026-11-03T04:18:06Z]。
- 三件在场: docs/P1_DATA_NEEDS_INVENTORY.md / P1_DESIGN.md / P1_DELIVERY.md [实取·`git ls-tree FETCH_HEAD docs/`,2026-11-03]。
- 12 条候选指标清单(BOJ_POLICY_RATE/JGB_10Y/JGB_2Y/JP_CPI_TOKYO_YOY/NIKKEI225/ECB_DFR/ECB_MRO/BUND_10Y/BUND_2Y/EA_HICP_YOY/DAX/CAC40,共 12 条) [实取·跨支只读: git show FETCH_HEAD:docs/P1_DESIGN.md L62,dev/p1-design@049ec978523dec659ba47f140bf41669604de24f,2026-11-03;该文件自标"候选清单"非冻结];「现行 81+12 候选=93 目标」口径 [实取·注入摘要(2026-11-03);其中 81 与本工作树实读一致(c.1),12 为跨支实读候选、落地以 WP-P1-A 为准(同支原文)]。实现包 WP-P1-A..E 停泊未执行 [注入摘要(2026-11-03),非工作树实读]。

---

## 面(d) GLM 层与停泊实现面实况(ls-remote 实况)

- `git ls-remote origin dev/p03-w2-glm-design` [实取·2026-11-03T04:18:06Z] → `0c8de3c3bece78dd2d9f0d8928a817b597e3104e`。状态: **另支,设计定稿(R019 PASS),实现包 WP-G1~G4 停泊未执行**(WP-G1 结论层输入装配器/WP-G2 结构化输出契约与校验器/WP-G3 可反驳条件推导与门禁对接+档案衔接/WP-G4 真实调用接线(需用户批准/PENDING) [实取·跨支只读: git show FETCH_HEAD:docs/P03_W2_GLM_DESIGN.md L216-234,dev/p03-w2-glm-design@0c8de3c3bece78dd2d9f0d8928a817b597e3104e,2026-11-03])。
- 在场 GLM 调用链(周报层,非研究结论层): `scripts/report_generator.py` L574(`_call_glm`)。研究结论层 GLM = 设计定稿、实现停泊,本包仅能力级引用。
- **停泊实现面全清单**(均未执行;内部 schema 一律不得表述为已实现或已冻结运行事实): E2E-A(契约草案)、E2E-B WP-B1~B5(5 包 [实取·`docs/P03_E2EB_DELIVERY.md` L23,2026-11-03])、GLM WP-G1~G4(4 包 [实取·跨支只读,同上])、P1 WP-P1-A..E [注入摘要(2026-11-03),非工作树实读]、P2 WP-P2-A~D(4 包 [实取·`docs/P2_DESIGN.md` L189-217,2026-11-03])。

---

## 面(e) P3 外部约束(治理登记)

| # | 约束 | 内容与取证 |
|---|---|---|
| e.1 | 上游依赖漂移常态化 | dateutil 4.0.0 事件先例(2026-11-01 上游发布,移除 six 传递依赖→CI 全新环境缺失→workflow 补装 six) [注入摘要(2026-11-03),非工作树实读];在场证据: `.github/workflows/offline-tests.yml` L33 安装清单含 six + 文件头注释 L7-12(被测模块 import 面须安装真实依赖) [实取·本 checkout,2026-11-03] |
| e.2 | 免费数据源边界(预授权③) | 免费公开源直用+来源/降级标记,禁冒充权威源;付费/凭证报批 [注入摘要(2026-11-03),非工作树实读]。本包零新数据源 |
| e.3 | 层序规则 | 实现面按层序推进(上层实现面未关闭不开下层);设计与实现包预拟属准备面,可依用户跨阶段并行授权(2026-11-02)提前 [注入摘要·handover §4a 层序规则逐字块(2026-11-03),非工作树实读] |
| e.4 | 横切运行时验收两项 | ≥7 个真实计划执行日+≥1 次真实周报回归;30 天生产观察+计划任务成功率≥95%+≥4 次正式周报;日历时间不可压缩(LIVE 部署后尽早起算) [注入摘要·handover §4a 横切块逐字(2026-11-03),非工作树实读];执行载体属 R018 停泊件 [注入摘要(2026-11-03),非工作树实读] |
| e.5 | 长期状态批量修改须用户批准 | 治理不变量: 论点/观点/预测长期状态批量修改须用户批准 [注入摘要(2026-11-03),非工作树实读];单条状态变更的门禁机制在场(a.1),但"批量修改"无程序通道、须用户批准为治理红线 |

---

## 已知缺口(P3 视角;编号 P3-G-*,供 DESIGN §7 承接)

| # | 缺口 | 对应能力面 |
|---|---|---|
| P3-G-01 | 跨档案检索索引缺失(快照/报告/论点/预测/深研任务无统一检索面) | a.6 检索索引 |
| P3-G-02 | 研究结论级版本链与历史结论修正记录缺失(history 散记非结构化版本链) | a.6 版本管理 |
| P3-G-03 | 新证据↔旧观点自动关联缺失(触发/匹配/呈现三要素零载体) | a.6 自动关联 |
| P3-G-04 | 预测错误模式复盘方法论与统计载体缺失(裁决留痕散落,无归类/统计/反馈闭环) | a.6 错误模式复盘 |
| P3-G-05 | 报告质量跨期评价循环缺失(Gate B 为即时门禁,非跨期质量统计与优化) | a.6 质量优化循环 |
| P3-G-06 | #37 个人技术分析/投资研究流程整合零接口 | a.6(全缺) |
| P3-G-07 | 共享研究档案载体停泊(E2E-B WP-B4/P0-3 前置)——P3 检索/版本/关联多包的公共依赖 | a.3 |
| P3-G-08 | 历史数值引用观测日纪律在提示词层在场(L506),跨档案历史观察聚合面(按指标/时间拉通 observations)缺失 | a.2/c.2 |

(缺口 8 项 [实取·本表清点,2026-11-03];DESIGN §7 逐包承接见该节末尾核对行。)

---

## 跨分支登记(只读;ls-remote 实取 2026-11-03T04:18:06Z)

| 分支 | 尖端全SHA | 取证方式 |
|---|---|---|
| dev/p2-design(本包基线) | f8ed401f4274e158c06a9404149d41260e5cc0ad | git ls-remote + 开工校验(前 7 位 f8ed401) |
| dev/p03-w2-glm-design | 0c8de3c3bece78dd2d9f0d8928a817b597e3104e | git ls-remote;文件实读经 git show FETCH_HEAD(只读,未 checkout) |
| dev/p1-design | 049ec978523dec659ba47f140bf41669604de24f | 同上 |

---

*本盘点 docs-only,零代码/测试/配置改动;行级引用以本 checkout(基线 f8ed401)实码为准,偏差≤3 行可复核。*
