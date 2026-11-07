# IA-P2-WP-B DELIVERY — 交付与证据索引

> 包: IA-P2-WP-B · 分支: `dev/p2-impl-b` · 基线 BASE-P2B=`a040faa741a69f4e7f037fb6e778f4e0bda3305a`(git rev-parse 实取 40 字符) · 本包**无并入步**(f8ed401 经 R033 并入步 dcfc7d0 祖先在场,merge-base --is-ancestor exit 0)
> 合同: IA-P2-WP-B-AC-v1.0(冻结,提示词附录A 注入) · 本文件=白名单 #4(§零.2)
> 时区: 未注明者 UTC。数值标注纪律同 REPORT §六(逐值 `[实取·来源]`/`[示意·非实取]`)。

## §一 提交序(k=4 笔 [实取·git log dev/p2-impl-b],本包无并入步)

| 笔 | SHA | 面 |
|---|---|---|
| 1 登记笔 | c825ee4 | REPORT §零 开工登记(规格抄录/白名单/DP/参数 P-B-01..18/前置实读/开工核验/BRANCH-SET 异常登记/运行边界) |
| 2 实现笔 | c906db5 | scripts/deep_research_matrix_engine.py(816 行)+tests/test_p2_wp_b.py(1009 行/57 用例/14 类)+REPORT §零.10 实现期登记(3 files/1839 insertions) |
| 3 报告笔 | (本笔) | REPORT §一-§六 回填+§零 路径/时点标注修正 5 处+DELIVERY §一-§五 新增 |
| 4 终笔 | (本笔) | DELIVERY §六 zip 定值登记(唯一补记位) |

模块面: 恰 1 个代码模块(矩阵装配与轮次引擎)+1 测试文件+REPORT+DELIVERY=k=4 白名单全量;本包无并入步,设计三件已在 BASE 在场→`git diff --name-status BASE..HEAD` A=4/M=0/D=0 [实取·§二取证]。

## §二 证据指针表(证据包根: /tmp/p2-wp-b-evidence/,装配后=IA-P2-WP-B-EVIDENCE.zip)

| 类 | 成员 | 要点 |
|---|---|---|
| 开工取证 | 01-startup-forensics/(heads-live-startup.txt 52 支·捕获 mtime 13:50:03 本地经 copy2 保留/branchset-frozen-table.txt/local-remote-refs.txt 第三源/whitelist-overlap-check.txt 0 字节/ls-remote-{main,p2-design,heads-prepush}.txt 推送前重取/design-blob-{head,p2design}.txt 等值/branchset-anomaly-analysis.txt/startup-README.txt 捕获语义) | main=a040faa7 全值一致;52 支无本分支;p2-design=f8ed401;4 支表值异常判定=提示词侧转录讹误(第三源与 live 逐一一致);设计三件 blob 双侧等值;白名单零重合 |
| 交付件副本 | 02-deliverables/(REPORT/DELIVERY/模块/测试 4 件) | 装配时点 TIP 版;与仓库工作树逐字节等值(§六 交叉哈希);模块 19a3a50e… 与注入前后等值链同值 |
| 负向敏感性 | 03-negative-sensitivity/negative-sensitivity-injections.txt | 三注入红 2/3/1(全部一次命中,无测试缺口暴露);恢复后 57 全绿;模块 sha256 注入前后等值 19a3a50e…;测试文件全程零改动 0a1484c0…;注入循环前首轮测试运行暴露缺陷 2 处当场修复(如实区分) |
| 本地 CI | 04-local-ci/(local-ci-summary.txt+suite-logs/ 逐套日志) | TOTAL=80/RUN=79/EXIT0=79/SKIPPED=1/FAIL=0;=WP-A 时点 79 槽+本包新增 1,零回归 |
| 运行锚定 | 05-acceptance-anchors/(daily-before/after.sha256+research-before/after.sha256+e2e-run-stdout.txt 全量日志+anchor-verdict.txt) | 官方 e2e exit=0: 快照 research_snapshot_20261102 digest 82bd93df… Gate A=FAIL(core_missing 5)→fail-closed 拒收→§4.4④ INCONCLUSIVE(任务 RT-DR-20261107-60e21f15);daily=27/27 前后逐行等值;research=13→24(+11/-0,全部运行产物区新增) |
| LIVE 隔离 | 06-live-isolation/(launchagents-list.txt/launchagents-sha256.txt/live-isolation-checks.txt) | LaunchAgents 12/12 与 WP-A 基线逐文件 sha256 全等(launchctl 零调用);交付件源码 grep LIVE 面常量 0 命中;LIVE 树复核=环境不可及,如实分列 NOT RE-VERIFIED@执行侧+结构性替代证据四项(REPORT §三.6) |
| git 取证 | 07-git-forensics/(BASE..HEAD name-status/rev-parse 链/log 父对/分支与 HEAD reflog 事件分类/tag 前后/push-output.txt 推送后 ls-remote 对照) | 终笔前装配;A=4/M=0/D=0/merges=0;reflog 零 reset/amend;tag 前后等值;推送后 53 支=52 既有尖端与开工快照全值一致(ZERO-DRIFT)+本分支新增 |
| 自述 | 08-selfreport/(selfreport-draft.txt 装配时点版) | 终局自述以会话 stdout 四段为准(R065 口径) |
| 清单 | SHA256SUMS | 逐成员 sha256;清单自身显式豁免(R019-D3/R065 先例) |

