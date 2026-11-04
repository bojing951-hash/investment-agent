# P0-2 W2-FIX1 交付报告（独立验收阻断性缺陷整改）

- 契约：IA-P0-2-W2-FIX1-AC-v1.0（本轮）/ W2-AC / W1-FIX1-AC / W1-AC / IA-P0-2-AC-v1.0；P0-1 全部冻结契约不变
- 角色：开发自检；独立验收由 Agent 4 执行。日期：2026-10-29；分支：`dev/p0-2-w2`（无 force push、未推 main、未 merge）
- 开发指令：IA-P0-2-W2-FIX1-DEV-v1.0
- **本轮状态：READY FOR W2 INDEPENDENT ACCEPTANCE**（三项代码缺陷修复+两项政策证据齐备+DFEDTARU/L 已获第三轮批复；无待批准项残留）

## 1. 固定失败验收 Commit

`958b52e3906485b643cafb0f88e5bf727872fb68`（W2 第一轮交付 docs-only 提交，Agent 4 判 FAIL 的验收对象）。本轮自该 SHA 继续，**未重做 W2**（W2 原实现 `63bd750`、首轮 CI run 40848606583 不作数）。

## 2. 新实现 Commit

`ea9a88cd939bfb93f23b76efc5bf2bd95d24ecda`（18 文件，+1548/−204；含新增 4 文件：三份政策/证据文档 + tests/test_p02_w2_fix1.py）。

## 3. 最终交付 Commit

本文件所在 docs-only 提交（分支尖端）；**CI head_sha 必须等于该提交**——若 head_sha 非本提交则非本轮交付形态。

## 4. 增量 Diff（958b52e → ea9a88c）

`git diff --stat 958b52e ea9a88c`：18 文件 +1548/−204。脚本 7 个（freshness_policy 190 行、data_validator 168、fact_engine 100、allocation_engine 32、daily_prediction_observer 18、research_provenance 11、snapshot_builder 11——均在本轮授权文件清单内）；注册表仅 2 行数值变更（DFEDTARU/DFEDTARL `45→10`，用户第三轮批复后修改，保持原 indent=1 格式无重排）；FRESHNESS.{json,md} 政策矩阵同步；测试 5 处既有期望更新（§14 逐项理由）+ 新增 FIX1 套件。

## 5. W2 累积 Diff（W1 最终 69d7fc7 → 本轮尖端）

`git diff --stat 69d7fc7 <本交付提交>`：W2 原实现（freshness_policy.py 新建、注册表 22 项已批准窗口统一、fe/dv 消费、43→44 检查 W2 套件）+ 本 FIX1 增量。W1/W1-FIX1/P0-1 冻结契约零触碰（§14）。

## 6. FIX1-01：非法日期洗白修复（DEF-001）与强制反例

- **共享原语** `fp.parse_instant`：date/datetime 实例、完整 ISO 日期、完整 ISO 时间戳（`[T ]HH:MM:SS[.ffffff][Z|±HH:MM]`，时差须带冒号）整串接受；后缀垃圾/假日历（2026-02-30）/非法月/部分时间/前后缀空白/非字符串一律 None——**无任何 `[:10]` 截断**。观测日语义=纯日期（与 P0-1-FIX5 冻结原语 `fe.parse_iso_date` 同口径，带时间戳 obs 双原语同判非法，共享原语不分歧）；as_of/release_date 接受完整时间戳（真实锚点文件 as_of 即时间戳形态）。
- **消费面收敛**（正式认证链全链，非孤立副本）：`dv._norm_date/metric_registry_info/is_fresh_anchor/stale_anchor_warning`、`fe.validate_fact(as_of_date/release)`、`ae.verify_evidence_items`（rg:1008/ae:1100 证据门同路径）、`rp` 周报重算 cutoff、`dpo._metric_problem`（正式长期观察入口）。
- **§5.4 强制反例表**（BTC 2 日窗，as_of=2026-10-24，四入口逐行验证于 test_p02_w2_fix1 A2/A3）：`'2026-10-23'`→FRESH/True/证据过；`'2026-10-23INVALID'`/`'2026-10-23xxx'`/`'2026-02-30'`/`[]`→INVALID_DATE/False/证据拒(不可解析)+警示"无法判龄"；`None`→NOT_OBSERVED/拒(缺obs_date)；`'2026-10-25'`→FUTURE_DATE/拒(未来)；as_of=`'2026-10-24INVALID'`→assess INVALID_DATE+dv False+ae 拒(研究截止非法)+警示——**同一输入不得一方 INVALID_DATE 另一方 True**（A2 循环断言 assess↔dv↔ae 警示逐行一致）。时间戳+后缀垃圾 `…+08:00X` 同拒（时间戳接受≠放松整串验证）。

