# 完整研究报告(一键研究 MVP)

- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- run_ok: True | 证据行: 68 | run.ts_utc: 20261119T120815Z

## L1 事实层(引擎确定性产出)

| 指标 | 值 | 单位 | 观测日 | 质量 | 证据 ref |
|---|---|---|---|---|---|
| SPX | 7323.63 | index_point | 2026-11-18 | PASS | SPX@2026-11-18 |
| NDX | 27116.26 | index_point | 2026-11-18 | PASS | NDX@2026-11-18 |
| RUT | 2714.31 | index_point | 2026-11-18 | PASS | RUT@2026-11-18 |
| DXY | 103.78 | index_point | 2026-11-18 | PASS | DXY@2026-11-18 |
| EURUSD | 1.1 | usd_per_eur | 2026-11-18 | PASS | EURUSD@2026-11-18 |
| GOLD_F | 3727.8 | usd_per_oz | 2026-11-18 | PASS | GOLD_F@2026-11-18 |
| SILVER_F | 44.97 | usd_per_oz | 2026-11-18 | PASS | SILVER_F@2026-11-18 |
| BRENT_F | 88.68 | usd_per_barrel | 2026-11-18 | PASS | BRENT_F@2026-11-18 |
| VIX | 24.56 | index_point | 2026-11-18 | PASS | VIX@2026-11-18 |
| DAX | 26045.37 | index_point | 2026-11-17 | PASS | DAX@2026-11-17 |
| CAC40 | 8216.78 | index_point | 2026-11-17 | PASS | CAC40@2026-11-17 |
| USDJPY | 159.3 | jpy_per_usd | 2026-11-18 | PASS | USDJPY@2026-11-18 |
| USDCNY | 6.66 | cny_per_usd | 2026-11-18 | PASS | USDCNY@2026-11-18 |
| HY_OAS | 3.43 | percentage_point | 2026-11-17 | PASS | HY_OAS@2026-11-17 |
| BB_OAS | 2.04 | percentage_point | 2026-11-17 | PASS | BB_OAS@2026-11-17 |
| B_OAS | 3.68 | percentage_point | 2026-11-17 | PASS | B_OAS@2026-11-17 |
| CCC_OAS | 13.29 | percentage_point | 2026-11-17 | PASS | CCC_OAS@2026-11-17 |
| IG_OAS | 0.92 | percentage_point | 2026-11-17 | PASS | IG_OAS@2026-11-17 |
| UST_2Y | 4.8 | percent | 2026-11-17 | PASS | UST_2Y@2026-11-17 |
| UST_10Y | 5.1 | percent | 2026-11-17 | PASS | UST_10Y@2026-11-17 |
| UST_30Y | 5.46 | percent | 2026-11-17 | PASS | UST_30Y@2026-11-17 |
| TIPS_5Y | 2.64 | percent | 2026-11-17 | PASS | TIPS_5Y@2026-11-17 |
| TIPS_10Y | 2.89 | percent | 2026-11-17 | PASS | TIPS_10Y@2026-11-17 |
| BEI_5Y | 2.23 | percent | 2026-11-18 | PASS | BEI_5Y@2026-11-18 |
| BEI_10Y | 2.19 | percent | 2026-11-18 | PASS | BEI_10Y@2026-11-18 |
| CURVE_2S10S | 0.27 | percentage_point | 2026-11-18 | PASS | CURVE_2S10S@2026-11-18 |
| CPI | 337.476 | index_point_1982_84 | 2026-10-01 | WARN | CPI@2026-10-01 |
| CORE_PCE | 130.902 | index_point_2017 | 2026-09-01 | DEGRADED | CORE_PCE@2026-09-01 |
| UNEMPLOYMENT | 4.1 | percent | 2026-10-01 | WARN | UNEMPLOYMENT@2026-10-01 |
| CORE_CPI | 339.9 | index_point_1982_84 | 2026-10-01 | WARN | CORE_CPI@2026-10-01 |
| UST_5Y | 4.9 | percent | 2026-11-17 | PASS | UST_5Y@2026-11-17 |
| INDPRO | 103.3954 | index_point_2017 | 2026-10-01 | WARN | INDPRO@2026-10-01 |
| US_REAL_GDP | 24611.077 | billion_usd | 2026-07-01 | DEGRADED | US_REAL_GDP@2026-07-01 |
| SHCOMP | 3587.83 | index_point | 2026-11-18 | PASS | SHCOMP@2026-11-18 |
| HSI | 22814.93 | index_point | 2026-11-19 | PASS | HSI@2026-11-19 |
| CN_LPR_1Y | 3.0 | percent | 2026-10-20 | WARN | CN_LPR_1Y@2026-10-20 |
| CN_PMI_MFG | 49.3 | index_point | 2026-10-01 | WARN | CN_PMI_MFG@2026-10-01 |
| NIKKEI225 | 59024.28 | index_point | 2026-11-18 | PASS | NIKKEI225@2026-11-18 |
| JP_CPI_YOY | 2.16 | percent | 2026-09-01 | DEGRADED | JP_CPI_YOY@2026-09-01 |
| ECB_DFR | 2.5 | percent | 2026-09-16 | DEGRADED | ECB_DFR@2026-09-16 |
| ECB_MRO | 2.65 | percent | 2026-09-16 | DEGRADED | ECB_MRO@2026-09-16 |
| EA_HICP_YOY | 4.0 | percent | 2026-10-01 | WARN | EA_HICP_YOY@2026-10-01 |
| JP_POLICY_RATE | 1.227 | percent | 2026-10-01 | WARN | JP_POLICY_RATE@2026-10-01 |

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=False n=None 隔离=None
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)

