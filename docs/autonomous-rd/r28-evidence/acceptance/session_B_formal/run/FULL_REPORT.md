# 完整研究报告(一键研究 MVP)

- 问题: 对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整过了多久？
- run_ok: True | 证据行: 63 | run.ts_utc: 20261121T074345Z

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
| UST_30Y | 5.4 | percent | 2026-11-19 | PASS | UST_30Y@2026-11-19 |
| TIPS_5Y | 2.64 | percent | 2026-11-19 | PASS | TIPS_5Y@2026-11-19 |
| TIPS_10Y | 2.88 | percent | 2026-11-19 | PASS | TIPS_10Y@2026-11-19 |
| BEI_5Y | 2.18 | percent | 2026-11-20 | PASS | BEI_5Y@2026-11-20 |
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
| NIKKEI225 | 56436.65 | index_point | 2026-11-20 | PASS | NIKKEI225@2026-11-20 |
| EA_HICP_YOY | 4.0 | percent | 2026-10-01 | WARN | EA_HICP_YOY@2026-10-01 |
| JP_POLICY_RATE | 1.227 | percent | 2026-10-01 | WARN | JP_POLICY_RATE@2026-10-01 |

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=False n=None 隔离=None
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)

## L3 AI 推断层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### CON-1 · 以 2026-08-21 与 2026-11-21 两个日历点锚对照,美国与欧元区三个月变化的共同主线在通胀侧而非增长侧: 美国增长面大体平稳(产出同比微降、工业生产同比回升、失业率持平)而通胀读数温和上行;欧元区增长面在本报告证据面不可判,通胀则显著加速,已成为两地通胀-增长组合中失衡更大的一端;日本在同窗将政策利率(市场月均口径)再抬一格,紧缩方向延续。三地组合由「增长修复+通胀温和」向「增长平稳/不可判+通胀上移+政策渐进收紧」移动。
- 依据: 证据面: 引擎三时点点值面(US_REAL_GDP、UNEMPLOYMENT、INDPRO、CPI、CORE_CPI、CORE_PCE、EA_HICP_YOY、JP_POLICY_RATE 八格锚值;EA_REAL_GDP_YOY 序列缺席该格如实标数据不可得),观测月/发布日/修订口径随格。
- 竞争性解释: 供给/基数驱动解释: 若欧元区通胀加速与美国通胀温和上行主要由能源与基数等临时因素驱动,则无需政策持续紧缩应自行回落——将观察到 BEI_10Y 与大宗价格领先回落、核心口径(CORE_PCE/CORE_CPI)跟随下行。
- 竞争性解释: 需求过热驱动解释: 若通胀上移由需求韧性(工资-物价循环)驱动,则具有黏性、政策须维持紧缩——将观察到核心口径持续走高且 UNEMPLOYMENT 维持低位、INDPRO 同比不回落。
- 竞争性解释: 口径与巧合解释: 两地通胀同窗上移或为各地统计口径与局部因素(欧元区能源、美国服务)的巧合叠加,后续跨区走势将分化而非共振。
### CON-2 · 利率市场结构不支持「通胀预期驱动」叙事: 近一月 UST_10Y 名义小幅回落,而 TIPS_10Y 上行、BEI_10Y 下行;十二个月窗 UST_10Y 的上行几乎全部由 TIPS_10Y 承载,BEI_10Y 反而下降;VIX 处于高位。市场定价的是实际利率型紧缩,通胀预期未脱锚——这与欧元区通胀加速并存,构成「通胀现实上行 vs 通胀预期受控」的张力。
- 依据: 证据面: 引擎共同交易日三利率分解(名义/实际/盈亏平衡同窗复算,窗口与残差随行),近一月与近十二月两窗;快照事实见 evidence_refs。
- 竞争性解释: 政策与自然利率解释: 实际利率上行源于货币政策再定价与增长韧性推升的实际利率中枢——则 BEI_10Y 应维持稳定而 TIPS_10Y 与政策预期同向上行。
- 竞争性解释: 期限溢价与财政供给解释: 长端主要由财政供给与期限溢价定价,与通胀与政策预期无关——则 CURVE_2S10S 趋势陡峭化且长端与短端分化。
- 竞争性解释: 避险与流动性解释: 近一月风险资产大幅回撤、VIX 处于高位,避险买盘压低 UST_10Y 名义收益率,而 TIPS 流动性较差使 TIPS_10Y 被动走高——该解释的区分观察=TIPS_10Y 月窗升幅与 VIX 高位状态是否同起同落;当前两者并存,该解释未被排除。
### CON-3 · 「日本央行政策利率处于什么水平、距上次调整多久」由两层口径共同回答且两层层级分记: 官方实录层(日历实录条目,BOJ 决议实录表)给出政策目标水平、决议日与生效日,距上次调整按生效日精确计天;市场月均层(JP_POLICY_RATE 无担保隔夜拆借月均)以月频分辨率印证目标水平并平滑呈现加息的跨月效应。月均不冒充目标宣布值。对更早两次抬升,本报告实录面未含决议日,「同为单次步长」的解读仍属推断;月均与目标之间的残余偏差容纳两种读法。
- 依据: 证据面: 引擎政策实录面(日历实录条目 RC-JP-BOJ-TARGET 与 RC-JP-BOJ-MAINT,BOJ 决议实录表,经 freshness_policy 政策决议状态复核)+JP_POLICY_RATE 月均序列与 policy_window_path 事件面。
- 竞争性解释: 步长解读(最新一段已获实录支持): 最新一次抬升由实录裁明为单次调整(决议与生效分记);更早两段月均形态与之同构,推断同为单次步长跨月平滑——需更早决议日的实录全表方可转证。
- 竞争性解释: 残余偏差的波动解读: 月均与目标的残余差距反映市场利率围绕目标的日常波动与月末资金面,而非另一次调整——若后续月均回到目标附近则支持;若持续偏离且伴随新实录决议,则调整解读胜出。
### 机制链 CH-1 · 欧美通胀上移→政策再定价→实际利率结构→风险资产承压
- 环1 [E1] 三个月窗通胀变化: 欧元区 EA_HICP_YOY 同比 2.9(2026-07)→4.0(2026-10),+1.1pp,且 2026-08 起 3.2→3.8→4.0 连续三期上行;美国 CPI 派生同比 3.30(2026-07)→3.72(2026-09 最新有效,2026-10 缺基期不可得),CORE_CPI 2.47→2.57(2026-07→2026-09),CORE_PCE 3.04→3.12(2026-06→2026-09)——美温和、欧陡峭。
- 环2 [E1] 政策面(引擎可得部分): JP_POLICY_RATE 月均 0.978(2026-07)→1.227(2026-10),三个月 +24.9bp;十二个月窗净 +67bp(0.557→1.227,2025-11→2026-10 观测),变动点序列呈 2025-12/2026-01(+8/+17bp)、2026-06/07(+11/+14bp)、2026-09/10(+7/+18bp)三段爬升。Fed/ECB 政策利率决议序列不在本报告证据面(本次计划未含),美欧政策反应环以「证据面缺席」呈现,不虚构。
- 环3 [E2] 美债利率结构: 月度共同交易日窗(2026-10-20→2026-11-19)UST_10Y -8bp = TIPS_10Y +11bp + BEI_10Y -19bp(期末水平 5.04/2.88/2.16);十二个月窗(2025-11-19→2026-11-19)+91bp = +102bp + (-11bp)——两窗均由实际利率承载。
  - 缺环注记: 缺失环【假设】: 政策利率/通胀现实→长端实际利率定价的映射为假设——本报告证据面无政策预期曲线或期限溢价分解序列,仅能以 TIPS_10Y 与通胀、政策路径的同向共现间接支持,因果方向不可证。
