# P0 Gate A 修复报告 08（FIX8：symlink/.. 穿越与检查-访问路径分叉）

- 契约：IA-P0-1-FIX8-AC（本轮）；IA-P0-1-AC-v1.0 及 FIX1~FIX7-AC 全部继续有效，未降低任何阈值
- 角色：开发（本轮自检）；独立验收由 Agent 4 另行执行
- 日期：2026-10-28
- 分支：main

## 1. 开发前固定 Commit

- dev-before：`2a0de711179fb985ab27d498123b4c20e801cc6a`（FIX7 文档终 HEAD，本轮指令固定基线）
- FIX7 实现：`1644933e1e3a17eadc158da0b9c4344156afbf83`；原始审计基线 `844fd3bef5e1e7e17b4d333278acd319f1dbae41`（不变）
- 基线状态：26 套离线测试全绿（FIX7 回归记录）；工作区干净，本地=远程=2a0de71

## 2. 实现 Commit

- `a950a68b9c7868b4e81bd9dd6f6a1cc28eeb1b04`（代码+测试，推送 main，无 force）
- 变更：14 文件，+898/−131（scripts 6 个、tests 7 个更新 + tests/test_p01_fix8.py 新增）

## 3. 最终交付 Commit

- 文档 Commit B = 本提交（docs only）；其 SHA 与 Actions 运行在推送后于最终开发回复中给出（文件无法自含其推送后才生成的事实，不预填）

## 4. IA-F7-DEF-001 修复结果

**IMPLEMENTED（待独立验收确认）。** 验收反例 `project/alias/../data/daily`（`alias → outside/child`）在新实现下从
`trusted_dir_problems / trusted_source_dir / resolve_inputs / build_snapshot /
sources_status_problems / recompute_gate_a / gate_status / data_assembler /
report_generator 预检` 全链拒绝；且新测试先以 4 项前提（§6）证明该反例
在修改前确为放行路径，负向前提被固化保留。

## 5. 根因分析

- 旧 `trusted_dir_problems()` 第一步即 `os.path.normpath(data_dir)`：词法折叠把
  `alias/..` 消除后，**被校验对象**变成了折叠后的"可信形态"；而调用方
  （resolve_inputs 等）后续文件访问用的是**原始路径**，`alias` 组件经符号链接
  解析到不可信位置——安全检查对象 ≠ 实际 IO 对象。
- 附带缺陷 B：即使补做 realpath 包含检查，"词法越界→物理落点回根内→自动
  重新授信"（external-link→project/data 后传 external-link/daily）仍可绕过——
  等于用被校验路径的物理解析结果自证授权。
- 附带缺陷 C：`da.build_markdown`/`dpo.observe`/`rda --data-dir` 曾从**待校验
  路径自身**（data_dir 参数、anchors_path 父目录）推导可信根——被校验路径自证。
- 本轮还发现并修复一个消费端语义洞：`real_data_acceptance` 对 gate_a.status
  为 None/FAIL 的快照只把 Gate A 记为一条非 FAIL 判定，不可信目录全 SKIP 场景
  以 exit 0"验收通过"放行——已改为非 PASS/DEGRADED 一律 exit 2（收紧，非降低）。

## 6. 原始 symlink/.. 反例复现（FIX8-04 §8.1）

测试先证明反例前提成立（修改前确为漏洞，负向前提保留，不因修复后通过而失去意义）：

1. `normpath(原始路径)` 词法位于 project 内（旧代码的检查对象）——测试 A1a；
2. `realpath(原始路径)` 物理位于 outside（真实 IO 解析对象）——A1b；
3. 原始路径确实能读到外部文件的篡改内容（SPX=99999.0）——A1c；
4. 折叠形态 `normpath(DD)` 经旧式校验零问题（= 修改前 FIX7 代码放行）——A1d。

新实现结果（同一测试文件 A2~A12）：`..` 组件在词法折叠**前**被组件级拒绝；
`trusted_source_dir` 返回 (None, 问题)；`resolve_inputs` 不读取该目录任何文件
（缺省与显式可信根双口径）；`build_snapshot` 只产 Gate A≠PASS 诊断快照；
`sources_status_problems / recompute_gate_a / gate_status` 全部不放行。

## 7. 外部链接重新入根测试（FIX8-02）

`external-link → project/data`，传入 `external-link/daily`：物理落点在可信根内
（前提 B1 成立），仍拒——词法越界后 realpath 落点不自动授信；无任何外部符号链接
白名单机制。构建端不选文件、验证端 None（B2/B3）。

