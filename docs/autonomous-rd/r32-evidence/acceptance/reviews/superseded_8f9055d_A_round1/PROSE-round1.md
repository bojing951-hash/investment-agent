# Audit-R32 正式使用验收 · 工单 A · 第 1 轮 · 零上下文独立语义审计席复算记录

- 席位: semantic-audit-seat(Reviewer = independent-zero-context-seat-r32-a-round1)
- 审计日: 2026-11-24
- 受审运行: `/tmp/r32-accept/final5/output/research_runs/20261123T213303Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_日本在12个月前_3个月前和最`
- 裁决: **REVISE**(MAJOR 3 / MINOR 4 / NIT 4)
- 复算: **1111 点 / 8 处不一致**(去重后 6 处不同事实: 判断档 MAJOR 3、判断档 NIT 2、引擎面规则观察 1)

简称: SS = 冻结快照 `/tmp/r32-accept/final5/data/daily/research_snapshot_20261123.json` 的 series_store(`<指标>` 的 dates/values); CAL = 运行目录 `root_overlay/config/release_calendar.json`; AJ = `agent_judgment.json`; ENV = `AGENT_SEAT_ENVELOPE.json`; REP = `report.json`; MAP = `MAP_REPORT.md`; FULL = `FULL_REPORT.md`。

## 0. 受审对象、证据面与程序性披露

### 0.1 受审对象(全部只读)

- AJ 全文(sha256 `7a0434f091ad27d406bf21b1778790ba938ed1855e55d73ac364f3e0f4b52cc9`): l3(三条矛盾陈述 C1–C3、两条机制链 M1 四环/M2 两环)、l4(两情景)、reader_map(一句总判断、四地走位、传导两链、三转折与补选、三历史段)、quality_gate_notes 六条。
- 判断档文字在读者报告中的渲染: MAP(sha256 `80ccd9087febceb9d71ff7679608fbdb43e7e3c7f23fec0023f5e86853a0b5a2`,与旁挂 `MAP_REPORT.sha256` 一致)、FULL、`report.md`。

### 0.2 证据面(全部只读)

- SS: research_as_of 2026-11-23T22:53:47+08:00,92 条序列;facts 105 项;gate_a。
- CAL(与安装树冻结日历逐字相同,sha256 前缀 `e44fd2aa5ced0310`)、`metric_registry.json`。
- ENV 引擎面(turning_candidates_top9、point_anchors、us_rates_trio、asset_moves、dimension_gaps、policy_doc_facts 等);REP(research_plan 点值格、steps[61] 相似检索面、契约验证、Gate A、附件记录)。

### 0.3 渲染一致性

AJ 共 447 个字符串叶子,长度≥40 的 87 个: MAP 逐字渲染 59 个(一句总判断、四地走位、传导两链、三转折与补选、三历史段、情景 6/8);FULL 与 `report.md` 各逐字渲染 26 个(L3 三条矛盾陈述与两链全文、情景 8/8)。未入 MAP 的仅 L3 全文与质量注记(按版式归 FULL),未见改写或截断。三处 MAJOR 原句在 MAP 第 227、235、236 行逐字在场;「低 35 个基点」句另在 FULL 第 101 行、`report.md` 第 109 行在场。

读者报告处于裁决缺席态: MAP 第 8 行「独立语义审查待裁」、`report.md` 第 112 行「语义审查(席位待唤起)」,REP semantic_review.seat_invoked=false、verdict=null——与规程预期一致。

### 0.4 程序性披露

1. 为核对「决议时点前可见的通胀」与同步面两端取值,只读阅读了安装树 `scripts/research_map_planner.py` 的发布规则表(RELEASE_RULES)、地区×维度同步面函数(`history_region_sync_face`,约 358–511 行)与 `_aof_first_pub`(约 646–688 行);未修改、未运行该模块。席位在 s10_cells.py 中的可见性表先于该阅读按各指标发布节奏独立录入,两种做法结论一致。
2. 较早一次全树检索时,终端回显了 `tests/test_audit_r*.py` 的若干截断行(仅片段,未采用其中任何内容作为裁决依据);此后未再读取 tests/。
3. 受审文件在审计期间未变: 运行目录文件写于北京时间 06:40:04–06:40:21(REP 附件记录 attached_at=20261123T224004Z),席位于 06:43:37 取 AJ 副本,07:16 复核与现文件规范化后逐字相同(s23_drift.py)。07:14 一次读取瞬时返回 FileNotFound,重试正常,文件哈希与修改时间未变。
4. 本席未读取规程第 2 节所列任何目录,未联网,未运行任何写操作,未委派子代理。

## 1. 复算总表

| 编号 | 脚本 | 复算内容 | 点数 | 不一致 |
|---|---|---|---|---|
| A.1 | s10_cells.py | 三时点锚格: 观测日、值、发布日、同比、走位回贴行 | 320 | 0 |
| A.2 | s11_monthly.py | 月频同比路径、转折窗端点、低点月、地区走位数字 | 69 | 1 |
| A.3 | s12_policy.py | 政策利率序列、决议日与生效日、步进、中国利率 | 42 | 0 |
| A.4 | s13_rates_assets.py | 三利率分解、资产月窗、同日收盘对照、HY_OAS 分位、汇率与日频共动 | 125 | 3 |
| A.5 | s14_history.py | 历史段事后月末表(99 值)、相似度维度占比、地区×维度同步面、发布可见性 | 397 | 1 |
| A.6 | s15b_misc.py | Gate A 清单、证据引用计数、发布可见性、情景阈值、时区换算 | 122 | 0 |
| A.7 | s26_final.py | 三处候选偏离的独立复算与交付面(渲染、哈希、契约验证) | 32 | 3 |
| A.8 | s33_cov.py | 状态向量维度覆盖与候选月信用维缺失 | 4 | 0 |
| 合计 | | | **1111** | **8** |

逐点清单(出处键 / 直算值 / 报告值 / 一致与否)见附录 A;原始输出为同目录 `_out_s*.txt`,脚本均以 `/usr/bin/python3 -I <脚本> <路径参数>` 运行。

8 处不一致的构成: (A)「低 35 个基点」在 A.4 与 A.7 各记 1 次;(B)「此后连升」在 A.2 与 A.7 各记 1 次;(C)「候选面全体首位为中国制造业PMI」在 A.7 记 1 次;两处引用标签日期(CN_PPI_YOY@2026-10-31、CN_CPI_YOY@2026-10-31,序列观测日为 2026-10-01)在 A.4 记 2 次,属判断档质量注记④已披露的标签约定;A.5 的 1 处是引擎同步面对 2022-06 锚的 LPR 发布日取 2022-06-19(规则为月末减 11 天),实际发布日 2022-06-20(周一),该值前后均为 3.7、同步标签不受影响,且不在判断档文字内——仅作引擎面观察上报,不计入判断档偏离。

## 2. 规程第 3 节逐项结论

### ① 截止日

| 出处键 | 直算值 | 报告值(位置) | 结论 |
|---|---|---|---|
| SS.research_as_of | 2026-11-23T22:53:47+08:00 | 质量注记①同 | 一致 |
| SS.series_store 全部序列最晚观测日 | 2026-11-23 | 无晚于截止日的观测被引用 | 一致 |
| 截止时点换算(纽约/法兰克福/东京/上海) | 09:53 / 15:53 / 23:53 / 22:53 | 质量注记①同 | 一致(4 点) |
| CAL: 日本央行决议/生效/维持;FOMC 纪要发布 | 2026-09-18 / 2026-09-24 / 2026-10-30;2026-11-18 | 均不晚于截止日 | 一致 |
| SS.CPI: 2025-10 水平 | 缺席,2026-10 同比不可算 | AJ 未给出 2026-10 同比;SCN1 明写「待 2025-10 基期补齐后再核」 | 一致 |
| AJ /reader_map/history_periods 事后数字 | 99 个事后月末值全部复算一致,均标「事后」口径 | 事后结果≠预测 | 一致 |

未见以截止日之后的观测、发布、决议或生效日期作为当时可知证据;历史事后数字均以事后口径陈述。

### ② 点值锚格(A.1,320 点)

22 个点值格 × {观测日、值、发布日、同比、状态}及 63 行走位回贴(anchor_echo)全部与 SS 及 CAL 复算一致。例: ECB_DFR 十二个月前 2.0(观测 2025-06-11)/三个月前 2.25(2026-06-17)/最新 2.5(2026-09-16);CN_CPI_YOY 0.2(2025-10)/0.5(2026-07)/0.7(2026-10)。锚格非核心缺口 7 项与 Gate A 清单逐项相同(点值格缺数席位数见 A.1)。美国实际 GDP 与欧元区、日本 GDP 同比锚格取最新修订族,判断档已明示「事后回顾口径…未转述首发值」。

### ③ 同比(A.2,69 点)

| 出处键 | 直算值 | 报告值(位置) | 结论 |
|---|---|---|---|
| SS.CPI 同比 2026-05 / 07 / 08 / 09 | 4.17 / 3.30 / 3.35 / 3.72 | M1 环2、C1、TR1 同 | 一致 |
| SS.CPI 同比 2025-09 对 2026-09 | 3.0226 对 3.7173(走高) | C1「同比较一年前走高」 | 一致 |
| SS.CORE_PCE 同比 2026-05 / 07 / 09 | 3.16 / 3.00 / 3.12 | TR1 环1、SCN1 同 | 一致 |
| SS.CORE_CPI 同比 2026-02 / 05 | 2.47 / 2.82 | TR1 环1 同 | 一致 |
| SS.EA_HICP_YOY 2026-01 / 05 / 06 / 10 | 1.7 / 3.2 / 2.8 / 4.0 | MAP 走位、C1 同 | 一致 |
| SS.JP_CPI_YOY 2025-01 / 2026-02 / 2026-10 | 4.03 / 1.27 / 2.44 | turnings[2] 同 | 一致 |
| SS.CN_CPI_YOY 窗内最小 / 最大 | 0.2(2025-10)/ 1.3(2026-02) | 锚格与「一点零至一点三」 | 一致 |

同比均由当月观测与去年同月观测直算;缺基期处(美国 CPI 2026-10)判断档未给同比。

### ④ 政策面(A.3 42 点,A.6)

| 出处键 | 直算值 | 报告值(位置) | 结论 |
|---|---|---|---|
| SS.ECB_DFR 变动点 | 2025-06-11 2.0 → 2026-06-17 2.25 → 2026-09-16 2.5 | 「各+25个基点(2.0→2.5)」 | 一致 |
| SS.ECB_MRO 窗内净变动 | 2.15 → 2.65(+50bp) | 质量注记⑤「+50bp」 | 一致 |
| SS.DFF 2025-12-10 / 12-11 / 2026-09-16 / 09-17 | 3.89 / 3.64 / 3.63 / 3.88 | 「回补2025-12-11生效的降息」 | 一致 |
| SS.DFEDTARU 2025-12-11 / 2026-09-17 之后 | 3.75 / 4.00 | 走位「目标区间上限 4.0→3.75」及 9 月回补 | 一致 |
| SS.JP_POLICY_RATE 2025-11 / 2025-12 / 2026-10 | 0.478 / 0.557 / 1.227 | 「净+75…另一口径+67」 | 一致 |
| CAL 日本央行条目 | 决议 2026-09-18,生效 2026-09-24,目标 1.25;维持 2026-10-30 | 质量注记③所引一致 | 一致 |
| SS.JP_POLICY_TARGET;注册表 | 序列与注册表均无 | ENV dimension_gaps「数据不可得」,未以相邻口径冒充 | 一致 |
| SS.CN_LPR_1Y / CN_OMO_7D / CN_POLICY_OVERNIGHT | 3.0(最新 2026-11-20)/ 1.4(末观测 2026-10-30,滞后 24 天)/ 1.25(2026-11-02 起) | C3、走位、质量注记⑤ | 一致 |

### ⑤ 三利率分解与资产月窗(A.4,125 点)

| 出处键 | 直算值 | 报告值(位置) | 结论 |
|---|---|---|---|
| SS.UST_10Y/TIPS_10Y/BEI_10Y 2025-11-19→2026-11-19 | 名义 +91(4.13→5.04)= 实际 +102(1.86→2.88)+ 盈亏平衡 −11(2.27→2.16),残差 0 | M1 环3 | 一致 |
| 同上 2026-10-20→2026-11-19 | 名义 −8 = 实际 +11 + 盈亏平衡 −19 | rates_decomposition、C1 解释B | 一致 |
| SS.TIPS_10Y 2026-08-19→2026-11-19 | +53bp | M1 环4 | 一致 |
| 资产 1 月窗 2026-10-23→11-19/20/23 | SPX −5.51、SHCOMP −4.11、DAX +0.11、NIKKEI225 −9.98、VIX +38.87、DXY +2.23、GOLD_F −8.05、UST_10Y +0.8% | asset_returns_echo 8 行 | 一致(8 行逐位) |
| 同日收盘 2026-10-23→2026-11-20 | SPX −9.36、DAX −1.50、CAC40 +1.86、NIKKEI225 −9.98、VIX +84.52 | 质量注记①、TR1 环3 | 一致 |
| SS.HY_OAS | 3.52@2026-11-19;序列自 2023-11-21,n=786;高点 4.61@2025-04-07;不高于 3.52 者占 91.98% | 「约第 92 百分位」「低于…4.61」 | 一致 |
| SS.USDCNY 2025-11-19→2026-11-19 | 7.1075 → 6.6676(−6.19%) | C3 解释C | 一致 |
| SS.USDJPY 2026-10-23→2026-11-23 | 156.494 → 159.347(+1.82%) | 水平 159.35 | 一致 |
| SS.BEI_10Y 2020-11-30 / 2026-11-20 | 1.77 / 2.15,差 38bp;距阈值 1.8 为 35bp | 「低 35 个基点」 | **不一致(MAJOR-1)** |
| 证据引用标签日期 CN_PPI_YOY、CN_CPI_YOY | 序列观测日 2026-10-01 | 标签 2026-10-31 | 不一致(NIT-1,已披露) |

### ⑥ 转折判断与候选面(A.2、A.7)

| 出处键 | 直算值 | 报告值(位置) | 结论 |
|---|---|---|---|
| SS.CPI 2026-02 / 2026-05 | 2.434 / 4.1666 | turnings[0] | 一致 |
| SS.EA_HICP_YOY、CN_PPI_YOY 2026-02→05 | 1.9→3.2;−0.9→3.9 | turnings[0] | 一致 |
| SS.CPI、EA_HICP_YOY 窗内低点月 | 均为 2026-01 | turnings[0] | 一致 |
| SS.CN_PPI_YOY 窗内低点月 | 2025-11(−2.2) | turnings[0] | 一致 |
| SS.CN_PPI_YOY 低点后月度变动 | 2026-07 由 4.1 回落至 3.5 | 「此后连升」 | **不一致(MAJOR-2)** |
| SS.INDPRO 同比 2025-11 / 2026-02 / 2026-03 | 1.7543 / 0.7972 / 0.69 | turnings[1] | 一致 |
| SS.CN_PMI_MFG 同比% 2026-02→05 | −2.3904→1.0101,增量 3.4005 | turnings[1] | 一致 |
| ENV turning_candidates_top9 首行 | CN_PPI_YOY,增量 4.8(通胀维);CN_PMI_MFG 居第 2、增长维首位 | 「候选面全体首位为中国制造业PMI，增量3.40」 | **不一致(MAJOR-3)** |
| SS.JP_CPI_YOY 2025-11→2026-02;月末路径 | 2.9→1.27;2.9→2.13→1.51→1.27 | turnings[2] | 一致 |
| SS.JP_CPI_TOKYO_YOY 2026-06 / 09 | 1.6 / 2.69 | turning_supplement | 一致 |

MAP 第 241–252 行候选面表与 ENV 同序(中国 PPI 同比 4.8 居首,中国制造业 PMI 3.4005 次之),判断档 turnings[1] 的「全体首位」与引擎面及读者报告表格相左。

### ⑦ 传导链各环(A.2–A.4、A.6)

M1 环1: BRENT_F 月末 72.48(2026-02-27)→118.35(03-31)→92.05(05-29),首尾 +27.00%——一致。环2: 决议前按发布规则可见的美国 CPI 同比为 2026-04 的 3.78(规则发布 2026-05-13,周三)、2026-07 的 3.30(2026-08-13,周四)、2026-08 的 3.35(2026-09-13,周日,规则值);CORE_PCE 2026-07 的 3.00(08-30);HICP 2026-04 的 3.0(05-16)、2026-07 的 2.9(08-16);日本 CPI 2026-07 的 1.97(08-20);2026-08 HICP 于 2026-09-10 不可见、2026-09-16 可见——均一致。环3、环4 数字见⑤。M2 环1 月度步进 +8/+17/+11/+14/+7/+18(2025-12、2026-01、2026-06、2026-07、2026-09、2026-10)与序列一致;M2 环2 以「无 JGB 历史序列」标为整环假设,与 SS(无 JGB 序列,仅 2026-11-19 单点 facts 三项)一致。

证据级标注与各环证据相称: M1 环1、环3 与 M2 环1 标 E1 且数字均可回贴;M1 环2 的动机、M1 环4 的因果传导与 M2 环2 整环均以【假设】措辞出现,未以事实位措辞出现。

### ⑧ 历史类比(A.5、A.8)

- 距离与分位: 2025-03 为 0.7272(0.0%)、2022-06 为 0.7918(1.37%)、2023-10 为 1.0542(30.14%),与 REP steps[61] 及判断档一致。
- 维度占比: 2022-06 利率 51.9 / 估值 33.6 / 通胀 11.4 / 波动 3.0 / 增长 0.0;2023-10 波动 60.1 / 估值 21.2 / 利率 11.0 / 通胀 7.7;2025-03 波动 42.1 + 利率 40.7——一致。
- 事后月末表 3 段 × 3/6/12 月 × 11 指标共 99 值全部一致;引擎事后块(锚月后首观测)另行核对,两口径差异均如实分列。
- 同步面: 「九格中三格 / 五格 / 一格同步」与引擎地区×维度同步面及席位复算(3 / 5 / 1)一致,无「叙述称同步而面为缺证」或叙述与面冲突。
- 状态向量覆盖 growth 0.1667 / inflation 0.3333 / credit 0.5 等于引擎面 coverage 值;前五候选月信用维特征(HY_OAS_level、HY_IG_gap_level)均缺席,「信用维在多数候选月缺席」成立。说明: 引擎 coverage 的分母含计划内未到场特征,席位只能核对引用值等于引擎面值,未能脱离引擎独立重建该比值。

