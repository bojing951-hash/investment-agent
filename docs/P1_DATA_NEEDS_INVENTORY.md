# P1 数据资产与缺口盘点(INVENTORY)

> 包: R015 · IA-P1-DESIGN(四经济体研究能力 · 设计线第1包,docs-only)
> 基线 checkout: `1ddfb65ec78f4358b7a004be8ef5d8916ba0f052`(分支 `dev/p1-design` 自其切出)
> 编制时间: 2026-11-02(UTC) | 编制者: 执行Agent(R015)
>
> **数值标注纪律(全文)**: 本文任何具体数值逐个二选一标注——**[实取]**+文件与日期引用,或 **[示意]**+显式「非实取」。凡 `文件:行号` 形式的行级引用,其行号均为 [实取] 行级引用(checkout `1ddfb65`,审计可 `grep -n` 复核,偏差以 ≤3 行为界)。凡未标注来源的计数字(如条目序号)为行号/序号本身,非研究数值。跨分支登记数值(引自驱动注入摘要、未在本 checkout 复核)一律标 [示意·非实取·跨分支登记] 并注来源分支与尖端SHA。

---

## (a) 四经济体界定与指标归属规则

### a.1 四经济体界定(DP-1 登记型决策点)

**DP-1(登记型决策点,先登记后成文;最终确认保留给用户/后续包,本包不做终局裁断)**

| 组 | 经济体 | 显式定义 | 依据与标注 |
|---|---|---|---|
| 1 | 美国(US) | 美国本土市场与美国货币/财政当局发布的宏观序列;含在美上市以美国资产为标的的工具 | **默认候选**(路线图语境注入);仓库 docs 无四经济体权威定义(见下),现行81指标以美国+全球为主 [实取·config/metric_registry.json,version 2.0.0,created 2026-10-17] |
| 2 | 中国(CN) | 中国大陆在岸市场(沪深交易所上市工具与人民币计价序列);中国香港单列 HK 组(见a.2注) | **默认候选**+china 采集通道在场 [实取·scripts/china_market_collector.py L21 起整文件、data/daily/china_20261102.json] |
| 3 | 日本(JP) | 日本在岸市场与本币序列(JGB、日经225、日银政策利率、日本通胀);含日元汇率对 | **默认候选**(E2E-B 美日场景语境注入);本 checkout 实测 JP 侧仅汇率对与离岸代理,零本币市场注册(见(b)汇总) |
| 4 | 欧元区(EA) | 欧元区(货币联盟整体):欧央行政策利率、德债为代表的欧元区核心国收益率、欧元区HICP;德法股指本币指数 | **默认候选**(路线图语境注入);本 checkout 实测 EA 侧仅汇率对与离岸代理,零本币市场注册(见(b)汇总) |

**仓库实读检索声明(DP-1 出处义务)**: 于本 checkout 对 `docs/` 全量 grep「四经济体/四个经济体/美/中/日/欧 构成类表述」,**未发现**四经济体权威定义;`docs/UPGRADE_PLAN.md` L66-83 的「P1 研究增强(2026-10-11 完成4/4)/P2 配置研究引擎」系**旧阶段命名方案,与本设计线 P1 同名不同物**(命名冲突登记,DESIGN §一承接)。故上表按注入默认候选 美/中/日/欧 登记,构成最终确认保留给用户。

### a.2 附加归属组(非经济体,盘点必需)

| 组 | 定义 | 存在理由 |
|---|---|---|
| HK | 中国香港市场(恒生系指数、AH溢价、南北向资金) | registry 实测有 4 条 HK 日历条目 [实取·config/metric_registry.json L1921/L1949/L1977/L2005];HK 不属四经济体,单列登记避免与中国大陆混同 |
| GLOBAL | 全球跨市场工具:美元指数、全球定价商品(金/银/油)、加密资产、非四经济体市场代理(EM/英国/印度)与货币对(GBP) | registry 实测在场的全球类与跨资产类 [实取·同文件,归类见(b)表] |

### a.3 指标归属规则(机械可复核,按序首中即定)

