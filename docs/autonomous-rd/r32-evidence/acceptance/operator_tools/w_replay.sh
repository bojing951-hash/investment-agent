#!/bin/zsh
# w_replay.sh <tag> — replays of the final-stamp re-delivered package of one work order
# (/tmp/r32-accept/archive/r32w/<run id>), each into a fresh replay-out directory:
#   [1] W engine (the package's archiving code), strict
#       (expected: rc=0, byte_equal, all checks — gate 4 passes on the declared archiving code;
#        the package records run SHA = Y, the execution stamp)
#   [2] Y engine (the package's run SHA), strict
#       (expected: refused, verdict_binding_threeway — the execution-stamp code predates the
#        status-equivalence handling)
# Receipts: out/wreplay_<tag>_{Wstrict,Ystrict}.{json,err,rc}; outputs out/wreplay_<tag>_<name>_out/
set -u
TAG=$1; S=/tmp/r32-accept/scripts; O=/tmp/r32-accept/out
source /tmp/r32-accept/env8.sh
eval "RD=\$RDW_$TAG"; RID=$(basename "$RD")
case $TAG in C4) W=/tmp/r32-accept/final8-degraded; Y=/tmp/r32-accept/final6-degraded;;
  AUG) W=/tmp/r32-accept/final8-aug; Y=/tmp/r32-accept/final6-aug;;
  *) W=/tmp/r32-accept/final8; Y=/tmp/r32-accept/final6;; esac
PKG=/tmp/r32-accept/archive/r32w/$RID
[ -f "$PKG/ARCHIVE_MANIFEST.json" ] || { echo "not an archive package: $PKG"; exit 7; }
for spec in "Wstrict:$W:" "Ystrict:$Y:"; do
  name=${spec%%:*}; rest=${spec#*:}; eng=${rest%%:*}; flag=${rest#*:}
  if [ -e $O/wreplay_${TAG}_${name}_out ]; then echo "== $name: replay-out already exists (not overwritten)"; continue; fi
  echo "== $name  engine=$eng flag=${flag:-none}  ($(date '+%T'))"
  ( cd $eng && .venv/bin/python ia_cli.py research-one --stage replay --package "$PKG" \
      --replay-out $O/wreplay_${TAG}_${name}_out ${flag:+"$flag"} \
      > $O/wreplay_${TAG}_${name}.json 2> $O/wreplay_${TAG}_${name}.err; echo $? > $O/wreplay_${TAG}_${name}.rc )
  echo "rc=$(cat $O/wreplay_${TAG}_${name}.rc)"
  /usr/bin/python3 -I $S/rp_summ.py $O/wreplay_${TAG}_${name}.json
  tail -2 $O/wreplay_${TAG}_${name}.err | cut -c1-240
done
echo "$(date '+%F %T') w_replay $TAG pkg=$PKG Wstrict_rc=$(cat $O/wreplay_${TAG}_Wstrict.rc 2>/dev/null) Ystrict_rc=$(cat $O/wreplay_${TAG}_Ystrict.rc 2>/dev/null)" >> $O/ops_ledger.txt
