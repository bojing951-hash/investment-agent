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

---

## T3 操作者席验证(2026-11-14 深夜)

对象=dev/arch-reform-p3(实现席两笔 0f10022 码波+56fb2df 记账;验证基=纯克隆 /tmp/reform-verify3@56fb2df)。

| # | 项 | 方法 | 结果 |
|---|---|---|---|
| 1 | 套件+门独立复跑 | 纯克隆跑 T3 套件+G 门+一致性门 | **43/43 PASS**;thresholds_gate exit=0;rd_state_consistency **6/6** |
| 2 | 真档逐字独立复核 | 自备副本(macro_20261114.json→/tmp/t3-op-verify,与实现席 tmp 隔离)直调 merge_macro_series,31 键 store 值 vs 档内 series 原文逐字比对 | **31 键入场,不一致=0**;HY_OAS n=785(2023-11-14→2026-11-12)/CURVE_2S10S n=2500(2016-11-14→2026-11-13)/UST_10Y n=2499/WTI_SPOT_M n=120(别名臂实效);notes 恰=档内带 history_note 的 6 键,CURVE_2S10S 无注记不入 ✓ |
| 3 | 码面审 | git show 0f10022 逐行 | merge_macro_series=与 merge_series_sections 先例同构(权属门/形态门/先占/零改写);别名臂=fe._MACRO_ALIAS 逐字提升单一权威(fact_engine diff 亲核,函数局部同字面搬移);notes 防孤儿(序列未入则注记不入) |
| 4 | 全量 CI 同款 | 纯克隆 56fb2df tests/test_*.py 逐个(model_live 跳过) | **145 执行 0 红**(含 T3 套件 43 判;p0 在纯克隆绿=环境工件定案再获反证;实现席 worktree 跑的 144/1 红=链式 worktree 环境差异,同 T1+T2 第4项) |

### 四项申报裁定(操作者席)

1. **别名臂: 采**。fe._MACRO_ALIAS 提升=逐字搬移单一权威(非新表非白名单),WTI_SPOT_M 注册表 source=macro_collector 权属实证;不加则 WTI_SPOT_M 月频全史静默缺席=更差。门泛化性质保持。
2. **体积增量 862.9KB: 接受**。如实入账+对照口径合理(同快照剔除法);本地数据档体积非模型载荷面;禁截断/抽稀/改写符合章程(零数据改写)。预估 ~650KB 为操作者任务书估值误差,记入任务书精度教训。
3. **NO_DATA_CORR_NO_STORE 措辞残留: 登记不修(缓)**。仅 store 真缺席时触发的拒因串,语义仍正确(拒=对),措辞「不经store」过时;改串动 test_p03_e2eb_b2 既有断言=扩面,留 T7 新旧并行对照波统一处置(该波必触此路径)。
4. **fact_engine 伴生改动: 采**。任务书未列但为单源纪律必要(别名表模块级),行为零漂移申报+套件全绿背书。

### 结论

T3 工单验收面双证实成立: 「两序列可查询」=快照 store 面(真跑逐字)+rhq 接入点 A 面(套件 D 组);「新鲜度窗判定真实跑」=套件 B 组(EXACT/7 日窗 FALLBACK/8 日窗外 MISSING 零造数)+真跑 EXACT。T3 已毕,可进 T4(claim_factory 六型——谓词已有米下锅)。

---

## T4 claim_factory 六型(2026-11-14)

**范围**: 工单T4——新包 scripts/research_contract/ 只落 claim_factory.py(六型+谓词文法+单位代数)+claim_bundle.py(容器/schema) 两件(claim_verifier=T5、render/text=T6 未碰);fixture=真实快照垂直切片入仓;tests/test_arch_reform_t4_claims.py。零模型调用/零网络/零随机/零 env/零 LIVE 树指向。

### 交付与执行证据

