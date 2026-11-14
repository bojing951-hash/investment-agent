# PHASE3-LOG — 架构整改阶段三纵向切片执行日志

> 依据 ARCH_REFORM_PHASE3_PLAN.md §纪律: 每任务毕落本档(执行证据=命令+输出摘录,禁只写结论)。
> 分支 dev/arch-reform-p3(基点 main@aa7a96b);未经用户授权不并 main 不动生产。

---

## T1+T2 合并波 — S1 六项 + thresholds v1.0 落盘 + G1-G4 CI 门(2026-11-14)

**范围**: 章程§九 T1(S1 六项: framework 四处对齐/macro_scorecard 硬编码退役+BEI 显示串真修/data_validator 数值词典整族退役) + T2(thresholds.json v1.0-SIGNED 落盘 + scripts/thresholds_gate.py G1-G4 对账门 + CI 接线 + 回归套件)。

### 交付与执行证据

**A. config/thresholds.json(新件)** — SIGNED-v0.2 内容逐字为基(69 键/schema/boundary_convention/unit_policy/two_level_model/kind_vocabulary/conflicts 全保),增 top-level `signed_by`/`signed_at="2026-11-14"`/`adjudication_ref`,status→`v1.0-SIGNED`。零键值增删改(金融席只签不改值);provenance.quote 锚同步 12 键=裁定 S1-3a 授权常规维护(INDPRO 4 键重锚 framework 补行+scenario 2 键+regime stagflation+cn_turnover+sb_flow+ahe 3 键),闭合清单由套件 S1 断言钉死。
```
$ python3 -c "import json;d=json.load(open('config/thresholds.json'));..."
top keys: ['schema','status','signed_by','signed_at','adjudication_ref',...,'entries','conflicts',...]
n entries: 69    pending count: 4 (全 ism_pmi.scorecard.m48/m50/p52/p55)
```

**B. config/framework.md 四处修改(对齐+漂移注记,非静默)** — ①BEI 双级注记(headline 2.5/band_edge 2.6,裁定#1);②增长表第四项=工业生产MoM(INDPRO) 按代码口径补行,ISM 行保留为「待采:未激活,2026-11-14架构整改注」注记行(裁定#5);③失业率 3m 空洞带 (+0.1,+0.3] 补「+0.1~+0.3%=0(左开右闭)」(裁定#6);④§八「±1~+3」→「+1~+3」笔误修正+S1-3a 注记行。

**C. scripts/data_validator.py** — SANITY_CHECKS 数值界字段(min_value/max_value/max_value_K)整族退役: SPX/WTI/VIX 改 `range_metric_id`→`metric_validation_range()` 读 metric_registry validation.range(fail-closed,缺键 RuntimeError);非农 max_value_K=1000 退役改 NFP_MOM_K 归一化比对(人÷1000→persons_thousands);L253-258 A股口径词汇规则显式保留+注记(裁定#2/#3/#4,S1-2a)。区间差(逐键申报): SPX [2000,10000]→[1000,30000];VIX [8,90]→[5,100];WTI [20,200]→[10,300];非农 max 1000K→[-2500,1500]K(下界经现有正则不可达=纵深防御,捕获组仅无符号数)。真实带内行为等价。
```
$ python3 tests/test_rd_r27_gateb_extractor.py
R27 Gate B 误杀修复: 45 PASS / 0 FAIL     # 11-14 真实报告全文 0 数值错,量级检查走注册表
  ✅ WTI范围: 88.92 (合理,注册表区间[10,300])  ✅ VIX范围: 19.3/25.6 (合理,注册表区间[5,100])
```

**D. scripts/macro_scorecard.py** — 全部评分带/体制阈值/显示串常量改 `TH(key)` 读 thresholds.json(`SCORECARD_THRESHOLD_KEYS` 35 键声明+缺键 RuntimeError);**BEI 显示串低侧真修复**(旧串「高通胀>2」误写→「低通胀<1.5% | 高通胀>2.5%」,headline 叙述级;距离计算仍 band_edge 2.6)=本波唯一申报行为差。带边界扫描 8 指标×(4 边界±0.001+极端)新旧逐点等价。
```
$ python3 -c "...print(scores['bei_10y']['thresholds'])"
低通胀<1.5% | 高通胀>2.5%
```

**E. scripts/thresholds_gate.py(新件)+CI 接线** — G1 注册表↔framework 双向锚(正向 quote 逐字命中[空白归一/分段/管道分解/表格列头复合锚];反向 framework 阈值区全数值须映射注册表值+行族在册,白名单仅非阈值语义{2,0.1,±8}逐一注明);G2 代码常量集↔注册表 scorecard 族差集双侧空(pending 豁免显式列出;headline 键按 two_level_model=叙述级,读取须在册但不入族);G3 概念隔离双向静态断言;G4 词典/常量退役断言(退役字段零残余+if/elif 阈值位裸数值扫描,非阈值工程常量逐一注释豁免)。门红 exit≠0;`.github/workflows/offline-tests.yml` 增独立步骤(测试环后、一致性门前)。
```
$ python3 scripts/thresholds_gate.py
🟢 G1_forward / 🟢 G1_reverse / 🟢 G2 / 🟢 G3 / 🟢 G4: PASS
🟡 pending 键(豁免 G2 实施比对,显式列出): [ism_pmi m48/m50/p52/p55]
结果: 全绿(G1-G4 PASS)  exit=0
```

**F. tests/test_arch_reform_t1t2.py(新件,87 判)** — S1 注册表完整性+34 键值=旧常量逐键相等+签字稿逐字对照(本地);S2 带边界等价扫描+BEI 真修+体制边界+fail-closed;S3 真实件等价+区间差带逐键+词汇规则保留;S4 门全绿+12 变异红(quote 篡改/framework 暗改/孤儿数值/未注册行族/TH typo/声明删/退回硬编码/G3 两向/G4 三态);S5 framework 四处在场性。
```
$ python3 tests/test_arch_reform_t1t2.py
T1+T2 回归: 87 PASS / 0 FAIL (共87判定)   全部通过 ✅
```

### 全量回归(诚实面)

```
$ for t in tests/test_*.py (排除 test_model_live):  # tests/ 共 145 件,执行 144
  142 exit=0;  2 RED: test_p0_baseline_lock_equivalence / test_rd_r20_recovery
```
**两红均为既有红非本波引入**——基点 aa7a96b 干净工作树复跑同判:
`test_p0_baseline_lock_equivalence` 30/1(R-还原 worktree 副本清理失败);`test_rd_r20_recovery` 3/2(R1/R1a 恢复下一任务期望 vs T-R27-1 回流拒启)。本波改动文件两套件均不触及(已存档基点证据)。

```
$ python3 scripts/rd_state_consistency.py --repo . --state-dir docs/autonomous-rd
①基线一致 ②RESUME健全 ③台账规范 ④验收矩阵 ⑤日志-台账 ⑥目标完整 — 6/6 PASS
```

### 发现但无权修(申报)

- 任务书 C 项措辞「读 config/thresholds.json 对应键的 validation.range」与签字稿冲突: thresholds.json 按 G3 概念隔离**不含** validation.range;绑定权威=metric_registry.json validation.range(裁定#2/#3/#4+签字稿 G4 段自述)。按签字稿实施,措辞差申报。
- `scenario.growth.neutral_floor` semantic_note 仍记「±1~+3 笔误待修」——framework 笔误已修(B④),semantic_note 为签字稿原文不可擅改,待金融席下轮随签刷新。
- 非农模式下界 -2500K 经现有捕获正则不可达(仅无符号数)——纵深防御非行为面,已注记于套件。
