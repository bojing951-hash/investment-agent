# Audit-R32 · N30 · 独立语义审查(零上下文席位)· round1 · PROSE

## 0. 受审对象与边界

- 席位: semantic-audit-seat / independent-zero-context-seat-r32-n30-round1;审查日 2026-11-24。
- 受审稿: 运行目录 `20261123T235157Z_2026年11月_日本和欧元区最近六个月的通胀与政策环境有什么不同_哪些方面分化` 下 `agent_judgment.json`,sha256 前 16 位 `b82bf46df353a653`(全文 sha256 `b82bf46df353a65373ef9c2e62c2c32f3020e5ed08ead83c7bbe1096c8b87ddf`);run 20261123T235157Z;代码印章 36499bb78a18dea1ff2b027074088b0ba404c3b8。判断档 183 个字符串叶(l3 / l4 / reader_map / quality_gate_notes / agent_declaration)全部入审,另对三份读者报告中的判断文字做逐字比对。
- 只读面: 冻结快照 `root_overlay/data/daily/research_snapshot_20261123.json`(target_date 20261123,research_as_of 2026-11-23T22:53:47+08:00)、冻结日历 `root_overlay/config/release_calendar.json`(v1.5.0,2026-11-21 更新)、注册表 `root_overlay/config/metric_registry.json`、`report.json`(引擎面: research_plan / evidence_index / layers / steps / notes / semantic_review)、三份读者报告 `MAP_REPORT.md`、`FULL_REPORT.md`、`report.md`;只读安装树内引擎源码 `scripts/research_contract/judgment_contract.py`、`text_consistency.py` 仅用于核对 quality_gate_notes[5] 所述引擎缺口。
- 边界执行: 未读取规程第 2 节禁止路径;未联网;未运行 ia_cli 任何写操作;未调用 record_semantic_verdict;未委派子代理;未修改运行目录与安装树内任何文件;席位脚本与中间表全部位于本目录 `review6/N30_round1`。读数据的 Python 均以 `/usr/bin/python3 -I` 运行,路径作参数传入,不在数据目录内起解释器。未凭记忆或常识补数。

## 1. 裁决

**UPHELD**。复算 1277 点,偏离 0;MAJOR 0 条;MINOR 2 条;NIT 8 条。六查逐项成立,19 条反方攻击无一撼动判断档结论(详见第 4、5 节)。两条 MINOR 均为披露/取用标准可改进,不改变任何数字、方向或结论。

## 2. 复算方法与总览

### 2.1 方法

1. 直算: 每个数字先从只读面独立算出(「直算值」),再在受审稿文字中定位对应 token(记录叶路径),与「报告值」比对;判据型条目核对陈述是否成立。出处一律写到 文件+键。
2. 推定发布规则按注册表与判断档自述独立实现,并用于可见性复算: 欧元区 HICP 月末+16 天;日本全国 CPI 月末+20 天;东京都 CPI 月末−1 天;BOJ 月均 月均+5 天;ECB 决议日=生效日前上一个周四(仅对应受审稿「引擎回推决议日」口径)。冻结日历内没有这些月度读数的实录,故凡依赖推定日的结论都按「引擎推定规则」与「日历实录锚形态(当月最后一个周五/次月首日速报+月中终值)」各算一遍。
3. 工具: `rc_common.py`(取数/定位/比较)+ 分节脚本 `s10a_core.py`、`s10b_chain.py`、`s10c_disc.py`、`s10d_gap.py`、`s10e_final.py`、`s10f_values.py`(判断档主体各覆盖项,逐点落节以附录 A「节」栏为准)、`s10g1_l4trans.py`(l4 情景/传导)、`s10g2a_headturn.py`(headline/turnings/history)、`s10g2b_qgn.py`(quality_gate_notes)、`s10g3a_mapface.py`/`s10g3c_cands.py`(MAP 引擎渲染面)、`s10g3b_xreport.py`(三报告逐字比对)、`s10h_index.py`(证据索引 60 行解析)、`s10i_numeric.py`(判断档数值型 JSON 字段 33 个),`s20_merge.py`(合并)、`s21_closure.py`(数值 token 闭合)。合并结果 `s10_all.json`,逐点表见附录 A。

### 2.2 计数(合并脚本输出: TOTAL points 1277, mismatch 0)

| 分节 | 含义(规程第 3 节覆盖项) | 点数 | 偏离 |
|---|---|---|---|
| ① | 截止日与研究窗口 | 64 | 0 |
| ② | 点值锚格 | 115 | 0 |
| ③ | 同比 | 39 | 0 |
| ④ | 政策面 | 144 | 0 |
| ⑤ | 三利率分解与资产月窗 | 47 | 0 |
| ⑥ | 转折与候选面 | 74 | 0 |
| ⑦ | 传导链各环 | 106 | 0 |
| ⑧ | 历史类比 | 7 | 0 |
| ⑨ | 情景 | 17 | 0 |
| ⑩ | 总判断/走位/对质表一致 | 47 | 0 |
| ⑪ | 诚实缺席项 | 65 | 0 |
| ⑫ | 截止日当日日频观测时点/口径 | 23 | 0 |
| ⑬ | 契约验证非 VERIFIED 项、交付门缺口、「最近六个月」窗口 | 23 | 0 |
| E-日期 / E-月串 / E-月日 | 判断档内日期、月串、月日闭合到证据 | 47 / 21 / 10 | 0 |
| F | 衍生量(天数差、窗口月数、锚间变动等) | 51 | 0 |
| G | l4 情景阈值与传导数值、四层标注、证据引用、数据需求面、证据索引 60 行解析 | 253 | 0 |
| MAP | 读者报告 MAP_REPORT 引擎渲染数值(资产月窗表、候选表、政策聚簇) | 67 | 0 |
| N | 判断档数值型 JSON 字段(锚回声值、转折前后值、资产月窗回声、三利率分解、环序号;判断档全部 33 个数值叶) | 57 | 0 |
| 合计 | | 1277 | 0 |

构成: 文内数值锚定点 617(判断档主体 l3/l4/reader_map/quality_gate_notes 607 点: 按叶路径定位 543 点,覆盖 429 个不同的(叶路径, token)组合与 46 个字符串叶;另 64 点为日期、月串、月日的闭合点,按全文出现次数定位;agent_declaration 叶 8 点、schema_version 2 点);其余 660 点为判据、结构与引擎面交叉核对(含 N 节 57 点、MAP 渲染面 67 点;证据索引 60 行: snapshot_fact 35 行逐行在 series_store 该日有值,s3_envelope 25 行逐行在 report.json 的 S3 步或 L1 行在场)。规程要求最低 90 点。

### 2.3 席位脚本自身修正留痕(均非受审稿偏离)

- l4「峰值」判据: 初版按 2026-01..2026-09 全期取最大得 2026-09,与受审句「决议日前可见读数低于 2026-05 峰值」不符;受审句语义是「决议日前可见读数」的最大值,判据改为按可见期取最大(=2026-05),一致。
- 负数比较: 三处差值(−1.63/−1.64/−1.11)席位脚本未取绝对值;history 键实际位于 reader_map.history_periods。
- quality_gate_notes: insufficient_coverage 条目键名、源码文件定位与参数索引、「21 条」按条目数(非去重数)计。
- MAP 引擎面: 资产月窗表为 8 行;末值按引擎渲染精度取容差(1.093972 对 1.09397);候选表 Δ 引擎印三位小数(0.251),比较改为对未取整差值。
- 剔除 1 条空洞点(「证据索引各行 value 与 series_store 同日值一致」): 证据索引行只有 ref/kind/metric_id、不带 value,该判据原样不可成立;改由 `s10h_index.py` 以「ref 在 series_store 该日有值 / S3 步在场」重新核 60 点后计入。
- 以上全部是席位脚本的符号、取整、路径、键名或计数口径问题;没有一处通过放宽判据迁就受审稿。

### 2.4 闭合核对

- 判断档内 56 个不同日期/月串全部映射到证据(series_store 观测日、日历条目、推定发布日、回推决议日、日历更新日、书面日期、情景时限)。
- 未被已核点锚定的非日期 token 88 个: 其中值从未被已核点覆盖的 13 个全为指标 id 分量(如 NIKKEI225 的 225、CAC40 的 40);其余为习语(第一主面、一度、上一个周四、一致、一次性、第二、周五)或已核值的重复出现。

### 2.5 三份读者报告一致性

- 68 个关键串逐字比对: MAP_REPORT.md = reader_map(headline、regions、turnings 的 first_mover/follow_or_diverge、transmission 去 verdict_note),不含 C1–C3、机制链、情景叙述;FULL_REPORT.md 与 report.md = l3+l4+turnings 全文+历史注记,不含 headline、走位、传导;verdict_note 与 quality_gate_notes 不进任何读者报告(与 quality_gate_notes[1] 自述一致)。
- 三报告中不在判断档的数值 token(MAP 46、FULL 73、REPORT 59 个不同值)均为引擎渲染面(运行元数据、事实行表、S6 类比表、S3 相关、数据门文字、证据索引序号、资产月窗表、候选表),逐一直算一致;三报告之间无相互矛盾的数字。

## 3. 逐项复算要点(规程第 3 节覆盖项;逐点表见附录 A)

格式: 出处键 → 直算值 → 受审稿值 → 判定。出处简写: snap=冻结快照,SS=snap.series_store,RP=report.json.research_plan,CAL=冻结日历,REG=注册表。

**① 截止日与窗口** — snap.target_date=20261123、snap.research_as_of=2026-11-23T22:53:47+08:00、RP.question_window → 截止日 2026-11-23(快照实际覆盖日),六个月窗 2026-05-23..2026-11-23 → 受审稿 headline 与 quality_gate_notes[4] 写明截止日为 2026-11-23、问句所称 2026-11 月末尚未到而如实截至,窗口同上 → 一致(64 点)。截止日之后: 判断档内晚于 2026-11-23 的日期与月串只有书面日期 2026-11-24、问句请求期末 2026-11-30(未到)、情景观测月 2026-12、时限 2027-02-15 及其推定入档月份(2027-01、2027-02),均不以证据身份出现;冻结日历 18 条无晚于截止日的决议/生效条目,无待生效决定;历史段为 0,无事后段。

**② 点值锚格** — RP.point_values.cells[*].anchors 与 SS.<指标>@<观测日> → 各格 anchors 键集合恰为「6个月前」「最新一期」,全部 status=ok、absent=[]:EA_HICP_YOY 2026-04 的 3.0(推定发布 2026-05-16)→2026-10 的 4.0(2026-11-16);JP_CPI_YOY 1.38(2026-04,2026-05-20)→2.44(2026-10,2026-11-20);JP_CPI_TOKYO_YOY 1.42(2026-04)→2.73(2026-10,2026-10-30);JP_POLICY_RATE 0.727(2026-04,2026-05-05)→1.227(2026-10,2026-11-05);ECB_MRO 2.15(2025-06-11)→2.65(2026-09-16);ECB_DFR 2.0(2025-06-11)→2.5(2026-09-16)。「6个月前」锚=推定发布日不晚于窗起 2026-05-23 的最新已发布观测,逐格复算相同 → reader_map.regions[*].anchor_echo 与 C1/C2 所引逐格一致(115 点)。

**③ 同比** — SS.EA_HICP_YOY@2025-10-01=2.1、@2026-10-01=4.0;SS.JP_CPI_YOY@2025-10-01=2.99、@2026-10-01=2.44 → 欧元区 +1.9pp、日本 −0.55pp、水平差 1.56pp → C1「抬升一点九」「回落约零点五五」「高于日本约一点五六」及 regions.from_to 同值 → 一致(39 点)。基期: 两序列同为同比口径(基期=去年同月);日本序列系引擎按注册表口径自算(REG calc: zmi2025aa+zmi2020aa 双档各自同月同比后拼接,新基优先,重叠差>0.10pp 告警),受审稿已点明;东京序列自 2026-01 起、去年同月读数不在序列内,受审稿写明无法做同比方向对照。未见「缺基期给同比」。路径数: JP 2025-01=4.03、2025-09=2.91、2026-02=1.27、2026-03=1.46、2026-04=1.38;EA 2026-06..10=2.8/2.9/3.2/3.8/4.0;东京 2026-06=1.6→2026-09=2.69;2026-09 期日本对欧元区水平差 全国 −1.64、东京 −1.11 → 逐一相同。

**④ 政策面** — SS.ECB_MRO / ECB_DFR 变更点、CAL 条目、REG 无 JP_POLICY_TARGET → MRO 2026-06-17 2.15→2.4、2026-09-16 2.4→2.65;DFR 2026-06-17 2.0→2.25、2026-09-16 2.25→2.5(各 25bp);两序列自 2025-06-11 至 2026-06-17 维持 2.15/2.0 共 371 天;两次生效日相隔 91 天;回推决议日 2026-06-11、2026-09-10。JP_POLICY_RATE 月均 2025-11=0.478→2026-10=1.227(近 12 个月约 +75bp);六个月锚间 0.727→1.227 净 +50bp(06/07/09/10 月上台阶合计 +50.1bp,含 2026-08 的 −0.1bp)。CAL: BOJ 2026-09-18 决议、2026-09-24 生效、目标 1.25、2026-10-30 维持(两条均 user_directive);生效日对生效日 8 天、回推决议日对决议日 8 天;2026-10-30 至截止 24 天。水平差 MRO 口径 1.40、DFR 口径 1.25 → C2、机制链环 2、headline、MAP 走位所引逐一相同;四层标注齐备(日历两条【事实】、月均台阶与收紧方向【推断】、回推决议日【推断】、后续决议面【尚未验证】) → 一致(144 点)。

**⑤ 三利率分解与资产月窗** — reader_map.rates_decomposition 与 RP.us_rates_trio / asset_moves、SS 日频 → 三利率窗 2026-10-20..2026-11-19 两面相同,名义 −8bp=实际 +11bp+盈亏平衡 −19bp(直算 UST_10Y 5.12→5.04、TIPS_10Y 2.77→2.88、BEI_10Y 2.35→2.16;窗末 5.04=2.88+2.16;恒等残差 0);资产月窗 2026-10-23..2026-11-23;资产月窗回声 NIKKEI225 −9.98%(至 11-20)、DAX +0.11%、SPX −5.51%、VIX +38.87%(直算同值);MAP 资产月窗表 8 行起值/末值/变动%/指数点变动全部重算一致(SPX 7623.68→7203.85 即 −5.51%、EURUSD 1.1221→1.0970 即 −2.24%、USDJPY 156.494→159.707 即 +2.05%、DXY 101.81→103.81 即 +1.96% 等) → 判断档所引同值(47 点;另 MAP 渲染面 67 点覆盖资产月窗表、候选表与政策聚簇行)。截止日盘中口径: EURUSD 1.0940(−2.51%)、USDJPY 159.347(+1.82%)、DXY 104.079(+2.23%)、SPX 7203.85、VIX 27.01;VIX 近 30 日 19.45→27.01(+38.87%),末六收盘 11-13 19.30、11-16 22.91、11-17 25.46、11-18 24.56、11-19 28.44、11-20 35.89 → 一致。

**⑥ 转折与候选面** — RP.turning_candidates、MAP 候选表、SS → 候选 4 行: JP_CPI_YOY 2025-11..2026-02 2.9→1.27(Δ−1.63,|Δ| 最大)、EA_HICP_YOY 2026-02..05 1.9→3.2(+1.3)、JP_CPI_TOKYO_YOY 2026-06..09 1.6→2.69(+1.09)、JP_POLICY_RATE 2026-04..07 0.727→0.978(+0.251) → 受审稿「日本回落为幅度最大候选」成立;三条转折的 date/metric_id/before_date/value_before/value_after 与序列一致;turning_supplement 为空且与引擎面一致(74 点)。

**⑦ 传导链各环** — 机制链 M1 四环证据级 E1/E1/E2/E2。环 1: 两序列 2026-05..2026-10 逐月值与月度差距 0.93–1.67pp(3.2−1.53=1.67 … 2.9−1.97=0.93)。环 2: ECB 两次变更、BOJ 决议/生效/目标/维持、月均台阶(同④)。环 3【假设】: EURJPY 合成 175.61→175.19(−0.24%)→174.32(−0.73%)、汇率月窗、UST_10Y 5.04%(2026-11-19),缺环注记「引擎无政策差-汇率联动通道证据」。环 4【假设·归因】: 同日收盘 SPX −9.36%、NIKKEI225 −9.98%、DAX −1.50%、CAC40 +1.86%、VIX 19.45→35.89(+84.5%);先例 2026-11-04→11-05 VIX 16.61→28.18(+69.66%)、至 11-11 回落 17.49(四个交易日,−37.93%)、SPX 11-05 −4.36%、NIKKEI225 11-06 −5.96%;两读数日 VIX +18.70%/+26.20%;缺环注记「归因环节为【假设】(单月窗、多因子叠加)」。传导三环: 决议前可见读数 2026-04=3.0 与生效日 2026-05=3.2、第二次 2026-07=2.9 与 2026-08=3.2。全部重算一致(106 点)。相称性: 环 3、环 4 的因果与归因句均带【假设】/【假设·归因】并附缺环注记,事实句与假设句分写,E2 环无事实位措辞;E1 环只含快照序列与日历事实。

**⑧ 历史类比** — reader_map.history_periods 长度 0,history_zero_case_note 写明 0 段及理由;所引 S6 信封(扫描候选月 1871、有效 74、TOP1 候选月 2025-03 距离 0.727)与 report.json 对应键一致;历史段为 0,无事后段,不涉及「随后 3/6/12 个月结果」的措辞问题(7 点)。

**⑨ 情景** — l4.scenarios 两情景 rows 各 5 键;S1 阈值(EA_HICP_YOY ≥3.5 且两地水平差 ≥1.5)对 S2(<3.0 且 ≤1.0)互斥互补;S1 前提「日本全国 CPI 同比 2.0% 以上」与截止读数 2.44 相容;时限 2027-02-15;观测月 2026-11/2026-12 的推定入档日 2026-12-16、2026-12-20、2027-01-16、2027-01-20 均晚于截止日且早于时限;证伪指标 EA_HICP_YOY/JP_CPI_YOY 在册可观测;证伪阈不含 VIX 分量(文本核对);披露区间(3.0–3.5 不触发亦不证伪、3.5–4.0 前提成立不触发、VIX 25–30 均不触发)与阈值表逐条相符;S1 政策分量步长 25bp 等于已观测变更步长(⑨ 17 点,另见 G 节 l4 情景阈值复算)。

**⑩ 总判断/走位/对质表** — headline 与 l3/l4 的数值与方向逐项一致(4.0 对 2.44;MRO 2.65/DFR 2.5 对 BOJ 目标 1.25;两次各 25bp 对月均净 +50bp;证据不足六项与 C3 ①–⑥ 一一对应);MAP 走位(regions/turnings 文字)与 reader_map 逐字一致;对质表 3 行与 transmission.links 的 observed_fact / causal_hypothesis / competing_explanation / main_predicts / competing_predicts / face_off_verdict 逐字一致(47 点)。

**⑪ 诚实缺席项** — C3 六项逐项对到只读面: ①REG 无 JP_POLICY_TARGET,CAL 仅目标决议一条与维持确认一条(均 user_directive);②序列末日 2026-09-16、距截止 68 天,超过注册表 10 天新鲜度阈(REG freshness.max_calendar_lag_days=10;另设 decision_dated 规则);snap.gate_a 将 ECB_DFR/ECB_MRO 列于 noncore_degraded;③CAL 内 EA HICP 实录三条(观测月 2021-05、2022-06、2025-03),其余为推定;④修订口径披露;⑤EA/JP GDP 序列在 noncore_missing、序列面至 2026-07(1.28/1.16)而受审稿不取用;⑥BUND_2Y/10Y 缺席、JGB 事实行 2026-11-19 为 PASS(1.853/2.235/2.87)。gate_a: status=DEGRADED、noncore_missing 7 项、noncore_degraded 8 项,与 MAP 数据门行一致(65 点)。

**⑫ 截止日当日日频观测时点/口径** — snap.research_as_of=2026-11-23T22:53:47+08:00 → 纽约 09:53、柏林 15:53、东京 23:53、上海 22:53 → quality_gate_notes[4] 四地时刻逐一相同;SPX/VIX/DAX/CAC40、汇率与 DXY 的截止日值为盘中快照而非收盘,受审稿逐处标明;VIX 截止日盘中 27.01 与末收盘(11-20)35.89 分记,未混用(23 点)。

**⑬ 契约验证非 VERIFIED 项与交付门** — report.json.agent_judgment.contract_verification.verdicts 共 5 条(VERIFIED 4、STALE 1),唯一非 VERIFIED 项为 C2 所引 ECB_DFR 数值串 2.5%(value=expected=2.5,注记「Fact 直读 ECB_DFR@2026-09-16=2.5」),总判 VERIFIED → C3② 写明「契约验证对本档水平对照所引存款便利利率数值串记状态 STALE——数值一致、观测滞后六十八天」,指标与原因一致。交付门: run.evidence_gate(discipline r32、as_of 2026-11-23、publication_basis=snapshot_presence)无 blocked_class/草稿判定字段,facts_kept 105、facts_dropped 0、facts_excluded_version 0;RP.point_values.absent=[];缺席项(JP_POLICY_TARGET、GDP、BUND)均写为不可得/缺席而非「无变化」;月均市场利率与 BOJ 宣布目标分记,未见把序列值写成官方宣布目标;report.notes「地图计划指标缺数(披露不阻断…): ECB_MRO、ECB_DFR」已渲染进读者报告(判断档未点名该形态,见 MINOR-2);semantic_review.seat_invoked=false、verdict=null,与开席前状态相符。**⑬' 「最近六个月」窗口** — RP.question_window.windows[0].months=6、窗 2026-05-23..2026-11-23;锚间比较与月窗口径均落在此窗内;近 12 个月月均 +75bp 另标「近 12 个月」,未见以 12 个月窗数值充当六个月(23 点)。

## 4. 六查与反方攻击

### 4.1 六查

1. 一致性(数字/日期/方向跨节、跨三份读者报告): 成立。headline、C1–C3、机制链、情景、走位、对质表与 MAP/FULL/report 渲染之间无相异数字(第 2.5 节)。
2. 基期与口径: 成立。同比均带去年同月基期;东京速报/全国、宣布值/月均市场利率、盘中/收盘、六个月锚间/近 12 个月均分记并标注;双基期拼接已披露。
3. 因果措辞: 成立。机制链环 3、环 4 与传导三环的主解释均标【假设】/【假设·归因】,附缺环注记与区分指标;三环对质均为「尚不能区分」(对质理由以「裁定理由:」标出后并入 observed_fact 末段,见 NIT-8;理由内容是预期与观测的比对,未把假设写成事实)。
4. 竞争解释并列: 成立。三条矛盾陈述各 2 条【假设】竞争解释并注明不可在引擎面验证;机制链四环各附竞争解释;传导三环主/竞争预期并列写出。
5. 可观测性与证伪: 成立。触发与证伪阈值为在册指标上的数值条件,带时限 2027-02-15,晚于观测月推定入档日;「不触发亦不证伪」区间如实披露。
6. 事后信息: 成立。全部引用观测日不晚于 2026-11-23;决议前可见性按推定规则与日历实录锚形态各算一遍;情景观测月为未来并标假设;月度值修订口径已披露。

### 4.2 反方攻击记录(每条 L3 矛盾陈述、机制链每环至少一条;共 19 条)

1. C1·同期性: 若两地观测期不同即为相邻口径冒充 → SS 两序列最新已发布观测均为 2026-10 期(EA 4.0、JP 2.44;推定发布 11-16、11-20 均不晚于截止) → 攻击不成立。
2. C1·动量相近是否削弱「分化」: 锚间 EA +1.0pp 对 JP +1.06pp → 受审句已自述「水平与同比方向分化、窗内动量不分化」,并列三种起算点(自 2026-06 期 +1.2 对 +0.77、自 2026-05 期 +0.8 对 +0.91,快慢互换),复算一致,未隐瞒 → 攻击不成立。
3. C1·同比方向相反是否由拼接造成: 日本序列双基期拼接仅影响同月同比后的拼接处且有 >0.10pp 告警阈,−0.55pp 的幅度与方向远超该阈;受审句已披露「双基期档各自同月同比后拼接,非官方公布值直取」 → 不构成问题,留 NIT-7 建议点明对照是否跨拼接点。
4. C1·东京读数: 东京都 CPI 在 gate_a.noncore_missing 内却被用作方向佐证 → 属实,但每处已披露;记 MINOR-1,不动摇以全国口径为主的第一主面。
5. C2·「累计幅度相近」口径: 欧央行宣布值 50bp 对日本月均 +50bp → 受审句明写口径不同「仅作量级对照」;若改用近 12 个月窗,日本月均约 +75bp 而欧央行仍 +50bp,「相近」只在六个月锚间成立——受审稿限定语正是「最近六个月窗口」 → 攻击不成立。
6. C2·日本「收紧」方向无宣布值前值: CAL 只有目标决议(1.25)与维持确认两条、无前值 → 受审句把方向标【推断】并以月均台阶(0.727→1.227)为据,未以事实位措辞出现 → 攻击不成立。
7. C2·欧央行决议日为回推: 实际决议日若不同则先后排序变 → 受审句并列「生效日对生效日 8 天」与「回推决议日对决议日 8 天」并标【推断】,写明月频证据下先后未定,结论不依赖单一回推 → 攻击不成立。
8. C2·水平差口径: 用 MRO 2.65 对 BOJ 目标 1.25 是否拔高分化 → 受审句同时给出 DFR 口径 1.25 与 MRO 口径 1.4,复算相同 → 攻击不成立。
9. C3·「六项」是否有漏项或无据项: ①–⑥ 逐项对到只读面(第 3 节⑪) → 无无据项;漏掉的是引擎数据需求面「窗内覆盖不足/计划指标缺数」形态,记 MINOR-2。
10. M1 环 1(E1)·路径方向: 「日本逐月上行、欧元区非单调」是否属实 → 窗内 JP 1.53/1.67/1.97/1.98/2.16/2.44 单调不降,EA 于 2026-06 回落至 2.8,月度差距 0.93–1.67pp → 攻击不成立。
11. M1 环 2(E1)·台阶合计: 「合计 +50bp」是否漏算 2026-08 的 −0.1bp(0.978→0.977) → 所列四级上台阶合计 +50.1bp,含该微降后净 +50.0bp,受审句为净额口径 → 一致。
12. M1 环 3(E2)·利差假说未纳入美元端: 是否仍被当作解释 → 受审句标【假设】,写明未纳入 UST_10Y(5.04%)故两解释对本月窗预期相同、尚不能区分,E2 环无事实位措辞 → 相称。
13. M1 环 4(E2)·「读数发布主因」的反证: 11-16、11-20 两日 EURUSD/USDJPY 单日变动最大 0.2293%,四地股指 11-13→11-20 跌幅均不深于 SPX 的 8.61%;但 VIX 两个最大单日跳升恰在这两日(+18.70%/+26.20%) → 主因确实不可区分,受审句结论即「尚不能区分」且归因标【假设】 → 无过度归因。
14. 传导链三环·对质是否偏袒: 三环 face_off_verdict 均「尚不能区分」(支持主解释 0、竞争 0、未定 3),与 quality_gate_notes[1] 自述一致;各环数值逐一直算一致 → 攻击不成立。
15. 传导环 1·n=2 的反向观察: 「读数低于峰值仍触发上调」是否被写成规律 → 受审句自陈按日历两档形态计则不成立(决议日前可见读数为 2026-05 与 2026-08 的 3.2),复算一致 → 未写成规律。
16. 情景·可观测性与相容性: S1/S2 阈值互斥互补;3.0–3.5、3.5–4.0、VIX 25–30 三个不触发区间已披露;观测月 2026-11/2026-12 推定入档日 2026-12-16..2027-01-20 晚于截止日且早于时限 2027-02-15 → 截止日读数(EA 4.0、JP 2.44、差 1.56)与 S1 前提相容而未触发,与 S2 前提相反且 S2 自称并列反例情景;证伪指标在册可观测 → 攻击不成立。政策分量须待日历补录,已披露。
17. 历史类比·S6 已有最近类比段而判断档取 0 段: 是否漏用 → 受审档写明 0 段及理由,信封标量与 report.json 一致 → 保守选择且如实披露,不构成问题。
18. 截止日口径·是否把盘中当收盘或混入事后信息: 采集时点 2026-11-23T22:53:47+08:00(纽约 09:53、柏林 15:53、东京 23:53),SPX/VIX/DAX/CAC40 与汇率为盘中快照且逐处标明;全部引用观测日不晚于 2026-11-23 → 攻击不成立。
19. 读者报告·是否与判断档相左: 68 个关键串逐字比对分区一致;三报告中不在判断档的数值 token 均为引擎渲染面并逐一直算一致 → 无相左。

