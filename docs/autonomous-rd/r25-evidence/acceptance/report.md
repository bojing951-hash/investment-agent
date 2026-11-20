# 一键研究报告(零模型编排 v2.0)
- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 运行: 20261120T072551Z @ None
- 快照: research_snapshot_20261120_v2 (target 20261120)
- 数据门(gate_a): 61/61 信封步非 OK(DEGRADED)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、中国(CN)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 22 项 | 对照点锚 12个月前@2025-11-20、3个月前@2026-08-20、最新一期@2026-11-20 | 事后偏移+3月/6月/12月(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 8 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_POLICY_OVERNIGHT(缺什么: CN_POLICY_OVERNIGHT(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内首观测2026-11-02晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内有效观测 n=15<131(日历期望262×半额;总量15不替代窗口归属)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_OMO_7D(缺什么: CN_OMO_7D(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内首观测2025-12-08晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-10-30早于窗止-10天容忍(发布滞后外缺口)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_MRO(缺什么: ECB_MRO(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<131(日历期望262×半额;总量48不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_DFR(缺什么: ECB_DFR(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<131(日历期望262×半额;总量69不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_REAL_GDP_YOY(缺什么: JP_REAL_GDP_YOY(任务窗2025-11-20..2026-11-20)——任务窗窗口成员/覆盖不满足;任务窗2025-11-20..2026-11-20未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过

## 四层区分

### L1 事实层 available=True
- SPX = 7175.83 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:SPX@2026-11-19]
- NDX = 26517.05 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:NDX@2026-11-19]
- RUT = 2655.11 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:RUT@2026-11-19]
- DXY = 103.8 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:DXY@2026-11-20]
- EURUSD = 1.1 usd_per_eur @2026-11-20 [质量:PASS] [来源:snapshot_fact:EURUSD@2026-11-20]
- GOLD_F = 3547.5 usd_per_oz @2026-11-20 [质量:PASS] [来源:snapshot_fact:GOLD_F@2026-11-20]
- SILVER_F = 41.78 usd_per_oz @2026-11-20 [质量:PASS] [来源:snapshot_fact:SILVER_F@2026-11-20]
- BRENT_F = 89.56 usd_per_barrel @2026-11-20 [质量:PASS] [来源:snapshot_fact:BRENT_F@2026-11-20]
- VIX = 28.44 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:VIX@2026-11-19]
- DAX = 25463.81 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:DAX@2026-11-19]
- CAC40 = 8080.74 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:CAC40@2026-11-19]
- USDJPY = 159.15 jpy_per_usd @2026-11-20 [质量:PASS] [来源:snapshot_fact:USDJPY@2026-11-20]
- USDCNY = 6.67 cny_per_usd @2026-11-20 [质量:PASS] [来源:snapshot_fact:USDCNY@2026-11-20]
- HY_OAS = 3.47 percentage_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:HY_OAS@2026-11-18]
- BB_OAS = 2.05 percentage_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:BB_OAS@2026-11-18]
- B_OAS = 3.73 percentage_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:B_OAS@2026-11-18]
- CCC_OAS = 13.53 percentage_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:CCC_OAS@2026-11-18]
- IG_OAS = 0.93 percentage_point @2026-11-18 [质量:PASS] [来源:snapshot_fact:IG_OAS@2026-11-18]
- UST_2Y = 4.8 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:UST_2Y@2026-11-18]
- UST_10Y = 5.07 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:UST_10Y@2026-11-18]
- UST_30Y = 5.41 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:UST_30Y@2026-11-18]
- TIPS_5Y = 2.66 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:TIPS_5Y@2026-11-18]
- TIPS_10Y = 2.88 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:TIPS_10Y@2026-11-18]
- BEI_5Y = 2.22 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:BEI_5Y@2026-11-19]
- BEI_10Y = 2.16 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:BEI_10Y@2026-11-19]
- CURVE_2S10S = 0.28 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:CURVE_2S10S@2026-11-19]
- CPI = 337.476 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CPI@2026-10-01]
- CORE_PCE = 130.902 index_point_2017 @2026-09-01 [质量:DEGRADED] [来源:snapshot_fact:CORE_PCE@2026-09-01]
- UNEMPLOYMENT = 4.1 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:UNEMPLOYMENT@2026-10-01]
- CORE_CPI = 339.9 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CORE_CPI@2026-10-01]
- UST_5Y = 4.89 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:UST_5Y@2026-11-18]
- INDPRO = 103.3954 index_point_2017 @2026-10-01 [质量:WARN] [来源:snapshot_fact:INDPRO@2026-10-01]
- US_REAL_GDP = 24611.077 billion_usd @2026-07-01 [质量:DEGRADED] [来源:snapshot_fact:US_REAL_GDP@2026-07-01]
- SHCOMP = 3577.6174 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:SHCOMP@2026-11-19]
- HSI = 22369.58 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:HSI@2026-11-20]
- CN_LPR_1Y = 3.0 percent @2026-11-20 [质量:WARN] [来源:snapshot_fact:CN_LPR_1Y@2026-11-20]
- CN_CPI_YOY = 0.7 percent @2026-10-31 [质量:WARN] [来源:snapshot_fact:CN_CPI_YOY@2026-10-31]
- CN_PPI_YOY = 5.7 percent @2026-10-31 [质量:WARN] [来源:snapshot_fact:CN_PPI_YOY@2026-10-31]
- CN_PMI_MFG = 49.3 index_point @2026-10-01 [质量:WARN] [来源:snapshot_fact:CN_PMI_MFG@2026-10-01]
- DFF = 3.88 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:DFF@2026-11-18]
- DFEDTARU = 4.0 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:DFEDTARU@2026-11-19]
- NIKKEI225 = 59444.21 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-11-19]
- JP_CPI_YOY = 2.44 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_CPI_YOY@2026-10-01]
- ECB_DFR = 2.5 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_DFR@2026-09-16]
- ECB_MRO = 2.65 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_MRO@2026-09-16]
- EA_HICP_YOY = 4.0 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:EA_HICP_YOY@2026-10-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **CON-1**: 四地环境走位综合:美国由降息周期转为重新加息(有效联邦基金利率最新为 3.88%),中国生产价格强再通胀(CN_PPI_YOY 最新为 5.7%),欧元区通胀连续上行并伴随两次加息(HICP 同比最新为百分之四),日本全年持续上调政策利率(JP_POLICY_RATE 最新月均为 1.227%)——全球宏观从一年前的分化格局走向通胀实现值普遍上行与政策普遍转紧。数据不可得面如实在场:日本政策目标序列不在注册表,美国 CPI 最新一期缺基期格同比不可得,欧元区与日本实际 GDP 末观测滞后标注。
  - 依据: 证据: 快照事实行 DFEDTARU、CN_PPI_YOY、EA_HICP_YOY、JP_POLICY_RATE、ECB_DFR;政策决议日与生效日见引擎政策事件簇与政策口径四分面。
  - 竞争性解释1: 解释一(共同冲击): 全球能源与商品价格共同冲击推动四地通胀实现值同窗上行,央行后顾型响应转向紧缩——若如此,三地通胀同月转折是共同原因的结果,能源价格应同窗大涨(引擎面 BRENT_F 同窗观测支持此解释)
  - 竞争性解释2: 解释二(中国出口链): 中国生产价格经出口商品链向外传导——若如此,中国 PPI 应领先美欧 CPI 转折;但月频证据下三地同月转折、先后未定,该解释与解释一暂不可分
  - 竞争性解释3: 解释三(各地独立因素叠加): 美国财政/关税、欧元区能源、日本工资等本国因素碰巧同期共振——引擎无分项成因序列,此解释不可验,列为备选
  - 证据: DFEDTARU@2026-11-19, CN_PPI_YOY@2026-10-31, EA_HICP_YOY@2026-10-01, JP_POLICY_RATE@2026-10-01, ECB_DFR@2026-09-16, BRENT_F@2026-11-20
