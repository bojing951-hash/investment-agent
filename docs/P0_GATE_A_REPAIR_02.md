# IA-P0-1-FIX2 整改开发报告(P0质量门禁第二轮修复)

- **日期**: 2026-10-27
- **角色**: 资深Python工程师(整改开发方)
- **仓库**: github.com/bojing951-hash/investment-agent,分支`main`
- **契约**: IA-P0-1-AC-v1.0 + IA-P0-1-FIX1-AC-v1.0 + IA-P0-1-FIX2-AC-v1.0(累积,均未改动)

---

## 1. 开发版本与Commit SHA

| 项 | 值 |
|---|---|
| 开发前基线(dev-before) | `a8114501263aba49d1079f6f6d656db6fd53ac19`(=开发开始时remote main,已核实) |
| Commit A(代码+测试) | `6abcc9399a2d8bde6f9aa9d51f460f90e4e46796`(`fix(p0): close FIX2 quality gate and publication blockers`,已推送) |
| Commit B(本报告) | 见`git log`(本文件所在commit) |
| Commit C(CI工作流,本地) | `.github/workflows/offline-tests.yml`;推送被GitHub拒绝(PAT缺`workflow` scope),commit留在本地待具备权限的凭据推送,见§11 |

开发在独立克隆`/tmp/inv-dev`进行,基线与remote一致,未覆盖任何未知改动,未强推。

## 2. 五项缺陷整改总览(FIX2-01~05)

| 缺陷 | 整改 | 主要落点 |
|---|---|---|
| FIX2-01(IA-DEF-001) 报告发布事务 | 报告先落**候选文件**(`weekly_report_{ymd}_CANDIDATE.md`);Gate B对候选执行;候选状态走**独立文件**`report_status_{ymd}_candidate.json`(awaiting_publish,任何读取方不得当发布状态);发布=备份旧正式文件(.prev.bak)→os.replace原子替换→`_atomic_write_json`原子写主状态(published=True);任一环失败:旧报告/旧状态字节级保持有效,新产物隔离`_UNVALIDATED`,失败记录指向真实文件;**绝不先把既有PASS主状态改成published=False**;序列化失败先于任何写(原文件不动);进程中断由`reconcile_publication`(主状态=权威指针+备份回滚)恢复;同日重发=刷新 | `scripts/report_generator.py`(generate_weekly_report事务段/write_report_status/write_candidate_status/reconcile_publication/_atomic_write_json);`run_weekly.py`(台账原子写) |
| FIX2-02(IA-DEF-002) Gate A事实重算 | 新增`rp.recompute_gate_a`:以**注册表32核心+facts实况**重算(core_missing/core_fail/noncore_fail/noncore_degraded/duplicates/illegal_quality/counts恰3键/overall),effective=FAIL(核心缺失∪核心FAIL∪重复)>DEGRADED(非核心FAIL/降级)>PASS;`gate_status`裁决链:格式→重算(损坏→None)→声明状态↔effective→声明清单↔重算清单→counts/overall↔重计,任何矛盾→None;overall(最差原始事实)与status(研究许可)语义区分、各自自洽 | `scripts/research_provenance.py` |
| FIX2-03(IA-DEF-003) 步骤依赖与报告授权 | 评分卡为**关键步骤**且其产物被装配进正式包:装配器/校验器依赖=评分卡+快照构建+全部4个关键采集器;评分卡失败→装配/校验SKIPPED(原因点名上游);当日无评分→包内显式披露缺失,仅有旧评分→包内标注【历史参考】(滞后天数);pack meta记录`scorecard_date/scorecard_current`,报告入口拒绝非当日评分;台账`allow_formal_report`=快照可用∧Gate A∈(PASS,DEGRADED)∧评分卡/装配/校验步骤成功;非关键(新闻/相关性)失败→降级运行,观察器不被阻止;DEGRADED日正常研究能力保留;另修复DEGRADED日装配器对非数值事实的格式化崩溃(`_fv`) | `run_weekly.py`(步骤依赖/台账);`scripts/data_assembler.py`(评分状态/披露/_fv);`scripts/report_generator.py`(入口核验) |
| FIX2-04(IA-DEF-004) 快照版本规范 | `_version_of`:base(=v1)或`_vN`(N≥2,**规范十进制**,无前导零);`_v0/_v00/_v1/_v01/_v02`等非法表示→该候选版本号None;选择器对任何非法/损坏/身份冲突/日期不符/同日重复版本→**整日拒绝**(None+原因),不静默忽略、不猜测回退次高版;合法多版时最高修订版规则保持;同日重建base→CLI exit 3(不可变),`--allow-revision`产`_v2+` | `scripts/research_provenance.py`;`scripts/snapshot_builder.py` |
| FIX2-05(IA-DEF-005) 来源元数据完整一致 | `verify_anchor_batch`:meta存在∧source=snapshot;请求日期=文件名日期=meta.target_date三方一致;必需字段(target_date/snapshot_id/snapshot_digest/anchors_digest/gate_a)缺一即拒;meta.gate_a须与权威快照Gate A一致且∈(PASS,DEGRADED)(FAIL批次不入正式链);两个digest无条件从实际字节/权威快照重算;锚点集合与数值经权威快照**确定性重建**比对(改数字+同步改摘要亦拒);FIX1全部实际内容绑定增益保留 | `scripts/research_provenance.py`;`scripts/snapshot_builder.py`(meta生成) |

