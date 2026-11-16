# 一键研究报告(零模型编排 v2.0)
- 问题: 布伦特原油价格的大幅波动,还会传导到美国长期通胀预期(10年期盈亏平衡通胀率 BEI_10Y)吗?近年有时油价暴涨、长期通胀预期明显跟着走高,有时油价暴跌、预期却似乎纹丝不动——这种传导究竟是在减弱、已被「锚定」,还是本来就时有时无?
- 运行: 20261116T114933Z @ ad2f6e4
- 快照: research_snapshot_20261112_v2 (target 20261112)
- 数据门(gate_a): 5/5 信封步非 OK(DEGRADED)——缺口/降级明细见步骤台账各步信封 warnings;降级不阻断,判断层须知

## 四层区分

### L1 事实层 available=True
- BEI_10Y = 2.2 percent @2026-11-10 [质量:PASS] [来源:snapshot_fact:BEI_10Y@2026-11-10]

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
- **CON-1**: 【推断】按统计期对齐(不代表当时市场信息集), 布伦特原油期货(BRENT_F)与长期通胀预期(BEI_10Y)的日度变化传导呈「频率增强与幅度钝化并存」的结构: 全样本窗两者日度变化的相关为正, 分年相关逐年走强并于最近一年达到全窗最高(逐年数值与口径见机制链), 负窗占比极小(计数见机制链)。而幅度维度上, 大油价上行月的 BEI_10Y 月度响应按每十个百分点油价折算, 后段窗较前段窗大幅下降(分组数值见机制链), 最近一年三月布伦特大涨之月 BEI_10Y 仅小幅上行(数值见机制链)。机构观点面: MSIM 记叙本轮债市调整的重定价来源是实际收益率而非通胀预期(VP-VIEW-20261111-006, 归因转述)。「传导减弱」「已被锚定」「时有时无」三种读法各自只抓住一个维度, 单独采用任何一个都不完整。
  - 依据: 本席只读复算(方法与口径全文留痕于计算档, 编号方法一至方法九): 对齐为两序列共同交易日历的内连接与连续日变化对, 月度聚合以共同日历月首末观测, 事件阈值与滚动窗为方法自选并在机制链逐环注明, 全部数值断言逐位可由引擎树研究快照档与宏观采集档复算。BEI_10Y 为名义减实际利差, 含通胀风险溢价与流动性溢价, 非纯预期, 幅度钝化不能直接读作预期被锚定的同义语。BRENT_F 为主力连续期货, 引擎身份注记含展期跳空可能。相关与斜率均为统计描述, 相关不等于因果。
  - 竞争性解释1: 政策反应函数中介论: 若央行可信度上升, 市场把能源冲击的重定价由通胀预期渠道转入实际利率渠道(与机构观点 MSIM 的实际收益率主导记叙同向), 则幅度钝化是政策锚定生效而非传导机制死亡; 假设该读法成立, 当油价转为持续上行且央行反应函数弱化时, 幅度传导将恢复。
  - 竞争性解释2: 冲击结构论: 机构观点 IEA 记叙本轮上涨为供给驱动而非需求拉动(VP-VIEW-20261110-010, 归因转述), 若市场把供给型油价上行定价为一次性水平位移, 长期通胀预期本就无需大幅重定价; 假设油价上行的性质转为需求拉动型, 传导幅度或回升——该条件分叉在本证据面不可判别。
  - 竞争性解释3: 度量噪音论: 盈亏平衡差含流动性溢价与期限结构噪音, 假设部分预期重定价已被利差结构抵消, 幅度钝化部分是度量 artefact; 本引擎无流动性调整分解序列, 该读法不可验证亦不可排除, 如实披露。
  - 证据: BEI_10Y@2026-11-10, BRENT_F@2026-11-11, VP-VIEW-20261111-006, VP-VIEW-20261110-010
