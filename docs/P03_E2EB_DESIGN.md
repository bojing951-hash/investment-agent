# P03 E2E-B 架构设计(DESIGN) — 模式B自然语言研究入口

> 包: R014 · IA-P03-E2EB-DESIGN(P0-3 设计线第1包,docs-only 零代码)
> 基线: `1ddfb65ec78f4358b7a004be8ef5d8916ba0f052`(dev/p0-2-w5-fix3 尖端)
> 设计分支: `dev/p03-e2eb-design`
> 事实依据: `docs/P03_E2EB_QUERY_SURFACE_INVENTORY.md`(下称 INVENTORY;行级引用以该checkout实码为准)
> 状态: 架构设计定稿候选;§六验收要点为**草案**(正式AC由主Agent后续轮拟定,本包不冻结)

**数值标注约定(全文适用,二选一)**: **[实取]**=读自本checkout真实文件或由fact_engine离线确定性运行于授权数据副本所得(随注输入文件+日期/研究截止,公式由引擎代码执行,非人工估算);**[示意]**=非实取示例,显式标注。schema示例中的ID字符串(如`QB-20261102-001`)为标识符非数据值。

---

## §一 目标与边界

**模式B定义**: 用户以自然语言提问 → 系统映射为对**事实层/快照层**的结构化查询 → 复用 fact_engine 统一口径**独立计算** → 接地作答。禁止模型直叙无数据支撑的结论;数据缺席=如实「无数据」;禁编造;禁「数据不足填0」。

**验证场景 E2E-B = 美日政策分化与 USDJPY**: 用户问美日政策利率差/收益率差变化与USDJPY走势关系类问题。数据在场性(INVENTORY实测): 美端政策利率与收益率**在场**(DFEDTARU/DFEDTARL/DFF/UST_2Y/UST_10Y等13条注册身份);USDJPY**在场**(注册L445-467+global通道260观测序列);**日端利率缺席**(JGB/日银目标不在81指标,INVENTORY G-01)——缺席是差距清单合法内容,不是设计障碍。

**In-scope(本设计覆盖)**: ①中间表示(IR)字段级schema ②NL→IR映射层架构 ③查询执行器(快照绑定+引擎口径复用+查询期派生) ④接地规则与缺席路径 ⑤E2E-B端到端走查 ⑥E2E-A对齐与共享研究档案衔接 ⑦差距→工作包映射。

**Out-of-scope(后续包)**: GLM提示词工程与作答语言层细化 / Gate B细化 / E2E-A实现 / 新数据源实际采集与注册表变更 / 任何代码改动(本包docs-only)。

---

## §二 盘点引用与决策点

### 2.1 盘点引用

- 事实引擎查询面: INVENTORY §一层①(E1-E17, fact_engine.py)
- 注册表结构与实测81指标: INVENTORY §一层②
- 快照构建/读取面与不可变语义: INVENTORY §一层③(S1-S5, R1-R7)
- data/daily命名/字段/时区口径: INVENTORY §一层④
- 装配/评分/相关性层: INVENTORY §一层⑤(A1-A5, M1-M7, C1-C6)
- 已知缺口: INVENTORY §二(G-01~G-08)
- 跨分支工具登记: INVENTORY §三

### 2.2 登记型决策点(候选项+选定规则)

