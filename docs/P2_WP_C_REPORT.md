# IA-P2-WP-C REPORT — P2 深研层第 3 实现包(跟踪触发与 GLM 综合对接)

> 包: IA-P2-WP-C(P2 族第 3 包) · 执行Agent: Agent 3 · 分支: `dev/p2-impl-c`
> 基线: BASE-P2C=`f0648841fd72ad75862a0b8ef13f69a5880fdddf`(origin/main,开工 ls-remote 实取一致;本包**无并入步**,f8ed401 经祖先在场)
> 合同: IA-P2-WP-C-AC-v1.0(冻结,附录A 内嵌注入)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY/上游在场件行号一律为**本包基线工作树(BASE-P2C checkout)实读**行号(2026-11-07T07:39Z-08:0xZ 实取);提示词注入内容引用一律标注「注入摘要,非工作树实读」。
> 数值标注边界: 本文所有计数类/统计类数值逐个二选一标注 `[实取·来源: …]` 或 `[示意·非实取]`;日期/SHA/结构编号(WP-P2-A/B/C、P2-G-08)、档键成分(ID 格式字符串)按合同边界出圈,不强制标注。

---

## §零 规格抄录与交付面登记(开工首步,AC-01;登记后即本合同白名单实体)

### §零.1 DESIGN §七 WP-P2-C 行四要素逐字抄录

实读 `docs/P2_DESIGN.md`(基线工作树在场,blob `63a1964812f0c081aef0ea38148dec82537c7416`,与 f8ed401 侧等值,§零.7 核验),WP-P2-C 行位于 L205-L209,逐字抄录:

```text
L205: **WP-P2-C 跟踪触发与 GLM 综合对接(PENDING)**
L206: - 目标: 落地 S-3 跟踪触发入口(入口子类 3 个 [实取·本文 §2.1 S-3 枚举,2026-11-02]: 论点触发器/预测裁决/拒写提案)+§6.2/6.3 评估与证伪后处置;GLM 综合能力级对接(§五)。
L207: - 范围: 触发监听(论点触发器/预测裁决/拒写提案三类入口)+条件程序评估+结论状态机;GLM 对接仅接口预留(**待 R019 定稿,实现包阶段对齐**;R019 定稿前零调用)。
L208: - 依赖: WP-P2-A/B;**R019 定稿(在途)**;真实 GLM 调用与费用——**确认权留用户**(DP-4)。
L209: - 验收要点草案: ①触发入口各子类端到端用例(子类 3 个 [实取·本文 §2.1 S-3 枚举,2026-11-02]) ②条件评估与每日观察先例口径一致性(观察窗内观测才参与裁决)③证伪后处置路径断言(路径 3 条 [示意·非实取,设计提案];FALSIFIED 不可改写/关联论点走门禁/新任务闭环)④GLM 零调用断言(定稿前)⑤CI 零回归。
```

