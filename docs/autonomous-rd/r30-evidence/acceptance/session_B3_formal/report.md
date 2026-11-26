# 一键研究报告(零模型编排 v2.0)
- 问题: 对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整过了多久？
- 运行: 20261121T151204Z @ 59dcc096fff5138429105214bbd24ccd3ce003bb
- 快照: research_snapshot_20261121 (target 20261121)
- 数据门(gate_a): 42/42 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 9 项 | 对照点锚 3个月前@2026-08-21、最新一期@2026-11-21 | 事后偏移+(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 9 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+95天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-130天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量39不替代窗口归属)(问题未限定范围→quarterly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: UNEMPLOYMENT(缺什么: UNEMPLOYMENT(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+62天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-75天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量118不替代窗口归属)(问题未限定范围→monthly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: INDPRO(缺什么: INDPRO(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+62天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-75天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量119不替代窗口归属)(问题未限定范围→monthly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CPI(缺什么: CPI(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+62天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-75天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量118不替代窗口归属)(问题未限定范围→monthly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_CPI(缺什么: CORE_CPI(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+62天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-75天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量118不替代窗口归属)(问题未限定范围→monthly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+62天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-75天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量118不替代窗口归属)(问题未限定范围→monthly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+95天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-130天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量123不替代窗口归属)(问题未限定范围→quarterly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_HICP_YOY(缺什么: EA_HICP_YOY(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+62天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-75天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量358不替代窗口归属)(问题未限定范围→monthly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_POLICY_RATE(缺什么: JP_POLICY_RATE(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+62天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-75天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量496不替代窗口归属)(问题未限定范围→monthly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过

## 四层区分

### L1 事实层 available=True
- SPX = 6910.39 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:SPX@2026-11-20]
- NDX = 25028.98 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:NDX@2026-11-20]
- RUT = 2581.79 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:RUT@2026-11-20]
- DXY = 103.81 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:DXY@2026-11-20]
- EURUSD = 1.1 usd_per_eur @2026-11-20 [质量:PASS] [来源:snapshot_fact:EURUSD@2026-11-20]
- GOLD_F = 3515.4 usd_per_oz @2026-11-20 [质量:PASS] [来源:snapshot_fact:GOLD_F@2026-11-20]
- SILVER_F = 41.03 usd_per_oz @2026-11-20 [质量:PASS] [来源:snapshot_fact:SILVER_F@2026-11-20]
- BRENT_F = 92.57 usd_per_barrel @2026-11-20 [质量:PASS] [来源:snapshot_fact:BRENT_F@2026-11-20]
- VIX = 35.89 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:VIX@2026-11-20]
- DAX = 24802.78 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:DAX@2026-11-20]
- CAC40 = 7927.75 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:CAC40@2026-11-20]
- USDJPY = 159.71 jpy_per_usd @2026-11-20 [质量:PASS] [来源:snapshot_fact:USDJPY@2026-11-20]
- USDCNY = 6.68 cny_per_usd @2026-11-21 [质量:PASS] [来源:snapshot_fact:USDCNY@2026-11-21]
- HY_OAS = 3.52 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:HY_OAS@2026-11-19]
- BB_OAS = 2.1 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:BB_OAS@2026-11-19]
- B_OAS = 3.8 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:B_OAS@2026-11-19]
- CCC_OAS = 13.61 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:CCC_OAS@2026-11-19]
- IG_OAS = 0.94 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:IG_OAS@2026-11-19]
- UST_2Y = 4.76 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:UST_2Y@2026-11-19]
- UST_10Y = 5.04 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:UST_10Y@2026-11-19]
- BEI_10Y = 2.15 percent @2026-11-20 [质量:PASS] [来源:snapshot_fact:BEI_10Y@2026-11-20]
- CURVE_2S10S = 0.29 percentage_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:CURVE_2S10S@2026-11-20]
- CPI = 337.476 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CPI@2026-10-01]
- CORE_PCE = 130.902 index_point_2017 @2026-09-01 [质量:DEGRADED] [来源:snapshot_fact:CORE_PCE@2026-09-01]
- UNEMPLOYMENT = 4.1 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:UNEMPLOYMENT@2026-10-01]
- CORE_CPI = 339.9 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CORE_CPI@2026-10-01]
- UST_5Y = 4.86 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:UST_5Y@2026-11-19]
- INDPRO = 103.3954 index_point_2017 @2026-10-01 [质量:WARN] [来源:snapshot_fact:INDPRO@2026-10-01]
- US_REAL_GDP = 24611.077 billion_usd @2026-07-01 [质量:DEGRADED] [来源:snapshot_fact:US_REAL_GDP@2026-07-01]
- SHCOMP = 3533.79 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:SHCOMP@2026-11-20]
- HSI = 22410.8 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:HSI@2026-11-20]
- NIKKEI225 = 56436.65 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-11-20]
- EA_HICP_YOY = 4.0 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:EA_HICP_YOY@2026-10-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **CON-1**: 相比3个月前(锚日 2026-08-21,锚格取发布日≤锚日的最新观测),美国与欧元区的增长环境大体平稳、通胀环境双双趋紧,且欧元区消费通胀的上行更快: 增长面,美国失业率(UNEMPLOYMENT)持平于 4.1,欧元区实际GDP同比温和回升、美国实际GDP同比温和放缓(读数与观测月见走位面回贴);通胀面,欧元区 HICP 同比最新读数较三个月前明显上行(两读数逐位见走位面 anchor_echo 回贴),美国核心PCE与CPI同比(引擎派生口径)中枢同样上移,但升幅小于欧元区。增长动能口径互有分歧(美国GDP同比微降而工业生产同比回升),不构成单一方向的加速或减速。
  - 依据: 证据面: 引擎三时点锚格(本问两锚: 3个月前@2026-08-21/最新一期@2026-11-21)与转折候选面;美国 CPI 与 CORE_CPI 最新锚格(2026-10 观测)缺去年同月基期,同比不可得以最近有效同比(2026-09 观测)代述——数值与观测月逐位见 reader_map 各地区走位与 anchor_echo;欧元区 HICP 同比为引擎原序列口径(非派生)。
  - 竞争性解释1: 供给/能源与基数驱动解释: 欧美通胀三个月上行主要由能源与基数等瞬态因素驱动,后续读数将自行回落——将观察到 BRENT_F 回落领先、BEI_10Y 保持温和而 HICP 同比随之降档。
  - 竞争性解释2: 需求黏性解释: 通胀上行由工资-物价与服务黏性驱动,具持续性,政策须维持紧缩——将观察到 CORE_PCE 同比持续高位、失业率维持低位而通胀不下行。
  - 竞争性解释3: 美欧非同步解释: 欧元区上行快于美国主要是两地瞬态因素构成不同(欧元区能源与基数敞口更大)的叠加,而非全球同步的需求过热——将观察到后续月份美欧通胀读数相关性减弱、各自独立波动。
  - 证据: EA_HICP_YOY@2026-10-01, UNEMPLOYMENT@2026-10-01, CORE_PCE@2026-09-01, CPI@2026-10-01