规则仅依赖 registry 条目的 `calendar`、`asset_class`、`source_symbol` 三个 [实取] 字段,全文一致适用:

| 序 | 条件(字段实取值) | 归属 |
|---|---|---|
| P1 | `calendar == "cn"` | CN |
| P2 | `calendar == "hk"` | HK |
| P3 | `calendar == "us_rates"` | US |
| P4 | `asset_class == "fed_futures"` | US(Fed 期货标的=美国政策利率,虽日历=commodity,先于P7判定) |
| P5 | `calendar == "fx"` → 按非美元腿: `JPY=X`→JP;`CNY=X`→CN;`EURUSD=X`→EA;其余(`DX-Y.NYB` 美元篮子、`GBPUSD=X` 英镑∉四经济体)→GLOBAL | 各如其列 |
| P6 | `asset_class == "country_etf_proxy"` → 按代理目标市场(`source_symbol`): `EWJ`→JP;`EZU`/`FEZ`/`EWG`→EA(欧元区/欧元区核心国德国);`FXI`→CN;其余(`EEM` EM、`EWU` 英国、`INDA` 印度,∉四经济体)→GLOBAL | 各如其列 |
| P7 | `calendar ∈ {commodity, crypto}` 或 `asset_class ∈ {spot_commodity_etf, commodity_futures_etf}` | GLOBAL |
| P8 | 其余(实测= `calendar == "us_equity"` 的 equity_index / volatility_index / single_stock / bond_etf) | US |
| — | 无规则命中 | 登记「未归类」待人工裁决;**实测命中 0 条** [实取·81条逐条套用,见(b)表] |

---

## (b) 现有资产盘点(全部以 checkout `1ddfb65` 实测为准)

### b.1 指标注册表实测

- 文件: `config/metric_registry.json`;`version` = 2.0.0 [实取·该文件 L2],`created` = 2026-10-17 [实取·L3]
- **指标总数 = 81** [实取·`metrics` 数组 L26 起、条目区 L27-L2324,`json.load` 后 `len(metrics)`=81;审计可 `grep -c '"metric_id"'` 复核=81]
- 归属汇总: **US 49 / CN 10 / HK 4 / JP 2 / EA 4 / GLOBAL 12**(合计81)[实取·下表逐行按 a.3 规则套用后计数]
- 关键结构事实: JP 侧 2 条(USDJPY、EWJ)与 EA 侧 4 条(EURUSD、EZU、FEZ、EWG)**全部是汇率对或 US 上市离岸代理,零本币在岸市场指标、零政策利率、零通胀序列注册**;CN 侧 10 条已注册但存在采集断点(见 c 与 b.3 实况)。

### b.2 逐指标归类表(81 行,行=registry 行锚 [实取·grep -n])

