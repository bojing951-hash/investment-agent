# IA-P2-WP-C DELIVERY — 交付与证据索引

> 包: IA-P2-WP-C · 分支: `dev/p2-impl-c` · 基线 BASE-P2C=`f0648841fd72ad75862a0b8ef13f69a5880fdddf`(origin/main,开工 ls-remote 实取一致) · 本包**无并入步**(f8ed401 经 R033 并入步 dcfc7d0 祖先在场,merge-base --is-ancestor exit 0)
> 合同: IA-P2-WP-C-AC-v1.0(冻结,提示词附录A 注入) · 本文件=白名单 #4(§零.2)
> 时区: 未注明者 UTC。数值标注纪律同 REPORT §六(逐值 `[实取·来源]`/`[示意·非实取]`)。

## §一 提交序(k=4 笔 [实取·git log dev/p2-impl-c],本包无并入步)

| 笔 | SHA | 面 |
|---|---|---|
| 1 登记笔 | 4e94b8e | REPORT §零 开工登记(规格抄录/白名单/DP/参数 P-C-01..18/前置实读/开工核验/BRANCH-SET 异常登记/运行边界/AC-03.7 适用判定) |
| 2 实现笔 | 37d0593 | scripts/deep_research_tracking_engine.py(1004 行)+tests/test_p2_wp_c.py(1386 行/77 用例/13 类)+REPORT §零.10 实现期登记(3 files/2407 insertions) |
| 3 报告笔 | (本笔) | REPORT §一-§六 回填+DELIVERY §一-§五 新增 |
| 4 终笔 | (本笔) | DELIVERY §六 zip 定值登记(唯一补记位) |

模块面: 恰 1 个代码模块(跟踪触发与 GLM 综合对接)+1 测试文件+REPORT+DELIVERY=k=4 白名单全量;本包无并入步,设计三件已在 BASE 在场→`git diff --name-status BASE..HEAD` A=4/M=0/D=0 [实取·§二取证]。

## §二 证据指针表(证据包根: /tmp/p2-wp-c-evidence/,装配后=IA-P2-WP-C-EVIDENCE.zip)

