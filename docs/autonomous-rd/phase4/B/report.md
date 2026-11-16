# 一键研究报告(零模型编排 v2.0)
- 问题: 中国宏观信用与制造业景气: CN_NEW_LOANS 新增贷款与 CN_PMI_MFG 制造业PMI 对 CHINEXT 创业板指与 FXI 中国大盘股的影响
- 运行: 20261116T053224Z @ 3550ca3
- 快照: research_snapshot_20261112_v2 (target 20261112)
- 数据门(gate_a): 7/7 信封步非 OK(DEGRADED)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知

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
- **CON-1**: 【推断】政策面信用扩张叙事与实体面景气收缩并存——机构观点人民银行二季报表述将继续实施适度宽松的货币政策、加大逆周期调节力度并单设 1万亿元民营企业再贷款(机构观点原文);引擎事实面制造业PMI 49.3@2026-10-01 处荣枯线下方(WARN 单点)、新增人民币贷款 12734 亿元@2026-09-01 为单点快照(DEGRADED), 两指标历史序列步均报 no_series(中国宏观序列在本引擎无登记接入点)——信用供给与制造业景气之间的传导在本证据面不可机器验证;资产面创业板指 2572.0672@2026-11-11 年内 -19.7025%、处 2026 年 206 个观测中第 4.9 百分位, 景气收缩已在在岸成长指数定价中计入相当部分;「宽信用托底成长股」与「信用扩张传导失灵、收缩延续」两种读法在引擎内不可判别。机构观点出处: 人民银行/世界银行/PIMCO(VP-VIEW-20261111-001, VP-VIEW-20261110-007, VP-VIEW-20261110-003)。
  - 依据: L1 事实行与概览步信封(CN_PMI_MFG/CN_NEW_LOANS 为单点快照, 历史序列步对二者 no_series, 为本运行 run_ok=False 的构成步骤)+创业板指(CHINEXT)年内序列统计(样本数/百分位按钉死口径自 S4 序列复算)+机构观点库(人民银行宽松与结构性工具表述、世界银行内需疲弱与房地产下行判断、PIMCO 中国例外判断, 引用归因 institution_stated);两 CN 宏观指标无年内分布可引, 本条对其不作百分位或区间类表述;单点与单点之间不作同窗对比, 观测日随行披露
  - 竞争性解释1: 信贷需求不足论: 制造业景气收缩(荣枯线下方)压制企业信贷需求, 信用扩张停留在供给端——与机构观点世界银行对中国内需疲弱、信心低迷与房地产旷日持久的判断同向; 若该读法成立, 新增贷款放量难以持续, 成长股盈利修复缺乏实体抓手, 宽信用对指数的托底落空
  - 竞争性解释2: 政策时滞与结构性错位论: 机构观点人民银行的适度宽松经由结构性工具(科技创新和技术改造再贷款、民营企业再贷款)定向滴灌制造业升级, 传导需要时间; 假设一至两个季度后景气与信用同步修复, 当前单点裂口只是滞后而非失灵, 在岸成长资产的低位定价反而预留修复空间
  - 竞争性解释3: 单点口径噪音论: 新增贷款月度值本身具季节性(季末冲量), 九月单点且质量状态 DEGRADED、无序列对照, 无法区分趋势与噪音; 若后续月份读数回落, 裂口读法反转——本引擎无该序列, 此为诚实披露的不可判别而非结论
  - 证据: CN_PMI_MFG@2026-10-01, CN_NEW_LOANS@2026-09-01, CHINEXT@2026-11-11, VP-VIEW-20261111-001, VP-VIEW-20261110-007, VP-VIEW-20261110-003