| # | 行 | metric_id | 归属 | 规则 | 依据字段 |
|---|---|---|---|---|---|
| 01 | 28 | SPX | US | P8 | us_equity/equity_index |
| 02 | 56 | NDX | US | P8 | us_equity/equity_index |
| 03 | 84 | RUT | US | P8 | us_equity/equity_index |
| 04 | 112 | VIX | US | P8 | us_equity/volatility_index |
| 05 | 140 | NVDA | US | P8 | us_equity/single_stock |
| 06 | 168 | AAPL | US | P8 | us_equity/single_stock |
| 07 | 196 | MSFT | US | P8 | us_equity/single_stock |
| 08 | 224 | TLT | US | P8 | us_equity/bond_etf |
| 09 | 253 | IEF | US | P8 | us_equity/bond_etf |
| 10 | 282 | SHY | US | P8 | us_equity/bond_etf |
| 11 | 311 | HYG | US | P8 | us_equity/bond_etf |
| 12 | 340 | LQD | US | P8 | us_equity/bond_etf |
| 13 | 369 | DXY | GLOBAL | P5 | fx / DX-Y.NYB 美元篮子 |
| 14 | 397 | EURUSD | EA | P5 | fx / EURUSD=X 非美腿EUR |
| 15 | 421 | GBPUSD | GLOBAL | P5 | fx / GBPUSD=X 英镑∉四经济体 |
| 16 | 445 | USDJPY | JP | P5 | fx / JPY=X 非美腿JPY |
| 17 | 469 | USDCNY | CN | P5 | fx / CNY=X 非美腿CNY |
| 18 | 493 | GOLD_F | GLOBAL | P7 | commodity/commodity_futures |
| 19 | 521 | SILVER_F | GLOBAL | P7 | commodity/commodity_futures |
| 20 | 549 | WTI_F | GLOBAL | P7 | commodity/commodity_futures |
| 21 | 577 | BRENT_F | GLOBAL | P7 | commodity/commodity_futures |
| 22 | 605 | GLD | GLOBAL | P7 | us_equity/spot_commodity_etf |
| 23 | 635 | USO | GLOBAL | P7 | us_equity/commodity_futures_etf |
| 24 | 665 | EEM | GLOBAL | P6 | country_etf_proxy/EM∉四经济体 |
| 25 | 695 | EZU | EA | P6 | country_etf_proxy/欧元区 |
| 26 | 725 | FEZ | EA | P6 | country_etf_proxy/欧元区 |
| 27 | 755 | EWU | GLOBAL | P6 | country_etf_proxy/英国∉四经济体 |
| 28 | 785 | EWG | EA | P6 | country_etf_proxy/德国∈EA |
| 29 | 815 | EWJ | JP | P6 | country_etf_proxy/日本 |
| 30 | 845 | INDA | GLOBAL | P6 | country_etf_proxy/印度∉四经济体 |
| 31 | 875 | FXI | CN | P6 | country_etf_proxy/中国 |
| 32 | 905 | BTC | GLOBAL | P7 | crypto/crypto |
| 33 | 933 | UST_2Y | US | P3 | us_rates/rates_yield |
| 34 | 962 | UST_5Y | US | P3 | us_rates/rates_yield |
| 35 | 991 | UST_10Y | US | P3 | us_rates/rates_yield |
| 36 | 1020 | UST_30Y | US | P3 | us_rates/rates_yield |
| 37 | 1049 | HY_OAS | US | P3 | us_rates/credit_spread |
| 38 | 1078 | BB_OAS | US | P3 | us_rates/credit_spread |
| 39 | 1107 | B_OAS | US | P3 | us_rates/credit_spread |
| 40 | 1136 | CCC_OAS | US | P3 | us_rates/credit_spread |
| 41 | 1165 | IG_OAS | US | P3 | us_rates/credit_spread |
| 42 | 1194 | TIPS_5Y | US | P3 | us_rates/real_rate |
| 43 | 1223 | TIPS_10Y | US | P3 | us_rates/real_rate |
| 44 | 1252 | BEI_5Y | US | P3 | us_rates/inflation_expectation |
| 45 | 1281 | BEI_10Y | US | P3 | us_rates/inflation_expectation |
| 46 | 1310 | CURVE_2S10S | US | P3 | us_rates/curve_slope |
| 47 | 1339 | FED_FUNDS | US | P3 | us_rates/policy_rate |
| 48 | 1369 | CPI | US | P3 | us_rates/macro_index |
| 49 | 1399 | CORE_CPI | US | P3 | us_rates/macro_index |
| 50 | 1429 | CORE_PCE | US | P3 | us_rates/macro_index |
| 51 | 1459 | UNEMPLOYMENT | US | P3 | us_rates/macro_rate |
| 52 | 1489 | NFP | US | P3 | us_rates/macro_count |
| 53 | 1519 | NFP_MOM_K | US | P3 | us_rates/macro_count_derived |
| 54 | 1550 | AHE | US | P3 | us_rates/macro_index |
| 55 | 1580 | WTI_SPOT_M | US | P3 | us_rates/macro_price |
| 56 | 1610 | UMCSENT | US | P3 | us_rates/sentiment |
| 57 | 1640 | RSAFS | US | P3 | us_rates/macro_index |
| 58 | 1670 | INDPRO | US | P3 | us_rates/macro_index |
| 59 | 1700 | ICSA | US | P3 | us_rates/macro_count |
| 60 | 1729 | DFF | US | P3 | us_rates/policy_rate |
| 61 | 1758 | DFEDTARU | US | P3 | us_rates/policy_rate |
| 62 | 1783 | DFEDTARL | US | P3 | us_rates/policy_rate |
| 63 | 1807 | ZQ_F1_PRICE | US | P4 | fed_futures(日历=commodity,P4先于P7) |
| 64 | 1836 | SHCOMP | CN | P1 | cn/equity_index |
| 65 | 1864 | SZCI | CN | P1 | cn/equity_index |
| 66 | 1893 | CHINEXT | CN | P1 | cn/equity_index |
| 67 | 1921 | HSI | HK | P2 | hk/equity_index |
| 68 | 1949 | HSCEI | HK | P2 | hk/equity_index |
| 69 | 1977 | HSAHP | HK | P2 | hk/spread_index |
| 70 | 2005 | SB_FLOW | HK | P2 | hk/flow |
| 71 | 2029 | MARGIN_BAL | CN | P1 | cn/leverage |
| 72 | 2053 | SH_PE | CN | P1 | cn/valuation |
| 73 | 2077 | SH_AMOUNT | CN | P1 | cn/volume_amount |
| 74 | 2101 | SZ_COMPONENT_AMOUNT | CN | P1 | cn/volume_amount |
| 75 | 2125 | CN_TOTAL_TURNOVER | CN | P1 | cn/volume_amount |
| 76 | 2155 | REAL_10Y | US | P3 | us_rates/real_rate(fact_engine派生) |
| 77 | 2183 | REAL_5Y | US | P3 | us_rates/real_rate(fact_engine派生) |
| 78 | 2211 | REAL_SHORT | US | P3 | us_rates/real_rate(派生,status=deprecated) |
| 79 | 2241 | HY_IG_DIFF | US | P3 | us_rates/credit_spread(fact_engine派生) |
| 80 | 2269 | ZQ_IMPLIED_AVG | US | P4 | fed_futures(fact_engine派生) |
| 81 | 2297 | JTSJOL | US | P3 | us_rates/macro_count |

