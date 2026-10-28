# P0 Gate A 修复报告 10（FIX10：代码导入词法别名不得取得来源授权）

- 契约：IA-P0-1-FIX10-AC-v1.0（本轮）；IA-P0-1-AC-v1.0 及 FIX1~FIX9-AC 全部继续冻结有效，未降低任何阈值
- 角色：开发（本轮自检）；独立验收由 Agent 4 另行执行
- 日期：2026-10-28
- 分支：main

## 1. 开发前 Commit

- dev-before：`4ff6baeef053adc936326da1e5e201ffc5fed014`（FIX9 终 HEAD，本轮指令固定基线；独立验收 FAIL 定点）
- 原始审计基线 `844fd3bef5e1e7e17b4d333278acd319f1dbae41`（不变）
- 基线状态：本地 HEAD=远程 HEAD=4ff6bae，工作区干净，无未知修改

## 2. 实现 Commit

- `8ef6773ed951f6cf60cf58ec753c27492aa6ca62`（代码+测试，3 文件 +517/−27：research_provenance.py、test_p01_fix10.py 新增、test_p01_fix9.py fixture 修正）

## 3. 最终交付 Commit

- 文档 Commit B = 本提交（docs only）；SHA 与 Actions 运行在推送后于最终开发回复中给出（不预填）

## 4. IA-F9-DEF-001 的代码修复（已证实实际代码缺陷）

**缺陷**：FIX9 的 `_trusted_entry_forms(rt)` 第三来源"代码位置词法形式"——`cr = normpath(dirname(dirname(abspath(__file__))))`，当 `realpath(cr) == rt` 时加入入口集合。若代码**经未批准外部根级符号链接导入**（sys.path 含 `UNAPPROVED-external-link-to-project-root/scripts`），`__file__` 词法上穿过该链接，`cr` = 外链词法路径且 realpath 回指物理根——"代码恰好从那里被导入"使外链取得可信入口身份，`<link>/data/daily` 随之获得采集授权。指令指明 `if not os.path.islink(cr)` 式半措施不足（`external-link/scripts` 自身不是链接，链接在祖先），本轮未采用任何半措施。

**修复（FIX10-01）**：整段删除 `cr` 词法形式分支。入口集合封闭于**两类**与 data_dir、导入路径均无关的来源：
1. 可信根物理路径 rt 本身；
2. `_SYSTEM_PREFIX_ALIASES` 封闭常量表（darwin-only）对 rt 的系统级前缀变换，且逐个运行时验证 realpath 回指 rt。

`default_trusted_root()` 继续以 realpath(代码位置) 确定**物理根**（§6.2 允许项，未改）；`abspath(__file__)` 的**词法形态本身永不构成授权**。同一物理可信目录的授权结论在物理导入与别名导入下完全一致（fix10-A4 入口集合逐元素相等）。拒绝消息追加 FIX10-01/IA-F9-DEF-001 标注。

## 5. 双导入形态反例复现（FIX10-03，真实子进程标准 import）

隔离项目（mkdtemp 内）整目录复制**真实** `scripts/` + `config/` + `env_config.py`（不摘抄片段、不重写被测信任函数），写入 `data/daily/global_20261024.json`，建 `UNAPPROVED-external-link-to-project-root → project`。两个**独立 Python 子进程**（绝不共享 sys.modules）分别以 `PYTHONPATH=project/scripts` 与 `PYTHONPATH=<link>/scripts` 标准 `import research_provenance`，执行 `default_trusted_root()/_trusted_entry_forms()/trusted_dir_problems()/trusted_source_dir()`。修复前本机复现：B 形态入口集合含外链、`<link>/data/daily` 被放行（DEFECT）；修复后对照表：

| 场景 | 导入搜索路径 | 观测 `__file__`（词法） | 物理根推导 | 入口集合 | data_dir=物理 daily | data_dir=`<link>`/data/daily |
|---|---|---|---|---|---|---|
| A 物理导入 | `project/scripts` | `…/fix10-main-*/project/scripts/research_provenance.py` | `…/project`（/private 物理形态） | {物理锚, /var 别名形式} | 放行 | 拒绝 |
| B 外链导入 | `<link>/scripts` | `…/fix10-main-*/UNAPPROVED-external-link-to-project-root/scripts/research_provenance.py` | 同 A（realpath 一致） | **与 A 逐元素相等** | **仍放行** | **拒绝** |

