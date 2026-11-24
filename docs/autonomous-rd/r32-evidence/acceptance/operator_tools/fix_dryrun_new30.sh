#!/bin/zsh
# fix_dryrun_new30.sh — local dry run BEFORE any repository change (Audit-R32 Task-3 correction).
# Builds the corrected R31 NEW30 package copy in a new empty directory (rename only: the two
# verdict files get the names recorded in ARCHIVE_MANIFEST.json), proves it against the original
# archive package of the R31 work area (read-only), then runs one strict replay on the engine at
# the package's recorded run sha (ca916cd). Nothing under any repository is written.
set -u
DEV=~/investment-agent-product
SRC=$DEV/docs/autonomous-rd/r31-evidence/acceptance/session_NEW30
ORIG="/private/tmp/r31-accept/install/research_archive/20261122T145134Z_2026年11月_日本和欧元区最近六个月的通胀与政策环境有什么不同_哪些方面分化"
S=/tmp/r32-accept/scripts
ENGINE=/tmp/r32-accept/redl/engine_ca916cd
W=/tmp/r32-accept/scratch_new30fix
[ -e "$W" ] && { echo "work dir already exists: $W"; exit 2; }
mkdir -p "$W/pkg" "$W/replay"
cd "$W"

echo "=== R32 Task-3 correction dry run $(date '+%F %T') ==="
echo "[1] committed copy (HEAD $(git -C $DEV rev-parse --short=7 HEAD)) -> scratch, then rename only"
rsync -a "$SRC/" "$W/pkg/"
V=$W/pkg/verdicts
mv "$V/VERDICT-20261122T145134Z-01.json" "$V/20261123__VERDICT-20261122T145134Z-01.json"
mv "$V/VERDICT-20261122T145134Z-02.json" "$V/20261123__VERDICT-20261122T145134Z-02.json"
echo "files: committed=$(find "$SRC" -type f | wc -l | tr -d ' ') corrected=$(find "$W/pkg" -type f | wc -l | tr -d ' ') original=$(find "$ORIG" -type f | wc -l | tr -d ' ')"
echo "[2] corrected copy vs the original archive package (every original file must be byte-identical)"
same=0; diff=0; miss=0
while IFS= read -r -d '' f; do
  rel="${f#$ORIG/}"
  if [ ! -f "$W/pkg/$rel" ]; then miss=$((miss+1)); echo "  MISSING in corrected copy: $rel"
  elif cmp -s "$f" "$W/pkg/$rel"; then same=$((same+1))
  else diff=$((diff+1)); echo "  DIFFERENT: $rel"; fi
done < <(find "$ORIG" -type f -print0)
echo "original files: identical=$same different=$diff missing=$miss"
echo "[3] rename-only proof against the committed copy: every committed file is present with the same bytes"
same=0; diff=0; miss=0; renamed=0
while IFS= read -r -d '' f; do
  rel="${f#$SRC/}"
  case "$rel" in
    verdicts/VERDICT-20261122T145134Z-01.json) new="verdicts/20261123__VERDICT-20261122T145134Z-01.json"; renamed=$((renamed+1)) ;;
    verdicts/VERDICT-20261122T145134Z-02.json) new="verdicts/20261123__VERDICT-20261122T145134Z-02.json"; renamed=$((renamed+1)) ;;
    *) new="$rel" ;;
  esac
  if [ ! -f "$W/pkg/$new" ]; then miss=$((miss+1)); echo "  MISSING: $rel"
  elif cmp -s "$f" "$W/pkg/$new"; then same=$((same+1))
  else diff=$((diff+1)); echo "  DIFFERENT: $rel"; fi
done < <(find "$SRC" -type f -print0)
echo "committed files: identical=$same different=$diff missing=$miss (of which renamed=$renamed)"
echo "sha16 of the two verdict files (corrected names):"
shasum -a 256 "$V"/20261123__VERDICT-20261122T145134Z-0*.json | awk '{print "  " substr($1,1,16), $2}' | sed "s#$W/##"
echo "[4] manifest check (bound files present with the bound digest)"
python3 -I "$S/verify_manifest.py" "$W/pkg"; echo "verify_manifest rc=$?"
echo "[5] strict replay on the engine at the package's recorded run sha (ca916cd)"
cd "$W/replay"
"$ENGINE/.venv/bin/python" "$ENGINE/ia_cli.py" research-one --stage replay --package "$W/pkg" \
  --replay-out out0 > r0.json 2> r0.err; RC=$?
echo "rc=$RC"
python3 -I "$S/rsum.py" r0.json r0.err
ls out0 2>/dev/null | tr '\n' ' '; echo
echo "=== dry run end $(date '+%F %T') ==="
