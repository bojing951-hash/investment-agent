# P0-2 W5-RERUN-2 交付文档(R032;契约 IA-P0-2-W5-RERUN-2-AC-v1.0)

- 契约: IA-P0-2-W5-RERUN-2-AC-v1.0(FROZEN 2026-11-03 12:21 HKT,存档 SHA256=1f442e687c8b5a5e051ae2aea3d387dc8076a7d547c0ae22273a217db130c400)
- 分支/基点: `dev/p0-2-w5-rerun` 自基点 58d0cc1e2851022612b6bf272523101b74cfe1ae 线性追加(本轮恰 1 笔 commit=新增本文件,零 M/D)
- 执行日: 2026-11-04(UTC);证据包: /tmp/w5rerun2-evidence/IA-P0-2-W5-RERUN-2-EVIDENCE.zip
- 终局一句话: 判别实验证实**日配额在满释点后仍被外部先在耗尽**,正式重跑(判定件 attempt1_formal_20261104)exit=2、Gate A FAIL、**core 缺失 4 未清零**——补证据目标未达成,如实按 NV 臂交付(判定权属 Agent 4)。

## ① 窗口与首调时刻(UTC)+干净性依据

- 开轮 UTC=2026-11-04T00:59:08Z(`date -u` 实取);窗口下界=2026-11-04T00:14:00Z(R007 末调 2026-11-03T00:14:09Z+24h,契约锚定)。
- 判别实验首调时刻=**2026-11-04T01:07:57.461402Z**(probe_result.json `call_start_utc`,机器件)> 下界 ✓。
- 干净性依据: 开轮(00:59:08Z)至首调(01:07:57Z)之间本轮零真实 tushare 调用——本轮全部日志/报文时间轴中最早 tushare 报文即该判别首调;四源采集器的首次 tushare 报文均在判别之后(china 采集器运行窗 01:09:22Z 起,attempts/attempt1_china_20261104.meta.txt 实取)。

## ② 判别实验(R007 审计 DEFERRED-4 承接;恰 1 次真实调用)

- 脚本: /tmp/w5rerun2-evidence/experiments/probe_index_daily.py(仅存 /tmp 证据域,DEV 零代码 hunk);接口与凭证环境与采集器完全一致(`sys.path` 插入项目根→`from env_config import TUSHARE_TOKEN`→`ts.pro_api(TUSHARE_TOKEN)`,即采集器 `_pro()` 同一构造)。
- 参数(采集器字典序首指标 `000001.SH` 同参,运行时同式计算): `ts_code=000001.SH, start_date=20260101, end_date=20261104`。
- 调用窗口: 2026-11-04T01:07:57.461402Z–01:07:57.623699Z(duration 0.162s)。
- **报文全文(REJECTED,逐字,源=probe_result.json `message_full`)**: `抱歉，您访问接口(index_daily)频率超限(5次/天)，具体频次详情：https://tushare.pro/document/1?doc_id=108。`
- 判读结论: **日配额满**。DEV 侧自 R007 末调(2026-11-03T00:14:09Z)已满释 24h53m 而配额仍满 ⇒ R007 拟合的「滚动24h·DEV侧独占·计被拒」模型被本轮观察**否证**;最佳拟合=同 token 外部消耗方先在耗尽(R007 限流模型分析 §二.3 候选(b): LIVE 侧定时作业等)。按 R2-AC-04.1 只读取证范围(仅限三项),未扩 LIVE 侧查证;归因链交审计裁定。
- 凭证路径如实登记: 本轮 shell 环境 `TUSHARE_TOKEN` 为空(probe `token_present=false`,布尔登记)→ `pro_api` 走与采集器完全相同的本地凭证回落;采集报文与 R007 同型=同凭证路径。凭证明文零落盘。
- 判别结果不授权任何变更: 本轮零参数变更/零 FIX/零重构/零备源;DEV 改动恰 1 新增文件(本文件)。

## ③ 尝试时间线(逐次 UTC 起止/数据日/结果/退出码;判别实验单列不混入)

