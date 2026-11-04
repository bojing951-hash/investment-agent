# IA-P03-W1 E2E-A 报告 — 场景登记 / 参数冻结 / 逐模块设计 / 证据指针

- 分支: `dev/p03-e2ea`(自 e04c063d4c3b6ef7ffb71e3720e338094e7ebb9a 切出,线性提交)
- 日期: 2026-11-04(HKT);基点 = main 合并笔(P0-2 封版 + R010 收包后基线)
- 本报告 = 合同 §零"场景登记前置"的正式登记载体: **所有登记项均在真实回放 Run 1 之前完成冻结,运行后零回改**(证据指针见 §六)。

---

## 一、前置实读与场景登记(合同 §3 全部决策)

### 1.1 metric_registry 实读抄录(只读,config/metric_registry.json @ e04c063)

| 类 | 指标 ID | registry 行 | 源/符号 | 频率·单位 | 备注 |
|---|---|---|---|---|---|
| 利率·名义 | UST_2Y | L933 | DGS2 | daily·percent | |
| 利率·名义 | UST_5Y | L962 | DGS5 | daily·percent | |
| 利率·名义 | UST_10Y | L991 | DGS10 | daily·percent | |
| 利率·名义 | UST_30Y | L1020 | DGS30 | daily·percent | |
| 利率·实际 | **TIPS_5Y** | L1194 | DFII5 | daily·percent | |
| 利率·实际 | **TIPS_10Y** | L1223 | DFII10 | daily·percent | **real_rate·core·active,本包选用** |
| 利率·实际 | REAL_10Y | L2155 | fact_engine 派生 | daily·percent | UST_10Y−BEI_10Y,calc L2170 自标"近似" |
| 利率·实际 | REAL_5Y | L2183 | fact_engine 派生 | daily·percent | 同上,标"近似" |
| 利率·实际 | REAL_SHORT | L2211 | — | — | deprecated,不用 |
| 黄金 | **GOLD_F** | L493 | GC=F(COMEX 主力连续) | daily·usd_per_oz | **core,本包选用** |
| 黄金 | GLD | L605 | ETF 代理 | daily·usd | 弃用(期货主力连续优先) |
| 通胀 | BEI_5Y | L1252 | T5YIE | daily·percent | |
| 通胀 | BEI_10Y | L1281 | T10YIE | daily·percent | |
| 通胀 | CPI / CORE_CPI | L1369 / L1399 | — | monthly | |
| 通胀 | CORE_PCE | L1429 | — | monthly | |

**实际历史深度(实读 20261104 采集档)**: TIPS_10Y 459 观测(2025-01-02→2026-11-02,macro_20261104.json);GOLD_F 252 观测(2025-11-04→2026-11-04,global_20261104.json);共同观测 248 日。

### 1.2 "实际利率"构造决策(合同 §3.2 四级优先级,逐级判断)

- **判定: 命中第①级 → TIPS_10Y 直用**。registry 已有 TIPS 类市场观测实际利率(DFII10=10Y TIPS 收益率,Treasury 市场价直出),identity 标 real_rate·core·active,无"近似"标注。
- 第②级(UST−盈亏平衡)/第③级(UST−CPI_YoY)/第④级(利率类替代场景)均**无需降级**。
- 对照弃用项: REAL_10Y/REAL_5Y 为 fact_engine 派生(UST−BEI 期限匹配,L2170 自标"与 TIPS_10Y 市场价差口径略有差异,标'近似'")——市场观测直出优于派生近似,故不取。

### 1.3 数据接入点实读登记(file:line,均实读可抽查)

**macro 通道指标(TIPS_10Y 等)**:
```
snapshot_builder.resolve_inputs          scripts/snapshot_builder.py:47   (FIX7/8 可信边界+规范文件名核验)
  → 字节读取+sha256(与 build_snapshot 读取段 :263-269 同语义;单处 open,源码内标记
    ACCESS_POINT_EXEMPT(标准化层转递)——合同 E2EA-AC-01 豁免句"经标准化层转递不在此限")
  → fact_engine.normalize_macro           scripts/fact_engine.py:275       (身份映射+时效校验+质量分级)
  → 序列提取自标准化层确认的输入结构,结果附事实 unit/quality_status/observation_date
```
**global 通道指标(GOLD_F)**:
```
snapshot_builder.build_snapshot(write=False)  scripts/snapshot_builder.py:236  (全内存,零落盘)
  → snapshot['series_store'][metric_id]        scripts/snapshot_builder.py:358-382
  → 旧ID GOLD→GOLD_F 映射                      scripts/fact_engine.py:244
```
**源码级锁**: tests/test_p03_e2ea.py T6SourceBoundaryLocks 断言 research_history_query.py 全文件**唯一一处** `open(` 且含 ACCESS_POINT_EXEMPT 标记、零 `daily` 目录字样(缺省目录经 `sb.DATA_DIR` 权威常量转发)、零 glob/猜文件名;research_task_manager.py 恰 4 处 `open(` 全部作用于自产研究档案,零触采集档。