### ⑨ 情景(A.6)

- SCN1 触发(美国 2026-11 或 2026-12 月 CPI 同比≥3.5,或欧央行/美联储再加息)与失效(CPI 同比<2.5 且 CORE_PCE 同比<2.8 持续两月): 最新 CPI 同比 3.72(2026-09)、CORE_PCE 同比 3.12(2026-09),失效未触发。
- SCN2 失效(BEI_10Y 跌破 1.8 且继续下行): 最新 2.15@2026-11-20,未触发;阈值依据句算术有误(MAJOR-1)。
- 所需区分指标 CPI、CORE_PCE、BEI_10Y、DFEDTARU、ECB_DFR 均在 SS 在场;期限均为 2027-02-28;两情景均标「假设非预测」。
- 资产方向的历史对照: 2022-06 段三个月窗 SPX −5.28%、GOLD_F −7.49%、DXY +7.10%,十二个月窗 SPX +17.57%;2025-03 段十二个月窗 GOLD_F +48.83%、DXY −4.08%、SPX +16.33%——全部复算一致;2025-03 段「样本非独立」已披露。
- 两情景方向互补: SCN1(收紧延续)为股指承压、GOLD_F 受压、DXY 偏强,SCN2(一次性通胀)为股指修复、GOLD_F 走强、DXY 转弱;两情景的触发条件均待验证(未被截止日读数触发或证伪),无已证伪前提充当待验证情景。

### ⑩ 总判断、走位与对质表

- 一句总判断: 末尾明写「(描述,非预测)」;句内数字(名义 +91 / 实际 +102 / 盈亏平衡 −11、SPX −5.51%、VIX +38.87%、DFF 回到 3.88 等)全部复算一致,盘中快照已标注。
- 走位: 63 行 anchor_echo 的值与观测月与点值格逐位一致;正文月份均在引擎面月份集内。
- 对质表(传导链逐环): TR1 环1「支持主解释」——BRENT_F 同窗 +27.00%,与竞争解释的「大体平稳」相左,成立;TR1 环2「尚不能区分」——BEI_10Y 收紧前 2.25→2.50、收紧后区间 2.15–2.40,窗口内方向前后相反,成立;TR1 环3「尚不能区分」——实际利率 +11bp 合主解释、盈亏平衡 −19bp 合竞争解释,成立;TR2 环1「支持竞争解释」——收缩窗内 SPX −5.51% 而 USDJPY +1.82%,未见「日元走强同现」,成立;但该环观察事实只列水平,未写明窗内方向,日频同向 16/21 日亦未披露(MINOR-3)。

### ⑪ 诚实缺席项

Gate A 核心缺口 0、非核心缺口 7(BUND_10Y、BUND_2Y、CN_OMO_7D、CN_POLICY_OVERNIGHT、EA_REAL_GDP_YOY、JP_CPI_TOKYO_YOY、JP_REAL_GDP_YOY)、非核心降级 8,清单与判断档质量注记④逐项相同;JP_POLICY_TARGET 序列与注册表均缺席,日本央行目标取自冻结日历并注明来源;JGB 无历史序列(单点)如实标为不可验证;CN_OMO_7D 过期(滞后 24 天)如实披露;M2 环2 整环假设。未见以相邻口径冒充。

### ⑫ 截止日当日日频观测标注

C1 水平清单中标注为 2026-11-23 盘中快照的仅 VIX(27.01)与 USDJPY(159.347),与「其中 VIX 与 USDJPY 为 2026-11-23 盘中快照」逐项相符;其余水平日期(UST_10Y、TIPS_10Y、HY_OAS 为 11-19,BEI_10Y 为 11-20,DFF 为 11-19)与序列一致。质量注记①与 TR1 环3 对 SPX、DAX、CAC40、VIX、GOLD_F、DXY、BRENT_F 与外汇的当日值标注盘中,NIKKEI225 止于 11-20、SHCOMP 为 11-23 收盘,与序列末观测日一致。

### ⑬ 契约验证中非 VERIFIED 项

REP 契约验证 14 条判定、16 条六查、地图核对各条均为 VERIFIED,无非 VERIFIED 项;语义审查席位未唤起(seat_invoked=false,verdict=null),属裁决缺席态。

### ⑭ 交付门缺口

Gate A=DEGRADED 已在质量注记④披露,缺口与降级清单逐项一致;缺口对结论的影响(JGB 单点、日本政策目标无序列、中国逆回购过期)均有披露。未见把序列值写成官方宣布目标(日本官方目标 1.25 取自冻结日历,月均 1.227 另标为无担保隔夜拆借月均);无晚于截止日的待生效决定。「7天逆回购利率窗内无变动」处的观测止点披露可改进,记 MINOR-4。

### (map) 三时点对照与工单五面相称性

三时点锚为 2025-11-23 / 2026-08-23 / 2026-11-23,点值格 22 个、缺数格 0;四地(US、CN、EA、JP)走位齐备。工单五面均在: 一句总判断(529 字)、各地区环境走位(4 地)、传导图逐环四件套(TR1 三环、TR2 一环,各含观察事实 / 因果假设 / 竞争解释 / 区分指标,并填主/竞争预期与裁定)、三个转折(3 项,另补选 1 项)与历史段(3 段,含相似点、关键差异、同步面、3/6/12 月事后与样本注记);另有 rates_decomposition 与 asset_returns_echo 8 行回贴。三转折为不同指标-月且跨两维度(通胀 2 项、增长 1 项,指标与月份各异),无重复计事件。

## 3. 规程第 4 节: 六查与反方攻击

### 3.1 C1 主线综合(通胀再加速→政策再收紧→实际利率上行→风险资产收缩;三种解释不可裁决)

- 证据相关性: 相关。C1 所列 11 个水平值全部回贴 SS(A.4)。
- 支持度: 共动格局成立——名义 +91 = 实际 +102 + 盈亏平衡 −11;ECB_DFR 两度 +25bp、DFF 回补降息;近月 SPX −5.51%、NIKKEI225 −9.98%、GOLD_F −8.05% 对 DXY +2.23%、VIX +38.87%。「谁驱动谁」未裁决,与证据相称。
- 竞争解释: A 主链 / B 增长担忧 / C 跨边境溢出与技术面,各带区分指标预期(BEI_10Y 与 TIPS_10Y 分解走向;USDJPY 耦合与 HY_OAS)。
- 反对证据: 判断自述 12 个月窗实际利率 +102bp 与 SPX +8.03%、NIKKEI225 +22.47%、DAX +9.93% 同向上行;决议前可见通胀低于 2026-05 高点;BEI_10Y 十二月回落 11bp。
- 结论是否超出证据: 未超出,条件式表述。
- 证伪条件可观测性: BEI_10Y、TIPS_10Y、HY_OAS、USDJPY 均在场;两解释预言方向不同(B: BEI 主导下行且 TIPS 转平;A: BEI 大体稳定且 TIPS 续升;C: USDJPY 与风险资产紧耦合)。
- 反方攻击 1: 「以近月资产收缩补全链条,而全年窗股指上涨,第四腿与全年证据相左」→ 判断在句内明示资产收缩属近月窗口事实、全年窗股指并未下行,并在 M1 环4 列两窗对照;攻击被披露吸收,不构成隐瞒。
- 反方攻击 2: 「解释B 预言 TIPS 转平或回落,而近 1 个月实际利率 +11bp」→ 成立: C1 解释B 末句「与该解释相容」只对盈亏平衡一腿成立,记 MINOR-1。
- 反方攻击 3: 「DFF 回到降息前水平只对 2025-12 降息成立(2025-10-30 降息前 DFF 为 4.12)」→ 十二个月窗内唯一降息为 2025-12,窗内口径成立;一句总判断已写明「回补此前降息(回到3.88)」,记 NIT-2。

### 3.2 C2 历史相似段的证据冲突

- 证据相关性: 相关。三候选即引擎相似检索面前三(距离 0.7272 / 0.7918 / 1.0542)。
- 支持度: 事后路径分歧的 99 个值与符号一致率均复算一致。
- 竞争解释: A 各段独有政策与冲击环境(标假设);B 相似度量低维覆盖(growth 0.17 / inflation 0.33 / credit 0.5,候选月信用维缺失)。
- 反对证据: 分歧本身即反对「相似即同路径」;判断据此只作结构对照。
- 结论是否超出证据: 未超出,「相似≠因果≠预测」。
- 证伪条件可观测性: 本陈述不带独立证伪阈值,其下游两情景给出可观测阈值(CPI、CORE_PCE、BEI_10Y),均在场。
- 反方攻击 4: 「2025-03 段的事后窗与本轮早段重叠,以其为相似证据等于把本轮自身当证据」→ 判断在 sample_note 与 SCN2 明示「样本非独立」,攻击被披露吸收。

### 3.3 C3 中国政策与美欧日方向背离未定案

- 证据相关性: 相关。CN_PPI_YOY −2.2(2025-11)→5.7(2026-10),摆动 7.9pp 为所列价格指标最大;CN_LPR_1Y 3.0、CN_OMO_7D 1.4 窗内无变动;CN_POLICY_OVERNIGHT 1.25 自 2026-11-02 起;USDCNY −6.19%。
- 支持度: 背离事实成立。
- 竞争解释: A 输入型/供给驱动;B 内需不足制约;C 汇率/资本流动(无资本流动序列,标【尚未验证】;汇率腿不支持贬值压力读法)。
- 反对证据: CN_CPI_YOY 仅 0.7、CN_PMI_MFG 49.3,内需与增长侧偏弱。
- 结论是否超出证据: 未超出,三种解释不可区分如实标注。
- 证伪条件可观测性: 解释C 在引擎面不可检验并已标注;A 与 B 对现有读数同向容纳,预言方向未分立,判断未强裁。
- 反方攻击 5: 「换锚(7 天 1.4 → 隔夜 1.25)本身是政策动作,『窗内持平』掩盖了换锚」→ 判断在 C3、TR1 环2 与质量注记⑤披露换锚、新锚自首观测起持平且原工具无新观测;「未跟进加息」在两种口径下均成立,攻击不成立。

### 3.4 M1 机制链(四环)

- 环1 冲击环【事实/E1】: 美国 CPI 2.434→4.1666、HICP 1.9→3.2、中国 PPI −0.9→3.9、核心 CPI 2.47→2.82、BRENT_F 月末 +27.00%——一致;相关且支持。
- 环2 政策环【时序为事实,动机为假设/E3】: 决议日、生效日、幅度与决议前可见通胀(见⑦)一致;动机归因标 E3,并自述决议前可见通胀低于高点(反对证据在场)。
- 环3 利率环【事实/E1】: 分解与恒等残差为 0——一致。
- 环4 资产环【E2,缺环为假设】: 近月资产数字一致;12 个月窗反例(实际利率与股指同向上行)已披露;证伪观察 HY_OAS 升破 4.61 可观测但在场。
- 竞争解释与证伪可观测性: 逐环竞争解释见 TR1;区分指标 BRENT_F、BEI_10Y、HY_OAS 在场,两侧预期方向不同。
- 反方攻击 6: 「收紧发生在通胀见顶(2026-05)之后,『通胀迫使收紧』的时序支持弱」→ 判断在环2 自述动机环证据减弱并标假设,攻击被披露吸收。
- 反方攻击 7: 「证伪阈值 4.61 为序列历史高点,距最新 3.52 达 109bp,几乎不可能被触发,等于不可证伪」→ 阈值在证据面可观测,不构成 MAJOR;但作为区分指标过松,记 MINOR-2。

### 3.5 M2 机制链(两环)

- 环1【事实/E1】: JP_POLICY_RATE 0.478→1.227(+75bp)及六个步进月与序列一致;相关且支持。
- 环2【E3 整环假设】: 无 JGB 历史序列,整环不可验证并已标注;证伪指标 USDJPY 在场,两侧预期方向不同(同现 vs 解耦)。
- 反方攻击 8: 「日本月均利率自 2025-12 已上调,早于美欧通胀共振(2026-02),更像独立正常化进程」→ 判断在 TR1 环2 作为竞争解释写明,攻击被披露吸收。

### 3.6 传导对质表复核

TR1 环1「支持主解释」、环2 与环3「尚不能区分」、TR2 环1「支持竞争解释」四项裁定均与席位对各自区分指标的复算方向相符(见⑩)。TR2 环1 的裁定所依据的窗内方向(SPX −5.51% 对 USDJPY +1.82%)未写入该环观察事实,记 MINOR-3。

## 4. 问题清单

### MAJOR(3)

**MAJOR-1 数字错(算术)** — AJ `/l4/scenarios[1]/rows/falsification/threshold`(SCN2 失效阈值依据句);MAP 第 227 行;FULL 第 101 行;`report.md` 第 109 行。
原句: 「较最新读数 2.15(2026-11-20)低 35 个基点」
问题: SS.BEI_10Y@2020-11-30 = 1.77、@2026-11-20 = 2.15,差为 38bp;35bp 是最新读数距阈值 1.8 的距离,句中把两个距离混用。
改句: 「较最新读数 2.15(2026-11-20)低 38 个基点(该读数较阈值 1.8 高 35 个基点)」

**MAJOR-2 方向与证据相左** — AJ `/reader_map/turnings[0]/first_mover`;MAP 第 235 行。
原句: 「中国 PPI 低点在 2025-11 且此后连升」
问题: SS.CN_PPI_YOY 低点后的月度路径为 −1.9、−1.4、−0.9、0.5、2.8、3.9、4.1、3.5、3.8、5.0、5.7(2025-12 至 2026-10),2026-07 由 4.1 回落至 3.5,并非连升;判断档 TR1 环1 已写「中国PPI 2026-07回落至 3.5 后升至 5.7@2026-10」,与该句自相矛盾。低点月(2025-11)本身正确,转折结论不变。
改句: 「中国 PPI 低点在 2025-11，此后总体上行(至 2026-10 的 5.7；其间仅 2026-07 由 4.1 回落至 3.5)」

**MAJOR-3 与引擎面相左(排序陈述)** — AJ `/reader_map/turnings[1]/first_mover`;MAP 第 236 行。
原句: 「(候选面全体首位为中国制造业PMI，增量3.40)」
问题: ENV `/reader_map_contract/engine_faces/turning_candidates_top9` 首行为 CN_PPI_YOY(2026-02→2026-05,−0.9→3.9,增量 4.8,通胀维);CN_PMI_MFG 增量 3.4005 居全体第 2、增长维首位;MAP 第 241–252 行候选面表同序。两行增量均由 SS 直算相符。
改句: 「(中国制造业PMI居增长维候选面首位，增量3.40；候选面全体首位为中国PPI同比，增量4.8)」

三条均有证据面数字可成立的改句,不属「证据不足」。

### MINOR(4,不构成阻断,如实列出)

- MINOR-1 — AJ `/l3/contradictions[0]/competing_explanations[1]`;FULL 第 69 行;`report.md` 第 76 行: 「近1个月分解(实际+11bp、盈亏平衡-19bp)与该解释相容」。解释B 的预期是「BEI_10Y 主导性下行而 TIPS_10Y 转平或回落」,实际利率 +11bp 与后一腿相左,仅盈亏平衡一腿相容;与 TR1 环3 的「尚不能区分」不一致。建议改为「…与该解释的盈亏平衡一腿相容、与实际利率一腿相左,整体仅部分相容」。
- MINOR-2 — AJ `/l3/mechanism_chains[0]/links[3]`(证伪观察)与 `/reader_map/transmission[0]/links[2]`: 证伪阈值为 HY_OAS 升破序列高点 4.61,距最新 3.52 达 109bp,可观测但过松。建议增设预警级(如升破 2025-05-09 的 3.53,即库内上一次不低于最新读数的水平),失效级保留 4.61。
- MINOR-3 — AJ `/reader_map/transmission[1]/links[0]/observed_fact`: 该环观察事实只列 JP_POLICY_RATE 步进与 USDJPY 水平,未写明裁定「支持竞争解释」所依据的窗内方向(2026-10-23→2026-11-23 SPX −5.51% 对 USDJPY +1.82%);日频对数收益相关 0.19、同向 16/21 日、SPX 下跌 12 日中 USDJPY 下跌 9 日(四个最大跌幅日 USDJPY 变动为 −0.07%、+0.20%、−0.08%、−0.06%)亦未披露。建议在观察事实中补写窗内方向与日频共动两句。
- MINOR-4 — AJ `/reader_map/headline_conclusion` 与 `/l3/contradictions[2]/statement`: 「7天逆回购利率与LPR窗内无变动」「CN_LPR_1Y 与 7天逆回购利率窗内持平」未带观测止点。SS.CN_OMO_7D 末观测为 2026-10-30(其后至截止日无观测,滞后 24 天),SS.ECB_MRO / ECB_DFR 末观测为 2026-09-16(距截止日 68 天)。质量注记④⑤与四地走位已披露过期与降级,「未跟进加息」另有新锚 CN_POLICY_OVERNIGHT 1.25 自 2026-11-02 至 2026-11-23 的逐日观测支持,结论不变;建议在一句总判断与 C3 的「无变动/持平」处括注「(7天逆回购末观测 2026-10-30,其后缺观测)」,避免把缺席读成无变化。

### NIT(4)

- NIT-1 — AJ `/l3/contradictions[0]/evidence_refs`、`/l3/contradictions[2]/evidence_refs`、`/l3/mechanism_chains[0]/links[0]/evidence_refs`: 引用标签 `CN_PPI_YOY@2026-10-31`、`CN_CPI_YOY@2026-10-31` 的日期为观测月末,序列观测日为 2026-10-01;质量注记④已披露,属标签约定,建议统一为序列观测日。
- NIT-2 — AJ `/l3/contradictions[0]/statement`: 「DFF 回到降息前水平」宜写明「回到 2025-12 降息前水平(3.88)」;2025-10-30 降息前 DFF 为 4.12(2025-10-29),窗外但读者易混。
- NIT-3 — AJ `/l3/mechanism_chains[0]/links[3]/text`: 「SPX 8.03、NIKKEI225 22.47、DAX 9.93」缺百分号;HY_OAS 水平单位写作「3.52pp」(利差常以 % 或基点计)。
- NIT-4 — AJ `/l4/scenarios[0]`(SCN1)与 M2 环1: 冻结日历另有日本央行 2026-10-30 维持决议(目标 1.25)条目,判断档仅引 2026-09-18 决议;「日央行维持收紧倾向」可补引该条目。

