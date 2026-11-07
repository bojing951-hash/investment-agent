# IA-P2-WP-A REPORT — P2 深研层第 1 实现包(深研任务与假设登记器)

> 包: IA-P2-WP-A(P2 族首包) · 执行Agent: Agent 3 · 分支: `dev/p2-impl-a`
> 基线: BASE-P2A=`0c9fc3f88bfcfab57b4b6930912045f5bd083f5a`(origin/main,开工 ls-remote 实取一致)
> 指定并入步: f8ed401(第二父,恰 1 个 merge 提交;§零.7 登记)
> 合同: IA-P2-WP-A-AC-v1.1(冻结,附录A 内嵌注入)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY/上游在场件行号一律为**本包基线工作树(并入步后 HEAD 工作树)实读**行号(2026-11-07T04:0xZ 实取);提示词注入内容引用一律标注「注入摘要,非工作树实读」。
> 数值标注边界: 本文所有计数类/统计类数值逐个二选一标注 `[实取·来源: …]` 或 `[示意·非实取]`;日期/SHA/结构编号/档键成分按合同边界出圈登记。

---

## §零 规格抄录与交付面登记(开工首步,AC-01;登记后即本合同白名单实体)

### §零.1 DESIGN §七 WP-P2-A 行四要素逐字抄录

实读 `docs/P2_DESIGN.md`(并入步带入,blob `63a1964812f0c081aef0ea38148dec82537c7416`,与 f8ed401 侧等值,§零.7 核验),WP-P2-A 行位于 L193-L197,逐字抄录:

```text
L193: **WP-P2-A 深研任务与假设登记器**
L194: - 目标: 落地 §二任务模型+§4.1 假设登记+§6.1 条件登记(append-only 记录族;三发起来源入口字段;DRAFT 校验拒收单假设任务)。
L195: - 范围: 新增深研任务/假设/条件记录模块与档案集合(挂共享档案);不改 registry/fact_engine/snapshot_builder 既有签名。
L196: - 依赖: **P0-3 落地(E2E-A 任务管理器+E2E-B WP-B4 档案)为前置**;E2E-A 冻结合同为 ID 族对齐准据(DP-3)。
L197: - 验收要点草案: ①append-only 不可变测试(重复写入/改写被拒)②DRAFT 登记负向用例(假设数 <2 拒收;合同底线 ≥2 [实取·注入合同 AC-02§4])③条件 schema 校验(字段集见 §6.1)+**登记型参数(阈值/窗口/轮次预算 DP-1/DP-2/DP-6)先登记后运行、禁回改**的负向测试(回改被拒)④snapshot_id+digest 绑定校验(篡改快照→档案校验拒绝)⑤CI 零回归(工件: 测试文件+run ID)。
```

