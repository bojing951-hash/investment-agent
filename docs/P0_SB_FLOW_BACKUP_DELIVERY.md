# P0 SB_FLOW 备源修复交付文档(IA-P0-SB-FLOW-BACKUP-AC-v1.0 / R058)

> 包: 南向资金 tushare 权限拒 → akshare 东财港股通回落(仿 R049 EM 备源模式;用户 L0-5 决策二通过 2026-11-05,预授权③=东财免费公开源)。
> 分支: `dev/p0-2-sbflow-em`(基点 02565b9bec3ca998a0d71f4c48c55540d85974de=R057 merge 后 origin main,纯线性零 merge)。日期: 2026-11-05(HKT)。

## §零 基线实读与登记型决策点(先登记后实现,运行后禁回改)

### 0.1 基线实读(行号=基点 02565b9 实读)

| 对象 | 行号 | 现状 |
|---|---|---|
| `scripts/china_market_collector.py` `fetch_southbound()` | L408-448 | tushare 单通道;L414 `_pro().moneyflow_hsgt(start_date=start_week, end_date=end_date)`;L415-417 空返回→print+return None;L419-444 成功路径(result={date,south_money,north_money,[south_5d_total,north_5d_total]},south_money=百万口径,L442 print「百万」);L446-448 异常→print+return None;无任何回落 |
| `scripts/fact_engine.py` `normalize_china` SB_FLOW 区 | L357-363 | add() 两处=L359(net_buy,无sub,calc=当日净买入(亿港元))与L362(south_money,/100→亿港元,**sub='eastmoney' 一刀切**——tushare 主路产物也被标 eastmoney,构成冒兼风险,本包废除);add() 定义 L307-320(L313-314 sub→f['source']['channel']) |
| `scripts/freshness_policy.py` | L418 | `'china.southbound.net_buy': 'SB_FLOW'`(10日窗)——本包零触碰 |
| R010 登记 | — | southbound=source-persist(权限类拒「没有接口访问权限」,结构性,非限流) |

锁面核查: 全仓测试对 SB_FLOW 的断言均为**值级**(test_p02_w2 L144 `('SB_FLOW', 551.87)`/test_p02_w4 L451/fixt.py L174),无一断言 channel=='eastmoney';`f['source']['channel']` 对 SB_FLOW 无关键下游消费方(snapshot_builder L174 仅键名映射)。标签改造安全面确认。

### 0.2 接口选型(登记冻结)

- **选定**: akshare v1.18.64 `stock_hsgt_hist_em(symbol='南向资金')`(datacenter-web.eastmoney.com,reportName=RPT_MUTUAL_DEAL_HISTORY,MUTUAL_TYPE=006;免费公开零凭证,预授权③范围)。
- **淘汰**: `stock_hsgt_fund_flow_summary_em`(RPT_MUTUAL_QUOTA)——仅返回当日快照(实测 2026-11-05 单日 4 行),无带日期历史序列,无法做完结行选择与近5日累计;保留为锚定互证面。

### 0.3 字段映射与单位换算(登记冻结)

- 日期(datetime.date)→str[:10]→YYYYMMDD(同 tushare 规格)。
- 当日成交净买额(akshare 归一单位=**亿港元**)→**×100**→`south_money`(百万港元,tushare 路径现行口径);近5完结行合计同系数→`south_5d_total`。
- fact_engine 侧换算 ÷100→亿港元(现行不动)。实测往返: -32.7717亿→-3277.17百万→-32.77亿(差 0.0017=2位舍入,现行口径共享)。
- `north_money`/`north_5d_total` **键缺席如实**: EM 北向净买披露 2024-08 起停止(实测 summary 端点沪股通/深股通成交净买额恒 0),不伪造 null/0。

### 0.4 回落条件(登记冻结)

主路三态失败(异常含权限拒 / df None / len(df)==0)→进入 EM 回落,逐次 print 如实记录;取值行=日期≤`_em_max_date()`(R051 动态截止,复用 `_em_settled_pairs` 冻结 helper,在途行禁用);EM 无完结行/取值行 NaN/异常→None(=现行 source-persist 语义,如实缺失,禁假值禁重试凑数)。

### 0.5 诚实标签两值制(登记冻结)

- collector 主路产物**零改动**(不添 source 键);EM 回落产物恰一新增键 `source='akshare_em'`(禁冒充 tushare)。
- fact_engine: `source=='akshare_em'`→sub='akshare_em'+calc=东财南向当日净流入(百万港元→亿港元);否则(缺 source 键=tushare 主路产物或历史数据,R049 turnover 同款判源惯例)→sub='tushare'+calc=Tushare南向当日净流入(百万港元→亿港元)。旧 'eastmoney' 一刀切标签废除(源内该字符串零出现=测试 T5b 锁)。
- net_buy 分支(legacy,无现役 producer)零改动(基线行为: 无 channel 键)。

