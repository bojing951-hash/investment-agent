# 独立语义审查席规程(Audit-R32 正式使用验收,T3,Round-1,零上下文)

本文件只含程序与工件路径,不含任何判断内容,也不含开发者期望。
席位性质(章程 docs/autonomous-rd/SEMANTIC-AUDIT-SEAT.md §1): 真独立、无开发树
上下文;席可拒开发者声明(UPHELD 不欠,REVISE 不留情)。数值对错由确定性层负责,
但本席仍须独立复算抽核——报告里的数字若与证据面不符即为 MAJOR。

## 1. 工单与受审对象(只读)

- 工单原文(逐字): `/tmp/r32-accept/final2/output/research_runs/20261123T124341Z_2026年11月_日本和欧元区的通胀与政策环境_两地央行当前官方政策目标利率各处/question_verbatim.txt`
- 受审运行目录(只读,不得写入任何文件): `/tmp/r32-accept/final2/output/research_runs/20261123T124341Z_2026年11月_日本和欧元区的通胀与政策环境_两地央行当前官方政策目标利率各处`
  - 读者报告: `MAP_REPORT.md`(地图问句读者面)、`FULL_REPORT.md`(完整报告)、`report.md`
  - 判断档(研判席产出,已 attach): `agent_judgment.json`(l3.contradictions / l3.mechanism_chains / l4.scenarios / reader_map / agent_declaration)
  - 引擎运行档: `report.json`(约 4 MB,用 python 抽取,勿整读)、`evidence_index.json`、`views_digest.json`
  - 冻结输入副本: `root_overlay/config/release_calendar.json`(发布/政策日历)、`root_overlay/config/metric_registry.json`、`root_overlay/data/daily/research_snapshot_20261123.json`(冻结快照)
- 隔离安装树(只读;git archive 净安装,`CODE_VERSION.json` 印章 f722e3c0bf7cd10aee64a8f4a166a136180a28ea): `/tmp/r32-accept/final2`
  - 快照同一份: `/tmp/r32-accept/final2/data/daily/research_snapshot_20261123.json`(顶层含 research_as_of / facts / series_store / gate_a / quality 等)
- report.json 抽取指针: `run`(evidence_gate / frozen_inputs / git_head / ts_utc)、`research_plan`
  (point_values / point_anchors / regions / turning_candidates / us_rates_trio / asset_moves /
  policy_event_clusters / policy_doc_facts / dimension_gaps / ex_post_offsets / cutoff)、
  `layers.L1_事实层.rows`、`agent_judgment.contract_verification`(确定性验证结果,含逐项 verdicts)、
  `steps[*].envelope`(S3/S4/S5/S6/S8 各子命令信封=引擎确定性面)。

## 2. 边界

- 只读复算。可运行树内只读接口或自写脚本做独立计算;**不得**修改运行目录与安装树内任何文件
  (席位自己的脚本与产出只写到 `/tmp/r32-accept/review/T3_round1`)。
- 不得联网;不得运行 `ia_cli.py` 的 plan/attach/report/archive/replay/update 等任何写操作;
  不得调用 `agent_judgment.record_semantic_verdict`(登记由操作席执行)。
- 不得读取: `research_archive/`、树内 `docs/`(含各轮证据与报告)、`/tmp/r32-accept/out/`、
  `/tmp/r32-accept/scripts/`、`/tmp/r32-accept/replay/`、`/tmp/r32-accept/install*`、其他运行目录、
  `~/investment-agent-product`——这些含操作席/研判席的中间产物,读了即失独立。
- 自写脚本放 `/tmp/r32-accept/review/T3_round1/`,用 `python3 -I <脚本> <路径参数…>` 运行(路径作参数传入,不在数据目录内起解释器)。

## 3. 复算覆盖要求(最低 40 点;逐点独立于报告转述——从冻结快照 series_store、
冻结日历、report.json 引擎面直算后,再与报告/判断档文字比对)

① 研究截止日: 报告自称的截止日与快照 research_as_of/target_date 是否一致;报告引用的每个
   观测日/发布日/决议日/生效日与截止日的关系(晚于截止日的观测、发布、决议、生效均不得作为
   可引用证据;历史类比的事后段只能以「事后结果」身份出现并明确标注)。
② 点值锚格: 每个被引用的地区×维度×时点(12个月前/3个月前/最新一期,或工单指定的窗口端点)
   的值/观测日/同比/缺席理由,从 series_store 直算。
③ 同比: 凡称「同比」的数,基期是否为去年同月/同季;基期观测缺席处是否如实标「缺基期/
   不可得」而非用相邻月份替代;「最近有效同比」的月份与数值直算。
④ 政策面: 决议日/生效日/目标值/距离上次调整天数,逐项与冻结日历条目和序列变更日核对;
   「官方目标」「市场报价」「月均值」各口径是否分列且不互相冒充;待生效决定(若有)是否
   与现行有效目标分记。