(「依据字段」列为 `calendar/asset_class` 实取值缩写,规则命中的完整字段证据见 a.3。)

### b.3 五层在场入口盘点(文件+行号区间+实体名)

**① 指标注册表 — 在场**
- REG-1 | `config/metric_registry.json` L26-L2324 | 实体: `metrics` 数组(81条目;版本字段 L2 `version`="2.0.0")

**② 采集通道 — 在场(4数据通道+新闻+编排)**
- COL-1 | `scripts/global_market_collector.py` L188-L240 | 实体: 逐资产 `week_chg/mtd_chg/ytd_chg` 采集侧计算与输出条目构造(`close/date` 等,采集器自带口径,v2起仅作原始观察记录);另 L96-L144 实体 `btc_completed_utc_days_only`(BTC 已完结UTC日K语义,BTC_CLOSE_SOURCE L109)
- COL-2 | `scripts/china_market_collector.py` L524-L526 | 实体: 写档 `china_{date_str}.json`;tushare pro 惰性初始化 L28-L29;境内源禁代理直连约束 L67-L79;交易日窗口 `get_trade_dates` L94-L98
- COL-3 | `scripts/macro_collector.py` L287-L289 | 实体: 写档 `macro_{today_str}.json`(`today_str` 取自 L280 `datetime.now().strftime('%Y%m%d')`;FRED 源)
- COL-4 | `scripts/rate_expectations.py` L347 | 实体: 写档 `rate_economy_{today}.json`(配套 .md L385;输入候选 glob L31)
- COL-5 | `scripts/news_collector.py` L17 | 实体: 每日写 `news_refs_YYYYMMDD.json` 确定性来源索引(W3-05;非关键步骤)
- COL-6 | `run_weekly.py` L126-L151 | 实体: 11步流水线 `steps`(1-5采集/6快照Gate A/7评分卡/8相关性/9装配/10校验锚点/11预测观察;关键性标注在列)
- **数据档命名与日期时区口径(实取)**: 档名= `global_/china_/macro_/rate_economy_ + YYYYMMDD.json`,日期取采集器运行时本地日期(`datetime.now()`,部署环境 UTC+8,佐证=global_market_collector.py L97 注释「每日07:00(UTC+8)=前一日23:00 UTC」);BTC 显式采用已完结UTC日语义(L96-L144);china 通道观测日=交易所 `trade_date`;快照层显式声明 `timezone: "Asia/Shanghai"`(snapshot_builder.py L348)。当日档实况 [实取·data/daily/]: `china_20261102.json`(timestamp 2026-11-02 01:55:40, version 2.1)、`global_20261102.json`(date 20261102, time 00:11:22)、`macro_20261102.json`、`rate_economy_20261102.json`(generated_at 2026-11-02T00:14:40);另 20261101 各通道同构在场,共 8 个 .json(另含 2 通道 .md 渲染)。

