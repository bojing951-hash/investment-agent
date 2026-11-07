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

### §零.9 实现期登记(实现笔回填)

(占位: 实现笔回填——交付物行数/sha256/用例分类/黄金值登记/实现期缺陷修复/负向敏感性注入/本地 CI 镜像/零运行产物锚定)

---

## §一 实现摘要

(占位: 报告笔回填)

## §二 AC-02 五要点逐条映射表(DESIGN L186①-⑤)

(占位: 报告笔回填)

## §三 如实偏差与登记承接

(占位: 报告笔回填)

## §四 DP 零回改自检表

(占位: 报告笔回填)

## §五 git 纪律自检(七项)

(占位: 报告笔回填)

## §六 数值标注自检(AC-04;逐项实取·来源)

(占位: 报告笔回填)
