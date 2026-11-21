# 完整研究报告(一键研究 MVP)

- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- run_ok: True | 证据行: 68 | run.ts_utc: 20261119T153709Z

## L1 事实层(引擎确定性产出)

| 指标 | 值 | 单位 | 观测日 | 质量 | 证据 ref |
|---|---|---|---|---|---|
| SPX | 7323.63 | index_point | 2026-11-18 | PASS | SPX@2026-11-18 |
| NDX | 27116.26 | index_point | 2026-11-18 | PASS | NDX@2026-11-18 |
| RUT | 2714.31 | index_point | 2026-11-18 | PASS | RUT@2026-11-18 |
| DXY | 103.78 | index_point | 2026-11-18 | PASS | DXY@2026-11-18 |
| EURUSD | 1.1 | usd_per_eur | 2026-11-18 | PASS | EURUSD@2026-11-18 |
| GOLD_F | 3727.8 | usd_per_oz | 2026-11-18 | PASS | GOLD_F@2026-11-18 |
| SILVER_F | 44.97 | usd_per_oz | 2026-11-18 | PASS | SILVER_F@2026-11-18 |
| BRENT_F | 88.68 | usd_per_barrel | 2026-11-18 | PASS | BRENT_F@2026-11-18 |
| VIX | 24.56 | index_point | 2026-11-18 | PASS | VIX@2026-11-18 |
| DAX | 26045.37 | index_point | 2026-11-17 | PASS | DAX@2026-11-17 |
| CAC40 | 8216.78 | index_point | 2026-11-17 | PASS | CAC40@2026-11-17 |
| USDJPY | 159.3 | jpy_per_usd | 2026-11-18 | PASS | USDJPY@2026-11-18 |
| USDCNY | 6.66 | cny_per_usd | 2026-11-18 | PASS | USDCNY@2026-11-18 |
| HY_OAS | 3.43 | percentage_point | 2026-11-17 | PASS | HY_OAS@2026-11-17 |
| BB_OAS | 2.04 | percentage_point | 2026-11-17 | PASS | BB_OAS@2026-11-17 |
| B_OAS | 3.68 | percentage_point | 2026-11-17 | PASS | B_OAS@2026-11-17 |
| CCC_OAS | 13.29 | percentage_point | 2026-11-17 | PASS | CCC_OAS@2026-11-17 |
| IG_OAS | 0.92 | percentage_point | 2026-11-17 | PASS | IG_OAS@2026-11-17 |
| UST_2Y | 4.8 | percent | 2026-11-17 | PASS | UST_2Y@2026-11-17 |
| UST_10Y | 5.1 | percent | 2026-11-17 | PASS | UST_10Y@2026-11-17 |
| UST_30Y | 5.46 | percent | 2026-11-17 | PASS | UST_30Y@2026-11-17 |
| TIPS_5Y | 2.64 | percent | 2026-11-17 | PASS | TIPS_5Y@2026-11-17 |
| TIPS_10Y | 2.89 | percent | 2026-11-17 | PASS | TIPS_10Y@2026-11-17 |
| BEI_5Y | 2.23 | percent | 2026-11-18 | PASS | BEI_5Y@2026-11-18 |
| BEI_10Y | 2.19 | percent | 2026-11-18 | PASS | BEI_10Y@2026-11-18 |
| CURVE_2S10S | 0.27 | percentage_point | 2026-11-18 | PASS | CURVE_2S10S@2026-11-18 |
| CPI | 337.476 | index_point_1982_84 | 2026-10-01 | WARN | CPI@2026-10-01 |
| CORE_PCE | 130.902 | index_point_2017 | 2026-09-01 | DEGRADED | CORE_PCE@2026-09-01 |
| UNEMPLOYMENT | 4.1 | percent | 2026-10-01 | WARN | UNEMPLOYMENT@2026-10-01 |
| CORE_CPI | 339.9 | index_point_1982_84 | 2026-10-01 | WARN | CORE_CPI@2026-10-01 |
| UST_5Y | 4.9 | percent | 2026-11-17 | PASS | UST_5Y@2026-11-17 |
| INDPRO | 103.3954 | index_point_2017 | 2026-10-01 | WARN | INDPRO@2026-10-01 |
| US_REAL_GDP | 24611.077 | billion_usd | 2026-07-01 | DEGRADED | US_REAL_GDP@2026-07-01 |
| SHCOMP | 3587.83 | index_point | 2026-11-18 | PASS | SHCOMP@2026-11-18 |
| HSI | 22814.93 | index_point | 2026-11-19 | PASS | HSI@2026-11-19 |
| CN_LPR_1Y | 3.0 | percent | 2026-10-20 | WARN | CN_LPR_1Y@2026-10-20 |
| CN_PMI_MFG | 49.3 | index_point | 2026-10-01 | WARN | CN_PMI_MFG@2026-10-01 |
| NIKKEI225 | 59024.28 | index_point | 2026-11-18 | PASS | NIKKEI225@2026-11-18 |
| JP_CPI_YOY | 2.16 | percent | 2026-09-01 | DEGRADED | JP_CPI_YOY@2026-09-01 |
| ECB_DFR | 2.5 | percent | 2026-09-16 | DEGRADED | ECB_DFR@2026-09-16 |
| ECB_MRO | 2.65 | percent | 2026-09-16 | DEGRADED | ECB_MRO@2026-09-16 |
| EA_HICP_YOY | 4.0 | percent | 2026-10-01 | WARN | EA_HICP_YOY@2026-10-01 |
| JP_POLICY_RATE | 1.227 | percent | 2026-10-01 | WARN | JP_POLICY_RATE@2026-10-01 |

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=False n=None 隔离=None
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)

