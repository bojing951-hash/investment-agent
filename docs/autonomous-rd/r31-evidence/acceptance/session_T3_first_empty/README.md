# T3 首跑(不可交付面)证据

## 背景

T3 问句初稿(见 `question_verbatim.txt`)为任务3定向探针——问当前官方政策目标利率、
已决议未生效调整、同比最新读数相比去年同月——但**未携带地图研究问句的形状词**
(如「通胀与政策环境」「哪里分化」)。正式入口实跑结果如实留档于此。

## 实跑结果(2026-11-22 21:29–21:59,树=/tmp 接受树 @ ca916cd)

- `research-one` 正式链:**不可交付**。席位以 report 段实跑得 `deliverable=false`
  (`critical_zero_evidence`,事实行数为 0)。
- `report.json`(本目录):`S1_decompose` 确定性面 `metrics: []`,注记
  「问题未词面命中任何指标(零模型不做语义翻译);事实面降级为经济体概览,
  接地问答步骤仍如实作答/拒答」;L1/L2 行数 0,L3/L4 `produced=false`;
  13 步全 `ok=true`(无崩溃,是诚实空面)。
- 席位未写研判、未 attach、未独立审查、未归档——**不可交付时不硬造交付**,
  改以 overview/history/compare 引擎面出补充披露草稿(seat log 第 6–103 行),
  并如实呈报 8 条引擎侧观察(含 ECB 决议日口径注册表/地图规划器不一致等 R32 候选)。
- 会话 `rc=0`(席位行为正确:诚实拒答+草稿披露)。

## 判定:非代码回归,是问句形状纪律

`detect_map_question` 要求形状词;无形状词的问句落入非地图链,该链只做指标名
字面命中(零模型语义翻译是 R11/R12 冻结契约的设计),命中 0 → 诚实不可交付。
与 R30 报告 T3 案例的 `map_question: True`(「哪里分化」形状词)对照,
重写问句加入「通胀与政策环境」形状词后 `detect_map_question(q, {'economies':['JP','EA']})`
= True(探针验证见 `session_T3b_formal/`),T3b 重跑走地图链正式交付。

## 文件清单

- `question_verbatim.txt`——初稿问句原文(安装树根 `question_verbatim_20261122-213248.txt` 副本)
- `report.json` / `report.md` / `FULL_REPORT.md`——正式链空面运行产物
  (安装树 `output/research_runs/20261122T133320Z_…/` 副本;FULL_REPORT 为席位
  草稿面补充披露的完整文本)
- `seat_T3_first.log`——席位会话日志(私有根路径已 ~ 归一后副本)