| 类 | 成员 | 要点 |
|---|---|---|
| 开工取证 | 01-startup-forensics/(startup-forensics.txt: 开工时点 git status+ls-remote 53 支全表(main=f0648841 全值)+冻结表对照+设计三件 blob 双侧等值+BRANCH-SET 异常判定;P2_DESIGN-baseline-copy.md 基线设计件副本(232 行 [实取·wc -l]);REPORT-section-zero.md 登记笔时点 §零 副本(105 行 [实取·wc -l]);报告笔时点起前两件自 02-spec-transcription 并入本类,终局布局根层恰 8 类目录) | main=f0648841 全值一致;53 支无本分支;4 支表值异常判定=提示词侧转录讹误(§零.7,WP-B R033 同型);设计三件 blob 双侧等值=冻结章三值;白名单零重合(§零.3) |
| 交付件副本 | 02-deliverables/(REPORT/DELIVERY/模块/测试 4 件;终笔前装配时点写入) | 装配时点 TIP 版;与仓库工作树逐字节等值(§六 交叉哈希);模块 `fd927a94…` 与负向敏感性注入前后等值链同值(§二取证链闭合) |
| 负向敏感性 | 03-negative-sensitivity/(negative-sensitivity-injections.txt+golden-precompute/{wpc-golden-precompute.py,wpc-digest-check.py,precompute-output.txt,digest-check-output.txt}) | 三注入红 5/1/1(全部一次命中,无测试缺口暴露;注入①5 红含黄金 CON 指纹下游 3——黄金链本身即窗口语义敏感性锚,红数构成如实拆分);恢复后 77 全绿;模块 sha256 注入前后等值 `fd927a94…`;黄金 25 字面量独立预计算 24 GOLDEN-OK+digest 独立 EQUAL(脚本侧 ACT 槽位缺陷 1 行 MISMATCH 已注记=REPORT §三.4) |
| 本地 CI | 04-local-ci/(local-ci-mirror.txt: offline-tests.yml 同口径逐套登记) | TOTAL=80/RUN=80/EXIT0=80/SKIPPED(镜像面)=0/FAIL=0;=基线 79 run 零回归+本包新增 1;槽位记账 79 run+1 SKIP→80 run+1 SKIP [实取·git ls-tree f0648841=80 tracked] |
| 验收锚定 | 05-acceptance-anchors/(zero-run-products-anchor.txt+daily-tree-sha256.txt) | §零.8 零运行产物判定的包末复核: data/research 全树清点 `wp_c` 零命中+git status clean;data/daily 全树 sha256 现存态锚 28 行 [实取·wc -l]=本包零数据面运行的负向证据(对照 WP-B 的 before/after 双锚: 本包无真实运行故单现存态锚) |
| LIVE 隔离 | 06-live-isolation/(launchagents-sha256.txt+live-isolation-checks.txt) | LaunchAgents 12/12 与 WP-B 证据基线逐文件 sha256 全等(launchctl 零调用);交付件源码 grep LIVE 面常量 0 命中;LIVE 树复核=环境不可及,如实分列 NOT RE-VERIFIED@执行侧+结构性替代证据四项(REPORT §三.7) |
| git 取证 | 07-git-forensics/(BASE..HEAD name-status/rev-parse 链/log 父对/分支与 HEAD reflog 事件分类/tag 前后/push 后 ls-remote 对照) | 终笔前装配;A=4/M=0/D=0/merges=0;reflog 零 reset/amend;tag 前后等值;推送后 54 支=53 既有尖端与开工快照全值一致(ZERO-DRIFT)+本分支唯一新增 |
| 自述 | 08-selfreport/(selfreport-draft.txt 装配时点版) | 终局自述以会话 stdout 四段为准(R065 口径) |
| 清单 | SHA256SUMS | 逐成员 sha256;清单自身显式豁免(R019-D3/R065 先例) |

CI dispatch 登记件: rounds/036/P2-WP-C-CI-dispatch-evidence.md(操作者面;执行Agent 不 dispatch)。

## §三 合同逐条自评(C-AC-01..07)

| AC | 要点 | 自评 |
|---|---|---|
| C-AC-01 | 开工序列(占位符核验/远端实取/切支/设计在场[无并入步]/规格抄录/白名单登记) | **PASS**: §零.1-§零.7 全链登记;BRANCH-SET 异常按显式判据不触发停止(§零.7/§三.1) |
| C-AC-02 | 5 验收要点→实现/证据/自检映射 | **PASS**: REPORT §二 表(要点①-⑤ 逐条 file:line+类·用例数) |
| C-AC-03 | 纯度面(import/网络/数据源;AC-03.1 标准库+既有依赖;零运行产物=§零.8 判定,测试全离线) | **PASS**: P-C-15/16/17 实现值一致;TestStaticPurity·3(零 data/daily 路径字面[文档串纪律表述除外 WP-A 先例]/AST 零网络 import+import 面白名单/零研究状态档字面);AC-03.7=适用最保守口径处置(§零.9: GLM 接口预留面一律本地合成桩,桩注入点 file:line 已登记=REPORT §零.10) |
| C-AC-04 | 测试纪律(fixture 唯一数据源/预期值硬编码字面量/负向敏感性/历史回归) | **PASS**: 合成 fixture(5 快照含 SNAPSHOT_POST 窗口敏感锚)+25 黄金常量(§五映射表);三注入红 5/1/1+恢复绿+哈希等值 `fd927a94…`;80 套件零回归 |
| C-AC-05 | 证据包(8 类+SHA256SUMS 自豁免) | **PASS**(终笔定值): §二指针+§六 zip 定值(装配器 hashlib 与 shasum 独立复算双源一致;unzip -t 无错;SHA256SUMS 逐条解包复算) |
| C-AC-06 | CI 零回归 | **本地面 PASS+CI 面 NOT VERIFIED(操作者保留)**: 本地镜像 80 run FAIL=0;真实 CI run=操作者 dispatch 面(rounds/036),执行时点未产生,如实分列 |
| C-AC-07 | git 纪律/LIVE 隔离/零破坏性(生命周期经既有状态保护转递=AC-07.5 面;快照加载结构性不可达 data/daily) | **PASS**: §二 git 取证;LIVE 隔离(§三.7: LaunchAgents 12/12 全等+LIVE 树 NOT RE-VERIFIED@执行侧 如实分列,不以结构性证据冒充实读 PASS);AC-07.5=P-C-13③(TRACKING→ARCHIVED 经 drr.append_lifecycle_event 既有迁移表转递+TestConclusionStateMachine 终态保护/处置非 TRACKING 如实);快照=drr._load_snapshot_for_verify 复用+TestStaticPurity |