### 引擎面观察(非判断档问题,供操作者登记)

- EO-1 — REP 相似检索同步面(MAP 第 455–472 行)对 2022-06 锚的中国政策格发布日取 2022-06-19(规则: 月末减 11 天),而 LPR 实际发布日为 2022-06-20(周一);该观测前后值均为 3.7,同步标签不受影响。规则在 6 月等 30 天月份会把 20 日的发布提前一天。

## 5. 裁决

存在 3 条 MAJOR(数字错 1、方向与证据相左 1、与引擎面相左 1),按规程第 5 节判 **REVISE**。三条必修均有证据面数字可成立的改句;其余 1111 点中未见截止日违规、缺基期给同比、相邻口径冒充、事后信息冒充当时可知或证伪条件不可观测。MINOR 4 条与 NIT 4 条不构成阻断,如实列出。修订后建议复核点: MAJOR-1 至 3 的改句落地(含 MAP、FULL、`report.md` 三处渲染)、MINOR-1 与 TR1 环3 表述一致、MINOR-3 观察事实补写后的裁定是否仍为「支持竞争解释」(按席位复算应不变)。

## 附录 A · 逐点复算清单(逐点: 出处键 / 直算值 / 报告值 / 一致与否)

### A.1 s10_cells.py — 出处键: 快照 series_store.<metric> dates/values + 冻结日历 root_overlay/config/release_calendar.json + report.json /research_plan 点值格 + agent_judgment.json /reader_map/regions[*] 走位与锚格叙述(席位自拟发布可见性表,独立于引擎规划器)

```text
     obs_date                         mine=2025-04-01                   claim=2025-04-01                   OK
     value                            mine=23884.563                    claim=23884.563                    OK
     pub_date                         mine=2025-07-29                   claim=2025-07-29                   OK
     echo.value                       mine=23884.563                    claim=23884.563                    OK
     echo.obs_month                   mine=2025-04                      claim=2025-04                      OK
     yoy_pct(derived)                 mine=2.42                         claim=2.42                         OK
     obs_date                         mine=2026-04-01                   claim=2026-04-01                   OK
     value                            mine=24408.011                    claim=24408.011                    OK
     pub_date                         mine=2026-07-29                   claim=2026-07-29                   OK
     echo.value                       mine=24408.011                    claim=24408.011                    OK
     echo.obs_month                   mine=2026-04                      claim=2026-04                      OK
     yoy_pct(derived)                 mine=2.19                         claim=2.19                         OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=24611.077                    claim=24611.077                    OK
     pub_date                         mine=2026-10-29                   claim=2026-10-29                   OK
     echo.value                       mine=24611.077                    claim=24611.077                    OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     yoy_pct(derived)                 mine=2.07                         claim=2.07                         OK
     obs_date                         mine=2025-09-01                   claim=2025-09-01                   OK
     value                            mine=4.4                          claim=4.4                          OK
     pub_date                         mine=2025-11-20                   claim=2025-11-20                   OK
     echo.value                       mine=4.4                          claim=4.4                          OK
     echo.obs_month                   mine=2025-09                      claim=2025-09                      OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=4.1                          claim=4.1                          OK
     pub_date                         mine=2026-08-05                   claim=2026-08-05                   OK
     echo.value                       mine=4.1                          claim=4.1                          OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     obs_date                         mine=2026-10-01                   claim=2026-10-01                   OK
     value                            mine=4.1                          claim=4.1                          OK
     pub_date                         mine=2026-11-05                   claim=2026-11-05                   OK
     echo.value                       mine=4.1                          claim=4.1                          OK
     echo.obs_month                   mine=2026-10                      claim=2026-10                      OK
     obs_date                         mine=2025-08-01                   claim=2025-08-01                   OK
     value                            mine=101.6247                     claim=101.6247                     OK
     pub_date                         mine=2025-09-15                   claim=2025-09-15                   OK
     echo.value                       mine=101.6247                     claim=101.6247                     OK
     echo.obs_month                   mine=2025-08                      claim=2025-08                      OK
     yoy_pct(derived)                 mine=1.19                         claim=1.19                         OK
     yoy_status                       mine=ok                           claim=ok                           OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=103.1675                     claim=103.1675                     OK
     pub_date                         mine=2026-08-15                   claim=2026-08-15                   OK
     echo.value                       mine=103.1675                     claim=103.1675                     OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     yoy_pct(derived)                 mine=1.25                         claim=1.25                         OK
     yoy_status                       mine=ok                           claim=ok                           OK
     obs_date                         mine=2026-10-01                   claim=2026-10-01                   OK
     value                            mine=103.3954                     claim=103.3954                     OK
     pub_date                         mine=2026-11-15                   claim=2026-11-15                   OK
     echo.value                       mine=103.3954                     claim=103.3954                     OK
     echo.obs_month                   mine=2026-10                      claim=2026-10                      OK
     yoy_pct(derived)                 mine=2.15                         claim=2.15                         OK
     yoy_status                       mine=ok                           claim=ok                           OK
     obs_date                         mine=2025-09-01                   claim=2025-09-01                   OK
     value                            mine=324.245                      claim=324.245                      OK
     pub_date                         mine=2025-10-24                   claim=2025-10-24                   OK
     echo.value                       mine=324.245                      claim=324.245                      OK
     echo.obs_month                   mine=2025-09                      claim=2025-09                      OK
     yoy_pct(derived)                 mine=3.02                         claim=3.02                         OK
     yoy_status                       mine=ok                           claim=ok                           OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=332.813                      claim=332.813                      OK
     pub_date                         mine=2026-08-13                   claim=2026-08-13                   OK
     echo.value                       mine=332.813                      claim=332.813                      OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     yoy_pct(derived)                 mine=3.3                          claim=3.3                          OK
     yoy_status                       mine=ok                           claim=ok                           OK
     obs_date                         mine=2026-10-01                   claim=2026-10-01                   OK
     value                            mine=337.476                      claim=337.476                      OK
     pub_date                         mine=2026-11-13                   claim=2026-11-13                   OK
     echo.value                       mine=337.476                      claim=337.476                      OK
     echo.obs_month                   mine=2026-10                      claim=2026-10                      OK
     yoy_pct(derived)                 mine=None                         claim=None                         OK
     yoy_status                       mine=no_base                      claim=no_base                      OK
     obs_date                         mine=2025-09-01                   claim=2025-09-01                   OK
     value                            mine=330.418                      claim=330.418                      OK
     pub_date                         mine=2025-10-24                   claim=2025-10-24                   OK
     echo.value                       mine=330.418                      claim=330.418                      OK
     echo.obs_month                   mine=2025-09                      claim=2025-09                      OK
     yoy_pct(derived)                 mine=3.02                         claim=3.02                         OK
     yoy_status                       mine=ok                           claim=ok                           OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=336.789                      claim=336.789                      OK
     pub_date                         mine=2026-08-13                   claim=2026-08-13                   OK
     echo.value                       mine=336.789                      claim=336.789                      OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     yoy_pct(derived)                 mine=2.47                         claim=2.47                         OK
     yoy_status                       mine=ok                           claim=ok                           OK
     obs_date                         mine=2026-10-01                   claim=2026-10-01                   OK
     value                            mine=339.9                        claim=339.9                        OK
     pub_date                         mine=2026-11-13                   claim=2026-11-13                   OK
     echo.value                       mine=339.9                        claim=339.9                        OK
     echo.obs_month                   mine=2026-10                      claim=2026-10                      OK
     yoy_pct(derived)                 mine=None                         claim=None                         OK
     yoy_status                       mine=no_base                      claim=no_base                      OK
     obs_date                         mine=2025-08-01                   claim=2025-08-01                   OK
     value                            mine=126.646                      claim=126.646                      OK
     pub_date                         mine=2025-09-30                   claim=2025-09-30                   OK
     echo.value                       mine=126.646                      claim=126.646                      OK
     echo.obs_month                   mine=2025-08                      claim=2025-08                      OK
     yoy_pct(derived)                 mine=2.85                         claim=2.85                         OK
     yoy_status                       mine=ok                           claim=ok                           OK
     obs_date                         mine=2026-06-01                   claim=2026-06-01                   OK
     value                            mine=129.969                      claim=129.969                      OK
     pub_date                         mine=2026-07-30                   claim=2026-07-30                   OK
     echo.value                       mine=129.969                      claim=129.969                      OK
     echo.obs_month                   mine=2026-06                      claim=2026-06                      OK
     yoy_pct(derived)                 mine=3.04                         claim=3.04                         OK
     yoy_status                       mine=ok                           claim=ok                           OK
     obs_date                         mine=2026-09-01                   claim=2026-09-01                   OK
     value                            mine=130.902                      claim=130.902                      OK
     pub_date                         mine=2026-10-30                   claim=2026-10-30                   OK
     echo.value                       mine=130.902                      claim=130.902                      OK
     echo.obs_month                   mine=2026-09                      claim=2026-09                      OK
     yoy_pct(derived)                 mine=3.12                         claim=3.12                         OK
     yoy_status                       mine=ok                           claim=ok                           OK
     obs_date                         mine=2025-11-23                   claim=2025-11-23                   OK
     value                            mine=4.0                          claim=4.0                          OK
     echo.value                       mine=4.0                          claim=4.0                          OK
     echo.obs_month                   mine=2025-11                      claim=2025-11                      OK
     obs_date                         mine=2026-08-23                   claim=2026-08-23                   OK
     value                            mine=3.75                         claim=3.75                         OK
     echo.value                       mine=3.75                         claim=3.75                         OK
     echo.obs_month                   mine=2026-08                      claim=2026-08                      OK
     obs_date                         mine=2026-11-23                   claim=2026-11-23                   OK
     value                            mine=4.0                          claim=4.0                          OK
     echo.value                       mine=4.0                          claim=4.0                          OK
     echo.obs_month                   mine=2026-11                      claim=2026-11                      OK
   -> OK (engine used previous published obs ('2025-11-22', 3.88))
   -> OK (engine used previous published obs ('2026-08-22', 3.63))
     obs_date                         mine=2026-11-19                   claim=2026-11-19                   OK
     value                            mine=3.88                         claim=3.88                         OK
     echo.value                       mine=3.88                         claim=3.88                         OK
     echo.obs_month                   mine=2026-11                      claim=2026-11                      OK
     obs_date                         mine=2025-10-01                   claim=2025-10-01                   OK
     value                            mine=49.0                         claim=49.0                         OK
     pub_date                         mine=2025-10-30                   claim=2025-10-30                   OK
     echo.value                       mine=49.0                         claim=49.0                         OK
     echo.obs_month                   mine=2025-10                      claim=2025-10                      OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=49.2                         claim=49.2                         OK
     pub_date                         mine=2026-07-30                   claim=2026-07-30                   OK
     echo.value                       mine=49.2                         claim=49.2                         OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     obs_date                         mine=2026-10-01                   claim=2026-10-01                   OK
     value                            mine=49.3                         claim=49.3                         OK
     pub_date                         mine=2026-10-30                   claim=2026-10-30                   OK
     echo.value                       mine=49.3                         claim=49.3                         OK
     echo.obs_month                   mine=2026-10                      claim=2026-10                      OK
     obs_date                         mine=2025-10-01                   claim=2025-10-01                   OK
     value                            mine=0.2                          claim=0.2                          OK
     pub_date                         mine=2025-11-09                   claim=2025-11-09                   OK
     echo.value                       mine=0.2                          claim=0.2                          OK
     echo.obs_month                   mine=2025-10                      claim=2025-10                      OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=0.5                          claim=0.5                          OK
     pub_date                         mine=2026-08-09                   claim=2026-08-09                   OK
     echo.value                       mine=0.5                          claim=0.5                          OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     obs_date                         mine=2026-10-01                   claim=2026-10-01                   OK
     value                            mine=0.7                          claim=0.7                          OK
     pub_date                         mine=2026-11-09                   claim=2026-11-09                   OK
     echo.value                       mine=0.7                          claim=0.7                          OK
     echo.obs_month                   mine=2026-10                      claim=2026-10                      OK
     obs_date                         mine=2025-10-01                   claim=2025-10-01                   OK
     value                            mine=-2.1                         claim=-2.1                         OK
     pub_date                         mine=2025-11-09                   claim=2025-11-09                   OK
     echo.value                       mine=-2.1                         claim=-2.1                         OK
     echo.obs_month                   mine=2025-10                      claim=2025-10                      OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=3.5                          claim=3.5                          OK
     pub_date                         mine=2026-08-09                   claim=2026-08-09                   OK
     echo.value                       mine=3.5                          claim=3.5                          OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     obs_date                         mine=2026-10-01                   claim=2026-10-01                   OK
     value                            mine=5.7                          claim=5.7                          OK
     pub_date                         mine=2026-11-09                   claim=2026-11-09                   OK
     echo.value                       mine=5.7                          claim=5.7                          OK
     echo.obs_month                   mine=2026-10                      claim=2026-10                      OK
   -> consistent (series has no obs on/before anchor)
   -> consistent (series has no obs on/before anchor)
     obs_date                         mine=2026-11-23                   claim=2026-11-23                   OK
     value                            mine=1.25                         claim=1.25                         OK
     echo.value                       mine=1.25                         claim=1.25                         OK
     echo.obs_month                   mine=2026-11                      claim=2026-11                      OK
     obs_date                         mine=2025-11-14                   claim=2025-11-14                   OK
     value                            mine=1.4                          claim=1.4                          OK
     echo.value                       mine=1.4                          claim=1.4                          OK
     echo.obs_month                   mine=2025-11                      claim=2025-11                      OK
     obs_date                         mine=2026-08-21                   claim=2026-08-21                   OK
     value                            mine=1.4                          claim=1.4                          OK
     echo.value                       mine=1.4                          claim=1.4                          OK
     echo.obs_month                   mine=2026-08                      claim=2026-08                      OK
     obs_date                         mine=2026-10-30                   claim=2026-10-30                   OK
     value                            mine=1.4                          claim=1.4                          OK
     echo.value                       mine=1.4                          claim=1.4                          OK
     echo.obs_month                   mine=2026-10                      claim=2026-10                      OK
     obs_date                         mine=2025-11-20                   claim=2025-11-20                   OK
     value                            mine=3.0                          claim=3.0                          OK
     echo.value                       mine=3.0                          claim=3.0                          OK
     echo.obs_month                   mine=2025-11                      claim=2025-11                      OK
     obs_date                         mine=2026-08-20                   claim=2026-08-20                   OK
     value                            mine=3.0                          claim=3.0                          OK
     echo.value                       mine=3.0                          claim=3.0                          OK
     echo.obs_month                   mine=2026-08                      claim=2026-08                      OK
     obs_date                         mine=2026-11-20                   claim=2026-11-20                   OK
     value                            mine=3.0                          claim=3.0                          OK
     echo.value                       mine=3.0                          claim=3.0                          OK
     echo.obs_month                   mine=2026-11                      claim=2026-11                      OK
     obs_date                         mine=2025-07-01                   claim=2025-07-01                   OK
     value                            mine=1.11                         claim=1.11                         OK
     pub_date                         mine=2025-11-04                   claim=2025-11-04                   OK
     echo.value                       mine=1.11                         claim=1.11                         OK
     echo.obs_month                   mine=2025-07                      claim=2025-07                      OK
     obs_date                         mine=2026-04-01                   claim=2026-04-01                   OK
     value                            mine=1.19                         claim=1.19                         OK
     pub_date                         mine=2026-08-04                   claim=2026-08-04                   OK
     echo.value                       mine=1.19                         claim=1.19                         OK
     echo.obs_month                   mine=2026-04                      claim=2026-04                      OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=1.28                         claim=1.28                         OK
     pub_date                         mine=2026-11-04                   claim=2026-11-04                   OK
     echo.value                       mine=1.28                         claim=1.28                         OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     obs_date                         mine=2025-10-01                   claim=2025-10-01                   OK
     value                            mine=2.1                          claim=2.1                          OK
     pub_date                         mine=2025-11-16                   claim=2025-11-16                   OK
     echo.value                       mine=2.1                          claim=2.1                          OK
     echo.obs_month                   mine=2025-10                      claim=2025-10                      OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=2.9                          claim=2.9                          OK
     pub_date                         mine=2026-08-16                   claim=2026-08-16                   OK
     echo.value                       mine=2.9                          claim=2.9                          OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     obs_date                         mine=2026-10-01                   claim=2026-10-01                   OK
     value                            mine=4.0                          claim=4.0                          OK
     pub_date                         mine=2026-11-16                   claim=2026-11-16                   OK
     echo.value                       mine=4.0                          claim=4.0                          OK
     echo.obs_month                   mine=2026-10                      claim=2026-10                      OK
     obs_date                         mine=2025-06-11                   claim=2025-06-11                   OK
     value                            mine=2.15                         claim=2.15                         OK
     echo.value                       mine=2.15                         claim=2.15                         OK
     echo.obs_month                   mine=2025-06                      claim=2025-06                      OK
     obs_date                         mine=2026-06-17                   claim=2026-06-17                   OK
     value                            mine=2.4                          claim=2.4                          OK
     echo.value                       mine=2.4                          claim=2.4                          OK
     echo.obs_month                   mine=2026-06                      claim=2026-06                      OK
     obs_date                         mine=2026-09-16                   claim=2026-09-16                   OK
     value                            mine=2.65                         claim=2.65                         OK
     echo.value                       mine=2.65                         claim=2.65                         OK
     echo.obs_month                   mine=2026-09                      claim=2026-09                      OK
     obs_date                         mine=2025-06-11                   claim=2025-06-11                   OK
     value                            mine=2.0                          claim=2.0                          OK
     echo.value                       mine=2.0                          claim=2.0                          OK
     echo.obs_month                   mine=2025-06                      claim=2025-06                      OK
     obs_date                         mine=2026-06-17                   claim=2026-06-17                   OK
     value                            mine=2.25                         claim=2.25                         OK
     echo.value                       mine=2.25                         claim=2.25                         OK
     echo.obs_month                   mine=2026-06                      claim=2026-06                      OK
     obs_date                         mine=2026-09-16                   claim=2026-09-16                   OK
     value                            mine=2.5                          claim=2.5                          OK
     echo.value                       mine=2.5                          claim=2.5                          OK
     echo.obs_month                   mine=2026-09                      claim=2026-09                      OK
     obs_date                         mine=2025-07-01                   claim=2025-07-01                   OK
     value                            mine=0.63                         claim=0.63                         OK
     pub_date                         mine=2025-11-14                   claim=2025-11-14                   OK
     echo.value                       mine=0.63                         claim=0.63                         OK
     echo.obs_month                   mine=2025-07                      claim=2025-07                      OK
     obs_date                         mine=2026-04-01                   claim=2026-04-01                   OK
     value                            mine=0.8                          claim=0.8                          OK
     pub_date                         mine=2026-08-14                   claim=2026-08-14                   OK
     echo.value                       mine=0.8                          claim=0.8                          OK
     echo.obs_month                   mine=2026-04                      claim=2026-04                      OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=1.16                         claim=1.16                         OK
     pub_date                         mine=2026-11-14                   claim=2026-11-14                   OK
     echo.value                       mine=1.16                         claim=1.16                         OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     obs_date                         mine=2025-10-01                   claim=2025-10-01                   OK
     value                            mine=2.99                         claim=2.99                         OK
     pub_date                         mine=2025-11-20                   claim=2025-11-20                   OK
     echo.value                       mine=2.99                         claim=2.99                         OK
     echo.obs_month                   mine=2025-10                      claim=2025-10                      OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=1.97                         claim=1.97                         OK
     pub_date                         mine=2026-08-20                   claim=2026-08-20                   OK
     echo.value                       mine=1.97                         claim=1.97                         OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     obs_date                         mine=2026-10-01                   claim=2026-10-01                   OK
     value                            mine=2.44                         claim=2.44                         OK
     pub_date                         mine=2026-11-20                   claim=2026-11-20                   OK
     echo.value                       mine=2.44                         claim=2.44                         OK
     echo.obs_month                   mine=2026-10                      claim=2026-10                      OK
   -> consistent (both absent)
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=1.85                         claim=1.85                         OK
     pub_date                         mine=2026-07-30                   claim=2026-07-30                   OK
     echo.value                       mine=1.85                         claim=1.85                         OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     obs_date                         mine=2026-10-01                   claim=2026-10-01                   OK
     value                            mine=2.73                         claim=2.73                         OK
     pub_date                         mine=2026-10-30                   claim=2026-10-30                   OK
     echo.value                       mine=2.73                         claim=2.73                         OK
     echo.obs_month                   mine=2026-10                      claim=2026-10                      OK
     obs_date                         mine=2025-10-01                   claim=2025-10-01                   OK
     value                            mine=0.477                        claim=0.477                        OK
     pub_date                         mine=2025-11-05                   claim=2025-11-05                   OK
     echo.value                       mine=0.477                        claim=0.477                        OK
     echo.obs_month                   mine=2025-10                      claim=2025-10                      OK
     obs_date                         mine=2026-07-01                   claim=2026-07-01                   OK
     value                            mine=0.978                        claim=0.978                        OK
     pub_date                         mine=2026-08-05                   claim=2026-08-05                   OK
     echo.value                       mine=0.978                        claim=0.978                        OK
     echo.obs_month                   mine=2026-07                      claim=2026-07                      OK
     obs_date                         mine=2026-10-01                   claim=2026-10-01                   OK
     value                            mine=1.227                        claim=1.227                        OK
     pub_date                         mine=2026-11-05                   claim=2026-11-05                   OK
     echo.value                       mine=1.227                        claim=1.227                        OK
     echo.obs_month                   mine=2026-10                      claim=2026-10                      OK
```

