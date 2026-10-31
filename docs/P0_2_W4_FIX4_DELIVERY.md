# IA-P0-2-W4-FIX4 交付说明(输入根symlink授权保护+文件提取失败状态传播)

任务: IA-P0-2-W4-FIX4-DEV-v1.0 | 验收契约: IA-P0-2-W4-FIX4-AC-v1.0(冻结)
性质: FIX3独立验收失败后的**最小增量整改**(两项确定性源码缺陷+必要交付,
不重建W4/不从main或W3重来/不重写FIX1~FIX3)
基线: FIX3最终失败Commit `45db462f1b42bd1a0a6f101745d4fff440739ffe`
(=FIX3最终CI run 41213242780的49套"离线绿"不作为FIX4验收结果);
FIX2最终失败 `94fb1446`;FIX1最终 `5c65b231`;W4首轮 `62c1661`;
W3封版 `497b02c7b770d4eadb9086d453fea14d275bd4c9`;
GitHub main=P0-1封印 `50b5d13db6c477084c6f4b3944b7bd08a8e329d6`(禁合并)。

---

## 1. FIX3失败基线
Agent 4判定FIX3 FAILED的两项确定性缺陷(其余FIX3成果全部保留):
1. **FIX4-01 输入根符号链接自动授权**: `discover_files`的
   `root=os.path.realpath(data_dir)`把用户提供的路径直接解析为授权根——
   data_dir本身是symlink时,未经确认的目标目录被自动授权读取。
2. **FIX4-02 提取失败不传播**: `run_audit`提取循环捕获异常仅记
   `e['extract_error']`,状态判定只看`readable`/`input_changed`——全部文件
   提取失败仍返回COMPLETED退出码0,冒充完全成功。

## 2. FIX4实现与最终版本
增量Diff(`45db462→FIX4最终SHA`): scripts/historical_coverage_audit.py
(两项修复+SCHEMA_VERSION 1.3→1.4);tests/test_p02_w4_fix3.py(B5修订+1处
schema字面量);tests/test_p02_w4_fix1.py(1处schema字面量);
tests/test_p02_w4_fix2.py(1处schema字面量);tests/test_e2e_four_weeks.py
(1处时钟钉住,见§9);tests/test_p02_w4_fix4.py(新增41检查);
docs/P0_2_W4_FIX4_DELIVERY.md(本文件)。
**未触碰**: 采集器/fact_engine/snapshot_builder/trading_calendar/
metric_registry.json/新闻系统/Gate A/B/P0-1~W3代码/Mac LIVE/launchd/
生产data/daily/GitHub main;不实施W5或P0-3。

## 3. 两项缺陷及修复
- **FIX4-01**: `validate_paths`与`discover_files`在把输入路径realpath解析为
  授权根**之前**,检查用户实际提供的路径
  (`os.path.normpath(os.path.abspath(data_dir))`后`os.path.islink`,只查
  末组件)是否为symlink——是则fail-closed拒绝(问题文本/`PathBoundaryError`
  含原路径→目标realpath,提示"直接传入已确认授权的真实目录路径"),经既有
  `INVALID_PATH`路径退出码2,不自动跟随读取/不写输出/不生成成功报告。
  **不先realpath再检查**(realpath会解析掉symlink身份=自动授权);系统级
  路径别名祖先(测试沙箱基础路径,如macOS /tmp→/private/tmp)不影响——
  islink只判末组件。
- **FIX4-02**: ①Manifest逐文件`extract_status`(SUCCESS/FAILED/SKIPPED)
  与`readable`独立;②`extract_file`新增顶层记录与五通道主容器
  (global/macro的data/derived、china三表、rate的current_rates/
  real_economy/fed_funds_futures、research的facts/series_store)严格形态
  校验——非对象容器raise新`ExtractionError`(含空串/False等falsy垃圾不得
  经`or {}`当合法空对象),缺失/None=合法空容器(零观测,成功);③文件级
  原子性: 每文件先在隔离累积器(tmp_accs/tmp_unmapped)提取,成功才经
  `_merge_acc`(全字段合并,文件顺序处理+即时合并,与顺序直写等价)并入
  正式聚合,失败文件中途已产生的部分指标结果整体丢弃(不污染);④状态:
  全部可解析文件提取失败→`EXTRACTION_FAILED`,部分失败→
  `PARTIAL_EXTRACTION`,退出码均2;⑤`main()`写报告状态集合同步扩展两新
  状态(有合法输入且已形成Manifest的提取失败保留机器可读失败报告,不只
  控制台打印)。

