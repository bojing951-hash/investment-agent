# IA-P1-WP-B REPORT — 事实引擎与快照贯通(第2实现包)

- 角色: 执行Agent(合同 IA-P1-WP-B-AC-v1.1, FROZEN 2026-11-06 00:3x HKT)
- 基线: BASE-P1B = f6d0beb7cdba8631c9df6a20a2e9a5e6140c1c20(main@启动时点, 实读核实)
- 分支: dev/p1-impl-b(自 BASE-P1B 创建; 禁锚 c9626633 非祖先已核)
- 本 REPORT 遵守「先登记后实现」纪律: §零.1–§零.11 为实现前登记(实现参数全部先于此落笔),
  §零.12 起为实录节(实现后回填, 禁回改前节)。

---

## §零 登记节

### §零.1 契约锚与启动核验实录

| 项 | 值 | 核验方式 |
|---|---|---|
| 契约 | IA-P1-WP-B-AC-v1.1(FROZEN 2026-11-06 00:3x HKT) | 操作者注入全文,逐节实读 |
| BASE-P1B | f6d0beb7cdba8631c9df6a20a2e9a5e6140c1c20 | `git rev-parse HEAD` 于 dev/p1-impl-b = 同值 |
| 分支 | dev/p1-impl-b(自 f6d0beb 直接创建,零合并) | `git branch --show-current` + log 线性 |
| 禁锚 | c9626633 不得为祖先 | ~~merge-base 核验非祖先~~ **措辞失实, 更正见 §零.16.3**: c9626633 实为 BASE-P1B 自身的历史祖先; 正确核验=merge-base(dev/p1-impl-b, main)=f6d0beb=BASE-P1B ✓(分支基点正确) |
| BRANCH-SET | 42分支冻结表,唯一预期新增=dev/p1-impl-b | 实现后 ls-remote 对照(§零.16) |
| 工作树 | 启动时干净(status clean) | `git status --short` 空 |

### §零.2 规格转写(P1_DESIGN.md §六 L170, 逐字)

转写源: docs/P1_DESIGN.md(blob 13b263cf)第 170 行,VERBATIM:

```
| WP-P1-B 事实引擎与快照贯通 | 新通道进引擎与快照,缺席合法登记 | normalize_jp/ea、jp/ea 日历、build_all/resolve_inputs 扩展、Gate A 对新指标裁决 | WP-A | ① 单测: 新通道事实构造+口径(week/MTD/YTD 对 jp/ea 日历)+数据不足路径【测试】② 快照 sources_status 含 jp/ea 键的构建测试(含缺源 MISSING)【测试】③ 既有 US 面输出零回归(W-3 对照)【测试/CI】 |
```

> 转写勘正披露(v1.2 处置章整改授权项1, 2026-11-05T17:50Z): 本节转写原将 DESIGN L170 范围列的半角逗号误录为全角逗号(恰逐字块与下方四要素表"工作内容"行两处域), 原为全角已勘正为半角, 现与 DESIGN 原文(blob 13b263cf)逐字一致; 勘正依据=rounds/045 首审 FAIL 阻断项+处置章 v1.2 授权项1。

四要素分解:

| 要素 | 内容 | 本包处置 |
|---|---|---|
| 名称 | WP-P1-B 事实引擎与快照贯通 | 本 REPORT 主题 |
| 工作内容 | 新通道进引擎与快照,缺席合法登记 | 引擎面=normalize_jp/ea+build_all 扩展(实现);快照面=resolve_inputs/sources_status(WP-A 已交付,本包测试证成);缺席合法登记=Gate A 边界裁决实录(测试证成) |
| 技术要点 | normalize_jp/ea、jp/ea 日历、build_all/resolve_inputs 扩展、Gate A 对新指标裁决 | ①normalize_jp/ea 新增(fact_engine);②jp/ea 日历=tc.MARKETS 已含 'japan'/'ea'(B3/WP-A 已交付,本包零改动+口径测试);③build_all 扩展(实现)/resolve_inputs 扩展(WP-A 已交付);④Gate A 裁决=测试面对 rp.recompute_gate_a 的证成(rp 零改动) |
| 验收点 | ①②③ | 见 §一逐点证据映射 |

关联节实读: §三(a-3) L62-64(normalize_jp/ea 同构 normalize_rate@L406;compute_period_returns 零改动沿用;日历候选)、§三(a-4) L66(resolve_inputs/sources_status/series_store/Gate A)、§四 L126(冻结章 (b) 触面="扩展仅 resolve_inputs 增通道 glob 与 sources_status 新键")、§三(c) L79-84(五层降级)、§三(d) W-3 L115-118(US 零回归基线)、§七 L177-183(四红线)。

### §零.3 交付物清单(合同§一: A类 k=3 + M类 5,登记即白名单实体)

A类(新增文件, `git ls-files` 预检=0 重叠, 实测命令输出 0):

| # | 文件 | DESIGN依据 |
|---|---|---|
| A1 | docs/P1_WP_B_REPORT.md | 本文件(L170 验收①②③ 证据映射载体; 合同§五.1) |
| A2 | docs/P1_WP_B_DELIVERY.md | 交付说明五节+AC-03 漂移维护政策节(合同§五.2) |
| A3 | tests/test_p1_wp_b.py | L170 ①②③【测试】载体+Gate A 裁决测试 |

M类(既有文件触面, 合同冻结章五文件):

