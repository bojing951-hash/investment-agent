# 完整研究报告(一键研究 MVP)

- 问题: 美国、中国、欧元区、日本在12个月前、3个月前和最新一期的增长、通胀、货币政策环境对比;过去一年最重要的三个转折、先后顺序与传导机制;结构最像的历史时期及当时随后3、6、12个月经济与主要资产走势
- run_ok: True | 证据行: 68 | run.ts_utc: 20261120T024347Z

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
### CONTRA-1 · 同一全球再通胀之年,四地政策反应显著分化: 欧央行两度加息(ECB_DFR 路径),美联储在年末加回此前十二月预防式降息(DFEDTARU),日本无担保隔夜拆借月均(JP_POLICY_RATE)连续抬升,而中国贷款市场报价利率与七天逆回购利率全年未动,并于十一月初将政策利率锚换为更低水平的隔夜利率(数值与决议日详见 reader_map 各地区走位、政策事件簇面与转折栏)。【事实】政策分化为年内最大的结构性事实;对其成因的解释属【推断/假设】。
- 竞争性解释: 【假设】分化反映通胀水平差异: 欧元区 EA_HICP_YOY 已达 4.0 而中国 CN_CPI_YOY 仅 0.7,各央行对国内通胀的合理反应自然不同
- 竞争性解释: 【假设】分化反映冲击性质判断: 中国视 PPI 同比 5.7 为输入型/供给型价格而容忍(全年不动),美欧视通胀为需求过热而压制
- 竞争性解释: 【假设】分化含汇率约束: 日本连续收紧部分受日元弱势约束(USDJPY 12 个月 +1.47%),与国内通胀水平的关系居次
### CONTRA-2 · 近三个月,SPX 与美债价格同弱、GOLD_F 明显回落、DXY 走强并存——股、债、金三类资产同弱而美元独强,同期实际利率(TIPS 长端)大幅上行、VIX 抬升、HY_OAS 走阔(具体涨跌幅、窗口两端日与利率分解见 reader_map 资产回报回贴、rates_decomposition 与传导链)。【推断】该组合与『实际利率冲击』的解释一致,与『增长恐慌』解释相左——增长恐慌下债券应获避险买盘,而实际观察为债券收益率上行。并存事实为【事实】,归因属【假设】。
- 竞争性解释: 【假设】实际利率冲击主导: 贴现率上行同时压制股票与黄金,美元因利差走强——与近 1 个月三利率分解(名义 +1bp=实际 +15bp+盈亏平衡 -14bp)相容
- 竞争性解释: 【假设】若增长担忧叠加通胀粘性(类滞胀叙事),股金同跌而债券因衰退预期终将获支撑——当前债弱或源于期限溢价而非增长预期恶化
- 竞争性解释: 【假设】仓位/流动性冲击(保证金驱动抛售)短期主导三资产同跌,与宏观因子关系次要
### CONTRA-3 · 中国量价修复未伴随本地股指同幅修复: 工业品出厂价格同比(CN_PPI_YOY)大幅转正并持续上行、制造业景气同比动量(CN_PMI_MFG)转正(数值与窗口见 reader_map 与转折栏),但 A 股 SHCOMP 与港股 HSI 近一年收跌,同期人民币升值(USDCNY 回落)。【事实】实体价格修复与本地股指表现背离;成因属【假设】。
- 竞争性解释: 【假设】盈利传导滞后: PPI 回升阶段先压缩中下游利润率(成本上升快于终端提价),股指对价格修复的反应滞后
- 竞争性解释: 【假设】政策预期主导: 市场定价全年政策定力(CN_OMO_7D/CN_LPR_1Y 未动)为低于预期的刺激,风险偏好受抑
- 竞争性解释: 【假设】汇率与资金流: 人民币升值(USDCNY -6.33%)压制出口盈利预期,拖累以制造业为主的本地股指
### 机制链 CH-1 · 中国再通胀→美欧通胀回升→政策转鹰→实际利率上行→风险资产与黄金回落
- 环1 [E1] 【事实·引擎可核】中国量价修复: CN_PMI_MFG 三锚 49.0→49.2→49.3,CN_PPI_YOY 三锚 -2.1→3.5→5.7(转折候选面 2026-02→05 为 -0.9→+3.9,|Δ|4.8 为四地之最);同窗美国 CPI 同比 2.434→4.1666、欧元区 EA_HICP_YOY 1.9→3.2(均为转折候选面;月频同窗,三地先后未定)。
- 环2 [E2] 【假设】通胀回升→央行转向紧缩(政策反应函数环): ECB 2026-06-11 决议加息 25bp(DFR 2.0→2.25,生效 06-17)、2026-09-10 再加 25bp 至 2.5;Fed 2026-09-16 决议加息 25bp(DFEDTARU 3.75→4.0)。决议日为日频口径,ECB 首加早于 Fed 97 天,先后可判——此为【事实】;『因通胀而加息』的因果环为【假设】。
  - 缺环注记: 本引擎无央行反应函数或声明文本序列,『通胀→决议』环为【假设】;决议日与幅度可核(政策事件簇),动机不可核。
