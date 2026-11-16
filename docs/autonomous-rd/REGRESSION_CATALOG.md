# REGRESSION_CATALOG — 回归测试分类(章程§四.3 L2 层)

> 历史故障家族 → 回归锚套件映射。每族=「曾真实发生过的故障形态」;
> 新增波次引入的新族须回填本档。只分类不重构。

## 家族 → 锚套件

| 家族 | 历史实例 | 回归锚 |
|---|---|---|
| 测试聚合器吞错(测级异常不进退出码) | RDG-20261116-012,R42(两潜伏 ~14 轮) | tests/test_rd_r42_aggregator_error_gate.py |
| argv 污染(模块级脚本读外来 argv) | RDG-012 残余⑦,R43 四件套+R44 test_round6 X6 | tests/test_rd_r43_pytest_caliber.py(§A-§D) |
| Gate B 提取器误杀 | R27 辛壬癸距离子五缺陷(两期真实报告) | tests/test_rd_r27_gateb_extractor.py |
| 检查面构造物泄漏(A 族) | RDG-20261116-013,R44(326→283) | tests/test_rd_r43_checkface_preprocess.py |
| 叙事方向漏报/误读 | R38/R40(MAJOR-3b 等) | tests/test_rd_r38_narrative_fx.py, test_rd_r40_narrative_guards.py |
| 判定面结构缺陷(表驱动单源) | R41(scorecard_spec) | tests/test_rd_r41_t8r2_leftovers.py |
| 状态-Git 失同步 | R20 家族 | tests/test_rd_r20_state_checkpoint.py, test_rd_r20_state_consistency.py, test_arch_reform_phase6.py |
| attach 链原子性/重复 | R36 三 NIT | tests/test_rd_r36_attach_nits.py |
| 序列权威通道判错 | R37(history_source) | tests/test_rd_r37_history_source_auth.py |
| 跳步渲染误导 | R39 | tests/test_rd_r39_skip_ledger.py |
| 金融数值正确性 | R22 四案 | tests/test_rd_r22_fin_correctness.py |
| Agent Native E2E/attach 契约 | R23/R24/R34 | test_rd_r23_*, test_rd_r25_*, 席位档套件 |

## 执行口径(与 L1 同一套件,口径不同)

- **L1 开发面**: 全量 exit 口径(CI 同)+ pytest 逐件口径
  (绿判据=rc∈{0,5} 或 rc=3 伴 SystemExit:0;R44 判据修正版)。
- **L2 回归面**: 波次受影响面按上表点名复跑+新波变异自证。
- **L3/L4**: scripts/product_acceptance_runner.py(净克隆)+独立席材料包。
