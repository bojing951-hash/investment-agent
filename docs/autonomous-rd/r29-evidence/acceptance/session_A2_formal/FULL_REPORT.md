# 完整研究报告(一键研究 MVP)

- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- run_ok: False | 证据行: 64 | run.ts_utc: 20261121T115838Z

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
### CON-1 · 全球再通胀的来源未决。过去一年美国CPI与欧元区EA_HICP_YOY同比显著走高、日本JP_CPI_YOY降后回升,而增长面(INDPRO同比回升、UNEMPLOYMENT处于低位)不支持单一的需求过热解释;CORE_PCE同比较高但未失控。在『供给/输入型回升』与『需求拉动回升』两类解释之间,当前证据尚不能裁决。
- 依据: 引擎面: 欧元区EA_HICP_YOY与日本JP_CPI_YOY的最新同比读数、美国CORE_PCE同比与UNEMPLOYMENT的最新读数,逐位数值见读者报告走位面锚格回贴(anchor_echo);美国CPI最新锚格同比因缺基期格=不可得(yoy_status=no_same_period_base),水平读数与最近有效同比(观测2026-07)另列于走位面。价格与就业/产出同升而增长未过热,是两类解释都必须容纳的事实。
- 竞争性解释: 解释A(供给/输入型): 若能源、商品与进口价格传导主导,则通胀回升将主要出现在PPI与商品敏感分项,央行收紧对压低通胀的效果弱、时滞长。
- 竞争性解释: 解释B(需求拉动型): 若各经济体需求周期同步走强主导,则通胀回升应伴随产出缺口的收敛与就业的进一步走强,政策收紧应更有效也更必要。
- 竞争性解释: 解释C(通胀预期脱锚的尾部情形): 若市场长期通胀定价随读数系统性上移,则即使需求不过热,通胀也可能自我强化。
### CON-2 · 政策反应函数的分歧未决。欧元区与日本在收紧(ECB_DFR上调、JP_POLICY_RATE连续上行),美国先降后升(引擎政策事件簇面: 美联储2025-12-10降息一次、2026-09-16再加息一次,净变动为零);对『加息主要响应通胀回升』与『加息主要响应汇率与金融稳定考量』两种解释,现有证据不能区分。
- 依据: 引擎面: ECB_DFR最新读数(观测2026-09-16)、JP_POLICY_RATE最新读数(观测2026-10)、EA_HICP_YOY最新读数(观测2026-10)与USDJPY最新读数(观测2026-11-20),逐位数值见读者报告走位面锚格回贴(anchor_echo)。通胀走高与欧央行加息在月频时序上相容(先后不可证),日元偏弱与日本连续加息并存——通胀驱动与利差/汇率驱动两种叙事都容纳这些观测。美国DFEDTARU路径引用自引擎政策事件簇与点值锚格(该指标不在本报告证据索引,此句锚定政策簇面)。
- 竞争性解释: 解释A(通胀响应): 若政策反应函数以通胀为主,则后续加息节奏将跟随通胀读数,通胀回落时政策将转向。
- 竞争性解释: 解释B(汇率/金融稳定响应): 若加息主要出于日元贬值或利差压力等考量,则即使通胀温和,政策也可能继续收紧,且对通胀数据的敏感度低。
- 竞争性解释: 解释C(预防式收紧): 若央行在通胀尚未牢固回落时预防性收紧以保卫信誉,则路径将表现为小幅多次、对单月数据反应钝化。
### CON-3 · 近一月市场急跌的机制未决。SPX大幅回落、VIX大幅抬升、GOLD_F大跌与DXY走强同窗发生,而HY_OAS仅温和走阔、UST_10Y高位小幅回落、CURVE_2S10S维持正值——『利率/流动性冲击压估值』、『增长恐慌』与『仓位去杠杆』三类解释都容纳现有证据,单一叙事不足以裁决。
- 依据: 引擎面(资产月窗观测2026-10-21至2026-11-20,逐项数值见读者报告回贴面asset_returns_echo): HY_OAS、UST_10Y、CURVE_2S10S、BEI_10Y与IG_OAS的最新读数(观测日2026-11-19与2026-11-20)见证据索引行,数值随读者报告披露。信用市场OAS未与股市同步大幅走阔、盈亏平衡通胀并未随行情大跌而飙升,是三类解释都必须处理的事实。
- 竞争性解释: 解释A(利率/流动性冲击): 若高利率与政策再收紧主导,则估值压缩应集中在长久期与高估值资产,黄金与风险资产同跌可由流动性与实际利率解释,信用利差走阔相对滞后。
- 竞争性解释: 解释B(增长恐慌): 若市场定价的是增长转弱,则信用利差应趋势性走阔、周期商品与股市同跌、利率应明显下行而非高位徘徊。
- 竞争性解释: 解释C(仓位去杠杆): 若急跌主要源于杠杆仓位平仓,则波动率与跨资产相关性骤升应先于基本面变化,且行情对消息面过度敏感、利差与利率反应有限。
### 机制链 MC-1 · 
- 环1 [E1] 通胀面同步回升(引擎候选面,2026-02→2026-05,同比空间): 美国CPI 2.434→4.1666、欧元区HICP 1.9→3.2、中国PPI -0.9→3.9;月频证据下三地先后未定,但同窗同向成立。
- 环2 [E2] 政策再收紧(决议日=日频可排序): 欧央行2026-06-11加息25bp(DFR 2.0→2.25)、2026-09-10再加息25bp(→2.5);美联储2026-09-16加息25bp(3.75→4.0;此前2025-12-10曾降息25bp);日本政策利率(月均)由2025-10的0.477升至2026-10的1.227;中国OMO_7D全程1.4未动。
  - 缺环注记: 『加息因通胀回升而触发』这一因果环为【假设】——决议文本与反应函数不在引擎证据面;且本报告证据索引无DFEDTARU/DFF实据行,美国路径锚定引擎政策事件簇面(决议日逐条在档)而非索引实据。
