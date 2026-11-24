#!/bin/zsh
# z_deliver.sh <tag> — re-deliver one carried work order at the post-fix stamp (Z):
#   1. keep the carried MAP_REPORT.md bytes (execution stamp Y) -> out/zymap_<tag>_pre.md
#   2. report   (review-status surface refreshed when the verdict is approved)
#   3. diff Y bytes vs delivered (zmapdiff.py)                  -> out/zmapdiff_<tag>.txt
#   4. archive  -> /tmp/r32-accept/archive/r32z/<run id>  (a draft must be refused: no directory)
# Usage: zsh z_deliver.sh T3
set -u
TAG=$1
S=/tmp/r32-accept/scripts; O=/tmp/r32-accept/out
source /tmp/r32-accept/env7.sh
eval "RD=\$RDZ_$TAG"; eval "RS=\$RDY_$TAG"
case $TAG in C4) TREE=/tmp/r32-accept/final7-degraded; YTREE=/tmp/r32-accept/final6-degraded;;
  AUG) TREE=/tmp/r32-accept/final7-aug; YTREE=/tmp/r32-accept/final6-aug;;
  *) TREE=/tmp/r32-accept/final7; YTREE=/tmp/r32-accept/final6;; esac
RID=$(basename "$RD")
PRE=$O/zymap_${TAG}_pre.md
[ -e "$PRE" ] && { echo "pre snapshot exists: $PRE (not overwritten)"; exit 2; }
cp -p "$RD/MAP_REPORT.md" "$PRE"
echo "== report $TAG ($(date '+%F %T'))"
zsh $S/rx.sh "$TREE" "Z$TAG" report --report-dir "$RD"
RRCPT=$(ls -t $O/Z${TAG}_report_*.json | head -1); RRC=$(sed 's/rc=//' ${RRCPT%.json}.rc)
echo "report rc=$RRC receipt: $RRCPT"
/usr/bin/python3 -I $S/zmapdiff.py "$PRE" "$RD" "$YTREE" "$TREE" "${RID:0:16}" > $O/zmapdiff_${TAG}.txt 2>&1
echo "zmapdiff rc=$? -> $O/zmapdiff_${TAG}.txt"
head -12 $O/zmapdiff_${TAG}.txt | cut -c1-200
ARCBASE=/tmp/r32-accept/archive/r32z
mkdir -p "$ARCBASE"
echo "== archive $TAG ($(date '+%F %T'))"
zsh $S/rx.sh "$TREE" "Z$TAG" archive --report-dir "$RD" --archive-dir "$ARCBASE/$RID"
ARCPT=$(ls -t $O/Z${TAG}_archive_*.json 2>/dev/null | head -1); rc=$(sed 's/rc=//' ${ARCPT%.json}.rc)
echo "archive rc=$rc receipt: $ARCPT | archive dir present: $([ -d "$ARCBASE/$RID" ] && echo yes || echo no)"
echo "$(date '+%F %T') z_deliver $TAG tree=$TREE run=$RID report_rc=$RRC report_receipt=$(basename $RRCPT) archive_rc=$rc archive_dir_present=$([ -d "$ARCBASE/$RID" ] && echo yes || echo no)" >> $O/ops_ledger.txt
