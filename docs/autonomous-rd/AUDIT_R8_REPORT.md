# Audit-R8 第八轮审计修复报告(R52)

- 基线: `25f079f41dde2dfa34960b6c9055e4e3e8fc3549`(PR #1 第七轮收口尖)
- 修复提交(执行代码版本,固定 SHA): **`d3c3dc0aa351f4496522e5bee57a9c12f1ef5593`**(dev/audit-fix-r1)
- 范围: 仅关闭 R8-01/R8-02/R8-03,不扩功能、不瘦身、不降验收
- 判定口径: 30 判据新门(`tests/test_audit_r8_gate.py`,30/0)+ 电池 181 件直跑 180 绿(+1 册内既有红 `test_arch_reform_phase6`,整改树工作面净设计行为,提交后复跑 29/0 绿)

---

## R8-01 无效数值不得计入有效覆盖

**原问题**(基线复现,/tmp 六反例): PMI 226 日期 values 全 `"NaN"` 或全 `"Infinity"` 时有效数值 0,系统记近五年有效观测 59 并通过 `history`/report/archive;S4 信封保留日期 values=null 时窗口函数以 1.0 占位仍判覆盖满足。

**修改位置**:
| 文件 | 修改 |
| --- | --- |
| `scripts/research_history_query.py` | `_clean_series` 重写+`_valid_series_date`: 有效观测=合法日期(str[:10] fromisoformat)+有限数值(float 可转且非 NaN/±Inf);values=None=无有效数值面禁占位;长度错配按短侧配对如实登记;重复日期去重留末值;登记扩六键;合法数值原始精度保留(不改统计口径) |
| `scripts/research_orchestrator.py` | `_effective_window_obs`: 删 1.0 占位(values 缺失即无有效观测);非有限值剔除计数;`n_length_mismatch` 登记。终判链增「序列面在场但有效观测 0」据实分支(不再误标「均缺席」) |
| `scripts/china_market_collector.py` | 五处 NaN 检查点统一为非有限值检查(±Inf 同不入采集史;`_macro_month_rows` 纯函数) |

**反例结果**(V1-V6/V10-V11,真实格式原始文件→生产采集→查询→判定→交付门):
- 全 `"NaN"`×226 → 查询有效观测 0,`n_nonfinite_dropped=226`,判定 `insufficient_coverage`,report/archive 双拒(G1)
- 全 `"Infinity"`/`"-Infinity"` → 同上阻断(V2)
- 信封 values=null → 禁占位,`n_in_window=0` 阻断(V4)
- 全 null → `n_missing_dropped=226` 阻断(V6);max_available 未限定路径同规则阻断+据实入据「序列面在场但有效观测 0」(V10)
- 长度错配 226/225 → `n_length_mismatch=1`+有效 225(V5);非法日期 `2026-13-01` → 剔除登记 1(V11)

**正例结果**(V7-V9):
- 部分缺失 4 散点月 null → 窗内有效 55(非 59)按实际数量判,≥半额下界仍满足(V7a);窗内仅 2 有效 → 阻断(V7b)
- 重复日期 227 行含 1 重复 → 去重 226+留末值,`50.123456789123` 原始精度回读逐位一致(V8)
- 正常真实数据 226 观测逐位回读+近五年 satisfied(V9)

**执行代码版本**: `d3c3dc0aa351f4496522e5bee57a9c12f1ef5593`
**证据路径**: `tests/test_audit_r8_gate.py`(§V×11 判据);真实格式注入经生产 `save_macro`+`merge_cn_history` 写档,合成裁决仅用于 G3 正例身份标记(`R8-GATE`),不冒充真实独立审查
**状态**: 已实现+离线通过+在线通过(两轮实采 CN n=226 全史 fresh,见 R8-03)

## R8-02 时间要求不得静默丢失

**原问题**: 「研究 2020/01/01 至 2025/12/31 的 CN_PMI_MFG 变化」(斜杠日期)与「研究去年 CN_PMI_MFG 的变化」在仅 12 个月数据时均退化为 max_available 并交付;「截至2025年12月」解析层合法单侧窗但后续 start=null 无条件阻断,与声明支持不一致。

**修改位置**(`scripts/research_orchestrator.py`):
- `_QDATE_TOKEN_RE`+`_norm_qdate`: 增斜杠词形(`YYYY/M/D` 与 `YYYY/M`,止侧月末补齐)
- `_question_window`: 「去年」→ `calendar_year{offset:-1}` 绑定研究时点([Y-1-01-01, Y-1-12-31];时点不可核验=窗口不可核验,不回落);三态=未指定 None/已解析 explicit·relative·calendar_year/无法解析 unparseable(阻断不落 max_available)
- 单侧终界(`截至X`): 判定期窗起=实际序列首观测回填(`_win_single_end`,basis 注记「单侧终界: 窗起=实际序列首观测」);数据全在界后=窗内 0 诚实阻断

**反例结果**(W3/W4/W6/W9):
- 斜杠区间+12 个月数据 → 窗 2020-01-01..2025-12-31,窗内 2 阻断,report/archive 双拒(G2)——不再退化 max_available
- 「去年」+12 个月数据 → 窗 2025 自然年,窗内 2 阻断(W4)
- 「截至X」数据全在界后(2026-01..10)→ 窗内 0 阻断(W6);指定但无法解析(`2020年13月1日`)→ 阻断+「无法解析」入据(W9)

**正例结果**(W1/W2/W5/W7/W8):
- 解析器: 斜杠全日期/斜杠年月/斜杠+ISO 混排/「截至2025/12」斜止单侧 全部正确归一;斜杠非法月 `2020/13/01` → unparseable(W1a-d,W2a-b)
- 「截至2025年12月」+全量数据 → satisfied(窗起=首观测 2008-01-01,末窗内 2025-12-01)且生产门可交付(G3)——不再无条件拒
- 既有行为保留: ISO 区间/近五年/近十年/「以来」/无限制/合法历史回放(as_of=2021-01-15)全 satisfied(W7);「去年」+全量数据 → 2025 自然年窗内 12 satisfied(W8)

**执行代码版本**: `d3c3dc0aa351f4496522e5bee57a9c12f1ef5593`
**证据路径**: `tests/test_audit_r8_gate.py`(§W×11+§G 正反例,检查最终 report/archive 非仅解析器)
**状态**: 已实现+离线通过

## R8-03 完整绑定实际执行代码和每轮输入

**原问题**: 第一轮新采集输入被第二轮覆盖;第二轮输入未随证据包保存;当时执行的是基线+未提交修改仅存差异哈希无可重建面;`_git_state` 用 `git diff HEAD` 时新增未跟踪源码不改变指纹。

**修改与执行**(外审指定最简可验证流程,逐步落实):
1. 代码修复提交固定 SHA: `d3c3dc0`(本轮三缺陷修复+门,先行提交)
2. 该提交干净检出执行两轮正式采集+刷新: `git worktree` detached@`d3c3dc0`,`git status --porcelain` 为空=零未提交修改
3. 每轮独立证据目录 `docs/autonomous-rd/r8-evidence/round{1,2}/`: 脱敏命令(`command.txt`)/时戳(`timestamps.txt`)/代码版本(`code_version.txt`: HEAD+`git ls-files -s` 清单 sha256+`_git_state` 三元组)/脱敏日志(`round.log`,密钥零出现断言)/原始输入(`round2/input_macro_20261117.json`,sha256 `951d7b51…`)/输出档(`output_macro_*.json`)/完整查询信封三指标+全长 sha256(`query_envelopes.json`)/`SHA256SUMS.txt`
4. 第二轮不覆盖第一轮: round1 目录重算对勘逐字节一致(ROUND1-INTACT);round2 输入=round1 输出(同哈希 `951d7b51…`),两轮面各自在场
5. 执行源码清单+内容指纹: `code_version.txt` 两轮均 `(d3c3dc0…, 'run_root', e3b0c442…)`——指纹=空差异+零未跟踪源码的 sha256(干净态的可验证证明)
6. 未提交修改零执行 + 指纹随未跟踪源码变化: `_git_state` 指纹纳入 `git ls-files --others --exclude-standard` 逐文件内容 sha256(B1 判据: 同 HEAD 下新增/改内容指纹各异;提交后身份移至 head、指纹归净);CODE_VERSION 印章三级链保持(B2)
7. 最终 HEAD CI: 见下节

**反例结果**: 基线缺陷(输入覆盖/指纹不变)在 B1/W 结构判据+两轮证据目录结构中直接证伪
**正例结果**: 两轮实采 rc=0(US 22 项+CN 226 月全史);round2 `collection_status.mode=fresh`(非续存)、`last_success_at` 12:13:22Z→12:14:46Z 前进、`source_sha256` 前移 `951d7b51…`→`1621cab9…`——连续采集成功、CN 不被美国刷新遮蔽(R6-02 语义复证)
**执行代码版本**: `d3c3dc0aa351f4496522e5bee57a9c12f1ef5593`(两轮同版,干净检出)
**证据路径**: `docs/autonomous-rd/r8-evidence/round{1,2}/`(9+11 件;FRED key=既有 LIVE 只读授权进程内注入,零落盘零日志,证据包值对值扫描零命中)
**状态**: 已实现+离线通过+在线通过

---

## 四、保留已通过项(零回退核验)

上轮三时间窗反例/陈旧续用警告与 `stale_for_task` 阻断/合理续用与合法回放(W7f as_of=2021 复验)/中国历史连续采集及美国刷新后保留(两轮实采复证)/裁决链身份与篡改检查/required 阻断与 optional 降级/新版中国 B 与 E2E 统计/研究席·独立审查席·归档复放——电池 180/181 绿+r7 门 37/0+r6 门 25/0+r5 门 30/0(修复后复跑)全数保持。

## 五、CI 与四态汇总

- CI: 终 HEAD `27e062b`(证据+报告+状态收口尖) run [44081929118](https://github.com/bojing951-hash/investment-agent/actions/runs/44081929118) 三 job(gates / tests 3.11 / tests 3.12)**全绿**(2026-11-17T12:22:34Z completed success);代码修复提交 `d3c3dc0` 为其第一父(单一连续波,无中间红)
- 已实现: R8-01/R8-02/R8-03 全部代码修改+统一规则
- 离线通过: 30 判据门+电池 181 件直跑 180 绿+1 册内既有红(phase6 提交后绿)
- 在线通过: 两轮真网实采(FRED 22 项+CN 226 月;信封/状态/哈希全链)
- 尚未验证: 无(NOT_VERIFIED 项为零;真实外部依赖无阻塞)

## 剩余限制

- `test_p03_e2ea.py` 断言按 R8-01 六键新契约更新(子集断言+新键在场,语义断言不降级)
- HY_OAS 族源端 3 年授权窗(ICE BofA)沿既有注记,与本轮无关
- 本轮不合并 PR、不部署、不开新功能轮次——停等外部最终审计
