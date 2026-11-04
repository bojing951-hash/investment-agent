# IA-P03-E2EB-WP-B3 REPORT — 日本利率数据身份与获取【情形(d)规格冲突·合法停止·登记件】

> 包: IA-P03-E2EB-WP-B3(E2E-B 第 3 实现包) · 执行Agent: Agent 3
> 分支: `dev/p03-e2eb-b3`(v1.0 段自 fe046913404a63f3d08ec362a53808d418efdcde 切出;v1.1 段沿用既有分支续作,基点=9575419d2d8cedbeac69b7b7bf347f42168be8b9;本包无并入步)
> 合同: IA-P03-E2EB-WP-B3-AC-v1.1(v1.0 冻结→v1.0 执行段触发(d)→操作者 v1.1 修正章重冻,2026-11-05 05:22 HKT[注入,合同 v1.1 重冻章,非工作树实读];v1.0 原文归档=rounds/023/criteria-v1.0-frozen.md[注入])
> **状态(v1.0 段): 情形(d)规格冲突合法停止——零开发零实现;处置记录=rounds/023/OPERATOR-DISPOSITION-R023.md[注入]。**
> **状态(v1.1 段,本段): 情形(d)规格冲突合法停止(残余冲突面)——本文件为停止登记件,非交付登记件。v1.1 修正面已解决 v1.0 段 C-1~C-4 全部冲突点,但开工步骤5-6 实测暴露**新的结构冲突**(既有测试同步面/source 枚举镜像锁/calendar 封闭集,见 §零-v1.1(ii) C-1'~C-3'),交付清单仍不可合法实现 → 本包 v1.1 段零开发、零实现、无交付文件清单、无 DELIVERY、无测试、无运行产物;不判 FAIL、不进审计,处置权操作者。(依据: 合同 v1.1 附录A §零(iv)/§九(d)/§十;executor prompt v1.1 §3 步骤5 停止条件/§7)
> 时区边界声明: 本文件日期/时刻凡未注明者均为 UTC;v1.0 段引用 DESIGN 行号为基线 fe04691 工作树实读行号(2026-11-04T21:12–21:18Z 实取);v1.1 段引用行号为基线 9575419 工作树实读行号(2026-11-04T21:27–21:40Z 实取;DESIGN blob 经 v1.1 步骤4 核验与 fe04691 侧等值,行号不变);引用合同/executor prompt 内容标注「注入」;工作树事实一律实读取证(命令与输出可复核,实验日志原件存 /tmp/p03-e2eb-b3-evidence/v1.1-stop/)。

---

## §零 规格抄录与冲突登记(开工首步;抄录完成,交付面推导因结构冲突中止)

### (i) DESIGN §六 WP-B3 行四要素逐字抄录

实读 `docs/P03_E2EB_DESIGN.md`(基线工作树,blob `89de7de9ba570930d5765067ae034aca07b97d72`,与 `f1fe593` 侧等值——本 REPORT §零(iv) 步骤4核验),WP-B3 行位于 **L222-226**,逐字抄录如下:

```text
L222: **WP-B3 日本利率数据身份与获取(JGB/日银政策利率入注册表+采集)**
L223: - 目标: 消除GAP-01: 注册表新增日本政策利率与JGB关键期限(至10Y)身份(81 [实取: INVENTORY 层② registry v2.0.0实测指标总数, 2026-11-02]→新增N条,registry版本升级走既有变更纪律),采集通道落地(免费公开源规则循预授权③于本包适用)。
L224: - 范围: registry变更+采集器扩展+通道SOURCE_FILE_RULES登记;**不含**模式B其余面。
L225: - 依赖: 无硬依赖(可与WP-B1/B2并行);完成后E2E-B场景双端闭合。
L226: - 验收要点草案: ①注册表计数实测断言(81 [实取: INVENTORY 层② registry v2.0.0实测指标总数, 2026-11-02]+N,工件: 测试文件+registry文件SHA) ②身份语义校验通过(registry_semantics既有校验,工件: 测试) ③真实采集样本落data/daily且经快照Gate A(工件: 数据档文件+快照digest) ④文档口径登记(单位percent/日历/来源,工件: registry diff)。
```