## L3 AI 推断层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### CON-1 · 近月全球风险资产集体回调的主导驱动之争: 同一事实面(实际利率处历史高位且续升、盈亏平衡通胀回落、波动率跳升、权益与贵金属与日经同步走弱、美元走强)至少容纳三种解释——(甲)央行再收紧推升实际贴现率压制高估值资产;(乙)增长预期下修主导(实际利率上行只是增长担忧的镜像);(丙)日本央行连续加息引发日元融资套息头寸平仓、由日本资产外溢至全球。TIPS_10Y 与 BEI_10Y 的分解证据倾向(甲)为主导: 名义长端近一年的上行几乎全部由实际利率贡献、盈亏平衡贡献为负;而 USDJPY 全年仅温和变动、未出现套息头寸大规模强制平仓特有的剧烈波动,削弱(丙)作为主导解释的地位。三者并非互斥,月频宏观数据无法完全分解相对权重。
- 依据: 依据: TIPS_10Y/BEI_10Y/UST_10Y 共同交易日分解面(research_plan.us_rates_trio)、SPX/NIKKEI225/GOLD_F/VIX/DXY 资产窗行、USDJPY 十二月自配对区间变化。各解释成立的条件与区分指标见 reader_map.transmission 逐环四件套。
- 竞争性解释: 央行再收紧→实际利率上行→高估值与无现金流资产承压(折现率渠道主导)
- 竞争性解释: 增长预期下修→风险偏好收缩(盈亏平衡通胀下行与 GDP 同比放缓为其特征信号;若 BEI_10Y 持续显著下行而 TIPS_10Y 走平,该解释升为主导)
- 竞争性解释: 日银加息→日元套息平仓→日本资产领跌并外溢(若 USDJPY 出现急速下行伴随 VIX 跳升,该解释升为主导;当前十二月 USDJPY 方向与其不符)
### CON-2 · 中国 PPI 同比由通缩深度回升转正并续升至高位,其性质之争: (甲)全球商品价格与出口价格再通胀的外生传导(内需未必同步修复);(乙)内需修复主导的再通胀。CN_PMI_MFG 研究窗内多数月份低于荣枯线(最新一期 49.3 仍低于五十,仅少数月份略上或触线)支持(甲)的读法——价格修复显著领先于内需与制造业景气修复,CPI 同比亦仅小幅为正。二者对『中国增长环境』的判断含义不同: 前者对应『名义价格修复+实际增长偏弱』,后者对应景气全面回升。
- 依据: 依据: CN_PPI_YOY 月度路径(通缩退出发生在其后数月,引擎面逐月可溯)、CN_CPI_YOY 三时点、CN_PMI_MFG 三时点与最新水平。区分指标=CN_PMI_MFG 是否持续站上荣枯线。
- 竞争性解释: 全球商品/出口价格再通胀外生传导(若 CN_PMI_MFG 持续低于五十而 PPI 续升,支持本解释)
- 竞争性解释: 内需修复主导(若 CN_PMI_MFG 持续站上五十且新订单分项走强,支持本解释;引擎无分项序列,该条件为【假设】性外推)
### CON-3 · 政策分化之争: 在通胀普遍再加速的背景下,美欧日转向再收紧而中国按兵不动并于年末改换政策利率锚,分化由什么决定——(甲)各自通胀幅度与动能之差(欧区通胀越高其加息越早越连续);(乙)汇率与金融条件约束之差(日元汇率承压叠加再通胀使日银 normalization 提速,增长偏弱约束中国收紧空间——注意引擎窗内人民币实际走强,汇率约束论据对中国不成立,仅增长腿可保留)。EA_HICP_YOY 的高度与 ECB 两连加息的时序一致支持(甲)为主;但 JP_POLICY_RATE 的连续上行早于其通胀回升,为(乙)保留空间。引擎无汇率-政策反应函数序列,相对权重判定为【尚未验证】。
- 依据: 依据: EA_HICP_YOY 与 ECB_DFR/ECB_MRO 决策时序、JP_POLICY_RATE 月均路径、CN_LPR_1Y 与七天逆回购利率全年持平、中国隔夜政策锚序列(年末起)。
- 竞争性解释: 通胀幅度与动能之差主导政策分化
- 竞争性解释: 汇率与金融条件约束之差主导政策分化(若 JP_POLICY_RATE 续升而 JP_CPI_YOY 回落,该解释权重上升)
### 机制链 MECH-1 · 
- 环1 [E1] 【事实·E1】政策面转向再收紧: 美联储目标区间上限 2025-12 由 4.00 降至 3.75 后,2026-09 再升至 4.00(有效联邦基金利率 2026-08 月末 3.63→2026-09 月末 3.88,日频月末口径);欧央行存款便利利率 2026-06-17 由 2.00 升至 2.25、2026-09-16 再至 2.50;日本无担保隔夜拆借月均由 0.477(2025-10)连续升至 1.227(2026-10)。三者同向,且时序上日银先行(2025-12 起)、欧央行次之(2026-06)、美联储跟进(2026-09)。
- 环2 [E1] 【事实·E1】长端名义利率上行由实际利率主导: 近一年(共同交易日 2025-11-17→2026-11-17)UST_10Y +97bp = TIPS_10Y +104bp + BEI_10Y −7bp(恒等残差 0);近一月(2026-10-16→2026-11-17)UST_10Y +1bp = TIPS_10Y +15bp + BEI_10Y −14bp(残差 0)——即回调月名义持平之下实际利率仍在上行、通胀定价回落,呈『紧缩性实际利率+回落中的通胀预期』组合。
- 环3 [E1] 【事实·E1】资产面同步反应(引擎资产窗行,窗口两端实测日随行): 近三月 SPX −4.99%、NIKKEI225 −9.65%、GOLD_F −17.99%、DXY +5.01%、VIX +64.94%(水平 14.89→24.56);近一月 SPX −4.77%、NIKKEI225 −9.08%、GOLD_F −10.39%、DXY +1.76%、VIX +33.19%。近一年对照: SPX +10.26%、NIKKEI225 +21.61%、GOLD_F −8.70%、DXY +3.54%——即权益与黄金的年度正/负收益在近三月被快速侵蚀。
- 环4 [E2] 【假设·E2】传导语义环: 实际贴现率上行→高估值权益的风险溢价与长久期资产的机会成本上升→估值压缩与资金流向现金与美元。本引擎无股权风险溢价与估值-收益率联动序列,该环两端(实际利率水平→估值倍数变动)不可由本引擎确定性刻画,故标【假设】;可验证部分(实际利率与资产价格的同期反相关)已由第 2/3 环 E1 给出,相关≠因果。
  - 缺环注记: 本引擎无股权风险溢价/估值-收益率联动序列,此环为【假设】,不做因果断言。
