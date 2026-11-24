## 8. 引擎面附带观察（不计入判断档的命中与偏离计数，不影响裁决）

本节记录复算过程中在只读引擎面（MAP_REPORT.md 模板文字、契约验证、信封、Gate A）上看到的不一致，供操作席与引擎侧参考。裁决只针对判断档文字；下列各项凡判断档已自行披露的，注明其所在注记。事实出处: MAP_REPORT.md 行号、report.json（$.agent_judgment.contract_verification、$.semantic_review、$.research_plan、$.steps）、冻结快照 snapshot.gate_a 与 series_store。旁证脚本: s16_engine_obs.py、s17_contract_probe.py、s18_sr_probe.py，输出 out_s16_engine_obs.txt、out_s17_contract_probe.txt、out_s18_sr_probe.txt。

| 编号 | 观察 | 事实与出处 | 判断档是否披露 |
|---|---|---|---|
| E1 | 情景脚注与情景判据不符 | MAP_REPORT.md 第 212 行「两情景方向互补;触发=条件到达即验证,失效=证伪阈值到达即推翻」。以粗网格 32 态代入两情景的触发与证伪条件，12 态四类判据均不命中（附录 B），截止日现状 (上限 4.0、日本月均 1.227、LPR 3.0) 即在其中。 | 判断档未声明不穷尽 → 第 7 节 MINOR 6 |
| E2 | 页眉「经独立语义审查」与「席位待裁」并存 | MAP_REPORT.md 第 8 行「判断文字=Agent 席 reader_map 原文(attribution=ai_inferred,经独立语义审查)」；同件第 300 行「独立席位待裁(review required)」；report.json.$.semantic_review = {required: true, seat_invoked: false, verdict: null}；report.md 第 122 行「语义审查(席位待唤起)」（规程 §0 已说明后者为裁决缺席状态的预期文字）。第 8 行的「经独立语义审查」在裁决缺席状态下是模板预设语，无对应事实。 | 不属判断档文字 |
| E3 | 「三个对照时点」模板口径与本工单锚数不符 | MAP_REPORT.md 第 7 行「三个对照时点=日历点锚(截止日−12月/−3月/最新一期)」、节标题「四地三时点环境对照」；report.json.$.research_plan.point_anchors 只有 2 个锚（3个月前 as_of 2026-08-23、最新一期 as_of 2026-11-23），对照表只有「3个月前 / 最新一期」两列，「−12月」作为对照锚在该件只出现于第 7 行。工单问的是「相比三个月前」，两锚正确，错在模板说明。 | 不属判断档文字 |
| E4 | 判断档的限定语不进读者面 | reader_map.turnings[*].narrative 在三份报告中 0/3 渲染；quality_gate_notes 10 条在三份报告中 0/10 渲染；传导三环 verdict_note 0/3 渲染。读者能看到的裁定只有 face_off_verdict 标签（「支持主解释」在 MAP_REPORT.md 出现 2 次、「尚不能区分」2 次）。 | note[8]⑤ 已披露 verdict_note 不进渲染；其余未披露 |
| E5 | 契约验证的覆盖范围小于其「VERIFIED」给人的印象 | contract_verification: 版本 jc-v1.0-phase4，17 项判定（13 项水平 + 4 项变动），15 项 VERIFIED、2 项 STALE、0 项相左，总结论 VERIFIED。(a) 判定只绑定阿拉伯数字 token: 四条 L3 陈述内另有 22 处汉字数字百分比（C2 11、C3 6、C4 5；C1 0），C4 的五个收盘口径数与末句比较结论「两种口径下美日股指跌幅均相近」都不在绑定范围。(b) C4 的六查记录「opposing: 无未消化的相反证据」判为 VERIFIED，而该末句与本席直算相左（第 4.1 节）。(c) note[8]① 自述: 文本一致性别名表未收录 JP_CPI_YOY、JP_CPI_TOKYO_YOY、JP_REAL_GDP_YOY、EA_*，子串会绑定到美国同名序列，因此对这些指标改用不带阿拉伯数字的写法——覆盖缺口反过来决定了行文方式。 | note[8]① 已披露 (c) |
| E6 | 变动类判定的 expected 字段与被比对值不同基 | 4 项 family=change/week 的 expected 为周/月初至今口径（SPX 4.2466、SHCOMP 0.1459、DAX 1.6396、VIX −24.7423），与 token（−5.51、−4.11、+0.11、+38.87）数值不同，备注写明按「资产月窗基复算…与周/MTD 派生窗并行基」判 VERIFIED。本席按月窗独立复算四个 token，偏离均为 0；问题只在字段可读性与可审计性。 | 不属判断档文字 |
| E7 | 契约判 STALE 而格级新鲜度字段为空 | CORE_PCE（末观测 2026-09-01，距截止日 83 天）与 US_REAL_GDP（2026-07-01，145 天）在契约中判 STALE；report.json.$.research_plan.point_values.cells 内这两格的 freshness、freshness_lag_days、freshness_window_days 均为 null，MAP 点值表不带过期标记；对照 CN_OMO_7D 在 MAP 第 28 行带「⚠过期:末观测2026-10-30(滞后24天>10天窗口)」。 | note[3] 已披露两项 STALE 及原因（不渲染） |
| E8 | Gate A 与计划注记的口径不一致 | (a) snapshot.gate_a.noncore_missing 列 10 个指标，其中 4 个在 series_store 有观测: CN_OMO_7D（201 点）、CN_POLICY_OVERNIGHT（16 点）、JP_CPI_TOKYO_YOY（10 点）、JP_REAL_GDP_YOY（127 点）；gate_a.note 同时写「缺失/失败数据已披露,不得进入研究结论」。(b) 计划步注记「地图计划指标缺数(披露不阻断…)」列 19 个指标，而 point_values.absent 只有 4 项（EA × 增长 / 通胀 / 政策），其余 15 个在点值格有值。(c) 证据索引对中国月度指标用月末标签（CN_CPI_YOY@2026-10-31），点值格观测日为 2026-10-01。(d) S5_compare 注记「命中 52 个指标,compare 仅取注册表序前 2」。 | note[8]②③④ 已披露 (a)(b)(c)（不渲染） |
| E9 | 步骤信封里的语义失败没有说明 | report.json.$.steps 共 66 步；S8_grounded_qa: executed = true、ok = true、semantic_ok = false、note = null；S11_archive 注记「默认关」。已执行的 S3–S6 步（55 步）semantic_ok 均为 true，另 4 步 S4_history_EA_* / ECB_* 因欧元区序列缺席跳过（executed = false）。S8 的 semantic_ok = false 是否影响判断档，只读面上无从判断。 | 判断档未引用 grounded QA 结果 |
| E10 | 数据面可疑值（未被判断档使用） | series_store.CN_NEW_LOANS 共 226 点（2008-01-01 → 2026-10-01），含 6 个负值，最近三个为 2026-04 −4006、2026-07 −5896、2026-10 −5846。判断档全文引用该序列 0 次，不影响本裁决；提请数据面核对。 | 不适用 |

