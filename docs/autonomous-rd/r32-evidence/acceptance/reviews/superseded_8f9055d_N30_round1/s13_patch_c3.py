import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
def rep(s, a, b, cnt=1):
    assert s.count(a) == cnt, (s.count(a), a[:70])
    return s.replace(a, b)
s = rep(s, 'PATH_EA = "→".join("%s(%s)" % (n(VE[i]), "2026-%02d" % i) for i in range(5, 11))',
        'def p1(v):\n    s_ = n(v)\n    return s_ + ".0" if "." not in s_ else s_\n\n\nPATH_EA = "→".join("%s(%s)" % (p1(VE[i]), "2026-%02d" % i) for i in range(5, 11))')
s = rep(s, 'PATH_JP = "→".join("%s(%s)" % (n(VJ[i]), "2026-%02d" % i) for i in range(5, 11))',
        'PATH_JP = "→".join("%s(%s)" % (p1(VJ[i]), "2026-%02d" % i) for i in range(5, 11))')
s = rep(s, 'sup("美联储序列最近变动 2026-09-16→2026-09-17", [d for d in sorted(FTL) if d >= "2026-09-15"][:2] == ["2026-09-16", "2026-09-17"] and FTL["2026-09-16"] != FTL["2026-09-17"])',
        'FTL_KS = sorted(FTL)\nFTL_CH = [(a, b) for a, b in zip(FTL_KS, FTL_KS[1:]) if FTL[a] != FTL[b]]\n'
        'sup("美联储序列(DFEDTARL,日历日逐日)最近变动 " + FTL_CH[-1][0] + "→" + FTL_CH[-1][1] + "(" + n(FTL[FTL_CH[-1][0]]) + "→" + n(FTL[FTL_CH[-1][1]]) + ",其后至截止日无变动;此前一次变动 " + FTL_CH[-2][0] + "→" + FTL_CH[-2][1] + ")",\n'
        '    FTL_CH[-1] == ("2026-09-16", "2026-09-17") and FTL_CH[-2] == ("2025-12-10", "2025-12-11") and FTL["2026-09-16"] == 3.5 and FTL["2026-09-17"] == 3.75 and max(FTL) == CUTOFF and len(FTL_CH) > 2,\n'
        '    (FTL_CH[-2:], FTL["2026-09-16"], FTL["2026-09-17"]))')
new_item = '''EA_AN6 = CELLS["EA_HICP_YOY"]["anchors"]["6个月前"]
EA_PUB_WK, EA_RULE = str(EA_AN6["publication_date"]), str(EA_AN6["publication_rule"])
assert EA_PUB_WK == "2026-05-16" and D(EA_PUB_WK).weekday() == 5 and "月末+16天" in EA_RULE and "该推定日落在周日" in JALL and D("2026-08-30").weekday() == 6
item("MINOR", "reader_map.regions[0].from_to(欧元区行,「发布 2026-05-16」处)",
     "欧元区 2026-04 期读数的引擎推定发布日 %s 落在周六(引擎规则「%s」推算所得,不可能是实际发布日);句中已标引擎推定规则、非日历实录,但未如东京都 2026-08 期推定日处(2026-08-30,句中已点明落在周日)那样点明落在周末。"
     "该日期只作锚格发布面标注;六个月前锚取值(观测月 2026-04 的 %s)与各处可见性结论均不依赖它。披露可改进,结论不变。" % (EA_PUB_WK, EA_RULE, n(mo(EA, 2026, 4))),
     path=RG_P + [0, "from_to"], start="发布 2026-05-16,引擎推定规则、非日历实录",
     fix="发布 2026-05-16(周六;引擎月末+16 天推定规则、非日历实录,实际发布日以官方实录为准)")
'''
a = 'item("NIT", "l3.mechanism_chains[0].links[3].text(环4,「为窗内两个最大单日跳升日」)",'
s = rep(s, a, new_item + a)
s = rep(s, 'assert (N_MAJ, N_MIN, N_NIT) == (0, 7, 10), (N_MAJ, N_MIN, N_NIT)', 'assert (N_MAJ, N_MIN, N_NIT) == (0, 8, 10), (N_MAJ, N_MIN, N_NIT)')
open(p, "w", encoding="utf-8").write(s)
print("part C patched")
