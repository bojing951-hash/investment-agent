# IA-P1-GAP08 REPORT(快照接线+研究消费面收口轮)

- 工作包: IA-P1-GAP08-WIRING-AC-v1.1(R061;GAP-P1-08 快照 facts/series_store/provenance 接线 F1/F2/F3/F6+F4+R047-F1/F3+三轮审计 DEFERRED 注记收口;F5 排除)
- 契约: IA-P1-GAP08-WIRING-AC-v1.1(FROZEN 2026-11-06;v1.0 情形(d)停止后 §十 单值勘误重发;操作者注入全文,逐节实读)
- BASE-GAP08: 82d41e214b99f09bf4521c137261f61f17a3e5ff(=origin/main,开工 ls-remote 实取=同值)
- 分支: dev/p1-gap08(自 BASE-GAP08 切出,纯线性,零 push)
- CI 基线: 73 槽(run 42101669112:72 exit=0+1 test_glm_live SKIPPED;本轮新增测试文件恰 1→预期 74 槽=73 exit=0+1 SKIPPED)
- BRANCH-SET: 冻结 45 支(main=82d41e2…;dev/p1-design=049ec978…);唯一预期新增=dev/p1-gap08
- 数据三档(只读豁免登记,sha256 开工复算一致): jp_20261105.json=7f0bdeb100d332ea9579a594656c2783eed4794b73b624b4436d60fe8ca78ae3 / japan_20261105.json=6bba4718759ba12546499c1bdc510a1157b87f9462408e14071967d29e14e7f1 / ea_20261105.json=e6db3ddf226652da114e56652d2ce8f4664462b744d306e631de3454b911aeaa

## §零.1 保险四自检(开工实录)

| 项 | 结果 | 方式 |
|---|---|---|
| ① ls-remote main | 82d41e214b99f09bf4521c137261f61f17a3e5ff | `git ls-remote origin main` 实取 |
| ② HEAD=同值+工作树洁净 | 过(HEAD=同值,status clean,main) | `git rev-parse HEAD`+`git status --porcelain` 空 |
| ③ 规格链五源在场实读 | 过(三 DEV 文档实读+二引擎侧 audit 条以合同注入抄录,见 §零.2) | Read/grep 实测 |
| ④ 数据三档 sha | 过(三值与合同红线一致) | `shasum -a 256` 实算 |

## §零.2 规格链五源逐字锚抄录(grep 实测复核;引擎侧条目标注「注入」)

**源1** `docs/P1_WP_B_REPORT.md` §零.9(L128 节起)F1-F6 表(L132-137 实测):

| # | 逐字抄录(发现列) | 行号实测 |
|---|---|---|
| F1 | "build_snapshot facts 级 jp/ea 接线(L273-304 仅 4 通道)" | L132 |
| F2 | "series_store 增 NIKKEI225/DAX/CAC40 序列键" | L133 |
| F3 | "_SOURCE_TO_INPUT 增 jp/ea(缺席从 boundary 转 noncore_missing)" | L134 |
| F4 | "fixt.py L214 注释\"NIKKEI225∈[5000,60000]\"将随 (e) 上限调整而陈旧(值 38000 本身仍合法∈新区间)" | L135 |
| F5 | "EA 双源对账候选(DESIGN §三(a-3) cross_metric_checks EA 候选): ECB_MRO/DFR 双源(BBK vs ECB)在真实首档不可实现(DFR=READ_FAIL 缺席)" | L136 |
| F6 | "jp 对账输入(build_all 内)与 japan 通道事实的比对命中路径: build_all 无 japan_data 入参且 japan 通道 normalize 未接线(B3 D7), 对比恒 skip";承接列="japan normalize 接线属 F1/F3 同轮 \| 同 F1" | L137 |

