# IA-P3-WP-C DELIVERY — P3 收尾层第 3 实现包(预测复盘与错误模式统计)

> 包: IA-P3-WP-C(#35 挂靠;依赖列前件=WP-P3-A) · 分支: `dev/p3-impl-c` · 合同: IA-P3-WP-C-AC-v1.0
> 基线: BASE-P3C=`c14931c34f23dacc3439cc2609cf51a89d7ea60f`(origin/main 开工 ls-remote 实取全值一致)
> 本包无指定并入步(合同 §4;设计经祖先链在场,步骤4 双核验通过,REPORT §零.7)
> 本文=装配时点稿(zip 定值行以终笔提交与 stdout 四段为准,R065 先例口径);时区未注明者 UTC。

---

## §一 交付物(k=4 白名单,恰 C=4 纯新增)

| # | 文件 | 行数(实取) | sha256(实取@所属笔提交时点) |
|---|---|---|---|
| 1 | `scripts/prediction_review.py` | 642 | `bc1c4a543e7e7be9ea0330c1e3a3e61cc5ce0ef1046982588c0a70e2518ac7e1`(实现笔 cdd7dba 起,装配时点复核等值) |
| 2 | `tests/test_p3_wp_c.py` | 1306 | `a9effbcd493765face2f75a9fd1a8db4f8e9084dc27420af6039cf8046121d06`(同上) |
| 3 | `docs/P3_WP_C_REPORT.md` | 188(报告笔) | 终笔时点 `git show` 复核为准(本文档行数自指以 wc -l 实取为准) |
| 4 | `docs/P3_WP_C_DELIVERY.md` | 本文件 | 同上口径 |

提交链(纯线性,零 merge): 登记笔 ca56427 → 实现笔 cdd7dba → 报告笔 f3f3230 → 终笔(本笔)。
BASE-P3C 后恰 4 笔,每笔单父;`git log --merges c14931c..HEAD`=空(证据包 03 类)。

## §二 证据清单(证据包 `/tmp/p3-wp-c-evidence/IA-P3-WP-C-EVIDENCE.zip`,合同 AC-06 八类)

| 类目录 | 成员面 |
|---|---|
| 01-spec-registration/ | REPORT §零 全节副本(规格抄录 §零.1+登记清单 §零.2..§零.9,报告笔工作树版) |
| 02-dual-source-copies/ | 4 交付件×{git-show TIP 版+工作树版}+cross-hash-table.txt(DELIVERY TIP 版如实标注未入库@装配时点,R065 先例口径) |
| 03-git-forensics/ | ls-remote(推送前全分支集=BRANCH-SET §十一.1 57 支+dev/p3-impl-c 预推核验)/log/name-status(逐提交恰 A 行)/merges-check(空)/head-parents(单父)/base+design-fix1 祖先双核验/reflog/设计在场核验原始输出(DESIGN L182-186 逐字+设计三件 hash-object)/LIVE 三面(grep 零命中+real_data_acceptance sha256+LaunchAgents 清单) |
| 04-local-ci-mirror/ | CI 同款方法学镜像脚本+逐套件串行记录(85 行名称+退出码)+汇总结果(85=84 exit0+1 SKIP+0 非零;SKIP=身份锚 test_glm_live;基线 84 槽零回归+本包恰 +1) |
| 05-evidence-mapping/ | AC-02 五要点映射表副本(REPORT §二)+DP 登记节副本(REPORT §零.4/§零.5)+§5.3 数值标注扫描清单 |
| 06-run-artifacts/ | 零运行产物声明+锚定(find data/research -newer REPORT 空输出)/测试运行 stdout(115 OK)/模块 selfcheck/py_compile/黄金预计算件+输出/fixture 一致性件+输出(全 OK 含六面逐字节一致裁定)/负向敏感性三注入记录+sha256 基线终态等值对 |
| 07-selfreport-copy/ | stdout 四段自述装配时点稿(与终稿差异=恰 zip 整体定值行组,R065 先例口径) |
| (根) SHA256SUMS | 清单自身显式豁免(不塞入 zip 自身;置于 zip 旁 /tmp/p3-wp-c-evidence/ 下,合同 §3 步骤12 口径) |

zip 定值(文件数/字节数/sha256)以终笔提交信息与会话 stdout 为准(zip 内本副本不含该定值行,R065 先例口径)。

## §三 验收对照(合同 AC 逐条;详情见 REPORT §二/§六)

- AC-01 规格抄录: REPORT §零.1 DESIGN L182-186 逐字抄录+四要素齐备+C 行与 A/B/D/E/F 行可区分;冻结章注记 L181-185 偏差恰 1 行≤3 行容差 ✓
- AC-02 五要点: ①②③④本地面 PASS(实现面+测试面 file:line 映射,REPORT §二);⑤CI 面=工件入库+本地镜像 85=84+1SKIP+0 非零零回归,**run ID NOT VERIFIED@执行席**→操作者 CHECKPOINT dispatch `rounds/040/P3-WP-C-CI-dispatch-evidence.md`
- AC-03 全合成 fixture: 唯一数据源=文件内合成(18 预测+5 版本记录字面量,与独立首原理预计算件六面逐字节一致);预期值=黄金字面量 3 项(统计文档/警示清单/简报 sha256)+黄金计数/行面/basis 明细,独立预计算+测试内 hashlib 复算双源一致;映射表见 §五;AC-03.7 不适用(零 GLM 调用面,REPORT §零.8)
- AC-04 数值标注: REPORT §六 13 项+DELIVERY §二 计数逐项 [实取·来源] ✓;§5.3 六项扫描清单成件(证据包 05 类)
- AC-05 纯度: 零网络/零 GLM/零凭证/零付费(import AST 白名单 json/os/sys/datetime+ae/rri+剥 docstring 禁网令牌+只读 open+零直接写调用+零 data/daily+零默认 LIVE 路径);免责声明三处=模块 docstring+统计文档 note+简报尾行 ✓;上游对齐=复用调用禁复制分叉(ae 七面+rri 三面,REPORT §零.5 P-C-11)
- AC-06 git 纪律: 自 BASE-P3C 全值切出→纯线性 4 笔零 merge/amend/force;main 未触碰;LIVE/launchd 零触碰(证据包 03 类三面);零 tag;终局单支推送 no-force ✓
- AC-07 不构成投资建议: 模块 docstring+REVIEW_NOTE(统计文档 note)+简报尾行 ✓

## §四 参考与漂移维护策略(AC-03 生效;三要素)

1. **预期值唯一来源=版本化合成 fixture**: 全部断言预期值锚定 tests/test_p3_wp_c.py 内版本化定义(FX_PREDS L52-209+FX_VERSIONS L211-258+GOLDEN_DOC/WARNINGS/BRIEFING L279-332+三 sha256 字面量 L333-338),fixture 与断言同文件同 commit 演进;黄金值另经独立预计算件(/tmp/p3-wp-c/fixture_and_golden.py,零被测模块 import;证据包 06 类)固化第二源,双源不一致=fixture 一致性裁定器非零退出(三方裁定全 OK 实录)。
2. **fixture 演进同 commit 同步**: 新增/修改 fixture 须与受影响断言同一 commit(单一实现笔承载,拆分即红);预计算件与 GOLDEN 任一侧演进,须同 commit 重算对方并留三方一致裁定输出+六面逐字节一致裁定(证据包 06 类)。
3. **真实数据档永不入预期值来源**: data/daily 与 data/research 真实档结构性禁入(测试零真实档引用,AST 禁令牌+零默认路径常量;模块编排面 views_path/archive_dir 显式注入,无真实档默认读);ae/rri 上游行为变化(settlement 日历/mechanism 词表/版本链形)导致的漂移,以上游版本为权威修正 fixture 与黄金值(禁以被测模块输出口径反向固化预期值)。

## §五 fixture→断言映射表(断言组→fixture 定义 file:line)

| 断言组(测试类) | fixture 定义锚(tests/test_p3_wp_c.py) | 装配/消费面 |
|---|---|---|
| TestGoldenFirstPrinciples(黄金双源) | GOLDEN_DOC L279-310+GOLDEN_WARNINGS L312-316+GOLDEN_BRIEFING L318-331+sha 字面 L333-338 | hashlib 首原理复算对照(禁被测模块)+ae settlement/mechanism 锚定 |
| TestDPParamRegistration(登记锚定) | 模块常量+REPORT §零.4/§零.5 登记值字面 | registered_dp_values/registered_param_values/dp_selfcheck+monkeypatch 回改检出 6 面 |
| TestWindowBounds(窗口边界) | 无 fixture(纯日期函数) | P-C-04 月末日钳制/闭区间 |
| TestTerminalState(终态判定) | 内联最小 pred 字面 | P-C-02 词表+nyt 终态化+fail-loud |
| TestAnchorDate(锚定序) | FX_VERSIONS L211-258 | P-C-03 三源判定序+discrepancies+轻校验 |
| TestClassifyMiss(三轴规则) | FX_PREDS 成员+内联 D* 变体 | P-C-06 方向/期限/幅度/==/touch-high/settlement 回退/窗前排除/优先级 |
| TestClassifyRows(归类行) | FX_PREDS L52-209+FX_VERSIONS | 行 schema 13 键/输入序/单列类别/缺席轴 None |
| TestStatisticsGolden(统计黄金) | GOLDEN_DOC L279-310 | 全文档相等+dump sha+DP-6 分母+空/零分母变体 |
| TestHypothesisWarnings(警示游程) | FX_PREDS 变体(删元/改 status/合成 N*/U* 组) | P-C-09 末端游程≥3 边界+premise 不成组+哨兵不从调用方读 |
| TestRenderBriefing(简报渲染) | GOLDEN_BRIEFING L318-331+变体 | 纯文本黄金+免责尾行+N/A 分母+失配行消隐 |
| TestZeroWrite(只读零写入) | FX_VIEWS L260-261 落 tempfile 沙箱 | 字节级 sha256 前后等值+fixture 零突变+archive 零创建+repo config 套件级等值 |
| TestOrchestrator(编排面) | GOLDEN_ORCH_DOC/BRIEFING L341-347 | 空链黄金(discrepancies 消隐)+注入面等值+墙钟缺省+负向 4 面 |
| TestStaticPurity(AST 纯度) | 模块源码文件 | import 白名单/禁网/只读 open/零写调用/禁字符串/编译 |
| TestNegativeInputs(负向输入) | 内联非法形 | views/pred/version_records/as_of fail-loud |
| TestSelfcheckMain(__main__) | 模块 __main__ 入口 | subprocess 受控 1 处(退出码+哨兵行+免责) |

## §六 zip 定值(终笔登记)

(笔A 占位: 装配停点后由笔B 区内纯追加定值行组——文件数/字节数/sha256+复算与解包核验口径;R065/R067 先例口径)

## §七 如实偏差(全项登记;不声明「无偏差」)

> 本节仿 R067/R068 先例(WP-A/B DELIVERY 如实偏差专节)自笔A 起在场;内容与 REPORT §三 逐项对应。

1. **实现期缺陷修复 1 处**: `registered_param_values()` 期限桶镜像格式 `≥9周:9-+`→`≥9周:9+`(与 REPORT §零.5 P-C-07 登记字面量对齐;dp_selfcheck 首运行检出;登记定值本身未动);
2. **实现期口径修正 1 处**: `dump_statistics` 序列化——P-C-08 登记序列化式 `json.dumps(sort_keys=True)` 对 P-C-07 登记的 None 单列桶键抛 TypeError → `_canonical_order` 递归确定序(None 排首)后 sort_keys=False;str-only 文档产物与登记式逐字节等值(测试断言+fixture 一致性件双面);两登记定值同时保真,非回改;
3. **实现期口径补强 1 处**: 终态 miss 缺规范 deadline→ValueError fail-loud(P-C-06 未明列该输入形;窗口不可定界归类不可计算,fail-loud 优于 9999-12-31 假窗口;TestClassifyMiss.test_miss_without_deadline_fail_loud);
4. **测试 1 处 subprocess 受控用途**: TestSelfcheckMain(sys.executable+仓库内路径+timeout+capture;AST 禁 subprocess 面仅约束被测模块,模块 import 白名单零 subprocess);
5. **提交信息编号笔误**: 实现笔提交信息称「REPORT §零.10 实现期登记」,本 REPORT 实为 §零.9(内容指向无误;已提交信息不回改,如实登记于 REPORT §零.9/§三);
6. **REPORT §零.1 行号偏差承接**: 冻结章 §十一 注记 C 行 L181-185 vs 基线实读 L182-186,偏差恰 1 行≤3 行容差(AC-01 满足;开工已登记非本轮新增);
7. **CI 面 NOT VERIFIED@执行席**: AC-02⑤ CI run ID 不可见@执行席(禁 dispatch),本地镜像 85=84+1SKIP+0 非零为执行席证据面,CI 面留操作者 rounds/040 dispatch;
8. **其余无偏差声明不作出**: 以上为全量已登记偏差;DP-5/DP-6/P-C-01..P-C-16 登记定值运行后零回改(REPORT §四 自检表)。
