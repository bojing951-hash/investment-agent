# IA-P0-1 验收自检文档 — Gate A质量门禁全链路执行

- 任务编号: IA-P0-1 | 契约: IA-P0-1-AC-v1.0(固定,未改动)
- 日期: 2026-10-27 | 分支: main | 基线: 844fd3b
- 开发环境: /tmp/inv-dev(macOS, ~/AI内容/venv/bin/python3)
- 本文档记录真实执行结果;未运行的行为在§10如实标注,不虚构通过项。

---

## 1. 提交前检查(Pre-commit)

| 检查项 | 结果 |
|---|---|
| 工作区基于基线844fd3b,无用户未提交改动被覆盖 | ✅(开工前git status干净) |
| env_config.py未被修改(GitHub版保持脱敏) | ✅(git diff不含env_config.py) |
| 无API Key/敏感信息进入diff | ✅(人工复核全部diff;新增文件均为纯逻辑/测试) |
| 无真实生产数据修改(全部测试走tempdir隔离) | ✅ |
| 本地全部测试通过后才提交 | ✅(见§8) |

## 2. 提交后检查(Post-commit)

| 检查项 | 结果 |
|---|---|
| push到origin/main(非force) | ✅ |
| 远端HEAD=本地提交 | ✅(push后git status显示up to date) |
| CI | ➖ 本仓库无CI配置,不宣称CI通过 |

## 3. 修改文件清单

**新增(2)**:
- `scripts/research_provenance.py` — 来源绑定/门禁原语共享模块(快照版本选择/gate三态/digest/meta sidecar/门禁合成/锚点批次核验)
- `tests/test_gate_chain_p01.py` — 本轮AC行为测试套件(84项断言)

**修改(13)**:
- `scripts/snapshot_builder.py` — 锚点整体替换(不再merge残留键);原子写;anchors meta sidecar(source=snapshot+快照ID+digest+Gate A);source_file带实际版本(_vN)
- `scripts/data_assembler.py` — 移除"缺快照现场构建";改用确定性版本选择;Gate A FAIL/不可用→拒绝打包exit 2(无快照exit 1);DEGRADED继续+数据包内降级披露节;data_pack meta sidecar绑定快照
- `run_weekly.py` — 步骤依赖图(4元组,兼容3元组);依赖未成功→SKIPPED带原因(PipelineResults.skips);关键失败/跳过→exit 1;流水线台账logs/pipeline_run_*.json
- `scripts/report_generator.py` — main抽出为generate_weekly_report();预检verify_research_inputs(GLM前核验四件套,失败exit 2不调GLM不写状态);当日锚点/锚点prompt(替代glob最新);Gate A+B合成(rp.combine_gates);report_status_*.json sidecar;最终FAIL→改名*_UNVALIDATED.md+exit 3+不回写;DEGRADED→可见降级footer;上期报告过滤_annotated/_UNVALIDATED(修复'_'排序缺陷)
- `scripts/data_validator.py` — 快照锚点不重写(构建器唯一写入方);遗留路径save_anchors标注meta source=legacy;报告glob排除_UNVALIDATED
- `scripts/daily_prediction_observer.py` — 指标级质量FAIL→该预测跳过;锚点批次核验(legacy/失配→关键FAIL);glob排除meta侧挂;无meta旧格式保持既有规则(离线兼容)
- `scripts/macro_scorecard.py` / `scripts/correlation_calculator.py` — 改用rp.select_snapshot(同日多版本取最高修订版,候选损坏拒绝)
- `scripts/monthly_review.py` / `scripts/quarterly_outlook.py` — 输出头标注数据来源(原始序列直读,非快照链);周报索引排除_UNVALIDATED
- `scripts/daily_report_generator.py` — 遗留入口声明(不在调度内,输出不得作合格正式产出)
- `tests/test_phase4.py` — 修复既有日期依赖缺陷(用例只在首次调用mock datetime,10天后自然腐坏;改为三次统一固定today=20261017)
- `tests/test_glm_live.py` — glob排除*.meta.json(默认仍跳过,不产生付费调用)

## 4. 关键修复摘要(对应6个确认问题)

1. **Gate A FAIL不停下游** → 装配器exit 2拒绝打包;流水线依赖图使打包/校验SKIPPED;报告预检exit 2;观察器批次/质量核验。
2. **装配器接受失败快照** → 移除auto-build;gate_status缺字段/非法不默认PASS;exit 2。
3. **独立周报生成器无Gate检查** → verify_research_inputs四件套核验(快照+Gate A/包绑定/锚点批次/当日prompt),GLM调用次数=0可证。
4. **同日陈旧包/锚点/快照版本混用** → 确定性版本选择(最高修订版,损坏即拒);包/锚点meta绑定快照ID+digest;篡改/旧版残留自动失配。
5. **Gate A/B未合成** → combine_gates任一FAIL→FAIL;FAIL报告改名_UNVALIDATED+exit 3+不回写;DEGRADED可见披露。
6. **旧入口绕过快照** → legacy锚点批次meta标注并被观察器/预检拒绝;daily_report_generator显式声明遗留。

