# Audit-R6 第六轮审计验收收尾报告

- 受审基线: `dcb4b17931f0dea5412e6032730248b4daac62f1`(分支 `dev/audit-fix-r1`,
  PR #1;外审第六轮三项缺口 R6-01/R6-02/R6-03)。
- 纪律: 每项先在基线复现反例,再最小修复,回归测试调用生产路径,真实网络验收,
  修复席与独立复核席分离;未降低研究要求、未修改问题、未删除失败证据、未放宽
  门槛;已冻结验收合同未为通过而修改。

## 一、三项缺口关闭表

| # | 缺口 | 状态 | 证据锚 |
|---|------|------|--------|
| R6-01 | 任务时间范围与历史覆盖校验 | ✅关闭 | §二;`tests/test_audit_r6_gate.py` §W(W1-W11);真实面=B_run3 四项数据要求全 satisfied(窗口判据入档) |
| R6-02 | 中国历史数据正式持续采集 | ✅关闭 | §三;§C(C1-C8);真实网络四步验收(step1/2/3/3b);中国任务B全链跑在正式生成器数据上(§五) |
| R6-03 | 裁决链新旧格式共用校验 | ✅关闭 | §四;§V(V0-V5);七条既有归档链在新校验下 0 BAD(§六) |

## 二、R6-01 任务时间范围与历史覆盖校验

**基线复现**(证据 `/tmp/audit_r6/r601_repro_before.txt`): 反例1「近十年 DXY」
快照仅 12 个日频观测(16 天窗)→ satisfied 放行;反例2 3000 观测全部落在
1990-1998 → satisfied 放行。

**修复**(`scripts/research_orchestrator.py` `_evaluate_data_requirements`):
- 频率取自权威注册表 `config/metric_registry.json`(run_research 传
  `registry=reg.get(...)`),未知频率+限定范围=窗口不可核验→阻断,不回落宽松。
- 任务窗=研究时点 as_of − N×365.25;窗口容忍按频率族(daily 14/10 天,
  monthly 62/75 天,含月频发布滞后);有效观测按**窗口归属**计
  (n_in_window),总量不替代窗口归属。
- 快照路径按逐日历日过滤窗内观测;S4 信封路径按重叠判定
  (first≤窗止 且 last≥窗起);**序列早于窗起=覆盖窗起**(更长历史不得
  误拒),窗内首点=max(first, 窗起)。
- 未限定范围(max_available)口径保留;report 与 archive 同一判据。

**修复后**(证据 `r6_suite_after_25of25.txt` §W 25/0): 两反例均阻断
(insufficient_coverage,窗内 n=0<1260 等basis如实);真实完整十年日频/
月频十年+72 天发布滞后/226 月全史未限定范围均 satisfied 不误拒;2019-06
后半窗/未知频率/时点不可核验均阻断;窗口不满足→report 拒交付+archive 拒
归档同判据。

## 三、R6-02 中国历史数据正式持续采集

**基线缺陷**: 生产 `fetch_macro` 单点通道丢全史;历史依赖临时 JSON 补丁;
美国宏观刷新后中国历史归零。

**修复**(生产入口三件+注册表):
- `scripts/china_market_collector.py`: 新增 `fetch_macro_history()`——
  CN_PMI_MFG(国家统计局制造业 PMI,季调)/CN_NEW_LOANS(**对实体经济发放的
  人民币贷款**,央行社融口径,与全口径对照在注册表 calc 注记)226 月全史
  (2008-01..2026-10)经 akshare 既有授权端点拉取;月份列→月首锚
  (YYYY-MM-01)归一,NaN/坏行跳过,首见去重,升序;**数值原样透传不取整**
  (与 R5 已独立复核的 226 月序列逐位一致);provenance(source/fetched_at/
  coverage/revision_policy/observation_anchor/generated_by)随档。
- `scripts/macro_collector.py`: `merge_cn_history()` 三态——fresh(本轮拉取
  成功)/carry_forward(本轮失败续存最近档,含当日档,fresh=False+
  carry_forward_from+原因,原 fetched_at 保真)/absent(无档可续=如实缺席,
  零补造);`save_macro(..., cn_history=)` 可选键;`__main__` 正式接线
  (fetch_all_macro → CN 全史合并 → thresholds → derived → save)。
- 美国宏观刷新(FRED 面)与 CN 全史合并在同一正式入口内并存,美国刷新不再
  覆盖或遮蔽中国历史。
- `config/metric_registry.json` 两 CN 条目 calc 注记正式生成器
  (R5 临时 addendum 废止)。

**真实网络验收**(证据 `r602_step1/2/3/3b`,引擎 `/tmp/audit_r6/engine`,
FRED key=既有 LIVE 只读授权,进程内使用零落盘):
1. 净环境经正式入口生成中国历史: 两指标 fresh n=226(2008-01-01..
   2026-10-01,末值 49.3/-5846.0),provenance 完整(08:08:54Z)。
2. 连续第二次采集: fresh 复跑成功(08:10:43Z)。
3. 再执行美国宏观刷新(DFF/M2SL 更新): CN 序列仍在档(08:12:16Z)。
4. 每步之后两项中国历史可正确查询(load_metric_series,版本=fetched_at+
   文件 sha256,来源=provenance 溯源)。
5. 注入 CN 端点失败模拟: carry_forward 续存+诚实披露,不造史。
   离线回归 §C(C1-C8)覆盖归一/fresh/续存/净环境/档键/美国刷新遮蔽/同日
   重跑/注册表接线。
6. **使用正式流程新生成的数据完成中国任务 B**(§五)。

## 四、R6-03 裁决链新旧格式共用校验

**基线复现**(证据 `r603_repro_before.txt`): 反例1 三档链首档删 revision/
predecessor+run_ts=WRONG_RUN+overall=UNKNOWN_VERDICT → UPHELD 放行;
反例2 digest_algorithm=UNKNOWN_ALGORITHM → UPHELD 放行。

**修复**(`scripts/agent_judgment.py` `_verdict_record_error`): 任务身份
(run_ts)/席位裁决词表(UPHELD/REVISE/NOT_VERIFIED/REJECT_ENTRY)/
digest_algorithm 现行口径三项共用检查移到 legacy 早退**之前**——旧格式仅
兼容历史缺失字段,不豁免共用校验;逐档校验(任意档位非现行算法即阻断);
前序链完整性保留(合法 legacy 头+有效复审恢复能力不变,删除历史记录不
发生)。

**修复后**(证据 `r603_after.txt`+§V 25/0): 两反例分别以
`invalid_record: 裁决词越席位词表`/`digest_algorithm 非现行口径` 阻断;
合法旧链与有效复审照常通过;report 与归档两侧结果一致(V5 两门同拒)。

## 五、中国任务 B(正式数据全链)

- **数据**: 研究输入=冻结市场快照 research_snapshot_20261112_v2+CN 两指标
  226 月全史(**Audit-R6 正式生成器**产物 macro_20261117.json,与 R5 已独立
  复核序列逐位一致);研究席脚本重放输出与 R5 冻结输出**逐字节一致**
  (seat_calc_output.txt)。
- **运行**: B_run3/20261117T083954Z,run_ok=True,四项数据要求 satisfied
  (R6-01 窗口判据生效),L2 n=17。
- **判定档 v3**: R5 冻结终档同源+一处**措辞规约修订**(数字零改动): CON-1
  陈述句两处相位边界表述『PMI<50/>50 信号相位』改『低于/高于荣枯线』,
  『两个-23.0%最大跌幅月』改称『两个并列样本最大跌幅月』(-23.0% 数值在
  CON-2/CL-3/L4 原文保留,50 在 basis『荣枯线50两侧』与 caliber_notes 保留);
  修订动因=审计基线判定档合同将相位边界裸 token 与跨资产极值月 token 误绑
  CN_PMI_MFG 当期水平(见 §七 R5 溯源发现),措辞规约避让,**不改合同**
  (已冻结验收合同红线遵守)。
- **契约门**: 生产 attach 通过(validation_passed,blocked=null;复核验
  VERIFIED 6 检查=4 VERIFIED+2 STALE/0 矛盾/0 未绑/六检 6 族全过;2 条
  STALE=事实通道 12734亿@2026-09-01 落后历史通道一个月,basis/CL-6/CTR-4/
  limitations 五处如实披露,R5 同形)。
- **独立审查席 r6-b-review**(未参与研究与修订;自写复算脚本
  `review_seat/recompute_r6b.py`,纯 stdlib 零引用研究席代码): 裁决
  **UPHELD**(rev1,per_must_fix=[],105 项数字判定全吻合 0 失配)。覆盖面:
  ①修订面核验——v3 与 R5 归档终档全叶 diff=263 叶仅 3 处差异,与声明完全
  一致,全部数字/p 值/n 值零变化,-23.0% 在 CON-2/CL-3/SCN-3×2/十二问1
  保留、50 在 basis+caliber_notes 保留,荣枯线措辞与严格分组语义等价
  (50.0 持平月 3 个逐月复算剔除逻辑不变),revision_note 无夸大;②数字
  复算——相位统计/40 相关格逐格/极值月归属/CL-5/CL-1/CL-9/机制链/情景锚
  全部独立复现;③数据溯源——seat_data 两指标 226 月与正式生成器随档
  macro_20261117.json 逐位全等,冻结输出与 R5 仓内冻结输出 diff 全等;
  ④合同门复跑 VERIFIED 与 attach 记录逐项一致。非必修注记 5 条入档
  (MW 渐近无校正/NW 控滞后规格/CL-9 次月可得口径/-23.0% 一位小数约定
  下并列/CL-6 中国专文口径 3 份)。
- **归档**: `research_archive/20261117T083954Z_中国宏观信用与制造业景气_
  CN_NEW_LOANS_新增贷款与_CN_PMI_M/`(链 UPHELD×1,run==archive==裁决锚
  三处一致已核,content_sha256=06624da7…f6437a;仓内侧链复验
  UPHELD/fresh/零错);裁决档 `audit/semantic_review/20261117/
  VERDICT-20261117T083954Z-01.json`(format_version=2,digest_v3)。

## 六、无回退复验(A/C/BLIND/F10/中国B旧链/修正后E2E)

- **链级校验**(R6-03 修复后生产读取端,证据 `old_chains_reverify.txt`):
  全部 7 条既有归档链有效(0 BAD;修正前 E2E fresh=False=被修正后链取代,
  历史保留)。
- **判定档合同基线重跑**(证据 `old_chains_contract_rerun.txt`): 6/7 链
  VERIFIED(0 矛盾);**唯一例外=中国B旧链(20261117T035814Z)基线重跑
  CONTRADICTED 3/9**——根因见 §七,由本轮新链(§五)在基线代码上关闭。
- **BLIND 重放**: `sh docs/autonomous-rd/phase4/BLIND/blind_replay.sh` →
  PASS(切片重放逐字节一致+独立复算 64/64 中,拼接 sha256=feaa1536…e1c23
  与档一致)。
- **F10 重放**: `sh docs/autonomous-rd/phase4/F10/f10_replay.sh` → PASS
  (sha256=6e5fcf4a…14d3f 与档一致)。
- **修正后 E2E**: 链有效+基线合同重跑 VERIFIED 0/6。

## 七、R5 溯源发现(如实披露,历史裁决保留)

- R5 报告 §六曾披露暂存引擎 `/tmp/audit_r5/engine_cn` 与仓树存在「渲染器
  漂移(仅影响 report.md 视图渲染,不影响数据/判定)」。本轮复查发现该漂移
  **不止渲染器**: engine_cn 的 `scripts/research_contract/text_consistency.py`
  含当时未合并的引擎席位分支 `dev/rd-r45-b-scorecard-tableface`(ad2f6e4)
  改动(回落重路由/评分引用/表列角色感知),基线(dcb4b17)没有。
- 后果: 中国B旧链 attach 时的契约门运行在含 R45 席位改动的代码上
  (存档 VERIFIED 6/0/0);同一冻结输入在**审计基线**代码上重跑=
  CONTRADICTED 3/9——三条误绑(相位边界『50』×2+跨资产极值月『-23.0%』
  被绑为 CN_PMI_MFG 当期水平),属 R45 席位已修的 B 族误报类(引擎侧
  RDG-20261116-014 ③),该修复未进入审计基线=本轮分支点(36c1e7e)之前
  未合并 main。
- 同期 4 个归档运行 git_head 记录为 ad2f6e4(引擎树当时在该分支上);其中
  修正后 E2E 等其余链的判断档不含该误报类 token,基线重跑照常 VERIFIED
  (§六),仅中国B旧链受影响。
- 处置: 旧链按外审指令**原样保留**(裁决链有效,append-only);存储的契约门
  结论在基线代码上的可复现性标记 **NOT_VERIFIED**;本轮新链(§五)完全运行
  在审计基线代码上,彻底关闭该缝隙。引擎侧 R45 修复合入 main 后该误报类
  在两代码线上一致(超出本轮范围,如实移交)。

## 八、最终版本全量测试

- 回归套件: `tests/test_audit_r6_gate.py` **25/0**(§W/§C/§V);
  `tests/test_audit_r5_gate.py` 29/0(S4 信封重叠修复后,完整历史不误拒)。
- 全电池(exit 口径,逐件直跑): [待电池完成后回填]
- CI(最终 HEAD,3.11+3.12): [待推送后回填]

## 九、项目状态与恢复说明

- 分支 `dev/audit-fix-r1`(PR #1),本轮波=[待推送后回填];未并 main、
  未合并 PR、未部署、未改远端权限。
- 恢复入口=本报告+`docs/autonomous-rd/cn-task-b-20261117T083954Z/`
  (重放包)+归档 `research_archive/20261117T083954Z_…/`+裁决
  `audit/semantic_review/20261117/VERDICT-20261117T083954Z-*.json`;
  R6 证据文件=`/tmp/audit_r6/`(r601/r602/r603/old_chains/r6_suite)。
- **当前状态: 三项缺口+中国任务B收口完毕,停止在「等待外部审计」;不自行
  宣称最终验收通过。**

## 十、七项最终交付

1. **HEAD/分支/PR/CI**: [待推送后回填]
2. **三项缺口关闭表**: §一。
3. **反例修复前后**: §二/§四(r601/r603 before/after)。
4. **中国历史正式采集/连续更新/美国刷新后**: §三(step1/2/3/3b+每步查询)。
5. **新中国B报告/独立复核/输入版本/归档摘要**: §五。
6. **完整测试结果与未验证事项**: §八+§七(NOT_VERIFIED 面)。
7. **恢复入口**: §九。

> 没有证据的项目标记 NOT_VERIFIED。本报告完成时停止在「等待外部审计」。
