# hooks-candidate — 上下文管理钩子候选安装物(R21·Charter 10 §4.1)

> 2026-11-12 R21 持续执行验证波的交付物之一。**本目录是候选安装物,不是已安装
> 配置**——安装属操作者席(修改运行环境配置超出开发波权限面)。

## 为什么存在(实查结论,非历史文档口径)

R21 对当前环境逐项实查(`R21_CONTINUOUS_EXECUTION_AUDIT.md` §2):

| 面 | 实查真相 |
|---|---|
| 用户级 ~/.claude/settings.json | 只有 gstack Stop 钩子,**无** investment 相关钩子 |
| 项目 .claude/settings.json | 有 PreCompact/SessionStart,但仅 `echo … >&2` 提醒;且 **.claude/ 被 .gitignore(:16)排除**——worktree/CI 克隆/干净装机(AC9)全部不存在 |
| 机器强制力 | 一致性门在 CI(offline-tests.yml 硬门)+ finalize 管线,与钩子无关,**已在仓内、随克隆走** |

即: 钩子面当前是「本地弱提醒」,且不可移植。本目录把钩子升级为**可安装、随仓
分发**的候选物: SessionStart 不再只 echo,而是只读跑一致性门并播报 PASS/FAIL
(FAIL=「禁止直接开发,先对账」),把 RESUME 步骤 4 的纪律推到会话第一屏。

## 内容

- `session_start.sh` — 恢复入口四步 + `rd_state_consistency.py --quiet` 只读
  播报(FAIL 只警告不阻断;硬拦在 CI/finalize)。
- `pre_compact.sh` — 压缩前检查点提醒 + `rd_checkpoint.py --verify` 尾三行。
- `settings.fragment.json` — 待合并进项目 `.claude/settings.json` 的 hooks
  片段(SessionStart/PreCompact 各一条,timeout 30/15s)。

## 安装(操作者席执行;开发波不得改运行配置)

```bash
cd <repo>
# 1) 钩子可执行
chmod +x ops/hooks-candidate/*.sh
# 2) 手测两钩子(应看到 stderr 播报,exit 0)
bash ops/hooks-candidate/session_start.sh; echo rc=$?
bash ops/hooks-candidate/pre_compact.sh;  echo rc=$?
# 3) 把 settings.fragment.json 的 hooks 键合并进 .claude/settings.json
#    (手工合并或 jq;该文件在 .gitignore 内,属本机配置)
# 4) 重开会话验证第一屏出现「[investment-agent] 新会话恢复入口」与门播报
```

## 诚实边界

- 钩子是**提示与播报**,不是强制: 会话内跳过播报不构成违规;真正的强制力=
  CI 硬门 + finalize 管线 + 恢复验收测试(tests/test_rd_r20_recovery.py)。
- 钩子只读: 不写任何状态档、不改 Git,任何失败静默 exit 0(不阻断会话)。
- `$CLAUDE_PROJECT_DIR` 由 Claude Code 注入;直接裸跑脚本时回退脚本相对定位。
