# IA-P1-WP-CLOSE 交付说明(DELIVERY)

- 工作包: IA-P1-WP-CLOSE(#21 / 终名 WP-P1-CLOSE;P1 收口链终包)
- 分支: `dev/p1-close`(自 BASE-P1CLOSE 切出;冻结章登记名)
- BASE-P1CLOSE: `5e6ddcd3691a3d52a41472ef63793cb317e1d508`
- 角色: 执行Agent(开发席;判定权=独立审计 P1 终裁轮+用户卡点,本文件不自行宣布 PASS)
- 版本: v1.0(笔 3 装配时点版;§六 zip 定值=笔 4 终笔回填)

## §一 改动(k=4 白名单纯新增;提交序+模块面分解)

**提交序(纯线性,零 merge 零 amend 零 force;最终 SHA 以终笔后 `git rev-parse` 为准)**:

| 笔 | 提交 | 内容 |
|---|---|---|
| 1 规格笔 | `7cd8d68` | REPORT §零 开工登记(四要素逐字+白名单 4 件+DP-C1~C5+LINEAGE-TABLE 八行透传+P1_DESIGN 实读+开工核验 17 项+运行产物边界) |
| 2 实现笔 | `9d920fc` | scripts/p1_acceptance_check.py(307 行)+tests/test_p1_close.py(388 行,14 用例/7 类)纯新增 |
| 3 报告笔 | (本笔) | REPORT §一-§六 回填(谱系核对表机器输出原文+对照表+遗留承接+封版前置+证据映射+数值自检)+本 DELIVERY §一-§五+漂移维护专节+映射表 |
| 4 终笔 | (笔 3 后) | 本 DELIVERY §六 证据包 zip 定值登记(成员数/字节/sha256;装配时点 TIP=笔 3) |

**模块面分解(白名单 A 类 k=4;M=0/D=0 沿冻结章 §四;BASE..HEAD diff 证据包 03/07)**:

| 文件 | 行数(工作树实取@笔 3) | 面 |
|---|---|---|
| scripts/p1_acceptance_check.py | 307 | 验收核对脚本(冻结定值内嵌+在场核验+LINEAGE 逐行复演+引擎列透传) |
| tests/test_p1_close.py | 388 | 测试(合成 git 仓库 fixture 唯一数据源;14 用例/7 类) |
| docs/P1_CLOSE_REPORT.md | 287(§零=113@笔 1) | 终验报告(§零-§六) |
| docs/P1_CLOSE_DELIVERY.md | 本文件 | 交付说明(五节+漂移专节+§六 zip 定值) |

## §二 证据指针

| 证据 | 位置(证据包 /tmp/p1-close-evidence/IA-P1-WP-CLOSE-EVIDENCE.zip 内路径;zip 定值=§六) |
|---|---|
| 本地 CI 逐套件记录(78 槽=77 exit0+1 SKIPPED+0 fail;BASE 77+新增 1 零回归) | 04-local-ci/per-suite-records.txt+summary.txt+suite-logs/ |
| 验收核对脚本真实运行原始输出(两次均如实留痕: run1 2026-11-06T20:08:42Z rc 未同步捕获/run2 20:09:38Z exit=0;stdout 除 run_utc 横幅行外逐字节等值) | 06-acceptance-run/run-stdout.txt+run2-stdout.txt+run2-stderr.txt+exit-code.txt |
| 真实运行结论 | RESULT: ALL GREEN(rows=8, fail=0);SUMMARY rows=8 checked=8 row_pass=8 pass_checks=25 fail_checks=0;退出码 0 |
| 零运行产物[data 面]声明+data/daily 27 文件前后 sha256 等值 | 06-acceptance-run/zero-data-artifact-declaration.txt+data-daily-sha256-before/after.txt |
| git 取证(name-status/rev-parse/log/reflog/ls-remote 前后/tag -l 前后/BRANCH-SET 50 条目 diff/在场核验/注入负向) | 03-git-forensics/(终笔后终态取证补入) |
| 负向敏感性注入(3 真实注入→红 failures=6/1/9→恢复绿;前后 sha256 等值 5471847a…) | 03-git-forensics/14-injection-negative-tests.txt+script-sha-before-injections.txt |
| LIVE 隔离(grep `R066\|P1-CLOSE\|IA-P1-WP-CLOSE` 零命中+real_data_acceptance.py sha256=f9ca189c… 不变+LaunchAgents plist 哈希前后不变) | 03-git-forensics/13-live-* |
| 逐要点证据映射表+DP 登记节 | 05-mapping/(REPORT §五 副本)+数值自检清单 |
| 交付文件双源副本(git show 尖端版+工作树版,交叉哈希) | 02-deliverables/ |
| 规格承接登记件+白名单副本+LINEAGE-TABLE 冻结章透传副本 | 01-spec/ |
| 自述报告副本(zip 外文件系统+会话 stdout 承载口径;R064/R065 先例同构,自述不作通过依据) | /tmp/p1-close-evidence/result.md(zip 外)+07-selfreport/承载声明 |
| CI dispatch 登记件 | `rounds/066/P1-WP-CLOSE-CI-dispatch-evidence.md`(操作者 CHECKPOINT 段落落档;执行席不 dispatch,仅引用将落路径) |

## §三 逐 AC 自评(C-AC-01~C-AC-07;执行段自评,终判=独立审计 P1 终裁轮)

| AC | 自评 | 一句证据指引 |
|---|---|---|
| C-AC-01 规格承接与登记正确性 | PASS(执行段) | REPORT §零.1 四要素逐字+§零.2 白名单 4 件+§零.5 P1_DESIGN 行号登记(表头 L165/A..G L169-175/红线 L177+L179-184/§八.1 L192-223/§八.2 L225-256;#21 恰 3 处=L190/L200/L234 全衔接注记=预期形态,未触发(d)) |
| C-AC-02 谱系核对表机器验证 | PASS(执行段;引擎列终判=终裁轮复演) | 判据 1 无漏行 8/8 编号对应;判据 2 git 列全绿(ancestor exit0×8+tip ls-remote 实取全值一致+在场核验②~⑥入表);判据 3 引擎列逐字透传+来源注记(测试 L262 断言);判据 4 失败处置=测试双态覆盖+真实运行零失败;判据 5 DP-C1 笔 1 先登记→笔 2 实现→运行后零回改(提交序可证)。证据: REPORT §一+06-acceptance-run/ |
| C-AC-03 测试与确定性验证 | PASS | 零网络零新依赖;预期值字面量硬编码(L35-L44: DRIFT_TIP/FORBIDDEN_MERGE/WRONG_BLOB/MISSING_BRANCH/FIXTURE_CI/FIXTURE_AUDIT/ENGINE_NOTE/FROZEN_BASE);合成 fixture 唯一源(build_fixture L110-L164)+域分离反证(L361);双态覆盖(ancestor 通过/失败+tip 一致/漂移+FAIL 行/非零退出);本地 78 槽全绿;漂移策略专节+fixture→预期值映射表=本文件下两节;AC-03.7 外部调用面合成桩=不适用(白名单无调用面类文件,纯 git 本地取证即证) |
| C-AC-04 引用真实性与注入边界 | PASS | REPORT/DELIVERY 文件:行号 引用逐条可寻(§零.5/§二.1 表+映射表);LINEAGE-TABLE 全值=冻结章透传零转写(一处工作文件笔误由机械 diff 当场捕获,见 §四.3);跨支引用=ls-remote 实取;否定性声明可反证(03-git-forensics) |
| C-AC-05 范围/分支/生产隔离 | PASS | diff=4 A 行/M=0/D=0(03/07);纯线性零 merge;BRANCH-SET 50→51 唯一新增 dev/p1-close;tag -l 前后不变;零应用层网络(import 面纯标准库);LIVE 零写入(13-live-*);上游在场件+设计三件零改动(blob 对照) |
| C-AC-06 CI 与证据包交付 | 部分: 本地面 PASS/CI 面 NOT VERIFIED(操作者保留) | 本地 78=77+1 恰合预期;证据包八类+SHA256SUMS(清单自身显式豁免,R019-D3 措辞)已装配(§六 定值);DELIVERY 五节齐备+专节;CI dispatch+登记件=操作者 CHECKPOINT 面,执行席不 dispatch(合同 §三.5 明文),终判待 rounds/066 落档 |
| C-AC-07 研究纪律与使用边界 | PASS | 封版四步链全 PENDING 零自决(REPORT §四);DP-C5 PENDING 零预激活零预创建;缺值如实缺席零造数;文案零投资建议;零真实调用/凭证/付费;LIVE=用户卡点③ PENDING 零涉及;研究状态档零触碰;W4/W5 不入链;DEFERRED 只登记不修复(REPORT §三 9 条) |

## §四 如实偏差登记(时间戳 UTC;零编造,阻断面如实标 U)

1. **笔 2 提交信息数值标注错误**(2026-11-06 实现笔): 提交信息写「tests/test_p1_close.py(872 行级 14 用例…)」——「872 行」系自 R065 测试文件行数误植,**实际 388 行**。处置: 零 amend(纯线性纪律+REPORT §零.6 已登记 9d920fc 全值,改写将破坏登记链);以本节+REPORT §六 实值(307/388/113)为准。
2. **run1 退出码未同步捕获**(2026-11-06T20:08:42Z 真实运行): 沙箱禁 `echo $?`,首跑退出码未留痕。处置: capture_exit_code.py 以同命令补跑 run2(20:09:38Z)=exit 0,stdout 对照除 run_utc 横幅行外逐字节等值;两次运行均如实留痕入证据包(非隐匿重跑;脚本纯只读,重跑无副作用)。
3. **BRANCH-SET 预期文件一处笔误**(2026-11-06 证据装配): 04a 预期文件将 dev/p1-gap08 分支尖端 `…90be9ed53…` 误写 `…90be9d53…`(漏一字符 e);机械 diff 当场捕获,修正后重跑=50/50 零差异。R061 转录教训防线有效性的直接例证;误值未入包。
4. **zip 内 DELIVERY 副本=笔 3 版**: 不含笔 4 §六 zip 定值行(R065 先例口径;§六 内自登记,终局自述以会话 stdout 四段为准)。
5. **run2-stderr.txt=0 字节**: 真实运行 stderr 无输出,如实留空文件非缺件。
6. **tests/test_p1_close.py 头注释行号漂移**: 文件头注释(L19)标注伪值字面量「L60-L64」,实际 DRIFT_TIP/FORBIDDEN_MERGE/WRONG_BLOB 位于 L35/L36/L37(开发中文件头部增删所致);零功能影响,正确行号=本文件映射表所载实值。

## §五 参考

- 合同: IA-P1-WP-CLOSE-AC-v1.0(冻结版;冻结章五实值+BRANCH-SET 50+LINEAGE-TABLE 八行+M=0+k=4;附录A 内嵌,contracts/ 存档=操作者面)
- 设计: docs/P1_DESIGN.md §六(L165-184)/§八(L192-256)
- 上游交付面: docs/P1_WP_A..G_REPORT.md/GAP08 报告/P1_DELIVERY.md(工作树在场,本包零改动)
- 先例与学习点: R022 AC-03.6 漂移三要素;R014-D3 合成 fixture 唯一源;R061 转录教训(机械 diff);R065 zip 装配+§六 终笔定值先例;R019-D3 SHA256SUMS 清单自身豁免措辞;R017-D2 CI 登记件字面值;R064/R065 自述 zip 外承载口径(R065 audit DEFERRED-1 校准承接)
- CI: .github/workflows/offline-tests.yml L34-L57(逐文件独立子进程;test_glm_live SKIPPED)
- CI dispatch 登记件(操作者): rounds/066/P1-WP-CLOSE-CI-dispatch-evidence.md

## §六 证据包 zip 定值登记(终笔回填;装配时点 TIP=笔 3)

- 路径: `/tmp/p1-close-evidence/IA-P1-WP-CLOSE-EVIDENCE.zip`
- 装配时点 TIP=笔 3=`6a3c2032ef358c3b79436191bcca0317d6183eb4`(rev-parse=ls-remote 实取一致)
- 成员数: **137 files**=136 成员+SHA256SUMS(清单自身显式豁免不入自身校验和,R019-D3 措辞;R065 先例)
- 字节: **331005**(未压缩 918809)
- zip 整体 sha256: **`8ab0de3258ce414107f0103a4e00a7451dcd2df35a9318555de2b3031d0401e0`**(装配 stdout 与 shasum 独立复算一致)
- 验证记录: `unzip -t`=No errors detected;SHA256SUMS 136 条解包逐条复算=136 OK/0 BAD;根层零杂散(恰 9 类目录=01-spec/02-deliverables/03-git-forensics/04-local-ci/05-mapping/06-acceptance-run/07-selfreport/08-sha256sums/09-helpers);02 双源副本交叉哈希 4/4 equal(git show TIP 版 vs 工作树版)
- 披露(R065 先例口径): zip 内本文副本=笔 3 装配时点版,**不含本节定值行**(终笔=本笔);终局自述以会话 stdout 四段为准。

## 漂移维护策略专节(AC-03.6 三要素;沿 R022)

1. **预期值唯一来源=仓库内版本化合成 fixture**: tests/test_p1_close.py 于临时目录构造合成 git 仓库谱系(`git init -b main`+固定身份/日期的合成提交/分支/merge --no-ff/tag,零真实档零 origin 零网络;build_fixture L110-L164+_green_table L167-L190),一切 git 列预期值由 fixture 拓扑推导或字面量硬编码,不随真实仓库演进漂移;LINEAGE-TABLE 相关预期值=FROZEN_LINEAGE 字面量镜像(L45-L70,冻结章透传,禁从 scripts 模块导入计算=禁自证恒真)。
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: fixture 拓扑(提交/分支/tag 结构)与断言字面量(DRIFT_TIP/FORBIDDEN_MERGE/WRONG_BLOB/CI 串/冻结八行表)必须在同一提交内同步变更,禁分笔错位(审计可对单提交 diff 双侧对照)。
3. **真实仓库/真实档永不进入测试预期值来源**: 测试零引用真实 SHA/真实分支名/真实 data 面;域分离由 TestRealFixtureSeparation.test_real_table_against_fixture_must_fail(L361)反向证明——真实冻结表跑在合成仓库上必全红,两域零互染。真实谱系核对仅经 scripts/p1_acceptance_check.py 真实运行步(§二/REPORT §一),与测试步严格分离。

## fixture→预期值映射表(逐断言组可追溯;tests/test_p1_close.py)

| 断言组(测试) | 行号 | 预期值 | fixture 定义处(file:line) |
|---|---|---|---|
| TestFrozenTableFidelity 内嵌表==冻结字面量 | L232 | FROZEN_LINEAGE 八行镜像 | L45-L70(字面量;冻结章透传,非 fixture 推导) |
| TestFixtureAllGreen 全绿两态 | L246 | rc=0+`RESULT: ALL GREEN(rows=3, fail=0)`+`rows=3 checked=3 row_pass=3`+①SKIPPED 行 | build_fixture L110-L164(c0 tag p03fx L126/merge m1 L143/m2 L154/c3=HEAD L158)+_green_table 三行表 L167-L190 |
| 引擎列逐字透传+来源注记×3 | L262 | `99999999999 success 70槽=69exit0+1SKIP`+注记原文 | FIXTURE_CI_LITERAL L39(硬编码)+_green_table 引擎列 L182/L185/L188 |
| TestAncestorFailState 未并入侧支 | L273 | row_fail=1+行 FAIL 前缀 | 侧支 dev/fx-side 自 c1 分出 s1 未并入 L130-L135 |
| TestAncestorFailState 伪 SHA | L284 | FAIL+非零退出 | 40 位非对象字面量(测试内联) |
| TestTipStates tip 漂移 | L298 | FAIL(全零 SHA 失配) | DRIFT_TIP L35(40×'0' 硬编码) |
| TestTipStates 分支缺席 | L308 | FAIL(`<缺席>`如实) | MISSING_BRANCH L38 |
| TestPresenceFailStates ②祖先不可达 | L321 | FAIL | 期望尖端=侧支 s1(未并入)L130-L135 |
| TestPresenceFailStates ⑥tag 锚侧支 | L330 | FAIL | side-tag-20981231 锚未并入 s1 L135 |
| TestPresenceFailStates ⑤blob 失配 | L338 | FAIL | WRONG_BLOB L37(40×'f') |
| TestPresenceFailStates ⑦禁锚前缀 | L347 | FAIL | FORBIDDEN_MERGE L36(c9626633+32×'0') |
| TestRealFixtureSeparation 域分离 | L361 | 真实表×fixture 必 FAIL | FROZEN_LINEAGE L45(真实冻结值)×合成仓库(build_fixture) |
| TestUsageErrors 非法 tip-source | L372 | exit=2 | argparse 契约(无 fixture) |
| TestUsageErrors 坏表文件 | L378 | exit=2 | JSON 解析失败路径(无 fixture) |

(笔 3 完;终笔=§六 zip 定值登记。)