| # | 文件 | 授权触面 | 判定 |
|---|---|---|---|
| M-a | scripts/fact_engine.py | normalize_jp/normalize_ea 新增 + build_all@L723 尾部入参扩展; 既有 normalize_* 零改动 | 触面生效(§零.11 参数) |
| M-b | scripts/snapshot_builder.py | resolve_inputs@L47 + sources_status jp/ea 键; 其余零改动 | **零改动判定**: SOURCES@L43-44 自 rp.SOURCE_FILE_RULES 推导(WP-A 已含 jp/ea),resolve_inputs/sources_status 由此自动含 jp/ea 键——冻结章授权面已被上游实现吸收,本包零 diff(§零.4 依据) |
| M-c | scripts/trading_calendar.py | jp/ea 日历面 | **零改动判定**: MARKETS@L35-36 已含 'japan'/'ea',is_trading_day L108-116 已实现(B3 增 japan, WP-A 增 ea),GAP-P1-07 已闭 |
| M-d | scripts/data_validator.py | 条件项: 仅当 Gate A/registry 政策面需扩展 | **条件未触发**: Gate A 裁决面=rp.recompute_gate_a(注册表 criticality 驱动,零通道硬编码),validate_fact 消费 fp 政策(注册表驱动);新指标裁决无需 data_validator 改动,零 diff |
| M-e | config/metric_registry.json | 条件项: 仅 NIKKEI225.validation.range 上限单字段 | 触面生效: 60000→150000(§零.11, 先登记) |

超域=违约: 除上列 A1-A3+M-a/M-e 两处生效触面外,任何文件 diff 均构成 AC-05 违约(§零.13 实录)。

### §零.4 触面收敛依据(判定实录,文件:行级证据)

**(b) snapshot_builder 零改动判定**:
1. 冻结章 (b) 授权触面 = "resolve_inputs 扩展+sources_status 含 jp/ea 键;其余零改动"(DESIGN §四 L126 同口径: "扩展仅 resolve_inputs 增通道 glob 与 sources_status 新键")。
2. snapshot_builder.py L40-44: `SOURCES = [(ch, f"{r['prefix']}*.json", r['max_fallback_days']) for ch, r in rp.SOURCE_FILE_RULES.items()]` — FIX6-01 单一权威定义在 rp;WP-A 已在 SOURCE_FILE_RULES 登记 jp/ea(L174-175),故 resolve_inputs 与 build_snapshot L252-261 的 sources_status 构造**已自动**含 jp/ea 键。
3. tests/fixt.py L218-219(上游注释): "本通道事实提取未接线(WP-B/GAP-P1-08: _SOURCE_TO_INPUT 无 jp/ea 键),文件仅承担通道身份/EXACT-FALLBACK 构造面"——上游对本包快照面的理解一致=通道身份+来源状态,非 facts 级接线。
4. 结论: 授权面已被上游实现吸收;本包对 (b) 的交付义务转化为**测试证成**(A3 验收②: jp/ea 键在场+缺源 MISSING 实测),代码零 diff。
5. facts 级快照接线(build_snapshot L273-304 仅 global/macro/china/rate_economy)、series_store 增 NIKKEI225/DAX/CAC40 键(DESIGN §三(a-4) 候选)、_SOURCE_TO_INPUT 增 jp/ea 键(rp)——三者均在白名单外(分别属 (b)"其余零改动"禁区、(b) 禁区、rp 不在 M 类),登记为白名单外发现(§零.9),本包不实现。

**(c) trading_calendar 零改动判定**: L35-36 MARKETS 元组已含 'japan','ea';L108-111 japan/L112-116 ea 的 is_trading_day 已实现(保守最小集: 周末+01-01+12-25)。注册表 13 新指标 calendar 字段='japan'/'ea'(实测 13/13)。日历触面已被 B3/WP-A 交付,本包测试证成口径(验收① week/MTD/YTD 对 jp/ea 日历)。

**(d) data_validator 条件未触发判定**: Gate B 报告校验为锚点驱动(零通道/jp/ea 硬编码, 函数清单+docstring 实读);Gate A 裁决面在 rp.recompute_gate_a(注册表驱动);fact_engine.validate_fact 消费 fp 政策(注册表 freshness 驱动, 13 新指标已带窗口)。新指标裁决所需全部面均注册表驱动,零扩展必要→零 diff。

### §零.5 既有代码/既有测试零改动声明

- 既有 normalize_global/normalize_macro/normalize_china/normalize_rate/compute_period_returns/compute_derived/cross_metric_checks/validate_fact/make_fact/validate_derived: 零改动(冻结章 (a) "existing normalize_* zero change";L170 无任何派生公式授权)。
- 既有全部测试文件(含 tests/fixt.py, tests/test_p1_wp_a.py, tests/test_p03_e2eb_b3.py 等): 零改动(A 类白名单外)。
- run_weekly/采集器/装配/引擎目录: 零触碰。

### §零.6 P1专项纪律注册(实现全程有效)

1. 四红线(DESIGN §七): ①禁伪造数据/回填日期; ②禁跨边界写(LIVE/launchd/引擎目录); ③禁白名单外文件改动; ④禁网络出站(本包纯离线测试)。
2. DESIGN §三(a-2) L58: 任何节缺席→键不出现或 value=null,**禁以 0 占位**——normalize_jp/ea 对缺席节(真实首档 jp_.inflation=null, ea_.bund/inflation/prices 键不出现)必须照实不产事实。
3. DESIGN §三 L26 deny-by-default: 未注册键→FAIL 诊断记录(normalize_global L256-258 先例),不静默跳过不造事实。
4. compute_period_returns/RATE_UNITS/PRICE_LIKE_UNITS/validate_fact/grade_issues: 零改动沿用(注册表单位驱动口径)。
5. §三(c) 五层降级: 源失败/数据陈旧→诚实 DEGRADED/缺席,不粉饰(真实首档 ECB_MRO 滞后 50 天>10 天窗→DEGRADED 实录, 见 §零.12)。
6. 数值标注纪律: [实取]=读自真实首档/真实注册表, [示意]=测试合成(硬编码字面量,不冒充真实)。

