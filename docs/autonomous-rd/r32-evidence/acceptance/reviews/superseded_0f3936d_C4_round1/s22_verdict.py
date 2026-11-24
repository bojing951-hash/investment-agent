#!/usr/bin/python3 -I
# s22_verdict.py — 按规程第 6 节结构生成 VERDICT-round1.json
# 用法: /usr/bin/python3 -I s22_verdict.py <out_s10_summary.json> <输出路径>
# 计数与偏离明细从主脚本输出 out_s10_summary.json 读入, 不手填。
import json, sys

summ_p, out_p = sys.argv[1:3]
summ = json.load(open(summ_p, encoding="utf-8"))

ORIG = ("同日收盘口径(2026-10-23→2026-11-20)近一月： 标普500指数下跌百分之九点三六、日经225下跌百分之九点九八、"
        "上证综指下跌百分之四点二五、DAX 下跌百分之一点五零、VIX 上涨百分之八十四点五二，两种口径下美日股指跌幅均相近。")
FIX = ("同日收盘口径(2026-10-23→2026-11-20)近一月： 标普500指数下跌百分之九点三六、日经225下跌百分之九点九八、"
       "上证综指下跌百分之四点二五、DAX 下跌百分之一点五零、VIX 上涨百分之八十四点五二；收盘口径下美日股指跌幅相近且深于中国与欧洲，"
       "但引擎窗(2026-10-23→2026-11-23，止于盘中快照)下标普500指数下跌百分之五点五一、日经225下跌百分之九点九八，"
       "两者相差约四点四七个百分点，并不相近，标普与上证综指(下跌百分之四点一一)的落差仅一点四零个百分点。")
WHERE_MAJOR = "agent_judgment.json → l3.contradictions[C4-EVIDENCE-BOUNDARY].statement 末句；渲染于 FULL_REPORT.md 第 73 行、report.md 第 95 行(MAP_REPORT.md 0 处)"