四要素齐备(目标/范围/依赖/验收要点),无缺失;依赖列「无硬依赖(可与WP-B1/B2并行)」与基线 fe04691 无矛盾、不要求并入他支。**但范围(L224)与验收要点(L226①③④)与冻结合同结构边界正面冲突,触发合同 §零(iv) 合法停止条件 → 交付文件清单不可合法推导,本包开工即停。冲突逐点登记如下。**

### (ii) 冲突登记(五点,全部基线工作树实读取证,2026-11-04T21:12–21:18Z)

**C-1 范围项「registry变更」+验收要点④工件「registry diff」 ↔ 合同§八④/AC-05①「M/D 行=0」「不改 config/metric_registry.json」**
- 取证: `config/metric_registry.json` 为既有文件(`git ls-files` 在场),version 2.0.0、81 指标[实取: 本文件实读 json,2026-11-04T21:14Z;与 DESIGN L223 登记值 81/2026-11-02 相符]。任何 registry 变更 = 对既有文件 M 行,直接触发 AC-05 反例①;要点④工件「registry diff」本身即以 M 行存在为前提。
- 依合同附录A §零(iii) 结构约束「清单内路径与 git ls-files 零重合(纯新增)」,registry 变更无法进入白名单。

**C-2 范围项「采集器扩展」 ↔ 合同§八④「不改研究主流水线任何既有文件」/AC-05⑤(采集器明列零改动对象)**
- 取证: 采集器为 scripts/ 既有文件:`china_market_collector.py`/`global_market_collector.py`/`macro_collector.py`/`news_collector.py`/`rate_expectations.py`(git ls-files 在场;registry 81 指标按源分布[实取]: china_market_collector 12/fact_engine(derived) 4/global_market_collector 32/macro_collector 28/macro_collector(derived) 1/rate_expectations 4)。「扩展」= 修改既有采集器或其通道配置,M 行。

**C-3 范围项「通道SOURCE_FILE_RULES登记」 ↔ 合同§八④/AC-05⑤(主流水线零改动)**
- 取证: `SOURCE_FILE_RULES` 定义于 `scripts/research_provenance.py:152-157`(基线工作树实读;四通道 global/macro/china/rate_economy,单一权威定义纪律见同文件 L148-151 注释),`scripts/snapshot_builder.py:41-44` 自其推导 SOURCES。新增日本利率通道 = 修改该既有 dict,M 行。

**C-4 验收要点③「真实采集样本落data/daily」 ↔ 合同§八⑤「零网络调用;不申请/使用新数据源」/AC-05④零网络/AC-07④(新源发现→登记不实施)/§零运行产物边界「data/daily/ 与既有快照只读」**
- 取证(离线不可得性): `data/daily/` 现有 4 数据族(china/global/macro/rate_economy)[实取: 目录实测];对全部 *.json 关键词扫描(jgb/japan/boj/日本/yen/jpy)日本利率**零命中**——唯一日本相关数据为 global 族内 USDJPY 汇率(`/data/JPY=X`,如 `data/daily/global_20261102.json`)[实取],非利率;registry 81 指标日本利率零命中(日本侧唯一指标=EWJ ETF)[实取]。→ 要点③要求从免费公开源发起**真实网络采集**(新数据源),在零网络边界下不可达;且其产物落点 `data/daily/` 被合同明令只读(合同运行产物边界仅允许产物落 `data/research/`)。
- 注: 治理层「免费公开数据源直用(预授权③)」[注入摘要,非工作树实读]与合同§八⑤本包零网络/不新源的包级边界不一致——本合同冻结在后且为本包权威边界,冲突按(d)上交,不由执行Agent裁量。

