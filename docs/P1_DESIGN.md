# P1 设计:四经济体研究能力扩展(DESIGN)

> 包: R015 · IA-P1-DESIGN(docs-only 零代码) | 基线 checkout: `1ddfb65ec78f4358b7a004be8ef5d8916ba0f052`(`dev/p1-design` 自其切出)
> 配套盘点: `docs/P1_DATA_NEEDS_INVENTORY.md`(下称 INVENTORY) | 编制: 2026-11-02(UTC)
>
> **数值标注纪律(全文)**: 任何具体数值逐个二选一——**[实取]**+文件与日期引用,或 **[示意]**+显式「非实取」。`文件:行号` 行级引用= [实取](checkout `1ddfb65`,偏差 ≤3 行可复核)。设计示例值(候选源频率、字段长度等)均为 [示意·非实取]。跨分支登记数值标 [示意·非实取·跨分支登记]。

---

## §一 目标与边界

**P1 定义**: 把 investment-agent 的数据面与场景面从「以美国为主+部分全球指标」扩展到**四经济体(US/CN/JP/EA,DP-1)**,复用 v2 六层架构与 P0-2/P0-3 全部既有机制,**不重写**。本轮仅设计(差距+架构+拆包),零代码、零采集。

**命名冲突登记**: `docs/UPGRADE_PLAN.md` L66-L83 的「P1 研究增强/P2 配置研究引擎」为 2026-10-11 旧阶段方案 [实取],与本设计线 P1(四经济体)**同名不同物**;本线编号以路线图 P0-3→P1→P2 为准,后续包命名建议带「IA-P1」前缀消歧。

**In scope**: registry 经济体化字段与新经济体条目、JP/EA 新数据通道、CN 断点修复与宏观扩展(依赖用户授权)、fact_engine 口径面扩展、快照通道面扩展、评分/装配/报告经济体化、NL 查询与共享档案的四经济体衔接(依赖 P0-3 落地)。

**Out of scope(红线级)**: 交易/管理真实仓位/承诺收益;LIVE 与 launchd 任何写入;绕开快照+门禁直读原始数据;数据不足填0;本轮冻结后续包 AC(§六验收要点=草案)。

## §二 盘点引用与决策点

**引用**: 数据资产、五层入口、缺口编号(G-P1-01..19)、结构性已知缺口(K-1..K-6)全部引用 INVENTORY (a)/(b)/(c),本文不重复行级证据。

**登记型决策点(先登记后成文;最终确认保留给用户/后续包)**:

| DP | 决策点 | 候选项 | 选定规则(本轮登记) |
|---|---|---|---|
| DP-1 | 四经济体构成 | 默认候选 美/中/日/欧;仓库另无权威定义(INVENTORY a.1 实读检索声明) | 结构不因构成微调失效;最终确认留用户 |
| DP-2 | JP/EA 源优先级 | ①官方免费API(BOJ/ECB/Bundesbank) ②yfinance 并批 ③PENDING 付费 | 官方免费API优先(循预授权③);yfinance 仅用于行情类;付费一律 PENDING 不进依赖 |
| DP-3 | 评分经济体化形态 | ①`macro_scorecard` 维度函数参数化 economy ②并列新 runner | 倾向①(复用 `score_growth/score_inflation` 与 `DATA_INSUFFICIENT` 机制,字段级落点=函数签名增 economy 形参);最终由 WP-P1-C 实现包定 |
| DP-4 | CN 面拆包 | ①并入 WP-P1-A ②独立 WP-P1-E | 倾向②独立(china 采集器改动冻结在案,风险与授权路径独立,不阻塞 JP/EA 主线);最终由排期定 |

## §三 经济体扩展架构

### (a) 扩展数据结构(字段级 schema;字段名/类型/语义逐项)

**a-1 registry 条目扩展(在既有 17 字段 [实取·INVENTORY K-1] 之上新增 3 字段,81 [实取·INVENTORY b.1 registry 实测计数,2026-11-02] 条目全量回填 + 新条目沿用)**

| 字段名 | 类型 | 语义 |
|---|---|---|
| `economy` | string, enum {US,CN,JP,EA,HK,GLOBAL} | 经济体归属,取值=INVENTORY a.3 规则 P1-P8 的机械结果 |
| `economy_rule` | string | 命中规则编号(如 "P8"),审计可机械复核 |
| `market_seat` | string, enum {onshore_local, offshore_proxy, global} | 本币在岸 vs 离岸代理(SHCOMP=onshore_local;EWJ=offshore_proxy;GOLD_F=global) |

**a-2 新经济体数据档结构(`data/daily/jp_YYYYMMDD.json`、`ea_YYYYMMDD.json`;档名/日期时区口径与既有四通道一致,INVENTORY b.3②)**

