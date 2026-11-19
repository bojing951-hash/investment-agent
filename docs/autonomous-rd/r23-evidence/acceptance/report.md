# 一键研究报告(零模型编排 v2.0)
- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 运行: 20261119T173248Z @ b316e88b2b4a98e95ab23aeac71a304485e78b0f
- 快照: research_snapshot_20261119 (target 20261119)
- 数据门(gate_a): 61/61 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、中国(CN)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 22 项 | 对照点锚 12个月前@2025-11-19、3个月前@2026-08-19、最新一期@2026-11-19 | 事后偏移+3月/6月/12月(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 9 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_POLICY_OVERNIGHT(缺什么: CN_POLICY_OVERNIGHT(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内首观测2026-11-02晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内有效观测 n=14<131(日历期望262×半额;总量14不替代窗口归属)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_OMO_7D(缺什么: CN_OMO_7D(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内首观测2025-12-08晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-10-30早于窗止-10天容忍(发布滞后外缺口)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_MRO(缺什么: ECB_MRO(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<131(日历期望262×半额;总量48不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_DFR(缺什么: ECB_DFR(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<131(日历期望262×半额;总量69不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_REAL_GDP_YOY(缺什么: JP_REAL_GDP_YOY(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_CPI_YOY(缺什么: JP_CPI_YOY(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过

## 四层区分

### L1 事实层 available=True
- SPX = 7323.63 index_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:SPX@2026-11-18]
- NDX = 27116.26 index_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:NDX@2026-11-18]
- RUT = 2714.31 index_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:RUT@2026-11-18]
- DXY = 103.78 index_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:DXY@2026-11-18]
- EURUSD = 1.1 usd_per_eur @2026-11-18 [质量:PASS] [来源:snapshot_fact:EURUSD@2026-11-18]
- GOLD_F = 3727.8 usd_per_oz @2026-11-18 [质量:PASS] [来源:snapshot_fact:GOLD_F@2026-11-18]
- SILVER_F = 44.97 usd_per_oz @2026-11-18 [质量:PASS] [来源:snapshot_fact:SILVER_F@2026-11-18]
- BRENT_F = 88.68 usd_per_barrel @2026-11-18 [质量:PASS] [来源:snapshot_fact:BRENT_F@2026-11-18]
- VIX = 24.56 index_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:VIX@2026-11-18]
- DAX = 26045.37 index_point @2026-11-17 [质量:PASS] [来源:snapshot_fact:DAX@2026-11-17]
- CAC40 = 8216.78 index_point @2026-11-17 [质量:PASS] [来源:snapshot_fact:CAC40@2026-11-17]
- USDJPY = 159.3 jpy_per_usd @2026-11-18 [质量:PASS] [来源:snapshot_fact:USDJPY@2026-11-18]
- USDCNY = 6.66 cny_per_usd @2026-11-18 [质量:PASS] [来源:snapshot_fact:USDCNY@2026-11-18]
- HY_OAS = 3.43 percentage_point @2026-11-17 [质量:PASS] [来源:snapshot_fact:HY_OAS@2026-11-17]
- BB_OAS = 2.04 percentage_point @2026-11-17 [质量:PASS] [来源:snapshot_fact:BB_OAS@2026-11-17]
- B_OAS = 3.68 percentage_point @2026-11-17 [质量:PASS] [来源:snapshot_fact:B_OAS@2026-11-17]
- CCC_OAS = 13.29 percentage_point @2026-11-17 [质量:PASS] [来源:snapshot_fact:CCC_OAS@2026-11-17]
- IG_OAS = 0.92 percentage_point @2026-11-17 [质量:PASS] [来源:snapshot_fact:IG_OAS@2026-11-17]
- UST_2Y = 4.8 percent @2026-11-17 [质量:PASS] [来源:snapshot_fact:UST_2Y@2026-11-17]
- UST_10Y = 5.1 percent @2026-11-17 [质量:PASS] [来源:snapshot_fact:UST_10Y@2026-11-17]
- UST_30Y = 5.46 percent @2026-11-17 [质量:PASS] [来源:snapshot_fact:UST_30Y@2026-11-17]
- TIPS_5Y = 2.64 percent @2026-11-17 [质量:PASS] [来源:snapshot_fact:TIPS_5Y@2026-11-17]
- TIPS_10Y = 2.89 percent @2026-11-17 [质量:PASS] [来源:snapshot_fact:TIPS_10Y@2026-11-17]
- BEI_5Y = 2.23 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:BEI_5Y@2026-11-18]
- BEI_10Y = 2.19 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:BEI_10Y@2026-11-18]
- CURVE_2S10S = 0.27 percentage_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:CURVE_2S10S@2026-11-18]
- CPI = 337.476 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CPI@2026-10-01]
- CORE_PCE = 130.902 index_point_2017 @2026-09-01 [质量:DEGRADED] [来源:snapshot_fact:CORE_PCE@2026-09-01]
- UNEMPLOYMENT = 4.1 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:UNEMPLOYMENT@2026-10-01]
- CORE_CPI = 339.9 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CORE_CPI@2026-10-01]
- UST_5Y = 4.9 percent @2026-11-17 [质量:PASS] [来源:snapshot_fact:UST_5Y@2026-11-17]
- INDPRO = 103.3954 index_point_2017 @2026-10-01 [质量:WARN] [来源:snapshot_fact:INDPRO@2026-10-01]
- US_REAL_GDP = 24611.077 billion_usd @2026-07-01 [质量:DEGRADED] [来源:snapshot_fact:US_REAL_GDP@2026-07-01]
- SHCOMP = 3587.83 index_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:SHCOMP@2026-11-18]
- HSI = 22814.93 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:HSI@2026-11-19]
- CN_LPR_1Y = 3.0 percent @2026-10-20 [质量:WARN] [来源:snapshot_fact:CN_LPR_1Y@2026-10-20]
- CN_PMI_MFG = 49.3 index_point @2026-10-01 [质量:WARN] [来源:snapshot_fact:CN_PMI_MFG@2026-10-01]
- NIKKEI225 = 59024.28 index_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-11-18]
- JP_CPI_YOY = 2.16 percent @2026-09-01 [质量:DEGRADED] [来源:snapshot_fact:JP_CPI_YOY@2026-09-01]
- ECB_DFR = 2.5 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_DFR@2026-09-16]
- ECB_MRO = 2.65 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_MRO@2026-09-16]
- EA_HICP_YOY = 4.0 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:EA_HICP_YOY@2026-10-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **CON-1**: 过去十二个月 UST_10Y 名义利率的上行几乎全部由 TIPS_10Y 实际利率分量承担,BEI_10Y 盈亏平衡通胀分量净变动为轻微负值(引擎共同交易日三利率同窗分解,数值回贴见 reader_map.rates_decomposition)——市场重定价发生在实际贴现率,而非通胀预期失控。
  - 依据: 引擎面: 美联储2025-12降息后于2026-09转加息(DFEDTARU),DFF 同窗同向印证;欧央行2026-06与2026-09两度加息(ECB_DFR);同期 CPI 同比自2026-02抬头(候选面),而盈亏平衡分量未随通胀读数走高。名义-实际-盈亏平衡的分解结构是本期最稳定的客观事实之一,也是传导链『全球再通胀→政策转紧→实际利率』的起点。
  - 竞争性解释1: 主解释: 若政策紧缩预期是主因,实际利率随加息预期上行而盈亏平衡受控——与引擎面观察一致
  - 竞争性解释2: 竞争解释一: 若自然利率/增长前景上移主导(INDPRO 同比后段抬升),实际利率同样上行,与通胀和政策无关
  - 竞争性解释3: 竞争解释二: 若期限溢价抬升(财政供给担忧)主导,名义与实际同升且盈亏平衡可以不动——亦容纳观察
  - 证据: UST_10Y@2026-11-17, TIPS_10Y@2026-11-17, BEI_10Y@2026-11-18, INDPRO@2026-10-01, ECB_DFR@2026-09-16, CPI@2026-10-01
