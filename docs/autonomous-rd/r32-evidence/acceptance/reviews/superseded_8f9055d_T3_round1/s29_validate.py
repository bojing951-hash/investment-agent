#!/usr/bin/python3 -I
"""Validate the two deliverables of the seat.

1. VERDICT JSON: strict UTF-8, exact key set/order/types per protocol section 6, verdict value, counts.
2. Sensitive-string scan of the two deliverables and of every script / intermediate file in this directory
   (top level and nested): model-vendor names (patterns assembled from code points, so no such name is
   written literally here) and secret-like strings (key / token / password patterns). The matcher is
   self-tested on an in-memory probe before scanning.

Args: <out_dir>
"""
import json
import os
import re
import sys

out_dir = sys.argv[1]
VP = os.path.join(out_dir, "VERDICT-round1.json")
PP = os.path.join(out_dir, "PROSE-round1.md")
errs = []


def cp(*codes):
    return "".join(chr(c) for c in codes)


# ---- 1. VERDICT structure
raw = open(VP, "rb").read()
try:
    vtxt = raw.decode("utf-8")
except UnicodeDecodeError as e:
    errs.append("VERDICT not valid UTF-8: %r" % e)
    vtxt = raw.decode("utf-8", "replace")
v = json.loads(vtxt)
EXP = ["seat", "reviewer", "verdict", "overall", "notes", "items", "must_fix", "counterexamples_sought",
       "recompute_points", "recompute_mismatches", "mismatch_details", "audited_at"]
if list(v.keys()) != EXP:
    errs.append("VERDICT keys/order != protocol: %s" % list(v.keys()))
TYPES = {"seat": str, "reviewer": str, "verdict": str, "overall": str, "notes": str, "items": list, "must_fix": list,
         "counterexamples_sought": list, "recompute_points": int, "recompute_mismatches": int, "mismatch_details": list,
         "audited_at": str}
for k, t in TYPES.items():
    if k in v and type(v[k]) is not t:
        errs.append("VERDICT[%s] has type %s, expected %s" % (k, type(v[k]).__name__, t.__name__))
if v.get("verdict") not in ("UPHELD", "REVISE"):
    errs.append("verdict value invalid: %r" % v.get("verdict"))
if v.get("verdict") == "UPHELD" and v.get("must_fix"):
    errs.append("UPHELD with non-empty must_fix")
if v.get("verdict") == "REVISE" and not v.get("must_fix"):
    errs.append("REVISE with empty must_fix")
if v.get("seat") != "semantic-audit-seat":
    errs.append("seat value invalid")
if v.get("reviewer") != "independent-zero-context-seat-r32-t3-round1":
    errs.append("reviewer value invalid")
if v.get("audited_at") != "2026-11-24":
    errs.append("audited_at invalid")
for it in v.get("items", []):
    if list(it.keys()) != ["severity", "where", "note", "original", "fix"]:
        errs.append("item keys invalid: %s" % list(it.keys()))
    if it.get("severity") not in ("MAJOR", "MINOR", "NIT"):
        errs.append("item severity invalid: %r" % it.get("severity"))
for s in v.get("counterexamples_sought", []):
    if not (isinstance(s, str) and s.startswith("反方攻击") and "→" in s):
        errs.append("counterexample format invalid: %r" % s[:40])
if not isinstance(v.get("recompute_points"), int) or v.get("recompute_points", 0) < 90:
    errs.append("recompute_points below protocol minimum (90)")
if v.get("recompute_mismatches") != len(v.get("mismatch_details", [])):
    errs.append("mismatch count != mismatch_details length")
n_major = sum(1 for it in v.get("items", []) if it["severity"] == "MAJOR")
if n_major and v.get("verdict") == "UPHELD":
    errs.append("UPHELD with MAJOR items")
# PROSE must carry the same verdict and counts
ptxt = open(PP, "rb").read().decode("utf-8")
if ("**裁决: %s**" % v.get("verdict")) not in ptxt:
    errs.append("PROSE verdict line missing")
for needle in ("范围内复算 %d 点" % v.get("recompute_points", -1), "反方攻击记录", "六查逐项结论", "问题清单", "复算清单"):
    if needle not in ptxt:
        errs.append("PROSE section/needle missing: %s" % needle)
if "�" in ptxt or "�" in vtxt:
    errs.append("replacement character present in an output")
print("VERDICT: verdict=%s points=%s mismatches=%s items=%d (MAJOR %d / MINOR %d / NIT %d) attacks=%d must_fix=%d bytes=%d"
      % (v.get("verdict"), v.get("recompute_points"), v.get("recompute_mismatches"), len(v.get("items", [])), n_major,
         sum(1 for it in v.get("items", []) if it["severity"] == "MINOR"),
         sum(1 for it in v.get("items", []) if it["severity"] == "NIT"),
         len(v.get("counterexamples_sought", [])), len(v.get("must_fix", [])), len(raw)))
print("PROSE bytes=%d lines=%d" % (len(ptxt.encode("utf-8")), ptxt.count("\n")))

