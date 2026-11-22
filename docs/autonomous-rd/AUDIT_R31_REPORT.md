# Audit-R31 收口报告 — 时点统一/三输入钉死/关键证据校验三修+真实验收

- 链: `aec4712`(R30 终笔)→ `ca916cd`(三任务代码+R31 门 43/43+重放漏读补修)→ 本提交(证据+报告)
- 基线: PR #1 head `aec4712f7f67ecebd7783eb5eac163906560a71e`(local==remote 核对);R31 门
  **43/43**;CI `44983589369` 三 job 绿@`ca916cd`(本地==origin 核对)
- 验收树: `git archive ca916cd` + CODE_VERSION 印章 + LIVE 只读复制 + 树内
  `install_skill --target project`;AUG 树=纯 git archive+仓内提交 11 月快照
- 电池: 首轮 202 PASS / 2 FAIL→raw 移出后 **203 PASS / 1 FAIL**(唯一红=phase6-D3
  未提交文档红,证据提交后复跑绿)rc∈{0,5} 口径——第二红=vendor 守卫被电池 raw
  输出(他测试自述文本)自触发,raw 移出仓外复跑绿,如实入档

## 任务1 — 统一研究截止日和回看窗

- **缺陷**: 「2026年11月,日本和欧元区最近六个月的通胀与政策环境…」(NEW30 问)按
  R11/R12 冻结契约判多范围 unparseable——裸年月与单一相对回看窗本是「一个截止日+一个
  回看窗」的自然语义,被整单拒绝(R30 NEW30 会话以 --allow-failed-run 降级随档,地图面
  正确消费窗但问句时间面未解析);显式「以 X 为研究时点」形虽可解析,但计划截止日仍取
  快照 target_date,时点声明未贯穿取数/覆盖检查/政策窗/资产月窗/渲染。
- **修复**(`scripts/research_orchestrator.py` + `research_map_planner.py`):
  - `_q_is_bare_year_month`/`_q_month_end`/`_question_asof_declared`(:512-:580): 统一时点
    解析器——显式时点标记(以X为研究时点,多时点冲突→None 不择一)或裸**单**年月+**恰好
    一个**相对回看约束(月数或整年数恰一,无自然年/无其他相对)→该年月按**月末**时点化
    为研究截止日;其余组合(双相对/相对+自然年/显式区间+相对/裸全年形/残缺数量)不合并
    ——真冲突仍拒绝(R11/R12 契约面不动);
  - `_question_window` 单窗分支消费同一判据(:798 一带): 裸年月+单一相对窗→
    `relative_months`/`relative` 携 `as_of`(与 `_q_relative_tail` R10 锚点语义同源);
  - **贯穿**(`_run_research_body` :2070 一带): `_question_asof_declared` 先于 plan_map,
    声明时点**优先于**快照 target_date 覆盖 `_cutoff`→计划截止日/`parse_point_anchors`
    (锚 as_of=声明时点: 观测日≤时点且首发日≤时点的最新观测——10 月观测、11 月发布的
    通胀不入 2026-08-21 历史研究)/`policy_window_path`/`official_policy_record_face`
    (cutoff)/`asset_move_face`(cutoff)/`us_rates_trio_face`(新增 cutoff 参: 共同交易日
    取≤时点最近)/数据需求窗 spec.as_of 同源;`research_plan['as_of_declared']` 落
    {as_of, basis, snapshot_target_date, differs_from_snapshot}——与快照不一致=如实披露,
    不静默改判;
  - 渲染(`render_map_report` :2588): 研究截止日行下增时点口径披露行(全部窗口/锚点/
    政策面绑定该时点,数据=当时已发布面,后来发布的数据不回填)。
- **实测**: NEW30 问→cutoff 2026-11-30(裸年月 11 月末时点化)+窗 2026-05-30..2026-11-30
  (基线=多范围拒绝→现解析);AUG 问(以 2026-08-21 为研究时点)→窗 2026-02-21..2026-08-21
  全链绑定,EA_HICP 最新一期=2026-07 观测(2026-08-16 发布),2026-08-21 后零观测消费,
  10/11 月观测不入;双裸年月/双时点/双相对/裸年月+自然年/全日期+相对/显式区间+相对
  六形仍拒。
