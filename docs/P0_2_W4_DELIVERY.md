# P0-2 W4 交付报告（历史数据覆盖只读审计）

任务编号: IA-P0-2-W4 ｜ 指令: IA-P0-2-W4-DEV-v1.0 ｜ 验收契约: IA-P0-2-W4-AC-v1.0
开发分支: dev/p0-2-w4（从W3封版建立，不合并 main，不部署 Mac LIVE，不触发任何采集器）

---

## 1. 基线与固定Commit

| 项 | 值 |
|---|---|
| W3封版基线（本轮起点，CI 41172799763） | `497b02c7b770d4eadb9086d453fea14d275bd4c9` |
| W4实现Commit（审计器+专项测试） | `62ed379f9b58a3b9cfbbc288f81f6c40f44b9fee` |
| W4最终固定Commit | 本交付文档所在Commit（完整SHA、CI run#2编号、Job ID、checkout SHA与真实数据审计实数按防预写纪律入Git外隔离证据与对话交付报告，不写入仓库） |
| W4增量Diff | `git diff 497b02c..HEAD` — 仅2个新增文件（scripts/historical_coverage_audit.py 1033行、tests/test_p02_w4.py 828行）+本文档；**零行改动既有代码** |
| 封版链 | P0-1 `50b5d13` → W1 `69d7fc7` → W2 `14fe6e5` → W3 `778050c`→FIX1 `522ca13`→FIX2 `e3d6b67`→FIX3 `ea93618`→FIX4 `e8b9e35`→FIX5 `497b02c` → **W4（本Commit）** |

## 2. 任务性质与边界（§一）

W4=对**实际已保存历史数据**的只读覆盖调查：基于 `data/daily/` 五通道每日JSON存档，独立核查全部81项注册指标的真实历史覆盖（最早/最晚/独立观测日/缺口/连续段/异常），输出可由输入文件逐条复算的审计报告。不是： 扩展采集器、十年回补、历史查询API、外部价格真实性验证（W5）、自动专题研究、修改金融事实引擎或生产报告。审计器不创造任何新数据。

## 3. 实际修改范围（§三工程边界）

新增仅2文件+本文档；零改动: fact_engine.py/snapshot_builder.py/trading_calendar.py/三个采集器/rate_expectations.py/report_generator.py/全部Gate与正式研究产物/config/metric_registry.json/全部既有测试。真实数据访问方式=生产 `data/daily/` 五通道JSON的**隔离冻结副本**（`cp -p` 保留mtime→SHA-256逐文件核对与LIVE一致→审计只读副本→结束后复核LIVE原件未变）；审计程序从DEV执行，从未在LIVE执行任何开发代码，未读取API密钥或私人研究内容（快照文件只消费 facts/series_store 数值字段），未在LIVE写入任何文件。

## 4. 历史数据源Schema（实测，§四W4-01）

审计器消费且仅消费5通道机器输入（同前缀`.md`人读镜像与anchors/scorecard/anchor_prompt/correlation/news为非本审计对象，计数披露于`input.excluded`）：
- **global_YYYYMMDD.json**: `data{asset:{close,"date"=最后收盘ISO日,series{dates,values}}}`；series块自2026-10-17（Layer2）起随文件保存，内含采集回看窗口（period='1y'/tail400）
- **macro_YYYYMMDD.json**: `data{name:{value,"date"=ISO最新观测,series{dates,values},revision{obs_date,prev_value,value}?}}`+`derived{...}`（无观测日字段）
- **rate_economy_YYYYMMDD.json**: `current_rates{FEDFUNDS/DFF/DFEDTARU/DFEDTARL:{value,date}}`、`real_economy{UNRATE/PAYEMS/...:{value,date}}`、`fed_funds_futures[{ticker,price,"date"=ISO真实观测日}]`（ZQ=F为主力行，ZQ**.CBT为月份合约）、`generated_at`
- **china_YYYYMMDD.json**（三代格式并存）: 新格式`a_share_indices{code:{close,"date"=YYYYMMDD,series}}/hk_indices/southbound{date,south_money百万}/margin{date,rzye_billion}/valuation{code:{pe_ttm}}嵌套/turnover{sh/sz/total_amount_billion}/ah_premium{date=ISO,close}`；旧代平铺；最旧代（仅20260326一天）`a_share{标签}/hk{标签}/southbound{latest}/volume{volume}`
- **research_snapshot_YYYYMMDD.json**（15文件，2026-10-17起）: `facts[{metric_id,value,observation_date,source}]`+`series_store{mid:{dates,values}}`（Layer3，恒非权威同源重复）

