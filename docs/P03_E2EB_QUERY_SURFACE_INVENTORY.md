# P03 E2E-B 查询面盘点(QUERY SURFACE INVENTORY)

> 包: R014 · IA-P03-E2EB-DESIGN(P0-3 设计线第1包,docs-only)
> 基线: `1ddfb65ec78f4358b7a004be8ef5d8916ba0f052`(dev/p0-2-w5-fix3 尖端)
> 盘点分支: `dev/p03-e2eb-design`(自基线切出)
> 盘点时点: 2026-11-02(UTC) · 全部行级引用以本 checkout 实码为准,实测方法逐处注明
> 用途: 为模式B(用户自然语言研究)的 NL→查询映射设计提供**事实层依据**;已知缺口清单供 DESIGN §五承接

---

## 数值标注约定(全文适用)

- **[实取]** = 直接读自本 checkout 内真实文件,随注文件名与日期;
- **[实取·引擎]** = 由 fact_engine 离线运行于授权数据副本(data/daily 只读)计算所得,随注输入文件、as_of 与计算口径(计算为引擎代码确定性执行,非人工估算);
- **[示意]** = 非实取,仅示例。本文无 [示意] 数值。

---

## §一 五层查询入口盘点

### 层① 事实引擎 fact_engine — `scripts/fact_engine.py`(751行)

身份与口径的唯一权威。以下入口均为可编程查询面(函数/常量),离线纯函数,零网络。

| # | 实体名 | 类型 | 行号区间 | 查询用途 |
|---|---|---|---|---|
| E1 | `load_registry(path=None, force=False)` | 函数 | L43-72 | 加载并校验注册表;构建 `by_id` 索引(L51-58, L70) |
| E2 | `metric(metric_id)` | 函数 | L75-76 | 按 metric_id 查指标身份(unit/calendar/source/frequency等) |
| E3 | `compute_period_returns(dates, values, unit, calendar, as_of=None)` | 函数 | L81-174 | 统一收益引擎: week/mtd/ytd/m1/m3/m6/m12 七窗口;单位纪律(价格→pct,利率→pp+bp,计数→绝对差);**数据不足→`{"available": False, "reason": ...}`,绝不回退0.0**(L90, L94-95, L143, L155, L162, L173) |
| E4 | `parse_iso_date(s)` | 函数 | L182-193 | 严格完整ISO日期原语(非法输入→None,不截断洗白) |
| E5 | `make_fact(metric_id, value, observation_date, as_of, source_file, collector, ...)` | 函数 | L196-238 | 事实构造;fact_id=`{metric_id}@{obs}` (L211);携带source/calculation_ref/identity/quality_status |
| E6 | `_GLOBAL_ID_MAP` | 常量 | L244-245 | global通道资产ID→metric_id 映射(含 `"JPY=X": "USDJPY"`) |
| E7 | `normalize_global(data, as_of, source_file="global_*.json")` | 函数 | L247-272 | global_*.json → 事实列表;不在注册表的资产→FAIL诊断记录(L256-258) |
| E8 | `normalize_macro(data, as_of, source_file="macro_*.json")` | 函数 | L275-298 | macro_*.json → 事实;别名表 `_MACRO_ALIAS`(L281, 如 `WTI→WTI_SPOT_M`) |
| E9 | `normalize_china(data, as_of, source_file="china_*.json")` | 函数 | L301-392 | china_*.json → 事实;新旧采集格式双支持;未注册代码如实跳过(L341-345) |
| E10 | `normalize_rate(data, as_of, source_file="rate_economy_*.json")` | 函数 | L406-459 | rate_economy_*.json → (事实, 对账输入+期货曲线);非权威系列转reconciliation(L428-435) |
| E11 | `compute_derived(facts, as_of, source_file="derived")` | 函数 | L462-500 | 派生指标: REAL_10Y/REAL_5Y/HY_IG_DIFF/ZQ_IMPLIED_AVG/NFP_MOM_K——**派生公式硬编码于此**(L478-480, L484),非通用配对机制 |
| E12 | `validate_fact(fact, raw_item, m, as_of_date=None)` | 函数 | L513-636 | 12类校验: 类型/区间/时间/点时可得性/频率新鲜度/离群/连续性 |
| E13 | `grade_issues(issues)` / `SEVERITY_ORDER` | 函数/常量 | L505-510 | 质量分级 PASS/DEGRADED/FAIL(最严重定级) |
| E14 | `cross_metric_checks(facts)` | 函数 | L661-702 | 跨指标逻辑(目标区间次序/评级-利差次序/黄金双载体)+来源对账 |
| E15 | `build_all(global_data=None, macro_data=None, china_data=None, as_of=None)` | 函数 | L709-724 | 一站式规范化+派生+跨指标 → (facts, reconciliation);**注意: 不含rate通道**(rate由snapshot_builder单独接入,L286-289) |
| E16 | `snapshot_quality_grade(facts)` | 函数 | L727-744 | 快照整体分级(只统计active指标,L735) |
| E17 | `PRICE_LIKE_UNITS` / `RATE_UNITS` / `COUNT_UNITS` | 常量 | L33-38 | 单位语义→变化口径分派 |

