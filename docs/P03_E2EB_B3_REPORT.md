# P03 E2EB WP-B3 实施报告 — 日本利率数据身份与获取

- 合同: IA-P03-E2EB-WP-B3-AC-v1.4 案A回做版(sha256前缀 c878e5a8,以操作者归档件为准)
- 执行: Agent 3(executor), DEV 仓 /Users/cast/investment-agent-dev, 分支 dev/p03-e2eb-b3
- 基线: 04ead6d384f5ef30113883fa8ff46197d08771f1(main 与分支双 tip 实测一致;设计三文件
  与 f1fe593 blob 级相等已验)
- 报告纪律: §零为**运行前登记**(登记型决策点先登记后实现,运行后禁回改);
  §一起按执行进度如实追加。红/绿、失败、归因一律实测,不凑数不造数。

---

## §零.1 任务转写(DESIGN §六 WP-B3 L222-226 逐字,零改写)

> **WP-B3 日本利率数据身份与获取(JGB/日银政策利率入注册表+采集)**
> - 目标: 消除GAP-01: 注册表新增日本政策利率与JGB关键期限(至10Y)身份(81 [实取: INVENTORY 层② registry v2.0.0实测指标总数, 2026-11-02]→新增N条,registry版本升级走既有变更纪律),采集通道落地(免费公开源规则循预授权③于本包适用)。
> - 范围: registry变更+采集器扩展+通道SOURCE_FILE_RULES登记;**不含**模式B其余面。
> - 依赖: 无硬依赖(可与WP-B1/B2并行);完成后E2E-B场景双端闭合。
> - 验收要点草案: ①注册表计数实测断言(81 [实取: INVENTORY 层② registry v2.0.0实测指标总数, 2026-11-02]+N,工件: 测试文件+registry文件SHA) ②身份语义校验通过(registry_semantics既有校验,工件: 测试) ③真实采集样本落data/daily且经快照Gate A(工件: 数据档文件+快照digest) ④文档口径登记(单位percent/日历/来源,工件: registry diff)。

N 的取值: 4(见 D1;政策利率1条+JGB关键期限3条: 2Y/5Y/10Y——"至10Y"字面内的关键期限,
DESIGN 未列 1Y/3Y 等,不自行扩盘)。

## §零.2 交付物清单(M/A/D 行,白名单闭包)

| 行 | 工件 | 说明 |
|---|---|---|
| M1 | config/metric_registry.json | 81→85,v2.0.0→v2.1.0,新增4条目(D11全字段冻结) |
| M2 | scripts/research_provenance.py | `_AUTHORIZED_COLLECTORS`+japan_rate_collector;`SOURCE_FILE_RULES`+japan;`SOURCE_CHANNELS`**四通道不动**(D6);L143-144注释随实况更新 |
| M3 | scripts/registry_semantics.py | `KNOWN_SOURCES`+japan_rate_collector;`KNOWN_CALENDARS`+japan;镜像注释同步 |
| M4 | scripts/trading_calendar.py | `MARKETS`+japan;`is_trading_day` japan分支;模块docstring日历口径表补行 |
| M5 | tests/test_e2e_frozen14.py | 演进域化: L276/280/287 Gate-PASS 锁族 R057 形迁移(D14) |
| M5 | tests/test_e2e_orig14.py | 演进域化: L411 现场 Gate 声明域迁移(D14) |
| M5 | tests/test_gate_chain_p01.py | 演进域化: L177-189 gate_status 三态循环域迁移(D14) |
| M5 | tests/test_fact_engine.py | 演进域化: L268-269 快照质量分级域迁移(D14) |
| A1 | scripts/japan_rate_collector.py | 新采集器模块(D10) |
| A2 | data/daily/japan_20261105.json | 真实采集档(2026-11-05 运行;现存文件 sha256 零变化) |
| A3 | tests/test_p03_e2eb_b3.py | 离线测试锁(合成fixture+硬编码预期值+负向敏感性) |
| A4 | docs/P03_E2EB_B3_DELIVERY.md | 交付报告(五节+漂移维护+演进域化迁移表) |
| A5 | /tmp/p03-e2eb-b3-evidence/IA-P03-E2EB-WP-B3-EVIDENCE.zip | 证据包(九类成员+SHA256SUMS) |

