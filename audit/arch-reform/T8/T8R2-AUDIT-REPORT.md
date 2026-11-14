# T8-R2 独立审计报告: 迁移门整改复验

- 审计席: T8-R2(全新上下文, 与开发席无共享会话, 不采信开发席声称, 全部亲自复跑)
- 日期: 2026-11-15
- 审计对象: commit `5feba7f`("T8整改轮: 引擎12项机制修复+四检查器+叙事方向+时代面"), 分支 dev/arch-reform-p3, 审计时 HEAD=`5feba7f2910ba595b11e5fad26b203268f0e1d2`, 工作树干净
- 前轮裁决: aafa350 报告 FAIL(P1/P2/P3/P5 四项败)
- 协议依据: HELDOUT-PROTOCOL.md §5(全量重跑+整体计入+独立裁决)
- 本席权限: 只写本报告并提交, 未改动任何引擎/测试代码

---

## 一、封存核验(判据: 文件级两哈希与清单一致)

命令:

```sh
cd ~/agent-loop/ARCH-REFORM/QA && shasum -a 256 heldout-sealed/*.json
```

实测:

```
9a15ab369ef2d9b7c067626c3c526e40f7978c6958ecb1f56324481e5f340c07  heldout-sealed/V5-HELDOUT.json
8370240d12c0ff6792d4711bcdbd765409c92cff3d21ae6dd086e5ce4b0a2347  heldout-sealed/V6-HELDOUT.json
```

清单(HELDOUT-MANIFEST.sha256 文件级节): 两值逐一相同。**一致。**

本席加验条目级哈希(防"改文件+改清单"双篡改): 按清单头注算法重算 15 条条目级 SHA256,V5-S01..S09 与 V6-S01..S06 全部 15/15 与清单一致。

另核: 留出条目原生含 `base_anchor_set` 字段(封存 schema 之一, 哈希未变证明非开发席后加); `seal/anchor_sources/schema_doc` 等 QA 元数据在场。**封存完整, 未被整改轮触碰。**

## 二、逐项执行证据

### B. 门套件(8 套)

命令: `for t in tests/test_arch_reform_t1t2.py ... test_arch_reform_t8r.py; do python3 "$t" ...; done`

```
PASS tests/test_arch_reform_t1t2.py        PASS tests/test_arch_reform_t6a_statistic.py
PASS tests/test_arch_reform_t3_series.py   PASS tests/test_arch_reform_t6b.py
PASS tests/test_arch_reform_t4_claims.py   PASS tests/test_arch_reform_t6c.py
PASS tests/test_arch_reform_t5_verifier.py PASS tests/test_arch_reform_t8r.py
```

防"空跑即绿"抽查(verbose): T8R=31 PASS/0 FAIL(含"启封条目 15/15"回归), T1+T2=90 PASS/0 FAIL。判定真实。

### C. 公开面矩阵

命令: `python3 tests/migration_matrix.py --fails` → `TOTAL ok=35 fail=0 / 35`, exit=0。

全量明细(去 --fails 复跑): V5-001..021 全 CONTRADICTED(21/21), V6-001..014 全 VERIFIED(14/14), 每条 `unbound=0`。

### D. 留出面(协议§5 已启封, 同命令同配置)

```
python3 tests/run_matrix_dir.py ~/agent-loop/ARCH-REFORM/QA/heldout-sealed/V5-HELDOUT.json
[OK] V5-S01/additivity_break+digit_error  ... got=CONTRADICTED (contra=1 veri=3 unbound=0)
[OK] V5-S02/band_threshold_error          ... got=CONTRADICTED (contra=1 veri=1 unbound=0)
[OK] V5-S03/sign_flip ... [OK] V5-S04/composite_score_error (contra=2)
[OK] V5-S05/additivity_break              ... got=CONTRADICTED (contra=1 veri=0 unbound=0)
[OK] V5-S06/narrative_contradiction (contra=2) [OK] V5-S07/narrative_contradiction (contra=1)
[OK] V5-S08/window_confusion [OK] V5-S09/forecast_conflation
TOTAL 9/9 达标; unmapped=0    exit=0

python3 tests/run_matrix_dir.py ~/agent-loop/ARCH-REFORM/QA/heldout-sealed/V6-HELDOUT.json
[OK] V6-S01 era=20261114 VERIFIED | V6-S02 era=20261114 VERIFIED
[OK] V6-S03 era=20261108 VERIFIED | V6-S04..S06 era=20261114 VERIFIED
TOTAL 6/6 达标; unmapped=0    exit=0
```

### E. P4 真实值复位

`python3 tests/run_matrix_dir.py --p4` → V1-滞后166天/V1-距离0.80pp/V1-DXY周+1.09%/V2-VIX桥式+32.03%至25.64/V2-顿号零售+0.77% 全 VERIFIED, `P4 5/5 复位 VERIFIED`, exit=0。

