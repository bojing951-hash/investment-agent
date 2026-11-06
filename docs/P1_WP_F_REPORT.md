# IA-P1-WP-F REPORT(跨经济体比较视图 #19)

> 工作包: IA-P1-WP-F(=§4a 第二层收口链第 1 包/#19)。执行 Agent: Agent 3。
> 基线: BASE-P1F=`64ce40c25409bdb0a3d9fecc4c5f0f5df74dd902`(2026-11-06T16:15Z 开工实取 ls-remote=origin/main 全值一致)。
> 分支: `dev/p1-impl-f`(自 BASE-P1F 切出;开工首步=指定并入步 merge `dev/p1-design-comp@7190eb7aae110dcc23cf059b4969cd9978429d4d`,恰 1 个 merge 提交第二父=7190eb7,其后纯线性)。
> 规格源: `docs/P1_DESIGN.md`(并入后 HEAD blob=`10e026c08ce2828908ff7a5421aee8aba1f4e6d0`=dev/p1-design-comp@7190eb7 侧;行号=并入后工作树实读,与 design-comp 侧一致)。
> 边界声明(§5.3 第 5 项): 本文日期/时刻=UTC(git 取证原样);SHA=全值;行号=并入后工作树实读(P1_DESIGN 三件以基线工作树在场版为准)。

---

## §零 规格抄录、交付文件清单(白名单)、特有纪律、DP 与实现参数登记(开工首步,先登记后实现后运行)

### §零.1 开工核验(步骤 0-4 实录)

| 项 | 结果 | 摘要 |
|---|---|---|
| 步骤0 时序 | 过 | git status clean;开工 UTC=2026-11-06T16:15:10Z |
| 步骤1 占位符 | 过 | §0 四占位符全实值(BASE-P1F/BASE-P1F-CI-SUITES=75/BRANCH-SET=48 支/SPEC-ANCHOR=§六 L174+§八.1 L192-L223) |
| 步骤2 前置实取 | 过 | ls-remote: main=`64ce40c…`(=BASE-P1F)/dev/p1-design=`049ec978…`/dev/p1-design-comp=`7190eb7…` 全值一致;禁锚 c9626633 未混入(锚定侧=7190eb7) |
| 步骤3 切分支 | 过 | `dev/p1-impl-f` 自 BASE-P1F 切出(此前本地与远端均不存在);ls-remote 全表 52 行=1 HEAD+48 支分支(与冻结章 BRANCH-SET 逐一 SHA 对照一致)+3 行 tags(非分支);白名单外新支零在场 |
| 步骤4 指定并入步 | 过 | `git merge --no-ff 7190eb7…` 成功零冲突,恰 1 个 merge 提交(第二父=7190eb7),引入恰 3 文件(M docs/P1_DESIGN.md+A docs/P1_DESIGN_COMP_REPORT.md+A docs/P1_DESIGN_COMP_DELIVERY.md=§五.1 豁免行);`git merge-base --is-ancestor 049ec978… HEAD`=exit 0(ANCESTOR_OK);三件 blob 对照: P1_DATA_NEEDS_INVENTORY.md=`df79c06f…`/P1_DELIVERY.md=`314c2644…`(=049ec978 侧)/P1_DESIGN.md=`10e026c0…`(=design-comp 侧,≠049ec978 侧 13b263cf=R064 合法纯追加预期差异);禁锚 c9626633: HEAD 全树 grep 命中仅 6 处全为历史包报告「禁锚未混入」核验措辞(其中 5 文件=BASE-P1F 既有内容 git grep 64ce40c 复证、1 文件=R064 已审 DESIGN_COMP_REPORT),零锚定使用 |

### §零.2 规格抄录(AC-01;逐字抄录自 docs/P1_DESIGN.md 并入后工作树实读)

**锚 1 = §六 L174(包行,五列)**:

> | WP-P1-F 跨经济体比较视图(§4a#19) | 四经济体横向比较消费面: 在场底图之上的并置比较视图,不重做底图 | 比较视图装配(消费 economy_scorecard_* 档与经济体观察节)、比较事实与跨域对呈现、economy 过滤查询比较用例;零新数据源(纯消费面);不含持续运行监测面(=#20,互斥) | A..E+GAP08+第一层 P0-3 落地链在场交付件(锚见 §八.1);零新数据源 | ① 比较视图=快照/事实/评分卡消费面,零直读采集档【测试】② 四经济体并置+缺席如实(DATA_INSUFFICIENT/「无数据」,不填0)【测试】③ 既有 US 面零回归【测试/CI】④ 实现参数先登记后运行、禁回改;真实调用/凭证/付费面=PENDING·用户实批前置【PENDING】 |

**锚 2 = §八.1 规格节 L192-L223(节名行 L192;四要素+DP 节)**:

**目标**(L194,逐字):

> 在 P1 底图层在场交付面之上,提供四经济体(US/CN/JP/EA,INVENTORY a.1 DP-1 默认候选)横向比较消费面——把各经济体评分卡状态、关键事实与跨域相关性并置为单一比较视图,支撑 W-1 型(US×EA 政策分化,§三(d) L88-L100)跨经济体研究问题的例行对照。**纯消费面**: 零新数据源、零新采集通道、不重做底图;数据与研究档案唯一入口=研究快照(§四衔接设计 L141)。

**范围**(L196-L200,逐字,4 条):

> 1. **比较视图装配面**: US 主评分卡(`scorecard_{ymd}.json`)与非 US 档(`economy_scorecard_{econ}_{ymd}.json`,macro_scorecard.py L40/L487-L488)并置;复用数据包「经济体观察」节渲染面(data_assembler.py L277-L301)扩展比较呈现;沿用评分卡 DISCLAIMER 口径(内部模型观点非客观事实,macro_scorecard.py L32-L33),不构成投资建议;
> 2. **比较事实面**: 快照事实+`series_store`(snapshot_builder.py L427-L471)与跨域对(correlation_calculator.py PAIRS L28,含 NIKKEI225×USDJPY L49/DAX×EURUSD L51)的比较型呈现;
> 3. **查询比较面**: economy 过滤维度(research_history_query.py L184-L201/L337)的比较型查询用例(W-1/W-2 型问题);
> 4. **互斥划界**: 不含持续运行监测/告警/台账常态面(=#20);不含 #21 终验/封版面(衔接注记: 终验/封版面由 #21 承载)。

**依赖**(L202-L210,逐字;L202 节名行含层序前置声明):

> **依赖**(层序前置声明: 实现面排程前置=第一层已关闭+WP-P1-A..E(R044-R048)+GAP08(R061)全部在场[BASE-COMP 工作树实读,能力面清单见 REPORT §四];#19 不登记 #20 前件):
> - scripts/macro_scorecard.py: score_growth L99/score_inflation L200(economy 参数)/save_scorecard L414-L417/DATA_INSUFFICIENT L30/ECONOMY_NAMES L39;
> - scripts/data_assembler.py: economy_scorecard L91/「经济体观察」节 L277-L301;
> - scripts/correlation_calculator.py: PAIRS L28/L49/L51,paired_returns L60,compute_all L90;
> - scripts/snapshot_builder.py: build_snapshot L266/jp/ea 接线 L335-L350/series_store L427-L471;
> - scripts/fact_engine.py: normalize_jp L523/normalize_ea L566/build_all L837;
> - config/metric_registry.json: v2.3.0 [实取·json.load,2026-11-06]/102 条目 [实取·同上]/economy 字段(US49/CN18/EA11/JP8/HK4/GLOBAL12 [实取·同上]);
> - scripts/research_history_query.py: ECONOMIES L77/query_window L184/--economy L337;
> - 第一层 P0-3 落地链查询面: e2eb_query_ir.py ECONOMIES L53。

**验收要点**(L212-L217,逐字;L212 节名行注「草案;正式 AC 由 #19 实现包合同冻结」——正式 AC=IA-P1-WP-F-AC-v1.1 冻结版):

> ① 比较视图产物=纯快照/事实/评分卡档消费,零直读 `data/daily/` 采集档(禁直读约束=§四 L130 对 jp_/ea_ 档同样生效)【测试】
> ② 四经济体并置渲染+缺席如实: 任一经济体档缺席→该经济体如实标 DATA_INSUFFICIENT/「无数据」,禁填0、禁跳过整行、禁以离岸代理冒充在岸口径【测试】
> ③ 既有 US 面零回归: `scorecard_{ymd}` 主评分卡输出与既有套件断言零变化(§三(d) W-3 基准路径行为零回归,L118)【测试/CI】
> ④ 实现参数(落位形态/并置指标最小集/配对新增)先登记后运行、禁回改(登记型 DP 纪律承接,见 DP 节)【纪律】
> ⑤ 本包零新数据源/零凭证/零付费;若实现中识别需真实调用/凭证/付费/新数据源→只以 DP/PENDING 登记·用户实批前置,禁直接依赖【PENDING】

**DP 节**(L219-L223,逐字):

> **DP 节**(决策点/选项≥2/推荐/影响+分类;登记型提案值均为 [示意·非实取],终值由 #19 实现包合同登记定):
> - **DP-F1(登记型)比较视图落位形态**: ①数据包新节(装配器扩展) ②独立比较视图模块(消费快照+评分卡档) ③报告模板新章节。推荐②——US 面零回归触面最小;影响=实现包白名单与零回归面。
> - **DP-F2(登记型)并置指标最小集**: ①仅增长/通胀总分+regime ②总分+regime 加关键事实行(政策利率/通胀同比) ③全量指标表。推荐②——比较密度与缺席披露面平衡;影响=视图信息结构与要点②断言面。
> - **DP-F3(登记型)跨经济体配对新增**: ①零新增(仅呈现既有两跨域对 L49/L51) ②增候选对(如 SPX×SHCOMP,序列双在场性由实现包实读核验) ③更广候选集。推荐①——配对扩容属底图面非本包消费面;影响=series_store 消费面与相关性输出。
> - **确认型 DP: 无**——零新数据源/零凭证/零付费/零部署面/零批量状态修改(如实登记;若实现中发现确认型事项,只登记 PENDING,确认权留用户)。

**可区分性判定**(§零(iv) 冲突处置面的反面核验): A..E 行(L169-L173)无 #19 挂靠、无跨经济体比较视图语义;§八.1=R064 新增节(§一-§七 既有行零改动,L190 节首声明);#20 行(L175)互斥划界显式。四要素齐备无缺项,规格可独立实现,非同构错行。

### §零.3 交付文件清单(登记制白名单;登记后即本合同白名单实体)

范围列为模块级(装配面/事实面/查询面)非文件级 → 按附录A §零(ii) 固定推导规则生成。**A 类纯新增 k=4 文件**:

| # | 路径 | 类 | 推导依据(DESIGN 行/节) |
|---|---|---|---|
| 1 | `scripts/economy_comparison_view.py` | A | 固定规则「每个代码模块=scripts/ 下恰 1 文件」×比较视图模块 1 个(DP-F1 ②定值=独立比较视图模块,承载范围 1 装配面[L197]+范围 2 事实面[L198]) |
| 2 | `tests/test_p1_wp_f.py` | A | 附录A §零(ii) 必含件(含代码则必含);覆盖验收要点①②③【测试】(L213-L215)+范围 3 查询比较面用例(L199) |
| 3 | `docs/P1_WP_F_REPORT.md` | A | 附录A §零(ii) 必含件(本文) |
| 4 | `docs/P1_WP_F_DELIVERY.md` | A | 附录A §零(ii) 必含件 |

结构约束核验: 上 4 路径与 `git ls-files` 输出零重合(纯新增;开工实测 4 路径均不存在,见 §一 落位登记);M 类授权=0(v1.1 冻结 M=0 维持;开工实读 §八.1 范围=纯消费面,新文件可实现,未触发 (d) 停止);清单外一切路径零变更。运行产物(如有)落 `data/research/` 不 commit——本轮验收要点①②③④⑤均无真实运行面(【测试】【纪律】【PENDING】标记,零【真实运行】标记)→ 登记「零运行产物」(对照依据见 §五 映射表)。

### §零.4 P1 特有纪律登记(实读锚定;§八 L190 红线承接声明=§六 L177 红线筛查+§七 L179-L184 四红线对 #19 全量适用)

| # | 纪律(节号锚) | 本包承接 |
|---|---|---|
| 1 | §六 L177+§七 L181: 快照+门禁不可绕开——四经济体一切新数据经 `build_snapshot` 进入研究面,研究引擎/查询/报告零直读采集档(§四 L130: jp_/ea_ 档同禁直读) | 比较视图数据入口=研究快照(rp.select_snapshot)+评分卡存档(data_assembler.economy_scorecard),零直读采集档(要点①,毒丸负向测试证) |
| 2 | §七 L182: LIVE 禁写+launchd 零触碰 | 全部工作在 DEV 仓库 dev/* 分支;LIVE 目录/launchd 零接触 |
| 3 | §七 L183: 禁交易/仓位/收益承诺 | 视图文案沿 DISCLAIMER 口径(§八.1 L197),不构成投资建议 |
| 4 | §七 L184: 数据不足不填0(五层一致) | 缺席语义=DATA_INSUFFICIENT(macro_scorecard L30)/「数据不足」(data_assembler L295-L296 式样)/「无数据」,禁 0 占位禁跳行(要点②) |
| 5 | §八.1 L197: DISCLAIMER 口径沿用(macro_scorecard.py L32-L33) | 逐字 import 复用上游常量,零改写 |
| 6 | §八.1 L200: 互斥划界(不含 #20 监测面/#21 封版面) | 模块零监测/告警/台账/LIVE 部署面 |
| 7 | §八 L190: W4/W5 侧边验收工具不入链 | 本包零 W4/W5 引用 |

其余特有面判定: 规格锚及其所引节(L88-L100/L118/L130/L133/L141/§六 L177/§七/§八)未载明本包特有的数据口径变更/快照路径变更/研究状态写入面——比较视图=只读消费面,不触研究状态档(论点/观点/预测 append-only 保护面零触及,AC-07.5 不适用判定见 §五)。

### §零.5 DP 登记(定值=实现值;先登记后运行,运行后禁回改)

| DP | 分类 | 登记定值 | 依据 |
|---|---|---|---|
| DP-F1 比较视图落位形态 | 登记型 | **形态② 独立比较视图模块(消费快照+评分卡档)**——`scripts/economy_comparison_view.py` 单模块,不改数据包/报告模板 | DESIGN L220 推荐②(US 面零回归触面最小) |
| DP-F2 并置指标最小集 | 登记型 | **形态② 总分+regime 加关键事实行(政策利率/通胀同比)**——并置列=增长总分/通胀总分/制度(regime)/数据状态+关键事实行(政策利率、通胀同比) | DESIGN L221 推荐②(比较密度与缺席披露面平衡) |
| DP-F3 跨经济体配对新增 | 登记型 | **形态① 零新增**——仅呈现既有两跨域对(NIKKEI225×USDJPY / DAX×EURUSD),经 correlation_calculator.compute_all 复用计算,零 PAIRS 扩容 | DESIGN L222 推荐①(配对扩容属底图面非本包消费面) |

确认型 DP: §八.1 L223 载明「确认型 DP: 无」——实读一致(零新数据源/零凭证/零付费/零部署面/零批量状态修改);实现中未发现确认型事项,零 PENDING 触发。

### §零.6 实现参数登记(一切对齐/映射/阈值/窗口/比较口径类;先登记后运行,运行后禁回改)

| 参数 | 登记值 | 实读来源 |
|---|---|---|
| P1 比较经济体集 | `('US','CN','JP','EA')` | DESIGN L194 四经济体(US/CN/JP/EA,INVENTORY a.1 DP-1 默认候选);macro_scorecard.ECONOMY_NAMES L39 同集 |
| 关键事实·政策利率 metric_id 映射 | US=`DFEDTARL` / CN=`CN_LPR_1Y` / JP=`JP_POLICY_RATE` / EA=`ECB_DFR`(均 percent,取 fact.value) | config/metric_registry.json 实取[json.load,2026-11-06T16:2xZ; registry v2.3.0/102 条目同刻复取一致];US 侧 DFEDTARL=既有政策利率锚先例(docs/P0_2_W2_FIX2_POLICY_DFEDTARL.md);EA 取 DFR(存款便利利率=当前 ECB 政策利率锚)而非 MRO,与 INVENTORY a.1「欧央行政策利率」口径相容 |
| 关键事实·通胀同比 metric_id 映射 | US=`CPI`(index_point_1982_84 → 取 fact.derived.m12.pct_change 为同比) / CN=`CN_CPI_YOY` / JP=`JP_CPI_TOKYO_YOY` / EA=`EA_HICP_YOY`(均 percent,取 fact.value) | 同上 registry 实取;US CPI=指数级注册,同比=引擎派生口径(macro_scorecard._derived 同式: derived.m12.pct_change) |
| 跨域对呈现集 | `(('NIKKEI225','USDJPY'), ('DAX','EURUSD'))` | correlation_calculator.PAIRS L49/L51 实读(DP-F3① 仅此两对,按 a/b 二元组精确匹配) |
| 比较行·缺席语义 | 评分卡档缺失→「未生成(当日评分卡不存在)」行在场(禁跳行);growth_total/inflation_total 非 int→「数据不足」;关键事实缺席→「无数据」;快照缺席→事实/跨域节整体「无数据」;一律禁 0 占位 | data_assembler L291-L296 式样实读;macro_scorecard DATA_INSUFFICIENT L30 |
| 数据根约定 | `data_root` 默认=仓库 `data/`(含 `daily/` 子目录);快照选择=rp.select_snapshot(ymd, data_root/daily);评分卡=data_assembler.economy_scorecard(econ, ymd, data_root) | 两上游函数签名实读(macro_scorecard.load_snapshot L46-L57/data_assembler.economy_scorecard L91-L102) |
| 快照缺席行为 | 不沿用 macro_scorecard.load_snapshot 的 sys.exit(1) 中断行为——消费面对缺席如实呈现(None→「无数据」节),直接复用 rp.select_snapshot 返回 (None, reason) 分支 | rp.select_snapshot L1270-L1321 实读;比较视图=消费面非评分主流程 |
| 查询比较面 | comparison_query(payloads, start, end, lookback=0, economies=None)→逐经济体调 research_history_query.query_window(payload,…,economy=econ)并置;过滤不命中=上游如实空窗语义(L194-L201)零新逻辑 | research_history_query.query_window L184-L213 实读 |
| 输出面 | build_comparison_view(ymd,data_dir=None)→dict(结构化行+跨域对+缺席披露);render_comparison_markdown→str;CLI(--ymd/--data-dir/--out)默认落 data/research/comparison_view_{ymd}.md(本轮零真实运行→零运行产物,§零.3) | 运行产物边界(附录A §零) |
| 视图开档面(白名单三族) | 仅 `scorecard_*.json` / `economy_scorecard_*.json` / `research_snapshot_*.json` 三族开档(经上游 helper);零采集档 glob | 要点①;§四 L130 |
| 网络面 | import 面纯标准库+项目既有模块,零 requests/urllib/socket,零新第三方依赖 | AC-03.1/AC-05.4 |

上游在场交付件接口锚(依赖列 L203-L210 逐条开工实读核验一致): macro_scorecard.py L30/L32-L33/L39/L40/L99/L200/L414-L417/L487-L488 ✓;data_assembler.py L91-L102/L277-L301 ✓;correlation_calculator.py L28/L49/L51/L60/L90 ✓;snapshot_builder.py L266/L335-L350/GAP08-F2 注释区 L450-L469/series_store L427-L471 ✓;fact_engine.py(依赖列锚 L523/L566/L837——本包经 correlation_calculator/research_history_query 间接消费,不直接调用 normalize_*)✓;config/metric_registry.json v2.3.0/102 条目/economy 字段(US49/CN18/EA11/JP8/HK4/GLOBAL12)✓;research_history_query.py L77/L141/L167/L184-L201/L337 ✓;e2eb_query_ir.py L53 ECONOMIES ✓(经 research_history_query.ECONOMIES L75-L77 注释引为先例,本包不直接调用)。上游交付件引用同源=各包工作树在场 REPORT §零 登记清单(tests/test_p1_wp_a..e.py、test_p1_gap08.py 等在场即证,本包零修改)。

---

## §一 落位登记(行号=dev/p1-impl-f 工作树实读,实现笔 f4769cf 版)

**scripts/economy_comparison_view.py**(278 行[实取·wc -l]):
- 登记参数区: COMPARISON_ECONOMIES L42 / KEY_FACTS L43-L52(八映射) / CROSS_DOMAIN_PAIRS L53(恰两元组)——与 §零.5/§零.6 登记值逐字一致(断言面=tests L280-L294);
- 缺席语义常量: NO_DATA/INSUFFICIENT_CELL/NOT_GENERATED/_REGIME_STATUS_NAMES L56-L62(上游式样锚: data_assembler L286-L296);
- 接口复用面(零复制分叉,全部 import 调用,import 区 L24-L37: 标准库 L24-L28+项目模块 L33-L37): rp.select_snapshot(L68-L75 消费面版,缺席不中断)+data_assembler.economy_scorecard(L124)+correlation_calculator.PAIRS/compute_all(L145-L153)+macro_scorecard DATA_INSUFFICIENT/DISCLAIMER/ECONOMY_NAMES/fact_of(L36)+research_history_query.query_window(L37);
- 结构: key_fact L87-L118 / economy_row L120-L143 / cross_domain_pairs_view L145-L154 / comparison_query L156-L171 / build_comparison_view L173-L197 / _kf_cell L200-L208 / render_comparison_markdown L210-L256 / main L258-L277。

**tests/test_p1_wp_f.py**(399 行[实取·wc -l],19 用例[实取·unittest「Ran 19 tests」]):
- fixture 工厂(唯一数据源,全[示意]合成): _us_scorecard L43 / _nonus_scorecard L48 / _snapshot_facts L55 / _series_store L70(收益率手工构造±1 联动) / make_fixture L86-L110 / 毒丸 POISON L36;
- 用例类: TestAcceptance1ZeroDirectRead L121 / TestAcceptance2SideBySideHonestAbsence L162 / TestAcceptance3USFaceZeroRegression L247 / TestCrossDomainPairs L278 / TestComparisonQuery L354。

## §二 逐要点证据映射表(AC-02;要点条数=映射行数,逐条编号对应)

**验收要点(§八.1 L212-L217)五条**:

| # | 要点 | (a) 实现落点 | (b) 证据指针 | (c) 自检 |
|---|---|---|---|---|
| ① | 纯快照/事实/评分卡档消费,零直读采集档 | ecv L173-L197(开档仅经 L68-L75 select_snapshot+L124 economy_scorecard 两入口,零采集档 glob) | tests L123-L135(采集档在场/缺席双变体视图逐字节等值)+L138-L148(毒丸标记零泄漏)+L150-L159(源码静态扫描);负向敏感度: 缺陷注入①直读采集档→2 用例红(证据包④负向记录) | 过 |
| ② | 四经济体并置+缺席如实(不填0/不跳行/不冒充) | ecv L87-L142(key_fact/economy_row 五态缺席语义)+L200-L208(_kf_cell 无数据+原因) | tests L175-L178(四行恒在场行序锚)+L180-L186(US int 总分)+L188-L197(非 US None→数据不足)+L199-L205(EA 未生成行在场)+L207-L218(关键事实接地字面量)+L220-L236(缺席变体 available=False/value=None+禁 0.00%)+L238-L245(DISCLAIMER);负向敏感度: 缺陷注入②缺席填 0→1 用例红 | 过 |
| ③ | 既有 US 面零回归 | ecv 纯读面(零写入路径;M=0 零触碰既有文件) | tests L249-L261(daily/ 全目录 sha256 前后等值+零新档)+L263-L276(US 主评分卡字节不变);套件级=本地 CI 76 套件全绿零回归(证据包④)+CI dispatch=操作者面 | 过(CI dispatch 面留操作者) |
| ④ | 实现参数先登记后运行、禁回改 | 登记=本文 §零.5/§零.6(规格笔 829e13a,先于实现笔 f4769cf);常量=ecv L42-L53;运行面=测试断言 | tests L280-L294(test_registered_parameters_frozen: 登记=常量逐字断言);负向敏感度: 缺陷注入③第三对→该用例红(初注入数据面未红缺口→补常量面断言闭合,如实登记);git log 提交序=登记先于实现 | 过 |
| ⑤ | 零新数据源/凭证/付费;识别即 PENDING | ecv import 面 L24-L37 纯标准库+项目既有模块(零 requests/urllib/socket/http/subprocess) | tests L150-L159(静态扫描);实现期零确认型事项发现→§零.5「确认型=无」维持;零 PENDING 触发 | 过 |

**范围四条(L197-L200)+目标(L194)映射**:

| 面向 | (a) 实现落点 | (b) 证据指针 | (c) 自检 |
|---|---|---|---|
| 目标: 四经济体比较消费面/W-1 例行对照 | ecv L173-L197(单一比较视图装配) | tests L175-L178 四经济体并置+CLI 冒烟(证据包⑥面 stdout exit=0) | 过 |
| 范围1 装配面: US 主卡与非 US 档并置+经济体观察式样+DISCLAIMER 沿用 | ecv L120-L143(经上游 helper 读两命名族)+L210-L232(表式样沿 data_assembler L277-L301)+L60-L64(DISCLAIMER import 逐字) | tests L180-L205+L238-L245 | 过 |
| 范围2 事实面: 快照事实+series_store+跨域对比较呈现 | ecv L87-L118(facts)+L145-L154(跨域对经 compute_all 复用) | tests L296-L319(恰两对+corr±1 手算+n/窗口字面量)+L321-L331(序列缺席如实)+L333-L352(快照缺席整体无数据) | 过 |
| 范围3 查询比较面: economy 过滤比较用例(W-1/W-2) | ecv L156-L171(comparison_query 逐经济体调上游 query_window) | tests L368-L378(命中窗口手算字面量)+L380-L390(不命中=上游如实空窗)+L392-L396(payload 缺席无数据) | 过 |
| 范围4 互斥划界: 不含 #20/#21 面 | ecv 全模块零监测/告警/台账/部署面(源码直读可证) | tests L150-L159 静态扫描佐证;grep 零 cron/alert/monitor 面 | 过 |

**DP 判据⑥(§二.6)自检**: 登记型 DP-F1/F2/F3 全部于 REPORT §零.5 登记定值且运行后零回改(登记 829e13a→实现 f4769cf→运行,git 提交序可证;§零.5/§零.6 文本运行后零改动);确认型 DP 未被自决(§八.1 L223「确认型 DP: 无」实读一致,实现期零触及);DP 登记=P1_DESIGN 实读编号/分类一致(F1/F2/F3 登记型,L220-L222)。

**AC-03.7 判定**: 登记清单含 `.py` 实现文件→AC-03 全部生效(含 6/7 项);清单**不含外部服务调用面实现**(GLM/LLM 客户端/网络编排/数据源客户端类零在场——ecv import 面 L24-L37 直读即证)→第 7 项「不适用」+判定依据=清单与源码 import 面均无调用面类文件。

## §三 真实运行面判定(步骤 10 对照)

**零运行产物**: 验收要点①②③④⑤标记面=【测试】×2+【测试/CI】×1+【纪律】×1+【PENDING】×1(§八.1 L213-L217 逐字),零【真实运行】标记;登记清单编排入口(main CLI)存在但合同/要点未要求真实运行→本轮零真实运行、零 `data/research/` 产物、`data/daily/` 与既有快照零触碰(测试全在 tempfile 临时目录,CLI 冒烟输出 /tmp)。对照依据=本表+§二 逐要点(c)列。

## §四 数值标注扫描清单(§5.3 六项自检;成件入证据包⑤)

| 数值 | 标注 |
|---|---|
| 白名单 A 类 k=4 文件 | [实取·§零.3 登记+git ls-files 零重合核验 2026-11-06T16:2xZ] |
| 测试用例 19 | [实取·unittest stdout「Ran 19 tests」2026-11-06T16:3xZ] |
| 本地 CI 76 套件=75 exit0+1 SKIPPED | [实取·/tmp/p1-wp-f-evidence/local_ci_records.txt 76 行] |
| BASE-P1F-CI-SUITES=75(对照基数) | [注入·冻结章实值,2026-11-07 00:1x HKT 主 CI 42211060088@64ce40c] |
| registry v2.3.0/102 条目/US49+CN18+EA11+JP8+HK4+GLOBAL12 | [实取·json.load 同刻复取一致 2026-11-06T16:2xZ] |
| KEY_FACTS 八映射(4 经济体×2 指标) | [实取·registry 逐 id 在场核验] |
| 跨域对 2 元组 | [实取·correlation_calculator.PAIRS L49/L51] |
| 经济体集 4(US/CN/JP/EA) | [实取·DESIGN L194+INVENTORY a.1 L19-L22+macro_scorecard L39] |
| ecv 278 行/tests 399 行/REPORT 行数 | [实取·wc -l,REPORT 行数随终稿以 zip 内副本为准] |
| 分支提交: 指定并入步 1 merge+开发笔(规格笔 829e13a/实现笔 f4769cf/报告笔/终笔=4 开发笔) | [实取·git log dev/p1-impl-f] |
| BRANCH-SET 48 支(52 行=1 HEAD+48 支+3 tags) | [实取·ls-remote 00-lsremote-full.txt] |
| 毒丸标记/合成值(POISON_XR71_MARKER/YMD 20990101/序列值/评分卡值) | [示意·tests fixture 发明,非真实数据] |

边界声明(第 5 项): 本文日期时刻=UTC;SHA=全值;P1_DESIGN 行号=并入后工作树实读(=design-comp 侧一致)。第 3 项全表复核完毕,零失实项;第 4 项无触发。
