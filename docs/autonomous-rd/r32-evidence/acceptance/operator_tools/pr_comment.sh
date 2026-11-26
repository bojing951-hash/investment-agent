#!/bin/zsh
# pr_comment.sh <body_file> — post ONE delivery comment on PR #1 (bojing951-hash/investment-agent) from a UTF-8
# body file; prints the comment id and html_url only. Token from the macOS keychain, never echoed.
BODY="$1"
[ -f "$BODY" ] || { echo "body file missing"; exit 2; }
KP=$(printf "protocol=https\nhost=github.com\n" | git credential-osxkeychain get | grep '^password=' | cut -d= -f2)
[ -n "$KP" ] || { echo "no token"; exit 1; }
python3 -I - "$BODY" > /tmp/r32-accept/out/pr_comment_payload.json <<'PY'
import json, sys
print(json.dumps({"body": open(sys.argv[1], encoding='utf-8').read()}, ensure_ascii=False))
PY
curl -s -X POST -H "Authorization: token $KP" -H "Accept: application/vnd.github+json" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data-binary @/tmp/r32-accept/out/pr_comment_payload.json \
  "https://api.github.com/repos/bojing951-hash/investment-agent/issues/1/comments" \
| python3 -c "
import json, sys
j = json.load(sys.stdin)
print('comment', j.get('id'), j.get('html_url'), j.get('created_at')) if 'id' in j else print('API:', str(j)[:300])
"
rm -f /tmp/r32-accept/out/pr_comment_payload.json
