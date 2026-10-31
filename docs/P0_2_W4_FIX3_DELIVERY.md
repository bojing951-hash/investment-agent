# IA-P0-2-W4-FIX3 交付说明(已注册异常Schema溯源+父目录symlink越界阻断+近期历史合法槽位口径)

任务: IA-P0-2-W4-FIX3-DEV-v1.0 | 验收契约: IA-P0-2-W4-FIX3-AC-v1.0
性质: W4-FIX2独立验收失败后的**最小增量整改**(三项确定性缺陷+交付证据,
不重建W4/不从main或W3重来)
基线: FIX2最终失败Commit `94fb1446e8e4c6ef20580abd2d90105477defca9`
(FIX2两轮CI 41205021727/41205244712均48绿但验收判FAILED);FIX1最终
`5c65b231`;W4首轮 `62c1661`;W3封版 `497b02c7b770d4eadb9086d453fea14d275bd4c9`;
GitHub main仍=P0-1封印 `50b5d13db6c477084c6f4b3944b7bd08a8e329d6`(禁合并)。

---

## 1. 修复范围(只针对FIX2验收失败的三项确定性缺陷)

1. **FIX3-01 已注册异常Schema与未注册混在同一条unmapped路径**: 旧实现
   `if mid not in registry_ids or not isinstance(item, dict): _unmapped(...)`把
   "指标不存在"与"指标存在但记录结构错误"合并——已注册指标的结构异常既拿不到
   指标身份,也不出现在该指标的input_files溯源里。
2. **FIX3-02 父目录符号链接可越出授权数据根**: 旧实现只拒文件自身是symlink
   (`os.path.islink(p)`),不检查候选文件的**真实路径**是否仍在授权根内——
   daily/整体外指symlink时越界文件会被当有效输入读取。
3. **FIX3-03 近期历史findings与合法槽位口径不一致**: 旧判据
   `uniq>=1 and span<30`用原始唯一观测日数+首末自然日跨度——纯周末异常
   (NO_VALID_SLOTS)会被误入"只有最近数据",日历外远端异常日期会无依据撑大
   正式跨度把真近期数据误排除。

FIX1/FIX2已通过的语义全部保留(槽位连续段/重复拆分/MARGIN_BAL口径/五通道
发现/NO_VALID_SLOTS与UNDETERMINED/完整input_files/Manifest+SHA-256/81项
输出,经D组历史合同回归逐项锁定,§8)。

## 2. FIX3实现(修改限于允许清单)

增量Diff(`94fb144→FIX3实现Commit`): scripts/historical_coverage_audit.py
(约1350→1507行,纯增量修复);tests/test_p02_w4_fix3.py(新增34检查);
tests/test_p02_w4_fix1.py(1处schema字面量,§9);tests/test_p02_w4_fix2.py
(1处schema字面量,§9);docs/P0_2_W4_FIX3_DELIVERY.md(本文件)。
**未触碰**: 采集器/fact_engine/snapshot_builder/trading_calendar/
metric_registry.json/新闻原始来源及W3/Gate A/B/P0-1~W3代码/Mac LIVE/
launchd/生产data/daily/GitHub main;不实施W5或P0-3。

## 3. FIX3-01 已注册异常Schema逐指标溯源

- `extract_file`新增闭包`record_schema_bad(mid, key, auth)`: 取得MetricAcc→
  `a.invalid_date+=1`+`a.note('schema',…)`→`_file_event_bad(a, rel, ch, auth,
  'record', 'record_schema:not_object')`登记文件到file_contrib——保留Manifest
  关联(relpath→sha256/size/mtime_ns)、文件出现在该指标input_files、
  invalid_reasons含`record_schema:not_object`、valid_observation_contributed
  =false;**不生成有效observation_date/数值、不增权威历史**(状态如实MISSING,
  不冒充覆盖)。计数口径: 文件级Schema异常不一定对应一条可识别观测记录,
  不能伪造observation_date,故不进记录级raw计数(与series_shape文件级事件
  同口径)。