| # | 决策点 | 候选 | 选定 | 规则/依据 |
|---|---|---|---|---|
| D1 | 查询数据入口 | (a)直读data/daily (b)快照/事实层 | **(b)** | 架构v2红线"新研究模块必须走快照+门禁,禁止绕开直读原始文件";E2E-A research_history_query同款禁直读约束;机制落点=R1 `select_snapshot`+R3 `gate_allows_formal_research` |
| D2 | 数值计算口径 | (a)GLM自行从数据叙述 (b)复用fact_engine统一口径独立计算 | **(b)** | 模式B定义"真实数据+独立计算,非模型直叙";落点=E3 `compute_period_returns`/E11 `compute_derived` |
| D3 | 跨指标求差(利率差类) | (a)预先注册每个组合为派生指标 (b)查询期计算+calculation_ref | **(b)为主,(a)用于高频稳定组合** | (a)随组合数爆炸且需注册表变更流程;(b)对齐引擎派生纪律(E11同款calculation_ref);落点=IR `derived_operations[]`(§三(a));承接GAP-03 |
| D4 | USDJPY数据来源 | (a)global通道既有series(INVENTORY层④实测在场) (b)新采集通道 | **(a)** | `_GLOBAL_ID_MAP`"JPY=X"→USDJPY(fact_engine.py L244-245)既有身份;日端利率缺席走差距GAP-01而非绕道 |
| D5 | 缺席输出 | (a)空值/0 (b)结构化NO_DATA(available:false+reason) | **(b)** | 对齐引擎E3数据不足语义(`{"available": False, "reason": ...}`绝不回退0.0)与macro_scorecard `DATA_INSUFFICIENT`(M1);承接GAP-08 |
| D6 | 历史时点查询 | (a)拒绝一切历史问题 (b)显式as_of透传+快照时点锚定 | **(b)** | S1/E3/E5既有as_of注入面;只读锚定对齐E2E-A真实历史回放纪律;承接GAP-07 |
| D7 | 查询历史存储 | (a)可变数据库 (b)append-only日志 | **(b)** | 对齐研究任务append-only语义(E2E-A摘要);落点=§四`query_history` |

---

## §三 NL→查询映射

### (a) 中间表示(StructuredResearchQuery IR)字段级schema

```text
StructuredResearchQuery = {
  query_id:            string           # 标识符,格式 QB-YYYYMMDD-NNN(模式B查询记录)
  created_at:          string           # ISO8601时间戳(UTC+8),查询受理时刻
  mode:                string           # 恒 "B"(字面量;区别于模式A任务)
  question_text:       string           # 用户原始自然语言问题(原样保留)
  as_of:               string | null    # 研究截止(ISO日期或时间戳);null=绑定最新可用快照
  target_snapshot_id:  string | null    # 解析后绑定的快照ID(research_snapshot_YYYYMMDD[_vN]);null=未绑定(见缺席路径)
  metric_bindings:     list[MetricBinding]
  derived_operations:  list[DerivedOperation]
  unresolved_entities: list[UnresolvedEntity]   # 映射失败的NL指称,如实上浮
  answer_constraints:  { grounding_required: true,     # 接地强制(见(b))
                         no_data_policy: "report_absence" }  # 缺席策略(见(c))
}

MetricBinding = {
  binding_id:       string      # 绑定标识符,如 MB-1
  metric_id:        string      # 注册表身份(config/metric_registry.json metric_id)
  role:             string      # "level" | "derived_window" | "spread_component" | "correlation_series"
  window:           string|null # "week"|"mtd"|"ytd"|"m1"|"m3"|"m6"|"m12"(role=derived_window时必填)
  field:            string|null # "value"|"pct_change"|"pp_change"|"bp_change"|"abs_change"(单位纪律见E3)
  status:           string      # "RESOLVED"|"ABSENT_REGISTRY"|"ABSENT_SOURCE"|"ABSENT_DATA"|"ABSENT_WINDOW"
  absence_reason:   string|null # 引擎/注册表/通道给出的原样原因(见(c))
  provenance: Provenance | null # status=RESOLVED时必填
}

Provenance = {
  metric_id:        string    # 与binding一致
  snapshot_id:      string    # 值来源快照(不可变批次)
  fact_id:          string    # 格式 metric_id@YYYY-MM-DD(E5 L211)
  observation_date: string    # ISO观测日
  source_file:      string    # 采集文件名(披露用;查询器不直接读它——D1)
  quality_status:   string    # PASS|DEGRADED|WARN|FAIL(事实质量,E13)
  calculation_ref:  string|null  # 派生值公式/基准日/窗口(E5;查询期派生=D3落点)
}

DerivedOperation = {
  op_id:          string   # 如 OP-1
  op_type:        string   # "spread"(两水平求差)| "level_diff"(同指标两时点差)| "correlation"(两序列相关)
  operands:       list[string]   # binding_id 引用列表
  formula:        string   # 人类可读公式(如 "UST_10Y − UST_2Y")
  unit:           string   # 结果单位(利率差→percentage_point;E3单位纪律)
  status:         string   # "COMPUTED" | "NO_DATA"(任一operand缺席或窗口不可用)
  result:         number | null   # status=COMPUTED时为引擎/确定性算术结果
  calculation_ref: string  # 对齐E11纪律(公式+输入观测日+期限匹配)
}

UnresolvedEntity = {
  mention:         string   # 问题中未能映射的指称原文
  mapping_status:  string   # "no_registry_identity"|"ambiguous"|"out_of_scope"(禁交易/仓位类等)
  note:            string   # 处置说明(如实告知,不猜映射)
}
```

