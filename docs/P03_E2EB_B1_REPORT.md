# IA-P03-E2EB-WP-B1 REPORT — NL→查询映射层(IR schema+映射器v1+缺席路径)

> 包: IA-P03-E2EB-WP-B1(E2E-B 首个实现包) · 执行Agent: Agent 3
> 分支: `dev/p03-e2eb-b1`(自基线 a6d086b8b184067d530815e0bf8963d959275743 切出)
> 设计并入: `f1fe593faa0f1754e6a6ab14c39f39fc0848550a`(--no-ff,merge-base=1ddfb65ec78f4358b7a004be8ef5d8916ba0f052,结构性零冲突实测通过)
> 合同: IA-P03-E2EB-WP-B1-AC-v1.0(冻结,占位符已实值化)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY 行号一律为**并入后工作树实读**行号(2026-11-04T19:0xZ 实取)。

---

## §零 规格抄录与交付面登记(开工首步,AC-01)

### (i) DESIGN §六 WP-B1 行四要素逐字抄录

实读 `docs/P03_E2EB_DESIGN.md`(并入后工作树),WP-B1 行位于 L210-214,逐字抄录如下:

```text
L210: **WP-B1 NL→查询映射层(IR schema+映射器v1+缺席路径)**
L211: - 目标: 落地§三(a)IR schema与v1映射器(约束式映射: 词表+注册表检索),产出可执行IR;缺席四级与unresolved_entities如实上浮。
L212: - 范围: 新增IR定义模块+映射器;不含执行器与渲染。
L213: - 依赖: 无(注册表只读接口E2既有)。
L214: - 验收要点草案: ①离线单测: IR字段级schema校验用例(工件: tests/test_p03_b1*.py,CI offline-tests套件) ②§三(d)问题文本→IR映射黄金用例,含MB-8/MB-9 ABSENT_REGISTRY断言(工件: 测试文件+CI run) ③unresolved_entities负向用例(禁交易类问题→out_of_scope,工件: 测试文件) ④模块SHA登记(工件: commit SHA)。
```

四要素齐备(目标/范围/依赖/验收要点),无缺失;依赖列「无(注册表只读接口E2既有)」与基线事实一致(fact_engine E2 于基线在场,scripts/fact_engine.py:75-76 实读);范围不含 GLM/网络/新数据源凭证要求 → 无情形(d)停止条件。

### (ii) 交付文件清单(k=5,登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据 |
|---|---|---|
| 1 | `scripts/e2eb_query_ir.py` | DESIGN L212「新增IR定义模块」+L211「落地§三(a)IR schema」;合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」第 1 模块 |
| 2 | `scripts/e2eb_query_mapper.py` | DESIGN L211「v1映射器(约束式映射: 词表+注册表检索)」+L212「映射器」;同上第 2 模块 |
| 3 | `tests/test_p03_e2eb_b1.py` | DESIGN L214①②③工件「tests/test_p03_b1*.py」(**草案glob**)+合同附录A §零(ii)「含代码则必含 tests/test_p03_e2eb_b1.py」(冻结合同实值文件名)。**差异如实登记**: `test_p03_e2eb_b1.py` 不字面匹配草案glob `test_p03_b1*.py`;DESIGN §六标题自注「验收要点=草案,正式AC由主Agent后续轮拟定」(L206)→以冻结合同附录A §零(ii)指定名为准,非静默绕过 |
| 4 | `docs/P03_E2EB_B1_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 5 | `docs/P03_E2EB_B1_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L214④「模块SHA登记」落点=本 REPORT §五 |

### (iii) 结构约束核验

- 与 `git ls-files` 输出零重合: 5 路径均为纯新增(开工时实读 `git ls-files scripts/ tests/ docs/` 无一存在)✓
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p03_e2eb_b1.py)✓
- 推导无越界: 范围列「新增IR定义模块+映射器」恰 2 个代码模块 → scripts/ 恰 2 文件;未引入 DESIGN 依据外文件 ✓

