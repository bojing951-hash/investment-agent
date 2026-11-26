# 完整研究报告(一键研究 MVP)

- 问题: 给我一份全球宏观经济变化地图。美国、中国、欧元区、日本在12个月前、3个月前和最新一期，分别处于什么增长、通胀和货币政策环境？过去一年最重要的三个转折是什么，谁先变，谁跟进或背离？证据最充分的传导机制是什么，还有什么解释，哪个指标能区分它们？历史上哪些时期结构最像，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- run_ok: True | 证据行: 68 | run.ts_utc: 20261121T005508Z

## L1 事实层(引擎确定性产出)

| 指标 | 值 | 单位 | 观测日 | 质量 | 证据 ref |
|---|---|---|---|---|---|
| SPX | 7018.53 | index_point | 2026-11-20 | PASS | SPX@2026-11-20 |
| NDX | 25495.15 | index_point | 2026-11-20 | PASS | NDX@2026-11-20 |
| RUT | 2606.02 | index_point | 2026-11-20 | PASS | RUT@2026-11-20 |
| DXY | 103.82 | index_point | 2026-11-20 | PASS | DXY@2026-11-20 |
| EURUSD | 1.1 | usd_per_eur | 2026-11-20 | PASS | EURUSD@2026-11-20 |
| GOLD_F | 3527.6 | usd_per_oz | 2026-11-20 | PASS | GOLD_F@2026-11-20 |
| SILVER_F | 40.83 | usd_per_oz | 2026-11-20 | PASS | SILVER_F@2026-11-20 |
| BRENT_F | 89.18 | usd_per_barrel | 2026-11-20 | PASS | BRENT_F@2026-11-20 |
| VIX | 32.04 | index_point | 2026-11-20 | PASS | VIX@2026-11-20 |
| DAX | 24802.78 | index_point | 2026-11-20 | PASS | DAX@2026-11-20 |
| CAC40 | 7927.75 | index_point | 2026-11-20 | PASS | CAC40@2026-11-20 |
| USDJPY | 158.76 | jpy_per_usd | 2026-11-20 | PASS | USDJPY@2026-11-20 |
| USDCNY | 6.66 | cny_per_usd | 2026-11-20 | PASS | USDCNY@2026-11-20 |
| HY_OAS | 3.52 | percentage_point | 2026-11-19 | PASS | HY_OAS@2026-11-19 |
| BB_OAS | 2.1 | percentage_point | 2026-11-19 | PASS | BB_OAS@2026-11-19 |
| B_OAS | 3.8 | percentage_point | 2026-11-19 | PASS | B_OAS@2026-11-19 |
| CCC_OAS | 13.61 | percentage_point | 2026-11-19 | PASS | CCC_OAS@2026-11-19 |
| IG_OAS | 0.94 | percentage_point | 2026-11-19 | PASS | IG_OAS@2026-11-19 |
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
| SHCOMP | 3533.79 | index_point | 2026-11-20 | PASS | SHCOMP@2026-11-20 |
| HSI | 22841.62 | index_point | 2026-11-19 | PASS | HSI@2026-11-19 |
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
### CONTRA-1 · 2026年春季全球通胀再加速是过去一年最重要的共同冲击:美国 CPI 与欧元区 EA_HICP_YOY 的同比在2026-02至2026-05同窗显著抬升(具体前后值见转折表与锚值回贴),中国生产者价格 CN_PPI_YOY 同窗由负转正且至2026-10升幅为四地最大;美欧中三者转折同月(月频观测,先后未定)。驱动归因存在数据同样容纳的并列解释(见 competing_explanations),引擎面无法单声一种叙事。
- 依据: 证据锚(当前快照水平): CPI 337.476@2026-10-01、CORE_CPI 339.9@2026-10-01、CORE_PCE 130.902@2026-09-01、BRENT_F 89.18@2026-11-20;欧元区 EA_HICP_YOY 的最新同比读数(见走位锚值回贴,2026-10已突破四)为四地最高。headline 与核心的裂口、核心 PCE 的上行、商品价格的双向剧烈波动并存,分别支持不同解释。
- 竞争性解释: 输入型解释: 若商品与生产者价格沿贸易链外溢,则 headline 将先于核心上行、裂口走阔——与当前 headline 高于核心约1.15个百分点的现况一致(【假设】:引擎无分国进口价格/贸易链序列,外溢环不可直接验证,证伪指标 BRENT_F——若 BRENT_F 持续回落而 headline 同比仍居高,输入型解释被削弱)
- 竞争性解释: 内生型解释: 若服务/工资等内生动力主导,则核心通胀将同步上行——与 CORE_PCE 同比持续上行的走势一致;此解释下央行紧缩对通胀的抑制会更慢(证伪指标 CORE_PCE——若其同比回落至2.5%以下,内生粘性解释被削弱)
- 竞争性解释: 基数/统计效应解释: 若2025年低基数与统计口径调整机械推高同比,则6-12个月内同比将自行回落、无需政策起效(证伪指标 CPI——若2027年春同比仍高于3.5%,基数解释被否定)
### CONTRA-2 · 美债十年期名义利率过去十二个月大幅上行,且引擎恒等分解显示上行几乎全部由实际利率贡献、盈亏平衡通胀反而小幅回落——这与『通胀预期失控推升名义利率』的直觉叙事相反(该叙事被分解直接排除);但实际利率上行的来源(政策紧缩 vs 期限溢价/财政供给 vs 增长预期上修)不可由分解本身区分(12个月窗分解数值见 reader_map 传导链与 rates_decomposition 回贴)。
- 依据: 证据锚(当前快照水平): UST_10Y 5.07@2026-11-18、TIPS_10Y 2.88@2026-11-18、BEI_10Y 2.16@2026-11-19、CURVE_2S10S 0.28@2026-11-19;近30日窗口名义与盈亏平衡回落、实际利率回升,与12个月窗方向一致。
- 竞争性解释: 政策紧缩驱动: 若再收紧定价主导,则前端敏感、曲线走平——与过去一年曲线走平的方向一致,但曲线形状非充分识别(【推断】非定论)
- 竞争性解释: 期限溢价/财政供给驱动: 若债券供给压力抬升期限溢价,则长端上行与政策预期无关,曲线应走陡——与现况相反,此解释当前证据较弱但不可排除(【假设】:引擎无期限溢价分解序列,证伪指标 UST_30Y——若长端在政策持稳期继续独自上行,该解释获支持)
- 竞争性解释: 增长预期上修驱动: 若市场定价潜在增速上移,实际利率自然上行——但美国增长面在减速,解释力弱,列为完备性并列(证伪指标 US_REAL_GDP——若其同比重新加速至2.5%以上需重估)
### CONTRA-3 · 近1个月风险资产急跌而信用利差月内近乎不动: SPX 月窗-9.52%(7018.53@2026-11-20)、VIX 32.04(月窗+92.09%)、GOLD_F 月窗-15.0%、DXY 月窗+2.0%,同期 HY_OAS 月内仅+0.08pp(3.52@2026-11-19)、IG_OAS 月内+0.00pp——股票与黄金同月大幅走低而投资级信用利差纹丝不动,这一组合的机制归属存在并列解释;最近一周 HY_OAS +0.29pp、CCC_OAS +0.45pp 开始追赶,证据面在演化中。
- 依据: 证据锚: SPX/NIKKEI225/GOLD_F/VIX/DXY/HY_OAS 快照与月窗(2026-10-21至2026-11-20)及周窗(2026-11-13起)变化;HY_OAS 年内+0.71pp、CCC_OAS 年内+4.76pp(2025-12-31基准)显示信用压力全年渐进累积。
- 竞争性解释: 利率/流动性挤压: 若实际利率高位与美元流动性收紧是主因,则估值压缩+黄金与股票同向+美元偏强的组合成立——月内信用利差近零与此一致(证伪指标 HY_OAS——若其持续升破4.0pp,利率单一渠道解释被削弱)
- 竞争性解释: 增长/信用恶化: 若市场开始定价增长转弱,则信用利差应后来居上——最近一周 HY_OAS 的追赶与此一致,但单周不足定论(证伪指标 HY_OAS 与 CCC_OAS 同向持续走阔)
- 竞争性解释: 波动冲击/去杠杆: 若 VIX 单月接近翻倍触发机械性减仓,则跨资产相关性趋同、利差滞后反应为技术性而非基本面——若 VIX 回落后利差随即收窄,支持本解释(证伪指标 VIX——若 VIX 回落至20以下而 HY_OAS 仍居4.0pp上方,去杠杆解释被削弱)
### CONTRA-4 · 主要央行政策路径先分化后趋同:美联储2025-12-10降息后,于2026-09-16与欧央行同周重新加息(利率终点回到起点,前后值见锚值回贴);欧央行2026-06-11与2026-09-10两度加息;日央行 JP_POLICY_RATE(月均口径)全年渐进上调;中国在 CN_LPR_1Y 与七天期逆回购利率上全年按兵。全球货币政策在2026年由分化转向协同再收紧,中国是唯一未跟随加息的主要经济体。
- 依据: 证据锚(当前快照水平): ECB_DFR 2.5@2026-09-16、JP_POLICY_RATE 1.227@2026-10-01、CN_LPR_1Y 3.0@2026-11-20、CN_PMI_MFG 49.3@2026-10-01(中国增长弱修复背景)。政策决议日为日频事件,2026-09-10(欧央行)与2026-09-16(美联储)同处一周,按同一全球政策事件簇计数。
- 竞争性解释: 共同外部冲击解释: 若全球输入型通胀是共同触发器,则协同再收紧是各自对本国 headline 破位的同向反应(时序上通胀转折在前、政策转折在后,方向一致但月频-日频混合下不可严格确立因果)
- 竞争性解释: 各央行独立反应函数解释: 若各自锚定国内口径(美核心PCE、欧HICP、日东京CPI的读数都在抬升),则协同只是各自独立决策的巧合重叠,同周加息不构成协同证据
- 竞争性解释: 中国独立周期解释: 若中国按本国低通胀(CN_CPI_YOY 最新0.7)与弱修复(CN_PMI_MFG 49.3荣枯线下)决策,则其不加息是理性独立——这本身就是『协同』表象的反例,提示所谓全球收紧并不存在统一机制
### 机制链 MC-POLICY-RATES-EQUITY · 
- 环1 [E2] 通胀再加速触发央行再收紧:政策动作(美联储2025-12-10降息、2026-09-16加息;欧央行2026-06-11与2026-09-10各加息25bp)与通胀序列(CPI/EA_HICP_YOY)两端均可观测,时序方向一致(通胀转折2026-05在前、政策转折2026-06至09在后);但『反应函数』环节引擎无对应序列,此环为【假设】
  - 缺环注记: 引擎无央行反应函数/决策规则序列,通胀→政策的因果方向为【假设】,仅时序与幅度旁证
