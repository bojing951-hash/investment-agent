# 一键研究报告(零模型编排 v2.0)
- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 运行: 20261121T005508Z @ b7cc80b
- 快照: research_snapshot_20261121 (target 20261121)
- 数据门(gate_a): 61/61 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、中国(CN)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 22 项 | 对照点锚 12个月前@2025-11-21、3个月前@2026-08-21、最新一期@2026-11-21 | 事后偏移+3月/6月/12月(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 8 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_POLICY_OVERNIGHT(缺什么: CN_POLICY_OVERNIGHT(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-11-02晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内有效观测 n=15<130(日历期望261×半额;总量15不替代窗口归属)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_OMO_7D(缺什么: CN_OMO_7D(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2025-12-08晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-10-30早于窗止-10天容忍(发布滞后外缺口)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_MRO(缺什么: ECB_MRO(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<130(日历期望261×半额;总量48不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_DFR(缺什么: ECB_DFR(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<130(日历期望261×半额;总量69不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_REAL_GDP_YOY(缺什么: JP_REAL_GDP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过

## 四层区分

### L1 事实层 available=True
- SPX = 7018.53 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:SPX@2026-11-20]
- NDX = 25495.15 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:NDX@2026-11-20]
- RUT = 2606.02 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:RUT@2026-11-20]
- DXY = 103.82 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:DXY@2026-11-20]
- EURUSD = 1.1 usd_per_eur @2026-11-20 [质量:PASS] [来源:snapshot_fact:EURUSD@2026-11-20]
- GOLD_F = 3527.6 usd_per_oz @2026-11-20 [质量:PASS] [来源:snapshot_fact:GOLD_F@2026-11-20]
- SILVER_F = 40.83 usd_per_oz @2026-11-20 [质量:PASS] [来源:snapshot_fact:SILVER_F@2026-11-20]
- BRENT_F = 89.18 usd_per_barrel @2026-11-20 [质量:PASS] [来源:snapshot_fact:BRENT_F@2026-11-20]
- VIX = 32.04 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:VIX@2026-11-20]
- DAX = 24802.78 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:DAX@2026-11-20]
- CAC40 = 7927.75 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:CAC40@2026-11-20]
- USDJPY = 158.76 jpy_per_usd @2026-11-20 [质量:PASS] [来源:snapshot_fact:USDJPY@2026-11-20]
- USDCNY = 6.66 cny_per_usd @2026-11-20 [质量:PASS] [来源:snapshot_fact:USDCNY@2026-11-20]
- HY_OAS = 3.52 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:HY_OAS@2026-11-19]
- BB_OAS = 2.1 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:BB_OAS@2026-11-19]
- B_OAS = 3.8 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:B_OAS@2026-11-19]
- CCC_OAS = 13.61 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:CCC_OAS@2026-11-19]
- IG_OAS = 0.94 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:IG_OAS@2026-11-19]
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
- SHCOMP = 3533.79 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:SHCOMP@2026-11-20]
- HSI = 22841.62 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:HSI@2026-11-19]
- CN_LPR_1Y = 3.0 percent @2026-11-20 [质量:WARN] [来源:snapshot_fact:CN_LPR_1Y@2026-11-20]
- CN_PMI_MFG = 49.3 index_point @2026-10-01 [质量:WARN] [来源:snapshot_fact:CN_PMI_MFG@2026-10-01]
- NIKKEI225 = 56436.65 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-11-20]
- JP_CPI_YOY = 2.44 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_CPI_YOY@2026-10-01]
- ECB_DFR = 2.5 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_DFR@2026-09-16]
- ECB_MRO = 2.65 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_MRO@2026-09-16]
- EA_HICP_YOY = 4.0 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:EA_HICP_YOY@2026-10-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **CONTRA-1**: 2026年春季全球通胀再加速是过去一年最重要的共同冲击:美国 CPI 与欧元区 EA_HICP_YOY 的同比在2026-02至2026-05同窗显著抬升(具体前后值见转折表与锚值回贴),中国生产者价格 CN_PPI_YOY 同窗由负转正且至2026-10升幅为四地最大;美欧中三者转折同月(月频观测,先后未定)。驱动归因存在数据同样容纳的并列解释(见 competing_explanations),引擎面无法单声一种叙事。
  - 依据: 证据锚(当前快照水平): CPI 337.476@2026-10-01、CORE_CPI 339.9@2026-10-01、CORE_PCE 130.902@2026-09-01、BRENT_F 89.18@2026-11-20;欧元区 EA_HICP_YOY 的最新同比读数(见走位锚值回贴,2026-10已突破四)为四地最高。headline 与核心的裂口、核心 PCE 的上行、商品价格的双向剧烈波动并存,分别支持不同解释。
  - 竞争性解释1: 输入型解释: 若商品与生产者价格沿贸易链外溢,则 headline 将先于核心上行、裂口走阔——与当前 headline 高于核心约1.15个百分点的现况一致(【假设】:引擎无分国进口价格/贸易链序列,外溢环不可直接验证,证伪指标 BRENT_F——若 BRENT_F 持续回落而 headline 同比仍居高,输入型解释被削弱)
  - 竞争性解释2: 内生型解释: 若服务/工资等内生动力主导,则核心通胀将同步上行——与 CORE_PCE 同比持续上行的走势一致;此解释下央行紧缩对通胀的抑制会更慢(证伪指标 CORE_PCE——若其同比回落至2.5%以下,内生粘性解释被削弱)
  - 竞争性解释3: 基数/统计效应解释: 若2025年低基数与统计口径调整机械推高同比,则6-12个月内同比将自行回落、无需政策起效(证伪指标 CPI——若2027年春同比仍高于3.5%,基数解释被否定)
  - 证据: CPI@2026-10-01, CORE_CPI@2026-10-01, CORE_PCE@2026-09-01, EA_HICP_YOY@2026-10-01, BRENT_F@2026-11-20
