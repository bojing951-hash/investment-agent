# Audit-R9 第九轮审计修复报告(R53)

- 基线: `a4fb7c7a13c5ab40890ea4727ff8ae70297fe714`(PR #1 第八轮 CI 回填尖)
- 修复提交(执行代码版本,固定 SHA): **`74fb612`**(dev/audit-fix-r1;全文 SHA 见 CI/仓库)
- 范围: 仅关闭 R9-01、R9-02;目标、研究能力、统计口径不变;不扩功能、不瘦身、不降验收
- 判定口径: 33 判据新门(`tests/test_audit_r9_gate.py`,33/0)+ 电池 182 件直跑 181 绿(phase6 册内既档红,提交后复跑 rc=0 绿——182/182)+ 复放四包(BLIND/F10/新 B/e2e-corrected 全 PASS)

---

## R9-01 有效观测规则覆盖全部数据路径

**原问题**(基线 a4fb7c7 复现,/tmp/r9_repro.py 8 例全 BASELINE-BUG): 生产链路「真实格式 macro 文件→build_snapshot→series_store→workbench/history→data_requirements→report→archive」中,「研究 CN_PMI_MFG 的变化」(未限定)以下输入全被记 n=226、satisfied、报告归档通过——①226 日期值全 NaN(有效 0);②全 Infinity;③全 null;④225 null+仅末值有效(有效 1);⑤226 条同一天重复观测(有效去重 1)。同类输入在「近五年」已可阻断(R8),剩余缺口=快照直读(merge_macro_series/metric_series/判定器直信原始数组)与 max_available 绕过统一清洗;另 S4 信封声明 n 被信任(声明 226+全 NaN 数组→satisfied)。

**修改位置**:
| 文件 | 修改 |
| --- | --- |
| `scripts/research_history_query.py` | 新增 `effective_series(dates, values)` 公共入口=**唯一有效观测清洗规则**(内部即 R8 `_clean_series`: 合法 ISO 日期+有限数值+同日去重留末+长度错配短侧配对+六键登记;值精度原样)——快照构建/工作台读取/需求判定/查询 loader 四路同一实现,不另立副本 |
| `scripts/snapshot_builder.py` | `merge_series_sections`(japan/ea/shiller)与 `merge_macro_series` 入 store 前统一清洗(函数内导入防环 rhq→sb): 等长前置条件撤除,改短侧配对如实登记;坏值序列不入场,n 不以原始数组长度冒充;`merge_macro_series` 新增 `clean_out` 出参→`build_snapshot` 写入快照顶层平节 **`series_store_clean`**(raw_n+六键核验披露);序列未入档则注记/provenance 同不入(防孤儿,既有纪律保持) |
| `scripts/workbench_data.py` | `metric_series` 快照分支过同一清洗: n=0 诚实拒答(不再返回坏值面)、`series_clean` 披露(raw_n+六键)、`collection_status` 末观测取清洗后末观测;`series_capable_metrics` 两面(快照/采集档)first/last/n 统计取自有效序列 |
| `scripts/research_orchestrator.py` | `_evaluate_data_requirements`: 快照直读 `_n_series/_first/_last` 取自清洗后序列(`_ser_face_present`=原始面在场);S4 信封面吃 dates/values 数组经同一清洗,**不信任声明 n/first/last**(生产 ia_cli cmd_history 信封恒携全长数组,声明字段仅披露用;dates 为 list 含空=面在场=探测发生过,有效 0 走据实分支不误标「均缺席」;dates 缺席=覆盖不可核验,声明 n 不采信);建档清洗后未入 store 的序列由快照 `series_store_clean` 披露面据实分类(「序列面在场但有效观测 0」) |

**交叉验收矩阵**(§M,`tests/test_audit_r9_gate.py` 33 判据;每格经生产读取→查询→需求判定→交付门,非辅助函数直证):

| 数据状态 \ (路径×范围) | 快照×近五年 | 快照×未限定 | 采集档×近五年 | 采集档×未限定 |
| --- | --- | --- | --- | --- |
| 正常真实序列(226) | satisfied n_in=59 | satisfied n=226 | satisfied n_in=59 | satisfied n=226 |
| 全 NaN×226 | 阻断 | 阻断(面在场有效 0) | 阻断 | 阻断(面在场有效 0) |
| 全 ±Infinity×226 | 阻断 | 阻断(同上) | 阻断 | 阻断(同上) |
| 全 null×226 | 阻断 | 阻断(同上) | 阻断 | 阻断(同上) |
| 长度错配(227 日期/226 值) | satisfied n_in=59 | satisfied n=226 | satisfied n_in=59 | satisfied n=226(短侧配对+登记 1,末位未配对日期不冒充) |
| 仅 1 个有效观测 | 阻断 n_in=1 | 阻断 n=1<12 | 阻断 | 阻断 |
| 大量重复日期(226 同日) | 阻断 n_in=1 | 阻断 n=1 | 阻断 | 阻断 |
| 合理少量缺失(6 散点 null) | satisfied n_in=56(非 59) | satisfied n=220 | satisfied n_in=56 | satisfied n=220 |

- 附 M-mm2(尾截断错配 226/225=丢最新值): 显式窗「窗内末观测 2026-09-01 早于窗止−75 天容忍」阻断+未限定路径 stale_for_task(R7-02 三级阻断)——**首败记录**: 首跑曾按 satisfied 预期失败,复核为生产正确判定(错配吞最新值=端覆盖与新鲜度据实失败),期望据实修正并入册
- M-b 信封声明 n=226+全 NaN 数组 → 阻断+「有效观测 0」入据(声明 n 不采信)
- M-c 快照全 NaN 未限定 → 「序列面在场但有效观测 0」据实(不误标均缺席)+`series_store_clean` raw_n=226 在场
- §G 生产门: 快照全 NaN 规格→report 拒+archive 拒;真实格式注入经生产 `save_macro`+`merge_cn_history` 写档,合成裁决仅用于 G4 正例身份标记(`R9-GATE`),不冒充真实独立审查
- §S 披露: 错配双层披露(建档面 `series_store_clean` mismatch=1/raw_n=227→226+读面 `series_clean` n=226);重复日期去重留末值 `50.123456789123` 逐位保留

**执行代码版本**: `74fb612`
**证据路径**: `tests/test_audit_r9_gate.py`(§M×19+§Y×7+§G×4+§S×3);反例复现脚本 `/tmp/r9_repro.py`(基线 8/8 BASELINE-BUG→修复后 8/8 fixed)
**状态**: 已实现+离线通过

## R9-02 时间要求无法解析时明确阻断

**原问题**(反例 A/B,基线复现): 无匹配日期词形时 `_question_window` 直接返回 None,把「有时间要求但未解析」混同于「没有时间要求」——A:「研究前年 CN_PMI_MFG 的变化」(时点 2026-11-17,仅 2025-11..2026-10 十二观测,2024 无数据)经 max_available 交付;B:「研究过去六个月 …」(2021-11 前史+2026-10 一点共 168 点,最近六个月仅 1 点)同误放行。

**修改位置**(`scripts/research_orchestrator.py`):
- **三态固定**: ①未指定范围(None,唯一允许 max_available)②已指定且成功解析(explicit/relative/relative_months/calendar_year)③已指定但无法解析(unparseable 阻断);时间**意图识别与窗口解析分离**
- `_RANGE_MONTHS_RE`+`_question_range_months`+`_shift_months`: 近/最近/过去 N 个月、N 个月以内/以来/内 → `relative_months`(研究时点倒推 N 个自然月,日按目标月长收敛;**相对时间绑定研究时点,不用系统当前时间**;时点不可核验=窗口不可核验阻断,不回落)
- 「前年」→ `calendar_year offset -2`(负向后视 `(?<!大)` 防「大前年」误切;大前年在未支持表)
- `_QTIME_UNSUPPORTED_RE`: 未支持时间词——今年/明年/后年/大前年/上半年/下半年/年初/年中/年末/月初/月底/月末、上/本/下/这(个)季度、上周/本周/这周/下周(`(?!期)` 防上周期)、上(个)月/本月/这(个)月/下(个)月/当月、近/最近/过去 N 周/星期/天/日、N 周/天 以内/以来/内、未来/接下来/此后 N 年/月/周/天/日——→ unparseable 带「请改用明确日期区间或受支持表达」提示;**单日期提及≠区间,但未支持时间词在场=时间意图未解析**(同判阻断);显式日期区间在场时区间胜(更具体)
- 判定器 `relative_months` 分支: 窗=[as_of−N 月, as_of];`unparseable` basis 贯通提示词

**验收**(§Y):
- Y1 反例 A: 「前年」+12 月数据 → 窗 2024-01-01..2024-12-31,窗内 0 阻断(window≠max_available)——**误放行关闭**
- Y2 反例 B: 「过去六个月」+168 点 → 窗 2026-05-17..2026-11-17,窗内 1 阻断——**误放行关闭**
- Y3 未支持表达 19 词形解析层 unparseable+提示,判定层四代表词(今年/上周/近三十天/未来三个月)阻断——**非两特例**
- Y4 资产名护栏: 十年期美债/上周期值/中美利差/十年期与两年期利差 → 未指定范围(任务时间要求与资产名称区分)
- Y5 正例保留 11 形: ISO 区间/斜杠区间/近五年/近十年/去年/前年(2024 窗内 12 satisfied)/过去六个月(窗内 5=窗起 2026-05-17 后的 6..10 月,诚实计数)/以来/截至/未限定(max_available)/2021-01-15 合法回放 全 satisfied
- Y6 研究时点不可核验+过去六个月 → 「相对月窗无法判定」阻断(非系统当前时间)
- Y7 解析器: 前年=-2/大前年=未支持/近六个月·六个月内·过去 12 个月=relative_months
- §G: 前年规格/近六月 168 点规格 → report 拒+archive 拒(检查最终 report/archive,非仅解析结果);近六月全量 → deliverable(正例对照)

**执行代码版本**: `74fb612`
**证据路径**: `tests/test_audit_r9_gate.py` §Y×7+§G×3
**状态**: 已实现+离线通过

---

## 三、保留已关闭成果(零回退核验)

R8-03 两轮实采证据包原样保留(本轮未重复采集);陈旧续用警告与 `stale_for_task` 阻断(M-mm2 复证)/合理续用与历史回放(Y5 as_of=2021)/中国历史连续采集与美国刷新后保留(R7 证据)/裁决身份、算法、前驱、摘要及篡改检查(R6-03 门绿)/required 阻断与 optional 降级/新版中国 B 与 E2E 统计(重放复证)——**复放四包**: BLIND `feaa1536…` PASS、F10 `6e5fcf4a…` PASS、新 B `recompute_r6b.py` 105/105 rc=0、e2e-corrected `independent_recompute.py` PASS;旧 B 包(035814Z)三失配=R6 既档 CONTRADICTED 保全态(标 NOT_VERIFIED,新链替代),非本轮回归。电池+七门(r4/r5/r6/r7/r8/r9/t3/r42)全绿。

## 四、夹具对齐记录(语义不降)

| 套件 | 对齐 | 理由 |
| --- | --- | --- |
| `tests/test_audit_r4_gate.py` | `_s4_step` 信封携带 dates/values 数组(合法 ISO 日序);N_snap 快照日期 `['d']*2514`→合法 ISO | R9-01 判定器不采信声明 n;非法日期面在新规则下=0 有效(判据语义 n≥min→satisfied 不变) |
| `tests/test_audit_r5_gate.py` | S4 用例 `s4('TEST_M0', 100, freq='daily')` 补 first/last(生产信封形态) | 同上;不带 dates 的窗口负例(§S 既档判据)原样保留 |
| `tests/test_arch_reform_t3_series.py` | 等长破坏 SOFR 从「整段跳过」改「短侧配对入档 5 有效+注记随入」 | R9-01 统一规则明确长度错配处理=短侧配对+登记(R8 先例),不再整段拒绝;泛化门/权属门/别名/先占/values verbatim 判据不变 |

## 五、CI 与四态汇总

- CI: 终 HEAD(报告+状态收口尖)见下方回填;代码修复提交 `74fb612` 为其第一父
- 已实现: R9-01/R9-02 全部代码修改+统一规则+披露面
- 离线通过: 33 判据门+电池 182 件 181 绿(phase6 提交后绿=182/182)+复放四包
- 在线通过: 本轮无新采集(指令: R8-03 已过外审,不重复无关采集)
- 尚未验证: 无(NOT_VERIFIED 项为零;真实外部依赖无阻塞)

## 剩余限制

- 未支持时间词表为确定性词面匹配,非自然语言全覆盖——不支持时诚实失败+改写提示(指令⑦口径),不猜
- 「近六月」(无「个」量词)歧义于六月,不解析(维持未指定);月份量词须「N 个月」形态
- 旧 B 包(035814Z)CONTRADICTED 保全态沿 R6 注记,由新 B 链(083954Z,105/105)替代
- 本轮不合并 PR、不部署、不开新功能轮次——停等外部最终审计

## CI 回填

(推送后回填)
