# T8 独立审计席报告 — 迁移门终裁(当众启封留出集)

- 报告时间: 2026-11-15 02:12:49 +0800
- 执行人: T8 独立审计席(无开发席上下文;零咨询;全部输出亲手复跑)
- 审计对象: dev/arch-reform-p3 @ 841e7c9(2026-11-15 02:06:50 +0800)
- 标尺: MIGRATION-CRITERIA-DRAFT.md v1.0(预固定 P1-P6)+ HELDOUT-PROTOCOL.md v1.0
- 纪律执行: 除本报告文件及其 commit 外零写入;未改任何代码/测试/夹具/LIVE 树;未 push;未 merge;未咨询开发席

---

## 1. 启封记录(append-only)

### 1.1 启封时点与前置条件确认

- 启封时点: 2026-11-15 02:12 +0800,公开面完整判定记录已由本席亲手复跑产出(§2 证据),符合协议 §4「唯一启封时点」。
- 执行人: 独立审计席(非开发席、非 QA 席)。
- **哈希核验在读取任何封存内容之前完成**(先 §1.2 后 §2 留出面判定与 §4 抽查读取)。

### 1.2 哈希核验输出(逐行)

文件级(shasum -a 256,实时复算 vs HELDOUT-MANIFEST.sha256):

```
9a15ab369ef2d9b7c067626c3c526e40f7978c6958ecb1f56324481e5f340c07  heldout-sealed/V5-HELDOUT.json   = 清单一致 MATCH
8370240d12c0ff6792d4711bcdbd765409c92cff3d21ae6dd086e5ce4b0a2347  heldout-sealed/V6-HELDOUT.json   = 清单一致 MATCH
```

条目级(协议 §2 公式复算,15/15):

```
eed4246f...346f1a  V5-S01   MATCH      d409319c...899a4  V6-S01   MATCH
74d94fdc...c4bd8e  V5-S02   MATCH      1341b1bb...19b7c  V6-S02   MATCH
87a9dfaa...93f29bb V5-S03   MATCH      36299dab...f9367  V6-S03   MATCH
d06dab7a...bc09b0  V5-S04   MATCH      fca090ee...b6a668  V6-S04   MATCH
e836aded...787968  V5-S05   MATCH      8715eaf9...b0cd1  V6-S05   MATCH
525fc53c...58bc4   V5-S06   MATCH      0801c66a...626b228 V6-S06  MATCH
b5b304f9...867d01  V5-S07   MATCH
2eeed8c5...b9f00   V5-S08   MATCH
d6ec6ab2...58623   V5-S09   MATCH
```

**结论: 文件级 2/2 + 条目级 15/15 全部匹配,封印完好,无破损事件(重大回归事件 6 未发生)。** 比对方式说明: 逐行 diff(manifest 双空格分隔,复算单空格,规范化分隔后 diff 零差异,各 15 行)。

### 1.3 留出面判定输出(逐行,与公开面完全相同的命令与配置)

命令: `python3 tests/run_matrix_dir.py <sealed.json>`(配置=migration_matrix.load(),与公开面同源;跑台代码 28 行确认)。

V5-HELDOUT(须 9/9 CONTRADICTED, unmapped=0):

```
[OK]  V5-S01/additivity_break+digit_error  want=CONTRADICTED got=CONTRADICTED   (contra=3 veri=1 unbound=0)
[BAD] V5-S02/band_threshold_error          want=CONTRADICTED got=INSUFFICIENT_EVIDENCE (contra=0 veri=0 unbound=1)
[OK]  V5-S03/sign_flip                     want=CONTRADICTED got=CONTRADICTED   (contra=1 veri=1 unbound=0)
[BAD] V5-S04/composite_score_error         want=CONTRADICTED got=INSUFFICIENT_EVIDENCE (contra=0 veri=0 unbound=2)
[BAD] V5-S05/additivity_break              want=CONTRADICTED got=INSUFFICIENT_EVIDENCE (contra=0 veri=0 unbound=6)
[BAD] V5-S06/narrative_contradiction       want=CONTRADICTED got=VERIFIED       (contra=0 veri=4 unbound=0)
[BAD] V5-S07/narrative_contradiction       want=CONTRADICTED got=VERIFIED       (contra=0 veri=2 unbound=0)
[OK]  V5-S08/window_confusion              want=CONTRADICTED got=CONTRADICTED   (contra=1 veri=0 unbound=0)
[BAD] V5-S09/forecast_conflation           want=CONTRADICTED got=INSUFFICIENT_EVIDENCE (contra=0 veri=0 unbound=0)
TOTAL 3/9 达标; unmapped=9
```

