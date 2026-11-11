# ITERATION_LOG — 研发轮记录(只追加)

> 记录粒度: 一个章程/一个重要阶段一条。历史大节点自 git tag 与发布记录回填(2026-11-11)。
> 2026-11-08 之前的 38 包轮次明细在 `~/agent-loop/rounds` 与 `contracts/`(仓库外,不迁入)。

| 日期 | 轮/章程 | 交付 | tag@SHA | 验收 |
|---|---|---|---|---|
| 11-04 | W5 终局 | china 采集通道改造+重跑 | w5-final-20261104@5ab7c16 | Agent4 终裁 |
| 11-05 | P3 终局 | 38/38 全收口+四层封版 | p3-final-20261108@bafb0f3 | 四层全封 |
| 11-07 | P1/P2 终局 | 实现链封版 | p1-final-20261107@0c9fc3f / p2-final-20261107@9fb23ec | 用户亲批 |
| 11-08 | OSS 产品化 | 公开仓+主 CI 基线 90 | v0.1.0-alpha@ac5d2a2 | 已公开 |
| 11-08 | Agent Skill 化 | 技能+ia_cli 八能力+安装器 | v0.2.0-alpha@cb38e21 | CI 绿=基线 93 |
| 11-09 | v1.1 整改 | P0×4+安装器+档案旁挂 | v0.3.0-alpha@79f2551 | 九项验收 9 PASS |
| 11-09 | Model-Agnostic v2.0 | Agent Native 零额外 Key/凭证消毒/归档六参 | v0.4.0-alpha@2af3f9f | 四路验收 9 PASS+CODEX NOT_VERIFIED |
| 11-09 | v2.1 整改+glm 清零 | 旗标删除/模块改名/门禁三态/--lag | v0.5.0-alpha@0f92151 | 13 判定全 PASS |
| 11-10 | Charter 6 全球宏观深度 | analog 六维引擎/十年数据/Shiller 145 年 | v0.6.0-alpha@cca2e4a | 四路审计+D 席四案例全 PASS |
| 11-10 | Charter 7 能力建设 | P0 七问题修复+SOFR/WALCL+缺口台账 18 项 | v0.7.0-alpha@97d758e | D 席终验六项全 PASS |
| 11-10 | 数据批 1 | SPX_EPS 145 年+DAX/CAC/CN 六指数+M2SL | v0.7.1-alpha@cd5524c | 复验五面全 PASS;LIVE 部署此面 |
| 11-11 | Charter 8 机构观点 | 观点库 11 份/10 机构+view_verifier+四页工作台 | v0.8.0-alpha@06bb65d | 五席协作+E 席七面零 BLOCKER |
| 11-11 | Charter 9 研究闭环 | 三型验证/六标签/四状态/research-map/一键研究 | v0.9.0-alpha@cdffebe | A-E 全 PASS+反例 10/10;CI 基线 126 |
| 11-11 | 长期研发章程初始化 | CLAUDE.md+autonomous-rd 七文件 | dev/autonomous-rd-charter | 总指令待落位,待用户验收 |

## 排队中

- **总指令落位轮**: `PRODUCT_GOAL.md` 原文入库 → `ACCEPTANCE_CRITERIA.md`/`CAPABILITY_MATRIX.md`
  对齐 → 全仓差距审计 → 首轮研发(等用户下一条)。
- **F 补证轮**: 2026-12-05 观察钟满,引擎自动触发(日历门,勿手工提前)。
