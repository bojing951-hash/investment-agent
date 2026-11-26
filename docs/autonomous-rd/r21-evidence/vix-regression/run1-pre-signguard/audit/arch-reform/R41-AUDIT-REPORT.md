# R41 独立审计报告(未参与席·四维对抗审查)

- **审计对象**: R41 波次 T8-R2 余留①②③(提交 53d480c 开轮 docs / 838c4ec 主工作 / d134e80 新套件 / fb8bf50 键数笔误修正;基点 2798d8a=main)
- **审计席**: 独立审计席(未参与开发;对抗式,不采信开发席任何声称,全部亲跑取证)
- **日期**: 2026-11-16(HKT)。分支 `dev/rd-r41-t8r2-leftovers`,工作树审计前净、审计后仅本文件未跟踪。
- **方法备注**: 审计脚本/旧引擎提取件均在 /tmp/r41audit 与 /tmp/t8_old(不进仓);三次变异拆装后 `git status` 还原为净。

---

## 维一: 代码正确性 — **通过(无阻断缺陷)**

### ③ spec 表逐位核对(亲跑,非采信)

- `SCORECARD_DIMENSIONS` 8 行×4 键与 `config/thresholds.json` 实存键**逐位相符**(键名拼写与数值序): std 行四键升序喂 `_score_band4(v,m1,m2,p1,p2)`——CORE_CPI(1.0/2.0/2.5/3.5)、BEI_10Y(1.5/2.0/2.3/2.6)、WTI_F(40/50/70/90)、AHE(2.0/3.0/3.5/4.5)、UMCSENT(50/60/80/95)、RSAFS(-1.0/-0.5/0.5/1.0)、INDPRO(-1.0/-0.3/0.3/1.0);UNEMPLOYMENT rev 行键序 (p05,p03,m01,m03)=(0.5,0.3,-0.1,-0.3) 与 `_score_band_rev` 形参序一致,与 `macro_scorecard` 引擎 `change>p05→-2 … >m03→+1 … else+2` 链同构。与 2798d8a 版 `_check_score_total` 旧字面枚举 diff 对照: **成员集与键序逐位等价**(旧 i_parts/g_parts 顺序 CORE_CPI/BEI_10Y/WTI_F/AHE + UMCSENT/UNEMPLOYMENT/RSAFS/INDPRO 与新表行序相同,unemployment 四键旧代码即按 p05,p03,m01,m03 位传参)。
- `macro_scorecard.SCORECARD_THRESHOLD_KEYS` 新推导式 = `threshold_keys()∪REGIME(2)∪EXTRA(1)` = 35 键,与旧字面 35 键集合相等(S2 判+我方独立 dump 比对);注册表 `ism_pmi.scorecard.*` 4 键 status=pending,G2 显式豁免列出——非本轮引入,语义原样。
- G2 门: 亲跑 `python3 scripts/thresholds_gate.py` **全绿(G1-G4 PASS)**。新 spec_src 解析三处(维度行键正则 `[a-z0-9_]*\.scorecard\.[a-z0-9_.]+` / REGIME 元组 / EXTRA 元组)现源码无非法键混入;diff-set 四向断言(used-declared / declared-used / declared-all_keys / fam-declared)语义原样;t1t2 随迁变异 3 判绿。

### 自建对抗(全部我方独立脚本,非复用开发席测试)