V6-HELDOUT(须 6/6 VERIFIED, unmapped=0):

```
[BAD] V6-S01 want=VERIFIED got=CONTRADICTED (contra=1 veri=1 unbound=1)
[BAD] V6-S02 want=VERIFIED got=CONTRADICTED (contra=1 veri=1 unbound=0)
[BAD] V6-S03 want=VERIFIED got=CONTRADICTED (contra=3 veri=1 unbound=0)
[BAD] V6-S04 want=VERIFIED got=CONTRADICTED (contra=1 veri=0 unbound=0)
[BAD] V6-S05 want=VERIFIED got=CONTRADICTED (contra=3 veri=0 unbound=0)
[BAD] V6-S06 want=VERIFIED got=CONTRADICTED (contra=2 veri=1 unbound=0)
TOTAL 0/6 达标; unmapped=1
unmapped 明细: [('V6-S01', '104 ')]
```

---

## 2. 判据逐项判定 + 证据

### 门禁与公开面(本席亲手复跑)

门禁七套(全部退出码 0): test_arch_reform_t1t2(90 PASS/0 FAIL)、t3_series(43/0)、t4_claims(115/0)、t5_verifier(46/0)、t6a_statistic(28/0)、t6b(20/0)、t6c(26/0)。

公开面: `python3 tests/migration_matrix.py` → **TOTAL ok=35 fail=0 / 35**(V5 21 条全 CONTRADICTED、V6 14 条全 VERIFIED、unbound 全 0)——与 T7-PARALLEL-RESULTS.md 声明一致,开发席公开面声明属实。

P4: `python3 tests/run_matrix_dir.py --p4` → **5/5 复位 VERIFIED**(滞后166天/距离0.80pp/DXY周+1.09%/VIX桥式+32.03%至25.64/顿号零售+0.77%)。

### P1 — V6 零误杀(公开+留出分计): **FAIL**

- 公开面 14/14 PASS ✓(本席复跑)。
- 留出面 **0/6**: 六条真值变体全部终态 CONTRADICTED,误杀 6 条,容许数 0,超标 6 条。
- 误杀机制逐条(本席取 checks 明细核实,数值真实性见 §4):

| 条目 | 误杀机制(绑定引擎缺陷定性) |
|---|---|
| V6-S01 | 阈值距离值 `0.59` 被绑 DXY **level** 检查(expected=103.41)→CONTRA;另 `104 `(阈值常数)unmapped |
| V6-S02 | 月换算约数 `约5`(个半月)的 `5` 被绑 SPX_EPS level(expected=295.3881)→CONTRA;166 天本身 VERIFIED |
| V6-S03 | `25bp/0.25pp` 红线距离被 threshold_constant 检查误 CONTRA;`5.25%`(20261108 锚集真值)对照 20261114 快照 UST_30Y=5.43 →CONTRA(锚集时点错配,见 §4) |
| V6-S04 | 可加性贡献集污染: 把分解目标 `+0.24pp` 也吞进贡献集,0.23+0.24+0.01=0.48 vs 0.23 →CONTRA(正确恒等式 0.23+0.01=0.24) |
| V6-S05 | 顿号枚举错位(T7 FK-2 同型): yoy 4.08 绑 CPI mom 检查(0.3503)、mom 0.35 与 yoy 2.87 绑 CORE_CPI mom 检查(0.2963)→三条 CONTRA |
| V6-S06 | 阈值 `90` 绑 WTI_F level(expected=88.92)→CONTRA;上期引用 103.44 不在 prior 锚链 [88.92,90.83,90.83,104.12] →prior_reference CONTRA |

