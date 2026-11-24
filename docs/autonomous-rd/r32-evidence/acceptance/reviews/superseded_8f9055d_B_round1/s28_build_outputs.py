# 席位自写: 由叙事件 + 复算表 + 判断档原文拼装 PROSE-round1.md 与 VERDICT-round1.json
# 用法: /usr/bin/python3 -I s28_build_outputs.py <agent_judgment.json> <MAP_REPORT.md> <out_s19_table.md> <_prose_parts.md> <out_s19_points.json> <输出目录>
import json, sys, re, os

jud_path, map_path, table_path, parts_path, points_path, outdir = sys.argv[1:7]
jud = json.load(open(jud_path, encoding="utf-8"))
J = json.dumps(jud, ensure_ascii=False)
MAP = open(map_path, encoding="utf-8").read()
table = open(table_path, encoding="utf-8").read()
parts = open(parts_path, encoding="utf-8").read()
P = json.load(open(points_path, encoding="utf-8"))
rows = P["points"]
N = len(rows)
bad = [r for r in rows if r["ok"] is False]
M = len(bad)
n_major = sum(1 for r in bad if r["level"] == "MAJOR")
n_minor_counted = sum(1 for r in bad if r["level"] == "MINOR")
ntab = len([l for l in table.split("\n") if re.match(r"^\| \d+ \|", l)])
assert N == ntab == 214 and M == 3 and n_major == 2 and n_minor_counted == 1, (N, ntab, M)

# ---------- 判断档原文(逐字切片, 保证 原句 精确) ----------
TR = jud["reader_map"]["transmission"][0]["links"]
l0 = TR[0]
of = l0["observed_fact"]
C1 = jud["l3"]["contradictions"][0]["statement"]
QGN1 = jud["quality_gate_notes"][1]
ORIG1A = of[of.index("供给侧对账"):]
ORIG1B = C1[C1.index("供给侧读数对账见传导面第一环"):]
_a = QGN1.index("另 2 环("); _b = QGN1.index("×2", _a) + 2
ORIG2A = QGN1[_a:_b]
_a = of.index("——合竞争解释中"); _b = of.index("合主解释。", _a) + len("合主解释。")
ORIG2B = of[_a:_b]
assert l0["face_off_verdict"] == "尚不能区分" and ORIG1A.endswith("不改裁定。") and ORIG1B.endswith("【尚未验证】)。")
assert ORIG2A.startswith("另 2 环(") and ORIG2A.endswith("×2") and ORIG2B.startswith("——合竞争解释中") and ORIG2B.endswith("合主解释。")

FIX1A = ("供给侧对账(能源前提 vs 在场读数): 布伦特原油(BRENT_F)近三个月自 2026-08-19 的 91.62 至 2026-11-23 的 88.19 为 -3.74%"
         "(近一月 116.72→88.19 为 -24.44%,11-23 为盘中快照;近 12 个月 +38.86%),但该端点差来自窗末急跌: "
         "窗内先升至 2026-10-23 的 116.72(较窗启 +27.40%)、窗内高点 117.64(2026-10-30),窗内 68 个观测中 61 个不低于窗启值;"
         "按序列库日值计的月均 2026-07 84.51→2026-09 102.26(+21.0%)→2026-10 108.34(+28.2%),2026-10 月均较 2025-10 月均 63.95 高 69.4%"
         "——在本问所解释的 2026-09/2026-10 观测月,油价与两地通胀同向走高,不构成对「能源持续传导」的反向事实;"
         "油价回落发生在 11 月、晚于上述观测月(这些读数的发布日 2026-10-13 至 2026-11-16 的油价在 92.44 至 117.64 之间,均不低于窗启值 91.62),"
         "只对此后读数构成「能源基数消退」的同向前瞻事实【尚未验证】;该读数不在本环区分指标上,不改裁定。")
FIX1B = ("供给侧读数对账见传导面第一环(近三个月布伦特原油端点微降系窗末急跌所致;在通胀观测月口径下油价月均走高、与两地通胀同向,"
         "不构成对「能源持续传导」的反向事实,十一月回落仅为对此后读数的前瞻事实【尚未验证】)。")
