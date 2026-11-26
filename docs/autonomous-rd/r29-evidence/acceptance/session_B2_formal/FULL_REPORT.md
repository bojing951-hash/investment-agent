# 完整研究报告(一键研究 MVP)

- 问题: 对比角度换一个：2026年11月，美国与欧元区的增长和通胀环境相比3个月前各有什么变化？日本央行政策利率处于什么水平，距离上次调整过了多久？
- run_ok: False | 证据行: 59 | run.ts_utc: 20261121T115819Z

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
| NIKKEI225 | 56436.65 | index_point | 2026-11-20 | PASS | NIKKEI225@2026-11-20 |
| EA_HICP_YOY | 4.0 | percent | 2026-10-01 | WARN | EA_HICP_YOY@2026-10-01 |
| JP_POLICY_RATE | 1.227 | percent | 2026-10-01 | WARN | JP_POLICY_RATE@2026-10-01 |

## L2 机构观点层(VP sidecar 验证面+views 库摘编)

- available=False n=None 隔离=None
- 富内容摘编: views_digest.json(在场机构主张原文,机构面=institution_stated)

## L3 AI 推断层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### CON-1 · 三个月对照的主线是『通胀再上行、增长大体平稳』而非『增长失速』: 美国增长面大体平稳(工业生产回升、失业率持平、GDP 同比微降),通胀读数续升;欧元区增长温和回升而通胀大幅上移,欧元区通胀动能明显强于美国。两地的增长-通胀组合都在向『通胀占主导』方向倾斜,但斜率明显不同。
- 依据: 证据面: 引擎点值锚格面(US_REAL_GDP、UNEMPLOYMENT、INDPRO、CPI、CORE_CPI、CORE_PCE、EA_REAL_GDP_YOY、EA_HICP_YOY)与最新月快照事实(见 evidence_refs);美国 2026-10 通胀格缺去年同月基期,同比以最近有效读数注记,不以邻近值代。
- 竞争性解释: 能源与供给传导解释: 若欧元区通胀上移主要由能源与进口价格传导驱动,则其将随大宗价格回落而回落——将观察到 BRENT_F 领先回落、EA_HICP_YOY 跟随下行、BEI_10Y 保持温和。
- 竞争性解释: 需求黏性解释: 若上移由服务与工资-物价循环驱动,则通胀将具黏性、政策须维持紧缩——将观察到 CORE_PCE 同比持续处于高位且 UNEMPLOYMENT 维持低位。
- 竞争性解释: 基数与口径巧合解释: 若美欧同窗上移主要是基数效应与统计口径的巧合叠加,则后续月份两地通胀相关性将减弱、各自独立波动。
### CON-2 · 日本货币政策面处于渐进正常化通道,且决议日级答案可得: 报告官方记录面(日历实录,基准=用户验收指令实录)载明最近一次目标调整的决议日与生效日及现行目标水平,距上次调整天数按生效日与按决议日两种口径随行;此后最近一次会议(十月末)确认维持,目标未再变。市场月均序列与实录并存互证: 无担保隔夜拆借月均在三个月对照窗内逐级上移,十二个月窗六个变动点均为向上、净上移幅度与三分之二个百分点相当;月均水平与宣布目标属两口径,并存呈现、不互相覆盖。初版判断宣称『决议日级数据不可得』系证据检索范围未含日历实录通道所致,已被同报告官方记录面纠正——缺的是目标历史序列,不是现行宣布值实录。
- 依据: 证据面: 官方记录面(日历实录两条——目标调整实录与维持确认实录,渲染于 MAP_REPORT 政策官方记录面)、引擎点值面与政策路径窗(日本无担保隔夜拆借月均序列,见 evidence_refs);目标口径指标的历史序列与注册表元数据不可得(序列通道),现行宣布值实录在场(日历通道)——两通道分记,不以任一面静默覆盖。
- 竞争性解释: 加息周期延续解释: 若通胀与日元压力持续,后续会议将再上调目标——将观察到新的决议实录与月均序列再台阶上移。
- 竞争性解释: 观望暂停解释: 若增长或金融稳定面转弱,正常化将暂停——将观察到后续会议维持实录与月均序列走平;十月末的确认维持与『延续』『暂停』两读均相容,单次维持不构成裁决。
### CON-3 · 近一月市场呈避险收缩组合: 主要股指普跌、波动率大幅抬升、黄金同步深回撤、美元走强而长端利率小幅回落——利率不升反微降,说明压制并非单纯来自贴现率上行;增长担忧与流动性收缩两类解释均与该组合相容,单月窗口不足以裁决主因。
- 依据: 证据面: 引擎资产月窗复算(美股/日股/欧股股指、黄金、波动率指数、美元指数、美债十年期收益率,两端观测日随行)与利率水平快照(美债两年期与十年期收益率、盈亏平衡通胀率、期限利差、高收益信用利差,见 evidence_refs)。
- 竞争性解释: 增长担忧解释: 若回撤源于盈利预期下修,则高收益利差将走阔并领先或同步于股指、利率因避险回落——与本月利率小幅回落相容。
- 竞争性解释: 流动性去杠杆解释: 若源于保证金与套息去杠杆,则美元与波动率齐升、黄金被抛售换取美元流动性——与本月黄金深回撤、美元走强的组合相容。
- 竞争性解释: 贴现率冲击解释: 若源于实际利率急升,则长端利率应上行而非回落——与本月观测不相容,该侧证据较弱;且引擎本期无 TIPS 序列,实际利率分量分解不可验证,不能完全排除。
### 机制链 CH-1 · 美欧通胀再上行→紧缩定价与流动性压力→风险资产承压+美元走强
- 环1 [E1] 美欧通胀三个月上移: EA_HICP_YOY 同比 2.9(2026-07)→4.0(2026-10);美国 CPI 同比 3.3(2026-07)→最近有效读数 3.72(2026-09,2026-10 格缺去年同月基期,同比不可得);CORE_CPI 同比 2.47(2026-07)→最近有效 2.57(2026-09);CORE_PCE 同比 3.04(2026-06)→3.12(2026-09)。
- 环2 [E2] 通胀上移与利率高位并存: UST_10Y 5.04%、UST_2Y 4.76%(2026-11-19)、BEI_10Y 2.15%(2026-11-20)、CURVE_2S10S 0.29pp(2026-11-20)——盈亏平衡端温和,名义高位的分量结构本期无法分解验证。
  - 缺环注记: 缺失环【假设】: 通胀读数→政策紧缩预期→利率中枢的映射为假设——引擎面无政策预期曲线,且 TIPS_10Y 序列本期缺席,实际利率/盈亏平衡分解不可验证,该环仅能以利率水平与通胀同向并存间接支持。
