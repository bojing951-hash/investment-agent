# 完整研究报告(一键研究 MVP)

- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- run_ok: True | 证据行: 70 | run.ts_utc: 20261120T162144Z

## L1 事实层(引擎确定性产出)

| 指标 | 值 | 单位 | 观测日 | 质量 | 证据 ref |
|---|---|---|---|---|---|
| SPX | 7175.83 | index_point | 2026-11-19 | PASS | SPX@2026-11-19 |
| NDX | 26517.05 | index_point | 2026-11-19 | PASS | NDX@2026-11-19 |
| RUT | 2655.11 | index_point | 2026-11-19 | PASS | RUT@2026-11-19 |
| DXY | 103.94 | index_point | 2026-11-19 | PASS | DXY@2026-11-19 |
| EURUSD | 1.1 | usd_per_eur | 2026-11-19 | PASS | EURUSD@2026-11-19 |
| GOLD_F | 3627.9 | usd_per_oz | 2026-11-19 | PASS | GOLD_F@2026-11-19 |
| SILVER_F | 42.83 | usd_per_oz | 2026-11-19 | PASS | SILVER_F@2026-11-19 |
| BRENT_F | 90.05 | usd_per_barrel | 2026-11-19 | PASS | BRENT_F@2026-11-19 |
| VIX | 28.44 | index_point | 2026-11-19 | PASS | VIX@2026-11-19 |
| DAX | 25736.24 | index_point | 2026-11-18 | PASS | DAX@2026-11-18 |
| CAC40 | 8146.83 | index_point | 2026-11-18 | PASS | CAC40@2026-11-18 |
| USDJPY | 159.61 | jpy_per_usd | 2026-11-19 | PASS | USDJPY@2026-11-19 |
| USDCNY | 6.67 | cny_per_usd | 2026-11-19 | PASS | USDCNY@2026-11-19 |
| HY_OAS | 3.47 | percentage_point | 2026-11-18 | PASS | HY_OAS@2026-11-18 |
| BB_OAS | 2.05 | percentage_point | 2026-11-18 | PASS | BB_OAS@2026-11-18 |
| B_OAS | 3.73 | percentage_point | 2026-11-18 | PASS | B_OAS@2026-11-18 |
| CCC_OAS | 13.53 | percentage_point | 2026-11-18 | PASS | CCC_OAS@2026-11-18 |
| IG_OAS | 0.93 | percentage_point | 2026-11-18 | PASS | IG_OAS@2026-11-18 |
| UST_2Y | 4.8 | percent | 2026-11-18 | PASS | UST_2Y@2026-11-18 |
| UST_10Y | 5.07 | percent | 2026-11-18 | PASS | UST_10Y@2026-11-18 |
| UST_30Y | 5.41 | percent | 2026-11-18 | PASS | UST_30Y@2026-11-18 |
| TIPS_5Y | 2.66 | percent | 2026-11-18 | PASS | TIPS_5Y@2026-11-18 |
| TIPS_10Y | 2.88 | percent | 2026-11-18 | PASS | TIPS_10Y@2026-11-18 |
| BEI_5Y | 2.22 | percent | 2026-11-19 | PASS | BEI_5Y@2026-11-19 |
| BEI_10Y | 2.16 | percent | 2026-11-19 | PASS | BEI_10Y@2026-11-19 |
| CURVE_2S10S | 0.28 | percentage_point | 2026-11-19 | PASS | CURVE_2S10S@2026-11-19 |
| CPI | 337.476 | index_point_1982_84 | 2026-10-01 | WARN | CPI@2026-10-01 |
| CORE_PCE | 130.902 | index_point_2017 | 2026-09-01 | DEGRADED | CORE_PCE@2026-09-01 |
| UNEMPLOYMENT | 4.1 | percent | 2026-10-01 | WARN | UNEMPLOYMENT@2026-10-01 |
| CORE_CPI | 339.9 | index_point_1982_84 | 2026-10-01 | WARN | CORE_CPI@2026-10-01 |
| UST_5Y | 4.89 | percent | 2026-11-18 | PASS | UST_5Y@2026-11-18 |
| INDPRO | 103.3954 | index_point_2017 | 2026-10-01 | WARN | INDPRO@2026-10-01 |
| US_REAL_GDP | 24611.077 | billion_usd | 2026-07-01 | DEGRADED | US_REAL_GDP@2026-07-01 |
| SHCOMP | 3533.79 | index_point | 2026-11-20 | PASS | SHCOMP@2026-11-20 |
| HSI | 22410.8 | index_point | 2026-11-20 | PASS | HSI@2026-11-20 |
| CN_LPR_1Y | 3.0 | percent | 2026-11-20 | WARN | CN_LPR_1Y@2026-11-20 |
| CN_PMI_MFG | 49.3 | index_point | 2026-10-01 | WARN | CN_PMI_MFG@2026-10-01 |
| DFF | 3.88 | percent | 2026-11-18 | PASS | DFF@2026-11-18 |
| DFEDTARU | 4.0 | percent | 2026-11-19 | PASS | DFEDTARU@2026-11-19 |
| NIKKEI225 | 56436.65 | index_point | 2026-11-20 | PASS | NIKKEI225@2026-11-20 |
| JP_CPI_YOY | 2.44 | percent | 2026-10-01 | WARN | JP_CPI_YOY@2026-10-01 |
| ECB_DFR | 2.5 | percent | 2026-09-16 | DEGRADED | ECB_DFR@2026-09-16 |
| ECB_MRO | 2.65 | percent | 2026-09-16 | DEGRADED | ECB_MRO@2026-09-16 |
| EA_HICP_YOY | 1.9 | percent | 2025-12-01 | DEGRADED | EA_HICP_YOY@2025-12-01 |
| JP_POLICY_RATE | 1.227 | percent | 2026-10-01 | WARN | JP_POLICY_RATE@2026-10-01 |

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=False n=None 隔离=None
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)

