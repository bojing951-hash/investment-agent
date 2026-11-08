# IA-P1-WP-A REPORT(登记件 · **v1.4 实现轮 · 状态=执行中(v1.3 停止#3 已处置: N3d 单点扩容授权)**)

> 包: IA-P1-WP-A(P1 四经济体底图层实现包第 1 包/族首包)| 分支: `dev/p1-impl-a`(自 018d913061a2b0ab5680e6c49c544efef740db7e 切出)
> 合同: IA-P1-WP-A-AC-v1.1(FROZEN 2026-11-05 21:1x HKT 操作者代批)→ v1.2(FROZEN 2026-11-05 操作者发车,§3 步骤3=分支续作形态 @33d0dfc)→ **v1.3(FROZEN 2026-11-05 操作者发车,§3 步骤3=分支续作形态 @f0a2aea;(g)-(k)+从属锁类增 t06+research_provenance 括注明确化+实现参数预登记锚定)**
> **状态: v1.1(§零.1-§零.6)+v1.2(§零.7-§零.10)+v1.3(§零.11-§零.15)三轮历史在案;v1.4 轮(§零.16)执行完毕: N3d 域化+要点②真实采集(A6/A7 首档在场)+本地 CI 70 槽全绿+终笔推送**
> 时点: v1.1 轮停止 2026-11-05T13:1xZ / v1.2 轮停止 2026-11-05T13:57:07Z / v1.3 轮开工 2026-11-05T14:04:45Z / v1.4 轮开工 2026-11-05T15:36:00Z(UTC)[实取·本机 date -u]
> 本文件数值标注纪律沿 §5.3: 逐值 [实取·来源] 或 [示意·非实取]。

---

## §零.1 规格抄录(AC-01 锚;逐字抄录自 `docs/P1_DESIGN.md` §六 L169,基线工作树实读)

**定位**: §六「工作包拆解」表,表头 L167,WP-P1-A 行=**L169**;同族后继行 WP-P1-B..E=L170-L173 [实取·docs/P1_DESIGN.md L165-L173 逐行实读]。A 行与后继行可区分(A=registry+JP/EA 采集面;B=事实引擎快照/C=评分装配报告/D=查询面且依赖列明文「依赖 P0-3 落地」/E=CN 面且依赖列明文「依赖用户授权」)——冻结章三项实读义务记录同款判定,实读一致。

**L169 原文逐字抄录**:

```
| WP-P1-A 注册表与 JP/EA 采集面 | 81 [实取·INVENTORY b.1 registry 实测计数,2026-11-02] + 12 [示意·候选·§三(a-3) 候选清单,非实取] 条目经济体化+JP/EA 通道落地 | registry 三字段回填与12候选条目 [示意·候选·§三(a-3) 候选清单,非实取]、jp_/ea_ 采集脚本与数据档、run_weekly 步骤接入 | 免费 public API 循预授权③(DP-2);不依赖 P0-3 | ① 单测: registry economy 字段与 P1-P8 规则一致性(逐条断言)+负向(规则未命中条目拒入)【测试】② 首份 `data/daily/jp_/ea_YYYYMMDD.json` 真实档在场【数据档引用】③ 新采集器离线测试(源失败→MISSING 不填0)【测试/CI】④ offline-tests 全套件零回归【CI】 |
```

**四要素逐字分解**(表格单元格切分,字符零增删):

- **目标**(L169 列2): `81 [实取·INVENTORY b.1 registry 实测计数,2026-11-02] + 12 [示意·候选·§三(a-3) 候选清单,非实取] 条目经济体化+JP/EA 通道落地`
- **范围**(L169 列3): `registry 三字段回填与12候选条目 [示意·候选·§三(a-3) 候选清单,非实取]、jp_/ea_ 采集脚本与数据档、run_weekly 步骤接入`
- **依赖**(L169 列4): `免费 public API 循预授权③(DP-2);不依赖 P0-3`
- **验收要点草案**(L169 列5): `① 单测: registry economy 字段与 P1-P8 规则一致性(逐条断言)+负向(规则未命中条目拒入)【测试】② 首份 `data/daily/jp_/ea_YYYYMMDD.json` 真实档在场【数据档引用】③ 新采集器离线测试(源失败→MISSING 不填0)【测试/CI】④ offline-tests 全套件零回归【CI】`

**所引设计节实读登记**(步骤6 前置实读,冲突证据涉及处):

- §三(a-1) L37-L43: registry 在既有 17 字段上新增 3 字段(`economy` enum {US,CN,JP,EA,HK,GLOBAL} / `economy_rule` / `market_seat` enum {onshore_local, offshore_proxy, global}),`economy` 取值=INVENTORY a.3 规则 P1-P8 的机械结果 [实读]。
- §三(a-2) L45-L58: jp_/ea_ 数据档结构(顶层 date/generated_at/sources_status;jp_ 节 policy_rates.BOJ_POLICY_RATE、jgb.JGB_10Y/JGB_2Y、inflation.JP_CPI_TOKYO_YOY、prices.NIKKEI225;ea_ 节 policy_rates.ECB_DFR/ECB_MRO、bund.BUND_10Y/BUND_2Y、inflation.EA_HICP_YOY、prices.DAX/CAC40;「任何节缺席→键不出现或 value=null,禁以 0 占位」L58)。
- §三(a-3) L62: registry 新条目候选清单 **12 条**(`BOJ_POLICY_RATE / JGB_10Y / JGB_2Y / JP_CPI_TOKYO_YOY / NIKKEI225 / ECB_DFR / ECB_MRO / BUND_10Y / BUND_2Y / EA_HICP_YOY / DAX / CAC40`,标注 [示意·非实取·候选清单],**「落地以 WP-A 为准」**);新函数 normalize_jp/normalize_ea 属 WP-B(GAP-P1-06 承接=WP-B,L154)。
- §四 L1 行 L124: 「新增 `scripts/jp_market_collector.py`/`ea_market_collector.py`(**候选名**);档名 `jp_/ea_YYYYMMDD.json`(a-2);`run_weekly.py` steps 列表 [实取·L126-L151] 增步骤;既有四通道零改动」。
- §五 GAP-P1-01/02/03/13 承接列=WP-A;GAP-P1-08(快照 resolve_inputs/sources_status 未含新通道)承接=**WP-B**(L156)——通道入快照登记不在本包。
- INVENTORY a.3 L35-L47: P1-P8 机械规则表(仅依赖 `calendar`/`asset_class`/`source_symbol` 三字段;P8=其余→US;无命中→「未归类」拒入待人工裁决);b.2 L62-L144: 81 行逐条归类表;b.1 L57: 归属汇总 US 49/CN 10/HK 4/JP 2/EA 4/GLOBAL 12。
- **基线工作树与 DESIGN 时点差异(实读,非注入)**: registry 现为 **85 条**/v2.1.0 [实取·config/metric_registry.json,`len(metrics)`=85、version=2.1.0,2026-11-05 实测],其中 4 条为 B3 后入场(`JP_POLICY_RATE/JGB2Y/JGB5Y/JGB10Y`,`calendar="japan"`,`source="japan_rate_collector"` [实取·同文件])——DESIGN 目标列「81」系设计时点计数(其标注自带 [实取·INVENTORY…2026-11-02] 时点戳)。

## §零.2 交付文件清单推导(附录A §零(ii) 固定规则;**因 §零.5 冲突未生效为实现白名单,仅作登记**)

按固定推导规则(每个代码模块=scripts/ 下恰 1 文件;含代码必含 tests/test_p1_wp_a.py;必含 REPORT/DELIVERY 双文档),假想清单 k=**7** A 行 + **2** M 行:

| # | 路径 | A/M | DESIGN 依据 |
|---|---|---|---|
| 1 | docs/P1_WP_A_REPORT.md | A | 必含件(附录A §零(ii));本文件 |
| 2 | docs/P1_WP_A_DELIVERY.md | A | 必含件(附录A §零(ii)) |
| 3 | scripts/jp_market_collector.py | A | §四 L124「新增 scripts/jp_market_collector.py(候选名)」+ L169 范围「jp_/ea_ 采集脚本」 |
| 4 | scripts/ea_market_collector.py | A | §四 L124「新增 scripts/ea_market_collector.py(候选名)」+ L169 范围同上 |
| 5 | tests/test_p1_wp_a.py | A | 含代码→必含(附录A §零(ii));覆盖 L169 验收要点①③ |
| 6 | data/daily/jp_YYYYMMDD.json | A | L169 验收要点②「首份 data/daily/jp_/ea_YYYYMMDD.json 真实档在场」+ v1.1④ 豁免 |
| 7 | data/daily/ea_YYYYMMDD.json | A | 同上 |
| M1 | config/metric_registry.json | M | L169 范围「registry 三字段回填与12候选条目」+ §三(a-1) L37-L43/a-3 L62;v1.1③(a) |
| M2 | run_weekly.py | M | L169 范围「run_weekly 步骤接入」+ §四 L124;v1.1③(b) |

- **条件类判定(v1.1③(c))**: `scripts/japan_rate_collector.py` M 授权**未触及**——抄录范围要求**新增**独立采集脚本(§四 L124「新增…(候选名)」),未要求扩展 B3 采集器 jp 面;复用调用(fetch 函数 import)优先于扩展,亦不构成对该文件的修改。
- **从属锁同步类(实现路径启动后生效)**: `tests/test_p03_e2eb_b3.py`(t01 计数 85/84/v2.1.0、t02 四条目全字段冻结)与 `tests/test_p03_final_acceptance.py`(t11 同款计数锁)为 registry 变更的受影响测试锁,v1.1③(a) 授权同提交域化迁移(R057/R060 形态,禁语义弱化);(d) 停止下未触。
- 结构约束(iii) 预检: A 行 7 路径与 `git ls-files` 零重合 [实取·`git ls-files` 全量对照,2026-11-05: 无同名文件在场];必含件齐;含代码件含对应 tests。

## §零.3 前置核验记录(§3 步骤0-4,原样登记)

