# Charter 7 三案例执行手册(Agent A 执行设计, P0 修复前版本)

- 作者: Agent A(全球宏观研究席)。性质: **执行设计, 零研究结论**——本文只做"分析要求→引擎能力"映射, 不预判任何市场/机制判断。
- 基线: 分支 dev/charter7-research-v1 @cca2e4a(只读); 快照 research_snapshot_20261110_v2(10yr 深度)。
- 实测面: catalog 76 序列 + facts 96 单值节点; analog/compare/history/changes/overview 均已实跑探针核验(本文所有"命令→字段"映射基于实际输出, 非臆测)。
- 前置依赖: **案例B 全部步骤 blocked-by-P0**(独立验证员复现七大正确性问题: analog 维度标准/aftermath 口径/候选重叠等, 引擎可能要修); 修后须重跑边界探针再执行。案例A/C 大部分步骤不依赖 P0。

## 0. 数据双层结构(一切映射的前提)

| 层 | 内容 | 可用能力 |
|---|---|---|
| 序列层(catalog 76) | 有 dates/values 历史: US 宏观月频 10yr(CPI/CORE_PCE/UNEMP/NFP/AHE/INDPRO/RSAFS/JTSJOL/UMCSENT/FED_FUNDS n=118-120)、日频利率 10yr(UST_2/5/10/30Y·TIPS_5/10Y·BEI_5/10Y·CURVE_2S10S n≈2496)、OAS 族 3yr(HY/IG/B/BB/CCC n=783-784, 2023-11 起)、ICSA 周频 521、US_REAL_GDP 季频 40、SPX_CAPE 1881 起 n=1750、SPX_PE_TTM 1871→**2026-06 止**、US/CN/JP 股指(DXY/USDCNY/EURUSD/USDJPY/GBPUSD/GOLD_F/WTI_F/BRENT_F/SILVER_F 等); CN 股指(SHCOMP/SZCI/CHINEXT)**仅 2026-01 起 n=204**; ECB_DFR 阶梯 n=69(1999→2026-09); JP_POLICY_RATE n=495(1985→2026-09) | history/compare/analog 全统计 |
| 单值 fact 层(96) | 仅最新值+observation_date, **无历史**: CN_LPR_1Y/5Y(2026-10)、CN_PMI_MFG(2026-10)、CN_NEW_LOANS(2026-09)、MARGIN_BAL/SH_PE/SH_AMOUNT/成交额(2026-11)、CN_CPI_YOY/CN_PPI_YOY(**2025-08, 陈旧15月**)、EA_HICP_YOY(**2025-12, 陈旧11月**)、JGB2Y/5Y/10Y(2026-11-06 新鲜单点) | 仅 overview 节点引用(+changes 若纳入); **不能** compare/lag/窗口/interval_change |

登记未采集(注册表有、快照无): DFF/DFEDTARL/U、REAL_10Y/5Y/SHORT、HY_IG_DIFF、NFP_MOM_K、WTI_SPOT_M、ZQ_F1_PRICE/ZQ_IMPLIED_AVG、BUND_2Y/10Y、DAX、CAC40、ECB_MRO、JGB2/5/10Y(序列)、JP_CPI_TOKYO_YOY、CN_OMO_7D(缺)、CN_SF_FLOW(缺)、SB_FLOW。other 族别名(WTI/GOLD/SILVER/BRENT/CNY=X/JPY=X/GBPUSD=X): 计算路径结构性禁入(compare 拒算 rc=1), 展示层引用必须用 _F 期货或 ETF 正名。

---

## 案例A 全球宏观现状(US/CN/EA/JP)

### A-1 七维 × 四经济体可得性矩阵

图例: ◎=序列层(全统计) / ○=单值 fact(仅 overview) / △=部分 / ✗=缺

