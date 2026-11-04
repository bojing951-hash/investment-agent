# P0-2 W5 封口文档(R054;IA-P0-2-W5-SEAL-AC-v1.0 配套)

- **性质与权力声明**: 本文件=W5 封口留档件(合同 S-AC-03)。执行方零裁量: 全部数值/结论转引自机器件与 audit 原文并逐处标注出处;W5 最终 VERDICT 签发权专属 Agent 4(已行使,见§二);独立验收主体=Agent 4,本文自检非终判。
- **合同**: IA-P0-2-W5-SEAL-AC-v1.0(FROZEN 2026-11-04 19:3x HKT,操作者依用户预授权①批准冻结)。附录A注入文本转录件 sha256=`4afb3a52a54322281249ee9e0e29d45633811f6a9c51d134f683b4effc429429`(/tmp/w5seal-evidence/git/appendix-A-injected-contract.md);引擎侧存档原件(contracts/)执行位不可达,未逐字节比对——如实登记,R051/R052/R053 同象。
- **执行**: Agent 3(R054),开轮 UTC=2026-11-04T11:32:09Z(机器件 /tmp/w5seal-evidence/git/opening-utc.txt);法律基础=用户预授权①(合并main,登记在案,用户保留事后否决权)+rounds/053/audit.md 终裁 PASS(引擎侧操作者预核,转述入冻结章)。
- **本轮产出**: 合并提交(main←dev/p0-2-w5-emwin,非ff)+tag `w5-final-20261104`+本封口文档;恰2笔 commit(合并笔+文档笔);LIVE 部署≠本轮(=rounds/055,预授权②);launchd 零触碰。

## 一 W5 历程表(R003→R053 全轮;S-AC-03①)

「VERDICT」列=R053 索引§二(锚定四逐字=执行位唯一可达登记源)逐字转录;R053 行=本合同冻结章转述。「CI run ID」列=DEV 侧机器可达登记源(本轮 grep 实取 docs/P0_2_W5_*.md;无登记者如实标注)。

| 轮 | 对象(工作包) | VERDICT(登记源逐字) | CI run ID | DEV 可达证据指针 |
|---|---|---|---|---|
| R003 | W5 首轮(真实数据验收重构) | PASS | 41270649203(docs/P0_2_W5_DELIVERY.md L124) | docs/P0_2_W5_DELIVERY.md;dev/p0-2-w5@78f4c9a83962fd7b6bdaa0328a917122a0cfd2e6(实现4f0d42cd…);注①两源并列登记 |
| R004 | W5-FIX1(七项缺陷修复) | FAIL | 41279559970(52套件全绿;docs/P0_2_W5_FIX1_DELIVERY.md L119-120) | docs/P0_2_W5_FIX1_DELIVERY.md;dev/p0-2-w5@10207929c8d505845ac30f8af9a742b124b0f4d5;旁证: FIX2交付「整改对象: R004 终裁两项 BLOCKER」 |
| R005 | W5-FIX2(BTC截断口径+计数修复) | FAIL | 无CI run登记(DEV侧本轮机器grep零命中,如实) | docs/P0_2_W5_FIX2_DELIVERY.md;dev/p0-2-w5-fix2@02f1bade0688fed6afd61aa8973bc326c3a75c1d;证据包/tmp/w5fix2-evidence/ |
| R006 | W5-FIX3(近零代码整改) | PASS | 41334594465(53/53;登记源=docs/P0_2_W5_RERUN_DELIVERY.md L108) | docs/P0_2_W5_FIX3_DELIVERY.md;dev/p0-2-w5-fix3@1ddfb65ec78f4358b7a004be8ef5d8916ba0f052;证据包/tmp/w5fix3-evidence/ |
| R007 | W5-RERUN(方案A限流治理+正式重跑) | NV | 无本 轮run登记(DEV侧本轮机器grep零命中;其交付L108仅引fix3基线run) | docs/P0_2_W5_RERUN_DELIVERY.md;轮尖端58d0cc1e2851022612b6bf272523101b74cfe1ae;证据包/tmp/w5rerun-evidence/ |
| R012 | W5 终裁1(本链法律基础来源) | NV(终裁1) | —(引擎侧轮,DEV不可达) | 引擎 rounds/012/audit.md §三门槛表+§八NV-1处方(不可达;转述=R053索引§二/R053合同锚定) |
| R032 | W5-RERUN-2(判别实验+正式重跑) | NV | 无DEV侧run登记(docs-only轮;交付§CI=操作者侧登记说明) | docs/P0_2_W5_RERUN_2_DELIVERY.md;dev/p0-2-w5-rerun@cebc4afcaf96d172fcee01de43451cea6cfe6997;证据包/tmp/w5rerun2-evidence/ |
| R049 | W5-DATASRC-B(方案B通道修复;含fix1/fix2) | PASS(方案B通道修复,CI 41790197694) | 41790197694(锚定四) | docs/P0_2_W5_DATASRC_B_DELIVERY.md;dev/p0-2-w5-rerun@b40e70d715b0de4f1e6d2da0536e1d2af1811b8d;证据包/tmp/w5datasrc-b-evidence/ |
| R050 | W5-RERUN-3(修复后正式重跑) | NV(零执行缺陷;core 4→0首次清零+八项产生;NV=合同预登记路径[EM窗钉死+Coinbase直连不可达+FRED T+1]) | 无DEV侧run登记(如实) | docs/P0_2_W5_RERUN_3_DELIVERY.md;dev/p0-2-w5-rerun@f124ef3b5a261b329fbbef9722026df23e2f7e7a;证据包/tmp/w5rerun3-evidence/ |
| R051 | W5-EMWIN(EM窗动态化微修复) | PASS(EM窗动态化,CI 41811559827) | 41811559827(锚定四) | docs/P0_2_W5_EMWIN_DELIVERY.md;dev/p0-2-w5-emwin@4561535067e996225eb8f99152d061d7ec116d1d;证据包/tmp/w5emwin-evidence/ |
| R052 | W5-RERUN-4(达标判定件轮) | PASS(18:54:10) | 41815882938(success@07f87cc,54套件绿;登记源=冻结头「R052审计PASS 18:54:10[CI 41815882938…]」) | docs/P0_2_W5_RERUN_4_DELIVERY.md;证据包/tmp/w5rerun4-evidence/;审计登记=合同冻结头 |
| R053 | W5 终裁R2程序包(零裁量索引)+W5最终VERDICT签发 | W5 最终 VERDICT = **PASS**(19:26:30签发);R053审计零阻断(DEFERRED五项均留档不阻断;R003锚定对象列错位裁定为伪象,勘误留档) | CI success@0b5a6df 54套件(冻结章登记;run ID引擎侧DEV不可达,如实) | docs/P0_2_W5_FINALVERDICT_R2_INDEX.md@0b5a6df493043f8e4aceb289d92f5e53a88fc75d;证据包/tmp/w5fvr2-evidence/;终裁=rounds/053/audit.md(引擎侧,冻结章转述=§二) |