- **步骤0** [2026-11-05T13:13:58Z 实取]: `git status` clean;HEAD=018d913061a2b0ab5680e6c49c544efef740db7e(=BASE-P1A)。
- **步骤1 占位符**: 3 处已实值——BASE-P1A=018d913…(全值)、BASE-P1A-CI-SUITES=69(68 exit=0+1 SKIPPED,run 42032319207)、BRANCH-SET=冻结章 41 分支机器表(逐行清点=41 [实取·附录A 冻结章]);生效前置信号=冻结章「生效判定 ✓」;零残留。
- **步骤2 前置实取** [2026-11-05 实取]: `git ls-remote origin main`=018d913061a2b0ab5680e6c49c544efef740db7e(全值一致);`git ls-remote origin dev/p1-design`=049ec978523dec659ba47f140bf41669604de24f(全值一致;禁锚 c9626633 未触)。
- **步骤3 切建分支**: `git checkout -b dev/p1-impl-a 018d913…` ✓(自基线 SHA 切出,非盲切)。
- **步骤4 设计在场核验**: ①`git merge-base --is-ancestor 049ec978… HEAD`=**exit 0 可达**;②设计三件双侧 blob 等值 [实取·`git ls-tree` HEAD vs 049ec978]: `docs/P1_DATA_NEEDS_INVENTORY.md`=df79c06f66c368d93159b7a3b46852b6fcb9b196、`docs/P1_DELIVERY.md`=314c2644a51f2f575a90253580cb56346e2f93b6、`docs/P1_DESIGN.md`=13b263cf3139d420e01bf1e154b03ce85a35db4c(与冻结章三项实读义务登记值一致;第三件实际文件名以基线工作树实况为准=P1_DATA_NEEDS_INVENTORY.md,合同 §零明文「以基线工作树实况为准」)。**无失配。**

## §零.4 P1 特有纪律预读登记 + DP 登记(步骤6;因 (d) 停止,登记为「已读未及执行」)

**特有纪律(实读锚定)**:

1. DESIGN §七 L177-L183「红线遵守」四条: ①快照+门禁不可绕开(四经济体一切新数据经 build_snapshot 进入研究面,jp_/ea_ 档同禁直读,L179)②LIVE 禁写(L180)③禁交易/仓位/收益承诺(L181)④数据不足不填0 五层一致(L182);§六 L175 红线筛查行(全包通用: 不含 LIVE 部署/launchd 改动/绕开快照直读)。已读;(d) 停止下零开发、零触碰,自然遵守。
2. 数据口径纪律: §三(a-2) L58「任何节缺席→键不出现或 value=null,禁以 0 占位」;§三(c) L79-L84 降级路径五层。已读;(d) 停止下无实现面。
3. 命名冲突登记(§一 L14): UPGRADE_PLAN 旧「P1」与本设计线同名不同物——本包命名带 IA-P1 前缀,已遵守(本文件名 P1_WP_A_REPORT.md 即循此)。

**DP 登记**:

- A 行依赖列明文引用 **DP-2**(JP/EA 源优先级;§二 L29,登记型[§二 L24 表头明文「登记型决策点」]),选定规则=「官方免费API优先(循预授权③);yfinance 仅用于行情类;付费一律 PENDING 不进依赖」。v1.1② 冻结章已将其操作化为白名单五域(boj.or.jp/mof.go.jp/fred.stlouisfed.org/ecb.europa.eu/bundesbank.de)+yfinance 不入依赖面。本包未运行任何采集,零 URL 实取发生(§零 原定「REPORT §零登记实取 URL」义务随 (d) 停止无实体)。DP 编号/分类与实读一致,**无 DP 类 (d) 触发**。
- 确认型 DP: §二 L24-L31 实读零确认型载明(凭证/费用/批量状态修改类均未触及);本包零触及。
- 其余 DP-1/DP-3/DP-4 不在 A 行依赖列引用面(DP-3=WP-C、DP-4=WP-E 范围),不登记。

## §零.5 冲突登记(情形(d)核心: DESIGN WP-P1-A 范围要素与合同 M 白名单结构边界矛盾)

**冲突一句话**: A 行范围「registry 三字段回填与**12候选条目**」+「jp_/ea_ 采集脚本」的**诚实注册路径**,在当前基线必需链式修改 **3 件合同冻结在 M 白名单外的文件**(`research_provenance.py`/`registry_semantics.py`/`trading_calendar.py`);在白名单内不存在不违反「如实/零编造」纪律的替代实现——故按合同 §九(d)「与结构边界矛盾」/§零(iv) 停止。

**证据链(全部基线工作树实读+运行时实测,2026-11-05)**:

1. **注册表生产加载即拒新来源/新日历**(error 级 fail-loud):
   - `scripts/registry_semantics.py` L74-L78: `KNOWN_SOURCES` 封闭 7 值集 = {global_market_collector, macro_collector, china_market_collector, rate_expectations, fact_engine(derived), macro_collector(derived), japan_rate_collector} [实取·运行时 `sorted(rsem.KNOWN_SOURCES)`];L283-L285 `R-SOURCE-ENUM` error: source∉集→error。
   - L64-L65: `KNOWN_CALENDARS`=trading_calendar.MARKETS 镜像={us_equity,us_rates,commodity,cn,hk,fx,crypto,japan}(无 `ea`)[实取·运行时];L279-L282 `R-CALENDAR-ENUM` error。
   - `scripts/fact_engine.py` L57: `assert m.get('calendar') in tc.MARKETS`(calendar 实质必填+封闭,缺省亦拒);L64: `rsem.assert_registry_semantics(reg,…)`→error 即抛 `RegistrySemanticsError`。
   - 推论: 12 候选中任一以新采集器为 source 注册 → **注册表整表不可加载**(生产 fail-loud + offline-tests 大面积红),直接违反验收要点④「全套件零回归」。source 为必填字段(L266-L269 `R-FIELD-STR`),封闭集内 7 值对 jp_/ea_ 新采集器数据**无一诚实可归属**(数据实际产自新脚本;虚假归属违反 handover L165「凑合数据打来源/降级标记禁冒充权威源」级纪律)。
2. **诚实注册路径所需文件均在 M 白名单外**:
   - `scripts/research_provenance.py` L135-L144 `_AUTHORIZED_COLLECTORS` 封闭 6 键;L141-L143 注释明文 B3 先例=新采集器入注册表须本表登记(「WP-B3…日本利率通道采集器——collector与registry source同符号(事实级授权)」)。新增 `jp_market_collector`/`ea_market_collector` 须改本文件。
   - `scripts/registry_semantics.py` L74-L78 同步扩 `KNOWN_SOURCES`(A6c 双侧镜像);EA 侧另需 `scripts/trading_calendar.py` `MARKETS` 增 `ea` 日历(JP 侧可复用 `japan`——B3 已入)。
   - 双侧镜像锁 `tests/test_p03_e2eb_b3.py` L164-L171(t04: `rsem.KNOWN_SOURCES == rp._AUTHORIZED_COLLECTORS ∪ {macro_collector(derived)}`)——单侧扩集即红,证明该链必须成套改。
   - 合同 v1.1③ M 类穷尽清单=恰 {config/metric_registry.json; run_weekly.py; 条件类 japan_rate_collector.py(未触及,§零.2 判定)};AC-05.1「出现任何清单外 M 行即违约」;§八.4 同款。上述 3 件均不在内。
3. **B3 先例反向印证**: B3 验收件被测对象清单 [实取·tests/test_p03_e2eb_b3.py L6-L8] =「scripts/japan_rate_collector.py + config/metric_registry.json(81→85) + **research_provenance(通道登记) + registry_semantics/trading_calendar(双侧同步)** + snapshot_builder(零改动派生)」——即 B3 合同范围**包含**通道登记文件链;本合同 v1.1③ 未含,系冻结章 v1.1 六项修正未覆盖到的同类「合同起草模板与设计权威范围冲突」(与 v1.1 已修正的 ①M/D=0↔registry 回填 同族,但修正面漏掉了通道登记链)。
4. **条件类亦不可 rescue**: v1.1③(c) 对 `japan_rate_collector.py` 的 M 授权条件=「抄录范围要求扩展 jp 面」;实读范围要求**新增独立脚本**(§四 L124「新增…(候选名)」),条件不成立;且「复用调用优先于扩展」——新脚本 import B3 fetch 函数属复用调用,不改变 registry source 诚实归属仍为新采集器的事实。EA 侧无任何既有采集器可诚实承载(ECB/Bundesbank/HICP/DAX/CAC40 数据产自 ea_market_collector)。
5. **未被阻断的范围要素(如实区分)**: ①三字段回填(85 条既有条目)——rsem 不校验 economy 族字段,可单独过验(需同步 B3 锁 t01/t02 与终验收锁 t11,属 v1.1③(a) 授权面);②jp_/ea_ 采集脚本+数据档本体——无校验器拦新脚本/新档(通道入快照登记=WP-B 范围,GAP-P1-08 L156);③run_weekly 步骤接入——v1.1③(b) 授权。**被阻断的核心恰为目标列主体「12候选条目…经济体化」与「JP/EA 通道落地」的注册面**(12 候选中 10 条须新 source 注册[JGB_10Y/JGB_2Y 原可按 a-3「落地以 WP-A 为准」复用 B3 既有 JGB10Y/JGB2Y 条目,但其余 10 条——JP 侧 BOJ_POLICY_RATE/JP_CPI_TOKYO_YOY/NIKKEI225 与 EA 侧全部 7 条——无诚实 source 可归属];EA 侧另缺 `ea` 日历)。

**处置建议(供操作者,非自决)**: 修订合同 v1.2 将通道登记链 3 件(research_provenance.py/registry_semantics.py/trading_calendar.py,含 A6c 镜像锁同步)纳入 M 白名单(B3 先例范围形态);或改 DESIGN 落地面(如 JP/EA 指标经既有通道承载——需设计修订,非本包权限)。本包停泊,零文本变更择时重发或 v1.2 重发。

## §零.6 (d) 停止下的边界声明

- 零开发: 未创建/修改任何代码、测试、registry、run_weekly、workflow;未发起任何网络调用/真实采集/凭证/付费;零 GLM;未写入 LIVE;未改 launchd;未触碰 main;未建其他分支。
- 本登记件(本文件)为「仅登记件执行」形态的唯一提交物;分支 `dev/p1-impl-a` 零开发提交(重发时可由操作者处置: 续用本登记件或 reset 重切)。
- 排除事项 12 项、AC-01..07 在 (d) 停止下均未进入执行面(除 §零.1-§零.4 登记义务);不判 FAIL、不进审计。

---

# ══ v1.2 轮登记(2026-11-05;分支续作形态 @33d0dfc,§3 步骤3 v1.2④)══

## §零.7 v1.2 轮开工核验(步骤0-4 复核,原样登记)

