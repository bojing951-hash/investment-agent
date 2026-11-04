# P0-2 W2 交付报告（数据时效规则一致性）

- 契约：IA-P0-2-W2-AC-v1.0（本轮）/ IA-P0-2-W1-AC-v1.0 / W1-FIX1-AC / IA-P0-2-AC-v1.0；P0-1 全部冻结契约不变
- 角色：开发自检；独立验收由 Agent 4 执行。日期：2026-10-29；分支：`dev/p0-2-w2`（无 force push、未推 main、未 merge）
- 开发指令：IA-P0-2-W2-DEV-v1.0

## 1. 开发基线

`69d7fc71f4ac05d3e5323cb5e270585ec48d6f97`（W1 最终验收 Commit；开发前核实 DEV HEAD=该 SHA=origin/dev/p0-2-w1，工作树干净，自该 SHA 创建 `dev/p0-2-w2`，非 GitHub main——main 仍冻结于 P0-1 的 `50b5d13`）。

## 2. 本轮实现 SHA

`63bd7504eefaed7e80d5ab22024484ab64d2227d`（15 文件，+3616/−87；文件清单见 `git show --stat 63bd750`）；本报告为随后 docs-only 提交。

## 3. 最终交付 SHA

分支尖端 docs-only 提交（本文件）；CI（§16）head_sha 须等于该提交——若 head_sha 非 docs 提交则非本轮交付形态。

## 4. W2-01：81 项规则审计与政策矩阵（先行产出）

`docs/P0_2_W2_FRESHNESS.{json,md}`：81 项逐条（metric_id/来源/频率/日历/观测日语义/release_date可得性/发布节奏证据/retrieved_at与as_of用法/改前三窗口对照[注册表·引擎·Gate B]/冲突描述/生效窗口/政策状态/审批依据/Gate A影响/Gate B影响/生产影响）。焦点 15 项含发布日历证据（BLS/BEA/EIA/Fed G.17/FOMC/密歇根）。**程序生成**（生成器 `/tmp/gen_w2_policy.py`，输出一致性由 test_p02_w2 A1-A7 锁定），改前三窗口以 `git show HEAD:config/metric_registry.json` 基线读取，非手填。

改前冲突全景：81 项中注册表≠引擎生效 61 项（月频 13 项 45vs92、行情日频 44 项 5vs7、BTC 2vs7、DFF/SH_PE 10vs7、DFEDTARU/L 45vs7）；Gate B 另有独立 prefix 规则（rate_economy 一律月度 45、macro 月度枚举表漏 5 项月频且 'WTI' 死键从未匹配、china 一律 7、未映射默认 14 信任）。

## 5. 政策审批（两轮，2026-10-29，用户批准）

实施关口（§5.4）先输出政策矩阵与待批决策后实施。**第一轮**：月频 45 / 行情日频 5 / 特殊日频 BTC2·DFF10·SH_PE10 / 政策区间 45 获批。实施前复核发布日历算术发现两处第一轮推荐依据错误，**第二轮修正获批**：月频 45→**60**（BEA/EIA/G.17 系正常发布滞后可达 ~60 天，45 会把按时发布的 CORE_PCE/WTI_SPOT_M 在每月下旬误判过期）；中国大陆日频 8 项 5→**10**（春节/国庆休市 8~9 天，节后首日必误报；HK 无此量级维持 5）；MARGIN_BAL 7→**10**（同一休市日历一致化）。无冲突 52 项维持（利率族 7、ICSA 16 等）。审批全记录冻结于 `freshness_policy.POLICY_APPROVAL` 与政策矩阵 `approval` 段。**未选择"最容易让测试通过"的窗口**：92（旧值，测试改动最小）被否决，因与"缺口必须披露"目标偏离最大。

## 6. W2-02：统一原语 scripts/freshness_policy.py（新增，纯函数）

