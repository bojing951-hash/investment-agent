# P0-2 W5 终裁R2 程序包索引(R053;IA-P0-2-W5-FINALVERDICT-R2-AC-v1.0 配套)

- **性质与权力声明**: 本文件=零裁量机械索引(合同§一.2/R2-AC-02)。Agent 3 非终裁、无意见权;W5 最终 VERDICT 签发权专属 Agent 4;§三门槛表判定列全部留空(合同:填=FAIL)。本文档不含任何执行方判定、结论或口径改写;所有数值要么是机器件/合同原文逐字转录,要么是指向证据位置的指针。
- **合同**: IA-P0-2-W5-FINALVERDICT-R2-AC-v1.0(FROZEN 2026-11-04 18:5x HKT,占位符已实值化:【R052TIP】/【R052AUDIT】/【R052ZIP】)。附录A注入文本落档 sha256=394147d40b462e6176251a170b5687c07361510d4a4dd907f2f9718c36a57f12(=执行提示词注入转录文本的哈希;引擎侧存档原件执行位不可达未比对,R051/R052 同象如实登记——见 /tmp/w5fvr2-evidence/git/appendix-A-injected-contract.md)。
- **执行**: Agent 3(R053),开轮 UTC=Wed Nov  4 10:57:29 UTC 2026(机器件 git/opening-utc.txt);分支 dev/p0-2-w5-emwin 自基点 07f87cc5cc18db0e5e67fd6fb5d8e3a606998183(=合同【R052TIP】逐字同值)线性追加恰 1 笔 commit=新增本文件;代码零改动零 M/D;非 force;禁 main。
- **本轮证据包**: /tmp/w5fvr2-evidence/(SHA256SUMS+zip 收轮装配;哈希登记于 result.md,不自嵌本文档)。

## 〇 保险与隔离登记(R2-AC-01/R2-AC-03;机器件均在 /tmp/w5fvr2-evidence/)

1. **基点**: `git rev-parse HEAD`=07f87cc5cc18db0e5e67fd6fb5d8e3a606998183(=合同【R052TIP】逐字 ✓);工作树净(git/opening-git-status.txt 仅分支行,零改动行)。
2. **分支集 origin 25 支零漂移**: ls-remote 机器捕获(git/opening-ls-remote-raw.txt,25 refs/heads+HEAD 对称引用)与 R052 收轮件(/tmp/w5rerun4-evidence/git/closing-ls-remote-raw.txt)**逐字节一致**(diff 空,机器件 git/ls-remote-vs-r052closing.diff)→其余 24 支零漂移。关键支实值: main=50b5d13db6c477084c6f4b3944b7bd08a8e329d6(未动)/dev/p0-2-w5-rerun=f124ef3b5a261b329fbbef9722026df23e2f7e7a/dev/p0-2-w5-emwin=07f87cc5cc18db0e5e67fd6fb5d8e3a606998183。gh api 通道沙箱待批→ls-remote 等效替代(R052 先例,已登记环境事实)。
3. **LIVE/launchd 三项只读(开轮;收轮×2 复核见证据包 isolation/CLOSING-REGISTRATION.md)**:
   - LIVE scripts/real_data_acceptance.py SHA256=f9ca189c5248199bb5acbc78b2a2c82d59c10e1c7c2c2d20bdaaa6105fbfe3eb(机器件 isolation/opening-live-acceptance-sha.txt;=R050/R051/R052 在案同值=LIVE 零变化;≠DEV 01e3f890793f09b86f1e885da9a4eb9fc143a1638cb4a56e80e2f34a5bcb331b ✓);
   - LIVE 全库 grep「FINALVERDICT-R2|FINALVERDICT_R2|IA-P0-2-W5-FINALVERDICT-R2|P0_2_W5_FINALVERDICT_R2_INDEX」=**0 命中** ✓;
   - ~/Library/LaunchAgents grep「investment-agent-dev」=**0 命中** ✓(清单快照 isolation/opening-launchd-listing.txt)。
