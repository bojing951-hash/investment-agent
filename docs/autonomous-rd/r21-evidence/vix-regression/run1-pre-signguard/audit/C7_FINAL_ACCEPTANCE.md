# Charter 7「全球宏观研究能力建设」D席独立终验报告

- 验收人: D席(产品与真实用户验收线;与A席研究/B席工程/verify-p0-c7 两轮验证零共享上下文,全部判定基于本人独立复算与重放)
- 日期: 2026-11-10
- 对象: `dev/charter7-research-v1` @ `6a0dd80`(父链 cca2e4a→308f615(P0)→74657be(P2首批)→6a0dd80(P2-3首跑收口);未push未合并)
- 验收入参: 快照 `research_snapshot_20261110_v3`;研究归档 QB-20261110-021/022/023/029(archive get 可读);审计档 C7_P0_seven_issues_verify.md + C7_P0_fix_review.md;台账 docs/P2_DATA_GAP_LEDGER.md
- 方法: 隔离环境 `/tmp/ia-c7`(本地 clone@6a0dd80 + DEV data/daily 67 文件含 v3 + 独立 venv);零模型 Key、零付费调用、未跑 update、LIVE/launchd 零触碰(只读核查);**全部金融数字从原始序列独立复算,不引用 A/B 席期望值**;测试套件独立全量重跑
- 纪律: 只验不修;缺陷分级 BLOCKER/DEFERRED/观察;数据不足=NOT_VERIFIED 如实标注

## 总判定

| 验收项 | 判定 |
|---|---|
| ① 三完整真实案例(研究实质) | **PASS** |
| ② 金融正确性(独立复算 5+1 项) | **PASS** |
| ③ 缺口清单闭环(台账 18 项+归档 open_questions) | **PASS** |
| ④ Agent 调用记录可追溯 | **PASS** |
| ⑤ 代码/测试/文档/提交(三笔 diff 级审+独立全量 112 套件) | **PASS**(附 1 条环境性测试观察) |
| ⑥ 红线终检(七项) | **PASS** |
| 专项① QB-023 排序键裁决复核 | **裁决维持**(机制无错+披露已加;A席机制归因不成立但现象真实) |
| 专项② WALCL WARN 与 ICSA 一致性 | **同款同文案确认,登记而非修=正确处置** |
| 专项③ Gate A 8 项 noncore_missing | **确认全部为其他通道既有缺席** |

**总评: PASS。** 未发现 BLOCKER;未发现 DEFERRED;观察项 5 条(见末节),均不影响功能正确性与诚实性。

---

## ① 三完整真实案例(研究实质,非格式合规)

### 数字真实性(可溯源 ia_cli/引擎数据)
抽验 31 项数值全部复现(零容差外偏差):
- 相关性 9 组(QB-021/022): TIPS×UST +0.8278(n=2495)/VIX×SPX −0.7138(2512)/NIKKEI×USDJPY +0.2145(2434)/GOLD×TIPS −0.3013(2491)/GOLD×TIPS lag −21 rho +0.0321(2470,GOLD 领先=负 lag 号,归档括注口径正确)/EZU×SPX +0.8012(2512)/NDX×RUT +0.7644(2512)/DXY×GOLD −0.3935(2511)/USDJPY×UST_2Y +0.0064(2491)——本席在 v3 现役环境逐条重跑,r/n 全对上。
- 区间变动 6 项(QB-021 自配对口径): SPX 1m −3.1557/1y +12.4276/5y +61.4648、GOLD_F 5y +126.939、FED_FUNDS 12m +0.00pp(basis 2025-11-01→end 2026-10-01 双 3.88)、NIKKEI 1m −14.8563——basis/end 观测日与值逐位复现。
- analog 全链(QB-023): TOP-5 五席距离/分位/簇员数/missing 原因/事后 4 资产×4 窗(抽 2024-12 SPX 12m +16.647217)/dispersion 符号一致率(0.6~0.8,n_independent_clusters=5)/state_vector 六维 z(含 CAPE 40.71 z+2.999 hist_n=1750)——与 v2 归档逐值一致,且在本席 v3 环境零扰动复现(SOFR/WALCL 不入 FEATURE_SPECS 的台账声明经实测成立)。

