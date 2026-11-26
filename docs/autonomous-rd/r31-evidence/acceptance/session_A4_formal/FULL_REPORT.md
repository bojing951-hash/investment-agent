# 完整研究报告(一键研究 MVP)

- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- run_ok: True | 证据行: 72 | run.ts_utc: 20261122T120924Z

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
| USDCNY | 6.66 | cny_per_usd | 2026-11-21 | PASS | USDCNY@2026-11-21 |
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
| SHCOMP | 3533.7929 | index_point | 2026-11-20 | PASS | SHCOMP@2026-11-20 |
| HSI | 22410.8 | index_point | 2026-11-20 | PASS | HSI@2026-11-20 |
| CN_LPR_1Y | 3.0 | percent | 2026-11-20 | WARN | CN_LPR_1Y@2026-11-20 |
| CN_CPI_YOY | 0.7 | percent | 2026-10-31 | WARN | CN_CPI_YOY@2026-10-31 |
| CN_PPI_YOY | 5.7 | percent | 2026-10-31 | WARN | CN_PPI_YOY@2026-10-31 |
| CN_PMI_MFG | 49.3 | index_point | 2026-10-01 | WARN | CN_PMI_MFG@2026-10-01 |
| DFF | 3.88 | percent | 2026-11-19 | PASS | DFF@2026-11-19 |
| DFEDTARU | 4.0 | percent | 2026-11-21 | PASS | DFEDTARU@2026-11-21 |
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
### C1 · 主线综合: 过去12个月(至2026-11-22)四地证据面呈现『通胀再加速→政策再收紧→实际利率上行→风险资产收缩』的同向共动——CPI 与 CORE_PCE 同比走高、EA_HICP_YOY 升至本轮最高、CN_PPI_YOY 自负转正并续创本轮新高、CN_PMI_MFG 于2026年春季一度回升至荣枯线上方后回落至线下、DFF 回到降息前水平、ECB_DFR 两度上调、JP_POLICY_RATE 持续上行、UST_10Y 与 TIPS_10Y 上行而 BEI_10Y 回落、SPX 与 NIKKEI225 与 GOLD_F 近月收缩而 DXY 与 VIX 走高。该共动格局成立;但对『谁驱动谁』至少有三种数据同样容纳的解释(见竞争解释),当前证据不足以在它们之间裁决——区分依赖 BEI_10Y 与 TIPS_10Y 的分解走向、HY_OAS 与 USDJPY 的后续观测(传导面对质三件见 reader_map.transmission)。
- 竞争性解释: 解释A(主链): 通胀再加速(2026-02至2026-05三地共振)迫使央行再收紧,名义利率上行由实际利率主导(12个月实际+102bp),高实际利率压制风险资产估值并推升 DXY、压低 GOLD_F——若成立,BEI_10Y 应大体稳定而 TIPS_10Y 续升
- 竞争性解释: 解释B(增长担忧): 风险资产收缩主要由增长预期下修驱动(美国工业同比一度折半、GDP 同比放缓),利率变化是结果而非原因——若成立,BEI_10Y 应主导性下行(衰退定价)而 TIPS_10Y 转平或回落;近1个月分解(实际+11bp、盈亏平衡-19bp)与该解释相容
- 竞争性解释: 解释C(跨边境溢出/技术面): JP_POLICY_RATE 全年步进式正常化经由套息与久期渠道放大全球资产波动,或仓位/流动性技术因素主导近月收缩——若成立,USDJPY 与风险资产的波动应在时间上更紧地耦合,且 HY_OAS 应保持平稳(非信用事件)
### C2 · 历史相似段的证据冲突: 三个最相似候选(2022-06、2025-03、2020-10)的事后路径分歧明显——2022-06 段股指三个月窗先收缩而十二个月窗转正,2025-03 段与 2020-10 段风险资产与 GOLD_F 在十二个月窗普遍走强(2020-10 段 GOLD_F 为负);TOP-N 事后符号一致率: 股指十二个月窗满一致,股指短窗与 UST_10Y/DXY/GOLD_F 各窗仅中低水平(零点六至零点八)。据此『当前状态可外推某一段事后路径』的主张不成立: 历史段只作结构对照与情景校准,不作预测(相似≠因果≠预测,分歧出现=结论降级为描述性)。
- 竞争性解释: 解释A: 三段事后差异主要由各自独有的政策与冲击环境造成(2022-06 处加息中段、2020-10 处极低利率再通胀启动、2025-03 处波动冲击后修复)——事件叙述均为【假设】,引擎面不含事件因果数据
- 竞争性解释: 解释B: 差异由相似度量本身的低维覆盖造成(状态向量 growth 覆盖0.17、inflation 0.33、credit 0.5,信用维在多数候选月缺席),距离最近的时期未必在未覆盖维上可比——若如此,任何单段外推都缺失维度证据
### C3 · 中国政策与美欧日方向的背离未被解释定案: CN_PPI_YOY 自深负值区间升至本轮高点(四大经济体最大价格摆动)而 CN_LPR_1Y 全年持平、政策利率锚于2026-11-02切换为隔夜利率工具,即生产价格大幅上行而政策利率不动。引擎面无中国利率预期序列与信贷/内需序列,三种解释不可区分,标注【尚未验证】。
- 竞争性解释: 解释A: 价格上行主要为输入型/供给驱动(PPI 与 CPI 剪刀差大),内需(CN_CPI_YOY 仅0.7)不足以支持收紧——若如此,背离是合理的政策反应
- 竞争性解释: 解释B: 内需不足制约政策空间(增长侧 CN_PMI_MFG 最新49.3处荣枯线下),即便价格上行也不敢收紧——若如此,背离反映的是增长约束而非价格判断
- 竞争性解释: 解释C: 汇率/资本流动目标约束政策选择——引擎面无中国资本流动序列,该解释当前不可检验,标注【尚未验证】
### 机制链 M1 · 
- 环1 [E1] 冲击环【事实/E1】: 2026-02→2026-05 美欧中通胀同窗回升(美国CPI同比2.434→4.1666、EA_HICP_YOY 1.9→3.2、CN_PPI_YOY -0.9→3.9),此后美国 CORE_PCE 同比续升至3.12@2026-09、EA_HICP_YOY 续升至4.0@2026-10、CN_PPI_YOY 续升至5.7@2026-10。
- 环2 [E3] 政策环【时序为事实,动机为假设/E3】: 时序上政策再收紧的变动月(2026-06起: ECB 决议2026-06-11生效2026-06-17、决议2026-09-10生效2026-09-16;美联储2026-09-17生效回补降息;日本央行决议2026-09-18生效2026-09-24)在通胀转折月(至2026-05)之后;『央行因通胀再加速而收紧』的动机归因不可由本引擎数据验证,整环为【假设】,证伪指标=CPI(若 CPI 同比回落至2.5以下而央行仍续紧,动机环被证伪)。
- 环3 [E1] 利率环【事实/E1】: 12个月窗(2025-11-19→2026-11-19共同交易日)十年期美债名义+91bp=实际(TIPS_10Y)+102bp+盈亏平衡(BEI_10Y)-11bp,恒等残差0;水平 UST_10Y 5.04、TIPS_10Y 2.88、BEI_10Y 2.15@2026-11-19/20——名义上行几乎全部由实际利率贡献,市场通胀预期(盈亏平衡)反而回落。
- 环4 [E2] 资产环【E2,缺环为假设】: 近1个月(2026-10-22→2026-11-20/19)SPX -9.83%、NIKKEI225 -10.29%、GOLD_F -13.42%、DXY +2.17%、VIX 19.03→35.89,与『实际利率上行压制长久期/无现金流资产、推升美元』的机制相容;但资产与利率只有共动事实(相关≠因果),『利率变化导致估值变化』的传导环节本引擎无法直接验证,此环为【假设】;若为利率驱动,HY_OAS 应保持温和(非信用驱动),证伪观察=HY_OAS 快速走阔至危机水平。
  - 缺环注记: 缺失环=利率变化→估值变化的因果传导(引擎只有共动事实,无因果识别);该环为【假设】,证伪指标=HY_OAS
