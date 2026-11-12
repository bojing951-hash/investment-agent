#!/bin/bash
# PreCompact 钩子候选(investment-agent·R21·Charter 10 §4.1)
# 作用: 上下文压缩前提醒保存检查点,并只读播报当前检查点状态。
# 纪律: 只读不写、不阻断压缩;压缩后由 SessionStart 钩子/恢复步骤重读状态。
proj="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
echo "[investment-agent] PreCompact: 立即保存检查点——CURRENT_STATE.md 权威快照+RESUME.md「下一步」;轮末收口=prose 先行→rd_checkpoint.py --finalize(finalize 必须是分支最后一笔提交)" >&2
if [ -f "$proj/scripts/rd_checkpoint.py" ]; then
  (cd "$proj" && python3 scripts/rd_checkpoint.py --verify --repo . 2>&1 | tail -3) >&2 || true
fi
exit 0