## 5. AC-01~13自检

| AC | 结果 | 说明 |
|---|---|---|
| AC-01 Gate A三态语义 | IMPLEMENTED | 缺gate_a字段/非法状态/非对象→None(不默认PASS);PASS正常/DEGRADED继续+披露/FAIL阻断(§8套件§1;装配器/预检/观察器三处消费) |
| AC-02 流水线关键失败/依赖 | IMPLEMENTED | 依赖失败→SKIPPED带原因不执行;独立安全诊断(观察器)继续;关键失败/跳过→exit 1(§8套件§9;round5 R17回归通过) |
| AC-03 装配器不得绕过Gate A | IMPLEMENTED | FAIL/缺字段→exit 2不产包;无快照exit 1;移除auto-build(§8套件§4) |
| AC-04 可验证来源绑定 | IMPLEMENTED | snapshot→pack→anchors→report经meta sidecar链(ID/digest/研究日期/Gate A);版本选择确定性;不可判断即拒绝(§8套件§2/3/5) |
| AC-05 独立周报入口预检 | IMPLEMENTED | 10种缺陷场景全部拒绝且GLM调用=0/不写状态/不产报告/exit 2;无内存依赖,全部基于磁盘产物(§8套件§5/6) |
| AC-06 Gate A+B正确合成 | IMPLEMENTED | 12组合穷举(含未知状态按FAIL)(§8套件§6) |
| AC-07 FAIL报告不冒充合格 | IMPLEMENTED | 改名*_UNVALIDATED.md;上期报告/校验glob/月报索引均排除;status sidecar记FAIL(§8套件§6/7/11) |
| AC-08 长期状态保护 | IMPLEMENTED | 观察器: 质量FAIL指标跳过、legacy/失配批次关键FAIL、合格指标照常;报告侧FAIL不回写;未清空/重置任何历史状态(§8套件§8) |
| AC-09 遗留入口 | IMPLEMENTED | legacy锚点meta标注+下游拒绝;daily_report_generator显式声明;月报/季报输出标注数据来源 |
| AC-10 DEGRADED降级能力 | IMPLEMENTED | 预检通过继续生成;数据包含降级披露节+不合格指标点名;报告尾部可见footer;回写按既有规则(§8套件§4/5/6) |
| AC-11 状态/来源/跳过可追溯 | IMPLEMENTED | SKIPPED原因公示+.skips;pipeline_run_*.json台账;report_status_*.json;validation日志保留(§8套件§9) |
| AC-12 核心功能无回归 | IMPLEMENTED | 17个既有离线套件781项断言全部通过(§8);无测试被删除;test_phase4修复的是日期腐坏缺陷而非规则弱化 |
| AC-13 测试/提交/交付证据 | IMPLEMENTED | 新套件84项;真实命令与计数见§8;本文件即交付证据 |

## 6. 各AC代码路径(入口→核验→拒绝/放行)

- AC-01: `research_provenance.gate_status/gate_allows_formal_research` ← `data_assembler.main` / `report_generator.verify_research_inputs`
- AC-02: `run_weekly.run_pipeline`(依赖判定+PipelineResults.skips) ← `run_weekly.main`(exit 1) / `run_daily.sh`(透传退出码)
- AC-03: `data_assembler.load_snapshot`(rp.select_snapshot) + `data_assembler.main`(exit 1/2)
- AC-04: `research_provenance.select_snapshot/digest_snapshot/provenance_of/write_meta` ← `snapshot_builder`(anchors meta) / `data_assembler`(pack meta) / `report_generator.verify_research_inputs`(核验) / `report_status_*.json`
- AC-05: `report_generator.verify_research_inputs` + `generate_weekly_report`(第0.9步,exit 2在GLM之前)
- AC-06: `research_provenance.combine_gates` ← `generate_weekly_report`(第3.55步)
- AC-07: `generate_weekly_report`(改名+exit 3) / `load_previous_report` / `data_validator.__main__`报告glob / `monthly_review` wk_files
- AC-08: `daily_prediction_observer.observe/_metric_problem`(质量FAIL跳过) + `research_provenance.verify_anchor_batch`(批次) ;报告侧`apply_status_updates`(FAIL拦截,既有)
- AC-09: `data_validator.save_anchors(source='legacy')` meta标注;`daily_report_generator`模块docstring声明
- AC-10: `data_assembler.build_markdown`降级披露节;`report_generator._append_degraded_footer`
- AC-11: `run_weekly`(SKIPPED公示+logs/pipeline_run_*.json);`report_status_*.json`;`logs/validation_*.log`(既有)