D 行: **无**(D=0;无任何删除行工件)。

白名单外零触碰(红线声明): tests/fixt.py、tests/helpers/baseline_locks.py、
scripts/snapshot_builder.py、scripts/fact_engine.py、scripts/historical_coverage_audit.py、
tests/test_p0_baseline_lock_equivalence.py、tests/test_p01_fix6.py、tests/test_p02_w4.py、
launchd/LIVE/CI 配置——一律零改动(其红面按 §零.6 (b) 路由如实登记)。

## §零.3 冲突自检(步骤⑤)

**无 (d) 级规格冲突**(无"规格不可执行/自相矛盾"情形)。冻结测试面与本包合法演进之间的
张力(fix6 通道迭代域/w4-d2 通道权威矩阵/equivalence-Z0 冻结映射表等)属**上游锁族对
新通道的未覆盖面**,非规格矛盾,按三态路由 (b) 吸收: 禁当场改冻结件,红面如实登记
(§零.6),修复路径归后续重冻轮(DELIVERY §漂移维护)。

## §零.4 登记型决策点(先登记后实现;运行后禁回改)

- **D1 命名**: `JP_POLICY_RATE / JGB2Y / JGB5Y / JGB10Y`。理由: 冻结工件碰撞规避——
  R057 等价套件 `_evolved_85()`(test_p0_baseline_lock_equivalence.py L106-112)向
  **实载注册表副本**追加 `BOJ_POLICY_RATE/JGB_2Y/JGB_5Y/JGB_10Y`,真实注册表若同名,
  N5d/R[legal85] 注入 doc 即现重复 metric_id→T2 双射红(非本包语义);`JGB_10Y` 另为
  glm_g1 `UNREGISTERED_METRIC`(ABSENT_REGISTRY 语义锚,test_p03_w2_glm_g1.py L49),
  注册将翻转该语义。无下划线形态避开全部碰撞,且与 source_symbol 家形不冲突。
- **D2 source 字段**: `'japan_rate_collector'`(=新采集器模块名;家形先例: source值==
  采集器模块名,macro_collector→macro_collector.py)。**弃** `macro_collector` 冒充
  形态(R057 `_jp()` 模板取 macro_collector 系**等价套件虚构条目**的锁行为形态,非真实
  数据身份): 数据实际出自 japan 采集器,若注册表声明 macro_collector,未来真实事实
  collector='japan_rate_collector' 将被 `fact_source_problems`(_AUTHORIZED_COLLECTORS)
  拒绝,或被迫冒充 collector='macro_collector'——两种形态均违反来源诚实红线,且 B3 身份
  将被 E2E-B 回溯推翻。诚实身份的红面代价(Z0/d2)按 (b) 路由登记。
- **D3 日历**: `calendar='japan'`;trading_calendar.MARKETS 追加 'japan',
  `is_trading_day` japan 分支=**周末+01-01+12-25 最小保守集**(hk 同款先例;宁多预期
  一天不假miss原则,日本祝日不逐个精确——11-3 文化日 MOF 无发布,该日被保守视为
  交易日仅影响窗口标注精度,2026-11-05 实测证实);registry_semantics.KNOWN_CALENDARS
  同步追加(A6b 镜像 test_p02_w1.py L114-115 保持绿)。
- **D4 单位/量纲/身份**: unit=`'percent'`(现行利率水平量纲纪律,零枚举扩展);
  JGB value_type=`'yield_or_spread_level'`(UST_2Y 同形),asset_class=`'rates_yield'`,
  instrument=`'index_rate_series'`;JP_POLICY_RATE 镜像 FED_FUNDS 家形:
  value_type=`'monthly_avg_rate'`,asset_class=`'policy_rate'`,instrument=`'macro_series'`
  (源为月均拆借利率序列,非决议值本身;决议值口径差异登记于 calc/release_semantics)。
