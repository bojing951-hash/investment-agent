# P0-2 W1 指标注册表金融语义审计报告(81项)

- 契约: IA-P0-2-W1-AC-v1.0 / 总冻结: IA-P0-2-AC-v1.0 / 开发指令: IA-P0-2-W1-DEV-v1.0
- 固定基线: `50b5d13db6c477084c6f4b3944b7bd08a8e329d6`(P0-1验收Commit) | 分支: dev/p0-2-w1 | 生成: 2026-10-29T10:06:39+08:00
- 角色: 开发自检;独立验收由 Agent 4 执行

## 1. 总量与分类

| 项 | 值 |
|---|---|
| 指标总数/唯一ID | 81 / 81 |
| active / active+core / deprecated | 80 / 32 / 1 |
| VERIFIED_CONSISTENT | 77 |
| FIXED | 3(NVDA/AAPL/MSFT) |
| REVIEW | 1(DXY) |
| BLOCKED | 0 |

## 2. 审计方法与证据分级

1. **程序字段一致性**: 逐项字段在场性/类型/封闭集合/结构(registry_semantics,当前error=0/review=0);事实链消费点通读(fe.make_fact/rp.fact_structure_problems/rp.fact_source_problems/sb.build_anchors/rp.core_metric_ids)。
2. **来源/工具语义确认**: 采集器符号表快照(WATCHLIST 38项/FRED_SERIES 27项/rate 4项/china通道12项)与注册表source_symbol逐项比对——全部一致;identity.instrument在scripts/tests/run_weekly零消费(W1-03前),修复无运行时行为影响。
3. **真实金融数据准确性**: **不在W1范围,未认证**(见not_verified_statements)。

## 3. 确认修复(W1-02)

| metric_id | 字段 | 修复前 | 修复后 | 其他字段 |
|---|---|---|---|---|
| NVDA | identity.instrument | `etf` | `single_stock` | 逐字节未动 |
| AAPL | identity.instrument | `etf` | `single_stock` | 逐字节未动 |
| MSFT | identity.instrument | `etf` | `single_stock` | 逐字节未动 |

依据: 个股(single_stock)是发行人权益凭证,不是基金份额(ETF);指令确认为确定性身份错误。修复后由registry_semantics规则R-STOCK-NOT-ETF/R-ETF-EXCLUSIVITY/R-INSTRUMENT-CLASS机器拦截同类回归。

## 4. REVIEW项(1)

- **DXY**: instrument=index而calc注明'ICE美元指数期货结算近似'——DX-Y.NYB报价口径(ICE美元指数计算值 vs 期货结算价)需外部来源核实,W1离线环境无法确认
  - 依据: 字段间自洽(index身份+index_point单位+fx日历+符号DX-Y.NYB一致);唯一未能离线确认项为报价源口径本身;处置: 不修改(无确定性错误);留REVIEW待外部来源核实后定案

## 5. 系统性发现(不属单指标错误)

- **S1·注册表freshness窗为声明性元数据,运行时未按其执行**(P2(W2交接)): fact_engine.validate_fact读取freshness.max_calendar_lag_days至局部变量fr后未使用,实际生效窗为按频率硬编码(日7/周16/月92)。注册表声明值(BTC 2/SPX 5/UST 7/月频45/DFEDTAR 45/ICSA 16)与执行窗存在差异(BTC 2vs7、月频45vs92、DFEDTAR 45vs7)。
  - 处置: W1未修改时效政策与窗口(指令§5.2明令归W2);本轮仅在registry_semantics校验freshness结构合法性。登记移交W2。
- **S2·china通道source_symbol语义=采集器通道键/真实指数代码**(P2(说明)): china类source_symbol(HSI=hkHSI/SB_FLOW=southbound/SH_PE=valuation等)为china_market_collector输出JSON键/通道键而非交易所符号;normalize_china以显式映射消费,语义一致。
  - 处置: 无需修改;审计报告显式记录该通道符号语义。
- **S3·ZQ联邦基金期货calendar=commodity**(P2(说明)): trading_calendar.MARKETS无独立利率期货日历;ZQ(CME/Globex)归入commodity桶,两个fed_futures指标一致使用,新鲜度窗5天按日频采集校验。
  - 处置: 桶选择为既有设计,两指标一致;如后续需要精确CME日历属W2+议题,本轮不动。