## 9. 本席局限

1. 类比面只核 TOP-5 的距离与份额恒等、维度覆盖率、剔除计数自洽（1871 − 1785 − 74 = 12）与排序键单调，未独立重扫 1871 个候选月。
2. 美国决议日 2026-09-16 无法核实: 冻结日历 v1.5.0 没有任何美国政策或纪要条目，只能核对「生效日前一日」推定规则与 DFEDTARU 序列变更日 2026-09-17（生效日）直读成立。
3. 「日本 2026-11-23 休市」判断档已自标未经核实，本席同样无法在只读面上核实。
4. 引擎确定性表（MAP_REPORT.md、FULL_REPORT.md 的点值表与分解表）只在与判断档数值相关的格点上抽查，未逐格复算引擎表本身；契约 expected 字段的生成逻辑未读引擎源码，E6 的描述限于字段值对比。
5. 「相近」没有客观阈值，本席采用判断档自身在传导第 3 环给出的尺度（美中落差 1.40 个百分点称「不足两个百分点」）。即便换成宽松尺度，4.47 个百分点、约 1.81 倍的落差也难称相近。
6. 情景真值表用粗网格（上限 4 值 × 日本月均 4 值 × LPR 2 值）只为展示判据不穷尽，不是对连续取值的完整枚举。
7. 必修改句是本席依据直算值给出的一版可用表述；研判席可采用等价表述，但须保留引擎窗两个跌幅、两者落差，以及与传导第 3 环一致的「尚不能区分」口径。
