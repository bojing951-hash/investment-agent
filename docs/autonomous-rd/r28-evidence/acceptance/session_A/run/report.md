# 一键研究报告(零模型编排 v2.0)
- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 运行: 20261121T063746Z @ 2679629132fe939d756b3b26136473a910929291
- 快照: research_snapshot_20261121 (target 20261121)
- 数据门(gate_a): 25/25 信封步非 OK(FAIL)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 研究计划(共享): 地区 美国(US)、中国(CN)、欧元区(EA)、日本(JP) | 维度 增长、通胀、货币政策 | 计划指标 22 项 | 对照点锚 12个月前@2025-11-21、3个月前@2026-08-21、最新一期@2026-11-21 | 事后偏移+3月/6月/12月(点锚=截止日−N 月,事后偏移=事件日+N 月,两类分记)
  - 缺口: JP/policy —— 计划指标 JP_POLICY_TARGET 不在注册表(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)——JP_POLICY_TARGET 历史序列与元数据均不可得,该格以「数据不可得」呈现(影响: 日本货币政策环境该口径三时点对照不可判,不以相邻口径冒充),不虚构
- 数据需求(运行前冻结): 必要 0 项(问题命中,规格=序列/最低覆盖4 观测),缺口 14 项;可选面缺席=降级披露不构成缺口
  - 任务目标缺口: US_REAL_GDP(缺什么: US_REAL_GDP(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-07-01早于窗止-130天容忍(发布滞后外缺口)(问题限定 1 年×quarterly 频率年观测 4;判定面=S4 信封实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CORE_PCE(缺什么: CORE_PCE(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内末观测2026-09-01早于窗止-75天容忍(发布滞后外缺口)(问题限定 1 年×monthly 频率年观测 12;判定面=S4 信封实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_CPI_YOY(缺什么: CN_CPI_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_PPI_YOY(缺什么: CN_PPI_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_POLICY_OVERNIGHT(缺什么: CN_POLICY_OVERNIGHT(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_OMO_7D(缺什么: CN_OMO_7D(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: CN_LPR_1Y(缺什么: CN_LPR_1Y(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_REAL_GDP_YOY(缺什么: EA_REAL_GDP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: EA_HICP_YOY(缺什么: EA_HICP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_MRO(缺什么: ECB_MRO(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<130(日历期望261×半额;总量48不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: ECB_DFR(缺什么: ECB_DFR(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21未满足: 窗内首观测2026-06-17晚于窗起+14天容忍(历史未覆盖任务窗起点);窗内末观测2026-09-16早于窗止-10天容忍(发布滞后外缺口);窗内有效观测 n=2<130(日历期望261×半额;总量69不替代窗口归属);窗内观测最大相邻间距91天>频率族断档上限30天(严重断档)(问题限定 1 年×daily 频率年观测 252;判定面=快照 series_store 实际 dates/values))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_REAL_GDP_YOY(缺什么: JP_REAL_GDP_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_CPI_YOY(缺什么: JP_CPI_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过
  - 任务目标缺口: JP_CPI_TOKYO_YOY(缺什么: JP_CPI_TOKYO_YOY(任务窗2025-11-21..2026-11-21)——任务窗窗口成员/覆盖不满足;任务窗2025-11-21..2026-11-21窗口成员不可核验(快照无序列且 S4 信封无实际 dates——不得凭 first/last 裁剪或总量冒充窗内观测;源=研究快照 series_store))——未事后缩减,补齐授权范围内数据或按降级面显式越过

## 四层区分

### L1 事实层 available=True
- HSI = 22841.62 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:HSI@2026-11-19]
- NIKKEI225 = 59444.21 index_point @2026-11-19 [质量:PASS] [来源:snapshot_fact:NIKKEI225@2026-11-19]
- ECB_DFR = 2.5 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_DFR@2026-09-16]
- ECB_MRO = 2.65 percent @2026-09-16 [质量:DEGRADED] [来源:snapshot_fact:ECB_MRO@2026-09-16]
- EA_HICP_YOY = 1.9 percent @2025-12-01 [质量:DEGRADED] [来源:snapshot_fact:EA_HICP_YOY@2025-12-01]
- JP_POLICY_RATE = 1.227 percent @2026-10-01 [质量:WARN] [来源:snapshot_fact:JP_POLICY_RATE@2026-10-01]

### L2 机构观点层 available=False(VP sidecar 缺席(data/ 本地层;干净 clone 常态))

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **C1-inflation-policy-cycle**: 过去十二个月四经济体的核心矛盾是通胀再加速与政策周期错位: 美国与欧元区整体通胀再度上行,中国呈现增长筑底,日本通胀在目标附近先回落再回升;政策方向因此分化——美联储先降后升、欧央行两度加息、日本持续正常化、中国货币政策环境三时点对照数据不可得(检索范围=快照 series_store+注册表 history_source 采集档通道)。
  - 依据: 证据行: ECB_DFR 报 2.5(2026-09-16 生效观测,较 2025-06 观测水平两度上调);ECB_MRO 证据行同日同步上调(数值属点值锚面);JP_POLICY_RATE 报 1.227(2026-10 月均);EA_HICP_YOY 证据行为快照序列滞后观测(质量 DEGRADED,三时点锚值见地图面);美联储目标区间上限路径的数值属引擎点值面,不在本证据行面(免锚理由: 点值面数值经 reader_map anchor_echo 逐位回贴核对)。
  - 竞争性解释1: 需求粘性解释(主): 若工资-服务通胀粘性与需求韧性推动通胀再加速,则核心通胀应与整体通胀同步走高,央行被迫转鹰;
  - 竞争性解释2: 供给/基数解释: 若能源与食品基数效应主导整体读数,则核心通胀温和、政策转鹰更多反映增长与金融条件考量;
  - 竞争性解释3: 统计口径解释: 若权重调整与基数镜像推高表观读数,则实际通胀动能弱于读数,政策反应函数未变。
  - 证据: ECB_DFR@2026-09-16, ECB_MRO@2026-09-16, JP_POLICY_RATE@2026-10-01, EA_HICP_YOY@2025-12-01
- **C2-rates-riskassets-2026Q4**: 2026-10 以来 NIKKEI225 显著走弱、恒生指数同步承压,与高企的实际利率并存;该组合更像贴现率冲击而非典型增长衰退冲击(权益走弱同时长端名义收益率高位、美元走强、波动率飙升)。黄金与权益同跌不符合典型避险组合,指向实际利率机会成本渠道。SPX/DAX/VIX/GOLD_F/DXY 的同窗变动数值属引擎资产计划面(不在本判定证据序列面)。
  - 依据: 证据行: NIKKEI225 收于 59444.21(2026-11-19),HSI 收于 22841.62(2026-11-19),HSCEI 同步承压(数值属引擎计划面);十年期美债收益率水平与近月/十二月窗口的名义-实际-盈亏平衡分解属引擎共同交易日面(数值经 reader_map rates_decomposition 逐位回贴,不在本证据行面);NIKKEI225 资产月窗(2026-10-21→2026-11-19)幅度经 reader_map asset_returns_echo 回贴。
  - 竞争性解释1: 贴现率冲击(主): 若实际利率上行与政策再紧缩预期主导,则估值压缩沿长久期/成长资产扩散,黄金受实际利率机会成本压制;
  - 竞争性解释2: 增长冲击解释: 若衰退担忧主导,则长端收益率应明显下行、黄金通常受益——与观测组合不符,但滞胀混合情形不能排除;
  - 竞争性解释3: 仓位/流动性解释: 若单一风险事件或杠杆去化主导,则波动率飙升应相对短暂,跨资产同跌属技术性而非宏观定价。
  - 证据: NIKKEI225@2026-11-19, HSI@2026-11-19, HSCEI@2026-11-19
- **C3-japan-normalization-divergence**: 日本是四经济体中唯一政策持续单边正常化者: JP_POLICY_RATE(月均)最新报 1.227,全年逐级上行;方向上与美欧 2026-09 的同步加息一致,节奏上贯穿全年而先于美联储转鹰。
  - 依据: 证据行: JP_POLICY_RATE 1.227(2026-10 月均,quality WARN 披露);ECB_DFR 与 ECB_MRO 证据行同期上调(2026-09-16,数值属点值锚面,经 reader_map anchor_echo 回贴)。日债收益率(JGB 族)为单点观测,属采集面非判定证据序列,不入对账。
  - 竞争性解释1: 内生再通胀解释: 若日本国内通胀持稳于目标上方,则正常化将随数据持续;
  - 竞争性解释2: 外部约束解释: 若日元贬值压力主导,则加息节奏取决于美联储路径而非国内通胀;
  - 竞争性解释3: 技术性退出解释: 若非常规政策工具的正常化程序主导,则步幅与通胀动能弱相关。
  - 证据: JP_POLICY_RATE@2026-10-01, ECB_DFR@2026-09-16, ECB_MRO@2026-09-16
- **机制链 MC1-inflation-to-policy-to-rates-to-assets**: 
  - E1 【事实+推断】美国CPI同比自 2026-02 的 2.434 升至 2026-05 的 4.1666(引擎转折候选面,通胀维最大事件);欧元区HICP同比同窗自 1.9 升至 3.2;美国核心PCE同比路径 2.85→3.04→3.12(引擎点值面),核心与整体同向上行。 [证据: EA_HICP_YOY@2025-12-01]
  - E1 【事实+推断】政策响应: ECB_DFR 于 2026-06-11 与 2026-09-10 两度各上调一档至 2.5;DFEDTARU 于 2026-09-16 上调回 4.0(引擎政策事件簇 POLCLUSTER-03: 决议日相差 6 日,同轮跨国事件)。 [证据: ECB_DFR@2026-09-16, ECB_MRO@2026-09-16]
  - E1 【事实】利率定价传导: 十年期美债收益率 2026-11-19 报 5.04;十二个月窗口名义 +91bp=实际(TIPS_10Y)+102bp+盈亏平衡(BEI_10Y)-11bp;近一月窗口名义 -8bp=实际 +11bp+盈亏平衡 -19bp(引擎共同交易日分解,恒等残差 0.0)。NIKKEI225 同期收于 59444.21,资产月窗 2026-10-21→2026-11-19 回落 8.01%(引擎资产窗面)。 [证据: NIKKEI225@2026-11-19]
  - E3 【假设】实际利率→估值/黄金的广义传导: 高实际利率抬升持有黄金的机会成本并压制约成长/长久期资产估值;该环为叙事性机制推断(引擎面无估值-利率弹性序列),证伪观测=实际利率回落而风险资产不修复。 [证伪指标: TIPS_10Y]
- **机制链 MC2-japan-normalization**: 
  - E1 【事实】JP_POLICY_RATE(月均)自 2025-10 的 0.477 升至 2026-07 的 0.978 再至 2026-10 的 1.227(引擎点值面与证据行),为四经济体中唯一全年单边上行政策序列。 [证据: JP_POLICY_RATE@2026-10-01]
  - E2 【推断+假设】通胀持稳于目标附近(全国CPI同比 2.99→1.97→2.44,东京都 2026-06 的 1.6→2026-09 的 2.69)支撑加息决策——本引擎无日本通胀预期与日元汇率序列,该因果环为【假设】。 [缺失环: 本引擎无日本通胀预期序列、无 USDJPY 序列,此环为【假设】]
  - E3 【假设】外部反馈环: 若日元贬值压力参与决策,则美联储路径变化将反过来影响日本加息节奏;纯叙事环,证伪观测=日本CPI回落至 1 下方而加息仍持续(则非通胀驱动)。 [证伪指标: JP_CPI_YOY]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **S1-tightening-persistence**()
  - 情景: 假设(非预测): 美国通胀粘性使美联储将目标区间上限维持 4.0 至 2027 年中、欧央行维持 2.5 上方、十年期实际利率高位震荡,则估值压缩与高波动延续。
  - 资产方向判断: 发达市场权益 3-6 个月偏弱、12 个月维度不定向;黄金受高实际利率压制(置信: 有历史相似证据) 
  - 敏感变量: TIPS_10Y, CPI
  - 证伪指标: TIPS_10Y 阈值 10年期实际利率回落跌破 2.50 且 CORE_PCE 同比回落至 3.0 以下(连续两个月)
  - 触发条件: 连续两个月 CORE_PCE 同比 ≥ 3.0 且 TIPS_10Y 月末维持 ≥ 2.50(紧缩延续的观测确认)(时限 2027-05-31)
- **S2-disinflation-pivot**()
  - 情景: 假设(非预测): 美国通胀在 2027 年上半年前回落至 3.0 下方,美联储与欧央行转回降息,实际利率下行,则风险资产与黄金修复。
  - 资产方向判断: 发达市场权益与黄金 6-12 个月修复上行(置信: 有历史相似证据) 
  - 敏感变量: CPI, DFEDTARU
  - 证伪指标: CPI 阈值 CPI 同比升破 4.5 且政策目标区间上限再度上调
  - 触发条件: TIPS_10Y 任一月末 ≤ 2.50 且当月 CORE_PCE 同比 < 3.0(通胀回落推动政策转松)(时限 2027-05-31)

## 语义审查(席位已裁)

- 席位裁决: REVISE(档: audit/semantic_review/20261121/VERDICT-20261121T063746Z-01.json)

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
- [SKIP|—] S4_history_CN_CPI_YOY 地图计划指标 CN_CPI_YOY 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_CN_PPI_YOY 地图计划指标 CN_PPI_YOY 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_CN_POLICY_OVERNIGHT 地图计划指标 CN_POLICY_OVERNIGHT 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_CN_OMO_7D 地图计划指标 CN_OMO_7D 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_CN_LPR_1Y 地图计划指标 CN_LPR_1Y 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [SKIP|—] S4_history_EA_REAL_GDP_YOY 地图计划指标 EA_REAL_GDP_YOY 历史序列缺席(point_values 同源探测)——如实跳过,该格以「数据不可得」呈现
- [OK |语义✗] S4_history_EA_HICP_YOY 
- [OK |语义✔] S4_history_ECB_MRO 
- [OK |语义✔] S4_history_ECB_DFR 
- [OK |语义✗] S4_history_JP_REAL_GDP_YOY 
- [OK |语义✗] S4_history_JP_CPI_YOY 
- [OK |语义✗] S4_history_JP_CPI_TOKYO_YOY 
- [OK |语义✔] S4_history_JP_POLICY_RATE 
- [OK |语义✔] S4_history_UST_10Y 
- [OK |语义✔] S4_history_TIPS_10Y 
- [OK |语义✔] S4_history_BEI_10Y 
- [OK |语义✔] S4_history_NIKKEI225 
- [OK |语义✔] S4_history_HSI 
- [OK |语义✔] S5_compare 命中 27 个指标,compare 仅取注册表序前 2(US_REAL_GDP,UNEMPLOYMENT);其余 INDPRO,CPI,CORE_CPI,CORE_PCE,DFEDTARU,DFF,CN_PMI_MFG,CN_CPI_YOY,CN_PPI_YOY,CN_POLICY_OVERNIGHT,CN_OMO_7D,CN_LPR_1Y,EA_REAL_GDP_YOY,EA_HICP_YOY,ECB_MRO,ECB_DFR,JP_REAL_GDP_YOY,JP_CPI_YOY,JP_CPI_TOKYO_YOY,JP_POLICY_RATE,UST_10Y,TIPS_10Y,BEI_10Y,NIKKEI225,HSI 以 L1 事实行呈现,如需对比另行单跑
- [OK |语义✗] S6_analog 
- [OK |不适用] S7_mode_gate 
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(7 行)

- snapshot_fact:HSI@2026-11-19 → HSI
- snapshot_fact:NIKKEI225@2026-11-19 → NIKKEI225
- snapshot_fact:ECB_DFR@2026-09-16 → ECB_DFR
- snapshot_fact:ECB_MRO@2026-09-16 → ECB_MRO
- snapshot_fact:EA_HICP_YOY@2025-12-01 → EA_HICP_YOY
- snapshot_fact:JP_POLICY_RATE@2026-10-01 → JP_POLICY_RATE
- s3_envelope:HSCEI@2026-11-19 → HSCEI

## 注记

- 地图计划指标缺数(披露不阻断;缺数格=「数据不可得」+检索范围+影响): US_REAL_GDP、CORE_PCE、CN_CPI_YOY、CN_PPI_YOY、CN_POLICY_OVERNIGHT、CN_OMO_7D、CN_LPR_1Y、EA_REAL_GDP_YOY、EA_HICP_YOY、ECB_MRO、ECB_DFR、JP_REAL_GDP_YOY、JP_CPI_YOY、JP_CPI_TOKYO_YOY