四要素齐备(目标 L194/范围 L195/依赖 L196/验收要点 L197 共 5 条),无缺失。依赖列核验: ①「P0-3 落地为前置」——上游=[E2E-A 任务管理器=R011(#7)+E2E-B WP-B4 共享档案=R024(#11)](注入摘要,非工作树实读),二者交付件基线工作树在场实读(§零.6 登记),不要求并入指定并入步外他支;②「E2E-A 冻结合同为 ID 族对齐准据(DP-3)」——对齐面=ID 族(非任务 schema 全量,DESIGN DP-3 行 L67 实读),在场准据=`scripts/research_task_manager.py` RT- 族确定性 ID(L48-L53 实读);③范围列无真实 GLM 调用/网络出站/新数据源凭证付费要求 → 无情形(d)停止条件。

### §零.2 交付文件清单(k=4 [实取·本节清点],登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据(推导逐条附) |
|---|---|---|
| 1 | `scripts/deep_research_registrar.py` | DESIGN L195「新增深研任务/假设/条件记录模块」=恰 1 个代码模块(任务/假设/条件三记录族同模块,WP 题名「深研任务与假设登记器」L193 单数)+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」;文件名依 WP 题名「登记器」+既有 deep_/research_* 命名先例(scripts/research_task_manager.py 等) |
| 2 | `tests/test_p2_wp_a.py` | DESIGN L197①②③④工件「测试文件」+合同附录A §零(ii)「含代码则必含 tests/test_p2_wp_a.py」 |
| 3 | `docs/P2_WP_A_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P2_WP_A_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L197⑤「CI 零回归」证据落点=DELIVERY |

### §零.3 结构约束核验

- 与 `git ls-files` 零重合: 4 路径 `git ls-files <paths>` 输出=0 行 [实取·开工 2026-11-07T04:1xZ],且工作树均不存在(ls 四路均 No such file)→ 纯新增 ✓
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p2_wp_a.py)✓
- 推导无越界: 范围列恰 1 个代码模块 → scripts/ 恰 1 文件;DESIGN L197 工件未另指定模块文件名,依固定推导规则命名;未引入 DESIGN 依据外文件 ✓

### §零.4 DP 登记(开工首步登记定值,登记定值即实现值;先登记后运行,运行后禁回改)

实读 DESIGN §2.4 DP 表(L63-L72,6 DP 四要素齐备 [实取·表清点]):

| DP | 分类(DESIGN 实读) | 本包登记定值(=实现值) | DESIGN 依据 |
|---|---|---|---|
| DP-1 深研轮次预算 | 登记型(L65) | **(c) 双轨制: 固定上限 N=5 + 提前终止**(终止条件 DESIGN L130 任一触发即收束不等预算耗尽);落任务档 `registered_params.round_budget=5`;模块常量 `DP1_ROUND_BUDGET_DEFAULT=5` | L65 推荐 (c),N=5 系设计提案值 [示意·非实取] → 本包登记定值 5 |
| DP-2 证据权重量表 | 登记型(L66) | **(b) 五级=星级 1-5**(复用证据分级 v2 刻度,同 Gate B 星级门槛同构,不新增语义);落任务档 `registered_params.weight_scale=[1,5]`;模块常量 `DP2_WEIGHT_SCALE=(1,5)`;矩阵装配消费面属 WP-P2-B(本包登记+禁回改面,不实现矩阵) | L66 推荐 (b) |
| DP-6 区分性判据最低数 | 登记型(L70) | **(a) 每对假设 ≥1**;DRAFT 校验强制全对覆盖(C(n,2) 对 [示意·非实取·组合数公式],每对 ≥1 条);模块常量 `DP6_MIN_DISCRIMINATING_PER_PAIR=1` | L70 推荐 (a) 起步 |
| DP-3 ID 族 | 对齐型(L67,非登记型清单成员) | 对齐准据=E2E-A 冻结合同 RT- 族(依赖列 L196 指定):深研任务 id 取 **RT- 族成员** `RT-DR-{YYYYMMDD}-{hash8}`(确定性指纹,对齐 E2E-A make_task_id 先例 research_task_manager.py:48-53;满足共享档案 TASK_REF_RE `^RT-\S+$` research_archive.py:53);假设/条件/事件 id=HP-/FC-/EV- 同构确定性(HP- 字样系 DESIGN L67 示意,本包登记为结构性先例非冻结格式,DESIGN「本设计不冻结 ID 格式」L67 明示) | L67+L196 |
| DP-4 GLM 角色 | 确认权留用户(L68) | **本包不触及**(范围 L195=纯确定性记录模块,无 GLM 面;DESIGN L207 GLM 对接属 WP-P2-C) | L68 |
| DP-5 外部源扩展 | 确认权留用户(L69) | **本包不触及**(范围无任何数据源扩展;D3 事件日历属 WP-P2-D L211-215) | L69 |

DP 编号/数量与 DESIGN 实读一致(6 个 [实取·DESIGN §2.4 表清点]);DP-4/DP-5 未被自决实施(本包范围零触及)。

### §零.5 实现参数登记(P-A-01..,先登记后实现,运行后禁回改)

| # | 参数 | 登记定值 | 依据 |
|---|---|---|---|
| P-A-01 | 档案集合名(挂共享档案) | 共享档案族根 `data/research/research_archive/`(B4 载体先例 research_archive.py:44-46 同源根)下新增 4 集合: `deep_research_tasks`/`deep_research_hypotheses`/`deep_research_conditions`/`deep_research_events`;文件=一记录一文件 `{记录id}.json` | DESIGN L195「档案集合(挂共享档案)」+L57 §2.3(集合族沿 E2E-B DESIGN §4.1)+E2E-B DESIGN L185(载体=文件族分集合);E2E-A 任务集合 `research_tasks` 属 E2E-A 任务(E2E-B DESIGN L185 实读),深研新集合不占用其名 |
| P-A-02 | 任务记录 schema | `record_type/deep_research_task` 字段集: task_id/created_at/status/origin/question/hypothesis_ids/discriminating_criteria/condition_ids/registered_params/snapshot_id/digest_snapshot/history | DESIGN §2.2 L46-L53(生命周期+DRAFT 登记 5 要件)+§2.1 L39-L41(三来源入口字段)+§4.1 L102-103(≥2 假设+区分性判据)+§2.3 L58(记录必携 snapshot_id+digest) |
| P-A-03 | origin 恰一三类入口 | 恰一(S-1)`origin_anomaly{metric_id,snapshot_id}`/(S-2)`origin_query_id`(严格 QB-YYYYMMDD-NNN,复用 `ra.validate_id_conventions`)/(S-3)`origin_trigger{kind∈{thesis_invalidation,prediction_adjudication,rejected_rating_proposal},ref}`;零个或 ≥2 个 → 拒收 | DESIGN §2.1 L39-L41 三行实读(S-1 异常事件 metric_id+snapshot_id 落档 L39;S-2 origin_query_id 回链 L40;S-3 三入口子类 L41) |
| P-A-04 | 假设记录 schema | `record_type/deep_research_hypothesis`: hypothesis_id/task_id/created_at/statement/mechanism_story/status(初值 REGISTERED)/revision_of/revision_reason/snapshot_id/digest_snapshot/history;statement 与 mechanism_story 非空;同任务内 statement 两两互异(结构性竞争代理校验,语义竞争性=人/GLM 判断面不在本包)。**勘误(2026-11-07T05:0xZ,实现期登记修正,先于任何运行)**: 本表初版曾将 `registry_status` 误列入假设字段集——该字段语义属条件记录(P-A-05,metric 注册表身份),非假设面;实现值与本勘误后登记值一致,详见 §三 | DESIGN §4.2 L110(HypothesisRecord 字段 statement/mechanism_story/状态)+§4.1 L102(相互竞争,单假设拒收)+§6.3 L183(新假设=新记录+新 ID 关联引用原假设) |
| P-A-05 | 条件记录 schema(§6.1 字段级) | `record_type/deep_research_condition`: condition_id/task_id/hypothesis_id/created_at/字段五项 {metric_id(string)/operator∈{">=","<=",">","<"}(沿 pred_op 词表 DESIGN L157)/threshold(number)/window{mode∈{"expiry","touch"},deadline(ISO日期)或 weeks(正整数)恰一}(L159)/premise(可选非空 string)(L160)}/threshold_source∈{"registry_validation","historical_quantile","user_explicit"}(L158 三档)/source_note/direction∈{"supporting","falsifying"}(L164④)/registry_status∈{"RESOLVED","ABSENT_REGISTRY"}(metric 经 `fe.metric()` 实读,缺席→ABSENT_REGISTRY 如实标不拒收,L164①)/revision_of/revision_reason/snapshot_id/digest_snapshot/history;每假设 ≥1 条(L152) | DESIGN §6.1 L152-L164 |
| P-A-06 | 任务 id 确定性指纹 | `RT-DR-{YYYYMMDD}-{sha256[:8]}`;指纹=canonical JSON {question,origin,假设(statement+mechanism_story)升序集,discriminating_criteria 集,registered_params}(不含时间戳,重放幂等锚) | E2E-A 先例 research_task_manager.py:48-53(同窗口/规则/指标/参数→同 id) |
| P-A-07 | 假设/条件/事件 id | `HP-`/`FC-`/`EV-` + `{YYYYMMDD}-{sha256[:8]}`;指纹分别为(假设: task_id+statement+mechanism_story)/(条件: hypothesis_id+条件五字段 canonical)/(事件: task_id+from_status+to_status+note) | DP-3 对齐型结构性先例(P-A-02 同理);DESIGN L67「不冻结 ID 格式」→ 本包登记即本包实现值 |
| P-A-08 | 生命周期状态机(事件溯源) | 迁移表: DRAFT→ACTIVE;ACTIVE→{RESOLVED,ALL_FALSIFIED,INCONCLUSIVE,SUPERSEDED};{四终态}→TRACKING;TRACKING→ARCHIVED;任务档字节不可变,迁移=追加 `deep_research_events` 事件记录 {event_id,task_id,created_at,seq,from_status,to_status,note,trigger_ref};非法迁移拒收。**勘误(2026-11-07T05:0xZ,实现期登记修正,先于任何运行)**: 本表初版事件字段集无 `seq`——实现期冒烟发现 created_at 并列时按 (created_at,event_id) 折叠当前态次序不确定(注入同刻时刻的测试必触发),补 `seq`=每任务单调递增序号(初始事件 seq=1,先例=B4 `_same_day_max_seq` research_archive.py:282-290),`list_events` 按 seq 排序、`current_status` 按 seq 折叠;实现值与本勘误后登记值一致,详见 §三 | DESIGN §2.2 L46-L52(状态图+终态 4 种 L51)+append-only L50/L131 |
| P-A-09 | 重放策略(append-only 判据) | 同记录 id 文件已存在 → 一律拒收(`rejected-duplicate`,不区分内容;B4 §四行6 同款「重复写入与改写一律拒」research_archive.py:309 实读);原档字节永不动;修订=新记录(revision_of+revision_reason 必填,DESIGN L50/L164「修订=新版本记录+修订原因」);登记型参数禁回改=记录不可变+重放拒收的结构性保证 | DESIGN L50/L164+AC 要点①(L197) |
| P-A-10 | snapshot 绑定面 | 注册时 digest 经 `rp.digest_snapshot(snapshot)` **重算**(API 无 digest 入参,禁采声明值,FIX-01 纪律 B4 先例 research_archive.py:321);校验时快照文件名经 `ra.parse_snapshot_id` 规范分解派生(research_archive_YYYYMMDD[_vN].json,结构性不可达 data/daily 原始采集档,AC-07.1)+digest 复算对照,篡改→拒绝 | DESIGN §2.3 L58+§3.1 L80;AC 要点④(L197) |
| P-A-11 | import 面 | 纯标准库(json/os/re/hashlib/sys/datetime)+项目既有依赖复用调用: `research_provenance`(digest_snapshot)/`research_archive`(parse_snapshot_id,validate_id_conventions)/`e2eb_query_ir`(经 ra 转递)/`fact_engine`(metric 注册表身份实读);零新增第三方依赖,零网络 | AC-03.1/AC-05.4 |
| P-A-12 | 零墙钟纪律 | created_at/archived 类时刻缺省 now(UTC)属登记落档时刻;一切 id 指纹不含墙钟(重放幂等);测试显式注入时刻(B4 先例 research_archive.py:22-23) | 确定性测试纪律 |

### §零.6 前置实读登记(file:line,均本包基线工作树并入步后 HEAD 实读,2026-11-07T04:0xZ)

| 对象 | 登记 |
|---|---|
| P2 DESIGN §七 WP-P2-A 行 | docs/P2_DESIGN.md:193-197(§零.1 逐字抄录) |
| P2 DESIGN §二 任务模型 | 同文件:33-72(三来源 L39-41;生命周期 L46-53;共享衔接 L57-59;DP 表 L63-72) |
| P2 DESIGN §三 数据契约/快照纪律 | 同文件:76-94(快照纪律红线 L80;数据五类三态 L84-90;证据记录契约 L94) |
| P2 DESIGN §四 假设论证 | 同文件:98-131(≥2 竞争假设 L102;区分性判据 L103;证据矩阵 L108-117;反方证据强制 L121-125;轮次推进/终止 L127-131) |
| P2 DESIGN §六 可反驳性 | 同文件:148-185(条件字段五项 L154-162;推导规则 L164;Gate B 对接 L168-170;结论状态机 L174-185) |
| P2 DESIGN §八 红线 | 同文件:221-228(快照+门禁 L223;LIVE 禁写 L224;禁交易 L225;append-only L226;GLM/费用确认权 L227;如实 L228) |
| P2 INVENTORY 缺口承接 | docs/P2_INVENTORY.md:160-162(P2-G-01 深研任务/假设记录载体/P2-G-03 共享档案存储→本包承接面;P2-G-02 异常检测器=E2E-A 已落地不在本包)+86(面(a)小结) |
| E2E-A 任务管理器(上游#7) | scripts/research_task_manager.py:36-42(SCHEMA_MIN_FIELDS/STATUS_FLOW/REPLAY_POLICY)/48-53(make_task_id RT- 族确定性先例)/164-185(save_task append-only 重放)/79-156(build_task falsifiable_conditions 先例) |
| E2E-B WP-B4 共享档案(上游#11) | scripts/research_archive.py:39-46(档案族根/集合结构)/48-62(记录键/正则族)/67-91(validate_id_conventions 复用面)/96-121(parse_snapshot_id 规范分解)/304-360(append_query_record append-only 先例)/377-411(verify_* digest 复算先例) |
| E2E-B DESIGN §4.1(引用约定权威) | docs/P03_E2EB_DESIGN.md:180-185(snapshot_id 完整引用+16 位指纹 L182;task_id/query_id 格式 L183;origin_query_id/promoted_to_task_id 交叉引用 L184;档案载体文件族分集合 L185) |
| R5/R1/R3 数据接入点(标准化接口) | scripts/research_provenance.py:1210(gate_allows_formal_research)/1270(select_snapshot)/1324-1328(digest_snapshot=canonical JSON sha256 前 16 位)。注: DESIGN §3.1 L80 引 L1243/L1183-1188 与 INVENTORY 引 L1297-1301 为其各自历史基线行号,现树实测=1210/1270/1324(本包登记以现树为准,历史行号差异=上游演进非失实) |
| QB 格式(经 ra 复用) | scripts/e2eb_query_ir.py:59(QUERY_ID_RE `^QB-\d{8}-\d{3}$`)/64(ISO_DATE_PREFIX_RE) |
| 注册表身份实读面 | scripts/fact_engine.py:75-76(metric→registry by_id 查询,缺席返回 None) |

### §零.7 开工核验记录(步骤0-4,UTC 2026-11-07T03:58:48Z 起)

1. **步骤0**: `git status` clean(基点分支 dev/p1-close,非本包所致脏=零)✓;UTC=2026-11-07T03:58:48Z。
2. **步骤1-2 占位符/前置实取**: `git ls-remote origin main`=`0c9fc3f88bfcfab57b4b6930912045f5bd083f5a` 全值一致 ✓;`git ls-remote origin dev/p2-design`=`f8ed401f4274e158c06a9404149d41260e5cc0ad` ✓;`git ls-remote --heads origin` 计 51 支 ✓ 且无 `dev/p2-impl-a` ✓(原始输出=证据包 03/ls-remote-heads-start.txt)。
3. **BRANCH-SET 全表对照发现登记(如实)**: 51 支分支名集合与冻结章 §三.1 完全一致、45/51 支尖端全值相等;**6 支提示词冻结表值与 live 不符**(dev/p0-2-w5-fix3/dev/p0-baseline-restruct/dev/p03-e2eb-b2/dev/p03-final-acceptance/dev/p1-impl-f/dev/round3-reliability),其中 2 条表值为结构无效 SHA(39/41 字符,真 ls-remote 不可能产出),另 2 条与仓库多轮已提交文档记载值冲突(docs/P0_2_W5_RERUN_DELIVERY.md:16 等 ≥6 处记载 fix3=…004be…;scripts/p1_acceptance_check.py:32/tests/test_p1_close.py:65/docs/P1_CLOSE_REPORT.md:56 记载 impl-f=44a7a686f97ad923…40 字符)→ 判定=**提示词侧转录讹误,非分支漂移**(证据链=证据包 03/branchset-anomaly-analysis.txt:结构无效长度×2+已提交文档反证+fetch 零更新输出);处置=开工步 2 显式判据(计数/无本分支)全过不触发停止,执行窗口漂移检测锚定开工真观测快照,建议操作者对合同存档件冻结章 §三.1 作勘误登记(执行Agent 无权改合同);执行后 ls-remote 对照见 DELIVERY §二。
4. **步骤3/3b**: `git checkout -b dev/p2-impl-a 0c9fc3f…`(自基线 SHA 切出)+ 指定并入步 `git merge --no-ff f8ed401…`(恰 1 个 merge 提交,第二父=f8ed401,零冲突,带入设计三件 481 行)✓(取证=证据包 03)。
5. **步骤4 设计在场核验**: ①`git merge-base --is-ancestor f8ed401… HEAD` exit 0 ✓(经指定并入步);②设计三件 `git ls-tree` 双侧(HEAD vs f8ed401)blob 等值: P2_INVENTORY=`c83c3938269ffb7192da9e7810bb052885cd9bb5`/P2_DESIGN=`63a1964812f0c081aef0ea38148dec82537c7416`/P2_DELIVERY=`ac80196fd06d28019e8c5e63f86a63ab94429f99`,与合同 §零 预期三值逐一相同 ✓(原始输出=证据包 03/design-blob-*.txt)。
6. **生效前置**: 依赖列上游(E2E-A/E2E-B WP-B4)交付件基线工作树在场(§零.6 实读)✓;合同级生效前置=操作者发车时保证(注入摘要,非工作树实读)。

### §零.8 运行产物边界登记

**零运行产物**: DESIGN L193-L197 未为本包指定编排入口或真实运行要求(验收要点①-⑤工件全部=测试文件+CI run 登记类,DESIGN L197 实读;端到端走查属后续包),本包登记清单亦无编排入口文件 → 无真实运行面。data/research/ 零真实写入(测试全合成 fixture 写 tempdir,§四映射),data/daily/ 与既有快照零读取零写入;保险锚定(运行前后 data/daily+data/research 哈希清单对照)仍执行并入证据包 06(§五.4)。

### §零.9 GLM 能力级调用面判定(AC-03.7)

登记清单(§零.2)不含 GLM 能力级调用面实现(无客户端封装/调用编排/适配器类文件;范围 L195=纯确定性记录模块)→ **AC-03.7 不适用**,判定依据=清单无调用面类文件即证;真实调用/凭证/付费=零(本包任何成员不得发生,DESIGN L68/L207 GLM 对接属 WP-P2-C)。

---

## §一 做了什么(实现摘要)

(实现笔后回填)

## §二 逐要点证据映射表(AC-02)

(实现笔后回填)

## §三 偏离与如实声明

(报告笔回填;开工期发现=§零.7.3 BRANCH-SET 异常登记)

## §四 DP 与登记参数运行后零回改自检

(报告笔回填)

## §五 git 纪律与范围自检

(报告笔回填)

## §六 提交前数值标注六项自检清单(§5.3,强制)

(报告笔回填)
