#!/bin/bash
# Audit-R24 任务5 Seat-A 一问验收(真实会话,零上下文,唯一输入=原问句)
# 前置: /tmp/r68/accept/install = git archive <代码修复SHA> + data/daily 面拷贝 + 技能已从该树安装(personal-cc --force)
# 会话: claude -p "$(cat run_question_verbatim.txt)"  cwd=install 树  (与 rd-headless round.sh 同款纪律)
set -u
BASE=/tmp/r68/accept
INSTALL="$BASE/install"
LOG="$BASE/seat_a_session.log"
CB=$(ls -d "$HOME"/.vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude 2>/dev/null | sort -V | tail -1)
[ -z "$CB" ] || [ ! -x "$CB" ] && { echo "FATAL: 未发现 claude 二进制" > "$LOG"; exit 1; }
echo "$(date '+%F %T') binary=$CB" > "$LOG"
cd "$INSTALL" || exit 1
( "$CB" -p "$(cat "$BASE/run_question_verbatim.txt")" \
    --permission-mode acceptEdits \
    --max-budget-usd 50 \
    --allowedTools 'Edit' 'Write' 'Read' 'Glob' 'Grep' 'Skill' 'Agent' 'Task' \
        'Bash(python3 *)' 'Bash(python *)' \
        'Bash(git status*)' 'Bash(git diff*)' 'Bash(git log*)' 'Bash(git show*)' \
        'Bash(ls *)' 'Bash(grep *)' 'Bash(diff *)' 'Bash(wc *)' 'Bash(sha256sum *)' \
        'Bash(shasum *)' 'Bash(head *)' 'Bash(tail *)' 'Bash(cat *)' 'Bash(mkdir *)' \
        'Bash(cp *)' 'Bash(mv *)' 'Bash(sed *)' 'Bash(sort *)' 'Bash(find *)' \
    --disallowedTools 'Bash(git push*)' 'Bash(git remote*)' 'Bash(ssh *)' \
        'Bash(scp *)' 'Bash(curl *)' 'Bash(rm -rf *)' 'Bash(npm *)' 'Bash(pip *)' \
        'Bash(git switch*)' 'Bash(git checkout *)' 'Bash(git worktree *)' 'Bash(git add *)' 'Bash(git commit *)' \
    >> "$LOG" 2>&1 ) &
PID=$!
( sleep 9000; kill "$PID" 2>/dev/null ) &
WATCHDOG=$!
wait "$PID"; RC=$?
kill "$WATCHDOG" 2>/dev/null
echo "$(date '+%F %T') acceptance session done rc=$RC" >> "$LOG"
exit "$RC"
