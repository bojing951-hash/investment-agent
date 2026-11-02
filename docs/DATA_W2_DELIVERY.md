# IA-DATA-W2 交付文档(DELIVERY)

- **轮次**: Round 009(IA-DATA-W2 指标覆盖全量审计)
- **分支**: `dev/data-coverage`,基 = `7cbef4c9`(IA-DATA-W1 尖端)
- **性质**: 只读诊断轮,**零修复实施**。白名单 4 新文件(A 工具 / B 测试 / C 报告 / D 本文档),既有文件零改动。
- **审计窗口**: `data/daily/` 当前 12 文件(baseline 清单 2026-11-02T03:14Z,收尾复核逐字节一致)

---

## 一、用法(A `scripts/metric_coverage_audit.py`)

```bash
python3 scripts/metric_coverage_audit.py \
    --registry config/metric_registry.json \
    --data-dir data/daily \
    [--out /tmp/audit_output.json]
```

- **参数**: `--registry` 与 `--data-dir` 均为必填(**刻意不设仓库相对默认值**——防止无参误跑触达真实路径,测试夹具由此保证全离线);`--out` 可选,省略时仅打印人类可读摘要到 stdout,JSON 走 stdout 末段。
- **退出码**: `0` = 审计正常完成(无论发现多少缺失——缺失是审计产出而非运行错误);`2` = 输入错误(registry/data-dir 不存在或非法 JSON,详细信息走 stderr)。
- **仅标准库**: argparse/datetime/hashlib/json/os/re/sys,无任何第三方依赖,本地 3.9.6 与 CI 3.11 双环境可跑。
- **只读**: 对 `--data-dir` 内文件仅 `open(...,'r')` + sha256 流式读取,不写不删不改权限。
- **输出 JSON 结构**: `schema_version` / `generated_at`(UTC)/ `registry`(路径+sha256+条目数)/ `window`(入窗文件数、按通道统计、逐文件 sha256)/ `metrics[]`(每 registry 条目一行: metric_id, state, value, observation_date, files[](按日期升序的逐档证据: file/date/sha256/value/observation_date), deps, source, source_symbol, status) / `state_counts`(8 机械状态计数)。

**人类可读摘要语义**(stdout 首段): 逐非 PRESENT/DERIVED_READY 指标打印 `metric_id 状态 值@观测日 ←最近文件证据`;末段打印 state_counts 与"非正常计数"。

### B 测试(`tests/test_metric_coverage_audit.py`,15 用例,全离线)

```bash
python3 tests/test_metric_coverage_audit.py    # unittest,无 pytest 依赖,期望 OK
```

合成 registry(21 条目,含 MYSTERY 未知来源与 deprecated 项)+ tempfile 四通道夹具;CLI 用 `sys.executable` 子进程直跑脚本本体。分组: M(4 场景含别名)/ W(窗口历史多档)/ X(派生+弃用+未知来源)/ C(6 退出码语义)/ R(负向敏感性: R1 值盲退化、R2 PATH_NULL/KEY_ABSENT 混淆退化——以 importlib 加载文本降级副本,断言降级版**确实误报**且正确版通过,并演示 M2 断言在降级版上会红)。

---

## 二、分类规则与判定口径

### 2.1 registry 实取结构摘录(config/metric_registry.json)

- `version: 2.0.0`;metrics 数组 **81 条**;逐条字段(实测键集): `metric_id / source / source_symbol / status / asset_class / calc / calendar / criticality / display_name / frequency / freshness / identity / unit / validation / value_type`。registry **不记录**目标文件与字段——指标→文件→字段映射由本工具从引擎读侧面反推(见 2.3)。
- source 分布: `global_market_collector` 32 / `macro_collector` 28 / `rate_expectations` 4 / `china_market_collector` 12 / `fact_engine(derived)` 4 / `macro_collector(derived)` 1。
- status: active 80 + deprecated 1(REAL_SHORT,replaced_by REAL_5Y;其值存于 macro 顶层 `derived` 字典,引擎事实面不消费——按 registry 设计弃用,报告内注记)。
- 本轮审计时点 registry sha256: `60ef058a2fb1e12cb0786f0d4b977e3e084c0ca4aa7798debdbe0266b18097ed`(锁定判定所依据的注册表版本)。