## 3. 修改文件清单(Commit A)

| 文件 | 变更 |
|---|---|
| `scripts/report_generator.py` | FIX2-01事务(候选/状态分离/备份替换回滚/中断恢复/原子写);FIX2-03入口评分状态核验 |
| `scripts/research_provenance.py` | FIX2-02 recompute_gate_a/gate_status裁决链;FIX2-04版本规范;FIX2-05批次核验收紧 |
| `scripts/data_assembler.py` | FIX2-03评分状态(scorecard_state/历史参考标注/缺失披露/pack meta字段);`_fv`降级日数值安全格式化;main内缺陷修复 |
| `scripts/snapshot_builder.py` | FIX2-04版本规范/修订CLI;FIX2-05 meta生成 |
| `scripts/daily_report_generator.py` | 遗留日报双重UNVALIDATED自证(HTML注释+可见横幅) |
| `run_weekly.py` | FIX2-03步骤依赖图(装配/校验+评分卡)与台账allow/原子写 |
| `tests/fixt.py` | **新增**: 真实注册表全核心(32 core齐备)fixture——采集JSON→真实build_snapshot→真实装配/锚点/prompt |
| `tests/test_p01_fix2.py` | **新增**: 96断言(§1九类发布故障注入/§2重算矩阵/§3依赖授权/§4版本/§5元数据/§6§11兼容) |
| `tests/test_e2e_orig14.py` | **新增**: 41断言,14个强制场景全链路复测(真实CLI+阶段函数) |
| `tests/test_gate_chain_p01.py` | fixture改真实构建(85→86断言,详见§9) |
| `tests/test_p01_fix1.py` | fixture改真实构建(81→82断言,详见§9) |

未改动: 指标注册表(81指标/32核心)、事实引擎评分模型、GLM 5.3通道、论点/观点/预测状态与全部生产历史数据、launchd配置、三份冻结契约。`env_config.py`(本地文件,入库但本轮零改动,密钥来自环境/钥匙串占位)。

## 4. FIX1-DEF-001~008 保持情况

FIX1全部交付在Commit A后经全量回归保持生效,且新增真实fixture与全链路E2E提供更强证据:

| FIX1契约 | 本轮证据 |
|---|---|
| DEF-001 实际内容绑定 | test_e2e_orig14 S1-S5全链路(真实CLI产物上篡改→GLM=0拒绝) |
| DEF-002 合格报告保护 | test_p01_fix2 §1 C1-C9;e2e S11-13(字节级) |
| DEF-003 关键采集传导 | test_p01_fix2 §3(4采集器×SKIPPED);e2e S9 |
| DEF-004 预测观察验证 | test_gate_chain_p01 §8回归(86/0);fix2 §2锚点质量链 |
| DEF-005 Gate A真语义 | FIX2-02重算为其强化实现;fix2 §2矩阵 |
| DEF-006 修订身份 | fix2 §4(+e2e S6: 修订后旧包绑base→入口拒绝) |
| DEF-007 月季报旁路 | fix2 §6+e2e S14(UNVALIDATED草稿/dry-run/索引排除) |
| DEF-008 台账可追溯 | fix2 §3(allow=False证据化+SKIPPED原因) |

