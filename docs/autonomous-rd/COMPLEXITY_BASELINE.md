# COMPLEXITY_BASELINE — 复杂度基线(章程§四.4,只测不瘦)

> **R32 重登(2026-11-23)**: 上次登记(R26)后 Audit-R27~R31 验收波次累积未登记
> (93f/60969L→93f/63340L,+2371 行,+3.9%,未触发 5% 门)+Audit-R32 正式使用
> 收尾(93f/63340L→94f/64680L,+1 文件/+1340 行): R32 证据截止规则取数入口
> (新增模块 `scripts/evidence_gate.py`——取数入口统一截止与证据资格,S3–S8/
> L1/证据索引/研究席/契约/报告/归档共用;非新增框架)+同比/政策核验+交付链
> 冻结件校验+跨指标问题重定级/金双载体同窗前提,均为既有文件的验收工单
> 扩展;测试面同步扩(210f/94917L→216f/99261L,r27-r32 门)。

- 生产面: 94 py 文件 / 64680 行 / 1714 函数
- 测试面: 216 py 文件 / 99261 行

## 最大 10 文件(生产面)

| 文件 | 行数 |
|---|---|
| scripts/research_map_planner.py | 3697 |
| ia_cli.py | 3216 |
| scripts/research_orchestrator.py | 3187 |
| scripts/research_provenance.py | 2274 |
| scripts/research_contract/text_consistency.py | 2036 |
| scripts/china_market_collector.py | 2016 |
| scripts/agent_judgment.py | 1957 |
| scripts/research_contract/judgment_contract.py | 1789 |
| scripts/historical_coverage_audit.py | 1693 |
| scripts/report_generator.py | 1621 |

## 增长控制
- 新增框架/系统/重复模型: 须证明不可复用+登记成本(章程§四.4)
- 基线漂移>5% 未登记理由 → `complexity_baseline.py --check` 红
- 重构候选只进 CODEBASE_SIMPLIFICATION_BACKLOG(DEFERRED,本轮不执行)
