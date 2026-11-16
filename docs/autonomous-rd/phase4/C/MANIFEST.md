# Phase 4 Task C — 美日政策利率分化(DFF/JP_POLICY_RATE→USDJPY/GOLD_F)

- 执行: 2026-11-16,操作者席+独立 Agent 研究席(subagent,45 工具调用)
- 入口: `ia_cli.py research-one` 三段式;数据根=引擎树注入(快照 20261112_v2)
- 问题: 美日政策利率分化: DFF 与 JP_POLICY_RATE 之差 对 USDJPY 日元汇率与
  GOLD_F 黄金的影响
- 同族先档: 20261113T005117Z(R24 线)——本席三处分歧已显式声明并以本次
  证据面为准(近零渠道表述/机构方向证据缺席/无决策口径矛盾)

## 链结果

| 段 | 结果 |
|---|---|
| plan | run_ok=True 零失败步,L1=4(DXY 不在题面;DFF/JP_POLICY_RATE/USDJPY/GOLD_F),evidence=65 |
| Agent 席 | validate passed=True 零违规;verify_judgment **VERIFIED**(18/18 六查+3 数值裁决亲算: 利差 +2.837pp=|3.88−1.043| 价差算术/目标区间 3.75-4.00% 快照裁决);迭代修 1 CONTRADICTED+1 unbound 后全绿 |
| attach | attached=True,violations=[] |
| report | **ok=True,L3∧L4 produced=True** |

## 判断面概要

- L3 矛盾 3: CON-1 利差收窄与日元走弱并存(全窗相关 +0.767 vs
  2024-09..2026-11 窗 −0.735 本席确定性复算,4 竞争解释)/CON-2 黄金对同
  利差变量分窗符号翻转(−0.850 vs +0.536,2026-01 冲顶 5318.4 后 −24.5%
  回撤)/CON-3 度量口径 +2.837pp vs 决策口径约 +2.6pp(FOMC 中值−BOJ,
  JP 月均滞后摊薄,L1 本标 DEGRADED)
- 机制链 3(E1→E2→E3): 利差→USDJPY(存量 carry+实际利率差)/央行决议
  事件→USDJPY 短窗(2026-07 BOJ 三日 −3.83% 事件级预演)/利差→GOLD_F
  (机会成本通道+S5 日度相关 −0.0496 渠道分离)
- L4 情景 3(基准+反例×2): SCN-A 证伪=2027-03-31 前 USDJPY 连续 20 日
  <150.0(基准 159.81@2026-11-11);SCN-B 证伪=BOJ 至 1.50% 后 20 日内
  USDJPY 升破 163.9;SCN-C 证伪=FOMC 再加息 ≥50bp 后 GOLD_F 仍 <4000.0
  (基准 4013.4@2026-11-11)
- 证据缺口(E2 假设): 无跨境资本流动/套息持仓序列/美日实际利率差在册
  序列/央行购金与投机持仓流量/决议日历事件控制/决策口径利率序列;
  gate_a=DEGRADED(10/10 信封步非 OK)已知悉入口径矛盾 CON-3

## Audit-R1 修订记录(2026-11-16,第一轮外部审计修复)

- **v3(终版 sha256 前 16 位 `82b26a72af0be0a0`,旧版 `ef15ad56429e9337`)**:
  依第一轮语义复审 5 发现+F01 证伪条款修复:
  - MECH-1 环4 证伪区重写[MAJOR]: 「利差仍处+1.0pp 上方而 USDJPY 急升向
    145 下方」方计证伪,与 CON-1 解释一确认区(利差近零⇒急升)构造性互斥、
    两区不可重叠计分;中间带(0,+1.0)双向不计分=保守留白;旧「+2.0pp下方」
    区作废(仅存作废引文内);
  - SCN-C 前提门重写[MAJOR]: 前提在场=trigger 已触发(BRENT_F 连续 10 日
    >110 或核心 CPI 连续两月高于共识)且利差自基准+2.837pp 升破+3.5pp
    (旧 3.3 门作废);FOMC 加息明示不构成前提;
  - SCN-A +0.536 引文作废→事件事实(Fed 2026-09 再加息后 GOLD_F 收于 1月
    峰值下方约 24.5%,附符号误读注记)[MINOR];措辞修正(任何方向变动含
    跌破 150.0)[NIT];4600 S4 口径注记(中位 4439/p75 约 4698)[NIT]。
  - 标记形制映射: 扫描字段内用无数字标记「复审」,未扫描字段保留
    Audit-R1 F0x。
- **修订闭环终审**: 独立席(bc-closure-seat)python3 只读复算 30+ 项断言
  (相关面全窗+分窗/GOLD 面/事件面/DFF 阶跃日亲验/锚点全中)——两 MAJOR
  证伪逻辑修复均正道落地且边界逻辑独立判过,全部数值逐位吻合,零新增
  缺陷。**裁定 VERIFIED**,裁决档
  `audit/semantic_review/20261116/VERDICT-20261116T053259Z-01.json`(fresh=True)。
  残留三项既有 NIT(约0.09/约5.1 叙事压缩、4600『其』绑定歧义)列出不阻断。
- **四态终态**: generated ✓ / machine_verified ✓ / review=VERIFIED(fresh) /
  **deliverable=True**;FULL_REPORT.md 已换 F09 完整装配版。

## 工件

入库(本目录): FULL_REPORT.md / report.md / judgment_mvp.json /
AGENT_SEAT_ENVELOPE.json / BIGFILES.sha256
大件(运行目录 /tmp/phase4_C/20261116T053259Z_*,sha256 在档):
report.json / views_digest.json / evidence_index.json / agent_judgment.json
