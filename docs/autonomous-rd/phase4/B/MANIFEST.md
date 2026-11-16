# Phase 4 Task B — 中国宏观信用与制造业景气(CN_NEW_LOANS/CN_PMI_MFG→CHINEXT/FXI)

- 执行: 2026-11-16,操作者席+独立 Agent 研究席(subagent,79 工具调用)
- 入口: `ia_cli.py research-one` 三段式;数据根=引擎树注入
- 问题: 中国宏观信用与制造业景气: CN_NEW_LOANS 新增贷款与 CN_PMI_MFG
  制造业PMI 对 CHINEXT 创业板指与 FXI 中国大盘股的影响

## 链结果(含诚实边界)

| 段 | 结果 |
|---|---|
| plan | **run_ok=False=诚实数据边界**(S4 对 CN_NEW_LOANS/CN_PMI_MFG no_series: 中国宏观序列无登记接入点;CHINEXT/FXI 序列在场),L1=4,evidence=65 |
| Agent 席 | validate passed=True 零违规;verify_judgment **VERIFIED**(12 项数字核对: 11 VERIFIED+1 STALE[观测龄旗标,9 月观测 vs as-of 11-16,档内自披露];18 项六查全 VERIFIED) |
| attach | attached=True,violations=[],**--allow-failed-run 显式越过 MINOR-4**(诚实拒答类失败+证据面可用,门槛显式=可审计) |
| report | **ok=True,L3∧L4 produced=True** |

## 判断面概要

- L3 矛盾 3(各 3 竞争解释): 信用扩张叙事(PBOC 适度宽松+1 万亿民企再贷款,
  institution_stated)vs 景气收缩事实(PMI 49.3 荣枯线下/新增贷款 12734 亿
  单点)/同周双资产反向定价(创业板周 +4.3337% vs FXI 同周下跌)/量价挤压
  (PPI 5.0% vs CPI 0.9% 剪刀差+PMI 收缩)vs 政策对冲
- 机制链 3(E1/E2/E3): 信用脉冲→景气→在岸成长/在岸离岸同周背离数字面
  (全窗 pearson 0.3621)/剪刀差→利润率→成长盈利
- L4 情景 3(基准+双反例,**confidence_tier 全取最低档「纯逻辑推理」并说明
  理由=驱动指标无历史序列无条件相似渠道**): 证伪阈值全部取 S4 序列钉死
  口径可观测值(创业板 2391.6518 年内低点@2026-11-03/高点 3043.3346@
  2026-10-09;FXI 31.59@2026-06-26),时限 2027-03-31/2027-06-30

## CN 无序列边界披露方式(全档)

agent_declaration 首条披露 run_ok=False 构成;CN_PMI_MFG/CN_NEW_LOANS/
PPI/CPI **零年内百分位/区间类表述**;序列类表述只落 CHINEXT/FXI;FXI=美股
上市美元计价 ETF 代理(offshore_proxy)如实标注;观察日不同步(信贷 9 月/
PMI 10 月/资产 11-11)标注"非同窗对比";S6 类比不含中国宏观序列故不引用。

## 引擎观察项(移交引擎席,R46 候选)

- S4 no_series 未标 honest_refusal 标志(语义上属诚实拒答类,但总判按普通
  失败计 run_ok=False)——若补标,B 类任务可不走 --allow-failed-run 显式门

## 工件

入库(本目录): FULL_REPORT.md / report.md / judgment_mvp.json /
AGENT_SEAT_ENVELOPE.json / BIGFILES.sha256
大件(运行目录 /tmp/phase4_B/20261116T053224Z_*,sha256 在档):
report.json / views_digest.json / evidence_index.json / agent_judgment.json
