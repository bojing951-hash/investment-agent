#!/bin/zsh
# redl_r31_all.sh <commit_sha> [orig_new30_pkg_dir] — run redl_r31.sh for the three R31 archive
# packages in sequence (A4/B2 = single UPHELD verdict; NEW30 = REVISE→UPHELD two-verdict chain). All
# three take the same path: manifest check, blob identity, strict replay on the cloned commit's engine
# (expected: version gate), six steps on the recording-code engine. With the optional second argument
# the NEW30 run also compares the downloaded package file by file with the original archive package of
# the R31 work area (read-only reference on this machine; redl_r31.sh step [2b]).
# session_T3b_formal is an evidence copy of a run directory, not an archive package (no
# ARCHIVE_MANIFEST.json) → not replayable, not listed.
# Master log: /tmp/r32-accept/redl/<sha7>/r31_all_<ts>.log
SHA="$1"; ORIG="${2:-}"
SHA7=$(echo "$SHA" | cut -c1-7)
mkdir -p /tmp/r32-accept/redl/$SHA7
LOG=/tmp/r32-accept/redl/$SHA7/r31_all_$(date +%Y%m%dT%H%M%S).log
{
  echo "=== redl_r31_all start $(date '+%F %T') sha=$SHA"
  for pair in "session_A4_formal:A4dl" "session_B2_formal:B2dl" "session_NEW30:NEW30dl"; do
    s="${pair%%:*}"; t="${pair#*:}"
    echo "--- session=$s tag=$t start $(date '+%T')"
    if [ "$s" = session_NEW30 ] && [ -n "$ORIG" ]; then
      ORIG_PKG="$ORIG" zsh /tmp/r32-accept/scripts/redl_r31.sh "$SHA" "$s" "$t" > /tmp/r32-accept/redl/$SHA7/r31_${t}.out 2>&1
    else
      zsh /tmp/r32-accept/scripts/redl_r31.sh "$SHA" "$s" "$t" > /tmp/r32-accept/redl/$SHA7/r31_${t}.out 2>&1
    fi
    echo "--- session=$s tag=$t end rc=$? $(date '+%T')"
  done
  echo "=== redl_r31_all end $(date '+%F %T')"
} >> "$LOG" 2>&1
echo "$LOG"