## 5. AC-01~13自检(IA-P0-1-AC-v1.0,未改动)

| AC | 结论 | 本轮证据 |
|---|---|---|
| AC-01 Gate A三态语义 | PASS(FIX2再强化) | recompute权威重算+声明矛盾拒绝;test_p01_fix2 §2(17项矩阵) |
| AC-02 流水线关键失败/依赖 | PASS(FIX2再强化) | 评分卡纳入关键依赖;fix2 §3;e2e S9 |
| AC-03 装配器不得绕过Gate A | PASS | e2e S8b: 真实da.main对FAIL日exit 2且**完全不产包** |
| AC-04 可验证来源绑定 | PASS(FIX2再强化) | FIX2-05必需字段+日期三方+无条件重算;fix2 §5 |
| AC-05 独立入口预检 | PASS | e2e S1-S7全部GLM=0前置拒绝 |
| AC-06 Gate A+B合成 | PASS | combine_gates未动;全部套件回归 |
| AC-07 FAIL报告不冒充合格 | PASS(FIX2事务化) | fix2 §1九类故障注入×字节级断言 |
| AC-08 长期状态保护 | PASS(FIX2字节级) | e2e各失败场景thesis/views沙箱前后字节一致;零回写 |
| AC-09 遗留入口 | PASS(附如实备注) | 遗留日报双重UNVALIDATED自证(fix2 §6/e2e S14d);**备注**: 其import面要求env_config提供DEEPSEEK_API_KEY/BASE_URL/MODEL三键,dev桩仅含API_KEY——测试对已加载模块对象注入空值完成离线验证(不改env_config.py,不引入密钥);生产env_config为本地完整文件 |
| AC-10 DEGRADED降级能力 | PASS | e2e S8a全链: DEGRADED发布成功+降级披露+页脚;`_fv`修复降级日装配崩溃 |
| AC-11 状态/来源/跳过可追溯 | PASS | fix2 §3台账断言;发布状态指向真实文件 |
| AC-12 核心功能无回归 | PASS | §9: 20离线套件1086断言0失败 |
| AC-13 测试/提交/交付证据 | PASS(CI部分阻断如实) | 本文件+§1 SHA+§9逐套件计数;CI见§11(不宣称CI通过) |

## 6. 第二轮验收(RAC)对照

**诚实声明**: RAC逐条编号文本未留存于本仓库(与FIX1报告§7同类情况),不伪造映射。第二轮验收结论为"6 FAIL/3 NOT VERIFIED",其FAIL项对应本轮FIX2-01~05五缺陷+CI未激活。对应关系: 发布事务缺陷→FIX2-01(§2/fix2§1);Gate A声明可信度→FIX2-02(§2/fix2§2);步骤依赖/授权→FIX2-03(§2/fix2§3);版本规范→FIX2-04(§2/fix2§4);元数据完整性→FIX2-05(§2/fix2§5);CI未激活→§11(本轮已尝试,凭据阻断,如实呈报)。若验收方RAC文本另有条目不在上列,即为缺口,接受据此判NOT VERIFIED。

## 7. F2-AC自检矩阵(IA-P0-1-FIX2-AC-v1.0)