## L3 AI 推断层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### CON-1 · 过去一年的全球主线是通胀中枢上移与货币政策再定价,而不是增长衰退: 四地增长大体平稳(美国温和放缓、欧元区与日本回升、中国低位修复),而通胀同比普遍上移(美欧生产与消费价格走高、日本先回落再回升);政策取向上 Fed 先降后升净变动为零、ECB 转入连续加息、日本以市场口径渐进收紧、中国按兵不动并更换政策利率锚——政策与通胀的组合在四地分化,而非同步紧缩。
- 依据: 证据面: 引擎三时点点值面与转折候选面(CPI、CORE_PCE、CN_PPI_YOY、CN_PMI_MFG、EA_HICP_YOY、JP_CPI_YOY、INDPRO、US_REAL_GDP、EA_REAL_GDP_YOY、JP_REAL_GDP_YOY、JP_POLICY_RATE),政策事件簇与点值面(DFEDTARU、DFF、ECB_DFR、央行七天逆回购利率、隔夜新锚、LPR 报价利率)。
- 竞争性解释: 供给驱动解释: 若通胀上移主要由供给端(能源与运输瓶颈、行业供给侧整合)驱动,则其将随供给修复自行回落,政策无须持续紧缩——将观察到 BEI_10Y 与大宗价格领先回落、核心通胀跟随下行。
- 竞争性解释: 需求过热解释: 若通胀上移由需求过热(财政扩张与工资-物价循环)驱动,则将具有黏性,政策须维持紧缩甚至加码——将观察到 CORE_PCE 增速持续高于目标且 UNEMPLOYMENT 维持低位。
- 竞争性解释: 巧合叠加解释: 若美欧中通胀同窗上移主要是各地基数与口径因素的巧合,则后续月份跨区相关性将减弱、各自独立波动。
### CON-2 · 十年期美债名义利率的过去一年上行几乎全部由实际利率承载,盈亏平衡通胀率反而小幅回落——市场定价的是「实际利率型」紧缩,通胀预期并未脱锚。曲线较一年前更平,与期限溢价主导的形态不符。
- 依据: 证据面: 引擎共同交易日三利率分解(十年期名义、十年期实际、十年期盈亏平衡三序列同窗复算;快照事实见 evidence_refs),曲线与风险资产对照面(快照事实见 evidence_refs)。
- 竞争性解释: 期限溢价解释: 若上行主要来自财政供给与期限溢价,则 BEI_10Y 将与名义利率同升、CURVE_2S10S 将趋势性陡峭化——当前年窗盈亏平衡小幅回落且曲线较一年前更平,与该解释的主方向不符,但尚不能排除财政因素的边际贡献。
- 竞争性解释: 自然利率解释: 若实际利率上行源于增长预期改善推升自然利率,则风险资产将与实际利率同涨——而近一月 SPX 回撤与 TIPS_10Y 上行反向,与该解释不相容(窗口尚短,不能定论)。
### CON-3 · 近一月风险资产与黄金同步回撤、波动率抬升、美元走强,方向上与实际利率上行一致;但现有单月窗口不足以在「政策/实际利率驱动」与「增长担忧驱动」之间作出裁决。
- 依据: 证据面: 引擎资产月窗复算(SPX、NIKKEI225、GOLD_F、VIX、DAX、DXY、SHCOMP)与 TIPS_10Y 月窗复算、信用利差月度对照(HY_OAS、IG_OAS)。
- 竞争性解释: 实际利率驱动: 若压制来自贴现率上行,则零票息的 GOLD_F 对 TIPS_10Y 的弹性应最大、DXY 偏强——与本月黄金回撤最深、美元走强的组合相容。
- 竞争性解释: 增长担忧驱动: 若回撤源于盈利预期下修,则 HY_OAS 走阔将领先或同步于股指、利率将因避险反而下行——当前月窗信用利差变动温和(约收窄),证据尚不足以支持该侧。
### 机制链 CH-1 · 全球通胀上移→政策再定价→实际利率上行→风险资产承压
- 环1 [E1] 美中欧通胀于 2026-02→2026-05 同窗上移: 美国CPI同比 2.434→4.1666、中国 CN_PPI_YOY 同比 -0.9→3.9、欧元区 EA_HICP_YOY 同比 1.9→3.2(引擎转折候选面,月频);美国 CORE_PCE 同比由 2.85(2025-08 观测)升至 3.12(2026-09 观测)。
- 环2 [E1] 政策再定价跟进: ECB 于 2026-06-11、2026-09-10 各加息 25bp(ECB_DFR 2.0→2.5);Fed 于 2026-09-16 加息 25bp(DFEDTARU 3.75→4.0,与 ECB 决议构成跨国同一政策事件簇);日本以无担保隔夜拆借月均口径渐进抬升(JP_POLICY_RATE 0.477→1.227);中国 CN_OMO_7D 1.4 与 CN_LPR_1Y 3.0 按兵不动(政策背离端)。
- 环3 [E2] 美债长端名义利率上行几乎全部由实际利率承载: 年度窗 UST_10Y +97bp = TIPS_10Y +104bp + BEI_10Y -7bp(2025-11-17→2026-11-17 共同交易日复算);月度窗名义 +1bp = 实际 +15bp + 盈亏平衡 -14bp(2026-10-16→2026-11-17)。
  - 缺环注记: 缺失环【假设】: 政策利率→长端实际利率的映射为假设——引擎面无远期政策曲线或期限溢价分解的直接观测,仅能以 TIPS_10Y 与政策决议窗口的同向变动间接支持。
