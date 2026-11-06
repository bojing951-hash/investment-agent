# IA-P1-WP-G DELIVERY(常态监测 #20)

> 分支 `dev/p1-impl-g`(自 BASE-P1G=`8b157fd3c0c0b8a42407e49c84cbcc1254aa8a75` 切出;路径甲=基线自带设计在场,零并入步,纯线性)。规格源=`docs/P1_DESIGN.md`(blob=`10e026c08ce2828908ff7a5421aee8aba1f4e6d0`)§六 L175+§八.2 L225-L256。定值登记=`docs/P1_WP_G_REPORT.md` §零.5/§零.6。

## ① 改动

- **白名单 A 类 k=7 纯新增**(REPORT §零.3 登记,git ls-files 零重合): `scripts/routine_health_monitor.py`(299 行)/`scripts/economy_anomaly_rules.py`(181 行)/`scripts/monitor_task_bridge.py`(234 行)/`scripts/monitor_history_view.py`(270 行)/`tests/test_p1_wp_g.py`(872 行,38 用例=7 类)/`docs/P1_WP_G_REPORT.md`/`docs/P1_WP_G_DELIVERY.md`(本文);M=0;D=0;
- **提交序**(纯线性,零 merge 零 amend 零 force): 规格笔(REPORT §零 登记)→实现笔(四模块+测试)→报告笔(REPORT §一/§二/§四+本文)→终笔(zip 定值);
- **模块面分解**(范围四面各一模块,REPORT §零.3 推导规则): 范围1=routine_health_monitor(台账+快照+新鲜度三面)/范围2=economy_anomaly_rules(DP-G2=② 独立规则模块,冻结章§四裁定)/范围3=monitor_task_bridge(RT- append-only 衔接)/范围4=monitor_history_view(economy 过滤回溯+RT- 列示+#19 前件消费);
- **零运行产物**(REPORT §三): 要点①-⑦=测试×3+CI+纪律+PENDING×2,零【数据档引用】标记;`data/daily/` 零读取零写入,`data/research/` 零真实写入(测试全在 tempfile;CLI 冒烟=测试内合成 fixture+tmp 输出);
- **上游交付件零改动**(复用调用禁复制分叉: rp.select_snapshot/rtm.make_task_id+_task_economy+save_task+SCHEMA_MIN_FIELDS/rhq.query_window+ECONOMIES/ecv.economy_row/fe.load_registry+metric;anomaly_detector.py=封版件零 import 零触碰=DP-G2=② 划界;阈值登记结构同构复用)。

## ② 证据指针

- 证据包: `/tmp/p1-wp-g-evidence/IA-P1-WP-G-EVIDENCE.zip`(八类成员+SHA256SUMS 清单自身显式豁免;整体 sha256 见 §六 定值登记);
- 本地 CI: 逐套件记录=证据包④(`local_ci.log`,77 行)——**77 槽=76 exit0+1 SKIPPED**(BASE-P1G-CI-SUITES=76+新增 tests/test_p1_wp_g.py 1=77,零回归;SKIPPED=test_glm_live 真实 GLM 套件不进 CI);驱动器=`run_local_ci.py`(与 .github/workflows/offline-tests.yml 同构: 逐套件独立子进程,test_glm_live SKIPPED);
- 负向敏感度: 四缺陷注入四红记录(injections/01 rules 含等号→严格=cond_corr 边界用例 ERROR/02 新鲜度 >→>= =等号边界用例 FAIL/03 bridge append-only 旁路→幂等重放用例 FAIL/04 history 损坏档静默跳过→corrupt 用例 FAIL);每注入后恢复原字节并复跑全绿(期望零弱化,注入脚本内建恢复);
- 套件绿态: 38/38 用例全绿(`suite-logs/test_p1_wp_g.log`);
- git 取证: 证据包③(name-status/rev-parse/log/reflog/ls-remote+设计在场核验输出);
- CI dispatch: 操作者 CHECKPOINT 面(登记件落 `rounds/065/P1-WP-G-CI-dispatch-evidence.md`,执行席不自行 dispatch);
- LIVE 隔离: LIVE 目录本轮标记 grep(`R062|R064|P1-WP-G|IA-P1-WP-G`)零命中+`real_data_acceptance.py` SHA256 不变(证据包③)。

## ③ 逐 AC 自评(自评仅供参考,判定权=Agent 4 审计)

- **AC-01 规格抄录**: PASS——REPORT §零.2 逐字抄录(§六 L175+§八.2 L225-L256 四要素+DP 节),行号=开工时点工作树实读与冻结章登记一致;清单推导逐条附依据(范围四面→四模块+DP-G2=② 独立规则模块裁定);k=7 零重合+必含件齐(REPORT/tests/DELIVERY);
- **AC-02 要点映射**: PASS——七要点+目标/范围四面映射表零漏检(REPORT §二);落点 file:line 实取;参数登记制=登记(REPORT §零 首笔)先于实现(实现笔)先于运行,登记/常量/断言三者一致(TestRegisteredParamsFrozen 4 用例);零真实运行面→要点④ CI/⑤ 纪律/⑥⑦ PENDING 面如实;
- **AC-03 测试与确定性**: PASS——38 用例全绿;零网络零新依赖零 requirements 改动;预期值字面量硬编码(rho=±1 比例序列构造/cond_move 边界 +2.0%/−2.0%/lag 92/60/27 自然日手算/窗端点 2098-12-19);合成 fixture 唯一数据源(零读真实 data/daily/ 与 data/research/;SYNTH_REGISTRY 注入面=hermetic registry);要点可离线功能点全覆盖(①②③⑤⑥⑦+范围2/4);漂移维护策略专节见⑥;AC-03.7 不适用(零外部调用面实现,判定依据=REPORT §零.5(5)+四模块静态扫描用例);
- **AC-04 引用真实性**: PASS——REPORT/本文一切 file:line 引用实现后工作树复核(§一 行号=实现终笔实取);注入摘要标注「注入摘要,非工作树实读」;跨支引用=ls-remote 实取全值;
- **AC-05 范围/分支/生产隔离**: PASS——BASE-P1G..HEAD diff=A 行恰 k=7+M=0+D=0;分支历史=BASE 切出纯线性零 merge(路径甲);reflog 零 reset/amend;BRANCH-SET 既有 49 支尖端不变+唯一新增 dev/p1-impl-g(远端 50 支);零网络(静态扫描+运行面零出站);上游件/主流水线/workflow 零改动;LIVE 零写入零 launchd;研究档案不 commit;.gitignore 不改;
- **AC-06 CI 与证据包**: 自评 PASS 待操作者 CI dispatch——本地全绿 77 槽;证据包八类成员齐+SHA256SUMS;本文五节+漂移专节;自述四段;CI dispatch=操作者 CHECKPOINT 面(非执行席动作,如实登记);
- **AC-07 研究纪律**: PASS——特有纪律 8 条登记并遵守(REPORT §零.4);缺值不填0(通道 MISSING/新鲜度缺席/序列缺席/台账缺席/损坏档五态如实);MONITOR_DISCLAIMER 登记文案逐字+非投资建议;零真实 GLM/网络/凭证/付费;研究状态保护不绕开(零 update_thesis_status+allow_state_writeback 只读+save_task append-only 唯一写面);W4/W5 零引用;白名单外需求零实施。

## ④ 如实偏差与登记

1. **CI dispatch 非执行席动作**: 合同 §六.1 dispatch=操作者 CHECKPOINT 面,执行席不自 dispatch(合同明文),本地同构 CI 已全绿(77 槽)代偿,终局 CI Run 以操作者登记件(rounds/065)为准;
2. **`__v{N}` 追加面的构造口径**: make_task_id 指纹含 frozen_params→经 build 面「同 id 异指纹」不可达(同参数才同 id);要点③ 的 __v{N} 断言经「同 task_id+deepcopy 变异 frozen_params」构造(save_task 既有机制验证,非绕过 build 校验);如实登记构造口径,幂等跳过断言则经 run_bridge 全链两次实跑;
3. **zip 内副本=装配时点版**: §六 zip 定值行不在 zip 内本文副本中(R064 384dedd+R062 §七 DISCLOSED 先例口径);终局自述以会话 stdout 四段为准;
4. **本地环境差异预声明**: 本地=macOS(Darwin 24.6.0,大小写不敏感卷)/CI=ubuntu-latest(大小写敏感)/Python 3.11+依赖安装面(workflow 明文);本地驱动器与 CI 同构(逐套件独立子进程),如环境差导致分歧→情形(b)如实分流;fixture 写档名已按上游大写约定(R062 CI-红-F1 教训承接,make_history_fixture L191-L197);
5. **非偏差登记**: `_count_by` 的 '(corrupt)' 聚合键=损坏档在 n_by_status 的显示聚合(非状态改写);`economy=None`(指标不在 registry)经上游 economy 过滤如实空窗呈现(不删行不造 economy);回溯窗缺省两模块各自常量=同值 14(DP-G1=② 单源两处,断言锚定两者相等语义)。

## ⑤ 参考

- 规格: `docs/P1_DESIGN.md` §六 L175+§八.2 L225-L256(blob 10e026c0,=基线工作树在场版);
- 合同: IA-P1-WP-G-AC-v1.0 冻结版(附录A 内嵌,contracts/IA-P1-WP-G-AC-v1.0.md 存档);
- 上游同源: 各包工作树在场 REPORT §零 登记清单(docs/P1_WP_A..F_REPORT.md、docs/P1_GAP08_*.md 等,本包零修改);
- 定值与映射: `docs/P1_WP_G_REPORT.md` §零.5/§零.6/§一/§二/§四。

## ⑥ 漂移维护策略(AC-03 生效专节;沿 R022 AC-03.6 三要素)

1. **预期值唯一来源=仓库内版本化合成 fixture**: tests/test_p1_wp_g.py 手算构造器+fixture 工厂(L45-L219: YMD/POISON/SYNTH_REGISTRY/_pair_series L72/_boundary_series L88/_write_snapshot L116/_write_ledger L130/make_health_fixture L145/make_bridge_fixture L166/make_history_fixture L180-L219)=全部断言组唯一数据源,与真实数据档零耦合;
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: 任何 fixture 值改动→受影响断言组期望字面量必须同 commit 更新(审查面=diff 内 fixture 与期望值同窗出现);
3. **真实数据档永不进入测试预期值来源**: 测试零读 `data/daily/` 与 `data/research/`(全部 tempfile 临时目录),零网络,零 GLM;若有未来用例需真实档→另行报批,不入本套件。

**fixture→预期值映射**(逐断言组可追溯):

| 断言组 | fixture 定义处 | 预期值形态 |
|---|---|---|
| 要点⑤ 参数冻结 | REPORT §零.5 登记表+模块常量 | 常量逐字断言(14/60/0.30/2.0/True+规则族三行五元组+echo_params 全 dict+DISCLAIMER 逐字) |
| 要点① 三面毒丸 | make_health_fixture(with_collectors)/make_bridge_fixture/make_history_fixture(毒丸档 7 通道) | 等值性断言+POISON 字面量 L46 零出现(视图 dict+渲染 md+任务档) |
| 要点① 静态零网络 | 四模块源文件 | 禁面 token 表(requests/urllib/socket/http/subprocess/smtplib/plistlib 等)零出现 |
| 要点② MISSING streak | snap_days 三日(20981230 EXACT/20981231 MISSING/YMD MISSING)+隔日变体 | streak=2/1 字面量+DEGRADED 回显断链语义 |
| 要点② 新鲜度 | anchor_facts(CPI@2098-10-01/FED_FUNDS@2098-12-05/CN_LPR_1Y@2098-11-02)+SYNTH_REGISTRY 窗 60 | lag=92>60 越限/27 未越限/60 等号未越限(自然日手算)+EA_HICP_YOY 缺席行 |
| 要点② 台账 | _write_ledger(critical_fail/skipped 开关)+缺席变体+损坏档 | critical_failed=['facts']/skipped 字典/days_allowing=[]/note 语义 |
| 范围2 规则引擎 | _pair_series(逐日差分交替 ±amp→pearson=±1 精确;60 对净变动 0%) | rho=±1.0/chg=0.0 字面量+cond_corr/cond_move 归因+n_scored=1 |
| 范围2 含等号边界 | _boundary_series(fx [100..159,102]/eq [200..259,196],末日窗) | chg_fx_pct=2.0/chg_eq_pct=−2.0 恰达阈触发+cond_corr 注入面(−1.0≤−1.0) |
| 要点③ schema/economy | run_bridge 全链(JP 触发序列)+诱饵档 RT-DECOY | 十字段零缺/economy='JP'/pending→active/重放幂等+全目录 sha256 等值/__v2 追加原档不动/不触发零档 |
| 范围4 回溯 | make_history_fixture(series_store 六序列+RT- 三件+评分卡档大写名) | n_window=2/values=[150.0,151.0]/过滤不命中 metric_economy='JP'/'active'/'pending'/'(corrupt)' 计数/评分卡 2/4 |
| 要点⑥⑦ 静态面 | 四模块源文件+CLI 全链 | launchd/通知/GLM token 零出现+CLI 唯一写面+daily/ sha256 前后等值 |

## §六 zip 定值登记(终笔)

- 证据包: `/tmp/p1-wp-g-evidence/IA-P1-WP-G-EVIDENCE.zip`
- (装配后回填: 成员数/字节/zip 整体 sha256;装配脚本 stdout 与 shasum 独立复算一致;testzip=OK;SHA256SUMS 清单自身显式豁免不入 zip 自身校验和,R019/R023/R060/R062/R064 先例)
- 装配时点 TIP=(终笔前一笔);zip 内本文副本=装配时点版,不含本节定值行(R064 384dedd DISCLOSED 口径);终局自述以会话 stdout 四段为准。