- `build_policy(registry)`：注册表窗口→逐指标生效策略；缺失/非正整数/bool/float/字符串/非法频率 → `FreshnessPolicyError` fail-loud（**不得静默回退 7/16/92**）。
- `set_policy/policy_for`：fe.load_registry 注入共享缓存；未被注入时惰性自载默认注册表（与 fe 同一文件）——Gate B 侧独立进程/导入序（报告校验、观察器、配置引擎）不依赖 fe 先行加载。
- `canonical_anchor_metric/verify_anchor_identity`：锚点键→注册表指标 canonical 映射，**镜像 snapshot_builder 构造规则**（三张映射表 lazy 引用 sb 单一来源不复制；china 特殊键镜像并经真实 build_anchors 全键回环锁定）；仅逐段精确语法匹配，**无子串授权**；`info.metric_id` 仅交叉核验，冲突以 canonical 为准并披露。
- `assess`：三问分离——A 已观测（完整 ISO 真实日期且≤as_of）/ B 点时已发布（**仅当真实 release_date 在场才作答**：>as_of=NOT_AVAILABLE_AT_AS_OF；缺失=RELEASE_UNKNOWN 如实标注，**绝不伪造**；早于观测=INVALID_RELEASE）/ C 新鲜（lag≤已批准窗口）。未知指标/未知策略/非法输入一律不得转为有效。
- 零网络、零新依赖、模块级不 import fe/da/sb（无环）。

## 7. W2-03：fact_engine.validate_fact 接入（DEF-001 修复）

死变量 `fr` 与硬编码 `eff_window=7/16/92` 删除；窗口=`fp.policy_for(mid)`（注册表已批准策略）。滞后超窗→既有 DEGRADED 分级与消息格式（仅窗值来源变化）；月频 release-limit WARN（当月观测未过半）原样保留；无窗口指标→新增 `freshness_policy` 类 DEGRADED（不得默认按任意窗口视为新鲜）。`load_registry` 在 rsem 断言后构建并注入统一策略（非法→fail-loud）。BTC 按批准 2 天窗（lag3 即披露，非旧 7 天）；月频 60（lag61 起披露，旧 92）。

## 8. W2-04：Gate B 统一（DEF-002/003 修复）

`metric_frequency/freshness_rule_for/metric_registry_info/is_fresh_anchor/stale_anchor_warning` 重写为消费 fp 同一策略；旧 MACRO_MONTHLY_SERIES 枚举表、rate_economy 一律月度 45、china 一律 7、`.close` 正则启发全部废除。修复的确定性错误：rate_economy.current_rates.DFF/DFEDTARU/DFEDTARL 恢复日频（10/45/45）；INDPRO/JTSJOL/RSAFS/UMCSENT/NFP_MOM_K/WTI_SPOT_M 六项月频不再误按日频 7；macro.derived.*（REAL_10Y 等）从 unknown/14 恢复注册表身份 7。**未映射锚点 fail-closed**：`is_fresh_anchor`→False + "无法认证时效(UNMAPPED)"警告（旧默认 14 天信任废除；14 仅作为 `freshness_rule_for` 遗留诊断兼容值保留，注明非认证）；scorecard.*（报告内部推导，非注册表）维持遗留周度 10 并显式标注。`metric_registry_info` 返回真实 metric_id + identity_status/conflict 披露，release_date 仍如实 None（不伪造）。签名兼容：daily_prediction_observer:111/allocation_engine:409 两处调用零改动；`_obs_staleness_warning`（报告时点提示）与 Gate B 数值校验/prev/锚点版本机制未动。锚点信息信任边界：调用方 info.metric_id 不作授权（伪装实测按 canonical 判窗，test_p02_w2 E1-E5）。

## 9. W2-05：三路一致性（实证）

test_p02_w2 D 节：10 项强制指标（BTC/SPX/CPI/CORE_PCE/ICSA/DFF/DFEDTARU/DFEDTARL/SH_PE/UST_10Y）× 正常+过期，`fp.assess` ↔ 真实 `validate_fact`（frequency 类 issue 在否）↔ `is_fresh_anchor` **三路逐点一致**（20 组无失配）；rate_economy.current_rates.DFF.value 判日频 10（不再自动月度）。A9 锚点族回环：真实 `sb.build_anchors` 产出的**每一个**锚点键 canonical 映射=锚点自带 metric_id（sb↔fp 镜像锁定，防映射漂移）。

