# IA-P1-WP-F DELIVERY(跨经济体比较视图 #19)

> 分支 `dev/p1-impl-f`(自 BASE-P1F=`64ce40c25409bdb0a3d9fecc4c5f0f5df74dd902` 切出+指定并入步 merge `dev/p1-design-comp@7190eb7aae110dcc23cf059b4969cd9978429d4d` 恰 1 个[第二父=7190eb7]+其后纯线性)。规格源=`docs/P1_DESIGN.md`(blob=`10e026c08ce2828908ff7a5421aee8aba1f4e6d0`=design-comp 侧)§六 L174+§八.1 L192-L223。定值登记=`docs/P1_WP_F_REPORT.md` §零.5/§零.6。

## ① 改动

- **白名单 A 类 k=4 纯新增**(REPORT §零.3 登记,git ls-files 零重合): `scripts/economy_comparison_view.py`(278 行)/`tests/test_p1_wp_f.py`(432 行,20 用例[原 19+CI-红-F1 守卫 1])/`docs/P1_WP_F_REPORT.md`/`docs/P1_WP_F_DELIVERY.md`(本文);M=0(v1.1 冻结维持,开工实读 §八.1=纯消费面新文件可实现,未触发(d));
- **提交序**(纯线性,零 amend 零 force): da288df(指定并入步,豁免行=M docs/P1_DESIGN.md+A P1_DESIGN_COMP_REPORT.md+A P1_DESIGN_COMP_DELIVERY.md=R064 已审内容,§五.1 豁免行单列不计本包 M/A)→829e13a 规格笔(REPORT §零 登记)→f4769cf 实现笔(模块+测试)→报告笔(REPORT §一-§四+本文)→终笔(zip 哈希定值)→**整改笔(CI-红-F1: tests fixture 写档名对齐上游大写约定+守卫用例+REPORT §五/本文续作登记;模块零改动)+整改终笔(本文 §八 zip 重装配定值)**——整改续段=操作者 2026-11-07 0:5x HKT 处置段授权,自 1220ab6 续笔纯线性零新 merge;
- **整改续段修复面**: 仅 `tests/test_p1_wp_f.py`(fixture 写档名 `econ.lower()`→`econ`[对齐上游大写约定三方实证: macro_scorecard L487-L488 写档/data_assembler L288-L289 读档/test_p1_wp_c L172-L173 契约]+文末守卫类 TestRemediationFixtureNameCaseExact L403-L428);`scripts/economy_comparison_view.py` 零改动(sha256=`fb8aa49c…` 前后等值);期望零弱化(test_nonus_rows 期望「数据不足」原样,规格 §八.1 L213-L214+L217 支持现期望;根因=fixture 命名滑笔非模块语义,REPORT §五.2/§五.3);
- **零运行产物**: 要点①②③④⑤=【测试】×2+【测试/CI】+【纪律】+【PENDING】,零【真实运行】标记(REPORT §三 对照);`data/daily/` 与既有快照零触碰,`data/research/` 零写入(测试全在 tempfile,CLI 冒烟输出 /tmp);
- **上游交付件零改动**(对齐=复用调用: rp.select_snapshot/data_assembler.economy_scorecard/correlation_calculator.compute_all+PAIRS/macro_scorecard 四常量与 fact_of/research_history_query.query_window,import 面零复制分叉)。

## ② 证据指针