- 环4 [E3] 风险资产与波动率: 近一月(2026-10-21→2026-11-20)SPX -10.92%、NIKKEI225 -12.67%、GOLD_F -15.29%、DAX -3.28%,VIX +115.17%,DXY +1.99%;UST_10Y 月窗 -1.75%(2026-10-21→2026-11-19)。高实际利率与波动抬升并存的格局与估值承压叙事相容,但单月窗口不能排除冲击与仓位因素。
### 机制链 CH-2 · 欧元区通胀加速→(政策反应环证据缺席)→欧元资产与汇率
- 环1 [E1] EA_HICP_YOY 由 2.9(2026-07)经 3.2(2026-08)、3.8(2026-09)至 4.0(2026-10),四个月连续加速,幅度+1.1pp;同期美国口径温和(CPI 派生同比 +0.42pp 至 3.72),欧元区是本轮三个月窗内通胀恶化更快的一端。
- 环2 [E2] 政策反应环: 本报告证据面无 ECB 利率决议/预期序列——该环为【假设】(常规机制推断: 通胀加速或引发紧缩定价与欧债利率上行),无引擎观测可验,不以教科书方向作依据。
  - 缺环注记: 缺失环【假设】: EA 通胀→ECB 政策→欧债利率的传导环在本报告证据面无任何一端的序列(ECB 决议序列与欧元区国债收益率均缺席),整环为假设,区分指标需补采集。