顶层(两档同构): `date`:string(YYYYMMDD,采集日) / `generated_at`:string(ISO时刻) / `sources_status`:object(逐源 {status, retrieved_at})。
`jp_` 通道节:
- `policy_rates.BOJ_POLICY_RATE`:{value:float, unit:"percent", date:观测日YYYY-MM-DD, prev_value:float|null}
- `jgb.JGB_10Y`、`jgb.JGB_2Y`:{value:float, unit:"percent", date, prev_value}
- `inflation.JP_CPI_TOKYO_YOY`:{value:float, unit:"percent", date, prev_value, change, change_period, freq:"Monthly"}
- `prices.NIKKEI225`:{close:float, date, high, low, series:{"YYYY-MM-DD": close}}(series 供 week/MTD/YTD 派生,同既有行情档形态 [实取·global_20261102.json 各资产条目键集 close/high/low/week_chg/mtd_chg/ytd_chg/vs_50d])
`ea_` 通道节:
- `policy_rates.ECB_DFR`、`policy_rates.ECB_MRO`:{value, unit:"percent", date, prev_value}
- `bund.BUND_10Y`、`bund.BUND_2Y`:{value, unit:"percent", date, prev_value}
- `inflation.EA_HICP_YOY`:{value, unit:"percent", date, prev_value, change, change_period, freq:"Monthly"}
- `prices.DAX`、`prices.CAC40`:{close, date, high, low, series}
单位纪律: 利率/通胀水平一律 percent,期间变化由引擎派生为 pp/bp(与 `RATE_UNITS` [实取·fact_engine.py L37] 一致);**任何节缺席→键不出现或 value=null,禁以 0 占位**。

**a-3 fact_engine 口径扩展点**

- 新函数 `normalize_jp(data, as_of, source_file="jp_*.json")`、`normalize_ea(...)`——结构同构于 `normalize_rate`(通道→事实+对账输入) [实取·fact_engine.py L406];registry 新条目(候选 metric_id,落地以 WP-A 为准): BOJ_POLICY_RATE / JGB_10Y / JGB_2Y / JP_CPI_TOKYO_YOY / NIKKEI225 / ECB_DFR / ECB_MRO / BUND_10Y / BUND_2Y / EA_HICP_YOY / DAX / CAC40,共 12 条候选 [示意·非实取·候选清单]
- `compute_period_returns` **零改动沿用**——签名已参数化 calendar [实取·L81 `def compute_period_returns(dates, values, unit, calendar, as_of=None)`];日历扩展=`trading_calendar` 新增 jp_equity / ea_euro 日历(交易日历表驱动)
- `build_all` [实取·L709] 增 jp_data/ea_data 入参;对账 `cross_metric_checks`(L661)可增 EA 双源对账位(ECB API vs Bundesbank API 的 Bund 交叉,候选)

**a-4 快照通道面扩展**: `resolve_inputs` [实取·snapshot_builder.py L47] 增 jp/ea glob;`sources_status` 增 jp/ea 键(缺源={'status':'MISSING'} 沿用 L253-L254);`series_store` 增 NIKKEI225/DAX/CAC40 序列键;`build_snapshot`/Gate A/不可变/锚点机制**零改动**(L236/L313/L388-L398/L411-L427)。

**a-5 装配/报告扩展**: `data_assembler.build_markdown` [实取·L123] 新增「经济体观察」节(渲染复用 `_rows`/`_fv`,L107/L97);`macro_scorecard` 维度函数 economy 参数化(DP-3);`correlation_calculator.compute_all`(L83)增新对(候选: NIKKEI225×USDJPY、DAX×EURUSD);报告模板经济体章节;Gate B 锚点自动覆盖新 metric_id(锚点=build_anchors 按快照事实生成,零改动)。

### (b) 数据策略(逐缺口候选源/频率/配额)

逐缺口候选源与频率=INVENTORY (c) 表 G-P1-01..19(此处不复制,以该表为准)。配额约束与纪律:
- **免费公开源循预授权③直用**: ECB Data Portal / BOJ 时系列 / Bundesbank / BEA(均免费无凭证);设计采集频率=每日 1 次,并入既有 11 步流水线(run_weekly.py L126-L151 [实取·steps 列表实测恰 11 步,2026-11-02])新增步骤,公共 API 合理使用量级 [示意·非实取·频率设计值]
- **yfinance 并批**: DAX/CAC40/NIKKEI225 并入 global 通道**同一采集批次**,不新增调用轮次、不增请求结构 [示意·非实取·策略]
- **付费/凭证源只登记 PENDING 候选,禁直接依赖**: S&P PMI(付费)、e-Stat(appId)、tushare 积分接口、FRED 超既有凭证范围扩量——均 PENDING 报批,任何 WP 不得将其设为唯一路径
- **依赖用户授权**: G-P1-10..18 全部 china 通道改动(采集器冻结在案),独立拆包 WP-P1-E(DP-4),不阻塞 JP/EA 主线
- 跨分支登记事实必须吸收 [示意·非实取·跨分支登记,dev/data-coverage@`06f715b6be34dedd69f6776b1947238708de0563`]: 81指标覆盖 N71/S8/B2/C0/U0、china 通道 12 指标 8 个源端失败、MARGIN_BAL/SH_PE 双断点——即 CN 面修复**先于** CN 宏观扩展的优先级判断依据

### (c) 降级路径(与「数据不足不填0」一致)