映射层职责(NL→IR): 词法/实体识别 → 候选指标检索(注册表`display_name`/`calc`/别名,经E2) → 窗口与字段解析(对齐E3口径词表) → 绑定或如实登记`unresolved_entities`。映射器**只产IR,不取数**;一切数值由执行器从快照/引擎取得(D2)。

### (b) 接地规则(进入回答的数值必携来源标识)

1. 任何进入回答的数值必须携带以下来源标识**之一以上**: ①`metric_id`(+`fact_id`) ②快照字段路径(`snapshot_id`+字段名,如`facts[].value`/`series_store.{mid}`) ③数据文件+观测日期(`source_file`+`observation_date`,披露用)。
2. 派生/计算值必附`calculation_ref`(公式+输入观测日;D3/E11同款纪律)。
3. 回答渲染层执行**接地强制**: 模板只接受携带`provenance`的数值节点;无来源标识的数值节点=渲染失败(fail-closed),不降级为无源输出。落点机制名: `answer_constraints.grounding_required`(IR) + 渲染校验(WP-B5工件)。
4. 质量传导: `quality_status`非PASS的事实进入回答时必须随附降级披露(对齐A4降级披露纪律,INVENTORY层⑤)。

### (c) 数据缺席路径(输出「无数据」而非编造;与"数据不足不填0"一致)

四级缺席,全部结构化输出、**零填0**:

| 级别 | IR落点 | 触发 | 回答表现 |
|---|---|---|---|
| A1 指标不在注册表 | `metric_bindings[].status="ABSENT_REGISTRY"` | E2查无身份(如"JGB 10Y") | "该指标不在注册表(无身份定义),无法取数" |
| A2 通道源失败 | `"ABSENT_SOURCE"` | 注册在场但快照`sources_status`对应通道MISSING/READ_FAIL | "指标已注册但当日采集缺失" |
| A3 数据缺席 | `"ABSENT_DATA"` | 快照facts无该metric_id(如FED_FUNDS某日缺席,跨分支覆盖审计已见同类) | "本期无该指标事实" |
| A4 窗口不足 | `"ABSENT_WINDOW"` | E3返回`{"available": False, "reason": ...}`(如序列不足N个月) | 原样转述引擎reason |

派生操作任一operand缺席→`DerivedOperation.status="NO_DATA"`,`result=null`,**不部分计算不近似**。回答文本对缺席项显式声明「无数据」;禁止以相近指标冒充、禁止内插、禁止填0。此口径与E3 L90/L94-95、M1 `DATA_INSUFFICIENT`、C5 missing清单三处既有实现同源。

### (d) E2E-B端到端走查(美日政策分化与USDJPY)

**第一环·自然语言问题**:
> "美日政策利率差和10年期国债收益率差最近怎么样?和美元兑日元走势合起来看是什么状态?"

**第二环·中间表示(关键节点摘录,IR全文按§三(a)schema)**:
- `as_of=null`(用户未指定时点→绑定最新可用快照;本走查以DEV授权副本离线等价执行,研究截止=2026-11-02T12:00:00+08:00,下称[as_of])
- `metric_bindings`: MB-1 DFEDTARL(level)/ MB-2 DFEDTARU(level)/ MB-3 DFF(level)/ MB-4 UST_2Y(level)/ MB-5 UST_10Y(level)/ MB-6 CURVE_2S10S(level)/ MB-7 USDJPY(level+derived_window week/ytd)/ MB-8 日本政策利率(role=spread_component)/ MB-9 JGB_10Y(role=spread_component)
- `derived_operations`: OP-1 spread(美日政策利率差=MB-8−(MB-1+MB-2)/2中值,unit=percentage_point) / OP-2 spread(美日10Y收益率差=MB-9−MB-5,unit=percentage_point) / OP-3 spread(美端2s10s=MB-5−MB-4,查询期计算对照注册值MB-6)