## 4. 输入根symlink授权边界(§4)
- 默认拒绝: 传symlink根→INVALID_PATH/退出码2/零输出/不读目标字节
  (canary验证)/输入侧零改动;消息含"输入数据根为符号链接"+原路径→目标
  realpath(供人工确认授权)。
- 正向对照(§4.3): 明确授权后**直接传真实目录**正常完成(不误拒合法用法)。
- 边界保持: daily/子目录symlink拒绝、文件级symlink跳过披露、候选文件
  realpath containment(FIX3-02)全部保留;相似前缀兄弟目录仍按commonpath
  拒绝。

## 5. 提取成功与JSON解析成功的区别(§5.1-5.3,5.7)
`readable`=JSON可解析能力;`extract_status`=提取执行结果。固定反例
`{"date":"2026-10-20","data":["SPX"]}`: readable=True而extract_status=
FAILED,audit_status=EXTRACTION_FAILED≠COMPLETED,退出码2,extract_error+
文件路径+SHA-256+失败原因+执行日志齐备。`"data":"invalid"`/`""`/`false`
均为FAILED(falsy垃圾≠合法空对象);`"data":{}`为SUCCESS零观测(合法空)。
真实冻结副本848文件主容器形态全符合(dict/list齐备,零异常)——严格校验
不误伤真实数据(2026-11-01扫描证实)。

## 6. 全部失败与部分失败状态(§5.4-5.6,5.8)
- 全部可解析文件提取失败→`EXTRACTION_FAILED`(退出2,零指标获观测);
  部分失败→`PARTIAL_EXTRACTION`(退出2,成功文件数据正常保留不丢失,
  失败文件可追溯且不出现在任何指标input_files)。
- 报告四件套(JSON/Manifest/MD/执行日志)均含: 提取成功数/失败数/
  `extraction.failed_files`(relpath/channel/sha256/extract_error)/
  最终audit_status/exit_code/输入完整性状态;MD含"提取不完整…不得当
  COMPLETED使用"显著披露;JSON`extraction`节含两概念独立判定的definition。
- 优先级: ALL_UNREADABLE>INPUT_CHANGED>EXTRACTION_FAILED>
  PARTIAL_EXTRACTION>COMPLETED(INPUT_CHANGED语义不变)。

## 7. 修订的旧B5及原因(§4.5,场景保留)
`tests/test_p02_w4_fix3.py::test_b5_*`: 场景与构造完全不变(输入根=显式
`os.symlink(real,entry)`),断言由"经symlink入口exit=0 COMPLETED"反转为
"默认拒绝exit=2/零输出/消息含'输入数据根为符号链接'+正向对照(直接传
real→COMPLETED)"。**旧预期违反冻结契约F3-AC-03的原因**: FIX3的授权边界
定义"授权根=数据根realpath"在data_dir本身为symlink时等于把未经确认的
目标自动纳入授权——旧B5恰以"自动跟随symlink入口并成功"为期望,把FIX4-01
判定的缺陷固化成了断言。安全负例未删除,仅安全预期反转(修订依据=
FIX4指令§4.5)。

## 8. 新专项测试(tests/test_p02_w4_fix4.py,41检查,全部真实main/discover_files)
- **A组8**(§六A): 真实目录成功/输入根symlink拒绝/daily外指拒绝/文件级
  symlink跳过/相似前缀/跨平台临时目录(不依赖OS路径别名,FIX3 CI run#1a
  教训的确定性版本)/§4.4固定负向(alias→real-data+canary: 拒绝+不读正文+
  不写两侧+退出2)/拒绝后全树无成功审计产出。
