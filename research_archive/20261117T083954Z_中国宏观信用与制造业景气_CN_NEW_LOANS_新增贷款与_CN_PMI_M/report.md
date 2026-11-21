# 一键研究报告(零模型编排 v2.0)
- 问题: 中国宏观信用与制造业景气: CN_NEW_LOANS 新增贷款与 CN_PMI_MFG 制造业PMI 对 CHINEXT 创业板指与 FXI 中国大盘股的影响
- 运行: 20261117T083954Z @ None
- 快照: research_snapshot_20261112_v2 (target 20261112)
- 数据门(gate_a): 9/9 信封步非 OK(DEGRADED)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知
- 数据需求(运行前冻结): 必要 4 项(问题命中,规格=序列/最低覆盖60 观测),缺口 0 项;可选面缺席=降级披露不构成缺口

## 四层区分

### L1 事实层 available=True
- FXI = 33.92 usd @2026-11-11 [质量:PASS] [来源:snapshot_fact:FXI@2026-11-11]
- CHINEXT = 2572.0672 index_point @2026-11-11 [质量:PASS] [来源:snapshot_fact:CHINEXT@2026-11-11]
- CN_PMI_MFG = 49.3 index_point @2026-10-01 [质量:WARN] [来源:snapshot_fact:CN_PMI_MFG@2026-10-01]
- CN_NEW_LOANS = 12734.0 cny_100m @2026-09-01 [质量:DEGRADED] [来源:snapshot_fact:CN_NEW_LOANS@2026-09-01]

### L2 机构观点层 available=True n=17
- VIEW-20261110-001: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'INSUFFICIENT_EVIDENCE', 'B': 'INSUFFICIENT_EVIDENCE', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261110-002: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'PARTIALLY_SUPPORTED', 'B': 'INSUFFICIENT_EVIDENCE', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261110-003: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'MIXED', 'B': 'MIXED', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261110-004: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'INSUFFICIENT_EVIDENCE', 'B': 'INSUFFICIENT_EVIDENCE', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261110-005: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'PARTIALLY_SUPPORTED', 'B': 'MIXED', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261110-006: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'PARTIALLY_SUPPORTED', 'B': 'MIXED', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261110-007: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'INSUFFICIENT_EVIDENCE', 'B': 'INSUFFICIENT_EVIDENCE', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261110-008: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'INSUFFICIENT_EVIDENCE', 'B': 'INSUFFICIENT_EVIDENCE', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261110-009: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'INSUFFICIENT_EVIDENCE', 'B': 'PARTIALLY_SUPPORTED', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261110-010: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'PARTIALLY_SUPPORTED', 'B': 'INSUFFICIENT_EVIDENCE', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261110-011: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'INSUFFICIENT_EVIDENCE', 'B': 'INSUFFICIENT_EVIDENCE', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261111-001: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'INSUFFICIENT_EVIDENCE', 'B': 'INSUFFICIENT_EVIDENCE', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261111-002: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'PARTIALLY_SUPPORTED', 'B': 'INSUFFICIENT_EVIDENCE', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261111-003: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'MIXED', 'B': 'INSUFFICIENT_EVIDENCE', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261111-004: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'INSUFFICIENT_EVIDENCE', 'B': 'INSUFFICIENT_EVIDENCE', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261111-005: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'INSUFFICIENT_EVIDENCE', 'B': 'PARTIALLY_SUPPORTED', 'C': 'INSUFFICIENT_EVIDENCE'}
- VIEW-20261111-006: view_label=INSUFFICIENT_EVIDENCE 阶段摘要={'A': 'MIXED', 'B': 'MIXED', 'C': 'INSUFFICIENT_EVIDENCE'}

