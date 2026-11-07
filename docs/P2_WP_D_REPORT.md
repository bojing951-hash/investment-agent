# IA-P2-WP-D REPORT — P2 深研层第 4 实现包·族末(事件序列数据面)

> 包: IA-P2-WP-D(P2 族末实现包) · 执行Agent: Agent 3 · 分支: `dev/p2-impl-d`
> 基线: BASE-P2D=`e557fd3a6598b0145c9c40cee07299a992ad56bb`(origin/main,开工 ls-remote 实取全值一致)
> 合同: IA-P2-WP-D-AC-v1.0(冻结,附录A 内嵌注入)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY/上游在场件行号一律为**本包基线工作树实读**行号(2026-11-07T09:4xZ 实取);提示词注入内容引用一律标注「注入摘要,非工作树实读」。
> 数值标注边界: 本文所有计数类/统计类数值逐个二选一标注 `[实取·来源: …]` 或 `[示意·非实取]`;日期/SHA/结构编号(WP-P2-D/P2-G-04 等)/档键成分(ID 格式字符串)按合同边界出圈登记;来源白名单 URL 字符串=登记型参数(登记值,本包零访问零网络,P-D-04)。

---

## §零 规格抄录与交付面登记(开工首步,AC-01;登记后即本合同白名单实体)

### §零.1 DESIGN §七 WP-P2-D 行四要素逐字抄录

实读 `docs/P2_DESIGN.md`(基线工作树在场,blob `63a1964812f0c081aef0ea38148dec82537c7416`,§零.7 核验与 f8ed401 侧等值),WP-P2-D 行位于 L211-L215,逐字抄录:

```text
L211: **WP-P2-D 事件序列数据面(独立小包)**
L212: - 目标: 消除 P2-G-04: 议息/发布事件结构化日历(最小集: FOMC 议息日+本注册表高频引用指标发布日 [示意·非实取,范围最小集提案])。
L213: - 范围: 免费公开日历源直用(循预授权③,DP-5(a))+事件档格式+快照挂载;付费源须报批(确认权留用户)。
L214: - 依赖: 无硬依赖(可与 A/B 并行);事件窗计算消费方在 WP-P2-B。
L215: - 验收要点草案: ①事件档 schema 与来源登记(免费源 URL 白名单登记制)②事件窗对齐计算单测(事件前后窗口取数经快照)③零凭证零付费断言 ④CI 零回归。
```

四要素齐备(目标 L212/范围 L213/依赖 L214/验收要点 L215 共 4 条),无缺失。核验:
- **D 行可区分性**: 与 A/B/C 行四要素逐项可区分(A=任务与假设登记器 L193-197/B=矩阵装配与轮次引擎 L199-203/C=跟踪触发与 GLM 对接 L205-209/D=事件序列数据面 L211-215,题名与四要素内容均不同构)→ 合同附录A §零(iv)冲突处置首项不触发;
- **依赖列核验**: 「无硬依赖(可与 A/B 并行)」与 BASE-P2D 无矛盾、不要求并入他支(本包路径甲无并入步,§零.7);「事件窗计算消费方在 WP-P2-B」=消费方注记(WP-P2-B 已 PASS,其范围列明文「事件日历(D3)另包」实读 `docs/P2_WP_B_REPORT.md` §零.1 L201 抄录行,本包=该缺口 P2-G-04 的承接方;对齐=本包提供可独立调用的确定性窗计算函数,不改 WP-P2-B 在场件);
- **范围列无真实 GLM 调用/网络出站/付费凭证要求**: 「免费公开日历源直用(循预授权③,DP-5(a))」=数据源政策面(免费公开+登记制),本包实现手段=确定性结构(档格式+来源白名单登记+快照挂载+窗对齐计算),合同 AC-07.4 零网络出站绝对边界下零真实抓取零访问(真实抓取属预授权③运行面,由操作者另行排程,注入摘要,非工作树实读)→ 无情形(d)停止条件。

