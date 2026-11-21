# 完整研究报告(一键研究 MVP)

- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- run_ok: True | 证据行: 72 | run.ts_utc: 20261120T072551Z

## L1 事实层(引擎确定性产出)

| 指标 | 值 | 单位 | 观测日 | 质量 | 证据 ref |
|---|---|---|---|---|---|
| SPX | 7175.83 | index_point | 2026-11-19 | PASS | SPX@2026-11-19 |
| NDX | 26517.05 | index_point | 2026-11-19 | PASS | NDX@2026-11-19 |
| RUT | 2655.11 | index_point | 2026-11-19 | PASS | RUT@2026-11-19 |
| DXY | 103.8 | index_point | 2026-11-20 | PASS | DXY@2026-11-20 |
| EURUSD | 1.1 | usd_per_eur | 2026-11-20 | PASS | EURUSD@2026-11-20 |
| GOLD_F | 3547.5 | usd_per_oz | 2026-11-20 | PASS | GOLD_F@2026-11-20 |
| SILVER_F | 41.78 | usd_per_oz | 2026-11-20 | PASS | SILVER_F@2026-11-20 |
| BRENT_F | 89.56 | usd_per_barrel | 2026-11-20 | PASS | BRENT_F@2026-11-20 |
| VIX | 28.44 | index_point | 2026-11-19 | PASS | VIX@2026-11-19 |
| DAX | 25463.81 | index_point | 2026-11-19 | PASS | DAX@2026-11-19 |
| CAC40 | 8080.74 | index_point | 2026-11-19 | PASS | CAC40@2026-11-19 |
| USDJPY | 159.15 | jpy_per_usd | 2026-11-20 | PASS | USDJPY@2026-11-20 |
| USDCNY | 6.67 | cny_per_usd | 2026-11-20 | PASS | USDCNY@2026-11-20 |
| HY_OAS | 3.47 | percentage_point | 2026-11-18 | PASS | HY_OAS@2026-11-18 |
| BB_OAS | 2.05 | percentage_point | 2026-11-18 | PASS | BB_OAS@2026-11-18 |
| B_OAS | 3.73 | percentage_point | 2026-11-18 | PASS | B_OAS@2026-11-18 |
| CCC_OAS | 13.53 | percentage_point | 2026-11-18 | PASS | CCC_OAS@2026-11-18 |
| IG_OAS | 0.93 | percentage_point | 2026-11-18 | PASS | IG_OAS@2026-11-18 |
| UST_2Y | 4.8 | percent | 2026-11-18 | PASS | UST_2Y@2026-11-18 |
| UST_10Y | 5.07 | percent | 2026-11-18 | PASS | UST_10Y@2026-11-18 |
| UST_30Y | 5.41 | percent | 2026-11-18 | PASS | UST_30Y@2026-11-18 |
| TIPS_5Y | 2.66 | percent | 2026-11-18 | PASS | TIPS_5Y@2026-11-18 |
| TIPS_10Y | 2.88 | percent | 2026-11-18 | PASS | TIPS_10Y@2026-11-18 |
| BEI_5Y | 2.22 | percent | 2026-11-19 | PASS | BEI_5Y@2026-11-19 |
| BEI_10Y | 2.16 | percent | 2026-11-19 | PASS | BEI_10Y@2026-11-19 |
| CURVE_2S10S | 0.28 | percentage_point | 2026-11-19 | PASS | CURVE_2S10S@2026-11-19 |
| CPI | 337.476 | index_point_1982_84 | 2026-10-01 | WARN | CPI@2026-10-01 |
| CORE_PCE | 130.902 | index_point_2017 | 2026-09-01 | DEGRADED | CORE_PCE@2026-09-01 |
| UNEMPLOYMENT | 4.1 | percent | 2026-10-01 | WARN | UNEMPLOYMENT@2026-10-01 |
| CORE_CPI | 339.9 | index_point_1982_84 | 2026-10-01 | WARN | CORE_CPI@2026-10-01 |
| UST_5Y | 4.89 | percent | 2026-11-18 | PASS | UST_5Y@2026-11-18 |
| INDPRO | 103.3954 | index_point_2017 | 2026-10-01 | WARN | INDPRO@2026-10-01 |
| US_REAL_GDP | 24611.077 | billion_usd | 2026-07-01 | DEGRADED | US_REAL_GDP@2026-07-01 |
| SHCOMP | 3577.6174 | index_point | 2026-11-19 | PASS | SHCOMP@2026-11-19 |
| HSI | 22369.58 | index_point | 2026-11-20 | PASS | HSI@2026-11-20 |
| CN_LPR_1Y | 3.0 | percent | 2026-11-20 | WARN | CN_LPR_1Y@2026-11-20 |
| CN_CPI_YOY | 0.7 | percent | 2026-10-31 | WARN | CN_CPI_YOY@2026-10-31 |
| CN_PPI_YOY | 5.7 | percent | 2026-10-31 | WARN | CN_PPI_YOY@2026-10-31 |
| CN_PMI_MFG | 49.3 | index_point | 2026-10-01 | WARN | CN_PMI_MFG@2026-10-01 |
| DFF | 3.88 | percent | 2026-11-18 | PASS | DFF@2026-11-18 |
| DFEDTARU | 4.0 | percent | 2026-11-19 | PASS | DFEDTARU@2026-11-19 |
| NIKKEI225 | 59444.21 | index_point | 2026-11-19 | PASS | NIKKEI225@2026-11-19 |
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
### CON-1 · 四地环境走位综合:美国由降息周期转为重新加息(有效联邦基金利率最新为 3.88%),中国生产价格强再通胀(CN_PPI_YOY 最新为 5.7%),欧元区通胀连续上行并伴随两次加息(HICP 同比最新为百分之四),日本全年持续上调政策利率(JP_POLICY_RATE 最新月均为 1.227%)——全球宏观从一年前的分化格局走向通胀实现值普遍上行与政策普遍转紧。数据不可得面如实在场:日本政策目标序列不在注册表,美国 CPI 最新一期缺基期格同比不可得,欧元区与日本实际 GDP 末观测滞后标注。
- 依据: 证据: 快照事实行 DFEDTARU、CN_PPI_YOY、EA_HICP_YOY、JP_POLICY_RATE、ECB_DFR;政策决议日与生效日见引擎政策事件簇与政策口径四分面。
- 竞争性解释: 解释一(共同冲击): 全球能源与商品价格共同冲击推动四地通胀实现值同窗上行,央行后顾型响应转向紧缩——若如此,三地通胀同月转折是共同原因的结果,能源价格应同窗大涨(引擎面 BRENT_F 同窗观测支持此解释)
- 竞争性解释: 解释二(中国出口链): 中国生产价格经出口商品链向外传导——若如此,中国 PPI 应领先美欧 CPI 转折;但月频证据下三地同月转折、先后未定,该解释与解释一暂不可分
- 竞争性解释: 解释三(各地独立因素叠加): 美国财政/关税、欧元区能源、日本工资等本国因素碰巧同期共振——引擎无分项成因序列,此解释不可验,列为备选
### CON-2 · 证据最充分的机制环节在利率结构:美债名义利率过去十二个月的上行几乎全部由实际利率贡献(UST_10Y 最新为 5.07%,TIPS_10Y 为 2.88%),盈亏平衡分量十二个月净变动接近零——这与「央行响应已实现通胀、市场通胀预期保持锚定」的解释相容,而与「通胀预期失控」叙事不相容;同期风险资产与贵金属回调、美元走强(VIX 最新处于高位)。
- 依据: 证据: 快照事实行 UST_10Y、TIPS_10Y、BEI_10Y、VIX、DXY、SPX、GOLD_F;三利率共同交易日同窗分解(年度窗与月度窗数值)见读者报告美债三利率分解节,本句不重复数字。
- 竞争性解释: 主解释(政策渠道): 央行紧缩叠加期限溢价推升实际利率——若如此,实际利率上行应集中于决议窗口附近,且盈亏平衡保持平稳(引擎面十二个月分解与此一致)
- 竞争性解释: 竞争解释A(财政/供给): 储蓄-投资平衡与债券供给放量推升实际利率——若如此,实际利率上行应分布于非决议期并与发行日历相关(引擎无发行日历序列,两解释的窗口预测尚不能区分)
- 竞争性解释: 竞争解释B(增长预期上修): 实际利率上行反映增长预期改善——若如此,增长指标改善应与实际利率上行同现;日本与欧元区增长改善与此相容,该解释未被排除
### CON-3 · 历史结构对照:六维等权状态距离最近的三个候选月为二零二五年三月、二零二二年六月与二零二三年十月;三者事后路径分歧明显——二零二五年三月与二零二三年十月候选之后股与金双上涨、美债利率大致走平,而二零二二年六月候选之后三个月股金双下跌、美债利率大幅上行。TOP-N 独立簇事后同向度在多个资产-期限组合仅约六成,候选间事后走向存在分歧,任何单一候选的外推都须降级使用(对照资产=SPX/GOLD_F/DXY/UST_10Y 当前观测)。
- 依据: 证据: 快照事实行 SPX、GOLD_F、DXY、UST_10Y;三候选事后块(锚月后一/三/六/十二个月,窗口两端实测日随行)见引擎 analog 面;披露语随行:相似不等于因果更非预测,距离分位不是概率。
- 竞争性解释: 解释一(距离优先): 距离最近的候选(二零二五年三月)事后表现对外推参考权重最高——若如此,软着陆后风险资产续涨是基准参照
- 竞争性解释: 解释二(结构分量优先): 本次锚点的利率维与波动维贡献占主导,更接近二零二二年六月候选的紧缩结构——若如此,未来一个季度金融条件收紧与股债双压风险更高
- 竞争性解释: 解释三(方法警示): 六维等权距离对特征选择敏感,信用维贡献为零且部分特征维缺席,排序不稳健——类比只作历史记录引用,不构成预测依据
### 机制链 MECH-1 · 全球再通胀→央行转紧→实际利率上行→风险资产承压(主链)
- 环1 [E1] 冲击环:三地通胀实现值同窗转折——中国 PPI 同比由二零二六年二月的负零点九转升至五月的三点九(十月已至五点七),美国 CPI 同比二点四三四升至四点一六六六,欧元区 HICP 一点九升至三点二;月频分辨率下三地先后未定。
- 环2 [E2] 国际传导环(冲击→各国消费通胀):引擎无出口价格、贸易流与通胀分项序列,此环因果为【假设】;区分指标 BRENT_F 同窗月末大涨(二零二六年二月末至五月末上行百分之二十七点零零零六),观测支持能源共同冲击解释而非中国出口链独家传导。
  - 缺环注记: 本引擎无出口价格/贸易流/通胀分项序列,冲击向各国消费通胀的传导为【假设】;能源共同冲击与中国出口链两解释以 BRENT_F 同窗观测对质,当前观测方向与前者一致
