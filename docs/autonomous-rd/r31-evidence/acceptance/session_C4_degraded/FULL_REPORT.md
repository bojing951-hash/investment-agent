# 完整研究报告(一键研究 MVP)

- 问题: 2026年11月,美、欧、中、日四地的宏观环境相比三个月前,哪些经济体之间出现了明显分化?分化主要体现在哪些维度?请给出具体数据和各数据的公布时间,并说明哪些维度证据不足以下结论。
- run_ok: True | 证据行: 61 | run.ts_utc: 20261122T040935Z

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
| HSI | 22841.62 | index_point | 2026-11-19 | PASS | HSI@2026-11-19 |
| DFF | 3.88 | percent | 2026-11-19 | PASS | DFF@2026-11-19 |
| DFEDTARU | 4.0 | percent | 2026-11-21 | PASS | DFEDTARU@2026-11-21 |
| NIKKEI225 | 59444.21 | index_point | 2026-11-19 | PASS | NIKKEI225@2026-11-19 |
| JP_POLICY_RATE | 1.227 | percent | 2026-10-01 | WARN | JP_POLICY_RATE@2026-10-01 |

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=False n=None 隔离=None
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)

## L3 AI 推断层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### CON-1 · 政策维(美日两席可判): 研究窗内 DFF 与 JP_POLICY_RATE 同向收紧、幅度同为一次标准步长量级,窗口内方向同步而非分化;分化体现在十二个月路径——DFF 先降后升往返净零,JP_POLICY_RATE 月均持续抬升(净抬升约零点六七个百分点),且两席水平差维持悬殊。欧央行两席(ECB_MRO/ECB_DFR)与中国人民银行各席序列缺席,政策维的『四地分化』不可判,只能陈述美日对照。
- 竞争性解释: 若美日同幅收紧是对同一全球通胀/能源压力的共同反应(BRENT_F 处于高位可作候选共同因子),则窗口内同步属同一全球政策事件,后续将同进同退
- 竞争性解释: 若各自国内周期独立(美国通胀回升触发重启收紧、日本正常化收官),同步属巧合,后续将分道——美国或按通胀数据停步、日本或按正常化节奏继续
### CON-2 · 通胀维(仅美国可判): 美国读数趋升——CPI 最近有效同比(九月)高于三个月前读数, CORE_CPI 与 CORE_PCE 最近有效同比亦均高于三个月前;最新十月 CPI 水平已发布但同比缺基期不可得(引擎口径: 月度同比只配去年同月,不以近值代基期)。EA_HICP_YOY、CN_CPI_YOY、CN_PPI_YOY、JP_CPI_YOY、JP_CPI_TOKYO_YOY 序列全部缺席——四地通胀维分化不可判,只能陈述『美国趋升、其余三地未知』。
- 竞争性解释: 若美国通胀回升为需求驱动,将推动政策维持偏紧并压制风险资产估值
- 竞争性解释: 若为基数效应或能源价格传导的暂时性抬升,通胀将自然回落,政策收紧或止步于已宣布的步长
### CON-3 · 增长维(仅美国可判)与市场面(独立证据层): 美国增长面稳——US_REAL_GDP 同比小幅放缓、UNEMPLOYMENT 读数持平、INDPRO 同比回升;EA_REAL_GDP_YOY、CN_PMI_MFG、JP_REAL_GDP_YOY 缺席,四地增长维分化不可判。市场面: 近三月 SPX 与 NIKKEI225 跌幅相当且深于 DAX, VIX 大幅抬升, UST_10Y 上行——市场表现的分化是事实,但把市场跌幅差直接当作宏观环境分化属推断而非事实(资产价格是预期与定价的混合,非宏观读数)。
- 竞争性解释: 若市场跌幅差反映宏观预期分化,则美股与日经深跌或预示美日相对走弱被市场提前定价
- 竞争性解释: 若为估值/仓位技术性调整(前期涨幅与拥挤度的差异),宏观面并未同步分化,跌幅差将收敛
### CON-4 · 证据边界(对应问题第三问): 欧元区三维(增长/通胀/政策)、中国三维、日本增长与通胀席在本运行面全部不可得(检索范围=快照 series_store+注册表 history_source 采集档通道,缺数格如实在档);可判维度仅=政策维的美日对照(DFF/JP_POLICY_RATE 两席)与美国单边宏观格。凡以『美、欧、中、日四地』为主语的横向分化结论,在本证据面上均证据不足,不得下结论。
- 竞争性解释: 若序列缺席源于采集配置(密钥/源端未接通),恢复采集后欧中面或将补齐,分化图谱可能改变
- 竞争性解释: 若源端确无该口径,则为长期数据边界——两种情形引擎面不可区分,且缺席既不等于『无分化』也不等于『有分化』
### 机制链 MECH-1 · 
- 环1 [E1] 通胀读数抬升可核: CPI 最近有效同比(9月)3.72% 高于 7月 3.3%,CORE_PCE 同比(9月)3.12% 高于 6月 3.04%;10月 CPI 同比缺基期不可得(水平337.476已于2026-11-13发布)。
- 环2 [E1] 政策反应可核: DFF 于2026-09-17生效跳升(+25bp至3.88,决议2026-09-16);日本央行2026-09-18决议、2026-09-24生效(目标约1.25)后,JP_POLICY_RATE 十月月均至1.227。
- 环3 [E2] 利率与资产同窗并存: TIPS_10Y 共同交易日三十日窗+11bp(2026-10-20至2026-11-19,名义-8bp=实际+11bp+盈亏平衡-19bp),SPX 三个月-9.95%(2026-08-21至2026-11-20)。
  - 缺环注记: 加息→实际利率→股市回撤的因果环为【假设】: 本引擎无高频冲击识别/意外窗序列,同窗并存只是统计事实,反向因果与共同原因不能排除。