- **CON-2**: 【推断】同周双资产反向定价: 创业板指周 +4.3337%;自 11 月低点 2391.6518 起的短短数个交易日内反弹, 而美元计价离岸代理 FXI 同周下跌、年内亦双位数下跌(数字面与口径见机制链);美元兑人民币 6.66(USDCNY)周窗变动幅度远小于上述背离幅度, 汇率口径不足以解释同周分裂;机构观点面全库 INSUFFICIENT_EVIDENCE(首验窗 2026-12), 无一家机构对 CN 权益方向给出可验证预测;「同一基本面下的分裂定价」与「两资产本非同一资产(市场席位/成分/计价货币口径不同, FXI 为美股上市 ETF 代理)」两种读法并存, 机构观点出处(VP-VIEW-20261110-003)在 PIMCO 对中国例外的判断中给出背景。
  - 依据: 概览步周窗与年内窗信封(创业板指(CHINEXT)周窗与年内窗、FXI 周窗与年内窗、美元兑人民币(USDCNY)水平与周窗)+对齐比较步信封(两资产日度收益全窗 pearson 相关、样本数、共同观测窗与日期间隔警告, 数字面在机制链环列示——FXI 无别名表锚, 其数字面按纪律置于机制链)+机构观点库(PIMCO 中国例外判断, institution_stated);创业板指 11 月低点按钉死口径自 S4 序列复算;FXI 年内数值不作百分位表述(序列在场但为代理口径, 仅方向性引用)
  - 竞争性解释1: 口径与结构论: FXI 身份字段自证为美股上市、美元计价、offshore_proxy 席位的 ETF 代理, 创业板指为在岸本地指数——若把同周背离主要读作席位/成分/计价货币的口径与风格差异(离岸大盘中资股 vs 在岸成长指数), 则「分裂定价」部分是错觉, 两资产本就不覆盖同一现金流与投资者群
  - 竞争性解释2: 投资者结构与流动性论: 在岸短线资金在两融余额在场(概览步 22945.61 亿元)的条件下对超跌成长筹码发动反弹, 而离岸机构资金对中国资产维持谨慎; 假设这一结构差延续, 背离将持续而非收敛, 在岸相对离岸的韧性不代表基本面——引擎无资金流/持仓序列, 此环不可验证
  - 竞争性解释3: 领先滞后论: 若本轮在岸反弹是政策预期驱动的先行信号, 离岸将随后跟进修复; 反之若离岸定价更接近基本面(景气收缩未反转), 在岸反弹将被回补——两个方向在引擎内不可判别, 需后续观测裁决
  - 证据: CHINEXT@2026-11-11, FXI@2026-11-11, USDCNY@2026-11-11, VP-VIEW-20261110-003
- **CON-3**: 【推断】制造业量价面呈挤压组合——引擎事实 PPI 5.0% 与中国CPI 0.9% 同为 2026-09-30 观测(WARN), 制造业PMI 49.3@2026-10-01 处荣枯线下方: 投入成本高企与产出价格疲弱并存, 指向中下游制造业利润率承压, 对在岸成长资产的盈利端构成压制;对冲面机构观点人民银行以结构性工具定向支持(科技创新和技术改造再贷款、民营企业再贷款额度扩容), 政策受益方向与利润挤压方向在在岸成长资产上并存, 净效应在引擎内不可判别。机构观点出处: 人民银行(VP-VIEW-20261111-001)与 IEA(VP-VIEW-20261110-010)。
  - 依据: 概览步与事实行信封三指标同框(PPI/CPI 同月观测、制造业PMI 次月观测, 观测日随行, 两百分比读数与荣枯线判断均为快照单点、无序列对照)+机构观点库(人民银行结构性工具表述、IEA 供给驱动能源冲击记叙, institution_stated);PPI→CPI→利润率的映射无引擎序列(无中国利润率/盈利序列), 剪刀差读法限于水平对照而非传导验证;CN_PPI_YOY/CN_CPI_YOY 与 CN_PMI_MFG 均无历史序列接入, 本条对其不作百分位或区间类表述
  - 竞争性解释1: 利润挤压论: PPI 与 CPI 剪刀差指向中下游利润率收缩——若 PPI 高企由输入成本推动且向下游传导受阻, 制造业(景气已在荣枯线下方)将量价双承压, 成长资产盈利预期下修, 反弹缺乏盈利支撑
  - 竞争性解释2: 政策对冲论: 机构观点人民银行的结构性再贷款定向科技创新与技改、民营企业——假设额度放量先于盈利兑现, 市场对政策的敏感度高于对当期盈利的敏感度, 指数或提前反应政策而非等待利润表; 与利润挤压论的净效应方向相反
  - 竞争性解释3: 信号噪音论: 两个百分比读数为九月单月同比、PMI 为十月单月, 无序列对照; 若 PPI 回落(机构观点 IEA 记叙油价上行为供给驱动, 或随供给恢复消退, 与人民银行输入型通胀压力表述同域), 剪刀差自行收敛, 挤压论弱化——单月水平对照不足以定趋势
  - 证据: CN_PMI_MFG@2026-10-01, VP-VIEW-20261111-001, VP-VIEW-20261110-010