**③ 事实引擎口径面 — 在场**
- FE-1 | `scripts/fact_engine.py` L81-L174 | 实体: `compute_period_returns`(全系统唯一收益口径: week L137-L143 基准=ISO周开始前最后观测; mtd L145-L155 基准=前一自然月最后观测; ytd L157-L162 基准=上年末最后观测; m1/m3/m6/m12 L164-L173;单位纪律 L89 价格→pct、利率→pp+bp、计数→绝对差;数据不足→`{"available": false, "reason": …}` 绝不回填0,L90 与 L94-L95)
- FE-2 | `scripts/fact_engine.py` L37 | 实体: `RATE_UNITS`(利率单位族 percent/percentage_point)
- FE-3 | `scripts/fact_engine.py` L247/L275/L301/L406 | 实体: `normalize_global`/`normalize_macro`/`normalize_china`/`normalize_rate`(四通道→事实记录,别名映射 L244 `_GLOBAL_ID_MAP`)
- FE-4 | `scripts/fact_engine.py` L462 | 实体: `compute_derived`(派生指标 REAL_10Y 等)
- FE-5 | `scripts/fact_engine.py` L513/L661 | 实体: `validate_fact`(12类校验)/`cross_metric_checks`(对账)
- FE-6 | `scripts/fact_engine.py` L709/L727 | 实体: `build_all`/`snapshot_quality_grade`

**④ 研究快照 — 在场**
- SNAP-1 | `scripts/snapshot_builder.py` L236-L438 | 实体: `build_snapshot`(构建入口;源文件 sha256 内容绑定 L263-L269;Gate A 写入时从事实重算 L308-L321 调 `rp.recompute_gate_a`;`snapshot_id`=research_snapshot_{ymd} L345;`timezone` L348;**不可变**: 已存在拒写、须 `--allow-revision` 出 `_vN` 并记 `revision_reason` L388-L398;原子写 L399-L403;锚点整体替换+meta sidecar L411-L427)
- SNAP-2 | `scripts/snapshot_builder.py` L47 | 实体: `resolve_inputs`(四通道当日档/回退解析,MISSING/FALLBACK 状态)
- SNAP-3 | 可读取面 | 快照 `research_snapshot_{ymd}.json/.md` + 锚点 `anchors_{ymd}.json`+meta(`rp.write_meta` 含 provenance/digest,L419-L427);消费方见⑤(装配层只吃快照,run_weekly.py L134-L135 注释明示「不再各自glob最新文件」)