## 7. FIX1-02：未来发布日期实际传递链（DEF-002）

- **真实元数据路径**：release_date 仅来自采集记录（`normalize_global/normalize_macro/normalize_rate` 的 `item.get('release_date')`）→ `make_fact` 原样存键（缺失不写键=RELEASE_UNKNOWN，**绝不以 observation_date/retrieved_at/文件日期/快照日期伪造**；非法原样保留交 FAIL）→ `validate_fact` 经 `fp.assess` 点时判定 → `sb.emit` 锚点透传 → `dv.is_fresh_anchor`（Gate B）→ `ae.verify_evidence_items`（证据门）。
- **判定**：release>as_of→FAIL `NOT_AVAILABLE_AT_AS_OF`（核心→既有 Gate A 规则 FAIL）；release<obs→FAIL（发布先于观测）；release 非法→FAIL；缺失+月频→WARN RELEASE_UNKNOWN 披露（**有限新鲜度判断仍允许**——is_fresh 按窗照常，点时可得性如实标注未认证）；既有无 release 数据不整体 FAIL（默认链路 Gate A 照常 PASS，B10 实证）。
- **Agent 4 精确反例**（B7）：CPI obs=2026-09-01/as_of=2026-10-24/release=2026-10-28：`lag_days=53≤60` 窗内**但** NOT_AVAILABLE_AT_AS_OF、fresh=False、is_fresh=False、ae 证据拒——lag 提前计算保证早退时诊断完整（可追踪性）。§6.6 十场景全部落地（B1-B10，场景 8=真实 `normalize_macro` 入口、场景 9=真实 Gate B 链路含 sb 透传）。
- **Gate B 信任边界**（§6.5）：仅拒绝性消费——调用方自填**过去** release 不授予任何额外认证（fresh 结论与合法缺 release 一致，B9b），自填**未来** release 拒绝；`metric_registry_info.release_provenance` 标注 `anchor_metadata(未独立核验;仅拒绝性消费)`，不表述为已认证发布时间。

## 8. FIX1-03：锚点来源-身份约束（DEF-003）

- **家族↔权威来源绑定** `_FAMILY_SOURCES`（registry `source` 字段为权威）：global_market→global_market_collector；china_index/china_special→china_market_collector；macro→macro_collector（NFP_MOM_K 除外）；derived→fact_engine(derived)；rate_current→rate_expectations；rate_real_economy→macro_collector（经 `_RATE_OLD_NAME` 兼容映射 UNEMPLOYMENT→UNRATE）；futures_curve→{rate_expectations, fact_engine(derived)}。**注册表存在≠该通道可生成**。
- **冲突 fail-closed**（§7.4）：合法键+调用方 metric_id 冲突→`UNVERIFIED(identity_conflict)`→is_fresh=False——不再"记录冲突后以 canonical 继续授予 FRESH"（W2 E5 原断言该语义，已按§7.4 拆分 E5a 正向对照/E5b 冲突拒绝）。
- **八反例**（C1-C3 全拒 + D4 文件级）：`global_market.data.CPI.close`/`macro.data.BTC.value`/`macro.data.SPX.value`→SOURCE_MISMATCH→UNVERIFIED；合法 BTC 键+自称 CPI→identity_conflict；未注册/非规范键结构（`BTC.value`）→UNMAPPED；同名跨家族（`china.southbound.BTC.value`）→UNMAPPED；未认证自报 metric_id（未注册键自称 BTC / 跨通道键自洽自称）不授信。
- **正向兼容零回退**：真实 `sb.build_anchors` 128 键回环——0 UNVERIFIED、UNMAPPED 仅 `.week_chg` 诊断兄弟键；兼容键（china.southbound.net_buy/current_rates.DFF/macro.derived.REAL_10Y/real_economy.UNRATE(旧名 UNEMPLOYMENT)/macro.data.CPI/futures_curve.0.price/global_market.data.BTC.close）全部 MAPPED 且新鲜照常 True；scorecard 维持诊断专用 10 日窗。**P0-1 锚点权威重建不可绕过**（D4）：注入 spoof 键/篡改 metric_id/键改家族→`rp.verify_anchor_batch` 权威重建比对全拒，恢复后重过。