- **B组11**(§六B): 正常成功/坏JSON→SKIPPED/数字data/`data:["SPX"]`固定
  反例全断言/非法字符串data("invalid"/""/false)/合法空`{}`/一文件全失败/
  两文件部分失败(成功数据不丢失+失败文件不在任何input_files)/两文件全
  失败/单文件中途异常原子性(CPI中途结果被丢弃,MISSING+0 input_files)/
  已注册单指标Schema仍正常记录(FIX3-01语义: schema事件≠提取失败,
  COMPLETED)。
- **C组8**(§六C): readable与extract_status独立(同审计两组合并存)/
  failed_files完整(64位SHA)/六状态-退出码映射/Manifest保留失败文件/
  81项不虚增/SHA可追溯(测试复算==报告值)/MD披露(计数+文件+状态+退出码+
  禁用声明)/JSON与日志一致(末行状态-退出码+提取失败行)。
- **D组10**(历史合同): FIX3别名Schema溯源(GOLD→GOLD_F)/FIX3近期历史
  findings2口径/FIX2槽位不变量(observed==unique,sum(segments)==observed)/
  FIX2两文件完整input_files+SHA关联/FIX1连续段4槽/FIX1同文件重复拆分
  (same_file_extra≥1且unique<raw)/MARGIN_BAL仅rzye_billion不获权威/
  五通道全发现提取/audit_commit=git HEAD+generated_at UTC+schema 1.4/
  输入只读(SHA前后一致,PARTIAL状态亦只读)。
- **E组4**(负向退化必检出): ①恢复realpath自动授权(对alias路径让
  islink说谎)→symlink根被跟随且COMPLETED(A2/A7敏感);②恢复readable唯一
  成功判定(提取失败状态改写回COMPLETED/0)→全部失败仍成功(B4/B7/B9);
  ③删除提取错误传播(剥离extraction块与manifest提取字段)→状态在但零文件
  级诊断(C2/C4/C7);④部分失败仍COMPLETED(B8)。全部经mock注入缝+真实
  main()执行,非复制算法。

## 9. 原W4及FIX1~FIX3回归+旧测试修订
本地全量(推送前): tests/下50套件(49旧+新增fix4;test_glm_live按契约
排除)全部exit=0。修订3类(均为最小语义修正,场景保留):
1. **fix3 B5**(§7);
2. **schema字面量1.3→1.4**×3(fix1/fix2/fix3): FIX4语义变更(新状态+新字段
   +symlink拒绝)属版本升级,断言结构不变;
3. **test_e2e_four_weeks.py 1处时钟钉住**: "当月未完结→预览模式"检查把
   '202610'当"当前未完结月"——2026-11-01本地时区起
   `month_is_complete('202610')`恒True(纯日历时滞;该套件零引用FIX4模块,
   生产代码monthly_review.py未动)。修订=该检查内把`mr.date`钉在
   2026-10-31(期间内),场景与断言语义(期间未完结→预览)不变。

## 10. 最终CI(workflow_dispatch, dev/p0-2-w4)
实现Commit→推送→CI run#1(实际数字回填于下)→文档回填→最终固定Commit→
推送→CI run#2(最终SHA)。最终轮实数按防预写纪律不入Git,见Git外附件
IA-P0-2-W4-FIX4-REAL-AUDIT-*.txt与IA-P0-2-W4-FIX4-POSTCOMMIT-ISOLATION-
*.txt及对话交付报告。FIX3的49绿(41213242780)不作为FIX4验收结果;CI必须
跑FIX4最终SHA;不合并main(50b5d13)。

### CI实证(回填区)
- **run#1(实现Commit `73065ee1f871c49a7f958bd93b903db5a839067d`)**:
  Actions Run ID=**41219621123** | Job ID=**124591260146**(tests) |
  event=workflow_dispatch | head_branch=dev/p0-2-w4 | head_sha=73065ee…
  conclusion=**success** | **50套件全部exit=0**(test_glm_live按契约排除;
  逐套件test_<name> exit=N自Job日志逐行提取,非零数=0;W4五套件:
  test_p02_w4=0 / fix1=0 / fix2=0 / fix3=0 / **fix4=0**;
  test_e2e_four_weeks=0含§9.3时钟钉住)
