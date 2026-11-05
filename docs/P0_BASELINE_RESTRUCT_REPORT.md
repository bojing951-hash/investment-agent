# IA-P0-BASELINE-RESTRUCT WP-BR 报告(注册表演进测试基线重构包)

> 包: IA-P0-BASELINE-RESTRUCT-WP-BR-AC-v1.0 | 分支: `dev/p0-baseline-restruct`(自 5e9fc88650b9d4a483e83b6638cbc984f8e7b514 切出,纯线性)
> 基线: BASE-BR=5e9fc88650b9d4a483e83b6638cbc984f8e7b514(=冻结时 origin/main 尖端,ls-remote 实取核对一致);BASE-BR-CI-SUITES=64(本地基线全量实测 63 绿+test_p4_fixes 红[已知 ambient 态],套件数=64 与冻结值一致)
> 本 REPORT 为登记制文件: §零开工首步落档(M/A 集自登记时点起即为本合同白名单实体);§一~§七随各步完成填充,终版随 docs 提交定稿。

## §零 全量基线锁清点表 + M/A 集登记(开工首步)

### 零.0 清点方法(三源交叉,登记)

家族名模式发现(`tests/test_p01_fix*.py`/`test_p02_w2_fix*.py`/`test_p02_w3*.py`/`test_p02_w4*.py`/`test_p02_w5.py`/`test_data_w3*.py` + 实证扩充 `test_p02_w1*.py`/`test_p02_w2.py`/`test_p4_fixes.py`)× 机制 grep 锚(合同附录A: `== 81`/`==81`/`81项`/`len(.*registry.*by_id`/`core_metric_ids.*== 32`/`Gate A`/`all(.*active`/`全active`/`齐备`/`sources_status`/`KNOWN_SOURCES`/`CHANNELS`/test_p4_fixes 内 `data/daily`)× 文件实读定类。发现程序机器化脚本与原始 198 行命中清单入证据包(`discovery/`)。

机制类别口径(登记): **81计数**=注册表/审计结果项数字面等值锁;**全active契约**=fixt 构造的全 active 正常日上"Gate A=PASS/effective=PASS"断言(含包 meta gate_a=PASS 链);**sources_status结构**=来源状态逐值迭代/通道枚举断言;**p4环境敏感**=test_p4_fixes 对 ambient `data/daily` 在场/缺席的分支依赖。

### 零.1 全量基线锁清点表(每锁一行: 文件:行号/机制/锁原文摘录/保护的回归类/三联锁重构方案)

