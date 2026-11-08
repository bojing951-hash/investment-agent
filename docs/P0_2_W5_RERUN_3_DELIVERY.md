# P0-2 W5-RERUN-3 交付文档(R050;契约 IA-P0-2-W5-RERUN-3-AC-v1.0)

- 契约: IA-P0-2-W5-RERUN-3-AC-v1.0(FROZEN 2026-11-04 16:4x HKT;存档 contracts/,SHA256=eabbd058e060aff5(前16位,注入文所载);附录A 合同全文未注入执行提示词,执行面以注入的 AC 草案+任务提示词 §0–§4 为操作依据,冲突处以合同为准——如实登记,未见冲突)
- 分支/基点: `dev/p0-2-w5-rerun` 自基点 b40e70d715b0de4f1e6d2da0536e1d2af1811b8d(R049 最终尖端)线性追加(本轮恰 1 笔 commit=新增本文件,零 M/D,代码零改动)
- 执行日: 2026-11-04(UTC);证据包: /tmp/w5rerun3-evidence/IA-P0-2-W5-RERUN-3-EVIDENCE.zip
- 终局一句话: 修复后正式重跑完成——**Gate A core 缺口 4→0 清零**(4 只全到位,全经 R049 东财EM回落;tushare 7 调全拒,首调即「5次/天」),验收首次自 R032 后通过 Gate A 产生 overall=**NOT_VERIFIED(exit 3)**(市场类真PASS 0<2+外部总PASS 3<4);但**收盘守卫不过**(china 取值行 date=**20261103**,EM 合同级截止 EM_FALLBACK_MAX_DATE='2026-11-03' 所定,≠要求的 20261104)——按合同 §0/R3-AC-01/02「不过→NV 如实零凑数」,本轮以 **NV 臂**如实交付(判定权属 Agent 4)。

## ① 开工保险(§0;全实值)

- 合同 FROZEN(AC 草案头部登记;附录A 未注入,见文首披露)。
- 基点= b40e70d715b0de4f1e6d2da0536e1d2af1811b8d,HEAD 逐字同值;工作树净(git/opening-git-status.txt 仅分支行)。
- 分支集= origin 24 支(opening-ls-remote.txt 机器件=24 refs/heads+HEAD 对称引用);与 R049 收轮件对照唯一差异=本支 35f2962→b40e70d(R049-fix1/2 两笔,属 R049 轮),其余 23 支零漂移。
- 窗口: 开轮 UTC=2026-11-04T08:54:10Z > 2026-11-04T08:15Z(16:15 HKT 收盘后)✓,未撞限未停。
- 收盘守卫(运行后实值判定,attempts/attempt1_china_20261104.guard.txt): china 取值行 date=**20261103**(六指数+成交额全体,EM 合同级截止所定)≠20261104 → **FAIL→NV 如实**;EM amount 量级自洽(sh=810,829,284,737.9 元>6e11,但行为 2026-11-03 完结行非 11-04 行)。守卫不过的机制性原因: tushare index_daily 7 调全拒(首调「5次/天」=日配额仍被外部先在耗尽,R032 模型再证),EM 回落在冻结代码下截止 2026-11-03;本轮 §1 代码零改动,无从取 11-04 行,零凑数。

## ② 登记(§3.1)

- 脚本双 SHA(与 R049 尖端一致,开轮 shasum 实取):
  - `scripts/real_data_acceptance.py` SHA256=01e3f890793f09b86f1e885da9a4eb9fc143a1638cb4a56e80e2f34a5bcb331b(=R032 契约登记全值逐字一致;git blob=4096163ecb227b980079036eccaf5e17442081a8;该文件 R032 后零改动)。
  - `scripts/china_market_collector.py` SHA256=2509fccc8684aa5e4f3c7066d1ea83dcb833c13378ab3238d61ff87b563aef54(git blob=48ad60d5d37cc12cd1870fdd9815895561f3155c@b40e70d=R049 最终尖端,含方案B修复,本轮只读零改动)。
- 证据域三子目录: /tmp/w5rerun3-evidence/{attempts,formal,git} 2026-11-04T08:54Z 建立(+isolation/ 隔离件);R032/R049 证据包全程只读。
- 隔离开轮三项(只读): LIVE acceptance SHA=f9ca189c…(≠DEV ✓,与 R032 同值=LIVE 零变化);LIVE grep「RERUN-3|RERUN_3|IA-P0-2-W5-RERUN-3」=0 命中 ✓;LaunchAgents grep「investment-agent-dev」=0 命中 ✓(清单快照在档)。

## ③ 运行叙事(§3.2;四源全跑,news 不扩)