### P2 — V5 拦截率 + 六族地板: **FAIL**

- 公开面 21/21 ≥ 20/21 ✓,六族公开面全中 ✓。
- 留出面 **3/9**(须 9/9=100%): S02/S04/S05/S09 终态 INSUFFICIENT_EVIDENCE,不属于拦截终态集合 {CONTRADICTED, SEMANTIC_REVIEW_REQUIRED, REVISE};S06/S07 终态 VERIFIED(见 P3)。
- **族地板击穿(留出面,两处)**:
  - 区间/阈值关系族(V5-016 族): V5-S02(HY OAS 320bp 标「恐慌区>500bp」频段错置)→ INSUFFICIENT_EVIDENCE,unbound `'500bp'`;
  - 分解可加性族(V5-009/010 族): V5-S05(情景概率和 35+35+25+15+5=115%≠100%)→ INSUFFICIENT_EVIDENCE,unbound 6 个百分号 token。
  - 判据原文:「这六族不依赖序列通道扩展,纯 Fact+注册表可判,漏任何一条=契约核心机制失效」。
- 机制定性: 公开面同族条目(如 V5-016/V5-009/010)通过,留出变体失败——留出变体的载体/数值形态(中文括号内 `>500bp`、竖线枚举概率)未被 text_consistency 映射,token 落 unbound→checks=0→INSUFFICIENT_EVIDENCE。属**形态过拟合**(协议 §5「先裁后看」所防范的形态,在留出面被测出)。

### P3 — 漏放=0(硬门): **FAIL**

- V5-S06(narrative_contradiction, fault-B 同族): 数值全对(DXY 103.41/+1.09%、EURUSD 1.11/−1.59%),叙事「美元走弱、欧元升值、压力缓解」与数值全部反向 → 新链判 **VERIFIED**(veri=4, contra=0)。
- V5-S07(narrative_contradiction): 0.27% 正利差却说「曲线倒挂加深,衰退信号强化」→ 新链判 **VERIFIED**(veri=2, contra=0)。
- 两面合计 30 条中 2 条以 VERIFIED 终态(S06 文本更以【事实】区标签开头)→ **漏放 2 条,硬门击穿,无豁免、无平均值救济**。
- 机制定性: 纯叙事-数值方向矛盾不在确定性检查器能力面;判据允许以 SEMANTIC_REVIEW_REQUIRED 拦截,但语义审查席阶段四才就位,当前链径直 VERIFIED。

### P4 — 真实历史重放(V1/V2 五值复位): **PASS**

本席亲手复跑 `run_matrix_dir.py --p4` → 5/5 全 VERIFIED(输出见上)。与 T7 声明一致。

### P5 — 文本一致性与白名单纪律: **FAIL(留出面口径)/ 公开面达标**

- 公开面 V6 14 条 unbound 全 0 ✓(migration_matrix 输出)。
- 留出面 V6-S01 存在未映射数值 token `'104 '` → 判据文字「V6 **全部**条目经 text_consistency 后未映射数值 token=0」未限定公开面,如实计 FAIL。
- 白名单: research_contract 五模块(claim_factory/claim_verifier/text_consistency/claim_bundle/render_hook)grep `whitelist|白名单|exempt` **零命中**——新链无白名单通道,新增=0 ✓。
- thresholds 注册表: 最后变更=96d265e(2026-11-14 21:12,T1 落盘,status=`v1.0-SIGNED: 金融席终签(2026-11-14)`),此后(含 T6c/T7/T8前置提交)零触碰,diff=0 ✓。

### P6 — CI 与冻结件: **PASS**

