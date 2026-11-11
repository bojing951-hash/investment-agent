# C9 修复轮独立复验报告 (C席)

- 对象: `dev/charter9-closeloop-v1` @ 7dcbf8e (六笔: dddaea P0-4口径 / 8e73f83 P0-3来源验证 / 4bdcf6e P0-1三型verifier / a6b1114 P0-2 VP sidecar / 803b2a1 P3页2页4 / 7dcbf8e P4 research-map+编排层+Web入口)
- 环境: 真git clone `/tmp/c9fix` (含 .git/HEAD, 满足5个audit_commit类测试) + dev库data/全量拷贝; 对照基线 `/tmp/c9v` @ 06bb65d
- 纪律: 只读不改代码; 独立期望值全部重算; 合成件沙箱 `/tmp/c9fix_sbx/`
- 结论: **10面全 PASS**; D席 126/126 + CI模拟声明独立确认; 无阻塞性新问题, 4项非阻塞观察见文末

---

## 面1 采集档降级近似 (裁定⑦重点) — PASS

| 检查 | 独立证据 | 判定 |
|---|---|---|
| vintage锚定跨日判据 | `rp.vintage_dates(data/daily)`=['20261108','20261110']; publish≥2026-11-08 走 vintage, 否则回退 | ✓ |
| 回退标注如实 | 合成 VIEW-20260915-001 与真实 VIEW-20261110-002 (publish 10-28) 均输出 `{anchor:'approx_filtered', cutoff:'2026-10-28', degraded:true}` + 裁定⑦原文注记"当时信息集近似,DEGRADED" | ✓ |
| 裁定① ≤含 (facts) | view_verifier.py L411-412 `observation_date ≤ pymd` 含等号; vintage快照20261108 facts 观测日含恰好 2026-11-08 当日 | ✓ |
| 裁定① ≤含 (series截断) | L415-416 `dates ≤ pymd` 含等号; D席测试 L247 锁定"陈旧观测在场,晚于publish的事实被滤" | ✓ |
| cutoff披露 | 两条路径 vintage_note.cutoff 均在场 (vintage=cutoff日, 回退=publish_date) | ✓ |
| 真实走回退路径的观点档 | 真实17份中16份 publish<2026-11-08 全走回退; 量化: publish 09-15→n_evidence 0/16, publish 10-28→10/26行, publish 11-09(vintage)→52/60行 | ✓ |
| vintage锚真实件 | VIEW-20261111-004 (publish 11-09): anchor=vintage_snapshot, cutoff=20261108, degraded=false; UST_10Y obs 2026-11-05≤cutoff | ✓ |

## 面2 三型区分度 — PASS

- **mode A/B relation压None+护栏**: `relation=None` + "成熟度护栏: 期限NOT_YET_TESTABLE→不判supports/against" ✓
- **mode B since_publish**: basis 2026-09-14 4.97 → end 2026-11-05 4.84 = **−0.13pp**, 与 interval_change"严格早于start最后观测"基准语义独立复算一致 ✓
- **mode C 未到期**: NOT_YET_TESTABLE + "到期 2027-09-15 > 验证日 20261110(未到期不判)" ✓; "12个月"→上界 2027-09-15 正确
- **mode C 已到期** (合成件 publish 2026-05-15 + horizon"2026-10"): horizon_end=2026-10-31; 我手算 publish→10-31 UST_10Y **+0.47pp** (basis 05-14→end 10-30) =up, hint=上行 ⇒ **supports** = 引擎值 ✓; 反向件(下行)→**against** ✓; 点位件("4.5%附近")→**LEVEL_TARGET**+actual_observation 2026-10-30 4.94 ✓
- **legacy缺省行为不变**: 06bb65d 与 7dcbf8e 同参数(无directions)均 `relation=None`("未传directions→不做方向判断"), 数值零漂移 (1m −0.4 / 3m +0.19 / 1y +0.73pp); legacy+directions 仍判 supports; 新增 maturity/revision_anchors 纯披露字段
- **P0-1原缺陷(三份输出逐字节相同)已修**: publish 09-15 vs 01-01 两件 maturity horizon_end (2027-09-15 vs 2027-01-01) 与 since_publish (−0.13 vs +0.66pp) 均可辨, 输出不再相同

