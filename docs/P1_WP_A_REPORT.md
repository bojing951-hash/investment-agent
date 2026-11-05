# IA-P1-WP-A REPORT(登记件 · 情形(d)停止)

> 包: IA-P1-WP-A(P1 四经济体底图层实现包第 1 包/族首包)| 分支: `dev/p1-impl-a`(自 018d913061a2b0ab5680e6c49c544efef740db7e 切出)
> 合同: IA-P1-WP-A-AC-v1.1(FROZEN 2026-11-05 21:1x HKT 操作者代批)
> **状态: 情形(d)规格冲突合法停止——仅登记件执行,零开发**(合同 §九(d)、§3 步骤5/§零(iv);不判 FAIL、不进审计,处置权操作者)
> 停止时刻: 2026-11-05T13:1xZ(UTC)[实取·本机 date -u,开工 2026-11-05T13:13:58Z]
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