- **CON-2**: 日本端货币政策近一年处于渐进收紧通道: 日本无担保隔夜拆借利率月均(JP_POLICY_RATE)最新观测为 1.227(2026-10 月均),较三个月前锚继续抬升;引擎一年窗政策路径事件面示六次月度变动,最近一次可观测变动落在 2026-10 月均(前月读数与路径明细见走位面与转折面回贴),距研究截止约三至七周(月频分辨率,自统计窗末约三周、自观测月起点约七周)。两口径边界须随行: 其一,该序列为市场利率月均,不等于政策目标宣布值,政策目标口径序列 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道),目标水平=数据不可得;其二,2026-11 月均尚未发布(BOJ 次月初公布),11 月内是否有新调整在现有数据面不可判。
  - 依据: 证据面: 引擎点值锚格(JP_POLICY_RATE 两锚)与 policy_window_path 一年窗事件面(窗=研究截止−12个月..研究截止;events 的 date=序列值变更日=生效日口径,月均序列无决议日面,决议日/生效日/统计窗终点分记);月频证据只能支持『最近变动落在 2026-10 月均』这一粒度,具体决议日不可判,先后排序主张按纪律写明分辨率。
  - 竞争性解释1: 政策意图驱动解释: 月均逐月抬升反映 BOJ 连续小幅上调政策目标或引导市场利率上移的紧缩意图,与美欧通胀上行后的全球再定价方向一致——将观察到后续月均继续阶梯抬升且与美欧政策事件簇同期。
  - 竞争性解释2: 技术性漂移解释: 月均在目标区间内的逐月上行属市场资金面与操作技术性漂移(月末/季度因素),政策目标并未逐月调整——将观察到月均抬升不呈阶梯状、且与决议日历无对应关系(本引擎无决议日面,此环暂不可证)。
  - 竞争性解释3: 滞后反应解释: 月均抬升是日本通胀读数回升后的滞后反应而非领先信号——将观察到日本通胀同比先于月均抬升见顶。
  - 证据: JP_POLICY_RATE@2026-10-01