- **步骤0 时序自检** [2026-11-05T13:3xZ 实取]: `git status` clean;HEAD=33d0dfccef9221cfa2b84b0d13103b3c2d00784e=v1.1 轮(d)登记件提交;本轮复核 [2026-11-05T13:5xZ 实取] 仍 clean。
- **步骤1 占位符**: 沿 v1.1 轮核验(BASE-P1A=018d913…全值/BASE-P1A-CI-SUITES=69/BRANCH-SET=41 行),零残留;v1.2 冻结章新增占位符(分支续作尖端 33d0dfc/CI 目标 70 槽=69+新增 1)已实值 [实取·任务书 §0]。
- **步骤2 前置实取** [2026-11-05T13:5xZ 实取]: `git ls-remote origin dev/p1-impl-a`=33d0dfccef9221cfa2b84b0d13103b3c2d00784e(全值一致);`dev/p1-design`=049ec978523dec659ba47f140bf41669604de24f(全值一致;禁锚 c9626633 未触)。
- **步骤3 分支续作**: `dev/p1-impl-a` 在场@33d0dfc,checkout 续作,不删不重建不 force ✓(v1.2④ 形态;B3 v1.4 先例)。
- **步骤4 设计在场核验**: `merge-base --is-ancestor 049ec978… HEAD` exit 0 ✓;P1 设计三件 blob 等值(HEAD vs 049ec978 侧逐一相同,v1.1 轮已核、本轮 HEAD 前进仅本文件,设计件 blob 未变 [实取·git ls-tree 比对])。
- **步骤5 规格抄录**: 沿 §零.1(v1.1 轮已逐字抄录 L169;L169 本轮实读未变 [实取·blob 等值推论]);无 (d) 触发。

## §零.8 运行态锁清查(v1.2 轮核心增量;方法+清查面+实验证据)

**v1.1→v1.2 的差异**: v1.1 轮停止于**静态封闭集层**(KNOWN_SOURCES/KNOWN_CALENDARS/MARKETS/_AUTHORIZED_COLLECTORS 生产登记链);v1.2③ 已授权该层(rsem[KNOWN_SOURCES+A6c镜像]/rp[_AUTHORIZED_COLLECTORS]/tc[MARKETS/CALENDARS 增 ea]+两件 P0-3 测试锁域化)。本轮将清查推进至**运行态锁层**(注册表实载后 69 套件会真实执行到的锁),发现新的强制触红面——全部落在 v1.2③ 清单外。

**清查方法**(可复核): ①对 {registry `source` 字段消费者, `rp.SOURCE_FILE_RULES` 消费者, `tc.MARKETS`/`KNOWN_CALENDARS` 消费者, `run_weekly` 步骤形态消费者, `data/daily` 枚举消费者} 五轴做定向 grep+逐件实读;②以内存 monkeypatch 模拟「v1.2③ 授权面全部落地后的世界」,对两处核心锁执行**实验复现**(脚本+输出全文见 §零.8.3,只读仓库零写入)。

### §零.8.1 强制触红清单(全部 v1.2③ 清单外;阻止验收要点④「全套件零回归」)

| # | 锁(文件:行) | 触红机制 | 修复所需(清单外?) | 先例形态 |
|---|---|---|---|---|
| 红-1 | `tests/test_p02_w4.py` d2 L773 `assertIsNotNone(hca.REGISTRY_SOURCE_CHANNEL.get(m['source']))` | 9 条新 source 条目(`jp_market_collector`/`ea_market_collector`)在 `scripts/historical_coverage_audit.py` L108-L110 `REGISTRY_SOURCE_CHANNEL` 封闭 5 键映射中 get→None | hca 映射 +2 行(**清单外**,生产脚本) | R060/B3-DELIVERY M3 行(同字典+japan_rate_collector→japan,L108-110 恰一邻域,注释自证) |
| 红-2 | `tests/test_p0_baseline_lock_equivalence.py` Z0 L144 `bl.evolution_legal()[0]` | `tests/helpers/baseline_locks.py` L291-L294: `ch=collector_to_channel.get(source)`(L273-L280 硬编码 6 键)→ None/∉`set(rp.SOURCE_FILE_RULES)` → 「无采集通道登记(SOURCE_FILE_RULES缺)」 | 修复簇=①baseline_locks `collector_to_channel` +2 行(**清单外**,测试助手)+②`rp.SOURCE_FILE_RULES`+`jp`/`ea` 键(rp 文件在清单内但 v1.2③ 括注仅 `_AUTHORIZED_COLLECTORS`,**括注歧义待明确**) | R060(同字典同形式,B3 四条目入口;注释 L276-L279 自证) |
| 红-2b | (同上②触发) | `SOURCE_FILE_RULES` 键集(现 5: global/macro/china/rate_economy/japan [实取·运行时])不含 jp/ea——即便授权①字典扩展,ch∉键集仍红(§零.8.3 变体实验证明) | `rp.SOURCE_FILE_RULES` +{jp,ea}(通道身份 jp_/ea_ 前缀+回退窗参数=实现参数,v1.3 预登记) | B3(japan 通道入口即此形态) |
| 红-3 | `tests/test_phase3.py` L216 `src.count('/11') == 11` | v1.2③(b) 授权的 run_weekly 步骤接入(11→13 步)必然改写 N/11 标签 → count≠11 | test_phase3.py 标签锁域化 11→13(**清单外**) | R057「弃字面常量/域化」形态 |
| 红-4 | `tests/test_p01_fix6.py` L342-L355 B 循环(条件: 红-2b 落地后触发) | 循环迭代 `rp.SOURCE_FILE_RULES.items()` 逐通道断言 FALLBACK 构造;`tests/fixt.py` `collector_payloads`(L200-L211)仅产 5 通道文件 → jp/ea 无 fixture 文件 → `sources_status[jp/ea]=MISSING ≠ FALLBACK` → check 失败 | fixt.py +jp/ea 合成 payload(**清单外**)或 B 循环域基线化(**清单外**,test_p01_fix6.py) | R060 REM-AC-02④⑤(fixture japan 通道+篡改循环域基线化,二选一先例形态均在) |

**排除「用授权面 dodge」的路径(已逐一否证)**: ①新条目 source 改挂 `japan_rate_collector`(hca/bl 字典已有)——语义谎报(数据实产自新脚本,违反来源诚实纪律),且 EA 7 条无任何既有采集器可承载;②source 加 `(derived)` 后缀钻 d2 L772 豁免——同上谎报+`R-SOURCE-ENUM` 枚举亦无此值;③12 候选砍到只剩 3 条复用(BOJ_POLICY_RATE≡JP_POLICY_RATE/JGB_10Y/JGB_2Y 复用 B3 既有)——违反 L169 范围「12候选条目」主体;④EA 日历复用 fx/global——日历语义谎报(d2/A6c 镜像虽自适应,fe 日历断言过但口径失实)。

### §零.8.2 v1.2③ 授权面生效性佐证(授权层工作正常——红因恰只在清单外运行态锁)

[实取·§零.8.3 实验输出] 模拟世界(v1.2③ 授权的 rsem/tc/rp 三件扩展全部落地+registry 追加 2 条模拟条目): `rsem.validate_registry` errors=0;`bl.registry_self_consistent` ok=True;A6c 镜像 `KNOWN_CALENDARS==frozenset(MARKETS)` 保持 True(自适应镜像锁 test_p02_w1 L114-L117/test_p02_w1_fix1 L324-L325/test_p03_e2eb_b3 t04 双侧同长即绿);`vintage_additions` 净增恰=新增条目集(t06 域化=授权内)。

**清查为绿/不受影响面(逐件实读登记,实现轮免重复清查)**: test_p03_e2eb_b3 t04/t10(assertIn 自适应)/L238(assertIn japan);test_fact_engine L276(`<=` 子集);test_p01_fix4/fix5/fix6 `vintage_additions` 减法模式(新条目入 additions 即被减去);test_p02_w4 L236(assertGreaterEqual);无 `len(tc.MARKETS)`/`len(SOURCE_FILE_RULES)`/`sources_status` 精确键集锁;无 `data/daily` 文件枚举锁(japan_20261105.json sha 锁 t51/t13 不受新档影响);mapper(e2eb_query_mapper L133-L143 `_search_registry` **首命中**语义)——新条目 append 于 metrics 数组尾则金题 11 绑定/unresolved=[] 不变(实现参数预登记: **新条目一律 append 尾部,禁插中段**)。残余风险如实声明: run_weekly 台账断言(e2e_frozen14/orig14/p01_fix1/fix2 经 mock run_step 消费 main())静态清查未见步数/精确序列锁,但本轮未运行全套件佐证((d) 停止零实现零运行),实现轮 CI 实测兜底。

### §零.8.3 实验: 脚本与输出全文(证据自包含入库;原件 /tmp/p1_wpa_runtime_lock_experiment.py)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-P1-WP-A v1.2轮 情形(d)取证实验(只读仓库,内存monkeypatch模拟,v1.2③授权面全落地后世界)。

目的: 在「v1.2③ 已授权的全部生产镜像扩展都做完」的模拟世界里,证明 WP-A 规格强制
(注册表 85→94 含 9 条新 source 条目)仍使两处**白名单外**运行态锁结构性触红:
  红-1: tests/test_p02_w4.py d2 L773  assertIsNotNone(hca.REGISTRY_SOURCE_CHANNEL.get(source))
  红-2: tests/test_p0_baseline_lock_equivalence.py Z0 L144 经 bl.evolution_legal L291-294
并且白名单内 rp.SOURCE_FILE_RULES 括注不含 jp/ea 时,即使授权 baseline_locks 字典扩展也无法使红-2 转绿。

