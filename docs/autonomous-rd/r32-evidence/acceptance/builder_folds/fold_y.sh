#!/bin/zsh
# fold_y.sh <tag> <old_run_id> <new_run_id> — restamp the previous-stamp judgment of one work
# order to the new-stamp run id, apply the round-1 fold (fold_<tag>6.py), then dry-verify and
# token-probe the result on the new-stamp run directory.  Writes scratch_x/judgment6_<tag>.json.
# Usage: zsh fold_y.sh A 20261123T213303Z 20261123T235103Z
set -u
TAG=$1; OLD=$2; NEW=$3
S=/tmp/r32-accept/scripts; X=/tmp/r32-accept/scratch_x; O=/tmp/r32-accept/out
source /tmp/r32-accept/env6.sh
eval "RD=\$RD_$TAG"
case $TAG in C4) TREE=/tmp/r32-accept/final6-degraded;; AUG) TREE=/tmp/r32-accept/final6-aug;; *) TREE=/tmp/r32-accept/final6;; esac
P=$TREE/.venv/bin/python
NOW=$(date '+%Y-%m-%dT%H:%M:%S+08:00')
WA=()
$P -I -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); sys.exit(0 if 'written_at' in d.get('agent_declaration',{}) else 1)" $X/judgment5_$TAG.json && WA=(--written-at $NOW)
$P -I $S/restamp_judgment.py $X/judgment5_$TAG.json $X/restamp6_$TAG.json $OLD $NEW "${WA[@]}" || { echo "restamp rc=$?"; exit 3; }
R32_STAMP=36499bb $P -I $S/fold_${TAG}6.py $X/restamp6_$TAG.json $TREE "$RD" $X/judgment6_$TAG.json > $O/fold_Y_$TAG.txt 2>&1
rc=$?
echo "fold $TAG rc=$rc | $(tail -1 $O/fold_Y_$TAG.txt | cut -c1-160)"
[ $rc -eq 0 ] || { grep -n -B4 'Error' $O/fold_Y_$TAG.txt | cut -c1-240 | head -12; exit 4; }
zsh $S/dv.sh $TREE "$RD" $X/judgment6_$TAG.json > $O/dv6_$TAG.console 2>&1
echo "dv $TAG rc=$? | $(grep -v '^  V ' $O/dryverify_judgment6_$TAG.txt | cut -c1-200 | tr '\n' ' ')"
$P -I $S/tc_probe.py $TREE "$RD" $X/judgment6_$TAG.json > $O/tcprobe6_$TAG.txt 2>&1
echo "tc_probe $TAG rc=$? | clauses=$(grep -c '^ \[' $O/tcprobe6_$TAG.txt) n_b=$(grep '^==' $O/tcprobe6_$TAG.txt | sed -E 's/.*n_b ([0-9]+)/\1/' | tr '\n' ',')"
echo "$(date '+%F %T') fold Y $TAG run=$NEW tree=$TREE -> $X/judgment6_$TAG.json fold_rc=$rc" >> $O/ops_ledger.txt
