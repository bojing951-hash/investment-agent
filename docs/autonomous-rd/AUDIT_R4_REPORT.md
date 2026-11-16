# AUDIT_R4_REPORT — 第四轮审计收尾修复报告(2026-11-17)

> 审计对象: PR #1(github.com/bojing951-hash/investment-agent)分支 `dev/audit-fix-r1`,
> 受审基线 commit `5fc5df8c05e56fc13b62355a56c0182eee8af5a4`(Audit-R2 收口尖)。
> 本轮指令: 六项收尾修复 R4-01..R4-06(§二),反例优先验证+真实流程验收(§三),七件交付(§五)。
> 边界遵守: 未并 main / 未合并 PR / 未部署 / 未改远端权限 / 未瘦身
> (CODEBASE_SIMPLIFICATION 保持 DEFERRED)/ 沿用既有 PR #1 不另开。
> 不伪造数据、运行日志、独立席位或通过状态;无法验证处显式标 NOT_VERIFIED。

## 一、六项发现关闭表(§二)

| # | 项 | 状态 | 修复位置 | 回归结果 | 真实任务证据 | 剩余限制 |
|---|---|---|---|---|---|---|
| R4-01 | 裁决损坏与缺字段不得放行 | ✅关闭 | `scripts/agent_judgment.py`(最新档解析失败=`corrupt_latest` 全链阻断,**不回退旧 UPHELD**;缺必填/越表词/revision 撞号/错误 run 键=落档即抛;`record_health` 披露历史损坏;失败历史保留,有效复审 rev 跳号恢复交付) | J1-J9 九检全绿(健全基线/截断/缺字段/复审恢复/损坏保留/跨日截断/撞号/错误 run/mtime 调换) | P1-1 反例(§二);E2E 链(§六)由生产写档函数全程生成 | 无 |
| R4-02 | 审查覆盖全部实际交付输入 | ✅关闭 | `scripts/agent_judgment.py`(content_digest **v3**=canonical(report.json−semantic_review)+judgment−semantic_review+**views_digest.json**;唯一规范内容=三件,FULL_REPORT 由同源渲染并受 copies_consistent 门;semantic_review 状态块排除=防循环绑定;改任一渲染输入→旧裁决 fresh=False) | K1-K4 四检全绿(含 K2 反例: 只改 views_digest 机构/标题→旧裁决失效拒交付) | P1-2 反例(§二);四归档 manifest `digest_algorithm=v3` 三方一致核验(§三) | 无 |
| R4-03 | BLIND 同版重放证据 | ✅关闭 | `docs/autonomous-rd/phase4/BLIND/`: data_slice/(GOLD_F/DXY/VIX/UST_10Y/BEI_10Y/TIPS_10Y/HY_OAS 七序列**原始输入切片**,双 sha256 核验)+blind_replay.sh(一条命令)+REPLAY.md(冻结参数表: 数据版本/范围/对齐/缺失处理/窗口/分桶/t 式/数值规范)+blind_independent_recompute.py(独立实现 64 靶值) | 重放 PASS: 切片重跑与冻结输出逐字节一致+独立复算 64/64 | `sh docs/autonomous-rd/phase4/BLIND/blind_replay.sh`(§四) | 复算席首轮自检 10 失配=复算席自身靶值构造错误,已逐项溯源修正并留注记(REPLAY.md 判定纪律节);带边括注第 4 位小数跨实现浮点噪声按 1.5e-3 容差披露(sum vs fsum 求和路径),不触及结论性声明 |
| R4-04 | 跨日归档保留完整裁决历史 | ✅关闭 | `scripts/research_orchestrator.py`+`ia_cli.py`(归档名=verdicts/`<YYYYMMDD>__<basename>` 全局唯一;归档前路径冲突检查;ARCHIVE_MANIFEST verdict_chain 逐档 sha256+predecessor(源形)+revision) | L1-L4 四检全绿(跨日撞名三档全保留/唯一名/manifest 链/终裁三处一致) | 四真实归档 10/10 链条目全验(§三);重复归档正例拒=`archive_exists` | 无 |
| R4-05 | 必要/可选数据规则贯通 | ✅关闭 | `scripts/research_orchestrator.py`(plan 采集前冻结 data_requirements;**outcome 判定源序**=快照 series_store→本管线 S4 history 步信封→L1/S3 单点=insufficient_coverage→missing)+`scripts/agent_judgment.py`(blocked_class_of 三级单源: critical_zero_evidence>required_data_missing>optional_data_missing,attach/report/archive 同判) | M1-M5+N1-N6 十一检全绿(单点≠历史分析/可选缺失+旗标+有效审查=可交付/可选无旗标拒/零证据旗标也不放行/单源复算/BEI 采集档 2499 日 satisfied 回归) | B 任务三面实证+E2E 全绿路径(§六) | 引擎树 CN 宏观序列(CN_PMI_MFG/CN_NEW_LOANS)仅有最新单点=硬边界,B 如实拒答(见 §三 B 行) |
| R4-06 | A/B/C 当前版本验收关闭 | ✅关闭 | `scripts/agent_judgment.py` `rebind_verdict_digest`: 旧锚(v1/v2)在当前内容上复算一致=**内容未变的机器证明**,才写 v3 新档(revision 续链+rebind 块);内容已变→ValueError(须重审查,不得改 hash 冒充) | A/C/BLIND/F10 四任务 rebind 全成;A 原 /tmp 运行目录被系统回收→replay_view 档案字节拼装,v1 锚(60e1746e)在拼装面精确复配 | 四任务 report 门+归档门全绿(§三);B 按新分级如实拒答+三面实证 | B 交付阻塞维持(必要数据缺口),恢复条件=引擎树接入 CN 宏观历史序列后重跑 |

