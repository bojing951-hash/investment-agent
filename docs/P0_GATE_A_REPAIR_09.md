# P0 Gate A 修复报告 09（FIX9：可信根入口授权收紧 + 保护测试证据修复）

- 契约：IA-P0-1-FIX9-AC-v1.0（本轮）；IA-P0-1-AC-v1.0 及 FIX1~FIX8-AC 全部继续冻结有效，未降低任何阈值
- 角色：开发（本轮自检）；独立验收由 Agent 4 另行执行
- 日期：2026-10-28
- 分支：main

## 1. 开发前 Commit

- dev-before：`52a490a97a813ad7ba232a0fdb1ec45065893a62`（FIX8 终 HEAD，本轮指令固定基线；独立验收 FAIL 定点）
- FIX8 实现：`a950a68b9c7868b4e81bd9dd6f6a1cc28eeb1b04`；原始审计基线 `844fd3bef5e1e7e17b4d333278acd319f1dbae41`（不变）
- 基线状态：本地 HEAD=远程 HEAD=52a490a，工作区干净，无未知修改

## 2. 实现 Commit

- `261113ff1f4a3e04b071f6ccd5429c2afad10aa9`（代码+测试，3 文件 +729/−78：research_provenance.py、test_p01_fix8.py 重构 G 节、test_p01_fix9.py 新增）

## 3. 最终交付 Commit

- 文档 Commit B = 本提交（docs only）；SHA 与 Actions 运行在推送后于最终开发回复中给出（不预填）

## 4. IA-F8-DEF-001 的代码修复（已证实实际代码缺陷）

**缺陷**：FIX8 的词法-物理前缀回退遍历**被验证 data_dir 自身的前缀**——任何外部符号链接只要 realpath 恰等于可信项目根，就被临时授予可信入口身份。§6.2 固定反例（`UNAPPROVED-external-link-to-project-root → <tmp>/project`，传入 `<link>/data/daily`：文件物理在根内、文件名/内容合法、realpath 落点在根内、终文件非链接、SHA 正确）在修复前被放行（本机复现：`trusted_dir_problems` 返回空）。

**修复（FIX9-01）**：删除动态前缀发现，改为**预先确定的可信入口集合** `_trusted_entry_forms(rt)`——集合只由三类与 data_dir 无关的来源推导：
1. 可信根物理路径（realpath 锚）本身；
2. 代码位置推导的项目根**词法形式**（仅当其 realpath==物理锚时加入）；
3. 封闭常量表 `_SYSTEM_PREFIX_ALIASES`（/tmp、/var、/etc ↔ /private/\*，仅 `sys.platform=='darwin'` 参与推导）对可信根做系统级前缀变换得到的形式，且运行时逐个验证 realpath 回指物理锚。

data_dir 必须词法位于某一入口之下（或恰等于入口），再经入口以下逐组件 islink 审计 + realpath 物理包含 + isdir。**realpath(候选前缀)==可信根不再构成任何授权**。修复后反例拒绝，消息注明 FIX9-01/IA-F8-DEF-001。

## 5. 根级别外部链接反例复现

test_p01_fix9.py A2/A2b：精确目录名 `UNAPPROVED-external-link-to-project-root`；先证明前提（realpath 在根内、文件规范可读），再证 `trusted_dir_problems` 拒；A10 证明即使文件物理在根内、SHA 可算，经未批准入口的 `resolve_inputs` 仍全通道不选（来源身份=入口授权，非文件内容）。D 节对该场景执行完整真实链路（见 §9/§11）。

## 6. 可信入口授权规则

入口集合封闭于三类来源（§4）；匹配规则=最长入口前缀匹配；入口以下组件逐级非符号链接；物理包含锚兜底。**没有**用户批准的外部存储白名单，本轮未新增任何白名单机制；显式 `trusted_root` 测试参数仍只定义根，不能凭空授权根外链接（fix9-A 全矩阵 + fix8 A/B/G 节回归证明）。

## 7. macOS 系统级别名兼容说明（FIX9-02）

