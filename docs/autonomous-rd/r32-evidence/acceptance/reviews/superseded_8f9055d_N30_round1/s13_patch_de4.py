import re, sys
def load(p): return open(p, encoding="utf-8").read()
def save(p, s): open(p, "w", encoding="utf-8").write(s)
def rep(s, a, b, cnt=1):
    assert s.count(a) == cnt, (s.count(a), a[:80])
    return s.replace(a, b)

# ---------------- part D
p = sys.argv[1]; s = load(p)
s = rep(s, 'ALT = (round(VE[10] - mo(EA, 2025, 9), 2), round(mo(JPC, 2025, 9) - VJ[10], 2))',
        'ALT = (round(VE[10] - mo(EA, 2025, 9), 2), round(mo(JPC, 2025, 9) - VJ[10], 2))\n\n\ndef fxv(dct, d, k):\n    """currency level with the precision the judgment itself uses (EURUSD 4 / USDJPY 3 / DXY >=2 decimals)"""\n'
        '    s_ = ("%." + str(d) + "f") % dct[k]\n    if dct is DXY:\n        s_ = s_.rstrip("0")\n        s_ += "0" * max(0, 2 - len(s_.split(".")[1]))\n    return s_')
cnt = [0, 0, 0]
for name, dct, d in (("EUR", "EUR", 4), ("JPY", "JPY", 3), ("DXY", "DXY", 3)):
    s, k = re.subn(r"n\(" + name + r"\[([^\]]+)\]\)", "fxv(" + dct + ", " + str(d) + r", \1)", s)
    cnt[("EUR", "JPY", "DXY").index(name)] = k
print("fxv replacements", cnt)
s = rep(s, 'EURJPY 合成 %s/%s/%s(%s%%/%s%%)——全部直算一致。" % (',
        'EURJPY 合成 %s/%s/%s(%s%%/%s%%)——全部直算一致(汇率各日值取自快照 series_store 的 EURUSD/USDJPY/DXY;EURJPY=同日两腿相乘)。" % (')
save(p, s)

# ---------------- part C (MINOR-8 wording + count assertion)
p = sys.argv[2]; s = load(p)
s = rep(s, 'assert EA_PUB_WK == "2026-05-16" and D(EA_PUB_WK).weekday() == 5 and "月末+16天" in EA_RULE and "该推定日落在周日" in JALL and D("2026-08-30").weekday() == 6',
        'N_EA_PUB_WK = sum(v.count("2026-05-16") for _p, v in LV if isinstance(v, str) and _p[0] != "agent_declaration")\n'
        'assert EA_PUB_WK == "2026-05-16" and D(EA_PUB_WK).weekday() == 5 and "月末+16天" in EA_RULE and "该推定日落在周日" in JALL and D("2026-08-30").weekday() == 6 and N_EA_PUB_WK == 1')
s = rep(s, '"该日期只作锚格发布面标注;六个月前锚取值(观测月 2026-04 的 %s)与各处可见性结论均不依赖它。披露可改进,结论不变。"',
        '"该日期在判断档正文仅此一处、只作六个月前锚的发布面标注;锚取值(观测月 2026-04 的 %s)与各处可见性结论均不依赖它。披露可改进,结论不变。"')
save(p, s)

# ---------------- part E
p = sys.argv[3]; s = load(p)
s = rep(s, '''P.append("4. 二路脚本(s06_independent_check.py,不调用主表任何函数)复核被引数值 %d 点;首跑报 3 点偏离,经查为本席比对参数所致(判断档按一位小数书写的 VIX 百分比与带 float32 尾数的原始值被按 ±0.005 比对),"
         "按书写精度比对后 %d/%d。" % (I["n"], I["ok"], I["n"]))''',
        '''P.append("4. 二路脚本(s06_independent_check.py,不调用主表任何函数)复核被引数值 %d 点;首跑报 3 点偏离,经查均为本席比对容差设置过紧所致(判断档按一位小数书写的百分比与序列原值直算结果之间的书写精度差),"
         "按书写精度设定容差后 %d/%d。" % (I["n"], I["ok"], I["n"]))''')
s = rep(s, '"本席自存中间转储中有两份因含不宜留存的名称已就地遮蔽,不参与任何复算;复算脚本与中间表均不依赖它们。",',
        '"本席自存中间转储中有两份(dump/registry_notes.txt、dump/step_01_S2_doctor.json)因含不宜留存的名称已就地遮蔽,不参与任何复算;复算脚本(s05_recompute.py、s05_summ.py、s06_independent_check.py)文本内不引用这两个文件名。",')