- **CONTRA-2**: 美债十年期名义利率过去十二个月大幅上行,且引擎恒等分解显示上行几乎全部由实际利率贡献、盈亏平衡通胀反而小幅回落——这与『通胀预期失控推升名义利率』的直觉叙事相反(该叙事被分解直接排除);但实际利率上行的来源(政策紧缩 vs 期限溢价/财政供给 vs 增长预期上修)不可由分解本身区分(12个月窗分解数值见 reader_map 传导链与 rates_decomposition 回贴)。
  - 依据: 证据锚(当前快照水平): UST_10Y 5.07@2026-11-18、TIPS_10Y 2.88@2026-11-18、BEI_10Y 2.16@2026-11-19、CURVE_2S10S 0.28@2026-11-19;近30日窗口名义与盈亏平衡回落、实际利率回升,与12个月窗方向一致。
  - 竞争性解释1: 政策紧缩驱动: 若再收紧定价主导,则前端敏感、曲线走平——与过去一年曲线走平的方向一致,但曲线形状非充分识别(【推断】非定论)
  - 竞争性解释2: 期限溢价/财政供给驱动: 若债券供给压力抬升期限溢价,则长端上行与政策预期无关,曲线应走陡——与现况相反,此解释当前证据较弱但不可排除(【假设】:引擎无期限溢价分解序列,证伪指标 UST_30Y——若长端在政策持稳期继续独自上行,该解释获支持)
  - 竞争性解释3: 增长预期上修驱动: 若市场定价潜在增速上移,实际利率自然上行——但美国增长面在减速,解释力弱,列为完备性并列(证伪指标 US_REAL_GDP——若其同比重新加速至2.5%以上需重估)
  - 证据: UST_10Y@2026-11-18, TIPS_10Y@2026-11-18, BEI_10Y@2026-11-19, CURVE_2S10S@2026-11-19
- **CONTRA-3**: 近1个月风险资产急跌而信用利差月内近乎不动: SPX 月窗-9.52%(7018.53@2026-11-20)、VIX 32.04(月窗+92.09%)、GOLD_F 月窗-15.0%、DXY 月窗+2.0%,同期 HY_OAS 月内仅+0.08pp(3.52@2026-11-19)、IG_OAS 月内+0.00pp——股票与黄金同月大幅走低而投资级信用利差纹丝不动,这一组合的机制归属存在并列解释;最近一周 HY_OAS +0.29pp、CCC_OAS +0.45pp 开始追赶,证据面在演化中。
  - 依据: 证据锚: SPX/NIKKEI225/GOLD_F/VIX/DXY/HY_OAS 快照与月窗(2026-10-21至2026-11-20)及周窗(2026-11-13起)变化;HY_OAS 年内+0.71pp、CCC_OAS 年内+4.76pp(2025-12-31基准)显示信用压力全年渐进累积。
  - 竞争性解释1: 利率/流动性挤压: 若实际利率高位与美元流动性收紧是主因,则估值压缩+黄金与股票同向+美元偏强的组合成立——月内信用利差近零与此一致(证伪指标 HY_OAS——若其持续升破4.0pp,利率单一渠道解释被削弱)
  - 竞争性解释2: 增长/信用恶化: 若市场开始定价增长转弱,则信用利差应后来居上——最近一周 HY_OAS 的追赶与此一致,但单周不足定论(证伪指标 HY_OAS 与 CCC_OAS 同向持续走阔)
  - 竞争性解释3: 波动冲击/去杠杆: 若 VIX 单月接近翻倍触发机械性减仓,则跨资产相关性趋同、利差滞后反应为技术性而非基本面——若 VIX 回落后利差随即收窄,支持本解释(证伪指标 VIX——若 VIX 回落至20以下而 HY_OAS 仍居4.0pp上方,去杠杆解释被削弱)
  - 证据: SPX@2026-11-20, NIKKEI225@2026-11-20, GOLD_F@2026-11-20, VIX@2026-11-20, DXY@2026-11-20, HY_OAS@2026-11-19, IG_OAS@2026-11-19