| 维度 | US | CN | EA | JP |
|---|---|---|---|---|
| 增长 | ◎ INDPRO/RSAFS(月, DEGRADED 止 2026-09)+US_REAL_GDP(季)+ICSA/NFP | ○ CN_PMI_MFG(新鲜); ✗ CN GDP/工业 | ✗ | ✗ |
| 通胀 | ◎ CPI/CORE_CPI/CORE_PCE(月)+BEI_5Y/10Y(日, 市场口径) | ○ CN_CPI/PPI_YOY(**陈旧 2025-08, 纪律10 必须明示滞后**) | ○ EA_HICP_YOY(陈旧 2025-12) | ✗(JP_CPI_TOKYO_YOY 登记未采集) |
| 就业 | ◎ UNEMPLOYMENT/NFP/AHE/JTSJOL/ICSA | ✗ | ✗ | ✗ |
| 政策 | ◎ FED_FUNDS(月 10yr; DFF/DFEDTAR 登记未采集) | ○ CN_LPR_1Y/5Y(2026-10); CN_OMO_7D 缺 | ◎ ECB_DFR(阶梯序列 1999→) | ◎ JP_POLICY_RATE(1985→, DEGRADED) |
| 利率 | ◎ UST 全曲线+TIPS+BEI+CURVE | ✗(无 CN 国债收益率序列) | ✗(BUND 登记未采集, 连单值都无) | ○ JGB 2/5/10Y 单点(2026-11-06; 已知边界: 单点无历史) |
| 信用 | △ HY_OAS 族仅 3yr(FRED 源端限制, 窗口警示随行) | ✗ | ✗ | ✗ |
| 流动性 | ✗(无 M2/SOFR/央行表; ZQ 期货登记未采集) | ○(SH_AMOUNT/MARGIN_BAL/两所成交=市场活跃度单值, 引用须标"非宏观流动性") | ✗ | ✗ |

执行命令模式: `overview --economy US,CN,EA,JP` → data.economies.{eco}.metrics[] 每节点引用 value+unit+observation_date+quality_status(纪律1/2/3/10); 缺席节点 presence:"missing" 如实转述(纪律2)。

### A-2 资产类映射(股/债/汇/黄金/能源/估值)

- 股: US ◎(SPX/NDX/RUT 10yr); JP ◎(NIKKEI225 10yr); CN △(SHCOMP/SZCI/CHINEXT 仅 10 个月——1年以上窗口 blocked-by-P2); EA △(**仅 ETF 代理** EZU/EWG/FEZ, is_proxy:true 纪律6 代理身份强制随行; DAX/CAC40 登记未采集); HK(HSI/HSCEI 2025-07 起)。
- 债: US ◎(UST 曲线序列+TLT/IEF/SHY/LQD/HYG ETF); 他经济体 ✗ 序列(JGB 单点 fact; 无 BUND/EA 债序列)。
- 汇: ◎ DXY+USDCNY/EURUSD/USDJPY/GBPUSD 全 10yr; unit_subfamily:"fx" 方向语义按 calc 原文(纪律: USDJPY 涨=美元升值)。
- 黄金: ◎ GOLD_F(期货)+GLD(ETF); SILVER_F 佐证; 别名 GOLD=other 族禁算。
- 能源: **WTI_F/BRENT_F(期货, GLOBAL, 10yr)**+USO(ETF); 别名 WTI/BRENT=other 族禁算(compare rc=1, 引用必须走 _F); WTI_SPOT_M 登记未采集。
- 估值: US △(SPX_CAPE 1881 起 WARN / SPX_PE_TTM **止 2026-06** DEGRADED / SPX_PB 登记不可得); CN ○(SH_PE 单值 2026-11-09 新鲜); **EA/JP ✗**(无任何估值序列)。
- 命令: `changes` → data.by_asset_class.{equity_index|bond_etf|fx_rate|fx_index|commodity_futures|spot_commodity_etf|volatility_index|credit_spread} 每条 changes[]{value,change_unit,basis_date,end_date,window_semantics,formula}(纪律: pp≠%不可混, 禁裸数字)。

### A-3 过去 1月/1年/5年 变化(已知缺口+已实测替代路径)

- 现状: `changes` 只有 week/mtd/ytd 三窗(CHANGE_WINDOWS L60)。**1月/1年/5年窗=统计类缺口, 预判 P2**。
- **替代路径(本手册实测可行, 全程引擎计算零自算)**:
  `compare --metrics X,X --start <T-k> --end <T>` → sides[0].interval_change_common_window{basis_date(严格早于窗起点的末观测, 纪律14 同源), basis_value, end_date, end_value, pct_change(价格类)|pp_change+bp_change(利率类), formula}。
  实测: SPX 1年窗 basis 2025-10-31→end 2026-11-06 pct 7.8457; FED_FUNDS 5年窗 pp +3.80/bp 380。
  纪律: ①自配对输出的相关性字段(恒=1)与 alignment **不引用不转述**; ②月频宏观 end=窗内末月值, 观测滞后随行; ③阶梯序列(ECB_DFR/JP_POLICY_RATE)end 取窗内末次调息值, "区间无变化"须引 basis/end 原值而非自算持平。
