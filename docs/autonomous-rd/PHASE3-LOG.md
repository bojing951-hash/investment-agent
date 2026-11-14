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

---

## T1+T2 操作者席验证(2026-11-14 深夜)

对象=dev/arch-reform-p3(验证基 281af6a[含 main R20 修复合入]+硬化 53a0508),独立复核在纯克隆 /tmp/reform-clone 与 /tmp/reform-verify2 执行。

| # | 项 | 方法 | 结果 |
|---|---|---|---|
| 1 | 签字稿保真 | 按 stable_key 建 69 键索引,与 ~/agent-loop/ARCH-REFORM/thresholds-registry-draft.json 逐键比 metric_id/value/unit/level/kind/direction/status/source_quote_bp 八字段 | **69/69 全同,零漂移**;pending=4 全 ism_pmi;boundary_convention 左开右闭保留 |
| 2 | G 门独立变异咬合 | 唯一值键 hy_oas.warning 4.0→4.1 篡改→跑门→还原 | **exit=1,G1r 两违例红**(OAS 表 HY OAS 关注/警告 4 孤儿);还原 exit=0。设计边界咬合属实 |
| 3 | **盲区发现+硬化(本波新发现)** | 重复值键 hy_oas.attention 3.0→3.1 篡改→跑门 | **门全绿=盲区实锤**:G1r 按值集合映射,69 键中 49 键值有重复(band 族共享边缘值,3.0 被 5 键共享),重复值键纯值漂移对 G1-G4 机器不可见 → 增 S4b 签字语义投影哈希钉(全文档剔 entries[].provenance.quote[quote 同步=G1 常规维护免重签]后规范化投影 sha256;重签流程=金融席签字→同提交更新钉)。quote 同步免钉实测不改投影,篡值必红。commit **53a0508**,套件 87→90 判全绿 |
| 4 | 实现席两红定案 | R20 套件 281af6a 合入后纯克隆跑;p0 套件纯克隆 vs 链式 worktree 对照 | R20 恢复套件 **5/5**;p0 纯克隆 **31/0 exit=0** vs 链式 worktree 30/1(判据「worktree 副本清单回零」在父仓合法挂多工作树环境下不可满足)→ **环境工件非回归**,实现席申报属实 |
| 5 | 全量 CI 同款回归 | /tmp/reform-verify2 纯克隆 53a0508,tests/test_*.py 逐个(model_live 跳过) | **144 执行 0 红**(含硬化件;实现席期两红[R20/p0]分别经 281af6a 合入修复与环境工件定案后全绿) |

### 验证期处置与遗留

- 任务书措辞差(validator 读 metric_registry 而非 thresholds 的 validation.range)=操作者席任务书笔误,实现席按签字稿实施正确,无码面动作(实现席申报①采信)。
- semantic_note「±1~+3 笔误待修」陈旧注记=签字稿原文,待金融席下轮随签刷新(实现席申报②),已登记为签字流程伴生项。
- S4b 钉属验证侧控制(操作者席武装),非实现席交付;未来 G1r 若收紧为逐键映射,套件内盲区复证判据应同步翻转(已在判据注释注明)。

---

## T3 series_store 补 macro 通道(2026-11-14)

**范围**: 工单T3——HY_OAS/CURVE_2S10S 进周报路径序列库(Agent Native S4→series_store 键;源窗与滞后如实注记)。泛化实现非两键白名单: 权属门自然放行全部合规 macro 序列,真实档实测 **31 键全入场**。

### 交付与执行证据

**A. scripts/snapshot_builder.py** — 新增 `merge_macro_series(store, raw)`(merge_series_sections 同区紧随)+ build_snapshot 构建段接线(五池并入后调用;注记非空时写顶层平节 `snapshot['series_store_notes']`)。门=通道别名 `fe._MACRO_ALIAS` 解析注册表 metric_id 且 `(history_source or source)=='macro_collector'`(history_source 臂=R25 DFF 双通道先例;未注册键/越权序列拒入);形态={'dates','values'} 双 list 等长非空(升序直通零改写零造数);store 既有键先占不覆盖(五池先占 macro 池殿后);**history_note 随序列入平节**(键=metric_id;无注记键不入;序列未入档则注记不入=防孤儿;series_store 值保持 {'dates','values'} 纯净不混注记);新鲜度窗=继承 resolve_inputs macro 档窗(rp.SOURCE_FILE_RULES=7 自然日),窗内无档→序列诚实缺席零造数。

**B. scripts/fact_engine.py(伴生最小改动,零行为漂移)** — `_MACRO_ALIAS` 自 normalize_macro 函数局部提升为模块级单一权威(FIX6-01 不两处漂移纪律),normalize_macro 改引模块级常量。等价证明:
```
$ git show HEAD:scripts/fact_engine.py 经 importlib 载入(REGISTRY_PATH 指回本仓),对 fixt 全 macro payload+WTI 别名臂比对
HEAD vs current normalize_macro equal: True   (n facts: 28 28)
alias arm equal: True
```

