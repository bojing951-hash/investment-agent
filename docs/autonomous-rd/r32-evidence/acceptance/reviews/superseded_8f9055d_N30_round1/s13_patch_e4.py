import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
def rep(s, a, b, cnt=1):
    assert s.count(a) == cnt, (s.count(a), a[:80])
    return s.replace(a, b)
# 1. main table rows kept as a list
s = rep(s, '''for i, p in enumerate(PTS, 1):
    P.append("| %d | %s | %s | %s | %s | %s | %s |" % (i, p["section"], cell(p["where"]), cell(p["claim"]), cell(p["computed"]), cell(p["source"]), "一致" if p["ok"] else "偏离"))
''', '''MAIN_ROWS = ["| %d | %s | %s | %s | %s | %s | %s |" % (i, p["section"], cell(p["where"]), cell(p["claim"]), cell(p["computed"]), cell(p["source"]), "一致" if p["ok"] else "偏离")
             for i, p in enumerate(PTS, 1)]
P.extend(MAIN_ROWS)
''')
# 2. six-check bullets already carry their own bullet marker
s = rep(s, '''    for b in bs:
        P.append("- " + b)''', '''    assert all(b.startswith("- ") for b in bs)
    for b in bs:
        P.append(b)''')
# 3. supplementary / numeric tables
s = rep(s, 'P.append("生成器内补充核对(第 %d 组起;不计数,写出前要求全部成立;第三路数值复算 %d 项)" % (1, len(NUM)))',
        'P.append("生成器内补充核对(%d 项;不计数,写出前要求全部成立)" % len(SUP))')
s = rep(s, '''for lab, got, exp, ok in NUM:
    if not ok:
        P.append("| 数值 | %s: 直算 %s 对期望 %s | 不成立 |" % (cell(lab), cell(got), cell(exp)))
P.append("")''', '''P.append("")
P.append("生成器内第三路数值复算(%d 项;不计数,写出前要求全部成立;期望值=本席叙述所引、与判断档书写同值的数值,直算值由只读输入在本脚本内重算)" % len(NUM))
P.append("")
P.append("| 序 | 数值项 | 直算值 | 期望值 | 结果 |")
P.append("|---|---|---|---|---|")
for i, (lab, got, exp, ok) in enumerate(NUM, 1):
    P.append("| %d | %s | %s | %s | %s |" % (i, cell(lab), cell(got), cell(exp), "一致" if ok else "偏离"))
P.append("")''')
# 4. interruption disclosure
s = rep(s, '"5. 过程中断如实披露: 单次大文件写入失败一次、接口速率限制中断一次、输出长度上限中断一次(此后分段写入生成器),均与受审内容无关,受审版本未变(印章与快照 id 在每次续跑时重新读取核对)。"',
        '"5. 过程中断如实披露: 本席工作曾多次因席位接口层中断(单次大文件写入失败、接口速率限制、输出长度上限、上下文压缩),均与受审内容无关;生成器因此分段写成。每次续跑都重新读取只读输入并核对代码印章(run.git_head 与 MAP 印章同值)与快照 research_as_of,受审版本未变。"')