**A. scripts/research_contract/claim_factory.py(新件)** — 六型全确定性派生自 Fact 层+series_store(含 T3 macro 通道序列)+thresholds 注册表+metric_registry:
- level: fact 值直读零改写;band 子结构两路=①fact 对(BAND_FACT_SPECS: Fed 目标带 3.75–4.00=契约§2 例)②注册表 band_edge 对(DXY 100–104=契约§2 例);value={low,high} 一带对象两数;
- change: 双轨直读 Fact 层 derived(spec §4.4 单位族单一权威=import fact_engine PRICE_LIKE/RATE/COUNT 三常量,不另造): 价格类→relative/pct_change(percent,basis 必带)/利率类→absolute/pp_change(pp+bp 双 token)/计数类→absolute/abs_change(原单位);禁合成另一轨(SPX 零 absolute、UST_10Y 零 relative=套件钉);
- comparison: spread/diff 同单位校验(异单位 UnitAlgebraError 拒)/rank=注册表 asset_class 数据驱动族(equity_index 周pct降序);
- threshold: relation(above/below/at)+since_date(last_crossing 谓词派生)+persistence(last_crossing+crossing_count 全窗);序列缺席→since=None 如实注记;阈值单位≠指标 canonical 单位→抛(注册表单位策略 fail-closed);
- threshold_distance: |level−threshold|(契约§2 示例 |3.20−4.00|=0.80 复现);无注册表条目指标零产不造(诚实缺席台账);
- observation_lag: as_of−observation_date 自然日(JP_POLICY_RATE=74 天=契约§4 STALE 行字面复现);
- 谓词文法(§3 逐字): percentile_rank=100×(严格小于+0.5×并列)/n/窗界=前一年度末观测含当期/min-n 门 20/月频 ytd 禁用;sign_flip_date(CURVE=2024-09-05=契约字面)/last_crossing/crossing_count(遍历计数+min-n)/AND 组合;
- 单位代数(律3): pp↔bp=×100 精确往返+canonical=percentage_point/basis_point;percent→pp 无基准必抛(唯一合法通道=显式基准);「400bp 与 4.00%」两 token 映射同一 hy_oas.warning claim(threshold_token_matches);跨指标 spread 同单位校验。
```
$ python3 scripts/research_contract/claim_factory.py tests/fixtures/t4_claims/snapshot_slice_20261114.json --out /tmp/t4_cli_out
bundle=claims_20261114 claims=109 → /tmp/t4_cli_out/claims_20261114.json
counts: {"level": 15, "change": 56, "comparison": 5, "threshold": 10, "threshold_distance": 10, "observation_lag": 13}
coverage_ledger: 9 条诚实缺席   predicate_ledger: 7 条
```

**B. scripts/research_contract/claim_bundle.py(新件)** — ResearchClaim v1.0 容器: schema 逐字段校验(三元组/change 律2 基准/evidence 必带值/band 区间对象/comparison 多成员/threshold_ref+provenance 稳定键)+装配+落盘 claims_YYYYMMDD.json(快照旁挂)+读写往返同 validator;零时间戳注入(纯函数确定性;时间身份=快照 research_as_of)。`__init__.py`=五模块布局注记(T5/T6 占位显式)。

**C. tests/fixtures/t4_claims/snapshot_slice_20261114.json(新件,95KB vs 全档 3.9MB)** — LIVE 树最新快照 research_snapshot_20261114_v2.json **只读复制提取**垂直切片: facts 13 指标全字段(工单五指标 SPX/UST_10Y/DXY/HY_OAS/CPI+comparison/band 伴生 8 件,见申报①)+series 6 键(SPX/DXY 尾窗自快照 store;HY_OAS 全史785/UST_10Y 尾130/CURVE_2S10S 自2024-01-01/CPI 全史月频119 自 macro_20261114.json——LIVE 快照 store 早于 T3 通道,序列取自 build_snapshot 同一输入档)。`_fixture_provenance` 随档: 源快照 id+两源档 sha256(快照 d533be2d…/macro cb252655…)+提取日 2026-11-14+逐键切片窗注记。代码零指向 LIVE 树,五新文件零绝对路径零网络(CI 干净克隆安全)。

**D. tests/test_arch_reform_t4_claims.py(新件,115 判)** — S1-S6 六型真实快照用例(验收原文「每型≥3」: level 15/change 56/comparison 5/threshold 10/threshold_distance 10/observation_lag 13,逐值套件内**独立复算**对照非回叫工厂;契约字面五钉: 0.80pp/2024-09-05/74天/3.75–4.00/100–104);U1 单位代数反例(pp↔bp 错值红/percent→pp 无基准拒/400bp≡4.00% 同 claim/跨单位 spread 拒);P1 谓词反例(并列半权 Fraction 手算/min-n 门/月频 ytd 拒/真实 HY_OAS 序列 crossing_count 手数对照=2024 年以来 2 次/last_crossing 独立扫/AND);Z1 零模型断言双面(静态: 三模块源码零模型客户端零 env 零网络零随机零时钟;动态: MODEL_* 绊线环境子进程生成=逐字节同输出+生成全程零网络模块载入);D1 确定性(双跑逐字节相等/claim_id 稳定序/写读往返/九类 schema 变异必红/诚实缺席台账/fixture 出处)。
```
$ python3 tests/test_arch_reform_t4_claims.py
T4 回归: 115 PASS / 0 FAIL (共115判定)   全部通过 ✅
$ python3 scripts/thresholds_gate.py        → G1-G4 全绿 exit=0
$ python3 scripts/rd_state_consistency.py --repo . --state-dir docs/autonomous-rd → 6/6 PASS
```