### 机制链 MECH-2 · 
- 环1 [E1] 【事实·E1】中国生产价格由通缩转再通胀: CN_PPI_YOY 由 2026-02 的 −0.9 转正(2026-03 为 +0.5)续升至 2026-10 的 5.7,十二个月摆幅近八个百分点;同期 CN_PMI_MFG 仍在荣枯线下方附近(2026-10 为 49.3)。
- 环2 [E2] 【假设·E2】传导环: 中国生产价格回升经全球商品链与出口价格传导至美欧商品通胀。本引擎无贸易价格/出口单价序列,该环不可确定性验证;时间上美欧通胀再加速与中国 PPI 转正同窗(月频先后未定),与该机制相容但同样与共同外因(全球商品供给/能源)相容。
  - 缺环注记: 本引擎无贸易价格/出口单价序列,此环为【假设】;共同外因(全球商品供给冲击)与该机制在引擎数据内不可区分。
- 环3 [E3] 【假设·E3】若该机制成立,其含义是美欧核心通胀的商品分量粘性上升、央行被迫维持紧缩——纯叙事推演,证伪指标 CORE_PCE: 若 CORE_PCE 同比回落至疫情前区间下方且中国 PPI 同步回落,该传导叙事失效。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### SCN-A · 角色=
- 情景: 假设(非预测): 全球通胀再加速延续,美欧日政策利率维持高位或续升,实际利率维持强势——『紧缩延续』情景。
- 资产方向: 权益与贵金属整体承压、波动率中枢抬升、美元偏强(条件式方向判断,非预测) | 置信档: 有相关证据
- 敏感变量: TIPS_10Y, BEI_10Y
- 证伪: 指标=CPI | 阈值=最近有效同比口径的美国 CPI 同比在 2027-04-30 前回落至 3.0 以下,则本情景的核心前提(通胀粘性)失效 | 次级=EA_HICP_YOY,CORE_PCE
- 触发: TIPS_10Y 维持在 2.8 以上且最近有效口径 CPI 同比不低于 3.5 且 DFEDTARU 再上行一档或以上 | 期限: 2027-02-28
### SCN-B · 角色=
- 情景: 假设(非预测): 基数效应与供给修复令美欧通胀在两至三个季度内回落至目标附近,央行转向鸽派——『通胀回落转鸽』反例情景。
- 资产方向: 风险资产修复、实际利率回落、贵金属重新走强(条件式方向判断,非预测;历史上加息尾声转鸽期权益与黄金事后表现较强,见历史段 2023-10 类比) | 置信档: 有历史相似证据
- 敏感变量: BEI_10Y, CPI
- 证伪: 指标=CPI | 阈值=最近有效同比口径的美国 CPI 同比在 2027-01-31 前仍高于 4.0,则本情景前提(通胀回落)失效 | 次级=EA_HICP_YOY
- 触发: BEI_10Y 回落至 2.0 以下且最近有效口径 CPI 同比连续两个月下行且 DFEDTARU 出现下调 | 期限: 2027-04-30

