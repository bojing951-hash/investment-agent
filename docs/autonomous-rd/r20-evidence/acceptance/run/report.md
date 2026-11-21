# 一键研究报告(零模型编排 v2.0)
- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 运行: 20261119T060058Z @ None
- 快照: research_snapshot_20261119 (target 20261119)
- 数据门(gate_a): 33/33 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、中国(CN)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 21 项 | 对照点锚 12个月前@2025-11-19、3个月前@2026-08-19、最新一期@2026-11-19 | 事后偏移+3月/6月/12月(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 8 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_OMO_7D(缺什么: CN_OMO_7D(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内首观测2025-12-08晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-10-30早于窗止-10天容忍(发布滞后外缺口)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_MRO(缺什么: ECB_MRO(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<131(日历期望262×半额;总量48不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_DFR(缺什么: ECB_DFR(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<131(日历期望262×半额;总量69不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_REAL_GDP_YOY(缺什么: JP_REAL_GDP_YOY(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_CPI_YOY(缺什么: JP_CPI_YOY(任务窗2025-11-19..2026-11-19)——任务窗窗口成员/覆盖不满足;任务窗2025-11-19..2026-11-19未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过

## 四层区分

### L1 事实层 available=True
- UST_10Y = 5.1 percent @2026-11-17 [质量:PASS] [来源:snapshot_fact:UST_10Y@2026-11-17]
- TIPS_10Y = 2.89 percent @2026-11-17 [质量:PASS] [来源:snapshot_fact:TIPS_10Y@2026-11-17]
- BEI_10Y = 2.19 percent @2026-11-18 [质量:PASS] [来源:snapshot_fact:BEI_10Y@2026-11-18]
- CPI = 337.476 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CPI@2026-10-01]
- CORE_PCE = 130.902 index_point_2017 @2026-09-01 [质量:DEGRADED] [来源:snapshot_fact:CORE_PCE@2026-09-01]
- UNEMPLOYMENT = 4.1 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:UNEMPLOYMENT@2026-10-01]
- CORE_CPI = 339.9 index_point_1982_84 @2026-10-01 [质量:WARN] [来源:snapshot_fact:CORE_CPI@2026-10-01]
- INDPRO = 103.3954 index_point_2017 @2026-10-01 [质量:WARN] [来源:snapshot_fact:INDPRO@2026-10-01]
- US_REAL_GDP = 24611.077 billion_usd @2026-07-01 [质量:DEGRADED] [来源:snapshot_fact:US_REAL_GDP@2026-07-01]
- CN_LPR_1Y = 3.0 percent @2026-10-20 [质量:WARN] [来源:snapshot_fact:CN_LPR_1Y@2026-10-20]
- CN_PMI_MFG = 49.3 index_point @2026-10-01 [质量:WARN] [来源:snapshot_fact:CN_PMI_MFG@2026-10-01]
- JP_CPI_YOY = 2.16 percent @2026-09-01 [质量:DEGRADED] [来源:snapshot_fact:JP_CPI_YOY@2026-09-01]
- ECB_DFR = 2.5 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_DFR@2026-09-16]
- ECB_MRO = 2.65 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_MRO@2026-09-16]
- EA_HICP_YOY = 4.0 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:EA_HICP_YOY@2026-10-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **C1**: 全球通胀在二零二六年一季度末同步再加速,但幅度与步调分化: 中国生产端价格最早摆脱通缩且幅度最大,美欧消费通胀紧随其后,日本通胀先回落再追赶;随后美欧日央行转向紧缩,而中国政策利率按兵不动。同一全球冲击下,四经济体通胀相位并不一致。
  - 依据: 依据: 引擎月度序列 CN_PPI_YOY、CPI、CORE_PCE、EA_HICP_YOY、JP_CPI_YOY、JP_CPI_TOKYO_YOY 的同比路径,与点值面三时点对照;转折候选面把中国生产价格与美国消费通胀的再加速列为最大变动。
  - 竞争性解释1: 若中国生产端再通胀经出口商品价格与全球供应链传导,则美欧通胀再加速应伴随商品与进口价格上行(引擎证据面无商品/服务分项与进口价格序列,此为缺失环)
  - 竞争性解释2: 若再加速主要由各经济体内需与服务业工资驱动,则中外通胀同月转身只是巧合,贸易传导链条不成立
  - 竞争性解释3: 若共同驱动是能源与大宗商品价格,则贸易品占比高的经济体应先动且幅度更大,四经济体应同向
  - 证据: CPI@2026-10-01, EA_HICP_YOY@2026-10-01, JP_CPI_YOY@2026-09-01
- **C2**: 政策反应函数分化: 美联储在一段降息后重新加息,欧央行连续两拍加息,日本央行全年渐进加息,中国人民银行保持报价利率不变——同一全球通胀冲击下,四大央行反应方向并不同步。
  - 依据: 依据: 政策利率序列 DFEDTARU(目标区间上限,月度路径含降息后的再加息)、ECB_DFR、JP_POLICY_RATE(无担保隔夜拆借月均)、CN_LPR_1Y(全年持平);中国 OMO 七天期利率序列在个别月份出现孤立零值读数,与前后月及 LPR 不变矛盾,按采集伪影披露,不作为政策变化依据。
  - 竞争性解释1: 若反应差异由通胀缺口决定,则通胀再加速越早越高的经济体加息越早越猛(与美欧日先后一致)
  - 竞争性解释2: 若差异由增长与汇率考量驱动,则低增长经济体应更晚更温和地收紧
  - 竞争性解释3: 若中国按兵不动反映消费端通缩风险仍存,则中国 CPI 低位与 PPI 高企并存支持结构性再通胀的解释
  - 证据: ECB_DFR@2026-09-16, JP_POLICY_RATE@2026-10-01, CN_LPR_1Y@2026-10-20
- **C3**: 资产面呈实际利率主导结构: 最近一个月美国十年期名义收益率基本持平,其中实际利率贡献上行、盈亏平衡通胀贡献下行;同期波动率上升,风险资产与黄金同步回调。这与通胀预期驱动的叙事方向相反。
  - 依据: 依据: 引擎共同交易日三利率分解面(UST_10Y 与 TIPS_10Y、BEI_10Y 同窗分解,恒等残差为零)与资产变动面(VIX 上升,股指与黄金回落);复盘锚点状态面上十年期实际利率的扩张期标准化分位处于高位。
  - 竞争性解释1: 若实际利率上行是主导变量,则黄金与长久期资产同跌而盈亏平衡通胀回落(当前观测与此一致)
  - 竞争性解释2: 若回调由增长担忧主导,则盈亏平衡通胀应更深度下行且收益率曲线走牛陡
  - 竞争性解释3: 若回调由仓位与技术面主导,则应与宏观指标变化弱相关且更快修复
  - 证据: UST_10Y@2026-11-17, TIPS_10Y@2026-11-17, BEI_10Y@2026-11-18, VIX@2026-11-18
- **机制链 M1**: 中国生产端再通胀—全球消费通胀再加速—央行再紧缩—实际利率上行—资产定价
  - E1 观察事实: CN_PPI_YOY 同比由 2026-02 的 -0.9 升至 2026-05 的 3.9,并进一步升至 2026-10 的 5.7(引擎月度序列,发布口径);同期 EA_HICP_YOY 由 1.9(2026-02)升至 3.2(2026-05)再至 4.0(2026-10);美国 CPI 同比(引擎转折口径)由 2.434(2026-02)升至 4.1666(2026-05)。三国消费/生产价格在 2026-03 同月转身向上。 [证据: CPI@2026-10-01, EA_HICP_YOY@2026-10-01]
  - E2 传导假设: 中国生产端价格上行经出口商品价格与全球供应链推升美欧商品通胀,是美欧 CPI 再加速的贡献项之一。 [缺失环: 缺失环【假设】: 引擎证据面无美欧 CPI 商品/服务分项、无进口价格序列,无法直接验证传导份额;此环为因果假设而非观察事实,区分指标见 reader_map 传导图。]
  - E1 政策反应(观察事实): 美联储目标区间上限 DFEDTARU 由 2025-08 的 4.5 经三拍降至 2025-12 的 3.75,2026-09 重新升至 4.0;ECB_DFR 于 2026-06-17 与 2026-09-16 两拍各加息 25bp 至 2.50;JP_POLICY_RATE(月均)由 2025-10 的 0.477 连续升至 2026-10 的 1.227;中国 CN_LPR_1Y 全年保持 3.0 不变。 [证据: ECB_DFR@2026-09-16, JP_POLICY_RATE@2026-10-01]
  - E1 利率与资产(观察事实,引擎共同交易日窗 2026-10-16→2026-11-17): UST_10Y 名义 +1bp = TIPS_10Y 实际 +15bp + BEI_10Y 盈亏平衡 -14bp(恒等残差 0)。近一月(引擎资产面): UST_10Y 变动 -0.97%(2026-10-19→2026-11-17),SPX -4.77%、NIKKEI225 -9.08%、GOLD_F -10.39%、DXY +1.76%、VIX +33.19%(18.44→24.56,窗口 2026-10-19→2026-11-18)。 [证据: UST_10Y@2026-11-17, TIPS_10Y@2026-11-17, BEI_10Y@2026-11-18]
  - E3 叙事推演(纯逻辑): 若实际利率在高位继续上行,高估值资产的贴现率压力加深,黄金的机会成本上升;若再通胀消退且央行转向,则反向。此环为条件推演,非预测。 [证伪指标: TIPS_10Y]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **S1**(基准)
  - 情景: 基准情景(延续): 假设全球再通胀延续——中国 PPI 同比维持高位,美欧消费通胀停留在当前水平上方,美欧日央行维持紧缩倾向、美联储不再降息,实际利率高位震荡;此情景下长久期利率债与高估值风险资产承压,黄金区间震荡。
  - 资产方向判断: 美国十年期国债收益率高位震荡偏上行(长久期债偏空);高估值股指承压(偏空);黄金区间震荡(中性偏空)(置信: 有历史相似证据) 结构距离最近的通胀再紧缩可比段 2022-06: 事后 12 个月 SPX +16.34%、UST_10Y +0.93pp(2022-07-01→2023-06-30,引擎类比事后面)——紧缩期股票最终收涨而收益率续升,方向并非单边;当时通胀绝对水平更高,故置信档取有历史相似证据而非更高。
  - 敏感变量: CN_PPI_YOY, EA_HICP_YOY
  - 证伪指标: CPI 阈值 美国 CPI 同比(引擎月度同比口径)连续两个月回落到 3.0 以下
  - 触发条件: EA_HICP_YOY 同比升破 4.5 且 CN_PPI_YOY 同比维持 5.0 以上(再通胀扩散确认)(时限 2027-02-28)
- **S2**(反例)
  - 情景: 反例情景(消退): 假设本轮再通胀主要是暂时性供给扰动,未来两个季度消退——中国 PPI 同比回落、美欧通胀回到目标附近,美联储与欧央行转向再降息,实际利率回落;此情景下风险资产修复、收益率曲线牛陡、黄金重拾上行。
  - 资产方向判断: 股指偏多;长久期利率债偏多(收益率下行);黄金偏多(置信: 有相关证据) 2023-10 与 2025-03 两个类比段的事后 12 个月窗口均为风险资产正回报(SPX +34.63% / +15.90%)、收益率下行或基本持平(UST_10Y -0.49pp / +0.13pp)、黄金大幅上行(GOLD_F +38.33% / +47.73%,窗口随引擎类比事后面)——通胀回落叠加宽松预期的组合与此情景相关,但相关非因果。
  - 敏感变量: CN_PPI_YOY
  - 证伪指标: CN_PPI_YOY 阈值 中国 PPI 同比升破 7.0 并持续上行(供给驱动强化,消退情景失效)
  - 触发条件: DFEDTARU 目标区间上限或 ECB_DFR 任一出现下调(时限 2027-05-31)

## 语义审查(席位已裁)

- 席位裁决: REVISE(档: audit/semantic_review/20261119/VERDICT-20261119T060058Z-01.json)

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
- [OK |语义✔] S5_compare 命中 24 个指标,compare 仅取注册表序前 2(US_REAL_GDP,UNEMPLOYMENT);其余 INDPRO,CPI,CORE_CPI,CORE_PCE,DFEDTARU,DFF,CN_PMI_MFG,CN_CPI_YOY,CN_PPI_YOY,CN_OMO_7D,CN_LPR_1Y,EA_REAL_GDP_YOY,EA_HICP_YOY,ECB_MRO,ECB_DFR,JP_REAL_GDP_YOY,JP_CPI_YOY,JP_CPI_TOKYO_YOY,JP_POLICY_RATE,UST_10Y,TIPS_10Y,BEI_10Y 以 L1 事实行呈现,如需对比另行单跑
- [OK |语义✔] S6_analog 
- [OK |不适用] S7_mode_gate 
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(62 行)

- snapshot_fact:UST_10Y@2026-11-17 → UST_10Y
- snapshot_fact:TIPS_10Y@2026-11-17 → TIPS_10Y
- snapshot_fact:BEI_10Y@2026-11-18 → BEI_10Y
- snapshot_fact:CPI@2026-10-01 → CPI
- snapshot_fact:CORE_PCE@2026-09-01 → CORE_PCE
- snapshot_fact:UNEMPLOYMENT@2026-10-01 → UNEMPLOYMENT
- snapshot_fact:CORE_CPI@2026-10-01 → CORE_CPI
- snapshot_fact:INDPRO@2026-10-01 → INDPRO
- snapshot_fact:US_REAL_GDP@2026-07-01 → US_REAL_GDP
- snapshot_fact:CN_LPR_1Y@2026-10-20 → CN_LPR_1Y
- snapshot_fact:CN_PMI_MFG@2026-10-01 → CN_PMI_MFG
- snapshot_fact:JP_CPI_YOY@2026-09-01 → JP_CPI_YOY
- snapshot_fact:ECB_DFR@2026-09-16 → ECB_DFR
- snapshot_fact:ECB_MRO@2026-09-16 → ECB_MRO
- snapshot_fact:EA_HICP_YOY@2026-10-01 → EA_HICP_YOY
- snapshot_fact:JP_POLICY_RATE@2026-10-01 → JP_POLICY_RATE
- s3_envelope:SPX@2026-11-18 → SPX
- s3_envelope:NDX@2026-11-18 → NDX
- s3_envelope:RUT@2026-11-18 → RUT
- s3_envelope:SHCOMP@2026-11-18 → SHCOMP
- s3_envelope:SZCI@2026-11-18 → SZCI
- s3_envelope:CHINEXT@2026-11-18 → CHINEXT
- s3_envelope:HSI@2026-11-19 → HSI
- s3_envelope:HSCEI@2026-11-19 → HSCEI
- s3_envelope:NIKKEI225@2026-11-18 → NIKKEI225
- s3_envelope:DAX@2026-11-17 → DAX
- s3_envelope:CAC40@2026-11-17 → CAC40
- s3_envelope:VIX@2026-11-18 → VIX
- s3_envelope:NVDA@2026-11-18 → NVDA
- s3_envelope:AAPL@2026-11-18 → AAPL
- s3_envelope:MSFT@2026-11-18 → MSFT
- s3_envelope:TLT@2026-11-18 → TLT
- s3_envelope:IEF@2026-11-18 → IEF
- s3_envelope:SHY@2026-11-18 → SHY
- s3_envelope:HYG@2026-11-18 → HYG
- s3_envelope:LQD@2026-11-18 → LQD
- s3_envelope:DXY@2026-11-18 → DXY
- s3_envelope:EURUSD@2026-11-18 → EURUSD
- s3_envelope:GBPUSD@2026-11-18 → GBPUSD
- s3_envelope:USDJPY@2026-11-18 → USDJPY
- s3_envelope:USDCNY@2026-11-18 → USDCNY
- s3_envelope:GOLD_F@2026-11-18 → GOLD_F
- s3_envelope:SILVER_F@2026-11-18 → SILVER_F
- s3_envelope:WTI_F@2026-11-18 → WTI_F
- s3_envelope:BRENT_F@2026-11-18 → BRENT_F
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
- s3_envelope:HY_OAS@2026-11-17 → HY_OAS
- s3_envelope:BB_OAS@2026-11-17 → BB_OAS
- s3_envelope:B_OAS@2026-11-17 → B_OAS
- s3_envelope:CCC_OAS@2026-11-17 → CCC_OAS
- s3_envelope:IG_OAS@2026-11-17 → IG_OAS
- s3_envelope:HY_IG_DIFF@2026-11-17 → HY_IG_DIFF

## 注记

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、CORE_PCE、CN_OMO_7D、EA_REAL_GDP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY、JP_CPI_YOY
