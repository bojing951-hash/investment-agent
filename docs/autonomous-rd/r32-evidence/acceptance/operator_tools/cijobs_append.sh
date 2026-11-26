#!/bin/zsh
# cijobs_append.sh <run_id> [...] — append the jobs of the given CI runs to out/ci_jobs_all_stamps.txt
# (same line format as the existing file: run | job | name | status | conclusion | started -> completed);
# a run already present in the file is skipped.  Token from macOS keychain, never echoed.
OUTF=/tmp/r32-accept/out/ci_jobs_all_stamps.txt
KP=$(printf "protocol=https\nhost=github.com\n" | git credential-osxkeychain get | grep '^password=' | cut -d= -f2)
[ -n "$KP" ] || { echo "no token"; exit 1; }
for RUN in "$@"; do
  if grep -q "^$RUN | " "$OUTF"; then echo "skip $RUN (already listed)"; continue; fi
  curl -s -H "Authorization: token $KP" -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/bojing951-hash/investment-agent/actions/runs/$RUN/jobs?per_page=20" \
  | RUN="$RUN" python3 -c "
import json, os, sys
j = json.load(sys.stdin)
if 'jobs' not in j:
    print('API:', str(j)[:200]); sys.exit(1)
for b in j['jobs']:
    print('%s | job %s | %s | %s | %s | %s -> %s' % (os.environ['RUN'], b['id'], b['name'], b['status'], b.get('conclusion'), b.get('started_at'), b.get('completed_at')))
" >> "$OUTF"
  echo "appended $RUN"
done
wc -l "$OUTF"