- **双侧同分**: 120 组随机合成快照(每指标候选=五带中点+四个边界精确值,覆盖 -2..2 全带位与左开右闭边界)——`tc._check_score_total`(经 `check_text`)复算 expected 与 `macro_scorecard.score_inflation/score_growth` 总分 **120/120 全等**;claimed≠expected→CONTRADICTED、claimed=expected→VERIFIED 状态逻辑正确;五带位专项(8 指标同带→i_total=g_total=4b)全对。
- **部分缺失**: 逐指标摘除×8——tc=INSUFFICIENT_EVIDENCE(`成分缺失不计0分: [<mid>]`)+ms=部分分照判+missing 清单披露该指标+**对侧维度复算不受扰**,与 S4 锁定语义一致(该差异为既有双引擎语义,非本轮引入,报告已如实声明)。
- **键摘除 fail-closed**: 从 thresholds 逐个剔 `core_cpi.scorecard.m1`/`unemployment_3m.scorecard.p03`/`ahe.scorecard.p45` → tc 该维拒判(INSUFFICIENT),0 漏。
- **co_anchor 后置段**: 只加 `co_anchor` 字段+note 定长后缀,不改任何 status/note 前缀/统计(维三双跑逐位证);`_check_band_label` 对 mid 空值早退 → band_label 检查 metric 恒非 None,`None in _lvl_contra_mids` 误标结构性不可能。

---

## 维二: 诚实纪律(重点①裁定面) — **通过(全部亲证,零真错声明经受住对抗)**

### 亲跑复跑器

- `python3 tests/r41_realface_runner.py`: **V1 contra=53 / V2=175 / V3=98,delta=0**,与在库工件 runs 面一致;新写出 JSON 的 runs 节与提交版工件 runs 节**逐位相同**(diff 仅开发席另注的 adjudication 节;已 git 还原在库版)。工件在库形态与 R1 三判(326 全簇/簇数和=contra/A 族≥150 居首)自洽,rollup 154+40+38+28+23+16+13+5+5+4=326。

### 裁定抽样对抗(13 簇 ≥4/报告,含点名挑战样例;报告原文亲读+数值亲算)

| 报告 | 簇(族,n) | 我方独立复核结论 |
|---|---|---|
| V1 | level\|ZQ_IMPLIED_AVG(C,10) | 路径各月值 3.8775/4.07/4.165/4.57/4.715 均显式标注合约月(报告:19/109/159 行);4.165=快照 ZQ 事实值(2027-01 合约)自吻合;升幅 4.715−3.8775=0.8375≈「约0.84pp」亲算无误;`8775%`=小数误切分碎片。**FP 成立** |
| V1 | level\|WTI_F(D,6) | 7.16=布伦特96.08−WTI88.92 亲算精确;102.07=现货月均(2026-10)显式口径披露,偏差 (88.92−102.07)/102.07=−12.88% 亲算吻合。**FP 成立** |
| V1 | level\|REAL_10Y(B,4) | +0.23pp=表格周变化列+贡献分解(0.23+0.01=0.24=名义10Y+0.24pp 恒等亲核);水平句 2.86% 与快照 2.86@2026-11-12 一致。**FP 成立** |
| V1 | scorecard_total(I,1) | 「通胀总分+4」出现于上期对比/回落叙事(报告:20/146 行);上期 V3 面(20261024)引擎自判 VERIFIED(+4),本期面 +2=CORE_CPI+1+BEI0+WTI+1+AHE0(亲复算),+4→+2 回落算术逐项吻合。**FP 成立** |
| V1 | narrative_direction(G,1) | 「是否…甚至倒挂」疑问推测语境,2s10s=0.27>0 非断言倒挂。**FP 成立** |
| V2 | level\|CORE_CPI(D,4)**[点名挑战]** | **挑战被驳回**: 2.5658=快照 derived m12 pct_change 原值(V2 面 fact obs 2026-09-01,338.896 为指数水平);表内 2.57%=2.5658 两位显示;+1=正确带分(2.5≤2.5658<3.5);1320bp=CCC 13.20%×100 精确换算(84/118/120 行)。**报告文本无误,FP 成立** |
| V2 | level\|WTI_F(A,22)**[最大簇]** | 22 token 逐类核: 星级碎片 3/4/6、阈值语境 90/85/100/110、评分列 +2(90.83≥90 正确)、7.49=98.32−90.83 亲算、102.07 口径差 −11.01% 亲算、0.83=90.83−90 亲算、48.1=UMCSENT 值串绑。**FP 成立** |
| V2 | level\|UST_30Y(G,4) | 4.5%=失效条件触发线(140 行);30Y 水平句 5.25% 与快照 5.25@2026-11-05 一致;5.25−5.0=25bp 亲核。**FP 成立** |
| V2 | level\|UNEMPLOYMENT(B,5) | 0.0pp=评分卡 m3 变化列、0=分值列;失业率水平句 4.1% 与快照一致;16.5万人=165,000 换算正确。**FP 成立** |
| V3 | threshold_constant(K,6)**[点名挑战]** | **挑战被驳回**: 5.29%=30Y 水平值近「红线」词误触(5.29−5.00=0.29pp 亲核);−0.14pp/−0.04pp=表列周变化;0.31%=2s10s 利差水平;报告另处「4.8%警戒线」与注册表 ust_30y.warning=4.8 吻合。**FP 成立** |
| V3 | level\|WTI_F(B,8) | +2=分值列(103.44≥90 正确);97.31=WTI 月均现货(9月,环比+15.98%)显式口径;85/90/110=触发线。**FP 成立** |
| V3 | level\|UMCSENT(G,3) | 50=<50 触发阈值、−2=分值列(48.1<50 带分正确);表内 48.1 与快照一致。**FP 成立** |
| V3 | level\|ZQ_IMPLIED_AVG(C,6) | 「从3.885%升至4.575%」=期货曲线逐月路径显式标注;约70bp=4.575−3.885=0.69 亲核。**FP 成立** |

