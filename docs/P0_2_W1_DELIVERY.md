# P0-2 W1 交付报告（指标身份与金融语义一致性）

- 契约：IA-P0-2-W1-AC-v1.0（本轮）/ IA-P0-2-AC-v1.0（总冻结）/ 开发指令 IA-P0-2-W1-DEV-v1.0；P0-1 全部冻结契约（IA-P0-1-AC-v1.0 及 FIX1~11-AC）不变
- 角色：开发（本轮自检）；独立验收由 Agent 4 执行
- 日期：2026-10-29；分支：`dev/p0-2-w1`（未推送 main，未合并）

## 1. 开发身份

| 项 | 值 |
|---|---|
| 固定基线 Commit | `50b5d13db6c477084c6f4b3944b7bd08a8e329d6`（P0-1 验收 HEAD；origin/main 与之一致，fetch 后核实） |
| 开发分支 | `dev/p0-2-w1`（自固定 SHA 创建，非失控 HEAD） |
| DEV 工作目录 | `/Users/cast/investment-agent-dev`（独立持久化 clone） |
| 实现 Commit A | `80a7744`（6 文件 +2438/−3） |
| 最终 W1 Commit B | 本提交（docs only）；推送后 Actions 运行链接在最终开发回复给出（不以 P0-1 历史 run 代替） |

## 2. 隔离证据

- LIVE 物理路径：`/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent`（属上层 monorepo，launchd 生产目录）。
- DEV 物理路径：`/Users/cast/investment-agent-dev`；`git rev-parse --show-toplevel` = DEV 自身；remote = `git@github.com:bojing951-hash/investment-agent.git`（fetch/push 同源）。
- 隔离判断：LIVE≠DEV、互非祖先/后代（realpath 逐级核实）、DEV 树内无任何符号链接、不使用 LIVE 上层 monorepo。
- LIVE：零读取零修改（本轮全部操作位于 DEV 与 /tmp 临时目录；未运行 git reset/checkout/clean/pull 于 LIVE）。
- GitHub main：未被修改（仅创建/推送 dev/p0-2-w1）。
- 生产状态文件：未访问 LIVE env_config.py / thesis.json / allocation_views.json / data/ / output/ / logs/ / launchd plist；开发测试仅用 GitHub 净化源码 + 合成 fixture；零真实 GLM/金融 API 调用；未安装任何依赖（系统 Python 3.9.6 现有依赖面即满足，未触碰 LIVE venv）。

## 3. 81 项审计结论（W1-01）

- 总量：81 指标 / 81 唯一 metric_id / 80 active / 32 active+core / 1 deprecated（REAL_SHORT）——与指令给定基线一致。
- 分类：**VERIFIED_CONSISTENT 77 · FIXED 3 · REVIEW 1（DXY：DX-Y.NYB 报价口径需外部来源核实，字段自洽、calc 已诚实披露"近似"）· BLOCKED 0**。
- 采集器符号交叉核验：global WATCHLIST 38 项 / FRED_SERIES 27 项 / rate 4 项 / china 通道 12 项与注册表 source_symbol **全部一致**（开发期从固定 Commit 实读快照比对，冻结于审计 JSON）。
- 系统性发现（非单指标错误，均记录未擅改）：S1 注册表 freshness 窗为声明性元数据、validate_fact 实际按频率硬编码窗执行（BTC 2vs7、月频 45vs92、DFEDTAR 45vs7）——**移交 W2**（指令§5.2 禁改时效政策）；S2 china 通道 source_symbol=通道键语义；S3 ZQ 日历归 commodity 桶；S4 派生 source 两惯例（fact_engine(derived) vs macro_collector）行为一致。
- 完整 81 项逐条（issues_found/basis/impact/action/evidence）见 `docs/P0_2_W1_REGISTRY_AUDIT.json` 与 `.md`。

## 4. 代码修改（逐文件）

| 文件 | 修改 |
|---|---|
| config/metric_registry.json | 仅 3 处：NVDA/AAPL/MSFT `identity.instrument` `etf`→`single_stock`（±3 行；其余字段逐字节未动） |
| scripts/registry_semantics.py | 新增（388 行）：纯离线注册表语义验证——error 级封闭规则（ID 唯一/字段类型/单位量纲纪律/日历与来源枚举/status·criticality·frequency 词汇/instrument 类别映射与 ETF 排他性/proxy 完备性/validation·freshness 结构）+ review 级（未确认组合只诊断不拦截）；`NOT_VERIFIED_HERE` 显式声明不覆盖范围 |
| scripts/fact_engine.py | +7 行：`load_registry()` 接入 `rsem.assert_registry_semantics`（error 级 fail-loud；既有 ID/unit/calendar 断言不变；合法历史兼容结构如统计序列可选 identity 不受影响） |
| tests/test_p02_w1.py | 新增（263 行，46 检查，A~E 五节，三遍幂等） |
| docs/P0_2_W1_REGISTRY_AUDIT.{json,md} | 新增：81 项审计清单（机器可读+人读） |
| docs/P0_2_W1_DELIVERY.md | 本报告 |