## 10. W2-06：专项测试 test_p02_w2.py（43 检查，A~H，三遍幂等中的两遍+全量各一次）

A 81 项矩阵完整性（覆盖=注册表、生效值逐项=注册表现值、总数由 items 重算、对照字段如实、审批两轮在场、焦点 15 项、锚点族回环）；B 注册表改窗经真实 validate_fact 生效（SPX 5→2 后 lag3 披露/lag2 边界内/恢复后往返）；C 月频六场景（未发布 WARN+RELEASE_UNKNOWN/上一期新鲜/长期未更新 DEGRADED/连缺多期/已知发布晚于 as_of 拒绝/发布未知不伪造）；D 三路一致；E 身份伪装（窄窗冒宽窗按窄判/未映射带 metric_id 仍拒/子串不授权/宽窗如实保留）；F 非法输入（缺观测/非法日期/未来/未注册/非法 release/六类坏窗口 fail-loud/生产加载路径）；G 正式研究链（正常 PASS+批次核验过/合法 DEGRADED 披露不阻断/SPX 'N/A'→FAIL 传导/Gate B 新鲜不重开 Gate A FAIL/过期证据不进观察）；H 敏感性（收窄与放宽双向检出/篡改锚点数值+身份→权威重建核验拒绝/恢复后重过）。

## 11. 既有测试调整（逐项合法性）

| 文件:位置 | 原钉住 | 调整 | 合法性 |
|---|---|---|---|
| test_fact_engine.py:53 | CPI 注册表窗==45 | ==60 | 追踪批准后注册表事实；窗口边界行为另由 test_p02_w2 B/H 锁定（非弱化） |
| test_round3_p0.py A3 | UNRATE Gate B==45 | ==60 | 旧 45 为 Gate B 分叉值；统一后=注册表月频 60（审批记录） |
| test_round3_p0.py A4 | china prefix 7/5 + 虚构 label 键 | 真实键 10/5/南向 10 + 虚构键 UNMAPPED 14 | '南向资金净流入'/'上证' 从未被 sb 发出（真实键=china.southbound.net_buy/'上证指数'）；prefix 启发正是 W2-DEF-002；虚构键 fail-closed 为正确语义 |
| test_round3_p0.py A7 注释 | ≤45 | ≤60 | 注释随批准值更新，断言（lag38 新鲜）不变且仍通过 |
| test_round4.py:283 注释 | 月频45天内 | 60天内 | 注释更新；CPI lag27 断言不变 |
| test_e2e_frozen14.py / test_e2e_orig14.py chain_build | sb CLI 子进程用真实墙钟 | 注入 `--as-of`=场景日 08:00 | **时间炸弹修复**：场景日本义即"以该日为研究截止"；旧实现随运行日期漂移（旧 7 天窗下场景日+8 天起同样会爆，W2 收紧至 5 提前暴露）。期望语义不变，未放松任何门禁 |

未删除任何测试；未修改 P0-1 冻结验收语义；test_glm_live 未动。

## 12. 注册表 22 项窗口修改（均为已批准值）

月频 13 项 45→60（CPI/CORE_CPI/CORE_PCE/UNEMPLOYMENT/NFP/NFP_MOM_K/AHE/FED_FUNDS/INDPRO/JTSJOL/RSAFS/UMCSENT/WTI_SPOT_M）；中国大陆日频 8 项 5→10（SHCOMP/SZCI/CHINEXT/HSAHP/SB_FLOW/SH_AMOUNT/SZ_COMPONENT_AMOUNT/CN_TOTAL_TURNOVER）；MARGIN_BAL 7→10。HK（HSI/HSCEI=5）、BTC=2、DFF/SH_PE=10、DFEDTARU/L=45、利率族 7、ICSA 16 原值未动（前四者为第一轮已批注册表原值直接生效）。外科手术式文本替换（仅 freshness.max_calendar_lag_days 22 处，其余逐字节未动）；W1 审计 JSON 为 W1 时点历史记录不回写（其中"freshness 45 天，W2 范围未动"表述以本报告为准更新）。