- 环3 [E3] 高贴现率与流动性压力压低风险资产与非孳息资产: 近一月 SPX -10.92%、NIKKEI225 -12.67%、DAX -3.28%、GOLD_F -15.29%、VIX +115.17%、DXY +1.99%(月窗 2026-10-21→2026-11-20);UST_10Y 同窗 -0.09pp(至 2026-11-19)——利率不升反微降,与『增长/流动性驱动』的相容度高于『纯贴现率驱动』。
### 机制链 CH-2 · 日本渐进正常化→日元与日股重定价(与美欧通胀链并列的竞争通道)
- 环1 [E1] JP_POLICY_RATE 月均 0.727(2026-04)→0.978(2026-07)→1.227(2026-10);12 个月政策路径窗(2025-11-21..2026-11-21)六个向上变动点 +8/+17/+11/+14/+7/+18bp、净变动 +67bp;官方实录面另载 2026-09-18 决议、2026-09-24 生效的目标调整(目标 1.25)——月均 2026-09/2026-10 变动点与该决议-生效窗相容。
- 环2 [E2] 日元低位与日股深回撤并存: USDJPY 159.71(2026-11-20)、NIKKEI225 月窗 -12.67%(2026-10-21→2026-11-20,月窗行内主要股指中最深)——若正常化传导成立,USDJPY 应趋势回落(日元走强)而日股估值承压;当前 USDJPY 仍处高位,与『正常化已被充分定价』的解释同样相容。
  - 缺环注记: 缺失环【假设】: 政策利率→日元/日股的传导为假设——引擎无日债收益率历史序列与跨境资金流序列,该环仅能以同窗观测并存支持,方向不可断。