| # | 对象 | UTC 起–止(时长) | 数据日 | 结果 | 退出码 |
|---|---|---|---|---|---|
| 判别(单列) | probe_index_daily(恰1调) | 01:07:57.461–01:07:57.623(0.162s) | 序列窗 20260101–20261104 | REJECTED「5次/天」 | (记录器自身 exit 0;报文见②) |
| attempt1-china | china_market_collector.py(T1 闸门) | 01:09:22–01:16:29(427.0s) | 写 china_20261104.json | index_daily 8 调全拒(逐调报文见⑤);HSI/HSCEI(腾讯直连)✓、HSAHP(新浪直连)✓ | 0 |
| attempt1-macro | macro_collector.py | 01:09:35–01:10:18(43.2s) | 写 macro_20261104.json | 全部指标 ✅(console 尾 12 项 ✅) | 0 |
| attempt1-rate | rate_expectations.py | 01:10:29–01:12:50(140.3s) | 写 rate_economy_20261104.json/.md | ✅ | 0 |
| attempt1-global | global_market_collector.py | 01:13:18–01:13:41(23.5s) | 写 global_20261104.json/.md | 32/32 采集,其中 18 资产值=nan(NVDA/AAPL/MSFT/TLT/HYG/EEM/EZU/FEZ/EWU/EWG/EWJ/INDA/FXI/IEF/SHY/LQD/GLD/USO;全非 core;R007 同位 0 nan) | 0 |
| **attempt1-formal(判定件)** | real_data_acceptance.py(零裁量参数) | 01:17:37–01:17:41(3.7s) | 验收数据日 **20261104**(自动最新四源齐全日,lag=0) | **Gate A=FAIL,core缺失 4,exit=2**(原文见④) | **2** |

- 运行形态披露: china 以后台运行与 macro/rate/global(前台顺序)在时间上交叠(01:09:22–01:13:41 窗内);四源互不共享状态、各自 console/meta 独立留档,每源调用方式与 R007 逐字相同(`python3 scripts/<script>`,cwd=仓库根)。
- 多试状态: 判别首调即报「5次/天」=日配额满 ⇒ 依 R2-AC-03.2「配额耗尽→当日停止」,本轮**恰 1 次正式尝试**,末次=判定件,零重试零删改。

## ④ 末次判定原文+口径披露

判定件 console 原文(逐字,formal/attempt1_formal_20261104/console.log):

```
📌 验收数据日: 20261104(自动最新四源齐全日(lag=0天);来源目录/Users/cast/investment-agent-dev/data/daily)
✅ 快照: /var/folders/9f/db_l8h8s5tz45287qy9v7ml40000gn/T/tmp68yztyr6/research_snapshot_20261104.json
   MD:   /var/folders/9f/db_l8h8s5tz45287qy9v7ml40000gn/T/tmp68yztyr6/research_snapshot_20261104.md
   锚点: /var/folders/9f/db_l8h8s5tz45287qy9v7ml40000gn/T/tmp68yztyr6/anchors_20261104.json (171个)
   Gate A: FAIL | 事实 71 | 质量 {'PASS': 39, 'DEGRADED': 12, 'FAIL': 18} | core缺失 4 | 非核心缺失 5项(CHINEXT,MARGIN_BAL,SB_FLOW,SH_PE,SZ_COMPONENT_AMOUNT)
❌ 当日研究快照Gate A=FAIL(采集目录不可信或核心来源缺失)——该数据集不得通过真实数据验收
```

逐项口径披露:

- **overall**: 未产生——Gate A 非 PASS 即 `sys.exit(2)`(real_data_acceptance.py:1190-1195 冻结行为),早于综合判定;无判定行可转录,如实登记(R007 审计 L19 先例)。
- **exit**: **2**(run.meta.txt 实取)。
- **门槛计数**(EXT-BTC/外部总 PASS≥4/市场类≥2/UST 三期限/复算≥2): **未执行、未产生**(八项外部核验与复算位于 Gate A 阻断之后,console 无对应行)。
- **Gate A core 缺口状态: 4,未清零**(console 行「core缺失 4」直读;补证据目标=缺口清零,未达成)。通道归因(解释性登记,非另立计数口径): 采集侧 china 通道 index_daily 8 调全拒→a_share_indices=[]、turnover=None→SHCOMP/SZCI/SH_AMOUNT/CN_TOTAL_TURNOVER 4 项 core 缺失(与 R007 锚定二 L47 同一「缺失 4」;registry 实读 core(active)=32,china 源 core=7,其中恰此 4 项依赖 index_daily 通道,HSI/HSCEI/HSAHP 经腾讯/新浪通道在场)。
- **报告 JSON/MD**: exit=2 时零产出(冻结行为)。
- 快照临时件: 随 `tempfile.TemporaryDirectory` 清除,无存活件 → 证据包⑧类按「未产出(存活)」如实登记(转以判定件 console+四要素为证)。
- 质量分布差异(如实): 今日 {'PASS':39,'DEGRADED':12,'FAIL':18} vs R007 {'PASS':57,'DEGRADED':13,'FAIL':0};18 个 FAIL 与 global 采集日志 18 个 nan 资产**计数一致**(grep -c nan=18,机器件),成员名单见③;快照明细已随 tempdir 清除,成员级映射不可直读,如上归因供审计裁定。
- 判定件四要素: HEAD=58d0cc1e2851022612b6bf272523101b74cfe1ae(=运行时分支尖端=基点;worktree_dirty_files=0);脚本SHA256=01e3f890793f09b86f1e885da9a4eb9fc143a1638cb4a56e80e2f34a5bcb331b(=契约登记全值);UTC=2026-11-04T01:17:37Z–01:17:41Z;exit=2。

## ⑤ 配额与限流观察汇总(逐次报文语义)

| 时刻依据 | 调用 | 报文语义(原文摘录) |
|---|---|---|
| probe_result.json 01:07:57Z | 判别 000001.SH(恰1调) | 「频率超限(**5次/天**)」 |
| attempt1_china console(运行窗 01:09:22–01:16:29;采集器无逐调时间戳,时刻不推算) | 000001.SH→399001.SZ→399006.SZ→000300.SH→000905.SH→000852.SH(字典序,T1 闸门 7 次等待 58.8–60.8s 全程生效) | 逐调「频率超限(**1次/小时**)」×6 |
| 同上(成交额段) | turnover 000001.SH(tushare 通道) | 「频率超限(**1次/小时**)」;akshare 回落「amount为0，跳过」(R007 尝试1/2/3 同型) |
| 同上(非 index_daily) | moneyflow_hsgt×1、index_dailybasic×3、margin×5日窗 | 「您没有接口(…)访问权限」/「暂不可用」(权限类既有状态,R007 同型,非本轮阻断项) |

- 语义判读: 首调「5次/天」+后续全「1次/小时」与 R007 尝试1 **逐字同型**(报文优先呈现小时窗);结合满释点后首调仍满 ⇒ **外部先在消耗**最佳拟合(同 token 外部消耗方;DEV 侧无任何先行调用,时间轴为证)。
- 补证据目标结论: **未达成**(Gate A core 缺口 4 未清零);根因归类建议(权属 Agent 4): 环境性——tushare index_daily 日配额被外部先在耗尽,证据链=②判别报文+③时间轴+⑤逐调报文+R007 限流模型分析交叉。

## ⑥ R006-D1 类不重复实施声明

本轮零 FIX、零重构、零参数变更(闸门 61s/A_SHARE_INDICES 字典序/比较日/容差 0.5% 全部零变化)、零备源、零新数据源·新 token、零数据改写;R006-D1 类实施不重复(R007 已实施);DEV 改动=恰 1 新增文件(本文件),零 M/D(`git diff --name-status 基点..尖端` 可验)。

## ⑦ CI 登记说明

CI 由操作者 CHECKPOINT 侧对最终尖端 workflow_dispatch `offline-tests`(Run ID/conclusion/headSha/时间戳落字面值登记至引擎侧 `rounds/032/W5-RERUN2-CI-dispatch-evidence.md`),不入 DEV 文件;执行方本轮零 CI 动作(不 dispatch、不改触发)。预期套件数 53(契约占位符实值;本轮 docs-only 零测试面变更)。

## 附:data/daily 本轮痕迹(R2-AC-03.6)

采集前 18 件→采集后 24 件;新增 6 件(全 20261104): china_20261104.json(275a489e…)、global_20261104.json(774b389a…)、global_20261104.md(0f2d1045…)、macro_20261104.json(8531cdb2…)、rate_economy_20261104.json(26e7f11b…)、rate_economy_20261104.md(07b3c0a0…);零删除、零改写、**同日覆盖件数=0**(既有 18 件哈希逐一不变;全量 SHA256 见 data_daily_{prerun,postrun}_inventory.txt 机器件)。