**源2** `docs/P1_WP_D_REPORT.md` §一.6:
- F1(L157 实测): "「研究任务记录增 economy 字段(候选,WP-P1-D 落地)」……RT- 记录体增字段的完整落地需操作者处置(后续包授权或合同修订),本包不越界。"
- F3(L159 实测): "§四 L130「查询覆盖面扩展至新 metric_id,economy 字段可作过滤维度」的消费方=research_history_query(E2E-A 侧);本包交付 IR 携带维度+schema 校验,消费面接线=白名单外,登记待后续处置。"

**源3**【注入】rounds/045/audit.md DEFERRED-1(引擎侧不可达,合同 §零 注入抄录): "P1_WP_B_REPORT.md §零.1 L20 指针滑笔勘正(「更正见 §零.16.3」→实为 **§零.16.2**,单行)"——DEV 侧在场性实证: P1_WP_B_REPORT.md L20 现值含"更正见 §零.16.3";§零.16.2(L246)=禁锚措辞失实更正节,§零.16.3(L252)=v1.2 zip 终笔节——指针确指错节,勘正目标=§零.16.2 成立。

**源4**【注入】rounds/046/audit.md DEFERRED-1/2(同上注入抄录): D1="P1_WP_C_DELIVERY §三 AC-05 行 v1.1 时点残留(diff 恰 3A+3M+0D)补 v1.2 注记(权威值 3A+4M 已在 §一)"——DEV 侧实证: C_DELIVERY L37 现值"diff 恰 3A+3M+0D";§一 L22 权威值"恰 3 行 A(A1-A3)+4 行 M"。D2="§零.7 t05「20 legacy 键」勘误族补一行注记(实际断言=19 键)"——DEV 侧实证: 「20 legacy 键」文字在场=P1_WP_C_REPORT.md §零.7 t05 行(L135,"20 legacy 键在+无 economy 键");REPORT L224 勘误③已记"§零.6-a4 legacy 键计数 20→19"但 §零.7 t05 行未随注;注记落点=C_DELIVERY(白名单 (g)),单行。

**源5**【注入】rounds/047/audit.md DEFERRED-1(同上注入抄录): "P1_WP_D_DELIVERY §五 辅锚缘偏(L170-186→L165-179)注记"——DEV 侧实证: D_DELIVERY §五 fixture→预期值映射表 t24-t29 行(L70)现值"_record@L170-186";tests/test_p1_wp_d.py `_record` 实测 def@L165/return@L179——勘正值 L165-179 成立。

**上游设计依据(只读)**: `docs/P1_DESIGN.md` §四 L130(economy 过滤维度)/L143(RT- 侧 economy 字段候选)——L130/L143 逐字 grep 实测在场。

**F3 第三键值依据(v1.1 §十 勘正值 'japan')**: tests/helpers/baseline_locks.py L279=`'japan_rate_collector': 'japan'` 与 scripts/historical_coverage_audit.py L110=同值(双先例实测);japan_*.json=japan_rate_collector 采集档(通道键 'japan'),SOURCE_FILE_RULES L173 'japan' 前缀恰为其归属(rp L168-176 实读)。

## §零.3 白名单与清单

- M 白名单: 合同 §零 表实列 **8 行 (a)-(h)**=scripts/snapshot_builder.py(a)/scripts/research_provenance.py(b)/scripts/research_task_manager.py(c)/scripts/research_history_query.py(d)/tests/fixt.py(e)/docs/P1_WP_B_REPORT.md(f)/docs/P1_WP_C_DELIVERY.md(g)/docs/P1_WP_D_DELIVERY.md(h)——合同文面宣"M 恰 9 件/条件类零触发时 diff 恰 M9+A3"与表列 8 行**计数不一致**(滑笔,如实登记;实现面对齐表列 8 行,零表外文件,+条件类 (j)。开工预登记原按"M 恰 9=(a)-(h)+(j)"理解,本行已按表列实数更正,原样披露)。条件类 (j) 开工预判触发=wp_b/wp_c 两件,实测 5 件(§一.10)。
- A 恰 3: tests/test_p1_gap08.py/docs/P1_GAP08_REPORT.md/docs/P1_GAP08_DELIVERY.md。D=0。
- `git ls-files` 与 A 类零重合(三件均为新路径)。

