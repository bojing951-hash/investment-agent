# P0-2 W1 / FIX1 — DEV/LIVE 只读隔离核验证据

- 轮次：IA-P02-W1-FIX1（前置核验于本轮开发前完成，同日复跑生成本文件）
- 性质：全部为**只读**操作（stat/realpath/git rev-parse/git show/sha256/plistlib 读取）；零写入 LIVE、零写入 DEV 生产无关路径
- 机器可读明细：`docs/P0_2_W1_DEV_LIVE_ISOLATION.json`（含每次核验的时间戳与完整字段）

## 1. 核验环境

- 核验时间：2026-10-29（北京时间，ISO 时间戳见 JSON `verified_at`）
- 操作系统：Darwin 24.6.0（macOS, arm64）——`platform.system()/release()/machine()` 实取

## 2. 物理路径与目录身份（非字符串前缀比较）

| 项 | 值 |
|---|---|
| DEV 声明路径 / realpath | `/Users/cast/investment-agent-dev` → realpath 同（无符号链接参与） |
| LIVE 声明路径 / realpath | `/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent` → realpath 同 |
| DEV Git 根 realpath | `/Users/cast/investment-agent-dev/.git`（Git 根=DEV 自身，独立仓库） |
| 目录身份（st_dev, st_ino） | DEV=(16777231, 60895116)；LIVE=(16777231, 22199716)——**inode 不同，物理上两个目录** |
| 是否同一目录 | 否（realpath 与 inode 双重判定） |
| 祖先/后代关系 | 否（`os.path.commonpath` 双向判定均否） |
| DEV 经符号链接指向 LIVE | 否 |
| LIVE 经符号链接指向 DEV | 否 |
| DEV 工作树内符号链接 | 无（全树扫描，`.git` 内部除外） |

## 3. Git 状态（DEV 内只读执行）

| 项 | 值 |
|---|---|
| 分支 | `dev/p0-2-w1` |
| DEV HEAD（开发前） | `704cd5903349989fa4e3cca86a51c7b4ca78554d`（=指令固定失败验收 Commit） |
| origin/main | `50b5d13db6c477084c6f4b3944b7bd08a8e329d6`（=P0-1 封版，**未被修改**） |
| origin/dev/p0-2-w1 | `704cd59`（与本地一致，fetch 后核实） |
| 工作树 | 开发前干净；本轮修改仅 FIX1 范围内 9 个文件（见交付报告） |

## 4. LIVE 生产代码 vs P0-1 封版 Commit（SHA-256 逐字节对照）

| 文件 | LIVE = 50b5d13 ? |
|---|---|
| run_daily.sh | ✅ 一致 |
| run_weekly.py | ✅ 一致 |
| scripts/fact_engine.py | ✅ 一致 |
| scripts/report_generator.py | ✅ 一致 |
| scripts/research_provenance.py | ✅ 一致 |
| config/metric_registry.json | ✅ 一致（**W1/W1-FIX1 的注册表修改不在 LIVE**——LIVE 仍为 P0-1 形态） |

未读取：LIVE `env_config.py` 密钥内容、`data/`、`output/`、`thesis.json`、`allocation_views.json`、日志。仅对上述非敏感生产源码做二进制读取哈希。

## 5. launchd 执行路径（只读核验）

| Label | Program/Arguments | 指向 |
|---|---|---|
| com.investment.daily | `/bin/bash <LIVE>/run_daily.sh`（07:00） | ✅ LIVE，非 DEV |
| com.investment.weekly | `<venv>/python3 <LIVE>/scripts/report_generator.py`（周六 08:00） | ✅ LIVE，非 DEV |

两个 plist 的全部路径型参数逐条 realpath 核验：至少一条落在 LIVE 内、零条落在 DEV 内。

## 6. 结论与证据能力限制

**结论**：DEV/LIVE 物理隔离成立（不同 inode、无祖先关系、无符号链接交指）；LIVE 六个核心生产文件与 P0-1 封版 Commit 逐字节一致；launchd 生产调度只引用 LIVE；GitHub main 未动。**本轮未对 LIVE 做任何生产修改，未部署，未改 launchd。**

**限制（如实声明）**：
1. 哈希一致仅证明**核验时刻**状态一致；缺少开发前基线快照，不能绝对证明历史上从未发生短暂改写。
2. "本轮零写入 LIVE"以本轮会话实际操作为据；完整命令历史不构成"绝对没有任何写入"的数学证明。
3. 如需独立本机见证，可只读复跑 JSON 中 `rerun_commands` 所列命令（realpath/git rev-parse/shasum-256 对照/plutil），结果应与本文件一致。