- 环3 [E1] 可观资产端: EURUSD 水平 1.10(2026-11-20),DAX 近一月 -3.28%(2026-10-21→2026-11-20),跌幅较 SPX 的 -10.92% 温和;EZU/FEZ 为美元计价 ETF 代理(is_proxy),不作本土口径引用。
### 机制链 CH-3 · 日本渐进收紧→日元与日股(与全球风险-off 并列的竞争通道)
- 环1 [E1] JP_POLICY_RATE 十二个月净 +67bp(0.557→1.227),最近一段 2026-09/10 两格 +7/+18bp;USDJPY 水平 159.71(2026-11-20),NIKKEI225 近一月 -12.67%(2026-10-21→2026-11-20),跌幅居主要股指最深。 官方实录面: 政策目标 1.25%(决议 2026-09-18、生效 2026-09-24,2026-10-30 确认维持,距截止 58 天/64 天)——月均 1.227 为其平滑印证。
- 环2 [E3] 机制环: 「加息→日元升值→出口与风险资产承压」为教科书叙事,其中利率→汇率渠道在本引擎 transmission_edges 属近零证据渠道,不得作方向依据;当前 USDJPY 仍在 159.71 高位,汇率并未给出升值印证——日股深跌更可能由全球风险-off 同步驱动(同月 SPX -10.92%、VIX +115.17%)。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### S1-通胀黏性与高实际利率延续 · 角色=基准(主通道延续)
- 情景: 假设(非预测): 欧美通胀黏性延续(欧元区高位徘徊、美国温和上行),日本延续渐进收紧,实际利率维持高位,增长温和降温但不衰退。
- 资产方向: 风险资产估值承压(SPX/NDX/NIKKEI225)、VIX 中枢抬升、DXY 偏强;GOLD_F 对高实际利率弹性最大、续承压;UST_10Y 名义受盈亏平衡压制而涨幅有限。 | 置信档: 有相关证据
- 敏感变量: BEI_10Y, EA_HICP_YOY
- 证伪: 指标=TIPS_10Y | 阈值=TIPS_10Y 月末值自 2026-11 的 2.88 回落至 2.40 下方并连续两个月维持(实际利率趋势性下行即推翻本情景主通道) | 次级=BEI_10Y
- 触发: BEI_10Y 月末维持 2.2 附近或以下(紧缩继续由实际利率承载)且 JP_POLICY_RATE 月均再抬升一格(较前值 +7bp 以上) | 期限: 2027-05-21
### S2-通胀快速回落→宽松重定价 · 角色=反例(与基准并列检验)
- 情景: 假设(非预测): 欧元区与美国通胀快速回落(基数或供给修复主导),市场转向宽松定价,重演 2025-03 锚点之后风险资产与黄金上行的历史相似路径(引擎类比距离第二的候选锚)。
- 资产方向: 股指与黄金反弹、DXY 走弱、VIX 回落(历史相似样本 2025-03 锚后 12 个月 SPX +16.33%、GOLD_F +48.83%、DXY -4.08%,事后记录非预测)。 | 置信档: 有历史相似证据
- 敏感变量: EA_HICP_YOY, CPI
- 证伪: 指标=EA_HICP_YOY | 阈值=EA_HICP_YOY 升破 4.5 并连续两个月维持(欧元区通胀加速失控,宽松重定价前提失效)
- 触发: EA_HICP_YOY 与 CPI(引擎派生同比口径)连续两个月回落,且 VIX 月末回落至 25 下方 | 期限: 2027-05-21

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
| 21 | snapshot_fact | UST_30Y@2026-11-19 |  |
| 22 | snapshot_fact | TIPS_5Y@2026-11-19 |  |
| 23 | snapshot_fact | TIPS_10Y@2026-11-19 |  |
| 24 | snapshot_fact | BEI_5Y@2026-11-20 |  |
| 25 | snapshot_fact | BEI_10Y@2026-11-20 |  |
| 26 | snapshot_fact | CURVE_2S10S@2026-11-20 |  |
| 27 | snapshot_fact | CPI@2026-10-01 |  |
| 28 | snapshot_fact | CORE_PCE@2026-09-01 |  |
| 29 | snapshot_fact | UNEMPLOYMENT@2026-10-01 |  |
| 30 | snapshot_fact | CORE_CPI@2026-10-01 |  |
| 31 | snapshot_fact | UST_5Y@2026-11-19 |  |
| 32 | snapshot_fact | INDPRO@2026-10-01 |  |
| 33 | snapshot_fact | US_REAL_GDP@2026-07-01 |  |
| 34 | snapshot_fact | SHCOMP@2026-11-20 |  |
| 35 | snapshot_fact | HSI@2026-11-20 |  |
| 36 | snapshot_fact | NIKKEI225@2026-11-20 |  |
| 37 | snapshot_fact | EA_HICP_YOY@2026-10-01 |  |
| 38 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 39 | s3_envelope | SZCI@2026-11-20 |  |
| 40 | s3_envelope | CHINEXT@2026-11-20 |  |
| 41 | s3_envelope | HSCEI@2026-11-20 |  |
| 42 | s3_envelope | NVDA@2026-11-20 |  |
| 43 | s3_envelope | AAPL@2026-11-20 |  |
| 44 | s3_envelope | MSFT@2026-11-20 |  |
| 45 | s3_envelope | TLT@2026-11-20 |  |
| 46 | s3_envelope | IEF@2026-11-20 |  |
| 47 | s3_envelope | SHY@2026-11-20 |  |
| 48 | s3_envelope | HYG@2026-11-20 |  |
| 49 | s3_envelope | LQD@2026-11-20 |  |
| 50 | s3_envelope | GBPUSD@2026-11-20 |  |
| 51 | s3_envelope | WTI_F@2026-11-20 |  |
| 52 | s3_envelope | GLD@2026-11-20 |  |
| 53 | s3_envelope | USO@2026-11-20 |  |
| 54 | s3_envelope | EEM@2026-11-20 |  |
| 55 | s3_envelope | EZU@2026-11-20 |  |
| 56 | s3_envelope | FEZ@2026-11-20 |  |
| 57 | s3_envelope | EWU@2026-11-20 |  |
| 58 | s3_envelope | EWG@2026-11-20 |  |
| 59 | s3_envelope | EWJ@2026-11-20 |  |
| 60 | s3_envelope | INDA@2026-11-20 |  |
| 61 | s3_envelope | FXI@2026-11-20 |  |
| 62 | s3_envelope | BTC@2026-11-19 |  |
| 63 | s3_envelope | HY_IG_DIFF@2026-11-19 |  |

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


## 质量状态(Audit-R1 F02 四态+Audit-R2 绑定面+Audit-R4 贯通面)

- generated: true(FULL_REPORT 完整装配: L1+L2+L3/L4 全文内联+证据索引)
- machine_verified: True(L3∧L4 produced+纪律校验过+底座非降级或 optional 级显式降级随档)
- run 门(Audit-R4 条目5): blocked_class=map_core_dimension_missing degraded_ok=False
- review: required=True seat_invoked=True verdict=UPHELD fresh=True error=None 修订链档数=2
- copies_consistent(多副本一致): True(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前确定性装配)
- deliverable(可交付): False
- 内容绑定(Audit-R4 条目2): content_sha256=canonical(report.json 剥离 semantic_review)+canonical(agent_judgment.json)+canonical(views_digest.json)——机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。
