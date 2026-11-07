# IA-P3-WP-C REPORT — P3 收尾层第 3 实现包(预测复盘与错误模式统计)

> 包: IA-P3-WP-C(P3 族第 3 实现包,#35 挂靠;依赖列前件=WP-P3-A) · 执行Agent: Agent 3 · 分支: `dev/p3-impl-c`
> 基线: BASE-P3C=`c14931c34f23dacc3439cc2609cf51a89d7ea60f`(origin/main,开工 ls-remote 实取全值一致)
> 合同: IA-P3-WP-C-AC-v1.0(冻结,附录A 内嵌注入)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY/上游在场件行号一律为**本包基线工作树实读**行号(2026-11-07T19:2x-19:3xZ 实取,基线=BASE-P3C 工作树);提示词注入内容引用一律标注「注入摘要,非工作树实读」。
> 数值标注边界: 本文所有计数类/统计类数值逐个二选一标注 `[实取·来源: …]` 或 `[示意·非实取]`;日期/SHA/结构编号(WP-P3-C/#31-38/P3-G-04 等)/档键成分(ID 格式字符串,如 `PRED-1`)按合同边界出圈登记。

---

## §零 规格抄录与交付面登记(开工首步,AC-01;登记后即本合同白名单实体)

### §零.1 DESIGN §7 WP-P3-C 行四要素逐字抄录

实读 `docs/P3_DESIGN.md`(基线工作树在场,blob `5acc130a88d9635a1e82d7ad3beb4f1dbe008106`,§零.7 核验与 7f43724 侧等值),WP-P3-C 行位于 L182-L186,逐字抄录:

```text
L182: **WP-P3-C 预测复盘与错误模式统计**(挂靠编号: **#35**)
L183: - 目标: 落地 §5.2 归类框架/统计口径/反馈闭环(只读聚合+警示清单)。
L184: - 范围: 终态预测归类器(四轴)/分桶统计器/假设生成警示清单生成;承接在场载体(observations/裁决记录)零改写。
L185: - 依赖: WP-P3-A(版本记录供终态判定);层序前置(同上)。
L186: - 验收要点草案: ①历史裁决记录零改写断言 ②归类框架与统计口径参数(DP-5/DP-6: 窗口 12 个月 [示意·非实取,DP-5 登记候选]/分母口径)**先登记后运行、禁回改**负向测试 ③inconclusive/not_yet_triggered 不入错误分母断言 ④警示清单只作输入槽位、周报结构与回写路径零改动断言 ⑤CI 零回归。
```

四要素齐备(目标 L183/范围 L184/依赖 L185/验收要点 L186 共 4 条),无缺失。核验:
- **C 行可区分性**: 与 A/B/D/E/F 行四要素逐项可区分(A=档案检索与结论版本管理 L170-174/B=新证据关联与持续跟踪聚合 L176-180[同族前列件行]/D=报告质量评价循环 L188-192/E=个人流程整合接口 L194-198/F=终验+总封版 L200-208;C 行题名「预测复盘与错误模式统计」与挂靠 #35、归类器/统计器/警示清单三件范围要素均为他行所无)→ 合同附录A §零(iv)冲突处置首项不触发;冻结章 §十一 注记行号 L181-185 与本实读 L182-186 偏差恰 1 行(≤3 行容差内,AC-01 判据满足);
- **依赖列核验**: 「WP-P3-A(版本记录供终态判定)」=同族前列件 R038+R067 整体 PASS 已合入 main(冻结章 §十一 生效前置达成登记,注入摘要,非工作树实读;其尖端 202a09d2 在 BASE-P3C 谱系内[冻结章 §十一 BASE-P3C 实值依据]),交付件在本基线工作树在场(`scripts/research_index.py`+`tests/test_p3_wp_a.py`+`docs/P3_WP_A_REPORT.md`+`docs/P3_WP_A_DELIVERY.md` [实取·本工作树 git ls-files 清点=4 件,与 WP-A REPORT §零.2 登记清单一致]);「版本记录供终态判定」=本包终态锚定面消费入口(P-C-03);「层序前置(同上)」=§7 L168 层序排程依赖声明(冻结章 §十一 登记逐层核验 ✓,注入摘要,非工作树实读);依赖列与 BASE-P3C(`c14931c…`)无矛盾、**不要求并入其他支**(本包无并入步,纯线性)✓;
- **范围列无真实 GLM 调用/网络出站/付费凭证要求**: 范围列 L184 零 GLM/网络/凭证/付费字样;三件(终态预测归类器[四轴]/分桶统计器/假设生成警示清单生成)均为确定性结构;所引 §5.2 L134 反馈闭环明文「作为**输入槽位**注入…(只加输入,不改周报结构与回写路径)」且闭环消费面(周报证据校准段/§6.1 质量循环)=WP-P3-D 范围 → 无情形(d)停止条件。

### §零.2 交付文件清单(k=4 [实取·本节清点],登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据(推导逐条附) |
|---|---|---|
| 1 | `scripts/prediction_review.py` | DESIGN L184 范围列三件(终态预测归类器[四轴]/分桶统计器/假设生成警示清单生成)=**恰 1 个代码模块**: WP 题名「预测复盘与错误模式统计」(L182)单一工作包,三件共享终态判定/四轴词表/窗口口径与同一状态文件输入面(§5.2 L130-134 归类-统计-警示三段同环,同一批已终态预测样本流经三件;L186②「归类框架与统计口径参数」并列单点登记=同模块参数面)+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」;文件名=域词 prediction(预测)+review(复盘,WP 行题名「预测复盘」用词),避开既有 `daily_prediction_observer.py`(每日观察器,写路径件)与 `evidence_linkage.py`(WP-B)(ls scripts/ 实读,命名不冲突 [实取·开工 grep -ri prediction_review scripts/ tests/=0 命中]) |
| 2 | `tests/test_p3_wp_c.py` | DESIGN L186①②③④工件「断言/负向测试」+合同附录A §零(ii)「含代码则必含 tests/test_p3_wp_c.py」 |
| 3 | `docs/P3_WP_C_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P3_WP_C_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L186⑤「CI 零回归」证据落点=DELIVERY |

### §零.3 结构约束核验(2026-11-07T19:3xZ 实取)

- 与 `git ls-files` 零重合: 4 路径 `git ls-files scripts/prediction_review.py tests/test_p3_wp_c.py docs/P3_WP_C_REPORT.md docs/P3_WP_C_DELIVERY.md` 输出=0 行 [实取·开工 git ls-files]→ 纯新增 ✓;
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p3_wp_c.py)✓;
- 推导无越界: 范围列恰 1 个代码模块(§零.2 行 1 依据,同族前列件 WP-A/WP-B 单模块先例 P-A-01/P-B-01 同构)→ scripts/ 恰 1 文件;未引入 DESIGN 依据外文件 ✓。

### §零.4 DP 登记(开工首步登记定值;DESIGN 决策点登记表 L226-L241 实读,DP 共 10 个 [实取·表清点],行内所引=DP-5/DP-6 均登记型)

| DP | 分类(DESIGN 实读) | 本包登记定值(登记即实现值,先登记后运行,禁回改) | 依据 |
|---|---|---|---|
| DP-5 错误模式归类框架与统计窗口 | 登记型(L234) | **四轴归类 × 滚动窗口 12 个月**(推荐项全取): 四轴=方向错误(direction_error)/期限错误(horizon_error)/幅度错误(magnitude_error)/前提类(premise_class),词面=§5.2 L130 括注逐字(方向错误[判断涨实际跌/反向]/期限错误[方向对窗口错]/幅度错误[方向对量级错]/前提类[前提未兑现或无法裁决]);窗口=滚动 12 个日历月闭区间(P-C-04);候选 6/24 个月不采 | L234+L130+L132 |
| DP-6 复盘统计分母口径 | 登记型(L235) | **(a) inconclusive/not_yet_triggered 不入分母单列**: 命中率分母=窗内终态 hit+miss;inconclusive 与 not_yet_triggered(终态未生效)单列计数与样本清单,不入错误分母;命中率=hit÷(hit+miss)(§5.2 L132 口径提案);分母=0→hit_rate=None 如实缺席(不填 0);全样本入分母的 (b) 不采 | L235+L130+L132 |
| DP-1/DP-2/DP-3 | 登记型(L230-232) | **上游 WP-P3-A 已登记定值**(旁路索引文件/O-1~O-4 全 4 类/记录级粒度;本包只读复用其载体面与词表常量,不重新登记不改写;WP-A REPORT §零.4 登记在案) | L230-232 |
| DP-4/DP-8/DP-9/DP-10 | 确认权留用户(L233/L237/L238/L239) | **本包零触及**: DP-4=§4.1 关联第三层(WP-P3-B 面)、DP-8=§6.1 提示词注入(WP-P3-D 面)、DP-9=§6.2 接口(WP-P3-E 面)、DP-10=终验观察窗(WP-P3-F 面)——均非 C 行范围列(L184)所及,本包无 GLM/费用/个人流程/LIVE 面 | L233/L237-239 |
| DP-7 | 登记型(L236) | **本包不触及**(WP-P3-D 面: 质量评价维度);零引用零改写 | L236 |
| **行内登记型参数(警示阈值)** | 登记型(L186②「先登记后运行、禁回改」+§5.2 L134「阈值登记项[示意·非实取]」+§8.5「各包登记项」类) | **P-C-09 于 §零.5 登记定值**(机制类别末端连续 miss 游程阈值=3);登记定值即实现值,先登记后运行,运行后禁回改(负向测试面见 §二) | L134+L186②+L220 |

DP 编号/数量/分类与 DESIGN 实读一致: 行内所引 DP-5/DP-6(L186② 明文)均登记型(L234/L235 表行分类「登记型」逐行一致),已登记定值;确认型(DP-4/8/9/10)未被自决实施(§零.1 核验: 范围列零触及面);DP-1/2/3 上游登记面只读复用;DP-7 他包面零触及。

### §零.5 实现参数登记(P-C-01..P-C-16,先登记后实现,运行后禁回改)

| # | 参数 | 登记定值 | 依据 |
|---|---|---|---|
| P-C-01 | 模块载体 | `scripts/prediction_review.py` 恰 1 文件(终态预测归类器[四轴]+分桶统计器+假设生成警示清单生成三组件同模块,§零.2 行 1) | DESIGN L184+§零.2 |
| P-C-02 | 终态判定词表与规则 | 结果终态词表 `RESULT_TERMINAL_STATUSES=("hit","miss","inconclusive")`(report_generator L534 裁决 4 值之前三,evidence_linkage L63 TERMINAL_PRED_STATUSES 同源);not_yet_triggered 终态判定=status==not_yet_triggered 且 deadline≤as_of(引擎语义 [实取·allocation_engine evaluate_predictions L913-915「前提条件至截止日未成立,预测未生效(截止日不顺延)」终态化口径+L691-709 _is_final_prediction 三序判定];deadline 缺席/不可解析→ValueError fail-loud);observing/open=未决(pending,不入复盘单列);未知 status→ValueError fail-loud;**status 面以状态文件为权威**(O-3 载体 DESIGN §2.1 L51),版本记录仅作锚定与对账(P-C-03) | DESIGN L124+rg L534+ae L913-915 |
| P-C-03 | 终态锚定日期(版本记录供终态判定) | anchor_date 判定序(先者优先): ①`resolved_date` 非空且规范→取日期段(引擎裁决落档日 [实取·allocation_engine L1529/L1548/L1587/L1590 写入面]);②缺席→该 `PRED-{pred_id}` 在结论版本链(WP-P3-A `rri.list_conclusion_versions` 产出,object_type=prediction+change_type=status_change)最新记录(按 created_at,同刻按 version_id)created_at 日期段——**依赖列 L185「版本记录供终态判定」消费入口**;③再缺席→deadline 日期段。对账面: 版本链在场且其最新 status_change 变更 after 值与状态文件现值失配→`discrepancies` 如实清单(不改判不 fail: 版本链=旁路 append-only 记录,状态文件=权威载体;§3.1 L73「不复制数值语义为第二事实源」);version_records 注入面=已验证记录形,模块对注入记录做必备字段轻校验(record_type/version_id/object_type/object_id/change_type/changes/created_at 缺一→ValueError fail-loud) | L185+WP-A P-A-11/12 |
| P-C-04 | 滚动窗口(DP-5 窗口半) | `DP5_ROLLING_WINDOW_MONTHS=12`;窗口=[as_of 减 12 个日历月同日, as_of] **闭区间**;月末日钳制(目标月无同日→取当月最后一日,如 2024-02-29→2023-02-28、2026-03-31→2025-03-31);样本入窗判据=anchor_date∈窗口 | DP-5+L132 |
| P-C-05 | 归类框架(DP-5 四轴半+DP-6 分母口径) | miss→三轴之一或 unclassifiable;hit→correct_samples(正确模式样本,L130「hit 归正确模式样本」);inconclusive→premise_class 单列(无法裁决);not_yet_triggered 终态→premise_class 单列(前提未兑现);未决(observing/open/nyt 未到期)→pending_excluded 不入复盘;**分母=窗内终态 hit+miss**(DP-6(a)),inconclusive/not_yet_triggered 终态单列不入错误分母;unclassifiable miss 计入分母(状态面 miss 事实)但单列于三轴之外(数据不足不硬归类,§8.7「统计缺席走结构化 NO_DATA」同源纪律) | DP-5/DP-6+L130 |
| P-C-06 | 归类数值规则(miss 三轴,零 GLM 确定性) | 观察窗=`ae._window_obs(p)` 在场复用(L819-826,[observe_from\|date_made, deadline] 闭区间,禁窗内外推);价格口径 basis=`p.get('price_basis','close')`(ae L885/L949 同式),观测值经 `ae._obs_field_value` 复用(L829-835);可用观测=窗内 basis 口径值非 None 按 obs_date 升序。**规格不可计算**(metric 缺席/comparator∉ae.COMPARATORS/target 非数值,ae._pred_spec L677-680 口径)或**可用观测<2 条**→unclassifiable(reason=spec_not_computable/insufficient_window_observations,如实单列)。否则: start_v=首条可用观测值;终值 final_v: verify_mode=expiry→有效截止交易日(`ae.settlement_date(deadline, ae.market_of_metric(metric))` 复用,L865-876/L854-862)当日 close 口径观测值(缺席→窗内最后可用观测,final_source=last_window_observation_fallback 如实标记)/touch→窗内最后可用观测(basis 口径,final_source=last_window_observation);窗口后兑现计数 post_deadline_hits=记录全量 observations 中 obs_date>deadline 且 basis 口径值满足 `ae.COMPARATORS[comparator]` 的观测数。**三轴判定**: comparator=="=="→无方向轴→magnitude_error(水平未达);预期上行(comparator∈{">=",">"})且 final_v<start_v,或预期下行("<=","<")且 final_v>start_v→direction_error(判断涨实际跌/反向);方向正确(或持平)且 post_deadline_hits>0→horizon_error(方向对,兑现迟于窗口);其余→magnitude_error(方向对量级未达)。判定依据明细 basis={window,price_basis,comparator,target,n_usable,start_v,final_v,final_source,post_deadline_hits,unclassifiable_reason?}随行输出,零改写输入 | DESIGN L130+§5.1 L122-126+ae 复用面 |
| P-C-07 | 分桶维度 | 资产轴=`p.asset` 原样(状态文件字段;缺席→None 单列键 None);机制轴=metric 在场→`ae.mechanism_of(metric)` 复用(L117-124,词表 `ae.MECHANISM_CATEGORIES` L104=report_generator L518 同源 7 类 [实取·两处词面比对]);metric 缺席(定性预测)→None 如实缺席单列(不冒充机制归类);期限桶 `HORIZON_BUCKETS=(("≤2周",1,2),("3-8周",3,8),("≥9周",9,None))`: horizon_weeks≤2→"≤2周"/3-8→"3-8周"/≥9→"≥9周";horizon_weeks 缺席或非数值→None 单列;桶行 schema={count,hit,miss,inconclusive,not_yet_triggered_terminal,hit_rate}(分母口径同 P-C-05,hit_rate=None 当 hit+miss=0);桶键按字典序( None 键排首) | DESIGN L132「按资产/机制类别/期限桶(horizon_weeks)分桶」 |
| P-C-08 | 统计文档 schema 与确定性序列化 | `{schema_version:1, note:<免责声明>, as_of, window_start, window_end, counts:{hit,miss,inconclusive,not_yet_triggered_terminal,hit_rate,out_of_window_terminal,non_terminal_excluded}, error_patterns:{direction_error,horizon_error,magnitude_error,unclassifiable}, correct_samples, premise_class:{inconclusive,not_yet_triggered_terminal}, excluded_pending, buckets:{asset,mechanism,horizon}, discrepancies}`;counts.*=窗内计数(excluded_pending/non_terminal_excluded=未决数,out_of_window_terminal=终态但锚定出窗数);样本列表=[pred_id…] 按 (anchor_date,str(pred_id)) 排序;归类行序=输入序(状态文件序,同输入同输出);hit_rate=精确浮点除(无舍入,渲染面另格式化);序列化=`json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=1)`(家族先例 P-A-03 同款) | DP-5/DP-6+AC-03 确定性 |
| P-C-09 | 警示清单规则(阈值登记项) | `WARNING_CONSEC_MISS_THRESHOLD=3`(DESIGN §5.2 L134「如某机制类别连续 miss 达阈值[示意·非实取,阈值登记项]」——本登记即定值);规则: 窗内(category∈{hit_sample,error_pattern})且机制轴非 None 的样本按机制分组,组内按 (anchor_date,str(pred_id)) 升序,取**末端连续 miss 游程**长度≥3→警示条目;条目 schema={mechanism,axis_label,consecutive_misses,miss_pred_ids,threshold,window_start,window_end,slot};slot=`"hypothesis_generation_warning_input_slot"`(**只作输入槽位**: L134 明文「作为输入槽位注入周报生成的证据校准段(只加输入,不改周报结构与回写路径)」——本包产出=数据结构与旁路渲染文本,**零注入零回写零周报系统触碰**;周报消费面=WP-P3-D 范围禁提前带入);条目按 mechanism 字典序;**只读聚合,不自动修改任何论点/观点/预测**(L134 闭环纪律) | DESIGN L134+要点④ |
| P-C-10 | 只读零写入纪律 | 模块**零文件写入面**(全源码零写模式 open/零 os.replace/零 json.dump/零临时文件/零 shutil);状态文件只读直载 `json.load`(**不经 `ae.load_views`**——其读侧归一 `_migrate_views` L145-173 对 dict 就地变更,复盘面禁用,防内存态扰动;fixture 供 v3 规范形);历史裁决记录(observations/resolved_note/status/resolved_date 等全字段)零改写(要点①;§5.2 L132「统计为只读聚合,不改写任何历史裁决记录(append-only)」);断言面=测试字节级 sha256 前后等值+AST 零写调用 | 要点①+L132 |
| P-C-11 | 上游复用面(对齐=复用调用,禁复制分叉) | ae: `_window_obs`/`_obs_field_value`/`COMPARATORS`/`market_of_metric`/`settlement_date`/`mechanism_of`/`MECHANISM_CATEGORIES`(读侧复用);rri(WP-P3-A): `list_conclusion_versions`/`PREDICTION_KEY_PREFIX`/`DEFAULT_ARCHIVE_DIR`(便利编排面 archive_dir 缺省只读);零 drr/rp/sb 直接依赖(本包无快照绑定面/无档案写入面;rri 内部自理) | AC-05.5+依赖列 L185 |
| P-C-12 | 纯度与免责 | import 面白名单={json,os,sys,datetime+项目既有 allocation_engine,research_index}(纯标准库+项目既有依赖);AST 零网络 import(urllib/requests/http/socket/httpx 禁);零凭证/密钥/token;免责三处=模块 docstring+统计文档 note+警示简报尾行,词面携「预测复盘与错误模式统计面输出,不构成投资建议(禁交易/禁仓位/禁收益承诺)」(§8.3 红线承接) | AC-05.4+AC-07.3+§8.3 |
| P-C-13 | as_of 注入纪律 | 一切日期依赖纯函数(classify/statistics/warnings/window_bounds)显式 as_of 必填(测试恒显式注入,零墙钟);唯一墙钟缺省=便利编排面 `prediction_review_report(views_path, as_of=None,…)` 边缘(测试恒显式) | AC-03 确定性纪律 |
| P-C-14 | 他包范围排除 | WP-P3-D 质量循环/提示词注入零实现零引用(警示清单=输入槽位数据结构,消费面留 WP-D,L134→§6.1 链条);WP-P3-A/B 面只读复用零改写;W4/W5 侧边验收工具零接入(AC-07.6);report_generator/data_validator/主流水线零触碰(白名单 M=0 结构性保障) | AC-08.1/8.3+要点④ |
| P-C-15 | DP/参数哨兵 | `registered_dp_values()`+`registered_param_values()`(活性常量)+`dp_selfcheck()`(活性常量 vs 模块内登记镜像逐值对照,回改任一定值→AssertionError);`__main__` 自检入口零写入零默认路径 | DP 纪律+WP-A/B 先例 |
| P-C-16 | 零运行产物判定 | C 行验收要点 5 条(L186①-⑤)全为测试面/CI 面(①②③④=断言与负向测试,⑤=CI 工件;范围列 L184 零「真实运行/端到端/编排入口」措辞,对照 WP-A 行 L174/WP-B 行 L180 同构判定先例)→ **本包登记「零运行产物」**,`data/research/` 零写入(统计/警示全落函数返回值与测试临时沙箱);`.gitignore` 不改 | 合同§零 运行产物边界+要点对照 |

### §零.6 前置实读登记(file:line;基线工作树 2026-11-07T19:2x-19:3xZ 实取)

- DESIGN 相关节(工作树在场件,=7f43724 侧 blob 等值,§零.7): §2.1 积累对象 L47-53(O-3 预测记录与裁决 L51)/§3.1 快照纪律 L69-73/§5 预测验证与复盘 L120-134(§5.1 承接载体 L122-126/§5.2 方法论 L128-134)/§7 层序声明+WP-P3-C 行 L166-210(C 行 L182-186)/§8 红线 L214-222(快照纪律 L216/禁建议 L218/append-only L220/如实 L222)/决策点登记表 L226-241(DP-5 L234/DP-6 L235);
- 上游在场件(只读禁改,对齐=复用调用):
  - `scripts/allocation_engine.py`: PRICE_BASIS_CN L82/_PRED_STATUS_MAP L85-93/COMPARATORS L95-101/MECHANISM_CATEGORIES L104/METRIC_MECHANISM L106-114/mechanism_of L117-124/due_predictions L187-192/_pred_spec L677-680/_premise_spec L683-688/_is_final_prediction L691-709/record_observations L726-816/_window_obs L819-826/_obs_field_value L829-835/market_of_metric L854-862/settlement_date L865-876/window_coverage L879-892/evaluate_predictions L895-1008(nyt 终态化 L913-915/touch L950-984/expiry L985-1007)/predictions_in_period L1011-1029;
  - `scripts/research_index.py`(WP-P3-A): DEFAULT_ARCHIVE_DIR L74/COLLECTION_VERSIONS L75/OBJECT_TYPES L86/PREDICTION_KEY_PREFIX L96/validate_conclusion_version_record L503-542/list_conclusion_versions L616-629;
  - `scripts/evidence_linkage.py`(WP-P3-B): TERMINAL_PRED_STATUSES L63(终态词表同源锚);
  - `scripts/report_generator.py`: 论点状态词表 L501/机制类别 7 类词表 L518/预测裁决词表 4 值 L534/裁决纪律 L536-540(前提未兑现不得判 hit L540);
  - `config/allocation_views.json`(门禁后状态文件): predictions[] 18 字段(pred_id,date_made,asset,direction,horizon_weeks,deadline,trigger,status,metric,comparator,target,evidence_ref,premise_text,verify_mode,observations,data_source,note,resolved_note [实取·predictions[0] 键清点=18]);生命周期附加字段经引擎面(premise/observe_from/premise_triggered_date/price_basis/resolved_date/final [实取·allocation_engine L759-771/L791-795/L821/L885/L1529+ 读写面]);
  - 同族前列件 REPORT: `docs/P3_WP_A_REPORT.md` §零.2 登记清单(k=4)/§零.5 参数面、`docs/P3_WP_B_REPORT.md` §零.2 登记清单(k=4)/§零.5 参数面/§零.10 实现期登记(fixture 形态与本地 CI 镜像方法学先例);
  - `docs/P3_INVENTORY.md`(P3-G-04 统计半→WP-P3-C 承接,DESIGN L210 缺口承接句实读)。

### §零.7 开工核验(2026-11-07T19:2x-19:3xZ 实取)

- 步骤0: `git status` clean(开工时在 dev/p3-impl-b@e21789a,工作树干净,非本包所致脏=无);UTC 开工时刻 2026-11-07T19:32:16Z;
- 步骤1: 合同三占位符均实值化(BASE-P3C=c14931c34f23dacc3439cc2609cf51a89d7ea60f 全值/BASE-P3C-CI-SUITES=84/BRANCH-SET=57 支全表 §十一.1 内嵌),无未解析标记 ✓;生效前置信号=冻结章 §十一 生效前置达成登记(WP-P3-A R038+R067 PASS+层序闭合,注入摘要,非工作树实读)✓;
- 步骤2: `git ls-remote origin main dev/p3-design-fix1 dev/p3-impl-a dev/p3-impl-b dev/p3-impl-c` 实取: main=`c14931c34f23dacc3439cc2609cf51a89d7ea60f`(=BASE-P3C 全值一致 ✓,=冻结章登记前件分支尖端)/dev/p3-design-fix1=`7f43724661b50e011394e643cdd8c223c0b27a90`(全值一致 ✓,未锚 f93adb5)/dev/p3-impl-a=`202a09d2570f2894acff05fb8fe1a4dbe7c26a79`(一致 ✓)/dev/p3-impl-b=`e21789a72b83c765b8fc54264372951db53abcfa`(一致 ✓)/dev/p3-impl-c 零命中(无预创建违规 ✓);
- 步骤3: `git checkout -b dev/p3-impl-c c14931c…` 自基线全值切出(非自当前 HEAD 盲切)✓;
- 步骤4(设计在场核验,本包无并入步): ①`git merge-base --is-ancestor 7f43724661b50e011394e643cdd8c223c0b27a90 HEAD`→exit 0 可达(经祖先在场,冻结章 §十一 路径甲注记一致)✓;②设计三件 `git ls-tree` 双侧(HEAD vs 7f43724)blob 逐一相同: P3_INVENTORY=9f366da5a9e327e524ae1a17eec229722cd85d5f/P3_DESIGN=5acc130a88d9635a1e82d7ad3beb4f1dbe008106/P3_DELIVERY=ac8965ce0e09a964f5b493ebe1ef7dcacfca9b2d ✓;
- CI 基线: `ls tests/test_*.py` 计数=84 [实取·开工清点]=BASE-P3C-CI-SUITES 84 槽口径一致(83 exit0+1 SKIP,冻结章 §十一 CI 基线实值依据;分支 run 预期=84+本包新增 tests 文件数 1=85);本地 Python 3.9.6(CI=3.11),实现保持 3.9 兼容语法(WP-A/B 同款约束)。

### §零.8 AC-03.7(GLM 桩边界)适用判定

登记清单(§零.2)无 GLM/LLM 能力级调用面实现文件(范围列 L184 零 GLM 字样;模块=归类器+统计器+警示清单确定性结构;§5.2 归类框架为登记型零 GLM 路径)→ **AC-03.7 不适用**,判定依据=清单无调用面类文件(§零.2 表 1-4 无客户端封装/调用编排/适配器类)。

### §零.9 实现期登记(实现笔回填;实现笔=cdd7dba,2026-11-08 实取)

- **交付物双代码件**(实现笔 git-show 尖端版=工作树版,shasum -a 256 双源与装配期一致): `scripts/prediction_review.py` 642 行,sha256=`bc1c4a543e7e7be9ea0330c1e3a3e61cc5ce0ef1046982588c0a70e2518ac7e1`;`tests/test_p3_wp_c.py` 1306 行,sha256=`a9effbcd493765face2f75a9fd1a8db4f8e9084dc27420af6039cf8046121d06` [实取·shasum];
- **合成 fixture**(唯一数据源,18 预测 C01..C18+版本记录 5 条,as_of=2026-10-31,窗口 [2025-10-31,2026-10-31]): 与独立首原理预计算件 `/tmp/p3-wp-c/fixture_and_golden.py`(零被测模块 import)字面量逐字节一致 [实取·/tmp/p3-wp-c/fixture_byte_equality.py 六面裁定=preds/versions/doc/warnings/briefing/sha256 全 OK];fixture 一致性三方裁定(手推黄金==模块输出==上游 ae 锚定 settlement/mechanism/词表)`/tmp/p3-wp-c/fixture_consistency.py` 全 OK(含 str-only 文档 dump==sort_keys 形等值性检查);
- **黄金值登记**(首原理固化,测试内 hashlib 复算双源一致): 统计文档 canonical sha256=`2c40919e35d60cc9dd32939adde27504cb12be6e33ee8d1f699bbc0b31ac5eb7`;警示清单 canonical sha256=`a3004f5e253bc4051a9b7821cfe6f436abf526a120a30cbe0aeed50bfbafd8c2`;简报文本 sha256=`7a9ec406f48c933a381d97e8474ec80b84a01828a5316ac014ecb46c3b63c980`;黄金数值锚: 窗内 hit=3/miss=10/inconclusive=1/nyt 终态=1,hit_rate=3/13(精确浮点 0.23076923076923078),窗外终态=1,未决=2;
- **用例分类**: 115 用例 15 类 [实取·unittest 计数]: ①黄金首原理复算(6) ②DP/参数登记哨兵含 monkeypatch 回改检出 6 面(10) ③滚动窗口边界月末日钳制(7) ④终态判定(9) ⑤锚定序 resolved_date→VER→deadline+失配(10) ⑥miss 三轴规则含 touch-high/settlement 回退/窗前观测排除/方向优先于期限(15) ⑦归类行 schema/序/单列(8) ⑧分桶统计黄金含 DP-6 分母/空文档/零分母 None(12) ⑨警示游程边界恰 3 触发/2 不触发/hit 打断/premise 不成组/unclassified 计入游程/哨兵不从调用方读(9) ⑩简报渲染含免责尾行/N-A 分母(7) ⑪只读零写入(views 字节等值/fixture 零突变/archive 零创建/repo config 套件前后等值)(5) ⑫编排面(空链黄金/注入面等值/墙钟缺省/负向 4 面)(7) ⑬AST 纯度(import 白名单/禁网/只读 open/零写调用/禁字符串/编译)(6) ⑭负向输入(7) ⑮__main__ 自检(subprocess 受控 1 处)(1);
- **实现期缺陷修复 1 处**(实现笔前修复,如实登记): `registered_param_values()` 期限桶镜像格式化 `≥9周:9-+`→`≥9周:9+` 与 §零.5 登记字面量对齐(镜像格式缺陷,登记定值本身未动;首运行 dp_selfcheck 检出);
- **实现期口径修正 1 处**(首原理预计算件检出,如实登记): `dump_statistics` 序列化——`json.dumps(sort_keys=True)` 对 P-C-07 登记的 None 单列桶键抛 TypeError(CPython 不支持 None/str 混合排序)→ 增 `_canonical_order` 递归确定序(None 键排首)后 sort_keys=False 序列化;str-only 文档产物与 §零.5 P-C-08 登记序列化式**逐字节等值**(测试断言+fixture 一致性双面);P-C-07 None 单列键与 P-C-08 确定性序列化两登记定值同时保真;
- **负向敏感性三注入**(红→还原→复绿→sha256 前后等值零残留,记录件 `/tmp/p3-wp-c/negative-sensitivity-record.txt`): INJ-1 方向轴判定翻转(magnitude_error 冒充 direction_error)→ 红;INJ-2 警示阈值哨兵旁路(阈值-1,游程 2 也触发)→ 红;INJ-3 DP-6 分母口径破坏(inconclusive 入分母,hit_rate 3/13→3/14)→ 红;三注入后模块 sha256=实现笔全值等值;
- **本地 CI 镜像**(CI 同款逐文件串行,记录件 `/tmp/p3-wp-c/local-ci-mirror.txt`): 85 文件=84 exit0+1 SKIP(test_glm_live)+0 非零 [实取·镜像记录]=基线 84 槽零回归+本包恰 +1(test_p3_wp_c),与 §零.7 预期一致;
- **零运行产物锚定**: `find data/research -newer docs/P3_WP_C_REPORT.md` 零输出 [实取·find];`git status` 实现笔前后工作树仅白名单 2 文件纯新增(M=0/D=0);
- **编号注记**: 实现笔提交信息所称「REPORT §零.10 实现期登记」实为本 §零.9(本 REPORT 无 §零.10;提交信息编号笔误,内容指向无误,终笔不回改——如实登记)。

---

## §一 实现摘要

`scripts/prediction_review.py`(642 行,§零.9 sha256)按 §零.4/§零.5 登记定值确定性落地,四组件:

1. **终态预测归类器(四轴,DP-5)**: `terminal_state`(P-C-02 词表: hit/miss/inconclusive 结果终态;not_yet_triggered 且 deadline≤as_of 终态化[引擎 L913-915 语义];observing/open 未决;未知 status/nyt 缺 deadline→ValueError fail-loud)+`anchor_date_of`(P-C-03 判定序 resolved_date→结论版本链[rri.list_conclusion_versions,object_type=prediction+change_type=status_change 最新 created_at,同刻按 version_id]→deadline;版本链 after 值与状态文件失配→discrepancies 如实清单[状态文件=权威载体,不改判不 fail])+`classify_miss`(P-C-06 三轴: ae._window_obs/_obs_field_value/COMPARATORS/market_of_metric/settlement_date 在场复用;==无方向轴→幅度错误/预期反向→方向错误/方向对且 post_deadline_hits>0→期限错误/其余→幅度错误;规格不可计算或可用观测<2→unclassifiable 单列;终态 miss 缺 deadline→ValueError)+`classify_predictions`(行 schema 13 键,行序=输入序;hit→hit_sample/miss→error_pattern/inconclusive 与 nyt 终态→premise_class 单列[DP-6(a)]/未决→pending_excluded);
2. **分桶统计器(§5.2 L132)**: `window_bounds`+`shift_months`(P-C-04 滚动 12 个日历月闭区间,月末日钳制)+`_bucket_rows`(P-C-07 资产/机制[ae.mechanism_of 复用]/期限桶 ≤2周-3-8周-≥9周,缺席轴 None 单列键,桶行 6 键含 hit_rate=None 当分母 0)+`review_statistics`(P-C-08 统计文档 12 键;hit_rate=hit÷(hit+miss) 精确浮点)+`dump_statistics`(确定性序列化,_canonical_order None 键可承载形,§零.9 口径修正);
3. **假设生成警示清单(§5.2 L134)**: `hypothesis_warnings`(P-C-09 窗内机制分组末端连续 miss 游程≥3[登记阈值]→条目;条目 8 键携 slot=hypothesis_generation_warning_input_slot;只读聚合零写入)+`render_warning_briefing`(旁路渲染纯文本,零注入零回写零周报系统触碰;消费面=WP-P3-D 范围禁提前带入);
4. **编排面与哨兵**: `prediction_review_report`(P-C-13 唯一墙钟缺省=as_of 边缘;状态文件只读直载 json.load 不经 ae.load_views;archive_dir 只读)+`registered_dp_values`/`registered_param_values`/`dp_selfcheck`(P-C-15 登记哨兵,回改任一定值→AssertionError)+`__main__` 自检零写入。

测试面 `tests/test_p3_wp_c.py`(1306 行 115 用例 15 类,§零.9 分类): 全合成 fixture 18 预测+版本记录 5 条唯一数据源;预期值一律字面量硬编码不从被测模块派生;三黄金 sha256 首原理固化+测试内 hashlib 复算双源;DP-5/DP-6/阈值回改 monkeypatch 检出 6 面;AST 纯度面;只读零写入字节级断言;负向输入 fail-loud;1 处 subprocess 受控用途(§三)。

## §二 AC-02 五要点逐条映射表(DESIGN L186①-⑤)

| 要点 | 落地面(测试 file:case) | 结果 |
|---|---|---|
| ①历史裁决记录零改写断言 | TestZeroWrite.test_views_file_bytes_unchanged_after_report(编排面全流程后 views 文件字节 sha256 前后等值)+test_input_fixture_dicts_not_mutated(输入 fixture 深比较零突变)+test_archive_dir_not_created(archive 目录零创建)+模块面 P-C-10(零文件写入面,observations/resolved_note/status/resolved_date 全字段零改写,AST 零写调用断言 TestStaticPurity.test_zero_write_calls)+TestZeroWrite 套件级 repo config/allocation_views.json sha256 前后等值(setUpModule/tearDownModule) | PASS [实取·115/115 OK] |
| ②归类框架与统计口径参数(DP-5/DP-6: 窗口 12 个月/分母口径)先登记后运行、禁回改负向测试 | 登记时序: §零.4/§零.5 登记笔 ca56427(2026-11-07)先于实现笔 cdd7dba(2026-11-08)(git 时序);运行期哨兵 dp_selfcheck(活性常量 vs 模块内登记镜像逐值对照)+负向检出 TestDPParamRegistration.test_monkeypatch_window_months_detected(DP-5 窗口 12→6→AssertionError)/test_monkeypatch_dp6_scope_detected(DP-6 口径→AssertionError)/test_monkeypatch_threshold_detected(P-C-09 阈值 3→2→AssertionError)等 6 面;字面量三方一致 test_registered_dp_values_literals/test_registered_param_values_literals/test_module_constants_vs_registered(常量=镜像=§零.4/§零.5 登记字面量) | PASS [实取·115/115 OK] |
| ③inconclusive/not_yet_triggered 不入错误分母断言 | TestStatisticsGolden.test_premise_class_excluded_from_error_denominator(C08/C09 不入三轴与 correct_samples;premise_class 单列清单断言)+test_full_document_equals_golden(黄金 counts: hit_rate=3/13 分母不含 inconclusive=1 与 nyt 终态=1)+test_zero_denominator_hit_rate_none(仅 inconclusive→hit_rate=None 如实缺席)+TestClassifyRows.test_premise_class_rows_dp6a(premise_class 类别行)+负向敏感性 INJ-3(inconclusive 入分母→红) | PASS [实取·115/115 OK] |
| ④警示清单只作输入槽位、周报结构与回写路径零改动断言 | 结构面: 警示条目携 slot=hypothesis_generation_warning_input_slot(P-C-09;TestHypothesisWarnings 黄金断言)+模块零周报系统触碰(P-C-14: report_generator 零依赖=TestStaticPurity.test_no_banned_strings 禁字符串断言;回写路径零改写=要点①面同源);渲染面 render_warning_briefing=纯函数返回字符串零写入(TestRenderBriefing 全类;TestZeroWrite 沙箱零新文件);消费面 WP-P3-D 零提前带入(P-C-14) | PASS [实取·115/115 OK] |
| ⑤CI 零回归 | 本地 CI 镜像(CI 同款逐文件串行)85 文件=84 exit0+1 SKIP+0 非零=基线 84 槽零回归+恰 +1(test_p3_wp_c) [实取·/tmp/p3-wp-c/local-ci-mirror.txt];CI 面 run=操作者 rounds/040 dispatch(执行席 NOT VERIFIED,§五/DELIVERY 承接) | 本地面 PASS;CI 面 NOT VERIFIED@执行席→操作者 dispatch |

## §三 如实偏差与登记承接

1. **实现期缺陷修复 1 处**: `registered_param_values()` 期限桶镜像格式 `≥9周:9-+`→`≥9周:9+`(§零.5 登记字面量对齐;首运行 dp_selfcheck 检出;登记定值未动)——登记于 §零.9,仿 WP-B「实现期缺陷修复」先例;
2. **实现期口径修正 1 处**: `dump_statistics` 序列化式——P-C-08 登记序列化式 `json.dumps(sort_keys=True)` 对 P-C-07 登记的 None 单列桶键抛 TypeError(登记内部张力,首原理预计算件检出)→ `_canonical_order` 确定序(None 排首)后 sort_keys=False;str-only 文档与登记式逐字节等值(测试断言);**两登记定值同时保真,非回改**(P-C-07 None 键保留/P-C-08 确定性保留)——登记于 §零.9;
3. **实现期口径补强 1 处**: 终态 miss 缺规范 deadline→classify_miss ValueError fail-loud——P-C-06 未明列该输入形(P-C-02 仅登记 nyt 缺 deadline 的 fail-loud);理由=窗口不可定界归类不可计算,fail-loud 优于沿用 ae._window_obs 的 9999-12-31 缺省假窗口;测试 TestClassifyMiss.test_miss_without_deadline_fail_loud;
4. **测试 1 处 subprocess 受控用途**: TestSelfcheckMain 以 subprocess 运行 `scripts/prediction_review.py` __main__ 自检(受控: sys.executable+仓库内路径+timeout=60+capture_output;仿 WP-B 先例登记);AST 纯度禁 subprocess 面仅约束被测模块(模块 import 白名单经 test_import_whitelist 断言零 subprocess);
5. **提交信息编号笔误**: 实现笔提交信息称「REPORT §零.10 实现期登记」,本 REPORT 实为 §零.9(无 §零.10;内容指向无误);已提交信息不回改,如实登记于 §零.9/本节;
6. **REPORT §零.1 行号偏差**: 冻结章 §十一 注记 C 行 L181-185 vs 基线实读 L182-186,偏差恰 1 行≤3 行容差(§零.1 已登记,AC-01 满足)——承接非新增;
7. **无其他偏差**: 未声明「无偏差」;WP-A/B 全部前序偏差项与本包无涉;DP-5/DP-6/P-C-01..P-C-16 登记定值运行后零回改(§四)。

## §四 DP 零回改自检表

| DP/参数 | 登记定值(§零.4/§零.5) | 实现值(实现笔尖端) | 零回改证据 |
|---|---|---|---|
| DP-5 | four_axis × 滚动 12 个月 | DP5_ERROR_FRAMEWORK="four_axis";DP5_ROLLING_WINDOW_MONTHS=12;四轴词面 §零.4 | dp_selfcheck 镜像对照+monkeypatch 检出(test_monkeypatch_window_months_detected)+字面量三方一致 |
| DP-6 | (a) inconclusive/not_yet_triggered 不入分母单列 | DP6_DENOMINATOR_SCOPE=hit_miss_only_inconclusive_nyt_listed_separately;counts 分母=hit+miss | 同上(test_monkeypatch_dp6_scope_detected)+INJ-3 负向敏感性红 |
| P-C-09 阈值 | 机制末端连续 miss≥3 | WARNING_CONSEC_MISS_THRESHOLD=3 | test_monkeypatch_threshold_detected+INJ-2 红 |
| P-C-02/07/08 | 终态词表/期限桶/schema v1 | RESULT_TERMINAL_STATUSES/HORIZON_BUCKETS/STATS_SCHEMA_VERSION 登记值 | test_monkeypatch_terminal_statuses_detected/nonmonotonic/schema_version 3 面+字面量断言 |
| DP-1/2/3 | 上游 WP-P3-A 已登记,只读复用 | 模块只 import ae/rri 读侧面,零载体改写 | AST import 白名单+零写调用+fixture 深比较零突变 |
| DP-4/8/9/10 | 确认型零触及 | 零实现零引用(§零.8 同判;grep 面=TestStaticPurity 禁字符串) | AST/字符串断言 |
| DP-7 | 不触及(WP-P3-D 面) | 零引用零改写 | 同上 |

## §五 git 纪律自检(七项)

1. 基线切出: dev/p3-impl-c 自 BASE-P3C `c14931c…` 全值切出(§零.7 步骤3,非自 HEAD 盲切)✓;
2. 纯线性: BASE 后登记笔 ca56427→实现笔 cdd7dba→报告笔(本笔)→终笔,零 merge 零 amend 零 force(git log --oneline 单父链)✓;
3. main 未触碰: 全程零 checkout main/零 push main;main 尖端开工 ls-remote=BASE-P3C 全值一致(§零.7 步骤2)✓;
4. LIVE 零写入: LIVE 目录零写入(DELIVERY 取证: grep R040/P3-WP-C/IA-P3-WP-C 零命中+real_data_acceptance.py sha256 不变)✓;
5. launchd 零改动: ~/Library/LaunchAgents 清单前后等值取证(DELIVERY)✓;
6. 零 tag: 全程零 git tag(基线先存 tag 与本包无涉)✓;
7. 网络: 仅取证类(ls-remote/push);终局单支推送 dev/p3-impl-c(不 force)→ ls-remote 全分支集比对 §十一.1 57 支冻结表(新增仅 dev/p3-impl-c)✓。

## §六 数值标注自检(AC-04;逐项实取·来源)

| 数值 | 值 | 标注 |
|---|---|---|
| 交付模块行数 | 642 行 | [实取·wc -l 实现笔工作树] |
| 测试行数/用例/类 | 1306 行/115 用例/15 类 | [实取·wc -l+unittest Ran 115 tests] |
| 模块/测试 sha256 | bc1c4a54…8ac7e1/a9effbcd…6121d06 | [实取·shasum -a 256 全值见 §零.9] |
| 合成 fixture 规模 | 18 预测+5 版本记录 | [实取·fixture 字面量清点] |
| as_of/窗口 | 2026-10-31/[2025-10-31,2026-10-31] | [实取·fixture 定值(合成,非真实日期数据)] |
| 黄金统计 sha256 三值 | 2c40919e…/a3004f5e…/7a9ec406… | [实取·/tmp/p3-wp-c 首原理预计算+测试内 hashlib 复算] |
| 黄金计数 | hit=3/miss=10/inconclusive=1/nyt=1/hit_rate=3/13 | [实取·手推黄金=模块输出=测试断言] |
| DP-5 窗口/DP-6 口径/阈值 | 12 个月/(a) 单列不入分母/3 | [实取·登记定值=模块常量=测试字面量] |
| CI 基线/镜像 | 84 槽/85 文件=84 exit0+1 SKIP+0 非零 | [实取·§零.7 清点+/tmp/p3-wp-c/local-ci-mirror.txt] |
| 负向敏感性 | 3 注入全红→复绿→零残留 | [实取·/tmp/p3-wp-c/negative-sensitivity-record.txt] |
| 零运行产物 | find data/research -newer REPORT 零输出 | [实取·find] |
| 分支笔序 | BASE c14931c→ca56427→cdd7dba→报告笔 | [实取·git log] |
| fixture 截止日交易日锚定 | 13 个 expiry 截止日 settlement==当日 | [实取·ae.settlement_date 复核(fixture 一致性件)] |

---

## §七 续段登记(R040 续段授权·分支 CI 红最小修复;2026-11-08 实取)

> 续段授权=操作者 2026-11-08 04:0x 指令(仿 R062/R048 v1.4 先例;附录A 合同文本零变更;注入摘要,非工作树实读)。续段基点=笔B 尖端 `b25542e7b64a1171cfd50f1c9ab83ad479b85d80`(开工核验 `git rev-parse HEAD` 实取全值一致,树 clean,UTC 2026-11-07T20:10:19Z);BASE 侧全值核验照旧(main ls-remote=`c14931c34f23dacc3439cc2609cf51a89d7ea60f` 等值/设计支=`7f43724661b50e011394e643cdd8c223c0b27a90` 等值/设计三件 blob 复核等值)。**本节纯追加,§零~§六 零改动**;§零.9/§六 的历史计数(115 用例 15 类/642/1306 行)为所属笔时点值,续段新值以本节为准(数值演进承接声明,防 AC-04 失实判定)。

### §七.1 根因(注入+工作树实读复核)

- 分支 CI run `42409208175`@b25542e=**failure**: 85 槽=83 exit0+1 红+1 SKIP,唯一失败用例 `TestOrchestrator.test_bad_as_of_rejected`(`as_of="20261031"` 期望 ValueError 实未抛)【注入摘要·操作者 CHECKPOINT 机器捕获,非执行席实取;执行席 run ID 不可见】;
- 解释器版本差实化(R067 审计 DEFERRED-4 预警【注入】): 本地镜像=venv `python3` **3.9.6** [实取·sys.version],CI=**3.11** [实取·.github/workflows/offline-tests.yml L29 `python-version: '3.11'`]——3.9 `date.fromisoformat` 拒收紧凑形(只收十位带杠形 YYYY-MM-DD)→`_require_iso_date` raise(本地绿);**3.11+ 扩收 ISO 8601 基本式**("20261031"→date(2026,10,31) 不抛)→as_of 被放行(CI 红);
- 缺陷定位=模块守卫面(`_parse_iso_date` 以 `fromisoformat` 为唯一判定,scripts/prediction_review.py 修复前 L98-106);测试编码=登记口径「规范 YYYY-MM-DD」拒收非规范形→**缺陷在模块守卫面,禁以弱化测试转绿**(续段授权红线)。

### §七.2 修复(最小修复域,恰 1 函数;笔C)

- `scripts/prediction_review.py` `_parse_iso_date`: 截断候选 `t=s.strip()[:10]` 后增**规范形守卫**——十位带杠形(YYYY-MM-DD,第 5/8 位为 `-`)显式判定(`len(t)!=10 or t[4]!="-" or t[7]!="-"`→None)后才入 `date.fromisoformat`(或等价判定,授权原文口径);
- **语义不弱化论证**: 3.9 `fromisoformat` 恰只收十位带杠形(CPython 3.9 语义)→守卫+`fromisoformat` 对任一输入的行为与修复前 3.9 完全一致=3.9 规范语义精确复刻;规范形收/非规范形拒判定面**不放宽不收窄**;既有 `[:10]` 截断语义(内部 created_at 时间戳取日期段)/None 契约(P-C-02/P-C-03 调用方决定面)/`_require_iso_date` 消息词面零变更;
- **黄金面零影响**: 黄金 sha256 三值修复前后等值 [实取·首原理预计算件复跑: 统计文档 `2c40919e35d60cc9dd32939adde27504cb12be6e33ee8d1f699bbc0b31ac5eb7`/警示清单 `a3004f5e253bc4051a9b7821cfe6f436abf526a120a30cbe0aeed50bfbafd8c2`/简报 `7a9ec406f48c933a381d97e8474ec80b84a01828a5316ac014ecb46c3b63c980`];黄金计数 hit=3/miss=10/inconclusive=1/nyt 终态=1/hit_rate=3/13 不变;
- **DP 面**: 零新增 DP 零回改——守卫=已登记口径「规范 YYYY-MM-DD」(§零.5 P-C-03「非空且规范」用词+`_require_iso_date` 既有消息词面+`_parse_iso_date` 既有 docstring 首句)的合规修复,非参数变更;DP-5/DP-6/P-C-01..P-C-16 登记定值全部未动(§四 自检表面仍成立)。

### §七.3 tests 面(纯新增;笔C)

- 新增类 **⑯ TestCanonicalFormGuard** 5 用例: ①`test_guard_rejects_311_extended_family`(3.11 扩收形族 5 形 `20261031`/`2026-W44`/`2026W44`/`2026-W44-1`/`2026W441` 守卫级全拒)②`test_guard_accepts_canonical_form`(规范形收)③`test_guard_keeps_timestamp_tail_truncation`(既有截断语义保持不收窄)④`test_window_bounds_rejects_extended_forms`(公共 API 拒收)⑤`test_orchestrator_rejects_compact_as_of`(CI 红用例回归锚,编排面拒收紧凑形);
- 用例计数 **115→120,类 15→16** [实取·unittest `Ran 120 tests` OK];既有 115 用例**零删除零跳过零弱化**(diff 面纯新增行,无既有断言改动);
- 跨版本证明链(次新解释器执行席不可达,见 §七.4②): 守卫=纯字符串判定(len/index 比较)零解释器版本依赖;新增用例构成 **3.11 守卫敏感面**(守卫若缺席,`_parse_iso_date("20261031")` 在 3.11 返回 "2026-10-31"→①⑤必红=CI 唯一红机理);CI 3.11 复跑=操作者 CHECKPOINT。

### §七.4 复验记录(续段授权第 5 条逐项;2026-11-08 实取)

- **①本地逐套件串行镜像重跑全量**: 85 文件=84 exit0+1 SKIP(test_glm_live)+**0 非零**;test_p3_wp_c exit=0(含续段新增 5 用例) [实取·/tmp/p3-wp-c/local-ci-mirror.txt 复跑记录,记录头 2026-11-08 04:15:30];
- **②双解释器交叉佐证**: python3(3.9.6,venv,=镜像同款)TestCanonicalFormGuard 类级 5/5 OK+全套件 120 OK [实取·运行记录];**次新解释器(3.10+)执行席不可达**——`command -v`/直呼 python3.10..3.13 权限面拒绝或不存在、/opt/homebrew/bin 与 /usr/local/bin 目录不存在、/usr/bin/python3 直呼权限面拒绝 [实取·Glob/命令面],按授权「不可达则如实登记」处置,以 §七.3 证明链+操作者 CI 3.11 复跑补位(双解释器记录件入证据包 04 类);
- **③证据包重装**: `/tmp/p3-wp-c-evidence/IA-P3-WP-C-EVIDENCE.zip` v2 新定值(文件数/字节数/sha256 落 DELIVERY §六 续段行组与续段终笔提交信息);**原 zip 只读留痕**更名 `IA-P3-WP-C-EVIDENCE.b25542e.zip`(sha256=`1e84a4ff607b780d656fc27c3ba36b078854d3f9a8fe132cfec6a9ea7f063500` 等值不变,装配器 v2 前置断言;SHA256SUMS 同步旁置更名留痕);
- **④DELIVERY §六 定值行组随续段终笔更新**(R065/R068 口径: §六 区内纯追加,§一~§五+§七 零改动;笔D);
- **⑤根因-修复-复验三面**=本节+stdout 四段自述;
- 附: 负向敏感性三注入复验(模块变更后新鲜基线): 3 注入全红→复绿→sha256 零残留,终态 sha256=§七.5 登记笔C 值 [实取·negative_sensitivity.py 复跑];模块/测试续段笔C 工作树计数: `scripts/prediction_review.py` **651 行** sha256=`4397b6de7b2f15299e39f61a75f24f4ca928e4b515da170660a64765b5471d74`、`tests/test_p3_wp_c.py` **1346 行** sha256=`0acbaf984387d1a2636df9801440698c5120c73dae924e8973a05089a6baf173` [实取·wc -l/shasum]。

### §七.5 续段 git 纪律与取证

- 笔C(修复笔=模块+tests+本 §七;本笔)/笔D(续段终笔=DELIVERY §六 续段定值行组)两笔纯线性续进,BASE-P3C 后 5→7 笔,零 merge/amend/force;main 未触碰(续段开工 ls-remote 实取 main=BASE 全值一致;dev/p3-design-fix1 等值;dev/p3-impl-c=笔B 全值);
- LIVE 三面复取: grep(`R040|P3-WP-C|IA-P3-WP-C|prediction_review`) **0 命中** [实取·Grep 工具全目录扫描];LIVE `real_data_acceptance.py` sha256=`f9ca189c5248199bb5acbc78b2a2c82d59c10e1c7c2c2d20bdaaa6105fbfe3eb` 等值 [实取·shasum 只读];LaunchAgents 12 件 plist 清单+逐件 sha256 与 v1 取证一致,全部 mtime≤2026-11-03 早于开工,零改动零新增零删除 [实取·ls/shasum 只读];
- 零 tag;零网络(取证/推送类除外);终局单支推送 `dev/p3-impl-c` no-force,推送后 ls-remote 复核(57 支冻结表零漂移+main=BASE 全值);
- CI 复跑=操作者 CHECKPOINT 职能(执行席禁 dispatch,run ID 不可见如实声明);登记件 `rounds/040/P3-WP-C-CI-dispatch-evidence.md` 落字面值(run ID+headSha+conclusion+套件数)。

### §七.6 偏差登记增补(§三 历史节零回改,续段增补项在此登记)

9. **续段 CI 红(3.11 扩收差)与修复**: CI run 42409208175@b25542e 唯一红=as_of 紧凑形被 3.11 `fromisoformat` 扩收放行(根因 §七.1;run 事实=注入摘要);修复=§七.2 守卫(最小域恰 1 函数);复验=§七.4;测试零弱化(§七.3)=R067 审计 DEFERRED-4 预警的实化承接;
10. **双解释器交叉佐证面 3.10+ 执行席不可达**: 如实登记(§七.4②),以守卫纯字符串判定零版本依赖+新增用例 3.11 守御敏感面+操作者 CI 3.11 复跑补位——如实非 FAIL;
11. **无其他续段偏差声明不作出**: 以上为续段全量增补;其余沿 §三 1-7 项与 DELIVERY §七 1-8 项终态不变。
