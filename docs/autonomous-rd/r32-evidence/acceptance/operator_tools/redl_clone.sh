#!/bin/zsh
# redl_clone.sh <session_dir> — clone the PR branch tip (depth 1) into <session_dir>/src,
# retrying on transport failures (the public host is reached directly and times out at times);
# every attempt is appended to <session_dir>/console.log. Exit 0 once src/.git exists.
D="$1"
cd "$D" || exit 2
URL=https://github.com/bojing951-hash/investment-agent.git
if [ -d src/.git ]; then echo "clone: reusing existing src" | tee -a console.log; exit 0; fi
for i in 1 2 3 4 5 6; do
  if git clone --quiet --depth 1 --branch dev/audit-fix-r1 "$URL" src 2> clone.err; then
    echo "clone: ok (attempt $i, $(date '+%T'))" | tee -a console.log; exit 0
  fi
  echo "clone: attempt $i failed: $(tail -1 clone.err | cut -c1-160)" | tee -a console.log
  if [ -e src ]; then echo "clone: partial destination left behind — inspect by hand" | tee -a console.log; exit 5; fi
  [ "$i" -lt 6 ] && sleep 30
done
echo "clone failed after 6 attempts" | tee -a console.log
exit 4