- **门**: §B 17 判据(NEW30/AUG 两形解析+真冲突六形仍拒+R12 裸年月单独零回归+相比
  三个月前点锚零回归+纯相对窗无 as_of 零回归+计划级贯穿(cutoff/窗/点锚发布可知面/
  10月11月观测不消费)+三利率共同日面绑定时点)。

## 任务2 — 首次取数前固定快照、发布日期历和指标注册表

- **缺陷**(R30 已钉快照,余两件): 计划/核验/历史渲染/发布批次/重放对**发布日期历**与
  **指标注册表**仍各读本地现状——运行中本地文件被改(编辑器/并行进程)则同一次运行
  两次读取两套输入;子命令子进程与主进程各解析;R30 的 `IA_SNAPSHOT_PIN` 单件钉死
  无异常安全释放(S1 后异常→env 残留,同进程后续工单吃首跑钉死)。
- **修复**:
  - `scripts/research_orchestrator.py` `_pin_frozen_inputs`(:1957)/`_release_frozen_inputs`
    (:1995): run_research 入口(第一次取数前)三钉死——快照=R30 既有
    `IA_SNAPSHOT_PIN`(解析原版绝对路径);日历/注册表=`IA_CALENDAR_PIN`/
    `IA_REGISTRY_PIN` 指向入口**字节冻结副本**(tempfile 目录);上游已钉死尊重
    (不重解析);`run_research` 包装层 try/finally(:2015)——**异常路径同样释放**
    (同进程异常后再跑,新工单正确重解析选 _v2);`_pinned_frozen_src`(:2004):
    frozen_inputs 摘要与 root_overlay 归档副本的源=钉死路径(归档字节=入口字节,
    运行中本地修改不入档);
  - `scripts/release_calendar.py` `resolved_calendar_path`(:32): 钉死优先于传参与默认;
    `_load` 钉死文件缺席→FileNotFoundError 拒绝静默回退(fail-closed;无钉死=原语义
    fail-open 警告);
  - `scripts/workbench_data.py` `resolved_registry_path`(:122);`fact_engine.load_registry`
    钉死在场且未显式传 path→读冻结副本(显式路径优先于钉死;缓存语义与既有口径一致
    ——最近一次 load 覆盖默认缓存,p02_w2 污染-恢复契约原样);
  - `scripts/freshness_policy.py` 三政策面(:659/:696/:741)+默认策略(:415)统一经
    resolver——主进程/子进程/重放同一份冻结输入。
  - **重放历史面日历漏读(本任务实补)**: [1b] 预检(R30 B3 包+引擎日历移
    RC-EA-HICP-2022M06 重放)首跑红——`deterministic_rerender` DIFFER,进程内
    spy 锁定 `render_map_report → history_asof_face/history_region_sync_face →
    _aof_first_pub/_aof_publish_instant` 全部**无 root 直调** `rc.*`(path=None
    →引擎本地日历),包内 overlay 日历被绕过。修复: `_aof_first_pub` 加 root
    参数(visible_publish_date/first_publish/final_publish 统一 path 绑定)、
    `_hist_region_reading`/`history_asof_face`/`history_region_sync_face`
    root 透传、渲染调用点(:3364/:3402)传 root——重放重渲读包内 overlay,
    会话内钉死仍优先(resolver 语义不变);修后 [1b] 预检 B3/A3 双包 rc=0+
    byte_equal(B3=38058 字节),引擎日历完好基线重放同样绿。
- **重放面**: 重放本就绑包内 root_overlay 三件(R30 起包自含),resolver 不改显式路径
    语义——引擎本地日历换血/移条目零影响(验收 [1]/[1b] 实证)。
- **门**: §A 11 判据(运行中三钉死在位+返回后释放/冻结临时副本收尾清理/运行中改本地
  日历+注册表→frozen_inputs 与 root_overlay 仍=入口字节+哨兵证明确实被改/异常路径三钉
  死释放/同进程二次运行选 _v2/钉死缺席 fail-closed/resolver 语义/fact_engine 钉死+缓存
  契约/政策面读冻结副本(冻结独有条目可见,本地不串))。

