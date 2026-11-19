# Charter 9 D席双盲审计与修复设计(P0四项+P3/P4工程面)

分支 dev/charter9-closeloop-v1 @ 06bb65d · 2026-11-11 · 工程负责人 D席
**双盲声明**: 本文档在未见 C席(verify-p0-c7)复现报告的情况下独立完成;
两者交叉一致处才动代码,冲突处标注留协调仲裁(§7)。全部结论基于源码
逐行阅读+真实数据抽样验证(10份views/148条QB档/边档25边),零网络零模型。

---

## 0. 审计范围与方法

| 审计面 | 文件 | 方法 |
|---|---|---|
| P0-1/2 | scripts/view_verifier.py(254行全读)/view_store.py(316行全读) | 逐函数读+真实views抽样(001 IMF/002 Fed/003 PIMCO) |
| P0-3 | research_archive.py 公开面(verify_query_record L537/verify_archive L555)/QB-022 sidecar 实测 | API能力盘点+sidecar实测 |
| P0-4 | scripts/workbench_data.py(608行全读)/app.py(322行全读)/research_history_query.interval_change/fact_engine.compute_period_returns | 逐函数口径核对 |
| C7复用件 | research_provenance.vintage_dates/snapshot_candidates/read_archived_source/analog_engine.realtime_gate_text | 确认可复用原语 |

**现状一 sentence 诊断**: Charter8 交付的验证器是"单时点证据表"(最新快照
×subjects映射指标×区间变动),**没有时间三段概念、没有假设级链条、没有
来源核实引擎、渲染层口径有一处频率盲区**——四项P0全部成立,非误报。

---

## 1. P0-1 view_verifier 三型验证重建设计

### 1.1 现状缺陷(源码定位)
- `verify()`(view_verifier.py L150-175)只用**一个**快照(最新或--snapshot-id),
  无 publish_date 感知: IMF 10-13 发布的观点与 11-10 的最新快照证据同表混排,
  发布前历史/发布后新信息**未分离**——违反时间三段纪律。
- 无到期概念: forecasts[].horizon 是自由文本(实测: 'CY2026'/'当前(会后即刻)'
  /'未指明'/'6-12个月'),verifier 完全不碰 forecasts。
- `--directions` 机制健康(显式传入才机械判 supports/against),保留。

### 1.2 设计: 三段模式(CLI 兼容扩展,现有 17 断言套件不动)

```
python3 scripts/view_verifier.py VIEW-ID                 # 现行为不变(latest证据表)
python3 scripts/view_verifier.py VIEW-ID --mode A        # 段A 观点提出时证据
python3 scripts/view_verifier.py VIEW-ID --mode B        # 段B 发布后新信息
python3 scripts/view_verifier.py VIEW-ID --mode C        # 段C 到期预测验证
python3 scripts/view_verifier.py VIEW-ID --mode all      # 三段合表(时间轴不混)
```

**段A(观点提出时证据)**——数据 vintage 切到 publish_date:
1. vintage 判定(复用C7判据,**同一权威零新实现**): `rp.vintage_dates(daily_dir)`
   取跨日 vintage 基础日期集(同日 _vN 不算,现成函数);选 `max{v ≤ publish_date}`;
   存在→`rp.select_snapshot(v)` 得时点快照 → 证据表计算与现路径同构
   (metric_evidence_table 换 snapshot 入参即可,纯函数已支持)。
2. vintage 缺席(观点发布在两次引擎运行之间,常态)→ **采集档降级路径**:
   metric_series 取序列后按 `observation_date ≤ publish_date` 过滤(序列元素
   自带 dates),快照 facts 层不可用时同档过滤;输出显式标注
   `vintage_gate: 'degraded_collector_filter'`+realtime_gate_text 同款文案
   (现存跨日vintage列表+「非时点重构,发布日信息集为近似」),**不冒充时点**。
3. 窗口: interval_change(start=publish_date−k, end=publish_date)。

**段B(发布后新信息)**: 现役最新序列,`interval_change(start=publish_date,
end=today)`,仅取**严格晚于 publish_date** 的观测为"新信息";输出独立表,
不与段A同表混排;无 directions 时依旧零语义判断。

