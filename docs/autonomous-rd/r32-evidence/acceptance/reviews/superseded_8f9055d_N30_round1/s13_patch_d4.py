import re, sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
def rep(s, a, b, cnt=1):
    assert s.count(a) == cnt, (s.count(a), a[:80])
    return s.replace(a, b)
# formatters
s = rep(s, '''        s_ += "0" * max(0, 2 - len(s_.split(".")[1]))
    return s_''', '''        s_ += "0" * max(0, 2 - len(s_.split(".")[1]))
    return s_


def f2(v):
    return "%.2f" % v


def f3(v):
    return "%.3f" % v


def sgn(v):
    return "+" if v > 0 else ("−" if v < 0 else "")


def sg2(v):
    return sgn(v) + f2(abs(v))


def sp1(v):
    return sgn(v) + p1(abs(v))''')
# SIX C1
s = rep(s, '陈述内全部数值直算一致: 水平差 %s−%s=%s;同比对照欧元区 +%s、日本 %s;锚间 +%s 对 +%s;自 2026-06 +%s 对 +%s;自 2026-05 +%s 对 +%s;"',
        '陈述内全部数值直算一致: 水平差 %s−%s=%s;同比对照欧元区 %s、日本 %s;锚间 %s 对 %s;自 2026-06 %s 对 %s;自 2026-05 %s 对 %s;"')
s = rep(s, 'n(VE[10]), n(VJ[10]), n(GAP10), n(YEA), sg(-YJP), n(D04[0]), n(D04[1]), n(D06[0]), n(D06[1]), n(D05[0]), n(D05[1]),',
        'p1(VE[10]), p1(VJ[10]), f2(GAP10), sp1(YEA), sp1(-YJP), sp1(D04[0]), sp1(D04[1]), sp1(D06[0]), sp1(D06[1]), sp1(D05[0]), sp1(D05[1]),')
# SIX C2
s = rep(s, 'n(MRO["2025-06-11"]), n(MRO["2026-06-17"]), n(MRO["2026-09-16"]), n(DFR["2025-06-11"]), n(DFR["2026-06-17"]), n(DFR["2026-09-16"]), n(mo(JPR, 2026, 4)), n(mo(JPR, 2026, 10)), n(mo(JPR, 2025, 11)),',
        'f2(MRO["2025-06-11"]), f2(MRO["2026-06-17"]), f2(MRO["2026-09-16"]), f2(DFR["2025-06-11"]), f2(DFR["2026-06-17"]), f2(DFR["2026-09-16"]), f3(mo(JPR, 2026, 4)), f3(mo(JPR, 2026, 10)), f3(mo(JPR, 2025, 11)),')
s = rep(s, '"%.3f" % JPY[CUTOFF], "%.2f" % SPX[CUTOFF], "%.2f" % VIX[CUTOFF], JPT["decision_date"], JPT["effective_on"], n(JPT["target_value"]), JPT["basis"], JPM["decision_date"], JPM["kind"]),',
        '"%.3f" % JPY[CUTOFF], "%.2f" % SPX[CUTOFF], "%.2f" % VIX[CUTOFF], JPT["decision_date"], JPT["effective_on"], f2(JPT["target_value"]), JPT["basis"], JPM["decision_date"], JPM["kind"]),')
s = rep(s, 'n(MRO[LAST_MRO]), n(TARGET), n(round(MRO[LAST_MRO] - TARGET, 2)), n(DFR[LAST_DFR]), n(TARGET), n(round(DFR[LAST_DFR] - TARGET, 2)), DD["d8a"], DD["d8b"]),',
        'f2(MRO[LAST_MRO]), f2(TARGET), f2(MRO[LAST_MRO] - TARGET), f2(DFR[LAST_DFR]), f2(TARGET), f2(DFR[LAST_DFR] - TARGET), DD["d8a"], DD["d8b"]),')
# SIX C3 / link1 / face-off
s = rep(s, 'Q_DET_GDP, n(mo(GEA, 2026, 7)), n(mo(GJP, 2026, 7))),', 'Q_DET_GDP, f2(mo(GEA, 2026, 7)), f2(mo(GJP, 2026, 7))),')
s = rep(s, 'n(GAPM[GAPM_MIN]), GAPM_MIN, n(GAPM[GAPM_MAX]), GAPM_MAX),', 'f2(GAPM[GAPM_MIN]), GAPM_MIN, f2(GAPM[GAPM_MAX]), GAPM_MAX),')
s = rep(s, '"- 支持度: 两地上行(欧元区 2026-06 一度回落至 %s,非逐月单调;日本 2026-05 至 2026-10 逐月上行)逐月直算属实。" % n(VE[6]),',
        '"- 支持度: 两地上行(欧元区 2026-06 一度回落至 %s,非逐月单调;日本 2026-05 至 2026-10 逐月上行)逐月直算属实。" % p1(VE[6]),')
