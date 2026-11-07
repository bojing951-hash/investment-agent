# IA-P2-WP-D DELIVERY — P2 深研层第 4 实现包·族末(事件序列数据面)交付件

> 包: IA-P2-WP-D(P2 族末实现包) · 分支: `dev/p2-impl-d`(自 BASE-P2D `e557fd3a6598b0145c9c40cee07299a992ad56bb` 切出) · 合同: IA-P2-WP-D-AC-v1.0(冻结,附录A 内嵌注入)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;行号一律为本包基线工作树实读(2026-11-07 实取);提示词注入内容引用一律标注「注入摘要,非工作树实读」。
> 数值标注边界: 本文所有计数类/统计类数值逐个标注 `[实取·来源: …]` 或 `[示意·非实取]`;日期/SHA/结构编号/档键成分按合同边界出圈;URL 字符串=登记型参数(登记值,零访问)。

---

## §一 改动清单(白名单 k=4,纯新增 A=4/M=0/D=0)

提交链(纯线性,零 merge 零 amend 零 force;终笔前取证值,§六 定稿时点复核):

| 笔 | commit | 内容 |
|---|---|---|
| 1 登记笔 | `2e8d92d` | REPORT §零 开工登记(规格抄录/清单/DP/参数/前置实读/开工核验/零运行产物判定/AC-03.7 不适用判定) |
| 2 实现笔 | `4240c14` | 模块+测试纯新增+REPORT §零.10 实现期登记(黄金预计算/缺陷修复/负向敏感性/本地 CI/零运行产物锚定) |
| 3 报告笔 | `91b395c` | REPORT §一-§六 回填(实现摘要/AC-02 映射表/如实偏差/DP 零回改/git 纪律/数值标注自检) |
| 4 终笔 | (本笔) | DELIVERY 五节+漂移维护策略+fixture 映射+§六 zip 定值登记 |

逐文件(白名单与 REPORT §零.2 登记清单一致,git ls-files 零重合实取=0):

1. **`scripts/deep_research_event_calendar.py`**(470 行 [实取·wc -l]): 事件序列数据面确定性结构四件——①事件档格式(CAL-{YYYYMMDD}-{sha256[:8]} 确定性指纹不含墙钟,`make_calendar_event_id` L127/`validate_calendar_event` L152/`register_calendar_event` L225/`list_calendar_events` L260)②来源登记面(`SOURCE_WHITELIST` L69 三源免费公开零凭证零付费,登记不访问)③快照挂载(`load_snapshot_disciplined` L281 三重纪律+`mount_event_context` L398 读侧纯计算)④事件窗对齐计算(`event_window_bounds` L302+`classify_observation` L316+`event_window_observations` L333,pre 不含事件日/post 含事件日默认 5/5,FAIL 质量如实排除,零合格观测 DATA_INSUFFICIENT 不填 0)。
2. **`tests/test_p2_wp_d.py`**(702 行 [实取·wc -l],15 类 60 用例 [实取·Ran 60 tests]): 全合成 fixture 唯一数据源;GOLDEN 8 字面量(CAL×5+DIGEST×3)独立预计算首原理复算交叉验证;零网络零墙钟。
3. **`docs/P2_WP_D_REPORT.md`**(199 行 [实取·wc -l]): §零.1-.10 开工登记+§一-§六 报告(AC-01/02/04 锚定面)。
4. **`docs/P2_WP_D_DELIVERY.md`**(本文件): §一-§六。

## §二 证据指针表(证据包 `/tmp/p2-wp-d-evidence/IA-P2-WP-D-EVIDENCE.zip`;合同 AC-06 八类最低集)

