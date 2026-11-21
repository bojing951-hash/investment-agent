# 完整研究报告(一键研究 MVP)

- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- run_ok: True | 证据行: 68 | run.ts_utc: 20261121T074411Z

## L1 事实层(引擎确定性产出)

| 指标 | 值 | 单位 | 观测日 | 质量 | 证据 ref |
|---|---|---|---|---|---|
| SPX | 6910.39 | index_point | 2026-11-20 | PASS | SPX@2026-11-20 |
| NDX | 25028.98 | index_point | 2026-11-20 | PASS | NDX@2026-11-20 |
| RUT | 2581.79 | index_point | 2026-11-20 | PASS | RUT@2026-11-20 |
| DXY | 103.81 | index_point | 2026-11-20 | PASS | DXY@2026-11-20 |
| EURUSD | 1.1 | usd_per_eur | 2026-11-20 | PASS | EURUSD@2026-11-20 |
| GOLD_F | 3515.4 | usd_per_oz | 2026-11-20 | PASS | GOLD_F@2026-11-20 |
| SILVER_F | 41.03 | usd_per_oz | 2026-11-20 | PASS | SILVER_F@2026-11-20 |
| BRENT_F | 92.57 | usd_per_barrel | 2026-11-20 | PASS | BRENT_F@2026-11-20 |
| VIX | 35.89 | index_point | 2026-11-20 | PASS | VIX@2026-11-20 |
| DAX | 24802.78 | index_point | 2026-11-20 | PASS | DAX@2026-11-20 |
| CAC40 | 7927.75 | index_point | 2026-11-20 | PASS | CAC40@2026-11-20 |
| USDJPY | 159.71 | jpy_per_usd | 2026-11-20 | PASS | USDJPY@2026-11-20 |
| USDCNY | 6.68 | cny_per_usd | 2026-11-21 | PASS | USDCNY@2026-11-21 |
| HY_OAS | 3.52 | percentage_point | 2026-11-19 | PASS | HY_OAS@2026-11-19 |
| BB_OAS | 2.1 | percentage_point | 2026-11-19 | PASS | BB_OAS@2026-11-19 |
| B_OAS | 3.8 | percentage_point | 2026-11-19 | PASS | B_OAS@2026-11-19 |
| CCC_OAS | 13.61 | percentage_point | 2026-11-19 | PASS | CCC_OAS@2026-11-19 |
| IG_OAS | 0.94 | percentage_point | 2026-11-19 | PASS | IG_OAS@2026-11-19 |
| UST_2Y | 4.76 | percent | 2026-11-19 | PASS | UST_2Y@2026-11-19 |
| UST_10Y | 5.04 | percent | 2026-11-19 | PASS | UST_10Y@2026-11-19 |
| UST_30Y | 5.4 | percent | 2026-11-19 | PASS | UST_30Y@2026-11-19 |
| TIPS_5Y | 2.64 | percent | 2026-11-19 | PASS | TIPS_5Y@2026-11-19 |
| TIPS_10Y | 2.88 | percent | 2026-11-19 | PASS | TIPS_10Y@2026-11-19 |
| BEI_5Y | 2.18 | percent | 2026-11-20 | PASS | BEI_5Y@2026-11-20 |
| BEI_10Y | 2.15 | percent | 2026-11-20 | PASS | BEI_10Y@2026-11-20 |
| CURVE_2S10S | 0.29 | percentage_point | 2026-11-20 | PASS | CURVE_2S10S@2026-11-20 |
| CPI | 337.476 | index_point_1982_84 | 2026-10-01 | WARN | CPI@2026-10-01 |
| CORE_PCE | 130.902 | index_point_2017 | 2026-09-01 | DEGRADED | CORE_PCE@2026-09-01 |
| UNEMPLOYMENT | 4.1 | percent | 2026-10-01 | WARN | UNEMPLOYMENT@2026-10-01 |
| CORE_CPI | 339.9 | index_point_1982_84 | 2026-10-01 | WARN | CORE_CPI@2026-10-01 |
| UST_5Y | 4.86 | percent | 2026-11-19 | PASS | UST_5Y@2026-11-19 |
| INDPRO | 103.3954 | index_point_2017 | 2026-10-01 | WARN | INDPRO@2026-10-01 |
| US_REAL_GDP | 24611.077 | billion_usd | 2026-07-01 | DEGRADED | US_REAL_GDP@2026-07-01 |
| SHCOMP | 3533.79 | index_point | 2026-11-20 | PASS | SHCOMP@2026-11-20 |
| HSI | 22410.8 | index_point | 2026-11-20 | PASS | HSI@2026-11-20 |
| CN_LPR_1Y | 3.0 | percent | 2026-11-20 | WARN | CN_LPR_1Y@2026-11-20 |
| CN_PMI_MFG | 49.3 | index_point | 2026-10-01 | WARN | CN_PMI_MFG@2026-10-01 |
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
### C1-us-inflation-policy · 美国宏观组合从『通胀回落+政策宽松』切换为『通胀再加速+政策再紧缩』: 引擎面显示 CPI 与 CORE_PCE 同比在三锚点间逐级走高,而增长面仅温和放缓(US_REAL_GDP 同比小幅下行、INDPRO 同比回升、UNEMPLOYMENT 平稳)——这是政策面在降息后重新转向加息的宏观背景;该组合下政策路径对通胀数据的敏感度显著上升。
- 依据: 依据证据索引 CPI、CORE_CPI、CORE_PCE、US_REAL_GDP、INDPRO、UNEMPLOYMENT 的锚点观测,以及引擎政策事件簇面(DFEDTARU 路径: 2025-12 降息后 2026-09 重启加息,簇内与 ECB 决议同窗合并计数)。
- 竞争性解释: 若通胀动能主要来自需求韧性(增长未失速、失业率平稳),则紧缩将持续更久、实际利率中枢上移,估值消化期更长
- 竞争性解释: 若通胀再加速主要来自能源与工业品的全球供给脉冲(引擎面 BRENT_F 与 CN_PPI_YOY 同期大幅走高与之相容),则通胀对政策收紧的响应更快、回落也可能更快
- 竞争性解释: 【假设】2025 年秋美国统计发布停摆造成的基期错位与发布延迟可能放大同比读数,通胀回升幅度或被高估——证伪指标: CORE_PCE(若后续修订/新基期下同比回落至停摆前趋势,该解释成立)
### C2-nov-selloff-driver · 最新月窗出现跨资产急跌: SPX 与 NIKKEI225 双位数百分比月跌幅、VIX 大幅冲高、GOLD_F 同月显著回落而 DXY 走高——『股票与黄金同跌+美元走强』的组合在月频分辨率下同时容纳两类机制: 政策再紧缩下实际利率上行对高估值的压制,与流动性收紧/去杠杆冲击;两者对后续通胀预期与信用利差的含义不同。
- 依据: 依据证据索引 SPX、NIKKEI225、DAX、SHCOMP、VIX、GOLD_F、DXY、HY_OAS、UST_10Y 的最新观测、引擎月窗变化面(asset_moves),以及共同交易日利率三分解(数值随 reader_map.rates_decomposition 回贴;近30日名义下行=实际段上行+盈亏平衡下行)。
- 竞争性解释: 若实际利率快速上行是主因,则跌幅应集中于长久期与高估值资产、通胀预期基本锚定、信用利差仅温和走阔(引擎面 HY_OAS 十二个月变化温和与之相容)
- 竞争性解释: 若流动性冲击/去杠杆是主因,则黄金与股票同跌、美元走强、波动率飙升并存(最新月窗形态与之相容),且跨资产相关性趋于同向化
- 竞争性解释: 若增长担忧主导,则盈亏平衡通胀应明显下行且曲线加速趋平——三类机制可用 BEI_10Y 与 CURVE_2S10S 的后续轨迹区分
### C3-policy-divergence · 同一全球再通胀背景下四大央行反应分化: ECB 两度加息、日本持续正常化、美国降息后重启加息、中国政策利率全程不动——分化方向与各地增长-通胀组合的相对位置一致(中国 PMI 三期处于收缩区间、日本增长加速、美国通胀偏高、欧元区政策先行)。
- 依据: 依据证据索引 ECB_DFR、ECB_MRO、JP_POLICY_RATE、CN_LPR_1Y、CN_PMI_MFG 观测与引擎政策事件簇面(2026-09 欧美决议同窗合并为同一全球政策事件)。
- 竞争性解释: 若分化主要由各地国内基本面驱动,后续政策路径将继续跟随各自通胀与增长数据(中国 PMI 修复至50上方前无加息压力)
- 竞争性解释: 【假设】若分化部分源于汇率与资本流动约束(如日元贬值压力影响日本加息节奏、中美利差影响中国宽松空间),则外部利差(美日、中美)是比国内通胀更好的同步指标——引擎面 USDJPY 与美日政策分化同向演变与之相容
- 竞争性解释: 若中国工业品再通胀向核心通胀传导加速,中国『按兵不动』存在边际调整可能——证伪指标: CN_CPI_YOY(若连续数月升至2以上,该解释被强化而非证伪;若停留在1以下,政策不动解释成立)
### 机制链 M1-us-reflation-tightening · 
- 环1 [E1] 环1(观察,通胀): 美国 CPI 同比从12个月前锚的 3.02 升至最近有效观测 3.72(2026-09,最新锚缺基期不可得),CORE_CPI 同比 2.57(2026-09 最近有效)、CORE_PCE 同比 2.85→3.12——通胀再加速为引擎点值面直接可验事实。
- 环2 [E1] 环2(政策反应): 引擎政策事件簇面: 联储 2025-12-10 降25bp后于 2026-09-16 重启加息25bp(与 ECB 2026-09-10 决议同窗±7日,合并为同一全球政策事件 POLCLUSTER-03);ECB 2026-06-11、2026-09-10 各加25bp;日本 2026-04→07 窗政策利率续升。政策面转向可由 ECB_DFR/JP_POLICY_RATE 序列直接验证(DFEDTARU 逐次决议在引擎簇面)。
- 环3 [E1] 环3(利率结构): 共同交易日12个月窗(2025-11-19→2026-11-19)名义 UST_10Y +91bp 全部来自实际段(TIPS_10Y +102bp)而盈亏平衡 BEI_10Y −11bp;UST_2Y 12个月 +125bp(2025-11-21→2026-11-19 自配对原值)高于长端,CURVE_2S10S −26bp 走平——短端政策预期主导利率上行。
- 环4 [E1] 环4(资产): 最新月窗 SPX −10.92%、NIKKEI225 −12.67%、DAX −3.28%、SHCOMP −4.83%,VIX 16.68→35.89(+115.17%),GOLD_F −15.29%、DXY +1.99%;HY_OAS 12个月 +33bp(自配对原值,3.19→3.52)温和走阔——跨资产调整为引擎月窗面原值。
- 环5 [E2] 环5(归因,估值敏感度): 实际利率快速上行在高估值环境(SPX_CAPE z=2.82,引擎 analog 状态面)放大股票久期重定价——此环为推断。
  - 缺环注记: 引擎无『估值-实际利率弹性』序列,该环为【假设】;可验证替代观察: 若该环成立,BEI_10Y 应保持锚定而 SPX 与 TIPS_10Y 同步反向变动。
