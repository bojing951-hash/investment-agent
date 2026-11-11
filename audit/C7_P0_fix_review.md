# Charter 7 P0 修复轮独立复验报告

- 复验员: 独立验证员(同第一轮 C7_P0_seven_issues_verify.md 作者;本轮只复验不修)
- 日期: 2026-11-10
- 复验对象: 分支 `dev/charter7-research-v1` commit `308f615`(父 `cca2e4a`,未合并未 push;main/origin 仍=`cca2e4a`,已核对 `git branch -vv`)
- 基线: 本人第一轮判定 #1 CONFIRMED / #2 CONFIRMED / #3 PARTIAL / #4 CONFIRMED / #5 CONFIRMED / #6 CONFIRMED / #7 CONFIRMED
- 方法声明: 只读复验;全部重放与独立手算使用 `~/AI内容/venv/bin/python3`(仅运行,零修改该目录);零网络;tempdir 模拟用官方测试缝 `trusted_root`;LIVE/launchd/远端/main 零触碰。**每条的独立复算均不引用 B 席测试期望值作为复算来源**(测试文件只用于交叉印证,不作数值来源)。

## 总判定

| # | 问题(第一轮判定) | 修复判定 |
|---|---|---|
| 1 | realtime 门语义(CONFIRMED) | **PASS** |
| 2 | 锚点/候选有效维度标准不一致(CONFIRMED) | **PASS** |
| 3 | aftermath 起止口径(PARTIAL) | **PASS** |
| 4 | 跨频率 36 月门槛(CONFIRMED) | **PASS** |
| 5 | 候选月份高度重叠(CONFIRMED) | **PASS** |
| 6 | 保留策略 vs 历史研究溯源(CONFIRMED) | **PASS** |
| 7 | update 未经授权触发付费模型(CONFIRMED) | **PASS** |

**总体判定: 七条全 PASS。附带修正三处确认均为真修复。测试改动逐项审查均为合法校准,未发现"改期望值制造通过"。独立全量套件: 112 个测试文件中 111 套全绿(1 套=test_model_live 按契约排除),与声明一致。未发现修复引入的新缺陷。**

---

## 1. realtime 门=查询时窗跨日 vintage 在场性 —— PASS

**修复内容**(ia_cli.py `_realtime_window_band` + scripts/analog_engine.py `realtime_gate_text` ~L351 + ia_cli compare 接线): 判据从"同日 `_vN` 在场性"(70102d5 方向)改为"**查询起点月窗内跨日 vintage(research_snapshot 基础日期)在场性**";带=[start, min(end, 起点月末)];`vintage_dates()`(research_provenance.py L1309,正则取基础日期,`_vN` 归并不新增日期)随行披露。

**本人第一轮 exploit 重放**(必须 blocked):
```
ia_cli compare --start 2024-06-01 --end 2024-06-30
→ realtime_info_set = "blocked: 查询期20240601~20240630起点月窗内无vintage快照
  (现存跨日vintage:20261108,20261110——历史时点信息集不可重构,修订值≠当时值,
  不得以今日修订口径冒充当时值; 当日修订版在场…)"
```
第一轮该场景为 available(以同日修订版冒充当时信息集)——现已按正确判据 blocked,且给出现存清单与如实原因。

**当前窗对照**(无 --start): `"available(现役快照即当前时点信息集;跨日vintage=2个[20261108,20261110];同日_vN修订不构成跨日vintage…)"`——语义正确: 现役快照本身就是当前时点信息集,同日修订只作尾注披露。

**边界独立性**(纯函数直测,B 席测试之外的独立复核): `realtime_gate_text` 带边界——vintage=起点日在带、前月末/次月首日均出带;同日 `_vN` 在场不翻 blocked(修订值≠当时值)。与 B 席 ⑨ 三形态断言交叉一致。

**回归锁**: test_afin_acceptance ⑨ 形态③显式锁死"同日 _vN 在场也不翻转"(对 70102d5 错误方向的方向反转回归锁)。

## 2. 统一特征集 U + 固定分母 W_U —— PASS

