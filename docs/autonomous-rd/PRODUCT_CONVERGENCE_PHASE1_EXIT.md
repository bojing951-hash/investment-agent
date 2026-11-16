# Product Convergence — Phase 1 出口审计(2026-11-16)

> 席位: 操作者。基线: dev/product-convergence-mvp @953c9ff(含 main@3550ca3 并入)。
> 判据来源: 章程§五 Phase 1「工程硬约束落地」+§四 四项。

## 1. 交付物对照(章程§四 → 实况)

| 章程要求 | 交付物 | 验证 |
|---|---|---|
| §四.1 目标完整性检查(G0) | target_integrity_guard.py 四件哈希登记+CI 校验路径 | test_target_integrity 13/0(§A 基线/§B 行为证伪/§C 同步/§D 防掏空);guard --check 绿 |
| §四.2 Git/CI 保护准备 | TARGET_PROTECTION_PREP.md(三步清单+可复制 Ruleset 值+行为预告) | 外部权限项如实标「待用户」;不冒称已保护 |
| §四.3 验收隔离四层 | product_acceptance_runner.py(L3)+REGRESSION_CATALOG(L2 锚表)+既有 L1 | runner VERDICT 诚实边界:L3 不冒认研究质量 |
| §四.4 复杂度增长控制 | complexity_baseline.py+COMPLEXITY_BASELINE.md+BACKLOG(S-1~5 DEFERRED) | --check ±5% 门绿;本轮零瘦身执行 |
| Phase 1 守卫总面 | tests/test_pc_phase1_hardening.py 13/0 | 资产/门/纪律三节 |

## 2. 基线事实(并入 main@3550ca3 后)

- R44 已落地: 引擎 A 族硬化(真实周报误报 326→283)+口径判据修正
  (pytest 逐件绿=rc∈{0,5} 或 rc=3 伴 SystemExit:0)+test_round6 X6 追修。
- main CI=43805774407 绿;净克隆双口径 167/0+167/0。
- 复杂度基线: 生产 89f/51038L,测试 178f/80094L。

## 3. 出口判据自检

「工程硬约束落地」——**满足**: ①目标契约未授权变更→红(行为证伪过);
②保护配置=唯一用户清单在手;③验收四层隔离入口在位;④增长控制门绿+
简化只登记。**可进 Phase 2**。

## 4. Phase 2 开工面(关键验证修复)

- 依赖已就绪: 引擎 R44 落地(283 残余,B 族 40 居首=引擎席 R45)。
- 本席分工(章程§五 Phase 2): 残余评估(283 的族分布复算+可治面排序)
  +**新旧 Gate B 并行迁移框架**(并行 runner+迁移判据固定,达标才迁,
  不提前替换生产 Gate B)。
- 边界: 引擎席修检查器本体(R45 B 族),本席不重复修,只建框架与评估。
