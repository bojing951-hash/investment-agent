# IA-P2-WP-A DELIVERY — 交付与证据索引

> 包: IA-P2-WP-A · 分支: `dev/p2-impl-a` · 基线 BASE-P2A=`0c9fc3f88bfcfab57b4b6930912045f5bd083f5a`(git rev-parse 实取 40 字符) · 指定并入步 f8ed401(第二父)
> 合同: IA-P2-WP-A-AC-v1.1(冻结,提示词附录A 注入) · 本文件=白名单 #4(§零.2)
> 时区: 未注明者 UTC。数值标注纪律同 REPORT §六(逐值 `[实取·来源]`/`[示意·非实取]`)。

## §一 提交序(k=4 笔 [实取·git log dev/p2-impl-a],并入步不计入笔序)

| 笔 | SHA | 面 |
|---|---|---|
| 并入步 | dcfc7d0 | `merge --no-ff f8ed401`(恰 1 merge,第二父=f8ed401,设计三件 481 行带入,合同指定步) |
| 1 登记笔 | 7b6a00e | REPORT §零 开工登记(规格抄录/白名单/DP/参数/前置实读/开工核验/BRANCH-SET 异常登记) |
| 2 实现笔 | 0f2b48c | scripts/deep_research_registrar.py(842 行)+tests/test_p2_wp_a.py(595 行/45 用例)+REPORT 勘误 2 处(P-A-04/P-A-08) |
| 3 报告笔 | (本笔) | REPORT §一-§六 回填+DELIVERY §一-§五 新增 |
| 4 终笔 | (待) | DELIVERY §六 zip 定值登记(唯一补记位) |

模块面: 恰 1 个代码模块(登记器)+1 测试文件+REPORT+DELIVERY=k=4 白名单全量,`git diff --name-status BASE..HEAD` A=7(4 白名单+3 设计件)/M=0/D=0 [实取·§二取证]。

## §二 证据指针表(证据包根: /tmp/p2-wp-a-evidence/,装配后=IA-P2-WP-A-EVIDENCE.zip)

| 类 | 成员 | 要点 |
|---|---|---|
| 开工取证 | ls-remote-heads-start.txt(51 支)/frozen-sorted.txt/heads-start-sorted.txt/branchset-anomaly-analysis.txt/design-blob-{head,f8ed401}.txt/compute_golden.py | main/p2-design 全值一致;51 支无本分支;6 支表值异常判定=提示词侧转录讹误;设计三件 blob 双侧等值;黄金值独立预计算脚本(反自证纪律) |
| 负向敏感性 | negative-sensitivity-injections.txt | 三注入红 2/1/3(注入 2 首轮全绿=测试缺口暴露→补强→1 红);恢复后 45 全绿;模块 sha256 注入前后等值 8600ad36… |
| 本地 CI | 04-local-ci/(ci-mirror-summary.txt+78 套件日志)+run_ci_mirror.py(镜像脚本) | TOTAL=79/RUN=78/EXIT0=78/SKIPPED=1/FAIL=0;=P1 基线 78+新增 1,零回归 |
| 运行/锚定 | 06-acceptance-run/(data-tree-anchor-T1/T2)+hash_data_trees.py | daily=27/research=13 文件逐文件 sha256;套件重跑前后逐字节等值(零写入实证) |
| LIVE 隔离 | live-isolation-checks.txt/launchagents-list.txt/launchagents-sha256.txt | real_data_acceptance.py=f9ca189c… 等值;grep 0 命中;LaunchAgents 12/12 与 P1 基线逐字节全等;LIVE 先行修改如实登记(REPORT §三.7) |
| git 取证 | 05-mapping/(BASE..HEAD name-status/rev-parse/log 父对/reflog/tag 前后/推送后 ls-remote 对照) | 终笔前装配;A=7/M=0/D=0;reflog 零 reset/amend;tag 前后等值;推送后 52 支且既有 51 支尖端与开工快照全值一致 |
| 自述 | 07-selfreport/(stdout 四段自述原文) | 会话 stdout 存档 |
| 清单 | 08-sha256sums/SHA256SUMS | 逐成员 sha256;清单自身显式豁免(R019-D3/R065 先例) |

