#!/bin/zsh
# ci_wait.sh <sha40> [max_minutes] — poll the CI run of one commit on the PR branch every 30 s until it
# completes, then print "<run id> <status> <conclusion> <url>". Token from macOS keychain, never echoed.
SHA="$1"; MAX="${2:-45}"
KP=$(printf "protocol=https\nhost=github.com\n" | git credential-osxkeychain get | grep '^password=' | cut -d= -f2)
[ -n "$KP" ] || { echo "no token"; exit 1; }
t=0
while [ $t -lt $((MAX*60)) ]; do
  R=$(curl -s --max-time 40 -H "Authorization: token $KP" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/bojing951-hash/investment-agent/actions/runs?branch=dev/audit-fix-r1&per_page=10&head_sha=$SHA" \
  | SHA="$SHA" python3 -c "
import json, os, sys
try:
    j = json.load(sys.stdin)
except Exception:
    print('parse-error'); sys.exit(0)
rs = [r for r in j.get('workflow_runs', []) if r.get('head_sha') == os.environ['SHA']]
if not rs:
    print('none-yet'); sys.exit(0)
r = rs[0]
print(r['id'], r['status'], r.get('conclusion'), r.get('html_url'))
")
  echo "$(date '+%H:%M:%S') $R"
  case "$R" in
    *completed*) exit 0 ;;
  esac
  sleep 30; t=$((t+30))
done
echo "timeout after $MAX minutes"
exit 3
