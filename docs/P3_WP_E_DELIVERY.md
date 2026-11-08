# IA-P3-WP-E DELIVERY — P3 收尾层第 5 实现包(个人流程整合接口)

> 包: IA-P3-WP-E(#37 挂靠;依赖列前件=WP-P3-D) · 分支: `dev/p3-impl-e` · 合同: IA-P3-WP-E-AC-v1.0
> 基线: BASE-P3E=`91612378d2f095530e1f29faa48d53e959d5fe13`(origin/main 开工 ls-remote 实取全值一致)
> 本包无指定并入步(合同 §4;设计经祖先链在场,步骤4 双核验通过,REPORT §零.7)
> 本文=装配时点稿(zip 定值行以终笔提交与 stdout 四段为准,R065/WP-C/WP-D 先例口径);时区未注明者 UTC。

---

## §一 交付物(k=4 白名单,恰 A=4 纯新增)

| # | 文件 | 行数(实取) | sha256(实取@所属笔提交时点) |
|---|---|---|---|
| 1 | `scripts/personal_flow_integration.py` | 721 | `7985308c995cc5ea94a3dafdcccb0997003a67a8b1472e5e2b2f7c87d3359096`(实现笔 04e30fc 起,后续笔零改动;负向敏感性三注入还原后等值复验) |
| 2 | `tests/test_p3_wp_e.py` | 1301(测试补齐笔 1b50fc3 终态;129 用例 18 类) | `6b4a8c77681d6bf23bb62e134f9f55b504d98efaf1991e35e70b56473c653b2a`(实现笔初版 1251 行/126 用例 sha `437e0284…b351`,补齐笔区内纯追加) |
| 3 | `docs/P3_WP_E_REPORT.md` | 168(勘误② 0036073 时点) | 勘误② 时点 `git show` 复核为准(报告笔 9bc2200+勘误①1972970+勘误②0036073 三笔承载;本文档行数自指以 wc -l 实取为准) |
| 4 | `docs/P3_WP_E_DELIVERY.md` | 本文件 | 终笔时点 `git show` 复核为准 |

提交链(纯线性,零 merge): 登记 bcd363d → 实现 04e30fc → 测试补齐 1b50fc3 → 报告 9bc2200 → 勘误①1972970 → 勘误②0036073 → DELIVERY 笔(本笔)→ 定值笔(终笔)。
BASE-P3E 后每笔单父;`git log --merges 91612378..HEAD`=空(证据包 03 类)。较家族 5 笔先例多 3 笔(测试补齐+勘误×2,REPORT §三.4/§三.5 如实登记)。

## §二 证据清单(证据包 `/tmp/p3-wp-e-evidence/IA-P3-WP-E-EVIDENCE.zip`,8 类)

| 类目录 | 成员面 |
|---|---|
| 01-spec-registration/ | REPORT §零 全节副本(规格抄录 §零.1+登记清单 §零.2..§零.9,勘误② 后工作树版) |
| 02-dual-source-copies/ | 4 交付件×{git-show TIP 版+工作树版}+cross-hash-table.txt(DELIVERY TIP 版如实标注未入库@装配时点,R065 先例口径) |
| 03-git-forensics/ | ls-remote(推送前全分支快照+dev/p3-impl-e 推送前未上远端核验+main=91612378 等值)/log/name-status(BASE..DELIVERY 恰 A=4+M=0+D=0)/merges-check(空)/head-parents(单父)/base+design-fix1 祖先双核验/reflog/设计在场核验原始输出(DESIGN L194-198 逐字+设计三件 hash-object 双侧)/LIVE 三面(grep 零命中+real_data_acceptance sha256+LaunchAgents 清单哈希) |
| 04-local-ci-mirror/ | CI 同款方法学镜像脚本+逐套件串行记录(87 行名称+退出码)+汇总结果(87=86 exit0+1 SKIP+0 非零;SKIP=身份锚 test_glm_live;基线 86 槽零回归+本包恰 +1) |
| 05-evidence-mapping/ | AC-02 四要点映射表副本(REPORT §二)+如实偏差副本(REPORT §三)+DP/参数登记节副本(REPORT §零.4/§零.5)+§5.3 数值标注扫描清单(REPORT+DELIVERY 双件) |
| 06-run-artifacts/ | 零运行产物声明+锚定(repo 零本包运行产物双 find 扫描)/测试运行 stdout(129 OK verbose)/模块 selfcheck+py_compile 实跑/黄金首原理件与输出(六 sha)/模块实跑交叉裁定件与输出(ALL MATCH 六面全等)/负向敏感性三注入脚本+终态记录(9/2/4 红→复绿→sha 零残留) |
| 07-selfreport-copy/ | stdout 四段自述装配时点稿(与终稿差异=恰 zip 整体定值行组,R065 先例口径) |
| 08-dual-interpreter-record/ | 双解释器记录: 系统 3.9.6 全套件 129 OK+selfcheck;3.10+ 执行席不可达如实登记(命令面/目录面沙箱拦截);规范形守卫零版本依赖证明链(纯字符串+月长表+闰年规则,零 fromisoformat 3.11 宽形面);CI 3.11@offline-tests.yml L29 实读 |
| (根) SHA256SUMS | 清单自身显式豁免(不塞入 zip 自身;置于 zip 旁 /tmp/p3-wp-e-evidence/ 下,合同 §3 步骤12 口径) |

zip 定值(文件数/字节数/sha256)以终笔提交信息与会话 stdout 为准(zip 内本副本不含该定值行,R065/WP-C/WP-D 先例口径)。

## §三 验收对照(合同 AC 逐条;详情见 REPORT §二/§三/§六)

- AC-01 规格抄录: REPORT §零.1 DESIGN L194-198 逐字抄录+四要素齐备+E 行与 A/B/C/D/F 行可区分;冻结章注记行号一致偏差 0 行 ✓
- AC-02 四要点: ①②③本地面 PASS(实现面+测试面 file:line 映射,REPORT §二);④CI 面=工件入库+本地镜像 87=86+1SKIP+0 非零零回归,**分支 run NOT VERIFIED@执行席**→操作者 CHECKPOINT dispatch `rounds/042/P3-WP-E-CI-dispatch-evidence.md`
- AC-03 全合成 fixture: 唯一数据源=文件内合成(标注 2+笔记 2+合成 WP-D 编排面输出 1 件字面量,与独立首原理预计算件六面输出逐字节一致);预期值=黄金字面量 6 项(标注/笔记视图+标注/笔记档字节+导出文档序列化+导出渲染 sha256),独立预计算+测试内 hashlib 复算+模块实跑三方一致;映射表见 §五;AC-03.7 不适用(零 GLM 调用面,REPORT §零.8)
- AC-04 数值标注: REPORT §六(实取类+合成手推定值类+示意类=无)+DELIVERY §二 计数逐项 [实取·来源] ✓;§5.3 六项扫描清单成件(证据包 05 类,REPORT+DELIVERY 双件)
- AC-05 纯度: 零网络/零 GLM/零凭证/零付费(import AST 白名单 {json,os,sys}+report_quality_review+剥 docstring 禁网令牌+P3 族五模块零网络 import+零目录扫描调用+模块级路径类常量封闭集);免责声明三处=模块 docstring+标注/笔记视图尾行+导出尾行 ✓;上游对齐=复用调用禁复制分叉(rqr 常量锚+passthrough 引用同一性,P-E-15)
- AC-06 git 纪律: 自 BASE-P3E 全值切出→纯线性 8 笔零 merge/amend/force;main 未触碰;LIVE/launchd 零触碰(证据包 03 类三面);零 tag;终局单支推送 no-force ✓
- AC-07 不构成投资建议+快照纪律+他包范围: 免责三处(同 AC-05)+三红线承载(零主动采集/来源等级隔离/用户数据零落 LIVE)+快照纪律守卫 data+daily 相邻组件 fail-loud 三读写面;rg L545 周报技术分析槽位零触碰(白名单 M=0 结构性保障);WP-A/B/C/D 面只读复用零改写,W4/W5 侧边验收工具零接入,零状态档写入 ✓

## §四 参考与漂移维护策略(AC-03 生效;三要素)

1. **预期值唯一来源=版本化合成 fixture**: 全部断言预期值锚定 tests/test_p3_wp_e.py 内版本化定义(FX_* L38-46+EXPECT_* L48-59+QUALITY_REVIEW_OUTPUT L62-88+GOLDEN_SHAS L90-103+黄金三渲染全文 L105-155+_build_golden_fixture L164-190),fixture 与断言同文件同 commit 演进;黄金值另经独立预计算件(/tmp/p3-wp-e/fixture_and_golden.py,零被测模块 import;证据包 06 类)固化第二源,双源不一致=交叉裁定器非零退出(六面 ALL MATCH 实录)。
2. **fixture 演进同 commit 同步**: 新增/修改 fixture 须与受影响断言同一 commit;预计算件与 GOLDEN 任一侧演进,须同 commit 重算对方并留三方一致裁定输出+六面逐字节一致裁定(证据包 06 类)。
3. **真实数据档永不入预期值来源**: data/daily 与 data/research 真实档结构性禁入(测试零真实档引用+四输入面路径守卫 fail-loud+零默认真实路径+AST 零连续字面量);上游行为变化(rqr STATS_SCHEMA_VERSION/编排面返回文档结构/rg v2 词表)导致的漂移,以上游版本为权威修正 fixture 与黄金值(禁以被测模块输出口径反向固化预期值);接口(c) 输入 fixture 为 WP-D 编排面返回文档的合成等价件,WP-D 演进时须同步该 fixture 结构面(schema_version 锚经 `rqr.STATS_SCHEMA_VERSION` 复用调用自动追踪)。

## §五 fixture→断言映射表(断言组→fixture 定义 file:line)

| 断言组(测试类) | fixture 定义锚(tests/test_p3_wp_e.py) | 装配/消费面 |
|---|---|---|
| TestGoldenFirstPrinciples(黄金双源) | FX_* L38-46+EXPECT_* L48-59+QUALITY_REVIEW_OUTPUT L62-88+GOLDEN_SHAS L90-103+黄金三渲染 L105-155+_build_golden_fixture L164-190 | hashlib 首原理复算对照(六面 sha+三渲染全文逐字) |
| TestDPParamRegistration(登记锚定) | 模块常量+REPORT §零.4/§零.5 登记值字面 | registered_dp_values/registered_param_values/dp_selfcheck+monkeypatch 回改检出三面 |
| TestDateGuard(规范形守卫) | 无 fixture(纯日期函数) | P-E-03 十位带杠 ASCII 形+截断语义/月界/闰年含世纪规则/紧凑形周形拒 |
| TestRecordKeys(档键族) | EXPECT_* 档键形 | ANN-/NOTE-YYYYMMDD-NNN 形/序号界/显式 ID 日期段一致 |
| TestAnnotationInterface(接口 a) | FX_A1/A2+EXPECT_A1/A2 | 6 字段封闭集/空白拒/自动配号/显式透传/读回等值 |
| TestNoteInterface(接口 b) | FX_N1/N2+EXPECT_N1/N2 | source_level 系统强制签名不可传入/引用拷贝非别名/metric_refs 校验 |
| TestAppendOnly(append-only 纪律) | EXPECT_*+档字节 | 同日单调/跨日独立/前缀字节保逐字节/重复拒/溢出 fail-loud/G3·G4 黄金 |
| TestLoadRecordsFailLoud(档读取) | 坏行字面 | 坏 JSON/非 dict/缺档键/重复档键/空行容忍 |
| TestSourceLevelIsolation(隔离三面) | v2 词表锚+标签词面 | 词表/键集/渲染三面+monkeypatch 破坏检出+零 ★ |
| TestZeroActiveCollection(零主动采集) | 模块源码+P3 族五模块 | 禁扫描调用/import 白名单/零监视网令牌/路径常量封闭集/五模块零网络 import |
| TestPathGuards(守卫四面) | 沙箱树(data/daily·LIVE mock) | 快照纪律三面+LIVE 三面+user_root LIVE 拒+~/ 形+写入域外拒+相邻性正例 |
| TestExportInterface(接口 c 校验装配) | QUALITY_REVIEW_OUTPUT L62-88 | 9 键恰等/引用同一性 passthrough/窗口字段承载/rqr 常量锚/确定性序列化/G5 黄金 |
| TestExportRender(导出渲染) | QUALITY_REVIEW_OUTPUT 变体 | G6 黄金全文+简报逐字嵌入+hit_rate 数值/N-A/空建议/非文档拒 |
| TestRenderViews(旁路渲染) | EXPECT_* | G1/G2 黄金全文+免责尾行+空清单计数+非列表拒 |
| TestStaticPurity(AST 纯度) | 模块源码文件 | open 模式记账 'a'×2+'w'×1+'r'×1/禁写调用/sys.path.insert 恰 1/LIVE 行锚定+连续形禁/零回读面/零改写 API 面/上游 sha 等值/编译 |
| TestNegativeInputs(负向守卫) | 内联非法形+沙箱树 | 非 dict 记录/缺字段/非字符串内容/写入域外/LIVE/快乐路径单文件 |
| TestZeroWrite(零回写) | fixture 树+rqr 源档 | 读渲染装配树 sha 前后等值/append 恰改目标档/失败追加零部分写/上游源档 sha 等值 |
| TestSelfcheckMain(__main__) | 模块 __main__ 入口 | subprocess 受控 1 处(退出码+哨兵行+免责+运行目录零新文件) |

## §六 zip 定值(终笔登记)

(定值笔区内纯追加,R065/WP-C/WP-D 笔B 先例;文件数/字节数/sha256 以终笔提交信息与会话 stdout 四段为准)

## §七 如实偏差(全项登记;不声明「无偏差」)

与 REPORT §三 同源同步(8 项): 模块-登记对齐 2(open 'a' 内联化恰 2 处+零 datetime 纯日历化[P-E-03 登记文 fromisoformat 词面与 P-E-16 白名单张力,取白名单优先,行为面逐值等价])/测试字面量自纠 3(截断语义归位+渲染隔离断言归位+路径类常量封闭集归位)/测试补齐笔 1(四登记面补齐 126→129 用例,k=4/M=0 不变)/补齐笔提交信息行数误记(1297→实取 1301)+勘误笔×2(GOLDEN_SHAS 行锚+提交链计数,零 amend 独立纠偏)/subprocess 受控 1 处(TestSelfcheckMain)/CI 分支 run NOT VERIFIED@执行席(操作者 rounds/042 dispatch)/行号容差承接(偏差 0);不声明无偏差。
