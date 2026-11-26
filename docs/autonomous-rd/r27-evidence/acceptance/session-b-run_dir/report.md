# 一键研究报告(零模型编排 v2.0)
- 问题: 对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整过了多久？
- 运行: 20261121T013826Z @ b7cc80b
- 快照: research_snapshot_20261121 (target 20261121)
- 数据门(gate_a): 46/46 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
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
- NIKKEI225 = 56436.65 index_point @2026-11-20 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-11-20]
- EA_HICP_YOY = 4.0 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:EA_HICP_YOY@2026-10-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **C1**: 通胀边际变化的跨大区分化和区内结构分化: 双锚对照窗内,欧元区 EA_HICP_YOY 同比明显跳升,美国 CORE_PCE 同比仅温和走高;美国整体 CPI 读数明显高于其核心 CORE_CPI(最近有效同比口径)——两大经济体通胀方向同向(回升)但幅度分化,欧元区边际升温更大,且美国整体与核心读数本身背离。
  - 依据: 引擎双锚点值面: EA_HICP_YOY 与 CORE_PCE 的两锚值、CPI 与 CORE_CPI 的最近有效同比与缺基期标注;口径=锚格发布纪律(发布日不晚于锚日的最新观测)。
  - 竞争性解释1: 欧元区特有成本冲击(能源/进口价格)推升整体 HICP,美国所受冲击较小,幅度差反映冲击暴露与传导差异【假设】
  - 竞争性解释2: 全球共同通胀因子在两地均存在,幅度差由指数口径与权重结构(HICP vs PCE/CPI)及去年同期基数差异放大,底层动能差异小于读数差异【假设】
  - 竞争性解释3: 美国整体读数高于核心的结构背离由食品能源等波动项驱动,若此,核心通胀的温和走势更能代表底层动能,欧元区跳升中亦可能含类似波动项成分【假设】
  - 证据: EA_HICP_YOY@2026-10-01, CORE_PCE@2026-09-01, CPI@2026-10-01, CORE_CPI@2026-10-01
- **C2**: 美国增长面信号分化: UNEMPLOYMENT 双锚持平、INDPRO 同比回暖、US_REAL_GDP 同比微降——就业平稳、产出修复与 GDP 读数微降并存,单季微降不足以判定增长环境转弱,也不足以断言加速。
  - 依据: 引擎双锚点值面三指标锚值与同比派生;US_REAL_GDP 为季频最新修订口径(事后回顾,非当时首发值)。
  - 竞争性解释1: 增长实质稳健,GDP 单季波动为常态噪音,就业与工业读数更可靠地指示平稳环境【假设】
  - 竞争性解释2: 就业为滞后指标,工业产出回暖是修复先行信号,后续就业与 GDP 或跟随走高【假设】
  - 竞争性解释3: GDP 微降是真实放缓的早期信号,工业读数受部门性/政策性因素(如制造回流)扰动而夸大回暖【假设】
  - 证据: UNEMPLOYMENT@2026-10-01, INDPRO@2026-10-01, US_REAL_GDP@2026-07-01
- **C3**: 日本政策利率的月均口径仍在紧缩路径: JP_POLICY_RATE 月均序列一年窗净抬升、最近一次登记变动落在最新可得月格;月均序列无法区分政策决议与市场利率漂移,决议日与生效日在引擎面缺席,距上次调整的时长只能按登记月口径给出上下界,不冒充精确决议时点。
  - 依据: 引擎 JP_POLICY_RATE 序列与政策路径事件面(policy_window_path);JP_POLICY_TARGET 宣布值口径注册表缺席;月均口径注记随行。
  - 竞争性解释1: 台阶式月均抬升反映政策目标利率的多次上调(渐进紧缩周期),月均是决议的市场映像【假设】
  - 竞争性解释2: 部分格变动是市场利率围绕既定目标的波动与流动性季节性,并非每次格变动都对应决议【假设】
  - 竞争性解释3: 混合情形: 上半年若干格变动对应决议,近月变动部分为决议、部分为市场漂移,决议日数据缺席使两者不可分【假设】
  - 证据: JP_POLICY_RATE@2026-10-01