## 9. FIX1-04：DFEDTARU/L 政策复核（W2-POLICY-001）

专项评估文档 `docs/P0_2_W2_FIX1_POLICY_DFEDTARL.md`：FRED 官方证据（Frequency **"Daily, 7-Day"**；Notes："The data updated each day is the data effective as of that day"）→ 观测戳逐日推进，45 天窗唯一实际效果=掩盖 8~44 天采集中断；概念 A（政策状态有效性）由值本身承载、概念 B（观测新鲜度）才是窗口职责。方案 A（45→10 对齐同族 DFF）/方案 B（双轴建模）/维持 45 三方案对照（正常情形三案零差异、假日簇零误报、检测延迟 45/10/10、改动面 2 数值/新概念/0）。**未擅自改值**——2026-10-29 提交正式决策请求，用户批复**方案 A（45→10）**（批复原文逐字冻结于 APPROVAL_EVIDENCE §5）。执行：注册表 2 行、FRESHNESS.{json,md} 第三轮审批记录+APPROVED_FIX1_ROUND3+影响分析、受影响测试期望更新（§14）。

## 10. FIX1-05：HSAHP/SB_FLOW 日历专项（W2-EVIDENCE-001）

专项文档 `docs/P0_2_W2_FIX1_POLICY_HK_CALENDAR.md`：五概念区分表（大陆交易所日历/香港交易所日历/沪深港通交易日交集/实际观测日/业务理由）。核心不对称性：**HK 开市不保证两指标有观测，大陆开市（且 HK 同开）才保证**——SB_FLOW=南向净买入须两地同开+通道开放（大陆春节/国庆 8~9 天休市→南向停摆）；HSAHP=AH 溢价须 A/H 两腿同时有价（A 腿停市即停更）→ 观测缺口由大陆长假簇主导→10 天窗；HSI/HSCEI 无长假簇→5 天。`calendar='hk'` 字段语义=收益计算/序列日期推进日历，非时效窗口归属声明（两独立字段，无自相矛盾）；字段级显式化（observation_calendar）作为后续建议记录（§17.3）。**非按采集器自动归类**：round-2 批准选项原文逐字列明"SHCOMP/SZCI/CHINEXT/**HSAHP**/**SB_FLOW**/…共8项**含南向并集日历**…春节/国庆休市8~9天"——分组与业务理由均为批准材料的一部分。

## 11. 政策原始批准证据（W2-EVIDENCE-001 主项）

`docs/P0_2_W2_FIX1_APPROVAL_EVIDENCE.md`：**用户原始批准消息逐字回填**（非开发者转述）——Round-1（2026-10-29T07:57:50.613Z，4 题）与 Round-2（2026-10-29T08:37:35.660Z，3 题）tool_result 原文、提问时间戳、六要素表（条目/前值→现值/证据轮次）、可独立执行的 transcript 复核命令（路径+解析脚本逐字可粘贴）。DFEDTARU/L 例外诚实披露：round-1 批准时未见官方逐日发布语义，按§八重新提交决策并获第三轮批复（§5 补录区含批复原文）。**待批准清单：空**（无 AWAITING 项）。

## 12. 正式研究联合 E2E（§十，test_p02_w2_fix1 D 节）