## 任务3 — 收紧关键证据校验

- **缺陷三处**: ① m12 同比基期取「≤end−12 月最后观测」——去年同月缺观测时拿 13 个月前
  观测冒充同比(与地图面 R19 严格口径不一致);② 判断席正文提及决议日而未配生效日/
  待生效标注——「次月末才生效」被写成当时已发生;③ 问句明确要求当前官方政策目标而
  as_of 时点仅有待生效公告——待生效值冒充当前官方目标。
- **修复**:
  - `scripts/fact_engine.py` compute_period_returns m12 分支: 基期=严格去年**同月**——
    同月内有≤锚日观测取之(数值零变化),该月仅有晚于锚日观测(月末戳月频)仍=同月
    基期(窗注如实区分),同月无观测=`available:false`+缺基期原因(最近可得基期披露,
    「13 个月前≠同比」);m1/m3/m6 宽松口径零回归;`economy_comparison_view.key_fact`
    缺基期原因如实透传(不以笼统「无派生」掩盖);消费面(data_assembler 表格/
    macro_scorecard/snapshot_builder)按缺基期=缺证处理;
  - `scripts/agent_judgment.py`: `collect_policy_events`(:81,日历决议事件确定性面)+
    `_date_word_forms`(补零/不补零两形)+`_judgment_text_segments`(l3/l4/reader_map
    全文段+定位)→`validate_judgment` POL-EFF 规则(:363): 段含政策词+决议日词形而无
    生效日词形且无待生效标注→violation(提及决议日 X 但未配生效日 Y——决议与生效分记,
    次月末才生效不得写成当时已发生);`policy_events=None`(缺省)=规则关闭,既有调用方
    零回归;attach_judgment 传生产日历事件面(钉死经 _load 尊重);
  - `scripts/research_map_planner.py` official_policy_record_face(:2028): 问句点名官方
    目标(`question_official_target_regions`)+as_of 无已生效决议+仅有待生效公告→
    `current_target_missing_evidence`+缺证注记,渲染官方目标列=「缺证(仅有待生效公告)」
    (R28 缺口判定口径原样——未点名地区/生效日后不触发)。
- **门**: §C 15 判据(m12 四情景: 同月≤锚日/缺基期 13 个月/月末戳晚于锚日/m3 宽松零
  回归+POL-EFF 七情景: 决议日单独三词形拦/待生效/生效日成对/无政策词/无日期放行+
  规则关闭零回归+当前目标缺证三态: 仅待生效→缺证明标/未点名→不触发/生效日后→升格
  +渲染文案在场+key_fact 原因透传);R30 §B(2022-03 历史端点/LPR 官方日期/BOJ 生效日)
  经 test_audit_r30_gate 全绿保全。

## 验收记录(真实会话+实包重放)

- **环境前置(如实留档)**: 验收树首建即继承 LIVE 晨跑快照(n=78,宏观史缺席——日常
  文件从不携带宏观史,史由快照重建时向源端抓取;LIVE 自身 1117-1122 同形)+当日
  china 重采面被 face-guard 以身份丢失转存 superseded。四会话(A/A2/A3)环境性草稿/
  缺维不可交付,时间线与通道修复全程实录于 `r31-evidence/acceptance/drop_v2_record/
  DROP_V2_TIMELINE.md`。树面修正(零代码改动): 采集侧四采集器重采+superseded 完整面
  嫁接(series_source 随档披露)+merge_cn_history 当日新采(n=226)并入 macro →
  快照重建 **n=90**(EA4/CN7/JP4,Gate A DEGRADED core 缺失 0)。正式验收跑 A4/B2
  均起于该面——环境修复只动验收树,LIVE 零写入。
- **A4**(四地地图正问,操作者归档): 12 组核心维全绿→attach 契约 VERIFIED→独立零上下文
  审查席外复算(21 格锚值/三转折/利率分解/历史九窗/63 个发布日检查)全对,裁决
  **UPHELD**(rev=1,链 1 档;3 NIT 登记不修订)→归档 rc=0(九件套+root_overlay 三件
  +ARCHIVE_MANIFEST,run_code_git_head=ca916cd)。MAP_REPORT 102KB 读者版五面可追溯;
  政策决议/生效分记(欧央行决议 6-11/生效 6-17 等)与任务3口径一致呈报。
