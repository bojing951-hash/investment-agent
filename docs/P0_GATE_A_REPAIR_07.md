# P0 Gate A 修复报告 07（FIX7：可信采集根与祖先路径校验）

- 契约：IA-P0-1-FIX7-AC-v1.0（本轮）；IA-P0-1-AC-v1.0 及 FIX1~FIX6-AC 全部继续有效，未降低任何阈值
- 角色：开发（本轮自检）；独立验收由 Agent 4 另行执行
- 日期：2026-10-28
- 分支：main

## 1. 开发前固定 Commit

- dev-before：`f92f18e147e0cb98aa106b258d1824b384a21d2a`（FIX6 文档终 HEAD）
- FIX6 实现：`1e4b8b3b4a7a647ad6e1a439edea10a610e802b7`；原始审计基线 `844fd3bef5e1e7e17b4d333278acd319f1dbae41`（不变）
- 基线状态：26 套离线测试全绿；工作区干净，本地=远程=f92f18e；无其他开发任务差异

## 2. 实现 Commit

- `1644933e1e3a17eadc158da0b9c4344156afbf83`（代码+测试，已推送 main，无 force）
- 变更：19 文件，+846/−107（scripts 6 个、tests 12 个更新 + test_p01_fix7.py 新增）

## 3. 最终交付 Commit

- 文档 Commit B = 本提交（docs only）；其 SHA 与 Actions 运行在推送后于最终开发回复中给出（文件无法自含其推送后才生成的事实，不预填）

## 4. IA-F6-DEF-001 整改矩阵

| 缺陷场景（必须不可通过） | 实现机制（FIX7-01/02/03） | 测试 |
|---|---|---|
| trusted-project/data → /outside，真实规范文件在 /outside/daily，文件本身非链接、规范名、FIX6 式 realpath 等式成立（**验收反例原样**） | `trusted_dir_problems` 组件逐级 islink 审计：可信根以下每个路径组件不得为符号链接 + realpath 物理包含于可信根；可信根独立推导，绝不由 data_dir/realpath 自证 | B1a/b/c（B1a 先自证旧检查前提成立） |
| daily 组件是符号链接 | 同上（组件审计覆盖 data 与 daily 任一层） | B2 |
| 最终文件是符号链接 | 文件层 islink（FIX6 语义保留，纳入统一框架） | B3 |
| 多级祖先（a/b→outside，daily 物理在外） | 组件审计逐级覆盖任意深度 | B4 |
| 采集根本身经链接重定向（词法在可信根内） | 词法包含 + 组件审计：链接名本身是被审计组件 | B5 |
| 外部真实目录无任何链接、realpath 完全自洽 | 词法包含失败即拒（不建立"批准的外部符号链接存储"白名单；外部存储须显式配置可信根） | B6 |
| 构建端从重定向目录构建出 PASS | `resolve_inputs` 信任门：不可信目录**不读取任何文件**，全通道按缺源 → Gate A fail-closed（§6.3 上下游同一实体核验函数） | B7 |
| 装配/预检/观察器吃进重定向目录产物 | 生产入口各自锚定可信根（§6 表）；拒绝传播至 exit2/预检拒/观察 FAIL | B8、E2、E3 |
| `../`、绝对路径、目录冒充、跨通道、非规范扩展名、损坏内容 | FIX6 身份层+实体层规则在可信根框架下原样保留 | C1~C7 |

## 5. 可信根定义与推导（§5.3 核心原则）

**项目采集根目录必须独立可信，不能由被校验的 data_dir 或它的 realpath 自证可信。**

- 权威原语：`rp.default_trusted_root()` = `realpath(dirname(dirname(abspath(research_provenance.py))))`——**可信代码位置**推导的项目根。定义时即 realpath 解析（macOS /var、/tmp 等系统符号链接在定义点消解，**绝不进入组件审计范围**——只审计可信根以下的组件，符合"不扫描系统根"要求）
- `rp.trusted_dir_problems(data_dir, trusted_root=None)`：缺省 trusted_root=代码位置锚；**显式参数是唯一覆盖途径**
- 无任何"按目录形状猜测可信根"的启发式：被校验目录的祖先名/层级不作为信任依据，杜绝攻击形态与沙箱形态不可区分的问题

