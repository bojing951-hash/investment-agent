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