- **机制链 MECH-1**: 信用脉冲→制造业景气→在岸成长定价(证据分级链)
  - E1 E1(引擎直接可验证): 四点同框、观测日不同(非同窗对比, 如实并列): 新增人民币贷款 12734 亿元@2026-09-01(DEGRADED)、制造业PMI 49.3@2026-10-01(WARN)、创业板指 2572.0672@2026-11-11(PASS, 年内 -19.7025%)、FXI 33.92 美元@2026-11-11(PASS, 年内 -10.7475%)——均为 L1/概览步快照原值直读 [证据: CN_NEW_LOANS@2026-09-01, CN_PMI_MFG@2026-10-01, CHINEXT@2026-11-11, FXI@2026-11-11]
  - E2 E2(部分支持): 信用供给→实体景气的传导环——引擎对 CN_NEW_LOANS/CN_PMI_MFG 无历史序列(历史步 no_series), 「信贷放量领先 PMI 修复」的历史对应不可复算; 机构面人民银行加大逆周期调节的表述为 institution_stated 支持叙事而非引擎验证 [缺失环: 缺失环【假设】: 引擎无 CN_NEW_LOANS/CN_PMI_MFG 历史序列(历史步 no_series), 信贷→景气传导的时点/幅度/因果不可机器验证; 此环为【假设】——假设货币信用扩张经一至两个季度传导至制造业景气]
  - E3 E3(纯叙事, 给证伪指标): 若传导兑现, 制造业PMI 回到荣枯线上方且创业板指脱离年内低位区; 若传导持续失灵, 创业板指回测年内低点(2391.6518@2026-11-03, S4 序列钉死口径复算)——两分支均不作预测, 以资产序列可观测裁决 [证伪指标: CHINEXT]
- **机制链 MECH-2**: 在岸/离岸同周背离(数字面与相关结构)
  - E1 E1(引擎直接可验证): 概览步周窗——创业板指 +4.3337%(基准 2026-11-06 值 2465.232)与 FXI -2.9468%(基准 2026-11-06 值 34.950001)同周反向, 反向幅度合计约 7.28 个百分点(两周窗原值亲算加总); 年内窗创业板指 -19.7025% vs FXI -10.7475%; 美元兑人民币周窗 -0.3888%(基准 6.688)、水平 6.66@2026-11-11, 汇率窗变动远小于资产背离; 对齐比较步——两资产日度收益全窗 pearson 相关 0.3620708(2344 个变化对, 共同观测 2345 日, 共同窗 2016-11-14 至 2026-11-11, FXI 侧掉落 168 日、创业板指侧 82 日, 共同窗内相邻观测最大间隔 12 天——引擎日期间隔警告原文随行): 长期温和正相关之下, 同周反向属波动常态而非口径异常 [证据: CHINEXT@2026-11-11, FXI@2026-11-11, USDCNY@2026-11-11]
  - E2 E2(部分支持): 背离驱动环——在岸短线资金(两融余额 22945.61 亿元@2026-11-10, 概览步原值)与离岸机构配置再平衡的行为差, 引擎无资金流/持仓/陆港通序列可验; 相关结构(0.36 全窗 pearson)只作统计事实陈述, 不作因果解释(纪律: 相关≠因果) [缺失环: 缺失环【假设】: 引擎无资金流/持仓/南北向序列, 在岸反弹与离岸走弱的投资者行为归因不可机器验证; 此环为【假设】]
  - E3 E3(纯叙事, 给证伪指标): 若背离为口径与波动噪音, 后续两资产同向修复(全窗正相关回归常态); 若离岸定价领先基本面, 在岸反弹将被回补——观察 FXI 与创业板指的同向性裁决, 不作预测 [证伪指标: FXI]
