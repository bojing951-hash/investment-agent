#!/bin/zsh
# z_replay.sh <tag> — replays of the post-fix re-delivered package of one work order
# (/tmp/r32-accept/archive/r32z/<run id>), each into a fresh replay-out directory:
#   [1] Z engine, strict                 (expected: refused, code_version_mismatch —
#                                        the package records run SHA = Y, the execution stamp)
#   [2] Z engine, --allow-code-mismatch  (expected: rc=0, byte_equal, all checks; disclosed)
#   [3] Y engine (the package's run SHA), strict
#                                        (expected: refused, verdict_binding_threeway — the
#                                        execution-stamp code predates the status-equivalence handling)
# Receipts: out/zreplay_<tag>_{Zstrict,Zallow,Ystrict}.{json,err,rc}; outputs out/zreplay_<tag>_<name>_out/
set -u
TAG=$1; S=/tmp/r32-accept/scripts; O=/tmp/r32-accept/out
source /tmp/r32-accept/env7.sh
eval "RD=\$RDZ_$TAG"; RID=$(basename "$RD")
case $TAG in C4) Z=/tmp/r32-accept/final7-degraded; Y=/tmp/r32-accept/final6-degraded;;
  AUG) Z=/tmp/r32-accept/final7-aug; Y=/tmp/r32-accept/final6-aug;;
  *) Z=/tmp/r32-accept/final7; Y=/tmp/r32-accept/final6;; esac
PKG=/tmp/r32-accept/archive/r32z/$RID
[ -f "$PKG/ARCHIVE_MANIFEST.json" ] || { echo "not an archive package: $PKG"; exit 7; }
for spec in "Zstrict:$Z:" "Zallow:$Z:--allow-code-mismatch" "Ystrict:$Y:"; do
  name=${spec%%:*}; rest=${spec#*:}; eng=${rest%%:*}; flag=${rest#*:}
  if [ -e $O/zreplay_${TAG}_${name}_out ]; then echo "== $name: replay-out already exists (not overwritten)"; continue; fi
  echo "== $name  engine=$eng flag=${flag:-none}  ($(date '+%T'))"
  ( cd $eng && .venv/bin/python ia_cli.py research-one --stage replay --package "$PKG" \
      --replay-out $O/zreplay_${TAG}_${name}_out ${flag:+"$flag"} \
      > $O/zreplay_${TAG}_${name}.json 2> $O/zreplay_${TAG}_${name}.err; echo $? > $O/zreplay_${TAG}_${name}.rc )
  echo "rc=$(cat $O/zreplay_${TAG}_${name}.rc)"
  /usr/bin/python3 -I $S/rp_summ.py $O/zreplay_${TAG}_${name}.json
  tail -2 $O/zreplay_${TAG}_${name}.err | cut -c1-240
done
echo "$(date '+%F %T') z_replay $TAG pkg=$PKG Zstrict_rc=$(cat $O/zreplay_${TAG}_Zstrict.rc 2>/dev/null) Zallow_rc=$(cat $O/zreplay_${TAG}_Zallow.rc 2>/dev/null) Ystrict_rc=$(cat $O/zreplay_${TAG}_Ystrict.rc 2>/dev/null)" >> $O/ops_ledger.txt