| F2-AC | 要求 | 结论 | 证据 |
|---|---|---|---|
| F2-AC-01 | 发布事务: 候选独立/状态分离/不降级既有PASS/原子写/序列化失败不截断/发布失败保旧/隔离失败不损旧/中断无假发布/同日重发 | IMPLEMENTED | fix2 §1 C1-C9+原子写原语(每类含字节/状态/正式入口认定/无伪装合格/留痕/退出码六维);e2e S11-13 |
| F2-AC-02 | Gate A重算: 注册表权威/核心缺或FAIL→不放行/矛盾→不放行/非核心FAIL合理降级/非法质量不可证明/fixture须真实注册表全核心 | IMPLEMENTED | fix2 §2(重算层11项+裁决层11项,全量真实32核心fixture);**未**改criticality/未降阈值 |
| F2-AC-03 | 步骤依赖/授权: 评分卡关键且失败传导/旧评分仅历史参考/allow须有依据/入口拒非当日评分/SKIPPED留原因/非关键降级保留/观察不被无理阻断 | IMPLEMENTED | fix2 §3(10场景)+e2e S9;入口拒绝见fix2 §3末三例 |
| F2-AC-04 | 版本规范: 仅base+_v2+规范十进制/拒绝_v0,_v00,_v1,_v01,_v02、非规范、ID失配、日期失配/最高修订规则保留/真实FS测试 | IMPLEMENTED | fix2 §4(13项,含真实FS与CLI不可变性/修订) |
| F2-AC-05 | 元数据完整一致: 请求日期/文件名日期/meta.target_date/ID/版本/gate_a/摘要全量一致,冲突或缺失→拒 | IMPLEMENTED | fix2 §5(14项: 字段缺失×5/日期×2/谎报gate×2/digest×2/改数值+同步改摘要) |
| F2-AC-06 | §11兼容实测: 月/季CLI离线mock+遗留日报;未验证产物不被误认合格;月季历史/期间/dry-run保留;无日报模型迁移 | IMPLEMENTED | fix2 §6+e2e S14(dry-run零GLM/UNVALIDATED名+横幅/索引排除/日报双重自证);日报生成逻辑未迁移 |
| F2-AC-07 | 对抗测试真实性: 真实模块/临时文件+Mock/故障注入/无生产数据/无付费GLM/无源码字符串匹配 | IMPLEMENTED | fixt.py真实构建;全部断言针对运行结果与磁盘文件字节/JSON;唯一源码grep仅e2e S14c(索引排除规则存在性,行为断言在前) |
| F2-AC-08 | 原E2E-01~14为可运行测试(不得以自定义分类替代) | IMPLEMENTED(附编号声明) | tests/test_e2e_orig14.py: 14个强制场景原文逐条全链路复测41断言;原始编号未留存,按场景文字组织(同§6诚实声明),不删减不发明 |
| F2-AC-09 | CI激活: 显式Python版本/全部离线测试/14 E2E/失败即红/无密钥付费/实际生效 | **BLOCKED(如实)** | `.github/workflows/offline-tests.yml`已写入本地commit(Python 3.11/全部套件含E2E/排除test_glm_live/exit非零);**推送被GitHub拒绝**(PAT缺workflow scope,remote rejected原样留存);不宣称CI生效,见§11 |

## 8. E2E-01~14测试结果(tests/test_e2e_orig14.py,41断言全通过)

编号声明同§6/§7(F2-AC-08): 按验收指令留存的14个强制场景文字逐条复测,每条为**全链路**(采集JSON→snapshot_builder CLI真实子进程→macro_scorecard真实main→data_assembler真实main含Gate拒绝→锚点/prompt真实确定性构建→report_generator真实入口/GLM mock→Gate B→发布事务→长期状态字节保护):

