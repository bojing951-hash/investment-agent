# R26 · VP 旧库 5 行 LABEL_DRIFT 对账单

- 日期: 2026-11-14(HKT)
- 分支: `dev/rd-r26-label-drift`
- 任务: RESUME R26 候选①(T-R26-1;R22 遗留台账项)
- 工具: `scripts/view_plausibility.py --reconcile-drift VIEW-…`(新增
  `reconcile_label_drift`,R26)
- 测试: `tests/test_rd_r26_label_drift_reconcile.py`(28 判定绿)

## 一、根因(审计定性)

VP v1.0 存量(2026-11-10 批 11 档中的 5 档)的 mode C verdict 由早于期限
解析器成熟期的构建面写入,`no_forecast` 为旧期词汇(语义="无机器可验预测
绑定");现行引擎(view_verifier verify_expiry,P0-1 4bdcf6e 起+R22 5.2 到期
新鲜度门)已按**期限可解析性**分化:

- 期限文本不可解析(如「当前(会后即刻)」「未指明」)→ `UNPARSEABLE_HORIZON`
- 期限可解析且未到期(如「CY2026」「2026全年」→ 2026-12-31)→ `NOT_YET_TESTABLE`

**R22「重建即消」预期对这 5 行不成立**:`build_vp` C 层零变动设计
(`doc = dict(base)` 原样保留 `hypotheses[].evidence`),`--build-all` 不刷新
存量 verdict——词汇漂移只能经显式对账收口(本轮新增 reconcile 面)。

旁证: 同档兄弟假设(如 VIEW-20261110-007 hyp1)已是新词汇 NOT_YET_TESTABLE,
证明 hyp0 的 no_forecast 是构建期滞后残留,非当前引擎语义。

## 二、逐行处置(5/5=重贴,可见非静默)

对账基: 快照 `research_snapshot_20261112_v2`(as_of=20261112,与存量档同基,
排除快照推进因素)。全部 5 行重算 verdict 均经本席对照 views 档 forecast
原文(horizon/value_or_direction)人工核对语义正确。

| 档 | 假设 | verdict 从→到 | 标签从→到 | view_label | 语义依据 |
|---|---|---|---|---|---|
| VIEW-20261110-002 | hypotheses[0] | `no_forecast`→`UNPARSEABLE_HORIZON` | INSUFFICIENT→INSUFFICIENT(不变) | INSUFFICIENT(不变) | fc0「维持3.75%-4.00%」horizon「当前(会后即刻)」=期限不可解析 |
| VIEW-20261110-005 | hypotheses[0] | `UH/UH`(2-join)→`UH/UH/UH`(3-join) | INSUFFICIENT→INSUFFICIENT(不变) | INSUFFICIENT(不变) | linked[0,1,2] 三 forecast 全期限不可解析(维持2.50%/2.65%/2.90%),存量 arity 缺一 |
| VIEW-20261110-006 | hypotheses[0] | `no_forecast`→`UNPARSEABLE_HORIZON` | INSUFFICIENT→INSUFFICIENT(不变) | INSUFFICIENT(不变) | fc0「维持约1.25%」无期限 |
| VIEW-20261110-007 | hypotheses[0] | `no_forecast`→`NOT_YET_TESTABLE` | INSUFFICIENT→**NOT_YET_TESTABLE** | INSUFFICIENT(不变,混合档 rollup) | fc0「4.4%」horizon CY2026→到期 2026-12-31>20261112 未到期 |
| VIEW-20261110-010 | hypotheses[0] | `no_forecast`→`NOT_YET_TESTABLE` | INSUFFICIENT→**NOT_YET_TESTABLE** | INSUFFICIENT(不变,混合档 rollup) | fc0「102.4 mb/d」horizon 2026全年→到期 2026-12-31 未到期 |

注: UNPARSEABLE_HORIZON=UNP 缩写。007/010 标签变更为**精度提升**(从"证据
不足"细化为"真预测、未到期"),非判定内容变更(两标签同属不可判族
`_UNTESTABLE_FAMILY`,不触发 BINDING_VIOLATION 判据);库级六标签契约
(17 档 view_label 全 INSUFFICIENT_EVIDENCE)经 rollup 自动保持,零档变动。

## 三、可见非静默纪律(工具内建)

- 每行 `evidence.verdict_history` 追加 `{date(HKT), from, to, basis,
  snapshot_id, by}`(不删旧史);标签变更行另留 `label_history`(含 reason)。
- 档级 `reconciliations` 台账追加(round=R26/principle=可见非静默)。
- 拒写边界: 档内存在 `BINDING_VIOLATION`(红线)→ 整档拒写;重算标签=
  SUPPORTED/CONTRADICTED(判定内容变更)→ 默认拒写,须 `--allow-judgment`
  显式放行。本轮 5 档均未触碰两边界(0 violation/0 判定标签)。
- 写前 `validate_vp` 全过;原子写(`.tmp`+`os.replace`);幂等(零漂移=零写)。

## 四、真实面复证(dev 树 data/institutions/verification/ 17 档)

| 项 | 前 | 后 |
|---|---|---|
| 全库绑定扫描(133 假设行) | 128 BINDING_OK + **5 LABEL_DRIFT** + 0 违规 | **133 BINDING_OK + 0 LABEL_DRIFT + 0 BINDING_VIOLATION** |
| view_label 17 档 | 全 INSUFFICIENT_EVIDENCE | 全 INSUFFICIENT_EVIDENCE(零变动) |
| 5 档文件 sha256[:16] | 48d2797f…/ebdec679…/9a62f970…/86758383…/7d5a58f4… | 05a293e4…/6d60b415…/85b64373…/43a3493e…/dd85f17b… |

(data/ 为 gitignored 本地面;LIVE 树不动——Charter 10 §十,LIVE 修改须
用户明确指令。)

## 五、边界与诚实声明

- 对账=**重贴存量词汇/到期性判定**,不产生新的研究结论;007/010 的
  NOT_YET_TESTABLE 首验窗仍=各自到期日(2026-12-31 后的快照窗口),与
  库级六标签首验窗(2026-12)一致。
- `no_forecast` 旧词汇在 4 档中为存量文本,重贴后全库已无该词汇残留
  (重算+扫描确认);历史经 verdict_history 可追溯。
- 本轮不动 R25 余留 NIT(Ni-2/3/4/5)——留 R26+ 候选②。