**C-5 交付文件清单推导结构性失败 ↔ 合同附录A §零(ii)固定推导规则仅支持「纯新增 scripts/ 模块」+§零(iii)零重合约束**
- 范围三项(C-1/C-2/C-3 对象)全部为**对既有文件的修改**,无一项可表达为纯新增文件;验收要点①④工件(registry文件SHA/registry diff)同样以既有文件变更为前提。若以「新增旁路 registry 文件/旁路采集脚本」创造性绕开,即合同§七/§九明令禁止之「创造性解决冲突」,且背离 DESIGN L223「registry版本升级走既有变更纪律」本意(旁路文件不生效即未消除 GAP-01,生效即必改既有加载链=越界)。
- → 交付文件清单不可合法推导,白名单无法成立,AC-01 交付面登记无法完成。

### (iii) 停止判定与执行内容

依冻结合同附录A §零(iv)(「DESIGN 范围要求…网络·新数据源凭证 → 开工即停」「清单违反结构约束」)、§九(d)(「与结构边界矛盾」→ 开工即停,零开发或最小登记执行,不判 FAIL 不进审计,处置权操作者)、§十.3(主Agent拟合同自检即预设「WP-B3 可能含…网络/数据获取需求…冲突=开工停止(d)而非违约」[注入])及 executor prompt §3 步骤5/§7 同款条款:

- **本包宣告情形(d)规格冲突合法停止。**
- 零开发: 不实现任何 WP-B3 范围项;不创建 DELIVERY/测试/代码文件;不触碰 registry/采集器/SOURCE_FILE_RULES/data/daily/LIVE 路径/launchd;零网络零 GLM 零凭证。
- 仅登记件执行: 本 REPORT §零(抄录+冲突登记+核验记录)为唯一落档动作。
- 不运行测试套件、不装配 /tmp 证据包、不 dispatch CI(均属审计交付面,(d)停止不进审计;分支相对基线唯一差异为本 docs 文件,无代码路径变化,CI 零回归由 diff 结构自证)。
- **处置权操作者**。处置参考(非本Agent决定): ①合同 v1.1 增设授权面——registry 变更(M 行豁免条款)+采集器扩展+SOURCE_FILE_RULES 登记之既有文件修改授权、免费公开源网络采集授权(如循治理预授权③,须操作者定夺)、采集样本落 data/daily 之写入授权(现合同只读条款豁免)、对应白名单结构改造(M/A 混合清单);或②回补设计处置(如将采集拆为独立包另立合同)。涉用户保留事项则 PENDING。

### (iv) 开工核验记录(取证留档,全部原样可复核)

| 核验项 | 结果 |
|---|---|
| 步骤0 时序自检 | `git status` clean,分支 main 起,2026-11-04T21:12:19Z(UTC) |
| 步骤1 占位符 | 三占位符已实值化: BASE-B3=fe046913404a63f3d08ec362a53808d418efdcde/CI套件58/BRANCH-SET 33支[注入: 提示词§0,冻结 2026-11-05 05:11 HKT];生效前置信号(WP-B2 PASS)成立 |
| 步骤2 前置实取 | `git ls-remote origin dev/p03-e2eb-b2` = fe046913404a63f3d08ec362a53808d418efdcde(全值一致);`dev/p03-e2eb-design` 尖端 f1fe593faa0f1754e6a6ab14c39f39fc0848550a(前7位=f1fe593 一致);main=b5c33f85c42e12b4f04e2a80faa1131244997c70 |
| 步骤3 切建分支 | `git checkout -b dev/p03-e2eb-b3 fe046913…`,HEAD=fe046913404a63f3d08ec362a53808d418efdcde |
| 步骤4 设计在场核验 | `git merge-base --is-ancestor f1fe593… HEAD` exit 0(可达);三件 blob 双侧等值: P03_E2EB_DELIVERY.md=5e0eb558036f631f27c751bec296c8d8d97e2ec9,P03_E2EB_DESIGN.md=89de7de9ba570930d5765067ae034aca07b97d72,P03_E2EB_QUERY_SURFACE_INVENTORY.md=9306e68b54ac2ec03252289f2330355f395a2b38(HEAD 侧与 f1fe593 侧逐一相同) |
| 步骤5 规格抄录 | 完成(本 §零(i),L222-226 逐字);交付面推导中止于 §零(ii) C-5 → 触发(d)停止 |
| 基线工作树事实 | registry v2.0.0/81指标/日本利率零命中(唯一日本侧=EWJ);SOURCE_FILE_RULES=research_provenance.py:152-157(4通道);data/daily 4数据族、日本利率数据零命中(仅 USDJPY 汇率);registry 指标按源分布见 C-2 |