- **CONTRA-4**: 主要央行政策路径先分化后趋同:美联储2025-12-10降息后,于2026-09-16与欧央行同周重新加息(利率终点回到起点,前后值见锚值回贴);欧央行2026-06-11与2026-09-10两度加息;日央行 JP_POLICY_RATE(月均口径)全年渐进上调;中国在 CN_LPR_1Y 与七天期逆回购利率上全年按兵。全球货币政策在2026年由分化转向协同再收紧,中国是唯一未跟随加息的主要经济体。
  - 依据: 证据锚(当前快照水平): ECB_DFR 2.5@2026-09-16、JP_POLICY_RATE 1.227@2026-10-01、CN_LPR_1Y 3.0@2026-11-20、CN_PMI_MFG 49.3@2026-10-01(中国增长弱修复背景)。政策决议日为日频事件,2026-09-10(欧央行)与2026-09-16(美联储)同处一周,按同一全球政策事件簇计数。
  - 竞争性解释1: 共同外部冲击解释: 若全球输入型通胀是共同触发器,则协同再收紧是各自对本国 headline 破位的同向反应(时序上通胀转折在前、政策转折在后,方向一致但月频-日频混合下不可严格确立因果)
  - 竞争性解释2: 各央行独立反应函数解释: 若各自锚定国内口径(美核心PCE、欧HICP、日东京CPI的读数都在抬升),则协同只是各自独立决策的巧合重叠,同周加息不构成协同证据
  - 竞争性解释3: 中国独立周期解释: 若中国按本国低通胀(CN_CPI_YOY 最新0.7)与弱修复(CN_PMI_MFG 49.3荣枯线下)决策,则其不加息是理性独立——这本身就是『协同』表象的反例,提示所谓全球收紧并不存在统一机制
  - 证据: ECB_DFR@2026-09-16, ECB_MRO@2026-09-16, JP_POLICY_RATE@2026-10-01, CN_LPR_1Y@2026-11-20, CN_PMI_MFG@2026-10-01
- **机制链 MC-POLICY-RATES-EQUITY**: 
  - E2 通胀再加速触发央行再收紧:政策动作(美联储2025-12-10降息、2026-09-16加息;欧央行2026-06-11与2026-09-10各加息25bp)与通胀序列(CPI/EA_HICP_YOY)两端均可观测,时序方向一致(通胀转折2026-05在前、政策转折2026-06至09在后);但『反应函数』环节引擎无对应序列,此环为【假设】 [缺失环: 引擎无央行反应函数/决策规则序列,通胀→政策的因果方向为【假设】,仅时序与幅度旁证]
  - E1 政策利率→债券名义/实际利率:名义=实际+盈亏平衡为恒等式,可确定性复算——UST_10Y 12个月+95bp=TIPS_10Y +103bp+BEI_10Y -8bp(引擎共同交易日同窗分解,恒等残差0.0),名义上行全部由实际利率贡献;近30日窗口名义-8bp=实际+8bp+盈亏平衡-16bp [证据: UST_10Y@2026-11-18, TIPS_10Y@2026-11-18, BEI_10Y@2026-11-19]
  - E2 实际利率上行→风险资产估值压缩与波动放大:端点可观测(近1月 SPX -9.52%、VIX 月窗+92.09%、GOLD_F -15.0%、NIKKEI225 -12.67%),但『贴现率→估值』传导环无引擎序列,此环为【假设】;黄金与股票同月同向的组合更提示流动性/保证金渠道同时在场 [缺失环: 估值与贴现率之间无引擎序列可刻画,传导方向为【假设】;信用利差月内近零(HY_OAS 月内+0.08pp)约束了纯信用渠道的解释空间]
  - E1 资产联动事实面(可直接验证):近1月(2026-10-21至2026-11-20)SPX -9.52%、NIKKEI225 -12.67%、DAX -3.28%、SHCOMP -4.83%、GOLD_F -15.0%、DXY +2.0%、VIX +92.09%;UST_10Y 月内-1.17%(避险方向);HY_OAS 月内+0.08pp、最近一周+0.29pp [证据: SPX@2026-11-20, NIKKEI225@2026-11-20, GOLD_F@2026-11-20, VIX@2026-11-20, DXY@2026-11-20, DAX@2026-11-20, SHCOMP@2026-11-20]
  - E3 期限溢价/财政供给替代叙事:长端实际利率上行或主要反映债券供给与期限溢价而非政策预期——纯叙事环,无引擎序列可验;若成立,曲线应走陡而非走平 [证伪指标: CURVE_2S10S]
