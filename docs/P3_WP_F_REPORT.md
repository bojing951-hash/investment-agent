# IA-P3-WP-F REPORT — P3 收尾层第 6 实现包/族末包(P3 终验+项目总封版)

> 包: IA-P3-WP-F(P3 族第 6 实现包/族末包,#38 挂靠;依赖列前件=WP-P3-A~E 全部关闭+横切验收窗口+用户实批) · 执行Agent: Agent 3 · 分支: `dev/p3-impl-f`
> 基线: BASE-P3F=`98f1a95d0c7345bf1c71b05766f78c394fa78618`(origin/main,开工 ls-remote 实取全值一致)
> 合同: IA-P3-WP-F-AC-v1.0(冻结,附录A 内嵌注入)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;引用 DESIGN/INVENTORY/上游在场件行号一律为**本包基线工作树实读**行号(2026-11-08T05:2xZ 起实取,基线=BASE-P3F 工作树);提示词注入内容引用一律标注「注入摘要,非工作树实读」。
> 数值标注边界: 本文所有计数类/统计类数值逐个二选一标注 `[实取·来源: …]` 或 `[示意·非实取]`;日期/SHA/结构编号(WP-P3-F/#31-38/FA-S* 等)/档键成分(ID 格式字符串)按合同边界出圈登记。

---

## §零 规格抄录与交付面登记(开工首步,AC-01;登记后即本合同白名单实体)

### §零.1 DESIGN §7 WP-P3-F 行四要素逐字抄录

实读 `docs/P3_DESIGN.md`(基线工作树在场,blob `5acc130a88d9635a1e82d7ad3beb4f1dbe008106`,§零.7 核验与 7f43724 侧等值),WP-P3-F 行位于 L200-L208,逐字抄录:

```text
L200: **WP-P3-F P3 终验 + 项目总封版**(挂靠编号: **#38**;**单列一包**)**PENDING·用户实批前置**(LIVE 部署与观察窗起算属用户保留卡点 [实取·注入摘要·handover §4a 用户三个保留卡点(2026-11-03),非工作树实读])
L201: - 目标: P3 全包终验 + 项目级总封版判定。
L202: - 范围: 终验清单执行(七 AC 复演式终验/层序关闭核对/各层交付件归档索引)+ 总封版判定材料汇编;**含横切运行时验收登记**(不预执行,登记如下)。
L203: - 依赖: WP-P3-A~E 全部关闭;横切验收窗口(见下);用户实批(LIVE 相关事项)。
L204: - 验收要点草案(横切运行时验收登记,两项 [实取·注入摘要·handover §4a 横切块逐字(2026-11-03),非工作树实读]):
L205:   - ①≥7 个真实计划执行日 + ≥1 次真实周报回归(原始 P0 要求)[实取·注入摘要·handover §4a 横切块逐字(2026-11-03),非工作树实读];
L206:   - ②30 天生产观察 + 计划任务成功率≥95% + ≥4 次正式周报;**日历时间不可压缩: LIVE 部署后尽早起算,与后续层开发并行计时** [实取·注入摘要·handover §4a 横切块逐字(2026-11-03),非工作树实读];
L207:   - ③执行载体 = R018 停泊件(注入摘要级对接,本包零预执行);
L208:   - ④终验清单与计时起点**先登记后运行、禁回改**(登记型,负向测试: 终验开始后回改清单被拒);⑤总封版判定材料如实汇编(FAIL 项如实留档,不美化)。
```

四要素齐备(目标 L201/范围 L202/依赖 L203/验收要点草案 L204-208,要点 5 条 ①-⑤),无缺失。核验:
- **F 行可区分性**: 与 A/B/C/D/E 行四要素逐项可区分(A=档案检索与结论版本管理 L170-174/B=新证据关联与持续跟踪聚合 L176-180/C=预测复盘与错误模式统计 L182-186/D=报告质量评价循环 L188-192/E=个人流程整合接口 L194-198[同族前列件行];F 行题名「P3 终验 + 项目总封版」与挂靠 #38 单列、「终验清单执行+总封版判定材料汇编+横切运行时验收登记(不预执行)」范围要素、七 AC 复演/层序关闭/归档索引/计时禁回改/判定材料如实汇编要点均为他行所无,族内唯一)→ 合同附录A §零(iv)冲突处置首项不触发;冻结章 §十一 F 行定位登记 L200-208 与本实读一致(偏差 0 行,≤3 行容差内);
- **依赖列核验**: 「WP-P3-A~E 全部关闭」=同族前列包全部独立审计 PASS 已合入 main(冻结章 §十一 生效前置达成登记: A=R038+R067 merge b3628fd tip 202a09d2/B=R039+R068 merge c14931c tip e21789a/C=R040+整改续段 merge aeb39e8 tip 57eb3a3/D=R041 merge 91612378 tip f349b83/E=R042 merge 98f1a95=本 BASE tip f74a126,注入摘要,非工作树实读),其交付件在本基线工作树在场(A~E 各 k=4,§零.6 实读登记);「横切验收窗口」=进行中(LIVE 2026-11-05 部署,观察钟 2026-11-05→2026-12-05,冻结时第 3/30 天;DESIGN L202 明文「不预执行,登记如下」=窗口项以登记面承接,不阻断本包,注入摘要,非工作树实读);「用户实批(LIVE 相关事项)」=已取得(下条);「层序前置」=§7 L168 层序排程依赖声明(冻结章 §十一 登记逐层核验 ✓,注入摘要,非工作树实读);依赖列与 BASE-P3F(`98f1a95…`)无矛盾、**不要求并入其他支**(本包无并入步,纯线性)✓;
- **末包执行发车硬门核验(合同 §0 联动保险)**: 冻结章 §十一 判定「是」(#38 横切/终验+用户确认面)且已附实批落档证据(用户 2026-11-08 13:0x HKT 于 R042 收口呈报问答实批「现在就发 F」,PENDING-APPROVALS.md 批复行,冻结章 §十一 凭证,注入摘要,非工作树实读;用户已知悉并采纳: 30 天观察项冻结时仅 3/30 天=如实 NOT VERIFIED 登记,2026-12-05 观察钟满后走补证轮收口)→ **硬门满足,开工合法**;执行Agent 零自决零代批,以注入冻结章凭证为准;
- **范围列无真实 GLM 调用/网络出站/付费凭证要求**: 范围列 L202 零 GLM/网络/凭证/付费字样;三件(终验清单执行/总封版判定材料汇编/横切运行时验收登记)均为确定性结构+登记面;「不预执行」明文承接(L202)——运行时验收两项(①②)属 R018 停泊件载体+补证轮面,本包零预执行零真实执行;无情形(d)停止条件。

### §零.2 交付文件清单(k=4 [实取·本节清点],登记后即本合同白名单实体)

| # | 文件 | DESIGN/合同依据(推导逐条附) |
|---|---|---|
| 1 | `scripts/project_final_seal.py` | DESIGN L202 范围列三件(终验清单执行[七 AC 复演式终验/层序关闭核对/各层交付件归档索引]+总封版判定材料汇编+横切运行时验收登记[不预执行])=**恰 1 个代码模块**: WP 题名「P3 终验 + 项目总封版」(L200)单一工作包,三件共享同一终验清单载体(L204-208 要点①-⑤全部锚在清单/计时/判定三面)、同一登记纪律(L208④ 先登记后运行禁回改+§8.5 L220「终验清单只追加」红线)与同一 DP-10 参数面(L203 依赖列单点+L239)+合同附录A §零(ii)固定推导规则「每个代码模块=scripts/ 下恰 1 文件」;文件名=域词 project(项目)+final(终)+seal(封版,WP 行题名「项目总封版」用词),避开既有全部 scripts/ 文件(ls scripts/ 实读;开工 grep -ri "final_seal\|project_final_seal" scripts/ tests/ docs/=0 命中 [实取·开工 grep,2026-11-08T05:2xZ];既有近名件 `scripts/p03_final_acceptance_run.py` 为 P0-3 层终验运行件,前缀/域不同不冲突) |
| 2 | `tests/test_p3_wp_f.py` | DESIGN L204-208 工件「负向测试: 终验开始后回改清单被拒」(L208④)等断言面+合同附录A §零(ii)「含代码则必含 tests/test_p3_wp_f.py」 |
| 3 | `docs/P3_WP_F_REPORT.md` | 合同附录A §零(ii)必含件(本文件) |
| 4 | `docs/P3_WP_F_DELIVERY.md` | 合同附录A §零(ii)必含件;DESIGN L208⑤「判定材料如实汇编」证据落点=DELIVERY |

### §零.3 结构约束核验(2026-11-08T05:2xZ 实取)

- 与 `git ls-files` 零重合: 4 路径 `git ls-files scripts/project_final_seal.py tests/test_p3_wp_f.py docs/P3_WP_F_REPORT.md docs/P3_WP_F_DELIVERY.md` 输出=0 行 [实取·开工 git ls-files](REPORT 本件于登记笔先行入库,登记时点其余 3 件零重合;本件=清单内必含件,登记笔提交即白名单实体)→ 纯新增 ✓;
- 必含 DELIVERY ✓;含 .py 实现文件 → 必含对应 tests(tests/test_p3_wp_f.py)✓;
- 推导无越界: 范围列恰 1 个代码模块(§零.2 行 1 依据,同族前列件 WP-A/WP-B/WP-C/WP-D/WP-E 单模块先例同构)→ scripts/ 恰 1 文件;未引入 DESIGN 依据外文件 ✓。

### §零.4 DP 登记(开工首步登记定值;DESIGN 决策点登记表 L226-L241 实读,DP 共 10 个 [实取·表清点 L241],F 行内所引=DP-10[LIVE 类·确认权留用户+登记型,L239];L200/L203 明文 PENDING·用户实批前置=DP-10 确认面)

| DP | 分类(DESIGN 实读) | 本包登记定值(登记即实现值,先登记后运行,禁回改) | 依据 |
|---|---|---|---|
| DP-10 终验观察窗起算与计时载体 | LIVE 类·确认权留用户+登记型(L239;F 行 L200 明文「PENDING·用户实批前置(LIVE 部署与观察窗起算属用户保留卡点)」+依赖列 L203「用户实批(LIVE 相关事项)」) | **确认面已由用户行使,本包据此实现,非执行Agent自决**: 用户 2026-11-08 实批「现在就发 F」(冻结章 §十一 硬门实批落档,PENDING-APPROVALS.md 批复行@engine 侧执行席不可达如实声明,注入摘要,非工作树实读;用户保留事后否决权),且已知悉并采纳「30 天观察项冻结时仅 3/30 天=如实 NOT VERIFIED 登记,2026-12-05 观察钟满后走补证轮收口」——该知悉即对起算点 (a) 与补证轮处置的确认。**登记面定值(选项 (a)+(i),=DESIGN L239 推荐列)**: 起算=LIVE 部署日 `2026-11-05`(选项 a);载体=R018 停泊件(选项 i,注入摘要级对接,本包零预执行);观察窗 30 天(DESIGN L206 逐字)→终点 `2026-12-05`(=起算+30 天,纯日历推导);补证轮=观察钟满后(2026-12-05 后)收口。模块登记承载: `DP10_*` 常量组+`RT_*` 阈值组(P-F-02/P-F-04/P-F-05) | L239+L200+L203+L206+冻结章 §十一 |
| DP-1/DP-2/DP-3 | 登记型(L230-232) | **上游 WP-P3-A 已登记定值**(旁路索引文件/O-1~O-4 全 4 类/记录级粒度;本包零消费零改写——F 面无检索/版本链逻辑面;上游交付件仅作归档索引**文件级**在场核验对象,零逻辑复制;WP-A REPORT §零.4 登记在案) | L230-232 |
| DP-5/DP-6 | 登记型(L234-235) | **上游 WP-P3-C 已登记定值**(四轴×滚动 12 个月/inconclusive·not_yet_triggered 不入分母单列;本包零消费零改写——F 面无统计逻辑面;WP-C REPORT §零.4 登记在案) | L234-235 |
| DP-7 | 登记型(L236) | **上游 WP-P3-D 已登记定值**(维度 5 项全启+阈值首期;本包零消费零改写;WP-D REPORT §零.4 登记在案) | L236 |
| DP-4/DP-8/DP-9 | 确认权留用户(L233/L237/L238) | **本包零触及**: DP-4=§4.1 关联第三层(WP-P3-B 面)、DP-8=§6.1 提示词注入(WP-P3-D 面)、DP-9=接口形态与启用时点(WP-P3-E 面,用户 2026-11-08 已实批由 E 包承接)——均非 F 行范围列(L202)所及,本包无 GLM/注入/个人流程面 | L233/L237/L238 |

DP 编号/数量/分类与 DESIGN 实读一致: 行内所引 DP-10(L200/L203 明文)双性(LIVE 类确认+登记),其确认面**已由用户本人行使**(2026-11-08 实批+知悉采纳,冻结章凭证,非本包自决实施——合同 AC-02 判据 6「确认型 DP 未被自决实施」=执行Agent 零自决,凭证在案),登记面按 (a)+(i) 定值先行登记;其余 DP(登记型 DP-1/2/3/5/6/7=上游登记面零消费零改写;确认型 DP-4/8/9=零触及)分类与 DESIGN L230-L239 表逐行一致。

### §零.5 实现参数登记(P-F-01..P-F-21,先登记后实现,运行后禁回改)

| # | 参数 | 登记定值 | 依据 |
|---|---|---|---|
| P-F-01 | 模块载体 | `scripts/project_final_seal.py` 恰 1 文件(终验清单执行+总封版判定材料汇编+横切运行时验收登记三组件同模块,§零.2 行 1) | DESIGN L202+§零.2 |
| P-F-02 | DP-10 定值承载 | `DP10_CLASSIFICATION`(L239 词面)+`DP10_USER_APPROVAL="user_approved_2026-11-08_now_dispatch_F"`(用户实批时点标记,凭证=冻结章 §十一,注入摘要非工作树实读)+`DP10_CARRIER="R018_parked_artifact"`+`DP10_CARRIER_INTERFACE_LEVEL="注入摘要级对接"`+`DP10_ZERO_PREEXECUTION=True`;运行期哨兵 dp_selfcheck 对照(回改任一→AssertionError) | DP-10+§零.4+L207 |
| P-F-03 | 终验清单结构 | 清单项 24 项 [实取·本行清点]=六段: S1 七 AC 复演式终验 7 项(FA-S1-AC-01..07,题面=本合同 §一..§七 AC 题)/S2 层序关闭核对 11 项(FA-S2-01..11,层行=L0-gov/L1-p02/L1w3-dataw3/L2a-e2ea/L2fa-p03fa/L2b-e2eb/L3-glm/L4-p1/L5-p2/L6-p3ae/L6-p3f)/S3 各层交付件归档索引 1 项(FA-S3-01)/S4 横切运行时验收登记 3 项(FA-S4-01=①/FA-S4-02=②/FA-S4-03=③)/S5 清单纪律 1 项(FA-S5-01=④)/S6 总封版判定 1 项(FA-S6-01=⑤);项字段封闭集 `{item_id, section, title, requirement, kind, design_anchor}`;kind 枚举 7 值 `{SEVEN_AC_INPUT, LAYER_CLOSURE, ARCHIVE_INDEX, RUNTIME_WINDOW, RUNTIME_CARRIER, DISCIPLINE, DETERMINATION}`;verdict 值域 `{PASS, FAIL, NOT_VERIFIED}` | DESIGN L202+L204-208 |
| P-F-04 | 计时基线与观察窗 | 起算=`2026-11-05`(LIVE 部署日,DP-10 选项 a)/观察窗=30 天(DESIGN L206 逐字)/终点=`2026-12-05`(=起算+30 天纯日历推导)/补证轮登记=`SUPPLEMENTARY_ROUND_AFTER="2026-12-05"`(观察钟满后收口,用户知悉采纳,冻结章 §十一);elapsed 计算面=纯日历函数(P-F-15),零 datetime | DP-10+L206+§零.4 |
| P-F-05 | 运行时验收阈值(DESIGN L205-206 逐字数值) | `RT_MIN_SCHEDULED_EXECUTION_DAYS=7`(①≥7 个真实计划执行日)/`RT_MIN_WEEKLY_REGRESSIONS=1`(①≥1 次真实周报回归)/`RT_MIN_OBSERVATION_DAYS=30`(②30 天生产观察)/`RT_MIN_TASK_SUCCESS_RATE_PCT=95`(②计划任务成功率≥95%)/`RT_MIN_FORMAL_WEEKLY_REPORTS=4`(②≥4 次正式周报);仅登记承载于清单项 requirement 与材料汇编,**零执行面**(P-F-06) | DESIGN L205-206 逐字 |
| P-F-06 | 零预执行纪律(要点③) | ①②运行时验收=登记面 only: 模块零运行时执行面(无任何执行/采集/统计真实运行时数据的函数面;结构由 AST+词面测试锁定),FA-S4-01/02 verdict 恒 `NOT_VERIFIED`(附 elapsed 天数与补证轮注记,不因窗口满而自判 PASS——证据汇编属 R018 载体/补证轮面);FA-S4-03(③载体登记)verdict=`PASS`(载体=R018 停泊件+注入摘要级对接+零预执行,登记纪律本身成立) | DESIGN L202「不预执行」+L207 |
| P-F-07 | 状态日志形态 | JSONL append-only(`open(path,"a")` 纯字节追加,零改写既有行;坏行/非 dict 行→ValueError fail-loud);路径=运行编排自变量(真实运行默认 `data/research/p3_final_seal/acceptance_journal.jsonl`,P-F-20;测试全落临时沙箱);记录类型封闭集 `{baseline, started, compiled}`(record_type 外值→ValueError);状态机=baseline(恰 1)→started(恰 1)→compiled(恰 1),重复任一→ValueError,越级→ValueError;journal_schema_version=1 | DESIGN L208④+§8.5 L220「终验清单只追加」 |
| P-F-08 | 禁回改执行器(要点④) | digest 链: `fa_digest()`=sha256(canonical_json([registered_checklist(), registered_timing()]))(canonical=sort_keys+ensure_ascii=False+separators 紧凑形);baseline 记录登记时 digest→start 时复核等值(不符→ValueError「清单/计时与登记基线不符(禁回改)」)→compile 时再复核;`propose_checklist_amendment(state_path, note)` 恒拒: 未登记→ValueError「未登记,无清单可改」/已登记未开始→ValueError「已登记禁回改(先登记后运行纪律)」/已开始→ValueError「终验开始后回改清单被拒(DESIGN L208④)」——L208④ 负向测试锚面;常量直改攻击面=monkeypatch 改 CHECKLIST/计时常量后 start/compile digest 失配→拒(测试面) | DESIGN L208④+§8.5 L220 |
| P-F-09 | 层序关闭登记表 | 11 行(=P-F-03 S2 层行): 每行 `{layer_id, title, closure_provenance}`;closure_provenance: L0-gov/L1-p02/L1w3/L2a/L2fa/L2b/L3/L4/L5=「冻结章 §十一 层序闭合逐层核验 ✓(注入摘要,非工作树实读)」+在场归档注记(L1-p02 另注 P0_2_W5_SEALING 封版件在场;L3-glm 另注 G4 凭证面=PENDING 用户实批面本包零触及);L6-p3ae=逐包轮次+merge+tip(A=R038+R067/b3628fd/202a09d2,B=R039+R068/c14931c/e21789a,C=R040+整改续段/aeb39e8/57eb3a3,D=R041/91612378/f349b83,E=R042/98f1a95/f74a126;冻结章 §十一,注入摘要);L6-p3f=「本包执行席交付+自评,独立审计 R043 待→NOT_VERIFIED@执行席」 | DESIGN L202「层序关闭核对」+L203+冻结章 §十一 |
| P-F-10 | 归档索引构建规则 | 索引=仓库内版本化登记常量(冻结登记,禁随新增文件漂移;机械转储自基线工作树 `/tmp/p3-wp-f/gen_archive_table.py` 生成件 [实取·2026-11-08T05:3xZ,证据包 06 类],归属规则=文件名前缀分层): 计 **154 件** [实取·生成件 TOTAL]=docs/ 全档 144 件 [实取·`ls docs/ \| wc -l`=144] 分层 L0-gov 21/L1-p02 45/L1w3-dataw3 2/L2a-e2ea 2/L2fa-p03fa 2/L2b-e2eb 13/L3-glm 12/L4-p1 23/L5-p2 11/L6-p3 13+P3 族代码/测试交付件 10 件(A~E 各 module+tests,上游各包 REPORT §零.2 登记清单对照同源,§零.6)归 L6-p3;**F 自豁免 4 件**=`SELF_EXCLUDED_PATHS={scripts/project_final_seal.py, tests/test_p3_wp_f.py, docs/P3_WP_F_REPORT.md, docs/P3_WP_F_DELIVERY.md}`(自指环豁免,沿 R019-D3 SHA256SUMS 自豁免先例精神: 本包自身交付件不入本包归档完整性核验面,其交付由 diff/CI/审计承载);索引零 data/daily 路径、零 LIVE 路径(selfcheck 断言) | DESIGN L202「各层交付件归档索引」+AC-05.5 |
| P-F-11 | 归档核验 | `verify_archive_index(repo_root, index=None)`(None=登记索引): 逐件 `os.path.isfile` 在场核验+sha256 指纹(`hashlib`,读 "rb");缺席→该层 files_missing 记录+对应 S2/S3 项 FAIL(如实,不美化);每层 digest=sha256(canonical_json({path: sha256,…}))+总 digest;测试面以合成 mini 索引为唯一数据源(真实档零依赖) | DESIGN L202+AC-03.3 |
| P-F-12 | 七 AC 复演输入契约 | S1 项 verdict=运行输入(非模块自算——避免自证): 输入表=REPORT §四 逐 AC 自评表登记值(执行席自评,独立审计待 R043);结构校验: dict 恰键 `AC-01..AC-07`,每值 `{verdict ∈ {PASS,FAIL,NOT_VERIFIED}, evidence 非空 str, note str}`,违式→ValueError;材料汇编逐字承载输入行+provenance 标注「REPORT §四 登记值(执行席自评,独立审计待 R043)」 | DESIGN L202「七 AC 复演式终验」 |
| P-F-13 | 总封版判定规则 | `determine(verdicts)`: 任一 FAIL→`NOT_SEALED`;否则任一 NOT_VERIFIED→`PENDING_SUPPLEMENTARY_EVIDENCE`;否则→`SEALED`;规则随材料汇编逐字登记(determination_rule 字段);真实运行预期=PENDING_SUPPLEMENTARY_EVIDENCE(观察窗 3/30+审计待 R043+CI 登记面,如实不美化——用户知悉采纳的处置,冻结章 §十一) | DESIGN L208⑤ |
| P-F-14 | 判定材料 schema 与渲染 | 文档键封闭集 `{schema_version, as_of, fa_digest, timing_baseline, runtime_window, seven_ac_reverification, checklist_verdicts, layer_closure, archive_index, fail_items, determination, determination_rule, disclaimer, provenance_notes}`(SEAL_DOC_SCHEMA_VERSION=1);确定性序列化=`json.dumps(sort_keys=True, ensure_ascii=False, indent=1)`(家族先例 P-A-03/P-C-08/P-D-13/P-E-13 同款);渲染 `render_seal_determination(doc)` 纯文本=标题/计时基线/判定结论/七 AC 复演表/S2 层序表/S3 索引摘要(逐层件数+digest)/S4 运行时登记(elapsed 天数+补证轮)/FAIL 项如实区(空则「无 FAIL 项」)/免责尾行;免责词面=「本判定材料为项目工程收尾状态如实汇编,不构成投资建议(禁交易/禁仓位/禁收益承诺);FAIL/NOT_VERIFIED 项如实留档,不美化」(§8.3 L218 红线承接+`scripts/macro_scorecard.py` L32-33 先例) | DESIGN L208⑤+§8.3 L218 |
| P-F-15 | 日历纯函数(零 datetime) | `parse_ymd`(严格十位带杠形 YYYY-MM-DD,月 1-12/日 1-月长,闰年规则=(y%4==0 and y%100!=0) or y%400==0,紧凑形/周形拒绝)+月长表 `_MONTH_LENGTHS`+`ymd_to_ordinal`/`ordinal_to_ymd`+`add_days`+`days_between`;selfcheck 断言 `add_days("2026-11-05",30)=="2026-12-05"`;零 `import datetime`(3.9/3.11 行为一致由构造保证,WP-E 同款纪律) | P-F-04+家族先例 |
| P-F-16 | 路径守卫 | `_reject_live_path`(expanduser+normpath 后组件序列含 LIVE 根四组件序列即拒,组件化 `_LIVE_ROOT_GUARD=("AI内容","🤖_AI投资项目","每周宏观追踪","investment-agent")`,**源码零连续 LIVE 路径字面量**)+`_reject_raw_data_path`(组件序列含 `("data","daily")` 相邻即拒)——适用**全部读写面**(状态日志/材料写入/七 AC 输入读取/归档件读取);fail-loud ValueError | AC-07.1+WP-E P-E-10/P-E-11 先例 |
| P-F-17 | 纯度 | import 白名单={json, os, sys, hashlib}(纯标准库,零项目内依赖[本包无上游逻辑复用面,P-F-18]+零第三方);AST 零网络 import(urllib/requests/http/socket/httpx 禁)、零 subprocess、零 datetime;open 恰 3 helper 各 1 处(`_read_bytes` "rb"/`_append_journal_line` "a"/`_write_text_once` "w"),AST 测试面;零凭证/密钥/token;Python 3.9 兼容语法(本地 3.9.6/CI 3.11) | AC-05.4+AC-03 |
| P-F-18 | 上游复用面(对齐=复用调用,禁复制分叉) | 本包零上游模块 import(F 面与 A~E 域不同构,无逻辑复用点);上游在场交付件仅作**文件级**归档核验对象(P-F-10 索引,对照同源=各包工作树在场 REPORT §零.2 登记清单);零上游逻辑复制(索引=路径登记非逻辑);主流水线/config/workflow 零触碰 | AC-05.5+合同§八.3 |
| P-F-19 | 哨兵与入口 | `registered_dp_values()`+`registered_param_values()`(活性常量)+`dp_selfcheck()`(活性常量 vs 模块内登记镜像逐值对照+结构断言: DP-10 日期算术/阈值五值/清单 24 项六段计数 7-11-1-3-1-1/item_id 唯一/层注册表 11 行=索引层集+L6-p3f/索引零 data/daily 与 LIVE 路径/自豁免恰 4 件/记录类型封闭集;回改任一定值→AssertionError);`__main__` 双入口: 缺省/selfcheck=零写入只打印;`run`=显式编排入口(--repo-root/--as-of/--seven-ac-file/[--state-path/--out-dir],用法错 exit2/纪律违例 exit1/成功 exit0) | DP 纪律+WP-A..E 先例+P-F-20 |
| P-F-20 | 运行产物面 | 真实运行(编排入口)=终验清单执行+判定材料汇编的交付运行面: 产物落 `data/research/p3_final_seal/`(自有子目录,不 commit 不入 diff,.gitignore L1 `data/` 结构性保障): `acceptance_journal.jsonl`+`seven_ac_selfcheck_input.json`(运行输入=REPORT §四 表 echo)+`seal_determination.json`+`seal_determination.md`;模块对 data/research 其余既有档案零读取零写入(边界=自有子目录);`data/daily/` 只读锚定(运行前后 sha256 清单对照);运行 stdout/stderr 全文+退出码入证据包 | 合同§零 运行产物边界+DESIGN L202 |
| P-F-21 | 他包范围排除 | WP-P3-A/B/C/D/E 零改零复制(上游件只读);研究主流水线/config/metric_registry.json/workflow 零触碰;W4/W5 侧边验收工具零接入(AC-07.6);论点/观点/预测状态档零写入(AC-07.5);LIVE/launchd 零触碰;零 tag;研究档案不 commit | 合同§八.1/.3/.4/.6/.7 |

### §零.6 前置实读登记(file:line;基线工作树 2026-11-08T05:23-05:4xZ 实取)

- DESIGN 相关节(工作树在场件,=7f43724 侧 blob 等值,§零.7): §1 P3 定位与不预执行边界 L15-24(L24「不预执行 #38 终验或横切运行时验收…R018 停泊件,注入摘要级对接」)/§7 层序声明 L168+包拆解 L166-210(A L170-174/B L176-180/C L182-186/D L188-192/E L194-198[同族前列件行,区分对照+上游在场件引用面]/**F L200-208 本包规格**/包清点核对行 L210)/§8 红线 L214-222(快照纪律 L216/LIVE 禁写 L217/禁建议 L218/批量修改 L219/**append-only L220[「版本记录/关联记录/标注档/终验清单只追加」——终验清单在列,④纪律红线锚]**/GLM 凭证 L221/如实 L222)/决策点登记表 L226-241(**DP-10 L239**;DP-1/2/3 L230-232/DP-4 L233/DP-5/6 L234-235/DP-7 L236/DP-8 L237/DP-9 L238);
- INVENTORY(`docs/P3_INVENTORY.md`): e.4 横切运行时验收两项逐字 L147(≥7 执行日+≥1 周报回归;30 天观察+成功率≥95%+≥4 正式周报;R018 载体——P-F-05 阈值源)/e.3 层序规则 L146/面(d) 停泊实现面清单 L132-136/a.4 表述纪律先例 L59(`scripts/macro_scorecard.py` L32-33 免责——P-F-14 免责词面先例)/c.2 数据面现行形态 L115-122(data/daily 18 件@盘点时点;快照长期积累于 LIVE 侧,DEV 禁写);
- 上游在场件(只读禁改;REPORT §零.2 登记清单对照同源,各 k=4 [实取·各件 L30-37 逐件实读]): WP-A(`scripts/research_index.py`+`tests/test_p3_wp_a.py`+`docs/P3_WP_A_REPORT.md`+`docs/P3_WP_A_DELIVERY.md`)/WP-B(`scripts/evidence_linkage.py`+`tests/test_p3_wp_b.py`+REPORT+DELIVERY)/WP-C(`scripts/prediction_review.py`+`tests/test_p3_wp_c.py`+REPORT+DELIVERY)/WP-D(`scripts/report_quality_review.py`+`tests/test_p3_wp_d.py`+REPORT+DELIVERY)/WP-E(`scripts/personal_flow_integration.py`+`tests/test_p3_wp_e.py`+`docs/P3_WP_E_REPORT.md`+`docs/P3_WP_E_DELIVERY.md`)——五包 module+tests 共 10 件=归档索引 L6-p3 代码件来源(P-F-10);
- 同族前列件 REPORT 结构先例: `docs/P3_WP_E_REPORT.md` §零.1-§零.9/§一-§六(登记制 REPORT 结构)+`docs/P3_WP_E_DELIVERY.md` §一-§七(zip 定值/双源副本/漂移维护三要素/fixture→预期值映射节式,本文档族式承接);
- 数据接入点登记(快照/事实引擎标准化产出面——本包**零新数据接入**): 终验清单执行与判定汇编的取数面=仓库内版本化文件(归档索引对象)+自产状态日志,零 data/daily 直读(P-F-16 守卫)、零研究状态档读写(P-F-21)、零 GLM/网络(§零.8);
- `.gitignore` L1(`data/` 全忽略——运行产物不 commit 结构性保障,P-F-20);
- CI 面: `.github/workflows/offline-tests.yml` L1-64(触发 push/PR main+dispatch;Python 3.11@L29;逐套件运行记录退出码,L40 test_glm_live 显式 SKIP);

### §零.7 开工核验(2026-11-08T05:23-05:4xZ 实取)

- 步骤0: `git status` clean(开工时在 dev/p3-impl-e@f74a126,工作树干净,非本包所致脏=无);UTC 开工时刻 2026-11-08T05:23:18Z;
- 步骤1: 合同三占位符均实值化(BASE-P3F=98f1a95d0c7345bf1c71b05766f78c394fa78618 全值/CI=87[86 exit0+1 SKIP]/60 支冻结表 §十一.1 内嵌),无未解析标记 ✓;生效前置信号=冻结章 §十一 生效前置达成登记(WP-P3-A~E 全 PASS+层序闭合,注入摘要,非工作树实读)✓;**执行发车硬门联动核验**: 冻结章判定「是」+注入附实批落档证据(§零.1)→ 门满足 ✓;
- 步骤2: `git ls-remote origin main dev/p3-design-fix1 dev/p3-impl-e` 实取: main=`98f1a95d0c7345bf1c71b05766f78c394fa78618`(=BASE-P3F 全值一致 ✓)/dev/p3-design-fix1=`7f43724661b50e011394e643cdd8c223c0b27a90`(全值一致 ✓,未锚 f93adb5)/dev/p3-impl-e=`f74a126d958058c13fb291464c15690f4c50e47b`(=冻结表登记值一致 ✓);全量 ls-remote 留证(证据包 03 类);
- 步骤3: `git checkout -b dev/p3-impl-f 98f1a95d…` 自基线全值切出(非自当前 HEAD 盲切)✓;
- 步骤4(设计在场核验,本包无并入步): ①`git merge-base --is-ancestor 7f43724661b50e011394e643cdd8c223c0b27a90 HEAD`→exit 0 可达 ✓;②设计三件 `git ls-tree` 双侧(HEAD vs 7f43724)blob 逐一相同: P3_INVENTORY=9f366da5a9e327e524ae1a17eec229722cd85d5f/P3_DESIGN=5acc130a88d9635a1e82d7ad3beb4f1dbe008106/P3_DELIVERY=ac8965ce0e09a964f5b493ebe1ef7dcacfca9b2d ✓;
- 步骤5: §7 实读 WP-P3-F 行在场(L200-208)四要素齐备,与 A/B/C/D/E 行可区分(§零.1)✓;范围列非文件级→固定推导规则生成清单(§零.2)✓;依赖列无并入他支要求/无真实 GLM·网络·凭证·付费要求 ✓;
- CI 基线: `ls tests/test_*.py` 计数=87 [实取·开工清点 2026-11-08T05:2xZ]=冻结章 CI 87 槽口径一致(86 exit0+1 SKIP;分支 run 预期=87+本包新增 tests 文件数 1=88);本地 Python 3.9.6(CI=3.11@offline-tests.yml L29),实现保持 3.9 兼容语法(WP-A..E 同款约束;日历函数零 datetime,P-F-15)。

### §零.8 AC-03.7(GLM 桩边界)适用判定

登记清单(§零.2)无 GLM/LLM 能力级调用面实现文件(范围列 L202 零 GLM 字样;模块=终验清单执行+判定材料汇编+横切登记确定性结构;L202 明文「不预执行」——运行时验收两项①②零执行面,P-F-06)→ **AC-03.7 不适用**,判定依据=清单无调用面类文件(§零.2 表 1-4 无客户端封装/调用编排/适配器类)。

### §零.9 实现期登记(报告笔回填;时点=各笔提交时点)

- (报告笔回填: 交付双代码件定值 sha256/黄金面双源一致/本地测试计数/本地 CI 镜像/负向敏感性注入记录/双解释器/实现期对账与自纠/真实运行产物登记——预留)
