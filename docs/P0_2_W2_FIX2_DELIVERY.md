# IA-P0-2-W2-FIX2 交付报告: Gate A 严格截止时间与真实发布时间精度修复

- 任务: IA-P0-2-W2-FIX2 (指令 IA-P0-2-W2-FIX2-DEV-v1.0)
- 分支: dev/p0-2-w2 | 仓库: bojing951-hash/investment-agent (DEV=/Users/cast/investment-agent-dev)
- 日期: 2026-10-29
- 状态结论: **CODE FIXED — 独立验收材料齐备, READY FOR W2 INDEPENDENT ACCEPTANCE**
  (最终裁决权属 Agent 4; HSAHP 政策已获用户第四轮批准, 见§14)

## 1. 开发前基线

- 起点: `124a26641dcf7aa84d32e87031b55a936ca94655` (W2-FIX1 最终固定提交, 工作树clean)
- origin/main: `50b5d13` (全程未合并main/未force push)

## 2. 最终提交

- FIX2 实现提交: 见 git log (本文档首次随实现提交入库)
- FIX2 最终固定提交: 本交付文档最后一次提交即最终提交(其SHA见§18 CI head_sha
  与 `git log -1 dev/p0-2-w2`; 交付文档无法含自身哈希, 以CI运行记录为准)

## 3. 变更范围

- 增量 diff(124a266→FIX2最终): §18 CI 页面 diff 链接与统计
- 累计 W2 diff(69d7fc7→FIX2最终): 同上 base 版本切换
- 改动文件(实现): scripts/freshness_policy.py(新增解析/比较原语+assess点时重写),
  scripts/research_provenance.py(研究截止三态), scripts/fact_engine.py(发布分支
  统一消费瞬时判断), scripts/data_validator.py(警示披露绝对时刻关系),
  config/metric_registry.json(HSAHP窗口10→7, **1行**, 用户批准),
  tests/test_p02_w2_fix2.py(新增43检查), tests/test_p02_w2.py(A6a三轮→四轮,
  唯一期望值变更, 理由: 第四轮批准新增, 前三轮断言原文保留),
  docs/P0_2_W2_FRESHNESS.md/.json(第4轮记录+HSAHP行, JSON仅HSAHP块4行),
  docs/P0_2_W2_FIX1_POLICY_HK_CALENDAR.md(修订记录块, 原文保留),
  docs/P0_2_W2_FIX2_POLICY_HSAHP.md(新), docs/P0_2_W2_FIX2_APPROVAL_FORENSICS.md(新),
  本交付文档
- 未改: Gate A/B 架构, P0-1 来源授权边界, W1 身份修复, 81项其余窗口,
  新闻/真实数据验收模块, 任何 Mac LIVE 内容, launchd, 历史快照/报告

## 4. FIX2-01: Gate A 研究截止三态(截断洗白封堵)

缺陷: `rp.recompute_gate_a()` 原逻辑对 research_as_of 先 `[:10]` 截断,
`'2026-10-24INVALID'`+`target_date='20261024'` 可形成有效 Gate A(截止洗白)。

修复(scripts/research_provenance.py, `_ABSENT` 哨兵三态):
- **态A** research_as_of 合法(完整ISO日期/时间戳, 经 `fp.parse_temporal_value`
  整串验证, 绝不截断)→ 取研究日期, `cutoff_source='research_as_of'`;
- **态B** 键**真缺席**→受控历史兼容回退: target_date 须严格 `re.fullmatch(r'\d{8}')`
  且为真实日历日(`'20261024INVALID'/'20261024xxx'/'20260230'/'2026102400'/
  非字符串`一律不可用), 记 `cutoff_source='target_date_fallback'` 可诊断;
- **态C** 显式存在但非法(非法后缀/假日历/非字符串/空串/不可解释时间类型如
  `datetime.time`)→直接 fail-closed, reason 点名"显式存在但非法…不得经
  target_date 回退洗白…不得放行", **绝无 fallback**。

