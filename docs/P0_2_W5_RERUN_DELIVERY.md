# P0-2 W5-RERUN 交付文档 — 通道限流治理(方案A) + 正式重跑(承接 F2-AC-03)

契约: IA-P0-2-W5-RERUN-AC-v1.0(FROZEN 2026-11-02,用户批准方案A+操作者代批)
分支: `dev/p0-2-w5-rerun`(自 `dev/p0-2-w5-fix3`@`1ddfb65ec78f4358b7a004be8ef5d8916ba0f052` 切出)
执行窗口: UTC 2026-11-02T16:24Z – 2026-11-03T00:4xZ
证据包: `/tmp/w5rerun-evidence/IA-P0-2-W5-RERUN-EVIDENCE.zip`(SHA256 见§10,轮末不删)

---

## 0. 一句话结论

T1 限流治理(方案A,61s 间隔)已实施并全程生效;T2 正式重跑共 3 次采集尝试 + 2 次正式验收运行,**末次判定件 exit=2/Gate A FAIL**(core缺失4,全部为 tushare index_daily 通道指标)——tushare 限流实测语义(接口级1次/小时+5次/天且被拒调用计数)超出本合同冻结时点实证的"1次/分钟",方案A解除分钟窗不足以解除小时窗/日配额;根因属外部源配额环境,NOT VERIFIED 分流建议权属 Agent 4。EXT-BTC 独立诊断 PASS(0.02%)。R006-D1(范围E)已实施。

## 1. 开轮登记(固定基线实取)

- 基线: `git rev-parse dev/p0-2-w5-fix3` = `1ddfb65ec78f4358b7a004be8ef5d8916ba0f052`(与合同注入短SHA `1ddfb65` 一致;R006 审计 gh run 记录末位 `f052` 吻合)
- `real_data_acceptance.py` SHA256(开轮登记,全程不变,收轮复核一致):
  `01e3f890793f09b86f1e885da9a4eb9fc143a1638cb4a56e80e2f34a5bcb331b`(前缀 `01e3f890` ✓)
- 开轮 `git status`: clean(工作树零脏文件)
- `data/daily/` 开轮全清单(15文件+SHA256): 见证据包 `data_daily_opening_inventory.txt`(UTC 2026-11-02T16:34:12Z)
- `git ls-remote origin` 实取(收轮 2026-11-03T00:1xZ 复核,逐项与基线一致**零变化**):
  - main `50b5d13db6c477084c6f4b3944b7bd08a8e329d6` ✓(P0-1 封版)
  - dev/p0-2-w1 `69d7fc71f4ac05d3e5323cb5e270585ec48d6f97` ✓ / w2 `14fe6e57004b46ede889a190952b373d51eb4f76` ✓ / w3 `497b02c7b770d4eadb9086d453fea14d275bd4c9` ✓ / w4 `7c004c65e98e54a519b2a647632c74b6b83b1bcd` ✓
  - dev/p0-2-w5 `10207929c8d505845ac30f8af9a742b124b0f4d5` ✓ / fix2 `02f1bade0688fed6afd61aa8973bc326c3a75c1d` ✓ / fix3 `1ddfb65ec78f4358b7a004be8ef5d8916ba0f052` ✓
  - `dev/p0-2-w5-rerun` 开轮不存在(origin 上新建,非 force 首推,尖端=本分支尖端)

## 2. T1 通道限流治理(方案A / 范围D / R-AC-01)

### 2.1 改造内容与生效范围