items = [
    {"severity": "MAJOR", "where": WHERE_MAJOR,
     "note": "「两种口径下美日股指跌幅均相近」与证据相左。冻结快照 series_store 直算: 引擎窗(2026-10-23→2026-11-23，止于盘中快照)SPX 7623.680176→7203.850098 = -5.51%，"
             "NIKKEI225 62693.16→56436.65(止于 2026-11-20) = -9.98%，相差 4.47 个百分点(约 1.81 倍)，不相近；"
             "只有收盘口径(→2026-11-20)SPX 6910.390137 即 -9.36% 对 NIKKEI225 -9.98%(差 0.62 个百分点)相近。"
             "同档传导第 3 环把引擎窗 SPX 与 SHCOMP(-4.11%)之间 1.40 个百分点的落差称作「不足两个百分点、该排序弱化」并裁「尚不能区分」，"
             "按同一尺度 4.47 个百分点的美日落差不能称相近；引擎窗下标普离上证综指比离日经更近。该句五个收盘口径数字本身无误，错在跨口径的比较结论。",
     "original": ORIG, "fix": FIX},
    {"severity": "MINOR", "where": "agent_judgment.json → reader_map.transmission[CH-POLICY-RATES-ASSETS].links[1].observed_fact；MAP_REPORT.md 第 186 行(复算清单 #183)",
     "note": "「最新 2.16(观测 2026-11-19)」是三利率共同交易日窗的窗末值；series_store.BEI_10Y 最新观测为 2.15@2026-11-20，"
             "同环 evidence_refs 引用的也是 BEI_10Y@2026-11-20，MAP 第 189、200 行引擎面显示 2026-11-20=2.15。两窗变动 -19bp / -11bp 无误，结论不变。",
     "original": "…12 个月窗(2025-11-19→2026-11-19)变动 -11bp，最新 2.16(观测 2026-11-19)——两个窗口盈亏平衡均回落…",
     "fix": "…12 个月窗(2025-11-19→2026-11-19)变动 -11bp，窗末 2.16(2026-11-19)，最新观测 2.15(2026-11-20)——两个窗口盈亏平衡均回落…"},
    {"severity": "MINOR", "where": "agent_judgment.json → quality_gate_notes[2]（证伪面；复算清单 #170）",
     "note": "「日历内仅有 FOMC 2026年10月会议纪要条目」出处标错。冻结日历 v1.5.0 共 18 条(美国数据发布停摆或改期 11 条、欧元区 HICP 3 条、日本央行政策 2 条、中国 LPR 2 条)，"
             "没有任何美国政策决议或会议纪要条目；纪要发布日 2026-11-18 出自 report.json → research_plan.policy_doc_facts[0](basis=user_directive)。"
             "同句前半「冻结日历无美国政策条目」正确，前后自相矛盾。日期本身无误(#169)，该注记不进三份报告。",
     "original": "…冻结日历无美国政策条目)，日历内仅有 FOMC 2026年10月会议纪要条目(2026-11-18 发布，纪要发布≠决议日)。",
     "fix": "…冻结日历无美国政策与纪要条目)，引擎政策文件面载 FOMC 2026年10月会议纪要 2026-11-18 发布(纪要发布≠决议日)。"},
    {"severity": "MINOR", "where": "agent_judgment.json → l3.contradictions[C3-GROWTH-LIMITED].statement 首句",
     "note": "「可判证据只显示各经济体状态延续，未见经济体之间的方向性分化」强于自列数据。series_store 直算: 美国实际 GDP 同比 2.1916%(2026Q1)→2.0657%(2026Q2) 回落，"
             "日本 GDP 同比 0.8→1.16 回升，美国 INDPRO 同比 1.2498→2.1497 上升；经济体之间确有小幅方向差异，只是幅度小、指标间不一致。"
             "小结「证据不足以单独成论」保守，与数据相容，不构成 MAJOR。",
     "original": "增长维： 可判证据只显示各经济体状态延续，未见经济体之间的方向性分化。",
     "fix": "增长维： 可判证据显示各经济体以状态延续为主，经济体之间仅有小幅方向差异(美国 GDP 同比小幅回落、日本回升、美国工业生产同比上升)，幅度小且指标间不一致。"},
    {"severity": "MINOR", "where": "agent_judgment.json → l3.contradictions[C2-INFLATION-DIVERGENCE].statement 首句；reader_map.headline_conclusion；对比 reader_map.turnings[1].follow_or_diverge / narrative(渲染于 MAP_REPORT.md 第 219 行)",
     "note": "C2 与标题写「三地读数方向同向」「方向上未见经济体之间的反向」「分化在水平而非方向」，转折面写「美日通胀方向分化」「日本通胀回升而美国核心通胀缓和，方向分化」，没有任何一句调和。"
             "两处窗口不同且各自写明: C2 = 三个月前锚到最新(美国核心CPI同比 2.4665→2.5658、日本全国 1.97→2.44 均升)；转折 = 2026-05→2026-08 美国核心CPI同比 2.8229→2.4462 回落，对 2026-06→2026-09 东京都 1.6→2.69 上行。不构成数字性矛盾。",
     "original": "通胀维： 三地读数方向同向(均高于三个月前)，分化体现在水平…",
     "fix": "通胀维： 三个月对照窗内三地读数方向同向(均高于三个月前)，分化体现在水平(转折面的美日通胀方向分化指 2026-05→2026-08 美国核心CPI同比回落对 2026-06→2026-09 东京都同比上行，窗口终点不晚于三个月前锚)…"},
    {"severity": "MINOR", "where": "agent_judgment.json → reader_map.transmission[CH-POLICY-RATES-ASSETS].links[0]、links[1] 的 face_off_verdict / competing_predicts / verdict_note；MAP_REPORT.md 第 199–200 行对质表",
     "note": "两环 face_off_verdict 均为「支持主解释」，强于证据: (a) 第 1 环竞争解释的预期「TIPS_10Y 不随政策分化系统性上行」不是「变动由通胀预期、估值与仓位驱动」的必然推论；"
             "(b) 12 个月窗内美国政策先降后升净 0(2025-12-11 -25bp、2026-09-17 +25bp)而 TIPS_10Y +102bp，政策归因有限；"
             "(c) 盈亏平衡回落(-19bp / -11bp)与「因通胀压力收紧且政策可信」相容，同窗通胀读数在走高(日本 1.97→2.44、美国 3.30→3.72、中国 PPI 3.5→5.7)；"
             "(d) 分解面只含美国国债(series_store 无日本、中国国债收益率序列)。verdict_note 已写明「裁定限于方向一致，幅度与归因保留」「该读法不与主解释冲突」「指标仅覆盖美国国债市场」，但该字段不进渲染，读者只见两个「支持主解释」。",
     "fix": "两环标签改为「方向一致、归因未定(尚不能区分)」，或把 verdict_note 的保留句并入可渲染字段；第 1 环竞争预期改为与竞争解释等价的表述。"},
    {"severity": "MINOR", "where": "agent_judgment.json → l4.scenarios[SCN-A-POLICY-DIVERGENCE-EXTENDS] / [SCN-B-POLICY-CONVERGES] 的 scenario / trigger / falsification；MAP_REPORT.md 第 212 行脚注",
     "note": "两情景方向互补但不穷尽、不自洽。以截止日读数(DFEDTARU 上限 4.0、JP_POLICY_RATE 2026-10 月均 1.227、CN_LPR_1Y 3.0)代入，两情景均未触发亦未证伪，「美日不再加码且中国不动」的平台态无归属；"
             "SCN-B 文本「或美国降回 3.75」不在其触发条件(以中国 LPR 下调为必要条件)与证伪条件内；SCN-B 触发用日本月均 ≤1.28，情景文本用「不再高于 1.227」；"
             "SCN-A 证伪只列上限回落至 3.75 以下或日本月均回落至 1.17 以下，不覆盖「上限停在 4.0、不再加码」的主要落空形态。"
             "三组阈值均为在库可观测序列，两情景均标【假设·非预测】，截止日未作认定，故不构成「证伪条件不可观测」。",
     "fix": "补平台态归属或明示两情景不穷尽；把「美国降回 3.75」写入 SCN-B 触发或删去；统一日本阈值；SCN-A 证伪增列「至 2027-02-28 DFEDTARU 上限未再上调」。"},
    {"severity": "MINOR", "where": "agent_judgment.json → l3.mechanism_chains[M2-CN-PPI-CPI-SCISSORS].links[1].missing_link_note",
     "note": "区分指标 CN_PPI_YOY 回落至 3.0 以下对两个分支(上游传导挤压利润 → 政策维持；PPI 向 CPI 传导 → 政策空间收窄)都没有区分力，PPI 回落只说明高位消退。"
             "series_store 直算 2026-07→2026-10: CN_PPI_YOY 3.5→5.7(+2.2 个百分点)，CN_CPI_YOY 0.5→0.7(+0.2 个百分点)，剪刀差由 3.0 扩至 5.0 个百分点。",
     "original": "…区分指标=CN_PPI_YOY(若三个月内 CN_PPI_YOY 回落至 3.0 以下，上游传导假设减弱)。",
     "fix": "…区分指标=CN_CPI_YOY 相对 CN_PPI_YOY： 若至 2027-02-23 前 CN_CPI_YOY 随 PPI 同向上行(剪刀差收窄)，传导分支增强；若 PPI 回落而 CPI 仍低位，挤压分支随前提消退；当前剪刀差由 3.0 扩至 5.0 个百分点，尚无传导迹象。"},
    {"severity": "MINOR", "where": "agent_judgment.json → l3.contradictions[C1-POLICY-DIVERGENCE].competing_explanations[0]；[C2-INFLATION-DIVERGENCE].competing_explanations[0]、[1]",
     "note": "C1 竞争解释(一)点名「能源价格」为共同冲击变量，该变量在 series_store 在场而判断档未对质，也未说明不对质的理由: WTI_F 87.06(2026-08-21)→82.02(2026-11-23) 即 -5.79%，"
             "BRENT_F 94.39→88.19 即 -6.57%，月度现货均价 WTI_SPOT_M 83.9(2026-08)→102.07(2026-10) 即 +21.66%。"
             "C2 两条解释所需的通胀分项(能源食品对服务工资)证据面没有，判断档未写明不可区分。事实结论不受影响。",
     "fix": "C1 对能源价格做一次对质或写明不对质的理由；C2 写明「本证据面无分项数据，两解释不可区分」。"},
    {"severity": "MINOR", "where": "对比 report.json → research_plan.point_values.cells[US_REAL_GDP / JP_REAL_GDP_YOY / JP_CPI_YOY].vintage_semantics 与 MAP_REPORT.md 第 255–260、267–268、280 行；判断档 l3 的 C2 / C3 与 reader_map.regions[US / JP].from_to、anchor_echo",
     "note": "美国实际 GDP、日本实际 GDP 同比、日本全国 CPI 同比共 6 个锚格在引擎面标为「事后回顾(最新修订值,非当时首发值)」，MAP 点值表逐格标「(事后回顾)」并有修订口径说明；"
             "判断档引用了这 6 个值(24408.011、24611.077、0.8、1.16、1.97、2.44)，全文不含「事后回顾」「最新修订值」。判断档没有把修订值称作当时首发值，不构成事后信息冒充；"
             "但三个月前锚的严格历史时点值可能是当期初值，判断档未转述该口径。",
     "fix": "在「证据与口径」注记补一句: 美国实际 GDP、日本实际 GDP 同比、日本全国 CPI 同比的锚格值为最新修订族(事后回顾口径)，三个月前锚的严格历史时点值可能为当期初值。"},
    {"severity": "NIT", "where": "agent_judgment.json → l3.contradictions[C1-POLICY-DIVERGENCE].statement 首句", "note": "「政策维是四地中方向最清晰的分化」: 欧元区政策序列缺席，实为可比三地，句末已自限；建议改「可比口径下三地中」。"},
    {"severity": "NIT", "where": "agent_judgment.json → l3.contradictions[C1-POLICY-DIVERGENCE].statement", "note": "「分化体现在中美、日中之间方向相反(收紧对未变)」: 「未变」不是反方向，建议改「分化体现在中美、日中之间(收紧对未变)」。"},
    {"severity": "NIT", "where": "agent_judgment.json → reader_map.turnings[0].first_mover", "note": "「…是其后持续收紧的起点」: 日本月均已在 2025-12、2026-01 两次上调(0.478→0.557→0.728)，2026-08 亦微降(0.978→0.977)；「起点」应限定为候选窗起点。"},
    {"severity": "NIT", "where": "agent_judgment.json → reader_map.regions[US].from_to(核心CPI 括号)", "note": "「核心CPI 同比 2.47%(2026-07 月)→最近有效 2.57%(2026-09；指数 336.789→339.9；发布 2026-08-13→2026-11-13…)」: 括号内同比期(2026-09)、指数期(2026-10)与发布日分属三个时点，建议分开写。"},
    {"severity": "NIT", "where": "agent_judgment.json → l3.mechanism_chains[M1-POLICY-RATES-ASSETS].links[2].text", "note": "原始浮点外露「19.450001→27.01」「19.450001→35.889999」(共 2 处)，同档传导第 3 环与「证据与口径」注记写 19.45→27.01、19.45→35.89。"},
    {"severity": "NIT", "where": "agent_judgment.json → quality_gate_notes[6]②", "note": "「本工单路径面未载净变动字段」对 AGENT_SEAT_ENVELOPE.json 成立(该文件内 net_bp 出现 0 次)，但 report.json → research_plan.point_values.cells[*].policy_window_path.net_bp 与 MAP_REPORT.md 第 121 行政策路径表载「净变动 +67bp(0.557→1.227)」；建议写明所指文件。"},
    {"severity": "NIT", "where": "agent_judgment.json → quality_gate_notes[0]", "note": "「席位常识为日本当日为勤劳感谢日休市，未经本轮证据面核实」: 已自标未核实；建议核实后保留或删去。"},
    {"severity": "NIT", "where": "agent_judgment.json → l3.mechanism_chains[M2-CN-PPI-CPI-SCISSORS].links[1].missing_link_note", "note": "「三个月内」未给具体日期(按截止日 2026-11-23 应为 2027-02-23 前后)。"},
]

