import sys
pd, pe = sys.argv[1:3]
def patch(p, R):
    s = open(p, encoding="utf-8").read()
    for a, b in R:
        assert s.count(a) == 1, (p, s.count(a), a[:50])
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s)
    print("patched", p, len(R))
patch(pd, [('②点值锚格 94 点全中;"', '②点值锚格 " + str(SEC["B②点值锚格"]["ok"]) + " 点全中;"')])
patch(pe, [
    ('NARR = P[:I4S] + P[I4e:I11S] if False else P[:I4S] + P[I4E:I11S]', 'NARR = P[:I4S] + P[I4E:I11S]'),
    ('" ".join(list(ENTRY.values()) + list(NEXT_REL.values()) + RUNS and ["%d" % x for r in RUNS for x in r[:4]])', '" ".join(list(ENTRY.values()) + list(NEXT_REL.values()) + ["%d" % x for r in RUNS for x in r[:4]])'),
    ('    log("CHECK-ONLY: nothing written")', '    open(os.path.join(SEAT_DIR, "s12_preview_prose.txt"), "w", encoding="utf-8", newline="\\n").write(PROSE_TXT)\n    log("CHECK-ONLY: nothing written (preview in s12_preview_prose.txt)")'),
])