## 证据索引

| # | kind | ref | 说明 |
|---|---|---|---|
| 1 | snapshot_fact | SPX@2026-11-18 |  |
| 2 | snapshot_fact | NDX@2026-11-18 |  |
| 3 | snapshot_fact | RUT@2026-11-18 |  |
| 4 | snapshot_fact | DXY@2026-11-18 |  |
| 5 | snapshot_fact | EURUSD@2026-11-18 |  |
| 6 | snapshot_fact | GOLD_F@2026-11-18 |  |
| 7 | snapshot_fact | SILVER_F@2026-11-18 |  |
| 8 | snapshot_fact | BRENT_F@2026-11-18 |  |
| 9 | snapshot_fact | VIX@2026-11-18 |  |
| 10 | snapshot_fact | DAX@2026-11-17 |  |
| 11 | snapshot_fact | CAC40@2026-11-17 |  |
| 12 | snapshot_fact | USDJPY@2026-11-18 |  |
| 13 | snapshot_fact | USDCNY@2026-11-18 |  |
| 14 | snapshot_fact | HY_OAS@2026-11-17 |  |
| 15 | snapshot_fact | BB_OAS@2026-11-17 |  |
| 16 | snapshot_fact | B_OAS@2026-11-17 |  |
| 17 | snapshot_fact | CCC_OAS@2026-11-17 |  |
| 18 | snapshot_fact | IG_OAS@2026-11-17 |  |
| 19 | snapshot_fact | UST_2Y@2026-11-17 |  |
| 20 | snapshot_fact | UST_10Y@2026-11-17 |  |
| 21 | snapshot_fact | UST_30Y@2026-11-17 |  |
| 22 | snapshot_fact | TIPS_5Y@2026-11-17 |  |
| 23 | snapshot_fact | TIPS_10Y@2026-11-17 |  |
| 24 | snapshot_fact | BEI_5Y@2026-11-18 |  |
| 25 | snapshot_fact | BEI_10Y@2026-11-18 |  |
| 26 | snapshot_fact | CURVE_2S10S@2026-11-18 |  |
| 27 | snapshot_fact | CPI@2026-10-01 |  |
| 28 | snapshot_fact | CORE_PCE@2026-09-01 |  |
| 29 | snapshot_fact | UNEMPLOYMENT@2026-10-01 |  |
| 30 | snapshot_fact | CORE_CPI@2026-10-01 |  |
| 31 | snapshot_fact | UST_5Y@2026-11-17 |  |
| 32 | snapshot_fact | INDPRO@2026-10-01 |  |
| 33 | snapshot_fact | US_REAL_GDP@2026-07-01 |  |
| 34 | snapshot_fact | SHCOMP@2026-11-18 |  |
| 35 | snapshot_fact | HSI@2026-11-19 |  |
| 36 | snapshot_fact | CN_LPR_1Y@2026-10-20 |  |
| 37 | snapshot_fact | CN_PMI_MFG@2026-10-01 |  |
| 38 | snapshot_fact | NIKKEI225@2026-11-18 |  |
| 39 | snapshot_fact | JP_CPI_YOY@2026-09-01 |  |
| 40 | snapshot_fact | ECB_DFR@2026-09-16 |  |
| 41 | snapshot_fact | ECB_MRO@2026-09-16 |  |
| 42 | snapshot_fact | EA_HICP_YOY@2026-10-01 |  |
| 43 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 44 | s3_envelope | SZCI@2026-11-18 |  |
| 45 | s3_envelope | CHINEXT@2026-11-18 |  |
| 46 | s3_envelope | HSCEI@2026-11-19 |  |
| 47 | s3_envelope | NVDA@2026-11-18 |  |
| 48 | s3_envelope | AAPL@2026-11-18 |  |
| 49 | s3_envelope | MSFT@2026-11-18 |  |
| 50 | s3_envelope | TLT@2026-11-18 |  |
| 51 | s3_envelope | IEF@2026-11-18 |  |
| 52 | s3_envelope | SHY@2026-11-18 |  |
| 53 | s3_envelope | HYG@2026-11-18 |  |
| 54 | s3_envelope | LQD@2026-11-18 |  |
| 55 | s3_envelope | GBPUSD@2026-11-18 |  |
| 56 | s3_envelope | WTI_F@2026-11-18 |  |
| 57 | s3_envelope | GLD@2026-11-18 |  |
| 58 | s3_envelope | USO@2026-11-18 |  |
| 59 | s3_envelope | EEM@2026-11-18 |  |
| 60 | s3_envelope | EZU@2026-11-18 |  |
| 61 | s3_envelope | FEZ@2026-11-18 |  |
| 62 | s3_envelope | EWU@2026-11-18 |  |
| 63 | s3_envelope | EWG@2026-11-18 |  |
| 64 | s3_envelope | EWJ@2026-11-18 |  |
| 65 | s3_envelope | INDA@2026-11-18 |  |
| 66 | s3_envelope | FXI@2026-11-18 |  |
| 67 | s3_envelope | BTC@2026-11-17 |  |
| 68 | s3_envelope | HY_IG_DIFF@2026-11-17 |  |

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2025-03 | 0.575783 | 0.0 | rates 68.5%、inflation 11.9% |
| 2 | 2022-06 | 0.784188 | 15.0685 | rates 51.2%、valuation 34.3% |
| 3 | 2023-10 | 0.828843 | 20.5479 | volatility 38.6%、valuation 34.3% |
| 4 | 2021-02 | 1.190346 | 69.863 | rates 85.6%、inflation 7.3% |
| 5 | 2019-12 | 1.191908 | 71.2329 | rates 54.8%、volatility 28.1% |