1. **采集/源层**: 源不可得→`sources_status` 记 MISSING/READ_FAIL [实取·snapshot_builder.py L253-L254, L270-L271]→当日档该节键缺席(非0);备源次序按 DP-2(如 e-Stat 不可达→BOJ 镜像)。
2. **引擎层**: 序列不足→`{"available": false, "reason": …}` 绝不回填0 [实取·fact_engine.py L90, L94-L95];月频未发布≠缺失(月频窗=60天,沿既有新鲜度规则 [实取·config/metric_registry.json L1393(CPI条目 freshness.max_calendar_lag_days=60)、scripts/fact_engine.py L592-595(现行月频窗=60天;92=已废除旧硬编码、45=被否决候选,均非现行),实测2026-11-02])。
3. **快照/Gate A 层**: 新经济体指标按注册表 criticality 进入裁决——核心缺失→Gate A FAIL 如实暴露,非核心缺失→DEGRADED 结构化披露 [实取·snapshot_builder.py L308-L321 注释与实现,recompute_gate_a]。
4. **查询/报告层**: 缺席→「无数据」如实输出+差距登记(E2E-B 缺席路径沿用;禁编造禁填0);评分维度可用指标<2→`DATA_INSUFFICIENT`「数据不足不可判」 [实取·macro_scorecard.py L11-L12, L30]。

### (d) 端到端走查(3 场景,覆盖 3 经济体,2 条含缺席处置链;链=研究需求→指标清单→逐指标处置)

**W-1 欧元区(US×EA 政策分化;缺席主导链)**
- 研究需求: 欧央行与美联储政策立场的分化,及其对 EURUSD 与欧元股的传导。
- 指标清单: DFF、DFEDTARL/DFEDTARU(US)、UST_10Y(US)、ECB_DFR(EA)、BUND_10Y(EA)、EA_HICP_YOY(EA)、EURUSD(EA汇率)、EZU(EA代理)。
- 逐指标处置:
  - DFF=3.88 [实取·data/daily/rate_economy_20261102.json,观测2026-10-29]
  - DFEDTARL=3.75、DFEDTARU=4.00 [实取·同档,观测2026-11-01]
  - UST_10Y=4.98 [实取·data/daily/macro_20261102.json,观测2026-10-29]
  - **ECB_DFR: 缺席**(registry 零注册+通道无)→差距登记 G-P1-01→承接包 WP-P1-A
  - **BUND_10Y: 缺席**→G-P1-02→WP-P1-A
  - **EA_HICP_YOY: 缺席**→G-P1-03→WP-P1-A
  - EURUSD close=1.12、ytd −4.83% [实取·data/daily/global_20261102.json,观测2026-10-30]
  - EZU close=65.16、ytd +2.03% [实取·同档,观测2026-10-30]
- 结论形态: 当期仅能以 US 在岸利率 + EA 离岸代理作部分对照;政策分化论证条件登记入研究任务 `falsifiable_conditions`(机制沿用 E2E-A),待 WP-P1-A 落地补全。

**W-2 中国(CN 增长与政策组合;在场/缺席混合链)**
- 研究需求: 中国增长与政策组合对人民币汇率与中资股的传导。
- 指标清单: USDCNY、FXI、HSI、HSAHP(在场)、SHCOMP、MARGIN_BAL(注册在场·采集断点)、中国CPI、LPR、7天逆回购(零注册)。
- 逐指标处置:
  - USDCNY close=6.64、ytd −5.02% [实取·data/daily/global_20261102.json,观测2026-11-01]
  - FXI close=33.08、ytd −16.30% [实取·同档,观测2026-10-30]
  - HSI close=23294.42 [实取·data/daily/china_20261102.json,观测2026-10-30]
  - HSAHP close=132.49 [实取·同档,观测2026-10-30]
  - **SHCOMP: 缺席**——注册在场 [实取·registry L1836] 但当日档 `a_share_indices={}` [实取·china_20261102.json;20261101 档同构]→断点登记 G-P1-10→WP-P1-E(依赖用户授权)
  - **MARGIN_BAL: 缺席**(注册 L2029,当日档 margin=None [实取·同档])→G-P1-11→WP-P1-E
  - **中国CPI / LPR / 7天逆回购: 缺席**(零注册)→G-P1-15 / G-P1-14 / G-P1-18→WP-P1-E
- 结论形态: 在场四条支撑汇率-市场观察;增长与政策侧结论=「数据不足不可判」(DATA_INSUFFICIENT 沿用),断点修复前不给出 CN 基本面结论。

**W-3 美国(全在场对照链,简短;回归基准)**
- 研究需求: 美联储政策利率路径与曲线形态。
- 处置: DFF=3.88(观测2026-10-29)、DFEDTARL=3.75(2026-11-01)、UST_2Y=4.61(2026-10-29)、UST_10Y=4.98(2026-10-29)、CURVE_2S10S=0.38(2026-10-30)、ZQ 近月价格 96.12/隐含月均 3.88(2026-10-30) [均实取·rate_economy_20261102.json 与 macro_20261102.json]。
- 全链在场=基准路径;WP-A..D 的扩展约束=**该路径行为零回归**(既有 US 面输出不变)。

## §四 P0-2·P0-3 复用对齐(逐要素: 沿用/扩展/分歧 + 字段/机制级落点)