## §零.4 实现形态预登记(先登记后实现;运行后禁回改)

1. **F1(build_snapshot facts 段 jp/ea/japan 接线)**: L273-304 邻域在四通道分支后追加——`jp`: `fe.normalize_jp(raw['jp'], as_of, sources_status['jp']['file'])[0]`;`ea`: `fe.normalize_ea(...)[0]`;`japan`: 模块本地 `_normalize_japan(raw['japan'], as_of, sources_status['japan']['file'])`(flat 形态 data.{mid}+observations.{mid},经 `fe.make_fact/fe.validate_fact/fe.grade_issues` 现成函数产 4 事实,collector='japan_rate_collector';**fact_engine 零改**;依据=源1-F6 承接列"japan normalize 接线属 F1/F3 同轮"+F3 第三键 japan_rate_collector→'japan' 落地后 japan 档在场而无事实=虚构"采集遗漏"披露,必须接线以保持 FIX4-03 诚实语义;测试先例=_japan_facts 构造形态 test_p1_wp_b.py L120-133)。缺源(键不在 raw)=来源级缺失照实披露(resolve_inputs 已产 MISSING/sources_status,不进 facts);core 指标缺席 fail-closed 语义保持(13 新指标 criticality 全=important,core 面零涉)。
2. **F2(series_store 三键)**: L358-382 邻域 china 池后追加 jp/ea prices 池——遍历 `raw['jp']['prices']`/`raw['ea']['prices']`,键=registry metric_id 实读(fe.metric(key) 在场且 source=对应采集器;现注册面恰=NIKKEI225(jp)/DAX+CAC40(ea));序列=档内 series **值直通**(形态转 {'dates':sorted,'values':[按序]} 与 global/china 池统一——消费面 correlation_calculator.paired_returns(L60-73)/rhq._clean_series 均吃该形态;值零改写零造数,先例=normalize_jp series 转换 WP-B §零.10.4)。
3. **F3(_SOURCE_TO_INPUT 三键)**: rp L111-117 邻域恰增三键 `jp_market_collector→'jp'/ea_market_collector→'ea'/japan_rate_collector→'japan'`(v1.1 §十 勘正值;双先例 baseline_locks L279/hca L110);SOURCE_FILE_RULES 零改(已含三前缀,L168-176 实读)。口径翻转面: jp/ea/japan 指标缺席自 boundary 记录转入 noncore_missing(来源在场=采集遗漏/来源缺失=来源级缺失,rp L1059-1071 既有两分支)→Gate A effective 至少 DEGRADED(FIX4-03 既有语义)。
4. **F6(对账输入启用判定)**: F1 接线后 normalize_jp 返回的 jp 对账输入(BOJ_POLICY_RATE→JP_POLICY_RATE/JGB_10Y→JGB10Y/JGB_2Y→JGB2Y,_JP_RECON_MAP 档内既有)在 build_snapshot 内消费: **判定条件=当次事实集中存在 japan 通道事实(source.collector=='japan_rate_collector')**;命中→逐条按既有对账规则(rate_recon_extra 同式: diff/rel<0.005→consistent 否则 diff-needs-review,观测日不同附注)产出 source-diff 记录进 reconciliation;无对手方→如实不进(不伪造);**fe.build_all docstring 陈旧括注在 fact_engine.py L842-845(实测)——按合同步骤5 只登记不改,情形(b) PENDING**(见 §四)。
5. **F4(fixt 注释勘正)**: L214 "NIKKEI225∈[5000,60000]"→"[5000,150000]"(registry v2.2.0 实值,t19 锁);同族陈旧接线注释 2 处同笔勘正(japan L197-198/ea L218-219 "本通道事实提取未接线(_SOURCE_TO_INPUT 无 japan|jp/ea 键)"→已接线注记)——1:1 登记 DELIVERY 演进表;零功能改动。
6. **R47-F1(RT- economy 字段)**: build_task 内增派生辅助 `_task_economy(indicators)`——经 registry.economy 实读派生指标族经济体集合,**恰单值→task 增顶层 'economy' 键(条件写);跨经济体/零值→不写键**(形态先例=WP-D PD-4 恰单族命中才写 ir["economy"];默认任务 TIPS_10Y(US)+GOLD_F(GLOBAL)=跨经济体→如实不写键);DESIGN L143"任务体其余字段含 falsifiable_conditions 不变"=既有键零改;schema=可增不可减(SCHEMA_MIN_FIELDS 不动)。
7. **R47-F3(rhq economy 过滤维度+覆盖面)**: ①ECONOMIES 常量(US/CN/JP/EA/HK/GLOBAL,registry 值域实测同集;先例=qir.ECONOMIES PD-1);②load_metric_series 增 jp_market_collector/ea_market_collector 接入点(=接入点B 快照 series_store 同路,post-F2 NIKKEI225/DAX/CAC40 在 store;jp_/ea_ 档禁直读约束保持——查询只吃快照层,DESIGN L130);japan_rate_collector 无序列(flat 单点)→无接入点,ValueError 既有文案如实;③payload 增 'economy' echo(m.get('economy'),四接入点统一);④query_window 增可选 economy 参数——非 None 且与 payload.economy 不等→如实空窗(coverage.note 披露过滤不命中,不造数据);⑤_main 增 --economy(choices=ECONOMIES,CLI 边界校验)。
8. **文档三注记**: (f) L20 单行勘正 §零.16.3→§零.16.2+§零.9 表 F1-F6 各行/表尾处置注记(处置=R061);(g) §三 AC-05 行 v1.2 注记(权威值 3A+4M 在 §一)+勘误族单行注记(REPORT §零.7 t05 行"20 legacy 键"=勘误族,实际断言 19 键);(h) §五 t24-t29 行辅锚注记(L170-186→L165-179)+F1/F3 承接回填注记。均一处一行,措辞照合同 §零 源条目。
9. **DP 判定**: 零新增(纯接线零服务调用零判据引入;economy 取值=registry 值域族内,WP-D §零.5 先例)。