**修复内容**(analog_engine.py): `U=sorted(zs_anchor)`(锚点准入=距离特征面唯一决定);`W_U=Σfeat_w[k] for k∈U`(固定分母,全候选一致);候选循环仅遍历 U,缺席入 `missing` 附原因(`no_value_at_candidate_month`/`hist_n<req`/`sigma_0`);排序键 `(len(missing), D, month)` 双键;`weighted_distance(..., wsum_total=None)` 仅存留于独立单元测试的旧口径。输出新增 `feature_set{basis,features,n_features,wsum}`/`accounted_wsum`/`missing_features`/`missing_wsum`。

**真实数据双键排序证据**(data/daily=research_snapshot_20261110_v2,独立跑 analog TOP-5):
```
2024-12 D=0.326433 miss=2 (簇代表, 22 簇员 2024-01..2025-10)
2023-12 D=0.698587 miss=2   2022-01 D=0.809482 miss=2
2020-12 D=1.191539 miss=2   ← D 大于下行但缺席同为 2 → 双键下排前
2019-12 D=1.007559 miss=7   ← D 更小但缺 7 特征 → 不得反超
feature_set: n=17 wsum=0.638889 basis=anchor_admitted(统一特征集…)
top1 accounted_wsum=0.555556 missing_wsum=0.083333(和=W_U ✓)
```
**本人第一轮构造例重放**(偏差大但数据全 vs 距离小但缺 5 特征,前者必须胜): 合成序列 v3(在 Y−12 处 FED/UST/TIPS/CURVE 挖洞杀 4 个 d12m 特征+VIX 于 Y 挖洞,保留增长/通胀/利率水平/估值四维):
```
X=2022-01: D=0.474108, missing=0 → 簇代表, 榜首
Y=2023-02: D=0.057943, missing=5(CURVE_2S10S/FED_FUNDS/TIPS/UST_d12m+VIX_level)
           → 落入 2023-04 簇(簇员披露), 其代表仅列第 4
```
缺数候选距离再小也不得反超完整证据候选——与第一轮审计主张一致。

**独立复算**(不引用 B 席期望值):
- TOP-1 距离手算 `√(Σ w_norm·gap²)`=0.326434 vs 引擎 0.326433(6dp 舍入)✓
- UNEMP z 手算: μ=4.526891,σ=1.723281(n=119,ddof=0)→ z@2026-10=−0.247720;z@2024-12=−0.257155(n=98)——与引擎逐值一致 ✓
- HY_OAS ≤2024-12 观测手数=14=引擎 `hist_14<36` 原因 ✓
- W_U=0.638889 手算=Σ(1/6)/每维规格特征数 over U=17 ✓

## 3. aftermath 窗口起止观测日披露 —— PASS

**修复内容**: 逐资产逐 horizon 新增 `{资产}_window{start,end}`(实际起止**观测日**);`AFTERMATH_LABEL` 明示"起点=候选锚点月之后首个观测"与窗口随行口径;数值口径不变(仍为窗内末观测 vs 起点,不以 0%/缩短窗冒充)。

**独立验证**:
- 真实数据(候选 2024-12): `SPX_window`={"1m":{2025-01-02,2025-01-31},"3m":{2025-01-02,2025-03-31},"6m":{2025-01-02,2025-06-30},"12m":{2025-01-02,2025-12-31}}——起点/末观测日与本人第一轮从序列逐日手查的观测日一致;SPX 12m=16.647217 数值与第一轮手算一致(语义未变,现在可复算)。
- 合成探针(B 席外独立设计): UST 事后观测置 `2024-01-05=9.99`(12m 界=2023-12-31 之外)→ 12m 仍=0.75pp 而非 9.99−4.0(窗外观测不被吸窗);1m 末=窗内实际观测 2023-01-15 而非界日。
- 第一轮 PARTIAL 项(起点月内数据不得回吸): `起点不回吸锚点月内数据`——2022-12-15=1000 未入 2022-12 候选窗(3m≠(1210/1000−1))已由引擎行为与 B 席断言双侧证实。

## 4. 跨频率指标 36 月门槛(步长折算) —— PASS

**修复内容**: `_grid_step_months`=网格相邻键月差中位数;`min_observations(step)=ceil(36/step)`;锚点侧弃用原因分类披露(`release_lag`/`quarterly_grid`/`no_value_at_anchor`);候选侧同样按各自特征门槛;候选侧维度缺席新警示。