波内附加修复(验证过程发现): outcome 判定只查快照 series_store 时,BEI_10Y 等经 macro 采集档入库的 2499 日序列被误判「仅最新单点」——修为消费本管线 S4_history 步信封(与 Agent 席所见同源,零新信任面,不越 FIX7 读外部采集目录),§N 六检回归。

## 二、P1 反例验证(§三: 修改前失败→修复后拒绝误放行)

两反例脚本在生产写档函数上构造完整裁决链,基线与修复面同脚本同数据:

| 反例 | 基线 5fc5df8 | 修复后 1d53857 |
|---|---|---|
| P1-1(R4-01) `repro_r401.py`: rev1 REVISE→rev2 UPHELD→生产写 rev3 REVISE 后截断 | ❌ 误放行: verdict=UPHELD fresh=True error=None(裁决倒退回旧 UPHELD,deliverable 通行),exit=0 | ✅ 已阻断: verdict=None error=corrupt_latest(全链失效),exit=1 |
| P1-2(R4-02) `repro_r402.py`: 裁决后只改 views_digest 机构名/标题 | ❌ 误放行: deliverable=True fresh=True copies=True 且 FULL_REPORT 已含篡改名,exit=0 | ✅ 已阻断: deliverable=False fresh=False copies=False,exit=1 |

正例保留: 同链健全基线(J1/K1)在修复面依旧 deliverable=True——拦截不伤有效交付。
复现环境: 基线=git worktree@5fc5df8,修复面=1d53857;脚本与输出存 `/tmp/audit_r4/repro_r4{01,02}.py`(会话工件,逻辑已固化为套件 J2/K2 检)。

## 三、A/B/C/BLIND/F10 交付与归档状态(§五.3)

| 档 | 交付态(report 门,1d53857 实测) | 归档态 | 裁决链 |
|---|---|---|---|
| A(UST_10Y→HY_OAS/SPX) | deliverable=True fresh=True verdict=UPHELD n=2 copies=True | `research_archive/20261116T045959Z_…/`(2 链条目全验) | 20261116 -01(原)→20261117 -01(rebind,v1 锚经 replay_view 拼装面复配) |
| B(CN 宏观信用) | **deliverable=False blocked_class=required_data_missing degraded_ok=False**(如实拒答) | 未归档(不可交付不归档) | 无有效裁决;三面实证见 §六.2 |
| C(美日政策利率分化→USDJP) | deliverable=True fresh=True verdict=UPHELD n=2 copies=True | `research_archive/20261116T053259Z_…/`(2 链条目全验) | 原档→rebind |
| BLIND(GOLD_F×REAL_10Y×DXY) | deliverable=True fresh=True verdict=UPHELD n=3 copies=True | `research_archive/20261116T053623Z_…/`(3 链条目全验) | 20261116 -01→-02(R2 独立复算)→20261117 rebind |
| F10(BRENT→BEI) | deliverable=True fresh=True verdict=UPHELD n=3 copies=True | `research_archive/20261116T114933Z_…/`(3 链条目全验) | 原档→R2 -02→20261117 rebind |