### 研究实质四查
- **NOT_VERIFIED 如实使用**: QB-021 CN/EA/JP 无序列维度、QB-029 缩表/扩表相位切换时点、QB-022 增长放缓翼"尚未在硬数据确立"——均为缺数据即拒断言,无绕过。
- **模型知识冒充数据**: 未发现。事件/制度叙述(2019-12 外生疫情、2020-12 QE 制度、2022-01 加息起点)全部落【假设】/E3 层并附证伪指标;QB-023 要素②环境描写仅用引擎 cand_z 字段。
- **历史相似当预测叙事**: 无。QB-023 §6 明写"不支持'历史上最像的时期之后 X 上涨,现在也会'的外推";事后块逐块携带"非预测,不参与相似度"标签;三重警示(单维主导×4/事后分歧/信用维缺席)全部转述并把结论置信上限压低。
- **重要结论附证伪条件**: M1–M8 每条、S1–S4 每情景、QB-029 量价格局均有可观测阈值型证伪指标(如 CORE_PCE 突破 3.5/ICSA 4 周均值≥220k/WALCL 连续 4 周单边>±0.3%)。
- 附: 四档 answer_text 本席复跑 lint_fact_contract_text = 4/4 零违规(归档自述属实)。

**判定: PASS。**

## ② 金融正确性(独立复算,容差 1e-4 相对)

| 项 | 声称值 | 本席独立复算(原始序列自算) | 结果 |
|---|---|---|---|
| WALCL 1y | +2.6688% | +2.668799%(6,572,732@2025-11-05 → 6,748,145@2026-11-04) | ✅(relerr 4.1e-7) |
| WALCL 5y | −21.3032% | −21.303248%(8,574,871@2021-11-03 → 6,748,145) | ✅(2.2e-6) |
| SOFR 5y | +3.84pp | +3.840000(0.05@2021-11-09 → 3.89@2026-11-06) | ✅(0) |
| analog 2024-12 D | 0.326433,W_U=0.638889 固定分母 | 由输出 features_detail 逐特征 w_norm·gap² 重算 √Σ=0.326434;Σw_norm=0.869568=accounted_wsum/W_U 恰合;W_U=0.638889(n=17 特征) | ✅(1.4e-6,输出 6dp 舍入所致) |
| aftermath 12m SPX | +16.6472% | +16.647217%(2025-01-02@5868.5498 → 2025-12-31@6845.50,起止观测日与 {资产}_window 随行字段一致) | ✅(1.0e-6) |
| WALCL×UST_10Y | r=−0.0863(n=512,b_dropped=1983) | 对齐层语义(exact_date 交 513 个水平观测日→对齐后逐段变化 512 对):本席手算 r=−0.086275,n=512,b_dropped=1983 全中;引擎全精度 −0.08627457,4dp 舍入=−0.0863 | ✅(舍入格内一致) |

方法注记(供复核): WALCL×UST 变化相关的第一种天真口径(各序列先按自身连续观测求变化再按日期相交)得 r=+0.0182——n 同为 512 但值集不同;引擎语义=**先对齐水平观测日、再在对齐序列上取变化**(compare 输出 alignment.n_common_observations=513/n_change_pairs=512 佐证)。本席以对齐层口径复算命中,引擎口径在输出契约中可自明(alignment 块随行)。

**判定: PASS(5/5 全中,D 复算另计)。**

## ③ 缺口清单闭环