### 2.2 机械状态(工具 8 态)→ 主状态(N/S/B/C/U)映射

| 机械状态 | 定义 | 主状态 |
|---|---|---|
| PRESENT | 路径全层存在,叶键有值 | N |
| PRESENT_NULL | 路径全层存在,叶键为 null | S(映射口径一致,值缺席=源端失败) |
| PATH_NULL | 路径中间节点为 null(如 `margin: null`) | 默认 S;若采集端任何成功路径都写不出引擎期望键→B |
| KEY_ABSENT | 容器在档但键缺席(如 `a_share_indices: {}`) | 同上仲裁 |
| FILE_ABSENT | 当窗某通道无文件 | S(通道粒度) |
| DERIVED_READY | 派生依赖齐备且可计算 | N |
| DERIVED_BLOCKED | 派生依赖不齐 | S(依赖粒度,报依赖缺席明细) |
| MAPPING_UNRESOLVED | source 不在已知映射表(未知来源) | U |

**B-over-S 仲裁规则**(REPORT §二规则3): 机械事实只能证明"当窗没值";判 B 需**代码侧证据**——引擎读侧期望键 vs 采集端全部成功路径实写键集合比对,若引擎期望键在采集端**任何**成功路径下都不会被写出,则映射断裂(结构性),当日源端失败只是次级现象。反向 grep 取证: china_market_collector.py 全文件无 `balance` 键、无扁平 `pe` 键(grep 零命中),000001.SH 仅出现于 A_SHARE_INDICES(L42-49)与 fetch_turnover(L367),不在 VALUATION_INDICES(L88-92)。

**C(从未采集)**: 判据 = registry 有条目但全部通道文件+代码侧均无该指标痕迹。本轮实测 **0 项**。

**U(离线不可定夺)**: 仅 MAPPING_UNRESOLVED 与需外部源文档/生产侧信息才能定的项。本轮 **0 项**。

### 2.3 逐来源映射规则(含出处,全部为引擎读侧实读)

- **global_market_collector(32)** → `global_YYYYMMDD.json` 的 `data[资产键].close`。资产键 = 注册表 ID,除恒等外 7 个别名取 `fact_engine.py` L244-245 `_GLOBAL_ID_MAP` 之逆(GOLD_F→GOLD, SILVER_F→SILVER, WTI_F→WTI, BRENT_F→BRENT, USDJPY→JPY=X, USDCNY→CNY=X, GBPUSD→GBPUSD=X)。
- **macro_collector(28)** → `macro_YYYYMMDD.json` 的 `data[数据键].value`。数据键 = ID,除 WTI_SPOT_M→WTI(L281 `_MACRO_ALIAS` 之逆)。观测日取系列内最新非 null 日期(`observation_date`)。
- **rate_expectations(4)** → `rate_economy_YYYYMMDD.json`: US_2Y/US_10Y 走 `current_rates` 行匹配(L417-427);ZQ_F1_PRICE/ZQ_NEXT_MEETING 走 `fed_funds_futures` 中 `ZQ=F` 行(L448-458)。
- **china_market_collector(12)** → `china_YYYYMMDD.json` 路径表 = `fact_engine.py` L322-391 `normalize_china` 之逆(SHCOMP→a_share_indices.000001.SH.close 等;MARGIN_BAL→margin.balance L364-366;SH_PE→valuation.pe L367-369;SB_FLOW 按采集端实写面取 southbound.south_money L357-363;CN_TOTAL_TURNOVER 主路径 sh+sz 双依赖(L381-385)+akshare 降级备路径 total_amount_billion(L386-391))。工具同时用 MARGIN_COLLECTOR_KEYS(rzye/rqye/rzye_billion,L314-319)与 VALUATION_PROBE(嵌套 pe_ttm/pb,L344-351)做采集端对照探针,产出 B 层证据。
- **fact_engine(derived)(4)+ macro_collector(derived)(1)** → 依赖表 = `fact_engine.py` L462-500 `compute_derived` 实读: REAL_10Y←(UST_10Y,BEI_10Y)、REAL_5Y←(UST_5Y,BEI_5Y)、HY_IG_DIFF←(HY_OAS,IG_OAS)、ZQ_IMPLIED_AVG←ZQ_F1_PRICE、NFP_MOM_K←NFP(需序列 derived.m1,L490-499)。REAL_SHORT(deprecated)按 macro 顶层 `derived` 字典探针(macro_collector.py L257-275)。

