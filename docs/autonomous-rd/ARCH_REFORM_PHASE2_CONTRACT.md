# 阶段二: 统一研究数据契约设计 v1.2(2026-11-14 操作者席·Architecture)

> v1.1=金融席审查 1 BLOCKER+5 MAJOR 全采纳;v1.2=独立审计席 APPROVE-with-conditions C1-C6 全落(§4b/§3 crossing_count/律8/§5 C1 载重墙/C5 数值化门)+金融席策展轮 2 项修正(律8 裸%规则/版本标识)。修订清单见文末。**两席放行,设计面闭环**。

> 章程: CHARTER-ARCH-REFORM-2026-11-14.md §四。输入=阶段一基线(共同根因: 语义非一等可验证对象;追认式闭环)。
> 原则2落地: 只新增「断言层+验证层+文本一致性」,采集/快照/统计/历史比较/观点库/Agent Native/CLI/档案/Git状态系统全保留。

## 0. 现有资产盘点(实读 2026-11-14,非记忆)

| 资产 | 实况 | 契约角色 |
|---|---|---|
| snapshot facts | `research_snapshot_*.json` facts[] 已含 `fact_id("SPX@2026-11-13")/metric_id/display_name/value/unit/value_type("level")/observation_date/as_of/source{collector,file}/calculation_ref/calc/identity` | **Fact 层原样复用**,不建第二套 |
| anchors | 扁平 path 键(`global_market.data.SPX.close`→值+meta) | 验证对照源之一(保留) |
| 阈值 | **四源且已漂移(金融席实锤)**: ①framework.md 四种异构格式(利率表/OAS bp表/DXY散文/WTI表)②macro_scorecard.py 硬编码带(L239-247 同函数三个「高通胀线」数字=活标本)③registry validation.range(SPX[1000,30000])④data_validator.py L238-251 又一套(SPX 2000-10000,与③矛盾=11-14 误杀当事代码) | **缺口→人工策展 thresholds 注册表(金融席逐行签字)+headline/band 边缘两级建模+CI 三方对账门** |
| 数值入口 | `report_generator.py _call_model`(L494/536)模型从 prompt 数据直写散文;输入侧已有锚点 prompt 确定性复核(FIX-01) | 改造为消费 claims bundle |
| Agent Native | `agent_judgment.py validate_judgment` 纯结构/存在性检查;`evidence_index` 行={ref,kind,metric_id} **无值**;S4 序列(n=784/2498)在 report.json 无人读 | 阶段四改造点(evidence 带值) |

## 1. 分层契约(目标架构→模块映射)

```
Data Sources            → 现有 collectors(保留)
Canonical Snapshot      → 现有 snapshot_builder(保留;facts=Fact 层)
Evidence Records        → 统一 ref 语法: fact_id / series_ref(S4序列) / VIEW-ref(机构观点) / QB-ref(传导边) / claim_ref(断言链) / prior_bundle_ref(上期引用) / reconciliation_ref(对账记录)
Structured Claims       → 新 scripts/research_contract/claim_factory.py(确定性六型)+模型断言提交(两型)
Deterministic Verify    → 新 scripts/research_contract/claim_verifier.py
AI Research & Interpret → 现有 report_generator / agent_judgment(改造为消费已验证 claims)
Semantic Review         → 常驻独立语义审计席(阶段四落;席须真 Subagent,可拒开发者声明;I/O 契约=§4b,审计席 C4 条件)
Rendering & Delivery    → 现有渲染 + 新 text_consistency.py(数值溯源门)
```

## 2. ResearchClaim v1.0 契约

```json
{
  "claim_id": "CLM-20261114-0031",
  "claim_type": "threshold_distance",
  "metric_id": "HY_OAS",
  "value": 0.80,
  "unit": "percentage_point",
  "window": null,
  "observation_date": "2026-11-13",
  "evidence_refs": [{"ref": "HY_OAS@2026-11-13", "kind": "snapshot_fact", "value": 3.20, "unit": "percentage_point"}],
  "threshold_ref": {"name": "warning_400bp", "value": 4.00, "unit": "percentage_point", "provenance": "thresholds-registry:hy_oas.warning@v1(stable key,非行号)"},
  "attribution": "deterministic",
  "derivation": {"basis": ["HY_OAS@2026-11-13", "threshold:warning_400bp"], "formula": "|3.20-4.00|=0.80pp"},
  "verification": {"status": "VERIFIED", "checked_against": "snapshot+thresholds", "computed": 0.80, "delta": 0.0, "tolerance": 0.0, "checker_version": "claim_verifier 1.0"},
  "disclosure": null
}
```