**第三环·指标清单与第四环·逐指标处置**(值均为fact_engine离线确定性运行于`data/daily/*_20261102.json`授权副本[实取·引擎,as_of 2026-11-02T12:00:00+08:00],观测日与质量为引擎产出):

| 绑定 | 指标 | 处置 | 值与来源标识 |
|---|---|---|---|
| MB-1 | DFEDTARL | **在场→实取值+引用** | 3.75 percent @2026-11-01, PASS; fact DFEDTARL@2026-11-01; 源文件 rate_economy_20261102.json [实取·引擎] |
| MB-2 | DFEDTARU | 在场→实取值+引用 | 4.0 percent @2026-11-01, PASS; fact DFEDTARU@2026-11-01; 同源文件 [实取·引擎] |
| MB-3 | DFF | 在场→实取值+引用 | 3.88 percent @2026-10-29, PASS; fact DFF@2026-10-29; 同源文件 [实取·引擎] |
| MB-4 | UST_2Y | 在场→实取值+引用 | 4.61 percent @2026-10-29, PASS; 周−0.08pp(基准2026-10-23), YTD+1.14pp; fact UST_2Y@2026-10-29; 源 macro_20261102.json [实取·引擎] |
| MB-5 | UST_10Y | 在场→实取值+引用 | 4.98 percent @2026-10-29, PASS; 周−0.02pp(基准2026-10-23), YTD+0.80pp; fact UST_10Y@2026-10-29; 同源 [实取·引擎] |
| MB-6 | CURVE_2S10S | 在场→实取值+引用 | 0.38 pp @2026-10-30, PASS; 周+0.07pp; fact CURVE_2S10S@2026-10-30; 同源 [实取·引擎] |
| MB-7 | USDJPY | 在场→实取值+引用 | 157.8 jpy_per_usd @2026-10-30, PASS; 周+0.8371%(基准2026-10-23), MTD+0.2541%(基准2026-09-30), YTD+0.8893%(基准2025-12-31); fact USDJPY@2026-10-30; 源 global_20261102.json [实取·引擎] |
| MB-8 | 日本政策利率 | **缺席→差距登记** | status=ABSENT_REGISTRY; absence_reason="日本政策利率不在注册表(81指标,INVENTORY G-01)"; 回答表现=「无数据」; 不以DFF或任何值冒充 |
| MB-9 | JGB_10Y | 缺席→差距登记 | status=ABSENT_REGISTRY; 同G-01; 「无数据」 |
| OP-1 | 美日政策利率差 | **NO_DATA** | 任一operand(MB-8)缺席→不部分计算; result=null [规则§三(c)] |
| OP-2 | 美日10Y收益率差 | NO_DATA | operand MB-9缺席; result=null |
| OP-3 | 美端2s10s(查询期) | COMPUTED | 4.98−4.61=0.37 pp; calculation_ref="UST_10Y − UST_2Y @观测日2026-10-29(期限匹配,查询期计算)"; 输入均[实取·引擎]; 与注册指标MB-6(0.38pp@2026-10-30)差异源于观测日不同(10-29 vs 10-30),回答中并注两个口径不混同 |

**接地作答样例骨架(渲染层输出形态,节选)**:
> 美端: 联邦基金目标区间 [3.75, 4.0] percent(DFEDTARL/DFEDTARU @2026-11-01, PASS, rate_economy_20261102.json);有效联邦基金利率 3.88 percent(@2026-10-29)。美债10Y 4.98、2Y 4.61 percent(@2026-10-29),查询期2s10s=0.37 pp(calculation_ref见OP-3;注册口径CURVE_2S10S=0.38 pp@2026-10-30)。
> USDJPY: 157.8(@2026-10-30,周+0.84%、YTD+0.89%)。
> **日端: 日本政策利率与JGB 10Y不在注册表——无数据**(ABSENT_REGISTRY);"美日政策利率差/收益率差"不可计算(NO_DATA)。已登记差距GAP-01;在本差距修复前,任何"美日分化"表述只能基于美端单侧事实,不得推断日端。

