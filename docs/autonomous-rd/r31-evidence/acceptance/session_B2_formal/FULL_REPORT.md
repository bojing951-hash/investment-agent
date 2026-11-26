# 完整研究报告(一键研究 MVP)

- 问题: 对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整过了多久？
- run_ok: True | 证据行: 63 | run.ts_utc: 20261122T125710Z

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
| NIKKEI225 | 56436.65 | index_point | 2026-11-20 | PASS | NIKKEI225@2026-11-20 |
| EA_HICP_YOY | 4.0 | percent | 2026-10-01 | WARN | EA_HICP_YOY@2026-10-01 |
| JP_POLICY_RATE | 1.227 | percent | 2026-10-01 | WARN | JP_POLICY_RATE@2026-10-01 |

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=False n=None 隔离=None
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)

## L3 AI 推断层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### C1-INFL-SYNC · 美欧通胀环境较 3 个月前同步走高、欧元区幅度更大。欧元区 EA_HICP_YOY 最新读数明显走高、为三地最高水平(数值与观测月见走位对照);美国 CPI 指数水平最新报 337.476(观测 2026-10;3 个月前锚前值 332.813,观测 2026-07;同比派生口径 2026-10 因缺上年同月基期观测不可得,最近有效同比见走位对照),CORE_CPI 报 339.9(观测 2026-10),CORE_PCE 报 130.902(观测 2026-09)。美国 headline 与核心口径同向上行,但读数水平低于欧元区。
- 竞争性解释: 若美欧通胀抬升主要源于能源与进口成本的持续传导(弱欧元放大输入压力),则 headline 强于 core 的结构应延续,且同比读数在数月内维持高位。
- 竞争性解释: 若抬升主要来自低基数与一次性扰动(统计口径、季节性、能源基数),则未来数月同比应自行回落——近一月 BEI_10Y 走低(月窗 -19bp,2026-10-20→2026-11-19,水平 2.15%@2026-11-20)与市场未定价持续通胀的解读相容。
### C2-GROWTH-STABLE · 两地增长面大体平稳、并非本期主导变化。US_REAL_GDP(季频水平)最新报 24611.077(观测 2026-07 季),UNEMPLOYMENT 最新报 4.1(观测 2026-10),其 3 个月前锚前值为 4.1(观测 2026-07);INDPRO 报 103.3954(观测 2026-10),3 个月前锚前值为 103.1675(观测 2026-07)。欧元区实际 GDP 同比读数在引擎点值面仅微幅变动(见走位对照),增长端未见方向性转折。
- 竞争性解释: 若美国工业生产同比回升(1.25→2.15,引擎派生口径)代表制造业周期回暖,则增长动能在 2026 年三季度后段重新加速,失业率低位与此相容。
- 竞争性解释: 若工业读数回升主要为价格与基数效应或单月波动,则增长面应视为走平,实际 GDP 同比的小幅回落(2.19→2.07,引擎派生口径)更代表主趋势。
### C3-JP-POLICY · 日本政策利率处于抬升通道。JP_POLICY_RATE 月均口径最新一期(观测 2026-10)报 1.227%,3 个月前锚前值为 0.978(观测 2026-07)——该序列为无担保隔夜拆借利率月均口径,非政策目标宣布值,宣布目标序列 JP_POLICY_TARGET 在引擎注册表不可得。发布日历实录的最近一次政策决议为 2026-09-18(2026-09-24 生效),至研究截止 2026-11-22 已约两个月,月均口径的最近一级台阶落在 2026-09→2026-10 之交(前值 1.043,现值即最新一期读数),与决议-生效记录相容。
- 竞争性解释: 若月均台阶主要反映日本央行面对通胀与汇率压力的连续上调,则后续月均应呈现更高中枢的平台,2026-11 月均(预计 2026-12 初公布)应维持当前水平附近。
- 竞争性解释: 若台阶包含决议跨月生效的均值效应(决议后次月月均=新水平整月)与资金面季节性,则单月读数变化不完全等于连续上调,需以决议日历为准——引擎日历 2026-09-18 决议(2026-09-24 生效)后暂无新条目,11 月是否有新决议尚未验证。
### 机制链 M1-JP-RATE-PATH · 
- 环1 [E1] 观察: JP_POLICY_RATE 月均自 2025-11 的 0.478 抬升至 2026-10 的 1.227,近 12 个月政策窗净变动 +67bp(引擎政策窗口径),呈多级台阶(2025-12 0.557、2026-01 0.728、2026-06 0.841、2026-07 0.978、2026-09 1.043、2026-10 1.227)。
- 环2 [E2] 传导【假设】: 政策利率中枢上移→日元融资成本上升→套息结构边际压缩;本引擎无日本融资成本/套息持仓序列,此环为【假设】。
  - 缺环注记: 本引擎无日本套息持仓/融资成本序列,该环为【假设】,缺环待采;可核环节仅政策利率路径本身(E1)。
