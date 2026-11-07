# IA-P3-WP-A REPORT — P3 收尾层第 1 实现包·族首(档案检索与结论版本管理)

> 包: IA-P3-WP-A(P3 族首实现包,#31/#32 挂靠) · 执行Agent: Agent 3 · 分支: `dev/p3-impl-a`
> 基线: BASE-P3A=`8cebe74d3a848e4c50681d2a88baca1d3d0c55f1`(origin/main,开工 ls-remote 实取全值一致)
> 合同: IA-P3-WP-A-AC-v1.1(冻结,附录A 内嵌注入)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY/上游在场件行号一律为**本包基线工作树实读**行号(2026-11-07T14:2x-15:0xZ 实取,基线=BASE-P3A+指定并入步带入设计三件);提示词注入内容引用一律标注「注入摘要,非工作树实读」。
> 数值标注边界: 本文所有计数类/统计类数值逐个二选一标注 `[实取·来源: …]` 或 `[示意·非实取]`;日期/SHA/结构编号(WP-P3-A/#31-38/P3-G-01 等)/档键成分(ID 格式字符串)按合同边界出圈登记。

---

## §零 规格抄录与交付面登记(开工首步,AC-01;登记后即本合同白名单实体)

### §零.1 DESIGN §7 WP-P3-A 行四要素逐字抄录

实读 `docs/P3_DESIGN.md`(基线工作树在场,blob `5acc130a88d9635a1e82d7ad3beb4f1dbe008106`,§零.7 核验与 7f43724 侧等值),WP-P3-A 行位于 L170-L174,逐字抄录:

```text
L170: **WP-P3-A 档案检索与结论版本管理**(挂靠编号: **#31/#32**)
L171: - 目标: 落地 §3.2 检索面(对象 4 类第一期 [实取·§3.2 枚举,2026-11-03] + O-5 接口预留)+ §3.3 结论版本链与修正机制。
L172: - 范围: 新增旁路索引器/结构化查询 API/版本记录写入挂接(旁路,不改既有回写签名);索引输入限门禁后正式产物(§3.1)。
L173: - 依赖: 层序前置(见上声明);O-5 接入依赖 P0-3 共享档案落地(E2E-B WP-B4,停泊中)——第一期以在场载体 4 类(O-1~O-4 [实取·§2.1 枚举,2026-11-03])交付,O-5 仅接口预留。
L174: - 验收要点草案: ①索引直读原始 data/daily 的负向测试(须被拒)②索引可重建性测试(删索引→从权威源确定性重建→逐字节一致)③版本记录 append-only 负向测试(改写历史版本记录被拒)+登记型参数(DP-1/DP-2/DP-3)**先登记后运行、禁回改**负向测试 ④修正提案走既有门禁断言(无弱门禁旁路)⑤CI 零回归(工件: 测试文件+run ID)。
```

四要素齐备(目标 L171/范围 L172/依赖 L173/验收要点 L174 共 4 条),无缺失。核验:
- **A 行可区分性**: 与 B/C/D/E/F 行四要素逐项可区分(A=档案检索与结论版本管理 L170-174/B=新证据关联与持续跟踪聚合 L176-180/C=预测复盘与错误模式统计 L182-186/D=报告质量评价循环 L188-192/E=个人流程整合接口 L194-198/F=终验+总封版 L200-208,题名与四要素内容均不同构)→ 合同附录A §零(iv)冲突处置首项不触发;
- **依赖列核验**: 「层序前置(见上声明)」=§7 L168 层序排程依赖声明(第一~三层实现面全部关闭;合同冻结章 §二 登记逐层核验 ✓,注入摘要,非工作树实读);「O-5 接入依赖 P0-3 共享档案落地(E2E-B WP-B4,停泊中)」=O-5 信息性登记(范围列明文「O-5 仅接口预留」,非本包硬前置);依赖列与 BASE-P3A(`8cebe74d…`)无矛盾、**不要求并入指定并入步(v1.1 合同条款: 第二父=7f43724)外其他支** ✓;
- **范围列无真实 GLM 调用/网络出站/付费凭证要求**: 范围列 L172 零 GLM/网络/凭证/付费字样;三件(旁路索引器/结构化查询 API/版本记录写入挂接)均为确定性结构 → 无情形(d)停止条件。

### §零.2 交付文件清单(k=4 [实取·本节清点],登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据(推导逐条附) |
|---|---|---|
| 1 | `scripts/research_index.py` | DESIGN L172 范围列三件(旁路索引器/结构化查询 API/版本记录写入挂接)=**恰 1 个代码模块**: WP 题名「档案检索与结论版本管理」(L170)单一工作包,三件共享索引条目/档键/集合词汇与索引文件载体(§3.2 L77 检索对象④「结论版本记录(§3.3 新增,**随建随入索引**)」明文索引器与版本记录同环;查询 API 消费索引形态同模块内聚)+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」;文件名=域词 research(研究档案检索与版本管理)+index(DESIGN §3.2 L86「索引形态决策」/L77 检索面用词),避开既有 `research_archive.py`(B4 共享档案)/`research_provenance.py`(R 系)(ls scripts/ 实读 2 件在场,命名不冲突) |
| 2 | `tests/test_p3_wp_a.py` | DESIGN L174①②③④工件「负向测试/断言」+合同附录A §零(ii)「含代码则必含 tests/test_p3_wp_a.py」 |
| 3 | `docs/P3_WP_A_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P3_WP_A_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L174⑤「CI 零回归」证据落点=DELIVERY |

### §零.3 结构约束核验

- 与 `git ls-files` 零重合: 4 路径 `git ls-files scripts/research_index.py tests/test_p3_wp_a.py docs/P3_WP_A_REPORT.md docs/P3_WP_A_DELIVERY.md` 输出=0 行 [实取·开工 2026-11-07T14:5xZ]→ 纯新增 ✓
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p3_wp_a.py)✓
- 推导无越界: 范围列恰 1 个代码模块(§零.2 行 1 依据)→ scripts/ 恰 1 文件;未引入 DESIGN 依据外文件 ✓

### §零.4 DP 登记(开工首步登记定值;DESIGN 决策点登记表 L226-L241 实读,DP 共 10 个 [实取·表清点],行内所引=DP-1/DP-2/DP-3 均登记型)

| DP | 分类(DESIGN 实读) | 本包登记定值(登记即实现值,先登记后运行,禁回改) | 依据 |
|---|---|---|---|
| DP-1 检索索引形态与更新时机 | 登记型(L230) | **(a) 旁路索引文件+事件触发增量更新**: 索引=JSON 单文件(默认 `data/research/research_index.json`,P-A-02),条目级增量合并(同 (kind,ref) 键替换为最新计算值,不可变对象只追加)后**规范化整体重写**(确定性序列化,P-A-03);索引=衍生物可随时从权威源确定性重建(§3.1 L73),(c) 数据库不采(违反纯本地文件先例) | L230+L86 |
| DP-2 检索第一期对象集 | 登记型(L231) | **(a) O-1~O-4 全 4 类**: ①快照事实(经 rp.select_snapshot 版本选择)②正式报告(rp.scan_formal_weekly_reports 认定)③论点/观点/预测状态记录(config/thesis.json+config/allocation_views.json)④结论版本记录(本包 VER- 族随建随入);O-5 深研任务档案=接口预留(P-A-15,词表在场+收录集排除+skipped_reserved 如实清单) | L231+L77 |
| DP-3 结论版本记录粒度 | 登记型(L232) | **(a) 记录级**: changes=[{field, before, after}, …≥1] 承载「变更前值+变更后值+受影响字段清单」三项(P-A-12),不采 (b) 字段级 diff | L232+L91 |
| DP-4/DP-8/DP-9/DP-10 | 确认权留用户(L233/L237/L238/L239) | **本包零触及**: DP-4=§4.1 关联第三层(WP-P3-B 面)、DP-8=§6.1 提示词注入(WP-P3-D 面)、DP-9=§6.2 接口(WP-P3-E 面)、DP-10=终验观察窗(WP-P3-F 面)——均非本包范围列(L172)所及,本包无 GLM/费用/个人流程/LIVE 面 | L233/L237-239 |
| DP-5/DP-6/DP-7 | 登记型(L234-236) | **本包不触及**(WP-P3-C/D 面: 错误模式统计窗口/复盘分母/质量评价维度);零引用零改写 | L234-236 |

行内所引 DP-1/DP-2/DP-3 与 DESIGN 实读编号/数量/分类一致(L174③ 明文「登记型参数(DP-1/DP-2/DP-3)」↔ L230-232 表行分类「登记型」逐行一致);确认型(DP-4/8/9/10)未被自决实施(§零.1 核验: 范围列零触及面)。

### §零.5 实现参数登记(P-A-01..P-A-16,先登记后实现,运行后禁回改)

| # | 参数 | 登记定值 | 依据 |
|---|---|---|---|
| P-A-01 | 模块载体 | `scripts/research_index.py` 恰 1 文件(旁路索引器+结构化查询 API+版本记录写入挂接同模块,§零.2 行 1) | DESIGN L172+§零.2 |
| P-A-02 | 索引文件路径 | 默认 `data/research/research_index.json`(`index_path` 参数注入,测试传沙箱路径;运行产物边界: 不 commit);文件名常量 `RESEARCH_INDEX_FILENAME="research_index.json"` | DP-1(a)+§3.2 L86 |
| P-A-03 | 索引文件格式与确定性序列化 | JSON 单文件 `{schema_version:1, note:<免责与衍生物声明>, entries:[…]}`;序列化=`json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=1)`(drr._write_records 同款先例,L513-524 实读);**零时间戳/零生成方式元数据**(过程性字段破坏确定性重建逐字节一致,结构性排除);entries 按 (kind, ref) 字典序排序,每 (kind,ref) 恰一条(状态对象=最新计算值;索引文件非 append-only=衍生物可重写,§3.1 L73「索引损坏/漂移→重建」;append-only 红线对象=版本记录等记录族,§8.5) | DP-1+要点② |
| P-A-04 | 条目 schema | 11 键固定 `{kind, ref, date, status, metric_ids, assets, mechanisms, obs_min, obs_max, snapshot_id, digest}`;维度面无信息=null(如实缺席,不填 0/空串冒充);列表字段=排序去重 | §3.2 L79 六维度 |
| P-A-05 | 档键词表(登记键) | snapshot→snapshot_id / formal_report→`weekly_report_{ymd}` / thesis→`THESIS-{id}` / view→`VIEW-{id}` / prediction→`PRED-{pred_id}` / conclusion_version→version_id(`VER-*`);`THESIS-`/`VIEW-`/`PRED-`=本包登记型状态记录键前缀,避开已占 10 族 [实取·scripts 实读: `research_archive.py` QB-(L278)/`deep_research_registrar.py` RT-DR-/HP-/FC-/EV-(L60-63)/`deep_research_matrix_engine.py` EVI-/RD-(L69-70)/`deep_research_tracking_engine.py` TRG-/CON-/DSP-(L77-79 附近集合名+前缀)/`deep_research_event_calendar.py` CAL-(L60)] | §3.2 L79「档键前缀(QB-/RT-/VER- 等族)」+§3.3 L91 VER- 族明文 |
| P-A-06 | 快照索引口径 | 枚举=严格 glob `research_snapshot_*.json`(模式结构性不可达原始采集件)→ymd 集→逐 ymd `rp.select_snapshot(ymd, daily_dir)` 权威版本选择(L1270 实读);放行=gate_a.status 经 `rp.gate_allows_formal_research`(L1210 实读;PASS/DEGRADED 入索引,FAIL/无候选/损坏→excluded 如实清单不入索引);metric_ids=facts[].metric_id 排序去重;obs_min/obs_max=facts[].observation_date(ISO 规范者)min/max;assets=经 `fe.metric(mid)['asset_class']` 并集排序(registry 经 fe 在场接口,缺席如实不入);date=快照 ymd;digest=`rp.digest_snapshot`(L1324 实读) | §3.1+§3.2①+§3.2 L79 |
| P-A-07 | 报告索引口径 | `rp.scan_formal_weekly_reports(output_dir)` 在场复用(L1520 实读,8 条校验链 formal_report_view L1456);date=ymd;metric_ids/assets/mechanisms=null(不解析 md 内容——§3.1 L73「查询结果引用一律落到源档档键,不复制数值语义为第二事实源」) | §3.2②+§3.1 |
| P-A-08 | 状态文件索引口径 | thesis 条目: date=文件顶层 last_updated,status=thesis.status(4 值词表 [实取·report_generator L501: 进行中/待观察/已验证/已失效]),metric_ids=quant_triggers[].metric 并集,assets/mechanisms=null;view 条目: date=last_updated,status=rating(4 值 [实取·allocation_views ratings_scale L5-10: 超配/标配/低配/观望]),assets=[asset];prediction 条目: date=date_made,status=prediction.status(裁决 4 值 [实取·report_generator L534: hit/miss/inconclusive/not_yet_triggered]+在场展示态 observing [实取·allocation_views L421]),assets=[asset],metric_ids=[metric](在场者;无规格=null 如实);mechanisms=null——**登记发现**: DEV 在场状态文件无结构化机制标签(thesis.json 实读无 evidence_ledger/evidence 字段,机制标签仅存在于周报 md 状态块非结构化回写面),机制维度数据面如实缺席(维度与过滤器已实现,见 P-A-10;非缺陷,机制标签结构化来源待上游载体演进,登记不越界实施) | §3.2③+L79 词表实读 |
| P-A-09 | 版本记录索引口径 | 每 VER- 记录恰一条;date=created_at 日期段;status=change_type;metric_ids/assets/mechanisms=null(记录面无该三维信息,如实缺席;对象关联经 object_id 联查状态条目) | §3.2④ |
| P-A-10 | 结构化查询 API | `query_index(index, *, metric_ids=None, obs_start=None, obs_end=None, assets=None, mechanisms=None, statuses=None, key_prefixes=None)`;离线纯函数零网络零 GLM(§3.2(a) L82);命中语义(登记): metric_ids/assets/mechanisms=集合交集非空;statuses=条目 status 精确等值(任一命中);key_prefixes=ref.startswith 任一;时间窗=[obs_start,obs_end](YYYY-MM-DD,闭区间)→条目 date∈窗 **或** 条目 [obs_min,obs_max] 与窗相交(两支任一;null 面不命中对应支);多过滤器=AND;输出=[{kind, ref, snapshot_id, digest}] 按 (kind,ref) 排序(**档键引用列表,非数值本身**,§3.2(a) L82) | §3.2 L79-84 |
| P-A-11 | 版本记录集合与 ID | 集合 `conclusion_versions` 挂共享档案族根(复用 `drr.ARCHIVE_FAMILY`/`drr.DEFAULT_ARCHIVE_DIR` 常量,L45/L53 实读;不占上游已占集合名 [实取·清单: queries(ra)/deep_research_tasks/hypotheses/conditions/events(drr)/deep_research_evidence/rounds(P2-B)/deep_research_triggers/conclusions/disposals(P2-C)/calendar_events(P2-D)]);ID=`VER-{YYYYMMDD}-{NNN}`(DESIGN §3.3 L91 明文族),NNN=同日单调配号(扫集合目录当日最大序号+1,ra.allocate_query_id 同款纪律 L282-299 实读;ymd 取 created_at 日期段) | §3.3 L91+族先例 |
| P-A-12 | 版本记录 schema | §3.3 L91 字段 9 项全落: `{record_type:"conclusion_version", version_id, object_type∈{thesis,view,prediction,deep_research_conclusion}, object_id, change_type, changes:[{field,before,after}…≥1](DP-3(a) 记录级=前值+后值+受影响字段清单), gate_basis, snapshot_id, digest_snapshot, created_at, history:[{ts,note}]}`;快照 digest 由模块经 `rp.digest_snapshot` 重算(API 无 digest 入参,禁采声明值) | §3.3 L91+DP-3 |
| P-A-13 | 门禁依据强制(修正机制,要点④) | `gate_basis` 二选一: `{kind:"trigger", trigger_id:<非空 str>}`(引擎核验已触发的触发器)或 `{kind:"program_evidence", evidence_refs:[<引用 str>,…len≥2]}`(≥2 项程序验证证据)——沿现行门禁语义 [实取·report_generator L503「触发器…被引擎核验为已触发,或本周≥2项新增独立支持证据通过程序验证」/L521 评级门禁同构/L505 确信度门禁];不合法/不足→ValueError fail-loud 零写入;**签名无 bypass/force/skip 类参数**(无弱门禁旁路,§3.3 L93「不设任何弱门禁旁路」);修正提案=change_type "revision_proposal" 记录落档+返回 applied=False(实际状态变更仍走既有回写路径 report_generator 门禁族,本模块旁路零状态文件写入——「不改动既有回写签名,以旁路写入实现」§3.3 L92) | §3.3 L92-93+L174④ |
| P-A-14 | 快照三重纪律(版本记录绑定) | ①`drr._load_snapshot_for_verify` 规范分解加载(L778-801 实读,结构性不可达原始采集档)②`rp.digest_snapshot` 内容重算绑定(禁采声明值)③`rp.gate_allows_formal_research` 放行核验;Gate A=FAIL→fail-closed 拒收(§3.1 L71/L216 红线) | §3.1+WP-D P-D-07 先例 |
| P-A-15 | O-5 接口预留 | `REF_KINDS` 词表含 `deep_research_task`(O-5 对象类,§2.1 L53);`INDEXED_KINDS` 第一期收录集=6 kind(snapshot/formal_report/thesis/view/prediction/conclusion_version)不含之;索引输入遇 O-5 类→`skipped_reserved` 如实清单(不冒充已收录,接口预留=P0-3 落地后接入) | §2.1 L53+§3.2 L77⑤ |
| P-A-16 | 纯度与免责 | import 面白名单={json, os, sys, datetime, deep_research_registrar, research_provenance, fact_engine}(纯标准库+项目既有依赖);AST 零网络 import(urllib/requests/http/socket/httpx 禁);零凭证/密钥/token;模块 docstring+索引文件 note+查询输出 note 携「研究检索面输出,不构成投资建议(禁交易/禁仓位/禁收益承诺)」 | AC-05.4+AC-07+§8.3 红线 |

### §零.6 前置实读登记(file:line;基线工作树 2026-11-07T14:2x-15:0xZ)

- DESIGN 相关节(工作树在场件,=7f43724 侧 blob 等值): §2.1 积累对象清单 L47-53(O-1~O-5)/§2.3 衔接声明 L59-63/§3.1 快照纪律 L69-73/§3.2 检索面 L75-86/§3.3 版本管理 L88-95/§7 层序声明+WP-P3-A 行 L166-174/§8 红线 L214-222/决策点登记表 L226-241;
- INVENTORY: `docs/P3_INVENTORY.md`(P3-G-01/02/08→WP-P3-A 承接面,DESIGN L210 缺口承接句实读);
- 上游在场件(只读禁改,对齐=复用调用):
  - `scripts/research_provenance.py`: gate_allows_formal_research L1210-1213/select_snapshot L1270-1321(含 snapshot_candidates L1257)/digest_snapshot L1324-1328/formal_report_view L1456-1517(8 条校验链)/scan_formal_weekly_reports L1520-1529;
  - `scripts/deep_research_registrar.py`(WP-P2-A): ARCHIVE_FAMILY/DEFAULT_ARCHIVE_DIR L45/L53、_canonical L102-103、_hash8 L106-107、_collection_dir L118-119、_write_records L513-524(append-only 落档)、_record_path L527-528、_load_snapshot_for_verify L778-801;
  - `scripts/research_archive.py`(WP-B4): _same_day_max_seq L282-290/allocate_query_id L293-299(同日单调配号先例)/QB- 键 L278;
  - `scripts/fact_engine.py`: metric() 在场接口(registry 解析面);
  - `scripts/report_generator.py`: 论点状态词表 L501/机制类别 7 类 L518/预测裁决词表 L534/门禁语义 L503-505+L521-523(修正机制门禁依据语义源)/发布事务 L909-924(经 rp 正式性认定面消费);
  - `config/thesis.json`(门禁后状态文件: theses[].{id,status,confidence,quant_triggers[].metric},顶层 last_updated L3;实读无 evidence_ledger/结构化机制标签→P-A-08 登记发现);
  - `config/allocation_views.json`(views[].{id,asset,rating,quant_triggers}+顶层 predictions[].{pred_id,date_made,asset,status,metric,deadline};ratings_scale L5-10);
  - P2 族先例件: `scripts/deep_research_event_calendar.py`(快照三重纪律 load_snapshot_disciplined L281-297/白名单登记制/ID 前缀避占/免责文案先例)、`tests/test_p2_wp_d.py`(合成快照 fixture 形态 L50-84/黄金字面量独立预计算 L37-46 先例)、`docs/P2_WP_D_REPORT.md`(§零 结构先例 L11-114)。

### §零.7 开工核验(2026-11-07T14:24-15:1xZ 实取)

- 步骤0: `git status` clean(开工时在 dev/p2-impl-d@22d8734,工作树干净,非本包所致脏=无);UTC 开工时刻 2026-11-07T14:24:13Z;
- 步骤1: 合同三占位符均实值化(BASE-P3A=8cebe74d…55f1 全值/BASE-P3A-CI-SUITES=82/BRANCH-SET=55 支全表),无未解析标记;
- 步骤2: `git ls-remote origin main`=8cebe74d3a848e4c50681d2a88baca1d3d0c55f1 全值一致 ✓;`git ls-remote --heads origin` 计数=55 ✓ 且 dev/p3-impl-a 零命中(无预创建违规)✓;`git ls-remote origin dev/p3-design-fix1`=7f43724661b50e011394e643cdd8c223c0b27a90 全值一致 ✓(未锚 f93adb5);
  - **BRANCH-SET 零漂移对照方法登记(如实)**: 冻结章 §三.1 全表经人工转录为 /tmp 对照件后与 ls-remote 机器 diff 出现 5 行 SHA 字符级差异(b3-legacy 41hex 非法结构 1 处+glm-g3/p1-impl-b/p1-impl-e/round3-reliability 相似字符置换 4 处);经独立机器记录链裁定=R037 执行后表 `/tmp/r037-post-branchset-api.txt`(55 支 gh api 机器转储,冻结章 §三 捕获注记引用件,在场实取)与本次 ls-remote 机器 diff 差异集=**恰 1 支[main e557fd3→8cebe74d 前移,冻结章 §三 捕获注记在档的两跳=R037 merge 9fb23ecc+Node20 基建笔]**,其余 54 支全值一致零漂移→**5 行差异全部归因于本席人工转录失真,远端零漂移成立**(裁定脚本 /tmp/p3a-branchset-r037-compare.py,VERDICT: MATCHES-FROZEN-CHAPTER-ANNOTATION)。教训承接: 长 SHA 表对照以机器转储链为准(R033/R035/R036/R037 引擎层观察+本合同 §五.2.3 首效条款),本包事件如实登记于此;
- 步骤3: `git checkout -b dev/p3-impl-a 8cebe74d…`(自基线全值切出;本地对象库缺基线对象→先行 `git fetch origin main` 只读取回,e557fd3..8cebe74d)✓;
- 步骤3b(指定并入步,v1.1): `git merge --no-ff 7f43724661b50e011394e643cdd8c223c0b27a90`→merge 提交产生,带入恰 3 A 行(P3 设计三件,517 insertions),无冲突 ✓;
- 步骤4(设计在场核验): ①`git merge-base --is-ancestor 7f43724… HEAD`=exit 0 可达(经并入步)✓;②设计三件 `git ls-tree` 双侧(HEAD vs 7f43724)blob 逐一相同: P3_INVENTORY=9f366da5a9e327e524ae1a17eec229722cd85d5f / P3_DESIGN=5acc130a88d9635a1e82d7ad3beb4f1dbe008106 / P3_DELIVERY=ac8965ce0e09a964f5b493ebe1ef7dcacfca9b2d,与合同 §零 登记三值一致 ✓;
- CI 基线: tests/test_*.py 计数 [实取·开工 2026-11-07T15:0xZ ls 清点,见 §零.10 实现笔回填]=与 BASE-P3A-CI-SUITES=82 槽口径对照(81 exit0+1 SKIPPED);本地 Python 3.9.6(CI=3.11),实现保持 3.9 兼容语法。

### §零.8 零运行产物判定(要点对照)

DESIGN L174 验收要点 5 条: ①负向测试=测试面 ②可重建性测试=测试面(合成 fixture 沙箱) ③append-only 负向+DP 负向=测试面 ④修正提案门禁断言=测试面 ⑤CI 零回归=CI 面(工件=测试文件+run ID,run ID 由操作者 CHECKPOINT dispatch 登记 `rounds/038/P3-WP-A-CI-dispatch-evidence.md`)。五条均无真实运行/编排入口要求(范围列 L172 零「真实运行/端到端/数据档引用」措辞;对照 P2-WP-B 行 L203④「DEV 授权数据副本端到端(数据档引用 data/daily/*_20261102.json)」明文真实运行面,A 行 L174 无对应措辞)→ **本包登记「零运行产物」**,`data/research/` 零写入(索引文件落测试临时沙箱,不落默认路径);`.gitignore` 不改。

### §零.9 AC-03.7(GLM 桩边界)适用判定

登记清单(§零.2)无 GLM/LLM 能力级调用面实现文件(范围列 L172 无 GLM 字样;模块=旁路索引器+结构化查询+版本记录确定性结构;§3.2 查询形态 (b) NL 查询=复用模式B NL→IR 映射停泊面非本包,(c) 关联扫描=WP-P3-B 面)→ **AC-03.7 不适用**,判定依据=清单无调用面类文件(§零.2 表 1-4 无客户端封装/调用编排/适配器类)。

### §零.10 实现期登记(实现笔回填)

**交付物实取行数与指纹**(2026-11-07 实现笔时点):

- `scripts/research_index.py` = **721 行**(wc -l 实取);sha256=`ea782f210ed16340d2c75ee17985d4c7c510a7f86d76e2eb9291d8e0af119c49`
- `tests/test_p3_wp_a.py` = **1081 行**(wc -l 实取);sha256=`307fbee84fe437a00597798290ca098cde395ef7b227bc03500d24b558af68ba`
- 测试面: **75 用例 / 17 类**,`python3 tests/test_p3_wp_a.py` → `Ran 75 tests … OK`(rc=0)。

**用例分类实取**(类名: 用例数): TestGoldenFirstPrinciples 3(黄金字面量×测试内 hashlib 首原理复算逐值相等+索引文档 sha256 独立重演)/TestDPRegistration 4(登记值锚定/哨兵绿/回改检出 monkeypatch×2 面/词表收录集划分)/TestEntrySchema 6(11 键恰集/null 如实缺席/列表规范化去重排序/预留类与未知类拒/坏 ref 与坏日期拒/观测区间倒置拒)/TestSnapshotIndexing 8(当日修订版 v2 权威选择+条目黄金/DEGRADED 放行/Gate A FAIL excluded 如实/混合日放行分裂/采集件结构性不可达零读取零改写/混合目录仅快照被发现/损坏候选 excluded/合成指标 assets=[] 不造值)/TestFormalReportIndexing 3(发布 PASS+DEGRADED 入索引且 digest=None 档键语义/四负向面不入/空目录)/TestStateFileIndexing 5(论点条目/观点 rating=status/预测条目/mechanisms=null 如实缺席/状态档缺失 fail-loud)/TestVersionRecordGolden 5(首记录 trigger 黄金含规范化 gate_basis 与 on-disk 复校/同日单调+跨类型+翌日重起/DEGRADED 快照可绑定/deep_research_conclusion 类型无前缀约束/版本条目索引)/TestVersionValidationNegative 7(门禁依据 8 变体拒+零写入/changes 5 变体拒/对象面拒/快照注入面拒/快照接地缺失拒/Gate A FAIL fail-closed 拒/记录校验器 13 篡改变体逐字段拒)/TestVersionAppendOnly 3(三记录后既有档逐字节不变/篡改档 list fail-loud/并发窗口模拟 rejected-duplicate 且既有档不变)/TestReviseConclusion 2(revision_proposal 入链 applied=False/弱依据仍拒+状态档零写入)/TestIndexDeterminism 4(小索引字节 sha256 黄金/删后重建逐字节一致/重写与同键重放幂等/同键替换非追加)/TestIndexFileFace 6(往返/损坏 JSON/错 schema/键集多与少/排序漂移与重复/预留类条目不可装载)/TestQueryAPI 10(六维度逐一+窗 date 落窗与 obs 相交命中+AND 组合+输出形与确定性排序+mechanisms 如实不匹配+6 负向入参)/TestOSkipping 3(登记项形/预留类不可构造/收录集排除)/TestStaticPurity 4(import 白名单 AST/零网络零凭证 token 面/零 data/daily 字面+严格 glob 字面锚/墙钟仅限 _now_iso)/TestZeroStateWrite 1(record+revise 后状态档逐字节不变+索引默认路径非 config)/TestEndToEnd 1(四源构建 11 条目+重建逐字节一致+查询 5/3/7 命中+O-5 登记项非条目)。

**黄金值登记**: GOLDEN 表 7 项(4 快照指纹+2 报告文件指纹+1 索引文档 sha256),独立预计算脚本 `/tmp/p3a-golden-precompute.py`(证据包 03 成员,首原理 hashlib/json,禁 import 被测模块);fixture 三方一致裁定脚本 `/tmp/p3a-fixture-consistency.py`(证据包 04 成员): 测试 fixture=预计算副本逐字节一致(7 组)+预计算器主路径独立重演值=测试 GOLDEN 表逐值相等(7/7)。

**实现期缺陷修复登记**(如实):
1. **模块侧 1 处**: `query_index` 输出未按 P-A-10 登记语义确定性排序(仅承袭条目序;直接构造索引输入时非 (kind,ref) 序)→ 首轮测试红 3(test_metric_filter/test_output_shape_and_order/test_window_date_inclusion)暴露 → 模块补 `out.sort(key=(kind,ref))` 修复,复绿。非 DP 回改(P-A-10 登记语义本就是确定性排序,实现向登记收敛)。
2. **测试侧 2 处**: ①GOLDEN["INDEX_SMALL_SHA256"] 长串手工折行转录丢 1 字符(`1576|608e2` 应为 `1576|6608e2`),被 TestGoldenFirstPrinciples 测试内首原理复算当场抓获(双源一致机制生效的实证);②`record()` 沙箱助手以 `is not None` 兜底默认值,吞没显式 `None` 负向入参(gate_basis=None/snapshot=None 两用例假绿)→ 改哨兵 `_UNSET` 仅缺席时兜底。

**负向敏感性三注入**(真实缺陷注入→红→还原→复绿→sha256 等值;脚本 `/tmp/p3a-negative-sensitivity.py` 证据包 05 成员):
- INJ-1 门禁依据校验失活(`_validate_gate_basis` 一律放行)→ **红 3**;还原复绿。
- INJ-2 Gate A fail-closed 失活(FAIL 快照放行)→ **红 1**;还原复绿。
- INJ-3 严格快照 glob 失活(任意 `*.json` 皆候选)→ **红 3**;还原复绿。
- 还原后模块 sha256 与注入前锚点**等值**(`ea782f210ed16340d2c75ee17985d4c7c510a7f86d76e2eb9291d8e0af119c49`),零残留。

**本地 CI 镜像重演**(CI 同款方法学: 仓库根 CWD 逐文件 `python3 tests/test_X.py` 直接执行,`test_glm_live` 契约性跳过;首轮以 `-m unittest` 方法学误跑出 2 假失败[helpers 导入面差异]+5 假 SKIP[词面误判],勘误后按 workflow 实取命令重演;脚本 `/tmp/p3a-local-ci-mirror.py` 证据包 06 成员):
- **83 文件 = 82 exit0 + 0 非零 + 1 SKIPPED(test_glm_live)**,基线 82 槽(81 exit0+1 SKIP)零回归+本包恰 1 新增套件。
- 本地 Python 3.9.6(CI=3.11),模块保持 3.9 兼容语法(py_compile 过)。

**零运行产物锚定**: 套件单跑前后 `find data/research -newer <锚>` 零输出(§零.8 判定兑现,索引/版本记录全落测试临时沙箱)。