- 窗口边界: CN 股指 1年/5年 blocked-by-P2(数据: 序列仅 2026-01 起); SPX_PE_TTM 窗末值止 2026-06(如实); OAS 族 5年 blocked-by-P2(数据: 仅 3yr)。
- 若不做替代: 标记 blocked-by-P2 待 changes 窗口参数化。**建议执行时采用替代路径**(纪律14 已背书该口径)。

### A-4 当前主要矛盾 + 跨经济体相互影响(compare 组合清单)

全部 `compare --metrics A,B`(必要时 --start/--end 限窗; 预期字段: pearson_returns.value+n、change_basis(pp/pct 口径)、alignment{n_common,a_dropped,b_dropped,mode,warnings}、research_mode_gate 三态——纪律5/12 逐字转述):

| 组合 | 支撑什么 | 预期限制 |
|---|---|---|
| CORE_PCE×FED_FUNDS | 通胀×政策(月×月 n≈119) | 月频对齐 |
| TIPS_10Y×UST_10Y | 通胀分解(名义−实际) | 日×日 10yr |
| BEI_10Y×FED_FUNDS | 市场通胀预期×政策 | 跨频月网格披露 |
| CURVE_2S10S×HY_OAS | 增长预期×信用 | **HY 仅 3yr 窗警示** |
| SPX×HY_OAS | 风险偏好一致性 | 同上 |
| VIX×SPX | 波动×权益 | 日×日 |
| DXY×UST_10Y | 美元×利率(Charter5 已验全窗 +0.357) | — |
| USDJPY×UST_10Y / ×JP_POLICY_RATE | 日元×美债/政策差 | 阶梯序列变化对稀疏→零基过滤警示如实 |
| USDCNY×SPX | 人民币×风险偏好 | **CN 序列 10 个月, 强警示** |
| EURUSD×ECB_DFR | 欧元×欧政策 | 阶梯序列同上 |
| SPX_CAPE×UST_10Y | 估值×利率(月×日跨频) | CAPE 月频 |
| GOLD_F×TIPS_10Y | 实利率×黄金(Charter5 案例A 基线) | — |
| NIKKEI225×USDJPY | 日股×日元 | — |

"主要矛盾"陈述框架: 哪些相关处于窗口内异常(引用 --window 60 滚动端值)——滚动窗一律 `--window 60`(须 --metrics); 矛盾图谱在增长/估值维标注数据缺席(A-1 矩阵)。

---

## 案例B 历史相似(当前美国 增长/通胀/利率/信用/估值 组合)——**整体 blocked-by-P0**

### B-1 analog 现状能力边界(实测 @20261110_v2, 引擎未修)

- anchor 2026-10; candidates scanned=1871/valid=73/overlap=13/insufficient=1785。
- 25 规格特征中锚点在场 17: growth 3/6(ICSA_4w/NFP_3m/UNEMP; INDPRO_yoy/RSAFS_yoy/GDP_yoy 因锚点月无观测缺席——月频发布滞后), inflation 1/3(仅 BEI_10Y; CPI/CORE_CPI 同上), rates 8/8, credit 2/4(HY_OAS_level/HY_IG_gap_level; 两个 d12m 弃 hist 24<36), volatility 2/2, valuation 1/2(SPX_CAPE; SPX_PE_TTM 止 2026-06)。
- **HY 族候选侧历史不足(3yr−12m 滞后<36)→ 信用维在全部候选距离中恒缺席(贡献 0)**——"HY 族弃用"的准确表述。
- 单维主导旗标大量触发(利率 contribution_share 0.60-0.87): rates 8 特征在场 vs 其他维 1-3 特征, 重归一后利率权约占半——如实转述, 不得筛掉。
- aftermath: SPX/UST_10Y/DXY/GOLD_F 1/3/6/12m; 起点=候选锚点次月 01 后首个观测; unavailable 按资产字典。
- **P0 修复后预期变化(执行前必须重验)**: 维度标准统一(锚点月特征在场判定可能改变 growth/inflation 在场数→单维主导现象或缓解或转移)、候选去重、aftermath 口径明确、scanned 计数(1871 含 PE 1871 年起网格月, 语义待修)。修后本节数字全部以重跑为准, 本手册数字仅作"修前基线"存档。
- 执行步骤: `history`(catalog)确认特征覆盖 → `analog --top 5`(修后); 拒答路径已在浅快照验证(insufficient_history kind 正确)。输出引用纪律: disclosure 三条逐字(纪律17)、巧合旗标全转述、TOP-N 不得浓缩为"当时 Y 涨所以现在 Y 涨"句式(违规)。