- 环2 [E1] 政策利率→债券名义/实际利率:名义=实际+盈亏平衡为恒等式,可确定性复算——UST_10Y 12个月+95bp=TIPS_10Y +103bp+BEI_10Y -8bp(引擎共同交易日同窗分解,恒等残差0.0),名义上行全部由实际利率贡献;近30日窗口名义-8bp=实际+8bp+盈亏平衡-16bp
- 环3 [E2] 实际利率上行→风险资产估值压缩与波动放大:端点可观测(近1月 SPX -9.52%、VIX 月窗+92.09%、GOLD_F -15.0%、NIKKEI225 -12.67%),但『贴现率→估值』传导环无引擎序列,此环为【假设】;黄金与股票同月同向的组合更提示流动性/保证金渠道同时在场
  - 缺环注记: 估值与贴现率之间无引擎序列可刻画,传导方向为【假设】;信用利差月内近零(HY_OAS 月内+0.08pp)约束了纯信用渠道的解释空间
- 环4 [E1] 资产联动事实面(可直接验证):近1月(2026-10-21至2026-11-20)SPX -9.52%、NIKKEI225 -12.67%、DAX -3.28%、SHCOMP -4.83%、GOLD_F -15.0%、DXY +2.0%、VIX +92.09%;UST_10Y 月内-1.17%(避险方向);HY_OAS 月内+0.08pp、最近一周+0.29pp
- 环5 [E3] 期限溢价/财政供给替代叙事:长端实际利率上行或主要反映债券供给与期限溢价而非政策预期——纯叙事环,无引擎序列可验;若成立,曲线应走陡而非走平
### 机制链 MC-CN-PPI-GLOBAL · 
- 环1 [E2] 中国 PPI→全球商品价格:两端序列在(CN_PPI_YOY 2026-02的-0.9至2026-05的+3.9至2026-10的+5.7;BRENT_F 89.18、年内+46.56%但11月内-24.19%),但跨国商品/中间品贸易传导环引擎无序列,此环为【假设】;中国是本轮再通胀中变幅最大的震动源(Δ+4.8pp)但月频下与美欧转折先后未定
  - 缺环注记: 引擎无跨国投入产出/商品贸易流序列,中国 PPI 至全球商品价格的因果方向为【假设】
