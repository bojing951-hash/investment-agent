# 完整研究报告(一键研究 MVP)

- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- run_ok: True | 证据行: 71 | run.ts_utc: 20261120T115457Z

## L1 事实层(引擎确定性产出)

| 指标 | 值 | 单位 | 观测日 | 质量 | 证据 ref |
|---|---|---|---|---|---|
| SPX | 7175.83 | index_point | 2026-11-19 | PASS | SPX@2026-11-19 |
| NDX | 26517.05 | index_point | 2026-11-19 | PASS | NDX@2026-11-19 |
| RUT | 2655.11 | index_point | 2026-11-19 | PASS | RUT@2026-11-19 |
| DXY | 103.94 | index_point | 2026-11-19 | PASS | DXY@2026-11-19 |
| EURUSD | 1.1 | usd_per_eur | 2026-11-19 | PASS | EURUSD@2026-11-19 |
| GOLD_F | 3627.9 | usd_per_oz | 2026-11-19 | PASS | GOLD_F@2026-11-19 |
| SILVER_F | 42.83 | usd_per_oz | 2026-11-19 | PASS | SILVER_F@2026-11-19 |
| BRENT_F | 90.05 | usd_per_barrel | 2026-11-19 | PASS | BRENT_F@2026-11-19 |
| VIX | 28.44 | index_point | 2026-11-19 | PASS | VIX@2026-11-19 |
| DAX | 25736.24 | index_point | 2026-11-18 | PASS | DAX@2026-11-18 |
| CAC40 | 8146.83 | index_point | 2026-11-18 | PASS | CAC40@2026-11-18 |
| USDJPY | 159.61 | jpy_per_usd | 2026-11-19 | PASS | USDJPY@2026-11-19 |
| USDCNY | 6.67 | cny_per_usd | 2026-11-19 | PASS | USDCNY@2026-11-19 |
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
| HSI | 22841.62 | index_point | 2026-11-19 | PASS | HSI@2026-11-19 |
| CN_LPR_1Y | 3.0 | percent | 2026-10-20 | WARN | CN_LPR_1Y@2026-10-20 |
| CN_CPI_YOY | 0.7 | percent | 2026-10-31 | WARN | CN_CPI_YOY@2026-10-31 |
| CN_PPI_YOY | 5.7 | percent | 2026-10-31 | WARN | CN_PPI_YOY@2026-10-31 |
| CN_PMI_MFG | 49.3 | index_point | 2026-10-01 | WARN | CN_PMI_MFG@2026-10-01 |
| DFF | 3.88 | percent | 2026-11-18 | PASS | DFF@2026-11-18 |
| DFEDTARU | 4.0 | percent | 2026-11-19 | PASS | DFEDTARU@2026-11-19 |
| NIKKEI225 | 59444.21 | index_point | 2026-11-19 | PASS | NIKKEI225@2026-11-19 |
| ECB_DFR | 2.5 | percent | 2026-09-16 | DEGRADED | ECB_DFR@2026-09-16 |
| ECB_MRO | 2.65 | percent | 2026-09-16 | DEGRADED | ECB_MRO@2026-09-16 |
| EA_HICP_YOY | 1.9 | percent | 2025-12-01 | DEGRADED | EA_HICP_YOY@2025-12-01 |
| JP_POLICY_RATE | 1.227 | percent | 2026-10-01 | WARN | JP_POLICY_RATE@2026-10-01 |

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=False n=None 隔离=None
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)