- **间隔值: `INDEX_DAILY_MIN_INTERVAL_SECONDS = 61`(≥61s,满足合同下限)**
- 实现: 新增模块级 `_index_daily(**kwargs)` 调用闸门——全局单调时钟(`time.monotonic()`)保证**任意相邻两次 index_daily 调用**(无论成败、无论所在函数)间隔 ≥61s;已超出间隔的调用不额外等待。`fetch_a_share_indices` 循环 6 只 + `fetch_turnover` 2 只(000001.SH/399001.SZ)共 8 个调用点全部经闸门发起,跨函数相邻对(循环末调→成交额首调)同样受闸门覆盖(尝试3实证: 该对实际间隔=61.0s,等待37.5s+23.5s间隔处理)。
- 理由备案: 用户批准的路径①第一分支(≥61s间隔),对症 FIX3 §六附则实证链"字典序第2只(399001.SZ)+1次/分钟+无备源"结构性死路;最小改动、零新依赖/凭证/付费。
- **零变化项(R-AC-01.1,逐项自检)**: `A_SHARE_INDICES` 清单内容与字典序(000001.SH→399001.SZ→399006.SZ→000300.SH→000905.SH→000852.SH)未动;tushare 接口选择(`_pro().index_daily`,参数原样透传)未动;备源回落逻辑未动;import 依赖清单未动(零新增import,`time` 为既有导入)。
- 行为备注(如实): 本运行环境下 `time.monotonic()` 表现为进程相对时钟,故每次进程首调也会等待约60s(尝试1首调等待60.0s/尝试3等待57.6s)——方向保守(只会更慢不会更快),不影响"相邻调用间隔≥61s"的合同语义;尝试内相邻调用间隔实证≈61.0s(三次尝试共21次调用全部打印闸门等待行)。

### 2.2 diff 全文(`git diff 1ddfb65..50be9c7 -- scripts/china_market_collector.py`;证据包 `collector_T1_diff_full.txt` 同文)

```diff
diff --git a/scripts/china_market_collector.py b/scripts/china_market_collector.py
index 19d5db7..ab626f6 100644
--- a/scripts/china_market_collector.py
+++ b/scripts/china_market_collector.py
@@ -38,6 +38,29 @@ def _pro():
         _pro_client = ts.pro_api(TUSHARE_TOKEN)
     return _pro_client
 
+
+# ============ 方案A限流间隔(W5-RERUN T1/范围D, 2026-11-03) ============
+# 实证(FIX3 §六附则/操作者2026-11-01实测): tushare index_daily 对同账号相邻
+# 快速连发按"1次/分钟"限流——A_SHARE_INDICES 字典序第2只(399001.SZ)在无
+# 间隔连发下必然"频率超限",且SZCI无备源→结构性死路(任何零代码重跑必缺SZCI
+# →Gate A core FAIL)。本模块所有 index_daily 调用统一经 _index_daily 发起:
+# 全局单调时钟保证任意相邻两次调用(无论成败、无论所在函数)间隔
+# ≥ INDEX_DAILY_MIN_INTERVAL_SECONDS;已超出间隔的调用不额外等待。
+# 清单/字典序/接口选择/参数/备源回落/import 依赖零变化(仅加间隔)。
+INDEX_DAILY_MIN_INTERVAL_SECONDS = 61
+_index_daily_last_ts = 0.0
+
+
+def _index_daily(**kwargs):
+    """index_daily 调用闸门(方案A): 相邻调用间隔≥61s;接口与参数零变化。"""
+    global _index_daily_last_ts
+    wait = INDEX_DAILY_MIN_INTERVAL_SECONDS - (time.monotonic() - _index_daily_last_ts)
+    if wait > 0:
+        print(f"  ⏳ tushare index_daily 限流间隔(方案A≥61s): 等待{wait:.1f}s")
+        time.sleep(wait)
+    _index_daily_last_ts = time.monotonic()
+    return _pro().index_daily(**kwargs)
+
 # A股指数列表
 A_SHARE_INDICES = {
     '000001.SH': '上证指数',
@@ -109,7 +132,7 @@ def fetch_a_share_indices():
         try:
             # 第七轮: 单次拉取年初至今全序列(原为近10天+年初两次调用),
             # 附加原始series供事实引擎统一口径计算(周/MTD/YTD=期前收盘基准)
-            df_year = _pro().index_daily(ts_code=code, start_date=start_year, end_date=end_date)
+            df_year = _index_daily(ts_code=code, start_date=start_year, end_date=end_date)
             if df_year is None or len(df_year) == 0:
                 print(f"  ⚠️ {name}({code}): 无数据")
                 continue
@@ -364,14 +387,14 @@ def fetch_turnover():
     try:
         today = datetime.now().strftime('%Y%m%d')
         # 查最近5个交易日
-        df = _pro().index_daily(ts_code='000001.SH', start_date=(datetime.now() - timedelta(days=10)).strftime('%Y%m%d'), end_date=today)
+        df = _index_daily(ts_code='000001.SH', start_date=(datetime.now() - timedelta(days=10)).strftime('%Y%m%d'), end_date=today)
         if df is not None and len(df) > 0:
             latest = df.sort_values('trade_date').iloc[-1]
             sh_amount = float(latest.get('amount', 0))  # 千元
             sh_date = str(latest['trade_date'])
 
             # 同时获取深证成指成交额
-            df2 = _pro().index_daily(ts_code='399001.SZ', start_date=(datetime.now() - timedelta(days=10)).strftime('%Y%m%d'), end_date=today)
+            df2 = _index_daily(ts_code='399001.SZ', start_date=(datetime.now() - timedelta(days=10)).strftime('%Y%m%d'), end_date=today)
             sz_amount = 0
             if df2 is not None and len(df2) > 0:
                 latest2 = df2.sort_values('trade_date').iloc[-1]
```