走查四环(问题→中间表示→指标清单→逐指标处置)完整闭环;缺席链路(A1级+NO_DATA)在场景内真实触发并如实呈现——这正是E2E-B场景对"缺席=合法路径"的验证价值。

---

## §四 E2E-A 对齐(基线=注入摘要;最终准据=引擎冻结版 IA-P03-W1-E2EA-AC-v1.0,冲突由后续包登记型修订承接)

| # | E2E-A要素 | 处置 | 字段/机制级落点 |
|---|---|---|---|
| 1 | `research_history_query` 模块 | **沿用+扩展** | 沿用: 其禁直读约束(E2E-A摘要"禁直读原始数据档,必须经快照/事实层")与模式B D1完全同构;扩展: 模式B `metric_bindings[].provenance.snapshot_id/fact_id`复用同一快照寻址面(R1 `select_snapshot`),`source_file`仅作披露字段从事实透传,查询器无直读路径(IR schema明示) |
| 2 | `anomaly_detector` | **分歧(不依赖)+衔接** | 模式B默认不触发异常检测(回答型,非监测型);衔接机制: 若E2E-A异常事件以`metric_id+snapshot_id`落档,模式B经`metric_bindings`同键可回查该事件上下文——互操作键=`metric_id`+`snapshot_id`(两模式IR/事件档共用该二元组) |
| 3 | `research_task_manager` | **分歧(默认不建任务)+单向升级** | 模式B默认无状态作答;可选升级路径"查询→研究任务"将IR移交E2E-A任务管理器;落点=共享档案记录字段 `origin_query_id`(任务档回链模式B查询,§4.1) |
| 4 | 研究任务schema最低字段集 | **沿用(引用不重定义)** | 模式B不另立任务schema;升级为任务时**整体采用**E2E-A最低字段集;落点=共享档案任务记录外键 `task_id`(格式见§4.1) |
| 5 | `falsifiable_conditions` | **分歧(查询记录不带)+升级承接** | 模式B查询记录(QB-*)无预测语义,不设`falsifiable_conditions`;一旦升级为任务(E2E-A),该字段按E2E-A schema强制在场——分歧边界=是否预测型研究对象 |
| 6 | append-only(仅追加) | **沿用** | 模式B查询历史`query_history`同语义仅追加: `query_id`单调、记录不可变不可删改;落点=§4.1共享档案 `query_history`集合 + IR `query_id` |
| 7 | 真实历史回放只读锚定 | **沿用** | 模式B as_of时点查询(D6)同款纪律: 只读锚定既有快照/离线构建(write=False,S1 L384-385);对应禁令=禁调窗口/口径/容差凑答案(对应E2E-A"禁调参凑触发");落点=IR `as_of`+`target_snapshot_id`绑定后不可变 |
| 8 | 两模式共享可信事实与研究档案 | **沿用** | 唯一事实源=注册表+fact_engine+快照(两模式同一入口,R1/E2);共享档案=§4.1 |

### 4.1 共享研究档案衔接设计(快照ID/任务ID引用约定)

- **快照ID引用约定**: 两模式一切记录引用快照时**必须用完整`snapshot_id`**(`research_snapshot_{YYYYMMDD}[_vN]`,S1 L345/L397),并附`digest_snapshot`16位指纹(R5)实现内容级绑定(防同名篡改,对齐数据包meta绑定纪律A5)。
- **任务ID引用约定**: E2E-A任务 `task_id` 格式 `RT-YYYYMMDD-NNN`;模式B查询 `query_id` 格式 `QB-YYYYMMDD-NNN`(同日序列各自独立计数)。
- **交叉引用字段**: 任务记录可携 `origin_query_id: string|null`(由模式B升级而来的任务回链);查询记录可携 `promoted_to_task_id: string|null`(升级结果回链);两字段由append-only写入后不可改。
- **档案载体(设计层)**: 单一共享档案文件族(如`research_archive/`下分集合),集合含 `query_history`(模式B查询IR+作答摘要)/ `research_tasks`(E2E-A任务)/ `anomaly_events`(E2E-A异常);所有记录必携 `snapshot_id`+digest;实现与路径最终由实现包定,本设计固定**引用约定**。