- **机制链 M1**: 
  - E1 EA_HICP_YOY 同比自 2026-07 的 2.9 连续三期走高至 2026-10 的 4.0(净变动 +1.1 个百分点);同期 EA_REAL_GDP_YOY 仅自 1.19(2026Q2)微升至 1.28(2026Q3)——通胀上行发生在增长低位、温和修复的背景上 [证据: EA_HICP_YOY@2026-10-01]
  - E2 通胀跳升→欧央行政策反应收紧→欧元区利率与汇率重定价→风险资产贴现率上行;观测端 EURUSD 自 2026-11-05 的 1.1235 回落至 2026-11-20 的 1.0973 [缺失环: 引擎无欧央行决议日/政策预期/欧债收益率曲线序列(BUND 序列因 FRED_KEY 缺席采集),中间环为【假设】;仅两端(EA_HICP_YOY 数据与 EURUSD 汇率)引擎可验]
  - E3 若成本端(能源/进口)驱动主导且增长低位,央行反应或偏温和,风险资产受通胀的直接冲击有限——此环为纯叙事【假设】,以 EA_HICP_YOY 后续路径为证伪观察 [证伪指标: EA_HICP_YOY]
- **机制链 M2**: 
  - E1 JP_POLICY_RATE 月均自 2026-07 的 0.978 升至 2026-10 的 1.227(月均抬升 0.249 个百分点,=+24.9bp);一年窗净 +67bp,最近登记变动 2026-10 格(1.043→1.227,引擎事件增量 18bp) [证据: JP_POLICY_RATE@2026-10-01]
  - E2 政策紧缩→日元融资套息头寸平仓→日股回调与日元升值联动;观测面 USDJPY 处 157-160 高位(2026-11-20 收 158.76)、NIKKEI225 一个月窗回落 12.67%(2026-10-21→2026-11-20) [缺失环: 引擎无套息交易持仓/资金流序列与 BOJ 决议日数据,平仓机制环为【假设】;仅两端(政策利率序列与 USDJPY/NIKKEI225 行情)引擎可验]
  - E3 若全球风险因子(波动率抬升)主导日股波动,日本政策路径的解释冗余——纯叙事【假设】,以 NIKKEI225 与 VIX 的联动结构为证伪观察 [证伪指标: NIKKEI225]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **SCN-A**()
  - 情景: 假设(非预测): 欧元区通胀动能延续——EA_HICP_YOY 同比在未来两期(至 2027-01)维持在接近当前读数的水平(约 4% 一带)或更高;美国核心通胀(CORE_PCE 同比)维持 3% 上方。此为基准情景,与反例情景 SCN-B 并列呈现。
  - 资产方向判断: EURUSD 走强方向(欧央行紧缩预期主导利差与贴现率渠道;条件式判断,非预测)(置信: 纯逻辑推理) 
  - 敏感变量: EA_HICP_YOY, EURUSD
  - 证伪指标: EA_HICP_YOY 阈值 EA_HICP_YOY 同比在 2027-01 与 2027-02 两期读数均回落至 3.0 以下,则通胀延续假设被证伪
  - 触发条件: 月度 HICP 同比 2026-11 或 2026-12 任一期读数不低于 3.8(维持在接近当前 4.0 的水平)(时限 2027-01-31)
- **SCN-B**()
  - 情景: 假设(非预测): 欧元区通胀为成本端暂时性冲击——EA_HICP_YOY 同比自当前读数逐步回落至 3% 下方,欧央行无需进一步紧缩。此为反例情景,与基准情景 SCN-A 并列呈现。
  - 资产方向判断: EURUSD 走弱方向(欧元区利差支撑消退,美元相对走强;条件式判断,非预测)(置信: 纯逻辑推理) 
  - 敏感变量: EA_HICP_YOY, VIX
  - 证伪指标: EA_HICP_YOY 阈值 EA_HICP_YOY 同比升破 4.5 且下一期仍不低于 4.5,则回落假设被证伪
  - 触发条件: 月度 HICP 同比 2026-11 或 2026-12 任一期读数回落至 3.2 或更低(自 4.0 回落至少 0.8 个百分点)(时限 2027-01-31)

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
- snapshot_fact:NIKKEI225@2026-11-20 → NIKKEI225
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

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、UNEMPLOYMENT、INDPRO、CPI、CORE_CPI、CORE_PCE、EA_REAL_GDP_YOY、EA_HICP_YOY、JP_POLICY_RATE
