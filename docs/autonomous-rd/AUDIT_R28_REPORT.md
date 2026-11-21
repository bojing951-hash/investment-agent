# Audit-R28 交付报告(R73)

基线 **193c289**(独立审计基线,PR #1 dev/audit-fix-r1 尖)→ 本轮四任务
代码+门收口(提交 SHA 见 §6)。用户验收令四任务对应本报告四节;新门
tests/test_audit_r28_gate.py **37 判据**(34→36→37 随两整改段演进);回归 r7/r23/r24/r25/r26/r27
六门+全量电池见 §5;四席真实一问会话(原问 A/换问 B/残缺 C/临时开放问)
+ 离线重放见 §4。

## 0. 环境与既成状态

- 验收令四任务(用户原文): ①修默认入口——把流程约束装进用户实际使用的
  Claude Code 入口,安装配置一次后新会话只输入原问,由 research-one 自动
  完成取证、研判、独立语义审查、必要修订和报告交付;用同一入口实跑仓内
  question_A.txt 和 question_B.txt,保存原问与真实会话记录;归档停在用户
  裁定②修当期政策和日期——官方决议、核验覆盖截止和指标口径纳入同一
  交付判定;确认维持也更新核验日期;必需当期只有过期与未核验值、或缺
  用户指定的官方目标时,交付草稿、点名缺口并拒绝归档;按 2026-11-21
  复测 B(日本央行目标约 1.25%,9 月 18 日决议、9 月 24 日生效、10 月 30
  日维持);明确距上次调整的天数按哪一天计算;中国 LPR 各表统一读官方
  发布时间,复测 2026-11-20 09:00;覆盖 ECB 2024-06-06 决议缺档、政策
  确认维持、过期与未核验混合、缺指定目标和正常放行;验收日期和数值只作
  测试基准③修历史回答——保留美国类比标签,逐段按历史截点核对美中欧日,
  按地区和维度写出同步、分化或缺证,绑定实际公布日和数据版本;用 C 的
  2022 年 6 月叙述复测相对日期和无绝对日期的事后事实;事实按当时可知和
  事后实际落位,保留随后 3/6/12 个月的结果;独立审查同时复核机制链、
  竞争解释和区分指标④修离线重放——沿用现有报告/归档入口和 manifest,
  打包完整运行 SHA、原问、冻结输入与快照标识、views_digest.json、判定、
  裁决链和地图哈希;提供一条从干净目录执行的命令,用最终候选交付包
  离线重放同一工单,逐字节核对地图及裁决绑定;实测缺件和篡改拒绝、
  重复运行保留原档。最后用最终候选实际跑 A 原问、B 换问、C 缺核心数据
  和一条临时开放问;A/B 交正式读者报告与独立裁决,C 交草稿并实测拒绝
  归档;保留既有并发、取数和归档回归,跑全量测试并核对候选 SHA 对应的
  CI;在隔离目录完成归档验证;最终交一页验收结果;AC3 按真实到期证据
  填报;正式归档、合并、LIVE 和付费凭证由用户裁定;只在已有本轮推送
  授权时更新现有 PR。
- 独立审计基线=193c289(用户令指定),与本轮起点 HEAD 一致;全部 R28
  改动在其上叠加,先仓内门+电池收口再提交(提交链见 §6)。
- 验收树=/tmp/r70/r28-accept 隔离副本(git archive 干净树+CODE_VERSION.json
  全长 SHA 印章+LIVE 数据树只读复制+树内 install_skill);LIVE 数据树
  零写入,采集只在隔离树。**会话两代如实记录**: 先导代=2679629 树
  (A 全链 UPHELD/归档拒=B/C 缺当期正当拒;B/OPEN 即席作答暴露任务1
  缺陷→整改 48c03cb;C 先导 run 件因重建树未及拷贝而毁,幸存件=
  归档拒绝探针,见 session_C_pilot_2679629/README);**正式代=48c03cb
  树四席全跑**(整改后 CLAUDE.md 必读路由层在场,快照当日重build n=91
  含 CN_CPI_YOY 226,Gate A 如实 5 核心缺失=当族未采,草稿纪律吸收)。
- 运行 SHA 与会话/重放/CI 事实见 §4-§6(逐项随证据在档)。

## 1. 默认入口:问句路由纪律进技能面(任务1)

- **落位=.agents/skills/global-macro-research/SKILL.md 新增「问句路由
  纪律」节**(技能=用户实际使用的 Claude Code 入口;install_skill.py
  --target project 把 .agents 源装进树内 .claude/skills,安装配置一次后
  新会话默认加载): 收到用户消息先判类,**研究问句一律走正式闭环入口
  research-one**(单命令四段 plan→attach→report→archive,含独立语义审查
  与必要修订),不得以即席作答或 overview/changes/history/compare/analog
  等工具组合替代正式链回答研究问句。判类三分: 研究问句(宏观/市场/政策
  的水平、变化、对比、机制、转折、历史对照、观点验证)→正式链起步
  `research-one --stage plan --question-file <原问文件>`+报告交付后停等
  用户裁定;非研究查问(环境排障/引擎用法/字段口径/档案检索)→直接用
  对应能力;research-one 拒答后的探索披露→工具组合只做补充披露且结论层
  仍标注草稿面;模糊按研究问句处理(多走正式链的代价=多一轮机器校验,
  反向代价=无审计的即席结论)。
- R27 在案根因(R27 §4.1: 裸问句两轮即席作答=会话启动器丢程序性帧)
  在本任务的正道修法=把路由纪律做成**技能默认行为**而非会话级提示词
  补充——约束随技能安装走,不依赖每轮手工带帧。会话级脚本只保留环境
  面(权限/预算/禁令),零研究内容指示。
- 实跑: 同一入口跑仓内 question_A.txt(490B)与 question_B.txt(196B),
  原问与真实会话记录随证据入仓(§4);归档停在用户裁定(会话末态如实
  在档)。
- 门面(§A,3+1 判据): SKILL.md 路由纪律在场性——research-one 一词、
  「不得以即席作答…替代正式链」、停等用户裁定、「只输入原问」安装一次
  语义、两个新草稿类名在草稿纪律清单(任务2联动)、判类三分词面。
- **真实验收暴露的整改(48c03cb)**: 2679629 树四席先导实测——A/C(地图形
  问句)路由正常走正式链,但 **B(换问)/OPEN(开放问)两度即席作答**
  (compare 工具组合+叙事结论,零 research-one 链路,证据=
  r28-evidence/acceptance/session_B_first_adhoc 与 session_OPEN_first_
  adhoc)。根因=路由纪律只落 SKILL.md,**非地图形问句不触发技能加载**
  (技能可见≠技能被读)。正道修法=CLAUDE.md 增「研究问句路由」节
  (会话启动必读层,随仓安装即生效,不依赖技能被唤起): 研究问句一律
  research-one 正式链+不得即席作答+三分判类+停等用户裁定+模糊按研究
  问句处理,与技能内纪律同文同源;门新增 §A4 六词面断言(37/37 绿)。
  整改后四席(A 原问/B 换问/C 残缺/开放问)在 48c03cb 树全部重跑(§4)。

## 2. 当期政策与日期:官方记录面+三新日历能力(任务2)

- **日历 v1.5.0**(config/release_calendar.json,+3 生产条目共 17):
  RC-JP-BOJ-TARGET-2026-09(policy_decision: 决议 2026-09-18/生效
  2026-09-24/目标 1.25)、RC-JP-BOJ-MAINT-2026-10(policy_maintenance:
  2026-10-30 确认维持)、RC-CN-LPR-2026M11(first_publish 2026-11-20,
  **官方发布时刻 09:00**,official=true)。spec 逐条注记来源与口径;
  R25 v1.4.0 修订记事原样保留(r25 门 §B1 断言随结构演进放宽为
  只增不减,v1.4.0 记事仍在)。
- **freshness_policy.policy_decision_state(metric_id, as_of)**(纯日历
  文件面,零网络): 汇总可见的决议/维持条目→present/last_decision/
  last_effective/official_target/last_maintenance/**last_confirmed_on
  (核验覆盖截止=决议首发与维持发布的最近日——确认维持也更新核验
  日期)**/days_since_adjustment/**days_since_decision/days_since_
  maintenance 三距分记**。**距上次调整按生效日**(目标水平自生效日起
  实际执行,决议日是公告面)——2026-11-21 复测 B: 日本央行目标 1.25
  (2026-09-18 决议/2026-09-24 生效/2026-10-30 维持)→距上次调整
  **58 天**(按生效日)/距决议 64 天/距维持 22 天,三数并列交付不再
  单义歧义。记录缺席→present=False 如实注记(官方记录缺席≠政策未发生,
  不虚构)。
- **release_calendar 新双入口**: policy_entries(path=None)与
  publish_instant(metric_id, obs_date)——中国 LPR 各表统一读官方发布
  时刻(复测 2026-11-20 09:00;缺时刻条目返回 None 不编造)。
- **两个新草稿类**(blocked_class_of,agent_judgment.py;渲染/阻断/归档
  三门同源):
  - `map_current_period_stale_mix`: 必需当期的 ok 锚**全部**为过期与
    未核验**混合**(两类都在场且无新鲜 ok)——R27 已拦单一形态
    (missing/unverified),混合形态此前漏网;current_period_groups
    返回结构新增 stale_mix 键(r27 门 §C5 断言随结构扩展)。
  - `map_official_target_missing`: 问句点名央行×水平/调整问词
    (question_official_target_regions 确定性词形判定,A 问句→∅/B 问句
    →{JP})而日历无该地区政策决议/维持实录且序列面决议/生效日不可推
    ——「缺用户指定的官方目标」点名阻断;未点名地区记录缺席如实不入
    rows 不触发缺口(不因新增类改判旧问句)。
- **official_policy_record_face**: 政策官方记录面 rows+gaps 阻断/渲染
  共源——记录在场→决议/生效/官方目标/最近维持/距上次调整(按生效日)
  逐项入 rows(不以市场序列值冒充官方目标);缺席→回退序列+惯例可推性
  判定;gaps 只对问句指定官方目标的地区判。引擎树日历同源: report/
  archive 两调用点显式传 engine_root 的 config/release_calendar.json
  (注入树/验收树各自的日历,不回落本仓默认——修前缺陷: 验收树改日历
  不生效)。
- 门面(§B,13 判据)五形态全覆盖: ECB 2024-06-06 决议缺档(旧值
  不因本地日历未收录被判新鲜→STALE 如实)+政策确认维持(维持发布
  刷新核验截止→FRESH;间隔超决策周期上限→UNVERIFIED)+过期与未核验
  混合(report rc=1 草稿 bc=map_current_period_stale_mix+archive
  not_deliverable 全链)+缺指定目标(B 问句抽走 JP_POLICY_TARGET
  条目→草稿+归档拒绝)+正常放行(记录齐→无阻断);附 policy_decision_
  state 58/64/22 三距、publish_instant 09:00/None、official face gaps
  字典形态(点名 region/metric_id/label/note)、cutoff 相对天数、A 问句
  空集负例、管道级 report→archive 两段实录。

## 3. 历史回答:同步面+相对事后纪律+席位加查(任务3)

- **history_region_sync_face**(research_map_planner.py): 逐段按历史
  截点核对美中欧日——每段(锚月/截止月)×每地区×每维度输出一行:
  可见观测值+公布日+数据版本(绑定实际公布日与版本面),标签∈同步/
  分化/缺证(缺证=无可见观测或美国同维基准缺证,逐行点名原因)。美国
  =基准位(类比标签保留,R24 口径),非美地区与基准同向=同步/反向=
  分化/基准不在场=缺证。
- **judgment_contract 两条新规**(R27 拦显式事后日期后补相对词形漏洞):
  - `relative_expost_in_asof_segment`: 当时叙述(similarity/difference/
    other_regions_sync)含「随后/此后/接下来 N 个月」类**无绝对日期的
    相对事后引用**→CONTRADICTED——事后走向一律移入 ex_post 段;
  - `relative_without_absolute_anchor`: ex_post 段相对窗口**必须点名
    绝对年月**(锚 YYYY-MM 或窗口端点),否则窗口不可核、复测不可
    重复→CONTRADICTED。
- 事后事实按当时可知/事后实际两段落位,ex_post 保留随后 3/6/12 个月
  结果(R24/R27 既有口径不变)。
- **席位章程加查三项+同步性复核**(SEMANTIC-AUDIT-SEAT.md,历史段
  同步面在场的裁决必查): 机制链复核(每环 E1/E2/E3 相称性,E2/E3 不得
  以事实位措辞出现,环内数字可回贴引擎面)+竞争解释复核(真正竞争非
  稻草人,「尚不能区分」须与对质面一致)+区分指标复核(预言方向确实
  相反/不同幅且指标在场,缺席=证伪条件不可观测)+历史段同步性复核
  (叙述主张须与地区×维度同步面标签一致,冲突或同步主张配缺证面=
  REVISE 必修)。
- 复测: C 的 2022 年 6 月叙述(r23 既有档,历史段真实样本)——门 §C
  在 r23 档上注入相对事后引用(当时段)与无绝对锚(事后段)两类变异
  逐条拦下,锚定版干净;同步面在 r23 真实数据上 12 行×2 段全位: 覆盖
  段零缺证(同步+分化标签+值+公布日在场),未覆盖段(S4 信封 2016-11
  起>该段截止)12/12 缺证且逐行点名「无可见观测/美国同维基准缺证」
  ——诚实缺证而非编造同步。r23 基线在现行契约下=CONTRADICTED(既有
  bp_attributed/expost_date_written_back 旧项,R28 两规以 delta 断言,
  不动旧结论)。

## 4. 四席真实一问会话+离线重放(任务4)

**会话形态**(两代如实): 先导代=2679629 树四席——A/C 正常路由走全链,
B/OPEN 即席作答暴露任务1 缺陷(→整改 48c03cb,§1);**正式代=48c03cb 树
四席全跑**(CLAUDE.md 必读路由层在场),同一入口=裸问句文件直进
`claude -p "$(cat 原问)"`(零程序性帧,acceptEdits,预算/禁令环境面),
技能+CLAUDE.md 双层路由。四席 verbatim 逐字节: A=409eef0c(与 R27-A
同值)/B=7e8821bd(与 R27-B 同值)/开放问=426b32ee(临时拟)。

| 席 | 问句 | 树 | 链路 | 裁决链 | 交付 | 归档探针(操作者实测) |
|---|---|---|---|---|---|---|
| A 原问 | 全球宏观变化地图(四地三时点) | install(全数据) | plan→attach→report→席位 | REVISE(三必修)→REVISE(同类第三处)→**UPHELD**(3 档 append-only) | 草稿交付(读者版 MAP_REPORT 107KB+FULL_REPORT),缺数格如实标注 | rc=1 not_deliverable/map_core_dimension_missing |
| B 换问 | 美/欧增长通胀变化+日央行水平与距上次调整 | install-b(全数据) | 同上 | REVISE→**UPHELD**(2 档) | 草稿交付;**任务2 复测在图**: 官方实录行=1.25/决议 09-18/生效 09-24/维持 10-30/核验截止 10-30/距上次调整 58 天(按生效日)/距决议 64/距维持 22/溯源 RC-JP-BOJ-TARGET;宣布值与月均印证两层分记 | rc=1 同上 |
| C 缺核心数据 | A 原问 | install-degraded(ea 当日面抽除+快照重建) | 同上 | **UPHELD**(首过) | 草稿横幅=欧区增长/通胀两维缺数,检索范围+影响逐格点名 | rc=1 同上(契约「C 交草稿并实测拒绝归档」=PASS) |
| 开放问 | 四地三个月分化+维度+证据不足 | install-open(全数据) | plan(run_ok=true,verbatim 落盘)→**零指标映射**(S4/S5 如实跳过)→attach 结构性受阻→按技能纪律转工具组合补充披露 | 无席位(零映射无可审对象,诚实缺席) | **结论层标注草稿面**+证据不足维度逐项点名 | rc=1 not_deliverable(无可审链) |

- **席位判例增量**(正式代,全文在档): A 席 REVISE①传导第 2 环对质
  失配(BEI_10Y 在列竞争解释与被检变体不符→「支持主解释」越判,改
  尚不能区分+脱锚变体单列)②历史段当时可知口径违例两处(2022-06/
  2025-03 取值用事后值)③2022-06 水平共振而方向分化措辞→REVISE 复裁
  同类第三处(2023-10 段)→UPHELD(3 档);**B 席 REVISE=MAJOR: 判断层
  「距上次调整只能给区间 21-51 天」与同报告引擎官方记录面(实录 58 天)
  冲突——席位强制官方实录层为主答、月均序列降为印证层,UPHELD 复裁
  零残留**(任务2 官方记录优先纪律的席位执法实例);C 席首过 UPHELD
  (20+ 数值抽查全一致);先导代判例:A=两情景触发方向倒置、C=会话内
  compare 实时数与冻结证据面 1-6bp 出入,均修订后 UPHELD。四席
  run.git_head=48c03cb 全长在档。
- **归档拒绝的 honest 面向**: A/B/C 拒绝根因=map_core_dimension_missing
  ——EA_REAL_GDP_YOY 全 LIVE 史零观测(ea 面从未含 GDP)、CN 政策族
  (LPR/OMO/overnight)注册表无历史通道(china_market_collector 无登记
  接入点)、当日利率族未入快照。此为真实数据现实的正确行为(任务2
  「必需当期只有过期与未核验值…交付草稿、点名缺口并拒绝归档」同一
  纪律),非缺陷;补数/补通道后重跑可转正。
- **离线重放(实包五步,候选代码=48c03cb 前身 2679629 树 ia_cli)**:
  对象=R27 旧真实包(20261117T_修正后 BEI/黄金,repo 内 research_
  archive)。[0]严格面 rc=1(旧档 manifest 无 run_code_git_head 键,
  crosscheck FAIL+blocked=code_version_mismatch——未记录≠一致);
  [1]--allow-code-mismatch 披露降级 rc=0,10 检查 0 失败,检查明细点名
  「旧档未记录键」;[2]重复运行 rc=0+原包 3e7e243816b1253f 逐字节
  不动(输出目录 append-only);[3]抽 views_digest.json rc=1
  (completeness/copies/content/untouched 四 FAIL);[4]翻转 report.md
  一字节 rc=1(copies_sha16_match)。命令+原始 JSON 全量在
  r28-evidence/acceptance/replay_legacy_real/。**候选代码包重放**=
  门 §D1-§D7(37 判据内): 夹具裁决链归档包上逐字节核对/篡改/缺件/
  重复/代码版本门/旧档形态全覆盖——当日真实工单因数据缺口全部正当
  拒归档(上行),故真实包重放以 R27 旧包+门夹具双证。

## 5. 电池与 CI

- 全量电池(59de8c1 提交前工作树,CI 同口径 for t in tests/test_*.py
  排除 test_model_live,逐套件 rc∈{0,5} 绿): **200 套件,红 2,均定性**
  ——①test_arch_reform_phase6 rc=1=D3「整改树工作面净」契约(红=未
  提交改动在场,提交后复验: 唯余报告/证据未跟踪件=R27 同弧,终笔
  docs 提交后闭);②test_audit_r25_gate rc=1=§B1 断言钉旧日历口径
  (v1.4.0+14 条目),R28 日历正道演进至 v1.5.0+17 后断言随结构更新
  (只增不减+v1.4.0 记事仍在场语义)——电池日志先于修复落盘,修复后
  直跑 **55/55 绿**。
- 提交后改动门复跑绿: r25 **55/0**、r27 **35/0**;**r28 门三段演进**:
  34/34(59de8c1)→36/36(2679629,+§D7 旧档两判据)→**37/37(48c03cb,
  +§A4 CLAUDE.md 路由)**。
- **CI(候选链逐 SHA)**: 59de8c1→run **44873916693 success**;
  2679629→run **44875871599 success**;**48c03cb(终候选)→run
  44881389897 success**(offline-tests,电池同口径)。
- phase6 提交后复验 D3 仅余 AUDIT_R28_REPORT.md+r28-evidence 未跟踪件
  (本档本体,终笔提交后全绿)。

## 6. 交付面(提交链/证据/一页验收结果)

**提交链**(dev/audit-fix-r1,独立审计基线 193c289):
193c289 → **59de8c1**(四任务代码+门)→ **2679629**(重放旧档兼容+
门 D7)→ **48c03cb**(任务1整改 CLAUDE.md 路由+门 A4)=终候选 →
终笔 docs 提交 **238245c**(本报告+r28-evidence,CI run **44884667220
success**)。
**终候选 48c03cb 全长=48c03cb847ff985615c4f2254558d3a7f0be4b1a,
CI run 44881389897 success。**

**证据地图**(docs/autonomous-rd/r28-evidence/):
- acceptance/question_{A,B,open}.txt(原问逐字)+real_evidence_face.txt
  (AC3 真实到期证据面)+session_A_first_attempt_aborted.txt(首试
  中止诚实记录: rc=143,双重根因=采集步缺席+LIVE 当日空面);
- acceptance/session_A_formal|B_formal|C_formal|OPEN_formal/(四席
  正式: 会话日志+verbatim+run 九件套+裁决档+归档探针);
- acceptance/session_A/(先导 A@2679629 全件)、session_C_pilot_
  2679629/(幸存件+残缺注记 README)、session_B_first_adhoc 与
  session_OPEN_first_adhoc/(即席作答缺陷实证→整改依据);
- acceptance/replay_legacy_real/(实包五步重放: demo_output+五 JSON
  +可复跑脚本)。

### 一页验收结果

- **实际通过**: 任务1 默认入口(技能+CLAUDE.md 双层路由;四席正式
  全走 research-one 链;整改依据=先导 B/OPEN 即席作答实证);任务2
  当期政策与日期(B 图官方实录行 1.25/09-18/09-24/10-30/核验 10-30/
  58-64-22 三距+LPR 09:00+席位执法判例;五形态门全覆盖);任务3
  历史回答(同步面+两新契约规+席位加查;A 席当时可知违例三处全拦);
  任务4 离线重放(实包五步+门 D1-D7;缺件/篡改/重复/代码版本/旧档
  全拒或核对);归档拒绝契约(A/B/C 三席操作者探针 rc=1
  not_deliverable/map_core_dimension_missing+开放问无可审链拒)。
- **剩余阻断(非本轮缺陷,如实)**: ①当日真实工单全部正当拒归档——
  EA GDP 全史零观测/CN 政策族无历史通道/利率族当日未入快照,补数或
  补通道后重跑可转正(候选转正路径在图);②机构观点库 0 份→观点级
  到期样本 NOT_VERIFIED(首验窗 2026-12,AC3 如实填报)。
- **SHA**: 基线 193c289;代码链 59de8c1→2679629→**48c03cb(终)**;
  CI=44873916693/44875871599/**44881389897 全 success**。
- **工单**: A=409eef0c(491B 文件/490B 载荷)、B=7e8821bd(196B)、
  开放问=426b32ee(249B);四席 run=20261121T074401Z/074345Z/074411Z/
  074415Z。
- **报告路径**: 本报告+reader 版
  r28-evidence/acceptance/session_{A,B,C}_formal/run/MAP_REPORT.md。
- **重放命令与输出**: `python3 ia_cli.py research-one --stage replay
  --package <包> [--allow-code-mismatch(旧档)] --replay-out <目录>`;
  实测输出=replay_legacy_real/demo_output.txt(五步 rc=1/0/0/1/1)。
- **正式归档/合并/LIVE/付费凭证=用户裁定**;PR #1 仅按既有授权更新。

### 坑台账(本轮新增)

1. 验收树建造后必须跑采集轮+快照重建——R27 的 run_collect 步不能省
   (首试全指标缺席的根因之一;快照「已存在且不可变」要删当日快照
   文件再重建,post_collect 的重建步须真实生效)。
2. LIVE 当日空面+最新面选取=全指标缺席(macro 07:20 空面盖住旧面;
   metric_series 只读最新面)——空面当日回退旧面仍为候选观察。
3. 旧档 manifest 无 run_code_git_head 键(未记录≠矛盾)——严格面照
   拒,--allow-code-mismatch 披露降级(2679629+门 D7)。
4. install_skill 输出人类行+JSON 混合,建造器 json.load 须容错(技能
   实际已装,警告为噪音)。
5. `-p` 模式无过程输出(缓冲到结束),进度看树内文件不看日志;同因,
   会话日志同名重跑会覆写——先导证据须会话毕立即拷贝(C 先导 run 件
   因此丢失,已如实注记)。
6. replay 默认输出落包旁(archive 父目录),对仓内包=写进 repo——演示
   /批量重放须显式 --replay-out 到隔离目录;append-only 同秒重放会
   replay_out_exists 拒(设计行为,非缺陷)。
7. 技能可见≠技能被读: 非地图形研究问句不触发技能加载→路由纪律失效
   (B/OPEN 即席作答根因)——会话行为约束必须落必读层(CLAUDE.md),
   任务1 整改 48c03cb。
