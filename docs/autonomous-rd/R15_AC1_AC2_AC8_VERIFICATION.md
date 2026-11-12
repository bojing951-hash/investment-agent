# R15 验证报告 — AC1 / AC2 / AC8 正式复核(dev/rd-r15-ac1-ac2-ac8 @ dc4c57a)

> 验证时间: 2026-11-12。验证席: 操作者 fork(独立 worktree /tmp/r15-wt;真实数据只读引用 dev 树,零写入)。
> 权威定义: `docs/autonomous-rd/PRODUCT_GOAL.md` §八。本报告为独立复核,非自验——结论基于本席亲跑命令与亲算数值。
> 终判纪律: 状态置 EXECUTED/PASS 候选,终判留用户裁定席(与 AC7/AC10 行同款)。

## 第1节 AC1 真实全球宏观全景 — **PASS 候选**

定义(ProductGoal 330-332): ①基于真实数据生成主要经济体和金融市场的当前状态;②明确展示重要指标、变化、数据日期、来源和缺口。

### 1a 真实数据覆盖主要经济体

- 注册表 `config/metric_registry.json` v2.8.4: **110 指标**,零缺 `source`/`source_symbol`(全量脚本核验)。经济体分布: **US 57 / CN 18 / GLOBAL 12 / EA 11 / JP 8 / HK 4**;criticality: core 32 / important 76 / context 2。
- 深度样板(亲查 registry 原文): `SPX_CAPE`←shiller_collector `ie_data.xls!CAPE`(1871+ 月频);`SPX_EPS`←`ie_data.xls!E`;`JP_POLICY_RATE`←FRED `IRSTCI01JPM156N`(政策利率长期史)。
- 权威快照 `data/daily/research_snapshot_20261112_v2.json`: **103 facts 全带 value/unit/observation_date/as_of/source**(脚本核验 0 缺);质量计数 PASS 72 / DEGRADED 13 / FAIL 0。

### 1b 指标/变化/日期/来源/缺口的展示面

- 报告面 `research_snapshot_20261112_v2.md`(179 行): 表头=**指标|收盘/最新|单位|观测日|周变化|身份备注|质量**,135 数据行;开头披露 research_as_of+Gate A+「不可变快照,数值表由程序确定性生成(模型只作解释,不选数/不改数)」。
- 变化面: facts `derived` 结构(week/mtd 窗含 basis_value+formula 字符串)覆盖 **71/103**;其余 32 为月频政策利率/估值水平/流量存量类,md 周变化列显式示「—」(显式披露,非隐藏)。抽验 UST_30Y: derived.week 含 `formula: "2026-11-09值−2026-11-06值(百分点;1pp=100bp)"`。
- 来源面: md「数据源状态」表 8 通道(global/macro/china/rate_economy/japan/jp/ea/shiller)全 EXACT+文件名+采集日;每 fact 另带 `source{collector,file}`。
- 缺口面: Gate A=DEGRADED,`noncore_missing` 5 项(BUND_10Y/BUND_2Y/CN_OMO_7D/CN_SF_FLOW/JP_CPI_TOKYO_YOY)逐项带因;`docs/P2_DATA_GAP_LEDGER.md` 台账在档(BUND=源端封锁、JP_CPI=用户裁定诚实缺席、CN_SF_FLOW=R9 mofcom 复通带镜像滞后降级)。
- 口径注记(非违规): v2 md 对缺失项的措辞「来源文件在场而指标缺席(采集遗漏)」为 R11 三分支归因**之前**的旧措辞;R11/R13 后 recompute 已细分「子源缺席/采集遗漏/不可区分」。快照为不可变历史档,保留旧措辞=设计使然;现行代码口径更细。

**终判理由**: 两款定义条款均有真实数据+机器可查的展示面支撑;缺席项全部诚实登记且不进研究结论(Gate A note 明示)。**PASS 候选**。

## 第2节 AC2 真实机构研究 — **PASS 候选**

定义(ProductGoal 333-336): ①从合法可获得的公开原始资料获取机构观点;②每条重要观点可追溯机构、报告、发布时间、原始内容;③区分机构明示观点与 AI 推导。