- **机制链 MECH-3**: 量价挤压→成长资产盈利(证据分级链)
  - E1 E1(引擎直接可验证): 三点同框(概览步/事实行直读, 观测日随行): CN_PPI_YOY 5.0%@2026-09-30(WARN)、CN_CPI_YOY 0.9%@2026-09-30(WARN)、制造业PMI 49.3@2026-10-01(WARN)荣枯线下方——量(收缩)价(投入高企/产出疲弱)组合为快照原值 [证据: CN_PMI_MFG@2026-10-01]
  - E2 E2(部分支持): 剪刀差→中下游利润率→成长资产盈利的映射——引擎无中国利润率/盈利序列; PPI 上行成因若为全球能源供给冲击的输入型传导(机构观点 IEA 记叙油价上行为供给驱动、人民银行表述输入型通胀压力仍在持续, 均 institution_stated), 或随供给恢复消退 [缺失环: 缺失环【假设】: 引擎无中国利润率/盈利序列, 剪刀差→利润率→指数盈利的传导不可机器验证; 此环为【假设】]
  - E3 E3(纯叙事, 给证伪指标): 若挤压持续且景气不修复, 成长资产反弹在盈利预期下修前难以延续; 若 PPI 随能源供给恢复回落, 压制解除——以创业板指可观测走势裁决, 不作预测 [证伪指标: CHINEXT]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **SCN-A**(基准)
  - 情景: 情景A(假设非预测): 信用与景气的传导时滞未兑现——制造业PMI 在荣枯线下方附近徘徊, 政策维持适度宽松但增量以结构性工具为主, 创业板指在年内低位区(11 月低点上方)拉锯, FXI 随离岸风险偏好弱势震荡; 两资产同向偏弱, 在岸相对离岸的短线反弹不具持续性
  - 资产方向判断: 创业板指低位区间震荡略偏弱, FXI 偏弱震荡(同向偏弱)(置信: 纯逻辑推理) 驱动指标(CN_PMI_MFG/CN_NEW_LOANS)无历史序列, 无条件历史相似渠道可引; 资产序列仅提供当前位置事实(创业板指处年内低百分位区), 不构成方向证据; 状态类比步六维特征面不含中国宏观序列, 不适用——置信取最低档
  - 敏感变量: CN_PMI_MFG, CHINEXT
  - 证伪指标: CHINEXT 阈值 创业板指收盘跌破 2391.65(基准: 年内低点 2391.6518@2026-11-03, S4 序列钉死口径)且 FXI 同步收于 31.59(基准: FXI 年内低点 31.59@2026-06-26)下方——低位拉锯假设被证伪, 转入失速再定价
  - 触发条件: 制造业PMI 下一期公布值仍处荣枯线下方且创业板指任一周收盘跌破 2391.6518(时限 2027-03-31)
- **SCN-B**(反例)
  - 情景: 情景B(假设非预测): 增量政策兑现与景气修复——制造业PMI 回到荣枯线上方, 结构性再贷款放量带动信用扩张生效, 离岸资金回流, 创业板指与 FXI 双双修复性上行
  - 资产方向判断: 双资产修复上行(创业板指弹性大于 FXI)(置信: 纯逻辑推理) 政策→景气→资产的传导链在本引擎无历史序列验证(见 MECH-1 环二的假设), 机构面人民银行增量政策表述为 institution_stated 而非方向预测; 机构观点世界银行对增长放缓与内需疲弱的判断与该情景相反方向同域并列——置信最低档
  - 敏感变量: CN_PMI_MFG, CN_NEW_LOANS
  - 证伪指标: CHINEXT 阈值 至期限创业板指从未收于 3043.33(基准: 2026 年 10 月高点 3043.3346@2026-10-09, S4 序列钉死口径)上方且制造业PMI 未出现荣枯线上方读数——修复假设被证伪
  - 触发条件: 制造业PMI 公布值回到荣枯线上方且新增人民币贷款单月读数较 12734 亿元(基准值@2026-09-01)放量(时限 2027-06-30)
- **SCN-C**(反例二(下行边界))
  - 情景: 情景C(假设非预测): 景气失速与输入型通胀挤压利润——制造业PMI 进一步下行, PPI 高企不落, 量价双杀令成长资产盈利预期下修, 两资产跌破各自年内低点, 在岸向离岸收敛补跌
  - 资产方向判断: 创业板指与 FXI 同步下行创新低(在岸向离岸收敛)(置信: 纯逻辑推理) 量价挤压机制(见 MECH-3 环二的假设)的盈利映射不可机器验证; 机构观点世界银行对房地产旷日持久的下行与信心低迷的判断(institution_stated)与该情景同向但非方向预测——置信最低档
  - 敏感变量: CN_PPI_YOY, CHINEXT
  - 证伪指标: FXI 阈值 FXI 周收盘持续守稳 31.59(基准: 年内低点 31.59@2026-06-26, S4 序列钉死口径)上方且创业板指未跌破 2391.6518——失速假设被证伪
  - 触发条件: 创业板指周收盘跌破 2391.6518 或 FXI 周收盘跌破 31.59(时限 2027-03-31)

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
- [FAIL|语义✗] S4_history_CN_PMI_MFG 
- [FAIL|语义✗] S4_history_CN_NEW_LOANS 
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