| 合同类 | 证据包成员 | 内容与可直读位置 |
|---|---|---|
| ①规格抄录+登记清单 | `01-startup-forensics/` | 开工占位符/前置核验输出+DESIGN D 行基线副本+REPORT §零 副本(装配时点版)+BRANCH-SET 零漂移裁定件(含 R036 机器转储对照) |
| ②交付文件双源副本 | `02-deliverables/` | 4 白名单件双源副本(git show 尖端版+工作树版)+交叉哈希清单(manifest 逐件 EQUAL/不等即 FAIL);模块注入前后 sha256 等值链 |
| ③git 取证原样输出(含设计在场核验) | `07-git-forensics/`+`01-startup-forensics/` | name-status(A=4/M=0/D=0)/rev-parse 全值/log --parents(纯线性)/reflog(零 reset 零 amend)/tag 前后等值/ls-remote 推送后对照/push 输出;设计在场核验(merge-base --is-ancestor f8ed401 exit 0+设计三件 ls-tree 双侧 blob 等值三值) |
| ④本地 CI 逐套件记录 | `04-local-ci/` | 82 文件逐套件名称+退出码(81 exit0+1 SKIP=test_glm_live+零非零)+汇总计数件 |
| ⑤逐要点证据映射表(含 DP 登记节) | `05-acceptance-anchors/` | REPORT §二 映射表副本+REPORT §零.4 DP 登记节副本+数值标注自检清单副本(REPORT §六)+零运行产物声明(类⑥合并落位,见下行) |
| ⑥零运行产物声明(本包无真实运行面) | `05-acceptance-anchors/zero-run-products.txt` | §零.8 判定+§零.10 锚定输出(`find data/research -newer <模块>` 零输出+`git status` 快照) |
| ⑦自述报告副本 | `08-selfreport/` | stdout 四段自述副本(装配时点版;终局自述以会话 stdout 为准,R065 口径先例) |
| ⑧SHA256SUMS | zip 根层 `SHA256SUMS` | 全部成员逐件 sha256;**清单自身显式豁免不入 zip 自身**(沿 R019 审计 D3/R026 正式采用措辞) |
| (附)负向敏感性 | `03-negative-sensitivity/` | 三注入(INJ1 窗口归属红 2/INJ2 白名单红 1/INJ3 GateA 红 2)执行记录+还原 60 全绿+模块 sha256 注入前后等值(f9267192…b674c8)+黄金独立预计算脚本副本 |

zip 整体 sha256/字节数 → §六(装配时点定值;装配器 hashlib 与 `shasum -a 256` 独立复算双源一致)。

## §三 逐 AC 自评(合同 IA-P2-WP-D-AC-v1.0 §一-§七)