- **词法条件真实触发**：两形态 `__file__` 词法不同且 B 穿过外链（A2 硬断言；CPython 对 PYTHONPATH 导入不做符号链接归一化，本机 3.9.21 与 CI 3.11 均成立——无需援引"环境限制"豁免）。
- 前置断言（A0）：链接存在且 realpath 指向 project、采集文件物理在 project 内、`project/scripts` 组件非链接。
- 同一物理模块文件：两形态 `realpath(__file__)` 相同（A3）。

## 6. 可信入口授权规则（收紧后）

入口集合封闭两类（§4）；匹配=最长入口前缀；入口以下逐组件 islink 审计；realpath 物理包含锚兜底；fail-closed 全链不变。**没有**为任何词法代码路径建白名单；`trusted_root` 显式参数仍只定义根、不能授权根外链接（fix10-B 全矩阵）。

## 7. macOS 系统级别名兼容（FIX10-02，未改动）

`_SYSTEM_PREFIX_ALIASES` 冻结三条（/tmp,/var,/etc ↔ /private/\*，darwin-only）原样保留；无动态扩充；用户级伪别名仍拒绝（fix10-C3）；两种导入形态观测的封闭表均==冻结常量（C4——导入路径不扩充系统前缀集合）。macOS 真机：C1 入口集合恰=物理锚+/var 形式、双向互认通过。

## 8. 原始 symlink/.. 回归

fix10-B：外链→project 根（B1）/→project/data（B2，FIX8 反例）/多级路径外链（B3）/项目内未批准链接→外部（B4）/外链+`..`（B5，词法 `..` 规范化前拒绝）/正常物理放行（B6）。FIX6/7/8/9 全矩阵经 fix9-C 与 fix8 A~D 原样回归通过；symlink/.. 拒绝能力未降低。

## 9. 调用链审计与生产启动兼容（FIX10-04）

- `rp.default_trusted_root()`：realpath 物理锚（允许保留项），未改。
- `da`/`rg`：可信根锚=模块 `DATA_DIR` 上级——别名导入下该锚词法=外链（或 `<link>/scripts/..` 形态），经根校验（根自身是符号链接/入口失配）**fail-closed**，绝不放行（fix10-D5/D6/D7 实测 exit 2）。
- `sb`/`dpo`：缺省 `rp.default_trusted_root()` 物理锚；外链词法 data_dir 入口失配拒绝（fix10-D4 全通道缺源+Gate A 不可证明）。
- `rda`：显式 `--trusted-root`（FIX8-03）不变。
- **launchd/CLI 兼容**：两 plist 均以物理路径启动（`/Users/cast/AI内容/…/investment-agent/run_daily.sh`、`…/scripts/report_generator.py`），无外部级根符号链接——生产零影响。建议（未自动修改 launchd，遵守禁令）：启动路径/PYTHONPATH 一律使用物理项目路径；若运维改为经外部根链接启动，本轮起将 fail-closed（exit 2 + 信任边界报错），这正是预期行为而非故障。

## 10. G4/正式报告保护（FIX10-05，原样保持）

fix8-G（G0~G5，52 检查）与 fix9-E（E0~E5，42 检查）**未改动**、全量重跑通过：真实发布事务基线时序、`formal_report_view` 前置断言、published=true 仅发布日、apply_status_updates 零次、报告/状态/thesis/views 字节保护、篡改自检全部保持。fix10-D 在**外链导入**攻击形态下补充验证：GLM 调用=0（D6 子进程+D7 进程内双计数）、weekly 目录零新文件、快照/采集文件 SHA-256 不变（D6b）、全项目无新增 report_status_\*/weekly_report_\*（D6c/D8）。

## 11. 受影响测试 fixture 修正（§12）

