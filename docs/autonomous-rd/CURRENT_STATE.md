# CURRENT_STATE — 最新研发状态

> 研发面恢复入口(新会话先读这里,再读 `RESUME.md`)。
> 引擎运转面(LIVE/轮次/合同)不在本档——见 `~/agent-loop/STATE.md` 顶部速览。
> 更新纪律: 每完成一个重要研发阶段必须更新本档(进度/测试与审计结果/分支与 Commit/下一步)。

## 快照: 2026-11-11 (HKT, R2 后)

- **基线**: main = `cdffebe`(v0.9.0-alpha,Charter 9「全球宏观研究闭环与一键研究」当日闭合);
  Release 441388150 上线,CI 42983226791 绿 = main 基线 126 槽。
- **LIVE(阿里云)**: 仍跑 v0.7.1 面;升级新面 = 用户保留卡点③,待批。
- **引擎**: 停于唯一日历门——F 补证轮观察钟 2026-12-05 满自动触发,此前无排程任务。
- **长期研发章程**: 2026-11-11 用户《总指令》原文已落位 `PRODUCT_GOAL.md`;
  《长期自主研发系统启动指令》原文已落位 `RUN_MANDATE.md`(自主循环/环境自检/AC11–AC12)。
  FINAL_ACCEPTANCE.md: AC3 = **PARTIAL**(R1+审计收口),AC6 = **PARTIAL**(R2 编排器真执行),
  其余 NOT_VERIFIED。
- **R2(一键研究真执行)已完成**: 分支 `dev/rd-r2-research-orchestrator` @`ac40ef8`+
  R1.1 并入(merge `946625b`)——`scripts/research_orchestrator.py` 十一步确定性管线
  (S1 分解→S11 归档):每步真 `ia_cli` 子进程执行+信封留档,process-ok 与 semantic-ok
  分记,L3 AI 推断/L4 条件情景恒 declared-not-produced(诚实面),逐数证据索引
  (L1 每行挂 snapshot fact_id/L2 挂 VP-id),实体映射零命中=如实 unmapped 不猜,
  归档默认关。入口 `ia_cli.py research-run --question …`。自测 31 判定绿;R1 无回归;
  **全套回归 129/129 exit 0**(全仓口径=tests/128+根 test_env.py 环境探测脚本)。
- **R1(三型证据落库)已完成+审计收口**: 分支 `dev/rd-r1-stage-evidence` @ `26d4ef7`——
  VP sidecar v1.1(阶段A/B 结构化+stage_labels,mode C 契约零变动)、research-map 命令清单
  可执行化(14 条实解析)、页③三阶段证据披露;本地 17 份 VP 重建(A面 12 INSUFFICIENT/
  4 PARTIALLY_SUPPORTED/1 MIXED;B面 12 INSUFFICIENT/5 MIXED)。**全套回归已绿**(2026-11-11
  在 R1 分支干净重跑: 129/129 文件全部 exit 0,零 FAIL;此前章程分支上的作废运行系测试文件
  被分支切换污染)。**独立审计已收口**(2026-11-11,对抗式 6 维: 无前视/标签纪律/方向归因/
  契约真实性/可复算性/B面抽验——六维全 PASS,交付物 17/17 清洁、逐字节重建一致、31 数值
  独立复算全中;结论=无 BLOCKER,2 MAJOR 潜伏缺陷+6 MINOR+3 NIT,报告 `/tmp/r1_audit_report.md`)。
  **R1.1 已修**(MAJOR-1 `interval_change` 入口日期归一 `_norm_ymd`(无横线端锚字符串比较
  使封顶整年失效)→ 根治含阶段B端锚与回落序列;MAJOR-2 `_hypothesis_directions` 废双基
  容忍、定 1-based 单基+provenance 记 `forecast_index_basis`;MINOR-3 词表否定护栏
  ('不再加息'/'no further cuts'/'supply-driven'→None)+英文词边界正则)。回归: 套件增至
  50 判定全绿+受影响 8 文件全 exit 0;**对照实验**(HEAD 代码 vs 修复代码、同一份真数据、
  独立进程、同种子重建 17 份)= 语义零差异 0/17,证明修复不改今日产出。剩余 MINOR 转
  `OPEN_ISSUES.md` 技术待办。章程分支已并入 R1 分支(merge 87afebe,统一历史线)。
- **自主机制**(2026-11-11 配置): 项目级 `.claude/settings.json`(gitignore,仅本地)挂
  PreCompact+SessionStart hooks——PreCompact 提醒完成检查点,SessionStart 提示恢复入口
  (CLAUDE.md→RESUME.md)。stderr 级提醒,无写操作;对在未来于本仓启动的会话生效。

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