**独立重放(GDP_yoy 三连,坐标令指定)**:
```
11 季 → None(hist_11<12)   12 季 → z=1.5933(恰好门槛)
13 季 → z=1.6036(过界可算,门槛=最少观测)
min_observations 手算核对: step1→36, step2→18, step3→12 (=ceil(36/step)) ✓
```
真实数据锚点弃用披露 8 条(逐条与数据端点核对): INDPRO/RSAFS/GDP/CORE_CPI/CPI_yoy→`release_lag(序列止于2026-09,月度发布滞后一个月,如实缺席不以前值/插值冒充)`;HY_OAS_d12m/HY_IG_gap_d12m→`hist_24<36点`;SPX_PE_TTM_level→`no_value_at_anchor(止于2026-06,差4个月)`。第一轮"GDP_yoy 无声消失"→现在有因有据。

**候选侧维度缺席**(真实数据): `"候选侧维度缺席: 信用(credit)在全部有效候选上无有效特征…"`——第一轮只报锚点侧的盲区补齐。

## 5. 候选月份高度重叠(簇去重) —— PASS

**修复内容**: `CLUSTER_GAP_MONTHS=12`;TOP-N 只出**簇代表**(按 (缺席数,D) 排序后贪心,任意两代表相差≥12 月);相邻月候选入 `cluster_members` 披露;`dispersion` 判据(单维主导/事后分歧/分离度)全部改按独立簇代表口径,新增 `n_independent_clusters`;请求 N>簇数→实际输出 N'=簇数+簇不足警示。

**本人第一轮重放(2024-12+2025-01 相邻月)**: 真实数据 TOP-5 中 2024-12 为簇代表,簇员 22 个=[2024-01..2025-10]**含 2025-01**——第一轮"相邻月冒充独立样本"构造例已坍缩为簇员;TOP-5 五条代表两两相差≥12 月。`dispersion.basis="TOP-N 独立簇代表(候选月相差<12个月=同簇只计代表)"`,n_independent_clusters=5。合成斜坡 fixture(95 月)四代表恰为 2023/22/21/20-12(B 席),与贪心口径独立推导一致。

## 6. 保留策略与历史研究溯源兼容 —— PASS

**修复内容**(data_retention/research_provenance/snapshot_builder/research_history_query 四件套):
- `research_referenced_files`: 扫 research_snapshot_*.json 的 sources_status 各通道 `file` 字段(EXACT/FALLBACK 均收)入保护集;
- prune: 声明档→`protected_archived`(gzip 进 archive/,永不删);月度代表档照常 gzip;研究层档不触碰;
- `sources_status_problems`: 采集目录缺档→查 `archive/*.gz`;在场且 sha256(解压字节)一致→无问题+notes 披露归档事实;否则"已查采集目录与archive/*.gz——声明批次不可证明,研究溯源链断裂";
- `resolve_inputs` 归档回退(lag 窗约束+`archived:True`);`load_metric_series` 解压读回,sha256 按未压缩口径。

**本人第一轮 tempdir 模拟重放**(研究快照声明**非月度代表档** macro_20260119.json,保护必须显式触发):
```
A 清理前: sources_status_problems=文件日期陈旧警告(EXACT 旧档冒充当日采集,正交预存检查,应保留)——无来源档缺失问题
B prune: deleted=[0105,0112(未声明旧档)] protected_archived=[macro_20260119.json(声明档)]
         archived=[macro_20260126.json(月度代表)] 研究快照原样在场
C 清理后: data_dir 层=CLEAN + note "来源文件已按保留策略归档:archive/macro_20260119.json.gz
         在场且可读回(sha256与构建时一致,研究溯源链保持)"
D 对照(未声明被删档): →"…不存在且无归档…研究溯源链断裂"(仍正确拒绝,不放过)
E read_archived_source: 解压字节=原档(json 一致), sha256(解压)=构建时摘要 ✓
F 篡改对照(archive 写垃圾): → 溯源链断裂(摘要不匹配不放行) ✓
```
第一轮失败场景(声明档被 prune 物理删除→溯源链断裂)已消除;归档读回通道经本人模拟与 resolve_inputs/load_metric_series 归档回退测试双重证实(含"过窗归档不冒充"负对照: lag19>7→缺,不取)。