- 环3 [E2] 金融条件收紧与波动抬升并存(资产月窗2026-10-21→2026-11-20): SPX -10.92%、NIKKEI225 -12.67%、VIX 16.68→35.89、GOLD_F -15.29%、DXY +1.99%;UST_10Y 5.04%(2026-11-19)高位、HY_OAS 3.52%(2026-11-19)。
  - 缺环注记: 『高利率压缩估值(经由实际利率)』环节为【假设】——引擎无TIPS实际利率序列,实际利率传导不可直接验证;可验证部分仅为名义利率水平与资产同窗变动。
- 环4 [E3] 黄金大跌与美元走强同窗的组合被解释为流动性/保证金压力: 黄金在股市急跌中未发挥避险功能反而下跌,美元同窗走高,兼容『流动性收紧主导』叙事。
### 机制链 MC-2 · 
- 环1 [E1] 日本通胀降后回升(CPI同比2025-10为2.99→2026-07为1.97→2026-10为2.44;东京CPI同比2026-06 1.6→2026-09 2.69),政策利率(月均)同期由0.477升至1.227。
- 环2 [E2] 若日本通胀继续回升,日央行维持加息节奏,美日短端利差将收敛,日元存在升值(USDJPY下行)压力;USDJPY 2026-11-20为159.707。
  - 缺环注记: 『利差收敛→日元升值』环节为【假设】——引擎无美日实际利差与资本流动序列,该环不可直接验证,为教科书机制的本地数据外推。
- 环3 [E3] 该链的竞争解释: 日元弱势由美国利率居高主导,日本加息幅度不足以扭转利差,USDJPY维持高位。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### SCN-A · 角色=
- 情景: 假设非预测: 全球通胀(尤其美国CPI同比与欧元区HICP)在未来两个季度维持当前高位不回落,美联储与欧央行维持紧缩、不再转向降息。
- 资产方向: 在该假设下,风险资产估值持续承压,SPX等权益指数倾向下行或维持高波动,黄金受高利率与强美元压制,信用利差逐步走阔。 | 置信档: 有历史相似证据
- 敏感变量: CPI, BEI_10Y
- 证伪: 指标=CPI | 阈值=若美国CPI同比(引擎同比空间)在2027-04前回落至3.0以下且连续两个月,本情景失效 | 次级=BEI_10Y,EA_HICP_YOY
- 触发: 未来两次FOMC决议(2026-12与2027-01窗口)任一再度加息,或点阵图中值上移 | 期限: 2027-02-01
### SCN-B · 角色=
- 情景: 假设非预测: 核心通胀延续回落(引擎候选面: 美国CORE_CPI同比2026-05→2026-08由2.8229降至2.4462;CORE_PCE同比最新3.12),市场重新定价降息,美元与名义利率回落、风险资产修复。注: 两核心口径当期背离(CORE_CPI回落vs CORE_PCE同比3.04→3.12上行),本情景前提依赖CORE_CPI口径的延续性,属该情景的敏感前提。
- 资产方向: 在该假设下,若降息预期重建,SPX等风险资产倾向修复、DXY走弱、黄金修复;历史上2025-03相似锚(距离0.968)之后的12个月曾出现SPX +16.33%、GOLD_F +48.83%的组合(事后记录,非预测)。 | 置信档: 有相关证据
- 敏感变量: CORE_PCE, UST_2Y
- 证伪: 指标=CORE_PCE | 阈值=若核心PCE同比在2027-03前升破3.5,本情景失效 | 次级=CORE_CPI
- 触发: 联邦基金期货隐含路径或FOMC点阵图显示2027年内至少两次降息定价 | 期限: 2027-03-31

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
- review: required=True seat_invoked=True verdict=UPHELD fresh=True error=None 修订链档数=2
- copies_consistent(多副本一致): True(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前确定性装配)
- deliverable(可交付): True
- 内容绑定(Audit-R4 条目2): content_sha256=canonical(report.json 剥离 semantic_review)+canonical(agent_judgment.json)+canonical(views_digest.json)——机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。
