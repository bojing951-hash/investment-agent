# IA-P0-1 FIX4 整改开发报告(P0_GATE_A_REPAIR_04)

> 角色: 开发方(高级Python工程师)。本报告为开发自检记录,**不构成**P0-1验收结论;
> 最终验收由独立Agent(Agent 4)执行。冻结契约五份(IA-P0-1-AC-v1.0 / FIX1-AC /
> FIX2-AC / FIX3-AC / FIX4-AC即本轮指令§五~§十三要求)均未改动、未降低任何
> 已冻结标准。

## 1. 开发前固定 Commit

| 基线 | SHA |
|---|---|
| 原始审计基线 | `844fd3bef5e1e7e17b4d333278acd319f1dbae41` |
| FIX3最终HEAD(FIX4开发前固定,`git status`干净且与远端一致) | `38d920ac229a69b9af0a57e1ff04ef2ac2f8c5cb` |

## 2. 实际实现 Commit 与最终 HEAD

| 项 | 值 |
|---|---|
| 实现Commit(代码+测试,消息=`fix(p0): validate research facts and formal report identity`) | `be37d4049dab4bf39e48fb2d46e0d6f8206694a8` |
| 文档Commit(本文件) | 推送后即本文件所在提交(见git log;按"实际SHA不得预填"不虚构) |
| 最终GitHub HEAD | 文档Commit(其CI运行须与此对应,见§10) |
| 推送方式 | SSH(`git@github.com:bojing951-hash/investment-agent.git`,普通授权通道,无force push) |

## 3. FIX3-NEW-001~004 整改矩阵

