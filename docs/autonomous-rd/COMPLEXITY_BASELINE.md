# COMPLEXITY_BASELINE — 复杂度基线(章程§四.4,只测不瘦)

> **R33 重登(2026-11-25;任务5后更新)**: 上次登记(任务4后)后 Audit-R33 任务5
> (预期差研究接入正式入口;生产面 96f/69250L/1851fn→98f/74524L/1999fn,+2 文件/
> +5274 行/+148 函数,+7.6%,越 5% 门故登记): 新增模块 `scripts/expectations_gap.py`
> (预期差对照块: 机构观点库×同期限市场定价×事实逐行确定性对照,候选≠结论;证伪
> 窗口/事后表现/到期核验;观点库解析与确定性验证复用既有 `view_store`/`view_verifier`,
> 定价取既有冻结曲线,不新增数据源)+席位装配脚本
> `scripts/seat_tools/make_expectations_gap_judgment.py`(只服务其预设的真实工单;
> 自检不过即拒写);`ia_cli.py` research-one 增预期差单型入口与席位回声;
> `scripts/research_contract/judgment_contract.py` 回声/结构化对质/观测窗三项软契约
> (字段在场才核,旧档零变化);`scripts/research_map_planner.py` 计划分流、对照面取数
> 分级并入、对质观测窗同窗读数(规则唯一出处 `_face_off_window_points`);
> `scripts/research_orchestrator.py`/`scripts/agent_judgment.py` 交付门与读者面;均为
> 现有模块内的工单面扩展,非新增框架/系统;独立席首轮 REVISE 后的修订(同批未提交
> 改动,含门在定稿时抓出的对质观测窗四处缺陷)不另计。测试面同步扩
> (217f/103644L→217f/105789L,r33 门 §T5 a–g+合成观点夹具,夹具全部虚构机构)。
- 生产面: 98 py 文件 / 74524 行 / 1999 函数
- 测试面: 217 py 文件 / 105789 行

## 最大 10 文件(生产面)

| 文件 | 行数 |
|---|---|
| scripts/research_map_planner.py | 4170 |
| ia_cli.py | 3745 |
| scripts/research_orchestrator.py | 3627 |
| scripts/research_contract/judgment_contract.py | 2707 |
| scripts/china_market_collector.py | 2435 |
| scripts/agent_judgment.py | 2404 |
| scripts/research_provenance.py | 2341 |
| scripts/expectations_gap.py | 2285 |
| scripts/research_contract/text_consistency.py | 2036 |
| scripts/seat_tools/make_expectations_gap_judgment.py | 2028 |

## 增长控制
- 新增框架/系统/重复模型: 须证明不可复用+登记成本(章程§四.4)
- 基线漂移>5% 未登记理由 → `complexity_baseline.py --check` 红
- 重构候选只进 CODEBASE_SIMPLIFICATION_BACKLOG(DEFERRED,本轮不执行)