- run#2(最终固定Commit): 见Git外附件

## 11. 正式真实数据审计(§十,最终固定Commit后实际执行)
复用冻结副本前**重新核实授权**(不预设848): 目录存在/输入根非未确认
symlink/逐文件SHA-256与LIVE原件对应/与授权范围一致;核验不过→停止并
如实报告。在FIX4最终固定Commit干净工作区执行(audit_commit==最终GitHub
SHA+真实UTC generated_at);Git仓库外独立新目录(不覆盖FIX1/FIX2/FIX3
产物);输出4文件+81项分布+完整input_files+读取与提取状态(extract_status/
failed_files)+退出码+输入未变化证据。**必须真执行并交付**。

## 12. 全部81项报告
真实审计输出全部81项注册指标(不截断),逐项含coverage/input_files/
discovery/counts;状态分布与FIX1~FIX3对照如实(预期与FIX3一致:
71 OBSERVED/2 SPARSE/2 MISSING/6 DERIVED_ONLY——真实数据主容器形态
全符合,extract_status应全SUCCESS,如不一致如实披露)。

## 13. 完整Manifest
`input_manifest_*.json`逐文件(relpath/channel/collector/file_date/size/
mtime_ns/sha256/readable/error/**extract_status**/extract_error)全量不
截断;与FIX1~FIX3同输入→同run_id可复算比对。

## 14. 最终DEV/LIVE只读隔离核查(⑨)
核验时间/DEV HEAD与分支与工作区/GitHub main=P0-1封印/W3封版未动/DEV与
LIVE realpath+inode不同体/LIVE无.git/launchd指向LIVE/LIVE核心源码=P0-1
封印SHA-256/W4+FIX1~FIX4新模块未部署LIVE/生产零触碰(只读元数据)/冻结
副本与授权来源关系/无法证明的历史瞬时事实如实声明。FIX3时点隔离证据
不证明FIX4终态。

## 15. §十二实际文件交接
真实审计后生成`IA-P0-2-W4-FIX4-ACCEPTANCE-EVIDENCE.zip`(Git外),含7类
**实际文件**(非模板): ①81项完整coverage JSON②完整input Manifest③MD
报告④执行日志⑤DEV/LIVE隔离原始记录⑥脱敏授权与冻结副本证明⑦最终
GitHub/CI执行摘要;对话交付报告列每个文件路径+字节+SHA-256+最终Commit+
CI Run/Job+审计退出码。未实际交付不得宣告READY;禁止打包生产密钥/
未授权原始数据/不必要私人研究正文。

## 16. 未验证事项
- 真实生产数据金融数值真实性/W5研究充分性(全部research_sufficiency=
  UNDETERMINED)。
- LIVE冻结时点后新增文件不在授权集,未读。
- 日历近似的单日级断点判定近似性(逐指标经calendar_limitations披露)。
- MARGIN_BAL两融合计重建(须另行确认来源/单位/公式)。
- 真实数据无自然触发的输入根symlink与主容器形态异常(潜伏态): 两项修复
  正确性由合成固定反例+E组退化注入证明;真实审计extract_status全SUCCESS
  即为"未触发"的如实证据,非缺陷不存在。
- 单次快照+SHA复检证明当前时刻;历史瞬时事实无法事后证明。
- test_e2e_four_weeks时钟钉住(§9.3)后,该套件不再依赖运行时钟——若未来
  需要滚动"当前月"场景,须另行设计冻结时钟注入缝(超出FIX4范围)。

## 17. 最终状态
三选一结论见对话交付报告与Git外附件(材料齐全→**READY FOR W4
INDEPENDENT ACCEPTANCE**;确定性阻断→FAILED;缺真实审计或隔离材料→
NOT VERIFIED)。不自行签发W4 PASS/不合并main/不部署LIVE/不提前实施
W5、P0-3。