---

## §一 数值标注清单(§5.3 纪律适用于本登记件)

| 数值 | 标注 |
|---|---|
| WP-B3 行号 L222-226 | [实取·来源: docs/P03_E2EB_DESIGN.md 基线工作树,2026-11-04T21:13Z] |
| registry version 2.0.0 / 81 指标 | [实取·来源: config/metric_registry.json 实读,2026-11-04T21:14Z] |
| registry 按源分布 12/4/32/28/1/4 | [实取·来源: config/metric_registry.json groupby source,2026-11-04T21:18Z] |
| SOURCE_FILE_RULES 行号 152-157/4通道 | [实取·来源: scripts/research_provenance.py] |
| snapshot_builder 引用行 41-44 | [实取·来源: scripts/snapshot_builder.py] |
| data/daily 4 数据族 | [实取·来源: data/daily/ 目录实测,2026-11-04T21:15Z] |
| 三件 blob 哈希/基线/design/main SHA | [实取·来源: git ls-tree/ls-remote,§零(iv)] |
| 冻结时刻 05:10/05:11 HKT、58 套件、33 支 | [注入·来源: executor prompt §0 与合同冻结章,非工作树实读] |
| N(新增条数) | DESIGN 未定值(原文即「新增N条」),[示意·非实取,DESIGN L223 原文] |

---

*〔v1.0 段完,2026-11-04T21:18Z;以下为 v1.1 重发执行段追加,2026-11-04T21:40Z〕*

---

# v1.1 执行段(基点 9575419d2d8cedbeac69b7b7bf347f42168be8b9)

## §零-v1.1 开工核验与残余冲突登记

### (i) 开工核验记录(步骤0-5,全部原样可复核)

| 核验项 | 结果 |
|---|---|
| 步骤0 时序自检 | `git status` clean,分支 dev/p03-e2eb-b3,2026-11-04T21:27:17Z(UTC) |
| 步骤1 占位符 | 三占位符已实值化: BASE-B3=9575419d2d8cedbeac69b7b7bf347f42168be8b9/CI套件58/BRANCH-SET 34支[注入: 提示词§0,v1.1 重冻 2026-11-05 05:22 HKT];生效前置(WP-B2 PASS 合并 main b5c33f8)成立 |
| 步骤2 前置实取 | `git ls-remote origin dev/p03-e2eb-b3`=9575419d2d8cedbeac69b7b7bf347f42168be8b9(=基线,全值一致);`dev/p03-e2eb-b2`=fe046913404a63f3d08ec362a53808d418efdcde(谱系前件一致);`dev/p03-e2eb-design`=f1fe593faa0f1754e6a6ab14c39f39fc0848550a(前7位 f1fe593);main=b5c33f85c42e12b4f04e2a80faa1131244997c70 |
| 步骤3 接管既有分支 | 已在 dev/p03-e2eb-b3,`git rev-parse HEAD`=9575419d2d8cedbeac69b7b7bf347f42168be8b9(=基线);v1.0 (d)登记件 commit 为合法谱系前件,保留不 revert |
| 步骤4 设计在场核验 | `git merge-base --is-ancestor f1fe593… HEAD` exit 0(可达);三件 blob 双侧等值: P03_E2EB_DELIVERY.md=5e0eb558036f631f27c751bec296c8d8d97e2ec9,P03_E2EB_DESIGN.md=89de7de9ba570930d5765067ae034aca07b97d72,P03_E2EB_QUERY_SURFACE_INVENTORY.md=9306e68b54ac2ec03252289f2330355f395a2b38(HEAD 侧与 f1fe593 侧逐一相同)——**核验通过,无基线异常** |
| 步骤5 规格抄录 | WP-B3 行 L222-226 四要素逐字抄录沿用 §零(i)(DESIGN blob 等值核验通过,原文与行号不变);v1.1 修正面消解 v1.0 段 C-1(registry M 行授权)~C-4(网络+data/daily 写入豁免)→ 抄录面无冲突,**推进至交付清单推导与实现可行性实测** |
| 步骤6 前置实读 | registry_semantics.py 封闭集/fact_engine 通道 normalize/snapshot_builder SOURCES 推导/B1/B2 REPORT §零/INVENTORY 日本侧实测,登记见 (ii) |