### (iv) 运行产物边界登记

WP-B1 验收要点(L214①-④)工件全部为离线测试/文档/commit 登记类,**无真实运行面**(映射器只产IR不取数,DESIGN L109/L212 实读)→ 本包登记「**零运行产物**」;data/daily 与既有档案零读取零写入(测试全合成 fixture,见 §六 D-B1-11)。

---

## §一 前置实读登记(file:line)

(实现前实读,全部工作树实取,非注入摘要)

| 对象 | 登记 |
|---|---|
| DESIGN §三(a) IR schema | docs/P03_E2EB_DESIGN.md:53-107(五结构字段级定义) |
| DESIGN §三(b) 接地规则 | 同文件:111-116(grounding_required/no_data_policy 字面量来源 L115) |
| DESIGN §三(c) 缺席四级 | 同文件:118-129(A1-A4 触发与 IR 落点表 L122-127;A1=ABSENT_REGISTRY 由 E2 查无身份触发 L124) |
| DESIGN §三(d) E2E-B 走查 | 同文件:131-163(黄金问题文本 L134;IR 摘要 L138;MB-1..MB-9 与 OP-1..OP-3 处置 L143-156;OP-1 公式「MB-8−(MB-1+MB-2)/2中值」L139) |
| DESIGN §四 E2E-A 对齐 | 同文件:167-185(§4.1 ID 引用约定: query_id=QB-YYYYMMDD-NNN L183) |
| DESIGN §七 红线 | 同文件:244-249(§七3 out_of_scope 拦截交易/仓位/收益承诺类 L248;§七1 快照纪律 L246) |
| E2 注册表只读接口 | scripts/fact_engine.py:75-76(`metric(metric_id)`≡`load_registry()['by_id'].get`) |
| E1 注册表加载 | scripts/fact_engine.py:43-72(by_id 索引构建 L51-58) |
| E4 严格ISO日期原语 | scripts/fact_engine.py:182-193(`parse_iso_date`,非法输入→None,不截断洗白;as_of 检测复用) |
| E3 单位纪律常量 | scripts/fact_engine.py:33-38(PRICE_LIKE_UNITS/RATE_UNITS/COUNT_UNITS;窗口 field 分派复用,零复制) |
| E2E-A 测试惯例 | tests/test_p03_e2ea.py:34-42(sys.path 注入 ROOT+scripts;字面量硬编码预期纪律 L20) |
| 注册表场景条目 | config/metric_registry.json(只读实取 2026-11-04: DFEDTARL/DFEDTARU/DFF/UST_2Y/UST_10Y/CURVE_2S10S/USDJPY 七条 display_name/unit/calendar 见 INVENTORY 层②表;总数 81) |

## §二 实现(逐文件)

**scripts/e2eb_query_ir.py**(IR定义模块,DESIGN L211「落地§三(a)IR schema」):
- §三(a) 五结构字段级 schema: IR_KEYS/BINDING_KEYS/PROVENANCE_KEYS/OP_KEYS/UNRESOLVED_KEYS(L63-68)与枚举常量 P-01..P-14(L32-60);
- `validate_ir(ir, stage)`(L248-): 两阶段字段级校验(mapped/executed;枚举/ID格式/必填/跨引用[operands→binding_id]/阶段规则),返回 issues 列表空=合法;
- 辅助构造 `make_query_id`(L71-;QB-YYYYMMDD-NNN,D-B1-10);
- 零文件IO零项目依赖(纯 schema 定义;T5 源码锁用例锁死)。