**段C(到期预测验证)**——只碰 forecasts[]:
1. horizon 解析(确定性解析器,解析失败=显式类别不猜):
   - 相对: '3m/6m/12m/18m' → publish_date + N月;
   - 绝对: 'CY2026'/'2026'/'2026-12' → 对应年末/月末;
   - 区间: '6-12个月' → **取上界为到期日**(披露"区间预测按上界判到期");
   - 不可机械解析: '当前'/'未指明' → `UNPARSEABLE_HORIZON`(非错误,如实)。
2. `horizon_end ≥ today` → 整条 `NOT_YET_TESTABLE`(未到期不比实际)。
3. target→指标映射: 新 `config/forecast_target_map.json`(Agent 层维护,
   ai_inferred 标注;确定性消费),如 global_real_GDP_growth_2026→US_REAL_GDP。
4. 值比对(只做机械可算的): value_or_direction 数值可解析(±X%/区间/点位)
   → 与 horizon_end 前(≤horizon_end)最后观测比偏差 pp/pct;方向型(看涨/
   回落)→ (publish_date, horizon_end] 区间变动符号;不可解析 →
   `NOT_MACHINE_VERIFIABLE`。**偏差数值+口径给全,"未预见因素"列举归
   Agent 层**(确定性边界)。
5. 输出 per-forecast: {target, horizon_raw, horizon_end, status, expected,
   actual{value,date,metric_id}, deviation, notes}。

**rc**: 0=有输出 / 1=view或数据错 / 2=用法错(与现契约一致)。
**测试**: test_c9_verifier_modes.py——合成快照对(publish 前后各一)+合成view,
断言段A用旧快照/段B用新序列/段C三态(未到期/到期偏差/不可解析);真实档
抽样断言(本地在场时)。边界: 段A含 publish_date 当日观测(≤含,待仲裁§7)。

---

## 2. P0-2 假设级验证链设计

### 2.1 现状缺陷
- key_assumptions 只有 {statement, attribution}(schema v1.1 L204-214 lint 只验
  形状)——**无经济变量→可观察指标链**,验证器完全不消费 assumptions。
- subject→metrics(view_metric_map.json 11主题,实测每主题3-21指标)是主题级
  粗映射,PIMCO 案例单 view 9 主题=60+指标铺开,信息密度低——按章程应降级为
  "指标发现"辅助(保留,不删)。

### 2.2 设计: 验证计划 sidecar + 六标签
1. **不动 views schema**(单一版本纪律 v1.1 刚仲裁,不升 1.2):
   新增 `data/institutions/verification/VP-{VIEW-ID}.json`(Agent 起草,attribution
   恒 ai_inferred;追加式,不覆写):
   ```json
   {"view_id": "VIEW-20261110-003", "planned_at": "...",
    "assumptions": [
      {"ref": "key_assumptions[1]", "statement_digest": "能源价格随时间回落...",
       "metric_refs": [{"metric_id": "WTI_F", "direction": "down", "segment": "B"}],
       "horizon": "6m"}]}
   ```
   每条 assumption→N 个 metric_refs(经济变量→可观察指标的显式落地);
   segment 指用段A/B/C 哪段时间证据。
2. **六标签机械映射表**(测试锁定,零 AI):
   - 全部 metric_refs 有数据且方向全符 → SUPPORTED
   - 有符有不足(无反) → PARTIALLY_SUPPORTED
   - 有符有反 → MIXED
   - 全反 → CONTRADICTED
   - 数据全不足(available=False/NOT_MACHINE_VERIFIABLE) → INSUFFICIENT_EVIDENCE
   - horizon 未到期 / 段C NOT_YET_TESTABLE → NOT_YET_TESTABLE
   (direction 缺省的 metric_ref 只报数值不投票——attribution 纪律: 方向是
   Agent 的主张,verifier 只机械比对。)
3. CLI: `view_verifier.py VIEW-ID --plan [VP路径]`(缺省自动找同目录
   VP-{VIEW-ID}.json;无 plan→报"无验证计划"非猜)。
