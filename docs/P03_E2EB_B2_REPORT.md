# IA-P03-E2EB-WP-B2 REPORT — 查询执行器(快照绑定+引擎口径复用+查询期派生+按需相关性+as_of语义)

> 包: IA-P03-E2EB-WP-B2(E2E-B 第 2 实现包) · 执行Agent: Agent 3
> 分支: `dev/p03-e2eb-b2`(自基线 3e7c300b85a38ab2f60990397751e2f3b44a997f 切出;本包无并入步,设计三件经 B1 指定并入步已在基线祖先谱系,开工步骤4实测核验)
> 合同: IA-P03-E2EB-WP-B2-AC-v1.0(冻结,占位符已实值化)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY/B1 在场件行号一律为**基线工作树(3e7c300)实读**行号(2026-11-04T19:5xZ 实取);B1 模块行号为其实现在场版(基线工作树)行号。

---

## §零 规格抄录与交付面登记(开工首步,AC-01)

### (i) DESIGN §六 WP-B2 行四要素逐字抄录

实读 `docs/P03_E2EB_DESIGN.md`(基线工作树),WP-B2 行位于 L216-220,逐字抄录如下:

```text
L216: **WP-B2 查询执行器(快照绑定+引擎口径复用+查询期派生+按需相关性+as_of语义)**
L217: - 目标: IR→数值: 快照绑定(R1/R3)、engine口径取值(E3/E5/E11复用)、spread/level_diff查询期派生(calculation_ref纪律,D3)、按需配对相关性(C3/C4复用series_store,D4)、as_of时点只读锚定(D6)。
L218: - 范围: 新增执行器模块;不改fact_engine/snapshot_builder既有函数签名。
L219: - 依赖: WP-B1;GAP-01修复前美日双端场景按§三(c)缺席输出。
L220: - 验收要点草案: ①离线单测以DEV授权副本(data/daily 20261101/20261102)构建write=False快照并执行OP-3(工件: 测试文件+数据档引用 data/daily/macro_20261102.json) ②NO_DATA传导用例(OP-1/OP-2 result=null,工件: 测试文件) ③as_of历史锚定用例: 同一问题两个as_of,输出随快照时点不同且不混入期后数据(工件: 测试文件+as_of字符串) ④引擎口径一致性: 执行器输出与fact_engine直算逐值相等(硬编码预期值,对齐E2E-A"测试预期值硬编码"纪律;工件: 测试文件) ⑤CI零回归(工件: GitHub Actions run ID)。
```

四要素齐备(目标/范围/依赖/验收要点),无缺失。依赖列核验: WP-B1 已落地(基线 3e7c300b85a38ab2f60990397751e2f3b44a997f=dev/p03-e2eb-b1 审计 PASS 尖端,开工 ls-remote 全值比对一致,`scripts/e2eb_query_ir.py`/`scripts/e2eb_query_mapper.py`/`tests/test_p03_e2eb_b1.py` 在场);GAP-01(日端利率身份)未修复=基线现状,按 §三(c) 缺席输出承接 ✓;范围不含 GLM/网络/新数据源凭证要求,不要求并入他支 → 无情形(d)停止条件。

### (ii) 交付文件清单(k=4,登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据 |
|---|---|---|
| 1 | `scripts/e2eb_query_executor.py` | DESIGN L218「新增执行器模块」(恰 1 个代码模块)+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」 |
| 2 | `tests/test_p03_e2eb_b2.py` | DESIGN L220①-④工件「测试文件」+合同附录A §零(ii)「含代码则必含 tests/test_p03_e2eb_b2.py」 |
| 3 | `docs/P03_E2EB_B2_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P03_E2EB_B2_DELIVERY.md` | 合同附录A §零(ii)必含件 |

### (iii) 结构约束核验

- 与 `git ls-files` 输出零重合: 4 路径均为纯新增(开工时实读 `git ls-files scripts/ tests/ docs/` 无一存在;B1 交付件为 `e2eb_query_ir.py`/`e2eb_query_mapper.py`/`test_p03_e2eb_b1.py`/`P03_E2EB_B1_*.md`,零重合)✓
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p03_e2eb_b2.py)✓
- 推导无越界: 范围列「新增执行器模块」恰 1 个代码模块 → scripts/ 恰 1 文件;DESIGN L220 工件未另指定模块文件名,依固定推导规则与 B1 命名族(e2eb_query_*)命名;未引入 DESIGN 依据外文件 ✓

### (iv) 运行产物边界登记