配套模块(引擎依赖,查询语义相关):
- `scripts/freshness_policy.py`: `POLICY_APPROVAL` L37 / `build_policy(registry)` L341-369 / `set_policy` L370 / `policy_for(metric_id)` L393 / `compare_release_availability(release, as_of)` L226-337
- `scripts/trading_calendar.py`: `MARKETS` L30(7个日历) / `expected_trading_days(start, end, market, upto=None)` L107 / `last_session_on_or_before(d, dates)` L142 / `iso_week_bounds(d)` L162 / `months_before(d, n)` L179
- `scripts/registry_semantics.py`: `assert_registry_semantics(reg, source_desc)`(金融语义一致性,由load_registry生产调用,fact_engine.py L64)

### 层② 指标注册表 — `config/metric_registry.json`(2325行)

**结构与查指标方式**:
- 顶层键: `version`(L2, 实值 `"2.0.0"`[实取,本文件]) / `created`(L3) / `spec`(L4) / `field_semantics`(L5-20, unit与freshness语义) / `notes`(L21-25) / `metrics`(L26起,对象数组)
- 条目字段schema(以SPX首条 L28-54 为例): `metric_id` / `display_name` / `source` / `source_symbol` / `asset_class` / `frequency` / `unit` / `calendar` / `criticality` / `status` / `identity{instrument,adjustment}` / `value_type` / `calc` / `validation{range,max_week_pct_move}` / `freshness{max_calendar_lag_days}`
- **查指标方式**: `fact_engine.metric(metric_id)`(E2)经`load_registry()`的`by_id`索引(fact_engine.py L51-58, L70);也可直接对`metrics`数组线性过滤
- **实测指标总数: 81**[实取·实测: `python3 -c` 于本checkout执行 `len(json.load(open('config/metric_registry.json'))['metrics'])` = 81, 2026-11-02];构成: active 80 + deprecated 1(REAL_SHORT, L2211, status L2220);criticality分布: core 32 / important 48 / context 1;首条SPX L28,末条JTSJOL L2297
- E2E-B场景相关条目(行号为该条目`metric_id`行):

| metric_id | display_name | 行号 | unit | source | criticality | status |
|---|---|---|---|---|---|---|
| USDJPY | 美元兑日元 | L445-467 | jpy_per_usd | global_market_collector | important | active |
| EWJ | iShares日本ETF | L815 | usd | global_market_collector | important | active |
| UST_2Y | 2年期美债收益率 | L933 | percent | macro_collector | core | active |
| UST_10Y | 10年期美债收益率 | L991 | percent | macro_collector | core | active |
| TIPS_10Y | 10年期TIPS实际收益率 | L1223 | percent | macro_collector | core | active |
| CURVE_2S10S | 2s10s期限利差 | L1310 | percentage_point | macro_collector | core | active |
| FED_FUNDS | 有效联邦基金利率(月均) | L1339 | percent | macro_collector | context | active |
| DFF | 有效联邦基金利率(日频) | L1729 | percent | rate_expectations | core | active |
| DFEDTARU | 联邦基金目标区间上限 | L1758 | percent | rate_expectations | core | active |
| DFEDTARL | 联邦基金目标区间下限 | L1783 | percent | rate_expectations | core | active |
| ZQ_F1_PRICE | 30天联邦基金期货主力价格 | L1807 | points | rate_expectations | important | active |
| REAL_10Y | 10年期实际利率(近似) | L2155 | percent | fact_engine(derived) | core | active |
| ZQ_IMPLIED_AVG | 联邦基金期货隐含当月日均利率 | L2269 | percent | fact_engine(derived) | core | active |

