#!/bin/zsh
# fold_y2.sh <tag> <k> — same-stamp builder fold for one work order at stamp 36499bb, by judgment
# file number k: judgment<k-1>_<tag>.json -> fold_<tag><k>.py -> judgment<k>_<tag>.json on the work
# order's run directory (no restamp: the input was written against this run id), then dry-verify and
# clause-probe the result.  Follow-up rounds of fold_y.sh (which produces judgment6_<tag>.json).
# Usage: zsh fold_y2.sh B 7
set -u
TAG=$1; N=$2            # N = output judgment file number (review round that produced it = N-5)
S=/tmp/r32-accept/scripts; X=/tmp/r32-accept/scratch_x; O=/tmp/r32-accept/out
source /tmp/r32-accept/env6.sh
eval "RD=\$RD_$TAG"
case $TAG in C4) TREE=/tmp/r32-accept/final6-degraded;; AUG) TREE=/tmp/r32-accept/final6-aug;; *) TREE=/tmp/r32-accept/final6;; esac
P=$TREE/.venv/bin/python
JIN=$X/judgment$((N-1))_$TAG.json; JOUT=$X/judgment${N}_$TAG.json
[ -f "$JIN" ] || { echo "missing input $JIN"; exit 2; }
[ -e "$JOUT" ] && { echo "output exists: $JOUT (not overwritten)"; exit 2; }
R32_STAMP=36499bb $P -I $S/fold_${TAG}${N}.py $JIN $TREE "$RD" $JOUT > $O/fold_Y_${TAG}_j${N}.txt 2>&1
rc=$?
echo "fold $TAG j$N rc=$rc | $(tail -1 $O/fold_Y_${TAG}_j${N}.txt | cut -c1-160)"
[ $rc -eq 0 ] || { grep -n -B6 'Error' $O/fold_Y_${TAG}_j${N}.txt | cut -c1-260 | tail -14; exit 4; }
zsh $S/dv.sh $TREE "$RD" $JOUT > $O/dvj${N}_$TAG.console 2>&1
echo "dv $TAG j$N $(tail -1 $O/dvj${N}_$TAG.console | cut -c1-200)"
grep -v '^  V ' $O/dryverify_judgment${N}_$TAG.txt | cut -c1-220 | head -20
$P -I $S/tc_probe.py $TREE "$RD" $JOUT > $O/tcprobej${N}_$TAG.txt 2>&1
echo "tc_probe $TAG j$N rc=$? | n_b=$(grep '^==' $O/tcprobej${N}_$TAG.txt | sed -E 's/.*n_b ([0-9]+)/\1/' | tr '\n' ',')"
grep '^==' $O/tcprobej${N}_$TAG.txt | cut -c1-120
echo "$(date '+%F %T') fold Y $TAG judgment_no=$N tree=$TREE -> $JOUT fold_rc=$rc" >> $O/ops_ledger.txt