**结构性缺口(如实登记,不实施)**: series_store 仅收 global+china 序列(snapshot_builder.py:358-382);macro 利率序列不经快照任何位置——make_fact 不保留 series(fact_engine.py:196,series 仅 :224-227 供派生计算用后即弃)。故 TIPS_10Y 只能经"标准化层转递"豁免句取序列。若政策后续要求利率序列亦走 series_store,须改 snapshot_builder/fact_engine(**白名单外**)→ 见 §四 PENDING-1。

### 1.4 回放窗口登记(合同 §3.4: 优先"实际利率大幅上行而金价坚挺"反常区间)

**登记窗口: 2026-06-30 → 2026-09-30**(自然季度;双序列共同深度 248 日内最长的完整反常季度)。

登记依据(只读探针 /tmp/p03-e2ea-evidence/window_probe.log,探针**先于**参数冻结,只做分段走势观察、零检测计算):
- 2026-06-30→2026-09-01: TIPS 2.20→2.44(**+24bp**)而 GOLD 4038.5→4396.4(**+8.9%**)——全探针唯一"利率金价同涨"标记段;
- 全窗 2026-06-30→2026-09-30: TIPS 2.20→2.93(**+73bp**),GOLD 4038.5→4186.7(**+3.7%**)——实际利率大幅上行而金价坚挺,恰为合同点名场景;
- 窗口后对照段 2026-09-30→2026-11-02: TIPS −31bp 且 GOLD −5.2%(利率回落金价同跌)——登记为后续 tracking 关注背景,**本包不引出任何结论**(无 GLM 环节)。

**时序纪律**: 探针(选窗)→ 参数冻结(§二)→ Run 1;Run 1 触发后窗口与参数**零回改**。

---

## 二、参数冻结登记(检测规则 RD-DIV-001;冻结于 Run 1 前,运行后禁回改)

| 参数 | 冻结值 | 登记理由 |
|---|---|---|
| rule_id | `RD-DIV-001` | 利率vs黄金背离,登记于本节 |
| rolling_window W | `60` 共同观测日差分样本 | 先例=correlation_calculator 滚动窗 60(约一季度) |
| corr_threshold | `0.30`(≥,**含等号**) | 日变化相关由正常负相关翻转为显著正相关的判定阈 |
| rate_bp_threshold | `25.0` bp(≥,**含等号**) | "实际利率大幅上行"量级锚: ≈登记窗真实 +73bp 的 1/3、与 W=60(≈一季度)粒度匹配的显著下限;次临界敏感性由 24bp 用例锁定(不触发) |
| gold_pct_threshold | `2.0` %(≥,**含等号**) | "金价坚挺"下限(同窗金价上行 ≥2%) |
| thresholds_inclusive | `True` | 各阈值比较均为 ≥(等号触发)——临界可精确构造复现 |
| stats_rounding | rho→4 / chg_r_bp→1 / chg_g_pct→4 | 判定基于 round 后统计值(浮点临界可复现) |

**判定式(逐共同观测日 t,窗口 [start,end] 内,i≥W,统计在全序列共同观测上计算=窗口前观测作预热)**:
```
rho(t)       = pearson(最近 W 个 Δr, Δg)                    round4
chg_r_bp(t)  = (r(t) − r(t−W)) × 100                        round1
chg_g_pct(t) = (g(t)/g(t−W) − 1) × 100                      round4
cond_corr(t) = rho(t) is not None and rho(t) ≥ 0.30
cond_move(t) = chg_r_bp(t) ≥ 25.0 and chg_g_pct(t) ≥ 2.0
triggered(t) = cond_corr(t) or cond_move(t)
窗口触发 ⇔ 窗口内 ≥1 个 triggered(t)
```
单位口径: 利率 pp→bp 与 fact_engine.RATE_UNITS emit 同式(fact_engine.py:128-131);价格→pct 与 PRICE_LIKE_UNITS 同式(fact_engine.py:124-127)。

**echo 三方一致**: 日志首行 echo(scripts/anomaly_detector.py echo_params)= 代码常量 = 本节登记值——由 t3a 字面量断言 + Run1/Run2 日志首行共同锁定。

---

## 三、逐模块设计