## 8. 原 FIX6 B1 测试

`project/datalink → outside` 传入 `datalink/daily`：组件 islink 审计继续拒
（测试 C1）；FIX6 全套身份层/实体层规则（规范名/非链接/非目录/扩展名/通道）
在套件 C/D 与 test_p01_fix6.py 全量重跑中原样保留。

## 9. 可信根来源及路径验证机制

- **可信根唯一来源**：`rp.default_trusted_root()`（可信代码位置推导的项目根
  realpath）或调用方**显式传入**的 trusted_root（测试 fixture 授权缝 / rda
  `--trusted-root` 显式授权）。绝不从被校验路径、其 normpath 或其 realpath 推导。
- **验证次序**：① 原始路径类型与 `..` 组件检查（任何词法规范化之前）；
  ② 可信根本身合法性（存在/非符号链接/是目录）；③ abspath 后词法包含于可信根；
  ④ 词法不包含时的**组件前缀回退**：仅当 data_dir 的某组件前缀 P 满足
  `realpath(P)==可信根物理锚`（系统级别名，如 macOS /var→/private/var，且位于
  可信根之上）才接受——**绝不整条路径 realpath 重试**（那等于自动重新授信）；
  ⑤ 可信根以下逐组件非符号链接审计；⑥ realpath 物理包含；⑦ isdir。
  任一步失败即 fail-closed，`OSError/ValueError` 同样 fail-closed。
- **验证路径=访问路径**：`trusted_source_dir()` 返回核验通过的物理路径，
  snapshot_builder 的一切后续 IO 全部改用该返回值（不再持有原始可疑字符串）。

调用端锚定（§7.3 审计后）：

| 入口 | 可信根锚定 | 测试 |
|---|---|---|
| snapshot_builder.resolve_inputs/build_snapshot | default_trusted_root() 或显式参数 | A5/A8、fix7 E1/E5、fix8 A/B/G |
| data_assembler.build_markdown / main | `dirname(DATA_DIR)` 模块常量（生产=代码位置配置；测试 patch=fixture 授权缝）或显式参数；**data_dir 参数不再自证** | fix8 I1、G2 |
| report_generator（预检/正式） | `dirname(DATA_DIR)` 同上 | G3 |
| daily_prediction_observer.observe | default_trusted_root() 或显式参数；**不从 anchors_path 推导** | fix8 I2、fix7 E2 |
| real_data_acceptance.main | default_trusted_root() 或 `--trusted-root` 显式授权；**不从 --data-dir 推导**；Gate A 非 PASS/DEGRADED → exit 2 | fix8 I3 |

## 10. 构建端与消费端一致性

同一原语 `trusted_dir_problems/trusted_source_dir`（§6.3 不两处漂移）：
构建端（resolve_inputs 选文件）与消费端（sources_status_problems/
recompute_gate_a/gate_status/verify_anchor_batch/verify_meta_gate_a 复核）
对同一目录结论一致——反例目录两端同时拒绝（A2~A12、G1~G3）；
`sources_status_problems` 内部文件级核验亦统一经已验证物理路径执行
（probe=verified；诊断性 fallback 仅用于已判致命目录的报错信息，不影响判定）。

## 11. 完整研究链路结果（FIX8-06）

沙箱内在档：合格已发布周报 + report_status(published) + thesis.json +
allocation_views.json（sha256 留痕）；构造 `alias/..` 越界来源（外部含当日四通道
篡改文件）后真实执行：

- `snapshot_builder`：Gate A≠PASS 诊断快照，失败原因（`..` 组件）留痕（G1）；
- `data_assembler.main`：exit=2，无数据包文件产生（G2）;
- `report_generator.generate_weekly_report`：预检拒绝 exit=2，**GLM 调用 0 次**
  （计数器实测），无新正式报告（G3）；
- 保护对象（周报/状态/thesis/views）前后 sha256 完全一致（G4）；
- mock 仅限外部 API/GLM/时钟，未 mock 任何信任原语/Gate A/预检。

## 12. 原始 E2E-01～14

由 test_e2e_orig14.py / test_e2e_frozen14.py / test_e2e_four_weeks.py /
test_gate_chain_p01.py 承载，含义未改（E2E-01 完整正常数据 … E2E-14 已有合格
报告的后续失败保护），本轮全量重跑通过；本轮新增路径攻击测试独立编号于
test_p01_fix8.py（A~I 节），未替代任何原始 E2E 编号。

