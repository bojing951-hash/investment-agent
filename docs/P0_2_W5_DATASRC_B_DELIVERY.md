# P0-2 W5-DATASRC-B 交付文档(R049;契约 IA-P0-2-W5-DATASRC-B-AC-v1.0)

- 契约: IA-P0-2-W5-DATASRC-B-AC-v1.0(FROZEN 2026-11-04 11:2x HKT;存档 `contracts/`,SHA256=c3b685f85b5d3bff06c5a87475a364ac78675ff116ee451ad9e1ff5bc424d29c)
- 分支/基点: `dev/p0-2-w5-rerun` 自基点 cebc4afcaf96d172fcee01de43451cea6cfe6997 线性追加,本轮恰 2 笔 commit(C1 实现=scripts×2+tests×1;C2 docs=本文件+R032 交付文档补登块);最终尖端=本 docs commit,SHA 不自嵌,以 `git rev-parse HEAD`/`git ls-remote`/证据包 git/FINAL-TIP.txt 为准(R048 T4 先例)。
- 执行日: 2026-11-04(UTC);证据包: /tmp/w5datasrc-b-evidence/IA-P0-2-W5-DATASRC-B-EVIDENCE.zip
- 终局一句话: 方案B备源修复落地——指数逐只 **tushare 先行零变化+异常时东财 EM 回落(via 标记,date≤20261103 在途行禁用)**,成交额 **方案2重写为 EM 双取(元÷1e8→亿元,source 标记,旧新浪回落删除)**,fact_engine **恰两处诚实标签(diff 恰 2 hunk)**;CI 等效环境全套件 54/54 exit=0,负向敏感性 6 注入全红;本轮不跑验收、不产生判定件(那是 R050)。

## ① 根因实证(引合同附录A §〇锚定四)与批准基础(引锚定三)

- **判定件根因**(R032, rounds/012 终裁 NV-1): Gate A core 4(SHCOMP/SZCI/SH_AMOUNT/CN_TOTAL_TURNOVER)未清零 = tushare 同 token index_daily 配额被外部先在耗尽(判别首调 2026-11-04T01:07:57Z 即「5次/天」,环境性)。
- **旧 akshare 回落 amount=0 的结构性根因——本轮实取补强**(证据 attempts/sina_column_probe_console.txt,2026-11-04 实取): `ak.stock_zh_index_daily(symbol='sh000001')` 列清单=[date, open, high, low, close, volume],**无 amount 列**(机器输出「含 amount 列: False」)→ 旧代码 `latest.get('amount', 0)` 恒 0 → R032 attempt1_china console L39「akshare amount为0，跳过」。结论与锚定四一致: 非数据源不可用,是端点无该字段(结构性缺陷)→ 删除而非修补。
- **东财端点可用性**(证据 attempts/em_probe_console.txt,2026-11-04 实取): `ak.stock_zh_index_daily_em` 6 只 EM 标的(sh000001/sz399001/sz399006/sh000300/sh000905/sh000852)全部实取成功;免费、无需凭证、经仓库 `_no_proxy` 惯例禁代理直连(系统代理 127.0.0.1:7890 在场被正确禁用);完结日(2026-11-03)close 与新浪端点交叉一致(sh000001: EM 3608.10 vs 新浪 3608.098);在途行(2026-11-04,当日盘中)在案且被截止规则排除。
- **批准基础**(引合同附录A §〇锚定三): 用户已实批「备源换路」方向。本轮仅落实合同 §三范围: 唯一新增通道=akshare 公开免费端点,零新 token/零付费源;`real_data_acceptance.py`/八项门槛/容差/比较日/61s 闸门/tushare 调用参数/A_SHARE_INDICES 成员与顺序全部零触碰。

## ② 改动逐 hunk 映射(B-AC-01/02/03)