## 5. 81项指标身份处理（§六W4-03）

全部81项从真实注册表加载输出（含无数据者）。通道键→注册id映射全部复用项目既有实现，并由测试D组ast解析源码守护防漂移：
- `fe._GLOBAL_ID_MAP`（模块级直接复用）: GOLD→GOLD_F、SILVER→SILVER_F、WTI→WTI_F、BRENT→BRENT_F、JPY=X→USDJPY、CNY=X→USDCNY、GBPUSD=X→GBPUSD；其余global键=注册id原样
- macro别名 `{'WTI':'WTI_SPOT_M'}`（与fe函数内`_MACRO_ALIAS`同值守护）: 宏观现货月频与global期货日频**分开**
- china: `{"000001.SH":"SHCOMP","399001.SZ":"SZCI","399006.SZ":"CHINEXT"}`、`{"^HSI":"HSI","^HSCE":"HSCEI","^HSCEI":"HSCEI"}`（与fe/snapshot_builder同值守护）+最旧代中文标签（上证指数/深证成指/创业板指/恒生指数/恒生国企[指数]）
- rate: `current_rates` FEDFUNDS→FED_FUNDS（注册权威=macro→本通道**非权威**对账）；`real_economy` FRED键→注册id（UNRATE→UNEMPLOYMENT、PAYEMS→NFP等，非权威对账）；`fed_funds_futures` **ZQ=F→ZQ_F1_PRICE（权威）**，月份合约ZQ**.CBT→unmapped披露
- 权威性判定: `REGISTRY_SOURCE_CHANNEL`（注册表source声明通道）=采集通道→权威；research_snapshot（Layer3）与rate对账键恒非权威，只登记重复不新增覆盖
- 派生: REAL_10Y/REAL_5Y/HY_IG_DIFF/ZQ_IMPLIED_AVG（fact_engine(derived)）、REAL_SHORT（macro(derived)）、NFP_MOM_K（source_symbol含(derived)）→DERIVED_ONLY，不冒充独立原始历史
- 未注册键不丢失: 000300.SH/000905.SH/000852.SH（采集但未入注册表）、valuation嵌套pe_ttm（注册SH_PE语义=上证PE，非同身份，**不得**归SH_PE）、最旧代southbound.latest/volume.volume、全部月份合约→`unmapped_records`独立披露（真实数据26组，含每组出现文件数）

## 6. 日期提取规则（§七7.1）

只用: ①`series.dates`逐元素 ②单点字段`date`/`observation_date`（china `YYYYMMDD`紧凑格式经`fe._iso`规范化）。**严禁且未用**: 采集文件日期（文件名YYYYMMDD）、`as_of`、`retrieved_at`、`generated_at`、报告生成时间补造缺失观测日。严格解析（`fe.parse_iso_date`，非法日历日如2026-13-45拒绝），不做[:10]截断洗白。文件日期仅用于**前瞻性核对**（观测日晚于文件日→future_dated如实计数）。macro `derived`块无观测日字段→如实记invalid_date、零有效观测，不以文件日补造（负向敏感性E1守护此纪律）。

## 7. 数值与去重纪律（§七7.2/7.3）