## §零.5 (j) 涟漪勘正预判(F3 口径翻转的直接受影响断言;实现后逐一 1:1 实录 DELIVERY §五)

预判红面(全部=F3 来源映射口径翻转的直接涟漪): test_p1_wp_b t13/t14/t16/t18(boundary→noncore_missing 预期值+7通道快照 facts 含新通道)+t20 零涉(fe 直调);test_p1_wp_c L438(gate PASS→DEGRADED,7通道 canon 日 JP_CPI/DAX/CAC40 诚实缺席入 noncore_missing)。其余套件负向排查以本地全量实录为准(§一.4);预登记外新红→情形(b) PENDING 不当场改。

(以下 §一-§六 实现后回填)

## §一 实现实录(§零.4 预登记形态逐项落地,零回改)

### §一.1 F3(scripts/research_provenance.py L117-124)
_SOURCE_TO_INPUT 追加三键 `'jp_market_collector': 'jp'/'ea_market_collector': 'ea'/'japan_rate_collector': 'japan'`(注释含承接链+勘误依据+双先例锚);SOURCE_FILE_RULES/SOURCE_CHANNELS 零改(jp_/ea_/japan_ 前缀与基线四通道冻结原样)。口径翻转生效: jp/ea/japan 指标缺席自 boundary 记录(L1060-1071 unmapped 分支)转入 FIX4-03 noncore_missing——来源在场=「来源文件在场而指标缺席(采集遗漏)」(L1077)/来源缺失=「来源文件缺失({ch}:{status})」(L1079),双分支实测见 §二 测试 g04/g05。