4. 渲染: 页3详情每条 assumption 后随标签徽章(§5-P3-1 同一笔改)。
5. 测试: 六标签各一合成例+边界(混合 insufficient+against→按表取 MIXED?
   **否——有反即入 MIXED/CONTRADICTED 族,表内优先级待仲裁§7**)。

---

## 3. P0-3 source_verifier.py 设计(新脚本)

### 3.1 现状缺陷
- edges qb_source 只有"装载时非空校验"(workbench_data.transmission_edges L303-316
  raise 缺 qb_source)+测试里"指向在册归档"子集校验——**运行时无核验引擎**,
  归档被移动/误删/誊录漂移时渲染层照画。
- 无机构观点来源核实;无合成档案隔离纪律(测试 fixture 与生产档案同构,
  仅靠 tmpdir 位置区分——渲染层无防线)。

### 3.2 设计: 离线优先的状态机
```
python3 scripts/source_verifier.py --edges            # 核 config/transmission_edges.json
python3 scripts/source_verifier.py --views [ID|all]   # 核 views 来源一致性
python3 scripts/source_verifier.py --qb QB-ID --recompute  # 深度统计复算(可选重)
[--online]   # URL 活性(默认关,零网络纪律)
```
输出单 JSON: {ok, target, checks: [...], summary: {VERIFIED: n, PARTIAL: n,
MISSING: n, CONFLICTED: n}};rc 0/1/2 同库内约定。

**① qb_source 核验(状态机,全部复用现成 API)**:
- 存在: `ra.load_query_record(qb)` 缺→MISSING;
- 身份/版本: `ra.parse_snapshot_id(record.snapshot_id)`+`ra.load_snapshot_by_id`
  (快照档缺→PARTIAL+"记录在快照档不在");
- 引用一致: `ra.verify_query_record(record, snapshot_dir)`(L537 现成,digest
  R5 绑定校验)不过→CONFLICTED;
- 统计复算: `ra.load_research_full(qb).answer_text` 逐字含边表 r/n 行
  (QB-022 实测: 边表 r 值以表格行 '| VIX×SPX | −0.7138 | 2512 |' 形式逐字
  在档,C8测试已锁四处,推广到全部25边)——誊录漂移即 CONFLICTED;
  `--recompute` 才真跑相关性重算(compare 同路径,重: 默认关)。
- **合成档案禁冒充**: ①路径核验: 归档必须位于引擎 `DEFAULT_ARCHIVE_DIR`
  之下(tmpdir/外部路径→SYNTHETIC_EXCLUDED 不消费);②标记纪律: 约定
  fixture 档 question_text 前缀 `SYNTH:`(fixt_c8_archive.py 落实),verifier
  见前缀即剔除——双防线,渲染层只认 VERIFIED/PARTIAL。

**② 机构观点核验(离线部分)**: URL 格式/publish_date≤fetch_date(lint 已有,
交叉复验)/revisions[].date ≤ publish_date(新检查,lint 未覆盖)/quote 与
source_url 配对在档。**URL 活性**: 仅 --online: urllib HEAD/GET 8s 超时,
记录 status/重定向;离线运行该字段恒 'offline_not_attempted'(默认,零网络
纪律优先,待仲裁§7)。

**③ 渲染消费**: `wd.transmission_edges(verify=True)`(缺省 False,性能+零网络)
逐边附 `verification_status`;app 页2 MISSING/CONFLICTED 边降级显示
(徽标+置灰行,不删边——"来源未验证"本身是信息);页3 详情同款徽标。
状态缓存: 快照日+边档 sha256 为键的内存级缓存(进程内,不落盘新状态文件)。

测试: test_c9_source_verifier.py——合成归档四状态各一例+SYNTH 剔除+真实档
抽样(本地在场);与 C8 edges 套件正向衔接(fixture 轨道即天然测试素材)。

---

## 4. P0-4 口径审计(app.py/workbench_data.py 逐函数)

### 4.1 发现清单(按严重度)

