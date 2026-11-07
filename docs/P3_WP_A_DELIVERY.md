# IA-P3-WP-A DELIVERY — P3 收尾层第 1 实现包·族首(档案检索与结论版本管理)

> 包: IA-P3-WP-A(#31/#32 挂靠) · 分支: `dev/p3-impl-a` · 合同: IA-P3-WP-A-AC-v1.1
> 基线: BASE-P3A=`8cebe74d3a848e4c50681d2a88baca1d3d0c55f1`(origin/main 开工实取一致)
> 指定并入步: 第二父=`7f43724661b50e011394e643cdd8c223c0b27a90`(dev/p3-design-fix1,v1.1 条款)
> 本文=装配时点稿(zip 定值行以终笔提交与 stdout 四段为准);时区未注明者 UTC。

---

## §一 交付物(k=4 白名单,恰 A=4 纯新增)

| # | 文件 | 行数(实取) | sha256(实取@所属笔提交时点) |
|---|---|---|---|
| 1 | `scripts/research_index.py` | 721 | ea782f210ed16340d2c75ee17985d4c7c510a7f86d76e2eb9291d8e0af119c49(实现笔 a8bf61e 起,终笔复核等值) |
| 2 | `tests/test_p3_wp_a.py` | 1081 | 307fbee84fe437a00597798290ca098cde395ef7b227bc03500d24b558af68ba(同上) |
| 3 | `docs/P3_WP_A_REPORT.md` | 207(报告笔) | 终笔时点 `git show` 复核为准(本文档行数自指见 REPORT §三.6) |
| 4 | `docs/P3_WP_A_DELIVERY.md` | 本文件 | 同上口径 |

提交链(纯线性,首笔=指定并入步): merge(601bf9a,第二父 7f43724)→ 登记笔 92bcca7 → 实现笔 a8bf61e → 报告笔 febba90 → 终笔(本笔)。

## §二 证据清单(证据包 `/tmp/p3-wp-a-evidence/IA-P3-WP-A-EVIDENCE.zip`,8 类根层目录)

| 类目录 | 成员面 |
|---|---|
| 01-branchset/ | 冻结章人工转录件(含 5 处失真,如实在场)+开工 ls-remote 转储+R037 独立链对照脚本×2+裁定输出(MATCHES-FROZEN-CHAPTER-ANNOTATION) |
| 02-git-chain/ | 提交链 log/name-status(逐提交恰 A 行)/merge 双父/reflog(装配时点=报告笔 TIP) |
| 03-golden-precompute/ | 黄金预计算脚本(首原理 hashlib/json,禁 import 被测模块)+输出 7 值 |
| 04-fixture-consistency/ | fixture 三方一致裁定脚本+输出(测试 fixture=预计算副本逐字节 7 组+主路径重演=GOLDEN 7/7) |
| 05-negative-sensitivity/ | 三注入脚本+输出(红 3/1/3→还原复绿→sha256 等值零残留) |
| 06-local-ci-mirror/ | CI 同款方法学镜像脚本+输出(83=82 exit0+0 非零+1 SKIP)+首轮误方法学输出(如实偏差)+workflow 命令依据副本 |
| 07-test-artifacts/ | 套件运行日志(Ran 75 tests OK)+零运行产物锚定(find data/research -newer 空输出)+py_compile 证 |
| 08-report-delivery/ | REPORT(报告笔版)与 DELIVERY(装配时点稿)副本 |

zip 定值(文件数/字节数/sha256)以终笔提交信息与会话 stdout 为准(zip 内本副本不含该定值行,R065 先例口径)。

## §三 验收对照(合同 AC 逐条;详情见 REPORT §二/§六)

- AC-01 规格抄录: REPORT §零.1 DESIGN L170-174 逐字抄录+四要素齐备+行间可区分 ✓
- AC-02 五要点: ①②③④本地面 PASS(模块面+测试面 file:line 映射,REPORT §二);⑤CI 面=工件入库+本地镜像 83=82+0+1 零回归,**run ID NOT VERIFIED@执行席**→操作者 CHECKPOINT dispatch `rounds/038/P3-WP-A-CI-dispatch-evidence.md`
- AC-03 全合成 fixture: 唯一数据源=沙箱合成(快照/报告/状态档/版本记录全临时目录);预期值=黄金字面量 7 项独立预计算+测试内首原理复算双源一致;映射表见 §五
- AC-04 数值标注: REPORT §六 12 项逐项 [实取·来源] ✓
- AC-05 纯度: 零网络/零 GLM/零凭证/零付费(import AST 白名单+token 面+零墙钟外泄测试锚);免责声明模块 docstring+索引 note ✓
- AC-06 git 纪律: 指定并入步恰 1(第二父=7f43724,带入恰 3 A 行)→纯线性 4 笔零 merge/amend/force;main 未触碰;LIVE/launchd 零触碰(隔离核验 stdout) ✓
- AC-07 不构成投资建议: 模块 docstring L39-42+DISCLAIMER_NOTE L104-106+record 返回 note ✓

## §四 参考与漂移维护策略(AC-03.6 三要素专节)

1. **预期值唯一来源=版本化合成 fixture**: 全部断言预期值锚定 tests/test_p3_wp_a.py 内版本化定义(GOLDEN 表 L45-56/SNAP 族 L58-87/MD 字节 L89-92/THESIS_DOC+VIEWS_DOC L94-117/CHANGES+GATE L119-122),fixture 与断言同文件同 commit 演进;黄金值另经独立预计算脚本(证据包 03)固化第二源,双源不一致=测试红(实现期实录: 折行转录丢 1 字符即被抓获)。
2. **fixture 演进同 commit 同步**: 新增/修改 fixture 须与受影响断言同一 commit(单一实现笔承载,拆分即红);预计算脚本与 GOLDEN 表任一侧演进,须同 commit 重算对方并留三方一致裁定输出(证据包 04)。
3. **真实数据档永不入预期值来源**: data/daily 与 LIVE 真实档结构性禁入(测试零真实档触碰,TestStaticPurity 源码级零 data/daily 字面锚);rp/drr/fe 上游行为变化导致的漂移,以上游版本为权威修正 fixture(禁以被测模块输出口径反向固化预期值)。

## §五 fixture→断言映射表(断言组→fixture 定义 file:line)

| 断言组(测试类) | fixture 定义锚(tests/test_p3_wp_a.py) | 装配/消费面 |
|---|---|---|
| TestGoldenFirstPrinciples(黄金双源) | GOLDEN L45-56+SNAP 族 L58-87+MD L89-92 | hashlib 首原理复算对照(禁被测模块) |
| TestDPRegistration(DP 锚定) | 模块常量面(REPORT §零.4 登记值字面) | registered_dp_values/dp_selfcheck+monkeypatch |
| TestEntrySchema | ri._mk_entry 直构(无档 fixture) | 11 键/null/规范化/负向 |
| TestSnapshotIndexing | SNAP_OK/V2/DEGRADED/FAIL L58-87;write_snapshot L170 | rp.select_snapshot+gate 消费;GOLDEN 指纹 4 |
| TestFormalReportIndexing | MD_A/B_BYTES L89-92;write_formal_report L173(状态档合成) | rp.scan_formal_weekly_reports;GOLDEN 指纹 2 |
| TestStateFileIndexing | THESIS_DOC L94-103/VIEWS_DOC L104-117 | index_state_files 消费 |
| TestVersionRecordGolden/Negative/AppendOnly | CHANGES L119-120/GATE L121-122/SNAP_OK_V2;record 助手 L196 | 三重纪律+配号+append-only;GOLDEN V2 指纹 |
| TestReviseConclusion/TestZeroStateWrite | 同上+THESIS/VIEWS_DOC 状态档字节 | 修正提案+零状态写入字节比对 |
| TestIndexDeterminism/TestIndexFileFace | SMALL 单条目(类属性)+GOLDEN INDEX_SMALL_SHA256 L55-56 | 确定性序列化 sha256 黄金 |
| TestQueryAPI | _qentries L125-143(六条目直构) | query_index 六维度 |
| TestOSkipping/TestStaticPurity | 模块源码文件+词表常量 | 登记项形/AST 纯度 |
| TestEndToEnd | 全 fixture 族(SNAP×4+MD×2+DOC×2+CHANGES/GATE) | 四源 11 条目全链 |

## §六 zip 定值(终笔登记)

- 路径: `/tmp/p3-wp-a-evidence/IA-P3-WP-A-EVIDENCE.zip`
- 文件数: **32**(31 类成员+SHA256SUMS 自豁免);根层恰 8 类目录,类计数 8+5+2+2+2+6+4+2=31
- 字节数: **72740**
- sha256: **82d218a12c05029abac0b2adedfa9762d0334bd75827ddff1be292a0444193df**(装配器 hashlib 与 shasum -a 256 独立复算双源一致;unzip -t No errors;解包逐成员复算 SHA256SUMS 31 条=31 OK/0 BAD/自引用 0)
- 装配时点 TIP=报告笔 febba90(zip 内 REPORT 副本=报告笔版,DELIVERY 副本=装配时点稿不含本定值行,R065 先例口径);终局自述以会话 stdout 四段为准。

## §七 如实偏差(R038 审计承接与 R067/FIX1 整改对照)

> 本节=IA-P3-WP-A-FIX1 笔A 纯新增(插入位=既有 §六 之后文末追加;既有 §一-§六 零重排/零删除/零改写)。
> 整改证据包: `/tmp/p3-wp-a-fix1-evidence/IA-P3-WP-A-FIX1-EVIDENCE.zip`(定值见 §六 FIX1 行组,笔B 登记);R038 原包 `/tmp/p3-wp-a-evidence/IA-P3-WP-A-EVIDENCE.zip` 只读对照源(sha256=82d218a1…93df)。

### ① R038 审计 5 阻断与 FIX1 补齐对照(rounds/038 audit §2 逐项)

| # | 阻断(rounds/038 audit §2) | FIX1 补齐落点(FIX1 包成员指针) |
|---|---|---|
| 1 | AC-06.2② 交付文件双源副本(git show 尖端版+工作树版+交叉哈希)整体缺失,核心代码件在包内零副本 | `09-dual-source-copies/`: 4 交付件×{`git show` 装配时点TIP版+工作树版}+`cross-hash-table.txt`(逐件 sha256+BASE-FIX1 侧 blob 对照;代码件=预期值 ea782f21…/307fbee8…) |
| 2 | AC-06.3 DELIVERY 缺「如实偏差」专节(五节要求破一) | 本节(§七,笔A 纯新增)+`09-dual-source-copies/gitshow-docs-P3_WP_A_DELIVERY.md`(装配时点稿双源副本之一) |
| 3 | AC-06.2④/AC-03.5 本地 CI 镜像仅聚合计数,无逐套件名称+退出码记录 | `06-local-ci-mirror/fix1-per-suite-serial-record.txt`(83 行=每套件一行「名称+退出码」+汇总行;记录头含装配时点 TIP full SHA+命令原文+「串行」方法学注记) |
| 4 | AC-06.2③ 设计在场核验(rev-parse/blob 对照)原始输出未作为 zip 成员 | `02-git-chain/fix1-design-presence-raw.txt`(5 组命令+原始输出逐字捕获: rev-parse×2/is-ancestor×2/601bf9a 第二父全值/设计三件 ls-tree 双侧对照) |
| 5 | AC-06.2⑦ 四段自述副本未入包 | `10-selfreport-copy/selfreport-assembly-time-draft.md`(四段齐备装配时点稿;与 stdout 终稿差异=恰 zip 整体定值行组,自指口径见 §六 注记) |

### ② R038 执行期 7 项偏离承接索引(R038 result.md §三 逐项承接,不删略)

1. **P-A-16 白名单枚举漏 `re`**: REPORT §零.5 参数 P-A-16 与模块 docstring import 白名单枚举均漏列 `re`(实际 import=json/os/re/sys/datetime);报告笔勘误已补录;模块 docstring 侧为零改动(保 sha256 稳定)未随改,以测试 AST 实锚为权威。
2. **CI 镜像首轮方法学误用**: 首轮误用 `python3 -m unittest tests.test_X` 循环,产生 2 假失败(helpers 导入面差异: 直接执行时 sys.path[0]=tests/ 可解析,-m unittest 不可)+5 假 SKIP(输出词面误判);按 workflow `offline-tests.yml` 实取命令勘误后重演=干净 83=82 exit0+1 SKIP(原包 06 类两方法学件对照留存,本轮 β 携行)。
3. **BRANCH-SET 转录失真裁定**: R038 REPORT §零.7 冻结章人工转录 5 处失真;经 R037 独立链机器 diff 裁定=远端零漂移(54 支全值一致+恰 main 登记内前移),失真在本席转录侧非仓库侧。
4. **实现期缺陷 3 处(当轮修复+测试复绿证实)**: 模块侧 1 处(query_index 未按 P-A-10 确定性排序,首轮红 3 暴露,补排序复绿);测试侧 2 处(GOLDEN 长串折行转录丢 1 字符被测试内首原理复算当场抓获;record 助手 `is not None` 兜底吞没显式 None 负向,改哨兵后负向复红)。
5. **锁等价套件并发假失败**: R038 终局镜像首捕与误方法学重演/负向敏感性重演并行执行时 `test_p0_baseline_lock_equivalence` 出现 1 次非零(锁等价套件对并发文件活动敏感);隔离重跑 31 用例全通过;串行重捕=干净 83=82+0+1。教训=镜像运行禁与其他套件并发——本轮 FIX1 逐套件记录显式采**串行**方法学(①.3 记录头注记在场)。
6. **CI run ID 执行席不可见**: R038 CI 面 AC-02⑤ NOT VERIFIED@执行席,run ID 证据通道=操作者 CHECKPOINT 登记件(rounds/038/P3-WP-A-CI-dispatch-evidence.md)+审计 gh 复核;本轮同口径(rounds/067/P3-WP-A-FIX1-CI-dispatch-evidence.md=操作者面,执行席零 dispatch)。
7. **行数自指占位**: REPORT/DELIVERY 行数等自指标注以占位先行、终笔以实取替换(721/1081/207 等);本文件 §一 表行数列同口径。

### ③ R038 审计 DEFERRED 4 项如实引述(逐项标注)

1. **DEFERRED·本轮不修**: 模块 docstring import 白名单漏 `re`(P-A-16;测试 AST 锚为权威,模块零改动保 sha256 稳定)。
2. **DEFERRED·本轮不修**: 镜像首轮 `-m unittest` 方法学误用史+锁等价套件并发敏感 1 次非零记录(原包 06 类 README 已登记,本轮 β 携行保留)。
3. **DEFERRED·本轮不修**: CI run ID 执行席不可见 NV 列(操作者通道已闭环)。
4. **DEFERRED·本轮不修**: 原包内 DELIVERY 副本时点稿(自指口径已采认,R038 审计 DEFERRED-4)。