| 缺陷 | 要求摘要 | 结论 | 实现与证据 |
|---|---|---|---|
| FIX3-NEW-001(FIX4-01) | 金融事实必要字段与注册表身份校验:身份(注册/active/口径一致,未注册不得自宣有效,不发明注册表指标)/value(有限实数,None/NaN/Inf/布尔/不可解析字符串对声明有效事实=非法;合法非核心FAIL保留异常原值隔离,不与结构不可证明混同,不整体升FAIL)/unit(非空且与注册表一致)/observation_date(存在/可解析/≤研究截止,不得以采集日/生成日/mtime顶替)/source(对象+collector+file身份;派生须calculation_ref;retrieved_at按采集器实况可为None)/一致性(结构不可证明→拒,核心FAIL→Gate A FAIL,非核心合法FAIL→DEGRADED,矛盾→拒,正常事实不误拒;快照生成与下游Gate A同口径) | **IMPLEMENTED** | `research_provenance.fact_structure_problems()`以make_fact真实结构为基准对声明有效(PASS/WARN/DEGRADED)的注册表事实做Tier-B结构校验;`recompute_gate_a()`新增:未注册/非active指标自报有效→`illegal_quality`(effective=None fail-closed),仅FAIL→`non_research_facts`诊断桶(不入counts/非核心清单,不阻断);研究截止=research_as_of[:10]→target_date,两者皆不可得→fail-closed;`fact_engine.snapshot_quality_grade`同口径只计active研究事实(quality.counts↔重算counts恒可互证);`snapshot_builder`构建时即传入sources_status/as_of/target_date(生成与下游同口径)。19例矩阵+真实下游入口:`tests/test_p01_fix4.py`(全active 80事实真实快照定点篡改:删value/value=None/NaN/Infinity/字符串/布尔/删unit/unit=None/unit口径不符/删od/od不可解析/od晚于截止/删source/source非对象/source缺collector/file身份/派生缺calc_ref/未注册自报PASS/未注册仅FAIL诊断/合法非核心FAIL/核心FAIL/合法DEGRADED;下游=真实装配器exit2+真实周报预检拒+verify_meta_gate_a失配)。真实生产11份快照零误伤(见§13) |
| FIX3-NEW-002(FIX4-02) | 正式报告身份字段严格核验:report_file存在且=实际文件名/target_date存在且=文件名日期/report_path存在且对应实际路径(可靠规范化:别名/遍历/错误相对路径)/report_digest与实际内容一致/published恰为True/final_quality∈{PASS,DEGRADED}/允许目录与规范路径;不完整旧状态不默认放行(只走既有未验证档案机制);核查全部真实消费者(load_previous_report/data_validator正式读取/月度周报索引/季度/全部扫描器) | **IMPLEMENTED** | `research_provenance.formal_report_view()`在FIX3七链之上新增三条强制身份链:report_file≠实际文件名→拒;target_date缺失或≠文件名日期→拒;report_path非字符串/空→拒,`os.path.realpath`标准化后≠实际读取路径→拒(指向其他目录/另一报告/被移动报告),同一文件的`./`·`../`别名等价路径放行(不因别名误拒,亦不借别名冒充);兼容规则以`_status_body`真实写入行为为准(发布时写入正式文件完整路径)。16例矩阵全部经**真实消费者**断言(非仅新辅助函数):`rp.formal_report_view`+`rp.scan_formal_weekly_reports`/`latest_formal_weekly_report`+真实`rg.load_previous_report`(次日视角)+真实`dv.find_latest_report_for_validation`(formal/archive降级)+真实`mr.gather_month_context`月度索引(未验证档案标注):report_file缺失/错误,target_date缺失/错误,report_path缺失/其他目录/另一报告/裸文件名,published=False,final_quality=FAIL,digest不符,状态损坏,首发布中断(仅candidate),中断+已有合格旧报告(回读昨日合格),路径别名不误拒,正常PASS,正常DEGRADED——身份缺失/冲突全部拒绝,正常报告全部可读 |
| FIX3-NEW-003(FIX4-03) | active非核心指标完全缺失→进缺失清单+Gate A DEGRADED(非PASS)+可核查缺失原因;注册表驱动(status/criticality/source),区分active/core/important/context/deprecated/确不适用;无硬编码特例;不改criticality分级;不补零/不伪造历史或当期数据/不无理阻断其他有效研究;月度区分"下期尚未发布"vs"应存在而采集缺失",注册表判不了可得性时显式记录判断边界,不发明发布日历/新鲜度阈值;传播:快照JSON保存缺失信息/快照MD披露/Gate A与缺失清单一致/数据包记录/正式周报保留可见DEGRADED解释/有效数据继续研究/quality.overall与Gate A语义不混同(缺席不虚增FAIL计数) | **IMPLEMENTED** | `recompute_gate_a()`注册表驱动缺失判定:非派生→来源采集通道映射,来源文件在场(EXACT/FALLBACK)=『来源文件在场而指标缺席(采集遗漏)』,文件级缺失=『来源文件缺失(通道:状态)』;派生→输入齐全而缺席才计(输入缺席=归因性缺席不计,NFP_MOM_K镜像compute_derived的m1条件);来源无法映射通道/无sources_status→显式boundary记录不虚报不编造;deprecated不要求;noncore_missing非空→effective至少DEGRADED。传播链:`snapshot_builder`(gate_a.noncore_missing/detail/boundary入JSON+MD披露块+构建摘要)、`data_assembler`(包正文披露行+包meta.noncore_missing)、`report_generator`既有degraded footer经`gate_reason_desc`新增『非核心缺失: …』点名。月度边界:缺席恒=采集缺口,"尚未发布新期"表现为**在场旧期**观测滞后→既有92天新鲜度DEGRADED(不进缺失清单),两形态各有归因互不冒充。场景矩阵:`tests/test_p01_fix4.py`场景B(缺席→noncore_missing点名+DEGRADED+三级披露+无伪造事实+counts不虚增)/场景A(值坏→noncore_fail,既有语义保留)/核心完全缺席→FAIL/月度边界(旧期在场≠缺席)/来源文件级缺失独立归因/deprecated(REAL_SHORT)不追责/无sources_status显式边界+`test_e2e_frozen14.py` E2E-02d(原始场景B翻转,见§7) |
| FIX3-NEW-004(FIX4-04) | 重新实现原始E2E-12:同一合法可追溯批次内部分预测指标有效+部分无效→仅合法观察被记录;合法批次(真实快照/Gate A如实/锚点来自快照/溯源元数据完整/锚点内容=快照/无人工篡改);经真实DEGRADED(非核心数据异常);≥2条有效状态测试预测(A合法PASS指标,B质量FAIL或不可用非核心指标);执行daily_prediction_observer.observe()+必要真实状态引擎逻辑;预期:批次来源核验通过/有效指标观察被写入/无效跳过且原因明确/无效不入长期历史/不无理阻断其他/同批次二次运行幂等/正常终态预测不重开;对比临时allocation_views.json前后实际内容(观察数+值/observation_date/source/未触发vs观察中逻辑/重复运行后文件状态/无无效记录被静默写入);锚点篡改测试保留为附加源对抗测试,不再冒充E2E-12 | **IMPLEMENTED** | `tests/test_e2e_frozen14.py` E2E-12重建:合法链路内构造UMCSENT**数值型区间外**(9999.9,注册表区间[40,120])→真实事实引擎区间校验FAIL(锚点带数值+quality=FAIL,与字符串'N/A'的无锚点形态区分)→合法Gate A=DEGRADED;真实批次核验通过(build_anchors确定性重建);预测集=观察中A(SPX,合法PASS)+观察中B(UMCSENT,质量FAIL)+终态C(hit)+未触发D(合法前提未兑现)+未触发E(前提=无效指标);真实`dpo.observe()`(指标级质量门禁rp.anchor_quality_problem同口径)+真实`ae.record_observations`写入;断言:A记入观察(值7659.44/obs_date/source=快照文件)/B与E跳过原因明确且observations保持空/状态PARTIAL/C不重开不追记/D保持未触发/二次运行changes=[]且views.json字节不变。旧锚点篡改用例保留为**E2E-12x[附加源对抗测试]**(剥离quality+同步meta摘要→权威重建比对整批拒+对照批次过+预检拒+exit2+GLM=0),标题显式标注"附加",不再冒充E2E-12 |

