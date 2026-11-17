# COMPLEXITY_BASELINE — 复杂度基线(章程§四.4,只测不瘦)

- 生产面: 91 py 文件 / 54650 行 / 1528 函数
- 测试面: 195 py 文件 / 86455 行

## 最大 10 文件(生产面)

| 文件 | 行数 |
|---|---|
| ia_cli.py | 2252 |
| scripts/research_orchestrator.py | 2135 |
| scripts/research_contract/text_consistency.py | 2036 |
| scripts/research_provenance.py | 1893 |
| scripts/historical_coverage_audit.py | 1693 |
| scripts/china_market_collector.py | 1656 |
| scripts/report_generator.py | 1621 |
| scripts/allocation_engine.py | 1620 |
| scripts/real_data_acceptance.py | 1446 |
| scripts/data_validator.py | 1279 |

## 增长控制
- 新增框架/系统/重复模型: 须证明不可复用+登记成本(章程§四.4)
- 基线漂移>5% 未登记理由 → `complexity_baseline.py --check` 红
- 重构候选只进 CODEBASE_SIMPLIFICATION_BACKLOG(DEFERRED,本轮不执行)