CI dispatch 登记件: rounds/033/P2-WP-A-CI-dispatch-evidence.md(操作者面;执行Agent 不 dispatch)。

## §三 合同逐条自评(C-AC-01..07)

| AC | 要点 | 自评 |
|---|---|---|
| C-AC-01 | 开工序列(占位符核验/远端实取/切支/并入步/设计在场/规格抄录/白名单登记) | **PASS**: §零.1-§零.7 全链登记;BRANCH-SET 异常按显式判据不触发停止(§零.7.3/§三.1) |
| C-AC-02 | 5 验收要点→实现/证据/自检映射 | **PASS**: REPORT §二 表(要点①-⑤ 逐条 file:line+类·用例数) |
| C-AC-03 | 纯度面(import/网络/数据源;AC-03.1 标准库+既有依赖;AC-03.7 GLM 调用面不适用) | **PASS**: P-A-11 实现值一致;TestStaticPurity(零 data/daily 引用/零网络 import);AC-03.7=§零.9 不适用(清单无调用面文件即证) |
| C-AC-04 | 测试纪律(fixture 唯一数据源/预期值硬编码字面量/负向敏感性/历史回归) | **PASS**: 合成 fixture+字面量(§五映射表);三注入红 2/1/3+恢复绿+哈希等值;79 套件零回归 |
| C-AC-05 | 证据包(8 类+SHA256SUMS 自豁免) | **PASS**(终笔定值): §二指针+§六 zip 定值(装配 stdout 与独立 shasum 双算一致;unzip -t 无错;SHA256SUMS 逐条解包复算) |
| C-AC-06 | CI 零回归 | **本地面 PASS+CI 面 NOT VERIFIED(操作者保留)**: 本地镜像 79 套件 FAIL=0;真实 CI run=操作者 dispatch 面(rounds/033),执行时点未产生,如实分列 |
| C-AC-07 | git 纪律/LIVE 隔离/零破坏性(AC-07.1 快照经 parse_snapshot_id 结构性不可达 data/daily) | **PASS**: §二 git 取证;LIVE 三件套等值(REPORT §三.7);AC-07.1=P-A-10 实现+TestSnapshotBinding |

## §四 如实偏差登记(全部=REPORT §三 详情)

1. BRANCH-SET 提示词侧转录讹误(6 支;2 条结构无效 SHA 反证;建议合同存档勘误,执行Agent 无权改)。
2. P-A-04 登记勘误(registry_status 归位条件面;实现期、先于运行、登记=实现终态一致)。
3. P-A-08 登记勘误(事件记录补 seq;实测发现同刻折叠不定序;同上纪律)。
4. 负向注入 2 首轮全绿→测试缺口暴露→补强双面用例;补强用例首版断言自身有误当场修正(均先于实现笔提交)。
5. 重复事件用例首版设计与防线触发次序不符→重构公共面+白盒两面;lifecycle 死代码守卫提交前清理。
6. 实现期缺陷修复 3 处(引导对/校验视图漏键/seq 字段化;冒烟发现、提交前修复、零事后改档)。
7. LIVE 工作树先行修改如实登记(非本包所为;本包 LIVE 全程只读+零写入结构性成立)。
8. CI run ID 如实分列 NOT VERIFIED@执行侧(操作者 dispatch 面)。

## §五 参考与漂移维护策略

- 参考: REPORT §零.5/§零.6(DESIGN/上游 file:line 全量);P1 族先例=R019-D3(清单自豁免)/R022+R014-D3(fixture 唯一数据源+字面量)/R065(zip 定值双算)/R062(指定并入步 da288df)/R066(行号差异如实注记)。
- **漂移维护三要素**: ①fixture 唯一数据源=tests 内 `FIX_SNAP`+黄金输入集(L45-L110),零真实档零网络;②预期值全部硬编码字面量(L31-L41 黄金族+各负向期望消息);③fixture→断言映射表如下(行号=实现笔 0f2b48c 实读):

