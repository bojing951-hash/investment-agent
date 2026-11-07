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