must_fix = [
    "必修 1(位置: " + WHERE_MAJOR + ")。原句: 「" + ORIG + "」 → 改句: 「" + FIX + "」"
]

counter = [
    "反方攻击 1(C1): 中国「未变」可能失真——隔夜利率 2026-11-02 换锚本身是政策动作→未击穿: 判断档把「未变」限定于一年期 LPR(3.0→3.0)与七天逆回购(1.4→1.4)两个口径，并声明隔夜口径三个月对照不可得; 留 NIT(「四地中」应限为可比三地)。",
    "反方攻击 2(C1): 「同一周内的同步收紧」依赖引擎推定的美国决议日→未击穿: 冻结日历无美国政策条目，判断档明示决议日系按生效日前一日推定且不据此排序先后; DFEDTARU 3.75→4.0 的序列变更日 2026-09-17 直读成立，日本 2026-09-18 决议为日历实录，相隔两日。",
    "反方攻击 3(C1): 美国「收紧」是否成立——近一年先降后升净 0→未击穿: 三个月窗 +25bp 直算成立，近一年净 0 判断档已并列披露。",
    "反方攻击 4(C1): 竞争解释点名的「能源价格」在证据面可检验而未检验→部分击穿: series_store 内 WTI_F -5.79%、BRENT_F -6.57%、WTI_SPOT_M 2026-08→2026-10 +21.66% 在场，判断档未对质; 事实结论不受影响，定 MINOR。",
    "反方攻击 5(C2): 「三地读数方向同向」是否以相邻口径冒充，且美国核心CPI同比 2026-05→2026-08 已回落→未击穿结论，留 MINOR: 缺失基期如实标缺，以 2026-09 最近有效同比披露并写明观测月; 与转折面「美日通胀方向分化」的张力未调和。",
    "反方攻击 6(C3): 「未见经济体之间的方向性分化」是否与自列数据相左→部分击穿: 美国 GDP 同比 2.1916→2.0657 回落、日本 0.8→1.16 回升; 首句措辞强于数据，定 MINOR; 小结「证据不足以单独成论」与数据相容。",
    "反方攻击 7(C4): 「两种口径下美日股指跌幅均相近」是否与证据相左→击穿: 引擎窗 SPX -5.51% 对 NIKKEI225 -9.98%，差 4.47 个百分点(约 1.81 倍)，不相近; 仅收盘口径(-9.36% 对 -9.98%，差 0.62 个百分点)相近; 与同档传导第 3 环的尺度和「尚不能区分」裁定相左; 定 MAJOR。",
    "反方攻击 8(M1 第 1、2 环): 「支持主解释」是否超出证据→对裁定标签击穿，定 MINOR: 12 个月窗美国政策净 0 而 TIPS_10Y +102bp; 盈亏平衡回落与「因通胀压力收紧且政策可信」相容; 竞争解释的预期不是其必然推论; 分解面只含美国国债。窗变动与恒等式数值(-8 = +11 − 19; +91 = +102 − 11; 残差 0)直算无误。",
    "反方攻击 9(M1 第 3 环): 主解释预期「美日相近且深于中国」在引擎窗是否成立→未击穿: 引擎窗 SPX 与 SHCOMP 落差 1.40 个百分点，小于与 NIKKEI225 的 4.47 个百分点，判断档已如实裁为「尚不能区分」并并列两口径。",
    "反方攻击 10(M2): 区分指标 CN_PPI_YOY 回落至 3.0 以下能否区分两个分支→击穿，定 MINOR: PPI +2.2 个百分点对 CPI +0.2 个百分点(2026-07→2026-10)才是对质证据; 第 1 环读数与缺环披露如实。",
    "反方攻击 11(历史类比): 取零段是否为回避→未击穿: 类比面特征与事后窗全部为美国序列，增长维覆盖率 0.17，信用维在有效候选上无有效特征，零段理由逐项可复算。",
    "反方攻击 12(L4 情景): 两情景是否互斥穷尽、阈值是否可观测→部分击穿，定 MINOR: 截止日读数代入两情景均未触发亦未证伪，粗网格 32 态中 12 态四类判据均不命中; SCN-B 文本「或美国降回 3.75」不在其触发与证伪条件内; 三组阈值均为在库可观测序列，不构成「证伪条件不可观测」。",
    "反方攻击 13(交付定性): 判断档自称「草稿、不可交付」是否与引擎面一致→未击穿: FULL_REPORT.md 载 blocked_class = map_core_dimension_missing、可交付 = False; report.json semantic_review.required = True、seat_invoked = False; 缺席格恰为 EA × 增长 / 通胀 / 政策。",
    "反方攻击 14(数值面): 是否存在事后信息、缺基期同比或相邻口径冒充→未击穿: 全文 YYYY-MM-DD 形式日期去重 39 个，晚于 2026-11-23 的只有情景期限 2027-02-28; 88 条序列末观测均不晚于截止日; 23 个同比点基期全部为去年同月/同季，美国 2026-10 CPI 同比如实标缺; 35 个锚格发布日逐格复算一致。",
]