## 面3 期限解析器 — PASS

- 真实库普查 (17份): view级 **16/17 可解析** (1份 horizon="other"→UNPARSEABLE 如实), forecast级 39/70 parsed / 31 UNPARSEABLE (战术配置/当前/中期/会议间期间/持续/已实现数据/未指明 等如实拒绝) — 与D席声明一致
- 26形态独立抽验全对, 关键: **裁定② '2026-2027'→2027-12-31 (区间取上界)**; CY2026→2026-12-31; '12个月'→publish+12m; **'6-12个月'→上界12m**; '2026-12'→月末2026-12-31; '已实现数据(2026-09-30)'→ISO提取; UNPARSEABLE词表9形态全拒+原因
- 禁猜: 未映射/非期限→UNPARSEABLE, 无一瞎猜

## 面4 VP rollup优先级表 (裁定④) — PASS

- rollup_view_label 独立用例 **8/8**, 含顺序陷阱: [NOT_YET, CONTRADICTED]→**MIXED** (任CONTRA先于全NOT_YET) ✓, 空→INSUFFICIENT ✓
- verdict_to_label: supports→SUPPORTED / against→CONTRADICTED / NOT_YET→NOT_YET / 四类不可判+neutral→INSUFFICIENT / **未知verdict→INSUFFICIENT不猜** ✓
- validate_vp 拒绝面 9类全中: view_label≠聚合、label越六标签、ref.index越界、digest与被引陈述不符、hypotheses空、schema≠1.0、metric_refs空、kind错位digest; 正常件装载OK
- 编排层写/引擎校验分离成立 (view_label必须==rollup重算否则拒绝)

## 面5 P0-4原判项复跑 — PASS

- **slice_series_window 日历截取**: SPX_CAPE'1年'=**13 obs** (2025-10-01→2026-10-01, 旧缺陷显21年); UST_10Y日频'1年'=251 obs; '全部'=1750; note带"日期截取非定点数"
- **caption族感知**: rate→pp("−0.13pp,利率口径"), price→pct(+10.00%), **负基数→'基准值为负,价格类百分比变化语义不可用'**, 零基数→'百分比变化不可定义', count→绝对差
- **interval_change负基数护**: index −5→−4 → `available=False`+"基准值为负(−5.0)…" 如实拒算
- **多窗口表含利率族**: 65行含 UST_10Y(3m +0.19pp/1y +0.73pp)/FED_FUNDS/CURVE_2S10S/BUND/JGB/SOFR; `include_rates=False` 回退46行旧口径

## 面6 P0-3原反例复跑 — PASS

- **伪号硬闸**: 边档注入 QB-20990101-999 → **ValueError"禁伪号入页"** (06bb65d时零拦截); 缺qb_source边→ValueError; mechanism_findings伪号同样受闸; SYNTH:前缀跳过+detail披露不入checked_refs
- **干净clone降级**: 归档目录缺席→`archive_check.performed=False` 如实注记; 伪号+归档缺席→放行但披露performed=False (设计: 禁CI崩溃, 全量核验在source_verifier)
- **source_verifier --edges**: 33条全 VERIFIED (25边+7机制+1结构性), rc=0
- **--recompute 复算对账**: compare真被调用, 全部 r✓n✓ 零CONFLICTED, lag边双向试算 ({1:0.1322, −1:0.0444})
- **containment_check直测**: r/n命中、全角负号−归一、精度变体、未命中→CONFLICTED分支
- **裁定③ lint默认离线**: 默认lint **0.07s** 零网络; `--verify-urls` action='store_true' 缺省False, 全库唯一调用点在门控内; 不可达→"只披露不隔离"

## 面7 research-map如实面 — PASS

- 十问扇出: 10问×(章程§五原文/数据面/命令), RQ3(AI推断)→agent_judgment面"引擎不产出"
- **conflicts=[] 是如实非掩盖**: 我独立重算全部17份forecasts→direction: 仅 UBS FED_FUNDS=up, 无任何同指标多空双方; **UBS两条加息forecast同向, 确不算对撞** — 引擎空数组与独立复算一致
- **pseudo_consensus=[] 同样一致**: 11主题全部≥2机构 (fx=2家最小; HK_macro=0=缺席非单源)
- ART-M/ART-FALS/观察钟: data/research/ 确无对应文件 (真缺席), 输出 present:false+"缺席(终报告内嵌可接受)"/"引擎只透传,绝不代触发"