改动 hunk 清单: ①新增闸门常量+函数(纯新增);②`fetch_a_share_indices` 循环内 1 处调用改经闸门;③`fetch_turnover` 2 处调用改经闸门。全部 hunks ⊆ 限流间隔治理。

### 2.3 本地全套件(R-AC-01.3,T级工程自检)

- CI 同构 53 套件逐套件直跑(`tests/test_*.py`,排除 test_glm_live): **52 套件 exit=0;`test_p4_fixes` exit=1(39通过/4失败)**
- 逐套件退出码全文: 证据包 `local_suite_summary.txt`;逐套件日志 `suite-logs/*.log`(53份)
- 失败项与 T1 改动无关性: 4 失败项均为 FRED 月度序列提取类(环境性数据面);**基线对照**——还原至 `1ddfb65` 原状复跑 `test_p4_fixes`,同样"39通过/4失败"逐字一致(`suite-logs/test_p4_fixes_at_baseline_1ddfb65.log`,带 provenance 头)⇒ 先在于本地环境差异(本地 python3.9.6 vs CI 3.11,历轮已登记),非 T1 引入;CI 侧该套件在 fix3 基线为绿(run `41334594465`,53/53)。
- **基线日志更正登记(如实)**: 首轮会话(11-02T16:2xZ)声称的基线对照日志当时未落盘(引用失实);续行会话(11-03T00:3xZ)以 `git checkout 1ddfb65 -- scripts/china_market_collector.py` 临时还原复跑、即时恢复 T1 版本(worktree 验证 clean)补齐该日志,复跑结果与首轮所述逐字一致(39/4)——结论成立,引用现在有据;更正全文见证据包 `T1_local_suite_baseline_comparison.txt` 文末"更正登记"。
- 既有套件零删除/零跳过/零弱化;套件对 collector 仅测纯函数,不触 index_daily 路径;全套件无超时(最慢 7.7s)。

## 3. T2 正式重跑——尝试时间线(R-AC-02;全部尝试留档于证据包 `attempts/`+`formal/`,零删改)