WP-B2 验收要点(L220①-⑤)工件全部为离线测试文件/as_of字符串/CI run 登记类;范围列(L218)为执行器模块本身,DESIGN 未为 WP-B2 指定编排入口或真实运行要求(端到端走查固化属 WP-B5,L234-238)→ 本包登记「**零运行产物**」: data/research/ 零写入,data/daily 与既有快照零读取零写入(测试全合成 fixture 写 tempdir,见 §六 D-B2-14)。要点①「数据档引用 data/daily/macro_20261102.json」按冻结合同 AC-03(合成 fixture 唯一数据源,R014-D3 承接)处理为 fixture 结构参照引用(测试文件内文档注记),非测试数据依赖——差异如实登记于 §七.1。

---

## §一 前置实读登记(file:line)

(实现前实读,全部为基线工作树实取,非注入摘要)

| 对象 | 登记 |
|---|---|
| DESIGN §三(a) IR schema | docs/P03_E2EB_DESIGN.md:53-107(MetricBinding L70-79/Provenance L81-89/DerivedOperation L91-100) |
| DESIGN §三(c) 缺席四级 | 同文件:118-129(A1-A4 表 L122-127;NO_DATA 不部分计算 L129) |
| DESIGN §三(d) E2E-B 走查 | 同文件:131-163(OP-3 查询期计算+观测日差异披露 L156) |
| DESIGN §四 E2E-A 对齐 | 同文件:167-185(§4.7 as_of 只读锚定=既有快照/离线构建 write=False L177) |
| DESIGN §六 WP-B2 行 | 同文件:216-220(§零(i) 逐字抄录) |
| DESIGN §七 红线 | 同文件:244-249(§七1 唯一数据入口=R1+R3 L246;§七4 数据不足不填0 L249) |
| B1 IR 模块(承接) | scripts/e2eb_query_ir.py:46(PENDING_EXECUTION 哨兵)/156-179(绑定两阶段 status 规则)/248-304(validate_ir) |
| B1 映射器(承接) | scripts/e2eb_query_mapper.py:163-322(map_question 只产IR不取数 L7/L109;D-B1-12 派生映射期 NO_DATA 判定 L269-289;D-B1-13 calc_ref 模板 L107) |
| B1 REPORT 参数登记(承接) | docs/P03_E2EB_B1_REPORT.md:122-159(§六 D-B1-01..13;D-B1-01 哨兵语义/D-B1-12 派生判定为执行器承接面) |
| E1 注册表加载 | scripts/fact_engine.py:43-72 |
| E2 注册表只读接口 | scripts/fact_engine.py:75-76 |
| E3 统一收益引擎 | scripts/fact_engine.py:81-174(单位纪律 L124-134;数据不足 available:False L90/L94-95) |
| E4 严格ISO日期原语 | scripts/fact_engine.py:182-193 |
| E5 事实构造 | scripts/fact_engine.py:196-238(fact_id 格式 L211;source{collector,file} L219) |
| E11 派生计算纪律 | scripts/fact_engine.py:465-503(calculation_ref=公式+观测日+期限匹配 L476) |
| S1 快照构建入口 | scripts/snapshot_builder.py:236-438(write=False 早退 L384-385;gate_a 装配 L313-342) |
| S2 输入解析 | scripts/snapshot_builder.py:47-101(精确/fallback/可信边界) |
| 快照 series_store | scripts/snapshot_builder.py:358-382(仅 global+china 序列;macro 序列不经 store=既有结构事实) |
| R1 确定性快照选择 | scripts/research_provenance.py:1243-1294(最高修订版;候选损坏整体拒绝) |
| R3 门禁放行判定 | scripts/research_provenance.py:1183-1188(PASS/DEGRADED 放行;FAIL/None 拒绝) |
| 门禁降级原因摘要 | scripts/research_provenance.py:1189-1207(gate_reason_desc) |
| Gate A 重算 | scripts/research_provenance.py:853-894(core_missing→FAIL;noncore_missing→至少DEGRADED;FIX5-04 通道缺失→effective=None) |
| 通道规范文件规则 | scripts/research_provenance.py:143-157(SOURCE_CHANNELS/SOURCE_FILE_RULES: global/macro/china/rate_economy 四通道) |
| C3 共同观测日配对 | scripts/correlation_calculator.py:53-66(paired_returns) |
| C4 皮尔逊相关 | scripts/correlation_calculator.py:69-80(pearson) |
| E2E-A 接入点范式 | scripts/research_history_query.py:30-57(ACCESS_POINTS 登记制)/80-153(load_metric_series 经登记接入点,禁直读;series_store 结构边界登记 L25-27) |
| 既有测试范式 | tests/test_snapshot.py:30-104(build_fixture_day 合成采集文件)/117-119(tempdir+trusted_root 同构) |
| B1 测试纪律范式 | tests/test_p03_e2eb_b1.py:30-50(合成 fixture 注册表)/583-619(T5 接线与纯度锁) |
| 注册表实测计数 | config/metric_registry.json(只读实取 2026-11-04: 81 指标,core=32,source 分布 global 32/macro 28+1/rate 4/china 12) |

