#!/bin/zsh
# redl_r32v.sh <commit_sha> <session_dir_name> <tag>
# Audit-R32 任务3: 从最终提交(证据提交, 纯文档)重新下载 R32 交付包(运行=执行印章 36499bb, 归档印章=cf33de3),
# 按清单原样解包, 三份引擎各验一面:
#   [1] 浅克隆 PR 分支到全新空目录(下载件=不可信数据: 只用 git archive / python -I 读), 核对 HEAD == 指定提交
#   [2] verify_manifest.py: 清单绑定件逐件 sha16(十件套/裁决链/冻结三件); pkg_blob_check.py: 包内逐件 git blob
#       哈希 == 克隆提交树 → 原样解包、源包保持原字节
#   [3] 引擎=最终提交(git archive 指定提交+venv+印章): 严格重放一次, 逐门记录
#       (预期拒: 门④ code_version_mismatch——最终提交是归档印章之后的纯文档提交, 门④比的是提交身份, 非录制代码)
#   [3b] 仅状态面等价包: 最终提交引擎 + --allow-code-mismatch(显式越过版本门=披露性重放; 最终提交相对
#       归档印章只多纯文档, 代码同归档印章=录制代码; 预期 rc=0 逐字节)
#   [4] 引擎=清单声明的录制代码, replay_real_r32.sh 六步
#       (严格面/换本地日历/独立引擎删实录/重复重放/缺冻结件拒/篡改一字节拒/manifest 单侧改写拒)
#         状态面等价包(清单 map_binding_status_equivalent=true: 地图由归档印章代码翻新审查状态短语)
#           → 归档印章引擎
#         同渲染包(无该键: 地图在执行印章渲染时裁决已在场, 交付字节全由运行印章代码所产)
#           → 运行印章引擎(归档印章代码不是录制代码)
#   [5] 另一印章引擎严格重放一次, 逐门记录
#         状态面等价包 → 执行印章引擎(预期拒: verdict_binding_threeway——执行印章代码早于状态面等价处理)
#         同渲染包     → 归档印章引擎(预期拒: 门④ code_version_mismatch——归档≠录制)
#   [5b] 仅同渲染包: 归档印章引擎 + --allow-code-mismatch(显式越过版本门=披露性重放, 非录制代码; 预期 rc=0 逐字节)
#   [6] 重放后包内逐件 blob 哈希再核对(源包未被重放改动)
# 产物在 /tmp/r32-accept/redl/<sha7>/r32v_<session>/ 下, console.log 为总回执. 引擎目录按提交共用.
set -eu
set -o pipefail
SHA="$1"; SESSION="$2"; TAG="$3"
[ "${#SHA}" -eq 40 ] || { echo "sha must be 40 hex"; exit 2; }
SHA7=$(echo "$SHA" | cut -c1-7)
ROOT=/tmp/r32-accept/redl/$SHA7
REL=docs/autonomous-rd/r32-evidence/acceptance/$SESSION
S=/tmp/r32-accept/scripts
D="$ROOT/r32v_$SESSION"
ENGINE=/tmp/r32-accept/redl/engine_$SHA7
mkdir -p "$D"
cd "$D"
echo "=== R32 从最终提交重下重放(交付包: 运行=执行印章, 归档印章翻新状态面或同渲染) $(date '+%F %T') sha=$SHA session=$SESSION ===" | tee console.log
if [ ! -d src/.git ]; then
  zsh "$S/redl_clone.sh" "$D" || exit 4
fi
HEAD=$(git -C src rev-parse HEAD)
echo "[1] downloaded HEAD=$HEAD (expect $SHA)" | tee -a console.log
[ "$HEAD" = "$SHA" ] || { echo "HEAD MISMATCH" | tee -a console.log; exit 3; }
PKG="$D/src/$REL"
[ -d "$PKG" ] || { echo "package dir missing in commit: $REL" | tee -a console.log; exit 7; }
[ -f "$PKG/ARCHIVE_MANIFEST.json" ] || { echo "not an archive package (no ARCHIVE_MANIFEST.json): $REL" | tee -a console.log; exit 7; }
echo "[2] manifest check: $PKG" | tee -a console.log
python3 -I "$S/verify_manifest.py" "$PKG" | tee -a console.log || echo "verify_manifest rc=${pipestatus[1]} (non-zero)" | tee -a console.log
RSHA=$(python3 -I "$S/manifest_head.py" "$PKG")
ASHA=$(python3 -I "$S/manifest_arch_head.py" "$PKG")
echo "manifest run_code_git_head=$RSHA archive_code_git_head=${ASHA:-(none)}" | tee -a console.log
[ "${#ASHA}" -eq 40 ] || { echo "not a two-stamp package (no archive_code_git_head) — use redl_replay.sh; stop" | tee -a console.log; exit 8; }
EQ=$(python3 -I "$S/manifest_status_eq.py" "$PKG")
if [ "$EQ" = 1 ]; then
  KIND=status-equivalent; REC=$ASHA; OTHER=$RSHA; RECLBL=archiving; OTHERLBL=run
else
  KIND=same-render; REC=$RSHA; OTHER=$ASHA; RECLBL=run; OTHERLBL=archiving
