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

*(本节随 helper 实现提交填充终版;要点开工时点已定: 见零.1 各行方案列)*

## §二 逐文件重构摘要

*(随重构提交填充)*

## §三 等价电池映射表+运行红面记录

*(随等价套件提交填充)*

## §四 演进兼容预演双向记录

*(随预演运行填充)*

## §五 test_p4_fixes 双态运行记录

*(随 p4 隔离提交填充)*

## §六 本地全量实测表

*(随最终全量跑填充)*

## §七 谱系(基线/分支/尖端/SHA 链)

*(终版填充)*
