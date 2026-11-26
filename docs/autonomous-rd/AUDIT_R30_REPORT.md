# Audit-R30 收口报告 — 输入钉死/时点口径/自然问窗三修+真实验收

- 链: `8909db4`(R29 终笔)→ `59dcc09`(三任务代码+R30 门+真实历史夹具)→ 本提交(证据+报告)
- 基线: PR #1 head `8909db4`,CI 44908311329 三 job 绿;R30 门 37/37;R30 CI
  **44915389898** 三 job 绿@59dcc09
- 验收树: `git archive 59dcc09` + LIVE 只读复制 + 当日面真采 + 树内 `install_skill --target project`
- 电池: 202 绿+phase6-D3 未提交文档红(代码提交后消,文档提交后复跑绿) rc∈{0,5} 口径

## 任务1 — 输入钉死(第一次取数前固定快照)

- **缺陷**: 同日修订版(`research_snapshot_<date>_v2.json`)在运行中途落盘时,orchestrator 两次独立解析(S1 计划 :1893 / 报告段 :2078)与子命令子进程(ia_cli changes/overview 各自重解析)会各取各的——计划读原版、报告读新版,同一次运行两套输入;另 `fetch_ea_real_gdp_yoy(raw=…)` 注入口 `alerts` 未初始化(raw 分支才赋值,parse 段 extend 直落 `UnboundLocalError`——R29 §A 只测了在线路径)。
- **修复**:
  - `scripts/workbench_data.py` `latest_snapshot` 增 `IA_SNAPSHOT_PIN` 运行级钉死 seam(绝对路径;文件被移除→如实报错拒绝静默回退文件系统解析,fail-closed);
  - `scripts/research_orchestrator.py` `run_research` 入口(第一次取数前)解析一次并置位 env——S1 计划、`run_step` 子命令子进程(env 继承)、报告段二次解析、L1 事实面全部同一份;上游已钉死则尊重不重解析;收尾恢复入口前环境(同进程二次 run_research 不吃首跑残留);
  - 快照缺席/钉死不可读=如实落原因,各消费面走既有缺快照路径(不虚构);
  - `scripts/ea_market_collector.py` `alerts=[]` 提升到 raw 注入口之前(在线 3 次重试保留,语义不变)。
- **落点核对**: 计划=钉死解析直读;子命令=env 继承;L1/渲染=报告段同钉死解析;裁决/归档=R29 冻结面(`run.frozen_inputs` 摘要+`rd/root_overlay/` 字节副本,副本源=钉死路径的 relpath)——同日 _v2 中途落盘全程不串号。
- **门**: `tests/test_audit_r30_gate.py` §A 7 判据(raw 注入两形/钉死后 _v2 落盘再解析仍原版/新进程无钉死选 _v2(修订版感知)/子进程 env 继承/钉死文件移除 fail-closed/运行级钉死+收尾恢复(13 步 monkeypatch 台账逐步=原版,S3 期落 _v2))。

## 任务2 — 时点口径(BOJ/LPR/2022-03 锚)

- **缺陷**: `policy_decision_state` 把「已公告」当「已生效」——as_of=2026-09-20 时 official_target=1.25(09-24 才生效)且 days_since_adjustment=−4(负数日面);历史类比同步面 `history_region_sync_face` 两端共用判断截止月末,锚−3月端吃 3 个月发布面后视;生产日历缺 CN_LPR_1Y 2025-11 期条目。
- **修复**:
  - `scripts/freshness_policy.py` 生效/待生效分记: as_of 时点**已生效**(effective_on ≤ as_of)的决议构成当前官方目标面(official_target/last_effective/days_since_adjustment 恒≥0);已公告未生效落 `pending_adjustments`(+便利键 pending_target/pending_effective_on);
  - 生产日历时间线(实测): 09-19/20/23=目标 None(无已生效决议在档,如实)+待生效 1.25@09-24;09-24 切换(1.25,距调整 0);10-30 维持公告只更新确认状态(目标/生效日不动,距调整 36);11-21 距调整 58(R29 席位复验口径零回归)。生产日历无 2026-09 前决议记录——「旧目标可核实」语义经门夹具证明(前决议 0.75 已生效+新决议待生效),不向生产日历虚构前史;
  - 次月末生效窗(夹具 01-15 决/02-28 效): 窗内 02-10 无已生效新决议+0.75 待生效(不提前切换),生效日切换;
  - `config/release_calendar.json` 补 `RC-CN-LPR-2025M11`(2025-11-20 09:00,官方节奏每月 20 日;2025-11 观测=在库真实序列)——LPR 两期各表统一读官方日期与 09:00;
  - `history_region_sync_face` 锚−3月端按**自己的**可知截止(该月末)取数(判断截止端口径不变)——R29 §C7 同判据下逐位复跑绿(旧口径在该判据上不可区分,真实历史回归下区分: 见 §B4b);
  - `point_values` 同一期重复观测披露: 不同时点锚落位同一观测日→逐锚注明「与某锚为同一观测,无新增观测」。