(A.1 小计: 320 点, 0 不一致)

### A.2 s11_monthly.py — 出处键: 快照 series_store 月频序列(同比=当月观测/去年同月观测-1) + agent_judgment.json /l3、/reader_map/turnings、/l4 文字中的月频数字

```text
### US CPI yoy (derived, same-month base)
   CPI yoy 2026-02 = 2.434                        mine=2.434                      claim=2.434                      OK
   CPI yoy 2026-05 = 4.1666 (peak 4.17)           mine=4.1666                     claim=4.1666                     OK
   CPI yoy 2026-07 = 3.30                         mine=3.3                        claim=3.3                        OK
   CPI yoy 2026-08 = 3.35                         mine=3.35                       claim=3.35                       OK
   CPI yoy 2026-09 = 3.72                         mine=3.72                       claim=3.72                       OK
   CPI yoy 2026-10 missing base                   mine=None                       claim=None                       OK
   CPI yoy 2026-04 = 3.78                         mine=3.78                       claim=3.78                       OK
   peak of CPI yoy in window is 2026-05           mine=2026-05                    claim=2026-05                    OK
   low of CPI yoy is 2026-01                      mine=2026-01                    claim=2026-01                    OK
   all post-2026-05 CPI yoy < 4.1666              mine=True                       claim=True                       OK
### US CORE_CPI yoy
   CORE_CPI yoy 2026-02 = 2.47                    mine=2.47                       claim=2.47                       OK
   CORE_CPI yoy 2026-05 = 2.82                    mine=2.82                       claim=2.82                       OK
   CORE_CPI yoy 2026-05 = 2.8229                  mine=2.8229                     claim=2.8229                     OK
   CORE_CPI yoy 2026-08 = 2.4462                  mine=2.4462                     claim=2.4462                     OK
   CORE_CPI delta 05->08 = -0.3767 (rounded endpoints) mine=-0.3767                    claim=-0.3767                    OK
   CORE_CPI delta 05->08 unrounded = -0.3768      mine=-0.3768                    claim=-0.3768                    OK
   CORE_CPI yoy 2026-07 = 2.47 (3m anchor)        mine=2.47                       claim=2.47                       OK
   CORE_CPI latest valid yoy 2026-09 = 2.57       mine=2.57                       claim=2.57                       OK
   CORE_CPI yoy 2025-09 = 3.02                    mine=3.02                       claim=3.02                       OK
### US CORE_PCE yoy
   CORE_PCE yoy 2025-08 = 2.85                    mine=2.85                       claim=2.85                       OK
   CORE_PCE yoy 2026-05 = 3.16 (peak)             mine=3.16                       claim=3.16                       OK
   CORE_PCE yoy 2026-06 = 3.04                    mine=3.04                       claim=3.04                       OK
   CORE_PCE yoy 2026-07 = 3.00                    mine=3.0                        claim=3.0                        OK
   CORE_PCE yoy 2026-09 = 3.12                    mine=3.12                       claim=3.12                       OK
   CORE_PCE peak month in window                  mine=2026-05                    claim=2026-05                    OK
   post-peak CORE_PCE never above 3.16            mine=True                       claim=True                       OK
### US INDPRO yoy
   INDPRO yoy 2025-11 = 1.7543                    mine=1.7543                     claim=1.7543                     OK
   INDPRO yoy 2026-02 = 0.7972                    mine=0.7972                     claim=0.7972                     OK
   INDPRO yoy 2026-03 = 0.69 (low)                mine=0.69                       claim=0.69                       OK
   INDPRO yoy low month in window                 mine=2026-03                    claim=2026-03                    OK
   INDPRO halved: 0.7972/1.7543 < 0.5             mine=True                       claim=True                       OK
### US GDP yoy by quarter
### CN PMI (level, yoy, vs 50) 2025-11..2026-10
   months >50 = [2025-12,2026-03,2026-04,2026-06,2026-09] mine=['2025-12', '2026-03', '2026-04', '2026-06', '2026-09'] claim=['2025-12', '2026-03', '2026-04', '2026-06', '2026-09'] OK
   values >50 = 50.1/50.4/50.3/50.3/50.1          mine=[50.1, 50.4, 50.3, 50.3, 50.1] claim=[50.1, 50.4, 50.3, 50.3, 50.1] OK
   2026-05 == 50.0                                mine=50.0                       claim=50.0                       OK
   below-50 range = 49.0..49.8                    mine=(49.0, 49.8)               claim=(49.0, 49.8)               OK
   PMI yoy 2025-10 = -2.2 (diff -1.1pt)           mine=(-2.2, -1.1)               claim=(-2.2, -1.1)               OK
   PMI yoy 2026-07 = -0.2 (diff -0.1pt)           mine=(-0.2, -0.1)               claim=(-0.2, -0.1)               OK
   PMI yoy 2026-10 = 0.6/0.61 (diff +0.3pt)       mine=(0.61, 0.3)                claim=(0.61, 0.3)                OK
   PMI candidate 2026-02 yoy = -2.3904            mine=-2.3904                    claim=-2.3904                    OK
   PMI candidate 2026-05 yoy = 1.0101             mine=1.0101                     claim=1.0101                     OK
### CN_CPI_YOY (published yoy series) 2024-09..last
### CN_PPI_YOY (published yoy series) 2024-09..last
### EA_HICP_YOY (published yoy series) 2024-09..last
### JP_CPI_YOY (published yoy series) 2024-09..last
### JP_CPI_TOKYO_YOY (published yoy series) 2024-09..last
### JP_POLICY_RATE (published yoy series) 2024-09..last
### claim checks CN
   CN_PPI 2025-11 low of window                   mine=2025-11                    claim=2025-11                    OK
   CN_PPI non-decreasing after low (连升)           mine=False                      claim=True                       <<< MISMATCH
   CN_PPI 2026-02 = -0.9                          mine=-0.9                       claim=-0.9                       OK
   CN_PPI 2026-05 = 3.9                           mine=3.9                        claim=3.9                        OK
   CN_PPI 2026-07 = 3.5                           mine=3.5                        claim=3.5                        OK
   CN_PPI 2026-10 = 5.7 (window max)              mine=(5.7, True)                claim=(5.7, True)                OK
   CN_CPI 2026-02..05 all in [1.0,1.3]            mine=True                       claim=True                       OK
   CN_CPI candidate 2026-01 0.2 -> 2026-04 1.2    mine=(0.2, 1.2)                 claim=(0.2, 1.2)                 OK
   largest price swing among four (PPI -2.1 -> 5.7 = 7.8pp) mine=7.8                        claim=7.8                        OK
### claim checks EA
   EA HICP 2026-01 low = 1.7                      mine=1.7                        claim=1.7                        OK
   EA HICP 2026-02 = 1.9                          mine=1.9                        claim=1.9                        OK
   EA HICP 2026-04 = 3.0                          mine=3.0                        claim=3.0                        OK
   EA HICP 2026-05 = 3.2                          mine=3.2                        claim=3.2                        OK
   EA HICP 2026-06 = 2.8                          mine=2.8                        claim=2.8                        OK
   EA HICP 2026-07 = 2.9                          mine=2.9                        claim=2.9                        OK
   EA HICP 2026-08 = 3.2                          mine=3.2                        claim=3.2                        OK
   EA HICP 2026-10 = 4.0                          mine=4.0                        claim=4.0                        OK
   EA HICP increments 07,08,09,10 = +0.1,+0.3,+0.6,+0.2 mine=(0.1, 0.3, 0.6, 0.2)       claim=(0.1, 0.3, 0.6, 0.2)       OK
   EA HICP 4.0 is window max (本轮最高)               mine=True                       claim=True                       OK
   EA HICP monotone up 2026-01..2026-05           mine=True                       claim=True                       OK
### claim checks JP
   JP CPI 2025-01 high = 4.03                     mine=4.03                       claim=4.03                       OK
   JP CPI high month (2024-06..2026-02)           mine=2025-01                    claim=2025-01                    OK
   JP CPI path 2025-11 2.9 / 12 2.13 / 2026-01 1.51 / 02 1.27 mine=(2.9, 2.13, 1.51, 1.27)    claim=(2.9, 2.13, 1.51, 1.27)    OK
   JP CPI 2026-03 = 1.46, 2026-04 = 1.38          mine=(1.46, 1.38)               claim=(1.46, 1.38)               OK
   JP CPI 2026-07 = 1.97, 2026-10 = 2.44          mine=(1.97, 2.44)               claim=(1.97, 2.44)               OK
   JP CPI low month 2026-02                       mine=2026-02                    claim=2026-02                    OK
   JP CPI rising every month from 2026-05         mine=True                       claim=True                       OK
   Tokyo 2026-06 = 1.6, 2026-09 = 2.69, 2026-08 = 1.9, 2026-07 = 1.85, 2026-10 = 2.73 mine=(1.6, 2.69, 1.9, 1.85, 2.73) claim=(1.6, 2.69, 1.9, 1.85, 2.73) OK
### latest consumer-price readings: EA 4.0 highest among four (latest obs month)
   EA 4.0 > US 3.72, JP 2.44, CN 0.7              mine=True                       claim=True                       OK
```

(A.2 小计: 69 点, 1 不一致)

### A.3 s12_policy.py — 出处键: 快照 series_store 政策利率序列(DFEDTARU/DFEDTARL/DFF/ECB_MRO/ECB_DFR/JP_POLICY_RATE/CN_LPR_1Y/CN_OMO_7D/CN_POLICY_OVERNIGHT) + 冻结日历条目 + report.json 政策路径面

```text
### DFEDTARU first=2016-11-23 last=2026-11-23 n=3653
### DFF first=2016-11-23 last=2026-11-19 n=3649
### ECB_DFR first=1999-01-01 last=2026-09-16 n=69
### ECB_MRO first=1999-01-01 last=2026-09-16 n=48
### CN_OMO_7D first=2025-10-09 last=2026-10-30 n=201
### CN_POLICY_OVERNIGHT first=2026-11-02 last=2026-11-23 n=16
### CN_LPR_1Y first=2013-10-25 last=2026-11-20 n=1540
### claims
   DFEDTARU window change points = [2025-12-11 -25, 2026-09-17 +25] mine=[('2025-12-11', -25), ('2026-09-17', 25)] claim=[('2025-12-11', -25), ('2026-09-17', 25)] OK
   Fed 2025-12-11 from 4.0 -> 3.75                          mine=(4.0, 3.75)                    claim=(4.0, 3.75)                OK
   Fed 2026-09-17 from 3.75 -> 4.0                          mine=(3.75, 4.0)                    claim=(3.75, 4.0)                OK
   decision date = effective-1 day for 2025-12-11           mine=2025-12-10                     claim=2025-12-10                 OK
   decision 2026-09-16 is weekday before Wed 2026-09-17     mine=2026-09-16                     claim=2026-09-16                 OK
   net bp in window (start-in-force -> end)                 mine=0                              claim=0                          OK
   prior Fed change (before window) effective 2025-10-30 from 4.25 -> 4.0 mine=('2025-10-30', 4.0)            claim=('2025-10-30', 4.0)        OK
   DFF change points in window                              mine=[('2025-11-28', 1.0), ('2025-12-11', -25.0), ('2026-05-07', -1.0), ('2026-05-19', -1.0), ('2026-06-15', 1.0), ('2026-07-08', -1.0), ('2026-07-14', 1.0), ('2026-09-17', 25.0)] claim=[('2025-11-28', 1), ('2025-12-11', -25), ('2026-05-07', -1), ('2026-05-19', -1), ('2 …(截断,全行见 _out_s12_policy.txt)
   DFF 2026-09-17 3.63 -> 3.88                              mine=(3.63, 3.88)                   claim=(3.63, 3.88)               OK
   DFF @2026-09-16 = 3.63                                   mine=3.63                           claim=3.63                       OK
   DFF latest 3.88 @2026-11-19                              mine=('2026-11-19', 3.88)           claim=('2026-11-19', 3.88)       OK
   ECB_DFR window changes                                   mine=[('2026-06-17', 2.0, 2.25), ('2026-09-16', 2.25, 2.5)] claim=[('2026-06-17', 2.0, 2.25), ('2026-09-16', 2.25, 2.5)] OK
   ECB_DFR last obs / lag days                              mine=('2026-09-16', 68)             claim=('2026-09-16', 68)         OK
   ECB_DFR value in force at window start                   mine=('2025-06-11', 2.0)            claim=('2025-06-11', 2.0)        OK
   ECB_DFR first obs inside window                          mine=('2026-06-17', 2.25)           claim=('2026-06-17', 2.25)       OK
   ECB_MRO window changes                                   mine=[('2026-06-17', 2.15, 2.4), ('2026-09-16', 2.4, 2.65)] claim=[('2026-06-17', 2.15, 2.4), ('2026-09-16', 2.4, 2.65)] OK
   ECB_MRO last obs / lag days                              mine=('2026-09-16', 68)             claim=('2026-09-16', 68)         OK
   ECB_MRO value in force at window start                   mine=('2025-06-11', 2.15)           claim=('2025-06-11', 2.15)       OK
   ECB_MRO first obs inside window                          mine=('2026-06-17', 2.4)            claim=('2026-06-17', 2.4)        OK
   ECB effective 2026-06-17 weekday                         mine=Wed                            claim=Wed                        OK
   ECB effective 2026-09-16 weekday                         mine=Wed                            claim=Wed                        OK
   prev Thursday before 2026-06-17 = 2026-06-11             mine=2026-06-11                     claim=2026-06-11                 OK
   weekday of 2026-06-11                                    mine=Thu                            claim=Thu                        OK
   prev Thursday before 2026-09-16 = 2026-09-10             mine=2026-09-10                     claim=2026-09-10                 OK
   weekday of 2026-09-10                                    mine=Thu                            claim=Thu                        OK
   ECB net bp (start-in-force -> end) DFR                   mine=50                             claim=50                         OK
   ECB alt net bp (first obs in window -> end) DFR          mine=25                             claim=25                         OK
   JP step months (>=5bp) = 12,01,06,07,09,10               mine=['2025-12', '2026-01', '2026-06', '2026-07', '2026-09', '2026-10'] claim=['2025-12', '2026-01', '2026-06', '2026-07', '2026-09', '2026-10'] OK
   JP step sizes rounded to whole bp = +8/+17/+11/+14/+7/+18 mine=[8, 17, 11, 14, 7, 18]         claim=[8, 17, 11, 14, 7, 18]     OK
   JP rounding moves about 0.1bp at 2026-04, 2026-08        mine=[('2026-04', -0.1), ('2026-08', -0.1)] claim=[('2026-04', -0.1), ('2026-08', -0.1)] OK
   JP no other nonzero month in window                      mine=8                              claim=8                          OK
   JP sum of steps = 74.9bp                                 mine=74.9                           claim=74.9                       OK
   JP net from 2025-11 0.478 -> 1.227 = 74.9bp              mine=74.9                           claim=74.9                       OK
   JP alt net from 2025-12 0.557 -> 1.227 = 67.0bp          mine=67.0                           claim=67.0                       OK
   JP_POLICY_TARGET in series_store                         mine=False                          claim=False                      OK
   JP_POLICY_TARGET in metric_registry                      mine=False                          claim=False                      OK
   CN_OMO_7D all values in window are 1.4 (no change)       mine=[1.4]                          claim=[1.4]                      OK
   CN_OMO_7D last obs / lag days                            mine=('2026-10-30', 24)             claim=('2026-10-30', 24)         OK
   CN_LPR_1Y all values in window are 3.0                   mine=[3.0]                          claim=[3.0]                      OK
   CN_POLICY_OVERNIGHT first obs                            mine=('2026-11-02', 1.25)           claim=('2026-11-02', 1.25)       OK
   CN_POLICY_OVERNIGHT all values 1.25                      mine=[1.25]                         claim=[1.25]                     OK
   CN_POLICY_OVERNIGHT last obs                             mine=('2026-11-23', 1.25)           claim=('2026-11-23', 1.25)       OK
```