- **CON-2**: 近月风险资产与黄金同向回落、美元指数走强、波动率大幅抬升(引擎资产月窗: SPX、NIKKEI225、GOLD_F、SHCOMP 下行,DXY 上行,VIX 跳升;窗口两端日与数值逐项回贴 asset_returns_echo)——股金同跌叠加美元强与波动升,是当前最突出的待解释事实组合。
  - 依据: 引擎面资产月窗为同窗复算口径(界日无观测取最近邻,两端实测日随行披露)。GOLD_F 与股票同向下行这一组合排除了『单纯避险』的简单叙事(避险通常对应黄金上行),将解释压缩到贴现率/流动性/增长三类,对质面见传导链。
  - 竞争性解释1: 若实际利率急升是主因(贴现率渠道),长久期与无现金流资产同跌、美元走强——与观察一致
  - 竞争性解释2: 若流动性/保证金冲击主导,黄金与股票同跌、VIX 跳升、美元因平仓回流走强——同样容纳观察
  - 竞争性解释3: 若增长担忧主导,盈亏平衡通胀分量应与股票同向下行而黄金相对抗跌——该组合与本轮观察部分不符
  - 证据: SPX@2026-11-18, GOLD_F@2026-11-18, VIX@2026-11-18, DXY@2026-11-18, NIKKEI225@2026-11-18, TIPS_10Y@2026-11-17, BEI_10Y@2026-11-18
