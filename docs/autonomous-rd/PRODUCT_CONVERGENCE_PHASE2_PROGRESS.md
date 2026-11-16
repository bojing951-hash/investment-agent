# Product Convergence — Phase 2 进度(关键验证修复·操作者席,2026-11-16)

> 分工(章程§五): 引擎席修检查器本体(R44 A 族已落/R45 B 族队列);本席=
> 残余评估+新旧 Gate B 并行迁移框架。达标才迁,不提前替换生产 Gate B。

## 1. 残余评估(R44 后,席位侧独立复算)

- 复算件 tests/r43_realface_runner.py 本席重跑: **V1=50/V2=144/V3=89 总=283**
  与引擎报告逐位吻合(可复现性独立验过)。
- 残余族分布(引擎 R41 裁定件口径,R44 后): B 评分卡分值列 40 居首
  +D 别名/期限 38+C 前瞻路径 23+G 条件句 28+F 枚举错位 13+K 检查器误触发 16
  +H/I 其余——**全部=误报(零真错)**,即迁移门自由文本接管的可治面。
- V3 抽样亲证: top 绑定对=WTI_F `+2`(评分卡分值列=B 族)/REAL_10Y/DXY
  level 邻近碎片——与族归因一致。

## 2. 并行迁移框架(scripts/gate_b_parallel_harness.py)

- **迁移判据先固定后测量**(MC1-MC4 在源码 MIGRATION_CRITERIA+测试防漂):
  - MC1 真错零容忍(裁定档在档,本件计数对照)
  - MC2 **裁定基对比**(R44 首测修正: 裸计数不可比——旧=聚合 problems,
    新=逐 token 断言;V1 旧 18 vs 新 46 非同基,裸计数仅上下文披露)
  - MC3 连续 ≥2 期真实周报达标
  - MC4 独立席复核裁定档
- **三报首测**(canonical,快照同源映射=realface 同款):
  | 报告 | 旧 problems | 新 contra(无 prior_anchors,偏高保守) |
  |---|---|---|
  | 20261114_UNVALIDATED | 18 | 46(realface 全参=50) |
  | 20261108_UNVALIDATED | 22 | 143(realface=144) |
  | 20261024 | 17 | 89(realface=89 逐位吻合) |
- honest note: prior_anchors 未接线=新面计数保守偏高;MC1/2 评估须裁定档
  (R45 后 B 族治面更新再评)。

## 3. 下一步(Phase 2 尾→Phase 3)

- 引擎 R45(B 族)落地后: 重跑并行首测+MC1 裁定档更新→MC2/3 评估。
- Phase 3 一键研究 MVP 单入口开工(自然语言→规划→run→真 L3/L4→attach→
  验证→报告;复用 Agent Native/Skill,禁 produced 造假)。