### (ii) 残余冲突登记(三点,全部基线工作树实读取证+受控实验,2026-11-04T21:27–21:40Z)

**C-1' registry 新增 active 日本指标 ↔ 既有测试计数锁/契约锁的同步面不在 v1.1 M 行授权内(实测坐实)**

DESIGN L223/L226① 要求 registry「81→新增N条」+要点①「注册表计数实测断言(81+N)」。受控实验(方法见 (iii)): 向 `config/metric_registry.json` 注入恰 1 条 status='active' 日本利率指标(rates_yield/percent/macro_collector/us_rates,与真实设计定义同构)后,**≥5 个既有 CI 套件 21 处断言红**(实验日志原件 /tmp/p03-e2eb-b3-evidence/v1.1-stop/exp_*.log):

| 套件 | 基线(81指标) | 注入1条active后 | 失败断言(file:line) |
|---|---|---|---|
| tests/test_p02_w1.py | 46通过/0失败 | 41通过/**5失败** | A1 L71 `len(_REG['metrics'])==81`;A2 L75 `n_active==80 and n_core==32`(措辞原文「非预期改变即红」);A5 L93 审计报告覆盖全部81项;D6 L220 active defs 80;E4 L257 恢复后默认注册表(81/32) |
| tests/test_p02_w1_fix1.py | 41通过/0失败 | 37通过/**4失败** | L229 `len(fe.load_registry()['by_id'])==81`;L239 `len(_REG['metrics'])==81`;L271 审计覆盖81;L306 `len(fe.load_registry(force=True)['by_id'])==81` |
| tests/test_p02_w2.py | 44通过/0失败 | 42通过/**2失败** | L93 矩阵覆盖全部81项;L349 G1 正常日真实链路 Gate A=PASS(实测变 DEGRADED) |
| tests/test_e2e_frozen14.py | 33通过/0失败 | 28通过/**5失败** | E2E-01a Gate A=PASS(实测 DEGRADED);01b 包meta.gate_a='PASS';01c 周报PASS;02d L334 `noncore_missing==['UMCSENT']`(实测变 `['JGB_10Y_EXP','UMCSENT']`);02d2 facts 计数 |
| tests/test_gate_chain_p01.py | 86通过/0失败 | 81通过/**5失败** | 真实快照 gate=DEGRADED 连锁(gate_status 读取PASS/裸字符串PASS/锚点上下文/合成质量PASS/无降级footer) |

机制: ①81 计数锁 8 处(3 文件)直接红;②「全 active 齐备=正常日 Gate A=PASS」契约(tests/fixt.py L6-10 明文: 「fixture必须使用**真实指标注册表**生成的完整active/core集合…缺席=非核心缺失→DEGRADED披露」)——新增 active 指标不在 fixt 合成采集 payload(硬编码 80 active 项,tests/fixt.py collector_payloads),缺席→noncore_missing→DEGRADED,凡断言正常日 PASS 的连锁红。

合同边界: v1.1 AC-05①「M 行=恰授权白名单恰 m 行(registry+research_provenance+REPORT §零登记的采集器文件)」,§八「清单外任何 A/M 行=违约」——tests/ 既有文件零授权;不改测试→5 套件红→AC-06③ 反例③(套件红);改测试→AC-05① 反例①(M 行违例)。历史先例: 63bd7504eefaed7e80d5ab22004484ab64d2227d(registry 22 项窗口修改)同 commit 同步修改 5 个既有测试文件——「registry版本升级走既有变更纪律」(DESIGN L223)在既有工程实践中**事实包含测试同步**,v1.1 授权面未覆盖此同步面(与 v1.0 段 C-1 同构: v1.1 修了 registry 文件的 M 行,未修其纪律配套面)。

**C-2' 采集器扩展的 source 枚举封闭+三方镜像锁,扩枚举需两处白名单外文件同步**

registry 新指标的 `source` 字段必须属于 `registry_semantics.KNOWN_SOURCES`(封闭 6 值,error 级: scripts/registry_semantics.py L68-73 定义、L276-277 R-SOURCE-ENUM「source ∉ KNOWN_SOURCES → error」,经 fact_engine.load_registry 接入生产加载,出现即抛 RegistrySemanticsError——非枚举值=全系统 registry 加载失败,58 套件崩)。新采集器(DESIGN L224「采集器扩展」,v1.1 M 行授权对象)的自然 source 值不可入枚举;扩枚举需三方同步: ①`research_provenance._AUTHORIZED_COLLECTORS`(L135-141,M 行内)②`registry_semantics.KNOWN_SOURCES`(L68-73,**白名单外**)③`tests/test_p02_w1.py` A6c 镜像锁(L106-107: `KNOWN_SOURCES == frozenset(rp._AUTHORIZED_COLLECTORS) | {'macro_collector(derived)'}`,**白名单外**)——任一缺省即测试红或加载崩。不扩枚举(source 取既有 4 采集器值)则与 japan_rate 新通道错位: `_SOURCE_TO_INPUT`(research_provenance.py L111-117)把既有 source 映射到既有通道,`fact_source_problems`(同文件 L745-829)批次一致性要求事实 source.file==该通道批次文件,日本指标事实(若未来经 fact_engine 接入)与 japan_rate_*.json 批次冲突被拒——通道登记(范围第三项)与来源身份结构性脱节。

**C-3' calendar 封闭集无 japan 日历,要点④「日历」口径登记无语义正确合法值(弱冲突,如实登记)**

registry 指标 `calendar` 必须属于 `KNOWN_CALENDARS={us_equity,us_rates,commodity,cn,hk,fx,crypto}`(registry_semantics.py L61+L273-274 R-CALENDAR-ENUM error 级;tests/test_p02_w1.py L104 A6b 镜像 trading_calendar.MARKETS)。日本利率(JGB/日银政策利率,日本金融市场观测)无对应日历;取 'us_rates'=美国利率市场日历配日本国债,属口径失实,与要点④「文档口径登记(单位percent/**日历**/来源)」的如实登记要求冲突。trading_calendar.py/registry_semantics.py 均白名单外,不可新增 'jp_rates' 类日历。