- 环3 [E3] 日股跌幅深于美欧股指,存在『日本自身政策+日元弱势压力』的附加解释,但单月窗口、单一横截面不可区分其与全球风险偏好回落(链一)的主次。

## L4 条件情景层(Agent 席真产·全文内联)

- produced=True attribution=ai_inferred
### S1-通胀惯性延续 · 角色=基准(主解释延续)
- 情景: 假设(非预测): 欧元区与美国通胀惯性延续(EA_HICP_YOY 维持 3.5 以上、美国核心通胀黏性),政策维持紧缩立场,增长温和放缓但不衰退,波动率中枢维持高位。
- 资产方向: 股指(SPX/DAX/NIKKEI225)承压、VIX 中枢维持高位、DXY 偏强、黄金反弹乏力;现金与短久期相对占优。 | 置信档: 有相关证据
- 敏感变量: EA_HICP_YOY, CPI
- 证伪: 指标=EA_HICP_YOY | 阈值=EA_HICP_YOY 自 2026-10 的 4.0 回落至 2.5 以下并连续两个月维持(通胀惯性前提失效)
- 触发: EA_HICP_YOY 保持 3.5 以上且 VIX 月末值维持 30 以上 | 期限: 2027-02-21
### S2-通胀快速回落→风险偏好修复 · 角色=反例(与基准并列检验)
- 情景: 假设(非预测): 通胀回落速度快于政策反应(基数与供给修复主导),市场转向宽松定价,重演 2022-06 类比锚后 12 个月风险资产修复的历史相似路径(历史记录,非预测)。
- 资产方向: 股指与黄金反弹、DXY 走弱、VIX 回落(历史相似样本 2022-06 锚月末→2023-06 月末: SPX +17.57%、日经225 +25.75%、黄金期货 +6.76%)。 | 置信档: 有历史相似证据
- 敏感变量: EA_HICP_YOY, BEI_10Y
- 证伪: 指标=BEI_10Y | 阈值=BEI_10Y 升破 2.60 并连续两个月维持,且 EA_HICP_YOY 同期维持 4.0 以上(通胀预期脱锚,宽松重定价前提失效) | 次级=EA_HICP_YOY
- 触发: EA_HICP_YOY 回落至 3.0 以下且 BEI_10Y 维持 2.2 附近或更低 | 期限: 2027-02-21

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
| 32 | snapshot_fact | NIKKEI225@2026-11-20 |  |
| 33 | snapshot_fact | EA_HICP_YOY@2026-10-01 |  |
| 34 | snapshot_fact | JP_POLICY_RATE@2026-10-01 |  |
| 35 | s3_envelope | SZCI@2026-11-20 |  |
| 36 | s3_envelope | CHINEXT@2026-11-20 |  |
| 37 | s3_envelope | HSCEI@2026-11-20 |  |
| 38 | s3_envelope | NVDA@2026-11-20 |  |
| 39 | s3_envelope | AAPL@2026-11-20 |  |
| 40 | s3_envelope | MSFT@2026-11-20 |  |
| 41 | s3_envelope | TLT@2026-11-20 |  |
| 42 | s3_envelope | IEF@2026-11-20 |  |
| 43 | s3_envelope | SHY@2026-11-20 |  |
| 44 | s3_envelope | HYG@2026-11-20 |  |
| 45 | s3_envelope | LQD@2026-11-20 |  |
| 46 | s3_envelope | GBPUSD@2026-11-20 |  |
| 47 | s3_envelope | WTI_F@2026-11-20 |  |
| 48 | s3_envelope | GLD@2026-11-20 |  |
| 49 | s3_envelope | USO@2026-11-20 |  |
| 50 | s3_envelope | EEM@2026-11-20 |  |
| 51 | s3_envelope | EZU@2026-11-20 |  |
| 52 | s3_envelope | FEZ@2026-11-20 |  |
| 53 | s3_envelope | EWU@2026-11-20 |  |
| 54 | s3_envelope | EWG@2026-11-20 |  |
| 55 | s3_envelope | EWJ@2026-11-20 |  |
| 56 | s3_envelope | INDA@2026-11-20 |  |
| 57 | s3_envelope | FXI@2026-11-20 |  |
| 58 | s3_envelope | BTC@2026-11-20 |  |
| 59 | s3_envelope | HY_IG_DIFF@2026-11-19 |  |

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