- **机制链 MECH-1**: 全球再通胀→政策转紧→实际利率上行→风险资产重定价
  - E1 E1 环: 2026-02→05 美/中/欧通胀同比同步抬升: CPI 同比自2.434(2026-02)升至4.1666(2026-05),CN_PPI_YOY 自-0.9(2026-02)升至3.9(2026-05;零线穿越在2026-03=0.5),EA_HICP_YOY 自1.9(2026-02)升至3.2(2026-05)——引擎转折候选面前三候选同窗,月频观测先后未定;此后政策转紧: 美联储2026-09-16加息25bp(DFEDTARU 3.75→4.0)、欧央行2026-06-11与2026-09-10各加息25bp(ECB_DFR 2.0→2.25(2026-06-11)→2.5(2026-09-10)) [证据: CPI@2026-10-01, EA_HICP_YOY@2026-10-01, CN_PMI_MFG@2026-10-01, ECB_DFR@2026-09-16]
  - E2 E2 环: 政策紧缩预期→实际利率上行: 引擎无『政策预期/点阵图』序列,此环为【假设】;可验证邻环=实际利率已大幅上行(12个月窗 TIPS_10Y +104bp;近月窗2026-10-16→2026-11-17 +15bp)且政策已实际转紧 [缺失环: 本引擎无政策预期/点阵图序列,『预期→实际利率』环节为【假设】,以两端可验证观测夹逼]
  - E1 E1 环: 实际利率与风险资产反向(资产侧观测): 近月资产月窗(2026-10-19→2026-11-18/17)SPX -4.77%、NIKKEI225 -9.08%、GOLD_F -10.39%、SHCOMP -3.84%、DXY +1.76%、VIX +33.19%、UST_10Y -0.97%、DAX +2.87%——股金同跌、美元走强、波动跳升 [证据: SPX@2026-11-18, TIPS_10Y@2026-11-17, VIX@2026-11-18, GOLD_F@2026-11-18]
