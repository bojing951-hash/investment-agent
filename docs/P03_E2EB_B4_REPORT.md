# IA-P03-E2EB-WP-B4 REPORT — 共享研究档案与查询历史(append-only)

> 包: IA-P03-E2EB-WP-B4(E2E-B 第 4 实现包) · 执行Agent: Agent 3
> 分支: `dev/p03-e2eb-b4`(自基线 b5c33f85c42e12b4f04e2a80faa1131244997c70 切出;本包无并入步,设计三件经 B1 指定并入步已在基线祖先谱系,开工步骤4实测核验)
> 合同: IA-P03-E2EB-WP-B4-AC-v1.0(冻结,占位符已实值化)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY/B1/B2/E2E-A 在场件行号一律为**基线工作树(b5c33f85)实读**行号(2026-11-04T22:3xZ 实取);提示词注入内容引用一律标注「注入摘要,非工作树实读」。

---

## §零 规格抄录与交付面登记(开工首步,AC-01)

### (i) DESIGN §六 WP-B4 行四要素逐字抄录

实读 `docs/P03_E2EB_DESIGN.md`(基线工作树),WP-B4 行位于 L228-232,逐字抄录如下:

```text
L228: **WP-B4 共享研究档案与查询历史(append-only)**
L229: - 目标: 落地§4.1: query_history集合、ID引用约定(query_id/task_id/origin_query_id/promoted_to_task_id)、snapshot_id+digest内容级绑定。
L230: - 范围: 档案存储模块(append-only文件族);E2E-A任务集合字段以E2E-A冻结合同为准(本包只建模式B侧+引用约定)。
L231: - 依赖: WP-B1(IR即首类记录)。
L232: - 验收要点草案: ①append-only不可变测试: 重复写入/改写被拒(工件: 测试文件) ②ID格式与交叉引用字段校验(工件: 测试文件) ③digest绑定: 篡改快照后档案校验拒绝(工件: 测试+R5机制) ④CI零回归(工件: run ID)。
```

