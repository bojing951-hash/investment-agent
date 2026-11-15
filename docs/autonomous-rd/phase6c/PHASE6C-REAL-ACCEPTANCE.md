# 阶段六 C-real 真实一键研究验收判据(WALCL×SOFR×DXY,未优化面)

> 背景: 操作者会话尝试亲跑被权限分类器拦(Real-World Transactions 类,
> 与 LIVE 部署同模式)→ 按既有先例转为用户终端亲跑件 /tmp/run_phase6c_real.sh。
> 本档=验收判据(章程§八 C: 数据→机构观点→历史研究→经济机制→竞争性
> 解释→条件推演→完整报告;不能以离线测试代替真实验收)。

## 面选择理由(未优化证明)

- R24 真实验收面 = HY_OAS×SPX×VIX×CURVE_2S10S(信用/波动/股指/曲线);
- R7 只验证过 SOFR/WALCL 的**数据通道**(真实拉取+排序披露),从未在该
  组合上做过研究链/判定层验收;
- DXY 周报面常在,但「缩表×短端利率×美元」三元组合状态研究从未运行。

## 验收判据(真跑后逐条对照)

1. **run_ok=True 且步骤完整**: report.json run_ok=true,步骤含
   数据快照/Gate A/机构观点/历史研究/analog/证据索引(L3/L4 在 attach 前
   恒 declared-not-produced——这是纪律不是缺陷)。
2. **三元指标真实在场**: WALCL/SOFR/DXY 各自有 fact(value/unit/
   observation_date),WALCL 为周频(滞后如实注记),SOFR 日频。
3. **数值一致性**: 面内恒等/变化率由 judgment_contract 复算全绿
   (操作者侧跑 verify_judgment;或 tc.check_text 抽验三指标水平+周变)。
4. **零未映射**: 报告正文数值 token 对面未映射=0(migration 跑台同口径)。
5. **缺口如实**: 若 SOFR/WALCL 源端更新滞后于研究日,Gate A/缺口台账
   如实注记(不编数)。
6. **判定层(可选,须真模型)**: 若用户授权 agent 判定(L3/L4 attach),
   产物过 judgment_contract 契约验证(阶段四门)——未授权则
   declared-not-produced 即为诚实终态。

## 完成后动作

把运行目录名告诉操作者会话(或直接说「C-real 跑完了」),操作者:
- 将目录登入 PHASE3-LOG 阶段六节;
- tests/test_arch_reform_phase6.py 的 C4-real 项解除 PENDING 并把
  C-real 核验段指向新运行目录。
