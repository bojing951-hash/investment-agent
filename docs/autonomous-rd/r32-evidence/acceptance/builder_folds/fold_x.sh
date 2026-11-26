#!/bin/zsh
# fold_x.sh <tag> <in_judgment.json> <out_judgment.json> [--expect-new-engine]
# Run one builder fold script (fold_<tag>5.py) against the work order re-planned
# at the consolidated-fix stamp (tree + run dir from /tmp/r32-accept/env5.sh).
TAG="$1"; IN="$2"; OUTJ="$3"; shift 3
source /tmp/r32-accept/env5.sh
case "$TAG" in
  C4) TREE=/tmp/r32-accept/final5-degraded ;;
  *) TREE=/tmp/r32-accept/final5 ;;
esac
case "$TAG" in
  A) RD="$RD_A" ;; B) RD="$RD_B" ;; T3) RD="$RD_T3" ;; N30) RD="$RD_N30" ;;
  C4) RD="$RD_C4" ;; AUG) RD="$RD_AUG" ;; *) echo "unknown tag $TAG"; exit 2 ;;
esac
mkdir -p "$(dirname "$OUTJ")"
LOG=/tmp/r32-accept/out/fold_X_${TAG}.txt
/usr/bin/python3 -I /tmp/r32-accept/scripts/fold_${TAG}5.py "$IN" "$TREE" "$RD" "$OUTJ" "$@" > "$LOG" 2>&1
rc=$?
echo "fold $TAG rc=$rc | in=$(basename "$IN") out=$OUTJ | tree=$(basename "$TREE") run=$(basename "$RD" | cut -c1-16) args=$*"
echo "$(date '+%Y-%m-%d %H:%M:%S') op stage=fold tag=$TAG tree=$(basename "$TREE") rc=$rc args=$IN -> $OUTJ $*" >> /tmp/r32-accept/seat_operator.log
exit $rc