四要素齐备(目标/范围/依赖/验收要点),无缺失。依赖列核验: WP-B1 已落地(基线 b5c33f85 工作树 `scripts/e2eb_query_ir.py`/`scripts/e2eb_query_mapper.py`/`tests/test_p03_e2eb_b1.py` 在场实读;依赖列「=WP-B1(IR即首类记录)」与冻结合同附录A §零生效前置一致,不要求并入他支、不含 GLM/网络/新数据源凭证要求 → 无情形(d)停止条件。

### (ii) 交付文件清单(k=4,登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据 |
|---|---|---|
| 1 | `scripts/research_archive.py` | DESIGN L230「档案存储模块」恰 1 个代码模块+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」;文件名依 DESIGN L185「单一共享档案文件族(如`research_archive/`下分集合)」命名族+既有 research_* 命名先例(scripts/research_task_manager.py 等) |
| 2 | `tests/test_p03_e2eb_b4.py` | DESIGN L232①②③工件「测试文件」+合同附录A §零(ii)「含代码则必含 tests/test_p03_e2eb_b4.py」 |
| 3 | `docs/P03_E2EB_B4_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P03_E2EB_B4_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L232④「CI 零回归」证据落点=DELIVERY §五 |

### (iii) 结构约束核验

- 与 `git ls-files` 输出零重合: 4 路径均为纯新增(开工时实读 `git ls-files scripts/ tests/ docs/` 无一存在;B1 交付件=e2eb_query_ir.py/e2eb_query_mapper.py/test_p03_e2eb_b1.py/P03_E2EB_B1_*.md,B2 交付件=e2eb_query_executor.py/test_p03_e2eb_b2.py/P03_E2EB_B2_*.md,E2E-A 六件与 G1-G3 交付件均与本清单零重合)✓
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p03_e2eb_b4.py)✓
- 推导无越界: 范围列「档案存储模块(append-only文件族)」恰 1 个代码模块 → scripts/ 恰 1 文件;DESIGN L232 工件未另指定模块文件名,依固定推导规则命名;未引入 DESIGN 依据外文件 ✓

### (iv) 运行产物边界登记

WP-B4 验收要点(L232①-④)工件全部为离线测试文件/CI run 登记类;范围列(L230)为档案存储模块本身,DESIGN 未为 WP-B4 指定编排入口或真实运行要求(端到端走查固化属 WP-B5,L234-238)→ 本包登记「**零运行产物**」: data/research/ 零真实写入(测试全合成 fixture 写 tempdir,见 §六 D-B4-12),data/daily 与既有快照零读取零写入。§4.1 引用约定与档案机制的全部可离线验证面由 tests/test_p03_e2eb_b4.py 覆盖(§四映射表)。

---

## §一 前置实读登记(file:line)

(实现前实读,全部为基线工作树(b5c33f85)实取,非注入摘要)

| 对象 | 登记 |
|---|---|
| DESIGN §六 WP-B4 行 | docs/P03_E2EB_DESIGN.md:228-232(§零(i) 逐字抄录) |
| DESIGN §4.1 共享档案衔接 | 同文件:180-185(快照ID+digest 绑定 L182;task_id/query_id 格式 L183;origin_query_id/promoted_to_task_id 交叉引用 L184;档案载体=文件族分集合 L185) |
| DESIGN §四 E2E-A 对齐 | 同文件:167-185(行3 升级路径 origin_query_id L173;行4 任务外键 task_id L174;行5 查询记录不带 falsifiable_conditions L175;行6 query_history append-only/query_id 单调 L176) |
| DESIGN §七 红线 | 同文件:244-249(§七1 快照纪律 L246;§七2 LIVE 禁写 L247;§七4 数据不足不填0 L249) |
| B1 IR 模块(承接) | scripts/e2eb_query_ir.py:51(QUERY_ID_RE)/55(SNAPSHOT_ID_RE)/56-57(ISO_DATE_PREFIX_RE/AS_OF_RE)/71-85(make_query_id;L73-75「同日唯一性计数与落盘属 WP-B4 档案」承接注释)/248-304(validate_ir 双阶段) |
| B1 参数登记 D-B1-10 | docs/P03_E2EB_B1_REPORT.md:156(query_id 生成;「同日单调计数与落盘属 WP-B4 档案」) |
| R5 快照内容指纹 | scripts/research_provenance.py:1297-1301(digest_snapshot=canonical JSON sha256 前16位) |
| R1 身份纪律先例 | scripts/research_provenance.py:1271-1277(内部 snapshot_id↔文件名版本一致,IA-DEF-007) |
| FIX2-04 版本表示规范 | scripts/research_provenance.py:1212-1227(_version_of: _v0/_v1/前导零非规范十进制一律非法) |
| FIX-01 内容绑定重算纪律 | scripts/research_provenance.py:1304-1308(digest_file docstring: 内容绑定必须读实际文件重算,不得采 sidecar 声明值) |
| E2E-A 档案机制(同构先例) | scripts/research_task_manager.py:32-34(DEFAULT_OUT_DIR=data/research/)/48-53(make_task_id 实况形态 RT-{start}~{end}-{rule}-{hash8})/135-156(save_task append-only+原子写 .tmp+os.replace)/159-173(save_detection_series 序号递增永不覆盖) |
| G3 RT-前缀族先例 | scripts/glm_conclusion_integrator.py:80-84(_RT_PREFIX_RE=^RT- 注「E2E-A 任务(rtm.py:53 形态)」;_QB_PREFIX_RE=^QB-)/518-522(task_id/origin_query_id 形态校验) |
| B2 执行器产出结构(消费面) | scripts/e2eb_query_executor.py:70-73(_refusal 结构)/267-283(execute_query 返回 {ir,values,snapshot_id,gate_status} 或 refusal 四键) |
| E2E-A 档案在场实据 | data/research/RT-2026-06-30~2026-09-30-RD-DIV-001-17788777.json+detection_series_*.json(E2E-A 自产档案;task_id 实况形态佐证;data/ 目录 gitignored,.gitignore:1) |

---

## §二 实现(逐文件)

**实现提交见 §五 commit 链;以下行号为实现提交(08f0dcc)工作树实取(2026-11-05)。**

### scripts/research_archive.py(395 行,纯新增)

- 常量层(L39-60): ARCHIVE_FAMILY/ARCHIVE_COLLECTION/RECORD_TYPE_QUERY/MODE_B_LITERAL(L39-42,D-B4-01/03)/DEFAULT_ARCHIVE_DIR(L44-46,data/research/research_archive)/QUERY_RECORD_KEYS 十三键(L48-51)/TASK_REF_RE=`^RT-\S+$`(L53,D-B4-02)/DIGEST_RE(L54)/_QUERY_FILE_RE/_SNAPSHOT_ID_PARTS_RE(L55-56)/三状态常量(L58-60)。
- `validate_id_conventions`(L67-88,D-B4-07;要点②直测面): 四 ID 参数各自非 None 时校验——query_id/origin_query_id 严格 QB 格(复用 qir.QUERY_ID_RE),task_id/promoted_to_task_id RT-前缀族。
- `parse_snapshot_id`(L96-107,D-B4-03): research_snapshot_YYYYMMDD[_vN] 规范分解;_v0/_v1/前导零→None(FIX2-04 同源,rp._version_of:1212-1227 纪律)。
- `_snapshot_filename`/`_load_snapshot_for_binding`(L115-141,D-B4-08): **唯一快照读取面**——文件名仅由 snapshot_id 规范分解派生(research_snapshot_*.json),结构性不可达原始采集档(AC-07.1);文件缺失/JSON 损坏/内部 snapshot_id 不符→结构化原因(R1 身份纪律同款,rp.select_snapshot:1271-1277 先例)。
- `_detect_ir_stage`(L151-161,D-B4-05①): qir.validate_ir executed→mapped 双阶段探测,双败 ValueError fail-loud。
- `build_answer_summary`(L164-183,D-B4-04): counts(sorted 键稳定序)+values(仅 execution 成功)+refusal(B2 D-B2-03 原样上浮)确定性摘要。
- `validate_query_record`(L191-247,D-B4-03/07): 记录级全链——键集/record_type 字面量/query_id 严格格式+日期段一致性(L211-214)/echo 四字段(L235-238)/IR 阶段校验复用 qir/snapshot_id 规范/digest 十六位格式/promoted_to_task_id RT-前缀族/archived_at ISO;返回 issues 不抛校验异常。
- `list_query_records`/`_same_day_max_seq`/`allocate_query_id`(L258-291,D-B4-06/09): 纯目录扫描(零墙钟);配号=qir.make_query_id(created_at, seq=同日max+1)(D-B1-10 承接面)。
- `append_query_record`(L293-344,D-B4-05;要点①主入口): 八步链(IR 阶段探测 L301→snapshot 注入绑定+target 一致性 L302-309→R5 digest 模块内重算 L310→execution.ir 一致性 L311-312→记录构造 L315-327→validate_query_record fail-loud L328-330→唯一性 L333-334(同 id 文件在场=**重复写入/改写一律拒**)→同日单调 L337-338(≤max 拒,空洞合法)→原子落盘 L339-343 .tmp+os.replace);返回 (status, path);零 update/delete API。
- `load_query_record`/`verify_query_record`/`verify_archive`(L349-395,D-B4-08/09;要点③): 读回(缺档 FileNotFoundError)/单档验证(记录级校验+快照解析+R5 digest 复算对照 L373-377,不匹配→「digest不匹配(快照内容与档案绑定漂移/篡改嫌疑)」)/全档案逐档复核汇总 {n_records, n_ok, failures}。

### tests/test_p03_e2eb_b4.py(675 行,纯新增)

- fixture 层(L33-152): SNAP_A/SNAP_B_V2(手造最小快照)+IR_M/IR_E(mapped/executed 双态手造最小 IR,过 qir.validate_ir 双阶段)+EXEC_OK/EXEC_REFUSAL(B2 产出结构同构);预期值字面量层(L127-146): L_DIGEST_A=`756c258d9943841d`/L_DIGEST_B_V2=`2418e26ca8294e02`(R5 真实管线预计算誊写,/tmp/b4_precalc.py hashlib 独立旁证)/三条摘要字面量/L_REFUSAL/L_ARCHIVED_AT。
- 七类 50 用例: T0 fixture 自检(2)/T1 append-only(8)/T2 ID 约定(6)/T3 digest 绑定(10)/T4 schema 与摘要(14)/T5 复用纯度锁(6)/T6 fail-loud(4)。逐类行号: T0 L211/T1 L225/T2 L312/T3 L370/T4 L491/T5 L609/T6 L653。
- 纯度锁(T5): 复用面正向锁(import e2eb_query_ir/research_provenance+rp.digest_snapshot 调用;digest 算法零复制=源码无 `hexdigest()[:16]`)/原始采集档文件名模式零存在(macro_2/global_2/china_market/rate_economy)/open( 面恰 3 处白名单函数/零网络 import/公共 API 白名单(禁 update/delete 族)/DEFAULT_ARCHIVE_DIR 隔离(LIVE 路径零涉)。

---

## §三 测试与本地CI

**本地运行(2026-11-05,python3 tests/test_p03_e2eb_b4.py): Ran 50 tests — OK(exit=0),证据包④ log。**

**负向敏感性注入(D1-D4,真实注入→定向红→还原→sha256 逐字节一致;注入器 /tmp/b4_inject.py 入证据包④ injections/)**:

| 注入 | 缺陷内容 | 红(定向) | 还原核验 |
|---|---|---|---|
| D1 | 重复写入拒绝拆除(`if False and os.path.exists`) | 3 红: test_duplicate_append_identical_rejected_bytes_unchanged/test_duplicate_append_modified_content_rejected/test_append_never_overwrites_precreated_file | sha 还原一致 |
| D2 | digest 绑定旁路(存常数 16 零指纹) | 4 红: test_append_stores_r5_digest_literal/test_verify_ok_untampered/test_snapshot_v2_filename_resolution/test_append_mapped_written_and_readable | sha 还原一致 |
| D3 | 同日单调检查拆除(守卫恒假) | 1 红: test_monotonic_seq_enforced | sha 还原一致 |
| D4 | query_id↔created_at 日期一致性拆除 | 1 红: test_record_query_id_date_consistency | sha 还原一致 |

模块 sha256(注入前=每次还原后): `635d9a3e820816c3cd47d3531faff3fced2f8b156fdf8e7751e841498604aeb3`;还原态全量 50 用例复跑 OK(证据包④ injections/)。

**本地CI(步骤9,.github/workflows/offline-tests.yml 同构: 全部 tests/test_*.py 排除 test_glm_live,逐套退出码;runner /tmp/b4_run_ci.py 入证据包④ ci-runner/)**:

- 文件总数 63(基线 b5c33f85 既有 62+本包新增 1);运行套件 62(排除 test_glm_live=skipped);**61 套 exit=0 + 1 套 exit=1(test_p4_fixes)= B1/B2/B3 基线既有红原样归因**(其尾部「39通过 / 4失败」,与 B1/B2 REPORT §七登记的基线实值完全一致;DEV data/daily 真实副本 20261101-1104 在场触发 real 分支无 9 月数据,CI fresh checkout 绿,与本包零导入关系);本包新套件 test_p03_e2eb_b4 exit=0(Ran 50 tests OK)。
- **与冻结合同「58+新增1=59」对照不符,如实登记(§七.5)**: 冻结值 58=B2 分支谱系计数(B2 尖端 59 test 文件−1 跳过);main 尖端 b5c33f85 经两次 merge(B1/B2)合入 main 侧 G1/G2/G3 三个 GLM 测试文件(git diff fe04691..b5c33f85 -- tests/ 实取恰 3 行 A),故 62+1=63 文件/62 运行套件为真实计数;零回归判据成立(B2 时点 57 绿+1 红 → 本包 61 绿+1 红,差集=+3 GLM 绿+本包绿)。CI Actions run 证据=操作者 CHECKPOINT 派发后落 rounds/024/E2EB-WP-B4-CI-dispatch-evidence.md(执行Agent 不自行派发,合同 §五)。
- 逐套退出码全表落证据包④ suite-summary.txt。

---

## §四 逐要点证据映射表(AC-02)

| DESIGN L232 要点 | 实现/测试证据(file:line) | 运行证据 | 结论 |
|---|---|---|---|
| ① append-only 不可变: 重复写入/改写被拒 | append 唯一性拒绝链 scripts/research_archive.py:333-334+同日单调拒绝 L337-338+状态常量 L58-60+零改写/删除 API(公共面仅 §二清单函数);tests T1(test_duplicate_append_identical_rejected_bytes_unchanged/test_duplicate_append_modified_content_rejected/test_append_never_overwrites_precreated_file/test_no_rewrite_or_delete_api/test_monotonic_seq_enforced/test_cross_day_independent_sequence) | T1 全绿+D1 注入定向红 3(证据包④) | 过 |
| ② ID 格式与交叉引用字段校验 | validate_id_conventions L67-88(四 ID)+validate_query_record L191-247(query_id 严格格+日期段一致性 L211-214+promoted_to_task_id RT-前缀族+echo L235-238);tests T2 六用例(含 DESIGN L183 严格格与 E2E-A 实况形态双合法族) | T2 全绿+D4 注入定向红 1 | 过 |
| ③ digest 绑定: 篡改快照后档案校验拒绝(工件: 测试+R5机制) | digest=rp.digest_snapshot 模块内重算 L310(R5 复用 rp:1297-1301,FIX-01 纪律,API 无 digest 入参)+verify_query_record digest 复算对照 L373-377;tests T3 十用例(tampered/missing/corrupt/身份不符/错误 digest/非规范 snapshot_id/v2 解析) | T3 全绿+D2 注入定向红 4 | 过 |
| ④ CI 零回归 | 本地 CI 同构 63 文件/62 套/61 绿+1 既有红归因(§三);Actions run=操作者 CHECKPOINT 派发(执行Agent 禁自行派发) | 证据包④ suite-summary.txt;派发证据=操作者落档 rounds/024/E2EB-WP-B4-CI-dispatch-evidence.md | 过(本地侧);Actions run 待派发后登记 |
| 补: §4.1 引用约定四 ID 全落位 | D-B4-02;T2 全覆盖 | 同上 | 过 |
| 补: 快照引用=完整 snapshot_id+16 位指纹内容级绑定(L182) | QUERY_RECORD_KEYS 携双字段+D-B4-03;T3/T4 | 同上 | 过 |
| 补: query_id 同日单调/跨日独立+配号(L183,D-B1-10 承接) | allocate_query_id L282-291+append 单调拒绝 L337-338;T1 test_monotonic_seq_enforced/test_cross_day_independent_sequence/test_allocate_query_id_scans_existing | 同上+D3 注入定向红 1 | 过 |
| 补: 记录不可变不可删改(§四行6) | 零 update/delete API;T1 test_no_rewrite_or_delete_api/T5 test_module_api_surface_whitelist | 同上 | 过 |
| 补: 作答摘要确定性(L185「IR+作答摘要」) | build_answer_summary L164-183;T4 三摘要字面量用例 | 同上 | 过 |
| 补: 查询记录不设 falsifiable_conditions(§四行5) | QUERY_RECORD_KEYS 无该键(D-B4-03);T4 键集用例 | 同上 | 过 |

---

## §五 模块SHA登记

| 文件 | sha256(实现提交 08f0dcc 工作树实取,2026-11-05) |
|---|---|
| scripts/research_archive.py | 635d9a3e820816c3cd47d3531faff3fced2f8b156fdf8e7751e841498604aeb3 |
| tests/test_p03_e2eb_b4.py | f543369ce04f6e6a79b39743a7fad54727675faaac7595fdcd1324d677ef4d0f |
| docs/P03_E2EB_B4_REPORT.md | (本文件自身;提交前终值以工作树 sha 为准,自指豁免同 B1/B2 先例——zip 整体 sha 于 DELIVERY §五追加行落档) |
| docs/P03_E2EB_B4_DELIVERY.md | (同上,DELIVERY §五) |

commit 链(纯线性,零 merge): 开工登记 5e383e3(REPORT §零/§一/§六+D-B4-02 实现期收紧注记)→ 实现提交 08f0dcc(两实现文件,SHA 见上表)→ REPORT/DELIVERY 终版提交(本 REPORT §二-§五/§七-§九 回填+DELIVERY)→ zip sha 追加提交(DELIVERY §五 zip 实测值追加行,自指豁免沿 B1/B2 先例;终态 SHA 与最终 ls-remote 见证据目录 08-sidecar/final-state.txt,zip 外)。

---

## §六 实现参数与决策点登记(先登记后运行,运行后禁回改)

**承接 B1/B2 参数**(docs/P03_E2EB_B1_REPORT.md §六 / docs/P03_E2EB_B2_REPORT.md §六,运行后已禁改;本包作为下游消费面原样承接): P-01..P-14(IR schema 常量)/D-B1-01(PENDING_EXECUTION 哨兵双阶段语义)/D-B1-10(query_id=QB-YYYYMMDD-NNN,同日单调计数与落盘属 WP-B4 档案——本包承接面)/D-B2-03(执行器结构化 refusal {ir,values,snapshot_id,gate_status,refusal})/D-B2-06(执行器返回 values=仅 RESOLVED 绑定)。

**本包登记型决策点**:

| # | 决策点 | 登记内容(运行前登记) |
|---|---|---|
| D-B4-01 | 档案载体与路径 | 单一共享档案文件族=「实现包定路径」授权面(DESIGN L185「实现与路径最终由实现包定,本设计固定引用约定」);落 `<archive_root>/research_archive/query_history/{query_id}.json`,一记录一文件;默认 archive_root=DEV 仓 `data/research/`(E2E-A DEFAULT_OUT_DIR 同源根,rtm.py:32-34);原子写=path+'.tmp'+os.replace(rtm.py:152-155 同构);**本包只建模式B侧**(research_tasks/anomaly_events 集合目录不建不写,L230「本包只建模式B侧+引用约定」;E2E-A 档案留其既有 data/research/ 根存储零触碰) |
| D-B4-02 | ID 引用约定 | ①query_id=QB-YYYYMMDD-NNN 严格格式,**复用** qir.QUERY_ID_RE(禁复制);②任务引用(promoted_to_task_id)=**RT- 前缀族** `^RT-\S+$`(非空白余部;G3 在场先例 glm_conclusion_integrator.py:82「E2E-A 任务(rtm.py:53 形态)」;DESIGN L183 RT-YYYYMMDD-NNN 为其严格子集;E2E-A 实况 task_id=RT-{start}~{end}-{rule}-{hash8},rtm.py:48-53+data/research 在场档佐证——DESIGN §四头部「冲突由后续包登记型修订承接」→本包登记发现(§七.2)不擅改设计;**实现期一次性收紧**: 草案 `^RT-.+$`→`^RT-\S+$` 以拒空白余部尾随 id,发生于任何真实运行/测试定稿前,非运行后回改,§七.4 登记);③origin_query_id=query_id 同严格格式(模式B查询恒由 B1 make_query_id 产格,qir.QUERY_ID_RE);④一致性规则: record.query_id 的 YYYYMMDD 段==ir.created_at 前10字符日期段(B1 make_query_id 派生一致性);⑤同日序列各自独立计数(L183) |
| D-B4-03 | query_history 记录 schema | 键集=(record_type,query_id,created_at,mode,question_text,as_of,snapshot_id,digest_snapshot,ir,ir_stage,answer_summary,promoted_to_task_id,archived_at);record_type 字面量"query_history"(L185 集合名);mode 字面量"B"(IR L59 透传);created_at/mode/question_text/as_of 四 echo 字段必须与 ir 同名字段相等(记录=IR+绑定+摘要,echo 防分叉);snapshot_id=规范 research_snapshot_YYYYMMDD[_vN](vN≥2 规范十进制,_v0/_v1/前导零非规范一律拒绝,FIX2-04 纪律同源 rp._version_of:1212-1227);digest_snapshot=R5 十六位小写指纹(格式锁 `^[0-9a-f]{16}$`);promoted_to_task_id∈null∪RT-前缀族;archived_at=落档时刻 UTC ISO 秒(缺省 now,测试显式注入;B1 created_at 缺省 now 同款先例)。**查询记录不设 falsifiable_conditions**(DESIGN §四行5「模式B查询记录无预测语义,不设该字段」) |
| D-B4-04 | answer_summary 确定性摘要 | `{ir_stage, refusal, binding_status_counts, op_status_counts, n_unresolved, values}`;counts=对 IR metric_bindings/derived_operations 各 status 计数(sorted 键稳定序);values=execution 成功时执行器 values 映射原样并入(仅 RESOLVED 绑定,B2 D-B2-06 语义);refusal=execution 为拒绝结构时其 refusal 原因原样上浮(B2 D-B2-03);摘要为计数/映射结构,无数值编造面(缺零填0纪律零涉及) |
| D-B4-05 | append 语义 | `append_query_record(ir, *, snapshot, archive_dir=None, execution=None, promoted_to_task_id=None, archived_at=None)` → `(status, path)`;校验链=①IR 阶段探测(qir.validate_ir 双阶段: executed 过→executed;否则 mapped 过→mapped;双败→ValueError fail-loud)②snapshot 注入绑定(须非空 dict 且 snapshot_id 在场且规范;ir.target_snapshot_id 非空时必==snapshot.snapshot_id,mapped 期 None=绑定调用方注入快照)③digest=rp.digest_snapshot(snapshot) **模块内重算**(FIX-01 同源纪律: 内容绑定必实测重算,禁采调用方声明值;API 无 digest 入参)④execution 一致性(execution 携 ir 键时必与归档 ir 相等,不等→ValueError)⑤记录构造(echo+绑定+摘要)⑥validate_query_record 全链(issues 非空→ValueError)⑦同日单调+唯一性(见 D-B4-06)⑧原子落盘;status∈{"written","rejected-duplicate-query-id","rejected-non-monotonic-seq"}(结构化拒绝合法返回非异常,调用方可路由;schema 违规=异常 fail-loud);**重复写入与改写一律拒**(同 query_id 文件在场→rejected,不区分内容是否相同——要点①「重复写入/改写被拒」严格读法;与 E2E-A REPLAY_POLICY 幂等跳过分歧如实登记: 查询记录无 E2E-A 任务同窗同参确定性指纹语义,幂等跳过将使「重复写入」静默成功,与要点①字面冲突→选严格拒绝,§七.3);零 update/delete API(记录不可变不可删改,§四行6);既有档字节零触碰 |
| D-B4-06 | 同日单调与配号 | `_same_day_max_seq`=枚举集合目录 `^QB-(\d{8})-(\d{3})\.json$` 取同日最大 N(纯目录扫描零墙钟);新记录 seq 须>同日 max(单调,允许空洞——单调≠连续;§四行6「query_id单调」);跨日恒新序列(L183);`allocate_query_id(created_at, archive_dir)`=qir.make_query_id(created_at, seq=max+1)(D-B1-10「同日单调计数与落盘属 WP-B4 档案」承接面;空目录→seq 1) |
| D-B4-07 | 校验面 API | `validate_id_conventions(*, query_id=None, origin_query_id=None, task_id=None, promoted_to_task_id=None)`→issues(四 ID 各自非 None 时校验,要点②直测面;origin/严格 QB 格、task/promoted/RT-前缀族);`validate_query_record(record)`→issues(记录级全链: 键集/字面量/echo/ID 格式与日期一致性/IR 阶段校验/digest 格式);返回 issues 列表(qir 风格,空=合法),不抛校验异常;append 内部消费时 fail-loud |
| D-B4-08 | 验证与快照绑定复核 | `verify_query_record(record|query_id, snapshot_dir)`→`(ok, issues)`: 记录级校验+快照解析+digest 复算对照;快照解析=按 snapshot_id 规范分解派生文件名(base=research_snapshot_{ymd}.json;vN≥2=research_snapshot_{ymd}_v{N}.json)于 snapshot_dir 加载;文件缺失/JSON 损坏→issues;内部 snapshot_id 必与引用一致(R1 同款身份纪律,rp.select_snapshot:1271-1277 先例);digest 复算≠档案登记值→「digest不匹配(快照内容与档案绑定漂移/篡改嫌疑)」(要点③);`verify_archive(archive_dir, snapshot_dir)`→`{n_records, n_ok, failures}`(逐档复核汇总);**解析面仅打开由 snapshot_id 规范分解派生的 research_snapshot_*.json 文件名,结构性不可达原始采集档**(AC-07.1;纯度锁测试 §三 T5) |
| D-B4-09 | 读回 API | `load_query_record(query_id, archive_dir=None)`(缺档 FileNotFoundError);`list_query_records(archive_dir, ymd=None)`(排序返回 query_id 列表,ymd 过滤同日子集) |
| D-B4-10 | 复用面(禁复制分叉) | qir.QUERY_ID_RE/SNAPSHOT_ID_RE/ISO_DATE_PREFIX_RE/AS_OF_RE/validate_ir/make_query_id(B1);rp.digest_snapshot(R5,rp:1297-1301);不 import B1 映射器/B2 执行器(档案消费其产出物面——IR dict 与 execution dict——不依赖其内部);rtm 原子写/一档一文件模式=机制同构非逻辑复制 |
| D-B4-11 | 网络与墙钟 | 零网络(import 面=纯标准库 os/re/json/sys/datetime+qir/rp 既有依赖);archived_at 缺省=datetime.now(timezone.utc)(E2E-A build_task created_at 同款,rtm.py:59),确定性测试显式注入;allocate/append 的 seq 决策零墙钟(纯目录扫描) |
| D-B4-12 | 测试数据纪律(R014-D3/R022 承接) | 全合成 fixture: 手造最小快照 dict(带 snapshot_id/target_date/gate_a/facts)与最小 IR(mapped/executed 双态,过 qir.validate_ir)写 tempfile.TemporaryDirectory;预期值字面量硬编码(快照 digest 十六位字面量预计算誊写、状态串/计数/拒绝原因字面量,不从被测模块导入计算);零真实数据档读取(不读 data/daily 与 data/research 任何真实档);fixture→预期值映射逐断言组登记 DELIVERY 专节 |

以上参数于任何测试运行之前登记(本节先于 §二/§三 实现与运行落盘);运行后禁回改。

---

## §七 偏离与如实声明

1. **DESIGN §4.1 RT 严格格与 E2E-A 实况形态分歧(登记型发现,处置权操作者)**: DESIGN L183 任务引用严格格=RT-YYYYMMDD-NNN;E2E-A 实况 task_id=RT-{start}~{end}-{rule}-{hash8}(rtm.py:48-53+data/research 在场档 RT-2026-06-30~2026-09-30-RD-DIV-001-17788777.json 实据)。若按 L183 严格格实现,E2E-A 既有任务 id 全部非法,promoted_to_task_id 交叉引用结构性断裂。本包采 **RT- 前缀族 `^RT-\S+$`**(G3 在场先例 glm_conclusion_integrator.py:80-84 同款先例,L183 严格格为其真子集——双合法族)。依 DESIGN §四头部「冲突由后续包登记型修订承接」登记为发现,**不擅改设计**;建议操作者以登记型修订将 §4.1 L183 任务引用格式行更新为前缀族表述(与 §四行4「任务外键 task_id」的 E2E-A 对齐语义一致)。
2. **重复写入语义选严格拒绝,与 E2E-A 幂等跳过分歧(登记型)**: E2E-A rtm REPLAY_POLICY 对同窗同参任务幂等跳过(已存在则不重写);本包对同 query_id 在场文件一律 `rejected-duplicate-query-id`,不区分内容异同。理由: 要点①字面「重复写入/改写被拒」——幂等跳过将使重复写入静默返回成功,与字面冲突;查询记录亦无 E2E-A 任务同窗同参确定性指纹语义可供幂等判定。D-B4-05 运行前登记。
3. **时间戳口径**: 本文件与 DELIVERY 全部日期/时刻为 UTC(文件头声明);测试断言时刻均为显式注入字面量,零墙钟依赖(除 archived_at 缺省值函数路径,D-B4-11)。
4. **D-B4-02 实现期一次性收紧(非运行后回改)**: 草案正则 `^RT-.+$` 在 T2 用例首跑暴露接受尾随空白 id(`RT-20261105-001 ` 合法误判),于**任何真实运行/测试定稿前**一次性收紧为 `^RT-\S+$`;§六 D-B4-02 行已同步载明收紧事实与理由。此为实现期参数修正,非「运行后回改」——§六参数登记时点(5e383e3)先于测试定稿(08f0dcc),两时点间修正已在 D-B4-02 行内披露。
5. **CI 套件计数与冻结合同不符(型观察,非本包所致)**: 冻结合同 CI-SUITES=58、零回归判据「58+新增1=59」。实测本包尖端 63 test 文件/62 运行套件(排除 test_glm_live)。分解: 58=B2 分支谱系计数(B2 尖端 59 文件−1 跳过);基线 b5c33f85 经 B1/B2 两次合并步合入 main 侧 G1/G2/G3 三个 GLM 测试文件(git diff fe04691..b5c33f85 -- tests/ 实取恰 3 行 A,均为绿套件)→ 62+本包 1=63。零回归判据以逐套对照成立: B2 时点 57 绿+1 环境红 → 本包 61 绿+1 环境红,差集恰=+3 GLM 绿+本包新绿。计数差异为谱系事实,非本包引入。
6. **test_p4_fixes 环境红归因(承接 B1/B2 登记)**: 本地 CI 1 套 exit=1(test_p4_fixes,尾部「39通过/4失败」),DEV 工作树 data/daily 真实副本 20261101-1104 在场触发 real 分支无 9 月数据所致;CI fresh checkout 绿;与本包零导入关系(基线 b5c33f85 原样,非本包引入)。
7. **CI Actions run 取证受限,如实登记**: 本执行Agent 对既有 Actions run(run 41913165599 等)的 `gh api` 核验两次被拒(环境授权限制),未重试;以上 run 归属/结论以**本地 git 事实链**佐证(基线谱系 diff 实取,见第 5 条),Actions run 登记依合同 §五由操作者 CHECKPOINT 派发后落 rounds/024/E2EB-WP-B4-CI-dispatch-evidence.md。操作者如需闭环可复核该 run。
8. **一次性 /tmp 工具(不入白名单,B2 先例同款)**: /tmp/b4_precalc.py(digest 字面量预计算+hashlib 独立旁证)/tmp/b4_inject.py(D1-D4 注入器)/tmp/b4_run_ci.py(本地 CI 同构 runner)——三件均为本包一次性执行工具,全部留档证据包④(源码+输出),零改动仓内任何非白名单文件。
9. **零运行产物重申**: 本包无编排入口、无真实运行要求(DESIGN 未为 WP-B4 指定;端到端走查属 WP-B5)→ data/research/ 与 data/daily 零真实读写;全部验证经合成 fixture 于 tempdir 完成(D-B4-12)。

---

## §八 合同逐条自检(AC-01~AC-07)

| AC | 自评 | 一句证据指引 |
|---|---|---|
| AC-01 规格抄录与交付面登记正确性 | **PASS** | §零(i) L228-232 逐字抄录(行号 0 偏差)+四要素齐备+k=4 清单逐条附 DESIGN 依据+结构约束核验(iii)(git ls-files 零重合/必含件齐/推导无越界);证据包① |
| AC-02 验收要点逐条交付与证据映射 | **PASS**(④Actions run 面待操作者) | §四映射表 L232①②③+六个补充要点全落行,落点=实现 file:line(08f0dcc 实取)+用例名+运行证据;④本地侧同构 CI 61绿+1既有红归因(§三),Actions run=操作者 CHECKPOINT 派发(合同§五禁自行派发),登记件将落 rounds/024/E2EB-WP-B4-CI-dispatch-evidence.md |
| AC-03 测试与确定性验证 | **PASS** | 50 用例全绿(证据包④);零网络(源码零网络 import,纯度锁用例)/全合成 fixture 唯一数据源(D-B4-12)/预期值字面量硬编码(digest 预计算誊写+hashlib 独立旁证,禁自证恒真)/D1-D4 注入定向红(§三)/漂移维护策略专节+fixture→预期值映射=DELIVERY §六/§七 |
| AC-04 引用真实性与注入边界 | **PASS** | §一/§二/§四 全部 file:line 为工作树实读(±3 行内;实现件行号=08f0dcc 实取复核);注入内容引用标注「注入摘要」(文件头声明);跨支引用零(设计三件=基线工作树实读,无跨支文件引用);否定性声明可 grep 反证(T5 纯度锁) |
| AC-05 范围/分支/生产隔离 | **PASS** | diff b5c33f85..HEAD=M/D 0+A 恰 4 行=白名单 k=4(§五 commit 链;终态复核入证据包③);纯线性零 merge+reflog 无 reset/amend;ls-remote 34 支尖端不变唯一新增本支(§七.5 谱系证据+终态 ls-remote 入证据包③);零网络;LIVE 零写入(grep [R024\|E2EB-WP-B4\|IA-P03-E2EB-WP-B4] 零命中+real_data_acceptance.py sha256=f9ca189c…不变,取证入证据包③);LaunchAgents 零改动;E2E-A/B1/B2 在场件零改动(A 行恰白名单可反证);复用禁复制分叉(T5 正向锁+digest 算法零复制);档案不 commit(data/ gitignored);.gitignore 零改动 |
| AC-06 CI 与证据包 | **PASS**(②③④)/**NOT VERIFIED**(①·操作者 CHECKPOINT 派发面) | ②证据包八类成员+SHA256SUMS 于 /tmp/p03-e2eb-b4-evidence/(装配时序见 §五 commit 链);③DELIVERY 五节+漂移维护专节+映射节齐备;④stdout 四段自述=证据包⑦副本;①Actions run=操作者面(执行Agent禁自行派发,合同§五),登记件 rounds/024/E2EB-WP-B4-CI-dispatch-evidence.md 由操作者落字面值 |
| AC-07 研究纪律与使用边界 | **PASS** | ①零直读 data/daily 原始档(快照读取面文件名仅由 snapshot_id 规范分解派生=结构性不可达,T5 纯度锁反证;测试全合成);②零填0(摘要为计数映射无数值编造面,D-B4-04);③零交易/仓位/收益承诺文案;④零 GLM/凭证/付费(import 面纯标准库+qir/rp);⑤W4/W5 零链接;⑥白名单外零实施(diff 反证) |

---

## §九 提交前数值标注六项自检清单(§5.3,强制)

扫描范围=本 REPORT+DELIVERY 双文档全文。日期/SHA/行号/结构编号类按第 5 项边界出圈登记(文件头时区与实读声明+§五 SHA 表);以下为计数类/统计类数值清单(§5.3 第 1-2 项,逐个二选一标注;第 3 项实取复核于 2026-11-05 工作树重跑/重读完成,禁凭记忆——关键项复核手段注于来源列):

| # | 数值(出现节) | 标注 |
|---|---|---|
| 1 | 白名单文件数 k=4(§零(ii)) | [实取·来源: DESIGN L228-232 抄录+固定推导规则;git ls-files 对照零重合(§零(iii))] |
| 2 | 模块 395 行(§二) | [实取·来源: wc -l scripts/research_archive.py,2026-11-05 工作树复核=395] |
| 3 | 测试 675 行(§二) | [实取·来源: wc -l tests/test_p03_e2eb_b4.py,复核=675] |
| 4 | 测试用例 50=T0 2+T1 8+T2 6+T3 10+T4 14+T5 6+T6 4(§二/§三) | [实取·来源: python3 直跑 Ran 50 tests OK(2026-11-05 复跑);逐类计数=unittest 类方法枚举] |
| 5 | 记录 schema 十三键(§六 D-B4-03) | [实取·来源: len(QUERY_RECORD_KEYS)=13,python3 工作树复核] |
| 6 | digest 字面量 `756c258d9943841d`/`2418e26ca8294e02`(§二/DELIVERY 专节) | [实取·来源: /tmp/b4_precalc.py R5 管线预计算+hashlib 独立旁证;T0 用例断言 rp.digest_snapshot(SNAP_A)==字面量 绿] |
| 7 | 摘要计数字面量 {ABSENT_REGISTRY:1,PENDING_EXECUTION:1}/{ABSENT_REGISTRY:1,RESOLVED:1}/{NO_DATA:1}/values={MB-1:157.8}(§六 D-B4-04/DELIVERY) | [实取·来源: 由 fixture L43-125 计数派生,T4 三摘要用例断言绿;157.8 为 fixture 发明值(与 EXEC_OK values 同源誊写)] |
| 8 | fixture 数值 157.8/158.2(DELIVERY 专节) | [示意·非实取](合成 fixture 发明字面量,tests L47/L55/L121-122) |
| 9 | fixture 文案「81指标」(IR absence_reason,tests L73/L107) | [示意·非实取](合成 IR 文案内数值,非运行统计;非对 registry 计数的运行断言) |
| 10 | D1-D4 注入定向红 3/4/1/1(§三) | [实取·来源: /tmp/b4_inject.py 运行日志(证据包④ injections/);还原态 50 用例复跑 OK] |
| 11 | 模块 sha256 `635d9a3e…4aeb3`/测试 `f543369c…4d0f`(§五) | [实取·来源: shasum -a 256 工作树复核(2026-11-05,与 §五表一致);注入器 4 次还原比对同值] |
| 12 | 本地 CI: 63 文件/62 套/61 绿+1 红/1 跳过(§三/DELIVERY §二) | [实取·来源: /tmp/b4_run_ci.py 全量逐套退出码(证据包④ suite-summary.txt);63=基线 62+本包 1] |
| 13 | 冻结计数 58 与「58+新增1=59」(§三/§七.5) | [实取·来源: 冻结合同文本注入(IA-P03-E2EB-WP-B4-AC-v1.0 §六 AC-06①「套件数=58」);与实测 62 的谱系分解见 §七.5] |
| 14 | B2 时点基线 57 绿+1 红(§三/§七.5) | [实取·来源: docs/P03_E2EB_B2_DELIVERY.md §二(基线工作树实读,58套件57绿+1既有红)] |
| 15 | merge 增量 3 个 GLM 测试文件(§七.5) | [实取·来源: git diff fe04691..b5c33f85 --stat -- tests/ 实取恰 3 行 A] |
| 16 | test_p4_fixes「39通过/4失败」(§三/§七.6) | [实取·来源: 本地 CI 该套 stderr 尾部(证据包④);与 B1/B2 REPORT §七登记同款] |
| 17 | 开工 ls-remote 34 支/终态 35 支(§八 AC-05) | [实取·来源: 开工步骤2 ls-remote 输出 34 支(证据包③);终态=推送后 ls-remote 复测 35(08-sidecar/final-state.txt,zip 外)] |
| 18 | commit 数: 开工登记+实现+终版+zip 追加=4 提交(§五) | [实取·来源: git log 纯线性核验(证据包③);零 merge 提交] |
| 19 | 证据包八类最低集成员(§八 AC-06) | [实取·来源: /tmp/p03-e2eb-b4-evidence/ 装配后 SHA256SUMS 逐件哈希(证据包⑧)] |
| 20 | Actions run 41913165599(§七.7) | [示意·非实取](gh api 核验两次被拒,run 归属未由本执行Agent 证实;仅为受限取证事实登记,操作者可复核) |
| 21 | zip 成员数/字节数(DELIVERY §五追加行) | [实取·来源: 装配后 shasum+wc -c(§五 commit 链时序)] |

第 4 项纪律: 疑似失实项=无(第 20 项原本可能失实,已按合法出口降级为「受限取证事实」如实登记而非断言 run 结论)。第 6 项: 本清单成件入证据包(09-numeric-checklist.md,八类最低集外附加成员)。
