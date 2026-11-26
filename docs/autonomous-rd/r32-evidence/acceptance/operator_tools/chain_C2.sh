#!/bin/zsh
# chain_C2.sh <commit_sha40> <orig_new30_pkg_dir>
# Continuation of chain_C.sh after its first run was stopped: step 1 (R32 four packages) had completed and
# is kept; the R31 step was stuck in the baseline fetch (the public host's https endpoint timed out for
# 4 attempts). This script runs, in one sequence (no parallel engine processes):
#   2. re-download replays of the three R31 packages (redl_r31_all.sh; NEW30 also compared with the
#      original archive package of the R31 work area, read-only; fetches alternate https / ssh)
#   3. offline battery of the committed tree (battery.sh C; raw logs stay outside the repo)
#   4. post-commit phase6 check (29/0 expected)
# Console: /tmp/r32-accept/out/correction/chain_C2.console.log
set -u
C40="$1"; ORIG="$2"
[ "${#C40}" -eq 40 ] || { echo "sha must be 40 hex"; exit 2; }
[ -d "$ORIG" ] || { echo "original NEW30 package dir missing: $ORIG"; exit 2; }
O=/tmp/r32-accept/out/correction
S=/tmp/r32-accept/scripts
mkdir -p "$O" /tmp/r32-accept/out/post_commit_correction
{
  echo "=== chain_C2 start $(date '+%F %T') sha=$C40"
  zsh "$S/redl_r31_all.sh" "$C40" "$ORIG"; echo "step2 r31_all rc=$? $(date '+%T')"
  zsh "$S/battery.sh" C; echo "step3 battery rc=$? $(date '+%T')"
  ( cd ~/investment-agent-product && git status --short | wc -l && git rev-parse HEAD && python3 tests/test_arch_reform_phase6.py ) \
    > /tmp/r32-accept/out/post_commit_correction/phase6_postcommit_C.txt 2>&1
  echo "step4 phase6 rc=$? $(date '+%T')"
  echo "=== chain_C2 end $(date '+%F %T')"
} > "$O/chain_C2.console.log" 2>&1
echo "$O/chain_C2.console.log"