| # | 场景 | 结果 |
|---|---|---|
| 1 | 数据包数字改变(仅改/改+同步改meta摘要) | ✅ 双变体exit 2,零GLM,状态文件字节不动 |
| 2 | 锚点数字改变(仅改/改+同步改摘要) | ✅ 双变体拒绝 |
| 3 | Prompt内容替换(换数字/追加伪造行) | ✅ 均拒绝 |
| 4 | 锚点meta摘要被改(anchors_digest/snapshot_digest) | ✅ 均拒绝 |
| 5 | 锚点残留旧指标(+meta同步) | ✅ 入口拒绝+批次核验原因点名残留键 |
| 6 | 快照文件名与内部身份冲突 | ✅ 同日重建exit 3;v2→v3确定性取最高;修订后旧包绑base→入口拒;_v2名自称base→整日拒 |
| 7 | Gate A声明与事实冲突 | ✅ 非核心FAIL谎报PASS/核心FAIL谎报DEGRADED/清单隐瞒→全拒 |
| 8 | 非核心单指标失败 | ✅ UMCSENT坏→DEGRADED全链发布+披露+页脚;SPX坏→装配器exit 2无包+入口exit 2零GLM |
| 9 | 关键采集失败后下游 | ✅ exit 1+装配/校验SKIPPED+allow=False+链路终点入口拒绝;新闻失败→exit 0降级 |
| 10 | 缺质量字段的预测观察锚点 | ✅ 批次核验拒绝(与权威重建不一致)+入口拒绝 |
| 11 | 既有合格报告被失败报告尝试覆盖 | ✅ 字节不变/主状态仍published/失败入UNVALIDATED侧车/零回写 |
| 12 | Gate B校验异常 | ✅ exit 3隔离,GLM恰1次,零回写 |
| 13 | 报告状态写入异常 | ✅ 首发布不留半发布态;已有合格→旧报告/旧状态字节不变 |
| 14 | 月/季/日报独立入口 | ✅ dry-run零GLM;UNVALIDATED名+横幅;索引排除;日报双重自证 |

## 9. 完整回归测试结果(逐套件)

环境: `~/AI内容/venv/bin/python3`(Python 3.9.6,stdlib-only)。命令: `cd /tmp/inv-dev && ~/AI内容/venv/bin/python3 tests/<套件>.py`,逐套件独立进程,退出码全0。

| 套件 | 断言 | 通过 | 失败 | 相对FIX1轮变化 |
|---|---|---|---|---|
| test_datafix_20261017 | 13 | 13 | 0 | 不变 |
| test_e2e_four_weeks | 59 | 59 | 0 | 不变 |
| **test_e2e_orig14(新增)** | 41 | 41 | 0 | 新增 |
| test_fact_engine | 59 | 59 | 0 | 不变 |
| test_gate_chain_p01 | 86 | 86 | 0 | 85→86(+1,见下) |
| test_glm_live | — | — | — | 跳过(需RUN_GLM_LIVE=1真实付费调用,契约排除) |
| test_p01_fix1 | 82 | 82 | 0 | 81→82(+1,见下) |
| **test_p01_fix2(新增)** | 96 | 96 | 0 | 新增 |
| test_p0_fixes | 22 | 22 | 0 | 不变 |
| test_p1_fixes | 36 | 36 | 0 | 不变 |
| test_p2_fixes | 82 | 82 | 0 | 不变 |
| test_p4_fixes | 43 | 43 | 0 | 不变 |
| test_p7_fixes | 30 | 30 | 0 | 不变 |
| test_phase3 | 47 | 47 | 0 | 不变 |
| test_phase4 | 20 | 20 | 0 | 不变 |
| test_round3_adversarial | 24 | 24 | 0 | 不变 |
| test_round3_p0 | 91 | 91 | 0 | 不变 |
| test_round4 | 94 | 94 | 0 | 不变 |
| test_round5 | 64 | 64 | 0 | 不变 |
| test_round6 | 51 | 51 | 0 | 不变 |
| test_snapshot | 46 | 46 | 0 | 不变 |
| **合计(20离线套件)** | **1086** | **1086** | **0** | |

**计数变化解释(均为新增/改写断言,零删除,零期望放宽)**:
1. `test_gate_chain_p01` 85→86: §1改用真实构建快照读三态(真实fixture替代手造最小dict),最小dict探针按FIX2-02新语义改为断言None(声明无事实不可信——收紧),新增1项断言。
2. `test_p01_fix1` 81→82: §10"同日重复版本"改写——`_v02`现被FIX2-04规范十进制规则判"非法版本"(收紧,先于重复检测命中),断言接受两种拒绝理由并新增1项。
3. 两套件fixture由"少量手造指标"改为fixt.py真实注册表全核心构建(F2-AC-07要求),断言语义不变或收紧;**未删除任何失败用例**。

**测试预期修正说明**: (a)上述两处均为收紧方向;(b)E2E S8b断言与真实装配器行为对齐——FAIL日装配器**完全不产包**(此前fixt路径曾造stale残留包,真实main从不写包),此为对齐真实行为而非放宽;(c)无其他修正,无测试文件删除。