**⑤ 装配/评分/报告层 — 在场(基线部分)**
- ASM-1 | `scripts/data_assembler.py` L123(辅 L37 `load_snapshot`) | 实体: `build_markdown`(数据包=快照渲染)
- ASM-2 | `scripts/macro_scorecard.py` L92 `score_growth` / L180 `score_inflation` / L271 `determine_regime` / L303 `resolve_transition` / L357 `attribute_regime` / L383 `save_scorecard`;数据不足态实体 L30 `DATA_INSUFFICIENT`(维度可用指标<2 →「数据不足不可判」,缺失≠0分)
- ASM-3 | `scripts/correlation_calculator.py` L83 | 实体: `compute_all`(消费快照 `series_store`)
- ASM-4 | `scripts/report_generator.py` L377 `generate_report` / L574 `_call_glm` / L612 `verify_research_inputs` / L985 `update_thesis_status` / L1243 `validate_generated_report`
- ASM-5 | `scripts/data_validator.py` L755 `validate_report`(Gate B)/ L238 `forbidden_phrases_in`(禁语)
- **如实不在场登记**: E2E-A 三模块(`research_history_query`/`anomaly_detector`/`research_task_manager`)与 E2E-B NL→查询中间表示**在本 checkout 均不在场**(属 P0-3 执行包,合同已冻结待发/在途;本盘点依注入摘要对齐,见 DESIGN §四)。

---

## (c) 缺口清单(编号+数据项+候选源+频率+归属)

> 候选源标注口径: 「免费公开源循预授权③」= 免费且无需凭证,可直用;「PENDING 报批」= 付费或需凭证;「依赖用户授权」= 代码面改动受在案冻结约束(china 采集器改动未获用户授权,属用户决策)。候选源为设计登记,本轮零采集、零配额消费。

| 编号 | 数据项/指标 | 候选源 | 频率 | 归属 |
|---|---|---|---|---|
| G-P1-01 | 欧央行政策利率(ECB存款便利利率DFR、主要再融资利率MRO) | ECB Data Portal API(免费公开无凭证,循预授权③) | 日(决议日变动) | EA |
| G-P1-02 | 德债收益率 10Y/2Y(Bund) | Deutsche Bundesbank 开放数据API(免费无凭证,循预授权③);备选 ECB Data Portal 成员国国债收益率序列(免费无凭证) | 日 | EA |
| G-P1-03 | 欧元区HICP同比 | ECB Data Portal(免费无凭证,循预授权③) | 月 | EA |
| G-P1-04 | 欧元区/德国制造业PMI | S&P Global 官方 PMI(付费)→ **PENDING 报批**;无官方免费公开替代(免费汇总源非权威,不登记为候选) | 月 | EA |
| G-P1-05 | 欧元区股指本币指数(DAX、CAC40) | yfinance `^GDAXI`/`^FCHI`(免费;并入既有 global 通道同一采集批次,不新增调用轮次) | 日 | EA |
| G-P1-06 | 日银政策利率(无担保隔夜利率/当座預金利率) | 日本银行(BOJ)时系列统计API(免费无凭证,循预授权③) | 日(决议日变动) | JP |
| G-P1-07 | 日本国债收益率 10Y/2Y(JGB) | BOJ 时系列统计API(免费无凭证,循预授权③) | 日 | JP |
| G-P1-08 | 日本CPI(东京/全国,同比) | BOJ 时系列API镜像系列(免费无凭证,循预授权③);e-Stat API(免费层但需 appId 凭证)→ **PENDING 报批** | 月 | JP |
| G-P1-09 | 日经225本币指数 | yfinance `^N225`(免费;并入既有 global 通道批次) | 日 | JP |
| G-P1-10 | A股指数断点修复: SHCOMP/SZCI/CHINEXT(注册在场,L1836/L1864/L1893;当日档 `a_share_indices` 为空 [实取·data/daily/china_20261102.json 及 china_20261101.json 同构]) | 既有代码内备源: akshare 新浪日K(china_market_collector.py L486-L494 方案2在场)/东财 akshare(L501-L503,网络不可达注释在档);tushare index_daily 为接口级限流既有阻断(5次/天) | 日 | CN |
| G-P1-11 | 两融与估值断点修复: MARGIN_BAL/SH_PE(注册在场 L2029/L2053;当日档 `margin`/`valuation` 为空/None [实取·同上]) | akshare 备源(免费)/tushare `margin`(限流+积分)→ tushare 侧 **PENDING 报批**;**依赖用户授权**(china 采集器改动冻结在案) | 日 | CN |
| G-P1-12 | 成交额断点修复: SH_AMOUNT/SZ_COMPONENT_AMOUNT/CN_TOTAL_TURNOVER(注册在场 L2077/L2101/L2125;当日档 `turnover` None [实取·同上]) | 同 G-P1-10 备源;**依赖用户授权** | 日 | CN |
| G-P1-13 | 南北向资金断点修复: SB_FLOW(注册在场 L2005;当日档 `southbound` None [实取·同上]) | akshare 港股通(免费)/tushare(限流);**依赖用户授权** | 日 | HK |
| G-P1-14 | 中国LPR(1Y/5Y) | akshare(免费无凭证,境内直连,已在既有代码技术栈)/国家统计局与央行公告页(免费无API,工程化成本登记);tushare(需积分凭证)→ **PENDING 报批**;**依赖用户授权**(china 通道扩展) | 月(每月20日) | CN |
| G-P1-15 | 中国CPI/PPI同比 | 同 G-P1-14 | 月 | CN |
| G-P1-16 | 中国官方制造业PMI | 同 G-P1-14 | 月 | CN |
| G-P1-17 | 社会融资规模增量/新增人民币贷款 | 同 G-P1-14 | 月 | CN |
| G-P1-18 | 中国7天逆回购利率(政策利率) | 央行公开市场操作公告(免费)/akshare(免费);**依赖用户授权** | 决议日不定期 | CN |
| G-P1-19 | 美国GDP环比折年(现库就业/通胀在场面较全,GDP 零注册) | BEA API(免费无凭证,循预授权③);FRED 镜像(免费但 FRED API key=凭证——**既有 macro 通道已在用,新增序列沿用既有凭证;如需扩量级→PENDING 确认**) | 季 | US |