⑤ 三利率分解与资产月窗(若在场): 名义=实际+盈亏平衡恒等、窗口端点日期与值、变化幅。
⑥ 转折判断与候选面: 前值→后值/窗口/谁先变/跟进或背离的叙述是否与候选面一致,
   「先后」主张是否有相应时间分辨率支撑。
⑦ 传导链各环: 证据级(E1/E2/E3)标注与该环实际证据是否相称,E2/E3 环不得以事实位措辞出现;
   环内数字可回贴引擎面。
⑧ 历史类比(若报告含该节): 候选段/距离/分位/同步性叙述所引数字;当时可知面与事后段的
   划分是否正确;随后 3/6/12 个月结果是否以「事后实际」措辞呈现、是否被表述成预测。
⑨ 情景: 触发条件/证伪阈值/期限是否可观测、是否与截止日读数相容(已触发的触发条件、
   已被证伪的前提不得作为「待验证」情景);两情景是否方向互补而非孤证。
⑩ 总判断/走位/对质表文字与数值的一致性(方向词/单位/精度/「最高」「最低」「回到」类关系词);
   对质表「尚不能区分/支持竞争解释」的判断是否与该行观测一致。
⑪ 诚实缺席项: 报告声明的每个缺口(序列缺席/缺基期/过期/降级)是否属实(序列级证实),
   有无以相邻口径冒充;Gate A 状态是否如实披露。
⑫ 截止日当日标注的日频观测(如有): 是否带时点/口径说明,该说明与快照 research_as_of
   时间戳是否相容。
⑬ 工单问及两地央行「当前官方政策目标利率」与通胀同比: 核验每个目标利率的数值/生效日/是否
   现行有效(待生效决定与现行有效目标是否分记)、通胀同比的基期与数值。

## 4. 六查+证伪(章程 §4,须主动找反例)

对每条 L3 矛盾陈述与每条机制链: 证据相关性 / 支持度(定性措辞 vs 证据强度)/ 竞争解释
(是否在列且真正竞争,同证据可容纳,非稻草人)/ 反对证据(有无未披露的反向事实)/
结论是否超出证据 / 证伪条件可观测性(被点名的区分指标须在证据面在场,且两解释在其上的
预言方向确实不同)。每条至少做一次「反方攻击」并记录攻击与结果。
历史段同步性(若在场): 同步/分化主张须与引擎地区×维度同步面一致;叙述称同步而面=缺证,
或叙述与面冲突,均为 REVISE 必修。

## 5. 裁决标准

- MAJOR = 数字/日期/方向错或与证据相左;缺基期却给出同比;以相邻口径冒充;事后信息冒充
  当时可知;结论超出证据且无标注;证伪条件不可观测。
- MINOR = 口径/披露可改进但不改变结论;NIT = 行文。
- 零 MAJOR 且无 REVISE 级问题 → **UPHELD**(MINOR/NIT 如实列出,不构成阻断)。
- 存在 MAJOR 或 REVISE 级问题 → **REVISE**,并逐条给出「原句 → 改句」(只改必修句,
  改句须可用证据面数字成立;拿不出成立的改句=证据不足,如实写明)。
- 禁止凭记忆或常识补数: 席位引用的每个数字必须来自上述只读面并写明出处(文件+键)。

## 6. 产出(写到 `/tmp/r32-accept/review/T3_round1/`)

1) `PROSE-round1.md`: 复算清单(逐点: 出处键/直算值/报告值/一致与否)+ 六查逐项结论 +
   反方攻击记录 + 问题清单(按 MAJOR/MINOR/NIT)。
2) `VERDICT-round1.json`(UTF-8,合法 JSON):
```json
{
  "seat": "semantic-audit-seat",
  "reviewer": "independent-zero-context-seat-r32-t3-round1",
  "verdict": "UPHELD|REVISE",
  "overall": "UPHELD|REVISE",
  "notes": "裁决依据摘要(中文,含抽核命中/偏离计数与要点;此段将逐字进入裁决档)",
  "items": [{"severity": "MAJOR|MINOR|NIT", "where": "文件+段落/条目", "note": "问题",
             "original": "原句(MAJOR 必填)", "fix": "改句(MAJOR 必填)"}],
  "must_fix": ["必修条目(MAJOR)逐条,无则空数组"],
  "counterexamples_sought": ["反方攻击 1: 攻击内容→结果", "…(每条 L3/机制链至少一条)"],
  "recompute_points": 0,
  "recompute_mismatches": 0,
  "mismatch_details": [],
  "audited_at": "2026-11-23"
}
```
3) 席位自写的复算脚本与中间表(同目录),供操作席复核。
最终回复只需给出: 裁决词、recompute_points / mismatches、MAJOR 条数、两件产出路径。