- 数值: None/NaN/inf/bool/非法串→invalid_value如实记录；dates/values长度不一致→length_mismatch且该series整体不入观测（无法安全配对）
- 去重: 同observation_date跨文件重复采集只计一次观测日（cross_file_duplicate_records单独计数，真实数据GOLD_F=3560条重复）；同文件内重复日期（same_file_dup）；乱序（out_of_order）逐项记录；**同观测日不同值不擅自选真值**——round(6)分组全保留为`conflict_candidates`（真实数据GOLD_F=41个冲突日期，即跨日重采的序列修订候选）；macro `revision{obs_date,prev_value,value}`→`revision_events`捕获
- 快照重复: facts/series_store与每日文件指向相同底层数据→恒非权威，不重复计数（non_authority_only_dates披露"仅存于快照的日期"）

## 8. 频率/日历/缺口定义（§八W4-05）

预期槽位: **daily**=`tc.expected_trading_days`（全系统唯一日历权威；cn仅2026含精确节假日其余年份周末近似、hk最小集、fx周一~五、crypto 7×24）+`calendar_limitations`注记；**weekly**=ISO周一键；**monthly**=YYYY-MM键（同月多观测日只计一个月槽，负向敏感性E4守护）。输出 first/last/span/total_unique/expected/observed/missing_count+sample10/extra_beyond_calendar/coverage_ratio/longest_continuous_segment/continuous_segments/usable_intervals(≥2观测)/max_internal_gap_days。first→last只是跨度≠连续；未到发布日与无存档是不同问题（只报可证明部分，月度指标缺当月如实记missing）。全部阈值（断段日10/21/92、sparse<0.5、complete≥0.9且≥60独立观测、recent_only<30天）公开于`threshold_definitions`并声明为**工程描述约定非金融事实**；research_sufficiency恒UNDETERMINED。

## 9. 连续覆盖区间算法（§八）

相邻观测日自然日间隔>频率阈值（daily 10/weekly 21/monthly 92）断段；每段记录start/end/slots；usable_intervals=slots≥2的段；max_internal_gap_days=相邻观测日最大自然日间隔（serious break判定依据，报告发现3按频率阈值列出）。

## 10. 机器报告Schema（§十W4-07）

`coverage_audit_<run_id>.json`（顶层: tool/schema_version/run_id/audit_status/registry{path,version,metric_count}/input{data_dir,realpath,files,by_channel,unreadable_files,excluded,source_note}/summary{8计数+by_status+core_by_status+core_missing_or_unreadable}/metrics[81]/unmapped_records/findings六问/threshold_definitions/integrity{input_changed_during_audit,changed_files,manifest_digest,recheck}/）+逐指标: 身份块（metric_id/display_name/source/source_symbol/status/criticality/frequency/calendar/unit/identity/asset_class/calc/authority_channel）+discovery{found,authority_channel_records,non_authority_records,series_available,non_authority_only_dates,notes{长度不一致/乱序/非法日/非法值/语义漂移/单位换算有界样例}}+counts{16计数}+coverage{14字段}+conflict_candidates[:10]+revision_events[:10]+input_degraded+status+research_sufficiency。JSON可从输入manifest与原始文件逐条复算。`coverage_audit_<run_id>.md`: 总体表+81行逐项表+审计发现六问+unmapped表+阈值JSON+BASIS_NOTE+日历限制+证据限制。`input_manifest_<run_id>.json`: 每文件relpath/channel/collector/file_date/size/mtime_ns/SHA-256/readable/error。run_id=输入清单摘要前12位→**同输入字节级可复算**（测试C22双执行逐文件比对）。退出码: 0=COMPLETED/2=NO_INPUT·ALL_UNREADABLE·INVALID_PATH/3=INPUT_CHANGED。

## 11. 合成专项测试（§十一W4-08，tests/test_p02_w4.py，36检查）