> 相似≠因果, 更非预测: TOP-N 是历史状态距离最近的时期, 当时之后的演变只是历史记录
> 特征为最新修订口径的描述性对齐, 不代表当时市场信息集(research_mode_gate)
> 距离分位=该候选在全部有效候选中的相对位置, 不是概率

## 日度相关(引擎确定性面·读者版)

- US_REAL_GDP×UNEMPLOYMENT 日收益×日变化 pearson = -0.8936(n=37 对,共同窗 2017-01..2026-07;描述性统计≠因果)


## 质量状态(Audit-R1 F02 四态+Audit-R2 绑定面+Audit-R4 贯通面)

- generated: true(FULL_REPORT 完整装配: L1+L2+L3/L4 全文内联+证据索引)
- machine_verified: True(L3∧L4 produced+纪律校验过+底座非降级或 optional 级显式降级随档)
- run 门(Audit-R4 条目5): blocked_class=None degraded_ok=False
- review: required=True seat_invoked=True verdict=UPHELD fresh=True error=None 修订链档数=1
- copies_consistent(多副本一致): True(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前确定性装配)
- deliverable(可交付): True
- 内容绑定(Audit-R4 条目2): content_sha256=canonical(report.json 剥离 semantic_review)+canonical(agent_judgment.json)+canonical(views_digest.json)——机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。