## §二 实现(逐文件)

(实现后回填;开工登记版占位——本节于实现提交后填写,见 §五 commit 链)

## §三 测试与本地CI

(实现后回填)

## §四 逐要点证据映射表(AC-02)

(实现后回填)

## §五 模块SHA登记

(实现后回填)

## §六 实现参数与决策点登记(先登记后运行,运行后禁回改)

**承接 B1 参数**(docs/P03_E2EB_B1_REPORT.md §六,运行后已禁改;本包作为下游消费面原样承接): P-01..P-14(IR schema 常量)/D-B1-01(PENDING_EXECUTION 哨兵=映射期词汇,executed 阶段零出现)/D-B1-12(派生映射期 NO_DATA|PENDING_EXECUTION 判定)/D-B1-13(calc_ref 映射期模板)。

**本包登记型决策点**:

| # | 决策点 | 登记内容(运行前登记) |
|---|---|---|
| D-B2-01 | 执行器入参与数据入口 | `execute_query(ir, *, snapshot=None, daily_dir=None, trusted_root=None, registry=None)`。snapshot 显式注入=调用方经 R1/S1 取得的快照(依赖注入面,对齐 B1 registry 注入先例 D-B1-11);daily_dir 路径=执行器自取: R1 优先(当日既有快照文件)→ 无则 S1 `build_snapshot(write=False)` 离线构建(DESIGN L177「只读锚定既有快照/离线构建(write=False)」);**禁墙钟**: as_of=None 且 daily_dir 无既有快照文件 → 结构化 refusal(不取 now 构建非确定性快照) |
| D-B2-02 | 目标快照日派生 | ymd=as_of 前10字符经 `fe.parse_iso_date`(E4)严格校验(非法→ValueError fail-loud);as_of 带时间戳仅取日期部分(日粒度绑定;被绑定快照自身 research_as_of 治理其内部点时语义——登记披露,非混同) |
| D-B2-03 | 门禁纪律(R3) | `gate_a.status` 经 `rp.gate_allows_formal_research`(R3)判定;FAIL/None/缺失 → 结构化 refusal `{"ir": 原样mapped, "values": {}, "refusal": 含rp.gate_reason_desc摘要}`,零部分执行零绑定解析(DESIGN L208「查询执行器数据入口恒为R1快照选择+R3门禁放行判定」严格读法) |
| D-B2-04 | 绑定执行序与四级缺席落位 | 输入 IR 须过 `validate_ir(stage="mapped")`(不过→ValueError);ABSENT_REGISTRY(mapper期A1)原样保留;PENDING_EXECUTION→事实在场=RESOLVED+provenance;事实缺席→通道级 A2/A3 分级(见 D-B2-07);derived_window 绑定四级: 无事实(同A2/A3)/fact 无 derived 键(ABSENT_WINDOW,理由模板「事实无窗口派生(序列缺席,窗口不可用)」)/`derived[window].available==False`(ABSENT_WINDOW,引擎 reason **原样转述**,DESIGN L127)/窗口字段在场→RESOLVED(value=derived[window][field]) |
| D-B2-05 | provenance 装配 | `{metric_id, snapshot_id=目标快照ID, fact_id, observation_date, source_file=fact.source.file(仅披露字段,查询器无直读路径,D1/L86), quality_status=fact.quality_status, calculation_ref}`: level/spread_component/correlation_series 绑定=fact.calculation_ref 原样透传(string|null);derived_window 绑定=模板 `窗口{window}.{field};基准{basis_date}(E3口径)` |
| D-B2-06 | 数值出口与不可变性 | 返回 `{"ir": executed_ir, "values": {binding_id: value}, "snapshot_id", "gate_status"}`;IR schema 绑定无 value 字段(DESIGN §三(a) L70-79),values 映射=执行器数值面(WP-B5 渲染层消费,DESIGN L115 渲染校验衔接);仅 RESOLVED 绑定入 values;输入 IR 深拷贝后变异,零原地修改;`target_snapshot_id` 绑定后由 executed IR 携带(L177「绑定后不可变」) |
| D-B2-07 | 通道映射与 A2/A3 分级 | registry `source`→sources_status 通道: `macro_collector→macro`/`global_market_collector→global`/`rate_expectations→rate_economy`/`china_market_collector→china`;通道状态 MISSING/READ_FAIL → **ABSENT_SOURCE**,理由模板「指标已注册但当日采集缺失(通道{ch}状态{st})」(DESIGN L125 措辞);EXACT/FALLBACK 而无事实 → **ABSENT_DATA**,理由模板「本期无该指标事实」(L126 措辞);`fact_engine(derived)` 族无采集通道 → ABSENT_DATA 追加「(派生输入缺席,归因性缺席)」 |
| D-B2-08 | 执行器侧 A1 防御 | PENDING 绑定 metric_id 经 registry by_id(E2 同构 fe:75-76)查无 → 回退 ABSENT_REGISTRY(metric_id 置 None+理由「{mid}不在注册表({n}指标)」)——mapper 注入面 fixture 与真实 registry 差集(如 WP-B3 前瞻 JP 身份)的如实兜底;与 schema 一致(ABSENT_REGISTRY→metric_id=None) |
| D-B2-09 | spread 执行 | 全 operand RESOLVED → `result=round(v[0]−mean(v[1:]),4)`(2 operand=首−次;3 operand=首−其余均值,恰覆盖 OP-1 目标区间中值/OP-2/OP-3 公式族,D-B1-02 登记公式集);任一 operand 非 RESOLVED → status=NO_DATA,result=None(calculation_ref 追加「;operand缺席→NO_DATA不部分计算」);COMPUTED 的 calculation_ref=模板 `公式: {formula};输入观测日{dates};{期限匹配判定}`——观测日一致=「期限匹配(观测日一致,E11纪律)」,不一致=「观测日不一致({a} vs {b}),差异如实披露不混同」(DESIGN L156 先例) |
| D-B2-10 | level_diff 执行 | 恰 2 operand 且同 metric_id、其一 role=level 另一 role=derived_window(违规→ValueError 语义 fail-loud);「同指标两时点差」(DESIGN L93)=观测日时点 vs E3 窗口基准日时点;`result=round(level值−窗口基准值,4)`;calculation_ref 披露两时点(observation_date 与 basis_date) |
| D-B2-11 | correlation 执行 | 恰 2 operand;序列=快照 `series_store[metric_id]`(D4,快照历史序列层,sb:358-382);**复用** `cc.paired_returns`(C3)+`cc.pearson`(C4)零复制;`result=round(全共同观测日窗口 pearson,4)`;任一序列不在 store / 共同样本<3 / 零方差 → NO_DATA result=None(理由注明「序列不在快照series_store」——macro 通道序列不经 store=既有结构事实,research_history_query.py:25-27 同源登记,**登记发现不实施**: macro 序列入 store 须改 snapshot_builder,白名单外,REPORT §七.5) |
| D-B2-12 | R1 版本纪律复用 | daily_dir 路径先 `rp.select_snapshot(ymd, daily_dir)`(最高修订版/候选损坏整体拒绝语义全继承,R1);as_of=None → 以 os.listdir 枚举 daily_dir 内 `research_snapshot_YYYYMMDD.json` 取最大 ymd 再经 R1 选择(**仅快照层目录列举,零采集档文件 IO**) |
| D-B2-13 | 产出校验 fail-loud | executed IR 产出必过 `qir.validate_ir(stage="executed")`(两阶段校验,B1 D-B1-01 承接: PENDING 零出现/RESOLVED 必携 provenance/COMPUTED 必有数值 result+calculation_ref),不过 → ValueError(对齐 B1 映射器 fail-loud 自检先例) |
| D-B2-14 | 测试数据纪律(R014-D3 承接) | 合成采集文件(四通道全: global_/macro_/china_/rate_economy_YYYYMMDD.json,结构复刻采集器输出)写 tempfile.TemporaryDirectory+`trusted_root=同目录`(tests/test_snapshot.py:117-119 同构);**核心覆盖生成器**=运行时读真实 registry 枚举 core 集,按 metric `source` 路由合成事实(通用值=registry validation.range 中点,场景指标显式覆写为**发明字面量**——零真实数据数值转录)——注册表演进(如 WP-B3 新增 core)自动适配,零硬编码 core 清单;预期值全字面量硬编码(手算,不从被测模块导入计算);零真实数据档读取(不读 data/daily 任何档;真实 registry 只作为身份/校验管道既有依赖,与全仓既有测试同构);fixture→预期值映射逐断言组登记于 DELIVERY 专节 |

以上参数于任何测试运行之前登记(本节先于 §二/§三 实现与运行落盘);运行后禁回改。

## §七 偏离与如实声明

(实现后回填)

## §八 合同逐条自检(AC-01~AC-07)

(实现后回填)

## §九 提交前数值标注六项自检清单(§5.3,强制)

(实现后回填)