覆盖24项强制用例: A组19（①81全输出②GOLD别名映射+WTI双通道语义③重复采集不虚增④月频跨日只计一次⑤单点/连续/usable区分⑥日频合法交易日（SPX工作日5槽ratio1.0；crypto 7×24）⑦非交易日观测+cn/hk日历近似注记⑧周月频缺口（ICSA缺3周/NFP缺2月）⑨真实内部缺口（BTC 20天断点2段/SHCOMP 200天）⑩乱序⑪非法日期⑫缺值⑬数组不等长⑭同日不同值候选⑮快照不重复计数⑯无数据指标仍输出⑰未注册来源披露+排除项计数⑱中国三代格式/单位换算注记/字段语义漂移⑲权威通道与派生/UNDETERMINED）；B组6（⑱部分损坏降级完成+input_degraded/全坏ALL_UNREADABLE退出2、⑲路径缺失退出2零写入、⑳非法输出路径三向拒绝+数据目录零新增、㉓空输入NO_INPUT不虚报、INPUT_CHANGED模拟检出退出3）；C组4（㉑输入SHA前后不变含mtime_ns、㉒重复执行字节级一致、㉔只读零副作用+报告Schema： 阈值公开/六问/81行表/未注册表）；D组2（身份映射ast漂移守护+通道权威矩阵）。全部走真实run_audit/main与真实注册表，未复制审计实现自证。
**负向敏感性5项（E组）**: E1 `to_obs_date`对None回退文件日→非法日期被"治愈"+观测虚增（用例⑪必败）；E2 去重失效同日多次抓取各计新观测（用例③必败）；E3 `expected_slots`用理论请求起点2025-01-01当最早观测日→覆盖率假坍塌（用例⑥必败）；E4 月频当日频→缺口假阳性（用例④⑧必败）；E5 classify把MISSING洗白成OBSERVED（用例⑯必败）。每项均实证"正确运行为真、退化运行为假"的检测性。

## 12. 真实审计执行证据（§十二W4-09）

- **开发期smoke（本Commit前，已披露）**: LIVE `data/daily/` 五通道848文件（global 210/china 210/macro 206/rate_economy 207/research_snapshot 15）`cp -p`冻结副本至Git外 `/Users/cast/audit/w4-real-data/`，SHA-256逐文件核对与LIVE一致（848/848，0差异）；DEV代码只读审计副本2.3秒完成: COMPLETED、848可读0坏、81项全输出、run_id `ra_d7a7f17bbf0c`；结束后复核LIVE原件848文件SHA全部未变（审计零触碰）。smoke产物在Git外 `/Users/cast/audit/w4-real-audit-smoke/`（不作为官方审计证据，仅开发调试）。
- **官方真实审计（本Commit后按§十四顺序）**: 用最终固定Commit代码+冻结副本（重新核对SHA）执行，完整脱敏审计记录与真实覆盖报告（run_id/81项状态分布/关键指标明细/六问发现）在对话交付报告与Git外附件 `/Users/cast/audit/` 交付Agent 4，不写入仓库。严禁且未做: 合成数据替代真实审计、period='1y'推断已存一年、observation_start推断最早观测日、网络API补回、因覆盖差改旧数据、改生产周报或长期状态。只有两周就报两周，没数据就报没数据。
- **真实数据smoke事实预览**（官方审计将复核）: 状态分布72 OBSERVED+2 SPARSE（ZQ_F1_PRICE 19观测/4段/最大间隔126天、HSAHP 25观测）+1 MISSING（SH_PE: 新格式valuation仅300/500/1000嵌套pe_ttm，与注册"上证PE"非同身份，26组unmapped如实披露）+6 DERIVED_ONLY；series backed 64/81；全部权威观测最早日2025-01-01（macro月频）/2025-10-17（global日频回看窗口）；ZQ=F仅出现在31/207个rate文件（历史真实现象，非解析缺陷——31文件外futures数组为空或仅月份合约）。

## 13. 输入完整性（§五5.2）

审计前: 逐文件size/mtime_ns/SHA-256/readable入manifest；审计结束逐文件重算SHA-256复检，任何变化→`INPUT_CHANGED_DURING_AUDIT`+changed_files+退出3（测试B25模拟采集器写入实测检出）。生产目录持续更新的事实如实披露，官方审计在冻结副本上执行（副本与LIVE原件SHA逐文件一致为前提，审计后复核LIVE未变）。manifest_digest决定run_id→同输入同输出，支持Agent 4独立复算比对。

## 14. P0-1~W3全量回归（§十三）