## L3 AI 推断层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### C1 · 过去一年全球风险资产普跌与美元走强的主导渠道,证据面容纳两种并列解释:其一,再通胀→政策再收紧→实际利率抬升→折现率冲击,压制长久期权益与无息资产黄金;其二,日本货币政策正常化→套息头寸平仓→波动全球传染。两个可核面对前者更有利:USDJPY近月不跌反微升,与套息平仓应有的日元急升特征相反;HY_OAS信用利差未走阔,与信用收缩型下跌不符。但日经225跌幅大于SPX的放大项仍可能含日本自身因素,竞争解释不能完全排除。
- 依据: TIPS_10Y一年显著上行而BEI_10Y基本持平略降,十年期美债UST_10Y长端抬升由实际利率主导(共同交易日分解);近一月SPX与NIKKEI225和GOLD_F下跌,VIX与DXY上行;USDJPY微升;HY_OAS处于较窄水平而CCC_OAS偏高。证据引用: TIPS_10Y/BEI_10Y/UST_10Y/SPX/NIKKEI225/GOLD_F/VIX/DXY/USDJPY/HY_OAS快照事实。
- 竞争性解释: 主解释(再通胀-折现率渠道):若实际利率TIPS_10Y维持高位,折现率冲击将持续压制SPX与GOLD_F等长久期/无息资产,DXY随利差走强——与近一月观察一致
- 竞争性解释: 竞争解释A(日本套息平仓渠道):若日央行正常化引发融资头寸去杠杆,USDJPY应显著下行(日元急升)且日经领跌全球——汇率面观察与此不符,但权益放大项不可全排除
- 竞争性解释: 竞争解释B(高估值去化渠道):若CAPE高位下的利率敏感性放大回调,则跌幅应集中于高估值指数而信用面平稳——与HY_OAS未走阔相容,可与主解释叠加而非互斥
### C2 · 中国PPI同比由负转正并大幅走高,而中国CPI同比温和、制造业PMI三个对照锚水平均处荣枯线下方:供给侧/上游成本推动、内需边际修复、低基数效应三种解释并存,引擎无行业成分与进口价格序列,不能裁决。CN_PMI_MFG同比维度同期改善为需求侧解释提供部分支持,但其水平仍在收缩区间,支持力度有限。
- 依据: CN_PMI_MFG三锚水平低于五十;中国通胀序列见步骤台账的序列面;无成分/权重数据,禁作成分归因。
- 竞争性解释: 供给侧/上游成本推动(【假设】):若为上游价格驱动,PPI先于CPI转正且幅度差大、CPI温和——与观察一致但缺进口价格序列佐证
- 竞争性解释: 内需边际修复(【假设】):若需求修复,PMI同比维度应同步改善——已观察到,但PMI水平仍低于荣枯线,需求证据弱
- 竞争性解释: 低基数效应(【假设】):同比口径受基期影响,若为基数主导,水平序列环比动能应平淡——可用PPI环比口径复核,现以同比空间呈现
### 机制链 M1_reflation_discount_shock · 
- 环1 [E1] 通胀再加速可核:美国CPI同比(派生)2026-02为2.434、2026-05为4.1666;核心CPI同比2026-05为2.8229、2026-08回落至2.4462;核心PCE同比最新3.12——再通胀集中于标题口径,核心口径温和
- 环2 [E1] 政策再定价可核:Fed有效基金利率DFF年中下行(2026-08-20为3.63)后于2026-11-18回到3.88,目标区间上限DFEDTARU最新4.0;ECB存款便利利率2026-06-11与2026-09-10各上调25bp至2.5;日本政策利率(月均)2026-04为0.727、2026-07为0.978、2026-10为1.227;中国OMO利率三锚不变——政策阵营分裂
- 环3 [E1] 长端分解可核:十年期美债名义一年+95bp=实际TIPS_10Y+103bp+盈亏平衡BEI_10Y-8bp(共同交易日窗2025-11-18→2026-11-18);近一月名义-8bp=实际+8bp+盈亏平衡-16bp——抬升由实际利率主导,通胀预期锚定
- 环4 [E1] 资产端可核:近一月(2026-10-21→最新)SPX -7.49%、NIKKEI225 -12.67%、GOLD_F -12.58%、SHCOMP -4.83%、DAX +0.36%,VIX +70.5%、DXY +2.12%、USDJPY +0.85%;HY_OAS 3.47pp未显著走阔——股金双跌、美元走强、信用平稳
- 环5 [E2] 机制环节:实际利率抬升→折现率上升→压制长久期权益与无息黄金;信用利差未走阔→本轮下跌非信用收缩事件。本引擎无期限溢价/股权风险溢价分解序列,该环拆分为【假设】
  - 缺环注记: 缺期限溢价与股权风险溢价序列,折现率机制的定量拆分为【假设】,可由HY_OAS与CCC_OAS后续走向部分监视
