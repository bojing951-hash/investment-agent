# 完整研究报告(一键研究 MVP)

- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- run_ok: False | 证据行: 64 | run.ts_utc: 20261121T144742Z

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
| EA_HICP_YOY | 4.0 | percent | 2026-10-01 | WARN | EA_HICP_YOY@2026-10-01 |
| JP_POLICY_RATE | 1.227 | percent | 2026-10-01 | WARN | JP_POLICY_RATE@2026-10-01 |

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=False n=None 隔离=None
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)

## L3 AI 推断层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### CON-1 · 过去一年的全球主线是通胀中枢上移与货币政策再定价,而不是增长衰退: 增长面四地大体平稳——美国温和放缓(最新失业率 UNEMPLOYMENT 4.1)、欧元区与日本回升、中国低位修复。通胀面普遍上移: 中国生产端价格同比由负转正并明显走高(最新读数见走位面),欧元区消费通胀加速(读数见走位面),日本先回落再回升,美国消费与核心通胀同比中枢同样上移(引擎派生口径)。政策面分化而非同步紧缩: Fed 先降后升(目前有效联邦基金利率 DFF 3.88,一年净变动为零而方向已由降转升)。ECB 转入连续加息至 ECB_DFR 2.5。日本渐进收紧至 JP_POLICY_RATE 1.227。中国按兵不动并与欧美方向背离。
- 依据: 证据面: 引擎三时点点值面与转折候选面(CPI、CORE_PCE、CN_PPI_YOY、CN_PMI_MFG、EA_HICP_YOY、JP_CPI_YOY、INDPRO、US_REAL_GDP、EA_REAL_GDP_YOY、JP_REAL_GDP_YOY、JP_POLICY_RATE),政策事件簇(POLCLUSTER-01 Fed 2025-12-10 降息;POLCLUSTER-02 ECB 2026-06-11 加息;POLCLUSTER-03 ECB 2026-09-10 与 Fed 2026-09-16 加息构成跨国同一事件簇)与点值面;三期对照与同比派生数值见 reader_map 各地区走位与机制链。
- 竞争性解释: 供给驱动解释: 若通胀上移主要由供给端(能源与运输瓶颈、行业供给侧整合)驱动,则其将随供给修复自行回落,政策无须持续紧缩——将观察到 BEI_10Y 与 BRENT_F 领先回落、核心通胀跟随下行。
- 竞争性解释: 需求过热解释: 若通胀上移由需求过热(财政扩张与工资-物价循环)驱动,则将具有黏性,政策须维持紧缩甚至加码——将观察到 CORE_PCE 增速持续高位且 UNEMPLOYMENT 维持低位。
- 竞争性解释: 巧合叠加解释: 若美欧中通胀同窗上移主要是各地基数与口径因素的巧合,则后续月份跨区相关性将减弱、各自独立波动。
### CON-2 · 美债长端利率升至高位而曲线更平、通胀预期温和: 最新 UST_10Y 5.04、UST_2Y 4.76、CURVE_2S10S 0.29、BEI_10Y 2.15、VIX 35.89——市场定价的是高利率与高波动的组合,通胀预期并未脱锚;TIPS_10Y 序列不可得,实际利率分量无法直接验证,名义上行的归因(实际利率 vs 期限溢价)在引擎面上不可裁决。
- 依据: 证据面: 快照事实(见 evidence_refs)与 S4 序列月末口径复算(UST_10Y、UST_2Y、BEI_10Y、CURVE_2S10S,年度窗两端=2025-11 月末与 2026-11 月末,数值见机制链 CH-1 第 3 环);us_rates_trio 三利率共同交易日分解面 status=absent(TIPS_10Y 不可得,检索范围=快照 series_store 采集档通道)。
- 竞争性解释: 政策重定价解释: 若长端上行主要由政策再紧缩与增长韧性驱动,则短端应领先上行、曲线走平或持稳、BEI_10Y 温和——与当前组合(短端高位、曲线较一年前更平、盈亏平衡温和)相容。
- 竞争性解释: 期限溢价解释: 若长端上行主要由财政供给与期限溢价推升,则 BEI_10Y 应与名义利率同升、CURVE_2S10S 趋势陡峭化——当前盈亏平衡温和且曲线走平,与该解释的主方向不符,但尚不能排除财政因素的边际贡献。
### CON-3 · 近一月风险资产与黄金同步深跌、波动率翻倍、美元走强: SPX -10.92%、NIKKEI225 -12.67%、DAX -3.28%、SHCOMP -4.83%、GOLD_F -15.29%、VIX +115.17%、DXY +1.99%(月窗 2026-10-21→2026-11-20),UST_10Y 5.04 于同窗高位小幅回落(窗口 2026-10-21→2026-11-19);信用利差并未显著走阔(HY_OAS 3.52、IG_OAS 0.94),单月窗口不足以在「利率/贴现率驱动」与「增长担忧驱动」之间作出裁决。
- 依据: 证据面: 引擎资产月窗复算(asset_moves 八行,窗口 2026-10-21→2026-11-20,UST_10Y 行至 2026-11-19,两端实测日随行),快照事实与信用利差对照(HY_OAS、IG_OAS、BB_OAS、B_OAS、CCC_OAS)。
- 竞争性解释: 贴现率驱动: 若压制来自高利率与波动冲击,则零票息的 GOLD_F 弹性应最大、DXY 偏强——与本月黄金回撤最深、美元走强的组合相容。
- 竞争性解释: 增长担忧驱动: 若回撤源于盈利预期下修,则 HY_OAS 走阔将领先或同步于股指、利率将因避险反而大幅下行——当前月窗信用利差变动温和、利率仅小幅回落,证据尚不足以支持该侧。
- 竞争性解释: 波动率自我强化: 若 VIX 冲高引发波动率目标与流动性反馈,则回撤与基本面指标的相关性将弱、修复也快——该解释与任何单一致因并列存在。
### 机制链 CH-1 · 全球通胀上移→政策再定价→利率高位与曲线走平→风险资产与黄金承压
- 环1 [E1] 美中欧通胀于 2026-02→2026-05 同窗上移: 美国 CPI 同比(引擎派生口径)2.434→4.1666、中国 CN_PPI_YOY -0.9→3.9、欧元区 EA_HICP_YOY 1.9→3.2(引擎转折候选面,月频);美国 CORE_PCE 同比 2.85(2025-08 观测)→3.12(2026-09 观测)。
- 环2 [E1] 政策再定价跟进: ECB 于 2026-06-11、2026-09-10 各加息 25bp(ECB_DFR 2.0→2.5);Fed 于 2026-09-16 加息 25bp(DFEDTARU 3.75→4.0,与 ECB 决议构成跨国同一政策事件簇 POLCLUSTER-03);日本以无担保隔夜拆借月均口径渐进抬升(JP_POLICY_RATE 0.477→1.227);中国 CN_OMO_7D 1.4 与 CN_LPR_1Y 3.0 按兵不动(政策背离端)。
- 环3 [E2] 长端利率升至高位而曲线走平: UST_10Y 4.02→5.04、UST_2Y 3.47→4.76(2025-11-28→2026-11-19 月末口径),CURVE_2S10S 0.55→0.29,BEI_10Y 2.23→2.15(通胀预期温和)。
  - 缺环注记: 缺失环【假设】: 政策利率→长端利率的映射为假设——本引擎 TIPS_10Y 序列不可得(三利率共同交易日分解缺席),实际利率与期限溢价的分解无法直接验证,仅能以短端大幅上行+曲线走平+盈亏平衡温和间接支持政策驱动一侧。