- **CON-2**: 证据最充分的机制环节在利率结构:美债名义利率过去十二个月的上行几乎全部由实际利率贡献(UST_10Y 最新为 5.07%,TIPS_10Y 为 2.88%),盈亏平衡分量十二个月净变动接近零——这与「央行响应已实现通胀、市场通胀预期保持锚定」的解释相容,而与「通胀预期失控」叙事不相容;同期风险资产与贵金属回调、美元走强(VIX 最新处于高位)。
  - 依据: 证据: 快照事实行 UST_10Y、TIPS_10Y、BEI_10Y、VIX、DXY、SPX、GOLD_F;三利率共同交易日同窗分解(年度窗与月度窗数值)见读者报告美债三利率分解节,本句不重复数字。
  - 竞争性解释1: 主解释(政策渠道): 央行紧缩叠加期限溢价推升实际利率——若如此,实际利率上行应集中于决议窗口附近,且盈亏平衡保持平稳(引擎面十二个月分解与此一致)
  - 竞争性解释2: 竞争解释A(财政/供给): 储蓄-投资平衡与债券供给放量推升实际利率——若如此,实际利率上行应分布于非决议期并与发行日历相关(引擎无发行日历序列,两解释的窗口预测尚不能区分)
  - 竞争性解释3: 竞争解释B(增长预期上修): 实际利率上行反映增长预期改善——若如此,增长指标改善应与实际利率上行同现;日本与欧元区增长改善与此相容,该解释未被排除
  - 证据: UST_10Y@2026-11-18, TIPS_10Y@2026-11-18, BEI_10Y@2026-11-19, VIX@2026-11-19, DXY@2026-11-20, SPX@2026-11-19, GOLD_F@2026-11-20