| 要素(注入摘要) | 处置 | 字段/机制级落点 |
|---|---|---|
| L1 采集层 | 扩展 | 新增 `scripts/jp_market_collector.py`/`ea_market_collector.py`(候选名);档名 `jp_/ea_YYYYMMDD.json`(a-2);`run_weekly.py` steps 列表 [实取·L126-L151] 增步骤;既有四通道零改动 |
| L2 金融事实引擎 | 扩展 | registry 增 `economy/economy_rule/market_seat` 三字段+12候选条目 [示意·候选·§三(a-3) 候选清单,非实取];`normalize_jp/normalize_ea` 新函数;`trading_calendar` 增 jp_equity/ea_euro;`compute_period_returns`/`RATE_UNITS`/`validate_fact` 零改动沿用 |
| L3 不可变研究快照+Gate A | 沿用(机制)/扩展(通道面) | `build_snapshot`、不可变拒写、`--allow-revision`、原子写、锚点整体替换全部零改动 [实取·snapshot_builder.py L388-L427];扩展仅 `resolve_inputs` 增通道 glob 与 `sources_status` 新键 |
| L4 研究引擎(装配层) | 扩展 | `build_markdown` 增经济体节;scorecard 维度函数 economy 参数化(DP-3);`compute_all` 增新对;`DATA_INSUFFICIENT` 沿用 |
| L5 GLM 报告 | 扩展 | `generate_report` prompt 输入=数据包新节自动进入;「只解释」「当日纪律」(无当日包拒绝生成)沿用 [实取·docs/ARCHITECTURE_V2.md L48] |
| L6 Gate B | 沿用 | `validate_report` 全量核验+canonical 身份对新锚点自动生效(锚点=快照事实渲染,零改动);禁语扫描沿用 |
| E2E-A `research_history_query`(含禁直读约束) | 沿用+扩展 | 禁直读原始数据档约束**原样覆盖 P1 新通道**(jp_/ea_ 档同禁直读,查询只吃快照/事实层);查询覆盖面扩展至新 metric_id,`economy` 字段可作过滤维度 |
| E2E-A `anomaly_detector` | 扩展 | 检测输入=快照事实集→新经济体事实自动进入检测面,无需新机制;触发阈值按新指标 registry `validation` 配置 |
| E2E-A `research_task_manager` | 沿用 | 任务 schema 最低字段集 `falsifiable_conditions` + **append-only 仅追加**语义不变;经济体研究任务复用同一 schema(W-1 结论形态即其用例) |
| E2E-B NL→查询中间表示 | 扩展 | IR 字段级 schema 增经济体过滤字段(候选: `economy: enum{US,CN,JP,EA,HK,GLOBAL}`,取值经 registry.economy 推导);其余字段集沿用 E2E-B 冻结设计 |
| E2E-B 接地规则 | 沿用 | 进入回答的数值必携来源标识(metric_id/快照字段/文件+观测日)——四经济体统一适用;W-1/W-2 处置列即接地形态 |
| 两模式共享可信事实与研究档案 | 沿用+衔接(见下) | 见「衔接设计」段 |

**分歧登记**: 无结构性分歧。唯一口径注意=§一命名冲突(UPGRADE_PLAN 旧 P1/P2);此为登记事项,非要素分歧。日后与 E2E-A/E2E-B 引擎冻结版冲突→由后续包登记型修订承接(注入摘要注记)。

**衔接设计(P1 与两模式共享研究档案)**:
1. 共享档案 ID 约定沿用 E2E-B 设计基线: `QB-`(NL查询)/`RT-`(研究任务)/`origin_query_id`/`snapshot_id`+`digest`;
2. P1 全部新经济体数据进入研究档案的**唯一入口=研究快照**(`snapshot_id` 格式 `research_snapshot_{ymd}` 沿用 [实取·snapshot_builder.py L345]),采集档本身不入档案;
3. NL 查询记录(`QB-`)与研究任务(`RT-`)凡引用经济体维度,必附 `snapshot_id`+`digest`(接地到快照,禁引用采集档);
4. 自主模式识别的经济体异常→研究任务记录增 `economy` 字段(候选,WP-P1-D 落地),任务体其余字段含 `falsifiable_conditions` 不变。

## §五 差距清单(每条可追溯: INVENTORY 缺口或 §三 设计需要;映射见 §六)