**日本侧身份在场性(实测)**: 对全注册表JSON字符串检索 `JGB`/`BOJ`/`日本` —— 除 USDJPY(汇率)与 EWJ(日本股票ETF)外**零命中**;即: **日本政策利率(日银目标)与JGB各期限收益率均不在81指标注册表内**[实取·实测,2026-11-02]。

### 层③ 研究快照 — `scripts/snapshot_builder.py`(569行)+ `scripts/research_provenance.py`

**构建入口**:
| # | 实体名 | 类型 | 行号区间 | 说明 |
|---|---|---|---|---|
| S1 | `build_snapshot(target_ymd, data_dir, out_dir, as_of, write, allow_revision, revision_reason, trusted_root)` | 函数 | snapshot_builder.py L236-438 | 唯一快照构建入口;as_of可注入确定性研究截止(L545-546 CLI对应) |
| S2 | `resolve_inputs(target_ymd, data_dir=None, trusted_root=None)` | 函数 | snapshot_builder.py L47-101 | 采集文件解析: 精确匹配优先→新鲜度窗内fallback并显式披露;可信边界核验(FIX7/8) |
| S3 | `build_anchors(snapshot, ymd)` | 函数 | snapshot_builder.py L121-231 | 快照事实→旧格式锚点(兼容桥) |
| S4 | `render_markdown(snap)` | 函数 | snapshot_builder.py L459-527 | 人读版确定性渲染 |
| S5 | CLI `__main__` | 脚本入口 | snapshot_builder.py L530-569 | `--date/--data-dir/--trusted-root/--out-dir/--allow-revision/--revision-reason/--as-of`;Gate A FAIL→exit 2,不可变拒绝→exit 3 |

**不可变语义**: 同日快照已存在→拒绝覆盖(L389-392);`--allow-revision`→生成`_v2`修订版并保留原版+修订原因(L393-398);原子写tmp+replace(L399-403)。

**快照内字段(build_snapshot产出dict, L344-357)**:
`snapshot_id`(格式`research_snapshot_{YYYYMMDD}[_vN]`,L345/L397) / `research_as_of`(ISO时间戳,默认UTC+8当前时刻,L243-245) / `target_date` / `timezone`(恒`"Asia/Shanghai"`,L348) / `sources_status`(逐通道EXACT/FALLBACK/MISSING/READ_FAIL+sha256,L256-269) / `fed_futures_curve` / `facts`(事实记录数组,结构=fact_engine.make_fact产物) / `reconciliation` / `quality`(snapshot_quality_grade) / `gate_a`(status/core_missing/core_fail/noncore_fail/noncore_missing/noncore_degraded/note,L316-342) / `notes`;可选`series_store`(L358-382,相关性等配对序列研究用,键=注册表metric_id,值=采集器series{dates,values});修订版加`revision_reason`(L398)。

**可读取面(下游查询入口)**:
| # | 实体名 | 位置 | 行号区间 | 说明 |
|---|---|---|---|---|
| R1 | `select_snapshot(ymd, daily_dir)` | research_provenance.py | L1243-1294 | 确定性版本选择: 同日多版取最高修订版;候选损坏/身份冲突→明确拒绝不猜测 |
| R2 | `gate_status(snapshot, data_dir, trusted_root)` | research_provenance.py | L1101-1182 | 下游复算Gate A状态(与写入时同源口径) |
| R3 | `gate_allows_formal_research(status)` | research_provenance.py | L1183-1188 | PASS/DEGRADED放行正式研究,FAIL/None拒绝 |
| R4 | `recompute_gate_a(snapshot, ...)` | research_provenance.py | L853-1100 | 从事实重算Gate A(写入时调用,快照声明与事实不可矛盾) |
| R5 | `digest_snapshot(snapshot)` | research_provenance.py | L1297-1301 | 快照内容指纹(sha256前16位,canonical JSON) |
| R6 | `SOURCE_FILE_RULES` / `canonical_source_file(channel, file)` | research_provenance.py | L152-157 / L162-185 | 通道规范文件名单一权威(prefix+8位真实日历日期);snapshot_builder.SOURCES由此推导(snapshot_builder.py L43-44) |
| R7 | `combine_gates(gate_a, gate_b)` | research_provenance.py | L1533 | Gate A×B合成 |