## 5. 问题清单与裁决

### 5.1 问题清单

MAJOR: 无。

**MINOR-1 东京都 CPI(Gate A 缺席指标)的取用标准不一**
- 位置: l3.contradictions[0].statement(C1 末段)、reader_map.turnings[2].first_mover、reader_map.regions[1].from_to 与 anchor_echo。
- 事实: JP_CPI_TOKYO_YOY 在冻结快照 gate_a.noncore_missing 内,Gate A 注记为「缺失/失败数据已披露,不得进入研究结论」;判断档仍以其序列面读数充当第三转折的先行指标、C1 方向佐证与锚回声。每处均写明「Gate A 列于 noncore_missing,读数取自快照序列面、L1 无对应事实行」,而 C3⑤ 对同为 noncore_missing 的 GDP 序列采取「按 Gate A 不取用」——同一档内取用标准不一。
- 定级理由: 结论(两地水平与同比方向分化、日本通胀回升)主要由全国口径序列支撑,剔除东京读数不改变结论;属披露/口径可改进 → MINOR。
- 建议: 统一取用规则;若保留,在第三转折与锚回声处明写「序列面参考、不作为结论必要支撑」,并提请核对引擎各面对该指标的不一致(数据需求面 satisfied、点值格 status=ok 而 Gate A 缺席)。

**MINOR-2 ECB 两指标的「窗内覆盖不足/计划指标缺数」形态未在判断档点名**
- 位置: l3.contradictions[2].statement(C3 ②)。
- 事实: 引擎数据需求面将 ECB_MRO/ECB_DFR 记为 insufficient_coverage(窗内有效观测 n=2<66),report.notes 列「地图计划指标缺数(披露不阻断…): ECB_MRO、ECB_DFR」并渲染进读者报告;判断档已披露实质限制(序列止于 2026-09-16、距截止 68 天、Gate A 降级、契约 STALE、后续决议面不可判),但未点名这一引擎面形态,读者在报告表格层看到「缺数」字样时判断档无对应说明。
- 定级理由: 不改变结论 → MINOR。建议在 C3② 补一句指向数据需求面的覆盖不足记载。

**NIT(行文,不影响结论)**
- NIT-1: regions[1].from_to「自 2025-01 高点 4.03」——4.03 为 2025-01 读数,非全序列最高(SS.JP_CPI_YOY 最高为 2023-01 的 4.31),建议加「阶段」限定。
- NIT-2: l4.scenarios[0] asset_direction.confidence_tier「有相关证据」与 scenarios[1]「纯逻辑推理」、同窗传导对质「尚不能区分」并列时层级语义不一(此处「相关证据」指同窗观测相容而非因果已立),建议加限定语。
- NIT-3: quality_gate_notes[3]「两情景五行齐备」易读作合计五行(实为每情景五行),建议「两情景各五行齐备」。
- NIT-4: 数字前后空格不统一(headline「距截止 六十八 天」对 quality_gate_notes[4]「距截止 68 天」)。
- NIT-5: C1、C2 单段长数百字,建议分句分段。
- NIT-6: quality_gate_notes[0]「共 21 条 snapshot_fact 引用」为条目数(去重后 11 条),建议注明。
- NIT-7: C1 同比方向对照(2025-10 的 2.99 对 2026-10 的 2.44)是否跨双基期拼接点未点明;幅度与方向远超注册表 0.10pp 告警阈,结论稳健,建议补一句。
- NIT-8: 传导三环 observed_fact 末段并入「裁定理由」(因 verdict_note 不进读者报告渲染),事实与理由虽以「裁定理由:」分隔,但置于事实栏易使读者把对质推理读作观测,建议拆为独立「对质理由」栏或在栏名注明。

### 5.2 引擎面观察(非受审稿问题,不计入 items)

- 注册表 JP_CPI_YOY.calc 文字载「覆盖2021-01..2026-09」,而冻结快照序列已含 2026-10 期;属注册表描述滞后,受审稿所用 2.44 与快照序列及 L1 事实行一致。
- 引擎各面对 JP_CPI_TOKYO_YOY、ECB_MRO/ECB_DFR 的状态记载互不一致(见 MINOR-1、MINOR-2),属引擎面维护事项。
- quality_gate_notes[5] 所列三项引擎缺口: ①锚序检查硬编码「12个月前/3个月前/最新一期」(judgment_contract.py 锚标签循环)与 ②text_consistency.ALIASES 未覆盖本问五个指标 id,经只读源码核实属实;③「历史截止视图下两面口径不一」及「已登记待用户裁定」为席位对研发台账的程序性陈述,不在本席只读面可核范围,未计入复算,亦不构成对受审稿的疑点。
- history_zero_case_note 所称「契约允许 0..3 段」与引擎源码一致(至多 3 段;零段须写明检索范围与原因)。

### 5.3 裁决依据

按规程第 5 节逐条比对 MAJOR 判据: 数字/日期/方向错或与证据相左——无(1277 点 0 偏离);缺基期却给同比——无;以相邻口径冒充——无(各口径分记并标注);事后信息冒充当时可知——无;结论超出证据且无标注——无(唯一贴近者为东京读数的取用,已逐处披露,定 MINOR-1);证伪条件不可观测——无。零 MAJOR 且无 REVISE 级问题,两条 MINOR 与八条 NIT 均不改变任何数字、方向或结论 → **UPHELD**。

## 附录 A · 逐点复算表(由 s10_all.json 生成;一致=直算值与受审稿值相符)