### §零.7 DP 登记

**零 DP**。判定依据: L170 行内及所引节(§三(a-3)/(a-4)/§四/§七)零 DP 编号出现;DESIGN §二 DP 表(DP-1..4)均为 registered-type,无任何一行被本包工作内容引用。本包不消费、不新增、不修改任何 DP。

### §零.8 测试面登记(A3: tests/test_p1_wp_b.py)

全部离线(零网络, 零真实 GLM);期望值硬编码字面量;合成 fixture 不冒充真实采集(真实档=data/daily/jp_20261105.json/ea_20261105.json, WP-A 交付, 测试只读引用并标注[实取])。

| 测 | 名称 | 覆盖 | 数据 |
|---|---|---|---|
| t01 | normalize_jp 身份与权属拆分 | 验收① | 合成[示意] |
| t02 | normalize_jp 权属同构(B3 权属→对账输入, 不立事实) | 验收①/技术要点 | 合成[示意] |
| t03 | NIKKEI225 week/mtd/ytd 口径(japan 日历, 01-01 假日排除) | 验收① | 合成[示意], 手算字面量 |
| t04 | 数据不足路径(week/mtd/ytd/m1 unavailable+原因) | 验收① | 合成[示意] |
| t05 | 未注册键 FAIL 诊断(deny-by-default) | 验收①/§三 L26 | 合成[示意] |
| t06 | inflation 诚实缺席(inflation=null 不产事实不填 0) | 验收①/L58 | 合成[示意] |
| t07 | normalize_ea 七指标身份(7 facts, collector/值/观测日字面量) | 验收① | 合成[示意] |
| t08 | DAX 价格类口径(pct_change, 无 pp_change) | 验收① | 合成[示意] |
| t09 | ea 诚实缺席(仅 ECB_MRO 真实首档形态→1 fact) | 验收①/L58 | 合成镜像真实首档[示意] |
| t10 | build_all 扩展(jp_data/ea_data 入参, US+jp/ea 共存) | 验收①/③ | fixt 合成 |
| t11 | build_all 向后兼容(3+1 位置参数原签名调用) | 验收③ | fixt 合成 |
| t12 | jp 对账输入无对手方时不伪造对账记录 | 验收①/诚实性 | fixt 合成 |
| t13 | Gate A: 在场 PASS 计数+边界排除(13 指标不在 noncore_missing) | 技术要点④ | fixt+make_fact 合成 |
| t14 | Gate A: 缺席→noncore_missing_boundary 边界记录 | 技术要点④ | 合成 |
| t15 | Gate A: 坏值→noncore_fail(注册表 range 裁决) | 技术要点④ | fixt 合成 |
| t16 | 快照 sources_status 含 jp/ea 键(jp EXACT+ea EXACT) | 验收② | fixt 合成+真实 build_snapshot |
| t17 | 快照缺源 MISSING(ea 文件缺席→sources_status['ea']=MISSING) | 验收② | fixt 合成+真实 build_snapshot |
| t18 | W-3 零回归: 7通道 vs 5通道(无 jp_/ea_)快照 US 面全等 | 验收③ | fixt 合成+真实 build_snapshot |
| t19 | registry 单字段锁(NIKKEI225 range=[5000,150000]) | (e) 触面锁 | [实取]注册表 |
| t20 | 真实首档冒烟(jp_20261105: NIKKEI=61077.9+对账 3 条; ea_20261105: ECB_MRO=2.65 滞后50天 DEGRADED) | §三(c) 降级实录 | [实取] |

(实测定稿以 A3 文件为准;编号如有增删在 §零.12 如实登记。)

### §零.9 白名单外发现登记(不实现, AC-07.7/§八.9 承接)

| # | 发现 | 属地 | 为何不属本包 | 建议承接 |
|---|---|---|---|---|
| F1 | build_snapshot facts 级 jp/ea 接线(L273-304 仅 4 通道) | snapshot_builder L273-304 | 冻结章 (b) "其余零改动"禁区 | 快照接线轮(与 F3 同包, GAP-P1-08) |
| F2 | series_store 增 NIKKEI225/DAX/CAC40 序列键 | snapshot_builder L358-382 | 同上(DESIGN §三(a-4) 候选, 冻结章未授权) | 同 F1 |
| F3 | _SOURCE_TO_INPUT 增 jp/ea(缺席从 boundary 转 noncore_missing) | rp L111-117 | rp 不在 M 类白名单; 且翻转将改既有缺席口径(既有 fixture 预期随之变, 超 W-3 面) | GAP-P1-08 承接(rp 注释 L145-146 已预告"批次绑定属 WP-B"→经核对该注释所指=normalize 接线与批次绑定整体, 归 F1/F3 同轮) |
| F4 | fixt.py L214 注释"NIKKEI225∈[5000,60000]"将随 (e) 上限调整而陈旧(值 38000 本身仍合法∈新区间) | tests/fixt.py | fixt 不在白名单(注释文本陈旧非功能面) | 下轮触碰 fixt 时顺手更新 |
| F5 | EA 双源对账候选(DESIGN §三(a-3) cross_metric_checks EA 候选): ECB_MRO/DFR 双源(BBK vs ECB)在真实首档不可实现(DFR=READ_FAIL 缺席) | fact_engine cross_metric_checks | 无双源数据可对; 且 cross_metric_checks 属既有函数零改动面 | 数据齐备后的对账轮 |
| F6 | jp 对账输入(build_all 内)与 japan 通道事实的比对命中路径: build_all 无 japan_data 入参且 japan 通道 normalize 未接线(B3 D7), 对比恒 skip | fact_engine build_all | japan normalize 接线属 F1/F3 同轮 | 同 F1 |