### 3.1 scripts/research_history_query.py — 历史查询与跨频率对齐(E2EA-AC-01)

- `load_metric_series(metric_id, source_date_ymd, as_of=None, …)`: 按指标 ID 走 §1.3 登记接入点载入全序列;`as_of` 缺省=source_date 日末(北京时间)→ 标准化层时效判定不用墙钟,**回放确定性**。macro 通道返回附事实质量状态与源档 sha256;global 通道附 sources_status 的 file/sha256。
- `_clean_series`: 升序去重(同日留最后)+缺值剔除并计 `n_missing_dropped`——**缺值如实缺席,绝不填 0**。
- 对齐规则登记:
  - 日频默认: 共同实际观测日内连接(升序交集;先例 correlation_calculator.paired_returns scripts/correlation_calculator.py:53-66,算术对齐不假设日历);
  - `align_to_iso_week` / `align_to_month`: 网格代表值=该 ISO 周(周一起)/自然月内**最后有效观测**——与 fact_engine compute_period_returns 的 week/mtd 基准("期开始之前最后有效观测",scripts/fact_engine.py:81)互为对偶,口径同构登记;
  - `interval_change`: end=≤end 最后观测;**基准=严格早于 start 的最后观测**(不取 start 当日,与"期开始之前"一致);单位纪律与 fact_engine emit() 同式(利率→pp+bp,价格→pct,其他→绝对差);基准值 0→百分比不可定义;数据不足→`available=False`+原因,不回退 0。
- `pearson` / `rolling_correlation`(参数化): correlation_calculator.pearson 同式(scripts/correlation_calculator.py:69-80;n<3 或零方差→None)。

### 3.2 scripts/anomaly_detector.py — 背离检测器(E2EA-AC-02)

纯计算、零网络零文件 IO(t3g 源码锁)。冻结常量即 §二;`detect_divergence` 在**全序列共同观测**上计算滚动统计(窗口前观测自然提供预热,调用方无须截预热),仅窗口内统计行进入 series/判定;窗口内无可评分观测→如实空序列+原因(不造点)。三情形合成验证见 §五测试表。

### 3.3 scripts/research_task_manager.py — 任务结构与 E2E-A 编排(E2EA-AC-03/04)

- schema 最低字段(可增不可减,实际档恰 10 字段无额外): task_id / created_at(UTC) / phenomenon / status / indicators / window / detection(规则+冻结参数+触发统计) / evidence(接入点+产物标识+计算指针+数据质量状态) / **falsifiable_conditions(非空,3 条)** / history(追加式)。
- 状态机登记: `pending → active → concluded → tracking`,**本包实现至 active**(=证据装配完毕;concluded 及以后为 P0-3 后续包)。
- task_id 确定性: `RT-{start}~{end}-{RULE_ID}-{sha256(指纹)[:8]}`,指纹=窗口/规则/指标/参数排序 JSON——同窗同参重放必然同 id(幂等锚)。
- append-only 档案(落 `data/research/`,不 commit): 同 id 同指纹→**幂等跳过**(零写入);同 id 异指纹→追加 `{task_id}__v{N}.json`(原档字节不动);检测统计序列每运行落独立 `detection_series_{start}_{end}_{seq:03d}.json`(序号递增,永不覆盖)。
- E2E-A 编排(stdout=运行日志): 参数 echo 首行 → 窗口/重放策略 → 逐指标源信息(unit/quality/观测日/n_obs/源档/sha256/接入通道) → 对齐 → 统计摘要 → 触发统计序列落档 → 触发→建任务+装配(窗口内共同序列档内直读 evidence.series_window)+落档+active;**不触发→如实输出+情形(c)分流说明,exit 0(合法结果,禁调参凑触发)**。
- 可证伪条件(3 条,自动生成自冻结参数): A 阈值反证(窗口数据可直接复核反驳)/ B 现象消解(金价转负而利率续升)/ C 解释竞争(控制变量引入后相关恢复负值则主题必要性不成立)。

---

## 四、发现与 PENDING(白名单外需求,登记不实施)

- **PENDING-1(结构性缺口)**: macro 利率序列不经快照 series_store(§1.3)——本包依合同豁免句"经标准化层转递"实现 TIPS_10Y 取数;若后续政策要求全部研究序列统一走 series_store,须扩 snapshot_builder/fact_engine 序列保留面(白名单外,建议 P0-3 后续包评估)。
- **PENDING-2(信息噪音,轻微)**: fe.normalize_macro 处理 macro 采集档时对 registry 外 A 股代码(000300/000905/000852.SH)打印警告,混入 E2E 运行日志——标准化层既有行为,非本包引入,不建议本包屏蔽(保持上游原样);如需静默建议上游加过滤参数(白名单外)。
- **观察登记(非结论)**: 本登记窗口 rho 全负([-0.3202,-0.0735],利率-金价日变化相关保持负),背离体现在**幅度共涨**(cond_move 路径,16 触发日全部 cond_move=True/cond_corr=False)而非相关翻转——与 phenomenon"实际上行而金价坚挺"表述一致,如实记录。