(A.3 小计: 42 点, 0 不一致)

### A.4 s13_rates_assets.py — 出处键: 快照 series_store 日频序列(UST_10Y/TIPS_10Y/BEI_10Y/SPX/NIKKEI225/DAX/CAC40/SHCOMP/VIX/DXY/GOLD_F/BRENT_F/HY_OAS/USDJPY/USDCNY 等) + agent_judgment.json /l3/contradictions[0]、/l3/mechanism_chains、/reader_map 文字中的日频数字

```text
### C1 levels
   UST_10Y latest                                             mine=('2026-11-19', 5.04)       claim=('2026-11-19', 5.04)   OK
   TIPS_10Y latest                                            mine=('2026-11-19', 2.88)       claim=('2026-11-19', 2.88)   OK
   BEI_10Y latest                                             mine=('2026-11-20', 2.15)       claim=('2026-11-20', 2.15)   OK
   VIX latest                                                 mine=('2026-11-23', 27.01)      claim=('2026-11-23', 27.01)  OK
   HY_OAS latest                                              mine=('2026-11-19', 3.52)       claim=('2026-11-19', 3.52)   OK
   USDJPY latest (rounded 2dp)                                mine=('2026-11-23', 159.35)     claim=('2026-11-23', 159.35) OK
   DFF latest                                                 mine=('2026-11-19', 3.88)       claim=('2026-11-19', 3.88)   OK
   JP_POLICY_RATE latest                                      mine=('2026-10-01', 1.227)      claim=('2026-10-01', 1.227)  OK
   CN_PPI_YOY latest value (label in judgment = obs month-end) mine=5.7                        claim=5.7                    OK
   CN_PPI_YOY latest series date vs judgment label            mine=2026-10-01                 claim=2026-10-31             <<< MISMATCH
   CN_CPI_YOY latest value (label in judgment = obs month-end) mine=0.7                        claim=0.7                    OK
   CN_CPI_YOY latest series date vs judgment label            mine=2026-10-01                 claim=2026-10-31             <<< MISMATCH
   CN_PMI_MFG latest                                          mine=('2026-10-01', 49.3)       claim=('2026-10-01', 49.3)   OK
### identity nominal = real + breakeven (same day)
### 12m decomposition 2025-11-19 -> 2026-11-19 (common trading day)
   12m UST_10Y chg bp                                         mine=91                         claim=91                     OK
   12m TIPS_10Y chg bp                                        mine=102                        claim=102                    OK
   12m BEI_10Y chg bp                                         mine=-11                        claim=-11                    OK
   12m residual bp                                            mine=0.0                        claim=0.0                    OK
   12m window endpoints (UST)                                 mine=('2025-11-19', '2026-11-19') claim=('2025-11-19', '2026-11-19') OK
   BEI_10Y 12m 2.27 -> 2.16                                   mine=(2.27, 2.16)               claim=(2.27, 2.16)           OK
### 1m common-day 2026-10-20 -> 2026-11-19
   1m UST_10Y chg bp                                          mine=-8                         claim=-8                     OK
   1m TIPS_10Y chg bp                                         mine=11                         claim=11                     OK
   1m BEI_10Y chg bp                                          mine=-19                        claim=-19                    OK
   1m residual bp                                             mine=0.0                        claim=0.0                    OK
### 3m common-day 2026-08-19 -> 2026-11-19
   3m TIPS_10Y chg bp                                         mine=53                         claim=53                     OK
### BEI_10Y path
   BEI_10Y 2026-02-27 = 2.25                                  mine=2.25                       claim=2.25                   OK
   BEI_10Y 2026-05-04 = 2.50                                  mine=2.5                        claim=2.5                    OK
   BEI_10Y 2026-06-10 = 2.34                                  mine=2.34                       claim=2.34                   OK
   BEI_10Y 2026-10-23 = 2.34                                  mine=2.34                       claim=2.34                   OK
   BEI_10Y range from 2026-06-17: min                         mine=2.15                       claim=2.15                   OK
   BEI_10Y range from 2026-06-17: max                         mine=2.4                        claim=2.4                    OK
   calendar days 2026-10-23 -> 2026-11-20                     mine=28                         claim=28                     OK
   last BEI_10Y obs below 1.8                                 mine=('2020-11-30', 1.77)       claim=('2020-11-30', 1.77)   OK
   BEI_10Y first obs date (informational)                     mine=2016-11-23                 claim=2016-11-23             OK
   judgment: 1.77 is 35bp below latest 2.15 (arithmetic)      mine=38                         claim=35                     <<< MISMATCH
### asset 1-month windows (base = obs nearest to 2026-10-23; end = latest <= 2026-11-23)
   SPX base value                                             mine=7623.68                    claim=7623.68                OK
   SPX end value                                              mine=7203.85                    claim=7203.85                OK
   SPX end date                                               mine=2026-11-23                 claim=2026-11-23             OK
   SPX chg pct                                                mine=-5.51                      claim=-5.51                  OK
   SHCOMP base value                                          mine=3690.48                    claim=3690.48                OK
   SHCOMP end value                                           mine=3538.95                    claim=3538.95                OK
   SHCOMP end date                                            mine=2026-11-23                 claim=2026-11-23             OK
   SHCOMP chg pct                                             mine=-4.11                      claim=-4.11                  OK
   DAX base value                                             mine=25181.65                   claim=25181.65               OK
   DAX end value                                              mine=25209.45                   claim=25209.45               OK
   DAX end date                                               mine=2026-11-23                 claim=2026-11-23             OK
   DAX chg pct                                                mine=0.11                       claim=0.11                   OK
   NIKKEI225 base value                                       mine=62693.16                   claim=62693.16               OK
   NIKKEI225 end value                                        mine=56436.65                   claim=56436.65               OK
   NIKKEI225 end date                                         mine=2026-11-20                 claim=2026-11-20             OK
   NIKKEI225 chg pct                                          mine=-9.98                      claim=-9.98                  OK
   VIX base value                                             mine=19.45                      claim=19.45                  OK
   VIX end value                                              mine=27.01                      claim=27.01                  OK
   VIX end date                                               mine=2026-11-23                 claim=2026-11-23             OK
   VIX chg pct                                                mine=38.87                      claim=38.87                  OK
   DXY base value                                             mine=101.81                     claim=101.81                 OK
   DXY end value                                              mine=104.08                     claim=104.079                OK
   DXY end date                                               mine=2026-11-23                 claim=2026-11-23             OK
   DXY chg pct                                                mine=2.23                       claim=2.23                   OK
   GOLD_F base value                                          mine=4007.9                     claim=4007.9                 OK
   GOLD_F end value                                           mine=3685.2                     claim=3685.2                 OK
   GOLD_F end date                                            mine=2026-11-23                 claim=2026-11-23             OK
   GOLD_F chg pct                                             mine=-8.05                      claim=-8.05                  OK
   UST_10Y base value                                         mine=5.0                        claim=5.0                    OK
   UST_10Y end value                                          mine=5.04                       claim=5.04                   OK
   UST_10Y end date                                           mine=2026-11-19                 claim=2026-11-19             OK
   UST_10Y chg pct                                            mine=0.8                        claim=0.8                    OK
   CAC40 in series_store                                      mine=True                       claim=True                   OK
### same-day close 2026-10-23 -> 2026-11-20
   SPX base date (10-23 or prior)                             mine=2026-10-23                 claim=2026-10-23             OK
   SPX 10-23 -> 11-20 pct                                     mine=-9.36                      claim=-9.36                  OK
   DAX base date (10-23 or prior)                             mine=2026-10-23                 claim=2026-10-23             OK
   DAX 10-23 -> 11-20 pct                                     mine=-1.5                       claim=-1.5                   OK
   CAC40 base date (10-23 or prior)                           mine=2026-10-23                 claim=2026-10-23             OK
   CAC40 10-23 -> 11-20 pct                                   mine=1.86                       claim=1.86                   OK
   NIKKEI225 base date (10-23 or prior)                       mine=2026-10-23                 claim=2026-10-23             OK
   NIKKEI225 10-23 -> 11-20 pct                               mine=-9.98                      claim=-9.98                  OK
   VIX base date (10-23 or prior)                             mine=2026-10-23                 claim=2026-10-23             OK
   VIX 10-23 -> 11-20 pct                                     mine=84.52                      claim=84.52                  OK
### common-day SPX vs TIPS
   12m SPX pct (2025-11-19 -> 2026-11-19)                     mine=8.03                       claim=8.03                   OK
   12m NIKKEI225 pct (2025-11-19 -> 2026-11-19)               mine=22.47                      claim=22.47                  OK
   12m DAX pct (2025-11-19 -> 2026-11-19)                     mine=9.93                       claim=9.93                   OK
   1m SPX pct (2026-10-20 -> 2026-11-19)                      mine=-6.96                      claim=-6.96                  OK
   3m SPX pct (2026-08-19 -> 2026-11-19)                      mine=-6.9                       claim=-6.9                   OK
### BRENT_F
   BRENT_F month-end 2026-02                                  mine=('2026-02-27', 72.48)      claim=('2026-02-27', 72.48)  OK
   BRENT_F month-end 2026-03                                  mine=('2026-03-31', 118.35)     claim=('2026-03-31', 118.35) OK
   BRENT_F month-end 2026-05                                  mine=('2026-05-29', 92.05)      claim=('2026-05-29', 92.05)  OK
   BRENT_F month-end 2026-06                                  mine=('2026-06-30', 72.92)      claim=('2026-06-30', 72.92)  OK
   BRENT_F first-last 02->05 pct                              mine=27.0                       claim=27.0                   OK
   BRENT_F latest                                             mine=('2026-11-23', 88.19)      claim=('2026-11-23', 88.19)  OK
   BRENT_F 2026-10-23                                         mine=116.720001                 claim=116.72                 OK
   BRENT_F MTD pct (from 2026-10 month-end)                   mine=-25.03                     claim=-25.03                 OK
### HY_OAS
   HY_OAS first obs                                           mine=('2023-11-21', 3.95)       claim=('2023-11-21', 3.95)   OK
   HY_OAS series max                                          mine=('2025-04-07', 4.61)       claim=('2025-04-07', 4.61)   OK
   HY_OAS percentile (mid-rank, all history to date)          mine=92                         claim=92                     OK
   HY_OAS percentile (share<=x)                               mine=92                         claim=92                     OK
   no obs >= 3.52 between 2025-05-10 and latest               mine=[]                         claim=[]                     OK
   last obs >= 3.52 before latest = 2025-05-09                mine=2025-05-09                 claim=2025-05-09             OK
   HY_OAS ISO-week base 2026-11-13                            mine=('2026-11-13', 3.23)       claim=('2026-11-13', 3.23)   OK
   HY_OAS 1-week chg (pp)                                     mine=0.29                       claim=0.29                   OK
   HY_OAS strict 7-day chg (pp)                               mine=0.32                       claim=0.32                   OK
   HY_OAS 12m ago obs                                         mine=('2025-11-19', 3.17)       claim=('2025-11-19', 3.17)   OK
   HY_OAS 12m chg (pp)                                        mine=0.35                       claim=0.35                   OK
### FX
   USDCNY 2025-11-19                                          mine=7.1075                     claim=7.1075                 OK
   USDCNY 2026-11-19                                          mine=6.6676                     claim=6.6676                 OK
   USDCNY chg pct (full precision)                            mine=-6.19                      claim=-6.19                  OK
   USDJPY 2026-10-23                                          mine=156.494003                 claim=156.49                 OK
   USDJPY 2026-11-23                                          mine=159.347                    claim=159.35                 OK
   USDJPY 1m pct (full precision)                             mine=1.82                       claim=1.82                   OK
### USDJPY / SPX daily co-movement, base 2026-10-23, days 2026-10-26..2026-11-23 on common dates
   number of common trading days                              mine=21                         claim=21                     OK
   corr of daily pct changes                                  mine=0.19                       claim=0.19                   OK
   SPX down days                                              mine=12                         claim=12                     OK
   SPX up days                                                mine=9                          claim=9                      OK
   USDJPY down on SPX-down days                               mine=9                          claim=9                      OK
   USDJPY up on SPX-down days                                 mine=3                          claim=3                      OK
   USDJPY up on SPX-up days                                   mine=7                          claim=7                      OK
   USDJPY down on SPX-up days                                 mine=2                          claim=2                      OK
   USDJPY compound on SPX-down days                           mine=0.16                       claim=0.16                   OK
   USDJPY compound on SPX-up days                             mine=1.66                       claim=1.66                   OK
   four largest SPX daily drops (dates)                       mine=['2026-11-05', '2026-11-20', '2026-11-19', '2026-11-16'] claim=['2026-11-05', '2026-11-20', '2026-11-19', '2026-11-16'] OK
   USDJPY pct on those days                                   mine=[-0.07, 0.2, -0.08, -0.06] claim=[-0.07, 0.2, -0.08, -0.06] OK
### JP CPI path and CN PMI window
   JP CPI 2025-01 = 4.03                                      mine=4.03                       claim=4.03                   OK
   JP CPI max over 2025-01..2026-02 is 2025-01                mine=2025-01                    claim=2025-01                OK
   months of uptick between 2025-02 and 2026-02               mine=['2025-09', '2025-10']     claim=['2025-09', '2025-10'] OK
   CN PMI months >50 in window                                mine=['2025-12', '2026-03', '2026-04', '2026-06', '2026-09'] claim=['2025-12', '2026-03', '2026-04', '2026-06', '2026-09'] OK
   CN PMI months ==50 in window                               mine=['2026-05']                claim=['2026-05']            OK
   CN PMI remaining months range                              mine=(49.0, 49.8)               claim=(49.0, 49.8)           OK
```

(A.4 小计: 125 点, 3 不一致)

### A.5 s14_history.py — 出处键: 快照 series_store(事后月末表、同步面两端取值、同比基期) + 冻结日历(发布日) + MAP_REPORT.md 同步表(第337-354/455-472/579-596行) + report.json 相似检索面 + agent_judgment.json /reader_map/history_periods