## 7. 测试名称(新套件, tests/test_gate_chain_p01.py)

§1 Gate A三态(6) · §2 版本选择(6) · §3 快照构建器来源链(8,含CLI exit 2/3) · §4 装配器门禁(6) · §5 预检矩阵(13) · §6 报告主流程(14,含GLM mock: 预检失败GLM=0/PASS/FAIL改名/DEGRADED footer/合成穷举12) · §7 上期报告过滤(1) · §8 观察器(6) · §9 流水线依赖(7) · §10 遗留标注(1) · §11 校验过滤(1) — 共84项断言。

## 8. 实际执行的测试命令与真实结果

运行器: `~/AI内容/venv/bin/python3`(无CI,本地逐套件执行,2026-10-27):

| 套件 | 命令 | 结果 |
|---|---|---|
| test_datafix_20261017 | `.../python3 tests/test_datafix_20261017.py` | 13通过/0失败 |
| test_e2e_four_weeks | 同上格式 | 59通过/0失败 |
| test_fact_engine | 同上 | 59通过/0失败 |
| test_p0_fixes | 同上 | 22通过/0失败 |
| test_p1_fixes | 同上 | 36通过/0失败 |
| test_p2_fixes | 同上 | 82通过/0失败 |
| test_p4_fixes | 同上 | 43通过/0失败 |
| test_p7_fixes | 同上 | 30通过/0失败 |
| test_phase3 | 同上 | 47通过/0失败 |
| test_phase4 | 同上 | 20通过/0失败(修复既有日期腐坏后) |
| test_round3_adversarial | 同上 | 24通过/0失败 |
| test_round3_p0 | 同上 | 91通过/0失败 |
| test_round4 | 同上 | 94通过/0失败 |
| test_round5 | 同上 | 64通过/0失败 |
| test_round6 | 同上 | 51通过/0失败 |
| test_snapshot | 同上 | 46通过/0失败 |
| **test_gate_chain_p01(新)** | 同上 | **84通过/0失败** |
| test_glm_live | 同上 | 跳过(设计如此: 需RUN_GLM_LIVE=1,默认不产生付费调用) |

**合计: 865项断言通过 / 0失败 / 1套件按设计跳过。**
本轮测试未调用付费GLM API(报告主流程用例全部mock `_call_glm`并断言调用次数)。

## 9. 未验证/无法在本环境验证的行为

1. **launchd真实调度下的端到端**: com.investment.daily/weekly未在本轮触发(约束: 不得自动更改launchd任务)。退出码约定已由X6/R16e式用例与run_daily.sh透传逻辑覆盖,但真实launchd告警链路未实测。
2. **真实GLM生成+Gate B真实分级的新链路**: Gate B分级本身由既有套件覆盖(round3_adversarial等);新链路中validate_generated_report以mock分级驱动(真实GLM输出与分级的组合留待下一次真实周报运行观察)。
3. **生产目录首次运行**: 首个采用新代码的运行日,当天须先完整跑daily流水线(产出带meta的数据包)后,weekly报告入口才能通过预检——旧存量包无meta会被预检拒绝(预期行为,见§11)。

## 10. 生产部署注意(不加launchd变更,人工操作)

1. 同步代码到生产目录后,**首个运行日**的周六08:00 weekly前,须确保当日07:00 daily流水线已用新代码完整跑过(anchors/pack带meta);否则weekly预检exit 2(安全侧: 不产报告,不污染状态)。
2. 存量历史快照/数据包/锚点无需迁移: 新消费方只对**当日**产物要求meta;历史重生成场景需先重跑当日装配。
3. 观察器对无meta的历史锚点文件保持既有日期规则(不回溯拒绝),仅对**带meta**的批次执行来源核验。
4. 修订快照流程不变: `--allow-revision`生成_vN后,须重跑装配器(第9步)与校验器(第10步)刷新包/锚点绑定;依赖图会自动联动。
5. 回滚方式: revert本次commit即可恢复旧行为(无数据格式破坏;meta sidecar为新增文件,旧代码忽略之)。

## 11. 遗留问题

- 无阻塞遗留。§9所列3项为环境限制下的未实测项,均有对应离线覆盖与安全侧设计。
