# 完整研究报告(一键研究 MVP)

- 问题: 对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整过了多久？
- run_ok: True | 证据行: 63 | run.ts_utc: 20261121T013826Z

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
| NIKKEI225 | 56436.65 | index_point | 2026-11-20 | PASS | NIKKEI225@2026-11-20 |
| EA_HICP_YOY | 4.0 | percent | 2026-10-01 | WARN | EA_HICP_YOY@2026-10-01 |
| JP_POLICY_RATE | 1.227 | percent | 2026-10-01 | WARN | JP_POLICY_RATE@2026-10-01 |

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=False n=None 隔离=None
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)

## L3 AI 推断层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### C1 · 通胀边际变化的跨大区分化和区内结构分化: 双锚对照窗内,欧元区 EA_HICP_YOY 同比明显跳升,美国 CORE_PCE 同比仅温和走高;美国整体 CPI 读数明显高于其核心 CORE_CPI(最近有效同比口径)——两大经济体通胀方向同向(回升)但幅度分化,欧元区边际升温更大,且美国整体与核心读数本身背离。
- 依据: 引擎双锚点值面: EA_HICP_YOY 与 CORE_PCE 的两锚值、CPI 与 CORE_CPI 的最近有效同比与缺基期标注;口径=锚格发布纪律(发布日不晚于锚日的最新观测)。
- 竞争性解释: 欧元区特有成本冲击(能源/进口价格)推升整体 HICP,美国所受冲击较小,幅度差反映冲击暴露与传导差异【假设】
- 竞争性解释: 全球共同通胀因子在两地均存在,幅度差由指数口径与权重结构(HICP vs PCE/CPI)及去年同期基数差异放大,底层动能差异小于读数差异【假设】
- 竞争性解释: 美国整体读数高于核心的结构背离由食品能源等波动项驱动,若此,核心通胀的温和走势更能代表底层动能,欧元区跳升中亦可能含类似波动项成分【假设】
### C2 · 美国增长面信号分化: UNEMPLOYMENT 双锚持平、INDPRO 同比回暖、US_REAL_GDP 同比微降——就业平稳、产出修复与 GDP 读数微降并存,单季微降不足以判定增长环境转弱,也不足以断言加速。
- 依据: 引擎双锚点值面三指标锚值与同比派生;US_REAL_GDP 为季频最新修订口径(事后回顾,非当时首发值)。
- 竞争性解释: 增长实质稳健,GDP 单季波动为常态噪音,就业与工业读数更可靠地指示平稳环境【假设】
- 竞争性解释: 就业为滞后指标,工业产出回暖是修复先行信号,后续就业与 GDP 或跟随走高【假设】
- 竞争性解释: GDP 微降是真实放缓的早期信号,工业读数受部门性/政策性因素(如制造回流)扰动而夸大回暖【假设】
### C3 · 日本政策利率的月均口径仍在紧缩路径: JP_POLICY_RATE 月均序列一年窗净抬升、最近一次登记变动落在最新可得月格;月均序列无法区分政策决议与市场利率漂移,决议日与生效日在引擎面缺席,距上次调整的时长只能按登记月口径给出上下界,不冒充精确决议时点。
- 依据: 引擎 JP_POLICY_RATE 序列与政策路径事件面(policy_window_path);JP_POLICY_TARGET 宣布值口径注册表缺席;月均口径注记随行。
- 竞争性解释: 台阶式月均抬升反映政策目标利率的多次上调(渐进紧缩周期),月均是决议的市场映像【假设】
- 竞争性解释: 部分格变动是市场利率围绕既定目标的波动与流动性季节性,并非每次格变动都对应决议【假设】
- 竞争性解释: 混合情形: 上半年若干格变动对应决议,近月变动部分为决议、部分为市场漂移,决议日数据缺席使两者不可分【假设】
### 机制链 M1 · 
- 环1 [E1] EA_HICP_YOY 同比自 2026-07 的 2.9 连续三期走高至 2026-10 的 4.0(净变动 +1.1 个百分点);同期 EA_REAL_GDP_YOY 仅自 1.19(2026Q2)微升至 1.28(2026Q3)——通胀上行发生在增长低位、温和修复的背景上
- 环2 [E2] 通胀跳升→欧央行政策反应收紧→欧元区利率与汇率重定价→风险资产贴现率上行;观测端 EURUSD 自 2026-11-05 的 1.1235 回落至 2026-11-20 的 1.0973
  - 缺环注记: 引擎无欧央行决议日/政策预期/欧债收益率曲线序列(BUND 序列因 FRED_KEY 缺席采集),中间环为【假设】;仅两端(EA_HICP_YOY 数据与 EURUSD 汇率)引擎可验
