# IA-P2-WP-B REPORT — P2 深研层第 2 实现包(证据矩阵装配与轮次推进引擎)

> 包: IA-P2-WP-B(P2 族第 2 包) · 执行Agent: Agent 3 · 分支: `dev/p2-impl-b`
> 基线: BASE-P2B=`a040faa741a69f4e7f037fb6e778f4e0bda3305a`(origin/main,开工 ls-remote 实取一致;本包**无并入步**,f8ed401 经祖先在场)
> 合同: IA-P2-WP-B-AC-v1.0(冻结,附录A 内嵌注入)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY/上游在场件行号一律为**本包基线工作树(BASE-P2B checkout)实读**行号(2026-11-07T05:49Z-06:3xZ 实取);提示词注入内容引用一律标注「注入摘要,非工作树实读」。
> 数值标注边界: 本文所有计数类/统计类数值逐个二选一标注 `[实取·来源: …]` 或 `[示意·非实取]`;日期/SHA/结构编号(WP-P2-A/B、P2-G-05)、档键成分(ID 格式字符串)按合同边界出圈,不强制标注。

---

## §零 规格抄录与交付面登记(开工首步,AC-01;登记后即本合同白名单实体)

### §零.1 DESIGN §七 WP-P2-B 行四要素逐字抄录

实读 `docs/P2_DESIGN.md`(基线工作树在场,blob `63a1964812f0c081aef0ea38148dec82537c7416`,与 f8ed401 侧等值,§零.7 核验),WP-P2-B 行位于 L199-L203,逐字抄录:

```text
L199: **WP-P2-B 证据矩阵装配与轮次推进引擎**
L200: - 目标: 落地 §3.3 证据契约+§4.2 矩阵+§4.4 轮次推进/终止判定(程序确定性汇总;快照绑定取数)。
L201: - 范围: 新增矩阵装配与轮次引擎模块;按需配对计算沿 E2E-B WP-B2 承接(P2-G-05 不在本包重复实现);事件日历(D3)另包。
L202: - 依赖: WP-P2-A;快照构建走 write=False 离线路径(P2-G-06 范式)。
L203: - 验收要点草案: ①证据接地负向测试(无 provenance 数值注入矩阵→fail-closed)②矩阵汇总确定性测试(同输入同输出;去重/封顶规则与 L520-521 同构断言)③轮次终止条件各自触发用例(条件 4 项 [实取·本文 §4.4 枚举,2026-11-02];含数据阻断→INCONCLUSIVE+登记,不编造)④DEV 授权数据副本端到端(数据档引用 data/daily/*_20261102.json)⑤CI 零回归。
```

