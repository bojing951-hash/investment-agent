#!/bin/zsh
# ci.sh [sha] — list CI runs on the PR branch (token from macOS keychain; never echoed).
SHA="${1:-}"
KP=$(printf "protocol=https\nhost=github.com\n" | git credential-osxkeychain get | grep '^password=' | cut -d= -f2)
[ -n "$KP" ] || { echo "no token"; exit 1; }
Q="branch=dev/audit-fix-r1&per_page=6"
[ -n "$SHA" ] && Q="branch=dev/audit-fix-r1&per_page=20&head_sha=$SHA"
curl -s -H "Authorization: token $KP" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/bojing951-hash/investment-agent/actions/runs?$Q" \
| python3 -c "
import json, sys
j = json.load(sys.stdin)
for r in j.get('workflow_runs', [])[:8]:
    print(r['id'], r['head_sha'][:7], r['name'], r['status'], r['conclusion'], r['created_at'], r['html_url'])
if 'message' in j: print('API:', j['message'][:200])
"
