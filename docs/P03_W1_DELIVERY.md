# IA-P03-W1 DELIVERY — E2E-A 确定性研究底座

- 分支 `dev/p03-e2ea` · 基点 e04c063d4c3b6ef7ffb71e3720e338094e7ebb9a · 2026-11-04
- 白名单符合性: **恰 6 文件纯新增(6A/0M/0D)**,白名单外零改动;研究档案落 `data/research/`(不 commit);`.gitignore` 未改;`data/daily` 只读(双次锚定零 delta)。

## 一、改动清单

| 文件 | 类型 | 内容摘要 |
|---|---|---|
| scripts/research_history_query.py | A | 指标ID+区间历史查询;双登记接入点(macro=resolve_inputs→normalize_macro 标准化层转递豁免;global=build_snapshot(write=False)→series_store);跨频率对齐(共同观测日内连接/ISO周/自然月,与 fact_engine 口径同构);区间变动(利率 pp+bp/价格 pct)与滚动相关;缺值剔除不填0 |
| scripts/anomaly_detector.py | A | RD-DIV-001 背离检测器,冻结参数(60/0.30/25.0bp/2.0%/含等号);全序列共同观测预热+窗口内评分;纯计算零网络零IO |
| scripts/research_task_manager.py | A | 任务 schema 最低字段集;状态机至 active;确定性 task_id;append-only 档案(幂等跳过/__vN 追加)+检测统计序列独立落档;E2E-A 编排入口(--run-e2e) |
| tests/test_p03_e2ea.py | A | 34 用例六类(T1-T6,见 REPORT §5.3);全合成 fixture/零网络/零新依赖/预期值字面量硬编码 |
| docs/P03_W1_E2EA_REPORT.md | A | 场景登记(registry 抄录/实际利率四级决策/接入点 file:line/窗口+探针依据)/参数冻结/逐模块设计/PENDING/证据指针 |
| docs/P03_W1_DELIVERY.md | A | 本文件(五节) |

## 二、证据清单(全量在 /tmp/p03-e2ea-evidence/,zip=IA-P03-W1-E2EA-EVIDENCE.zip+SHA256SUMS)

| 合同最低集 | 证据件 | 要点 |
|---|---|---|
| ①双次锚定清单 | manifest_daily_pre_run1.txt / manifest_daily_post_run2.txt / manifest_research_pre_run1.txt / manifest_research_post_run2.txt | data/daily 24 文件前后 **零 delta**;data/research 回放前不存在、回放后恰 3 档(逐档 sha256) |
| ②双次原始日志+退出码 | run1_raw.log / run2_raw.log | Run1 TRIGGERED(16 触发日,首 2026-08-21);Run2 skipped-idempotent,档案 sha256 03b4fd7d… 不变;exit 0×2(Run1 退出码注记见档尾,Run2 显式捕获) |
| ③档案全量副本+逐文件 sha256 | evidence 内 research_copies/ + manifest_research_post_run2.txt | 任务档+统计序列 _001/_002(内容确定性一致) |
| ④触发统计序列 | detection_series_2026-06-30_2026-09-30_001/002.json | 65 逐期行(rho/chg_r_bp/chg_g_pct/cond_corr/cond_move/triggered)档内直读 |
| ⑤git/ls-remote 全量 | git_local_state.txt / ls_remote_pre_push.txt / ls_remote_post_push.txt | push 前 27 支尖端快照;push 后唯一新增 dev/p03-e2ea,既有尖端零漂移 |
| ⑥CI 登记件引用 | rounds/011/P03-W1-CI-dispatch-evidence.md | 操作者 CHECKPOINT dispatch 后落档(本包不自行 dispatch);预期 55+1=56 套件 |
| ⑦两 docs | docs/P03_W1_E2EA_REPORT.md / docs/P03_W1_DELIVERY.md | 已随分支提交 |
| ⑧逐套件测试记录 | full_regression.log / negative_sensitivity.log / archive_verify.log / p4_fixes_preexisting_red_detail.log / test_p03_e2ea 单套件记录 | 56 套件=55绿+1既有红(§四);负向敏感 4/4 RED 后回绿 |

关键哈希: 任务档 sha256=03b4fd7d7cb9684ff1170de1a536bd67bd2952cf84390f5e1d13958006abd261(Run1=Run2 逐字节不变);检测统计序列 sha256=8d3c631aea7886276023947e45fefbbce821fcfe2b6f4d8a7a0675176269ca93(_001=_002 确定性一致)。

## 三、逐 AC 自评(合同 IA-P03-W1-E2EA-AC-v1.0)