### §零.10 已核对锚(排雷实录, 实现前完成)

1. **t02 B3 冻结锚**(tests/test_p03_e2eb_b3.py L55-184): 仅冻结 JP_POLICY_RATE/JGB2Y/JGB5Y/JGB10Y **完整字段**(range [-0.5,2]/[-0.5,15]×3)——NIKKEI225 不在其列,(e) 上限调整不触碰该锚。
2. **NIKKEI225 旧区间无任何测试锁定**: 全仓 grep range 相关断言,仅 test_p1_wp_a/t2c 断言 NEW9 成员资格与 fixt 值 38000∈区间(38000<150000 保持合法)。
3. **registry 13 新指标字段实测**(本 REPORT 前 `python3 -c` 实读): JP 6(japan_rate_collector×4: JP_POLICY_RATE[-0.5,2]/月频/japan; JGB2Y/5Y/10Y[-0.5,15]/日频/japan; jp_market_collector×2: JP_CPI_TOKYO_YOY[-2,15]/月频, NIKKEI225[5000,60000]/日频)+EA 7(ea_market_collector 全部: ECB_DFR/ECB_MRO[-1,15], BUND_10Y/2Y[-0.5,15], EA_HICP_YOY[-2,15], DAX[1000,40000], CAC40[1000,10000]);criticality 全部=important(非 core→Gate A 缺席不判 FAIL, 在场坏值→noncore_fail)。
4. **真实首档形态实测**: jp_20261105.json 顶层键含 policy_rates/jgb/prices+inflation=null; prices.NIKKEI225={close:61077.9[实取], date:2026-11-05, high:null, low:null, series=**date→value 字典** 251 观测}(非 {'dates','values'} 形态→normalize_jp 须转换); policy_rates.BOJ_POLICY_RATE={value:1.043, date:2026-09-01, prev_value:0.977}; jgb.JGB_10Y={2.855, 2026-11-04, 2.817}/JGB_2Y={1.891, 2026-11-04, 1.88}; ea_20261105.json 仅 policy_rates.ECB_MRO={2.65, 2026-09-16, 2.4}, bund/inflation/prices 键不出现。
5. **Gate A 对在场 jp/ea 事实的裁决路径实测推演**(rp L786-848/L1024-1076 实读): collector∈_AUTHORIZED_COLLECTORS(WP-A 已登记 L147-148)→通过; _SOURCE_TO_INPUT 无 jp/ea→batch=None→批次比对合法跳过(L826-827)→在场事实按质量计数; 缺席→boundary 记录(L1060-1064)"来源无法映射采集通道,不入缺失判定"→不入 noncore_missing。
6. **fixt 7 通道构造器**(tests/fixt.py L40-46/L212-276): collector_payloads 返回含 jp/ea;write_collectors 落盘 {name}_{ymd}.json×7——A3 快照级测试直接复用该 canon(L320 先例)。
7. **build_all 既有调用面**: tests/test_fact_engine.py L285-287 以关键字参数调用→尾部追加 jp_data/ea_data 形参向后兼容。

### §零.11 实现参数预登记(先登记后实现;运行后禁回改)

1. **(e) NIKKEI225.validation.range 上限: 60000 → 150000**(单字段, 下限 5000 与 max_week_pct_move=25 不动)。
   - 直接动因: 真实首档 close=61077.9[实取] 超旧上限→旧区间将把真实数据判 FAIL(outlier)。
   - 同侪 equity_index 余量先例(上限/近期真实收盘, 数据=global_20261104.json[实取]): SPX 30000/7568.92=3.96×, NDX 60000/28180.26=2.13×; 新值 150000/61077.9=**2.4555×**, 落于同侪带 [2.13×, 3.96×] 中段, 非激进外推。
   - 兼容性: 38000.0(fixt 合成值)∈[5000,150000] 合法; 38250/38100.5/38000.25(test_p1_wp_a SYN 序列)∈区间; t02 B3 冻结锚不涉 NIKKEI225(§零.10.1)。
2. **_JP_RECON_MAP(通道键→注册表 id, jp_ 文件内 japan_rate_collector 权属系列→对账输入)**: {'BOJ_POLICY_RATE':'JP_POLICY_RATE', 'JGB_10Y':'JGB10Y', 'JGB_2Y':'JGB2Y'}(JGB_5Y 不入 a-2 面, WP-A t3a 已锁"JGB_5Y 不入")。先例: _GLOBAL_ID_MAP(L244)/_MACRO_ALIAS(L281)/real_economy 对账(normalize_rate L442-449)。
3. **normalize_jp(data, as_of, source_file="jp_*.json") → (facts, recon_inputs)**:
   - 节→权属: prices/inflation 内注册且 source=='jp_market_collector' 的指标→事实; policy_rates/jgb 内 _JP_RECON_MAP 命中→对账输入 {metric_id, value, observation_date, channel='jp', prev_value, unit}(不立事实——registry 权属 japan_rate_collector, 同构 normalize_rate real_economy);注册但权属不符的对账节键→对账输入(权属判定以 registry source 为唯一权威);未注册键→FAIL 诊断记录(metric_id=原键, issues=[identity FAIL], 先例 L256-258)。
   - prices 项取值: close/date/high/low 透传(high/low 非 None 才写, 先例 L264-267); series: date→value 字典→{'dates':sorted, 'values':[按序]} 转换后入 make_fact(§零.10.4 形态); 连续性校验 raw_item 用 {'close','date','series':转换后} 使 >30 观测时真实生效(真实首档 251 观测)。
   - rate-like/policy/inflation 项取值: value/date(无 series, a-2 形态); release_date 键透传(在场时)。
   - collector='jp_market_collector'; retrieved_at=data.get('fetched_at'); validate_fact+grade_issues 同构 normalize_global L269-270。
   - inflation=None/节缺席→不产事实零异常(禁 0 占位)。
