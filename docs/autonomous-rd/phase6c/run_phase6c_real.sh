#!/bin/bash
# 阶段六 C-real 真实一键研究验收 — 用户终端亲跑件(权限分类器拦操作者侧执行;
# 与 LIVE 部署脚本同批处理模式: /tmp/deploy_v0230_live.py 先例)。
# 问题=WALCL×SOFR×DXY 组合状态: 判定层研究面从未在此组合上优化/验收过
# (R24 面=HY_OAS×SPX×VIX×CURVE_2S10S;R7 只验过 SOFR/WALCL 数据通道)。
set -u
cd "$HOME/investment-agent-dev" || exit 1
echo "== 前置检查: 无头锁(引擎轮次进行中则先等它结束) =="
if [ -e "$HOME/agent-loop/headless/lock" ]; then
  echo "引擎轮次在跑(lock 在场)——稍后再试"; exit 1
fi
echo "== 真实一键研究(确定性链,零模型;L3/L4 恒 declared-not-produced) =="
python3 ia_cli.py research-run \
  --question "美元流动性与短端利率: WALCL 缩表进程、SOFR 走势与 DXY 的组合状态研究"
RC=$?
echo "rc=$RC"
echo "== 验收判据(逐条对照 docs/autonomous-rd/phase6c/PHASE6C-REAL-ACCEPTANCE.md) =="
echo "完成后把输出目录名(形如 20261115T****_美元流动性*)回填给操作者会话即可,"
echo "操作者跑 tests/test_arch_reform_phase6.py 的 C-real 核验段(结构/数值/零未映射)。"
exit $RC