**偏离登记(W2-AC-01)**: 主状态与机械状态的偏离恰 2 处(MARGIN_BAL: PATH_NULL→B;SH_PE: KEY_ABSENT→B),均依 B-over-S 规则以代码侧行级证据判出,已在 REPORT §三行内+§末登记;其余 79 行零偏离。

---

## 三、CI 机制结论(承接 R005/W1 情形(a))

新套件 `tests/test_metric_coverage_audit.py` 匹配 `.github/workflows/offline-tests.yml` 的 glob 发现,**无需改 workflow 即被纳入**:

- L38: `for t in tests/test_*.py; do`
- L40-42: `if [ "$name" = "test_glm_live" ]; then ... echo "== $name: SKIPPED(真实GLM付费调用,不进CI) exit=skipped"; continue`
- L45: `if python3 "$t" > "/tmp/suite-logs/$name.log" 2>&1; then`(逐套件独立运行、独立退出码)

依赖面: 套件只 import 标准库(unittest/tempfile/subprocess/json/importlib),workflow L33 安装清单已足够;本地全套件双环境(3.9.6)等价实跑记录见证据包 `local_ci_equivalent_run.txt`。CI dispatch 属操作者动作,本轮**不触发**。

---

## 四、债务清单导读与数据线路线图承接

- 债务清单(REPORT §四)= 覆盖表全部非 N 指标,恰 10 项: B×2(MARGIN_BAL 键口径断裂、SH_PE 扁平口径+上证身份断裂)与 S×8(china 通道大面积源端失败: SHCOMP/SZCI/CHINEXT/SB_FLOW/SH_AMOUNT/SZ_COMPONENT_AMOUNT/CN_TOTAL_TURNOVER + FED_FUNDS 单日键缺席)。
- **范围边界: 修复面待 R007 后"数据线第2包"另立合同**——本轮只登记不修。B×2 直接承接 R008/W1 的双层/三层断点诊断;S×7(china 通道)是本轮全量审计的**新发现**(R008 只看 margin/valuation 两断点,未扫 12 指标全量),建议第2包先排查通道层公共原因(token/积分/网络),再谈逐指标;FED_FUNDS 列观察项(月频单日缺席≠缺期,macro_20261101 在场 3.75@2025-09-01,若连续多日缺席才升级)。
- 快照侧连带事实(登记不修): snapshot_builder L249-261 按文件粒度回退、无按键回退——FED_FUNDS 这类"最新档键缺席"会直接缺事实。

---

## 五、如实声明

1. **只读**: `data/daily/` baseline(2026-11-02T03:14Z)与 closing 逐字节一致(12 文件);LIVE 生产目录零写入(三项只读取证: LIVE real_data_acceptance.py sha256 与 DEV 不一致且 DEV 侧未动 / LIVE 目录标记 grep 零命中 / LaunchAgents 无 DEV 引用),见证据包 `live_isolation_checks.txt`。
2. **零修复**: 未改任何 collector/registry/fact_engine/snapshot_builder/freshness_policy/既有测试/既有文档;`git diff --name-status 7cbef4c9..<尖端>` 恰 4 行 A(白名单)。
3. **U 清单 = 空(0 项)**: 81 项全部离线可定夺;REPORT §五为正式登记。
4. **判定可重演**: 工具+registry+data/daily 三元组任何人可复跑;2 处 B 偏离附行级代码证据供审计独立复核。
5. 网络零调用、CI 不 dispatch(操作者动作)、不碰其他分支。

---

## 六、证据包(/tmp/data-w2-evidence → IA-DATA-W2-EVIDENCE.zip)

baseline/closing 清单与比对、工具实跑 JSON+人类摘要、覆盖表行生成器及产物(内部一致性保障: 表行由工具输出机器生成)、workflow 原文摘录、本地全套件等价实跑记录、LIVE 隔离三查、U=0 声明、尖端 SHA、SHA256SUMS(不含 zip 自身)。逐项清单见 zip 内 SHA256SUMS。