- **D5 criticality**: 4条目均 `'important'`(非 core)。理由: ①core 缺席即 Gate A FAIL,
  而本包事实提取未接通(E2E-B 范围,D7),core 化将使一切 fixture/真实快照核心缺失;
  ②CORE_FLOOR=32 下限语义不受影响(core 32 不变)。
- **D6 通道登记**: `SOURCE_FILE_RULES['japan']={'prefix':'japan_','max_fallback_days':5}`
  (5 自然日≈周末+短假,与 global/china 同档)。`SOURCE_CHANNELS` **保持四通道不动**:
  它是 sources_status_problems 的**必需通道迭代域**——历史快照(全部存量
  research_snapshot_*.json)无 japan 键,回溯要求将使全部历史重验失败;japan 键在新快照
  中在场而验证器中性忽略(不拒不查),其自身规范名身份由 canonical_source_file(japan)
  承担。
- **D7 `_SOURCE_TO_INPUT` 故意不加** japan_rate_collector 映射: 该表是**事实级批次绑定**
  (fact_source_problems/recompute_gate_a L1012/L1040)。本包不含 sb/fe 事实提取接线
  (DESIGN L224"不含模式B其余面"),未映射源在 recompute_gate_a 走 L1040-1044
  **边界记录**(noncore_missing_boundary,如实披露,不影响 effective);若现在加映射,
  JP 指标将以"来源文件在场而指标缺席"进 noncore_missing,一切 fixture 快照 Gate A 由
  PASS 翻 DEGRADED,红面从3套件爆炸至全域——演进不撞墙(R057 R[legal85] 检查名自述
  "B3重冻发车前提")语义要求接线与映射同轮(E2E-B/重冻轮)落地。
- **D8 授权采集器双侧同步**: `_AUTHORIZED_COLLECTORS`+`'japan_rate_collector'` 与
  registry_semantics.`KNOWN_SOURCES` 同步追加(A6c 镜像 L116-117 保持绿;单侧将红)。
- **D9 版本**: registry v2.0.0→**v2.1.0**(次版本=新增条目,无既有字段语义变更)。
- **D10 采集器形态**: 新模块 scripts/japan_rate_collector.py(A 行)。源=①MOF jgbcme
  (https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv,
  白名单域 mof.go.jp,无key,Shift_JIS 解码,当月日频收盘,列头 Date,1Y..40Y)→
  JGB2Y/JGB5Y/JGB10Y;②FRED fredgraph 公开端点
  (https://fred.stlouisfed.org/graph/fredgraph.csv?id=IRSTCI01JPM156N,白名单域
  fred.stlouisfed.org,无key,月频)→JP_POLICY_RATE。产出 data/daily/japan_YYYYMMDD.json
  (YYYYMMDD=运行日),家形镜像 macro 通道 `{date,data:{metric_id:value}}` 并增
  `observations`(逐系列观测日,月频/发布时差如实不冒充运行日)/`sources`(逐源url)/
  `fetched_at`/`alerts`。仅标准库(urllib),禁第三方依赖。失败语义: 单源失败不阻断
  另一源(alerts 如实);全部失败 exit 1 且不产出空 data 文件。
- **D11 四条目全字段冻结**(实现在 M1;值域实测锚定见 D12):
  - JP_POLICY_RATE: display_name 日本无担保隔夜拆借利率(月均);source_symbol
    IRSTCI01JPM156N;monthly;percent;japan;important;active;instrument macro_series;
    value_type monthly_avg_rate;validation range [-0.5,2] 无周动键(镜像 FED_FUNDS
    月频无周键);freshness 60+月频note;calc/release_semantics 见 M1 落稿。
  - JGB2Y/JGB5Y/JGB10Y: display_name {2,5,10}年期日债收益率;source_symbol "2Y"/"5Y"/
    "10Y"(MOF jgbcme 列名原样,source_symbol=源系统符号的家形纪律);daily;percent;
    japan;important;active;instrument index_rate_series;value_type
    yield_or_spread_level;validation range [-0.5,15]+max_week_abs_move 1.0
    (镜像 UST_2Y,下限-0.5 容纳负利率时代历史值,非猜测);freshness 7;
    calc=MOF jgbcme 关键期限最新收盘观测;release_semantics=MOF 每营业日发布/按观测日
    保守处理(UST_2Y 同形)。