- **CON-3**: 对照期内的市场面与上述宏观走向同向: 近一月风险资产与黄金深跌、波动率翻倍、美元走强——SPX -10.92%、DAX -3.28%、NIKKEI225 -12.67%、GOLD_F -15.29%、VIX +115.17%、DXY +1.99%(月窗 2026-10-21→2026-11-20),UST_10Y 5.04 于同窗高位小幅回落(窗口 2026-10-21→2026-11-19);长端与曲线维持高位(UST_2Y 4.76、CURVE_2S10S 0.29、BEI_10Y 2.15),信用利差未显著走阔(HY_OAS 3.52、IG_OAS 0.94)——市场定价的是高利率与高波动组合而非信用事件,单月窗口不足以在『利率/贴现率驱动』与『增长担忧驱动』之间裁决。
  - 依据: 证据面: 引擎资产月窗复算(asset_moves 行,窗口 2026-10-21→2026-11-20,UST_10Y 行至 2026-11-19,两端实测日随行),快照事实与信用利差对照;TIPS_10Y 序列不可得,实际利率分量无法直接验证,名义利率归因在引擎面不可裁决。
  - 竞争性解释1: 贴现率驱动解释: 股指与黄金同跌由高利率与波动冲击的估值压缩驱动——将观察到 VIX 与利率同向、HY_OAS 温和而 GOLD_F 弹性最大。
  - 竞争性解释2: 增长担忧驱动解释: 回撤由增长与盈利预期下修驱动——将观察到 HY_OAS 走阔领先于股指、利率因避险反而下行。
  - 证据: SPX@2026-11-20, DAX@2026-11-20, NIKKEI225@2026-11-20, GOLD_F@2026-11-20, VIX@2026-11-20, DXY@2026-11-20, UST_10Y@2026-11-19, HY_OAS@2026-11-19