### F. T7 并行对照

`python3 tests/t7_parallel_harness.py; echo exit=$?` → 七项指标落档, `P4 五处全部复位 VERIFIED ✓`, **exit=0**。对照面: 错误拦截 new 21/21 vs old 0/21; 误报/漏报(new_v6=0, new_v5=0); V4/V7 序列依赖条目按 R24 判定档 DEFERRED_PHASE4/5 且哈希冻结(与第一轮口径一致)。

### G. 机制级 vs 条目特调(详见第四节) — PASS, 引擎零字面量命中

## 三、六+1 项裁决表

| 项 | 判据 | 本席实测 | 裁决 |
|---|---|---|---|
| P1 留出 V6 | 6/6 VERIFIED | 6/6 VERIFIED, unmapped=0;V6-S03 走 20261108 时代面(见下) | **PASS** |
| P2 留出 V5 | 9/9 CONTRA 且族底线检查器命中(非巧合) | 9/9 CONTRA;S02 由 `band_label` 命中(note: 值3.2实际处[attention]带 vs 标签[panic]);S05 由 `probability_sum` 命中(note: 5项概率和=115% vs 100%) | **PASS** |
| P3 叙事反转 | S06/S07 应 CONTRA | S06 双 CONTRA(`narrative_direction`: 美元走弱 vs DXY周+1.086%; 欧元升值 vs EURUSD周-1.5857%);S07 CONTRA(叙事倒挂 vs 2s10s=0.27pp 非负) | **PASS** |
| P4 真实值复位 | 5/5 VERIFIED | E 与 F 两处均 5/5 VERIFIED | **PASS** |
| P5 unmapped | 公开面+留出面=0 | C 35 条全 unbound=0;D 两面 TOTAL 行 `unmapped=0` | **PASS** |
| P6 门+封存 | 8 套全绿+封存完整 | 8/8 PASS(抽查判定数非空);封存文件级 2/2+条目级 15/15 一致 | **PASS** |
| P7 机制级(新设) | 无"为单一条目定制且无法解释为通用机制"的代码 | 引擎可执行路径零留出条目字面量(全部命中为 docstring 机制示例);修复均为注册表驱动/位置式规则/通用正则族 | **PASS** |

**V6-S03 时代面反向实证**(证明机制真实而非摆设): 同句在 20261108 面(其 base_anchor_set)VERIFIED;故意换 20261114 面即翻 CONTRA(threshold_constant: 红线0.25pp vs 注册表常量; level: 5.25% vs Fact UST_30Y@2026-11-12=5.43)。HC-1 时代面为真机制。

## 四、G 项审查细节(机制级 vs 条目特调)

审阅 `git diff aafa350..5feba7f -- scripts/research_contract/text_consistency.py`(891 行 diff 全文通读)+ 跑台两文件 diff(119 行)。修复清单及其机制属性:

1. **时代面 HC-1/HC-2**: `ERAS` 注册表+`load_era`(未知时代 fail-closed 抛 KeyError); 条目自带 `base_anchor_set` 路由, 公开面/留出面同一命令同一机制。数据驱动, 非条目分支。
2. **EA-1 距离配对式**: `_check_distance` 重写为 (常量, 距离) 对穷举+单位复述消费; 常量=注册表任意同值阈值(单位族相容 `_CONST_UNIT_FAMILY`), 非硬编码 104/5。
3. **EA-3/EA-6 注册表常量路由**: `_registry_const_hit` — 值=注册表某阈值且句段带阈值语境词 → 常量复述 VERIFIED。通用, P5 的 '104' 由该机制解决。
4. **EC-1..4 四检查器**: `_check_band_label`(带标签 vs 注册表带位, 含下沿之内/未达等否定语境的 eff_idx 移位), `_check_score_total`(快照事实+签字阈值 stable_key 独立复算, 成分缺失→INSUFFICIENT_EVIDENCE 不计 0 分, 含体制映射同构), `_check_probability_sum`(枚举≥3 项求和=100%), `_check_target_range`(DFEDTARL/U 对照, 前瞻口径跳过)。全部注册表驱动。
5. **EN-1 叙事方向**: `_check_narrative_direction` 后置检查(美元/欧元/2s10s 倒挂; 货币后缀 `(?<![\d.,，。])` 防误触; 倒挂解除语境排除; 异常降级 INSUFFICIENT_EVIDENCE)。通用叙事词表+方向事实。
6. **EA-5 枚举前向** `_window_of` 取 token 前缀最近窗口词; **prior 反噬防护** `_prior_role` 本期/当前标记优先(位置式); EA-2 时长换算 lag_duration; EA-4 可加性贡献集+流量形态三(additivity_flow, 排除注册表常量)。