- **CON-3**: 历史结构对照:六维等权状态距离最近的三个候选月为二零二五年三月、二零二二年六月与二零二三年十月;三者事后路径分歧明显——二零二五年三月与二零二三年十月候选之后股与金双上涨、美债利率大致走平,而二零二二年六月候选之后三个月股金双下跌、美债利率大幅上行。TOP-N 独立簇事后同向度在多个资产-期限组合仅约六成,候选间事后走向存在分歧,任何单一候选的外推都须降级使用(对照资产=SPX/GOLD_F/DXY/UST_10Y 当前观测)。
  - 依据: 证据: 快照事实行 SPX、GOLD_F、DXY、UST_10Y;三候选事后块(锚月后一/三/六/十二个月,窗口两端实测日随行)见引擎 analog 面;披露语随行:相似不等于因果更非预测,距离分位不是概率。
  - 竞争性解释1: 解释一(距离优先): 距离最近的候选(二零二五年三月)事后表现对外推参考权重最高——若如此,软着陆后风险资产续涨是基准参照
  - 竞争性解释2: 解释二(结构分量优先): 本次锚点的利率维与波动维贡献占主导,更接近二零二二年六月候选的紧缩结构——若如此,未来一个季度金融条件收紧与股债双压风险更高
  - 竞争性解释3: 解释三(方法警示): 六维等权距离对特征选择敏感,信用维贡献为零且部分特征维缺席,排序不稳健——类比只作历史记录引用,不构成预测依据
  - 证据: SPX@2026-11-19, GOLD_F@2026-11-20, DXY@2026-11-20, UST_10Y@2026-11-18
- **机制链 MECH-1**: 全球再通胀→央行转紧→实际利率上行→风险资产承压(主链)
  - E1 冲击环:三地通胀实现值同窗转折——中国 PPI 同比由二零二六年二月的负零点九转升至五月的三点九(十月已至五点七),美国 CPI 同比二点四三四升至四点一六六六,欧元区 HICP 一点九升至三点二;月频分辨率下三地先后未定。 [证据: CN_PPI_YOY@2026-10-31, CPI@2026-10-01, EA_HICP_YOY@2026-10-01]
  - E2 国际传导环(冲击→各国消费通胀):引擎无出口价格、贸易流与通胀分项序列,此环因果为【假设】;区分指标 BRENT_F 同窗月末大涨(二零二六年二月末至五月末上行百分之二十七点零零零六),观测支持能源共同冲击解释而非中国出口链独家传导。 [缺失环: 本引擎无出口价格/贸易流/通胀分项序列,冲击向各国消费通胀的传导为【假设】;能源共同冲击与中国出口链两解释以 BRENT_F 同窗观测对质,当前观测方向与前者一致]
  - E1 政策环:欧央行二零二六年六月十一日决议加息二十五个基点、九月十日再加息二十五个基点,美联储九月十六日决议加息二十五个基点(此前二零二五年十二月十日曾决议降息二十五个基点)——决议日口径可排序:欧央行先于美联储转向;月频宏观数值是统计期值,不得按发布日做事件研究。 [证据: ECB_DFR@2026-09-16, DFEDTARU@2026-11-19]
  - E1 利率结构环:十二个月窗名义上行九十五个基点=实际上行一百零三个基点+盈亏平衡净降八个基点(共同交易日同窗,恒等残差为零)——名义上行全由实际利率贡献,盈亏平衡不是主贡献分量。 [证据: UST_10Y@2026-11-18, TIPS_10Y@2026-11-18, BEI_10Y@2026-11-19]
  - E2 资产定价环:实际利率上行收紧金融条件→风险资产与无息贵金属承压、美元走强——近一月 SPX 与 GOLD_F 回调、DXY 走强、VIX 冲高与 TIPS_10Y 同窗共存(方向与主解释一致,单月窗样本不足以确立因果),整环贴现率传导为【假设】。 [缺失环: 引擎无仓位/流动性/风险溢价分解序列,贴现率传导至资产定价的环内因果为【假设】;同窗方向一致性为 E1 事实,因果归因不可证]
