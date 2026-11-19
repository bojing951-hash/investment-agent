# Audit-R20(R64) — 全球宏观经济变化地图: 正式使用验收(四地补齐/发布可见性/读者正文/一问验收/反例拦截)

- 基线: abba4d1(R19 CI 回填后,PR #1 分支 dev/audit-fix-r1)
- 修复提交: **d123f24**
- 分支: dev/audit-fix-r1(PR #1);合并与上线由用户裁定,本波不并 main 不部署
- 状态: 停等外部审计

## 〇、指令与五任务

用户指令(节选): 在 PR #1、分支 dev/audit-fix-r1 完成「全球宏观经济变化地图」的正式使用验收;
以 abba4d1 和 docs/autonomous-rd/r19-evidence/ 复现问题;直接修改现有采集、研究、渲染和归档
流程,修完自行重跑;合并由用户决定。

1. 补齐四地地图(US/CN/EA/JP × 增长/通胀/政策 × 12个月前/3个月前/最新一期=12组36时点格,
   每格数值/单位/观察期/实际发布日期/来源;政策目标、贷款报价、隔夜市场均值分开标明)
2. 修复历史可见性(vintage/as-published per cutoff;2025-11-18 美国只见 Q2 GDP+八月失业率 4.3;
   政策决定日/生效日/统计窗口结束日分列;历史类比分相似点/他经济体同步/事后3-6-12月;仅最新
   修订值时标事后回顾)
3. 修复读者正文(同一组可复算事实生成首页/表格/传导图/历史回报;CN PMI 五月=50.0、九月=50.1;
   共同交易日美债分解;因果链逐环事实/假设+区分指标;两情景触发与失效方向;历史类比0-3段零段
   写明检索范围;真实 VIX 工单回归月涨 38.07% 及计算窗口)
4. 真正的一问验收(隔离目录零同题归档零预填判断,全新会话只输入 run.question 原文一次,现有入口
   完成研究/判断/独立复核/必要修订/归档;新 MAP_REPORT 逐项检查)
5. 验证修复能拦错(正例跑通;反例 −6.27%→+99.00%、正文月份错误、提前引用未发布、核心维度缺失
   均无法新增正式归档;修复 pytest 对 R19 套件的入口识别保留原断言)

## 一、基线复现(r19-evidence 实测)

1. **四地缺格**: 归档判定显示 CN 通胀/政策两维「CN_CPI_YOY/CN_PPI_YOY/CN_OMO_7D/CN_LPR_1Y
   历史序列均不可得」,EA「注册表无欧元区增长指标+EA_HICP_YOY 不可得,仅政策一格可判」,
   JP「增长/通胀不可判,央行目标利率不在注册表」——12组36格基线只有美国全维+CN仅PMI+EA/JP仅政策。
2. **发布可见性失真**: 锚值按推定滞后规则取数,无经证实发布日历——2025-11-18 截止面会把
   2025-11-19 才首发的停摆积压数据(9-10月 BLS/BEA 系列、Q3 GDP)当作已发布引用。
3. **读者正文四缺口**: 归档 research_plan 无 asset_moves 面(VIX 月涨 38.07% 一类数字后台可算
   但读者面无窗无表);利率分解三序列各取各自最新观测日(分量和≠名义变化,残差不披露);
   正文月份可写错而契约不拦;零段历史类比检索范围不落正文。
4. **反例不拦**: 编造回报(+99.00%)、月份错误、提前引用未发布、核心维度缺失在基线契约下均可
   新增正式归档(无对应 CONTRADICTED/阻断器)。
5. **pytest 入口**: R19 套件尾部缺模块级 `sys.exit(` 标记,conftest SuiteFile 静态查判
   「套件不自执行」强制红(入口识别缺陷,非断言缺陷)。

## 二、修复(12 文件改+3 新增,+1724/−148)

| # | 修复 | 落点 |
|---|---|---|
| F1 | 四地采集补齐: CN CPI/PPI/OMO_7D/LPR_1Y+六指数四级fallback梯(tushare→东财直连→系统代理→腾讯ifzq→akshare);EA_HICP_YOY/EA_REAL_GDP_YOY/ECB_MRO/ECB_DFR;JP_CPI_YOY/JP_REAL_GDP_YOY/JP_POLICY_RATE(1985起);DFEDTARU/DFEDTARL 目标区间;注册表补维+政策目标/贷款报价/隔夜市场均值分列+stat_window_end | china/ea/jp_market_collector/japan_rate_collector/macro_collector/metric_registry |
| F2 | 发布可见性: release_calendar.py+config/release_calendar.json 经证实条目(2025停摆: Q3 GDP与9-10月BLS/BEA系列首发2025-11-19)优先于RELEASE_RULES推定;_visible_publish 全链贯通快照/锚;锚循环跳过被日历阻断观测;no_published格带停摆延误+首发日+依据 | release_calendar*/snapshot_builder/research_orchestrator |
| F3 | 读者正文面: asset_moves面入research_plan(截止日显式传参=契约同参复算;窗=≤截止最新观测vs最近于截止−N月观测,两端实测日随行);三利率共同交易日复算+12个月窗双口径(恒等残差逐位披露);policy_dates(决定/生效/统计窗口);render新增资产表/双窗分解/停摆披露/政策三日期 | research_map_planner/research_orchestrator |
| F4 | 契约三回贴+组级阻断: anchor_echo(逐地数值5e-3)/rates_decomposition(窗口+三分量逐位)/asset_returns_echo(回报chg+窗口exact);map_core_dimension_missing组级阻断挂归档带 | research_contract/judgment_contract.py/ia_cli/agent_judgment |
| F5 | 门与入口: 新增 tests/test_audit_r20_gate.py(30查);R19 套件尾部补 `sys.exit(0)` 入口标记原断言零改动;§B 期望值按经证实日历更新(2025-11-18锚: 失业率=8月4.3,9月值首发11-19被排除)在档注记 | tests/test_audit_r20_gate.py/tests/test_audit_r19_gate.py |

## 三、门测试

- **tests/test_audit_r20_gate.py 30/30 全绿**: §A 注册表/日历/_visible_publish;§B 回归锚(2025-11-18
  美国只见 Q2 GDP+八月失业率 4.3)+12组×36格五要素+政策三日期+vintage+CN PMI;§B2 三利率恒等+VIX
  复算;§C 三回贴反例(CONTRADICTED: 编造回报99.00/月份错误/提前引用未发布);§D 渲染六查
  (含停摆延误披露);§E 正例归档+稀疏根核心维度缺失零归档。
- **tests/test_audit_r19_gate.py 35/35 全绿**(入口识别修复后直跑+pytest 双口径)。

## 四、真实面冒烟(引擎树 /tmp/r20_real,截止 2026-11-18,7/7)

快照 series_store 携带全部新指标(EA_HICP_YOY 358obs/EA_REAL_GDP_YOY 123季/JP_CPI_YOY 69obs/
JP_REAL_GDP_YOY 127季/JP_POLICY_RATE 496obs 自1985/CN_CPI_YOY/CN_OMO_7D/DFEDTARU 3652obs…);
回归锚① 12个月前 GDP=2025Q2(obs 2025-04-01,Q3 首发 11-19 被日历排除);回归锚② 12个月前失业率
=2025-08 4.3(9月停摆被排除);12组×3锚全 ok;CN PMI 2026-05=50.0/2026-09=50.1;三利率共同交易日
月窗 Δ+1bp=+15−14 残差0.0;VIX 月窗带计算窗口;DFEDTARU 决议日=生效日=观测日。
(r20_smoke.py+r20_smoke_output.txt 见 r20-evidence/)

## 五、真实 VIX 工单回归(R17 工单原面复算,4/4)

工单「近一个月VIX飙升而高收益债OAS利差几乎未动…」原运行面=LIVE data/daily *_20261118.json
只读副本(含原 research_snapshot_20261118.json,未重建——即工单当日真实 series_store)。修复后
同一面: **VIX 月涨 +38.07%(窗口 2026-10-19→2026-11-17,18.44→25.46)**,读者表行
`| VIX | 2026-10-19..2026-11-17 | 18.440001→25.459999 | +38.07%(+7.02) |`;
契约层同窗复算逐位一致(echo 可通过);同行 SPX −4.55% 与 R17 归档逐字吻合。
窗口规则=「≤截止最新观测 vs 最近于截止−N月观测(界日无观测取最近邻)」——R17 基线取界日后
首个交易日(10-19),旧 R20 草案取界日前最后交易日(10-16,33天窗),现统一为最近邻(30天整月)
且两端实测日随行披露,读者可自核。

## 六、共同交易日美债分解(月窗+12个月窗双口径)

指令核验数「+100＝+107−7bp」为 R19 基线的各序列各自最新观测日口径(名义/实分量差 3bp 不齐)。
严格共同交易日复算(真面 2026-11-19): 12 个月窗 **2025-11-17→2026-11-17: 名义 Δ+97bp =
实际 Δ+104bp + 盈亏平衡 Δ−7bp,恒等残差 0.0**;月窗 2026-10-16→2026-11-17: +1=+15−14 残差 0.0。
两窗均入读者渲染(us_rates_trio_20261119.json 见 r20-evidence/)。

## 七、全新会话一问验收

**运行编号 20261119T060058Z,最终裁决 UPHELD(裁决链 2 档),已正式归档。**
隔离目录 /tmp/r20_accept(修复后代码+最小数据面,零同题归档零预填判断)内,全新操作者会话
只输入 run.question 原文一次,现有入口 `research-one --stage auto/--stage archive` 走完全链:
plan → AGENT_SEAT_ENVELOPE → judgment(attach 契约 VERIFIED,50 锚回贴+三利率分解+8 资产回报
全过)→ 独立语义审查席首裁 **REVISE 四必修**(①INDPRO 低点月错 ②CN PMI 荣枯线表征不实
③BEI 日期-数值错置 ④共同交易日计数)→ 修订正文四处+契约重挂 VERIFIED → 复裁 **UPHELD**
(rev=2,回归抽查零漂移)→ 归档(九件套,content_sha256=5b1d1fdd… 与裁决锚三处核对一致)。
新 MAP_REPORT 五项逐检通过: 首页总判断/四地对照表(12组+诚实缺格+Δ事后回顾)/五环文字传导图
(逐环事实+假设+竞争解释+区分指标)/三个转折(按日期+谁先变+跟进背离,修订后低点分层正确)/
历史事后表现(3 段×随后3-6-12月)。证据= docs/autonomous-rd/r20-evidence/acceptance/
(README+run_question_verbatim+归档九件套+裁决链双档)。诚实披露: 隔离面未携 rate_economy
通道→Gate A core_missing 6 项披露放行,judgment/正文未引用该族;入口路径实测补修一处
(数据树无快照时截止日回退 `20261119T0[:10]` 崩 int('T0'),改真 ISO 日期——research_orchestrator
~L1892)。

## 八、反例拦截实测(门内+真面)

- 标普三个月回报 −6.27%→+99.00%: attach 阶 CONTRADICTED(asset_returns_echo 同窗复算
  SPX 真值不符),不交付零归档。
- 正文月份错误: anchor_echo observation_month 不符 CONTRADICTED。
- 提前引用未发布数据: 发布日>锚日观测被 _visible_publish 排除,格内无该值;强写则锚回贴
  nonexistent-cell CONTRADICTED。
- 核心维度缺失: EA/JP 组剥格 → map_core_dimension_missing 阻断 report deliverable+
  ia_cli 归档带 missing_groups 拒绝,零新增归档目录。

## 九、电池与 CI

- **本地电池 `python3 -m pytest -q`: 191 passed / 1 failed(=tests/test_arch_reform_phase6 D3 干净树
  检查——R20 未提交工作面自身触发,与 R28 同型预期红;提交后转绿)**。基线 abba4d1 对照:
  基线 21 红全部复现为 R20 超越(注册表 v2.8.5→2.8.6 +3 指标 110→113/108→111、采集通道接线、
  复杂度基线 93f/57909L/1591函数),经 /tmp/r20_baseline worktree 抽验 7 件基线全绿定性。
- **冻结期望更新纪律**: 16 个测试文件+README.md+复杂度基线档,scripts/config 生产面零触碰;
  断言结构/原意不变,逐处 `# R20:` 超越注记;test_p02_w5_datasrc_b 数值期望零改动——根因=
  R20 四路阶梯把 akshare 注入口降到末路+前三路真出网(测试纪律破损),修法=空注入直连/腾讯两路
  使被测面确定性落末路,81.82/999.0 原值通过。
- **门复核**: R20 gate 30/30、R19 gate 35/35(入口识别修复)、R18 gate 40/40 一次全跑绿;
  邻接面(e2e_orig14/p01_fix4/fix5/fact_engine)回归绿。
- CI: 提交后 GitHub Actions 三 job 绿(run 见下)。
- **登记候选(未改生产码,下轮裁定)**: ① research_provenance.gate_reason_desc 对 noncore_missing
  截断窗 [:16] 而合法名单已 19 项——UMCSENT/WALCL 落出周报降级披露点名(E2E-02d3 已按在场断言
  据实锁定,可见性由 02d/02d2 承载;建议改全量+溢出计数);② 真实面 registry JP_CPI_TOKYO_YOY
  source_key='JP_CPI_TOKYO' vs jp 采集器写档键 'STATGO_CPI_TOKYO'——R11 子源分类将落「不可区分」
  兜底话术,仅影响披露精度不影响裁决;③ vintage_additions 实算=32(29+3),相关断言按实算落锁。

## 十、证据包与留档

- docs/autonomous-rd/r20-evidence/: r20_smoke.py+output(真面冒烟 7/7)、r20_vix_regression.py+
  output(VIX 工单回归 4/4)、us_rates_trio_20261119.json(双窗分解面)、acceptance/(一问验收
  全件套)。
- 状态: ITERATION_LOG/CURRENT_STATE/RESUME 经 rd_checkpoint --finalize 收口。