| 文件 | hunk | AC | 内容 |
|---|---|---|---|
| scripts/china_market_collector.py | h1(@@-71,6+71,99) | B-AC-01/02 | 常量+行选择: `EM_FALLBACK_MAX_DATE='2026-11-03'`(合同级截止,在途行禁用)、`EM_MAP`(6 标的,=A_SHARE_INDICES 全集)、`_em_settled_pairs`(date≤截止 升序完结行)、`_em_last_settled`(最后一完结行)、`_fetch_index_em`(F1 回落 item 构造) |
| scripts/china_market_collector.py | h2(@@-166,11+259,19) | B-AC-01 | `fetch_a_share_indices`: tushare 成功路径 item 新增恰一键 `via='tushare'`(tushare 调用/闸门/字典序零变化);异常路径原 `❌` 打印逐字保留后追加 EM 回落,EM item=同 schema 全键+恰一新增键 `via='akshare_em'`(周/YTD/pct 按取值行当年窗口与 tushare 路径同规则推导,series=年窗序列,date→YYYYMMDD 同规格);EM 失败→该指数如实缺失+告警打印 |
| scripts/china_market_collector.py | h3(@@-420,32+521,44) | B-AC-02 | `fetch_turnover`: 方案1 零变化;方案2=旧新浪回落**删除**→EM 双取 sh000001+sz399001(禁代理直连,同样 date≤2026-11-03),amount(元)÷1e8 round2 → sh/sz/total_amount_billion + `source:'akshare_em'` + date 同方案1 规格(YYYYMMDD)+scope 口径串;打印样例 `✅ 成交额(akshare-em): sh≈8108.29 sz≈8926.08 total≈17034.37 亿`(实测输出与合同字样逐字一致);无完结行/EM 失败→None(如实) |
| scripts/fact_engine.py | h1(@@-343,7+343,7) | B-AC-03 | a_share_indices 消费行 `sub='sina'`→`sub=item.get('via','sina')`(via 透传;无 via 的历史数据行为不变) |
| scripts/fact_engine.py | h2(@@-372,17+372,20) | B-AC-03 | turnover calc 按 `to.get('source')` 分支: akshare_em→「东财 元→亿元(…)」三串;缺失→原字符串逐字保留;elif 降级分支与其余消费逻辑零触碰 |
| tests/test_p02_w5_datasrc_b.py | 新增(21 用例) | B-AC-04 | 离线 mock 行为锁(零网络,中性合成数值不冒充真实行情): T1 tushare 先行零变化/EM 仅异常触发;T2 在途行禁用·无完结行→None·schema=tushare键∪{via}恰一新增·周/YTD/pct 推导·截止日常量锁;T3 方案1 零变化(千元÷1e5·无 source 键)·EM 双取(元÷1e8 round2·source·date·双取顺序)·EM 失败→None(无第三方案=旧新浪回落已删);T4 via 透传/缺省 sina·东财 calc 分支·缺 source 原字符串·旧 elif 降级分支不变;T5 源级冻结锁(旧新浪调用已删/清单顺序/61s 闸门/EM_MAP 全覆盖) |

- fact_engine diff=**恰 2 hunk**(grep -c '^@@'=2,机器可验);collector diff=3 hunk;合计 5 hunk+1 新增测试文件,无其他文件改动。

## ③ 预期值表与实取对照(±0.1%;B-AC-01/02)

| 项 | 合同预期 | EM 实取(2026-11-03 完结行) | 偏差 | 结论 |
|---|---|---|---|---|
| SHCOMP close | 3608.10 | 3608.10 | 0.0000% | ✓ |
| SZCI close | 10876.99 | 10876.99 | 0.0000% | ✓ |
| sh_amount_billion | 8108.29 | 8108.29(=810829284737.9元÷1e8 round2) | 0.0000% | ✓ |
| sz_amount_billion | 8926.08 | 8926.08(=892607522375.23元÷1e8) | 0.0000% | ✓ |
| total_amount_billion | 17034.37 | 17034.37(=8108.29+8926.08) | 0.0000% | ✓ |

- 实取来源=attempts/em_probe_console.txt(§0.4 境内直连环境自检+双端点实取,含 6 标的在途行原始尾 3 行与「在途行(date>2026-11-03): ['2026-11-04']」逐标的机器行)。
- 真实通道 console(attempts/live_channel_console.txt,2026-11-04T04:1x–04:2xZ 实取): 在 DEV 工作树真实执行 `fetch_a_share_indices()`+`fetch_turnover()` 两函数(tushare 先行真实调用 7 次 index_daily 全被拒——首调「5次/天」+后续「1次/小时」,与 R032 外部耗尽模型一致;零写入)。**实际结局=配额仍耗尽,全落东财回落**: 六指数逐只 `✅ … [东财回落 akshare_em]`(SHCOMP 3608.1/SZCI 10876.99/…,date=20261103 在途行已排除,week/ytd 在场);成交额行逐字=「`✅ 成交额(akshare-em): sh≈8108.29 sz≈8926.08 total≈17034.37 亿`」(与合同 §三 B-AC-02 期望样例逐字一致),结果 JSON 含 `source:"akshare_em"`、`date:"20261103"`、sh/sz/total=8108.29/8926.08/17034.37;末尾五项期望值对照全部偏差 0.0000% ✓。

## ④ 测试与负向敏感性(B-AC-04)