归档完整性独立核验(2026-11-17 于 1d53857): 四档 verdict_chain **10/10 条目**逐项验证=归档件在场+sha256 前 16 位吻合+source_rel 在册可解析+predecessor(源形)续链+revision 单调;重复归档请求被 `archive_exists` 正确拒绝(路径冲突守卫)。
B 重跑冻结面(20261116T221809Z): FXI/CHINEXT=satisfied;CN_PMI_MFG/CN_NEW_LOANS=insufficient_coverage(仅最新单点≠历史分析)。

## 四、BLIND 一条命令重放(§五.4)

```sh
sh docs/autonomous-rd/phase4/BLIND/blind_replay.sh
# 期望末行: BLIND REPLAY PASS: 冻结输出拼接 sha256=feaa1536dc19404fd316cebada87caa8076884b106dd5b6426c379b93dee1c23
```

输入哈希(脚本内 `-c` 核验,改动即 FAIL):
- research 切片 `4e5e504ac300f6bb689b4f1b014735e62d4ead9440ff4ce5e354c301fb2abfa4`(GOLD_F/DXY/VIX)
- macro 切片 `aaf7b429891036a7f01c7f3843f18904c5b430e18e3d3fc5230d7d06c35b84d8`(UST_10Y/BEI_10Y/TIPS_10Y/HY_OAS)

固定参数全表见 `docs/autonomous-rd/phase4/BLIND/REPLAY.md`(数据版本/切片范围/对齐=四序列交集 n=2492/缺失处理=配对剔除无插值/REAL=round(UST−BEI,4)/窗口 252(辅 126)/VIX=20 分桶/HY 严格三桶/t 式/sum-vs-fsum 数值规范)。零网络零模型,任意 cwd 可跑。

## 五、测试与 CI(§五.5)

- 直跑口径: 候选 `1d53857` 全量 `tests/test_*.py` **176 件全部绿(0 红)**(test_model_live 既有跳过惯例维持)。
- pytest 目录口径: 同候选 **176 passed / 0 failed**(353s)。
- 新增套件 `tests/test_audit_r4_gate.py` **29/0**(J1-J9/K1-K4/L1-L4/M1-M5/N1-N6;直跑+pytest 双入口)。
- test_p3_wp_d: 96 用例 OK(浮点末位与固定摘要修复维持;R1 期 23 行修正,本轮复验绿)。
- 复杂度基线: 生产 90f/52559L vs 基线 52253L(+0.6%,±5% 门内)。
- CI(py3.11+3.12 真实矩阵,`.github/workflows/offline-tests.yml` matrix=['3.11','3.12']): 见 §八回填。

## 六、完整自然语言流程运行记录(§三.5)

### 1. E2E 主链(BEI_10Y×GOLD_F×DXY,2026-11-16/17)

问题(自然语言,一次输入,用户无需运行中间命令):
「美国盈亏平衡通胀预期 BEI_10Y 上行阶段,黄金 GOLD_F 与美元指数 DXY 的表现与传导」