4. **normalize_ea(data, as_of, source_file="ea_*.json") → (facts, recon_inputs)**: 节 policy_rates/bund/inflation/prices;全部 7 注册指标权属 ea_market_collector→全部立事实; 键名即注册表 id(零别名, 实测确认); rate-like 项(value/date)与 prices 项(close/date/high/low/series 转换)取值同 normalize_jp 第 3 条; 对账输入恒空列表(返回签名同构, 无跨通道权属系列); 未注册键 FAIL 诊断同上。
5. **build_all 签名**: `build_all(global_data=None, macro_data=None, china_data=None, as_of=None, jp_data=None, ea_data=None)`(尾部追加, 位置兼容); jp_data/ea_data 非 None 时 `facts += normalize_jp/ea(data, as_of)[0]`; jp 对账输入的消费=F6 登记不实现(无 japan 事实对手方, 不伪造 source-diff 记录); compute_derived/cross_metric_checks 调用位置不动(派生面 US 专属, 13 新指标无派生依赖, _DERIVED_DEPS 无新键)。
6. **测试期望值(手算字面量, t03)**: NIKKEI 系列 {2025-12-30:50000, 2026-01-05:51000, 2026-01-09:52000}, as_of='2026-01-09T08:00:00+08:00' → end=2026-01-09; week 基准=2025-12-30(ISO 周一 2026-01-05 前最后观测) pct=52000/50000−1=**+4.0%**; mtd 基准=2025-12-30 pct=**+4.0%**; ytd 基准=2025-12-30 pct=**+4.0%**; m1=unavailable(无 ≤2025-12-09 观测, reason 含"序列不足1个月"); expected_sessions(week)=**8**(2025-12-30..2026-01-09 japan 日历: 12-30,12-31,01-02,01-05..01-09=8; 01-01 假日排除); index_point→pct_change 在场/pp_change 不在场。
7. **t20 真实首档期望[实取]**: jp_: NIKKEI fact value=61077.9/observation_date=2026-11-05/quality PASS(as_of=2026-11-05T20:00:00+08:00, lag=0≤5; range[5000,150000] 调整后合法); 对账输入 3 条(JP_POLICY_RATE=1.043/JGB10Y=2.855/JGB2Y=1.891)。ea_: ECB_MRO fact value=2.65/observation_date=2026-09-16/quality **DEGRADED**(滞后50天>10天窗, 日频政策利率观测陈旧如实降级, §三(c))。
8. **条件项零 diff 判定参数**: (b)(c)(d) 见 §零.4;全包 diff 预期= M-a(fact_engine.py)+M-e(metric_registry.json 单字段)+A1/A2/A3 三新文件, 任何其余 diff=违约。

---

## §零.12 实现实录

**M-a scripts/fact_engine.py**(diff=+127/−2; 唯二删除行=旧 build_all 签名+docstring,
既有 normalize_* 全函数零改动):

| 新增 | 行号 | 内容 |
|---|---|---|
| `_JP_RECON_MAP` | L480-481 | 通道键→注册表 id 三映射(§零.11.2 登记) |
| `_series_from_map` | L484-491 | a-2 prices.series(date→value 字典)→{'dates','values'} 形态转换 |
| `_channel_fact` | L493-512 | 已注册单项→事实(prices 取 close/series, 其余取 value; validate+grade; high/low 透传) |
| `_unregistered_diag` | L514-521 | 未注册键→FAIL 诊断记录(deny-by-default) |
| `normalize_jp` | L523-564 | 返回 (facts, recon); prices/inflation→事实(jp_market_collector 权属), policy_rates/jgb→对账输入(B3 权属), inflation=null 诚实缺席 |
| `normalize_ea` | L566-587 | 返回 (facts, recon); 四节全立事实(ea_market_collector 权属), 对账输入恒空 |
| `build_all` 扩展 | L837-859 | 尾部入参 jp_data/ea_data(位置兼容); jp 对账输入消费=F6 不实现(不伪造 source-diff) |

**M-e config/metric_registry.json**(diff=1 行): NIKKEI225 validation.range 上限 60000→**150000**(下限 5000/max_week_pct_move 25/版本 2.2.0/条目数 94 均不动, t19 锁)。

**(b)(c)(d) 零 diff**: 按 §零.4 判定, snapshot_builder.py/trading_calendar.py/data_validator.py 本包零触碰。

**实测冒烟实录**(实现后即时, /tmp/wp_b_smoke.py):
- [示意] t03 场景: NIKKEI week pct=**+4.0**/expected_sessions=**8**/mtd=ytd=**+4.0**/m1 unavailable('序列不足1个月')——与 §零.11.6 预登记逐字一致。
- [实取] jp_20261105.json: facts=[NIKKEI225@61077.9 PASS@2026-11-05], recon 3 条(JP_POLICY_RATE=1.043/JGB10Y=2.855/JGB2Y=1.891), derived 七窗口全算出(251 观测序列), inflation=null 不产事实。
- [实取] ea_20261105.json: facts=[ECB_MRO@2.65 **DEGRADED**@2026-09-16], issue=frequency/'ECB_MRO观测日滞后50天(>10天有效窗,daily频;未发布或采集失败,不得当作最新一期)'——§三(c) 五层降级实录(政策利率观测陈旧如实降级, 不粉饰)。

