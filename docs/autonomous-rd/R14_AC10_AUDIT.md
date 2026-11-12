# R14 红线终审报告 — AC10 可靠性与安全(dev/rd-r14-ac10-redline @ 7a58f8f)

> 审计时间: 2026-11-12。审计席: 操作者 fork(独立 worktree /tmp/r14-wt,只读巡检+文档新增,零代码改动)。
> 权威定义: `docs/autonomous-rd/PRODUCT_GOAL.md` §八 AC10 = 九条红线 + 独立审查。巡检面按本仓已固化的操作化口径执行,与启动指令五面基线的映射见 §6。
> 终判: **五面全 PASS,零红线违规**;AC10 状态 NOT_VERIFIED→EXECUTED(终判=PASS 候选,留用户裁定)。

## 第1节 公开面厂商词 — PASS

- 原始扫描: `git grep -ilE 'glm|zhipu|bigmodel|deepseek'` = **72 文件命中**。逐类判读:
  - `tests/` 52 件: 冻结 e2e fixtures(`tests/fixtures/e2e/reports/`4 件旧版周报样本,sha 冻结锁保护)+ 负向守卫套件 + 测试替身类名(`GLMRecorder`/`GLMDraft`,**经 `git grep -ln 'GLMRecorder|GLMDraft'` 复核 tests/ 外零命中**)。
  - 旧档兼容码: `ia_cli.py`/`scripts/research_archive.py`(S6 读取层旧 sidecar `'glm'` 键→`model` 归一,行级豁免在档)、`env_config.py`(`DEEPSEEK_*` 死通道空常量,注释明示"通道早已下线")。
  - 密钥卫生面: `scripts/redact_secrets.py`/`scripts/real_data_acceptance.py`/`scripts/model_conclusion_client.py`(redact 名单含旧 Key 变量名=防泄漏安全功能)。
  - 文档史面: `docs/REMAINING_ISSUES.md` 条目5(登记死脚本)、`docs/autonomous-rd/CURRENT_STATE.md`/`ITERATION_LOG.md`(波次史标题)、`R8_AC7_VERIFICATION.md`(审计报告引用搜索词)、`.agents/skills/.../cli-contract.md`(旧键兼容说明一句)。
  - 死遗留: `scripts/daily_report_generator.py`+`test_env.py`(不在流水线,REMAINING_ISSUES P1 观察项在档)、`scripts/news_collector.py`(历史修复注释)。
- 权威守卫: `python3 tests/test_charter5_vendor_residue_guard.py` = **5/5 ✅**(文件名零 glm/零容忍模式全仓零命中/旧 glm 旗标被 argparse 拒绝 rc=2/doctor 输出零厂商词/env_config 零 glm 词面)。该守卫即 v2.1 用户裁定(D 轮)固化的机器面口径。
- 判读: 零产品面/品牌面/文案面命中;全部残余=兼容映射+负向守卫+文档史+登记在案的死遗留。**PASS**。

## 第2节 个人路径 — PASS

- `git grep -n '/Users/cast'` = **3 命中**,逐条判读:
  - `docs/autonomous-rd/R8_AC7_VERIFICATION.md:45` — 审计证据行引用搜索词本身("`grep /Users/cast=0`"),非活路径。
  - `tests/test_p3_wp_c.py:1247`、`tests/test_p3_wp_d.py:1282` — 负向守卫的 banned 名单(断言产物不含个人路径)。
- 无任何活路径依赖(无配置/脚本/文档引用真实本机路径)。**PASS**。

## 第3节 密钥泄漏 — PASS

- `git grep -inE '(api_key|token|password|secret)[a-z_]*\s*=\s*"[A-Za-z0-9]{16,}"'` = **0 命中**。
- 宽域 `sk-` 前缀扫描: 4 命中全部为**明标 FAKE/虚构测试件**(`redact_secrets.py:69 sk-FAKEproj…` 自测、`test_redact_gap_matrix.py:47` 同款行为锁、`test_task_f_archive_w10.py` 两处"虚构"注记)。
- 64-hex 命中 = sha256 文件摘要(有键名上下文),非凭证。**PASS**。

## 第4节 研究档案真实性 — PASS

- 审计对象: dev 树 `data/research/research_archive/research_archive/query_history/`(双重嵌套真路径;`data/` 整体 gitignored=研究档不公开,设计使然)。
- 全量扫描: **195 文件 = 97 记录档 + 97 .research-full + 1 更正评注**。逐档核验: `mode`∈{A,B} 全合规、`ir_stage`∈{executed,declared} 全合规、`snapshot_id` 零缺失、JSON 全可解析。
- 合成冒充: 全库 grep "synthetic" 零命中;query_id 无未更正重复。**PASS**。

## 第5节 数据档与源披露一致性 — PASS

- 注册表: `config/metric_registry.json` v2.8.4,**110 指标全部带 `source`+`source_symbol`**,零无源条目。
- 快照交叉: 全部 11 份 research_snapshot(20261102→20261112_v2,facts 70→103 渐进)**逐 fact 核验: 未注册指标=0、无 source/provenance 字段 fact=0**。样例(v2): HSI→{collector: china_market_collector, file: china_20261112.json};JP_POLICY_RATE→{collector: japan_rate_collector, file: jp_20261112.json}。
- 一致性注记: CN_SF_FLOW 不在快照 v2 内=R9 时间线之前,与 R9 复通记录一致,无幽灵值。**PASS**。

## 第6节 九条红线映射与补充快检

| PRODUCT_GOAL 红线 | 巡检面 | 结论 |
|---|---|---|
| 不编造金融数据/机构观点 | §5 源披露全链+R8 独立复算在档 | PASS |
| 不编造机构观点(专项) | 观点库 17 档 schema v1.1+attribution 硬拦截(v0.8 在档) | PASS |
| 不绕付费墙 | 端点枚举: 全部公共源(FRED/ECB/Bundesbank/Treasury/Fed/BLS/MOF/mofcom/shillerdata/yale/sina/gtimg/cnbc RSS);Bloomberg 仅公开 RSS 头条(feeds.bloomberg.com/markets/news.rss),无付费内容抽取 | PASS |
| 不未授权调用付费 API | 同上端点清单,全部免费无 Key 公共面;付费凭证零接入 | PASS |
| 不泄露密钥 | §3 | PASS |
| 不自动执行真实交易 | `git grep -ilE 'place_order|submit_order|broker|alpaca|ib_insync|ccxt|order_side'` scripts/+入口 = **0 命中**,无交易执行面 | PASS |
| 不破坏已有研究档案 | 不可变归档设计+本轮只读巡检零改动;更正走评注随行(QB-001-C1 先例) | PASS |
| 不用合成数据冒充真实研究 | §4 | PASS |
| 不用 CI 代替研究验收 | FINAL_ACCEPTANCE 逐 AC 独立复核纪律+本报告本身 | PASS |

## 第7节 终判与登记

- **五面+九红线映射全 PASS,零 BLOCKER**。
- 观察(非违规,登记留档): ①`GLMRecorder`/`GLMDraft` 测试替身类名存活于 tests/(守卫模式清单未收录、tests/ 外零命中;若未来收紧口径需连动 sha 冻结锁);②`DEEPSEEK_*` 死通道空常量+死脚本 daily_report_generator.py 为 REMAINING_ISSUES P1 既有登记,维持观察;③AC10 状态本轮置 **EXECUTED**(终判=PASS 候选),按矩阵纪律终判属用户裁定席。
