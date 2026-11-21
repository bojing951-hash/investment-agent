# COMPLEXITY_BASELINE — 复杂度基线(章程§四.4,只测不瘦)

> **R26 重登(2026-11-20)**: Audit-R21~R26 验收波次累积——生产面
> 93f/57909L→93f/60969L(+0 文件/+3060 行,+5.3%): R21 发布实录日历
> batches/R22 打印日≠变更日分记/R23 冻结源渲染/R24 政策事件面/
> R25 采集保全守卫+原问逐字/R26 指标身份+有效观测守卫强化+统计期末
> 与政策确认三日期分离+BoJ 实录表+草稿规则与逐组覆盖表——全部为既有
> 文件的验收工单扩展,非新增框架/重复模型;测试面同步扩(r18-r26 门)。

- 生产面: 93 py 文件 / 60969 行 / 1642 函数
- 测试面: 210 py 文件 / 94917 行

## 最大 10 文件(生产面)

| 文件 | 行数 |
|---|---|
| scripts/research_orchestrator.py | 2707 |
| scripts/research_map_planner.py | 2670 |
| ia_cli.py | 2652 |
| scripts/research_provenance.py | 2186 |
| scripts/research_contract/text_consistency.py | 2036 |
| scripts/china_market_collector.py | 2016 |
| scripts/research_contract/judgment_contract.py | 1713 |
| scripts/historical_coverage_audit.py | 1693 |
| scripts/report_generator.py | 1621 |
| scripts/allocation_engine.py | 1620 |

## 增长控制
- 新增框架/系统/重复模型: 须证明不可复用+登记成本(章程§四.4)
- 基线漂移>5% 未登记理由 → `complexity_baseline.py --check` 红
- 重构候选只进 CODEBASE_SIMPLIFICATION_BACKLOG(DEFERRED,本轮不执行)
