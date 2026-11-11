# CURRENT_STATE — 最新研发状态

> 研发面恢复入口(新会话先读这里,再读 `RESUME.md`)。
> 引擎运转面(LIVE/轮次/合同)不在本档——见 `~/agent-loop/STATE.md` 顶部速览。
> 更新纪律: 每完成一个重要研发阶段必须更新本档(进度/测试与审计结果/分支与 Commit/下一步)。

## 快照: 2026-11-11 (HKT)

- **基线**: main = `cdffebe`(v0.9.0-alpha,Charter 9「全球宏观研究闭环与一键研究」当日闭合);
  Release 441388150 上线,CI 42983226791 绿 = main 基线 126 槽。
- **LIVE(阿里云)**: 仍跑 v0.7.1 面;升级新面 = 用户保留卡点③,待批。
- **引擎**: 停于唯一日历门——F 补证轮观察钟 2026-12-05 满自动触发,此前无排程任务。
- **长期研发章程**: 2026-11-11 用户启动《自主研发、独立审计与持续迭代总指令》,本目录建立。
  总指令原文待用户消息落位 `PRODUCT_GOAL.md`(落位前,本目录其余文件按现行事实登记)。
- **章程初始化分支**: `dev/autonomous-rd-charter`(CLAUDE.md + autonomous-rd 七文件;
  未合并 main、未推送)。

## 里程碑脉络(详录 = `ITERATION_LOG.md`)

38/38 工作包全收口(11-08 四层封版)→ MW-V1 章程校准 → OSS 产品化 v0.1 → Skill 化 v0.2 →
v1.1 整改 v0.3 → Model-Agnostic v2.0(v0.4)→ v2.1 整改+glm 清零(v0.5)→ Charter 6 十年深度(v0.6)→
Charter 7 能力建设(v0.7/v0.7.1)→ Charter 8 机构观点交叉验证(v0.8)→ Charter 9 研究闭环+一键研究(v0.9)。

## 当前差距要点(详表 = `CAPABILITY_MATRIX.md`)

- 机构观点库六标签全库 INSUFFICIENT(库龄函数,首验窗 2026-12)。
- LIVE 面落后 dev 面(v0.7.1 vs v0.9.0)。
- 数据缺口台账 18 项(`../P2_DATA_GAP_LEDGER.md`);HY_OAS 族 = 源端 3 年授权窗如实注记。
- 历史遗留(`../REMAINING_ISSUES.md`,2026-10-17 版): P0 空,余 P1 观察项。

## 用户保留卡点(未经用户亲自批准不得动)

① 封版合并 main(含本章程初始化分支) ② 新数据源凭证/付费 ③ LIVE 部署。