| # | 节 | 出处(文件+键) | 直算值 | 受审稿值 / 文内 token | 一致 |
|---|---|---|---|---|---|
| 1 | ① | snap.target_date | 2026-11-23 | 2026-11-23 / 2026-11-23 | 是 |
| 2 | ① | snap.research_as_of | 2026-11-23T22:53:47+08:00 | 2026-11-23T22:53:47+08:00 / 2026-11-23T22:53:47+08:0… | 是 |
| 3 | ① | report.as_of_declared.requested_as_of | 2026-11-30 | 2026-11-30 / 2026-11-30 | 是 |
| 4 | ① | report.as_of_declared.clamped_to_coverage | true | (判据成立) | 是 |
| 5 | ① | 判断档文字 | 在场 | 在场 / 引擎按 clamped_to_coverage … | 是 |
| 6 | ① | report.question_window (6个月回看窗起) | 2026-05-23 | 2026-05-23 / 2026-05-23 | 是 |
| 7 | ① | 独立推算: 截止日-6自然月 | 2026-05-23 | 2026-05-23 / 2026-05-23 | 是 |
| 8 | ① | report.question_window.to | 2026-11-23 | 2026-11-23 / 2026-11-23 | 是 |
| 9 | ① | 独立推算: 2026-11 月末 | 2026-11-30 | 2026-11-30 / 2026-11-30 | 是 |
| 10 | ① | series_store.EA_HICP_YOY.dates[-1] | 2026-10-01 (末值 4.0) | (判据成立) | 是 |
| 11 | ① | series_store.JP_CPI_YOY.dates[-1] | 2026-10-01 (末值 2.44) | (判据成立) | 是 |
| 12 | ① | series_store.JP_CPI_TOKYO_YOY.dates[-1] | 2026-10-01 (末值 2.73) | (判据成立) | 是 |
| 13 | ① | series_store.JP_POLICY_RATE.dates[-1] | 2026-10-01 (末值 1.227) | (判据成立) | 是 |
| 14 | ① | series_store.ECB_MRO.dates[-1] | 2026-09-16 (末值 2.65) | (判据成立) | 是 |
| 15 | ① | series_store.ECB_DFR.dates[-1] | 2026-09-16 (末值 2.5) | (判据成立) | 是 |
| 16 | ① | series_store.SPX.dates[-1] | 2026-11-23 (末值 7203.850098) | (判据成立) | 是 |
| 17 | ① | series_store.VIX.dates[-1] | 2026-11-23 (末值 27.01) | (判据成立) | 是 |
| 18 | ① | series_store.DAX.dates[-1] | 2026-11-23 (末值 25209.449219) | (判据成立) | 是 |
| 19 | ① | series_store.CAC40.dates[-1] | 2026-11-23 (末值 8022.620117) | (判据成立) | 是 |
| 20 | ① | series_store.NIKKEI225.dates[-1] | 2026-11-20 (末值 56436.65) | (判据成立) | 是 |
| 21 | ① | series_store.EURUSD.dates[-1] | 2026-11-23 (末值 1.093972) | (判据成立) | 是 |
| 22 | ① | series_store.USDJPY.dates[-1] | 2026-11-23 (末值 159.347) | (判据成立) | 是 |
| 23 | ① | series_store.DXY.dates[-1] | 2026-11-23 (末值 104.079002) | (判据成立) | 是 |
| 24 | ① | series_store.UST_10Y.dates[-1] | 2026-11-19 (末值 5.04) | (判据成立) | 是 |
| 25 | ① | series_store.TIPS_10Y.dates[-1] | 2026-11-19 (末值 2.88) | (判据成立) | 是 |
| 26 | ① | series_store.BEI_10Y.dates[-1] | 2026-11-20 (末值 2.15) | (判据成立) | 是 |
| 27 | ① | facts.JGB2Y.observation_date(该指标无 series_store 序列) | 2026-11-19 (末值 1.853) | (判据成立) | 是 |
| 28 | ① | facts.JGB5Y.observation_date(该指标无 series_store 序列) | 2026-11-19 (末值 2.235) | (判据成立) | 是 |
| 29 | ① | facts.JGB10Y.observation_date(该指标无 series_store 序列) | 2026-11-19 (末值 2.87) | (判据成立) | 是 |
| 30 | ① | series_store.DFEDTARL.dates[-1] | 2026-11-23 (末值 3.75) | (判据成立) | 是 |
| 31 | ① | series_store.DFEDTARU.dates[-1] | 2026-11-23 (末值 4.0) | (判据成立) | 是 |
| 32 | ① | 推定发布规则 EA_HICP_YOY 2026-10 (月末偏移) | 2026-11-16 | (判据成立) | 是 |
| 33 | ① | 推定发布规则 JP_CPI_YOY 2026-10 (月末偏移) | 2026-11-20 | (判据成立) | 是 |
| 34 | ① | 推定发布规则 JP_CPI_TOKYO_YOY 2026-10 (月末偏移) | 2026-10-30 | (判据成立) | 是 |
| 35 | ① | 推定发布规则 JP_POLICY_RATE 2026-10 (月末偏移) | 2026-11-05 | (判据成立) | 是 |
| 36 | ① | 冻结日历 JP_POLICY_TARGET 条目日期 | 2026-09-18 | (判据成立) | 是 |
| 37 | ① | 冻结日历 JP_POLICY_TARGET 条目日期 | 2026-09-24 | (判据成立) | 是 |
| 38 | ① | 冻结日历 JP_POLICY_TARGET 条目日期 | 2026-10-30 | (判据成立) | 是 |
| 39 | ① | 序列变更日/回推决议日 | 2026-06-11 | (判据成立) | 是 |
| 40 | ① | 序列变更日/回推决议日 | 2026-09-10 | (判据成立) | 是 |
| 41 | ① | 序列变更日/回推决议日 | 2026-06-17 | (判据成立) | 是 |
| 42 | ① | 序列变更日/回推决议日 | 2026-09-16 | (判据成立) | 是 |
| 43 | ① | 星期: 2026-05-16 | 周六 | 周六 / 周六 | 是 |
| 44 | ① | 星期: 2026-08-30 | 周日 | 周日 / 周日 | 是 |
| 45 | ① | 独立推算: 2026-10 最后一个周五 | 2026-10-30 | 2026-10-30 / 2026-10-30 | 是 |
| 46 | ① | 独立推算: 2026-06 最后一个周五 | 2026-06-26 | 2026-06-26 / 2026-06-26 | 是 |
| 47 | ① | 时区换算 research_as_of(UTC-8h)→纽约 | 09:53 | 09:53 / 09:53 | 是 |
| 48 | ① | 时区换算 research_as_of(UTC-8h)→柏林 | 15:53 | 15:53 / 15:53 | 是 |
| 49 | ① | 时区换算 research_as_of(UTC-8h)→东京 | 23:53 | 23:53 / 23:53 | 是 |
| 50 | ① | 时区换算 research_as_of(UTC-8h)→上海 | 22:53 | 22:53 / 22:53 | 是 |
| 51 | ① | research_as_of+08:00 → UTC | 14:53:47Z | (判据成立) | 是 |
| 52 | ① | release_calendar.version | 1.5.0 | 1.5.0 | 是 |
| 53 | ① | release_calendar.updated | 2026-11-21 | 2026-11-21 | 是 |
| 54 | ① | 判断档文字 | 在场 | 在场 / 工单冻结发布日历(v1.5.0,2026-11-… | 是 |
| 55 | ① | evidence_index 行数 | 60 | 60 | 是 |
| 56 | ① | 判断档文字 | 在场 | 在场 / 证据索引(60行)、点值格(6格) | 是 |
| 57 | ① | point_values.cells 格数 | 6 | 6 | 是 |
| 58 | ① | report.run.git_head | 36499bb78a18dea1ff2b027074088b0ba404c3b8 | 36499bb78a18dea1ff2b027074088b0ba404c3b8 | 是 |
| 59 | ② | series_store.EA_HICP_YOY 最新已发布观测(推定发布日<=2026-05-23) | 3.0 | 3.0 / 3.0 | 是 |
| 60 | ② | series_store.EA_HICP_YOY.dates | 2026-04 | 2026-04 / 2026-04 | 是 |
| 61 | ② | 推定发布规则 EA_HICP_YOY (2026-04) | 2026-05-16 | 2026-05-16 / 2026-05-16 | 是 |
| 62 | ② | series_store.EA_HICP_YOY 最新已发布观测(推定发布日<=2026-11-23) | 4.0 | 4.0 / 4.0 | 是 |
| 63 | ② | series_store.EA_HICP_YOY.dates | 2026-10 | 2026-10 / 2026-10 | 是 |
| 64 | ② | 推定发布规则 EA_HICP_YOY (2026-10) | 2026-11-16 | 2026-11-16 / 2026-11-16 | 是 |
| 65 | ② | series_store.JP_CPI_YOY 最新已发布观测(推定发布日<=2026-05-23) | 1.38 | 1.38 / 1.38 | 是 |
| 66 | ② | series_store.JP_CPI_YOY.dates | 2026-04 | 2026-04 / 2026-04 | 是 |
| 67 | ② | 推定发布规则 JP_CPI_YOY (2026-04) | 2026-05-20 | 2026-05-20 / 2026-05-20 | 是 |
| 68 | ② | series_store.JP_CPI_YOY 最新已发布观测(推定发布日<=2026-11-23) | 2.44 | 2.44 / 2.44 | 是 |
| 69 | ② | series_store.JP_CPI_YOY.dates | 2026-10 | 2026-10 / 2026-10 | 是 |
| 70 | ② | 推定发布规则 JP_CPI_YOY (2026-10) | 2026-11-20 | 2026-11-20 / 2026-11-20 | 是 |
| 71 | ② | series_store.JP_CPI_TOKYO_YOY 最新已发布观测(推定发布日<=2026-05-23) | 1.42 | 1.42 / 1.42 | 是 |
| 72 | ② | series_store.JP_CPI_TOKYO_YOY.dates | 2026-04 | 2026-04 / 2026-04 | 是 |
| 73 | ② | series_store.JP_CPI_TOKYO_YOY 最新已发布观测(推定发布日<=2026-11-23) | 2.73 | 2.73 / 2.73 | 是 |
| 74 | ② | series_store.JP_CPI_TOKYO_YOY.dates | 2026-10 | 2026-10 / 2026-10 | 是 |
| 75 | ② | 推定发布规则 JP_CPI_TOKYO_YOY (2026-10) | 2026-10-30 | 2026-10-30 / 2026-10-30 | 是 |
| 76 | ② | series_store.JP_POLICY_RATE 最新已发布观测(推定发布日<=2026-05-23) | 0.727 | 0.727 / 0.727 | 是 |
| 77 | ② | series_store.JP_POLICY_RATE.dates | 2026-04 | 2026-04 / 2026-04 | 是 |
| 78 | ② | 推定发布规则 JP_POLICY_RATE (2026-04) | 2026-05-05 | 2026-05-05 / 2026-05-05 | 是 |
| 79 | ② | series_store.JP_POLICY_RATE 最新已发布观测(推定发布日<=2026-11-23) | 1.227 | 1.227 / 1.227 | 是 |
| 80 | ② | series_store.JP_POLICY_RATE.dates | 2026-10 | 2026-10 / 2026-10 | 是 |
| 81 | ② | 推定发布规则 JP_POLICY_RATE (2026-10) | 2026-11-05 | 2026-11-05 / 2026-11-05 | 是 |
| 82 | ② | series_store.ECB_MRO 末观测<=2026-05-23 | 2.15 | 2.15 / 2.15 | 是 |
| 83 | ② | series_store.ECB_MRO 末观测<=截止日 | 2.65 | 2.65 / 2.65 | 是 |
| 84 | ② | series_store.ECB_MRO 6个月前锚观测日 | 2025-06-11 | 2025-06-11 / 2025-06-11 | 是 |
| 85 | ② | series_store.ECB_MRO 最新一期锚观测日 | 2026-09-16 | 2026-09-16 / 2026-09-16 | 是 |
| 86 | ② | series_store.ECB_DFR 末观测<=2026-05-23 | 2.0 | 2.0 / 2.0 | 是 |
| 87 | ② | series_store.ECB_DFR 末观测<=截止日 | 2.5 | 2.5 / 2.5 | 是 |
| 88 | ② | series_store.ECB_DFR 6个月前锚观测日 | 2025-06-11 | 2025-06-11 / 2025-06-11 | 是 |
| 89 | ② | series_store.ECB_DFR 最新一期锚观测日 | 2026-09-16 | 2026-09-16 / 2026-09-16 | 是 |
| 90 | ② | engine point_values.EA_HICP_YOY.6个月前.value | 3.0 | 3.0 | 是 |
| 91 | ② | engine point_values.EA_HICP_YOY.6个月前.observation_date | 2026-04-01 | 2026-04-01 | 是 |
| 92 | ② | engine point_values.EA_HICP_YOY.6个月前.publication_date | 2026-05-16 | 2026-05-16 | 是 |
| 93 | ② | engine point_values.EA_HICP_YOY.6个月前.status | ok | ok | 是 |
| 94 | ② | engine point_values.EA_HICP_YOY.最新一期.value | 4.0 | 4.0 | 是 |
| 95 | ② | engine point_values.EA_HICP_YOY.最新一期.observation_date | 2026-10-01 | 2026-10-01 | 是 |
| 96 | ② | engine point_values.EA_HICP_YOY.最新一期.publication_date | 2026-11-16 | 2026-11-16 | 是 |
| 97 | ② | engine point_values.EA_HICP_YOY.最新一期.status | ok | ok | 是 |
| 98 | ② | engine point_values.ECB_MRO.6个月前.value | 2.15 | 2.15 | 是 |
| 99 | ② | engine point_values.ECB_MRO.6个月前.observation_date | 2025-06-11 | 2025-06-11 | 是 |
| 100 | ② | engine point_values.ECB_MRO.6个月前.publication_date | 2025-06-11 | 2025-06-11 | 是 |
| 101 | ② | engine point_values.ECB_MRO.6个月前.status | ok | ok | 是 |
| 102 | ② | engine point_values.ECB_MRO.最新一期.value | 2.65 | 2.65 | 是 |
| 103 | ② | engine point_values.ECB_MRO.最新一期.observation_date | 2026-09-16 | 2026-09-16 | 是 |
| 104 | ② | engine point_values.ECB_MRO.最新一期.publication_date | 2026-09-16 | 2026-09-16 | 是 |
| 105 | ② | engine point_values.ECB_MRO.最新一期.status | ok | ok | 是 |
| 106 | ② | engine point_values.ECB_DFR.6个月前.value | 2.0 | 2.0 | 是 |
| 107 | ② | engine point_values.ECB_DFR.6个月前.observation_date | 2025-06-11 | 2025-06-11 | 是 |
| 108 | ② | engine point_values.ECB_DFR.6个月前.publication_date | 2025-06-11 | 2025-06-11 | 是 |
| 109 | ② | engine point_values.ECB_DFR.6个月前.status | ok | ok | 是 |
| 110 | ② | engine point_values.ECB_DFR.最新一期.value | 2.5 | 2.5 | 是 |
| 111 | ② | engine point_values.ECB_DFR.最新一期.observation_date | 2026-09-16 | 2026-09-16 | 是 |
| 112 | ② | engine point_values.ECB_DFR.最新一期.publication_date | 2026-09-16 | 2026-09-16 | 是 |
| 113 | ② | engine point_values.ECB_DFR.最新一期.status | ok | ok | 是 |
| 114 | ② | engine point_values.JP_CPI_YOY.6个月前.value | 1.38 | 1.38 | 是 |
| 115 | ② | engine point_values.JP_CPI_YOY.6个月前.observation_date | 2026-04-01 | 2026-04-01 | 是 |
| 116 | ② | engine point_values.JP_CPI_YOY.6个月前.publication_date | 2026-05-20 | 2026-05-20 | 是 |
| 117 | ② | engine point_values.JP_CPI_YOY.6个月前.status | ok | ok | 是 |
| 118 | ② | engine point_values.JP_CPI_YOY.最新一期.value | 2.44 | 2.44 | 是 |
| 119 | ② | engine point_values.JP_CPI_YOY.最新一期.observation_date | 2026-10-01 | 2026-10-01 | 是 |
| 120 | ② | engine point_values.JP_CPI_YOY.最新一期.publication_date | 2026-11-20 | 2026-11-20 | 是 |
| 121 | ② | engine point_values.JP_CPI_YOY.最新一期.status | ok | ok | 是 |
| 122 | ② | engine point_values.JP_CPI_TOKYO_YOY.6个月前.value | 1.42 | 1.42 | 是 |
| 123 | ② | engine point_values.JP_CPI_TOKYO_YOY.6个月前.observation_date | 2026-04-01 | 2026-04-01 | 是 |
| 124 | ② | engine point_values.JP_CPI_TOKYO_YOY.6个月前.publication_date | 2026-04-29 | 2026-04-29 | 是 |
| 125 | ② | engine point_values.JP_CPI_TOKYO_YOY.6个月前.status | ok | ok | 是 |
| 126 | ② | engine point_values.JP_CPI_TOKYO_YOY.最新一期.value | 2.73 | 2.73 | 是 |
| 127 | ② | engine point_values.JP_CPI_TOKYO_YOY.最新一期.observation_date | 2026-10-01 | 2026-10-01 | 是 |
| 128 | ② | engine point_values.JP_CPI_TOKYO_YOY.最新一期.publication_date | 2026-10-30 | 2026-10-30 | 是 |
| 129 | ② | engine point_values.JP_CPI_TOKYO_YOY.最新一期.status | ok | ok | 是 |
| 130 | ② | engine point_values.JP_POLICY_RATE.6个月前.value | 0.727 | 0.727 | 是 |
| 131 | ② | engine point_values.JP_POLICY_RATE.6个月前.observation_date | 2026-04-01 | 2026-04-01 | 是 |
| 132 | ② | engine point_values.JP_POLICY_RATE.6个月前.publication_date | 2026-05-05 | 2026-05-05 | 是 |
| 133 | ② | engine point_values.JP_POLICY_RATE.6个月前.status | ok | ok | 是 |
| 134 | ② | engine point_values.JP_POLICY_RATE.最新一期.value | 1.227 | 1.227 | 是 |
| 135 | ② | engine point_values.JP_POLICY_RATE.最新一期.observation_date | 2026-10-01 | 2026-10-01 | 是 |
| 136 | ② | engine point_values.JP_POLICY_RATE.最新一期.publication_date | 2026-11-05 | 2026-11-05 | 是 |
| 137 | ② | engine point_values.JP_POLICY_RATE.最新一期.status | ok | ok | 是 |
| 138 | ② | anchor_echo EA[0] metric_id | ECB_MRO | ECB_MRO | 是 |
| 139 | ② | anchor_echo EA[0] value (series_store 直算) | 2.15 | 2.15 | 是 |
| 140 | ② | anchor_echo EA[0] observation_month (series_store 直算) | 2025-06 | 2025-06 | 是 |
| 141 | ② | anchor_echo EA[1] metric_id | ECB_MRO | ECB_MRO | 是 |
| 142 | ② | anchor_echo EA[1] value (series_store 直算) | 2.65 | 2.65 | 是 |
| 143 | ② | anchor_echo EA[1] observation_month (series_store 直算) | 2026-09 | 2026-09 | 是 |
| 144 | ② | anchor_echo EA[2] metric_id | ECB_DFR | ECB_DFR | 是 |
| 145 | ② | anchor_echo EA[2] value (series_store 直算) | 2.0 | 2.0 | 是 |
| 146 | ② | anchor_echo EA[2] observation_month (series_store 直算) | 2025-06 | 2025-06 | 是 |
| 147 | ② | anchor_echo EA[3] metric_id | ECB_DFR | ECB_DFR | 是 |
| 148 | ② | anchor_echo EA[3] value (series_store 直算) | 2.5 | 2.5 | 是 |
| 149 | ② | anchor_echo EA[3] observation_month (series_store 直算) | 2026-09 | 2026-09 | 是 |
| 150 | ② | anchor_echo EA[4] metric_id | EA_HICP_YOY | EA_HICP_YOY | 是 |
| 151 | ② | anchor_echo EA[4] value (series_store 直算) | 3.0 | 3.0 | 是 |
| 152 | ② | anchor_echo EA[4] observation_month (series_store 直算) | 2026-04 | 2026-04 | 是 |
| 153 | ② | anchor_echo EA[5] metric_id | EA_HICP_YOY | EA_HICP_YOY | 是 |
| 154 | ② | anchor_echo EA[5] value (series_store 直算) | 4.0 | 4.0 | 是 |
| 155 | ② | anchor_echo EA[5] observation_month (series_store 直算) | 2026-10 | 2026-10 | 是 |
| 156 | ② | anchor_echo JP[0] metric_id | JP_POLICY_RATE | JP_POLICY_RATE | 是 |
| 157 | ② | anchor_echo JP[0] value (series_store 直算) | 0.727 | 0.727 | 是 |
| 158 | ② | anchor_echo JP[0] observation_month (series_store 直算) | 2026-04 | 2026-04 | 是 |
| 159 | ② | anchor_echo JP[1] metric_id | JP_POLICY_RATE | JP_POLICY_RATE | 是 |
| 160 | ② | anchor_echo JP[1] value (series_store 直算) | 1.227 | 1.227 | 是 |
| 161 | ② | anchor_echo JP[1] observation_month (series_store 直算) | 2026-10 | 2026-10 | 是 |
| 162 | ② | anchor_echo JP[2] metric_id | JP_CPI_YOY | JP_CPI_YOY | 是 |
| 163 | ② | anchor_echo JP[2] value (series_store 直算) | 1.38 | 1.38 | 是 |
| 164 | ② | anchor_echo JP[2] observation_month (series_store 直算) | 2026-04 | 2026-04 | 是 |
| 165 | ② | anchor_echo JP[3] metric_id | JP_CPI_YOY | JP_CPI_YOY | 是 |
| 166 | ② | anchor_echo JP[3] value (series_store 直算) | 2.44 | 2.44 | 是 |
| 167 | ② | anchor_echo JP[3] observation_month (series_store 直算) | 2026-10 | 2026-10 | 是 |
| 168 | ② | anchor_echo JP[4] metric_id | JP_CPI_TOKYO_YOY | JP_CPI_TOKYO_YOY | 是 |
| 169 | ② | anchor_echo JP[4] value (series_store 直算) | 1.42 | 1.42 | 是 |
| 170 | ② | anchor_echo JP[4] observation_month (series_store 直算) | 2026-04 | 2026-04 | 是 |
| 171 | ② | anchor_echo JP[5] metric_id | JP_CPI_TOKYO_YOY | JP_CPI_TOKYO_YOY | 是 |
| 172 | ② | anchor_echo JP[5] value (series_store 直算) | 2.73 | 2.73 | 是 |
| 173 | ② | anchor_echo JP[5] observation_month (series_store 直算) | 2026-10 | 2026-10 | 是 |
| 174 | ③ | series_store.EA_HICP_YOY@2025-10-01 | 2.1 | 2.1 / 百分之二点一 | 是 |
| 175 | ③ | series_store.JP_CPI_YOY@2025-10-01 | 2.99 | 2.99 / 百分之二点九九 | 是 |
| 176 | ③ | series_store.EA_HICP_YOY@2026-10-01 | 4.0 | 4.0 / 百分之四点零 | 是 |
| 177 | ③ | series_store.JP_CPI_YOY@2026-10-01 | 2.44 | 2.44 / 百分之二点四四 | 是 |
| 178 | ③ | EA@2026-10 − JP@2026-10 | 1.56 | 1.56 / 一点五六 | 是 |
| 179 | ③ | EA@2026-10 − EA@2025-10 | 1.9 | 1.9 / 一点九 | 是 |
| 180 | ③ | ¦JP@2026-10 − JP@2025-10¦ | 0.5500000000000003 | 0.55 / 零点五五 | 是 |
| 181 | ③ | 方向: EA 同比对照向上 | 上升 | (判据成立) | 是 |
| 182 | ③ | 方向: JP 同比对照向下 | 下降 | (判据成立) | 是 |
| 183 | ③ | 判断档文字 | 在场 | 在场 / 同比对照方向相反 | 是 |
| 184 | ③ | headline EA 2025-10 | 2.1 | 2.1 / 2.1 | 是 |
| 185 | ③ | headline JP 2025-10 | 2.99 | 2.99 / 2.99 | 是 |
| 186 | ③ | regions EA 相比去年同月 | 1.9 | 1.9 / 1.9 | 是 |
| 187 | ③ | regions JP ¦相比去年同月¦ | 0.5500000000000003 | 0.55 / 0.55 | 是 |
| 188 | ③ | series_store.JP_CPI_TOKYO_YOY 无 2025-10 观测 | [] | (判据成立) | 是 |
| 189 | ③ | series_store.JP_CPI_TOKYO_YOY.dates[0] | 2026-01 | 2026-01 / 2026-01 | 是 |
| 190 | ③ | series_store.JP_CPI_TOKYO_YOY 观测数 | 10 | 10 | 是 |
| 191 | ③ | 注册表 calc: JP_CPI_YOY=双基期档各自严格同月同比后拼接 | 0pp 告警),覆盖2021-01..2026-09;与官方公布值抽验一致(2026-09=2.16 vs 官方2.1) | (判据成立) | 是 |
| 192 | ③ | 注册表 calc: EA_HICP_YOY=年度变化率 | ECB Data Portal 系列 HICP.M.U2.N.000000.4D0.ANR(欧元区HICP年度变化率,未 | (判据成立) | 是 |
| 193 | ③ | 判断档文字 | 在场 | 在场 / 该序列为引擎按注册表口径自算的同比值——双基期档… | 是 |
| 194 | ③ | series_store.JP_CPI_YOY@2026-09-01 | 2.16 | 2.16 / 2.16 | 是 |
| 195 | ③ | 注册表 JP_CPI_YOY.calc 含官方抽验 | ;与官方公布值抽验一致(2026-09=2.16 vs 官方2.1) | (判据成立) | 是 |
| 196 | ④ | series_store.ECB_MRO 变更点 2026-06-17 | ["2026-06-17", 2.15, 2.4] | (判据成立) | 是 |
| 197 | ④ | series_store.ECB_MRO 变更幅 2026-06-17 | 25.0 | (判据成立) | 是 |
| 198 | ④ | series_store.ECB_MRO 变更点 2026-09-16 | ["2026-09-16", 2.4, 2.65] | (判据成立) | 是 |
| 199 | ④ | series_store.ECB_MRO 变更幅 2026-09-16 | 25.0 | (判据成立) | 是 |
| 200 | ④ | series_store.ECB_DFR 变更点 2026-06-17 | ["2026-06-17", 2.0, 2.25] | (判据成立) | 是 |
| 201 | ④ | series_store.ECB_DFR 变更幅 2026-06-17 | 25.0 | (判据成立) | 是 |
| 202 | ④ | series_store.ECB_DFR 变更点 2026-09-16 | ["2026-09-16", 2.25, 2.5] | (判据成立) | 是 |
| 203 | ④ | series_store.ECB_DFR 变更幅 2026-09-16 | 25.0 | (判据成立) | 是 |
| 204 | ④ | series_store.ECB_MRO 六个月窗内变更点数=2 | ["2026-06-17", "2026-09-16"] | (判据成立) | 是 |
| 205 | ④ | series_store.ECB_DFR 六个月窗内变更点数=2 | ["2026-06-17", "2026-09-16"] | (判据成立) | 是 |
| 206 | ④ | 独立推算: 2026-06-17 生效日前上一个周四 | 2026-06-11 | 2026-06-11 / 2026-06-11 | 是 |
| 207 | ④ | 序列变更日 2026-06-17 为周三 | 周三 | (判据成立) | 是 |
| 208 | ④ | 独立推算: 2026-09-16 生效日前上一个周四 | 2026-09-10 | 2026-09-10 / 2026-09-10 | 是 |
| 209 | ④ | 序列变更日 2026-09-16 为周三 | 周三 | (判据成立) | 是 |
| 210 | ④ | 判断档文字 | 在场 | 在场 / 决议日 2026-06-11 系引擎按『生效日前… | 是 |
| 211 | ④ | engine policy_dates.decision (最新一期) | 2026-09-10 | 2026-09-10 | 是 |
| 212 | ④ | engine policy_dates.decision (6个月前) | 2025-06-05 | 2025-06-05 | 是 |
| 213 | ④ | 独立推算: 2025-06-11 生效日前上一个周四 | 2025-06-05 | 2025-06-05 / 2025-06-05 | 是 |
| 214 | ④ | 冻结日历 ECB 条目数=0 | 0 | (判据成立) | 是 |
| 215 | ④ | 判断档文字 | 在场 | 在场 / 冻结发布日历对欧央行无实录条目 | 是 |
| 216 | ④ | 注册表 ECB_MRO.release_semantics 含「决议公布后生效并当日更新系列」 | ECB管委会金融政策决议公布后生效并当日更新系列 | (判据成立) | 是 |
| 217 | ④ | 判断档文字 | 在场 | 在场 / 注册表该序列 release_semantics… | 是 |
| 218 | ④ | 注册表 ECB_DFR.freshness.max_calendar_lag_days | 10 | 10 | 是 |
| 219 | ④ | 注册表 ECB_DFR.freshness.decision_dated | true | true | 是 |
| 220 | ④ | 注册表 ECB_MRO.freshness.decision_dated | true | true | 是 |
| 221 | ④ | gate_a.status | DEGRADED | DEGRADED | 是 |
| 222 | ④ | gate_a.noncore_degraded 含 ECB_DFR | true | true | 是 |
| 223 | ④ | facts.ECB_DFR.quality_status | DEGRADED | DEGRADED | 是 |
| 224 | ④ | gate_a.noncore_degraded 含 ECB_MRO | true | true | 是 |
| 225 | ④ | facts.ECB_MRO.quality_status | DEGRADED | DEGRADED | 是 |
| 226 | ④ | facts.ECB_DFR.observation_date 距截止日天数 | 68 | 68 / 68 | 是 |
| 227 | ④ | facts.ECB_DFR.issues[0].message 含「滞后68天(>10天」 | ECB_DFR观测日滞后68天(>10天有效窗,daily频;未发布或采集失败,不得当作最新一期) | (判据成立) | 是 |
| 228 | ④ | C3② 观测日距研究截止 | 68 | 68 / 六十八 | 是 |
| 229 | ④ | 契约 STALE 披露: 观测滞后 | 68 | 68 / 六十八 | 是 |
| 230 | ④ | engine point_values ECB_DFR 最新一期 status | ok | ok | 是 |
| 231 | ④ | 判断档文字 | 在场 | 在场 / 而研究计划点值格记该锚 status=ok,引擎… | 是 |
| 232 | ④ | 冻结日历 JP_POLICY_TARGET 条目数 | 2 | 2 | 是 |
| 233 | ④ | 冻结日历 决议条目.decision_date | 2026-09-18 | 2026-09-18 | 是 |
| 234 | ④ | 冻结日历 决议条目.effective_on | 2026-09-24 | 2026-09-24 | 是 |
| 235 | ④ | 冻结日历 决议条目.target_value | 1.25 | 1.25 | 是 |
| 236 | ④ | 冻结日历 决议条目.basis | user_directive | user_directive | 是 |
| 237 | ④ | 冻结日历 维持条目.decision_date | 2026-10-30 | 2026-10-30 | 是 |
| 238 | ④ | 冻结日历 维持条目.target_value | 1.25 | 1.25 | 是 |
| 239 | ④ | 冻结日历 维持条目.basis | user_directive | user_directive | 是 |
| 240 | ④ | 冻结日历 维持条目.kind | policy_maintenance | policy_maintenance | 是 |
| 241 | ④ | 冻结日历两条均无前值字段 | ["basis", "decision_date", "effective_on", "entry_id", "first_publish_… | (判据成立) | 是 |
| 242 | ④ | 判断档文字 | 在场 | 在场 / 2026-09-18 决议、2026-09-24… | 是 |
| 243 | ④ | 判断档文字 | 在场 | 在场 / 政策目标利率 1.25%,2026-09-18 … | 是 |
| 244 | ④ | 判断档文字 | 在场 | 在场 / 实录无前值,属【推断】 | 是 |
| 245 | ④ | 冻结日历 target_value | 1.25 | 1.25 / 一点二五 | 是 |
| 246 | ④ | 冻结日历 target_value | 1.25 | 1.25 / 1.25 | 是 |
| 247 | ④ | 冻结日历 target_value | 1.25 | 1.25 / 1.25 | 是 |
| 248 | ④ | 冻结日历 target_value | 1.25 | 1.25 / 1.25 | 是 |
| 249 | ④ | 冻结日历 target_value | 1.25 | 1.25 / 1.25 | 是 |
| 250 | ④ | 注册表无 JP_POLICY_TARGET | ["JP_POLICY_RATE"] | (判据成立) | 是 |
| 251 | ④ | series_store 无 JP_POLICY_TARGET | null | (判据成立) | 是 |
| 252 | ④ | engine dimension_gaps[0].gap | registry_absent | registry_absent | 是 |
| 253 | ④ | engine dimension_gaps[0].metric_id | JP_POLICY_TARGET | JP_POLICY_TARGET | 是 |
| 254 | ④ | 判断档文字 | 在场 | 在场 / 注册表无 JP_POLICY_TARGET(检索… | 是 |
| 255 | ④ | series_store.JP_POLICY_RATE@2025-11-01 | 0.478 | 0.478 / 零点四七八 | 是 |
| 256 | ④ | series_store.JP_POLICY_RATE@2026-10-01 | 1.227 | 1.227 / 一点二二七 | 是 |
| 257 | ④ | days(2026-10-30→截止) | 24 | 24 / 二十四 | 是 |
| 258 | ④ | series_store.ECB_MRO 末值 | 2.65 | 2.65 / 百分之二点六五 | 是 |
| 259 | ④ | series_store.ECB_MRO@2025-06-11 | 2.15 | 2.15 / 百分之二点一五 | 是 |
| 260 | ④ | MRO − 日银目标(日历) | 1.4 | 1.4 / 一点四 | 是 |
| 261 | ④ | DFR − 日银目标(日历) | 1.25 | 1.25 / 一点二五 | 是 |
| 262 | ④ | series_store.ECB_MRO 末值 | 2.65 | 2.65 / 二点六五 | 是 |
| 263 | ④ | series_store.ECB_DFR 末值 | 2.5 | 2.5 / 二点五 | 是 |
| 264 | ④ | 冻结日历 target_value | 1.25 | 1.25 / 一点二五 | 是 |
| 265 | ④ | ECB 单次变更幅(bp) | 25.0 | 25 / 二十五 | 是 |
| 266 | ④ | ECB 两次合计(bp) | 50.0 | 50 / 五十 | 是 |
| 267 | ④ | days(09-16 生效→09-24 生效) | 8 | 8 / 八 | 是 |
| 268 | ④ | days(09-10 决议→09-18 决议) | 8 | 8 / 八 | 是 |
| 269 | ④ | 09-16 生效在前、09-18 决议在后 | 2026-09-16<2026-09-18; 2026-09-10<2026-09-18 | (判据成立) | 是 |
| 270 | ④ | ECB 生效日与 BOJ 生效日同月(2026-09) | 2026-09 | (判据成立) | 是 |
| 271 | ④ | 判断档文字 | 在场 | 在场 / 月频证据下先后未定 | 是 |
| 272 | ④ | series_store.USDJPY@2026-11-23 | 159.347 | 159.35 / 159.35 | 是 |
| 273 | ④ | facts.USDJPY.value@2026-11-23 | 159.35 | 159.35 | 是 |
| 274 | ④ | facts.USDJPY.observation_date | 2026-11-23 | 2026-11-23 | 是 |
| 275 | ④ | series_store.SPX@2026-11-23 | 7203.850098 | 7203.85 / 7203.85 | 是 |
| 276 | ④ | facts.SPX.value@2026-11-23 | 7203.85 | 7203.85 | 是 |
| 277 | ④ | facts.SPX.observation_date | 2026-11-23 | 2026-11-23 | 是 |
| 278 | ④ | series_store.VIX@2026-11-23 | 27.01 | 27.01 / 27.01 | 是 |
| 279 | ④ | facts.VIX.value@2026-11-23 | 27.01 | 27.01 | 是 |
| 280 | ④ | facts.VIX.observation_date | 2026-11-23 | 2026-11-23 | 是 |
| 281 | ④ | series_store.JP_POLICY_RATE@2025-11 | 0.478 | 0.478 | 是 |
| 282 | ④ | series_store.JP_POLICY_RATE@2025-12 | 0.557 | 0.557 | 是 |
| 283 | ④ | series_store.JP_POLICY_RATE@2026-01 | 0.728 | 0.728 | 是 |
| 284 | ④ | series_store.JP_POLICY_RATE@2026-02 | 0.728 | 0.728 | 是 |
| 285 | ④ | series_store.JP_POLICY_RATE@2026-03 | 0.728 | 0.728 | 是 |
| 286 | ④ | series_store.JP_POLICY_RATE@2026-04 | 0.727 | 0.727 | 是 |
| 287 | ④ | series_store.JP_POLICY_RATE@2026-05 | 0.727 | 0.727 | 是 |
| 288 | ④ | series_store.JP_POLICY_RATE@2026-06 | 0.841 | 0.841 | 是 |
| 289 | ④ | series_store.JP_POLICY_RATE@2026-07 | 0.978 | 0.978 | 是 |
| 290 | ④ | series_store.JP_POLICY_RATE@2026-08 | 0.977 | 0.977 | 是 |
| 291 | ④ | series_store.JP_POLICY_RATE@2026-09 | 1.043 | 1.043 | 是 |
| 292 | ④ | series_store.JP_POLICY_RATE@2026-10 | 1.227 | 1.227 | 是 |
| 293 | ④ | JP 月均 6个月锚间净变动(bp) | 50.000000000000014 | 50 / 五十 | 是 |
| 294 | ④ | JP 月均 6个月锚间净变动(bp) | 50.000000000000014 | 50 / 50 | 是 |
| 295 | ④ | JP 月均 四台阶之和(bp) | 50.10000000000001 | 50 / 50 | 是 |
| 296 | ④ | JP 月均 近12月净变动(bp) | 74.9 | 75 / 75 | 是 |
| 297 | ④ | JP 月均 引擎一年窗净变动(bp) | 74.9 | 75 / 75 | 是 |
| 298 | ④ | policy_window_path JP 事件数 | 6 | 6 | 是 |
| 299 | ④ | policy_window_path JP net_bp | 75 | 75 | 是 |
| 300 | ④ | policy_window_path JP delta_bp 之和=75 | 75 | (判据成立) | 是 |
| 301 | ④ | policy_window_path JP 六事件与 series_store 变更点(幅>=0.5bp)逐项一致 | series_store 一年窗内原始变更点: [('2025-12-01', 7.9), ('2026-01-01', 17.1), ('… | (判据成立) | 是 |
| 302 | ④ | policy_window_path JP window | ["2025-11-23", "2026-11-23"] | ["2025-11-23", "2026-11-23"] | 是 |
| 303 | ④ | policy_window_path JP window_start_observation | 2025-11-01 | 2025-11-01 | 是 |
| 304 | ④ | 判断档文字 | 在场 | 在场 / 窗口 2025-11-23..2026-11-2… | 是 |
| 305 | ④ | 判断档文字 | 在场 | 在场 / 净 +75bp=六个变动点之和 | 是 |
| 306 | ④ | policy_window_path ECB_MRO events | [["2026-06-17", 2.15, 2.4, 25, "2026-06-11"], ["2026-09-16", 2.4, 2.65… | [["2026-06-17", 2.15, 2.4, 25, "2026-06-11"], ["20… | 是 |
| 307 | ④ | policy_window_path ECB_MRO net_bp | 50 | 50 | 是 |
| 308 | ④ | policy_window_path ECB_DFR events | [["2026-06-17", 2.0, 2.25, 25, "2026-06-11"], ["2026-09-16", 2.25, 2.5… | [["2026-06-17", 2.0, 2.25, 25, "2026-06-11"], ["20… | 是 |
| 309 | ④ | policy_window_path ECB_DFR net_bp | 50 | 50 | 是 |
| 310 | ④ | series_store.ECB_MRO@2026-06-17 | 2.4 | 2.4 / 2.4 | 是 |
| 311 | ④ | series_store.ECB_DFR@2026-06-17 | 2.25 | 2.25 / 2.25 | 是 |
| 312 | ④ | series_store.ECB_MRO@2026-09-16 | 2.65 | 2.65 / 2.65 | 是 |
| 313 | ④ | series_store.ECB_DFR@2026-09-16 | 2.5 | 2.5 / 2.5 | 是 |
| 314 | ④ | series_store.ECB_MRO@2025-06-11 | 2.15 | 2.15 / 2.15 | 是 |
| 315 | ④ | series_store.ECB_DFR@2025-06-11 | 2.0 | 2.0 / 2.0 | 是 |
| 316 | ④ | series_store.JP_POLICY_RATE@2026-10 | 1.227 | 1.227 / 1.227 | 是 |
| 317 | ④ | series_store.JP_POLICY_RATE@2026-04 | 0.727 | 0.727 / 0.727 | 是 |
| 318 | ④ | series_store.JP_POLICY_RATE@2026-06 | 0.841 | 0.841 / 0.841 | 是 |
| 319 | ④ | series_store.JP_POLICY_RATE@2026-07 | 0.978 | 0.978 / 0.978 | 是 |
| 320 | ④ | series_store.JP_POLICY_RATE@2026-09 | 1.043 | 1.043 / 1.043 | 是 |
| 321 | ④ | series_store.JP_POLICY_RATE@2026-10 | 1.227 | 1.227 / 1.227 | 是 |
| 322 | ④ | series_store.JP_POLICY_RATE@2026-08 | 0.977 | 0.977 / 0.977 | 是 |
| 323 | ④ | series_store.JP_POLICY_RATE@2025-11 | 0.478 | 0.478 / 0.478 | 是 |
| 324 | ④ | series_store.ECB_MRO 末值 | 2.65 | 2.65 / 2.65 | 是 |
| 325 | ④ | series_store.ECB_DFR 末值 | 2.5 | 2.5 / 2.5 | 是 |
| 326 | ④ | series_store.ECB_MRO 末值 | 2.65 | 2.65 / 2.65 | 是 |
| 327 | ④ | 冻结日历 target_value | 1.25 | 1.25 / 1.25 | 是 |
| 328 | ④ | series_store.DFEDTARU 最近变更日 | 2026-09-17 | 2026-09-17 / 2026-09-17 | 是 |
| 329 | ④ | series_store.DFEDTARL 最近变更日 | 2026-09-17 | 2026-09-17 / 2026-09-17 | 是 |
| 330 | ④ | series_store.DFEDTARL@2026-11-23 | 3.75 | 3.75 / 3.75 | 是 |
| 331 | ④ | series_store.DFEDTARU@2026-11-23 | 4.0 | 4.0 / 4.00 | 是 |
| 332 | ④ | series_store.DFEDTARL/DFEDTARU 末观测日 | 2026-11-23 | 2026-11-23 / 2026-11-23 | 是 |
| 333 | ④ | DFEDTARL/DFEDTARU 不在证据索引 | [] | (判据成立) | 是 |
| 334 | ④ | 窗(2026-10-23..截止)内 ECB/Fed 序列无变更点 | none | (判据成立) | 是 |
| 335 | ④ | 窗(2026-10-23..截止)内 JP 月均观测日口径无变更点 | none | (判据成立) | 是 |
| 336 | ④ | 判断档文字 | 在场 | 在场 / 窗内三地均无政策利率变动点(序列面最近变动: 欧… | 是 |
| 337 | ④ | days(2025-06-11→2026-06-17) 两序列维持期 | 371 | 371 / 371 | 是 |
| 338 | ④ | 2025-06-11 至 2026-06-17 间两序列无变更点 | none | (判据成立) | 是 |
| 339 | ④ | days(2026-06-17→2026-09-16) 两次变更间隔 | 91 | 91 / 91 | 是 |
| 340 | ③ | EA_HICP_YOY@2026-04 | 3.0 | 3.0 / 百分之三点零 | 是 |
| 341 | ③ | JP_CPI_YOY@2026-04 | 1.38 | 1.38 / 百分之一点三八 | 是 |
| 342 | ③ | EA 锚间变化 4.0-3.0 | 1.0 | 1.0 / 一 | 是 |
| 343 | ③ | JP 锚间变化 2.44-1.38 | 1.06 | 1.0 / 一 | 是 |
| 344 | ③ | EA 自 2026-06 期起算 4.0-2.8 | 1.2000000000000002 | 1.2 / 一点二 | 是 |
| 345 | ③ | JP 自 2026-06 期起算 2.44-1.67 | 0.77 | 0.77 / 零点七七 | 是 |
| 346 | ③ | EA 自 2026-05 期起算 4.0-3.2 | 0.7999999999999998 | 0.8 / 零点八 | 是 |
| 347 | ③ | JP 自 2026-05 期起算 2.44-1.53 | 0.9099999999999999 | 0.91 / 零点九一 | 是 |
| 348 | ③ | 快慢互换: 自06期 EA快 / 自05期 JP快 | 成立 | (判据成立) | 是 |
| 349 | ③ | JP_CPI_TOKYO_YOY@2026-10 | 2.73 | 2.73 / 百分之二点七三 | 是 |
| 350 | ③ | JP_CPI_TOKYO_YOY 2026-10 观测月 | 2026-10 | 2026-10 / 2026-10 | 是 |
| 351 | ③ | 推定发布规则 东京 2026-10 (月末-1天) | 2026-10-30 | 2026-10-30 / 2026-10-30 | 是 |
| 352 | ③ | 同月两者均较前月上行: 东京 2.73>2.69 且 全国 2.44>2.16 | [2.69, 2.16] | (判据成立) | 是 |
| 353 | ③ | 判断档文字 | 在场 | 在场 / 与全国口径方向一致——同月两者均较前月上行 | 是 |
| 354 | ③ | facts.JP_CPI_YOY.quality_status | WARN | WARN | 是 |
| 355 | ③ | facts.EA_HICP_YOY.quality_status | WARN | WARN | 是 |
| 356 | ③ | series_store.JP_CPI_TOKYO_YOY 无事实行 | null | (判据成立) | 是 |
| 357 | ⑥ | JP_CPI_TOKYO_YOY@2026-04 | 1.42 | 1.42 / 1.42 | 是 |
| 358 | ⑥ | JP_CPI_TOKYO_YOY@2026-10 | 2.73 | 2.73 / 2.73 | 是 |
| 359 | ⑦ | EA_HICP_YOY@2026-05 | 3.2 | 3.2 / 3.2 | 是 |
| 360 | ⑦ | EA_HICP_YOY@2026-06 | 2.8 | 2.8 / 2.8 | 是 |
| 361 | ⑦ | EA_HICP_YOY@2026-07 | 2.9 | 2.9 / 2.9 | 是 |
| 362 | ⑦ | EA_HICP_YOY@2026-08 | 3.2 | 3.2 / 3.2 | 是 |
| 363 | ⑦ | EA_HICP_YOY@2026-09 | 3.8 | 3.8 / 3.8 | 是 |
| 364 | ⑦ | EA_HICP_YOY@2026-10 | 4.0 | 4.0 / 4.0 | 是 |
| 365 | ⑦ | JP_CPI_YOY@2026-05 | 1.53 | 1.53 / 1.53 | 是 |
| 366 | ⑬ | 窗内逐月路径 JP 2026-05 | 1.53 | 1.53 / 1.53 | 是 |
| 367 | ⑦ | JP_CPI_YOY@2026-06 | 1.67 | 1.67 / 1.67 | 是 |
| 368 | ⑬ | 窗内逐月路径 JP 2026-06 | 1.67 | 1.67 / 1.67 | 是 |
| 369 | ⑦ | JP_CPI_YOY@2026-07 | 1.97 | 1.97 / 1.97 | 是 |
| 370 | ⑬ | 窗内逐月路径 JP 2026-07 | 1.97 | 1.97 / 1.97 | 是 |
| 371 | ⑦ | JP_CPI_YOY@2026-08 | 1.98 | 1.98 / 1.98 | 是 |
| 372 | ⑬ | 窗内逐月路径 JP 2026-08 | 1.98 | 1.98 / 1.98 | 是 |
| 373 | ⑦ | JP_CPI_YOY@2026-09 | 2.16 | 2.16 / 2.16 | 是 |
| 374 | ⑬ | 窗内逐月路径 JP 2026-09 | 2.16 | 2.16 / 2.16 | 是 |
| 375 | ⑦ | JP_CPI_YOY@2026-10 | 2.44 | 2.44 / 2.44 | 是 |
| 376 | ⑬ | 窗内逐月路径 JP 2026-10 | 2.44 | 2.44 / 2.44 | 是 |
| 377 | ⑦ | 窗内各月 EA-JP 最小差 | 0.9299999999999999 | 0.93 / 0.93 | 是 |
| 378 | ⑦ | 窗内各月 EA-JP 最大差 | 1.6700000000000002 | 1.67 / 1.67 | 是 |
| 379 | ⑦ | 欧元区 2026-06 一度回落至 2.8 | 非逐月单调 | (判据成立) | 是 |
| 380 | ⑦ | 日本 2026-05..10 逐月上行 | [["2026-05", 1.53], ["2026-06", 1.67], ["2026-07", 1.97], ["2026-08", … | (判据成立) | 是 |
| 381 | ① | 2026-05 期观测日早于窗起 | ["2026-05-01", "2026-05-01"] | (判据成立) | 是 |
| 382 | ① | 2026-05 期观测日 | 2026-05-01 | 2026-05-01 / 2026-05-01 | 是 |
| 383 | ① | 2026-05 期推定发布日在窗内 | ["2026-06-16", "2026-06-20"] | (判据成立) | 是 |
| 384 | ① | 推定发布规则 EA 2026-05 | 2026-06-16 | 2026-06-16 / 2026-06-16 | 是 |
| 385 | ① | 推定发布规则 JP 2026-05 | 2026-06-20 | 2026-06-20 / 2026-06-20 | 是 |
| 386 | ① | 2026-06..10 期观测与推定发布均在窗内 | ok | (判据成立) | 是 |
| 387 | ⑥ | EA_HICP_YOY 谷底→2026-05 | 3.2 | 3.2 / 3.2 | 是 |
| 388 | ⑥ | EA_HICP_YOY 2026-02 谷底 | 1.9 | 1.9 / 1.9 | 是 |
| 389 | ⑥ | 三个月变化 3.2-1.9 | 1.3000000000000003 | 1.3 / 1.30 | 是 |
| 390 | ⑥ | 引擎候选 EA_HICP 2026-02→05 属 ¦三个月变化¦ 最大者集合(并列最大集合直算) | [["2026-01", "2026-04", 1.7, 3.0, 1.3], ["2026-02", "2026-05", 1.9, 3.… | (判据成立) | 是 |
| 391 | ⑥ | JP_CPI_YOY 2026-02 谷底 | 1.27 | 1.27 / 1.27 | 是 |
| 392 | ⑥ | JP_CPI_YOY@2026-05 | 1.53 | 1.53 / 1.53 | 是 |
| 393 | ⑥ | turnings[0].value_before | 1.9 | 1.9 | 是 |
| 394 | ⑥ | turnings[0].value_after | 3.2 | 3.2 | 是 |
| 395 | ⑥ | 近12月谷底: EA 2026-01 的 1.7 | [1.7, "2026-01"] | (判据成立) | 是 |
| 396 | ⑥ | 近12月谷底: JP 2026-02 的 1.27 | [1.27, "2026-02"] | (判据成立) | 是 |
| 397 | ⑥ | 近12月最高: EA 2026-10 的 4.0 | [4.0, "2026-10"] | (判据成立) | 是 |
| 398 | ⑥ | JP_CPI_YOY@2025-11 | 2.9 | 2.9 / 2.9 | 是 |
| 399 | ⑥ | JP_CPI_YOY@2026-02 | 1.27 | 1.27 / 1.27 | 是 |
| 400 | ⑥ | 三个月变化 1.27-2.9 | 1.63 | 1.63 / 1.63 | 是 |
| 401 | ⑥ | JP_CPI 幅度最大候选=2025-11→2026-02 | ["2025-11", "2026-02", 2.9, 1.27, -1.63] | (判据成立) | 是 |
| 402 | ⑥ | 四指标中 ¦三个月变化¦ 最大者=JP_CPI 2025-11→02 | [1.3, -1.63, 1.09, 0.251] | (判据成立) | 是 |
| 403 | ⑥ | EA_HICP_YOY@2026-06 | 2.8 | 2.8 / 2.8 | 是 |
| 404 | ⑥ | EA_HICP_YOY@2026-07 | 2.9 | 2.9 / 2.9 | 是 |
| 405 | ⑥ | EA_HICP_YOY@2026-08 | 3.2 | 3.2 / 3.2 | 是 |
| 406 | ⑥ | EA_HICP_YOY@2026-09 | 3.8 | 3.8 / 3.8 | 是 |
| 407 | ⑥ | EA_HICP_YOY@2026-10 | 4.0 | 4.0 / 4.0 | 是 |
| 408 | ⑥ | engine turning_candidates 数 | 4 | 4 | 是 |
| 409 | ⑥ | engine candidate EA_HICP_YOY from/to | ["2026-02", "2026-05", 1.9, 3.2] | ["2026-02", "2026-05", 1.9, 3.2] | 是 |
| 410 | ⑥ | engine candidate JP_CPI_YOY from/to | ["2025-11", "2026-02", 2.9, 1.27] | ["2025-11", "2026-02", 2.9, 1.27] | 是 |
| 411 | ⑥ | engine candidate JP_CPI_TOKYO_YOY from/to | ["2026-06", "2026-09", 1.6, 2.69] | ["2026-06", "2026-09", 1.6, 2.69] | 是 |
| 412 | ⑥ | engine candidate JP_POLICY_RATE from/to | ["2026-04", "2026-07", 0.727, 0.978] | ["2026-04", "2026-07", 0.727, 0.978] | 是 |
| 413 | ⑥ | JP_POLICY_RATE@2026-07 | 0.978 | 0.978 / 0.978 | 是 |
| 414 | ⑥ | JP_POLICY_RATE@2026-04 | 0.727 | 0.727 / 0.727 | 是 |
| 415 | ⑥ | JP_POLICY_RATE@2026-06 | 0.841 | 0.841 / 0.841 | 是 |
| 416 | ⑥ | turnings[1].value_before/after | [0.727, 0.978] | [0.727, 0.978] | 是 |
| 417 | ⑥ | JP_CPI_TOKYO_YOY@2026-06 | 1.6 | 1.6 / 1.6 | 是 |
| 418 | ⑥ | JP_CPI_TOKYO_YOY@2026-09 | 2.69 | 2.69 / 2.69 | 是 |
| 419 | ⑥ | 东京三个月变化 2.69-1.6 | 1.0899999999999999 | 1.09 / 1.09 | 是 |
| 420 | ⑥ | turnings[2].value_before/after | [1.6, 2.69] | [1.6, 2.69] | 是 |
| 421 | ⑥ | JP_CPI_YOY@2026-06 | 1.67 | 1.67 / 1.67 | 是 |
| 422 | ⑥ | JP_CPI_YOY@2026-08 | 1.98 | 1.98 / 1.98 | 是 |
| 423 | ⑥ | JP−EA 2026-09 期水平差绝对值 | 1.6399999999999997 | 1.64 / 1.64 | 是 |
| 424 | ⑥ | 方向: 2026-09 期日本全国低于欧元区 | -1.64 | (判据成立) | 是 |
| 425 | ⑥ | EA−东京 2026-09 期水平差 | 1.1099999999999999 | 1.11 / 1.11 | 是 |
| 426 | ⑥ | TK−EA 2026-09 期水平差 | 1.1099999999999999 | 1.11 / 1.11 | 是 |
| 427 | ⑥ | 两水平差均为负(日本低于欧元区) | 负 | (判据成立) | 是 |
| 428 | ⑥ | EA_HICP_YOY@2026-09 | 3.8 | 3.8 / 3.8 | 是 |
| 429 | ⑥ | 推定发布规则 东京 2026-09 | 2026-09-29 | 2026-09-29 / 2026-09-29 | 是 |
| 430 | ⑥ | 东京 2026-09 推定发布日 晚于 2026-09-18 | 2026-09-29 | (判据成立) | 是 |
| 431 | ⑥ | 推定发布规则 东京 2026-08 | 2026-08-30 | 2026-08-30 / 2026-08-30 | 是 |
| 432 | ⑥ | 决议前(2026-09-18)可见最近东京读数=2026-08 | ["2026-08-01", 1.9] | (判据成立) | 是 |
| 433 | ⑥ | JP_CPI_TOKYO_YOY@2026-08 | 1.9 | 1.9 / 1.9 | 是 |
| 434 | ⑥ | 月末-1天推定日 vs 当月最后周五: 2026-06 不一致 / 2026-10 一致 | ["2026-06-29", "2026-06-26", "2026-10-30", "2026-10-30"] | (判据成立) | 是 |
| 435 | ⑥ | JP_CPI_YOY 2026-03→04 回落 | 0.08000000000000007 | 0.08 / 0.08 | 是 |
| 436 | ⑥ | JP_CPI_YOY@2026-03 | 1.46 | 1.46 / 1.46 | 是 |
| 437 | ⑥ | JP_CPI_YOY@2025-01 | 4.03 | 4.03 / 4.03 | 是 |
| 438 | ⑥ | JP_CPI_YOY@2025-09 | 2.91 | 2.91 / 2.91 | 是 |
| 439 | ⑥ | JP_CPI_YOY@2025-10 | 2.99 | 2.99 / 2.99 | 是 |
| 440 | ⑥ | JP_CPI 2025-01 为 2024-01 以来最高且为局部高点(全序列最高为 2023-01 的 4.31, 高于 2025-01; 文称「2025-01 高点 4.03」… | {"2024-12": 3.62, "2025-01": 4.03, "2025-02": 3.66, "allmax": [4.31, "… | (判据成立) | 是 |
| 441 | ⑥ | 2025-01 之后至 2026-02 总体回落(末<起 且 2026-02 为其间最低) | ok | (判据成立) | 是 |
| 442 | ⑥ | 2026-02 之后总体回升至 2026-10(最高在 2026-10) | ok | (判据成立) | 是 |
| 443 | ⑥ | 决议日(回推 06-11)前可见 EA 读数=2026-04 | ["2026-04-01", 3.0] | (判据成立) | 是 |
| 444 | ⑥ | c.vis(EA, 2026-06-11) | 3.0 | 3.0 / 3.0 | 是 |
| 445 | ⑥ | 生效日(06-17)前可见 EA 读数=2026-05 | ["2026-05-01", 3.2] | (判据成立) | 是 |
| 446 | ⑥ | c.vis(EA, 2026-06-17) | 3.2 | 3.2 / 3.2 | 是 |
| 447 | ⑥ | 决议日(回推 09-10)前可见 EA 读数=2026-07 | ["2026-07-01", 2.9] | (判据成立) | 是 |
| 448 | ⑥ | c.vis(EA, 2026-09-10) | 2.9 | 2.9 / 2.9 | 是 |
| 449 | ⑥ | 生效日(09-16)前可见 EA 读数=2026-08 | ["2026-08-01", 3.2] | (判据成立) | 是 |
| 450 | ⑥ | c.vis(EA, 2026-09-16) | 3.2 | 3.2 / 3.2 | 是 |
| 451 | ⑥ | 推定发布规则 EA 2026-08 | 2026-09-16 | 2026-09-16 / 2026-09-16 | 是 |
| 452 | ⑥ | 两次变更前可见读数(3.0/3.2/2.9/3.2)均高于 2026-02 的 1.9 | ok | (判据成立) | 是 |
| 453 | ⑥ | 快报形态(次月首日)下决议日前可见: 06-11→2026-05, 09-10→2026-08 | ok | (判据成立) | 是 |
| 454 | ⑥ | EA@2026-01 | 1.7 | 1.7 / 1.7 | 是 |
| 455 | ⑥ | 2026-01→04: 1.7→3.0 而两序列未变更 | ok | (判据成立) | 是 |
| 456 | ⑥ | 2026-05=3.2 为 2026-01..08 区间峰值(并列 2026-08) | ["2026-05", "2026-08"] | (判据成立) | 是 |
| 457 | ⑥ | BOJ 决议前(09-18)可见全国读数=2026-07 | ["2026-07-01", 1.97] | (判据成立) | 是 |
| 458 | ⑥ | 推定发布规则 JP 2026-08 | 2026-09-20 | 2026-09-20 / 2026-09-20 | 是 |
| 459 | ⑦ | series_store.EURUSD@2026-10-23 | 1.122146 | 1.1221 / 1.1221 | 是 |
| 460 | ⑦ | series_store.EURUSD@2026-11-20 | 1.096972 | 1.097 / 1.097 | 是 |
| 461 | ⑦ | EURUSD 10-23→11-20 % | 2.2433800949252625 | 2.24 / 2.24 | 是 |
| 462 | ⑦ | EURUSD 10-23→11-20 方向=下降 | -2.243 | (判据成立) | 是 |
| 463 | ⑦ | series_store.USDJPY@2026-10-23 | 156.494003 | 156.494 / 156.494 | 是 |
| 464 | ⑦ | series_store.USDJPY@2026-11-20 | 159.707001 | 159.707 / 159.707 | 是 |
| 465 | ⑦ | USDJPY 10-23→11-20 % | 2.053112540037705 | 2.05 / 2.05 | 是 |
| 466 | ⑦ | series_store.DXY@2026-10-23 | 101.809998 | 101.81 / 101.81 | 是 |
| 467 | ⑦ | series_store.DXY@2026-11-20 | 103.809998 | 103.81 / 103.81 | 是 |
| 468 | ⑦ | DXY 10-23→11-20 % | 1.9644436099488072 | 1.96 / 1.96 | 是 |
| 469 | ⑦ | series_store.EURUSD@2026-11-23 | 1.093972 | 1.094 / 1.094 | 是 |
| 470 | ⑦ | EURUSD 10-23→11-23 % | 2.51072498587529 | 2.51 / 2.51 | 是 |
| 471 | ⑦ | EURUSD 10-23→11-23 方向=下降 | -2.511 | (判据成立) | 是 |
| 472 | ⑦ | series_store.USDJPY@2026-11-23 | 159.347 | 159.347 / 159.347 | 是 |
| 473 | ⑦ | USDJPY 10-23→11-23 % | 1.8230711371093333 | 1.82 / 1.82 | 是 |
| 474 | ⑦ | series_store.DXY@2026-11-23 | 104.079002 | 104.079 / 104.079 | 是 |
| 475 | ⑦ | DXY 10-23→11-23 % | 2.2286652043741473 | 2.23 / 2.23 | 是 |
| 476 | ⑦ | EURUSD×USDJPY@10-23 | 175.60911949043802 | 175.61 / 175.61 | 是 |
| 477 | ⑦ | EURUSD×USDJPY@11-20 | 175.194108300972 | 175.19 / 175.19 | 是 |
| 478 | ⑦ | EURJPY 合成 10-23→11-20 % | 0.23632667293717047 | 0.24 / 0.24 | 是 |
| 479 | ⑦ | EURJPY 合成 10-23→11-20 方向=下降 | -0.236 | (判据成立) | 是 |
| 480 | ⑦ | EURUSD×USDJPY@11-23 | 174.321156284 | 174.32 / 174.32 | 是 |
| 481 | ⑦ | EURJPY 合成 10-23→11-23 % | 0.7334261513156415 | 0.73 / 0.73 | 是 |
| 482 | ⑦ | EURJPY 合成 10-23→11-23 方向=下降 | -0.733 | (判据成立) | 是 |
| 483 | ⑦ | 方向: 欧元对美元走弱、日元对美元走弱、美元指数上行 | ok | (判据成立) | 是 |
| 484 | ⑦ | series_store.UST_10Y@2026-11-19 | 5.04 | 5.04 / 5.04 | 是 |
| 485 | ⑦ | UST_10Y(5.04) 高于 MRO(2.65) 与 BOJ 目标(1.25) | ok | (判据成立) | 是 |
| 486 | ⑦ | engine asset_moves.DXY.chg_pct | 2.23 | 2.23 | 是 |
| 487 | ⑤ | engine asset_moves.SPX chg_pct (series_store 直算) | -5.51 | -5.51 | 是 |
| 488 | ⑤ | engine asset_moves.SPX from_value | 7623.680176 | 7623.680176 | 是 |
| 489 | ⑤ | engine asset_moves.SPX to_value | 7203.850098 | 7203.850098 | 是 |
| 490 | ⑤ | engine asset_moves.SHCOMP chg_pct (series_store 直算) | -4.11 | -4.11 | 是 |
| 491 | ⑤ | engine asset_moves.SHCOMP from_value | 3690.4753 | 3690.4753 | 是 |
| 492 | ⑤ | engine asset_moves.SHCOMP to_value | 3538.948 | 3538.948 | 是 |
| 493 | ⑤ | engine asset_moves.DAX chg_pct (series_store 直算) | 0.11 | 0.11 | 是 |
| 494 | ⑤ | engine asset_moves.DAX from_value | 25181.650391 | 25181.650391 | 是 |
| 495 | ⑤ | engine asset_moves.DAX to_value | 25209.449219 | 25209.449219 | 是 |
| 496 | ⑤ | engine asset_moves.NIKKEI225 chg_pct (series_store 直算) | -9.98 | -9.98 | 是 |
| 497 | ⑤ | engine asset_moves.NIKKEI225 from_value | 62693.16 | 62693.16 | 是 |
| 498 | ⑤ | engine asset_moves.NIKKEI225 to_value | 56436.65 | 56436.65 | 是 |
| 499 | ⑤ | engine asset_moves.VIX chg_pct (series_store 直算) | 38.87 | 38.87 | 是 |
| 500 | ⑤ | engine asset_moves.VIX from_value | 19.450001 | 19.450001 | 是 |
| 501 | ⑤ | engine asset_moves.VIX to_value | 27.01 | 27.01 | 是 |
| 502 | ⑤ | engine asset_moves.DXY chg_pct (series_store 直算) | 2.23 | 2.23 | 是 |
| 503 | ⑤ | engine asset_moves.DXY from_value | 101.809998 | 101.809998 | 是 |
| 504 | ⑤ | engine asset_moves.DXY to_value | 104.079002 | 104.079002 | 是 |
| 505 | ⑤ | engine asset_moves.GOLD_F chg_pct (series_store 直算) | -8.05 | -8.05 | 是 |
| 506 | ⑤ | engine asset_moves.GOLD_F from_value | 4007.899902 | 4007.899902 | 是 |
| 507 | ⑤ | engine asset_moves.GOLD_F to_value | 3685.199951 | 3685.199951 | 是 |
| 508 | ⑤ | engine asset_moves.UST_10Y chg_pct (series_store 直算) | 0.8 | 0.8 | 是 |
| 509 | ⑤ | engine asset_moves.UST_10Y from_value | 5.0 | 5.0 | 是 |
| 510 | ⑤ | engine asset_moves.UST_10Y to_value | 5.04 | 5.04 | 是 |
| 511 | ⑦ | SPX 10-23→11-20 % | 9.356242950032168 | 9.36 / 9.36 | 是 |
| 512 | ⑦ | SPX 方向词与符号 | -9.3562 | (判据成立) | 是 |
| 513 | ⑦ | NIKKEI225 10-23→11-20 % | 9.979573529233498 | 9.98 / 9.98 | 是 |
| 514 | ⑦ | NIKKEI225 方向词与符号 | -9.9796 | (判据成立) | 是 |
| 515 | ⑦ | DAX 10-23→11-20 % | 1.5045522756340413 | 1.5 / 1.5 | 是 |
| 516 | ⑦ | DAX 方向词与符号 | -1.5046 | (判据成立) | 是 |
| 517 | ⑦ | CAC40 10-23→11-20 % | 1.8621807940751411 | 1.86 / 1.86 | 是 |
| 518 | ⑦ | CAC40 方向词与符号 | 1.8622 | (判据成立) | 是 |
| 519 | ⑦ | VIX@10-23 | 19.450001 | 19.45 / 19.45 | 是 |
| 520 | ⑦ | VIX@11-20 | 35.889999 | 35.89 / 35.89 | 是 |
| 521 | ⑦ | VIX 10-23→11-20 % | 84.52440696532612 | 84.5 / 84.5 | 是 |
| 522 | ⑦ | series_store.VIX@2026-11-13 | 19.299999 | 19.3 / 19.3 | 是 |
| 523 | ⑦ | series_store.VIX@2026-11-16 | 22.91 | 22.91 / 22.91 | 是 |
| 524 | ⑦ | series_store.VIX@2026-11-17 | 25.459999 | 25.46 / 25.46 | 是 |
| 525 | ⑦ | series_store.VIX@2026-11-18 | 24.559999 | 24.56 / 24.56 | 是 |
| 526 | ⑦ | series_store.VIX@2026-11-19 | 28.440001 | 28.44 / 28.44 | 是 |
| 527 | ⑦ | series_store.VIX@2026-11-20 | 35.889999 | 35.89 / 35.89 | 是 |
| 528 | ⑦ | 跳升窗 2026-11-13→11-20 含 5 个交易日(不含起点日) | ["2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19",… | (判据成立) | 是 |
| 529 | ⑦ | 末六个交易日收盘路径=11-13..11-20(截止日前的最后六个观测; 11-21/22 为周末, 11-23 为截止日盘中) | ["2026-11-13", "2026-11-16", "2026-11-17", "2026-11-18", "2026-11-19",… | (判据成立) | 是 |
| 530 | ⑦ | 资产月窗 SPX chg_pct 10-23→11-23 | 5.506921438305623 | 5.51 / 5.51 | 是 |
| 531 | ⑦ | 资产月窗 DAX chg_pct 10-23→11-23 | 0.11039319333070452 | 0.11 / 0.11 | 是 |
| 532 | ⑦ | 资产月窗 NIKKEI225 chg_pct 10-23→11-20 | 9.979573529233498 | 9.98 / 9.98 | 是 |
| 533 | ⑦ | 资产月窗 VIX chg_pct 10-23→11-23 | 38.86888746175386 | 38.87 / 38.87 | 是 |
| 534 | ⑦ | series_store.DAX@2026-11-23 | 25209.449219 | 25209.45 / 25209.45 | 是 |
| 535 | ⑦ | series_store.NIKKEI225@2026-11-20 | 56436.65 | 56436.65 / 56436.65 | 是 |
| 536 | ⑦ | VIX 11-20 收盘→11-23 盘中 % | 24.742265944337305 | 24.7 / 24.7 | 是 |
| 537 | ⑦ | 方向词: 较 11-20 收盘为负 | -24.742 | (判据成立) | 是 |
| 538 | ⑦ | series_store.VIX@2026-11-04 | 16.610001 | 16.61 / 16.61 | 是 |
| 539 | ⑦ | series_store.VIX@2026-11-05 | 28.18 | 28.18 / 28.18 | 是 |
| 540 | ⑦ | VIX 11-04→11-05 % | 69.65682301885472 | 69.66 / 69.66 | 是 |
| 541 | ⑦ | series_store.VIX@2026-11-11 | 17.49 | 17.49 / 17.49 | 是 |
| 542 | ⑦ | 11-05→11-11 四个交易日 | ["2026-11-06", "2026-11-09", "2026-11-10", "2026-11-11"] | (判据成立) | 是 |
| 543 | ⑦ | VIX 11-05→11-11 % | 37.9347054648687 | 37.93 / 37.93 | 是 |
| 544 | ⑦ | SPX 11-05 单日 % | 4.3556598180672035 | 4.36 / 4.36 | 是 |
| 545 | ⑦ | NIKKEI225 11-06 单日 % | 5.964727012552828 | 5.96 / 5.96 | 是 |
| 546 | ⑦ | 负号方向: SPX 月窗/NIKKEI 月窗/VIX 11-20→11-23/VIX 11-05→11-11/SPX 11-05/NIKKEI 11-06 均为负 | [-5.507, -9.98, -24.742, -37.935, -4.356, -5.965] | (判据成立) | 是 |
| 547 | ⑦ | NIKKEI225 11-05 的下一交易日=11-06 | ok | (判据成立) | 是 |
| 548 | ⑦ | VIX 11-13→11-16 单日 % | 18.704669362936244 | 18.7 / 18.70 | 是 |
| 549 | ⑦ | VIX 11-19→11-20 单日 % | 26.195491343337164 | 26.2 / 26.20 | 是 |
| 550 | ⑦ | 11-16/11-20 为跳升窗内两个最大单日跳升日 | [["2026-11-16", 18.7], ["2026-11-17", 11.13], ["2026-11-18", -3.53], [… | (判据成立) | 是 |
| 551 | ⑦ | SPX 11-13→11-20 % | 8.612909472617414 | 8.61 / 8.61 | 是 |
| 552 | ⑦ | NIKKEI225 11-13→11-20 % | 7.696302153908052 | 7.7 / 7.7 | 是 |
| 553 | ⑦ | DAX 11-13→11-20 % | 7.279153713745967 | 7.28 / 7.28 | 是 |
| 554 | ⑦ | CAC40 11-13→11-20 % | 5.271417039693215 | 5.27 / 5.27 | 是 |
| 555 | ⑦ | 11-13→11-20 四地股指跌幅均不深于美股 | [-8.613, -7.696, -7.279, -5.271] | (判据成立) | 是 |
| 556 | ⑦ | 11-16/11-20 两日 EURUSD/USDJPY 单日变动最大幅 <=0.23% | 0.2293 | (判据成立) | 是 |
| 557 | ⑦ | engine policy_doc_facts[0].published_on | 2026-11-18 | 2026-11-18 | 是 |
| 558 | ⑦ | engine policy_doc_facts 条数 | 1 | 1 | 是 |
| 559 | ⑦ | 判断档文字 | 在场 | 在场 / FOMC 2026年10月会议纪要 2026-1… | 是 |
| 560 | ⑦ | 判断档文字 | 在场 | 在场 / 政策文档事实仅 FOMC 纪要一条 | 是 |
| 561 | ⑦ | days(2026-10-30→11-13) | 14 | 14 / 14 | 是 |
| 562 | ⑦ | days(2026-09-16→11-13) | 58 | 58 / 58 | 是 |
| 563 | ⑦ | days(2026-10-30→11-20) | 21 | 21 / 21 | 是 |
| 564 | ⑦ | days(2026-09-16→11-20) | 65 | 65 / 65 | 是 |
| 565 | ⑦ | 判断档文字 | 在场 | 在场 / 证据倾向竞争解释但不足以裁定,尚不能区分 | 是 |
| 566 | ⑦ | 同日收盘对照: DAX/CAC40 跌幅浅于 SPX, NIKKEI225 与 SPX 相当(差<0.7pp) | [-9.356, -9.98, -1.505, 1.862] | (判据成立) | 是 |
| 567 | ⑤ | us_rates_trio chg_bp.UST_10Y (series_store 直算) | -8.0 | -8.0 | 是 |
| 568 | ⑤ | us_rates_trio levels_at_to.UST_10Y | 5.04 | 5.04 | 是 |
| 569 | ⑤ | us_rates_trio chg_bp.TIPS_10Y (series_store 直算) | 11.0 | 11.0 | 是 |
| 570 | ⑤ | us_rates_trio levels_at_to.TIPS_10Y | 2.88 | 2.88 | 是 |
| 571 | ⑤ | us_rates_trio chg_bp.BEI_10Y (series_store 直算) | -19.0 | -19.0 | 是 |
| 572 | ⑤ | us_rates_trio levels_at_to.BEI_10Y | 2.16 | 2.16 | 是 |
| 573 | ⑤ | rates_decomposition.window_from | 2026-10-20 | 2026-10-20 | 是 |
| 574 | ⑤ | rates_decomposition.window_to | 2026-11-19 | 2026-11-19 | 是 |
| 575 | ⑤ | rates_decomposition.nominal_bp | -8.0 | -8.0 | 是 |
| 576 | ⑤ | rates_decomposition.real_bp | 11.0 | 11.0 | 是 |
| 577 | ⑤ | rates_decomposition.bei_bp | -19.0 | -19.0 | 是 |
| 578 | ⑤ | 恒等式 Δ名义=Δ实际+Δ盈亏平衡 (bp) | 0.0 | (判据成立) | 是 |
| 579 | ⑤ | 水平恒等式 名义=实际+盈亏平衡 @2026-10-20 | [5.12, 2.77, 2.35] | (判据成立) | 是 |
| 580 | ⑤ | 水平恒等式 名义=实际+盈亏平衡 @2026-11-19 | [5.04, 2.88, 2.16] | (判据成立) | 是 |
| 581 | ⑤ | us_rates_trio chg_bp_12m.UST_10Y (series_store 直算) | 91.0 | 91.0 | 是 |
| 582 | ⑤ | us_rates_trio chg_bp_12m.TIPS_10Y (series_store 直算) | 102.0 | 102.0 | 是 |
| 583 | ⑤ | us_rates_trio chg_bp_12m.BEI_10Y (series_store 直算) | -11.0 | -11.0 | 是 |
| 584 | ⑤ | us_rates_trio.window_12m | ["2025-11-19", "2026-11-19"] | ["2025-11-19", "2026-11-19"] | 是 |
| 585 | ⑤ | 12月窗=365 天且止于 11-19 | 365 | (判据成立) | 是 |
| 586 | ⑤ | asset_returns_echo NIKKEI225 chg_pct (series_store 直算) | -9.98 | -9.98 | 是 |
| 587 | ⑤ | asset_returns_echo DAX chg_pct (series_store 直算) | 0.11 | 0.11 | 是 |
| 588 | ⑤ | asset_returns_echo SPX chg_pct (series_store 直算) | -5.51 | -5.51 | 是 |
| 589 | ⑤ | asset_returns_echo VIX chg_pct (series_store 直算) | 38.87 | 38.87 | 是 |
| 590 | ⑧ | S6 信封定位(含 1871 的 step 数) | [42] | (判据成立) | 是 |
| 591 | ⑧ | S6: 扫描候选月=1871 | 1871 | (判据成立) | 是 |
| 592 | ⑧ | S6: 有效候选=74 | [".data.candidates.valid"] | (判据成立) | 是 |
| 593 | ⑧ | S6: TOP1 候选月 2025-03 | [".data.top[0].candidate_month", ".data.top[0].cluster_members[11]"] | (判据成立) | 是 |
| 594 | ⑧ | S6: TOP1 距离 0.727 | [[".data.top[0].distance", 0.727212]] | (判据成立) | 是 |
| 595 | ⑧ | 判断档文字 | 在场 | 在场 / 历史类比 0 段(契约允许 0..3 段,零段如… | 是 |
| 596 | ⑧ | reader_map.history_periods 段数 | 0 | 0 | 是 |
| 597 | ⑨ | 判断档文字 | 在场 | 在场 / 【假设·非预测】分化延续 | 是 |
| 598 | ⑨ | 判断档文字 | 在场 | 在场 / 【假设·非预测】分化收敛 | 是 |
| 599 | ⑨ | 推定发布规则 EA 2026-12 → 入档月 | 2027-01 | 2027-01 / 2027-01 | 是 |
| 600 | ⑨ | EA/JP 2026-11、2026-12 期推定发布日均早于 2027-02-15 | [["EA_HICP_YOY", "2026-11", "2026-12-16"], ["EA_HICP_YOY", "2026-12", … | (判据成立) | 是 |
| 601 | ⑨ | 2026-11 期读数在截止日尚未发布 | ["2026-12-16", "2026-12-20"] | (判据成立) | 是 |
| 602 | ⑨ | l4.scenarios[0].trigger.deadline | 2027-02-15 | 2027-02-15 | 是 |
| 603 | ⑨ | l4.scenarios[1].trigger.deadline | 2027-02-15 | 2027-02-15 | 是 |
| 604 | ⑨ | 截止日读数与 S1 前提相容: EA 4.0≥3.5, JP 2.44≥2.0, 水平差 1.56≥1.5 | [4.0, 2.44, 1.56] | (判据成立) | 是 |
| 605 | ⑨ | S1/S2 证伪条件(须两月)未被截止日前已发布读数满足 | 2026-11/12 期未发布 | (判据成立) | 是 |
| 606 | ⑨ | 截止日 VIX 末收盘 35.89: >30(S1 的 VIX 分量现值满足) 且 >=25(S2 的 VIX 分量现值不满足) | 35.889999 | (判据成立) | 是 |
| 607 | ⑨ | 判断档文字 | 在场 | 在场 / VIX 收盘在 25–30 之间时两情景均不触发… | 是 |
| 608 | ⑨ | 判断档文字 | 在场 | 在场 / S2 证伪阈值(3.5%)较前提水平(3.0% … | 是 |
| 609 | ⑨ | 判断档文字 | 在场 | 在场 / S1 触发阈 4.0% 高于前提水平 3.5%,… | 是 |
| 610 | ⑨ | l4.scenarios falsification.metric_id | ["EA_HICP_YOY", "EA_HICP_YOY"] | ["EA_HICP_YOY", "EA_HICP_YOY"] | 是 |
| 611 | ⑨ | l4.scenarios falsification.secondary_metric_ids | [["JP_CPI_YOY"], ["JP_CPI_YOY"]] | [["JP_CPI_YOY"], ["JP_CPI_YOY"]] | 是 |
| 612 | ⑨ | 证伪指标 EA_HICP_YOY/JP_CPI_YOY 在册(注册表+series_store) | ok | (判据成立) | 是 |
| 613 | ⑨ | 判断档文字 | 在场 | 在场 / 该方向与近一月观察(SPX 下跌 9.36%、N… | 是 |
| 614 | ⑩ | headline_conclusion | 在场 | 在场 / 日本与欧元区通胀与政策环境呈「方向同、水平分化、… | 是 |
| 615 | ⑩ | headline_conclusion | 在场 | 在场 / 证据不足六项 | 是 |
| 616 | ⑩ | headline 六项与 C3 ①–⑥ 同题 | 在场 | 在场 / 日本宣布值口径序列不可得(注册表无 JP_POL… | 是 |
| 617 | ⑩ | headline 六项与 C3 ①–⑥ 同题 | 在场 | 在场 / 欧央行序列止于 2026-09-16 | 是 |
| 618 | ⑩ | headline 六项与 C3 ①–⑥ 同题 | 在场 | 在场 / 通胀公布时间均为推定规则非实录 | 是 |
| 619 | ⑩ | headline 六项与 C3 ①–⑥ 同题 | 在场 | 在场 / 事后回顾修订口径 | 是 |
| 620 | ⑩ | headline 六项与 C3 ①–⑥ 同题 | 在场 | 在场 / 增长与核心通胀背景对照缺席 | 是 |
| 621 | ⑩ | headline 六项与 C3 ①–⑥ 同题 | 在场 | 在场 / 两地国债收益率期限结构对照不对称 | 是 |
| 622 | ⑩ | C3 六项编号在场 | 在场 | 在场 / ①日本政策目标宣布值口径不可得 | 是 |
| 623 | ⑩ | C3 六项编号在场 | 在场 | 在场 / ②欧央行序列止于最近一次变更日 | 是 |
| 624 | ⑩ | C3 六项编号在场 | 在场 | 在场 / ③本窗月度通胀读数的公布时间为推定规则非实录 | 是 |
| 625 | ⑩ | C3 六项编号在场 | 在场 | 在场 / ④欧元区 HICP 与日本全国 CPI 月度数值… | 是 |
| 626 | ⑩ | C3 六项编号在场 | 在场 | 在场 / ⑤增长与核心通胀背景对照缺席 | 是 |
| 627 | ⑩ | C3 六项编号在场 | 在场 | 在场 / ⑥两地国债收益率期限结构对照不对称 | 是 |
| 628 | ⑩ | C3 「引擎可核者六项」 | 在场 | 在场 / 引擎可核者六项 | 是 |
| 629 | ⑩ | headline JP target_value (calendar) | 1.25 | 1.25 / 1.25 | 是 |
| 630 | ⑩ | headline JP decision_date | 2026-09-18 | 2026-09-18 / 2026-09-18 | 是 |
| 631 | ⑩ | headline JP effective_on | 2026-09-24 | 2026-09-24 / 2026-09-24 | 是 |
| 632 | ⑩ | headline JP maintenance decision_date | 2026-10-30 | 2026-10-30 / 2026-10-30 | 是 |
| 633 | ⑩ | headline ECB_MRO last | 2.65 | 2.65 / 2.65 | 是 |
| 634 | ⑩ | headline ECB_DFR last | 2.5 | 2.5 / 2.5 | 是 |
| 635 | ⑩ | headline JP_POLICY_RATE 6m anchor | 0.727 | 0.727 / 0.727 | 是 |
| 636 | ⑩ | headline JP_POLICY_RATE latest | 1.227 | 1.227 / 1.227 | 是 |
| 637 | ⑩ | headline EA 2025-10 | 2.1 | 2.1 / 2.1 | 是 |
| 638 | ⑩ | headline JP 2025-10 | 2.99 | 2.99 / 2.99 | 是 |
| 639 | ⑩ | headline EA latest | 4.0 | 4.0 / 4.0 | 是 |
| 640 | ⑩ | headline JP latest | 2.44 | 2.44 / 2.44 | 是 |
| 641 | ⑩ | headline 方向词: EA 同比上升(4.0>2.1)、JP 同比下降(2.44<2.99) | ok | (判据成立) | 是 |
| 642 | ⑩ | headline 方向词: 两地通胀均上行(六个月锚间) | [3.0, 1.38] | (判据成立) | 是 |
| 643 | ⑩ | headline 方向词: 政策均收紧(ECB DFR 2.0→2.5; JP 月均 0.727→1.227; JP 目标实录无前值) | [2.5, 1.227] | (判据成立) | 是 |
| 644 | ⑩ | headline「欧央行宣布值口径两次合计五十个基点」=2×25bp | [50, 50] | (判据成立) | 是 |
| 645 | ⑩ | headline「日本月均口径六个月锚间净变动约五十个基点」 | 50.0 | (判据成立) | 是 |
| 646 | ⑩ | headline「距截止 六十八 天」 | 在场 | 在场 / 距截止 六十八 天,Gate A 列 degra… | 是 |
| 647 | ⑩ | headline 回看窗 | 在场 | 在场 / 窗起 2026-05-23 至研究截止 2026… | 是 |
| 648 | ⑩ | headline 请求月末未到 | 在场 | 在场 / 问句请求月末 2026-11-30 未到,研究截… | 是 |
| 649 | ⑩ | transmission 三环 face_off_verdict | ["尚不能区分", "尚不能区分", "尚不能区分"] | ["尚不能区分", "尚不能区分", "尚不能区分"] | 是 |
| 650 | ⑩ | transmission 环数 | 3 | 3 | 是 |
| 651 | ⑩ | transmission 各环字段齐备 | true | true | 是 |
| 652 | ⑩ | transmission distinguishing_metric | ["EA_HICP_YOY", "EURUSD", "VIX"] | ["EA_HICP_YOY", "EURUSD", "VIX"] | 是 |
| 653 | ⑩ | 区分指标在证据索引在场(EA_HICP_YOY/EURUSD/VIX) | ok | (判据成立) | 是 |
| 654 | ⑩ | l3.contradictions 条数 | 3 | 3 | 是 |
| 655 | ⑩ | l3.mechanism_chains 条数 | 1 | 1 | 是 |
| 656 | ⑩ | 每条矛盾陈述 2 条竞争解释 | [2, 2, 2] | [2, 2, 2] | 是 |
| 657 | ⑩ | 矛盾陈述竞争解释均以【假设】起头 | ok | (判据成立) | 是 |
| 658 | ⑦ | M1 四环 evidence_level | ["E1", "E1", "E2", "E2"] | ["E1", "E1", "E2", "E2"] | 是 |
| 659 | ⑦ | E2 环3 以「传导【假设】」起头,含【假设】标注与「尚不能区分」 | 传导【假设】: 若政 | (判据成立) | 是 |
| 660 | ⑦ | E2 环4 归因句带【假设·归因】且结论「单一归因于两地政策不可证」 | 2 | (判据成立) | 是 |
| 661 | ⑦ | 传导三环 causal_hypothesis/competing_explanation 均以【假设】起头(非事实位措辞) | ok | (判据成立) | 是 |
| 662 | ⑦ | E2 环均有 missing_link_note | ["引擎无政策差-汇率联动通道证据(近零渠道),该环为【假设】;", "归因环节为【假设】(单月窗、多因子叠加);区分指标=VIX,"] | (判据成立) | 是 |
| 663 | ⑦ | 对质表「尚不能区分」与各行观测一致: 环1 n=2 且反向观察在场; 环2 预期未分立; 环3 仅一个盘中回落观测 | ok | (判据成立) | 是 |
| 664 | ⑩ | 情景条数/各环五行齐备 | [2, true] | [2, true] | 是 |
| 665 | ⑩ | S1/S2 sensitive_variables | [["EA_HICP_YOY", "JP_CPI_YOY"], ["EA_HICP_YOY", "JP_CPI_YOY"]] | [["EA_HICP_YOY", "JP_CPI_YOY"], ["EA_HICP_YOY", "J… | 是 |
| 666 | ⑩ | S1/S2 confidence_tier | ["有相关证据", "纯逻辑推理"] | ["有相关证据", "纯逻辑推理"] | 是 |
| 667 | ⑪ | gate_a.status | DEGRADED | DEGRADED | 是 |
| 668 | ⑪ | 判断档文字(Gate A 降级披露) | 在场 | 在场 / 当日快照 Gate A 将该两序列列于降级名单 | 是 |
| 669 | ⑪ | gate_a.noncore_missing 含 BUND_10Y | true | true | 是 |
| 670 | ⑪ | facts 无 BUND_10Y 行 | null | null | 是 |
| 671 | ⑪ | gate_a.noncore_missing 含 BUND_2Y | true | true | 是 |
| 672 | ⑪ | facts 无 BUND_2Y 行 | null | null | 是 |
| 673 | ⑪ | gate_a.noncore_missing 含 EA_REAL_GDP_YOY | true | true | 是 |
| 674 | ⑪ | facts 无 EA_REAL_GDP_YOY 行 | null | null | 是 |
| 675 | ⑪ | gate_a.noncore_missing 含 JP_REAL_GDP_YOY | true | true | 是 |
| 676 | ⑪ | facts 无 JP_REAL_GDP_YOY 行 | null | null | 是 |
| 677 | ⑪ | gate_a.noncore_missing 含 JP_CPI_TOKYO_YOY | true | true | 是 |
| 678 | ⑪ | facts 无 JP_CPI_TOKYO_YOY 行 | null | null | 是 |
| 679 | ⑪ | series_store 无 BUND_10Y/BUND_2Y | [false, false] | [false, false] | 是 |
| 680 | ⑪ | series_store 有 EA/JP GDP 与东京序列 | [true, true, true] | [true, true, true] | 是 |
| 681 | ⑪ | series_store.EA_REAL_GDP_YOY 末观测 | ["2026-07-01", 1.28] | ["2026-07-01", 1.28] | 是 |
| 682 | ⑪ | series_store.JP_REAL_GDP_YOY 末观测 | ["2026-07-01", 1.16] | ["2026-07-01", 1.16] | 是 |
| 683 | ⑪ | 判断档文字: GDP 序列面至 2026-07 | 在场 | 在场 / 序列面存有至 2026-07 期读数(欧元区一点… | 是 |
| 684 | ⑪ | 判断档文字: GDP 缺席 | 在场 | 在场 / EA_REAL_GDP_YOY、JP_REAL_… | 是 |
| 685 | ⑪ | missing_detail: 东京=来源文件在场而指标缺席 | 来源文件在场而指标缺席(采集遗漏或子源缺席——档内无该指标子源状态记录,不可区分) | (判据成立) | 是 |
| 686 | ⑪ | missing_detail: BUND=子源缺席、非采集遗漏 | 子源缺席(ea档记录:BBK_WU3146=READ_FAIL——源端不可得/未采,非采集遗漏) | (判据成立) | 是 |
| 687 | ⑪ | missing_detail: EA/JP GDP=采集器已取到而事实未生成 | 来源文件在场且子源FRED_EA_GDP取数成功而指标缺席(采集遗漏——采集器已取到而事实未生成) | (判据成立) | 是 |
| 688 | ⑪ | 判断档文字: BUND 注记 | 在场 | 在场 / BUND_10Y、BUND_2Y 在册,当日快照… | 是 |
| 689 | ⑪ | 判断档文字: 东京都注记 | 在场 | 在场 / 该序列在当日快照 Gate A 列于 nonco… | 是 |
| 690 | ⑪ | facts.JGB2Y value/observation_date/quality_status | [1.853, "2026-11-19", "PASS"] | [1.853, "2026-11-19", "PASS"] | 是 |
| 691 | ⑪ | series_store 无 JGB2Y | false | false | 是 |
| 692 | ⑪ | facts.JGB5Y value/observation_date/quality_status | [2.235, "2026-11-19", "PASS"] | [2.235, "2026-11-19", "PASS"] | 是 |
| 693 | ⑪ | series_store 无 JGB5Y | false | false | 是 |
| 694 | ⑪ | facts.JGB10Y value/observation_date/quality_status | [2.87, "2026-11-19", "PASS"] | [2.87, "2026-11-19", "PASS"] | 是 |
| 695 | ⑪ | series_store 无 JGB10Y | false | false | 是 |
| 696 | ⑪ | 判断档文字: JGB 三值 | 在场 | 在场 / 2026-11-19 为 1.853、2.235… | 是 |
| 697 | ⑪ | 证据索引不含 BUND_10Y | BUND_10Y | (判据成立) | 是 |
| 698 | ⑪ | 证据索引不含 BUND_2Y | BUND_2Y | (判据成立) | 是 |
| 699 | ⑪ | 证据索引不含 JGB2Y | JGB2Y | (判据成立) | 是 |
| 700 | ⑪ | 证据索引不含 JGB5Y | JGB5Y | (判据成立) | 是 |
| 701 | ⑪ | 证据索引不含 JGB10Y | JGB10Y | (判据成立) | 是 |
| 702 | ⑪ | 判断档文字: 五条序列均不在本问证据索引 | 在场 | 在场 / 但五条序列均不在本问证据索引 | 是 |
| 703 | ⑪ | 注册表 JP/EA 面无核心通胀序列 | [] | (判据成立) | 是 |
| 704 | ⑪ | 判断档文字: 注册表无两地核心通胀序列 | 在场 | 在场 / 注册表无两地核心通胀序列(检索范围=注册表 ec… | 是 |
| 705 | ⑪ | 注册表无 JP_POLICY_TARGET 且 series_store 无 | ok | (判据成立) | 是 |
| 706 | ⑪ | 判断档文字: 注册表无 JP_POLICY_TARGET | 在场 | 在场 / 注册表无 JP_POLICY_TARGET(检索… | 是 |
| 707 | ⑪ | 注册表 JP 通胀面指标 | ["JP_CPI_TOKYO_YOY", "JP_CPI_YOY"] | ["JP_CPI_TOKYO_YOY", "JP_CPI_YOY"] | 是 |
| 708 | ⑪ | 日历 JP 条目数 | 2 | 2 | 是 |
| 709 | ⑪ | 日历 ECB 条目数 | 0 | 0 | 是 |
| 710 | ⑪ | 日历 EA HICP 条目数/观测月 | [3, ["2021-05", "2022-06", "2025-03"]] | [3, ["2021-05", "2022-06", "2025-03"]] | 是 |
| 711 | ⑪ | 判断档文字: 日历日欧面覆盖 | 在场 | 在场 / 冻结日历实录于日欧面仅覆盖日本政策目标两条与三条… | 是 |
| 712 | ⑪ | JP target entry basis/decision/effective/target | ["user_directive", "2026-09-18", "2026-09-24", 1.25] | ["user_directive", "2026-09-18", "2026-09-24", 1.2… | 是 |
| 713 | ⑪ | JP maint entry basis/decision/kind | ["user_directive", "2026-10-30", "policy_maintenance"] | ["user_directive", "2026-10-30", "policy_maintenan… | 是 |
| 714 | ⑪ | JP target entry 无前值字段 | ["basis", "decision_date", "effective_on", "entry_id", "first_publish_… | (判据成立) | 是 |
| 715 | ⑪ | 判断档文字: 均 user_directive | 在场 | 在场 / 均 user_directive 基础 | 是 |
| 716 | ⑪ | 日历 version/updated | ["1.5.0", "2026-11-21"] | ["1.5.0", "2026-11-21"] | 是 |
| 717 | ⑪ | 判断档文字: v1.5.0 | 在场 | 在场 / 发布日历实录(v1.5.0,2026-11-21… | 是 |
| 718 | ⑪ | noncore_degraded 含 ECB_DFR/ECB_MRO | [true, true] | [true, true] | 是 |
| 719 | ⑪ | facts.ECB_MRO quality_status | DEGRADED | DEGRADED | 是 |
| 720 | ⑪ | facts.ECB_MRO observation_date | 2026-09-16 | 2026-09-16 | 是 |
| 721 | ⑪ | series_store.ECB_MRO 末观测日 | 2026-09-16 | 2026-09-16 | 是 |
| 722 | ⑪ | facts.ECB_DFR quality_status | DEGRADED | DEGRADED | 是 |
| 723 | ⑪ | facts.ECB_DFR observation_date | 2026-09-16 | 2026-09-16 | 是 |
| 724 | ⑪ | series_store.ECB_DFR 末观测日 | 2026-09-16 | 2026-09-16 | 是 |
| 725 | ⑪ | 判断档文字: L1 事实行 quality_status=DEGRADED | 在场 | 在场 / L1 事实行 quality_status=DE… | 是 |
| 726 | ⑪ | Gate A 注记「不得进入研究结论」在场 | 缺失/失败数据已披露,不得进入研究结论;单个资产缺失不阻断其余研究;非核心FAIL按降级披露(注册表criticality为权威) | (判据成立) | 是 |
| 727 | ⑪ | facts.JP_CPI_YOY quality_status | WARN | WARN | 是 |
| 728 | ⑪ | facts.JP_CPI_YOY issues 类别 | ["release"] | ["release"] | 是 |
| 729 | ⑪ | facts.EA_HICP_YOY quality_status | WARN | WARN | 是 |
| 730 | ⑪ | facts.EA_HICP_YOY issues 类别 | ["release"] | ["release"] | 是 |
| 731 | ⑪ | 判断档文字: WARN 与 WARN | 在场 | 在场 / 两条全国/全区最新读数 L1 quality_s… | 是 |
| 732 | ⑫ | snapshot.research_as_of | 2026-11-23T22:53:47+08:00 | 2026-11-23T22:53:47+08:00 | 是 |
| 733 | ⑫ | 判断档文字: 采集时点 | 在场 | 在场 / 快照采集于 2026-11-23T22:53:4… | 是 |
| 734 | ⑫ | series_store.SPX 末观测日=截止日 | 2026-11-23 | 2026-11-23 | 是 |
| 735 | ⑫ | series_store.VIX 末观测日=截止日 | 2026-11-23 | 2026-11-23 | 是 |
| 736 | ⑫ | series_store.DAX 末观测日=截止日 | 2026-11-23 | 2026-11-23 | 是 |
| 737 | ⑫ | series_store.CAC40 末观测日=截止日 | 2026-11-23 | 2026-11-23 | 是 |
| 738 | ⑫ | series_store.EURUSD 末观测日=截止日 | 2026-11-23 | 2026-11-23 | 是 |
| 739 | ⑫ | series_store.USDJPY 末观测日=截止日 | 2026-11-23 | 2026-11-23 | 是 |
| 740 | ⑫ | series_store.DXY 末观测日=截止日 | 2026-11-23 | 2026-11-23 | 是 |
| 741 | ⑫ | series_store.NIKKEI225 末观测日 | 2026-11-20 | 2026-11-20 | 是 |
| 742 | ⑫ | 判断档文字: 盘中非收盘 | 在场 | 在场 / SPX/VIX/DAX/CAC40 的截止日值与… | 是 |
| 743 | ⑫ | 判断档文字: 统一 11-20 同日收盘口径 | 在场 | 在场 / 席位跨地区对照统一采用 2026-11-20 同… | 是 |
| 744 | ⑫ | 2026-11-20 为周五 | 周五 | (判据成立) | 是 |
| 745 | ⑫ | 2026-11-23 为周一 | 周一 | (判据成立) | 是 |
| 746 | ⑫ | SPX/VIX/DAX/CAC40 在 11-20 后、11-23 前无观测 | ok | (判据成立) | 是 |
| 747 | ⑫ | C2 文字: 均为 2026-11-23 盘中快照、非收盘价 | 在场 | 在场 / 均为 2026-11-23 盘中快照、非收盘价 | 是 |
| 748 | ⑫ | C2 引用三值 USDJPY/SPX/VIX@11-23 (四舍五入 2 位) | [159.35, 7203.85, 27.01] | [159.35, 7203.85, 27.01] | 是 |
| 749 | ⑫ | facts USDJPY/SPX/VIX@11-23 值 | [159.35, 7203.85, 27.01] | [159.35, 7203.85, 27.01] | 是 |
| 750 | ⑫ | facts USDJPY/SPX/VIX 观测日 | ["2026-11-23", "2026-11-23", "2026-11-23"] | ["2026-11-23", "2026-11-23", "2026-11-23"] | 是 |
| 751 | ⑫ | M1 环3 USDJPY@11-23 三位小数 159.347 / EURUSD 1.0940 / DXY 104.079 | [159.347, 1.094, 104.079] | [159.347, 1.094, 104.079] | 是 |
| 752 | ⑫ | M1 环3 DXY/EURUSD 窗起值 101.81 / 1.1221 | [101.81, 1.1221] | [101.81, 1.1221] | 是 |
| 753 | ⑫ | M1 环3 至 11-20 收盘 EURUSD 1.0970 / USDJPY 159.707 / DXY 103.81 | [1.097, 159.707, 103.81] | [1.097, 159.707, 103.81] | 是 |
| 754 | ⑫ | M1 环3 窗起 USDJPY 156.494 | 156.494 | 156.494 | 是 |
| 755 | ⑬ | contract_verification.verdict | VERIFIED | VERIFIED | 是 |
| 756 | ⑬ | 契约非 VERIFIED 项数 | 1 | 1 | 是 |
| 757 | ⑬ | 契约非 VERIFIED 项指标 | ["ECB_DFR"] | ["ECB_DFR"] | 是 |
| 758 | ⑬ | 契约 verdicts 总数 | 5 | 5 | 是 |
| 759 | ⑬ | STALE 项 token/value/expected | ["2.5%", 2.5, 2.5] | ["2.5%", 2.5, 2.5] | 是 |
| 760 | ⑬ | STALE 项 note=Fact 直读 ECB_DFR@2026-09-16=2.5 与快照一致 | recompute:Fact 直读 ECB_DFR@2026-09-16=2.5 | (判据成立) | 是 |
| 761 | ⑬ | 其余 VERIFIED 项 metric/token | [["JP_POLICY_RATE", "1.227%"], ["USDJPY", "159.35"], ["SPX", "7203.85"… | [["JP_POLICY_RATE", "1.227%"], ["USDJPY", "159.35"… | 是 |
| 762 | ⑬ | 判断档文字: STALE 披露 | 在场 | 在场 / 引擎契约验证对本档水平对照所引存款便利利率数值串… | 是 |
| 763 | ⑬ | 「观测滞后六十八天」= days(2026-09-16→2026-11-23) | 68 | (判据成立) | 是 |
| 764 | ⑬ | L3 引用总数 | 21 | 21 | 是 |
| 765 | ⑬ | 矛盾陈述引用数 | [2, 6, 3] | [2, 6, 3] | 是 |
| 766 | ⑬ | 机制链各环引用数 | [2, 2, 2, 4] | [2, 2, 2, 4] | 是 |
| 767 | ⑬ | 21 条引用全部在证据索引且 kind=snapshot_fact | [] | (判据成立) | 是 |
| 768 | ⑬ | 判断档文字: 21 条 | 在场 | 在场 / 三条矛盾陈述+机制链四环共 21 条 snaps… | 是 |
| 769 | ⑬ | 判断档文字: 对质计数 | 在场 | 在场 / 支持主解释 0·支持竞争解释 0·尚不能区分 3 | 是 |
| 770 | ⑬ | 判断档全部 evidence_refs 数(含情景) | 25 | 25 | 是 |
| 771 | ⑬ | 全部 evidence_refs 均在证据索引 | [] | (判据成立) | 是 |
| 772 | E-日期 | rates_decomposition.window_from == us_rates_trio.window.from | ["2026-10-20", "2026-10-20"] | (判据成立) | 是 |
| 773 | E-日期 | rates_decomposition.window_to == us_rates_trio.window.to | ["2026-11-19", "2026-11-19"] | (判据成立) | 是 |
| 774 | E-日期 | 推定发布日 2026-05-16 的星期 | 周六 | 周六 / 周六 | 是 |
| 775 | E-日期 | 欧元区 2026-06..2026-10 各期观测日与推定发布日均在窗内; 2026-05 期观测日早于窗起而推定发布日在窗内 | ["2026-05-01", "2026-06-16"] | (判据成立) | 是 |
| 776 | E-日期 | 日本 2026-06..2026-10 各期观测日与推定发布日均在窗内; 2026-05 期观测日早于窗起而推定发布日在窗内 | ["2026-05-01", "2026-06-20"] | (判据成立) | 是 |
| 777 | E-日期 | 六个月前锚在值观测日(obe@2026-05-23) | 2025-06-11 | 2025-06-11 / 2025-06-11 | 是 |
| 778 | E-日期 | point_values JP_POLICY_RATE.policy_window_path.window[0](一年窗起) | 2025-11-23 | 2025-11-23 / 2025-11-23 | 是 |
| 779 | E-日期 | series_store.EA_HICP_YOY 2026-05 期观测日(月初); JP_CPI_YOY 同月观测日=2026-05-01 | 2026-05-01 | 2026-05-01 / 2026-05-01 | 是 |
| 780 | E-日期 | 推定发布规则 月均 月末+5 (2026-04 期) | 2026-05-05 | 2026-05-05 / 2026-05-05 | 是 |
| 781 | E-日期 | 推定发布规则 EA 月末+16 (2026-04 期) | 2026-05-16 | 2026-05-16 / 2026-05-16 | 是 |
| 782 | E-日期 | 推定发布规则 全国CPI 月末+20 (2026-04 期) | 2026-05-20 | 2026-05-20 / 2026-05-20 | 是 |
| 783 | E-日期 | question_window.windows[0].from(回看窗起) | 2026-05-23 | 2026-05-23 / 2026-05-23 | 是 |
| 784 | E-日期 | 引擎 policy_window_path.events 决议日=生效日前上一个周四(回推) | 2026-06-11 | 2026-06-11 / 2026-06-11 | 是 |
| 785 | E-日期 | 推定发布规则 EA 月末+16 (2026-05 期) | 2026-06-16 | 2026-06-16 / 2026-06-16 | 是 |
| 786 | E-日期 | series_store.ECB_MRO/DFR 窗内变更日1(=生效日) | 2026-06-17 | 2026-06-17 / 2026-06-17 | 是 |
| 787 | E-日期 | 推定发布规则 全国CPI 月末+20 (2026-05 期) | 2026-06-20 | 2026-06-20 / 2026-06-20 | 是 |
| 788 | E-日期 | 2026-06 最后一个周五(=引擎 publication_rule 所载官方实录锚 6月分) | 2026-06-26 | 2026-06-26 / 2026-06-26 | 是 |
| 789 | E-日期 | 推定发布规则 东京 月末−1 (2026-08 期) | 2026-08-30 | 2026-08-30 / 2026-08-30 | 是 |
| 790 | E-日期 | 引擎 policy_window_path.events 决议日=生效日前上一个周四(回推) | 2026-09-10 | 2026-09-10 / 2026-09-10 | 是 |
| 791 | E-日期 | series_store.ECB_MRO/DFR 窗内变更日2(=生效日) | 2026-09-16 | 2026-09-16 / 2026-09-16 | 是 |
| 792 | E-日期 | ECB 末变更日次日(区间起) | 2026-09-17 | 2026-09-17 / 2026-09-17 | 是 |
| 793 | E-日期 | 日历 RC-JP-BOJ-TARGET 决议日 | 2026-09-18 | 2026-09-18 / 2026-09-18 | 是 |
| 794 | E-日期 | 日历 RC-JP-BOJ-TARGET 生效日 | 2026-09-24 | 2026-09-24 / 2026-09-24 | 是 |
| 795 | E-日期 | 推定发布规则 东京 月末−1 (2026-09 期) | 2026-09-29 | 2026-09-29 / 2026-09-29 | 是 |
| 796 | E-日期 | us_rates_trio.window.from(三利率分解窗起); 判断档 rates_decomposition.window_from 应同值 | 2026-10-20 | 2026-10-20 / 2026-10-20 | 是 |
| 797 | E-日期 | asset_moves 月窗 window.from | 2026-10-23 | 2026-10-23 / 2026-10-23 | 是 |
| 798 | E-日期 | 推定发布规则 东京 月末−1 (2026-10 期); 兼=日历维持条目决议日 | 2026-10-30 | 2026-10-30 / 2026-10-30 | 是 |
| 799 | E-日期 | series_store.VIX 观测日(收盘路径) | 2026-11-04 | 2026-11-04 / 2026-11-04 | 是 |
| 800 | E-日期 | 推定发布规则 月均 月末+5 (2026-10 期) | 2026-11-05 | 2026-11-05 / 2026-11-05 | 是 |
| 801 | E-日期 | series_store.VIX 观测日(收盘路径) | 2026-11-13 | 2026-11-13 / 2026-11-13 | 是 |
| 802 | E-日期 | 推定发布规则 EA_HICP 月末+16 (2026-10 期) | 2026-11-16 | 2026-11-16 / 2026-11-16 | 是 |
| 803 | E-日期 | policy_doc_facts FOMC 纪要 published_on; 兼=VIX 收盘日 | 2026-11-18 | 2026-11-18 / 2026-11-18 | 是 |
| 804 | E-日期 | series_store.UST_10Y 末观测日; JGB 事实行观测日 | 2026-11-19 | 2026-11-19 / 2026-11-19 | 是 |
| 805 | E-日期 | 推定发布规则 全国CPI 月末+20 (2026-10 期); 兼=截止前最后收盘日 | 2026-11-20 | 2026-11-20 / 2026-11-20 | 是 |
| 806 | E-日期 | 冻结日历 updated | 2026-11-21 | 2026-11-21 / 2026-11-21 | 是 |
| 807 | E-日期 | 快照 research_as_of 日期=研究截止/实际覆盖日 | 2026-11-23 | 2026-11-23 / 2026-11-23 | 是 |
| 808 | E-日期 | research_plan.as_of_declared.requested_as_of(请求月末,未到) | 2026-11-30 | 2026-11-30 / 2026-11-30 | 是 |
| 809 | E-日期 | l4 情景时限(晚于 2026-12 期推定入档日 2027-01-16) | 2027-02-15 | 2027-02-15 / 2027-02-15 | 是 |
| 810 | E-日期 | NIKKEI225 末观测日=截止前最后收盘日(周五) | 2026-11-20 | 2026-11-20 / 2026-11-20 | 是 |
| 811 | E-日期 | 日历 RC-JP-BOJ-MAINT-2026-10 决议日 | 2026-10-30 | 2026-10-30 / 2026-10-30 | 是 |
| 812 | E-日期 | 日历 RC-JP-BOJ-MAINT-2026-10 决议日 | 2026-10-30 | 2026-10-30 / 2026-10-30 | 是 |
| 813 | E-日期 | 日历维持条目决议日(跳升起点距最近政策日) | 2026-10-30 | 2026-10-30 / 2026-10-30 | 是 |
| 814 | E-日期 | 推定发布规则 EA 月末+16 (2026-08 期)=与 ECB 生效日同日 | 2026-09-16 | 2026-09-16 / 2026-09-16 | 是 |
| 815 | E-日期 | series_store.ECB_MRO 前一变更日(其后至 2026-06-17 维持 2.15) | 2025-06-11 | 2025-06-11 / 2025-06-11 | 是 |
| 816 | E-日期 | series_store.DFEDTARU 最近变更日(美联储生效日) | 2026-09-17 | 2026-09-17 / 2026-09-17 | 是 |
| 817 | E-日期 | policy_doc_facts[0].published_on | 2026-11-18 | 2026-11-18 / 2026-11-18 | 是 |
| 818 | E-日期 | series_store.VIX 观测日(收盘路径末六日之首) | 2026-11-13 | 2026-11-13 / 2026-11-13 | 是 |
| 819 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2021-05 | 2021-05 / 2021-05 | 是 |
| 820 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2022-06 | 2022-06 / 2022-06 | 是 |
| 821 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2025-01 | 2025-01 / 2025-01 | 是 |
| 822 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2025-03 | 2025-03 / 2025-03 | 是 |
| 823 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2025-06 | 2025-06 / 2025-06 | 是 |
| 824 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2025-09 | 2025-09 / 2025-09 | 是 |
| 825 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2025-10 | 2025-10 / 2025-10 | 是 |
| 826 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2025-11 | 2025-11 / 2025-11 | 是 |
| 827 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2026-01 | 2026-01 / 2026-01 | 是 |
| 828 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2026-02 | 2026-02 / 2026-02 | 是 |
| 829 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2026-03 | 2026-03 / 2026-03 | 是 |
| 830 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2026-04 | 2026-04 / 2026-04 | 是 |
| 831 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2026-05 | 2026-05 / 2026-05 | 是 |
| 832 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2026-06 | 2026-06 / 2026-06 | 是 |
| 833 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2026-07 | 2026-07 / 2026-07 | 是 |
| 834 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2026-08 | 2026-08 / 2026-08 | 是 |
| 835 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2026-09 | 2026-09 / 2026-09 | 是 |
| 836 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2026-10 | 2026-10 / 2026-10 | 是 |
| 837 | E-月串 | series_store(EA/JP/东京/月均)观测月 或 日历条目观测月 | 2026-11 | 2026-11 / 2026-11 | 是 |
| 838 | E-月串 | l4 情景观测月(未来,设定值) | 2026-12 | 2026-12 / 2026-12 | 是 |
| 839 | E-月串 | 2026-12 期读数推定入档月(月末+16) | 2027-01 | 2027-01 / 2027-01 | 是 |
| 840 | E-月日 | series_store.VIX 观测日(2026-)/asset 月窗起 2026-10-23 | 10-23 | 10-23 / 10-23 | 是 |
| 841 | E-月日 | series_store.VIX 观测日(2026-)/asset 月窗起 2026-10-23 | 11-05 | 11-05 / 11-05 | 是 |
| 842 | E-月日 | series_store.VIX 观测日(2026-)/asset 月窗起 2026-10-23 | 11-06 | 11-06 / 11-06 | 是 |
| 843 | E-月日 | series_store.VIX 观测日(2026-)/asset 月窗起 2026-10-23 | 11-11 | 11-11 / 11-11 | 是 |
| 844 | E-月日 | series_store.VIX 观测日(2026-)/asset 月窗起 2026-10-23 | 11-13 | 11-13 / 11-13 | 是 |
| 845 | E-月日 | series_store.VIX 观测日(2026-)/asset 月窗起 2026-10-23 | 11-16 | 11-16 / 11-16 | 是 |
| 846 | E-月日 | series_store.VIX 观测日(2026-)/asset 月窗起 2026-10-23 | 11-17 | 11-17 / 11-17 | 是 |
| 847 | E-月日 | series_store.VIX 观测日(2026-)/asset 月窗起 2026-10-23 | 11-18 | 11-18 / 11-18 | 是 |
| 848 | E-月日 | series_store.VIX 观测日(2026-)/asset 月窗起 2026-10-23 | 11-19 | 11-19 / 11-19 | 是 |
| 849 | E-月日 | series_store.VIX 观测日(2026-)/asset 月窗起 2026-10-23 | 11-20 | 11-20 / 11-20 | 是 |
| 850 | F | days(pub(EA,2026-10), pub(JP,2026-10)) 推定发布日差 | 4 | 4 / 四 | 是 |
| 851 | F | question_window.windows[0].months | 6 | 6 / 六 | 是 |
| 852 | F | point_values.cells[*].anchors 键含「6个月前」 | 6 | 6 / 六 | 是 |
| 853 | F | series_store.EA_HICP_YOY@2026-10 | 4.0 | 4.0 / 百分之四点零 | 是 |
| 854 | F | series_store.JP_CPI_YOY@2026-10 | 2.44 | 2.44 / 百分之二点四四 | 是 |
| 855 | F | 锚标签「6个月前」 | 6 | 6 / 六 | 是 |
| 856 | F | 注册表 economy∈{JP,EA} 且 id 含 CPI/HICP/CORE 的指标=['EA_HICP_YOY', 'JP_CPI_TOKYO_YOY', 'JP_CPI_Y… | 3 | 3 / 三 | 是 |
| 857 | F | 注册表 JP/EA 面核心通胀序列(应为空) | [] | [] | 是 |
| 858 | F | question_window.windows[0].months | 6 | 6 / 六 | 是 |
| 859 | F | 锚标签「6个月前」 | 6 | 6 / 六 | 是 |
| 860 | F | series_store.ECB_DFR 六个月前锚在值(obe@2026-05-23, 观测 2025-06-11) | 2.0 | 2.0 / 百分之二点零 | 是 |
| 861 | F | series_store.ECB_DFR 末观测 | 2.5 | 2.5 / 2.5 | 是 |
| 862 | F | 锚标签「6个月前」 | 6 | 6 / 六 | 是 |
| 863 | F | series_store.JP_POLICY_RATE@2026-10 | 1.227 | 1.227 / 1.227 | 是 |
| 864 | F | 锚标签「6个月前」 | 6 | 6 / 六 | 是 |
| 865 | F | series_store.JP_POLICY_RATE@2026-04 | 0.727 | 0.727 / 百分之零点七二七 | 是 |
| 866 | F | 锚标签「6个月前」 | 6 | 6 / 六 | 是 |
| 867 | F | series_store.ECB_MRO 末值 | 2.65 | 2.65 / 二点六五 | 是 |
| 868 | F | series_store.ECB_DFR 末值 | 2.5 | 2.5 / 二点五 | 是 |
| 869 | F | JP_POLICY_RATE 变更点月=2026-09 且 ECB 变更月=2026-09 | 9 | 9 / 9 | 是 |
| 870 | F | EA@2026-10 | 4.0 | 4.0 / 百分之四点零 | 是 |
| 871 | F | JP@2026-10 | 2.44 | 2.44 / 百分之二点四四 | 是 |
| 872 | F | 日历 JP_POLICY_TARGET 条目中 RC-JP-BOJ-TARGET-* 条数(basis 均为 user_directive) | 1 | 1 / 一 | 是 |
| 873 | F | 日历 JP_POLICY_TARGET 条目中 RC-JP-BOJ-MAINT-* 条数 | 1 | 1 / 一 | 是 |
| 874 | F | 注册表 ECB_MRO.freshness.max_calendar_lag_days(=ECB_DFR 同值) | 10 | 10 / 十 | 是 |
| 875 | F | 「欧元区两年期与十年期国债收益率在册,当日快照 Gate A 列于缺席名单(事实行缺席)」 | BUND_2Y/BUND_10Y 在册; 事实行 0; noncore_missing 在列 | (判据成立) | 是 |
| 876 | F | 「日本端二年、五年、十年期国债收益率事实行在场(观测 2026-11-19,质量状态 PASS)」 | [["JGB2Y", 1.853], ["JGB5Y", 2.235], ["JGB10Y", 2.87]] | (判据成立) | 是 |
| 877 | F | 「五条序列均不在本问证据索引」 | 证据索引 id 集合与 series_store 均不含五条 | (判据成立) | 是 |
| 878 | F | series_store.ECB_MRO 末值 | 2.65 | 2.65 / 2.65 | 是 |
| 879 | F | series_store.ECB_DFR 末值 | 2.5 | 2.5 / 2.5 | 是 |
| 880 | F | EA@2026-06 | 2.8 | 2.8 / 2.8 | 是 |
| 881 | F | ECB_DFR 窗内两次变更幅(bp)=0.25×100 | 25 | 25 / 25 | 是 |
| 882 | F | series_store.ECB_MRO 变更点(2026-06-17→2.4, 2026-09-16 自 2.4) | 2.4 | 2.4 / 2.4 | 是 |
| 883 | F | series_store.ECB_DFR 变更点(2026-09-16 自 2.25) | 2.25 | 2.25 / 2.25 | 是 |
| 884 | F | 锚标签「6个月前」 | 6 | 6 / 六 | 是 |
| 885 | F | series_store.JP_POLICY_RATE@2026-05 | 0.727 | 0.727 / 0.727 | 是 |
| 886 | F | series_store.JP_POLICY_RATE@2026-06 | 0.841 | 0.841 / 0.841 | 是 |
| 887 | F | series_store.JP_POLICY_RATE@2026-08 | 0.977 | 0.977 / 0.977 | 是 |
| 888 | F | series_store.JP_POLICY_RATE@2026-09 | 1.043 | 1.043 / 1.043 | 是 |
| 889 | F | series_store.ECB_MRO 末值 | 2.65 | 2.65 / 2.65 | 是 |
| 890 | F | 日历 RC-JP-BOJ-TARGET target_value | 1.25 | 1.25 / 1.25 | 是 |
| 891 | F | VIX 截止前最后六个收盘观测日=2026-11-13..2026-11-20 | 6 | 6 / 六 | 是 |
| 892 | F | VIX 2026-11-16..2026-11-20 收盘观测日数 | 5 | 5 / 五 | 是 |
| 893 | F | series_store.VIX@2026-11-13 | 19.299999 | 19.3 / 19.30 | 是 |
| 894 | F | series_store.VIX@2026-11-20 | 35.889999 | 35.89 / 35.89 | 是 |
| 895 | F | series_store.SPX 末观测(2026-11-23 盘中) round2 | 7203.85 | 7203.85 / 7203.85 | 是 |
| 896 | F | series_store.VIX 末观测(2026-11-23 盘中) | 27.01 | 27.01 / 27.01 | 是 |
| 897 | F | VIX 2026-11-05 之后的收盘观测日数(至 11-11) | 4 | 4 / 四 | 是 |
| 898 | F | 同窗对照股指数(SPX/NIKKEI225/DAX/CAC40) | 4 | 4 / 四 | 是 |
| 899 | F | EURUSD/USDJPY 在 2026-11-16、2026-11-20 单日变动绝对值最大值(%) | 0.22931690890942713 | 0.23 / 0.23 | 是 |
| 900 | F | 同上 ≤0.235(「不超过 0.23%」) | 0.2293 | (判据成立) | 是 |
| 901 | G | S1 前提阈 3.5; 与截止读数相容(EA@2026-10=4.0) | 3.5 | 3.5 / 3.5 | 是 |
| 902 | G | S1 政策分量步长=已观测变更步长 25bp | 25 | 25 / 25 | 是 |
| 903 | G | S1 前提阈 2.0; 与截止读数相容(JP@2026-10=2.44) | 2.0 | 2.0 / 2.0 | 是 |
| 904 | G | S1 前提水平差 1.5; 截止读数 EA−JP=1.56 | 1.5 | 1.5 / 1.5 | 是 |
| 905 | G | S1 证伪阈=S1 前提阈 | 3.5 | 3.5 / 3.5 | 是 |
| 906 | G | S1 证伪阈=S1 前提阈 | 2.0 | 2.0 / 2.0 | 是 |
| 907 | G | S1 证伪阈=S1 前提水平差 | 1.5 | 1.5 / 1.5 | 是 |
| 908 | G | S1 触发阈 4.0=截止读数(不等式成立; 2026-11 期读数未发布故未触发) | 4.0 | 4.0 / 4.0 | 是 |
| 909 | G | S1 触发水平差阈=S1 前提 | 1.5 | 1.5 / 1.5 | 是 |
| 910 | G | S1 VIX 触发阈 30(设定值; 截止前末收盘 35.889999) | 30 | 30 / 30 | 是 |
| 911 | G | S2 前提阈 3.0(与截止读数方向相反=并列反例情景) | 3.0 | 3.0 / 3.0 | 是 |
| 912 | G | S2 前提阈 2.0 | 2.0 | 2.0 / 2.0 | 是 |
| 913 | G | S2 前提水平差 1.0 | 1.0 | 1 / 1 | 是 |
| 914 | G | S2 证伪阈 3.5(较前提 3.0 放缓, 已披露) | 3.5 | 3.5 / 3.5 | 是 |
| 915 | G | S2 证伪文本所引前提阈=S2 前提 | 3.0 | 3.0 / 3.0 | 是 |
| 916 | G | S2 日本端证伪阈=S2 前提 | 2.0 | 2.0 / 2.0 | 是 |
| 917 | G | S2 水平差证伪阈=S2 前提 | 1.0 | 1.0 / 1.0 | 是 |
| 918 | G | S2 触发阈=S2 前提 | 3.0 | 3.0 / 3.0 | 是 |
| 919 | G | S2 触发阈=S2 前提 | 2.0 | 2.0 / 2.0 | 是 |
| 920 | G | S2 触发水平差阈=S2 前提 | 1.0 | 1.0 / 1.0 | 是 |
| 921 | G | S2 VIX 触发阈 25(设定值; 与 S1 的 30 之间为两情景均不触发区, 已披露) | 25 | 25 / 25 | 是 |
| 922 | G | 两情景 rows 五行齐备(scenario/asset_direction/sensitive_variables/falsification/trigger) | [["asset_direction", "falsification", "scenario", "sensitive_variables… | (判据成立) | 是 |
| 923 | G | 两情景方向互补且互斥: EA 端 S1「3.5% 以上」vs S2「3.0% 以下」; 水平差 S1「1.5 或以上」vs S2「1 个百分点以内」 | S1/S2 | (判据成立) | 是 |
| 924 | G | 不触发/不证伪区间已披露(3.0%–3.5%、3.5%–4.0%、VIX 25–30) | quality_gate_notes[3] | (判据成立) | 是 |
| 925 | G | 证伪条件文本确不含 VIX 分量(S1/S2 falsification.threshold) | l4.scenarios[*].rows.falsification.threshold | (判据成立) | 是 |
| 926 | G | 两情景时限 2027-02-15 均晚于 2026-12 期读数推定入档日 | ["2027-01-16", "2027-01-20"] | (判据成立) | 是 |
| 927 | G | 情景观测月 2026-11/2026-12 的推定发布日均晚于研究截止日(未被截止日读数触发或证伪) | ["2026-12-16", "2026-12-20"] | (判据成立) | 是 |
| 928 | G | EA@2026-05 | 3.2 | 3.2 / 3.2 | 是 |
| 929 | G | EA@2026-10 | 4.0 | 4.0 / 4.0 | 是 |
| 930 | G | JP@2026-05 | 1.53 | 1.53 / 1.53 | 是 |
| 931 | G | JP@2026-10 | 2.44 | 2.44 / 2.44 | 是 |
| 932 | G | ECB 两次变更幅(bp) | 25 | 25 / 25 | 是 |
| 933 | G | EA@2026-02 | 1.9 | 1.9 / 1.9 | 是 |
| 934 | G | EA@2026-02 | 1.9 | 1.9 / 1.9 | 是 |
| 935 | G | ECB_MRO@2025-06-11 在值 | 2.15 | 2.15 / 2.15 | 是 |
| 936 | G | ECB_DFR@2025-06-11 在值 | 2.0 | 2.0 / 2.0 | 是 |
| 937 | G | EA@2026-04 | 3.0 | 3.0 / 3.0 | 是 |
| 938 | G | ECB 两次变更幅(bp) | 25 | 25 / 25 | 是 |
| 939 | G | ECB 两次变更幅(bp) | 25 | 25 / 25 | 是 |
| 940 | G | ECB 窗内变更次数 | 2 | 2 / 2 | 是 |
| 941 | G | ECB 窗内变更次数 | 2 | 2 / 2 | 是 |
| 942 | G | JP 决议日 2026-09-18 前可见读数(推定发布规则) | 1.97 | 1.97 / 1.97 | 是 |
| 943 | G | 东京 决议日前可见读数 | 1.9 | 1.9 / 1.9 | 是 |
| 944 | G | JP 决议日前可见读数 | 1.97 | 1.97 / 1.97 | 是 |
| 945 | G | EA 第二次回推决议日(2026-09-10)前可见读数 | 2.9 | 2.9 / 2.9 | 是 |
| 946 | G | 第二次回推决议日(2026-09-10)前可见读数(近十二期)峰值=2026-05 | 3.2 | 3.2 / 3.2 | 是 |
| 947 | G | 按日历两档形态第一次决议日前可见=2026-05 期 | 3.2 | 3.2 / 3.2 | 是 |
| 948 | G | 按日历两档形态第二次决议日前可见=2026-08 期 | 3.2 | 3.2 / 3.2 | 是 |
| 949 | G | days(2025-06-11,2026-06-17) | 371 | 371 / 371 | 是 |
| 950 | G | JP 2025-01..2026-10 谷底=2026-02 | 1.27 | 1.27 / 1.27 | 是 |
| 951 | G | 冻结日历 EA HICP 三条实录均为「次月首日快报(first_publish=次月1日)+次月终值」形态 | [["2021-06-01", "2021-06-17"], ["2022-07-01", "2022-07-19"], ["2025-04… | (判据成立) | 是 |
| 952 | G | 按该两档形态两次回推决议日前可见分别为 2026-05 期(快报 2026-06-01)与 2026-08 期(快报 2026-09-01) | ["2026-06-11", "2026-09-10"] | (判据成立) | 是 |
| 953 | G | ECB_MRO 末值 | 2.65 | 2.65 / 2.65 | 是 |
| 954 | G | 日历 BOJ 目标 | 1.25 | 1.25 / 1.25 | 是 |
| 955 | G | EURUSD×USDJPY@2026-10-23 | 175.61 | 175.61 / 175.61 | 是 |
| 956 | G | EURUSD×USDJPY@2026-11-20 | 175.19 | 175.19 / 175.19 | 是 |
| 957 | G | EURUSD×USDJPY@2026-11-23(2026-11-23) | 174.32 | 174.32 / 174.32 | 是 |
| 958 | G | EURJPY 合成 11-23 对 10-23 变动% | 0.7334261513156415 | 0.73 / 0.73 | 是 |
| 959 | G | EURJPY 合成 11-20 对 10-23 变动% | 0.23632667293717047 | 0.24 / 0.24 | 是 |
| 960 | G | EURJPY 合成 11-23 对 10-23 变动% | 0.7334261513156415 | 0.73 / 0.73 | 是 |
| 961 | G | EURJPY 合成 11-20 对 10-23 变动% | 0.23632667293717047 | 0.24 / 0.24 | 是 |
| 962 | G | EURJPY 合成 11-23 对 10-23 变动% | 0.7334261513156415 | 0.73 / 0.73 | 是 |
| 963 | G | VIX 末观测(盘中) | 27.01 | 27.01 / 27.01 | 是 |
| 964 | G | VIX@2026-11-20 | 35.889999 | 35.89 / 35.89 | 是 |
| 965 | G | VIX 27.01 对 35.89 变动% | 24.742265944337305 | 24.7 / 24.7 | 是 |
| 966 | G | VIX 27.01 对 35.89 变动% | 24.742265944337305 | 24.7 / 24.7 | 是 |
| 967 | G | VIX 10-23→11-20 变动% | 84.52440696532612 | 84.5 / 84.5 | 是 |
| 968 | G | DAX 10-23→11-20 | 1.5045522756340413 | 1.5 / 1.50 | 是 |
| 969 | G | CAC40 10-23→11-20 | 1.8621807940751411 | 1.86 / 1.86 | 是 |
| 970 | G | SPX 10-23→11-20 | 9.356242950032168 | 9.36 / 9.36 | 是 |
| 971 | G | NIKKEI225 10-23→11-20 | 9.979573529233498 | 9.98 / 9.98 | 是 |
| 972 | G | VIX@2026-11-13 | 19.299999 | 19.3 / 19.30 | 是 |
| 973 | G | VIX@2026-11-20 | 35.889999 | 35.89 / 35.89 | 是 |
| 974 | G | days(2026-10-30,2026-11-13) | 14 | 14 / 14 | 是 |
| 975 | G | days(2026-09-16,2026-11-13) | 58 | 58 / 58 | 是 |
| 976 | G | EURUSD/USDJPY 两发布日单日变动绝对值最大值(%) | 0.22931690890942713 | 0.23 / 0.23 | 是 |
| 977 | G | as_of_declared.requested_as_of 月份 | 11 | 11 / 11 | 是 |
| 978 | G | question_window 月数 | 6 | 6 / 六 | 是 |
| 979 | G | EA@2025-10 | 2.1 | 2.1 / 2.1 | 是 |
| 980 | G | JP@2025-10 | 2.99 | 2.99 / 2.99 | 是 |
| 981 | G | PR 六个月前锚(观测月 2026-04) | 0.727 | 0.727 / 0.727 | 是 |
| 982 | G | PR 最新一期锚(观测月 2026-10) | 1.227 | 1.227 / 1.227 | 是 |
| 983 | G | ECB_MRO 最新 − 六个月前锚(bp) | 50 | 50 / 五十 | 是 |
| 984 | G | PR 最新 − 六个月前锚(bp) | 50 | 50 / 五十 | 是 |
| 985 | G | headline 证据不足项顶层顿号分隔计数 | 6 | 6 / 六 | 是 |
| 986 | G | days(ECB 序列末日,研究截止) | 68 | 68 / 六十八 | 是 |
| 987 | G | 「欧元区两年期与十年期在册」(注册表含 BUND_2Y/BUND_10Y) | [true, true] | (判据成立) | 是 |
| 988 | G | 「欧元区两年期与十年期在册」(期限名称,非数值主张) | 在场 | 在场 / 欧元区两年期与十年期在册 | 是 |
| 989 | G | 「日本端事实行在场」(JGB2Y/JGB5Y/JGB10Y 事实行) | [true, true, true] | (判据成立) | 是 |
| 990 | G | 「均不在本问证据索引」(BUND_2Y/BUND_10Y/JGB2Y/JGB5Y/JGB10Y 均不在 evidence_index) | ["AAPL", "BB_OAS", "BEI_10Y", "BEI_5Y", "BRENT_F", "BTC", "B_OAS", "CA… | (判据成立) | 是 |
| 991 | G | 「GDP 两序列在册、当日快照事实行缺席」 | [[true, null], [true, null]] | (判据成立) | 是 |
| 992 | G | EA@2026-02 | 1.9 | 1.9 / 1.9 | 是 |
| 993 | G | EA@2026-05 | 3.2 | 3.2 / 3.2 | 是 |
| 994 | G | 月差 2026-02→2026-05 | 3 | 3 / 三 | 是 |
| 995 | G | EA 2026-05 − 2026-02 | 1.3 | 1.3 / 1.30 | 是 |
| 996 | G | JP@2026-02 | 1.27 | 1.27 / 1.27 | 是 |
| 997 | G | JP@2026-05 | 1.53 | 1.53 / 1.53 | 是 |
| 998 | G | EA 2026 年内谷底=2026-01 | 1.7 | 1.7 / 1.7 | 是 |
| 999 | G | JP 2025-01..2026-10 谷底=2026-02 | 1.27 | 1.27 / 1.27 | 是 |
| 1000 | G | JP@2025-11 | 2.9 | 2.9 / 2.9 | 是 |
| 1001 | G | JP@2026-02 | 1.27 | 1.27 / 1.27 | 是 |
| 1002 | G | 月差 2025-11→2026-02 | 3 | 3 / 三 | 是 |
| 1003 | G | JP 2026-02 − 2025-11 | 1.63 | 1.63 / 1.63 | 是 |
| 1004 | G | 走位面转折条数 | 3 | 3 / 三 | 是 |
| 1005 | G | 回看窗月数 | 6 | 6 / 六 | 是 |
| 1006 | G | EA@2026-06 | 2.8 | 2.8 / 2.8 | 是 |
| 1007 | G | EA@2026-07 | 2.9 | 2.9 / 2.9 | 是 |
| 1008 | G | EA@2026-08 | 3.2 | 3.2 / 3.2 | 是 |
| 1009 | G | EA@2026-09 | 3.8 | 3.8 / 3.8 | 是 |
| 1010 | G | EA@2026-10 | 4.0 | 4.0 / 4.0 | 是 |
| 1011 | G | EA@2026-06 | 2.8 | 2.8 / 2.8 | 是 |
| 1012 | G | EA 2025-11..2026-10 最高=最新读数 | 12 | 12 / 十二 | 是 |
| 1013 | G | PR@2026-04 | 0.727 | 0.727 / 0.727 | 是 |
| 1014 | G | PR@2026-07 | 0.978 | 0.978 / 0.978 | 是 |
| 1015 | G | PR@2026-06 | 0.841 | 0.841 / 0.841 | 是 |
| 1016 | G | PR@2026-05(台阶前值) | 0.727 | 0.727 / 0.727 | 是 |
| 1017 | G | PR@2026-06 | 0.841 | 0.841 / 0.841 | 是 |
| 1018 | G | PR@2026-08 | 0.977 | 0.977 / 0.977 | 是 |
| 1019 | G | PR@2026-09 | 1.043 | 1.043 / 1.043 | 是 |
| 1020 | G | PR@2026-10 | 1.227 | 1.227 / 1.227 | 是 |
| 1021 | G | PR@2026-09 | 1.043 | 1.043 / 1.043 | 是 |
| 1022 | G | PR@2026-10 | 1.227 | 1.227 / 1.227 | 是 |
| 1023 | G | TK@2026-06 | 1.6 | 1.6 / 1.6 | 是 |
| 1024 | G | TK@2026-09 | 2.69 | 2.69 / 2.69 | 是 |
| 1025 | G | 月差 2026-06→2026-09 | 3 | 3 / 三 | 是 |
| 1026 | G | TK 2026-09 − 2026-06 | 1.09 | 1.09 / 1.09 | 是 |
| 1027 | G | EA@2026-09 | 3.8 | 3.8 / 3.8 | 是 |
| 1028 | G | TK@2026-09 | 2.69 | 2.69 / 2.69 | 是 |
| 1029 | G | JP@2026-06 | 1.67 | 1.67 / 1.67 | 是 |
| 1030 | G | JP@2026-08 | 1.98 | 1.98 / 1.98 | 是 |
| 1031 | G | JP − EA @2026-09 | 1.64 | 1.64 / 1.64 | 是 |
| 1032 | G | TK − EA @2026-09 | 1.11 | 1.11 / 1.11 | 是 |
| 1033 | G | TK@2026-08 | 1.9 | 1.9 / 1.9 | 是 |
| 1034 | G | 东京 2026-08 期推定发布日(月末−1) | 2026-08-30 | 2026-08-30 | 是 |
| 1035 | G | 该推定日星期 | 周日 | 周日 | 是 |
| 1036 | G | 官方实录锚 2026-06-26、2026-10-30 均为当月最后一个周五 | ["2026-06-26", "2026-10-30"] | (判据成立) | 是 |
| 1037 | G | 按「当月最后一个周五」形态东京可见性结论不变: 2026-08 期 08-28 早于 BOJ 决议日 09-18; 2026-09 期 09-25 晚于 09-18 | ["2026-08-28", "2026-09-25"] | (判据成立) | 是 |
| 1038 | G | l4 历史类比段数(键 ['history_periods']) | 0 | 0 / 0 | 是 |
| 1039 | G | S6 analog 扫描候选月数(report.json 标量 1871) | 1871 | 1871 / 1871 | 是 |
| 1040 | G | S6 analog 有效候选月数 | 74 | 74 / 74 | 是 |
| 1041 | G | S6 analog TOP1 距离 | 0.727212 | 0.727 / 0.727 | 是 |
| 1042 | G | S6 analog TOP1 候选月=2025-03(同一容器内字符串) | ["steps", 42, "envelope", "data"] | (判据成立) | 是 |
| 1043 | G | 回看窗月数 | 6 | 6 / 六 | 是 |
| 1044 | G | l3.contradictions 条数 | 3 | 3 / 三 | 是 |
| 1045 | G | M1 links 环数 | 4 | 4 / 四 | 是 |
| 1046 | G | l4.scenarios asset_direction evidence_refs 亦全部解析到 evidence_index(kind=snapshot_fact) | ["NIKKEI225@2026-11-20", "VIX@2026-11-23"] | (判据成立) | 是 |
| 1047 | G | l3(三条矛盾陈述+机制链四环) evidence_refs 条目数且全部在 evidence_index(kind=snapshot_fact) | 21 | 21 / 21 | 是 |
| 1048 | G | 每条矛盾陈述 competing_explanations 条数 | 2 | 2 / 2 | 是 |
| 1049 | G | 传导链环数 | 3 | 3 / 三 | 是 |
| 1050 | G | face_off_verdict=支持主解释 环数 | 0 | 0 / 0 | 是 |
| 1051 | G | face_off_verdict=支持竞争解释 环数 | 0 | 0 / 0 | 是 |
| 1052 | G | face_off_verdict=尚不能区分 环数 | 3 | 3 / 3 | 是 |
| 1053 | G | M1 links[2] 证据级 | 3 | 3 / 3 | 是 |
| 1054 | G | M1 links[3] 证据级 | 4 | 4 / 4 | 是 |
| 1055 | G | M1 step3/step4 E2 | 2 | 2 / 2 | 是 |
| 1056 | G | 四类标注在判断档文本中出现数 | 4 | 4 / 四 | 是 |
| 1057 | G | 每情景 rows 键数 | 5 | 5 / 五 | 是 |
| 1058 | G | S1 前提/证伪阈 EA | 3.5 | 3.5 / 3.5 | 是 |
| 1059 | G | S1 前提/证伪阈 JP | 2.0 | 2.0 / 2.0 | 是 |
| 1060 | G | S1 前提/证伪阈 水平差 | 1.5 | 1.5 / 1.5 | 是 |
| 1061 | G | S2 证伪阈 EA | 3.5 | 3.5 / 3.5 | 是 |
| 1062 | G | S2 前提 EA | 3.0 | 3.0 / 3.0 | 是 |
| 1063 | G | S2 前提 EA | 3.0 | 3.0 / 3.0 | 是 |
| 1064 | G | S2 证伪阈 EA | 3.5 | 3.5 / 3.5 | 是 |
| 1065 | G | S1 触发阈 EA | 4.0 | 4.0 / 4.0 | 是 |
| 1066 | G | S1 前提 EA | 3.5 | 3.5 / 3.5 | 是 |
| 1067 | G | S1 前提 EA | 3.5 | 3.5 / 3.5 | 是 |
| 1068 | G | S1 触发阈 EA | 4.0 | 4.0 / 4.0 | 是 |
| 1069 | G | S2 VIX 触发阈 | 25 | 25 / 25 | 是 |
| 1070 | G | S1 VIX 触发阈 | 30 | 30 / 30 | 是 |
| 1071 | G | requested_as_of 月份 | 11 | 11 / 11 | 是 |
| 1072 | G | 冻结日历版本串 v1.5.0 | 1.5 | 1.5 / 1.5 | 是 |
| 1073 | G | 冻结日历版本串 v1.5.0 | 0 | 0 / 0 | 是 |
| 1074 | G | policy_window_path 窗月数 ['2025-11-23', '2026-11-23'] | 12 | 12 / 12 | 是 |
| 1075 | G | 注册表 ECB_MRO.freshness.max_calendar_lag_days | 10 | 10 / 10 | 是 |
| 1076 | G | 快照采集时刻 2026-11-23T22:53:47+08:00 在冻结快照文本内 | snapshot 文本检索 | (判据成立) | 是 |
| 1077 | G | 纽约 当地时刻=北京 22:53 按 11 月标准时(UTC-5)换算 | 09:53 | 09:53 / 09:53 | 是 |
| 1078 | G | 柏林 当地时刻=北京 22:53 按 11 月标准时(UTC1)换算 | 15:53 | 15:53 / 15:53 | 是 |
| 1079 | G | 东京 当地时刻=北京 22:53 按 11 月标准时(UTC+9)换算 | 23:53 | 23:53 / 23:53 | 是 |
| 1080 | G | 上海 当地时刻=北京 22:53 按 11 月标准时(UTC+8)换算 | 22:53 | 22:53 / 22:53 | 是 |
| 1081 | G | ①②③ 计数 | 3 | 3 / 三 | 是 |
| 1082 | G | 源码 judgment_contract.py: def _map_checks 与检查(13)注释在场 | 13 | 13 / 13 | 是 |
| 1083 | G | 源码硬编码锚标签行在场 | 12 | 12 / 12 | 是 |
| 1084 | G | 源码硬编码锚标签行在场 | 3 | 3 / 3 | 是 |
| 1085 | G | 锚标签「6个月前」 | 6 | 6 / 6 | 是 |
| 1086 | G | point_values 各格 anchors 键集合恰为 {6个月前, 最新一期} | [["6个月前", "最新一期"], ["6个月前", "最新一期"]] | (判据成立) | 是 |
| 1087 | G | text_consistency.ALIASES 不含 JP_CPI_YOY/EA_HICP_YOY/JP_CPI_TOKYO_YOY/JP_POLICY_TARGET/ECB_M… | ["n_keys", 72] | (判据成立) | 是 |
| 1088 | G | ALIASES 含 JP_POLICY_RATE/JGB10Y/JGB2Y/ECB_DFR(带别名指标最新值由契约逐位核验的陈述前提) |  | (判据成立) | 是 |
| 1089 | G | data_requirements.outcome(EA_HICP_YOY,JP_CPI_YOY,JP_CPI_TOKYO_YOY,JP_POLICY_RATE,ECB_MRO,E… | ["satisfied", "satisfied", "satisfied", "satisfied", "insufficient_cov… | ["satisfied", "satisfied", "satisfied", "satisfied… | 是 |
| 1090 | G | ECB_MRO 窗内有效观测 n_in_window | 2 | 2 | 是 |
| 1091 | G | report.notes 含 ECB_MRO、ECB_DFR「地图计划指标缺数」披露 | true | true | 是 |
| 1092 | G | evidence_index 60 条 ref 逐条解析(snapshot_fact: METRIC@观测日 ∈ series_store 观测日或 facts 观测日; s3_e… | [35, 25, [], []] | (判据成立) | 是 |
| 1093 | MAP | SPX 起值@2026-10-23(实际观测 2026-10-23) ¦ 文内 token 7623.68 | ["7623.68", 7623.680176] | (判据成立) | 是 |
| 1094 | MAP | SPX 末值@2026-11-23(实际观测 2026-11-23) ¦ 文内 token 7203.85 | ["7203.85", 7203.850098] | (判据成立) | 是 |
| 1095 | MAP | SPX 变动% ¦ 文内 token -5.51 | ["-5.51", -5.506921438305623] | (判据成立) | 是 |
| 1096 | MAP | SPX 指数点变动 ¦ 文内 token -419.83 | ["-419.83", -419.83007799999996] | (判据成立) | 是 |
| 1097 | MAP | SHCOMP 起值@2026-10-23(实际观测 2026-10-23) ¦ 文内 token 3690.48 | ["3690.48", 3690.4753] | (判据成立) | 是 |
| 1098 | MAP | SHCOMP 末值@2026-11-23(实际观测 2026-11-23) ¦ 文内 token 3538.95 | ["3538.95", 3538.948] | (判据成立) | 是 |
| 1099 | MAP | SHCOMP 变动% ¦ 文内 token -4.11 | ["-4.11", -4.105902022972496] | (判据成立) | 是 |
| 1100 | MAP | SHCOMP 指数点变动 ¦ 文内 token -151.527 | ["-151.527", -151.5273000000002] | (判据成立) | 是 |
| 1101 | MAP | DAX 起值@2026-10-23(实际观测 2026-10-23) ¦ 文内 token 25181.7 | ["25181.7", 25181.650391] | (判据成立) | 是 |
| 1102 | MAP | DAX 末值@2026-11-23(实际观测 2026-11-23) ¦ 文内 token 25209.4 | ["25209.4", 25209.449219] | (判据成立) | 是 |
| 1103 | MAP | DAX 变动% ¦ 文内 token +0.11 | ["+0.11", 0.11039319333070452] | (判据成立) | 是 |
| 1104 | MAP | DAX 指数点变动 ¦ 文内 token +27.7988 | ["+27.7988", 27.798827999999048] | (判据成立) | 是 |
| 1105 | MAP | NIKKEI225 起值@2026-10-23(实际观测 2026-10-23) ¦ 文内 token 62693.2 | ["62693.2", 62693.16] | (判据成立) | 是 |
| 1106 | MAP | NIKKEI225 末值@2026-11-20(实际观测 2026-11-20) ¦ 文内 token 56436.7 | ["56436.7", 56436.65] | (判据成立) | 是 |
| 1107 | MAP | NIKKEI225 变动% ¦ 文内 token -9.98 | ["-9.98", -9.979573529233498] | (判据成立) | 是 |
| 1108 | MAP | NIKKEI225 指数点变动 ¦ 文内 token -6256.51 | ["-6256.51", -6256.510000000002] | (判据成立) | 是 |
| 1109 | MAP | VIX 起值@2026-10-23(实际观测 2026-10-23) ¦ 文内 token 19.45 | ["19.45", 19.450001] | (判据成立) | 是 |
| 1110 | MAP | VIX 末值@2026-11-23(实际观测 2026-11-23) ¦ 文内 token 27.01 | ["27.01", 27.01] | (判据成立) | 是 |
| 1111 | MAP | VIX 变动% ¦ 文内 token +38.87 | ["+38.87", 38.86888746175386] | (判据成立) | 是 |
| 1112 | MAP | VIX 指数点变动 ¦ 文内 token +7.56 | ["+7.56", 7.559999000000001] | (判据成立) | 是 |
| 1113 | MAP | DXY 起值@2026-10-23(实际观测 2026-10-23) ¦ 文内 token 101.81 | ["101.81", 101.809998] | (判据成立) | 是 |
| 1114 | MAP | DXY 末值@2026-11-23(实际观测 2026-11-23) ¦ 文内 token 104.079 | ["104.079", 104.079002] | (判据成立) | 是 |
| 1115 | MAP | DXY 变动% ¦ 文内 token +2.23 | ["+2.23", 2.2286652043741473] | (判据成立) | 是 |
| 1116 | MAP | DXY 指数点变动 ¦ 文内 token +2.269 | ["+2.269", 2.2690040000000096] | (判据成立) | 是 |
| 1117 | MAP | GOLD_F 起值@2026-10-23(实际观测 2026-10-23) ¦ 文内 token 4007.9 | ["4007.9", 4007.899902] | (判据成立) | 是 |
| 1118 | MAP | GOLD_F 末值@2026-11-23(实际观测 2026-11-23) ¦ 文内 token 3685.2 | ["3685.2", 3685.199951] | (判据成立) | 是 |
| 1119 | MAP | GOLD_F 变动% ¦ 文内 token -8.05 | ["-8.05", -8.051597068054717] | (判据成立) | 是 |
| 1120 | MAP | GOLD_F 指数点变动 ¦ 文内 token -322.7 | ["-322.7", -322.69995100000006] | (判据成立) | 是 |
| 1121 | MAP | UST_10Y 起值@2026-10-23(实际观测 2026-10-23) ¦ 文内 token 5 | ["5", 5.0] | (判据成立) | 是 |
| 1122 | MAP | UST_10Y 末值@2026-11-19(实际观测 2026-11-19) ¦ 文内 token 5.04 | ["5.04", 5.04] | (判据成立) | 是 |
| 1123 | MAP | UST_10Y 变动% ¦ 文内 token +0.8 | ["+0.8", 0.8000000000000007] | (判据成立) | 是 |
| 1124 | MAP | UST_10Y 指数点变动 ¦ 文内 token +0.04 | ["+0.04", 0.040000000000000036] | (判据成立) | 是 |
| 1125 | MAP | MAP 资产月窗表行数(L112-L119) | 8 | 8 | 是 |
| 1126 | MAP | VIX 收盘 2026-11-13 ¦ 文内 token 19.30 | ["19.30", 19.299999] | (判据成立) | 是 |
| 1127 | MAP | VIX 收盘 2026-11-16 ¦ 文内 token 22.91 | ["22.91", 22.91] | (判据成立) | 是 |
| 1128 | MAP | VIX 收盘 2026-11-17 ¦ 文内 token 25.46 | ["25.46", 25.459999] | (判据成立) | 是 |
| 1129 | MAP | VIX 收盘 2026-11-18 ¦ 文内 token 24.56 | ["24.56", 24.559999] | (判据成立) | 是 |
| 1130 | MAP | VIX 收盘 2026-11-19 ¦ 文内 token 28.44 | ["28.44", 28.440001] | (判据成立) | 是 |
| 1131 | MAP | VIX 收盘 2026-11-20 ¦ 文内 token 35.89 | ["35.89", 35.889999] | (判据成立) | 是 |
| 1132 | MAP | EURUSD 10-23 收盘 ¦ 文内 token 1.1221 | ["1.1221", 1.122146] | (判据成立) | 是 |
| 1133 | MAP | EURUSD 11-20 收盘 ¦ 文内 token 1.0970 | ["1.0970", 1.096972] | (判据成立) | 是 |
| 1134 | MAP | EURUSD 至 11-20 变动% ¦ 文内 token -2.24 | ["-2.24", -2.2433800949252625] | (判据成立) | 是 |
| 1135 | MAP | EURUSD 截止日盘中值与对 10-23 变动%(引擎当前面) | [["2026-11-23", 1.093972], -2.511, ["EURUSD 1.0940(-2.51%)", "EURUSD 1… | (判据成立) | 是 |
| 1136 | MAP | USDJPY 10-23 收盘 ¦ 文内 token 156.494 | ["156.494", 156.494003] | (判据成立) | 是 |
| 1137 | MAP | USDJPY 11-20 收盘 ¦ 文内 token 159.707 | ["159.707", 159.707001] | (判据成立) | 是 |
| 1138 | MAP | USDJPY 至 11-20 变动% ¦ 文内 token +2.05 | ["+2.05", 2.053112540037705] | (判据成立) | 是 |
| 1139 | MAP | USDJPY 截止日盘中值与对 10-23 变动%(引擎当前面) | [["2026-11-23", 159.347], 1.823, ["USDJPY 159.347(+1.82%)", "USDJPY 15… | (判据成立) | 是 |
| 1140 | MAP | DXY 10-23 收盘 ¦ 文内 token 101.81 | ["101.81", 101.809998] | (判据成立) | 是 |
| 1141 | MAP | DXY 11-20 收盘 ¦ 文内 token 103.81 | ["103.81", 103.809998] | (判据成立) | 是 |
| 1142 | MAP | DXY 至 11-20 变动% ¦ 文内 token +1.96 | ["+1.96", 1.9644436099488072] | (判据成立) | 是 |
| 1143 | MAP | DXY 截止日盘中值与对 10-23 变动%(引擎当前面) | [["2026-11-23", 104.079002], 2.229, ["DXY 104.079(+2.23%)", "DXY 104.0… | (判据成立) | 是 |
| 1144 | MAP | 引擎当前面「近30日 A→B,Δ 指数点(x%)」可由 10-23 观测→截止日观测复算: 近30日1.12215→1.09397,-0.028174 指数点(-2.51%) | [["EURUSD", true], ["VIX", false]] | (判据成立) | 是 |
| 1145 | MAP | 引擎当前面「近30日 A→B,Δ 指数点(x%)」可由 10-23 观测→截止日观测复算: 近30日19.45→27.01,+7.56 指数点(+38.87%) | [["EURUSD", false], ["VIX", true]] | (判据成立) | 是 |
| 1146 | MAP | 引擎当前面「近30日 A→B,Δ 指数点(x%)」可由 10-23 观测→截止日观测复算: 近30日1.12215→1.09397,-0.028174 指数点(-2.51%) | [["EURUSD", true], ["VIX", false]] | (判据成立) | 是 |
| 1147 | MAP | 引擎当前面「近30日 A→B,Δ 指数点(x%)」可由 10-23 观测→截止日观测复算: 近30日19.45→27.01,+7.56 指数点(+38.87%) | [["EURUSD", false], ["VIX", true]] | (判据成立) | 是 |
| 1148 | MAP | 「2026-11-23=1.09397」=EURUSD 截止日观测 | ["2026-11-23", 1.093972] | (判据成立) | 是 |
| 1149 | MAP | 「2026-11-23=27.01」=VIX 截止日观测 | ["2026-11-23", 27.01] | (判据成立) | 是 |
| 1150 | MAP | 「2026-10-01=4」=EA@2026-10 且「2026-09-01=3.8→2026-10-01=4,Δ+20bp」 | [3.8, 4.0] | (判据成立) | 是 |
| 1151 | MAP | JP_CPI_YOY 候选 2025-11..2026-02 起→末(2.9→1.27) | [2.9, 1.27] | (判据成立) | 是 |
| 1152 | MAP | JP_CPI_YOY 候选变动 -1.63 | -1.63 | (判据成立) | 是 |
| 1153 | MAP | EA_HICP_YOY 候选 2026-02..2026-05 起→末(1.9→3.2) | [1.9, 3.2] | (判据成立) | 是 |
| 1154 | MAP | EA_HICP_YOY 候选变动 1.3 | 1.3 | (判据成立) | 是 |
| 1155 | MAP | JP_CPI_TOKYO_YOY 候选 2026-06..2026-09 起→末(1.6→2.69) | [1.6, 2.69] | (判据成立) | 是 |
| 1156 | MAP | JP_CPI_TOKYO_YOY 候选变动 1.09 | 1.09 | (判据成立) | 是 |
| 1157 | MAP | JP_POLICY_RATE 候选 2026-04..2026-07 起→末(0.727→0.978) | [0.727, 0.978] | (判据成立) | 是 |
| 1158 | MAP | JP_POLICY_RATE 候选变动 0.251 | 0.251 | (判据成立) | 是 |
| 1159 | MAP | MAP 候选表行数 | 4 | 4 | 是 |
| 1160 | G | 「引擎候选面另列日本全国 CPI 2025-11→2026-02…为幅度最大候选」=候选表 ¦变动¦ 最大行 | ["JP_CPI_YOY", 1.63] | (判据成立) | 是 |
| 1161 | G | evidence_index SPX@2026-11-23 -> series_store 该日有值 | ["SPX", "2026-11-23", 7203.850098] | (判据成立) | 是 |
| 1162 | G | evidence_index NDX@2026-11-23 -> series_store 该日有值 | ["NDX", "2026-11-23", 26672.849609] | (判据成立) | 是 |
| 1163 | G | evidence_index RUT@2026-11-20 -> series_store 该日有值 | ["RUT", "2026-11-20", 2581.790039] | (判据成立) | 是 |
| 1164 | G | evidence_index DXY@2026-11-23 -> series_store 该日有值 | ["DXY", "2026-11-23", 104.079002] | (判据成立) | 是 |
| 1165 | G | evidence_index EURUSD@2026-11-23 -> series_store 该日有值 | ["EURUSD", "2026-11-23", 1.093972] | (判据成立) | 是 |
| 1166 | G | evidence_index GOLD_F@2026-11-23 -> series_store 该日有值 | ["GOLD_F", "2026-11-23", 3685.199951] | (判据成立) | 是 |
| 1167 | G | evidence_index SILVER_F@2026-11-23 -> series_store 该日有值 | ["SILVER_F", "2026-11-23", 43.875] | (判据成立) | 是 |
| 1168 | G | evidence_index BRENT_F@2026-11-23 -> series_store 该日有值 | ["BRENT_F", "2026-11-23", 88.190002] | (判据成立) | 是 |
| 1169 | G | evidence_index VIX@2026-11-23 -> series_store 该日有值 | ["VIX", "2026-11-23", 27.01] | (判据成立) | 是 |
| 1170 | G | evidence_index DAX@2026-11-23 -> series_store 该日有值 | ["DAX", "2026-11-23", 25209.449219] | (判据成立) | 是 |
| 1171 | G | evidence_index CAC40@2026-11-23 -> series_store 该日有值 | ["CAC40", "2026-11-23", 8022.620117] | (判据成立) | 是 |
| 1172 | G | evidence_index USDJPY@2026-11-23 -> series_store 该日有值 | ["USDJPY", "2026-11-23", 159.347] | (判据成立) | 是 |
| 1173 | G | evidence_index USDCNY@2026-11-23 -> series_store 该日有值 | ["USDCNY", "2026-11-23", 6.6542] | (判据成立) | 是 |
| 1174 | G | evidence_index HY_OAS@2026-11-19 -> series_store 该日有值 | ["HY_OAS", "2026-11-19", 3.52] | (判据成立) | 是 |
| 1175 | G | evidence_index BB_OAS@2026-11-19 -> series_store 该日有值 | ["BB_OAS", "2026-11-19", 2.1] | (判据成立) | 是 |
| 1176 | G | evidence_index B_OAS@2026-11-19 -> series_store 该日有值 | ["B_OAS", "2026-11-19", 3.8] | (判据成立) | 是 |
| 1177 | G | evidence_index CCC_OAS@2026-11-19 -> series_store 该日有值 | ["CCC_OAS", "2026-11-19", 13.61] | (判据成立) | 是 |
| 1178 | G | evidence_index IG_OAS@2026-11-19 -> series_store 该日有值 | ["IG_OAS", "2026-11-19", 0.94] | (判据成立) | 是 |
| 1179 | G | evidence_index UST_2Y@2026-11-19 -> series_store 该日有值 | ["UST_2Y", "2026-11-19", 4.76] | (判据成立) | 是 |
| 1180 | G | evidence_index UST_10Y@2026-11-19 -> series_store 该日有值 | ["UST_10Y", "2026-11-19", 5.04] | (判据成立) | 是 |
| 1181 | G | evidence_index UST_30Y@2026-11-19 -> series_store 该日有值 | ["UST_30Y", "2026-11-19", 5.4] | (判据成立) | 是 |
| 1182 | G | evidence_index TIPS_5Y@2026-11-19 -> series_store 该日有值 | ["TIPS_5Y", "2026-11-19", 2.64] | (判据成立) | 是 |
| 1183 | G | evidence_index TIPS_10Y@2026-11-19 -> series_store 该日有值 | ["TIPS_10Y", "2026-11-19", 2.88] | (判据成立) | 是 |
| 1184 | G | evidence_index BEI_5Y@2026-11-20 -> series_store 该日有值 | ["BEI_5Y", "2026-11-20", 2.18] | (判据成立) | 是 |
| 1185 | G | evidence_index BEI_10Y@2026-11-20 -> series_store 该日有值 | ["BEI_10Y", "2026-11-20", 2.15] | (判据成立) | 是 |
| 1186 | G | evidence_index CURVE_2S10S@2026-11-20 -> series_store 该日有值 | ["CURVE_2S10S", "2026-11-20", 0.29] | (判据成立) | 是 |
| 1187 | G | evidence_index UST_5Y@2026-11-19 -> series_store 该日有值 | ["UST_5Y", "2026-11-19", 4.86] | (判据成立) | 是 |
| 1188 | G | evidence_index SHCOMP@2026-11-23 -> series_store 该日有值 | ["SHCOMP", "2026-11-23", 3538.948] | (判据成立) | 是 |
| 1189 | G | evidence_index HSI@2026-11-23 -> series_store 该日有值 | ["HSI", "2026-11-23", 22383.74] | (判据成立) | 是 |
| 1190 | G | evidence_index NIKKEI225@2026-11-20 -> series_store 该日有值 | ["NIKKEI225", "2026-11-20", 56436.65] | (判据成立) | 是 |
| 1191 | G | evidence_index JP_CPI_YOY@2026-10-01 -> series_store 该日有值 | ["JP_CPI_YOY", "2026-10-01", 2.44] | (判据成立) | 是 |
| 1192 | G | evidence_index ECB_DFR@2026-09-16 -> series_store 该日有值 | ["ECB_DFR", "2026-09-16", 2.5] | (判据成立) | 是 |
| 1193 | G | evidence_index ECB_MRO@2026-09-16 -> series_store 该日有值 | ["ECB_MRO", "2026-09-16", 2.65] | (判据成立) | 是 |
| 1194 | G | evidence_index EA_HICP_YOY@2026-10-01 -> series_store 该日有值 | ["EA_HICP_YOY", "2026-10-01", 4.0] | (判据成立) | 是 |
| 1195 | G | evidence_index JP_POLICY_RATE@2026-10-01 -> series_store 该日有值 | ["JP_POLICY_RATE", "2026-10-01", 1.227] | (判据成立) | 是 |
| 1196 | G | evidence_index SZCI@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | SZCI | (判据成立) | 是 |
| 1197 | G | evidence_index CHINEXT@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | CHINEXT | (判据成立) | 是 |
| 1198 | G | evidence_index HSCEI@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | HSCEI | (判据成立) | 是 |
| 1199 | G | evidence_index NVDA@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | NVDA | (判据成立) | 是 |
| 1200 | G | evidence_index AAPL@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | AAPL | (判据成立) | 是 |
| 1201 | G | evidence_index MSFT@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | MSFT | (判据成立) | 是 |
| 1202 | G | evidence_index TLT@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | TLT | (判据成立) | 是 |
| 1203 | G | evidence_index IEF@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | IEF | (判据成立) | 是 |
| 1204 | G | evidence_index SHY@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | SHY | (判据成立) | 是 |
| 1205 | G | evidence_index HYG@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | HYG | (判据成立) | 是 |
| 1206 | G | evidence_index LQD@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | LQD | (判据成立) | 是 |
| 1207 | G | evidence_index GBPUSD@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | GBPUSD | (判据成立) | 是 |
| 1208 | G | evidence_index WTI_F@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | WTI_F | (判据成立) | 是 |
| 1209 | G | evidence_index GLD@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | GLD | (判据成立) | 是 |
| 1210 | G | evidence_index USO@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | USO | (判据成立) | 是 |
| 1211 | G | evidence_index EEM@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | EEM | (判据成立) | 是 |
| 1212 | G | evidence_index EZU@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | EZU | (判据成立) | 是 |
| 1213 | G | evidence_index FEZ@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | FEZ | (判据成立) | 是 |
| 1214 | G | evidence_index EWU@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | EWU | (判据成立) | 是 |
| 1215 | G | evidence_index EWG@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | EWG | (判据成立) | 是 |
| 1216 | G | evidence_index EWJ@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | EWJ | (判据成立) | 是 |
| 1217 | G | evidence_index INDA@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | INDA | (判据成立) | 是 |
| 1218 | G | evidence_index FXI@2026-11-23 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | FXI | (判据成立) | 是 |
| 1219 | G | evidence_index BTC@2026-11-22 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | BTC | (判据成立) | 是 |
| 1220 | G | evidence_index HY_IG_DIFF@2026-11-19 (s3_envelope) -> 该指标在 report.json S3 步/L1 行在场 | HY_IG_DIFF | (判据成立) | 是 |
| 1221 | N | l3.mechanism_chains[0].links[0].step | 1 | 1 | 是 |
| 1222 | N | l3.mechanism_chains[0].links[1].step | 2 | 2 | 是 |
| 1223 | N | l3.mechanism_chains[0].links[2].step | 3 | 3 | 是 |
| 1224 | N | l3.mechanism_chains[0].links[3].step | 4 | 4 | 是 |
| 1225 | N | series_store.NIKKEI225 @2026-10-23→2026-11-20 同口径变动% | -9.98 | -9.98 | 是 |
| 1226 | N | asset_returns_echo NIKKEI225 window_months | 1 | 1 | 是 |
| 1227 | N | 资产月窗起(窗末=截止日 2026-11-23 的一个月前) | 2026-10-23 | 2026-10-23 | 是 |
| 1228 | N | series_store.NIKKEI225 最后观测日(不晚于截止日) | 2026-11-20 | 2026-11-20 | 是 |
| 1229 | N | series_store.DAX @2026-10-23→2026-11-23 同口径变动% | 0.11 | 0.11 | 是 |
| 1230 | N | asset_returns_echo DAX window_months | 1 | 1 | 是 |
| 1231 | N | 资产月窗起(窗末=截止日 2026-11-23 的一个月前) | 2026-10-23 | 2026-10-23 | 是 |
| 1232 | N | series_store.DAX 最后观测日(不晚于截止日) | 2026-11-23 | 2026-11-23 | 是 |
| 1233 | N | series_store.SPX @2026-10-23→2026-11-23 同口径变动% | -5.51 | -5.51 | 是 |
| 1234 | N | asset_returns_echo SPX window_months | 1 | 1 | 是 |
| 1235 | N | 资产月窗起(窗末=截止日 2026-11-23 的一个月前) | 2026-10-23 | 2026-10-23 | 是 |
| 1236 | N | series_store.SPX 最后观测日(不晚于截止日) | 2026-11-23 | 2026-11-23 | 是 |
| 1237 | N | series_store.VIX @2026-10-23→2026-11-23 同口径变动% | 38.87 | 38.87 | 是 |
| 1238 | N | asset_returns_echo VIX window_months | 1 | 1 | 是 |
| 1239 | N | 资产月窗起(窗末=截止日 2026-11-23 的一个月前) | 2026-10-23 | 2026-10-23 | 是 |
| 1240 | N | series_store.VIX 最后观测日(不晚于截止日) | 2026-11-23 | 2026-11-23 | 是 |
| 1241 | N | series_store UST_10Y 2026-10-20→2026-11-19 变动bp | -8.0 | -8.0 | 是 |
| 1242 | N | series_store TIPS_10Y 同窗变动bp | 11.0 | 11.0 | 是 |
| 1243 | N | series_store BEI_10Y 同窗变动bp | -19.0 | -19.0 | 是 |
| 1244 | N | 名义=实际+盈亏平衡 恒等残差bp(判断档值) | 0.0 | 0.0 | 是 |
| 1245 | N | 名义−实际−盈亏平衡 残差bp(直算) | 0.0 | 0.0 | 是 |
| 1246 | N | us_rates_trio.window == reader_map.rates_decomposition 窗 | ["2026-10-20", "2026-11-19"] | ["2026-10-20", "2026-11-19"] | 是 |
| 1247 | N | UST_10Y@窗末 == TIPS_10Y@窗末 + BEI_10Y@窗末 | 5.04 | 5.04 | 是 |
| 1248 | N | series_store.EA_HICP_YOY@2026-02 | 1.9 | 1.9 | 是 |
| 1249 | N | series_store.EA_HICP_YOY@2026-05 | 3.2 | 3.2 | 是 |
| 1250 | N | series_store.JP_POLICY_RATE@2026-04 | 0.727 | 0.727 | 是 |
| 1251 | N | series_store.JP_POLICY_RATE@2026-07 | 0.978 | 0.978 | 是 |
| 1252 | N | series_store.JP_CPI_TOKYO_YOY@2026-06 | 1.6 | 1.6 | 是 |
| 1253 | N | series_store.JP_CPI_TOKYO_YOY@2026-09 | 2.69 | 2.69 | 是 |
| 1254 | N | series_store.ECB_MRO@2025-06 | 2.15 | 2.15 | 是 |
| 1255 | N | anchor_echo ECB_MRO 键集 | ["anchor", "metric_id", "observation_month", "value"] | ["anchor", "metric_id", "observation_month", "valu… | 是 |
| 1256 | N | series_store.ECB_MRO@2026-09 | 2.65 | 2.65 | 是 |
| 1257 | N | anchor_echo ECB_MRO 键集 | ["anchor", "metric_id", "observation_month", "value"] | ["anchor", "metric_id", "observation_month", "valu… | 是 |
| 1258 | N | series_store.ECB_DFR@2025-06 | 2.0 | 2.0 | 是 |
| 1259 | N | anchor_echo ECB_DFR 键集 | ["anchor", "metric_id", "observation_month", "value"] | ["anchor", "metric_id", "observation_month", "valu… | 是 |
| 1260 | N | series_store.ECB_DFR@2026-09 | 2.5 | 2.5 | 是 |
| 1261 | N | anchor_echo ECB_DFR 键集 | ["anchor", "metric_id", "observation_month", "value"] | ["anchor", "metric_id", "observation_month", "valu… | 是 |
| 1262 | N | series_store.EA_HICP_YOY@2026-04 | 3.0 | 3.0 | 是 |
| 1263 | N | anchor_echo EA_HICP_YOY 键集 | ["anchor", "metric_id", "observation_month", "value"] | ["anchor", "metric_id", "observation_month", "valu… | 是 |
| 1264 | N | series_store.EA_HICP_YOY@2026-10 | 4.0 | 4.0 | 是 |
| 1265 | N | anchor_echo EA_HICP_YOY 键集 | ["anchor", "metric_id", "observation_month", "value"] | ["anchor", "metric_id", "observation_month", "valu… | 是 |
| 1266 | N | series_store.JP_POLICY_RATE@2026-04 | 0.727 | 0.727 | 是 |
| 1267 | N | anchor_echo JP_POLICY_RATE 键集 | ["anchor", "metric_id", "observation_month", "value"] | ["anchor", "metric_id", "observation_month", "valu… | 是 |
| 1268 | N | series_store.JP_POLICY_RATE@2026-10 | 1.227 | 1.227 | 是 |
| 1269 | N | anchor_echo JP_POLICY_RATE 键集 | ["anchor", "metric_id", "observation_month", "value"] | ["anchor", "metric_id", "observation_month", "valu… | 是 |
| 1270 | N | series_store.JP_CPI_YOY@2026-04 | 1.38 | 1.38 | 是 |
| 1271 | N | anchor_echo JP_CPI_YOY 键集 | ["anchor", "metric_id", "observation_month", "value"] | ["anchor", "metric_id", "observation_month", "valu… | 是 |
| 1272 | N | series_store.JP_CPI_YOY@2026-10 | 2.44 | 2.44 | 是 |
| 1273 | N | anchor_echo JP_CPI_YOY 键集 | ["anchor", "metric_id", "observation_month", "value"] | ["anchor", "metric_id", "observation_month", "valu… | 是 |
| 1274 | N | series_store.JP_CPI_TOKYO_YOY@2026-04 | 1.42 | 1.42 | 是 |
| 1275 | N | anchor_echo JP_CPI_TOKYO_YOY 键集 | ["anchor", "metric_id", "observation_month", "value"] | ["anchor", "metric_id", "observation_month", "valu… | 是 |
| 1276 | N | series_store.JP_CPI_TOKYO_YOY@2026-10 | 2.73 | 2.73 | 是 |
| 1277 | N | anchor_echo JP_CPI_TOKYO_YOY 键集 | ["anchor", "metric_id", "observation_month", "value"] | ["anchor", "metric_id", "observation_month", "valu… | 是 |