---

## §五 差距清单(编号承接INVENTORY §二;每条可追溯)

| 编号 | 差距(来源) | 内容 | 承接包 |
|---|---|---|---|
| GAP-01 | INVENTORY G-01 | 日本政策利率与JGB各期限收益率不在注册表(81指标实测零命中),E2E-B场景日端缺席 | WP-B3 |
| GAP-02 | INVENTORY G-02 | 无NL查询面/中间表示/映射层 | WP-B1 |
| GAP-03 | INVENTORY G-03 | 无查询期通用配对派生机制(compute_derived硬编码五族) | WP-B2 |
| GAP-04 | INVENTORY G-04 | 相关性PAIRS固定10对无USDJPY配对、无按需配对面(序列数据在场) | WP-B2 |
| GAP-05 | INVENTORY G-05 | DEV侧无持久化快照,查询执行器测试需离线构建(write=False)路径固化 | WP-B5 |
| GAP-06 | INVENTORY G-06 | 无共享研究档案/查询历史存储与ID引用约定落点 | WP-B4 |
| GAP-07 | INVENTORY G-07 | 历史as_of时点查询语义部分在场、无模式B显式规格与测试 | WP-B2 |
| GAP-08 | INVENTORY G-08+§三(b) | 答案接地强制机制(无源数值fail-closed渲染)无落点 | WP-B5 |

(§三设计新增需要已并入上表: GAP-03/04/07/08;无悬空条目。)

---

## §六 工作包拆解(验收要点=草案,正式AC由主Agent后续轮拟定)

> 全部工作包共同红线(每包验收必查): 禁LIVE部署/禁launchd改动/禁交易与收益承诺/禁绕开快照+门禁直读原始数据;查询执行器数据入口恒为R1快照选择+R3门禁放行判定。

**WP-B1 NL→查询映射层(IR schema+映射器v1+缺席路径)**
- 目标: 落地§三(a)IR schema与v1映射器(约束式映射: 词表+注册表检索),产出可执行IR;缺席四级与unresolved_entities如实上浮。
- 范围: 新增IR定义模块+映射器;不含执行器与渲染。
- 依赖: 无(注册表只读接口E2既有)。
- 验收要点草案: ①离线单测: IR字段级schema校验用例(工件: tests/test_p03_b1*.py,CI offline-tests套件) ②§三(d)问题文本→IR映射黄金用例,含MB-8/MB-9 ABSENT_REGISTRY断言(工件: 测试文件+CI run) ③unresolved_entities负向用例(禁交易类问题→out_of_scope,工件: 测试文件) ④模块SHA登记(工件: commit SHA)。

**WP-B2 查询执行器(快照绑定+引擎口径复用+查询期派生+按需相关性+as_of语义)**
- 目标: IR→数值: 快照绑定(R1/R3)、engine口径取值(E3/E5/E11复用)、spread/level_diff查询期派生(calculation_ref纪律,D3)、按需配对相关性(C3/C4复用series_store,D4)、as_of时点只读锚定(D6)。
- 范围: 新增执行器模块;不改fact_engine/snapshot_builder既有函数签名。
- 依赖: WP-B1;GAP-01修复前美日双端场景按§三(c)缺席输出。
- 验收要点草案: ①离线单测以DEV授权副本(data/daily 20261101/20261102)构建write=False快照并执行OP-3(工件: 测试文件+数据档引用 data/daily/macro_20261102.json) ②NO_DATA传导用例(OP-1/OP-2 result=null,工件: 测试文件) ③as_of历史锚定用例: 同一问题两个as_of,输出随快照时点不同且不混入期后数据(工件: 测试文件+as_of字符串) ④引擎口径一致性: 执行器输出与fact_engine直算逐值相等(硬编码预期值,对齐E2E-A"测试预期值硬编码"纪律;工件: 测试文件) ⑤CI零回归(工件: GitHub Actions run ID)。