- 环4 [E3] 高实际利率对风险资产与非孳息资产估值形成压制: 近一月 SPX -4.77%、NIKKEI225 -9.08%、GOLD_F -10.39%、SHCOMP -3.84%、VIX +33.19%、DXY +1.76%,DAX +2.87% 逆势(月窗复算,两端观测日随行披露)。
### 机制链 CH-2 · 美国增长温和降温→政策两难(与通胀主链并列的竞争通道)
- 环1 [E1] 美国增长面: 实际GDP同比 2.42(2025Q2)→2.19(2026Q2)→2.07(2026Q3,事后回顾口径);失业率 4.3→4.1→4.1;INDPRO 同比 1.19→1.25→2.15(先于 2026-02 一度降至 0.7972 后回升)。
- 环2 [E3] 增长温和降温与通胀上移并存使政策进入两难: 若增长进一步走弱而通胀居高,则紧缩的可持续性存疑——该环为叙事推断,非引擎直接可验证。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### S1-紧缩延续 · 角色=基准(主解释延续)
- 情景: 假设(非预测): 通胀中枢上移与政策再紧缩延续,实际利率维持高位甚至进一步上行,增长温和降温但不衰退。
- 资产方向: 长久期成长股指(SPX/NDX)与黄金(GOLD_F)承压、VIX 中枢抬升、DXY 偏强;现金与短久期相对占优。 | 置信档: 有相关证据
- 敏感变量: TIPS_10Y, BEI_10Y
- 证伪: 指标=TIPS_10Y | 阈值=TIPS_10Y 月末值自 2026-11 的 2.89 回落至 2.50 下方并连续两个月维持(实际利率趋势性下行即推翻本情景主通道) | 次级=BEI_10Y
- 触发: BEI_10Y 月末维持在 2.2 附近或以下(名义上行继续由实际利率承载)且 Fed 再加息一次或点阵图上修 | 期限: 2027-05-19
### S2-通胀快速回落→宽松重定价 · 角色=反例(与基准并列检验)
- 情景: 假设(非预测): 通胀回落速度快于政策反应,市场转向宽松定价,重演 2023-10 锚点之后利率见顶回落、风险资产与黄金上行的历史相似路径。
- 资产方向: 股指与黄金反弹、DXY 走弱、VIX 回落(历史相似样本 2023-10 锚后 12 个月 SPX +36.04%、黄金期货 +37.86%)。 | 置信档: 有历史相似证据
- 敏感变量: BEI_10Y, CPI
- 证伪: 指标=BEI_10Y | 阈值=BEI_10Y 月末升破 2.60 并连续两个月维持(通胀预期脱锚上行,宽松重定价前提失效)
- 触发: CPI 同比(引擎派生口径)连续两个月回落,且 Fed 在最后一次加息后按兵不动超过两个会议周期 | 期限: 2027-05-19