| AC | 自评 | 一句证据指引 |
|---|---|---|
| D-AC-01 规格抄录与交付面登记正确性 | PASS(执行席自评) | REPORT §零.1 逐字抄录(L211-L215 行号锚,四要素齐备,D 行与 A/B/C 行可区分)+§零.2 k=4 清单逐条附 DESIGN 依据+§零.3 结构约束(`git ls-files` 零重合实取=0);审计实读 DESIGN 对照 |
| D-AC-02 验收要点逐条交付与证据映射 | PASS(执行席自评) | REPORT §二 映射表 4 行=要点 4 条逐条对应((a)落点行锚实测/(b)证据指针/(c)结论);DP 判据⑥同表自检(DP-1/2/6 不触及零回改/DP-4/5 未自决/编号 6 与 DESIGN §2.4 实读一致) |
| D-AC-03 测试与确定性验证 | PASS(执行席自评;第 7 项不适用) | 清单含 2 个 .py → 第 1-6 项生效: 零网络/全合成 fixture/零新依赖、预期值字面量硬编码(GOLDEN 8 项禁导入被测模块计算)、要点可离线面逐一有用例(REPORT §二 (a)列)、本地逐套件全绿(82=81 exit0+1SKIP);第 6 项漂移维护策略=本文件 §五;第 7 项 GLM 桩=清单无调用面类文件(判定依据 REPORT §零.9)→ 不适用 |
| D-AC-04 引用真实性与注入边界 | PASS(执行席自评) | 双文档 file:line 引用逐条实测锚定(REPORT §二/§四 行锚;DELIVERY §一 同款);注入内容引用均标注「注入摘要」;跨支引用 dev/p2-design f8ed401f4274e158c06a9404149d41260e5cc0ad(ls-remote 实取,REPORT §零.7);否定性声明可 grep/diff 反证(零 data/daily 字面 grep 零命中/AST import 白名单) |
| D-AC-05 范围/分支/生产隔离 | PASS(执行席自评) | `git diff --name-status e557fd3a…HEAD` A=4 恰白名单/M=0/D=0(07 取证件);纯线性零 merge/reflog 零 reset 零 amend/不 force/不碰 main;ls-remote 推送后 55 支=BRANCH-SET 54 支尖端全值一致+唯一新增 dev/p2-impl-d;LIVE grep(R037\|P2-WP-D\|IA-P2-WP-D)零命中+real_data_acceptance.py SHA256 `f9ca189c…` 不变+LaunchAgents 零改动(06 取证件);零网络(源码 AST);研究档案零 commit;.gitignore/workflow 零改动(M=0 判据内) |
| D-AC-06 CI 与证据包交付 | 分列: 本地面 PASS+CI 面 NOT VERIFIED@执行席 | 本地面: 证据包八类齐+SHA256SUMS 自豁免+DELIVERY 五节+漂移策略专节+自述四段(stdout);套件 82=81+1 零回归(04 取证件)。CI 面: 本席不自行 dispatch(合同步骤14/AC-06.5),登记件=操作者 CHECKPOINT `rounds/037/P2-WP-D-CI-dispatch-evidence.md`(将落路径,run ID+headSha+conclusion+套件数字面值由操作者登记)——执行席对 CI run 结论如实标 NOT VERIFIED,不以本地面冒充 |
| D-AC-07 研究纪律与使用边界 | PASS(执行席自评) | 快照纪律(模块经 drr._load_snapshot_for_verify+rp 接口转递,源码零 data/daily 路径字面 grep 零命中+测试断言);数据不足=DATA_INSUFFICIENT 如实缺席不填 0;不构成投资建议声明(模块 L98 DISCLAIMER_NOTE+端到端断言);零真实 GLM/零网络/零凭证/零付费(AST+纯度类);研究状态零直改(本包新档族 calendar_event=研究素材档,非论点/观点/预测状态档,零状态机绕开面);W4/W5 零接入;白名单外零实施 |

## §四 如实偏差索引(与 REPORT §三 同源,增补 2 项;完整叙述以 REPORT §三 为准)

| # | 偏差 | 处置 |
|---|---|---|
| 1 | BRANCH-SET 54 支人工重打表 7 行 SHA 尾差 | 以 R036 证据包机器转储独立链裁定=转录失真;远端差异集恰 2 支均为登记内预期前移,52 支全值一致零漂移(REPORT §零.7/§三.1;两源对照件入证据包 01) |
| 2 | 实现期缺陷修复 1 处(测试侧) | TestEventLoading NFP spec source_id 笔误→红 1,修正后 60 全绿;模块零缺陷零改动(REPORT §零.10) |
| 3 | 本地 Python 3.9.6 vs CI 3.11 | 语法面保持 3.9 兼容;CI 面以操作者 dispatch 登记件为准(REPORT §三.3) |
| 4 | CI 面结构性留操作者 | NOT VERIFIED@执行席 分列,不冒充(REPORT §三.4;本文件 §三 AC-06 行) |
| 5 | 黄金预计算脚本 EV_CORE_CPI 槽位残留 | 预演素材未入测试,输出未被采用;黄金值实采 8 项(REPORT §三.5) |
| 6 | 报告笔提交信息 2 处标注失准(commit message 层面,提交已入链不 amend) | ①「报告283」=REPORT 行数预估残留,实测 199 行 [实取·wc -l](本文件 §一 第 3 条为实值);②「黄金8字面+25常量?实为8字面」=草稿措辞残留,正确口径=黄金 8 字面量(CAL×5+DIGEST×3),无 25 常量计数;REPORT 正文无此二失准(正文 §六 第 7/10 行为实值),偏差仅存在于提交信息文本,如实登记 |
| 7 | 无其他偏离 | 无规格冲突/无套件数不符(82=81+1)/无不触发面/无引用不可达/无中断 |

