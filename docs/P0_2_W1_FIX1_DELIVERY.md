# P0-2 W1-FIX1 交付报告（阻断性缺陷整改）

- 契约：IA-P0-2-W1-FIX1-AC-v1.0（本轮）/ IA-P0-2-W1-AC-v1.0 / IA-P0-2-AC-v1.0；P0-1 全部冻结契约不变
- 角色：开发自检；独立验收由 Agent 4 执行。日期：2026-10-29；分支：`dev/p0-2-w1`（无 force push、未推 main、未 merge）

## 1. 开发前失败验收 SHA

`704cd5903349989fa4e3cca86a51c7b4ca78554d`（本轮增量基线；开发前已核实 DEV HEAD=该 SHA=origin/dev/p0-2-w1，工作树干净）。

## 2. 本轮实现 SHA

`4a09599`（10 文件，+790/−49；显式暂存清单见 git show --stat）。

## 3. 最终交付 SHA

本提交（docs/P0_2_W1_FIX1_DELIVERY.md，docs-only）；CI 以最终分支尖端运行为准（§16）。

## 4. IA-P02-W1-DEF-001 修复（CORE_PCE 指数基期）

- 缺陷：注册表 `CORE_PCE.unit=index_point_2012`、采集器标签"指数点(2012=100)"，与 FRED PCEPILFE 官方单位 **Index 2017=100** 矛盾；W1 首轮审计还将其误标 VERIFIED（审计结论错误一并修正，见 §11）。
- 修复：注册表 unit → `index_point_2017`（仅 1 行 diff）；`macro_collector.SERIES_UNITS` 标签 → "指数点(2017=100)"（仅 1 行）。**语义标注修复，非数值重新定基**：采集器直读 FRED 原始值，无任何换算系数；metric_id/source/source_symbol/frequency/calendar/criticality/status/validation.range/数值/历史序列/freshness（45 天，W2 范围未动）逐字节未动。
- 影响面核查：`index_point_2017` 已在 `fe.PRICE_LIKE_UNITS` 与 `rsem.KNOWN_UNITS`（既有单位体系，未新增设计）；`make_fact`/`normalize_macro` 按注册表透传 unit，真实路径验证输出 `index_point_2017` 且数值 118.6/观测日 2026-09-30 原样；数据包/锚点单位随注册表自动一致；全部既有 fixture 无 2012 硬编码（grep 全仓仅注册表 1 处），32 套回归零 fixture 修改。

## 5. IA-P02-W1-DEF-002 修复（关键字段非法类型静默放行）

- 缺陷：`if isinstance(status, str) and status not in ...` 守卫使 `status=123`/`criticality=123` 等非字符串值绕过枚举判断。
- 修复（registry_semantics.py）：status/criticality/frequency 建立三段拦截——缺失/None/非字符串/空串 → `R-STATUS-TYPE`/`R-CRITICALITY-TYPE`/`R-FREQUENCY-TYPE` error（消息含实际值 repr+类型名+允许枚举）；合法字符串但枚举外 → `R-*-ENUM` error；value_type 在场而非非空字符串 → `R-VALUETYPE-TYPE` error，合法字符串未确认词汇维持 review 不擅自升 error。**value_type 允许缺失的历史兼容保留**，依据=fact_engine.py:210 `m.get('value_type','level')` 缺省 level（"可选"≠"允许显式非法类型"）。
- 类型检查先于语义使用：非法类型无法进入注册表缓存（`load_registry` 仅在断言全过后写缓存）、无法把 active core 指标静默逐出 Gate A、不再依赖下游 AttributeError 兜底。

## 6. CORE_PCE 官方元数据证据（独立权威映射）

`registry_semantics.OFFICIAL_FRED_INDEX_UNITS`/`OFFICIAL_METRIC_SERIES`——期望值**独立于被验证注册表**（绝不由当前配置生成，防注册表与校验共同携带同一错误）。证据（FRED 官方序列页，核验 2026-10-29，存于审计 JSON `official_units_evidence`）：