| # | 位置 | 问题 | 级别 | 处置 |
|---|---|---|---|---|
| 1 | app.py L130 `_render_series` 窗口切片 | **频率盲区**: 窗口=观测点数(1260/252/126/63/21)按日频假设;月频序列(SPX_CAPE/宏观月度)"1年"切 252 点=21年 | **P0** | 改日期截取: cutoff=今日−窗口,dates≥cutoff(用序列真日期,零频率假设) |
| 2 | app.py L138-145 历史走势首末% | (末−首)/abs(首) 无单位族判断,利率序列也显示"+x.xx%"(水平百分比,非 pp) | P1 | 族感知: rate→pp,price→pct(app 已可经 registry 判族) |
| 3 | workbench_data L196-217 metric_window_changes | 口径正确(interval_change 自配对,common window);月频 1m 窗常 available=False 如实 | ✓ | 仅补文档caption |
| 4 | workbench_data L179-193 horizon_start | 自然月/自然年回退正确;2/29→2/28 处理;跨年窗口正确(2027-03-01−1y=2026-03-01) | ✓ | 边界测试锁定 |
| 5 | rhq.interval_change L276-316 | ISO 字符串比较=字典序=时序,正确;基准严格<start 文档化;利率 pp 负水平安全;**价格 pct 仅护 base==0,负基数的 pct 语义反转无护** | P2 | 边界测试+护栏(v0<0→available=False+原因,价格类负水平=数据异常如实拒算) |
| 6 | fact_engine.compute_period_returns(L81起) | week=ISO周前末观测/mtd=前一自然月末/ytd=**前一自然年末**(非当年首日)——语义正确但页面文案"年初至今"未披露基准口径 | P2 | app 页1 caption 补一句 |
| 7 | workbench_data L347-375 research_archive_rows | 截断≤81/最新在前/读取失败行如实 | ✓ | C8套件已锁 |
| 8 | workbench_data L271-300 economy_dimension_matrix | 在场/活跃如实,不放大 | ✓ | 已锁 |
| 9 | workbench_data L80-95 fmt_value | 千位分隔/4位小数/None→缺失,负值安全 | ✓ | — |
| 10 | view_verifier L65-69 | 薄委托 wd.metric_window_changes,口径单一实现 | ✓ | 三段扩展不改此层 |