### §一.2 F1(scripts/snapshot_builder.py L335-351+适配器 L234-262)
- jp: `if 'jp' in raw:` → `fe.normalize_jp(raw['jp'], as_of, sources_status['jp']['file'])`(L339-342),facts 入列+对账输入留 F6;
- ea: `if 'ea' in raw:` → `fe.normalize_ea(...)[0]`(L343-345);
- japan: `if 'japan' in raw:` → 模块本地 `_normalize_japan(raw['japan'], as_of, sources_status['japan']['file'])`(L349-351)——flat 形态 data.{mid}+observations.{mid} 经 fe.make_fact/validate_fact/grade_issues 产 4 事实,collector='japan_rate_collector'(fact_engine 零改;构造形态先例=WP-B t13 _japan_facts;承接依据=源1-F6 承接列"japan normalize 接线属 F1/F3 同轮"——F3 japan 键落地而无 japan 事实=虚构"采集遗漏",故必须同轮接线);
- 缺源(键不在 raw)=来源级缺失照实披露(resolve_inputs 已产 MISSING,不产事实不填 0);core 面零涉(13 新指标 criticality 全=important)。

### §一.3 F6(scripts/snapshot_builder.py L352-373)
判定条件=当次事实集存在 japan 通道事实(`any(f.source.collector=='japan_rate_collector')`);命中→normalize_jp 对账输入(_JP_RECON_MAP 已映射 JP_POLICY_RATE/JGB10Y/JGB2Y)逐条与 japan 事实比对: diff/rel<0.005→consistent 否则 diff-needs-review,观测日不同附注(rate_recon_extra 同式);无对手方→如实不进 reconciliation(不伪造)。fe.build_all docstring 陈旧括注(fact_engine.py L842-845,实测)——fact_engine 零改红线内**只登记不改**,情形(b) PENDING 见 §四。

### §一.4 F2(scripts/snapshot_builder.py L450-469)
jp/ea prices 池遍历: 键=registry metric_id 实读(fe.metric 在场且 source=对应采集器);序列=档内 series **值直通**,形态转 {'dates':sorted,'values':[按序]} 与 global/china 池统一(消费面 correlation_calculator.paired_returns L60-73/rhq._clean_series 均吃该形态;值零改写零造数,先例=normalize_jp series 转换 WP-B §零.10.4);prices 节缺席(真实首档 ea 形态)=诚实缺席不造序列;WP-C 跨域对(NIKKEI225×USDJPY/DAX×EURUSD)自此数据面可用。

### §一.5 F4(tests/fixt.py 三处注释,零功能改动)
L214 "NIKKEI225∈[5000,60000]"→"[5000,150000]"(registry v2.2.0 实值,t19 锁);L197-198 japan"本通道事实提取未接线"→已接线注记(F1/F3);L218-219 jp/ea 同族→已接线注记(normalize_jp/ea 入 build_snapshot facts)。1:1 登记 DELIVERY §五演进表。

### §一.6 R47-F1(scripts/research_task_manager.py L56-76+L151-155)
RT_ECONOMIES 常量+`_task_economy(indicators)`(registry.economy 实读集合恰单值且∈值域→该值;跨经济体/零注册/零值→None);build_task 内条件写 `task['economy']`(恰单经济体才写键);默认任务 TIPS_10Y(US)+GOLD_F(GLOBAL)=跨经济体→如实不写键(形态先例=WP-D PD-4);schema 可增不可减(SCHEMA_MIN_FIELDS 不动),falsifiable_conditions 等既有键零改。

### §一.7 R47-F3(scripts/research_history_query.py)
①ECONOMIES 常量(L77);②jp/ea 接入点(ACCESS_POINTS L69-72+load_metric_series 快照通道分支 L151-175,=接入点B series_store 同路;jp_/ea_ 档禁直读保持);③payload 'economy' echo(L141 macro/L166 快照,四接入点统一);④query_window 可选 economy 参数(L184-202: 非 None 且≠payload.economy→如实空窗+coverage.economy_filter 披露,不造数据);⑤_main --economy(choices=ECONOMIES,CLI 边界校验,L337)。japan_rate_collector=flat 单点无序列→无接入点,ValueError 既有文案如实(g13)。