(US/GLOBAL 现场较全,不扩列;GLOBAL 12 条与 US 49 条在场见 b.2,如实不列为缺口。)

### 跨分支登记(数据线并行成果;不承担行级引用义务,不入本 AC 行级核验面)

| 分支 | 尖端全SHA [实取·git ls-remote origin,2026-11-02] | 成果与发现(引自驱动注入摘要,[示意·非实取·跨分支登记,本包未在 checkout 复核]) |
|---|---|---|
| dev/data-inventory | `7cbef4c9bd25586ef03fc02819ae6792d0929fa0` | data_inventory 盘点工具+缺失诊断交付(W1) |
| dev/data-coverage | `06f715b6be34dedd69f6776b1947238708de0563` | metric_coverage_audit 工具+15测试+81行覆盖报告;覆盖实测 N71/S8/B2/C0/U0;债务清单10项;MARGIN_BAL/SH_PE 双断点;china 通道12指标中8个源端失败;test_p4_fixes DEV 红=在案数据依赖 |

### 已知缺口小节(供 DESIGN §五承接;结构性,非数据项)

- K-1 registry 无经济体归属字段(81条目零 `economy` 类字段 [实取·b.1 entry 字段集: asset_class/calc/calendar/criticality/display_name/frequency/freshness/identity/metric_id/notes/release_semantics/source/source_symbol/status/unit/validation/value_type])
- K-2 JP/EA 本币在岸市场面零注册(b.1 汇总: JP 2/EA 4 全为汇率或离岸代理)
- K-3 CN 注册在场但四组采集断点(b.3 COL-2 实况+G-P1-10..13)
- K-4 评分/装配/报告基线为美国单一经济体视角(ASM-2 实体仅消费 US 事实;ASM-1 数据包无经济体分节)
- K-5 E2E-A 三模块与 E2E-B 中间表示未落地(P0-3 在途),四经济体查询/档案衔接只能先立约定(DESIGN §四)
- K-6 快照通道面固定四通道(SNAP-2 `resolve_inputs` 无 jp/ea 通道),新经济体数据无合法进入口——与「新研究模块必须走快照+门禁」红线共同要求:扩展=加通道,**不是**绕开