**C. scripts/research_history_query.py(doc-only 登记收口)** — 模块头「结构性缺口(登记)」→「登记→已收口」: macro 序列自 T3 起入 snapshot series_store,周报路径序列库覆盖 macro 池;本模块 macro 接入点 A(直读标准化层输入)不变。

**D. tests/test_arch_reform_t3_series.py(新件,43 判)** — A 单元面 21 判(门/逐字/先占不覆盖/形态跳过/平节携带·不携带·防孤儿/权属纯度全称)+ B 新鲜度窗 11 判(EXACT·注记随行/lag=7 FALLBACK 可用/lag=8 窗外 MISSING 零造数/档缺席)+ C 端到端 8 刭(fixt 合成采集档→build_snapshot 全链: 既有五池 40 键零回归+macro 18 键逐字+无序列键诚实缺席+无注记日平节不发+Gate A 不因 T3 改变+快照可序列化)+ D 查询面回归 3 刭(load_metric_series 接入点A 不受影响)。全合成 tmpdir+真实注册表,零绝对路径/零 LIVE 树/零网络=CI 干净克隆安全;CI 自动拾取(offline-tests.yml glob `for t in tests/test_*.py`,无需登记)。
```
$ python3 tests/test_arch_reform_t3_series.py
T3 回归: 43 PASS / 0 FAIL (共43判定)   全部通过 ✅
```

**E. 真实跑证据(验收面)** — 真实 macro_20261114.json **复制**到 tmp fixture 目录(代码零指向 LIVE 树),build_snapshot(target=20261114, trusted_root=tmp):
```
macro 档状态: EXACT file: macro_20261114.json
store 总键数: 31  其中来自 macro 档: 31
HY_OAS: n=785 末观测日=2026-11-12 与源档逐字相等=True
CURVE_2S10S: n=2500 末观测日=2026-11-13 与源档逐字相等=True
全 31 键逐字校验不一致数: 0
notes 平节键: ['BB_OAS','B_OAS','CCC_OAS','HY_OAS','IG_OAS','SOFR'](=源档带 history_note 的 6 键)
HY_OAS 注记逐字: True    CURVE_2S10S 无注记不入平节: True
快照序列化体积: 含macro=1000422字节 无macro=116854字节 增量=883568字节(862.9 KB)
store 内 macro 序列 n 合计: 31203
```
两序列末观测日均在新风窗内(EXACT 档): HY_OAS 2026-11-12/CURVE_2S10S 2026-11-13(源端发布滞后,history_note 如实注记)。

### 全量回归(诚实面)

```
$ for t in tests/test_*.py(排除 test_model_live):  # tests/ 共 146 件(含新 T3 套件),执行 145
  144 exit=0;  1 RED: test_p0_baseline_lock_equivalence(30通过/1失败)
```
唯一红=T1+T2 期与操作者席验证第4项已定案的**环境工件**(判据「R-还原 worktree清单回零」在父仓合法挂多工作树的链式 worktree 环境不可满足;纯克隆跑 31/0 绿),失败判据逐字同款,非 T3 引入。T3 改动文件不在该套件触及面。

```
$ python3 scripts/thresholds_gate.py        → G1-G4 全绿 exit=0
$ python3 scripts/rd_state_consistency.py --repo . --state-dir docs/autonomous-rd → 6/6 PASS
```

### 偏离与申报

1. **别名臂(对门字面的最小扩展)**: 任务书门字面=「m=fe.metric(key) 可解析」,而真实档 WTI 键须经 fe._MACRO_ALIAS→WTI_SPOT_M 才解析(normalize_macro 既有同一别名,rhq 反向表同源登记)。不加别名臂则 31→30 键且 WTI_SPOT_M 月频全史(n=120)静默缺席,与任务书「31 键自然放行」预期不符——按单一权威纪律实施别名臂(store 键=注册表 metric_id),非白名单特例。
2. **体积增量实测 862.9KB > 预估 ~650KB**(31 键全量直通,禁截断/抽稀/改写,如实入账;对照口径=同快照剔除 macro store 键与平节后的序列化体积)。
3. **e2eb_query_executor.NO_DATA_CORR_NO_STORE** 拒因串「macro通道序列不经store,既有结构边界」自 T3 起为历史措辞(该消息仅在所查快照 store 真缺席时触发: 手构快照/旧版快照/形态不合规被跳过);改串会动 test_p03_e2eb_b2 既有断言,本波不扩面,申报残留待操作者/审计席裁量。
4. fact_engine.py 为任务书未列文件的伴生最小改动(单源纪律,行为等价已证,见 B);PHASE3-LOG 本节随档入库操作者席 T1+T2 验证节(T3 开工时点为未提交工作树稿,单独 commit 说明)。