- fix9-B2：原断言"代码位置词法形式在可信入口集合"**依赖已删除的自动授信分支（缺陷本体）**——按 §12 修正为：入口集合 ⊆ 物理锚+封闭表变换形式（macOS 上 /tmp/inv-dev 形式经 /tmp↔/private/tmp **系统表**而非代码位置身份合法在场，Linux 上词法==物理天然相等），且无任何额外来源。
- fix9-B3 非darwin分支：由"⊆{物理锚,代码词法}"收紧为"**恰=**{物理锚}"（FIX10 后 Linux 入口集合唯一）。
- 两处均为**收紧方向**修正，未删除/削弱任何负向断言；diff 可核。

## 12. 原始 14 项 E2E

test_e2e_frozen14、test_e2e_orig14、test_e2e_four_weeks 本轮全量重跑通过（rc=0），含义未改；FIX10 新测试独立编号（fix10 A~D），未替代任何 E2E 编号。

## 13. 全部适用离线测试（本轮实际执行）

**30 套执行 / 0 跳过导致失败 / 全部 exit 0**（本机 Python 3.9.21 + macOS Darwin 24.6.0，2026-10-28；test_glm_live 离线契约自跳过真实付费调用、套件 exit 0，如实说明）：

test_datafix_20261017、test_e2e_four_weeks、test_e2e_frozen14、test_e2e_orig14、test_fact_engine、test_gate_chain_p01、test_glm_live(离线自跳过)、test_p01_fix1~fix9、**test_p01_fix10（新增，29 检查）**、test_p0/p1/p2/p4/p7_fixes、test_phase3、test_phase4、test_round3_adversarial、test_round3_p0、test_round4、test_round5、test_round6、test_snapshot。

关键计数：fix7 41/0、fix8 52/0（G 节含 G4 证据）、fix9 42/0（fixture 修正后）、fix10 29/0；两次连续运行幂等验证通过。

## 14. GitHub Actions

`.github/workflows/offline-tests.yml` 未改动（glob 自动纳入 test_p01_fix10.py）。CI（Linux）将真实执行双导入形态子进程测试（fix10-A/D 的子进程在 Linux 上同样触发词法穿过外链的导入）。新最终 Commit 的真实运行链接在推送后于最终开发回复给出；不以 FIX9 历史绿灯（run 40675678744）代替本轮验证。

## 15. 历史来源摘要边界（不变）

FIX7-05 SHA-256 内容绑定原样保留；FIX7 之前历史快照无 sha256 的可信度局限照旧如实记录；本轮未重建/迁移/改写任何生产研究数据。

## 16. 仍未完成的非阻断性项目

- Windows 路径分隔符 `..` 检查未在 Windows 实测（生产为 macOS/Linux）。
- 硬链接替换不可检测（FIX7 已记录，指令明确不扩项）。
- macOS /private 别名的 CI 级证据仍无法产生（CI 为 Linux）；macOS 侧行为由本机实测+封闭表断言覆盖（同 FIX9 §16）。

## 17. 生产部署注意事项

- 生产 launchd/CLI 启动路径均为物理路径（§9），上线 `research_provenance.py` 后无需任何 launchd 变更；建议人工跑一次 `snapshot_builder` 确认当日 Gate A 与旧版一致。
- 任何"经链接启动/传链接路径"的运维习惯自本轮起 fail-closed；接入外部存储仍走显式可信根配置评审，无运行时白名单。

## 18. 证据分级（按指令要求区分）

- **已证实实际代码缺陷并修复**：IA-F9-DEF-001（§4/§5，本机修复前后双态复现：B 形态入口集合含外链且 `<link>/data/daily` 放行 → 修复后拒绝）。
- **已修正的测试 fixture（依赖缺陷行为，非生产损害）**：fix9-B2/B3（§11）。
- **仅由开发者自检证明**：macOS /private 别名真机行为（fix10-C1、30 套本机回归）；双导入形态的 macOS 侧观测值（§5 表，CI 为 Linux 形态）。
- **由 GitHub CI 确认**：Linux 环境全部 30 套（含 fix10 双导入子进程）通过（链接见最终回复）。
- **环境限制如实记录**：无——词法导入条件在本机与 CI 目标 Python 均真实触发，未触发豁免条款。