- **机制链 CH-1**: 美欧通胀三个月趋紧→政策与预期重定价(日本渐进抬升)→利率高位/曲线平→风险资产与黄金承压
  - E1 通胀端: 欧元区 HICP 同比 2.9(2026-07 观测)→4.0(2026-10 观测),美国 CPI 派生同比 3.30(2026-07)→最近有效 3.72(2026-09 观测,2026-10 格缺基期),核心PCE派生同比 3.04(2026-06)→3.12(2026-09);更早的转折候选面示美欧通胀曾于 2026-02→2026-05 同窗大幅上移(美国 CPI 派生 2.434→4.1666、欧元区 1.9→3.2)。 [证据: EA_HICP_YOY@2026-10-01, CPI@2026-10-01, CORE_PCE@2026-09-01]
  - E2 政策端: 日本以无担保隔夜拆借月均口径渐进抬升,一年窗自 0.557(2025-12 观测)升至 1.227(2026-10 观测),2025-12/2026-01/2026-06/2026-07/2026-09/2026-10 六次月度变动,净抬升 67bp(引擎 policy_window_path,月均≠目标宣布值);美欧政策决议面不在本问计划指标内,本 run 证据索引无 ECB/Fed 政策行,该环仅以利率市场水平间接支持。 [缺失环: 缺失环【假设】: 『通胀上移→美欧央行再紧缩』为本引擎本 run 无政策决议行下的假设——证据索引无 ECB_DFR/DFEDTARU 等政策序列(检索范围=本 run 证据索引 59 行),只有日本月均口径可 E1 直证;美欧端的政策反应环标【假设】,证伪指标=UST_2Y(若美欧政策预期未紧缩,短端应回落而非维持 4.76 高位)。]
  - E1 利率市场端: UST_10Y 5.04、UST_2Y 4.76(2026-11-19),CURVE_2S10S 0.29、BEI_10Y 2.15(2026-11-20)——长端高位、曲线偏平、盈亏平衡温和,名义上行主要由非通胀预期分量承载的说法与该组水平一致。 [证据: UST_10Y@2026-11-19, UST_2Y@2026-11-19, BEI_10Y@2026-11-20, CURVE_2S10S@2026-11-20]
  - E3 资产端: 近一月 SPX -10.92%、DAX -3.28%、NIKKEI225 -12.67%、GOLD_F -15.29%、VIX +115.17%、DXY +1.99%(月窗 2026-10-21→2026-11-20)——高利率与高波动组合压制长久期风险资产与非孳息黄金、支撑美元。 [证伪指标: VIX]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **S1-通胀趋紧延续**(基准(主解释延续))
  - 情景: 假设(非预测): 欧元区通胀上行与美国核心通胀黏性延续,政策面整体维持紧缩倾向(日本月均口径继续阶梯抬升),增长温和降温但不衰退,高波动逐步消化而非扩散为信用事件。
  - 资产方向判断: 风险资产(SPX/DAX/NIKKEI225)与黄金(GOLD_F)承压、VIX 中枢维持高位、DXY 偏强、长端利率高位(UST_10Y 维持 5 附近);现金与短久期相对占优。(置信: 有相关证据) 
  - 敏感变量: EA_HICP_YOY, CORE_PCE
  - 证伪指标: EA_HICP_YOY 阈值 EA_HICP_YOY 同比自 2026-10 的 4.0 回落至 3.0 下方并连续两个月维持(通胀趋紧延续的主通道被推翻)
  - 触发条件: 2026-12 或 2027-01 发布的 HICP 同比仍 ≥3.8 且 JP_POLICY_RATE 月均口径在 2026-11 或 2026-12 再度抬升(高于 1.227)(时限 2027-02-21)
- **S2-瞬态回落修复**(反例(供给/基数瞬态))
  - 情景: 假设(非预测): 三个月通胀上行主要为能源与基数等瞬态因素,后续读数回落,政策转向观望(日本月均走平),风险资产修复、波动回落。
  - 资产方向判断: 风险资产修复反弹、VIX 自 35.89 高位回落、长端利率小幅下行、黄金反弹;美元偏强缓和。(置信: 纯逻辑推理) 
  - 敏感变量: EA_HICP_YOY, VIX
  - 证伪指标: EA_HICP_YOY 阈值 HICP 同比连续两个月维持 4.0 或以上未回落(瞬态回落假设被推翻)
  - 触发条件: HICP 同比连续两个月回落至 3.4 下方且 VIX 月末回落至 25 下方(时限 2027-02-21)

## 语义审查(席位待唤起)

- **叙事语义未经独立裁决**——定性推断/条件情景在文;常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后方可去掉本披露(章程 §4b/§8)

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2022-06 | 0.888098 | 0.0 | volatility 37.2%、valuation 29.0% |
| 2 | 2025-03 | 0.967636 | 4.1096 | volatility 73.7%、rates 15.7% |
| 3 | 2020-10 | 0.979606 | 8.2192 | rates 78.6%、valuation 9.9% |
| 4 | 2023-10 | 1.343214 | 52.0548 | volatility 74.6%、valuation 14.1% |
| 5 | 2019-10 | 1.614863 | 94.5205 | volatility 49.0%、rates 22.6% |

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
- [OK |语义✔] S3_overview_EA 
- [OK |语义✔] S3_overview_JP 
- [OK |语义✔] S3_changes 
- [OK |语义✔] S4_history_US_REAL_GDP 
- [OK |语义✔] S4_history_UNEMPLOYMENT 
- [OK |语义✔] S4_history_INDPRO 
- [OK |语义✔] S4_history_CPI 
- [OK |语义✔] S4_history_CORE_CPI 
- [OK |语义✔] S4_history_CORE_PCE 
- [OK |语义✔] S4_history_EA_REAL_GDP_YOY 
- [OK |语义✔] S4_history_EA_HICP_YOY 
- [OK |语义✔] S4_history_JP_POLICY_RATE 
- [OK |语义✔] S4_history_UST_10Y 
- [FAIL|语义✗] S4_history_TIPS_10Y 
- [OK |语义✔] S4_history_BEI_10Y 
- [OK |语义✔] S4_history_UST_2Y 
- [OK |语义✔] S4_history_UST_5Y 
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
- [OK |语义✔] S5_compare 命中 36 个指标,compare 仅取注册表序前 2(US_REAL_GDP,UNEMPLOYMENT);其余 INDPRO,CPI,CORE_CPI,CORE_PCE,EA_REAL_GDP_YOY,EA_HICP_YOY,JP_POLICY_RATE,UST_10Y,TIPS_10Y,BEI_10Y,UST_2Y,UST_5Y,CURVE_2S10S,SPX,NDX,RUT,DAX,CAC40,NIKKEI225,HSI,SHCOMP,DXY,EURUSD,USDJPY,USDCNY,GOLD_F,SILVER_F,BRENT_F,HY_OAS,IG_OAS,BB_OAS,B_OAS,CCC_OAS,VIX 以 L1 事实行呈现,如需对比另行单跑
- [OK |语义✔] S6_analog 
- [OK |不适用] S7_mode_gate 
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(59 行)

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
- snapshot_fact:USDCNY@2026-11-21 → USDCNY
- snapshot_fact:HY_OAS@2026-11-19 → HY_OAS
- snapshot_fact:BB_OAS@2026-11-19 → BB_OAS
- snapshot_fact:B_OAS@2026-11-19 → B_OAS
- snapshot_fact:CCC_OAS@2026-11-19 → CCC_OAS
- snapshot_fact:IG_OAS@2026-11-19 → IG_OAS
- snapshot_fact:UST_2Y@2026-11-19 → UST_2Y
- snapshot_fact:UST_10Y@2026-11-19 → UST_10Y
- snapshot_fact:BEI_10Y@2026-11-20 → BEI_10Y
- snapshot_fact:CURVE_2S10S@2026-11-20 → CURVE_2S10S
- snapshot_fact:CPI@2026-10-01 → CPI
- snapshot_fact:CORE_PCE@2026-09-01 → CORE_PCE
- snapshot_fact:UNEMPLOYMENT@2026-10-01 → UNEMPLOYMENT
- snapshot_fact:CORE_CPI@2026-10-01 → CORE_CPI
- snapshot_fact:UST_5Y@2026-11-19 → UST_5Y
- snapshot_fact:INDPRO@2026-10-01 → INDPRO
- snapshot_fact:US_REAL_GDP@2026-07-01 → US_REAL_GDP
- snapshot_fact:SHCOMP@2026-11-20 → SHCOMP
- snapshot_fact:HSI@2026-11-20 → HSI
- snapshot_fact:NIKKEI225@2026-11-20 → NIKKEI225
- snapshot_fact:EA_HICP_YOY@2026-10-01 → EA_HICP_YOY
- snapshot_fact:JP_POLICY_RATE@2026-10-01 → JP_POLICY_RATE
- s3_envelope:SZCI@2026-11-20 → SZCI
- s3_envelope:CHINEXT@2026-11-20 → CHINEXT
- s3_envelope:HSCEI@2026-11-20 → HSCEI
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
- s3_envelope:BTC@2026-11-20 → BTC
- s3_envelope:HY_IG_DIFF@2026-11-19 → HY_IG_DIFF

## 注记

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、UNEMPLOYMENT、INDPRO、CPI、CORE_CPI、CORE_PCE、EA_REAL_GDP_YOY、EA_HICP_YOY、JP_POLICY_RATE