**scripts/e2eb_query_mapper.py**(映射器v1,DESIGN L211「约束式映射: 词表+注册表检索」):
- 登记词表: OUT_OF_SCOPE_PATTERNS(L35-39,21词)/AS_OF_CUE_RE(L46)/TREND_CUE_RE(L50)/METRICISH_RE(L53)/CONCEPT_RULES(L57-103,恰4条);
- `field_for_window`(L113-;单位纪律,复用 fe.RATE_UNITS/PRICE_LIKE_UNITS/COUNT_UNITS 零复制);
- `_search_registry`(L133-;display_name/calc 关键词检索=A1发现机制)/`_merge_spans`(L146-);
- `map_question`(L163-): 七步流水——①OOS拦截(L189)②as_of检测经E4(L201)③概念触发(L207)④三阶段绑定发射(L215-267;identity/metric_id分离防缺席概念撞键)⑤派生操作operand齐备性判定(L269-289)⑥剩余指称上浮(L291-304)⑦IR装配+validate_ir(stage="mapped") fail-loud自检(L306-);
- 缺省数据面=fe.load_registry()(E1)/by_id检索与E2同构(fact_engine.py:75-76);registry参数=注入面。

**tests/test_p03_e2eb_b1.py**(59用例,五类):
- T0 fixture自检(TestFixtureSanity L138-): 8条合成注册表结构/单位字面量/零日本侧身份;
- T1 schema两阶段(TestIRSchemaValid L157-/TestIRSchemaNegative L180-/TestMakeQueryId L327-): 合法mapped/executed基底+33单缺陷注入(枚举/格式/必填/跨引用/阶段规则逐条);
- T2 黄金映射(TestGoldenMapping L341-): §三(d)问题全文→IR**全量字面量对照**(L342-414)+MB-8/MB-9 ABSENT_REGISTRY点名(L416-)+自schema校验/确定性/JP在场身份自动解析(L436-)/US缺席变体/query_seq/双触发去重;
- T3 窗口与as_of(TestWindowsAndAsOf L484-): field_for_window单位纪律字面量/无cue无窗口/文本as_of/非法日期忽略/参数优先/规则D/E4行为锚;
- T4 unresolved负向(TestUnresolvedEntities L536-): 交易类问题→out_of_scope(mention字面量「应该买入」「能保证赚钱」)/剩余中性照常映射/印度政策利率→no_registry_identity/空问题/空文本拒绝;
- T5 接线与纯度(TestWiringAndPurity L583-): mock.patch注入fixture证明E1缺省接线零真实文件读取/两模块源码零网络import锁/零采集档路径字面量与零open()锁/IR模块零项目依赖锁。

## §三 测试与本地CI

- 专项套件: `python3 tests/test_p03_e2eb_b1.py` → **Ran 59 tests, OK(exit=0)**(2026-11-04T19:2xZ UTC);
- 负向敏感性(D1-D4真实注入,记录于证据包④): D1词表删「买入」→红1(test_trading_question_out_of_scope);D2硬编码缺席(跳过注册表检索)→红1(test_jp_present_fixture_resolves_identity);D3 validator删RESOLVED→provenance必填分支→红1(test_resolved_requires_provenance_executed);D4规则B发射序交换→红2(test_golden_ir_full_literal+test_us_metric_missing_fixture_absent);全部还原后59全绿,两模块sha256与注入前逐字节一致(545bddfa…/71448d40…);
- 本地CI同构(与 offline-tests.yml 逐套件循环同构,python驱动): **58个test文件=57 CI套件(排除test_glm_live)中56绿+1既有红+1跳过**;套件数对照: 56(基线,注入快照+本地57文件-1排除实测一致)+1(新增tests/test_p03_e2eb_b1.py)=57 ✓ 零漂移;
- 既有红归因: `test_p4_fixes exit=1`(39通过/4失败: 月度序列提取0条/无序列/bp报告空/%报告空——monthly_review数据块,与基线a6d086b交付时登记的**同款既有红**[E2E-A提交信息⑥「test_p4_fixes既有红4项…与本包零导入关系,归因在案」];本包diff零M/D纯新增A行,test_p4_fixes不import本包任何模块→结构性零影响;本地数据演化所致,CI环境[run 41862875466 success]与本地数据面不同);
- 逐套件记录: 证据包成员④ local-suites/suite-summary.txt(58行)+logs/。