- **B2**(换问: 美欧增长通胀对比 3 个月前,操作者归档): plan→attach→report
  machine_verified=true→归档内独立审查 **UPHELD**(rev=1,链 1 档);渲染面带出
  政策官方记录面(日历实录): 日本官方目标 1.25%(2026-09-24 生效,溯源
  RC-JP-BOJ-TARGET-2026-09)/最近确认维持 2026-10-30——与月均 1.227 相互印证且
  口径分记(任务2冻结日历的正式消费面)。**冻结件=`research_snapshot_20261122_v2.json`
  (r31_v2_mark=true)**——A4 运行中落盘的 _v2 被释放后的新工单正确选中(判据3实证)。
- **同进程 _v2 三判据**(任务2,`drop_v2_record/`): ①A4 frozen_inputs/root_overlay
  快照字节=入口 base 字节(中途落盘的 _v2 不入在飞运行);②A4 运行中途本地出现 _v2,
  同次运行两次读数不串号;③随后新工单 B2 正确选中 _v2。三判据齐(watcher4 于
  20:09:12 以 n=90 基面落盘,只动验收树)。
- **AUG**(显式 8 月截止问,任务1主回归): 仓内提交 11 月快照(n=88)上正式 CLI 实跑:
  rc=0 run_ok=False(失败步=诚实缺席类)——`cutoff=2026-08-21`、`as_of_declared:
  as_of=2026-08-21 differs_from_snapshot=True`(与快照不一致如实披露不静默改判)、
  窗 **2026-02-21..2026-08-21**(months=6)贯穿计划/取数/覆盖检查/政策面/资产面;
  锚观测>时点=零、锚首发>时点=零;EA_HICP 最新一期=2026-07 观测(**2026-08-16
  发布**;8 月观测 09-16 发布>时点不入);**10 月/11 月观测消费=零**——11 月快照上的
  历史研究不吞未来数据。
- **C4**(残缺树,ea 面全撤): 草稿照出(US 面可判+EA×三维零 ok 格如实「数据不可得」
  +检索范围注记)→**归档实测拒绝**: `--stage archive` rc=1,blocked=not_deliverable,
  payload 双警示(独立审查裁决缺席不得标记可验收/归档对象=最终受审版本)——缺核心
  数据交草稿并拒绝归档。
- **T3**(任务3定向探针问: 官方目标水平/已决议未生效/同比相比去年同月):
  首跑(初稿无地图形状词)诚实空面——S1 确定性面零命中(注记「零模型不做语义翻译」)、
  L1/L2 行数 0、L3/L4 produced=false,席位不硬造交付,改以引擎面出草稿披露+8 条
  引擎侧观察如实呈报(留档 `session_T3_first_empty/`,判定=问句形状纪律非代码回归,
  与 R30 T3 形状词对照后重写问句)。
  重写(加「通胀与政策环境」形状词,`detect_map_question`=True)后 T3b 正式闭环:
  plan→研判 **4 轮契约迭代**→attach VERIFIED→独立审查 **REVISE→修订→UPHELD**
  (链 2 档,predecessor 完整),`deliverable=true`(48 步 run_ok=True)——任务3三修复
  的正式消费面: ①政策表**决议公布日/生效日双列分记**(BoJ 09-18→09-24;ECB
  09-10→09-16),「已决议未生效」=无+【尚未验证】注记(ECB 序列止 09-16+DEGRADED,
  结论仅覆盖引擎可见面);②同比对照=**同观测月 2025-10 基期**(JP 2.44 vs 2.99;
  EA 4.0 vs 2.1),东京都 CPI 序列 2026-01 起**基期不可得→对照不可判**(缺基期
  不以相邻月冒充);③官方宣布值(日历实录)与月均市场口径(1.227)分记,净 +67bp
  与决议-生效记录相容。发布日=推定规则如实标注。席位另发现引擎缺口三项
  (obs_run 锚标签硬编码/数值别名表缺四 ID/东京 CPI 推定发布日张力)登记 R32
  候选。证据 `session_T3b_formal/`(含 4 轮迭代 judgment+两档裁决链+root_overlay)。