| 断言组 | fixture/输入 | 预期值字面量 | 测试位置 |
|---|---|---|---|
| 任务/假设/条件/事件 ID 族 | 黄金输入集(QUESTION L65/H1S L50/H2S L52/条件 C1/C2/判据/CA L41) | GOLDEN_TASK_ID/HP1/HP2/FC1/FC2/EVENT_INIT(L31-L36) | TestGoldenRegistration L112-L162 |
| digest 绑定 | FIX_SNAP(L45) | GOLDEN_DIGEST="36fdd08c3cd49f60"(L37) | TestGoldenRegistration+TestSnapshotBinding L406-L465 |
| DP 登记参数 echo | GOLDEN_PARAMS(L38) | {round_budget:5,weight_scale:[1,5],min_discriminating_per_pair:1} | TestGoldenRegistration |
| append-only 拒收 | 同输入重放/篡改档(round_budget→9) | status=rejected-duplicate/原档字节不变 | TestAppendOnly L163-L224 |
| DRAFT 负向 | 单假设/零假设/同语句/origin 违规各态 | ValueError 消息片段(≥2/互异/origin) | TestDraftNegative L225-L284 |
| 条件 schema 负向 | 算子/窗口/正整数/threshold_source 各态 | ValueError 消息片段 | TestConditionSchema L285-L333 |
| DP 禁回改 | API 签名+篡改档 | inspect 无参+校验拒 | TestDPNoRewrite L334-L360 |
| 判据覆盖 | 部分/零/成员不命中 | ValueError 消息(不足/未命中) | TestDiscriminatingCriteria L361-L405 |
| snapshot 篡改 | 篡改快照/篡改档/缺档/lying 声明值 | digest 不匹配/快照文件缺失/独立重算≠声明值 | TestSnapshotBinding L406-L465 |
| 生命周期 | 全链+四终态+跳态 | written/ARCHIVED/非法迁移/不一致 | TestLifecycle L466-L529 |
| 修订 | revise_hypothesis | 新 id+revision_of/revision_reason 必填 | TestRevision L530-L559 |
| ABSENT_REGISTRY | 非 registry 指标(合成名) | registry_status=ABSENT_REGISTRY 不拒收 | TestAbsentRegistry L560-L573 |
| 静态纯度 | 模块源码文本 | 无 data/daily 引用/无网络 import | TestStaticPurity L574-L595 |

行号漂移注记: 上表行号为实现笔 0f2b48c 版;后续演进以类名+用例名为锚,行号仅辅助(R066 口径)。

## §六 zip 定值登记(终笔唯一补记位)

**装配定值**(装配器 assemble_evidence.py,2026-11-07 终笔时点;证据包根 /tmp/p2-wp-a-evidence/):

- 包: `IA-P2-WP-A-EVIDENCE.zip`,**341705 字节 [实取·zip 文件大小]/未压缩合计 986670 字节 [实取·unzip -l 合计,113 files 含清单]**;
- 成员: **SHA256SUMS 清单 112 条 [实取·清单行数]**(staging 113 文件,清单自身显式豁免,R019-D3/R065 先例);根层恰 8 类目录+SHA256SUMS 零杂散 [实取·staging 根清点]: 01-startup-forensics/02-deliverables/03-negative-sensitivity/04-local-ci(含 logs/78 套件日志)/05-acceptance-anchors/06-live-isolation/07-git-forensics/08-selfreport;
- sha256: **`33a4ead14842fb3691542ae08264574d2c1a8f7ac4f218a6f2d1ef13793944a4` [实取·装配器 hashlib 与 shasum -a 256 独立复算双源一致]**;
- 完整性: `unzip -t` No errors detected [实取];SHA256SUMS 112 条解包逐条复算 **112 OK/0 BAD [实取·装配器 verify()]**;
- 双源副本交叉哈希: 02-deliverables 4 件(REPORT/DELIVERY/模块/测试)与仓库工作树逐字节等值 **4/4 EQUAL [实取·sha256 对照]**;其中模块 `8600ad36…` 与负向敏感性注入前后等值链同值(§二取证链闭合);
- 装配时点 TIP=报告笔 `8f856aa`(rev-parse=推送后 ls-remote 一致,§二 git 取证);zip 内 DELIVERY/自述副本=装配时点版,不含本 §六 定值行(R065 先例口径),终局自述以会话 stdout 四段为准;
- 如实登记: push 原始输出经会话 stdout 呈现(输出重定向落档通道被环境安全策略拒),07-git-forensics/push-output.txt 为推送后单支 ls-remote 复核+说明头(等价终态证据,非原始输出副本)。