- **D12 实测锚定值**(2026-11-05 采集实测,作 A3 测试硬编码预期与 D11 值域佐证):
  MOF jgbcme 2026-11-04 行: 2Y=1.891,5Y=2.269,10Y=2.855(单位%;2026-11-03 文化日无
  发布行,当日历法佐证 D3);FRED IRSTCI01JPM156N 最新观测 2026-09-01=1.043(月频,
  2026-09 统计期)。原始回执存证据包 real/。
- **D13 可选⑦的取舍**: 选**映射表分类**(DELIVERY §演进域化迁移表承载: 逐受影响
  套件/检查→红/绿面→归因→修复路径),**不做** N8 等价用例追加——等价套件为 R057 冻结
  M 件,加例须动冻结文件;映射表形式信息等价且零冻结面触碰。
- **D14 演进域化四文件迁移形态**(R057 形=gate_vintage_ok/一致性绑定,禁语义弱化/
  删断言/skip;迁移前后现态均须绿——受控注入实验已证四文件注入态全绿,迁移为纯域化):
  - test_e2e_frozen14.py E2E-01a(L275-277): `gate_a.status=='PASS'` →
    `bl.gate_vintage_ok(snap['gate_a'])[0]`(PASS 恒真+DEGRADED 仅 vintage 合法);
  - E2E-01b(L278-281): `meta.gate_a=='PASS'` → meta 与快照实际 gate 一致
    (`meta.get('gate_a')==snap['gate_a']['status']`)且 `bl.gate_vintage_ok(...)`
    (一致性语义强化非弱化);
  - E2E-01c(L284-288): `final_quality=='PASS'` → 与 combine_gates 精确一致
    (gate_b='PASS' 注入下 final=DEGRADED iff gate_a=DEGRADED,绑定快照实际值);
  - test_e2e_orig14.py L411 现场: 场景7声明冲突循环的声明域按快照实际 gate 有效值
    对齐(迁移落点以工作树实读为准,1:1 映射入 DELIVERY 表);
  - test_gate_chain_p01.py L177-189: 三态读取循环逐态断言不动,快照 gate_a 有效值
    构造域按 vintage 语义校验(bl.gate_vintage_ok 旁证,不替换三态断言);
  - test_fact_engine.py L268-269: `overall=='PASS'` 质量分级断言旁证 vintage 域
    (分级语义不动,gate 域旁证)。
  落地时逐处以工作树实读行号为准复核,1:1 before/after 入 DELIVERY 迁移表。
- **D15 真实采集运行口径**: 2026-11-05(运行日)执行 A1 模块一次,产出
  data/daily/japan_20261105.json;观测日=源端各自最新已发布(MOF 2026-11-04/FRED
  2026-09-01,见 D12),逐系列记于 observations 不冒充运行日;data/daily 现存全部文件
  sha256 前后零变化(A 行只新增)。
- **D16 证据快照形态**: 沙箱目录(四基线通道取 data/daily 20261104 真实档副本+
  japan_20261105.json)经 snapshot_builder.build_snapshot(target_date=20261105) 构建,
  gate_a/sources_status/digest 如实存证(预期: 基线四通道 FALLBACK lag1、japan EXACT
  lag0;Gate A 有效值如实记录,若 DEGRADED 须 vintage 合法并登记明细)。不触碰生产
  research_snapshot_*。