## 7. 新闻模型摘要显式 opt-in —— PASS

**修复内容**(news_collector.py `news_model_summary_mode`+run() 门 + ia_cli ENV_KEYS/--yes 提示 + doctor 面 + USER_GUIDE): 三参齐**不再**自动调用;唯一调用形态= `IA_NEWS_MODEL_SUMMARY=1` **且** MODEL_* 三参齐;否则确定性标题回退并如实说明。

**流程级零调用重放**(stub 采集/归档,仅门逻辑真实;计数器替代 `generate_news_summary`):

| 场景 | mode | generate_news_summary 调用数 | 回退 |
|---|---|---|---|
| A 三参齐+未 opt-in(**第一轮 exploit**) | off_optin | **0** | 确定性标题回退 ✓ |
| B 三参齐+opt-in=1(唯一付费形态) | model | 1 | — |
| C opt-in=1+三参不齐 | off_incomplete | 0 | 回退+如实说明 ✓ |
| D 全缺(默认) | off_optin | 0 | 回退 ✓ |

旧代码在场景 A 自动调用付费 API——现已零调用。`IA_NEWS_MODEL_SUMMARY=0`(≠1)亦 off_optin。doctor 面(独立运行核实): `{'configured': False, 'purpose': '新闻模型摘要显式开关(Charter7-7: 默认关闭;须=1 且 MODEL_* 三参齐才调用付费模型摘要…)'}`;USER_GUIDE 同步(三消费点表述+默认关闭)。**注意**: 周报叙事层/AI 研究解释仍按原三参语义运行(仅新闻摘要加门)——与章程"消除未授权付费调用"的第一轮指控范围一致,未扩大也未遗漏。

---

## 附带修正三处判定(确认=修复,非行为变更)

| 项 | 位置 | 判定 |
|---|---|---|
| (a) TOP-N 簇警示 f 前缀 | analog_engine.py L636-637 `f'TOP-{top} 请求但独立簇仅 {len(reps)} 个…'`;L614 候选侧维度缺席同 | **真修复**: 纯渲染修正,真实/合成重放均见插值后文本("…独立簇仅 2 个"),不影响判定/排序/距离 |
| (b) 分离度判据双键误读 | L673-674 `ds_sorted=sorted(x['D'] for x in dists)` | **真修复**: 双键排序后 `dists[0]`≠距离最小者,判据本义"(中位−最小)/中位<10%"按距离值排序取 min/中位;cca2e4a L507 旧形在旧单键排序下恰好正确,新排序下必须改——修复使判据在新排序下语义不变 |
| (c) missing_wsum −0.0 | L846 `round(W_U−accounted,6)+0.0` | **真修复**: 纯显示(0 缺席候选不再输出 −0.0);数值语义零变化(实跑 top1 miss=2→0.083333 正常) |

## 测试合法性审查(章程红线"禁改期望值制造通过")