- **机制链 MC-CN-PPI-GLOBAL**: 
  - E2 中国 PPI→全球商品价格:两端序列在(CN_PPI_YOY 2026-02的-0.9至2026-05的+3.9至2026-10的+5.7;BRENT_F 89.18、年内+46.56%但11月内-24.19%),但跨国商品/中间品贸易传导环引擎无序列,此环为【假设】;中国是本轮再通胀中变幅最大的震动源(Δ+4.8pp)但月频下与美欧转折先后未定 [缺失环: 引擎无跨国投入产出/商品贸易流序列,中国 PPI 至全球商品价格的因果方向为【假设】]
  - E2 输入通胀→美欧 headline 超核心:裂口本身可确定性计算(CPI 最近有效同比3.72@2026-09 vs CORE_CPI 2.57@2026-09,裂口约1.15个百分点),但『进口成分主导』的归因环为【假设】;核心 PCE 同期上行提示内生成分同时在场 [缺失环: 引擎无 CPI 分项(能源/进口品权重)序列,headline-核心裂口的成因归属为【假设】]
  - E2 他国通胀→央行反应与前端利率定价:前端利率端点可观测(UST_2Y 4.8@2026-11-18),政策动作可观测(欧央行2026-06/09加息、美联储2026-09加息),但『输入通胀→政策』反应环为【假设】 [缺失环: 政策反应函数环节为【假设】,见 MC-POLICY-RATES-EQUITY 第1环]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **SCN-TIGHTER-LONGER**()
  - 情景: 假设(非预测):通胀粘性使主要央行维持再收紧甚至加码,实际利率维持高位,增长继续温和减速——『紧得更久』基准情景
  - 资产方向判断: 风险资产估值持续受压:SPX 偏弱、VIX 中枢抬升、DXY 偏强、黄金在实际利率与美元双高压下承压;信用利差渐进走阔(置信: 有相关证据) 
  - 敏感变量: TIPS_10Y, VIX
  - 证伪指标: VIX 阈值 VIX 收盘回落至20以下并持续10个交易日(高波动压制解除=本情景失效)
  - 触发条件: TIPS_10Y 维持2.8%上方,且下一次 CPI 同比读数(最近有效3.72@2026-09)仍高于3.5%(时限 2027-02-19)
- **SCN-INFLATION-FADE**()
  - 情景: 假设(非预测):通胀随基数效应与商品回落(11月 BRENT_F 月内-24.19%)自行降温,央行暂停紧缩,风险资产与黄金修复——『通胀自熄』反例情景
  - 资产方向判断: SPX 与 GOLD_F 修复性反弹、VIX 回落、实际利率下行——方向与历史相似段2023-10的事后12个月(SPX +36.04%、GOLD_F +37.86%,锚月末至12个月后月末口径)一致;注意该段相似性由波动维单维主导(巧合警示),外推力弱(置信: 有历史相似证据) 
  - 敏感变量: BEI_10Y, HY_OAS
  - 证伪指标: BEI_10Y 阈值 BEI_10Y 跌破1.8%且 SPX 仍低于7500(通胀预期已下行而资产未修复=本情景传导假设失效)
  - 触发条件: CPI 同比(最近有效3.72@2026-09)回落至3.0%以下,且 DFEDTARU 维持4.0不再上调(时限 2027-05-21)

## 语义审查(席位待唤起)