## 6. 各生产入口的可信根锚定表

| 入口 | 可信根推导 | 生产值 | 测试授权缝（§5.3） |
|---|---|---|---|
| rp 全部校验函数（ssp/recompute/gate_status/provenance_of/verify_meta_gate_a/verify_anchor_batch） | 参数缺省 = `default_trusted_root()`（代码位置） | 仓库根（realpath） | 显式 `trusted_root=` 参数=fixture 授权，沙箱目录必须显式传入（E4 证明缺省即拒） |
| sb.resolve_inputs / build_snapshot | 参数缺省同上 | 同上 | 同上；CLI `--trusted-root`（E1 证明缺省 fail-closed） |
| da.main（装配器） | `dirname(dirname(abspath(快照路径)))`，快照路径=DATA_DIR/daily/…，**独立于被校验 data_dir** | 项目根 | mock.patch DATA_DIR=沙箱 → 锚随沙箱根（fixture 授权） |
| da.build_markdown | `dirname(normpath(data_dir or DATA_DIR))` | 项目根 | 同上 |
| rg.verify_research_inputs（周报预检，GLM 前置） | `dirname(normpath(DATA_DIR))` | 项目根 | 同上 |
| dpo.observe（观察器） | `dirname(dirname(abspath(anchors_path)))` | 项目根 | 同上 |
| real_data_acceptance | `dirname(dirname(abspath(args.data_dir)))` | 项目根 | CLI 参数=沙箱根 |

生产环境全部入口收敛到同一物理项目根；launchd 调用链不传任何 trusted_root 参数（生产无需 --trusted-root，它是沙箱/诊断缝而非生产路径）。

## 7. 祖先路径校验实现（FIX7-02）

`trusted_dir_problems(data_dir, trusted_root)` 五步 fail-closed 链（任一失败即拒，OSError 一律按不可证明处理）：

1. 可信根本身：存在 + isdir + 非 islink（可信根经链接重定向=不可信）；
2. 词法包含：`commonpath([data_dir, trusted_root]) == trusted_root`；词法形态不匹配时以 realpath 形态重试包含判定（前缀形态差异如 /var vs /private/var 不误伤——**已通过词法审计后，解析形态不可能隐藏链接组件**）；
3. **组件逐级 islink 审计**：从可信根向下到 data_dir 的每一个相对路径组件，任一为符号链接即拒（信息含组件路径+显式理由，不自动跟随）；
4. 物理包含：`realpath(data_dir)` 必须位于 `realpath(trusted_root)` 之下；
5. data_dir 是目录。

macOS/Linux 边界：可信根定义点 realpath（第 1 步只对可信根自身做 islink 判定于其**解析后**路径），组件审计只覆盖可信根以下——/var、/tmp 等系统链接永不扫描；全部 27 套测试在 macOS TemporaryDirectory（位于 /var/folders/...）中通过即为实证。

## 8. 统一实体核验（FIX7-02 §6.3 单源）

- **构建端**（sb.resolve_inputs）：`trusted_dir_problems` 不过 → 打印 `⛔ [FIX7信任边界]` 各条理由 + 汇总行，**返回全通道 None（不读取该目录任何文件）**→ 全通道 MISSING → Gate A fail-closed；
- **验证端**（rp.sources_status_problems）：函数入口即执行一次 `trusted_dir_problems`（data_dir 给出时）→ recompute effective=None；单通道实体块保留 islink/isdir/isfile/realpath 规范位核验（FIX6 语义）；
- 两端调用**同一函数**（`trusted_dir_problems`）+ 同一日源文件规则（FIX6 的 `SOURCE_FILE_RULES`）——不存在"构建端放行、验证端拒绝"或反向的口径分裂；
- Gate A 裁决（gate_status）在正式口径（data_dir 给出）下级联上述全部拒绝；纯历史口径（data_dir=None）不进行实体核验（契约证据边界，docstring 显式）。

## 9. 拒绝传播链与日志（FIX7-03）

链路：文件选择（resolve_inputs 全 None）→ 快照构建（Gate A 不得 PASS）→ 装配器（exit 2，无数据包）→ 周报预检（verify_research_inputs False → **GLM 0 次调用**）→ 无新合格正式报告 → 观察器关键 FAIL 不写长期状态 → 发布/视图字节不变（E2/E3 实证）。

