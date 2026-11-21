# Audit-R27 交付报告(R72)

基线 382a8c1(R26 尖,PR #1)→ **54c9974(任务1-4 代码修复)**→
**4b030c3(门+测试口径跟进)**→ **b7cc80b(验收补: 守卫占位 null 身份
豁免)**,全部在 dev/audit-fix-r1(PR #1)。用户验收令四任务对应本报告
四节;新门 tests/test_audit_r27_gate.py 35 判据;回归 r20-r26 七门+
phase6+p03+r7 全绿(r7 三红=夹具日期腐烂,首跑 CI 揭穿后正道修复,见 §5);
全量电池与 CI 见第 5
节;三席真实一问会话(原问 A/换问 B/残缺 C)见第 4 节。

## 0. 环境与既成状态

- 验收令四任务(用户原文): ①会话 B 原问修正点锚——对照表必须同时有
  2026 年 11 月当期和三个月前,日本央行子问须给出有来源的现值与最近
  调整或明确标为未核验;按所请求的不同时间点统计覆盖,同一时点多个
  指标不能替代另一个时点;必要当期缺失/过期/无法核验时首页、交付状态
  和归档统一判草稿;用 2024-06-06 ECB 决议复测政策时效,旧值不能因
  本地日历没收录新决议就被判新鲜②修会话 A 的三段历史正文——当时
  是否同步逐项使用截止日前已公布的证据,后续观察移入事后结果;加一个
  把事后日期写回当时段的拒绝用例;在修复版本上重跑并重新签发③修同日
  首次并发——检查存在、读取、判断降级和提交纳入同一把锁;从空目录
  同时写完整档和缺 CPI 档两种提交顺序都须保住完整数据;条数相同但最新
  有效观测回退时应转存;保留正常修订和写盘中断回归④随包提交完整运行
  SHA、原问、裁决链、地图摘要和一条可执行的重放命令;用最终版本复跑
  原问 A、换问 B、残缺 C;在全新临时目录直接从包验证 A/B 的原问、裁决
  和地图字节,并验证 C 只出草稿、拒绝归档;若日志声称 REVISE→UPHELD,
  两条记录都须随包可核对。
- 运行 SHA=**b7cc80b**(git archive 干净树+CODE_VERSION.json 印章,
  R7-03 三级链第三级)。
- 验收树=/tmp/r70/r27-accept 隔离副本(2875 件),LIVE 数据树只读复制
  历史面,当日面由本树采集器重采;LIVE 数据树零写入。
- 本轮环境实录: 采集首轮遭遇本机网络中断(DNS 解析失败),ea/japan/jp/
  shiller 四采集器诚实缺席不落盘;网络恢复后重采四源全落。CN 端点
  (NBS/mofcom)python-urllib TLS 协商断持续在案(R9 已记),china 采集器
  curl 通道慢速成功(断网空壳面→后到富面事件成为任务3守卫的真实验收
  素材,见 §3)。

## 1. 点锚修正+句段作用域+政策时效第三态+当期草稿(任务1)

### 1.1 点锚修正(会话 B 原问)

- `_POINT_EXPLICIT_YM_RE`(YYYY年M月): 等于截止月→**当期锚**(label
  仍为「最新一期」,叠加 explicit_period 字段);1..120 个月前→显式历史
  锚(「YYYY年M月」);未来忽略。
- `_POINT_COMPARE_RE`(相比|对比|相较|较之|比起)∧在场月前锚→比较结构
  隐含**当期端点**,当期锚缺席即补。
- 会话 B 原问(196B)实测锚列: `[3个月前, 最新一期(explicit 2026-11)]`
  ——对照表恒有当期列+3 个月前列。会话 A 原问(490B)锚列不变
  `[12个月前, 3个月前, 最新一期]`(零回归,门 §B1/§B2)。
- 纯历史点问句(如「2024年6月相比2023年6月」)显式历史锚入列且**不虚构
  当期锚**(门 §B3)。

### 1.2 句段作用域请求(日本央行子问)

- `_clause_region_dimension_requests`: 问句按 。？！?！;；\n 切段,段内
  命中地区×段内命中维度(含政策子问词形: 政策利率/央行/加息/降息/降准/
  LPR/逆回购/利率水平)才入计划;词形分置无段请求→回退全域全维笛卡尔
  (旧口径,零回归)。
- 会话 B 原问实测计划组恰 5 组: US×{增长,通胀}、EA×{增长,通胀}、
  JP×policy——「日本央行政策利率」子问只请求 JP×policy,不以全域网格
  摊大检索面;JP_POLICY_RATE 在计划(有来源现值+最近调整入政策四分面)。
- **验收实测缺陷修**: plan_map 内残留旧全域笛卡尔循环曾以全组覆写句段
  作用域结果(B 问计划 9 组而非 5 组)——已删除,门 §B7 断言计划组=请求组。
- 会话 A 单句全组 12 组全网格不变(门 §B5/§B6 回退口径)。

### 1.3 政策时效第三态 UNVERIFIED(2024-06-06 ECB 复测)

- decision_dated 序列(ECB_MRO/ECB_DFR/DFEDTARU/DFEDTARL): 无更晚已
  证实决议且无证实间隔>决策周期上限(缺省 90 天,注册表 freshness.
  max_unconfirmed_days 可覆写)→ **UNVERIFIED**(fresh=False,
  unconfirmed_span_days/decision_cycle_bound_days 键)——本地日历未收录
  ≠未发生,现值是否仍有效无法核验: 不判新鲜,亦不以未证实间隔虚构过期。
- 2024-06-06 ECB 决议复测(门 §C1/§C2): 旧值 obs 2024-06-05@as_of
  2024-12-01 无日历确认→UNVERIFIED(不因本地日历没收录新决议判新鲜);
  日历收录该决议→确证 STALE(第三态不放松既有过期判)。
- 边界(门 §C3): 无证实间隔 90 天 FRESH/91 天 UNVERIFIED;会话 A 形态
  (滞后 65 天)FRESH 不误伤完整交付(门 §C4)。
- 90 天选择依据: Fed/ECB/BOJ 年会次~8 次,最大会间 ~56 天,90≈两个
  决策周期;利率长期不变≠无法核验的判据=「无证实间隔超过两个决策周期」。

### 1.4 当期草稿三侧共源(按时点统计覆盖)

- `current_period_groups(point_values, planned_pairs, has_current_anchor)`:
  组内最新一期锚零 ok 格→missing(他时点 ok 不补当期);当期 ok 锚全部
  freshness=unverified→unverified;计划无当期锚(纯历史点问句)不判。
- 新阻断类 `map_current_period_missing` / `map_current_period_unverified`
  入 BLOCKING(attach/报告/归档同源)+belt 草稿元组+SKILL 草稿纪律
  (门 §C7-§C9/§E4)。
- 渲染: 首页两类草稿横幅(当期缺数/无法核验);对照表 ⚠未核验 标注
  (最后确认日+无证实天数+决策周期上限);逐组覆盖表 ⚠未核验;**按时点
  统计覆盖行**(组级——同一时点多个指标不能替代另一个时点,逐锚分开
  计数);政策四分面无决议变更月→「未核验(实录表无该值变更月,不以回推
  造日期)」+当期生效日附距研究截止天数(门 §C10-§C13)。

## 2. 当时可知纪律强化(任务2)

- 契约条目 16 `_after` 扩到**全部非政策事件事后数值行**(setdefault,
  截止月行仍为代表值)——异常延误行的值被当时正文引用同样判 as_of_leak。
- 新增 16b `expost_date_written_back`: 相似/差异/同步段含显式日期
  (YYYY-MM-DD/YYYY-MM/YYYY年M月)严格晚于判断截止月末→CONTRADICTED
  (事后日期不得写回「当时」段)。
- 门 §D 三判据: 写回拒绝(expost_date_written_back)/当时可知改写(含
  当时日期)不误伤 VERIFIED/延误行值(-2.2,首发 2025-06-01)引用→as_of_leak。

## 3. 同日首写并发一把锁+占位 null 豁免(任务3)

- **查存在/读取/判降级/提交同一临界区**: 首写亦入 `_guard_lock`(锁=
  superseded/ 内 per-规范文件 flock,锁宿主目录随首次加锁创建——
  p03 t39 断言随之更新为「顶层=规范档+锁宿主,全树无 .tmp 半成品」)。
- 空目录同时写完整档+缺 CPI 档(门 §A1/§A2 两序+§A3 fork 真并发):
  完整先到→缺 CPI 档按身份丢失转存,规范档保完整;缺 CPI 先到→完整档
  身份超集覆写;真并发任意交错规范档收敛=完整数据。
- **同计数时点回退**(门 §A4): `daily_face_valid_obs_horizon` 按身份取
  dates/values 对有效观测最大日,条数相同但最新有效观测日后移→
  degraded_diverted(「条数相同」不掩时点回退)。
- 正常数值修订/前向追加放行,写盘中断回归保全(门 §A5)。
- **验收实测缺陷修(占位 null 身份豁免,门 §A6/§A7)**: 断网轮空壳面
  先落(ah_premium/margin/southbound=null 占位),网络恢复后富面后到——
  null→富容器提升使占位身份从叶集消失,曾被误判「身份丢失」转存,富面
  被阻,规范档停留空壳。修正: 身份丢失判定排除有效观测=0 的占位身份
  (不承载数据,其消失非数据损失);真实数据身份(叶数>0)被删仍判丢失;
  观测蒸发(>0→0)缩水分支不受影响。此事件为验收树真实采集轮实测
  (china 面 superseded 槽位在档,证据 r27-evidence/acceptance/guard-events)。
- **并集收敛实录**: 空壳面(富 intraday)与后到富面(全 CN 宏观+序列)
  各持部分真实数据——操作者并集合并后经守卫落规范位(overwritten_
  preserved,零丢失),与任务3「两种提交顺序都保住完整数据」同哲学。

## 4. 三席真实一问会话+随包重放(任务4)

- 会话运行形态: 全新 claude -p 零上下文,唯一输入=原问句文件,验收树
  =b7cc80b 干净档+当日真实采集面;允许=读写/python3/检索,禁止=push/
  ssh/curl/rm -rf/commit。
- **随包重放面(本轮新增)**: report 段落盘 `run_dir/question_verbatim.txt`
  (字节=run.question;在场异字节→copies_consistent False+拒付);MAP_REPORT
  尾部「## 重放(随包可执行)」footer=完整运行 SHA(来源+CODE_VERSION.json
  印章可核)+原问件+裁决链 REVISE→UPHELD 双记录注记+MAP_REPORT.sha256
  锚+可执行 `python3 ia_cli.py research-one --stage auto --question-file
  <本运行档目录>/question_verbatim.txt`;归档件集 _arc_files+=
  question_verbatim.txt。footer 在冻结内容 SHA 之前(稳定输入,不破坏
  既有印章口径)。
- (会话结果与全新临时目录包验证明细见 §4.1-§4.3 与第 6 节交付面)

### 4.1 会话形态与裸问句根因实录(R21 坑复现+修复)

- 会话=全新 claude -p 零上下文,唯一研究输入=原问句逐字(196B/490B 均包验字节一致),
  允许=读写/python3/检索,禁止=push/ssh/curl/rm -rf/commit,$50 预算+4h 看门狗。
- **裸问句两轮失败(诚实记录,弃用——R21 同坑)**: 会话 B 首两轮(裸问句直传)即席
  作答: 引擎 compare/history 数据手拼对照表,零 research-one 调用、零 run_dir、零
  裁决链。根因排查: ①验收树 .claude/skills 缺失(构建脚本漏 R26 的技能复制步,
  已补:技能+engine-path.json 就位后第二轮仍即席作答→排除该单一因素)②R26 起会话
  启动器丢失 R21/R22 的**程序性规程帧**(R21 在案: 「裸问句 headless 即席作答须
  程序性帧」;R26 裸启恰走全链=侥幸,R27 暴露)。修复=恢复 R21 认可口径: 原问一次
  +程序性规程(走正式入口/REVISE 必要修订/停等用户裁定归档;**零研究内容指示**)。
  帧文本随证据入仓(prompt_b_frame.txt 1049B/prompt_c_frame.txt 1419B)。
- 会话 A 裸启即走全链(kept,无需重跑);B 第三轮(B3)与 C 按规程帧运行。

### 4.2 会话 A(原问,490B)

- run_dir `20261121T005508Z_给我一份全球宏观经济变化地图…`;git_head=b7cc80b
  (source=code_version_stamp);blocked_class 无;首页无草稿横幅;逐组覆盖表+
  按时点统计覆盖行在场;随包 question_verbatim.txt 字节=run.question;
  MAP_REPORT.sha256 一致(0cc2a678…);裁决链 UPHELD rev1
  (VERDICT-20261121T005508Z-01.json,run_ts 绑定=R26 既有契约);会话末停等
  用户归档裁定(纪律正确)。
- 全新临时目录包验(verify_A.out 全 PASS): 印章/原问字节(409eef0c…,唯一差异=
  文件级尾部换行)/重放面 footer 四件+可执行命令/对照表当期列。

### 4.3 会话 B(换问,196B,程序性规程帧)

- run_dir `20261121T013826Z_对比角度换一个…`;plan run_ok=true 证据索引 63 行;
  Agent 席本地干跑两轮先拦 4 类违规(悬空引用/对质三态外/事后日期回写/as_of 泄漏)
  后 attach 一次通过(violations=[]);report machine_verified=true,
  copies_consistent=true;独立语义审查席(fresh-context)首裁 **UPHELD** rev1
  (抽核 18 锚格/同比派生 10 项/转折 7 条/事后窗/JP 路径/三分解/资产月窗/发布日
  纪律逐位一致;2 MINOR+1 NIT 低于修订级);deliverable=true 无草稿旗标。
- **任务1验收点在 B 地图实测**: 双锚对照列(3个月前=2026-08-21 可见面 vs
  最新一期=2026-11-21 可见面)恒在场;按时点统计覆盖行「3个月前=5/5组ok;
  最新一期=5/5组ok」(同一时点多指标不互替);日本央行子问=有来源现值
  (JP_POLICY_RATE 月均 1.227%@2026-10,口径注记「月均≠政策目标宣布值」)+最近
  月均格变动 2026-10 格距截止约三至七周+决议日引擎缺席如实注记(JP_POLICY_TARGET
  不在注册表→「数据不可得」呈现,不以相邻口径冒充)。
- 全新临时目录包验(verify_B.out 全 PASS): 原问字节一致(7e8821bd…,含尾部换行
  逐字节同)/印章 b7cc80b/随包原问/MAP_REPORT.sha256(da799e36…)/重放面/
  裁决链 UPHELD rev1。

### 4.4 会话 C(残缺树,规程帧)——只出草稿+拒绝归档

- 残缺树=静树复制后抽走当日 ea 面+重建快照: EA_HICP_YOY/EA_REAL_GDP_YOY
  序列空(MISS),CN 面完好(n=226)。
- run_dir `20261121T020733Z_给我一份全球宏观经济变化地图…`(degraded 树);
  Gate A 59/59 信封步 FAIL 如实披露;Agent 席本地预校验拦下 1 处中文别名误绑
  (美元指数↔BRENT -25.17%)修正后 attach violations=[];独立语义审查席
  **UPHELD** rev1(VERDICT-20261121T020733Z-01.json,fresh=true)。
- **交付门拦截(任务4 C 契约)**: blocked_class=map_core_dimension_missing
  (欧元区增长/通胀序列缺席)→ deliverable=false → 信封以草稿交付
  (draft_delivered=true);MAP_REPORT 首页草稿横幅「核心维度组缺数」在场,
  缺数格标草稿+缺口注记。
- **归档拒绝双实录**: ①会话内按规程帧尝试 `--stage archive` 一次,引擎拒绝
  (exit 1,blocked=not_deliverable,警告文本含 R27 任务1 草稿类「当期缺失/
  未核验维度首页标草稿」);②操作者独立复演(strict rc=1,ok=false,
  deliverable=false,verdict=UPHELD——语义过、数据门拦,verify_C.out+
  verify_C_archive_probe.json 在档)。残缺树 research_archive 零条目
  (C 未入正式档案)。
- 包验: 原问逐字(409eef0c…,尾换行差异同 A 口径)/印章 b7cc80b/随包原问/
  MAP_REPORT.sha256(5bdc1691…)/重放面/裁决链 UPHELD rev1。

## 5. 电池与 CI

- 邻域门: r20 30/0、r21 50/0、r22 36/36、r23 51/0、r24 74/0、r25 55/0、
  r26 46/0、**r27 35/0**、phase6 29/0(提交后)、p03 28/28、**r7 38/0**。
- **r7 三红根因更正(重要)**: 收口轮 CI(run 44856874693)揭 r7 F4c/F5/F7
  三断言红;此前本地电池同三红曾被误记为「CN 端点网络环境类」——实为
  **夹具日期腐烂**: F4c/F5 硬编码 day=(2026-11-21/22) 充当 R26 验收日
  (11-20)的「跨日」,日历走到 11-21 后 F4..F4c 变同日写,守卫正道转存
  部分面致断言红(测试内的「CN 端点不可达」行=注入的模拟异常,非真网)。
  修复= d1 序列 st1..st4 钉 day=(2026-11-20),序列永冻结,跨日语义恒成立;
  r7 门 38/0 复绿。R26 绿轮 CI(44777614706,11-20 跑)同套件全绿佐证
  非代码回归。
- 同轮第二红: r27 门 §E 曾读 `.claude/skills/.../SKILL.md`——gitignored,
  CI 干净克隆缺席(R8/R22 在案坑),本地恰有安装面才过。修复=在场性守卫
  (.claude gitignored 缺席合法豁免,.agents 仓内跟踪面必须在)+内容查
  (.agents);本地/干净克隆双形态 35/0。
- 全量电池: tests/test_*.py 逐件 rc∈{0,5} 口径,修复后全绿(唯一过窗红=
  phase6 净树自指检查,提交后复跑 29/0 自绿——既档行为)。
- 远端 CI: 首跑 run 44856874693 红(上述两红;gates job 绿);修复提交
  746a80d 复跑 **run 44858942833 全绿**。
  https://github.com/bojing951-hash/investment-agent/actions/runs/44858942833

## 6. 交付面

- 运行 SHA=**b7cc80b**(dev/audit-fix-r1,PR #1;链 382a8c1→54c9974→4b030c3→
  b7cc80b)。
- 三份工单(隔离验收树 /tmp/r70/r27-accept,证据入仓 docs/autonomous-rd/
  r27-evidence/acceptance/):
  - **A 原问**(490B,sha256 409eef0c…): run `20261121T005508Z`,
    UPHELD rev1,deliverable=true,无草稿;
  - **B 换问**(196B,sha256 7e8821bd…): run `20261121T013826Z`(程序性
    规程帧),UPHELD rev1,deliverable=true,双锚列+JP 现值/最近调整/决议日
    诚实缺席齐;
  - **C 残缺**(=原问 A,EA 面抽走): run `20261121T020733Z`(degraded 树),
    UPHELD rev1+草稿交付(blocked_class=map_core_dimension_missing)+
    归档拒绝 rc=1 双实录。
- 重放命令(随包 footer 同文,任一工单档目录可执行):
  `python3 ia_cli.py research-one --stage auto --question-file <运行档目录>/question_verbatim.txt`
- 逐项验收结果: 任务1=§1+§4.3(点锚/句段作用域/UNVERIFIED 第三态/当期草稿
  三侧共源,ECB 2024-06-06 复测门 §C1/§C2);任务2=§2(当时可知+写回拒绝
  用例,门 §D);任务3=§3(一把锁+占位豁免+时点回退,门 §A 七查);任务4=
  §4(三席真跑+全新临时目录包验 A/B/C+REVISE→UPHELD 双记录条款——本轮三席
  均首裁 UPHELD,单记录如实;footer 双记录注记为条件式)。
- PR 尖=**746a80d**(746a80d85815d1c5cb05b4f839297d1bd5f665e7,
  dev/audit-fix-r1→PR #1);CI=run 44858942833 绿
  (https://github.com/bojing951-hash/investment-agent/actions/runs/44858942833)。
- 交付评论=PR #1 comment 7056049726;正式归档与合并停等用户裁定。