- **S4·派生指标source标注存在两种惯例**(P2(说明)): REAL_*/HY_IG_DIFF/ZQ_IMPLIED_AVG标注source='fact_engine(derived)'(计算模块),NFP_MOM_K标注source='macro_collector'(数据通道);实际collector均为fact_engine。rp._DERIVED_DEPS分支按依赖集授权(先于source查找),sb锚点分支显式排除macro_count_derived——两惯例行为一致,无冲突。
  - 处置: 记录惯例差异;统一命名属后续清理项,不影响正确性,本轮不改(最小修改原则)。

## 6. 81项逐项清单

| # | metric_id | asset_class | instrument | unit | source | 符号比对 | 结果 | 关键注记 |
|---|---|---|---|---|---|---|---|---|
| 1 | SPX | equity_index | index | index_point | global_market_collector | ✓ | VERIFIED | calc显式'非ETF;SPY为独立指标'——指数与代理ETF双身份分离声明 |
| 2 | NDX | equity_index | index | index_point | global_market_collector | ✓ | VERIFIED |  |
| 3 | RUT | equity_index | index | index_point | global_market_collector | ✓ | VERIFIED |  |
| 4 | VIX | volatility_index | index | index_point | global_market_collector | ✓ | VERIFIED |  |
| 5 | NVDA | single_stock | single_stock | usd | global_market_collector | ✓ | **FIXED** |  |
| 6 | AAPL | single_stock | single_stock | usd | global_market_collector | ✓ | **FIXED** |  |
| 7 | MSFT | single_stock | single_stock | usd | global_market_collector | ✓ | **FIXED** |  |
| 8 | TLT | bond_etf | etf | usd | global_market_collector | ✓ | VERIFIED |  |
| 9 | IEF | bond_etf | etf | usd | global_market_collector | ✓ | VERIFIED |  |
| 10 | SHY | bond_etf | etf | usd | global_market_collector | ✓ | VERIFIED |  |
| 11 | HYG | bond_etf | etf | usd | global_market_collector | ✓ | VERIFIED |  |
| 12 | LQD | bond_etf | etf | usd | global_market_collector | ✓ | VERIFIED |  |
| 13 | DXY | fx_index | index | index_point | global_market_collector | ✓ | **REVIEW** |  |
| 14 | EURUSD | fx_rate | ∅ | usd_per_eur | global_market_collector | ✓ | VERIFIED |  |
| 15 | GBPUSD | fx_rate | ∅ | usd_per_gbp | global_market_collector | ✓ | VERIFIED |  |
| 16 | USDJPY | fx_rate | ∅ | jpy_per_usd | global_market_collector | ✓ | VERIFIED | calc标注与EURUSD方向语义相反(上涨=美元升值)——防方向倒置误读 |
| 17 | USDCNY | fx_rate | ∅ | cny_per_usd | global_market_collector | ✓ | VERIFIED | calc标注上涨=人民币贬值 |
| 18 | GOLD_F | commodity_futures | futures_front_continuous | usd_per_oz | global_market_collector | ✓ | VERIFIED |  |
| 19 | SILVER_F | commodity_futures | futures_front_continuous | usd_per_oz | global_market_collector | ✓ | VERIFIED |  |
| 20 | WTI_F | commodity_futures | futures_front_continuous | usd_per_barrel | global_market_collector | ✓ | VERIFIED | 与WTI_SPOT_M构成期货/现货月均双身份,cross_metric_checks有口径差异披露 |
| 21 | BRENT_F | commodity_futures | futures_front_continuous | usd_per_barrel | global_market_collector | ✓ | VERIFIED |  |
| 22 | GLD | spot_commodity_etf | etf | usd | global_market_collector | ✓ | VERIFIED | ETF代理现货黄金:is_proxy+proxy_of,未冒充现货指数 |
| 23 | USO | commodity_futures_etf | etf | usd | global_market_collector | ✓ | VERIFIED | ETF代理WTI期货近月:展期损耗披露,未与期货本体混同 |
| 24 | EEM | country_etf_proxy | etf | usd | global_market_collector | ✓ | VERIFIED |  |
| 25 | EZU | country_etf_proxy | etf | usd | global_market_collector | ✓ | VERIFIED |  |
| 26 | FEZ | country_etf_proxy | etf | usd | global_market_collector | ✓ | VERIFIED |  |
| 27 | EWU | country_etf_proxy | etf | usd | global_market_collector | ✓ | VERIFIED |  |
| 28 | EWG | country_etf_proxy | etf | usd | global_market_collector | ✓ | VERIFIED |  |
| 29 | EWJ | country_etf_proxy | etf | usd | global_market_collector | ✓ | VERIFIED |  |
| 30 | INDA | country_etf_proxy | etf | usd | global_market_collector | ✓ | VERIFIED |  |
| 31 | FXI | country_etf_proxy | etf | usd | global_market_collector | ✓ | VERIFIED | proxy_of注明成分含港股上市中资股、非A股指数 |
| 32 | BTC | crypto | spot_crypto | usd | global_market_collector | ✓ | VERIFIED | 7×24自然日观测,freshness窗2天(结构合法) |
| 33 | UST_2Y | rates_yield | index_rate_series | percent | macro_collector | ✓ | VERIFIED |  |
| 34 | UST_5Y | rates_yield | index_rate_series | percent | macro_collector | ✓ | VERIFIED |  |
| 35 | UST_10Y | rates_yield | index_rate_series | percent | macro_collector | ✓ | VERIFIED |  |
| 36 | UST_30Y | rates_yield | index_rate_series | percent | macro_collector | ✓ | VERIFIED |  |
| 37 | HY_OAS | credit_spread | index_rate_series | percentage_point | macro_collector | ✓ | VERIFIED |  |
| 38 | BB_OAS | credit_spread | index_rate_series | percentage_point | macro_collector | ✓ | VERIFIED |  |
| 39 | B_OAS | credit_spread | index_rate_series | percentage_point | macro_collector | ✓ | VERIFIED |  |
| 40 | CCC_OAS | credit_spread | index_rate_series | percentage_point | macro_collector | ✓ | VERIFIED |  |
| 41 | IG_OAS | credit_spread | index_rate_series | percentage_point | macro_collector | ✓ | VERIFIED |  |
| 42 | TIPS_5Y | real_rate | index_rate_series | percent | macro_collector | ✓ | VERIFIED |  |
| 43 | TIPS_10Y | real_rate | index_rate_series | percent | macro_collector | ✓ | VERIFIED |  |
| 44 | BEI_5Y | inflation_expectation | index_rate_series | percent | macro_collector | ✓ | VERIFIED |  |
| 45 | BEI_10Y | inflation_expectation | index_rate_series | percent | macro_collector | ✓ | VERIFIED |  |
| 46 | CURVE_2S10S | curve_slope | index_rate_series | percentage_point | macro_collector | ✓ | VERIFIED |  |
| 47 | FED_FUNDS | policy_rate | macro_series | percent | macro_collector | ✓ | VERIFIED | 月均值口径(与DFF某日时点值区别)写入calc |
| 48 | CPI | macro_index | macro_series | index_point_1982_84 | macro_collector | ✓ | VERIFIED | SA指数,1982-84=100基期编码单位;MoM/YoY由引擎按系列计算 |
| 49 | CORE_CPI | macro_index | macro_series | index_point_1982_84 | macro_collector | ✓ | VERIFIED | 核心CPI(食品能源剔除),SA,1982-84基期 |
| 50 | CORE_PCE | macro_index | macro_series | index_point_2012 | macro_collector | ✓ | VERIFIED | 2012=100链式指数 |
| 51 | UNEMPLOYMENT | macro_rate | macro_series | percent | macro_collector | ✓ | VERIFIED |  |
| 52 | NFP | macro_count | macro_series | persons_thousands | macro_collector | ✓ | VERIFIED | 存量水平(千人);媒体'新增非农'=NFP_MOM_K月差,两者注册分离 |
| 53 | NFP_MOM_K | macro_count_derived | macro_series | persons_thousands | macro_collector | — | VERIFIED | source=macro_collector(数据通道语义)而collector=fact_engine(计算模块)——两组派生标注惯例已在rp._DERIVED_DEPS分支/sb锚点排除显式处理,行为一致(系统性说明S4) |
| 54 | AHE | macro_index | macro_series | usd_per_hour | macro_collector | ✓ | VERIFIED | 名义时薪(美元/小时) |
| 55 | WTI_SPOT_M | macro_price | macro_series | usd_per_barrel | macro_collector | ✓ | VERIFIED | 月度现货均价,与WTI_F日频期货为两个指标(对账仅披露不判错) |
| 56 | UMCSENT | sentiment | macro_series | index_point_1966 | macro_collector | ✓ | VERIFIED | 1966Q1=100 |
| 57 | RSAFS | macro_index | macro_series | million_usd | macro_collector | ✓ | VERIFIED |  |
| 58 | INDPRO | macro_index | macro_series | index_point_2017 | macro_collector | ✓ | VERIFIED | 2017=100工业生产指数 |
| 59 | ICSA | macro_count | macro_series | persons | macro_collector | ✓ | VERIFIED | 周频周四发布,16天窗结构合法 |
| 60 | DFF | policy_rate | index_rate_series | percent | rate_expectations | ✓ | VERIFIED |  |
| 61 | DFEDTARU | policy_rate | ∅ | percent | rate_expectations | ✓ | VERIFIED | identity缺省=历史兼容(统计系列可选身份);value_type=target_band口径显式 |
| 62 | DFEDTARL | policy_rate | ∅ | percent | rate_expectations | ✓ | VERIFIED | 同DFEDTARU |
| 63 | ZQ_F1_PRICE | fed_futures | futures_front_continuous | points | rate_expectations | ✓ | VERIFIED | calendar=commodity(CME/Globex交易时段桶,MARKETS无独立利率期货日历——桶选择见系统性说明S3) |
| 64 | SHCOMP | equity_index | index | index_point | china_market_collector | ✓ | VERIFIED |  |
| 65 | SZCI | equity_index | index | index_point | china_market_collector | ✓ | VERIFIED |  |
| 66 | CHINEXT | equity_index | index | index_point | china_market_collector | ✓ | VERIFIED |  |
| 67 | HSI | equity_index | index | index_point | china_market_collector | ✓ | VERIFIED | source_symbol=hkHSI为采集器通道键(腾讯主通道/yfinance备用),非yfinance符号——通道键语义 |
| 68 | HSCEI | equity_index | index | index_point | china_market_collector | ✓ | VERIFIED | source_symbol=hkHSCEI通道键语义同HSI |
| 69 | HSAHP | spread_index | index | index_point | china_market_collector | ✓ | VERIFIED | 恒生AH溢价指数真实代码 |
| 70 | SB_FLOW | flow | ∅ | hkd_100m | china_market_collector | ✓ | VERIFIED |  |
| 71 | MARGIN_BAL | leverage | ∅ | cny_100m | china_market_collector | ✓ | VERIFIED |  |
| 72 | SH_PE | valuation | ∅ | ratio | china_market_collector | ✓ | VERIFIED |  |
| 73 | SH_AMOUNT | volume_amount | ∅ | cny_100m | china_market_collector | ✓ | VERIFIED |  |
| 74 | SZ_COMPONENT_AMOUNT | volume_amount | ∅ | cny_100m | china_market_collector | ✓ | VERIFIED | 成分口径(非深市全市场)在normalize与notes双披露 |
| 75 | CN_TOTAL_TURNOVER | volume_amount | aggregate | cny_100m | china_market_collector | ✓ | VERIFIED | is_proxy=true:沪市全市场+深证成指成分近似口径,DEGRADED/WARN披露链完备 |
| 76 | REAL_10Y | real_rate | derived | percent | fact_engine(derived) | — | VERIFIED |  |
| 77 | REAL_5Y | real_rate | derived | percent | fact_engine(derived) | — | VERIFIED |  |
| 78 | REAL_SHORT | real_rate | derived | percent | macro_collector(derived) | — | VERIFIED | deprecated:2Y/5Y期限错配由第七轮判定,notes指明替代(REAL_5Y/REAL_10Y);引擎不再产出(rp/fe双侧确认) |
| 79 | HY_IG_DIFF | credit_spread | derived | percentage_point | fact_engine(derived) | — | VERIFIED |  |
| 80 | ZQ_IMPLIED_AVG | fed_futures | derived | percent | fact_engine(derived) | — | VERIFIED | calc含'不得换算降息次数'纪律 |
| 81 | JTSJOL | macro_count | macro_series | persons_thousands | macro_collector | ✓ | VERIFIED | criticality=context(非core),JOLTS职位空缺千人 |

注: 符号比对✓=注册表source_symbol与采集器符号表快照一致;—=派生/通道键语义不适用直接比对。
逐项完整字段(issues_found/basis/impact/action/evidence)见机器可读清单 docs/P0_2_W1_REGISTRY_AUDIT.json。

## 7. 范围声明

- 本审计只覆盖注册表字段一致性与已确认金融语义矛盾;不构成"81项金融数据真实准确"的认证
- 真实价格/利率/计数与外部市场的一致性核验不在W1范围
- 时效窗口政策语义(W2)、新闻情绪模块(W3)、W4/W5业务模块未审计未修改
- 采集器运行时符号表以开发期快照为准(冻结于本报告);采集器后续演进需重新比对
- 真实金融数值准确性(价格/利率/计数与外部市场的一致性)——W1范围外
- 时效政策与有效期窗口数值(freshness仅查结构合法性;语义归W2)
- 采集器运行时实际符号表与source_symbol的一致性(开发期人工核验,见审计报告)
- 未确认asset_class/instrument组合的金融正当性(标review,待人工或后续工作包)
- 新闻/情绪与业务模块口径(W3~W5范围)