**快照消费范式(基线在场)**: data_assembler.load_snapshot(data_assembler.py L37-44)与macro_scorecard.load_snapshot(macro_scorecard.py L39-50)均经R1读取;`__main__`流水线编排run_weekly.py `run_pipeline`(run_weekly.py L64, L101)。

**本checkout快照在场性(实测)**: `data/daily/`共12个文件——china/global/macro/rate_economy各2日(20261101/20261102)JSON+3个人读md,**无任何已持久化`research_snapshot_*.json`**[实取·实测`ls`,2026-11-02];即DEV仓快照层=构建/选择代码面在场、数据档缺席(生产快照在LIVE侧,本包禁写)。离线构建可行性由 tests/test_snapshot.py(基线在场)背书。

### 层④ 数据档 data/daily — 文件命名/字段/日期与时区口径

**命名规范**(R6单一权威): `{channel}_YYYYMMDD.json`,通道与回退窗: `global_`5天 / `macro_`7天 / `china_`5天 / `rate_economy_`7天(research_provenance.py L153-156);目录/符号链接/伪装前后缀/非真实日历日期一律非规范(L162-185)。

**字段结构(逐通道实取, 2026-11-02, 以`*_20261102.json`为样本)**:
- `global_20261102.json`: 顶层`date`/`time`/`count`/`data`;`data`按资产ID键控(32个资产,含`JPY=X`);每资产: `asset_id`/`close`/`high`/`low`/`week_chg`/`mtd_chg`/`ytd_chg`/`vs_50d`/`vs_200d`/`date`(观测日YYYY-MM-DD)/`series{dates[],values[]}`;USDJPY样本: close=157.8, 观测日2026-10-30, series 260个观测[实取,本文件]。**注意**: 采集器自带的`week_chg/mtd_chg/ytd_chg`为采集器口径,研究口径一律以fact_engine.compute_period_returns(E3)重算为准(引擎统一收益原则,fact_engine.py L82注释)
- `macro_20261102.json`: 顶层`date`/`data`/`alerts`/`derived`;`data`按序列名键控(26个: HY_OAS…JTSJOL);每序列: `value`/`date`/`series{dates,values}`等;UST_2Y=4.61@2026-10-29, UST_10Y=4.98@2026-10-29[实取,本文件]
- `china_20261102.json`: 顶层`timestamp`/`version`/`a_share_indices`/`hk_indices`/`southbound`/`margin`/`valuation`/`turnover`/`ah_premium`(新旧格式双支持见E9)
- `rate_economy_20261102.json`: 顶层`date`/`fed_funds_futures`/`current_rates`/`real_economy`/`rate_expectations`/`generated_at`;`current_rates`: FEDFUNDS=3.75@2026-09-01, DFF=3.88@2026-10-29, DFEDTARU=4.0@2026-11-01, DFEDTARL=3.75@2026-11-01[实取,本文件];`fed_funds_futures`9行,首行ZQ=F价格96.12[实取,本文件]

**日期与时区口径**:
- 文件内观测日: ISO `YYYY-MM-DD`(global/macro)或紧凑`YYYYMMDD`(部分通道,由`fact_engine._iso`/`make_fact`归一,fact_engine.py L207-209, L397-403)
- 研究截止`research_as_of`: ISO时间戳,默认`datetime.now(TZ_BJ)`(UTC+8,snapshot_builder.py L37, L243-245);快照`timezone`恒`Asia/Shanghai`(L348)
- 新鲜度语义: 注册表`freshness.max_calendar_lag_days`(观测日距研究截止最大自然日滞后,超出→DEGRADED,registry L18;生效政策经freshness_policy单一来源)
- 点时可得性: `release_date`透传+`compare_release_availability`(freshness_policy.py L226),as_of时点不可得→FAIL(fact_engine.py L574-580)