### §一.8 文档三注记(一处一行,零扩写)
(f) P1_WP_B_REPORT.md: L20 "§零.16.3"→"§零.16.2"(单行)+§零.9 F1-F6 六行承接列追加 R061 处置注记(F5 注"仍排除");(g) P1_WP_C_DELIVERY.md: §三 AC-05 行 v1.2 注记(权威值 3A+4M 在 §一)+§五.2 勘误族单行注记(t05"20 legacy 键"实际=19 键);(h) P1_WP_D_DELIVERY.md: §五映射表 t24-t29 行辅锚勘正(L170-186→L165-179)+§七 F1/F3 承接回填行。

### §一.9 DP 判定
零新增(纯接线零服务调用零判据引入;economy 取值=registry 值域族内,WP-D §零.5 先例)——与 §零.4-9 预登记一致。

### §一.10 (j) 涟漪实录(§零.5 预判 2 件+实测新增 3 件,全部 (j) 覆盖面内)
预判面(§零.5)按预登记落地: test_p1_wp_b t13/t14/t16/t18+test_p1_wp_c L438。本地全量首跑(74 槽)另出预判外新红 3 件: test_p1_wp_a t2c_d7/test_gate_chain_p01(5 处 check)/test_e2e_frozen14(E2E-02d/02d2)——逐处诊断(§二.2)全部为 F1/F3 授权面直接涟漪(三键在场翻转 boundary 冻结断言/jp+ea fixture 诚实缺席三指标入 noncore_missing 使 fixture PASS 日重算 DEGRADED 的声明一致族断言),属合同 (j)"既有测试若因 jp/ea 接线/来源映射口径翻转出现预期值红"(不限文件)覆盖面内,**非**"预登记外新面"→同链 1:1 勘正+逐处登记 DELIVERY §五演进表(13 处),禁删/禁 skip/禁语义弱化。(j) 触发面实测=5 文件,§零.3 预登记行(2 件)为预判值,实测以此节为准。

## §二 测试与本地镜像实录

### §二.1 新套件 tests/test_p1_gap08.py(13 测/6 类,首次运行即绿)
- TestF1SnapshotWiring g01(10 新事实值/权属/批次绑定+诚实缺席不造数据)/g02(缺源 MISSING+13 来源级缺失+boundary 空+DEGRADED);
- TestF2SeriesStore g03(NIKKEI225/DAX/CAC40 三键+{dates,values} 形态+值直通逐值复核+SPX 零回归);
- TestF3SourceMappingFlip g04(来源在场指标缺席=采集遗漏 13 项+boundary 清空)/g05(来源级缺失理由串如实区分);
- TestF6Reconciliation g06(3 条 source-diff consistent+差+0.0000)/g07(无 japan 对手方零伪造);
- TestR47F1TaskEconomy g08(派生四态)/g09(默认跨经济体不写键+同族条件写 US+schema 不减);
- TestR47F3RhqEconomy g10(ECONOMIES=registry 值域实取)/g11(economy echo+jp 快照接入+macro 不变)/g12(过滤命中/None/不命中三态)/g13(japan_rate 无接入点 ValueError)。

### §二.2 负向敏感性注入(3 组,红→复原→绿→零残留)
| 注入 | 红面 | 复原 |
|---|---|---|
| ①删 _SOURCE_TO_INPUT 'jp' 键 | g02/g04/g05 3 红(缺源详情+两 Gate 重算) | 绿,sha 复原一致 |
| ②F1 jp 接线禁用(`if False and`) | g01/g06 2 红(事实缺席+对账缺席) | 绿,sha 复原一致 |
| ③F2 ea 池键删 | g03 1 红(KeyError DAX) | 绿,sha 复原一致 |
零残留=pre/post sha256 双文件全等(diff 空);注入日志+sha 全值入证据包④类。