本地: tests/下47个套件文件，执行46个**全部exit=0**（test_glm_live按契约跳过且跳过逻辑本身exit=0）: 含W3 38/38、FIX1 44/44、FIX2 26/26、FIX3 26/26、FIX4 35/35、FIX5 33/33、W2/FIX1~6、W1/W1-FIX1、P0-1 FIX1~11、原始14项E2E/四周/冻结14、Gate链、fact_engine、snapshot、P0/P1/P2/P4/P7、phase3/4、round3~6、datafix。**零旧测试删改、零预期弱化**（本轮未触碰任何既有文件）。CI（offline-tests.yml排除test_glm_live）46套件。

## 15. GitHub Actions CI（workflow_dispatch, offline-tests.yml, ref=dev/p0-2-w4）

| 轮 | Run ID | Job ID | head_sha | 结论 |
|---|---|---|---|---|
| run#1（实现Commit 62ed379） | 41186236831 | 124493618278 | 62ed379f9b58… | success，46套件全部exit=0（含新增test_p02_w4；test_glm_live按workflow契约排除；逐套件退出码清单已从Job日志逐行提取核对） |
| run#2（最终固定Commit=本Commit） | 防预写: 编号/Job ID/head_sha/逐套件退出码在本Commit推送后运行，实证结果只入Git外隔离证据附件与对话交付报告，不写入仓库 | — | 最终固定SHA | 见Git外证据 |

## 16. DEV/LIVE隔离（§三）

DEV=`/Users/cast/investment-agent-dev`（独立Git仓库，分支dev/p0-2-w4，本轮前工作区0脏项）；LIVE=`/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent`（无.git）。开发前后只读核查: realpath+inode非同目录/非祖先后代；launchd两服务程序与工作目录仅指LIVE零DEV引用；真实数据只经冻结副本接触；LIVE原件复核未变。最终Commit与CI run#2后按§十四⑥执行完整只读取证（模板=W3-FIX5隔离脚本改W4版: 基线497b02c、分支dev/p0-2-w4、W4产物在LIVE缺席清单、两轮CI、零修改证明），证据入Git外 `/Users/cast/audit/` 并在对话完整输出（脱敏）。

## 17. 未验证事项

- 数值的金融真实性（报价错误/前复权漂移/幸存者偏差）——属W5，本审计只证本地存档覆盖事实。
- 生产目录未来新增文件的覆盖变化（单次快照式审计；快照与series保存策略的后续演进不在本轮范围）。
- ZQ=F行在176/207个rate文件缺席的**上游成因**（akshare失败缓存/采集时点）——本轮只如实报告覆盖率，不猜测成因、不修改采集器。
- SH_PE在新格式时代的可采集性（需上游确认上证PE数据源；本轮按身份矩阵如实归MISSING，不把300 pe_ttm冒充）。
- W4交付后的Agent 4独立工程验收结论（本报告不自宣PASS）。

## 18. W4-W5-P0-3边界（§一/§十五）

W4到此为止: 只读审计+可复核报告。不启动W5（外部价格真实性/回补授权属后续独立指令）、不启动P0-3、不修改采集器与研究状态、不部署LIVE、不合并main（main仍=P0-1封印50b5d13）、不产生新Commit改变最终固定SHA。

## 19. 结论声明

真实数据官方审计按§十四顺序在最终固定Commit上执行完毕后，结论只能是以下三者之一（由执行时点决定）: `READY FOR W4 INDEPENDENT ACCEPTANCE` / `NOT VERIFIED｜REAL-DATA AUDIT PENDING` / `FAILED`。W4是否通过由Agent 4独立工程验收决定；本报告不自宣W4 PASS。

---
*回填说明: 实现Commit（代码+测试）先行推送并完成CI run#1实证后，本文档回填实现SHA与run#1实数形成最终固定Commit；run#2对本Commit运行，官方真实数据审计用本Commit代码执行——两者实数按防预写纪律只入Git外审计附件与对话交付报告。此后零新提交，固定SHA不变。*