- **机制链 MECH-2**: 中国生产价格再通胀→全球制造业/商品渠道→美国通胀结构
  - E1 E1 环: CN_PPI_YOY 自2026-02的-0.9升至2026-05的3.9(2026-03转正0.5),2026-10达5.7;CN_PMI_MFG 同比自-2.3904(2026-02)转正至1.0101(2026-05),水平值围绕荣枯线反复: 2026-03=50.4、04=50.3、06=50.3、09=50.1四个月高于50,2026-05=50.0恰在荣枯线上,2026-02=49.0与最新2026-10=49.3低于50(最新同比0.61)——上方停留未持续,价修复强于量修复 [证据: CN_PMI_MFG@2026-10-01]
  - E2 E2 环: 中国生产价格→美国商品需求/工业生产传导: 引擎无双边贸易/订单序列,此环为【假设】;邻环可验证=INDPRO 同比自1.25(2026-07观测)升至2.15(2026-10观测) [缺失环: 【假设】: 本引擎无双边贸易/新订单序列,跨国传导环节以两端观测夹逼]
  - E3 E3 环(纯叙事推演,整环【假设】): 若中国生产价格上行经商品渠道输出至美国,整体CPI相对核心偏强的结构应延续;证伪指标=CORE_PCE——若 CORE_PCE 升速持续反超 CPI(同比差转负收窄),商品渠道叙事被削弱 [证伪指标: CORE_PCE]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **SCN-A**(基准)
  - 情景: 情景A(假设非预测): 再通胀-紧缩延续——通胀读数维持高位,政策维持紧缩倾向,实际利率高位,盈亏平衡受控。
  - 资产方向判断: 风险资产估值承压、实际利率维持高位、盈亏平衡受控;美元相对偏强;长久期与高估值资产相对弱势。(置信: 有相关证据) 与近月窗观察同向(实际利率上行+风险资产回落+盈亏平衡偏弱)
  - 敏感变量: TIPS_10Y, CPI
  - 证伪指标: BEI_10Y 阈值 BEI_10Y 升破3.0%(较2026-11-17的2.21明显抬升)即证伪『盈亏平衡受控』分句
  - 触发条件: 未来两次FOMC会议之一再加息,或 CPI 最近有效同比连续不低于3.5%(时限 2027-03-31)
- **SCN-B**(反例)
  - 情景: 情景B(假设非预测): 增长担忧接管——增长动能转弱成为主导叙事,政策由紧转松预期升温。
  - 资产方向判断: 股票承压先于通胀见顶,盈亏平衡下行快于名义,收益率曲线先平后陡,黄金先弱后稳。(置信: 纯逻辑推理) 反例情景: 与基准分立的增长路径
  - 敏感变量: UNEMPLOYMENT, BEI_10Y
  - 证伪指标: UNEMPLOYMENT 阈值 失业率维持在4.1或更低且 CPI 同比升破4.2,即证伪本情景(增长未弱且通胀再上行)
  - 触发条件: UNEMPLOYMENT 连续两个月不低于4.4,或 INDPRO 同比转负(时限 2027-06-30)

## 语义审查(席位已裁)

- 席位裁决: REVISE(档: audit/semantic_review/20261120/VERDICT-20261119T173248Z-02.json)

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


## Agent 判断落位

- attached=True(schema 1.1;violations=0)

## 步骤台账