- **机制链 MECH-2**: 日本独立加息周期:通胀回升→持续加息→汇率与股市(背离链)
  - E1 日本通胀回升环:东京 CPI 同比由二零二六年六月的一点六升至九月的二点六九,全国 CPI 由七月的一点九七回升至十月的二点四四。 [证据: JP_CPI_YOY@2026-10-01]
  - E1 政策环:无担保隔夜拆借利率(月均)由二零二五年十月的零点四七七升至二零二六年十月的的一点二二七,月度台阶(零点五五七/零点七二八/零点八四一/零点九七八/一点零四三/一点二二七)显示多次上调——市场月均口径,决议意图归因不可验。 [证据: JP_POLICY_RATE@2026-10-01]
  - E3 汇率-股市环:日本持续加息与日元温和走弱并存(USDJPY 十二个月月末口径上行百分之一点八三五一,未随加息回落——与汇率防御叙事相左、与利差叙事相容),日经近一月与全球股指同幅回调——本国加息与全球风险偏好两归因不可分,此环为【假设】,证伪指标=NIKKEI225。 [证伪指标: NIKKEI225]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **SCN-A**(基准情景)
  - 情景: 假设(非预测):美欧央行对已实现通胀继续紧缩,中国 PPI 维持高位,通胀实现值续升而市场盈亏平衡保持平稳——延续「实际利率上行+金融条件收紧」结构。
  - 资产方向判断: 风险资产(SPX/NIKKEI225)与贵金属(GOLD_F)承压、美元(DXY)偏强、实际利率(TIPS_10Y)趋升——条件式方向判断,假设非预测(置信: 有相关证据) 
  - 敏感变量: TIPS_10Y, EA_HICP_YOY
  - 证伪指标: BEI_10Y 阈值 BEI_10Y 收于 2.8% 上方(较当前 2.16 上升超过 0.6 个百分点)且维持两个月——盈亏平衡趋势上行则本情景的「预期稳定」前提失效
  - 触发条件: 欧央行或美联储再决议加息至少 25bp,且 EA_HICP_YOY 升破 4.5% 或美国最近有效 CPI 同比高于 4.2%(时限 2027-02-20)
- **SCN-B**(反例情景)
  - 情景: 假设(非预测):全球增长放缓主导(美国工业与就业走弱、中国 PPI 回落),美欧央行停止紧缩并转向——切向「增长担忧+宽松预期」结构。
  - 资产方向判断: 风险资产修复、美元走弱、黄金反弹、美债收益率下行——条件式方向判断;历史相似参照(历史记录,相似不等于预测):二零二三年十月候选事后十二个月 SPX +36.04%、UST_10Y -0.60pp、GOLD_F +37.86%(置信: 有历史相似证据) 
  - 敏感变量: UNEMPLOYMENT, CN_PPI_YOY
  - 证伪指标: EA_HICP_YOY 阈值 EA_HICP_YOY 连续两个月不低于 4.5%(当前 4.0)——通胀续升则宽松转向假设失效
  - 触发条件: 美联储决议降息至少 25bp,或美国失业率高于 4.6%(当前 4.1)(时限 2027-02-20)

## 语义审查(席位待唤起)

- **叙事语义未经独立裁决**——定性推断/条件情景在文;常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后方可去掉本披露(章程 §4b/§8)

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

## 证据索引(72 行)