## 面8 页面渲染面 — PASS (代码面+纯函数直测)

- app.py: L89-102 页1刷新按钮(st.button门控subprocess+超时护); L222 页2边徽标; L300 页3 VP徽章表; **L319-330 mechanism_steps/evidence_cited渲染 (P0-2原缺陷已修)**; L361 页4十问
- research_questions: 恰10问/RQ1-10连续/五层(客观事实/机构观点/AI推断/历史统计/条件情景)各覆盖; 4类破损注入全FAIL-LOUD (9问/层越枚举/id断裂/五层覆盖缺)
- edge badge四态: VERIFIED✅(在册+sidecar回读9443字符) / MISSING❌(悬空) / PARTIAL⚠️(归档缺席performed=False) / SYNTH披露"生产边档禁用"

## 面9 CI模拟复跑 — PASS (独立确认126/126)

- 真 git clone + `TZ=UTC` + CI同款逐文件循环 (`python3 tests/test_*.py`, 排除test_model_live): **125套件 exit=0 + 1 skipped, ci_fail=0**
- D席"必须真clone不能用git archive"方法注记成立: audit_commit类测试读真 .git/HEAD, 本轮全程真clone

## 面10 120基线零弱化 — PASS (一处已披露的放宽, 判适配)

- test_charter8_view_verifier.py: '7m'由非法变合法=P0-3窗口语法通用化(Nm/Ny任意正整数)的**必要适配**; fail-loud断言保留(改用'bogus'触发)且**新增**正向断言 7m→2026-04-10 (2026-11-10−7月, 我独立复算正确) — 净增强
- test_charter8_workbench.py hunk1: "正文在场"扫描窗 top-10→top-50, 带注记 (并行工单追加QB-20261111-*无sidecar致固定10行窗漂移); 四要素/最新在前/≤81断言不动 — **判: 边界性放宽但有披露有理由, 意图保留**, 非删断言
- hunk2: '十个能力速查'→'十一个能力速查' (research-map入册) — 纯适配等强度

---

## 非阻塞观察 (新发现, 均不构成FAIL)

1. **mode A回退的evidence表随publish年龄变薄**: 当前快照facts均为近期观测, 回退过滤后 publish 09-15→0/16行, 10-28→10/26行 (series截断仍有数据但evidence行按fact判定)。属D席测试锁定的设计意图(保守如实"发布时点无该fact"), 但mode A对旧观点的可用性主要落在序列层——建议编排层知情使用。
2. **forecast_target_map覆盖面小**: 17份观点的机构target文本仅2条映射到方向可判指标 (UBS 联邦基金利率/标普500), 其余大量 NOT_MACHINE_VERIFIABLE (禁猜, 扩充归Agent层) — 如实但意味着 mode C 近期可机械判定面很窄。
3. **pytest无法收集本测试套件**: test_afin_acceptance.py 模块级 sys.exit(0) 致 pytest INTERNALERROR。CI契约(逐文件python3)不受影响, 但直接跑pytest者会误判——可考虑文件名或守卫惯例注记。
4. **'2027年起年度步伐'→2027-12-31**: 裸年子串规则的确定性命中, basis披露"绝对时点", 但语义上是节奏表述非时点预测——非缺陷, 语义边界备忘。

## 复验方法可重放要点

- 隔离: `git clone --no-hardlinks ~/investment-agent-dev /tmp/c9fix && cd /tmp/c9fix && git checkout dev/charter9-closeloop-v1 && cp -R ~/investment-agent-dev/data /tmp/c9fix/`
- 合成件: /tmp/c9fix_sbx/views/ 五件 (枚举合规view_horizon); VP沙箱 validate_vp 直调
- 手算锚点: UST_10Y publish 2026-05-15→2026-10-31 = +0.47pp (basis 05-14→end 10-30); UST_10Y 1m/3m/1y = −0.4/+0.19/+0.73pp (双代码库双跑一致)