---

## 五、真实回放结果与测试(证据指针全量见 DELIVERY §二)

### 5.1 Run 1(登记窗口 2026-06-30→2026-09-30,source=20261104,as_of=日末)

**TRIGGERED**(exit 0): n_common=65,n_scored=65,**n_triggered=16,首触发 2026-08-21**;rho_range=[-0.3202,-0.0735];首触发行={rho:-0.1122, chg_r_bp:31.0, chg_g_pct:5.2199, cond_move:True};末行(2026-09-30){rho:-0.3141, chg_r_bp:63.0, chg_g_pct:0.7048}自身不触发(金价涨幅已回落至 0.7%<2%),如实保留。任务档 `data/research/RT-2026-06-30~2026-09-30-RD-DIV-001-17788777.json`(sha256=03b4fd7d7cb9684ff1170de1a536bd67bd2952cf84390f5e1d13958006abd261)——schema 10 字段/状态 active/history(None→pending→active)/证据(接入点+双源档 sha256+series_window 65 日直读+质量状态)全量可直读复核(archive_verify.log)。

### 5.2 Run 2(同窗同参重放,验证 append-only)

**skipped-idempotent**(exit 0): 既有档案 sha256 **逐字节不变**(同上全值);新增仅 `detection_series_…_002.json`(内容与 _001 确定性一致,同 sha256=8d3c631a…);双次运行前后 `data/daily/` 24 文件 sha256 清单 **零 delta**(manifest diff)。零调参尝试、零窗口回改、零重跑凑数——恰 2 次运行。

### 5.3 测试(tests/test_p03_e2ea.py,34 用例全绿;全合成/零网络/零新依赖)

| 类 | 用例数 | 覆盖 |
|---|---|---|
| T1 历史查询与接入点 | 7 | 双通道合成档载入/接入点文本/清洗不填0/时效 as_of |
| T2 对齐与计算 | 8 | 内连接/ISO周/自然月代表值/区间变动(bp·pct·不足)/pearson 字面量/滚动相关 |
| T3 检测器三情形 | 7 | **在场触发(恰25.0bp+2.0%含等号)/次临界不触发(24bp)/相关性路径触发/正常负相关不触发/数据不足如实空/纯计算锁/echo=登记常量** |
| T4 任务结构与档案 | 5 | schema 最低字段/状态机/append-only 幂等跳过(字节不变)/异指纹__v2 追加/统计序列序号递增 |
| T5 E2E 编排(合成) | 3 | 触发路径全链落档/重放幂等/不触发情形(c)分流 |
| T6 源码边界锁 | 4 | 唯一 open 且含豁免标记/零 daily 字样零 glob/零网络 import/编排器 open 边界 |

**负向敏感性(真实注入缺陷→专项红→恢复)**: NEG1a 阈值漂移 0.30→0.50(t3a 红)/ NEG1b cond_move `and`→`or`(t3c 红)/ NEG2 区间基准 `<`→`<=`(t2d 红)/ NEG3 幂等跳过删除(t4c 红)——4/4 RED,恢复后 34 用例回绿(negative_sensitivity.log)。

**全量回归**: 56 套件(CI 55+1)= 55 绿 + test_p4_fixes.py 本地红(既有基线,4 失败全在 monthly_review.build_data_block 真实数据块提取,P4 域与本包零导入关系;明细 p4_fixes_preexisting_red_detail.log)。

---

## 六、证据指针

全部落 `/tmp/p03-e2ea-evidence/`(zip+SHA256SUMS 为合同 AC-07 最低集①-⑧): manifest_daily_pre_run1 / manifest_daily_post_run2(零 delta)/ manifest_research_pre_run1(目录不存在)/ manifest_research_post_run2 / run1_raw.log / run2_raw.log(含 exit_code)/ negative_sensitivity.log / full_regression.log / archive_verify.log / window_probe.log(+脚本)/ 档案全量副本 / p4_fixes_preexisting_red_detail.log / git_local_state.txt / ls_remote_pre_push.txt(+push 后件)/ CI 登记件由操作者后补至 `rounds/011/P03-W1-CI-dispatch-evidence.md`(本报告引用其将落路径)。
