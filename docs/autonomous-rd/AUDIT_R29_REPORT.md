# Audit-R29 收口报告 — 全球宏观变化地图正式使用续收尾四任务

- 链: `fbeb478`(R28 终笔)→ `900a8bd`(四任务代码+37/37 新门)→ `2412968`(SKILL 席位绑定随新合同)→ `37b8713`(席位绑定机械化,38/38)→ `b7f9ccf`(C2 实雷修:地图草稿类判定脱离 run_ok 门,43/43)
- 基线: PR #1 head `fbeb478`,CI 44887984054 三 job 绿;`37b8713` CI 44901335878 绿;`b7f9ccf` CI 44905667262 绿
- 验收树: `git archive 2412968` + LIVE 只读复制 + 当日面重采(china/ea/jp/japan 旧格式面删后真采)+ 树内 `install_skill --target project`
- 电池: 202/202 rc=0 零红(提交树 `900a8bd`;`2412968` 为 docs-only 技能面,读技能面四门 r26/r27/r28/r29 复跑绿)

## 任务1 — EA_REAL_GDP_YOY 接通常规更新与研究快照

- **根因复现**: R28 当日 EA 面缺席=FRED 单次 `URLError: EOF occurred in violation of protocol (_ssl.c:1129)` 瞬时 TLS 故障吞掉整日面→快照 series 缺→地图 EA 增长格连锁缺数(A 12 组只缺 EA 增长,B 同)。采集器与入库链本身通畅(R26/R27 树已证)。
- **修复**: `scripts/ea_market_collector.py` 网络路径固定 3 次尝试(间隔 2s);成功路径 parse 告警与重试告警合并(修内实雷: `parse_fred_csv` 原重绑 alerts 吞掉重试记录);全部尝试失败才落 READ_FAIL 如实缺席。raw 注入路径零网络零重试,语义不变。
- **实测**: 验收树默认路径真采——`ea_20261121.json` `series.EA_REAL_GDP_YOY` **123 季 1996Q1→2026Q3(末值 1.28)**落地;快照重建后 `series_store` n=88,十地图指标全解析(含 `EA_REAL_GDP_YOY:123`)。`run_weekly.py` 常规步白名单含 ea 采集器(门 §A3)。
- **门**: `tests/test_audit_r29_gate.py` §A 4 判据(瞬时失败一次→重试成功+告警如实/全败诚实缺席/面→快照入库链/常规步在场)。

## 任务2 — 开放问句(question_open.txt 原文)零指标根修

- **缺陷**: 旧口径经济体识别只匹配全名——「美、欧、中、日四地」零命中→S3 默认面 US+CN;零维度词形→降级经济体概览,`data_requirements.items=[]`,12 组网格不成形。
- **修复**:
  - `scripts/workbench_data.py` 新增 `economy_abbrev_hits`: 三形守卫(`、`/`,` 枚举 run≥2 / ≥3 字并排 / 双字+数量词(两|三|四|各)+(地|国|方|经济体)前瞻)。对抗反例实测: 「其中完美日子里」「完美的中式餐饮」「日本央行政策利率」「美国与欧元区的增长」零命中。
  - `scripts/research_map_planner.py` 隐含维度展开: 宏观环境/宏观基本面/(明显)分化/哪些维度/什么维度线索且无显式维度词形→全维族 [增长+通胀+货币政策](确定性、披露性);`detect_map_question` 与 `_clause_region_dimension_requests` 同一展开(检测与计划不两套口径);`MAP_SHAPE_WORDS` 补「基本面」(同族问句形判漏检);`plan_map` 落档 `dimension_source` 三态(implicit_macro_environment / explicit_words / fallback_full_grid)——读者可核网格为何如此。
  - `scripts/research_orchestrator.py` `map_entities` 并入简称命中。
- **门**: §B 13 判据(正例 5 形/反例 4 形/开放问句四地全中/12 组/dimension_source/新问同形态/近失 2 形不误触发)。
- **真实会话**: OPEN(question_open.txt 原文)+ NEW(未参与调试新问「美、日两地宏观基本面…」)——见 §验收记录。

## 任务3 — 时点口径

- **BOJ 生效日口径(实测 2026-11-21)**: `policy_decision_state('JP_POLICY_TARGET')` = 决议 2026-09-18 / **生效 2026-09-24** / 官方目标 1.25 / 维持公告 2026-10-30 只更新确认状态(`last_maintenance=last_confirmed_on=2026-10-30`,目标与生效日不动)——距上次调整 **58 天按生效日**(非决议日 64),距决议 64,距维持 22。
- **LPR 官方 09:00 三处统一**: `config/metric_registry.json` 两处 09:15→09:00 + `POLICY_FACE` + `RELEASE_RULES`(发布节奏表)——全仓 `09:15` 零残留;日历条目 `time=09:00`(v1.5.0 既有,本轮核齐)。
- **历史两端各按自己的可知截止**(门 §C 纯函数判据):
  - 2022-03 锚不泄漏: 截止 03-31 只见 2 月观测(3 月观测 04-09 发布=事后才可知,4 月更不取);
  - 同比缺基期: 水平序列基期观测不可见→`no_visible_base` 缺证,不虚构同比;
  - 同一期重复观测: 同月取最晚观测日,平局后位胜,重复调用逐位一致;
  - 相对日期事后事实: 「随后 N 个月」绑**事件日**锚(`parse_ex_post_offsets` anchored_on=事件日),与日历点锚(截止日−N 月)分记两类;
  - 两端各按可知截止: 截止端与锚−3 月端分别落位,不并轨取同一值。
