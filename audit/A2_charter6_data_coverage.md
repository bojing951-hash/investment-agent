# Charter 6 审计①: 金融数据与历史覆盖(A2)

- 审计对象: dev/deep-macro-v1 @0f92151(与 main 同源),只读审计+本地实跑 catalog
- 日期: 2026-11-09 | 审计人: A2 | 红线遵守: 未改代码、未动 LIVE、未调任何在线 API(全部结论来自仓内代码+已落盘数据档+本地 catalog 实跑)
- 结论速览: 深度天花板=三个硬编码窗口(macro L203 / global L148+283 / china L237-238),全部一行级可参数化;真正缺失的是 US 实际 GDP 与估值序列;BTC**并非缺失**;EA/日政策利率是"有最新值无历史",不是"完全无序列"。

---

## 0. 实况调查复核(协调方数据 + 勘误)

### 0.1 catalog 实测复核(ia_cli.py history → series_capable_metrics)——协调方数字基本准确

共 **71 条**;频率分布 daily 52 / monthly 11 / weekly 1 / 无频率 7。抽核:
FED_FUNDS n=22 ✓、CPI n=20 ✓、UNEMPLOYMENT n=21 ✓、NFP n=22 ✓、ICSA n=96 ✓、
UST_10Y n=462 ✓、TIPS_10Y n=462 ✓、HY_OAS n=484 ✓、SPX n=251 ✓、GOLD_F n=250 ✓、
DXY n=250 ✓、NIKKEI225 n=251 ✓、VIX n=254 ✓、USDJPY n=261 ✓。

**勘误与补全(与协调方清单的差异)**:

| 项 | 协调方结论 | 实测勘误 |
|---|---|---|
| BTC_USD | 完全无序列 | **错。BTC 已在 catalog**: daily n=366(2025-11-08→2026-11-08,含周末=加密 7d 日历),来源 yfinance BTC-USD,且已内置"UTC 完结日K"纪律(global_market_collector.py L98-115)。缺的只是深度(1y),不缺序列 |
| EA_POLICY | 完全无序列 | **半错。registry 已有 ECB_DFR/ECB_MRO**(ea_market_collector),数据档有**最新值**(DFR=2.5 @2026-09-16,带 prev_value),但 payload 只存最新值+前值,**无 series 数组** → 进不了 history catalog。属"有值无史" |
| JP 政策利率 | 完全无序列 | **半错。registry 已有 JP_POLICY_RATE**(japan_rate_collector,源=FRED fredgraph CSV `IRSTCI01JPM156N`,japan_rate_collector.py L39-40),但解析**只取最后一个非空行**(L"取最后一个非空值行=最新已发布期")→ 有值无史 |
| US_REAL_GDP | 完全无序列 | **确认属实**:registry 102 条中零 GDP 条目,FRED_SERIES(macro_collector.py L18-46)无 GDPC1 |
| 估值类疑似全缺 | 待确认 | **分三种情况**:①US 估值=真缺(registry 无任何 PE/PB/CAPE 条目;FRED 无现成 PE;Yahoo ^GSPC 无 PE 属实);②CN 估值=**有最新值无史**(china_20261108.json `valuation/000001.SH/pe_ttm=16.0` + 300/500/1000 + pe=16.83,registry 有 SH_PE 但无 series);③PB=全缺(见 §2.5) |

### 0.2 更深一层的结构性事实(协调方未列,案例B相关)

**registry 102 条 vs catalog 71 条——31 条注册指标无历史能力**。catalog 收录规则(scripts/workbench_data.py L171-215)= 快照 series_store ∪ 采集档含 `series.dates` 的键(仅扫 `macro_/global_/rate_economy_` 前缀的**最新一档**)。无 series 的值型通道:

- **rate_expectations**(DFF/DFEDTARU/DFEDTARL/ZQ_F1_PRICE): 最新值型,无史
- **ea_market_collector**(ECB_DFR/ECB_MRO/BUND_2Y/10Y/EA_HICP_YOY/DAX/CAC40): payload=observations+policy_rates 最新值;且实测 **Bundesbank 源失败**(ea_20261108.json alerts: `BBK_WU3146源获取失败:RemoteDisconnected`)→ Bund 收益率实际断供;EA_HICP_YOY stale 至 2025-12
- **japan_rate_collector**(JP_POLICY_RATE/JGB2Y/5Y/10Y): 最新值型(fredgraph CSV 只取末行 + MOF jgbcme.csv 只取当日曲线)。**MOF jgbcme.csv 本身是全史单文件**(1974 至今每日全曲线),扩展近乎免费
- **china 宏观/估值**(CN_LPR/CN_CPI_YOY/CN_PPI_YOY/CN_PMI_MFG/CN_NEW_LOANS/SH_PE 等 15 条): 最新值型
- **jp_market_collector**: NIKKEI225 有 series(n=251,在 catalog),JP_CPI_TOKYO_YOY 值型