- 五通道拆分点: global/macro的`未注册 or 非对象`合并条件拆为两分支(未注册→
  unmapped;已注册非对象→record_schema_bad);china三表(a_share_indices/
  hk_indices/indices·a_share·hk legacy)由`if mid and isinstance(item,dict)`
  的静默跳过改为身份/结构两分支(`{"a_share_indices":{"000001.SH":"invalid"}}`
  归入SHCOMP无效来源);rate_economy的current_rates与real_economy同样拆分
  (real_economy事件auth=False,与recon_point同口径)。
- **无法确定metric_id的元素级非对象不分配给指标**(保持跳过): fed_funds_
  futures列表非dict元素、research facts非dict元素——分配给任何指标都需伪造
  身份。series_store已由`_add_series`的series_shape事件覆盖,不重复。
- 不做通用Schema引擎(仅外层记录对象性判定,与指令§四一致)。
- unmapped文案同步收窄: "未注册**或形态异常**"→"未注册"(形态异常不再进
  unmapped,无旧测试断言该文案,§9)。

## 4. FIX3-02 阻断父目录符号链接越界(fail-closed)

- 新`class PathBoundaryError(Exception)`;授权边界=**用户指定数据根的
  realpath**(symlink目标不自动获授权)。
- `discover_files`: ①`root=os.path.realpath(data_dir)`后,`daily/`本身是
  symlink即`raise`(父目录逃逸整体拒绝,不逐文件补救);②每候选文件在既有
  文件symlink跳过之后`rp=os.path.realpath(p)`,`os.path.commonpath([rp,root])
  ==root`方可用(禁用startswith前缀比较;commonpath异常ValueError=必在界外)
  ——防御纵深,覆盖未来模式加深/结构变化;③错误传播: run_audit以
  try/except捕获→`INVALID_PATH`+problems+退出码2。
- 拒绝时: 不读越界文件字节/不入Manifest/不创建不写out-dir/无COMPLETED输出/
  输入侧零改动/诊断信息只含路径不含内容。
- 兼容性(B5/B6实证): 正常`data/daily/china_20261020.json`保持可用;五通道
  任意子集有效;输入根与daily并存保留FIX1选择规则;macOS符号路径前缀
  (/tmp→/private/tmp)下root先realpath故不误拒。

## 5. FIX3-03 近期历史findings与合法槽位口径统一(只改summarize)

- 新判据(替换`uniq>=1 and span<30`): ①状态属有效历史类
  (`SINGLE_OBSERVATION/SPARSE/OBSERVED`;NO_VALID_SLOTS/UNDETERMINED/
  MISSING/UNREADABLE/DERIVED_ONLY不入);②跨度由**有效覆盖槽位对应的实际
  观测范围**计算——`continuous_segments`(只含预期日历内槽位,start/end=段内
  实际观测日首末)的全段首末`max-min<30`自然日;`coverage.observation_span_
  days`/`total_unique_observations`保留为描述性原始字段不作判据。