- 环3 [E1] 政策环:欧央行二零二六年六月十一日决议加息二十五个基点、九月十日再加息二十五个基点,美联储九月十六日决议加息二十五个基点(此前二零二五年十二月十日曾决议降息二十五个基点)——决议日口径可排序:欧央行先于美联储转向;月频宏观数值是统计期值,不得按发布日做事件研究。
- 环4 [E1] 利率结构环:十二个月窗名义上行九十五个基点=实际上行一百零三个基点+盈亏平衡净降八个基点(共同交易日同窗,恒等残差为零)——名义上行全由实际利率贡献,盈亏平衡不是主贡献分量。
- 环5 [E2] 资产定价环:实际利率上行收紧金融条件→风险资产与无息贵金属承压、美元走强——近一月 SPX 与 GOLD_F 回调、DXY 走强、VIX 冲高与 TIPS_10Y 同窗共存(方向与主解释一致,单月窗样本不足以确立因果),整环贴现率传导为【假设】。
  - 缺环注记: 引擎无仓位/流动性/风险溢价分解序列,贴现率传导至资产定价的环内因果为【假设】;同窗方向一致性为 E1 事实,因果归因不可证
### 机制链 MECH-2 · 日本独立加息周期:通胀回升→持续加息→汇率与股市(背离链)
- 环1 [E1] 日本通胀回升环:东京 CPI 同比由二零二六年六月的一点六升至九月的二点六九,全国 CPI 由七月的一点九七回升至十月的二点四四。
- 环2 [E1] 政策环:无担保隔夜拆借利率(月均)由二零二五年十月的零点四七七升至二零二六年十月的的一点二二七,月度台阶(零点五五七/零点七二八/零点八四一/零点九七八/一点零四三/一点二二七)显示多次上调——市场月均口径,决议意图归因不可验。
- 环3 [E3] 汇率-股市环:日本持续加息与日元温和走弱并存(USDJPY 十二个月月末口径上行百分之一点八三五一,未随加息回落——与汇率防御叙事相左、与利差叙事相容),日经近一月与全球股指同幅回调——本国加息与全球风险偏好两归因不可分,此环为【假设】,证伪指标=NIKKEI225。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### SCN-A · 角色=基准情景
- 情景: 假设(非预测):美欧央行对已实现通胀继续紧缩,中国 PPI 维持高位,通胀实现值续升而市场盈亏平衡保持平稳——延续「实际利率上行+金融条件收紧」结构。
- 资产方向: 风险资产(SPX/NIKKEI225)与贵金属(GOLD_F)承压、美元(DXY)偏强、实际利率(TIPS_10Y)趋升——条件式方向判断,假设非预测 | 置信档: 有相关证据
- 敏感变量: TIPS_10Y, EA_HICP_YOY
- 证伪: 指标=BEI_10Y | 阈值=BEI_10Y 收于 2.8% 上方(较当前 2.16 上升超过 0.6 个百分点)且维持两个月——盈亏平衡趋势上行则本情景的「预期稳定」前提失效 | 次级=TIPS_10Y
- 触发: 欧央行或美联储再决议加息至少 25bp,且 EA_HICP_YOY 升破 4.5% 或美国最近有效 CPI 同比高于 4.2% | 期限: 2027-02-20
### SCN-B · 角色=反例情景
- 情景: 假设(非预测):全球增长放缓主导(美国工业与就业走弱、中国 PPI 回落),美欧央行停止紧缩并转向——切向「增长担忧+宽松预期」结构。
- 资产方向: 风险资产修复、美元走弱、黄金反弹、美债收益率下行——条件式方向判断;历史相似参照(历史记录,相似不等于预测):二零二三年十月候选事后十二个月 SPX +36.04%、UST_10Y -0.60pp、GOLD_F +37.86% | 置信档: 有历史相似证据
- 敏感变量: UNEMPLOYMENT, CN_PPI_YOY
- 证伪: 指标=EA_HICP_YOY | 阈值=EA_HICP_YOY 连续两个月不低于 4.5%(当前 4.0)——通胀续升则宽松转向假设失效 | 次级=DFEDTARU
- 触发: 美联储决议降息至少 25bp,或美国失业率高于 4.6%(当前 4.1) | 期限: 2027-02-20