FIX2A = ("另 2 环中, BEI_10Y 环两侧预期分立(走高或维持高位 对 走低或持平)且有在场观测(本问三窗方向一致向下、最新水平为十二个月窗内最低)，"
         "判断=支持竞争解释 ×1;TIPS_10Y 相对名义利率环两解释在该指标上预期方向不分立，判断=尚不能区分 ×1")
FIX2B = ("——按判断口径(预期分立且引擎面观测在场),本环区分指标上的在场观测支持竞争解释「走低或持平」、不合主解释「走高或维持高位」;"
         "两点限定如实注记: 竞争解释的另一半(通胀读数数月内自行回落)为前瞻含义,截至截止日尚未兑现"
         "(欧元区 2026-10 读数 4.0 为年内新高；美国 CPI 同比 2026-09 回升至 3.72，仍低于 2026-05 的 4.17);"
         "更早的通胀上行段(三个月窗 2026-02→2026-05) BEI_10Y 自 2026-02-27 的 2.25 升至 2026-05-04 的 2.50,合主解释,但属另一事件窗,不改本窗裁定。")
assert not re.search(r"[0-9]", FIX1B), "C1 陈述改句不得新增阿拉伯数字"
# FIX2B 中的数字必须全部已见于同环 observed_fact 原文(不引入新数字)
for num in re.findall(r"[0-9]+(?:-[0-9]{2}){0,2}(?:\.[0-9]+)?", FIX2B):
    assert num in of, num
_f2a = FIX2A.replace("另 2 环", "").replace("×1", "")
for _mid in ("BEI_10Y", "TIPS_10Y"):
    _f2a = _f2a.replace(_mid, "")
assert not re.search(r"[0-9]", _f2a), "FIX2A 不得新增数字(指标名除外)"
for s in (ORIG1A, ORIG1B, ORIG2A, ORIG2B):
    assert s in J

MC = jud["l3"]["mechanism_chains"][0]["links"]
S1 = jud["l4"]["scenarios"][0]["rows"]; S2 = jud["l4"]["scenarios"][1]["rows"]
t3 = MC[2]["text"]; _a = t3.index("若加息传导单一成立"); _b = t3.index("而股指已明显回落") + len("而股指已明显回落")
ORIG_MC = t3[_a:_b]
US = [r for r in jud["reader_map"]["regions"] if r["region"] == "US"][0]["from_to"]
HL = jud["reader_map"]["headline_conclusion"]
ORIG_MINOR_A = "美欧通胀同月抬升、月频证据先后未定"
ORIG_MINOR_B = MC[1]["missing_link_note"]
ORIG_MINOR_C = ORIG_MC
ORIG_MINOR_D = S1["scenario"] + " ‖ " + S2["trigger"]["condition"]
for s in (ORIG_MINOR_A, ORIG_MINOR_B, ORIG_MINOR_C, ORIG_MINOR_D.split(" ‖ ")[0], ORIG_MINOR_D.split(" ‖ ")[1]):
    assert s in J, s[:30]

# ---------- PROSE ----------
cut = table.index("## 反方攻击用直算")
tbl = table[:cut].split("\n", 2)[2].strip()      # 去掉表标题与空行
atk = table[cut:].split("\n", 1)[1].strip()
NITS = 11
rep = {"{{POINTS}}": str(N), "{{MISMATCH}}": str(M), "{{NITS}}": str(NITS), "{{TABLE}}": tbl, "{{ATTACKS}}": atk,
       "{{ORIG1A}}": "> " + ORIG1A, "{{FIX1A}}": "> " + FIX1A, "{{ORIG1B}}": "> " + ORIG1B, "{{FIX1B}}": "> " + FIX1B,
       "{{ORIG2A}}": "> " + ORIG2A, "{{FIX2A}}": "> " + FIX2A, "{{ORIG2B}}": "> " + ORIG2B, "{{FIX2B}}": "> " + FIX2B}
prose = parts
for k, v in rep.items():
    assert k in prose, k
    prose = prose.replace(k, v)
assert "{{" not in prose and "}}" not in prose
open(os.path.join(outdir, "PROSE-round1.md"), "w", encoding="utf-8").write(prose)

