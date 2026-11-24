#!/bin/zsh
# build_final9.sh <sha> <base|degraded|aug|entry>
# (from build_final8.sh, at the final stamp V after the third delivery-chain fix: replay gate 4 accepts
#  the archiving code for every re-delivery package whose manifest declares archive_code_git_head — also
#  when the map was rendered with the verdict already bound (same-render two-stamp package, no
#  map_binding_status_equivalent key); no rendering change. The Y (36499bb) run directories and verdict
#  records are carried in byte-identical by scripts/carry_yz.py; report/archive/replays are re-run here.)
# Acceptance trees at the consolidated-fix SHA (argument; must be a pushed
# commit of dev/audit-fix-r1). Clean install strictly per the user doc
# (README), same as build_final4.sh: git archive → python3 -m venv .venv →
# pip install -r requirements.txt → CODE_VERSION stamp → env_config.py
# (LIVE read-only copy; values never echoed) → install_skill.py --target project.
#   base     = + frozen evidence base copied additively from final3/data/ (the
#              daily faces and research_snapshot_20261123.json produced by the
#              standard update entry truly run at 19638e1: ia_cli update --yes,
#              15/15 steps, 2026-11-23T14:37:34Z..14:53:49Z). The consolidated
#              fix changes the reader report / point-anchor labels / policy
#              window net change only (no collection / snapshot / config /
#              committed-data change) — the five work orders keep the same
#              frozen snapshot (research_as_of 2026-11-23T22:53:47+08:00).
#   degraded = base minus the ea_20261123 face (final3-degraded/data; snapshot
#              rebuilt in-tree there at 19638e1).
#   aug      = + repo-committed research_snapshot_20261121.json (R30 A3 face).
#   entry    = clean install only; the standard update entry is run here at
#              the final SHA (ux.sh <tree> <tag>).
set -eu
SHA="$1"; KIND="$2"
case "$KIND" in
  base) DEST=/tmp/r32-accept/final9 ;;
  degraded) DEST=/tmp/r32-accept/final9-degraded ;;
  aug) DEST=/tmp/r32-accept/final9-aug ;;
  entry) DEST=/tmp/r32-accept/final9-entry ;;
  *) echo "usage: build_final9.sh <sha> <base|degraded|aug|entry>"; exit 2 ;;
esac
[ "$#SHA" -ne 40 ] && { echo "sha must be 40 hex"; exit 2; }
REPO=~/investment-agent-product
LIVE="~/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent"
F3=/tmp/r32-accept/final3
OUT=/tmp/r32-accept/out
[ -e "$DEST" ] && { echo "dest exists: $DEST"; exit 2; }
mkdir -p "$DEST"
echo "=== build $KIND tree @ $SHA  dest=$DEST  $(date '+%F %T %z')"
( cd "$REPO" && git -C "$REPO" cat-file -e "$SHA^{commit}" && git archive "$SHA" ) | tar -x -C "$DEST"
python3 - "$DEST" "$SHA" <<'PY'
import datetime, json, sys
dest, sha = sys.argv[1:3]
json.dump({'git_head': sha, 'git_diff_sha256': None,
           'stamped_at': datetime.datetime.now().astimezone().isoformat(
               timespec='seconds')},
          open(dest + '/CODE_VERSION.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
PY
cd "$DEST"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt > "$OUT/final9_${KIND}_pip.log" 2>&1 || { echo "pip rc=$?"; tail -5 "$OUT/final9_${KIND}_pip.log"; }
echo "pip rc=0"
cp "$LIVE/env_config.py" "$DEST/env_config.py"
.venv/bin/python install_skill.py --target project \
    > "$OUT/final9_${KIND}_skill_install.json" 2> "$OUT/final9_${KIND}_skill_install.err" || true
.venv/bin/python -c "import env_config as e; c=e.model_runtime_config(); print('模型API(三参配齐):', c['complete'], '| FRED:', bool(e.FRED_API_KEY), '| TUSHARE:', bool(e.TUSHARE_TOKEN))"
if [ "$KIND" = base ]; then
  # additive copy of the collected evidence base (no --delete: archive files stay)
  rsync -a "$F3/data/" "$DEST/data/"
  echo "snapshot(=final3) sha256=$(shasum -a 256 data/daily/research_snapshot_20261123.json | cut -c1-64)"
  echo "final3 snapshot    sha256=$(shasum -a 256 $F3/data/daily/research_snapshot_20261123.json | cut -c1-64)"
  echo "data files: final3=$(find "$F3/data" -type f | wc -l | tr -d ' ') tree=$(find data -type f | wc -l | tr -d ' ')"
fi
if [ "$KIND" = degraded ]; then
  rm -rf "$DEST/data"
  cp -a /tmp/r32-accept/final3-degraded/data "$DEST/data"
  diff -rq /tmp/r32-accept/final3-degraded/data "$DEST/data" && echo "degraded data == final3-degraded/data"
  .venv/bin/python - <<'PY'
import json
d = json.load(open('data/daily/research_snapshot_20261123.json'))
ss = d.get('series_store') or {}
pol = sorted(m for m, v in ss.items() if m.startswith(('EA_', 'ECB_'))
             and (v or {}).get('dates'))
print('snapshot research_snapshot_20261123 | series n=%d | research_as_of %s | EA series with data: %d %s'
      % (len(ss), d.get('research_as_of'), len(pol), pol))
PY
fi
if [ "$KIND" = aug ]; then
  SNAP="docs/autonomous-rd/r30-evidence/acceptance/session_A3_formal/root_overlay/data/daily/research_snapshot_20261121.json"
  cp "$SNAP" data/daily/research_snapshot_20261121.json
  .venv/bin/python - <<'PY'
import hashlib, json
b = open('data/daily/research_snapshot_20261121.json', 'rb').read()
d = json.loads(b)
print('snapshot research_snapshot_20261121 | n_series=%d | research_as_of %s | sha256=%s'
      % (len(d.get('series_store') or {}), d.get('research_as_of'),
         hashlib.sha256(b).hexdigest()[:16]))
PY
  echo "question_aug sha256=$(shasum -a 256 docs/autonomous-rd/r32-evidence/acceptance/questions/question_aug.txt | cut -c1-64)"
  # + the collected macro daily face (macro_20261123.json, standard update entry at
  # 19638e1 = final3/data/daily; byte-identical copy): the S4 history step for TIPS_10Y
  # reads the engine-local macro daily face, absent in a snapshot-only tree (same
  # preparation as final4-aug; the evidence gate still admits only <= cutoff rows)
  cp -p /tmp/r32-accept/final3/data/daily/macro_20261123.json data/daily/macro_20261123.json
  echo "macro face sha256=$(shasum -a 256 data/daily/macro_20261123.json | cut -c1-64)"
fi
echo "=== $KIND tree ready: $(find "$DEST" -type f -not -path "$DEST/.venv/*" | wc -l | tr -d ' ') files (excl. .venv); .env present? $([ -e "$DEST/.env" ] && echo yes || echo no); CODE_VERSION git_head=$(python3 -c "import json; print(json.load(open('$DEST/CODE_VERSION.json'))['git_head'])")"
