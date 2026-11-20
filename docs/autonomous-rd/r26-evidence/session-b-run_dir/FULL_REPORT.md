# 完整研究报告(一键研究 MVP)

- 问题: 对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整过了多久？
- run_ok: True | 证据行: 63 | run.ts_utc: 20261120T151654Z

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
| SHCOMP | 3533.79 | index_point | 2026-11-20 | PASS | SHCOMP@2026-11-20 |
| HSI | 22410.8 | index_point | 2026-11-20 | PASS | HSI@2026-11-20 |
| NIKKEI225 | 56436.65 | index_point | 2026-11-20 | PASS | NIKKEI225@2026-11-20 |
| JP_CPI_YOY | 2.44 | percent | 2026-10-01 | WARN | JP_CPI_YOY@2026-10-01 |
| EA_HICP_YOY | 4.0 | percent | 2026-10-01 | WARN | EA_HICP_YOY@2026-10-01 |

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=False n=None 隔离=None
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)

## L3 AI 推断层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### C1 · 三个月对照窗口内(锚为三个月前,截止为研究当日),美国与欧元区通胀读数同步回升而增长面大体平稳,宏观组合由『通胀回落中段』摆向『通胀再加速』;该同步回升是共同全球驱动(能源或上游成本)还是两地独立过程的共振,月频证据不能裁决,按统计期对齐不代表当时市场信息集。
- 依据: 引擎锚点面与序列(EA_HICP_YOY/CPI/CORE_CPI/CORE_PCE/INDPRO/US_REAL_GDP/EA_REAL_GDP_YOY/UNEMPLOYMENT):欧HICP同比与美CPI最近有效同比均高于各自锚,核心PCE接近锚;增长面美失业率与锚持平、工业生产同比回升、实际GDP同比微降,欧实际GDP同比微升。research_mode_gate: event_study blocked,不得按发布日对齐。
- 竞争性解释: 共同全球驱动:若能源与上游成本是主因,后续美欧标题通胀应与商品价格同节奏波动,且标题读数变化领先核心读数【假设——引擎无跨国冲击识别序列】
- 竞争性解释: 独立过程共振:若回升源于各自的服务通胀与工资动力,后续美欧通胀应脱钩(有的回落有的续升),核心与标题差距收窄【假设】
- 竞争性解释: 统计口径因素:美国上年停摆补发布造成基期月缺席,严格同月同比最新格不可得,表观回升幅度可能被基期口径放大【尚未验证】
### C2 · 美国增长信号内部背离:失业率与锚持平、工业生产同比回升、实际GDP同比较锚微降——整体更接近『平稳偏缓』而非『加速』或『衰退』,但三种读数的权重取舍无引擎证据可裁决;增长环境的定性对指标选择敏感。
- 依据: 锚(三个月前)与最新观测来自引擎点值面与序列(UNEMPLOYMENT/INDPRO/US_REAL_GDP);工业生产同比回升与实际GDP同比微降并存,方向判断对指标选择敏感,两组读数均为最新修订或采集口径。
- 竞争性解释: 动能稳固:若工业与就业信号为主导,实际GDP的微降反映基数与统计波动,增长环境较三个月前略有改善【假设】
- 竞争性解释: 降温前兆:若GDP口径为主导,工业回升是库存周期扰动,增长环境趋缓【假设——引擎无分项/信贷敏感部门序列,此环缺失】
### C3 · 日本央行处于连续收紧通道:无担保隔夜拆借利率月均自年中以来台阶式上行且最新观测月读数为该轮最高;同时日本全国与东京CPI同比均高于各自锚读数,通胀回到目标上方为继续正常化提供理由,而日经225近月显著走弱提示金融条件已明显收紧——收紧节奏会否被市场波动掣肘,现有证据不能裁决。
- 依据: 利率读数来自引擎history序列(JP_POLICY_RATE,月均operative口径,非决议目标值;决议日级序列引擎不可得);通胀与资产读数来自本报告证据面(JP_CPI_YOY/JP_CPI_TOKYO_YOY锚点面、NIKKEI225/USDJPY快照)。月均序列显示最近台阶落在最近两个观测月之间,更精确的决议日定位不可得。
- 竞争性解释: 通胀主导:若日本通胀续升,央行维持渐进收紧,国内流动性续收紧、日元流动性环境偏紧【假设】
- 竞争性解释: 金融稳定主导:若股市波动被央行视为金融稳定风险,收紧节奏放缓甚至暂停【假设——引擎无央行沟通/预期序列】
### 机制链 M1 · 
- 环1 [E1] 锚至最新通胀面:欧元区HICP同比2.9(2026-07观测)→4.0(2026-10观测);美国CPI同比最近有效3.7173(2026-09观测,严格同月基期;2026-10格缺2025-10基期不可得,引擎12个月窗2026-10对2025-09基期=4.0806);核心PCE同比3.04(2026-06观测)→3.1212(2026-09观测)。
- 环2 [E2] 通胀回升→货币当局维持或加码紧缩:BOJ月均operative利率0.977(2026-08观测)→1.043(2026-09观测)→1.227(2026-10观测);ECB存款便利利率末观测2.5(2026-09-16,决议日级序列);Fed目标区间上限4.0、下限3.75(2026-11-19)。
  - 缺环注记: 引擎无通胀→政策反应函数序列,『通胀回升促使维持紧缩』这一映射为【假设】;各政策读数为引擎原值。