- **10.1 正常对照**（D1）：真实 `build_full_day` Gate A=PASS+数据包+meta 绑定 snapshot；合法 DEGRADED（UMCSENT 真实降级）照常披露+产出；真实 `da.main` exit 0——整改不阻断合法正式链路。
- **10.2 未来发布 CPI 真实链路**（D2）：真实采集日携带 release=2026-10-28 → 事实规范化→时效质量验证（fact FAIL NOT_AVAILABLE_AT_AS_OF）→Gate A FAIL（CPI 核心）→数据装配拒（exit 2 无包）→周报预检拒（真实 `generate_weekly_report` exit 2+**GLM 零调用**+零 `apply_status_updates` 回写）→证据门拒（未来发布事实不得作当前证据）——质量门逐层拦截、下游不得覆盖、无非法正式产出。
- **10.3 已发布报告保护**（D3）：真实发布事务先建立合法历史报告（exit 0+GLM 恰 1 次+报告/状态落盘+formal_report_view 接受）→**危险操作前**记录四对象 SHA-256（报告/发布状态/thesis.json/allocation_views.json）→根内真实采集日携带未来发布 CPI（数据级攻击）→周报入口拒（exit 2+GLM 0）→执行后四对象摘要逐一不变+发布身份仍有效+无新 weekly_report_/report_status_ 文件+published=true 仅发布日+无长期状态回写+`scan_formal_weekly_reports` 不变；基线比较机制自检有效。
- **10.4 锚点 spoof**（D4，见§8）；**10.5 日期异常**（D5/A2）：真实 dv（is_fresh/warning/registry_info 如实 None+note 点名原始非法值）与真实 dpo 观察入口（obs 非法→不可解析不记录/未来→不记录/研究截止非法→不记录）。

## 13. 已有正式报告与长期状态保护

§12 D3 之外：P0-1 FIX9 既有的发布保护语义（formal_report_view/scan/apply_status_updates 隔离）本轮零改动全量回归通过（test_p01_fix9 42/0）；test_p02_w2_fix1 证明 FIX1 改动不引入绕过（批次核验 spoof 全拒、发布链 GLM 零调用路径不受日期/发布/身份新分支影响）。

## 14. W1/P0-1 继承回归 + 既有测试期望变更（逐项理由）

全量 35 套件（含 W2/W1/W1-FIX1/fix1~11/原始 14 项 E2E×3/GLM 跳过）全部 exit 0。变更 6 处，每处附理由注释于代码内：

| 位置 | 原预期 | 新预期 | 理由（原预期为何错误/新预期如何符合冻结契约/新反例保护） |
|---|---|---|---|
| test_p02_w2 E5 | 冲突 caller metric_id 下 is_fresh=True（canonical 继续授予） | 拆 E5a（无冲突 lag9→True 正向对照）/E5b（冲突→UNVERIFIED→False） | §7.4 明文禁止原语义（DEF-003 判定项）；非弱化——断言意图（合法路径不回退）由 E5a 保留，E5b 为新增反例保护 |
| test_p02_w2 A6a/A7/D-CASES/D3/E1 文案 | DFEDTARU/L=45（两轮审批） | =10（第三轮批复）；lag 正常/过期 44/47→9/12 | 用户 2026-10-29 第三轮批复方案 A（§9）；矩阵 A3"生效值=注册表现值"一致性锁定不放松，D3 同时断言 lag44 现为 False（收紧方向验证） |
| test_fact_engine「月频观测滞后不判错」 | 无 release 月频 quality=PASS | ∈{PASS,WARN} 且无 FAIL/DEGRADED 且 RELEASE_UNKNOWN WARN 在场 | §6.4"缺失→披露不伪造"：披露即 WARN 为新预期语义；断言意图（不误判过期）不变且新增披露验证（更强） |
| test_p01_fix1 UMCSENT 计数 | 硬编码 PASS−1 | 按事实实际 grade 动态推导（WARN→不计桶） | FIX1-02 使月频缺 release 进入 WARN（不计入 counts 桶）；"无 FAIL/DEGRADED"断言不变 |
| test_p01_fix5 A0/B4/B5/C10（4 处） | 硬编码 PASS 计数/月频=PASS | 动态推导实际 grade；C10 改为断言月频=WARN+RELEASE_UNKNOWN issue+周频 ICSA=PASS | 同上（月频 13 项 WARN 化的级联）；各处加§6.4 理由注释，"零 FAIL/DEGRADED"意图全部保留 |
| tests/fixt.py | — | 未改动 | 采集 fixture 不带 release_date（真实采集端形态），B10 锁定不伪造 |