另: catalog 含 7 条无频率别名行(BRENT/CNY=X/GBPUSD=X/GOLD/JPY=X/SILVER/WTI)——原始符号名漏进 series_store 的卫生问题,建议 B 顺手去重(非本审计重点)。

### 0.3 根因定位复核——三处硬编码窗口全部属实

1. `scripts/macro_collector.py:203` — `fred.get_series(series_id, observation_start='2025-01-01')` ✓
2. `scripts/global_market_collector.py:148` — `def fetch_all(period="1y")` + `:283` 调用点 `fetch_all(period="1y")` ✓(yfinance,period 参数直通 Yahoo)
3. `scripts/china_market_collector.py:237-238` — `start_date_week = today-10d; start_date_year = f'{today.year}0101'`(当年窗口;实测 SHCOMP/SZCI/CHINEXT first=2026-01-05 n=203,HSI/HSCEI first=2025-07-23 n=320)✓
4. 补充第 4/5 处: `ea_market_collector` ECB API URL 内嵌 `startPeriod=2024-01-01`(ea_20261108.json sources 可见);`japan_rate_collector` 结构性只取末行(见 §0.1)

---

## 1. 采集窗口扩展可行性清单(10yr)

### 1.1 逐 collector 现状与改法

| collector | 现状窗口 | 10yr 改法 | 上游支持 | 限流/配额风险 |
|---|---|---|---|---|
| **macro_collector**(FRED, fredapi, FRED_API_KEY) | observation_start='2025-01-01' 硬编码;27 series(L18-46) | 参数化 start(配置/env,如 MACRO_HISTORY_START 或固定 '2015-01-01')。fredapi `get_series(observation_start=…)` 原生支持全史 | FRED 全史:CPIAUCSL 1913+、FEDFUNDS 1954+、DGS 1976+、PAYEMS 1939+、GDPC1 1947+;BAML OAS 族 1996+;DFII5/10 与 T5YIE 2003/1999 起(**≥10yr 全部够用**) | 免费档 ~120 req/min,27 series/次远低于限;单次全史月频系列极小 |
| **global_market_collector**(yfinance→Yahoo) | period="1y" 默认值+调用点双处 | 参数化 period('10y' 默认;备选 'max',^GSPC 可回 1927 但体积大,建议默认 10y、CLI 旗标放开 max)。yfinance period/start/end 原生支持 | Yahoo 10y daily 全支持;BTC-USD 2014+ | 无 Key 免费非官方 API:现有每资产 2 次重试已备;**launchd NO_PROXY=× 导致 429 的坑已在文件头注记**(L10)。32 资产×10y 单轮 60-120s 可接受;建议保持逐资产间隔 |
| **china_market_collector**(纯 requests,东财/新浪等免费端点) | 指数=当年窗口(L237-238);另有 1mo/ytd 辅助窗口(L357/367) | 指数 K 线端点改传 start_date=今日-10y(东财 kline 端点支持长区间);估值/宏观值型通道见 §2.5 | 东财历史 K 线全史可得 | 免费端点反爬/限流风险中等:保持现有分批 sleep;**不依赖 tushare(无积分配额问题)**,akshare 未使用 |
| **ea_market_collector**(ECB Data Portal + Bundesbank) | ECB URL 内嵌 startPeriod=2024-01-01;BBK 源故障中 | DFR/MRO 改 startPeriod=1999(或整段去参=全史)+ **解析全 CSV 行入 series**(现只存末值);BUND 走 BBK 修复(RemoteDisconnected: 加 UA/重试/退避)或换源 | ECB Data Portal 免费无 Key,全史 1999+;limit 宽松 | 低;BBK 偶发断连需重试逻辑 |
| **japan_rate_collector**(FRED fredgraph CSV + MOF jgbcme.csv) | 两源都只取**最后一行** | fredgraph CSV 本身返回 IRSTCI01JPM156N 全史(月频 1960s+)——解析全部行入 series 即得 10yr+;jgbcme.csv 同理是全史单文件,多行解析即得 JGB 曲线全史 | 两源全史现成,**零新增请求面** | 极低(单文件 GET) |
| **jp_market_collector**(yfinance) | 随 global 同款 1y(period 在其自身调用点) | 同 global 参数化 | 同上 | 同上 |
| **rate_expectations**(DFF/联邦基金期货) | 值型 | **不在 P0**:对案例B 非必需;若要史,DFF 全史走 FRED_SERIES 一行即可 | FRED DFF 2008+/DFEDTAR 2008+ | 低 |