### B-2 "当时实际发生了什么"——【假设】层设计(QB-013 先例)

- 引擎**无事件数据**(无事件年表/叙事 fact): 事件叙述全部落【假设】层并强制标注"事件知识非引擎数据, 不可验证"(纪律4/15; Charter6 QB-013 先例句式)。
- 数据侧佐证(可并列): `history --metric UST_10Y --start <候选月-3> --end <候选月+12>` 等取候选期轨迹**原值序列**; `compare --metrics VIX,SPX --start <候选窗> --end <候选窗>` 给候选窗内可验关系——这些是【事实】位, 与事件叙事分层呈现。
- 边界: 事件因果("因为降息所以反弹")禁入事实位(纪律6 事实位因果禁令); 竞争性事件解释并列≥1(纪律4)。

### B-3 "哪些机制仍成立/已不适用"——证据分级执行

- E1(引擎可验): 候选窗内 compare/--lag/--window 输出字段原值; 引用格式=命令+字段原值。
- E2(部分可验): 可验环给 E1 证据, 缺失环(如跨境资本流动——无任何流量序列)明写"本引擎无 X 序列, 此环为【假设】"。
- E3(纯叙事): 整环【假设】+证伪指标(§纪律15 模板逐字)。
- 差异>1σ 的维度逐维点名: 引擎 dims.{dim}.z_gap+contribution_share 原值反读; TOP-1 vs TOP-N aftermath 分歧时结论降级(dispersion.topN_aftermath_sign_agreement<0.6)。

---

## 案例C 传导与条件推演

### C-1 传导链逐项可得性

链条: 政策利率→实际利率→美元/资本流动→金融条件→盈利与估值(章程例)。

| 环节 | 可得性 | 具体命令/字段 |
|---|---|---|
| 政策利率 US | ◎ | history/compare FED_FUNDS(月 10yr); DFF/DFEDTAR 登记未采集 |
| 政策利率 EA/JP | ◎/◎ | ECB_DFR(阶梯 1999→)/JP_POLICY_RATE(1985→); compare 零基过滤警示如实 |
| 政策利率 CN | ○ | CN_LPR_1Y/5Y 单值 fact(overview); 历史/滞后比较 blocked-by-P2(数据) |
| 实际利率 | ◎ | TIPS_5Y/TIPS_10Y 日频 10yr(市场定价口径, 明示口径) |
| 美债 | ◎ | UST_2/5/10/30Y+CURVE_2S10S |
| 美元 | ◎ | DXY+四双边汇率 |
| 日欧中政策环境 | △ | JP/EA 政策序列 ✓; 中 OMO 缺/LPR 单值; 环境叙述落【假设】处标 E2/E3 |
| 汇率 | ◎ | fx 方向语义 calc 随行 |
| **跨境资本流动** | ✗ | 无任何序列(CN_SF_FLOW/SB_FLOW 登记未采集; 无 TIC/EPFR)→ 整环 E2/E3【假设】 |
| 金融条件 | △(组合近似) | 无 FCI 指数; 以 HY_OAS+VIX+TIPS_10Y+CURVE_2S10S **各自原值并列**表达, 强制披露"组合近似, 非金融条件指数"; HY 仅 3yr 窗随行 |
| 盈利 | ✗ | 无 EPS/盈利预期序列→E3【假设】; SPX_PE_TTM(止 2026-06)只作估值侧间接参照 |
| 风险溢价 | △ | HY_OAS/IG_OAS 3yr(信用溢价)+VIX; ERP 无直接序列→E2 |
| 估值 | △ | SPX_CAPE(145yr)/SPX_PE_TTM(滞后); SPX_PB 不可得; CN SH_PE 单值; EA/JP 无 |

### C-2 竞争性解释与情景(结构要求, 非结论)

- ≥2 竞争性解释: 每条按四层标注分层(【事实】=引擎字段原值/【推断】=给依据/【假设】/【尚未验证】), 并列呈现不单声(纪律4)。
- ≥3 条件情景 × 五行齐备(纪律16): 情景(明写"假设非预测")/资产方向判断(方向+置信层级: 历史相似证据(引用 analog)/相关证据(引用 E1)/纯逻辑推理(标明))/敏感变量(1-2 个引擎指标)/证伪指标(可观测阈值)/触发条件(可观测条件+时限)。单一情景不得单独呈现(并列基准+反例)。固定边界文案逐字收录(references/research-discipline.md)。
- 禁: 点位/时间承诺/路径概率(引擎不输出)。