### 机制链 M2-cn-reflation-commodity · 
- 环1 [E2] 环1(观察,中国再通胀): CN_PPI_YOY 同比 −2.1(2025-10)→3.5(2026-07)→5.7(2026-10),CN_CPI_YOY 0.2→0.7;同期美 CPI 同比 3.02→3.72(最近有效),BRENT_F 12个月 +47.97%(62.56→92.57,自配对原值)——中美价格共振与能源脉冲并存。
  - 缺环注记: CN_PPI_YOY/CN_CPI_YOY 数值在研究计划点值格(引擎确定性面)但不在证据索引68行内,本环 E1 锚不可用;【假设】: 工业品价格回升沿企业定价与库存周期待导,引擎无中国工业库存序列。
- 环2 [E1] 环2(资产面): SHCOMP 最新月窗 −4.83%,跌幅浅于 SPX(−10.92%)与 NIKKEI225(−12.67%);HSI 最新观测 22410.8 在档——A股相对抗跌为引擎月窗面可验事实。
- 环3 [E3] 环3(叙事): 『全球商品脉冲→中国 PPI 回升→制造业名义盈利改善→A 股相对抗跌』整链为叙事层;引擎无中国行业盈利序列。
### 机制链 M3-jpy-normalization · 
- 环1 [E1] 环1(观察,日本): JP_POLICY_RATE 三锚点 0.477→0.978→1.227,JP_CPI_YOY 2.99→1.97→2.44(先回落再回升),东京CPI 2026-09 回升至 2.69,JP_REAL_GDP_YOY 0.63→1.16 加速——『增长加速+通胀回升+持续加息』组合为点值面直接可验事实。
- 环2 [E1] 环2(汇率): USDJPY 12个月 +1.49%(157.37→159.71,2025-11-21→2026-11-20 自配对原值)、自3个月前锚以来 +8.41%(147.32→159.71)——日本加息未能扭转日元弱势,与美国实际利率12个月 +102bp 的利差主导叙事相容。
- 环3 [E3] 环3(叙事): 『日元贬值→输入通胀→支持继续加息』的正反馈为叙事层,引擎无日本进口价格序列;若日元大幅走强后日本通胀仍续升,输入通胀环被证伪。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### S1-tightening-persists · 角色=
- 情景: 基准情景(假设非预测): 假设美国通胀韧性延续、政策维持偏紧甚至再加码,实际利率高位震荡,高估值继续消化、波动中枢抬升。
- 资产方向: 发达市场股票承压或高波动震荡,长久期高估值资产相对劣势;黄金与股票相关性不稳定(流动性压力时段同跌)。 | 置信档: 有相关证据
- 敏感变量: CPI, TIPS_10Y
- 证伪: 指标=CPI | 阈值=2027-01 CPI 同比回落至 2.8 以下且 CORE_PCE 同比回落至 2.8 以下(两者同时成立)则『通胀韧性』假设被证伪 | 次级=CORE_PCE
- 触发: FOMC 2026-12 或 2027-01 会议再度加息,或官方点阵图 2027 路径上移 | 期限: 2027-02-05
### S2-inflation-cools · 角色=
- 情景: 反例情景(假设非预测): 假设核心通胀延续 2026-08 以来的回落(候选面 CORE_CPI 2026-05 2.82→2026-08 2.45),供给脉冲消退,政策转向观望甚至重新讨论降息,估值压力缓解。
- 资产方向: 股票止跌回稳、波动回落,短久期与利率敏感资产相对受益;美元走强压力减弱。 | 置信档: 有相关证据
- 敏感变量: CORE_CPI, BEI_10Y
- 证伪: 指标=CORE_CPI | 阈值=2027-01 核心 CPI 同比回升至 2.8 以上,或 BEI_10Y 升破 2.6(任一成立)则『通胀快速回落』假设被证伪 | 次级=BEI_10Y
- 触发: FOMC 2026-12 会议声明移除进一步紧缩倾向,或 CORE_CPI 同比连续两个月低于 2.5 | 期限: 2027-01-31

