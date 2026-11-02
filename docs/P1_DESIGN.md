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

**a-1 registry 条目扩展(在既有 17 字段 [实取·INVENTORY K-1] 之上新增 3 字段,81 条目全量回填 + 新条目沿用)**

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
- **免费公开源循预授权③直用**: ECB Data Portal / BOJ 时系列 / Bundesbank / BEA(均免费无凭证);设计采集频率=每日 1 次,并入既有 11 步流水线(run_weekly.py L126-L151 [实取])新增步骤,公共 API 合理使用量级 [示意·非实取·频率设计值]
- **yfinance 并批**: DAX/CAC40/NIKKEI225 并入 global 通道**同一采集批次**,不新增调用轮次、不增请求结构 [示意·非实取·策略]
- **付费/凭证源只登记 PENDING 候选,禁直接依赖**: S&P PMI(付费)、e-Stat(appId)、tushare 积分接口、FRED 超既有凭证范围扩量——均 PENDING 报批,任何 WP 不得将其设为唯一路径
- **依赖用户授权**: G-P1-10..18 全部 china 通道改动(采集器冻结在案),独立拆包 WP-P1-E(DP-4),不阻塞 JP/EA 主线
- 跨分支登记事实必须吸收 [示意·非实取·跨分支登记,dev/data-coverage@`06f715b6be34dedd69f6776b1947238708de0563`]: 81指标覆盖 N71/S8/B2/C0/U0、china 通道 12 指标 8 个源端失败、MARGIN_BAL/SH_PE 双断点——即 CN 面修复**先于** CN 宏观扩展的优先级判断依据

### (c) 降级路径(与「数据不足不填0」一致)

1. **采集/源层**: 源不可得→`sources_status` 记 MISSING/READ_FAIL [实取·snapshot_builder.py L253-L254, L270-L271]→当日档该节键缺席(非0);备源次序按 DP-2(如 e-Stat 不可达→BOJ 镜像)。
2. **引擎层**: 序列不足→`{"available": false, "reason": …}` 绝不回填0 [实取·fact_engine.py L90, L94-L95];月频未发布≠缺失(92天/45天有效窗沿既有新鲜度规则)。
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
| L2 金融事实引擎 | 扩展 | registry 增 `economy/economy_rule/market_seat` 三字段+12候选条目;`normalize_jp/normalize_ea` 新函数;`trading_calendar` 增 jp_equity/ea_euro;`compute_period_returns`/`RATE_UNITS`/`validate_fact` 零改动沿用 |
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
| WP-P1-A 注册表与 JP/EA 采集面 | 81+12 条目经济体化+JP/EA 通道落地 | registry 三字段回填与12候选条目、jp_/ea_ 采集脚本与数据档、run_weekly 步骤接入 | 免费 public API 循预授权③(DP-2);不依赖 P0-3 | ① 单测: registry economy 字段与 P1-P8 规则一致性(逐条断言)+负向(规则未命中条目拒入)【测试】② 首份 `data/daily/jp_/ea_YYYYMMDD.json` 真实档在场【数据档引用】③ 新采集器离线测试(源失败→MISSING 不填0)【测试/CI】④ offline-tests 全套件零回归【CI】 |
| WP-P1-B 事实引擎与快照贯通 | 新通道进引擎与快照,缺席合法登记 | normalize_jp/ea、jp/ea 日历、build_all/resolve_inputs 扩展、Gate A 对新指标裁决 | WP-A | ① 单测: 新通道事实构造+口径(week/MTD/YTD 对 jp/ea 日历)+数据不足路径【测试】② 快照 sources_status 含 jp/ea 键的构建测试(含缺源 MISSING)【测试】③ 既有 US 面输出零回归(W-3 对照)【测试/CI】 |
| WP-P1-C 经济体评分·装配·报告 | 评分/数据包/报告经济体化 | scorecard economy 参数化(DP-3)、数据包经济体节、相关性新对、报告模板与 Gate B 锚点 | WP-B | ① 维度扩展单测+DATA_INSUFFICIENT 负向【测试】② 数据包经济体节渲染快照测试【测试】③ Gate B 对新锚点全量核验用例【测试/CI】 |
| WP-P1-D 查询面与共享档案衔接 | 四经济体 NL 查询与档案 ID 衔接 | IR economy 字段、QB-/RT- 引用约定落地、W-1/W-2 场景实现化 | **依赖 P0-3 落地**(E2E-A/B 实现) | ① IR schema 扩展单测(economy 过滤+接地标识强制)【测试】② W-1/W-2 端到端用例: 缺席→「无数据」+差距登记断言【测试】③ 档案记录附 snapshot_id+digest 的校验【测试】 |
| WP-P1-E CN 面修复与宏观扩展 | 断点修复+CN 宏观接入 | G-P1-10..18(备源切换与新宏观接口) | **依赖用户授权**(china 采集器冻结在案);tushare 积分/e-Stat→PENDING 报批,不为唯一路径 | ① 断点修复后 `china_YYYYMMDD.json` 对应节非空【数据档引用】② 源端失败注入测试(限流→MISSING 披露)【测试】③ 宏观新指标 registry 条目+单测【测试/CI】 |

红线筛查(全包通用,逐包不再重复): 全部包**不含** LIVE 部署、launchd 改动、交易或收益承诺、绕开快照+门禁直读原始数据的设计;新数据一律经快照进入研究面(§三(a-4)、§四衔接设计)。

## §七 红线遵守

1. **快照+门禁不可绕开**: 四经济体一切新数据经 `build_snapshot` 进入研究面;研究引擎/查询/报告零直读采集档(E2E-A 禁直读约束对 jp_/ea_ 档同样生效;§四)。
2. **LIVE 禁写**: 全部工作在 DEV 仓库 dev/* 分支;LIVE 目录与 launchd 零触碰(本包 docs-only 已零接触)。
3. **禁交易/仓位/收益承诺**: 本设计与全部工作包不含任何交易、仓位管理、收益承诺内容。
4. **数据不足不填0**: 采集层键缺席/引擎层 available:false/Gate A 缺失披露/查询层「无数据」/评分层 DATA_INSUFFICIENT——五层一致(§三(c))。