**测试开发期如实登记**: 初版 4 处测试预期失实(均为测试侧预期错误, 非实现侧缺陷), 逐处诊断后更正——
1. t05: snapshot_quality_grade 计数预期 {'PASS':0,…}→实际 {'PASS':1,…}(facts 含 NIKKEI 真实事实; 诊断记录不入 FAIL 计数的断言本意保持, FAIL=0 不变);
2. t13: fixture 诚实缺席重算——fixt jp 无 inflation 节/ea 无 prices 节→在场 9 而非 11, boundary 预期 4→7(补 japan 后 3 而非 0; 缺席恰为 DAX/CAC40/JP_CPI 三项诚实缺席, 与真实首档形态一致);
3. t13/t15: Gate A 第二层批次比对要求 source.file=具体文件名, build_all 默认 glob 不符→测试装配镜像 build_snapshot L273-306 真实调用面(_us_face_facts 具体名传参), 实现侧零改动;
4. t18: 通道键恒在场(文件缺席→{'status':'MISSING'}, resolve_inputs 既有语义), assertNotIn 预期→MISSING 状态断言。
更正后 20/20 绿; 上述更正均为**测试预期对既有系统语义的对齐**, 无一为实现侧回改。

## §零.13 白名单遵守实录(AC-05)

`git diff --name-status f6d0beb..工作树`(提交前) = **A 恰 3 + M 恰 2 + D=0**:

| 状态 | 文件 | 白名单位 | 判定 |
|---|---|---|---|
| A | docs/P1_WP_B_REPORT.md | A1 | ✓ |
| A | docs/P1_WP_B_DELIVERY.md | A2 | ✓ |
| A | tests/test_p1_wp_b.py | A3 | ✓ |
| M | scripts/fact_engine.py | M-a | ✓(+127/−2, 唯二删除=旧 build_all 签名/docstring) |
| M | config/metric_registry.json | M-e | ✓(单字段 1 行) |

M-b(snapshot_builder)/M-c(trading_calendar)/M-d(data_validator)=**零 diff**(条件判定见 §零.4); 其余全仓文件零 diff; tests/fixt.py 等既有测试零触碰; LIVE/launchd/引擎目录零访问(§零.14 第 6 项)。运行产物零新增: data/daily/ 与 data/research/ 零变化(git status 无 data/ 条目)。

## §零.14 §5.3 六项自检(数值标注纪律)

1. **标注完整性**: 本 REPORT 与 DELIVERY 全部数值断言逐处标注 [实取](读自真实首档/注册表/命令输出)或 [示意](测试合成硬编码); 无未标注数值。
2. **实取可复算**: 61077.9/1.043/2.855/1.891/2.65(jp_/ea_ 首档, t20 锁)/94/2.2.0/13(注册表)/71/70/1/0(CI)/+127/−2/A3+M2(diff)均为命令输出直录, 可复算。
3. **示意不冒充**: A3 全部合成值在文件头与逐测 docstring 显式标注[示意], 真实值仅经 data/daily 只读引用(t20)并标注[实取]。
4. **手算独立性**: t03/t08 期望(4.0/8/6/5.0 等)为 §零.11 预登记手算字面量, 禁自证(不 import 实现侧计算结果)。
5. **无粉饰**: 失实 4 处如 §零.12 逐条登记; ECB_MRO DEGRADED(滞后50天)如实降级披露; fixture 诚实缺席 3 项(DAX/CAC40/JP_CPI)在 t13 断言为边界记录而非伪装在场。
6. **禁区零触碰**: LIVE(/Users/cast/AI内容/…)零 grep 命中(模式 `R045|P1-WP-B|IA-P1-WP-B`, 实录见 §零.16)/零写; 引擎目录/launchd 零访问; 网络零出站(测试全离线, 本会话唯一网络面=git push 经 gh HTTPS 凭证通道)。
7. **自检补充(取证期发现)**: §零.1"禁锚非祖先"措辞失实一处(c9626633 实为 base 历史祖先), §零.16.2 完整登记+更正指针, 判定权留操作者——本轮自检共发现失实 5 处(§零.12 四处测试预期+本处登记措辞), 全部如实披露零隐瞒。

## §零.15 本地 CI 镜像实录

- 同构面: .github/workflows/offline-tests.yml L34-57 镜像(沿 WP-A run_ci_v14.py canon: 逐 tests/test_*.py 以脚本方式自 DEV 根运行, test_glm_live SKIPPED 设计性)。
- 驱动件: /tmp/run_ci_wp_b.py;summary=/tmp/p1-wp-b-evidence/ci-summary-wpb.txt;逐套件 log=ci-logs-wpb/(71 件)。
- **[实取] 结果: TOTAL_SLOTS=71 GREEN=70 FAILFLAG=0**(2026-11-06 00:59-01:01 HKT/16:59-17:01Z; 71=基线 70+新增 test_p1_wp_b 恰 1 件); test_glm_live=SKIPPED(真实 GLM 付费调用不进 CI)。
- 关键从属锁套件全绿: test_p0_baseline_lock_equivalence(N3d 修复面)/test_p1_wp_a(23 测)/test_p03_e2eb_b3(t02 B3 冻结锚含 JP_POLICY_RATE/JGB range)/test_p03_final_acceptance/test_phase3/test_p01_fix6/test_fact_engine。
- 首轮镜像驱动曾以 `python -m unittest tests.<name>` 方式运行得 2 红(test_p02_w1/test_p02_w1_fix1, ModuleNotFoundError: helpers)——经诊断为**镜像脚本调用方式失当**(脚本式套件须以文件方式运行), 非代码回归; 两套件以 canon 文件方式运行 46/0+41/0 全绿。该失当如实登记, canon 重跑后 71 槽全绿为准。

## §零.16 证据包与取证登记(摘要; 全套证据=/tmp/p1-wp-b-evidence/ 与 zip)