### (iii) 受控实验记录(方法与还原,完整日志 /tmp/p03-e2eb-b3-evidence/v1.1-stop/)

1. 注入: 以 /tmp/b3_exp_inject.py 向 config/metric_registry.json append 1 条 `JGB_10Y_EXP`(active/rates_yield/percent/us_rates/macro_collector/index_rate_series/validation[0,15]/freshness 7)——注入后 82 指标;
2. 实测: 注入态跑 7 套件(test_p02_w1/w1_fix1/w2/e2e_frozen14/gate_chain_p01/e2e_orig14/e2e_four_weeks),5 套件红(21 断言,见 (ii) 表)、e2e_orig14 与 e2e_four_weeks 恰 0 失败(其对 noncore_missing/Gate 计数无精确断言,如实登记);
3. 还原: `git checkout -- config/metric_registry.json`(实验前工作树 clean、该文件无本地改动,还原到 HEAD 态;注入脚本首次备份命令因沙箱拒未落盘,还原用 git 权威态)→ 实测 81 指标/version 2.0.0/JGB_10Y_EXP 零残留;
4. 对照: 还原态重跑同 5 套件全绿(w1 46/0、w1_fix1 41/0、w2 44/0、frozen14 33/0、gate_chain 86/0)——红面由注入**单独**致生的因果链闭合;
5. 本实验零网络、零提交、零 LIVE 触碰,实验后工作树 clean。

