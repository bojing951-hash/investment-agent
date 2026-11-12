#!/bin/bash
# SessionStart 钩子候选(investment-agent·R21·Charter 10 §4.1)
# 作用: 新会话第一屏给出恢复入口 + 只读跑一致性门播报结果。
# 纪律: 本钩子只读不写、永不阻断会话(门 FAIL 只播报警告,真正硬拦在
# CI 与 finalize 管线);失败静默。安装方法见同目录 README.md。
proj="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
echo "[investment-agent] 新会话恢复入口: ①CLAUDE.md ②PRODUCT_GOAL.md ③docs/autonomous-rd/RESUME.md 检查点块 ④核对 git rev-parse HEAD(不盲信文档)" >&2
if [ -f "$proj/scripts/rd_state_consistency.py" ]; then
  if out=$(cd "$proj" && python3 scripts/rd_state_consistency.py --quiet --repo . 2>&1); then
    echo "[investment-agent] 状态一致性门: PASS(六项全绿,状态可信,准予开发)" >&2
  else
    echo "[investment-agent] ⚠ 状态一致性门: FAIL——禁止直接进入开发,先对账:" >&2
    echo "$out" | grep 'FAIL' | head -6 >&2
    echo "[investment-agent] 定位: python3 scripts/rd_state_consistency.py --repo ." >&2
  fi
fi
exit 0