- 证据目录: /tmp/p1-wp-b-evidence/; zip=IA-P1-WP-B-EVIDENCE.zip(装配脚本 assemble_zip_wpb.py, SHA256SUMS zip 外自指豁免先例沿 WP-A R023/R060)。
- LIVE grep 零命中实录: 模式 `R045|P1-WP-B|IA-P1-WP-B` 于 LIVE 仓库 grep=0 行(证据件 03-git-forensics/live-grep-zero.txt)。
- git 取证: name-status f6d0beb..HEAD=A3+M2+D0/rev-parse/log 线性/reflog 零 reset --hard/ls-remote BRANCH-SET 对照(42 冻结+唯一新增 dev/p1-impl-b)(证据件 03)。

### §零.16.1 zip 装配终笔(装配后回填定值)

- zip=IA-P1-WP-B-EVIDENCE.zip, **成员 111 件 / 397,969 字节 / sha256=6e786095e05479990e46bdb723ef7c4030d49d74a97e9412b1d8f9ebd728b37e**, 装配时刻 2026-11-05T17:12:26Z(UTC), 装配 TIP=fa95213d53d12fd6b551b48dbb08abd5d108f868[实取·装配脚本 stdout]。
- 八类最低集齐: 01-spec 3 件 / 02-deliverables 21 件(10 文件×gitshow+worktree 双源+cross-hash.txt, **双源交叉哈希 0 失配**) / 03-git-forensics 6 件 / 04-ci 75 件 / 05-mapping 4 件 / 06-no-run 1 件 / 07-self-report 1 件(zip 内); SHA256SUMS zip 外(自指豁免沿 WP-A R023/R060 先例)。
- zip 完整性 testzip=OK; zip 内不含 SHA256SUMS 自身[实取·核验脚本]。
- **zip 内 REPORT/自述副本=fa95213 装配时点版**: 本终笔(§零.16.1 回填)发生于 zip 装配之后, zip 内 REPORT 副本不含本节定值——先例沿 WP-A 8ec3737(装配时点版如实披露); zip sha 与本节定值以本提交(装配后终笔)登记为准。

### §零.16.2 §零.1 禁锚措辞失实更正(取证期发现, 如实登记)

- 原登记(§零.1): "禁锚 c9626633 不得为祖先 | merge-base 核验非祖先"——**后半句为失实表述**: 实测 `git merge-base --is-ancestor c9626633 HEAD` = exit 0(是祖先), 因 c9626633(P1-DESIGN T2 终笔)本就是 BASE-P1B 的历史祖先(`rev-list --count f6d0beb..c9626633`=0), 一切自 base 创建的分支必然包含它——"非祖先"字面条件对任何合规分支均不可满足, 该措辞系本 Agent 转写/核验失实。
- 禁锚的正确语义与合规判定: **不得以 c9626633 为分支基点**。实测三元组: merge-base(dev/p1-impl-b, main)=**f6d0beb=BASE-P1B**(分支基点正确); rev-list --count f6d0beb..dev/p1-impl-b=**1**(恰一实现提交 6a9414c, 纯线性); main 尖端=f6d0beb(未被触碰)。
- 处置: §零.1 原句保留划线+更正指针(不删除原文), 本节完整登记; 判定权留操作者(若合同原文确以"非祖先"字面为停止条件, 该条件自 base 起即不可满足, 望操作者裁决语义)。

### §零.16.3 v1.2 整改重装配终笔(处置章项4; 装配后回填定值)

- zip=IA-P1-WP-B-EVIDENCE.zip(v1.2 重装配), **成员 111 件 / 406,554 字节 / sha256=8529fd3dca25ef94863317d5e08b8f7e412b223a55c8b22225a26d2eb956f5ad**, 装配时刻 2026-11-05T17:58:08Z(UTC), 装配 TIP=5389bbe121a58607f889076e742dbf1039d759e9(整改笔)[实取·装配脚本 stdout+独立复算一致]。
- 重装配勘正内容(v1.2 项4): ③类设计在场取证件 anchor-triple-and-design-presence.txt=补第三件 docs/P1_DELIVERY.md blob 对照(314c2644a51f2f575a90253580cb56346e2f93b6, 与冻结章登记一致)+对照基改锚 049ec978(v1.1 误用 f6d0beb)+补 is-ancestor 可达性判定(exit0)与 rev-list --merges=0 判定; ①类 spec-transcription-L170.md 副本随 §零.2 勘正同步(zip 内实测零全角逗号+逐字行与 DESIGN L170 全等)。
- §零.16.1 的 v1.1 zip(sha=6e786095…, TIP=fa95213)=历史登记保留不删, 该物理件已被本次重装配取代。
- 完整性[实取·核验脚本]: 双源 10 文件交叉哈希 0 失配/SHA256SUMS 111 行 zip 外重建(自指豁免沿 R019/R023/R060)/zip 内不含 SUMS 自身/testzip=OK。
- **zip 内 REPORT/DELIVERY/自述副本=5389bbe 装配时点版**(不含本节定值与 DELIVERY §四 v1.2 行; 先例沿本包 8edfb68/WP-A 8ec3737); zip sha 与本节定值以本提交(zip 哈希终笔)登记为准。

---

## §一 验收点逐点证据映射(AC-02)