### C-3 敏感变量 compare/--lag 组合清单

`--lag K`(K>0=B 领先 K 个变化对; 只证时序先后, 禁写"驱动"; 与 --window 互斥):

| 命令 | 链环 |
|---|---|
| compare --metrics FED_FUNDS,UST_10Y --lag k | 政策→国债 |
| compare --metrics FED_FUNDS,DXY --lag k | 政策→美元 |
| compare --metrics FED_FUNDS,GOLD_F --lag k | 政策→黄金 |
| compare --metrics TIPS_10Y,GOLD_F --lag k | 实际利率→黄金 |
| compare --metrics UST_10Y,USDJPY --lag k | 利率差→日元 |
| compare --metrics HY_OAS,SPX --lag k | 信用→权益(3yr 窗警示) |
| compare --metrics VIX,SPX --lag k | 波动→权益 |
| compare --metrics SPX_CAPE,UST_10Y --lag k | 估值×利率(跨频月网格) |
| compare --metrics JP_POLICY_RATE,USDJPY --lag k | 日政策→日元(阶梯稀疏警示) |
| compare --metrics ECB_DFR,EURUSD --lag k | 欧政策→欧元(同上) |

`--window 60` 用于上述可验环的机制强度时间一致性(E1"滚动稳定性")。阶梯政策序列的变化对稀疏→n 骤减/零基过滤披露如实转述, 不足即降级 E2, 不硬凑。

---

## 附: 终稿纪律(三案例通用)

1. 事实位 lint 自检(references/cli-contract.md 末节调用方式)。
2. warnings 全转述(纪律: 强制); violations 出现即重做。
3. 用户认可后 `archive save --question ... --answer-text <全文> --evidence/--statistics/--hypotheses/--open-questions --as-of <T>` 六参直存(拒答不落档)。
4. 每数值 observation_date+source 随行; 陈旧单值(CN_CPI 2025-08/EA_HICP 2025-12)明示滞后月数(纪律10)。

## 附: 预判缺口清单(P2 候选面——只列不修, P2 只修真实研究中确认者)

**数据类**: ①CN 宏观序列化(CPI/PPI/PMI/新增贷款现仅单值, 且 CPI/PPI 停在 2025-08) ②CN 利率序列(10yr 国债/LPR 历史/OMO) ③EA: HICP 陈旧 2025-12+增长就业无+BUND 序列无+DAX/CAC40 未采集 ④JP 宏观(东京 CPI 登记未采集) ⑤流动性维度四经济体全缺(M2/SOFR/央行表; ZQ 期货未采集) ⑥跨境资本流动(TIC/EPFR/南北向; CN_SF_FLOW/SB_FLOW 未采集)——案例C 整环只能【假设】 ⑦盈利序列(EPS) ⑧EA/JP 本土股指与估值 ⑨HY_OAS 族源端仅 3yr——analog 信用维恒缺席+案例A 5年窗 blocked ⑩CN 股指序列仅 2026-01 起 ⑪registered-not-collected 一批(DFF/DFEDTAR/REAL_*/HY_IG_DIFF/WTI_SPOT_M/ZQ_*)。
**统计类**: ①changes 缺 1月/1年/5年 窗口(现有 compare X,X --start/--end interval_change_common_window 变通已实测可用, 但属变通) ②阶梯政策序列(ECB_DFR/JP_POLICY_RATE)×连续序列的变化对相关性: 零基过滤后样本骤减, 无专用口径 ③SPX_PE_TTM 滞后 4 个月的 freshness 处理 ④单值 fact 与序列层的能力断层(overview 有/history 无)。
**研究类**: ①analog P0 七项(维度标准/aftermath 口径/候选重叠/scanned 计数等——修后本手册 B-1 全部重测) ②事件年表 fact 层(案例B"当时发生了什么"永久归【假设】, 是否建最小事件档案属章程决策) ③金融条件组合近似的固定披露模板 ④浅窗警示(候选 73<120 满池)的结论降级话术标准化。
**Agent能力类**: ①五行模板 lint 自动校验(Charter6 §6 P1 建议未落, 现仅文本纪律) ②E1/E2/E3 分级机器可查标记 ③案例终稿→archive 六参直存的模板化 ④单值 fact 的陈旧度自动旗标(现靠纪律10 自觉)。