- **CON-2**: 【推断】「油价暴跌、长期预期纹丝不动」的直觉在引擎证据面的平均意义上不成立且方向相反: 大幅单日下跌事件的 BEI_10Y 同日响应幅度约为大幅上涨事件的两倍量级(事件阈值与分组数值见机制链), 后段窗的大跌月每十个百分点油价的 BEI_10Y 响应约为大涨月的三倍量级(分组数值见机制链)。但个例层面确有近零响应甚至反向的暴跌月(例证见机制链), 直觉体感或来自个例选择而非平均规律。机构观点面: OECD 记叙能源供给冲击在对通胀构成上行风险的同时拖累增长前景(VP-VIEW-20261111-002, 归因转述), 与下行冲击传导更强的画像同域。
  - 依据: 本席只读复算, 口径同前条并留痕于计算档: 事件研究分档阈值取单日涨跌幅绝对值超过百分之四与超过百分之六两档, 涨跌分组, 前向五/十/二十日累计变化自事件日起算于共同日历; 月度分组取单月涨跌幅不低于正负百分之八的大月。个别近零响应与反向响应的暴跌月例证在机制链环逐个列示数值。事件口径为统计期对齐, 非发布日事件研究, 不作当时市场反应声明。BRENT_F 与 BEI_10Y 的身份注记同前条披露。
  - 竞争性解释1: 通缩尾部定价论: 若油价大跌主要被解读为需求恶化与名义增长下移信号, 长期预期对负冲击更敏感, 涨弱跌强是冲击信息属性的不对称而非传导失灵。
  - 竞争性解释2: 对称锚未完成论: 若央行对称通胀目标完全可信, 涨跌两侧的传导都应弱; 假设本证据面的大跌月仍显著传导意味着下行侧的锚尚未建立, 所谓锚定至多是单侧锚定, 两侧不对称本身即反证。
  - 竞争性解释3: 事件构成论: 大跌事件在样本内集中于高波动体制窗, 假设响应强度来自体制而非方向, 分组不对称是样本构成 artefact; 分体制细分后样本不足, 不可判别, 如实披露。
  - 证据: BEI_10Y@2026-11-10, BRENT_F@2026-11-11, VP-VIEW-20261111-002
- **CON-3**: 【推断】传导不是「有时有、有时无」的方向开关, 而是强度在正区间内大幅摆动的调节器: 六十日滚动相关从未深度为负(最负值见机制链), 近零窗与负窗合计占比不足一成(计数见机制链), 其余时间传导方向稳定为正而强度摆动区间宽(逐月末数值见机制链)。后段紧缩周期中的个别大涨月 BEI_10Y 反而下行(例证数值见机制链), 与政策环境压制预期上行的读法同域。长期预期自身的波动并未压缩(分段均值见机制链), 锚定不体现为波动消失。机构观点面存在真实分歧: 美联储十一月会议记叙维持利率区间并待通胀回归目标(VP-VIEW-20261110-002), MSIM 记叙重定价已由实际利率承担并同时维持盈亏平衡敞口以对冲通胀高于目标更久的风险(VP-VIEW-20261111-006), UBS 预计未来两次会议各加息二十五基点(VP-VIEW-20261111-004), 三者均归因转述——锚定是否稳固恰是机构分歧本身。
  - 依据: 本席只读复算, 口径同前两条并留痕于计算档: 滚动窗取六十日(方法自选), 月末取该月最后一个窗值; 长期预期波动以六十日滚动标准差分段均值检验; 稳健性以替代油源与替代期限的分年口径旁证(逐年数值在机制链环列示, 方向一致)。二零二二年大涨月预期下行的例证在机制链环注明具体数值。窗长的全谱敏感性检验未做, 以分年口径(即换分组窗)方向不变作旁证, 如实披露该边界。
  - 竞争性解释1: 政策调制论: 若紧缩周期抬高对油价上行的政策响应预期, 市场会抑制通胀预期的上行幅度, 涨月负响应可解释为政策可信度压制定价, 强度时变即政策环境时变。
  - 竞争性解释2: 微观结构噪音论: 盈亏平衡差为交易变量, 假设仓位与流动性冲击可在短期压过宏观传导, 负窗与近零窗为微观结构噪音而非传导消失。
  - 竞争性解释3: 窗口径 artefact 论: 若六十日窗的强度摆动是窗长选择产物, 换窗后近零窗占比大增, 调节器读法将弱化; 本档以分年口径旁证方向不变, 但窗敏感性未做全谱检验, 如实披露。
  - 证据: BEI_10Y@2026-11-10, BRENT_F@2026-11-11, VP-VIEW-20261110-002, VP-VIEW-20261111-006, VP-VIEW-20261111-004