### 机制链 M2 · 
- 环1 [E1] 【事实/E1】: JP_POLICY_RATE(无担保隔夜拆借月均)自2025-12月均0.557步进升至2026-10月均1.227(窗内净+67bp,月度步进+8/+17/+11/+14/+7/+18bp),为四地唯一全年方向不变的政策轨迹;发布日历实录载政策决议2026-09-18(生效2026-09-24);USDJPY 水平159.71@2026-11-20。
- 环2 [E3] 【E3,整环假设】: 日本正常化推升日债收益率与全球期限溢价、经套息平仓放大风险资产波动——本引擎无 JGB 历史序列(单点观测),整环不可验证,为【假设】;证伪指标=USDJPY(若风险资产再次收缩而 USDJPY 未同步走低/日元未走强,套息平仓渠道的分量应被下调)。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### SCN1 · 角色=
- 情景: 基准情景(假设非预测): 假设通胀再加速延续(美国CPI同比保持在3以上)且欧/美/日维持收紧倾向、中国继续按兵不动,则实际利率维持高位、政策分化延续。
- 资产方向: 在此假设下,股指(SPX/NIKKEI225)倾向承压或高波动、GOLD_F 受高实际利率与强美元双重压力、DXY 偏强、VIX 中枢抬升;该方向与2022-06相似段3个月窗(SPX -5.28%、GOLD_F -7.49%、DXY +7.10%,月末口径)一致,但同段12个月窗 SPX 转正(+17.57%)——历史相似证据内部亦分歧。 | 置信档: 有历史相似证据
- 敏感变量: TIPS_10Y, CPI
- 证伪: 指标=CPI | 阈值=美国CPI同比(2025-10基期补齐后)回落至2.5以下且 CORE_PCE 同比回落至2.8以下并持续两个月——通胀再加速前提失效,本情景资产方向判断随之失效 | 次级=CORE_PCE
- 触发: 美国2026-11或2026-12月CPI同比继续≥3.5,或欧央行/美联储再加息(决议日见发布日历实录) | 期限: 2027-02-28
### SCN2 · 角色=
- 情景: 反例情景(假设非预测): 假设通胀再加速被证明为一次性(基数/供给消退),欧/美暂停并转向宽松预期,则盈亏平衡通胀回升而实际利率回落、政策分化收敛。
- 资产方向: 在此假设下,股指倾向修复、GOLD_F 修复走强、DXY 转弱;该方向与2025-03相似段12个月窗(GOLD_F +48.83%、DXY -4.08%、SPX +16.33%,月末口径)方向一致——注意该段相似度主要由波动维单独支撑且事后窗与本轮早段重叠,样本非独立。 | 置信档: 有历史相似证据
- 敏感变量: BEI_10Y, TIPS_10Y
- 证伪: 指标=BEI_10Y | 阈值=BEI_10Y 跌破1.8且继续下行——盈亏平衡通胀不回升反深跌,『一次性通胀+宽松预期修复』前提失效(深跌 BEI 指向衰退定价而非修复) | 次级=UST_10Y
- 触发: 欧央行或美联储下一次决议为降息或明确暂停指引(决议日见发布日历实录),或美国CPI同比连续两个月回落 | 期限: 2027-02-28

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
| 36 | snapshot_fact | CN_LPR_1Y@2026-11-20 |  |
| 37 | snapshot_fact | CN_CPI_YOY@2026-10-31 |  |
| 38 | snapshot_fact | CN_PPI_YOY@2026-10-31 |  |
| 39 | snapshot_fact | CN_PMI_MFG@2026-10-01 |  |
| 40 | snapshot_fact | DFF@2026-11-19 |  |
| 41 | snapshot_fact | DFEDTARU@2026-11-21 |  |
| 42 | snapshot_fact | NIKKEI225@2026-11-20 |  |
| 43 | snapshot_fact | JP_CPI_YOY@2026-10-01 |  |
| 44 | snapshot_fact | ECB_DFR@2026-09-16 |  |
| 45 | snapshot_fact | ECB_MRO@2026-09-16 |  |
| 46 | snapshot_fact | EA_HICP_YOY@2026-10-01 |  |
| 47 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 48 | s3_envelope | SZCI@2026-11-20 |  |
| 49 | s3_envelope | CHINEXT@2026-11-20 |  |
| 50 | s3_envelope | HSCEI@2026-11-20 |  |
| 51 | s3_envelope | NVDA@2026-11-20 |  |
| 52 | s3_envelope | AAPL@2026-11-20 |  |
| 53 | s3_envelope | MSFT@2026-11-20 |  |
| 54 | s3_envelope | TLT@2026-11-20 |  |
| 55 | s3_envelope | IEF@2026-11-20 |  |
| 56 | s3_envelope | SHY@2026-11-20 |  |
| 57 | s3_envelope | HYG@2026-11-20 |  |
| 58 | s3_envelope | LQD@2026-11-20 |  |
| 59 | s3_envelope | GBPUSD@2026-11-21 |  |
| 60 | s3_envelope | WTI_F@2026-11-20 |  |
| 61 | s3_envelope | GLD@2026-11-20 |  |
| 62 | s3_envelope | USO@2026-11-20 |  |
| 63 | s3_envelope | EEM@2026-11-20 |  |
| 64 | s3_envelope | EZU@2026-11-20 |  |
| 65 | s3_envelope | FEZ@2026-11-20 |  |
| 66 | s3_envelope | EWU@2026-11-20 |  |
| 67 | s3_envelope | EWG@2026-11-20 |  |
| 68 | s3_envelope | EWJ@2026-11-20 |  |
| 69 | s3_envelope | INDA@2026-11-20 |  |
| 70 | s3_envelope | FXI@2026-11-20 |  |
| 71 | s3_envelope | BTC@2026-11-20 |  |
| 72 | s3_envelope | HY_IG_DIFF@2026-11-19 |  |

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
- run 门(Audit-R4 条目5): blocked_class=None degraded_ok=False
- review: required=True seat_invoked=True verdict=UPHELD fresh=True error=None 修订链档数=1
- copies_consistent(多副本一致): True(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前确定性装配)
- deliverable(可交付): True
- 内容绑定(Audit-R4 条目2): content_sha256=canonical(report.json 剥离 semantic_review)+canonical(agent_judgment.json)+canonical(views_digest.json)——机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。
