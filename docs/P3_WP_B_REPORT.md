# IA-P3-WP-B REPORT — P3 收尾层第 2 实现包(新证据关联与持续跟踪聚合)

> 包: IA-P3-WP-B(P3 族第 2 实现包,#33/#34 挂靠;同族前件=WP-P3-A) · 执行Agent: Agent 3 · 分支: `dev/p3-impl-b`
> 基线: BASE-P3B=`b3628fdef81c81c7b46a698e89aca5b7a9925a30`(origin/main,开工 ls-remote 实取全值一致;=前件 WP-P3-A 终审尖端 202a09d2 合入 main 后基点,tree 与 202a09d2 逐字节等值[冻结章 §十一 BASE-P3B 实值依据,注入摘要,非工作树实读])
> 合同: IA-P3-WP-B-AC-v1.0(冻结,附录A 内嵌注入)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY/上游在场件行号一律为**本包基线工作树实读**行号(2026-11-07T17:25Z-实取,基线=BASE-P3B 工作树);提示词注入内容引用一律标注「注入摘要,非工作树实读」。
> 数值标注边界: 本文所有计数类/统计类数值逐个二选一标注 `[实取·来源: …]` 或 `[示意·非实取]`;日期/SHA/结构编号(WP-P3-B/#31-38/P3-G-03 等)/档键成分(ID 格式字符串,如 `LNK-20261108-001`)按合同边界出圈登记。

---

## §零 规格抄录与交付面登记(开工首步,AC-01;登记后即本合同白名单实体)

### §零.1 DESIGN §7 WP-P3-B 行四要素逐字抄录

实读 `docs/P3_DESIGN.md`(基线工作树在场,blob `5acc130a88d9635a1e82d7ad3beb4f1dbe008106`,§零.7 核验与 7f43724 侧等值),WP-P3-B 行位于 L176-L180,逐字抄录:

```text
L176: **WP-P3-B 新证据关联与持续跟踪聚合**(挂靠编号: **#33/#34**)
L177: - 目标: 落地 §4.1 分层关联(第一/二层零 GLM)+ §4.2 跟踪聚合视图。
L178: - 范围: 事件触发器(3 类事件 [实取·§4.1 枚举,2026-11-03])/匹配器(第一/二层)/关联档案(append-only)/未决触发器与到期裁决聚合视图;**不含第三层语义匹配**(PENDING 另拟)。
L179: - 依赖: WP-P3-A(索引与版本记录);层序前置(同上)。
L180: - 验收要点草案: ①关联不改状态断言(关联产物零状态写入)②触发事件消费门禁后事件流断言(原始数据轮询被拒)③匹配层参数(匹配阈值/规则表)**先登记后运行、禁回改**负向测试 ④关联建议引用带 snapshot_id+digest 断言 ⑤CI 零回归。
```

四要素齐备(目标 L177/范围 L178/依赖 L179/验收要点 L180 共 4 条),无缺失。核验:
- **B 行可区分性**: 与 A/C/D/E/F 行四要素逐项可区分(A=档案检索与结论版本管理 L170-174[同族前件行]/C=预测复盘与错误模式统计 L182-186/D=报告质量评价循环 L188-192/E=个人流程整合接口 L194-198/F=终验+总封版 L200-208;B 行题名「新证据关联与持续跟踪聚合」与挂靠 #33/#34、事件触发器/匹配器/关联档案/聚合视图四件范围要素均为他行所无)→ 合同附录A §零(iv)冲突处置首项不触发;
- **依赖列核验**: 「WP-P3-A(索引与版本记录)」=同族前件 R038+R067 整体 PASS 已合入 main(冻结章 §十一 生效前置达成登记,注入摘要,非工作树实读;本包基线 b3628fd tree 与终审尖端 202a09d2 等值=冻结章注记),其交付件在本基线工作树在场(`scripts/research_index.py`+`tests/test_p3_wp_a.py`+`docs/P3_WP_A_REPORT.md`+`docs/P3_WP_A_DELIVERY.md` [实取·本工作树 git ls-files 清点=4 件,与 WP-A REPORT §零.2 登记清单一致]);「层序前置(同上)」=§7 L168 层序排程依赖声明(冻结章 §十一 登记逐层核验 ✓,注入摘要,非工作树实读);依赖列与 BASE-P3B(`b3628fd…`)无矛盾、**不要求并入其他支**(本包无并入步,纯线性)✓;
- **范围列无真实 GLM 调用/网络出站/付费凭证要求**: 范围列 L178 明文「**不含第三层语义匹配**(PENDING 另拟)」+目标 L177「第一/二层零 GLM」;四件(事件触发器/匹配器第一二层/关联档案/聚合视图)均为确定性结构 → 无情形(d)停止条件。

### §零.2 交付文件清单(k=4 [实取·本节清点],登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据(推导逐条附) |
|---|---|---|
| 1 | `scripts/evidence_linkage.py` | DESIGN L178 范围列四件(事件触发器/匹配器[第一/二层]/关联档案[append-only]/未决触发器与到期裁决聚合视图)=**恰 1 个代码模块**: WP 题名「新证据关联与持续跟踪聚合」(L176)单一工作包,四件共享事件字典/锚点集/对象面与关联档案载体(§4.1 L101-110 触发-匹配-呈现三要素+L110 关联记录「append-only 入关联档案」同环;§4.2 L115 两聚合视图消费同一对象面与锚点集,同模块内聚)+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」;文件名=域词 evidence(新证据)+linkage(关联,DESIGN §4.1 题名「新证据↔旧观点自动关联」用词),避开既有 `research_index.py`(WP-A)/`research_archive.py`(B4)/`research_provenance.py`(R 系)/`allocation_engine.py`(ls scripts/ 实读 4 件在场合词面,命名不冲突 [实取·开工 ls 清点,grep -ci evidence/linkage=0]) |
| 2 | `tests/test_p3_wp_b.py` | DESIGN L180①②③④工件「断言/负向测试」+合同附录A §零(ii)「含代码则必含 tests/test_p3_wp_b.py」 |
| 3 | `docs/P3_WP_B_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P3_WP_B_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L180⑤「CI 零回归」证据落点=DELIVERY |

### §零.3 结构约束核验(2026-11-07T17:3xZ 实取)

- 与 `git ls-files` 零重合: 4 路径 `git ls-files scripts/evidence_linkage.py tests/test_p3_wp_b.py docs/P3_WP_B_REPORT.md docs/P3_WP_B_DELIVERY.md` 输出=0 行 [实取·开工 git ls-files]→ 纯新增 ✓;
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p3_wp_b.py)✓;
- 推导无越界: 范围列恰 1 个代码模块(§零.2 行 1 依据,同族前件 WP-A 单模块先例 P-A-01 同构)→ scripts/ 恰 1 文件;未引入 DESIGN 依据外文件 ✓。

### §零.4 DP 登记(开工首步登记定值;DESIGN 决策点登记表 L226-L241 实读,DP 共 10 个 [实取·表清点],行内所引节 §4.1 载 DP-4)

| DP | 分类(DESIGN 实读) | 本包登记 | 依据 |
|---|---|---|---|
| DP-4 关联匹配层次启用集 | **GLM 类·确认权留用户**(L233) | **确认面(第三层语义匹配/真实 GLM 调用)本包零实现零引用零触发**: B 行范围 L178 明文「**不含第三层语义匹配**(PENDING 另拟)」+目标 L177「第一/二层零 GLM」——本包按行内范围仅实现第一/二层(=DP-4 选项 (a)「仅第一/二层(零 GLM)」,该范围由 DESIGN 行文与冻结合同共同定死,非执行Agent自决);第三层启用面留用户确认+另拟 PENDING 包(L233「第三层启用须用户确认+另拟 PENDING 包」逐字),本包任何成员零真实调用/零网络/零凭证 | L233+L108+L177-178 |
| DP-1/DP-2/DP-3 | 登记型(L230-232) | **上游 WP-P3-A 已登记定值**(旁路索引文件/O-1~O-4 全 4 类/记录级粒度;本包只读复用其载体面,不重新登记不改写;WP-A REPORT §零.4 登记在案) | L230-232 |
| DP-5/DP-6/DP-7 | 登记型(L234-236) | **本包不触及**(WP-P3-C/D 面: 错误模式统计窗口/复盘分母/质量评价维度);零引用零改写 | L234-236 |
| DP-8/DP-9/DP-10 | 确认权留用户(L237-239) | **本包零触及**(提示词注入/个人流程接口/终验观察窗——均非 B 行范围所及,本包无费用/个人流程/LIVE 面) | L237-239 |
| **行内登记型参数(匹配阈值/规则表)** | 登记型(L180③ 明文「匹配层参数(匹配阈值/规则表)先登记后运行、禁回改」;§8.5「各包登记项」类) | **P-B-05/P-B-06/P-B-07/P-B-08 于 §零.5 登记定值**(第一层条件评估与建议动作映射/裁决事件匹配规则/第二层规则表+资产轴结构性缺席登记);登记定值即实现值,先登记后运行,运行后禁回改(负向测试面见 §二) | L180③+L220 |

DP 编号/数量/分类与 DESIGN 实读一致: 行内所引节 §4.1 载 DP-4(L108)恰 1 项,分类=确认权留用户(L233)——其确认面(第三层)未被自决实施(§零.1 核验: 范围列明文排除);登记型行内参数(匹配阈值/规则表)L180③ 明文 → §零.5 落定值;其余 DP 均非 B 行所引,零触及登记如上。

### §零.5 实现参数登记(P-B-01..P-B-16,先登记后实现,运行后禁回改)

| # | 参数 | 登记定值 | 依据 |
|---|---|---|---|
| P-B-01 | 模块载体 | `scripts/evidence_linkage.py` 恰 1 文件(事件触发器+匹配器第一/二层+关联档案 append-only+未决触发器与到期裁决聚合视图四组件同模块,§零.2 行 1) | DESIGN L178+§零.2 |
| P-B-02 | 事件类型词表 | `EVENT_KINDS=("snapshot","adjudication","formal_report")` 恰 3 类(§4.1 L103 枚举逐字: ①新快照经 Gate A 放行落档后②预测裁决落档[终态变更时]③新正式周报发布后) | §4.1 L103 |
| P-B-03 | 事件构造门禁(fail-closed) | ①`snapshot_event(snapshot)`: 注入 dict 门禁后事件流(**模块零轮询面**: 签名无 daily_dir/无任何 data/daily 路径引用,事件驱动=注入,L103「触发器消费门禁后事件流,不轮询原始数据」);snapshot_id 规范经 `drr.ra.parse_snapshot_id` 复用;gate_a.status 经 `rp.gate_allows_formal_research`(L1210-1213 实读)放行(PASS/DEGRADED 过,FAIL/None/未知→ValueError 零构造)②`adjudication_event(prediction, snapshot)`: prediction.status∈终态词表 `TERMINAL_PRED_STATUSES=("hit","miss","inconclusive")`(L534 裁决 4 值 hit/miss/inconclusive/not_yet_triggered 中 not_yet_triggered=前提未生效非终态;open/observing=未决态 [实取·allocation_engine due_predictions L187-192 未决词面]——均→ValueError);pred_id 非空必填;接地快照同①gate 核验+digest 重算③`formal_report_event(report_view, snapshot_dir)`: `rp.formal_report_view` 在场复用(L1456-1517 八条校验链: 规范文件名/发布状态 published=True/final_quality∈(PASS,DEGRADED)/身份三字段/内容摘要重算一致;候选/未发布/被替换产物一律拒);绑定快照=状态记录 `snapshot_id`(report_generator `_status_body` L791-795 实读携带)经 `drr._load_snapshot_for_verify`(L778-801)规范加载+同①gate 核验+`rp.digest_snapshot`(L1324-1328)重算,**与状态记录 snapshot_digest 声明值一致核验,失配→ValueError(证据链漂移 fail-loud,禁采声明值)** | §4.1 L103+§3.1 L71+要点② |
| P-B-04 | 事件锚点集 | 事件证据词汇表=锚点键族(quant_triggers.metric 同族): 默认经 `sb.build_anchors(snapshot, ymd)` 在场复用(L121-231,快照单一来源派生的兼容桥,P-A-06 同源锚键词面);`anchors=` 显式注入面(**依赖注入**: 测试以合成锚点集注入;门禁/digest 恒取 snapshot 本体重算,注入不影响门禁核验路径);注入条目形如 `{value, metric_id, obs_date}`(实档形态子集,匹配面仅消费 value[数值评估]与 metric_id[登记维度]) | §4.1 L106「复用既有结构」+桩纪律注入面先例 |
| P-B-05 | 第一层精确匹配规则(匹配阈值) | 对象 `quant_triggers[].metric`(锚键)∈事件锚点键集→命中;命中后条件评估=`ae._eval_condition_set(trigger, anchors)` 在场复用(L213 起,单指标/all/any 复合+COMPARATORS 词表 `{">=","<=","<",">"}` L95-101)→fired;**条件态词表=引擎核验词面逐字沿用**(L1052-1053 实读): fired=triggered 且 sustain_weeks>0→`"sustaining"`(一次性评估口径: 关联面无 persist 连续周数载体,按⏳持续确认中呈现,不冒充已触发;L316-317 引擎语义承接);否则=fired 词面(`"triggered"`/`"not_triggered"`/`"unverifiable"`);触发器 metric 缺席锚点集→**零条目**(该触发器无新证据,不造 unverifiable 条目,如实缺席) | §4.1 L106+L105-107 |
| P-B-06 | 第一层建议动作映射(登记定值) | `LAYER1_ACTION_MAP={"triggered":"提案","sustaining":"复核","not_triggered":"复核","unverifiable":"复核"}`(词面=DESIGN L110「建议动作(复核\|提案\|忽略)」全集之子集;**提案=仅生成关联建议条目**,实际状态变更走既有门禁[report_generator L503-505/L521-523 门禁族],关联面零状态写入——要点①) | §4.1 L110+要点① |
| P-B-07 | 裁决事件匹配规则 | 第一层=prediction 规格 `metric`(锚键词面,predictions 18 字段之 metric [实取·config/allocation_views.json predictions[0] 键清点=18])与对象触发器 metric **等值**→命中;condition_status=null(裁决=结果型证据,门槛跨越评估面如实缺席);建议动作=恒 `"复核"`(裁决结果建议复核关联对象,不生成提案——提案须门禁依据,裁决非门禁依据);第二层=机制类别交叉同 P-B-08(证据维度=spec.metric 单键);spec 缺 metric(定性预测)→零匹配条目(如实) | §4.1 L103②+L106-107 |
| P-B-08 | 第二层规则匹配规则表(机制类别单轴+资产轴结构性缺席登记) | 对象侧机制画像={`ae.mechanism_of(锚键)` for 对象 quant_triggers[].metric 非空}(`ae.METRIC_MECHANISM` 规则表 L106-114+`ae.mechanism_of` L117-124 在场复用,7 类词表=`ae.MECHANISM_CATEGORIES` L104=report_generator L518 同源 [实取·两处词面逐一相等比对]);证据侧=事件锚点各键同法;**第二层命中=证据锚键∉该对象触发器键集(第一层优先去重)且 mechanism_of(证据键)∈对象机制画像**;建议动作=`"忽略"`(规则匹配=弱信号,登记供人工筛选,词面=L110 全集第三值);condition_status=null;**资产标签轴结构性缺席登记(登记发现,非缺陷)**: views[].asset=中文资产标签(美股/贵金属(黄金)等 9 值 [实取·config/allocation_views.json views[].asset 清点])与证据侧 registry asset_class(英文技术类 [实取·config/metric_registry.json asset_class 值域清点=29 值])之间**无在场词表桥接**(scripts/ 实读 grep 资产标签映射表零命中;thesis 对象无 asset 字段 [实读·config/thesis.json theses[0] 键清点])——DESIGN L107「机制类别+资产标签交叉」之资产轴在 DEV 在场载体面**如实缺席**,单轴(机制类别)落地;载体演进(结构化资产标签桥)后按新登记扩展,不越界实施(AC-07.7) | §4.1 L107+AC-07.2/7.7 |
| P-B-09 | 关联档案载体 | 集合 `evidence_linkages` 挂共享档案族根(`drr._collection_dir` L118 复用;**不占上游已占 13 集合名** [实取·清单: queries/deep_research_tasks/hypotheses/conditions/events/deep_research_evidence/rounds/deep_research_triggers/conclusions/disposals/calendar_events(P2 族 drr/各件)+conclusion_versions(WP-P3-A)+ra 侧族载体]);ID=`LNK-{YYYYMMDD}-{NNN}` 同日单调配号(扫集合目录当日最大序号+1,ra.allocate_query_id/VER- 同款纪律;ymd 取 created_at 日期段;**LNK- 前缀避开已占 13 前缀** [实取·清单: QB-/RT-DR-/HP-/FC-/EV-/EVI-/RD-/TRG-/CON-/DSP-/CAL-/VER-/PRED-(WP-A)]);append-only 经 `drr._write_records`(L513-524 预检存在→STATUS_REJECTED_DUPLICATE 零写入);读档逐条重校验 fail-loud(篡改→ValueError) | §4.1 L110「关联记录本身 append-only 入关联档案(旁路件,可重建)」 |
| P-B-10 | 关联记录 schema | §4.1 L110 呈现字段 4 项全落+载体字段: `{record_type:"evidence_linkage", linkage_id, event_kind, evidence_key, object_type, object_id, match_layer, anchor_key, metric_id, trigger_id, condition_status, suggested_action, snapshot_id, digest_snapshot, created_at, history:[{ts,note}]}`——关联对=evidence_key↔object_id;匹配层=match_layer(1\|2);证据引用=snapshot_id+digest_snapshot(**`rp.digest_snapshot` 重算,API 无 digest 入参,禁采声明值——要点④**)+anchor_key/metric_id/trigger_id;建议动作=suggested_action(复核\|提案\|忽略);**零原始数值字段**(证据引用落档键+指纹,不复制数值语义为第二事实源,§3.1 L73 纪律延伸);evidence_key 词表: snapshot 事件=snapshot_id/周报事件=`weekly_report_{ymd}`/裁决事件=`PRED-{pred_id}`(rri.PREDICTION_KEY_PREFIX 复用);object_id=THESIS-/VIEW- 键(rri.THESIS_KEY_PREFIX/VIEW_KEY_PREFIX 复用,WP-A P-A-05 词表对齐);第二层条目 trigger_id/condition_status=null(如实);裁决事件条目 metric_id/condition_status=null(如实) | §4.1 L110+要点④ |
| P-B-11 | 匹配确定性 | 对象迭代序=theses(文件序)→views(文件序);第一层按对象触发器列表序,第二层按锚键字典序;条目输出按 (object_type,object_id,anchor_key,match_layer) 字典序;同输入同输出(匹配=纯函数);配号面独立于匹配面(配号按写入序,created_at 显式注入定值) | AC-03 确定性纪律 |
| P-B-12 | 聚合视图①未决触发器跨期清单 | `pending_triggers_overview(thesis_path, views_path, anchors, as_of)`: 只读零写入;views 侧=`ae.evaluate_quant_triggers(views_data, anchors, today_str=as_of, persist=False)` 在场复用(L265-328,persist=False 完全无副作用=渲染路径,L275 docstring 明文);theses 侧=只读适配壳 `{'views':[{id:THESIS-{id}, quant_triggers}]}` 过同一评估器(状态文件无 thesis trigger_state 载体 [实读·config/thesis.json 顶层与 theses[0] 键清点零 trigger_state]→连续周数按评估面如实起算,登记发现);输出行=仅 status∈{unverifiable,sustaining} 的触发器(❓待验证/⏳持续确认中 词面,L1052-1053),含 {object_type,object_id,asset(views),trig_id,direction,status,status_display,detail,consec,sustain},按 (object_type,object_id,trig_id) 排序;数据面=状态文件(对象集,§4.2 L115「数据源为状态文件」)+注入锚点集(评估面);as_of 显式注入 | §4.2 L115 |
| P-B-13 | 聚合视图②到期预测裁决待办 | `due_adjudications_overview(views_path, as_of)`: `ae.due_predictions(views_data, today_str=as_of)` 在场复用(L187-192 ⏰已到期口径: status∈{open,observing,not_yet_triggered} 且 deadline≤as_of;L1070 词面「⏰已到期,本周必须裁决」);输出行={pred_id,asset,status,deadline,metric,direction},按 pred_id 排序;as_of 显式注入(测试恒显式;交互面缺省=墙钟,与 ae 同语义);只读零写入 | §4.2 L115 |
| P-B-14 | 旁路简报渲染 | `render_tracking_briefing(thesis_path, views_path, anchors=None, as_of=None)`: 纯文本两清单渲染+免责尾行「持续跟踪聚合面输出,不构成投资建议(禁交易/禁仓位/禁收益承诺)」(§8.3 红线承接);**零写入零回写路径**(呈现载体=旁路简报,§4.2 L115「周报既有槽位或旁路简报」之旁路简报分支——本包取旁路简报面,不改周报系统) | §4.2 L115+§8.3 |
| P-B-15 | 纯度与上游对齐 | import 面白名单={json,os,re,sys,datetime+项目既有 allocation_engine/deep_research_registrar/research_provenance/snapshot_builder/research_index};AST 零网络 import(urllib/requests/http/socket/httpx 禁);零凭证/密钥/token;模块 docstring+简报尾行免责;**对齐上游=复用调用禁复制分叉**: ae._eval_condition_set/ae.evaluate_quant_triggers/ae.due_predictions/ae.mechanism_of/ae.COMPARATORS/ae.MECHANISM_CATEGORIES、drr._write_records/drr._record_path/drr._load_snapshot_for_verify/drr._collection_dir、rp.gate_allows_formal_research/rp.digest_snapshot/rp.formal_report_view、sb.build_anchors、rri.THESIS_/VIEW_/PREDICTION_KEY_PREFIX(依赖列「WP-P3-A[索引与版本记录]」复用面=状态记录键前缀词表+关联对象类型子集;关联匹配需 op/target 规格详情,索引条目仅档键引用[P-A-04],故对象面直读门禁后状态文件[§3.1 L71 认可输入],WP-A index_state_files 同源面);WP-P3-A 版本记录面=关联建议「提案」动作语义指向既有门禁修正机制(rri.revise_conclusion 在场面),本模块不自动调用(零状态写入) | AC-05.4+AC-07+§8 |
| P-B-16 | 他包范围排除 | 第三层语义匹配零实现零引用(DP-4 确认面,L108/L233);WP-P3-A/C/D/E/F 任何范围零带入(§7 行界);W4/W5 侧边验收工具零接入(AC-07.6);自然语言查询零涉及(§3.2(b) 停泊面) | AC-08.1+§7 |

### §零.6 前置实读登记(file:line;基线工作树 2026-11-07T17:25-18:0xZ 实取)

- DESIGN 相关节(工作树在场件,=7f43724 侧 blob 等值,§零.7): §2.1 积累对象 L47-53(O-1~O-5)/§3.1 快照纪律 L69-73/§3.2 查询形态 L75-86((c) 关联扫描 L84)/§4.1 新证据↔旧观点自动关联 L101-110(触发 L103/匹配 L105-108/呈现 L110)/§4.2 持续跟踪 L112-116(状态保护 L114/聚合面 L115)/§7 层序声明+WP-P3-B 行 L166-210/§8 红线 L214-222/决策点登记表 L226-241(DP-4 L233);
- 上游在场件(只读禁改,对齐=复用调用):
  - `scripts/research_index.py`(WP-P3-A): COLLECTION_VERSIONS L75/OBJECT_TYPES L86/状态记录键前缀 L94-96/_mk_entry L166/query_index L656;
  - `scripts/allocation_engine.py`: COMPARATORS L95-101/MECHANISM_CATEGORIES L104/METRIC_MECHANISM L106-114/mechanism_of L117-124/due_predictions L187-192/_eval_condition L198-210/_eval_condition_set L213-228/evaluate_quant_triggers L265-328(词面 L1052-1053/⏰口径 L1070);
  - `scripts/research_provenance.py`: gate_allows_formal_research L1210-1213/select_snapshot L1270-1321/digest_snapshot L1324-1328/formal_report_view L1456-1517(八条校验链)/scan_formal_weekly_reports L1520-1529;
  - `scripts/snapshot_builder.py`: _GLOBAL_OLD_ID L106-107/build_anchors L121-231(快照→锚点兼容桥,单一来源=快照);
  - `scripts/deep_research_registrar.py`: ARCHIVE_FAMILY L45/COLLECTIONS L50-52/DEFAULT_ARCHIVE_DIR L53/_collection_dir L118/_write_records L513-524(append-only 落档)/_record_path L527-528/_load_snapshot_for_verify L778-801;
  - `scripts/report_generator.py`: 论点状态词表 L501/门禁语义 L503-505/机制 7 类 L518/评级门禁 L521-523/预测裁决词表 L534/发布事务 save_candidate_report L909-924/_status_body L777-800(snapshot_id/snapshot_file/snapshot_digest 绑定 L791-795);
  - `config/thesis.json`(门禁后状态文件): theses[].{id,name,status,confidence,quant_triggers[].{trig_id,direction,metric,op,target,sustain_weeks,note}} 顶层 last_updated L3;quant_triggers 块 L34-60;**实读无 asset/trigger_state 字段**(P-B-08/P-B-12 登记发现);
  - `config/allocation_views.json`(门禁后状态文件): views[].{id,asset,rating,confidence,quant_triggers[]} L17-60(quant_triggers L38-49)/predictions[] 18 字段(pred_id,date_made,asset,direction,horizon_weeks,deadline,trigger,status,metric,comparator,target,evidence_ref,premise_text,verify_mode,observations,data_source,note,resolved_note [实取·predictions[0] 键清点=18])/ratings_scale L5-10;**实读无结构化机制标签与资产标签桥**(P-A-08 同源+P-B-08 资产轴登记发现);
  - 同族前件 REPORT: `docs/P3_WP_A_REPORT.md` §零.2 登记清单(k=4)/§零.5 参数面/§零.10 实现期登记(fixture 形态与本地 CI 镜像方法学先例);
  - `data/research/` 实况(只读勘察,非测试数据源): research_snapshot_20261104.json 在场(gate_a=DEGRADED,facts 77 条 [实取·实读清点])/anchors_20261104.json(181 键 [实取],锚键→metric_id 映射载体,如 global_market.data.GOLD.close→GOLD_F 别名实态)——仅接口勘察,不入测试 fixture(AC-03.3 合成 fixture 唯一数据源纪律)。

### §零.7 开工核验(2026-11-07T17:25-17:3xZ 实取)

- 步骤0: `git status` clean(开工时在 dev/p3-impl-a@202a09d2,工作树干净,非本包所致脏=无);UTC 开工时刻 2026-11-07T17:25:46Z;
- 步骤1: 合同三占位符均实值化(BASE-P3B=b3628fd… 全值/BASE-P3B-CI-SUITES=83/BRANCH-SET=56 支全表 §十一.1 内嵌),无未解析标记 ✓;
- 步骤2: `git ls-remote origin main dev/p3-design-fix1 dev/p3-impl-a` 实取: main=`b3628fdef81c81c7b46a698e89aca5b7a9925a30`(=BASE-P3B 全值一致 ✓)/dev/p3-design-fix1=`7f43724661b50e011394e643cdd8c223c0b27a90`(全值一致 ✓,未锚 f93adb5)/dev/p3-impl-a=`202a09d2570f2894acff05fb8fe1a4dbe7c26a79`(=冻结章终审登记尖端一致 ✓);
- 步骤3: 本地对象库缺 b3628fd(远端 merge 提交)→`git fetch origin main` 只读取回(8cebe74..b3628fd)→`git checkout -b dev/p3-impl-b b3628fd…` 自基线全值切出 ✓(rev-parse HEAD=b3628fd…);
- 步骤4(设计在场核验,本包无并入步): ①`git merge-base --is-ancestor 7f43724… HEAD`→exit 0 可达(经祖先在场,冻结章 §十一.3 路径甲注记一致)✓;②设计三件 `git ls-tree` 双侧(HEAD vs 7f43724)blob 逐一相同: P3_INVENTORY=9f366da5a9e327e524ae1a17eec229722cd85d5f/P3_DESIGN=5acc130a88d9635a1e82d7ad3beb4f1dbe008106/P3_DELIVERY=ac8965ce0e09a964f5b493ebe1ef7dcacfca9b2d ✓;
- CI 基线: `ls tests/test_*.py` 计数=83 [实取·开工清点]=BASE-P3B-CI-SUITES 83 槽口径一致(82 exit0+1 SKIP,冻结章 §十一 CI 基线实值依据;分支 run 预期=83+本包新增 tests 文件数 1=84);本地 Python 3.9.6(CI=3.11),实现保持 3.9 兼容语法(WP-A 同款约束)。

### §零.8 零运行产物判定(要点对照)

DESIGN L180 验收要点 5 条: ①关联不改状态断言=测试面 ②门禁后事件流断言=测试面 ③匹配层参数登记负向=测试面 ④snapshot_id+digest 断言=测试面 ⑤CI 零回归=CI 面(工件=测试文件+run ID,run ID 由操作者 CHECKPOINT dispatch 登记 `rounds/039/P3-WP-B-CI-dispatch-evidence.md`)。五条均无真实运行/编排入口要求(范围列 L178 零「真实运行/端到端/数据档引用」措辞;对照 WP-A 行 L174 同构判定先例 §零.8)→ **本包登记「零运行产物」**,`data/research/` 零写入(关联档案/聚合简报全落测试临时沙箱,不落默认路径);`.gitignore` 不改。

### §零.9 AC-03.7(GLM 桩边界)适用判定

登记清单(§零.2)无 GLM/LLM 能力级调用面实现文件(范围列 L178 明文「不含第三层语义匹配(PENDING 另拟)」+目标 L177「第一/二层零 GLM」;模块=事件触发器+匹配器+关联档案+聚合视图确定性结构)→ **AC-03.7 不适用**,判定依据=清单无调用面类文件(§零.2 表 1-4 无客户端封装/调用编排/适配器类)。

### §零.10 实现期登记(实现笔回填)

**交付物实取(行数/sha256 双源=shasum -a 256 与装配器 hashlib 复算一致)**:
- `scripts/evidence_linkage.py`: 748 行,sha256=`e639c42358017c92a59138c2c75530fb265a54033809bf48f8e43aa4c4d8f9ba`;
- `tests/test_p3_wp_b.py`: 1225 行,sha256=`dade7023c3480883b5e048ec099a5d326eaf86415aae6093854a9321df587de1`(基线 748+1225=1973 与本登记一致;`py_compile` 双件通过)。

**用例分类实取**: 117 用例/17 类 [实取·`Ran 117 tests`+`grep -c ^class Test`=17]——TestGoldenFirstPrinciples(4)/TestParamRegistration(8)/TestEventGateNegative(17)/TestEventGolden(8)/TestLoadLinkObjects(5)/TestLayer1Evaluation(6)/TestMatchGolden(7)/TestLayer2MechanismCross(5)/TestRecordLinkagesGolden(5)/TestBuildLinkageRecordsPure(4)/TestArchiveAppendOnly(6)/TestValidateTamperVariants(20)/TestRebuildDeterminism(1)/TestZeroStateWrite(5)/TestAggregations(9)/TestStaticPurity(5)/TestEndToEnd(2)。

**黄金值登记(独立首原理预计算 `/tmp/p3wpb/golden_precompute.py`,零被测模块 import;fixture 一致性 `/tmp/p3wpb/fixture_consistency.py` 三方裁定 0 失配)**: 快照 digest(PASS)=`3e5dd3494769532d`/(DEGRADED)=`0efa106fbb80f4b7`;周报 md digest=`8f1dcc804923a009`;关联档文件字节 sha256: LNK-20260105-001=`48d7311c…c9e73ac`/002=`7122a72e…0a4397`/003=`66c420a4…7f2d164`/004=`3038fc7e…c3f56f3`(全值见测试文件 GOLD_RECORD_SHA;测试内 hashlib 首原理复算逐值相等,双源一致)。

**实现期缺陷修复登记(2 处,当轮暴露当轮修复)**: ①`build_linkage_records` 占位配号缺 `:03d` 零填充(首轮红 `LNK-20260105-1`≠`LNK-20260105-001` 暴露,补格式化复绿);②`record_linkages` 拒绝路径返回值失真(count/linkage_ids 按计划面而非实写面报数——诚实性缺陷,改为拒绝时如实归零 0/[]);另 1 处**设计口径修正**(非缺陷): `_layer1_condition_status` sustain 分支首轮写作「sustain>0 一律 sustaining」,与引擎空状态一次性口径(sustain=1 首跨即满=triggered)不一致→按 `ae.evaluate_quant_triggers` consec=1 口径逐字对齐(sustain≤1→triggered;sustain>1→sustaining),对齐依据=复用禁分叉纪律(§零.5 P-B-05 登记值同步此口径)。

**负向敏感性三注入 [实取·注入→红→还原→复绿,sha256 前后等值零残留]**: ①第一层锚点在场守卫删除→红(failures=11,errors=1)→还原复绿;②Gate A fail-closed 条件替换为永假→红(failures=4)→还原复绿;③sustaining 分支删除→红(failures=5)→还原复绿;三循环前后模块 sha256 均等值 `e639c423…f9ba`(基线=终态)。

**本地 CI 镜像重演(CI 同款方法学: 逐文件直接执行,串行零并发——WP-A 教训在册)**: 84 文件=83 exit0+1 SKIP(test_glm_live 身份锚,RUN_GLM_LIVE 未设)+0 非零 [实取·`/tmp/p3wpb/ci_mirror_results.txt`];基线 83 槽零回归,本包恰 +1(tests/test_p3_wp_b.py exit0)。

**零运行产物锚定 [实取]**: `find data/research -newer scripts/evidence_linkage.py`→零输出;`git status --porcelain` 仅白名单 2 代码件未跟踪(登记笔后状态),data/ 零改动。

## §一 实现摘要

`scripts/evidence_linkage.py`(748 行)四组件确定性落地:

1. **事件触发器(3 类,P-B-02/P-B-03)**——触发器消费门禁后事件流(事件=注入,模块无 daily_dir 参数/零 data/daily 路径引用,结构性不可达采集件): ①快照事件 `snapshot_event(snapshot, anchors=None)`: gate_a.status 经 `rp.gate_allows_formal_research`(L1210-1213)放行,FAIL/None/未知→ValueError 零构造;digest=`rp.digest_snapshot`(L1324-1328)内容重算禁采声明值;②裁决事件 `adjudication_event(prediction, snapshot, …)`: 限终态词表 {hit,miss,inconclusive}(open/observing/not_yet_triggered 未决态如实拒),evidence_key=`PRED-{pred_id}`(rri 前缀词表),evidence_keys=规格 metric 单键;③周报事件 `formal_report_event(report_view, snapshot_dir, …)`: `rp.formal_report_view`(L1456-1517)八条校验链**复验**+绑定快照三重纪律(`drr._load_snapshot_for_verify` L778-801 规范加载+gate 放行+digest 重算),重算 digest 与发布状态 snapshot_digest 声明值失配→ValueError 证据链漂移 fail-loud。
2. **匹配器(第一/二层零 GLM,P-B-05..P-B-08)**——`match_event(event, objects)` 纯函数,输出按 (object_type, object_id, anchor_key, match_layer) 字典序: 第一层=对象 quant_triggers[].metric(锚键)∈事件锚点键集,条件评估经 `ae._eval_condition_set`(L213-233)在场复用,条件态沿用引擎核验词面(triggered/not_triggered/sustaining/unverifiable; sustain 一次性口径=引擎空状态 consec=1 首跨对齐),建议动作映射 triggered→提案/余三态→复核(提案=仅生成建议条目);第二层=`ae.mechanism_of`(L117-124)+`ae.MECHANISM_CATEGORIES`(L104)机制类别单轴交叉,建议动作=忽略;资产标签轴结构性缺席(P-B-08 登记发现,不造值)。
3. **关联档案(append-only 旁路件,P-B-09/P-B-10)**——LNK-{YYYYMMDD}-{NNN} 同日单调配号(扫集合目录当日最大序号+1),集合 `evidence_linkages` 避开上游 12 集合名/15 前缀,经 `drr._write_records`(L513-524)原子落档(预检存在→rejected-duplicate 零写入,包装层拒绝时 count/ids 如实归零);记录 16 键零原始数值(证据引用落 snapshot_id+digest_snapshot 重算值+档键);`validate_linkage_record` 全量校验+`list_linkages` 读档逐条重校验篡改 fail-loud;`build_linkage_records` 纯函数(占位配号)与 `record_linkages` 权威续配两口径显式分立;同事件×同对象×同 created_at 双档案重放逐字节一致(可重建)。
4. **聚合视图(只读零写入,P-B-12/P-B-13/P-B-14)**——①`pending_triggers_overview`: ❓待验证/⏳持续确认中两态跨期清单,views 直经 `ae.evaluate_quant_triggers`(L265-328,persist=False 零副作用渲染路径),theses 经只读适配壳同评估器;②`due_adjudications_overview`: `ae.due_predictions`(L187-192)在场复用(⏰已到期口径);③`render_tracking_briefing` 旁路简报渲染(两清单纯文本表+免责尾行,零回写路径);锚点集未注入时未决清单如实缺席渲染不冒充。

测试 `tests/test_p3_wp_b.py`(1225 行/117 用例/17 类): 全合成 fixture 唯一数据源,预期值字面量硬编码不从被测模块派生,黄金值(快照 digest×2/周报 md digest/关联档文件字节 sha256×4)独立首原理预计算固化+测试内 hashlib 复算双源一致+fixture 一致性三方裁定 0 失配。

## §二 AC-02 五要点逐条映射表

| 要点 | 实现面 | 测试面锚 |
|---|---|---|
| ① 关联不改状态(零状态写入) | `record_linkages` 唯一写路径=drr._write_records 落 evidence_linkages 集合;thesis/views/索引/任何权威档零触碰;聚合全 persist=False/只读 | TestZeroStateWrite 5 用例: 状态文件字节前后不变(关联+聚合+简报三面)/views 零 trigger_state 注入/archive 子树独占/record_linkages 无 archive_dir→TypeError(必填 kw,无默认路径常量结构性禁达 LIVE) |
| ② 触发事件消费门禁后事件流(原始数据轮询被拒) | 事件=注入面(snapshot/prediction/report_view dict);模块无 daily_dir/枚举/扫描原始数据参数;门禁核验构造器内置(快照 gate/裁决终态/周报八链)三态 fail-closed | TestEventGateNegative 17 用例: FAIL/缺 gate/未知态/非 dict/坏 snapshot_id/anchors 非 dict/非终态×3/坏 pred_id×2/裁决 gate FAIL/候选名/未发布/digest 漂移/绑定快照缺失/绑定 FAIL/坏质量/无 path;TestStaticPurity: 禁网令牌+data/daily 剥 docstring 代码面零在场 |
| ③ 匹配层参数先登记后运行禁回改 | P-B-01..P-B-16 登记笔(869770a)先于实现笔(479ec7d)(git 时序);活性常量+模块内登记镜像+测试字面量三方一致;运行期 `param_selfcheck` 哨兵 | TestParamRegistration 8 用例: registered_param_values 字面量全等/param_selfcheck=True/monkeypatch 回改 action_map·collection·prefix 三面→AssertionError 检出/集合名与前缀避上游/机制词表镜像引擎;__main__ 自检入口 exit0 |
| ④ 关联建议引用带 snapshot_id+digest 断言 | 记录 16 键含 snapshot_id+digest_snapshot(构造器重算值,禁采声明值);零原始数值字段 | TestRecordLinkagesGolden: 档文件字节 sha256 黄金×4+独立字面量 canonical 逐字节相等+记录 JSON 零原始数值串(1.85/2650/5900/4.9/\"value\" 全不在档);TestEventGolden: 三类事件 digest=重算黄金(周报事件声明值失配→ValueError) |
| ⑤ CI 零回归 | 本地镜像=CI 同款逐文件直接执行串行: 84 文件=83 exit0+1 SKIP(test_glm_live)+0 非零,基线 83 槽零回归本包恰 +1 [实取·/tmp/p3wpb/ci_mirror_results.txt] | CI 面 **NOT VERIFIED@执行席**: run ID 执行席不可见,操作者 CHECKPOINT 通道 `rounds/039/P3-WP-B-CI-dispatch-evidence.md`(冻结章登记),非自决 PASS |

## §三 如实偏差与登记承接

1. **实现期缺陷 2 处**(占位配号缺 :03d 零填充/拒绝路径返回值按计划面报数→如实归零)——当轮暴露当轮修复,登记 §零.10;
2. **设计口径修正 1 处**(sustain 分支首轮「sustain>0 一律 sustaining」与引擎空状态口径不一致→按 consec=1 首跨逐字对齐,复用禁分叉纪律)——登记 §零.10;
3. **CI 镜像 SKIP 分类首轮误标 6 槽**(字符串匹配把 5 个含「SKIP」字样的通过套件误计 SKIP 槽)→当场勘误为身份锚口径(唯一 SKIP 槽=test_glm_live,输出含 RUN_GLM_LIVE)→终局 83+1+0;
4. **CI run ID 执行席不可见**→⑤ CI 面分列 NOT VERIFIED@执行席,操作者 rounds/039 dispatch 通道(非偏差,如实分列);
5. **资产标签轴结构性缺席**(P-B-08 登记发现): 中文资产标签(美股等)与 registry asset_class(英文)无在场词表桥接,如实缺席不造值,记录 schema 无 asset 字段(TestLayer2MechanismCross 断言);
6. **默认锚点面注记**: 合成 fixture metric 不在真实 registry,`sb.build_anchors` 默认派生产出空集→测试以 P-B-04 注入面为主,默认面仅类型冒烟(TestEventGolden.test_snapshot_event_default_anchors_face);
7. **重放语义注记**(登记语义澄清非偏差): 同事件同日重放=同日单调追加新批(005-008),rejected-duplicate=drr 并发守卫面(测试以陈旧配号扫描模拟竞态窗口,真守卫拒绝零写入零部分落档);
8. **测试文件 1 处 subprocess 受控用途**: test_selfcheck_main_entry 仅以子进程运行被测模块 `__main__` 自检(本地零网络零凭证);被测模块 AST 纯度零 subprocess(TestStaticPurity 白名单外 import=∅)。

## §四 DP 零回改自检表

| DP | 处置 | 本包核验 |
|---|---|---|
| DP-1/2/3 | 上游 WP-A 已登记(报告笔 febba90 §四),本包只读复用 | rri.THESIS-/VIEW-/PRED-KEY_PREFIX 三常量只读引用,零回改 ✓(§零.4 登记) |
| DP-4 | 确认面(第三层语义匹配)PENDING 另拟,确认权留用户 | 本包零实现零引用: MATCH_LAYERS=(1,2),范围列 L178 明文排除,AC-03.7 不适用(§零.9) ✓ |
| DP-5/6/7/8/9/10 | 他包面 | 零触及 ✓(§零.4 登记) |
| 行内登记型参数 P-B-01..P-B-16 | 先登记后运行禁回改 | 登记笔 869770a(§零.5 全表)→实现笔 479ec7d,git 时序在册;三方一致(活性常量/镜像/测试字面量)+param_selfcheck 运行期哨兵+monkeypatch 回改检出 3 面 ✓ |

## §五 git 纪律自检(七项)

1. 基线切出: `git checkout -b dev/p3-impl-b b3628fd…` 自 BASE-P3B 全值切出(§零.7 步骤3,fetch 只读补对象库) ✓;
2. 纯线性: 登记笔 869770a→实现笔 479ec7d→报告笔→终笔,零 merge 零 amend 零 force ✓;
3. main 未触碰: 全程零 main 写操作(读/fetch/ls-remote 除外) ✓;
4. LIVE 零写入: data/ 零改动(find -newer 零输出+git status 零 data/ 条目),关联档案/简报全落测试沙箱 ✓;
5. launchd 零改动: 全程零 LaunchAgents 操作 ✓;
6. 零 tag: `git tag` 3 枚均为他流先存(p03-final-20261105/p1-final-20261107/w5-final-20261104,早于本包开工),本包零新增 ✓;
7. 网络: 仅取证类(ls-remote/fetch 只读;终局单支推送 dev/p3-impl-b,no-force),测试全离线 ✓。

## §六 数值标注自检(全实取)

| # | 数值 | 实取依据 |
|---|---|---|
| 1 | 模块 748 行 | `wc -l` 实取(§零.10) |
| 2 | 测试 1225 行 | `wc -l` 实取(§零.10) |
| 3 | 117 用例/17 类 | `Ran 117 tests`+`grep -c ^class Test`=17+AST 逐类计数(§零.10) |
| 4 | 黄金 digest×3+档 sha×4 | 独立预计算+测试内复算双源一致(§零.10) |
| 5 | 门禁负向 17 面/篡改变体 20 面 | AST 用例计数(§一/§零.10) |
| 6 | 注入红 11+1/4/5 | 三注入循环实取(§零.10) |
| 7 | CI 镜像 84=83 exit0+1 SKIP+0 非零 | /tmp/p3wpb/ci_mirror_results.txt(§零.10) |
| 8 | 基线 83 槽→分支 84 | §零.7 开工清点+镜像重演 |
| 9 | 集合名避 12/前缀避 15 | 上游实取清单(§零.5 P-B-09;测试 UPSTREAM_* 元组计数) |
| 10 | k=4 白名单恰 4 文件 | §零.2 登记+git 终局 name-status |
| 11 | 缺陷修复 2+口径修正 1+方法学勘误 1 | §三/§零.10 |
| 12 | 双代码件 sha256 全值 | shasum -a 256+装配器 hashlib 双源(§零.10) |