证据: test_p02_w2_fix2 A1a-A6(单元三态×12反例+真实链路洗白组合对照+
正式入口 da/rg 双拒+三正向: 合法both=PASS/缺as_of+合法tgt=PASS(回退)/
缺as_of+非法tgt=None)。

## 5. target_date 受控回退语义

仅态B且严格八位真实日历日可用; 回退事实经 `cutoff_source` 持久披露;
回退源自身非法时 reason 点名"缺失且回退不可用"并 fail-closed(A4×6反例,
F3 危险run2 磁盘级验证)。态C 下 target_date 合法也**不构成**回退(A5)。

## 6. FIX2-02: 时间精度与UTC偏移保真

缺陷: `fp.parse_instant()` 返回日期, 丢失时刻/UTC偏移——同日晚间发布被
"日期相等"放行。

新增原语(scripts/freshness_policy.py, 保留 parse_instant 日粒度接口):
- `parse_temporal_value(value)` → dict{ok, raw, date, precision
  (DATE_ONLY|DATETIME), tz_aware, utc_offset('+HH:MM'), instant, error};
  bool 先于数值拒; datetime/date 实例/完整ISO串(含Z/±HH:MM/空格分隔/微秒)
  整串验证; 原始输入原样保留(raw)。
- `compare_release_availability(release, as_of)` → verdict:
  RELEASED_BEFORE/RELEASED_AFTER(granularity INSTANT|DAY),
  UNVERIFIED_SAME_DAY, UNVERIFIED_TZ, INVALID_RELEASE, INVALID_AS_OF;
  A 双aware→绝对时刻比较(任意偏移, detail 含小时差);
  B 双date-only→遗留日粒度判定(标注DAY);
  C 同名义日(精度不足)→UNVERIFIED_SAME_DAY;
  D 相邻日且含无时区时刻→UNVERIFIED_TZ(任何时区解释下先后均可能, 绝不
  假设UTC/HKT/本地); E 非法输入→INVALID_*。
- `fp.assess` 点时字段(point_in_time)携带 status/release_date/granularity/
  detail: RELEASED_BEFORE→'OK'(INSTANT|DAY); RELEASED_AFTER→
  'RELEASE_AFTER_AS_OF'(fresh=False); UNVERIFIED_*→新状态
  **POINT_IN_TIME_UNCERTIFIED**(fresh=True日粒度兼容, 绝不宣称已验证点时)。

证据: A1, B1, C1, D1-D3, E1-E4; FIX1 兼容(B5 date-only OK/B4 点时不可得/
E4-E5)不回退。

## 7. 同日未来发布拒绝(指令核心反例)

CPI obs=2026-09-01, as_of=2026-10-24T08:00:00+08:00, release=
2026-10-24T20:00:00+08:00:
- 共享原语: RELEASED_AFTER(INSTANT, 差+12小时)(旧日期比较=相等放行的漏洞已封);
- fp.assess: NOT_AVAILABLE_AT_AS_OF, fresh=False;
- fe.validate_fact(真实入口): FAIL(category=release, 消息含原始release/as_of/
  绝对差+NOT_AVAILABLE_AT_AS_OF)→core CPI 事实质量失败;
- 真实链路(sb透传): Gate A=FAIL; dv.is_fresh_anchor=False; 警示含INSTANT+20:00;
- 数据包(da exit2无包)+周报(rg exit2)+GLM=0+零状态回写; ae 证据拒; dpo 拒。
证据: B1-B5。

## 8. 跨时区(名义日期序≠绝对时刻序)

两方向各一对(A1 D1/D2):
- 对1: release 2026-10-24T02:00+08(=10-23T18Z) vs as_of 2026-10-23T15:00-04
  (=19Z)→名义序"晚"绝对序"早"→RELEASED_BEFORE(旧日期比较会误拒);
