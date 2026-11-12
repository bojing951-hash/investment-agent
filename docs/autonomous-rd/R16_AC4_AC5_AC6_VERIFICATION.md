# R16 验证报告 — AC4/AC5 正式验证 + AC6 收口 + 移交注记(dev/rd-r16-ac4-ac5-ac6 @ bde1ab1)

> 验证时间: 2026-11-12。验证席: 操作者 fork(独立 worktree /tmp/r16-wt;真实数据只读引用 dev 树,零写入)。
> 权威定义: `PRODUCT_GOAL.md` §八。报告结构对齐 R14_AC10_AUDIT.md / R15_AC1_AC2_AC8_VERIFICATION.md。
> 结论: **AC4 EXECUTED(终判=PASS 候选)/AC5 EXECUTED(终判=PASS 候选)/AC6 收口为 EXECUTED(终判留用户席)**。至此矩阵=九项 EXECUTED+AC3 PARTIAL(C 型首验窗 2026-12 日历门未至,如实);全部终判属用户裁定席。

## 第1节 AC4 经济机制与历史研究 — EXECUTED(PASS 候选)

定义原文: 「能够检索历史相似结构、解释历史后果,并研究经济传导机制。明确区分统计事实、因果假设和条件预测。」

### 1a 历史相似结构检索(亲跑真数据)

命令: `python3 ia_cli.py analog --top 5`(dev 树,快照 research_snapshot_20261112_v2,零写入只读)。

- 扫描面: **1871 个月**全扫,73 有效候选,1785 因历史不足弃(=expanding z MIN_HISTORY=36 个月门,Charter7-4b,引擎源码 L63 在档),13 因 TOP-N 簇重叠弃;簇去重(候选月相差<12 个月=同簇仅留最优代表)5 独立簇。
- 六维状态向量(锚点 2026-10): growth/inflation/rates/credit/volatility/valuation,逐特征 value/z/hist_n 全随行;credit 维全场缺席如实披露(「未覆盖维度可能是共同驱动(缺变量)」)。
- **独立复算(本席)**: 取 rank-1 候选 2024-12 的 features_detail(15 特征逐个 anchor_z/cand_z/gap/w_norm),按加权欧氏口径亲算 Σsqrt 内积: **本席 0.326434 vs 引擎 0.326433,六位小数一致**(差距公式=加权 L2,norm_wsum=0.869568 未强制归一,缺失特征以 missing_wsum 单列)。rank-1 的 dims 贡献份额(rates 0.7372/volatility 0.1812/valuation 0.0738/…)与逐特征 gap 对账自洽。
- **四判据巧合旗标现役全开**: 当前 TOP-5 候选**全部**被标「相似性由单一维度主导,跨维度结构印证弱,巧合可能性高(利率 contribution_share=0.61~0.90)」——引擎在最不利情形下主动降调,与冻结测试断言口径一致。
- 诚实拒答三面: ①research_mode_gate.realtime_info_set=**blocked**(「起点月窗内无 vintage 快照——历史时点信息集不可重构,修订值≠当时值,不得以今日修订口径冒充当时值」);②event_study=blocked(发布日不可得,不得按发布日对齐);③features_dropped_at_anchor 四条 release_lag 如实缺席(INDPRO/RSAFS/GDP/CORE_CPI 月度发布滞后,不以前值/插值冒充)。

### 1b 解释历史后果(事后演变与排序严格分离)

- aftermath 块: 逐资产 1m/3m/6m/12m 真实窗口收益(如 SPX 1m +2.93/3m −4.37/6m +5.73/12m +16.65),**逐窗实际起止观测日随行**(SPX_window 1m=2025-01-02~2025-01-31 等,可自行复算);label 明示「非预测,不参与相似度;排序与事后严格分离」。
- dispersion 面: TOP-N 独立簇事后符号一致性(16 窗口径 0.6~0.8),basis 注明簇代表口径——防止"事后一致"被误读为预测力。
- disclosure 三条随行: 「相似≠因果,更非预测」「特征为最新修订口径的描述性对齐,不代表当时信息集」「距离分位≠概率」。

### 1c 经济传导机制(三态区分的机器面)

- 机制链证据分级 **E1/E2/E3**(.agents/skills/global-macro-research/references/research-discipline.md §E1E2E3): E1=引擎确定性可验证(compare 同步相关/--lag 领先滞后仅可表述"A/B 谁先动 k 期,禁写驱动"/--window 滚动稳定性/interval_change);E2=两端可验证中间环无序列→缺失环明写【假设】;E3=纯叙事→整环【假设】+必须给证伪指标。
- 四层标注衔接: E1 引用归【事实】、E2/E3 环节归【假设】、对 E1 的解读归【推断】——**E2/E3 永不进事实位**。= 「统计事实/因果假设/条件预测」三分的落地产物。
- 条件推演五行模板(同一文件): 环节 k [E1|E2|E3]+证据+资产方向判断(置信层级: 历史相似证据/相关证据/纯逻辑推理)+**证伪指标(可观测阈值)**。