## §五 参考与漂移维护策略(AC-03 生效专节)

**规格与上游参考**: DESIGN `docs/P2_DESIGN.md`(基线工作树 blob `63a1964812f0c081aef0ea38148dec82537c7416`,与 f8ed401 侧等值)§七 WP-P2-D 行 L211-L215/§2.4 DP 表 L63-L72/§3.1 L80/D3 L88/§八 L221-L228;P2_INVENTORY P2-G-04 L163;上游在场件接口(实读,零改动): `deep_research_registrar.py`(_write_records L513-524/_load_snapshot_for_verify L778-796/前缀族 L60-63)、`research_provenance.py`(digest_snapshot L1324-1328/gate_allows_formal_research L1210-1213)、`fact_engine.py`(metric L75-76)、`deep_research_matrix_engine.py`(质量纪律先例 L260-334);同族前包测试先例 `tests/test_p2_wp_c.py`(fixture 结构 L74-116)。

**漂移维护策略声明(合同 AC-03.6 三要素,沿 R022 AC-03.6 同款)**:
1. **测试预期值唯一来源=仓库内版本化合成 fixture**: 本包全部预期值(GOLDEN 8 项字面量+窗观测值+边界日期)唯一来源于 `tests/test_p2_wp_d.py` 内版本化定义的合成 fixture(GOLDEN L37-46/SNAP_MAIN L50-71/事件 fixture L100-112),不依赖任何运行时计算产物;
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: 任何 fixture 演进(如增删事实条目/改快照结构)→ 受影响预期值在同一 commit 内同步更新,禁分离提交(分离=漂移窗口);黄金值变更须经独立预计算脚本重算三源一致后方可入链;
3. **真实数据档永不进入测试预期值来源**: `data/daily/` 及真实研究档案永不为测试预期值来源(静态纯度类断言钉住: 零 data/daily 路径字面 grep);快照 fixture 全合成,与真实快照档无派生关系。

**fixture→预期值映射(逐断言组可追溯;fixture 定义处=tests/test_p2_wp_d.py 行锚 [实取·2026-11-07 工作树实测])**:

| 断言组(测试类) | 类定义行锚 | 所消费 fixture(定义处) | 预期值形态 |
|---|---|---|---|
| TestSourceWhitelistRegistry·3 | L131 | SOURCE_WHITELIST(模块 L69,测试读常量断言其定值) | 每源六要素字面断言(free_public/none/none/URL 定值) |
| TestZeroCredentialPaid·3 | L150 | 模块源码+SOURCE_WHITELIST(L69) | 零命中断言(凭证/env/付费模式字面)+AST import 面 |
| TestEventIdGolden·4 | L192 | GOLDEN.CAL_*(L37-48)+事件 fixture EV_CPI/EV_NFP/EV_FOMC/EV_FOMC_DFED(L100-110) | CAL ID 黄金字面量(CAL-20261101-…族) |
| TestEventSchemaNegative·10 | L207 | make_event(L87)构造+白名单外值 | 拒收断言(缺字段/未知类型/未登记源/URL 失配/指标出白名单/通道外/篡改 ID) |
| TestEventRegistryFace·2 | L279 | metric_registry(config 在场件只读)+patch fe.metric | registry 在场正向+patch 缺席负向 |
| TestEventAppendOnly·3 | L302 | make_event(L87)+临时档案沙箱 | 重放拒(STATUS_REJECTED_DUPLICATE)/跨沙箱同 ID/篡改档 fail-loud |
| TestEventLoading·2 | L348 | EV_CPI/EV_NFP/EV_FOMC/EV_FOMC_DFED/EV_FAR(L100-112)落档 | 排序黄金序列(event_date,event_id 升序)/空档 |
| TestWindowBounds·7 | L376 | 纯日期参数(无 fixture) | 边界元组字面量(pre 不含事件日/post 含/pre=0 空/post=0 仅当日/负数与非 int 拒) |
| TestWindowObservationsGolden·4 | L420 | SNAP_MAIN(L50-71)+EV_CPI(L100) | pre2+post1 观测值序列字面量+窗外排除(10-20 不入窗) |
| TestWindowQuality·4 | L466 | SNAP_MAIN FAIL 质量+「N/A」条目(L50-71) | excluded_fail/excluded_non_numeric 如实列+零合格 DATA_INSUFFICIENT+无绑定须显式 |
| TestSnapshotDiscipline·5 | L501 | SNAP_MAIN/SNAP_DEGRADED/SNAP_FAIL(L50-75)+write_snapshot(L78) | 缺失拒/GateA FAIL 拒/DEGRADED 放行/digest 黄金字面量(GOLDEN.DIGEST×3)/gate 回显 |
| TestMountContext·5 | L542 | SNAP_MAIN(L50-71)+EV 族(L100-112) | 相交集黄金 event_ids/不相交排除/as_of 未来排除(future_excluded 计数)/FAIL 拒/零写入 |
| TestStaticPurity·3 | L595 | 模块源码文本+AST | 零 data/daily 字面/import 白名单/零墙钟调用 |
| TestDeterminism·3 | L631 | GOLDEN(L37-48)+SNAP_MAIN(L50-71)+跨沙箱重放 | 首原理复算==GOLDEN(三源一致)/跨沙箱逐字节等/重放同 ID |
| TestEndToEnd·1 | L669 | SNAP_MAIN+EV 族全 fixture 链 | 登记→挂载→窗计算 OK+DATA_INSUFFICIENT 混合链+免责声明断言 |

