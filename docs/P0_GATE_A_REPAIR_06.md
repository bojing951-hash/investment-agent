# P0 Gate A 修复报告 06（FIX6：规范来源批次身份）

- 契约：IA-P0-1-FIX6-AC-v1.0（本轮）；IA-P0-1-AC-v1.0 及 FIX1~FIX5-AC 全部继续有效，未降低任何阈值
- 角色：开发（本轮自检）；独立验收由 Agent 4 另行执行
- 日期：2026-10-28
- 分支：main

## 1. 开发前固定 Commit

- dev-before：`686f33ecb7a63925efb301d39cd896584711e20a`（FIX5 终 HEAD）
- FIX5 实现：`5e3bdcc666b397c91dab53e0ccd5a4947abf82df`；原始审计基线 `844fd3bef5e1e7e17b4d333278acd319f1dbae41`（不变）
- 基线状态：25 套离线测试全绿；工作区干净，本地=远程=686f33e；无其他开发任务差异

## 2. 实现 Commit

- `1e4b8b3b4a7a647ad6e1a439edea10a610e802b7`（代码+测试，已推送 main，无 force）

## 3. 最终交付 Commit

- 文档 Commit B = 本提交（docs only）；其 SHA 与 Actions 运行在推送后于最终开发回复中给出（文件无法自含其推送后才生成的事实，不预填）

## 4. IA-F5-DEF-001～003 整改矩阵

| 缺陷 | 必须不可通过的场景 | 实现机制 | 测试 |
|---|---|---|---|
| DEF-001/FIX6-01 | global 声明 macro 文件；伪装前缀；非 JSON 扩展名；绝对路径/../；目录冒充；符号链接逃逸；文件名日期≠file_date；声明与事实同步改跨通道文件（字符串自报一致） | `SOURCE_FILE_RULES`+`canonical_source_file`（通道前缀+YYYYMMDD 真实日历+.json+无路径成分）；文件名日期==file_date；data_dir 模式 isfile/非链接/realpath 规范位一致 | A5-A14、A16、E3、E4b |
| DEF-001/FIX6-02 | EXACT 用前一日文件；FALLBACK 超窗 1 天/115 天（自报 lag 自洽）；FALLBACK 未来日期；lag 与真实差不符 | EXACT: 文件名日期==file_date==当日；FALLBACK: 真实早于当日+lag==真实差+**≤通道既有窗**（global/china=5，macro/rate_economy=7，resolve_inputs 同源约束） | B 全矩阵（四通道） |
| DEF-002/FIX6-03 | collector 为 None/空串/列表/字典/数字/布尔 → 旧代码 `col not in frozenset` 抛 TypeError | 成员测试前显式 `isinstance(col,str) and col.strip()` 类型守卫（可诊断拒绝，不吞异常）；source 非对象/file 非字符串同守卫；原始+派生两分支 | C 全矩阵+E6 |
| DEF-003/FIX6-04 | MISSING 携带 file（字符串/列表/字典）/file_date/lag_days；READ_FAIL 缺 error 或携带 file/file_date/lag_days；EXACT 携带 lag_days/error；FALLBACK 携带 error | 状态字段互斥规则（类型安全）：MISSING 仅 {'status'}（字段缺失与 None 等价，构建器口径）；READ_FAIL 必须非空字符串 error | D 全矩阵 |

## 5. 代码路径

- `scripts/research_provenance.py`：新增 `SOURCE_FILE_RULES`/`_SOURCE_FILE_RE`/`canonical_source_file()`；`sources_status_problems()` 重写 EXACT/FALLBACK/MISSING/READ_FAIL 四分支（规范名/日期互证/窗口/互斥/实体核验）；`fact_source_problems()` 类型守卫+批次规范名校验
- `scripts/snapshot_builder.py`：`SOURCES` 自 `rp.SOURCE_FILE_RULES` 推导（单一权威定义）；`resolve_inputs()` 只选规范普通文件（isfile+非链接+规范名）
- `tests/test_p01_fix6.py`（新增）、`tests/test_p01_fix5.py`（A11/D16 按更严契约更新）
- 门禁传播复用 FIX5 既有链路（§9）：recompute→gate_status→装配器 exit2→周报预检拒/GLM=0→发布/观察器保护，未另起炉灶

**真实来源规则表**（以代码为准，非新设标准）：

| 通道 | 文件模式 | collector（注册表权威） | EXACT 语义 | FALLBACK 语义 | 最大回退自然日 | MISSING/READ_FAIL 产物字段 |
|---|---|---|---|---|---|---|
| global | global_YYYYMMDD.json | global_market_collector | 文件名日期==file_date==当日 | 真实早于当日，lag==真实差 | 5 | MISSING={'status'}；READ_FAIL={'status','error'} |
| macro | macro_YYYYMMDD.json | macro_collector | 同上 | 同上 | 7 | 同上 |
| china | china_YYYYMMDD.json | china_market_collector | 同上 | 同上 | 5 | 同上 |
| rate_economy | rate_economy_YYYYMMDD.json | rate_expectations | 同上 | 同上 | 7 | 同上 |
| （派生） | 无行情 JSON（source.file='derived'） | fact_engine（compute_derived 输出集） | — | — | — | 派生须 calculation_ref+输入在场可算 |