## §四 逐要点证据映射表(AC-02)

抄录要点(DESIGN L214,①-④)逐条映射:

| 要点 | (a)实现落点 | (b)证据指针 | (c)自检结论 |
|---|---|---|---|
| ①离线单测: IR字段级schema校验用例 | scripts/e2eb_query_ir.py:32-60(常量)+126-180(绑定)+182-229(派生)+248-(总校验);tests/test_p03_e2eb_b1.py:157-339(TestIRSchemaValid/Negative/MakeQueryId共36用例: 合法基底2+单缺陷33+构造器1) | 证据包④local-suites/logs/test_p03_e2eb_b1.log(Ran 59 tests OK);CI run登记件=操作者CHECKPOINT落 rounds/021/E2EB-WP-B1-CI-dispatch-evidence.md | 过 |
| ②§三(d)问题文本→IR映射黄金用例,含MB-8/MB-9 ABSENT_REGISTRY断言 | scripts/e2eb_query_mapper.py:163-(map_question);tests:342-414(全量字面量对照,11绑定+3派生+缺席理由含「(8指标,INVENTORY G-01)」)+416-434(MB-8/MB-9点名断言) | 同上log;§六D-B1-02..05登记=实现常量=测试断言三方一致 | 过 |
| ③unresolved_entities负向用例(禁交易类问题→out_of_scope) | scripts/e2eb_query_mapper.py:35-39(21词表)+189-199(拦截);tests:537-559(交易问题→恰2实体out_of_scope+note含「不构成投资建议」)+561-581(剩余中性映射/no_registry_identity/空问题) | 同上log;D-B1-07登记=词表常量=断言一致 | 过 |
| ④模块SHA登记 | 本REPORT §五(下) | 证据包③git取证+§五 sha256;commit SHA=8d8b408c6c2ccaf50d702a2f0f3fa8fcefa1a389(实现提交,本REPORT回填提交前的稳定固定点) | 过 |

参数类登记核验(AC-02判据3): 词表/枚举/模板/触发词全部先登记(§六,commit 295ebf7)→实现常量→运行,三者一致,运行后零回改。

## §五 模块SHA登记(验收要点④)

| 文件 | sha256(实现提交8d8b408版,与当前工作树逐字节一致) |
|---|---|
| scripts/e2eb_query_ir.py | 545bddfa698a17f773313d5337b5ea7a2be8dec19c234fe144169677e87ddd2f |
| scripts/e2eb_query_mapper.py | 71448d40dd46742368a216eeb495ab15b05e9728daccd5ed022856b905d16a6e |
| tests/test_p03_e2eb_b1.py | 8c594c9afdc90238f6bfcf33fc1812cf7916db0813eeec2fa8be448d8b6f3cbe |

commit SHA 登记: 实现提交=8d8b408c6c2ccaf50d702a2f0f3fa8fcefa1a389;开工登记提交=295ebf7(全值见证据包③git取证);最终尖端与CI headSha登记=操作者CHECKPOINT(rounds/021/E2EB-WP-B1-CI-dispatch-evidence.md)。

## §六 实现参数与决策点登记(先登记后运行,运行后禁回改)

**IR schema 常量(全部抄自 DESIGN §三(a) 实读行号,零新造语义)**:

| # | 参数 | 登记值 | DESIGN 依据 |
|---|---|---|---|
| P-01 | mode 字面量 | `"B"` | L59 |
| P-02 | MetricBinding.role 枚举 | {level, derived_window, spread_component, correlation_series} | L73 |
| P-03 | window 枚举 | {week, mtd, ytd, m1, m3, m6, m12};role=derived_window→window 必填 | L74 |
| P-04 | field 枚举 | {value, pct_change, pp_change, bp_change, abs_change} | L75 |
| P-05 | 绑定 status 终态枚举 | {RESOLVED, ABSENT_REGISTRY, ABSENT_SOURCE, ABSENT_DATA, ABSENT_WINDOW} | L76 |
| P-06 | absence_reason 语义 | status≠RESOLVED 时如实的原样原因 | L77 |
| P-07 | provenance 规则 | status=RESOLVED 时必填 | L78 |
| P-08 | Provenance.quality_status 枚举 | {PASS, DEGRADED, WARN, FAIL} | L87 |
| P-09 | DerivedOperation.op_type 枚举 | {spread, level_diff, correlation} | L93 |
| P-10 | 派生 status 终态枚举 | {COMPUTED, NO_DATA};NO_DATA→result=null 不部分计算 | L97-98,L129 |
| P-11 | UnresolvedEntity.mapping_status 枚举 | {no_registry_identity, ambiguous, out_of_scope} | L104 |
| P-12 | answer_constraints 恒等值 | `{"grounding_required": True, "no_data_policy": "report_absence"}` | L66-67 |
| P-13 | ID 格式 | query_id=QB-YYYYMMDD-NNN;binding_id=MB-N;op_id=OP-N;fact_id=metric_id@YYYY-MM-DD;snapshot_id=research_snapshot_YYYYMMDD[_vN] | L57,L71,L92,L84,L62,L183 |
| P-14 | 派生单位 | 利率差类 op unit=percentage_point | L96 |

**登记型决策点**:

| # | 决策点 | 登记内容 |
|---|---|---|
| D-B1-01 | 生命周期哨兵 | DESIGN 五值 status(P-05)与二值派生 status(P-10)为**执行后终态词汇**;WP-B1 范围「不含执行器」(L212)→映射器对「注册在场但未取数」绑定与「operand 齐备但未计算」派生操作以哨兵值 `PENDING_EXECUTION` 如实标记(validate_ir 的 stage="mapped" 合法值;stage="executed" 下零出现);禁伪造 RESOLVED+provenance(取数属 WP-B2)。哨兵为映射期新增词汇,不改动 DESIGN 终态枚举本身 |
| D-B1-02 | 概念规则恰 4 条(约束式词表) | A=美日政策利率差: 触发词「政策利率差」;US侧绑定 DFEDTARL/DFEDTARU/DFF(level);JP缺席概念「日本政策利率」;OP-1 spread 公式「日本政策利率 − (DFEDTARL+DFEDTARU)/2(目标区间中值)」(对齐 L139)。B=美日10Y收益率差: 触发「(10年期\|十年期)+≤6汉字+收益率差」;US侧 UST_2Y/UST_10Y/CURVE_2S10S(level);JP缺席「JGB 10Y」;OP-2「JGB 10Y − UST_10Y」+OP-3「UST_10Y − UST_2Y(查询期计算,对照注册值CURVE_2S10S)」(对齐 L139)。C=USDJPY: 触发「美元兑日元\|美元日元\|USDJPY\|USD/JPY\|日元汇率」;趋势cue「最近\|走势\|表现\|怎么样\|涨\|跌」在场→附加 week+ytd 两窗口绑定(对齐 L138 MB-7 与 L151 周/YTD 口径)。D=美国政策利率水平: 触发「联邦基金\|美联储利率\|美国政策利率」;DFEDTARL/DFEDTARU/DFF(level),无 op 无 JP 缺席概念 |
| D-B1-03 | 绑定发射顺序 | 阶段1=按规则 A→B→C→D 序、各规则 us_bindings 登记序发射 level 绑定(未触发规则跳过);阶段2=缺席概念(规则序);阶段3=窗口绑定;binding_id 按发射序 MB-1.. 递增。发射序对齐 DESIGN §三(d) 走查 MB-1..MB-9 序(L138);MB-7「level+derived_window week/ytd」按 schema 单 role 约束(L73)展开为 MB-7(level)+MB-10/MB-11(week/ytd 窗口),走查仅列 9 绑定为「关键节点摘录」(L136),展开不改走查语义 |
| D-B1-04 | 缺席A1发现机制(非硬编码) | US侧: 意图 metric_id 经注册表 by_id 精确检索(E2 同构,fact_engine.py:75-76);JP/缺席概念: 经 display_name/calc 关键词检索,search_terms 登记=日本政策利率→(日本政策利率, 日银, BOJ);JGB 10Y→(JGB, 日本国债, 日本10年)。零命中→ABSENT_REGISTRY;命中→身份解析为该 metric_id(未来 WP-B3 注册后同问题自动转 PENDING_EXECUTION,证明缺席是发现而非硬编码) |
| D-B1-05 | 缺席理由模板 | JP族: `{label}不在注册表({n}指标,INVENTORY G-01)`(对齐 L152 走查文本格式);US侧意图缺席(fixture负向变体用): `{metric_id}不在注册表({n}指标)`;n=注册表 metrics 计数,运行时实取(不硬编码81) |
| D-B1-06 | 窗口field单位纪律 | field_for_window(unit): unit∈fact_engine.RATE_UNITS→pp_change;∈COUNT_UNITS→abs_change;∈PRICE_LIKE_UNITS→pct_change;否则 raise 不猜映射。复用 fact_engine.py:33-38 常量(零复制),对齐 E3 单位纪律(L88-89) |
| D-B1-07 | out_of_scope 词表 | {"买入","卖出","做多","做空","开仓","平仓","加仓","减仓","仓位","应该买","该不该买","能保证","稳赚","保证收益","投资建议","抄底","逃顶","止损","止盈","杠杆","赚钱"};命中(重叠span合并)→UnresolvedEntity(mapping_status="out_of_scope",note 含「不构成投资建议」);v1 不整题拒答——渲染层拦截属 WP-B5(DESIGN L248「实现于WP-B5渲染层」),指标映射对剩余中性指称照常如实进行并双双上浮 |
| D-B1-08 | as_of 检测 | 文本「截至\|截止于\|截止到\|截止\|as of」后随 YYYY-MM-DD,经 fe.parse_iso_date(E4)严格校验;非法日期→不设 as_of(不猜映射不截断洗白);显式参数优先于文本检测;target_snapshot_id 恒 None(快照绑定=R1,属 WP-B2 执行器,L62/L246) |
| D-B1-09 | 剩余指称上浮 | 指称类后缀正则 `(收益率|利率|利差|指数|汇率|期货|CPI|GDP)` 前缀≤8字符;与已消费span(规则触发/缺席概念词/out_of_scope命中)重叠者跳过;未消费且注册表 display_name/calc 零命中→UnresolvedEntity(no_registry_identity,note「如实上浮,不猜映射」);v1 不发 ambiguous(枚举在场由 schema 校验覆盖,登记为后续扩展) |
| D-B1-10 | query_id 生成 | QB-{created_at 的 YYYYMMDD}-{seq:03d};seq 参数默认 1;created_at 缺省=受理时刻 now(UTC+8,L58);同日单调计数与落盘属 WP-B4 档案(v1 零落盘) |
| D-B1-11 | 测试数据纪律 | 合成 fixture 注册表为唯一数据源(8条=7场景指标+1无关SPX,JP在场变体+2条=10,US缺席变体-1条=7);预期值全字面量硬编码;不读真实 config/metric_registry.json、不读 data/daily 任何档;registry 参数=依赖注入面,缺省=fe.load_registry()(E1)——wiring 测试经 mock.patch 注入,零真实文件读取 |
| D-B1-12 | 派生操作映射期判定 | 任一 operand 绑定 status∈ABSENT族→op status=NO_DATA,result=None(DESIGN L129 不部分计算);否则 PENDING_EXECUTION;COMPUTED 与数值结果属 WP-B2(D-B1-01 同源);operands 引用 binding_id(跨引用校验入 validate_ir) |
| D-B1-13 | calculation_ref 映射期模板 | `公式: {formula};输入观测日与期限匹配由执行器(WP-B2)按E11纪律落定`;NO_DATA 者追加 `;operand缺席→NO_DATA不部分计算(DESIGN §三(c))` |