| # | label | UTC 起止 | 数据日/产物 | 结果 | exit |
|---|---|---|---|---|---|
| 1 | attempt1_china | 11-02T16:36:58–16:44:06 | 20261103/china(新建) | 采集器正常完成;**A股指数0**;7调全拒: 首调"5次/天",其余6调"1次/小时";港股2✅/AH✅ | 0 |
| 2 | attempt1_macro | 11-02T16:49:52–16:51:26 | 20261103/macro(新建) | 28项全✅(UST_2Y 4.61/10Y 4.98/30Y 5.32,obs 2026-10-29) | 0 |
| 3 | attempt1_rate | 11-02T16:51:30–16:52:01 | 20261103/rate_economy(新建) | 联储期货10合约+实体经济6项全✅ | 0 |
| 4 | attempt2_china | 11-02T17:47:09–17:54:17 | 20261103/china(**覆盖**) | 距尝试1末调63分钟起跑(小时窗清空判别);逐字同型全拒;A股0 | 0 |
| 5 | attempt1_global | 11-02T21:05:29–21:05:49 | 20261103/global+md(新建) | 32/32资产✅(美东收盘后取数;SPX 7541.40 obs 11-02;BTC 78248.45 obs 11-01完结日,在途日11-02剔除,close_meta在档) | 0 |
| 6 | attempt1_formal | 11-02T21:06:24(+0.6s) | 20261103(自动四源齐全日) | **Gate A FAIL(core缺失4)**→exit 2 | **2** |
| 7 | attempt3_china | 11-03T00:06:59–00:14:09 | 20261103/china(**覆盖**) | UTC午夜后7分钟判别起跑: 首调仍"5次/天"(**UTC日历假说否证**);调2/调7"1次/分钟"(61s间隔下RTT>1s时分钟窗未清),调3-6"1次/小时";A股0 | 0 |
| 8 | **attempt2_formal(判定件)** | **11-03T00:18:52–00:18:54** | **20261103** | **Gate A FAIL(core缺失4)→exit 2**(原文见§4) | **2** |

非正式诊断(不充当正式证据,如实标注): DIAG-EXT-BTC R1(11-02T21:06:34Z)、R2(11-03T00:19:55Z,含范围E两字段);外部源探针3次(11-02T21:06:50Z/21:37:42Z/11-03T00:20:13Z)。

**同日覆盖前置件链(全部先入证据包)**: `data/daily/china_20261103.json` 由#1新建(96ad6c9a…)→#4覆盖(前置件96ad6c9a…在 `attempt1_overwrite_precursor_archive/`,覆盖后 dc15102c…)→#7覆盖(前置件 dc15102c… 在 `attempt2_overwrite_precursor_archive/` 与 `attempt3_overwrite_precursor_archive/`,覆盖后 abdeb5f0…)。macro/rate/global 的 20261103 文件均为开轮不存在的新建产物(开轮清单为证)。

**停止尝试依据(合同 R-AC-02.2)**: 尝试3按预登记判别计划(限流模型分析§五.5)于 UTC 午夜后执行,首调仍"5次/天"→按§五.4 预登记分支"当日停止尝试、如实交付";未执行尝试4(滚动24h模型下配额至约 11-04T00:14Z 后才可能满释,超出本轮窗口;继续连发只会刷新被拒计数使窗口更晚释放)。

## 4. 末次正式运行判定原文与口径披露(R-AC-02.3/02.4)

**判定件 = attempt2_formal_20261103**(证据包 `formal/attempt2_formal_20261103/`,console.log+run.meta.txt):

- HEAD= `50be9c7d19b66f29a305449e84f2cd436fd7a3d2`(=运行时分支尖端,其后仅交付文档回填 commit)
- 脚本 SHA256= `01e3f890793f09b86f1e885da9a4eb9fc143a1638cb4a56e80e2f34a5bcb331b`(零修改,=开轮值)
- UTC: 2026-11-03T00:18:52Z–00:18:54Z;**exit_code=2**;worktree_dirty_files=0
- INPUT-SNAPSHOT 四源 SHA(判定件实际输入):
  - china_20261103.json `abdeb5f0cfa441b92c9b90875955845c38ed6e9f685ddeeff806567e4e008e77`
  - global_20261103.json `795f8193ca6219b06290627a55172a5fad42c5e980972ebe86717e089fc2b16a`
  - macro_20261103.json `51e79e80a323a6fd5b0ec76cde3ddb25d33ff48e41a6889143b30d060ac744a1`
  - rate_economy_20261103.json `4e040291706192a98f8b821d545ffcee09af86f542e66026c9a12d681cbc7cc7`

**console 原文(全文在档,此处逐字)**:

```
============================================================
✅ 真实数据验收(W5版) — 独立外部来源 + 独立复算 + 三态综合
============================================================

📌 验收数据日: 20261103(自动最新四源齐全日(lag=0天);来源目录/Users/cast/investment-agent-dev/data/daily)
✅ 快照: /var/folders/…/T/tmp1u7vfhoe/research_snapshot_20261103.json
   MD:   /var/folders/…/T/tmp1u7vfhoe/research_snapshot_20261103.md
   锚点: /var/folders/…/T/tmp1u7vfhoe/anchors_20261103.json (171个)
   Gate A: FAIL | 事实 71 | 质量 {'PASS': 57, 'DEGRADED': 13, 'FAIL': 0} | core缺失 4 | 非核心缺失 5项(CHINEXT,MARGIN_BAL,SB_FLOW,SH_PE,SZ_COMPONENT_AMOUNT)
❌ 当日研究快照Gate A=FAIL(采集目录不可信或核心来源缺失)——该数据集不得通过真实数据验收
```

(路径内临时目录 UUID 仅为排版缩略;console.log 原文为全路径。)

**口径披露(判定=未达标,逐项如实)**:

- overall=**FAIL**(exit=2)——非 PASS/exit=0。阻断点=Gate A core缺失4:`SHCOMP`/`SZCI`/`SH_AMOUNT`/`CN_TOTAL_TURNOVER`(注册表 active core 全集33项逐一比对得出),四者全部依赖 tushare index_daily 通道(SHCOMP/SZCI←fetch_a_share_indices;SH_AMOUNT/CN_TOTAL_TURNOVER←fetch_turnover),即本轮改造对象通道的限流残余阻断。
- **八项外部核验(EXT-UST-2Y/10Y/30Y、EXT-BTC、EXT-GOLD-F、EXT-SHCOMP、EXT-SPX、EXT-WTI-F): 全部 NOT EXECUTED(未执行)**——脚本固有次序: Gate A 阻断即 `sys.exit(2)`,八项与复算均不运行、不产出报告 JSON/MD(两次正式运行同一行为;此为 `01e3f890` 版脚本的冻结行为,零修改)。故八项 check_id/判定/evidence_id 无法逐字转录——不存在被产出的判定行,如实登记为"未执行(NOT EXECUTED, Gate A 前置阻断)",不以任何构造行冒充。
- 门槛计数: 外部核验总 PASS=0/4(NV)、市场类 PASS=0/2(NV)、UST 三期限=未执行(无从判定"退化"与否)、EXT-BTC=未执行(正式件内);均非 PASS。
- 辅助工程诊断(非正式件,如实标注属性): EXT-BTC 独立诊断(§6)=PASS 0.02%;Treasury 2026-10-29 行在场且 UST 值逐字一致(探针);FRED SP500 最新 obs=2026-10-30(至收轮探针,若 Gate A 通过 SPX 同日比对亦将 NV)、FRED DCOILWTICO 最新=2026-10-27。

## 5. tushare 限流模型与根因分析(全文见证据包 `TUSHARE-LIMIT-MODEL-ANALYSIS.txt`,三轮尝试21次调用实证)

1. **日配额(5次/天)窗口 ≠ UTC日**(尝试3首调于 UTC 11-03 00:07Z 仍"5次/天");最佳拟合=**滚动24h且被拒调用计数**(与 FIX3 6次拒绝→尝试1即满、每轮被拒刷新窗口的全时间线相容)⇒ 本轮窗口内无成功可能(若模型成立,至 11-04T00:14Z 后才可能满释)。
2. **接口级小时窗对被拒调用打开**(三次尝试独立实证: 全新code首调亦报"1次/小时",其前1小时内唯一事件=上一被拒调)。
3. **分钟窗实测边界**: 61s(请求→请求)在 RTT>1s 时响应→下一请求实际<60s,尝试3调2/调7报"1次/分钟"(尝试1/2同位置报"1次/小时")——61s 间隔"通常有效但不保证"清分钟窗;更长间隔属参数变更,不在本轮授权内。
4. **结论**: 方案A(≥61s)已正确实施并全程生效,但冻结时点实证语义为"1次/分钟"(FIX3/操作者2026-11-01实测),现测语义=**接口级1次/小时+5次/天(计被拒)**——限流语义变化属外部源环境事实,解除分钟窗不足以解除小时窗/日配额;备源/换接口/改清单均未授权。**根因归类建议=环境性(外部源配额),触发§四 NOT VERIFIED 分流;分流终裁权属 Agent 4。**

