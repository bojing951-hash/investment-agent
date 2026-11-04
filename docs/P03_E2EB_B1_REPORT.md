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

(待实现后回填)

## §三 测试与本地CI

(待回填)

## §四 逐要点证据映射表(AC-02)

(待回填)

## §五 模块SHA登记(验收要点④)

(待回填)

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

(待回填)

## §八 合同逐条自检(AC-01~AC-07)

(待回填)