CI dispatch 登记件: rounds/035/P2-WP-B-CI-dispatch-evidence.md(操作者面;执行Agent 不 dispatch)。

## §三 合同逐条自评(C-AC-01..07)

| AC | 要点 | 自评 |
|---|---|---|
| C-AC-01 | 开工序列(占位符核验/远端实取/切支/设计在场[无并入步]/规格抄录/白名单登记) | **PASS**: §零.1-§零.7 全链登记;BRANCH-SET 异常按显式判据不触发停止(§零.7.4/§三.1) |
| C-AC-02 | 5 验收要点→实现/证据/自检映射 | **PASS**: REPORT §二 表(要点①-⑤ 逐条 file:line+类·用例数) |
| C-AC-03 | 纯度面(import/网络/数据源;AC-03.1 标准库+既有依赖;真实运行面=离线 sb 构建,零网络) | **PASS**: P-B-16 实现值一致;TestStaticPurity·3(零 data/daily 字面/零网络 import/产物区恒 data/research 子域);AC-03.7=§零.9 不适用(清单无调用面文件即证) |
| C-AC-04 | 测试纪律(fixture 唯一数据源/预期值硬编码字面量/负向敏感性/历史回归) | **PASS**: 合成 fixture+38 黄金常量(§五映射表);三注入红 2/3/1+恢复绿+哈希等值;80 套件零回归 |
| C-AC-05 | 证据包(8 类+SHA256SUMS 自豁免) | **PASS**(终笔定值): §二指针+§六 zip 定值(装配器 hashlib 与 shasum 独立复算双源一致;unzip -t 无错;SHA256SUMS 逐条解包复算) |
| C-AC-06 | CI 零回归 | **本地面 PASS+CI 面 NOT VERIFIED(操作者保留)**: 本地镜像 80 槽 FAIL=0;真实 CI run=操作者 dispatch 面(rounds/035),执行时点未产生,如实分列 |
| C-AC-07 | git 纪律/LIVE 隔离/零破坏性(生命周期经既有状态保护转递=AC-07.5 面;快照加载结构性不可达 data/daily) | **PASS**: §二 git 取证;LIVE 隔离(§三.6: LaunchAgents 12/12 全等+LIVE 树 NOT RE-VERIFIED@执行侧 如实分列,不以结构性证据冒充实读 PASS);AC-07.5=P-B-14(drr.append_lifecycle_event 转递+TestStateProtection·6);快照=drr._load_snapshot_for_verify 复用+TestStaticPurity |

## §四 如实偏差登记(全部=REPORT §三 详情)