### 1.2 数据量级估算与性能影响

现状单日档:global_20261108.json **380KB**(1y×32 资产)、macro_20261108.json **293KB**、快照 565KB(series_store 38 序列 + 94 事实)。

扩展 10yr 后估算:
- Yahoo: 32 资产 × ~2510 交易日 ≈ 8 万点 → global 单档 **~3.6-3.8MB**(≈现 10 倍)
- FRED: 日频 14 条 × ~2510 + 月/周 13 条小计 ≈ 3.7 万点 → macro 单档 **~1.2-1.5MB**
- 两处合计: 快照 series_store 同比放大 → research_snapshot ≈ **5-6MB**;data/daily 每天 +5MB,一年累计 ~1.8GB(见 1.3 处置)
- 性能: ia_cli/workbench 单档 JSON 解析 5MB ≈ 百毫秒级,可接受;compare/相关性按 --start/--end 取窗,已有月网格聚合(A-fin),不受全长影响;e2e 展示层若做全序列渲染需分页/抽样,建议 B 在 UI 层截尾展示(引擎层不动)

### 1.3 增量写入 vs 全量重拉(关键架构判断)

**现状=每次全量重拉+整档覆盖写**(macro/global 每日重取整个窗口重写 `data/daily/{prefix}_YYYYMMDD.json`;不读旧档)。

**建议: 保持全量重拉,不做增量合并**。理由:
1. FRED 27 请求/Yahoo 32 下载的单轮成本在 10y 窗口下仍为秒级-分钟级,幂等且无合并边界 bug(修订值自然被下次重拉纠正);
2. 增量合并(读旧档 series + append 新日期)在 FRED **月频修订**(CPI/NFP 回溯数月修订)下必须处理"同日改值"分支,复杂度不值;
3. data_assembler 从**快照**装配(不直接读历史 daily 档),快照构建只取最新档 → 下游零改动。
配套两条: (a) 10y 落地后给 data/daily 加**保留策略**(如仅留近 90 日全量档+每月 1 份归档,或旧档 gzip)防 1.8GB/年膨胀;(b) backfill 一次性动作(参数开大窗口跑一轮)与日常窗口分离。

---

## 2. 缺失序列补齐清单

每项: 建议序列 ID | 来源 | 频率 | 单位族 | registry 归属。