| 文件 | 改动 | 判定 |
|---|---|---|
| tests/test_afin_acceptance.py ⑧⑨ | 方向回转(vs 70102d5) | **合法校准**: 被测语义本身经第一轮审计#1 判错而反转;新断言更严——⑧ 由"startswith('available')"泛断言改为锁定具体前缀"available(现役快照即当前时点信息集"+`realtime_vintage_dates` 清单随行;⑨ fixture 覆盖三形态+带边界+**同日 _vN 不翻 blocked 的方向反转回归锁**+真实面最早 vintage 边界。无同一语义下的放松 |
| tests/test_charter6_p4_analog.py(重写,82→101 断言) | 全套重写 | **合法校准+镜像独立性成立**: 期望值侧为测试自写实现——`build_feats`(月末值/yoy/d12m/gap 独立变换)、`ind_z`(自有 expanding μ/σ,population 口径)、`ind_step/ind_required`(自有中位数+ceil)、双键排序/贪心簇/分位均测试侧独立实现;**未调用任何引擎计算函数生成期望值再喂回**(仅引用声明性输入: `ae.FEATURE_SPECS` 规格表与 `fe.load_registry()` 注册表加载=配置面)。抽验: ①TOP-1 距离/全序/簇员=独立重算 1e-6;②W_U/norm_wsum 全候选一致=手算 6dp;③missing_features 原因字典=镜像;④ramp fixture 距离=闭式 `|z_a−z_j|`(独立 `ramp_z`);⑤D2 判据 4 分离度=测试侧 13 候选全表距离重算。旧 82 断言名对照: 被删名全部为新语义下更强等价物所替代(如旧"TOP-1 距离=独立重算"→新固定分母版+缺席双键版;旧 D1 重归一期望因 Charter7-2 语义变更而废弃属当然;旧"idx34(n=34<36)"系旧名标注错误,新名 n=35 修正标注同一断言)。无"同语义放松" |
| tests/test_ia_cli.py / test_charter5_zero_key_matrix.py | doctor 键面 | **合法校准(面确实扩了)**: 精确集合等断言扩入 `IA_NEWS_MODEL_SUMMARY` 且新增专断言(configured=False+purpose 含"默认关闭")——断言更强非更弱 |
| tests/test_p02_w3{,fix1..fix5}.py(六套,各 +2 行) | 各加一行 `os.environ.setdefault('IA_NEWS_MODEL_SUMMARY','1')` | **合法校准(=1 setdown 属实)**: 新门使"mock 模型摘要路径"须显式 opt-in 才可达;六套件均 mock 模型调用并断言其产物,不加此行则被测路径失联。断言本体零改动;未 opt-in 零调用路径由 test_charter7_p0 独立覆盖。非弱化 |
| tests/test_charter7_p0.py(新,579 行) | 七修全覆盖 | 单元期望值为字面手算值(如 0.26/0.25/√(0.9·0.26²));⑦流程级零调用与本人独立重放结论一致 |

## 独立全量套件

CI 同款逐文件执行(`for t in tests/test_*.py; do python3 "$t"; done`,test_model_live 按契约排除):

```
PASS=110 FAIL=0 SKIP=1 TOTAL_FILES=111
(test_model_live=真实付费API验收套件,CI 契约显式排除——即 111 文件中
 110 套执行全绿 + 1 套按契约跳过)
```

与"111 文件全绿"声明一致(CI 口径下 skipped 即绿)。抽验: test_charter7_p0 60/0、test_charter6_p4_analog 101/0、test_afin_acceptance 33/0(+8 按设计跳过)、test_p02_w3 38/0。5 个日志含 ❌ 字样者均为负向对照 fixture 的内部输出(绿套件内被测降级路径的如实打印),非断言失败。日志: /tmp/c7r_suite_logs/(111 套)。

## 新缺陷与回归扫描

- 未发现修复引入的新缺陷。逐项核过的高风险面: ①compare 带 --start 当前月窗仍 available(语义正确);②双键排序对真实 TOP 序的重排(2020-12 上移 2019-12 下移)即修复本义,非回归;③resolve_inputs 归档回退仅在窗内无现行档时触发+lag 约束+archived 旗标,过窗归档不冒充(负对照在测);④sources_status 的 EXACT 旧档 file_date≠target 检查对归档档仍触发(正交预存检查,应保留);⑤`vintage_dates` 把现役快照基期也计入(历史窗 blocked 文案中的"现存清单"含 20261108/20261110)——语义正确(清单=现存跨日快照全集)。
- 观察项(非缺陷): test_afin ⑨ 真实面 `_vm+'31'` 月末界日在二月会构成非法日期串,但带语义按字符串界+min(月末)钳制,且现役最早 vintage=202611(11 月),当前不可达;如未来二月 vintage 首现可顺手改用日历月末。

## 红线核查

- LIVE/launchd/远端/main: 零触碰(main=origin=cca2e4a;工作树仅新增本报告,未 push 未合并)。
- 零凭证入档: diff 全文扫描 `api_key=…/sk-…/Bearer/password=` 零命中;tempdir 模拟用合成摘要。
- 公开面零厂商字样: diff **新增行** 厂商A/厂商A/厂商A 零命中(命中的两处均为预存上下文行与 test_charter5 的"无厂商词"负向断言自身)。