- **NEW30**(裸年月+单一相对窗,任务1 NEW30 回归): R30 原句直承——R30 时判多范围
  unparseable 以 --allow-failed-run 降级随档,R31 后正式解析: `as_of_declared`
  as_of=**2026-11-30**(裸年月末时点化)+窗 **2026-05-30..2026-11-30**(months=6),
  `differs_from_snapshot=true` 如实披露(快照 target=20261122),地图 6 个月前锚
  4/4 组 ok,渲染面时点口径披露行在场。真实席位链: 会话 plan→attach(VERIFIED)
  →report(machine_verified)后审查子代理被后台等待天花板杀→操作者启独立审查席
  **REVISE**(必修1: M1 环1 [E1]「持续高于约 1.3-1.9 个百分点」与冻结快照逐月
  复算 0.93–1.67pp 不符,五处副本;140+ 数字点其余全过——**席位存在理由第五证**)
  →修订席仅改必修句+重跑 attach/report(VERIFIED,旧句零残留)→复审席 **UPHELD**
  (rev=2 链完整,130+ 点独立复算逐位吻合,无新引入)→操作者归档 rc=0
  (verdicts_n=2,manifest head=ca916cd)。证据 `session_NEW30/`(四席位日志+
  REVIEW_REVISE_REQUIRED.md 逐月复算表随档)。
- **七步实包重放(A4/B2 各七绿)**: [0]严格面 rc=0 render byte_equal/[1]引擎本地日历
  换血逐字节不变/[1b]**引擎日历移 RC-EA-HICP-2022M06 重放逐字节不变**(本任务实补
  的漏读修复验证步——修复前该步红,修复后双包 rc=0 byte_equal)/[2]重复重放包不动/
  [3]缺冻结件拒(failed=frozen_inputs_present+digests)/[4]篡改一字节拒
  (failed=frozen_inputs_digests)/[5]manifest 单侧改写拒(failed=digests+
  match_report)。记录在 `r31-evidence/acceptance/replay_A4_real/`、`replay_B2_real/`。

## 电池与证据

- 电池(提交前工作面): 首轮 **202 PASS / 2 FAIL**(共 204 件,逐件
  `python3 tests/test_*.py`,rc∈{0,5} 绿)——1) phase6-D3 未提交文档红(整改树
  工作面净判据既有口径,证据提交后复跑绿);2) charter5 vendor 守卫**自指效应**:
  本证据包 battery_raw.txt 含其他测试自身输出的厂商旗标字样(`--`+厂商缩写)描述
  文本,触发全仓
  零容忍静态扫描——raw 移出仓外(/tmp 接受区留档)后单件复跑 **rc=0 绿**;立足面
  **203 PASS / 1 FAIL**(唯 phase6-D3),教训入档: 电池 raw 不入仓内证据树。
- CI: run `44983589369` 三 job 绿(tests 3.11 / tests 3.12 / gates)@`ca916cd`
  (本地==origin,head 40 位核对)。
- 证据: `docs/autonomous-rd/r31-evidence/`(README+acceptance/questions×6/
  session_A4_formal·session_B2_formal 正式包/session_T3_first_empty 空面留档·session_T3b_formal·
  session_NEW30(正式归档链)/session_C4_degraded/aug_plan/replay_A4_real·replay_B2_real/
  drop_v2_record/wave0_r31 电池+CI+重下离线重放回执);公开清洗扫描零命中
  (私有路径 seat log 内已 ~ 归一,零键形)。
- 重下实包离线重放(R30 起口径): 推送后 fetch origin→远端 HEAD 核对→git archive
  该 SHA 干净树为引擎→另干净目录按清单版本重放,回执补入 `wave0_r31/`。

## AC 状态

- **AC3(机构观点验证)**: 维持 **PARTIAL**——C 型到期预测实判首验窗 **2026-12**(日历门未到,依据真实到期证据填报;六标签全库 INSUFFICIENT=库龄函数,如实)。

## 停等事项

- 外部审计终判;**正式合并 PR #1 / LIVE 部署 / 付费凭证: 由用户裁定**(本轮零 LIVE 写入,LIVE 数据树只读复制)。