notes = (
    "零上下文语义审查席 Round-1 裁决: REVISE。只读复算计数点 297(规程最低 90)，偏离 3 条(MAJOR 1 / MINOR 2)；"
    "另记引擎面自洽、渲染观察与对照事实 7 项，不计入计数。"
    "MAJOR 1 条: C4-EVIDENCE-BOUNDARY 陈述末句「两种口径下美日股指跌幅均相近」与证据相左——冻结快照 series_store 直算，"
    "引擎窗(2026-10-23→2026-11-23，止于盘中快照)标普500指数 7623.6802→7203.8501 为 -5.51%，"
    "日经225(止于 2026-11-20 收盘)62693.16→56436.65 为 -9.98%，相差 4.47 个百分点(约 1.81 倍)；"
    "只有收盘口径(2026-10-23→2026-11-20)两者 -9.36% 对 -9.98% 相近。"
    "同档传导第 3 环把引擎窗美中 1.40 个百分点的落差称作「不足两个百分点、排序弱化」并裁「尚不能区分」，C4 末句与之自相矛盾；"
    "该句已渲染进 FULL_REPORT.md 第 73 行与 report.md 第 95 行。必修 1 条: 改为「收盘口径相近、引擎窗不相近」的表述。"
    "计入偏离的 MINOR 2 条: 盈亏平衡「最新 2.16(观测 2026-11-19)」实为共同交易日窗末值，序列最新观测为 2.15@2026-11-20；"
    "「日历内仅有 FOMC 2026年10月会议纪要条目」出处标错(冻结日历 v1.5.0 的 18 条里没有美国政策或纪要条目，纪要来自 research_plan.policy_doc_facts)。"
    "另有 MINOR 7 条与 NIT 8 条，不计入计数: C3 首句「未见方向性分化」强于自列数据(美国 GDP 同比 2.19→2.07 回落、日本 0.8→1.16 回升)；"
    "C2「分化在水平而非方向」与转折面「美日通胀方向分化」未调和(两处窗口不同且各自写明)；"
    "传导第 1、2 环「支持主解释」标签强于证据、保留意见只在未渲染的 verdict_note；两情景的触发与证伪判据不穷尽、不自洽(阈值均可观测)；"
    "M2 区分指标 CN_PPI_YOY 无区分力；C1、C2 的竞争解释未对质也未标注不可判；"
    "美国 GDP、日本 GDP 同比、日本 CPI 同比共 6 个锚格的「事后回顾(最新修订值)」口径未进判断档文字。"
    "其余复算一致: 35 个锚格的值与发布纪律、23 个同比点基期、政策面口径与日历实录、三利率恒等式与两窗变动、资产窗两口径数值、"
    "转折候选值与最大窗、类比面恒等与计数、情景阈值、证据引用与诚实缺席、契约 17 项判定、交付门缺口披露。"
    "六查对四条 L3 陈述与两条机制链逐条执行；反方攻击 14 次: 击穿 3 处(C4 末句定 MAJOR；M1 第 1、2 环裁定标签与 M2 区分指标定 MINOR)、部分击穿 3 处、未击穿 8 处。"
)