## 证据索引

| # | kind | ref | 说明 |
|---|---|---|---|
| 1 | snapshot_fact | SPX@2026-11-18 |  |
| 2 | snapshot_fact | NDX@2026-11-18 |  |
| 3 | snapshot_fact | RUT@2026-11-18 |  |
| 4 | snapshot_fact | DXY@2026-11-18 |  |
| 5 | snapshot_fact | EURUSD@2026-11-18 |  |
| 6 | snapshot_fact | GOLD_F@2026-11-18 |  |
| 7 | snapshot_fact | SILVER_F@2026-11-18 |  |
| 8 | snapshot_fact | BRENT_F@2026-11-18 |  |
| 9 | snapshot_fact | VIX@2026-11-18 |  |
| 10 | snapshot_fact | DAX@2026-11-17 |  |
| 11 | snapshot_fact | CAC40@2026-11-17 |  |
| 12 | snapshot_fact | USDJPY@2026-11-18 |  |
| 13 | snapshot_fact | USDCNY@2026-11-18 |  |
| 14 | snapshot_fact | HY_OAS@2026-11-17 |  |
| 15 | snapshot_fact | BB_OAS@2026-11-17 |  |
| 16 | snapshot_fact | B_OAS@2026-11-17 |  |
| 17 | snapshot_fact | CCC_OAS@2026-11-17 |  |
| 18 | snapshot_fact | IG_OAS@2026-11-17 |  |
| 19 | snapshot_fact | UST_2Y@2026-11-17 |  |
| 20 | snapshot_fact | UST_10Y@2026-11-17 |  |
| 21 | snapshot_fact | UST_30Y@2026-11-17 |  |
| 22 | snapshot_fact | TIPS_5Y@2026-11-17 |  |
| 23 | snapshot_fact | TIPS_10Y@2026-11-17 |  |
| 24 | snapshot_fact | BEI_5Y@2026-11-18 |  |
| 25 | snapshot_fact | BEI_10Y@2026-11-18 |  |
| 26 | snapshot_fact | CURVE_2S10S@2026-11-18 |  |
| 27 | snapshot_fact | CPI@2026-10-01 |  |
| 28 | snapshot_fact | CORE_PCE@2026-09-01 |  |
| 29 | snapshot_fact | UNEMPLOYMENT@2026-10-01 |  |
| 30 | snapshot_fact | CORE_CPI@2026-10-01 |  |
| 31 | snapshot_fact | UST_5Y@2026-11-17 |  |
| 32 | snapshot_fact | INDPRO@2026-10-01 |  |
| 33 | snapshot_fact | US_REAL_GDP@2026-07-01 |  |
| 34 | snapshot_fact | SHCOMP@2026-11-18 |  |
| 35 | snapshot_fact | HSI@2026-11-19 |  |
| 36 | snapshot_fact | CN_LPR_1Y@2026-10-20 |  |
| 37 | snapshot_fact | CN_PMI_MFG@2026-10-01 |  |
| 38 | snapshot_fact | NIKKEI225@2026-11-18 |  |
| 39 | snapshot_fact | JP_CPI_YOY@2026-09-01 |  |
| 40 | snapshot_fact | ECB_DFR@2026-09-16 |  |
| 41 | snapshot_fact | ECB_MRO@2026-09-16 |  |
| 42 | snapshot_fact | EA_HICP_YOY@2026-10-01 |  |
| 43 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 44 | s3_envelope | SZCI@2026-11-18 |  |
| 45 | s3_envelope | CHINEXT@2026-11-18 |  |
| 46 | s3_envelope | HSCEI@2026-11-19 |  |
| 47 | s3_envelope | NVDA@2026-11-18 |  |
| 48 | s3_envelope | AAPL@2026-11-18 |  |
| 49 | s3_envelope | MSFT@2026-11-18 |  |
| 50 | s3_envelope | TLT@2026-11-18 |  |
| 51 | s3_envelope | IEF@2026-11-18 |  |
| 52 | s3_envelope | SHY@2026-11-18 |  |
| 53 | s3_envelope | HYG@2026-11-18 |  |
| 54 | s3_envelope | LQD@2026-11-18 |  |
| 55 | s3_envelope | GBPUSD@2026-11-18 |  |
| 56 | s3_envelope | WTI_F@2026-11-18 |  |
| 57 | s3_envelope | GLD@2026-11-18 |  |
| 58 | s3_envelope | USO@2026-11-18 |  |
| 59 | s3_envelope | EEM@2026-11-18 |  |
| 60 | s3_envelope | EZU@2026-11-18 |  |
| 61 | s3_envelope | FEZ@2026-11-18 |  |
| 62 | s3_envelope | EWU@2026-11-18 |  |
| 63 | s3_envelope | EWG@2026-11-18 |  |
| 64 | s3_envelope | EWJ@2026-11-18 |  |
| 65 | s3_envelope | INDA@2026-11-18 |  |
| 66 | s3_envelope | FXI@2026-11-18 |  |
| 67 | s3_envelope | BTC@2026-11-17 |  |
| 68 | s3_envelope | HY_IG_DIFF@2026-11-17 |  |

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


## 质量状态(Audit-R1 F02 四态+Audit-R2 绑定面+Audit-R4 贯通面)

- generated: true(FULL_REPORT 完整装配: L1+L2+L3/L4 全文内联+证据索引)
- machine_verified: True(L3∧L4 produced+纪律校验过+底座非降级或 optional 级显式降级随档)
- run 门(Audit-R4 条目5): blocked_class=None degraded_ok=False
- review: required=True seat_invoked=True verdict=UPHELD fresh=True error=None 修订链档数=1
- copies_consistent(多副本一致): True(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前确定性装配)
- deliverable(可交付): True
- 内容绑定(Audit-R4 条目2): content_sha256=canonical(report.json 剥离 semantic_review)+canonical(agent_judgment.json)+canonical(views_digest.json)——机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。