| # | 文件:行号 | 机制 | 锁原文摘录 | 保护的回归类 | 三联锁重构方案 |
|---|---|---|---|---|---|
| 1 | tests/test_p02_w4.py:231 | 81计数 | `self.assertEqual(len(reg['metrics']), 81)` | 注册表静默缩水(条目丢失) | T1 下限≥81 + T2 实载集合(by 231-235 邻接已有 set 全等+唯一断言保持) |
| 2 | tests/test_p02_w4.py:232 | 81计数 | `self.assertEqual(len(self.result['metrics']), 81)` | 审计结果漏输出指标 | T2 结果 ID 集==注册表 ID 集(实载派生) + T1 下限≥81 |
| 3 | tests/test_p02_w4.py:410-412 | 81计数 | `st.get('MISSING',0)+…+st.get('DERIVED_ONLY',0), 81)` | by_status 桶和≠全量(静默丢桶/丢项) | T2 sum==len(result['metrics'])(自洽) + T1 下限≥81 |
| 4 | tests/test_p02_w4.py:691 | 81计数 | `self.assertEqual(r['registry']['metric_count'], 81)` | 机器报告 registry 回显漂移 | T2 ==实载注册表项数(运行时实读) + T1 下限 |
| 5 | tests/test_p02_w4.py:703-705 | 81计数 | `self.assertEqual(len(rows), 82)  # 表头1+81数据行` | 逐项覆盖表行数缩水(无数据指标丢行) | T2 ==1+实载注册表项数 + T1 下限≥82 |
| 6 | tests/test_p02_w4.py:745-746 | 81计数 | `self.assertEqual(len(ids), 81)` | 注册表唯一 ID 集缩水 | T1 下限≥81(唯一性由 745 set 构造+747-748 映射目标∈ids 保持) |
| 7 | tests/test_p02_w4_fix1.py:544 | 81计数 | `self.assertEqual(len(res['metrics']), 81)` | 审计结果漏输出 | T2 集==注册表集 + T1 下限 |
| 8 | tests/test_p02_w4_fix1.py:563 | 81计数 | `self.assertEqual(len(res['metrics']), 81, combo)` | 同上(五通道子集变体) | 同上 |
| 9 | tests/test_p02_w4_fix2.py:243 | 81计数 | `self.assertEqual(sum(…by_status…values()), 81)` | 桶和≠全量 | T2 sum==len(result) + T1 下限 |
| 10 | tests/test_p02_w4_fix2.py:543 | 81计数 | `self.assertEqual(len(res['metrics']), 81)` | 审计结果漏输出 | T2 集==注册表集 + T1 下限 |
| 11 | tests/test_p02_w4_fix3.py:411 | 81计数 | `self.assertEqual(len(res['metrics']), 81)` | 同上 | 同上 |
| 12 | tests/test_p02_w4_fix4.py:43,540-541 | 81计数 | `N_METRICS = 81` / `assertEqual(len(res['metrics']), N_METRICS)` | 失败态指标数虚增/缩水 | T2 ==实载注册表项数 + T1 下限≥81(N_METRICS 重定义为派生期望+冻结下限双形态) |
| 13 | tests/test_p01_fix1.py:416-420 | 全active | `check("全核心齐备+无失败→Gate A PASS(基线)", snap['gate_a']['status'] == 'PASS', …)` | 基线通道/指标静默死亡仍被当正常日 | vintage 域(gate_vintage_ok: PASS 恒绿;DEGRADED 仅当 core 桶净+noncore_missing⊆注册表 vintage 后新增未覆盖集) |
| 14 | tests/test_p01_fix2.py:364-367 | 全active | `rec['effective'] == 'PASS' and set(rec['counts'])==…`(RE_PASS) | 同上 | vintage 域(counts 键集词汇断言保持) |
| 15 | tests/test_p01_fix2.py:449-457 | 全active | `rec['counts']=={'PASS': _base_counts['PASS']-1,…} and rec['effective']=='PASS'` | 合法 WARN 变体吞降级 | vintage 域(counts 相对基线断言保持) |
| 16 | tests/test_p01_fix2.py:507-514 | 全active | `rec['counts']==_rec_pass['counts'] and rec['effective']=='PASS'` | 声明一致态漂移 | vintage 域 |
| 17 | tests/test_p01_fix3.py:238-244 | 全active | `check("对照: 全核心PASS日→预检通过+包meta.gate_a=PASS", ok and meta.get('gate_a')=='PASS')` | 正常日包 meta 降级未对齐 | meta gate_a==快照 gate 一致性 + vintage 域 |
| 18 | tests/test_p01_fix4.py:131-134 | 全active | `rec0['effective']=='PASS' and rp.gate_status(base)==('PASS','')` | 基线指标静默缺失 | vintage 域(gate_status 声明一致性分支保持——声明侧与重算侧同变体) |
| 19 | tests/test_p01_fix4.py:190-192 | 全active | 同上(注入回调变体) | 同上 | 同上 |
| 20 | tests/test_p01_fix4.py:535-541 | 全active | `rec_dep['effective'] == 'PASS'` | 派生链断裂吞降级 | vintage 域 |
| 21 | tests/test_p01_fix5.py:157-166 | 全active | `rec['effective']=='PASS' … and PASS+WARN总数>=78` | 全 active 日降级未捕获 | vintage 域 + ≥78 冻结下限保持(T1 形态已具,保留) |
| 22 | tests/test_p01_fix5.py:196-200 | sources_status | `all(st.get('status')=='EXACT' and st.get('file_date')==DAY for st in SNAP['sources_status'].values())` | 基线通道非 EXACT;盲迭代对新增通道回溯要求 | ⊇基线四通道逐通道 EXACT+file_date==DAY + 在场通道结构合法(status∈词汇表)——新增通道不回溯要求 |
| 23 | tests/test_p01_fix5.py:210-216 | sources_status | `all(st['status']=='FALLBACK' and st['file_date']==PREV_D and st['lag_days']==1 …values())` | 回退日通道状态漂移 | ⊇基线四通道逐通道 FALLBACK 语义 + 在场通道结构合法 |
| 24 | tests/test_p01_fix5.py:237-238,277-279,286-289,313-316,398-401,436-438 | 全active | `rp.recompute_gate_a(SNAP)['effective'] == 'PASS'`(六处对照) | 重算侧降级吞没 | vintage 域(逐处) |
| 25 | tests/test_p01_fix5.py:551-560 | 全active | `SNAP['gate_a']['status']=='PASS' … pm.get('gate_a')=='PASS'` | 包 meta 与快照 gate 漂移 | meta==快照一致性 + vintage 域 |
| 26 | tests/test_p01_fix6.py:237-239,306-309,354-357,427-429,443-445,461-463 | 全active | `rp.recompute_gate_a(SNAP…)['effective'] == 'PASS'`(六处) | 重算侧降级吞没 | vintage 域(逐处) |
| 27 | tests/test_p01_fix6.py:596-600 | 全active | `SNAP['gate_a']['status']=='PASS' … meta gate_a=='PASS'` | 正常进入数据包链漂移 | meta==快照一致性 + vintage 域 |
| 28 | tests/test_p01_fix7.py:108-115 | sources_status | `ssp(SNAP['sources_status'], data_dir=BASE_DAILY, trusted_root=BASE) == []` | 基线通道结构损坏 | 结构校验本体 vintage 中立,保留;追加 ⊇基线四通道在场断言(增强) |
| 29 | tests/test_p01_fix7.py:352-360 | 全active | `snap_d1['gate_a']['status'] == 'PASS'` | 正常日构建降级 | vintage 域 |
| 30 | tests/test_p01_fix7.py:369-381 | 全active | `snap_hist gate PASS + recompute PASS + gate_status PASS` | 纯历史口径降级 | vintage 域(三口径同变体) |
| 31 | tests/test_p01_fix8.py:350-363 | 全active+sources_status | `all(riF[ch] and riF[ch]['exact'] for ch in rp.SOURCE_CHANNELS) … snapF gate PASS … sha256 len==64` | 基线通道未被选中/摘要缺失 | 基线四通道==rp.SOURCE_CHANNELS 实载全等断言(通道枚举同步演进,T3 兼容)+逐通道 sha256 结构 + vintage 域 |
| 32 | tests/test_p01_fix8.py:699-701 | 全active | `_checks.get('Gate A状态') == 'PASS'` | 报告 Gate A 漂移 | vintage 域(以重建快照判 vintage) |
| 33 | tests/test_p01_fix9.py:245-251,266-276 | sources_status | `ok_ss = SNAP['sources_status']` 对照 + `ssp(…)` 结构族 | 基线通道结构损坏 | 结构校验保留;追加 ⊇基线四通道在场断言(增强) |
| 34 | tests/test_p01_fix10.py:289-310 | 全active+sources_status | `oD1['gate'] == 'PASS' and all(oD1['files'].get(c) for c in ('global','macro','china','rate_economy'))` | 物理导入子进程通道丢失/降级 | driver 负载扩展 gate 桶(core/noncore_missing)+基线四通道在场 + vintage 域 |
| 35 | tests/test_p01_fix11.py:138-162 | 同上 | POS 物理导入 driver `o_pos['gate'] == 'PASS'` | 同上 | 同上(driver 负载扩展) |
| 36 | tests/test_p01_fix11.py:250-270 | 同上 | srcst driver(负向侧伴随扩展) | 同上(负向不变) | 负向侧断言不变,仅负载字段伴随扩展 |
| 37 | tests/test_p02_w2_fix1.py:421-422 | 全active | `and snap10['gate_a']['status'] == 'PASS'` | 正常日降级 | vintage 域 |
| 38 | tests/test_p02_w2_fix1.py:517-526 | 全active | `snap_d1['gate_a']['status'] == 'PASS'`(D1 正常对照) | 同上 | vintage 域(meta 绑定断言保持) |
| 39 | tests/test_p02_w2_fix2.py:407-419 | 全active | `snapC['gate_a']['status'] == 'PASS'` | 同上(时刻语义变体) | vintage 域 |
| 40 | tests/test_p02_w3.py:757-765 | 全active | `gateO['gate_a']['status']=='PASS' and quality FAIL==0 and DEGRADED==0` | 金融事实链被新闻链回归 | vintage 域(quality 桶断言保持:fixture 事实全有效语义) |
| 41 | tests/test_p02_w3_fix1.py:773-781 | 全active | `and gateL['gate_a']['status'] == 'PASS'` | 同上 | 同上 |
| 42 | tests/test_p02_w3_fix2.py:573-579 | 全active | `and gateE['gate_a']['status'] == 'PASS'` | 同上 | 同上 |
| 43 | tests/test_p02_w3_fix3.py:637,710 | 全active | `gateE['gate_a']['status'] == 'PASS'`(两处) | 同上 | 同上 |
| 44 | tests/test_p02_w3_fix4.py:746,807 | 全active | `gateE['gate_a']['status'] == 'PASS'`(两处) | 同上 | 同上 |
| 45 | tests/test_p02_w5.py:684 | 全active | `self.assertEqual(checks.get('Gate A状态'), 'PASS')` | 验收报告 Gate A 漂移 | vintage 域(以重建快照判 vintage;重建确定性登记见 §一) |
| 46 | tests/test_p02_w5.py:807 | sources_status | `self.assertIn('sha256', rep['snapshot']['sources_status']['global'])` | 基线通道摘要结构 | 无需重构(已 vintage 中立: global∈基线四通道硬要求域);注记保留 |
| 47 | tests/test_p02_w1.py:71-72 | 81计数 | `len(_REG['metrics']) == 81 and len(by_id) == 81` | 缩水/重复 | T1 下限≥81 + T2 双射唯一(by_id 键集==metrics ID 集+无重复) |
| 48 | tests/test_p02_w1.py:73-76 | 80/32计数 | `n_active == 80 and n_core == 32` | active/core 缩水 | T1 下限≥80/≥32 + T2 实载派生 |
| 49 | tests/test_p02_w1.py:89-94 | 81计数 | `len(aud_ids)==81 and set(aud_ids)==set(by_id) and len(set(aud_ids))==81` | 审计清单漏项/重复/私货 | T2 审计集==注册表集∩vintage 锚 + 唯一 + T1 下限≥81 |
| 50 | tests/test_p02_w1.py:221-222 | 80/32计数 | `len(rp.core_metric_ids())==32 … len(rp.active_registry_metrics())==80` | core/active 漂移 | T1 下限 + 成员锚('SPX'/'UST_10Y'∈core 保持) |
| 51 | tests/test_p02_w1.py:258 | 81计数 | `len(fe.load_registry()['by_id']) == 81 and len(rp.core_metric_ids()) == 32` | 同上 | 同上 |
| 52 | tests/test_p02_w1_fix1.py:229 | 81计数 | `len(fe.load_registry()['by_id']) == 81` | 缩水 | T1 下限 + T2 实载 |
| 53 | tests/test_p02_w1_fix1.py:238-240 | 81/80/32计数 | `len(_REG['metrics'])==81 … core==32 … active==80` | 同上族 | 同上族 |
| 54 | tests/test_p02_w1_fix1.py:257 | 32计数 | `len(rp.core_metric_ids()) == 32 and 'SPX' in …` | core 漂移 | T1 下限+成员锚 |
| 55 | tests/test_p02_w1_fix1.py:270-271 | 81计数 | `len(aud_ids)==81 and len(set(aud_ids))==81 and set(aud_ids)==set(by_id)` | 审计清单完整性 | T2 集==注册表∩vintage+唯一+T1 |
| 56 | tests/test_p02_w1_fix1.py:305-306 | 81计数 | `len(fe.load_registry(force=True)['by_id']) == 81` | 默认注册表缩水 | T1 下限+T2 |
| 57 | tests/test_p02_w2.py:87-94 | 81计数 | `len(items)==81 and set(mat_by)==set(_BY) and len(mat_by)==81` | 政策矩阵漏项/私货/重复 | T2 矩阵集==注册表集∩vintage 锚+唯一+T1 下限≥81 |
| 58 | tests/test_p4_fixes.py:60-62 | p4环境敏感 | `real=ROOT/data/daily; data_dir = real if _glob.glob(real+'/global_2026*.json') else fixdir` | 环境依赖红/绿漂移(本地在场态月度序列提取 0→4 红) | 数据面 fixture 全 tmp 化: 提交内 `tests/fixtures/e2e/w4_data` 复制到独立 tmp 根,禁 ambient 分支 |

