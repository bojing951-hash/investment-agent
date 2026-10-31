# IA-P0-2-W4-FIX2 交付说明(合法覆盖槽位+逐指标完整文件溯源)

任务: IA-P0-2-W4-FIX2-DEV-v1.0 | 验收契约: IA-P0-2-W4-FIX2-AC-v1.0
性质: W4-FIX1独立验收失败后的定向增量修复(两项缺陷+两项交付,不重建审计器)
基线: FIX1最终失败Commit `5c65b231e40d33886f533cfe519e76d5819ddaa3`(FIX1最终
CI run 41196364762,47/47绿但验收判FAILED);W4首轮 `62c1661`;W3封版
`497b02c7b770d4eadb9086d453fea14d275bd4c9`;GitHub main仍=P0-1封印
`50b5d13db6c477084c6f4b3944b7bd08a8e329d6`(禁合并)。

---

## 1. 修复范围(只针对FIX1验收失败的两项缺陷+两项交付)

1. **FIX2-01 非交易日观测虚增覆盖**: 旧实现`n_slots=len(obs_keys)`把日历外
   槽位重新计入→仅周末采集的日频观测被当成2个独立样本,状态虚增。
2. **FIX2-02 逐指标缺完整贡献文件追溯**: 旧实现只有
   `series_files_sample/point_files_sample[:3]`样例截断,无机器可核的全量
   贡献文件清单。
3. 交付①: 最终真实数据审计(§7,在最终固定Commit上执行)。
4. 交付②: 最终DEV/LIVE只读隔离证据(§15)。

FIX1已通过的修复全部保留: 槽位连续段/重复拆分/MARGIN_BAL口径/五通道发现/
git元数据/Manifest+SHA-256/81项输出(经C组历史合同回归逐项锁定,§10)。

## 2. FIX2实现(全部修改限于允许清单四文件)

增量Diff(`5c65b231→FIX2最终SHA`): scripts/historical_coverage_audit.py
(1238→约1350行,纯增量修复);tests/test_p02_w4_fix2.py(新增34检查);
tests/test_p02_w4_fix1.py(3处预期修订,§11);tests/test_p02_w4.py(1处mock
签名同步,§11);docs/P0_2_W4_FIX2_DELIVERY.md(本文件)。
**未触碰**: fact_engine/snapshot_builder/trading_calendar/采集器/
metric_registry.json/新闻与W3来源保全/Gate A/B/P0-1~W3/生产文件/LIVE/
launchd/main。

## 3. FIX2-01 统一合法覆盖槽位

- 新纯函数`eligible_slots(auth_dates, freq, calendar)`(与split_slots同风格,
  亦是负向敏感性注入缝): **合法槽位=权威观测槽位键∩expected_slots预期槽位
  序列**;日历外(extra)完整保留只披露,不入正式覆盖统计/连续段/状态分类。
  返回(expected数, observed数, missing键, extra键, certified, 日历限制,
  原因);无法认证时expected/observed=None。
- `n_slots=observed_slots=len(eligible)`;`unique_observation_slots`同值;
  `expected`/`coverage_ratio`/`missing_slots`只按预期序列口径;同月/同周
  多个日期不虚增样本(月频键=自然月/周频键=ISO周一/日频键=交易日历日)。
- 新状态`NO_VALID_SLOTS`: 有权威观测日但无一落在预期槽位(如纯周末采集),
  优先于SINGLE判断,与MISSING(数据完全不存在)显式区分;findings4与summary
  (`no_valid_slots`计数)新增该键,定义公开写入报告。
- 新状态`UNDETERMINED`(§4.3): 预期槽位无法确定——不以`len(auth_dates)`冒充
  已认证槽位数(`unique_observation_slots=None`+`slots_certified=false`),
  不推导连续覆盖,输出`slots_unavailable_reason`限制说明,状态不冒充
  OBSERVED确定性结论;不改变有足够真实槽位证据的正常指标状态
  (registry频率全覆盖daily/weekly/monthly,真实数据预期不出现该状态)。
- §4.4下游全链同步: coverage全部槽位字段/status/continuous_segments/
  usable_intervals/summary.by_status/core_by_status/
  with_authority_observations(NO_VALID_SLOTS与UNDETERMINED均不计入)/
  findings4/完整历史判据(改用observed_slots)/自然日回退判据(加
  `unique_observation_slots is None`条件,NO_VALID_SLOTS不冒用)。
- 不变量(槽位可靠时,测试A9全81项逐指标核验):
  `unique_observation_slots==observed_slots==sum(segments.slots)`;
  `longest≤observed_slots`;日历外观测不进连续覆盖。
- classify签名增第6位`slots_certified`(默认True,旧调用兼容)。

## 4. FIX2-02 逐指标完整input_files

- 每指标机器字段`input_files`(逐条): `relpath/channel/record_types/
  raw_records/valid_records/invalid_records/authority_records/
  non_authority_records/invalid_reasons(去重[:5])/valid_observation_
  contributed`+Manifest关联字段(`manifest_sha256/size/mtime_ns/
  manifest_association`)。