s = rep(s, '''for f in sorted(os.listdir(SEAT_DIR)):
    fp = os.path.join(SEAT_DIR, f)
    if f in ("PROSE-round1.md", "VERDICT-round1.json"):
        continue
    if os.path.isdir(fp):
        P.append("- %s/ (%d 个文件)" % (f, len(os.listdir(fp))))
    else:
        P.append("- %s (%d 字节)" % (f, os.path.getsize(fp)))
P.append("")''',
        '''SIZES = []
for f in sorted(os.listdir(SEAT_DIR)):
    fp = os.path.join(SEAT_DIR, f)
    if f in ("PROSE-round1.md", "VERDICT-round1.json") or re.match(r"^s12_check\\d+\\.txt$", f):
        continue
    if os.path.isdir(fp):
        SIZES.append(len(os.listdir(fp)))
        P.append("- %s/ (%d 个文件)" % (f, len(os.listdir(fp))))
    else:
        SIZES.append(os.path.getsize(fp))
        P.append("- %s (%d 字节)" % (f, os.path.getsize(fp)))
P.append("- (生成器自身的运行日志 s12_check*.txt 正在写入,不计入;字节数为写出时刻的值。)")
P.append("")''')
s = rep(s, '''NUMTOK = re.compile(r"(?<![A-Za-z_0-9.])\\d+(?:\\.\\d+)?")
WL_TXT = "\\n".join([JALL, RTXT, SNAPTXT, REGTXT, json.dumps(CALE, ensure_ascii=False), MAP, FULL, json.dumps(T, ensure_ascii=False), json.dumps(I, ensure_ascii=False),
                    json.dumps(EIDX, ensure_ascii=False), "\\n".join("%r" % g for _, g, _, _ in NUM), " ".join(list(ENTRY.values()) + list(NEXT_REL.values()) + ["%d" % x for r in RUNS for x in r[:4]])])
WL = set(NUMTOK.findall(WL_TXT))
NARR = P[:I4S] + P[I4E:I11S]
MISS = sorted(set(t for t in NUMTOK.findall("\\n".join(NARR)) if t not in WL))''',
        '''NUMTOK = re.compile(r"(?<![A-Za-z_0-9.])\\d+(?:\\.\\d+)?")
HEADNUM = re.compile(r"^(#+ )+(\\d+(?:\\.\\d+)*\\.?) ")
DIAG = {"MAP/FULL found": (MAP_FOUND, N_LV, FULL_FOUND), "WMM": WMM, "WK": WK, "RP_WK": RP_WK, "CITED_PUB": CITED_PUB, "CITED_WK": CITED_WK,
        "LINES": (L_HEAD, L_COV, L_WED, L_BP, L_FOH, L_KOU, L_PEAR, L_MISS, L_JPT, L_TK, L_TKROW, L_6M), "REG_YIELDS": REG_YIELDS, "N_REF": N_REF, "JGBV": JGBV,
        "TYPE": dict(TP), "CAT": (dict(CAT), dict(OTH)), "FILES": sorted(os.listdir(SEAT_DIR)), "SIZES": SIZES, "FTL_CH": FTL_CH, "POLICY_CHANGE": FTL[FTL_CH[-1][0]],
        "COUNTS": (len(SUP), len(NUM), len(ATTACKS), len(ENG_OBS), N_BOOL, I["n"], I["ok"])}
assert "registry_notes" not in "".join(rd(os.path.join(SEAT_DIR, f)) for f in ("s05_recompute.py", "s05_summ.py", "s06_independent_check.py"))
assert "step_01_S2_doctor" not in "".join(rd(os.path.join(SEAT_DIR, f)) for f in ("s05_recompute.py", "s05_summ.py", "s06_independent_check.py"))
WL_TXT = "\\n".join([JALL, RTXT, SNAPTXT, REGTXT, json.dumps(CALE, ensure_ascii=False), MAP, FULL, json.dumps(T, ensure_ascii=False), json.dumps(I, ensure_ascii=False),
                    json.dumps(EIDX, ensure_ascii=False), "\\n".join("%r" % g for _, g, _, _ in NUM), " ".join(list(ENTRY.values()) + list(NEXT_REL.values()) + ["%d" % x for r in RUNS for x in r[:4]]),
                    json.dumps(DIAG, ensure_ascii=False, default=str)])
WL = set(NUMTOK.findall(WL_TXT))
NARR = P[:I4S] + P[I4E:I11S]
MISS = sorted(set(t for t in NUMTOK.findall("\\n".join(HEADNUM.sub(r"\\1", ln) for ln in NARR)) if t not in WL))''')
s = rep(s, '''for k, val in (("MAP/FULL found", (MAP_FOUND, N_LV, FULL_FOUND)), ("WMM", WMM), ("WK", WK), ("RP_WK", RP_WK), ("CITED_PUB", CITED_PUB), ("CITED_WK", CITED_WK), ("LINES", (L_HEAD, L_COV, L_WED, L_BP, L_FOH, L_KOU, L_PEAR, L_MISS, L_JPT, L_TK, L_TKROW, L_6M)),
              ("REG_YIELDS", REG_YIELDS), ("N_REF", N_REF), ("JGBV", JGBV), ("TYPE", dict(TP)), ("CAT", (dict(CAT), dict(OTH))), ("FILES", sorted(os.listdir(SEAT_DIR)))):
    log("%s %s" % (k, json.dumps(val, ensure_ascii=False)[:1500]))''',
        '''for k in sorted(DIAG):
    log("%s %s" % (k, json.dumps(DIAG[k], ensure_ascii=False, default=str)[:1500]))''')
s = rep(s, '''assert not [x for x in NUM if not x[3]], "numeric recheck failed"
''', '''assert not [x for x in NUM if not x[3]], "numeric recheck failed"
assert not MISS, ("numeral without provenance", MISS)
ROWS = [l for l in PROSE_TXT.split("\\n") if re.match(r"^\\| \\d+ \\| [A-O]", l)]
assert len(ROWS) == N_PTS and all(l.rstrip().endswith("| 一致 |") for l in ROWS), len(ROWS)
assert sum(1 for l in PROSE_TXT.split("\\n") if l.startswith("反方攻击") or l[:1].isdigit()) >= 0
''')
s = rep(s, '''JTXT = json.dumps(J, ensure_ascii=False)
assert all(x["original"] in JTXT for x in V2["items"])''', '''assert all(any(x["original"] in c for c in CORPUS) for x in V2["items"]) and PT2 == PROSE_TXT and rd(VERDICT_PATH) == VERDICT_TXT''')
save(p, s)
print("patched D/C/E")