- **D17 受控注入实验记录**(2026-11-05,零提交,运行后还原+清洁验证+抽查绿):
  注入=§零.2 M1-M4 等价态(85/84,v2.1.0);sanity: rsem 0 错/A6b/A6c 镜像绿/
  counts_ok 绿/evolution_legal 红(恰为 D2 预期)/sb.SOURCES 自动含 japan/canonical
  japan 规范名通过;全量 66 套件=**63绿3红**(红=test_p01_fix6[B[japan]×4]/
  test_p02_w4[d2×1]/test_p0_baseline_lock_equivalence[Z0+R[legal85]实验伪影]);日志
  存证据包 exp-logs/。R[legal85] 实验红因=预演变体构造自实载 doc(85+jp源)注入
  **clean worktree**(rsem 无 japan_rate_collector)→级联;真实分支 worktree=本包
  tip(jp-aware),级联不发生,但 d2(test_p02_w4∈M_FILES)仍使 R[legal85] 红——
  真实分支等价套件预期红面=Z0/N1a/N3d/N5d/N7b/R[legal85] 六项(N1a/N3d/N7b=负向电池
  按 live=81 校准的算术漂移,live=85 后单删条目不触下限——电池如实报告"锁需重锚",
  与 R[legal85] 检查名"重冻发车前提"同义)。

## §零.5 预期红面登记((b) 路由: 上游漂移诚实报告,禁当场改)

| 套件 | 红检查 | 归因 | 修复路径(重冻轮) |
|---|---|---|---|
| test_p01_fix6.py | B[japan]×4(L342-388 通道迭代域) | B 循环遍历 rp.SOURCE_FILE_RULES(含新 japan),fixture 无 japan 档→MISSING≠FALLBACK;ssp 迭代域=SOURCE_CHANNELS(四通道)不查 japan→不拒 | fixt 增 japan fixture+循环域基线化(迁移属冻结件,下轮) |
| test_p02_w4.py | test_d2_channel_authority_matrix(L761-773) | hca.REGISTRY_SOURCE_CHANNEL 冻结映射+L773 冻结五值词表(无 japan) | hca 映射+d2 词表域化(生产脚本+冻结测试,下轮) |
| test_p0_baseline_lock_equivalence.py | Z0+R[legal85](+N1a/N3d/N5d/N7b 电池算术漂移) | bl.evolution_legal 内置4采集器映射表(R057 REPORT L183 登记设计)无 japan_rate_collector;预演自实载 doc 构造 | baseline_locks 映射表扩展+电池锚重校准(R057 漂移维护要素2: 重冻时点) |

其余 63 套件(含演进域化四文件迁移后)预期全绿;A3 新套件绿。实测以 §三 全量运行
记录为准(如有出入以实measured为准如实登记,禁解释性漂白)。

## §零.6 白名单外零触碰声明

见 §零.2 末行红名单。实测=git diff 行级核对(DELIVERY §一交付清单附 diff 统计与
关键文件 sha256 前后对照)。

---

## §一 基线实读登记(步骤④,先读后动)

基点: `04ead6d`(R058 merge;分支 dev/p03-e2eb-b3 起点,operator-reset)。实读
对象与关键落点(行号=该时点实读):

- `scripts/snapshot_builder.py` L43-44(`SOURCES` 由 `rp.SOURCE_FILE_RULES`
  派生→登记 japan 后通道自动活,零 sb 改动);L236-310+L438(`build_snapshot`
  签名/`trusted_root`/单 dict 返回——D16 沙箱调用的形态依据)。
- `scripts/research_provenance.py` L111-117(`_SOURCE_TO_INPUT` 批量绑定与
  recompute 双消费点)、L145(`SOURCE_CHANNELS` 迭代域)、L152-157
  (`SOURCE_FILE_RULES`)、L172+(canonical_source_file 纯字符串身份层)、
  L863/L1111/L1307(recompute_gate_a/gate_status/digest_snapshot)。
- `tests/helpers/baseline_locks.py`(R057 三联锁: REGISTRY_FLOOR=81/
  ACTIVE_FLOOR=80/CORE_FLOOR=32;BASELINE_VINTAGE_IDS;evolution_legal 内置
  4 采集器映射;vintage_additions;gate_vintage_ok 正常日判定语义)。
- `tests/test_p0_baseline_lock_equivalence.py` L53-66(M_FILES 冻结集)、
  L89-126(_jp/_evolved_85/Z0 冻结映射)、L387-449(预演 worktree-at-HEAD)。
- `tests/test_p01_fix6.py` L342-388(B 通道迭代域=SOURCE_FILE_RULES 遍历);
  `tests/test_p02_w4.py` L748-773(d2=hca.REGISTRY_SOURCE_CHANNEL 冻结映射);
  `scripts/historical_coverage_audit.py` L108(第三处硬编码映射)。
