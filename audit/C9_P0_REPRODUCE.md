# Charter 9 P0 四项独立复现报告 (C席)

- 复现人: C席(独立Agent, 只验不修) | 日期: 2026-11-11 | 对象: Charter8 交付物在 06bb65d 的工程实际
- 纪律: 隔离环境 `/tmp/c9v` = `git archive 06bb65d` + dev库 `data/` 全量; 独立期望值(全部数值自算或引擎重跑); 禁机械接受章程/审计结论——每项指控给出 CONFIRMED/REFUTED/PARTIAL + 可重放证据
- 解释器: LIVE venv `~/AI内容/venv/bin/python3`(只读); 页面默认快照=`research_snapshot_20261110_v5`(latest_snapshot 取当日最高修订, 与 app.py 实际行为一致)
- 章程指控原文要点(逐条对判): ①"主要通过指标1m/3m/1y变化与方向参数比较,不能证明机构对未来的预测正确" ②"未区分观点提出时证据/当前证据更新/到期预测验证三型" ③"可能用过去一年资产上涨证明未来一年预测"

## 总判定表

| 项 | 指控要点 | 判定 |
|---|---|---|
| P0-1 | verifier 不能证明未来预测正确/无三型区分/历史变动冒充预测验证 | **CONFIRMED**(机制级实证; 含1项缓解注记) |
| P0-2 | subject→metrics映射→上涨=支持的推理路径; key_assumptions未被消费 | **CONFIRMED**(路径为"半自动": 方向hint须人工传入; key_assumptions零消费实证) |
| P0-3 | qb_source无存在性校验/无原文一致性校验/统计不可复算/伪造QB静默显示; views lint不验URL/publish_date/quote真实性 | **PARTIAL**: 存在性与一致性=CONFIRMED(无代码管控); 统计可复算性=**REFUTED**(3/3边独立复算到4位小数); views侧=CONFIRMED(全伪造件0违规入页面) |
| P0-4 | 图表统计口径(单位/窗口/收益口径/缺失/日历) | **PARTIAL**: 窗口表=真日历口径✓缺失渲染✓日历✓; **历史走势图窗口切片=固定观测数, 月频序列"1年"实显21年=CONFIRMED缺陷**; 利率类caption单位不一致=CONFIRMED(轻) |

---

## P0-1 view_verifier 验证逻辑 — CONFIRMED

代码全读: `scripts/view_verifier.py`(253行) + `config/view_metric_map.json`。

**① 验证单元 = view 级(经 subjects 展开), 不是观点级/假设级。**
`verify()` L150-157: view → `doc['subjects']` → `metric_evidence_table` 把该 view 全部 subjects 的**所有**映射指标并入一张证据表。view 的 `core_views[]`(观点陈述文本)、`forecasts[]`、`key_assumptions[]`、`view_horizon` **全部不参与计算**(grep 全仓: verifier 不含这些字段的读取; 实证: VIEW-20261110-001 有 5 观点/4 预测/1 假设/6 主题 → 证据表 n_evidence=54, 与 5 条观点无任何绑定)。US_rates 一个 subject 即拉入 16 个指标。

**② 时间基准 = snapshot.target_date 锚定的 trailing 窗口; publish_date 零参与。**
`interval_table()` L118 以 `snapshot.get('target_date')` 为窗末; `horizon_start()` 自然月/年回退(20261110: 1m→10-10/3m→08-10/1y→2025-11-10, 测试锁定)。`publish_date` 仅在输出中 echo(L163), 不进任何计算。观点提出时点的证据状态、到期与否、预测窗与验证窗是否重叠——代码层无任何概念。**三型区分(提出时证据/当前更新/到期验证)在实现中不存在。**

**③ "历史已实现变动 → 预测验证"路径存在(机制级)。**
`_net_direction()` L72-84: 取可用窗中**最长者(1y>3m>1m)**的净变动符号; `directions` 传入时机械比对: 同号→`supports`。没有任何检查: 预测期限是否已到、验证窗是否与预测前瞻窗重叠、claim 是前瞻型还是事后陈述型。
*缓解注记(不翻转化论)*: 默认不传 `directions` → `relation=None`+note"方向提取属 Agent 层"; docstring 与 determinism_note 均声明"零 AI 判断、语义层归 Agent"。即模块自身不产出"预测正确"的断言文本——但 `supports/against/n_supports` 的输出形态在调用方极易被当作预测验证使用, 且无任何护栏阻止。

**④ 最小反例(可重放, 已实测):**
构造三份除 `publish_date` 与陈述文本外全同的合成观点(`US_rates` 主题, verbatim 预测"未来12个月UST上行"), 于 /tmp/c9v_sbx 运行 `vv.verify(..., directions={"UST_10Y":"up"})`:

| view | publish_date | 陈述型别 | 输出 |
|---|---|---|---|
| VIEW-20260915-001 | 2026-09-15 | 前瞻预测(2027-09-15到期) | relation=**supports**, 1y pp=+0.73, n_supports=1 |
| VIEW-20261109-001 | 2026-11-09 | 前瞻预测 | **逐字节相同输出** |
| VIEW-20260101-001 | 2026-01-01 | 事后陈述("已经大幅下行") | **逐字节相同输出** |

方法学解读: 输出"susports"实际证明的仅是"**截至 2026-11-10 的过去 12 个月 UST_10Y 净变动 +0.73pp**"(当前状态一致性, E2 类事实); 它**不证明** 2026-09-15 那条 12 个月预测的正确性(至验证日仅走完 6 周≈11% 期限), 更无法区分一条与其方向相反的事后陈述。注意 1m 窗实为 −0.40pp(下行)——"最长窗优先"规则本身即内嵌了一个未声明的语义选择。

## P0-2 主题级 vs 假设级 — CONFIRMED

- "subject→metrics"映射存在: `view_metric_map.json` 11 subjects→注册表指标。但"映射上涨→观点获支持"**不是全自动路径**: relation 仅在调用方显式传 `directions` 时计算(L16-19 docstring 明示"方向提取属 Agent 层"); 不传 → 全部 `relation=None`+note。全仓 grep: 无任何代码自动生成 directions(CLI 是唯一入口, `--directions` 手传)。
- **一旦传入 hint, 判定即"指标级机械比对→view 级聚合"**: 实证 VIEW-20261110-001(IMF) 任意传 `{"UST_10Y":"up","USDJPY":"down"}` → n_evidence=54, n_supports=1, n_against=1——支持/反对计数挂在 **view** 头上, 无法追溯到 5 条 core_views 中任何一条(哪条观点被支持?代码不可答)。
- **key_assumptions 在 verifier 中零消费**: grep 全仓, 消费者仅 `view_store.py`(lint 形状校验)、`app.py` 页③(展示)、tests。verifier 不读、不映射、不验证假设。CONFIRMED。
- 同理 `forecasts[]`(含 horizon!)与 `view_horizon` 也未被 verifier 消费——预测的期限字段就在数据里, 验证逻辑却不用它锚定窗口(与 P0-1② 同根)。

## P0-3 来源验证缺口 — PARTIAL

**edges 侧(qb_source)**:
- ① **存在性无代码验证: CONFIRMED**。`wd.transmission_edges()` L303-316 唯一校验=qb_source 为非空字符串。实测: 沙箱改 `qb_source="QB-20990101-999"`(不存在) → 装载成功零拦截, 页②"来源"列将照常显示该伪号。空串才 raise ValueError。
- ② **引用数据与归档原文一致性无代码验证: CONFIRMED(缺管控), 实测未发现违例**。抽验 11 项(TIPS×UST 0.8278/2495, SPX×HY −0.6318/749, DXY×GOLD −0.3935/2511, COREPCE×FF 0.422, NDX×RUT 0.7644, MF 2020-12簇/2022-01簇 等)全部在 QB-20261110-022/023 归档 answer_text 中逐字在场(注意归档用全角负号−, edges 文件用半角-, 数值一致)。**A席遵守了 provenance_rule, 但管控纯靠纪律, 代码零执行。**
- ③ **统计可复算性: REFUTED(可复算)**。用 `ia_cli compare --metrics` 独立重算 3 条边, **全部到 4 位小数精确复现**:
  - TIPS_10Y×UST_10Y 全窗: r=0.8278015585603504, n_change_pairs=2495 → 边档 0.8278/2495 ✓
  - SPX×HY_OAS 3yr(start 2023-11): r=−0.631829702238754, n=749 → −0.6318/749 ✓
  - DXY×GOLD_F 2016起: r=−0.3935285087147287, n=2511 → −0.3935/2511 ✓
  (即: 若章程指控"统计不可复算"→REFUTED; 若指控"无自动复算校验"→CONFIRMED——引擎具备复算能力, edges 装载链不调用。)
- ④ **不存在 QB → 静默显示: CONFIRMED**(见①实测)。

**views 侧(lint)**: `view_store.lint_view` L80-234 逐条核对——URL 仅查 `startswith('http')`(L136); publish_date 仅查 ISO 格式+≤fetch_date(L139-146); quote 仅查非空+≤500 字符(L177-193)。**实测**: 构造全伪造件(`https://nonexistent-domain-xyz123.example.org/...`+publish_date 不可对证+凭空 quote"This quote was never written by anyone.")→ **0 违规通过 lint, 进入页③机构矩阵**。CONFIRMED: lint=结构纪律(attribution/引文长度/日期格式), 真实性核验零代码(缓解: lint 设计即离线; 真实 11 份经 B席流程+C8审计核过 URL/原文, 但那是流程不是代码)。

## P0-4 图表统计口径 — PARTIAL

对象: app.py 五页(四内容页+关于) + workbench_data.py。手算复核 7 组页面实际数字。

