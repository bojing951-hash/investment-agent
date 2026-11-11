# autonomous-rd — 长期研发章程与持久化研发记忆

> 建立: 2026-11-11,用户《自主研发、独立审计与持续迭代总指令》初始化。
> 本目录 = 研发面的唯一权威状态源;新会话仅凭本目录+CLAUDE.md 即可恢复工作。

## 文件职责

| 文件 | 职责 |
|---|---|
| `PRODUCT_GOAL.md` | 总指令原文,最高目标文件(未经用户授权不得修改/删减/降标) |
| `ACCEPTANCE_CRITERIA.md` | 最终验收标准(以总指令为准绳)+ 现行验收纪律 |
| `CAPABILITY_MATRIX.md` | 最终能力 × 当前差距 |
| `CURRENT_STATE.md` | 最新研发状态(研发恢复入口) |
| `ITERATION_LOG.md` | 每轮研发记录(只追加) |
| `OPEN_ISSUES.md` | 未解决问题与阻塞项(专项台账只挂指针) |
| `ACCEPTANCE_CRITERIA.md` | 验收标准(总指令 §八 AC1–AC10 + 现行纪律) |
| `FINAL_ACCEPTANCE.md` | 最终验收结果(独立审计复核后登记) |
| `RESUME.md` | 新会话恢复指令 |

## 与既有文档的关系(防双头维护,每主题唯一权威)

| 主题 | 唯一权威 | 说明 |
|---|---|---|
| 研发总纲/最终目标 | 本目录 `PRODUCT_GOAL.md` | 2026-11-11 起总指令为纲 |
| 产品能力目标 | 仓库根 `PRODUCT-GOAL.md` | 2026-11-08 用户重申的产品章程;与总指令冲突时以用户最新指令为准并回报裁定 |
| 研发状态/恢复 | 本目录 `CURRENT_STATE.md`+`RESUME.md` | — |
| 引擎运转面(轮次/合同/审批) | `~/agent-loop/`(STATE.md 顶部速览) | 仓库外,不迁入;本目录只记研发面结论 |
| 数据缺口台账(18 项) | `docs/P2_DATA_GAP_LEDGER.md` | `OPEN_ISSUES.md` 只挂指针 |
| 历史遗留问题 | `docs/REMAINING_ISSUES.md` | 同上 |
| 验收报告存档 | `audit/` | 各章程验收终报告原处 |