**注① R003 两源并列登记(如实;裁定权属 Agent 4,R053审计已裁定为伪象,勘误留档)**: DEV可达件 docs/P0_2_W5_FIX1_DELIVERY.md:4 载「失败基线: 78f4c9a83962fd7b6bdaa0328a917122a0cfd2e6(W5首轮,Agent4判FAILED)」,与锚定四登记值「R003 PASS」不一致;R053 索引§二注①原文并列两源不改写任一侧。

**VERDICT 行主登记源可达性(如实)**: 引擎目录(~/agent-loop,含 rounds/003~053 各 audit.md 原件与 contracts/ 存档)执行位不可达——VERDICT 行以 R053 合同锚定四(经操作者预核)为唯一可达登记源逐字转录;R053 终裁原文经操作者引擎侧预核逐字转述入本合同冻结章(§二);引擎原件逐行复核权属 Agent 4。

## 二 终裁结论原文引用(S-AC-03②)

**出处链**: rounds/053/audit.md(引擎侧原件,执行位不可达)→操作者引擎侧预核→逐字转述入 IA-P0-2-W5-SEAL-AC-v1.0 冻结章(附录A注入转录件 sha256=4afb3a52…,见文件头)。

**冻结章终裁原文(逐字)**:

> 'W5 终裁门槛 (a)-(i) 九项全PASS,据此 Agent 4 行使签发权:W5 最终 VERDICT = PASS(判定件 overall=PASS/exit=0 @4561535,CI success@0b5a6df 54套件,链11轮结论如实闭合)…W5 工作包可关闭'

**签发要素(冻结章登记)**: 【W5VERDICT】=PASS(19:26:30签发);R053审计零阻断(DEFERRED五项均留档不阻断;R003锚定对象列错位裁定为伪象,勘误留档)。

## 三 达标判定件指纹(S-AC-03③)