| FRED 系列 | 官方单位 | 频率/季调 | 数据来源 | 绑定指标 |
|---|---|---|---|---|
| PCEPILFE | Index 2017=100, SA | Monthly/SA | U.S. Bureau of Economic Analysis | CORE_PCE |
| CPIAUCSL | Index 1982-1984=100, SA | Monthly/SA | U.S. Bureau of Labor Statistics | CPI |
| CPILFESL | Index 1982-1984=100 | Monthly/SA | U.S. Bureau of Labor Statistics | CORE_CPI |
| INDPRO | Index 2017=100, SA | Monthly/SA | Federal Reserve Board (G.17) | INDPRO |
| UMCSENT | Index 1966:Q1=100, NSA | Monthly/NSA | University of Michigan | UMCSENT |

规则范围（有限、可审查，未启动 81 项外部研究）：`R-OFFICIAL-SERIES`（指标身份绑定序列，如 CORE_PCE 换成 CPIAUCSL/INDPRO → error，新序列自身合法不构成授权）、`R-OFFICIAL-UNIT`（source_symbol 命中官方映射而 unit 不符 → error，消息含期望值与实际值）、`collector_official_unit_problems`（注册表 unit ↔ 采集器标签同步，纯函数、采集器表由参数传入、零网络零运行时 FRED 查询）。

## 7. 注册表/采集器/事实引擎单位一致性

机器校验三处同步：注册表 `CORE_PCE.unit` = `rsem.OFFICIAL_FRED_INDEX_UNITS['PCEPILFE']`；采集器 `SERIES_UNITS['CORE_PCE']` 标签含"2017=100"（同步函数零问题）；`make_fact`/`normalize_macro` 真实路径输出 unit=`index_point_2017` 且数值/观测日不变（test_p02_w1_fix1 A6/A7）。负向：标签改回 2012 → `R-OFFICIAL-UNIT-SYNC` 点名失败（A5）。

## 8. 关键字段非法类型注入

test_p02_w1_fix1 B 节：4 字段 × {123, None, [], {}, True} = **20 项注入全部 R-*-TYPE 点名识别**（消息含实际值 repr）；另覆盖三必填字段缺失（键不存在）、枚举外合法字符串（分层 ENUM 非 TYPE）、value_type 缺失=合法兼容对照。

## 9. 真实 load_registry 拦截

C 节经**真实** `fact_engine.load_registry(path, force=True)` 加载 6 份临时非法注册表（CORE_PCE 回退 2012 / 换序列 / SPX 四字段=123）：全部抛受控 `RegistrySemanticsError`，消息点名 metric_id+规则号+期望/实际；无一静默加载；逐项拒绝后默认注册表缓存完好（C7）。

## 10. Gate A 核心集合回归

D 节：对照组合法注册表 81/80/32、SPX∈core 正常加载；`SPX.criticality=123` 的注册表**整表拒绝**（不产生"core 静默缩为 31"的合格假象）；拒绝后 `rp.core_metric_ids()` 仍 32 含 SPX。**未修改 research_provenance.py 的 Gate A 机制**（本轮该文件零改动），拦截全部来自注册表加载层。

## 11. 81 项审计报告修订

- CORE_PCE：VERIFIED_CONSISTENT → **FIXED**，完整保留原错误（首轮"2012=100链式指数"结论被权威来源证伪，注明审计方法缺陷=未核官方基期）+ 官方证据（来源页/单位/频率/季调/数据源/核验日期）+ 实际影响（标注级；存量历史快照旧标签未回写——历史产物保护）+ 未证明范围。
- 分类总数由**程序按 81 项逐条记录重算**（生成器 counts 由 items 推导，test E3 锁定 totals==重算、E4 锁定 76/4/1/0）。
- WATCHLIST 计数 38 → **32**（与 global_market_collector.py 逐键复核；首轮文档计数错误，纯文档缺陷）；首轮交付报告同处已带更正标注。修订历史（首轮误判→FIX1 改判）写入 JSON `revision_history` 与 MD §8。
- DXY 维持有界 REVIEW（未获确定性反例）；S1 freshness 矛盾继续移交 W2，本轮未动。

## 12. 原 W1 正向能力继承