- **claim_type 顶层八型(章程「至少」允许扩展)+必填 subtype(v1.1)**: level(含 band 子结构: 区间对象 100-104/3.75–4.00%=一带对象两数)/change(**relative/absolute 必显式**)/comparison(**spread/diff/rank**)/threshold(带 relation+since_date)/threshold_distance/observation_lag/forecast(带 ticker+合约月份身份: 近月 ZQ=F vs 日历月同屏须可辨)/qualitative_inference;**新增 statistic 型**(相关系数等联合统计量——framework §七强制每周 3-5 对,现契约无处落)与 **composite_score 型**(评分卡输出=确定性派生,非 qualitative);持续性陈述(连续第N周/2024-09-05 后无倒挂)=threshold.since_date+last_crossing 谓词;上期引用(上期103.44/评分+4→+2)=claim_ref/**prior_bundle_ref**;对账记录=reconciliation_ref
- **evidence_refs 必带值**(设计决策,直击故障B): 引用即携带被引 fact 的值与单位——「引用存在且值相符」从此可机械验证
- attribution: `deterministic`(工厂派生)｜`model_inferred`(模型提交)
- forecast 型必带 horizon+条件框架;qualitative_inference 型必带「可判定谓词」子结构(见§3)
- 版本管理: bundle 文件 `claims_YYYYMMDD.json`(快照旁挂,snapshot/anchors/data_pack/QB 档零改动);schema_version 字段

**八条设计律→机械执行**(章程§4.3 逐条):
1. 身份不靠文本: claim 自带 metric_id+claim_type;渲染只消费已验证 claim
2. 水平vs变化: value_type/claim_type 强类型;change 必带 window+基准值
3. **单位代数(以 metric_registry 为源的开放枚举+契约不变式,v1.1 重写)**: (claim_type,subtype,unit) 三元组定语义;变化必须显式 **relative(pct,basis 必带) vs absolute(pp/bp/原单位)**;pp↔bp=×100 精确且 canonical 字符串=Fact 层既成名 `percentage_point`/`basis_point`(不再出现 pp/bp 缩写名);percent↔pp 无基准禁换算;「400bp=4.00%」两 token 须映射同一 threshold claim;**渲染后缀不得反推单位**(OAS「3.20%」实为 pp 水平的显示形态;DXY「距离0.59」裸数同理);跨指标差(spread/diff)须同单位校验;Fact 层已实现此代数(实测 23 单位/11 value_type,周变化双轨:SPX=pct_change/UST_10Y=pp_change/HY_OAS=bp_change)——契约对齐既成事实,不另造
4. 数据日期 vs 研究日期: observation_date 与 as_of 字段级分离
5. 预测vs已发生: forecast 型永不与 level 同渲无标记
6. 未验证不冒充已验证: 渲染器只接 status=VERIFIED;其余进披露区
7. AI 给数不自动过: model_inferred 数值 claim 由 verifier 对照 fact/公式复算;不符=CONTRADICTED
8. 自由文本新数字不绕过: text_consistency 抽取渲染文本全部数值 token,逐一须映射到已验证 claim 或白名单(阈值/日期);**映射=三元(值,单位后缀,claim 角色)兼容(C2,金融席策展轮修正)**——**裸 % 后缀不携带单位信息**(OAS「3.20%」=percentage_point 水平的显示形态,「+2.51%」=percent 相对变化——按律8 原文两类各数十处全部违法=洪泛),故映射主体=manifest 的 claim 角色+值,后缀仅作**否定性排除**(pp/bp 后缀排除 percent 单位映射);值碰撞不可消解→SEMANTIC_REVIEW_REQUIRED,**禁 first-match**(审计席反例②: 水平值 3.20 冒充距离 3.20pp);**白名单税则冻结(C3)**: 计数须走 crossing_count 确定性派生或禁入【事实】标注句,白名单任何新增须金融席签字(与 thresholds 注册表同纪律)——此条不立,追认式闭环将以白名单形态还魂;未映射→SEMANTIC_REVIEW_REQUIRED 清单显式披露

## 3. 确定性断言工厂(核心杠杆)

六型(level/change/comparison/threshold/threshold_distance/observation_lag)**全部从 Fact 层+S4 序列+thresholds 注册表确定性派生,不过模型**——故障A类从根消灭: 提取器不复存在,数值语义身份从不离开结构域(「滞后166天」「距离0.80pp」从此是 claim,不是文本猜)。

- change: fact(level)×前值 fact,公式随行;**分解可加性**: basis 含 claim_ref 的 change claim 须做可加性复算(framework§三每周分解: 实际+0.23+BEI+0.01=名义+0.24,对不上=CONTRADICTED)
- threshold_distance: |level−threshold|,阈值取自 thresholds 注册表(provenance 指回 framework.md 行)
- observation_lag: as_of−observation_date 天数
- **qualitative_inference 的可算子集**(阶段四,直击故障B): 位阶/分位/形态类定性措辞→可判定谓词。**谓词文法(v1.1 扩)**: `percentile_rank`/`sign_flip_date`/`last_crossing` 三基础+**AND 组合**(如 Sell America 三条件);分位公式钉死 `100×(严格小于+0.5×并列)/n`,窗口边界=前一年度最后观测(与 derived.ytd basis 约定一致)含当期,**min-n 门**(n<20→INSUFFICIENT_EVIDENCE;月频 ytd 禁用),当月不完整标「年内至今」。「处年内低位」=percentile_rank(ytd)<10(与 R24 审计 95.6 百分位口径一致);「回正/从倒挂转向」=last_crossing 问题非百分位问题(sign_flip_date=2024-09-05)。R24 两 MAJOR 若有此层即机器可拦。**crossing_count 谓词(C3 补)**: 「2024 年以来第 3 次触及」类历史计数=可确定性派生(序列遍历计数+min-n 门)——计数不再依赖白名单放行(审计席反例①「第 3 次」零验证直通=已堵)。
- **序列可得性缺口(金融席实锤,阶段三前置依赖)**: 周报路径 series_store 46 键**不含 HY_OAS/CURVE_2S10S**(序列只在 Agent Native S4 信封)——须先补周报路径序列通道(扩展 series_store 或接 S4 存档),否则谓词无米下锅。

模型职责收缩为: narrative 文本+qualitative_inference/forecast 两型断言提交。**不声称 JSON 本身保证结论正确**(章程§4.3): 语义审计席(§1)保留对 narrative 与推断链的独立内容审查权。

## 4. 六验证状态+发布规则(章程§4.4)

| 状态 | 允许正式发布? | 披露要求 |
|---|---|---|
| VERIFIED | ✅ | 无 |
| CONTRADICTED | ❌ 禁发布——**claim 级修订+机械重渲染,非整报隔离**(否则 11-14 断供模式在新架构里复活) | 修订记录随档 |
| INSUFFICIENT_EVIDENCE | ✅(须披露) | 证据不足注记随文 |
| NOT_VERIFIABLE | **仅 deterministic 工厂产物可「披露后发布」;model_inferred 数值 claim 落此态=强制升 SEMANTIC_REVIEW_REQUIRED,禁直接发布**(v1.1 封死洗数通道——否则模型编任意数→无权威源→带脚注照发=故障B换皮) | 逐 claim 归因{路径/原因枚举/可否次级交叉};禁入【事实】区、禁加粗 |
| STALE | ✅(须披露) | **按滞后÷发布节奏分级**(社融227天≠ECB59天,单级太粗);披露**随文相邻**(11-14 报告 L33 现行写法=范本);滞后>2-3 个发布节奏禁入「现状」框架;**派生 claim 继承最差输入陈旧度**(美日利差=新鲜DFF−滞后74天JP利率→按74天档) |
| SEMANTIC_REVIEW_REQUIRED | ⏸ 暂缓;**超时策略=剔除存疑项+披露剔除后发布**(不无限期卡死) | 待语义审计席裁决;清单显式列出未映射数值/存疑断言 |

**Gate B 新语义**: PASS ⇔ (a)全部数值 claim 已验证 (b)text_consistency 零未映射数值。旧 Gate B 保留为对照路径(阶段三并行)。

**VERIFIED 语义注记(C6)**: VERIFIED=与权威快照一致,**≠市场真值**;报告用语不得将全绿表述为「数据经确证」;采集真值防线(Gate A+registry 合理性区间)保留并测试——plausible-but-wrong 采集值新旧架构同样不设防,如实入契约文档。

### §4b 语义审计席 I/O 契约(C4,阶段四实现,接口现补)

- **唤起点**: (i)text_consistency 产出 SEMANTIC_REVIEW_REQUIRED 非空;(ii)qualitative_inference/forecast 型 claim 待裁;(iii)超时策略触发前;(iv)任何席位/用户提请。
- **读取面**: claims bundle 全量+narrative 全文+被引证据原文(fact 值/S4 序列/VIEW 档/QB 档)+verifier 结果。
- **职责(章程6.2 四查+证伪)**: 证据相关性/支持度/竞争解释/反对证据/结论是否超出证据/证伪条件——须主动找反例。
- **裁决词表**: `UPHELD`(维持发布)/`REVISE`(claim 级修订+重渲)/`NOT_VERIFIED`(禁入事实区,可入观点区带标注)/`REJECT_ENTRY`(剔除+披露)。
- **状态迁移**: 裁决写入 claim.verification 与 narrative 审计档;REVISE→修订闭环(同 R24 模式但常驻化)。
- **归档**: `audit/semantic_review/YYYYMMDD/` 逐次落档(裁决+依据+引用),append-only。
- **过渡条款**: 本席就位前,周报携带常设披露「叙事语义未经独立裁决」——诚实优先于体面。

## 5. 迁移与并行(章程§五)

- 新包 `scripts/research_contract/`: claim_factory / claim_verifier / claim_bundle / render_hook / text_consistency **五小模块**,禁 god-module。**render manifest 义务(v1.1)**: 渲染器产 claim_id→文本位置映射;text_consistency 退化为「manifest 复核+游离数值扫描」——实测周报 537 数值 token/215 唯一值,纯抽取映射的「零未映射」门在千分位逗号/区间端点/换算对/约数上必成**新误杀工厂**(教训: 不能用新正则替代旧正则)
- **C1 载重墙(审计席,阶段三写码前最高优先)**: **渲染器=确定性模板,消费 VERIFIED claim,产出全部数值单元格/表格+manifest;模型丧失整文数值著作权**,只供 narrative 文本+qualitative_inference/forecast 两型断言提交。manifest 只准由该模板产出,**禁模型自报、禁按值反扫重建**——这一句是从「架构整改」滑回「换一层正则」的分水岭。
- **thresholds 注册表(v1.1 定稿方向)**: 人工策展(金融席逐行签字),headline 级+band 边缘两级建模,provenance 用稳定键非行号;**CI 三方对账门**(注册表/framework.md/评分卡代码常量);优先级明文——claims 只认注册表;data_validator 硬编码带(L238-251,11-14 当事)退役改读 registry;registry validation.range(合理性区间)与分析阈值**概念隔离**
- 并行 harness: 同一真实输入双路(旧 Gate B vs 新链),比较章程5.2 六指标;固定验收集=V1-V4+留出样本(QA 席封存,开发不可见)
- 迁移条件=章程5.3 六条逐条固化预写;任一不满足→**不迁移,重新审查设计**(明文,禁为完成整改强行迁移)
- **C5 数值化迁移门(审计席)**: 迁移门开跑前预固定数值标准(例: V6 改写集零误杀/V5 注入集拦截率≥预写值/CI 零红/零新增白名单项);「重大回归」=枚举事件类(V 集任何误杀/未验证内容入【事实】区/状态漂移复发);**迁移裁决权=独立审计席**(章程§九);QA 席=无 dev 树上下文的全新子代理;anchors/claims 双源并行=过渡期合法但**设 sunset 决策点**(防第二套事实数据库以 anchors 形态长存)
- **留出集结构性限制(如实,审计席E)**: 真实事故仅两起且已被固定集消耗,留出集至多**样本级盲**、不可能**模式级盲**(故障分类学对开发已知);迁移结论**不得表述为「真实留出验证通过」**,只可表述「合成注入+改写变体留出通过」
- 回滚: 新链纯增量旁挂(开关切回),旧路径原样可恢复

## 6. 兼容与不破坏

- 现有 CI 六门+143 测试零触碰;新套件独立文件挂载
- snapshot/anchors/data_pack/QB/判断档 schema 零改动(阶段四 evidence 带值=向后兼容 additive)
- Agent Native 路径: research-attach 链零变动直至阶段四统一切换

## 7. 开放问题(阶段三开工前须闭)

1. **(升:阶段三开工前必闭)精度往返规则**: 按单位定渲染位数+往返相等(7561.669922→7,561.67 ✓;3.8775 四位须显式);「约X」按所示位数取整相等,禁整体容差
2. model_inferred 数值 claim 容差策略(逐指标族 vs 沿 Gate B 现行容差)
3. 留出样本集构造与封存协议(QA 席);**V5/V6 注入集须纳入金融席点名形态**: 排名/相关性/分解可加性/区间端点/千分位+CJK 复合单位(12,245.39亿元/159,293千/551.84亿港元/英文189K/负值带逗号-5,846亿元)/约数/上期引用/nan 散文/反推链式(derivation.basis 收 claim_ref)
4. 情景概率和=100% 机检;prior_bundle 引用协议(bundle 本就周落盘)
5. anchors 与 claims 的冗余关系长期归一方向(阶段三后再定)

## 8. 阶段二完成条件对照(章程: 可执行的契约+接口+迁移方案+相应测试)

- [x] 数据契约: ResearchClaim v1.0(§2)+证据 ref 带值语法
- [x] 模块接口: 五小模块边界(§5)+分层映射(§1)
- [x] 迁移方案: 并行 harness+六条迁移条件+回滚(§5)
- [ ] 相应测试: =阶段三开工件(fixture 冻结协议=V1-V4 已在场,V5/V6+留出集=QA 席阶段三开工前交付)——契约的可执行验证随首条纵向切片交付,不以设计文档冒充
- 待: ~~Financial Research 席审查~~→**已毕: 终判放行(零残留 BLOCKER/MAJOR)**;~~Independent Auditor 席设计评审~~→**已毕(2026-11-14): APPROVE-with-conditions, C1-C4/C6 已落本档(§4b/§3 crossing_count/律8/§5 C1 载重墙/C5 数值化门), C5 治理项随迁移门执行**。**阶段二设计面闭环;阶段三前置余项=QA 席 V5/V6+留出协议+数值标准、thresholds 策展稿交金融席签、series_store 序列通道(首个码任务)**

## v1.1 修订清单(金融席意见→落点)

| 席判定 | 落点 |
|---|---|
| BLOCKER: NOT_VERIFIABLE=model_inferred 洗数通道 | §4 状态表: 仅 deterministic 可披露发布;model_inferred 数值落此态强制升 SEMANTIC_REVIEW |
| MAJOR-1 八型不完备(排名/相关性/价差/分解/区间/评分卡/持续性/上期引用每周必现) | §2: subtype 层+statistic/composite_score 新型+band 子结构+since_date+prior_bundle_ref/claim_ref/reconciliation_ref |
| MAJOR-2 单位模型自相矛盾(Fact 层已实现正确代数) | §2 律3 重写: (claim_type,subtype,unit) 三元组;relative/absolute 必显式;渲染后缀不反推单位;对齐 Fact 层 23单位/11 value_type 既成事实 |
| MAJOR-3 阈值四源漂移(评分卡同函数三个「高通胀线」;data_validator 与 registry 矛盾=11-14 当事) | §0 实录+§5: 策展注册表+两级建模+CI 三方对账门+硬编码退役 |
| MAJOR-4 percentile 五项未钉死+序列管道缺口 | §3: 谓词文法+公式钉死+min-n 门+last_crossing;series_store 缺 HY_OAS/CURVE=阶段三前置依赖 |
| MAJOR-5 状态规则洞(STALE 单级/派生陈旧度/CONTRADICTED 整报隔离=断供复活/NOT_VERIFIABLE 归因粒度) | §4 全行重写 |
| MAJOR-6(自由题) 缺 render manifest→纯抽取映射=新误杀工厂 | §5: render manifest 义务;text_consistency=复核+游离扫描 |
| 自由题 3-11(千分位/约/区间/反推/nan/精度/合约身份/概率和/稳定键) | §7 开放问题清单(1 升为阶段三前必闭) |
| **v1.1a(终判后机械修,席授权自证免重审)**: 示例JSON三处unit改percentage_point+provenance稳定键/§2律3canonical点名/§1补三类ref/§3可加性复算显式化 | §2示例·律3·§1·§3,本表即自证 |
| **金融席终判(2026-11-14): 放行阶段三,零残留 BLOCKER/MAJOR**;附带条件=Independent Auditor 设计评审(独立于金融席)+thresholds 策展稿交金融席逐行签 | §8 |