1. BRANCH-SET 提示词侧转录讹误(4 支;2 条 39 字符结构无效 SHA 反证;建议合同存档勘误,执行Agent 无权改)。
2. 实现期缺陷修复 3 处+文案 1 处(测试首轮运行暴露、提交前修复、零事后改档);修复B=沙箱逃逸级(绝对常量 join 语义,误落 gitignored 运行产物区非 LIVE,当场清除+测试断言锚定)。
3. 黄金 digest 定值 3 轮定稿,scratch 侧位置参数错配讹误当场逐字节 diff 修正(独立预计算侧讹误;测试 fixture 无缺陷)。
4. 负向注入循环零测试缺口(三注入全部一次命中,与 WP-A 注入2先例如实区分);缺陷暴露来自注入循环前的测试运行,时序如实登记。
5. 官方 e2e 结果=数据阻断路径(情形(c) 合法如实): Gate A FAIL core_missing 5→fail-closed→§4.4④ INCONCLUSIVE;开工探针已预登记预期路径,不编造放行态。
6. LIVE 树复核环境不可及(会话允许目录外)→NOT RE-VERIFIED@执行侧 如实分列+结构性替代证据;LaunchAgents 12/12 与 WP-A 基线全等。
7. CI run ID 如实分列 NOT VERIFIED@执行侧(操作者 dispatch 面 rounds/035)。
8. REPORT §零 证据包路径标注修正 4 处+时点标注修正 1 处(报告笔时点,零语义;装配终局布局 01-startup-forensics 对齐 WP-A)。

## §五 参考与漂移维护策略

- 参考: REPORT §零.5/§零.6(DESIGN/上游 file:line 全量);P1/P2 族先例=R019-D3(清单自豁免)/R022+R014-D3(fixture 唯一数据源+字面量)/R065(zip 定值双算+装配时点版口径)/R033 同型(提示词侧转录讹误处置)/R066(行号差异如实注记)。
- **漂移维护三要素**: ①fixture 唯一数据源=tests 内 `FIX_SNAP_B`/`FIX_SNAP_B_FAIL`(L107/L128,18+2 合成事实,含负向事实 ODD/WEIRD/BROKEN/HASHFORM)+黄金输入集,零真实档零网络(e2e 类自建最小合成数据档于 tmp);②预期值全部硬编码字面量(L43-L94 黄金族 38 常量+各负向期望消息);③fixture→断言映射表如下(行号=实现笔 c906db5 实读):

| 断言组 | fixture/输入 | 预期值字面量 | 测试位置 |
|---|---|---|---|
| 任务/假设/条件/事件 ID 族 | 黄金输入集+GOLDEN_PARAMS(L54) | GOLDEN_TASK_ID/HP1-3/FC1-3/EV_INIT/EV_ACTIVATE(L43-L51) | TestGoldenRegistration L263-L305 |
| digest 绑定(双快照) | FIX_SNAP_B(L107)/FIX_SNAP_B_FAIL(L128) | GOLDEN_DIGEST_B="41fb4043bb86a171"/GOLDEN_DIGEST_B_FAIL="a1ad1572eed4645f"(L52-L53) | TestGoldenRegistration+TestEvidenceGroundingNegative L306-L372 |
| 证据 ID 族(14 条) | E1-E5/E14(H1)/E6-E10(H2)/E11-E13(H3) 规格 | GOLDEN_E1..E13/E14(L62-L75) | TestEvidenceGroundingNegative+TestMatrixAssembly L306-L510 |
| 接地负向(事实四路错配/质量/Gate A/缺档/原子性) | ODD/WEIRD/BROKEN/HASHFORM 负向事实+FIX_SNAP_B_FAIL | ValueError 消息片段(未命中/不相等/质量/门禁/快照文件) | TestEvidenceGroundingNegative L306-L372 |
| schema 负向 | weight/direction/mechanism/explained/fact_id/缺字段各态 | ValueError 消息片段 | TestEvidenceSchemaNegative L373-L415 |
| append-only+零墙钟 | 同输入重放/同日异刻 | rejected-duplicate/原档字节不变/同 ID | TestAppendOnlyEvidence L416-L447 |
| 矩阵 summary/cells | E1-E14 黄金证据集 | GOLDEN_SUM_H1/H2/H3(L90-L94: 5★/封顶 3★/去重 1★)/cells 14 绑定对 | TestMatrixAssembly L448-L510 |
| 星级同构 | 同证据集经 ae.star_level_from_evidence 复算 | 矩阵 star≡ae 输出(逐假设相等) | TestStarIsomorphism L511-L526 |
| 确定性 | 同沙箱重复汇编/跨沙箱同输入 | canonical JSON 逐字节相等×2 | TestMatrixDeterminism L527-L562 |
| 轮次 ID 族(9 轮次场景) | R1 证据/R2 可计算/R3 义务/R4 hold/终态四路/优先序 | GOLDEN_RD_*(L78-L86) | TestRoundAdvance+TestRoundTerminal+TestRoundSequencing L563-L847 |
| 阻断复核负向 | 放行态谎报阻断/缺档快照 | ValueError+零落档 | TestRoundBlockingNegative L743-L772 |
| 状态保护 | 未激活/异假设/超预算/终态后各态 | ValueError/INCONCLUSIVE 终态保护 | TestStateProtection L848-L904 |
| 静态纯度 | 模块源码文本+AST | 零 data/daily 引用/零网络 import/产物区子域 | TestStaticPurity L905-L943 |
| e2e 离线链 | 最小合成数据面(tmp) | rejected-fail-closed/INCONCLUSIVE/事件链/产物沙箱内聚/不构成投资建议声明/重放拒 | TestOfflineE2E L944-L1009 |