- 系统**根级**符号链接（/tmp→private/tmp 等）创建属系统管理员权限行为，与用户级 `ln -s` 有本质区别——封闭表只收录这三条 macOS 惯例别名。
- 用户/进程在任何非根位置自建的链接（无论命名多像系统别名）不入表、不参与入口推导（fix9-B4 用 fixture 内复刻的 fakePrivate/fakeAlias 结构证明）。
- **macOS 真机验证**：本开发机（Darwin 24.6.0）实测通过——B3/B3b（/var↔/private/var 真实双向互认、入口集合含 /var 形式）、fix8-F1/F3（平铺沙箱 data_dir==可信根、双向形态），29 套全量回归亦在本机跑绿。
- **Linux（GitHub Actions）**：表不参与（平台分流），入口=物理锚+代码词法形式；fix9-B3 的非 darwin 分支断言 /tmp 别名形式不出现在入口集合。CI 无法真实复现 /private 别名——该部分证据=开发者本机自检 + 封闭表单元断言（B5），**未虚报已在 CI 验证 macOS 行为**。

## 8. 原始 symlink/.. 回归

fix9-C（FIX6 data→outside / FIX7 alias/../data/daily / 项目外绝对 / 穿越 / 文件链接 / 目录冒充 / 来源缺失 / 错误通道，8 项代表）+ fix8 A~D 全矩阵原样保留并通过；FIX8 external-link→project/data（A3）保持拒。symlink/.. 拒绝能力未降低。

## 9. 构建端和消费端的路径一致性（FIX9-03 保持）

- 可信检查先于文件访问：`resolve_inputs` 未获授权即返回全缺源、不读任何文件（A10/D3/E1）；
- `trusted_source_dir()` 未授权返回 (None, problems)（D2）；
- 一切文件 IO 用已验证物理路径（FIX8-03 设计未动）；
- 新入口逻辑未引入检查/访问分叉：入口集合匹配仍发生在 trusted_dir_problems 内部，verified 输出仍为 realpath 物理形态；
- 无 caller 可用不可信路径自行确定可信根（da/rg=模块常量 DATA_DIR 锚，dpo=缺省代码锚，rda=--trusted-root 显式授权；fix8-I1/I2/I3 全部保持通过）。

## 10. G4 原测试为什么无效（已修复的测试缺陷）

- **缺陷 A（基线时机）**：原 G4 在 `generate_weekly_report()` 执行**之后**才连续采集 before/after——两份摘要都只覆盖操作后状态，即使被测操作改写了文件也无法发现。
- **缺陷 B（保护对象不合格）**：原状态 fixture 写的是 `publication: 'published'` 字符串字段，而正式读取器要求 `published: true`（布尔）+ `report_digest`（与实际文件摘要一致）+ report_file/target_date/report_path 全套身份字段——该 fixture 从未被 `formal_report_view()` 接受过，不是有效的已认证历史周报。
- **无生产损害证据**：该缺陷只存在于测试fixture，验收与自检均未发现生产状态文件被实际破坏。

## 11. 新 G4 合格正式报告前置检查 + 执行前后摘要

- **真实发布事务**（fix8-G0/fix9-E0）：合格研究日经**真实** `generate_weekly_report()`（GLM mock≥500 字符、validate mock PASS，其余真实）发布 → 真实 `write_report_status()` 产生 `published: true` + `report_digest`；
- **前置断言**（G0b/E0b）：`rp.formal_report_view(REP)` 必须返回非 None，否则该测试 FAIL、不继续当保护对象（实测通过）；
- **执行前基线** `baseline_before`：4 对象（报告/状态/thesis/views）SHA-256 在**任何**攻击操作之前采集；
- **实际执行动作**（时钟固定，发布日 20261024 < 攻击日）：恶意源快照构建（sb）→ Gate A（sources_status/recompute/gate_status）→ 数据装配（da.main）→ 周报预检+生成入口（rg）→ GLM 计数；
- **执行后** `actual_after`：摘要逐一比对（相等）；报告仍被 formal_report_view 接受；scan_formal_weekly_reports 结果不变；无新 weekly_report_*/report_status_*；published=true 仅发布日；apply_status_updates 零次；GLM=0；
- **篡改自检**（G5/E5，独立夹具）：有意篡改一个对象证明比较机制能发现变化、不误报未动对象。

