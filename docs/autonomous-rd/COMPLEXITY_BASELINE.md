# COMPLEXITY_BASELINE — 复杂度基线(章程§四.4,只测不瘦)

- 生产面: 98 py 文件 / 74653 行 / 2008 函数
- 测试面: 217 py 文件 / 106095 行

## 最大 10 文件(生产面)

| 文件 | 行数 |
|---|---|
| scripts/research_map_planner.py | 4170 |
| ia_cli.py | 3745 |
| scripts/research_orchestrator.py | 3627 |
| scripts/research_contract/judgment_contract.py | 2707 |
| scripts/china_market_collector.py | 2525 |
| scripts/agent_judgment.py | 2404 |
| scripts/research_provenance.py | 2341 |
| scripts/expectations_gap.py | 2285 |
| scripts/seat_tools/make_expectations_gap_judgment.py | 2067 |
| scripts/research_contract/text_consistency.py | 2036 |

## 增长控制
- 新增框架/系统/重复模型: 须证明不可复用+登记成本(章程§四.4)
- 基线漂移>5% 未登记理由 → `complexity_baseline.py --check` 红
- 重构候选只进 CODEBASE_SIMPLIFICATION_BACKLOG(DEFERRED,本轮不执行)