- **机制链 MECH-1**: 油价到长期通胀预期: 频率与幅度结构链
  - E1 E1(引擎直接可验证, f10_calc.py 方法一/二/三/六/九复算): 对齐共同交易日 2495 个(2016-11-14 至 2026-11-10), 日度变化对 2494 个。全窗: 日度 pearson +0.3384, OLS 斜率 +0.00402pp/1% 油价(即每 10% 油价 +0.0402pp)。分年 pearson: 2016 +0.11(32 对)、2017 +0.18、2018 +0.32、2019 +0.34、2020 +0.35、2021 +0.38、2022 +0.36、2023 +0.26、2024 +0.30、2025 +0.45、2026 +0.54(215 对)——频率维度为全窗最高年; 分年斜率 2021-2025 在 0.0040-0.0060pp/1%, 2026 降至 0.00297pp/1%。幅度维度: 大涨月(月涨≥8%)2016-2021 窗(12 个)每 10% 油价 BEI 响应 +0.0846pp, 2022-2026 窗(10 个)降至 +0.0235pp(降幅约七成); 2026-03 布伦特单月 +63.3% 而 BEI 仅 +0.050pp。锚点(方法九): BRENT_F 93.87@2026-11-11, 2026 年内 max 118.35@2026-03-31、min 59.96@2026-01-07; BEI_10Y 2.2@2026-11-10, 2026 年内区间 2.18@2026-06-24 至 2.50@2026-05-04(n=217, 钉死百分位 0.5, 口径 100×count(v<cur)/n)。 [证据: BEI_10Y@2026-11-10, BRENT_F@2026-11-11]
  - E2 E2(部分支持): 政策反应函数中介环——机构观点 MSIM 记叙(institution_stated, VP-VIEW-20261111-006): 十年期实际收益率单月上行 49bp 而盈亏平衡仅走阔 5bp, 且发生在布伦特触及 106 美元/桶的月份, 几乎全部变动是实际利率重定价而非通胀预期, 显示投资者认可央行在应对能源冲击。引擎无政策反应函数序列、无实际收益率与盈亏平衡的冲击分解因果识别, 此环为【假设】: 假设传导负担被政策可信度由通胀预期渠道转移至实际利率渠道。 [缺失环: 缺失环【假设】: 引擎无政策反应函数/冲击分解序列, 「央行可信度把能源冲击重定价挤进实际利率渠道」不可机器验证; 机构观点为 institution_stated 叙事支持而非引擎验证, 此环标注【假设】。]
  - E3 E3(纯叙事, 给证伪指标): 幅度分支——若任一自然月 BEI_10Y 月度上行≥0.25pp 且同期 BRENT_F 单月涨幅≥8%(即回到 2016-2021 窗每 10%≥0.08pp 的早期量级), 幅度钝化结论被证伪; 频率分支——若分年 pearson 跌破 +0.10, 频率增强结论被证伪。两分支均以引擎可观测月度读数裁决, 不作预测。 [证伪指标: BEI_10Y]
- **机制链 MECH-2**: 涨跌不对称: 上行钝化与下行敏感链
  - E1 E1(引擎直接可验证, f10_calc.py 方法五/六复算, 统计期口径): 单日|涨跌|≥6% 事件——上涨组 n=33, 同日 BEI 均值 +0.0209pp; 下跌组 n=48, 同日 BEI 均值 -0.0400pp(下行同日响应约为上行的两倍); 前向 5/10/20 日两组均反转回补(上涨组 -0.0279/-0.0288/-0.0106pp, 下跌组 +0.0413/+0.0467/+0.0354pp)。|涨跌|≥4% 同构(上涨 n=92 同日 +0.0193pp, 下跌 n=113 同日 -0.0265pp)。月度分组: 2022-2026 大跌月(10 个, 油均 -13.5%)BEI 均值 -0.0970pp, 每 10% 油价响应 +0.0746pp, 为大涨月(+0.0235pp/10%)的约三倍。个例: 2021-11 油 -16.4% 而 BEI -0.010pp(近零), 2024-09 油 -8.9% 而 BEI +0.030pp(反向), 2020-03 油 -55.0% 而 BEI -0.540pp(最大传导月)。 [证据: BEI_10Y@2026-11-10, BRENT_F@2026-11-11]
  - E2 E2(部分支持): 信息属性不对称环——机构观点 IEA 记叙本轮上涨为供给驱动而非需求拉动、高油价已致需求破坏(VP-VIEW-20261110-010, institution_stated), OECD 记叙能源冲击拖累增长前景(VP-VIEW-20261111-002, institution_stated); 若供给型上行被定价为一次性而下行走需求恶化信号, 响应不对称即信息属性不对称的映射。引擎无油价冲击的供给/需求属性标签序列, 不可机器验证, 此环为【假设】。 [缺失环: 缺失环【假设】: 引擎无油价冲击供给/需求属性标签序列, 「上行=供给一次性行、下行=需求恶化信号」的解读机制不可机器验证, 此环为【假设】。]
  - E3 E3(纯叙事, 给证伪指标): 若后续上行月响应升至早期量级(月度每 10% 油 BEI≥0.08pp)或下行月响应缩至近零量级(每 10% 油 BEI 绝对值<0.02pp), 不对称画像被证伪——以 BEI_10Y 与 BRENT_F 月度读数可观测裁决, 不作预测。 [证伪指标: BEI_10Y]
