# P1 交付说明(DELIVERY)

> 包: R015 · IA-P1-DESIGN(docs-only 零代码) | 冻结合同: IA-P1-DESIGN-AC-v1.0(FROZEN 2026-11-02)
> 编制: 2026-11-02(UTC) | 执行Agent 自述配套文件(正式自述=result.md 四段,随证据包归档)

## ① 交付清单

| 项 | 值 |
|---|---|
| 分支 | `dev/p1-design`(自 `1ddfb65ec78f4358b7a004be8ef5d8916ba0f052` 切出,已推 origin) |
| 提交 | 2 个线性提交: 提交1 = `d8ab2c9`(INVENTORY+DESIGN);提交2 = 本提交(DELIVERY,尖端=本提交自身,全SHA 见 git 取证与 SHA256SUMS,自引不内嵌) |
| 白名单文件(恰3新) | `docs/P1_DATA_NEEDS_INVENTORY.md` / `docs/P1_DESIGN.md` / `docs/P1_DELIVERY.md` |
| 改动面 | 零代码/零测试/零工作流/零配置;`git diff --name-status 1ddfb65..HEAD` = 恰3行 A(证据包成员③全文) |
| 证据包 | `/tmp/p1-design-evidence/IA-P1-DESIGN-EVIDENCE.zip`(成员①-⑦;sha256 见 result.md 自述) |

## ② 内容摘要

- **INVENTORY**(事实层): 四经济体界定 DP-1 登记(默认候选美/中/日/欧;仓库 docs 无权威定义的实读检索声明,含 UPGRADE_PLAN 旧 P1/P2 命名冲突登记);指标归属规则 P1-P8(机械可复核);registry v2.0.0 实测 81 指标逐条归类表(US49/CN10/HK4/JP2/EA4/GLOBAL12,JP/EA 全为汇率或离岸代理、零本币注册);五层在场入口行级登记(①注册表 ②采集4数据通道+新闻+11步编排 ③fact_engine 口径 ④快照不可变+Gate A ⑤装配/评分/报告),E2E-A/B 模块如实登记不在场(P0-3 在途);缺口 G-P1-01..19(候选源三分标注: 免费公开循预授权③/PENDING 报批/依赖用户授权);跨分支登记 dev/data-inventory@`7cbef4c9bd25586ef03fc02819ae6792d0929fa0`、dev/data-coverage@`06f715b6be34dedd69f6776b1947238708de0563`;已知缺口 K-1..K-6。
- **DESIGN**(判断层): 七节齐备——§一目标边界(含命名冲突);§二决策点 DP-1..DP-4;§三经济体扩展架构:(a)字段级 schema(registry 三新字段 economy/economy_rule/market_seat、jp_/ea_ 数据档逐字段、fact_engine 扩展点、快照/装配扩展面)(b)数据策略(逐缺口引用 INVENTORY 表+配额纪律)(c)降级路径(五层一致「不填0」)(d)三个端到端走查 W-1 欧元区(缺席主导链)/W-2 中国(在场-缺席混合链)/W-3 美国(全在场基准链),实取值全部 file+观测日标注;§四 P0-2·P0-3 复用对齐(逐要素沿用/扩展/分歧+字段/机制级落点+共享档案衔接约定);§五差距 GAP-P1-01..13;§六工作包 WP-P1-A..E(四要素+可核验工件;依赖 P0-3/用户授权/PENDING 如实标注);§七红线四条。
- **DP-1 声明**: 本包不为四经济体构成做终局裁断,最终确认保留给用户/后续包。

## ③ 证据指针

- 本地逐套件运行(CI offline-tests 同构,工作流以 checkout 实读 `.github/workflows/offline-tests.yml` 为准): 逐套件日志与退出码 → 证据包成员④(`/tmp/p1-design-evidence/logs/`),汇总以 result.md 四段自述为准(本文件不复制退出码表,避免双处失同步)。
- git 取证(尖端/父提交全SHA、`git log --oneline -5`、diff --name-status 全文、ls-remote 全量)→ 证据包成员②③⑤。
- SHA256SUMS(逐成员)→ 证据包成员⑥;zip 自身 sha256 → result.md 自述(zip 不自含自哈希)。
- CI dispatch(conclusion=success 且 53 套件)属**操作者 CHECKPOINT 登记件**(`rounds/015/P1-DESIGN-CI-dispatch-evidence.md`),非执行方动作,本包不代行。

## ④ 偏离与如实声明

1. **本地环境差异预声明**: 本地 Python 为 3.9.6(CI 固定 3.11),依赖为既有环境预装(本包零网络、禁装依赖);若个别套件因工作区环境(如在案授权数据副本致套件走真实路径)出现非代码性 exit≠0,如实记录于成员④并注明归因,不以此改任何依赖/workflow——docs-only 不触测试面,代码内容与基线完全一致。
2. **跨分支数值未复核**: INVENTORY/DESIGN 中标 [示意·非实取·跨分支登记] 的数值(数据线 N71/S8/B2/C0/U0 等)引自驱动注入摘要,本包未在 checkout 内独立复核(该两分支不在本包核验面,合同明示)。
3. **候选源为设计登记**: 全部候选源(ECB/BOJ/Bundesbank/BEA/yfinance/akshare 等)仅登记,本包零采集、零配额消费、零网络(除 git/GitHub 推送);免费/凭证属性按公共知识登记,接入前由实现包实测验证。
4. **DP-1 构成未终裁**: 默认候选登记,结构不因微调失效。
5. **走查实值时点**: W-1/W-2/W-3 实取值观测日为数据档内嵌日期(2026-10-29/30、2026-11-01),非编制日当日;如实标注,不冒充实时。

## ⑤ 后续建议(明确不冻结 AC;正式 AC 由主Agent后续轮拟定)

1. WP-P1-A/B(JP/EA 主线)可先行排期——不依赖 P0-3、不依赖用户授权;建议实现包首件=registry 三字段回填+一致性单测(最小可验)。
2. WP-P1-E(CN 面)建议单独立合同并先取得用户对 china 采集器改动的授权决策(含 tushare 限流备源取舍),避免与 JP/EA 主线互相阻塞。
3. WP-P1-D 排程锚定 P0-3 落地节奏;E2E-A/B 引擎冻结版与本设计 §四 若冲突,以引擎冻结版为准并走登记型修订。
4. DP-2 官方 API 候选(ECB/BOJ/Bundesbank)建议实现包先做只读探活+样例序列核验(计入该包 AC,本轮未做)。
5. 后续包命名建议统一「IA-P1-*」前缀,消解与 UPGRADE_PLAN 旧 P1/P2 的同名冲突(§一登记)。