- **门**: §C 10 判据。

## 任务4 — 冻结输入与严格重放

- **设计**: 地图问句运行时实际读的 root 文件(发布日期历+指标注册表+运行快照——render 链经 metric_series 读注册表口径)在计划段逐字节摘要随 run 落档(`run.frozen_inputs`) + 字节级副本随运行目录走(`rd/root_overlay/`)——报告段重渲/归档打包/离线重放同一份字节,与本地日历/快照现状无关。席位终裁绑定冻结聚合摘要(`AGENT_SEAT_ENVELOPE.frozen_inputs_sha256` → verdict `extra`),归档 belt 校验,重放四门复验。非地图问句=None 不绑(零回归);R29 前旧档(无 frozen_inputs 键)重放走 legacy 路径(零回归)。
- **落点**:
  - `scripts/research_orchestrator.py`: 计划段冻结摘要+副本(逐字节核对后落位,失败如实报错不落半套);
  - `ia_cli.py`: plan 段工单载 `frozen_inputs(+/sha256)`;report 段渲染 `root=rd/root_overlay 优先`;archive 段冻结面随包(root_overlay/ 三件,byte+digest16 验证)+终裁绑定校验+manifest 两键;replay 段冻结三查(present/digests/match_report)+终裁冻结摘要入三面绑定+重渲 `root=包内 overlay`(本地日历无关);
  - `scripts/agent_judgment.py`: `frozen_inputs_digest`(排序 rel:sha16 聚合 sha256);
  - `.agents/skills/global-macro-research/SKILL.md`(`2412968`): 席位落裁指令补 `extra={'frozen_inputs_sha256': 工单值}`——不补则真实席位按旧指令落裁→归档拒(门内实雷,技能面同步)。
- **门**: §D 8 判据(D1 归档携冻结面+绑定 / D2 严格重放绿逐字节+冻结三查+三面绑定 / D3 换本地日历重放不变且==包内原档 / D4 重复重放+原包不动 / D5 缺件拒 / D6 篡改冻结件拒 / D7 manifest 单侧改写拒 / D8 终裁未绑摘要归档拒)。
- **r18/r19/r20 门席位仿体随新合同**(合成席位补 extra 绑定;r19 §H 实雷=计划段落 rd/root_overlay 后旧仿体未绑→已修)。

## 验收记录(真实会话+实包重放)

### wave-0(2412968 树,三会话——绑定手工化缺陷的实测暴露)

- **会话 B(换问)**: 全链走通——席位首裁 REVISE(两必修: 日本决议日实录未采信、欧元区通胀路径单调化误述)→修订→复裁 **UPHELD**(席位自证: JP 决议 09-18/生效 09-24/目标 1.25/维持 10-30,**距上次调整按生效日 58 天/按决议 64/距维持 22**——任务3口径被独立席逐格复验);`deliverable=true`。**实雷**: 落裁未按 SKILL 片段带 `extra` 冻结摘要→归档 belt 拒(`correlation_failed`)。**正道修**(`37b8713`): 绑定机械化——`record_semantic_verdict` 从 `report.run.frozen_inputs` 自动摸出并落 `frozen_inputs_sha256`(席位零手工;extra 传异摘要=ValueError 拒落档)。门 §D8 改真触面+§D8b 新增,38/38。
- **会话 A(原问)**: 主会话把席位作异步任务后先行结束回合,裁决未落地(`deliverable=false`,无新裁决档)——LLM 行为差异非代码缺陷;终 SHA 树重跑(下节)。
- **会话 C(残缺树,缺 ea 当日面)**: 会话产出**草稿交付**(EA 缺数面如实披露+停等裁定,补采属用户卡点);操作侧实测 `--stage archive` **拒绝**(2412968 面=冻结 belt 拒,印证 belt 有效;终 SHA 树重跑取草稿类拒绝正口)。

### wave-1(终 SHA `b7f9ccf` 树,真实会话四席)