行号漂移注记: 上表行号为实现笔 c906db5 版;后续演进以类名+用例名为锚,行号仅辅助(R066 口径)。

## §六 zip 定值登记(终笔唯一补记位)

**装配定值**(装配器 /tmp/p2b-assemble.py,2026-11-07 终笔时点;证据包根 /tmp/p2-wp-b-evidence/):

- 包: `IA-P2-WP-B-EVIDENCE.zip`,**292516 字节 [实取·zip 文件大小]/未压缩合计 875817 字节 [实取·zipfile infos 合计,121 files 含清单]**;
- 成员: **SHA256SUMS 清单 120 条 [实取·清单行数]**(staging 121 文件,清单自身显式豁免,R019-D3/R065 先例);根层恰 8 类目录+SHA256SUMS 零杂散 [实取·zip namelist 根层清点]: 01-startup-forensics(11)/02-deliverables(4)/03-negative-sensitivity(1)/04-local-ci(80=summary+79 套件日志)/05-acceptance-anchors(7)/06-live-isolation(3)/07-git-forensics(13)/08-selfreport(1);
- sha256: **`5e01a437340b57a09008dabbd5e63fd9998bc469d2320bc1f39aa50d419fbb9a` [实取·装配器 hashlib 与 shasum -a 256 独立复算双源一致]**;
- 完整性: `unzip -t` No errors detected [实取·外部命令第二源]+zipfile.testzip 无错 [实取];SHA256SUMS 120 条解包逐条复算 **120 OK/0 BAD [实取·装配器校验循环]**;
- 双源副本交叉哈希: 02-deliverables 4 件(REPORT/DELIVERY/模块/测试)与仓库工作树逐字节等值 **4/4 EQUAL [实取·sha256 对照]**;其中模块 `19a3a50e…` 与负向敏感性注入前后等值链同值(§二取证链闭合),测试 `0a1484c0…` 同款闭合;
- 装配时点 TIP=报告笔 `5bbee29`(rev-parse=推送后 ls-remote 单支值一致,07/rev-parse-tip.txt+push-output.txt);zip 内 DELIVERY/自述副本=装配时点版,不含本 §六 定值行(R065 先例口径),终局自述以会话 stdout 四段为准;
- 如实登记: push 原始输出经会话 stdout 呈现(输出重定向落档通道被环境安全策略拒),07-git-forensics/push-output.txt 为推送后单支 ls-remote 复核+说明头(等价终态证据,非原始输出副本);07/zero-drift-check.txt 首版装配脚本装饰行因相邻字符串字面量乘法缺陷错列,修正直写版+缺陷注记入件(对照数据行不受影响,07/forensics-README.txt 登记)。