### 机制链 MECH-2 · 
- 环1 [E1] 正常化路径可核: JP_POLICY_RATE 月均自2025-12起多次抬升(0.478→1.227,十二个月窗净+67bp),10月读数1.227(公布2026-11-05);2026-09-18决议、2026-09-24生效后目标约1.25。
- 环2 [E2] 汇率含义: USDJPY 报159.71(2026-11-20观测;USDJPY 上行=美元升值/日元贬值);正常化支撑日元的传导在本面未被证实。
  - 缺环注记: 正常化→日元升值的传导环为【假设】: 美日政策同幅收紧下利差方向不单一,引擎无利率差-汇率因果识别序列。
- 环3 [E3] 若正常化主导汇率定价,USDJPY 应趋势性回落;反之若美元强势主导(美元指数三个月+5.07%),日元将被动走弱。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### SCN-A · 角色=
- 情景: 假设情景(非预测)——美国通胀韧性延续: 11月CPI同比(2026-12中旬公布)维持在3.5%或以上,且核心PCE同比不低于3.0%,联储维持偏紧、不排除再加一次标准步长。
- 资产方向: 风险资产承压、波动中枢抬升(VIX高于其长期均值区),美债收益率维持高位 | 置信档: 有相关证据
- 敏感变量: CPI, DFF
- 证伪: 指标=CPI | 阈值=2026-12公布的11月CPI同比回落至3.0%以下(引擎同基期同比口径)即证伪本情景 | 次级=CORE_PCE
- 触发: 11月CPI同比(约2026-12-13公布)≥3.5% 且 10月核心PCE同比(约2026-11-30公布)≥3.0% | 期限: 2026-12-31
### SCN-B · 角色=
- 情景: 假设情景(非预测)——通胀回升为基数/供给扰动且需求边际走弱: 盈亏平衡通胀回落、失业率回升,联储停止进一步收紧,市场情绪修复。
- 资产方向: 美债收益率回落、美股企稳修复、VIX自高位回落 | 置信档: 纯逻辑推理
- 敏感变量: BEI_10Y, UNEMPLOYMENT
- 证伪: 指标=UNEMPLOYMENT | 阈值=11月失业率(2026-12首周公布)降至4.0%或更低(需求韧性)即证伪本情景
- 触发: 10月核心PCE同比(约2026-11-30公布)≤3.0% 且 10月失业率(2026-11-05已公布路径延续)回升至4.3%或以上 | 期限: 2026-12-15

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
| 34 | snapshot_fact | HSI@2026-11-19 |  |
| 35 | snapshot_fact | DFF@2026-11-19 |  |
| 36 | snapshot_fact | DFEDTARU@2026-11-21 |  |
| 37 | snapshot_fact | NIKKEI225@2026-11-19 |  |
| 38 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 39 | s3_envelope | HSCEI@2026-11-19 |  |
| 40 | s3_envelope | NVDA@2026-11-20 |  |
| 41 | s3_envelope | AAPL@2026-11-20 |  |
| 42 | s3_envelope | MSFT@2026-11-20 |  |
| 43 | s3_envelope | TLT@2026-11-20 |  |
| 44 | s3_envelope | IEF@2026-11-20 |  |
| 45 | s3_envelope | SHY@2026-11-20 |  |
| 46 | s3_envelope | HYG@2026-11-20 |  |
| 47 | s3_envelope | LQD@2026-11-20 |  |
| 48 | s3_envelope | GBPUSD@2026-11-21 |  |
| 49 | s3_envelope | WTI_F@2026-11-20 |  |
| 50 | s3_envelope | GLD@2026-11-20 |  |
| 51 | s3_envelope | USO@2026-11-20 |  |
| 52 | s3_envelope | EEM@2026-11-20 |  |
| 53 | s3_envelope | EZU@2026-11-20 |  |
| 54 | s3_envelope | FEZ@2026-11-20 |  |
| 55 | s3_envelope | EWU@2026-11-20 |  |
| 56 | s3_envelope | EWG@2026-11-20 |  |
| 57 | s3_envelope | EWJ@2026-11-20 |  |
| 58 | s3_envelope | INDA@2026-11-20 |  |
| 59 | s3_envelope | FXI@2026-11-20 |  |
| 60 | s3_envelope | BTC@2026-11-20 |  |
| 61 | s3_envelope | HY_IG_DIFF@2026-11-19 |  |

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
- review: required=True seat_invoked=False verdict=None fresh=None error=None 修订链档数=0
- copies_consistent(多副本一致): True(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前确定性装配)
- deliverable(可交付): False
- 内容绑定(Audit-R4 条目2): content_sha256=canonical(report.json 剥离 semantic_review)+canonical(agent_judgment.json)+canonical(views_digest.json)——机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。