### L3 AI推断层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **CON-1**: 矛盾: 教科书直觉『制造业景气扩张利多股指』在样本内方向相反——PMI>50信号月后的CHINEXT次月月均-0.74%、上涨概率39%,PMI<50信号月后月均+2.14%、上涨概率58%,组间差异不显著(Welch p=0.092,MW p=0.120);且两相位均现极端月——PMI低于荣枯线的信号相位内含最大涨幅月(2024-09=+37.6%),两个并列样本最大跌幅月落在PMI高于荣枯线的信号相位(信号月2026-06 PMI=50.3与2026-09 PMI=50.1,其收益月当月PMI均<50)。
  - 依据: 方法与数据: 本席自算(脚本research_seat_calc.py第二节,分组阈值=荣枯线50两侧严格分组即PMI>50与PMI<50,PMI=50.0持平月3个=2018-11/2020-01/2026-05不入任一组,组内统计=次月月均收益与上涨概率,显著性=Welch t与Mann-Whitney U双检)。当前证据锚: CN_PMI_MFG=49.3@2026-10-01,CHINEXT=2572.07@2026-11-11。
  - 竞争性解释1: 逆周期政策响应: 宏观越弱→政策刺激概率与力度越大→风险资产抢跑反弹(『坏消息=好消息』);旁证: L2央行货政报告的结构性工具扩容描述(VP标签INSUFFICIENT_EVIDENCE)
  - 竞争性解释2: 均值回归/超卖反弹的技术效应,与宏观无关——相位内σ高达9.81%,极端月主导均值
  - 竞争性解释3: 多重比较噪声: ~40个相关格中挑出的最大格,符号在k=2翻转(PMI水平k=2对CHINEXT为-0.176),FXI中不存在(p=0.250)
  - 竞争性解释4: 利率渠道反向: PMI扩张期常对应货币收紧或贸易摩擦升级期(如2018),估值承压压过盈利改善【假设】
  - 证据: CN_PMI_MFG@2026-10-01, CHINEXT@2026-11-11
- **CON-2**: 矛盾: 信用端处226个月全史最深收缩区(CI=-3.58万亿=第4.9百分位,即仅4.9%概率的历史月份深于此值,2026-10对实体贷款-5846亿,史上一贯负值月仅6个),但股指未现与信用收缩一致的稳定方向——CHINEXT 2025-08以来既现+24.1%月(2025-08)也现-23.0%月(2026-07/10),CI全部先行相关|r|≤0.10。
  - 依据: 方法与数据: CI=对实体经济人民币贷款的12月滚动和(单位亿,历史序列通道=macro采集档data.CN_NEW_LOANS.series月频全史,事实通道当期=CN_NEW_LOANS@2026-09-01,两通道发布滞后如实披露)。当前证据锚: CN_NEW_LOANS=12734亿@2026-09-01,CHINEXT=2572.07@2026-11-11。
  - 竞争性解释1: 贷款收缩是需求端信号(企业/居民借贷意愿弱)而非流动性供给收缩——股市由流动性与预期驱动,对需求疲弱的反应两义(盈利利空vs政策利好)
  - 竞争性解释2: 股市前瞻定价: 信用收缩已被价格吸收(有效市场),月频残差无可测增量信息
  - 竞争性解释3: 口径混杂: 对实体贷款可被政府债券/企业债/非标置换(社融内部结构轮动),股市或对社融总量而非贷款分量反应——引擎无社融序列不可验【假设】
  - 竞争性解释4: FXI为美元离岸定价,与境内信用周期近乎脱锚(r(CHINEXT,FXI)=0.351),『信用→股市』在FXI端本就不应成立
  - 证据: CN_NEW_LOANS@2026-09-01, CHINEXT@2026-11-11, FXI@2026-11-11
- **CON-3**: 矛盾: 两宏观信号自身仅弱同步(PMI水平vs CI同月r=+0.204,p=0.026)——『宏观信用×制造业景气』并非单一共同宏观因子,同一『中国宏观』标签下至少两条弱耦合路径。
  - 依据: 方法与数据: PMI水平与CI同月皮尔逊相关(历史序列通道,本席自算,research_seat_calc.py第三节)。当前证据锚: CN_PMI_MFG=49.3@2026-10-01,CN_NEW_LOANS=12734亿@2026-09-01。
  - 竞争性解释1: 统计性质差异: PMI=环比动能调查(软数据/快/季调),贷款=行为硬数据(慢/强季节/含偿还项),相位天然错位
  - 竞争性解释2: 决策主体不同: 制造业景气由出口订单与产能驱动,信用投放由银行供给与监管指导驱动,两者可政策性脱钩(如信贷窗口指导放松而订单未起)
  - 竞争性解释3: 真实经济即分化: 信用弱主因地产/平台债务收缩,制造业(尤其新质生产力方向)受定向信贷支持——L2世行简报『投资出口导向模式到极限/结构转型』与此相容(VP标签INSUFFICIENT_EVIDENCE)
  - 证据: CN_PMI_MFG@2026-10-01, CN_NEW_LOANS@2026-09-01