- 证据包: `/tmp/p1-wp-f-evidence/IA-P1-WP-F-EVIDENCE.zip`(八类成员+SHA256SUMS 清单自身显式豁免;整体 sha256 见 §六;**整改续段重装配后定值=§八**);
- **整改续段证据**(zip 09-remediation/ 续作成员,原 35 成员原样保留不洗不删): 01-rootcause-diagnosis(根因诊断+墙钟假设证伪)/02-guard-negative-proof(守卫负向: 回植滑笔本机即红)/03-testsuite-postfix(20 用例全绿)/04-local-ci-records-remediation(修复后 76 套件=75 exit0+1 SKIPPED,stdout 同目录)/05-negative-sensitivity-remediation(三注入复验 3/3 红零弱化)/06-cli-smoke-remediation(exit=0)/07-forensics-remediation(git 取证)/08-self-report-remediation(整改段自述副本);
- 本地 CI: 逐套件记录=证据包④(`/tmp/p1-wp-f-evidence/local_ci_records.txt`,76 行)——**76 套件=75 exit0+1 SKIPPED**(BASE-P1F-CI-SUITES=75+新增 tests 1=76,零回归);整改续段复跑同值(09-remediation/04);驱动器=`/tmp/p1-wp-f-evidence/run_local_ci.py`(与 .github/workflows/offline-tests.yml 同构: 逐套件独立进程,test_glm_live SKIPPED);
- 负向敏感度: 三缺陷注入三红记录(直读采集档→2 红/缺席填 0→1 红/DP-F3 第三对→补常量断言后红;第三对初注入未红的缺口发现与闭合如实登记于 REPORT §二 要点④行);**整改续段修复后代码复验 3/3 红(09-remediation/05,零弱化)**;
- git 取证: 证据包③(name-status/rev-parse/log/reflog/ls-remote+设计在场核验输出)+09-remediation/07(整改笔续作取证);
- CI dispatch: 操作者 CHECKPOINT 面(登记件落 `rounds/062/P1-WP-F-CI-dispatch-evidence.md`,执行席不自行 dispatch);
- LIVE 隔离: LIVE 目录本轮标记 grep(`R062|P1-WP-F|IA-P1-WP-F`)零命中+`real_data_acceptance.py` SHA256 不变(证据包③)。

## ③ 逐 AC 自评(自评仅供参考,判定权=Agent 4 审计)

- **AC-01 规格抄录**: PASS——REPORT §零.2 逐字抄录(§六 L174+§八.1 L192-L223 四要素+DP 节),行号=并入后工作树实读与冻结章登记一致;清单推导逐条附依据;k=4 零重合+必含件齐;
- **AC-02 要点映射**: PASS——五要点+目标/范围四面映射表零漏检(REPORT §二);落点 file:line 实取;参数登记制=登记(829e13a)先于实现(f4769cf)先于运行,登记/常量/断言三者一致(tests L280-L294);零真实运行面→要点④⑤纪律面/PENDING 面如实;
- **AC-03 测试与确定性**: PASS——19 用例全绿;零网络零新依赖零 requirements 改动;预期值字面量硬编码(含 corr=±1 手算构造序列);合成 fixture 唯一数据源(零读真实 data/daily/);要点可离线功能点全覆盖;漂移维护策略专节见下;AC-03.7 不适用(无外部调用面实现,判定依据=import 面 L24-L37);
- **AC-04 引用真实性**: PASS——REPORT/本文 一切 file:line 引用工作树实取复核(两处 import 面行号按实值修正 L25-L38→L24-L37,≤3 容差内主动更正);注入摘要均标注「注入摘要,非工作树实读」/「[注入·冻结章]」;跨支引用=ls-remote 实取全值;
- **AC-05 范围/分支/生产隔离**: PASS——BASE-P1F..HEAD diff=豁免行 3 行(并入步,R064 已审)+A 行恰 k=4+D=0+豁免行外 M=0;分支历史=BASE 切出+恰 1 merge(指定并入步)+纯线性;reflog 零 reset/amend;BRANCH-SET 既有 48 支尖端不变+唯一新增 dev/p1-impl-f;零网络(源码静态扫描);上游件/主流水线/workflow 零改动;LIVE 零写入零 launchd;研究档案不 commit;.gitignore 不改;
- **AC-06 CI 与证据包**: 自评 PASS 待操作者 CI dispatch——本地全绿 76 套件;证据包八类成员齐+SHA256SUMS;本文五节+漂移专节;自述四段;CI dispatch=操作者 CHECKPOINT 面(非执行席动作,如实登记);
- **AC-07 研究纪律**: PASS——特有纪律 7 条登记并遵守(REPORT §零.4);缺值不填 0(五态缺席语义);DISCLAIMER 沿用+不构成投资建议文案;零真实 GLM/网络/凭证/付费;研究状态档零触及(只读消费面);W4/W5 零引用;白名单外需求零实施(实现期零接口缺口发现)。

## ④ 如实偏差与登记