---

## 补登块(R049/IA-P0-2-W5-DATASRC-B,2026-11-04;append-only)

本块登记 R032 审计 DEFERRED-1/2 两处更正,每处四要素(旧文→新文映射/依据/定位/日期);上方原文一字未动。证据包 zip 已封口不重建(R048 T4 先例),更正以本块为准;所引散件留档于 /tmp/w5rerun2-evidence/(存续期内可复核)。

### 更正①(R032 DEFERRED-1): index_daily 调数叙事

- **旧文→新文映射**:
  - 本文档 §③ 表 attempt1-china 行: 「index_daily 8 调全拒(逐调报文见⑤)」→「index_daily 7 调全拒(逐调报文见⑤);全轮含判别合计 8 次」。即修正后调数口径=**采集段 7 调/全轮 8 次**(合同更正指令「7→8」之两数)。
  - 证据包散件 CLOSING-REGISTRATION.md L21 调用台账: 「tushare index_daily: 判别 1 + 采集 8 = 9 次(全被拒;报文逐字在档)」→「判别 1 + 采集 7 = 8 次(全被拒;报文逐字在档)」。
- **依据**(机器件 attempts/attempt1_china_20261104.log 逐行): 本采集器每次 `_index_daily` 调用恰对应一行「⏳ tushare index_daily 限流间隔…等待Ns」(首调亦有等待行——进程 `time.monotonic()` 初值≈1s,61−1≈60.0s 与 L8 实测吻合)。等待行 L8/10/12/14/16/18(指数段 6 调,60.0/60.6/60.8/60.5/60.8/60.8s)+L37(成交额方案1首调,58.8s)=**7 调**;被拒报文行 L9/11/13/15/17/19(`❌`×6)+L38(`⚠️`×1)=7 拒,另 L39 为 akshare 回落「amount为0」行(非 index_daily 调用)。时长自洽: 7×≈60.5s≈423.5s+其余采集段开销≈meta 登记的 427.0s;若为 8 调则闸门等待下界≈7×60.5+1×0≈484s>427.0s,矛盾。§⑤ 表「T1 闸门 7 次等待 58.8–60.8s 全程生效」(嵌于指数行)实为全 china 运行 7 次等待之总数(SCRIPT-SHA-CONSISTENCY.txt L27-28 同口径含 L37),置于指数行内致 scope 误读,此处一并澄清: 指数段等待=6 次(60.0–60.8s),第 7 次等待(58.8s)属成交额段。
- **定位**: docs/P0_2_W5_RERUN_2_DELIVERY.md §③ 表 attempt1-china 行「index_daily 8 调全拒」与 §⑤ 表第二行(7 次等待表述);证据包散件 CLOSING-REGISTRATION.md L21、SCRIPT-SHA-CONSISTENCY.txt L27-28(后者表述本身无误,澄清其计数口径)。
- **日期**: 2026-11-04(R049 补登)。

### 更正②(R032 DEFERRED-2): 采集器 blob 引用尾笔误

- **旧文→新文映射**: 证据包散件 OPENING-REGISTRATION.md L37 「(git blob=ab626f68b4d61f18b2cba93cf78e728dc3a18b3**s**@58d0cc1;」→「(git blob=ab626f68b4d61f18b2cba93cf78e728dc3a18b3**c**@58d0cc1;」——git blob 40 位十六进制尾字符 `s`→`c`(笔误,非合法 hex)。
- **依据**: `git rev-parse 58d0cc1:scripts/china_market_collector.py` 实取=ab626f68b4d61f18b2cba93cf78e728dc3a18b3c(2026-11-04 R049 开轮前复演;该文件自 50be9c7(W5-RERUN T1)后零改动,58d0cc1 与 cebc4af 同 blob)。同文件 L35-36 的文件级 SHA256=a1599ab992ef87d61811c7b2f6d5723399a68114662c17437ded79e064176784 无误,仅 L37 的 git blob 尾字符笔误。
- **定位**: 证据包散件 /tmp/w5rerun2-evidence/OPENING-REGISTRATION.md L37(副本随 zip 内 OPENING-REGISTRATION.md 同文)。
- **日期**: 2026-11-04(R049 补登)。