- 环3 [E1] 【事实·引擎可核】长端利率上行由实际利率驱动: UST_10Y 12 个月(2025-11-17→2026-11-17 共同交易日)+97bp = TIPS_10Y +104bp + BEI_10Y -7bp(名义=实际+盈亏平衡,恒等残差 0bp);近 1 个月(2026-10-16→2026-11-17)+1bp = 实际 +15bp + 盈亏平衡 -14bp;现值 UST_10Y 5.1%=TIPS_10Y 2.89%+BEI_10Y 2.21%。CURVE_2S10S 近 12 个月相对变化 -50.91%(曲线趋平)。
- 环4 [E2] 【事实·并存可核】实际利率上行与风险资产回落并存: 近 3 个月(2026-08-20→2026-11-18)TIPS_10Y 相对变化 +22.98%,同期 SPX 下跌 4.16%、NDX 下跌 7.18%、日经225 下跌 10.86%、恒指下跌 11.22%、GOLD_F 下跌 18.45%、VIX +53.40%、HY_OAS +24.73%。【假设】贴现率/估值渠道为因: 实际利率上行压缩长久期资产估值并抬升持有黄金的机会成本。方向性归因为【假设】。
  - 缺环注记: 『实际利率→资产估值』环两端有序列、同窗并存可核,但因果方向不可由本引擎确定,该环为【假设】。
### 机制链 CH-2 · 日本: 连续收紧→通胀先降后回→东京 CPI 再加速(汇率渠道 vs 工资渠道对质)
- 环1 [E1] 【事实·引擎可核】JP_POLICY_RATE(无担保隔夜拆借月均)三锚 0.477→0.978→1.227 连续收紧;JP_CPI_YOY 三锚 2.99→1.97→2.16 先降后回;JP_CPI_TOKYO_YOY 2026-06→09 自 1.6 升至 2.69(转折候选面);JP_REAL_GDP_YOY 三锚 0.63→0.80→1.16 逐季改善。
- 环2 [E2] 【假设】汇率-进口价格渠道: USDJPY 12 个月 +1.47%、近 3 个月 +0.65%(温和日元弱势),若该渠道主导,东京 CPI 再加速应与 USDJPY 高位并存(并存与【事实】一致,传导为【假设】)。
  - 缺环注记: 本引擎无日本进口价格序列,『USDJPY→东京 CPI 进口传导』环为【假设】。
