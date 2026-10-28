# P0 Gate A 修复报告 11（FIX11：外链导入环境下的联合 E2E 保护补证 + 周报链路径缺陷修复）

- 契约：IA-P0-1-FIX11-AC-v1.0（本轮）；IA-P0-1-AC-v1.0 及 FIX1~FIX10-AC 全部继续冻结有效，未降低任何阈值
- 角色：开发（本轮自检）；独立验收由 Agent 4 另行执行
- 日期：2026-10-28
- 分支：main

## 1. 开发前固定 Commit

- dev-before：`2e2bb698d49ffdbc16e3e24bd9c0b94a10cddccc`（FIX10 终 HEAD；基线核实：本地=远程，工作区干净）
- FIX10 实现 `8ef6773ed951f6cf60cf58ec753c27492aa6ca62`；原始审计基线 `844fd3bef5e1e7e17b4d333278acd319f1dbae41`（不变）

## 2. 测试实现 Commit

- `84d30a63e11fef5ba11bed01ee8981fb89df3e87`（联合测试 test_p01_fix11.py 新增 + report_generator.py 最小生产修复，2 文件 +450/−1）

## 3. 最终 GitHub HEAD

- 文档 Commit B = 本提交（docs only）；SHA 与 Actions 运行在推送后于最终开发回复给出（不预填）

## 4. FIX10-EVIDENCE-GAP-001 补证结果

验收指出：非法来源拒绝（FIX10）与正式报告/长期状态保护（FIX9 G4/E）分属两组测试，无同一条件链联合证据。本轮 test_p01_fix11.py 在**同一外链标准导入子进程**内闭环：前置验证 → 四对象执行前 SHA-256 → 真实非法研究链 → 复采比对 + 正式身份复核。17 检查全过（本机两轮幂等）。**该 gap 已补证**；同时联合测试暴露了一个新的确定性生产缺陷（§12，已最小修复）。

## 5. 与 FIX9/FIX10 的复用关系

复用：FIX10 的整目录项目复制（scripts+config+env_config）、外链命名 `UNAPPROVED-external-link-to-project-root`、子进程 PYTHONPATH 标准导入驱动、_DT 固定时钟；FIX9-E0 的真实发布 mock 栈（GLM≥500 字符/validate/load_views/pending/load_\*）；fixt.build_full_day/write_collectors/as_of_for；SHA-256 工具。未复制第三套框架；未改动 FIX9 G4、FIX10 双导入测试与原始 E2E。

## 6. 外链标准 Python 导入的真实 `__file__`（单次运行样本）

- rp：`…/fix11-be4qd2az/UNAPPROVED-external-link-to-project-root/scripts/research_provenance.py`
- rg：`…/fix11-be4qd2az/UNAPPROVED-external-link-to-project-root/scripts/report_generator.py`
- sb/da 同形态（A1 断言四模块全部穿过外链，驱动内 assert 失败即套件失败）

## 7. 实际模块物理根

- realpath：`…/fix11-be4qd2az/project/scripts/*`（四模块同物理项目）
- `default_trusted_root()` = `…/fix11-be4qd2az/project` 物理根（A1 断言）

## 8. 被测非法来源路径

- `…/UNAPPROVED-external-link-to-project-root/data/daily`（文件物理位于项目 data/daily 内——拒绝对象是**未经批准的访问路径入口**，非物理越界）

## 9. 正常物理来源正向对照

- 物理导入子进程对**同一批 ATK(20261025) 采集文件**构建：Gate A=PASS、四通道全选、`trusted_dir_problems(物理 daily)=[]`——证明拒绝只能来自路径入口而非数据缺陷（P1）。

## 10. 真实合格正式报告的前置验证

- 物理导入子进程：真实 `build_full_day` + `generate_weekly_report()`（GLM mock 恰 1 次）→ exit 0，报告/状态落盘；`formal_report_view` 返回有效视图（published=true、digest 与实际文件一致）+ `scan_formal_weekly_reports` 识别为已发布（P2/P2b）。失败即本轮 FAIL、不进入保护断言（契约要求）。

## 11. 四对象执行前 SHA-256（同一外链导入子进程内采集；单次运行样本，临时项目每次不同）

| 对象 | before（前 24…后 8 hex） |
|---|---|
| weekly_report_20261024.md | `5baafb0cd7f8ff84630971bb…613a88f7` |
| report_status_20261024.json | `3d99a7a3281386e9b837694b…d7455666` |
| config/thesis.json | `ff9de2c09800c037e9ff92d1…b8a8dcbe` |
| config/allocation_views.json | `3b896e29fdc7b0eeb5104740…73cce73f` |

- 经外链路径读取同一文件的摘要==物理路径摘要（A8：同一文件非两个保护对象）。