### 层⑤ 装配/评分/相关性层(基线分支在场部分)

**装配**: `scripts/data_assembler.py`(358行)
| # | 实体名 | 类型 | 行号区间 | 说明 |
|---|---|---|---|---|
| A1 | `load_snapshot(date_str=None)` | 函数 | L37-44 | 经R1读取快照(不自动构建) |
| A2 | `latest_before(pattern, ymd, max_lag=10, data_dir=None)` | 函数 | L47-61 | 指定日期前最新匹配文件(评分卡/相关性/新闻上下文挂载用) |
| A3 | `scorecard_state(ymd, data_dir=None)` | 函数 | L68-79 | 评分卡当日性判定(仅当日评分=本期有效研究) |
| A4 | `build_markdown(snapshot, ymd, data_dir=None, trusted_root=None)` | 函数 | L123-306 | 快照→GLM数据包md(数值表程序确定性生成;Gate A=DEGRADED→逐项降级披露L164-174;非核心缺失披露L145-148) |
| A5 | `main()` | 函数 | L309-354 | Gate A检查(R2/R3)→拒绝FAIL生成;数据包+meta sidecar(包↔快照digest绑定) |

**评分**: `scripts/macro_scorecard.py`(567行)
| # | 实体名 | 类型 | 行号区间 | 说明 |
|---|---|---|---|---|
| M1 | `DATA_INSUFFICIENT` / `MIN_AVAILABLE_PER_DIM` | 常量 | L30/L31 | "数据不足不可判";每维度≥2可用指标才给体制结论 |
| M2 | `load_snapshot(date_str=None, data_dir=None)` | 函数 | L39-50 | 快照接入(Layer 3→4唯一数据入口) |
| M3 | `fact_of(facts, metric_id)` | 函数 | L53-57 | 事实按metric_id查找 |
| M4 | `_derived(fact, period, field)` | 函数 | L70-80 | 引擎派生取数(m1/m3/m12,按单位取pct/pp/abs;不可用→None+原因) |
| M5 | `score_growth(facts)` / `score_inflation(facts)` | 函数 | L92-179 / L180-266 | 增长/通胀维度评分(missing≠0,缺失如实记录) |
| M6 | `determine_regime(g_total, i_total)` / `resolve_transition(...)` / `attribute_regime(...)` | 函数 | L271-302 / L303-334 / L357-378 | 体制映射v2.0/两周确认/敏感性分析 |
| M7 | `save_scorecard(...)` / `render_markdown(result)` / `main(date_str, data_dir)` | 函数 | L383-459 / L471-521 / L525-567 | 评分卡落盘(含data_basis)/渲染/入口 |

**相关性**: `scripts/correlation_calculator.py`(167行)
| # | 实体名 | 类型 | 行号区间 | 说明 |
|---|---|---|---|---|
| C1 | `PAIRS` | 常量 | L28-46 | **固定10对**(SPX-TLT…BTC-NDX);**不含任何USDJPY配对**(实测: 该常量内字符串`USDJPY`/`JPY`零出现);配对按注册表metric_id+披露字段定义 |
| C2 | `load_series_store(snapshot)` | 函数 | L49-50 | 快照series_store读取 |
| C3 | `paired_returns(series_a, series_b)` | 函数 | L53-66 | 共同观测日内连接→收益率对(<3样本→None) |
| C4 | `pearson(xs, ys)` | 函数 | L69-80 | 皮尔逊相关(<3样本/零方差→None) |
| C5 | `compute_all(snapshot)` | 函数 | L83-106 | 逐对计算;序列缺失→missing披露清单(不内插不冒充) |
| C6 | `generate_markdown(results, missing, as_of_str)` / `main(snapshot_path, out_path)` | 函数 | L113-141 / L144-163 | 渲染(相关性≠因果声明)/入口(经R1选快照) |

