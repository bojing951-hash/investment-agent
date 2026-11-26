#!/bin/zsh
# redl_engine.sh <engine_dir> <src_clone_dir> <sha>
# Build (once per sha) a clean engine for re-download replays: git archive <sha>
# from the downloaded clone → python3 -m venv .venv → pip install -r
# requirements.txt → CODE_VERSION.json stamp (same stamp the acceptance trees
# carry). Idempotent: an engine already built for the same sha is reused
# (marker <engine_dir>.redl_sha sits outside the code tree).
# The clone is downloaded (untrusted) data: only `git archive` reads it.
set -eu
E="$1"; SRC="$2"; SHA="$3"
[ "${#SHA}" -eq 40 ] || { echo "sha must be 40 hex"; exit 2; }
if [ -x "$E/.venv/bin/python" ] && [ -f "$E.redl_sha" ] && [ "$(cat "$E.redl_sha")" = "$SHA" ]; then
  echo "engine reused: $E (git archive $SHA)"; exit 0
fi
if [ -e "$E" ]; then
  echo "incomplete engine dir present: $E (no venv or other sha) — inspect by hand"; exit 6
fi
mkdir -p "$E"
git -C "$SRC" cat-file -e "$SHA^{commit}"
git -C "$SRC" archive "$SHA" | tar -x -C "$E"
python3 - "$E" "$SHA" <<'PY'
import datetime, json, sys
dest, sha = sys.argv[1:3]
json.dump({'git_head': sha, 'git_diff_sha256': None,
           'stamped_at': datetime.datetime.now().astimezone().isoformat(timespec='seconds')},
          open(dest + '/CODE_VERSION.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
PY
( cd "$E" && python3 -m venv .venv && .venv/bin/pip install -q -r requirements.txt ) > "$E.redl_pip.log" 2>&1 \
  || { echo "engine pip failed"; tail -3 "$E.redl_pip.log"; exit 5; }
echo "$SHA" > "$E.redl_sha"
echo "engine built: $E (git archive $SHA; .env present? $([ -e "$E/.env" ] && echo yes || echo no); env_config present? $([ -e "$E/env_config.py" ] && echo yes || echo no))"