- **判定件**: `formal/attempt1_formal_20261104_r4/`(证据包 /tmp/w5rerun4-evidence/;本轮 R054 只读实算 zip sha256=`5ee5a1e66680d1ede4ac2f1ce36662759609162631939eb18bae7ca3159cf4ff`=合同【R052ZIP】逐字一致;包内 62 散件 `shasum -a 256 -c SHA256SUMS` 重算全 OK exit 0)。
- **四要素(run.meta.txt 机器直读,R054 复核)**: HEAD=`4561535067e996225eb8f99152d061d7ec116d1d`(worktree_dirty_files=0)/脚本 SHA256=`01e3f890793f09b86f1e885da9a4eb9fc143a1638cb4a56e80e2f34a5bcb331b`/UTC 窗=2026-11-04T10:27:37Z–10:28:02Z(25.2s)/**exit_code=0**;JUDGMENT-PIECE-MARKER.txt 同目录在档。
- **判定结果(锚定三/R052 交付§④ 转引)**: overall=**PASS** exit=0;状态分布{PASS 8,FAIL 0,NOT_VERIFIED 2,NOT_COMPARABLE 1,INSUFFICIENT_HISTORY 1};coverage{ust_pass 3✓,market_pass 2✓,external_pass_total 5✓,recompute_pass 3✓,recompute_complete 3✓}零FAIL;Gate A=DEGRADED(core缺失0,非核心缺失3项 MARGIN_BAL/SB_FLOW/SH_PE)。
- **13 散件 SHA256 清单**: 逐字转录件=docs/P0_2_W5_FINALVERDICT_R2_INDEX.md §一(R052 包 SHA256SUMS formal/ 13行;本轮重算全 OK)。

## 四 Layer0 收口叙事(S-AC-03④)

以下全部为合同原文转引(IA-P0-2-W5-SEAL-AC-v1.0):

- **W5=Layer0 最后一项**(合同 S-AC-03④ 原文表述「Layer0收口叙事(W5=Layer0最后一项,路线图24包待推进声明)」;本封口轮=路线图 R013 条目,合同标题「P0-2 W5 封口验收契约(路线图R013条目)」)。
- **本轮边界(锚定一原文)**: 用户预授权"合并main"在案;本轮为其唯一执行点。**LIVE部署≠本轮**(=rounds/055,路线图R018条目,预授权②);**launchd零触碰**。
- **后链(§五原文)**: PASS→rounds/055(路线图R018): LIVE部署(预授权②;**零launchd触碰**=只同步审计过的脚本/文档到LIVE树,launchd job定义文件零改动;若发现必须改launchd才能部署→停下报用户实批)→**Layer0闭合→按层推进24包(B=021-025起)**。
- **24包待推进声明**: 路线图按层推进24包(B=021-025起)(§五原文);W5 关闭后 Layer0 余下唯一待办=LIVE部署(rounds/055,预授权②,零launchd触碰)。

## 五 遗留如实清单(S-AC-03⑤;合同枚举8项全,零遗漏)

| # | 遗留项 | 状态(登记源转引) |
|---|---|---|
| 1 | tushare 限流 | index_daily 7调全拒(首调「5次/天」,后续「1次/小时」)+权限类拒4调(index_dailybasic×3+moneyflow_hsgt×1);外部结构性配额耗尽非工程缺陷,R050~R052 持续同象(源: R052交付§⑥.6) |
| 2 | EM 兜底 | 六指数+成交额全落 EM 回落 via=akshare_em(R051 动态窗 `_em_max_date()` 生效,date=20261104 当日完结行);EM 为常驻回落通道,via/source 诚实标签(源: R052交付§③;R051交付) |
| 3 | SPX·WTI_F FRED T+1 | FRED realtime 2026-11-03 最高观测=2026-11-02(T+1),无同日观测;WTI_F 参考源 DCOILWTICO 不可达/无该日数据;两者不参与达标算术,零凑数零改口径(源: R052交付§⑥.1) |
| 4 | GOLD_F NC | PAXG 现货代币≠COMEX 期货连续,工具身份不同→NOT_COMPARABLE;参考偏差0.33%仅披露不参与判定(源: R052交付§⑥.2) |
| 5 | SHCOMP IH | 复算 YTD INSUFFICIENT_HISTORY(序列不含上年末观测),已核2/3期不冒充完整PASS;R050 同象=china指数series年窗语义(源: R052交付§⑥.3) |
| 6 | GateA DEGRADED | 非PASS: 非核心缺失3项(MARGIN_BAL/SB_FLOW/SH_PE)+质量12项DEGRADED;core缺失=0 满足进入条件(FAIL才阻断)(源: R052交付§⑥.4) |
| 7 | SSH 间歇 | 在案实测: R051 publickey被拒/R052 `remote: fatal error in commit_refs_rules`/R053 推送成功但收尾 ls-remote 再 publickey 被拒=间歇故障;可用通道=gh CLI HTTPS 凭证助手(范本=/tmp/w5rerun4-evidence/gh_cred_helper.py,token零落盘);本轮 R054 实测结果如实登记于§六/证据包 |
| 8 | CI glm_live skip | test_glm_live.py=真实GLM验收套件,按契约不得进入CI,workflow 显式排除(源: .github/workflows/offline-tests.yml L6+L34-40 排除分支) |

## 六 本轮执行登记(R054;机器件 /tmp/w5seal-evidence/)

1. **合并拓扑(机器件 topology/)**: 合并提交=`5ab7c16b278d27a8961f2fba19c1483cd1cb1263`,两父=`50b5d13db6c477084c6f4b3944b7bd08a8e329d6`(main)+`0b5a6df493043f8e4aceb289d92f5e53a88fc75d`(emwin/R053TIP),`git log --format='%H %P' -1` 直取;merge-base(main,dev/p0-2-w5-emwin)=`50b5d13…`;合并树=emwin 尖端树(`git diff --stat 0b5a6df..HEAD` 空,0字节);合并零冲突('ort'策略)。
2. **tag**: `w5-final-20261104` 注释tag,对象=`2370a8206ff028ff2b64c0445f3c449881ef4eb2`,指向合并提交 `5ab7c16…`(注释含终裁结论,见 topology/tag-annotation.txt)。
3. **恰2笔 commit**: 合并笔 `5ab7c16…`+文档笔(本文件;SHA 以 rev-parse 为准,登记于证据包 result.md);白名单新增恰1文件=本文件,零 M/D 于其他文件。
4. **开工保险(S-AC-01)**: 基点 HEAD=0b5a6df… 树净(git/opening-git-status.txt);main 远端尖端=50b5d13…(ls-remote 实取=合同【MAINAHEAD】;gh api 沙箱待批→ls-remote 等效,R052/R053 先例);附录A sha256=4afb3a52…(文件头);W5 终裁=PASS 落档 rounds/053/audit.md(冻结章转述)。
5. **隔离(开轮实测,收轮×2 复核见证据包 isolation/CLOSING-REGISTRATION.md)**: LIVE scripts/real_data_acceptance.py SHA256=`f9ca189c5248199bb5acbc78b2a2c82d59c10e1c7c2c2d20bdaaa6105fbfe3eb`(=R050~R053 在案同值=LIVE 零变化;≠DEV 01e3f890…);LIVE 全库 grep 本轮标识(W5-SEAL|W5_SEAL|IA-P0-2-W5-SEAL|P0_2_W5_SEALING|w5-final-20261104|R054)=0命中;LaunchAgents grep「investment-agent-dev」=0命中+清单快照开=收;基线 origin 25支(HEAD对称行+25 refs/heads)开轮与 R053 收轮件逐字节一致(diff 0字节)。
6. **CI(S-AC-05)**: 执行侧零 dispatch(在案权限事实);push→main 按 workflow 触发面(.github/workflows/offline-tests.yml L15-20)自动触发 offline-tests——本轮自动触发 run 如实登记于 result.md(可达则记);操作者(或opd)侧待办=dispatch+登记字面值(run ID/headSha=合并提交/conclusion/套件数,两时刻分列)。
7. **可达性如实**: 引擎目录(~/agent-loop)不读不写;rounds/*/audit.md 与 contracts/ 原件不可达——终裁/审计结论均经冻结章转述,出处链§二;gh api 沙箱待批→ls-remote 等效。