- 对2: release 2026-10-23T18:00-05(=23Z) vs as_of 2026-10-24T00:00+08
  (=10-23T16Z)→名义序"早"绝对序"晚"→RELEASED_AFTER+assess+真实
  validate_fact 双拒(旧日期比较会误放)。
UTC偏移(-04:00/-05:00/+08:00)在 parse_temporal_value 与判定 detail 中
保真可审计(D3)。

## 9. date-only 与 datetime 边界(精度不足守恒态)

- date release×datetime as_of 同名义日→UNVERIFIED_SAME_DAY;
- naive×aware 相邻日(双向)→UNVERIFIED_TZ;
- 统一守恒映射: fresh=True(日粒度可得, 历史兼容)+point_in_time=
  POINT_IN_TIME_UNCERTIFIED+fe 仅 INFO('点时未认证')绝不 FAIL 既有数据,
  绝不认证"已验证点时可得"; Gate A/B 语义: 可得性不降级(不误伤), 点时
  认证不升级(不虚报)。缺 release 维持 RELEASE_UNKNOWN(不伪造, B1/E5)。
证据: E1-E5; 双date-only遗留口径(DAY判定+点时OK)与跨日 NOT_AVAILABLE
(DAY)完整保留(FIX1 B4/B5/B1 兼容零期望变更)。

## 10. FIX2-03: 全消费方统一语义

| 消费方 | 统一后行为 | 证据 |
|---|---|---|
| fp.assess | compare_release_availability 驱动点时三态 | B1/E1 |
| fe.validate_fact | 真实消费统一瞬时可得判断: INVALID_RELEASE FAIL/早于观测 FAIL/RELEASED_AFTER FAIL(NOT_AVAILABLE_AT_AS_OF)/UNVERIFIED_* INFO/缺release WARN(RELEASE_UNKNOWN) | B2/B3/E1/E2 |
| rp.recompute_gate_a/gate_status | 研究截止三态(§4) | A2-A6 |
| dv.is_fresh_anchor | 经 assess 全精度(fresh=False 当且仅当点时不可得) | B4 |
| dv.stale_anchor_warning | 披露实际时刻关系"[INSTANT;绝对差]"(非两同日含糊) | B4 |
| sb.build_snapshot/build_anchors | release 字符串原样透传(不加/不删) | B4(锚点带偏移ts) |
| rg 周报预检 / da 数据包 | 经 gate_status 重算拒绝(B/A5b/F2) | A5b/B5/F2 |
| ae.verify_evidence_items | 非新鲜('数据过期'族)拒收未来发布证据 | B5 |
| dpo._metric_problem | 质量/新鲜度任一不过即不记录长期观察 | B5 |

未放松: metric_id-来源绑定(FIX1 C组不受影响, 53/0), 快照批次身份, 内容
摘要, 发布元数据透传, 报告发布保护(F组); 自报时间戳不授予任何来源授权
(FIX1 B9b 兼容保留)。

## 11. 联合 E2E

test_p02_w2_fix2 场景A-F: 真实模块+真实文件系统+隔离临时目录, mock 仅限
外部GLM(≥500字替身,只计数)/固定时钟/外部装载(承FIX1口径)。43检查全绿。
另: 全仓库 E2E(test_e2e_orig14 41/0, test_e2e_frozen14 复核通过,
test_e2e_four_weeks 59/0)。

## 12. 历史报告与长期状态保护

场景F: 真实发布事务(exit0+GLM恰1次)→四对象(报告正文/发布状态/thesis.json/
allocation_views.json)SHA-256执行前基线→危险run1(磁盘快照注入显式非法
research_as_of+合法target_date洗白诱饵)与危险run2(剔除as_of+非法回退源)
→da/rg 双拒(exit2+GLM=0+零状态回写)→四对象哈希全程不变+无新报告/状态+
published=true仅发布日+formal身份有效+scan_formal不变+失败reason可诊断
(F2-F5)。

## 13. FIX2-04: 政策批准原始对话证据(只读取证)