### (iv) 四路穷尽论证(无可合法实现路径)

| 路径 | 结果 |
|---|---|
| ①新增 active 指标+不改既有测试 | ≥5 套件 21 断言红(实测)→ AC-06③ 反例③「套件红」+ AC-03⑤「本地逐套件全绿」不可能 → **FAIL 面** |
| ②新增 active 指标+同步改既有测试 | tests/ 既有文件 M 行,v1.1 白名单外 → AC-05① 反例①「清单外任何 A/M 行=违约」 → **FAIL 面**(REPORT §零 把测试文件登记入 M 行亦违 §零(iii)「M 行=恰授权白名单」,登记无效) |
| ③新增 status='deprecated' 指标(绕开 active 集合与计数锁 active=80 断言——计数 81+N 断言满足、A2/D6 的 n_active==80 亦满足) | 语义伪造: 新增身份标「已弃用」与 DESIGN L223「新增日本政策利率与JGB关键期限身份」、L225「完成后E2E-B场景双端闭合」(要求可查询的 active 身份)、INVENTORY G-01(「日端无法取数」待消除)语义相反;deprecated 不入 active 集合(metric 检索/缺失判定/查询面均按非 active 处理),GAP-01 实质未消除 → AC-07 如实纪律/审计 AC-01 语义失实 → **FAIL 面**(且为「创造性解决冲突」禁令所禁) |
| ④零 registry 变更(仅采集器+通道登记) | 要点①(81+N 计数断言)②(registry_semantics 对**新增日本条目**的校验)④(registry diff 工件)三要点无实现落点 → AC-02 反例①「要点无映射行」 → **FAIL 面**;且 japan_rate 通道先行入 SOURCE_FILE_RULES 而身份缺席=半包状态,污染后续包边界 |

四路皆 FAIL 面 → DESIGN WP-B3 权威范围与 v1.1 合同结构边界在**测试同步面/枚举镜像锁/calendar 封闭集**上正面冲突,属合同 §九(d)「与结构边界矛盾」→ **开工即停,零开发,最小登记执行**。

### (v) 停止判定与执行内容(v1.1 段)

依合同 v1.1 附录A §零(iv)(「清单违反结构约束…→开工即停情形(d)」)、§九(d)(「规格冲突合法停止…与结构边界矛盾→开工即停如实报告,零开发或最小登记执行,不判 FAIL、不进审计,处置权操作者」)、§十.12、executor prompt v1.1 §3 步骤5/§7 同款条款:

- **本包 v1.1 执行段宣告情形(d)规格冲突合法停止(残余冲突面 C-1'~C-3')。**
- 零开发: 不实现任何 WP-B3 范围项;不创建 DELIVERY/测试/代码文件;不触碰 registry/采集器/research_provenance/registry_semantics/tests/data/daily/LIVE 路径/launchd;零网络零 GLM 零凭证零付费(受控实验为基线工作树内的临时注入+还原,零提交,已还原 clean 并全绿对照)。
- 仅登记件执行: 本 REPORT v1.1 段(核验记录+残余冲突登记+实验记录+四路穷尽+停止判定)为唯一落档动作;实验日志与基线对照日志原件存 /tmp/p03-e2eb-b3-evidence/v1.1-stop/(13 件,供操作者 v1.2 处置参考;(d)停止不进审计,不装配 AC-06 八类证据包)。
- 不运行 CI dispatch((d)停止不进审计;分支相对基线唯一差异为本 docs 文件追加,无代码路径变化,CI 零回归由 diff 结构自证)。
- **处置权操作者**。处置参考(非本Agent决定): ①合同 v1.2 修订——M 行授权扩至「测试同步面」(test_p02_w1.py/test_p02_w1_fix1.py/test_p02_w2.py/test_e2e_frozen14.py/test_gate_chain_p01.py/tests/fixt.py 的计数锁/契约锁同步更新)+registry_semantics.py(KNOWN_SOURCES/KNOWN_CALENDARS 扩枚举)+trading_calendar.py(japan 日历,若需)+A6 镜像锁三方同步,并相应更新 AC-05①/AC-06① 套件基线登记(58 不变,套件文件数不变);或②回补设计处置(WP-B3 拆分为「身份注册+测试同步」与「采集+通道」两包,前者先行);或③改用 DESIGN 行修订(要点①计数断言改为「≥81」弱锚或移除)。涉用户保留事项则 PENDING。

