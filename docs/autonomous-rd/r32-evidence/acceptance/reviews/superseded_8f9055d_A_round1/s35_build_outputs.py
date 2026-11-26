#!/usr/bin/python3 -I
"""Assemble PROSE-round1.md (body + per-point appendix) and write VERDICT-round1.json; validate.
usage: s35_build_outputs.py <this seat dir>"""
import sys, json, re, os
d = sys.argv[1]
body = open(os.path.join(d, "_prose_body.md"), encoding="utf-8").read()
app = open(os.path.join(d, "_appendix.md"), encoding="utf-8").read()
prose = body.rstrip("\n") + "\n\n## 附录 A · 逐点复算清单(逐点: 出处键 / 直算值 / 报告值 / 一致与否)\n" + app
open(os.path.join(d, "PROSE-round1.md"), "w", encoding="utf-8").write(prose)

M1_O = "较最新读数 2.15(2026-11-20)低 35 个基点"
M1_F = "较最新读数 2.15(2026-11-20)低 38 个基点(该读数较阈值 1.8 高 35 个基点)"
M2_O = "中国 PPI 低点在 2025-11 且此后连升"
M2_F = "中国 PPI 低点在 2025-11，此后总体上行(至 2026-10 的 5.7；其间仅 2026-07 由 4.1 回落至 3.5)"
M3_O = "(候选面全体首位为中国制造业PMI，增量3.40)"
M3_F = "(中国制造业PMI居增长维候选面首位，增量3.40；候选面全体首位为中国PPI同比，增量4.8)"
jud = json.load(open(sys.argv[2], encoding="utf-8")) if len(sys.argv) > 2 else None
if jud is not None:
    assert M1_O in jud["l4"]["scenarios"][1]["rows"]["falsification"]["threshold"]
    assert jud["reader_map"]["turnings"][0]["first_mover"].count(M2_O) == 1
    assert jud["reader_map"]["turnings"][1]["first_mover"].count(M3_O) == 1
    print("originals verified verbatim against agent_judgment.json")