四要素齐备(目标 L200/范围 L201/依赖 L202/验收要点 L203 共 5 条),无缺失;B 行与 A 行(L193-L197,任务/假设/条件登记器)四要素逐项可区分(题名/目标节引用/范围模块/依赖列/要点集全不同),不触发合同 §零(iv) 首项停止条件。依赖列核验: ①「依赖: WP-P2-A」——上游=同族前包 WP-P2-A(R033 #23 审计 PASS,注入摘要,非工作树实读),其交付件基线工作树在场实读(§零.6: `scripts/deep_research_registrar.py` 842 行 [实取·wc -l]+`tests/test_p2_wp_a.py`+`docs/P2_WP_A_REPORT.md`+`docs/P2_WP_A_DELIVERY.md`,REPORT §零.2 登记清单 k=4 同源对照),依赖列未要求并入他支;②「快照构建走 write=False 离线路径(P2-G-06 范式)」——`scripts/snapshot_builder.py` L266-268 `build_snapshot(..., write=True, ...)` 签名实读,write=False 即离线构建范式在场;③范围列无真实 GLM 调用/网络出站/新数据源凭证付费要求(「按需配对计算沿 E2E-B WP-B2 承接」=明确不在本包实现的承接登记,「事件日历(D3)另包」=明确排除)→ 无情形(d)停止条件。

### §零.2 交付文件清单(k=4 [实取·本节清点],登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据(推导逐条附) |
|---|---|---|
| 1 | `scripts/deep_research_matrix_engine.py` | DESIGN L201「新增矩阵装配与轮次引擎模块」=恰 1 个代码模块(「矩阵装配与轮次引擎」并列定语修饰单数「模块」,与 WP-A 行 L195「新增深研任务/假设/条件记录模块」同为单模块多记录族式样;题名 L199「证据矩阵装配与轮次推进引擎」单数佐证)+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」;文件名沿 WP-A `deep_research_registrar.py` 命名先例(deep_research_* 族) |
| 2 | `tests/test_p2_wp_b.py` | DESIGN L203①②③④工件「测试」+合同附录A §零(ii)「含代码则必含 tests/test_p2_wp_b.py」 |
| 3 | `docs/P2_WP_B_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P2_WP_B_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L203⑤「CI 零回归」证据落点=DELIVERY |

### §零.3 结构约束核验

- 与 `git ls-files` 零重合: 4 路径 `git ls-files -- <paths>` 输出=0 行 [实取·开工 2026-11-07T06:03Z(登记笔 c825ee4 提交前),输出入证据包 01-startup-forensics],且工作树均不存在 → 纯新增 ✓
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p2_wp_b.py)✓
- 推导无越界: 范围列恰 1 个代码模块 → scripts/ 恰 1 文件;范围列两处排除项(按需配对计算/事件日历)零实现零文件;未引入 DESIGN 依据外文件 ✓

### §零.4 DP 登记(开工首步登记定值,登记定值即实现值;先登记后运行,运行后禁回改)

实读 DESIGN §2.4 DP 表(L63-L72,6 DP 四要素齐备 [实取·表清点]);本包为 P2 族第 2 包,DP-1/DP-2/DP-6 已由同族前包 WP-P2-A 登记定值并落其模块常量与任务档 `registered_params`(REPORT §零.4 同源),本包**复用导入上游定值,不重复定义、不改写**(对齐上游=复用调用):

| DP | 分类(DESIGN 实读) | 本包登记定值(=实现值) | 依据与复用面 |
|---|---|---|---|
| DP-1 深研轮次预算 | 登记型(L65) | **(c) 双轨: 固定上限 N=5+提前终止**;消费面=轮次引擎预算核验(round ≤ round_budget)与终止条件③(§4.4 L130);实现值=`drr.DP1_ROUND_BUDGET_DEFAULT`(=5)+任务档 `registered_params.round_budget` | L65+DESIGN L202 依赖 WP-P2-A;复用 `deep_research_registrar.py` L39/L373-375 |
| DP-2 证据权重量表 | 登记型(L66) | **(b) 五级=星级 1-5**;消费面=证据记录 weight 词表与矩阵汇总星级复用;实现值=`drr.DP2_WEIGHT_SCALE`(=(1,5)) | L66;复用同上 L40/L376-378 |
| DP-6 区分性判据最低数 | 登记型(L70) | **(a) 每对 ≥1**;消费面=轮次引擎判据判定输入锚定(判定须引用任务档已登记判据,WP-A DRAFT 已强制全对覆盖);实现值=`drr.DP6_MIN_DISCRIMINATING_PER_PAIR`(=1) | L70;复用同上 L41 |
| DP-3 ID 族 | 对齐型(L67,非登记型清单成员) | 新记录族续用上游确定性 ID 构造先例: 证据 `EVI-{YYYYMMDD}-{sha256[:8]}`/轮次 `RD-{YYYYMMDD}-{sha256[:8]}`(指纹不含墙钟,重放幂等;前缀避开上游已占 RT-DR-/HP-/FC-/EV-) | L67「不冻结 ID 格式」+WP-A 先例(P-A-06/P-A-07);构造原语复用 `drr._hash8` |
| DP-4 GLM 角色 | 确认权留用户(L68) | **本包不触及**(范围 L201=纯确定性矩阵与轮次引擎,零 GLM 面;DESIGN L207 GLM 对接属 WP-P2-C) | L68 |
| DP-5 外部源扩展 | 确认权留用户(L69) | **本包不触及**(范围无任何数据源扩展;D3 事件日历属 WP-P2-D L211-215) | L69 |

DP 编号/数量与 DESIGN 实读一致(6 个 [实取·DESIGN §2.4 表清点]);DP-4/DP-5 未被自决实施(本包范围零触及)。

### §零.5 实现参数登记(P-B-01..P-B-18,先登记后实现,运行后禁回改)

| # | 参数 | 登记定值 | 依据 |
|---|---|---|---|
| P-B-01 | 档案集合(挂共享档案) | 共享档案族根 `data/research/research_archive/`(B4 载体,`ra.DEFAULT_ARCHIVE_DIR` 同源复用)下新增 2 集合: `deep_research_evidence`(证据记录)/`deep_research_rounds`(轮次记录);一记录一文件 `{记录id}.json`;不占用 WP-A 既有 4 集合名 | DESIGN L201「新增矩阵装配与轮次引擎模块」(记录族随模块)+§2.3 L57(挂共享档案);WP-A P-A-01 同款 |
| P-B-02 | 证据记录 schema(§3.3 字段级) | `record_type/deep_research_evidence` 字段集: evidence_id/task_id/hypothesis_id/round(正整数)/created_at + §3.3 L94 契约字段 {metric_id(string)/fact_id(string)/value(number)/observation_date(ISO日期)/snapshot_id/digest_snapshot(经 rp.digest_snapshot 重算,API 无 digest 入参,禁采声明值)/direction∈{"支持","反对","中性"}/weight∈{1..5}(DP-2)/mechanism∈机制族 7 类(P-B-04)/note(string)} + 反证解释对 {explained(bool,缺省 False)/explained_note(string\|null,explained=True 时必填}(§4.3 反证参与封顶需区分已解释/未解释,语义对齐 L518 证据分级 v2 `explained:true` 标记;§3.3 字段清单为最小必携集,本对为可选扩展字段,如实偏差登记 §三) | DESIGN §3.3 L94+§4.3 L124+L518 实读 |
| P-B-03 | 方向词表与 v2 映射 | direction 三值 支持\|反对\|中性(DESIGN L94 原文);映射证据分级 v2(L518): 支持→{contrary:False,neutral:False}/反对→{contrary:True,explained:记录值}/中性→{neutral:True};中性「数值照常核验但不计入支持数量」(L518 同款),反对「不计入支持数量,只参与反证校验」(L521 同款) | DESIGN L94(语义对齐 L518/L521)+report_generator.py L518/L521 实读 |
| P-B-04 | 机制族 7 类 | 增长/通胀/利率与流动性/信用/避险与估值/供应与库存/资金流=复用 `ae.MECHANISM_CATEGORIES`(allocation_engine.py L104,7 类 [实取·清单清点]);证据 mechanism 必须命中该清单(缺席→拒收,不以相近类冒充) | DESIGN L94(机制族 7 类之一 [实取·同上 L518])+L518 词面 |
| P-B-05 | 证据接地(fail-closed,要点①) | 证据注册六重接地,任一不过即拒(零写入): ①snapshot_id 规范(ra.parse_snapshot_id)且快照文件可载(drr._load_snapshot_for_verify,结构性不可达 data/daily 原始采集档);②digest=rp.digest_snapshot(快照)重算绑定(篡改快照→失配拒);③Gate A 纪律: 快照 gate_a.status 须 rp.gate_allows_formal_research(PASS/DEGRADED 放行,FAIL/缺省→拒,DESIGN §3.1 L80「Gate A=FAIL 的快照不得作为深研正式证据来源」);④事实接地: 快照 facts(真实快照结构=事实 dict 列表,snapshot_builder.py L420)中存在 fact_id 命中项,且 value/observation_date/metric_id 三者与记录逐一相等(无 provenance 的数值不得进入证据矩阵,fail-closed);⑤事实质量: 命中 fact 的 quality_status≠FAIL(FAIL=校验失败/数据不足,不得作数值证据;PASS/WARN/DEGRADED 放行,词表=fe.grade_issues L635-638);⑥任务面: task 在场且当前态=ACTIVE(drr.current_status)、hypothesis_id∈task.hypothesis_ids、round≤round_budget(DP-1) | DESIGN §3.1 L80+§3.3 L94(无 provenance fail-closed)+L203①+§4.4 L130;snapshot 结构 L413-426 实读 |
| P-B-06 | 矩阵 cells 形态 | cells=稀疏映射 {(hypothesis_id, evidence_id) → {direction, weight}}: 证据记录携 hypothesis_id(该证据对其绑定假设的方向/权重),绑定对入 cells;§4.2 L112「假设×证据」按映射语义实现为绑定对稀疏映射(非全叉积发明语义,无绑定对的格子不虚构中性值) | DESIGN §4.2 L110-L112+§3.3 L94 |
| P-B-07 | 矩阵 summary(每假设) | 四字段(DESIGN L113-115 逐字)+1 计算字段: 支持数(去重: 同一底层指标多次引用计 1 项,去重键=ae._base_metric,L520 规则)/反证数(同口径去重)/未解释重大反证(bool=存在 direction=反对 且 explained≠True 的证据;L521「存在未解释反证时封顶」)/机制覆盖数(支持向去重后独立证据的 mechanism 去重类数)/star(确信度封顶后星级,复用 ae.star_level_from_evidence 计算——L521 门槛 1★=1项/2★=2项/3★=3项且2类/4★=4项且3类且跨2观察期/5★=5项且3类且3观察期+未解释反证封顶 3★;要点②「封顶规则与 L520-521 同构断言」的可观测落点;star 系 DESIGN summary 四字段外的计算扩展字段,如实偏差登记 §三) | DESIGN §4.2 L113-L115+§4.3 L124+L520-L521+L203②;复用 allocation_engine.py L130-137/L562-568/L571-580/L592-622 |
| P-B-08 | 矩阵确定性汇编 | assemble_matrix(task_id): 假设按 hypothesis_id 升序/证据按 evidence_id 升序/汇总经复用 ae 函数;同输入同输出(字节级: canonical JSON sort_keys 序列化相等);模型不参与,程序确定性汇总(DESIGN L119「矩阵由程序从证据记录确定性汇总」) | DESIGN §4.2 L119+L203② |
| P-B-09 | 轮次引擎输入契约 | run_round(task_id, round_input, snapshot_dir): round_input={round(正整数,须=既有轮次+1,R1 起)/evidence[证据规格 dict 列表(P-B-02 字段,接地六重校验)]/criterion_judgments[{pair:[hp_id,hp_id],criterion,holds:bool}](pair 二成员须命中任务假设集且 (sorted(pair),criterion) 须命中任务档已登记判据集——判定锚定登记面,未登记判据的判定拒收)/hypotheses_falsified[hp_id 列表,成员须命中假设集](证伪判定=证伪向条件触发驱动的输入面,条件程序评估属 WP-P2-C L207,本包确定性汇总)/criterion_computable(bool,推进条件②输入)/counter_search_open[hp_id 列表,推进条件③输入: 反证检索义务未闭合的假设]/data_blocking(None\|{snapshot_id,detail},终止条件④输入: 阻断声明经引擎对快照 gate_a 复核实证——快照实为 gate 放行态而声明阻断→拒收不一致声明) | DESIGN §4.4 L129-L130+§4.1 L103+L203③;WP-P2-C 边界 L207 实读 |
| P-B-10 | 轮次终止判定(确定性,要点③) | 优先序=DESIGN §4.4 L130 枚举序(并列触发时按枚举序取先,登记为确定性平局规则): ①任一 criterion_judgments.holds=True→RESOLVED;②hypotheses_falsified 覆盖全部假设→ALL_FALSIFIED;③round≥round_budget(DP-1)→INCONCLUSIVE(硬上界依据=DESIGN §2.4 DP-1 行 L65 影响列「预算耗尽→INCONCLUSIVE 收束」;§4.4③「且连续无新增证据」子句如实落记为轮次记录属性 no_new_evidence_streak,不作门控——预算耗尽无论 streak 与否均须收束,不收束即违反 N 轮上限,如实偏差登记 §三);④data_blocking 在场且经复核→INCONCLUSIVE+阻断登记(轮次记录 blocking 字段+终态事件 note,如实不编造);终态迁移经 drr.append_lifecycle_event(ACTIVE→{终态},复用既有状态保护机制,AC-07.5 转递面) | DESIGN §4.4 L130+L203③+L65;复用 deep_research_registrar.py L709-L737 |
| P-B-11 | 轮次推进判定 | 无终态触发时按 §4.4 L129 推进条件任一: ①本轮新登记证据 ≥1 条;②criterion_computable=True;③counter_search_open 非空→decision.action="advance"(reasons 列明命中项);三项皆无→decision.action="hold"(DESIGN 未枚举该态,登记为确定性留守输出: 无可推进事由且未触终态,由外层驱动决定是否再入轮,如实登记) | DESIGN §4.4 L129 |
| P-B-12 | 轮次记录 schema(append-only) | `record_type/deep_research_round`: round_id(RD-{ymd}-{hash8(指纹={task_id,round,evidence_ids,criterion_judgments,hypotheses_falsified,data_blocking},不含墙钟,同轮次同输入重放→同 id→rejected-duplicate)/task_id/round/created_at/evidence_ids/matrix(本轮汇编矩阵快照,P-B-08)/criterion_judgments/hypotheses_falsified/no_new_evidence_streak(前轮至本轮连续零新登记证据的轮数,R1=0)/data_blocking/decision{action,terminal_status,rule,reasons}/blocking;轮次记录 append-only(重复/改写一律拒),轮次结论不回改历史轮记录 | DESIGN §4.4 L131+§2.2 L50;WP-A P-A-09 同款 |
| P-B-13 | 两段式写入原子性 | run_round: 先全量校验(证据六重接地×N+输入契约)后经 drr._write_records 原子落证据批(预检零存在,任一重复→rejected-duplicate 零写入),再落轮次记录(+终态事件);轮次记录若因重复拒收,已落证据批保留(append-only 语义,如实状态,重放同输入必撞同 id 被拒,无隐匿重跑面) | WP-A _write_records 先例(L513-524 复用)+append-only 纪律 |
| P-B-14 | 生命周期衔接(复用上游) | activate_task(task_id)=drr.append_lifecycle_event(DRAFT→ACTIVE)复用;run_round 要求当前态 ACTIVE;终态迁移同 P-B-10;本包零新增状态值、零改写迁移表,任务档字节不可变(事件溯源) | DESIGN §2.2 L46+AC-07.5(经既有状态保护机制转递);复用 drr L73-82/L709-737 |
| P-B-15 | e2e 编排入口(要点④) | 模块内 `run_dev_copy_end_to_end(target_ymd="20261102", ...)`: ①lazy import snapshot_builder,sb.build_snapshot(target_ymd,write=False)(P2-G-06 范式,离线,数据档经 sb 既有默认入口只读——本模块源码零 `data/daily` 字面引用,P2-G-06);②快照物化至运行产物区 `data/research/p2_wp_b_e2e/{ymd}/snapshots/`(data/research/ 允许写入不 commit);③digest 重算+Gate A 核验(rp.gate_allows_formal_research);④drr.register_deep_research_task 注册合成研究任务(问题/假设/判据为登记的 e2e 常量)绑定该快照;⑤activate+证据接地尝试(从快照 facts 实取一条 PASS/DEGRADED 质量事实构造证据规格——gate 放行则正向落档,gate FAIL 则如实 fail-closed 拒收并记录理由);⑥run_round R1(gate FAIL→data_blocking 输入,阻断经引擎复核)→终态判定;⑦产物 JSON 落 data/research/p2_wp_b_e2e/(不 commit)+stdout 全文日志(步骤10 采证) | DESIGN L202+L203④+§3.1 L80;P2-G-06(INVENTORY L165) |
| P-B-16 | import 面 | 纯标准库(json/os/sys/datetime)+项目既有模块复用调用: deep_research_registrar(drr,上游 WP-P2-A)/research_provenance(rp)/allocation_engine(ae,星级/去重/方向切分原语复用)/research_archive(ra,经 drr 转递)/snapshot_builder(sb,lazy,e2e 函数内);零新增第三方依赖,零网络 | AC-03.1/AC-05.4;上游 import 面实测(ae/fe/rp/ra 模块级零第三方 import [实取·AST 清点 2026-11-07T06:2xZ]) |
| P-B-17 | 零墙钟纪律 | created_at 缺省 now(UTC)属登记落档时刻;一切 id 指纹不含墙钟(重放幂等);测试显式注入时刻 | WP-A P-A-12 同款(B4 先例) |
| P-B-18 | 范围排除登记 | ①按需配对计算(D2/P2-G-05): 零实现零复制——沿 E2E-B WP-B2 承接登记(消费面=correlation_calculator.py 固定配对表现树 12 对 [实取·L28-L53 清点,原 10 对+IA-P1-WP-C 增补 2 对 L49-L52;DESIGN L87「固定 10 对」系 2026-11-02 历史快照口径,如实注记差异],本包证据面不经配对计算);②事件日历(D3/P2-G-04): 属 WP-P2-D,零触及;③条件程序评估/GLM 对接: 属 WP-P2-C,本包仅消费其判定结果作确定性输入(P-B-09) | DESIGN L201+§3.2 L87-L88+L211-215+L207 |

### §零.6 前置实读登记(file:line,均本包基线工作树 BASE-P2B checkout 实读,2026-11-07T05:49Z-06:3xZ)

| 对象 | 登记 |
|---|---|
| P2 DESIGN §七 WP-P2-B 行 | docs/P2_DESIGN.md:199-203(§零.1 逐字抄录) |
| P2 DESIGN §三 证据与数据契约 | 同文件:76-94(快照纪律红线 L80;数据五类三态 L84-90;证据记录契约 §3.3 L92-94) |
| P2 DESIGN §四 假设论证 | 同文件:98-131(≥2 竞争假设 L102;区分性判据 L103;证据矩阵 §4.2 L106-119;反方证据强制 §4.3 L121-125;轮次推进/终止 §4.4 L127-131) |
| P2 DESIGN §二 任务模型 | 同文件:33-72(生命周期 L46-53;共享衔接 L57-59;DP 表 L63-72) |
| P2 DESIGN §六 可反驳性 | 同文件:148-185(结论状态机 L172-180;证伪后处置 L182-185) |
| P2 DESIGN §八 红线 | 同文件:221-228(快照+门禁 L223;LIVE 禁写 L224;禁交易 L225;append-only L226;GLM/费用 L227;如实 L228) |
| P2 INVENTORY 缺口承接 | docs/P2_INVENTORY.md:164(P2-G-05 按需配对计算面=沿 E2E-B WP-B2 承接,不在本包)/165(P2-G-06 DEV 无持久化快照,write=False 离线构建范式=本包 e2e 消费) |
| WP-P2-A 交付件(上游,依赖列 L202 所载;只读禁改) | scripts/deep_research_registrar.py:39-41(DP 定值常量)/46-53(四集合)/60-63(ID 前缀族)/73-82(迁移表)/102-107(docstring 规格锚)/133-163(确定性 ID 构造)/513-524(_write_records append-only)/533-651(register_deep_research_task)/657-671(load_task)/699-706(current_status)/709-737(append_lifecycle_event)/778-801(_load_snapshot_for_verify)/804-842(verify_task_bindings);tests/test_p2_wp_a.py(全合成 fixture+黄金字面量范式,1-130 实读);docs/P2_WP_A_REPORT.md §零.2(其登记清单 k=4,上游对照同源) |
| 证据分级 v2 词面锚(L520-521 同构对象) | scripts/report_generator.py:518(机制 7 类/contrary/explained/neutral 语义)/520(同一底层指标多次引用只计 1 项)/521(星级门槛 5 档+未解释反证封顶 3★) |
| 星级/去重/方向切分实现件(复用调用面) | scripts/allocation_engine.py:104(MECHANISM_CATEGORIES 7 类)/130-136(STAR_RULES)/137(MAX_STAR_UNEXPLAINED_COUNTER=3)/546(_obs_period_bucket)/562-568(_base_metric 底层指标去重)/571-580(split_evidence_direction)/592-622(star_level_from_evidence) |
| R1/R3/R5 数据接入点 | scripts/research_provenance.py:1210-1213(gate_allows_formal_research: PASS/DEGRADED 放行)/1270-1321(select_snapshot)/1324-1328(digest_snapshot=canonical JSON sha256 前 16 位)。注: DESIGN §3.1 L80 引 L1243/L1183-1188 为其历史基线行号,现树实测同 WP-A REPORT §零.6 注记(1210/1270/1324) |
| 快照构建(P2-G-06) | scripts/snapshot_builder.py:266-268(build_snapshot 签名含 write=True 缺省,write=False=离线构建)/413-426(快照 dict 结构: facts=事实列表/gate_a/quality/sources_status)/379-411(Gate A 从事实重算) |
| 事实结构与质量词表 | scripts/fact_engine.py:196-238(make_fact: fact_id=`{metric_id}@{od}` L211,observation_date ISO)/635-638(grade_issues: FAIL/DEGRADED/WARN/PASS) |
| D2 承接面(只读登记,零实现) | scripts/correlation_calculator.py:28-53(PAIRS 固定配对表现树 12 对 [实取·清点],P-B-18①) |
| DEV 授权数据副本(要点④数据档) | data/daily/ 27 档 [实取·ls 清点 2026-11-07T05:5xZ];*_20261102.json 4 件在场(china/global/macro/rate_economy)[实取·同左],与 DESIGN L203④ 数据档引用一致 |

### §零.7 开工核验记录(步骤0-4,UTC 2026-11-07T05:49:38Z 起)

1. **步骤0**: `git status` clean(基点分支 dev/p2-impl-a[WP-A 终态残留检出态],非本包所致脏=零)✓;UTC=2026-11-07T05:49:38Z。
2. **步骤1 占位符核验**: 三占位符均实值化(BASE-P2B=`a040faa741a69f4e7f037fb6e778f4e0bda3305a`/CI-SUITES=79/BRANCH-SET=52 支全表)✓,无占位符开闭标记残留。
3. **步骤2 前置实取**: `git ls-remote origin main`=`a040faa741a69f4e7f037fb6e778f4e0bda3305a` 全值一致 ✓;`git ls-remote --heads origin` 计 **52** 支 ✓ 且无 `dev/p2-impl-b` ✓;`git ls-remote origin dev/p2-design`=`f8ed401f4274e158c06a9404149d41260e5cc0ad` 前 7 位=f8ed401 ✓(原始输出=证据包 01-startup-forensics/ls-remote-*.txt)。注记(如实): 本地仓库 origin/main 跟踪 ref 陈旧(0c9fc3f,WP-A 收口前),`git fetch origin main` 后对象在场合规(跨支只读取证允许,合同 §4);checkout 自基线 SHA 实切,非盲切 HEAD。
4. **BRANCH-SET 全表对照发现登记(如实,R033 同型先例)**: 52 支分支名集合与冻结章 §三.1 完全一致、48/52 支尖端全值相等;**4 支提示词冻结表值与 live ls-remote 不符**(dev/p03-w2-glm-design/dev/p1-impl-b/dev/p1-impl-f/dev/round4-reliability),其中 2 条表值为结构无效 SHA(39 字符: p03-w2-glm-design `0c8de3c3…d892a817b…`缺 1 字符/p1-impl-f `44a7a686…f97d923…`缺 1 字符,真 ls-remote 不可能产出),另 2 条单字符替换(p1-impl-b `…ee7b7…`→live `…ee7b5…`/round4-reliability `…2b69209…`→live `…2b69409…`);第三源复核=本地 remote-tracking refs(for-each-ref)与 live 逐一全值一致 → 判定=**提示词侧转录讹误,非分支漂移**(证据链=证据包 01-startup-forensics/branchset-anomaly-analysis.txt);处置=开工步 2 显式判据(main 尖端/计数 52/无本分支/p2-design 尖端)全过不触发停止,执行窗口漂移检测锚定开工真观测快照,建议操作者对合同存档件冻结章 §三.1 作勘误登记(执行Agent 无权改合同)。
5. **步骤3 切建分支**: `git checkout -b dev/p2-impl-b a040faa741a69f4e7f037fb6e778f4e0bda3305a` ✓(自基线 SHA 切出;本包无并入步,DESIGN 冻结章无分支名指定,维持 dev/p2-impl-b)。
6. **步骤4 设计在场核验(本包无并入步,路径甲)**: ①`git merge-base --is-ancestor f8ed401f4274e158c06a9404149d41260e5cc0ad HEAD` **exit 0 可达** ✓(经 R033 指定并入步 dcfc7d0 祖先在场);②设计三件 `git ls-tree` 双侧(HEAD vs f8ed401)blob 等值: P2_INVENTORY=`c83c3938269ffb7192da9e7810bb052885cd9bb5`/P2_DESIGN=`63a1964812f0c081aef0ea38148dec82537c7416`/P2_DELIVERY=`ac80196fd06d28019e8c5e63f86a63ab94429f99`,与合同冻结章 §三 登记三值逐一相同 ✓(原始输出=证据包 01-startup-forensics/design-blob-*.txt)。
7. **生效前置**: 依赖列上游=WP-P2-A(L199-203 依赖列所载恰 1 包),其交付件基线工作树在场(§零.6 实读)✓;合同级生效前置=操作者发车时保证(注入摘要,非工作树实读)。

### §零.8 运行产物边界登记

**有真实运行面(要点④)**: DESIGN L203④「DEV 授权数据副本端到端(数据档引用 data/daily/*_20261102.json)」+L202「快照构建走 write=False 离线路径」→ 登记清单含编排入口(实现模块内 run_dev_copy_end_to_end,P-B-15),正式运行=步骤10: 产物落 `data/research/p2_wp_b_e2e/`(允许写入,不 commit,不入 diff);`data/daily/` 与既有档案只读(运行前后 sha256 双面锚定);`.gitignore` 不改(data/ 整体 ignored 既有实况)。**实现期只读探针(如实登记,非正式运行)**: 2026-11-07T06:0xZ 经 sb.build_snapshot(target_ymd='20261102', write=False) 离线探针(零写入零产物)——Gate A=**FAIL**(core_missing 5 项 [实取·探针输出: CN_TOTAL_TURNOVER/FED_FUNDS/SHCOMP/SH_AMOUNT/SZCI],quality.counts={PASS:3,DEGRADED:66,FAIL:0}),gate_allows_formal_research=False → 正式 e2e 预期如实走「证据接地 fail-closed 拒收+数据阻断→INCONCLUSIVE+登记」路径(DESIGN §4.4④+§3.1 红线预见的合法如实结果,情形(c) 口径;探针=工程事实核验,正式运行以步骤10 全量日志为准,不以此预检替代)。

### §零.9 GLM 能力级调用面判定(AC-03.7)

登记清单(§零.2)不含 GLM 能力级调用面实现(无客户端封装/调用编排/适配器类文件;范围 L201=纯确定性矩阵装配与轮次引擎)→ **AC-03.7 不适用**,判定依据=清单无调用面类文件即证;真实调用/凭证/付费=零(本包任何成员不得发生;DESIGN L207 GLM 对接属 WP-P2-C;条件程序评估判定结果作为确定性输入消费的边界见 P-B-09/P-B-18③)。

### §零.10 实现期登记(勘误/缺陷修复/注入循环;实现笔时点回填,先于任何正式运行)

**登记型参数零勘误**: P-B-01..P-B-18 登记定值与实现值逐项一致(§零.5 登记即实现;含已预登记的设计张力处置: explained/explained_note 字段/star 字段/预算硬上界/阻断复核限门禁支/e2e 透传参数),DP-1/2/6 复用上游常量零自决。

**实现期缺陷修复 3 处(测试首轮运行暴露,当场修复,先于任何提交)**:
- 修复A: `run_round` 轮次记录 `drr._write_records` 返回值原被丢弃——同 id 重放场景会返回 written 假象;补 rejected-duplicate 回传分支(与证据批分支同款)。
- 修复B(沙箱逃逸级,如实重点登记): `run_dev_copy_end_to_end` 原以 `os.path.join(root, drr.DEFAULT_ARCHIVE_DIR)` 定档案区,而 `drr.DEFAULT_ARCHIVE_DIR` 为**绝对常量**(模块位置解析),join 语义静默丢弃 root → 测试与调试运行的合成任务族误落仓库 `data/research/research_archive/research_archive/deep_research_*`(gitignored 运行产物区,**非 LIVE 部署,零 git 污染**);修复=取常量尾部三段相对锚恒随 repo_root 落位;误写合成族(恰 5 目录单家族,20260301 合成快照来源)已当场清除,既有合法内容(query_history/)零触碰;e2e 测试以「档案区在 repo_root 沙箱内」断言锚定复发防线。
- 修复C: `run_round` 返回 dict 补 `blocking` 键(终态④复核结果的 API 面可见性;首轮断言暴露)。
- 文案修正 1 处: `_validate_round_input` 判据锚定错误消息乱码片段 `D-{''}P-6`→`DP-6`(纯消息面,零语义)。

**黄金字面量预计算修正(如实,测试 fixture 预备期)**: 快照 digest 定值经 3 轮定稿(v2 增 WEIRD 事实/v3 增 HASHFORM 事实后),其中 v3 首算经 scratch 脚本位置参数错配得出 `efc57914…`(WEIRD 覆写参数错位致 metric/quality 错值),与测试 fixture 实算 `41fb4043…` 不符→ 逐字节 diff 定位 scratch 侧转录讹误并修正(与 §零.7 BRANCH-SET 同类的「独立预计算侧讹误,当场防线捕获」例证;测试 fixture 本身无缺陷;所有 ID 族定值因指纹不含快照内容而不受影响,一次定稿)。

**负向敏感性注入循环(3 真实注入,登记件=证据包 03-negative-sensitivity/negative-sensitivity-injections.txt)**: ①Gate A fail-closed 失活→2 红(单条接地负向+e2e 链)②同基底去重失活→3 红(去重/中性排除/summary 定值)③阻断声明复核失活→1 红(放行快照谎报不再拒);恢复后 57 用例全绿,模块 sha256 注入前后逐字节等值 `19a3a50e…dfd43`(shasum 双次核验),测试文件全程零改动。注入循环前三注入全部一次命中预期红,无「注入后仍绿」测试缺口情形(与 WP-A 注入2同类缺口暴露不在本轮发生,如实区分)。

---

## §一 做了什么(实现摘要)

**实现笔 c906db5**(3 files changed/1839 insertions [实取·git show --stat c906db5]):

1. **scripts/deep_research_matrix_engine.py**(816 行 [实取·wc -l 2026-11-07T06:26Z]): 证据矩阵装配与轮次推进引擎,两新记录族(`deep_research_evidence`/`deep_research_rounds`,P-B-01)挂共享档案族根。核心面(行号=c906db5 版实读):
   - **确定性 ID 族**: `EVI-{YYYYMMDD}-{sha256[:8]}`/`RD-` 同构(make_evidence_id L86/make_round_id L98);指纹不含墙钟→重放幂等,前缀避开上游已占 RT-DR-/HP-/FC-/EV-;
   - **六重 fail-closed 证据接地** `_ground_and_build_record`(L260-L336): ①快照可载(drr._load_snapshot_for_verify,结构性不可达原始采集档)②digest 重算(rp.digest_snapshot,API 无 digest 入参,禁采声明值)③Gate A 放行(rp.gate_allows_formal_research,FAIL 快照不作正式证据源)④事实接地(fact_id 命中且 value/observation_date/metric_id 逐一相等——无 provenance 的数值不得进入矩阵)⑤事实质量≠FAIL(fe 词表)⑥任务面(ACTIVE+假设成员+round≤DP-1);
   - **证据矩阵确定性汇编** `assemble_matrix`(L406-L449): cells=绑定对稀疏映射(无绑定对的格子不虚构中性值);summary 四字段+star——同一底层指标去重/方向切分/星级门槛复用 `ae._base_metric`/`ae.split_evidence_direction`/`ae.star_level_from_evidence` **同一代码路径**(与 L520-521 同构=复用调用,非平行重写);`_to_v2_item`(L396)v2 分级映射(支持/反对{contrary,explained}/中性{neutral});
   - **轮次引擎** `run_round`(L545-L678): 推进任一(①新登记证据 ≥1 ②判据可计算 ③反证检索义务未闭合)否则 hold;终止枚举序 ①RESOLVED(判据成立)②ALL_FALSIFIED(全假设证伪)③INCONCLUSIVE(预算耗尽,DP-1 硬上界)④INCONCLUSIVE(数据阻断经 `_verify_blocking` L524 对快照 gate_a 复核实证——放行态快照谎报阻断→拒收不一致声明);判据判定锚定任务档登记面(`_registered_criteria_keys` L467,tuple(sorted(pair))+(criterion,) 命中检查);轮次序贯 append-only(round=既有+1,历史轮记录不可改写);证据批两段式全量校验后原子落档(drr._write_records 预检零存在);
   - **生命周期全经 drr 既有状态保护转递**: activate_task(L451)/终态事件均=append_lifecycle_event,零新增状态值零改迁移表(AC-07.5 转递面);
   - **e2e 编排入口** `run_dev_copy_end_to_end`(L680-L816): sb.build_snapshot(write=False) 离线构建(P2-G-06 范式),快照物化运行产物区,合成任务登记常量,证据接地如实尝试(gate 放行→落档/FAIL→fail-closed 拒收如实记录理由),阻断→§4.4④ 收束;产物落 `data/research/p2_wp_b_e2e/`(不 commit);data_dir/trusted_root/as_of 透传仅测试沙箱用;模块源码零 `data/daily` 字面引用。
2. **tests/test_p2_wp_b.py**(1009 行 [实取·wc -l 同上],57 用例/14 类 [实取·unittest 收集计数 2026-11-07T06:2xZ]): 黄金字面量 38 个 GOLDEN_* 常量 [实取·正则清点](32 ID 族+2 digest+3 summary 定值+1 e2e 参数组,独立预计算+首原理 canonical sha256 交叉验证,反自证纪律)+逐要点负向/正向(§二映射表);数据纪律=临时目录合成 fixture 唯一数据源+显式注入时刻+零真实档零网络。
3. **负向敏感性测试**(执行纪律 #4): 三真实注入(Gate A fail-closed 失活/同基底去重失活/阻断声明复核失活)→套件红 2/3/1 [实取·unittest 失败计数]→恢复后 57 全绿,模块 sha256 注入前后等值 `19a3a50e…` [实取·shasum 对照],测试文件全程零改动 `0a1484c0…`(全记录=证据包 03-negative-sensitivity/negative-sensitivity-injections.txt)。三注入全部一次命中预期红,无测试缺口暴露情形(§三.4 如实区分)。
4. **本地 CI 镜像**(仿 .github/workflows/offline-tests.yml 逐套 python3 直跑): TOTAL=80/RUN=79/EXIT0=79/SKIPPED=1(test_glm_live,合同排除)/FAIL=0 [实取·p2b-run-ci.py 输出,逐套日志=证据包 04-local-ci/](=WP-A 时点 79 槽+本包新增 1 套件,零回归)。
5. **官方 e2e 真实运行(要点④,步骤10)**: `run_dev_copy_end_to_end('20261102')` 于 DEV 授权数据副本实跑 **exit=0** [实取·e2e-run-stdout.txt]: 快照 `research_snapshot_20261102`(digest `82bd93dfdf625c02`)Gate A=**FAIL**(core_missing 5 项 [实取·运行日志: CN_TOTAL_TURNOVER/FED_FUNDS/SHCOMP/SH_AMOUNT/SZCI])→证据接地 **fail-closed 拒收**(拒收理由如实落档)→R1 终态判定 **INCONCLUSIVE**(rule=§4.4④ 数据阻断,经引擎对快照 gate_a 复核实证);任务 `RT-DR-20261107-60e21f15` 全链(事件 DRAFT→ACTIVE→INCONCLUSIVE);运行产物 11 文件落运行产物区(+11/-0,全量清单=证据包 05-acceptance-anchors/anchor-verdict.txt);数据纪律锚定: data/daily 27 件前后逐行 sha256 等值 [实取·hash_tree 对照],data/research 既有 13 件零改动。

## §二 逐要点证据映射表(AC-02)

DESIGN L203 验收要点①-⑤ → 实现/证据/自检逐条(行号=实现笔 c906db5 版实读):

| 要点 | 实现位置 | 测试证据(类·用例数 [实取·类清点]) | 自检 |
|---|---|---|---|
| ① 证据接地负向(无 provenance 数值注入矩阵→fail-closed) | `_ground_and_build_record`(L260-L336 六重校验,任一不过零写入) | TestEvidenceGroundingNegative·9: 事实缺席/数值错配/日期错配(WEIRD)/指标错配(ODD)/质量 FAIL(BROKEN)/Gate A FAIL 源拒收/DEGRADED 可用正例/缺档快照/批内原子性零部分写入 + TestEvidenceSchemaNegative·6: weight 量表/direction 词表/mechanism 7 族/explained 必携解释/fact_id 形式(HASHFORM)/缺字段 | ✓ 全绿;负向注入 1(Gate A 失活)→2 红实证防线真实(单条接地+e2e 链) |
| ② 矩阵汇总确定性(同输入同输出;去重/封顶规则与 L520-521 同构) | `assemble_matrix`(L406-L449)+`_to_v2_item`(L396)——ae 三原语复用调用非平行重写 | TestMatrixAssembly·7: summary 三假设定值(5★/封顶 3★/去重 1★)/cells 稀疏映射/同基底去重/中性排除/未解释封顶/已解释不封顶/零态全零 + TestStarIsomorphism·1: 矩阵 star≡ae.star_level_from_evidence 同证据集输出 + TestMatrixDeterminism·2: 同沙箱重复汇编+跨沙箱同输入 canonical 逐字节等 | ✓ 全绿;负向注入 2(去重失活)→3 红实证 |
| ③ 轮次终止条件各自触发(条件 4 项;数据阻断→INCONCLUSIVE+登记,不编造) | `run_round`(L545-L678)终止枚举序①②③④+`_verify_blocking`(L524 阻断复核实证) | TestRoundTerminal·7: 四终态各自可达+枚举优先序全对(①>②④/②>③/③>④/部分证伪非终态)+TestRoundAdvance·2(推进三源各自+hold)+TestRoundBlockingNegative·2(放行谎报拒收零落档/缺档快照拒收)+TestRoundSequencing·6(首轮须 1/超预算/重放拒/历史档篡改字节不变/野判据拒/pair 未命中拒) | ✓ 全绿;负向注入 3(阻断复核失活)→1 红实证 |
| ④ DEV 授权数据副本端到端(数据档引用 data/daily/*_20261102.json) | `run_dev_copy_end_to_end`(L680-L816;sb write=False 离线构建,模块零 data/daily 字面引用) | TestOfflineE2E·2: 最小合成数据面→真实 sb 门禁 FAIL→fail-closed 拒收→§4.4④ INCONCLUSIVE 全链+事件链 DRAFT→ACTIVE→INCONCLUSIVE+产物沙箱内聚断言+不构成投资建议声明;同沙箱重放拒 + 官方运行(§一.5,证据包 05 全量日志) | ✓ 全绿+正式运行 exit=0 |
| ⑤ CI 零回归(工件: 测试文件+run ID) | tests/test_p2_wp_b.py(57 用例,CI 入口直跑兼容 unittest.main) | 本地 CI 镜像 80 槽 FAIL=0(§一.4,日志=证据包 04);真实 CI run ID=操作者 dispatch 面(rounds/035 登记件),执行时点尚未产生,如实登记 NOT VERIFIED@执行侧(DELIVERY §三 AC-06 分列) | 本地面 ✓;CI 面=操作者面待 run |

另有非要点直映射的防线类: TestGoldenRegistration·2(ID 族定值+注册全链)/TestAppendOnlyEvidence·2(证据重放字节不变+零墙钟同日异刻同 ID)/TestStateProtection·6(未激活登记拒/异假设拒/超预算轮拒/未激活推进拒/终态后再入拒/终态后手工迁移拒)/TestStaticPurity·3(零 data/daily 字面/零网络 import/产物区恒 data/research 子域),全绿 [实取·unittest 计数]。

## §三 偏离与如实声明

1. **BRANCH-SET 提示词侧转录讹误**(开工发现,§零.7.4 全文): 4 支提示词冻结表值与 live 不符(2 条 39 字符结构无效 SHA+2 条单字符替换)→判定=提示词侧转录讹误非分支漂移(第三源 for-each-ref 与 live 逐一一致);开工步 2 显式判据(main 尖端/计数 52/无本分支/p2-design 尖端)全过不触发停止;处置=漂移检测锚定开工真观测快照+建议操作者对合同存档件冻结章 §三.1 作勘误登记(执行Agent 无权改合同)。执行后 ls-remote 对照=DELIVERY §二。
2. **实现期缺陷修复 3 处+文案修正 1 处**(均测试首轮运行暴露、实现笔提交前修复,§零.10): 修复A=轮次记录写入状态回传补 rejected-duplicate 分支;修复B(沙箱逃逸级,如实重点登记)=`os.path.join(root, drr.DEFAULT_ARCHIVE_DIR)` 因常量为绝对值而静默丢弃 root→合成任务族误落仓库 gitignored 运行产物区(非 LIVE,零 git 污染),修复=尾部三段相对锚,误写合成族当场清除,既有 query_history/ 零触碰,e2e 测试以「档案区在 repo_root 沙箱内」断言锚定;修复C=run_round 返回补 blocking 键;文案=DP-6 错误消息乱码片段修正(零语义)。
3. **黄金 digest 定值 3 轮定稿与 scratch 侧讹误当场修正**(实现期,§零.10): v3 首算经 scratch 脚本位置参数错配得 `efc57914…`,与测试 fixture 实算 `41fb4043…` 不符→逐字节 diff 定位 scratch 侧转录讹误并修正(独立预计算侧讹误,当场防线捕获;测试 fixture 本身无缺陷;ID 族定值不受影响)。
4. **负向注入循环零测试缺口(与 WP-A 注入2先例如实区分)**: 本轮三注入全部一次命中预期红,无「注入后仍绿」暴露测试缺口情形;注入循环前的首轮测试运行暴露实现缺陷 2 处(修复A/修复B)——缺陷暴露来自测试运行而非注入循环,时序如实登记(§零.10)。
5. **官方 e2e 结果=数据阻断路径(情形(c) 合法如实,不编造)**: DEV 授权副本 20261102 快照 Gate A=FAIL(core_missing 5 项)→证据接地 fail-closed 拒收→§4.4④ INCONCLUSIVE;开工只读探针已预登记该预期路径(§零.8),正式运行以步骤10 全量日志为准(exit=0,产物 +11/-0);不以合成数据冒充放行态,不以探针替代正式运行。
6. **LIVE 树复核环境不可及(如实分列 NOT RE-VERIFIED@执行侧,不以结构性证据冒充实读 PASS)**: LIVE 部署目录不在本会话允许目录清单内(安全策略,ls 即被拒)→real_data_acceptance.py sha256 复核与 LIVE 全树 grep 本会话不可执行,WP-A 时点基线值 `f9ca189c…` 留操作者/审计面对照;结构性替代证据=①交付件(模块+测试)源码 grep real_data_acceptance/LaunchAgents/launchctl 零命中 [实取·p2b-live-iso.py 输出]②全部写入经参数落位(测试沙箱断言锚定)③data/daily 27/27 前后逐行 sha256 等值④LaunchAgents 12/12 与 WP-A 基线逐文件 sha256 全等 [实取·同上](证据包 06-live-isolation/)。
7. **CI run ID 如实分列**: 真实 CI run 属操作者 dispatch 面(rounds/035),执行时点未产生→本包交付本地面证据(§二⑤),AC-06 CI 面如实登记 NOT VERIFIED@执行侧。
8. **§零 证据包路径标注修正 4 处+时点标注修正 1 处(报告笔时点,零语义)**: §零.3/§零.7.3/§零.7.4/§零.7.6 原以类号「03」预标注证据包路径,装配终局布局定为 01-startup-forensics(与 WP-A 同构),统一修正;§零.3 时点「06:4xZ」修正为「06:03Z」(登记笔 c825ee4=06:04:17Z 前,与包内 whitelist-overlap-check 登记口径一致);§零.10 的 03-negative-sensitivity 引用本就正确。

## §四 DP 与登记参数运行后零回改自检

| 项 | 登记定值(§零.4/§零.5) | 实现值(c906db5 实读) | 零回改自检 |
|---|---|---|---|
| DP-1 轮次预算 | 双轨 N=5(提前终止;复用上游定值) | `drr.DP1_ROUND_BUDGET_DEFAULT`(=5)复用导入零重复定义;消费面=接地六重之⑥(round≤round_budget)+超预算轮拒(TestStateProtection) | ✓ 常量=登记值;零自决 |
| DP-2 权重量表 | 星级 [1,5](复用上游定值) | `drr.DP2_WEIGHT_SCALE`(=(1,5))复用;weight∈{1..5} schema 拒收(TestEvidenceSchemaNegative) | ✓ 同上 |
| DP-6 每对判据 | 每对 ≥1(复用上游定值) | `drr.DP6_MIN_DISCRIMINATING_PER_PAIR`(=1)复用;判定锚定任务档登记面(野判据拒 TestRoundSequencing) | ✓ 同上 |
| DP-3 ID 族 | 对齐型不冻结;EVI-/RD- 确定性前缀 | make_evidence_id/make_round_id(指纹不含墙钟,重放幂等) | ✓ 黄金字面量定值一次定稿 |
| P-B-01..P-B-18 | §零.5 登记表 | 逐项实现一致(§零.10 登记型参数零勘误;含预登记张力处置: explained/star/预算硬上界/阻断复核限门禁支/e2e 透传) | ✓ 18 项逐一对照 |
| API 回改面 | 无(登记型参数非 API 参数) | `inspect.signature(register_evidence/run_round)` 无 DP 参数;证据规格无 digest 入参(经 rp.digest_snapshot 重算绑定) | ✓ TestStaticPurity+schema 断言 |

登记参数无任何「先登记后回改」事实: 本包登记型参数零勘误(与 WP-A 两处勘误对照如实区分);设计张力(§零.5 已预登记的 explained/star/预算硬上界等)均先登记后实现,运行后零回改。

## §五 git 纪律与范围自检

1. **分支**: `dev/p2-impl-b` 自 BASE-P2B=`a040faa7…` 切出(§零.7.5);开工时远端 52 支无本分支(§零.7.3)。
2. **本包无并入步(与 WP-A 唯一差异点)**: f8ed401 经 R033 指定并入步 dcfc7d0 祖先在场(merge-base --is-ancestor exit 0,§零.7.6);纯线性 4 笔: c825ee4(登记笔)→c906db5(实现笔)→报告笔→终笔;BASE..HEAD merges=0 [实取·终笔前复核=DELIVERY §二取证]。
3. **白名单符合**: 新增恰 k=4 文件(§零.2),无设计件带入(本包无并入步,设计三件已在 BASE);`git diff --name-status BASE..HEAD` 预期 A=4/M=0/D=0 [实取·终笔前复核=DELIVERY §二取证]。
4. **零破坏性操作**: 零 merge 零 amend 零 reset --hard 零 force-push;reflog 复核=DELIVERY §二。
5. **main/LIVE/launchd**: main 未触碰(无 checkout/merge/push main);LIVE 零写入(§三.6,会话可及面 LaunchAgents 12/12 全等+LIVE 树 NOT RE-VERIFIED@执行侧 如实分列);launchd 零变更(launchctl 零调用)。
6. **网络**: 全程仅 git ls-remote/push(取证与交付类,合同允许);零 API/凭证/付费(§零.9)。
7. **零 tag**: `git tag -l` 前后等值(DELIVERY §二取证)。

## §六 提交前数值标注六项自检清单(§5.3,强制)

| # | 自检项 | 本文件相关数值 | 标注合规 |
|---|---|---|---|
| 1 | 行数类 | 模块 816/测试 1009/REPORT 207/DELIVERY 83(均报告笔时点) | 逐值 `[实取·wc -l <时点>]`;zip 定值=终笔登记 |
| 2 | 用例/类计数 | 57 用例/14 类;逐类 2/9/6/2/7/1/2/2/7/2/6/6/3/2(声明序=文件内类定义序: Golden/接地/schema/append-only/矩阵/同构/确定性/推进/终止/阻断负向/序贯/状态保护/静态纯度/e2e) | `[实取·unittest 收集计数]`;和=57 复核 ✓ |
| 3 | 套件/退出码 | CI 镜像 TOTAL=80/RUN=79/EXIT0=79/SKIPPED=1/FAIL=0;注入红 2/3/1;官方 e2e exit=0;探针 1 次(§零.8) | `[实取·run 脚本输出/运行日志]` |
| 4 | 文件/锚定计数 | 证据包成员数与字节数(终笔 DELIVERY §六);锚定 daily=27/research 13→24(+11/-0);LaunchAgents=12;黄金常量 38;实现笔 1839 insertions/3 files | `[实取·清点]`;日期/SHA/档键成分按合同边界出圈登记 |
| 5 | 次数类 | 提交笔数 k=4(本包无并入步,零 merge 计入);负向注入 3 次;官方 e2e 运行 1 次;只读探针 1 次;实现期缺陷修复 3 处 | `[实取·git log/注入记录/运行日志]` |
| 6 | 全量扫描 | 本文件无未标注计数类/统计类数值;`[示意·非实取]` 标记本文未使用(全部数值实取) | 报告笔提交前通读扫描 ✓;zip 定值行=终笔唯一补记 |
