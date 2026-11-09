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
| quality_status | PASS / DEGRADED / MISSING / unknown |
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

- **doctor**: {python, platform, env{key→{configured,purpose}}(模型面= MODEL_API_KEY/MODEL_BASE_URL/MODEL_NAME 三行;v2.1 唯一凭证面,旧变量行已删除;只报已配置与否), model_key_note?(未配齐三参时的中性提示;v2.1 键名,旧医生面键已删除), snapshot{available,note,target_date,gate_a,missing,degraded,sources_status}, data_freshness{prefix→最新文件}, last_run{available,ledger_file,run_at,success_count,critical_steps_all_ok,gate_a,snapshot_id,allow_formal_report,critical_steps}, skill{source_present,project_install_present}}
- **update**: {exit_code, exit_semantics, output_tail(尾40行), critical_tail(⛔/❌/Traceback/ERROR/失败/错误 关键行,尾10行,留底根因), stderr_tail};stdout 恒单 JSON,进度提示走 stderr;三条 tail 均过密钥脱敏;确认门: 无 --yes → error.kind=confirmation_required
- **overview**: {economies{代码→{label,n_metrics,n_missing,observation_span,metrics[]}}, supported_hint}
- **changes**: {n_metrics, n_missing, by_asset_class{类→节点[]}, window_note}
- **history**: 无 --metric → {series_capable_metrics[](每项含 metric_id,label,unit,unit_family,frequency,first,last,n,calendar,release_semantics,**time_semantics{observation_period_kind,release_date_available}**(注册表人工登记键纯透传,缺键=null 不默认;A-fin 2026-11-09),**supported_stats**(由 unit_family 机械推导的可用统计面)), note};有 → {series{metric_id,label,unit,unit_family,frequency,identity,calc,n,first,last,dates[],values[],source}}
- **compare**: `--metrics A,B [--start YYYY-MM-DD --end YYYY-MM-DD] [--window N | --lag K]` → {mode:'metrics', sides[2]{...同 history 单序列字段 + interval_change_common_window(共同窗区间变动;基准=窗前末笔,窗前无观测→available:false 不编造) + **quality_status**(快照事实层透传,无事实→null) + **release_note**(注册表 release_semantics 透传,口径在册) + **time_semantics{observation_period_kind,release_date_available}**(A-fin: 注册表人工登记纯透传;快照 fact 层带 release_date 实测值时覆盖登记=数据>登记,release_date+release_date_source 随行) + aggregation?**(被聚合侧;月×月双侧各带)**}, alignment{**mode('exact_date' 精确日内交 | 'month_grid' 自然月网格)**, n_common_observations(=水平观测数,off-by-one 已修;月网格=共同月份数), n_level_observations, n_change_pairs(=水平数−1,几何变化对), common_first/common_last(月网格为 'YYYY-MM' 月键), **a_dropped/b_dropped(跨历掉落: 各侧未进入共同窗的观测数;月网格口径=月数)**, **research_mode_gate(A-fin 研究模式门,机械数据条件)**{descriptive:恒'available', event_study:任一侧 release_date_available!==true→'blocked: 无发布日, 不得按发布日对齐/不得声称事件研究'否则'available', realtime_info_set:data/daily 该日存在 _vN 历史版本→'available(经 select_snapshot 点时取版)'否则'blocked: 无历史版本, 修订值≠当时值'}, note(含"不做异常值处理(原始值直算)")}, **pearson_returns(单位感知变化相关: 利率侧按 pp、价格侧按 pct,count 族 pct 近似——不再混算)**, change_basis{a,b}('pct'|'pp'), n_change_pairs(剔除丢弃后实际参与对数), dropped_null, zero_base_dropped(**A-fin: 零基过滤按族独立**——仅 price/count 侧前值 0 丢整对,rate 侧前值 0 的 pp 变化数学有效保留;计数只含 price/count 侧零基), sample_note?(<30对;n_change_pairs=0 时为专门文案"相关性不可计算,勿引用"), **rolling?**(仅 --window N≥2: {window, n_windows, first/last{as_of,rho}, max, min, basis}=最近 N 个单位感知变化对的 diff 基 pearson(复用 rhq.rolling_correlation,首值自第 N+1 个变化日起,需差分样本满 N);变化对不足窗长→n_windows=0+note;不改全窗 pearson_returns), **lagged?**(仅 --lag K: {lag, rho, n_lag_pairs(=n_change_pairs−|K|), n_lag_expected, basis(配对=(A第i个变化,B第i−k个变化);k>0=B领先k个变化对先动), warning_if_insufficient?(n_lag<3→rho=null+提示)};pearson 复用零新统计,不扫全 lag 域)};--start/--end=指令窗口,**对齐前**先过滤两侧(空窗→error.kind=empty_window rc=1);--window 无 --metrics 或 N<2 → error.kind=bad_window rc=2;**--lag 无 --metrics 或与 --window 同用 → error.kind=bad_lag rc=2(A-fin: 互斥防输出歧义)**;两侧频率不同且低频侧=月频 → 默认 month_grid(高频侧聚合到自然月,代表=期内末值 align_to_month,月键 YYYY-MM 内交,该侧 sides[].aggregation 披露);**月×月(双侧月频) → month_grid 月键内交**(A-fin: 两侧各取月键,同格多观测取末值,锚日巧合不作为对齐前提;01 锚下月键≡日键,现役数值不变),否则 exact_date;date_gap 阈值频率归一: 月频参与 7→45 天(月网格口径=缺整月才报,月步长>1 报"缺失月份");任一侧 unit_family='other' → error.kind=incomparable_units;--economies → {mode:'economies', economies{...同overview}};--assets → {mode:'assets', pairs[](引擎12对,含 disclosure/n_20d/n_60d/window), missing[]}
- **research**: {status(answered/refusal/out_of_scope/no_registry_identity/unmapped/error), answer_text, values, unresolved, supported_hint, economy_fallback?(单经济体问题附概览节点), model?(仅 --explain;未配齐模型三参时 ok=false+中性未配置提示;v2.1 键名 model,旧厂商别名旗标已彻底删除), archived_query_id?(仅 --archive)};--note=用户备注(落 sidecar 前过密钥脱敏)、--follow-up-of=关联前档 query_id(校验失败 rc=2),两者随 research-full sidecar 落档;**unmapped/no_registry_identity 拒答文本末尾附 Agent 组合导流行(任务F C-4)**: 自由研究问题→history(列出可用指标)/compare(单位感知对齐)/overview/changes 由 Agent 组织
- **archive**: save → {saved, query_id, note}(另有 --note/--follow-up-of,独立保存 sidecar 中 answer 相关字段如实 null);**任务F(W10)完整成果六参: --answer-text/--evidence/--statistics/--hypotheses/--open-questions/--as-of**——Agent 成果直存 sidecar 对应键(全部文本过 redact;--as-of 落 research_as_of 位;不带=旧行为,成果键 null);**前置: save(含六参直存)需本地已有研究快照(先跑过 update/run_weekly),零数据环境 no_snapshot 拒存 rc=1**;list → {n_total, records[]{query_id,created_at,question_text,snapshot_id,ir_stage,has_full,user_note?}};get → **双视图: data.record(基档 QB-*.json 原样)+data.full?(sidecar 合并视图;成果文本在 data.full.answer_text**,不在 record)**,full 含作答正文/AI解释原文(model 键)/warnings/violations/user_note/follow_up_of/evidence/statistics/hypotheses/open_questions(旧 sidecar 缺键归一 null;旧档 glm 键读侧归一映射到 model;record_type 保 query_history)

## 退出码

`0` 进程成功(research 诚实拒答/未支持也在此列,看 ok/data.status);`1` 执行错误(无快照/无序列/确认缺失/单位族不可比 incomparable_units/compare 窗口空窗 empty_window 等);`2` 用法错误(未知经济体/参数缺失/无效 --follow-up-of invalid_follow_up/compare --window 用法违规 bad_window/compare --lag 用法违规或与 --window 互斥 bad_lag)。

## 纪律 lint 工具(自撰事实位文本自检)

给 AI 的提示: 你自己撰写"事实性描述"位文本(表格关键信号列、无标注的接地转述)前,先跑 lint 自检,零 violation 再输出:

```bash
python3 -c 'import sys; sys.path.insert(0, "<engine_root>"); from ia_cli import lint_fact_contract_text as L; print(L("""待检文本,可多行"""))'
```

返回 `[]` 即干净;非空则按 `kind` 修正(causal_claim_in_fact_position → 移入【推断】/【假设】/【尚未验证】或删除(批2 W10 D5 四分: 事实/推断/假设/尚未验证,三种标记后文字不计事实位);unsupported_composition_claim → 删除成分/权重断言或降级为【假设】并明示无法验证)。
