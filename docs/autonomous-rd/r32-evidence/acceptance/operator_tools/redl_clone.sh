#!/bin/zsh
# redl_clone.sh <session_dir> — clone the PR branch tip (depth 1) into <session_dir>/src,
# retrying on transport failures (the public host is reached directly and times out at times); attempts
# alternate https and ssh (the repository content is the same over either transport; git checks object
# ids, and the caller checks HEAD against the expected commit). Every attempt is appended to
# <session_dir>/console.log. Exit 0 once src/.git exists.
D="$1"
cd "$D" || exit 2
URL_HTTPS=https://github.com/bojing951-hash/investment-agent.git
URL_SSH=git@github.com:bojing951-hash/investment-agent.git
if [ -d src/.git ]; then echo "clone: reusing existing src" | tee -a console.log; exit 0; fi
for i in 1 2 3 4 5 6; do
  if [ $((i % 2)) -eq 1 ]; then url=$URL_HTTPS; via=https; else url=$URL_SSH; via=ssh; fi
  if git -c core.sshCommand='ssh -o ConnectTimeout=25 -o BatchMode=yes' clone --quiet --depth 1 --branch dev/audit-fix-r1 "$url" src 2> clone.err; then
    echo "clone: ok over $via (attempt $i, $(date '+%T'))" | tee -a console.log; exit 0
  fi
  echo "clone: attempt $i ($via) failed: $(tail -1 clone.err | cut -c1-160)" | tee -a console.log
  if [ -e src ]; then echo "clone: partial destination left behind — inspect by hand" | tee -a console.log; exit 5; fi
  [ "$i" -lt 6 ] && sleep 30
done
echo "clone failed after 6 attempts" | tee -a console.log
exit 4