- **①合法公开来源**: `data/institutions/views/` 17 档,`access_level` 分布 public_full 10 / public_summary 6 / headline_only 1(获取深度逐档披露),`source_url` 17/17 在场。15 机构(Fed/ECB/BOJ/PBoC/IMF/BIS/OECD/World Bank/Goldman/BlackRock/UBS/PIMCO/Vanguard/MSIM/IEA)。
- **②四要素零缺失**: 脚本全量核验 `institution`/`report_title`/`publish_date`/`core_views`(+`source_url`)在 **17/17 档零缺**;schema_version 全库统一 **1.1**;另带 authors/key_assumptions/mechanism_steps/forecasts/falsification_conditions/evidence_cited/revisions 完整链。
- **③明示 vs 推导=结构强制**: `scripts/view_store.py:163-201` attribution **枚举硬拦截**(缺失/非法→machine-readable 拒绝),`core_views[].attribution` 与 `falsification_conditions[].attribution` 双层要求;实测全库 **112/112 条 core_views 均 `institution_stated`**,零 AI 推导语句混入观点本体;AI 推导隔离在独立 VP sidecar 层(`data/institutions/verification/VP-*` 17/17,`generated_by`/`generation_basis` 声明引擎与口径)。
- **验证面(与 AC3 接口)**: `scripts/view_verifier.py` 三型 A/B/C(期限解析+maturity);`view_plausibility.py` 六标签。抽验 VP-VIEW-20261110-001: 6 hypotheses,label 分布 NOT_YET_TESTABLE 2 / INSUFFICIENT_EVIDENCE 4——**C 型(到期预测实判)全库未到期=如实不可判,首验窗 2026-12(日历门,不提前)**。

**终判理由**: 三款定义条款全满足,且「明示 vs 推导」是 schema 级硬约束而非文档约定。**PASS 候选**。

## 第3节 AC8 研究可复核 — **PASS 候选**

定义(ProductGoal 360-362): ①重要数据、机构观点、统计结果和研究结论能追溯来源;②独立审计者能够重新计算关键数值、复查原始资料、并判断结论是否超出证据范围。

### 3a 溯源链(本席亲验)

- fact→源档: 103/103 facts 带 `source{collector,file}`。
- 档案→快照绑定: QB-20261112-001(record+full)的 `digest_snapshot=d912054bb6e154a3`;本席按 `research_provenance.digest_snapshot` 正口径(canonical JSON sha256 前 16 位)**亲算当前 v2 快照 = d912054bb6e154a3,逐位一致**(注意: 绑定口径是内容指纹,非文件字节——文件字节 sha 会因格式化漂移,内容指纹才是防篡改绑定)。
- 快照→采集档: SPX 11-11 收盘 7609.63 与周基准 11-06 的 7376.85 **物理在场**于 `global_20261112.json`(fact.source 所指文件)。

### 3b 独立复算(本席亲算 4 组)

| # | 声明 | 本席复算 | 结果 |
|---|---|---|---|
| N1 | ZQ−DFF 利差: 档案原文 +0.295pp;correction-1 更正 +0.305pp | 4.185−3.88=**+0.305pp** | ✅ 更正确认(档案原值确为算错,R8 发现+评注随行链完整) |
| N2 | SPX 周变化 +3.16%(md)/3.1554(fact) | 7609.63/7376.85−1=**+3.16%** | ✅ |
| N3 | NDX 周变化 +5.2942 | 28418.90/26989.99−1=**+5.2942%** | ✅ |
| N4 | REAL_10Y=2.68(calc 自述=UST_10Y−BEI_10Y) | 4.88−2.20=**2.68** | ✅ 恒等式精确 |

- N1 是 AC8 条款②的端到端实证: 独立审计者复算→发现历史数值错误→更正评注不重写档案→结论方向/量级不变的越界判断在 correction-1 内。
- 先例证据(引用在档): R8 独立复算 31 数值全中(R8_AC7_VERIFICATION.md);R12 干净环境追溯 3/3 sha256 链;v2 md「对账与跨指标核验」节含跨通道一致性(GOLD_F vs GLD、jp vs japan 通道逐值对账)。

**终判理由**: 溯源链三层(档案→快照→采集档)与复算路径全通,且系统能承载「审计发现错→评注更正→不越界」的完整闭环。**PASS 候选**。

## 第4节 移交下轮(R16+)

1. **AC6 行注记过时**: FINAL_ACCEPTANCE AC6 行「剩余: AC7 端到端 3 任务+1 开放题未跑;真实案例积累」——AC7 已 EXECUTED(2026-11-12),该注记须 R16 更新为真实案例积累等剩余项。
2. **QB-005~008 为零 Key 边缘档**: 4 档 question_text=「零Key矩阵问题」、answer_summary 空 values(research_mode_gate 三态测试产物),合法但单薄;建议 R16 在归档说明面注记其边缘测试性质,避免未来读者误当研究失败例。
3. **v2 md 旧措辞快照**: §1b 口径注记——若未来重生成同名快照,R11 三分支归因措辞自动生效,无需回改历史档。

## 第5节 终判汇总

| AC | 状态 | 终判 |
|---|---|---|
| AC1 | NOT_VERIFIED→**EXECUTED** | PASS 候选,留用户裁定席 |
| AC2 | NOT_VERIFIED→**EXECUTED** | PASS 候选,留用户裁定席 |
| AC8 | NOT_VERIFIED→**EXECUTED** | PASS 候选,留用户裁定席 |