# ---------- VERDICT ----------
items = [
    {"severity": "MAJOR",
     "where": "agent_judgment.json reader_map.transmission[0].links[0].observed_fact「供给侧对账」句(MAP_REPORT.md 第120行);l3.contradictions[0](C1-INFL-SYNC).statement 末句括注",
     "note": "与证据面相左: 端点 -3.74%(2026-08-19 的 91.62→2026-11-23 的 88.19)属实,但「三个月窗内油价微降…对「能源持续传导」前提为反向事实」不成立——窗内先升至 2026-10-23 的 116.72(较窗启 +27.40%)、窗内高点 117.64(2026-10-30),窗内 68 个观测中 61 个不低于窗启值;按 series_store.BRENT_F 日值计的月均 2026-07 84.51→2026-09 102.26(+21.0%)→2026-10 108.34(+28.2%),月均同比 2026-09 +51.4%、2026-10 +69.4%(2025-10 月均 63.95);所解释读数的发布日油价(2026-10-13 为 105.69、2026-10-16 为 109.86、2026-10-30 为 117.64、2026-11-13 为 95.84、2026-11-16 为 92.44)均不低于窗启值 91.62;回落发生在 11 月、晚于 2026-09/2026-10 观测月。观测月口径下油价与两地通胀同向走高。出处: snapshot.series_store.BRENT_F;report.json research_plan.point_values.cells[*].anchors.*.publication_date 与 publication_basis(月末+13/+16 天规则)。",
     "original": ORIG1A + " ‖ " + ORIG1B,
     "fix": FIX1A + " ‖ " + FIX1B},
    {"severity": "MAJOR",
     "where": "agent_judgment.json reader_map.transmission[0].links[0].face_off_verdict(=尚不能区分)、quality_gate_notes[1](甲)、同环 observed_fact 子句(乙);MAP_REPORT.md 第137行对质表第1行",
     "note": "对质表 BEI_10Y 行裁定与该行观测不一致: 两侧预期分立(主解释「走高或维持高位」/ 竞争解释「走低或持平」)且观测在场(近 30 日 2.34→2.15 即 -19bp;本问三窗 -14/-19/-11bp;最新 2.15 为 12 个月窗内最低,窗内区间 2.15..2.50,出处 snapshot.series_store.BEI_10Y),观测合竞争解释、不合主解释,判断档自述「均合竞争解释「走低或持平」」,按读者报告自载判断口径(MAP 第141行: 预期分立且引擎面观测在场才可裁)应裁「支持竞争解释」;所持理由(竞争解释「通胀读数数月内自行回落」一半未兑现;更早的 2026-02→2026-05 上行段合主解释)分属另一指标的前瞻含义与另一事件窗。质量门注记把该环与「两解释在该指标上预期方向不分立」并述,与对质表该行两侧预期不符。C1 竞争解释 2 亦把近一月 BEI_10Y 走低写成与「市场未定价持续通胀」相容,与对质表裁定自相矛盾。",
     "original": ORIG2A + " ‖ " + ORIG2B,
     "fix": FIX2A + " ‖ " + FIX2B + " ‖ 同步改动: face_off_verdict「尚不能区分」→「支持竞争解释」;verdict_note 改为「本问三窗方向一致向下(三个月窗 -14bp、近一月 -19bp、12 个月窗 -11bp),均合竞争解释「走低或持平」、不合主解释「走高或维持高位」——支持竞争解释;竞争解释「通胀读数数月内自行回落」的一半尚未兑现(欧元区 2026-10 读数 4.0 为年内新高)与更早的 2026-02-27→2026-05-04 上行段合主解释,均作限定注记,不改本窗裁定。」(该字段不进渲染);MAP 第137行判断列随字段渲染。"},
    {"severity": "MINOR",
     "where": "agent_judgment.json reader_map.turnings[0..1];MAP_REPORT.md 第152、156–157、159行;无 turning_supplement",
     "note": "三条转折中 CPI@2026-05 与 EA_HICP_YOY@2026-05 为同维度同窗(2026-02..2026-05)同轮事件,独立事件只有两个;读者报告并项后 2 行,标题仍称「过去一年的三个转折」,并项与补选口径注所称补选行缺席。数值全部无误(复算表 #153–#161),按工单 produce 条款字面(不同指标-月、至少跨两维度)三条成立,故不升级。",
     "original": ORIG_MINOR_A,
     "fix": "建议以候选池中窗口不与已用窗重叠的增长维度候选补足第三转折: INDPRO 2025-11→2026-02 同比 1.7543→0.7972(Δ -0.9571,出处 report.json research_plan.turning_candidates.candidates),经 turning_supplement 写明谁先变/窗口/前后值;或在判断档内并项并明示只有两个独立事件。"},
    {"severity": "MINOR",
     "where": "agent_judgment.json l3.mechanism_chains[0](M1-JP-RATE-PATH).links[1].missing_link_note 与 text;FULL_REPORT.md 第70行",
     "note": "「无…(国债收益率)序列」在 series_store 面属实,但「缺环待采」不准确: 冻结快照事实面含 JGB2Y/JGB5Y/JGB10Y@2026-11-19 = 1.853/2.235/2.87(注册表在册、日频、quality_status=PASS,出处 snapshot.facts),与 UST_10Y@2026-11-19 = 5.04 可得单点利差 217.0bp;仅未入序列库历史与本问证据索引。",
     "original": ORIG_MINOR_B,
     "fix": "本问证据面未纳入日本套息持仓与日本国债收益率(快照事实面仅有 2026-11-19 点值 JGB 2/5/10 年 1.853/2.235/2.87,序列库无历史、未入证据索引),该环为【假设】;可核环节仅政策利率路径本身(E1)。"},
    {"severity": "MINOR",
     "where": "agent_judgment.json l3.mechanism_chains[0].links[2].text;FULL_REPORT.md 第71行",
     "note": "区分指标 USDJPY 的月变化未写出: 2026-10-23→2026-11-23 为 +1.82%(156.494→159.347),三个月 -0.13%(出处 snapshot.series_store.USDJPY)——这是对「应见 USDJPY 走低」最直接的反向观测;结论(传导方向证据不单一)不变且更稳。",
     "original": ORIG_MINOR_C,
     "fix": "…应见 USDJPY 走低与股指承压并存——当前 USDJPY 报 159.35、近一月(2026-10-23→2026-11-23)不降反升 1.82%(三个月 -0.13%),仍处高位(近 12 个月窗内约第 71 百分位)而股指已明显回落…"},
    {"severity": "MINOR",
     "where": "agent_judgment.json l4.scenarios[S1-INFL-STICKY].rows.scenario/falsification/trigger 与 [S2-INFL-FADE].rows.scenario/trigger/falsification;MAP_REPORT.md 第147–148行",
     "note": "阈值不闭合: S1 情景陈述「维持 3.5% 以上」而证伪阈值为「连续两个月低于 3.0%」(3.0–3.5 之间陈述不成立却未证伪);S2 陈述「回落至 3.0% 以下」而触发阈值为「≤3.4%」、证伪阈值为「均不低于 4.0%」(3.0–4.0 之间悬空)。证伪条件可观测、截止日读数相容(复算表 #167–#181),结论不受影响。",
     "original": ORIG_MINOR_D,
     "fix": "对齐阈值或写明缓冲带: S1 证伪阈值与情景陈述取同一界(或注明 3.0–3.5 为缓冲带);S2 触发阈值与情景陈述取同一界(或注明 3.0–4.0 为缓冲带)。"},
    {"severity": "NIT", "where": "agent_judgment.json reader_map.transmission[0].links[2].competing_explanation", "note": "把「仓位/流动性冲击」与「增长担忧」并列,而「TIPS_10Y 走低」的预期只对应增长担忧;competing_predicts 已只写「增长担忧主导」,两处宜对齐。", "original": TR[2]["competing_explanation"], "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json reader_map.regions[US].from_to;MAP_REPORT.md 第109行", "note": "失业率两锚 4.1 持平属实,中间路径 4.1、4.1、4.2、4.1(2026-09 为 4.2)未提及。", "original": "失业率 4.1%(2026-07)持平至 4.1%(2026-10)", "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json reader_map.headline_conclusion;MAP_REPORT.md 第13行", "note": "60/66 天依赖日历核验覆盖(止于 2026-10-30,距截止日 24 天);该限定正文有、总判断无。", "original": "距上次调整按生效日 60 天、按决议日 66 天", "fix": ""},
    {"severity": "NIT", "where": "美国走位与 C1 陈述中「缺上年同月基期观测」", "note": "属实;可进一步注明 2025-10 为序列库缺采(冻结日历保守界条目对 CPI/CORE_CPI/UNEMPLOYMENT 等给出 first_publish_on_or_after 2026-01-22),以免误读为去年同月未发布。", "original": "2026-10 同比因缺上年同月基期观测不可得", "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json l3.contradictions[0].competing_explanations[0]", "note": "「弱欧元」仅为【假设】;证据索引在场且可直算的 EURUSD@2026-11-23 = 1.093972 为 12 个月窗最低、三个月 -5.52%(2026-08-19→2026-11-23),可作在场证据引用(注明盘中快照)。", "original": "(弱欧元放大输入压力)", "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json l3.contradictions[0].statement", "note": "「水平高于美国」在最新可比月仅高 0.08 个百分点(3.8 对 3.7173),且 HICP 与 CPI 口径不同,宜注记幅度。", "original": "水平高于美国", "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json l3.contradictions[1].evidence_refs", "note": "未含 EA_REAL_GDP_YOY@2026-07-01,而陈述含欧元区 GDP 判断(走位面已引用),建议补入。", "original": "欧元区实际 GDP 同比读数在引擎点值面仅微幅变动(见走位对照)", "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json l3.contradictions[1].statement", "note": "对通胀用同比、对工业生产用水平口径: 同比口径下工业生产 +0.90 个百分点大于 CPI +0.41 个百分点,水平口径下 +0.22% 对 +1.40%;宜显式点明所用口径(走位面已披露基数效应)。", "original": "两地硬数据增长面大体平稳、并非本期主导变化", "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json l3.mechanism_chains[0].links[2].text", "note": "「USDJPY 仍处高位」可补序列库全史位置(2016-11-23 起 n=2601,现值为第 96.6 百分位),更能支撑「日元仍处低位」。", "original": "当前 USDJPY 仍处高位(近 12 个月窗内约第 71 百分位)", "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json reader_map.headline_conclusion 与 quality_gate_notes[0]", "note": "资产月窗取 2026-11-23 盘中快照(SPX 较 2026-11-20 收盘高 4.25%;收盘口径月变化标普500指数 -9.36%、VIX +84.52%),口径已披露;总判断可加一句「幅度对快照时点敏感」。", "original": "11-23 值为盘中快照(非收盘价)", "fix": ""},
    {"severity": "NIT", "where": "agent_judgment.json l3.contradictions[2].competing_explanations[0]", "note": "「下月月均应维持当前水平附近」无数值阈值,与竞争解释 2 不好区分,宜给出带宽。", "original": "下月月均应维持当前水平附近", "fix": ""},
]
for it in items:
    for part in it["original"].split(" ‖ "):
        assert part and part in J, (it["where"], part[:30])
    for k in ("severity", "where", "note", "original", "fix"):
        assert k in it
