import re, sys
txt = open(sys.argv[1], encoding="utf-8").read()
toks = sys.argv[2].split(",")
NUMTOK = re.compile(r"(?<![A-Za-z_0-9.])\d+(?:\.\d+)?")
lines = txt.split("\n")
for t in toks:
    hits = []
    for i, ln in enumerate(lines):
        for m in NUMTOK.finditer(ln):
            if m.group(0) == t:
                hits.append((i + 1, ln[max(0, m.start() - 70): m.end() + 50]))
                if len(hits) >= 3: break
        if len(hits) >= 3: break
    print("TOKEN", t, "n_shown", len(hits))
    for i, c in hits:
        print("   L%d: …%s…" % (i, c.replace("\n", " ")))
