# R8 独立验证报告 — AC7 真实端到端验收波(dev/rd-r7-ac7-e2e @ dae5a41)

> 验证时间: 2026-11-12。验证席: 独立 general-purpose agent(与开发席零上下文共享)。
> 环境: dev 树 main@a22a2b7 + 原件 /tmp/ac7-wt(dae5a41)双源;独立复算脚本不 import 项目代码;临时产物均在 /tmp/r8-verify。
> 两树工件哈希对账: 快照 v2、QB 短档/长档、ac7_r7 草稿逐字节一致。
> 终判: **零 BLOCKER**(合并门开);数值面单项 FAIL(ZQ−DFF),方向/量级/结论不变。

## 第1节 数值复算 — FAIL(单项:ZQ−DFF)/其余全部 PASS

- **ZQ_F1−DFF 利差: 声称 +0.295pp,复算 = +0.305pp → FAIL**。快照 facts: ZQ_IMPLIED_AVG=4.185(@11-11)、DFF=3.88(@11-09,v1/v2 两版及原始 rate_economy_20261112.json 三处一致);4.185−3.88=0.305。原始采集文件自带计算字段 `"diff_from_current": 0.305`。错误数值在 QB-001 归档出现 5 处(§01/M1/§05/S1/§11),其中 §11 写出显式算式 "ZQ_IMPLIED_AVG 4.185−DFF 3.88=+0.295pp"——减法本身算错。成因推断: 上一面 QB-032 的 +0.215(4.095−3.88,该面算术正确)+ 手算增量 0.08 递推而未重减(实际增量 +0.09)。影响面: 方向与量级结论全部不变(S1 边缘触发区间 [+25,+50)bp 仍命中,M1"走阔"成立);错误仅存在于 gitignored 归档数据,dae5a41 提交的 docs 内容经 grep 零命中 0.295(合并面干净)。**处置: 更正评注 QB-20261112-001-C1 随行+草稿五处修正(操作者已落)。**
- **PPI−CPI 剪刀差: PASS**。facts CN_PPI_YOY=5.0、CN_CPI_YOY=0.9(均@2026-09-30,tushare_pro),5.0−0.9=4.10pp=声称 +4.1pp。
- **SPX CAPE=40.71 且 z=+3.00: PASS**。fact 值 40.710609@2026-10-01;series_store SPX_CAPE n=1750(1881-01→2026-10,即 QB-001 §07 自述"145 年窗,均值 17.8/σ 7.6"口径);复算 mean=17.804、σ_pop=7.638 → z=(40.71−17.804)/7.638=2.999≈+3.00;分位(≤当前值占比)=98.9% 与声称逐位一致。
- **金油比 45.63: PASS(核心量精确)**。GOLD_F 4013.4/WTI_F 87.96=45.628(11-11 收盘)。必须按日期 join(两序列在 2018-01 起错位 1 日,位置 zip 会引入系统误差);join 后 n=2513,剔 2020-04-20 负油日(WTI=−37.63,快照内仅 1 日,档内写"n=2"略过计)。
- **10 年分位 80.1%: PASS**。复算 80.06%(中位 26.66、p90 53.26,与声称 26.7/53.3 逐位吻合)。
- **12 个月压缩 −32.3%: PASS(精确)**。锚点=日历 2025-11-11(恰为第 252 个交易日前),比值 67.44 → (45.63−67.44)/67.44=−32.34%。
- **滚动 60 相关 −0.3263: PASS(精确)**。简单收益率口径复算 −0.3263。
- **n=6 与 Episode 前视: PASS(全中)**。60 日窗压缩≥25% 不重叠前向扫得 7 段,末段(2026-06-18..2026-09-15)因前视 63 交易日不足被剔 → n=6;四项前视中位全部精确复现: 金油比 −0.91%、WTI −1.17%、SPX +8.45%、VIX −18.61%。
- 次要不吻合(入 MINOR): 全窗 pearson 声称 +0.022,复算 +0.057(date-join)或 +0.005(位置配对),三口径均"近零"定性成立但精确值未复现。

## 第2节 档完整性 — PASS

- 10/10 份(QB-20261112-001..005 × 短档+.research-full)全部 JSON 可解析;短档 snapshot_id 全绑 research_snapshot_20261112_v2;mode=B、ir_stage=executed;长档 record_type=research_full_v1。
- **QB-002 17 档/15 机构: PASS**。答案表 V-1001..V-1011+V-1101..V-1106=17 行;与观点库实证一致: data/institutions/views/ 17 文件=17 唯一 view_id,15 唯一机构(MSIM×3),quarantined=0,schema 全 1.1。
- **"上游通胀机构面空白": PASS**。17 份观点档 blob 全文 grep "PPI" 零命中,无一机构覆盖 PPI;QB-003 归档同口径声明(无一假设以 CN_CPI/PPI 为 metric_ref)。
- **QB-003 计数: PASS(以 /tmp/ac7-wt 原件为准)**。VP sidecar 17 件(as_of=20261112,B 面 snapshot=v2): B 面 rows=143、非零移动=86(口径=since_publish n_sessions_between>0,利率类走 pp/bp_change 不走 pct,故非 49)、机械判定=23=11 against/5 supports/7 neutral(逐判定行复数一致);C 型 133=96 NOT_MACHINE_VERIFIABLE+28 NOT_YET_TESTABLE+5 UNPARSEABLE+4 no_forecast(四分解逐项复现)。
- QB-001 十三节 01-13 全在场无空置。

## 第3节 诚实面 — PASS