**清点边界注记(锚命中但不构成本包锁)**: `81项`字样于 docstring/输出文案/注释者(test_p02_w2_fix5.py:417 check 文案、各文件模块 docstring)=历史注记豁免类,零改动;`p4-data/daily` 形态命中中 `os.path.join(td,'data','daily')` 类=temp 内自建目录构造,非 ambient 依赖,零改动;test_fact_engine.py:39 `len(by_id) >= 80`=已具 T1 下限形态的既存锁,演进兼容无需重构,注记保留;test_p02_w4_fix2.py:668-676 `input_files==15`=fixture 计数锁(与注册表项数无关),零改动。

### 零.2 与 R023 归因对照(逐条注记)

| R023 归因 | 清点实证 | 注记 |
|---|---|---|
| ①81计数→w4族 | ✓ w4 族 5 文件 12 锁 | 一致 |
| ①'81计数字面宿主全集 | 字面 81/80/32 锁另宿于 test_p02_w1/w1_fix1/w2(非五族) | **清点实证扩充**: R023 归因描述 v1.2 实验**红面家族**(哪些套件因该机制红),非锁宿主全集;三源交叉实证 w1/w1_fix1/w2 实际承载 81 计数锁,按 §零(i)②"±清点实证出入"入 M 集(理由: 同机制同形态,不入集则 AC-02① grep 零残留不可达) |
| ②全active→p01_fix/w3/w5族 | ✓ p01_fix 硬锁宿主实证 **11 文件**(fix1~fix11 全数);w3×5 ✓;w5×1(test_p02_w5.py) | R023 记 p01_fix×10;引擎档不可达无法核对差额属哪一文件;11 文件逐一有锁位实证(§零.1 #13-36),按③"仅含实际承载锁文件"全数入集,**出入注记**待审计复核 |
| ③sources_status第5通道→p01_fix5/6/10/11 | ✓ fix5(#22-23)/fix10(#34)/fix11(#35-36)实证;fix6 的 sources_status 锁为 `ssp` 结构对照族(非通道枚举迭代),fix7/fix9 另有结构对照锁(#28/#33) | **通道数口径出入注记**: 代码现实=快照 sources_status 恒四采集通道(rp.SOURCE_FILE_RULES: global/macro/china/rate_economy);"五通道"实体=historical_coverage_audit.CHANNEL_PATTERNS 五通道模式(四采集+research_snapshot)。"第5通道结构锁"按**代码现实**落档: sources_status ⊇ 断言作用于基线四采集通道;数据面五通道全集锚用于 w4 审计通道覆盖域。R023 语言与代码现实的该出入已注记,不构成矛盾 |
| ④w2_fix×2 | ✓ 恰= test_p02_w2_fix1(#37-38)+test_p02_w2_fix2(#39)(硬 PASS 锁宿主恰 2 文件;fix3:472/fix4:624 已是 ('PASS','DEGRADED') 容差形态,fix5/fix6 无该锁) | 一致 |
| ⑤w3×5 | ✓ 5 文件(#40-44) | 一致 |
| ⑥w5×1 | ✓ test_p02_w5.py(#45-46) | 一致(w5_fix1/fix2/datasrc_b 无三机制硬锁,锚命中为零,不入集) |

### 零.3 M 集(改既有测试资产,28 文件)与 A 集(纯新增,k=5)

**M 集**(全部位于 `tests/` 树内;家族归属+理由如上;共享 fixture 模块 tests/fixt.py 被 M 集外文件引用(test_gate_chain_p01/test_e2e_orig14/test_e2e_frozen14 等 30 文件),按 §零(i)④**不入集**——vintage 域化一律落在 M 文件断言侧):

w4族: test_p02_w4.py, test_p02_w4_fix1.py, test_p02_w4_fix2.py, test_p02_w4_fix3.py, test_p02_w4_fix4.py
p01_fix族(11,含×10/×11出入注记): test_p01_fix1.py, test_p01_fix2.py, test_p01_fix3.py, test_p01_fix4.py, test_p01_fix5.py, test_p01_fix6.py, test_p01_fix7.py, test_p01_fix8.py, test_p01_fix9.py, test_p01_fix10.py, test_p01_fix11.py
w2_fix族: test_p02_w2_fix1.py, test_p02_w2_fix2.py
w3族: test_p02_w3.py, test_p02_w3_fix1.py, test_p02_w3_fix2.py, test_p02_w3_fix3.py, test_p02_w3_fix4.py
w5族: test_p02_w5.py
清点实证扩充族: test_p02_w1.py, test_p02_w1_fix1.py, test_p02_w2.py
p4环境敏感: test_p4_fixes.py

**A 集**(k=5): tests/test_p0_baseline_lock_equivalence.py(等价套件,必含);tests/helpers/baseline_locks.py(三联锁共享助手——复用面≥2 文件,必含);tests/helpers/__init__.py(包标识,空文件);docs/P0_BASELINE_RESTRUCT_REPORT.md(本文件);docs/P0_BASELINE_RESTRUCT_DELIVERY.md

### 零.4 冲突自检(情形(d)面,开工时点结论)

- 基线锁宿主在 tests/ 树外? **无**——58 锁行宿主全数在 tests/ 树内;生产代码(scripts/)中存在**语义对应物**(rp.SOURCE_CHANNELS/hca.CHANNEL_PATTERS/SOURCE_FILE_RULES 为通道权威定义),它们是被测生产面而非"锁",零改动。
- 家族结构性矛盾? **无**——出入均为注记级(零.2 表),无矛盾。
- 三联锁某形态不可构造? **无**——三机制各有可构造实现(§一登记)。
- 结论: 无情形(d)面冲突,开工。

### 零.5 基线 test 函数数(M 集逐文件,方法=AST 计数: ast.walk 数 FunctionDef 名前缀 `test_`;check() 调用数为脚本式套件补充登记,非合同计量)

| 文件 | test_funcs(基线) | check_calls(基线,补充) |
|---|---|---|
| test_p02_w4.py | 36 | 0 |
| test_p02_w4_fix1.py | 40 | 0 |
| test_p02_w4_fix2.py | 34 | 0 |
| test_p02_w4_fix3.py | 34 | 0 |
| test_p02_w4_fix4.py | 41 | 0 |
| test_p01_fix1.py | 0 | 78 |
| test_p01_fix2.py | 0 | 96 |
| test_p01_fix3.py | 0 | 40 |
| test_p01_fix4.py | 0 | 23 |
| test_p01_fix5.py | 0 | 45 |
| test_p01_fix6.py | 0 | 33 |
| test_p01_fix7.py | 0 | 41 |
| test_p01_fix8.py | 0 | 52 |
| test_p01_fix9.py | 0 | 43 |
| test_p01_fix10.py | 0 | 30 |
| test_p01_fix11.py | 0 | 18 |
| test_p02_w2_fix1.py | 0 | 41 |
| test_p02_w2_fix2.py | 0 | 34 |
| test_p02_w3.py | 0 | 38 |
| test_p02_w3_fix1.py | 0 | 44 |
| test_p02_w3_fix2.py | 0 | 26 |
| test_p02_w3_fix3.py | 0 | 26 |
| test_p02_w3_fix4.py | 0 | 35 |
| test_p02_w5.py | 32 | 0 |
| test_p02_w1.py | 0 | 40 |
| test_p02_w1_fix1.py | 0 | 36 |
| test_p02_w2.py | 0 | 44 |
| test_p4_fixes.py | 0 | 45 |

(终值对照表见 §二末;约束: 各 M 文件 test 函数数≥基线值,check 调用数不减。)

## §一 三联锁设计登记(参数/签名/vintage 规则——R011 登记型决策点纪律,先登记后实现,运行后禁回改)

**宿主**: `tests/helpers/baseline_locks.py`(commit bca2e0a;模块 docstring 即登记文本,本节为登记的登记制转录,二者不一致时以模块 docstring 为准)。签名/参数/返回一览:

### 一.1 T1 冻结下限锁(防缩水)

| 常量/函数 | 签名 | 语义 |
|---|---|---|
| `REGISTRY_FLOOR=81` | 常量 | 注册表全量项数(含 deprecated)下限 |
| `ACTIVE_FLOOR=80` / `CORE_FLOOR=32` | 常量 | active / active+core 项数下限 |
| `W4_REPORT_ROWS_FLOOR=82` | 常量 | w4 机器报告逐项表行数下限(表头 1+81) |
| `BASELINE_SOURCE_CHANNELS` | 4 元组 | 基线四采集通道(global/macro/china/rate_economy),任何 vintage 硬 active 域 |
| `BASELINE_DATA_CHANNELS` | 5 元组 | 数据面五通道全集(四采集+research_snapshot;=hca.CHANNEL_PATTERNS 基线值),w4 审计通道覆盖域锚 |
| `BASELINE_VINTAGE_IDS` | frozenset(81) | 封版 vintage 锚,机器生成自 BASE-BR 基线态注册表零手抄(溯源 `VINTAGE_PROVENANCE`;生成指令入证据包 discovery/)。语义=「fixture 时点已存在的注册表条目」,仅用于下限/包含判断,禁与实载注册表整集相等 |
| `registry_counts_ok(reg=None)` | →(ok,why) | 全量≥81 ∧ active≥80 ∧ core≥32 三面下限 |
| `baseline_removals(reg=None)` | →set | 实载注册表缺失的 vintage 基线条目(必须为空;与计数下限互为冗余双面) |
| `vintage_additions(reg=None)` | →set | 时点后新增条目(合法演进不回溯要求域) |

### 一.2 T2 派生完备锁(防腐化——期望值一律自单一事实源实载派生,弃字面常量)

| 函数 | 签名 | 派生源与语义 |
|---|---|---|
| `registry_doc(reg=None)` | →dict | 默认实读 `config/metric_registry.json`;`reg` 注入时用于变体,不落盘不触生产文件 |
| `registry_metric_ids / active_metric_ids / core_metric_ids_loaded(reg=None)` | →set | 三态 ID 集,一律派生自 `registry_doc` |
| `expected_registry_count(reg=None)` | →int | w4 族派生期望: 审计结果项数==实载注册表项数 |
| `ids_unique_bijection_ok(reg=None)` | →(ok,why) | metrics 无重复 ∧ by_id 键集==metrics ID 集(双射)。by_id 口径: 生产原始 JSON 不含 by_id(fe.load_registry 加载时派生)——无注入以 fe 实载为准,注入自带 by_id 按注入比对(N3 由此红),缺省按生产同式派生 |
| `artifact_covers_vintage_baseline(artifact_ids, reg=None)` | →(ok,why) | 封版工件(审计清单/政策矩阵)恰覆盖 注册表∩vintage 锚: 唯一+无缺+无私货+∩≥81;时点后新增不要求工件回溯补录 |
| `gate_vintage_ok(gate, reg=None)` | →(ok,why) | 全 active 契约 vintage 域: `gate` 接受快照 gate_a dict(status)或 recompute 结果 dict(effective);合法=PASS(恒);或 DEGRADED 且 core_missing/core_fail/noncore_fail/noncore_degraded 全空 且 noncore_missing⊆vintage_additions(基线通道/指标静默死亡在此红) |
| `sources_status_baseline_ok(sources_status, require='EXACT'\|'FALLBACK', reg=None)` | →(ok,problems) | ① ⊇基线四通道逐通道 status==require(硬 active);② 每个在场通道委托生产校验器 `rp.sources_status_problems` 结构口径;③ 新增通道仅②,不回溯 EXACT |

### 一.3 T3 自洽演进锁(防静默未登记演进)

| 函数 | 签名 | 语义 |
|---|---|---|
| `registry_self_consistent(reg=None)` | →(ok,problems) | 双射唯一 + `rsem.validate_registry` 零 error(自洽破坏/重复/映射漂移 @任意 N 捕获) |
| `evolution_legal(reg=None)` | →(ok,problems) | 自洽前件 + vintage 后新增条目全字段合规: status∈('active','deprecated','pending')、source∈rsem.KNOWN_SOURCES 且映射通道∈rp.SOURCE_FILE_RULES(collector→channel 映射表内置;'(derived)' 源免通道登记)、calendar∈rsem.KNOWN_CALENDARS、unit∈rsem.KNOWN_UNITS |
| `reset_registry_caches()` | →None | 注入配套: 清 fe._REGISTRY_CACHE/rp._CORE_CACHE/rp._ACTIVE_CACHE——monkeypatch fe.load_registry 后必调,否则派生集仍旧注册表(注入失真) |

### 一.4 vintage 判定规则(登记)

条目属「fixture 时点已存在」iff metric_id∈BASELINE_VINTAGE_IDS;时点后新增(=实载−vintage 锚)不回溯要求。Gate A 正常日断言允许 DEGRADED 仅当 core_missing/core_fail/noncore_fail/noncore_degraded 全空 且 noncore_missing⊆时点后新增集;**基线四采集通道在任何 vintage 均 active 硬要求**(sources_status ⊇ 且逐通道 EXACT/FALLBACK 形态)。PENDING 形态由条目级 status='pending' 承载(不计入 active 期望,天然不产生 noncore_missing);通道级 PENDING 不在生产词汇表,不扩生产语义(出入注记见 §零.2③)。

### 一.5 重建确定性注记(w5/fix8 伴随)

w5 #45 与 fix8 #32 的原锁为「报告/预检输出 Gate A==PASS」文案锁,重构后断言基面换成**重建快照**(`sb.build_snapshot(...)` 产物)的 gate_a——两文件断言因此共享同一确定性来源: 同一 fixture 数据目录+同一 target_ymd+同一 as_of 输入下 build_snapshot 纯函数化,报告侧 `checks['Gate A状态']` 与重建快照 gate_a.status 逐字相等(等式双侧同源,文案漂移不再依赖字面 'PASS')。该注记随 commit 9df5c56 落档。

## §二 逐文件重构摘要

**w4 族 5 文件**(commit de11602)——81 计数锁 12 处全数替换: T1 冻结下限(≥81/≥82)+T2 实载派生(结果项数/桶和/registry 回显/逐项表行数==实载注册表项数,弃字面常量),对应清点表 #1-#12。漏项/私货/重复/缩水回归类由集合全等+唯一+下限三面保持捕获;注册表合法演进(81→85)不撞墙。

**p01_fix 族 11 文件**(commits a662434/a73ec5c/135cd9a)——fix1/fix2: gate_a 基线 PASS 断言→`bl.gate_vintage_ok`(快照 gate,基线通道硬 active,演进日 DEGRADED 且 noncore_missing⊆vintage 新增为可接受);重算矩阵 #14/15 与 gate_status 裁决三处(#15b/c/d)放行真实状态。fix3: #17 meta 一致性+vintage 域。fix4: #18/#19/#20 声明/重算同变体。fix5: #21 vintage 域+≥78 下限保持;#22/#23 → `bl.sources_status_baseline_ok(...,require='EXACT'/'FALLBACK')`+基线四通道 file_date==DAY/PREV_D。fix6: #26 六处重算对照 vintage 域+#27 meta 一致性。fix7: #28 ssp 结构本体保留+追加 ⊇基线四通道在场增强;#29/#30 vintage 域。fix8: #31 基线四通道==rp.SOURCE_CHANNELS 实载全等(通道枚举同步演进)+逐通道 sha256 结构;#32 报告 Gate A→重建快照 vintage 判定。fix9: #33 结构族保留+⊇增强,另加 +C0 检查(43→44)。fix10/fix11: #34/#35/#36 driver 负载扩展(gate 桶+gate_a 全量+基线四通道在场),负向侧断言不变。

**w2_fix 族 2 文件**(commit 9df5c56)——#37/#38/#39 快照 gate PASS 锁→vintage 域(`bl.gate_vintage_ok(snap['gate_a'])[0]`),D 对照 meta 绑定断言保持。

**w3 族 5 文件**(commit 9df5c56)——#40-#44 gate PASS 锁→vintage 域;quality 桶断言(FAIL==0/DEGRADED==0)保持 fixture 事实全有效语义;#40 final_quality==gate_a 一致性。

**w5 族 1 文件**(commit 9df5c56)——#45 重建快照判定(`sb.build_snapshot` 产物 gate_a vs 报告 checks['Gate A状态'] 逐字相等,确定性注记 §一.5);#46 global∈基线四通道硬要求域,原样保持注记。

**清点实证扩充族 3 文件**(commit 9df5c56)——w1/w1_fix1/w2 计数锁→T1 下限+`bl.artifact_covers_vintage_baseline`(审计清单/政策矩阵恰覆盖注册表∩vintage)+双射唯一+成员锚('SPX'/'UST_10Y'∈core 保持)。

**p4 环境敏感 1 文件**(commit d058cbe)——ambient 分支删除: `tests/fixtures/e2e/w4_data` 提交内 fixture 恒 `copytree` 到独立 tmp 根作 data_dir,禁 ambient `data/daily` 依赖(双态记录 §五)。

**邻接修复 8 处**(commit 94c6e84,演进敏感邻接锁——合法 85 预演首跑红面清单,不在 §零.1 清点表内但同为全 active/一致性语义): fix1 声明断言 got is None 分支化、fix1 FAIL重跑 final_quality==gate_a+`bl.gate_vintage_ok`、fix3/w3 final_quality==gate_a 一致性、fix6 D对照 `set(noncore_missing)-set(vintage_additions)=={'UMCSENT'}`、fix7 R5 干净形态、w2_fix2 G1/w2 G1 `bl.gate_vintage_ok(snap gate)[0]`。

### 二.1 终值计量对照表(AST 计数;约束: test 函数数≥基线,check 调用数不减)

| 文件 | tf 基线→终值 | ck 基线→终值 | 备注 |
|---|---|---|---|
| test_p02_w4.py | 36→36 | — | unittest 类族 |
| test_p02_w4_fix1.py | 40→40 | — | |
| test_p02_w4_fix2.py | 34→34 | — | |
| test_p02_w4_fix3.py | 34→34 | — | |
| test_p02_w4_fix4.py | 41→41 | — | |
| test_p01_fix1.py | — | 78→78 | |
| test_p01_fix2.py | — | 96→96 | |
| test_p01_fix3.py | — | 40→40 | |
| test_p01_fix4.py | — | 23→23 | |
| test_p01_fix5.py | — | 45→45 | |
| test_p01_fix6.py | — | 33→33 | |
| test_p01_fix7.py | — | 41→41 | |
| test_p01_fix8.py | — | 52→52 | |
| test_p01_fix9.py | — | 43→44 | +C0 在场断言(只增) |
| test_p01_fix10.py | — | 30→30 | |
| test_p01_fix11.py | — | 18→18 | |
| test_p02_w2_fix1.py | — | 41→41 | |
| test_p02_w2_fix2.py | — | 34→34 | |
| test_p02_w3.py | — | 38→38 | |
| test_p02_w3_fix1.py | — | 44→44 | |
| test_p02_w3_fix2.py | — | 26→26 | |
| test_p02_w3_fix3.py | — | 26→26 | |
| test_p02_w3_fix4.py | — | 35→35 | |
| test_p02_w5.py | 32→32 | — | unittest 类族 |
| test_p02_w1.py | — | 40→40 | |
| test_p02_w1_fix1.py | — | 36→36 | |
| test_p02_w2.py | — | 44→44 | |
| test_p4_fixes.py | — | 45→45 | 隔离化不动断言数 |

28/28 只增不减(仅 fix9 43→44 一处净增);计数脚本入证据包。

## §三 等价电池映射表+运行红面记录

**宿主**: `tests/test_p0_baseline_lock_equivalence.py`(A 集;脚本式,`python3 tests/test_p0_baseline_lock_equivalence.py`,退出码 0=全绿)。结构: Z0 基线态对照(注入前先证锁活着,防「恒红假等价」)→ N1-N7+ 负向注入电池(进程内 deep-copy 注入+monkeypatch,运行后还原)→ R 三态演进预演(worktree 副本+子进程)。每项 docstring 引用原锁 文件:行号。

### 三.1 电池项 ↔ 清点回归类 1:1 映射(合同 AC-03)

| 电池项 | 注入态 | 咬合的锁 | 清点表对应(回归类) |
|---|---|---|---|
| Z0 | 基线态(不注入) | T1/T2/T3 全绿 | 对照锚(锁非恒红前提) |
| N1a | 注册表 81→80(删 UMCSENT) | T1 计数下限红 | #1/#2/#7-#12/#47/#51-#57(静默缩水) |
| N1a2 | 同上 | baseline_removals 恰={UMCSENT} | #1 集合面(缩水) |
| N1b | core 32→31(monkeypatch fe.load_registry+reset_registry_caches) | 生产路径 core 下限红(n=31<32);还原后==32 零残留(N1b2) | #48/#50/#54(core 缩水) |
| N1c | 审计工件删 UMCSENT 一行 | artifact 恰覆盖锁红(漏项) | #49/#55(审计清单漏项) |
| N2a | metrics 重复 SPX | T2 双射唯一红 | #6/#47(重复) |
| N2b | 审计工件夹带私货条目 | artifact 恰覆盖锁红(多) | #49/#57(私货) |
| N3a | by_id 缺 VIX(列表在册) | T2 双射红(映射漂移) | #47/#52/#56(映射漂移) |
| N3b(自洽) | 同 N3a 前件 | rsem.validate_registry error 经 T3 前件红 | #28/#33(结构损坏) |
| N3b(桶和) | by_status 桶和≠项数 | T2 sum==len 红 | #3/#9(丢桶/丢项) |
| N3c | 机器报告回显 81(实载注入 85) | T2 回显==实载红 | #4/#12(回显漂移) |
| N3d | 逐项表行数==项数(缺表头) | T2 行数==1+实载 红 | #5(丢行) |
| N4a | fixt 快照正常日 vintage 基线缺席 UMCSENT(gate=DEGRADED) | gate_vintage_ok 红(noncore_missing 含 vintage 条目) | #13-#21/#24/#26/#29/#30/#32/#37-#45(基线指标静默死亡) |
| N4b(对照) | 全齐日 | gate_vintage_ok 绿(锁非恒红) | 对照锚 |
| N4b(通道) | 基线通道 china status=MISSING | sources_status 结构锁红(基线通道硬 active) | #22/#34(基线通道死亡) |
| N5a/b/c/d | 新条目日历/source/status 未登记×3 + 合法 85 对照绿 | T3 evolution_legal 红×3/绿对照 | T3 面(静默未登记演进;宿主 w1:71 fe.load_registry 崩溃面互证) |
| N6a | sources_status 缺 china | 基线四通道在场红 | #22/#23/#28/#31/#33/#34/#35(通道缺席) |
| N6b(对照) | 四通道齐 EXACT | 结构锁绿(锁非恒红) | 对照锚 |
| N6c | rp.SOURCE_CHANNELS 缩水(monkeypatch 缺 china,还原后 ⊇ 成立=N6c2) | ⊇基线四通道红 | #31(通道枚举缩水) |
| N7a | 协同缩水(注册表−1 且审计结果同步−1) | 旧形态 T2-only 等值比较绿=**漏检实锤** | #1/#2(三联锁缺件弱化面) |
| N7b | 同 N7a 注入 | T1 下限红+artifact∩vintage<81 红(T1 必要性) | #1/#2 |
| N-还原 | 电池运行后 | 实载注册表态与 Z0 一致(工作树零污染) | 红线(注入不触生产) |

### 三.2 运行红面记录(关键咬合证据摘录)

- N1a: `注册表项数80<81(静默缩水)`;N1b: `core项数31<32`;N2a: `metrics重复metric_id:['SPX']`;N3a: `by_id与metrics不同步: 仅列表有['VIX']`;N4a: `noncore_missing含vintage基线条目:['UMCSENT']`;N6c: `set(rp.SOURCE_CHANNELS)⊇基线四通道` 破;N7a: `res=80 reg=80`(旧形态绿=漏检)同注入 N7b 红。
- 恒红防线: Z0/N4b 对照/N5d/N6b 四处绿面(锁非恒红,注入可分辨)。
- 终值: **31/31 全绿,exit=0**(首次运行 N3c/N7b 两处电池自身构造缺陷——live 派生未接注入变体/artifact 锁未传注入 reg——修正后全绿,修正即电池语义自证的组成部分)。

## §四 演进兼容预演双向记录

**方法**(合同 AC-04): `git worktree add --detach <tmp> HEAD` 建纯副本→副本内覆写 `config/metric_registry.json` 为预演变体(合法 85/缩水 84/裸 85)→子进程逐套件运行 **M 集 28 文件零改动**→`git worktree remove`(副本全移除,主工作树零污染;套件内 R-还原 断言 worktree 清单回零)。预演变体语义: 合法 85=81+4 条日本利率新条目(BOJ_POLICY_RATE/JGB_2Y/JGB_5Y/JGB_10Y,source/日历/单位/通道/status 全登记,version 2.0.0→2.1.0,B3 DESIGN §六 口径);缩水 84=合法 85 删 vintage 基线条目 UMCSENT;裸 85=合法 85 但 JGB_2Y calendar='jp_unregistered'。

| 方向 | 注入 | 载体 | 结果 | 证据 |
|---|---|---|---|---|
| ①合法演进 | registry→85(全登记) | M 集 28 套件 | **28/28 全绿(reds=0)**——演进不撞墙,B3 重冻发车前提成立 | R[legal85] |
| ②非法缩水 | registry→84(删 vintage 基线条目) | 载体 4 套件(w1/w1_fix1/w2/w4) | **红面 4/4**: w1 A5/w1_fix1 E1/w2 A1 artifact 锁红「注册表∩vintage=80<81(基线条目被删)」;w4 StopIteration(UMCSENT 行查表落空)——防缩水面咬合 | R[shrink84] |
| ③非法裸演进 | registry→85(JGB_2Y 日历未登记) | 载体 w1 | **红面 1/1**: fe.load_registry 加载即 AssertionError「JGB_2Y日历非法: jp_unregistered」——静默未登记演进被 T3 前件(生产校验器)拦截 | R[bare85] |

双向结论: 演进合法(①)不撞墙 ∧ 演进非法(②③)必红——AC-04①② 双面成立。预演构造脚本与三变体 JSON 入证据包(`rehearsal/`)。

## §五 test_p4_fixes 双态运行记录

**重构**(commit d058cbe): 删除 ambient 分支(`real if glob(data/daily/global_2026*.json) else fixdir`)→恒定 `tests/fixtures/e2e/w4_data` `copytree` 到独立 tmp 根作 data_dir。断言数不动(45 check 调用)。

| 态 | 环境 | 结果 |
|---|---|---|
| ambient 态 | 主工作树(ambient `data/daily` 在场,基线红面环境) | **43/0,exit=0** |
| isolated 态 | `git worktree add --detach`(HEAD 提交树,无未跟踪 `data/daily`) | **43/0,exit=0** |

双态同绿=环境依赖消除(基线态下该套件 ambient 在场时月度序列提取 4 红的漂移面不复存在;脚本 `p4_dual.py` 入证据包 `p4/`)。无 @skip/xfail。

## §六 本地全量实测表

**口径**: 与 CI 同构(`for t in tests/test_*.py`,排除 test_glm_live 付费套件;`python3` 直跑逐套退出码)。驱动脚本与逐套日志/summary.csv 入证据包 `fullrun/`。

**结果**: **66 文件 → 65 运行 → 65 绿 / 0 红 / exit=0,总耗时 323s**(64 基线套件 + 1 新增等价套件 test_p0_baseline_lock_equivalence exit=0 146.8s)。

对照基线态: BASE-BR-CI-SUITES=64(本地基线实测 63 绿+test_p4_fixes ambient 红)→本包后 65/65 全绿——test_p4_fixes 经 §五隔离化在本地 ambient 在场态亦绿(基线漂移面消除);其余 64 套件与基线逐一对照零新红(无回归)。逐套行(名称/exit/秒)见证据包 `fullrun/summary.csv`(66 行,含 skipped 行)。

## §七 谱系(基线/分支/尖端/SHA 链)

- **BASE-BR**: `5e9fc88650b9d4a483e83b6638cbc984f8e7b514`(冻结时 origin/main 尖端,ls-remote 实取核对一致)
- **分支**: `dev/p0-baseline-restruct`(自 BASE-BR 切出,纯线性,`git merge-base --is-ancestor` 核验)
- **SHA 链**(11 提交,均无 merge/reset/amend):

| # | SHA | 内容 |
|---|---|---|
| 1 | 2503ccf | 清点登记(§零 58 锁表+M28/A5+冲突自检) |
| 2 | de11602 | w4 族 5 文件(81 计数 12 锁→T1+T2) |
| 3 | bca2e0a | 三联锁共享助手 tests/helpers/baseline_locks.py |
| 4 | a662434 | p01_fix 1/11-2/11(fix1/fix2 vintage 域) |
| 5 | a73ec5c | p01_fix 3/11-5/11(fix3/4/5+sources_status 基线域) |
| 6 | 135cd9a | p01_fix 6/11-11/11(fix6-11) |
| 7 | 9df5c56 | w2_fix/w3/w5/扩充族 11 文件 |
| 8 | d058cbe | p4 环境隔离(fixture tmp 化) |
| 9 | 94c6e84 | 预演红面修复(8 邻接演进敏感锁 vintage 域化) |
| 10 | ea5d230 | 等价套件(31/31)+REPORT §一-§五 |
| 11 | (本提交) | REPORT §六/§七终版+DELIVERY |