### 0.6 真实锚定登记(执行器实取,不入 CI 不入测试)

2026-11-05 14:21-14:47 HKT(截止=`_em_max_date()`=2026-11-04)。脱敏: 全程零凭证零 token(免费公开端点);未发起任何 tushare 真实调用(权限拒为 R010 在案事实,不烧共享 token 配额窗)。

| 面 | 实测 |
|---|---|
| 生产函数端到端 | `cmc._fetch_southbound_em()` 真跑 → `{'date':'20261104','south_money':-3277.17,'source':'akshare_em','south_5d_total':8755.38}` |
| hist_em 南向序列 | 11-02=-44.6923 / 11-03=+234.2024 / 11-04=-32.7717(亿港元) |
| 成分互证(同接口族独立 query) | 11-03: 沪+149.1416+深+85.0608=+234.2024,差 0.000000;11-04: 沪-31.6266+深-1.1451=-32.7717,差 0.000000 |
| summary 当日快照(11-05 在途,仅上下文) | 港股通(沪)-69.781331+(深)-20.757248;北向两行恒 0(披露停止实证) |
| 换算复算 | -32.7717亿 →×100→ -3277.17百万 →÷100→ -32.77亿(差 0.0017=2位舍入) |

**锚定结论: 单位判读(亿港元)经三独立 query 互证恰等,换算往返误差=换算口径内(2位舍入)。对照日≥1 日(11-03/11-04 两完结日)。**

## §一 交付清单与分支谱系

- **M 集(恰2文件,均修改)**: `scripts/china_market_collector.py`(限南向资金采集函数区与通道回落登记区)/`scripts/fact_engine.py`(限 SB_FLOW add() 标签区)。
- **A 集(恰2文件,均新增)**: `tests/test_p0_sbflow_backup.py` / `docs/P0_SB_FLOW_BACKUP_DELIVERY.md`(本文档)。
- **D=0**;`real_data_acceptance.py` 零改动(sha256=01e3f890793f09b86f1e885da9a4eb9fc143a1638cb4a56e80e2f34a5bcb331b 与基点逐字节一致,测试 T5c 锁)。
- **提交链(纯线性,自基点 02565b9)**: ①8b2c19a 实现(M2)→②56bdca9 测试(A1)→③docs(A1,本文档)→④zip哈希补记(docs-only)。尖端=④,已推 origin(见 §四终态)。

## §二 实现摘要

1. **collector(china_market_collector.py)**: `fetch_southbound()` 重构为双通道——tushare 主路调用参数/成功路径解析与键值**零变化**(L414 调用形态原样,成功产物键集/round/5日累计/print 全同基线);空返回两态(df None 与 len==0)与异常三态落入回落(逐次 print: 主路原因行+转场行「↪️ 南向主路失败/空,转东财EM回落(akshare)」)。新增 `_fetch_southbound_em()`: `import akshare; with _no_proxy(): ak.stock_hsgt_hist_em('南向资金')`,经 `df.rename({'日期':'date'})` 复用 `_em_settled_pairs`(R049/R051 冻结行选择语义),取值行=日期≤`_em_max_date()` 最后一行;`当日成交净买额×100`→south_money;近5完结行合计→south_5d_total;<5 行不产 5 日键;north_* 不产;恰一新增键 source='akshare_em';无完结行/取值行 NaN/异常→print+None。模块内登记块(L408 前)载明全部登记型决策点。
2. **fact_engine(fact_engine.py)**: SB_FLOW south_money 分支标签两值制(见 §0.5),换算 /100 不动;net_buy 分支零改动。
3. **降级标记规范**: 回落成功=正常值+akshare_em 标签;回落失败=None→现行 source-persist(S)语义沿用,无新状态、无假值、无重试凑数。

## §三 测试面(离线锁,零网络零 skip 零删断言)

`tests/test_p0_sbflow_backup.py` **18 用例全绿(exit=0)**:

- T1 主路回归×3: 成功路径键集/值/5日累计/无 source 键/EM 不触发;权限拒→回落接管不抛未捕获;df None 与 len==0 两态→回落接管。
- T2 EM 回落契约×6: 正常(×100 单位锁/在途行禁用/YYYYMMDD/近5累计/north 键缺席/schema 恰 {date,south_money,source,south_5d_total});异常→None;空(无行/全在途)→None;取值行 NaN→None;<5 行无 5 日键;FROZEN_POST 窗口推进。
- T3 标签两值×4: akshare_em 落位(channel+calc);缺 source 键→'tushare'(非 'eastmoney');net_buy legacy 无 channel 键;换算往返含真实锚定值复算(-3277.17→-32.77)。
- T4 降级如实×2: 双路异常→None;双路空→None;主路❌+转场↪️+回落⚠️三行逐次记录在场。
- T5 源级冻结锁×3: 主路调用形态零变化+新通道在场;fact_engine 'eastmoney' 零出现+两值在场;real_data_acceptance.py sha256 基点冻结。