| 编号 | 差距 | 追溯 | 承接包 |
|---|---|---|---|
| GAP-P1-01 | registry 无经济体归属字段(结构层) | INVENTORY K-1 | WP-A |
| GAP-P1-02 | JP 本币市场指标零注册(政策利率/JGB/CPI/日经) | INVENTORY K-2、G-P1-06..09 | WP-A |
| GAP-P1-03 | EA 本币市场指标零注册(ECB/Bund/HICP/DAX/CAC;PMI 为 PENDING) | INVENTORY K-2、G-P1-01..05 | WP-A |
| GAP-P1-04 | CN 注册在场但四组采集断点 | INVENTORY K-3、G-P1-10..13 | WP-E |
| GAP-P1-05 | CN 宏观登记缺口(LPR/CPI/PMI/社融/逆回购) | INVENTORY G-P1-14..18 | WP-E |
| GAP-P1-06 | fact_engine 无 jp/ea 通道 normalize 面 | §三(a-3)、INVENTORY K-6 | WP-B |
| GAP-P1-07 | trading_calendar 无 jp/ea 日历 | §三(a-3) | WP-B |
| GAP-P1-08 | 快照 resolve_inputs/sources_status 未含新通道 | §三(a-4)、INVENTORY K-6 | WP-B |
| GAP-P1-09 | 评分卡 US 单一经济体视角 | INVENTORY K-4、§三(a-5) | WP-C |
| GAP-P1-10 | 数据包/报告模板无经济体章节 | INVENTORY K-4、§三(a-5) | WP-C |
| GAP-P1-11 | US 面零回归保障(扩展不得改变既有输出) | §三(d) W-3 | WP-B/C(验收要点含既有套件零回归) |
| GAP-P1-12 | NL 查询 IR 与共享档案缺经济体衔接 | INVENTORY K-5、§四衔接设计 | WP-D(依赖 P0-3 落地) |
| GAP-P1-13 | 美国GDP季频缺口 | INVENTORY G-P1-19 | WP-A(BEA 免费源;FRED 扩量 PENDING 不为唯一路径) |

(§五每条在 §六列名承接包;G-P1 编号与 GAP 编号并存: 前者=数据项缺口,后者=设计需要,映射关系如上表追溯列。)

## §六 工作包拆解(验收要点=草案,正式 AC 由主Agent后续轮拟定,此处不冻结)

