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

(实现提交后回填)

---

## §三 测试与本地CI

(实现提交后回填)

---

## §四 逐要点证据映射表(AC-02)

(实现提交后回填)

---

## §五 模块SHA登记

(终版回填)

---

## §六 实现参数与决策点登记(先登记后运行,运行后禁回改)

**承接 B1/B2 参数**(docs/P03_E2EB_B1_REPORT.md §六 / docs/P03_E2EB_B2_REPORT.md §六,运行后已禁改;本包作为下游消费面原样承接): P-01..P-14(IR schema 常量)/D-B1-01(PENDING_EXECUTION 哨兵双阶段语义)/D-B1-10(query_id=QB-YYYYMMDD-NNN,同日单调计数与落盘属 WP-B4 档案——本包承接面)/D-B2-03(执行器结构化 refusal {ir,values,snapshot_id,gate_status,refusal})/D-B2-06(执行器返回 values=仅 RESOLVED 绑定)。

**本包登记型决策点**:

| # | 决策点 | 登记内容(运行前登记) |
|---|---|---|
| D-B4-01 | 档案载体与路径 | 单一共享档案文件族=「实现包定路径」授权面(DESIGN L185「实现与路径最终由实现包定,本设计固定引用约定」);落 `<archive_root>/research_archive/query_history/{query_id}.json`,一记录一文件;默认 archive_root=DEV 仓 `data/research/`(E2E-A DEFAULT_OUT_DIR 同源根,rtm.py:32-34);原子写=path+'.tmp'+os.replace(rtm.py:152-155 同构);**本包只建模式B侧**(research_tasks/anomaly_events 集合目录不建不写,L230「本包只建模式B侧+引用约定」;E2E-A 档案留其既有 data/research/ 根存储零触碰) |
| D-B4-02 | ID 引用约定 | ①query_id=QB-YYYYMMDD-NNN 严格格式,**复用** qir.QUERY_ID_RE(禁复制);②任务引用(promoted_to_task_id)=**RT- 前缀族** `^RT-.+$`(G3 在场先例 glm_conclusion_integrator.py:82「E2E-A 任务(rtm.py:53 形态)」;DESIGN L183 RT-YYYYMMDD-NNN 为其严格子集;E2E-A 实况 task_id=RT-{start}~{end}-{rule}-{hash8},rtm.py:48-53+data/research 在场档佐证——DESIGN §四头部「冲突由后续包登记型修订承接」→本包登记发现(§七.2)不擅改设计);③origin_query_id=query_id 同严格格式(模式B查询恒由 B1 make_query_id 产格,qir.QUERY_ID_RE);④一致性规则: record.query_id 的 YYYYMMDD 段==ir.created_at 前10字符日期段(B1 make_query_id 派生一致性);⑤同日序列各自独立计数(L183) |
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

(终版回填)

---

## §八 合同逐条自检(AC-01~AC-07)

(终版回填)

---

## §九 提交前数值标注六项自检清单(§5.3,强制)

(终版回填)