## §四 如实偏差登记(全部=REPORT §三 详情)

1. BRANCH-SET 提示词侧转录讹误(4 支;2 条 39 字符结构无效 SHA+2 条单字符替换;建议合同存档勘误,执行Agent 无权改)。
2. 实现笔提交信息逐类用例计数 4 处偏差(提交信息 12/8/8/8 vs 实取 11/6/7/7;总数 77/类数 13 无误;零 amend,以 REPORT §一.2/§六 勘误登记处置)。
3. 实现期缺陷修复 3 处(list_triggers 语法错误 py_compile 即红未入测试运行/_decide_status CONFIRMED 分支 NameError 冒烟即红/协议类文档串装饰性,均提交前修复零事后改档;与 WP-B 修复B 沙箱逃逸级如实区分——本包无沙箱逃逸级)。
4. 黄金预计算脚本侧 ACT["DIGEST"] 槽位缺陷 1 行 MISMATCH(当场注记+digest 独立复算件证 EQUAL;独立预计算侧缺陷,测试 fixture 无缺陷,WP-B scratch 先例同型)。
5. 负向注入②敏感性=1 红且防御双层(前置门+schema prior_status 词表兜底,单层失活不至静默改写,如实不强凑红数);注入①5 红含黄金指纹下游 3(红数构成如实拆分)。
6. CI run ID 如实分列 NOT VERIFIED@执行侧(操作者 dispatch 面 rounds/036)。
7. LIVE 树复核环境不可及(会话允许目录外)→NOT RE-VERIFIED@执行侧 如实分列+结构性替代证据四项;LaunchAgents 12/12 与 WP-B 基线全等。
8. 本包 §零 零标注修正(登记笔即按终局证据包布局书写,报告笔复核零修正;与 WP-B 5 处修正先例如实区分)。

## §五 参考与漂移维护策略

- 参考: REPORT §零.5/§零.6(DESIGN/上游/R019 跨支只读 file:line 全量);P1/P2 族先例=R019-D3(清单自豁免)/R022+R014-D3(fixture 唯一数据源+字面量)/R065(zip 定值双算+装配时点版口径+两段 push)/R033 同型(提示词侧转录讹误处置)/R066(行号差异如实注记)。
- **漂移维护三要素**: ①fixture 唯一数据源=tests 内 `SNAPSHOT_GOLD`/`SNAPSHOT_FAIL`/`SNAPSHOT_DEGRADED`/`SNAPSHOT_NOFACTS`/`SNAPSHOT_POST`(5 合成快照,L74 起;含负向事实 bad.metric FAIL/text.metric 非数值+截止日后观测 12-05=7.5 窗口敏感锚)+黄金输入集,零真实档零网络;②预期值全部硬编码字面量(L44-L70 黄金族 25 常量+各负向期望消息;测试内 CON/DSP 指纹复算用自带 `_h8` hashlib 首原理实现,禁导入模块计算=反自证);③fixture→断言映射表如下(行号=实现笔 37d0593 实读):