- 环3 [E3] 若成本端(能源/进口)驱动主导且增长低位,央行反应或偏温和,风险资产受通胀的直接冲击有限——此环为纯叙事【假设】,以 EA_HICP_YOY 后续路径为证伪观察
### 机制链 M2 · 
- 环1 [E1] JP_POLICY_RATE 月均自 2026-07 的 0.978 升至 2026-10 的 1.227(月均抬升 0.249 个百分点,=+24.9bp);一年窗净 +67bp,最近登记变动 2026-10 格(1.043→1.227,引擎事件增量 18bp)
- 环2 [E2] 政策紧缩→日元融资套息头寸平仓→日股回调与日元升值联动;观测面 USDJPY 处 157-160 高位(2026-11-20 收 158.76)、NIKKEI225 一个月窗回落 12.67%(2026-10-21→2026-11-20)
  - 缺环注记: 引擎无套息交易持仓/资金流序列与 BOJ 决议日数据,平仓机制环为【假设】;仅两端(政策利率序列与 USDJPY/NIKKEI225 行情)引擎可验
- 环3 [E3] 若全球风险因子(波动率抬升)主导日股波动,日本政策路径的解释冗余——纯叙事【假设】,以 NIKKEI225 与 VIX 的联动结构为证伪观察

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### SCN-A · 角色=
- 情景: 假设(非预测): 欧元区通胀动能延续——EA_HICP_YOY 同比在未来两期(至 2027-01)维持在接近当前读数的水平(约 4% 一带)或更高;美国核心通胀(CORE_PCE 同比)维持 3% 上方。此为基准情景,与反例情景 SCN-B 并列呈现。
- 资产方向: EURUSD 走强方向(欧央行紧缩预期主导利差与贴现率渠道;条件式判断,非预测) | 置信档: 纯逻辑推理
- 敏感变量: EA_HICP_YOY, EURUSD
- 证伪: 指标=EA_HICP_YOY | 阈值=EA_HICP_YOY 同比在 2027-01 与 2027-02 两期读数均回落至 3.0 以下,则通胀延续假设被证伪 | 次级=CORE_PCE
- 触发: 月度 HICP 同比 2026-11 或 2026-12 任一期读数不低于 3.8(维持在接近当前 4.0 的水平) | 期限: 2027-01-31
### SCN-B · 角色=
- 情景: 假设(非预测): 欧元区通胀为成本端暂时性冲击——EA_HICP_YOY 同比自当前读数逐步回落至 3% 下方,欧央行无需进一步紧缩。此为反例情景,与基准情景 SCN-A 并列呈现。
- 资产方向: EURUSD 走弱方向(欧元区利差支撑消退,美元相对走强;条件式判断,非预测) | 置信档: 纯逻辑推理
- 敏感变量: EA_HICP_YOY, VIX
- 证伪: 指标=EA_HICP_YOY | 阈值=EA_HICP_YOY 同比升破 4.5 且下一期仍不低于 4.5,则回落假设被证伪 | 次级=UST_10Y
- 触发: 月度 HICP 同比 2026-11 或 2026-12 任一期读数回落至 3.2 或更低(自 4.0 回落至少 0.8 个百分点) | 期限: 2027-01-31

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
| 36 | snapshot_fact | NIKKEI225@2026-11-20 |  |
| 37 | snapshot_fact | EA_HICP_YOY@2026-10-01 |  |
| 38 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 39 | s3_envelope | SZCI@2026-11-20 |  |
| 40 | s3_envelope | CHINEXT@2026-11-20 |  |
| 41 | s3_envelope | HSCEI@2026-11-19 |  |
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