- 环2 [E2] 输入通胀→美欧 headline 超核心:裂口本身可确定性计算(CPI 最近有效同比3.72@2026-09 vs CORE_CPI 2.57@2026-09,裂口约1.15个百分点),但『进口成分主导』的归因环为【假设】;核心 PCE 同期上行提示内生成分同时在场
  - 缺环注记: 引擎无 CPI 分项(能源/进口品权重)序列,headline-核心裂口的成因归属为【假设】
- 环3 [E2] 他国通胀→央行反应与前端利率定价:前端利率端点可观测(UST_2Y 4.8@2026-11-18),政策动作可观测(欧央行2026-06/09加息、美联储2026-09加息),但『输入通胀→政策』反应环为【假设】
  - 缺环注记: 政策反应函数环节为【假设】,见 MC-POLICY-RATES-EQUITY 第1环

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### SCN-TIGHTER-LONGER · 角色=
- 情景: 假设(非预测):通胀粘性使主要央行维持再收紧甚至加码,实际利率维持高位,增长继续温和减速——『紧得更久』基准情景
- 资产方向: 风险资产估值持续受压:SPX 偏弱、VIX 中枢抬升、DXY 偏强、黄金在实际利率与美元双高压下承压;信用利差渐进走阔 | 置信档: 有相关证据
- 敏感变量: TIPS_10Y, VIX
- 证伪: 指标=VIX | 阈值=VIX 收盘回落至20以下并持续10个交易日(高波动压制解除=本情景失效) | 次级=SPX,HY_OAS
- 触发: TIPS_10Y 维持2.8%上方,且下一次 CPI 同比读数(最近有效3.72@2026-09)仍高于3.5% | 期限: 2027-02-19
### SCN-INFLATION-FADE · 角色=
- 情景: 假设(非预测):通胀随基数效应与商品回落(11月 BRENT_F 月内-24.19%)自行降温,央行暂停紧缩,风险资产与黄金修复——『通胀自熄』反例情景
- 资产方向: SPX 与 GOLD_F 修复性反弹、VIX 回落、实际利率下行——方向与历史相似段2023-10的事后12个月(SPX +36.04%、GOLD_F +37.86%,锚月末至12个月后月末口径)一致;注意该段相似性由波动维单维主导(巧合警示),外推力弱 | 置信档: 有历史相似证据
- 敏感变量: BEI_10Y, HY_OAS
- 证伪: 指标=BEI_10Y | 阈值=BEI_10Y 跌破1.8%且 SPX 仍低于7500(通胀预期已下行而资产未修复=本情景传导假设失效) | 次级=SPX
- 触发: CPI 同比(最近有效3.72@2026-09)回落至3.0%以下,且 DFEDTARU 维持4.0不再上调 | 期限: 2027-05-21

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
| 13 | snapshot_fact | USDCNY@2026-11-20 |  |
| 14 | snapshot_fact | HY_OAS@2026-11-19 |  |
| 15 | snapshot_fact | BB_OAS@2026-11-19 |  |
| 16 | snapshot_fact | B_OAS@2026-11-19 |  |
| 17 | snapshot_fact | CCC_OAS@2026-11-19 |  |
| 18 | snapshot_fact | IG_OAS@2026-11-19 |  |
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
| 34 | snapshot_fact | SHCOMP@2026-11-20 |  |
| 35 | snapshot_fact | HSI@2026-11-19 |  |
| 36 | snapshot_fact | CN_LPR_1Y@2026-11-20 |  |
| 37 | snapshot_fact | CN_PMI_MFG@2026-10-01 |  |
| 38 | snapshot_fact | NIKKEI225@2026-11-20 |  |
| 39 | snapshot_fact | JP_CPI_YOY@2026-10-01 |  |
| 40 | snapshot_fact | ECB_DFR@2026-09-16 |  |
| 41 | snapshot_fact | ECB_MRO@2026-09-16 |  |
| 42 | snapshot_fact | EA_HICP_YOY@2026-10-01 |  |
| 43 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 44 | s3_envelope | SZCI@2026-11-20 |  |
| 45 | s3_envelope | CHINEXT@2026-11-20 |  |
| 46 | s3_envelope | HSCEI@2026-11-19 |  |
| 47 | s3_envelope | NVDA@2026-11-20 |  |
| 48 | s3_envelope | AAPL@2026-11-20 |  |
| 49 | s3_envelope | MSFT@2026-11-20 |  |
| 50 | s3_envelope | TLT@2026-11-20 |  |
| 51 | s3_envelope | IEF@2026-11-20 |  |
| 52 | s3_envelope | SHY@2026-11-20 |  |
| 53 | s3_envelope | HYG@2026-11-20 |  |
| 54 | s3_envelope | LQD@2026-11-20 |  |
| 55 | s3_envelope | GBPUSD@2026-11-20 |  |
| 56 | s3_envelope | WTI_F@2026-11-20 |  |
| 57 | s3_envelope | GLD@2026-11-20 |  |
| 58 | s3_envelope | USO@2026-11-20 |  |
| 59 | s3_envelope | EEM@2026-11-20 |  |
| 60 | s3_envelope | EZU@2026-11-20 |  |
| 61 | s3_envelope | FEZ@2026-11-20 |  |
| 62 | s3_envelope | EWU@2026-11-20 |  |
| 63 | s3_envelope | EWG@2026-11-20 |  |
| 64 | s3_envelope | EWJ@2026-11-20 |  |
| 65 | s3_envelope | INDA@2026-11-20 |  |
| 66 | s3_envelope | FXI@2026-11-20 |  |
| 67 | s3_envelope | BTC@2026-11-19 |  |
| 68 | s3_envelope | HY_IG_DIFF@2026-11-19 |  |

## 历史相似结构(引擎确定性面·读者版)

- 锚点月: 2026-11 | 特征窗: 12 个月 | 排序口径: (n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准

| rank | 候选月 | 距离 | 距离分位 | 主要贡献维(前2) |
|---|---|---|---|---|
| 1 | 2025-03 | 0.802571 | 0.0 | volatility 52.4%、rates 34.2% |
| 2 | 2022-06 | 0.841938 | 1.3699 | rates 45.2%、valuation 29.7% |
| 3 | 2023-10 | 1.113819 | 28.7671 | volatility 64.7%、valuation 19.0% |
| 4 | 2021-02 | 1.248144 | 56.1644 | rates 77.0%、volatility 13.3% |
| 5 | 2020-01 | 1.316398 | 68.4932 | rates 73.0%、inflation 12.6% |

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
