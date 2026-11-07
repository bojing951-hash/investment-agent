# IA-P3-WP-D REPORT — P3 收尾层第 4 实现包(报告质量评价循环)

> 包: IA-P3-WP-D(P3 族第 4 实现包,#36 挂靠;依赖列前件=WP-P3-C) · 执行Agent: Agent 3 · 分支: `dev/p3-impl-d`
> 基线: BASE-P3D=`aeb39e8d5937525afac4076061b9fede0c973fda`(origin/main,开工 ls-remote 实取全值一致)
> 合同: IA-P3-WP-D-AC-v1.0(冻结,附录A 内嵌注入)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY/上游在场件行号一律为**本包基线工作树实读**行号(2026-11-07T20:5x-21:1xZ 实取,基线=BASE-P3D 工作树);提示词注入内容引用一律标注「注入摘要,非工作树实读」。
> 数值标注边界: 本文所有计数类/统计类数值逐个二选一标注 `[实取·来源: …]` 或 `[示意·非实取]`;日期/SHA/结构编号(WP-P3-D/#31-38/P3-G-05 等)/档键成分(ID 格式字符串,如 `SUG-01`)按合同边界出圈登记。

---

## §零 规格抄录与交付面登记(开工首步,AC-01;登记后即本合同白名单实体)

### §零.1 DESIGN §7 WP-P3-D 行四要素逐字抄录

实读 `docs/P3_DESIGN.md`(基线工作树在场,blob `5acc130a88d9635a1e82d7ad3beb4f1dbe008106`,§零.7 核验与 7f43724 侧等值),WP-P3-D 行位于 L188-L192,逐字抄录:

```text
L188: **WP-P3-D 报告质量评价循环**(挂靠编号: **#36**)
L189: - 目标: 落地 §6.1 评价维度 5 项 [实取·§6.1 枚举,2026-11-03] 统计与质量简报/校准建议清单。
L190: - 范围: 旁路统计件(月度/季度节奏)+简报渲染;**不含提示词自动注入**(注入须用户确认,DP-8)。
L191: - 依赖: WP-P3-C(预测质量维度);层序前置(同上)。
L192: - 验收要点草案: ①周报系统主流程零改动断言(report_generator/data_validator diff 为空)②评价维度集与阈值(DP-7)**先登记后运行、禁回改**负向测试 ③统计取数经正式产物(发布状态认定)断言 ④CI 零回归。
```

四要素齐备(目标 L189/范围 L190/依赖 L191/验收要点 L192 共 4 条),无缺失。核验:
- **D 行可区分性**: 与 A/B/C/E/F 行四要素逐项可区分(A=档案检索与结论版本管理 L170-174/B=新证据关联与持续跟踪聚合 L176-180/C=预测复盘与错误模式统计 L182-186[同族前列件行]/E=个人流程整合接口 L194-198/F=终验+总封版 L200-208;D 行题名「报告质量评价循环」与挂靠 #36、旁路统计件[月度/季度节奏]+简报渲染范围要素、DP-7/DP-8 所指均为他行所无)→ 合同附录A §零(iv)冲突处置首项不触发;冻结章 §十一 注记行号 L188-192 与本实读一致(偏差 0 行,≤3 行容差内);
- **依赖列核验**: 「WP-P3-C(预测质量维度)」=同族前包 R040+续段 整体 PASS 已合入 main(冻结章 §十一 生效前置达成登记,注入摘要,非工作树实读;其终笔尖端 57eb3a3 已 merge 入 BASE-P3D=aeb39e8,父=c14931c+57eb3a3 [实取·git log --format='%H %P' -1 aeb39e8 工作树实取]),交付件在本基线工作树在场(`scripts/prediction_review.py`+`tests/test_p3_wp_c.py`+`docs/P3_WP_C_REPORT.md`+`docs/P3_WP_C_DELIVERY.md` [实取·本工作树 git ls-files 清点=4 件,与 WP-C REPORT §零.2 登记清单一致]);「预测质量维度」=本包 D3 维度消费入口(P-D-07,复用调用 prd.review_statistics);「层序前置(同上)」=§7 L168 层序排程依赖声明(冻结章 §十一 登记逐层核验 ✓,注入摘要,非工作树实读);依赖列与 BASE-P3D(`aeb39e8…`)无矛盾、**不要求并入其他支**(本包无并入步,纯线性)✓;
- **范围列无真实 GLM 调用/网络出站/付费凭证要求**: 范围列 L190 零 GLM/网络/凭证/付费字样,且明文**不含提示词自动注入**(注入须用户确认,DP-8=确认权留用户,本包零实现零自决);旁路统计件+简报渲染均为确定性结构;所引 §6.1 L149 优化循环明文「建议经用户确认后才注入提示词(DP-8,确认权留用户)」→ 无情形(d)停止条件。

### §零.2 交付文件清单(k=4 [实取·本节清点],登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据(推导逐条附) |
|---|---|---|
| 1 | `scripts/report_quality_review.py` | DESIGN L190 范围列两件(旁路统计件[月度/季度节奏]+简报渲染)=**恰 1 个代码模块**: WP 题名「报告质量评价循环」(L188)单一工作包,两件共享五维评价集/正式产物取数面/月度季度窗口与同一质量文档载体(§6.1 L142-147 维度集+L149 循环=统计→简报→建议清单同环,同一批正式周报流经两件;L192②「评价维度集与阈值」单点登记=同模块参数面)+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」;文件名=域词 report(周报)+quality(质量)+review(评价循环,WP 行题名「报告质量评价循环」用词),避开既有 `report_generator.py`(周报主流程件,本包禁触)与 `prediction_review.py`(WP-C)(ls scripts/ 实读,命名不冲突 [实取·开工 grep -ri report_quality scripts/ tests/ docs/=0 命中]) |
| 2 | `tests/test_p3_wp_d.py` | DESIGN L192①②③④工件「断言/负向测试」+合同附录A §零(ii)「含代码则必含 tests/test_p3_wp_d.py」 |
| 3 | `docs/P3_WP_D_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P3_WP_D_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L192④「CI 零回归」证据落点=DELIVERY |

### §零.3 结构约束核验(2026-11-07T20:5xZ 实取)

- 与 `git ls-files` 零重合: 4 路径 `git ls-files scripts/report_quality_review.py tests/test_p3_wp_d.py docs/P3_WP_D_REPORT.md docs/P3_WP_D_DELIVERY.md` 输出=0 行 [实取·开工 git ls-files]→ 纯新增 ✓;
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p3_wp_d.py)✓;
- 推导无越界: 范围列恰 1 个代码模块(§零.2 行 1 依据,同族前列件 WP-A/WP-B/WP-C 单模块先例 P-A-01/P-B-01/P-C-01 同构)→ scripts/ 恰 1 文件;未引入 DESIGN 依据外文件 ✓。

### §零.4 DP 登记(开工首步登记定值;DESIGN 决策点登记表 L226-L241 实读,DP 共 10 个 [实取·表清点],D 行内所引=DP-7[登记型]/DP-8[确认型])

| DP | 分类(DESIGN 实读) | 本包登记定值(登记即实现值,先登记后运行,禁回改) | 依据 |
|---|---|---|---|
| DP-7 报告质量评价维度集与阈值 | 登记型(L236) | **维度集 5 项全启**(§6.1 L142-147 逐字: ①数值质量②覆盖度③预测质量④时效⑤论证完整度)+**阈值首期登记定值**(下表 P-D-10;DESIGN L236「阈值可依首期统计再修订一次(修订=新登记记录,禁静默回改)」——本登记=首期登记,运行后禁回改) | L236+L142-147+L192② |
| DP-8 质量校准建议注入提示词的执行权 | 确认权留用户(L237) | **本包零实现零自决**: D 行范围列 L190 明文「**不含提示词自动注入**(注入须用户确认,DP-8)」——本包交付=校准建议清单(数据结构+旁路渲染,建议条目携 requires_user_confirmation=true 标记),零注入零提示词触碰零回写;注入步=用户实批 PENDING 面,本包任何成员不使其生效 | L237+L190+L149 |
| DP-1/DP-2/DP-3/DP-5/DP-6 | 登记型(L230-232/L234-235) | **上游已登记定值**(DP-1/2/3=WP-P3-A、DP-5/6=WP-P3-C;本包只读复用其载体面与常量,不重新登记不改写;WP-A REPORT §零.4/WP-C REPORT §零.4 登记在案)——DP-5/6 经 prd.review_statistics 复用承载(其窗口/分母口径=上游登记值,本包零重算零改写) | L230-235 |
| DP-4/DP-9/DP-10 | 确认权留用户(L233/L238/L239) | **本包零触及**: DP-4=§4.1 关联第三层(WP-P3-B 面)、DP-9=§6.2 接口(WP-P3-E 面)、DP-10=终验观察窗(WP-P3-F 面)——均非 D 行范围列(L190)所及,本包无 GLM/费用/个人流程/LIVE 面 | L233/L238-239 |

DP 编号/数量/分类与 DESIGN 实读一致: 行内所引 DP-7(L192② 明文)登记型已登记定值,DP-8(L190 明文)确认型零自决实施(范围列明文排除注入=合同授权面);确认型(DP-4/8/9/10)未被自决实施(§零.1 核验: 范围列零触及面);登记型 DP-1/2/3/5/6 上游登记面只读复用。

### §零.5 实现参数登记(P-D-01..P-D-20,先登记后实现,运行后禁回改)

| # | 参数 | 登记定值 | 依据 |
|---|---|---|---|
| P-D-01 | 模块载体 | `scripts/report_quality_review.py` 恰 1 文件(旁路统计件[月度/季度节奏]+简报渲染两组件同模块,§零.2 行 1) | DESIGN L190+§零.2 |
| P-D-02 | 窗口语义(月度/季度节奏) | `window_kind ∈ ("monthly","quarterly")`;monthly→窗口=[as_of 所在月首日, as_of] 闭区间;quarterly→窗口=[as_of 所在季度首日, as_of] 闭区间(月末日钳制由日历构造自带;as_of 居中=部分期如实呈现);报告入窗判据=该报告 target_date(ymd)∈窗口;**节奏对齐**=monthly_review.py/quarterly_outlook.py 在场制度(月度/季度节奏 [实取·monthly_review.py L31-33/quarterly_outlook.py L29-31 在场锚;DESIGN L149「月度/季度节奏对齐 monthly_review.py/quarterly_outlook.py 在场制度」]),**仅节奏对齐非取数路径对齐**(该两件为快照纪律前旧制直读件,本包取数面=P-D-03 禁 data/daily);D3 预测质量窗口=WP-C DP-5 滚动 12 个月(prd 自带窗口,本包零重开窗,质量文档双窗并记 prediction_window);window_kind 非法→ValueError fail-loud | DESIGN L190+L149+§6.1 |
| P-D-03 | 取数面(要点③: 统计取数经正式产物) | 周报面唯一取数入口=`rp.scan_formal_weekly_reports(output_dir)` 复用调用(research_provenance L1520-1529;发布状态认定链=规范文件名 L1425+FORMAL_REPORT_EXCLUDES L1423-1424+published=True+final_quality∈FORMAL_FINAL_QUALITIES L1426+身份字段一致+digest 实算一致,任一不满足即拒 L1456-1517)——候选/未验证/未发布/digest 失配件一律不入统计;周报文本=正式产物本体只读读取(md 文件即 L1517 view['path']);预测质量面=`prd.review_statistics(views_data, as_of, version_records)` 复用调用(WP-C 公共 API;views_data=门禁后状态文件 config/allocation_views.json 形直载 [DESIGN §3.1 L71 快照纪律输入清单第三类「门禁后状态文件(thesis/allocation_views)」],只读);core 集=调用方注入 core_metric_ids 或 registry_path 读取(config/metric_registry.json,配置源非数据档,快照纪律不禁);**快照纪律守卫见 P-D-04** | 要点③+DESIGN §3.1 L69-73+§8.1 L216+rp L1423-1529 |
| P-D-04 | 快照纪律路径守卫 | `_reject_raw_data_path(path)`: 路径规范化(os.path.normpath)后组件序列含 `data`+`daily` 相邻组件(以 os.path.join("data","daily") 形拼装比对,**源码零 data/daily 连续字面量**,AST 禁字符串测试面见 §二)→ValueError fail-loud;适用 weekly_output_dir/views_path/registry_path/version_archive_dir 四输入面(AC-07.1 禁直读原始采集档;经正式产物/状态文件/配置转递不在此限) | AC-07.1+DESIGN §3.1 L72 |
| P-D-05 | 维度①数值质量 | 对窗内正式报告 status 逐份统计: gate_b 分布(PASS/DEGRADED/FAIL 计数;正式集内 gate_b 实取域={PASS,DEGRADED},FAIL 不可能已发布,词表按 rp.GATES 三值承载)、gate_a 分布、final_quality 分布;gate_b_pass_rate=count(gate_b==PASS)÷n;degraded_rate=count(gate_b==DEGRADED)÷n;n=0→两率 None 如实缺席(不填 0) | DESIGN L143+dv L372-377 分级 |
| P-D-06 | 维度②覆盖度 | core 集=criticality=="core" 且 status=="active" 的 metric_id 集(调用方注入或 registry_path 读取;当前工作树 config/metric_registry.json v2.3.0: metrics 102 条,core 32 条全 active [实取·json 清点 2026-11-07;DESIGN L144「core 32 项」=INVENTORY c.1 L112 2026-11-03 时点 81 条/core 32——registry 演进后 core 计数仍 32,实取复核一致]);引用判定=词边界正则 `(?<![A-Za-z0-9_])`+re.escape(metric_id)+`(?![A-Za-z0-9_])` 命中报告全文(锚点形 macro.data.ID.value 中 ID 两侧为非字母数字下划线→命中;FXC1 不误命中 FXC10);per-report coverage=命中 core 数÷core 总数;mean_coverage=窗内报告 coverage 算术平均;core 集 0 项→ValueError fail-loud(覆盖度不可计算);报告文本空→coverage=0 如实(0÷|core|) | DESIGN L144+INVENTORY c.1 L112 |
| P-D-07 | 维度③预测质量 | `prd.review_statistics(views_data, as_of, version_records)` 返回文档的 counts 节(hit/miss/inconclusive/not_yet_triggered_terminal/hit_rate)与 error_patterns/correct_samples/premise_class **原样承载**(零重算零改写零重开窗;hit_rate 分母口径=DP-6(a) 上游登记);本维度计量行={counts 原样+hit_rate};views_data 缺 predictions→由 prd 抛 ValueError fail-loud(上游行为原样) | DESIGN L145「承接 §5.2」+依赖列 L191 |
| P-D-08 | 维度④时效 | on-time 判定=该报告 status.generated_at(rg L799 发布事务落档时间戳)日期段[:10]==target_date(发布事务同日落档=按时;DESIGN L146「按时发布率(发布事务载体 L909-924)」——候选→校验→发布事务 L909-921+L1491-1519 同日完成为按时口径);on_time_rate=count(on-time)÷n;n=0→None 如实缺席;generated_at 缺席/不可解析→该报告记 late_generated_at_missing 如实单列(late 计数内,不 fail: 正式认定已过,时间戳缺席=历史档形态) | DESIGN L146+rg L909-921/L1491-1519/L799 |
| P-D-09 | 维度⑤论证完整度 | 解析面=`ae._parse_status_block(text, tag)` 复用调用(L1117-1134,THESIS_STATUS+ALLOCATION_STATUS 两块;块缺席→该报告零行如实计入,不报错不造数);星级分布=两块行级 `confidence`(1-5 整数)直方图(论点行+观点行合并;DESIGN L147「证据分级星级分布」——报告行 confidence 受 rg L505/L523 确信度门禁约束[不得超过程序验证星级],正式产物内行级 confidence 即星级可观测面;重算程序星级需锚点验证面=越取数边界且复制引擎逻辑,禁);confidence 非 1-5 整数→ValueError fail-loud(词表非法);mean_confidence=全部行算术平均(0 行→None);unexplained_contrary_events=两块 evidence 数组中 `contrary==True`(严格布尔)且 `explained!=True` 的项数合计(rg L521「存在未解释反证时封顶3★」规则触发面的正式产物可观测计数) | DESIGN L147+rg L518-521+ae L1117-1134 |
| P-D-10 | 阈值定值(DP-7 阈值半) | `THRESHOLDS={numeric_quality.gate_b_pass_rate_min:0.90, coverage.mean_core_coverage_min:0.80, prediction_quality.hit_rate_min:0.30, timeliness.on_time_rate_min:0.90, argument_completeness.unexplained_contrary_attention_threshold:2}`(ATTENTION 当: gate_b_pass_rate<0.90 ∥ mean_coverage<0.80 ∥ hit_rate<0.30 ∥ on_time_rate<0.90 ∥ unexplained_contrary_events≥2);状态词表 `DIMENSION_STATUS=("OK","ATTENTION","NO_DATA")`(NO_DATA=计量值 None[分母 0/输入缺席],不填 0 不硬判);维度键词表 `DIMENSION_KEYS=("argument_completeness","coverage","numeric_quality","prediction_quality","timeliness")`(字典序,attention_dimensions/suggestions 序=此序) | DP-7+DESIGN L142-147 |
| P-D-11 | 质量简报渲染 | `render_quality_briefing(doc)` 纯文本: 标题行+窗口行(含 window_kind 与 prediction_window 双窗)+五维行(维度中文标签+计量+阈值+状态)+ATTENTION 清单行+免责尾行「本简报为报告质量评价循环面输出(旁路统计,零注入零回写,校准建议注入须用户确认[DP-8]);不构成投资建议(禁交易/禁仓位/禁收益承诺)」;None 计量渲染「N/A(分母=0,如实缺席)」;纯函数零写入零注入 | DESIGN L149+§8.3 L218 |
| P-D-12 | 校准建议清单 | `build_suggestions(doc, hypothesis_warnings)`: ATTENTION 维度→建议条目;WP-C 警示(prd.hypothesis_warnings 产出)非空→追加「证据校准段权重复核」建议条目(DESIGN L149「校准建议清单(如提示词证据段权重调整建议)」);条目 schema={suggestion_id("SUG-"+两位序号),dimension,trigger,proposal,requires_user_confirmation:true,dp8:"确认权留用户"};proposal 文本模板按维度登记(numeric→「数据包/锚点数值质量呈现复核建议」/coverage→「数据包核心指标呈现完整性复核建议」/prediction→「预测假设生成与证据权重校准复核建议」/timeliness→「发布事务排程复核建议」/argument→「证据段权重与反证解释要求复核建议」/warnings→「{N}条机制类别连续miss警示:证据校准段权重复核建议」);**零自动执行**: requires_user_confirmation 恒 true,注入步=用户实批 PENDING(DP-8 零自决) | DESIGN L149+L190+DP-8 |
| P-D-13 | 统计文档 schema 与确定性序列化 | `{schema_version:1, note:<免责声明>, as_of, window_kind, window_start, window_end, prediction_window:{start,end}, reports:[ymd 升序], dimensions:{五维各{…计量/阈值/状态}}, attention_dimensions:[DIMENSION_KEYS 序], suggestions:[P-D-12 序]}`;全部 dict 键=字符串(零 None 键);序列化=`json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=1)`(家族先例 P-A-03/P-C-08 同款) | AC-03 确定性 |
| P-D-14 | 只读零写入纪律(要点①) | 模块**零文件写入面**(全源码零写模式 open/零 os.replace/零 json.dump 落盘/零临时文件/零 shutil);输入件(周报 md/status json/registry/views/版本档)只读;断言面=测试字节级 sha256 前后等值(周报系统主流程件 scripts/report_generator.py+scripts/data_validator.py+全部输入件)+AST 零写调用;**周报系统主流程零改动**=report_generator/data_validator diff 为空(白名单 M=0 结构性保障+测试面双保险) | 要点①+DESIGN §6.1 L151 边界声明 |
| P-D-15 | 上游复用面(对齐=复用调用,禁复制分叉) | rp: `scan_formal_weekly_reports`/`formal_report_view`(经 scan 间接)/`weekly_report_files`(经 scan 间接)/`GATES`/`FORMAL_FINAL_QUALITIES`(常量锚);ae: `_parse_status_block`(状态块解析,读侧复用);prd: `review_statistics`/`classify_predictions`/`hypothesis_warnings`/`window_bounds`(D3 承载);零 rg/dv/monthly_review/quarterly_outlook/snapshot_builder 直接依赖(本包无发布面/无主流程面;monthly/quarterly 仅节奏对齐 P-D-02);零本地重实现(测试断言模块调用面=上游对象同一性) | AC-05.5+依赖列 L191 |
| P-D-16 | 纯度与免责 | import 面白名单={json,os,re,sys,datetime+项目既有 research_provenance,allocation_engine,prediction_review}(纯标准库+项目既有依赖);AST 零网络 import(urllib/requests/http/socket/httpx 禁);零凭证/密钥/token;免责三处=模块 docstring+统计文档 note+简报尾行,词面携「报告质量评价循环面输出,不构成投资建议(禁交易/禁仓位/禁收益承诺)」(§8.3 红线承接) | AC-05.4+AC-07.3+§8.3 |
| P-D-17 | as_of 注入纪律 | 一切日期依赖纯函数(window_bounds/report_text_statistics/evaluate_dimensions 等)显式 as_of 必填(测试恒显式注入,零墙钟);as_of 须规范 YYYY-MM-DD(规范形守卫仿 P-C 先例: 十位带杠形才入 fromisoformat,紧凑形/周形拒绝——R040 续段教训承接,3.9/3.11 行为一致);唯一墙钟缺省=便利编排面 `report_quality_review(..., as_of=None,…)` 边缘(测试恒显式) | AC-03 确定性纪律+R040 续段先例 |
| P-D-18 | 他包范围排除 | WP-P3-E/F 任何范围零实现零引用;提示词自动注入(DP-8)零实现(建议清单=数据结构+旁路渲染,requires_user_confirmation 恒 true);WP-P3-A/B/C 面只读复用零改写;W4/W5 侧边验收工具零接入(AC-07.6);report_generator/data_validator/发布事务/主流水线零触碰(要点①,白名单 M=0 结构性保障);版本链写入面(WP-A)零触碰(经 prd 只读消费) | AC-08.1+要点①+P-D-15 |
| P-D-19 | DP/参数哨兵 | `registered_dp_values()`+`registered_param_values()`(活性常量)+`dp_selfcheck()`(活性常量 vs 模块内登记镜像逐值对照,回改任一定值→AssertionError;另含维度键词表/状态词表/阈值全值/窗口词表一致性断言);`__main__` 自检入口零写入零默认路径 | DP 纪律+WP-A/B/C 先例 |
| P-D-20 | 零运行产物判定 | D 行验收要点 4 条(L192①-④)全为测试面/CI 面(①③=断言,②=负向测试,④=CI 工件;范围列 L190 零「真实运行/端到端/编排入口要求」措辞,对照 A 行 L174/B 行 L180/C 行 L186 同构判定先例=WP-C P-C-16 经 R040+续段审计 PASS 先例)→ **本包登记「零运行产物」**,`data/research/` 零写入(统计/简报/建议全落函数返回值与测试临时沙箱);`.gitignore` 不改 | 合同§零 运行产物边界+要点对照 |

### §零.6 前置实读登记(file:line;基线工作树 2026-11-07T20:5x-21:1xZ 实取)

- DESIGN 相关节(工作树在场件,=7f43724 侧 blob 等值,§零.7): §3.1 快照纪律 L69-73(禁直读 data/daily L72)/§6.1 报告质量持续优化 L140-151(维度 5 项 L142-147/优化循环 L149/边界声明 L151)/§6.2 L153-162(DP-9 面,零触及)/§7 层序声明+WP-P3-D 行 L166-210(D 行 L188-192)/§8 红线 L214-222(快照纪律 L216/LIVE 禁写 L217/禁建议 L218/批量修改 L219/append-only L220/GLM 凭证 L221/如实 L222)/决策点登记表 L226-241(DP-7 L236/DP-8 L237);
- 上游在场件(只读禁改,对齐=复用调用):
  - `scripts/research_provenance.py`: GATES L66/digest_file L1331/FORMAL_REPORT_EXCLUDES L1423-1424/_WEEKLY_REPORT_RE L1425/FORMAL_FINAL_QUALITIES L1426/weekly_report_files L1429-1441/read_report_status L1444-1453/formal_report_view L1456-1517(发布状态认定链)/scan_formal_weekly_reports L1520-1529/combine_gates L1560-1570;
  - `scripts/report_generator.py`(周报主流程件,本包禁改,引用面): OUTPUT_DIR L36/论点状态词表 L501/证据分级 v2 校验块 L518-521(星级门槛与未解释反证封顶 L521)/裁决词表 L534/候选→发布事务 save_candidate_report L909-921/save_report L924-935/_status_body L777-800(generated_at L799)/write_report_status L803+/发布主流程 L1423-1519;
  - `scripts/data_validator.py`(校验分级件,本包禁改,引用面): 校验分级注释 L372-377(PASS/DEGRADED/FAIL 三级)/classify_result L378+;
  - `scripts/allocation_engine.py`: _parse_status_block L1117-1134(状态块解析复用面)/update_allocation_status L1199(回写面,本包禁触只作语义锚);
  - `scripts/prediction_review.py`(WP-P3-C,依赖列前件交付件): DP5/DP6 常量 L49-53/window_bounds L147-151/dp_selfcheck L174-198/review_statistics L505-512/hypothesis_warnings L544-571/prediction_review_report L622-635;
  - `scripts/monthly_review.py` L31-33 与 `scripts/quarterly_outlook.py` L29-31/quarter_months L39-42(在场制度节奏锚,仅节奏对齐);
  - `config/metric_registry.json`(v2.3.0): metrics 102 条/criticality core 32 条全 active [实取·json 清点 2026-11-07];
  - 同族前列件 REPORT: `docs/P3_WP_A_REPORT.md` §零.2 登记清单(k=4 [实取·L30-37 实读])、`docs/P3_WP_B_REPORT.md` §零.2 登记清单(k=4 [实取·L30-37 实读])、`docs/P3_WP_C_REPORT.md` §零.2 登记清单(k=4)+§零.5 P-C-01..16+§零.6 L79-89 [实读];
  - `docs/P3_INVENTORY.md` c.1 L112(registry 时点登记: 2026-11-03 时 81 条/core 32;当前 102 条/core 32,演进注记见 P-D-06)。

### §零.7 开工核验(2026-11-07T20:50-21:1xZ 实取)

- 步骤0: `git status` clean(开工时在 dev/p3-impl-c@57eb3a3,工作树干净,非本包所致脏=无);UTC 开工时刻 2026-11-07T20:50:16Z;
- 步骤1: 合同三占位符均实值化(BASE-P3D=aeb39e8d5937525afac4076061b9fede0c973fda 全值/BASE-P3D-CI-SUITES=85/BRANCH-SET=58 支全表 §十一.1 内嵌),无未解析标记 ✓;生效前置信号=冻结章 §十一 生效前置达成登记(WP-P3-C R040+续段 PASS+层序闭合,注入摘要,非工作树实读)✓;
- 步骤2: `git ls-remote origin main dev/p3-design-fix1 dev/p3-impl-a dev/p3-impl-b dev/p3-impl-c` 实取: main=`aeb39e8d5937525afac4076061b9fede0c973fda`(=BASE-P3D 全值一致 ✓)/dev/p3-design-fix1=`7f43724661b50e011394e643cdd8c223c0b27a90`(全值一致 ✓,未锚 f93adb5)/dev/p3-impl-a=`202a09d2570f2894acff05fb8fe1a4dbe7c26a79`(一致 ✓)/dev/p3-impl-b=`e21789a72b83c765b8fc54264372951db53abcfa`(一致 ✓)/dev/p3-impl-c=`57eb3a3742628f9643b9e23e1a78862234d6c7bd`(一致 ✓);全量 ls-remote 64 行=1 HEAD+58 支 heads+5 行 tag(4 tag 含 1 peel 行) [实取·/tmp/p3-wp-d-lsremote-pre.txt],dev/p3-impl-d 零命中(无预创建违规 ✓);冻结表对照注记见 §三 偏差登记(2 支休眠历史支疑似单字符差异,如实登记非静默);
- 步骤3: `git checkout -b dev/p3-impl-d aeb39e8d…` 自基线全值切出(非自当前 HEAD 盲切)✓;
- 步骤4(设计在场核验,本包无并入步): ①`git merge-base --is-ancestor 7f43724661b50e011394e643cdd8c223c0b27a90 HEAD`→exit 0 可达(经祖先在场,冻结章 §十一 路径甲注记一致)✓;②设计三件 `git ls-tree` 双侧(HEAD vs 7f43724)blob 逐一相同: P3_INVENTORY=9f366da5a9e327e524ae1a17eec229722cd85d5f/P3_DESIGN=5acc130a88d9635a1e82d7ad3beb4f1dbe008106/P3_DELIVERY=ac8965ce0e09a964f5b493ebe1ef7dcacfca9b2d ✓;
- CI 基线: `ls tests/test_*.py` 计数=85 [实取·开工清点]=BASE-P3D-CI-SUITES 85 槽口径一致(84 exit0+1 SKIP,冻结章 §十一 CI 基线实值依据;分支 run 预期=85+本包新增 tests 文件数 1=86);本地 Python 3.9.6(CI=3.11),实现保持 3.9 兼容语法(WP-A/B/C 同款约束;日期解析规范形守卫仿 P-C 先例,R040 续段教训承接)。

### §零.8 AC-03.7(GLM 桩边界)适用判定

登记清单(§零.2)无 GLM/LLM 能力级调用面实现文件(范围列 L190 零 GLM 字样;模块=旁路统计件+简报渲染确定性结构;DP-8 注入面=范围列明文排除,零实现)→ **AC-03.7 不适用**,判定依据=清单无调用面类文件(§零.2 表 1-4 无客户端封装/调用编排/适配器类)。

### §零.9 实现期登记(实现笔回填)

(待实现笔回填)

---

## §一 实现摘要

(报告笔回填)

## §二 D-AC-02 验收要点逐条证据映射表

(报告笔回填)

## §三 如实偏差登记

(报告笔回填)

## §四 DP 零回改自检表

(报告笔回填)

## §五 git 纪律七项自检

(报告笔回填)

## §六 数值标注自检清单

(报告笔回填)