### 机制链 M2_japan_carry_competing · 
- 环1 [E1] 日本面可核:政策利率(月均)自2025-10的0.477升至2026-10的1.227;东京CPI同比2026-09为2.69再加速;全国CPI同比2026-10为2.44;USDJPY最新159.61(近一月+0.85%,日元未升值)
- 环2 [E3] 套息平仓叙事:日央行加息→日元融资头寸去杠杆→全球风险资产波动传染——整环为【假设】:本引擎无套息头寸/持仓/杠杆数据,且汇率面(USDJPY微升)不支持平仓主导

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### SCN1_baseline_reflation_persists · 角色=
- 情景: 【假设非预测】基准情景:再通胀持续性高于预期,美欧日政策利率维持高位或续升,实际利率TIPS_10Y居高,中国维持低利率——增长温和、通胀回落缓慢。
- 资产方向: 权益(SPX/NIKKEI225)与黄金GOLD_F承压(看跌),美元DXY偏强(看涨),信用利差HY_OAS温和走阔但不至危机 | 置信档: 有历史相似证据
- 敏感变量: TIPS_10Y, CPI
- 证伪: 指标=CORE_CPI | 阈值=美国核心CPI同比(派生口径)回落至2.0以下且连续两月——通胀快速消退则本情景证伪 | 次级=BEI_10Y
- 触发: TIPS_10Y维持≥2.8%且CPI同比(派生)≥3.5%再持续三个月 | 期限: 2027-02-28
### SCN2_counter_inflation_fades · 角色=
- 情景: 【假设非预测】反例情景:供给冲击消退,美国标题通胀向核心收敛并快速回落,央行转鸽(先Fed后ECB),日本正常化继续但速度放缓。
- 资产方向: 风险资产修复(看涨SPX/NIKKEI225),黄金先抑后扬(看涨,12个月维度),美元回落(看跌DXY) | 置信档: 有历史相似证据
- 敏感变量: BEI_10Y, CORE_CPI
- 证伪: 指标=BEI_10Y | 阈值=BEI_10Y升破2.6且TIPS_10Y≥3.0连续两月——通胀预期脱锚+实际利率续高则本情景证伪 | 次级=TIPS_10Y
- 触发: CORE_CPI同比(派生)连续两月≥2.4且BEI_10Y≥2.4 | 期限: 2027-02-28