1. **CI dispatch 非执行席动作**: 合同 §六.1 dispatch=操作者 CHECKPOINT 面,执行席不自 dispatch(合同明文),本地同构 CI 已全绿代偿,终局 CI Run 以操作者登记件为准;
2. **负向敏感度第三注入初未红**: DP-F3 第三对注入初版未触发(数据面静默滤除——fixture 无 SPX/SHCOMP 序列)→判定为参数一致性断言缺口→补 test_registered_parameters_frozen(常量面)→再注入即红;缺口发现与闭合如实登记,非静默;
3. **zip 内副本=装配时点版**: §六 zip 定值行不在 zip 内 DELIVERY 副本中(R064 384dedd 先例口径,DISCLOSED);终局自述以会话 stdout 四段为准;
4. **行号引用两处主动更正**: REPORT 初稿 import 面行号 L25-L38/L60-L64→实值 L24-L37/L36-L37(≤3 容差内,既发现即按 §5.3 第 4 项更正,R014/R030 教训承接);
5. **本地环境差异预声明**: 本地=macOS/Python 3.x 执行,CI=ubuntu-latest/Python 3.11+依赖安装面(workflow 明文);本地驱动器与 CI 同构(逐套件独立进程),如环境差导致 CI 与本地分歧→情形(b)如实分流;
6. **非偏差登记**: 指定并入步引入三行=§五.1 豁免行(R064 已审,非本包 M/A 违例);`data_assembler._st_names` 为函数内局部量不可 import→同值常量逐字登记(REPORT §零.6 判定依据),非复制分叉(3 个显示字面量,锚=data_assembler L286-L287 实读);
7. **CI-红-F1(整改续段,原红登记不洗不删)**: 分支 CI run **42256314191=failure**@1220ab6,76 槽=74 exit0+1 红+1 SKIP,唯一红=test_p1_wp_f `test_nonus_rows_data_insufficient_not_zero`(期望非 US 行「数据不足」实得「未生成」)。根因(诊断先于修复,REPORT §五.2)=**fixture 写档名 `econ.lower()` 小写滑笔偏离上游大写约定**——macOS 大小写不敏感卷隐藏错位,ubuntu-latest(大小写敏感)精确名 open 失败→非 US 行误分类「未生成」;墙钟/时区假设证伪(定位链零时钟)。修复=fixture 命名对齐+守卫用例(期望零弱化,规格 §八.1 L213-L214/L217 论证见 REPORT §五.3);复验=20 用例全绿+76 套件 75 exit0+1 SKIP+三注入 3/3 红+CLI 冒烟 exit0(REPORT §五.4)。④.5 环境差异预声明面就此实化闭合(实例=文件系统大小写敏感度差异,非版本/依赖漂移);
8. **zip 重装配披露(整改续段)**: 证据包 zip 重装配(原 35 成员原样保留+09-remediation/ 续作成员+SHA256SUMS 重生成),原 §七 定值(d00ffbcb…/35 成员)永久留痕不删;新定值=§八;zip 内本文副本=重装配时点版不含 §八 定值行(R064 384dedd+本包终笔 DISCLOSED 口径同沿)。

## ⑤ 参考

- 规格: `docs/P1_DESIGN.md` §六 L174+§八.1 L192-L223(blob 10e026c0,=dev/p1-design-comp@7190eb7 侧);
- 合同: IA-P1-WP-F-AC-v1.1 冻结版(附录A 内嵌,contracts/IA-P1-WP-F-AC-v1.1.md 存档);
- 上游同源: 各包工作树在场 REPORT §零 登记清单(docs/P1_WP_A..E_REPORT.md、docs/P1_GAP08_*.md 等,本包零修改);
- 定值与映射: `docs/P1_WP_F_REPORT.md` §零.5/§零.6/§一/§二/§四。

## ⑥ 漂移维护策略(AC-03 生效专节;沿 R022 AC-03.6 三要素)

1. **预期值唯一来源=仓库内版本化合成 fixture**: tests/test_p1_wp_f.py fixture 工厂(L35-L113: YMD/POISON/_us_scorecard L43/_nonus_scorecard L48/_snapshot_facts L55/_series_store L70/make_fixture L86-L113,写档名=上游大写约定 L96-L99)=全部断言组唯一数据源,与真实数据档零耦合;
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: 任何 fixture 值改动→受影响断言组期望字面量必须同 commit 更新(审查面=diff 内 fixture 与期望值同窗出现);
3. **真实数据档永不进入测试预期值来源**: 测试零读 `data/daily/`(全部 tempfile 临时目录),零网络,零 GLM;若有未来用例需真实档→另行报批,不入本套件。