## 6. EXT-BTC 独立工程诊断(FIX3 R2 同型,非正式验收产物)

- R1(11-02T21:06:34Z)与 R2(11-03T00:19:55Z,含范围E两字段)均: 我方 BTC close=78248.45(obs 2026-11-01,完结UTC日,close_meta 在档)vs Coinbase 同日 78230.55 → 偏差 0.02% ≤0.5% → **check_btc=PASS**;R2 展示 `http_status: 200` 与 `body_sha256: b3b4572f…`(与独立复算一致)。
- 如实披露: R1/R2 的 Coinbase body sha256 不同(517328f9…/b3b4572f…)——2026-11-02蜡烛在 R1 时点为在途日(收盘值漂移)、R2 时点已完结;两次检查仅用 obs 日 2026-11-01 蜡烛,该蜡烛值 78230.55 两次一致,判定不受影响。

## 7. R006-D1 实施声明(范围E)

**已实施**。EXT-BTC 诊理工具(证据包 `diag_ext_btc.py`)补齐抓取成功时 `status_code`/`sha256` 两个展示字段: 输出 `coinbase http_status`(取自 `_evidence` 的 `http_status`)与 `coinbase body_sha256`(取自 `body_sha256`),另保留独立复算行互证;该脚本其余逻辑零改动(diff 为两字段展示的纯新增;工具属 /tmp 证据域,不涉 DEV 生产代码)。R2 诊断输出(§6)即含两字段。

## 8. CI 登记说明(操作者 CHECKPOINT 侧)

本交付不含任何 CI 动作(执行方零 dispatch、零触发改动、不以本地 pytest 冒充;本地53套件为 T 级工程自检)。最终尖端绿 CI 由操作者在 CHECKPOINT 停点对 `dev/p0-2-w5-rerun` 最终尖端 workflow_dispatch `offline-tests` 并将 Run ID/conclusion/headSha/时间戳登记至轮次档案 `*-evidence.md`(R-AC-03;不入 DEV 文件)。

## 9. 范围/隔离/冻结纪律自检(R-AC-04)

- `git diff --name-status 1ddfb65..尖端`: 仅 `M scripts/china_market_collector.py`(范围D)+ `A docs/P0_2_W5_RERUN_DELIVERY.md`(范围A);其余代码/测试/workflow/配置零 hunk;`data/daily` 为 gitignored(范围C,开/收轮全清单+覆盖前置件覆盖)。
- 运行时 `real_data_acceptance.py` SHA256 全程=`01e3f890…b331b`(开轮/两次正式运行 meta/收轮复核四处一致)。
- 分支自 fix3@`1ddfb65` 切出,线性 commit(T1→交付文档回填),无 merge main/force push/reset --hard/amend;封版与固定尖端 ls-remote 实取逐项一致(§1)。
- LIVE 零写入、launchd 零改动;只读隔离三项开轮(16:24–16:58Z)与收轮(00:21–00:23Z)各一次: LIVE 脚本 SHA=`f9ca189c…`(≠DEV,两次一致)、"RERUN"在 LIVE 0 命中(两次)、launchd 零 DEV 引用(两次)。
- 不重开已闭工作包;无 P0-3/P1;无历史回补;无新增资产/采集器/付费源/凭证(方案B未实施——不在授权内);历史快照(20261101/20261102 全部文件)收轮与开轮清单 SHA 逐字节一致;R004/R005/R006 DEFERRED 未触碰(明文采纳的 R006-D1=范围E 已实施,§7)。

## 10. 证据包登记

`/tmp/w5rerun-evidence/IA-P0-2-W5-RERUN-EVIDENCE.zip`(轮末不删;操作者归档供 Agent 4)