- `tests/test_p02_w1.py`(A6b/A6c 双侧镜像惯例);`tests/test_p0_sbflow_backup.py`
  (R058 测试家形惯例: 合成 fixture+锚定复刻+零网络);`config/metric_registry.json`
  (UST_2Y/FED_FUNDS 家形模板)。
- 受控注入实验(实读的动态面,脚本+日志存证据包 exp-logs/): 在 HEAD 注入
  "registry 85+rsem+tc+collector+japan档"全量形态跑 66 套件=63绿3红,
  红面恰为 §零.5 登记三件(机制逐项吻合);撤针后 git-checkout 复原。结论:
  迁移四文件=纯域化(注入态与迁移态同为"演进已发生"宇宙),合法演进不撞其余
  63 套件之墙。

## §二 实现摘要(步骤⑥,M/A 白名单内)

- **M1** config/metric_registry.json: version 2.0.0→2.1.0;81→85(active 80→84);
  新增 JP_POLICY_RATE/JGB2Y/JGB5Y/JGB10Y(全字段=D11 冻结=A3 硬编码三方一致;
  家形镜像 FED_FUNDS 月频/UST_2Y 日频,range 下限-0.5 容纳负利率史值)。
- **M2** scripts/research_provenance.py: `_AUTHORIZED_COLLECTORS`
  +japan_rate_collector(白名单源);`SOURCE_FILE_RULES`+japan{prefix japan_,
  max_fallback_days 5};`SOURCE_CHANNELS` **四通道元组零变化**(D6,注释随实况
  更新);`_SOURCE_TO_INPUT` **有意不加**(D7→演进日缺席走
  noncore_missing_boundary 边界记录,不进 noncore_missing、不影响 gate)。
- **M3** scripts/registry_semantics.py: KNOWN_CALENDARS+japan、
  KNOWN_SOURCES+japan_rate_collector(A6 双侧镜像与 M2/M4 同步;D8)。
- **M4** scripts/trading_calendar.py: MARKETS+japan;is_trading_day japan 分支
  (最小集: 周末+01-01+12-25,hk 同款保守);docstring 日历口径表补行(D3)。
- **M5** 四文件演进域化迁移(D14 形态;逐处 1:1 before/after 见 DELIVERY
  §演进域化迁移表;迁移后四套件 33/0、43/0、88/0、61/0 全绿)。
- **A1** scripts/japan_rate_collector.py: 标准库-only 采集器。MOF jgbcme
  (Shift_JIS,列头期限映射,取最后合法数据行)+FRED fredgraph CSV('.'缺失跳过,
  取最后有值行);逐源 UA(FRED fredgraph 对陌生 UA 挂起→'curl/8.0 <身份>'
  前缀形态,注释实测登记);单源失败容错降级(缺席+alerts 如实);全缺→exit 1
  不落盘;原子写(tmp+replace);--data-dir 支持。
- **A2** data/daily/japan_20261105.json: 2026-11-05 真实采集档
  (sha256=6bba4718759ba12546499c1bdc510a1157b87f9462408e14071967d29e14e7f1);
  data/daily 现存 16 文件前后字节级零变化(daily_pre/post.sha256 对照);
  观测日逐系列如实(JGB=2026-11-04,policy=2026-09-01)不冒充运行日。

## §三 测试与全量运行(步骤⑧⑨)

**A3** tests/test_p03_e2eb_b3.py: 28 用例 5 组(T1 注册表身份 6/T2 通道登记 5/
T3 日历 2/T4 采集器离线 11/T5 一致性与真实档 4)全绿。离线零网络(raw 注入+
mock _http_get)、零 skip、合成 fixture 复刻真实锚定值(D12)作期望常量、
真实档全文 sha256 冻结、沙箱 build_snapshot 集成(japan EXACT/四通道 MISSING/
gate FAIL/core_missing——通道登记经生产 resolve 链证明)+负向(超回退窗→MISSING、
坏日历日期拒、跨通道文件拒、期限坏值缺席+告警、全源失败不落盘 exit 1)。