- **套件计数如实**: tests/ 现 55 个 test_*.py(基线 54+新增 1),test_glm_live 按冻结要求跳过 → **执行 54 套件**(基线 53+新增 1,与合同「新增测试文件则如实计数」一致)。
- **CI 等效环境全绿**(权威口径): 本地 clone@cebc4af+本轮 3 个改动文件+空 data/(与 GitHub Actions checkout 同构)逐文件 `python3 tests/test_*.py` → **54/54 exit=0,SUITE_FAIL=0**(证据 suite-ci-parity/SUITE-SUMMARY.txt)。
- **DEV 工作树直接运行**: 53/54 exit=0,test_p4_fixes exit=1——既有数据环境差异(W5-FIX2 交付文档 §6 已登记同象: 该套件依赖多月真实宏观历史序列,DEV 工作树 data/daily 只有近期单日→月度序列提取 0;同套件在空 data/ clone=43 通过/0 失败;与本轮 diff(China 采集回落+诚实标签)零交集,非本轮回归)。逐套件日志 suite-dev-worktree/。
- **pytest**: 新文件 `python3 -m pytest tests/test_p02_w5_datasrc_b.py -q` → **21 passed**;整树 `python3 -m pytest tests/ -q` 于基点 cebc4af 与本轮**同为既有结构性 INTERNALERROR**(53 套件中多为脚本式、模块级 `sys.exit`,pytest 收集期 SystemExit;本套件历史上以 CI 逐文件方式运行,W5-FIX2 轮先例同口径;非本轮引入、非本轮回归,pytest_baseline_pre.txt 留档基线同象)。
- **既有测试零删改零 skip**: diff 仅新增 1 测试文件(git 可验);无既有测试触碰回落路径(grep: 全 tests/ 无 fetch_turnover/stock_zh_index_daily/_fetch_index_em 引用),故不存在「改断言」项,新契约由新文件以不低于原覆盖强度锁定(原覆盖=0)。
- **负向敏感性(真实注入)**(证据 attempts/NEGATIVE-SENSITIVITY.txt): 6 类退化副本(importlib 加载,仅存 /tmp 证据域)——NEG-1 在途守卫删除(截止放开9999)→T2a/T2b/T2f/T3b/T3d 红;NEG-2 单位÷1e8→÷1e5→T3b 红(1234567.89≠1234.57);NEG-3 via 两处缺失→T1a/T1c/T2d 红;NEG-4 source 缺失→T3b 红(KeyError);NEG-5 fact_engine calc 分支删除→T4b 红(断言,非加载错);NEG-6 空数据守卫删除→T1b 红(越权回落被检出)。**ALL_RED**。

## ⑤ 证据包(⑹类)与 Git/隔离(B-AC-06)

- /tmp/w5datasrc-b-evidence/ 六类: ⑴ 双端点实取 console(em_probe(6 标的+在途行)/sina 列清单/live_channel)+⑵ 每 hunk diff(diffs/hunks/h1~h3-china、h1~h2-fact+全量 diff)+⑶ 测试输出(pytest 基线/新文件、suite-ci-parity、suite-dev-worktree、NEGATIVE-SENSITIVITY)+⑷ git 全套(opening/closing ls-remote、commit-chain、ACCEPTANCE-EMPTY-DIFF、FINAL-TIP)+⑸ 隔离×2(isolation/)+⑹ 自述副本;+zip+SHA256SUMS(SUMS 覆盖包内全部文件,显式豁免自身与 zip 容器)。
- `git diff cebc4af..HEAD -- scripts/real_data_acceptance.py` 输出=**空**(git/ACCEPTANCE-EMPTY-DIFF.txt 留档)。
- Git: 线性 2 笔(C1 实现、C2 docs),非 force,推送后基线 23 支 dev 尖端不变(仅本支推进;opening-ls-remote 与 closing-ls-remote 对照)。
- LIVE grep `R049|DATASRC-B|IA-P0-2-W5-DATASRC-B` 开轮/收轮各一次=零命中;launchd 零改动(投资类 plist 清单+mtime 留档,LaunchAgents 内 "investment-agent-dev" 零引用);引擎目录零读写;凭证明文零落盘(本轮零凭证使用)。

## ⑥ CI 登记说明(B-AC-07)

CI 由操作者 CHECKPOINT 侧对最终尖端 workflow_dispatch `offline-tests`,Run ID/conclusion/headSha/时间戳落字面值登记至引擎侧 `rounds/049/DATASRC-B-CI-dispatch-evidence.md`,不入 DEV 文件;执行方本轮零 CI 动作(不 dispatch、不改触发,R032 §⑦ 先例)。**预期套件数=54**(基线 53+新增 tests/test_p02_w5_datasrc_b.py)。

## ⑦ R050 依赖声明(步骤8)

- R050(正式重跑轮)以本轮最终尖端为基点,由操作者另冻合同;判定件产生权在 R050。本轮零验收运行、零判定件、零 data/daily 写入。
- 通道预期(两态均诚实): tushare 配额满→六指数+成交额全落 EM(via/source='akshare_em',取值行=2026-11-03 完结行)→Gate A core 4 项可经备源在场;tushare 配额释→via='tushare' 直取(61s 闸门照常,6+2 调用时长远小于小时窗)。若届时 EM 端点全失效→如实缺失进入 NV 臂,禁硬凑(合同三态)。
- 口径如实披露: ①china obs 日期=20261103(合同级截止,在途行禁用),R050 验收数据日若更近,时效窗口判定属 acceptance 冻结行为,非本轮改动面;②EM amount 单位=元(tushare 千元),消费侧 calc 按 source 分支标注,不冒充;③深侧成交额口径=399001 成指成分(非全市场),WARN 披露保持。
- R032 交付文档文末已按合同补登 DEFERRED-1/2 两处更正(四要素;append-only)。
