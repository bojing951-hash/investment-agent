#!/bin/sh
# F10 一条命令干净目录重放(Audit-R2 条目4)。
# 用法:  sh f10_replay.sh
# 行为:  在临时空目录内以数据切片重跑 f10_calc.py, 复算输出与
#        归档 f10_calc_output.json 逐字节比对(sha256), 打印 PASS/FAIL。
# 依赖:  python3 + shasum;零网络零模型;不触碰引擎树与 run 目录。
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
EXPECT=$(shasum -a 256 "$HERE/f10_calc_output.json" | cut -d' ' -f1)
TMP=$(mktemp -d /tmp/f10_replay.XXXXXX)
trap 'rm -rf "$TMP"' EXIT
cp "$HERE/f10_calc.py" "$TMP/"
mkdir -p "$TMP/engine/data/daily"
cp "$HERE"/data_slice/data/daily/*.json "$TMP/engine/data/daily/"
cd "$TMP"
IA_ENGINE_ROOT="$TMP/engine" python3 f10_calc.py >/dev/null
GOT=$(shasum -a 256 f10_calc_output.json | cut -d' ' -f1)
if [ "$GOT" = "$EXPECT" ]; then
  echo "F10 REPLAY PASS: $GOT (与归档输出逐字节一致)"
  exit 0
else
  echo "F10 REPLAY FAIL: got=$GOT expect=$EXPECT"
  exit 1
fi