v = {
 "seat": "semantic-audit-seat",
 "reviewer": "independent-zero-context-seat-r32-a-round1",
 "verdict": "REVISE",
 "overall": "REVISE",
 "notes": ("工单A第1轮: 席位在只读面(冻结快照 series_store、冻结发布日历、信封引擎面、report.json)亲自复算 1111 点, 8 处不一致(去重后 6 处: 判断档 5 处 + 引擎面规则观察 1 处)。"
           "判断档偏离: MAJOR 3、NIT 2; 引擎面 1 处(REP 相似检索同步面对 2022-06 锚的中国 LPR 发布日取 2022-06-19, 实际 2026-06-20, 前后值均 3.7、同步标签不受影响, 不在判断档文字内)。"
           "MAJOR-1 数字错: SCN2 失效阈值依据句称 2020-11-30 的 1.77「较最新读数 2.15(2026-11-20)低 35 个基点」, 直算为 38 个基点(35 是最新读数距阈值 1.8 的距离)。"
           "MAJOR-2 方向与证据相左: turnings[0] 称「中国 PPI 低点在 2025-11 且此后连升」, 而 CN_PPI_YOY 2026-07 由 4.1 回落至 3.5, 且与同档 TR1 环1 文字自相矛盾; 低点月本身正确。"
           "MAJOR-3 与引擎面相左: turnings[1] 称「候选面全体首位为中国制造业PMI，增量3.40」, 而引擎转折候选面首行为 CN_PPI_YOY(增量 4.8), CN_PMI_MFG(增量 3.4005)居全体第 2、增长维首位; MAP_REPORT.md 候选面表同序。"
           "三条均有证据面数字可成立的改句。其余复算一致: 截止日无违规(无晚于 2026-11-23 的观测被引用, 美国CPI 2026-10 同比因缺基期未给出), 22 个点值格与 63 行走位回贴逐位一致, 三利率分解(12个月 名义+91=实际+102+盈亏平衡-11, 近1个月 名义-8=实际+11+盈亏平衡-19, 残差0), 资产月窗 8 行回贴逐位一致, 政策面(欧央行两次+25bp、美联储+25bp回补、日本+75bp、中国持平)与决议前可见通胀一致, 历史段 99 个事后月末值与同步面 3/5/1 一致, 情景阈值指标在场且标「假设非预测」。"
           "六查与反方攻击对 C1/C2/C3/M1/M2 及传导对质四环逐条完成, 未见结论超出证据或证伪条件不可观测。"
           "MINOR 4: 解释B「近1个月分解…与该解释相容」只对盈亏平衡一腿成立(实际利率+11bp相左); HY_OAS 证伪阈值 4.61 过松; TR2 环1 观察事实未写明裁定所依据的窗内方向(SPX -5.51% 对 USDJPY +1.82%); 「7天逆回购利率窗内无变动/持平」未带观测止点(末观测 2026-10-30, 其后缺观测; 已在质量注记与走位披露, 结论另有新锚逐日观测支持)。"
           "NIT 4: 两处引用标签日期为观测月末(已披露); 「回到降息前水平」宜写明 2025-12 降息; 「SPX 8.03、NIKKEI225 22.47、DAX 9.93」缺百分号且 HY_OAS 单位写作 pp; 未引日本央行 2026-10-30 维持决议条目。"
           "契约验证 14 条判定、16 条六查、地图核对均 VERIFIED; 语义席位未唤起, 读者报告为裁决缺席态。程序性披露: 只读阅读了规划器的发布规则表与同步面函数; 一次检索回显了 tests/ 下文件的截断行(未采用); 受审文件在审计期间未变(哈希与规范化比对一致)。"),
 "items": [
  {"severity": "MAJOR", "where": "agent_judgment.json /l4/scenarios[1]/rows/falsification/threshold(SCN2 失效阈值依据句); MAP_REPORT.md 第227行; FULL_REPORT.md 第101行; report.md 第109行",
   "note": "算术错: series_store BEI_10Y@2020-11-30=1.77、@2026-11-20=2.15, 差为38个基点; 35个基点是最新读数距阈值1.8的距离, 句中两个距离混用",
   "original": M1_O, "fix": M1_F},
  {"severity": "MAJOR", "where": "agent_judgment.json /reader_map/turnings[0]/first_mover; MAP_REPORT.md 第235行",
   "note": "方向与证据相左: series_store CN_PPI_YOY 2026-07 由 4.1 回落至 3.5, 低点后并非逐月连升(2025-12至2026-10: -1.9/-1.4/-0.9/0.5/2.8/3.9/4.1/3.5/3.8/5.0/5.7); 与同档 TR1 环1「2026-07回落至 3.5 后升至 5.7」自相矛盾; 低点月 2025-11 本身正确, 转折结论不变",
   "original": M2_O, "fix": M2_F},
  {"severity": "MAJOR", "where": "agent_judgment.json /reader_map/turnings[1]/first_mover; MAP_REPORT.md 第236行",
   "note": "与引擎面相左: AGENT_SEAT_ENVELOPE.json /reader_map_contract/engine_faces/turning_candidates_top9 首行为 CN_PPI_YOY(2026-02→2026-05, -0.9→3.9, 增量4.8, 通胀维); CN_PMI_MFG 增量3.4005 居全体第2、增长维首位; MAP_REPORT.md 第241-252行候选面表同序; 两行增量由 series_store 直算相符",
   "original": M3_O, "fix": M3_F},
  {"severity": "MINOR", "where": "agent_judgment.json /l3/contradictions[0]/competing_explanations[1]; FULL_REPORT.md 第69行; report.md 第76行",
   "note": "「近1个月分解(实际+11bp、盈亏平衡-19bp)与该解释相容」: 解释B 预期 TIPS_10Y 转平或回落, 实际利率+11bp 与该腿相左, 仅盈亏平衡一腿相容; 与 TR1 环3「尚不能区分」不一致。建议改为「…与该解释的盈亏平衡一腿相容、与实际利率一腿相左, 整体仅部分相容」",
   "original": "近1个月分解(实际+11bp、盈亏平衡-19bp)与该解释相容", "fix": "近1个月分解(实际+11bp、盈亏平衡-19bp)与该解释的盈亏平衡一腿相容、与实际利率一腿相左, 整体仅部分相容"},
  {"severity": "MINOR", "where": "agent_judgment.json /l3/mechanism_chains[0]/links[3](证伪观察); /reader_map/transmission[0]/links[2]",
   "note": "证伪阈值 HY_OAS 升破序列高点 4.61 可观测但在场值 3.52 距其 109bp, 作为区分指标过松; 建议增设预警级(如升破 2025-05-09 的 3.53, 即库内上一次不低于最新读数的水平), 失效级保留 4.61",
   "original": "", "fix": ""},
  {"severity": "MINOR", "where": "agent_judgment.json /reader_map/transmission[1]/links[0]/observed_fact",
   "note": "裁定「支持竞争解释」所依据的窗内方向未写入该环观察事实(2026-10-23→2026-11-23 SPX -5.51% 对 USDJPY +1.82%); 日频对数收益相关 0.19、同向 16/21 日、SPX 下跌 12 日中 USDJPY 下跌 9 日亦未披露; 席位复算支持现有裁定, 仅属披露改进",
   "original": "", "fix": ""},
  {"severity": "MINOR", "where": "agent_judgment.json /reader_map/headline_conclusion; /l3/contradictions[2]/statement; MAP_REPORT.md 一句总判断节(第10行起)",
   "note": "「7天逆回购利率与LPR窗内无变动」「CN_LPR_1Y 与 7天逆回购利率窗内持平」未带观测止点: series_store CN_OMO_7D 末观测 2026-10-30(其后至截止日无观测, 滞后 24 天), ECB_MRO/ECB_DFR 末观测 2026-09-16; 质量注记④⑤与四地走位已披露过期与降级, 「未跟进加息」另有新锚 CN_POLICY_OVERNIGHT 1.25 自 2026-11-02 至 2026-11-23 的逐日观测支持, 结论不变; 建议括注「(7天逆回购末观测 2026-10-30, 其后缺观测)」, 避免把缺席读成无变化",
   "original": "", "fix": ""},
  {"severity": "NIT", "where": "agent_judgment.json /l3/contradictions[0]/evidence_refs; /l3/contradictions[2]/evidence_refs; /l3/mechanism_chains[0]/links[0]/evidence_refs",
   "note": "引用标签 CN_PPI_YOY@2026-10-31、CN_CPI_YOY@2026-10-31 的日期为观测月末, 序列观测日为 2026-10-01; 质量注记④已披露, 建议统一为序列观测日",
   "original": "", "fix": ""},
  {"severity": "NIT", "where": "agent_judgment.json /l3/contradictions[0]/statement",
   "note": "「DFF 回到降息前水平」宜写明「回到 2025-12 降息前水平(3.88)」; 2025-10-30 降息前 DFF 为 4.12(2025-10-29)",
   "original": "", "fix": ""},
  {"severity": "NIT", "where": "agent_judgment.json /l3/mechanism_chains[0]/links[3]/text",
   "note": "「SPX 8.03、NIKKEI225 22.47、DAX 9.93」缺百分号; HY_OAS 水平单位写作「3.52pp」(利差常以 % 或基点计)",
   "original": "", "fix": ""},
  {"severity": "NIT", "where": "agent_judgment.json /l4/scenarios[0](SCN1); /l3/mechanism_chains[1]/links[0]",
   "note": "冻结发布日历另有日本央行 2026-10-30 维持决议(目标 1.25)条目, 判断档仅引 2026-09-18 决议; 「日央行维持收紧倾向」可补引",
   "original": "", "fix": ""}
 ],
 "must_fix": [
  "MAJOR-1 (agent_judgment.json /l4/scenarios[1]/rows/falsification/threshold; MAP_REPORT.md 第227行; FULL_REPORT.md 第101行; report.md 第109行): 「%s」 → 「%s」" % (M1_O, M1_F),
  "MAJOR-2 (agent_judgment.json /reader_map/turnings[0]/first_mover; MAP_REPORT.md 第235行): 「%s」 → 「%s」" % (M2_O, M2_F),
  "MAJOR-3 (agent_judgment.json /reader_map/turnings[1]/first_mover; MAP_REPORT.md 第236行): 「%s」 → 「%s」" % (M3_O, M3_F)
 ],
 "counterexamples_sought": [
  "反方攻击 1 (C1/M1 环4): 以近月资产收缩补全链条, 而全年窗股指上涨(SPX +8.03%、NIKKEI225 +22.47%、DAX +9.93%), 第四腿与全年证据相左 → 判断在 C1 句内与 M1 环4 明示资产收缩属近月窗口事实并列两窗对照, 攻击被披露吸收, 不构成隐瞒",
  "反方攻击 2 (C1 解释B): 解释B 预言 TIPS_10Y 转平或回落, 而近1个月实际利率 +11bp, 「与该解释相容」不成立 → 攻击部分成立, 记 MINOR-1(仅盈亏平衡一腿相容)",
  "反方攻击 3 (C1): 「DFF 回到降息前水平」只对 2025-12 降息成立, 2025-10-30 降息前 DFF 为 4.12 → 十二个月窗内唯一降息为 2025-12, 窗内口径成立, 记 NIT-2",
  "反方攻击 4 (C2): 2025-03 相似段的事后窗与本轮早段重叠, 以其为相似证据等于把本轮自身当证据 → 判断在样本注记与 SCN2 明示「样本非独立」, 攻击被披露吸收",
  "反方攻击 5 (C3): 换锚(7天逆回购 1.4 → 隔夜 1.25)本身是政策动作, 「窗内持平」掩盖了换锚 → 判断在 C3、TR1 环2 与质量注记⑤披露换锚且新锚自首观测起持平, 「未跟进加息」在两种口径下均成立, 攻击不成立",
  "反方攻击 6 (M1 环2): 收紧发生在通胀见顶(2026-05)之后, 「通胀迫使收紧」的时序支持弱 → 判断自述决议前可见通胀低于高点、动机环证据减弱并标 E3 假设, 攻击被披露吸收",
  "反方攻击 7 (M1 环4): 证伪阈值 HY_OAS 4.61 为序列历史高点, 距最新 3.52 达 109bp, 几乎不可触发 → 阈值在证据面可观测, 不构成 MAJOR; 作为区分指标过松, 记 MINOR-2",
  "反方攻击 8 (M2/TR2): 日本月均利率自 2025-12 已上调, 早于美欧通胀共振(2026-02), 更像独立正常化进程; 且日频上 SPX 下跌 12 日中 USDJPY 下跌 9 日, 并非完全解耦 → 前者已作为 TR1 环2 竞争解释写明; 后者幅度极小(四个最大跌幅日 USDJPY 变动 -0.07%/+0.20%/-0.08%/-0.06%)且窗内 USDJPY +1.82%, 裁定「支持竞争解释」成立, 观察事实披露不足记 MINOR-3",
  "反方攻击 9 (MAJOR 定级): 三处偏离是否应为 MINOR(不改变结论) → 逐一对照规程第5节: MAJOR-1 为数字错(35 对 38), MAJOR-2 为方向词与证据相左且与同档文字矛盾, MAJOR-3 为排序陈述与引擎面及读者报告表格相左, 均属条文所列 MAJOR 情形; 均有证据面数字可成立的改句, 按「REVISE 不留情」如实定级"
 ],
 "recompute_points": 1111,
 "recompute_mismatches": 8,
 "mismatch_details": [
  {"id": "MAJOR-1", "script": "s13_rates_assets.py / s26_final.py", "point": "l4.scenarios[SCN2].falsification.threshold: 1.77 较最新 2.15 低多少个基点", "mine": 38, "claim": 35, "counted_twice": True, "class": "MAJOR"},
  {"id": "MAJOR-2", "script": "s11_monthly.py / s26_final.py", "point": "reader_map.turnings[0]: 中国 PPI 低点后是否逐月连升(月度下跌次数)", "mine": "False (2026-07 4.1→3.5, 下跌1次)", "claim": "True (连升, 0次)", "counted_twice": True, "class": "MAJOR"},
  {"id": "MAJOR-3", "script": "s26_final.py", "point": "reader_map.turnings[1]: 转折候选面全体首位指标", "mine": "CN_PPI_YOY (增量4.8; CN_PMI_MFG 居第2)", "claim": "CN_PMI_MFG (增量3.40)", "counted_twice": False, "class": "MAJOR"},
  {"id": "NIT-1a", "script": "s13_rates_assets.py", "point": "CN_PPI_YOY 最新序列观测日 对 引用标签日期", "mine": "2026-10-01", "claim": "2026-10-31", "counted_twice": False, "class": "NIT (质量注记④已披露)"},
  {"id": "NIT-1b", "script": "s13_rates_assets.py", "point": "CN_CPI_YOY 最新序列观测日 对 引用标签日期", "mine": "2026-10-01", "claim": "2026-10-31", "counted_twice": False, "class": "NIT (质量注记④已披露)"},
  {"id": "EO-1", "script": "s14_history.py", "point": "引擎同步面 2022-06 锚 中国政策格发布日", "mine": "2022-06-20", "claim": "2022-06-19", "counted_twice": False, "class": "引擎面规则观察(月末减11天), 不在判断档文字内, 前后值均3.7"}
 ],
 "audited_at": "2026-11-24"
}
out = os.path.join(d, "VERDICT-round1.json")
json.dump(v, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
back = json.load(open(out, encoding="utf-8"))
assert back["verdict"] in ("UPHELD", "REVISE") and back["overall"] == back["verdict"]
assert back["recompute_points"] == 1111 and back["recompute_mismatches"] == 8
assert sum(1 for i in back["items"] if i["severity"] == "MAJOR") == 3 and len(back["must_fix"]) == 3
print("VERDICT-round1.json valid; items=%d must_fix=%d" % (len(back["items"]), len(back["must_fix"])))
print("PROSE-round1.md bytes=%d" % len(prose.encode("utf-8")))
