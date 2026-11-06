# IA-P1-WP-G REPORT(常态监测 #20)

> 工作包: IA-P1-WP-G(=§4a 第二层收口链第 2 包/#20;终名=WP-P1-G,冻结章校准零全局替换)。执行 Agent: Agent 3。
> 基线: BASE-P1G=`8b157fd3c0c0b8a42407e49c84cbcc1254aa8a75`(2026-11-06T18:13Z 开工实取 ls-remote=origin/main 全值一致;=R062 merge commit)。
> 分支: `dev/p1-impl-g`(自 BASE-P1G 切出;此前本地与远端均不存在;路径甲=基线自带在场,零并入步,纯线性)。
> 规格源: `docs/P1_DESIGN.md`(HEAD blob=`10e026c08ce2828908ff7a5421aee8aba1f4e6d0`=冻结章登记期望值;行号=工作树实读)。
> 边界声明(§5.3 第 5 项): 本文日期/时刻=UTC;SHA=全值;行号=开工时点工作树实读(P1 设计三件以基线工作树在场版为准);「注入摘要,非工作树实读」标注=提示词 §2 注入内容。

---

## §零 规格抄录、交付文件清单(白名单)、特有纪律、DP 与实现参数登记(开工首步,先登记后实现后运行)

### §零.1 开工核验(步骤 0-4 实录)

| 项 | 结果 | 摘要 |
|---|---|---|
| 步骤0 时序 | 过 | git status clean;开工 UTC=2026-11-06T18:13:21Z;HEAD=8b157fd(=BASE-P1G) |
| 步骤1 占位符 | 过 | §0 四占位符全实值(BASE-P1G/BASE-P1G-CI-SUITES=76/BRANCH-SET=49 支全表/规格锚=§六 L175+§八.2 L225-L256) |
| 步骤2 前置实取 | 过 | ls-remote: main=`8b157fd…`(=BASE-P1G)/dev/p1-design=`049ec978…`/dev/p1-design-comp=`7190eb7…`/dev/p1-impl-f=`44a7a686…`(=冻结章登记 R062 最终 PASS 尖端)全值一致 |
| 步骤3 切分支 | 过 | `dev/p1-impl-g` 自 BASE-P1G 切出(此前本地与远端均不存在);ls-remote 全表 49 支与冻结章 BRANCH-SET 逐一对照一致(49 支全在场,白名单外新支零在场,dev/p1-impl-g 尚未推远端为切出前实取) |
| 步骤4 设计在场(路径甲) | 过 | 祖先判定×2: `merge-base --is-ancestor 7190eb7… HEAD`=exit0(设计在场✓);`merge-base --is-ancestor 44a7a686… HEAD`=exit0(#19 并入证明✓);三件 blob 对照(HEAD ls-tree 实取): P1_DATA_NEEDS_INVENTORY.md=`df79c06f66c368d93159b7a3b46852b6fcb9b196`/P1_DELIVERY.md=`314c2644a51f2f575a90253580cb56346e2f93b6`/P1_DESIGN.md=`10e026c08ce2828908ff7a5421aee8aba1f4e6d0`——三值=冻结章登记期望值逐值一致;禁锚 `c9626633`: 工作树 grep 命中仅历史包 REPORT「禁锚未混入」核验措辞 7 文件(P1_DESIGN 三件本体零出现),零锚定使用 |

### §零.2 规格抄录(AC-01;逐字抄录自 docs/P1_DESIGN.md 工作树实读)

**锚 1 = §六 L175(包行,五列)**:

> | WP-P1-G(候选名)常态监测(§4a#20) | 让 P0-3 验证的研究流程在四经济体底图上更大范围长期跑: 常态运行监测与异常→研究任务衔接的运行面 | 链路健康常态监测(流水线台账+sources_status+新鲜度)、异常检测经济体扩展、异常→RT- 任务 append-only 衔接、监测回溯查询;零新数据通道;不含按需比较视图(=#19 前件,互斥) | #19 前件+第一层 P0-3 落地链+A..E+GAP08 在场交付件(锚见 §八.2);零新数据源;LIVE 部署=用户保留卡点③(PENDING) | ① 监测面=台账/快照/事实层消费,零直读采集档【测试】② 断点/缺席如实列示(与 Gate A 语义一致,不填0)【测试】③ 异常→任务走 append-only+既有 schema(研究状态保护不绕开)【测试】④ 既有 offline-tests 全套件零回归【CI】⑤ LIVE 部署与通知面=确认型 DP·PENDING·确认权留用户【PENDING】 |

**锚 2 = §八.2 规格节 L225-L256(节名行 L225;四要素+DP 节)**:

**目标**(L227,逐字):

> 让 P0-3 验证的研究流程(注入摘要,2026-11-06,非工作树实读: E2E-A 历史查询/异常检测/研究任务结构与档案、E2E-B 自然语言入口、GLM 竞争性假设、报告生成+档案)在四经济体底图上「更大范围长期跑」(§4a L138 注入行)——设计常态监测运行面: 每日链路健康监测、四经济体异常检测扩展、异常→研究任务→档案的常态化衔接。**纯运行面设计**: 不重做底图、零新数据通道、不绕开快照与研究状态保护机制。

**范围**(L229-L235,逐字,6 款):

> 1. **链路健康常态监测面**: 既有 13 步流水线(run_weekly.py steps L126-L157 [实取·2026-11-06 工作树实读;R015 时点 11 步已被 WP-A v1.3 扩为 13 步,以工作树实读为准])台账(`logs/pipeline_run_YYYYMMDD.json`,run_weekly.py L12/L217-L238)与快照 sources_status/Gate A(snapshot_builder.py L382-L385)之上的常态健康视图(逐通道断点/MISSING 回溯、新鲜度越限列示——月频窗 60 天沿既有口径 [实取·config/metric_registry.json CPI 条目 freshness.max_calendar_lag_days=60,2026-11-06 json.load 复核];回溯窗=N 日=登记型 DP-G1);
> 2. **异常检测经济体扩展面**: 既有 detect_divergence(anomaly_detector.py L60,阈值登记 L29-L32 [实取: CORR_THRESHOLD=0.30/RATE_BP_THRESHOLD=25.0/GOLD_PCT_THRESHOLD=2.0])为 US 单一对(利率×黄金);扩展形态=登记型 DP-G2(泛化/新规则/regime 变化候选三选);
> 3. **异常→研究任务衔接面**: research_task_manager(build_task L79/SCHEMA_MIN_FIELDS L36-L37/falsifiable_conditions L139/append-only 落档 L165-L189)与 RT- economy 字段(_task_economy L64)的常态化衔接;**研究状态保护=append-only+状态机+门禁**(论点状态修改=report_generator.py update_thesis_status L985;流水线级放行语义=台账 allow_state_writeback,run_weekly.py L211-L216),设计禁绕开;
> 4. **监测回溯查询面**: research_history_query economy 过滤(L184-L201)作为监测回溯消费面;
> 5. **互斥划界**: 不含按需横向比较视图(=#19 前件,层内收口链序: #19 先落地);#21 终验/封版/用户确认面不进本包(衔接注记: 终验/封版面由 #21 承载);
> 6. **部署边界**: 「长期跑」运行宿主(LIVE launchd/定时面)=用户保留卡点(注入摘要 L166: 用户三个保留卡点③LIVE 部署)——本包只设计监测逻辑与离线可验面,任何 LIVE 部署=确认型 DP-G4·PENDING。

**依赖**(L237-L240,逐字;L237 节名行含层序前置声明):

> **依赖**(#19 前件+层序前置声明: 第一层已关闭+A..E+GAP08 在场;能力面清单见 REPORT §四):
> - 第一层 P0-3 落地链: anomaly_detector.py L29-L32/L60;research_task_manager.py L36-L37/L64/L79/L139/L165-L189;research_history_query.py L77/L100/L184;research_archive.py validate_id_conventions L67(QB-/RT-)/validate_query_record L191;report_generator.py generate_report L377/verify_research_inputs L612/update_thesis_status L985;data_validator.py validate_report L755(Gate B)/forbidden_phrases_in L238;
> - 底图: run_weekly.py L126-L157(13 步)/L211-L216(放行标志)/L217-L238(台账);snapshot_builder.py L47/L266/L335-L350/L382-L385;config/metric_registry.json v2.3.0/102 条目(freshness 字段);
> - #19(前件): 比较视图先落地,监测面消费其视图与底图。

**验收要点**(L242-L249,逐字,七条①-⑦):

> ① 监测视图=台账+快照+事实层消费,零直读采集档、零新数据通道【测试】
> ② 断点/缺席如实列示: 任一通道连续 MISSING/新鲜度越限→如实呈现(禁0填充禁静默),语义与 Gate A DEGRADED/MISSING 一致【测试】
> ③ 异常→研究任务衔接走 append-only+既有 schema(SCHEMA_MIN_FIELDS 可增不可减,falsifiable_conditions 语义不变);研究状态修改仅经既有状态机/门禁面【测试】
> ④ 既有 offline-tests 全套件零回归(套件数以 #20 实现包合同 BASE 实取值为准,不预植固定数)【CI】
> ⑤ 实现参数(回溯窗/新鲜度口径/异常规则族)先登记后运行、禁回改(登记型 DP 纪律承接,见 DP 节)【纪律】
> ⑥ LIVE 部署与通知面=确认型 DP·PENDING·确认权留用户(用户保留卡点③);本包交付零 LIVE 写入【PENDING】
> ⑦ 涉真实 GLM 调用面(若监测衔接报告生成)=PENDING·用户实批前置;离线测试全 mock【PENDING】

**DP 节**(L251-L256,逐字):

> **DP 节**(决策点/选项≥2/推荐/影响+分类;登记型提案值均为 [示意·非实取],终值由 #20 实现包合同登记定):
> - **DP-G1(登记型)常态健康回溯窗**: ①7 日 ②14 日 ③30 日。推荐② [示意·非实取];影响=监测视图数据面与要点②断言构造窗。
> - **DP-G2(登记型)异常检测经济体扩展形态**: ①detect_divergence 规则族参数化 economy 泛化 ②新增经济体专用规则模块 ③复用评分卡 regime 变化作异常候选。推荐①——复用既有阈值登记结构+registry economy 维度,零新机制;影响=检测面与任务生成量。
> - **DP-G3(登记型)新鲜度监测口径**: ①registry freshness 逐条监测 ②分层口径(月频 60 天窗沿既有 [实取·见范围1]+日频通道 MISSING 回溯) ③仅核心指标。推荐②;影响=要点②越限断言面与误报率。
> - **DP-G4(确认型)常态监测运行宿主与部署面**: ①LIVE launchd 定时任务 ②手动触发 ③DEV 侧演练先行。**确认权留用户,PENDING**——LIVE 部署=用户保留卡点③(注入摘要 L166);影响=#20 实现包交付面范围(部署面不进离线可验 AC)。
> - **DP-G5(确认型)监测结果通知形态**: ①零通知(仅台账与视图) ②终端摘要 ③外部通知(推送/邮件类)。推荐①(零凭证零外部依赖) [示意·非实取];**确认权留用户,PENDING**——通知面涉用户个人流程(选项③另涉凭证=PENDING 报批);影响=#20 实现包通知面有无。

### §零.3 交付文件清单(白名单登记;登记后即本合同白名单实体)

范围列=模块级(§八.2 范围四面各为一模块面;范围5/6=边界条款非交付面),按固定推导规则生成(每个代码模块=`scripts/` 下恰 1 文件;含代码必含 `tests/test_p1_wp_g.py`;必含 REPORT/DELIVERY 双档),DP-G2 终值=② 裁定范围2 为独立规则模块(冻结章§四),其余三面同构推导:

| # | 路径 | 类 | DESIGN 依据 |
|---|---|---|---|
| 1 | scripts/routine_health_monitor.py | A(新增) | §八.2 范围1 L230(链路健康常态监测面: 台账+sources_status/_gate_a+新鲜度视图) |
| 2 | scripts/economy_anomaly_rules.py | A(新增) | §八.2 范围2 L231(异常检测经济体扩展面)+DP-G2 终值=②新增经济体专用规则模块(冻结章§四裁定) |
| 3 | scripts/monitor_task_bridge.py | A(新增) | §八.2 范围3 L232(异常→研究任务衔接面: RT- append-only+既有 schema+状态保护不绕开) |
| 4 | scripts/monitor_history_view.py | A(新增) | §八.2 范围4 L233(监测回溯查询面: economy 过滤消费)+依赖 L240(#19 前件视图消费) |
| 5 | tests/test_p1_wp_g.py | A(新增) | 结构约束(iii): 含 .py 实现文件必含对应 tests |
| 6 | docs/P1_WP_G_REPORT.md | A(新增) | 必含件(结构约束 iii) |
| 7 | docs/P1_WP_G_DELIVERY.md | A(新增) | 必含件(结构约束 iii) |

- A 类=7 文件(k=7);M=0;D=0(冻结章§五 M 面裁定维持);`git ls-files` 对照零重合(开工实取,7 路径全部不在版本库);必含件齐(REPORT/DELIVERY/tests 三必含件在场);推导零越界(7 路径逐一映射范围 1-4+结构约束,无 DESIGN 依据外文件)。
- 运行产物边界: 验收要点①-⑦ 无真实运行面(①②③=离线测试,④=CI,⑤=纪律,⑥⑦=PENDING 登记——对照依据见 §三),本包登记「零运行产物」;CLI 编排入口以合成 fixture 冒烟于测试内(临时目录,零真实 data/daily 读取)。

### §零.4 P1 特有纪律登记(实读锚定;逐条登记节号并遵守)

实读规格锚(§六 L175+§八.2 L225-L256)及其所引节(§六 L177 红线筛查、§七 L179-L184 红线、§八 头 L190 红线承接语)所载特有纪律:

1. **快照+门禁不可绕开**(§七 L181;§六 L177;§八.2 目标 L227「不绕开快照」): 监测面数据入口=流水线台账(logs/pipeline_run_*.json)+研究快照(rp.select_snapshot 确定性版本选择)+registry 配置只读;零直读 `data/daily/` 采集档(jp_/ea_/global_/macro_/china_/rate_economy_/japan_ 档族禁开);
2. **LIVE 禁写**(§七 L182;§八.2 范围6 L235;要点⑥ L248): 全部工作在 DEV 仓库 dev/* 分支;LIVE 目录/launchd 零触碰;LIVE 部署/通知/常驻进程=用户保留卡点③ PENDING(本包不实施不预设,DP-G4/G5 未自决);
3. **禁交易/仓位/收益承诺**(§七 L183): 监测输出=链路健康/数据新鲜度/统计背离描述,非投资建议;规则预期符号=登记的机械模型假设非事实;
4. **数据不足不填0**(§七 L184 五层一致;要点② L244): 断点/缺席/MISSING/新鲜度越限/序列缺席一律如实列示,禁 0 填充禁静默;语义与 Gate A DEGRADED/MISSING 一致(消费其裁决不改判);
5. **研究状态保护不绕开**(§八.2 范围3 L232): 论点状态修改=report_generator.update_thesis_status L985 既有面,本包零调用;流水线放行=台账 allow_state_writeback(run_weekly L211-L216)既有语义,本包只读消费;RT- 任务=append-only 落档经 rtm.save_task(幂等跳过/新版本追加,原档字节不动)既有机制,禁绕开直改;
6. **零新数据通道/零新数据源**(§六 L175 范围列;§八.2 目标 L227): 监测面纯消费在场面(台账/快照/registry/#19 视图),零采集/零请求/零网络;
7. **真实 GLM 面=PENDING**(要点⑦ L249): 本包任何成员零真实 GLM/LLM 调用(监测不衔接报告生成——衔接面属用户实批 PENDING,本包未实现该面);
8. **W4/W5 侧边验收工具不入链**(§八 头 L190 承接语): 本包四模块与 W4/W5 零接线。

未载明面: 无(上列 8 条=锚内及所引节全部特有纪律载明;判定依据=§六 L177+§七 L179-L184+§八.2 L227/L230-L235/L243-L249+§八 L190 逐节实读)。

### §零.5 DP 登记(开工首步登记定值;先登记后运行,运行后禁回改)

**登记型 DP 定值(逐字转录冻结章§四三值,非自选)**:

| DP | 定值 | 影响(冻结章原文) |
|---|---|---|
| DP-G1 常态健康回溯窗 | **② 14 日** | 监测视图数据面与要点②断言构造窗 |
| DP-G2 异常检测经济体扩展形态 | **② 新增经济体专用规则模块** | 裁定依据(冻结章§四)=选项①须 M 改封版件 anomaly_detector.py 撞 §八.3 红线;②=纯 A 类新增模块,复用既有阈值登记结构与 registry economy 维度,零触碰封版件 |
| DP-G3 新鲜度监测口径 | **② 分层口径**(月频 60 天窗沿既有 registry freshness 口径+日频通道 MISSING 回溯) | 要点②越限断言面与误报率 |

**确认型 DP(未触及,未自决)**: DP-G4(运行宿主/部署面)=确认型·PENDING·确认权留用户——本包交付零 LIVE 部署/零定时任务/零常驻进程装载(要点⑥ 离线可验面不依赖宿主形态);DP-G5(通知形态)=确认型·PENDING·确认权留用户——本包交付零通知(输出仅 stdout/视图档/RT- 档案)。实现与要点均未触及两 DP 决策需求(部署面/通知面不在交付面),零自决。

**实现参数登记(登记定值即实现值;运行后禁回改)**:

(1) routine_health_monitor.py:
- `HEALTH_LOOKBACK_DAYS = 14`(DP-G1=②;窗口=[ymd−13, ymd] 含端点 14 自然日);
- 新鲜度分层(DP-G3=②): 层1 非日频 registry 指标(现值域 frequency∈{monthly,weekly},v2.3.0 实取 monthly 23+weekly 1=24 条 [实取·json.load 2026-11-06])逐条对照其 `freshness.max_calendar_lag_days`(逐条目窗,CPI/FED_FUNDS 等月频=60 [实取·registry]);越限判定=`(target_date − observation_date)` 自然日差 **>** 窗(严格大于;等号=未越限);事实缺席→「缺席行」如实列示(非违规行,不填0);
- 层2 日频通道 MISSING 回溯: 通道集=snapshot sources_status 键(现值域=SOURCE_FILE_RULES 7 通道 global/macro/china/rate_economy/japan/jp/ea [实取·research_provenance L176-L183]);streak 语义=自窗口内最近快照日在场日起向回逐日计数 `status=='MISSING'` 的连续快照日数,无快照日=断链(计数如实断开,不脑补);
- 台账消费: `logs/pipeline_run_{ymd}.json`(run_weekly L217-L238 写档形态;缺席=如实 no_ledger 行,不视为成功);

(2) economy_anomaly_rules.py(DP-G2=②;阈值登记结构=anomaly_detector.py L27-L32 同构复用):
- `ROLLING_WINDOW = 60` / `CORR_THRESHOLD = 0.30` / `FX_PCT_THRESHOLD = 2.0` / `EQ_PCT_THRESHOLD = 2.0` / `THRESHOLDS_INCLUSIVE = True`(比较含等号)/ 统计值 rounding rho=4 位,chg pct=4 位(与 anomaly_detector echo_params stats_rounding 同构);
- 规则族(registry v2.3.0 实取 economy 字段推导;序列面=快照 series_store 在场性实取[global/china/jp/ea 池,snapshot_builder L427-L469 实读]):

| 规则 ID | 经济体 | 驱动序列(fx) | 响应序列(eq) | 登记机械预期符号 s | 依据 |
|---|---|---|---|---|---|
| RD-DIV-CN-001 | CN | USDCNY(cny_per_usd) | SHCOMP(index_point) | −1(人民币走弱↔A 股承压,负共动) | 两成员 registry economy=CN 实取;均在 series_store(global/china 池) |
| RD-DIV-JP-001 | JP | USDJPY(jpy_per_usd) | NIKKEI225(index_point) | +1(日元走弱↔出口股利好,正共动) | 两成员 economy=JP;USDJPY 在 global 池,NIKKEI225 在 jp 池(F2 接线) |
| RD-DIV-EA-001 | EA | EURUSD(usd_per_eur) | DAX(index_point) | −1(欧元走强↔出口竞争力受损,负共动) | 两成员 economy=EA;EURUSD 在 global 池,DAX 在 ea 池(F2 接线) |

- 判定式(机械,阈值含等号): `cond_corr = rho is not None and (rho × s) <= −CORR_THRESHOLD`;`cond_move = (chg_fx_pct >= +FX_PCT_THRESHOLD) and (s × chg_eq_pct <= −EQ_PCT_THRESHOLD)`;`triggered = cond_corr or cond_move`;逐期统计=共同观测日升序交集上滚动 W 日差分 pearson(与 anomaly_detector L80-L98 同构);
- 预期符号=登记的机械模型假设(非事实非投资建议;描述统计非因果);
- US 划界(如实): US 对(TIPS_10Y×GOLD_F)=既有封版 RD-DIV-001(anomaly_detector.py,第一层 P0-3 落地链交付件)——本模块不重复实现零触碰;HK/GLOBAL 无登记规则(registry economy 值域内无经典共动对双成员序列在场面,如实缺席不造规则);

(3) monitor_task_bridge.py:
- task_id=rtm.make_task_id(start, end, rule_id, indicators, frozen_params) 既有确定性构造(重放幂等锚复用);economy 键=rtm._task_economy(indicators) 既有条件写(恰单经济体才写;CN/JP/EA 三规则对均单经济体,实读 registry 推导);落档=rtm.save_task 既有 append-only(幂等跳过/异指纹 __v{N} 追加/原档字节不动);schema=rtm.SCHEMA_MIN_FIELDS 十字段可增不可减(构造后校验);falsifiable_conditions 三条(阈值反证/现象消解/解释竞争,与上游 L139-L147 语义同族非空可反驳);任务状态=pending→active(证据装配后,上游 run_e2e L258-L273 同构);**零 update_thesis_status 调用、零既有档改写**(研究状态保护不绕开);
- 编排入口 run_bridge: 快照选择(rp.select_snapshot)→序列提取(series_store)→规则检测(economy_anomaly_rules)→触发→建任务+装配+落档;不触发=如实输出零任务(exit 0,合法结果);快照缺席=如实输出零检测;

(4) monitor_history_view.py:
- 回溯窗=DP-G1=14 日;逐经济体窗口=上游 rhq.query_window(payload, start, end, economy=econ) 直用(过滤不命中=上游如实空窗语义);RT- 任务列示=data/research/ 只读扫描(RT-*.json 含 __v{N},读 economy/status/task_id/created_at;零改写);#19 前件消费=ecv.economy_row(评分卡在场状态,复用不复制);

(5) 共通: MONITOR_DISCLAIMER=`常态监测输出=链路健康/数据新鲜度/统计背离描述,非投资建议;缺值如实缺席不填0;规则预期符号为登记的机械模型假设。`(登记文案,禁投资建议语);零网络 import 面(纯标准库+项目既有模块);AC-03.7 外部调用面=不适用(登记清单零调用面类文件——四模块均无 GLM/LLM 客户端/网络编排/数据源客户端/通知渠道实现,判定依据=§零.3 清单)。

### §零.6 上游在场交付件接入点登记(file:line=开工时点工作树实读)

| 上游件 | 接入点(file:line) | 消费方式 |
|---|---|---|
| research_provenance.py | select_snapshot L1270(确定性版本选择) | 快照唯一入口(先例=ecv.load_snapshot_for_view L68-L74 同式) |
| run_weekly.py(台账) | 台账写档 L217-L238(logs/pipeline_run_{ymd}.json);放行标志 L209-L216 | 只读消费 |
| snapshot_builder.py | build_snapshot L266/sources_status L282-L301(四态 MISSING/EXACT/FALLBACK/READ_FAIL)/Gate A L382-L390/series_store L427-L469 | 只读消费快照档(经 select_snapshot,零 import 构建面) |
| config/metric_registry.json | v2.3.0/102 条目(freshness/economy/frequency 字段) | fe.load_registry()/fe.metric() 只读 |
| fact_engine.py | metric L75 | registry 惰性只读 |
| anomaly_detector.py(封版件) | 常量登记结构 L27-L32/detect_divergence L60 | 结构同构复用(零 import 零改动——DP-G2=② 裁定零触碰) |
| research_task_manager.py | SCHEMA_MIN_FIELDS L36-L38/_task_economy L64/make_task_id L48/save_task L164-L185(append-only) | import 调用(复用不复制) |
| research_history_query.py | query_window L184-L201(economy 过滤)/ECONOMIES L77 | import 调用 |
| economy_comparison_view.py(#19 前件) | economy_row L120/KEY_FACTS L43-L52/COMPARISON_ECONOMIES L42 | import 调用(#19 视图消费,依赖 L240) |
| macro_scorecard.py | DATA_INSUFFICIENT L30/ECONOMY_NAMES L39(经 ecv 间接) | 间接消费 |

### §零.7 规格锚行锚复验与可区分性(步骤 5 判定记录)

- 行锚复验: §六 L175 行名「WP-P1-G(候选名)常态监测(§4a#20)」在场(五列式,与 L169-L173 A..E 五行同构式样,挂靠 #20 显式);§八.2 L225 节名行/L227 目标/L229-L235 范围六款/L237-L240 依赖/L242-L249 验收要点七条/L251-L256 DP 节——与冻结章 SPEC-ANCHOR 登记细锚逐项一致,零漂移;
- 可区分性: §六 L169-L173=A..E 五行(无 #20 挂靠),L174=#19 行(比较视图),L175=#20 行(常态监测)——L174 与 L175 行内互斥划界显式(「不含持续运行监测面(=#20,互斥)」/「不含按需比较视图(=#19 前件,互斥)」);§八.1(L192-L223)=#19 规格与 §八.2(L225-L256)=#20 规格目标/范围/要点三面均不同构(比较视图=并置消费面 vs 常态监测=运行监测+异常→任务衔接)→ 可独立实现的常态监测规格已定位,非同构抄重。

---

## §一 实现落位登记(实现后回填)

(待实现后登记: 四模块结构锚+tests 用例锚)

## §二 逐要点证据映射表(AC-02;实现后回填)

(待实现后登记)

## §三 运行产物判定(对照依据)

验收要点①-⑦ 逐条对照: ①②③=离线测试(合成 fixture);④=CI(操作者 dispatch);⑤=纪律(§零.5 先登记);⑥⑦=PENDING 登记(零实施)——**七条要点均无真实数据运行要求**(无【数据档引用】类标记;对照 WP-A 行含「② 首份 data/daily/jp_/ea_YYYYMMDD.json 真实档在场【数据档引用】」而本包行无此标记)。登记清单含 CLI 编排入口(routine_health_monitor/monitor_task_bridge/monitor_history_view main)但不要求真实运行——本包**零运行产物**(data/research/ 零新增;data/daily/ 零读取零写入;对照依据=本节)。

## §四 数值标注自检清单(§5.3;提交前回填)

(待双文档成文后扫描回填)