# ---- 2. sensitive-string scan
VENDORS = {
    "vendor-a": cp(103, 108, 109), "vendor-b": cp(122, 105, 112, 117), "vendor-c": cp(98, 105, 103, 109, 111, 100, 101, 108),
    "vendor-d": cp(111, 112, 101, 110, 97, 105), "vendor-e": cp(97, 110, 116, 104, 114, 111, 112, 105, 99),
    "vendor-f": cp(99, 108, 97, 117, 100, 101), "vendor-g": cp(100, 101, 101, 112, 115, 101, 101, 107),
    "vendor-h": cp(113, 119, 101, 110), "vendor-i": cp(107, 105, 109, 105), "vendor-j": cp(109, 111, 111, 110, 115, 104, 111, 116),
    "vendor-k": cp(103, 101, 109, 105, 110, 105), "vendor-l": cp(108, 108, 97, 109, 97), "vendor-m": cp(109, 105, 115, 116, 114, 97, 108),
    "vendor-n": cp(100, 111, 117, 98, 97, 111), "vendor-o": cp(109, 105, 110, 105, 109, 97, 120), "vendor-p": cp(121, 105, 45, 108, 97, 114, 103, 101),
    "vendor-cn-1": cp(0x667A, 0x8C31), "vendor-cn-2": cp(0x901A, 0x4E49), "vendor-cn-3": cp(0x6587, 0x5FC3),
    "vendor-cn-4": cp(0x8C46, 0x5305), "vendor-cn-5": cp(0x8BAF, 0x98DE), "vendor-cn-6": cp(0x5546, 0x6C64),
    "vendor-cn-7": cp(0x6708, 0x4E4B, 0x6697, 0x9762), "vendor-cn-8": cp(0x9636, 0x8DC3), "vendor-cn-9": cp(0x9762, 0x58C1),
}
MODELNAMES = {"model-a": cp(103, 112, 116), "model-b": cp(99, 104, 97, 116, 103, 112, 116), "model-c": cp(115, 111, 110, 110, 101, 116),
              "model-d": cp(111, 112, 117, 115), "model-e": cp(104, 97, 105, 107, 117), "model-f": cp(117, 110, 99, 108, 117, 100, 101),
              "model-g": cp(99, 111, 100, 101, 120)}
SECRETS = [r"sk-[A-Za-z0-9_\-]{16,}", r"(?i)api[_\-]?key\s*[:=]", r"(?i)token\s*[:=]", r"(?i)bearer\s+[A-Za-z0-9._\-]{16,}",
           r"(?i)passw(?:or)?d\s*[:=]", r"(?i)secret\s*[:=]", r"(?i)authorization\s*[:=]", r"AKIA[0-9A-Z]{16}",
           r"gh[pousr]_[A-Za-z0-9]{20,}", r"xox[baprs]-[A-Za-z0-9-]{10,}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
           r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}"]
ALLNAMES = list(VENDORS.items()) + list(MODELNAMES.items())


def name_finder(text):
    """Yield (tag, start, end) for every vendor / model-name occurrence in text."""
    low = text.lower()
    for tag, pat in ALLNAMES:
        for m in re.finditer(re.escape(pat.lower()), low):
            yield tag, m.start(), m.end()


# self-test of the matcher on in-memory probes (nothing is written)
_self = 0
for _tag, _pat in ALLNAMES:
    _probe = "甲乙 " + _pat.upper() + "-9.9 丙;前缀" + _pat + "后缀"
    # one name is contained in another, so count only the hits that carry the tested tag
    if sum(1 for tg, _a, _b in name_finder(_probe) if tg == _tag) != 2:
        errs.append("matcher self-test failed for %s" % _tag)
    _self += 1
_probe = "probe one two three"
if list(name_finder(_probe)):
    errs.append("matcher self-test: false positive on clean probe")
print("matcher self-test: %d patterns x 2 placements, clean probe" % _self)

hits = 0
scanned = 0
for root, _dirs, files in os.walk(out_dir):
    for fn in sorted(files):
        p = os.path.join(root, fn)
        if fn == "_protocol.md":
            continue
        if os.path.islink(p):
            continue
        try:
            t = open(p, "rb").read().decode("utf-8")
        except UnicodeDecodeError:
            t = open(p, "rb").read().decode("latin-1")
        scanned += 1
        rel = os.path.relpath(p, out_dir)
        low = t.lower()
        for tag, a, b in name_finder(t):
            print("  HIT %s | %s | ...%s..." % (tag, rel, low[max(0, a - 25):b + 25].replace("\n", " ")))
            hits += 1
        for pat in SECRETS:
            for m in re.finditer(pat, t):
                ctx = t[max(0, m.start() - 25):m.end() + 25].replace("\n", " ")
                if rel == os.path.basename(__file__):
                    print("  (self-scan-pattern, this script only) %s | ...%s..." % (pat[:24], ctx))
                else:
                    print("  SECRET-HIT %s | %s | ...%s..." % (pat[:24], rel, ctx))
                    hits += 1
# the protocol file is not a seat product; scanned separately for information only
t = open(os.path.join(out_dir, "_protocol.md"), "rb").read().decode("utf-8")
for tag, a, b in name_finder(t):
    print("  (information only, not a seat product) _protocol.md contains %s" % tag)
print("scanned %d files; sensitive-string hits in seat scripts/outputs: %d" % (scanned, hits))
print("VALIDATION", "PASS" if not errs and not hits else "FAIL")
for e in errs:
    print("  ERR", e)
sys.exit(0 if not errs and not hits else 1)