以上参数于任何测试运行之前登记(本节先于 §二/§三 实现与运行落盘);运行后禁回改。

## §七 偏离与如实声明

1. **tests 文件名差异**(§零(ii)已登记): DESIGN L214 工件草案glob `tests/test_p03_b1*.py` 与冻结合同附录A §零(ii)实值名 `tests/test_p03_e2eb_b1.py` 不字面匹配;依 DESIGN §六标题自注(L206「验收要点=草案,正式AC由主Agent后续轮拟定」)以冻结合同名为准,差异公开登记非静默。时刻: 2026-11-04T19:05Z UTC。
2. **test_p4_fixes 本地既有红**: 与基线a6d086b登记同款4项(monthly_review数据块),本包零M/D纯新增、零导入关系,归因在案(§三);CI环境基线run 41862875466=success。
3. **D-B1-01 生命周期哨兵 PENDING_EXECUTION**: DESIGN §三(a) 五值status/二值派生status为执行后终态词汇,而WP-B1范围「不含执行器」(L212)结构性要求映射期存在「已绑定未取数」状态;哨兵为**映射期新增词汇**(不改动终态枚举),已于运行前登记§六(§零 commit 295ebf7),非事后补登。
4. **走查MB-7展开**: DESIGN L138「MB-7 USDJPY(level+derived_window week/ytd)」为摘要压缩;schema单role约束(L73)下展开为MB-7(level)+MB-10/MB-11(week/ytd),MB-8/MB-9编号保持与走查一致(黄金断言不受影响),登记于D-B1-03。
5. **OOS相邻span合并**: 「能保证」(13,16)与「赚钱」(16,18)相接即并为一实体(mention=「能保证赚钱」),D-B1-07「重叠span合并」含相接情形,测试内手算注明。
6. **DELIVERY zip sha256 自指豁免**(沿 d667a4e/fa8db61 先例): zip内DELIVERY副本无zip整体哈希行(固定点不可内含自身哈希),实测值以封装后追加行落档,终态SHA与最终ls-remote见证据目录 08-sidecar/final-state.txt(zip外)。
7. 无其他偏离;未触发情形(b)上游漂移(套件数恰57=56+1);未触发情形(c)不可得(本包无真实运行面,登记零运行产物);未触发PREEMPT-STOP。

## §八 合同逐条自检(AC-01~AC-07)

| AC | 自评 | 一句证据指引 |
|---|---|---|
| AC-01 规格抄录与登记正确性 | PASS | §零(i)逐字抄录(L210-214,行号即DESIGN并入后实读)审计可直读对照;清单k=5逐条附依据;与git ls-files零重合;tests文件名差异公开登记(§七.1) |
| AC-02 逐要点交付与证据映射 | PASS | §四映射表4/4条,落点file:line实取;参数登记=常量=断言一致;无真实运行面→零运行产物登记(§零(iv)) |
| AC-03 测试与确定性验证 | PASS(生效) | 59用例零网络/合成fixture唯一数据源(不读真实registry与采集档,mock.patch注入)/预期值字面量硬编码;本地: 新套件exit=0,全量58文件57套件56绿+1既有红归因(§三);负向敏感性D1-D4全红 |
| AC-04 引用真实性与注入边界 | PASS | §一file:line逐条可寻(±3行);「注入快照」字样仅用于基线CI套件数56与31支快照(合同实值,已本地对照57文件-1排除=56一致);无跨支引用(设计三件=并入后工作树实读);无引擎路径依赖 |
| AC-05 范围/分支/生产隔离 | PASS | diff name-status=纯A行(3并入+5白名单,零M/D);分支自基线切出+恰1个--no-ff merge(800960e)+线性提交;reflog无reset/amend;ls-remote终态见证据(唯一新增dev/p03-e2eb-b1);零网络import(T5锁);E2E-A六文件/主流水线/registry/workflow零触碰(对齐=复用调用fe);LIVE零写入(取证见证据包③) |
| AC-06 CI与证据包 | PASS(本地侧)/CI待操作者 | 证据包八类成员+SHA256SUMS落/tmp/p03-e2eb-b1-evidence/;DELIVERY五节;自述四段(result.md由驱动落档);CI dispatch=操作者CHECKPOINT(执行Agent未自行dispatch),登记件路径 rounds/021/E2EB-WP-B1-CI-dispatch-evidence.md |
| AC-07 研究纪律与使用边界 | PASS | 模块零采集档路径字面量/零open(T5源码锁);缺值零填0(NO_DATA→result=None schema锁);OOS词表拦截+文案「不构成投资建议」;零GLM/零凭证/零付费;W4/W5未触碰;白名单外需求零实施(登记发现: 无) |

