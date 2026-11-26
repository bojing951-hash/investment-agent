#!/bin/zsh
# cijobs.sh <run_id> — list the jobs (name / conclusion / timestamps) of one CI run.
# Token from macOS keychain, never echoed.
RUN="$1"
KP=$(printf "protocol=https\nhost=github.com\n" | git credential-osxkeychain get | grep '^password=' | cut -d= -f2)
[ -n "$KP" ] || { echo "no token"; exit 1; }
curl -s -H "Authorization: token $KP" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/bojing951-hash/investment-agent/actions/runs/$RUN/jobs?per_page=20" \
| python3 -c "
import json, sys
j = json.load(sys.stdin)
if 'jobs' not in j:
    print('API:', str(j)[:200]); sys.exit(1)
print('run %s | total_count %s' % ('$RUN', j.get('total_count')))
for b in j['jobs']:
    print('  job %s | %s | %s / %s | %s -> %s' % (b['id'], b['name'], b['status'], b.get('conclusion'), b.get('started_at'), b.get('completed_at')))
    for s in b.get('steps', []):
        if s.get('conclusion') not in ('success', 'skipped', None):
            print('     step', s['name'], s.get('conclusion'))
"