### §零.2 交付文件清单(k=4 [实取·本节清点],登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据(推导逐条附) |
|---|---|---|
| 1 | `scripts/deep_research_event_calendar.py` | DESIGN L213「事件档格式+快照挂载」+L212「议息/发布事件结构化日历」=恰 1 个代码模块(事件档+来源白名单+快照挂载+事件窗对齐计算同模块,WP 题名「事件序列数据面(独立小包)」L211 单数)+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」;文件名沿族先例 `deep_research_registrar.py`/`deep_research_matrix_engine.py`/`deep_research_tracking_engine.py`(ls scripts/ 实取 3 件在场)+本包域词 event_calendar |
| 2 | `tests/test_p2_wp_d.py` | DESIGN L215①②③工件「单测/断言」+合同附录A §零(ii)「含代码则必含 tests/test_p2_wp_d.py」 |
| 3 | `docs/P2_WP_D_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P2_WP_D_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L215④「CI 零回归」证据落点=DELIVERY |

### §零.3 结构约束核验

- 与 `git ls-files` 零重合: 4 路径 `git ls-files <4路径>` 输出=0 行 [实取·开工 2026-11-07T09:47Z]→ 纯新增 ✓
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p2_wp_d.py)✓
- 推导无越界: 范围列恰 1 个代码模块 → scripts/ 恰 1 文件;DESIGN L215 工件未另指定模块文件名,依固定推导规则命名;未引入 DESIGN 依据外文件 ✓

### §零.4 DP 登记(开工首步登记定值;DESIGN §2.4 DP 表 L63-L72 实读,6 DP 四要素齐备 [实取·表清点])

| DP | 分类(DESIGN 实读) | 本包处置 | 依据 |
|---|---|---|---|
| DP-1 深研轮次预算 | 登记型(L65) | **本包不触及**(事件日历无轮次概念);沿用族级定值=WP-P2-A 登记(双轨 N=5+提前终止,`docs/P2_WP_A_REPORT.md` §零.4 L49 实读),本包零引用零改写 | L65 |
| DP-2 证据权重量表 | 登记型(L66) | **本包不触及**(窗观测产出原始事实绑定记录,不赋权;赋权属证据矩阵消费方 WP-P2-B);沿用族级定值=WP-P2-A 登记(星级 [1,5],同上 L50 实读) | L66 |
| DP-6 区分性判据最低数 | 登记型(L70) | **本包不触及**(无假设判据面);沿用族级定值=WP-P2-A 登记(每对 ≥1,同上 L51 实读) | L70 |
| DP-3 ID 族 | 对齐型(L67,非登记型清单成员) | 本包新记录族前缀 **`CAL-`**(日历事件;`CAL-{YYYYMMDD}-{sha256[:8]}` 确定性指纹,详见 P-D-02)——避开上游已占前缀 [实取·scripts 实读: `deep_research_registrar.py` L63 EV-+L72 附近 RT-DR-/HP-/FC-、`deep_research_matrix_engine.py` L69-70 EVI-/RD-、`deep_research_tracking_engine.py` TRG-/CON-/DSP-];DESIGN L67「本设计不冻结 ID 格式」明示,本登记=结构性先例非冻结格式 | L67 |
| DP-4 GLM 角色 | 确认权留用户(L68) | **本包不触及**(范围 L213 无 GLM 字样,本包无 GLM 面) | L68 |
| DP-5 外部源扩展 | 确认权留用户(L69) | **范围列明文触及=DP-5(a) 免费公开源直用(循预授权③)**: 本包处置=**白名单登记制**(P-D-04,登记免费公开官方源 URL 常量,登记不访问,零网络零凭证零付费);**(b) 付费源零实施零登记**(确认权留用户,合同冻结章 §五 PENDING 留痕: 「付费日历源=确认权留用户」,注入摘要,非工作树实读)。本包不发生任何真实源访问——DP-5(a) 的「直用」运行面(真实抓取)不在本包授权范围(AC-07.4 零网络出站绝对禁令),本包交付=其确定性结构与登记面 | L69+L213 |

DP 编号/数量与 DESIGN 实读一致(6 个 [实取·DESIGN §2.4 表清点]);DP-4/DP-5(b 付费面)未被自决实施;DP-5(a) 按 DESIGN 范围列明文+合同冻结章登记处置执行(白名单登记制,零访问),非执行Agent自决。

### §零.5 实现参数登记(P-D-01..P-D-13,先登记后实现,运行后禁回改)

| # | 参数 | 登记定值 | 依据 |
|---|---|---|---|
| P-D-01 | 档案载体与集合 | 挂共享档案族根(复用 drr:`ARCHIVE_FAMILY`=drr 同名常量、`DEFAULT_ARCHIVE_DIR`=drr 同名常量);新集合 `calendar_events`(不占用 WP-A 既有 4 集合名 [实取·drr L46-L51 集合常量清点: deep_research_tasks/hypotheses/conditions/events]与 WP-B 2 集合 [实取·matrix L62-63]与 WP-C 集合) | DESIGN L213「事件档格式」+族先例 |
| P-D-02 | 事件 ID 族 | `CAL-{YYYYMMDD}-{sha256[:8]}`;指纹件={source_id, event_type, event_date, metric_id, note};经 drr._hash8(canonical JSON sha256 前 8 位,L106-107 实读);ymd 取自 created_at 日期段;不含墙钟内容→重放幂等;前缀避占清单见 §零.4 DP-3 行 | DP-3+族先例(EVI- 同款 L86-95,ID 前缀族 L60-63) |
| P-D-03 | 事件类型词表 | `("FOMC_RATE_DECISION", "INDICATOR_RELEASE")` 恰 2 类(DESIGN L212 最小集: FOMC 议息日+指标发布日) | DESIGN L212 |
| P-D-04 | 免费源 URL 白名单(登记制,登记不访问) | 恰 3 源,每源五要素 {source_id, publisher, url, access:"free_public", credentials:"none", cost:"none"}: ①`SRC_FED`/Federal Reserve Board/`https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`(支持 FOMC_RATE_DECISION)②`SRC_BLS_CPI`/U.S. Bureau of Labor Statistics/`https://www.bls.gov/schedule/news_release/cpi.htm`(支持 INDICATOR_RELEASE)③`SRC_BLS_EMPSIT`/U.S. Bureau of Labor Statistics/`https://www.bls.gov/schedule/news_release/empsit.htm`(支持 INDICATOR_RELEASE)。URL=官方机构公开日历/发布计划页的登记值;**本包全生存期零访问**(零网络出站,AC-07.4);事件档 source_id 必须∈白名单且 source_url 须与该源登记 URL 逐字相等 | DESIGN L213「免费公开日历源直用(循预授权③,DP-5(a))」+L215①「免费源 URL 白名单登记制」 |
| P-D-05 | 最小集指标绑定 | `INDICATOR_RELEASE` 的 metric_id ∈ {CPI, CORE_CPI, NFP, NFP_MOM_K} 且必须经 fe.metric() 在 registry 在场(fact_engine.py L75-76 实读);`FOMC_RATE_DECISION` 的 metric_id ∈ {None, DFEDTARU, DFEDTARL}(议息决定目标区间,DFEDTARU/L 为 registry 在场日频通道)。最小集选取依据=主流水线高频引用计数 [实取·2026-11-07T09:5xZ 脚本统计 8 模块(report_generator/macro_scorecard/allocation_engine/correlation_calculator/market_regime/macro_dashboard/daily_prediction_observer/fact_engine)词边界计数: CPI=8/CORE_CPI=4/NFP=3/DFEDTARU=3/DFEDTARL=3/NFP_MOM_K=2/CORE_PCE=1/FED_FUNDS=0,取发布日类引用 ≥2 者;CORE_PCE=1/FED_FUNDS=0 不入最小集,schema 开放扩展];DESIGN L212 明标最小集提案 [示意·非实取]→本登记定值即实现值 | DESIGN L212+DP-5(a) |
| P-D-06 | 事件窗口径 | pre 窗=[event_date−pre_days, event_date−1] 自然日闭区间(**不含事件日**);post 窗=[event_date, event_date+post_days] 自然日闭区间(**含事件日**);两窗结构性不重叠;观测归属按 observation_date 落点判 side∈{"pre","post"};默认 `WINDOW_PRE_DEFAULT=5`/`WINDOW_POST_DEFAULT=5` 自然日(约一周);入参 pre_days/post_days 须为 int ≥0;post_days=0→post 窗=[event_date,event_date](仅事件日) | DESIGN L215②「事件前后窗口」+口径登记制 |
| P-D-07 | 快照三重纪律(挂载与窗计算共用) | 一切窗取数经快照: ①drr._load_snapshot_for_verify 按 snapshot_id 规范分解加载(L778-796 实读,结构性不可达 data/daily)②rp.digest_snapshot 内容重算绑定(L1324-1328 实读,禁采声明值)③rp.gate_allows_formal_research 放行核验(L1210-1213 实读);Gate A=FAIL → fail-closed 拒收(DESIGN §3.1 L80「Gate A=FAIL 的快照不得作为深研正式证据来源」) | DESIGN §3.1 L80+WP-B 六重接地先例(matrix L277-287) |
| P-D-08 | 窗内观测质量纪律 | 观测来源=快照 facts 该 metric_id 的条目(携 fact_id/value/observation_date/quality_status);quality_status=="FAIL"→排除出数值观测、如实入 excluded_fail 清单(不填 0);value 非数值(str/bool)→排除+入 excluded_non_numeric;窗内零合格观测→`{"available": False, "status": "DATA_INSUFFICIENT"}`(数据不足如实缺席,禁硬判) | DESIGN §八 L228+fact_engine 不填 0 纪律(DESIGN L80 引)+WP-B 质量排除先例(matrix L310-312) |
| P-D-09 | 挂载上下文(读侧,不落档) | `mount_event_context(events, snapshot_id, snapshot_dir, *, pre_days, post_days, as_of=None)` → 三重纪律(P-D-07)过闸后产出 {snapshot_id, digest_snapshot, gate_a_status, event_ids:[窗口与快照日期面相交的事件 id 升序], as_of, window:{pre_days,post_days}, note:不构成投资建议声明};as_of 给定时事件 event_date>as_of 的未来事件如实排除(future_excluded 清单);挂载为纯计算面零写入 | DESIGN L213「快照挂载」+D4 挂载先例(DESIGN §3.2 D4 行 L89「经快照/数据包挂载消费」) |
| P-D-10 | 零网络零凭证纯度 | 模块 import 面白名单={json,os,sys,datetime,deep_research_registrar,research_provenance,fact_engine}(纯标准库+项目既有依赖);AST 零网络 import(urllib/requests/http/socket/httpx 等禁);零 os.environ 读取;零凭证/密钥/token 字面;测试静态断言 | AC-05.4+AC-07.4 |
| P-D-11 | registry 解析面 | metric 在场校验经 fe.metric()(fact_engine.py L75-76 在场接口);本模块零 registry 文件直读零 JSON 解析复制 | 复用调用禁复制分叉(AC-05.5) |
| P-D-12 | 事件档 append-only | 落档经 drr._write_records(预检零存在→原子落盘;同 id 重放→STATUS_REJECTED_DUPLICATE 拒,L513-524 实读)+drr._record_path(L527-528);读取 list_calendar_events 档内逐条重校验 fail-loud | 族先例(WP-A 写入原语/WP-B L346-347 同款) |
| P-D-13 | 免责与边界文案 | 模块 docstring+挂载 note 携「研究结构面输出,不构成投资建议」;零交易/仓位/收益承诺字样 | DESIGN §八 L225 红线 |