- 固定反例实证: NDX纯周末(10-17/10-18)→NO_VALID_SLOTS/0槽/无段/**不入**
  findings2;SPX单合法交易日→SINGLE_OBSERVATION保持且**入**合法短历史;
  SPX合法2026-10-16+日历外远端2026-01-03(周六)→raw span=286≥30但有效槽位
  跨度=0→**仍入**(远端异常日期不扩大正式跨度),extra照常披露。
- `eligible_slots()`/`classify()`/槽位统计零改动(指令§六边界);findings2
  definition文本同步公开口径。
- 不回归: 完整历史/严重断点findings/81项汇总/研究充分性UNDETERMINED/
  MD与机器findings一致(C6)。

## 6. SCHEMA_VERSION
`w4-coverage-audit/1.2`→`**1.3**`(findings2口径变更+input_files新增schema
事件类型+INVALID_PATH新增路径边界子类)。

## 7. 新专项测试(tests/test_p02_w4_fix3.py,34检查,全部真实main/discover_files)
- **A组9**(§四固定例A-F): SPX字符串/NFP数组/SHCOMP字符串/别名GOLD→GOLD_F/
  current_rates FEDFUNDS→逐项核指标身份+input_files+invalid_reasons+Manifest
  SHA关联+有效观测数0+状态MISSING;UNKNOWN_X仍unmapped且两类不再互混;
  RUT合法正向不受影响;schema 1.3。
- **B组8**(§五强制测试,全部真实文件系统临时构造): daily目录symlink外指→
  ec2/INVALID_PATH/零输出;文件symlink跳过披露;discover_files单元级
  PathBoundaryError(消息含双方realpath);相似前缀兄弟目录allowed_evil不因
  前缀比较误通过;正常daily在符号路径前缀下不误拒;china-only子集81项;
  拒绝后allowed/outside两侧零新增;越界正文canary扫描(唯一含canary的文件=
  越界源文件本身)。
- **C组6**(§六固定反例): NDX纯周末不入;SPX单合法日入;正常短跨度入;
  UNDETERMINED不入(expected_slots注入缝,对照可认证时入);远端异常日期
  不扩大跨度(raw span≥30仍按有效槽位跨度入);MD与JSON一致。
- **D组8**(历史合同): 合法槽位2/缺1/2段;全81项槽位和不变量;同文件+跨文件
  重复拆分不变量;MARGIN_BAL仅rzye_billion不获权威;完整input_files两文件
  全列;通道子集计数;audit_commit=git HEAD+generated_at UTC;输入只读SHA。
- **E组3**(负向退化必检出): `_file_event_bad`退化为no-op→schema文件从
  input_files消失(A1/A9必败);`discover_files`退化为跟随父symlink→越界文件
  被读取且COMPLETED(B1必败);`summarize`恢复uniq+span旧判据→NDX误入/SPX
  误出(C1/C5必败)。全部经mock注入缝+真实main()执行。

## 8. 全量历史回归(本地,推送前)
tests/下48个test_*.py: 47套执行全部exit=0(test_glm_live按workflow契约
排除),含test_p02_w4.py/test_p02_w4_fix1.py(40)/test_p02_w4_fix2.py(34)/
**test_p02_w4_fix3.py(34)**及W3/W2/W1/P0-1/E2E/Gate A/B全部历史套件
(逐套件退出码见§11 CI实证)。

## 9. 旧测试修订(最小语义修正+理由)
仅2处schema版本字面量`1.2→1.3`(test_p02_w4_fix1.py L759、
test_p02_w4_fix2.py L580): §6版本升级是FIX3合同本身的语义变更,断言结构与
场景不变,仅字面量随实现升级——这是允许清单中"必要的W4/FIX1/FIX2测试最小
语义修正"的既定情形,非冻结合同回退。其余fix1 40检查/fix2 34检查零改动
(unmapped文案无断言依赖;findings2内容仅键存在断言)。

## 10. 输入真实路径边界(本轮授权)
真实审计只读授权冻结副本`/Users/cast/audit/w4-real-data`(W4授权范围的
逐字节副本),执行前按§12重新核验(目录存在/授权范围/逐文件SHA-256与LIVE
原件对应/路径无越界);LIVE冻结时点后新增文件不在授权集不读;不执行网络
回补;FIX3-02使越界路径构造在工具层即被拒绝。

## 11. GitHub提交与CI(workflow_dispatch, dev/p0-2-w4)
FIX3实现Commit→推送→CI run#1→本文档回填→最终固定Commit→推送→CI run#2
(最终SHA)→正式审计→隔离核查→附件交付。两轮Run/Job ID/head_sha核对/逐套件
退出码: run#1入本文档CI实证节;**最终轮实数按防预写纪律不入Git**,见Git外
附件IA-P0-2-W4-FIX3-REAL-AUDIT-*.txt与IA-P0-2-W4-FIX3-POSTCOMMIT-ISOLATION-
*.txt。FIX2的48绿(41205021727/41205244712)不作为FIX3验收结果;CI必须跑
FIX3最终SHA。不合并main(50b5d13)。

## 12. 正式真实数据审计(FIX3-06,最终固定Commit后执行)
- 复用冻结副本前重新核验(不预设848): 目录存在/授权范围有效/逐通道清单/
  逐文件SHA-256与LIVE原件(/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/
  investment-agent/data/daily)比对/与原始授权对应/路径无越界;核验不过→
  停止并如实报告NOT VERIFIED|REAL-DATA AUDIT PENDING。
- 在FIX3最终固定Commit上执行(audit_commit==最终GitHub SHA+真实UTC
  generated_at+干净工作区);Git仓库外独立新目录(不覆盖FIX2产物
  /Users/cast/audit/w4-fix2-real-audit-output);输出4文件(JSON/MD/Manifest/
  日志)+代码SHA+执行时间+退出码+81项分布+完整input_files映射验证+输入
  未改证据+异常与研究限制。**必须真执行并交付**,不得只写"将于最终Commit
  后执行"。

## 13. §十三实际文件交接
完成真实审计后在对话交付报告中列全部实际生成文件+完整本地路径+字节大小+
SHA-256: ①81项完整机器报告②完整输入Manifest③人类可读MD④执行日志⑤DEV/LIVE
隔离记录⑥脱敏证据说明;作为用户可实际取得的附件交接,Agent 4可逐项打开核查。
不上传未授权原始生产文件/API密钥/私人研究正文;不截断81项或贡献文件清单。

## 14. 最终DEV/LIVE只读隔离核查(⑩)
核验时间/DEV HEAD与分支与工作区/GitHub main=W3封版后的P0-1封印SHA/
W3封版497b02c未动/DEV与LIVE realpath+inode不同体/LIVE无.git/launchd实际
路径与工作目录指向LIVE/LIVE核心源码=P0-1封印SHA-256/W4及FIX1~FIX3新模块
与新测试未部署LIVE/生产数据与长期状态零触碰(只读元数据)/冻结副本与授权
来源关系/不能证明的历史瞬时事实如实声明。FIX2时点的隔离证据不证明FIX3终态。

## 15. 未验证事项
- 真实生产数据金融数值真实性/W5研究充分性(全部research_sufficiency=
  UNDETERMINED)。
- LIVE在冻结副本时点后的新增文件不在授权集内。
- 日历近似(cn仅2026精确/hk最小集/fx周一五/FRED按NYSE近似)的单日级断点
  判定近似性——逐指标经calendar_limitations披露,非金融事实。
- MARGIN_BAL两融合计重建(须另行确认来源/单位/公式)。
- B3单元级PathBoundaryError与防御性逐文件containment检查: 现行单层glob
  结构下文件级越界仅经父目录symlink可达(已由B1/B3/B4端到端+单元覆盖);
  逐文件检查为结构变化预留的防御纵深。
- 历史瞬时事实只能以单次快照+SHA复检证明。

## 16. 提交与推送纪律
实现Commit→推送→CI→文档回填→最终固定Commit→推送→最终CI→正式审计→隔离
核查→附件交付;此后不再新Commit(再出Commit须重新固定SHA/CI/审计/隔离);
不force push/不合并main(50b5d13)/不部署LIVE/不启动W5或P0-3。

## 17. 最终状态
三选一结论见对话交付报告与Git外附件(材料齐全→**READY FOR W4 INDEPENDENT
ACCEPTANCE**;确定性阻断→FAILED;缺真实审计或隔离材料→NOT VERIFIED)。
不自行签发W4 PASS/不合并main/不部署LIVE/不提前实施W5、P0-3。

---

## CI实证(workflow_dispatch, dev/p0-2-w4, offline-tests.yml)

### CI run#1 — FIX3实现Commit `<实现Commit SHA占位,推送后回填>`
- Actions Run ID: `<占位>` | Job ID: `<占位>`
- conclusion=success | 48套件全部exit=0(test_glm_live按契约排除;
  含新增test_p02_w4_fix3.py=34检查)

### CI run#2 — FIX3最终固定Commit(本Commit)
- 按防预写纪律不入Git,见Git外附件IA-P0-2-W4-FIX3-REAL-AUDIT-*.txt与
  IA-P0-2-W4-FIX3-POSTCOMMIT-ISOLATION-*.txt及对话交付报告。