**① 利率类单位: 窗口表正确 / 历史走势 caption 不一致。**
- 窗口表 `_fmt_interval`: rate→pp、price→%、count→abs, 与 interval_change 契约一致; HY_OAS 行 1m +0.31pp = 手算 3.42−3.11 ✓; UST_10Y 3m +0.19pp = 4.84−4.65 ✓(node 附 bp_change=19 与 formula 字符串)。
- **缺陷(轻)**: 页①历史走势 caption `_render_series` L139-145 对一切指标按 `(末-首)/|首|×100` 输出"区间变化 ±x.xx%"——UNEMPLOYMENT(4.7→4.1)显示"−12.77%"(水平的百分变化)而非 −0.6pp; 与窗口表的 pp 约定不一致, 易误读。
**② 窗口截取: 表=真日历 ✓ / 图=固定观测数缺陷 ✗。**
- 窗口表: `horizon_start` 自然月回退(月末钳制/闰年, 测试锁定), 基准=严格早于窗起点末观测——**月频 3m=日历 3 个月**(CORE_PCE 3m 实为 2026-08-01→2026-09-01 一个间隔, 10 月值未发布如实取 9 月末值)。章程若指"3m=3 观测或 90 天错配"→REFUTED。
- **缺陷: 历史走势图窗切片=固定观测数** `{'1年':252,'6个月':126,'3个月':63,'1个月':21}`(L130) 按日频设计, 月频序列全面错位: **SPX_CAPE(月频 n=1750)选"1年"实际显示 2005-11→2026-10 共 21 年**, caption"+56.99%"; UNEMPLOYMENT 选"1年"显示全部 119 个月≈10 年。仅日频序列(SPX 1年=2025-11-07→2026-11-09 ✓)正确。
**③ 价格/总回报口径: REFUTED(无错误)+披露建议。** 采集器显式 `auto_adjust=True`(global_market_collector L195, 注释"复权口径不变")——ETF 价格为复权基(近似总回报), 指数无分红影响; 口径在代码注释声明, 页面未标注, 建议页注。
**④ 缺失渲染: PASS。** 如实无填零: BUND_10Y/2Y 显示"缺失|来源文件在场而指标缺席(采集遗漏)"; HY_OAS 5y 显示"不可用(start(2021-11-10)之前无基准观测)"(3 年授权窗如实); EA_HICP 陈旧观测 2025-12-01 带 DEGRADED 标注。
**⑤ 交易日历: PASS(无独立模块但口径成立)。** 纯日期比较+basis 规则天然处理: SPX 1m 窗起点 2026-10-10(周六)→basis=10-09(周五)✓; SHCOMP 1m 跨国庆周→basis=2026-10-09(节后首个交易日)✓; 跨经济体相关用共同日交集。
**附加覆盖观察(移交D席)**: 页①"市场多窗口表"按 `MARKET_ASSET_CLASSES` 过滤, `rates_yield/policy_rate/curve_slope` 不在集合内——**UST_2Y/10Y、BUND、JGB、ECB 利率、2s10s 斜率在多窗口表零显示**(仅在 overview 周/月/年内与 verifier 可得)。"市场多窗口"页答不了"美债 3m 变化", 属覆盖缺口非数值错误。

**手算复核清单(7/7 中)**: SPX 1m −3.16%(算 −3.1558) / SHCOMP 1m −3.93%(−3.9349) / UST_10Y 3m +0.19pp(4.84−4.65) / CORE_PCE 3m +0.32%(+0.3165) / HY_OAS 1m +0.31pp(3.42−3.11) / UNEMPLOYMENT 图caption −12.77%(4.1/4.7−1=−12.766) / SPX 1y +12.43%(7565.03 vs 2025-11 末)。

---

## 修复轮输入建议(按危害排序)
1. **P0-1/P0-2(同根)**: verifier 引入 view_horizon/forecasts[].horizon 与 publish_date——预测型 claim 仅在验证日≥到期日才允许判 supports/against; 未到期一律"证据观察"不判对错; 三型(type=提出时/更新/到期验证)显式建模; n_supports 聚合下钻到观点级(需 core_view↔metric 绑定字段)。
2. **P0-3**: `transmission_edges()` 加 qb_source 存在性校验(list_query_records 集合比对, 不存在即 raise); 可选: r/n 复算对账(引擎已可复算, 本报告 3/3 实证)。views lint 保持离线, 但 `ia_cli views lint` 可加 `--verify-urls` 可选联网档位(默认关, 零网络纪律不破)。
3. **P0-4**: 历史走势图窗切片改按日历日期过滤(月频序列"1年"=12 个观测); `_render_series` caption 对 rate 族改 pp; 市场多窗口表考虑纳入 rates_yield/curve_slope(或页面注明覆盖边界)。

*复现工件(临时): /tmp/c9v(隔离环境) /tmp/c9v_sbx(伪造edges+合成views沙箱) /tmp/c9v_cmp1.json*