```text
### ex-post month-end tables (judgment history_periods[*].ex_post)
   2025-03 3m target month                              mine=2025-06                  claim=2025-06              OK
   2025-03 3m DFEDTARU                                  mine=0.0                      claim=0.0                  OK
   2025-03 3m UNEMPLOYMENT                              mine=-0.1                     claim=-0.1                 OK
   2025-03 3m CPI                                       mine=0.52                     claim=0.52                 OK
   2025-03 3m INDPRO                                    mine=0.43                     claim=0.43                 OK
   2025-03 3m SPX                                       mine=10.57                    claim=10.57                OK
   2025-03 3m NIKKEI225                                 mine=13.67                    claim=13.67                OK
   2025-03 3m DAX                                       mine=7.88                     claim=7.88                 OK
   2025-03 3m SHCOMP                                    mine=3.26                     claim=3.26                 OK
   2025-03 3m GOLD_F                                    mine=5.92                     claim=5.92                 OK
   2025-03 3m DXY                                       mine=-7.03                    claim=-7.03                OK
   2025-03 3m UST_10Y                                   mine=0.01                     claim=0.01                 OK
   2025-03 6m target month                              mine=2025-09                  claim=2025-09              OK
   2025-03 6m DFEDTARU                                  mine=-0.25                    claim=-0.25                OK
   2025-03 6m UNEMPLOYMENT                              mine=0.2                      claim=0.2                  OK
   2025-03 6m CPI                                       mine=1.39                     claim=1.39                 OK
   2025-03 6m INDPRO                                    mine=0.62                     claim=0.62                 OK
   2025-03 6m SPX                                       mine=19.18                    claim=19.18                OK
   2025-03 6m NIKKEI225                                 mine=26.15                    claim=26.15                OK
   2025-03 6m DAX                                       mine=7.75                     claim=7.75                 OK
   2025-03 6m SHCOMP                                    mine=16.4                     claim=16.4                 OK
   2025-03 6m GOLD_F                                    mine=24.03                    claim=24.03                OK
   2025-03 6m DXY                                       mine=-6.18                    claim=-6.18                OK
   2025-03 6m UST_10Y                                   mine=-0.07                    claim=-0.07                OK
   2025-03 12m target month                             mine=2026-03                  claim=2026-03              OK
   2025-03 12m DFEDTARU                                 mine=-0.75                    claim=-0.75                OK
   2025-03 12m UNEMPLOYMENT                             mine=0.1                      claim=0.1                  OK
   2025-03 12m CPI                                      mine=3.29                     claim=3.29                 OK
   2025-03 12m INDPRO                                   mine=0.69                     claim=0.69                 OK
   2025-03 12m SPX                                      mine=16.33                    claim=16.33                OK
   2025-03 12m NIKKEI225                                mine=43.37                    claim=43.37                OK
   2025-03 12m DAX                                      mine=2.33                     claim=2.33                 OK
   2025-03 12m SHCOMP                                   mine=16.67                    claim=16.67                OK
   2025-03 12m GOLD_F                                   mine=48.83                    claim=48.83                OK
   2025-03 12m DXY                                      mine=-4.08                    claim=-4.08                OK
   2025-03 12m UST_10Y                                  mine=0.07                     claim=0.07                 OK
   2022-06 3m target month                              mine=2022-09                  claim=2022-09              OK
   2022-06 3m DFEDTARU                                  mine=1.5                      claim=1.5                  OK
   2022-06 3m UNEMPLOYMENT                              mine=-0.1                     claim=-0.1                 OK
   2022-06 3m CPI                                       mine=0.47                     claim=0.47                 OK
   2022-06 3m INDPRO                                    mine=0.27                     claim=0.27                 OK
   2022-06 3m SPX                                       mine=-5.28                    claim=-5.28                OK
   2022-06 3m NIKKEI225                                 mine=-1.73                    claim=-1.73                OK
   2022-06 3m DAX                                       mine=-5.24                    claim=-5.24                OK
   2022-06 3m SHCOMP                                    mine=-11.01                   claim=-11.01               OK
   2022-06 3m GOLD_F                                    mine=-7.49                    claim=-7.49                OK
   2022-06 3m DXY                                       mine=7.1                      claim=7.1                  OK
   2022-06 3m UST_10Y                                   mine=0.85                     claim=0.85                 OK
   2022-06 6m target month                              mine=2022-12                  claim=2022-12              OK
   2022-06 6m DFEDTARU                                  mine=2.75                     claim=2.75                 OK
   2022-06 6m UNEMPLOYMENT                              mine=-0.1                     claim=-0.1                 OK
   2022-06 6m CPI                                       mine=1.31                     claim=1.31                 OK
   2022-06 6m INDPRO                                    mine=-1.24                    claim=-1.24                OK
   2022-06 6m SPX                                       mine=1.43                     claim=1.43                 OK
   2022-06 6m NIKKEI225                                 mine=-1.13                    claim=-1.13                OK
   2022-06 6m DAX                                       mine=8.92                     claim=8.92                 OK
   2022-06 6m SHCOMP                                    mine=-9.1                     claim=-9.1                 OK
   2022-06 6m GOLD_F                                    mine=1.05                     claim=1.05                 OK
   2022-06 6m DXY                                       mine=-1.12                    claim=-1.12                OK
   2022-06 6m UST_10Y                                   mine=0.9                      claim=0.9                  OK
   2022-06 12m target month                             mine=2023-06                  claim=2023-06              OK
   2022-06 12m DFEDTARU                                 mine=3.5                      claim=3.5                  OK
   2022-06 12m UNEMPLOYMENT                             mine=0.0                      claim=0.0                  OK
   2022-06 12m CPI                                      mine=3.07                     claim=3.07                 OK
   2022-06 12m INDPRO                                   mine=-0.89                    claim=-0.89                OK
   2022-06 12m SPX                                      mine=17.57                    claim=17.57                OK
   2022-06 12m NIKKEI225                                mine=25.75                    claim=25.75                OK
   2022-06 12m DAX                                      mine=26.32                    claim=26.32                OK
   2022-06 12m SHCOMP                                   mine=-5.78                    claim=-5.78                OK
   2022-06 12m GOLD_F                                   mine=6.76                     claim=6.76                 OK
   2022-06 12m DXY                                      mine=-1.7                     claim=-1.7                 OK
   2022-06 12m UST_10Y                                  mine=0.83                     claim=0.83                 OK
   2023-10 3m target month                              mine=2024-01                  claim=2024-01              OK
   2023-10 3m DFEDTARU                                  mine=0.0                      claim=0.0                  OK
   2023-10 3m UNEMPLOYMENT                              mine=-0.2                     claim=-0.2                 OK
   2023-10 3m CPI                                       mine=0.65                     claim=0.65                 OK
   2023-10 3m INDPRO                                    mine=-1.24                    claim=-1.24                OK
   2023-10 3m SPX                                       mine=15.54                    claim=15.54                OK
   2023-10 3m NIKKEI225                                 mine=17.59                    claim=17.59                OK
   2023-10 3m DAX                                       mine=14.13                    claim=14.13                OK
   2023-10 3m SHCOMP                                    mine=-7.63                    claim=-7.63                OK
   2023-10 3m GOLD_F                                    mine=2.71                     claim=2.71                 OK
   2023-10 3m DXY                                       mine=-3.18                    claim=-3.18                OK
   2023-10 3m UST_10Y                                   mine=-0.89                    claim=-0.89                OK
   2023-10 6m target month                              mine=2024-04                  claim=2024-04              OK
   2023-10 6m DFEDTARU                                  mine=0.0                      claim=0.0                  OK
   2023-10 6m UNEMPLOYMENT                              mine=0.0                      claim=0.0                  OK
   2023-10 6m CPI                                       mine=1.73                     claim=1.73                 OK
   2023-10 6m INDPRO                                    mine=-0.22                    claim=-0.22                OK
   2023-10 6m SPX                                       mine=20.07                    claim=20.07                OK
   2023-10 6m NIKKEI225                                 mine=24.46                    claim=24.46                OK
   2023-10 6m DAX                                       mine=21.08                    claim=21.08                OK
   2023-10 6m SHCOMP                                    mine=2.85                     claim=2.85                 OK
   2023-10 6m GOLD_F                                    mine=15.47                    claim=15.47                OK
   2023-10 6m DXY                                       mine=-0.41                    claim=-0.41                OK
   2023-10 6m UST_10Y                                   mine=-0.19                    claim=-0.19                OK
   2023-10 12m target month                             mine=2024-10                  claim=2024-10              OK
   2023-10 12m DFEDTARU                                 mine=-0.5                     claim=-0.5                 OK
   2023-10 12m UNEMPLOYMENT                             mine=0.2                      claim=0.2                  OK
   2023-10 12m CPI                                      mine=2.58                     claim=2.58                 OK
   2023-10 12m INDPRO                                   mine=-0.99                    claim=-0.99                OK
   2023-10 12m SPX                                      mine=36.04                    claim=36.04                OK
   2023-10 12m NIKKEI225                                mine=26.65                    claim=26.65                OK
   2023-10 12m DAX                                      mine=28.81                    claim=28.81                OK
   2023-10 12m SHCOMP                                   mine=8.65                     claim=8.65                 OK
   2023-10 12m GOLD_F                                   mine=37.86                    claim=37.86                OK
   2023-10 12m DXY                                      mine=-2.51                    claim=-2.51                OK
   2023-10 12m UST_10Y                                  mine=-0.6                     claim=-0.6                 OK
### scenario direction quotes (same tables)
   2022-06 3m SPX                                       mine=-5.28                    claim=-5.28                OK
   2022-06 3m GOLD_F                                    mine=-7.49                    claim=-7.49                OK
   2022-06 3m DXY                                       mine=7.1                      claim=7.1                  OK
   2022-06 12m SPX (+17.57)                             mine=17.57                    claim=17.57                OK
   2025-03 12m GOLD_F                                   mine=48.83                    claim=48.83                OK
   2025-03 12m DXY                                      mine=-4.08                    claim=-4.08                OK
   2025-03 12m SPX                                      mine=16.33                    claim=16.33                OK
### S6-derived history facts (distance / pct / dims)
   2025-03 distance 4dp                                 mine=0.7272                   claim=0.7272               OK
   2025-03 pct 2dp                                      mine=0.0                      claim=0.0                  OK
   2025-03 vol share pct                                mine=42.1                     claim=42.1                 OK
   2025-03 rates share pct                              mine=40.7                     claim=40.7                 OK
   2025-03 inflation share pct                          mine=10.5                     claim=10.5                 OK
   2025-03 valuation share pct                          mine=6.7                      claim=6.7                  OK
   2022-06 distance 4dp                                 mine=0.7918                   claim=0.7918               OK
   2022-06 pct 2dp                                      mine=1.3699                   claim=1.37                 OK
   2023-10 distance 4dp                                 mine=1.0542                   claim=1.0542               OK
   2023-10 pct 2dp                                      mine=30.137                   claim=30.14                OK
### sync-face: quoted latest-revised values
   2025-03 EA_HICP_YOY 2025-02                          mine=2.3                      claim=2.3                  OK
   2025-03 JP_CPI_YOY 2025-02                           mine=3.66                     claim=3.66                 OK
   2025-03 CN_PPI_YOY 2025-02                           mine=-2.2                     claim=-2.2                 OK
   2025-03 CN_CPI_YOY 2025-02                           mine=-0.7                     claim=-0.7                 OK
   2022-06 EA_HICP_YOY 2022-05                          mine=8.1                      claim=8.1                  OK
   2022-06 JP_CPI_YOY 2022-05                           mine=2.46                     claim=2.46                 OK
   2022-06 CN_PPI_YOY 2022-05                           mine=6.4                      claim=6.4                  OK
   2022-06 CN_CPI_YOY 2022-05                           mine=2.1                      claim=2.1                  OK
   2023-10 EA_HICP_YOY 2023-10                          mine=2.9                      claim=2.9                  OK
   2023-10 JP_CPI_YOY 2023-09                           mine=3.05                     claim=3.05                 OK
   2023-10 CN_PPI_YOY 2023-09                           mine=-2.5                     claim=-2.5                 OK
   2023-10 CN_CPI_YOY 2023-09                           mine=0.0                      claim=0.0                  OK
### sync-face recompute (visibility = publication date <= month end; rules from planner RELEASE_RULES)
   2025-03 US/growth anchor-3 obs date                  mine=2024-07-01               claim=2024-07-01           OK
   2025-03 US/growth anchor-3 value                     mine=2.9479                   claim=2.9479               OK
   2025-03 US/growth anchor-3 pub date                  mine=2024-10-29               claim=2024-10-29           OK
   2025-03 US/growth cutoff obs date                    mine=2024-10-01               claim=2024-10-01           OK
   2025-03 US/growth cutoff value                       mine=2.6419                   claim=2.6419               OK
   2025-03 US/growth cutoff pub date                    mine=2025-01-29               claim=2025-01-29           OK
   2025-03 US/inflation anchor-3 obs date               mine=2024-11-01               claim=2024-11-01           OK
   2025-03 US/inflation anchor-3 value                  mine=2.7195                   claim=2.7195               OK
   2025-03 US/inflation anchor-3 pub date               mine=2024-12-13               claim=2024-12-13           OK
   2025-03 US/inflation cutoff obs date                 mine=2025-02-01               claim=2025-02-01           OK
   2025-03 US/inflation cutoff value                    mine=2.8016                   claim=2.8016               OK
   2025-03 US/inflation cutoff pub date                 mine=2025-03-13               claim=2025-03-13           OK
   2025-03 US/policy anchor-3 obs date                  mine=2024-12-31               claim=2024-12-31           OK
   2025-03 US/policy anchor-3 value                     mine=4.5                      claim=4.5                  OK
   2025-03 US/policy anchor-3 pub date                  mine=2024-12-31               claim=2024-12-31           OK
   2025-03 US/policy cutoff obs date                    mine=2025-03-31               claim=2025-03-31           OK
   2025-03 US/policy cutoff value                       mine=4.5                      claim=4.5                  OK
   2025-03 US/policy cutoff pub date                    mine=2025-03-31               claim=2025-03-31           OK
   2025-03 CN/growth anchor-3 obs date                  mine=2024-12-01               claim=2024-12-01           OK
   2025-03 CN/growth anchor-3 value                     mine=50.1                     claim=50.1                 OK
   2025-03 CN/growth anchor-3 pub date                  mine=2024-12-30               claim=2024-12-30           OK
   2025-03 CN/growth cutoff obs date                    mine=2025-03-01               claim=2025-03-01           OK
   2025-03 CN/growth cutoff value                       mine=50.5                     claim=50.5                 OK
   2025-03 CN/growth cutoff pub date                    mine=2025-03-30               claim=2025-03-30           OK
   2025-03 CN/inflation anchor-3 obs date               mine=2024-11-01               claim=2024-11-01           OK
   2025-03 CN/inflation anchor-3 value                  mine=0.2                      claim=0.2                  OK
   2025-03 CN/inflation anchor-3 pub date               mine=2024-12-09               claim=2024-12-09           OK
   2025-03 CN/inflation cutoff obs date                 mine=2025-02-01               claim=2025-02-01           OK
   2025-03 CN/inflation cutoff value                    mine=-0.7                     claim=-0.7                 OK
   2025-03 CN/inflation cutoff pub date                 mine=2025-03-09               claim=2025-03-09           OK
   2025-03 CN/policy anchor-3 obs date                  mine=2024-12-20               claim=2024-12-20           OK
   2025-03 CN/policy anchor-3 value                     mine=3.1                      claim=3.1                  OK
   2025-03 CN/policy anchor-3 pub date                  mine=2024-12-20               claim=2024-12-20           OK
   2025-03 CN/policy cutoff obs date                    mine=2025-03-20               claim=2025-03-20           OK
   2025-03 CN/policy cutoff value                       mine=3.1                      claim=3.1                  OK
   2025-03 CN/policy cutoff pub date                    mine=2025-03-20               claim=2025-03-20           OK
   2025-03 EA/growth anchor-3 obs date                  mine=2024-07-01               claim=2024-07-01           OK
   2025-03 EA/growth anchor-3 value                     mine=1.31                     claim=1.31                 OK
   2025-03 EA/growth anchor-3 pub date                  mine=2024-11-04               claim=2024-11-04           OK
   2025-03 EA/growth cutoff obs date                    mine=2024-10-01               claim=2024-10-01           OK
   2025-03 EA/growth cutoff value                       mine=1.56                     claim=1.56                 OK
   2025-03 EA/growth cutoff pub date                    mine=2025-02-04               claim=2025-02-04           OK
   2025-03 EA/inflation anchor-3 obs date               mine=2024-12-01               claim=2024-12-01           OK
   2025-03 EA/inflation anchor-3 value                  mine=2.4                      claim=2.4                  OK
   2025-03 EA/inflation anchor-3 pub date               mine=2024-12-31               claim=2024-12-31           OK
   2025-03 EA/inflation cutoff obs date                 mine=2025-02-01               claim=2025-02-01           OK
   2025-03 EA/inflation cutoff value                    mine=2.3                      claim=2.3                  OK
   2025-03 EA/inflation cutoff pub date                 mine=2025-02-28               claim=2025-02-28           OK
   2025-03 EA/policy anchor-3 obs date                  mine=2024-12-18               claim=2024-12-18           OK
   2025-03 EA/policy anchor-3 value                     mine=3.15                     claim=3.15                 OK
   2025-03 EA/policy anchor-3 pub date                  mine=2024-12-18               claim=2024-12-18           OK
   2025-03 EA/policy cutoff obs date                    mine=2025-03-12               claim=2025-03-12           OK
   2025-03 EA/policy cutoff value                       mine=2.65                     claim=2.65                 OK
   2025-03 EA/policy cutoff pub date                    mine=2025-03-12               claim=2025-03-12           OK
   2025-03 JP/growth anchor-3 obs date                  mine=2024-07-01               claim=2024-07-01           OK
   2025-03 JP/growth anchor-3 value                     mine=1.11                     claim=1.11                 OK
   2025-03 JP/growth anchor-3 pub date                  mine=2024-11-14               claim=2024-11-14           OK
   2025-03 JP/growth cutoff obs date                    mine=2024-10-01               claim=2024-10-01           OK
   2025-03 JP/growth cutoff value                       mine=1.01                     claim=1.01                 OK
   2025-03 JP/growth cutoff pub date                    mine=2025-02-14               claim=2025-02-14           OK
   2025-03 JP/inflation anchor-3 obs date               mine=2024-11-01               claim=2024-11-01           OK
   2025-03 JP/inflation anchor-3 value                  mine=2.92                     claim=2.92                 OK
   2025-03 JP/inflation anchor-3 pub date               mine=2024-12-20               claim=2024-12-20           OK
   2025-03 JP/inflation cutoff obs date                 mine=2025-02-01               claim=2025-02-01           OK
   2025-03 JP/inflation cutoff value                    mine=3.66                     claim=3.66                 OK
   2025-03 JP/inflation cutoff pub date                 mine=2025-03-20               claim=2025-03-20           OK
   2025-03 JP/policy anchor-3 obs date                  mine=2024-11-01               claim=2024-11-01           OK
   2025-03 JP/policy anchor-3 value                     mine=0.227                    claim=0.227                OK
   2025-03 JP/policy anchor-3 pub date                  mine=2024-12-05               claim=2024-12-05           OK
   2025-03 JP/policy cutoff obs date                    mine=2025-02-01               claim=2025-02-01           OK
   2025-03 JP/policy cutoff value                       mine=0.478                    claim=0.478                OK
   2025-03 JP/policy cutoff pub date                    mine=2025-03-05               claim=2025-03-05           OK
   2025-03 label CN/growth                              mine=分化                       claim=分化                   OK
   2025-03 label CN/inflation                           mine=分化                       claim=分化                   OK
   2025-03 label CN/policy                              mine=同步                       claim=同步                   OK
   2025-03 label EA/growth                              mine=分化                       claim=分化                   OK
   2025-03 label EA/inflation                           mine=分化                       claim=分化                   OK
   2025-03 label EA/policy                              mine=分化                       claim=分化                   OK
   2025-03 label JP/growth                              mine=同步                       claim=同步                   OK
   2025-03 label JP/inflation                           mine=同步                       claim=同步                   OK
   2025-03 label JP/policy                              mine=分化                       claim=分化                   OK
   2025-03 number of synchronized cells (of 9)          mine=3                        claim=3                    OK
   2022-06 US/growth anchor-3 obs date                  mine=2021-10-01               claim=2021-10-01           OK
   2022-06 US/growth anchor-3 value                     mine=5.8182                   claim=5.8182               OK
   2022-06 US/growth anchor-3 pub date                  mine=2022-01-29               claim=2022-01-29           OK
   2022-06 US/growth cutoff obs date                    mine=2022-01-01               claim=2022-01-01           OK
   2022-06 US/growth cutoff value                       mine=3.9754                   claim=3.9754               OK
   2022-06 US/growth cutoff pub date                    mine=2022-04-29               claim=2022-04-29           OK
   2022-06 US/inflation anchor-3 obs date               mine=2022-02-01               claim=2022-02-01           OK
   2022-06 US/inflation anchor-3 value                  mine=7.9373                   claim=7.9373               OK
   2022-06 US/inflation anchor-3 pub date               mine=2022-03-13               claim=2022-03-13           OK
   2022-06 US/inflation cutoff obs date                 mine=2022-05-01               claim=2022-05-01           OK
   2022-06 US/inflation cutoff value                    mine=8.5382                   claim=8.5382               OK
   2022-06 US/inflation cutoff pub date                 mine=2022-06-13               claim=2022-06-13           OK
   2022-06 US/policy anchor-3 obs date                  mine=2022-03-31               claim=2022-03-31           OK
   2022-06 US/policy anchor-3 value                     mine=0.5                      claim=0.5                  OK
   2022-06 US/policy anchor-3 pub date                  mine=2022-03-31               claim=2022-03-31           OK
   2022-06 US/policy cutoff obs date                    mine=2022-06-30               claim=2022-06-30           OK
   2022-06 US/policy cutoff value                       mine=1.75                     claim=1.75                 OK
   2022-06 US/policy cutoff pub date                    mine=2022-06-30               claim=2022-06-30           OK
   2022-06 CN/growth anchor-3 obs date                  mine=2022-03-01               claim=2022-03-01           OK
   2022-06 CN/growth anchor-3 value                     mine=49.5                     claim=49.5                 OK
   2022-06 CN/growth anchor-3 pub date                  mine=2022-03-30               claim=2022-03-30           OK
   2022-06 CN/growth cutoff obs date                    mine=2022-06-01               claim=2022-06-01           OK
   2022-06 CN/growth cutoff value                       mine=50.2                     claim=50.2                 OK
   2022-06 CN/growth cutoff pub date                    mine=2022-06-29               claim=2022-06-29           OK
   2022-06 CN/inflation anchor-3 obs date               mine=2022-02-01               claim=2022-02-01           OK
   2022-06 CN/inflation anchor-3 value                  mine=0.9                      claim=0.9                  OK
   2022-06 CN/inflation anchor-3 pub date               mine=2022-03-09               claim=2022-03-09           OK
   2022-06 CN/inflation cutoff obs date                 mine=2022-05-01               claim=2022-05-01           OK
   2022-06 CN/inflation cutoff value                    mine=2.1                      claim=2.1                  OK
   2022-06 CN/inflation cutoff pub date                 mine=2022-06-09               claim=2022-06-09           OK
   2022-06 CN/policy anchor-3 obs date                  mine=2022-03-21               claim=2022-03-21           OK
   2022-06 CN/policy anchor-3 value                     mine=3.7                      claim=3.7                  OK
   2022-06 CN/policy anchor-3 pub date                  mine=2022-03-20               claim=2022-03-20           OK
   2022-06 CN/policy cutoff obs date                    mine=2022-06-20               claim=2022-06-20           OK
   2022-06 CN/policy cutoff value                       mine=3.7                      claim=3.7                  OK
   2022-06 CN/policy cutoff pub date                    mine=2022-06-20               claim=2022-06-19           <<< MISMATCH
   2022-06 EA/growth anchor-3 obs date                  mine=2021-10-01               claim=2021-10-01           OK
   2022-06 EA/growth anchor-3 value                     mine=5.68                     claim=5.68                 OK
   2022-06 EA/growth anchor-3 pub date                  mine=2022-02-04               claim=2022-02-04           OK
   2022-06 EA/growth cutoff obs date                    mine=2022-01-01               claim=2022-01-01           OK
   2022-06 EA/growth cutoff value                       mine=5.58                     claim=5.58                 OK
   2022-06 EA/growth cutoff pub date                    mine=2022-05-05               claim=2022-05-05           OK
   2022-06 EA/inflation anchor-3 obs date               mine=2022-03-01               claim=2022-03-01           OK
   2022-06 EA/inflation anchor-3 value                  mine=7.4                      claim=7.4                  OK
   2022-06 EA/inflation anchor-3 pub date               mine=2022-03-31               claim=2022-03-31           OK
   2022-06 EA/inflation cutoff obs date                 mine=2022-05-01               claim=2022-05-01           OK
   2022-06 EA/inflation cutoff value                    mine=8.1                      claim=8.1                  OK
   2022-06 EA/inflation cutoff pub date                 mine=2022-05-31               claim=2022-05-31           OK
   2022-06 EA/policy anchor-3 obs date                  mine=2019-09-18               claim=2019-09-18           OK
   2022-06 EA/policy anchor-3 value                     mine=0.0                      claim=0                    OK
   2022-06 EA/policy anchor-3 pub date                  mine=2019-09-18               claim=2019-09-18           OK
   2022-06 EA/policy cutoff obs date                    mine=2019-09-18               claim=2019-09-18           OK
   2022-06 EA/policy cutoff value                       mine=0.0                      claim=0                    OK
   2022-06 EA/policy cutoff pub date                    mine=2019-09-18               claim=2019-09-18           OK
   2022-06 JP/growth anchor-3 obs date                  mine=2021-10-01               claim=2021-10-01           OK
   2022-06 JP/growth anchor-3 value                     mine=2.8                      claim=2.8                  OK
   2022-06 JP/growth anchor-3 pub date                  mine=2022-02-14               claim=2022-02-14           OK
   2022-06 JP/growth cutoff obs date                    mine=2022-01-01               claim=2022-01-01           OK
   2022-06 JP/growth cutoff value                       mine=1.15                     claim=1.15                 OK
   2022-06 JP/growth cutoff pub date                    mine=2022-05-15               claim=2022-05-15           OK
   2022-06 JP/inflation anchor-3 obs date               mine=2022-02-01               claim=2022-02-01           OK
   2022-06 JP/inflation anchor-3 value                  mine=0.95                     claim=0.95                 OK
   2022-06 JP/inflation anchor-3 pub date               mine=2022-03-20               claim=2022-03-20           OK
   2022-06 JP/inflation cutoff obs date                 mine=2022-05-01               claim=2022-05-01           OK
   2022-06 JP/inflation cutoff value                    mine=2.46                     claim=2.46                 OK
   2022-06 JP/inflation cutoff pub date                 mine=2022-06-20               claim=2022-06-20           OK
   2022-06 JP/policy anchor-3 obs date                  mine=2022-02-01               claim=2022-02-01           OK
   2022-06 JP/policy anchor-3 value                     mine=-0.018                   claim=-0.018               OK
   2022-06 JP/policy anchor-3 pub date                  mine=2022-03-05               claim=2022-03-05           OK
   2022-06 JP/policy cutoff obs date                    mine=2022-05-01               claim=2022-05-01           OK
   2022-06 JP/policy cutoff value                       mine=-0.018                   claim=-0.018               OK
   2022-06 JP/policy cutoff pub date                    mine=2022-06-05               claim=2022-06-05           OK
   2022-06 label CN/growth                              mine=分化                       claim=分化                   OK
   2022-06 label CN/inflation                           mine=同步                       claim=同步                   OK
   2022-06 label CN/policy                              mine=分化                       claim=分化                   OK
   2022-06 label EA/growth                              mine=同步                       claim=同步                   OK
   2022-06 label EA/inflation                           mine=同步                       claim=同步                   OK
   2022-06 label EA/policy                              mine=分化                       claim=分化                   OK
   2022-06 label JP/growth                              mine=同步                       claim=同步                   OK
   2022-06 label JP/inflation                           mine=同步                       claim=同步                   OK
   2022-06 label JP/policy                              mine=分化                       claim=分化                   OK
   2022-06 number of synchronized cells (of 9)          mine=5                        claim=5                    OK
   2023-10 US/growth anchor-3 obs date                  mine=2023-04-01               claim=2023-04-01           OK
   2023-10 US/growth anchor-3 value                     mine=2.736                    claim=2.736                OK
   2023-10 US/growth anchor-3 pub date                  mine=2023-07-29               claim=2023-07-29           OK
   2023-10 US/growth cutoff obs date                    mine=2023-07-01               claim=2023-07-01           OK
   2023-10 US/growth cutoff value                       mine=3.1839                   claim=3.1839               OK
   2023-10 US/growth cutoff pub date                    mine=2023-10-29               claim=2023-10-29           OK
   2023-10 US/inflation anchor-3 obs date               mine=2023-06-01               claim=2023-06-01           OK
   2023-10 US/inflation anchor-3 value                  mine=3.0706                   claim=3.0706               OK
   2023-10 US/inflation anchor-3 pub date               mine=2023-07-13               claim=2023-07-13           OK
   2023-10 US/inflation cutoff obs date                 mine=2023-09-01               claim=2023-09-01           OK
   2023-10 US/inflation cutoff value                    mine=3.6872                   claim=3.6872               OK
   2023-10 US/inflation cutoff pub date                 mine=2023-10-13               claim=2023-10-13           OK
   2023-10 US/policy anchor-3 obs date                  mine=2023-07-31               claim=2023-07-31           OK
   2023-10 US/policy anchor-3 value                     mine=5.5                      claim=5.5                  OK
   2023-10 US/policy anchor-3 pub date                  mine=2023-07-31               claim=2023-07-31           OK
   2023-10 US/policy cutoff obs date                    mine=2023-10-31               claim=2023-10-31           OK
   2023-10 US/policy cutoff value                       mine=5.5                      claim=5.5                  OK
   2023-10 US/policy cutoff pub date                    mine=2023-10-31               claim=2023-10-31           OK
   2023-10 CN/growth anchor-3 obs date                  mine=2023-07-01               claim=2023-07-01           OK
   2023-10 CN/growth anchor-3 value                     mine=49.3                     claim=49.3                 OK
   2023-10 CN/growth anchor-3 pub date                  mine=2023-07-30               claim=2023-07-30           OK
   2023-10 CN/growth cutoff obs date                    mine=2023-10-01               claim=2023-10-01           OK
   2023-10 CN/growth cutoff value                       mine=49.5                     claim=49.5                 OK
   2023-10 CN/growth cutoff pub date                    mine=2023-10-30               claim=2023-10-30           OK
   2023-10 CN/inflation anchor-3 obs date               mine=2023-06-01               claim=2023-06-01           OK
   2023-10 CN/inflation anchor-3 value                  mine=0.0                      claim=0                    OK
   2023-10 CN/inflation anchor-3 pub date               mine=2023-07-09               claim=2023-07-09           OK
   2023-10 CN/inflation cutoff obs date                 mine=2023-09-01               claim=2023-09-01           OK
   2023-10 CN/inflation cutoff value                    mine=0.0                      claim=0                    OK
   2023-10 CN/inflation cutoff pub date                 mine=2023-10-09               claim=2023-10-09           OK
   2023-10 CN/policy anchor-3 obs date                  mine=2023-07-20               claim=2023-07-20           OK
   2023-10 CN/policy anchor-3 value                     mine=3.55                     claim=3.55                 OK
   2023-10 CN/policy anchor-3 pub date                  mine=2023-07-20               claim=2023-07-20           OK
   2023-10 CN/policy cutoff obs date                    mine=2023-10-20               claim=2023-10-20           OK
   2023-10 CN/policy cutoff value                       mine=3.45                     claim=3.45                 OK
   2023-10 CN/policy cutoff pub date                    mine=2023-10-20               claim=2023-10-20           OK
   2023-10 EA/growth anchor-3 obs date                  mine=2023-01-01               claim=2023-01-01           OK
   2023-10 EA/growth anchor-3 value                     mine=1.22                     claim=1.22                 OK
   2023-10 EA/growth anchor-3 pub date                  mine=2023-05-05               claim=2023-05-05           OK
   2023-10 EA/growth cutoff obs date                    mine=2023-04-01               claim=2023-04-01           OK
   2023-10 EA/growth cutoff value                       mine=0.48                     claim=0.48                 OK
   2023-10 EA/growth cutoff pub date                    mine=2023-08-04               claim=2023-08-04           OK
   2023-10 EA/inflation anchor-3 obs date               mine=2023-07-01               claim=2023-07-01           OK
   2023-10 EA/inflation anchor-3 value                  mine=5.3                      claim=5.3                  OK
   2023-10 EA/inflation anchor-3 pub date               mine=2023-07-31               claim=2023-07-31           OK
   2023-10 EA/inflation cutoff obs date                 mine=2023-10-01               claim=2023-10-01           OK
   2023-10 EA/inflation cutoff value                    mine=2.9                      claim=2.9                  OK
   2023-10 EA/inflation cutoff pub date                 mine=2023-10-31               claim=2023-10-31           OK
   2023-10 EA/policy anchor-3 obs date                  mine=2023-06-21               claim=2023-06-21           OK
   2023-10 EA/policy anchor-3 value                     mine=4.0                      claim=4                    OK
   2023-10 EA/policy anchor-3 pub date                  mine=2023-06-21               claim=2023-06-21           OK
   2023-10 EA/policy cutoff obs date                    mine=2023-09-20               claim=2023-09-20           OK
   2023-10 EA/policy cutoff value                       mine=4.5                      claim=4.5                  OK
   2023-10 EA/policy cutoff pub date                    mine=2023-09-20               claim=2023-09-20           OK
   2023-10 JP/growth anchor-3 obs date                  mine=2023-01-01               claim=2023-01-01           OK
   2023-10 JP/growth anchor-3 value                     mine=2.06                     claim=2.06                 OK
   2023-10 JP/growth anchor-3 pub date                  mine=2023-05-15               claim=2023-05-15           OK
   2023-10 JP/growth cutoff obs date                    mine=2023-04-01               claim=2023-04-01           OK
   2023-10 JP/growth cutoff value                       mine=1.17                     claim=1.17                 OK
   2023-10 JP/growth cutoff pub date                    mine=2023-08-14               claim=2023-08-14           OK
   2023-10 JP/inflation anchor-3 obs date               mine=2023-06-01               claim=2023-06-01           OK
   2023-10 JP/inflation anchor-3 value                  mine=3.3                      claim=3.3                  OK
   2023-10 JP/inflation anchor-3 pub date               mine=2023-07-20               claim=2023-07-20           OK
   2023-10 JP/inflation cutoff obs date                 mine=2023-09-01               claim=2023-09-01           OK
   2023-10 JP/inflation cutoff value                    mine=3.05                     claim=3.05                 OK
   2023-10 JP/inflation cutoff pub date                 mine=2023-10-20               claim=2023-10-20           OK
   2023-10 JP/policy anchor-3 obs date                  mine=2023-06-01               claim=2023-06-01           OK
   2023-10 JP/policy anchor-3 value                     mine=-0.066                   claim=-0.066               OK
   2023-10 JP/policy anchor-3 pub date                  mine=2023-07-05               claim=2023-07-05           OK
   2023-10 JP/policy cutoff obs date                    mine=2023-09-01               claim=2023-09-01           OK
   2023-10 JP/policy cutoff value                       mine=-0.054                   claim=-0.054               OK
   2023-10 JP/policy cutoff pub date                    mine=2023-10-05               claim=2023-10-05           OK
   2023-10 label CN/growth                              mine=同步                       claim=同步                   OK
   2023-10 label CN/inflation                           mine=分化                       claim=分化                   OK
   2023-10 label CN/policy                              mine=分化                       claim=分化                   OK
   2023-10 label EA/growth                              mine=分化                       claim=分化                   OK
   2023-10 label EA/inflation                           mine=分化                       claim=分化                   OK
   2023-10 label EA/policy                              mine=分化                       claim=分化                   OK
   2023-10 label JP/growth                              mine=分化                       claim=分化                   OK
   2023-10 label JP/inflation                           mine=分化                       claim=分化                   OK
   2023-10 label JP/policy                              mine=分化                       claim=分化                   OK
   2023-10 number of synchronized cells (of 9)          mine=1                        claim=1                    OK
### misc: JP policy path facts quoted in turnings[2]
   JP_POLICY_RATE 2025-11 = 0.478                       mine=0.478                    claim=0.478                OK
   JP_POLICY_RATE 2025-12 = 0.557                       mine=0.557                    claim=0.557                OK
   JP_POLICY_RATE 2026-10 = 1.227                       mine=1.227                    claim=1.227                OK
   net 2025-11 -> 2026-10 (bp)                          mine=75                       claim=75                   OK
   net 2025-12 -> 2026-10 (bp)                          mine=67                       claim=67                   OK
   JP CPI 2026-07 = 1.97                                mine=1.97                     claim=1.97                 OK
   JP CPI 2026-10 = 2.44                                mine=2.44                     claim=2.44                 OK
   JP CPI 2026-03 = 1.46                                mine=1.46                     claim=1.46                 OK
   JP CPI 2026-04 = 1.38                                mine=1.38                     claim=1.38                 OK
   CN overnight 1.25 @ 2026-11-23                       mine=1.25                     claim=1.25                 OK
   CN overnight latest                                  mine=('2026-11-23', 1.25)     claim=('2026-11-23', 1.25) OK
   CN_OMO_7D last obs                                   mine=('2026-10-30', 1.4)      claim=('2026-10-30', 1.4)  OK
   lag days CN_OMO_7D                                   mine=24                       claim=24                   OK
   CN_LPR_1Y last obs                                   mine=('2026-11-20', 3.0)      claim=('2026-11-20', 3.0)  OK
```