- 门禁七套退出码全 0(368 判定/0 FAIL)。
- 夹具冻结核验: 对 `audit/arch-reform/T7/t7_results.json` 的 `fixtures_sha256` 全部 13 件逐一重算(V1×2/V2×2/V3×1/V5×1/V6×1/V4×4/V7@f7a8d88×2,git 对象直读同法)→ **13/13 MATCH,零漂移**。
- 工作树干净(git status 零输出),分支 dev/arch-reform-p3。

---

## 3. 重大回归事件核对(判据 §2 六项)

| # | 事件 | 判定 | 证据 |
|---|---|---|---|
| 1 | V6 任何一条误杀(两面) | **发生** | 留出面 6/6 全 CONTRADICTED(§1.3) |
| 2 | V5 任何一条漏放(VERIFIED 入事实区) | **发生** | V5-S06/S07 终态 VERIFIED(§2 P3) |
| 3 | 白名单/阈值注册表未经签字变更 | 未发生 | thresholds 止于 96d265e v1.0-SIGNED;新链无白名单通道(§2 P5) |
| 4 | NOT_VERIFIABLE 的 model_inferred 数值 claim 直接发布 | 未发生(本轮证据面) | 本轮迁移门仅涉判定面(check_text),渲染/发布面未接入;V5-S04 模型观点条目被判 INSUFFICIENT 而非放行 |
| 5 | 状态漂移复发(故障C 同型) | 未发生(本轮证据面) | 状态语义一致性=V7@f7a8d88,DEFERRED_PHASE5,不在本轮判定面 |
| 6 | 封存哈希核验不匹配 | 未发生 | 文件级 2/2 + 条目级 15/15 全 MATCH(§1.2) |

事件 1、2 任一发生即「不迁移,重新审查设计」——两项均发生。

---

## 4. 独立抽查记录(防「歪打正着」,任务要求至少两项,实做四项)

### 4.1 V5-S01 注入偏差独立复算 vs CONTRA 机制核对 → **拦截成立,但机制歪打正着**

- 注入: SZ 分项 4,539.25→5,539.25。独立复算: 7,706.14+5,539.25=13,245.39 ≠ 总额 12,245.39,加总偏差 +1,000.00 亿(可加性破坏)。
- 检查器实际 CONTRA 三条全部是 **level 检查错绑**: 7,706.14亿/5,539.25亿/1万亿 均绑到 SZCI 上证指数水平(expected=10968.7872)——成交额与指数水平本就不同量纲,比对必然失败。
- **结论: 该条终态拦截成立(P2 终态口径),但未命中设计机制(可加性检查零 CONTRA),拦截依赖与 V6 误杀同源的绑定缺陷巧合命中。** 同一缺陷一面「凑成拦截」一面制造误杀,拦截质量打折,如实记录。

### 4.2 V5-S03 注入偏差独立复算 vs CONTRA 机制核对 → **机制精确命中**

- 注入: 周变化符号翻转(+24.73% vs 真 −24.73%)。独立复算: (19.30/25.64−1)×100 = **−24.727**%。
- 检查器 CONTRA: family=`change/week`, token=24.73%, value=24.73, expected=−24.727, note 含同位 4dp 复算公式 → **命中符号翻转机制本身,非巧合**。

### 4.3 V6-S05 数值 vs snapshot 独立复算 → **三值全部真实**

- CPI yoy: 快照 CPI@2026-10-01=337.476,m12 基准 324.245,(337.476/324.245−1)×100=**4.0806** → 条目 +4.08% ✓
- CPI mom: m1 基准 336.298,(337.476/336.298−1)×100=**0.3503** → 条目 +0.35% ✓
- CORE_CPI yoy: 339.9/330.418 独立复算=**2.8697** → 条目 +2.87% ✓
- 结论: 该条被 CONTRADICTED 是纯枚举错位误杀,数值本身无瑕——**排除了「留出集样本数值错误导致假误杀」的解释**。

### 4.4 V6-S06/V6-S03 数值真实性 + 锚配置覆盖核查

