# P0-2 W5-FIX1 终裁前置卷宗 — BTC vs Coinbase 1.34% 七轴独立归因(R003)

- 轮次: Round 003(IA-R003-ATTR,已冻结,用户 2026-11-01 批准"直跑")
- 执行: Agent 3(工程执行Agent),分支 `dev/p0-2-w5-attr`,基点 `10207929c8d505845ac30f8af9a742b124b0f4d5`(`dev/p0-2-w5` 实际最新 HEAD,与交接一致,无更新成果)
- 性质: **只分析,零修复,零代码改动**。本卷宗供 Agent 4 作 W5-FIX1 终裁;本文不裁决验收。
- 证据分级: C=固定GitHub源码 / T=Actions真实日志 / E=完整工程或真实模块链执行 / I=独立隔离反例 / D=开发机或生产侧实际只读取证 / U=未验证。包内文件属"交付物自述+留档原始响应"两类,引用时分别标注;本卷宗所有"包内证据"指 FIX1 证据包成员(哈希见§输入清单,轮末复测一致)。

---

## 0. 输入清单(证据来源+哈希)

| # | 输入 | 标识/哈希 | 分级 |
|---|------|-----------|------|
| 1 | FIX1证据包 `/tmp/w5-evidence/IA-P0-2-W5-FIX1-ACCEPTANCE-EVIDENCE.zip` | SHA256 `b5f070a556d359de9590b816074f36e6c8d38738af07f4b8856c63b89ec647e8`(轮初实测;前缀与登记 `b5f070a5…` **一致**) | I(独立实物) |
| 2 | W5首轮证据包 `/tmp/w5-evidence/IA-P0-2-W5-ACCEPTANCE-EVIDENCE.zip` | SHA256 `6e59f9cb9ad5580b9c2f9e75d9eaff0ed5cb61502af1e0a37ab5c310d739feeb`(轮初实测;前缀与登记 `6e59f9cb…` **一致**) | I |
| 3 | DEV仓库 `dev/p0-2-w5` @ `10207929c8d505845ac30f8af9a742b124b0f4d5` | git(远端 ls-remote 实取同 SHA) | C |
| 4 | 包内 `real_acceptance_20261101_1428.json`(正式验收结构化结果) | 包内 SHA256SUMS 校验 OK(见附录A) | 包内证据(含原始API响应留档) |
| 5 | LIVE `data/daily/global_20261030.json`(正式运行输入,与冻结副本逐字节同源,见§轴③) | SHA256 `62526e8cf2995835e4caab4d22586fd167dee03f8ed4ae21e65077d0b374295d`,**与包内JSON所记快照sha完全一致** | D(生产侧只读) |
| 6 | LIVE `data/daily/global_2026102[789].json`、`global_20261031.json`、`global_20261101.json`(相邻日与后继文件) | 跨文件series对照(§轴⑥) | D |
| 7 | LIVE `scripts/global_market_collector.py`(采集器源码,只读) | 行号引用见各轴 | D |
| 8 | DEV `scripts/real_data_acceptance.py`(验收脚本,只读) | SHA256 `62b2ed82d7dbbcdb23566ffd5772de62c25d23fec3c9c8e9cd6f69204ba12ba1`,与正式运行JSON `code_version.script.sha256` 一致 | C |
| 9 | Coinbase公开API重取(小时线+日线,公开无密钥) | 附录C留档(URL+UTC+SHA256) | I(独立外部) |
| 10 | `/Users/cast/audit/w4-real-data`(正式运行信任根) | **会话不可达(U)**;不可达性由其输入文件经哈希链(#5)与包内 INPUT-INTEGRITY(自述)替代佐证 | U |

**验收对象基本事实(包内证据)**: data_day=20261030(lag=2,`--data-day` 显式指定);acceptance_mode=formal_external_verification;executed_at_utc=2026-11-01T06:27:58Z(=14:27:58 UTC+8,与登记运行时间 2026-11-01 14:28 一致);运行时 git head=`4a19619e450cbf8699b6df4b088d2058b351ff2b`(回填commit 10207929 之前,脚本sha与DEV HEAD一致,见附录A注);overall=FAIL,exit_code=2。

**BTC检查双方数值(包内证据,`checks[3]`)**:
- 我方: value=**78822.59**, observation_date=**2026-10-29**, unit=usd, source={collector: global_market_collector, file: global_20261030.json, retrieved_at: **null**}
- 外部: value=**77780.33**, observation_date=**2026-10-29**, utc_window=2026-10-29T00:00:00Z–23:59:59Z(Coinbase Exchange,USD), evidence=EV-CB-BTC-USD(fetched_at_utc=2026-11-01T06:28:20Z,http 200,body_sha256=9841ce9b…,121字节)
- 判定: difference_pct=**1.34** > tolerance_pct=0.5 → **FAIL**(规则`|our_close − ext_close| / ext_close × 100 ≤ 0.5%(两侧均为UTC日收盘,USD计价)`,偏差四舍五入至0.01%)
- 与自述核对: 交付文档§7"BTC FAIL 1.34%(与W5基线同一真实差异)"及README_EVIDENCE自述**一致**(D2自述来源+包内结构化证据双重核对;W5首轮包内JSON同配对同值1.34%)。

---

## 1. 七轴逐项归因

> 每轴三态: **确认命中 / 确认排除 / 无法核验(附阻断原因)**。"命中"=该轴机制在本次差异中实际起作用;"排除"=有定量/文档证据证明该轴不是本差异的原因。

### 轴① 比较日是否一致 — **确认排除**

- 双方 observation_date 均为 **2026-10-29**(包内JSON `checks[3].ours/external`;W5首轮JSON同)。引擎侧数据日 20261030(lag=2),其快照内 BTC 最新观测日=2026-10-29;Coinbase 侧按我方观测日取同 ISO 日K。
- 配对代码: DEV `scripts/real_data_acceptance.py:537-538`——`od = o['observation_date']; c = candles.get(od)`,严格同 ISO 日期字符串配对;`L545-548` 校验K线起点为 UTC 日界,否则 NOT_VERIFIED。
- 定量反证(错日不能产生1.34%): 我方78822.59 vs Coinbase 10-28收盘81249.31=2.99%,vs 10-30收盘77180.42=2.13%(§2配对P-D)。
- 结论: 比较日**一致且正确**,不是差异原因。

### 轴② UTC日界和交易平台收盘定义 — **确认命中**(命中形态: "同日界定义下的**日窗未完结**",非"日界错位/错日")

- 双方"日"的边界定义**一致**: Coinbase日K起点均为UTC 00:00Z(包内证据 `start_ts=1793232000/1793318400`,`%86400==0`,脚本L545已校验);我方Yahoo日线对**已完结日**与Coinbase同ISO日收盘差≤0.03%(§2跨源基差表,六日全核)——若两源日界定义错位,完结日不可能逐日对齐到0.03%以内。
- 命中机制: 我方值并非该UTC日的**收盘**,而是该UTC日**尚未走完时**的截断值——采集发生在 2026-10-29 **23:00:17 UTC**(LIVE `global_20261030.json` 顶层 `time=07:00:17`(UTC+8);采集器以本地时间写文件名与time字段,LIVE `scripts/global_market_collector.py:194-200`)。同一ISO字符串"2026-10-29",我方窗口=00:00–23:00Z(23/24),Coinbase窗口=00:00–24:00Z(完整)。
- 日窗完结度直接证据(轴⑥联动): 该UTC日最后一小时(23:00–24:00Z)Coinbase自78860.64跌至77780.33(附录C小时线),跌幅1.39%,即1.34%差异的全部来源。
- 开发者首轮诊断(自述来源)称"我方采集日K的日界/收盘定义与Coinbase UTC日K不同"——本轮独立证据**修正其表述**: 日界定义相同,差异在**取值时点导致日窗未完结**;同文件其"对齐表"数值经本轮独立复核全部正确(见§2)。

### 轴③ 价格来源(Yahoo 与 Coinbase) — **确认排除**(作为1.34%的原因;来源身份事实如下)

- 我方值真实来源字段溯源(D级): LIVE `global_20261030.json` → `data.BTC` 由 `global_market_collector` 写入——`WATCHLIST["BTC"]="BTC-USD"`(采集器L71),`yf.Ticker("BTC-USD").history(period="1y", auto_adjust=True)`(L106-107,默认日线),取 `hist['Close'].iloc[-1]` 为close(L119,L136,L180)、`High/Low.iloc[-1]` 为当日高低(L168-169)、bar索引日期为obs日(L188)。**验收JSON所记78822.59与该文件BTC.close逐位一致,且文件SHA256与验收JSON所记快照sha一致**(输入#5)→ 正式运行输入=该LIVE文件同源冻结副本,数值未在链路中被改动。
- Coinbase证据: `api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400&start=2026-10-29T00:00Z&end=2026-10-30T00:00Z`(包内JSON `external_evidence[1].url`),响应121字节2根日K,10-29收盘77780.33。
- 可比性与基差: 两源对**完结UTC日**收盘的基差≤0.03%(§2六日表: 0.003%~0.026%),远小于0.5%容差,不足以产生1.34%。→ 来源不同本身不是原因。
- 附注(口径事实,非指控): 验收JSON `ours/source/retrieved_at=null`——事实侧未携带采集时刻,验收时框架无从直接感知"该值为盘中截断值"(脚本`_ours`仅透传fact已有source,DEV `real_data_acceptance.py:372-381`);原始global文件顶层`time`字段存在但未进入fact source。

### 轴④ 复权或连续数据处理 — **确认排除**

- 代码事实: `auto_adjust=True`(采集器L107)即yfinance后复权Close。BTC-USD为现货,无分红/拆分,复权因子恒等,不改变价格水平。
- 经验证据(D级): 跨文件series中**已完结历史日值逐文件不变**(10-26=80006.65625、10-27=80805.078125在20261029/30/31/1101四个文件中完全相同)→ 无事后回溯复权修正;且完结值与Coinbase同日差≤0.03%。
- 连续合约/展期: 不适用(现货BTC-USD,非期货连续)。GOLD_F(期货连续)的口径问题包内已单独判NOT_COMPARABLE,与BTC无关。

### 轴⑤ 币种和报价单位 — **确认排除**

- 双方均为BTC/USD美元计价: 我方 unit=usd(包内JSON;脚本L531-533强制非usd即NOT_VERIFIED),ticker=BTC-USD(yahoo,USD报价);外部=Coinbase Exchange BTC-USD现货USD(包内utc_window注明USD)。同币种、同计价、同标的(现货BTC),无汇率/单位换算参与。

### 轴⑥ 采集时间及源数据完整性 — **确认命中**(与轴②同一机制的两面)

- 取数时点: 我方=**2026-10-29 23:00:17 UTC**(LIVE文件`time=07:00:17` UTC+8;采集器`datetime.now()`写文件,L194-200;相邻日文件time均为~07:00本地,佐证每日07:00(UTC+8)定时采集——即每日UTC 23:00取"当日"线)。Coinbase证据=2026-11-01T06:28:20Z抓取的**已完结**历史日K。
- 是否取到未完结candle/盘中价: **是**。四条独立证据链:
  1. **跨文件序列修正**(D): 同一series值 2026-10-29 在 `global_20261030.json`=78822.59375(在途),在次日 `global_20261031.json`=**77775.109375**(完结)——yfinance历史在后继取数中自行覆盖为完结值,证明78822.59是时点值而非该日收盘;
  2. **窗口一致性**(包内+D): 我方high=81771.26 ≤ Coinbase完整日high=81890,我方low=78569.82 ≥ 完整日low=77699——截断窗口的高低价包含关系与"23/24日窗"完全一致;
  3. **同时点市价对齐**(I,附录C): Coinbase 23:00Z小时K open=78860.64,我方78822.59与之差0.05%——我方值就是23:00时点市价;
  4. **量级闭合**(I): 23:00Z小时K open→close=78860.64→77780.33(−1.39%),单独解释全部1.34%。
- 源记录完整性: 我方原始文件完整(哈希链闭合);Coinbase历史日K完结后不可变——本轮2026-11-01T09:59Z重取与正式运行06:28Z所取同K线数值逐位一致(附录C vs 包内证据),完结K稳定性实证。
- 未闭合项(U): yfinance当日请求的**原始响应未留档**,无法直接出示"yahoo当日返回的最后一根bar时间戳=2026-10-29且为在途"的一手响应;由上述1–4间接闭合。采集器console日志亦未入证据包(包内仅有验收脚本自身日志)。

### 轴⑦ 综合判断: 真实数据是否有错误 — **单一原因**(机制横跨轴②⑥表述,非多因叠加)

**总结论**: 1.34%差异的充分且单一原因是: **我方用于验收的BTC值是采集器于 2026-10-29 23:00:17 UTC(数据日晨间定时采集)取到的该UTC日"在途日K"截断值(时点价78822.59),而对照方为Coinbase该UTC日完结后的日K收盘(77780.33);同一ISO日、同一UTC日界定义、同一币种下,两值相差的1.34%恰为该日最后一小时(23:00–24:00Z)的真实跌幅(78860.64→77780.33,−1.39%)。**

- ①~⑥支撑关系: 轴①③④⑤排除(比较日/来源基差/复权/币种均不构成原因,各有定量证据);轴②⑥命中且为同一机制(日窗未完结×取值时点),二者不是独立叠加的两因。
- **"真实数据是否有错误"**: 无证据支持任何一方数据"错误"——我方78822.59是23:00:17Z时点的真实市价(与Coinbase同时点差0.05%),Coinbase 77780.33是完整日真实收盘;两源完结日互差≤0.03%。**差异是采集时点口径事实,不是数值错误**(此为归因结论,不构成验收判定;容差规则文本"两侧均为UTC日收盘"的我方一侧前提在采集口径上未满足,系口径性事实陈述)。
- 缺失证据清单: (a) yfinance当日原始响应(U,见轴⑥);(b) `/Users/cast/audit` 信任根本会话不可达(U,以哈希链替代佐证);(c) 采集器console日志未入包。
- 反预设声明: 本卷宗**不提议、不实施**任何容差放宽、比较日变更或数据改动;§2所有修正配对**仅归因证据,非验收口径变更**。W5-FIX1按原契约的正式结果为 FAIL/exit 2(包内证据),裁决权在 Agent 4。

---

## 2. 定量复核表(可复现: `docs/w5_attr_workspace/recompute_btc_pairings.py` + `.out.txt`)

输入=LIVE只读JSON+包内Coinbase证据+附录C重取(脚本内只读重放,未运行任何生产脚本)。

**主配对表**(差值=|a−b|/b×100,四舍五入0.01%;**仅归因证据,非验收口径变更**):

| 配对 | 定义 | 我方值 | Coinbase值 | 差值 |
|------|------|--------|-----------|------|
| **P-A 验收实际配对** | 我方在途值(23:00:17Z采集) vs 完整UTC日收盘 | 78822.59 | 77780.33 | **1.34%** ←即FAIL值 |
| P-B 修正配对(完结日收盘) | yahoo完结值(次日series定稿) vs 同ISO日Coinbase收盘 | 77775.11 | 77780.33 | **0.01%** |
| P-C 同时点配对 | 我方在途值 vs Coinbase 23:00Z小时K开盘 | 78822.59 | 78860.64 | **0.05%** |
| P-D 错日反证① | 我方在途值 vs Coinbase 10-28收盘 | 78822.59 | 81249.31 | 2.99% |
| P-D 错日反证② | 我方在途值 vs Coinbase 10-30收盘 | 78822.59 | 77180.42 | 2.13% |

→ **产生≈1.34%的唯有P-A**(在途 vs 完整日);**同口径配对P-B(0.01%)与同时点配对P-C(0.05%)均≈0**;错日配对P-D给2.99%/2.13%,排除错日假设。

**完结日跨源基差表**(yahoo完结 vs Coinbase同ISO日,均完整UTC日,六日全核):

| ISO日 | yahoo完结 | Coinbase | 基差 |
|-------|-----------|----------|------|
| 2026-10-26 | 80006.66 | 80008.79 | 0.003% |
| 2026-10-27 | 80805.08 | 80799.51 | 0.007% |
| 2026-10-28 | 81267.59 | 81249.31 | 0.022% |
| 2026-10-29 | 77775.11 | 77780.33 | 0.007% |
| 2026-10-30 | 77198.21 | 77180.42 | 0.023% |
| 2026-10-31 | 77403.48 | 77423.98 | 0.026% |

→ 完结口径下两源六日基差≤0.026%,单日波动(10-29最后一小时−1.39%)才是1.34%的量级来源。

**在途值跨文件演化**(D): 10-29值 78822.59375(1030文件,在途)→77775.109375(1031文件,完结);10-28值 81241.578125(在途,23:56:56Z采集,差0.01%)→81267.585938(完结);10-30值 76813.601562(在途,23:00:15Z)→77198.210938(完结)——采集时点越接近日界,在途值与完结值越接近(23:56采集差0.01%,23:00采集差1.34%/0.48%视当日尾盘波动),与截断机制自洽。

---

## 3. 总结论与缺失证据清单

见轴⑦。要点复述: 单一原因(采集时点→在途日K截断值 vs 完整UTC日收盘);非数据错误;非来源/复权/币种/比较日;缺失证据三项(U级): yfinance当日原始响应、/Users/cast/audit直接可达性、采集器console日志。

## 4. 对 Agent 4 的提交说明

1. 本卷宗为终裁前置材料;W5-FIX1 正式验收结果(包内证据)为 **FAIL/exit 2**,本归因**不改判**、不构成对任何一侧数据的有效性背书。
2. 若终裁需要"修正口径下能否通过"的参考: P-B/P-C(§2)为**归因性参考**,采用与否属冻结合同与Agent 4职权,本卷宗不提议采用。
3. 附带登记(与本归因无关但属终裁输入): GOLD_F=NOT_COMPARABLE、SHCOMP/SPX/WTI_F=NOT_VERIFIED、SHCOMP复算INSUFFICIENT_HISTORY(2/3期)、Gate A=DEGRADED(非核心缺MARGIN_BAL/SH_PE)——均包内证据,本轮未补齐(按任务边界禁止补齐)。
4. 差异清单(相对注入基准与R002 D1~D6)见附录A末;其中 D1(远端无 dev/p0-2-w5)**已消解**(本轮ls-remote实取到,SHA与本地一致),D2/D3/D5 维持,D4 未复核(U)。
5. 冻结合同 `IA-P0-2-W5-FIX1-AC/DEV-v1.0` 本体在DEV四类位置**均未寻获**(附录B);终裁若需合同原文,建议主Agent向操作者/引擎侧调取(用户配合项),勿以编号引用代替。

---

## 附录A · 任务A核验结果

### A.1 哈希(轮初实测,2026-11-01 UTC+8晨)
| zip | SHA256全值 | 登记前缀比对 |
|-----|-----------|--------------|
| IA-P0-2-W5-FIX1-ACCEPTANCE-EVIDENCE.zip | `b5f070a556d359de9590b816074f36e6c8d38738af07f4b8856c63b89ec647e8` | 与登记 `b5f070a5…` **一致** |
| IA-P0-2-W5-ACCEPTANCE-EVIDENCE.zip | `6e59f9cb9ad5580b9c2f9e75d9eaff0ed5cb61502af1e0a37ab5c310d739feeb` | 与登记 `6e59f9cb…` **一致** |

轮末复测: 两值不变(见自述报告§证据)。zip mtime均 2026-11-01 17:23(操作者放置时刻)。

### A.2 FIX1包结构 vs 登记
- unzip -l 实测 **22条目**(21常规文件+1目录项`evidence/`,unzip自计22)——登记"22文件"**一致**(以条目计;若按常规文件严格计为21,此为一处表述粒度差异,如实登记)。
- 六路外部来源evidence全在位: treasury_2026(01)/coinbase BTC-USD(02)/coinbase PAXG-USD(03)/sina sh000001(04)/fred SP500(05)/fred DCOILWTICO(06)✓;CI双job日志(4a19619+1020792)✓;real_acceptance JSON+MD+log+console.log ✓;SHA256SUMS ✓;提交后隔离证明 ✓;交付文档副本 ✓(SHA256=DEV原件 `4cc56362…`);README_EVIDENCE.txt ✓。另含登记描述未逐项枚举的: CI-SUMMARY×2、INCREMENTAL-DIFF、REAL-AUDIT、INPUT-INTEGRITY(README内容清单第12/13/16/17/18项自列,与登记结构相容)。
- W5首轮包: 17条目(16文件+1目录),含DIAGNOSTIC-BTC-DAY-BOUNDARY.txt(本轮归因的交叉输入,自述来源)。

### A.3 包内SHA256SUMS逐项校验
- FIX1包: `shasum -a 256 -c SHA256SUMS` → **20/20 全OK**(SHA256SUMS自身与目录项不列入,正常)。
- W5首轮包: `shasum -a 256 -c SHA256SUMS.txt` → **15/15 全OK**。

### A.4 real_acceptance 包内明细 vs 交付文档自述
- BTC: 78822.59(2026-10-29) vs 77780.33(2026-10-29),diff 1.34%>0.5% → FAIL ✓与自述一致。
- 分项(包内): UST_2Y/10Y/30Y PASS(0.0bp);GOLD_F NOT_COMPARABLE(PAXG现货代理≠COMEX期货连续,参考偏差仅披露);SHCOMP NOT_VERIFIED(新浪快照2026-10-30≠目标2026-10-29);SPX NOT_VERIFIED(FRED无2026-10-29同日观测);WTI_F NOT_VERIFIED(参考源不可达/无该日数据);复算: SPX/GOLD_F/HSI三期完整PASS,SHCOMP 2/3期INSUFFICIENT_HISTORY;Gate A DEGRADED。状态分布 {PASS:6, FAIL:1, NOT_VERIFIED:3, NOT_COMPARABLE:1, INSUFFICIENT_HISTORY:1} → 综合FAIL/exit2 ✓与README/交付文档§7自述一致。
- 注: 正式运行 git head=`4a19619e`(回填commit前),其 `code_version.script.sha256=62b2ed82…` 与DEV HEAD(10207929)脚本sha**一致**(4a19619→10207929间脚本未改,差异仅文档回填);W5首轮运行head=`78f4c9a`,BTC同配对同值1.34%。

### A.5 时间戳一致性
- FIX1: executed_at_utc=2026-11-01T06:27:58Z(=14:27:58 UTC+8);外部证据抓取06:28:18~06:28:30Z;zip成员mtime 14:39/14:40(打包于运行后)——与登记运行时间 **2026-11-01 14:28 一致**。
- W5首轮: executed_at_utc=2026-11-01T03:57:33Z(=11:57:33 UTC+8,登记"11:58"量级一致);成员mtime 12:02~12:05。

### A.6 差异清单(相对注入基准与 R002 D1~D6;核对范围=注入材料所列各项)
| 项 | R002基准 | 本轮实测 | 状态 |
|----|----------|----------|------|
| D1 | origin 侧无 dev/p0-2-w5 remote-tracking | `git ls-remote origin` 实取 `refs/heads/dev/p0-2-w5 → 10207929…`(=本地HEAD) | **已消解**(登记) |
| D2 | 交付文档§8未写zip路径与SHA256 | HEAD 10207929 交付文档L151仍为"路径与SHA256见交付说明"自指引占位,无实际值 | **维持** |
| D3 | 合同本体不在DEV | 全历史109 commit逐树grep+docs/+两包全成员: 仅编号引用,无全文(附录B) | **维持**(证据加强) |
| D4 | CI逐套件明细需登录不可见 | 本轮未复核(无需CI;包内CI job日志为自述+留档) | U(未变) |
| D5 | LIVE脚本sha≠DEV | LIVE `f9ca189c5248199bb5acbc78b2a2c82d59c10e1c7c2c2d20bdaaa6105fbfe3eb` ≠ DEV `62b2ed82…`(轮末复测不变) | **维持** |
| D6 | 其余各项一致 | 基点HEAD/两zip内容/分项状态/脚本sha链复核一致;无新增未登记差异 | 维持 |
| 新登记N1 | — | 正式运行head=4a19619e(非10207929),脚本sha一致(文档-only差异) | 登记 |
| 新登记N2 | — | 远端尚存历史分支 dev/fact-engine、dev/round2~6 等(非本轮产物,尖端未动) | 登记(背景) |

封版尖端核对(ls-remote实取): main=`50b5d13…`(=P0-1封版),w1=`69d7fc7…`,w2=`14fe6e5…`,w3=`497b02c…`,w4=`7c004c6…`——**全部与封版SHA一致,未动**。

## 附录B · 冻结合同定位(四类位置,结论: 未寻获)

目标: `IA-P0-2-W5-FIX1-AC-v1.0` 与 `IA-P0-2-W5-FIX1-DEV-v1.0` **全文**。

| 类 | 检索命令(要点) | 结果 |
|----|----------------|------|
| 1. DEV git全历史 | `rev-list --all`(109 commits);`log --all -S 'IA-P0-2-W5-FIX1-AC'`(命中4a19619);`-S '…-DEV'`(f1b6e42,4a19619);`-G 'W5-FIX1.*(验收条件|通过条件|冻结合同)'`(零);对109个commit逐一 `git grep -l <两编号>`;`log --all --name-only | grep -iE 'AC-v1|DEV-v1|contract|IA-'`(零) | AC编号仅现于 `docs/P0_2_W5_FIX1_DELIVERY.md:3,151`(4a19619起);DEV编号仅 `scripts/real_data_acceptance.py:30`、`tests/test_p02_w5_fix1.py:4`、交付文档L3——**全部为编号引用,无全文**;历史中从未存在合同命名文件 |
| 2. docs/现存文件 | `grep -rn 'IA-P0-2-W5-FIX1' docs/`;`grep -rnE '验收条件|通过条件|冻结合同' docs/`;`ls docs/` | 同上3处编号引用;"冻结合同"字样仅W4_FIX3无关语境;docs/无任何IA-*合同文件 |
| 3. FIX1包全部成员 | `grep -rn 'IA-P0-2-W5-FIX1-(AC|DEV)'` 于解压副本全部21文件 | 仅 `README_EVIDENCE.txt:2`、`P0_2_W5_FIX1_DELIVERY.md:3` 编号引用;交付文档副本与DEV原件逐字节相同(`4cc56362…`),无额外内嵌 |
| 4. W5首轮包全部成员 | 同上grep于16文件 | FIX1两编号**零命中**(该包制于FIX1之前,时序自洽);仅含W5原(非FIX1)合同编号引用(README_EVIDENCE.md:3等) |

**结论: 四类位置均未寻获合同全文。** 完整命令清单见 `docs/w5_attr_workspace/COMMAND_LOG.md` §2。编号引用不冒充全文;终裁需原文时建议主Agent经操作者从引擎侧(`~/agent-loop`合同存放处)调取——本会话不可达(U),不可达是权限边界事实,非合同不存在证明。

## 附录C · 外部抓取留档(公开无密钥,只读)

脚本: `docs/w5_attr_workspace/fetch_coinbase.py`;body/meta原件同目录已提交。

| 抓取 | URL | fetched_utc | status | body_sha256 | bytes |
|------|-----|-------------|--------|-------------|-------|
| 小时线 | `https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=3600&start=2026-10-29T20%3A00%3A00Z&end=2026-10-30T00%3A00%3A00Z` | 2026-11-01T09:59:16Z | 200 | `76d9a63459bf222ae85fdf80fe3c5fc6d67ce51a386022bd103a068bf0af0ac8` | 305 |
| 日线 | `https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400&start=2026-10-26T00%3A00%3A00Z&end=2026-10-31T00%3A00%3A00Z` | 2026-11-01T09:59:18Z | 200 | `e476e08f917a6d45e26f81f0c8897793b3e170e2df9239ccb9e4da43917ac3e7` | 366 |

要点: 小时线(格式[time,low,high,open,close,volume])—— 22:00Z收78862.27;**23:00Z open=78860.64 → close=77780.33**(low 77699/high 78880.81);00:00Z(10-30)open=77782.75。日线六根收盘 10-26~10-31 = 80008.79/80799.51/81249.31/77780.33/77180.42/77423.98,与W5首轮包DIAGNOSTIC(自述)所引**逐位一致**(该自述数值由此转为独立复核);其中10-29/10-30两根与FIX1包内验收证据文件逐位一致(完结K线不可变实证)。

## 附录D · 关键命令日志

见 `docs/w5_attr_workspace/COMMAND_LOG.md`(开轮自检/任务A/B/C/轮末全部命令要点与关键输出)。

---
*边界声明: 本轮零代码改动、零既有文件改动、LIVE零写入、未运行生产验收脚本、/tmp/w5-evidence只读(轮末复测一致)。分析配对均标注"仅归因证据,非验收口径变更"。*