(A.5 小计: 397 点, 1 不一致)

### A.6 s15b_misc.py — 出处键: report.json /agent_judgment/contract_verification、/steps 相似检索面、gate + 快照 gate_a + 冻结日历 + 指标注册表 + agent_judgment.json /l3、/l4、quality_gate_notes

```text
### ⑪ Gate A vs judgment quality note (report.json gate + snapshot gate_a)
   core_missing count                                         mine=0                              claim=0                        OK
   noncore_missing list (7)                                   mine=['BUND_10Y', 'BUND_2Y', 'CN_OMO_7D', 'CN_POLICY_OVERNIGHT', 'EA_REAL_GDP_YOY', 'JP_CPI_TOKYO_YOY', 'JP_REAL_GDP_YOY'] claim=['BUND_10Y', 'BUND_2Y', 'CN_OMO_7D', 'CN_POLICY_OVERNIGHT', 'EA_REAL_GDP_YOY', 'JP_CPI_TOKYO_YOY', 'JP_REAL_GDP_YOY'] OK
   noncore_degraded list (8)                                  mine=['CN_SF_FLOW', 'ECB_DFR', 'ECB_MRO', 'JTSJOL', 'M2SL', 'SPX_EPS', 'SPX_PE_TTM', 'US_REAL_GDP'] claim=['CN_SF_FLOW', 'ECB_DFR', 'ECB_MRO', 'JTSJOL', 'M2SL', 'SPX_EPS', 'SPX_PE_TTM', 'US_REAL_GDP'] OK
   missing metrics with stock observations in series_store (5) mine=['CN_OMO_7D', 'CN_POLICY_OVERNIGHT', 'EA_REAL_GDP_YOY', 'JP_CPI_TOKYO_YOY', 'JP_REAL_GDP_YOY'] claim=['CN_OMO_7D', 'CN_POLICY_OVERNIGHT', 'EA_REAL_GDP_YOY', 'JP_CPI_TOKYO_YOY', 'JP_REAL_GDP_YOY'] OK
   JP_POLICY_TARGET in series_store                           mine=False                          claim=False                    OK
   JP_POLICY_TARGET in metric registry                        mine=False                          claim=False                    OK
   JGB series in series_store                                 mine=[]                             claim=[]                       OK
   JGB single-point facts                                     mine=3                              claim=3                        OK
### evidence_refs counts (judgment)
   L3 refs incl. mechanism chains (judgment: 41)              mine=41                             claim=41                       OK
   L3 + L4 refs (judgment: 50)                                mine=50                             claim=50                       OK
   distinct refs (20)                                         mine=20                             claim=20                       OK
   every L3/L4 ref resolves to an observation in series_store (metric@date) mine=[]                             claim=[]                       OK
   L3 competing explanations per statement (3/2/3)            mine=[3, 2, 3]                      claim=[3, 2, 3]                OK
### ⑧ analog dims / diffs for 2022-06 and 2023-10 (report.json steps[61] S6_analog)
   top[1] month                                               mine=2022-06                        claim=2022-06                  OK
   top[1] distance                                            mine=0.7918                         claim=0.7918                   OK
   top[1] percentile                                          mine=1.37                           claim=1.37                     OK
   top[1] share rates                                         mine=51.9                           claim=51.9                     OK
   top[1] share valuation                                     mine=33.6                           claim=33.6                     OK
   top[1] share inflation                                     mine=11.4                           claim=11.4                     OK
   top[1] share volatility                                    mine=3.0                            claim=3.0                      OK
   top[2] month                                               mine=2023-10                        claim=2023-10                  OK
   top[2] distance                                            mine=1.0542                         claim=1.0542                   OK
   top[2] percentile                                          mine=30.14                          claim=30.14                    OK
   top[2] share volatility                                    mine=60.1                           claim=60.1                     OK
   top[2] share valuation                                     mine=21.2                           claim=21.2                     OK
   top[2] share rates                                         mine=11.0                           claim=11.0                     OK
   top[2] share inflation                                     mine=7.7                            claim=7.7                      OK
### publication-visibility claims (TR1 link 2 / M1 step 2) — rule dates from planner RELEASE_RULES + weekday
   CPI 2026-04 rule publication date                          mine=2026-05-13                     claim=2026-05-13               OK
   CPI 2026-05 rule publication date                          mine=2026-06-13                     claim=2026-06-13               OK
   CPI 2026-05 rule date weekday                              mine=Sat                            claim=Sat                      OK
   CPI 2026-07 rule publication date                          mine=2026-08-13                     claim=2026-08-13               OK
   CPI 2026-08 rule publication date                          mine=2026-09-13                     claim=2026-09-13               OK
   CPI 2026-08 rule date weekday                              mine=Sun                            claim=Sun                      OK
   CPI 2026-09 rule publication date                          mine=2026-10-13                     claim=2026-10-13               OK
   CORE_PCE 2026-07 rule publication date                     mine=2026-08-30                     claim=2026-08-30               OK
   CORE_PCE 2026-07 rule date weekday                         mine=Sun                            claim=Sun                      OK
   EA_HICP_YOY 2026-04 rule publication date                  mine=2026-05-16                     claim=2026-05-16               OK
   EA_HICP_YOY 2026-07 rule publication date                  mine=2026-08-16                     claim=2026-08-16               OK
   EA_HICP_YOY 2026-08 rule publication date                  mine=2026-09-16                     claim=2026-09-16               OK
   JP_CPI_YOY 2026-07 rule publication date                   mine=2026-08-20                     claim=2026-08-20               OK
   CPI latest visible obs month before 2026-06-11             mine=2026-04                        claim=2026-04                  OK
   CPI latest visible value before 2026-06-11                 mine=3.78                           claim=3.78                     OK
   CPI latest visible obs month before 2026-09-10             mine=2026-07                        claim=2026-07                  OK
   CPI latest visible value before 2026-09-10                 mine=3.3                            claim=3.3                      OK
   CPI latest visible obs month before 2026-09-16             mine=2026-08                        claim=2026-08                  OK
   CPI latest visible value before 2026-09-16                 mine=3.35                           claim=3.35                     OK
   CPI latest visible obs month before 2026-09-18             mine=2026-08                        claim=2026-08                  OK
   CPI latest visible value before 2026-09-18                 mine=3.35                           claim=3.35                     OK
   CORE_PCE latest visible obs month before 2026-09-16        mine=2026-07                        claim=2026-07                  OK
   CORE_PCE latest visible value before 2026-09-16            mine=3.0                            claim=3.0                      OK
   EA_HICP_YOY latest visible obs month before 2026-06-11     mine=2026-04                        claim=2026-04                  OK
   EA_HICP_YOY latest visible value before 2026-06-11         mine=3.0                            claim=3.0                      OK
   EA_HICP_YOY latest visible obs month before 2026-09-10     mine=2026-07                        claim=2026-07                  OK
   EA_HICP_YOY latest visible value before 2026-09-10         mine=2.9                            claim=2.9                      OK
   JP_CPI_YOY latest visible obs month before 2026-09-18      mine=2026-07                        claim=2026-07                  OK
   JP_CPI_YOY latest visible value before 2026-09-18          mine=1.97                           claim=1.97                     OK
   CPI 2026-09 yoy published after the Sept decisions (2026-10-13 > 2026-09-18) mine=False                          claim=False                    OK
   EA HICP 2026-08 not visible at 2026-09-10                  mine=False                          claim=False                    OK
   EA HICP 2026-08 visible at 2026-09-16                      mine=True                           claim=True                     OK
   CPI 2026-05 yoy 4.17                                       mine=4.17                           claim=4.17                     OK
   CPI 2026-09 yoy 3.72                                       mine=3.72                           claim=3.72                     OK
   CPI 2026-10 yoy missing base                               mine=None                           claim=None                     OK
   CPI 2026-11 yoy base (2025-11 level) present               mine=True                           claim=True                     OK
   CPI 2025-10 level absent                                   mine=None                           claim=None                     OK
   CORE_PCE 2026-05 yoy 3.16                                  mine=3.16                           claim=3.16                     OK
   CORE_PCE 2026-07 yoy 3.00                                  mine=3.0                            claim=3.0                      OK
   CORE_PCE 2026-09 yoy 3.12                                  mine=3.12                           claim=3.12                     OK
   CORE_CPI 2026-02 yoy 2.47                                  mine=2.47                           claim=2.47                     OK
   CORE_CPI 2026-05 yoy 2.82                                  mine=2.82                           claim=2.82                     OK
### policy date conventions (TR1 link 2)
   ECB decision = previous Thursday of 2026-06-17             mine=2026-06-11                     claim=2026-06-11               OK
   ECB decision = previous Thursday of 2026-09-16             mine=2026-09-10                     claim=2026-09-10               OK
   Fed decision = effective minus 1 day of 2026-09-17         mine=2026-09-16                     claim=2026-09-16               OK
   Fed decision = effective minus 1 day of 2025-12-11         mine=2025-12-10                     claim=2025-12-10               OK
   ECB_DFR 2026-06-17                                         mine=2.25                           claim=2.25                     OK
   ECB_DFR 2026-09-16                                         mine=2.5                            claim=2.5                      OK
   ECB_DFR level in force before 2026-06-17                   mine=2.0                            claim=2.0                      OK
   ECB_DFR policy-window net change (2.0 -> 2.5) bp           mine=50                             claim=50                       OK
   ECB_MRO policy-window net change bp                        mine=50                             claim=50                       OK
   DFF change 2025-12-11 (bp)                                 mine=-25                            claim=-25                      OK
   DFF change 2026-09-17 (bp)                                 mine=25                             claim=25                       OK
   DFEDTARU 2025-12-11 ->                                     mine=3.75                           claim=3.75                     OK
   DFEDTARU 2026-09-17 ->                                     mine=4.0                            claim=4.0                      OK
### BOJ calendar entries (frozen calendar)
   BOJ entries count                                          mine=2                              claim=2                        OK
   BOJ decision date                                          mine=2026-09-18                     claim=2026-09-18               OK
   BOJ effective date                                         mine=2026-09-24                     claim=2026-09-24               OK
   BOJ target_value                                           mine=1.25                           claim=1.25                     OK
   Fed minutes entry published 2026-11-18                     mine=[]                             claim=[]                       OK
### misc series facts quoted in TR links / C1
   BEI_10Y 2026-06-10 = 2.34                                  mine=2.34                           claim=2.34                     OK
   BRENT_F 2026-06 month-end 72.92                            mine=72.92                          claim=72.92                    OK
   BRENT_F 2026-02 month-end 72.48                            mine=72.48                          claim=72.48                    OK
   EA HICP 2026-10 is window max (4.0)                        mine=('2026-10', 4.0)               claim=('2026-10', 4.0)         OK
   CN PPI 2026-10 is window max (5.7)                         mine=('2026-10', 5.7)               claim=('2026-10', 5.7)         OK
   CN PPI window min                                          mine=('2025-11', -2.2)              claim=('2025-11', -2.2)        OK
   CN CPI window min (anchor 12m ago 2025-10 = 0.2)           mine=0.2                            claim=0.2                      OK
   CN CPI window max date/value                               mine=('2026-02-01', 1.3)            claim=('2026-02-01', 1.3)      OK
   CN CPI 3m-ago anchor (2026-07 = 0.5)                       mine=0.5                            claim=0.5                      OK
   CN PPI swing pp (window min->max)                          mine=7.9                            claim=7.9                      OK
   largest price swing among listed price metrics is CN_PPI_YOY mine=CN_PPI_YOY                     claim=CN_PPI_YOY               OK
   CPI yoy latest (2026-09) vs year-earlier (2025-09): higher mine=True                           claim=True                     OK
   CN overnight: first obs                                    mine=('2026-11-02', 1.25)           claim=('2026-11-02', 1.25)     OK
   CN overnight: all values 1.25                              mine=[1.25]                         claim=[1.25]                   OK
   CN overnight: last obs                                     mine=('2026-11-23', 1.25)           claim=('2026-11-23', 1.25)     OK
   CN_OMO_7D window values                                    mine=[1.4]                          claim=[1.4]                    OK
   CN_LPR_1Y window values                                    mine=[3.0]                          claim=[3.0]                    OK
   CN_NEW_LOANS last obs                                      mine=2026-10                        claim=2026-10                  OK
### ⑨ scenario thresholds vs cutoff readings
   SCN1 trigger: latest CPI yoy (2026-09) >= 3.5 (not yet triggered for 2026-11/12; pending) mine=3.72                           claim=3.72                     OK
   SCN1 falsification not met: CPI yoy >= 2.5                 mine=True                           claim=True                     OK
   SCN1 falsification not met: CORE_PCE yoy >= 2.8            mine=True                           claim=True                     OK
   SCN2 falsification not met: BEI_10Y latest >= 1.8          mine=('2026-11-20', 2.15)           claim=('2026-11-20', 2.15)     OK
   SCN2 falsification arithmetic: 2.15 - 1.77 (bp)            mine=38                             claim=38                       OK
   SCN2 threshold distance: 2.15 - 1.80 (bp)                  mine=35                             claim=35                       OK
   M1 step 4 falsification not met: HY_OAS latest < 4.61      mine=True                           claim=True                     OK
   SCN1 deadline                                              mine=2027-02-28                     claim=2027-02-28               OK
   SCN2 deadline                                              mine=2027-02-28                     claim=2027-02-28               OK
### ① cutoff / ⑫ time conversions
   snapshot research_as_of                                    mine=2026-11-23T22:53:47+08:00      claim=2026-11-23T22:53:47+08:00 OK
   snapshot target_date                                       mine=20261123                       claim=20261123                 OK
   cutoff in New York (EST, UTC-5)                            mine=09:53                          claim=09:53                    OK
   cutoff in Frankfurt (CET, UTC-1)                           mine=15:53                          claim=15:53                    OK
   cutoff in Tokyo (JST, UTC+9)                               mine=23:53                          claim=23:53                    OK
   cutoff in Shanghai (CST, UTC+8)                            mine=22:53                          claim=22:53                    OK
   no cited daily series has observations after the cutoff date mine=[]                             claim=[]                       OK
   latest observation date anywhere in series_store <= cutoff mine=True                           claim=True                     OK
```