## 12. 新增实际代码修复（与"补充证据"区分；IA-F10-DEF-001）

- **缺陷**：联合测试 P2（物理导入、**不 patch 模块锚**，即生产 run_weekly 子进程形态）确定性失败：rg `PROJECT_DIR = join(dirname(__file__),'..')` 使 `DATA_DIR` 词法含 `scripts/..`，自 FIX8-01 起被 `trusted_dir_problems` 的 `..` 组件拒绝一律 fail-closed → 周报预检 exit 2。
- **生产影响证据**：线上 LIVE rg.DATA_DIR（`…/investment-agent/scripts/../data`）实测被拒；最后发布周报 20261024（周六）早于 FIX8 上线，属**潜伏缺陷**——下一次周六运行（2026-10-31）将确定性失败；此前各轮测试均 patch DATA_DIR 为清洁沙箱路径，未覆盖模块缺省锚形态。
- **最小修复（FIX11-01）**：rg `PROJECT_DIR` 改为与 da/sb/dpo 一致的绝对双 dirname 形态（纯路径配置推导，不含 `..`；授权判断仍全部由 trusted_dir_problems 执行，本行不构成任何授权）。31 套全量回归通过；失败复现保留于 test_p01_fix11.py P2（修复前该检查确定性红）。
- **未改动**：collectors 的同类 `join(..,'..')` 形态（仅写路径、不进信任链，物理位置不变，最小修改原则下不动，如实记录）。

## 13. 同一子进程中的实际危险操作与结果（单次运行样本）

| 步骤 | 结果 |
|---|---|
| trusted_dir_problems / trusted_source_dir | REJECT（消息含信任边界/FIX10-01 标注；不返回授权路径） |
| sb.build_snapshot（外链入口） | Gate A=不可证明(None)、四通道全 MISSING、诊断快照写回项目目录 |
| da.main()（模块锚=外链词法） | exit **2**，无 EATK 正式数据包 |
| rg.verify_research_inputs(20261025) | 拒绝（原因可追踪来源授权/Gate A） |
| rg.generate_weekly_report() | exit **2**，GLM 调用 **0**，apply_status_updates（透传 spy）**0** 次 |

## 14. 四对象执行后 SHA-256

- 与 §11 执行前**逐项相等**（A7：before==after，逐键比较非长度比较）；父进程独立复算==子进程 after（B1，证明摘要来自真实文件非缓存）。

## 15. 正式报告后置验证及发布扫描差异

- formal_before=True → formal_after=True；scan `['20261024']` → `['20261024']`（集合一致）；new_published_count=0；published=true 仅发布日；输出目录无新增 weekly_report_\*/report_status_\*；EATK 诊断快照 Gate A≠PASS 不被当作合格研究输入（B2）。

## 16. 测试敏感性验证

- 独立夹具（四对象副本）篡改 thesis → 摘要比较发现变化且不误报未动对象（S1）；未修改任何生产/主实验文件；套件任一检查失败→非零退出。

## 17. 原始 E2E-01～14

test_e2e_frozen14、test_e2e_orig14、test_e2e_four_weeks 本轮全量重跑通过（rc=0），含义未改；FIX11 新测试独立编号，未替代任何 E2E 编号；E2E-10/12/14 未改动。

## 18. 全部适用离线测试

**31 套执行 / 全部 exit 0**（本机 Python 3.9.21 + macOS Darwin 24.6.0，2026-10-28；test_glm_live 离线契约自跳过、套件 exit 0，如实说明）。含 test_p01_fix1~fix11、test_e2e_\*、test_gate_chain_p01、test_p0/p1/p2/p4/p7_fixes、test_phase3/4、test_round3~6、test_snapshot、test_fact_engine、test_datafix_20261017。关键计数：fix7 41/0、fix8 52/0、fix9 42/0、fix10 29/0、**fix11 17/0（新增）**；fix11 两轮幂等。结构化观测输出（@FIX11-JSON@ 行）随套件 stdout 打印，CI 失败时经 annotation/日志可见。

## 19. FIX11 最终 Commit 对应 GitHub Actions

- 链接于推送后在最终开发回复给出（不以 FIX10 历史 run 40686370252 代替）。

## 20. 尚未验证事项与证据等级

- **已证实实际代码缺陷并修复**：IA-F10-DEF-001（§12，修复前后行为+线上 LIVE 形态实测）。
- **联合补证已闭环**：FIX10-EVIDENCE-GAP-001（§4，本机双运行；CI 确认见 §19）。
- **仅开发者本机证明**：macOS /private 别名环境行为、四对象摘要样本值（CI 为 Linux，路径形态不同但断言同构执行）。
- **未验证**：Windows；真实付费 GLM（契约禁用，全程 mock 计数）。
