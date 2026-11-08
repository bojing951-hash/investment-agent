# IA-P3-WP-E REPORT — P3 收尾层第 5 实现包(个人流程整合接口)

> 包: IA-P3-WP-E(P3 族第 5 实现包,#37 挂靠;依赖列前件=WP-P3-D) · 执行Agent: Agent 3 · 分支: `dev/p3-impl-e`
> 基线: BASE-P3E=`91612378d2f095530e1f29faa48d53e959d5fe13`(origin/main,开工 ls-remote 实取全值一致)
> 合同: IA-P3-WP-E-AC-v1.0(冻结,附录A 内嵌注入)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY/上游在场件行号一律为**本包基线工作树实读**行号(2026-11-08T01:3x-02:0xZ 实取,基线=BASE-P3E 工作树);提示词注入内容引用一律标注「注入摘要,非工作树实读」。
> 数值标注边界: 本文所有计数类/统计类数值逐个二选一标注 `[实取·来源: …]` 或 `[示意·非实取]`;日期/SHA/结构编号(WP-P3-E/#31-38/P3-G-06 等)/档键成分(ID 格式字符串,如 `ANN-20261108-001`)按合同边界出圈登记。

---

## §零 规格抄录与交付面登记(开工首步,AC-01;登记后即本合同白名单实体)

### §零.1 DESIGN §7 WP-P3-E 行四要素逐字抄录

实读 `docs/P3_DESIGN.md`(基线工作树在场,blob `5acc130a88d9635a1e82d7ad3beb4f1dbe008106`,§零.7 核验与 7f43724 侧等值),WP-P3-E 行位于 L194-L198,逐字抄录:

```text
L194: **WP-P3-E 个人流程整合接口**(挂靠编号: **#37**)**PENDING·用户实批前置**(接入用户个人流程属用户确认事项,DP-9;启用前零实现)
L195: - 目标: 落地 §6.2 接口(a)标注/(b)笔记引用/(c)导出。
L196: - 范围: 接口格式定义与旁路标注档/导出渲染;零私有数据主动采集;用户数据落 DEV 或用户指定路径。
L197: - 依赖: WP-P3-D(导出产物来源);**用户实批(接口形态与启用时点)**;层序前置(同上)。
L198: - 验收要点草案: ①零主动采集断言(全仓无用户数据拉取路径)②个人观察证据不冒充程序验证证据断言(来源等级隔离)③用户数据零落 LIVE 断言 ④CI 零回归。
```

四要素齐备(目标 L195/范围 L196/依赖 L197/验收要点 L198 共 4 条),无缺失。核验:
- **E 行可区分性**: 与 A/B/C/D/F 行四要素逐项可区分(A=档案检索与结论版本管理 L170-174/B=新证据关联与持续跟踪聚合 L176-180/C=预测复盘与错误模式统计 L182-186/D=报告质量评价循环 L188-192[同族前列件行]/F=终验+总封版 L200-208;E 行题名「个人流程整合接口」与挂靠 #37、接口格式定义+旁路标注档+导出渲染范围要素、零主动采集/来源等级隔离/零落 LIVE 三断言要点均为他行所无)→ 合同附录A §零(iv)冲突处置首项不触发;冻结章 §十一 注记行号 L194-198 与本实读一致(偏差 0 行,≤3 行容差内);
- **依赖列核验**: 「WP-P3-D(导出产物来源)」=同族前包 R041 整体 PASS 已合入 main(冻结章 §十一 生效前置达成登记,注入摘要,非工作树实读;其终笔尖端 f349b83 已 merge 91612378=本 BASE,父=aeb39e8+f349b83 [实取·`git log --format='%H %P' -1 91612378` 工作树实取=merge 双父]),交付件在本基线工作树在场(`scripts/report_quality_review.py`+`tests/test_p3_wp_d.py`+`docs/P3_WP_D_REPORT.md`+`docs/P3_WP_D_DELIVERY.md` [实取·本工作树 git ls-files 清点=4 件,与 WP-D REPORT §零.2 登记清单一致]);「导出产物来源」=本包接口(c)导出面消费入口(P-E-07,WP-D 编排面 `report_quality_review()` 返回文档承载 §6.1 质量简报+经其直通承载 §5 错误模式统计);「用户实批(接口形态与启用时点)」=DP-9 确认型决策,用户已于 2026-11-08 实批达成(§零.4 登记,冻结章 §十一 凭证,注入摘要,非工作树实读);「层序前置(同上)」=§7 L168 层序排程依赖声明(冻结章 §十一 登记逐层核验 ✓,注入摘要,非工作树实读);依赖列与 BASE-P3E(`91612378…`)无矛盾、**不要求并入其他支**(本包无并入步,纯线性)✓;
- **范围列无真实 GLM 调用/网络出站/付费凭证要求**: 范围列 L196 零 GLM/网络/凭证/付费字样;三件(接口格式定义/旁路标注档/导出渲染)均为确定性结构;所引 §6.2 L155 设计原则明文「零私有数据采集预设——系统**不主动采集**任何用户私有流程数据;一切整合 = 用户**主动推送/标注**;用户数据只落 DEV 仓或用户指定路径,禁落 LIVE」+L157「实现全部 PENDING·用户实批前置」——该 PENDING 前置已由用户 2026-11-08 实批解除(§零.4),本包据此实现,无情形(d)停止条件。

### §零.2 交付文件清单(k=4 [实取·本节清点],登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据(推导逐条附) |
|---|---|---|
| 1 | `scripts/personal_flow_integration.py` | DESIGN L196 范围列三件(接口格式定义与旁路标注档/导出渲染+两纪律面[零主动采集/用户数据落 DEV 或用户指定路径])=**恰 1 个代码模块**: WP 题名「个人流程整合接口」(L194)单一工作包,三件共享同一接口族(§6.2 L157-160 接口 3 个同节定义)、同一用户数据边界原则(L155 设计原则三红线)与同一 DP-9 参数面(L197 依赖列单点)+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」;文件名=域词 personal(个人)+flow(流程)+integration(整合,WP 行题名「个人流程整合接口」用词),避开既有全部 scripts/ 文件(ls scripts/ 实读,命名不冲突 [实取·开工 grep -ri personal_flow scripts/ tests/ docs/=0 命中]) |
| 2 | `tests/test_p3_wp_e.py` | DESIGN L198①②③④工件「断言」+合同附录A §零(ii)「含代码则必含 tests/test_p3_wp_e.py」 |
| 3 | `docs/P3_WP_E_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P3_WP_E_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L198④「CI 零回归」证据落点=DELIVERY |

### §零.3 结构约束核验(2026-11-08T01:5xZ 实取)

- 与 `git ls-files` 零重合: 4 路径 `git ls-files scripts/personal_flow_integration.py tests/test_p3_wp_e.py docs/P3_WP_E_REPORT.md docs/P3_WP_E_DELIVERY.md` 输出=0 行 [实取·开工 git ls-files]→ 纯新增 ✓;
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p3_wp_e.py)✓;
- 推导无越界: 范围列恰 1 个代码模块(§零.2 行 1 依据,同族前列件 WP-A/WP-B/WP-C/WP-D 单模块先例 P-A-01/P-B-01/P-C-01/P-D-01 同构)→ scripts/ 恰 1 文件;未引入 DESIGN 依据外文件 ✓。

### §零.4 DP 登记(开工首步登记定值;DESIGN 决策点登记表 L226-L241 实读,DP 共 10 个 [实取·表清点],E 行内所引=DP-9[确认型,已由用户实批])

| DP | 分类(DESIGN 实读) | 本包登记定值(登记即实现值,先登记后运行,禁回改) | 依据 |
|---|---|---|---|
| DP-9 #37 接口形态与启用时点 | 确认权留用户(L238;E 行 L197 明文「用户实批(接口形态与启用时点)」) | **用户已实批,本包据此实现,非执行Agent自决**: 用户 2026-11-08 实批「批准,发车 #37」——接口形态=§6.2 接口 3 个**同批全启**(a 标注/b 笔记引用/c 导出,选项 (b) 三接口同批),启用时点=即日发车;三红线随形态一并实批: 零主动采集/个人观察不冒充程序验证[来源等级隔离]/用户数据零落 LIVE(冻结章 §十一 生效前置达成登记=凭证载体,注入摘要,非工作树实读;PENDING-APPROVALS.md 留痕@engine 侧,执行席不可达如实声明;用户保留事后否决权)。模块登记承载: `DP9_INTERFACE_SET=("annotation","note_reference","export")` 三接口全启+`DP9_USER_APPROVAL` 实批时点标记+三红线常量(P-E-02/P-E-14) | L238+L197+L155-162+冻结章 §十一 |
| DP-1/DP-2/DP-3 | 登记型(L230-232) | **上游 WP-P3-A 已登记定值**(旁路索引文件/O-1~O-4 全 4 类/记录级粒度;本包零消费零改写——E 面无检索/版本链面;WP-A REPORT §零.4 登记在案) | L230-232 |
| DP-5/DP-6 | 登记型(L234-235) | **上游 WP-P3-C 已登记定值**(四轴×滚动 12 个月/inconclusive·not_yet_triggered 不入分母单列;本包经 WP-D 编排产物**间接原样承载**(接口(c) error_pattern_statistics=prd 统计文档 passthrough,零重算零改写零重开窗,窗口/分母口径=上游登记值;WP-C REPORT §零.4 登记在案) | L234-235 |
| DP-7 | 登记型(L236) | **上游 WP-P3-D 已登记定值**(维度 5 项全启+阈值首期;本包接口(c) 导出面承载其质量文档/简报/建议清单**原样**,零改写零注入零重算;WP-D REPORT §零.4 登记在案) | L236 |
| DP-4/DP-8/DP-10 | 确认权留用户(L233/L237/L239) | **本包零触及**: DP-4=§4.1 关联第三层(WP-P3-B 面)、DP-8=§6.1 提示词注入(WP-P3-D 面)、DP-10=终验观察窗(WP-P3-F 面)——均非 E 行范围列(L196)所及,本包无 GLM/注入/LIVE 面导出建议清单原样携带 requires_user_confirmation=true 标记(上游 WP-D 已置,本包零改动) | L233/L237/L239 |

DP 编号/数量/分类与 DESIGN 实读一致: 行内所引 DP-9(L197 明文)确认型,其确认权**已由用户本人行使**(2026-11-08 实批,冻结章凭证,非本包自决实施——合同 AC-02 判据 6「确认型 DP 未被自决实施」=执行Agent 零自决,用户实批凭证在案);其余 DP(登记型 DP-1/2/3/5/6/7=上游登记面零改写或间接原样承载;确认型 DP-4/8/10=零触及)分类与 DESIGN L230-L239 表逐行一致。

### §零.5 实现参数登记(P-E-01..P-E-19,先登记后实现,运行后禁回改)

| # | 参数 | 登记定值 | 依据 |
|---|---|---|---|
| P-E-01 | 模块载体 | `scripts/personal_flow_integration.py` 恰 1 文件(接口格式定义+旁路标注档+导出渲染三组件同模块,§零.2 行 1) | DESIGN L196+§零.2 |
| P-E-02 | DP-9 接口集与启用承载 | `DP9_INTERFACE_SET=("annotation","note_reference","export")` 三接口同批全启+`DP9_USER_APPROVAL="user_approved_2026-11-08_immediate"`(用户实批时点与即日启用标记,凭证=冻结章 §十一,注入摘要非工作树实读);三红线常量承载(见 P-E-14);运行期哨兵 dp_selfcheck 对照(回改任一→AssertionError) | DP-9+§零.4+L155 |
| P-E-03 | 接口(a) 个人技术分析标注记录格式 | 6 字段封闭集 `{schema_version:1, annotation_id, date, asset, view, basis}`(DESIGN L158「含日期/资产/观点/依据」4 用户字段+schema_version+annotation_id 系统字段;build 签名固定,外部不可增删字段);date=规范 YYYY-MM-DD(规范形守卫同族先例: 十位带杠形才入 fromisoformat,紧凑形/周形拒绝,3.9/3.11 行为一致);asset/view/basis=非空非全空白字符串;annotation_id 形=ANN-YYYYMMDD-NNN(P-E-12) | DESIGN L158 |
| P-E-04 | 标注档形态与 append-only(DESIGN §8.5 红线「标注档只追加」) | 旁路标注档=JSONL(每行恰 1 条规范 JSON 记录,`json.dumps(record, sort_keys=True, ensure_ascii=False)` 单行+换行);写入=open(path,"a") 纯字节追加,零改写既有行;重复 annotation_id→ValueError fail-loud;零改写面=模块无 update/delete/rewrite 类 API(AST+dir 扫描测试面);read=逐行 json.loads,坏行/非 dict 行→ValueError fail-loud(档案损坏如实暴露,不静默跳过) | DESIGN L158+L220 |
| P-E-05 | 接口(b) 个人研究笔记引用记录格式 | 6 字段封闭集 `{schema_version:1, note_id, date, archive_key, metric_refs, source_level}`(DESIGN L159 登记格式「档键+指标引用+日期」3 用户字段+note_id+schema_version+source_level 系统强制字段);date 规范形同 P-E-03;archive_key=非空非全空白字符串(档键字符串,值域成分出圈登记);metric_refs=字符串列表**至少 1 项**且逐项非空字符串(登记格式要求指标引用在场;空列表→ValueError);**source_level 恒 "个人观察"**——build 签名无此参数(用户不可传入),记录由 build 函数强制写入(P-E-06 隔离承载) | DESIGN L159 |
| P-E-06 | 来源等级隔离(要点②: 个人观察不冒充程序验证证据) | 三面隔离——①**词表隔离**: `NOTE_SOURCE_LEVEL="个人观察"` ∉ 证据分级 v2 机制 7 类词表(增长/通胀/利率与流动性/信用/避险与估值/供应与库存/资金流,rg L518 词面登记锚)∪ 星级串集("1".."5");②**键集隔离**: note 记录键集 ∩ v2 evidence 项字段名集 {metric,value,obs_date,mechanism,contrary,explained,neutral}(rg L518 词面锚)=∅——note 记录零 mechanism/confidence/星级字段,不参与星级计算与门禁核验(与 `config/allocation_views.json` L4 证据分级 v2 词表隔离,DESIGN L159 明文);③**渲染隔离**: render_note_references 逐条强制携带标签「来源等级=个人观察(证据分级外,不参与星级与门禁核验)」,全部笔记渲染面零"★"字符;哨兵 `source_level_isolation_check()` 运行期三面对照(任一破坏→AssertionError) | DESIGN L159+L198② |
| P-E-07 | 接口(c) 复盘结论导出文档格式 | `EXPORT_SCHEMA_VERSION=1`;输入=WP-D 编排面 `report_quality_review()` 返回文档 `{statistics,suggestions,briefing,prediction_review}`(校验: statistics 为 dict 且 statistics.schema_version==`rqr.STATS_SCHEMA_VERSION` **复用调用锚**(禁止本地重实现该常量);briefing=非空 str;suggestions=list;prediction_review.statistics=dict);导出文档 8 键 `{schema_version:1, note:<免责+单向声明>, as_of, window_kind, window_start, window_end(镜像质量文档窗口字段), quality_briefing(§6.1 质量简报原文), error_pattern_statistics(§5 统计文档=prd 统计原样承载,零重算零改写), suggestions(建议清单原样,requires_user_confirmation=true 标记随上游原样携带)}`;全键 str(零 None 键) | DESIGN L160+L195+依赖列 L197 |
| P-E-08 | 导出渲染与单向纪律(零回读) | `render_export_briefing(doc)` 纯文本: 标题行(单向导出·零回读)+窗口行+质量简报原文段(逐字嵌入)+错误模式统计段(counts 行[hit/miss/inconclusive/not_yet_triggered 终态+命中率,分母 0→「N/A(分母=0,如实缺席)」]+error_patterns 行[四桶])+建议清单计数行+免责尾行;`write_export_document(export_path, content, user_root=None)` 显式路径写入(open "w" 恰 1 处,返回规范化路径),写入后零回读;**结构性零回读**=模块无任何函数读取用户个人复盘流程数据或已导出产物(AST 测试面: 导出面零 read) | DESIGN L160「单向导出…零回读」 |
| P-E-09 | 零主动采集纪律(要点①) | 零网络 import(AST 白名单面);零目录扫描(os.listdir/os.walk/os.scandir/glob 零调用,AST 测试面);零文件监视/零定时轮询;一切输入=调用方显式传入(用户主动推送/标注,DESIGN L155「一切整合=用户主动推送/标注」);读取面仅 read_annotations/read_note_references 对显式传入档路径(=用户推送档);模块级路径常量唯一=`_DEV_ROOT`(由 __file__ 只读推导,守卫用);测试面另扫 P3 族五模块(research_index/evidence_linkage/prediction_review/report_quality_review/personal_flow_integration)零网络 import(P3 层零用户数据拉取路径断言) | DESIGN L155+L198① |
| P-E-10 | 写入域双守卫(要点③: 用户数据零落 LIVE/落 DEV 或用户指定路径) | ①`_reject_live_path`: 路径 expanduser+normpath 后组件序列含 LIVE 根四组件序列(AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent;组件化 `_LIVE_ROOT_GUARD` 四元组,**源码零连续 LIVE 路径字面量**,AST 字符串常量测试面)→ValueError fail-loud;**读写面均适用**,user_root 指向 LIVE 根亦拒(红线绝对性);②`_write_root_guard`: 写入路径规范化后须在 DEV repo root(__file__ 推导 `_DEV_ROOT`)或显式 `user_root` 目录之下(DESIGN L196「用户数据落 DEV 或用户指定路径」;user_root=调用方显式指定的用户目录);两守卫+P-E-11 守卫合成 `_guard_write_path` 适用三写入面(标注档/笔记档/导出件)与两读取面 | DESIGN L155/L196+L198③ |
| P-E-11 | 快照纪律路径守卫(AC-07.1) | `_reject_raw_data_path` 同族先例(WP-D P-D-04 同款): 路径 normpath 后组件序列含 `data`+`daily` 相邻组件(组件化 `_RAW_DIR_GUARD=("data","daily")`,源码零连续字面量)→ValueError fail-loud;适用标注档/笔记档/导出路径全部读写面(经快照/事实引擎/研究档案标准化接口转递不在此限——本包旁路档为用户数据非采集数据,守卫防误指) | AC-07.1+DESIGN §3.1 L72 |
| P-E-12 | 档键 ID 分配(ANN-/NOTE- 族) | `ANN-YYYYMMDD-NNN`/`NOTE-YYYYMMDD-NNN`(YYYYMMDD=记录 date 去杠形;NNN=3 位零填充 001-999);同日单调配号=档内同日已有最大序+1(首条=001;仿 research_archive QB- 同日配号先例[WP-A REPORT §零.6 引用面];跨日独立起算);显式传入 ID 须合法形且日期段==记录 date,否则 ValueError;序号>999→ValueError fail-loud | DESIGN §3.3 版本键 VER- 族先例+§3.2 档键前缀族 |
| P-E-13 | 确定性序列化 | 导出文档= `json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=1)`(家族先例 P-A-03/P-C-08/P-D-13 同款);档内单行记录=同参无缩进单行形+`\n` | AC-03 确定性 |
| P-E-14 | 免责与三红线常量承载 | 免责三处=模块 docstring+标注/笔记视图渲染尾行+导出渲染尾行(词面携「不构成投资建议(禁交易/禁仓位/禁收益承诺)」+「用户个人观点,系统零采集零核验零背书」;§8.3 L218 红线承接);三红线常量=`ZERO_ACTIVE_COLLECTION`/`SOURCE_LEVEL_ISOLATION`/`ZERO_LIVE_FALL`(§6.2 L155 设计原则三要素词面承载,渲染于视图/导出面标题区) | DESIGN L155+§8.3 L218 |
| P-E-15 | 上游复用面(对齐=复用调用,禁复制分叉) | rqr: `STATS_SCHEMA_VERSION` 常量锚(导出输入 schema 校验,唯一上游符号依赖);导出内容面=调用方传入的 WP-D 编排产物**原样承载**(briefing/statistics/suggestions/prediction_review.statistics 零重算零改写, passthrough 等值测试面);零 rg/dv/ae/prd/rp/snapshot_builder 直接依赖(E 面无取数面);零本地重实现(AST import 白名单锚) | AC-05.5+依赖列 L197 |
| P-E-16 | 纯度 | import 白名单={json,os,sys}+项目既有 report_quality_review(纯标准库+项目既有依赖);AST 零网络 import(urllib/requests/http/socket/httpx 禁);零凭证/密钥/token;open 模式白名单=标注档/笔记档追加 "a" 恰 2 处+导出件 "w" 恰 1 处+其余全 "r"(AST 测试面);Python 3.9 兼容语法(本地 3.9.6/CI 3.11,家族同款约束) | AC-05.4+AC-03 |
| P-E-17 | DP/参数哨兵 | `registered_dp_values()`+`registered_param_values()`(活性常量)+`dp_selfcheck()`(活性常量 vs 模块内登记镜像逐值对照,回改任一定值→AssertionError;另含三接口集完整性/三版本号/来源等级/守卫元组一致性断言);`__main__` 自检入口零写入零默认路径 | DP 纪律+WP-A/B/C/D 先例 |
| P-E-18 | 他包范围排除 | WP-P3-A/B/C/F 零实现零引用(WP-C/WP-D 面=经编排产物间接原样承载,见 P-E-15);**rg L545 周报「技术分析部分标注 [待用户补充]」槽位零触碰**(接口(a)=旁路结构化标注档扩展,零周报提示词/模板改动——白名单 M=0 结构性保障+上游 sha 字节级测试面);W4/W5 侧边验收工具零接入(AC-07.6);版本链/关联档案/统计器面零触碰;零状态档写入(论点/观点/预测状态保护面零接触,AC-07.5) | AC-08.1+DESIGN L158 |
| P-E-19 | 零运行产物判定 | E 行验收要点 4 条(L198①-④)全为断言面/CI 面(①②③=测试断言,④=CI 工件;范围列 L196 零「真实运行/端到端/编排入口要求」措辞;对照家族先例 P-D-20 同构判定[R041 整体 PASS 先例])→ **本包登记「零运行产物」**,`data/research/` 零写入(标注/笔记档运行期属用户使用面,非本包交付运行产物;测试全落临时沙箱);`.gitignore` 不改 | 合同§零 运行产物边界+要点对照 |

### §零.6 前置实读登记(file:line;基线工作树 2026-11-08T01:37-02:0xZ 实取)

- DESIGN 相关节(工作树在场件,=7f43724 侧 blob 等值,§零.7): §3.1 快照纪律 L69-73(禁直读 data/daily L72)/§6.2 个人流程整合 L153-162(设计原则 L155/接口级设计 L157-160[(a) 标注 L158/(b) 笔记引用 L159/(c) 导出 L160]/DP-9 句 L162)/§7 层序声明 L168+WP-P3-E 行 L194-198(E 行;同族前列件行 A L170-174/B L176-180/C L182-186/D L188-192;F 行 L200-208 仅区分对照)/§8 红线 L214-222(快照纪律 L216/LIVE 禁写 L217/禁建议 L218/批量修改 L219/**append-only L220[「版本记录/关联记录/标注档/终验清单只追加」——标注档在列]**/GLM 凭证 L221/如实 L222)/决策点登记表 L226-241(DP-9 L238;DP-1/2/3 L230-232/DP-4 L233/DP-5/6 L234-235/DP-7 L236/DP-8 L237/DP-10 L239);
- 上游在场件(只读禁改,对齐=复用调用):
  - `scripts/report_quality_review.py`(WP-P3-D,依赖列前件交付件): STATS_SCHEMA_VERSION=1 L76/REVIEW_NOTE L99-103/registered_dp_values·registered_param_values·dp_selfcheck L187-236/_reject_raw_data_path L147-158(守卫先例)/render_quality_briefing L588-628(免责尾行先例)/report_quality_review 编排面 L633-657(**接口(c) 导出输入文档来源**: 返回 {statistics,suggestions,briefing,prediction_review})/__main__ selfcheck L662-674;
  - `scripts/prediction_review.py`(WP-P3-C,经 WP-D 编排产物间接承载): _statistics_from_rows L454-502(**§5 统计文档 schema**: schema_version/note/as_of/window_start/window_end/counts{hit,miss,inconclusive,not_yet_triggered_terminal,hit_rate,out_of_window_terminal,non_terminal_excluded}/error_patterns{direction_error,horizon_error,magnitude_error,unclassifiable}/correct_samples/premise_class/excluded_pending/buckets/discrepancies)/review_statistics L505-512/prediction_review_report L622-635;
  - `scripts/report_generator.py`(周报主流程件,本包禁改,引用面): 证据分级 v2 校验块 L518(机制 7 类词面: 增长/通胀/利率与流动性/信用/避险与估值/供应与库存/资金流;evidence 项字段 metric/value/obs_date/mechanism/contrary/explained/neutral——P-E-06 隔离对照词表锚)/**L545「技术分析部分标注 [待用户补充]」槽位**(接口(a) 语义先例,P-E-18 零触碰面)/L516 rating 词表/L501 论点状态词表;
  - `config/allocation_views.json` L4(note: 证据分级 v2 程序校验描述——星级=独立证据数×机制类别×观察期,未解释反证封顶 3★;**P-E-06 隔离对象词表面**);
  - `scripts/research_archive.py` L282-299(WP-B4,_same_day_max_seq/allocate_query_id 同日单调配号先例——P-E-12 配号口径先例,经 WP-A REPORT §零.6 引用面转引,本包未直接依赖);
  - 同族前列件 REPORT §零.2 登记清单(各 k=4 [实取·L30-37 逐件实读]): WP-A(`scripts/research_index.py`+`tests/test_p3_wp_a.py`+REPORT+DELIVERY)/WP-B(`scripts/evidence_linkage.py`+`tests/test_p3_wp_b.py`+REPORT+DELIVERY)/WP-C(`scripts/prediction_review.py`+`tests/test_p3_wp_c.py`+REPORT+DELIVERY)/WP-D(`scripts/report_quality_review.py`+`tests/test_p3_wp_d.py`+REPORT+DELIVERY);
  - `docs/P3_INVENTORY.md`: a.4 报告制度 L51-59/a.6 P3 特有新能力面 L68-76(逐项不存在)/缺口表 P3-G-06→WP-P3-E L161(#37 个人技术分析/投资研究流程整合零接口→a.6 全缺——本包填补缺口);
  - `.gitignore` L1(`data/` 全忽略——研究档案/用户数据档不 commit 结构性保障,合同§零 运行产物边界承接)。

### §零.7 开工核验(2026-11-08T01:37-01:5xZ 实取)

- 步骤0: `git status` clean(开工时在 dev/p3-impl-d@f349b83,工作树干净,非本包所致脏=无);UTC 开工时刻 2026-11-08T01:37:32Z;
- 步骤1: 合同三占位符均实值化(BASE-P3E=91612378d2f095530e1f29faa48d53e959d5fe13 全值/BASE-P3E-CI-SUITES=86/BRANCH-SET=59 支全表 §十一.1 内嵌),无未解析标记 ✓;生效前置信号=冻结章 §十一 生效前置达成登记(WP-P3-D R041 整体 PASS+用户实批 DP-9「批准,发车 #37」+层序闭合,注入摘要,非工作树实读)✓;
- 步骤2: `git ls-remote origin main dev/p3-impl-d dev/p3-impl-c dev/p3-design-fix1 dev/p3-design dev/p3-impl-e` 实取: main=`91612378d2f095530e1f29faa48d53e959d5fe13`(=BASE-P3E 全值一致 ✓)/dev/p3-impl-d=`f349b83a5cc1cdbaefca3c204473b3e64b31071f`(=冻结表登记值一致 ✓)/dev/p3-impl-c=`57eb3a3742628f9643b9e23e1a78862234d6c7bd`(一致 ✓)/dev/p3-design-fix1=`7f43724661b50e011394e643cdd8c223c0b27a90`(全值一致 ✓,未锚 f93adb5)/dev/p3-impl-e 零命中(无预创建违规 ✓);全量 ls-remote 留证(证据包 03 类);
- 步骤3: `git checkout -b dev/p3-impl-e 91612378…` 自基线全值切出(非自当前 HEAD 盲切)✓;
- 步骤4(设计在场核验,本包无并入步): ①`git merge-base --is-ancestor 7f43724661b50e011394e643cdd8c223c0b27a90 HEAD`→exit 0 可达(经祖先在场,冻结章 §十一 路径甲注记一致)✓;②设计三件 `git ls-tree` 双侧(HEAD vs 7f43724)blob 逐一相同: P3_INVENTORY=9f366da5a9e327e524ae1a17eec229722cd85d5f/P3_DESIGN=5acc130a88d9635a1e82d7ad3beb4f1dbe008106/P3_DELIVERY=ac8965ce0e09a964f5b493ebe1ef7dcacfca9b2d ✓;
- 步骤5: §7 实读 WP-P3-E 行在场(L194-198)四要素齐备,与 A/B/C/D 行可区分(§零.1)✓;范围列非文件级→固定推导规则生成清单(§零.2)✓;依赖列无并入他支要求/无真实 GLM·网络·凭证·付费要求 ✓;
- CI 基线: `ls tests/test_*.py` 计数=86 [实取·开工清点]=BASE-P3E-CI-SUITES 86 槽口径一致(85 exit0+1 SKIP,冻结章 §十一 CI 基线实值依据;分支 run 预期=86+本包新增 tests 文件数 1=87);本地 Python 3.9.6(CI=3.11),实现保持 3.9 兼容语法(WP-A/B/C/D 同款约束;日期解析规范形守卫同族先例,R040 续段教训承接)。

### §零.8 AC-03.7(GLM 桩边界)适用判定

登记清单(§零.2)无 GLM/LLM 能力级调用面实现文件(范围列 L196 零 GLM 字样;模块=接口格式定义+旁路标注档+导出渲染确定性结构;DESIGN L157「实现全部 PENDING·用户实批前置」所指=接口启用面[DP-9,已实批],非 GLM 调用面)→ **AC-03.7 不适用**,判定依据=清单无调用面类文件(§零.2 表 1-4 无客户端封装/调用编排/适配器类)。

### §零.9 实现期登记(报告笔回填;时点=各笔提交时点)

- **交付双代码件定值**(sha256 实取):
  - `scripts/personal_flow_integration.py` 721 行,sha256=`7985308c995cc5ea94a3dafdcccb0997003a67a8b1472e5e2b2f7c87d3359096` [实取·实现笔 04e30fc 提交时点 `git hash-object`/hashlib 双源;终笔时点 `git show` 复核为准;补齐笔后零改动,负向敏感性三注入还原后 sha 零残留等值核验];
  - `tests/test_p3_wp_e.py` 实现笔 1251 行/126 用例(sha256=`437e0284a72200f6b29370e5e9554da3f87469392e15471830ecffb59622b351`)→ 测试补齐笔 1b50fc3 终态 **1301 行/129 用例**(sha256=`6b4a8c77681d6bf23bb62e134f9f55b504d98efaf1991e35e70b56473c653b2a`)[实取·wc -l+hashlib@补齐笔工作树];
- **黄金六面 sha256 双源一致** [实取·/tmp/p3-wp-e/fixture_and_golden.py(零被测模块 import 首原理件)与 cross_check.py(模块实跑)交叉裁定 ALL MATCH,六面逐字节全等]: G1 标注视图 `3379001e…e8c3c2`/G2 笔记视图 `c350686f…aceb0`/G3 标注档字节 `146c74b8…8ff13`/G4 笔记档字节 `d9112cec…365a4`/G5 导出文档序列化 `dea070d6…7288f`/G6 导出渲染 `20a5c876…4a59b`(全值见测试件 GOLDEN_SHAS L90-107 字面量);
- **本地测试**: 129 用例 18 类 OK [实取·`python3 -m unittest tests.test_p3_wp_e` @3.9.6,verbose stdout 证据包 06 类];
- **本地 CI 镜像**(CI 同款方法学,逐 tests/test_*.py 独立运行): 87 件=86 exit0+1 SKIP(test_glm_live 身份锚)+0 非零 [实取·/tmp/p3-wp-e/local_ci_mirror.py 终态记录;开工基线 86 槽零回归+本包恰 +1];
- **负向敏感性三注入**(终态 129 用例面复跑): 定值回改(NOTE_SOURCE_LEVEL→"增长")9 红/LIVE 写入守卫旁路 2 红/append 'a'→'w' 4 红→还原复绿→模块 sha256 零残留(=7985308c… 等值)[实取·注入脚本与记录,证据包 06 类];
- **双解释器**: 系统 3.9.6 全套件 129 OK+selfcheck;3.10+ 执行席不可达(command -v/目录面沙箱拦截,如实登记,WP-D 08 类同款先例);**规范形日期守卫零版本依赖证明链=纯字符串+月长表+闰年规则判定,零 datetime.fromisoformat(其 3.11 宽形接受面[紧凑形/周形]在本实现结构性不存在)**,3.9/3.11 行为一致由构造保证;CI=3.11(offline-tests.yml L29 实读);
- **实现期对账与自纠 6 项**如实登记(全项详见 §三): 模块-登记对齐 2(open 'a' 内联化恰 2 处+零 datetime 纯日历化,P-E-16 白名单优先)+测试字面量自纠 3(首跑 3 红对账: 截断语义归位/渲染隔离断言归位/路径类常量封闭集归位)+测试补齐笔 1(P-E-09/P-E-08/P-E-04/P-E-17 四登记面补齐,1b50fc3);
- **零运行产物**: `data/research/` 与 `data/daily/` 零写入,repo 零本包运行产物 [实取·双 find 锚定扫描=0 行,证据包 06 类;测试全落 tempfile 沙箱+selfcheck 零写入断言(test_selfcheck_main 运行目录零新文件)];`.gitignore` 零改动。

---

## §一 实现摘要(四组件;按 §零.4/§零.5 登记定值实现)

1. **接口(a) 个人技术分析标注**(P-E-03/P-E-04;DESIGN L158): `build_annotation(date,asset,view,basis,annotation_id=None)` 纯函数构造 6 字段封闭集记录(date 规范形守卫/asset·view·basis 非空非全空白/显式 annotation_id 形校验须与 date 日期段一致);`append_annotation(archive_path,record,user_root=None)` JSONL append-only 入档(§8.5 L220 红线「标注档只追加」: open "a" 纯字节追加,前缀字节保逐字节不变[测试断言]+同日单调配号 ANN-YYYYMMDD-NNN+重复档键拒);`read_annotations` fail-loud(坏行/非 dict 行/缺档键/重复档键→ValueError,档案损坏如实暴露)。
2. **接口(b) 个人研究笔记引用**(P-E-05/P-E-06;DESIGN L159): `build_note_reference(date,archive_key,metric_refs,note_id=None)` 登记格式构造,**source_level 由系统强制写入「个人观察」且签名无此参数=用户不可传入**(来源等级隔离承载面);来源等级隔离三面哨兵 `source_level_isolation_check()`(词表: 「个人观察」∉ v2 机制 7 类∪星级串/键集: note 键集∩v2 evidence 项字段=∅/渲染: 隔离标签词面完整性),渲染面零 ★ 字符;append/read 同接口(a) 纪律。
3. **接口(c) 复盘结论导出**(P-E-07/P-E-08/P-E-15;DESIGN L160): `validate_export_input` 锚 `rqr.STATS_SCHEMA_VERSION` 复用调用(禁本地重实现);`build_export_document` 9 键装配,内容面原样承载零重算(briefing/suggestions/prd statistics **引用同一性**测试断言 passthrough);`dump_export_document` 确定性序列化(sort_keys/ensure_ascii=False/indent=1);`render_export_briefing` 简报原文逐字嵌入+错误模式统计四桶轴+建议清单计数行(DP-8 标记随上游原样携带零注入)+免责尾行;`write_export_document` 单向导出零回读(open "w" 恰 1 处,函数体零读取面 AST 断言)。
4. **守卫与哨兵面**(P-E-09..P-E-14/P-E-16..P-E-18): 三红线承载(零主动采集[零网络 import/零目录扫描/零监听,模块级路径类常量封闭集={_RAW_DIR_GUARD,_LIVE_ROOT_GUARD,_DEV_ROOT}]/来源等级隔离[三面]/用户数据零落 LIVE[LIVE 根四组件序列拒读写导出三面+user_root 自身 LIVE 拒+~/ 形 expanduser 后同拒+写入域=DEV 仓∪显式 user_root])+快照纪律 data+daily 相邻组件 fail-loud(相邻性精确,data/other/daily 不误拒)+免责三处(模块 docstring+两视图尾行+导出尾行)+dp_selfcheck 登记镜像哨兵(活性常量 vs 模块内镜像,回改任一定值→AssertionError,monkeypatch 三面检出实证)+AST 纯度面(import 白名单恰 {json,os,sys,report_quality_review}/open 模式记账 'a'×2+'w'×1+'r'×1/sys.path.insert 恰 1/LIVE 与 data·daily 字面量行锚定与连续形禁/零网令牌[剥 docstring]/P3 族五模块零网络 import)。

## §二 E-AC-02 验收要点逐条证据映射表(要点①②③=本地断言面;④=CI 面)

| 要点 | 断言/证据(file:line 锚 tests/test_p3_wp_e.py 终态) |
|---|---|
| ①零主动采集断言(全仓无用户数据拉取路径) | TestZeroActiveCollection 5 用例: 禁目录扫描/进程调用(L698)+import 白名单恰等(L707)+零监视零网令牌·剥 docstring(L716)+**P3 族五模块零网络 import**(research_index/evidence_linkage/prediction_review/report_quality_review/personal_flow_integration,L734;P-E-09 P3 层断言)+模块级路径类常量封闭集(L755);零主动采集结构性面=一切输入显式传入(签名零默认数据路径,TestStaticPurity sys.path.insert 恰 1+无数据根常量) |
| ②个人观察不冒充程序验证证据(来源等级隔离) | TestSourceLevelIsolation 8 用例(L644-691): 三面哨兵 pass(L645)+v2 词表外+键集不交+字段锚+词表破坏 monkeypatch 检出(L663)+键集破坏 monkeypatch 检出+渲染标签在场零 ★(L677)+标签弱化检出;接口(b) 签名无 source_level 参数(TestNoteInterface L459-510 TypeError 用例)+手造错值拒;G2 黄金渲染面含隔离标签 |
| ③用户数据零落 LIVE 断言 | TestPathGuards 12 用例(L774-871): LIVE 根读写导出三面拒(L808 起)+user_root 指 LIVE 拒+~/ 形 expanduser 后拒(L835)+写入域外拒(DEV 仓锚词面)+DEV_ROOT 内允许(monkeypatch)+相邻性正例;守卫代码面=组件化四元组源码零连续字面量(TestStaticPurity 行锚定+连续形禁) |
| ④CI 零回归 | 本地 CI 镜像 87 件=86 exit0+1 SKIP(test_glm_live)+0 非零 [实取·终态记录](基线 86 槽零回归+本包恰 +1);**分支 run NOT VERIFIED@执行席**→操作者 CHECKPOINT dispatch `rounds/042/P3-WP-E-CI-dispatch-evidence.md`(登记文件为操作者面,执行席不创建);附: 导出面零回读(L1125)/零改写 API 面(L1144)AST 断言=登记面补齐件 |

## §三 如实偏差登记(全项;不声明「无偏差」)

1. **模块-登记对齐·open 'a' 内联化**(实现笔提交前): 实现首稿以共享 helper 承载追加使 open("a") 计 1 处,P-E-16 登记「'a' 恰 2 处」→提交前对齐为标注档/笔记档两处内联(登记语义零变更;对齐发生于实现笔 04e30fc 提交前,非登记后回改);
2. **模块-登记对齐·零 datetime 纯日历化**(实现笔提交前): P-E-03 登记文词面「十位带杠形才入 fromisoformat」与 P-E-16「import 白名单={json,os,sys}」存在内在张力(fromisoformat 需 datetime)→实现取白名单优先: 纯字符串+月长表+闰年规则判定;十位带杠 ASCII 数字形行为与 fromisoformat 逐值等价(年界≥1/月界/闰年含世纪规则),且零 fromisoformat 3.11 宽形接受面(紧凑形/周形在 3.11 被其接受,本实现结构性拒绝)——跨版本一致性由构造保证;
3. **测试字面量自纠 3 项**(实现笔首跑 3 红对账,全为期望侧口径归位非模块缺陷): ①尾随内容容差用例归位 R040 截断语义组(首十位规范即收=家族先例登记口径,原误置于拒绝组)②渲染隔离断言归位「零 ★+标签在场」(「不参与星级与门禁」本身即隔离声明词面,原误删「星级」字样)③模块级路径类常量封闭集归位含双守卫组件组(原误仅 _DEV_ROOT);
4. **测试补齐笔**(1b50fc3): 实现笔遗漏 P-E-09(P3 族五模块零网络 import)/P-E-08(write_export_document 零读取面 AST)/P-E-04(零改写类 API dir 扫描)/P-E-17(selfcheck 零写入)四登记面测试→补齐笔纯追加 3 用例+1 断言(126→129);白名单 k=4 不变/M=0 不变;提交链含补齐笔与勘误笔(见 5),较家族 5 笔先例多 2 笔(如实登记);
5. **补齐笔提交信息行数误记**: 提交信息称「1297 行」,实取 1301 行(wc -l;51 insertions-1 deletion 自证 1251+50=1301)——sha 与用例数无误,行数以本登记与 `git show` 终笔复核为准;**勘误笔×2**(报告笔内两处误记的零 amend 独立纠偏: ①GOLDEN_SHAS 行锚 L110-127→实锚 L90-107;②本 §三/§五 提交链计数: 报告笔原计 6 笔[未计勘误]→实 8 笔[登记→实现→测试补齐→报告→勘误①→勘误②→DELIVERY→定值],报告笔时点未预见自身后续勘误,如实登记);
6. **subprocess 受控 1 处**: TestSelfcheckMain(selfcheck 子进程,超时 60s/PYTHON* 环境变量剥离/运行目录沙箱零写入断言);
7. **CI 分支 run NOT VERIFIED@执行席**: 分支 run 属操作者 dispatch 面(与 WP-D AC-02④ 同款),本地镜像=方法学等价面如实呈报,不冒充分支 run;
8. **行号容差承接**: 冻结章 §十一 注记行号与本包基线工作树实读偏差 0 行(≤3 行容差内;§零.1 登记)。

## §四 DP 零回改自检表

| DP | 自检 |
|---|---|
| DP-9(确认型,用户实批) | 活性定值=登记定值: `annotation+note_reference+export@user_approved_2026-11-08_immediate`(registered_dp_values 对照+测试字面量+dp_selfcheck 哨兵三方一致;monkeypatch 回改三面[schema/interface_set/source_level]AssertionError 检出实证,负向敏感性定值回改注入 9 红);三接口集完整性断言(len==3+恰等三元组) |
| DP-1/2/3(上游登记型) | 零引用零改写: E 面无检索/版本链/O-1..O-4 消费面(TestStaticPurity import 白名单恰等=research_index/evidence_linkage 零 import) |
| DP-5/6(上游登记型) | 经 WP-D 编排产物**间接原样承载零重算零改写**: 接口(c) error_pattern_statistics=prd 统计 passthrough(引用同一性测试断言;渲染面计数行词面标注「DP-6 上游登记口径」);零重开窗/零分母改写 |
| DP-7(上游登记型) | WP-D 质量文档/简报/建议清单原样承载(briefing/suggestions 引用同一性;schema 锚=rqr.STATS_SCHEMA_VERSION 复用调用禁复制分叉);零改写零注入 |
| DP-4/8/10(确认型,他包面) | 零触及: 导出建议清单 requires_user_confirmation=true 标记随上游原样携带(渲染计数行明示「DP-8…本导出零注入」);零 GLM/零提示词注入/零终验窗 |

## §五 git 纪律七项自检(BASE-P3E `91612378…` 后纯线性 8 笔)

1. 切支: `git checkout -b dev/p3-impl-e 91612378…` 自基线全值切出(§零.7 步骤3)✓;2. 提交链纯线性零 merge: 登记 bcd363d→实现 04e30fc→测试补齐 1b50fc3→报告笔 9bc2200→勘误① 1972970→勘误②(本笔)→DELIVERY 笔→定值笔(每笔单父;`git log --merges 91612378..HEAD`=空,证据包 03 类)✓;3. 零 amend/零 force(全程未使用)✓;4. main 未触碰(仅读: ls-remote 取证)✓;5. LIVE 路径与 launchd/LaunchAgents 零触碰(模块结构性拒写+证据包 03 类三面[grep 零命中+real_data_acceptance sha 等值+LaunchAgents 清单哈希])✓;6. 零 tag ✓;7. 零网络(取证推送类除外;终局单支推送 dev/p3-impl-e no-force)✓;白名单 diff 面: BASE..终笔 `git diff --name-status`=恰 A=4 零 M 零 D(证据包 03 类)✓。

## §六 数值标注自检清单(§5.3 六项扫描;REPORT+DELIVERY 双件)

- 实取类(来源逐项): 129 用例/18 类 [实取·unittest verbose stdout]/721 行+1301 行 [实取·wc -l]/双 sha256 [实取·hashlib]/黄金六 sha [实取·首原理件+交叉裁定双源]/CI 镜像 87=86+1 SKIP+0 非零 [实取·镜像脚本终态记录]/负向敏感性 9/2/4 红→复绿→sha 零残留 [实取·注入记录]/evidence 包计数与 zip 定值 [实取·装配时点,DELIVERY §六 终笔定值]/ls-remote 分支值与哈希 [实取·git 取证];
- 合成手推定值类(黄金字面量,非实取统计): fixture 记录 4 条(标注 2+笔记 2)+合成 WP-D 编排面输出 1 件(建议清单 2 条/hit=2·miss=1·inconclusive=1·not_yet_triggered 终态=1/hit_rate=2÷3=0.6667)/黄金六面字节数(640/579/428/386/1235/1030);
- 示意类: 无(本文无数值属示意)。
