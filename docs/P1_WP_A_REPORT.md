# IA-P1-WP-A REPORT(登记件 · 情形(d)停止)

> 包: IA-P1-WP-A(P1 四经济体底图层实现包第 1 包/族首包)| 分支: `dev/p1-impl-a`(自 018d913061a2b0ab5680e6c49c544efef740db7e 切出)
> 合同: IA-P1-WP-A-AC-v1.1(FROZEN 2026-11-05 21:1x HKT 操作者代批)→ **v1.2(FROZEN 2026-11-05 操作者发车,§3 步骤3=分支续作形态 @33d0dfc)**
> **状态: 情形(d)规格冲突合法停止——v1.1 轮(§零.1-§零.6)+ v1.2 轮(§零.7-§零.10)两轮登记,均仅登记件执行,零开发**(合同 §九(d)、§3 步骤5/§零(iv);不判 FAIL、不进审计,处置权操作者)
> 停止时刻: v1.1 轮 2026-11-05T13:1xZ / v1.2 轮 2026-11-05T13:57:07Z(UTC)[实取·本机 date -u;v1.2 轮开工 2026-11-05T13:3xZ]
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

ROOT = "/Users/cast/investment-agent-dev"
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