## §九 提交前数值标注六项自检清单(§5.3,强制)

双文档(REPORT+DELIVERY)全文扫描,计数/统计类数值逐个二选一标注;[实取]项已回工作树复核(2026-11-04T19:3xZ):

| 数值 | 值 | 标注 |
|---|---|---|
| 白名单文件数 k | 5 | [实取·来源: 本REPORT §零(ii)清单] |
| DESIGN WP-B1行行号 | L210-214 | [实取·来源: docs/P03_E2EB_DESIGN.md 并入后工作树,2026-11-04实读] |
| 概念规则数 | 4 | [实取·来源: scripts/e2eb_query_mapper.py:57-103计数] |
| out_of_scope词表词数 | 21 | [实取·来源: scripts/e2eb_query_mapper.py:35-39计数] |
| 专项测试用例数 | 59 | [实取·来源: 本地运行"Ran 59 tests",证据包④log] |
| schema类用例数 | 36 | [实取·来源: tests/test_p03_e2eb_b1.py L157-339方法计数] |
| 黄金IR绑定数/派生数 | 11/3 | [实取·来源: tests全量字面量期望(手算登记)] |
| fixture注册表条数(基/JP变体/US变体) | 8/10/7 | [实取·来源: tests L48-90构造字面量] |
| 真实注册表指标总数 | 81 | [实取·来源: python计数config/metric_registry.json,2026-11-04;与INVENTORY层②一致] |
| 测试文件总数/CI套件数 | 58/57 | [实取·来源: 本地CI同构运行,证据包④suite-summary.txt] |
| 基线CI套件数 | 56 | [注入快照·合同实值BASE-B1-CI-SUITES;本地对照57文件-1排除=56一致] |
| 既有红失败项 | 4 | [实取·来源: 证据包④logs/test_p4_fixes.log「39通过/4失败」] |
| 负向敏感性注入 | D1-D4红1/1/1/2 | [实取·来源: 本地注入实测,§三] |
| merge-base | 1ddfb65ec78f4358b7a004be8ef5d8916ba0f052 | [实取·来源: git merge-base,2026-11-04] |
| 并入设计文件数/行数 | 3/489 | [实取·来源: merge输出"3 files changed, 489 insertions"] |
| 模块/测试sha256 | 3条全值 | [实取·来源: shasum -a 256,§五] |
| 实现提交SHA | 8d8b408c…a389 | [实取·来源: git rev-parse,§五] |
| 参数登记项数 | P-01..14(14)+D-B1-01..13(13) | [实取·来源: 本REPORT §六] |
| DELIVERY节数 | 5 | [实取·来源: docs/P03_E2EB_B1_DELIVERY.md结构] |
| 证据包成员类别 | 8 | [实取·来源: 合同附录A §六②最低集;证据包目录实测] |

日期/SHA/行号按边界出圈登记: 本文件头部时区声明(UTC);DESIGN行号=并入后工作树版本;无[示意]数值留档。