## 自检对照(S-AC-01~05+反例)

- **S-AC-01 保险** ✓: 合同FROZEN+附录A落档sha256;HEAD=0b5a6df树净(合并前机器件);main远端尖端=50b5d13(ls-remote等效,gh api待批如实);W5终裁PASS落档(冻结章转述)。反例核: 终裁=PASS才开工 ✓。
- **S-AC-02 合并** ✓: 合并提交两父=50b5d13+0b5a6df(机器件);tag指向合并提交;推送main非force(§六.3/result.md登记);拓扑机器件留档(topology/)。反例核: --no-ff真合并(两父)/未捎带他支(仅dev/p0-2-w5-emwin)/零force ✓。
- **S-AC-03 封口文档** ✓: 五节齐(§一历程表12行R003→R053/§二终裁原文/§三判定件指纹/§四Layer0收口/§五遗留8项全);数值全转引注出处。反例核: 零新增裁量结论;遗留项合同枚举8项零遗漏 ✓。
- **S-AC-04 隔离** ✓: LIVE三项只读×2;launchd清单开=收;基线25支零漂移(除main本轮封口推进;收轮实测=证据包)。反例核: LIVE/launchd零变化 ✓。
- **S-AC-05 CI(main)**: 执行侧零dispatch(权限事实);自动触发run如实登记;dispatch+两时刻登记=操作者侧待办(如实,非本轮执行方义务)。
- **三态自判**: 执行合规(S-AC-01~04全过,S-AC-05执行侧义务已尽、操作者侧待办如实)→**PASS臂**(独立验收主体=Agent 4,本自判非终判)。
