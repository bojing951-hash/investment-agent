# IA-P3-WP-B DELIVERY — P3 收尾层第 2 实现包(新证据关联与持续跟踪聚合)

> 包: IA-P3-WP-B(#33/#34 挂靠) · 分支: `dev/p3-impl-b` · 合同: IA-P3-WP-B-AC-v1.0
> 基线: BASE-P3B=`b3628fdef81c81c7b46a698e89aca5b7a9925a30`(origin/main 开工实取一致)
> 本包无指定并入步(合同 §4;设计经祖先链在场,步骤4 双核验通过)
> 本文=装配时点稿(zip 定值行以终笔提交与 stdout 四段为准);时区未注明者 UTC。

---

## §一 交付物(k=4 白名单,恰 B=4 纯新增)

| # | 文件 | 行数(实取) | sha256(实取@所属笔提交时点) |
|---|---|---|---|
| 1 | `scripts/evidence_linkage.py` | 748 | `e639c42358017c92a59138c2c75530fb265a54033809bf48f8e43aa4c4d8f9ba`(实现笔 479ec7d 起,装配时点复核等值) |
| 2 | `tests/test_p3_wp_b.py` | 1225 | `dade7023c3480883b5e048ec099a5d326eaf86415aae6093854a9321df587de1`(同上) |
| 3 | `docs/P3_WP_B_REPORT.md` | 194(报告笔) | 终笔时点 `git show` 复核为准(本文档行数自指以 wc -l 实取为准) |
| 4 | `docs/P3_WP_B_DELIVERY.md` | 本文件 | 同上口径 |

提交链(纯线性,零 merge): 登记笔 869770a → 实现笔 479ec7d → 报告笔 0251b00 → 终笔(本笔)。
BASE-P3B 后恰 4 笔,每笔单父;`git log --merges b3628fd..HEAD`=空(证据包 03 类)。

## §二 证据清单(证据包 `/tmp/p3-wp-b-evidence/IA-P3-WP-B-EVIDENCE.zip`,合同 AC-06 八类)

| 类目录 | 成员面 |
|---|---|
| 01-spec-registration/ | REPORT §零 全节副本(规格抄录 §零.1+登记清单 §零.2..§零.10,报告笔工作树版) |
| 02-dual-source-copies/ | 4 交付件×{git-show TIP 版+工作树版}+cross-hash-table.txt(DELIVERY TIP 版如实标注未入库@装配时点,R065 先例口径) |
| 03-git-forensics/ | ls-remote(推送前 56 支=BRANCH-SET 零漂移)/log/name-status(逐提交恰 A 行)/merges-check(空)/head-parents(单父)/base+design-fix1 祖先双核验/reflog/设计在场核验原始输出(DESIGN L176-180+§4.1 L101-110+§4.2 L112-116 逐字+设计三件 hash-object) |
| 04-local-ci-mirror/ | CI 同款方法学镜像脚本+逐套件串行记录(84 行名称+退出码)+汇总结果(84=83 exit0+1 SKIP+0 非零;SKIP=身份锚 test_glm_live) |
| 05-evidence-mapping/ | AC-02 五要点映射表副本(REPORT §二)+DP 登记节副本(REPORT §零.4/§零.5)+§5.3 数值标注扫描清单 |
| 06-run-artifacts/ | 零运行产物声明+锚定(find -newer 空输出)/测试运行 stdout(117 OK)/模块 selfcheck/py_compile/黄金预计算脚本+输出/fixture 一致性脚本+输出(0 失配)/负向敏感性三注入记录+sha256 基线终态等值对 |
| 07-selfreport-copy/ | stdout 四段自述装配时点稿(与终稿差异=恰 zip 整体定值行组,R065 先例口径) |
| (根) SHA256SUMS | 清单自身显式豁免(不塞入 zip 自身;置于 zip 旁 /tmp/p3-wp-b-evidence/ 下,合同 §3 步骤12 口径) |

zip 定值(文件数/字节数/sha256)以终笔提交信息与会话 stdout 为准(zip 内本副本不含该定值行,R065 先例口径)。

## §三 验收对照(合同 AC 逐条;详情见 REPORT §二/§六)

- AC-01 规格抄录: REPORT §零.1 DESIGN L176-180 逐字抄录+四要素齐备+B 行与 A 行可区分 ✓
- AC-02 五要点: ①②③④本地面 PASS(实现面+测试面 file:line 映射,REPORT §二);⑤CI 面=工件入库+本地镜像 84=83+1SKIP+0 非零零回归,**run ID NOT VERIFIED@执行席**→操作者 CHECKPOINT dispatch `rounds/039/P3-WP-B-CI-dispatch-evidence.md`
- AC-03 全合成 fixture: 唯一数据源=沙箱合成(快照/锚点/状态档/周报 md+状态 json/绑定快照全临时目录);预期值=黄金字面量 7 项(快照 digest×2+md digest+档字节 sha×4)独立预计算+测试内首原理复算双源一致;映射表见 §五;AC-03.7 不适用(零调用面,REPORT §零.9)
- AC-04 数值标注: REPORT §六 12 项+DELIVERY §二 计数逐项 [实取·来源] ✓;§5.3 六项扫描清单成件(证据包 05 类)
- AC-05 纯度: 零网络/零 GLM/零凭证/零付费(import AST 白名单+剥 docstring 禁网令牌+只读 open+零直接写调用+零默认 LIVE 路径);免责声明模块 docstring+DISCLAIMER_NOTE+简报尾行 ✓
- AC-06 git 纪律: 自 BASE-P3B 全值切出→纯线性 4 笔零 merge/amend/force;main 未触碰;LIVE/launchd 零触碰;零 tag(3 枚先存他流);终局单支推送 no-force ✓
- AC-07 不构成投资建议: 模块 docstring+DISCLAIMER_NOTE(简报渲染尾行)+关联记录 history note ✓

## §四 参考与漂移维护策略(AC-03 生效;三要素)

1. **预期值唯一来源=版本化合成 fixture**: 全部断言预期值锚定 tests/test_p3_wp_b.py 内版本化定义(FX_* 字面量 L33-108+E_* 期望清单 L123-169+GOLDEN 表 L112-115),fixture 与断言同文件同 commit 演进;黄金值另经独立预计算脚本(证据包 06 类)固化第二源,双源不一致=fixture 一致性裁定器非零退出(三方裁定 0 失配实录)。
2. **fixture 演进同 commit 同步**: 新增/修改 fixture 须与受影响断言同一 commit(单一实现笔承载,拆分即红);预计算脚本与 GOLDEN/期望清单任一侧演进,须同 commit 重算对方并留三方一致裁定输出(证据包 06 类)。
3. **真实数据档永不入预期值来源**: data/daily 与 data/research 真实档结构性禁入(测试零真实档引用,AST 禁令牌+零默认路径常量;SBANCH-TYPE 默认面在合成 metric 不入真实 registry 时如实产出空集,测试以注入面为主);ae/drr/rp/rri/sb 上游行为变化导致的漂移,以上游版本为权威修正 fixture(禁以被测模块输出口径反向固化预期值)。

## §五 fixture→断言映射表(断言组→fixture 定义 file:line)

| 断言组(测试类) | fixture 定义锚(tests/test_p3_wp_b.py) | 装配/消费面 |
|---|---|---|
| TestGoldenFirstPrinciples(黄金双源) | FX_SNAP/DEG/ANCH L33-75+GOLDEN 表 L112-115 | hashlib 首原理复算对照(禁被测模块) |
| TestParamRegistration(登记锚定) | 模块常量+REPORT §零.5 登记值字面 | registered_param_values/param_selfcheck+monkeypatch |
| TestEventGateNegative(门禁负向 17) | FX_SNAP_FAIL L55-62+write_formal_report 合成周报链 L207-235 | 三类事件构造器 fail-closed |
| TestEventGolden(事件黄金) | FX_SNAP/DEG/ANCH L33-75/MD_CONTENT+ADJ_PRED L105-106 | 事件字段黄金+digest 重算 |
| TestLoadLinkObjects(对象面) | FX_THESIS_DATA L76-85/FX_VIEWS_DATA L86-104 | 状态文件只读装载 |
| TestLayer1Evaluation(条件评估) | FX_ANCH L64-75 | ae._eval_condition_set 复用+sustain 口径 |
| TestMatchGolden(匹配黄金) | E_SNAP_ENTRIES L123-136/E_ADJ_ENTRIES L137-141 | match_event 确定性排序 |
| TestLayer2MechanismCross(第二层) | 同上+锚键机制派生 | 机制单轴交叉+资产轴缺席 |
| TestRecordLinkagesGolden(档案黄金) | GOLD_RECORD_SHA L115-121+E 字面 | 档字节 sha 黄金+零原始数值 |
| TestBuildLinkageRecordsPure(纯构造) | 同上 | 占位配号/纯函数/两口径分立 |
| TestArchiveAppendOnly(append-only) | 同上 | 重放追加+竞态拒绝+篡改 fail-loud |
| TestValidateTamperVariants(篡改 20) | _base 记录字面 L876-896 | validate_linkage_record 全字段 |
| TestRebuildDeterminism(可重建) | GOLD_RECORD_SHA L115-121 | 双档案逐字节一致 |
| TestZeroStateWrite(零状态写入) | FX_THESIS/VIEWS_DATA 状态档字节 | 要点① 字节级断言 |
| TestAggregations(聚合视图) | E_PENDING_ROWS L142-157/E_DUE_ROWS L158-169 | 两聚合清单黄金+简报子串 |
| TestStaticPurity(AST 纯度) | 模块源码文件 | import 白名单/禁网令牌/只读 open |
| TestEndToEnd(端到端) | 全 fixture 族 | 快照→裁决→聚合/周报全链 |

## §六 zip 定值(终笔登记)

路径 `/tmp/p3-wp-b-evidence/IA-P3-WP-B-EVIDENCE.zip`: **文件数 38**(7 类目录成员
01=1+02=8+03=11+04=3+05=3+06=11+07=1;SHA256SUMS 自豁免旁置不入包)· **字节数
155935** · **sha256=`824504698ef93ba911ed7f73f8efda8d3685eb6e9896c38ab497c7fd3343d609`**
(装配器 hashlib 与 `shasum -a 256` 双源复算一致;`unzip -t` No errors detected;
解包逐成员复算 38 OK/0 BAD/自引用 0;`unzip -l` 独立计数 38 files;根层恰 7 类目录)。
SHA256SUMS(38 行)旁置于 zip 同目录,清单自身显式豁免(合同 §3 步骤12 口径)。

## §七 如实偏差(R068/IA-P3-WP-B-FIX1 笔A 纯新增;AC-06.3 补齐)

> 本节=整改轮 IA-P3-WP-B-FIX1(R068)笔A 于既有 §一~§六 之后文末纯追加;既有各节零重排/零删除/零改写(笔A diff=纯新增行)。仿 R067 先例(WP-A 同构缺口补 §七 专节)。本节登记全部已登记偏差事实,**不声明「无偏差」**。

### §7.1 R039 审计唯一阻断(AC-06.3)事实与本轮补齐对照

**阻断事实(rounds/039 audit §2,逐字引述自本轮执行提示词注入文本;以 audit 落档原文为准)**:

> AC-06.3 — DELIVERY 缺“如实偏差”专节且未索引(docs/P3_WP_B_DELIVERY.md §一-§六;偏差内容仅存于 REPORT §三)。合同明文五节齐备破一;R038 审计对 WP-A 完全同构缺口判 AC-06.3 FAIL,R067 补 §七 如实偏差专节整改后方 PASS——修复面窄: 仿 R067 先例,DELIVERY 文末纯追加如实偏差专节(全文落节或引述 REPORT §三 8 项),零既有节改动,走整改轮补笔+重 dispatch CI。

**补齐对照(逐项→FIX1 包成员指针;包路径 `/tmp/p3-wp-b-fix1-evidence/IA-P3-WP-B-FIX1-EVIDENCE.zip`,装配时点 TIP=笔A 尖端)**:

| 阻断要件 | 本轮补齐落点(FIX1 包成员指针) |
|---|---|
| DELIVERY 缺「如实偏差」专节 | 本节本体(§七;插入位=§六 之后文末,恰合冻结章预期;既有节零改动) |
| 偏差内容仅存 REPORT §三、未索引 | §7.2 逐项全文落节承接 REPORT §三 实读全量 8 项(含 REPORT 行号索引,零删略零改写) |
| 证据通道(专节+装配证据可索引) | DELIVERY 双源副本→`02-dual-source-copies/`(gitshow TIP 版+工作树版+`cross-hash-table-fix1.txt`+`blob-equality-base-vs-tipa.txt`);git-chain 新取→`03-git-forensics/`;逐套件串行记录→`04-local-ci-mirror/per-suite-serial-record-fix1.txt`;本轮 AC 映射→`05-evidence-mapping/fix1-ac-mapping.md`;零运行声明→`06-run-artifacts/zero-run-products-declaration-fix1.txt`;自述副本→`07-selfreport-copy/`;装配 README(TIP full SHA+α/β 全量分类)→根层 `README.md` |
| 走整改轮补笔 | 本节=笔A;FIX1 包 zip 定值=笔B(§六 定值行组区内登记);恰 2 笔纯线性 |
| 重 dispatch CI | TIP-FIX1 推送后就绪待操作者 CHECKPOINT dispatch,登记件 `rounds/068/P3-WP-B-FIX1-CI-dispatch-evidence.md`(执行席零 dispatch,run ID 不可见不虚构) |

### §7.2 REPORT §三 执行期如实偏差项承接(实读全量=恰 8 项;逐项全文落节+行号索引)

实读 `docs/P3_WP_B_REPORT.md` §三「如实偏差与登记承接」(节首 L149,项区 L151-158),清点=**恰 8 项**,与 R039 审计登记 8 项**零出入**。以下逐项全文落节(逐字复制 REPORT §三 原文,零删略零改写;行号=本轮实读行号):

1. **实现期缺陷 2 处**(占位配号缺 :03d 零填充/拒绝路径返回值按计划面报数→如实归零)——当轮暴露当轮修复,登记 §零.10;(REPORT L151)
2. **设计口径修正 1 处**(sustain 分支首轮「sustain>0 一律 sustaining」与引擎空状态口径不一致→按 consec=1 首跨逐字对齐,复用禁分叉纪律)——登记 §零.10;(REPORT L152)
3. **CI 镜像 SKIP 分类首轮误标 6 槽**(字符串匹配把 5 个含「SKIP」字样的通过套件误计 SKIP 槽)→当场勘误为身份锚口径(唯一 SKIP 槽=test_glm_live,输出含 RUN_GLM_LIVE)→终局 83+1+0;(REPORT L153)
4. **CI run ID 执行席不可见**→⑤ CI 面分列 NOT VERIFIED@执行席,操作者 rounds/039 dispatch 通道(非偏差,如实分列);(REPORT L154)
5. **资产标签轴结构性缺席**(P-B-08 登记发现): 中文资产标签(美股等)与 registry asset_class(英文)无在场词表桥接,如实缺席不造值,记录 schema 无 asset 字段(TestLayer2MechanismCross 断言);(REPORT L155)
6. **默认锚点面注记**: 合成 fixture metric 不在真实 registry,`sb.build_anchors` 默认派生产出空集→测试以 P-B-04 注入面为主,默认面仅类型冒烟(TestEventGolden.test_snapshot_event_default_anchors_face);(REPORT L156)
7. **重放语义注记**(登记语义澄清非偏差): 同事件同日重放=同日单调追加新批(005-008),rejected-duplicate=drr 并发守卫面(测试以陈旧配号扫描模拟竞态窗口,真守卫拒绝零写入零部分落档);(REPORT L157)
8. **测试文件 1 处 subprocess 受控用途**: test_selfcheck_main_entry 仅以子进程运行被测模块 `__main__` 自检(本地零网络零凭证);被测模块 AST 纯度零 subprocess(TestStaticPurity 白名单外 import=∅)。(REPORT L158)

### §7.3 R039 审计 DEFERRED 4 项引述(DEFERRED·本轮不修)

引述自 rounds/039 audit §3(经本轮执行提示词 §1/附录A §八.1 注入;以 audit 落档原文为准)。4 项均**只记不修**,本轮零触碰(引述=文本引用,非修改):

- **DEFERRED-1(DEFERRED·本轮不修)**: tests `test_fixture_literals_sha256_of_full_set` 恒真断言(`assertEqual(len(blob), len(blob))`,建议下轮替换为具体指纹断言——本轮触改 tests 即违约;tests/test_p3_wp_b.py 本轮零触碰,blob 等值经 FIX1 包 `02-dual-source-copies/blob-equality-base-vs-tipa.txt` 锁定);
- **DEFERRED-2(DEFERRED·本轮不修)**: CI run annotation ubuntu-latest→Ubuntu 26 迁移提示(登记留意,不改 workflow;`.github/workflows/offline-tests.yml` 本轮零触碰);
- **DEFERRED-3(DEFERRED·本轮不修)**: 黄金 sha16 digest 第三源复算通道不可达(双源采认口径维持;R039 06 类固化输出经 FIX1 包携行承证,不加工);
- **DEFERRED-4(DEFERRED·本轮不修)**: DELIVERY §一 表第 3/4 行行数列自指口径(本轮**不**借机登记终值,§一 表零触碰;由笔A/笔B 白名单纪律+定值行组区外零变更锁定)。
