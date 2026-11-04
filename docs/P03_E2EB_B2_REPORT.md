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

**实现提交见 §五 commit 链;以下行号为实现提交版工作树实取(2026-11-05)。**

### scripts/e2eb_query_executor.py(359 行,纯新增)

- 常量层: `CHANNEL_OF_SOURCE`(L40-45,注册表 source→通道,D-B2-07)/`_SNAPSHOT_FILE_RE`(L47,快照层文件名,D-B2-12)/缺席理由模板 5 条(L50-54,DESIGN L124-127 措辞)/`REASON_ABSENT_REGISTRY`(L56,D-B2-08)/期限匹配与 calculation_ref 模板 6 条(L58-67,E11 纪律+NO_DATA 后缀)。
- `_refusal`(L70-73,D-B2-03 结构化拒绝: IR 原样 mapped 态+零数值+如实原因)。
- `_ymd_from_as_of`(L76-83,D-B2-02: E4 严格校验,非法→ValueError fail-loud)。
- `_latest_snapshot_ymd`(L86-97,D-B2-12: os.listdir 枚举快照层文件名取最大 ymd,零采集档 IO,禁墙钟)。
- `_acquire_snapshot`(L100-116,D-B2-01: as_of 路径 R1 既有快照优先→无则 S1 `build_snapshot(write=False)` 离线构建;as_of=None 路径 latest-ymd 枚举+R1;两路均无→refusal)。
- `_mark_resolved`(L119-131,D-B2-05: provenance 七字段装配,source_file 仅披露)。
- `_mark_channel_absent`(L134-145,D-B2-07: A2(通道 MISSING/READ_FAIL)优先,否则 A3;`fact_engine(derived)` 族无通道→归因性缺席措辞)。
- `_resolve_binding`(L148-181,D-B2-04: derived_window 四级缺席链(无事实→A2/A3;无 derived 键;available:False;字段缺席)与 level 族(事实值+fact_id+数值类型守卫)。
- `_execute_spread`(L188-199,D-B2-09: result=round(v[0]−mean(v[1:]),4);观测日一致/不一致的期限匹配披露)。
- `_execute_level_diff`(L202-230,D-B2-10: 恰 2 operand+同指标+level/derived_window 角色组合守卫(违规 ValueError);result=level 值−E3 basis_value;两时点 calculation_ref;基准值缺席→NO_DATA)。
- `_execute_correlation`(L233-264,D-B2-11: series_store 两序列→`cc.paired_returns`(C3)+`cc.pearson`(C4)复用零复制;store 缺席/样本<3/零方差→NO_DATA 如实)。
- `execute_query`(L267-359 主入口): mapped 校验 fail-loud(L285-288)→registry 缺省 E1(L289-292)→输入 IR 深拷贝(L293-297,D-B2-06)→快照获取(注入优先→daily_dir 自取;L299-307)→R3 门禁(L309-313)→`target_snapshot_id` 绑定(L315)→绑定循环(ABSENT 终态保留;执行器侧 A1 防御 L326-331;四级解析 L332-333)→派生循环(NO_DATA 终态保留;operand 非 RESOLVED 传导 NO_DATA L340-344;三 op_type 分派 L345-352)→executed 校验 fail-loud(L354-357,D-B2-13)→返回四键结构。

### tests/test_p03_e2eb_b2.py(1065 行,纯新增)

- fixture 注册表(L34-87): 基 8 条(带 source 字段)/CCC+GOLD_F 扩展 10 条/JP 在场变体 10 条——执行器绑定身份唯一数据源(D-B2-14)。
- 场景字面量(L89-136): 两日(D1=20261101/D2=20261102)四通道发明数值+预期值全字面量(手算,/tmp/b2_precalc.py 引擎原语预演核验后誊写,零自证)。
- 核心覆盖生成器 `write_day_files`(L159-243,D-B2-14: 运行时枚举真实 registry 按 source 路由;通用值=range 中点;场景指标显式覆写;CURVE_2S10S 蓄意缺席=A3 场景;NFP_MOM_K 等派生不在文件层重复立事实)。
- 手工快照/事实/IR 构造器(L248-309): hfact/hsnap/_pb/_pop/hand_ir/golden_ir/write_snapshot_file/quiet_build。
- 十个测试类 63 用例: T0 fixture 自检(6)/T1 黄金 E2E(11)/T2 as_of 锚定(5)/T3 引擎一致性(5)/T4 四级缺席(7)/T5 快照获取(7)/T6 门禁(5)/T7 派生操作(10)/T8 纯度接线(5)/T9 fail-loud(2)。逐类行号: T0 L313/T1 L369/T2 L472/T3 L531/T4 L615/T5 L713/T6 L804/T7 L847/T8 L1001/T9 L1040。

## §三 测试与本地CI

**本地运行(2026-11-05,python3 tests/test_p03_e2eb_b2.py): Ran 63 tests — OK(exit=0),证据包④ log。**

- 黄金路径(要点①/④): `test_values_all_literals`(D2 全 8 绑定值=V_D2 字面量: 4.25/4.50/4.33/4.58/5.04/152.75/0.8251/1.8333)/`test_op3_computed_with_maturity_disclosure`(OP-3=0.46+期限匹配披露)/`test_usdjpy_windows_equal_engine_direct`(week/mtd/ytd 三窗口=fe 直算=字面量 0.8251/1.0251/1.8333)/`test_ust_week_pp_equal_engine_direct`(+0.03/−0.08)/`test_gold_week_pct_and_level_diff_basis`(0.4098 与 basis 路径 10.0 区分)/`test_spread_equal_engine_free_literal`(=round(5.04−4.58,4))/`test_correlation_equal_cc_direct`(=cc.paired_returns+pearson=0.4675)。
- as_of 锚定(要点③): `test_d1_anchored_values`(D1 全值=V_D1,OP-3=0.40)/`test_d1_d2_no_period_mixing`(同目录两日档,值随锚点切换+观测日证明不混期)/`test_usdjpy_mtd_window_d2`(mtd=1.0251)/`test_as_of_before_any_files_refused`(早于全部文件→gate FAIL refusal)/`test_invalid_as_of_fail_loud`(垃圾日期→ValueError)。
- NO_DATA 传导(要点②): `test_op1_op2_no_data_preserved`(mapper 期 NO_DATA 终态原样保留,calc_ref 零追加)/`test_a1_executor_side_registry_defense`(注册表漂移→执行器 A1+OP-3 NO_DATA 传导)/`test_jp_present_spread_computed`(JP 在场→OP-1=−3.625/OP-2=−3.34 转 COMPUTED,B1 对照面)/`test_spread_maturity_mismatch_disclosed`(观测日不一致如实披露不混同)。
- 四级缺席: `test_mb6_curve_absent_data`(A3)/`test_mb8_mb9_absent_registry_preserved`(A1 mapper 期)/`test_a2_channel_missing_via_r1_file`+`test_a2_read_fail_variant`(A2 通道级)/`test_a4_fact_without_series`+`test_a4_window_unavailable`+`test_a4_window_field_missing`(A4 三变体)/`test_values_keys_exactly_resolved`(零填 0: values 键集=RESOLVED 集)。
- 快照获取: `test_r1_file_wins_over_s1_build`(R1 优先,S1 值 4.25≠文件值 9.99)/`test_r1_highest_revision_selected`(_v2)/`test_injected_snapshot_wins_over_daily_dir`/`test_as_of_none_binds_latest_ymd_no_wallclock`/`test_as_of_none_empty_dir_refused_no_wallclock`(禁墙钟 refusal)/`test_no_snapshot_no_dir_refused`/`test_r1_corrupt_falls_back_to_s1`(候选损坏→S1 接管)。
- 门禁: `test_gate_fail_refused_zero_partial`(FAIL→refusal+9 绑定零部分执行)/`test_gate_none_refused`/`test_gate_degraded_and_pass_allowed`/`test_injected_snapshot_not_mutated`/`test_non_dict_snapshot_refused`。
- 纯度接线(T8): `test_no_network_surface`/`test_no_collector_file_io`(零 open()/零 glob,唯一 IO=os.listdir;「global」不误伤=词边界正则)/`test_no_wall_clock`/`test_wiring_reuses_established_interfaces`(R1/R3/S1/E1/C3/C4/qir 八接线正向锁+不 import 映射器)/`test_absence_reason_no_invented_numbers`。
- fail-loud(T9): `test_invalid_mapped_ir_rejected`/`test_executed_output_sabotage_detected`(mock 注入枚举外终态→executed schema ValueError,D-B2-13)。

**负向敏感性注入(D1-D4,注入→定向红→还原→sha256 逐字节一致)**:

| 注入 | 缺陷内容 | 红(定向) | 还原核验 |
|---|---|---|---|
| D1 | `_ymd_from_as_of` 绕过 E4 严格校验(垃圾日期静默拼接) | 1 红: test_invalid_as_of_fail_loud | sha 还原一致 |
| D2 | operand 缺席传导拆除(守卫恒假) | 15 红(全部 COMPUTED 路径失效: 黄金 OP-3/JP spread/level_diff/correlation/引擎一致性等) | sha 还原一致 |
| D3 | R3 门禁旁路(`if False:`) | 3 红: test_gate_fail_refused_zero_partial/test_gate_none_refused/test_as_of_before_any_files_refused | sha 还原一致 |
| D4 | latest-ymd 枚举硬编码(锚定漂移) | 1 红: test_as_of_none_binds_latest_ymd_no_wallclock | sha 还原一致 |

模块 sha256(注入前=每次还原后): `54d1fe0c4259eb26657df37a4c20db78069839f5bf6f1cc745a7894842eba4ba`;注入中 sha 逐次漂移(c07ba2b2…/4c368233…/eea1daa2…/199bf546…),还原后 4 次均回到原值;最终全量 63 用例复跑 OK(证据包④ injections/)。

**本地CI(步骤9,.github/workflows/offline-tests.yml 同构: 全部 tests/test_*.py 排除 test_glm_live,逐套退出码)**:

- 文件总数 59(既有 58+本包新增 1);运行套件 58(排除 test_glm_live=skipped);**57 套 exit=0 + 1 套 exit=1(test_p4_fixes)= B1 基线既有红原样归因**(其日志尾部「39通过 / 4失败」,与 B1 REPORT §九登记的基线实值完全一致,零新增失败);本包新套件 test_p03_e2eb_b2 exit=0(Ran 63 tests OK)。
- 逐套退出码全表落证据包④ suite-summary.txt;要点⑤「CI 零回归」的 GitHub Actions run 证据=操作者 CHECKPOINT 派发后落 rounds/022/E2EB-WP-B2-CI-dispatch-evidence.md(执行Agent 不自行派发,合同 §五)。

## §四 逐要点证据映射表(AC-02)

| DESIGN L220 要点 | 实现/测试证据(file:line) | 运行证据 | 结论 |
|---|---|---|---|
| ① 离线单测构建 write=False 快照并执行 OP-3 | 执行器 `_acquire_snapshot` scripts/e2eb_query_executor.py:100-116(R1→S1 write=False);tests/test_p03_e2eb_b2.py:369-470(T1 黄金 E2E 经 daily_dir+trusted_root 两日合成采集档)/`test_r1_file_wins_over_s1_build`:736-745(R1/S1 分径) | T1 全绿(Ran 63 OK;证据包④ log) | 过 |
| ② OP-1/OP-2 NO_DATA result=null | 执行器 NO_DATA 终态保留(L337-338)+operand 传导(L340-344);tests `test_op1_op2_no_data_preserved`:395-403/`test_a1_executor_side_registry_defense`:625-639 | 同上 log;schema 锁 NO_DATA→result=None(qir L220-221) | 过 |
| ③ as_of 两时点锚定不混期后数据 | `_ymd_from_as_of`(L76-83)+`_acquire_snapshot`(L100-116);tests T2(L472-529): `test_d1_anchored_values`:489/`test_d1_d2_no_period_mixing`:495 D1/D2 双锚定值集 V_D1/V_D2 全字面量+观测日证明 | 同上 log | 过 |
| ④ 执行器输出与 fact_engine 直算逐值相等(硬编码预期值) | tests T3(L531-613): `test_usdjpy_windows_equal_engine_direct`:545/`test_ust_week_pp_equal_engine_direct`:560/`test_gold_week_pct_and_level_diff_basis`:575/`test_spread_equal_engine_free_literal`:590/`test_correlation_equal_cc_direct`:600(E3 三窗口/UST pp/GOLD pct+level_diff/correlation vs fe/cc 直算 vs 字面量);预演脚本 /tmp/b2_precalc.py(证据包④ precalc/) | 同上 log(7 组数值逐值相等断言) | 过 |
| ⑤ CI 零回归 | 本地 CI 同构 59 文件/58 套/57 绿+1 既有红归因(§三);GitHub Actions run=操作者 CHECKPOINT 派发(执行Agent 禁自行派发) | 证据包④ suite-summary.txt;派发证据=操作者落档 | 过(本地侧);Actions run 待派发后登记 |
| 补: R3 门禁拒绝零部分执行 | D-B2-03;tests T6(L804-845) | 同上 log | 过 |
| 补: 四级缺席 A1-A4 落位 | D-B2-04/07/08;tests T4(L615-712) | 同上 log | 过 |
| 补: 禁墙钟/纯度/接线 | D-B2-01/12;tests T5+T8(L713-802/L1001-1038) | 同上 log;D4 注入定向红 | 过 |
| 补: 输入零变异/产出 fail-loud | D-B2-06/13;tests `test_input_ir_zero_mutation`:445-453/`test_executed_output_sabotage_detected`:1048-1063 | 同上 log | 过 |

## §五 模块SHA登记

| 文件 | sha256(实现提交工作树实取,2026-11-05) |
|---|---|
| scripts/e2eb_query_executor.py | 54d1fe0c4259eb26657df37a4c20db78069839f5bf6f1cc745a7894842eba4ba |
| tests/test_p03_e2eb_b2.py | 39b4c42e3cbe0b5888b45a33173f42a677492d9159c885c50416bbae45ac5181 |
| docs/P03_E2EB_B2_REPORT.md | (本文件自身;提交前终值以工作树 sha 为准,自指豁免同 B1 先例——zip 整体 sha 于 DELIVERY §五追加行落档) |
| docs/P03_E2EB_B2_DELIVERY.md | (同上,DELIVERY §五) |

commit 链(纯线性,零 merge): 开工登记 8312889(REPORT §零/§一/§六)→ 实现提交(本 REPORT §二-§五 回填+两实现文件,SHA 见下行)→ REPORT/DELIVERY 终版提交(§七-§九 回填+DELIVERY)→ zip sha 追加提交(DELIVERY §五 zip 实测值追加行,自指豁免沿 B1/3e7c300 先例;见 git log dev/p03-e2eb-b2,证据包③+08-sidecar)。

实现提交SHA: fd36c08a83170b0c3c352b1f0da220b83abeff41

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

1. **要点①测试数据源差异**(§零(iv)已登记,此处展开): DESIGN L220①草案要求「DEV授权副本(data/daily 20261101/20261102)构建快照」,冻结合同 AC-03 承接 R014-D3 要求合成 fixture 为唯一数据源+预期值字面量硬编码;依 DESIGN L206 标题自注(「验收要点=草案,正式AC由主Agent后续轮拟定」)以冻结合同为准(与 B1 §七.1 同款先例)。实现=两日合成采集档(四通道全,结构复刻采集器输出,数值全发明)+核心覆盖生成器(D-B2-14);「数据档引用 data/daily/macro_20261102.json」以测试文件内 fixture 结构注记承接,非数据依赖。时刻: 2026-11-05T0x:xxZ UTC(证据包④ timestamps)。
2. **双层注册表纪律**: 执行器绑定身份=合成 fixture 注册表(registry 注入,8/10/10 条变体,不读真实注册表);S1 管线内部的指标身份/校验=真实 registry(fe.load_registry,sb 无注入面)——与 tests/test_snapshot.py:117-119 既有先例同构;真实注册表零数值转录(通用值=range 中点,场景值=发明字面量)。此为结构事实,非偏离,如实登记。
3. **level_diff 语义登记**(D-B2-10): DESIGN L93 仅给 op 名与「同指标两时点差」字样,operand 角色组合未定义;登记为「level 绑定+derived_window 绑定,result=level 值−E3 窗口基准值」,先登记后实现(§六),运行后未改。
4. **correlation 操作的 IR 生产面**: B1 映射器 v1 约束式规则只发射 spread(D-B1-02 恰 4 条规则登记集),不发射 correlation/level_diff 操作——本包以 hand_ir(手工 mapped IR,过 schema 自检)覆盖这两类 op 的执行语义;映射器扩展属 WP-B3+。如实登记非静默。
5. **macro 序列不经 series_store**(D-B2-11 登记): 相关性操作对 macro 通道序列结构性 NO_DATA(理由注明既有结构边界,research_history_query.py:25-27 同源登记);将 macro 序列纳入 store 须改 snapshot_builder=白名单外,登记发现不实施。
6. **fixture gate=DEGRADED 而非 PASS 的如实性**: 生成器蓄意不写 china 可选块(南向/两融/估值→SB_FLOW/MARGIN_BAL/SH_PE 非核心缺席)+CURVE_2S10S 缺席(A3 场景)+BTC 观测滞后 3 天超其 2 天窗(质量 DEGRADED,如实)→S1 构建快照 gate=DEGRADED(R3 放行);gate=PASS 路径经 R1 文件快照与注入快照覆盖(T5/T6)。断言字面量 `DEGRADED` 即 fixture 自检的一部分(T0)。
7. **test_p4_fixes 本地既有红**: 与 B1 基线登记同款 4 项(monthly_review 数据块,「39通过/4失败」),本包零 M/D 纯新增、与该套件零导入关系,归因在案(§三);Actions run 证据=操作者 CHECKPOINT 派发后落档(合同 §五,执行Agent 不自行 dispatch)。
8. **临时工具脚本**: /tmp/b2_precalc.py(预期值引擎原语预演)/tmp/b2_inject.py(D1-D4 注入器)/tmp/b2_run_ci.py(本地 CI runner)均为一次性工具,复制入证据包(④ precalc//④ injections//④ ci-runner/),不入白名单。
9. 无其他偏离;未触发情形(b)上游漂移(套件数 58=57+1 与 B1 终态+1 恰一致);未触发情形(c)不可得(零真实数据面,§零(iv) 零运行产物登记);未触发 PREEMPT-STOP。

## §八 合同逐条自检(AC-01~AC-07)

| AC | 自评 | 一句证据指引 |
|---|---|---|
| AC-01 规格抄录与登记正确性 | PASS | §零(i)逐字抄录(L216-220,基线工作树实读)可直读对照;清单 k=4 逐条附依据;与 git ls-files 零重合(§零(iii));要点①数据源差异公开登记(§七.1) |
| AC-02 逐要点交付与证据映射 | PASS | §四映射表要点①-⑤全落+4 补充行,file:line 实取;参数登记 D-B2-01..14=常量=断言一致(§六/§二);零运行产物登记(§零(iv)) |
| AC-03 测试与确定性验证 | PASS(生效) | 63 用例零网络/合成 fixture(四通道采集档+生成器)/预期值字面量硬编码(手算+预演核验);本地: 新套件 exit=0,全量 59 文件 58 套 57 绿+1 既有红归因(§三);负向敏感性 D1-D4 定向红(1/15/3/1)后还原逐字节一致 |
| AC-04 引用真实性与注入边界 | PASS | §一 file:line 逐条可寻(基线工作树实读);「注入快照」字样仅用于手工快照测试面(依赖注入语义,D-B2-01 登记)非证据伪造;无跨支引用;无引擎路径依赖(全仓可寻) |
| AC-05 范围/分支/生产隔离 | PASS | diff name-status=纯 A 行(白名单 k=4,零 M/D);分支自 3e7c300 切出+纯线性零 merge;reflog 无 reset/amend;零网络 import(T8 源码锁);fact_engine/snapshot_builder 既有函数签名零改动(DESIGN L218,复用调用);LIVE 零写入(取证见证据包③);main 零触碰 |
| AC-06 CI与证据包 | PASS(本地侧)/CI待操作者 | 证据包八类成员+SHA256SUMS 落 /tmp/p03-e2eb-b2-evidence/;DELIVERY 五节+漂移维护策略专节;CI dispatch=操作者 CHECKPOINT(执行Agent 未自行 dispatch),登记件路径 rounds/022/E2EB-WP-B2-CI-dispatch-evidence.md |
| AC-07 研究纪律与使用边界 | PASS | 模块零 open()/零 glob(T8 源码锁,唯一 IO=os.listdir 快照层文件名);禁墙钟(T8+D4 注入定向红);缺值零填 0(四级缺席+values 键集=RESOLVED 集断言);门禁 FAIL 拒答零部分执行(D-B2-03+D3 注入定向红);零 GLM/零凭证/零付费;白名单外需求零实施(登记发现: §七.5) |

## §九 提交前数值标注六项自检清单(§5.3,强制)

双文档(REPORT+DELIVERY)全文扫描,计数/统计类数值逐个二选一标注;[实取]项已回工作树复核(2026-11-05):

| 数值 | 值 | 标注 |
|---|---|---|
| 白名单文件数 k | 4 | [实取·来源: 本REPORT §零(ii)清单] |
| DESIGN WP-B2行行号 | L216-220 | [实取·来源: docs/P03_E2EB_DESIGN.md 基线工作树,2026-11-04实读] |
| 专项测试用例数 | 63 | [实取·来源: 本地运行"Ran 63 tests",证据包④log;类计数T0..T9=6/11/5/5/7/7/5/10/5/2] |
| fixture注册表条数(基/CCC变体/JP变体) | 8/10/10 | [实取·来源: tests L34-87构造字面量] |
| 合成场景日数/快照日 | 2/20261101+20261102 | [实取·来源: tests DAY_D1/DAY_D2] |
| 黄金IR绑定数/派生数(承接B1) | 11/3 | [实取·来源: B1黄金字面量+T1终态断言] |
| 核心覆盖core数(生成器) | 32 | [实取·来源: config/metric_registry.json criticality=core计数,2026-11-05] |
| 真实注册表指标总数 | 81 | [实取·来源: 同上计数;与B1 REPORT §九一致] |
| 负向敏感性注入 | D1-D4红1/15/3/1 | [实取·来源: 本地注入实测,§三] |
| 模块sha256(注入前=还原后) | 54d1fe0c…a4ba | [实取·来源: shasum -a 256 4次比对,§三/§五] |
| 测试文件总数/CI套件数 | 59/58 | [实取·来源: 本地CI同构运行,证据包④suite-summary.txt] |
| 基线CI套件数(B1终态) | 57 | [对照·来源: B1 REPORT §九58文件57套件;本包59=58+1,58套=57+1一致] |
| 既有红失败项 | 4 | [实取·来源: 证据包④logs/test_p4_fixes.log「39通过/4失败」,与B1基线同款] |
| 执行器/测试行数 | 359/1065 | [实取·来源: wc -l,2026-11-05] |
| 参数登记项数 | 承接P-01..14+D-B1-01/12/13;本包D-B2-01..14 | [实取·来源: 本REPORT §六] |
| DELIVERY节数 | 5+专节1 | [实取·来源: docs/P03_E2EB_B2_DELIVERY.md结构] |
| 证据包成员类别 | 8 | [实取·来源: 合同附录A §六②最低集;证据包目录实测] |
| 实现提交SHA | fd36c08a83170b0c3c352b1f0da220b83abeff41 | [实取·来源: git rev-parse fd36c08,已回填§五] |

日期/SHA/行号按边界出圈登记: 本文件头部时区声明(UTC);DESIGN行号=基线工作树(3e7c300)版本;无[示意]数值留档。