日志规范：拒绝信息含研究日期（快照/批次日期）、来源通道、来源文件名、失败原因、路径信任边界（组件路径+可信根物理路径），不含任何密钥/凭据。示例（B7 实际输出）：

```
⛔ [FIX7信任边界] 受保护路径组件是符号链接:…/fix7-trusted-…/data(祖先符号链接重定向不得自动跟随——FIX7-02;如需外部存储须显式配置可信根,不得以链接越界)
⛔ [FIX7信任边界] 采集目录物理路径逃逸可信项目根:…/fix7-outside-…/daily(可信根物理路径=…/fix7-trusted-…)
⛔ [FIX7信任边界] 采集目录不可信,不读取其任何文件(全部按缺源处理): …/fix7-trusted-…/data/daily
```

## 10. FIX7-04 测试矩阵（test_p01_fix7.py，41 项全过）

- **A 规范路径（8）**：真实构建日三口径（ssp/recompute/gate_status）全过；构建端 EXACT 四通道；合法 FALLBACK（lag=1 真实回退+披露）；可信根原语自检（真实目录/非链接/即项目根）；采集目录==可信根零问题；多级真实子目录零问题；词法/解析前缀形态差异不误伤；构建即记录 sha256 摘要（64 位十六进制）。
- **B 祖先符号链接（8）**：B1a/b/c=**验收反例精确复现**（见 §11）；B2 daily 链接；B3 文件链接；B4 多级祖先；B5 采集根自身经链接；B6 外部真实目录（realpath 完全自洽）拒；B7 构建端不读取+绝不 PASS；B8 全链路（装配 exit2+无包+预检拒=GLM 0 次）。
- **C 其他边界（8）**：目录冒充；声明文件不存在（可诊断：通道+文件名+原因）；`../`；绝对路径；跨通道；非规范扩展名；损坏内容 READ_FAIL；正常对照零误伤。
- **D 历史与临时目录兼容（5）**：TemporaryDirectory+显式 fixture 可信根正常；平铺自定义目录正常；**纯历史口径原始文件已删仍结构复算通过（不虚报实体/内容核验）**；裸文件名元数据边界；正式 vs 历史授权差异（同一合法回退声明：正式口径因实体不在场拒、历史口径结构过）。
- **E 链路传播（4）**：CLI 缺省可信根 fail-closed（沙箱 --data-dir 不传 --trusted-root → 拒读+exit 2）；观察器关键 FAIL+长期状态字节不变；重定向下零新增正式报告；测试参数非生产后门（直调不传 trusted_root → 按代码锚拒）。

## 11. B1 验收反例复现细节

构造与验收报告逐字对应：`trusted-project/data → /outside`；真实规范文件物理位于 `/outside/daily/{global,macro,china,rate_economy}_20261024.json`（真实采集 payload）；文件本身**非符号链接**、文件名规范、日期规范。

- **B1a（前提自证）**：isfile=True、islink(file)=False、`canonical_source_file` 认可、FIX6 式 `realpath(full)==join(realpath(data_dir), fil)` 等式**成立**——即旧检查在此形态下必然放行，本测试先证明这一点，再证明新代码拒绝（避免"测了个不是反例的东西"）；
- **B1b**：ssp 正式口径 ≥1 条问题且点名符号链接/可信项目根；
- **B1c**：gate_status → None（不可证明），绝不作为 PASS 放行。

## 12. IA-F6-RISK-002 验证结论与最小整改（FIX7-05，证据先行）

**行为观察（整改前形态）**：

1. 快照构建后变异原始采集文件为 "THIS IS NOT JSON"：**新建快照流程**原本就会在下次构建时以 READ_FAIL 识别（解析在构建端）；但**既有快照的正式复核不重读采集文件内容**——FIX6 实体核验只查 isfile/islink/realpath 规范位；
2. 变异为**仍合法的 JSON**（数值篡改）：新建快照会把篡改值当新事实采纳（无内容绑定），既有复核同样无感知；
3. 本轮 R5 测试即该行为的可复现演示：无摘要字段（=全部 12 份生产历史快照形态）+ 文件已变异 → 正式口径仍 PASS——**这是证据边界的真实呈现，非理论推演**。