**C2 实雷与正道修(`b7f9ccf`)**: wave-0 会话 C(残缺树)操作侧 `--stage archive` 在 `37b8713` 面**成功**(arc_C2/arc_C2b 两份实录,见 r29-evidence/session_C2_degraded_defect/)——根因: `blocked_class_of` 把全部地图内容草稿类包在 `if run_ok is not False:` 门内,TIPS_10Y 等源端诚实缺席把 run_ok 置 False 后整支跳过→缺 EA 增长+EA 通胀核心组的地图落 `optional_data_missing` 放行,与 R20 起草稿合同相反。修复: 地图问句先判内容类(与 run_ok 解耦),run_ok 门只保留给非地图问句;地图内容全绿且 run_ok=False 照旧落 `optional_data_missing`(B2 合法交付形态保形)。同报告直调复核: arc_C2→`map_core_dimension_missing`、arc_B2→`optional_data_missing`(不变);门 §E 五判据钉死(43/43)。

- **会话 A2(原问,健康树)**: 全链走通——席位两裁 REVISE(1 必修)→修订→**UPHELD**,两裁 `frozen_inputs_sha256=a09e4119…` 自动绑定(机械化面);`deliverable=true`;操作侧归档 arc_A2(content_sha256 `dbbd6a77…` 与终裁一致);**实包重放六步全绿**(严格面无旗标 byte_equal/换本地日历逐字节一致/重复重放原包不动/缺件拒/篡改一字节拒/manifest 单侧改写拒)。席位复验任务3 口径: JP 决议 09-18/生效 09-24/目标 1.25/维持 10-30,距上次调整按生效日 58 天。
- **会话 B2(换问)**: 详见 wave-0 段(绑定机械化首证);终 SHA 面重出重放回执(matched engine `37b8713`,六步全绿)。
- **重放版本门旁证**: 以 `b7f9ccf` 引擎重放 37b8713 包=**拒**(`code_version_mismatch`,13 项内容检查全绿、版本门拦——R28 门④在真实面再证);回执生成须 matched engine(引擎树 git archive 同 SHA+CODE_VERSION 印章)。
- **会话 C3(残缺树,终 SHA `b7f9ccf`)**: 全链走通——12 组计划,EA 增长+EA 通胀零 ok 格(残缺面如实);裁 **UPHELD**(冻结摘要 `1e0be210…` 绑定,残缺快照自有摘要);会话交付**草稿**并停等裁定(补数=FRED 凭证=用户保留卡点,如实);**操作侧归档拒绝实录**: `--stage archive` rc=1/blocked=not_deliverable/「底座 run_ok=False 且非 optional 级显式降级」——同报告 `blocked_class_of=map_core_dimension_missing`(树内同代码直调,回执在案);对照 arc_C2(修复前同形态**归档成功**)=缺陷→修复全链实证。`dimension_source=explicit_words`(原问显式点名三维,口径正确)。
- **会话 OPEN2(question_open.txt 原文,终 SHA)**: 全链走通——**12 组网格**(美/欧/中/日 × 增长/通胀/货币政策)零缺组,`dimension_source=implicit_macro_environment`(问句无显式维度词形,按环境/分化线索展开全维族+披露);报告面**逐项标注证据不足维度**(总判断明写: 波动归因与日本官方政策口径两处证据不足,各面披露);两裁 **UPHELD**(冻结摘要 `45666c82…` 绑定);归档 content_sha256 `b42a39ee…` 与终裁一致;`blocked_class_of=optional_data_missing`(run_ok=False=TIPS 诚实缺席,内容全绿→合法交付形态)。
- **会话 NEW2(未参与调试新问「美、日两地宏观基本面」,终 SHA)**: 全链走通——**6 组网格**(美/日 × 三维)零缺组,`dimension_source=implicit_macro_environment`;报告含「证据不足」「证据还不足」标注(新问原词形);裁 **UPHELD**(同日冻结面 `45666c82…`——同树同快照,聚合摘要一致属预期);归档 content_sha256 `75468f71…`;分类同上。

### 电池与证据

- **电池**(`b7f9ccf` 提交树): 202 件 **201 PASS / 1 FAIL**——唯一红=phase6 D3「整改树工作面净」看的是本报告+证据包的未提交件(docs commit 后复跑收绿,既档惯例);分类相关 23 套件(r4-r21/r26-r29/ia_cli/p03)提交前已全绿。
- **证据包**: `docs/autonomous-rd/r29-evidence/`(四问原文/wave-0 三席日志/A2·B2·OPEN2·NEW2 归档件+裁决链+读者报告/C2 缺陷实录+DEFECT_NOTE/C3 拒绝回执/A2·B2 六步重放回执;日志消毒=零本机路径零密钥形)。
- **CI**: `b7f9ccf` run **44905667262** 绿(offline-tests);远端 PR #1 head 已核对=`b7f9ccf`。

## AC 状态

- **AC3(机构观点验证)**: 维持 **PARTIAL**——C 型到期预测实判首验窗 **2026-12**(日历门未到,依据真实到期证据填报;六标签全库 INSUFFICIENT=库龄函数,如实)。A 面 vintage DEGRADED 近似锚如实标注(FINAL_ACCEPTANCE.md 既有口径)。

## 停等事项

- 外部审计终判;**正式合并 PR #1 / LIVE 部署 / 付费凭证: 由用户裁定**(本轮零 LIVE 写入,LIVE 数据树只读复制)。