s = rep(s, 'DD["d371"], DD["d91"], n(VE[4]), n(VE[7]), n(VE[5]), n(VE[8])),', 'DD["d371"], DD["d91"], p1(VE[4]), p1(VE[7]), p1(VE[5]), p1(VE[8])),')
# attacks
s = rep(s, '"锚格期 2026-04→2026-10: 欧元区 +" + n(D04[0]) + " 对日本 +" + n(D04[1]) + " 个百分点;自 2026-05: +" + n(D05[0]) + " 对 +" + n(D05[1]) +',
        '"锚格期 2026-04→2026-10: 欧元区 " + sp1(D04[0]) + " 对日本 " + sp1(D04[1]) + " 个百分点;自 2026-05: " + sp1(D05[0]) + " 对 " + sp1(D05[1]) +')
s = rep(s, '";自 2026-06: +" + n(D06[0]) + " 对 +" + n(D06[1]) + "(series_store.EA_HICP_YOY', '";自 2026-06: " + sp1(D06[0]) + " 对 " + sp1(D06[1]) + "(series_store.EA_HICP_YOY')
s = rep(s, '" + n(SEPJ) + "(2.16−3.8)、东京口径 " + n(SEPT) + "(2.69−3.8)', '" + sg2(SEPJ) + "(2.16−3.8)、东京口径 " + sg2(SEPT) + "(2.69−3.8)')
s = rep(s, ',均为去年同月直算(同比对照 +" + n(YEA) + "、" + sg(-YJP) +', ',均为去年同月直算(同比对照 " + sp1(YEA) + "、" + sp1(-YJP) +')
s = rep(s, '"35.89/19.45−1=" + "%.2f" % chg(VIX, W0, W1) + "%;27.01/35.89−1=" + "%.2f" % chg(VIX, W1, CUTOFF) + "%;', '"35.89/19.45−1=" + sg2(chg(VIX, W0, W1)) + "%;27.01/35.89−1=" + sg2(chg(VIX, W1, CUTOFF)) + "%;')
s = rep(s, '(欧元区 " + n(VE[10]) + "/日本 " + n(VJ[10]) + "/水平差 " + n(GAP10) + ")', '(欧元区 " + p1(VE[10]) + "/日本 " + p1(VJ[10]) + "/水平差 " + f2(GAP10) + ")')
s = rep(s, '''     "研究计划点值格的推定发布日中落周末者 " + str(len(WK)) + " 个(" + "、".join(WK) + ");判断档正文引用且见于点值格的日期为 " + "、".join(CITED_PUB) + ",其中落周末者 " + str(len(CITED_WK)) + " 个。未找到反例"),''',
        '''     "研究计划点值格的推定发布日中落周末者 " + str(len(WK)) + " 个(" + "、".join(WK) + ");判断档正文引用且见于点值格的日期为 " + "、".join(CITED_PUB) + ";正文落周末的日期记号 " + str(len(CITED_WK)) + " 个(" + "、".join(CITED_WK) + "): "
     "窗起日 2026-05-23 为六个月窗起点,东京都 2026-08 期推定日 2026-08-30 句中已点明落在周日;唯欧元区 2026-04 期推定日 2026-05-16 落在周六而句中未点明(已标引擎推定规则、非日历实录,不改变任何取值)。记 MINOR-8"),''')
n_sg = s.count("sg(chg(")
s = s.replace("sg(chg(", "sg2(chg(")
# notes: dynamic issue summaries
defs = '''MINOR_SUM = ["ECB 序列最新水平一句未带降级限定", "日欧 CPI 同比为引擎自算口径未注明", "日欧主权债收益率缺席未列入证据缺口", "东京都转折行未随行标注 noncore_missing",
             "对质裁定理由未渲染且主解释预期措辞未加限定", "ECB 决议日回推与注册表口径不一未明示", "ECB 降级归因未提引擎另一面", "欧元区 2026-04 期推定发布日落周六未点明"]
NIT_SUM = ["「为窗内两个最大单日跳升日」的窗口径", "契约 STALE 状态词未点名", "「冻结日历实录仅覆盖」缺日欧面限定", "「决议即…生效」", "「窗内月度路径」含观测日在窗前的一期",
           "「UST_10Y 最新 5.04%」未写观测日", "情景触发/证伪空档披露不全", "环2 标题「政策面跟进」", "「中旬速报先行口径」", "「此后总体回升」未注一次小幅回落"]
assert len(MINOR_SUM) == N_MIN and len(NIT_SUM) == N_NIT
NOTES = (
'''
s = rep(s, 'NOTES = (\n', defs)
a = s.index('"(ECB 序列最新水平一句未带降级限定;')
b = s.index('NIT " + str(N_NIT) + " 条(行文/限定语)。', a)
assert s[b - 15:b] == '),均不改结论;"\n    "', ascii(s[b - 15:b])
s = s[:a] + '"(" + "；".join(MINOR_SUM) + "),均不改结论;"\n    "' + s[b:]
c = s.index('str(N_NIT) + " 条(行文/限定语)。')
k = len('str(N_NIT) + " 条(行文/限定语)。')
s = s[:c] + 'str(N_NIT) + " 条(" + "；".join(NIT_SUM) + ")。' + s[c + k:]
open(p, "w", encoding="utf-8").write(s)
print("part D patched; sg(chg( replaced:", n_sg)