**契约判定**：来源文件内容与快照事实的绑定属于既有冻结契约（FIX-01 内容摘要绑定原则、D2/D6/D7 产物绑定语义在来源层的对应物）的未落实项——判定为**范围内的最小整改**，无需用户决策的更大方案：

- **构建端**：`snapshot_builder` 以字节一次读入 → 记录 `sources_status[ch]['sha256']` → 再解析（解析失败照旧 READ_FAIL 留痕）；
- **验证端**：`sources_status_problems` 正式口径在字段在场时重算实际文件摘要，失配即拒（`来源文件内容与构建时摘要不一致…FIX7-05内容绑定`）；**历史快照无该字段则如实跳过，不虚报内容核验、零误伤生产历史**（两级证据边界：FIX7 起构建的快照有内容证明，之前的没有）；
- 未引入签名/数据库/新存储（禁令遵守）。

**Gate A 范围答复**：正式口径（data_dir 给出）的 Gate A 现在同时绑定文件实体与内容摘要；纯历史口径不做（契约定义的证据范围，显式声明不虚报）。

## 13. R 矩阵证据（test_p01_fix7.py R1~R5，6 项全过）

- R1 既有快照复核：内容→非JSON（文件名/日期不变）→ 摘要失配拒绝（None+点名 FIX7-05）；
- R1b 新建快照：READ_FAIL + error 留痕（不吞异常）；
- R2 内容改为仍合法 JSON（SPX close→99999）→ 摘要失配拒绝（覆盖"合法 JSON 篡改"）；
- R3 内容未变 → 复核通过（摘要一致，零误伤）；
- R4 原始文件不可访问：正式口径拒（不存在），纯历史口径不受影响；
- R5 历史快照（无摘要字段）：不虚报内容核验、实体核验照常（=12 份生产快照兼容性的直接证据）。

## 14. 原始 14 项 E2E 结果

`tests/test_e2e_frozen14.py` 33/33、`tests/test_e2e_orig14.py` 41/41、`tests/test_e2e_four_weeks.py` 59/59——E2E-01~14 场景与编号未改；本轮仅按显式 fixture 可信根授权缝给既有调用补 `trusted_root` 参数（沙箱目录必须显式授权，E1/E4 证明缺省 fail-closed），断言原样。新增对抗用例独立成 test_p01_fix7.py，未替换任何原始用例。

## 15. 全部适用离线测试结果（本轮实际执行，2026-10-28）

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
| test_p01_fix6 | 86/0 | test_snapshot | 46/0 |
| test_p01_fix7（本轮新增） | 41/0 | | |

- 统计口径（如实区分）：**测试文件 27 个；全部 27 套实际执行且 exit 0（其中 test_glm_live 按约定自跳过内容）；逐项断言/检查合计 1416 通过 / 0 失败**（=26 个计数套件之和；glm_live 无断言计数）。不引用 FIX6 的 26 套/1375 项冒充本轮结果。
- 诚实声明：逐断言计数来自本机实际执行日志；GitHub Actions（§16）验证 27 套退出码，两者口径不同，均如实报告。

## 16. GitHub Actions 真实运行

- 实现 commit `1644933e1e3a17eadc158da0b9c4344156afbf83` 的运行：offline-tests **#13**（run id 40648680941）——结论 **Success**
  链接：https://github.com/bojing951-hash/investment-agent/actions/runs/40648680941
- 文档 commit（B）的运行：B 推送后触发，链接与结论在最终开发回复中报告
- FIX6 的 run 40635967351/40636098163 仅作历史证据，本轮不复用

## 17. 生产部署与历史数据兼容

- **只读复算（2026-10-28，12 份线上快照 20261017~20261028，双口径）**：FIX7 全部新校验 **0 trusted_dir_problems、0 sources_problems**（正式口径带 data_dir+trusted_root 逐份执行）——历史快照零误伤、无需改写；全部 12 份无 sha256 字段 → 按两级证据边界如实跳过内容核验（R5 行为）；
- 1017/1023 声明 PASS vs 复算 DEGRADED 不一致 = **FIX4 起既有事实**（FIX6 报告 §16 同记录），本轮行为不变，保持原样不自动重写；
- **生产路径符号链接现实（§5.4 如实记录，不自动豁免）**：live 项目根全组件无符号链接（实测）；生产锚=真实项目根；
- 部署：19 个变更文件已同步至生产目录并逐文件 cmp 校验一致；生产目录实测 fix5(62)/fix6(86)/fix7(41)/frozen14(33)/orig14(41) 全绿；launchd 未自动变更（禁令遵守），run_daily.sh 自 tomorrow 起以 FIX7 代码运行（生产入口锚=真实项目根，无需任何配置）；
- 新快照自 FIX7 起携带来源 sha256；历史快照若未来被判不可证明，按契约标记"未验证"，绝不自动重写或伪造。