- **机制链 MECH-3**: 强度时变与波动结构链
  - E1 E1(引擎直接可验证, f10_calc.py 方法四/七/八复算): 六十日滚动相关 2434 窗, 负窗占 2.1%, |r|<0.1 合计 5.3%, r≥0.3 占 59.9%, 范围 -0.202 至 +0.816——方向稳定为正、强度宽幅摆动。近零段例: 2017-10 月末 -0.11, 2023-08/09 月末 +0.05/+0.01; 高段例: 2026-06 至 2026-09 月末 +0.61/+0.65/+0.65/+0.66。紧缩年反例: 2022-01 油 +17.3% 而 BEI 月 -0.120pp, 2022-05 油 +12.3% 而 BEI 月 -0.240pp。波动无压缩(方法七): BEI_10Y 六十日滚动 std 分段均值 2019 年前 0.0476pp、2024 年起 0.0569pp、2026 年 0.0521pp。稳健性(方法八): WTI_F 代入分年相关同向(2025 +0.45, 2026 +0.55); BEI_5Y 代入分年相关每年更高(2026 +0.63)——短端预期对油价更敏感, 与十端幅度钝化互补, 期限结构内部自洽。 [证据: BEI_10Y@2026-11-10, BRENT_F@2026-11-11]
  - E2 E2(部分支持): 强度调制环——若政策环境与冲击属性共同调制传导强度(紧缩期上行被政策可信度压制、供给冲击期预期无需重定价), 滚动强度的摆动与紧缩年涨月负响应同域可解释; 机构观点美联储维持利率区间待通胀回归目标(VP-VIEW-20261110-002, institution_stated)为政策环境在场背景。引擎无政策周期/冲击属性时变标签序列, 不可机器验证, 此环为【假设】。 [缺失环: 缺失环【假设】: 引擎无政策周期与冲击属性的时变标签序列, 「政策环境调制传导强度」不可机器验证, 此环为【假设】。]
  - E3 E3(纯叙事, 给证伪指标): 若六十日滚动相关进入持续深负(连续六十个交易日窗值低于 -0.2), 「方向稳定为正」结论被证伪; 若 BEI_10Y 滚动 std 分段均值降至 0.03pp 以下量级, 「波动无压缩」结论被证伪——均以 BEI_10Y 序列可观测裁决, 不作预测。 [证伪指标: BEI_10Y]

### L4 条件情景层 produced=True
> Agent(编排层)研判落位,attribution=ai_inferred;纪律结构经机器校验(validate_judgment 全绿);内容原文未改写,判断质量归 Agent 与独立审计(attribution=ai_inferred)
- **SCN-A**(基准)
  - 情景: 情景A(假设非预测): 供给驱动的油价高波动延续, 政策反应函数保持强硬, BEI_10Y 对油价上行的幅度传导维持在钝化量级(每 10% 油价的月度响应低于 0.05pp), 重定价主要由实际利率承担, BEI_10Y 大体在 2026 年内区间(下沿 2.18, 上沿 2.50)内运行, 方向上与油价保持弱同向。
  - 资产方向判断: BEI_10Y 区间内震荡略偏强, UST_10Y 与实际利率端承担方向性重定价(置信: 有相关证据) 分年相关与事件研究统计(E1, 见 MECH-1/MECH-2)为「方向弱同向+幅度钝化」的证据, 情景本身是条件推演非预测。
  - 敏感变量: BRENT_F, BEI_10Y
  - 证伪指标: BEI_10Y 阈值 任一自然月 BEI_10Y 月度上行 ≥0.25pp 且同期 BRENT_F 单月涨幅 ≥8%(即恢复 2016-2021 窗每 10% 油 ≥0.08pp 的早期传导量级)——幅度钝化假设被证伪。前提缺席=未触发(两态口径): 若至期限 BRENT_F 从未出现单月 ≥8% 的上行月, 证伪前提不在场, 记未触发不计证伪。
  - 触发条件: BRENT_F 单月上涨 ≥8% 且该月 BEI_10Y 上行 ≥0.25pp(时限 2027-06-30)