## L3 AI 推断层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### CON-1 · 过去一年美债长端收益率上行主要由实际利率分量而非通胀预期分量驱动;近一月盈亏平衡通胀回落与名义利率回落并存。
- 依据: 引擎共同交易日三利率分解(us_rates_trio 面):十二个月窗名义上行的量级几乎全部由实际利率分量贡献,盈亏平衡分量为负;近一月窗名义回落的同时实际利率仍在上行、盈亏平衡快速回落。归档强渠道支持名义-实际同动读法(通胀保值债券与名义美债的日度变化相关系数为强正,E1,QB-20261110-022)。
- 竞争性解释: 主解释(实际利率驱动):央行再收紧叠加增长韧性推高实际利率,长端是实际利率现象——与名义-实际强共动边一致(E1)
- 竞争性解释: 竞争解释A(期限溢价/财政供给驱动):长端上行源于债券供给与期限溢价,与货币政策无关——本引擎无期限溢价序列,该环【假设】不可验
- 竞争性解释: 竞争解释B(通胀预期驱动):盈亏平衡应主导长端——但十二个月窗盈亏平衡分量为负,量级上数据不支持该解释成立
### CON-2 · 近一月美日中股市回调与波动急升、美元走强、黄金大跌并存(欧元区股指逆势上行);风险偏好收缩是数据支持最充分的统一解释。
- 依据: 近一月波动率指数与股指反向共动、美元指数上行与黄金回落同现(引擎月窗资产面);归档强渠道:波动率与股指、股指与高收益利差均为强负共动,美元指数与黄金期货亦为归档负相关渠道(数值与窗见机制链 M1 第 4 环,均 E1,QB-20261110-022);CCC 级利差绝对水平高企。
- 竞争性解释: 主解释(风险偏好/美元流动性渠道):波动升→股指与信用承压,美元流动性收紧→黄金承压——与三条强渠道符号一致(E1)
- 竞争性解释: 竞争解释A(增长担忧渠道):若衰退担忧主导,长端利率应大幅下行而波动不必领涨——但十年期美债近一月仅小幅回落、工业生产同比走强、失业率平稳,增长数据暂不支持
- 竞争性解释: 竞争解释B(黄金独立定价:通胀预期回落驱动):盈亏平衡近一月确有回落,但黄金×盈亏平衡渠道在本地数据近零(r=+0.0255,E1 归档),通胀预期渠道不支持作方向依据
### CON-3 · 日本无担保隔夜拆借利率最新月均为 1.227%,十二个月大幅正常化,而日元兑美元仍处弱势——教科书利差渠道(变化量口径)在本地数据近零,不能作为日元走势的方向依据(利差水平机制本引擎不可验)。
- 依据: 引擎月均口径序列显示日本隔夜利率自上年前值持续抬升至最新 1.227%;而美元兑日元处于高位。归档边:美元兑日元分别与美债长端、短端利率的日度变化相关系数均近零,波动率与美元兑日元的相关系数亦近零(均近零渠道,E1,QB-20261110-022)——利率渠道与风险偏好→carry 渠道两条教科书链均被本地数据拒绝作方向依据。
- 竞争性解释: 主解释(渠道近零=放弃单因子叙事):日元驱动应按多因子观察,任何单一利率渠道在本地数据均不支持——数据保守读法
- 竞争性解释: 竞争解释A(利差水平而非变化主导):利差绝对水平仍大,正常化的变化量级不足以扭转方向——与近零相关并不矛盾,但水平机制本引擎无法验证【尚未验证】
- 竞争性解释: 竞争解释B(结构性资本流出驱动):日元弱势由流量(并购/再配置)而非价格驱动——无在册序列,【假设】
### CON-4 · 中国出现工厂通胀高企与消费通胀低迷并存的剪刀差:中国PPI同比 5.7%,中国CPI同比 0.7%。
- 依据: 两点值均为 2026-10-31 快照单点(历史序列不可得,检索范围=快照 series_store+注册表采集档通道,不可作趋势断言);制造业PMI 同比年内转正但绝对水平仍处荣枯线下方(49.3,2026-10)——修复与剪刀差并存。
- 竞争性解释: 主解释(成本冲击未传导至消费端):上游价格由供给与外需驱动,国内消费需求偏弱吸收不足——【推断】
- 竞争性解释: 竞争解释A(内需疲弱主导):CPI 低迷是主信号,PPI 高企由外部大宗与出口需求驱动,内需不足与 PMI 偏弱一致
- 竞争性解释: 竞争解释B(基数/口径效应):单月剪刀差可能是基数错位——单点数据无法排除,须历史序列验证【尚未验证】
### 机制链 M1 · 通胀再加速→政策再收紧→实际利率上行→风险偏好收缩
- 环1 [E1] 始发冲击:美国CPI同比自 2026-02 低点至 2026-05 急升(引擎转折候选面 2.434→4.1666,同比空间),核心PCE同比三锚点连升(2.85→3.04→3.12)——通胀再加速
- 环2 [E1] 通胀-政策历史共动(CORE_PCE×FED_FUNDS 月网格 r=+0.422,归档边 COREPCE-FEDFUNDS,E1):政策再收紧落地——美联储 2026-09-16 决议加息(上限 3.75→4.0,次日生效),欧央行 2026-06-11 与 2026-09-10 两度决议加息(存款便利 2.0→2.5)
- 环3 [E1] 名义-实际利率同动(r=+0.8278,归档边 TIPS10Y-UST10Y,E1):十年期美债十二个月 +95bp 中实际利率 +103bp、盈亏平衡 -8bp(共同交易日窗 2025-11-18→2026-11-18)——紧缩主要落在实际利率而非通胀预期
- 环4 [E1] 风险偏好内环与美元-黄金渠道(VIX×SPX r=-0.7138、SPX×HY_OAS r=-0.6318、DXY×GOLD_F r=-0.3935,均 E1 归档强渠道):近一月 SPX -6.96%、VIX +64.3%、DXY +2.17%、GOLD_F -12.42%(引擎月窗 2026-10-20→2026-11-19)与该结构方向一致
- 环5 [E2] 机制分辨:『实际利率→股指估值』的直接久期渠道在本地数据近零(NDX×UST_10Y r=+0.0586,归档近零渠道档)——第 4 环联动更可能经由风险偏好内环而非久期渠道;该分辨含推断成分
  - 缺环注记: 本引擎无估值-利率因果序列,『经由风险偏好而非久期』的机制分辨含【假设】成分,仅以两条渠道的相关差为据