- **机制链 MC-1**: 
  - E1 E1环: PMI相位与次月收益分布可由引擎序列确定性刻画——PMI<50后CHINEXT月均+2.14%/胜率58%/σ9.81% vs PMI>50后-0.74%/39%/7.50%,Welch p=0.092、MW p=0.120不显著(本席自算,严格<50 vs >50分组,n=48/67,2016-12..2026-10)。 [证据: CN_PMI_MFG@2026-10-01, CHINEXT@2026-11-11]
  - E2 E2环: 『PMI走弱→政策宽松加码』——引擎无中国政策利率/公开市场操作/财政脉冲序列,该环无法在本引擎验证;L2面央行Q2货政报告(VP-VIEW-20261111-001)仅描述结构性工具(1万亿民营企业再贷款/科技再贷款扩容)与汇率稳定立场,标签INSUFFICIENT_EVIDENCE,只作旁证不作验证。 [缺失环: 缺失环=政策力度序列(降准/利率/财政)不在引擎,『弱数据触发政策宽松』为【假设】。]
  - E3 E3环: 政策宽松落地→风险偏好与流动性改善→高β成长股(CHINEXT)弹性最大。纯叙事;若该链真,信用端应在政策后可观测回升。 [证伪指标: CN_NEW_LOANS]
- **机制链 MC-2**: 
  - E1 E1环: CI(万亿)对CHINEXT/FXI月收益先行相关k=1:-0.009/-0.095,k=2:+0.014/-0.065,全部p>0.30;CI>0vs<0相位k=2次月Welch p=0.950/0.574;NW回归(控制收益滞后)|t|≤1.6——月频上信用脉冲→股指方向传导在本窗口不可识别(本席自算,n=117-118)。 [证据: CN_NEW_LOANS@2026-09-01, CHINEXT@2026-11-11, FXI@2026-11-11]
  - E2 E2环: 『CI→企业融资条件→盈利与流动性→股指』中间变量链——引擎无企业盈利/社融总量/信用利差(中国)序列,中间环断裂;境外信用利差(HY_OAS族)只有美欧序列,不可移植(近零渠道纪律)。 [缺失环: 缺失环=中国社融总量/企业盈利/境内信用利差序列,『信用→盈利→股价』中间环为【假设】。]
  - E3 E3环: 传导或被结构性对冲——贷款负增长部分反映政府债券/直接融资对银行贷款的置换(社融内部轮动),股市总量层面可能对社融而非贷款反应。纯叙事。 [证伪指标: CN_NEW_LOANS]
- **机制链 MC-3**: 
  - E1 E1环: FXI与CHINEXT月收益r=0.351、同向67%、2026-07单月分化约38.5pp——两资产1-r²≈88%方差互不共享(本席自算,n=119)。 [证据: FXI@2026-11-11, CHINEXT@2026-11-11]
  - E2 E2环: FXI美元回报≈境内资产本币回报×USDCNY变动±离岸/在岸估值差——引擎仅有USDCNY单点快照(2026-11-11)无历史序列,汇率分解不可算。 [缺失环: 缺失环=USDCNY月度历史序列不在引擎,汇率贡献分解为【假设】性表述。]
  - E3 E3环: FXI波动或主要受全球风险偏好(VIX/DXY/美债)驱动,境内宏观景气为次级因子——若真,FXI对中国宏观相位应系统性钝感(E1已见: PMI相位k=1 FXI差异p=0.250vs CHINEXT的0.092)。 [证伪指标: VIX]