### §零.6 前置实读登记(file:line;基线工作树 2026-11-07T09:4x-09:5xZ)

- DESIGN 相关节: §2.4 DP 表 L63-L72 / §3.1 快照纪律 L80 / §3.2 数据需求 D3 行 L88(事件序列=需新源循预授权③)/ §七 D 行 L211-L215 / §八 红线 L221-L228;
- INVENTORY: P2-G-04 行 L163(「事件序列结构化日历零在场(议息/发布日)」,本包消除对象);
- 上游在场件(只读禁改,对齐=复用调用):
  - `scripts/deep_research_registrar.py`(WP-A): ARCHIVE_FAMILY/集合常量/ID 前缀族 L45-L63、_canonical L102-103、_hash8 L106-107、_now_iso L110-111、_ymd_of L114-115、_collection_dir L118-119、_write_records L513-524、_record_path L527-528、_load_snapshot_for_verify L778-L796;
  - `scripts/research_provenance.py`(R5/R3): digest_snapshot L1324-1328、gate_allows_formal_research L1210-1213;
  - `scripts/fact_engine.py`: metric L75-76(config/metric_registry.json 经 fe 在场接口);
  - `scripts/deep_research_matrix_engine.py`(WP-B,消费方注记对应件): 事实接地+质量排除先例 L277-L312、集合命名先例 L62-63、ID 前缀先例 L69-70;其 REPORT §零.1 L201 抄录行「事件日历(D3)另包」(消费边界登记);
  - `tests/test_p2_wp_c.py`(WP-C): 合成快照 fixture 形态先例 L74-L116(facts 列表+gate_a.status+quality_status 字段约定);