### 全量回归(诚实面)

```
$ for t in tests/test_*.py(排除 test_model_live):  # tests/ 共 147 件(含新 T4 套件),执行 146
  145 exit=0;  1 RED: test_p0_baseline_lock_equivalence.py
```
唯一预期红=test_p0_baseline_lock_equivalence(T1+T2 期已定案环境工件: 判据「worktree 副本清单回零」在链式 worktree 不可满足,纯克隆绿;T3 期同判)。T4 改动为纯新增文件,不在该套件触及面。

### 偏离与申报

1. **fixture 增补 8 件伴生 fact**(JP_POLICY_RATE/DFF/IG_OAS/DFEDTARU/DFEDTARL/HY_IG_DIFF/NDX/RUT): 工单字面「五指标…即可」,但 comparison 型需真实同单位对(契约§4 STALE 行「美日利差=新鲜DFF−滞后74天JP利率」字面复现+HY_IG_DIFF=Fact 层既成 spread 对账 2.31)、band 型需 target_band 事实对、rank 需≥2 成员族——只按字面五指标则 comparison 真实用例不可达。体积 95KB 仍属克制(2.4% 全档);逐键 provenance 注记。
2. **comparison.diff 子类型无真实正例**: 真实对均落 spread(利差语义)/rank;diff 在 schema+builder 在册,以「跨单位拒」反例(UST_10Y−HY_OAS)覆盖其校验面。工单验收=「每型≥3」(型=comparison: 5 例 ✓);diff 子型留待真实语义对出现再入默认 bundle,如实申报。
3. **谓词产出位置**: percentile_rank/sign_flip 落 bundle.predicate_ledger(事实性派生字段),last_crossing/crossing_count 嵌 threshold claim persistence;六状态机字段预留给 T5(gate=INSUFFICIENT_EVIDENCE 仅事实标注,非验证状态)。
4. **fact_engine 只读引用零改动**(import 单位族三常量=单一权威纪律;无伴生码面改动,异于 T3 波)。
5. **formula 文本用 canonical 全名**(|3.2−4.0|=0.8 percentage_point)而非契约示例 pp 缩写后缀——律3「渲染后缀不得反推单位」精神,unit 字段=唯一权威(契约示例为示意非规范)。
6. BAND_FACT_SPECS/COMPARISON_SPECS=模块内确定性配置表(带出处,非自由文本输入;纯函数输入面=快照+两注册表不变)——Fed 带事实对无注册表配对语义可数据驱动泛化,如实以配置表声明。
7. PHASE3-LOG 工作树含操作者席 T3 验证节(T4 开工时点为未提交工作树稿)随本 commit 入库(T3 波同款先例)。

---

## T4 操作者席验证(2026-11-14 深夜)

对象=dev/arch-reform-p3@f65b28c(单笔: 新包两件+fixture+套件+记账)。独立复核基=纯克隆 /tmp/reform-verify4。

| # | 项 | 方法 | 结果 |
|---|---|---|---|
| 1 | 套件独立复跑 | 纯克隆 T4 套件 | **115/115 PASS** |
| 2 | CLI 真跑+计数 | factory 跑 fixture→bundle | **109 claims 计数全中**(level 15/change 56/comparison 5/threshold 10/threshold_distance 10/observation_lag 13)+coverage_ledger 9 条诚实缺席+predicate_ledger 7 条 |
| 3 | 契约字面钉 | bundle 逐值抽验 | HY_OAS 距警告线 **0.80pp**(=11-14 Gate B 误杀事故值,今为结构化 claim 带 thresholds 稳定键溯源);CURVE sign_flip_date=2024-09-05;HY_OAS 距离三档 0.2/0.8/1.8;Fed 带 3.75–4.00/DXY 带 100–104 band 对象;persistence.last_crossing 带穿越日/前后值/方向/现侧,窗内无严格穿越=诚实注记不造 |
| 4 | fixture 出处 | _fixture_provenance 双 sha256 vs LIVE 源档实算 | **双中**(research_snapshot_20261114_v2=d533be2d…/macro_20261114=cb252655…) |
| 5 | 静态纯度 | import 面+model/env/net/random 扫描+包清单 | 仅 stdlib+fact_engine(只读)+claim_bundle;扫描唯一命中=注释「model_inferred 提交面=阶段四」;包=3 件(init/factory/bundle),**无 T5/T6 越位**(verifier/render_hook/text_consistency 未落);f65b28c 未改 fact_engine=零伴生改动 |
| 6 | 纯函数独立咬合 | 篡 fixture HY_OAS fact 3.2→3.5→重跑 | 距离随动=|3.5−thr| 精确复算(0.5/0.5/1.5),claim 总数稳定 109 |
| 7 | 全量 CI 同款 | 纯克隆 f65b28c tests/test_*.py 逐个(model_live 跳过) | **146 执行 0 红**(含 T4 套件 115 判;p0 纯克隆绿=环境工件定案第三次反证;实现席 worktree 跑 145/1 同前环境差异) |