- **机制链 MC-4**: 
  - E1 E1环: 对实体贷款强季节性——1月均值27341亿=全史月均11234亿的2.4倍;负值月史仅6个且集中于7月×3/10月×2/4月×1(还款季);故本档禁用含负基数的YoY百分比、改用同比差/12月均值比/CI(本席自算,n=226全史)。 [证据: CN_NEW_LOANS@2026-09-01]
  - E2 E2环: 季节性由银行『开门红』投放与季度考核节奏驱动,且本口径剔除了非银与票据对消——引擎无银行行为数据,机制归因为推断层。 [缺失环: 缺失环=银行投放行为/票据贴现序列不在引擎,季节性成因环为【假设】。]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **SCN-1**()
  - 情景: 假设(非预测): 2026-11至2027-02宏观组合延续当前双重弱状态——CN_PMI_MFG在49上下(<50)且对实体信用脉冲CI维持深负(-3至-4万亿量级),无超常规政策冲击亦无系统性崩塌。此为基准情景。
  - 资产方向判断: CHINEXT与FXI方向均中性(不可判),但月度波动维持放大档(CHINEXT月σ参考9.8%量级vs扩张相位的7.5%);不建立任何单边方向头寸判断(置信: 有相关证据) 
  - 敏感变量: CN_PMI_MFG, CN_NEW_LOANS
  - 证伪指标: CHINEXT 阈值 2026-12..2027-02连续三个月月收益同号(全正或全负)且三个月累计绝对涨跌幅>15%——出现稳定单边即证伪『方向不可判、仅波动放大』
  - 触发条件: CN_PMI_MFG连续两月≥50.5,或按CN_NEW_LOANS计算的CI(12月滚动和同比变化)回升至-1万亿以上——宏观前提转换,须重开判断(时限 2027-01-31)
- **SCN-2**()
  - 情景: 假设(非预测): 信用深收缩与PMI走弱触发2024-09式超常规政策组合(全面宽松/准财政扩张),且政策在信用端可观测落地。此为反例情景一。
  - 资产方向判断: CHINEXT显著上行(高β成长弹性最大,参考2024-09=+37.6%/2019-02=+25.1%的相位极值月),FXI同向上行但幅度次之(置信: 有相关证据) 
  - 敏感变量: CN_NEW_LOANS, CN_PMI_MFG
  - 证伪指标: CN_NEW_LOANS 阈值 政策触发后3个月内CI未回升至0以上、且未再现单月≥25000亿的对实体贷款——『政策响应传导至信用端』链被证伪(届时上行判断失去机制支点,降级为纯流动性事件)
  - 触发条件: 单月CN_NEW_LOANS≥25000亿(2026-03=31522亿后首见该量级)且次月CN_PMI_MFG≥50(时限 2027-06-30)
- **SCN-3**()
  - 情景: 假设(非预测): 深收缩延续且政策响应不足或缺席,信用收缩自我强化(需求疲弱→盈利下修→风险偏好恶化),延续2026-07与2026-10两度单月-23.0%所处的环境。此为反例情景二。
  - 资产方向判断: CHINEXT下行(高β成长首当其冲,参考样本-23.0%极值月2026-07/10,两月均属PMI>50信号相位),FXI因美元/离岸大盘结构跌幅预计较浅(2026-07曾现FXI+15.5%与CHINEXT-23.0%并存)(置信: 有相关证据) 
  - 敏感变量: CN_NEW_LOANS, CHINEXT
  - 证伪指标: CHINEXT 阈值 2027-01..2027-03若CHINEXT月收益均>+1%且无单月<-10%——『收缩自我强化下行』未现,本情景被证伪
  - 触发条件: CN_NEW_LOANS连续三个月为负,或按其计算的CI跌破-5万亿(逼近历史极值-5.24万亿)(时限 2027-02-28)
- **SCN-4**()
  - 情景: 假设(非预测): 全球风险偏好与人民币汇率主导FXI端,境内宏观弱而不崩,两指数延续样本内1/3月份分化、月收益r≈0.35的结构——『中国股票』不是单一资产类别。此为结构性反例情景。
  - 资产方向判断: FXI相对CHINEXT占优(美元计价+离岸大盘+全球流动性敞口;境内宏观相位对FXI钝感,p=0.250vs CHINEXT的0.092);CHINEXT自身方向不可判(置信: 有相关证据) 
  - 敏感变量: FXI, USDCNY
  - 证伪指标: FXI 阈值 2026-12..2027-02三个月FXI与CHINEXT月收益同向比例3/3且FXI三个月累计涨幅≤CHINEXT——分化结构与相对占优同时未现,本情景被证伪
  - 触发条件: USDCNY(人民币)单月升值幅度>2%(资金回流境内资产),或VIX>30(全球避险致FXI承压)——分化方向反转,须重估(时限 2027-02-28)

## 语义审查(席位待唤起)

- **叙事语义未经独立裁决**——定性推断/条件情景在文;常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后方可去掉本披露(章程 §4b/§8)

## Agent 判断落位

- attached=True(schema 1.1;violations=0)

## 步骤台账

