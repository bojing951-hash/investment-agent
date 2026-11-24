# COMPLEXITY_BASELINE — 复杂度基线(章程§四.4,只测不瘦)

> **R33 重登(2026-11-25;任务4后更新)**: 上次登记(R32)后 Audit-R33 任务1~4
> (94f/64680L→96f/69250L,+2 文件/+4570 行,+7.1%,越 5% 门故登记): 任务1 历史证据
> 口径统一(`scripts/evidence_gate.py` 取数入口: 官方发布日期优先+事实/序列/派生值
> 绑同一冻结版本;`scripts/workbench_data.py` 采集档通道同口径)+任务2 政策时态
> (`scripts/agent_judgment.py`/`scripts/research_contract/judgment_contract.py`:
> 政策事件×断言时点×实施状态逐分句核验)+任务3 原问直答(新增模块
> `scripts/policy_question.py`: 研究年月/回看窗口/同比基期分别解析与分面块装配,
> S5–S8/席位装配/契约核验/attach 门共用;席位装配脚本
> `scripts/seat_tools/make_family_judgment.py`;`scripts/research_map_planner.py`/
> `scripts/research_orchestrator.py`/`ia_cli.py` 工单面扩展)+任务4 冷启动
> (`scripts/research_provenance.py` 日档守卫改观测图: 来源备注不计入指标覆盖;
> `run_weekly.py` 台账逐步时长/返回码/失败原因;`scripts/china_market_collector.py`
> 时间预算+A 股断点续采+随档 `collection_status`;`ia_cli.py` update 回执步骤与
> 守卫分流行;均非新增框架);测试面同步扩(216f/99261L→217f/103644L,r33 门+夹具)。
- 生产面: 96 py 文件 / 69250 行 / 1851 函数
- 测试面: 217 py 文件 / 103644 行

## 最大 10 文件(生产面)

| 文件 | 行数 |
|---|---|
| scripts/research_map_planner.py | 3943 |
| ia_cli.py | 3619 |
| scripts/research_orchestrator.py | 3510 |
| scripts/china_market_collector.py | 2435 |
| scripts/agent_judgment.py | 2385 |
| scripts/research_provenance.py | 2341 |
| scripts/research_contract/judgment_contract.py | 2235 |
| scripts/research_contract/text_consistency.py | 2036 |
| scripts/historical_coverage_audit.py | 1693 |
| scripts/report_generator.py | 1621 |

## 增长控制
- 新增框架/系统/重复模型: 须证明不可复用+登记成本(章程§四.4)
- 基线漂移>5% 未登记理由 → `complexity_baseline.py --check` 红
- 重构候选只进 CODEBASE_SIMPLIFICATION_BACKLOG(DEFERRED,本轮不执行)