抽样覆盖 A/B/C/D/G/I/K 七族,含两处点名挑战样例,均无法翻案——「326 全簇=误报,零真错」声明在我方对抗下成立。

### 零漂移与归因

- **零漂移**: 工件 `runs.*.baseline_stats` 与 `t7_results.json` `runs.*.new.stats` **逐位相同**(V1 221/53/165/113、V2 394/175/215/98、V3 229/98/130/47);基线已记录 40 行/报告(唯一三元组 33/39/38)**⊆ 当前全量,零消失**(机械核,missing=0)——与报告声明数字逐字吻合。
- **倒挂句非回归归因**: 亲跑 `/tmp/r41_attr.py` → 基线与当前同判 CONTRADICTED;且我方对 `/tmp/t8_engine` 三文件(text_consistency/fact_engine/claim_factory)与 `git show e81d363:` 对象做字节比对**全部相同**——归因实验的 e81d363 身份实证,报告§①「基线 e81d363 同判」表述与事实一致。
- 其他声明抽核: A 族 47%=154/326 ✓;全库 164 件 `ls tests/test_*.py | wc`=164 ✓;d134e80 所报 3 红(phase6+R20 两件)现均亲跑转绿(phase6 29/0、R20 三套 5/0+45/0+15/0)。

---

## 维三: 契约不变性 — **通过(逐位等价实证)**

- **受影响面七套件亲跑全绿**: t8r 31/0、t6c 26/0、phase4 57/0、t1t2 90/0、新套件 20/0、R38 34/0、R40 17/0。
- **新旧双跑对照**(2798d8a 旧引擎闭包提取至 /tmp/t8_old 含 config,真实 fixture `snapshot_20261114_v2.json` 面): 9 案例(总分正确句/错误句/成分缺失句/band 双报句/纯 band 句/band 绿句/别名双报/无总分句/总分+体制映射句)——`verdict`/`stats`/`unbound`/checks 列表**剥 co_anchor 字段+定长 note 后缀后逐位相同**;co_anchor 恰只落双报形态(band CONTRA+同指标 level CONTRA),纯 band/绿面零触碰;旧版零 co_anchor。
- **co_anchor 消费面**: 全库 grep(排除工件)消费方=runner 透传序列化+新套件断言;judgment_contract/render_hook 无封闭键集断言(phase4 57 判绿即证)。
- G2/状态门: `thresholds_gate.py` 亲跑全绿;`scripts/rd_state_consistency.py` 七项门 **7/7 PASS**(HEAD=fb8bf50,T-R41-1 台账进行中,账面自洽)。

---

## 维四: 测试真实性(变异自证,亲拆) — **通过(三拆两咬一披露)**

