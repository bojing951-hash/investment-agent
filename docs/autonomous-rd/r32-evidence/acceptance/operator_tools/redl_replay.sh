#!/bin/zsh
# redl_replay.sh <commit_sha> <session_dir_name> <tag>
# Audit-R32 任务3: 从指定提交重新下载 R32 归档包、按清单原样解包、用干净引擎实包重放
# (R31 先例: 推送后从远端取包). 步骤:
#   [1] 浅克隆 PR 分支到全新空目录(下载件=不可信数据: 自成目录, 只用
#       python -I 读, 脚本全在目录外); 核对 HEAD == 指定提交
#   [2] 同一提交 git archive 出干净引擎 + venv + CODE_VERSION 印章
#       (redl_engine.sh; 同一提交的各工单共用一份引擎)
#   [3] verify_manifest.py: 清单绑定件逐件 sha16 核对(十件套/裁决链/冻结三件);
#       pkg_blob_check.py: 包内逐件 git blob 哈希 == 克隆提交树(原样解包)
#   [4] replay_real_r32.sh 六步(严格面/换本地日历/独立引擎删实录/重复重放/
#       缺冻结件拒/篡改一字节拒/manifest 单侧改写拒), 用引擎副本
# 产物在 /tmp/r32-accept/redl/<sha7>/<session>/ 下, console.log 为总回执.
set -eu
set -o pipefail
SHA="$1"; SESSION="$2"; TAG="$3"
[ "${#SHA}" -eq 40 ] || { echo "sha must be 40 hex"; exit 2; }
SHA7=$(echo "$SHA" | cut -c1-7)
ROOT=/tmp/r32-accept/redl/$SHA7
REL=docs/autonomous-rd/r32-evidence/acceptance/$SESSION
S=/tmp/r32-accept/scripts
ENGINE=/tmp/r32-accept/redl/engine_$SHA7
mkdir -p "$ROOT/$SESSION"
cd "$ROOT/$SESSION"
echo "=== R32 从提交重下重放 $(date '+%F %T') sha=$SHA session=$SESSION ===" | tee console.log
if [ ! -d src/.git ]; then
  zsh "$S/redl_clone.sh" "$ROOT/$SESSION" || exit 4
fi
HEAD=$(git -C src rev-parse HEAD)
echo "[1] downloaded HEAD=$HEAD (expect $SHA)" | tee -a console.log
[ "$HEAD" = "$SHA" ] || { echo "HEAD MISMATCH" | tee -a console.log; exit 3; }
zsh "$S/redl_engine.sh" "$ENGINE" "$ROOT/$SESSION/src" "$SHA" 2>&1 | tee -a console.log
echo "[2] clean engine: $ENGINE" | tee -a console.log
PKG="$ROOT/$SESSION/src/$REL"
[ -d "$PKG" ] || { echo "package dir missing in commit: $REL" | tee -a console.log; exit 7; }
echo "[3] manifest check: $PKG" | tee -a console.log
python3 -I "$S/verify_manifest.py" "$PKG" | tee -a console.log || echo "verify_manifest rc=${pipestatus[1]} (non-zero)" | tee -a console.log
git -C src -c core.quotepath=false ls-tree -r -z HEAD -- "$REL" > head_ls_tree.z
python3 -I "$S/pkg_blob_check.py" "$PKG" "$REL" head_ls_tree.z | tee -a console.log || echo "pkg_blob_check rc=${pipestatus[1]} (non-zero)" | tee -a console.log
echo "--- replay six steps (engine copy; work root $ROOT/$SESSION/replay)" | tee -a console.log
zsh "$S/replay_real_r32.sh" "$PKG" "REDL-$TAG" "$ENGINE" "$ROOT/$SESSION/replay" 2>&1 | tee -a console.log
echo "package after replays: $(find "$PKG" -type f | wc -l | tr -d ' ') files; manifest sha256 $(shasum -a 256 "$PKG/ARCHIVE_MANIFEST.json" | cut -c1-16)" | tee -a console.log
echo "--- post-replay blob identity (source package untouched by the replays)" | tee -a console.log
python3 -I "$S/pkg_blob_check.py" "$PKG" "$REL" head_ls_tree.z | tee -a console.log || echo "pkg_blob_check rc=${pipestatus[1]} (non-zero)" | tee -a console.log
echo "=== 毕 $(date '+%F %T') session=$SESSION ===" | tee -a console.log