- **规划**: plan 段冻结 data_requirements 三项,采集后全 satisfied(BEI_10Y 经 S4 采集档 n=2499 日)。
- **证据**: 引擎真实数据(研究快照+macro 采集档),L1 事实行+证据索引落档。
- **判断**: 研究席(e2e-research-seat,独立上下文)自算统计并产 judgment_mvp.json;首轮契约门 CONTRADICTED(55/65,47 unbound——拉丁指标 ID 毗邻自算统计被绑为水平声明,与 BEI=2.2 面值相左)=**验证器正当拦截**;按措辞规约修订(数字与结论零改动,只改绑定形式: 别名隔离/辖域词/年份样本掩码/basis 重构/机构引用豁免;三处实质修正=「L1」字样改「快照事实行」防数字 1 误绑/脚本路径更名防 2 误绑/年内拆分端点差 0.04pp 如实披露),复验 **VERIFIED(6 检/0 相左/0 unbound)**。
- **attach(生产写)**: attached=True,validation 0 违规,contract_verification VERIFIED 落档。
- **report**: deliverable=False(仅因裁决未落,verdicts_n=0=审查暂停态),copies_consistent=True。
- **独立审查**: e2e-review-seat(未参与任何修复的独立上下文,自写复算实现 /tmp/review_seat_recompute.py,未读研究席脚本)从冻结输入(以 report.json 步骤信封为数据版本权威: research_snapshot_20261112_v2+macro_20261114)复算 **116 项: 113 逐位吻合/3 披露容忍(两处 OLS se_dBEI 第 3 位路径差,t 判定不变;最长非负段终点日引注滑 1 交易日,窗数与起点精确一致)/0 触结论失配**;语义面六点审读(辖域与证据分级/正面回答自洽/竞争性解释非稻草人/L4 可证伪完备/诚实披露复算/1 处不入必修的脚本名文档微瑕);初版偏差按纪律先疑自身构造(逐序列差分 vs 水平日交集口径),证实正文口径后全部逐位复现,反例探针 4 条入档。经生产写档函数落裁决: **UPHELD**(revision=1,content_sha256=78bb07e0…,落 `~/investment-agent-dev/audit/semantic_review/20261117/VERDICT-20261116T222254Z-01.json`,词表 fail-closed 内)。
- **必要修订**: 未触发——独立审查首裁即 UPHELD(3 容忍项均不触及结论,微瑕不入必修,如实随档);修订环的机器与真实先例分别为本研究判断的契约修订环(上一步)与 PC Phase 5 当日修订。
- **最终 report**: deliverable=**True**(verdict=UPHELD fresh=True verdicts_n=1,copies_consistent=True,mvp_complete=True)。
- **归档**: `research_archive/20261116T222254Z_…BEI_10Y…/`(append-only;三方摘要核对 78bb07e0=run=归档=裁决锚;verdicts/ 跨日唯一名随包)。

### 2. B 任务三面实证(R4-05,20261116T221809Z 重跑)

| 面 | 操作 | 结果 |
|---|---|---|
| 面1 | attach 无旗标 | ok=False attached=**False**(blocked=run_ok_false,写前拒;既有挂载记录不被面 1 触碰) |
| 面2 | attach --allow-failed-run + 坏 schema 判断 | attached=**False**,4 违规落档(SCHEMA×2/ATTR/SCN-PLURAL) |
| 面3 | attach --allow-failed-run + 有效判断(contract VERIFIED 12/0/0) | attached=**True**,但 report 门 deliverable=**False** blocked_class=required_data_missing——**旗标不是万能放行** |

注记(设计行为如实登记): 失败重提会以「末次尝试为准」覆盖前次成功挂载记录并清 L3/L4 残留 content(R23 MINOR-3 反半落位)——交付方向保守(失败重提使交付失效,须有效重提恢复),非误放行缺陷;面 2 演示后已重提有效判断恢复面 3 终态。

## 七、更新后的审计结论与项目恢复状态(§五.7)

- 六项发现全部关闭(§一);两个 P1 误放行反例在基线复现、在修复面阻断(§二)。
- 有效任务可交付(A/C/BLIND/F10 四档 deliverable=True+归档 10/10 链验),缺口任务如实拒答(B)。
- 证据可独立复算: BLIND 一条命令重放+64 靶值独立复算(§四);E2E 独立审查席从冻结输入复算(§六)。
- 治理发现维持(Audit-R2 §六): main 分支保护实测未配置,建议合并 PR #1 前启用;本轮未改远端权限。
- **当前状态: 等待用户外部审计**(分支尖+本报告;未并 main/未合并 PR/未部署)。

## 八、CI 回填(py3.11/3.12)

[待推送后回填: 两版本 run 链接与结果]

## 九、最终坐标

- 分支: `dev/audit-fix-r1`(覆盖推送至既有 PR #1)
- 修复链: `2882932`(R4-01/02/04/05 代码+R4-03 重放包+CI 矩阵)→`1d53857`(R4-06 rebind+四归档+B 重跑+outcome 源序修)→[待: 台账与本报告 docs commit]
- 最终 HEAD: [待回填]