## 13. P0-1 冻结契约继承（§十一红线）

未修改任何 LIVE 历史快照/报告/采集文件；未回填 release_date；未批量重算旧周报；未自动改变旧报告状态；未重置 thesis/allocation_views；未放宽来源 SHA-256 与 EXACT/FALLBACK 5/7/5/7 窗口（resolve_inputs 未动）；旧报告只读。历史 fixture 零修改（本轮全部测试数据为合成/临时目录）；`--as-of` 仅测试注入，生产 run_daily 不传、默认行为零变化。

## 14. DEV/LIVE 只读隔离证据

`docs/P0_2_W2_DEV_LIVE_ISOLATION.{md,json}`：物理隔离（inode 60895116 vs 22199716，互非祖先）；LIVE 8 个核心生产文件（含 data_validator/snapshot_builder）SHA-256 与 P0-1 封版逐字节一致；`scripts/freshness_policy.py` 不存在于 LIVE（未部署）；launchd 两 plist 只指向 LIVE；origin/main=50b5d13 未动。初版核验脚本 strip() 截断换行导致假性不一致，已用 git cat-file 原始字节修正复跑（结论全部一致）。证据能力限制如实声明于文件内。

## 15. 全量适用离线测试（本机 Python 3.9.6 + macOS，2026-10-29）

**33 套执行 / 0 失败 / 全部 exit 0**（test_glm_live 按契约跳过）：datafix_20261017(13)、e2e_four_weeks(59)、e2e_frozen14(33)、e2e_orig14(41)、fact_engine(60)、gate_chain_p01(86)、p01_fix1(82)/fix2(109)/fix3(45)/fix4(49)/fix5(62)/fix6(86)/fix7(41)/fix8(52)/fix9(42)/fix10(29)/fix11(17)、p02_w1(46)/p02_w1_fix1(41)、**p02_w2(43，新增，两遍幂等)**、p0(22)/p1(36)/p2(82)/p4(43)/p7(30)、phase3(47)、phase4(20)、round3_adversarial(24)、round3_p0(91)、round4(94)、round5(64)、round6(51)、snapshot(46)。Gate A PASS/DEGRADED/FAIL 分级、来源绑定、快照身份、批次核验、已发布报告保护、预测幂等、原始 14 项 E2E 全部经既有套件重跑通过。

## 16. GitHub Actions

按指令以 workflow_dispatch 对 `dev/p0-2-w2` 发起真实运行（不推 main、不以历史 run 代替）：运行链接、head_sha（须=最终交付 Commit）与 test_p02_w2 实际执行证据在**推送后的最终开发回复**给出。

## 17. 生产影响边界

**本轮没有实施生产部署**（LIVE 仍为 P0-1 形态，8 文件哈希一致证明；统一窗口/新模块尚未进入生产运行——上线后首个生产快照起，Gate A 按批准窗口计算：日频行情 6-7 天滞后、月频 61-92 天滞后、BTC 3 天起转为 DEGRADED 披露；DFEDTARU/L 8-45 天恢复有效）；**没有修改 GitHub main**；**没有开始 W3~W5 或 P0-3**；上线时序由后续指令决定。

## 18. 未验证事项（如实声明）

- 窗口的金融正确性=按公开发布日历推理+用户两轮批准，未逐系列调用官方 API 复核每个发布日（发布节奏证据为文档级）。
- 真实数值准确性仍非认证对象；本轮认证的是"时效规则一致性"。
- 期货曲线点锚点（rate_economy.fed_funds_futures.<i>.*）无 obs_date 的判龄缺口保持如实警告（补时间元数据未列入本轮范围，已在政策矩阵 known_limitations 登记）。
- LIVE 部署形态下的实际运行（本轮仅离线+CI）；CI（Linux/Python 3.11）与本机（macOS/3.9.6）双环境全绿缓解但不等于生产运行时验证。
- 开发者自检不构成 Agent 4 独立结论；W2 最终裁决权在独立验收。