# 5. diagnostics additions
s = rep(s, '"FTL_CH": FTL_CH,', '"FTL_CH": FTL_CH, "MAY_PUB": (EA_MAY_PUB, JP_MAY_PUB),')
# 6. pre-write assertions (run in both modes)
a = s.index('if CHECK_ONLY:\n    open(os.path.join(SEAT_DIR, "s12_preview_prose.txt")')
b = s.index('assert not os.path.exists(PROSE_PATH) and not os.path.exists(VERDICT_PATH), "deliverable already exists"\n')
new_block = '''# ---- guards: no vendor names / no credentials in the deliverables (patterns assembled from fragments), structure checks
_W = [x + y for x, y in (("Ant", "hropic"), ("cla", "ude"), ("open", "ai"), ("chat", "gpt"), ("deep", "seek"), ("q", "wen"), ("tong", "yi"), ("gem", "ini"), ("lla", "ma"),
                          ("mis", "tral"), ("mo", "onshot"), ("ki", "mi"), ("gro", "k"), ("bai", "chuan"), ("hun", "yuan"), ("dou", "bao"), ("min", "imax"), ("step", "fun"),
                          ("ern", "ie"), ("son", "net"), ("op", "us"), ("hai", "ku"), ("fab", "le"))] + ["\\u6587\\u5fc3", "\\u901a\\u4e49", "\\u667a\\u8c31", "\\u8c46\\u5305"]
SENS_RES = [re.compile("(?<![A-Za-z0-9_])(?:" + "|".join(_W) + ")(?![A-Za-z0-9_])", re.IGNORECASE), re.compile("g" + "lm", re.IGNORECASE), re.compile("zhi" + "pu", re.IGNORECASE)]
_SECRET_SRC = ["sk-[A-Za-z0-9]{16,}", "bearer\\\\s+[A-Za-z0-9._\\\\-]{16,}", "AKIA[0-9A-Z]{16}", "gh[pousr]_[A-Za-z0-9]{20,}", "xox[baprs]-[A-Za-z0-9\\\\-]{10,}",
               "(api[_ \\\\-]?key|access[_ \\\\-]?token|secret[_ \\\\-]?key|password|passwd)\\\\s*[:=]\\\\s*[\\"']?[A-Za-z0-9_.\\\\-]{10,}"]
for _q in _SECRET_SRC:
    SENS_RES.append(re.compile(_q, re.IGNORECASE))


def sensitive_hits(txt):
    hits = []
    for k, rx in enumerate(SENS_RES):
        for m in rx.finditer(txt):
            hits.append((k, m.start(), len(m.group(0))))
    return hits


def prewrite_asserts():
    assert not [q for q in SUP if not q[2]], "supplementary check failed"
    assert not [x for x in NUM if not x[3]], "numeric recheck failed"
    assert not MISS, ("numeral without provenance", MISS)
    assert len(MAIN_ROWS) == N_PTS and all(l.rstrip().endswith("| 一致 |") for l in MAIN_ROWS), len(MAIN_ROWS)
    assert all(l.startswith("| %d | " % i) for i, l in enumerate(MAIN_ROWS, 1))
    assert list(V.keys()) == KEYS and V["verdict"] in ("UPHELD", "REVISE") and V["overall"] == V["verdict"] and V["must_fix"] == []
    assert V["recompute_points"] == N_PTS and V["recompute_mismatches"] == N_MIS and V["mismatch_details"] == [] and V["audited_at"] == AUDITED_AT
    assert len(ITEMS) == N_MIN + N_NIT and all(any(x["original"] in c for c in CORPUS) for x in ITEMS)
    assert all(set(x.keys()) == {"severity", "where", "note", "original", "fix"} for x in ITEMS) and all(x["where"].startswith("agent_judgment.json: ") for x in ITEMS)
    assert len(V["counterexamples_sought"]) == N_ATT and V["notes"] == NOTES and NOTES in PROSE_TXT
    for _t in ("\\n## 1 裁决依据摘要", "\\n## 4 逐点复算清单", "\\n## 5 二路独立复核", "\\n## 6 六查逐项结论", "\\n## 7 反方攻击记录", "\\n## 8 问题清单", "\\n## 9 引擎面观察", "\\n## 10 未核验事项", "\\n## 11 席位文件清单"):
        assert PROSE_TXT.count(_t) == 1, _t
    assert "| 偏离 |" not in PROSE_TXT and "| 不成立" not in PROSE_TXT and PROSE_TXT.count("| 一致 |") >= N_PTS + I["ok"] + len(NUM)
    assert "\\n- - " not in PROSE_TXT
    _hits = sensitive_hits(PROSE_TXT + "\\n" + VERDICT_TXT)
    assert not _hits, ("sensitive name/credential pattern hit in deliverables (pattern index, offset, length)", _hits[:8])
    assert json.loads(VERDICT_TXT) == V


if CHECK_ONLY:
    try:
        prewrite_asserts()
        log("PREWRITE-ASSERTS: all passed")
    except AssertionError as e:
        log("PREWRITE-ASSERT-FAIL %r" % (e.args,))
    open(os.path.join(SEAT_DIR, "s12_preview_prose.txt"), "w", encoding="utf-8", newline="\\n").write(PROSE_TXT)
    log("CHECK-ONLY: nothing written (preview in s12_preview_prose.txt)")
    sys.exit(0)
prewrite_asserts()
'''
s = s[:a] + new_block + s[b:]
# 7. post-write validation
i = s.index('ROWS = [l for l in PT2.split("\\n") if re.match(r"^\\| \\d+ \\| [A-O]", l)]\nassert len(ROWS) == N_PTS and all(l.rstrip().endswith("| 一致 |") for l in ROWS), len(ROWS)\n')
j = s.index('assert all(any(x["original"] in c for c in CORPUS) for x in V2["items"])', i)
s = s[:i] + 'assert all(l in PT2 for l in MAIN_ROWS) and len(MAIN_ROWS) == N_PTS\n' + s[j:]
s = rep(s, 'PT2 == PROSE_TXT and rd(VERDICT_PATH) == VERDICT_TXT', 'PT2 == PROSE_TXT and rd(VERDICT_PATH) == VERDICT_TXT and V2["items"] == ITEMS')
open(p, "w", encoding="utf-8").write(s)
print("part E patched")