assert sum(1 for it in items if it["severity"] == "MAJOR") == 2
assert sum(1 for it in items if it["severity"] == "MINOR") == 4
assert sum(1 for it in items if it["severity"] == "NIT") == NITS

def r4(x):
    return round(x, 4) if isinstance(x, float) else x
mism = ["查%s | 出处键: %s | 直算: %s | 报告: %s | 级别: %s | 说明: %s" % (r["chk"], r["src"], json.dumps(r["calc"], ensure_ascii=False) if not isinstance(r["calc"], str) else r["calc"],
                                                                 json.dumps(r["rep"], ensure_ascii=False) if not isinstance(r["rep"], str) else r["rep"], r["level"], r["note"]) for r in bad]
must_fix = [
    "【MAJOR-1】原句(甲, 传导面第一环 observed_fact 末段): " + ORIG1A + " → 改句(甲): " + FIX1A + " ‖ 原句(乙, C1 陈述末句括注): " + ORIG1B + " → 改句(乙): " + FIX1B,
    "【MAJOR-2】原句(甲, quality_gate_notes[1] 片段): " + ORIG2A + " → 改句(甲): " + FIX2A + " ‖ 原句(乙, 同环 observed_fact 子句): " + ORIG2B + " → 改句(乙): " + FIX2B + " ‖ 同步改动: reader_map.transmission[0].links[0].face_off_verdict「尚不能区分」→「支持竞争解释」(MAP_REPORT.md 第137行判断列随渲染)。",
]
counter = [
    "反方攻击 1(C1): 美国最新同比是否以相邻月冒充→失败: 判断档明写 2026-10 同比因缺 2025-10 基期不可得,最近有效同比取 2026-09(直算 3.71725)。",
    "反方攻击 2(C1): 「欧元区幅度更大」是否成立→失败: 同月 2026-07→2026-09 欧元区 +0.90 个百分点、美国 CPI 同比 +0.41 个百分点;至各自最新欧元区 +1.10 个百分点。",
    "反方攻击 3(C1): 「2023-09 以来首个高于美国的可比月份」→失败: 同月可比 n=106,2023-10..2026-08 共 34 个月无一高于美国,2022-07..2023-09 共 15 个月全部高于美国;最新可比月 3.8 对 3.7173。",
    "反方攻击 4(C1): 「水平高于美国」的幅度→仅 NIT: 差距 0.08 个百分点,且 HICP 与 CPI 口径不同。",
    "反方攻击 5(C1): 「近三个月布伦特微降…对能源持续传导为反向事实」→成立(MAJOR-1): 窗内先升至 116.72(2026-10-23,+27.40%)、高点 117.64(2026-10-30),68 个观测中 61 个不低于窗启值;观测月月均 2026-09 102.26、2026-10 108.34(对 2026-07 +21.0%/+28.2%,同比 +51.4%/+69.4%);回落发生在 11 月、晚于观测月。",
    "反方攻击 6(C1): 对质表 BEI_10Y 行「尚不能区分」→成立(MAJOR-2): 预期分立且观测在场(三窗 -14/-19/-11bp,2.15 为 12 个月窗内最低),观测合竞争解释。",
    "反方攻击 7(C1): 「读数为年内新高」「headline 强于核心」→失败: EA_HICP_YOY 2026-01..2026-10 最大值 4.0@2026-10;同比 3.72 对 2.57,水平 +1.40% 对 +0.92%。",
    "反方攻击 8(C2): 「并非本期主导变化」的口径→不成立为 MAJOR、列 NIT: 同比口径工业生产 +0.90 个百分点大于 CPI +0.41 个百分点,但水平口径 +0.22% 对 +1.40%,2026-10 环比 -0.43%、基数下行 0.66% 已披露。",
    "反方攻击 9(C2): 失业率「持平」→仅 NIT: 路径 4.1、4.1、4.2、4.1,两锚属实。",
    "反方攻击 10(C2): GDP「微降」与欧元区 GDP「微升」→失败: 2.19157→2.06574;1.19→1.28;过期已按同一口径披露。",
    "反方攻击 11(C2): 工业生产「单月波动/基数效应」竞争解释→失败: 环比 2026-08 -0.07%、2026-09 +0.73%、2026-10 -0.43%,与判断档两种解释并列相容,未偏袒。",
    "反方攻击 12(C3): 「官方目标与市场月均相互印证」→失败: 2026-10 月均 1.227 低于目标 1.25 仅 2.3bp 且为生效后首个整月;2026-09 月均 1.043 介于 0.977 与 1.25 之间。",
    "反方攻击 13(C3): 60/66 天与 +75bp/+67bp→失败: 2026-09-24→11-23 为 60 天、2026-09-18→11-23 为 66 天;0.478→1.227 为 +74.9bp(六变动点之和 75.1bp),0.557→1.227 为 +67.0bp。",
    "反方攻击 14(C3): 「2026-10-30 确认维持之后无新条目」→仅 NIT: 日历核验覆盖止于 2026-10-30,判断档已写「下月是否有新决议尚未验证」。",
    "反方攻击 15(M1): 「应见 USDJPY 走低」→部分成立(MINOR-C): 近一月 +1.82%(156.494→159.347)、三个月 -0.13%,判断档只给水平百分位未给月变化;结论不变。",
    "反方攻击 16(M1): 「无日美利差序列」「缺环待采」→部分成立(MINOR-B): series_store 确无,但快照事实面含 JGB 2/5/10 年@2026-11-19 = 1.853/2.235/2.87。",
    "反方攻击 17(M1): NIKKEI225 -9.98% 是否被单一归因、第 71 百分位是否属实→失败: 写成混合态并标 E2【假设】;2025-11-23..2026-11-23 n=259,第 70.7–71.0 百分位。",
    "反方攻击 18(传导面): 其余两环裁定→失败: 环 2 预期未分立裁「尚不能区分」合规;环 3 TIPS_10Y +22bp 与 SPX -5.51% 同现裁「支持主解释」一致。",
    "反方攻击 19(通用): 截止日纪律与事后信息→失败: 被引 19 个序列最后观测日、点值格发布日(最大 2026-11-16)、政策条目与纪要日均不晚于截止日;历史类比零段。",
    "反方攻击 20(通用): 缺基期给同比、相邻口径冒充、证伪条件不可观测→失败: 见复算表 ③④⑪⑨;仅情景阈值不闭合列 MINOR-D。",
]
notes = ("裁决 REVISE。只读面独立直算 214 点(冻结快照 series_store/facts/gate_a、冻结日历与注册表、report.json 引擎面),与受审判断档及读者报告文字逐点比对: "
         "命中 211、偏离 3(MAJOR 2 + MINOR 1);另有不计入偏离的 MINOR 3 项与 NIT 11 项。数字面整体扎实: 截止日与时点、18 个锚格、全部同比与缺基期标注、"
         "日本央行决议日/生效日/目标值与 60/66 天、三利率分解恒等与三窗、资产月窗、转折数值、政策三口径分列、Gate A 与 STALE 披露均逐点一致,"
         "无缺基期给同比、无相邻口径冒充、无事后信息冒充当时可知。必修两条: (1) 传导面第一环与 C1 陈述括注把「近三个月布伦特端点 -3.74%」写成对「能源持续传导」的反向事实,"
         "与证据面相左——窗内油价先升至 2026-10-30 的 117.64(较窗启 +28.40%)、窗内 68 个观测中 61 个不低于窗启值,所解释的 2026-09/2026-10 观测月油价月均较 2026-07 高 21.0%/28.2%"
         "(同比 +51.4%/+69.4%),回落发生在 11 月、晚于观测月,观测月口径下油价与两地通胀同向;改句已给出(C1 括注改句不新增阿拉伯数字)。"
         "(2) 对质表 BEI_10Y 行两侧预期分立且观测在场(近 30 日 -19bp、本问三窗 -14/-19/-11bp、最新 2.15 为 12 个月窗内最低),判断档自述「均合竞争解释」却裁「尚不能区分」,"
         "并在质量门注记中与「预期方向不分立」并述,与该行观测及读者报告自载判断口径(MAP 第141行)不一致,应裁「支持竞争解释」并如实注记两点限定(竞争解释另一半未兑现、更早事件窗合主解释)。"
         "MINOR: 三转折中两条为同轮事件、读者面并项后仅两个独立事件且无补选;机制链称日债收益率「缺环待采」而快照事实面已有 2026-11-19 点值;USDJPY 区分指标近一月 +1.82% 未写出;"
         "两情景触发/证伪阈值与情景陈述不闭合(3.0–3.5 与 3.0–4.0 空档)。所有改句均以证据面数字成立。")
verdict = {
    "seat": "semantic-audit-seat",
    "reviewer": "independent-zero-context-seat-r32-b-round1",
    "verdict": "REVISE",
    "overall": "REVISE",
    "notes": notes,
    "items": items,
    "must_fix": must_fix,
    "counterexamples_sought": counter,
    "recompute_points": N,
    "recompute_mismatches": M,
    "mismatch_details": mism,
    "audited_at": "2026-11-24",
}
out = os.path.join(outdir, "VERDICT-round1.json")
json.dump(verdict, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
back = json.load(open(out, encoding="utf-8"))
assert back["verdict"] in ("UPHELD", "REVISE") and back["recompute_points"] == 214 and back["recompute_mismatches"] == 3
assert len(back["must_fix"]) == 2 and len(back["counterexamples_sought"]) >= 4
print("OK points=%d mismatches=%d major=%d minor=%d nit=%d counter=%d | prose_lines=%d verdict_bytes=%d" % (
    N, M, 2, 4, NITS, len(counter), prose.count("\n") + 1, os.path.getsize(out)))