## 18. 尚未验证或仍然存在的问题

1. test_glm_live 真实付费 GLM 冒烟未离线运行（环境门控；本轮 GLM 相关仅验证预检先行拒绝 → GLM 0 次调用）。
2. 12 份生产历史快照无来源 sha256 字段：其内容与来源文件的绑定**不可证明**（如实跳过而非虚报）；若需补绑定，须按流程重建快照——属生产数据操作，未自动执行。
3. 硬链接仍不可检测（符号链接/别名已拒；本地正式流程无此形态，FIX6 遗留声明不变）。
4. 1017/1023 声明与复算不一致为 FIX4 起既有事实，本轮保持原样（历史只读）。
5. `--trusted-root` CLI 参数是沙箱/诊断缝：生产调用链不使用；若未来生产需外部存储，须显式配置可信根并经用户批准（本轮无此需求，未建白名单）。

## 19. F7-AC 验收自检矩阵

- §5.3 可信根独立于 data_dir/realpath 自证：✅ 代码位置锚+显式参数唯一覆盖；B1/B6/E4
- §5.3 无批准外部符号链接存储白名单：✅ B6（无链接外部目录也拒）；拒绝信息显式说明"须显式配置可信根"
- §5.3 测试参数非生产后门：✅ E1（CLI 缺省拒）/E4（直调缺省拒）；生产入口不传参
- §5.4 逐组件核验（lstat/islink/realpath/commonpath）：✅ §7 实现；B2/B4/B5
- §5.4 macOS/Linux 不扫描系统根：✅ 可信根定义点 realpath+只审计根下组件；27 套测试在 macOS /var/folders 沙箱全绿
- §6.2/6.3 构建端与验证端共享同一实体核验：✅ trusted_dir_problems 单源；B7（构建端不读+不 PASS）
- §8 拒绝传播全链+可诊断日志（日期/通道/文件/原因/边界，无密钥）：✅ B8/E2/E3；§9 示例
- §9 RISK-002 证据先行+最小整改+无签名/DB/新存储：✅ §12/§13
- §10 全部既有套件+冻结 E2E 编号含义不变+新增对抗独立成套：✅ §14/§15

## 20. 历史契约适用自检

IA-P0-1-AC-v1.0 与 FIX1~FIX6-AC 全部适用项保持：81 指标注册表、关键性分级、事实引擎、快照不可变/修订、Gate A/B、统一来源规则、EXACT/FALLBACK 窗口、非核心缺失 DEGRADED、GLM 5.3、评分卡/相关性、正式发布事务、9 论点、9 视图、预测生命周期、月度/季度、launchd、GitHub Actions 均未改动；27 套全绿（含 FIX1~FIX6 全部冻结断言）即回归证明。禁令遵守：未降低来源校验标准、未建符号链接白名单、未删旧测试、未改回退窗口、未把 DEGRADED 全变 FAIL、未动生产历史数据、未重建 DB、未引入多 Agent/Web 服务/替换 GLM/自动交易/自动改 launchd、无 force push、无 API 密钥入库。

---

**开发自检结论**：IA-F6-DEF-001 已按 FIX7-01/02/03 实现（可信根独立锚定+组件逐级审计+上下游单源+全链拒绝传播）；IA-F6-RISK-002 按 FIX7-05 证据先行完成最小整改（来源内容摘要绑定，两级证据边界，历史零误伤）。27 套离线测试（含原始 14 项 E2E 与新增 41 项对抗矩阵）本轮实际执行全绿；生产 12 份快照只读复算零误伤并已同步部署。本报告为开发自检，P0-1 最终结论以独立 Agent 4 验收为准（READY FOR INDEPENDENT ACCEPTANCE）。