**迁移四套件**: frozen14 33通过/0失败;orig14 43/0;gate_chain_p01 88/0;
fact_engine 61/0(迁移前后均绿=纯域化,D14 复核)。

**全量(69 个 tests/*.py 逐文件真实运行,日志+汇总存证据包 fullrun-logs/)**:
66 PASS / 3 RED。三红面与 §零.5 登记**逐项吻合,零意外红**:

| 套件 | 实测红面 | §零.5 登记 | 吻合 |
|---|---|---|---|
| test_p01_fix6.py | 86通过/4失败,4红全为 B[japan](lag1 边界齐备/lag=5 边界/lag=6 拒/115 天拒;fixture 无 japan 档→MISSING≠FALLBACK,ssp 迭代域四通道不查 japan→probs=[]) | B[japan]×4 | ✓ |
| test_p02_w4.py | test_d2_channel_authority_matrix 1 红(hca.REGISTRY_SOURCE_CHANNEL 冻结映射+五值词表无 japan) | d2×1 | ✓ |
| test_p0_baseline_lock_equivalence.py | 25通过/6失败: Z0/N1a/N3d/N5d/N7b/R[legal85](greens=5 reds=23;bl.evolution_legal 冻结 4 采集器映射无 japan_rate_collector;电池算术按 live=81 校准漂移至 85) | Z0+R[legal85]+四电池 | ✓ |

路由: **(b) 上游漂移诚实报告**——禁当场改冻结件(fixt/baseline_locks/
equivalence/w4-d2/hca 一律未动,字节级 SAME 见 mfile_sha256.txt);修复路径归
后续重冻轮(DELIVERY §漂移维护)。

非常规件如实注记: test_glm_live.py 自护栏跳过(RUN_GLM_LIVE 未设,零 GLM 触碰,
红线 intact);fixt.py 直跑 exit 0(仅建 fixture 的模块护栏,tests/fixtures 零变化
——git status 无 fixtures 改动);此两件不在实验宇宙 66 套件内,计入本全量
69=66(实验宇宙)+A3+fixt+glm_live,66 绿含之,如实登记。

## §四 证据包(步骤⑪)

`/tmp/p03-e2eb-b3-evidence/IA-P03-E2EB-WP-B3-EVIDENCE.zip`(九类成员+SHA256SUMS;
装配后 zip 整体 sha256 按 R058 自指豁免先例补记于 DELIVERY 终笔):

1. 合同/设计引用件(AC v1.4 案A回做版 sha256 前缀 c878e5a8、DESIGN §六 WP-B3
   L222-226 摘录);
2. REPORT/DELIVERY 本轮全稿;
3. M 件 unified diff(8 文件,+195/−17)与 sha256 前后对照(mfile_sha256.txt,
   含白名单外 8 件字节级 SAME 断言);
4. A 件(japan_rate_collector.py/test_p03_e2eb_b3.py/japan_20261105.json 及
   指纹);
5. 真实采集原始回执(real/jgbcme.csv+real/irstci01jpm156n.csv,白名单域
   mof.go.jp/fred.stlouisfed.org 零凭证);
6. D16 证据快照(build_evidence_snapshot.py+sandbox/+research_snapshot_
   20261105_b3evidence.json,digest=8dc327664b8309fb;japan EXACT sha256=
   6bba4718759ba12546499c1bdc510a1157b87f9462408e14071967d29e14e7f1 全值;
   基线四通道 FALLBACK lag1;gate_a=DEGRADED vintage 合法,noncore_missing=
   [MARGIN_BAL,SB_FLOW,SH_PE]=china_20261104 真实档既有缺口(与演进无关),
   noncore_missing_boundary=JP 四条目恰=D7 设计);
7. data/daily 前后指纹(daily_pre.sha256/daily_post.sha256,16 文件零变化);
8. 实验与全量日志(exp-logs/ 66 套件+_summary、fullrun-logs/ 69 件+_summary、
   b3_exp.py/run_full_suite.py 工具);
9. 装入件清单(SHA256SUMS 全成员指纹)。

*(完;result.md 四节自报另出 stdout)*