docs/P0_2_W2_FIX2_APPROVAL_FORENSICS.md:
- 原始文件: 本Mac会话日志 b16f1517-…jsonl(只读, 未修改任何字节; 取证时刻
  SHA-256=34b23023…45f5, 12553908字节; 文件为活动日志仅追加, 核验以行号
  内容逐字节比对为准);
- 四轮批准(R1 2026-10-29T07:55:51.871Z问/07:57:50.613Z答; R2 08:08:20.160Z/
  08:37:35.660Z; R3 DFEDTAR 11:19:26.283Z/11:25:31.034Z; R4 HSAHP
  13:21:35.613Z/14:31:53.712Z)各含: 消息uuid(问/答)、tool_use call_id 配对
  (tool_result.tool_use_id 严格一致)、行号(先问后答无乱序)、逐字问题全文+
  选项描述+批复原文、逐摘录SHA-256;
- 复核结论: FIX1 文档既有时间戳(R1/R2)取证后**全部准确**; FIX2-05 裁决
  时间初记14:32:07Z(批复后date读数)已更正为精确事件14:31:53.712Z;
- 证据等级如实: 仓库摘录=C+D, 原始认证 U 级仅 Agent 4/授权独立核验人读取
  原始JSONL可升级; 按§7.3未上传任何完整JSONL, 摘录仅政策问答(无密钥/
  无非政策内容)。

## 14. FIX2-05: HSAHP 政策依据修正与第四轮批准

- 官方事实(指令交付, Agent 4确认): 恒生AH指数系列在**内地和/或香港市场
  开市期间**计算与发布→HSAHP观测日历=两地**并集**; FIX1-05 的"A/H须同时
  开市否则溢价无法计算"前提**错误**, 已在 P0_2_W2_FIX1_POLICY_HK_CALENDAR.md
  顶部加修订记录(6条逐项指出对HSAHP失效/对SB_FLOW仍成立, 原文保留)。
- 外部佐证: 官方页面 hsi.com.hk/eng/indexes/all-indexes/ahpremium(JS渲染
  无静态正文); Index Operation Guide PDF 已存档本地(CID字体不可提取, 未
  纳入证据链); 一次WebFetch遇GLM 1301内容风控未重试。证据等级: 指令确认
  (可信根)+URL佐证。
- 五日历区分(修正后): 理论计算日历=并集; 发布日历≈并集; 采集器实际源=
  新浪rt_hkHSAHP直连(主)/新浪日K(备)/东财(末选)(china_market_collector
  fetch_ah_premium); 可取新观测日=并集开市日; 合理采集滞后=业务判断项
  (禁读LIVE, 无源更新间隔统计)。
- 第四轮批准(2026-10-29T14:31:53.712Z, AskUserQuestion, 用户亲选
  **"缩短至7天(推荐)"**): HSAHP 10→7(并集日历最大正常缺口≈5天+2天采集
  缓冲); 未选: 5天(零缓冲)/维持10(纯采集容忍, 无统计支撑)。裁决逐字/
  选项描述/未选存档见 P0_2_W2_FIX2_POLICY_HSAHP.md §5。
- 变更执行: config/metric_registry.json HSAHP freshness.max_calendar_lag_days
  10→7(**外科手术式1行diff**, 其余80项逐字节未动); 81项矩阵(MD+JSON)第4轮
  记录+HSAHP行同步(JSON仅HSAHP块4字段+totals/rounds/legend); A6a期望
  三轮→四轮(唯一期望值变更, 理由=第四轮批准, 前三轮断言原文保留)。

## 15. SB_FLOW 单独日历(不受影响, 维持10)

SB_FLOW(南向净买入)观测日历=沪深港通**通道开放日=两地开市交集**: 大陆
春节/国庆8~9天长假通道整体关闭→缺口真实存在→10天窗维持有据, 与HSAHP的
并集修正无关。SB_FLOW=10/HSI=5/HSCEI=5/DFEDTARU/L=10 本轮零改动(矩阵
复核: 仅HSAHP行变更)。