## §六 证据包 zip 定值登记(终笔装配时点定值,2026-11-07T10:4xZ)

- 装配时点 TIP=报告笔 `91b395c3ab483b7cf31cfa1fb648488c8a35c07f`(rev-parse 实取;推送#1 后 ls-remote 单支值一致=07 取证件;终笔提交后以推送#2 单支复核为准,结果登记于 stdout 自述终版);
- zip 路径: `/tmp/p2-wp-d-evidence/IA-P2-WP-D-EVIDENCE.zip`;
- **成员 42 files(41 证据成员+SHA256SUMS 自身占 1,自豁免语义)** [实取·unzip 解包计数=装配器清单计数];根层恰 8 类目录+SHA256SUMS 零杂散 [实取·zip 清单]: 01-startup-forensics 7(startup-checks/design-presence-checks/DESIGN D 行基线副本/REPORT §零 副本/branchset-adjudication/ls-remote-heads-prepush/对照脚本)+02-deliverables 9(4 件双源副本+manifest)+03-negative-sensitivity 5(injection-rerun-record/golden-precompute.py+output/EVFAR 补算件+脚本)+04-local-ci 1(local-ci-records.txt 82 套件逐条)+05-acceptance-anchors 4(§二 映射表副本/§零.4 DP 副本/§六 数值清单副本/zero-run-products)+06-live-isolation 2(live-isolation/launchagents-sha256)+07-git-forensics 12(name-status/rev-parse/log-parents/merge-count/reflog/tags×2/branch-base-proof/单支复核/全表 postpush/推送输出/推送后对照脚本)+08-selfreport 1(装配时点草稿;终局以 stdout 为准,R065 口径);类计数和 7+9+5+1+4+2+12+1=41=42−SHA256SUMS,逐类以 zip 清单为准 [实取];
- **字节数 124815**(未压缩合计见 SHA256SUMS 逐件) [实取·os.path.getsize];
- **zip sha256=`ea3d75cce93b4d34bb08a46a58fac8069e1bb1f8e81e1e4b45d7be33a7629908`** [实取·装配器 hashlib 与 shasum -a 256 独立复算双源一致;unzip -t No errors;SHA256SUMS 41 条解包逐条复算 41 OK/0 BAD/自引用行 0];
- zip 内 DELIVERY/自述副本=装配时点版(不含本节定值行,R065 口径先例);终局自述以会话 stdout 四段为准。