(A.6 小计: 122 点, 0 不一致)

### A.7 s26_final.py — 出处键: AGENT_SEAT_ENVELOPE.json /reader_map_contract/engine_faces/turning_candidates_top9 + 快照 series_store(CN_PPI_YOY/CN_PMI_MFG/BEI_10Y) + agent_judgment.json 原句 + MAP_REPORT.md/FULL_REPORT.md/MAP_REPORT.sha256 + report.json 附件记录与契约验证

```text
### (C) turning-candidate face rank (judgment reader_map.turnings[1].first_mover: 候选面全体首位为中国制造业PMI，增量3.40)
   CN_PPI_YOY 2026-02 (face value_before)                             mine=-0.9                       claim=-0.9                   OK
   CN_PPI_YOY 2026-05 (face value_after)                              mine=3.9                        claim=3.9                    OK
   CN_PPI_YOY delta recomputed (face 4.8)                             mine=4.8                        claim=4.8                    OK
   CN_PMI_MFG yoy% 2026-02 (face -2.3904)                             mine=-2.390438247011961         claim=-2.3904                OK
   CN_PMI_MFG yoy% 2026-05 (face 1.0101)                              mine=1.0101010101010166         claim=1.0101                 OK
   CN_PMI_MFG delta recomputed (face 3.4005)                          mine=3.4005                     claim=3.4005                 OK
   face first row metric (judgment: 中国制造业PMI)                         mine=CN_PPI_YOY                 claim=CN_PMI_MFG             <<< MISMATCH
   face is sorted by |delta| descending                               mine=True                       claim=True                   OK
   largest |delta| row in face is also first row                      mine=CN_PPI_YOY                 claim=CN_PPI_YOY             OK
### (B) CN_PPI_YOY path after the window low (judgment: 中国 PPI 低点在 2025-11 且此后连升)
   window low month (judgment 2025-11)                                mine=2025-11                    claim=2025-11                OK
   window low value                                                   mine=-2.2                       claim=-2.2                   OK
   number of monthly declines after the low (judgment '连升' = 0)       mine=1                          claim=0                      <<< MISMATCH
### (A) BEI_10Y threshold sentence (judgment l4.scenarios[SCN2].falsification.threshold)
   last obs below 1.8 date (judgment 2020-11-30)                      mine=2020-11-30                 claim=2020-11-30             OK
   last obs below 1.8 value (judgment 1.77)                           mine=1.77                       claim=1.77                   OK
   latest BEI_10Y date (judgment 2026-11-20)                          mine=2026-11-20                 claim=2026-11-20             OK
   latest BEI_10Y value (judgment 2.15)                               mine=2.15                       claim=2.15                   OK
   latest minus last-below reading, bp (judgment 低 35 个基点)            mine=38.0                       claim=35                     <<< MISMATCH
   latest minus threshold 1.8, bp                                     mine=35.0                       claim=35                     OK
### rendering / delivery face
   SCN2 falsification threshold sentence rendered verbatim in MAP_REPORT.md mine=True                       claim=True                   OK
   turnings[0].first_mover rendered verbatim in MAP_REPORT.md         mine=True                       claim=True                   OK
   turnings[1].first_mover rendered verbatim in MAP_REPORT.md         mine=True                       claim=True                   OK
   C1 explanation B rendered verbatim in FULL_REPORT.md               mine=True                       claim=True                   OK
   SCN2 falsification threshold sentence rendered verbatim in FULL_REPORT.md mine=True                       claim=True                   OK
   C1 statement rendered verbatim in FULL_REPORT.md                   mine=True                       claim=True                   OK
   MAP_REPORT.md sha256 == sidecar MAP_REPORT.sha256                  mine=True                       claim=True                   OK
   contract verdicts count                                            mine=14                         claim=14                     OK
   contract verdicts not VERIFIED                                     mine=[]                         claim=[]                     OK
   six_checks not VERIFIED                                            mine=[]                         claim=[]                     OK
   map_checks not VERIFIED                                            mine=[]                         claim=[]                     OK
   semantic_review.seat_invoked (verdict-absent render expected)      mine=False                      claim=False                  OK
   semantic_review.verdict                                            mine=None                       claim=None                   OK
   attach record attached_at (file mtime 06:40:04 HKT)                mine=20261123T224004Z           claim=20261123T224004Z       OK
```

(A.7 小计: 32 点, 3 不一致)

### A.8 s33_cov.py — 出处键: report.json /steps[61](S6_analog)/envelope/data/state_vector/<dim>/coverage 与 /top[*](候选月缺失特征) + agent_judgment.json /l3/contradictions[1]/competing_explanations[1]

```text
### C2 explanation B: state-vector coverage (report.json /steps[61]/envelope/data/state_vector/<dim>/coverage)
   growth coverage (judgment 0.17)                              mine=0.1667         claim=0.17       OK
   inflation coverage (judgment 0.33)                           mine=0.3333         claim=0.33       OK
   credit coverage (judgment 0.5)                               mine=0.5            claim=0.5        OK
   credit features missing in majority of candidate months      mine=True           claim=True       OK
```

(A.8 小计: 4 点, 0 不一致)

附录合计: 1111 点, 8 不一致