| 验收点(DESIGN L170) | 证据(测试=tests/test_p1_wp_b.py, 全绿[实取·CI]) |
|---|---|
| ① 单测: 新通道事实构造+口径(week/MTD/YTD 对 jp/ea 日历)+数据不足路径【测试】 | 构造: t01/t02(jp 身份+权属拆分)/t07(t ea 七指标)/t09(诚实缺席形态); 口径: t03(NIKKEI week/mtd/ytd=+4.0, japan 日历 expected_sessions=8 含 01-01 排除)/t08(DAX +5.0, ea 日历 6); 数据不足: t04(七窗口 unavailable+原因, 绝不回退 0) |
| ② 快照 sources_status 含 jp/ea 键的构建测试(含缺源 MISSING)【测试】 | t16(真实 build_snapshot: jp/ea/japan EXACT+file/file_date; 13 新指标缺席=noncore_missing_boundary 13 条合法登记)/t17(ea 文件缺席→{'status':'MISSING'}, jp 不受影响) |
| ③ 既有 US 面输出零回归(W-3 对照)【测试/CI】 | t18(7 通道 vs 基线 4 通道快照: facts 全等/quality 全等/gate_a 状态与非核心缺失全等/基线 4 通道 sources_status 全等; 差异仅新通道键)+本地 CI 71 槽=70 绿+1 skip(§零.15, 含 test_p0_baseline_lock_equivalence 等全部从属锁) |
| 技术要点: normalize_jp/ea | fact_engine L523/L566[实取·diff]; t01-t09 |
| 技术要点: jp/ea 日历 | trading_calendar 既有 japan/ea(M-c 零 diff); t03/t08 口径断言(expected_sessions 8/6) |
| 技术要点: build_all 扩展 | fact_engine L837(+jp_data/ea_data 尾参); t10/t11(向后兼容)/t12(不伪造对账) |
| 技术要点: resolve_inputs 扩展 | WP-A 已交付(SOURCES 推导); t16/t17/t18 真实构建证成; M-b 零 diff(§零.4) |
| 技术要点: Gate A 对新指标裁决 | t13(在场→计数+不入缺失; 边界收敛 7→3)/t14(缺席→13 条边界合法登记, 精确字符串断言)/t15(坏值→noncore_fail+effective=DEGRADED) |
| (e) 条件触面 | registry NIKKEI225 上限=150000[实取]; t19(单字段锁: range=[5000,150000]/max_week_pct_move=25/版本 2.2.0/94 条目); t20 真实首档 61077.9 在新区间内通过 |

## §二 偏离与如实声明

1. **§零.1 禁锚措辞失实(取证期发现)**: 原登记"禁锚 c9626633 非祖先已核"失实——c9626633 实为 BASE-P1B 历史祖先(对一切合规分支"非祖先"字面均不可满足); 正确判定=分支基点核验(merge-base(dev/p1-impl-b, main)=f6d0beb=BASE-P1B, 恰 1 提交领先, 纯线性)——§零.16.2 完整登记, 原句划线保留不删, 判定权留操作者。
2. **快照面交付形态偏离(收敛性)**: 冻结章 (b) 授权"resolve_inputs 扩展+sources_status jp/ea 键"已被 WP-A 上游实现吸收(SOURCE_FILE_RULES→SOURCES 推导), 本包 (b) 零 diff、以测试证成(t16/t17/t18)——非缩水: 授权面功能全部在场且被验收测试锁定; facts 级快照接线/series_store/_SOURCE_TO_INPUT 属白名单外(F1/F2/F3 登记), 不实现=合规而非偏离。
3. **测试开发期 4 处预期失实**(§零.12): 均为测试侧预期错误并如实登记, 更正后全绿, 零实现侧回改。
4. **首轮 CI 镜像调用方式失当**(§零.15): `-m unittest` 方式致 2 个脚本式套件误红, canon 文件方式重跑全绿; 失当过程不隐瞒。
5. **F4 注释陈旧**: fixt.py L214"NIKKEI225∈[5000,60000]"注释随上限调整陈旧(值 38000 仍合法∈新区间), fixt 不在白名单不更新, 登记留后续。
6. **零运行产物**(步骤⑩登记): 验收①②③全部为【测试】/【CI】面, 无真实运行验收点; 本包未运行任何采集器/快照构建生产路径(build_snapshot 仅测试沙箱 tmp 目录), data/daily 与 data/research 零变化——故无运行产物档, 如实登记。
7. **ECB_MRO DEGRADED 如实降级**: 真实首档观测 2026-09-16 vs 研究 2026-11-05 滞后 50 天>10 天窗(注册表日频政策), t20 断言 DEGRADED+滞后消息——非缺陷, 诚实降级语义(§三(c))。

## §三 合同逐条自检 AC-01~AC-07

- **AC-01 规格转写忠实**: §零.2 逐字转写 L170+四要素分解; 关联节(L62-66/L79-84/L115-126/L177-183)实读; 无私自增删语义。✓
- **AC-02 逐点证据映射**: §一表格逐验收点→测试件行号映射, 全部可复跑。✓
- **AC-03 漂移维护**: DELIVERY 含漂移维护政策节(fixture/锚点/上游再演进三类处置政策); 本包锁面: t19(registry 单字段)/t11(build_all 兼容)/t18(W-3 基线)/t02(B3 冻结锚经 CI 全绿)。✓
- **AC-04 诚实性**: 缺席=缺席(t06/t09/t13 边界); 陈旧=DEGRADED(t20); 数据不足=unavailable+原因(t04); 诊断记录不入研究计数(t05); 失实过程如实登记(§零.12/§二)。绝不以 0 占位/回填/伪造对账。✓
- **AC-05 白名单遵守**: §零.13: A3+M2+D0 与白名单逐件符合, 零超域。✓
- **AC-06 git 纪律**: 纯线性提交(零 amend/零 reset --hard/零 force), 分支 dev/p1-impl-b 自 BASE-P1B 创建, push 经 gh HTTPS 通道; BRANCH-SET 42 冻结+唯一预期新增=本分支(§零.16)。✓
- **AC-07 停止纪律/例外如实**: 本轮授权面全部落地无停止; 白名单外发现 6 项(F1-F6)登记不实现(§零.9), 承接建议留操作者; 无(d)情形触发。✓