### 申报裁定(七项)

①fixture 增补 8 件伴生 fact=**采**(comparison/band/rank 真实用例可达性,体积 2.4% 克制);②comparison.diff 无真实正例=**接受**(schema 在册+跨单位拒反例覆盖,真实 diff 正例待后续真实快照自然产生);③谓词产出位置(percentile/sign_flip=predicate_ledger,crossing/last_crossing=threshold.persistence)=**采**(CURVE 零注册表键→序列仅产谓词不入 threshold 面,coverage 自洽);④canonical 全名非 pp 缩写=**采**(律3 原文即此);⑤BAND_FACT_SPECS/COMPARISON_SPECS 带出处配置表=**采**(配置≠白名单税则面;若 T5/T7 发现需数据驱动化再议);⑥⑦随档入库操作者节=T3 同款先例,核对采。附: 终报「fact_engine 只读 import 单位族三常量」措辞偏窄——实引用 fe.metric/load_registry/REGISTRY_PATH 只读 API=正确单源纪律,非文件改动,无碍。

### 结论

T4 工单验收面成立: 六型全确定性(纯函数咬合实证)+每型≥3 真实用例(109 claims 源自真快照,出处哈希双中)+零模型调用(静态扫描+包清单)。故障 A 类消灭路径落地第一块: 「距离0.80pp」从文本猜数变结构化 claim。进 T5(claim_verifier 六状态)。

---

## T5 claim_verifier 六状态确定性验证(2026-11-15 凌晨,接管席)

工单: PHASE3-PLAN T5+契约 §4 状态表(权威)。原派实现席 22:56 后零落盘,按「引擎不空转」授权由本席接管(STATE.md 接管声明在案,防双跑)。实现=**新增** scripts/research_contract/claim_verifier.py(631 行)+tests/test_arch_reform_t5_verifier.py(443 行,46 判);旧 Gate B 零改动(只读对照纪律)。

### 状态机(§4 逐字映射;优先级=不符>反洗数>证据缺失>无路径>陈旧>一致)

| 状态 | 触发 | 发布 |
|---|---|---|
| VERIFIED | 独立复算一致+fresh | ✅无披露(computed/delta/tolerance/checker_version 随行) |
| CONTRADICTED | 数值/证据/阈值/组核验/律3/§3可加性 任一不符 | ❌claim 级修订+机械重渲染(非整报隔离) |
| INSUFFICIENT_EVIDENCE | 空引用/无值引用/所引事实缺席快照 | ✅须披露 |
| NOT_VERIFIABLE | deterministic 无验证路径(带归因{路径/原因枚举/可否次级交叉}) | 仅 deterministic 可披露后发布;禁入【事实】区 |
| STALE | ratio=lag÷freshness.max_calendar_lag_days: ≤1 fresh/≤2 l1/≤3 l2/>3 l3 | ✅须披露;l3 另入 current_frame_forbidden |
| SEMANTIC_REVIEW_REQUIRED | model_inferred 数值证据缺失或无路径→强制升态 | ⏸超时=剔除+显式披露 |

反洗数(律7/v1.1): model_inferred 数值**有源→对照复算照常 VERIFIED;篡值→CONTRADICTED;证据缺失/无路径→一律 SEMANTIC_REVIEW**,禁经 INSUFFICIENT/NOT_VERIFIABLE 披露后洗出(C3/C5 双反例钉)。

### 验收原文「注入违例每状态≥1 反例咬住」→ 46 判映射

