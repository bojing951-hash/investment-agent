#!/bin/sh
# BLIND 一条命令干净目录重放(Audit-R4 R4-03 同版重放证据包)。
# 用法:  sh blind_replay.sh
# 行为:  临时空目录内只以本包 data_slice/(原始输入切片)重跑——
#          (1) blind_calc.py      → stdout 与冻结 blind_calc_output.txt 逐字节比对
#          (2) blind_calc2.py     → stdout 与冻结 blind_calc2_output.txt 逐字节比对
#          (3) blind_independent_recompute.py(独立实现) → 64 项正文靶值复算
# 依赖:  python3 + shasum;零网络零模型;不触碰引擎树与 run 目录。
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
TMP=$(mktemp -d /tmp/blind_replay.XXXXXX)
trap 'rm -rf "$TMP"' EXIT
cp "$HERE/blind_calc.py" "$HERE/blind_calc2.py" "$HERE/blind_independent_recompute.py" "$TMP/"
mkdir -p "$TMP/data_slice/data/daily"
cp "$HERE"/data_slice/data/daily/*.json "$TMP/data_slice/data/daily/"
cd "$TMP"

# 输入哈希核验(切片被改动即 FAIL)
cat > /tmp/blind_slice_expect.sha256 <<'EOF'
aaf7b429891036a7f01c7f3843f18904c5b430e18e3d3fc5230d7d06c35b84d8  data_slice/data/daily/macro_20261112.json
4e5e504ac300f6bb689b4f1b014735e62d4ead9440ff4ce5e354c301fb2abfa4  data_slice/data/daily/research_snapshot_20261112_v2.json
EOF
shasum -a 256 -c /tmp/blind_slice_expect.sha256

export IA_ENGINE_DAILY="$TMP/data_slice/data/daily"
python3 blind_calc.py        > blind_calc_replay.txt
python3 blind_calc2.py       > blind_calc2_replay.txt
if ! cmp -s blind_calc_replay.txt  "$HERE/blind_calc_output.txt";  then echo "BLIND REPLAY FAIL: blind_calc.py 输出与冻结件不一致"; exit 1; fi
if ! cmp -s blind_calc2_replay.txt "$HERE/blind_calc2_output.txt"; then echo "BLIND REPLAY FAIL: blind_calc2.py 输出与冻结件不一致"; exit 1; fi
python3 blind_independent_recompute.py

SIG=$(cat "$HERE/blind_calc_output.txt" "$HERE/blind_calc2_output.txt" | shasum -a 256 | cut -d' ' -f1)
echo "BLIND REPLAY PASS: 冻结输出拼接 sha256=$SIG (切片重放逐字节一致 + 独立复算全中)"
