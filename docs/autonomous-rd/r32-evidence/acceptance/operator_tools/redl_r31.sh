#!/bin/zsh
# redl_r31.sh <commit_sha> <session_dir_name> <tag>
# Audit-R32 任务3: 从指定提交重新下载 R31 入库包(session_A4_formal /
# session_B2_formal / session_NEW30), 按清单原样解包:
#   [1] 浅克隆 PR 分支到全新空目录(下载件=不可信数据), 核对 HEAD == 指定提交
#   [2] verify_manifest.py: 清单绑定件逐件 sha16 (十件套/裁决链/冻结三件)
#   [3] pkg_blob_check.py: 包内逐件 git blob 哈希 == 克隆提交树 == 审计基线
#       72dab1c 树(两份清单都从远端按提交取) → 源包保持原字节
#   [4] 最终引擎(git archive 指定提交+venv+印章)严格重放一次: 逐门记录
#       (R31 包绑定运行 SHA=ca916cd → 预期门④ code_version_mismatch;
#        NEW30 → 预期门① 裁决链缺档拒)
#   [5] 引擎=包记录运行版本(git archive manifest.run_code_git_head+印章, R31 D2
#       同法): A4/B2 六步重放(replay_real_r32.sh); NEW30 只做严格重放一次
# 产物在 /tmp/r32-accept/redl/<sha7>/r31_<session>/ 下, console.log 为总回执.
# 引擎目录按提交共用: /tmp/r32-accept/redl/engine_<sha7>.
set -eu
set -o pipefail
SHA="$1"; SESSION="$2"; TAG="$3"
[ "${#SHA}" -eq 40 ] || { echo "sha must be 40 hex"; exit 2; }
BASE=72dab1c0bc4a050613ba5ca3ca57051ae8475484
SHA7=$(echo "$SHA" | cut -c1-7)
ROOT=/tmp/r32-accept/redl/$SHA7
REL=docs/autonomous-rd/r31-evidence/acceptance/$SESSION
S=/tmp/r32-accept/scripts
D="$ROOT/r31_$SESSION"
ENGINE=/tmp/r32-accept/redl/engine_$SHA7
mkdir -p "$D"
cd "$D"
echo "=== R32 从提交重下 R31 入库包重放 $(date '+%F %T') sha=$SHA session=$SESSION ===" | tee console.log
if [ ! -d src/.git ]; then
  zsh "$S/redl_clone.sh" "$D" || exit 4
fi
HEAD=$(git -C src rev-parse HEAD)
echo "[1] downloaded HEAD=$HEAD (expect $SHA)" | tee -a console.log
[ "$HEAD" = "$SHA" ] || { echo "HEAD MISMATCH" | tee -a console.log; exit 3; }
PKG="$D/src/$REL"
[ -d "$PKG" ] || { echo "package dir missing in commit: $REL" | tee -a console.log; exit 7; }
[ -f "$PKG/ARCHIVE_MANIFEST.json" ] || { echo "not an archive package (no ARCHIVE_MANIFEST.json): $REL — not replayable" | tee -a console.log; exit 7; }
echo "[2] manifest check: $PKG" | tee -a console.log
python3 -I "$S/verify_manifest.py" "$PKG" | tee -a console.log || echo "verify_manifest rc=${pipestatus[1]} (non-zero)" | tee -a console.log
RSHA=$(python3 -I "$S/manifest_head.py" "$PKG")
echo "manifest run_code_git_head=$RSHA" | tee -a console.log
echo "[3] blob identity (cloned commit; audit baseline 72dab1c)" | tee -a console.log
git -C src -c core.quotepath=false ls-tree -r -z HEAD -- "$REL" > head_ls_tree.z
git -C src fetch -q --depth 1 origin "$BASE" 2> fetch_base.err || { echo "baseline fetch failed"; tail -3 fetch_base.err | tee -a console.log; }
git -C src -c core.quotepath=false ls-tree -r -z "$BASE" -- "$REL" > base_ls_tree.z
python3 -I "$S/pkg_blob_check.py" "$PKG" "$REL" head_ls_tree.z base_ls_tree.z | tee -a console.log || echo "pkg_blob_check rc=${pipestatus[1]} (non-zero)" | tee -a console.log
zsh "$S/redl_engine.sh" "$ENGINE" "$D/src" "$SHA" 2>&1 | tee -a console.log
mkdir -p replay_final_engine; cd replay_final_engine
echo "--- [4] strict replay on the final-commit engine (record doors)" | tee -a ../console.log
set +e
"$ENGINE/.venv/bin/python" "$ENGINE/ia_cli.py" research-one --stage replay --package "$PKG" \
  --replay-out out0 > r_final.json 2> r_final.err; RCF=$?
set -e
echo "rc=$RCF" | tee -a ../console.log
python3 -I "$S/rsum.py" r_final.json r_final.err | tee -a ../console.log || true
cd "$D"
[ "${#RSHA}" -eq 40 ] || { echo "manifest has no 40-hex run_code_git_head — stop before [5]" | tee -a console.log; exit 8; }
git -C src fetch -q --depth 1 origin "$RSHA" 2> fetch_runsha.err || { echo "fetch of run sha failed"; tail -3 fetch_runsha.err | tee -a console.log; exit 9; }
OLD=/tmp/r32-accept/redl/engine_${RSHA:0:7}
zsh "$S/redl_engine.sh" "$OLD" "$D/src" "$RSHA" 2>&1 | tee -a console.log
if [ "$SESSION" = "session_NEW30" ]; then
  mkdir -p replay_runsha_engine; cd replay_runsha_engine
  echo "--- [5] strict replay on the engine at the package's recorded run sha (NEW30: one strict attempt)" | tee -a ../console.log
  set +e
  "$OLD/.venv/bin/python" "$OLD/ia_cli.py" research-one --stage replay --package "$PKG" \
    --replay-out out0 > r_old.json 2> r_old.err; RCO=$?
  set -e
  echo "rc=$RCO" | tee -a ../console.log
  python3 -I "$S/rsum.py" r_old.json r_old.err | tee -a ../console.log || true
  cd "$D"
else
  echo "--- [5] six steps on the engine at the package's recorded run sha $RSHA (work root $D/replay_runsha_engine)" | tee -a console.log
  zsh "$S/replay_real_r32.sh" "$PKG" "REDL31-$TAG" "$OLD" "$D/replay_runsha_engine" 2>&1 | tee -a console.log
fi
echo "package after replays: $(find "$PKG" -type f | wc -l | tr -d ' ') files; manifest sha256 $(shasum -a 256 "$PKG/ARCHIVE_MANIFEST.json" | cut -c1-16)" | tee -a console.log
echo "--- post-replay blob identity (source package untouched by the replays)" | tee -a console.log
python3 -I "$S/pkg_blob_check.py" "$PKG" "$REL" head_ls_tree.z base_ls_tree.z | tee -a console.log || echo "pkg_blob_check rc=${pipestatus[1]} (non-zero)" | tee -a console.log
echo "=== 毕 $(date '+%F %T') session=$SESSION ===" | tee -a console.log