- **SCN-B**(反例)
  - 情景: 情景B(假设非预测): 油价上行的性质自供给一次性冲击转为持续通胀过程(机构观点背景: IEA 记叙供给受限与短缺延续、OECD 记叙持续通胀压力, 归因转述), 叠加通胀高于目标更久的定价, 市场把能源冲击重新计入长期预期, BEI_10Y 突破年内区间上沿 2.50 并站稳, BEI_5Y 领先上行(短端更敏感, 见 MECH-3 稳健性环)。
  - 资产方向判断: BEI_10Y 上行突破年内上沿 2.50 并站稳(盈亏平衡整体上移, BEI_5Y 领先)(置信: 纯逻辑推理) 传导重开属条件推演; 机构观点为背景叙事而非方向预测, 本运行无历史相似检索证据可引(analog 步对本问题不构成相似证据渠道), 置信最低档。
  - 敏感变量: BRENT_F, BEI_5Y
  - 证伪指标: BEI_10Y 阈值 至期限 BEI_10Y 从未收于 2.50 上方(基准: 2026 年内区间上沿 2.50@2026-05-04, f10_calc 方法九钉死口径复算)——传导重开假设未兑现。两态口径: BRENT_F 收盘曾站上 118.35(2026-03-31 年内高点)而 BEI_10Y 至期限仍从未收于 2.50 上方=前提在场+结果缺席, 计为证伪; BRENT_F 从未站上 118.35=前提缺席, 记未触发不计证伪。
  - 触发条件: BRENT_F 收盘站上 118.35 且 BEI_10Y 收于 2.50 上方(时限 2027-06-30)
- **SCN-C**(反例二(下行边界))
  - 情景: 情景C(假设非预测): 油价深跌与需求破坏预期互相强化(机构观点背景: IEA 记叙高油价需求破坏与经济前景恶化、OECD 记叙能源冲击拖累增长, 归因转述), 名义增长定价下移令长期预期锚向下方松动, BEI_10Y 跌破年内区间下沿 2.18, BEI_5Y 更深下行, 下行传导更强的不对称结构(见 MECH-2)在此方向兑现为脱锚。
  - 资产方向判断: BEI_10Y 下行跌破年内下沿 2.18 并伴随 BEI_5Y 领跌(置信: 有相关证据) 下行传导更强的事件研究统计(E1, 见 MECH-2)与该情景方向一致, 但跌破区间下沿为条件推演非预测。
  - 敏感变量: BRENT_F, BEI_5Y
  - 证伪指标: BEI_10Y 阈值 至期限 BEI_10Y 始终收于 2.18 上方(基准: 2026 年内区间下沿 2.18@2026-06-24, f10_calc 方法九钉死口径复算)——脱锚假设未兑现。两态口径: BRENT_F 收盘曾跌破 59.96(2026-01-07 年内低点)而 BEI_10Y 至期限仍从未收于 2.18 下方=前提在场+结果缺席, 计为证伪; BRENT_F 从未跌破 59.96=前提缺席, 记未触发不计证伪。
  - 触发条件: BRENT_F 收盘跌破 59.96 且 BEI_10Y 周收盘跌破 2.18(时限 2027-06-30)

## 语义审查(席位待唤起)

- **叙事语义未经独立裁决**——定性推断/条件情景在文;常驻席位=SEMANTIC-AUDIT-SEAT,编排层应唤席裁决后方可去掉本披露(章程 §4b/§8)

## Agent 判断落位

- attached=True(schema 1.1;violations=0)

## 步骤台账

- [OK |不适用] S1_decompose 
- [OK |语义✔] S2_doctor 
- [OK |语义✔] S3_overview_US 
- [OK |语义✔] S3_changes 
- [OK |语义✔] S4_history_BEI_10Y 
- [SKIP|—] S5_compare 命中指标不足 2 个,无可对齐自配对(如实跳过)
- [OK |语义✔] S6_analog 
- [OK |不适用] S7_mode_gate analog 锚点月窗门(compare 未产出对齐门——命中<2 或被拒)
- [OK |语义✗] S8_grounded_qa 
- [OK |语义✔] S9_views_lint 
- [OK |不适用] S10_selfcheck 
- [OK |不适用] S11_archive 默认关(--archive 显式开启;Skill 第 11 步=用户认可后)

## 证据索引(64 行)

- snapshot_fact:BEI_10Y@2026-11-10 → BEI_10Y
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
- s3_envelope:CHINEXT@2026-11-11 → CHINEXT
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
- s3_envelope:FXI@2026-11-11 → FXI
- s3_envelope:BTC@2026-11-10 → BTC
- s3_envelope:HY_OAS@2026-11-09 → HY_OAS
- s3_envelope:BB_OAS@2026-11-09 → BB_OAS
- s3_envelope:B_OAS@2026-11-09 → B_OAS
- s3_envelope:CCC_OAS@2026-11-09 → CCC_OAS
- s3_envelope:IG_OAS@2026-11-09 → IG_OAS
- s3_envelope:HY_IG_DIFF@2026-11-09 → HY_IG_DIFF