## 16. 最终 DEV-LIVE 只读核验(FIX2-06)

**以下在最终代码提交后、只读执行**(开发会话不改Mac LIVE任何字节):

| 项 | DEV | LIVE |
|---|---|---|
| realpath | /Users/cast/investment-agent-dev | /Users/cast/AI内容/📕_AI投资项目/每周宏观追踪/investment-agent |
| inode | 60895116 | 22199716 |
| Git | dev/p0-2-w2 @ FIX2最终SHA(§18 CI head_sha) | 纯消费目录, 无.git, 不在版本管理内 |
| origin/main | 50b5d13(未合并main) | — |
| launchd | 无引用(dev路径) | com.user.investment.*指向LIVE路径(本轮零改动) |
| 关键源文件 | — | 6-8个关键文件SHA-256与P0-1固定版本(50b5d13 blob)一致(见§16.1) |

§16.1 最终核验输出(LIVE 8文件 hash-object 对比 50b5d13): 见最终提交后
回填段(§18 附注); 任何不一致将如实报告并停止。
GitHub侧可验证: 本报告+diff+CI; Mac本地只读可验证: 上表; 不可证明: 历史
瞬态(取证时点的文件系统状态一致性属只读快照声明)。

## 17. P0-1 与 W1 回归(零期望变更)

36/36 套件全绿(RC=0): P0-1 FIX1~FIX11(82/109/45/49/62/86/41/52/42/29/17),
W1(46/0)+W1-FIX1(41/0), W2(44/0)+W2-FIX1(53/0)+W2-FIX2(43/0), E2E
(41/0+复核+59/0), gate_chain(86/0), fact_engine(60/0), snapshot(46/0),
round3-6/p0/p1/p2/p4/p7/phase3/phase4/datafix 全部0失败; test_glm_live
RC=0(真实GLM按指令跳过)。除A6a(§14, 第四轮批准所致)外**零期望值变更**;
无任何原有测试删除/弱化。

## 18. 最新 GitHub Actions(CI 证据)

- 工作流: offline-tests.yml, workflow_dispatch, ref=dev/p0-2-w2
- 本报告首次提交后dispatch运行#1(head_sha=实现提交), 最终提交后dispatch
  运行#2(head_sha=最终提交): **以运行#2为准**——须显示 test_p02_w2_fix2
  exit=0(43/0), test_p02_w2_fix1 exit=0(53/0), test_p02_w2 exit=0(44/0),
  E2E 14+四周, W1/W1-FIX1, P0-1 FIX1~11, GLM skipped; 旧34套件绿CI不作为
  FIX2证据。运行链接与head_sha: 最终提交后回填。

## 19. 未解决事项与证据等级

| 事项 | 状态 | 证据等级 |
|---|---|---|
| FIX2-01/02/03 代码缺陷 | 已修复, 43+36套件证据 | 开发者离线验证(C+D), 待Agent 4独立复核(U待授) |
| HSAHP 政策 | 已获用户第四轮批准(14:31:53.712Z亲选7天)并执行 | 原始认证U(会话日志取证§13), 摘录C+D |
| 恒指官方方法事实 | 指令交付(Agent 4已确认)+官方URL佐证; PDF存档不可提取 | 指令确认根, 外部文本佐证不完整(如实) |
| 采集源更新间隔统计 | 不可得(禁读LIVE; DEV为合成) → 7天窗含2天缓冲属业务批准值 | 用户批准(§14), 非统计测量 |
| 四轮批准原始证据 | 取证文档已交付 | C+D; U级升级=Agent 4读原始JSONL(§13) |
| CI 最终运行 | 最终提交后dispatch(§18回填) | GitHub公开可验证 |
| DEV-LIVE 隔离 | 最终提交后只读核验(§16回填) | Mac本地只读 |

— 最终裁决权: Agent 4 独立工程验收。