- **台账结构**: 评估表 18 项(数据 11/统计 4/研究 3/Agent 能力 1 之分布)+已实施 1 项(SOFR/WALCL 首跑登记)+已收口 3 项(1m/1y/5y 自配对正式口径、QB-023 排序依据披露、analog P0 七项)——append-only 纪律与"收口项移入第三节注记 commit"的声明与文件实况一致。
- **新增功能↔缺口闭环**: SOFR/WALCL 确因 Case A 缺口而加——QB-021(06:08Z 归档)明确记录"流动性维度四经济体全缺是最大研究缺口",台账选型依据同句引用;QB-029 附录真实使用(1m/1y/5y/相关/与 M1 连接,全部真数据);registry diff 全程仅 +SOFR/+WALCL 两条(本席 grep 确认)。
- **越红线不实施项守界**: 东京 CPI(台账#4)/TIC·EPFR(#6)/FCI(#16)/ERP(#17)零拉取零接线;JP_CPI_TOKYO_YOY/CN_OMO_7D/CN_SF_FLOW/ECB_MRO/BUND/CAC40/DAX 仍在 v3 noncore_missing 名单(缺席如实披露而非静默);OMO 维持 PENDING 不冒充。
- **归档 open_questions↔台账映射**: QB-021(CN 序列化/EA/JP/流动性/跨境流/盈利/EPS/HY 3yr/CN 股指/单值断层/PE_TTM 滞后)、QB-022(同上+ZQ 曲线/月网格 ev/长窗 rt)、QB-023(信用候选侧全缺/排序键→P2-1 收口/事后块 4 资产/release_lag/vintage)、QB-029(CN·EA·JP 流动性/频率感知阈值/SOFR 10yr 不可得/相位切换月度分解)——逐条可在台账 18 项或收口/首跑登记中找到落点,无孤儿缺口。

**判定: PASS。**

## ④ Agent 调用记录可追溯

- 四档 evidence/statistics 均结构化携带: 命令形态(analog --anchor 2026-10 --top 5/compare 自配对/overview/changes)、快照 id 与 research_as_of、n 与口径(pp/pct/月网格/exact_date)、引擎警示转述(date_gap/断点/样本不足/源端 3yr)、掉落数(a_dropped/b_dropped)。凭抽查即可从命令重放出归档数字(本席①项 31 数全中即证明可重放性)。
- 审计链完整: C7_case_execution_design(案例设计)→ C7_P0_seven_issues_verify(七问题复现,基线 cca2e4a)→ C7_P0_fix_review(308f615 复验)→ P2_DATA_GAP_LEDGER(处置登记)→ engine-notes Charter7-2 处置注记 → QB-021/022/023/029(研究成果)。缺陷发现→裁决→修复→复验→披露每环有档。
- 研究-工程互证: QB-023 把排序键现象"报协调方不自行修"→台账收口→P2-1 披露落地→本席源码级复核(专项①)——记录链闭合。

**判定: PASS。**

## ⑤ 代码/测试/文档/提交(三笔 commit diff 级审)

### (a) WALCL 单位口径版本内修订(million_usd)——合法
- 独立验证: v3 之前全部快照(research_snapshot_20261108/20261110/20261110_v2)grep WALCL/SOFR = 0/0/0——**billion_usd 错标从未进入任何快照事实**;registry v2.7.0 的 WALCL 事实唯一载体就是 v3(已为 million_usd);74657be 虽提交过 billion_usd 标签,但分支未 push、无任何数据产物携带该标签(测试 fixture 为合成值且断言为比值,量纲不变)。
- 修订内容=标签+量程 [3000,10000]→[3,000,000,10,000,000]+calc/release_semantics 文案+SERIES_UNITS 描述,**零换算逻辑**(存原始值惯例,RSAFS 同例);真实值 6,748,145(百万=$6.75T)与 5y 基点 8,574,871(=$8.57T)量级自洽。6a0dd80 并新增防错位测试锁(量程百万级+百万标签)。
- 台账"首跑登记"如实记录校准事由。**判定: 合法。**

### (b) 锁测试文件随升——全部合法校准,无"改期望值制造通过"
- P2 批 10 个锁测试文件(charter6_p1_missing_series/charter6_p2_shiller/e2e_frozen14/oss_workbench/p03_e2eb_b3/p03_final_acceptance/p1_wp_a/b/c/e)逐 diff 审: 计数锁 106→108、版本 2.6.0→2.7.0、聚合 US 53→55、活跃 104→106——与注册表 +SOFR/WALCL 一一对应;尾序锁 [-8:]→[-10:-2] 属块前移,**并新增 ('SOFR','WALCL') 尾序锁**(锁面净增强);vintage_additions 集合断言从"含 4 项"扩为"含 6 项"(新增必须成员,更强);e2e_frozen14 noncore_missing 12→14 如实点名新登记条目缺席(诚实方向)。未发现任何断言删除/放宽。
- P0 侧: afin ⑧⑨ 为语义回转(70102d5 方向经第一轮审计判错),新断言更严(前缀逐字锁+三形态 fixture+**同日 _vN 不翻 blocked 的方向反转回归锁**);charter5_zero_key_matrix/test_ia_cli 为精确集合断言扩键+新增专断言(更强);charter6_p4_analog 重写经本席核验: 期望侧为测试自写镜像(build_feats/ind_z/ind_step/ind_required/闭式 ramp_z),引擎符号仅作被测对象或声明性规格表(FEATURE_SPECS/load_registry),**无引擎计算函数产期望再喂回**;p02_w3 六套各 +1 行 opt-in 环境变量=mock 路径到达性修复,断言本体零改(未 opt-in 零调用路径由 charter7_p0 独立覆盖)。
- **判定: 全部合法。**

### (c) P2-1 纯披露零计算——成立
308f615→74657be 的 analog_engine.py diff 逐行共 3 处: SORT_BASIS 常量(含裁决注记)/输出顶层 'sort_basis' 字段/每条目 'n_missing' 计数。无任何计算路径改动。本席在 v3 环境实跑 TOP-5 与 QB-023(v2 时点)逐值一致,亦为行为不变的实证。**判定: 成立。**

### 独立全量套件
CI 同款逐文件执行(test_model_live 按 CI 契约排除): **112 文件中 111 套执行,110 套全绿,1 套(test_oss_product)43/44**。该 1 项失败经本席根因定位为**套件 CWD 敏感性**(观察 3): 检查"清空 PATH→应 rc=127+venv 指引"时,run_daily.sh 的 dirname 兜底把 PROJECT_DIR 解析到套件 CWD,而本席隔离环境 /tmp/ia-c7 恰含 .venv→Python 被找到→127 分支被绕过;在无 venv 的 CWD(/tmp)复跑同套件 **44/44 全绿**,且本席手工复现 127+修复指引路径成立。产品行为符合设计(观察记录,非缺陷)。

**判定: PASS。**

## ⑥ 红线终检(七项)

| 红线 | 核查 | 结果 |
|---|---|---|
| 未 push 未合并 | dev/charter7-research-v1 无 tracking 远端;`git branch -r --contains 6a0dd80` = 0 | ✅ |
| main 未动 | main = cca2e4a(=公开 v0.6.0-alpha 基线),一字未移 | ✅ |
| LIVE 零触碰 | launchd com.investment.daily/weekly 均指向旧管线根(~/AI内容/🤖_AI投资项目/…),非 DEV 树;本席全程只读核查 | ✅ |
| 零付费 API | 新闻模型摘要已改显式 opt-in(Charter7-7);P2-3 唯一外部调用=FRED 免费 API·现有 key·协调方书面批准;本席验收全程零 API | ✅ |
| 零新凭证 | 全 diff(3911 行)凭据形态扫描(api_key=/sk-/Bearer/password=/32hex)=零命中 | ✅ |
| FRED key 零回显零入档 | 台账/审计档仅出现变量**名**(FRED_API_KEY 无值);四档 QB-021/022/023/029 sidecar 32hex/sk- 扫描=零命中;revision_reason 只述"现有 FRED key" | ✅ |
| 公开面零厂商字样 | diff **新增行** 厂商A/厂商A/厂商A(大小写任意)=0 命中 | ✅ |

**判定: PASS。**

---

## 专项复核(三项历史判定,D席裁定)

### ① QB-023 排序键疑似缺陷之裁决——**裁决维持: 机制无错+P2-1 披露收口正确**
- 源码级复核(analog_engine.py): `weighted_distance(..., wsum_total=W_U)` 文档字符串明示旧重归一口径"仅独立单元测试保留,引擎主流程不再使用";主循环(协调方所指 :593 距离调用区)对每候选取固定分母距离后 `dists.sort(key=lambda x: (len(x['missing']), x['D'], x['month']))`——**排序键=(缺席数,距离,月)三键,非任何重归一距离**。A席"疑似仍用旧重归一口径"的机制归因**不成立**(其 D/accounted_wsum=2.1448<2.2670 的吻合属数值巧合,双键同样且更直接地产生该序);但其观察的现象(2020-12 D=1.19 排在 2019-12 D=1.01 之前,名次非纯距离序)**真实**,且当时输出未披露排序依据——缺陷定性准确。
- 输出契约复核: 顶层 `sort_basis` 逐字"(n_missing, distance, month) — 缺席特征多者降位,名次非纯距离序,比较相似度请以 distance 字段为准"+每条目 `n_missing`;distance_percentile 按 D 值独立于名次计算(核验 ds 列构造),分位不受排序口径影响。三处文档(cli-contract/SKILL/engine-notes)同步,engine-notes 含 QB-20261110-023 处置注记。
- 方向性评估: 缺席多者降位=保守方向(缺证据的候选不得凭更小距离反超),与"宁缺毋滥"哲学一致;QB-023 转述时已并列两种口径供读者自判。**裁定: 机制无错,披露已补,零计算改动——处置正确。**

### ② WALCL WARN(周频被日频启发式评)——**同款同文案确认;登记而非修=正确处置**
- 逐字对照: WALCL 与 ICSA 的 issues 完全同构——{category: continuity, severity: WARN, message: "<ID>近20自然日观测覆盖率3/15偏低(长假/停牌/采集缺口)"},仅指标名不同。ICSA 同款 WARN 在 20261108 快照已在场=**既有现状,非 P2-3 新引入缺陷**。
- 处置核验: 台账首跑登记已如实注记"与既有周频 ICSA 同款同文案(一致现状,非新缺陷;频率感知分母属后续引擎批,不在本台账范围)"+QB-029 open_questions 登记频率族适配建议;WARN 不改变 Gate A 语义(WALCL 仍 WARN 级、已从 noncore_missing 除名)。本批不动启发式=符合最小变更与"只登记不越界"纪律。**裁定: 登记正确,不应在本批修。**

### ③ Gate A=DEGRADED 的 8 项 noncore_missing——**确认全部为其他通道既有缺席**
- v2 与 v3 的 noncore_missing **完全一致**的 8 项: BUND_10Y/BUND_2Y/CAC40/CN_OMO_7D/CN_SF_FLOW/DAX/ECB_MRO/JP_CPI_TOKYO_YOY——SOFR/WALCL 入 v3 后即除名(事实 96→98,SOFR=PASS/WALCL=WARN,本席逐项核过 fact 层)。
- 通道归属: BUND×2=BBK 通道未采集、CAC40/DAX=Yahoo 欧股未采集、CN_OMO_7D/CN_SF_FLOW=CN 通道(PENDING/未采集,台账#2/#6)、ECB_MRO=EA 通道当日缺席(base/v2 已在场缺失,11-08 快照曾有数据)、JP_CPI_TOKYO_YOY=无免费源(台账#4 越红线不实施)——**无一项属 FRED macro 通道**,P2-3 的 macro 单档拉取不可能修复,缺席以 noncore_missing 如实披露而非降 Gate A 为 FAIL(语义正确: core_fail=[] 恒空)。**裁定: 确认。**

---

## 观察项(非缺陷,供后续批次参考)

1. **QB-029 头部引擎版本标注失准(文本溯源瑕疵)**: 归档正文写"@dev/charter7-research-v1(308f615)"但其内容(SOFR/WALCL 节点+自配对)在 308f615 注册表下不可产出(无 WALCL/SOFR 条目→no_series),实际运行环境≥74657be(数据 v3 由 P2-3 首跑产出)。数据本身本席已全部验真;仅版本标注沿袭母档未更新。建议后续归档头部版本号取运行时实值。
2. **归档文本两处笔误**: QB-023 §3+4 表后推断句混入西里尔词"горизонт"(应为"窗口");QB-022 S2 "ZQ_IMPLIED_AVD−DFF"(应为 AVG)。排版级,不影响数字与判定。
3. **test_oss_product"无Python环境"检查的 CWD 敏感性**: 该检查在套件 CWD 含 .venv/venv 时必然失败(run_daily.sh 的 dirname 兜底令 PROJECT_DIR 落到 CWD,venv 命中→127 分支绕过)。CI(无项目 venv)与无 venv CWD 下均绿;建议后续给该子检查固定 CWD(如 cd 到空临时目录)以消除环境依赖。本席在 /tmp 复跑 44/44 绿。
4. **WALCL×UST_10Y 相关的口径自明性**: 对齐层变化口径(alignment.n_common_observations=513→n_change_pairs=512)已随行,但"变化对=对齐后逐段变化"的语义对不读源码的用户仍偏隐晦;compare 的 change_basis 披露可加一句"变化在对齐序列上计算"。纯文档增强建议。
5. **正面记录**: candidates 四元组(scanned/valid/dropped_overlap/dropped_insufficient)+sort_basis+{资产}_window 起止观测日+features_dropped_at_anchor 带原因分类,使本次全部关键数字可在不读源码前提下由归档复算——这是本轮诚实性设计中最有价值的部分,建议作为后续能力的披露基准。

## 复验环境备注

- 全部命令在 /tmp/ia-c7(clone@6a0dd80)隔离执行;证据文件 /tmp/c7D_*.json(analog/compare/自配对/档案四件)、/tmp/c7D_suite_logs/(111 套日志+summary)、/tmp/c7D_full_diff.txt(全量 diff 扫描底稿)。
- 本席零 API 调用、零凭证读取、DEV 工作树仅新增本报告文件(未 commit);LIVE/launchd/main/远端零触碰。

**终验结论: Charter 7 六项验收全部 PASS,三项专项复核均维持/确认既定裁决;无 BLOCKER,无 DEFERRED;观察 5 条如上。**
