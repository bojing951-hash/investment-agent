# Product Convergence — Phase 3 进度(一键研究 MVP 单入口,2026-11-16)

> 席位: 操作者。分支: dev/product-convergence-mvp(未并 main,待用户外审)。
> 章程对应: Phase 3「自然语言→规划→research-run→Agent L3/L4 真生成→
> research-attach→验证→完整报告」;红线: L3/L4 必须真 produced,禁改字段造假。

## 1. 交付物

- **ia_cli.py `research-one` 三段式单入口**(e56fe91+e8d4a94+本波修正):
  - `--stage plan`: run_research 真跑(零模型编排)+AGENT_SEAT_ENVELOPE 工单
    +evidence_index.json 独立落盘+views_digest.json(L2 富内容确定性摘编,
    零生成——report.json L2 只含 VP sidecar 验证标签,机构原文在 views 库,
    字段选取入 run 目录)
  - `--stage attach`: agent_judgment.attach_judgment 纪律校验+合并
    (**produced 唯一写者**;MINOR-4 失败底座拒收;契约验证 CONTRADICTED 拒落位)
  - `--stage report`: FULL_REPORT.md 真汇编(L1 事实表+L2 摘编清单+L3/L4
    produced 面与归档指针;渲染纪律=只汇编在场事实不新增生成)
  - `--engine-root` 注入缝: research_orchestrator RUN_ROOT 全局——子进程
    cwd 与 ia_cli 路径不再钉死模块 ROOT,净代码树可跑真实数据树
- **守卫 tests/test_pc_phase3_research_one.py 22/0**(§A 入口参数面/§B 净树
  诚实链: 工件齐+无效输入永不半落位+ok 与 produced 同步)

## 2. 真链实证(mvp_run4,2026-11-16)

- 问题: UST_10Y 十年期美债利率上行的宏观传导: 对 HY_OAS 高收益债利差与
  SPX 股市估值的影响
- **plan**(engine_root=引擎树,含 views 库 17 份): run_ok=True,L1=3 行
  (SPX 7609.63/HY_OAS 3.34pp/UST_10Y 4.88%),evidence=64 行(47 事实+17 VP)
- **Agent 席真产**(独立 subagent,54 工具调用/20 分钟): judgment_mvp.json
  schema 1.1,attribution=ai_inferred——L3 矛盾 3 条(各 ≥2 竞争解释全锚定)
  +机制链 2 条(E1→E2→E3,假设环明写)+L4 情景 2 条(基准+反例,证伪阈值
  含基准值与日期,SCN-B 用 v1.1 secondary_metric_ids 复合证伪);自检
  validate_judgment passed=True 零违规+verify_judgment VERIFIED(23 checks)
  ——attach 前自修三处会被契约拦截的措辞+按 R34 判例改回证据锚定区间
- **attach**: attached=True,validation_passed=True,violations=[];
  report.md 重渲含 L3/L4 节(produced=True)
- **report**: ok=True,**L3_produced=True ∧ L4_produced=True**(G2 链全绿),
  FULL_REPORT.md 8 工件齐(report.json/report.md/FULL_REPORT.md/evidence_index/
  views_digest/AGENT_SEAT_ENVELOPE/judgment_mvp/agent_judgment 归档副本)

## 3. 本波发现与修复(全在 dev 分支)

| 发现 | 修复 |
|---|---|
| 净树 plan run_ok=False(无本地快照=untracked 数据) | 非缺陷:诚实降级 no_snapshot 如实报错;守卫 §B3 锁 MINOR-4 拒收路径 |
| report.json L2 只含 sidecar 标签,Agent 席拿不到机构原文 | views_digest.json 确定性摘编入 run 目录+工单 read_first |
| FULL_REPORT 问题行 None(question 在 run 子 dict) | 修正取键+守卫 §B4 锁非空 |
| attach blocked 路径不回传 blocked 键 | emit 增 blocked(守卫 §B3 揭示) |
| 工单 skill 路径 .claude/skills 不存在 | 修正 .agents/skills(实存) |

## 4. 已知边界(如实,不冒称)

- **问题短语需含指标 ID**: 零模型规划器只做词法命中(设计边界,非缺陷)——
  纯中文自然语言问题 L1 命中 0 行;Phase 4 任务将以纯中文问题探边界并如实记录
- VP sidecar 17 份全 INSUFFICIENT_EVIDENCE=库龄函数(首验窗 2026-12),
  Agent 席已在档标注;SCN-B 触发前提(UBS 加息路径)本身=未到期不可验预测
- 真链证据(mvp_run4)在 /tmp——**run 目录须归档**: 已按 S11 默认关(用户
  认可后 --archive);本波实证要点已在档,工件如需长存由 Phase 4 正式任务
  重新产出(正式任务用 --archive)

## 5. Phase 3 出口自检 → Phase 4

「单入口建成+真链全绿(一次输入→数据+观点+L3/L4+完整报告)」——**满足**
(G2 语义在净代码树+真实数据注入缝下达成;守卫锁结构面与诚实降级面)。
Phase 4: 三真实任务(A 美宏观利率传导=本链扩展/B 中国宏观信用股市/
C 跨经济体跨资产)+至少一盲测;每任务全链 --archive 归档。
