# Audit-R7 追加注记(append-only,不改既有档)

归档: `20261117T083954Z_中国宏观信用与制造业景气_CN_NEW_LOANS_新增贷款与_
CN_PMI_M/`(R6 中国任务 B 新链,裁决 UPHELD)。本注记仅追加信息,原档零改动。

## run.git_head=null 根因与版本绑定补全

- 本 run 执行树=`/tmp/audit_r6/engine`(代码副本,**无 .git**);当时
  `_git_head` 单级 `git rev-parse --short HEAD`(cwd=运行树)落空→
  run.git_head=null——版本失绑根因即此,非隐藏执行。
- R7-03 修复: `_git_state` 三级绑定链(运行树 git 库→代码树 scripts
  所在仓→运行树根 `CODE_VERSION.json` 印章)+ `run.git_head_source`/
  `run.git_diff_sha256` 两字段随档(执行树有未提交修改时以差异指纹
  可核对)。此后引擎树(代码副本)运行不再失绑。
- 本档执行版本回溯性锚定(输入侧,非重跑): 研究输入=冻结市场快照
  research_snapshot_20261112_v2(sha e2e91525…171769)+正式生成器随档
  macro_20261117.json(sha be1f7680…22c09e,已随重放包交付
  `docs/autonomous-rd/cn-task-b-20261117T083954Z/macro_input/`);
  研究席重放输出与 R5 冻结输出逐字节一致;独立席复算 105/105。

## 当前代码复验状态

- 判定档合同在 R7 代码(dev/audit-fix-r1 工作树)上重跑口径不变
  (R6 §五 VERIFIED 6 检查=4 VERIFIED+2 STALE,与 attach 记录一致);
  复算脚本已参数化(净检出直接可跑,见下)。
- 独立复放: `docs/autonomous-rd/cn-task-b-20261117T083954Z/
  review_seat/recompute_r6b.py`——默认按 `__file__` 相对定位 seat_data,
  `--seat/--out` 可覆写,校验失败非零退出;重放产物
  `recompute_replay_out.txt` 与冻结档核心段(162 行)逐行一致,
  105/105 OK(冻结档尾另有席位追加「反例面扫描补充」6 行,append-only)。