sev = [it["severity"] for it in items]
assert sev.count("MAJOR") == 1 and sev.count("MINOR") == 9 and sev.count("NIT") == 8, sev
assert summ["points"] == 297 and summ["mismatches"] == 3 and len(summ["mismatch_details"]) == 3
assert len(counter) == 14 and len(must_fix) == 1

doc = {
    "seat": "semantic-audit-seat",
    "reviewer": "independent-zero-context-seat-r32-c4-round1",
    "verdict": "REVISE",
    "overall": "REVISE",
    "notes": notes,
    "items": items,
    "must_fix": must_fix,
    "counterexamples_sought": counter,
    "recompute_points": summ["points"],
    "recompute_mismatches": summ["mismatches"],
    "mismatch_details": summ["mismatch_details"],
    "audited_at": "2026-11-24",
}
with open(out_p, "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=2)
    f.write("\n")
back = json.load(open(out_p, encoding="utf-8"))
assert list(back.keys()) == list(doc.keys())
print("written", out_p)
print("items:", {s: sev.count(s) for s in ("MAJOR", "MINOR", "NIT")}, "| points", back["recompute_points"], "| mismatches", back["recompute_mismatches"])
print("notes chars:", len(notes), "| counter:", len(back["counterexamples_sought"]), "| must_fix:", len(back["must_fix"]))
