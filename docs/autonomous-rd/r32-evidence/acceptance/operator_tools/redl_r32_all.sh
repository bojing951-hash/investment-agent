#!/bin/zsh
# redl_r32_all.sh <commit_sha> — run redl_replay.sh for the R32 final packages in sequence
# (the four archived work orders; C4 has no package: archive refused by design).
# Master log: /tmp/r32-accept/redl/<sha7>/r32_all_<ts>.log
SHA="$1"
SHA7=$(echo "$SHA" | cut -c1-7)
mkdir -p /tmp/r32-accept/redl/$SHA7
LOG=/tmp/r32-accept/redl/$SHA7/r32_all_$(date +%Y%m%dT%H%M%S).log
{
  echo "=== redl_r32_all start $(date '+%F %T') sha=$SHA"
  for pair in "session_A_formal:A" "session_B_formal:B" "session_T3_formal:T3" "session_NEW30:N30"; do
    s="${pair%%:*}"; t="${pair#*:}"
    echo "--- session=$s tag=$t start $(date '+%T')"
    zsh /tmp/r32-accept/scripts/redl_replay.sh "$SHA" "$s" "R32-$t" > /tmp/r32-accept/redl/$SHA7/r32_${t}.out 2>&1
    echo "--- session=$s tag=$t end rc=$? $(date '+%T')"
  done
  echo "=== redl_r32_all end $(date '+%F %T')"
} >> "$LOG" 2>&1
echo "$LOG"