- [OK |不适用] S1_decompose 
- [OK |语义✔] S2_doctor 
- [OK |语义✔] S3_overview_US 
- [OK |语义✔] S3_overview_CN 
- [OK |语义✔] S3_overview_EA 
- [OK |语义✔] S3_overview_JP 
- [OK |语义✔] S3_overview_GLOBAL 
- [OK |语义✔] S3_changes 
- [OK |语义✔] S4_history_US_REAL_GDP 
- [OK |语义✔] S4_history_UNEMPLOYMENT 
- [OK |语义✔] S4_history_INDPRO 
- [OK |语义✔] S4_history_CPI 
- [OK |语义✔] S4_history_CORE_CPI 
- [OK |语义✔] S4_history_CORE_PCE 
- [OK |语义✔] S4_history_DFEDTARU 
- [OK |语义✔] S4_history_DFF 
- [OK |语义✔] S4_history_CN_PMI_MFG 
- [OK |语义✔] S4_history_CN_CPI_YOY 
- [OK |语义✔] S4_history_CN_PPI_YOY 
- [OK |语义✔] S4_history_CN_POLICY_OVERNIGHT 
- [OK |语义✔] S4_history_CN_OMO_7D 
- [OK |语义✔] S4_history_CN_LPR_1Y 
- [OK |语义✔] S4_history_EA_REAL_GDP_YOY 
- [OK |语义✔] S4_history_EA_HICP_YOY 
- [OK |语义✔] S4_history_ECB_MRO 
- [OK |语义✔] S4_history_ECB_DFR 
- [OK |语义✔] S4_history_JP_REAL_GDP_YOY 
- [OK |语义✔] S4_history_JP_CPI_YOY 
- [OK |语义✔] S4_history_JP_CPI_TOKYO_YOY 
- [OK |语义✔] S4_history_JP_POLICY_RATE 
- [OK |语义✔] S4_history_UST_10Y 
- [OK |语义✔] S4_history_TIPS_10Y 
- [OK |语义✔] S4_history_BEI_10Y 
- [OK |语义✔] S4_history_UST_2Y 
- [OK |语义✔] S4_history_UST_5Y 
- [OK |语义✔] S4_history_UST_30Y 
- [OK |语义✔] S4_history_TIPS_5Y 
- [OK |语义✔] S4_history_BEI_5Y 
- [OK |语义✔] S4_history_CURVE_2S10S 
- [OK |语义✔] S4_history_SPX 
- [OK |语义✔] S4_history_NDX 
- [OK |语义✔] S4_history_RUT 
- [OK |语义✔] S4_history_DAX 
- [OK |语义✔] S4_history_CAC40 
- [OK |语义✔] S4_history_NIKKEI225 
- [OK |语义✔] S4_history_HSI 
- [OK |语义✔] S4_history_SHCOMP 
- [OK |语义✔] S4_history_DXY 
- [OK |语义✔] S4_history_EURUSD 
- [OK |语义✔] S4_history_USDJPY 
- [OK |语义✔] S4_history_USDCNY 
- [OK |语义✔] S4_history_GOLD_F 
- [OK |语义✔] S4_history_SILVER_F 
- [OK |语义✔] S4_history_BRENT_F 
- [OK |语义✔] S4_history_HY_OAS 
- [OK |语义✔] S4_history_IG_OAS 
- [OK |语义✔] S4_history_BB_OAS 
- [OK |语义✔] S4_history_B_OAS 
- [OK |语义✔] S4_history_CCC_OAS 
- [OK |语义✔] S4_history_VIX 
- [OK |语义✔] S5_compare 命中 52 个指标,compare 仅取注册表序前 2(US_REAL_GDP,UNEMPLOYMENT);其余 INDPRO,CPI,CORE_CPI,CORE_PCE,DFEDTARU,DFF,CN_PMI_MFG,CN_CPI_YOY,CN_PPI_YOY,CN_POLICY_OVERNIGHT,CN_OMO_7D,CN_LPR_1Y,EA_REAL_GDP_YOY,EA_HICP_YOY,ECB_MRO,ECB_DFR,JP_REAL_GDP_YOY,JP_CPI_YOY,JP_CPI_TOKYO_YOY,JP_POLICY_RATE,UST_10Y,TIPS_10Y,BEI_10Y,UST_2Y,UST_5Y,UST_30Y,TIPS_5Y,BEI_5Y,CURVE_2S10S,SPX,NDX,RUT,DAX,CAC40,NIKKEI225,HSI,SHCOMP,DXY,EURUSD,USDJPY,USDCNY,GOLD_F,SILVER_F,BRENT_F,HY_OAS,IG_OAS,BB_OAS,B_OAS,CCC_OAS,VIX 以 L1 事实行呈现,如需对比另行单跑
- [OK |语义✔] S6_analog 
- [OK |不适用] S7_mode_gate 
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(68 行)