- 环4 [E3] 高利率与波动冲击压制风险资产与非孳息资产: 近一月 SPX -10.92%、NIKKEI225 -12.67%、DAX -3.28%、SHCOMP -4.83%、GOLD_F -15.29%、VIX +115.17%、DXY +1.99%(月窗 2026-10-21→2026-11-20)。
### 机制链 CH-2 · 中国再通胀与欧美再紧缩的政策背离通道(并列竞争通道)
- 环1 [E1] 中国生产端价格由通缩转再通胀: CN_PPI_YOY -2.1(2025-10)→-0.9(2026-02)→3.9(2026-05)→5.7(2026-10);制造业 PMI 同比(派生)-2.2→-0.2→+0.61 转正。
- 环2 [E2] 中国政策未随再通胀收紧: CN_OMO_7D 1.4 三期持稳、CN_LPR_1Y 3.0 持稳,2026-11-02 起政策利率锚换为隔夜逆回购利率(CN_POLICY_OVERNIGHT 1.25)——与 ECB(2026-06 起)与 Fed(2026-09)的加息方向相反。
  - 缺环注记: 缺失环【假设】: 换锚与不收紧的动机(以再通胀修复名义增长/汇率考量)为假设——引擎无央行沟通文本序列,该环不可验证。
- 环3 [E3] 背离的资产含义: 中国资产本月相对抗跌(SHCOMP 月窗 -4.83% vs SPX -10.92%),但单月窗口不足以把「政策背离红利」与「估值/结构因素」区分开。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### S1-再紧缩延续 · 角色=基准(主解释延续)
- 情景: 假设(非预测): 通胀中枢上移与政策再紧缩延续,长端利率维持高位,增长温和降温但不衰退,高波动逐步消化而非扩散为信用事件。
- 资产方向: 长久期成长股指(SPX/NDX)与黄金(GOLD_F)承压、VIX 中枢抬升、DXY 偏强;现金与短久期相对占优。注意历史相似样本 2022-06 锚后 12 个月 SPX +17.57%——紧缩中段风险资产亦可先深跌后收复,方向判断置信有限。 | 置信档: 有相关证据
- 敏感变量: BEI_10Y, VIX
- 证伪: 指标=VIX | 阈值=VIX 月末值自 2026-11 的 35.89 回落至 20 下方并连续两个月维持(波动冲击趋势性消退即推翻本情景主通道) | 次级=BEI_10Y
- 触发: BEI_10Y 月末维持在 2.2 附近或以下(通胀预期未脱锚)且 Fed 或 ECB 再加息一次或点阵图上修 | 期限: 2027-05-21
### S2-通胀快速回落→宽松重定价 · 角色=反例(与基准并列检验)
- 情景: 假设(非预测): 通胀回落速度快于政策反应,市场转向宽松定价,结构上类似 2025-03 锚点之后的路径(该锚点后 12 个月 DFEDTARU -0.75pp、SPX +16.33%、GOLD_F +48.83%)。
- 资产方向: 股指与黄金反弹、DXY 走弱、VIX 回落(历史相似样本 2025-03 锚后 12 个月 SPX +16.33%、黄金期货 +48.83%)。 | 置信档: 有历史相似证据
- 敏感变量: CPI, BEI_10Y
- 证伪: 指标=BEI_10Y | 阈值=BEI_10Y 月末升破 2.60 并连续两个月维持(通胀预期脱锚上行,宽松重定价前提失效)
- 触发: CPI 同比(引擎派生口径)连续两个月回落,且 Fed 在 2026-09 加息后按兵不动超过两个会议周期 | 期限: 2027-05-21

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
| 21 | snapshot_fact | BEI_10Y@2026-11-20 |  |
| 22 | snapshot_fact | CURVE_2S10S@2026-11-20 |  |
| 23 | snapshot_fact | CPI@2026-10-01 |  |
| 24 | snapshot_fact | CORE_PCE@2026-09-01 |  |
| 25 | snapshot_fact | UNEMPLOYMENT@2026-10-01 |  |
| 26 | snapshot_fact | CORE_CPI@2026-10-01 |  |
| 27 | snapshot_fact | UST_5Y@2026-11-19 |  |
| 28 | snapshot_fact | INDPRO@2026-10-01 |  |
| 29 | snapshot_fact | US_REAL_GDP@2026-07-01 |  |
| 30 | snapshot_fact | SHCOMP@2026-11-20 |  |
| 31 | snapshot_fact | HSI@2026-11-20 |  |
| 32 | snapshot_fact | CN_LPR_1Y@2026-11-20 |  |
| 33 | snapshot_fact | CN_PMI_MFG@2026-10-01 |  |
| 34 | snapshot_fact | NIKKEI225@2026-11-20 |  |
| 35 | snapshot_fact | JP_CPI_YOY@2026-10-01 |  |
| 36 | snapshot_fact | ECB_DFR@2026-09-16 |  |
| 37 | snapshot_fact | ECB_MRO@2026-09-16 |  |
| 38 | snapshot_fact | EA_HICP_YOY@2026-10-01 |  |
| 39 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 40 | s3_envelope | SZCI@2026-11-20 |  |
| 41 | s3_envelope | CHINEXT@2026-11-20 |  |
| 42 | s3_envelope | HSCEI@2026-11-20 |  |
| 43 | s3_envelope | NVDA@2026-11-20 |  |
| 44 | s3_envelope | AAPL@2026-11-20 |  |
| 45 | s3_envelope | MSFT@2026-11-20 |  |
| 46 | s3_envelope | TLT@2026-11-20 |  |
| 47 | s3_envelope | IEF@2026-11-20 |  |
| 48 | s3_envelope | SHY@2026-11-20 |  |
| 49 | s3_envelope | HYG@2026-11-20 |  |
| 50 | s3_envelope | LQD@2026-11-20 |  |
| 51 | s3_envelope | GBPUSD@2026-11-20 |  |
| 52 | s3_envelope | WTI_F@2026-11-20 |  |
| 53 | s3_envelope | GLD@2026-11-20 |  |
| 54 | s3_envelope | USO@2026-11-20 |  |
| 55 | s3_envelope | EEM@2026-11-20 |  |
| 56 | s3_envelope | EZU@2026-11-20 |  |
| 57 | s3_envelope | FEZ@2026-11-20 |  |
| 58 | s3_envelope | EWU@2026-11-20 |  |
| 59 | s3_envelope | EWG@2026-11-20 |  |
| 60 | s3_envelope | EWJ@2026-11-20 |  |
| 61 | s3_envelope | INDA@2026-11-20 |  |
| 62 | s3_envelope | FXI@2026-11-20 |  |
| 63 | s3_envelope | BTC@2026-11-20 |  |
| 64 | s3_envelope | HY_IG_DIFF@2026-11-19 |  |

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


## 质量状态(Audit-R1 F02 四态+Audit-R2 绑定面+Audit-R4 贯通面)

- generated: true(FULL_REPORT 完整装配: L1+L2+L3/L4 全文内联+证据索引)
- machine_verified: True(L3∧L4 produced+纪律校验过+底座非降级或 optional 级显式降级随档)
- run 门(Audit-R4 条目5): blocked_class=optional_data_missing degraded_ok=True
- review: required=True seat_invoked=True verdict=UPHELD fresh=True error=None 修订链档数=1
- copies_consistent(多副本一致): True(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前确定性装配)
- deliverable(可交付): True
- 内容绑定(Audit-R4 条目2): content_sha256=canonical(report.json 剥离 semantic_review)+canonical(agent_judgment.json)+canonical(views_digest.json)——机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。