- **全量不截断**: 文件去重(同文件多类型聚合为一条,record_types并集,原始
  记录计数不变),100文件→全部100(B2/B12: 10文件与15文件全列);旧
  `*_files_sample[:3]`保留为样例不冒充全量。
- **区分权威/非权威/仅无效**: authority_records/non_authority_records分计;
  非权威(research_snapshot)文件可追溯但不增权威历史(B5: GOLD_F仍MISSING);
  无效观测文件可追溯但不增有效样本——文件发现事实(presence in list)与
  `valid_observation_contributed`显式区分(B6/B7/B8);derived块登记
  `derived_no_observation_date`。
- **登记贯穿全部路径**: point/series/快照point/快照series/legacy/
  margin/ah/southbound/shape失败(not_dict/not_list)/length_mismatch/
  invalid_date/invalid_value——不遗漏任何使该文件被读过的原因。
- **Manifest关联**(新函数`_associate_input_files`,注入缝): relpath唯一匹配
  →补sha256/size/mtime_ns;channel一致性核验;无法关联=显式完整性错误
  `integrity.input_files_association_problems`(not_in_manifest/
  channel_mismatch),不静默省略。
- 不引入数据库、不复制原始数值(只存身份+计数)。
- 完全缺失指标`input_files==[]`(字段恒在,B9)。

## 5. 状态分类公开定义(FIX2后)

| 状态 | 判据 |
|---|---|
| DERIVED_ONLY | 派生指标(无独立原始存档) |
| MISSING/UNREADABLE | 无权威观测日(后者=输入全不可读) |
| UNDETERMINED | 有权威观测日但预期槽位无法认证(§4.3,不冒充确定结论) |
| NO_VALID_SLOTS | 有权威观测日但无一落在预期槽位(≠MISSING) |
| SINGLE_OBSERVATION | 合法槽位=1 |
| SPARSE | 合法槽位覆盖率<0.5 |
| OBSERVED | 其余(≥2合法独立槽位) |

## 6. SCHEMA_VERSION
`w4-coverage-audit/1.1`→`**1.2**`(FIX2-01/02语义变更)。

## 7. 新专项测试(tests/test_p02_w4_fix2.py,34检查,全部真实run_audit/main)
- **A组9**(§四固定反例A-D+): A=SPX周五+周六→raw2/槽1/日历外1/SINGLE;
  B=NDX纯周末→槽0/NO_VALID_SLOTS/segments[]/≠MISSING(VIX对照);C=RUT
  周五→周一→2槽OBSERVED;D=AHE同月两日期→1槽SINGLE;周频同周→1槽;
  日频缺合法交易日→槽2/缺1/断2段;§4.3注入→UNDETERMINED不冒充OBSERVED
  (基线RUT仍OBSERVED);§4.4下游同步+统计可复算;不变量全81项核验。
- **B组12**: 单文件字段全/10文件全量/同文件point+series聚合(3条记录)/
  多文件同日重复(跨文件重复计数保留)/非权威snapshot可追溯不增权威/
  无效日期/无效数值/长度不一致(文件级无效,状态MISSING但文件在清单)/
  完全缺失空表/Manifest全局关联(含integrity空问题)/SHA-256+size+mtime_ns
  独立重算对磁盘实物/15文件去重无截断(sample仍是样例)。
- **C组8**(历史合同回归): NFP缺月断段/WTI月内3日期2槽/同文件+跨文件重复
  不变量(指令§五固定例直算)/MARGIN_BAL仅rzye_billion不得权威/china-only
  五通道子集COMPLETED/audit_commit=真实git HEAD+generated_at UTC/输入只读
  (审计前后SHA-256不变)/报告统计可复现+新状态键+schema 1.2。
- **D组5**(负向退化必检出): 恢复n_slots=len(obs_keys)→A1/A2失败;恢复
  日期数判状态+无视可认证性→A2/A7失败;input_files[:3]截断→B2/B12失败;
  快照写成权威(_add_point auth翻转)→B5失败;删Manifest映射→B10/B11失败。
  全部经mock注入缝(eligible_slots/classify/build_metric_record/_add_point/
  _associate_input_files)+真实main()执行。

## 8. 旧测试修订(场景全保留,预期修正+理由)
1. **test_p02_w4_fix1.py::test_a9**: 注入expected_slots不可用下
   `GOLD_F status 'OBSERVED'→'UNDETERMINED'`。原断言即FIX2-01§4.3所指
   缺陷(以观测日数冒充已认证覆盖);fixture与注入不变,新增
   `unique_observation_slots is None`/`slots_certified false`断言。
2. **test_p02_w4_fix1.py::test_e3**: schema字面量1.1→1.2(§6)。
3. **test_p02_w4.py::test_e5**: classify负向mock同步第6参
   `slots_certified`(FIX1轮同款签名同步,注入语义不变)。
   其余fix1 37检查/w4 35检查未改动。