- 环3 [E1] 实际利率与风险资产:引擎三利率分解12个月窗UST_10Y +95bp=TIPS_10Y +103bp+BEI_10Y -8bp(名义上行几乎全部来自实际利率);近1月资产月窗SPX -6.96%、NIKKEI225 -11.92%、VIX +64.3%、GOLD_F -12.42%。
### 机制链 M2 · 
- 环1 [E1] 日本通胀回升:全国CPI同比1.97(2026-07观测)→2.44(2026-10观测);东京都CPI同比2.73(2026-10观测,速报先行口径)。
- 环2 [E2] 通胀回到目标上方→BOJ继续收紧(月均operative利率1.043→1.227,2026-09→2026-10观测):决议目标值序列与决议日均不可得,该反应映射为【假设】。
  - 缺环注记: 引擎无日本央行决议目标值/决议日序列(release_semantics明示月均operative非决议值),通胀→加息决策环为【假设】。
- 环3 [E3] 套息头寸平仓放大日股与日元波动(日经225近1月-11.92%;USDJPY 159.61,2026-11-19)——纯叙事机制,相关非因果。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### SCN-1 · 角色=
- 情景: 【假设非预测】基准情景:若美欧通胀延续回升(美国CPI最近有效同比3.7173的基础上维持3.5上方)、BOJ延续渐进收紧、全球实际利率维持高位
- 资产方向: 日经225与高估值权益继续承压、波动率维持高位;若BOJ续紧则日元相对偏强(USDJPY回落)——该腿为前提下的逻辑推演 | 置信档: 有相关证据
- 敏感变量: JP_CPI_YOY, EA_HICP_YOY
- 证伪: 指标=JP_CPI_YOY | 阈值=2027-02-28前最近有效日本全国CPI同比回落至1.5下方,则『通胀支撑继续收紧』前提被证伪(当前2.44,2026-10观测)
- 触发: 观测月2026-11与2026-12的日本全国CPI同比(发布于2026-12与2027-01)均不低于2.0,且JP_POLICY_RATE月均序列继续抬升 | 期限: 2027-02-28
### SCN-2 · 角色=
- 情景: 【假设非预测】反例情景:若通胀回升被证明为能源与基数暂时性、BOJ暂停收紧、风险偏好修复
- 资产方向: 日经225修复反弹、VIX回落、USDJPY走弱 | 置信档: 纯逻辑推理
- 敏感变量: CPI, BRENT_F
- 证伪: 指标=CPI | 阈值=2027-01-31前最近有效美国CPI同比升至4.5上方(当前最近有效3.7173,2026-09观测),则『暂时性』解释被证伪
- 触发: 2026-12与2027-01发布的美国CPI同比(观测月2026-10起;2026-10格若因基期缺席则以最近有效格为准)连续回落至3.0下方 | 期限: 2027-01-31

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
| 34 | snapshot_fact | SHCOMP@2026-11-20 |  |
| 35 | snapshot_fact | HSI@2026-11-20 |  |
| 36 | snapshot_fact | NIKKEI225@2026-11-20 |  |
| 37 | snapshot_fact | JP_CPI_YOY@2026-10-01 |  |
| 38 | snapshot_fact | EA_HICP_YOY@2026-10-01 |  |
| 39 | s3_envelope | SZCI@2026-11-20 |  |
| 40 | s3_envelope | CHINEXT@2026-11-20 |  |
| 41 | s3_envelope | HSCEI@2026-11-20 |  |
| 42 | s3_envelope | NVDA@2026-11-19 |  |
| 43 | s3_envelope | AAPL@2026-11-19 |  |
| 44 | s3_envelope | MSFT@2026-11-19 |  |
| 45 | s3_envelope | TLT@2026-11-19 |  |
| 46 | s3_envelope | IEF@2026-11-19 |  |
| 47 | s3_envelope | SHY@2026-11-19 |  |
| 48 | s3_envelope | HYG@2026-11-19 |  |
| 49 | s3_envelope | LQD@2026-11-19 |  |
| 50 | s3_envelope | GBPUSD@2026-11-19 |  |
| 51 | s3_envelope | WTI_F@2026-11-19 |  |
| 52 | s3_envelope | GLD@2026-11-19 |  |
| 53 | s3_envelope | USO@2026-11-19 |  |
| 54 | s3_envelope | EEM@2026-11-19 |  |
| 55 | s3_envelope | EZU@2026-11-19 |  |
| 56 | s3_envelope | FEZ@2026-11-19 |  |
| 57 | s3_envelope | EWU@2026-11-19 |  |
| 58 | s3_envelope | EWG@2026-11-19 |  |
| 59 | s3_envelope | EWJ@2026-11-19 |  |
| 60 | s3_envelope | INDA@2026-11-19 |  |
| 61 | s3_envelope | FXI@2026-11-19 |  |
| 62 | s3_envelope | BTC@2026-11-18 |  |
| 63 | s3_envelope | HY_IG_DIFF@2026-11-18 |  |

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
