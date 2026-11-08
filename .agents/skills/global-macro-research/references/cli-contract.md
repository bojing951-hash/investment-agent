# ia_cli.py JSON 输出契约(完整版)

所有能力输出单个 JSON 对象到 stdout。本文是字段全表;SKILL.md 内是速查版。

## 信封(所有能力共有)

| 字段 | 类型 | 说明 |
|---|---|---|
| ok | bool | 语义成败(research 的诚实拒答 ok=false 但退出码 0) |
| capability | str | doctor/update/overview/changes/history/compare/research/archive |
| engine_root | str | 引擎仓库根绝对路径 |
| snapshot_id | str\|null | 所用研究快照 ID(未用到快照时 null) |
| target_date / research_as_of | str\|null | 研究目标日 / 快照生成时刻 |
| gate_a | str\|null | PASS / DEGRADED / FAIL / 无快照 |
| data | object | 能力负载(下分节) |
| warnings | list[str] | 引擎强制警示,必须转述用户 |
| violations | list[object] | 仅 research: 纪律违规(成分编造等),出现即文本不可信 |
| error | object | 仅 ok=false: {kind, message, hint},永不空串 |

## 数值节点(overview/changes/compare 各处通用)

| 字段 | 说明 |
|---|---|
| metric_id / display_name | 注册表身份 |
| value | 原始数值;缺失=null(绝不 0) |
| presence | present / missing |
| absence_reason | missing 时的原因(来自 Gate A 明细) |
| unit / unit_family / unit_subfamily | 单位;族=rate/price/count/other;汇率另有 subfamily=fx |
| frequency | 日/月频等 |
| asset_class | 注册表资产类 |
| observation_date | **该数值的观测日**(各指标不同!) |
| as_of | 采集时刻 |
| quality_status | PASS / DEGRADED / MISSIED / unknown |
| issues | 质量问题列表 |
| source | {collector, file} |
| identity | {instrument, is_proxy, proxy_of, adjustment, market_seat, economy} |
| calc | 引擎口径说明原文(汇率方向语义在这里) |
| changes[] | 变化节点列表(下表) |

## 变化节点

| 字段 | 说明 |
|---|---|
| window | week / mtd / ytd |
| change_unit | **pct**(价格族) / **pp**(利率族,另有 bp_equivalent) / bp |
| value | 变化值原值 |
| basis_date / basis_value | 窗口基准日与基准值 |
| end_date | = observation_date |
| window_semantics | 窗口口径原文(如"ISO周(2026-11-02起)之前最后观测为基准") |
| sessions_in_window / expected_sessions | 窗口内/预期会话数 |
| formula | 引擎计算公式原文 |
| return_semantics | 价格类的收益口径(如"采集器复权") |

## 各能力 data 负载

- **doctor**: {python, platform, env{key→{configured,purpose}}, glm_key_note?, snapshot{available,note,target_date,gate_a,missing,degraded,sources_status}, data_freshness{prefix→最新文件}, last_run{available,ledger_file,run_at,success_count,critical_steps_all_ok,gate_a,snapshot_id,allow_formal_report,critical_steps}, skill{source_present,project_install_present}}
- **update**: {exit_code, exit_semantics, output_tail, stderr_tail};确认门: 无 --yes → error.kind=confirmation_required
- **overview**: {economies{代码→{label,n_metrics,n_missing,observation_span,metrics[]}}, supported_hint}
- **changes**: {n_metrics, n_missing, by_asset_class{类→节点[]}, window_note}
- **history**: 无 --metric → {series_capable_metrics[], note};有 → {series{metric_id,label,unit,unit_family,frequency,identity,calc,n,first,last,dates[],values[],source}}
- **compare**: --metrics → {mode:'metrics', sides[2](含 interval_change_common_window), alignment{n_common_observations,common_first,common_last}, pearson_returns};--economies → {mode:'economies', economies{...同overview}};--assets → {mode:'assets', pairs[](引擎12对,含 disclosure/n_20d/n_60d/window), missing[]}
- **research**: {status(answered/refusal/out_of_scope/no_registry_identity/unmapped/error), answer_text, values, unresolved, supported_hint, economy_fallback?(单经济体问题附概览节点), glm?(仅 --glm), archived_query_id?(仅 --archive)}
- **archive**: save → {saved, query_id, note};list → {n_total, records[]{query_id,created_at,question_text,snapshot_id,ir_stage}};get → {record(完整档案记录)}

## 退出码

`0` 进程成功(research 诚实拒答/未支持也在此列,看 ok/data.status);`1` 执行错误(无快照/无序列/确认缺失等);`2` 用法错误(未知经济体/参数缺失)。