| 断言组 | fixture/输入 | 预期值字面量 | 测试位置 |
|---|---|---|---|
| 触发 ID 族(三子类) | 黄金输入集+GOLDEN(L44) | TRG_THESIS/TRG_PRED_MISS/TRG_PRED_PREM/TRG_PROP(L45-L48) | TestTriggerGoldenIntake L277-L319 |
| digest 绑定 | SNAPSHOT_GOLD/FAIL/DEGRADED/NOFACTS | DIGEST="2a86cee966ed2c12"(L49);FAIL 快照 blocked/DEGRADED 放行 | TestConditionGrounding L623-L680 |
| 触发 schema 负向 | engine_status 4 值/verdict 词表/评级四档/gate_status/未登记键 | ValueError 消息片段 | TestTriggerSchemaNegative L320-L407 |
| append-only+零墙钟 | 同输入重放/跨沙箱/同日异刻 | rejected-duplicate/原档字节不变/同 ID | TestTriggerAppendOnly L408-L444 |
| spawn 衔接 | TRG_THESIS/TRG_PRED_MISS+未知触发 | TASK1/TASK2 黄金 RT-DR ID(L50/L56)/拒绝消息 | TestSpawnFromTrigger L445-L484 |
| 窗口纪律(先例口径) | SNAPSHOT_GOLD+SNAPSHOT_POST | touch 提前/闭合/PENDING/DATA_INSUFFICIENT/NOT_TRIGGERED/NOT_YET_IN_WINDOW/NOT_ACTIVATED | TestConditionWindow L485-L622 |
| 接地负向 | 缺快照/Gate A FAIL/缺 facts/FAIL 质量+非数值/异假设/非法 as_of | blocked/ValueError 消息 | TestConditionGrounding L623-L680 |
| 结论状态机(五态黄金) | TASK1/TASK2 证据集 | CON_CONFIRMED/CON_EXPIRED/CON_FALSIFIED/CON_INCONCLUSIVE/CON_PARTIAL_FALSIFIED(L64-L68)+终态双拒/PARTIAL_SUPPORT 驻留两段式 | TestConclusionStateMachine L681-L851 |
| 证伪后处置 | FALSIFIED 黄金链 | DSP_NOARCHIVE(L69)+三路径全套(修订新 ID revision_of/review_request decided_by=gate/TRACKING→ARCHIVED/followup origin_trigger) | TestFalsificationDisposal L852-L1003 |
| GLM 接口(合成桩) | Stub 注入桩+PENDING 桩 | 输入契约字段/digest 绑定/缺席登记 called=False/输出 5 负向/协议 NotImplementedError | TestGLMInterface L1004-L1124 |
| 记录 schema 负向 | 结论/处置档各非法态 | 状态词表/终态前态/绑定格式/缺字段/review_request 形制消息 | TestRecordSchemas L1125-L1197 |
| 确定性 | 同沙箱重放/跨沙箱全链 | canonical JSON 逐字节等/CON 同 ID 拒/TRG+CON 指纹 hashlib 首原理独立复算 | TestGoldenDeterminism L1198-L1288 |
| 静态纯度 | 模块源码文本+AST | 零 data/daily 路径字面(文档串纪律表述除外)/零网络 import+import 白名单/零研究状态档字面 | TestStaticPurity L1289-L1332 |
| e2e 全链 | proposal→TASK3 运行期 ID(无黄金依赖) | 触发→spawn→证据→评估→证伪→处置→闭环断言+上游校验兜底 | TestEndToEndChain L1333-L1386 |

行号漂移注记: 上表行号为实现笔 37d0593 版;后续演进以类名+用例名为锚,行号仅辅助(R066 口径)。

## §六 zip 定值登记(终笔唯一补记位)

(本节由终笔回填。)