### 4.2 边界测试清单(test_c9_oral_accounting_edges.py,新增)
1. 月频序列(SPX_CAPE 型)图表"1年"窗口 → 日期截取后≈12点(修复#1回归锁)
2. 跨年窗口: target=1月15日,1y 窗基准落上年12月末观测
3. 单月缺测: 月频序列挖空一月 → interval_change 不插值,如实 available/窗内首可用
4. 利率负值: DFR −0.5→−0.4 era,pp=+0.10 正确;pct 路径不可达
5. 价格负基数: base<0 → 拒算+原因(修复#5)
6. 2/29 闰年: 1y 窗 2024-02-29→2023-02-28
7. 段A/B 切点: observation=publish_date 当日 → 属段A(≤含);次日属段B
8. horizon 解析: CY2026/6-12个月/未指明 三态
9. ytd 基准披露: 1月2日观测的 ytd 基准=上年12月31日(非1月1日)

---

## 5. P3/P4 工程面盘点

**P3-1 页3 mechanism_steps+evidence_cited 未展示——已定位**:
app.py page_views() L235-258 详情块渲染 core_views/forecasts/key_assumptions/
risk_factors/falsification_conditions/revisions,**从未读 doc['mechanism_steps']
与 doc['evidence_cited']**(数据在档且过 lint——schema TOP_REQUIRED 含这两键,
纯渲染遗漏非数据缺失)。修: 详情块加"机制链条(编号步骤)"与"引用证据"两节
+views_matrix rows 加两列计数。工作量最小,建议随 P0-2 标签渲染同一笔改。

**P3-2 页2 传导网络可探索化**: 现 st.dataframe 静态表(L173-184)。设计:
行选择(streamlit≥1.35 selection events,workbench 钉 1.49 ✓)→ 右侧详情面板:
机制 note+qb_source 徽标(P0-3 状态)+跳页4读 QB 全文(view_id/qb 联动
session_state)。零新依赖。近零渠道同款。可选远期: graphviz 布局图
(新依赖,**不建议本章程**,登记 P4 台账)。

**P3-3 页4 十问结构**: 现 page_research 是扁平 QB 列表。设计:
`config/research_questions.json`(十条常设研究问题=工作台自身研究议程,每条
{qid, question, metric_bundle, archive_tags});页4 按"十问"分组: 每问展示
最新 QB 链(问题→验证状态→结论摘要)+该问可执行命令。**问题清单内容需
用户/章程给定**(工程只做结构与渲染,待仲裁§7)。

**P4-1 ia_cli 一键 research 编排**: 新子命令 `ia_cli research-map`:
确定性扇出——十问各自跑既有能力(overview/changes/compare/research)产
**确定性中间产物 JSON**(envelope: {ok, capability, products:[{qid, question,
command, product_json}]},零模型零合成判断);十三步编排/综合叙述留 Skill 层
(Agent 拿中间产物自己编排——章程边界: CLI 给确定性,Agent 给判断)。
复用 build_parser/cmd_* 现有骨架,rc 纪律同库内。

**P4-2 Web"生成研究地图"入口**: 页1 顶部按钮"刷新数据(运行采集)"
(subprocess run_weekly,st.expander 流式日志;失败如实)——仅本地环境;
页4 顶部面板"生成研究地图": 无 Agent 环境显示=①一键刷数据+②展示已有研究
(边档/views/档案现状)③**可执行 Agent 命令清单**(research-map 十问命令
复制即用)——零模型纪律不动(页面永不调模型)。

---

## 6. 工时排序(建议实施顺序)

| 序 | 项 | 估时 | 依赖 |
|---|---|---|---|
| 1 | P0-4 修复#1(日期截取)+边界套件 | 0.5d | 无 |
| 2 | P0-3 source_verifier.py 核心+页2消费 | 1d | 无 |
| 3 | P0-1 三段模式(A降级路径最难) | 1.5d | C7原语(现成) |
| 4 | P0-2 VP sidecar+六标签 | 1d | P0-1段机制 |
| 5 | P3-1 页3补渲染(+P0-2标签) | 0.25d | P0-2 |
| 6 | P3-2 页2探索化 | 0.5d | P0-3状态 |
| 7 | P3-3 页4十问 | 0.5d | 清单仲裁 |
| 8 | P4-1 ia_cli research-map | 1d | 十问清单 |
| 9 | P4-2 Web入口 | 0.5d | P4-1 |

合计≈6.75d;P0 合计 3d。113/120 基线: 全部为**新增文件+兼容扩展**,现有
断言零弱化(C8 verifier 17断言保持默认行为不变;新增走 --mode/--plan)。

---

## 7. 交叉与仲裁点(等C席报告比对;此处列D席独立立场)

1. **段A是否含 publish_date 当日观测**: D席立场 ≤(含)——发布日盘中/收盘前
   公开的数据属"提出时可知";C席若立场 <(不含)则留仲裁。
2. **区间型 horizon('6-12个月')到期判定**: D席=上界;替代=不可验。
3. **URL 活性默认**: D席=默认离线(零网络纪律优先,--online 显式开);
   若C席复现环境要求默认开则仲裁。
4. **六标签优先级**: insufficient+against 混合 → D席表=有反即 MIXED 族
   (CONTRADICTED 仅全反);PARTIALLY 仅无反时可用。
5. **页4十问清单内容**: 工程只做结构,清单需用户给定。
6. **VP sidecar vs views schema v1.2**: D席=sidecar(不动 v1.1 单一版本纪律)。
7. **D席自查风险点**: 段A采集档降级路径的 observation_date 过滤,对
   "采集当时真实信息集"仍是近似(档内序列可能含发布后才回填的历史修订)
   ——已用 degraded 标注+gate 文案如实,不冒充时点重构;此近似边界是否
   达标请 C席数据面复现重点核。

—— D席 2026-11-11,等C席复现报告到后交叉比对,一致即按§6顺序动代码。