- (a) n=6 拒外推原文在档: QB-004 §二 "n=6 且 Episode 选择与油冲击事件相关(选择偏差),不得作为方向预测;相似≠因果";§四.2 "n=6 禁外推";§三 全条件句+证伪指标(BEI>2.6 或比值跌破中位 26.7)+观察钟 2026-12。
- (b) S8 披露在三处: report.md 步骤台账 "[OK |语义✗] S8_grounded_qa";report.json notes "问题未词面命中任何指标(零模型不做语义翻译)…接地问答步骤仍如实作答/拒答";dae5a41 CURRENT_STATE.md "S8=诚实 unmapped:接地问答仅支持四类利率问题"。精确语义: S8 非"跳过"而是 executed+unmapped 诚实拒答(run_ok=False 如实记)。
- (c) 反刍检查: PASS(决定性)。全库 178 个既有档(QB-20261112 之前)grep "金油比" 零命中,该词仅出现于 QB-20261112-004;金/油同现的 6 份旧档均为资产列举/传导链场景,无一问过比值本题;QB-004 自述提问依据(changes 面落差+compare 滚动相关)与 v2 快照可溯。
- (d) QB-005 "零Key矩阵问题": 非 AC7 四任务之一;为既有零Key矩阵测试的例行落档(库内同题历史档共 150 份,QB-20261109-009 起逐日),结构一致、两树一致、无密钥,合规无害。

## 第4节 Gate A 复算 — PASS

用项目自身代码 research_provenance.recompute_gate_a(从 facts+注册表重算,不信任快照声明字段)对 v2 复算: effective=DEGRADED、core_missing=[]、core_fail=[]、duplicates=[]、illegal_quality=[],与存储 gate_a 逐字段一致。DEGRADED 成因: noncore_missing=5(BUND_10Y/BUND_2Y/CN_OMO_7D/CN_SF_FLOW/JP_CPI_TOKYO_YOY,均注"来源文件在场而指标缺席(采集遗漏)")+noncore_degraded=12(观测日陈旧类)。附: 事实 103、质量计数 {PASS:72, DEGRADED:13, FAIL:0} 与 docs 声称逐位一致。

## 第5节 干净 clone 测试 — PASS

真 git clone @dae5a41,按 CI 官方口径跑研究面 11 套件: **339 判定 0 败**——c9_p4_research_map 31/0(即声称的"31 判定 0 败"套件)、rd_r2_orchestrator 11/0+1按设计跳过、archive_snapshot_binding 13/0、research_full_sidecar 35/0、c9_source_verifier 42/0、c9_verifier_modes 57/0、charter8_view_verifier 41/0、charter8_view_store 27/0、charter8_views_cli 19/0、charter8_verifier_cli 17/0、snapshot 46/0。另: p0_baseline_lock_equivalence 在真 clone 31/0 绿,证实开发席"worktree 清单断言=环境性 FAIL"的解释。全套 129 未重跑(docs-only diff,合理)。

## 第6节 红线检查 — PASS

git show dae5a41: 仅 4 文件(CURRENT_STATE +32/FINAL_ACCEPTANCE/ITERATION_LOG/RESUME),与声称一致;diff 全文 grep glm/zhipu/bigmodel/deepseek=0、/Users/cast=0。归档与快照密钥抽查: QB-20261112 全部 10 档 0 个 sk- 前缀/40位 hex/64位 hex 串;快照内 8 处 64-hex 全为 sources_status 的 sha256 文件摘要(有键名上下文),无 token/key 字段。

## 第7节 快照质量抽查 — PASS(附口径注记)

- HSI/HSCEI: series_store n=2000 整(2018-09-27..2026-11-11),末值 24315.92/8171.45 与 facts 一致;原始件 hk_indices ^HSI/^HSCE 均 2000 根,sha256=87d300e3…与快照 sources_status 声明吻合。"tencent 通道"为代码级事实(china_market_collector "腾讯ifzq直连(港股主通道)"),快照 JSON 本身无 channel 字段(注记,非缺陷)。
- CN_CPI/CN_PPI: 原始件 macro 节 cpi_yoy {2026-09-30, 0.9, source:"tushare_pro"}、ppi_yoy {2026-09-30, 5.0, source:"tushare_pro"} 双双在档。

## BLOCKER 列表

**零 BLOCKER**。合并对象 dae5a41 为 docs-only、内容与工件相符、红线全净、研究面测试全绿;唯一的数值错误(ZQ−DFF 0.295)不在提交内容内且不改任何研究结论。

## MINOR 观察列表与处置

1. [数据修正] QB-001 归档 +0.295pp 应为 +0.305pp(5 处)→ **已处置**: 更正评注 QB-20261112-001-C1 随行(不重写原件)+草稿五处修正+增量 0.08→0.09。
2. [同步缺口] dev 树两处工件为旧版(VP sidecar 20261110 面/china_20261112 无 hk_indices 旧版)→ **已处置**: VP 面 17 件同步 20261112、china/anchors 对齐 v2 声明(sha 87d300e3 验证通过),旧版存 *.pre_ac7_v1.json。
3. [口径措辞] "C 层 133 全 NOT_YET_TESTABLE"不准确: 实际=96 NMV+28 NYT+5 UNPARSEABLE+4 no_forecast,正确表述"全部不可判"→ ITERATION_LOG 记账已按此口径。
4. [小过计] QB-004 "剔 2020-04 负油价日 n=2": 快照内实际仅 1 日(2020-04-20);全窗 pearson +0.022 未精确复现(0.005~0.059,定性"近零"成立)→ 留档注记,不更正(量级无关)。
5. [台账语义] S11_archive 标 [FAIL] 系设计注记(默认关+用户认可后),该 run 已带 --archive 且 executed=true、archived_query_id=null;QB 归档系另行显式 research --archive 产生——如实但易误读 → 留档注记。

复算脚本与全部日志在 /tmp/r8-verify/(recompute*.py、g_*.log 等)。
