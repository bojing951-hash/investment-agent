# IA-P3-WP-F DELIVERY — P3 收尾层第 6 实现包/族末包(P3 终验+项目总封版)

> 包: IA-P3-WP-F(#38 挂靠;依赖列前件=WP-P3-A~E 全部关闭[已达成]+横切验收窗口[登记面承接]+用户实批[已取得]) · 分支: `dev/p3-impl-f` · 合同: IA-P3-WP-F-AC-v1.0
> 基线: BASE-P3F=`98f1a95d0c7345bf1c71b05766f78c394fa78618`(origin/main,开工 ls-remote 实取全值一致)
> 本包无指定并入步(纯线性;设计经祖先链在场,REPORT §零.7 双核验);时区未注明者 UTC。
> 本文=装配时点稿(zip 定值行以终笔提交与 stdout 四段为准,R065/WP-C/WP-D/WP-E 先例口径)。

---

## §一 交付物(k=4 白名单,恰 A=4 纯新增)

| # | 文件 | 行数(实取) | sha256(实取@所属笔提交时点) |
|---|---|---|---|
| 1 | `scripts/project_final_seal.py` | 1235 | `7d1701ac57fd56c05de3ca17ce44df2d6e9e2753d3c02a8e211a2bdcf75a9582`(实现笔 2d90631 起,后续笔零改动;负向敏感性三注入还原后逐字节等值复验) |
| 2 | `tests/test_p3_wp_f.py` | 1190(110 用例 19 类) | `f11e551e8bbf0f6321f7b4186c5776883374687fc94b3ea8eac8c2fa9c938a1f`(实现笔 2d90631,单笔成型零补齐) |
| 3 | `docs/P3_WP_F_REPORT.md` | 184(报告笔 ee0adaf 时点) | 报告笔时点 `git show` 复核为准(登记笔 c759640 §零+报告笔 §零.9/§一-§六 两笔承载;行数以 wc -l 实取为准) |
| 4 | `docs/P3_WP_F_DELIVERY.md` | 本文件 | 终笔时点 `git show` 复核为准 |

提交链(纯线性,零 merge): 登记 c759640 → 实现 2d90631 → 报告 ee0adaf → DELIVERY 笔(本笔)→ [真实运行+证据包装配,零提交]→ 定值笔(终笔)。
BASE-P3F 后每笔单父;`git log --merges 98f1a95..HEAD`=空(证据包 03 类)。较家族 5 笔先例多 2 笔(真实运行/装配不占提交;族末包无测试补齐/勘误笔,如实登记)。

## §二 证据清单(证据包 `/tmp/p3-wp-f-evidence/IA-P3-WP-F-EVIDENCE.zip`,8 类)

| 类目录 | 成员面 |
|---|---|
| 01-spec-registration/ | REPORT §零 全节副本(规格抄录 §零.1+登记清单 §零.2..§零.9,报告笔后工作树版) |
| 02-dual-source-copies/ | 4 交付件×{git-show TIP 版+工作树版}+cross-hash-table.txt(DELIVERY TIP 版如实标注未入库@装配时点,R065 先例口径) |
| 03-git-forensics/ | ls-remote(推送前全分支快照+dev/p3-impl-f 推送前未上远端核验+main=98f1a95 等值)/log/name-status(BASE..DELIVERY 恰 A=4+M=0+D=0)/merges-check(空)/head-parents(单父)/base+design-fix1 祖先双核验/reflog/设计在场核验原始输出(DESIGN L200-208 逐字+设计三件 hash-object 双侧等值)/LIVE 三面(grep 三令牌零命中+real_data_acceptance 执行席不可达如实登记[WP-D 冻结值 f9ca189c… 转引注记]+LaunchAgents 清单哈希) |
| 04-local-ci-mirror/ | CI 同款方法学镜像脚本+逐套件串行记录(88 行名称+退出码)+汇总结果(88=87 exit0+1 SKIP+0 非零;SKIP=身份锚 test_glm_live;基线 87 槽零回归+本包恰 +1;执行法=工作流 L45 逐字同款 `python3 "$t"` 脚本式) |
| 05-evidence-mapping/ | AC-02 ①-⑤ 映射表副本(REPORT §二)+如实偏差副本(REPORT §三)+七 AC 自评表副本(REPORT §四)+DP/参数登记节副本(REPORT §零.4/§零.5)+§5.3 数值标注扫描清单(REPORT+DELIVERY 双件) |
| 06-run-artifacts/ | 实现期零运行声明+repo 锚定双 find/测试运行 stdout(110 OK verbose)/模块 selfcheck+py_compile 实跑/首原理预计算件与输出(golden_values.json+黄金 md/json)/交叉裁定件与输出(ALL MATCH 六面)/负向敏感性三注入脚本与终态记录(10/5+1/4+19 红→复绿→sha 零残留)/**真实运行原始记录**(stdout/stderr 全文+退出码+运行前后 data/daily 与 data/research 既有档 sha256 锚定清单对照+运行产物四件 journal/seven_ac_input/seal json/md+判定=PENDING_SUPPLEMENTARY_EVIDENCE 如实) |
| 07-selfreport-copy/ | stdout 四段自述装配时点稿(与终稿差异=恰 zip 整体定值行组,R065 先例口径) |
| 08-dual-interpreter-record/ | 双解释器记录: 系统 3.9.6 全套件 110 OK+selfcheck;3.10+ 执行席不可达如实登记;守卫零版本依赖证明链(纯字符串+月长表+闰年规则,零 fromisoformat 3.11 宽形面);CI 3.11@offline-tests.yml L29 实读 |
| (根) SHA256SUMS | 清单自身显式豁免(不塞入 zip 自身;置于 zip 旁 /tmp/p3-wp-f-evidence/ 下,合同 §六.2/R019-D3 口径) |

zip 定值(文件数/字节数/sha256)以终笔提交信息与会话 stdout 四段为准(zip 内本副本不含该定值行,R065/WP-C/WP-D/WP-E 先例口径)。

## §三 验收对照(合同 AC 逐条;详情见 REPORT §二/§三/§四)

- AC-01 规格抄录: REPORT §零.1 DESIGN L200-208 逐字抄录+四要素齐备+F 行与 A~E 行可区分(族内唯一);冻结章行号登记一致偏差 0 行 ✓
- AC-02 验收要点: REPORT §二 ①-⑤ 映射表 5/5 无漏检+file:line 实锚+判据 1-6 全过;④真实运行类=run 面(DELIVERY 笔后执行,只读锚定+stdout 入证据包 06 类,本节登记)✓
- AC-03 测试与确定性: 110 用例 19 类全绿(3.9.6)+CI 镜像 88=87+1SKIP+0;全合成 fixture 唯一数据源+黄金字面量硬编码+交叉裁定 ALL MATCH 六面;漂移维护策略专节=§四(三要素);fixture→断言映射=§五;AC-03.7 不适用(REPORT §零.8)✓
- AC-04 引用真实性: file:line 实锚偏差 0;注入摘要逐处标注;设计三件工作树实读;上游交付件以在场 REPORT §零.2 为对照同源;交付物零 /tmp 运行期依赖 ✓
- AC-05 范围/分支/隔离: diff 恰 A=4+M/D=0;纯线性零 merge;main 未触碰;LIVE/launchd 零触碰(证据包 03 类三面);零网络(import 封闭集 {json,os,sys,hashlib} AST 锁定);上游件零改零复制分叉(零上游 import)✓
- AC-06 CI 与证据包: 工件面=本证据包八类+SHA256SUMS 旁置自豁免;本地镜像零回归;**CI 分支 run NOT VERIFIED@执行席**→操作者 CHECKPOINT dispatch `rounds/043/P3-WP-F-CI-dispatch-evidence.md`(执行Agent 不自行 dispatch)
- AC-07 研究纪律: 快照纪律(data/daily 相邻组件守卫全读写面+零连续字面量)+零真实 GLM/网络/凭证/付费+不构成投资建议(免责三处=模块 docstring/disclaimer 字段/渲染尾行)+研究状态档零写入+W4/W5 零接入+白名单外零实施 ✓

## §四 漂移维护策略(AC-03.6 生效;三要素)

1. **预期值唯一来源=版本化合成 fixture**: 全部断言预期值锚定 tests/test_p3_wp_f.py 内版本化定义(MINI_INDEX L34-46+seven_table 构造器 L57-70+AS_OF L32+黄金字面量组 GOLDEN_* L101-139),fixture 与断言同文件同 commit 演进;黄金值另经独立首原理预计算件(/tmp/p3-wp-f/fixture_and_golden.py,零被测模块 import;证据包 06 类)固化第二源,双源不一致=交叉裁定器非零退出(六面 ALL MATCH 实录;预计算件对 fa_digest/层 digest/overall/绿败路材料 sha/状态日志三行独立推导,与模块输出三方一致);
2. **fixture 演进同 commit 同步**: 新增/修改 fixture 须与受影响断言同一 commit;预计算件与黄金字面量任一侧演进,须同 commit 重算对方并留三方一致裁定输出(证据包 06 类);登记面漂移(清单 24 项/计时/阈值/索引 154 件)→fa_digest 变化→黄金字面量+预计算件+dp_selfcheck 镜像三面同步,漏任一=套件红(INJ1 实证 10 红);
3. **真实数据档永不入预期值来源**: data/daily 与 data/research 真实档结构性禁入(测试零真实档引用+全读写面路径守卫 fail-loud+AST 零连续字面量);归档索引=154 件冻结登记常量(禁随新增文件漂移,机械生成件为构造来源,上游新增件以上游在场 REPORT §零.2 为对照同源修订,禁以被测模块输出口径反向固化);层序关闭事实/DP-10 用户实批凭证=冻结章 §十一 注入摘要承载(非工作树实读),其演进以上游冻结章为权威。

## §五 fixture→断言映射表(断言组→fixture 定义 file:line)

| 断言组(测试类) | fixture 定义锚(tests/test_p3_wp_f.py) | 装配/消费面 |
|---|---|---|
| TestGoldenFirstPrinciples(黄金双源) | GOLDEN_* L101-139+MINI_INDEX L34+AS_OF L32 | fa_digest/determine/日历/层 digest 黄金 vs 首原理件三方 |
| TestCalendar(零 datetime 纯日历) | 无 fixture(纯日期函数) | 规范形/月界/闰年含世纪/序数往返/进位/负向 |
| TestAsOfGuard(时点守卫) | AS_OF L32 | 二十位规范形/时分秒越界/日期段校验 |
| TestPathGuards(LIVE+data/daily 守卫) | LIVE_TAIL 组件四元组(测试面构造) | 绝对/相对/~ 展开/相邻精确性/三 IO helper/verify/compile 全读写面 |
| TestJournalStateMachine(状态机) | GOLDEN_JOURNAL_* 三行 L125-139 | baseline/started 单发+黄金行+fail-loud 七面 |
| TestAmendmentRejection(恒拒面) | 无 fixture(纯状态日志) | 未登记/已登记/已开始三面 ValueError |
| TestDigestChainTamper(禁回改) | monkeypatch 回改注入 | 清单/计时回改→digest 失配→start/compile 拒 |
| TestArchiveIndexVerify(归档核验) | MINI_INDEX+迷你仓树 | 全在场计数/缺席逐字/索引结构校验五面 |
| TestSevenAcValidation(输入契约) | seven_table 构造器 L57 | 键集/字段/值域/evidence/note 十面 |
| TestCompileGreenPath(绿路汇编) | MINI_INDEX+seven_table_all_pass+GOLDEN_GREEN_* | 判定 PENDING/24 项分段 verdict/NV=3/elapsed=3/材料双 sha/状态日志三行黄金/封闭键集 |
| TestCompileFailPath(败路汇编) | seven_table_ac03_fail+GOLDEN_FAIL_* | NOT_SEALED/FAIL 逐字留档/材料双 sha |
| TestCompileMissingArchive(缺席如实) | MINI_INDEX 缺 1 件 | S2 层 FAIL+S3 FAIL→NOT_SEALED/缺席清单逐字 |
| TestCompileStatePreconditions(前置) | 状态日志+坏表 | 未 started/无 baseline/坏 verdict/坏 as_of 拒 |
| TestRender(渲染) | 同绿/败路 fixture | 首行/elapsed 行/overall digest 行/FAIL 区/免责尾行/S4 三行 |
| TestRegisteredValues(登记锚定) | REPORT §零.4/§零.5 登记值字面 | DP-10 七值/上游零消费/参数计数/dp_selfcheck+回改检出 |
| TestRegisteredIndex(154 件索引) | ARCHIVE_INDEX 登记常量 | 层计数 21/45/2/2/2/13/12/23/11/23/唯一性/自豁免/样例锚/注册表形 |
| TestAstPurity(AST 纯度) | 模块源码文件 | import 封闭集/禁调用面/网络字面量/open 恰 3 模式/零连续字面量(docstring 豁免)/编译 |
| TestZeroActiveCollection(零主动采集) | 模块源码文件 | 零监视令牌/在场核验=isfile only |
| TestRealRepoSample(真实仓稳定锚) | 27 个稳定路径清单 | 上游交付件/设计件/本包双代码件在场抽检 |
| TestCLI(入口,subprocess 受控 1 处) | 迷你仓+七AC表 json | selfcheck 零写+哨兵/run 面 NOT_SEALED 如实+重跑拒 exit1+守卫 exit1/exit2 面 |

## §六 zip 定值(终笔登记)

(定值笔区内纯追加,R065/WP-C/WP-D/WP-E 先例;文件数/字节数/sha256 以终笔提交信息与会话 stdout 四段为准)

## §七 如实偏差(全项登记;不声明「无偏差」)

与 REPORT §三 同源同步(9 项): 模块自纠 4(层集断言命名空间混淆/as_of 链式赋值笔误/SEAL_DOC_FIELDS 排序序/守卫消息 join 化,均提交前自纠未流入提交)+测试自纠 4(listdir 序/journal_compiled_record 键/docstring 豁免面/CI 镜像执行法对齐工作流 L45 脚本式)+subprocess 受控 1 处(TestCLI)+CI 分支 run NOT VERIFIED@执行席(操作者 rounds/043 dispatch)+归档索引时点注记(154 件冻结登记,后续新增结构性不在索引;L6-p3f=presence-only+NOT_VERIFIED@执行席)+行号容差承接(偏差 0);不声明无偏差。