四要素齐备(目标 L206/范围 L207/依赖 L208/验收要点 L209 共 5 条),无缺失;C 行与 A 行(L193-L197,任务/假设/条件登记器)、B 行(L199-L203,证据矩阵与轮次引擎)四要素逐项可区分(题名/目标节引用/范围模块/依赖列/要点集全不同),不触发合同 §零(iv) 首项停止条件。依赖列核验: ①「依赖: WP-P2-A/B」——上游=同族前包 WP-P2-A(R033 #23 审计 PASS)与 WP-P2-B(R035 #24 审计 PASS)(两者审计状态系注入摘要,非工作树实读;合同冻结章 §二 生效前置已登记),其交付件基线工作树在场实读(§零.6: `scripts/deep_research_registrar.py` 842 行 [实取·wc -l,2026-11-07T07:52Z]+`tests/test_p2_wp_a.py`+`docs/P2_WP_A_REPORT.md`+`docs/P2_WP_A_DELIVERY.md`[REPORT §零.2 清单 k=4 同源对照];`scripts/deep_research_matrix_engine.py` 816 行 [实取·wc -l,同上]+`tests/test_p2_wp_b.py`+`docs/P2_WP_B_REPORT.md`+`docs/P2_WP_B_DELIVERY.md`[REPORT §零.2 清单 k=4 同源对照]),依赖列未要求并入他支(本包无并入步,§零.7);②「R019 定稿(在途)」——实况=R019 GLM-DESIGN 已 PASS 定稿封存 @`0c8de3c3bece78dd2d9f0d8928a817b597e3104e`(载体分支 dev/p03-w2-glm-design,ls-remote 实取尖端一致 [实取·开工 ls-remote,2026-11-07T07:39Z];合同冻结章 §二 同款登记「(在途)」系设计成文时点注记,如实登记不改 DESIGN,AC-02.5 纪律);「实现包阶段对齐」=本包 GLM 接口预留与 R019 定稿字段面对齐(§零.5 P-C-14,跨支只读 `git show FETCH_HEAD:docs/P03_W2_GLM_DESIGN.md` 实读 [实取·开工 2026-11-07T07:4xZ,§三(a)(c)/§五(2) 字段名对齐]);③「真实 GLM 调用与费用——确认权留用户(DP-4)」——本包零真实调用零费用(要点④+合同 §七.4+排除事项 5 三重约束,DP-4 PENDING 留痕不实施,§零.4);④范围列无真实 GLM 调用·网络出站·新数据源凭证付费要求(「GLM 对接仅接口预留」=确定性接口面+本地桩,非调用面)→ 无情形(d)停止条件。

### §零.2 交付文件清单(k=4 [实取·本节清点],登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据(推导逐条附) |
|---|---|---|
| 1 | `scripts/deep_research_tracking_engine.py` | DESIGN L207「触发监听(论点触发器/预测裁决/拒写提案三类入口)+条件程序评估+结论状态机;GLM 对接仅接口预留」=恰 1 个代码模块(三分句并列修饰单数集成面「跟踪触发」,与 WP-A 行 L195「新增深研任务/假设/条件记录模块」、WP-B 行 L201「新增矩阵装配与轮次引擎模块」同为单模块多面式样;题名 L205「跟踪触发与 GLM 综合对接」单包佐证)+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」;文件名沿 WP-A/B `deep_research_*` 族命名先例(deep_research_registrar.py/deep_research_matrix_engine.py) |
| 2 | `tests/test_p2_wp_c.py` | DESIGN L209①②③④工件「用例/断言」+合同附录A §零(ii)「含代码则必含 tests/test_p2_wp_c.py」 |
| 3 | `docs/P2_WP_C_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P2_WP_C_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L209⑤「CI 零回归」证据落点=DELIVERY |

### §零.3 结构约束核验

- 与 `git ls-files` 零重合: 4 路径 `git ls-files -- <paths>` 输出=0 行 [实取·开工 2026-11-07T07:52Z,输出入证据包 01-startup-forensics],且工作树均不存在(ls 四路均 No such file)→ 纯新增 ✓
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p2_wp_c.py)✓
- 推导无越界: 范围列恰 1 个代码模块 → scripts/ 恰 1 文件;「GLM 对接仅接口预留」系模块内接口面非独立调用面模块(DESIGN L207 措辞「仅接口预留」+L208「定稿前零调用」,非客户端封装/调用编排包——R019 §七 WP-G1-G4 才是 GLM 层实现包系,本包仅预留对接接口);未引入 DESIGN 依据外文件 ✓

### §零.4 DP 登记(开工首步登记定值,登记定值即实现值;先登记后运行,运行后禁回改)

实读 DESIGN §2.4 DP 表(L63-L72,6 DP 四要素齐备 [实取·表清点]);本包为 P2 族第 3 包,DP-1/DP-2/DP-6 已由同族前包 WP-P2-A 登记定值并落其模块常量与任务档 `registered_params`(WP-A REPORT §零.4 同源),本包**复用导入上游定值,不重复定义、不改写**(对齐上游=复用调用):

| DP | 分类(DESIGN 实读) | 本包登记定值(=实现值) | 依据与复用面 |
|---|---|---|---|
| DP-1 深研轮次预算 | 登记型(L65) | **(c) 双轨: 固定上限 N=5+提前终止**;本包消费面=无直接消费(结论评估以条件窗口为界,不以轮次为界,DESIGN L168「程序判定,观察记录驱动」);透传面=GLM 输入构建器透传任务档 `registered_params`(echo);实现值=`drr.DP1_ROUND_BUDGET_DEFAULT`(=5) | L65;复用 `deep_research_registrar.py` L39 |
| DP-2 证据权重量表 | 登记型(L66) | **(b) 五级=星级 1-5**;本包消费面=矩阵经 dm.assemble_matrix 汇总后透传 GLM 输入(evidence_matrix 含 summary/star);实现值=`drr.DP2_WEIGHT_SCALE`(=(1,5)) | L66;复用同上 L40,经 `deep_research_matrix_engine.py` L406-L445 同一汇编路径 |
| DP-6 区分性判据最低数 | 登记型(L70) | **(a) 每对 ≥1**;本包消费面=触发后再研究 spawn 走 drr.register_deep_research_task DRAFT 校验(判据覆盖兜底复用);实现值=`drr.DP6_MIN_DISCRIMINATING_PER_PAIR`(=1) | L70;复用同上 L41 |
| DP-3 ID 族 | 对齐型(L67,非登记型清单成员) | 新记录族续用上游确定性 ID 构造先例: 触发 `TRG-{YYYYMMDD}-{sha256[:8]}`/结论 `CON-{YYYYMMDD}-{sha256[:8]}`/处置 `DSP-{YYYYMMDD}-{sha256[:8]}`(指纹不含墙钟,重放幂等;前缀避开上游已占 RT-DR-/HP-/FC-/EV-/EVI-/RD-) | L67「不冻结 ID 格式」+WP-A/B 先例(P-A-06/P-A-07/P-B-ID);构造原语复用 `drr._hash8` |
| DP-4 GLM 角色 | 确认权留用户(L68) | **触及面=仅接口预留+零调用断言,真实调用/费用零实施(PENDING 留痕)**: DESIGN L207「GLM 对接仅接口预留(待 R019 定稿,实现包阶段对齐;R019 定稿前零调用)」+合同冻结章 §五「真实调用面属后续专门步/包,发车硬门=用户实批」——本包交付=输入构建器+适配器协议+PENDING 桩(缺席登记返回,R019 §三(b)3 同款)+显式依赖注入点;**非自决实施**(要点④ GLM 零调用断言为交付内容本身) | L68+L207+L209④ |
| DP-5 外部源扩展 | 确认权留用户(L69) | **本包不触及**(范围无任何数据源扩展;D3 事件日历属 WP-P2-D L211-215) | L69 |

DP 编号/数量与 DESIGN 实读一致(6 个 [实取·DESIGN §2.4 表清点]);DP-4/DP-5 未被自决实施(DP-4=接口预留+PENDING 桩,零真实调用;DP-5 零触及)。

### §零.5 实现参数登记(P-C-01..P-C-18,先登记后实现,运行后禁回改)

| # | 参数 | 登记定值 | 依据 |
|---|---|---|---|
| P-C-01 | 载体与集合 | 3 新集合挂共享档案族根: `deep_research_triggers`(触发)/`deep_research_conclusions`(结论)/`deep_research_disposals`(处置);载体=`drr.ARCHIVE_FAMILY`/`drr.DEFAULT_ARCHIVE_DIR` 复用引用(不占用上游 4+2 既有集合名) | DESIGN §2.3 L57 共享档案;WP-A P-A-01/WP-B P-B-01 先例 |
| P-C-02 | 记录类型与 ID 族 | record_type 三值=deep_research_trigger/conclusion/disposal;ID=TRG-/CON-/DSP-{YYYYMMDD}-{sha256[:8]}(§零.4 DP-3 行);指纹 canonical json sort_keys,零墙钟 | 同上 |
| P-C-03 | 触发子类词表 | 恰 3 值复用上游 `drr.ORIGIN_TRIGGER_KINDS`=(thesis_invalidation,prediction_adjudication,rejected_rating_proposal)(WP-A P-A-03 登记,=DESIGN §2.1 L41 S-3 枚举三子类);零新增枚举值 | DESIGN L206「入口子类 3 个」;drr.py L90-92 实读 |
| P-C-04 | 触发 payload schema(按子类) | thesis_invalidation: {target(论点/观点标识,非空str), trigger_id(非空str), engine_status(恒"triggered"——L503 门禁仅引擎核验已触发者构成 S-3①入口,not_triggered/sustaining/unverifiable 一律拒收), verified_by(非空str)};prediction_adjudication: {pred_ref(非空str), event∈("adjudicated","premise_fulfilled"), verdict∈{hit,miss,inconclusive,not_yet_triggered}\|null(event=premise_fulfilled 时恒 null;adjudicated 时恒非 null), adjudicated_by(非空str)}(verdict 词表=report_generator.py L534 裁决四态实读;premise_fulfilled=DESIGN L41②「前提兑现转观察中」);rejected_rating_proposal: {view_ref(非空str), proposed_rating∈ae.ALLOWED_RATINGS(4 档实读 allocation_engine.py L63), gate_status(恒"rejected",L522 被拒提案留档/L1099 status=="rejected" 先例), reason(非空str)} | DESIGN §2.1 L41;report_generator.py L503/L522/L534/allocation_engine.py L63 实读 |
| P-C-05 | 触发→再研究衔接 | spawn 走 `drr.register_deep_research_task(question,hypotheses,criteria,snapshot,origin={"origin_trigger":{kind,ref}})`——kind/ref 取自触发档(origin 恰一校验+DRAFT 五要件兜底复用上游);快照绑定 digest 经 rp.digest_snapshot 重算(禁采声明值) | DESIGN §2.1 L41「任务档携 origin_trigger」;drr.py L533-L651 复用 |
| P-C-06 | 条件评估观察窗口径 | 仅窗口内观测参与裁决: 窗口=[window_start, deadline] 闭区间;window_start=premise 兑现日(条件带 premise 且评估输入携 premise_fulfilled_on 时)否则条件档 created_at 日期段;deadline=window.deadline 或(created_at 日期+weeks×7 日);窗口外观测一律不参与(每日观察先例 report_generator.py L537「观察窗内观测才参与裁决/窗口结束后的数据不得用于裁决」+allocation_engine.py L819-L826 `_window_obs` [start,end] 过滤同款) | DESIGN L209②+L168;先例实读 |
| P-C-07 | touch/expiry 语义 | touch: 窗内任一观测满足比较式→TRIGGERED(可提前,触及单调,allocation_engine.py L902/L918-931 同款);expiry: as_of<deadline→PENDING(不得提前裁决,L538 同款);as_of≥deadline: 取窗内≤deadline 最新观测判定满足→TRIGGERED/不满足→NOT_TRIGGERED;窗内零可用观测→DATA_INSUFFICIENT(不硬判,L903-904/L906 同款)。登记简化: 本模块观测源=快照事实级(fact observation_date),无逐指标交易日历覆盖模型(window_coverage 属市场锚点面),touch 到期未触发的 NOT_TRIGGERED 判定以窗内存在可用观测为数据充分性判据(零观测→DATA_INSUFFICIENT),如实登记非冒充 | DESIGN L209②;先例实读+§八 L228 如实纪律 |
| P-C-08 | premise 口径 | 条件 premise(WP-A FC- 字段,叙述性 string\|null)无法程序判定;评估输入显式携 premise_fulfilled_on(引擎核验产物,按 condition_id 键)才开窗;兑现日晚于 deadline→NOT_ACTIVATED(不激活,截止日不顺延,allocation_engine.py L762-L764 同款);premise 在场而无兑现输入→NOT_YET_IN_WINDOW | DESIGN L160/L164;record_observations 前提纪律实读 |
| P-C-09 | 比较符与判定算子 | 复用 `ae.COMPARATORS`(>=/<=/>/< 同一代码路径,allocation_engine.py L95-101);操作数=(观测 value, 条件 threshold) | 复用调用纪律 |
| P-C-10 | 结论状态机 | 状态集: 未裁决(无记录默认)→PARTIAL_SUPPORT(部分支持)/PARTIAL_FALSIFIED(部分证伪)(轮次中,可续评)→终态 4 值 CONFIRMED/FALSIFIED/EXPIRED_UNRESOLVED/INCONCLUSIVE(DESIGN L174-L180 逐字枚举);当前态=结论记录流按 created_at+conclusion_id 确定性排序折叠(append-only 推导,不改档,drr.current_status 同款范式);**终态后再评一律拒收**(FALSIFIED 不可改写+终态不可重开,L183 同款+`_is_final_prediction` 终态纪律 allocation_engine.py L691-L709 先例);确定性优先序: FALSIFIED>CONFIRMED>EXPIRED_UNRESOLVED>INCONCLUSIVE(证伪向触发优先于支持向成立=保护性优先;同点平局不可能——判定互斥分支) | DESIGN §6.3 L174-L185 |
| P-C-11 | 终态判定映射 | ①∃证伪向条件 TRIGGERED→FALSIFIED(L177「证伪向条件触发」);②∃支持向条件 TRIGGERED ∧ 矩阵 summary 未解释重大反证=False→CONFIRMED(L176「窗口内支持向条件成立且无未解释重大反证」;未解释重大反证旗经 dm.assemble_matrix 复用调用取 summary[hypothesis_id]["未解释重大反证"],零证据时空集无反证=False 如实);③支持向 TRIGGERED ∧ 未解释重大反证=True→PARTIAL_SUPPORT 非终态驻留(反证义务未闭合 §4.3,等待解释性证据或证伪向触发;终态判据被阻断不得降格 CONFIRMED 不得改判,如实驻留);④全条件窗口闭合(无 PENDING/NOT_YET_IN_WINDOW/NOT_ACTIVATED 待决)且非①②③: ∃DATA_INSUFFICIENT→INCONCLUSIVE(L179 数据阻断);否则→EXPIRED_UNRESOLVED(L178 窗口结束未触发);⑤窗口未闭合且非①②③: ∃证伪向条件窗内已现不利观测(expiry 待期终)→PARTIAL_FALSIFIED;∃支持向 TRIGGERED∧反证未解释→PARTIAL_SUPPORT(④③复用);否则→未裁决维持(零追加记录,评估结果如实返回) | DESIGN §6.3 L174-L180+§4.3 L123-125 |
| P-C-12 | 数据阻断面 | 评估取数经快照纪律三重: 快照可载(drr._load_snapshot_for_verify 规范分解派生,结构性不可达 data/daily)+digest 重算(rp.digest_snapshot)+Gate A 放行(rp.gate_allows_formal_research,FAIL 快照不作正式评估源→评估返回 blocked 如实,不编造观测);观测抽取=快照 facts 列表按 metric_id 聚合(quality_status≠FAIL 且 value 为 number,fact_engine 口径数据不足不填 0 承接: 缺值条件→DATA_INSUFFICIENT 不硬判) | DESIGN §3.1 L80+§6.2 L168;dm._fact_index 同款先例 |
| P-C-13 | 证伪后处置三路径 | 单处置档 DSP- 三路径一次成套: 路径①假设标记=引用 FALSIFIED 结论档(结论档字节不可改写,标记即终态档本身;可选实质新假设经 drr.revise_hypothesis=新记录+新ID+revision_of 关联引用原假设,L183 逐字);路径②关联论点/观点触发复核=结构化 review_request 留档处置档内{target,path:"terminal_gate_forward_flow",requires:("engine_verified_trigger","gte2_new_independent_evidence"),decided_by:"gate"}(终态门禁正向流程要求=触发器被引擎核验或≥2 项新增独立证据,L503/L184 同款;**深研层不直接改写状态**——模块零 thesis.json/allocation_views.json 写路径,由既有门禁裁决,L184「由门禁裁决是否进入已失效等终态」逐字承接);路径③跟踪处置=任务 TRACKING→ARCHIVED 经 drr.append_lifecycle_event(登记迁移表既有对,drr.py L80);可选闭环后续任务经 origin_trigger 发起(P-C-05 同款,触发子类由调用方显式携引擎核验事件,模块不发明触发);前置校验=该假设当前结论恒为 FALSIFIED(未证伪/未终态→拒收) | DESIGN §6.3 L182-L185 |
| P-C-14 | GLM 接口预留(R019 对齐) | ①输入构建器 `build_glm_synthesis_input`: {contract_version:"p2-gsi-1.0"(标识符), mode:"A", snapshot_binding:{snapshot_id,snapshot_digest(重算),gate_a}, task_ref:{task_id,question}, hypotheses(矩阵假设集含 statement/mechanism_story), evidence_matrix:{cells,summary,registered_params}(经 dm.assemble_matrix 复用汇编), prompt_contract:{language:"zh",counter_evidence_required:True,min_competing_hypotheses:2,numeric_grounding_required:True}}——字段名与 R019 GLMResearchInput(contract_version/mode/snapshot_binding/task_ref/prompt_contract)对齐 [实取·跨支只读 P03_W2_GLM_DESIGN.md §三(a) L62-70,2026-11-07T07:4xZ];②输出契约=结构化竞争假设陈述与置信标注(DESIGN L140),预留校验面 `validate_glm_synthesis_output`: hypotheses≥2(强制项 L141)+每假设 falsifiable_conditions≥1+confidence∈{high,medium,low}(R019 §三(c) L102 三档)+absent_ack 在场——**轻量结构校验仅属接口预留面,R019 WP-G2 结构化输出校验器(竞争性/区分性/阈值来源全量校验)不在本包重复实现**(承接登记);③适配器协议=单方法 synthesize(payload)→dict;④PENDING 桩 `PENDING_GLM_ADAPTER`: 返回缺席登记 {status:"ABSENT_PENDING_APPROVAL",...}(R019 §三(b)3 缺席登记同款: 不部分产出、不静默跳过、状态不因此推进),零调用零网络;⑤注入点=显式依赖注入参数 adapter(缺省=PENDING_GLM_ADAPTER),桩注入点 file:line 于 §零.10 登记 | DESIGN §五 L135-L144+L207;R019 定稿实读 |
| P-C-15 | 快照纪律与零直读 | 模块源码零 `data/daily` 路径字面/零原始研究档案直开;一切快照读取经 drr._load_snapshot_for_verify(快照文件由 snapshot_id 规范分解派生);研究状态零直改(§6.2 L169「回写必须经 Gate B 状态保护门禁」——本模块对 thesis/allocation/prediction 状态档零读写路径) | DESIGN §3.1 L80+§6.2 L169+§八 L223 |
| P-C-16 | append-only 落档 | 全记录族经 `drr._write_records`(预检零存在→原子写,同 id 重放一律 rejected-duplicate 零写入);记录 schema 校验 issues 列表风格(空=合法,上游同款);评估/处置/触发全携 history 初始条目 | WP-A P-A-09/WP-B 同款;B4 §四行6 先例 |
| P-C-17 | 零网络纯度 | import 面纯标准库(json/os/sys/datetime)+项目既有模块(drr/dm/rp/ae/ra);零 requests/urllib/socket/http/openai;零第三方新依赖,零 requirements 改动 | 合同 §五.4/AC-03.1 |
| P-C-18 | 零墙钟纪律 | ID 指纹不含墙钟(ymd 仅取 created_at 日期段);created_at 缺省 now 仅属登记落档时刻(评估 as_of 为显式必填参数,禁墙钟判定) | WP-A/B 同款;L131 轮次不可改写承接 |

### §零.6 前置实读登记(开工实读 file:line;均为本包基线工作树实读 2026-11-07T07:39Z-07:52Z)

- **DESIGN 三件**: P2_DESIGN.md §2.1 L41(S-3 三子类)/§2.2 L46-L53(生命周期)/§2.4 L63-L72(DP 表)/§3.1 L80(快照纪律)/§4.3 L123-L125(反证义务)/§6.1-L164(条件规则)/§6.2 L168-L170(评估与 Gate B)/§6.3 L174-L185(结论状态机+证伪后处置)/§七 L205-L209(WP-C 行)/§八 L223-L228(红线);P2_INVENTORY.md/P2_DELIVERY.md 在场(blob 等值 §零.7)
- **上游 WP-P2-A 在场件**(REPORT §零.2 清单 k=4 同源): `scripts/deep_research_registrar.py`——L37-L41(DP 定值常量)/L60-L63(ID 前缀)/L73-L82(迁移表含 TRACKING→ARCHIVED)/L86-L92(条件词表+ORIGIN_TRIGGER_KINDS)/L219-L258(validate_condition)/L505-L524(_write_records)/L533-L651(register_deep_research_task)/L657-L706(load_task/current_status)/L709-L737(append_lifecycle_event)/L742-L773(revise_hypothesis)/L778-L801(_load_snapshot_for_verify)
- **上游 WP-P2-B 在场件**(REPORT §零.2 清单 k=4 同源): `scripts/deep_research_matrix_engine.py`——L59-L75(集合/ID 前缀)/L252-L258(_fact_index)/L337-L350(register_evidence)/L406-L445(assemble_matrix+summary 未解释重大反证)/L451-L456(activate_task)/L545-L657(run_round)
- **数据接入点(标准化路径)**: 快照事实=快照 facts 列表经 drr._load_snapshot_for_verify 加载(dm._fact_index L252-L258 同款聚合先例);digest=rp.digest_snapshot(research_provenance.py L1324 定义实读);Gate A=rp.gate_allows_formal_research(L1210-L1213 定义实读: PASS/DEGRADED 放行)
- **S-3 入口锚点(DESIGN §2.1 L41 所引)**: report_generator.py L503-L504(终态门禁=失效/升级触发器被引擎核验已触发或≥2 项新增独立证据)/L505(确信度门禁)/L518-L522(证据分级 v2+评级变更门禁被拒提案留档)/L525-L526(pred 规格 pred_op/pred_mode expiry|touch/pred_weeks/前提)/L534(预测裁决四态 hit/miss/inconclusive/not_yet_triggered)/L537(观察窗内观测才参与裁决,窗口结束后的数据不得用于裁决)/L538(expiry 截止日未到不得提前裁决/touch 触及即判);allocation_engine.py L63(ALLOWED_RATINGS 四档)/L73-L78(五态+VERIFY_MODES)/L95-L101(COMPARATORS)/L104(机制 7 类)/L691-L709(_is_final_prediction 终态不可重开)/L726-L816(record_observations 前提兑现开窗/截止日不顺延 L762-L764)/L819-L826(_window_obs 窗内过滤)/L895-L907(evaluate_predictions touch 可提前/expiry 到期判/无数据不硬判)/L1066(五态口径行);daily_prediction_observer.py L122-L131(observe 每日观察先例);data_validator.py L372-L377(FAIL→禁止一切长期状态回写)
- **跨支只读(R019 对齐源)**: dev/p03-w2-glm-design@`0c8de3c3bece78dd2d9f0d8928a817b597e3104e`(ls-remote 实取尖端 [实取·开工 2026-11-07T07:39Z])`git show FETCH_HEAD:docs/P03_W2_GLM_DESIGN.md`——§三(a) L62-L70(GLMResearchInput 字段名)/§三(c) L93-L115(HypothesisSet 七字段+confidence 三档 L102)/§三(b) L84-L89(失败三径,缺席登记径 3=L87)/§五(2) L163-L169(Gate B 三态门禁/深研层不直接改写状态);只读禁改,零 checkout 切换

### §零.7 开工核验(2026-11-07T07:39Z-07:52Z UTC,输出原样入证据包 01-startup-forensics)

- `git ls-remote origin main`=f0648841fd72ad75862a0b8ef13f69a5880fdddf(全值=BASE-P2C ✓);`git ls-remote --heads origin` 总数=53 [实取·逐行清点] 且无 dev/p2-impl-c(在场即预创建违规——实测无 ✓);53 支尖端与合同冻结章 §三.1 全表逐行人工比对全值一致零漂移 ✓;`git ls-remote origin dev/p2-design` 尖端=f8ed401f4274e158c06a9404149d41260e5cc0ad(前 7 位=f8ed401 ✓)
- 步骤0: `git status` clean(开工前分支=dev/p2-impl-b@617a93a,工作树 clean,非本包所致脏=无)✓;UTC 时刻=2026-11-07T07:39:36Z
- 步骤3: `git checkout -b dev/p2-impl-c f0648841…`(自基线 SHA 切出,非盲切;因基线 merge commit 非本地对象,先 `git fetch origin main` 获取后切建,fetch=只读获取零改动)✓
- 步骤4 设计在场核验: ①`git merge-base --is-ancestor f8ed401f4274e158c06a9404149d41260e5cc0ad HEAD`=exit 0 可达 ✓(经 R033 指定并入步 dcfc7d0 入 main,R035 同链继承,本包无并入步);②P2 设计三件 `git ls-tree` 双侧(HEAD vs f8ed401)blob 逐一相同: INVENTORY c83c3938269ffb7192da9e7810bb052885cd9bb5/DESIGN 63a1964812f0c081aef0ea38148dec82537c7416/DELIVERY ac80196fd06d28019e8c5e63f86a63ab94429f99,且与合同冻结章 §三 登记值相同 ✓
- 步骤5 规格抄录: §零.1(四要素齐备,C 行与 A/B 行逐项可区分,无 §零(iv) 冲突处置触发)

### §零.8 运行边界判定

DESIGN L209 验收要点 5 条逐条对照: ①触发入口各子类端到端用例=测试面(tests 内三类入口 intake→落档→spawn 端到端);②条件评估口径一致性=测试面(窗内过滤/touch-expiry/premise 用例);③证伪后处置路径断言=测试面(三路径断言);④GLM 零调用断言=测试面+源码纯度面;⑤CI 零回归=CI 面(操作者 dispatch)。**要点集无真实数据运行要求(对照 WP-B 行 L203④「DEV 授权数据副本端到端」明文不在 C 行)**;范围列无编排入口要求 → 本包**零运行产物**,`data/research/` 无新增(运行产物边界条款: 无真实运行面→登记零运行产物+对照依据,本节即对照依据)。全量测试+本地 CI 镜像运行产物(临时目录沙箱)不落 `data/research/`。

### §零.9 AC-03.7 判定(GLM 能力级调用面合成桩边界)

**适用**(登记清单含 GLM 对接接口预留面,依 DESIGN L207「GLM 对接仅接口预留」以最保守口径按适用处置): 该面测试一律本地合成桩覆盖(显式依赖注入 adapter 参数,缺省 PENDING_GLM_ADAPTER 缺席登记桩),禁任何真实出站;桩注入点登记=本模块 adapter 注入参数定义处+PENDING 桩返回处(file:line 于 §零.10 实现笔登记);**零真实 GLM/LLM 调用、零凭证、零付费**(要点④断言+§七.4+排除事项 5 三重约束;真实调用面属后续专门步/包,DP-4 PENDING 留痕)。

### §零.10 实现期登记(实现笔追加;登记后禁回改)

**交付件定值**(wc -l 实取 2026-11-07T08:3xZ): `scripts/deep_research_tracking_engine.py` 1004 行/`tests/test_p2_wp_c.py` 1386 行(77 用例 [实取·pytest --collect-only]/13 类 [实取·class Test 清点])。模块 sha256(测试全绿态,负向敏感性基线=还原后)=`fd927a94340490be5a07a077f0aafe4e890753a92d7e5da5c2444edf5eb897fe`。

**桩注入点登记(§零.9/AC-03.7 承接)**: 适配器协议=`GLMSynthesisAdapter`(类 L822,`synthesize` L831-L834,NotImplementedError);PENDING 桩=`PendingGLMAdapter`(类 L837,缺席登记返回 L841-L852,`called=False/network=False` 零调用零网络);显式依赖注入点=`synthesize_competing_hypotheses(adapter=…)` 参数定义 L931-L934,缺省选择 L945(`adapter is not None else PENDING_GLM_ADAPTER`),注入协议校验零出站;测试一律本地合成桩(TestGLMInterface Stub 类,禁真实出站)。

**黄金值独立预计算**: 25 字面量(GOLDEN 表: TRG-×4/digest×1/RT-DR-×2/HP-×5/FC-×7/CON-×5/DSP-×1)由独立脚本首原理复算(自带 canonical sha256,不从被测模块导入计算;JSON sort_keys 指纹件逐项字面书写)与模块沙箱运行链交叉验证 24 项 GOLDEN-OK+digest 独立 EQUAL(脚本侧 ACT 槽位未填的 1 项 MISMATCH 行系脚本自身登记缺陷,已注记,证据包 03/golden-precompute);测试内 CON/DSP 指纹复算用自带 `_h8` hashlib 首原理实现(禁导入模块计算,反自证纪律)。

**实现期缺陷修复 3 处(如实登记,均为实现笔内发现+当场修复,零 LIVE 零 git 污染)**: ①`list_triggers`(L278-L281)首稿语法错误(`return _list_collection COLLECTION_TRIGGERS if False else _list_collection(…)` 非法语句)——py_compile 首次编译即红,未入任何测试运行,修复为直呼;②`_decide_status` CONFIRMED 分支(L541-L546)NameError——reasons 首项 f-string 引用 `e` 在推导式外,首次冒烟裁决即触发,修复为 `[… for e in s_trig]` 推导式;③`GLMSynthesisAdapter` 类文档字符串(L825)非 f-string 字面 `{GLM_REAL_CALL_FACE}`(装饰性缺陷,不影响行为)——修复为纯文本表述。三处修复均在登记参数语义零变更前提下进行(P-C-01..18 定值不受触)。

**测试面实现期登记(测试侧 fixture/锚定,非模块面,零 DP 回改)**: ①窗口敏感性锚: 黄金 fixture 之外补 `SNAPSHOT_POST`(截止日后观测 2026-12-05=7.5 晚于 11-16/11-30 两档 deadline)——窗口过滤负向注入①的直击锚(无此锚则截止日后观测翻转不可见);②PARTIAL_SUPPORT 驻留语义钉住(P-C-11③): unexplained 反证证据档 append-only 不可改写→「事后解释」路径在现有上游面不存在(新证据 explained=True 不改旧档),驻留态唯一出路=证伪向触发→FALSIFIED(测试 `test_partial_support_unexplained_counter_then_falsified` 两段式钉住: ③驻留→premise 兑现→①FALSIFIED,prior_status=PARTIAL_SUPPORT 续评合法);③任务生命周期面: evaluate/adjudicate 不设任务态前置(登记口径 P-C-11 无任务面前置;证据登记的 ACTIVE 门禁属 dm 上游自有面 `_check_task_face`),测试按登记口径覆盖 DRAFT/ACTIVE 两态评估;④测试调试图期 HYP_G 增补第 2 条件(us10y.real>=2.0 expiry)修正条件索引错位——测试侧 fixture 修正,TASK3 族无黄金 ID 依赖(运行期捕获),黄金链零影响。

**负向敏感性(真实注入 3 处,全部一次命中预期红,证据包 03)**: ①窗口过滤失活(in_window=全量观测)→5 红(直击 2: 截止日后观测翻转+截止日判定取错观测;下游 3: 黄金 CON 指纹钉住 evidence 首命中观测日期,11-01 窗前观测渗入即指纹漂移——黄金链即窗口语义敏感性锚);②终态不可重开失活(前置门短路)→1 红(专用拒收语义失位;schema 兜底 prior_status 词表仍 fail-closed,双层防御单层失活不至静默改写,如实登记);③S-3① 引擎核验门禁失活→1 红(not_triggered/sustaining/unverifiable/None 四值全放行即红)。三注入还原后 77 用例全绿,模块 sha256 注入前后等值(基线 fd927a94…b897fe)。

**本地 CI 镜像(证据包 04)**: 80 套件全 exit=0(offline-tests.yml 同口径 python3 逐套件,排除 test_glm_live)=基线 79 套件零回归+本包 1 新增;槽位记账: 基线 tracked test 文件=80 [实取·git ls-tree f0648841]=79 run+1 SKIP,本包后=81=80 run+1 SKIP(预期 CI 面,操作者 dispatch 后以 rounds/036 实跑为准)。

(§一-§六由报告笔回填。)
