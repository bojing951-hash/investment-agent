# COMPLEXITY_BASELINE — 复杂度基线(章程§四.4,只测不瘦)

> **R20 重登(2026-11-19)**: Audit-R20 四地地图数据面补齐波次——生产面
> 91f/54650L→93f/57909L(+2 文件/+3259 行,+6.0%): 新增 `scripts/release_calendar.py`
> (发布日历门)+`china/ea/jp_market_collector`/`macro_collector`/`snapshot_builder`
> 等四地采集与序列接线扩展(EM CPI/PPI 直取、PBC OMO 公告走查、stat.go.jp CPI
> 双基、FRED EA/JP GDP、DFEDTARU/L history_source)。增长=章程§四.4 数据面
> 补齐工单 F1 的登记成本,非新增框架/重复模型;测试面同步扩(冻结期望 R20 超越)。

- 生产面: 93 py 文件 / 57909 行 / 1591 函数
- 测试面: 204 py 文件 / 91320 行

## 最大 10 文件(生产面)

| 文件 | 行数 |
|---|---|
| scripts/research_orchestrator.py | 2645 |
| ia_cli.py | 2432 |
| scripts/research_contract/text_consistency.py | 2036 |
| scripts/china_market_collector.py | 1975 |
| scripts/research_provenance.py | 1893 |
| scripts/historical_coverage_audit.py | 1693 |
| scripts/report_generator.py | 1621 |
| scripts/allocation_engine.py | 1620 |
| scripts/real_data_acceptance.py | 1446 |
| scripts/agent_judgment.py | 1355 |

## 增长控制
- 新增框架/系统/重复模型: 须证明不可复用+登记成本(章程§四.4)
- 基线漂移>5% 未登记理由 → `complexity_baseline.py --check` 红
- 重构候选只进 CODEBASE_SIMPLIFICATION_BACKLOG(DEFERRED,本轮不执行)