| 变异 | 做法(临时改,后还原) | 结果 |
|---|---|---|
| 拆② | co_anchor 后置段条件改永假(no-op) | **B1 第二判转红**(PASS=19 FAIL=1),套件对②有真牙 |
| 拆③ | spec AHE 行 `ahe.scorecard.m2`→`ahe.scorecard.mx2` | **套件红**: ms `load_thresholds` 缺键 fail-closed RuntimeError 于 S2 即截停(exit≠0,无「结果」行)——比预期「S3 转红」**更早更硬**;tc 侧键缺→INSUFFICIENT 路径由我方维一独立 D 试验单独证实(0 漏) |
| 拆 S3 双侧锁 | 3a: `TH('core_cpi.scorecard.p35')`→常量 2.9 | **S3 通胀判红(tc=2 ms=3)+连带 3 判红**(PASS=16 FAIL=4),双侧锁有真牙 |
| 同上 | 3b: WTI 带键换位(m40↔p70) | **S3 不转红**(见 MINOR-1: 合成 WTI 值饱和于+2 带位差不可见) |
| 还原 | 三次变异后 `git status` | 每次即还原,**树净** |

S5 拆接线变异(抽 AHE 行→CONTRA/还原复绿)为套件内置,亲读逻辑成立。

---

## 发现清单

### BLOCKER(0 条)

无。

### MAJOR(0 条)

无。

### MINOR(2 条)

1. **[MINOR-1] S3 合成快照 WTI_F=p90+1 饱和于 +2 带,WTI 带链位变异盲区**
   证据: 变异 3b(m40↔p70 换位)套件 20/0 全绿;3a(CORE_CPI p35→2.9,合成值 3.0 落变异带内)即红。
   影响: S3 对「合成值所在带」的 ms/tc 位差敏感,对其余带位的换位类漂移不设防。
   缓解在场的证据: 我方 120 组随机含边界双侧同分已覆盖该位差;G2 门锁键集。属测试敏感度改进项(合成值改取带间中点即可),非行为缺陷。

2. **[MINOR-2] 真实面复跑 checks 总数增长未入报告 prose**
   证据: V2 checks 394→397(+3)、V3 229→231(+2),contra/verified/unbound 逐位不变(增长=INSUFFICIENT 类行);工件 JSON 两套 stats 如实并存,报告§①表格仅列 contra 列。
   影响: 「基线零漂移」按 contra 定义成立且工件可复核,但非 contra 检查行增长(+5)宜一句话披露,防后续读者误读「零漂移=全量逐位」。

### NIT(3 条)

3. **[NIT-3] co_anchor 跨子句作用域**: 同指标 level CONTRA 在全文任意位置即触发全部 band_label CONTRA 标记,不限同子句/同值语境。advisory 字段+状态零变动,现形态可接受;后续硬化可收紧作用域。
4. **[NIT-4] g2 spec 元组解析脆弱性**: `REGIME/EXTRA_THRESHOLD_KEYS = \((.*?)\)` 非贪婪至首个右括号,元组内注释若含 `)` 将 AttributeError 崩——崩向=红(fail-closed 方向),可接受。
5. **[NIT-5] S2 的 `len(want)==35` 锚定 spec 自身推导**,套件内无注册表侧 35 键独立断言(由 G2 门差集与 ms fail-closed 双重兜底,冗余可接受)。

---

## 终判

**可并入。** 四维全部通过: ③单源化成员集/键序/行为逐位等价(120 组随机+边界双侧同分亲证);②状态零变动(新旧双跑逐位同);①裁定面经 13 簇含点名挑战的独立复核,「326 全簇误报、零真错、基线零漂移、倒挂句非回归」四项声明全部亲证成立;测试有真牙(变异三拆两咬)。两条 MINOR 均为改进登记项(S3 合成值去饱和、checks 增长披露),不构成并入条件;建议随 RDG-011 回看或下轮硬化(A 族注释/碎片预处理为已登记首位)一并处理。

*(本报告为独立审计席产出,只写工作区不入提交,落账由开发席负责。)*