**负向敏感性(真实注入缺陷,验证确实红;注入→红→还原→逐字节核验)**:

| 注入 | 红面 | exit |
|---|---|---|
| D1 标签冒充(tushare 产物标 akshare_em) | t3b ×1 | 1 |
| D2 采集换算 ×100→×1000 | t1b/t1c×2/t2a/t2e/t2f ×6 | 1 |
| D3 事实换算 ÷100→÷1000 | t3a/t3b/t3d ×3 | 1 |
| D4 回落被删(主路失败直接 None) | t1b/t1c×2/t4a/t4b ×5 | 1 |

**全量本地实测(CI 同构循环,排除 test_glm_live)**: 终态 **67 文件→66 可运行→66 绿/0 红**(=基线 65+新增 1,零回归)。三轮过程如实登记: ①首跑 57 绿/9 红——本机缺 `openai`/`feedparser`/`finnhub`(import 期 ModuleNotFoundError,均 CI 声明依赖列表 offline-tests.yml L33 内);②装 openai+feedparser 后 59 绿/7 红(余 finnhub);③装 finnhub-python 后 66/66 全绿。归因=环境依赖缺席,与本包改动无关(红面全部为模块导入失败,先于任何被测逻辑执行;等价套件 R[legal85] 的 greens=22 reds=6 同因=其 M集重放含 6 个 feedparser 缺失套件)。证据: 证据包 full_run_summary.txt(终态)/full_run_summary_attempt1.txt(首跑)/full-run-logs/*。

## §四 证据包

`/tmp/sbflow-evidence/IA-P0-SB-FLOW-BACKUP-EVIDENCE.zip`(成员清单与逐文件 sha256 见包内 SHA256SUMS):

1. result.md 副本(执行Agent四段自述终版)
2. DELIVERY 副本(zip 内副本=终版提交版,无 zip 整体哈希上行实测值——自指豁免,B1/B2/B4/R057 同款先例)
3. 测试源副本(tests/test_p0_sbflow_backup.py)
4. 实现源副本(china_market_collector.py / fact_engine.py 终版)
5. 锚定记录(anchor-real-calls.txt + anchor_run.py 采集脚本)
6. 全量实测(full_run_summary.txt 终态 66 绿/full_run_summary_attempt1.txt 首跑/逐套件日志 full-run-logs/*)
7. 环境归因注记(env-attribution.txt)
8. 分支谱系机器捕获(branch-state.txt: ls-remote 终态)
9. SHA256SUMS(末位)

**zip 整体 sha256 实测值: 见下方补记行**(装配后追加登记)。

## §五 漂移维护三要素与未尽事项

**漂移维护三要素**:
1. **复算指令**: `python3 tests/test_p0_sbflow_backup.py`(专项 18 例);全量=CI 同构循环 `for t in tests/test_*.py`(排除 test_glm_live);锚定复演=`python3 /tmp/sbflow-evidence/anchor_run.py`(真实端点,不入 CI)。
2. **锁面触发器**(未来变更先撞哪把锁): 动主路调用形态→T1a/T5a;动回落条件/换算→T1b/T1c/T2a/T2e/T2f;动标签→T3a/T3b/T5b;动验收脚本→T5c;删除回落→T1b/T1c/T4;另 test_p02_w5_datasrc_b(T1b/T2c 空返回不回落语义仅限指数通道)与本包南向三态回落并存,改动任一须复跑两套件。
3. **合法演进路径**: 本包冻结语义(两值枚举/换算系数/回落三态/预授权③东财范围)变更须另拟 AC v1.1;新增非东财备源=新预授权面,不在本包。

**未尽事项**:
1. **CI**: offline-tests.yml 仅 push/PR→main+dispatch 触发,dev 分支 push 不自动跑;执行Agent无 dispatch 权——**需操作者 dispatch `offline-tests` 于分支尖端并落登记件 `rounds/058/SBF-CI-dispatch-evidence.md`**(预期 66 套件全 exit=0)。
2. **真实日采集恢复**: 本包=通道面修复;真实采集日 southbound 恢复产出由后续运行日自然验证(AC §六(a)),不在本包自证。
3. **MARGIN_BAL/SH_PE 真实值补验**: 权限/积分恢复后另行(W3 PENDING 在案),与本包无关。
4. **需用户批准事项**: 无新增(部署 LIVE/launchd=用户另批,本包零触碰;东财备源已获 L0-5 决策二+预授权③)。

---

## zip 哈希补记(装配后追加;自指豁免: 上方 zip 内 DELIVERY 副本无本行)

- zip 整体 sha256 实测值: `PENDING_ASSEMBLE`(待证据包装配后按 B1/B2/B4/R057 先例于推送前补记实测值)
