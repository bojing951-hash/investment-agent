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

## 工件

入库(本目录): FULL_REPORT.md / report.md / judgment_mvp.json /
AGENT_SEAT_ENVELOPE.json / BIGFILES.sha256
大件(运行目录 /tmp/phase4_C/20261116T053259Z_*,sha256 在档):
report.json / views_digest.json / evidence_index.json / agent_judgment.json