## 12. 原始 14 项 E2E

test_e2e_frozen14（33/0）+ orig14（41/0）+ four_weeks（59/0）本轮全量重跑通过，含义未改；FIX9 新测试独立编号（fix9 A~E），未替代任何 E2E 编号。

## 13. 全部适用离线测试（本轮实际执行）

**29 套执行 / 0 跳过 / 全部 exit 0**（本机 Python 3.9.21 + macOS Darwin 24.6.0，2026-10-28；test_glm_live 离线契约自跳过真实付费调用、套件 exit 0，如实说明）：

test_datafix_20261017、test_e2e_four_weeks、test_e2e_frozen14、test_e2e_orig14、test_fact_engine、test_gate_chain_p01、test_glm_live(离线自跳过)、test_p01_fix1~fix8、**test_p01_fix9（新增）**、test_p0/p1/p2/p4/p7_fixes、test_phase3、test_phase4、test_round3_adversarial、test_round3_p0、test_round4、test_round5、test_round6、test_snapshot。

本轮新增检查 **42** 项（fix9）+ fix8 G 节重构后由 49→**52** 项（G0/G0b/G5 新增，基线时机与正式身份修复）；两次连续运行幂等验证通过（修复了常量符号链接名导致的二次运行冲突）。无删除/削弱任何负向断言（diff 可核）。

## 14. GitHub Actions

`.github/workflows/offline-tests.yml` 未改动（glob 自动纳入 test_p01_fix9.py）。新最终 Commit 的真实运行链接在推送后于最终开发回复给出；不以 FIX8 历史绿灯（run 40666376085）代替本轮验证。

## 15. 历史来源摘要边界（不变）

新快照 FIX7-05 SHA-256 内容绑定原样保留（fix8-H1/H2 回归通过）；FIX7 之前历史快照无 sha256 的可信度局限照旧如实记录，不自动改写、不伪造、不宣称已完整验证；本轮未重建/迁移历史数据。

## 16. 仍未完成的非阻断性项目

- Windows 路径分隔符仅字符串层归一后的 `..` 检查，未在 Windows 文件系统实测（生产为 macOS/Linux）。
- 硬链接替换不可检测（FIX7 已记录，静态路径授权范围外，本轮指令明确不扩项）。
- macOS /private 别名的 **CI 环境证据**无法产生（CI 为 Linux）——macOS 侧行为由开发者本机实测+封闭表断言覆盖，若验收要求 CI 级 macOS 证据需另立 macOS runner（超出本轮范围）。

## 17. 生产部署注意事项

- 行为无生产影响变化：生产采集路径为项目内词法路径（无外部链接、无 `..`），入口集合第一类（物理锚）即覆盖；上线 `research_provenance.py` 后建议人工跑一次 `snapshot_builder` 确认当日 Gate A 结果与旧版一致。
- `real_data_acceptance` 验收线上数据仍须显式 `--trusted-root`（FIX8 起）。
- 任何外部存储接入需求仍走显式可信根配置评审，不存在运行时白名单。

## 18. 证据分级（按指令要求区分）

- **已证实实际代码缺陷并修复**：IA-F8-DEF-001（§4/§5，本机复现修复前后行为）。
- **已修复的测试缺陷（无生产损害证据）**：FIX8-G4-EVIDENCE（§10/§11）。
- **仅由开发者自检证明**：macOS /private 别名真机行为（B3/B3b、29 套本机回归）；全量套件计数。
- **由 GitHub CI 确认**：Linux 环境全部 29 套（含 fix9）通过（链接见最终回复）。
- **尚未在 macOS 真机验证**：无——macOS 侧行为已在开发机实测；未能覆盖的是 macOS 的 **CI 级**自动验证（见 §16）。