- 环3 [E3] 【假设·纯叙事】工资-服务粘性渠道: 若东京 CPI 回升主因国内工资-服务通胀(与汇率无关),则 USDJPY 回落时东京 CPI 应继续上行。证伪指标 JP_CPI_TOKYO_YOY: 若 2027-03 前 USDJPY 自当前水平回落 5% 以上而 JP_CPI_TOKYO_YOY 同比仍 ≥2.5,支持工资渠道;若随汇率回落同步降温,支持汇率渠道。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### SCN-TIGHT · 角色=基准情景·前提【假设非预测】全球通胀韧性延续(EA_HICP_YOY 维持 3.5% 以上、美国 CPI 同比维持 3.5% 以上),ECB 2026-12 再加息、Fed 2027 上半年再加息(置信档: 有相关证据)
- 情景: 【假设非预测】紧缩延续情景: 全球通胀韧性延续——EA_HICP_YOY 维持 3.5% 以上、美国 CPI 同比维持 3.5% 以上,ECB 于 2026-12 再加息、Fed 于 2027 上半年再加息,实际利率(TIPS_10Y)维持高位。
- 资产方向: 风险资产承压: SPX/NDX 相对 2026-11-18 水平未来 3-6 个月震荡走弱,长久期与高估值资产弱于短久期;美元相对欧元偏强;黄金承压。 | 置信档: 有相关证据
  - 依据: 近 3 个月(2026-08-20→2026-11-18)TIPS_10Y 相对变化 +22.98% 与 SPX 下跌 4.16%、GOLD_F 下跌 18.45%、VIX +53.40% 并存(引擎资产面);实际利率冲击若延续,贴现率渠道继续压制长久期与黄金。
- 敏感变量: EA_HICP_YOY, UST_10Y
- 证伪: 指标=EA_HICP_YOY | 阈值=若 2027-01 前 EA_HICP_YOY 降至 2.5% 以下且美国 CPI(derived_yoy_pct 口径)连续两个月低于 3.0%,紧缩延续假设证伪 | 次级=CPI
- 触发: ECB 2026-12 议息会议维持 2.5% 不再加息,且 2026-11 值 EA_HICP_YOY ≤ 3.0 | 期限: 2026-12-31
### SCN-DISINFL · 角色=反例情景·前提【假设非预测】美国核心通胀动能延续 CORE_CPI 2026-05→08 的回落(2.8229→2.4462)并扩散至整体,ECB 停在 2.5、Fed 2027 年内转向降息(置信档: 有历史相似证据——2023-10 类比段)
- 情景: 【假设非预测】通胀回落扩散情景(反例情景): 美国 CORE_CPI 动能延续 2026-05→08 的回落(2.8229→2.4462,转折候选面)并扩散至headline,ECB 停在 2.5、Fed 于 2027 年内转向降息,TIPS_10Y 实际利率见顶回落。历史相似面: analog 候选 2023-10(通胀回落期,详见 history_periods[2])之后 12 个月 SPX +34.63%、GOLD_F +38.33%。
- 资产方向: 风险资产修复: SPX 相对 2026-11-18 水平未来 6-12 个月回升;黄金在实际利率回落中反弹;美元走弱(DXY 回落)。 | 置信档: 有历史相似证据
  - 依据: analog 候选 2023-10(通胀回落期)之后 12 个月 SPX +34.63%、GOLD_F +38.33%(事后块口径,起点=候选月次月首日;锚月末→月末口径为 +36.04%/+37.86%,两套引擎窗口口径并存,见历史段窗口口径注);另近 1 个月三利率分解中盈亏平衡通胀 -14bp(BEI_10Y),通胀预期端已现回落迹象。
- 敏感变量: CORE_CPI, TIPS_10Y
- 证伪: 指标=CPI | 阈值=若美国 CPI 同比(derived_yoy_pct 口径)在 2027-01 前回升破 4.0%,或 EA_HICP_YOY 升破 4.5%,通胀回落假设证伪 | 次级=EA_HICP_YOY
- 触发: Fed 于 2027-03 议息会议决议加息或点阵图上修,或 EA_HICP_YOY 2026-11 值 ≥ 4.2 | 期限: 2027-03-31

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
- review: required=True seat_invoked=True verdict=UPHELD fresh=True error=None 修订链档数=2
- copies_consistent(多副本一致): True(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前确定性装配)
- deliverable(可交付): True
- 内容绑定(Audit-R4 条目2): content_sha256=canonical(report.json 剥离 semantic_review)+canonical(agent_judgment.json)+canonical(views_digest.json)——机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。