**报告层(边界参考,非查询面)**: `scripts/report_generator.py` — `verify_research_inputs` L612 / `validate_generated_report` L1243 / `write_report_status` L803 / `generate_weekly_report` L1328(Gate B与论点状态保护属该层,本包不展开)。

---

## §二 已知缺口(模式B查询需要而当前没有;供DESIGN §五承接)

| 编号 | 缺口 | 实测依据 | 对模式B的影响 |
|---|---|---|---|
| G-01 | **日本利率侧身份缺席**: 日本政策利率(日银目标)与JGB各期限收益率均不在注册表(81指标中日本相关仅USDJPY汇率+EWJ股票ETF) | §一层②日本侧在场性实测 | E2E-B场景"美日政策利率差/收益率差"的**日端**无法取数——差距登记为合法路径,但场景完整性依赖后续数据包 |
| G-02 | **无自然语言查询面**: 不存在NL解析器/中间表示/问题→指标映射的任何代码实体;现有入口全部为Python函数/CLI(§一五层清单) | §一全表 | 模式B的核心层整体缺席,需从零设计(DESIGN §三) |
| G-03 | **无查询期通用配对派生机制**: compute_derived公式硬编码(REAL_10Y/REAL_5Y/HY_IG_DIFF/ZQ/NFP_MOM_K五族,fact_engine.py L478-499);"任意两指标求差"无入口 | E11实测 | "美日利率差"类问题即使双侧数据在场,也无标准带calculation_ref的查询期求差机制 |
| G-04 | **相关性配对固定**: PAIRS恰10对且无USDJPY配对;无按需配对查询入口;但USDJPY序列数据在场(series_store可含,§一层③L358-382+global通道实测260观测) | C1实测 | "USDJPY与X的相关性"类问题无现成计算面(数据在,配对面不在) |
| G-05 | **DEV侧无持久化快照**: 本checkout data/daily零`research_snapshot_*.json`;快照层只有构建/选择代码面 | §一层③在场性实测 | 模式B查询执行器的DEV测试需先离线构建快照(write=False路径,L384-385)或依赖LIVE产出(禁写,只可读副本) |
| G-06 | **无共享研究档案/查询历史存储**: 无query/task持久化实体;E2E-A三模块(research_history_query/anomaly_detector/research_task_manager)不在基线 | §一全表零命中 | 两模式共享研究档案的衔接(快照ID/任务ID引用)无落点,需与E2E-A对齐设计(DESIGN §四) |
| G-07 | **历史as_of查询语义部分在场**: build_snapshot/normalize_*均接受as_of注入(S1, L545-546;E3/E5),resolve_inputs支持任意target_ymd(S2);但无"过去某日快照不存在时如何时点作答"的模式B显式语义与测试 | §一层①③ | "截至X日"类历史问题需显式语义(时点作答vs拒答),防事后数据混入 |
| G-08 | **答案接地强制机制缺席(模式B专用)**: 数据包/报告层有程序确定性渲染(A4)与Gate B,但无"回答中数值必携来源标识"的查询级模板/校验实体 | §一层⑤ | 模式B作答层的接地红线需要机制落点(DESIGN §三(b)) |

---

## §三 跨分支登记(不承担行级引用义务,不纳入AC-01核验面)

数据线并行分支的工具产物可作模式B实现期辅助(均已验证为可达commit对象,`git ls-remote origin`实取2026-11-02):

- 分支 `dev/data-inventory` @ `7cbef4c9bd25586ef03fc02819ae6792d0929fa0`: `scripts/data_inventory.py` — data/daily三元组独立哈希对照/盘点/diff工具
- 分支 `dev/data-coverage` @ `06f715b6be34dedd69f6776b1947238708de0563`: `scripts/metric_coverage_audit.py` — registry 81条全量覆盖审计(8机械状态/引擎读侧映射反推/债务清单: MARGIN_BAL、SH_PE、china通道7指标、FED_FUNDS单日缺席等)

---

*本盘点为设计输入事实层;判断与方案见 `docs/P03_E2EB_DESIGN.md`;交付说明见 `docs/P03_E2EB_DELIVERY.md`。*