### §二.3 本地全量镜像(CI 同款逐件退出码)
首跑(实现态+预判面修缮后): 74 槽=70 exit=0+1 skipped+3 exit=1(wp_a/gate_chain_p01/e2e_frozen14)→§一.10 诊断+(j) 勘正;**终跑: 74 槽=73 exit=0+1 test_glm_live SKIPPED**(逐件退出码=证据包④类 summary;test_glm_live=CI 同款设计性跳过如实注记)。

## §三 分支/红线/生产隔离处置(情形(a))
- 情形(a)受理: 终跑全绿→CI dispatch=操作者 CHECKPOINT 面,执行席未自行触发;
- 分支: dev/p1-gap08 自 BASE-GAP08 切出,纯线性,零 push/零 amend/零 force(reflog 佐证=证据包③类);
- 红线核验(命令+输出摘要=证据包⑤类): LIVE real_data_acceptance.py sha256=f9ca189c…fe3eb 全值一致+LIVE 目录 grep 零命中;china_market_collector.py/metric_registry.json/launchd/.github/.gitignore/test_glm_live/data-daily diff 零涉;数据三档 sha 复算与 §零 红线一致;零网络零 GLM 零凭证(源码 grep 证成);
- 45 支既有分支尖端逐一比对零漂移+唯一新增 dev/p1-gap08(证据包③类 ls-remote 全表)。

## §四 白名单外发现登记(PENDING,不越界)
1. fe.build_all docstring 陈旧括注(fact_engine.py L842-845 实测"japan 通道未接线"类文案)——F6 消费已在 build_snapshot 落地,但 fact_engine 属本轮零改红线(合同 §1 "fact_engine/registry/china 采集器/SOURCE_FILE_RULES 零改"),**只登记不改**,情形(b) PENDING,建议下轮触碰 fact_engine 时勘正;
2. 其余零新发现(F5=合同明列排除非发现;结构性缺口 series_store 不含 macro 利率序列=既有登记,rhq 模块头沿用)。

## §五 逐要点证据映射(恰 10 行;F5 排除见表尾)

| # | 要点 | 实现落点(file:line 实测) | 测试锚 |
|---|---|---|---|
| 1 | F1 build_snapshot jp/ea/japan facts 接线 | snapshot_builder.py L335-351(适配器 L234-262) | test_p1_gap08 g01/g02 |
| 2 | F2 series_store 三键值直通 | snapshot_builder.py L450-469 | g03 |
| 3 | F3 _SOURCE_TO_INPUT 三键+口径翻转 | research_provenance.py L117-124 | g04/g05(+wp_a t2c 勘正) |
| 4 | F4 fixt 三处注释勘正 | fixt.py L197-200/L214/L218-220 | 注释面零功能(t19 锁 registry 值) |
| 5 | F6 jp 对账输入消费判定 | snapshot_builder.py L352-373 | g06/g07 |
| 6 | R47-F1 RT- economy 条件写 | research_task_manager.py L56-76/L151-155 | g08/g09 |
| 7 | R47-F3 rhq economy 过滤维度+覆盖面 | research_history_query.py L69-77/L141/L151-175/L184-202/L337 | g10-g13 |
| 8 | 源3 R045-D1: B_REPORT L20 指针勘正 | P1_WP_B_REPORT.md L20(§零.16.3→§零.16.2) | grep 实测(证据包①类) |
| 9 | 源4 R046-D1+D2: C_DELIVERY 两注记 | P1_WP_C_DELIVERY.md §三 AC-05 行+§五.2 | grep 实测 |
| 10 | 源5 R047-D1: D_DELIVERY 辅锚+承接回填 | P1_WP_D_DELIVERY.md §五表行+§七 | grep 实测(_record@L165-179) |
| — | **F5 EA 双源对账=合同明列排除**(数据受阻 DFR=READ_FAIL 缺席如故),本包零实现零触碰 | — | — |

## §六 证据包与 zip 定值登记
(终笔回填=DELIVERY §六 同源;装配 stdout 与独立复算一致为准)