test_p02_w1.py 46/0（仅 A5b 期望值随审计修订同步，属追踪修订后事实而非弱化——总数↔逐项重算一致性另由 fix1 套件 E3/E4 锁定）；NVDA/AAPL/MSFT 身份保持（F1）；合法注册表 0 error 加载（F2/F3）；无效来源 fail-closed（F4）；单位/日历/来源三镜像集合锁不漂移（F5）；81 项审计清单完整性（E1）。

## 13. DEV/LIVE 只读隔离证据

`docs/P0_2_W1_DEV_LIVE_ISOLATION.{md,json}`：物理隔离（DEV inode 60895116 vs LIVE 22199716，realpath/commonpath 双向无祖先关系、无符号链接交指、DEV 树内零链接）；LIVE 六核心生产文件（run_daily.sh/run_weekly.py/fact_engine.py/report_generator.py/research_provenance.py/metric_registry.json）SHA-256 与 P0-1 封版 50b5d13 **逐字节一致**（W1/FIX1 修改不在 LIVE）；launchd 两 plist 全部路径型参数只指向 LIVE；origin/main=50b5d13 未动。证据能力限制如实声明（核验时刻状态一致≠历史绝对零改写证明；独立方可按 JSON `rerun_commands` 只读复跑）。

## 14. 全量适用离线测试（本机 Python 3.9.6 + macOS，2026-10-29）

**32 套执行 / 0 失败 / 全部 exit 0**（test_glm_live 按契约跳过）：datafix_20261017(13)、e2e_four_weeks(59)、e2e_frozen14(33)、e2e_orig14(41)、fact_engine(60)、gate_chain_p01(86)、p01_fix1(82)/fix2(109)/fix3(45)/fix4(49)/fix5(62)/fix6(86)/fix7(41)/fix8(52)/fix9(42)/fix10(29)/fix11(17)、p02_w1(46，A5b 随审计修订)、**p02_w1_fix1(41，新增，三遍幂等)**、p0(22)/p1(36)/p2(82)/p4(43)/p7(30)、phase3(47)、phase4(20)、round3_adversarial(24)、round3_p0(91)、round4(94)、round5(64)、round6(51)、snapshot(46)。Gate A PASS/DEGRADED/FAIL、来源绑定、快照身份、已发布报告保护、预测幂等全部经既有套件重跑通过；**历史 fixture 零修改**（无任何 fixture 含 2012 基期假设，grep 全仓核实）；未重写任何历史快照/报告/状态文件。

## 15. 原始 14 项 E2E

test_e2e_orig14(41/0) + test_e2e_frozen14(33/0) + test_e2e_four_weeks(59/0) 全绿——E2E-01~14 业务语义未动，质量门禁语义未放松。

## 16. GitHub Actions 新 Run

本轮真实运行（非沿用历史 run 40805443416）：workflow_dispatch `--ref dev/p0-2-w1`，head_sha=最终交付 Commit，test_p02_w1 与 **test_p02_w1_fix1 均实际执行**，全部套件 exit=0，test_glm_live 显式 SKIPPED，Job success。运行链接/Job ID/head_sha 于推送后在最终开发回复给出。

## 17. 生产影响边界

**本轮没有实施生产部署**（LIVE 仍为 P0-1 形态，六文件哈希一致证明）；**没有修改 GitHub main**（origin/main=50b5d13）；**没有重新开放 P0-1**（冻结契约零改动，P0-1 侧文件零触碰）；**没有开始 W2~W5**（S1 freshness 矛盾等仅登记移交）。registry/采集器改动将在未来部署时随分支合入，届时 LIVE 的 CORE_PCE 标签随之更正（数值序列不变）。

## 18. 未验证事项（如实声明）

- 真实金融数值准确性仍非认证对象（含 PCEPILFE 数值本身；本轮认证的是"单位标注与官方口径一致"）。
- LIVE 部署形态下新规则的实际运行（本轮仅离线+CI 验证；LIVE 上线时序由后续指令决定）。
- 其余 76 项 VERIFIED 中非 5 项官方保护序列的单位标签仍属首轮人工核验层面，未逐一外部核验。
- CI 环境与生产 macOS 环境（Python 3.11 vs 3.9）差异以双环境全绿缓解，但不等于生产运行时验证。
- 开发者自检不构成 Agent 4 独立结论；W1 最终裁决权在独立验收。