原始 14 项 E2E（frozen14/orig14/four_weeks）语义零变更、零改动文件。

## 15. 全量回归与本机结果

2026-10-29，macOS/Python 3.9.6：**35 套件全部 exit 0**（`tests/test_*.py` 全量；含新增 test_p02_w2_fix1=53 检查；test_glm_live 显示"⏭️ 跳过(设置 RUN_GLM_LIVE=1…)"=GLM 未调用）。W2 套件 44 检查（含 FIX1 修订后 A6a/A7/D/E5）。

## 16. GitHub Actions（离线 CI）

workflow_dispatch 于 `dev/p0-2-w2` 触发 offline-tests.yml；**head_sha 必须等于§3 最终交付提交**（旧 run 40848606583/40867101337 分别对应整改前后中间形态，以本文件最终提交的 run 为准）；须执行 fix1+W2+W1+W1-FIX1+原始 14 项 E2E+P0-1 FIX1~11 全量、GLM skipped、任一失败即 job 失败。

**已核验 run 40867101337（head_sha=1dc8ac3，2026-10-29T11:39Z）**：conclusion=success；日志逐套件核验——34 套件全部 `exit=0`（含 test_p02_w2_fix1/test_p02_w2/test_p02_w1/test_p02_w1_fix1/test_e2e_frozen14/test_e2e_orig14/test_e2e_four_weeks/test_p01_fix1~11），`test_glm_live: SKIPPED(真实GLM付费调用,不进CI) exit=skipped`，无任何非零退出。本文件为随后 CI 结果补录提交（§3 最终交付提交即本提交，CI 以本提交 head_sha 复跑核验）。

## 17. DEV/LIVE 隔离证据 + 未解决事项与证据等级

**隔离**（2026-10-29 执行）：LIVE 8 文件（fact_engine/data_validator/snapshot_builder/research_provenance/allocation_engine/daily_prediction_observer/report_generator/metric_registry）`git hash-object` 逐一经 DEV 仓库 `git ls-tree 50b5d13` 比对——**全部一致**（LIVE 仍冻结于 P0-1 main `50b5d13`，freshness_policy.py 在 LIVE 不存在=未部署 W2 改动）；launchd/GitHub main/LIVE 生产配置与密钥/生产 thesis/views/采集数据/历史报告零读写；无真实 GLM、无真实金融 API 采集、无 W3~W5/P0-3 实施、无新数据库或模型、P0-1 门禁零降低。

**未解决事项与证据等级**：
1. DFEDTARU/L=10：**APPROVED**（第三轮批复原文，APPROVAL_EVIDENCE §5）。
2. HSAHP/SB_FLOW=10（HK 2 项=5、月频 60、大陆 10、MARGIN_BAL 10 等）：**APPROVED**（round-1/round-2 批复原文，APPROVAL_EVIDENCE §1/§2/§3）。
3. 观测日语义=纯日期（时间戳 obs 拒绝）：与 P0-1-FIX5 冻结原语一致的实现决定（交付文档§6 披露，非政策项）。
4. `calendar` 字段与时效窗口分属两语义：本轮澄清不改结构（§10）；若 Agent 4 要求字段级显式化（如 `observation_calendar`），建议列入后续工作包——**非本轮阻断项**。
5. `fe:227` derived as_of `[:10]` 保留未改：该处入参在 `validate_fact` 已按非法 as_of FAIL 拒绝（上游不可达非法值），改动属范围纪律外——如实披露。
6. GLM/CI：本机全量绿；CI 结果以 GitHub Actions run 为准（§16 补录）。