- snapshot_fact:SPX@2026-11-18 → SPX
- snapshot_fact:NDX@2026-11-18 → NDX
- snapshot_fact:RUT@2026-11-18 → RUT
- snapshot_fact:DXY@2026-11-18 → DXY
- snapshot_fact:EURUSD@2026-11-18 → EURUSD
- snapshot_fact:GOLD_F@2026-11-18 → GOLD_F
- snapshot_fact:SILVER_F@2026-11-18 → SILVER_F
- snapshot_fact:BRENT_F@2026-11-18 → BRENT_F
- snapshot_fact:VIX@2026-11-18 → VIX
- snapshot_fact:DAX@2026-11-17 → DAX
- snapshot_fact:CAC40@2026-11-17 → CAC40
- snapshot_fact:USDJPY@2026-11-18 → USDJPY
- snapshot_fact:USDCNY@2026-11-18 → USDCNY
- snapshot_fact:HY_OAS@2026-11-17 → HY_OAS
- snapshot_fact:BB_OAS@2026-11-17 → BB_OAS
- snapshot_fact:B_OAS@2026-11-17 → B_OAS
- snapshot_fact:CCC_OAS@2026-11-17 → CCC_OAS
- snapshot_fact:IG_OAS@2026-11-17 → IG_OAS
- snapshot_fact:UST_2Y@2026-11-17 → UST_2Y
- snapshot_fact:UST_10Y@2026-11-17 → UST_10Y
- snapshot_fact:UST_30Y@2026-11-17 → UST_30Y
- snapshot_fact:TIPS_5Y@2026-11-17 → TIPS_5Y
- snapshot_fact:TIPS_10Y@2026-11-17 → TIPS_10Y
- snapshot_fact:BEI_5Y@2026-11-18 → BEI_5Y
- snapshot_fact:BEI_10Y@2026-11-18 → BEI_10Y
- snapshot_fact:CURVE_2S10S@2026-11-18 → CURVE_2S10S
- snapshot_fact:CPI@2026-10-01 → CPI
- snapshot_fact:CORE_PCE@2026-09-01 → CORE_PCE
- snapshot_fact:UNEMPLOYMENT@2026-10-01 → UNEMPLOYMENT
- snapshot_fact:CORE_CPI@2026-10-01 → CORE_CPI
- snapshot_fact:UST_5Y@2026-11-17 → UST_5Y
- snapshot_fact:INDPRO@2026-10-01 → INDPRO
- snapshot_fact:US_REAL_GDP@2026-07-01 → US_REAL_GDP
- snapshot_fact:SHCOMP@2026-11-18 → SHCOMP
- snapshot_fact:HSI@2026-11-19 → HSI
- snapshot_fact:CN_LPR_1Y@2026-10-20 → CN_LPR_1Y
- snapshot_fact:CN_PMI_MFG@2026-10-01 → CN_PMI_MFG
- snapshot_fact:NIKKEI225@2026-11-18 → NIKKEI225
- snapshot_fact:JP_CPI_YOY@2026-09-01 → JP_CPI_YOY
- snapshot_fact:ECB_DFR@2026-09-16 → ECB_DFR
- snapshot_fact:ECB_MRO@2026-09-16 → ECB_MRO
- snapshot_fact:EA_HICP_YOY@2026-10-01 → EA_HICP_YOY
- snapshot_fact:JP_POLICY_RATE@2026-10-01 → JP_POLICY_RATE
- s3_envelope:SZCI@2026-11-18 → SZCI
- s3_envelope:CHINEXT@2026-11-18 → CHINEXT
- s3_envelope:HSCEI@2026-11-19 → HSCEI
- s3_envelope:NVDA@2026-11-18 → NVDA
- s3_envelope:AAPL@2026-11-18 → AAPL
- s3_envelope:MSFT@2026-11-18 → MSFT
- s3_envelope:TLT@2026-11-18 → TLT
- s3_envelope:IEF@2026-11-18 → IEF
- s3_envelope:SHY@2026-11-18 → SHY
- s3_envelope:HYG@2026-11-18 → HYG
- s3_envelope:LQD@2026-11-18 → LQD
- s3_envelope:GBPUSD@2026-11-18 → GBPUSD
- s3_envelope:WTI_F@2026-11-18 → WTI_F
- s3_envelope:GLD@2026-11-18 → GLD
- s3_envelope:USO@2026-11-18 → USO
- s3_envelope:EEM@2026-11-18 → EEM
- s3_envelope:EZU@2026-11-18 → EZU
- s3_envelope:FEZ@2026-11-18 → FEZ
- s3_envelope:EWU@2026-11-18 → EWU
- s3_envelope:EWG@2026-11-18 → EWG
- s3_envelope:EWJ@2026-11-18 → EWJ
- s3_envelope:INDA@2026-11-18 → INDA
- s3_envelope:FXI@2026-11-18 → FXI
- s3_envelope:BTC@2026-11-17 → BTC
- s3_envelope:HY_IG_DIFF@2026-11-17 → HY_IG_DIFF

## 注记

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、CORE_PCE、CN_POLICY_OVERNIGHT、CN_OMO_7D、EA_REAL_GDP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY、JP_CPI_YOY