### 1d 数据深度对账(声明 vs 档案实数)

| 声明 | 档案实数(本席亲查) | 判 |
|---|---|---|
| FRED 宏观月频 n≈120 | analog 状态向量 hist_n=119~120(CORE_PCE n=119, FED_FUNDS/UST_10Y/TIPS/VIX n=120) | ✅ |
| 日频 n≈2500+ | series_store USDJPY n=2601(2016-11-11~2026-11-11) | ✅ |
| JP 政策利率回溯 1985 | JP_POLICY_RATE n=495, first=**1985-07-01**, last=2026-09-01 | ✅ |
| Shiller 145 年 SPX_CAPE n≈1750 | SPX_CAPE_level hist_n=**1750**(引擎扫描面 1871 月=1871+ 起) | ✅ |
| HY_OAS 源端 3 年窗 | HY_OAS_level hist_n=36(ICE BofA 授权窗如实注记,既有登记) | ✅(受限如实) |

测试面: test_charter6_p0_windows / p1_missing_series / p2_shiller / p4_analog 四套直跑 **rc=0 全绿**。

**AC4 终判: EXECUTED,终判=PASS 候选**(检索/后果解释/传导机制/三态区分四子句全有真实执行证据+独立复算;留用户裁定席)。

## 第2节 AC5 独立研究结论 — EXECUTED(PASS 候选)

定义原文: 「能够根据客观证据评价机构观点,识别重要分歧、关键未知及潜在预期差。结论必须具有竞争性解释和证伪条件。」

样本: `QB-20261110-032(.research-full).json`(Charter8 终报告·上,绑 research_snapshot_20261110_v4)+`QB-20261110-033`(下,R1-R30)。

### 2a 逐子句核验(QB-032 亲读)

- **评价机构观点(到期判)**: 「已到期可判仅两项: MSIM 述市场定价"9 月加息>50%"→**兑现**(9-16 加息,引擎月均逐级佐证); MSIM 10Y 8 月末 4.75%→**吻合**(引擎逐位)」——未到期观点一律「只评当前证据不判对错」(纪律声明),无越界判。
- **识别重要分歧**: 「机构层利率路径真实分裂」鹰侧(Cook/Hammack 票面+MSIM)vs 鸽侧(PIMCO)逐名归因;M1 三分支与机构分歧一一对应。
- **关键未知**: open_questions 12 条如实列(财政/贸易维零覆盖、BUND/JGB 无序列、JP 通胀 MISSING、盈利预期序列缺…);正文「财政维与贸易维: 四经济体均无任何序列→两维整体 NOT_VERIFIED,不以外部知识填空」。
- **潜在预期差**: ZQ_IMPLIED_AVG 4.095 vs DFF 3.88(+0.215pp)并附引擎口径警告(月均/时点错配不得换算次数)。
- **竞争性解释+证伪条件(S1-S4,五行模板实跑)**: 每情景 ①成立阈值(CORE_PCE≥3.2 两月/CPI≥4.0 两月/BEI≥2.6;USDJPY≥165 或 EURUSD≤1.08 且伴步长;PMI≥50 两月且 CHINEXT 3m 转正…=可观测证伪条件)②成因(带 E1/E3 分级,BOJ 官方层反向注记随行)③传导(E1 相关系数逐环)④方向性影响⑤证据(真实读数)⑥竞争情景互斥注记。当前判「S2 相容度最高,S1 四指标全未触发」=有证分级而非断言。

### 2b 独立复算(本席)

- 引数复核: 档案引「CORE_PCE×FED_FUNDS +0.4220, n=118(E1 月网格)」→ 本席在 v2 快照亲跑 `ia_cli.py compare --metrics CORE_PCE,FED_FUNDS` 得 **pearson_returns=0.42198** ✅(n=119=晚两日快照多一月,数值四位一致)。
- 证据链: evidence 字段载明全部命令口径(overview/compare/history/analog ×4 组 weights)+中间数据档路径+上游 QB 链(021/022/023/029);answer 纪律声明 12 条随行(attribution 分层/BOJ 信息层级铁律/禁点预测/事实位因果性动词不使用)。

### 2c 结论面覆盖

