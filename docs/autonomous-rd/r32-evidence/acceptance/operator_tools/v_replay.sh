#!/bin/zsh
# v_replay.sh <tag> — replays of the final-stamp (V) re-delivered package of one work order
# (/tmp/r32-accept/archive/r32v/<run id>), each into a fresh replay-out directory:
#   [1] V engine (the package's archiving code), strict
#       (expected: status-equivalent packages rc=0, byte_equal, all checks — gate 4 accepts the declared
#        archiving code; same-render packages (the map was rendered at the execution stamp with the
#        verdict already bound, e.g. B): refused, gate 4 code_version_mismatch — the archiving code is
#        not the recording code; the delivered bytes are the execution-stamp rendering)
#   [2] Y engine (the package's run SHA = the execution stamp), strict
#       (status-equivalent packages: refused, verdict_binding_threeway — the execution-stamp code
#        predates the status-equivalence handling; same-render packages: rc=0 byte_equal)
#   [1b] with the argument `override`: V engine + --allow-code-mismatch (same-render packages: rc=0 with the
#       override disclosed; the replay report says so and does not claim a declared status equivalence)
# Receipts: out/vreplay_<tag>_{Vstrict,Ystrict[,Voverride]}.{json,err,rc}; outputs out/vreplay_<tag>_<name>_out/
set -u
TAG=$1; S=/tmp/r32-accept/scripts; O=/tmp/r32-accept/out
source /tmp/r32-accept/env9.sh
eval "RD=\$RDV_$TAG"; RID=$(basename "$RD")
case $TAG in C4) W=/tmp/r32-accept/final9-degraded; Y=/tmp/r32-accept/final6-degraded;;
  AUG) W=/tmp/r32-accept/final9-aug; Y=/tmp/r32-accept/final6-aug;;
  *) W=/tmp/r32-accept/final9; Y=/tmp/r32-accept/final6;; esac
PKG=/tmp/r32-accept/archive/r32v/$RID
[ -f "$PKG/ARCHIVE_MANIFEST.json" ] || { echo "not an archive package: $PKG"; exit 7; }
specs=("Vstrict:$W:" "Ystrict:$Y:")
[ "${2:-}" = override ] && specs+=("Voverride:$W:--allow-code-mismatch")
for spec in $specs; do
  name=${spec%%:*}; rest=${spec#*:}; eng=${rest%%:*}; flag=${rest#*:}
  if [ -e $O/vreplay_${TAG}_${name}_out ]; then echo "== $name: replay-out already exists (not overwritten)"; continue; fi
  echo "== $name  engine=$eng flag=${flag:-none}  ($(date '+%T'))"
  ( cd $eng && .venv/bin/python ia_cli.py research-one --stage replay --package "$PKG" \
      --replay-out $O/vreplay_${TAG}_${name}_out ${flag:+"$flag"} \
      > $O/vreplay_${TAG}_${name}.json 2> $O/vreplay_${TAG}_${name}.err; echo $? > $O/vreplay_${TAG}_${name}.rc )
  echo "rc=$(cat $O/vreplay_${TAG}_${name}.rc)"
  /usr/bin/python3 -I $S/rp_summ.py $O/vreplay_${TAG}_${name}.json
  tail -2 $O/vreplay_${TAG}_${name}.err | cut -c1-240
done
echo "$(date '+%F %T') v_replay $TAG pkg=$PKG Vstrict_rc=$(cat $O/vreplay_${TAG}_Vstrict.rc 2>/dev/null) Ystrict_rc=$(cat $O/vreplay_${TAG}_Ystrict.rc 2>/dev/null)" >> $O/ops_ledger.txt