零仓库写入;零网络;全部断言/输出供 REPORT §零 登记(脚本+输出全文入库)。
"""
import copy
import json
import os
import sys

ROOT = "<DEV根目录>"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "tests"))

import fact_engine as fe                    # noqa: E402
import registry_semantics as rsem           # noqa: E402
import trading_calendar as tc               # noqa: E402
import research_provenance as rp            # noqa: E402
import historical_coverage_audit as hca     # noqa: E402
import helpers.baseline_locks as bl         # noqa: E402

REG_PATH = os.path.join(ROOT, "config", "metric_registry.json")
with open(REG_PATH, encoding="utf-8") as f:
    reg = json.load(f)

# ── 模拟条目: 镜像 B3 JP_POLICY_RATE 字段形态,唯 source=新采集器 ──────────
template = next(m for m in reg["metrics"] if m["metric_id"] == "JP_POLICY_RATE")
def dummy(mid, source, calendar):
    m = copy.deepcopy(template)
    m["metric_id"] = mid
    m["display_name"] = f"模拟{mid}(取证用,不入库)"
    m["source"] = source
    m["calendar"] = calendar
    return m

NEW = [dummy("X_JP_TEST", "jp_market_collector", "japan"),
       dummy("X_EA_TEST", "ea_market_collector", "ea")]
sim_reg = copy.deepcopy(reg)
sim_reg["metrics"].extend(NEW)              # append-at-end(mapper 首命中语义保持)
sim_reg["by_id"] = {m["metric_id"]: m for m in sim_reg["metrics"]}
print(f"[基线] 实载注册表 metrics={len(reg['metrics'])} version={reg['version']} "
      f"| 模拟追加 {len(NEW)} 条(active, source=新采集器) → {len(sim_reg['metrics'])}")

# ── 模拟 v1.2③ 授权面全部落地(生产镜像扩展,内存替换)────────────────────
rsem.KNOWN_SOURCES = frozenset(rsem.KNOWN_SOURCES) | {"jp_market_collector", "ea_market_collector"}
rsem.KNOWN_CALENDARS = frozenset(rsem.KNOWN_CALENDARS) | {"ea"}
tc.MARKETS = tuple(tc.MARKETS) + ("ea",)
_auth = dict(rp._AUTHORIZED_COLLECTORS)
_auth["jp_market_collector"] = {"url": "https://www.boj.or.jp/", "note": "模拟v1.2授权"}
_auth["ea_market_collector"] = {"url": "https://www.ecb.europa.eu/", "note": "模拟v1.2授权"}
rp._AUTHORIZED_COLLECTORS = _auth
print(f"[模拟] rsem.KNOWN_SOURCES +2 → {len(rsem.KNOWN_SOURCES)}; "
      f"KNOWN_CALENDARS +ea → {sorted(rsem.KNOWN_CALENDARS)}")
print(f"[模拟] tc.MARKETS +ea → {len(tc.MARKETS)} markets; "
      f"rp._AUTHORIZED_COLLECTORS +2 → {len(rp._AUTHORIZED_COLLECTORS)} keys")
print(f"[模拟] A6c 镜像(测试自适应形态)保持: "
      f"KNOWN_CALENDARS==frozenset(MARKETS) → "
      f"{rsem.KNOWN_CALENDARS == frozenset(tc.MARKETS)}")

# ── 红-1 复现: test_p02_w4.py d2 L770-777 断言体逐条执行 ──────────────────
print("\n== 红-1 复现: tests/test_p02_w4.py TestDIdentityDriftGuard.test_d2_channel_authority_matrix ==")
print(f"    (L773: assertIsNotNone(hca.REGISTRY_SOURCE_CHANNEL.get(m['source'])) — 白名单外 hca L108-110 未动)")
d2_failures = []
for m in sim_reg["metrics"]:
    ch = hca.REGISTRY_SOURCE_CHANNEL.get(m["source"])
    if "(derived)" not in m["source"] and "(derived)" not in str(m.get("source_symbol")):
        if ch is None:
            d2_failures.append(m["metric_id"])
    if ch not in (None,) + tuple(rp.SOURCE_FILE_RULES):
        d2_failures.append(f"{m['metric_id']}:ch={ch!r}∉SOURCE_FILE_RULES")
print(f"    d2 断言体结果: {'RED' if d2_failures else 'GREEN'}; 触红条目/问题: {d2_failures}")
print(f"    hca.REGISTRY_SOURCE_CHANNEL 键集(白名单外,未动): {sorted(hca.REGISTRY_SOURCE_CHANNEL)}")

# ── 红-2 复现: bl.evolution_legal(注入模拟注册表)──────────────────────
print("\n== 红-2 复现: tests/test_p0_baseline_lock_equivalence.py Z0(L144) 经 bl.evolution_legal ==")
ok, problems = bl.evolution_legal(sim_reg)
print(f"    (白名单外 tests/helpers/baseline_locks.py L273-280 collector_to_channel 未动)")
print(f"    evolution_legal → ok={ok}; problems={problems}")

# ── 变体: 即便授权 baseline_locks 字典扩展,若 rp.SOURCE_FILE_RULES 无 jp/ea ──
print("\n== 变体证明: 假想 baseline_locks collector_to_channel 已+2(仍无 rp.SOURCE_FILE_RULES 扩展) ==")
fake_map = {'global_market_collector': 'global', 'macro_collector': 'macro',
            'china_market_collector': 'china', 'rate_expectations': 'rate_economy',
            'japan_rate_collector': 'japan',
            'jp_market_collector': 'jp', 'ea_market_collector': 'ea'}
known_channels = set(rp.SOURCE_FILE_RULES)
still = [mid for mid, src in ((m["metric_id"], m["source"]) for m in sim_reg["metrics"])
         if src in fake_map and "(derived)" not in src
         and fake_map.get(src) not in known_channels]
print(f"    SOURCE_FILE_RULES 键集(v1.2③括注仅_AUTHORIZED_COLLECTORS,未扩): {sorted(known_channels)}")
print(f"    ch∉SOURCE_FILE_RULES 仍触红条目(Z0 路径 L292-294): {still or '无'}")

# ── 绿面佐证: v1.2 授权的两件 P0-3 测试锁迁移后可绿 + 自洽/枚举全过 ────────
print("\n== 佐证: 模拟世界里 rsem 枚举校验对 9X 条目零 error(即红因不在枚举层) ==")
errs = [p for p in rsem.validate_registry(sim_reg) if p.get("severity") == "error"]
print(f"    validate_registry errors={len(errs)} {errs[:2] if errs else ''}")
ok2, why2 = bl.registry_self_consistent(sim_reg)
print(f"    registry_self_consistent → ok={ok2} {why2 if not ok2 else ''}")
vadd = set(bl.vintage_additions(sim_reg)) - set(bl.vintage_additions(reg))
print(f"    vintage_additions 净增(=授权锁 t06 域化迁移面): {sorted(vadd)}")

# ── '/11' 步标签锁静态佐证 ────────────────────────────────────────────────
src = open(os.path.join(ROOT, "run_weekly.py"), encoding="utf-8").read()
print(f"\n== 静态佐证: tests/test_phase3.py L216 src.count('/11')=={src.count('/11')} "
      f"(现值 11 绿; 步骤 11→13 改标签后≠11 → RED; test_phase3.py 白名单外) ==")
print("\n结论: v1.2③ 授权面全落地后,WP-A 规格仍强制触红 2 白名单外运行态锁(红-1/红-2)"
      "+1 步标签锁(静态)+SOURCE_FILE_RULES 括注歧义(Z0 修复簇必需)。")
```

实验输出(2026-11-05T13:5xZ 实测,`python3 /tmp/p1_wpa_runtime_lock_experiment.py` 退出码 0,原样):

```
[基线] 实载注册表 metrics=85 version=2.1.0 | 模拟追加 2 条(active, source=新采集器) → 87
[模拟] rsem.KNOWN_SOURCES +2 → 9; KNOWN_CALENDARS +ea → ['cn', 'commodity', 'crypto', 'ea', 'fx', 'hk', 'japan', 'us_equity', 'us_rates']
[模拟] tc.MARKETS +ea → 9 markets; rp._AUTHORIZED_COLLECTORS +2 → 8 keys
[模拟] A6c 镜像(测试自适应形态)保持: KNOWN_CALENDARS==frozenset(MARKETS) → True

== 红-1 复现: tests/test_p02_w4.py TestDIdentityDriftGuard.test_d2_channel_authority_matrix ==
    (L773: assertIsNotNone(hca.REGISTRY_SOURCE_CHANNEL.get(m['source'])) — 白名单外 hca L108-110 未动)
    d2 断言体结果: RED; 触红条目/问题: ['X_JP_TEST', 'X_EA_TEST']
    hca.REGISTRY_SOURCE_CHANNEL 键集(白名单外,未动): ['china_market_collector', 'global_market_collector', 'japan_rate_collector', 'macro_collector', 'rate_expectations']

== 红-2 复现: tests/test_p0_baseline_lock_equivalence.py Z0(L144) 经 bl.evolution_legal ==
    (白名单外 tests/helpers/baseline_locks.py L273-280 collector_to_channel 未动)
    evolution_legal → ok=False; problems=["X_EA_TEST:source='ea_market_collector'无采集通道登记(SOURCE_FILE_RULES缺)", "X_JP_TEST:source='jp_market_collector'无采集通道登记(SOURCE_FILE_RULES缺)"]

== 变体证明: 假想 baseline_locks collector_to_channel 已+2(仍无 rp.SOURCE_FILE_RULES 扩展) ==
    SOURCE_FILE_RULES 键集(v1.2③括注仅_AUTHORIZED_COLLECTORS,未扩): ['china', 'global', 'japan', 'macro', 'rate_economy']
    ch∉SOURCE_FILE_RULES 仍触红条目(Z0 路径 L292-294): ['X_JP_TEST', 'X_EA_TEST']

== 佐证: 模拟世界里 rsem 枚举校验对 9X 条目零 error(即红因不在枚举层) ==
    validate_registry errors=0 
    registry_self_consistent → ok=True 
    vintage_additions 净增(=授权锁 t06 域化迁移面): ['X_EA_TEST', 'X_JP_TEST']

== 静态佐证: tests/test_phase3.py L216 src.count('/11')==11 (现值 11 绿; 步骤 11→13 改标签后≠11 → RED; test_phase3.py 白名单外) ==

结论: v1.2③ 授权面全落地后,WP-A 规格仍强制触红 2 白名单外运行态锁(红-1/红-2)+1 步标签锁(静态)+SOURCE_FILE_RULES 括注歧义(Z0 修复簇必需)。
```

(注: 实验以 2 条模拟条目代表 9 条新 source 条目——触红机制按 source 值判定,与条数无关;9 条全触红同理由。)

## §零.9 v1.2 轮冲突登记(情形(d)第二轮)与处置建议

**冲突一句话**: A 行范围「12候选条目…经济体化」+「run_weekly 步骤接入」的诚实实现路径,在 v1.2③ 授权面**全部落地后**的模拟世界里,仍必需链式修改 **5 件 v1.2③ 清单外文件**(`scripts/historical_coverage_audit.py`/`tests/helpers/baseline_locks.py`/`tests/test_phase3.py`/`tests/test_p01_fix6.py`/`tests/fixt.py`)+1 处清单内文件的括注歧义(`rp.SOURCE_FILE_RULES`);绝对禁令④「白名单外一切路径零变更」与验收要点④「全套件零回归」在 v1.2 冻结文本下不可同时满足——按合同 §九(d)「与结构边界矛盾」停止。

**触红链完整性声明**: 本轮清查覆盖 v1.1 轮未及的运行态锁层;§零.8.1 表=清查所得**全部**强制触红项(方法五轴+实验复现),§零.8.2=已逐一实读排除的绿面;残余不确定性(run_weekly 台账断言群)已如实标注。若 v1.3 按 §零.9.1 清单授权,预期无第三轮结构性停止(实现轮 CI 实测兜底最终裁判)。

### §零.9.1 处置建议(v1.3 M 类增量清单,供操作者;全部 R057/R060 既有形态,禁语义弱化)

1. `scripts/historical_coverage_audit.py` L108-L110 `REGISTRY_SOURCE_CHANNEL` +`jp_market_collector→jp`/`ea_market_collector→ea`(R060/B3-DELIVERY M3 同字典同形式先例);
2. `tests/helpers/baseline_locks.py` L273-L280 `collector_to_channel` +同 2 行+注释同步(R060 同字典先例;L276-L279 注释已自证该形态);
3. `scripts/research_provenance.py` 括注明确化: 授权 `SOURCE_FILE_RULES` +`jp`/`ea` 通道(前缀 `jp_`/`ea_`+回退窗参数——建议窗=5,沿 japan 通道 B3 先例;此为红-2 修复簇必要件,非可选);
4. `tests/test_phase3.py` L216 步标签锁域化(`/11`×11→`/13`×13,R057 形态);
5. `tests/fixt.py` +`jp`/`ea` 合成 fixture 或 `tests/test_p01_fix6.py` B 循环域基线化(R060 REM-AC-02④⑤ 先例二选一);
6. (既有授权面确认沿续) `tests/test_p03_e2eb_b3.py` t01/t02/t06 与 `tests/test_p03_final_acceptance.py` t11 域化迁移。

**实现参数预登记(v1.3 可直接采用或修订;全部 [示意·非实取],登记定值即实现值)**: ①P1-P8 规则补读: P8 操作条件读 `calendar=="us_equity"`(R2;唯一使「无规则命中→拒入」负向用例自洽的读法),续登记 P9 `calendar=="japan"→JP`/P10 `calendar=="ea"→EA`(沿 P1/P2 境内日历型规则形态);②market_seat 映射 S1-S4: country_etf_proxy→offshore_proxy/commodity·crypto·fed_futures·fx 族→global/us_equity·us_rates·cn·hk·japan·ea 其余→onshore_local;③12 候选落点: BOJ_POLICY_RATE≡复用既有 JP_POLICY_RATE(同 FRED IRSTCI01JPM156N 概念,禁同概念双注册)/JGB_10Y·JGB_2Y→复用 JGB10Y·JGB2Y/**新注册 9 条** JP_CPI_TOKYO_YOY·NIKKEI225·ECB_DFR·ECB_MRO·BUND_10Y·BUND_2Y·EA_HICP_YOY·DAX·CAC40 → registry **85→94/version 2.2.0/active 93** [示意·推导];④新条目一律 append 于 metrics 数组尾(mapper 首命中语义保持,§零.8.2);⑤run_weekly 步骤=非关键 2 步(jp/ea 采集),11→13 重编号;⑥白名单域内数据源: ECB Data Portal/Bundesbank API/FRED fredgraph/BOJ+MOF(经复用 japan_rate_collector import);DAX/CAC40 如白名单域无源→节点诚实缺席(键不出现,sources_status/alerts 如实,禁 0 占位);JP_CPI_TOKYO_YOY 如 BOJ stat-search 无东京CPI口径→诚实缺席,禁以全国CPI冒充。

### §零.9.2 未被阻断范围要素(沿 v1.1 §零.5.5 如实区分,口径不变)

三字段回填(85 条)/jp_/ea_ 采集脚本与数据档本体/run_weekly 步骤接入本体——三者实现面本轮仍零开发((d) 停止不拆包交付;整包 v1.3 重发后一并实现)。

## §零.10 v1.2 轮 (d) 停止边界声明

- 零开发: v1.2 轮未创建/修改任何代码、测试、registry、run_weekly、workflow、.gitignore;唯一仓库变更=本文件(§零.7-§零.10 追加+文件头状态行更新)。
- 零网络/零 GLM/零凭证/零付费;未写 LIVE;未触 launchd;未触 main;未 force;分支 `dev/p1-impl-a` 线性续加(33d0dfc→本轮登记件提交,零 merge)。
- 实验脚本存 `/tmp/p1_wpa_runtime_lock_experiment.py`(临时件;全文已入 §零.8.3,证据自包含于 git)。
- 排除事项 12 项、AC-01..07 在 v1.2 轮 (d) 停止下均未进入执行面(除 §零.7-§零.9 登记义务);不判 FAIL、不进审计;处置权操作者(v1.3 或停泊,建议清单 §零.9.1)。

# ══ v1.3 轮登记(2026-11-05;分支续作形态 @f0a2aea,§3 步骤3 v1.3④;实现轮)══

## §零.11 v1.3 轮开工核验(步骤0-4 复核,原样登记)

- **步骤0** [2026-11-05T14:04:45Z 实取·开工时点]: `git status` clean;HEAD=f0a2aeae287519d721fd624c021b3d822cdb70ff(=v1.2 轮登记件终态提交)。
- **步骤1 占位符**: 沿 v1.1 §零.3 已实值登记(BASE-P1A=018d913…/BASE-P1A-CI-SUITES=69/BRANCH-SET=41 分支表),v1.3 合同文本实收复核零残留。
- **步骤2 前置实取** [2026-11-05T14:0xZ 实取]: `git ls-remote origin` main=018d913061a2b0ab5680e6c49c544efef740db7e、dev/p1-design=049ec978523dec659ba47f140bf41669604de24f(禁锚 c9626633 未触)、dev/p1-impl-a=f0a2aeae287519d721fd624c021b3d822cdb70ff(与本地一致)。
- **步骤3 分支续作**: 续用既有 `dev/p1-impl-a`,自 f0a2aea 线性续加;零删除/零重建/零 force/零 checkout 重置。
- **步骤4 设计在场核验(复核)**: `git merge-base --is-ancestor 049ec978… HEAD`=exit 0 可达;设计三件双侧 blob 等值(HEAD vs 049ec978): P1_DATA_NEEDS_INVENTORY.md=df79c06f66c368d93159b7a3b46852b6fcb9b196 / P1_DELIVERY.md=314c2644a51f2f575a90253580cb56346e2f93b6 / P1_DESIGN.md=13b263cf3139d420e01bf1e154b03ce85a35db4c(与 v1.1 §零.3 登记值逐值一致)。**无失配。**
- **实现轮附加实读**(实现参数定值依据,全部只读):
  - `.github/workflows/offline-tests.yml` L38: CI 发现面=`tests/test_*.py` 全 glob(test_glm_live 显式排除,L40-42)→ 现役 69 件 [实取·`ls tests/test_*.py | wc -l`=69,2026-11-05] → 目标 **70 slots=69 exit=0+1 SKIPPED**(+tests/test_p1_wp_a.py 恰 1 件新套件)。
  - `config/metric_registry.json` 实况: 85 条/v2.1.0/active 84/deprecated 1(REAL_SHORT);tail 4=JP_POLICY_RATE/JGB2Y/JGB5Y/JGB10Y;asset_class 全集 29 值(含 country_etf_proxy 8/fx_rate 4/fx_index 1/fed_futures 2/crypto 1);calendar 全集 8 值(us_rates 35/us_equity 22/cn 8/commodity 6/fx 5/hk 4/japan 4/crypto 1);country_etf_proxy 8 条 source_symbol=EZU/FEZ/EWU/EWG/EWJ/INDA/FXI/EEM;identity.instrument 模板形态=equity_index→index/policy_rate→macro_series(或 index_rate_series)/rates_yield→index_rate_series/macro_index→macro_series。
  - P1-P10 规则 dry-run 对账 [实取·/tmp/p1a_dryrun_rules.py stdout,2026-11-05,零写入只算]: 85/85 全命中零未命中;**81-vintage 聚合=US 49/CN 10/HK 4/JP 2/EA 4/GLOBAL 12——与 INVENTORY b.1 L57 登记值逐值相等**;live-85 聚合=US 49/CN 10/HK 4/**JP 6**(JP2+JP4[P9])/EA 4/GLOBAL 12;seat 聚合=onshore_local 65/global 12/offshore_proxy 8。
  - `.gitignore` L1 `data/` 全忽略;B3 先例=`data/daily/japan_20261105.json` tracked(显式纳入) [实取·`git ls-files data/`=恰该 1 件;`git check-ignore` 对新路径 jp_20261105.json/ea_20261105.json 报 data/ 规则命中] → v1.3 首档同形态显式纳入。
  - `data/daily` 现役实况: 四通道 20261101-20261104 各 4 件+japan_20261105.json 1 件(采集前 sha256 全量锚定见 §零.14)。
  - `scripts/p03_final_acceptance_run.py`: 「85/v2.1.0」仅存在于注释与打印文本(L68/L71),无运行时计数断言,且非 CI 套件成员——零触碰。
  - `tests/test_p02_w4.py` d2 L773(红-1 触发体): 断言 `hca.REGISTRY_SOURCE_CHANNEL.get(m['source'])` 非空——hca 字典 +2 行后自适应转绿,**测试件零触碰**。

## §零.12 实现参数定值登记(先登记后真实运行,运行后禁回改;锚定源=本文件 §零.9.2[示意·非实取],本节登记定值即实现值)

**① 规则集(P1-P10 终版)**: P1-P8=INVENTORY a.3 L39-L47 逐字;P8 操作读法=**R2**(`calendar=="us_equity"`);补读 P9=`calendar=="japan"→JP`/P10=`calendar=="ea"→EA`(沿 P1/P2 境内日历型形态);无命中→「未归类」拒入待人工裁决(实测 0/85,dry-run 见 §零.11)。

**② market_seat(S1-S4 终版)**: S1 `asset_class=="country_etf_proxy"`→offshore_proxy;S2 `calendar∈{commodity,crypto,fx}`∪`asset_class∈{fed_futures,fx_rate,fx_index}`→global;S3/S4 其余(含 us_equity/us_rates/cn/hk/japan/ea 日历的本币在岸与境内序列、商品ETF[GLD/USO 等美交所上市工具])→onshore_local。

**③ economy_rule 字符串形态**: 短串 `"P{序}:{触发}"`(如 `P5:fx leg JPY=X`/`P6:etf EWJ`/`P9:calendar=japan`;P1/P2/P3/P8-R2/P10 同型 `P1:calendar=cn` 等;P4=`P4:asset_class=fed_futures`;P7=`P7:commodity/crypto`);测试侧独立重编码后按规则序对账。

**④ 12 候选落点(终版)**: 复用 3(BOJ_POLICY_RATE≡JP_POLICY_RATE[同 FRED IRSTCI01JPM156N 概念,禁同概念双注册];JGB_10Y→JGB10Y;JGB_2Y→JGB2Y)+新注册 9 → **registry 85→94 / version 2.1.0→2.2.0 / active 84→93 / deprecated 1 沿(REAL_SHORT)**;新 9 条一律 append 于 metrics 数组尾(mapper 首命中语义保持,§零.8.2)。

**⑤ 新 9 条字段定值表**(全字段镜像既有模板形态;economy/rule/seat 由 ①② 机械结果,不在此重复;identity.adjustment 全=none;status 全=active):

| metric_id | display_name | source | source_symbol | asset_class | freq | unit | calendar | criticality | value_type | identity.instrument | validation.range | validation 周限 | freshness.max_lag_days |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| JP_CPI_TOKYO_YOY | 东京都CPI同比 | jp_market_collector | PENDING | macro_index | monthly | percent | japan | important | level | macro_series | [-2,15] | — | 60(note:月频) |
| NIKKEI225 | 日经225指数 | jp_market_collector | NIKKEI225 | equity_index | daily | index_point | japan | important | level | index | [5000,60000] | max_week_pct_move 25 | 5 |
| ECB_DFR | 欧央行存款便利利率 | ea_market_collector | FM.B.U2.EUR.4F.KR.DFR.LEV | policy_rate | daily | percent | ea | important | level | macro_series | [-1,15] | max_week_abs_move 1.0 | 10 |
| ECB_MRO | 欧央行主要再融资利率 | ea_market_collector | FM.B.U2.EUR.4F.KR.MRR_FR.LEV | policy_rate | daily | percent | ea | important | level | macro_series | [-1,15] | max_week_abs_move 1.0 | 10 |
| BUND_10Y | 10年期德国国债收益率 | ea_market_collector | WU3146 | rates_yield | daily | percent | ea | important | yield_or_spread_level | index_rate_series | [-0.5,15] | max_week_abs_move 1.0 | 7 |
| BUND_2Y | 2年期德国国债收益率 | ea_market_collector | WU3141 | rates_yield | daily | percent | ea | important | yield_or_spread_level | index_rate_series | [-0.5,15] | max_week_abs_move 1.0 | 7 |
| EA_HICP_YOY | 欧元区HICP同比 | ea_market_collector | ICP.M.U2.N.000000.4.ANR | macro_index | monthly | percent | ea | important | level | macro_series | [-2,15] | — | 60(note:月频) |
| DAX | 德国DAX指数 | ea_market_collector | PENDING | equity_index | daily | index_point | ea | important | level | index | [1000,40000] | max_week_pct_move 25 | 5 |
| CAC40 | 法国CAC40指数 | ea_market_collector | PENDING | equity_index | daily | index_point | ea | important | level | index | [1000,10000] | max_week_pct_move 25 | 5 |

- `source_symbol=PENDING` 三义(JP_CPI_TOKYO_YOY/DAX/CAC40): 白名单五域无诚实口径源(见 ⑩诚实缺席),calc 字段如实登记口径与缺席理由;**PENDING≠编造源**;BUND_2Y `WU3141`=候选键(BBK01 收益率曲线残存期限 1-2 年档),运行时核口径,不符→数据档诚实缺席(条目身份保留)。
- release_semantics 各条如实登记(ECB=管委会决议日生效当日更新系列;Bundesbank=每营业日;FRED NIKKEI225=次日更新东京收盘;Eurostat HICP=次月中旬终值;PENDING 三条=口径源未接线,按缺席纪律处理)。

**⑥ 三字段回填面与终态聚合**: 全部 94 条(85 既有+9 新)回填 economy/economy_rule/market_seat(字段序插于 `calendar` 后);终态聚合 **US 49/CN 10/HK 4/JP 8/EA 11/GLOBAL 12=94** [示意·推导=85 实测聚合+P9×2+P10×7];seat 终态=onshore_local 74/global 12/offshore_proxy 8;top-level `version`="2.2.0"+`field_semantics` 增 economy/economy_rule/market_seat 三字段语义文档+`notes` 增 v2.2.0 版本纪要 1 行(同文件 (a) 授权面)。

**⑦ run_weekly 步骤接入**: 步骤列表尾追加 2 步,标签定值 `12/13 日本市场数据采集(jp_)`(脚本 jp_market_collector.py)/`13/13 欧元区市场数据采集(ea_)`(脚本 ea_market_collector.py),均非关键;既有 11 步标签 `/11`→`/13` 全量重编号(1/13…11/13);`_critical_collectors` 4 集零变化。

**⑧ 通道登记链定值**: `rp.SOURCE_FILE_RULES` +`"jp": {"prefix": "jp_", "max_fallback_days": 5}`/`"ea": {"prefix": "ea_", "max_fallback_days": 5}`(沿 japan 通道窗);`rp._AUTHORIZED_COLLECTORS` +`jp_market_collector`/`ea_market_collector`(A6c 双侧镜像同步 `rsem.KNOWN_SOURCES` +同 2 值);`tc.MARKETS` +`ea`,`is_trading_day` ea 分支=japan 同款(非 `01-01`/`12-25` 即交易日),日历注册表 docstring +ea 行;`hca.REGISTRY_SOURCE_CHANNEL` +2 行(jp_market_collector→jp/ea_market_collector→ea);`bl.collector_to_channel` +同 2 行+注释同步。**D7 边界保持**: `rp._SOURCE_TO_INPUT` 不加 jp/ea 键(无映射→noncore_missing_boundary 诚实记录,门禁面零变化;`rp.SOURCE_CHANNELS` 冻结 4 通道零变化;b3-t14「无 japan 键」断言形态沿续覆盖 jp/ea)。

**⑨ vintage/测试锁域化定值**: `bl.BASELINE_VINTAGE_IDS` 81 冻结零变化;`vintage_additions` 终态 4→13(JP4∪NEW9);b3-t06 期望=该 13 id 集;b3-t01=94/93/"2.2.0";b3-t02 四条目期望 dict 各+3 字段(JP_POLICY_RATE=JP/`P9:calendar=japan`/onshore_local;JGB2Y/JGB5Y/JGB10Y 同 P9/JP/onshore_local);final-t11=94/"2.2.0"/93;test_phase3 L216=`src.count('/13') == 13`;fixt 选择((k) 二选一)=**tests/fixt.py** +jp/ea 合成 payload(值全发明,镜像 a-2 嵌套节结构;test_p01_fix6.py B 循环零改动自动覆盖新通道 FALLBACK,**test_p01_fix6.py 零触碰**)。

**⑩ 白名单域数据源 URL 定值(jp_/ea_ 首档目标日=20261105)**:
- jp_ 通道: MOF jgbcme 曲线(复用 `japan_rate_collector.MOF_JGBCME_URL` import)→jgb 节;FRED IRSTCI01JPM156N(复用 `FRED_POLICY_URL`)→policy_rates.BOJ_POLICY_RATE;FRED fredgraph csv `?id=NIKKEI225`(fred.stlouisfed.org)→prices.NIKKEI225。
- ea_ 通道: ECB Data Portal(data-api.ecb.europa.eu)FM.B.U2.EUR.4F.KR.DFR.LEV/FM.B.U2.EUR.4F.KR.MRR_FR.LEV(日频)→policy_rates;ICP.M.U2.N.000000.4.ANR(月频)→inflation.EA_HICP_YOY;Bundesbank API(api.bundesbank.de)BBK01/WU3146→BUND_10Y、BBK01/WU3141→BUND_2Y(候选键运行时核口径,不符→该节诚实缺席)。
- **诚实缺席定值**(数据档键不出现,禁 0 占位;sources_status/alerts 如实;=⑤PENDING 三条的数据面): DAX/CAC40(yfinance 不入依赖面[v1.1② 冻结],白名单五域无指数口径源)/JP_CPI_TOKYO_YOY(东京CPI口径唯 stat.go.jp 发布,非白名单域,禁全国CPI冒充)。
- 数据档结构=`DESIGN §三(a-2) L45-L58` 逐字(顶层 date/generated_at/sources_status;jp_ 节 policy_rates/jgb/inflation/prices;ea_ 节 policy_rates/bund/inflation/prices;任何节缺席→键不出现)。

**⑪ 采集器 payload 形态**: 顶层=**a-2 逐字**(`date`/`generated_at`/`sources_status`[逐源 {status,retrieved_at},状态词汇沿 rp.SOURCE_STATUSES 语义: EXACT/READ_FAIL/MISSING]+通道节 `policy_rates`/`jgb`|`bund`/`inflation`/`prices` 直接挂顶层)+观测性附加键 `observations`(逐系列观测日,B3 纪律形态)/`sources`(逐源 url 口径)/`fetched_at`/`alerts`(诚实降级记录;附加键不与 a-2 冲突,a-2 未禁增);行情节 `series`=近端观测序列(窗口对齐既有 global 档实况,实现时实读取样定窗,禁编造历史);`prev_value`=源端次新观测(不可得→null);NIKKEI225 `high`/`low`=FRED 该系列仅收盘口径→**null(非 0)**。失败纪律=源失败→节键不出现+sources_status 该源 READ_FAIL+alerts 登记,禁 0 占位(L58);全节缺席→exit 1 不产空壳(B3 同款);离线测试(要点③)以注入 raw 验证失败→READ_FAIL/节缺席形态,零网络。

## §零.13 v1.3 白名单终版登记(A 行 7+M 行 12 授权[其中 (c) 条件类未触发零触碰]→M 实改 11 件)

| # | 路径 | A/M | 授权项 | DESIGN 依据(行号) |
|---|---|---|---|---|
| 1 | docs/P1_WP_A_REPORT.md | A(已在场续笔) | 必含件 | 附录A §零(ii);v1.1/v1.2 轮已建,本轮 §零.11-§零.14 续笔 |
| 2 | docs/P1_WP_A_DELIVERY.md | A(新建) | 必含件 | 附录A §零(ii);含代码必含 DELIVERY |
| 3 | scripts/jp_market_collector.py | A(新建) | §四 L124 | 「新增 scripts/jp_market_collector.py(候选名)」+L169 范围「jp_/ea_ 采集脚本」 |
| 4 | scripts/ea_market_collector.py | A(新建) | §四 L124 | 同上 |
| 5 | tests/test_p1_wp_a.py | A(新建) | 含代码必含 | L169 验收要点①③ |
| 6 | data/daily/jp_20261105.json | A(新建,显式纳入) | v1.1④ 豁免 | L169 验收要点②「首份 data/daily/jp_/ea_YYYYMMDD.json 真实档在场」 |
| 7 | data/daily/ea_20261105.json | A(新建,显式纳入) | v1.1④ 豁免 | 同上 |
| M-a | config/metric_registry.json | M | v1.2③(a)/v1.1③(a) | L169「registry 三字段回填与12候选条目」+§三(a-1) L37-L43/§三(a-3) L62 |
| M-b | run_weekly.py | M | v1.2③(b)/v1.1③(b) | L169「run_weekly 步骤接入」+§四 L124 |
| M-c | scripts/japan_rate_collector.py | **M 条件类未触发,零触碰** | v1.2③(c)/v1.1③(c) | §四 L124 要求「新增」独立脚本;复用调用(fetch import)优先于扩展 |
| M-d | scripts/registry_semantics.py | M | v1.2③(d) | KNOWN_SOURCES 扩容+A6c 镜像(通道登记链,B3 合同范围实证) |
| M-e | scripts/research_provenance.py | M | v1.2③(e)+v1.3③(i) | _AUTHORIZED_COLLECTORS 登记+SOURCE_FILE_RULES +{jp,ea}(括注明确化) |
| M-f | scripts/trading_calendar.py | M | v1.2③(f) | MARKETS/CALENDARS 增 ea(通道登记链) |
| M-g | scripts/historical_coverage_audit.py | M | v1.3③(g) | REGISTRY_SOURCE_CHANNEL +2 行(R060 M3 同字典先例;红-1 修复) |
| M-h | tests/helpers/baseline_locks.py | M | v1.3③(h) | collector_to_channel +2 行+注释同步(R060 先例;红-2 修复簇①) |
| M-j | tests/test_phase3.py | M | v1.3③(j) | L216 步标签锁域化 /11×11→/13×13(R057 形态;红-3 修复) |
| M-k | tests/fixt.py | M | v1.3③(k)二选一 | +jp/ea 合成 payload(R060 REM-AC-02④ 先例;红-4 修复;test_p01_fix6.py 零触碰) |
| M-锁1 | tests/test_p03_e2eb_b3.py | M | v1.2③(a) 从属锁+v1.3 增 t06 | t01/t02/t06 registry 计数/冻结/增集锁域化(R057/R060 形态,禁语义弱化) |
| M-锁2 | tests/test_p03_final_acceptance.py | M | v1.2③(a) 从属锁 | t11 registry 计数锁域化(同上) |

- 结构约束预检: A 行新建 5 件(REPORT/DELIVERY/双采集器/test_p1_wp_a)与 `git ls-files` 零重合 [实取·2026-11-05];jp_/ea_ 首档路径无同名在场件;必含件齐;含代码件含对应 tests。**清单外白名单外路径零变更**(AC-05.1)。

## §零.14 v1.3 轮纪律声明(实现轮;运行后终笔复核)

- **零网络边界**: 网络仅步骤⑪真实采集运行时、仅白名单五域(boj.or.jp/mof.go.jp/fred.stlouisfed.org/ecb.europa.eu/bundesbank.de;ECB Data Portal/Bundesbank API 属 ecb.europa.eu/bundesbank.de 域);采集前 `data/daily` 全量 sha256 锚定,运行后既有档哈希零变化登记。
- **零 GLM/零凭证/零付费;LIVE 禁写;launchd 零触碰;main 零触碰;分支唯 dev/p1-impl-a 线性零 merge;禁 reset --hard/force/amend 已推提交。**
- jp_/ea_ 首档 `git add -f` 显式纳入(`.gitignore data/` 规则下,B3 japan_20261105.json 同形态先例)。
- 本节 §零.12 定值先登记后运行,运行后禁回改;任何偏离=情形(b)/(d) 如实上报,不以调参换绿。
- 测试纪律: 新测试零网络/合成 fixture 唯一数据源/期望值硬编码字面量(禁自证);离线测试禁冒充真实金融数据。

## §零.15 (d) 停止#3 登记(验收要点④唯一红=N3d 清单外锁;处置建议供操作者,非自决)

**停止形态**: v1.3 授权面(A7[数据档 2 未产]+M11)全部落地,本地 CI 镜像 offline-tests(70 slots=68 exit0+1 skipped[test_glm_live]+1 红)。唯一红=`tests/test_p0_baseline_lock_equivalence.py`(清单外文件,AC-05 禁触碰)→ 按合同序(⑨ CI 门→⑪ 真实采集),要点②真实采集与 jp_/ea_ 首档落盘联动未启动。**情形(d)停止#3: 仅登记,处置供操作者。**

- **N3d 机理(唯一真实阻塞)**: 该文件 `n3d_table_rows()` 注入 `range(expected_registry_count()-4)` 行——live=94 时注入 rows=90 ≥ `W4_REPORT_ROWS_FLOOR`(82,冻结锚)→下限锁不咬合,T2 精确锁红而双联锁失败: 提交后复跑实测 `❌ N3d 逐项表行数缩水(缺表头+4行): T2行数==1+实载红且下限锁红(丢行捕获) rows=90 expect=1+94`。R060 先例=live 81→85 时同款锚迁移一次(「缺表头」→「缺表头+4行」,该函数 docstring 自证);v1.3 85→94 为同构情形。**v1.4 建议: 该文件 n3d 注入算术一行域化(锚改 floor−1 或 live 自适应缺行数,R060 重锚同形态,非语义弱化)**。v1.2 轮 §零.8.1「全部强制触红项」清查对该项**漏报,如实更正**(当时实验只覆盖 d2/evolution_legal/步标签/fixt 四簇,未触 N3d 注入算术)。
- **R[legal85] 提交序工件(非阻塞,已验证自愈)**: 预演 worktree 取 committed HEAD——未提交态下旧代码+新注册表世界结构性红;本地提交 7c179d9(代码与注册表同提交原子一致)后复跑: `R[legal85] 合法演进(实载85+4虚构=89项): M集28套件零改动全绿` ✅。
- **R-还原 红(自致工件,已清除)**: 提交前 CI 运行时 `/tmp/p1a-wt-diag` 诊断用 worktree 未移除致 `git worktree list` 计数≠1 触红;提交前 `git worktree remove --force` 清除,复跑 `R-还原 worktree清单回零` ✅。
- **复跑终态(提交 7c179d9 后)**: `等价套件结果: 30通过 / 1失败`(唯一失败=N3d,见上);log=`/tmp/p1-wp-a-evidence/equiv-post-commit.log`(证据随停止形态入库 ci-summary 旁)。
- **如更正登记**: 提交 7c179d9 message 内记「28通过/2失败」,提交前 CI 实录为 28通过/3失败(第三项=R-还原,自致工件已于提交前清除故未列入 message 两因);历史不 amend,以本节实录为准。提交前全量矩阵=`/tmp/p1-wp-a-evidence/ci-summary.txt`(TOTAL_SLOTS=70, RED=1)+ci-logs/ 逐套 log。
- **要点②联动未启动(如实)**: 采集器就绪+源 URL 定值(§零.12⑩);v1.4 授权 N3d 一行后,同轮执行步骤⑪(白名单五域真实采集)+A6/A7 首档 `git add -f`(§零.14)。

## §零.16 v1.4 轮开工核验与定值登记(合同=IA-P1-WP-A-AC-v1.4;先登记后实现后运行,运行后禁回改)

**开工核验(步骤0-4 复核,原样登记,2026-11-05T15:36:00Z [实取·本机 date -u])**:

- 步骤0: `git status` clean,已在 `dev/p1-impl-a`,HEAD=65cf32f49e84b3541b8aa20db705115d0402805b(v1.3 轮终态=实现笔 7c179d9+登记笔#3 65cf32f)。
- 步骤1: 三占位符已实值化(BASE-P1A=018d913…/CI-SUITES=69→本轮目标 70 槽/BRANCH-SET=41 分支表),§0 生效前置信号满足(冻结章 v1.4 处置章在场)。
- 步骤2: `git ls-remote origin main`=018d913061a2b0ab5680e6c49c544efef740db7e ✓;`dev/p1-design`=049ec978523dec659ba47f140bf41669604de24f 全值一致 ✓(禁锚 c9626633 未触);`dev/p1-impl-a`=65cf32f49e84b3541b8aa20db705115d0402805b=本地 HEAD ✓(v1.4③ 分支续作@65cf32f 形态)。
- 步骤4 设计在场核验: `git merge-base --is-ancestor 049ec978… HEAD`=exit 0 ✓;设计三件 blob 双侧等值 [实取·git ls-tree]: P1_DATA_NEEDS_INVENTORY=df79c06f66c368d93159b7a3b46852b6fcb9b196/P1_DELIVERY=314c2644a51f2f575a90253580cb56346e2f93b6/P1_DESIGN=13b263cf3139d420e01bf1e154b03ce85a35db4c(HEAD 侧=049ec978 侧逐一相同,与冻结章实读记录一致)。
- 步骤5-6: 规格抄录(§零.1)与白名单终版(§零.13)为 v1.3 轮已登记实体,本轮复核在场无漂移;本轮白名单增量=**v1.4③(l) 单点**: `tests/test_p0_baseline_lock_equivalence.py` **仅限 n3d 注入算术域化(该套件其余断言零触碰)**——M 行新增 1 件(累计 M 实改 11→12 件)。

**N3d 域化定值登记(登记型,先登记后改后运行)**:

- **二选一定值=「floor−1」**: 注入算术 `range(bl.expected_registry_count() - 4)` → `range(bl.W4_REPORT_ROWS_FLOOR - 1)`=81 行 [实取·tests/helpers/baseline_locks.py L45: W4_REPORT_ROWS_FLOOR=82]。
- **选 floor−1 弃 live 自适应缺行的理由**: ①81 与 R060 迁移后锚值(live85 count−4=81)数值连续,「live 81→85 同型」=迁移后注入行数保持 81 不变,本定值沿该型;②锚定冻结常量 `W4_REPORT_ROWS_FLOOR`(82),与 live registry 演进解耦,live 再扩容不再触红(R014-D3 硬编码预期随数据档演进漂移教训);live 自适应公式(如 `count-(count-floor)-1`)数值等价但公式绑 live,复杂度无收益。
- **双咬合验证算术(登记)**: rows=81: T2 精确锁 81≠1+live(94→95)咬合 ✓;下限锁 not(81≥82)=True 咬合 ✓——双联锁条件表达式**零改动**,语义不弱化(禁弱化判据=check 的两个条件子式逐字保持)。
- **同步面(数值标注与本体同步纪律,R014 教训)**: n3d_table_rows() docstring 追加 v1.4 二迁注记+check 描述文字「(缺表头+4行)」→「(floor−1=81行)」——描述与注入算术一体同步,不触该套件其余任何断言函数。

**v1.4 续段范围登记(合同 v1.4 修正面②,按序)**:

N3d 域化 → 要点②真实采集(A6/A7 jp_/ea_ 首档;白名单五域;源失败→MISSING 不填 0;诚实缺席三项照 §零.12⑩ 预登记[DAX/CAC40/JP_CPI_TOKYO_YOY])→本地 CI 全绿(70 槽=69 exit0+1 skip)→证据 zip 八类(§3 步骤12)→终笔推送。采集运行前 `data/daily/` 全量+`data/research/` 既有档案 sha256 锚定,运行后既有哈希一律不变(§3 步骤10);首档 `git add -f` 显式纳入(§零.14)。

### §零.16.1 v1.4 实录(终态;全部 [实取·运行输出/日志],证据=/tmp/p1-wp-a-evidence/)

**① N3d 域化落地与验证**: 改动=`tests/test_p0_baseline_lock_equivalence.py` n3d_table_rows() 内 3 处行内(docstring 追加 v1.4 二迁注记/注入算术一行 `range(bl.W4_REPORT_ROWS_FLOOR - 1)`/check 描述文字同步),**该套件其余断言函数零触碰**(diff 可复核)。验证: 等价套件复跑 **31通过/0失败**(v1.3 轮 30/1,唯一红=N3d → 本轮修复;输出见本节尾注)。负向敏感性算术验证(n3d-sensitivity-check.log): 旧锚 count−4=90→bite=False(红);新锚 floor−1=81→bite=True(咬合);weakened(90)=True 反证=下限锁子式若删则旧锚也咬合=语义弱化——本 diff 条件子式逐字保持,未弱化。v1.3 轮红实录(equiv-post-commit.log `rows=90 expect=1+94`)=同断言域化前负向证据。

**② 真实采集实录(要点②;白名单五域零凭证零付费)**:

- **jp_ 通道(1 次运行,全源成功)**: exit 0,写出 `data/daily/jp_20261105.json`(4 系列)。MOF_JGBCME=EXACT(jgb.JGB_10Y=2.855@2026-11-04 prev 2.817/jgb.JGB_2Y=1.891@2026-11-04 prev 1.880);FRED_POLICY=EXACT(policy_rates.BOJ_POLICY_RATE=1.043@2026-09-01 prev 0.977,月频观测);FRED_NIKKEI225=EXACT(prices.NIKKEI225 close=61077.9@2026-11-05,high/low=null 仅收盘口径,series=251 点);inflation 节键不出现(JP_CPI_TOKYO=MISSING 诚实缺席,alerts 如实)。log=jp-collector-run-attempt1.log。
- **ea_ 通道(2 次尝试,零改参,全部如实记录)**: attempt1(15:42)exit 0 写出: ECB_FM_DFR=EXACT(obs=2026-09-16,**数值不可考**——该档随后被 attempt2 原子覆盖,仅 log 留 observations 观测日)/ECB_FM_MRO=504 READ_FAIL/BBK_WU3146·WU3141=Connection reset READ_FAIL/ECB_ICP_HICP=504 READ_FAIL(1 系列);attempt2(15:43-15:45,零改参重试=瞬时网络错误恢复非调参凑结果)exit 0 写出(覆盖 attempt1): ECB_FM_MRO=EXACT(MRO 2.65@2026-09-16 prev 2.4)/其余同 504/reset READ_FAIL(1 系列)。终态档=`data/daily/ea_20261105.json`(policy_rates.ECB_MRO 在场;bund/inflation/prices 节键不出现;DAX/CAC40=MISSING 诚实缺席;alerts 9 条如实)。ECB FM 端点呈轮换性 504(两次各恰一个 FM 系列成功),BBK 持续 connection reset——**服务端瞬时/限流形态,如实 READ_FAIL,不再重试凑全**。log=ea-collector-run-attempt1.log/ea-collector-run-attempt2.log。
- **锚定对比(§3 步骤10)**: 运行前 anchor-data-daily-pre.txt(25 件,sha256=2469381439a127494c882f7a51a42df98b8b04eb780fab9f9801571f67c2e7cd)vs 运行后 anchor-data-daily-post.txt: diff 仅 2 行新增(ea_20261105.json=e6db3ddf…/jp_20261105.json=7f0bdeb1…),**既有 25 件哈希一律不变**;data/research 13 件 pre/post 逐字节一致零变化。

**③ 本地 CI 全绿(要点④)**: 与 `.github/workflows/offline-tests.yml` L34-57 同构镜像(run_ci_v14.py),**70 slots=69 exit=0+1 SKIPPED(test_glm_live 设计性)+FAILFLAG=0**(15:47:07Z-15:49:03Z)。关键套件: test_p0_baseline_lock_equivalence=exit 0(N3d 修复)/test_p1_wp_a=exit 0/从属锁套件(test_p03_e2eb_b3/test_p03_final_acceptance/test_phase3/test_p01_fix6)全绿。summary=ci-summary-v14.txt,逐套件 log=ci-logs-v14/。

**④ §5.3 六项自检(本轮新增数值清单,双文档扫描)**: 等价套件 31/0 [实取·运行输出];CI 70=69+1skip+FAILFLAG0 [实取·ci-summary-v14.txt];jp 4 系列数值 [实取·data/daily/jp_20261105.json];ea 1 系列+4 READ_FAIL+2 MISSING [实取·data/daily/ea_20261105.json];锚定 25→27 与 research 13 不变 [实取·diff anchor-pre/post];N3d 新锚 floor−1=81 [实取·tests/helpers/baseline_locks.py L45=82];改动文件数=3(tests/test_p0_baseline_lock_equivalence.py+data/daily/jp_+ea_ 两档)+文档 2 件(REPORT/DELIVERY 续笔);ea 尝试次数=2 [实取·两 attempt log]。全部 [实取] 项已回工作树复核;日期/SHA 出圈边界=本报告头部声明。清单本身入证据包(§5.3 第 6 项)。

### §零.16.2 v1.4 取证与 zip 登记(终态;全部 [实取·命令输出],原样件=/tmp/p1-wp-a-evidence/ 与 zip ③)

- **AC-05 全量 diff 判据**: `git diff --name-status 018d913..HEAD`=**A 恰 7**(REPORT/DELIVERY/jp_/ea_ 采集器/test_p1_wp_a/jp_+ea_ 两档)+**M 恰 12**(registry/run_weekly/rsem/rp/tc/hca/baseline_locks/test_phase3/fixt/b3/final/**test_p0_baseline_lock_equivalence**)+**D=0**;japan_rate_collector.py(M-c 条件类)零触碰。
- **分支历史**: 纯线性 5 笔(33d0dfc→f0a2aea→7c179d9→65cf32f→0c28e96+终笔),零 merge;reflog-20 零 reset/amend;不 force;main 零触碰。
- **BRANCH-SET 对照(41 冻结分支)**: **41/41 尖端语义零漂移+唯一新增分支=dev/p1-impl-a** ✓;**如实登记 3 处冻结章文本 vs ls-remote 实取的一位字符差异**: dev/p0-2-w5-emwin(章 `…a38fc75d`/实取 `…a88fc75d`)、dev/p0-2-w5-fix2(章 `…75b1d`/实取 `…75c1d`)、dev/p3-design(章 `f93adb5d033e…`/实取 `f93adb5d0338…`)——各恰 1 个十六进制位不同;git SHA 为密码学哈希,真实提交推进不可能恰差一位(概率≈10⁻⁴⁶),判定=**冻结章文本层单字符笔误**(R059 轮 dev/p0-2-w2 合同一位笔误重核先例同型),非尖端漂移;处置权留操作者复核。
- **LIVE 隔离**: LIVE `real_data_acceptance.py` sha256=f9ca189c5248199bb5acbc78b2a2c82d59c10e1c7c2c2d20bdaaa6105fbfe3eb(合同 AC-05.6 断言 f9ca189c… 前缀一致);LIVE 目录本轮标记 grep(`R044|P1-WP-A|IA-P1-WP-A`)=零命中;LaunchAgents 零改动。
- **证据 zip(AC-06.2)**: IA-P1-WP-A-EVIDENCE.zip=134 成员/578676 字节/sha256=a4d7b439bc9fd2a4cf067233d9024075692736fc8c186bf0489471b2b6df1c88(装配 2026-11-05T15:57:33Z,TIP=0c28e96);八类最低集齐(①spec 抄录+清单 ②19 件双源副本交叉哈希 0 失配 ③git 取证+设计在场核验+LIVE sha ④CI 70 套件+等价 31/0+敏感性 ⑤映射表+DP 登记 ⑥3 采集 log+双面锚定 4 件 ⑦自述副本 ⑧SHA256SUMS zip 外自指豁免);zip sha 落 DELIVERY §六;推送终态=证据目录 08-sidecar/final-state.txt。
- **CI dispatch**: 未自行 dispatch(合同 §六.5);登记件将落 `rounds/044/P1-WP-A-CI-dispatch-evidence.md`(操作者 CHECKPOINT 面)。
- **顺序偏离如实(合规补救)**: v1.4 续段合同序=「…zip 八类→终笔推送」;实现笔 0c28e96 因 zip sha 须落 DELIVERY 而先于 zip 装配推送→补救=R023/R060 先例形态(zip 装配内件=TIP 0c28e96 版→DELIVERY 补记 zip sha=本终笔提交,zip 内副本自指豁免);纯线性续加零 amend。