- R1-R30 结论链在 QB-033(下册);分歧矩阵 M1-M8+S1-S4 在 QB-032;MW-V1 首期周报样例与 data-only 周报管线(data/weekly/data_pack_*.md+meta 快照消化链)在档。
- 边界如实: C 型(到期预测实判)首验窗 2026-12 日历门未至,AC5 相关的到期判定积累以 2/17 起步如实计(AC3 行同口径)。

**AC5 终判: EXECUTED,终判=PASS 候选**(评价/分歧/未知/预期差/竞争性解释/证伪条件六要素全有真实档案证据+引数复算命中;留用户裁定席)。

## 第3节 AC6 真正的一键研究 — 收口为 EXECUTED(终判留用户席)

原行「剩余: AC7 端到端 3 任务+1 开放题未跑」已过时。现状:

- 一条自然语言指令自动完成完整研究: R2 `research-run` 十一步确定性编排真执行(每步真子进程+信封留档;ok 与 semantic 分记;L3+L4 恒 declared-not-produced 不冒充)。
- 真正执行工具调用非命令清单: R2 31 判+R3 十问扇出 --fanout 47 判+**R7 端到端真跑**(任务A 十一步+16 命令/任务B 分歧矩阵/任务C 交叉验证/开放题金油比条件前视,R8 独立复核 31 数值全中零 BLOCKER)。
- Web 工作台条款: 四页工作台(app.py)**零模型调用**为设计纪律——「本工作台不内置任何模型调用;数据图+缓存研究即全部页面能力」显式声明,无 AI 按钮冒充面(定义允许: 不提供按钮即无冒充;提供则须真接入);研究地图页=research-map 同引擎零模型。test_charter8_workbench 36✅ rc=0(本席亲跑)。
- 剩余如实: 真实使用案例积累(用户日常研究量仍少)+终判属用户裁定席。

**AC6 收口: EXECUTED(终判=PASS 候选留用户席)**。

## 第4节 移交注记(任务D)

### 4a QB-005~008「零Key矩阵问题」边缘档(根因已查明)

- 现象: query_history 内 QB-20261109~20261112 各有 005~008 号「零Key矩阵问题」档(共 16 记录+16 full),question_text 字面=测试用例名,mode B,answer/evidence/bindings 全空,archived_at 间隔≈4h=launchd 无头轮节奏。
- 根因: `tests/test_charter5_zero_key_matrix.py` §4「archive save 有快照→零Key正常落档」——**CI 干净克隆无快照走 no_snapshot 拒存分支(零写入);本地/无头在 dev 树跑套件=有快照→真写生产档案路径**。测试注释(L101-102)已知此双分支并以结构化断言覆盖,但未隔离写入面。
- 定性: **诚实空档、非伪造、非合成冒充**(R14 §4 口径不受影响——「零合成冒充」核验的是内容冒充,此为测试副产物流入);但属档案污染: 研究档案混入非研究记录。
- 修复候选(登记,本波不改代码): §4 改用 `_ARCHIVE_DIR` tempdir 注入缝(§6 即此先例,批2 WI6 缝已在)→ 本地跑套件不再写真档。已在 REMAINING_ISSUES.md P2 追加条目。
- 存量 16 件处置建议: **保留不删**(append-only 纪律;不重写历史档),报告+台账注记即收口;若未来出清理轮再由用户裁定。

### 4b R15 移交项清单核对

R15 报告移交节三项: ①AC6 注记过时→本报告第3节已收口;②QB-005~008 注记→本节 4a;③AC4+AC5 验证→本报告第1/2节。全部闭。

## 第5节 验证与登记

- 本席亲跑: analog 真数据 TOP-5(距离独立复算 1e-6 命中)+compare 复算 pearson 0.42198 命中+charter6 四套 rc=0+workbench 36✅+零Key矩阵套件 rc=0;真实数据全程只读。
- 全仓套件: 全量 133 套=**132 exit0+1 环境性+0 失败**(test_p0_baseline_lock_equivalence worktree 清单断言被本席活 worktree /tmp/r16-wt 触发,R13-R15 同款先例;test_model_live 在无 Key 环境走跳过面 exit0)。
- 登记: FINAL_ACCEPTANCE AC4/AC5/AC6 三行更新;REMAINING_ISSUES.md P2 +1 条(零Key测试档隔离);ITERATION_LOG R16 行;CURRENT_STATE/RESUME 同步。
- 移交 R17 候选: ①零Key套件 §4 tempdir 隔离(代码波,含 16 件存量注记引用本报告 4a);②矩阵十项全 EXECUTED 后的「终判覆盘轮」编排建议(用户裁定席材料包: 十行终判+日历门 F=2026-12-05/六标签 2026-12 状态一并呈报)。