## 6. F6-AC 验收自检矩阵

- §5 统一采集文件规则（两模块同一规则源）：✅ SOURCE_FILE_RULES 单点定义，sb 推导
- §5.3 文件名严格符合通道（8 类拒绝+路径越界）：✅ A5-A14
- §5.4 文件实体（目录/链接/越界/规范位；不能只 exists）：✅ A8-A10+A16+E4b
- §5.5 15 项测试+五层执行（ssp/fact_source/recompute/gate_status/下游预检）：✅ A 矩阵三口径直调+E 下游
- §6 EXACT/FALLBACK 时间一致性+四通道窗口+115 天：✅ B 全矩阵
- §6.3 观测日与批次日合法不同不强制相等：✅ B 对照
- §7 collector 六类非法类型×原始/派生，无 TypeError、Gate 不放行、装配/预检拒：✅ C+E6
- §8 状态互斥全场景+字段缺失与 None 规则用测试固定：✅ D（D1b 显式固定）
- §9 拒绝传播至 Gate A/装配/GLM=0/报告保护/长期状态/日志含通道与问题类型：✅ E3-E10
- §10 测试可独立执行、真实模块+临时目录、Mock 仅外部 API/GLM：✅

## 7. 历史契约适用自检

IA-P0-1-AC-v1.0 与 FIX1~FIX5-AC 全部适用项保持：fix1(82)/fix2(109)/fix3(45)/fix4(49)/fix5(62)/gate_chain(86)/frozen14(33)/orig14(41)/four_weeks(59) 本轮全绿即回归证明；FIX5 的两极 data_dir 口径、quality/issues 一致、严格日期、fail-closed 全部保留并在 FIX6 下继续通过。

## 8. 新增文件身份测试（test_p01_fix6.py A 矩阵，15 项要求全覆盖）

A1-A4 四通道规范名三口径过；A5 跨通道；A6 伪装前缀；A7 文件名日期≠file_date；A8 规范名不存在（纯口径结构过/正式口径拒）；A9 目录冒充；A10 符号链接逃逸；A11 绝对路径；A12 ../与子目录；A13 .txt/.json.bak；A14 13月/02-30 日历非法；A15 三者匹配对照；A16 构建端 resolve_inputs 同规（目录/伪装/非JSON/链接不选，真实规范回退文件照选）。全部同时执行 ssp 直调+recompute+gate_status（E 另验下游预检）。

## 9. EXACT/FALLBACK 边界测试（B 矩阵）

四通道各：真实构建 lag=1（PASS）与 lag=窗口边界（来源层接受，结构可证明；数据陈旧度按既有质量语义另行裁决——两类语义不混同）；篡改 lag=窗口+1 与 115 天（自报自洽仍拒）；EXACT 前一日文件/文件名与 file_date 冲突；FALLBACK 缺 lag/自报不符/未来日期/日期字段非法；观测日(2026-10-23 收盘)≠批次日(20261024)合法对照。

## 10. collector 非法类型测试（C 矩阵）

原始 SPX 与派生 REAL_10Y 各注入：合法字符串/空串/None/列表/字典/数字/布尔 → 合法者零 collector 问题，非法者"collector非法类型/空"可诊断拒绝；`no_exception` 断言无未受控 TypeError；另测 source 非对象（无 AttributeError）、source.file 列表、端到端磁盘注入列表 collector→装配 exit2+预检拒。

## 11. MISSING/READ_FAIL 互斥测试（D 矩阵）

正常 MISSING（仅 status）/MISSING file=None（与缺失等价，固定构建器口径）/正常 READ_FAIL+error/EXACT 正常/FALLBACK 正常（含 disclosure）为合法对照；MISSING+file 字符串·列表·字典、+file_date、+lag_days；READ_FAIL 缺 error、error 非字符串、+file、+file_date、+lag_days；EXACT+lag_days、EXACT+error、FALLBACK+error 全拒；真实构建非核心缺失（UMCSENT）仍 DEGRADED 披露、核心通道缺失（china）仍按核心规则 FAIL——fail-closed 不误伤合法降级。

## 12. 原始 14 项 E2E 结果

`tests/test_e2e_frozen14.py` 33/33、`tests/test_e2e_orig14.py` 41/41、`tests/test_e2e_four_weeks.py` 59/59——E2E-01~14 场景含义未改（01 正常全流程/02 非核心缺失降级/03 核心失败阻断/04 FAIL 时 GLM=0/05~07 旧包与修订/08 来源冲突/09 合法 DEGRADED 发布/10 GateB FAIL 禁回写/11 采集失败 SKIPPED/12 混合预测/13 锚点残留/14 报告保护）；本轮新增反向用例（跨通道/115天/目录/列表collector/互斥违背）在 test_p01_fix6.py，未改原始编号。