- zip SHA256 与条目清单: 装配后补登(见本文件末行"zip 装配登记");包内含本交付文档装配前版本(自指环以补登行解,历轮既定做法)。
- 必含项对照: collector diff 全文✓(§2.2+`collector_T1_diff_full.txt`)/诊理 diff 与前后对比✓(`diag_ext_btc.py` R2版+R1/R2 输出)/全部尝试日志+meta+退出码✓(`attempts/`8组+`formal/`2组,判定件显著标注于 `formal/` 目录与本文§4)/末次 INPUT-SNAPSHOT 四源 SHA✓(§4)/八项结果及关联=未执行披露✓(§4)/开收轮清单✓/本地全套件逐套件退出码✓/隔离三项×2✓/SHA256SUMS✓/未验证清单✓(`UNVERIFIED-LIST.txt`)/最终尖端 SHA✓(§11)。

## 11. 最终尖端 SHA(commit 后回填)

- T1 commit: `50be9c7d19b66f29a305449e84f2cd436fd7a3d2`
- 交付文档回填 commit 与最终尖端全SHA: **见文末补登行**

## 12. 差异清单(相对本轮提示词注入基准)与待裁决事项

- 注入的"本轮验收条件"与附录A合同正文一致核对: 无实质差异(仅排版/分段)。
- 差异1(时序): 本轮执行跨两个会话片段(UTC 11-02T16:24Z 开轮→11-02T21:38Z 暂停→11-03T00:04Z 续行),尝试1/2与尝试3/判定件间隔约2.5小时;全部产物连续留档于同一证据目录,时间线无缝。
- 差异2(工程细节): 本地 `time.monotonic()` 表现为进程相对时钟→每进程首调亦等待约60s(§2.1 行为备注;不影响合同语义,方向保守)。
- 待 Agent 4 裁决事项:
  1. 末次判定件 exit=2/Gate A FAIL 的根因归类(本方建议: 环境性→NOT VERIFIED 分流,证据链§5;备选解释与不相容性分析见限流模型分析§五)。
  2. 方案A在实测"1次/小时"语义下结构性不足的后续路径(更长时间窗重试/方案B备源/其他)——均超出本轮授权,需用户决策+另拟合同。
  3. R-AC-03 绿 CI(操作者 CHECKPOINT dispatch 后核验)。

---

### zip 装配登记(装配后补登)

- zip SHA256: `efc9543c9d55e5343dc6480c471be1eeb3798bd72a7781871b521d96c637bf2e`
- zip bytes: 233845;条目数: **94**(含 SHA256SUMS;含 §2.3 更正后的基线日志
  `test_p4_fixes_at_baseline_1ddfb65.log` 与更正登记版对照文件)
- 自指环处置(历轮既定做法): 包内 `P0_2_W5_RERUN_DELIVERY.md` 为本登记行
  补登前的装配版(v2);本行与最终尖端补登行为仓内终版(v3)内容,不入 zip;
  zip 本身不因补登重建(SHA 以上值为准)。
- 交付文档回填 commit #1(zip 与本节登记载体): `1001df6258aeabdb2442157d0d2497ea7343aef9`
- 最终尖端(本行所在 commit = 交付文档回填 commit #2,唯一目的=闭合 #1 遗留的
  "见下"悬空引用并声明最终尖端归属;其后再无任何 commit): commit 无法自含自身
  全SHA,最终尖端全SHA 以 `git rev-parse dev/p0-2-w5-rerun`(=origin 同名分支,
  非 force 推送)实取为准,并登记于 stdout 自述报告显著位置(合同 T3)。
  判定件运行时刻 HEAD=`50be9c7d19b66f29a305449e84f2cd436fd7a3d2`(§4/R-AC-02.3);
  #1/#2 两笔均为其后合法的交付文档回填 commit。
- 收尾会话(UTC 2026-11-03T01:5xZ 前后)第三次 DEV/LIVE 隔离三项只读取证:
  LIVE 脚本 SHA=`f9ca189c…`(≠DEV,与开/收轮一致)、"RERUN"在 LIVE 0 命中、
  launchd 零 DEV 引用(散件 `DEV-LIVE-ISOLATION-FINAL.txt` 于证据目录,zip 已
  封配不重建,故不入 zip);`data/daily` 12 个 json 收轮后复扫与收轮清单逐字
  一致(`data_daily_final_check.txt`,同上散件属性)。