4. **旧证据包只读复核**(zip sha256 重算,机器件 isolation/prior-evidence-zips-readonly-verify.txt+chain-round-zips-readonly-verify.txt): R050=4c2ae5eacbf66683024cbaa068f9f39d7fdfe4ee89193a5cfa45e65815d08049/R051=097bc7ccacf4b17eb0953ac4e5ad7d8da8ac9bea3210321d11027d650e6f5ceb/R052=5ee5a1e66680d1ede4ac2f1ce36662759609162631939eb18bae7ca3159cf4ff(=合同【R052ZIP】逐字)均与各轮登记值一致;R052 包 62 散件 `shasum -a 256 -c SHA256SUMS` 重算**全 OK**(exit 0)。
5. **R052 证据包定位**(任务§3.2): /tmp/w5rerun4-evidence/**存续可达**(zip=5ee5a1e66680d1ede4ac2f1ce36662759609162631939eb18bae7ca3159cf4ff);引擎侧 rounds/052 登记件执行位不可达,以包内 SHA256SUMS+result.md 副本+DEV 交付文档 docs/P0_2_W5_RERUN_4_DELIVERY.md@07f87cc5cc18db0e5e67fd6fb5d8e3a606998183 为据(与合同锚定三同源)。

## 一 判定件散件清单(R2-AC-02①;13 件)

核验方式: 本轮对 R052 包 SHA256SUMS 全 62 条 `shasum -a 256 -c` 重算全 OK 后,下表=SUMS 中 formal/ 路径 13 行**原文逐字转录**(相对路径=R052 证据包包内路径):

| # | 相对路径 | SHA256(SUMS 原文逐字) |
|---|---|---|
| 1 | `formal/attempt1_formal_20261104_r4.runner.txt` | `0f1a5e74fb25706aa86125ba361e1e16a426b86583a76dd0733bf3557971c0a6` |
| 2 | `formal/attempt1_formal_20261104_r4/JUDGMENT-PIECE-MARKER.txt` | `ea092c87593401ac264a2187d8f335212d1829fb9c05ad96ff9b75a32e81f007` |
| 3 | `formal/attempt1_formal_20261104_r4/console.log` | `becf713ffb8b332adf8a0b8142305de30018f54f7bec4e1b92ca84ac5dd7df3a` |
| 4 | `formal/attempt1_formal_20261104_r4/evidence/20261104_1828_01_treasury_2026.txt` | `c3614958080e01cbdd0e27d17d6a7309e64988cab0fa23b366e2db2574897871` |
| 5 | `formal/attempt1_formal_20261104_r4/evidence/20261104_1828_02_coinbase_BTC-USD.txt` | `06b449819a382a1450926299eaf5aae59f5062b1b1a8dcf0be348ff051bace7d` |
| 6 | `formal/attempt1_formal_20261104_r4/evidence/20261104_1828_03_coinbase_PAXG-USD.txt` | `8db7d587a0578282ae8b4662b410e0418c67e3575e271b65d6b91eea4e09f916` |
| 7 | `formal/attempt1_formal_20261104_r4/evidence/20261104_1828_04_sina_sh000001.txt` | `316394c42a82ae6579ad64d83ea363a6bd48850de8daff2cb1f9fc7ba9cb0c34` |
| 8 | `formal/attempt1_formal_20261104_r4/evidence/20261104_1828_05_fred_SP500.txt` | `a61d5566713d4ddc0e51a0e6d379a36b22f5db1ff3e138bed4cd5669e755c462` |
| 9 | `formal/attempt1_formal_20261104_r4/evidence/20261104_1828_06_fred_DCOILWTICO.txt` | `3191ff2d6f65564585e2f814408aa96e0b3c851bd44cde7e17efeeafcb200f65` |
| 10 | `formal/attempt1_formal_20261104_r4/real_acceptance_20261104_1828.json` | `b38206a315f19be8cf9609e90a46d8f1bffca9ebe08352dc0aec6e4a9346e698` |
| 11 | `formal/attempt1_formal_20261104_r4/real_acceptance_20261104_1828.log` | `6967a6ba5458669541ee1b62eb564cc4e5638f9bd8551e059a3a9881e5d4ab4d` |
| 12 | `formal/attempt1_formal_20261104_r4/real_acceptance_20261104_1828.md` | `8305316ebce6c4ad82623027cabf0c4aed9cab10bbbf8cf4c046da8757944fb0` |
| 13 | `formal/attempt1_formal_20261104_r4/run.meta.txt` | `bea279853d59c7e157e9717ca1726a02c362d955f2f42688b4138483024870ec` |

判定件四要素位置指针(锚定三登记;全值以散件直读为准): HEAD=4561535067e996225eb8f99152d061d7ec116d1d(run.meta.txt/console.log)/脚本 SHA=01e3f890793f09b86f1e885da9a4eb9fc143a1638cb4a56e80e2f34a5bcb331b/UTC 窗 10:27:37Z–10:28:02Z/exit=0;JUDGMENT-PIECE-MARKER.txt 同目录在档。

## 二 工程链各轮 audit.md VERDICT 行清单(R2-AC-02②;R003~R052)

**可达性总登记(如实)**: 引擎目录(~/agent-loop;含 rounds/003~052 各 audit.md 原件与 contracts/ 存档)执行位不可达→VERDICT 行**无法从 audit.md 原件摘录**。下表「VERDICT(锚定四逐字)」列=合同 §〇 锚定四登记值逐字转录(执行位唯一可达登记源);引擎原件逐行复核权与终裁权属 Agent 4。「DEV 可达证据指针」列=位置指针(分支尖端/交付文档/证据包,全部本轮机器实取或 DEV 在档件)。

| 轮 | 对象(工作包) | VERDICT(锚定四逐字) | DEV 可达证据指针(位置) |
|---|---|---|---|
| R003 | W5 首轮(真实数据验收重构) | PASS | docs/P0_2_W5_DELIVERY.md;dev/p0-2-w5@78f4c9a83962fd7b6bdaa0328a917122a0cfd2e6(实现 4f0d42cdb46c51e1a2e08e68f4bbb23893faac90);注①两源并列登记 |
| R004 | W5-FIX1(七项缺陷修复) | FAIL | docs/P0_2_W5_FIX1_DELIVERY.md;dev/p0-2-w5@10207929c8d505845ac30f8af9a742b124b0f4d5(分支尖端);旁证: docs/P0_2_W5_FIX2_DELIVERY.md「整改对象: R004 终裁两项 BLOCKER」 |
| R005 | W5-FIX2(BTC 截断口径+计数修复) | FAIL | docs/P0_2_W5_FIX2_DELIVERY.md;dev/p0-2-w5-fix2@02f1bade0688fed6afd61aa8973bc326c3a75c1d(最终代码 SHA 9e6fe71c85353bc0ef906471ef76b9227e75a37c);证据包 /tmp/w5fix2-evidence/ zip=aa3d907a942ba527730736bbb409aa910235670a7719e0251bcbb5b8f0a53c1f(本轮实算);旁证: docs/P0_2_W5_FIX3_DELIVERY.md「整改对象: R005 终裁三项阻断」 |
| R006 | W5-FIX3(近零代码整改) | PASS | docs/P0_2_W5_FIX3_DELIVERY.md;dev/p0-2-w5-fix3@1ddfb65ec78f4358b7a004be8ef5d8916ba0f052;证据包 /tmp/w5fix3-evidence/ zip=c2af048fc0442e661a9934fe8b1f6b9120fd2b22ef2e8e0b7bfca3c397427549(本轮实算);旁证: docs/P0_2_W5_RERUN_DELIVERY.md「R006 审计 gh run 记录末位 f052 吻合」 |
| R007 | W5-RERUN(方案A 限流治理+正式重跑) | NV | docs/P0_2_W5_RERUN_DELIVERY.md;dev/p0-2-w5-rerun 轮尖端 58d0cc1e2851022612b6bf272523101b74cfe1ae(R032 交付文档登记基点);证据包 /tmp/w5rerun-evidence/ zip=efc9543c9d55e5343dc6480c471be1eeb3798bd72a7781871b521d96c637bf2e(本轮实算) |
| R012 | W5 终裁1(本合同法律基础来源) | NV(终裁1) | 引擎 rounds/012/audit.md §三门槛表+§八 NV-1 处方(不可达;合同锚定一/二即其原文);DEV 侧引用: docs/P0_2_W5_DATASRC_B_DELIVERY.md「rounds/012 终裁 NV-1」 |
| R032 | W5-RERUN-2(判别实验+正式重跑) | NV | docs/P0_2_W5_RERUN_2_DELIVERY.md;dev/p0-2-w5-rerun@cebc4afcaf96d172fcee01de43451cea6cfe6997;证据包 /tmp/w5rerun2-evidence/ zip=756e3105bd9b4d6df52f2d9258b83532d20ee17c240b09c11b5a6f5200cd4553(本轮实算) |
| R049 | W5-DATASRC-B(方案B 通道修复) | PASS(方案B通道修复,CI 41790197694) | docs/P0_2_W5_DATASRC_B_DELIVERY.md;dev/p0-2-w5-rerun@b40e70d715b0de4f1e6d2da0536e1d2af1811b8d;证据包 /tmp/w5datasrc-b-evidence/ zip=e7cd361486656485681aae782302f8aaa2085fcf7669aac4653db9540d20f2e5(本轮实算) |
| R050 | W5-RERUN-3(修复后正式重跑) | NV(零执行缺陷;core 4→0首次清零+八项产生;NV=合同预登记路径[EM窗钉死+Coinbase直连不可达+FRED T+1]) | docs/P0_2_W5_RERUN_3_DELIVERY.md;dev/p0-2-w5-rerun@f124ef3b5a261b329fbbef9722026df23e2f7e7a;证据包 /tmp/w5rerun3-evidence/ zip=4c2ae5eacbf66683024cbaa068f9f39d7fdfe4ee89193a5cfa45e65815d08049(只读复核=登记值) |
| R051 | W5-EMWIN(EM 窗动态化微修复) | PASS(EM窗动态化,CI 41811559827) | docs/P0_2_W5_EMWIN_DELIVERY.md;dev/p0-2-w5-emwin@4561535067e996225eb8f99152d061d7ec116d1d;证据包 /tmp/w5emwin-evidence/ zip=097bc7ccacf4b17eb0953ac4e5ad7d8da8ac9bea3210321d11027d650e6f5ceb(只读复核=登记值) |
| R052 | W5-RERUN-4(达标判定件轮) | PASS(18:54:10) | docs/P0_2_W5_RERUN_4_DELIVERY.md@07f87cc5cc18db0e5e67fd6fb5d8e3a606998183;证据包 /tmp/w5rerun4-evidence/ zip=5ee5a1e66680d1ede4ac2f1ce36662759609162631939eb18bae7ca3159cf4ff(=合同【R052ZIP】只读复核一致);审计登记=合同冻结头「R052审计PASS 18:54:10[CI 41815882938 success@07f87cc,54套件绿,零阻断]」 |

**注① R003 两源并列登记(如实;裁定权属 Agent 4)**: DEV 可达件 docs/P0_2_W5_FIX1_DELIVERY.md:4 载「失败基线: 78f4c9a83962fd7b6bdaa0328a917122a0cfd2e6(W5首轮,Agent4判FAILED)」,与本表锚定四登记值「R003 PASS」**不一致**。执行位零裁量: 仅并列登记两源原文,不改写任一侧;引擎 rounds/003/audit.md 原件复核权属 Agent 4。

**未决项并入位置(门槛 h 指针)**: ①合同锚定三第 4 行(在案如实 NV/IH 级清单: SPX/WTI_F FRED T+1;GOLD_F PAXG 工具身份 NOT_COMPARABLE;SHCOMP 复算 YTD INSUFFICIENT_HISTORY;GateA=DEGRADED 非核心缺 3 项;tushare 限流持续 EM 回落);②各轮交付文档偏差节(最新=docs/P0_2_W5_RERUN_4_DELIVERY.md §⑥ 七项);③本表 R050 行 VERDICT 括注(EM 窗钉死+Coinbase 直连不可达+FRED T+1 三因,前两因 R051/R052 已修,如实留档)。

## 三 门槛表(a)-(i)×证据指针(R2-AC-02③;锚定二逐字;判定列留空=Agent 4 专属)

| # | 门槛(锚定二逐字,禁改写禁放宽) | 证据指针(仅位置;判定值以 Agent 4 直读为准) | 判定(Agent 4 填) |
|---|---|---|---|
| a | overall=PASS 且 exit=0 | 判定件 real_acceptance_20261104_1828.json 字段 `overall`·`exit_code`;console.log;run.meta.txt;DEV docs/P0_2_W5_RERUN_4_DELIVERY.md §④ | |
| b | EXT-BTC 同一已完结 UTC 日 \|差异\|≤0.5% | 同 JSON `.checks[check_id="EXT-BTC"]`(字段 `comparison`/`source_identity`/`verdict`)+`.btc_close_caliber.completed_through_utc`;散件 evidence/20261104_1828_02_coinbase_BTC-USD.txt;DEV 文档 §④ | |
| c | 外部核验总 PASS≥4 | 同 JSON `.coverage.external_pass_total`;`.checks[*].verdict`;DEV 文档 §④ | |
| d | 市场类 PASS≥2 | 同 JSON `.coverage.market_pass`;DEV 文档 §④ | |
| e | UST 三期限不退化 | 同 JSON `.checks[check_id="EXT-UST-2Y"/"EXT-UST-10Y"/"EXT-UST-30Y"]`(字段 `comparison`);散件 evidence/20261104_1828_01_treasury_2026.txt;前轮对照件=R032/R050/R051 判定件(/tmp/w5rerun2-evidence/·/tmp/w5rerun3-evidence/·/tmp/w5emwin-evidence/) | |
| f | ≥1 条真实序列 WEEK/MTD/YTD 三期完整复算 | 同 JSON `.recompute_results[*]`(metric_id=SPX/GOLD_F/HSI/SHCOMP;字段 `complete_recompute`/`insufficient_periods`)+`.coverage.recompute_complete`;DEV 文档 §④ 复算段 | |
| g | 八项 check check_id/判定/evidence_id 逐字转录+来源绑定 | 同 JSON `.checks[*]` 字段 `check_id`/`verdict`/`evidence_ids`;R052 包 GATEA-CHECKS-TRANSCRIPTION.txt;DEV 文档 §④;六件外部证据散件(evidence/20261104_1828_01~06) | |
| h | 工程链各轮结论与未决项如实并入 | 本文档 §二(11 轮 VERDICT 清单+R003 两源并列登记+未决项并入位置);docs/P0_2_W5_*.md 链交付文档;/tmp 各轮证据包(§二指针列) | |
| i | 生产隔离/密钥/金融数值无未解释重大错误 | R052 包 isolation/(开收轮登记·LIVE SHA·launchd 零命中)+CREDENTIAL-SWEEP.txt+SCRIPT-SHA-CONSISTENCY.txt+UNVERIFIED-LIST.txt+data_daily_{prerun,postrun}_inventory.txt;本轮开轮隔离登记 /tmp/w5fvr2-evidence/isolation/ | |

## 四 本轮执行登记

- **零改动声明**: 本轮代码零改动;白名单恰 1 新增本文件;`git diff 基点..尖端 --name-status` 可验(恰 1 A,零 M/D)。
- **CI(R2-AC-05)**: 执行侧零 dispatch(R032/R049/R050 先例;dev push 不自动触发 offline-tests);操作者侧待办=dispatch+登记字面值(run ID+headSha 全值+conclusion+套件数,dispatch/落档两时刻分列)至引擎侧 rounds/053/。预期套件数=54(R052 基线;本轮 docs-only 零测试面变更)。
- **可达性如实汇总**: 引擎目录(~/agent-loop,含 rounds/*/audit.md、contracts/ 存档原件)执行位不可达——VERDICT 行以锚定四为唯一可达登记源、合同附录A以注入转录文本落档,两处均无法与引擎原件逐字节比对(R051/R052 同象);gh api 沙箱待批→远端 refs 以 ls-remote 等效替代。