未改动：run_daily.sh / run_weekly.py / research_provenance.py / snapshot_builder.py / data_validator.py / 采集器 / W2 时效窗口 / W3~W5 模块 / P0-1 冻结契约 / 任何 P0-1 测试。

## 5. 负向验证（三项已知误标必被自动检测）

test_p02_w1 B1~B3：将 NVDA/AAPL/MSFT instrument 改回 `etf` → 同名 `R-STOCK-NOT-ETF` + `R-ETF-EXCLUSIVITY` + `R-INSTRUMENT-CLASS` 三条 error 点名实际 metric_id 与字段；E1~E3：真实文件回退 AAPL → 生产加载路径 `load_registry` 抛 `RegistrySemanticsError`，消息含 AAPL、规则号、字段路径与修复方向；E5 非法配置不污染缓存。另 B4~B9 覆盖指数伪装个股/量纲冲突/来源枚举外值/重复 ID/五类非法类型/未确认组合 review 通路。

## 6. 事实引擎回归（D 节，真实路径）

`make_fact('NVDA')` 与 `normalize_global` 输出的 identity 均为修复后 `single_stock`（逐键复制注册表）；原始数值 140.5 / 观测日 2026-10-24 / unit=value_type 沿注册表不变；非法 collector（shadow_module）仍被 `rp.fact_source_problems` 拒绝——**身份修复不授予来源授权**；合法 collector+批次零问题；Gate A 权威集合不变（core 32 / active defs 80）；未注册资产仍 FAIL(identity)；快照分级口径保持。

## 7. 全量测试（本机 Python 3.9.6 + macOS，2026-10-29）

**31 套执行 / 0 失败 / 全部 exit 0**（test_glm_live 按契约跳过真实付费调用）：datafix_20261017(13)、e2e_four_weeks(59)、e2e_frozen14、e2e_orig14(41)、fact_engine(60)、gate_chain_p01(86)、p01_fix1(82)/fix2(109)/fix3(45)/fix4(49)/fix5(62)/fix6(86)/fix7(41)/fix8(52)/fix9(42)/fix10(29)/fix11(17)、**p02_w1(46，新增)**、p0(22)/p1(36)/p2(82)/p4(43)/p7(30)_fixes、phase3(47)、phase4(20)、round3_adversarial(24)、round3_p0(91)、round4(94)、round5(64)、round6(51)、snapshot(46)。Gate A 正常 PASS/合法 DEGRADED/核心失败 FAIL、来源身份、内容摘要绑定、已发布报告保护、预测观察幂等、原始 14 项 E2E 全部经既有套件重跑通过；无历史 fixture 与新规则冲突（instrument 在 W1-03 前零消费者；镜像集合由 A6 节锁同步）。

## 8. GitHub CI

offline-tests.yml 触发为 push main / PR→main / workflow_dispatch——功能分支不自动触发。本轮按指令以 workflow_dispatch 对 `dev/p0-2-w1` 发起真实运行（不推 main 绕过、不以 P0-1 历史 run 代替）：运行链接、Job ID、head_sha（须=最终 W1 Commit）与 test_p02_w1 实际执行证据在**推送后的最终开发回复**中给出。

## 9. 继承契约（P0-1 冻结条件未破坏）

- 未删除/弱化任何既有测试；31 套全量重跑通过；test_glm_live 未动。
- 未修改 Gate A/B 行为、信任边界（rp/sb/da）、内容摘要与批次绑定、已发布报告保护、预测观察状态机；`load_registry` 既有断言原样保留，新增检查仅在"已确认非法配置"时拒绝（当前生产注册表 0 error 通过）。
- P0-2 范围纪律：未实施 W2（freshness 仅查结构，S1 移交）、W3、W4、W5、P0-3。

## 10. 未验证事项（如实声明）

- 真实金融数据数值准确性未认证（81 项审计为字段一致性与已确认语义矛盾层面；DXY 口径留 REVIEW 待外部来源）。
- 采集器符号表一致性为开发期快照证据（采集器后续演进需重新比对）。
- Windows 环境；CI（Linux/Python 3.11）结果以本轮 dispatch 运行为准（§8）。
- 生产部署：本轮为开发分支交付，**未部署 LIVE**（P0-1 生产观察不受影响；W1 上线时序由后续指令决定）。
