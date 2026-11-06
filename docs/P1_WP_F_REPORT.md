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

## §一 落位登记(实现后回填)
(占位;见 §五 映射表——本节由实现笔后补行号锚)

## §二 逐要点证据映射表(AC-02)
(占位;实现+测试后回填)

## §三 DP 自检
(占位;见 §五 映射表 DP 判据⑥行)

## §四 数值标注扫描清单(§5.3)
(占位;提交前自检后回填)