- CONTRADICTED 15 路反例(B1-B15): 九型数值篡改/relation/since 篡/threshold_ref 漂移/证据带值不符/rank 组换位(对位路)+组重复(多重集路)/跨单位 spread(律3,引用与事实一致篡改专打同单位校验)/分解可加性(§3)。
- SEMANTIC_REVIEW 2 例(C3 空引用/C5 fact 缺席);NOT_VERIFIABLE 1 例(C6 band_edge 对被抽,归因四字段逐项断言)+gate_b 联动(C5 False/C7 True);INSUFFICIENT 4 例(D1/D2/C4 全族);STALE 6 例(A5 契约权威例 JP 74 天=l1/A6 派生继承/E1 l2/E2 l3+禁入现状框架/E3-E4 阈值边界);VERIFIED 基线 107 条零误伤+model 有源照常过(C1)。
- F/G 面: 裁决写回=契约 §2 示例形状逐字段断言(F1-F2)/双跑逐字节(F3)/超时策略剔除+披露(F4-F5)/纯度静态扫描+MODEL_* 绊线子进程双跑逐字节同输出(F 面外 G1-G3)。

### 执行证据(命令+输出摘录)

1. 基线(工厂 clean bundle 真跑): `verify_bundle(generate_claims_bundle(snapshot_slice_20261114))` →
   `{"VERIFIED": 107, "CONTRADICTED": 0, ..., "STALE": 2, "total": 109}` + `gate_b_numeric_all_verified: True`;STALE 两条=JP_POLICY_RATE 74d/60d≈1.2(l1,契约 §4 STALE 行权威例数值命中)+DFF−JP spread 继承最差输入 l1(members 细节随裁决)。
2. 套件: `python3 tests/test_arch_reform_t5_verifier.py` → `结果: 46通过 / 0失败`(A1-G3 全绿)。
3. 全量(CI 同款逐套,纯克隆 /tmp/t5-pureclone@dev/arch-reform-p3+T5 四件): **147 执行 145 绿 2 红**。2 红=test_rd_r20_state_checkpoint(43/2)+test_rd_r20_state_consistency(11/1)=**既有分支状态面非本波**: 同克隆裸 f65b28c(无 T5 文件)复跑同红同文案(`main 超前 baseline 7 个提交中 1 个不容忍…如 496dc1a`)=与 T5 零相关;根因=reform 分支落后 main(R27 收口+HK 合并链+T-R28-2 对账行在 main 不在本分支),T4 时点 146/0 绿与此不矛盾(彼时 main 未超前)。main 纯克隆今日全绿 145/0(ALL_GREEN,任务档在案)。**分支随 main 收敛(由操作者席定 rebase/merge)后此两面自复绿,无需本波处理**(整改分支未经授权不并 main 纪律不动)。
4. CLI 冒烟: `python3 scripts/research_contract/claim_verifier.py <bundle> <snapshot> --out r.json`(MODEL_* 绊线 env)=退出 0+双跑逐字节同+summary 与进程内一致(G3)。

### 设计裁决记录(实现中发现,逐条修正)

1. threshold 型 value=float(Fact 水平)+relation/since_date/since_note/persistence=**顶层事实性字段**,验证=值+aux 逐项镜像重算(工厂 build_threshold_claims 口径逐字对照: side_now 同侧取 crossing_date/全窗同侧回窗首注记/末端侧不一致=如实空/序列缺席=series_absent 注记)。
2. change 族端值锚=**derived.end.value(原始序列值)**,非 fact.value(显示舍入位)——首版误锚致 clean 面 9 条假红(RUT −8.594 vs −8.5939 舍入边界),T4 同锚(S2 复算式)既证,修正后归零。
3. 派生 claim STALE 继承=**各成员按自身节奏定级后取最差**(members 细节随档),禁跨成员错除(首版 min(cadence)×max(lag) 把 DFF−JP spread 错算 7.4 节奏=l3,修正为 JP 1.2=l1)。
4. 无值引用归 INSUFFICIENT 薄证据路(§2「引用必带值」结构违约),非证据值不符硬红;引用-事实逐条一致性只对带值引用判。
5. 跨单位 spread=硬不符(CONTRADICTED,律3 篡改面),禁经 NOT_VERIFIABLE 披露洗出;basis=0 相对变化=predicate_uncomputable 诚实 NV。
6. 组哨兵=模块级单例(_GROUP_FAIL);每调用 object() 新建实例致 is 比较恒真(实测 rank 组重复反例抓出该缺陷后修正)。
7. model_inferred 数值+好证据+复算一致=VERIFIED(律7「有权威源→对照复算」,不因 attribution 一刀切——为阶段四语义审查席留正确接口,而非扩大强制面)。

### 遗留与移交

- T6(确定性渲染器 C1)起所有权归还未定(接管声明原约);T5 API 面=verify_bundle/apply_verdicts/timeout_policy+CLI,T6 消费律6=「渲染只吃 VERIFIED,余态入披露区」。
- 工作树保留原实现席未提交稿(claim_bundle.py attribution 扩展+24/-4+本档 T4 节)随本 commit 入库(T3/T4 波同款先例)。