- 高频引用计数脚本与输出: §零.5 P-D-05 行内登记(8 模块词边界计数,2026-11-07T09:5xZ 实跑)。

### §零.7 开工核验(2026-11-07T09:44-09:50Z 实取)

- 步骤0: `git status` clean(开工时在 dev/p2-impl-c@858af49,工作树干净,非本包所致脏=无);
- 步骤1: 合同三占位符均实值化(BASE-P2D=e557fd3a…ad56bb / BASE-P2D-CI-SUITES=81 / BRANCH-SET=54 支全表),无未解析标记;
- 步骤2: `git ls-remote origin main`=e557fd3a6598b0145c9c40cee07299a992ad56bb 全值一致 ✓;`git ls-remote --heads origin` 计数=54 ✓ 且 dev/p2-impl-d 零命中(无预创建违规)✓;`git ls-remote origin dev/p2-design`=f8ed401f4274e158c06a9404149d41260e5cc0ad(前 7 位=f8ed401)✓;
  - **BRANCH-SET 零漂移对照方法登记(如实)**: 冻结章 §三.1 全表经人工重打为 /tmp 对照件后与 ls-remote 机器 diff 出现 7 行 SHA 尾部字符差异;经独立机器记录链裁定=R036 证据包 `/tmp/p2-wp-c-evidence/07-git-forensics/ls-remote-heads-postpush.txt`(R036 终笔推送后 54 支机器转储,在场实取)与本次 ls-remote 机器 diff 差异集=恰 2 支且均为登记内预期前移(dev/p2-impl-c 3a96af0→858af49=R036 终笔提交推送[该证据包 07 目录装配于终笔前,REPORT 已登记该口径]/main f064884→e557fd3=R036 #25 merge 入 main),其余 52 支全值一致零漂移→**7 行差异全部归因于本席人工重打转录失真,远端零漂移成立**。教训承接: 长 SHA 表对照以机器转储链为准(合同步骤2 引 R033/R035/R036 引擎层观察),本包事件如实登记于此;
- 步骤3: `git checkout -b dev/p2-impl-d e557fd3a…`(自基线全值切出;本地对象库缺基线对象→先行 `git fetch origin main` 只读取回,f064884..e557fd3)✓;
- 步骤4: `git merge-base --is-ancestor f8ed401f4274e158c06a9404149d41260e5cc0ad HEAD`=exit 0 可达 ✓;设计三件 `git ls-tree` 双侧(HEAD vs f8ed401)blob 逐一相同: INVENTORY c83c3938269ffb7192da9e7810bb052885cd9bb5 / DESIGN 63a1964812f0c081aef0ea38148dec82537c7416 / DELIVERY ac80196fd06d28019e8c5e63f86a63ab94429f99,与合同冻结章 §三 登记三值一致 ✓;
- CI 基线: tests/test_*.py 计数=81 [实取·ls 计数 2026-11-07T09:5xZ]=80 进 CI+1 test_glm_live SKIP,与 BASE-P2D-CI-SUITES=81 槽口径一致;本地 Python 3.9.6(CI=3.11),实现保持 3.9 兼容语法。

### §零.8 零运行产物判定(要点对照)

DESIGN L215 验收要点 4 条: ①schema 与来源登记=确定性结构+测试 ②窗对齐计算**单测**(经快照=合成 fixture 快照,非真实 data/daily 档)③零凭证零付费断言=静态断言 ④CI 零回归=CI 面。四条均无真实运行/编排入口要求(对照 WP-P2-B 行 L203④「DEV 授权数据副本端到端(数据档引用 data/daily/*_20261102.json)」明文真实运行面,D 行 L215 无对应措辞)→ **本包登记「零运行产物」**,data/research/ 零写入;.gitignore 不改。

### §零.9 AC-03.7(GLM 桩边界)适用判定

登记清单(§零.2)无 GLM 能力级调用面实现文件(范围列 L213 无 GLM 字样;模块为事件档+挂载+窗计算确定性结构)→ **AC-03.7 不适用**,判定依据=清单无调用面类文件(§零.2 表 1-4 无客户端封装/调用编排/适配器类)。

### §零.10 实现期登记(实现笔回填)

- **模块**: `scripts/deep_research_event_calendar.py`(470 行 [实取·wc -l 2026-11-07T10:0xZ]),结构=docstring 纪律声明/载体与集合常量/词表与白名单(SOURCE_WHITELIST 三源+EVENT_TYPES 两类+指标白名单+窗口默认值)/基础件(_parse_ymd 严格日期/_shift_ymd/make_calendar_event_id)/validate_calendar_event 全量校验(含 ID 指纹重算防篡改)/register_calendar_event(append-only)/list_calendar_events(档内重校验 fail-loud)/load_snapshot_disciplined(三重纪律)/event_window_bounds+classify_observation(窗口口径)/event_window_observations(窗对齐计算)/mount_event_context(快照挂载)/_selfcheck 自检入口;桩注入点登记(AC-03.7 不适用,本包无 GLM 面;测试对模块的注入面=函数参数与临时沙箱,无网络桩)。
- **测试**: `tests/test_p2_wp_d.py`(702 行 [实取·wc -l 2026-11-07T10:0xZ]),15 类 60 用例 [实取·unittest 计数 Ran 60 tests]: 白名单登记 3/黄金 ID 4/schema 负向 10(缺字段/record_type/未知类型/非规范日期/非法日期/未登记源/URL 失配/源不支持类型/指标出白名单/FOMC 通道外/篡改 ID)/registry 面 2(最小集全在场正向+fe.metric patch 缺席负向)/append-only 3(重放拒/跨沙箱同 ID/篡改档 list fail-loud)/装载 2(排序/空档)/窗边界 7(默认边界/pre 边界日/post 含事件日/post=0 仅当日/pre=0 空区间/负数拒/非 int 拒)/窗观测黄金 4(CPI 主黄金 pre2+post1/NFP/窗外排除含 metric 不串窗/FOMC 显式 metric)/窗质量 4(FAIL 排除如实列/非数值排除/零合格 DATA_INSUFFICIENT/无绑定须显式 metric)/快照纪律 5(缺失拒/FAIL 拒/DEGRADED 放行/digest 首原理复算黄金/gate 回显)/挂载 5(黄金相交集/不相交排除/as_of 未来排除/FAIL 拒/零写入+非法档拒)/静态纯度 3(import 白名单/零原始采集档路径字面/零墙钟调用)/确定性 3(ID 首原理三源一致/跨沙箱窗输出逐字节等/重放登记同 ID)/端到端 1(登记→挂载→窗计算 OK+DATA_INSUFFICIENT 混合全链沙箱内聚+免责断言)。
- **黄金值独立预计算登记**: GOLDEN 表 8 项(CAL×5+DIGEST×3)由独立脚本首原理 hashlib 预计算固化(脚本副本入证据包 03/golden-precompute.py,/tmp/p2d-golden-precompute.py 同源);测试内 TestDeterminism.test_event_id_first_principles_recompute 再独立复算==GOLDEN(模块/预计算/测试内三源一致);DIGEST 经 json.dumps(sort_keys,ensure_ascii=False) sha256 前 16 位首原理,与 rp.digest_snapshot 同口径。
- **实现期缺陷修复 1 处**(如实登记,均测试侧,模块零缺陷修复): ①TestEventLoading NFP 事件 spec source_id 首稿误写 SRC_BLS_CPI(应 SRC_BLS_EMPSIT)→list 排序黄金断言红 1,修正后 60 全绿(登记参数零变更,fixture 声明笔误非模块缺陷;对照 WP-C 3 处含模块缺陷,本包模块一次成型 py_compile 即过零修复)。
- **负向敏感性(执行纪律 #4)**: 三真实注入(模块 sha256 注入前锚=f9267192ea0eefdbed83f4f2a202ec7b2c4a541fbefd5c9ec8e5faa68ab674c8): ①classify_observation pre 分支归属失活(pre 观测误判 post 流)→红 2(test_pre_window_boundary_day_before_event+test_cpi_event_window_golden,直击窗口归属语义)②validate_calendar_event source_id 白名单分支失活(`if src is None and False:`)→红 1(test_unregistered_source_rejected,ERROR 形态=后续 src["url"] TypeError,fail-loud 同效)③load_snapshot_disciplined Gate A 分支失活(`and False:`)→红 2(test_gate_a_fail_snapshot_rejected+test_mount_gate_a_fail_rejected,窗计算+挂载双侧拒收面);还原后 60 全绿,模块 sha256=注入前锚等值 f9267192…b674c8(零注入残留 grep INJ 零命中)。
- **本地 CI 镜像**(步骤9): 82 文件 [实取·ls 计数]=81 exit0+1 SKIPPED(test_glm_live)+零非零 [实取·2026-11-07T10:0xZ 逐套件循环];对照 BASE-P2D-CI-SUITES=81 槽(80+1SKIP)→ 基线 81 零回归+本包新增 1(test_p2_wp_d exit=0);套件数 82=81+登记清单内新增 tests 文件数 1,一致无分流。
- **零运行产物锚定**(步骤10 对照 §零.8): `find data/research -newer scripts/deep_research_event_calendar.py -type f` 零输出 [实取·2026-11-07T10:1xZ]=本包零写入 data/research/;`git status` 未跟踪恰=白名单 2 代码件(REPORT 已于登记笔提交)。

---

## §一 做了什么(实现摘要)

**模块** `scripts/deep_research_event_calendar.py`(470 行 [实取·wc -l]),P2-G-04 事件序列数据面确定性落地四件:
1. **事件档格式**: `calendar_event` 记录族(ID=CAL-{YYYYMMDD}-{sha256[:8]},指纹件 5 项不含墙钟→重放幂等);`validate_calendar_event` 全量校验(字段齐备/类型词表/规范日期/白名单/指标绑定/ID 指纹重算防篡改);`register_calendar_event`(append-only 经 drr._write_records,source_url 无入参由白名单登记值回填)+`list_calendar_events`(档内逐条重校验 fail-loud,按 event_date,event_id 升序);
2. **来源登记(DP-5(a) 白名单登记制)**: `SOURCE_WHITELIST` 三源(每源六要素: source_id/publisher/url/access=free_public/credentials=none/cost=none/supports),零付费源零凭证源登记,全生存期零访问(零网络);
3. **快照挂载**: `mount_event_context`——三重纪律过闸(drr._load_snapshot_for_verify+rp.digest_snapshot 重算+rp.gate_allows_formal_research 放行,FAIL fail-closed)后,把「事件窗∩快照观测日期面≠∅」的事件绑定为上下文{snapshot_id,digest_snapshot,gate_a_status,event_ids 升序,future_excluded,window,note},读侧纯计算零写入;
4. **事件窗对齐计算**: `event_window_observations`——pre 窗=[event−pre_days, event−1](不含事件日)/post 窗=[event, event+post_days](含事件日)默认 5/5 自然日(P-D-06);观测=快照 facts 该 metric 窗内条目(每条携 fact_id/snapshot_id/digest_snapshot provenance 绑定);FAIL 质量与非数值如实排除入清单(不填 0);零合格观测→DATA_INSUFFICIENT(available=False);事件无绑定且未显式给 metric→拒(不以相近指标冒充)。

**测试** `tests/test_p2_wp_d.py`(702 行 [实取·wc -l],15 类 60 用例 [实取·Ran 60 tests]),全合成 fixture 唯一数据源、预期值黄金字面量硬编码(GOLDEN 8 项独立预计算+测试内首原理三源复算)、零网络、created_at 全显式定值;类构成与负向敏感性三注入(红 2/1/2)与还原等值详见 §零.10。

**本地 CI 镜像**(2026-11-07T10:0xZ 实跑): 82 文件=81 exit0+1 SKIPPED(test_glm_live)+零非零;对照 BASE-P2D-CI-SUITES=81 槽(80+1SKIP)→ 基线 81 零回归+本包新增 1;套件数 82=81+登记清单内新增 tests 文件数 1,一致(无情形(b)分流)。逐套件记录=证据包 04。

**真实运行面**: 零(§零.8 判定+§零.10 锚定: `find data/research -newer <模块>` 零输出)。

## §二 逐要点证据映射表(AC-02;DESIGN L215 验收要点 4 条 [实取·§零.1 抄录])

| 要点 | (a) 实现落点 | (b) 证据指针 | (c) 自检结论 |
|---|---|---|---|
| ①事件档 schema 与来源登记(免费源 URL 白名单登记制) | 模块: SOURCE_WHITELIST 三源+validate_calendar_event(白名单/URL 逐字相等/类型支持/指标绑定/ID 指纹)+register_calendar_event(URL 无入参登记值回填)+append-only 落档;测试: TestSourceWhitelistRegistry·3+TestEventIdGolden·4+TestEventSchemaNegative·10+TestEventRegistryFace·2+TestEventAppendOnly·3+TestEventLoading·2(行锚: 测试 L131-L191/L192-L375) | 证据包 ①(REPORT §零 副本)+⑤(本表)+04(本地 CI test_p2_wp_d exit=0) | 过(60 用例全绿;未登记源/URL 失配/付费源零登记均有负向或断言锚) |
| ②事件窗对齐计算单测(事件前后窗口取数经快照) | 模块: event_window_bounds/classify_observation(窗口口径 P-D-06)+event_window_observations(经快照三重纪律取数+fact_id/digest provenance+质量纪律)+mount_event_context(挂载);测试: TestWindowBounds·7+TestWindowObservationsGolden·4+TestWindowQuality·4+TestSnapshotDiscipline·5+TestMountContext·5(类行锚: 测试 L376-L594);快照纪律锚: 快照缺失拒/GateA FAIL 拒/DEGRADED 放行/digest 重算黄金 | 证据包 ④+⑤;§零.10 负向敏感性(窗口归属失活注入红 2/GateA 失活注入红 2) | 过(pre 不含事件日+post 含事件日边界直测;DATA_INSUFFICIENT 如实;零直读原始采集档——模块零 data/daily 字面 grep 零命中) |
| ③零凭证零付费断言 | 模块: 白名单每源 credentials=none/cost=none 常量+_selfcheck;测试: TestZeroCredentialPaid·3(凭证/env/付费模式零命中+AST 零网络 import+取数调用字面零命中)+TestSourceWhitelistRegistry·2(免费/零凭证/零付费逐源断言)(类行锚: 测试 L131-L191) | 证据包 ④+⑤;§零.4 DP-5 行(付费源零登记零实施 PENDING 留痕) | 过(断言三面: 白名单常量/源码模式/AST import;零真实源访问结构性保证) |
| ④CI 零回归 | 本地 CI 镜像 82=81 exit0+1SKIP 零非零(基线 81 零回归+本包 1);CI 面=操作者 CHECKPOINT dispatch(登记件 rounds/037/P2-WP-D-CI-dispatch-evidence.md,本席不自行 dispatch) | 证据包 ④(逐套件记录)+§一;CI 登记件=操作者面 | 本地面过;CI 面执行侧留操作者 dispatch 后以登记件为准(NOT VERIFIED@执行席,结构性如实) |

**DP 判据⑥自检(R020-D5 承接)**: DP-1/DP-2/DP-6=本包不触及(零登记面零运行面零回改,沿用 WP-A 族级定值引用,§零.4 表);DP-5(a)=按 DESIGN 范围列明文+合同冻结章登记处置执行(白名单登记制,登记后零回改——SOURCE_WHITELIST 常量自实现笔起未变更,§五 git 取证可复核);DP-5(b) 付费源=零实施+PENDING 留痕;DP-4=零触及;DP 编号与 DESIGN §2.4 实读一致(6 DP)。

## §三 偏离与如实声明

1. **BRANCH-SET 对照方法偏离(如实)**: 冻结章 §三.1 全表经人工重打后机器 diff 出 7 行 SHA 尾部差异→经 R036 证据包 ls-remote-heads-postpush.txt(R036 终笔推送后 54 支机器转储)独立对照链裁定=本席重打转录失真,远端差异集恰 2 支均为登记内预期前移(dev/p2-impl-c→858af49+main→e557fd3),其余 52 支全值一致零漂移(§零.7 详登);教训=长 SHA 对照以机器转储链为准,已在证据包 07 留存两源对照件;
2. **实现期缺陷修复 1 处(测试侧)**: TestEventLoading NFP spec source_id 首稿笔误→排序黄金断言红 1,修正后全绿(§零.10;模块零缺陷一次成型,py_compile+60 用例首跑 59/60 仅此笔误);
3. **本地 Python 版本差异(如实登记)**: 本地 3.9.6 vs CI 3.11(合同步骤9 本地镜像同构跑,语法面已保持 3.9 兼容;CI 3.11 面以操作者 dispatch 登记件为准);
4. **CI 面结构性留操作者**: 本席不自行 dispatch(合同步骤14);AC-02 要点④ CI 面在执行席=NOT VERIFIED@执行侧,证据=登记件将落路径;
5. **黄金预计算脚本 ACT 槽位注记**: /tmp/p2d-golden-precompute.py 中 EV_CORE_CPI fixture(带非法日期串,作日期负向素材预演)最终未入测试文件(测试改用直接改档构造非法日期),脚本该条目为预演残留,其输出(CAL id)未被测试采用——如实注记,黄金值仅采 EV_CPI/EV_NFP/EV_FOMC/EV_FOMC_DFED/EV_FAR+DIGEST×3 共 8 项(测试 GOLDEN 表 [实取·计数 8]);
6. 无其他偏离: 无规格冲突/无套件数不符(82=81+1)/无不触发面/无引用不可达/无中断。

## §四 DP 与登记参数运行后零回改自检

| DP/参数 | 登记定值 | 实现值(运行后实读) | 零回改 |
|---|---|---|---|
| DP-1/2/6 | 本包不触及(§零.4) | 模块零引用(源码 grep DP1/DP2/DP6 零命中) | ✓(结构性无回改面) |
| DP-3 ID 前缀 | CAL-(§零.4) | EVENT_ID_PREFIX="CAL-"(模块 L60 [实取]) | ✓ |
| DP-5(a) 白名单 | 3 源登记不访问(§零.5 P-D-04) | SOURCE_WHITELIST 3 源常量(模块 L69-L89),登记笔后零变更(§五 diff 可复核) | ✓ |
| DP-5(b) 付费源 | 零实施 PENDING(§零.4) | 源码零付费源字面;测试断言白名单全免费 | ✓ |
| P-D-05 最小集指标 | {CPI,CORE_CPI,NFP,NFP_MOM_K}+FOMC{None,DFEDTARU,DFEDTARL}(§零.5) | INDICATOR_METRIC_WHITELIST/FOMC_METRIC_WHITELIST 常量(模块 L91-L92) | ✓ |
| P-D-06 窗口默认 | pre=5/post=5(§零.5) | WINDOW_PRE_DEFAULT=5/WINDOW_POST_DEFAULT=5(模块 L95-L96) | ✓ |
| 全部登记参数 | P-D-01..13(§零.5) | 实现与登记逐项一致(登记笔先于实现笔提交 2e8d92d→4240c14,git 序可复核) | ✓ 先登记后实现 |

## §五 git 纪律与范围自检

1. 分支 `dev/p2-impl-d` 自 e557fd3a6598b0145c9c40cee07299a992ad56bb 切出(§零.7 核验),纯线性: 2e8d92d(登记)→4240c14(实现)→报告笔→终笔,零 merge 提交(BASE..HEAD merges=0 预期,终笔取证);
2. `git diff --name-status e557fd3a…HEAD`: A=恰白名单 4 行、M=0、D=0 预期(终笔取证落证据包 07);
3. reflog 零 reset 零 amend;零 force push;main 未触碰(本地 fetch 仅只读取回对象);
4. 零网络: 模块 import 面白名单+AST 断言(§二 要点③);测试零网络;本席全程网络操作仅 git push/ls-remote/fetch(取证交付类);
5. LIVE 零写入: LIVE 目录本轮标记 grep(R037|P2-WP-D|IA-P2-WP-D)零命中+real_data_acceptance.py SHA256 不变(终笔取证,证据包 06);
6. launchd 零改动(LaunchAgents 快照取证,证据包 06);
7. 研究档案不 commit(data/research/ 零新增零 diff);.gitignore 零改动;workflow 零改动;上游在场件(E2E-A/WP-A/B/C 交付件+主流水线+registry)零改动(M=0 判据内)。

## §六 提交前数值标注六项自检清单(§5.3 强制;清单成件入证据包 03)

全文扫描(REPORT+DELIVERY 双文档)计数类/统计类数值清单与标注核验(逐项二选一标注;[实取] 项已回工作树复核):

| # | 数值 | 标注 |
|---|---|---|
| 1 | 交付清单 k=4 | [实取·§零.2 清点+git ls-files 零重合实跑] |
| 2 | DESIGN DP 表 6 个/D 行验收要点 4 条/事件类型 2 类 | [实取·DESIGN §2.4 表/§七 L215/模块 EVENT_TYPES 清点] |
| 3 | 白名单源 3(SRC_FED/SRC_BLS_CPI/SRC_BLS_EMPSIT) | [实取·模块 SOURCE_WHITELIST 清点+测试断言] |
| 4 | 最小集指标 4(CPI/CORE_CPI/NFP/NFP_MOM_K)+FOMC 通道 2(DFEDTARU/DFEDTARL)+可选 None | [实取·模块常量+registry 在场测试;选取依据引用计数 CPI=8/CORE_CPI=4/NFP=3/DFEDTARU=3/DFEDTARL=3/NFP_MOM_K=2/CORE_PCE=1/FED_FUNDS=0,2026-11-07T09:5xZ 8 模块词边界计数实跑] |
| 5 | 窗口默认 pre=5/post=5 自然日 | [登记定值·P-D-06,非统计观测值] |
| 6 | 高频引用计数统计面 8 模块 | [实取·report_generator/macro_scorecard/allocation_engine/correlation_calculator/market_regime/macro_dashboard/daily_prediction_observer/fact_engine,在场 ls 实跑] |
| 7 | 模块 470 行/测试 702 行 | [实取·wc -l 2026-11-07T10:0xZ] |
| 8 | 测试 15 类 60 用例 | [实取·Ran 60 tests+类定义清点 15] |
| 9 | 类内用例分布 3/4/10/2/3/2/7/4/4/5/5/3/3/3/1(和=60) | [实取·测试文件 def test_ 清点复核] |
| 10 | 黄金字面量 8 项(CAL×5+DIGEST×3) | [实取·GOLDEN 表清点+独立预计算脚本] |
| 11 | 负向敏感性 3 注入红 2/1/2;还原 60 全绿 | [实取·§零.10 执行记录] |
| 12 | 本地 CI 82 文件=81 exit0+1 SKIP;基线 81 槽=80+1SKIP | [实取·2026-11-07T10:0xZ 逐套件循环+合同冻结章 §三] |
| 13 | BRANCH-SET 54 支;远端对照差异集 2 支(52 支一致);重打失真 7 行 | [实取·ls-remote+R036 证据包机器转储对照,§零.7/§三.1] |
| 14 | 开工 heads 计数 54/分支总数执行后预期 55 | [实取·ls-remote 2026-11-07T09:44Z/合同冻结章 §三 注记] |
| 15 | 实现期缺陷修复 1 处(测试侧) | [实取·§零.10] |
| 16 | P-D-01..13 共 13 项登记参数 | [实取·§零.5 表清点] |
| 17 | 证据包成员 8 类;zip 字节数/哈希 | [实取·终笔装配后落 DELIVERY §六(装配时点定值)] |

日期/SHA/结构编号(WP-P2-D/P2-G-04/CAL-ID/DIGEST)/档键成分按边界出圈(头部声明);URL 字符串=登记型参数(P-D-04 登记值,非统计值)。**疑似失实项: 无**(第 17 项 zip 定值为装配时点占位于 DELIVERY §六 回填,双源哈希复核)。

