#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit-R32 / T3 / Round-1 独立语义审查席 —— 产出生成器。

usage: /usr/bin/python3 -I s30_write_outputs.py <agent_judgment.json> <MAP_REPORT.md> <report.md> <OUT_DIR>

只读输入: agent_judgment.json(受审对象;逐字抽取 original 句,带在场断言)、读者报告两件(仅用于数字出处核对);
          OUT_DIR/recompute_table.json、OUT_DIR/recompute_supplement.json(本席复算结果)。
只写输出: OUT_DIR/PROSE-round1.md、OUT_DIR/VERDICT-round1.json。
"""
import json
import os
import re
import sys

AJ_P, MAP_P, REPMD_P, OUT = sys.argv[1:5]
with open(AJ_P, "r", encoding="utf-8") as fh:
    aj = json.load(fh)
with open(os.path.join(OUT, "recompute_table.json"), "r", encoding="utf-8") as fh:
    TBL = json.load(fh)
with open(os.path.join(OUT, "recompute_supplement.json"), "r", encoding="utf-8") as fh:
    SUPP = json.load(fh)
ROWS = TBL["rows"]
T = {r["id"]: r for r in ROWS}
with open(MAP_P, "r", encoding="utf-8") as fh:
    MAP_TEXT = fh.read()
with open(REPMD_P, "r", encoding="utf-8") as fh:
    REPMD_TEXT = fh.read()

RM = aj["reader_map"]
REGI = {r["region"]: r for r in RM["regions"]}
TR = RM["transmission"][0]["links"]
TN = RM["turnings"]
ML = aj["l3"]["mechanism_chains"][0]["links"]
QGN = aj["quality_gate_notes"]
CST = {c["id"]: c["statement"] for c in aj["l3"]["contradictions"]}
S = {s["id"]: s["rows"] for s in aj["l4"]["scenarios"]}
JTDUMP = json.dumps(aj, ensure_ascii=False)


def sub(text, start, end=None):
    """逐字抽取 [start .. end](含) 子串;start/end 不在场即报错。"""
    i = text.index(start)
    if end is None:
        return text[i:]
    j = text.index(end, i)
    return text[i:j + len(end)]


def fmt(x, nd=2):
    return ("%." + str(nd) + "f") % x


def f2(pid):
    return fmt(T[pid]["calc"])


def clip(s, n):
    s = str(s).replace("\n", " ").replace("|", "\\|")
    return s if len(s) <= n else s[:n] + "…"


# ---------------------------------------------------------------- 数值(全部来自复算表/补充面)
FED = SUPP["fed_band"]
CR = SUPP["eurjpy_synthetic_cross"]
CHW = SUPP["policy_changes_in_fx_window_2026-10-23_2026-11-23"]
UST = fmt(T["J07"]["calc"])
TU, TL = fmt(FED["DFEDTARU@2026-11-23"]), fmt(FED["DFEDTARL@2026-11-23"])
MRO = fmt(T["D01"]["calc"])
BOJ = fmt(T["D22"]["calc"])
C20, C23 = fmt(CR["chg_pct_to_2026-11-20"]), fmt(CR["chg_pct_to_2026-11-23"])
X0, X20, X23 = fmt(CR["EURJPY@2026-10-23"]), fmt(CR["EURJPY@2026-11-20"]), fmt(CR["EURJPY@2026-11-23"])
DIFF = fmt(abs(T["G21"]["calc"] - T["G42"]["calc"]))      # 欧元与日元对美元月窗变动幅度之差(至 2026-11-20)
assert UST == "5.04" and (TU, TL) == ("4.00", "3.75") and MRO == "2.65" and BOJ == "1.25"
assert (C20, C23) == ("-0.24", "-0.73") and (X0, X20, X23) == ("175.61", "175.19", "174.32")
assert CHW["Fed(DFEDTARU)"] == [] and CHW["ECB_MRO"] == [] and CHW["ECB_DFR"] == [] and CHW["BOJ_calendar"] == ["2026-10-30"]
assert T["D25"]["ok"] and T["D25"]["calc"] == 1.25          # 2026-10-30 会议后目标仍 1.25(维持)
# EA 谷底
assert T["F16"]["calc"].startswith("2026-01(1.7)") and T["F18"]["ok"]
JPUP = [x[0] for x in [("2025-08→2025-09",), ("2025-09→2025-10",)]]
assert T["F20"]["calc"] == 2

# ---------------------------------------------------------------- original / fix
# MAJOR-A
oA = sub(REGI["EA"]["from_to"], "路径: ", "近十二个月最高")
assert "2026-02 谷底 1.9→" in oA
fA = oA.replace("2026-02 谷底 1.9→", "2026-01 谷底 1.7→2026-02 1.9→")
# MAJOR-B
oB1 = TR[1]["face_off_verdict"]
fB1 = "尚不能区分"
oB2 = TR[1]["verdict_note"]
fB2 = ("本月窗两种口径(至 2026-11-20 收盘、至 2026-11-23 盘中快照)一致: 欧元与日元同对美元走弱并同向随美元指数;"
       "但主解释预期的『方向分立』未纳入美元端利率——引擎面美元端利率高于两地(UST_10Y 最新 " + UST + "%;"
       "快照序列面联邦基金目标区间 " + TL + "%–" + TU + "%,DFEDTARL/DFEDTARU@2026-11-23,不在本轮证据索引),"
       "利差主导解释对本月窗同样预期两货币对美元走弱,两解释在区分指标 EURUSD 上预期未分立——尚不能区分。"
       "置信有限: 仅一个月窗、窗内三地均无政策利率变动(BOJ 2026-10-30 会议为维持不变);"
       "EURJPY 交叉盘序列不在证据面,由同日 EURUSD×USDJPY 两腿合成的交叉盘至 2026-11-20 约 " + C20 + "%、"
       "至 2026-11-23 约 " + C23 + "%,幅度小,利差渠道未获检验亦未被否定。")
oB3 = sub(TR[1]["observed_fact"], "EURJPY 交叉盘不在证据面")
fB3 = ("EURJPY 交叉盘序列不在证据面,但可由同日 EURUSD×USDJPY 两腿合成: 由 2026-10-23 的约 " + X0 +
       " 降至 2026-11-20 的约 " + X20 + "(" + C20 + "%)、2026-11-23 盘中约 " + X23 + "(" + C23 + "%),"
       "幅度小,利差假说的直接检验(欧元相对日元走强)可做但不足以单独裁定。")
oB4 = ML[2]["text"].split("。")[0] + "。"
assert oB4.startswith("传导【假设】") and "获支持" in oB4 and "不可直接检验)。" in oB4
fB4 = ("传导【假设】: 若政策利差主导汇率,两地同向收紧但水平差(MRO " + MRO + "% vs BOJ 目标 " + BOJ + "%)应体现于 EURUSD/USDJPY 方向分立"
       "——但该预期未纳入美元端利率(UST_10Y 最新 " + UST + "%,高于 MRO " + MRO + "% 与 BOJ 目标约 " + BOJ + "%),"
       "利差主导对本月窗同样预期两货币对美元走弱;本月窗两口径下两货币同对美元走弱、同向随美元指数,"
       "两解释在该观测上预期未分立——尚不能区分(置信有限;EURUSD×USDJPY 合成交叉盘至 2026-11-20 约 " + C20 +
       "%,幅度小,利差渠道未获检验)。")
oB5 = sub(QGN[1], "传导三环")
fB5 = oB5.replace("支持竞争解释 1·尚不能区分 2", "支持竞争解释 0·尚不能区分 3")
assert fB5 != oB5
assert oB3 in TR[1]["observed_fact"] and oB4 in ML[2]["text"] and oB5 in QGN[1] and oA in REGI["EA"]["from_to"]
# MINOR originals
oa = "日本与欧元区通胀环境方向相反"
assert oa in RM["headline_conclusion"]
fa = "日本与欧元区通胀同比相比去年同月方向相反(较六个月前锚两地读数均上行)"
od = sub(oB2, "主解释的预期未纳入美元端利率", "5.04%)")
fd = ("随 MAJOR-B 改句处理: 明示 UST_10Y 为市场收益率口径;如需政策口径,引快照序列面联邦基金目标区间 " + TL + "%–" + TU +
      "%(DFEDTARL/DFEDTARU@2026-11-23)并标注「不在本轮证据索引」")
oe = QGN[3]
fe = oe.replace("证伪阈值与前提水平对齐(3.5%)",
                "S1 证伪阈值与前提水平对齐(3.5%);S2 证伪阈值(3.5%)较前提水平(3.0% 以下)放宽,3.0%–3.5% 区间不触发亦不证伪")
assert fe != oe
of = sub(CST["C2-POLICY-SYNC"], "2026-10-30 会议确认维持不变", "无生效变动)")
ff = of + ";日本端「收紧」方向依据月均市场利率台阶(JP_POLICY_RATE 2025-11 的 0.478 至 2026-10 的 1.227),实录无前值,属【推断】;2026-10-30 至研究截止 24 天内的后续决议面不在实录【尚未验证】"
og = sub(TR[2]["verdict_note"], "(b)", "58 天。")
assert og.endswith("。")
fg = og[:-1] + ";同页引擎面另列 FOMC 2026年10月会议纪要 2026-11-18 发布(纪要发布≠决议日),落在跳升窗内,属第三类候选驱动,本对质不裁。"
# 环 3 缺环注记须在场(正文引用其「方向留白不裁」)
MLN = ML[2]["missing_link_note"]
assert "方向留白不裁" in MLN
# NIT originals
on1 = "月频下谁先转折不可判"
assert on1 in TN[0]["follow_or_diverge"]
fn1 = "按谷底月欧元区(2026-01)先于日本(2026-02)一个月转入上行;按引擎候选面转折日则为日本(2026-02)先于欧元区(2026-05)——两种排序口径不同,以口径为准,不宜笼统写「不可判」"
on2 = "spliced"
assert on2 in ML[0]["text"]
fn2 = "拼接"
on3 = "自 2025-01 高点 4.03 持续回落"
assert on3 in ML[0]["text"]
fn3 = "自 2025-01 高点 4.03 回落(非逐月单调,2025-09、2025-10 两度小幅回升)"
on4 = sub(TR[2]["verdict_note"], "但其『快速回落』预期仅有一个盘中观测", "非收盘)")
fn4 = on4 + ";另: 同窗内 2026-11-05 冲高 28.18 后至 2026-11-11 收盘 17.49 已有一段与日/欧政策日历无关的冲高回落"

NPTS, NHIT, NMIS = TBL["points"], TBL["hits"], TBL["mismatches"]
MISS = [r for r in ROWS if not r["ok"]]
assert (NPTS, NHIT, NMIS) == (287, 280, 7), (NPTS, NHIT, NMIS)

ITEMS = [
    {"severity": "MAJOR", "where": "agent_judgment.json → reader_map.regions[region=EA].from_to「通胀环境」分句(MAP_REPORT.md 第 122 行同源渲染)",
     "note": "把 2026-02 的 1.9 写成谷底: 证据面近十二个月(2025-11..2026-10)、2026 年内、2025 年以来三个窗口的最小值均为 2026-01 的 1.7"
             "(series_store.EA_HICP_YOY[2026-01-01]=1.7、[2026-02-01]=1.9),且与本档 turnings[0]「欧元区 2026-01 的 1.7」及第 1 环「2026-01 的 1.7 升至」自相矛盾(复算点 F16–F18)。",
     "original": oA, "fix": fA},
    {"severity": "MAJOR", "where": "agent_judgment.json → reader_map.transmission[0].links[1].face_off_verdict(MAP_REPORT.md 第 148 行对质表 EURUSD 行)",
     "note": "对质第 2 环裁「支持竞争解释」越证: 主解释预言「EURUSD/USDJPY 方向分立」未纳入美元端利率(UST_10Y 最新 5.04%、快照序列面联邦基金目标区间 3.75–4.00%"
             ",均高于 MRO 2.65% 与 BOJ 目标约 1.25%;窗内三地无政策利率变动),利差主导对本月窗同样预期两货币对美元走弱——两解释在区分指标上预言同向、预期未分立,"
             "按读者报告自述口径「预期未分立=尚不能区分,不以单侧证据裁」(MAP_REPORT.md 第 151 行)应改裁;第 3 环同档自用「证据倾向竞争解释但不足以裁定,尚不能区分」标准(复算点 J02)。",
     "original": oB1, "fix": fB1},
    {"severity": "MAJOR", "where": "agent_judgment.json → reader_map.transmission[0].links[1].verdict_note",
     "note": "裁定理由须随 face_off_verdict 同改: 写明美元端利率在场与「预期未分立」,置信注记保留(复算点 J02、J03、J07、G42)。",
     "original": oB2, "fix": fB2},
    {"severity": "MAJOR", "where": "agent_judgment.json → reader_map.transmission[0].links[1].observed_fact 末句",
     "note": "「直接检验不可做」与证据面不符: EURUSD 与 USDJPY 两序列同快照同日观测俱在,可合成 EURJPY 交叉盘"
             "(2026-10-23 约 175.61→2026-11-20 约 175.19 即 -0.24%、2026-11-23 约 174.32 即 -0.73%);幅度小,结果略不利于「欧元相对日元走强」但不足以单独裁定(复算点 J03;补充面 eurjpy_synthetic_cross)。",
     "original": oB3, "fix": fB3},
    {"severity": "MAJOR", "where": "agent_judgment.json → l3.mechanism_chains[0].links[2].text 首句(report.md 第 76 行 E2 环;MAP_REPORT.md 机制链同源)",
     "note": "与对质第 2 环同一越证: 「方向分立未出现→竞争解释在本月窗获支持」不成立(理由同上);该环 missing_link_note 自述「方向留白不裁」,与环文相左(复算点 J02、J03)。",
     "original": oB4, "fix": fB4},
    {"severity": "MAJOR", "where": "agent_judgment.json → quality_gate_notes[1]",
     "note": "对质计数须随裁定同改(由 0/1/2 改为 0/0/3)(复算点 J01)。",
     "original": oB5, "fix": fB5},
    {"severity": "MINOR", "where": "agent_judgment.json → reader_map.headline_conclusion 首句(MAP_REPORT.md 第 12 行)",
     "note": "「通胀环境方向相反」仅就「相比去年同月」成立: 较六个月前锚两地读数同向上行(JP_CPI_YOY 1.38→2.44、EA_HICP_YOY 3.0→4.0)。数值与方向词无误,建议限定口径(复算点 J05、J06;补充面 six_month_anchor_direction)。",
     "original": oa, "fix": fa},
    {"severity": "MINOR", "where": "agent_judgment.json → reader_map.transmission[0].links[1].verdict_note 置信注记",
     "note": "以 UST_10Y(市场收益率)充当「美元端利率」与 MRO/BOJ 政策目标并列,口径不一;快照序列面有联邦基金目标区间 3.75–4.00%(DFEDTARL/DFEDTARU@2026-11-23)但不在本轮 60 行证据索引(复算点 J07;补充面 fed_band)。",
     "original": od, "fix": fd},
    {"severity": "MINOR", "where": "agent_judgment.json → quality_gate_notes[3]",
     "note": "「证伪阈值与前提水平对齐(3.5%)」只对 S1 成立;S2 前提为「回落至 3.0% 以下」而证伪阈值为 3.5%,3.0%–3.5% 区间既不触发亦不证伪(复算点 I08、I09)。",
     "original": oe, "fix": fe},
    {"severity": "MINOR", "where": "agent_judgment.json → l3.contradictions[C2-POLICY-SYNC].statement 日本分句",
     "note": "日本端核验覆盖止于 2026-10-30(距截止 24 天),未如欧央行 68 天缺口那样对称标注【尚未验证】;且实录(basis=user_directive)只有目标值 1.25、无前值,日本端「收紧」方向的依据是月均市场利率台阶,属推断而未标【推断】(复算点 D20–D28、D36–D38)。",
     "original": of, "fix": ff},
    {"severity": "MINOR", "where": "agent_judgment.json → reader_map.transmission[0].links[2].verdict_note (b) 句(MAP_REPORT.md 第 149 行)",
     "note": "时点论证只量了日/欧政策日;引擎面同页列有 FOMC 2026年10月会议纪要 2026-11-18 发布(research_plan.policy_doc_facts[0],MAP_REPORT.md 第 94 行),落在跳升窗 2026-11-13→2026-11-20 内,"
             "其后 VIX 24.56→28.44→35.89;判断档未援引亦未排除这一第三类候选驱动。裁定(尚不能区分)不受影响(复算点 J10;补充面 policy_doc_event_window)。",
     "original": og, "fix": fg},
    {"severity": "NIT", "where": "agent_judgment.json → reader_map.turnings[0].follow_or_diverge 末句(MAP_REPORT.md 第 166 行)",
     "note": "同句既写两地谷底月(欧元区 2026-01、日本 2026-02)与「先后转入上行」,又写「月频下谁先转折不可判」;按谷底月排序为欧元区先一个月,按引擎候选面转折日则为日本(2026-02)先——宜点明排序口径(复算点 F16、F23)。",
     "original": on1, "fix": fn1},
    {"severity": "NIT", "where": "agent_judgment.json → l3.mechanism_chains[0].links[0].text / quality_gate_notes[4](report.md 第 74 行)",
     "note": "「spliced」非注册表用语;注册表与事实行 calc 文本为「拼接(新基优先,重叠差>0.10pp 告警)」,括注内容逐字在场(复算点 N07、N08)。",
     "original": on2, "fix": fn2},
    {"severity": "NIT", "where": "agent_judgment.json → l3.mechanism_chains[0].links[0].text / reader_map.regions[JP].from_to",
     "note": "「持续回落」非逐月单调: 2025-08→09 2.72→2.91、2025-09→10 2.91→2.99 两处回升;端点 4.03/3.1/1.27 无误(复算点 C28–C30、F20)。",
     "original": on3, "fix": fn3},
    {"severity": "NIT", "where": "agent_judgment.json → reader_map.transmission[0].links[2].verdict_note",
     "note": "字面成立(11-20 收盘后仅 2026-11-23 一个盘中观测);但同窗内 2026-11-05 冲高 28.18 后至 2026-11-11 收盘 17.49 已有一段与日/欧政策日历无关的冲高回落,未援引(复算点 J04;补充面 vix_midwindow_episode)。",
     "original": on4, "fix": fn4},
    {"severity": "NIT", "where": "MAP_REPORT.md(引擎渲染)",
     "note": "读者页无 Gate A 总体状态行(全文 0 处 DEGRADED),仅 report.md 第 5 行披露「42/42 信封步非 OK(DEGRADED)」;判断档已逐项披露具体名单(复算点 K10)。",
     "original": "", "fix": ""},
]
MUST = ["%s| 原句: %s | 改句: %s" % (w, it["original"], it["fix"])
        for it, w in zip(ITEMS, ["MAJOR-A", "MAJOR-B(1/5)", "MAJOR-B(2/5)", "MAJOR-B(3/5)", "MAJOR-B(4/5)", "MAJOR-B(5/5)"])
        if it["severity"] == "MAJOR"]
assert len(MUST) == 6

COUNTER = [
    "反方攻击 1(C1): 「方向相反」或为基数效应假象——日本 2025-10(2.99)是局部高点、欧元区 2025-10(2.1)是局部低点,且较六个月前锚两地同向上行(1.38→2.44、3.0→4.0)→攻击部分成立: C1 陈述限定「相比去年同月」且数值逐位无误,但总判断「通胀环境方向相反」外延偏宽=MINOR-a。",
    "反方攻击 2(C1): 东京 CPI 2.73% 高于全国 2.44%,「日本回落」是否已过时→东京序列自 2026-01 起、无去年同月基期,同比对照不可判,判断档已如实写明且分列口径;全国同比对照事实无误→不成立。",
    "反方攻击 3(C2): 欧央行序列止于 2026-09-16(距截止 68 天)且冻结日历无 ECB 实录,「无未生效决议」不可断言→判断档已限定「仅覆盖引擎可见面【尚未验证】」→已防;但日本端 2026-10-30 后 24 天缺口未对称标注=MINOR-f。",
    "反方攻击 4(C2): 「同向收紧」对日本端是否超出证据(实录无前值)→方向依据为月均市场利率台阶(0.478→1.227,约 +75bp),属推断而未标【推断】=MINOR-f;水平值 1.25% 与日期无误。",
    "反方攻击 5(C3): 变更点序列「止于变更日」是常态而非数据缺口→判断档已并列「仅反映源端未再更新」一解并声明引擎面不可区分,契约 STALE 项亦已披露→不成立。",
    "反方攻击 6(M1 环 1): 「持续回落」是否属实→2025-01→2026-02 间两处逐月回升(2.72→2.91→2.99),非单调=NIT-3;端点与路径数值无误。",
    "反方攻击 7(M1 环 2): 欧央行决议日是否以引擎惯例冒充实录→已标【推断】,且 2026-06-11、2026-09-10 复算确为生效日前上一个周四→不成立。",
    "反方攻击 8(M1 环 3 / 对质第 2 环): 「方向分立未出现」即可裁支持竞争解释?→纳入美元端利率(UST_10Y 5.04%;快照序列面联邦基金目标区间 3.75–4.00%)后,两解释对 EURUSD/USDJPY 预言同向,预期未分立→攻击成立=MAJOR-B。",
    "反方攻击 9(M1 环 3 / 对质第 2 环): EURJPY 是否确实不可检验→同日两腿相乘可得(至 2026-11-20 -0.24%、至 2026-11-23 -0.73%),「不可做」不成立=MAJOR-B;幅度小,交叉盘结果本身不足以改裁任何一方。",
    "反方攻击 10(M1 环 4 / 对质第 3 环): 「距最近政策日 14 天」是否遗漏窗内政策事件→FOMC 2026年10月会议纪要 2026-11-18 发布落在跳升窗内,判断档未提及=MINOR-g;「14 天/58 天」对日/欧政策日数值无误,裁定不变。",
    "反方攻击 11(M1 环 4 / 对质第 3 环): 「快速回落」是否已有多个收盘证据→2026-11-20 收盘后仅 2026-11-23 一个观测且为盘中(纽约 09:53),字面成立;窗内另有未援引的 2026-11-05 冲高回落段=NIT-4。",
    "反方攻击 12(对质第 1 环): 等距等幅(相隔 91 天、各 25bp)是否已足以裁「程序驱动」→n=2,两次决议前可见读数(3.0/3.2、2.9/3.2)均高于 2026-02 的 1.9,读数驱动(含滞后)亦相容→「尚不能区分」成立。",
    "反方攻击 13(情景 S1/S2): 情景是否已触发或已被证伪→2026-11、2026-12 观测月读数按席位规则于 2027-01-16 / 2027-01-20 入档,截止日未发布;2026-10 读数 4.0 / 2.44 与两情景均相容→未触发、未证伪成立;S2 证伪阈值(3.5%)与前提(3.0% 以下)未对齐=MINOR-e。",
    "反方攻击 14(交付门缺口披露): 缺席是否被写成「无变化」、序列值是否冒充官方宣布目标→东京 CPI 写「同比对照不可判」,BOJ 月均 1.227% 与日历目标 1.25% 分列,JP_POLICY_TARGET 写「数据不可得/注册表无」→不成立。",
    "反方攻击 15(截止日纪律): 判断档是否引用截止日后信息→除情景期限 2027-02-15 外,正文无晚于 2026-11-23 的日期;判断书写时刻 2026-11-23T19:40:28Z 不晚于 attach 时刻 19:40:59Z→不成立。",
]

NOTES = ("独立复算 287 点(规程 §3 最低 90 点),命中 280、偏离 7(MAJOR 3 行归 2 类、MINOR 2、NIT 2),裁决 REVISE。"
         "工单四问核心数值全部吻合: 日本全国 CPI 同比 2.44%(基期 2025-10 为 2.99,-0.55 个百分点)、欧元区 HICP 同比 4.0%(基期 2.1,+1.9 个百分点)、"
         "日本央行政策目标 1.25%(2026-09-18 决议、2026-09-24 生效、2026-10-30 维持)、欧央行 MRO 2.65%/DFR 2.5%(2026-06-17、2026-09-16 各 +25bp)、"
         "无已决议未生效调整(限引擎可见面,欧央行 68 天缺口已标【尚未验证】);发布日按席位独立规则复算与引擎点值格一致,契约 STALE 项已披露,缺席未写成无变化,情景未触发未证伪。"
         "MAJOR-A: reader_map.regions[EA].from_to 把 2026-02 的 1.9 写成谷底,证据面近十二个月及 2026 年内最小值为 2026-01 的 1.7,且与本档 turnings 自述「欧元区 2026-01 的 1.7」相左。"
         "MAJOR-B: 对质第 2 环(EURUSD)裁「支持竞争解释」越证——主解释「方向分立」预期未纳入美元端利率(UST_10Y 5.04%、快照序列面联邦基金目标区间 3.75–4.00% 均高于 MRO 2.65%/BOJ 约 1.25%,"
         "窗内三地无政策利率变动),两解释对 EURUSD/USDJPY 预言同向,按读者报告自述口径「预期未分立=尚不能区分」应改裁;并称 EURJPY「不可做」与证据面不符(同日两腿可合成,至 2026-11-20 约 -0.24%、至 2026-11-23 约 -0.73%);"
         "连带 M1 step3「获支持」与 QGN 对质计数须同改,共 5 处必修句。MINOR 5 条、NIT 5 条另列,不构成阻断。")

# ---------------------------------------------------------------- PROSE
by = {}
for r in ROWS:
    d = by.setdefault(r["cat"], [0, 0, 0])
    d[0] += 1
    d[1] += 1 if r["ok"] else 0
    d[2] += 0 if r["ok"] else 1
CATNAME = {"①": "截止日", "②": "点值锚格", "③": "同比基期", "④": "政策面", "⑤": "三利率分解与资产月窗", "⑥": "转折判断与候选面",
           "⑦": "传导链各环", "⑧": "历史类比", "⑨": "情景", "⑩": "文字与数值一致性/对质表", "⑪": "诚实缺席/Gate A", "⑫": "截止日当日观测时点",
           "⑬": "契约非 VERIFIED 项", "⑭": "交付门缺口披露"}

P = []
A = P.append
A("# Audit-R32 · T3 · Round-1 独立语义审查席: 复算清单与六查记录")
A("")
A("- 席位: semantic-audit-seat / independent-zero-context-seat-r32-t3-round1(零上下文;未与研判席、操作席通信)")
A("- 代码印章: 0f3936dd7eb74c557a2350e400d58e10a09c5139(report.json → run.git_head;MAP_REPORT.md 第 4 行;复算点 A08)")
A("- 受审对象: agent_judgment.json 全文(l3 / l4 / reader_map / quality_gate_notes / agent_declaration)与读者报告(MAP_REPORT.md、report.md)中的判断文字")
A("- 只读面(本文全部数值的出处,括号内为文件+键,「复算点 Xnn」见附表): ")
A("  - 冻结快照 root_overlay/data/daily/research_snapshot_20261123.json: series_store / facts / gate_a / research_as_of / target_date")
A("  - 冻结发布日历 root_overlay/config/release_calendar.json: entries(版本 v1.5.0,2026-11-21 更新;复算点 A09、A10)")
A("  - 指标注册表 root_overlay/config/metric_registry.json: metrics")
A("  - report.json: run / research_plan / steps[*].envelope / notes / agent_judgment.contract_verification(未读取 semantic_review 取值)")
A("  - agent_judgment.json、evidence_index.json、MAP_REPORT.md、report.md")
A("- 未做: 联网;引擎写操作;委派子代理;读取规程 §2 禁止路径;读取任何预审内容")
A("- 席位独立规则(与引擎推定规则相互独立复算): EA_HICP 月末+16 天;JP_CPI 月末+20 天;东京 CPI 月末−1 天;BOJ 月均月末+5 天;ECB 变更点序列发布日=变更日")
A("- 脚本: s20_recompute.py(入口)+ s20_part_a.py(①–⑤)+ s20_part_b.py(⑥–⑭);结果 recompute_table.tsv / recompute_table.json / recompute_supplement.json;"
  "本文件与裁决档由 s30_write_outputs.py 生成(原句逐字抽取自 agent_judgment.json,带在场断言)")
A("- 结果: 复算 %d 点,命中 %d,偏离 %d(MAJOR 3 行·归 2 类 / MINOR 2 / NIT 2)→ 裁决 **REVISE**(MAJOR 2 类共 6 处必修句)" % (NPTS, NHIT, NMIS))
A("")
A("## 1. 复算清单")
A("")
A("### 1.1 分类汇总")
A("")
A("| 规程 §3 项 | 复算点 | 命中 | 偏离 |")
A("|---|---|---|---|")
for k in sorted(by):
    A("| %s %s | %d | %d | %d |" % (k, CATNAME.get(k, ""), by[k][0], by[k][1], by[k][2]))
A("| 合计 | %d | %d | %d |" % (NPTS, NHIT, NMIS))
A("")
A("### 1.2 偏离逐条(共 %d 行)" % NMIS)
A("")
A("| 点 | 类 | 复算项 | 直算值 | 报告/判断档值 | 级别 | 说明 |")
A("|---|---|---|---|---|---|---|")
for r in MISS:
    A("| %s | %s | %s | %s | %s | %s | %s |" % (r["id"], r["cat"], clip(r["item"], 80), clip(r["calc"], 90), clip(r["rep"], 60), r["sev"], clip(r["note"], 150)))
A("")
A("逐点全表(点 / 类 / 复算项 / 出处键 / 直算值 / 报告值 / 一致)见文末附录。")
A("")
A("## 2. 六查逐项结论")
A("")
A("判据: 证据相关性 / 支持度 / 竞争解释(真正竞争,非稻草人)/ 反对证据 / 结论是否超出证据 / 证伪条件可观测性(被点名的区分指标须在证据面在场,且两解释在其上的预言方向确实不同)。")
A("")
A("### 2.1 C1-INFL-DIVERGE —— 两地通胀同比最新读数相比去年同月方向相反")
A("- 证据相关性: 引用 2 条(JP_CPI_YOY@2026-10-01、EA_HICP_YOY@2026-10-01;复算点 G06),对「最新读数与 L1 质量」直接相关;基期值(2025-10)在证据索引无对应行(索引只含最新期事实),本席自 series_store 直算核验(C02=2.99、C05=2.1)。成立。")
A("- 支持度: 日本 2.44 对 2.99,差 -0.55 个百分点(C01–C03);欧元区 4.0 对 2.1,差 +1.9 个百分点(C04–C06);基期月=最新观测月−12 月=2025-10(C07)。"
  "东京 CPI 2.73、序列自 2026-01 起、10 个观测、去年同月基期缺席(C08–C12);Gate A noncore_missing、「来源文件在场而指标缺席」、无 L1 事实行(K01–K03);两条最新读数 L1=WARN/WARN(K06、K07)。"
  "发布日按席位规则: 欧元区 2026-11-16、日本 2026-11-20、东京 2026-10-30,与引擎点值格一致(B02c、B08c、B10c)。全部吻合。")
A("- 竞争解释: 「能源/进口传导 + 日本高基数消退 → 剪刀差收敛」对「需求与政策组合 → 持续分化」,对同一可观测量(两地同比差)预言方向相反,是真竞争;均标【假设】并声明引擎面无分项序列"
  "(K12 核实: 序列库中名称含 HICP/CPI 的指标只有 EA_HICP_YOY、JP_CPI_YOY、JP_CPI_TOKYO_YOY、CN_CPI_YOY 与美国 CPI、CORE_CPI)。成立。")
A("- 反对证据: 较六个月前锚两地读数同向上行(日本 1.38→2.44、欧元区 3.0→4.0;B07b、B08b、B01b、B02b),谷底分别为 2026-02 与 2026-01(F23、F16)——「方向相反」只在「相比去年同月」口径成立。"
  "陈述句已限定口径;总判断「通胀环境方向相反」外延偏宽(MINOR-a)。")
A("- 结论是否超出证据: 陈述未作归因,未超出。")
A("- 证伪条件可观测性: 两条竞争解释给出方向预言但无阈值与时限,且未被裁定(如实并列);可观测指标在册。可接受。")
A("- 结论: 通过。")
A("")
A("### 2.2 C2-POLICY-SYNC —— 两地政策利率同向收紧,最近六个月可核行动均已生效、无未生效决议")
A("- 证据相关性: 引用 6 条(ECB_MRO、ECB_DFR、JP_POLICY_RATE 最新期 + USDJPY/SPX/VIX 截止日事实;G06),与陈述内各数值一一对应。成立。")
A("- 支持度: ECB_MRO 2.65 / ECB_DFR 2.5,末观测=变更日=生效日 2026-09-16(D01–D04);窗内两次变更 2026-06-17(2.15→2.4;2.0→2.25)、2026-09-16(2.4→2.65;2.25→2.5),各 25bp(D06–D11);"
  "决议日 2026-06-11、2026-09-10 确为「生效日前上一个周四」(D12、D13),生效日均为周三(D14);BOJ 目标 1.25,2026-09-18 决议、2026-09-24 生效、2026-10-30 维持(D20–D25),"
  "距截止 60/66/24 天(D26–D28);JP_POLICY_RATE 最新 1.227、六个月前锚 0.727(D37、D41);已决议未生效条目 0(D30);USDJPY 159.35、SPX 7203.85、VIX 27.01(M05–M07)。全部吻合。")
A("- 竞争解释: 「读数驱动」对「正常化程序/汇率与金融稳定考量」,预言(决议节奏随读数联动 对 脱钩)确实不同,且已交由对质第 1 环裁定(尚不能区分)。成立。")
A("- 反对证据: (i) ECB 序列止于 2026-09-16、距截止 68 天(D05),日历无 ECB 实录(D29)——判断档已标【尚未验证】;(ii) BOJ 侧最新实录止于 2026-10-30,其后 24 天(D28)无实录,未作对称标注(MINOR-f);"
  "(iii) BOJ 实录(basis=user_directive)只有目标值 1.25、无前值,日本端「收紧」方向的直接依据是月均市场利率台阶(0.478→1.227,约 +75bp;D36–D38),属推断而未标【推断】(MINOR-f)。")
A("- 结论是否超出证据: 「同向收紧」对日本端为推断(见上);「无未生效决议」已限定于引擎可见面。除标注缺口外未超出。")
A("- 证伪条件可观测性: 两竞争解释的预言可在后续决议与读数上观测,无数值阈值,由对质第 1 环如实裁为尚不能区分。可接受。")
A("- 结论: 通过(附 MINOR-f)。")
A("")
A("### 2.3 C3-ECB-VISIBILITY —— 欧央行序列止于最近一次变更日,其后决议面不可判")
A("- 证据相关性: 引用 2 条(ECB_DFR、ECB_MRO@2026-09-16;G06)。成立。")
A("- 支持度: 两序列末观测 2026-09-16(D02、D04),距截止 68 天(D05),注册表新鲜度阈 10 天(D32),Gate A noncore_degraded(K04、K05),两条 L1 quality_status=DEGRADED(D33、D34、M09),"
  "事实行注记「滞后68天(>10天」(D35),日历无 ECB 条目(D29)。契约 STALE 项即 ECB_DFR@2026-09-16=2.5(M02),判断档已披露(M03)。全部吻合。")
A("- 竞争解释: 「源端未再更新、实际无新决议」对「断档期间已有新决议、当前读数低估」,预言不同;声明引擎面不可区分、须官网核对(引擎外、须用户授权)。成立。")
A("- 反对证据: 无在面反对证据。变更点序列「止于变更日」本身是常态,判断档已把这一读法并列。")
A("- 结论是否超出证据: 否——明确写「引擎面不可判」。")
A("- 证伪条件可观测性: 区分手段(官网核对)在引擎面之外并已如实标注,不是不可观测的托辞。可接受。")
A("- 结论: 通过。")
A("")
A("### 2.4 机制链 M1-INFL-POLICY-ASSET(四环)")
A("证据级 E1/E1/E2/E2(G01);E2 两环带缺环注记(G02)并以【假设】/条件式措辞出现(G03);全链与三条矛盾陈述合计 20 条引用、零悬空(G04–G06)。")
A("")
A("环 1(E1)通胀路径: EA 2026-02 的 1.9→2026-05 的 3.2、2026-06 的 2.8、2026-10 的 4.0;JP 2025-01 的 4.03→2025-07 的 3.1→2026-02 的 1.27→2026-10 的 2.44(C21、C23、C24、C04、C28–C30、C01)。数值全部吻合。")
A("- 相关性 / 支持度: 成立。")
A("- 「持续回落」: 2025-01→2026-02 间有两处逐月回升(2025-08→09 2.72→2.91、2025-09→10 2.91→2.99;F20),端点无误,属行文(NIT-3)。")
A("- 「spliced」: 注册表与事实行 calc 文本用「拼接」,原句括注「新基优先,重叠差>0.10pp 告警」逐字在场(N07);英文词为研判席自拟(NIT-2)。")
A("- 竞争解释 / 证伪: 观察环不作因果主张,不适用。")
A("- 结论: 通过(附 NIT)。")
A("")
A("环 2(E1)政策面跟进: 数值全部吻合(见 2.2)。ECB 决议日标【推断】且复算属实;「月均台阶 1.043→1.227 与 2026-09-24 生效记录相容,其余台阶不作相容性判断」为审慎表述(D40、D37)。结论: 通过。")
A("")
A("环 3(E2)传导【假设】: 主张「利差主导应体现于 EURUSD/USDJPY 方向分立」,以「方向分立未出现」裁「美元全局主导的竞争解释在本月窗获支持」。")
A("- 相关性: 汇率月窗数值全部吻合——EURUSD 1.1221→1.0970(-2.24%)→1.0940(-2.51%);USDJPY 156.494→159.707(+2.05%)→159.347(+1.82%);DXY 101.81→103.81(+1.96%)→104.079(+2.23%)(G12–G26)。")
A("- 支持度(关键): 主解释预言忽略了美元端。证据面美元端利率高于两地——UST_10Y 最新 %s%%(J07;判断档自己引用)与快照序列面联邦基金目标区间 %s–%s%%(DFEDTARL/DFEDTARU@2026-11-23;补充面 fed_band),"
  "MRO %s%%(D01)、BOJ 目标 %s%%(D22);窗内(2026-10-23..2026-11-23)三地均无政策利率变动(DFEDTARU 上次变动 2026-09-17;ECB 2026-09-16;BOJ 2026-10-30 为维持;补充面 policy_changes_in_fx_window)。"
  "纳入美元端后,利差主导对本月窗同样预期两货币对美元走弱——与竞争解释预言同向。日元对美元 -2.01%%(G42)、欧元对美元 -2.24%%(G21),两者幅度相当(相差约 %s 个百分点;同日两腿相乘的合成交叉盘变动 %s%%,J03)。故「方向分立未出现」不是两解释的区分性观测。" % (UST, TL, TU, MRO, BOJ, DIFF, C20))
A("- 竞争解释: 两解释本身是真竞争,但对质所用预言未分立;读者报告自述口径为「预期未分立=尚不能区分,不以单侧证据裁」(MAP_REPORT.md 第 151 行)。")
A("- 反对证据: 第 3 环同档自用更严标准(「证据倾向竞争解释但不足以裁定,尚不能区分」);本环 missing_link_note 写「方向留白不裁」,与环文「获支持」自相矛盾。")
A("- 结论是否超出证据: 超出——裁定「支持竞争解释」无分立预期支撑(MAJOR-B)。")
A("- 证伪条件可观测性: 被点名的区分指标 EURUSD 在场;另称「EURJPY 交叉盘…直接检验不可做」与证据面不符——同日两腿可合成(EURUSD×USDJPY: %s→%s→%s,即 %s%% / %s%%;J03),"
  "幅度小,结果略不利于「欧元相对日元走强」,但不足以裁(MAJOR-B)。" % (X0, X20, X23, C20, C23))
A("- 结论: 不通过(MAJOR-B)。")
A("")
A("环 4(E2)资产面: SPX -9.36%、NIKKEI225 -9.98%、DAX -1.50%、CAC40 +1.86%(G27–G30);VIX 19.45→35.89(+84.5%,G31–G33),末六日路径逐位吻合(G34),末五个交易日(G35),"
  "距 2026-10-30 14 天、距 2026-09-16 58 天(G36、G37);引擎回贴 -5.51/+0.11/-9.98/+38.87(E10–E13)与 -24.7%(E14)。「两地股指弱于美股」在欧元区端不成立(J08),日本端与美股差 0.62 个百分点(J09)。"
  "结论「两种叙事均相容、单一归因不可证」审慎,未超出。")
A("- 反对证据 / 完整性: 跳升窗内另有引擎面政策文献事件——FOMC 2026年10月会议纪要 2026-11-18 发布(research_plan.policy_doc_facts[0];MAP_REPORT.md 第 94 行),其后 VIX 24.56→28.44→35.89(补充面 policy_doc_event_window);"
  "「距最近政策日 14 天」只就日/欧政策日成立,判断档未提及亦未排除这一第三类候选驱动(J10,MINOR-g)。裁定(尚不能区分)不受影响。")
A("- 结论: 通过(附 MINOR-g)。")
A("")
A("### 2.5 传导对照三环对质(MAP_REPORT.md 第 147–149 行)")
A("对质计数: 支持主解释 0·支持竞争解释 1·尚不能区分 2,与 QGN[1] 自述一致(J01)。")
A("")
A("第 1 环(EA_HICP_YOY,裁「尚不能区分」)")
A("- 可见读数复算(席位规则;决议日按引擎惯例回推): 2026-06-11 前 2026-04=3.0;2026-06-17 前 2026-05=3.2;2026-09-10 前 2026-07=2.9;2026-09-16(含)前 2026-08=3.2,其发布日 2026-09-16 与生效日同日(G07–G11)。全部吻合。")
A("- 两解释预言: 读数驱动=决议前已见读数抬升;程序驱动=节奏与读数无稳定关系。后者无方向预言,严格说预期未分立 → 裁「尚不能区分」符合自述口径。")
A("- 支持度与反对证据: 两次决议前读数均高于 2026-02 的 1.9;反向: 两序列维持 2.15/2.0 共 371 天(D18),其间读数自 2026-01 的 1.7 升至 2026-04 的 3.0 未触发变更;两次变更相隔 91 天、各 25bp(D17),等距等幅。读数驱动(含滞后)与程序驱动均相容,n=2。")
A("- 结论: 通过。裁定未超出证据。")
A("")
A("第 2 环(EURUSD,裁「支持竞争解释」): 不通过,见 2.4 环 3(MAJOR-B)。")
A("")
A("第 3 环(VIX,裁「尚不能区分」)")
A("- 数值全部吻合(见 2.4 环 4)。")
A("- 2026-11-20 冲高后的回落证据: 截止日只有 2026-11-23 一个观测,且快照采于纽约 09:53(A14)=盘中非收盘——「仅有一个盘中观测」字面成立(J04)。")
A("- 「证据倾向竞争解释但不足以裁定」与其自用标准一致,未超出。")
A("- 完整性: 同窗内已有一段与日/欧政策日历无关的冲高回落收盘(2026-11-04 16.61→2026-11-05 28.18→2026-11-09 19.92→2026-11-11 17.49;补充面 vix_midwindow_episode),判断档未援引(NIT-4);FOMC 纪要见 MINOR-g。")
A("- 结论: 通过。")
A("")
A("### 2.6 情景 S1-STICKY-TIGHTEN / S2-INFL-FADE")
A("- 可观测: 证伪指标 EA_HICP_YOY 在册(I12),敏感变量 EA_HICP_YOY/JP_CPI_YOY 在册;VIX 触发以收盘口径(高于 30 / 低于 25)表述,截止日 2026-11-20 收盘 35.89、2026-11-23 盘中 27.01,未单侧触发(I11)。")
A("- 与截止日读数相容: S1 前提(欧元区 3.5% 以上、日本 2.0% 以上)对 2026-10 读数 4.0 / 2.44 成立(I06、I07);S2 为反例情景并已声明与近一月观察相反。")
A("- 未触发 / 未证伪: 2026-11、2026-12 观测月读数按席位规则分别于 2027-01-16(欧元区)、2027-01-20(日本)入档,均早于期限 2027-02-15(I02、I03);截止日最新已发布观测月为 2026-10(I04、I05)→ 两情景均未触发、未被证伪。")
A("- 方向互补: S1「维持 3.5% 以上 + 再上调」对 S2「回落至 3.0% 以下 + 按兵不动」(I10)。")
A("- 证伪阈值对齐: S1 证伪(两月均低于 3.5%)与前提(3.5% 以上)对齐(I08);S2 证伪(两月均不低于 3.5%)较前提(3.0% 以下)放宽,3.0%–3.5% 区间既不触发也不证伪——"
  "QGN[3]「证伪阈值与前提水平对齐(3.5%)」只对 S1 成立(I09,MINOR-e)。日本分量与政策分量不设数值阈值,已如实声明。")
A("- 结论: 通过(附 MINOR-e)。")
A("")
A("### 2.7 读者面")
A("- 总判断(headline_conclusion;MAP_REPORT.md 第 12 行): 各数值与 2.1 / 2.2 一致(J05、J06)。「通胀环境方向相反」仅就「相比去年同月」成立,较六个月前锚两地同向上行(MINOR-a)。")
A("- 地区走位 EA(regions[EA].from_to;MAP_REPORT.md 第 122 行): 政策与环境数值吻合(D01–D11、C04–C06);「路径: 2026-02 谷底 1.9…」错——近十二个月(2025-11..2026-10)、2026 年内、2025-01 以来三个窗口的最小值均为 2026-01 的 1.7(2025 年内谷底为 2025-05 的 1.9;F16、F18),"
  "2026-02 的 1.9 高于前月;同档 turnings[0] 自述「欧元区 2026-01 的 1.7」(F16–F18)。MAJOR-A。")
A("- 地区走位 JP(regions[JP].from_to): 数值吻合(D22、D36–D39、C01–C03、C11、C12);「持续回落」见 NIT-3。")
A("- 转折表(turnings;MAP_REPORT.md 第 166 行): 三项前后值与月份与引擎候选面一致(F01–F14),候选为窗内三个月变动绝对值最大者(F05、F15);「候选池内最大单段变动 -1.63」属实(F24)。")
A("- 三利率分解与资产月窗: 名义 -8bp=实际 +11bp+盈亏平衡 -19bp,水平恒等 5.04=2.88+2.16(E01–E09);回贴值 E10–E14。")
A("- 历史类比: 0 段并如实写明;S6 扫描 1871、有效 74、TOP1 2025-03、距离 0.727(H01–H06)。")
A("- 截止日时点: 快照采集 2026-11-23T22:53:47+08:00(纽约 09:53、柏林 15:53、东京 23:53、上海 22:53;A14–A17、L01),截止日值标「盘中快照、非收盘价」(L03),NIKKEI225 最新观测 2026-11-20 未充当日值(L05)。")
A("")
A("## 3. 反方攻击记录")
A("")
for c in COUNTER:
    A("- " + c)
A("")
A("## 4. 问题清单")
A("")
A("### 4.1 MAJOR(必修;2 类共 6 处)")
A("")
for it, tag in zip(ITEMS[:6], ["MAJOR-A(1/1)", "MAJOR-B(1/5)", "MAJOR-B(2/5)", "MAJOR-B(3/5)", "MAJOR-B(4/5)", "MAJOR-B(5/5)"]):
    A("**%s**" % tag)
    A("- 位置: %s" % it["where"])
    A("- 问题: %s" % it["note"])
    A("- 原句: 「%s」" % it["original"])
    A("- 改句: 「%s」" % it["fix"])
    A("")
A("说明: 若研判席坚持「支持竞争解释」,须把主解释改写为可检验的相对预言(欧元相对日元走强)并以合成交叉盘 %s%% / %s%% 为据、同时说明单月窗与幅度;按本档第 3 环自用的标准,本席认为「尚不能区分」是可用证据面数字成立的改句。"
  "以上改句中 UST_10Y、MRO、BOJ 目标、EURUSD/USDJPY 均在本轮证据索引内;联邦基金目标区间取自冻结快照 series_store(DFEDTARL/DFEDTARU),不在本轮 60 行证据索引,研判席若无法按契约绑定可只保留 UST_10Y 一句,论证不变。" % (C20, C23))
A("")
A("### 4.2 MINOR(不构成阻断)")
A("")
for i, it in enumerate(ITEMS[6:11], 1):
    A("%d. **%s** — %s" % (i, it["where"], it["note"]))
    if it["original"]:
        A("   - 原句: 「%s」" % it["original"])
        A("   - 建议改句: 「%s」" % it["fix"])
A("")
A("### 4.3 NIT")
A("")
for i, it in enumerate(ITEMS[11:], 1):
    A("%d. **%s** — %s" % (i, it["where"], it["note"]))
    if it["original"]:
        A("   - 原句: 「%s」" % it["original"])
        A("   - 建议改句: 「%s」" % it["fix"])
A("")
A("## 5. 引擎面观察(不入裁决,供操作席参考)")
A("")
A("1. research_plan.point_values.cells[ECB_MRO / ECB_DFR].policy_window_path 的 net_bp 取「窗内首个观测」为起点,而该观测本身已含一次变动: ECB_MRO 净 +25bp(2.4→2.65)与窗内事件之和 +50bp 不一致,"
  "MAP_REPORT.md 第 73、76 行照渲染「净变动 +25bp」,判断档欧元区段未就该差异作说明;日本端同理(引擎窗净 +67bp,对自 2025-11 的 0.478 起算约 +75bp),判断档日本段已把两种净变动口径并列。建议立研发项复核(补充面 engine_policy_window_net_bp;复算点 D38、D39)。")
A("2. report.json → notes 与 report.md 第 240 行把六个计划指标全部列为「地图计划指标缺数」,report.md 第 11–16 行列为「任务目标缺口」,而点值格 12 个锚全部 status=ok(补充面 engine_notes_plan_metrics_missing)。属交付门面自述矛盾;判断档按点值格与序列面取值,未受该自述影响。")
A("3. EA 转折候选并列: 2026-01→04 与 2026-02→05 精确同为 +1.30,引擎因浮点噪声取后者(补充面 ea_rolling_tie)。")
A("4. 证据索引不含美元端政策利率(DFEDTARU / DFEDTARL 不在 60 行内),而快照序列面在场;研判席讨论「利差」时因此缺美元端政策锚。")
A("5. SPX / DAX / CAC40 的 2026-11-23 事实行 calc 文本写「收盘点位」、VIX 写「VIX指数收盘」,而快照采于纽约 09:53(盘中);判断档已正确标注「盘中快照、非收盘价」。")
A("6. 注册表 ECB_MRO / ECB_DFR 的 calc 写「决议变更即时生效」,引擎惯例为「决议日=生效日前上一个周四」;两者不矛盾但易误读。")
A("7. 中文数字表述(如「百分之二点四四」)不进契约的确定性数值绑定,独立复算是其唯一数值核验途径(本席已覆盖 C01–C06 等)。")
A("8. QGN[5]① 所述 obs_run 锚序检查硬编码,本席未读引擎源码;仅见 contract_verification.stats.map_fail=0 且 map_checks 无该项,未复核(补充面 contract_face)。")
A("")
A("## 附录: 复算清单全表")
A("")
A("| 点 | 类 | 复算项 | 出处(文件+键) | 直算值 | 报告/判断档值 | 一致 |")
A("|---|---|---|---|---|---|---|")
for r in ROWS:
    A("| %s | %s | %s | %s | %s | %s | %s |" % (r["id"], r["cat"], clip(r["item"], 120), clip(r["src"], 150), clip(r["calc"], 110), clip(r["rep"], 110), "是" if r["ok"] else "否(" + (r["sev"] or "-") + ")"))
A("")
PROSE = "\n".join(P)

VERDICT = {
    "seat": "semantic-audit-seat",
    "reviewer": "independent-zero-context-seat-r32-t3-round1",
    "verdict": "REVISE",
    "overall": "REVISE",
    "notes": NOTES,
    "items": ITEMS,
    "must_fix": MUST,
    "counterexamples_sought": COUNTER,
    "recompute_points": NPTS,
    "recompute_mismatches": NMIS,
    "mismatch_details": [{"id": r["id"], "category": r["cat"], "item": r["item"], "calc": r["calc"], "reported": r["rep"],
                          "severity": r["sev"], "note": r["note"]} for r in MISS],
    "audited_at": "2026-11-24",
}

with open(os.path.join(OUT, "PROSE-round1.md"), "w", encoding="utf-8") as fh:
    fh.write(PROSE)
with open(os.path.join(OUT, "VERDICT-round1.json"), "w", encoding="utf-8") as fh:
    json.dump(VERDICT, fh, ensure_ascii=False, indent=1)
    fh.write("\n")

# ---------------------------------------------------------------- 数字出处守卫(正文 0–5 节,不含附录)
body = PROSE.split("## 附录:")[0]
ALLOWED = set()
for r in ROWS:
    for k in ("calc", "rep", "item", "note", "src"):
        ALLOWED.add(str(r[k]))
ALLOWED.add(JTDUMP)
ALLOWED.add(json.dumps(SUPP, ensure_ascii=False))
ALLOWED.add(MAP_TEXT)
ALLOWED.add(REPMD_TEXT)
ALLOWED.add("%s %s %s %s %s" % (X0, X20, X23, TU, TL))
ALLOWTXT = "\n".join(ALLOWED)
WL = set(str(x) for x in list(range(0, 70)) + [74, 76, 79, 91, 94, 122, 147, 148, 149, 151, 166, 240, 287, 280])
unmatched = []
for tok in sorted(set(re.findall(r"\d+(?:\.\d+)?", body)), key=lambda x: (len(x), x)):
    if tok in WL:
        continue
    if tok not in ALLOWTXT:
        unmatched.append(tok)
print("WROTE: %s, %s" % (os.path.join(OUT, "PROSE-round1.md"), os.path.join(OUT, "VERDICT-round1.json")))
print("PROSE lines=%d chars=%d | items=%d (MAJOR=%d MINOR=%d NIT=%d) | must_fix=%d | counter=%d" % (
    len(P), len(PROSE), len(ITEMS), sum(i["severity"] == "MAJOR" for i in ITEMS), sum(i["severity"] == "MINOR" for i in ITEMS),
    sum(i["severity"] == "NIT" for i in ITEMS), len(MUST), len(COUNTER)))
print("NUMERIC_GUARD unmatched tokens: %s" % unmatched)