## 10. 测试命令与独立复核

```
cd /tmp/inv-dev
~/AI内容/venv/bin/python3 tests/test_p01_fix2.py      # 96/0
~/AI内容/venv/bin/python3 tests/test_e2e_orig14.py    # 41/0
for t in tests/test_*.py; do ~/AI内容/venv/bin/python3 "$t" || echo "FAIL $t"; done
```
- fixture: tests/fixt.py——SYNTHETIC采集JSON(32核心齐备+非核心),经真实`snapshot_builder.build_snapshot`构建,Gate A为真实计算值;临时目录隔离,不触真实data/config/output/logs。
- GLM: 全部mock(_GLMRecorder/记录器,零付费,零网络);test_glm_live整套排除。
- 断言对象: 磁盘文件字节/JSON内容/退出码/调用计数,非源码字符串(唯一例外见F2-AC-07)。

## 11. GitHub Actions状态(如实)

- 已创建`.github/workflows/offline-tests.yml`(本地Commit C): `on: push/PR→main + workflow_dispatch`;`ubuntu-latest`+`actions/setup-python@v5`**显式python-version '3.11'**;循环跑`tests/test_*.py`全部离线套件(含test_p01_fix2与test_e2e_orig14=14场景E2E),显式排除test_glm_live;任一套件失败`exit 1`工作流失败;零secret/零网络/零付费。
- **推送被拒**: `remote rejected ... refusing to allow a Personal Access Token to create or update workflow without 'workflow' scope`(GitHub原文)。本轮第二次尝试(含在A中合并推送与单独commit推送各一次),均被拒——与FIX1轮结论一致: 当前PAT不具备workflow scope。**不宣称CI已生效,无run链接可提供**。
- 启用步骤(需持workflow scope凭据): `git push origin main`(本地Commit C已在main顶端)或仓库网页端添加同内容文件;推送后push/PR即自动触发。
- 在此之前,§8/§9全部结果为本地离线运行。

## 12. 尚未验证/已知事项(如实)

1. **CI未生效**(§11): workflow文件已就绪并本地提交,推送被凭据权限阻断;无法提供Actions run链接。
2. **真实GLM端到端**: test_glm_live仍按契约排除(付费);所有GLM调用点为mock。
3. **launchd真实调度日志**未采集(约束: 未触碰launchd配置)。
4. **已知边角(未修,如实记录)**: `monthly_review.build_data_block`在ROOT_DIR下无`config/thesis.json`时KeyError(生产环境该文件恒在;测试沙箱已含;属遗留健壮性问题,不在FIX2五缺陷范围,未扩scope)。
5. **遗留日报import面**: 需env_config提供DEEPSEEK三键(dev桩缺BASE_URL/MODEL);测试以空值注入已加载模块完成离线验证,未改env_config.py(AC-09备注)。

## 13. 部署与兼容

- 生产目录(live)同步: 本轮Commit A的11个代码/测试文件已同步至live(`🤖_AI投资项目/每周宏观追踪/investment-agent`),排除env_config.py/data/output/logs;无数据迁移,无配置变更。
- 兼容: run_daily.sh/run_weekly调用面不变;月报`--month/--dry-run`、季报`--quarter/--dry-run`保留;日报入口保留(UNVALIDATED自证);81指标/评分模型/9论点/9视图/预测生命周期/GLM 5.3/8节周报结构零改动;launchd未动。
- 回滚: 代码均为纯Python单仓文件,`git revert 6abcc93`即可整体回退。

## 14. 交付状态结论

- 五项缺陷(FIX2-01~05)代码+对抗测试全部完成: fix2套件96断言、E2E 14场景41断言、全量回归20套件1086/0。
- AC-01~13: 13 PASS(其中AC-13的CI子项阻断如实呈报);F2-AC-01~08 IMPLEMENTED,F2-AC-09(CI实际生效)BLOCKED——凭据缺workflow scope,非开发侧可控。
- 唯一遗留阻断: workflow文件推送(§11);其余为契约性排除项(真实GLM/launchd观测,§12)。
- 除CI外,自检全部通过,进入独立验收。