### 机制链 M2 · 全球政策同步簇与日本正常化的传导
- 环1 [E1] 日本无担保隔夜拆借月均十二个月 +0.75 个百分点(0.477→1.227),节奏为四地最快;转折窗 2026-04→2026-07(0.727→0.978)
- 环2 [E1] 政策事件簇(引擎 policy_event_clusters):欧央行 2026-06-11 决议 +25bp(6-17 生效)、2026-09-10 决议 +25bp(9-16 生效);美联储 2026-09-16 决议 +25bp(9-17 生效)——九月欧美决议日落在 ±7 日窗内,构成同一全球政策事件(POLCLUSTER-03,跨国产合并计数)
- 环3 [E3] 日本加息向日元的传导:变化量口径下教科书利差渠道在本地数据近零(USDJPY×UST_10Y r=+0.0313、×UST_2Y r=+0.0064、VIX×USDJPY r=-0.0238,E1 近零档)——不能以该渠道作为日元走势的方向依据(日元弱势 USDJPY 159.61 另有驱动);利差水平机制与替代机制(贸易条件/资本流)本引擎无序列可验

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### SCN-A · 角色=基准情景
- 情景: 【假设非预测】美国通胀顽固:核心通胀维持当前区带上方,美联储将目标区间上限维持在 4.0%、实际利率续处高位,金融条件难松
- 资产方向: 美股承压、高波动延续,高收益与 CCC 级信用利差走阔风险 | 置信档: 有相关证据
  - 依据: 风险偏好内环(VIX×SPX r=-0.7138、SPX×HY_OAS r=-0.6318,E1)下,波动高位与股指弱势、信用走阔同现的结构延续概率较高——相关证据支持方向,非因果,非预测
- 敏感变量: VIX, CORE_PCE
- 证伪: 指标=CPI | 阈值=美国CPI同比(引擎派生口径)连续两个月回落至 3.0% 以下——通胀顽固假设被证伪 | 次级=CORE_PCE
- 触发: 2027-02-15 前发布的最近一期 CPI 同比仍在 3.5% 或以上(紧缩延续条件成立) | 期限: 2027-02-15
### SCN-B · 角色=反例情景
- 情景: 【假设非预测】通胀回落+政策转松:供给扰动消退带动通胀回落,美联储重启降息,实际利率见顶回落(近一月盈亏平衡 -16bp 与名义 -8bp 的组合若延续为趋势)
- 资产方向: 美股修复上行,黄金再度走强 | 置信档: 有历史相似证据
  - 依据: 历史相似段事后记录(analog 事后块,历史记录非预测):2023-10 簇事后十二个月 SPX +36.04%、GOLD_F +37.86%;2025-03 簇事后十二个月 SPX +16.33%、GOLD_F +48.83%——且 TOP-N 三个月窗方向分歧(符号一致率 0.6),外推须降级
- 敏感变量: BEI_10Y, TIPS_10Y
- 证伪: 指标=TIPS_10Y | 阈值=TIPS_10Y 收盘升破 3.20%——实际利率再上新台阶,『通胀回落+利率见顶』假设被证伪
- 触发: 2027-06-30 前 TIPS_10Y 回落至 2.60% 以下且 BEI_10Y 回升至 2.00% 以上(转松组合成立) | 期限: 2027-06-30