## 证据索引

| # | kind | ref | 说明 |
|---|---|---|---|
| 1 | snapshot_fact | SPX@2026-11-19 |  |
| 2 | snapshot_fact | NDX@2026-11-19 |  |
| 3 | snapshot_fact | RUT@2026-11-19 |  |
| 4 | snapshot_fact | DXY@2026-11-20 |  |
| 5 | snapshot_fact | EURUSD@2026-11-20 |  |
| 6 | snapshot_fact | GOLD_F@2026-11-20 |  |
| 7 | snapshot_fact | SILVER_F@2026-11-20 |  |
| 8 | snapshot_fact | BRENT_F@2026-11-20 |  |
| 9 | snapshot_fact | VIX@2026-11-19 |  |
| 10 | snapshot_fact | DAX@2026-11-19 |  |
| 11 | snapshot_fact | CAC40@2026-11-19 |  |
| 12 | snapshot_fact | USDJPY@2026-11-20 |  |
| 13 | snapshot_fact | USDCNY@2026-11-20 |  |
| 14 | snapshot_fact | HY_OAS@2026-11-18 |  |
| 15 | snapshot_fact | BB_OAS@2026-11-18 |  |
| 16 | snapshot_fact | B_OAS@2026-11-18 |  |
| 17 | snapshot_fact | CCC_OAS@2026-11-18 |  |
| 18 | snapshot_fact | IG_OAS@2026-11-18 |  |
| 19 | snapshot_fact | UST_2Y@2026-11-18 |  |
| 20 | snapshot_fact | UST_10Y@2026-11-18 |  |
| 21 | snapshot_fact | UST_30Y@2026-11-18 |  |
| 22 | snapshot_fact | TIPS_5Y@2026-11-18 |  |
| 23 | snapshot_fact | TIPS_10Y@2026-11-18 |  |
| 24 | snapshot_fact | BEI_5Y@2026-11-19 |  |
| 25 | snapshot_fact | BEI_10Y@2026-11-19 |  |
| 26 | snapshot_fact | CURVE_2S10S@2026-11-19 |  |
| 27 | snapshot_fact | CPI@2026-10-01 |  |
| 28 | snapshot_fact | CORE_PCE@2026-09-01 |  |
| 29 | snapshot_fact | UNEMPLOYMENT@2026-10-01 |  |
| 30 | snapshot_fact | CORE_CPI@2026-10-01 |  |
| 31 | snapshot_fact | UST_5Y@2026-11-18 |  |
| 32 | snapshot_fact | INDPRO@2026-10-01 |  |
| 33 | snapshot_fact | US_REAL_GDP@2026-07-01 |  |
| 34 | snapshot_fact | SHCOMP@2026-11-19 |  |
| 35 | snapshot_fact | HSI@2026-11-20 |  |
| 36 | snapshot_fact | CN_LPR_1Y@2026-11-20 |  |
| 37 | snapshot_fact | CN_CPI_YOY@2026-10-31 |  |
| 38 | snapshot_fact | CN_PPI_YOY@2026-10-31 |  |
| 39 | snapshot_fact | CN_PMI_MFG@2026-10-01 |  |
| 40 | snapshot_fact | DFF@2026-11-18 |  |
| 41 | snapshot_fact | DFEDTARU@2026-11-19 |  |
| 42 | snapshot_fact | NIKKEI225@2026-11-19 |  |
| 43 | snapshot_fact | JP_CPI_YOY@2026-10-01 |  |
| 44 | snapshot_fact | ECB_DFR@2026-09-16 |  |
| 45 | snapshot_fact | ECB_MRO@2026-09-16 |  |
| 46 | snapshot_fact | EA_HICP_YOY@2026-10-01 |  |
| 47 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 48 | s3_envelope | SZCI@2026-11-19 |  |
| 49 | s3_envelope | CHINEXT@2026-11-19 |  |
| 50 | s3_envelope | HSCEI@2026-11-20 |  |
| 51 | s3_envelope | NVDA@2026-11-19 |  |
| 52 | s3_envelope | AAPL@2026-11-19 |  |
| 53 | s3_envelope | MSFT@2026-11-19 |  |
| 54 | s3_envelope | TLT@2026-11-19 |  |
| 55 | s3_envelope | IEF@2026-11-19 |  |
| 56 | s3_envelope | SHY@2026-11-19 |  |
| 57 | s3_envelope | HYG@2026-11-19 |  |
| 58 | s3_envelope | LQD@2026-11-19 |  |
| 59 | s3_envelope | GBPUSD@2026-11-20 |  |
| 60 | s3_envelope | WTI_F@2026-11-20 |  |
| 61 | s3_envelope | GLD@2026-11-19 |  |
| 62 | s3_envelope | USO@2026-11-19 |  |
| 63 | s3_envelope | EEM@2026-11-19 |  |
| 64 | s3_envelope | EZU@2026-11-19 |  |
| 65 | s3_envelope | FEZ@2026-11-19 |  |
| 66 | s3_envelope | EWU@2026-11-19 |  |
| 67 | s3_envelope | EWG@2026-11-19 |  |
| 68 | s3_envelope | EWJ@2026-11-19 |  |
| 69 | s3_envelope | INDA@2026-11-19 |  |
| 70 | s3_envelope | FXI@2026-11-19 |  |
| 71 | s3_envelope | BTC@2026-11-18 |  |
| 72 | s3_envelope | HY_IG_DIFF@2026-11-18 |  |

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2025-03 | 0.673446 | 0.0 | rates 48.5%、volatility 32.3% |
| 2 | 2022-06 | 0.794208 | 1.3699 | rates 50.8%、valuation 33.4% |
| 3 | 2023-10 | 0.968894 | 26.0274 | volatility 53.4%、valuation 25.1% |
| 4 | 2021-02 | 1.203292 | 69.863 | rates 82.8%、inflation 8.5% |
| 5 | 2019-12 | 1.280722 | 72.6027 | rates 47.1%、volatility 39.1% |

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