| # | 对象 | UTC 起–止(时长) | 数据日/产物 | 结果 | 退出码 |
|---|---|---|---|---|---|
| attempt1-china | china_market_collector.py(T1闸门) | 08:57:15–09:04:24(428.9s) | 覆盖写 china_20261104.json(82,840B) | tushare index_daily 7 调全拒(6指数+成交额首调;首调「5次/天」+「1次/小时」×4+「1次/分钟」×2;闸门7次等待42.1–60.3s全程生效)→六指数全落EM回落✅(via=akshare_em,date=20261103)+成交额EM方案2✅(source=akshare_em,date=20261103);HSI/HSCEI(腾讯)✓ date=2026-11-04;HSAHP(新浪)✓ 130.12 date=2026-11-04;moneyflow_hsgt/index_dailybasic 权限拒绝+margin 不可用(既有状态同R032) | 0 |
| attempt1-macro | macro_collector.py | 08:57:25–08:59:04(99.0s) | 覆盖写 macro_20261104.json(重写字节不变) | 12项指标全✅ | 0 |
| attempt1-rate | rate_expectations.py | 08:59:26–09:03:04(218.3s) | 覆盖写 rate_economy_20261104.json/.md | ✅ | 0 |
| attempt1-global | global_market_collector.py | 09:03:31–09:03:54(23.6s) | 覆盖写 global_20261104.json/.md | **32/32成功,0 nan**(R032 的18 nan未复现);BTC在途UTC日正确剔除(保留≤2026-11-03,close_meta.completed_through=2026-11-03) | 0 |
| **attempt1-formal(判定件)** | real_data_acceptance.py(零裁量直调) | 09:06:00–09:07:48(108.6s) | 验收数据日 **20261104**(自动最新四源齐全日,lag=0) | **Gate A=DEGRADED,core缺失0,overall=NOT_VERIFIED,exit 3**(原文见④) | **3** |

- 运行形态: china 后台与 macro/rate/global(前台顺序)时间交叠(08:57:15–09:03:54 窗内),与 R032 同形态;四源互不共享状态、各自 console/meta 独立留档;每源调用方式=`python3 scripts/<script>`,cwd=仓库根(R032 逐字同构,运行器仅 OUTDIR 适配本证据域)。
- 多试状态: 本轮**恰 1 次正式尝试**(四源+判定件各恰 1 次),末次=判定件,零重试零删改;**无判别实验**(合同 §1 禁任何 tushare 探针调用,本轮零探针)。
- tushare 调用台账: index_daily 7 次(全被拒,报文逐字在 attempts/attempt1_china_20261104.log);moneyflow_hsgt 1、index_dailybasic 3(权限拒绝);margin ≤5(不可用,静默捕获);无其他 tushare 调用;零新 token。

## ④ 末次判定原文+逐项口径(§3.3/3.4;判定件=formal/attempt1_formal_20261104/)

判定件 console 关键行(逐字):

```
📌 验收数据日: 20261104(自动最新四源齐全日(lag=0天);来源目录<DEV根目录>/data/daily)
   Gate A: DEGRADED | 事实 77 | 质量 {'PASS': 61, 'DEGRADED': 12, 'FAIL': 0} | core缺失 0 | 非核心缺失 3项(MARGIN_BAL,SB_FLOW,SH_PE)
综合结果: NOT_VERIFIED | 状态分布: {'PASS': 6, 'FAIL': 0, 'NOT_VERIFIED': 5, 'NOT_COMPARABLE': 0, 'INSUFFICIENT_HISTORY': 1, 'SKIPPED': 0}
  · 市场资产类(BTC/SPX/SHCOMP)真实同日可比PASS不足2项——其他资产证据缺失
  · 外部对照总PASS3<4——真实独立可比证据不足
```

- 四要素: HEAD=b40e70d715b0de4f1e6d2da0536e1d2af1811b8d(=运行时尖端=基点;worktree_dirty_files=0);脚本SHA256=01e3f890…(契约登记全值);UTC=2026-11-04T09:06:00Z–09:07:48Z(108.6s);exit=**3**。
- **Gate A core 缺口=0(4→0 清零,R049 修复目标达成)**: SHCOMP/SZCI/SH_AMOUNT/CN_TOTAL_TURNOVER 全部到位(全经 EM 回落,obs=2026-11-03,lag=1≤10天窗,时效不降级);core_missing=[]、core_fail=[](报告 JSON 原样)。
- 八项 check **全部产生**,逐项判定+evidence_id 原样转录(GATEA-CHECKS-TRANSCRIPTION.txt 全表): UST_2Y/10Y/30Y=PASS(2026-11-02同日,差0.0bp≤3bp;EV-TSY-2026);BTC=NOT_VERIFIED(Coinbase日K不可达;EV-CB-BTC-USD);GOLD_F=NOT_VERIFIED(参考源不可达;EV-CB-PAXG-USD);SHCOMP=NOT_VERIFIED(新浪快照2026-11-04≠目标观测日2026-11-03;EV-SINA-SH000001);SPX=NOT_VERIFIED(FRED无2026-11-03同日观测,最近=2026-11-02;EV-FRED-SP500);WTI_F=NOT_VERIFIED(参考源不可达;EV-FRED-DCOILWTICO)。
- 复算四项: SPX=PASS/GOLD_F=PASS/HSI=PASS(均完整三期);SHCOMP=INSUFFICIENT_HISTORY(WEEK/MTD一致,YTD历史不足——china 指数 series 年窗语义无上年末基准,R049 前后同窗口语义,非本轮回归;解释性归因交审计)。
- 覆盖门槛(coverage 原样): ust_pass=3✓/market_pass=0(需≥2,未满足)/external_pass_total=3(需≥4,未满足)/recompute_pass=3✓/recompute_complete=3✓ → overall=NOT_VERIFIED(exit 3)。
- 报告产出(判定件目录内存活件): real_acceptance_20261104_1707.json/.md/.log + evidence/ 4件外部原始证据(treasury/sina/FRED×2;FRED URL 已脱敏 api_key=***REDACTED***);快照临时件随 TemporaryDirectory 清除(无存活件,与 R032 同形态;判定输出以报告+console 为证)。
- 判定件达标性(两维如实分列,裁定权属 Agent 4): R3-AC-03 两要素(core=0+八项产生)均达成;但 overall=NOT_VERIFIED(exit 3)且收盘守卫 FAIL(取值行=20261103≠20261104)→ 按 §0/R3-AC-01/02 明文「收盘守卫不过→NV 如实」,执行面取 **NV 臂**。