## 13. 全部适用回归（本轮实际执行，非历史数字）

实际执行 **28 套**（本机 Python 3.9.21，2026-10-28），全部退出码 **0**，
跳过 **0** 套（test_glm_live.py 离线契约下自跳过真实付费调用，套件本身执行
并以 0 退出，如实说明）：

test_datafix_20261017、test_e2e_four_weeks、test_e2e_frozen14、test_e2e_orig14、
test_fact_engine、test_gate_chain_p01、test_glm_live(离线自跳过)、
test_p01_fix1、test_p01_fix2、test_p01_fix3、test_p01_fix4、test_p01_fix5、
test_p01_fix6、test_p01_fix7、**test_p01_fix8（新增）**、test_p0_fixes、
test_p1_fixes、test_p2_fixes、test_p4_fixes、test_p7_fixes、test_phase3、
test_phase4、test_round3_adversarial、test_round3_p0、test_round4、
test_round5、test_round6、test_snapshot。

本轮新增检查 **49 项**（test_p01_fix8.py：A 原始反例 12、B 外链重入 3、
C FIX6 回归 1、D 边界矩阵 16、E 类型/合法形态 4、F 正常回归 5、G 完整链路 4、
H 摘要回归 2、I 锚定审计 2），49 通过 / 0 失败。既有套件中被 fixture 授权缝
更新涉及的文件：fixt.py、test_gate_chain_p01、test_p01_fix1/5/6/7、
test_e2e_frozen14——均为"向既有调用点显式传入 fixture 可信根/新增参数"，
无删除或削弱任何负向断言（diff 可核）。

## 14. GitHub Actions 运行链接

工作流 `.github/workflows/offline-tests.yml` 未改动，自动纳入
test_p01_fix8.py（glob 发现）。实现 Commit 与文档 Commit 的真实运行链接在
推送后于最终开发回复中给出（本轮新 Commit 的成功记录，不复用 FIX7 历史
runs/40649246402）。

## 15. 历史 JSON SHA-256 兼容说明（§11 边界）

- 新快照：FIX7-05 内容绑定原样保留（H1：构建后改内容 → 摘要失配拒）。
- 历史快照缺 sha256 字段：只读历史分析能力保留，不自动改写、不伪造摘要、
  不宣称历史来源内容已完整验证（H2：无摘要字段不产生失配误报，即不虚报
  "已核验"）；该局限如实记录为可信度边界。
- 内容摘要匹配 ≠ 物理来源可信——路径授权先于摘要比对（本轮主题）。
- 未借本轮重建历史数据库或迁移历史文件。

## 16. 未验证或未解决事项

- Windows 路径分隔符场景仅做了字符串层 `\\`→`/` 归一后的 `..` 组件检查，
  未在 Windows 文件系统实测（本项目生产环境为 macOS/Linux）。
- 历史（FIX7 之前）快照原始采集文件内容无法事后证明未变（§11 已记录局限，
  按指令不扩展为新整改项）。
- 其余：无已知未解决项。以上两项均不构成对冻结阻断条件的违反。

## 17. macOS 兼容情况

- /tmp→/private/tmp、/var→/private/var 系统别名经**组件前缀回退**处理
  （仅限可信根之上的系统级前缀），开发克隆 /tmp/inv-dev 与临时目录沙箱
  双向形态（dd=raw/根=realpath 与 dd=realpath/根=raw）均不误伤（F3）；
  根内相对路径与 PathLike 输入正常（E2~E4）。
- 平铺沙箱（data_dir==trusted_root，macOS tempfile 常态）经前缀回退覆盖
  全路径候选后放行（F1，修复过程中曾漏该形态并已回归 9 套受影响套件确认）。

## 18. 生产部署注意事项

- 线上从克隆目录验收线上数据时，`real_data_acceptance` 须显式传
  `--trusted-root <线上项目根>`（此前靠 --data-dir 自证，现已移除并在缺省
  拒绝时 exit 2）。
- 生产 `run_daily.sh` 流程不含 `..` 采集路径与外部符号链接，不受收紧影响；
  部署本轮 6 个 scripts 文件后建议先人工跑一次 `python3 scripts/
  snapshot_builder.py`（当日无篡改则行为与旧版一致：Gate A 结果不变）。
- 任何"把外部存储挂进项目目录"的需求，一律走显式可信根配置评审，不存在
  运行时白名单开关。