## 证据索引

| # | kind | ref | 说明 |
|---|---|---|---|
| 1 | snapshot_fact | SPX@2026-11-20 |  |
| 2 | snapshot_fact | NDX@2026-11-20 |  |
| 3 | snapshot_fact | RUT@2026-11-20 |  |
| 4 | snapshot_fact | DXY@2026-11-20 |  |
| 5 | snapshot_fact | EURUSD@2026-11-20 |  |
| 6 | snapshot_fact | GOLD_F@2026-11-20 |  |
| 7 | snapshot_fact | SILVER_F@2026-11-20 |  |
| 8 | snapshot_fact | BRENT_F@2026-11-20 |  |
| 9 | snapshot_fact | VIX@2026-11-20 |  |
| 10 | snapshot_fact | DAX@2026-11-20 |  |
| 11 | snapshot_fact | CAC40@2026-11-20 |  |
| 12 | snapshot_fact | USDJPY@2026-11-20 |  |
| 13 | snapshot_fact | USDCNY@2026-11-21 |  |
| 14 | snapshot_fact | HY_OAS@2026-11-19 |  |
| 15 | snapshot_fact | BB_OAS@2026-11-19 |  |
| 16 | snapshot_fact | B_OAS@2026-11-19 |  |
| 17 | snapshot_fact | CCC_OAS@2026-11-19 |  |
| 18 | snapshot_fact | IG_OAS@2026-11-19 |  |
| 19 | snapshot_fact | UST_2Y@2026-11-19 |  |
| 20 | snapshot_fact | UST_10Y@2026-11-19 |  |
| 21 | snapshot_fact | UST_30Y@2026-11-19 |  |
| 22 | snapshot_fact | TIPS_5Y@2026-11-19 |  |
| 23 | snapshot_fact | TIPS_10Y@2026-11-19 |  |
| 24 | snapshot_fact | BEI_5Y@2026-11-20 |  |
| 25 | snapshot_fact | BEI_10Y@2026-11-20 |  |
| 26 | snapshot_fact | CURVE_2S10S@2026-11-20 |  |
| 27 | snapshot_fact | CPI@2026-10-01 |  |
| 28 | snapshot_fact | CORE_PCE@2026-09-01 |  |
| 29 | snapshot_fact | UNEMPLOYMENT@2026-10-01 |  |
| 30 | snapshot_fact | CORE_CPI@2026-10-01 |  |
| 31 | snapshot_fact | UST_5Y@2026-11-19 |  |
| 32 | snapshot_fact | INDPRO@2026-10-01 |  |
| 33 | snapshot_fact | US_REAL_GDP@2026-07-01 |  |
| 34 | snapshot_fact | SHCOMP@2026-11-20 |  |
| 35 | snapshot_fact | HSI@2026-11-20 |  |
| 36 | snapshot_fact | CN_LPR_1Y@2026-11-20 |  |
| 37 | snapshot_fact | CN_PMI_MFG@2026-10-01 |  |
| 38 | snapshot_fact | NIKKEI225@2026-11-20 |  |
| 39 | snapshot_fact | JP_CPI_YOY@2026-10-01 |  |
| 40 | snapshot_fact | ECB_DFR@2026-09-16 |  |
| 41 | snapshot_fact | ECB_MRO@2026-09-16 |  |
| 42 | snapshot_fact | EA_HICP_YOY@2025-12-01 |  |
| 43 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 44 | s3_envelope | SZCI@2026-11-20 |  |
| 45 | s3_envelope | CHINEXT@2026-11-20 |  |
| 46 | s3_envelope | HSCEI@2026-11-20 |  |
| 47 | s3_envelope | NVDA@2026-11-20 |  |
| 48 | s3_envelope | AAPL@2026-11-20 |  |
| 49 | s3_envelope | MSFT@2026-11-20 |  |
| 50 | s3_envelope | TLT@2026-11-20 |  |
| 51 | s3_envelope | IEF@2026-11-20 |  |
| 52 | s3_envelope | SHY@2026-11-20 |  |
| 53 | s3_envelope | HYG@2026-11-20 |  |
| 54 | s3_envelope | LQD@2026-11-20 |  |
| 55 | s3_envelope | GBPUSD@2026-11-20 |  |
| 56 | s3_envelope | WTI_F@2026-11-20 |  |
| 57 | s3_envelope | GLD@2026-11-20 |  |
| 58 | s3_envelope | USO@2026-11-20 |  |
| 59 | s3_envelope | EEM@2026-11-20 |  |
| 60 | s3_envelope | EZU@2026-11-20 |  |
| 61 | s3_envelope | FEZ@2026-11-20 |  |
| 62 | s3_envelope | EWU@2026-11-20 |  |
| 63 | s3_envelope | EWG@2026-11-20 |  |
| 64 | s3_envelope | EWJ@2026-11-20 |  |
| 65 | s3_envelope | INDA@2026-11-20 |  |
| 66 | s3_envelope | FXI@2026-11-20 |  |
| 67 | s3_envelope | BTC@2026-11-19 |  |
| 68 | s3_envelope | HY_IG_DIFF@2026-11-19 |  |

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2022-06 | 0.937493 | 0.0 | rates 37.0%、volatility 30.8% |
| 2 | 2025-03 | 0.971202 | 1.3699 | volatility 67.6%、rates 22.8% |
| 3 | 2020-10 | 1.288514 | 28.7671 | rates 88.6%、valuation 5.3% |
| 4 | 2023-10 | 1.298078 | 32.8767 | volatility 73.7%、valuation 14.0% |
| 5 | 2019-10 | 1.694433 | 94.5205 | volatility 41.1%、rates 35.1% |

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