## 证据索引

| # | kind | ref | 说明 |
|---|---|---|---|
| 1 | snapshot_fact | SPX@2026-11-19 |  |
| 2 | snapshot_fact | NDX@2026-11-19 |  |
| 3 | snapshot_fact | RUT@2026-11-19 |  |
| 4 | snapshot_fact | DXY@2026-11-19 |  |
| 5 | snapshot_fact | EURUSD@2026-11-19 |  |
| 6 | snapshot_fact | GOLD_F@2026-11-19 |  |
| 7 | snapshot_fact | SILVER_F@2026-11-19 |  |
| 8 | snapshot_fact | BRENT_F@2026-11-19 |  |
| 9 | snapshot_fact | VIX@2026-11-19 |  |
| 10 | snapshot_fact | DAX@2026-11-18 |  |
| 11 | snapshot_fact | CAC40@2026-11-18 |  |
| 12 | snapshot_fact | USDJPY@2026-11-19 |  |
| 13 | snapshot_fact | USDCNY@2026-11-19 |  |
| 14 | snapshot_fact | HY_OAS@2026-11-18 |  |
| 15 | snapshot_fact | BB_OAS@2026-11-18 |  |
| 16 | snapshot_fact | B_OAS@2026-11-18 |  |
| 17 | snapshot_fact | CCC_OAS@2026-11-18 |  |
| 18 | snapshot_fact | IG_OAS@2026-11-18 |  |
| 19 | snapshot_fact | UST_2Y@2026-11-18 |  |
| 20 | snapshot_fact | UST_10Y@2026-11-18 |  |
| 21 | snapshot_fact | UST_30Y@2026-11-18 |  |
| 22 | snapshot_fact | TIPS_5Y@2026-11-18 |  |
| 23 | snapshot_fact | TIPS_10Y@2026-11-18 |  |
| 24 | snapshot_fact | BEI_5Y@2026-11-19 |  |
| 25 | snapshot_fact | BEI_10Y@2026-11-19 |  |
| 26 | snapshot_fact | CURVE_2S10S@2026-11-19 |  |
| 27 | snapshot_fact | CPI@2026-10-01 |  |
| 28 | snapshot_fact | CORE_PCE@2026-09-01 |  |
| 29 | snapshot_fact | UNEMPLOYMENT@2026-10-01 |  |
| 30 | snapshot_fact | CORE_CPI@2026-10-01 |  |
| 31 | snapshot_fact | UST_5Y@2026-11-18 |  |
| 32 | snapshot_fact | INDPRO@2026-10-01 |  |
| 33 | snapshot_fact | US_REAL_GDP@2026-07-01 |  |
| 34 | snapshot_fact | SHCOMP@2026-11-20 |  |
| 35 | snapshot_fact | HSI@2026-11-20 |  |
| 36 | snapshot_fact | CN_LPR_1Y@2026-11-20 |  |
| 37 | snapshot_fact | CN_PMI_MFG@2026-10-01 |  |
| 38 | snapshot_fact | DFF@2026-11-18 |  |
| 39 | snapshot_fact | DFEDTARU@2026-11-19 |  |
| 40 | snapshot_fact | NIKKEI225@2026-11-20 |  |
| 41 | snapshot_fact | JP_CPI_YOY@2026-10-01 |  |
| 42 | snapshot_fact | ECB_DFR@2026-09-16 |  |
| 43 | snapshot_fact | ECB_MRO@2026-09-16 |  |
| 44 | snapshot_fact | EA_HICP_YOY@2025-12-01 |  |
| 45 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 46 | s3_envelope | SZCI@2026-11-20 |  |
| 47 | s3_envelope | CHINEXT@2026-11-20 |  |
| 48 | s3_envelope | HSCEI@2026-11-20 |  |
| 49 | s3_envelope | NVDA@2026-11-19 |  |
| 50 | s3_envelope | AAPL@2026-11-19 |  |
| 51 | s3_envelope | MSFT@2026-11-19 |  |
| 52 | s3_envelope | TLT@2026-11-19 |  |
| 53 | s3_envelope | IEF@2026-11-19 |  |
| 54 | s3_envelope | SHY@2026-11-19 |  |
| 55 | s3_envelope | HYG@2026-11-19 |  |
| 56 | s3_envelope | LQD@2026-11-19 |  |
| 57 | s3_envelope | GBPUSD@2026-11-19 |  |
| 58 | s3_envelope | WTI_F@2026-11-19 |  |
| 59 | s3_envelope | GLD@2026-11-19 |  |
| 60 | s3_envelope | USO@2026-11-19 |  |
| 61 | s3_envelope | EEM@2026-11-19 |  |
| 62 | s3_envelope | EZU@2026-11-19 |  |
| 63 | s3_envelope | FEZ@2026-11-19 |  |
| 64 | s3_envelope | EWU@2026-11-19 |  |
| 65 | s3_envelope | EWG@2026-11-19 |  |
| 66 | s3_envelope | EWJ@2026-11-19 |  |
| 67 | s3_envelope | INDA@2026-11-19 |  |
| 68 | s3_envelope | FXI@2026-11-19 |  |
| 69 | s3_envelope | BTC@2026-11-18 |  |
| 70 | s3_envelope | HY_IG_DIFF@2026-11-18 |  |

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2025-03 | 0.673446 | 0.0 | rates 48.5%、volatility 32.3% |
| 2 | 2022-06 | 0.794208 | 1.3699 | rates 50.8%、valuation 33.4% |
| 3 | 2023-10 | 0.968894 | 26.0274 | volatility 53.4%、valuation 25.1% |
| 4 | 2021-02 | 1.203292 | 69.863 | rates 82.8%、inflation 8.5% |
| 5 | 2019-12 | 1.280722 | 72.6027 | rates 47.1%、volatility 39.1% |

