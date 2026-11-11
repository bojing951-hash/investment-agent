# CLAUDE.md — investment-agent 长期自主研发项目(会话启动必读)

本仓库 = GitHub `bojing951-hash/investment-agent` 本地开发树(公开仓)。项目运行于
《自主研发、独立审计与持续迭代》长期章程之下(2026-11-11 用户启动)。

## 每次会话启动,按序完成

1. 读 `docs/autonomous-rd/PRODUCT_GOAL.md` —— 最高目标文件(总指令原文)。
   未经用户明确授权,不得修改、删减或降低其中验收标准。
   若该文件不存在 = 总指令未落位,向用户索取原文,不得自行代拟。
2. 读 `docs/autonomous-rd/CURRENT_STATE.md` 与 `RESUME.md` —— 恢复最新状态与未完成任务。
3. 读 `docs/autonomous-rd/OPEN_ISSUES.md` —— 未解决问题与用户保留卡点。
4. 按研发循环继续: **审计 → 定优先级 → 开发 → 测试 → 独立验证 → 更新状态 → 下一轮**。
5. 引擎运转面(LIVE/轮次/合同)另见 `~/agent-loop/STATE.md` 顶部速览。
   研发恢复以本仓库 `docs/autonomous-rd/` 为准;LIVE 运转以 agent-loop 为准,互不重复维护。

## 红线(违者即停)

- 不得未经真实验收宣布最终完成;**CI 通过 ≠ 目标达成**
  (六层区分: 代码实现/合成测试/真实数据/真实机构资料/完整Agent流程/Web实际使用,未实际执行不得标 PASS)。
- 一切开发在 `dev/*` 独立分支;未经用户授权不合并 main、不推送公开仓(本仓为 public,推送=公开发布)。
- 不产生付费 API 费用;不绕付费墙;不删除重要数据;不动生产环境
  (阿里云 LIVE 树、launchd、GitHub 远端)。
- 已冻结的验收合同不得为通过而修改一字。
- `docs/autonomous-rd/PRODUCT_GOAL.md` 与 `ACCEPTANCE_CRITERIA.md` 的最终标准只有用户能改。
- 用户三保留卡点须用户亲自批准: ① 封版合并 main ② 新数据源凭证/付费 ③ LIVE 部署。

## 阶段检查点纪律

每完成一个重要研发阶段,必做:
更新 `CURRENT_STATE.md`(实际进度/测试与审计结果/分支与 Commit)→ 追加 `ITERATION_LOG.md`
→ 修订 `CAPABILITY_MATRIX.md` 差距 → 把下一步可执行任务写入 `RESUME.md`。
上下文将耗尽或会话将结束时,优先保存完整检查点,再处理其他事。
新会话必须仅凭仓库文件恢复工作,不依赖历史聊天记录。

时间戳一律带时区(默认 HKT/UTC+8;涉 CI 用 UTC)——本项目踩过时区炸弹,勿重蹈。