- **渲染**: 政策官方记录面增「待生效」列(当前官方目标仍为旧值/无已生效决议则空缺,新目标自生效日起入列)。
- **门**: §B 17 判据(生产时间线六时点+82 日逐日恒≥0/夹具旧目标可核实+待生效/次月末窗三态/LPR 双期/2022-03 真实历史回归——夹具=真实采集快照只读提取带 provenance,截止端只见 2022-02(0.9)、锚−3月端只见 2021-11(2.3)非共用截止的 2021-12(1.5)/同步面端到端/真实水平序列同比缺基期=缺证/同期重复观测注明)。

## 任务3 — 自然问入口(过去N个月窗)

- **缺陷**: 「美、欧、中、日过去三个月的增长、通胀和政策哪里分化」三维判据——裸「政策」不在 DIMENSION_WORDS(只识「货币政策」四字形)→政策维整列漏检;「哪里分化」无形状词(分化未入 MAP_SHAPE_WORDS)→不判地图问句,落默认 US+CN 概览;「过去三个月」窗词形零解析→网格锚空,所问时间窗在地图面被丢弃。
- **修复**(`scripts/research_map_planner.py`):
  - DIMENSION_WORDS 补 ('政策','policy')(与「货币政策」同值,plan_map 保序去重防并列命中出重复维);
  - MAP_SHAPE_WORDS 补「分化」;
  - 新增 `_POINT_WINDOW_RE`/`parse_question_windows`: (过去|近|最近)N 个月→窗{months,from=截止−N月,to=截止,source=原词形};`parse_point_anchors` 窗起入点锚对照(window_start 标记,点锚恰=窗起时同一锚兼两职)+窗端=当期锚;`plan_map` 落 `question_window` 披露(无窗词形=None 零回归);数据需求窗由 `_question_window` 同词形解析(relative_months,单一扫描器口径不变,窗不被当点语义消费)。
- **实测**: T3 问句→**12 组网格**(美/欧/中/日×增长/通胀/政策)+dimension_source=explicit_words+锚=[3个月前(窗起),最新一期]+question_window months=3(from 2026-08-21)+数据需求窗 relative_months 3。OPEN2/NEW2 回归不变(判形/组数/隐含来源/锚=相比三个月前基线/零窗面)。
- **门**: §C 13 判据(T3 全链/12 组/显式来源/窗锚+披露/需求窗同源/变体三形(近六个月/最近12个月/过去 3 个月)/负例两形(无数量不成窗、半年非数字词形不虚构)/窗起与显式点锚并存(标记只落窗起)/OPEN2·NEW2 回归)。

## 验收记录(真实会话+实包重放)

- **树**: `git archive 59dcc096fff5138429105214bbd24ccd3ce003bb` + CODE_VERSION 印章 +
  LIVE 只读复制 + 当日面真采(ea 面以 R30 代码在线重采,BUND 两项源端封锁诚实缺席,
  其余=当日真采面保留)+ 树内技能安装;快照 series_store n=88,十项地图指标全解析,
  Gate A 缺口与 R29 同日树逐项一致(既有缺口,非回归)。