> 相似≠因果, 更非预测: TOP-N 是历史状态距离最近的时期, 当时之后的演变只是历史记录
> 特征为最新修订口径的描述性对齐, 不代表当时市场信息集(research_mode_gate)
> 距离分位=该候选在全部有效候选中的相对位置, 不是概率

## 日度相关(引擎确定性面·读者版)

- US_REAL_GDP×UNEMPLOYMENT 日收益×日变化 pearson = -0.8936(n=37 对,共同窗 2017-01..2026-07;描述性统计≠因果)


## 质量状态(Audit-R1 F02 四态+Audit-R2 绑定面+Audit-R4 贯通面)

- generated: true(FULL_REPORT 完整装配: L1+L2+L3/L4 全文内联+证据索引)
- machine_verified: True(L3∧L4 produced+纪律校验过+底座非降级或 optional 级显式降级随档)
- run 门(Audit-R4 条目5): blocked_class=map_core_dimension_missing degraded_ok=False
- review: required=True seat_invoked=True verdict=UPHELD fresh=True error=None 修订链档数=1
- copies_consistent(多副本一致): True(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前确定性装配)
- deliverable(可交付): False
- 内容绑定(Audit-R4 条目2): content_sha256=canonical(report.json 剥离 semantic_review)+canonical(agent_judgment.json)+canonical(views_digest.json)——机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。