- [OK |不适用] S1_decompose 
- [OK |语义✔] S2_doctor 
- [OK |语义✔] S3_overview_CN 
- [OK |语义✔] S3_changes 
- [OK |语义✔] S4_history_FXI 
- [OK |语义✔] S4_history_CHINEXT 
- [OK |语义✔] S4_history_CN_PMI_MFG 
- [OK |语义✔] S4_history_CN_NEW_LOANS 
- [OK |语义✔] S5_compare 命中 4 个指标,compare 仅取注册表序前 2(FXI,CHINEXT);其余 CN_PMI_MFG,CN_NEW_LOANS 以 L1 事实行呈现,如需对比另行单跑
- [OK |语义✔] S6_analog 
- [OK |不适用] S7_mode_gate 
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(65 行)

- snapshot_fact:FXI@2026-11-11 → FXI
- snapshot_fact:CHINEXT@2026-11-11 → CHINEXT
- snapshot_fact:CN_PMI_MFG@2026-10-01 → CN_PMI_MFG
- snapshot_fact:CN_NEW_LOANS@2026-09-01 → CN_NEW_LOANS
- vp_sidecar:VP-VIEW-20261110-001 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261110-002 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261110-003 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261110-004 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261110-005 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261110-006 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261110-007 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261110-008 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261110-009 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261110-010 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261110-011 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261111-001 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261111-002 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261111-003 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261111-004 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261111-005 [INSUFFICIENT_EVIDENCE]
- vp_sidecar:VP-VIEW-20261111-006 [INSUFFICIENT_EVIDENCE]
- s3_envelope:SPX@2026-11-11 → SPX
- s3_envelope:NDX@2026-11-11 → NDX
- s3_envelope:RUT@2026-11-11 → RUT
- s3_envelope:SHCOMP@2026-11-11 → SHCOMP
- s3_envelope:SZCI@2026-11-11 → SZCI
- s3_envelope:HSI@2026-11-11 → HSI
- s3_envelope:HSCEI@2026-11-11 → HSCEI
- s3_envelope:NIKKEI225@2026-11-11 → NIKKEI225
- s3_envelope:DAX@2026-11-11 → DAX
- s3_envelope:CAC40@2026-11-11 → CAC40
- s3_envelope:VIX@2026-11-11 → VIX
- s3_envelope:NVDA@2026-11-11 → NVDA
- s3_envelope:AAPL@2026-11-11 → AAPL
- s3_envelope:MSFT@2026-11-11 → MSFT
- s3_envelope:TLT@2026-11-11 → TLT
- s3_envelope:IEF@2026-11-11 → IEF
- s3_envelope:SHY@2026-11-11 → SHY
- s3_envelope:HYG@2026-11-11 → HYG
- s3_envelope:LQD@2026-11-11 → LQD
- s3_envelope:DXY@2026-11-11 → DXY
- s3_envelope:EURUSD@2026-11-11 → EURUSD
- s3_envelope:GBPUSD@2026-11-11 → GBPUSD
- s3_envelope:USDJPY@2026-11-11 → USDJPY
- s3_envelope:USDCNY@2026-11-11 → USDCNY
- s3_envelope:GOLD_F@2026-11-11 → GOLD_F
- s3_envelope:SILVER_F@2026-11-11 → SILVER_F
- s3_envelope:WTI_F@2026-11-11 → WTI_F
- s3_envelope:BRENT_F@2026-11-11 → BRENT_F
- s3_envelope:GLD@2026-11-11 → GLD
- s3_envelope:USO@2026-11-11 → USO
- s3_envelope:EEM@2026-11-11 → EEM
- s3_envelope:EZU@2026-11-11 → EZU
- s3_envelope:FEZ@2026-11-11 → FEZ
- s3_envelope:EWU@2026-11-11 → EWU
- s3_envelope:EWG@2026-11-11 → EWG
- s3_envelope:EWJ@2026-11-11 → EWJ
- s3_envelope:INDA@2026-11-11 → INDA
- s3_envelope:BTC@2026-11-10 → BTC
- s3_envelope:HY_OAS@2026-11-09 → HY_OAS
- s3_envelope:BB_OAS@2026-11-09 → BB_OAS
- s3_envelope:B_OAS@2026-11-09 → B_OAS
- s3_envelope:CCC_OAS@2026-11-09 → CCC_OAS
- s3_envelope:IG_OAS@2026-11-09 → IG_OAS
- s3_envelope:HY_IG_DIFF@2026-11-09 → HY_IG_DIFF