| 包 | 目标 | 范围 | 依赖 | 验收要点草案(可核验工件) |
|---|---|---|---|---|
| WP-P1-A 注册表与 JP/EA 采集面 | 81 [实取·INVENTORY b.1 registry 实测计数,2026-11-02] + 12 [示意·候选·§三(a-3) 候选清单,非实取] 条目经济体化+JP/EA 通道落地 | registry 三字段回填与12候选条目 [示意·候选·§三(a-3) 候选清单,非实取]、jp_/ea_ 采集脚本与数据档、run_weekly 步骤接入 | 免费 public API 循预授权③(DP-2);不依赖 P0-3 | ① 单测: registry economy 字段与 P1-P8 规则一致性(逐条断言)+负向(规则未命中条目拒入)【测试】② 首份 `data/daily/jp_/ea_YYYYMMDD.json` 真实档在场【数据档引用】③ 新采集器离线测试(源失败→MISSING 不填0)【测试/CI】④ offline-tests 全套件零回归【CI】 |
| WP-P1-B 事实引擎与快照贯通 | 新通道进引擎与快照,缺席合法登记 | normalize_jp/ea、jp/ea 日历、build_all/resolve_inputs 扩展、Gate A 对新指标裁决 | WP-A | ① 单测: 新通道事实构造+口径(week/MTD/YTD 对 jp/ea 日历)+数据不足路径【测试】② 快照 sources_status 含 jp/ea 键的构建测试(含缺源 MISSING)【测试】③ 既有 US 面输出零回归(W-3 对照)【测试/CI】 |
| WP-P1-C 经济体评分·装配·报告 | 评分/数据包/报告经济体化 | scorecard economy 参数化(DP-3)、数据包经济体节、相关性新对、报告模板与 Gate B 锚点 | WP-B | ① 维度扩展单测+DATA_INSUFFICIENT 负向【测试】② 数据包经济体节渲染快照测试【测试】③ Gate B 对新锚点全量核验用例【测试/CI】 |
| WP-P1-D 查询面与共享档案衔接 | 四经济体 NL 查询与档案 ID 衔接 | IR economy 字段、QB-/RT- 引用约定落地、W-1/W-2 场景实现化 | **依赖 P0-3 落地**(E2E-A/B 实现) | ① IR schema 扩展单测(economy 过滤+接地标识强制)【测试】② W-1/W-2 端到端用例: 缺席→「无数据」+差距登记断言【测试】③ 档案记录附 snapshot_id+digest 的校验【测试】 |
| WP-P1-E CN 面修复与宏观扩展 | 断点修复+CN 宏观接入 | G-P1-10..18(备源切换与新宏观接口) | **依赖用户授权**(china 采集器冻结在案);tushare 积分/e-Stat→PENDING 报批,不为唯一路径 | ① 断点修复后 `china_YYYYMMDD.json` 对应节非空【数据档引用】② 源端失败注入测试(限流→MISSING 披露)【测试】③ 宏观新指标 registry 条目+单测【测试/CI】 |
| WP-P1-F 跨经济体比较视图(§4a#19) | 四经济体横向比较消费面: 在场底图之上的并置比较视图,不重做底图 | 比较视图装配(消费 economy_scorecard_* 档与经济体观察节)、比较事实与跨域对呈现、economy 过滤查询比较用例;零新数据源(纯消费面);不含持续运行监测面(=#20,互斥) | A..E+GAP08+第一层 P0-3 落地链在场交付件(锚见 §八.1);零新数据源 | ① 比较视图=快照/事实/评分卡消费面,零直读采集档【测试】② 四经济体并置+缺席如实(DATA_INSUFFICIENT/「无数据」,不填0)【测试】③ 既有 US 面零回归【测试/CI】④ 实现参数先登记后运行、禁回改;真实调用/凭证/付费面=PENDING·用户实批前置【PENDING】 |
| WP-P1-G(候选名)常态监测(§4a#20) | 让 P0-3 验证的研究流程在四经济体底图上更大范围长期跑: 常态运行监测与异常→研究任务衔接的运行面 | 链路健康常态监测(流水线台账+sources_status+新鲜度)、异常检测经济体扩展、异常→RT- 任务 append-only 衔接、监测回溯查询;零新数据通道;不含按需比较视图(=#19 前件,互斥) | #19 前件+第一层 P0-3 落地链+A..E+GAP08 在场交付件(锚见 §八.2);零新数据源;LIVE 部署=用户保留卡点③(PENDING) | ① 监测面=台账/快照/事实层消费,零直读采集档【测试】② 断点/缺席如实列示(与 Gate A 语义一致,不填0)【测试】③ 异常→任务走 append-only+既有 schema(研究状态保护不绕开)【测试】④ 既有 offline-tests 全套件零回归【CI】⑤ LIVE 部署与通知面=确认型 DP·PENDING·确认权留用户【PENDING】 |

红线筛查(全包通用,逐包不再重复): 全部包**不含** LIVE 部署、launchd 改动、交易或收益承诺、绕开快照+门禁直读原始数据的设计;新数据一律经快照进入研究面(§三(a-4)、§四衔接设计)。

## §七 红线遵守

1. **快照+门禁不可绕开**: 四经济体一切新数据经 `build_snapshot` 进入研究面;研究引擎/查询/报告零直读采集档(E2E-A 禁直读约束对 jp_/ea_ 档同样生效;§四)。
2. **LIVE 禁写**: 全部工作在 DEV 仓库 dev/* 分支;LIVE 目录与 launchd 零触碰(本包 docs-only 已零接触)。
3. **禁交易/仓位/收益承诺**: 本设计与全部工作包不含任何交易、仓位管理、收益承诺内容。
4. **数据不足不填0**: 采集层键缺席/引擎层 available:false/Gate A 缺失披露/查询层「无数据」/评分层 DATA_INSUFFICIENT——五层一致(§三(c))。

---

## §八 收口链设计补全: #19 跨经济体比较视图 + #20 常态监测(实现级规格;IA-P1-DESIGN-COMP/R064 纯追加)

> 本节由 R064 IA-P1-DESIGN-COMP(docs-only)追加,把 §4a 第二层 #19-20 路线级意图(注入摘要,2026-11-06,非工作树实读:L135-139 第二层行,其中 L138「19-20. 跨经济体比较视图+常态监测(让 P0-3 验证的研究流程更大范围长期跑)」=需求源行)展开为实现级规格;§一-§七 既有行零改动。溯源表/DP 登记节/数值扫描清单=`docs/P1_DESIGN_COMP_REPORT.md` §二-§五;数值标注纪律沿本文头部声明(L6)。**#21(P1 验收+终裁+封版)不在本节**: 终验/封版/用户确认面由 #21 合同事承载(本节仅衔接注记)。**两包范围互斥划界**: #19=按需横向比较消费面 / #20=持续运行监测面。**红线承接**: §六 L177 红线筛查与 §七 L179-L184 四红线对 #19/#20 全量适用(本节零例外条款);W4/W5 侧边验收工具不入链(注入摘要架构纪律)。

### §八.1 WP-P1-F 跨经济体比较视图(§4a #19;实现包=WP-P1-F,R062 停泊名,v1.1 重锚后生效)

**目标**: 在 P1 底图层在场交付面之上,提供四经济体(US/CN/JP/EA,INVENTORY a.1 DP-1 默认候选)横向比较消费面——把各经济体评分卡状态、关键事实与跨域相关性并置为单一比较视图,支撑 W-1 型(US×EA 政策分化,§三(d) L88-L100)跨经济体研究问题的例行对照。**纯消费面**: 零新数据源、零新采集通道、不重做底图;数据与研究档案唯一入口=研究快照(§四衔接设计 L141)。

**范围**:
1. **比较视图装配面**: US 主评分卡(`scorecard_{ymd}.json`)与非 US 档(`economy_scorecard_{econ}_{ymd}.json`,macro_scorecard.py L40/L487-L488)并置;复用数据包「经济体观察」节渲染面(data_assembler.py L277-L301)扩展比较呈现;沿用评分卡 DISCLAIMER 口径(内部模型观点非客观事实,macro_scorecard.py L32-L33),不构成投资建议;
2. **比较事实面**: 快照事实+`series_store`(snapshot_builder.py L427-L471)与跨域对(correlation_calculator.py PAIRS L28,含 NIKKEI225×USDJPY L49/DAX×EURUSD L51)的比较型呈现;
3. **查询比较面**: economy 过滤维度(research_history_query.py L184-L201/L337)的比较型查询用例(W-1/W-2 型问题);
4. **互斥划界**: 不含持续运行监测/告警/台账常态面(=#20);不含 #21 终验/封版面(衔接注记: 终验/封版面由 #21 承载)。

**依赖**(层序前置声明: 实现面排程前置=第一层已关闭+WP-P1-A..E(R044-R048)+GAP08(R061)全部在场[BASE-COMP 工作树实读,能力面清单见 REPORT §四];#19 不登记 #20 前件):
- scripts/macro_scorecard.py: score_growth L99/score_inflation L200(economy 参数)/save_scorecard L414-L417/DATA_INSUFFICIENT L30/ECONOMY_NAMES L39;
- scripts/data_assembler.py: economy_scorecard L91/「经济体观察」节 L277-L301;
- scripts/correlation_calculator.py: PAIRS L28/L49/L51,paired_returns L60,compute_all L90;
- scripts/snapshot_builder.py: build_snapshot L266/jp/ea 接线 L335-L350/series_store L427-L471;
- scripts/fact_engine.py: normalize_jp L523/normalize_ea L566/build_all L837;
- config/metric_registry.json: v2.3.0 [实取·json.load,2026-11-06]/102 条目 [实取·同上]/economy 字段(US49/CN18/EA11/JP8/HK4/GLOBAL12 [实取·同上]);
- scripts/research_history_query.py: ECONOMIES L77/query_window L184/--economy L337;
- 第一层 P0-3 落地链查询面: e2eb_query_ir.py ECONOMIES L53。

**验收要点(草案;正式 AC 由 #19 实现包合同冻结)**:
① 比较视图产物=纯快照/事实/评分卡档消费,零直读 `data/daily/` 采集档(禁直读约束=§四 L130 对 jp_/ea_ 档同样生效)【测试】
② 四经济体并置渲染+缺席如实: 任一经济体档缺席→该经济体如实标 DATA_INSUFFICIENT/「无数据」,禁填0、禁跳过整行、禁以离岸代理冒充在岸口径【测试】
③ 既有 US 面零回归: `scorecard_{ymd}` 主评分卡输出与既有套件断言零变化(§三(d) W-3 基准路径行为零回归,L118)【测试/CI】
④ 实现参数(落位形态/并置指标最小集/配对新增)先登记后运行、禁回改(登记型 DP 纪律承接,见 DP 节)【纪律】
⑤ 本包零新数据源/零凭证/零付费;若实现中识别需真实调用/凭证/付费/新数据源→只以 DP/PENDING 登记·用户实批前置,禁直接依赖【PENDING】

**DP 节**(决策点/选项≥2/推荐/影响+分类;登记型提案值均为 [示意·非实取],终值由 #19 实现包合同登记定):
- **DP-F1(登记型)比较视图落位形态**: ①数据包新节(装配器扩展) ②独立比较视图模块(消费快照+评分卡档) ③报告模板新章节。推荐②——US 面零回归触面最小;影响=实现包白名单与零回归面。
- **DP-F2(登记型)并置指标最小集**: ①仅增长/通胀总分+regime ②总分+regime 加关键事实行(政策利率/通胀同比) ③全量指标表。推荐②——比较密度与缺席披露面平衡;影响=视图信息结构与要点②断言面。
- **DP-F3(登记型)跨经济体配对新增**: ①零新增(仅呈现既有两跨域对 L49/L51) ②增候选对(如 SPX×SHCOMP,序列双在场性由实现包实读核验) ③更广候选集。推荐①——配对扩容属底图面非本包消费面;影响=series_store 消费面与相关性输出。
- **确认型 DP: 无**——零新数据源/零凭证/零付费/零部署面/零批量状态修改(如实登记;若实现中发现确认型事项,只登记 PENDING,确认权留用户)。

### §八.2 WP-P1-G(候选名)常态监测(§4a #20;包名候选,终名由主Agent #20 实现包预拟轮定)

**目标**: 让 P0-3 验证的研究流程(注入摘要,2026-11-06,非工作树实读: E2E-A 历史查询/异常检测/研究任务结构与档案、E2E-B 自然语言入口、GLM 竞争性假设、报告生成+档案)在四经济体底图上「更大范围长期跑」(§4a L138 注入行)——设计常态监测运行面: 每日链路健康监测、四经济体异常检测扩展、异常→研究任务→档案的常态化衔接。**纯运行面设计**: 不重做底图、零新数据通道、不绕开快照与研究状态保护机制。

**范围**:
1. **链路健康常态监测面**: 既有 13 步流水线(run_weekly.py steps L126-L157 [实取·2026-11-06 工作树实读;R015 时点 11 步已被 WP-A v1.3 扩为 13 步,以工作树实读为准])台账(`logs/pipeline_run_YYYYMMDD.json`,run_weekly.py L12/L217-L238)与快照 sources_status/Gate A(snapshot_builder.py L382-L385)之上的常态健康视图(逐通道断点/MISSING 回溯、新鲜度越限列示——月频窗 60 天沿既有口径 [实取·config/metric_registry.json CPI 条目 freshness.max_calendar_lag_days=60,2026-11-06 json.load 复核];回溯窗=N 日=登记型 DP-G1);
2. **异常检测经济体扩展面**: 既有 detect_divergence(anomaly_detector.py L60,阈值登记 L29-L32 [实取: CORR_THRESHOLD=0.30/RATE_BP_THRESHOLD=25.0/GOLD_PCT_THRESHOLD=2.0])为 US 单一对(利率×黄金);扩展形态=登记型 DP-G2(泛化/新规则/regime 变化候选三选);
3. **异常→研究任务衔接面**: research_task_manager(build_task L79/SCHEMA_MIN_FIELDS L36-L37/falsifiable_conditions L139/append-only 落档 L165-L189)与 RT- economy 字段(_task_economy L64)的常态化衔接;**研究状态保护=append-only+状态机+门禁**(论点状态修改=report_generator.py update_thesis_status L985;流水线级放行语义=台账 allow_state_writeback,run_weekly.py L211-L216),设计禁绕开;
4. **监测回溯查询面**: research_history_query economy 过滤(L184-L201)作为监测回溯消费面;
5. **互斥划界**: 不含按需横向比较视图(=#19 前件,层内收口链序: #19 先落地);#21 终验/封版/用户确认面不进本包(衔接注记: 终验/封版面由 #21 承载);
6. **部署边界**: 「长期跑」运行宿主(LIVE launchd/定时面)=用户保留卡点(注入摘要 L166: 用户三个保留卡点③LIVE 部署)——本包只设计监测逻辑与离线可验面,任何 LIVE 部署=确认型 DP-G4·PENDING。

**依赖**(#19 前件+层序前置声明: 第一层已关闭+A..E+GAP08 在场;能力面清单见 REPORT §四):
- 第一层 P0-3 落地链: anomaly_detector.py L29-L32/L60;research_task_manager.py L36-L37/L64/L79/L139/L165-L189;research_history_query.py L77/L100/L184;research_archive.py validate_id_conventions L67(QB-/RT-)/validate_query_record L191;report_generator.py generate_report L377/verify_research_inputs L612/update_thesis_status L985;data_validator.py validate_report L755(Gate B)/forbidden_phrases_in L238;
- 底图: run_weekly.py L126-L157(13 步)/L211-L216(放行标志)/L217-L238(台账);snapshot_builder.py L47/L266/L335-L350/L382-L385;config/metric_registry.json v2.3.0/102 条目(freshness 字段);
- #19(前件): 比较视图先落地,监测面消费其视图与底图。

**验收要点(草案;正式 AC 由 #20 实现包合同冻结)**:
① 监测视图=台账+快照+事实层消费,零直读采集档、零新数据通道【测试】
② 断点/缺席如实列示: 任一通道连续 MISSING/新鲜度越限→如实呈现(禁0填充禁静默),语义与 Gate A DEGRADED/MISSING 一致【测试】
③ 异常→研究任务衔接走 append-only+既有 schema(SCHEMA_MIN_FIELDS 可增不可减,falsifiable_conditions 语义不变);研究状态修改仅经既有状态机/门禁面【测试】
④ 既有 offline-tests 全套件零回归(套件数以 #20 实现包合同 BASE 实取值为准,不预植固定数)【CI】
⑤ 实现参数(回溯窗/新鲜度口径/异常规则族)先登记后运行、禁回改(登记型 DP 纪律承接,见 DP 节)【纪律】
⑥ LIVE 部署与通知面=确认型 DP·PENDING·确认权留用户(用户保留卡点③);本包交付零 LIVE 写入【PENDING】
⑦ 涉真实 GLM 调用面(若监测衔接报告生成)=PENDING·用户实批前置;离线测试全 mock【PENDING】

**DP 节**(决策点/选项≥2/推荐/影响+分类;登记型提案值均为 [示意·非实取],终值由 #20 实现包合同登记定):
- **DP-G1(登记型)常态健康回溯窗**: ①7 日 ②14 日 ③30 日。推荐② [示意·非实取];影响=监测视图数据面与要点②断言构造窗。
- **DP-G2(登记型)异常检测经济体扩展形态**: ①detect_divergence 规则族参数化 economy 泛化 ②新增经济体专用规则模块 ③复用评分卡 regime 变化作异常候选。推荐①——复用既有阈值登记结构+registry economy 维度,零新机制;影响=检测面与任务生成量。
- **DP-G3(登记型)新鲜度监测口径**: ①registry freshness 逐条监测 ②分层口径(月频 60 天窗沿既有 [实取·见范围1]+日频通道 MISSING 回溯) ③仅核心指标。推荐②;影响=要点②越限断言面与误报率。
- **DP-G4(确认型)常态监测运行宿主与部署面**: ①LIVE launchd 定时任务 ②手动触发 ③DEV 侧演练先行。**确认权留用户,PENDING**——LIVE 部署=用户保留卡点③(注入摘要 L166);影响=#20 实现包交付面范围(部署面不进离线可验 AC)。
- **DP-G5(确认型)监测结果通知形态**: ①零通知(仅台账与视图) ②终端摘要 ③外部通知(推送/邮件类)。推荐①(零凭证零外部依赖) [示意·非实取];**确认权留用户,PENDING**——通知面涉用户个人流程(选项③另涉凭证=PENDING 报批);影响=#20 实现包通知面有无。