- **叙事语义未经独立裁决**——定性推断/条件情景在文;常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后方可去掉本披露(章程 §4b/§8)

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2025-03 | 0.802571 | 0.0 | volatility 52.4%、rates 34.2% |
| 2 | 2022-06 | 0.841938 | 1.3699 | rates 45.2%、valuation 29.7% |
| 3 | 2023-10 | 1.113819 | 28.7671 | volatility 64.7%、valuation 19.0% |
| 4 | 2021-02 | 1.248144 | 56.1644 | rates 77.0%、volatility 13.3% |
| 5 | 2020-01 | 1.316398 | 68.4932 | rates 73.0%、inflation 12.6% |

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

- snapshot_fact:SPX@2026-11-20 → SPX
- snapshot_fact:NDX@2026-11-20 → NDX
- snapshot_fact:RUT@2026-11-20 → RUT
- snapshot_fact:DXY@2026-11-20 → DXY
- snapshot_fact:EURUSD@2026-11-20 → EURUSD
- snapshot_fact:GOLD_F@2026-11-20 → GOLD_F
- snapshot_fact:SILVER_F@2026-11-20 → SILVER_F
- snapshot_fact:BRENT_F@2026-11-20 → BRENT_F
- snapshot_fact:VIX@2026-11-20 → VIX
- snapshot_fact:DAX@2026-11-20 → DAX
- snapshot_fact:CAC40@2026-11-20 → CAC40
- snapshot_fact:USDJPY@2026-11-20 → USDJPY
- snapshot_fact:USDCNY@2026-11-20 → USDCNY
- snapshot_fact:HY_OAS@2026-11-19 → HY_OAS
- snapshot_fact:BB_OAS@2026-11-19 → BB_OAS
- snapshot_fact:B_OAS@2026-11-19 → B_OAS
- snapshot_fact:CCC_OAS@2026-11-19 → CCC_OAS
- snapshot_fact:IG_OAS@2026-11-19 → IG_OAS
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
- snapshot_fact:SHCOMP@2026-11-20 → SHCOMP
- snapshot_fact:HSI@2026-11-19 → HSI
- snapshot_fact:CN_LPR_1Y@2026-11-20 → CN_LPR_1Y
- snapshot_fact:CN_PMI_MFG@2026-10-01 → CN_PMI_MFG
- snapshot_fact:NIKKEI225@2026-11-20 → NIKKEI225
- snapshot_fact:JP_CPI_YOY@2026-10-01 → JP_CPI_YOY
- snapshot_fact:ECB_DFR@2026-09-16 → ECB_DFR
- snapshot_fact:ECB_MRO@2026-09-16 → ECB_MRO
- snapshot_fact:EA_HICP_YOY@2026-10-01 → EA_HICP_YOY
- snapshot_fact:JP_POLICY_RATE@2026-10-01 → JP_POLICY_RATE
- s3_envelope:SZCI@2026-11-20 → SZCI
- s3_envelope:CHINEXT@2026-11-20 → CHINEXT
- s3_envelope:HSCEI@2026-11-19 → HSCEI
- s3_envelope:NVDA@2026-11-20 → NVDA
- s3_envelope:AAPL@2026-11-20 → AAPL
- s3_envelope:MSFT@2026-11-20 → MSFT
- s3_envelope:TLT@2026-11-20 → TLT
- s3_envelope:IEF@2026-11-20 → IEF
- s3_envelope:SHY@2026-11-20 → SHY
- s3_envelope:HYG@2026-11-20 → HYG
- s3_envelope:LQD@2026-11-20 → LQD
- s3_envelope:GBPUSD@2026-11-20 → GBPUSD
- s3_envelope:WTI_F@2026-11-20 → WTI_F
- s3_envelope:GLD@2026-11-20 → GLD
- s3_envelope:USO@2026-11-20 → USO
- s3_envelope:EEM@2026-11-20 → EEM
- s3_envelope:EZU@2026-11-20 → EZU
- s3_envelope:FEZ@2026-11-20 → FEZ
- s3_envelope:EWU@2026-11-20 → EWU
- s3_envelope:EWG@2026-11-20 → EWG
- s3_envelope:EWJ@2026-11-20 → EWJ
- s3_envelope:INDA@2026-11-20 → INDA
- s3_envelope:FXI@2026-11-20 → FXI
- s3_envelope:BTC@2026-11-19 → BTC
- s3_envelope:HY_IG_DIFF@2026-11-19 → HY_IG_DIFF

## 注记

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、CORE_PCE、CN_POLICY_OVERNIGHT、CN_OMO_7D、EA_REAL_GDP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY
