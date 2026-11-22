# 一键研究报告(零模型编排 v2.0)
- 问题: 对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整过了多久？
- 运行: 20261122T125710Z @ ca916cdca7b749282e498d8c8f0eac8bf43b7372
- 快照: research_snapshot_20261122_v2 (target 20261122)
- 数据门(gate_a): 46/46 信封步非 OK(DEGRADED)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 9 项 | 对照点锚 3个月前@2026-08-22、最新一期@2026-11-22 | 事后偏移+(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 9 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+95天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-130天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量40不替代窗口归属)(问题未限定范围→quarterly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: UNEMPLOYMENT(缺什么: UNEMPLOYMENT(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+62天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-75天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量119不替代窗口归属)(问题未限定范围→monthly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: INDPRO(缺什么: INDPRO(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+62天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-75天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量120不替代窗口归属)(问题未限定范围→monthly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CPI(缺什么: CPI(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+62天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-75天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量119不替代窗口归属)(问题未限定范围→monthly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_CPI(缺什么: CORE_CPI(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+62天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-75天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量119不替代窗口归属)(问题未限定范围→monthly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2026-11-01..2026-11-30)——任务窗窗口成员/覆盖不满足;任务窗2026-11-01..2026-11-30未满足: 窗内首观测缺席晚于窗起+62天容忍(历史未覆盖任务窗起点);窗内末观测缺席早于窗止-75天容忍(发布滞后外缺口);窗内有效观测 n=0<1(日历期望1×半额;总量119不替代窗口归属)(问题未限定范围→monthly频率族兜底下界(任务范围不得用统一观测数替代);判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
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
- USDCNY = 6.66 cny_per_usd @2026-11-21 [质量:PASS] [来源:snapshot_fact:USDCNY@2026-11-21]
- HY_OAS = 3.52 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:HY_OAS@2026-11-19]
- BB_OAS = 2.1 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:BB_OAS@2026-11-19]
- B_OAS = 3.8 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:B_OAS@2026-11-19]
- CCC_OAS = 13.61 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:CCC_OAS@2026-11-19]
- IG_OAS = 0.94 percentage_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:IG_OAS@2026-11-19]
- UST_2Y = 4.76 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:UST_2Y@2026-11-19]
- UST_10Y = 5.04 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:UST_10Y@2026-11-19]
- UST_30Y = 5.4 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:UST_30Y@2026-11-19]
- TIPS_5Y = 2.64 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:TIPS_5Y@2026-11-19]
- TIPS_10Y = 2.88 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:TIPS_10Y@2026-11-19]
- BEI_5Y = 2.18 percent @2026-11-20 [质量:PASS] [来源:snapshot_fact:BEI_5Y@2026-11-20]
- BEI_10Y = 2.15 percent @2026-11-20 [质量:PASS] [来源:snapshot_fact:BEI_10Y@2026-11-20]
- CURVE_2S10S = 0.29 percentage_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:CURVE_2S10S@2026-11-20]
- CPI = 337.476 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CPI@2026-10-01]
- CORE_PCE = 130.902 index_point_2017 @2026-09-01 [质量:DEGRADED] [来源:snapshot_fact:CORE_PCE@2026-09-01]
- UNEMPLOYMENT = 4.1 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:UNEMPLOYMENT@2026-10-01]
- CORE_CPI = 339.9 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CORE_CPI@2026-10-01]
- UST_5Y = 4.86 percent @2026-11-19 [质量:PASS] [来源:snapshot_fact:UST_5Y@2026-11-19]
- INDPRO = 103.3954 index_point_2017 @2026-10-01 [质量:WARN] [来源:snapshot_fact:INDPRO@2026-10-01]
- US_REAL_GDP = 24611.077 billion_usd @2026-07-01 [质量:DEGRADED] [来源:snapshot_fact:US_REAL_GDP@2026-07-01]
- SHCOMP = 3533.7929 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:SHCOMP@2026-11-20]
- HSI = 22410.8 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:HSI@2026-11-20]
- NIKKEI225 = 56436.65 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-11-20]
- EA_HICP_YOY = 4.0 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:EA_HICP_YOY@2026-10-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **C1-INFL-SYNC**: 美欧通胀环境较 3 个月前同步走高、欧元区幅度更大。欧元区 EA_HICP_YOY 最新读数明显走高、为三地最高水平(数值与观测月见走位对照);美国 CPI 指数水平最新报 337.476(观测 2026-10;3 个月前锚前值 332.813,观测 2026-07;同比派生口径 2026-10 因缺上年同月基期观测不可得,最近有效同比见走位对照),CORE_CPI 报 339.9(观测 2026-10),CORE_PCE 报 130.902(观测 2026-09)。美国 headline 与核心口径同向上行,但读数水平低于欧元区。
  - 竞争性解释1: 若美欧通胀抬升主要源于能源与进口成本的持续传导(弱欧元放大输入压力),则 headline 强于 core 的结构应延续,且同比读数在数月内维持高位。
  - 竞争性解释2: 若抬升主要来自低基数与一次性扰动(统计口径、季节性、能源基数),则未来数月同比应自行回落——近一月 BEI_10Y 走低(月窗 -19bp,2026-10-20→2026-11-19,水平 2.15%@2026-11-20)与市场未定价持续通胀的解读相容。
  - 证据: EA_HICP_YOY@2026-10-01, CPI@2026-10-01, CORE_CPI@2026-10-01, CORE_PCE@2026-09-01
- **C2-GROWTH-STABLE**: 两地增长面大体平稳、并非本期主导变化。US_REAL_GDP(季频水平)最新报 24611.077(观测 2026-07 季),UNEMPLOYMENT 最新报 4.1(观测 2026-10),其 3 个月前锚前值为 4.1(观测 2026-07);INDPRO 报 103.3954(观测 2026-10),3 个月前锚前值为 103.1675(观测 2026-07)。欧元区实际 GDP 同比读数在引擎点值面仅微幅变动(见走位对照),增长端未见方向性转折。
  - 竞争性解释1: 若美国工业生产同比回升(1.25→2.15,引擎派生口径)代表制造业周期回暖,则增长动能在 2026 年三季度后段重新加速,失业率低位与此相容。
  - 竞争性解释2: 若工业读数回升主要为价格与基数效应或单月波动,则增长面应视为走平,实际 GDP 同比的小幅回落(2.19→2.07,引擎派生口径)更代表主趋势。
  - 证据: US_REAL_GDP@2026-07-01, UNEMPLOYMENT@2026-10-01, INDPRO@2026-10-01
- **C3-JP-POLICY**: 日本政策利率处于抬升通道。JP_POLICY_RATE 月均口径最新一期(观测 2026-10)报 1.227%,3 个月前锚前值为 0.978(观测 2026-07)——该序列为无担保隔夜拆借利率月均口径,非政策目标宣布值,宣布目标序列 JP_POLICY_TARGET 在引擎注册表不可得。发布日历实录的最近一次政策决议为 2026-09-18(2026-09-24 生效),至研究截止 2026-11-22 已约两个月,月均口径的最近一级台阶落在 2026-09→2026-10 之交(前值 1.043,现值即最新一期读数),与决议-生效记录相容。
  - 竞争性解释1: 若月均台阶主要反映日本央行面对通胀与汇率压力的连续上调,则后续月均应呈现更高中枢的平台,2026-11 月均(预计 2026-12 初公布)应维持当前水平附近。
  - 竞争性解释2: 若台阶包含决议跨月生效的均值效应(决议后次月月均=新水平整月)与资金面季节性,则单月读数变化不完全等于连续上调,需以决议日历为准——引擎日历 2026-09-18 决议(2026-09-24 生效)后暂无新条目,11 月是否有新决议尚未验证。
  - 证据: JP_POLICY_RATE@2026-10-01
- **机制链 M1-JP-RATE-PATH**: 
  - E1 观察: JP_POLICY_RATE 月均自 2025-11 的 0.478 抬升至 2026-10 的 1.227,近 12 个月政策窗净变动 +67bp(引擎政策窗口径),呈多级台阶(2025-12 0.557、2026-01 0.728、2026-06 0.841、2026-07 0.978、2026-09 1.043、2026-10 1.227)。 [证据: JP_POLICY_RATE@2026-10-01]
  - E2 传导【假设】: 政策利率中枢上移→日元融资成本上升→套息结构边际压缩;本引擎无日本融资成本/套息持仓序列,此环为【假设】。 [缺失环: 本引擎无日本套息持仓/融资成本序列,该环为【假设】,缺环待采;可核环节仅政策利率路径本身(E1)。]
  - E2 资产面观察与对照: USDJPY 最新报 159.71(观测 2026-11-20),NIKKEI225 近一月(2026-10-22→2026-11-20)下跌 10.29%;若加息传导单一成立,应见 USDJPY 走低与股指承压并存——当前 USDJPY 仍处高位而股指已明显回落,组合更接近「风险收缩+利差仍高」的混合态,传导方向证据不单一。 [缺失环: USDJPY 方向受多因子驱动(利差/风险情绪/干预预期),与加息传导的当期一致性无法在引擎面单一归因,该环归【假设】层;区分指标=USDJPY。]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **S1-INFL-STICKY**()
  - 情景: 【假设·非预测】美欧通胀延续当前抬升动能: 至 2027-01,EA_HICP_YOY 同比维持 3.5% 以上,美国 CORE_PCE 同比维持 3.0% 以上,两地政策面维持紧缩偏向(日本月均中枢不低于当前台阶)。
  - 资产方向判断: 在此假设下,实际利率与无风险利率中枢承压上行,利率敏感资产(高估值成长股、黄金)相对走弱,美元指数相对非美货币偏强;此为方向性推演,非幅度预测(置信: 有相关证据) 
  - 敏感变量: EA_HICP_YOY, CORE_PCE
  - 证伪指标: EA_HICP_YOY 阈值 若 2027-01 前发布的 EA_HICP_YOY 同比连续两个月低于 3.0%,通胀粘性假设被证伪
  - 触发条件: 2026-12 或 2027-01 发布的 EA_HICP_YOY 同比 ≥4.0% 且 CORE_PCE 同比 ≥3.1%,同时 TIPS_10Y 高于 3.0%(时限 2027-02-15)
- **S2-INFL-FADE**()
  - 情景: 【假设·非预测】当前美欧通胀抬升以一次性因素(能源基数、汇率进口传导)为主: 至 2027-01,EA_HICP_YOY 同比回落至 3.0% 以下,美国 CORE_PCE 同比回落至 2.8% 以下,市场重新定价宽松。
  - 资产方向判断: 在此假设下,通胀补偿与实际利率双双回落,风险资产修复、黄金重新走强、美元走弱;该方向与近一月观察(实际利率月窗 +11bp 而风险资产回落)相反,属并列反例情景(置信: 纯逻辑推理) 
  - 敏感变量: EA_HICP_YOY, CORE_PCE
  - 证伪指标: EA_HICP_YOY 阈值 若 2026-12 与 2027-01 两月 EA_HICP_YOY 同比均不低于 4.0%,一次性因素假设被证伪
  - 触发条件: EA_HICP_YOY 同比连续两个月回落且最新值 ≤3.4%,同时 BEI_10Y 低于 2.0%(时限 2027-02-15)

## 语义审查(席位待唤起)

- **叙事语义未经独立裁决**——定性推断/条件情景在文;常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后方可去掉本披露(章程 §4b/§8)

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
- [OK |语义✔] S5_compare 命中 39 个指标,compare 仅取注册表序前 2(US_REAL_GDP,UNEMPLOYMENT);其余 INDPRO,CPI,CORE_CPI,CORE_PCE,EA_REAL_GDP_YOY,EA_HICP_YOY,JP_POLICY_RATE,UST_10Y,TIPS_10Y,BEI_10Y,UST_2Y,UST_5Y,UST_30Y,TIPS_5Y,BEI_5Y,CURVE_2S10S,SPX,NDX,RUT,DAX,CAC40,NIKKEI225,HSI,SHCOMP,DXY,EURUSD,USDJPY,USDCNY,GOLD_F,SILVER_F,BRENT_F,HY_OAS,IG_OAS,BB_OAS,B_OAS,CCC_OAS,VIX 以 L1 事实行呈现,如需对比另行单跑
- [OK |语义✔] S6_analog 
- [OK |不适用] S7_mode_gate 
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(63 行)

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
- snapshot_fact:UST_30Y@2026-11-19 → UST_30Y
- snapshot_fact:TIPS_5Y@2026-11-19 → TIPS_5Y
- snapshot_fact:TIPS_10Y@2026-11-19 → TIPS_10Y
- snapshot_fact:BEI_5Y@2026-11-20 → BEI_5Y
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
- s3_envelope:GBPUSD@2026-11-21 → GBPUSD
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