- 环3 [E2] 资产面观察与对照: USDJPY 最新报 159.71(观测 2026-11-20),NIKKEI225 近一月(2026-10-22→2026-11-20)下跌 10.29%;若加息传导单一成立,应见 USDJPY 走低与股指承压并存——当前 USDJPY 仍处高位而股指已明显回落,组合更接近「风险收缩+利差仍高」的混合态,传导方向证据不单一。
  - 缺环注记: USDJPY 方向受多因子驱动(利差/风险情绪/干预预期),与加息传导的当期一致性无法在引擎面单一归因,该环归【假设】层;区分指标=USDJPY。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### S1-INFL-STICKY · 角色=
- 情景: 【假设·非预测】美欧通胀延续当前抬升动能: 至 2027-01,EA_HICP_YOY 同比维持 3.5% 以上,美国 CORE_PCE 同比维持 3.0% 以上,两地政策面维持紧缩偏向(日本月均中枢不低于当前台阶)。
- 资产方向: 在此假设下,实际利率与无风险利率中枢承压上行,利率敏感资产(高估值成长股、黄金)相对走弱,美元指数相对非美货币偏强;此为方向性推演,非幅度预测 | 置信档: 有相关证据
- 敏感变量: EA_HICP_YOY, CORE_PCE
- 证伪: 指标=EA_HICP_YOY | 阈值=若 2027-01 前发布的 EA_HICP_YOY 同比连续两个月低于 3.0%,通胀粘性假设被证伪 | 次级=CORE_PCE
- 触发: 2026-12 或 2027-01 发布的 EA_HICP_YOY 同比 ≥4.0% 且 CORE_PCE 同比 ≥3.1%,同时 TIPS_10Y 高于 3.0% | 期限: 2027-02-15
### S2-INFL-FADE · 角色=
- 情景: 【假设·非预测】当前美欧通胀抬升以一次性因素(能源基数、汇率进口传导)为主: 至 2027-01,EA_HICP_YOY 同比回落至 3.0% 以下,美国 CORE_PCE 同比回落至 2.8% 以下,市场重新定价宽松。
- 资产方向: 在此假设下,通胀补偿与实际利率双双回落,风险资产修复、黄金重新走强、美元走弱;该方向与近一月观察(实际利率月窗 +11bp 而风险资产回落)相反,属并列反例情景 | 置信档: 纯逻辑推理
- 敏感变量: EA_HICP_YOY, CORE_PCE
- 证伪: 指标=EA_HICP_YOY | 阈值=若 2026-12 与 2027-01 两月 EA_HICP_YOY 同比均不低于 4.0%,一次性因素假设被证伪 | 次级=CORE_PCE
- 触发: EA_HICP_YOY 同比连续两个月回落且最新值 ≤3.4%,同时 BEI_10Y 低于 2.0% | 期限: 2027-02-15

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
| 50 | s3_envelope | GBPUSD@2026-11-21 |  |
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
| 62 | s3_envelope | BTC@2026-11-20 |  |
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
- run 门(Audit-R4 条目5): blocked_class=None degraded_ok=False
- review: required=True seat_invoked=True verdict=UPHELD fresh=True error=None 修订链档数=1
- copies_consistent(多副本一致): True(report.md=report.json 当前渲染;FULL_REPORT 内容段=当前确定性装配)
- deliverable(可交付): True
- 内容绑定(Audit-R4 条目2): content_sha256=canonical(report.json 剥离 semantic_review)+canonical(agent_judgment.json)+canonical(views_digest.json)——机构归属/标题/日期/摘编/事实/L3/L4/run_ok/版本指针任一变化即失效旧裁决;审查与渲染同源,视图不一致即拒绝交付

---
渲染纪律: 本件只汇编在场事实(确定性装配),不做新增生成;L3/L4 内容归 Agent 席与独立审计,本段不代写。