## 4. F4-AC自检矩阵(FIX4-AC=本轮指令§九)

| F4-AC项 | 要求 | 结论 | 证据 |
|---|---|---|---|
| F4-AC-01 | 金融事实必要字段和身份完整 | PASS(自检) | §3 FIX4-01行;19例矩阵全绿+真实下游入口拒;生产11快照零误伤(§13) |
| F4-AC-02 | 正式报告发布状态身份严格匹配 | PASS(自检) | §3 FIX4-02行;16例矩阵全绿(全部真实消费者);正常PASS/DEGRADED不误伤 |
| F4-AC-03 | 非核心完全缺失合理降级披露 | PASS(自检) | §3 FIX4-03行;场景A/B互不冒充+月度边界+deprecated+来源级缺失+三级披露+不补零 |
| F4-AC-04 | E2E-12合法混合预测观察正确 | PASS(自检) | §3 FIX4-04行;合法批次+真实观察器+幂等+终态不重开;篡改用例降为附加测试 |
| F4-AC-05 | 既有质量机制与核心功能不回归 | PASS(自检) | §11回归:23套既有离线套件+2套E2E套件全部0失败;合法FAIL/DEGRADED/WARN语义逐项保留(fix4矩阵#17/#19/#M与frozen14 E2E-02a-c/09) |
| F4-AC-06 | 完整E2E、离线测试和CI可复核 | PASS(自检) | §7 E2E-01~14逐项实际结果;§9全部离线执行记录;§10新Commit真实Actions运行链接;无付费GLM/无生产研究数据进测试 |

## 5. 历史契约自检(原始AC-01~13 / RAC-01~09 / F2-AC-01~09 / F3-AC-01~06)

| 契约 | 结论 | 说明 |
|---|---|---|
| IA-P0-1-AC-v1.0(AC-01~13) | 适用项全部维持 | Gate A/B门禁、快照不可变+修订、事实引擎统一口径、来源核验、发布事务、预测生命周期、月度/季度报告、本地调度、CI均未削弱;FIX4只收紧不放松 |
| RAC-01~09 | 适用项全部维持 | 回归以全套件重跑+冻结14 E2E原样重执行覆盖(§7/§9/§11) |
| F2-AC-01~09 | 适用项全部维持 | FIX2的发布事务/状态隔离/原子写原样;FIX4-02仅在其status读取链上增加身份强制,真实写入路径(_status_body恒写report_file/target_date/report_path)产物不受影响 |
| F3-AC-01~06 | 适用项全部维持 | FIX3的fail-closed/统一读取器/verify_meta_gate_a/Actions真实运行/冻结编号E2E全部保留;FIX3绿色运行(40505879881/40507513231)仅作历史证据,不作为FIX4通过证据;E2E-12按FIX4指令重建为原始语义,旧实现对应用例保留为附加对抗测试(非删除) |

## 6. (并入§4/§5呈现,避免重复)

## 7. 原始E2E-01~14实际结果(`tests/test_e2e_frozen14.py`,33检查/0失败)

| E2E | 场景(冻结表原样) | 结果 |
|---|---|---|
| E2E-01 | 完整正常数据进入研究流程 | 通过(a-d: sb CLI exit0+Gate A=PASS/装配exit0+包meta.gate_a=PASS/周报exit0+GLM恰1次+formal认定PASS/分级回写1次) |
| E2E-02 | 部分非核心数据缺失,合理降级 | 通过(a-c: 值坏→DEGRADED可发布; **d/d2/d3: FIX4-03原始场景B翻转**——UMCSENT整体缺席→noncore_missing点名+Gate A=DEGRADED+未补零未伪造+快照MD/数据包/包meta逐级披露+正式周报保留可见降级解释点名缺席指标; 不再是旧的"缺席仍PASS") |
| E2E-03 | 核心失败导致Gate A FAIL | 通过(core_fail点名SPX+sb exit≠0+装配器exit2无包) |
| E2E-04 | Gate A FAIL后直接运行周报,GLM=0 | 通过(预检拒+exit2+GLM恰0) |
| E2E-05 | 失败快照与旧数据包 | 通过(旧包残留不被放行) |
| E2E-06~08 | 修订/跨日/来源不一致批次 | 通过(修订版绑定/跨日锚点拒/另日快照拒) |
| E2E-09 | Gate A DEGRADED+Gate B PASS→最终DEGRADED | 通过(exit0+发布+回写不阻断) |
| E2E-10 | Gate A PASS+Gate B FAIL→禁止回写 | 通过(exit3+applied=[]+长期状态字节不变) |
| E2E-11 | 关键步骤失败产生正确SKIPPED | 通过(a流水线exit1+SKIPPED;b报告入口exit2+零GLM) |
| E2E-12 | 有效、无效预测指标混合(**FIX4-04原始语义重建**) | 通过(a: 合法可追溯批次Gate A=DEGRADED+批次核验过;b: A合法PASS指标记入观察;c: B质量FAIL跳过不进长期历史;d: 终态不重开+无效前提不激活+合法未触发保持;e: 同批次重复运行幂等字节不变) |
| E2E-12x | [附加源对抗,原E2E-12旧实现保留降级] | 通过(锚点篡改+同步摘要→整批拒+对照过+预检拒+exit2+GLM=0) |
| E2E-13 | 旧锚点残留指标 | 通过(点名残留键+批次拒+exit2) |
| E2E-14 | 已有合格报告,后续输入质量失败 | 通过(a: 当日exit2+昨日字节不动仍唯一formal;b: 真实load_previous_report回读昨日无未验证标注) |

既有平行套件`tests/test_e2e_orig14.py`(41/0)同步全绿。E2E-02与E2E-12均**未使用替代场景**(02恢复原始场景B语义;12恢复原始混合预测语义)。

## 8. 新增与变更的测试及原因

| 测试 | 变更 | 原因 |
|---|---|---|
| `tests/test_p01_fix4.py` | **新增**(49检查) | FIX4-01 19例矩阵/FIX4-02 16例真实消费者矩阵/FIX4-03场景与边界矩阵的闭环验收 |
| `tests/test_e2e_frozen14.py` | E2E-02d翻转为原始场景B;E2E-12按原始语义重建;旧篡改用例保留为E2E-12x;chain_build增加post_collectors注入回调 | FIX4-03/FIX4-04指令要求:E2E-02与E2E-12不得使用替代场景;注入回调用于构造"合法链路内的数值型区间外"数据形态(经真实事实引擎判FAIL,非人工篡改锚点) |
| `tests/fixt.py` | fixture扩展至全部80个active指标(global 32/宏观日频+月频补全/china补创业板指+南向+两融+估值),NFP_MOM_K改为真实派生路径(NFP月序列差分带calculation_ref),B_OAS取值修入注册区间 | 合法输入契约自FIX4起包含"active非核心在场"(缺席即缺失→DEGRADED);直接塞NFP_MOM_K键无calculation_ref会被FIX4-01正确判非法且非真实链路;B_OAS=1.38低于注册区间[2,35]属fixture自身违反validation.range |
| `tests/test_fact_engine.py` | "含FAIL→整体DEGRADED以上"拆为两条:未注册FAIL诊断不计(overall=PASS)+注册指标合法FAIL计入 | FIX4-01语义:未注册FAIL=诊断记录不冒充研究事实;原检查依赖未注册UNKNOWN_X的FAIL计入分级,属与新冻结语义冲突的旧期望;负向检查保留且更严格(两条各自断言) |
| `tests/test_p01_fix1.py` | 篡改场景的quality.counts改为自真实快照计数推导(不再硬编码`{'PASS':33,...}`) | 旧数字来自34事实时代fixture;全active fixture下声明counts与事实counts不一致会被(必须保留的)counts一致性核验正确拒绝——fixture违反合法输入契约,核验本身是负向检查不动 |
| `tests/test_p01_fix2.py` | 同上counts硬编码修正;"注册表外指标"期望从noncore_fail更新为non_research_facts诊断桶+不计数+不降级+effective保持 | FIX4-01冻结语义:未注册指标不冒充非核心研究事实;原期望(进noncore_fail并使DEGRADED)与新契约冲突;核心不进入/不计数/不阻断等负向断言全部保留并加强 |
| `tests/test_p01_fix3.py` | 手工构造的合法基线状态补`report_path`字段 | FIX4-02: report_path为必需身份字段且真实_status_body恒写入;缺该字段的手工"合法"基线违反合法输入契约(缺失分支的负向覆盖在fix4矩阵16例中) |

全部修改均为fixture对齐合法输入契约或对齐FIX4冻结语义;**无任何负向检查被删除**,多处反而加强(如fix2注册表外指标新增"不计数不降级"断言)。

## 9. 全部离线测试执行记录(本机Python 3.9/macOS,全绿;CI为Python 3.11/Ubuntu亦全绿见§10)

| 套件 | 结果 | 套件 | 结果 |
|---|---|---|---|
| test_datafix_20261017 | 13/0 | test_p0_fixes | 22/0 |
| test_e2e_four_weeks | 59/0 | test_p1_fixes | 36/0 |
| test_e2e_frozen14 | 33/0 | test_p2_fixes | 82/0 |
| test_e2e_orig14 | 41/0 | test_p4_fixes | 43/0 |
| test_fact_engine | 60/0 | test_p7_fixes | 30/0 |
| test_gate_chain_p01 | 86/0 | test_phase3 | 47/0 |
| test_p01_fix1 | 82/0 | test_phase4 | 20/0 |
| test_p01_fix2 | 109/0 | test_round3_adversarial | 24/0 |
| test_p01_fix3 | 45/0 | test_round3_p0 | 91/0 |
| test_p01_fix4(**新增**) | 49/0 | test_round4 | 94/0 |
| test_snapshot | 46/0 | test_round5 | 64/0 |
| test_round6 | 51/0 | test_glm_live | 按契约不入CI/本轮未运行(真实GLM付费) |

24套合计约1,065检查/0失败;全量循环本机17.1s(exit全0)。

## 10. 新Commit的GitHub Actions运行

| Commit | Run | 结论 |
|---|---|---|
| `be37d40`(FIX4实现Commit) | https://github.com/bojing951-hash/investment-agent/actions/runs/40522469690 (run #7) | ✅ success(32s;零::error注解;工作流`tests/test_*.py`glob自动纳入test_p01_fix4.py,`exit $fail`结构下success⇔全部件exit 0;时长与本机全量循环一致) |
| 文档Commit(本文件) | 推送触发同工作流 | 见Actions页(本文件所在提交的运行;推送后以页面为准) |

FIX3历史绿色运行(#5 40505879881/#6 40507513231)不作FIX4证据。

## 11. 回归情况

- 23套既有离线套件+2套E2E套件全部重跑0失败(§9);仅§8所列fixture对齐修改,无删除断言。
- 合法质量语义回归点逐项验证:合法非核心FAIL→DEGRADED保留(fix4#17/E2E-02a-c);合法DEGRADED新鲜度降级保留(fix4#19/#M);WARN不阻断(fix2既有);核心FAIL→FAIL保留(fix4#18/E2E-03);Gate B失败禁止回写保留(E2E-10);发布事务/修订/跨日/来源核验全部保留(E2E-05~08/13/14)。
- 真实生产数据零误伤:11份生产快照重算零illegal_quality;8份FAIL日与3份DEGRADED日重算与声明一致(§13)。

## 12. 尚未验证或仍存在的问题(P0-1直接相关)

1. **生产采集长期缺口(修复超出FIX4范围)**: MARGIN_BAL/SH_PE在全部11份生产快照中缺席——china采集器实况JSON用`rzye/rzye_billion`与按指数代码的`pe_ttm`键,归一化器期望`balance`/`pe`。FIX4-03后该缺口被如实披露(当日Gate A=DEGRADED+点名),不再无声PASS;采集器桥接属后续整改,未在本轮擅自改动采集器。
2. **历史快照声明与重算不一致(20261017/20261023声明PASS,重算=DEGRADED)**: 由上述真实缺口导致;仅当这些历史快照被重新核验时gate_status返回None(fail-closed),正常流程只核验当日快照,无生产阻断;如需以新口径重建历史,须走--allow-revision修订链(未在本轮执行,不修改生产历史数据)。
3. **PAT缺workflow scope**: 推送仍走SSH授权通道(既有约束,未规避权限)。
4. **CI逐套件日志需登录查看**: 以结论+零error注解+glob结构+时长一致性作为证据链(FIX3同口径)。
5. **独立Agent 4验收**: 待执行;本报告不构成验收结论。

## 13. 生产兼容性说明(全部只读检查,零生产写入)

- **事实校验零误伤**: 以FIX4代码重算全部11份生产快照:`illegal_quality`均为空(生产采集器从不产未注册自报有效事实,合法FAIL/DEGRADED结构完整),无一份因新校验被误拒。
- **Gate A裁决变化(有意为之,如实披露)**: 声明FAIL的8份(1018-1022/1027)重算FAIL一致;声明DEGRADED的3份(1024-1026)重算DEGRADED一致;声明PASS的2份(1017/1023)重算=DEGRADED——因MARGIN_BAL/SH_PE真实缺席,旧代码将其判为无声PASS,新代码按FIX4-03如实降级披露。仅历史快照被重新核验时体现(gate_status=None),正常当日流程不受影响;未来生产运行将诚实发布DEGRADED+缺失点名,直至采集缺口修复。
- **正式报告身份核验零误伤**: 生产output/weekly的12份历史周报均无report_status sidecar(P0-1前产物),按FIX3既有机制归"未验证档案"读取,行为与FIX4前一致(FIX4新增身份链只影响**有状态文件**的报告,真实_status_body恒写全部身份字段,经发布事务产生的新报告全部可认定——E2E-01/02d3/09实测)。
- **数据包meta新增noncore_missing键**: 披露性冗余字段,报告入口权威仍为gate_a(verify_meta_gate_a),旧包无此键不受影响。
- **快照JSON新增键**(noncore_missing/detail/boundary/non_research_facts): 增量字段,旧快照无这些键时缺失判定按"无sources_status→显式边界"路径处理(手构dict场景),真实旧快照含sources_status,重算行为见上;快照不可变契约未动,生产data/output/config/thesis/views本轮零写入。