**fixture→预期值映射**(逐断言组可追溯):

| 断言组 | fixture 定义处 | 预期值形态 |
|---|---|---|
| 要点① 双变体等值+毒丸 | make_fixture L86-L110(with_collectors 开关+L102-L109 毒丸档) | 等值性断言+POISON 字面量 L36 零出现 |
| 要点② 评分卡行 | _us_scorecard L43-L46(int 总分 2/3)/_nonus_scorecard L48-L53(None/数据不足不可判)/make_fixture EA 缺席开关 | 单元格字面量('+2'/'数据不足'/'未生成(当日评分卡不存在)'/'本期在场;已确认/数据不足') |
| 要点② 关键事实 | _snapshot_facts L55-L68(八 metric 值+观测日;CPI derived.m12.pct_change=2.6) | 接地字面量('3.75%(DFEDTARL@2098-12-20)'等八组,'+2.60%(CPI@2098-12-15)') |
| 要点② 缺席变体 | make_fixture(with_ea_facts=False) | '无数据(快照无ECB_DFR有效事实)'等+available=False |
| 要点③ 只读锚定 | make_fixture 全档 | sha256 前后等值(非字面量,完整性断言) |
| 范围2 跨域对 | _series_store L70-L84(收益率手工构造: NIKKEI[0.10,0.05,-0.02]×USDJPY 2×→+1;DAX[0.02,-0.01,0.015]×EURUSD -1×→-1) | n_20d=3/窗口 2099-01-03~2099-01-05/corr±1(delta=1e-9)字面量 |
| 范围2 缺席变体 | with_eurusd=False/with_snapshot=False 开关 | 序列缺失/快照缺席披露语 |
| 范围3 查询 | _payloads L359-L369(静态方法内合成序列) | 窗口值[2.0,3.0,4.0]/[11.0,12.0]+n_window 3/2+不命中语义锚 |
| 参数冻结 | REPORT §零.5/§零.6 登记表 | 常量逐字断言(经济体集/八映射/两元组) |
| CI-红-F1 守卫(整改笔) | make_fixture L86-L113(档名大写约定 L96-L99) | exact-basename 等值断言(模块请求名逐字符在场+小写变体零在场;=大小写敏感 FS 语义,任何开发机文件系统上可复现) |

## §七 zip 定值登记(终笔)

- 证据包: `/tmp/p1-wp-f-evidence/IA-P1-WP-F-EVIDENCE.zip`
- 成员: 35 件+SHA256SUMS(=zip 内 36 files;八类最低集齐+08-tools 装配工具件)
- 字节: 108477(未压缩 234791)
- **zip 整体 sha256=`d00ffbcb3435ad7ca8612ee10c1e11c25edc8c2fea5ae3f6c5f116ded8016862`**(装配脚本 stdout 与 shasum -a 256 独立复算一致;testzip=OK;SHA256SUMS 36 行清单自身显式豁免不入 zip 自身校验和,R019/R023/R060/R064 先例)
- 装配时点 TIP=826579a(报告笔);zip 内本文副本=装配时点版,不含本节定值行(R064 384dedd DISCLOSED 口径);终局自述以会话 stdout 四段为准。

## §八 整改续段 zip 重装配定值(CI-红-F1;定值行由整改终笔登记)

- 重装配时点=整改笔尖端(自 1220ab6 续笔);原 §七 定值(sha256=`d00ffbcb…`/35 成员+SHA256SUMS=36 files)永久留痕不删,重装配=原 36 files 原样保留+`09-remediation/` 续作成员(01-08,见 ② 证据指针)+SHA256SUMS 重生成(覆盖全部成员,清单自身显式豁免不入自身校验和,R019-D3/R023/R060/R064 先例);
- zip 整体 sha256=【待整改终笔定值登记】;zip 内本文副本=重装配时点版,不含本节定值行(DISCLOSED 口径沿 §七);终局自述以会话 stdout 四段为准。