## 证据索引

| # | kind | ref | 说明 |
|---|---|---|---|
| 1 | snapshot_fact | SPX@2026-11-19 |  |
| 2 | snapshot_fact | NDX@2026-11-19 |  |
| 3 | snapshot_fact | RUT@2026-11-19 |  |
| 4 | snapshot_fact | DXY@2026-11-19 |  |
| 5 | snapshot_fact | EURUSD@2026-11-19 |  |
| 6 | snapshot_fact | GOLD_F@2026-11-19 |  |
| 7 | snapshot_fact | SILVER_F@2026-11-19 |  |
| 8 | snapshot_fact | BRENT_F@2026-11-19 |  |
| 9 | snapshot_fact | VIX@2026-11-19 |  |
| 10 | snapshot_fact | DAX@2026-11-18 |  |
| 11 | snapshot_fact | CAC40@2026-11-18 |  |
| 12 | snapshot_fact | USDJPY@2026-11-19 |  |
| 13 | snapshot_fact | USDCNY@2026-11-19 |  |
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
| 35 | snapshot_fact | HSI@2026-11-19 |  |
| 36 | snapshot_fact | CN_LPR_1Y@2026-10-20 |  |
| 37 | snapshot_fact | CN_CPI_YOY@2026-10-31 |  |
| 38 | snapshot_fact | CN_PPI_YOY@2026-10-31 |  |
| 39 | snapshot_fact | CN_PMI_MFG@2026-10-01 |  |
| 40 | snapshot_fact | DFF@2026-11-18 |  |
| 41 | snapshot_fact | DFEDTARU@2026-11-19 |  |
| 42 | snapshot_fact | NIKKEI225@2026-11-19 |  |
| 43 | snapshot_fact | ECB_DFR@2026-09-16 |  |
| 44 | snapshot_fact | ECB_MRO@2026-09-16 |  |
| 45 | snapshot_fact | EA_HICP_YOY@2025-12-01 |  |
| 46 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 47 | s3_envelope | SZCI@2026-11-19 |  |
| 48 | s3_envelope | CHINEXT@2026-11-19 |  |
| 49 | s3_envelope | HSCEI@2026-11-19 |  |
| 50 | s3_envelope | NVDA@2026-11-19 |  |
| 51 | s3_envelope | AAPL@2026-11-19 |  |
| 52 | s3_envelope | MSFT@2026-11-19 |  |
| 53 | s3_envelope | TLT@2026-11-19 |  |
| 54 | s3_envelope | IEF@2026-11-19 |  |
| 55 | s3_envelope | SHY@2026-11-19 |  |
| 56 | s3_envelope | HYG@2026-11-19 |  |
| 57 | s3_envelope | LQD@2026-11-19 |  |
| 58 | s3_envelope | GBPUSD@2026-11-19 |  |
| 59 | s3_envelope | WTI_F@2026-11-19 |  |
| 60 | s3_envelope | GLD@2026-11-19 |  |
| 61 | s3_envelope | USO@2026-11-19 |  |
| 62 | s3_envelope | EEM@2026-11-19 |  |
| 63 | s3_envelope | EZU@2026-11-19 |  |
| 64 | s3_envelope | FEZ@2026-11-19 |  |
| 65 | s3_envelope | EWU@2026-11-19 |  |
| 66 | s3_envelope | EWG@2026-11-19 |  |
| 67 | s3_envelope | EWJ@2026-11-19 |  |
| 68 | s3_envelope | INDA@2026-11-19 |  |
| 69 | s3_envelope | FXI@2026-11-19 |  |
| 70 | s3_envelope | BTC@2026-11-18 |  |
| 71 | s3_envelope | HY_IG_DIFF@2026-11-18 |  |

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
- run 门(Audit-R4 条目5): blocked_class=map_core_dimension_missing degraded_ok=False
- review: required=True seat_invoked=True verdict=UPHELD fresh=True error=None 修订链档数=2
- copies_consistent(多副本一致): True(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前确定性装配)
- deliverable(可交付): False
- 内容绑定(Audit-R4 条目2): content_sha256=canonical(report.json 剥离 semantic_review)+canonical(agent_judgment.json)+canonical(views_digest.json)——机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。