## 9. 全量历史回归(本地,推送前)
tests/下48个test_*.py: 47套执行全部exit=0(test_glm_live按workflow契约
排除),含test_p02_w4.py(36)/test_p02_w4_fix1.py(40)/test_p02_w4_fix2.py
(34)/W3及FIX1~5/W2及FIX1~6/W1/P0-1 FIX1~11/E2E/Gate A/B等全部通过
(逐套件退出码见§10 CI实证)。

## 10. GitHub最终CI(workflow_dispatch,dev/p0-2-w4)
实现Commit轮与最终固定Commit轮(本Commit)的Actions Run/Job ID/head_sha
核对/逐套件退出码见本文末"CI实证"节;**FIX1的47绿(41196364762)不作为
FIX2验收结果**,FIX2以新CI轮次为准(48文件-1排除=47套件,含新增
test_p02_w4_fix2.py)。

## 11. 正式真实数据审计(FIX2-04,最终Commit后执行)
- 数据: 复用W4授权冻结副本/Users/cast/audit/w4-real-data(848文件)前按§7.1
  重新核验: 目录存在/授权范围有效/文件计数与SHA-256与LIVE原件对应/来源
  清单完整/未授权文件不读——核验记录入Git外附件;核验不过→停止并如实报告
  NOT VERIFIED|REAL-DATA AUDIT PENDING。
- 在FIX2最终固定Commit上执行(audit_commit==最终GitHub SHA+真实
  generated_at+干净工作区),不得用FIX1旧输出;输出独立新目录(不覆盖FIX1
  产物): 4文件(JSON/MD/Manifest/日志)+冻结副本证明+文件数SHA核查+代码
  SHA+执行时间+退出码+81项新状态分布+完整input_files映射及验证+数据限制。
- **FIX1旧分布(71/2/2/6)不得沿用**: FIX2-01按合法槽位重算全部状态/覆盖率/
  连续段;新分布按新报告如实交付(数字以最终审计JSON为准,入Git外附件,
  不入Git)。

## 12. §7.5交付边界
真实报告与脱敏证据作为可读附件交用户再转Agent 4(可打包);禁上传API密钥/
环境变量秘密/未授权原始生产数据正文/私人研究内容;不截断81项记录或贡献
文件清单。

## 13. 未验证事项
- 真实生产数据金融数值真实性/W5研究充分性(全部research_sufficiency=
  UNDETERMINED)。
- LIVE在冻结副本时点后的新增文件不在授权集内。
- 日历近似(cn仅2026精确/hk最小集/fx周一五/FRED按NYSE近似)的单日级断点
  判定近似性——逐指标经calendar_limitations披露,非金融事实。
- MARGIN_BAL两融合计重建(须另行确认来源/单位/公式)。
- 历史瞬时事实只能以单次快照+SHA复检证明。

## 14. 提交与推送纪律
实现Commit→推送→CI run#1→文档回填→最终固定Commit→推送→CI run#2(最终
SHA)→正式审计→隔离核查→附件交付;此后不再新Commit(再出Commit须重新
固定SHA/CI/审计/隔离);不force push/不合并main(50b5d13)/不部署LIVE/
不启动W5或P0-3。FIX1时点的隔离证据不证明FIX2终态。

## 15. 最终状态
三选一结论见对话交付报告(材料齐全→READY FOR W4 INDEPENDENT ACCEPTANCE;
确定性阻断→FAILED;缺真实审计或隔离材料→NOT VERIFIED)。

---

## CI实证(workflow_dispatch, dev/p0-2-w4, offline-tests.yml)

### CI run#1 — FIX2实现Commit 5572cfd518fdacc86c5095207d7c56c9648579d2
- Actions Run ID: **41205021727** | Job ID: **124548242147**(tests)
- event=workflow_dispatch | head_branch=dev/p0-2-w4 | head_sha=5572cfd…(=实现Commit)
- conclusion=**success** | **48套件全部exit=0**(FIX1的47套件+新增
  test_p02_w4_fix2.py=48;test_glm_live按workflow契约排除未执行):
  test_datafix_20261017 / test_e2e_four_weeks / test_e2e_frozen14 /
  test_e2e_orig14 / test_fact_engine / test_gate_chain_p01 /
  test_p01_fix1~fix11(11套) / test_p02_w1 / test_p02_w1_fix1 / test_p02_w2 /
  test_p02_w2_fix1~fix6(6套) / test_p02_w3 / test_p02_w3_fix1~fix5(5套) /
  test_p02_w4 / test_p02_w4_fix1 / **test_p02_w4_fix2** / test_p0_fixes /
  test_p1_fixes / test_p2_fixes / test_p4_fixes / test_p7_fixes / test_phase3 /
  test_phase4 / test_round3_adversarial / test_round3_p0 / test_round4 /
  test_round5 / test_round6 / test_snapshot——逐套件退出码自Job
  124548242147日志逐行提取(`test_<name> exit=N`),全部=0。

### CI run#2 — FIX2最终固定Commit(本Commit)
- 按防预写纪律不入Git,见Git外附件IA-P0-2-W4-FIX2-REAL-AUDIT-*.txt与
  IA-P0-2-W4-FIX2-POSTCOMMIT-ISOLATION-*.txt及对话交付报告。