- **会话五席**(裸问句零上下文,唯一输入=原问文件):
  - **A3**(原问·12组地图): attach VERIFIED(0 违规)→独立审查 **UPHELD**(八项全过)。
    **任务1 实录**: 运行期 22:47:29(S3 数据子命令期间)同日
    `research_snapshot_20261121_v2.json` 落盘(身份协议合规+可观测标记)——
    旧工单全程原版(frozen_inputs=`fb1992a5396e033c`=base 摘要;归档包
    root_overlay 快照字节副本同摘要;终裁三处绑定一致),会话后无钉死新进程实测选
    `_v2`(mark=true),移除后回落 base(后续会话干净面)。详见
    `r30-evidence/acceptance/drop_v2_record/README.md`。
  - **B3**(换问): 22 格点值面→VERIFIED→**UPHELD**;frozen=同 base。
  - **OPEN3**(开放问): 22 格→VERIFIED→**UPHELD**;run_ok=False(TIPS_10Y 源端缺席,
    optional_data_missing 诚实随档)。
  - **T3**(任务3自然问「美、欧、中、日过去三个月的增长、通胀和政策哪里分化」):
    **12 组网格**(四地×三维,dimension_source=explicit_words)+锚=[3个月前(窗起标记),
    最新一期]+question_window months=3(2026-08-21..2026-11-21)+**22 项数据需求全部
    携带 relative_months 窗**(kind/basis/as_of 齐备)→attach VERIFIED(--allow-failed-run,
    失败步=诚实拒答类)→独立审查 **UPHELD**(94 项数值抽查全符)。
  - **NEW30**(代码冻结后新问,未参与开发——「2026年11月,日本和欧元区最近六个月的
    通胀与政策环境…」): 默认入口实跑: 地图面 4 组(JP+EA×通胀+政策)+窗 months=6
    (2026-05-21..2026-11-21)+窗起锚;**独立审查 REVISE(3 必修: 东京 10 月值提前引用/
    「8月站稳2」/「全程3上方」)→修订→复裁 UPHELD**(席位存在理由再证);诚实披露:
    裸「2026年11月」+「最近六个月」双时间词面按 R11/R12 冻结契约判多范围
    unparseable→--allow-failed-run 降级随档(地图面正确消费窗;裸月词形时点化=R31 候选)。
  - **C4**(残缺树,ea 面全撤): 草稿照出(US 面可判+EA×三维**零 ok 格**如实
    「数据不可得」+检索范围注记;双横幅 map_core_dimension_missing+
    map_current_period_missing);**实测拒绝隔离归档**: `--stage archive` rc=1,
    blocked=not_deliverable(「底座 run_ok=False 且非 optional 级显式降级(不可交付级)」)。
    席位并如实呈报残缺树根部一份非降级安装的悬空判定档(证据绑定拒用)。
- **A/B 正式交付**(操作者归档,rc=0): 完整包九件套+root_overlay 三件(快照/注册表/
  日历字节副本)+question_verbatim+verdicts/+ARCHIVE_MANIFEST——report.json、判断文件
  (agent_judgment)、观点摘要(views_digest)、root_overlay 三件、原问、裁决链、manifest
  七要件齐备;manifest 冻结摘要三件逐位匹配(root_overlay 基准);脱敏扫描零命中
  (私有路径/键形;摘要与终裁前完成)。
- **六步实包重放(A3/B3 各六绿)**: [0]严格面 rc=0 byte_equal+frozen 四查全绿
  (present/digests/match_report/verdict_binding_threeway)/[1]换本地日历逐字节不变/
  [2]重复重放包不动/[3]缺冻结件拒(rc=1)/[4]篡改一字节拒(rc=1)/[5]manifest 单侧
  改写拒(rc=1)。记录在 `r30-evidence/acceptance/replay_A3_real/`、`replay_B3_real/`。
- **重下实包离线重放**(R30 新增): fetch origin→远端 HEAD 核对→git archive 该 SHA
  干净树为引擎→提取 r30-evidence 交付包→另一干净目录六步重放(回执见 wave0_r30/
  `replay_downloaded_receipt.md`)。

## 电池与证据

- 电池(提交前工作面): **202 PASS / 1 FAIL**——唯一红=phase6-D3 未提交文档红
  (整改树工作面净判据对本轮未提交改动的既有口径,代码提交后仅余报告草稿未跟踪项,
  文档提交后复跑绿)。
- CI: run **44915389898** 三 job 绿(tests 3.11 / tests 3.12 / gates)@59dcc09。
- 证据: `docs/autonomous-rd/r30-evidence/acceptance/`(questions×5/session_A3_formal/
  session_B3_formal 含完整 root_overlay 包+seat log/session_{OPEN3,T3,NEW30}/
  session_C4_degraded 含四轮裁决链+归档拒绝回执/verdicts_20261121_22/replay_A3_real/
  replay_B3_real/drop_v2_record/wave0_r30);证据树公开清洗扫描零命中
  (私有路径已在 seat log 内以 ~ 归一,零键形)。

## AC 状态

- **AC3(机构观点验证)**: 维持 **PARTIAL**——C 型到期预测实判首验窗 **2026-12**(日历门未到,依据真实到期证据填报;六标签全库 INSUFFICIENT=库龄函数,如实)。

## 停等事项

- 外部审计终判;**正式合并 PR #1 / LIVE 部署 / 付费凭证: 由用户裁定**(本轮零 LIVE 写入,LIVE 数据树只读复制)。