| # | 指标 | 序列 ID/源 | 频率 | 单位族 | registry 归属 | 说明 |
|---|---|---|---|---|---|---|
| 1 | 美国实际 GDP | **FRED GDPC1**(Real GDP, SAAR, chained 2017$, 1947+) | quarterly | level(price 族,变化率由 compute_series_changes 现成机制派生 QoQ/YoY) | macro_collector(FRED_SERIES 加一行+registry 条目) | 案例B"增长结构"主锚;发布滞后约 27 天(registry release_date_available 已有机制) |
| 2 | 欧元区政策利率 | **首选 FRED ECBDFR**(daily, 1999+,与现有 fredapi 通道一行接入);或 ea collector 解析 ECB Data Portal 全 CSV(startPeriod=1999) | daily | rate | ECB_DFR 条目已存在,补 series 通道 | 双路取一即可;建议 FRED 路(复用 macro 通道,少一个解析器);BBK 故障另行修 |
| 3 | 日本政策利率 | **FRED IRSTCI01JPM156N**(monthly, OECD 源,1960s+)解析**全部行**入 series(源已在用,现只取末行) | monthly | rate | JP_POLICY_RATE 条目已存在 | 口径披露: 该系列=央行即时利率(BOJ 目标利率的 OECD 镜像,负利率期如实反映);BOJ 官网目标利率无干净 API,如需官方口径另做页面抓取(不建议 P0) |
| 4 | BTC | **无需新增**——BTC-USD 已在(global WATCHLIST),随 §1.1 窗口参数化自动得 10y(2014+) | daily(7d 日历) | price | BTC 条目已存在 | UTC 完结日K纪律已内建,直接受益 |
| 5 | 美股估值(案例B 估值结构主锚) | **Shiller ie_data.xls**(耶鲁官网 http://www.econ.yale.edu/~shiller/data/ie_data.xls,月频 1871+,含 Price/Earnings/**CAPE**/Dividends/CPI,免 Key 单文件下载) | monthly | ratio(other 族,支持分位数统计) | 新增 2-3 条: SPX_CAPE / SPX_PE_TTM(可加 SPX_REAL_PRICE) | **CAPE 是 5-10yr+ 历史相似期研究的估值标准工具**,1871 起历史分位直接可算;FRED 无 PE、Yahoo ^GSPC 无 PE 属实,Shiller 官方数据是最优免费源。注意 xls 解析(sheet 名/表头变动)需容错+源版本注记 |
| 6 | 美股 PB | **声明不可得**(如实披露口径限制): Shiller 无 book value;multpl.com 可抓但非 API、结构脆弱不建议进生产;用"价格+盈利增长近似估值"仅可作最后备选且必须显式披露为近似口径 | — | — | registry 登记为 unavailable+note | 纪律: 宁缺毋假,engine 侧拒答优于编造 |
| 7 | A 股估值历史 | SH_PE 现只有最新值;补**日频 PE 历史**: 东财/乐古乐(legulegu)指数 PE 历史端点(免 Key)或 akshare 封装(项目未用 akshare,建议继续纯 requests) | daily | ratio | SH_PE 条目已存在,补 series | 已有 000001/300/500/1000 四口径最新值,历史端点同源可得;限流中等,分批+sleep |
| 8 | EA/日/中其余值型通道历史化 | ECB HICP 全史(ECB API)、CN 宏观(东财/统计局端点月频全史)、JGB 曲线(MOF jgbcme.csv 全史多行解析) | 月/日 | 各归其族 | 条目均已存在 | 非案例B 硬前置,按 P1.5/P2 排 |

---

## 3. 金融正确性风险(窗口扩展后)

### 3.1 vintage/修订口径

- **现状**: FRED 通道返回**最新修订口径**(real-time 点时数据需 ALFRED vintage)。CPI/NFP/PAYEMS 回溯修订(NFP 年度基准修正可达 ±10 万级)。扩展到 10yr 后,历史段的"今天口径"值≠当时市场所见值。
- **披露机制已在**: registry 已有人工登记键 `observation_period_kind`/`release_date_available`,catalog 透传为 `time_semantics`(workbench_data.py L181-184,A-fin 落地)。**要求 B 补一个字段**: `revision_semantics='latest_vintage_asof_collected'`(registry 顶层或逐条),研究输出引用历史宏观值时必须随附该披露——案例B 事后演变叙述用最新修订口径是学界惯例,可接受,但**不得默不作声**。
- **可选增强(P3)**: ALFRED 同一 FRED Key 免费,`vintage_date` 参数可取点时真值(PAYEMS/CPIAUCSL 覆盖优)。仅当案例B 裁决要求"当时所见"严格口径时才做,默认不做。

### 3.2 未来信息泄漏防护(对数据层的要求)

- 相似期检索必须只用锚点日之前观测: 数据层已具备条件——所有 series 带观测日期数组,compare/相关性已有 `--start/--end`(correlation_calculator)。**要求**: ①案例B 引擎侧切片以 `observation_date ≤ anchor_date` 为硬边界,禁止任何"取最新"默认路径;②月频指标的**发布滞后**(GDP ~27 天/CPI ~15 天)意味着锚点日 T 可用的最后观测是 T-1/T-2 期,registry 的 release_date_available 键就是为此准备,切片逻辑必须消费它(而非只按观测期截断);③快照 target_date 已有,新增 10yr 序列不得改变"快照=研究时点冻结"的语义(快照只存采集时点已见数据,天然不泄漏)。
- 跨日历对齐: BTC 7d 日历 vs 交易日历 vs 月频——A-fin 月网格+time_semantics 已建,新增 GDPC1(季频)走月网格族聚合披露,机制现成。
- Yahoo 复权一致性: yfinance 新版默认 auto_adjust=True(近似全收益价),10yr 跨度下复权口径必须固定并在源注记中声明(与 1y 时代可比性),建议显式传 auto_adjust 参数不留默认。

### 3.3 序列起点参差

10yr 窗口下并非所有序列都满 10yr(BAML OAS 1996+、DFII 2003+、BTC 2014+、ECBDFR 1999+均够;Shiller 1871+;但若后续接 2015 年前新兴序列需注意)。catalog 的 first/n 字段已如实透传——案例B 相似期匹配必须按"共同可用窗口"收缩,不得静默 pad。

---

## 4. 最小必要开发清单(给 B,按优先级)

**P0 —— 案例B(历史相似期 5-10yr+)硬前置,不做则案例B 无法启动**
1. `macro_collector.py:203` observation_start 参数化(配置常量/env,默认 10yr 起点),一次 backfill 全量重拉。
2. `global_market_collector.py:148+283` period 参数化(默认 '10y';'max' 留 CLI 旗标);jp_market 同步;yfinance 显式 auto_adjust。
3. 下游耐长序列验证: compare/correlation/e2e/快照在 ~2500 点序列上回归(现测试面多用短窗,需加一条长序列 fixture 测试);catalog first/n 透传不变。
4. data/daily 保留策略(90 日+月度归档或 gzip)防 1.8GB/年。

**P1 —— 结构完整性(案例A/C 现状研究+案例B 输入面)**
5. FRED_SERIES += GDPC1(US 实际 GDP,季频)+ registry 条目(§2#1)。
6. JP_POLICY_RATE 历史化: fredgraph CSV 全行解析(源零新增,§2#3)。
7. ECB_DFR 历史化: FRED ECBDFR 一行接入(§2#2);顺修 BBK RemoteDisconnected(UA/重试)恢复 BUND。
8. BTC 深度: 随 #2 自动获得,验证 2014+ 起点即可。

**P1.5/P2 —— 估值面(案例B"估值结构"硬前置为 #9;CN 估值为 P2)**
9. Shiller CAPE/PE 采集器(ie_data.xls 月频,免 Key;新小 collector 或 macro 扩展)+ registry SPX_CAPE/SPX_PE_TTM(§2#5)——**案例B 四结构(增长/通胀/利率/估值)中估值唯一可行解**。
10. SPX PB 登记 unavailable+口径披露(§2#6)。
11. CN SH_PE 日频历史(东财/legulegu 端点,分批限速)(§2#7)。
12. JGB 曲线历史(MOF jgbcme.csv 多行解析)+ EA HICP/CN 宏观历史化(§2#8)。

**P3 —— 正确性增强(非前置)**
13. registry 增 `revision_semantics` 披露键+研究输出随附(§3.1)。
14. ALFRED 点时数据选项(仅当案例B 裁决要求)(§3.1)。
15. catalog 7 条无频率别名行去重(卫生项)。

**依赖关系一句话**: 案例B = P0 全部 + P1#5-8 + P2#9;案例A/C(现状结构)主要依赖 P1 缺失序列与现有 71 条短窗数据,不需要 10yr 深度;P2#11/P3 与案例B 解耦可并行。

---

## 附: 审计证据索引(文件:行)

- scripts/macro_collector.py L18-46(FRED_SERIES 27 条)、L203(observation_start 硬编码)
- scripts/global_market_collector.py L10(launchd NO_PROXY/429 注记)、L48+(WATCHLIST)、L98-115(BTC UTC 日K纪律)、L148/L283(period="1y")
- scripts/china_market_collector.py L237-238(当年窗口)、L357/367(1mo/ytd)
- scripts/japan_rate_collector.py L39-40(IRSTCI01JPM156N fredgraph URL)、fetch_fred_policy_rate(只取末行)
- scripts/ea_market_collector.py L272-277(save_daily);data/daily/ea_20261108.json(sources startPeriod=2024-01-01、BBK 失败 alert、policy_rates 末值)
- scripts/workbench_data.py L171-215(series_capable_metrics 收录规则=series_store ∪ macro_/global_/rate_economy_ 最新档含 series)
- config/metric_registry.json(102 条;含 ECB_DFR/JP_POLICY_RATE/SH_PE 已注册,无 GDP/无 US 估值)
- data/daily/china_20261108.json(valuation.pe_ttm 最新值在)、japan_20261108.json、jp_20261108.json(NIKKEI225 series 在)
- run_weekly.py L143-167(jp_/ea_/japan_ 步骤在快照后执行=T-1 回退;调度面全)
