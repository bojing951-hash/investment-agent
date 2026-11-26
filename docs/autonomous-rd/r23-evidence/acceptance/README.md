# Audit-R23 任务5 — 全新会话一问验收(隔离环境)

**运行编号: 20261119T173248Z** · 最终裁决: **UPHELD**(Round-3;三轮闭环 REVISE→REVISE→UPHELD,
两席分离全程保持: 判断席零上下文作答,审查席零上下文独立复算,操作席只记裁决+跑机械阶段)·
归档 content_sha256 = `bd5be016e546321e3b1c…`(ARCHIVE_MANIFEST = 裁决档-03 = `aj.content_digest(源run目录)` 三处逐位一致)

## 验收协议(按指令)

安装默认研究入口(ia_cli.py research-one)三段式,隔离树 /tmp/r23(git archive b316e88 +
11 件通道面 + CODE_VERSION.json 印章),空同题归档(树内 8 份旧档均异题)。
用户输入=旧工单(20261119T153709Z)report.json 的 run.question 原文,仅一次,
逐字(`run_question_verbatim.txt` == `report.run.question`,已核)。

## 席位与轮次

| 轮 | 判断席(Seat-A) | 审查席(Seat-B,独立复算) | 操作席 |
|---|---|---|---|
| R1 | plan(Gate A FAIL=core_missing 6 既有缺口,诚实)→attach 首过→report | 307 点: REVISE(1 MAJOR=SCN-A 阈值日期-数值错配;3 MINOR;4 NIT) | record rev=1 |
| R2 | 5 项修订+151/151 日期-数值自查 | 237 点: A1-A6 全 PASS+连续性专项新检出 1 MAJOR(CN_PMI『持续低于荣枯线』被序列否定——本席 R1 漏检,如实披露)→REVISE | record rev=2 |
| R3 | 连续性簇修订+对质行重判(『尚不能区分』→『支持主解释』,非机械) +9 断言自查矛盾 0 | 131 点零错配: UPHELD(1 MINOR+2 NIT 照列不阻断) | record rev=3 → deliverable=True → 归档 |

审查席三轮累计独立复算 **675 点**,全部从快照 series_store 与引擎接口直算,零转述。

## 关键数字(独立复算锚)

- 三利率双窗恒等: 年度 97=104+(−7)、月度 1=15+(−14),残差均 +0bp 披露;
  期末 5.1/2.89/2.21(共同交易日 2026-11-17);区分面 BEI 近30日 2.35→2.19=下降16bp。
- 36 核心格: 63 ok + 3 诚实缺席(东京CPI 12m/CN 新锚 2 格),复测 27/27
  (`../recheck_36cells.py <archive_dir>`,含 ARCHIVE_MANIFEST 溯源行)。
- CN_PMI_MFG 轨迹(R3 修正后): 2025-12=50.1、2026-03=50.4/04=50.3/05=50.0/06=50.3/
  09=50.1/10=49.3——上方停留未持续,最长连续 2 个月。
- 政策面: Fed 决议 09-16→生效 09-17(先降后升净 0);ECB 09-10→09-16(两跳
  2.0→2.25→2.5);JP 月均累计净上行 +67bp(两处 −0.1bp 显示级回落如实披露)。

## 溯源(三处同值)

- `report.run.git_head` = `ARCHIVE_MANIFEST.run_code_git_head` = MAP_REPORT 头行
  = **b316e88b2b4a98e95ab23aeac71a304485e78b0f**(CODE_VERSION.json 印章,全长 40)。

## 本轮检出的流程性事实(留档)

1. **席位分离第二证(R23 版)**: R2 的连续性 MAJOR 是审查席对判断席文本的专项扫描
   检出,且该席如实标注系自己 R1 漏检——两轮独立复核各抓到对方/自己前轮漏检,
   非单轮可替代。
2. 操作席 Round-1 审查规程误嵌 R21 版工单原文(MINOR-3): 受审件对实际 run.question
   四处文本自洽且覆盖完整,零影响;Round-2 起规程内嵌正确原文+自核命令。
3. 判断席发现契约 check15 的 headline bp 池={97,104,−7}/{1,15,−14}(三利率分解专用),
   JP +67bp 须置 from_to 而非 headline——契约面约束,非缺陷,报告存档。
4. 渲染器 NIT-2(pct 分支缺右括号)/NIT-4(指标名叠套)在受审 MAP 原样保留,
   收口提交修复+门 §F2 两判据(门 51/51)。

## 文件清单

- 归档九件 + `verdicts/`(席位原稿 VERDICT/PROSE-round1..3 + 操作席记录
  20261120__VERDICT-…-0{1,2,3}.json)
- `SEAT_A_LOG.md`(判断席三轮执行留痕)、`run_question_verbatim.txt`、
  三份审查规程 `_review_protocol_round{1,2,3}.md`、判断席规程 `_seat_a_protocol.md`
- 复测脚本: `../recheck_36cells.py`(R23 版: 印章期望值参数化自 CODE_VERSION、
  分解恒等式数值校验)