fi
echo "package kind=$KIND map_binding_status_equivalent=$EQ → recording code = $RECLBL stamp ${REC[1,7]}; the other stamp = $OTHERLBL ${OTHER[1,7]}" | tee -a console.log
echo "--- blob identity (cloned commit)" | tee -a console.log
git -C src -c core.quotepath=false ls-tree -r -z HEAD -- "$REL" > head_ls_tree.z
python3 -I "$S/pkg_blob_check.py" "$PKG" "$REL" head_ls_tree.z | tee -a console.log || echo "pkg_blob_check rc=${pipestatus[1]} (non-zero)" | tee -a console.log
git -C src fetch -q --depth 1 origin "$ASHA" 2> fetch_arch.err || { echo "fetch of the archiving stamp failed"; tail -3 fetch_arch.err | tee -a console.log; exit 9; }
git -C src fetch -q --depth 1 origin "$RSHA" 2> fetch_run.err || { echo "fetch of the run stamp failed"; tail -3 fetch_run.err | tee -a console.log; exit 9; }
echo "--- code identity of the downloaded final commit vs the archiving stamp (expected: docs only)" | tee -a console.log
git -C src -c core.quotepath=false diff --stat "$ASHA" "$SHA" | tee -a console.log | tail -4 | cut -c1-160
NODOCS=$(git -C src -c core.quotepath=false diff --name-only "$ASHA" "$SHA" | grep -v '^docs/' | wc -l | tr -d ' ')
echo "changed paths outside docs/: $NODOCS" | tee -a console.log
zsh "$S/redl_engine.sh" "$ENGINE" "$D/src" "$SHA" 2>&1 | tee -a console.log
mkdir -p replay_final_engine; cd replay_final_engine
echo "--- [3] strict replay on the final-commit engine (doors recorded)" | tee -a ../console.log
set +e
"$ENGINE/.venv/bin/python" "$ENGINE/ia_cli.py" research-one --stage replay --package "$PKG" \
  --replay-out out0 > r_final.json 2> r_final.err; RCF=$?
set -e
echo "rc=$RCF" | tee -a ../console.log
python3 -I "$S/rsum.py" r_final.json r_final.err | tee -a ../console.log || true
if [ "$EQ" = 1 ]; then
  echo "--- [3b] status-equivalent package: final-commit engine + --allow-code-mismatch (disclosed override; the final commit adds docs only on top of the archiving stamp = recording code)" | tee -a ../console.log
  set +e
  "$ENGINE/.venv/bin/python" "$ENGINE/ia_cli.py" research-one --stage replay --package "$PKG" \
    --replay-out out0_override --allow-code-mismatch > r_final_override.json 2> r_final_override.err; RCF2=$?
  set -e
  echo "rc=$RCF2" | tee -a ../console.log
  python3 -I "$S/rsum.py" r_final_override.json r_final_override.err | tee -a ../console.log || true
fi
cd "$D"
ARC=/tmp/r32-accept/redl/engine_${ASHA[1,7]}
RUN=/tmp/r32-accept/redl/engine_${RSHA[1,7]}
RECENG=/tmp/r32-accept/redl/engine_${REC[1,7]}
OTHENG=/tmp/r32-accept/redl/engine_${OTHER[1,7]}
zsh "$S/redl_engine.sh" "$RECENG" "$D/src" "$REC" 2>&1 | tee -a console.log
echo "--- [4] six steps on the recording-code engine ($RECLBL stamp $REC; work root $D/replay_recording_engine)" | tee -a console.log
zsh "$S/replay_real_r32.sh" "$PKG" "REDL32V-$TAG" "$RECENG" "$D/replay_recording_engine" 2>&1 | tee -a console.log
zsh "$S/redl_engine.sh" "$OTHENG" "$D/src" "$OTHER" 2>&1 | tee -a console.log
mkdir -p replay_other_engine; cd replay_other_engine
echo "--- [5] strict replay on the other-stamp engine ($OTHERLBL stamp $OTHER; one strict attempt; doors recorded)" | tee -a ../console.log
set +e
"$OTHENG/.venv/bin/python" "$OTHENG/ia_cli.py" research-one --stage replay --package "$PKG" \
  --replay-out out0 > r_other.json 2> r_other.err; RCO=$?
set -e
echo "rc=$RCO" | tee -a ../console.log
python3 -I "$S/rsum.py" r_other.json r_other.err | tee -a ../console.log || true
if [ "$EQ" != 1 ]; then
  echo "--- [5b] same-render package: archiving-stamp engine + --allow-code-mismatch (disclosed override, not the recording code)" | tee -a ../console.log
  set +e
  "$ARC/.venv/bin/python" "$ARC/ia_cli.py" research-one --stage replay --package "$PKG" \
    --replay-out out_override --allow-code-mismatch > r_override.json 2> r_override.err; RCV=$?
  set -e
  echo "rc=$RCV" | tee -a ../console.log
  python3 -I "$S/rsum.py" r_override.json r_override.err | tee -a ../console.log || true
  grep -n '归档代码 SHA' out_override/REPLAY_REPORT.md | cut -c1-400 | tee -a ../console.log || true
fi
cd "$D"
echo "package after replays: $(find "$PKG" -type f | wc -l | tr -d ' ') files; manifest sha256 $(shasum -a 256 "$PKG/ARCHIVE_MANIFEST.json" | cut -c1-16)" | tee -a console.log
echo "--- [6] post-replay blob identity (source package untouched by the replays)" | tee -a console.log
python3 -I "$S/pkg_blob_check.py" "$PKG" "$REL" head_ls_tree.z | tee -a console.log || echo "pkg_blob_check rc=${pipestatus[1]} (non-zero)" | tee -a console.log
echo "=== 毕 $(date '+%F %T') session=$SESSION ===" | tee -a console.log
