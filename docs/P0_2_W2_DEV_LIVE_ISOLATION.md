# P0-2 W2 — DEV/LIVE 只读隔离核验证据

- 轮次：IA-P0-2-W2（核验于本轮实现完成、提交前执行）
- 性质：全部为**只读**操作（stat/realpath/git cat-file/sha256/plistlib 读取）；零写入 LIVE
- 机器可读明细：`docs/P0_2_W2_DEV_LIVE_ISOLATION.json`（含复跑命令 `rerun_commands`）

## 1. 物理路径与目录身份

| 项 | 值 |
|---|---|
| DEV | `/Users/cast/investment-agent-dev`（realpath 同，无符号链接参与） |
| LIVE | `/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent`（realpath 同） |
| 目录身份 | DEV=(16777231, 60895116)；LIVE=(16777231, 22199716)——**inode 不同，物理两个目录** |
| 祖先/后代关系 | 否（commonpath 双向判定） |

## 2. Git 状态（DEV 内只读执行）

| 项 | 值 |
|---|---|
| 分支 | `dev/p0-2-w2`（父基线=W1 最终验收 Commit `69d7fc71f4ac05d3e5323cb5e270585ec48d6f97`，非 main） |
| origin/main | `50b5d13db6c477084c6f4b3944b7bd08a8e329d6d`（P0-1 封版，**未被修改**） |

## 3. LIVE 生产代码 vs P0-1 封版（SHA-256 原始字节对照）

| 文件 | LIVE = 50b5d13 ? |
|---|---|
| run_daily.sh / run_weekly.py | ✅ / ✅ |
| scripts/fact_engine.py / report_generator.py / research_provenance.py | ✅ / ✅ / ✅ |
| scripts/data_validator.py / snapshot_builder.py | ✅ / ✅ |
| config/metric_registry.json | ✅（**W2 的 22 项窗口修改不在 LIVE**） |
| scripts/freshness_policy.py | LIVE 不存在（W2 新文件，未部署） |

比对方法注记：blob 哈希以 `git cat-file` 原始字节计算；初版核验脚本曾因 `strip()` 截断尾部换行出现假性不一致，已修正并复跑（W1 轮六文件"全部一致"结论不变）。

未读取：LIVE `env_config.py` 密钥、`data/`、`output/`、`thesis.json`、`allocation_views.json`、日志。

## 4. launchd 执行路径（只读）

`com.investment.daily`（07:00）与 `com.investment.weekly`（周六 08:00）全部路径型参数 realpath 均落在 **LIVE**，零条落在 DEV。未修改任何 plist。

## 5. 结论与限制

**结论**：DEV/LIVE 物理隔离成立；LIVE 全部核心生产文件与 P0-1 封版逐字节一致；本轮未对 LIVE 做任何修改、未部署、未改 launchd；GitHub main 未动。

**限制**：哈希一致证明核验时刻状态一致，不构成历史绝对零改写的数学证明；独立方可按 JSON `rerun_commands` 只读复跑核对。