## 13. 全部适用离线测试结果（本轮实际执行，2026-10-28）

命令：`for f in tests/test_*.py; do python3 "$f"; done`

| 套件 | 结果 | 套件 | 结果 |
|---|---|---|---|
| test_datafix_20261017 | 13/0 | test_p0_fixes | 22/0 |
| test_e2e_four_weeks | 59/0 | test_p1_fixes | 36/0 |
| test_e2e_frozen14 | 33/0 | test_p2_fixes | 82/0 |
| test_e2e_orig14 | 41/0 | test_p4_fixes | 43/0 |
| test_fact_engine | 60/0 | test_p7_fixes | 30/0 |
| test_gate_chain_p01 | 86/0 | test_phase3 | 47/0 |
| test_glm_live | **跳过**（RUN_GLM_LIVE=1 门控，付费真实 API，离线默认不跑） | test_phase4 | 20/0 |
| test_p01_fix1 | 82/0 | test_round3_adversarial | 24/0 |
| test_p01_fix2 | 109/0 | test_round3_p0 | 91/0 |
| test_p01_fix3 | 45/0 | test_round4 | 94/0 |
| test_p01_fix4 | 49/0 | test_round5 | 64/0 |
| test_p01_fix5 | 62/0 | test_round6 | 51/0 |
| test_p01_fix6（本轮新增） | 86/0 | test_snapshot | 46/0 |

- 统计口径（如实区分）：**测试文件 26 个；全部 26 套实际执行且 exit 0（其中 test_glm_live 按约定自跳过内容）；逐项断言/检查合计 1375 通过 / 0 失败**（=上表 25 个计数套件之和；glm_live 无断言计数）。不引用 FIX5 的 24 套/1289 项冒充本轮结果。
- 诚实声明：逐断言计数来自本机实际执行日志；GitHub Actions（§14）验证 26 套退出码（0），两者口径不同，均如实报告。

## 14. GitHub Actions 真实运行

- 实现 commit `1e4b8b3b4a7a647ad6e1a439edea10a610e802b7` 的运行：offline-tests **#11**（run id 40635967351）——结论 **Success**，45s
  链接：https://github.com/bojing951-hash/investment-agent/actions/runs/40635967351
- 文档 commit（B）的运行：B 推送后触发，链接与结论在最终开发回复中报告（本文件无法自含其自身推送后的运行）
- FIX5 的 run 40544890781 仅作历史证据，本轮不复用

## 15. 尚未验证或仍然存在的问题

1. test_glm_live 真实付费 GLM 冒烟未离线运行（环境门控；本轮 GLM 相关仅 mock 网络侧验证预检先行/GLM=0，真实 API 质量未重测）。
2. 采集器键名桥接（MARGIN_BAL/SH_PE 的 rzye_billion/pe_ttm→balance/pe）仍未整改——生产持续诚实 DEGRADED 披露（本轮 20261028 快照亦然），属既有遗留非本轮缺陷。
3. 硬链接无法被 realpath 检测（符号链接/别名已拒）；规范文件实体核验覆盖 isfile/islink/realpath 三层，硬链接场景未构造测试（本地正式流程无此形态）。
4. data_dir=None 纯历史重验口径不核验文件实体（契约定义的证据范围边界，非缺陷；两种口径结论在文档与代码 docstring 显式区分）。

## 16. 历史数据兼容与部署注意事项

- 生产只读复算（2026-10-28，12 份线上快照 20261017~20261028）：FIX6 全部新校验 **0 illegal、0 sources_problems**（带/不带 data_dir 双口径一致）——历史快照零误伤、无需改写；1017/1023 声明 PASS 复算 DEGRADED 与 1024~1026 DEGRADED 均为 FIX4 起已披露的非核心缺失口径，保持原样；20261028（今晨）声明=复算=DEGRADED 一致。
- 生产 FALLBACK 历史值全部 ≤ 通道窗口（构建端 resolve_inputs 一直按窗口选取，本轮验证端与构建端同源化后天然一致）。
- 部署：实现 commit 已含全部代码变更；生产目录同步与 launchd 未自动变更（按禁令，生产同步由开发流程外完成并在最终回复报告）。历史快照若未来被新校验判不可证明，按契约标记"未验证"，绝不自动重写或伪造。

---

**开发自检结论**：IA-F5-DEF-001/002/003 已按 IA-P0-1-FIX6-AC-v1.0 实现；26 套离线测试（含原始 14 项 E2E 与新增 86 项对抗矩阵）本轮实际执行全绿；生产 12 份快照只读复算零误伤。本报告为开发自检，P0-1 最终结论以独立 Agent 4 验收为准（READY FOR INDEPENDENT ACCEPTANCE）。