- V6-S06: 本期 WTI 88.92 与快照一致 ✓;上期 103.44 为真实报告(11-14 L20)引用过的 2026-10-23 口径真值,但跑台 prior 锚链仅含 [88.92, 90.83, 90.830002, 104.120003],103.44 缺席(prior 中出现的 103.44 是 DXY 的 high,非 WTI)→ prior_reference 误杀含**锚链覆盖不足**叠加因素;`90` 阈值绑 WTI level 的 CONTRA 是纯绑定缺陷。
- V6-S03: 5.25 为 anchors_20261108 的 UST_30Y 真值(2026-11-05),跑台快照(20261114)UST_30Y=5.43(2026-11-12)→ level CONTRA 含**锚集时点错配**叠加因素;25bp/0.25pp 的 threshold_constant CONTRA 是纯绑定缺陷。
- 责任分层结论: 6 条误杀中 4 条(S01/S02/S04/S05)为纯绑定引擎缺陷,2 条(S03/S06)为绑定缺陷+跑台锚配置覆盖不足叠加。**无论哪种,按预固定判据 P1(容许=0)均计误杀;分层定性仅供整改定位,不构成豁免。**

---

## 5. 最终裁决

### 裁决: **FAIL — 迁移门不通过,新链不得接管**

| 判据 | 裁决 |
|---|---|
| P1 V6 零误杀 | **FAIL**(留出面 0/6,六条真值变体全误杀) |
| P2 V5 拦截率+族地板 | **FAIL**(留出面 3/9;阈值族 S02、可加性族 S05 族地板击穿) |
| P3 漏放=0 硬门 | **FAIL**(S06/S07 两条叙事-数值矛盾条目以 VERIFIED 放行) |
| P4 真实历史复位 | PASS(5/5,本席复跑) |
| P5 一致性/白名单 | **FAIL**(留出面 V6-S01 unmapped=1;白名单与 thresholds 纪律本身达标) |
| P6 门禁+冻结 | PASS(七套全绿;13/13 夹具零漂移;封印完好) |

### 理由(三句)

1. 留出面暴露的不是边缘瑕疵而是**结构性缺口**: 判定面(verdict)对「阈值距离/枚举/约数/贡献集/prior 引用」五类形态的绑定全部失真,导致真值全灭(V6 0/6)与注入漏放(V5 两条 VERIFIED)同时发生——公开面 35/35 与留出面 3/9+0/6 的落差正是协议 §5 预防的「公开面形态过拟合」被当众测出,留出集设计目的达成,但结果不支持迁移。
2. P3 是无豁免硬门: 一条漏放即失败,实测两条;且漏放族(fault-B 叙事反向)恰是两起真实事故的同族方向(正确数值+错误定性结论)。
3. P4/P6 干净只能证明「已实现的部分在已见的样本上成立」,不构成对未实现形态的救济。

### 后续程序(按协议,不由本席执行)

- 留出集已用尽(一次性盲区随启封消耗,条目并入固定验收集常设部分,不再具备留出效力)。
- 任何修复须开发席**全量重跑**(公开面+已启封留出面+V1-V4/V7),结果整体计入,另开审计席裁决;**禁止修复后仅重跑留出面宣称通过**(协议 §5 明令,本席未做任何修复)。
- 整改定位参考(非指令): §2 机制表+§4.4 分层——绑定引擎五类形态(距离值/枚举/约数/贡献集/prior)与叙事-数值方向矛盾(需 SEMANTIC_REVIEW_REQUIRED 通道)是两类主缺口;锚链覆盖(prior 期次/历史锚集)为第三类配置缺口。

### 结论表述纪律(遵预固定)

- 正确表述: 「合成注入+改写变体集(含留出面)在预固定数值标准下**未通过**: 公开面 35/35 通过、留出面 V5 3/9、V6 0/6;真实历史故障样本(V1/V2)复位验证通过(P4 5/5)。」
- 本报告任何位置不使用「真实留出验证通过/未通过」措辞(协议 §5 结构性限制: 真实事故仅两起且已被 V1/V2 消耗,留出集只可能是样本级盲)。

— T8 独立审计席,2026-11-15