### (vi) LIVE 侧零接触取证(2026-11-04T21:38Z)

- LIVE `real_data_acceptance.py` SHA256=f9ca189c5248199bb5acbc78b2a2c82d59c10e1c7c2c2d20bdaaa6105fbfe3eb(合同登记前缀 f9ca189c… 一致,不变);
- LIVE 目录 grep(`R023|E2EB-WP-B3|IA-P03-E2EB-WP-B3`)零命中;
- LaunchAgents 零改动;零写入(全部命令只读)。

## §一-v1.1 数值标注清单(§5.3 纪律)

| 数值 | 标注 |
|---|---|
| v1.1 基点 9575419d2d8cedbeac69b7b7bf347f42168be8b9 | [实取·来源: git rev-parse HEAD + ls-remote origin dev/p03-e2eb-b3,2026-11-04T21:27Z] |
| 套件基线 58/BRANCH-SET 34 支/重冻时刻 05:22 HKT | [注入·来源: executor prompt §0 与合同 v1.1 重冻章,非工作树实读] |
| 实测套件计数: tests/test_*.py=59 文件(CI 排除 test_glm_live→58 套件) | [实取·来源: Glob tests/test_*.py + .github/workflows/offline-tests.yml 排除逻辑实读,2026-11-04T21:31Z] |
| 注入实验红面: 5 套件/21 断言(w1 5+w1_fix1 4+w2 2+frozen14 5+gate_chain 5) | [实取·来源: /tmp/p03-e2eb-b3-evidence/v1.1-stop/exp_*.log 各文件「结果: X通过/Y失败」行+❌行,2026-11-04T21:32–21:33Z] |
| 还原对照绿面: w1 46/0、w1_fix1 41/0、w2 44/0、frozen14 33/0、gate_chain 86/0 | [实取·来源: 同目录 verify_*.log,2026-11-04T21:34–21:35Z] |
| registry v2.0.0/81 指标(实验前与还原后两度实读一致) | [实取·来源: config/metric_registry.json json.load,2026-11-04T21:28Z/21:34Z] |
| KNOWN_SOURCES 6 值/KNOWN_CALENDARS 7 值/R-SOURCE-ENUM L276-277/R-CALENDAR-ENUM L273-274 | [实取·来源: scripts/registry_semantics.py 实读,2026-11-04T21:29Z] |
| A6c 镜像锁 L106-107 | [实取·来源: tests/test_p02_w1.py 实读] |
| 计数锁行号 L71/L75/L93/L220/L257(w1)、L229/L239/L271/L306(w1_fix1)、L93/L349(w2)、L334(frozen14) | [实取·来源: 对应测试文件 grep -n 实取,2026-11-04T21:36Z] |
| fixt.py 全 active 齐备契约(L6-10 docstring) | [实取·来源: tests/fixt.py 实读] |
| 先例 commit 63bd7504eefaed7e80d5ab22004484ab64d2227d(registry 22 项窗口变更+同 commit 改 5 测试文件) | [实取·来源: git show --stat 63bd750,2026-11-04T21:30Z] |
| 三件设计文件 blob 哈希/各分支尖端 SHA | [实取·来源: git ls-tree 双侧 + ls-remote,§零-v1.1(i)] |
| LIVE sha256 f9ca189c…/grep 零命中 | [实取·来源: shasum -a 256 + grep -rl,2026-11-04T21:38Z] |
| N(DESIGN 未定值) | [示意·非实取,DESIGN L223 原文「新增N条」;实验注入 N=1 仅为冲突探针,非设计定值] |

---

*本文件为 IA-P03-E2EB-WP-B3 情形(d)合法停止登记件(v1.0 段+ v1.1 段);零实现零交付,不进审计;处置权操作者。*