- snapshot_fact:SPX@2026-11-19 → SPX
- snapshot_fact:NDX@2026-11-19 → NDX
- snapshot_fact:RUT@2026-11-19 → RUT
- snapshot_fact:DXY@2026-11-20 → DXY
- snapshot_fact:EURUSD@2026-11-20 → EURUSD
- snapshot_fact:GOLD_F@2026-11-20 → GOLD_F
- snapshot_fact:SILVER_F@2026-11-20 → SILVER_F
- snapshot_fact:BRENT_F@2026-11-20 → BRENT_F
- snapshot_fact:VIX@2026-11-19 → VIX
- snapshot_fact:DAX@2026-11-19 → DAX
- snapshot_fact:CAC40@2026-11-19 → CAC40
- snapshot_fact:USDJPY@2026-11-20 → USDJPY
- snapshot_fact:USDCNY@2026-11-20 → USDCNY
- snapshot_fact:HY_OAS@2026-11-18 → HY_OAS
- snapshot_fact:BB_OAS@2026-11-18 → BB_OAS
- snapshot_fact:B_OAS@2026-11-18 → B_OAS
- snapshot_fact:CCC_OAS@2026-11-18 → CCC_OAS
- snapshot_fact:IG_OAS@2026-11-18 → IG_OAS
- snapshot_fact:UST_2Y@2026-11-18 → UST_2Y
- snapshot_fact:UST_10Y@2026-11-18 → UST_10Y
- snapshot_fact:UST_30Y@2026-11-18 → UST_30Y
- snapshot_fact:TIPS_5Y@2026-11-18 → TIPS_5Y
- snapshot_fact:TIPS_10Y@2026-11-18 → TIPS_10Y
- snapshot_fact:BEI_5Y@2026-11-19 → BEI_5Y
- snapshot_fact:BEI_10Y@2026-11-19 → BEI_10Y
- snapshot_fact:CURVE_2S10S@2026-11-19 → CURVE_2S10S
- snapshot_fact:CPI@2026-10-01 → CPI
- snapshot_fact:CORE_PCE@2026-09-01 → CORE_PCE
- snapshot_fact:UNEMPLOYMENT@2026-10-01 → UNEMPLOYMENT
- snapshot_fact:CORE_CPI@2026-10-01 → CORE_CPI
- snapshot_fact:UST_5Y@2026-11-18 → UST_5Y
- snapshot_fact:INDPRO@2026-10-01 → INDPRO
- snapshot_fact:US_REAL_GDP@2026-07-01 → US_REAL_GDP
- snapshot_fact:SHCOMP@2026-11-19 → SHCOMP
- snapshot_fact:HSI@2026-11-20 → HSI
- snapshot_fact:CN_LPR_1Y@2026-11-20 → CN_LPR_1Y
- snapshot_fact:CN_CPI_YOY@2026-10-31 → CN_CPI_YOY
- snapshot_fact:CN_PPI_YOY@2026-10-31 → CN_PPI_YOY
- snapshot_fact:CN_PMI_MFG@2026-10-01 → CN_PMI_MFG
- snapshot_fact:DFF@2026-11-18 → DFF
- snapshot_fact:DFEDTARU@2026-11-19 → DFEDTARU
- snapshot_fact:NIKKEI225@2026-11-19 → NIKKEI225
- snapshot_fact:JP_CPI_YOY@2026-10-01 → JP_CPI_YOY
- snapshot_fact:ECB_DFR@2026-09-16 → ECB_DFR
- snapshot_fact:ECB_MRO@2026-09-16 → ECB_MRO
- snapshot_fact:EA_HICP_YOY@2026-10-01 → EA_HICP_YOY
- snapshot_fact:JP_POLICY_RATE@2026-10-01 → JP_POLICY_RATE
- s3_envelope:SZCI@2026-11-19 → SZCI
- s3_envelope:CHINEXT@2026-11-19 → CHINEXT
- s3_envelope:HSCEI@2026-11-20 → HSCEI
- s3_envelope:NVDA@2026-11-19 → NVDA
- s3_envelope:AAPL@2026-11-19 → AAPL
- s3_envelope:MSFT@2026-11-19 → MSFT
- s3_envelope:TLT@2026-11-19 → TLT
- s3_envelope:IEF@2026-11-19 → IEF
- s3_envelope:SHY@2026-11-19 → SHY
- s3_envelope:HYG@2026-11-19 → HYG
- s3_envelope:LQD@2026-11-19 → LQD
- s3_envelope:GBPUSD@2026-11-20 → GBPUSD
- s3_envelope:WTI_F@2026-11-20 → WTI_F
- s3_envelope:GLD@2026-11-19 → GLD
- s3_envelope:USO@2026-11-19 → USO
- s3_envelope:EEM@2026-11-19 → EEM
- s3_envelope:EZU@2026-11-19 → EZU
- s3_envelope:FEZ@2026-11-19 → FEZ
- s3_envelope:EWU@2026-11-19 → EWU
- s3_envelope:EWG@2026-11-19 → EWG
- s3_envelope:EWJ@2026-11-19 → EWJ
- s3_envelope:INDA@2026-11-19 → INDA
- s3_envelope:FXI@2026-11-19 → FXI
- s3_envelope:BTC@2026-11-18 → BTC
- s3_envelope:HY_IG_DIFF@2026-11-18 → HY_IG_DIFF

## 注记

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、CORE_PCE、CN_POLICY_OVERNIGHT、CN_OMO_7D、EA_REAL_GDP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY
