# ia_cli.py JSON 输出契约(完整版)

所有能力输出单个 JSON 对象到 stdout。本文是字段全表;SKILL.md 内是速查版。

## 信封(所有能力共有)

| 字段 | 类型 | 说明 |
|---|---|---|
| ok | bool | 语义成败(research 的诚实拒答 ok=false 但退出码 0) |
| capability | str | doctor/update/overview/changes/history/compare/analog/research/archive |
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
- **compare**: `--metrics A,B [--start YYYY-MM-DD --end YYYY-MM-DD] [--window N | --lag K]` → {mode:'metrics', sides[2]{...同 history 单序列字段 + interval_change_common_window(共同窗区间变动;基准=窗前末笔,窗前无观测→available:false 不编造) + **quality_status**(快照事实层透传,无事实→null) + **release_note**(注册表 release_semantics 透传,口径在册) + **time_semantics{observation_period_kind,release_date_available}**(A-fin: 注册表人工登记纯透传;快照 fact 层带 release_date 实测值时覆盖登记=数据>登记,release_date+release_date_source 随行) + aggregation?**(被聚合侧;月×月双侧各带)**}, alignment{**mode('exact_date' 精确日内交 | 'month_grid' 自然月网格)**, n_common_observations(=水平观测数,off-by-one 已修;月网格=共同月份数), n_level_observations, n_change_pairs(=水平数−1,几何变化对), common_first/common_last(月网格为 'YYYY-MM' 月键), **a_dropped/b_dropped(跨历掉落: 各侧未进入共同窗的观测数;月网格口径=月数)**, **research_mode_gate(A-fin 研究模式门,机械数据条件;Charter7-1 起实时门对查询时窗负责)**{descriptive:恒'available', event_study:任一侧 release_date_available!==true→'blocked: 无发布日, 不得按发布日对齐/不得声称事件研究'否则'available', realtime_info_set:**对查询时窗负责**——无 --start(当前窗)→'available(现役快照即当前时点信息集;…同日_vN修订不构成跨日vintage)';有 --start→查询起点月窗=[start, min(--end, 起点月末日)]内存在**跨日vintage**(research_snapshot 基础日期,同日 _vN 归并不新增)→'available(…可经select_snapshot点时取版…)'否则'blocked: …起点月窗内无vintage快照…不得以今日修订口径冒充当时值'(blocked 文案内嵌现存 vintage 日期与如实原因);realtime_vintage_dates[]=现存跨日vintage日期清单}, note(含"不做异常值处理(原始值直算)")}, **pearson_returns(单位感知变化相关: 利率侧按 pp、价格侧按 pct,count 族 pct 近似——不再混算)**, change_basis{a,b}('pct'|'pp'), n_change_pairs(剔除丢弃后实际参与对数), dropped_null, zero_base_dropped(**A-fin: 零基过滤按族独立**——仅 price/count 侧前值 0 丢整对,rate 侧前值 0 的 pp 变化数学有效保留;计数只含 price/count 侧零基), sample_note?(<30对;n_change_pairs=0 时为专门文案"相关性不可计算,勿引用"), **rolling?**(仅 --window N≥2: {window, n_windows, first/last{as_of,rho}, max, min, basis}=最近 N 个单位感知变化对的 diff 基 pearson(复用 rhq.rolling_correlation,首值自第 N+1 个变化日起,需差分样本满 N);变化对不足窗长→n_windows=0+note;不改全窗 pearson_returns), **lagged?**(仅 --lag K: {lag, rho, n_lag_pairs(=n_change_pairs−|K|), n_lag_expected, basis(配对=(A第i个变化,B第i−k个变化);k>0=B领先k个变化对先动), warning_if_insufficient?(n_lag<3→rho=null+提示)};pearson 复用零新统计,不扫全 lag 域)};--start/--end=指令窗口,**对齐前**先过滤两侧(空窗→error.kind=empty_window rc=1;**空串/纯空白→bad_window rc=2 不再静默当无界,history --start/--end 同规**,D 线终验 2026-11-09);**单指标多窗口变化正式口径(P2-2, 2026-11-10, Case A 实战)**: 1月/1年/5年等单指标区间变化用**自配对** `compare --metrics X,X --start T-k --end T`(两侧同一指标,输出即该指标窗内区间变动)——变化值读 sides[].interval_change_common_window(单位纪律随族: 利率 pp/价格 pct/计数绝对差;基准=严格早于窗内首观测的最后观测,窗前无观测→available:false 不编造);示例: 1年 `ia_cli.py compare --metrics FED_FUNDS,FED_FUNDS --start 2025-11-10 --end 2026-11-10`、1月(把起点推前一个月)`--start 2026-10-10 --end 2026-11-10`、**3个月(自然月回退,Charter8 交付⑤正式示例)**`--start 2026-08-10 --end 2026-11-10`、5年同理;**empty_window 语义**: 月频序列 1m 窗常无当月新观测(发布滞后/月中提问)→窗口过滤后空窗即 empty_window rc=1,**这是诚实拒绝不是故障**——此时只引水平值(history),不得以旧观测差硬造"当月变化";不自建第二条窗口逻辑(与 compare 同一条 interval_change_common_window 链路,防口径分叉);--window 无 --metrics 或 N<2 → error.kind=bad_window rc=2;**--lag 无 --metrics 或与 --window 同用 → error.kind=bad_lag rc=2(A-fin: 互斥防输出歧义)**;两侧频率不同且低频侧=月频 → 默认 month_grid(高频侧聚合到自然月,代表=期内末值 align_to_month,月键 YYYY-MM 内交,该侧 sides[].aggregation 披露);**月×月(双侧月频) → month_grid 月键内交**(A-fin: 两侧各取月键,同格多观测取末值,锚日巧合不作为对齐前提;01 锚下月键≡日键,现役数值不变),否则 exact_date;date_gap 阈值频率归一: 月频参与 7→45 天(月网格口径=缺整月才报,月步长>1 报"缺失月份");任一侧 unit_family='other' → error.kind=incomparable_units;--economies → {mode:'economies', economies{...同overview}};--assets → {mode:'assets', pairs[](引擎12对,含 disclosure/n_20d/n_60d/window), missing[]}
- **research**: {status(answered/refusal/out_of_scope/no_registry_identity/unmapped/error), answer_text, values, unresolved, supported_hint, economy_fallback?(单经济体问题附概览节点), model?(仅 --explain;未配齐模型三参时 ok=false+中性未配置提示;v2.1 键名 model,旧厂商别名旗标已彻底删除), archived_query_id?(仅 --archive)};--note=用户备注(落 sidecar 前过密钥脱敏)、--follow-up-of=关联前档 query_id(校验失败 rc=2),两者随 research-full sidecar 落档;**unmapped/no_registry_identity 拒答文本末尾附 Agent 组合导流行(任务F C-4)**: 自由研究问题→history(列出可用指标)/compare(单位感知对齐)/overview/changes 由 Agent 组织
- **analog**(Charter6, 2026-11-10;Charter7 修订 2026-11-10): `analog [--anchor YYYY-MM --top N --weights a,b,c,d,e,f --no-aftermath]`(无短别名,能力名须全拼) → {anchor_month(缺省=最近完整月), feature_window_months, **state_vector**(六维: growth/inflation/rates/credit/volatility/valuation, 各维=特征窗均值; 特征级 expanding z), normalization(method='expanding z (t≤各自锚点月末; μ/σ=含当期历史均值/总体标准差σ)', min_history_months=36, **min_observations_note=36个月史按网格步长折算观测数(月网格36点/季网格12点——36个季观测=9年系旧误设,Charter7-4b)**), weights(六维,和=1; --weights 六个非负数校验和=1 否则 bad_weights rc=2), **feature_set{basis='anchor_admitted', features[], n_features, wsum}**(Charter7-2 **统一特征集**: 距离特征面由锚点侧准入结果唯一决定;分母 W_U 全候选一致**不逐候选重归一**——重归一会让缺数候选相对权重变相放大,系可操纵口径;候选缺 U 特征→missing_features{特征→原因}随行,排序=(缺席数升序,距离升序),偏差更大但缺数者不得反超完整证据候选), candidates{scanned, valid, dropped_overlap(候选>锚点−12月排除), dropped_insufficient, **n_independent_clusters_topN, cluster_dedup**(Charter7-5: 候选月相差<12个月=同簇(事后窗重叠),TOP-N 仅输出各簇排序最优代表;准入/距离/分位计算本身不变——修正确性非降门槛)}, **sort_basis**(P2-1, 2026-11-10: TOP-N 排序依据 '(n_missing, distance, month)' 逐字随行——缺席特征多者降位,**名次非纯距离序**,比较相似度以 distance 字段为准;Case B 实战 QB-20261110-023 曾把名次误读为纯距离序), top[]{rank, candidate_month, distance(加权 z 距离,统一特征集固定分母 W_U), **n_missing**(缺席特征数=排序首键,P2-1), distance_percentile, **dims{维→{contribution_share, z_gap}}**, features_detail(逐特征 anchor_z/cand_z/gap/**w_norm**=原始权/W_U,同一特征全候选一致), **norm_wsum**(=W_U 统一特征集权重和,**全候选一致**,Charter7-2), **accounted_wsum**(该候选实际覆盖权重)+**missing_features{特征→原因}**+**missing_wsum**(缺席权重份额)+**cluster_members[]**(同簇成员月清单), **aftermath**{SPX/UST_10Y/DXY/GOLD_F × 1m/3m/6m/12m(价格 pct/利率 pp)+**{资产}_window{h→{start,end}|null}**(Charter7-3: 逐窗实际起止观测日随行——起点=候选锚点月之后首个观测(次月首日起),终点=候选月+N月内最后观测,可自行复算)+unavailable_horizons(按资产各自; 窗末无起点后新观测→该 horizon null,不以 0 冒充)+label(事后非预测,含起止口径)+note(修订口径提示)}}, dispersion(topN_aftermath_sign_agreement; **basis=独立簇代表口径, n_independent_clusters 随行**,Charter7-5), research_mode_gate(**realtime_info_set 对锚点月查询时窗负责**: 锚点月窗内存在跨日vintage才available,同日_vN不算,Charter7-1), **disclosure(三段固定文案,逐字转述)**, **features_dropped_at_anchor{特征→原因}**(Charter7-4a: 锚点月无值的特征不再静默跳过——release_lag(月度发布滞后)/quarterly_grid(锚点非季末月)/no_value_at_anchor 等原因随行;维度缺席判据**双侧**(锚点有效维<6 或候选侧某维全部候选无有效特征均警示,Charter7-4d);候选有效维度只按统一特征集 U 内特征计(不在 U 的特征如锚点缺席的 SPX_PE_TTM 不得为候选积维度证据,Charter7-4c))};**拒答序(全部如实透出,不放宽)**: --weights 非法 bad_weights / --anchor 非月格式 bad_anchor(rc=2)→ 无快照 no_snapshot / 锚点月数据不完整 anchor_not_complete / 有效维历史不足 insufficient_history / 有效候选<8 insufficient_candidates(rc=1; 短数据下 insufficient_history/insufficient_candidates 属正确行为);--no-aftermath → top[].aftermath=null(排序不变);巧合旗标走 warnings(单维贡献>0.6/事后分歧<0.6,n≥3(独立簇口径)/维度缺席<6 双侧/TOP-1 与中位距离差<10% 不分离);别名序列(other 族)结构性不进特征面
- **archive**: save → {saved, query_id, snapshot_id, note}(另有 --note/--follow-up-of,独立保存 sidecar 中 answer 相关字段如实 null);**任务F(W10)完整成果六参: --answer-text/--evidence/--statistics/--hypotheses/--open-questions/--as-of**——Agent 成果直存 sidecar 对应键(全部文本过 redact;--as-of 落 research_as_of 位;不带=旧行为,成果键 null);**快照指针语义(C席观察②,2026-11-10): record.snapshot_id/digest 随注入快照走,save 默认注入最新快照——研究实际基于旧版时须 `--snapshot-id research_snapshot_YYYYMMDD_vN`(容忍短形 YYYYMMDD_vN;不存在/非规范 rc=2 snapshot_not_found),否则读者按指针找不到研究所用版本(QB-032/033 教训)**;**前置: save(含六参直存)需本地已有研究快照(先跑过 update/run_weekly),零数据环境 no_snapshot 拒存 rc=1**;list → {n_total, records[]{query_id,created_at,question_text,snapshot_id,ir_stage,has_full,user_note?}};get → **双视图: data.record(基档 QB-*.json 原样)+data.full?(sidecar 合并视图;成果文本在 data.full.answer_text**,不在 record)**,full 含作答正文/AI解释原文(model 键)/warnings/violations/user_note/follow_up_of/evidence/statistics/hypotheses/open_questions(旧 sidecar 缺键归一 null;旧档 glm 键读侧归一映射到 model;record_type 保 query_history)
- **views**(Charter8, 2026-11-10): `views list / get --view-id VIEW-YYYYMMDD-NNN / lint` → list → {schema_version:'1.1', views[]{view_id,institution,publish_date,view_horizon,subjects[],n_core_views,report_title}, n_views, n_quarantined, n_files, views_dir}(有隔离→warnings 提示);get → {view(合规件完整档)};lint → {schema_version, n_compliant, n_quarantined, n_files, quarantined[]{file,view_id,violations[]{field,rule,message}}}(有隔离 ok=false+rc=1,warnings 附违规规则集);隔离件 get 拒绝 error.kind=view_not_found_or_quarantined rc=1,缺 --view-id rc=2;**不依赖快照(信封 snapshot_id/target_date/research_as_of/gate_a=null)**;schema v1.1 要点: 条目 attribution∈{institution_stated,ai_inferred}(硬拦截,机构明示与 AI 推导不得含糊)、quote 任意 basis 可附原文佐证(≤500 字符,verbatim_quote 强制必填)、falsification_conditions 用 condition 键、revisions[]{date,change,source_url} 只追加;配套确定性验证(不经 ia_cli,直接脚本): `python3 scripts/view_verifier.py VIEW-... --mode A|B|C|all [--directions '{"SPX":"up"}'] [--snapshot-id research_snapshot_YYYYMMDD_vN]` → {ok,view_id,institution,publish_date,subjects,snapshot_id,target_date,gate_a,n_evidence,n_missing,n_supports,n_against,evidence[]{metric_id,subject,display_name,unit,unit_family,level,observation_date,quality_status,series_source,changes{1m,3m,1y}(interval_change 同 compare 自配对口径),relation,relation_note},missing[]{metric_id,reason},notes[]}(relation 仅显式 directions 下机械计算;verifier 零 AI 判断;快照默认最新,--snapshot-id 显式绑定同 archive save 款——短形容忍/不存在 rc=2 snapshot_not_found,envelope.snapshot_id 即验证所用版本;rc=0 成功/1 无 view 或无快照/2 用法错)

- **research-map**(Charter9 P4, 2026-11-11): `research-map [--views-dir DIR]` → {schema_version:'1.0', questions[10]{id(RQ1..RQ10),text(章程§五原文),primary_layer(客观事实|机构观点|AI推断|历史统计|条件情景),draws[],surface,data_faces[{kind(snapshot|views|transmission|archive|agent_judgment),…计数/覆盖/新鲜度}],commands[](既有能力确定性命令清单)}, nomination_inputs{conflicts[]{metric_id,bull[],bear[]}(forecast 可映射+方向可解析面内同指标多空对撞),pseudo_consensus_subjects[](恰1家机构覆盖主题),note(提名归编排层 Agent,引擎只产原料)}, art{m_table/falsification{present,n,ids?}+缺席如实 present:false}, observation_clock{present,n,entries?}(编排层维护 data/research/observation_clock.json;引擎只透传绝不代触发), notes[]};零模型零网络;AI 层问题(RQ3/RQ9)只给 agent_judgment 面+命令提示,答案归编排层明示 attribution;warnings 提示对撞/单源/ART 未文件化/观察钟未建

- **research-run**(R2/R3, 2026-11-11;R23 并入闭环): `research-run --question "..." [--archive] [--fanout] [--out-dir DIR]` → {report_dir, pipeline_version, steps[{step,ok,executed,note}](S1 拆问题→S11 落档,每步真子进程信封留档;analog 诚实拒答豁免 run_ok), layers_summary{L1_available,L1_n_rows,L2_vp_available,L2_n_views,L3_produced,L4_produced}(L3/L4 管线恒 false,归编排层 Agent), n_evidence_rows, fanout{requested,n_rq,n_executed,n_agent_layer}, archive{requested,archived_query_id}};报告落 report_dir/report.json+report.md(L1 事实行逐行 fact_id 源/L2 VP 面/证据索引);**R23 闭环: L3/L4 由 Agent 补作后经 research-attach 落位 produced=True**

- **research-attach**(R23 阶段四, 2026-11-13;R24 硬化): `research-attach --report-dir DIR --judgment FILE [--allow-failed-run]` → {report_dir, attached, blocked?, run_ok_at_attach?, layers_summary{L3_produced,L4_produced}, validation{passed,n_violations,violations[]{code,where,detail},n_contradictions,n_mechanism_chains,n_scenarios}};judgment schema v1.0(scripts/agent_judgment.py 模块docstring 全schema): {schema_version:'1.0', agent_declaration{attribution='ai_inferred'(硬校验)}, l3{contradictions[{id,statement,basis,competing_explanations[≥2],evidence_refs[](R24 CON-REF: 须≥1 可解析引用,或 no_anchor_reason 非空明示免锚——静默零锚拒收)], mechanism_chains[{id,name,links[{step,text,evidence_level E1|E2|E3,evidence_refs[](E1 必≥1 且须解析到本报告证据索引),missing_link_note(E2 须含"假设"),falsification_metric(E3 须注册表在册)}]}]}, l4{scenarios[≥2 并列]{id,role,rows{scenario(str,须含"假设"),asset_direction{direction,confidence_tier∈{有历史相似证据,有相关证据,纯逻辑推理},text,evidence_refs[]},sensitive_variables(list,1-2 注册表在册),falsification{metric_id 在册,threshold},trigger{condition,deadline YYYY-MM-DD 真日期}}}}}(R24 SCN-TYPE: 五行类型锁——scenario=str/asset_direction=dict/sensitive_variables=list/falsification=dict/trigger=dict,错型显式拒收);**校验器零生成零改写**: 过=produced True+attribution ai_inferred+judgment 原文副本落 report_dir/agent_judgment.json+report.md 重渲;不过=produced 保持 False+violations 落 report.json 供修订重提(绝不半落位);**R24 MINOR-4 门槛**: run_ok=False 的报告默认拒收(blocked='run_ok_false',layers 不动,attempt 随档),显式 --allow-failed-run 才放行且 run_ok_at_attach+allow_failed_run 随档可审计;rc: 0 过/1 违规/门槛拦或错误;warnings 载逐条违规明细+门槛提示

## 退出码

`0` 进程成功(research 诚实拒答/未支持也在此列,看 ok/data.status);`1` 执行错误(无快照/无序列/确认缺失/单位族不可比 incomparable_units/compare 窗口空窗 empty_window/analog no_snapshot·anchor_not_complete·insufficient_history·insufficient_candidates 等);`2` 用法错误(未知经济体/参数缺失/无效 --follow-up-of invalid_follow_up/compare --window 用法违规 bad_window/compare --lag 用法违规或与 --window 互斥 bad_lag/--start/--end 空串或纯空白 bad_window(含 history;曾静默当无界,D 线终验收紧)/analog --weights 非六数或和≠1 bad_weights·--anchor 非月格式 bad_anchor/archive --snapshot-id 不存在或非规范 snapshot_not_found)。

## 纪律 lint 工具(自撰事实位文本自检)

给 AI 的提示: 你自己撰写"事实性描述"位文本(表格关键信号列、无标注的接地转述)前,先跑 lint 自检,零 violation 再输出:

```bash
python3 -c 'import sys; sys.path.insert(0, "<engine_root>"); from ia_cli import lint_fact_contract_text as L; print(L("""待检文本,可多行"""))'
```

返回 `[]` 即干净;非空则按 `kind` 修正(causal_claim_in_fact_position → 移入【推断】/【假设】/【尚未验证】或删除(批2 W10 D5 四分: 事实/推断/假设/尚未验证,三种标记后文字不计事实位);unsupported_composition_claim → 删除成分/权重断言或降级为【假设】并明示无法验证)。