**WP-B3 日本利率数据身份与获取(JGB/日银政策利率入注册表+采集)**
- 目标: 消除GAP-01: 注册表新增日本政策利率与JGB关键期限(至10Y)身份(81→新增N条,registry版本升级走既有变更纪律),采集通道落地(免费公开源规则循预授权③于本包适用)。
- 范围: registry变更+采集器扩展+通道SOURCE_FILE_RULES登记;**不含**模式B其余面。
- 依赖: 无硬依赖(可与WP-B1/B2并行);完成后E2E-B场景双端闭合。
- 验收要点草案: ①注册表计数实测断言(81+N,工件: 测试文件+registry文件SHA) ②身份语义校验通过(registry_semantics既有校验,工件: 测试) ③真实采集样本落data/daily且经快照Gate A(工件: 数据档文件+快照digest) ④文档口径登记(单位percent/日历/来源,工件: registry diff)。

**WP-B4 共享研究档案与查询历史(append-only)**
- 目标: 落地§4.1: query_history集合、ID引用约定(query_id/task_id/origin_query_id/promoted_to_task_id)、snapshot_id+digest内容级绑定。
- 范围: 档案存储模块(append-only文件族);E2E-A任务集合字段以E2E-A冻结合同为准(本包只建模式B侧+引用约定)。
- 依赖: WP-B1(IR即首类记录)。
- 验收要点草案: ①append-only不可变测试: 重复写入/改写被拒(工件: 测试文件) ②ID格式与交叉引用字段校验(工件: 测试文件) ③digest绑定: 篡改快照后档案校验拒绝(工件: 测试+R5机制) ④CI零回归(工件: run ID)。

**WP-B5 E2E-B场景端到端验收(接地强制渲染+走查固化)**
- 目标: 回答渲染层: 接地强制(§三(b),无源数值fail-closed)、缺席文本化、质量披露;把§三(d)走查固化为端到端黄金用例(问题→IR→执行→接地答案)。
- 范围: 渲染/校验模块+端到端测试;含GAP-05的write=False快照测试范式固化。
- 依赖: WP-B1/B2(必),WP-B4(查询历史记录)。
- 验收要点草案: ①无provenance数值注入→渲染fail-closed负向测试(工件: 测试文件) ②端到端黄金用例: DEV授权副本上全链路,断言美端值+日端「无数据」+OP-1 NO_DATA(工件: 测试文件+数据档引用) ③WP-B3完成后同用例升级为双端闭合版(工件: 测试+新数据档) ④CI零回归(工件: run ID)。

(包数=5 ≥3;GAP-01~08全部有承接;每包四要素齐备;无任何包含红线项。)

---

## §七 红线遵守

1. **快照+门禁不可绕开**: 查询执行器唯一数据入口=`select_snapshot`(R1)+`gate_allows_formal_research`(R3);IR的`source_file`仅披露,不构成读取路径(D1;§三(a) Provenance注释);新研究模块(模式B全链)不例外于架构v2"必须走快照+门禁"。
2. **LIVE禁写**: 全部工作包产物落DEV仓与测试沙箱;LIVE路径(/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent)与launchd零触碰;WP-B3采集落DEV数据档。
3. **禁交易/收益承诺**: `answer_constraints`与映射器`out_of_scope`(§三(a) UnresolvedEntity)显式拦截交易指令/仓位管理/收益承诺类问题;回答模板禁止投资建议措辞(实现于WP-B5渲染层)。
4. **数据不足不填0**: 四级缺席路径(§三(c))零填零;派生NO_DATA不部分计算;与E3/M1/C5三处既有"不填0"实现同源;走查中MB-8/9与OP-1/2为活例。

---

*设计依据事实见INVENTORY;交付说明与证据见DELIVERY。本设计docs-only,未改任何代码/测试/配置。*