| AC | 自评 | 依据(证据指针) |
|---|---|---|
| **01 历史查询与对齐(确定性)** | 过 | 双接入点登记 REPORT §1.3(file:line 实读);对齐规则登记且与 fact_engine 同构(ISO周/月=期内最后观测,区间基准=严格早于 start);利率 pp+bp=fe:128-131 同式;缺值 n_missing_dropped 不填0;合成预期字面量硬编码(T2 全类);T6 源码锁=唯一 open 且标豁免、零 daily 字样、零 glob。反例自检: 无直开(源码锁)、规则全登记、t2f 不足→available=False 非恒真、t1 清洗不填0 |
| **02 检测器行为(确定性)** | 过 | 三情形: 在场触发 t3b(恰 25.0bp+2.0% **含等号**边界可复现)/不在场不触发 t3c(24bp 次临界)+t3e(正常负相关)/临界 t3b 恰阈值;echo=常量=登记值 t3a 字面量+Run1/Run2 日志首行;运行后参数零回改(仅 2 次运行,零调参尝试) |
| **03 任务结构与档案(确定性)** | 过 | schema 10 字段全在场无缺(archive_verify.log;falsifiable_conditions 非空 3 条;evidence 含接入点+产物标识+计算指针+质量状态);状态机至 active(history None→pending→active);append-only: Run2 幂等跳过+既有档 sha256 不变;t4c/t4d 锁幂等与 __v2 追加;统计序列序号递增 t4e |
| **04 真实历史回放(真实子项)** | 过 | DEV 真实数据只读×2 次(登记窗口+同窗重放);触发→落档→档内直读可验(series_window 65 日+trigger_stats 逐期);①双锚定 data/daily 零 delta+新增仅 data/research;②如实: 触发结果落档,末行不触发如实保留,零调参;③日志全文+退出码+序列入证据包 |
| **05 引用真实性与只读边界** | 过 | 全部 file:line 实读核验(REPORT §1.1/§1.3 抽查表);否定性声明可 grep/diff 反证(T6 源码锁+manifest diff);diff 恰 6A 零 M/D;registry/fact_engine/snapshot_builder/采集器/评分装配/report_generator/data_validator/workflow/requirements 零改动;W4/W5 未接入(diff 无既有文件) |
| **06 范围/分支/生产隔离** | 过 | 线性提交、不碰 main、不 force/reset/amend;ls-remote 对照 27 支快照=既有尖端零漂移+唯一新增 dev/p03-e2ea(ls_remote_post_push.txt);零网络(全链离线)、零新增依赖、requirements 零改;LIVE 零写入(全流程无 LIVE 路径引用)、launchd 零触碰 |
| **07 CI 与证据包** | 部分(设计内) | 证据包 ①-⑧ 齐备+SHA256SUMS;DELIVERY 五节/result 四段齐备;**CI dispatch=操作者 CHECKPOINT 责任面**(本执行Agent不自行 dispatch),登记件将落 rounds/011/P03-W1-CI-dispatch-evidence.md——本条 CI 腿按合同流程留待操作者,其余腿已齐 |

**三态分流自判**: 确定性子项(01/02/03/05/06)全过+真实子项(04)齐备诚实+07 证据包腿齐备(CI 腿待操作者)→ 按合同 §九申请三态裁决;无上游漂移情形(b)不适用;窗口触发为真实结果,情形(c)分流未发生(如后续补证据轮需要,仅补真实重跑/调窗重放)。

**场景登记摘要**: 实际利率=第①级 TIPS_10Y 直用(registry L1223,DFII10 市场观测,优于派生"近似"项);黄金=GOLD_F(L493,COMEX 主力连续);窗口 2026-06-30→2026-09-30(TIPS +73bp & GOLD +3.7%,合同点名场景,探针依据 REPORT §1.4);冻结参数 RD-DIV-001: W=60/ρ≥0.30/≥25.0bp/≥2.0%/含等号/rounding 4-1-4(REPORT §二,冻结先于 Run 1)。

## 四、如实偏差

1. **Run 1 退出码为注记而非显式捕获**: Run 1 经 shell 重定向执行,执行器以正常完成状态返回(非零会报错,未发生);Run 2 起改用子进程捕获显式写 exit_code=0(run2_raw.log 尾行)。已在 run1_raw.log 尾部如实注记,未回改原始日志正文。
2. **test_p4_fixes.py 本地红(既有基线,与本包无关)**: 39 通过/4 失败,4 失败全在 monthly_review.build_data_block(月度序列提取/单位报告——依赖本地 data/daily 真实数据演化,P4 域)。本包改动全部为**新增**文件,与该套件零导入关系;该红在本包动工前已存在(R010 收包记录"既有本地红套件基点归因在案")。明细入证据包,不隐瞒不代修复(白名单外)。
3. **PENDING-1 结构性缺口(白名单外需求,登记不实施)**: macro 利率序列不经快照 series_store——TIPS_10Y 取数依合同豁免句"经标准化层转递"实现(单处 open 标记+T6 源码锁);统一序列面需改 snapshot_builder/fact_engine,建议 P0-3 后续包评估(REPORT §四)。
4. **PENDING-2 信息噪音**: normalize_macro 对 registry 外 A 股代码警告混入 E2E 日志(上游既有行为,保持原样未屏蔽,REPORT §四)。
5. **CI dispatch 未由本包执行**: 合同§七/任务§1 明示操作者 CHECKPOINT 责任面;本包已备齐 55+1=56 套件预期的本地记录,引用件路径已登记。若 CI 出现套件红/漂移→按情形(b)如实报告,不当场改 workflow。
6. **窗口选择探针直读了采集档(/tmp 探针脚本,已入证据包)**: 探针=选窗前的只读走势观察,零检测计算,非白名单模块;合同禁直读约束对象=新模块源码(三模块均守,T6 锁)。如实披露以备审计。
7. **GOLD_F 源值带浮点尾差(如 4186.700195)**: 采集档原始字节数值,按"不改口径/不改写"原则原样保留,仅在统计口径处 round。

## 五、参考

- 冻结合同: IA-P03-W1-E2EA-AC-v1.0(任务提示词 §10 内嵌全文;本轮 Round 011)
- 场景登记与设计详情: docs/P03_W1_E2EA_REPORT.md(同分支)
- 上游基线: e04c063(main 合并笔;R010 IA-DATA-W3 收包+P0-2 封版)
- 关键依赖(只读复用): scripts/snapshot_builder.py(:47/:236/:263-269/:358-382)、scripts/fact_engine.py(:81/:124-131/:196/:224-227/:244/:275)、scripts/correlation_calculator.py(:53-66/:69-80)、config/metric_registry.json
- 证据包: /tmp/p03-e2ea-evidence/IA-P03-W1-E2EA-EVIDENCE.zip(+SHA256SUMS)