**字面量扫描**(本席自建): 提取 15 条留出条目文本中全部 ≥3 位数字与小数串, 对引擎/跑台/测试四文件 grep。甄别结果:
- `scripts/research_contract/text_consistency.py` 命中 18 处, **逐一经行号核实全部为 docstring/注释中的机制示例**(`「同比+4.08%、环比+0.35%、同比+2.87%」`枚举示例、`0.59 points below the 104`配对式示例、`4.07–4.32%`目标区间示例、`0.23+0.01=0.24`等式括注示例、年-月正则说明等), 无一处于可执行判定路径。
- `tests/test_arch_reform_t8r.py` 命中=已启封 15 条固化为常备回归(防未来回归), 属测试断言而非引擎逻辑, 不构成特调。
- `tests/migration_matrix.py` 中 `5.25` 出现于注释"V6-S03=20261108 面: UST_30Y 5.25 时代"(解释 ERAS 存在理由); `tests/run_matrix_dir.py` 命中全部来自 P4 公开用例(第一轮已存在)。

## 五、泛化抽查(防"背题")

自造变体句(数字/分布/指标语境均不同于留出原文), era=20261114 面:

| 变体 | 文本 | 结果 | 命中族 |
|---|---|---|---|
| 1 概率和错误(不同分布) | 情景矩阵(概率和=100%): 扩张40%｜持平40%｜收缩30% | **CONTRADICTED** | probability_sum |
| 2 带标签错误(警告区但值在关注带) | HY OAS 3.20%, 已进入警告区(>400bp) | **CONTRADICTED** | band_label |
| 3 叙事反转(欧元贬值但欧元涨) | 本周欧元贬值: EURUSD 1.11(+1.60%) | **CONTRADICTED** | change/week(值在场, 主循环方向核先抓) |
| 4 正确变体(本席自造) | HY OAS 3.20%(-0.22pp), 仍处关注带, 压力可控 | **VERIFIED** | level+change/week+band_label 全绿 |

附注(如实记录): 任务提示所给的"正确变体"`HY OAS 4.20%, 已进入警告区(>400bp)` 实测 CONTRA——原因是引擎语义以**快照事实为唯一锚**: HY_OAS 快照真值=3.2(2026-11-12), 文本水平 4.20 与快照不符, level 正确报错, band_label 同按快照落带报错。此为该引擎设计(防文本自带错误值污染带判定)下的一致行为, 非泛化缺陷; 其方向为"宁多报不漏报"(见遗留风险 2)。本席另造真·正确变体(表内变体 4)全绿。

## 六、总结论

# 迁移门整改复验 PASS

六+1 项(P1/P2/P3/P4/P5/P6/P7)全部 PASS, 每一项均由本席独立复跑取得, 未采信开发席任何声称。整改轮对第一轮四败项(P1/P2/P3/P5)的修复全部为机制级(时代面注册表/距离配对式/注册表常量路由/四检查器/叙事方向), 族底线由对应族检查器真实命中, 时代面经反向实证为必要机制, 封存件零触碰(文件级+条目级 17 个哈希全一致)。

## 七、遗留风险诚实清单

1. **T7 真实报告面 new=0/3**(定性项, 非本门六项范围): 三份真实历史报告在新契约下全文 CONTRA, 归因"绑定旧引擎叙事面"(抽样定性见 real_face_adjudication)。真实报告全量迁移口径未闭合, 属后续阶段工作。
2. **band_label 以快照事实为锚的冗余报**: 文本值错误+标签"按该错值看似对"时会与 level 双报。方向为多报不漏报, 无漏报风险, 但 LIVE 化时需在报告层去重提示。
3. **_check_score_total 维度清单硬编码**: 8 指标×4 个 stable_key 显式枚举(值仍注册表驱动)。新增评分卡指标须同步改代码, 属维护性风险, 非特调。
4. **era 路由对"缺 base_anchor_set 字段"静默回退 20261114**(仅对"未知字段值"fail-closed)。未来封存条目若属其他时代却漏写字段将用错面。建议后续协议补: 封存 schema 将该字段设为必填校验。
5. **叙事方向检查器覆盖面**: 当前限美元/欧元/2s10s 三资产族; 日元/英镑等不在覆盖内(不误杀, 但也不拦), 属已知边界, 随 LIVE 词汇扩展。
6. **留出面效力耗尽**: 15 条启封条目已固化为常备回归(test_arch_reform_t8r), 本批条目从此失去"未见数据"效力; 下一轮迁移门须重新封存新面(封存面占比 30% 的设计初衷即为此)。
7. **泛化抽查样本量**: 本席 4 句+2 项机制反向实证, 非穷尽模糊测试; 建议后续以更大规模变异集做压力轮(不阻塞本门)。

---
*T8-R2 独立审计席, 2026-11-15。本报告为唯一产出; 审计过程未改动任何引擎/测试代码。*