## ⑤ data/daily 清单(§3.5;先/后机器件+新增 SHA)

- 先=24件/后=24件(data_daily_{prerun,postrun}_inventory.txt 全量 SHA256;data_daily_round_writes.json 机器对比)。
- **新增 0、删除 0**;同日覆盖写盘 **6 件**=20261104 四源文件(R032 今日 01:1xZ 所写→本轮 08:5x–09:0xZ 重跑,采集器固有多读写盘语义): 4 件哈希变化——china_20261104.json(275a489e…→7e32e9b1…,28,680B→82,840B,指数0个→6个+成交额❌→✅)、global_20261104.json(774b389a…→3724a40c…)、global_20261104.md(0f2d1045…→84d91f76…)、rate_economy_20261104.json(26e7f11b…→23414140…);2 件重写后字节不变哈希不变——macro_20261104.json、rate_economy_20261104.md(重写以 mtime 2026-11-04 16:59/17:03 HKT 为证,内容与 R032 产物逐字节一致)。其余 18 件零触碰哈希逐一不变。

## ⑥ 偏差与如实声明

- **收盘守卫 FAIL→NV(本轮主偏差,合同预登记路径)**: china 取值行=20261103 非 20261104。机制: tushare 日配额外部先在耗尽(本轮首调 08:57Z 即「5次/天」,R032 判别结论再证,无需新判别)+EM 回落合同级截止 EM_FALLBACK_MAX_DATE='2026-11-03'(R049 冻结,在途行禁用)+本轮代码零改动(§1)。**零凑数**: 未改截止、未改阈值、未换比较日、未以任何方式伪造 11-04 行。
- AC 草案内部张力如实披露(交 Agent 4): 三态定义「PASS=执行合规+判定件达标(core=0+八项产生)」与 R3-AC-01/02「收盘守卫不过→NV」在本轮事实组合下指向不同臂(core=0+八项产生=是;守卫=不过)。执行面按更具体、更严格的守卫明文取 NV 臂;两维事实均已在④逐项列明,裁定权属 Agent 4。
- overall=NOT_VERIFIED 的构成(如实): 市场类真PASS=0(BTC=Coinbase不可达;SHCOMP=新浪11-04快照≠obs 11-03;SPX=FRED无11-03同日观测)——市场类证据缺失与 china 取值行滞后一日直接相关(SHCOMP/SPX 同为「目标观测日2026-11-03 而外部端点只有 11-04/无11-03」型日期错配;BTC/GOLD/WTI 为端点不可达,与 china 无关)。
- R032 的 global 18 nan 未复现(本轮 32/32,质量 FAIL=0)——跨日环境差异如实登记,不构成任何处置依据。
- 非核心缺失 3 项(MARGIN_BAL/SB_FLOW/SH_PE)=tushare 权限类既有状态(R007/R032 同型),非本轮回归。
- 本轮零验收参数变更/零 FIX/零备源新增/零 R006-D1 类实施(§1 代码零改动=事实: `git diff b40e70d..HEAD --stat` 仅本文件新增)。

## ⑦ CI 登记说明

CI 由操作者 CHECKPOINT 侧对最终尖端 workflow_dispatch `offline-tests`(Run ID/conclusion/headSha/时间戳落字面值登记至引擎侧 `rounds/050/W5-RERUN3-CI-dispatch-evidence.md`),不入 DEV 文件;执行方本轮零 CI 动作(不 dispatch、不改触发,R032/R049 先例;执行面白名单亦无 dispatch 权)。**预期套件数=54**(R049 基线 54,本轮 docs-only 零测试面变更)。
