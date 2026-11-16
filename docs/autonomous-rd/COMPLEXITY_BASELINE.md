# COMPLEXITY_BASELINE — 复杂度基线(章程§四.4,只测不瘦)

- 生产面: 90 py 文件 / 52253 行 / 1476 函数
- 测试面: 187 py 文件 / 81689 行

## 最大 10 文件(生产面)

| 文件 | 行数 |
|---|---|
| ia_cli.py | 2109 |
| scripts/research_contract/text_consistency.py | 2036 |
| scripts/research_provenance.py | 1893 |
| scripts/historical_coverage_audit.py | 1693 |
| scripts/report_generator.py | 1621 |
| scripts/allocation_engine.py | 1620 |
| scripts/china_market_collector.py | 1559 |
| scripts/real_data_acceptance.py | 1446 |
| scripts/data_validator.py | 1279 |
| scripts/view_plausibility.py | 1022 |

## 增长控制
- 新增框架/系统/重复模型: 须证明不可复用+登记成本(章程§四.4)
- 基线漂移>5% 未登记理由 → `complexity_baseline.py --check` 红
- 重构候选只进 CODEBASE_SIMPLIFICATION_BACKLOG(DEFERRED,本轮不执行)

## 漂移登记(Audit-R2 收口,2026-11-16)

- 基线 89f/51038L(生产)+178f(测试)@953c9ff → 本次重定 90f/52244L+187f。
- **test_files +5.1%(超 5% 阈,依章程§四.4 登记)**: 全部为回归/守卫面,
  非新框架——Product Convergence Phase 2-6(test_pc_phase2/3…)+
  Audit-R1 反例回归(test_audit_r1_f02/f03/f09)+ Audit-R2
  (test_audit_r2_chain_archive 条目1/2 链档反例、test_pytest_entry_fix
  条目5 三入口、conftest)。每件对应章程条目,零新增运行时框架。
- **prod +1f=scripts/gate_b_parallel_harness.py**(PC Phase 2 并行迁移
  只测框架)+2.4% 行在阈内,理由同上随波次说明在档。
- CODEBASE_SIMPLIFICATION 保持 DEFERRED(本轮不瘦身,章程不变)。
