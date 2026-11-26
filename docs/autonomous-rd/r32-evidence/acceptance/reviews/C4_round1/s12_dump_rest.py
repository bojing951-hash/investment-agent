#!/usr/bin/python3 -I
# s12: 打印受审稿中六查所需的其余原文(并列解释/机制链各环/转折/走位 CN·EA)与反方攻击所需直算值。只读, 仅打印。
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rc_lib import *
snap_p, aj_p, outdir = sys.argv[1:4]
snap = json.load(open(snap_p, encoding="utf-8")); aj = json.load(open(aj_p, encoding="utf-8"))
SS = snap["series_store"]
print("##### L3 contradictions: 并列解释与证据引用")
for c in aj["l3"]["contradictions"]:
    print("\n[%s] refs=%s" % (c.get("id"), c.get("evidence_refs")))
    for i, x in enumerate(c["competing_explanations"]):
        print("  解释%d: %s" % (i + 1, x))
print("\n##### L3 mechanism chains")
for ch in aj["l3"]["mechanism_chains"]:
    print("\n[%s] keys=%s" % (ch.get("id"), list(ch.keys())))
    for k, v in ch.items():
        if k not in ("links", "id"):
            print("  %s: %s" % (k, json.dumps(v, ensure_ascii=False)[:500]))
    for i, l in enumerate(ch["links"]):
        print("  -- link %d keys=%s refs=%s" % (i, list(l.keys()), l.get("evidence_refs")))
        for k, v in l.items():
            if k not in ("evidence_refs",) and not (isinstance(v, str) and len(v) > 700):
                print("     %s: %s" % (k, v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)))
            elif isinstance(v, str):
                print("     %s: %s…(%d 字)" % (k, v[:700], len(v)))
print("\n##### reader_map.turnings")
for t in aj["reader_map"]["turnings"]:
    print(json.dumps(t, ensure_ascii=False, indent=1))
print("\n##### reader_map.regions (label + from_to)")
for r in aj["reader_map"]["regions"]:
    print("[%s] %s | %s\n" % (r.get("region") or r.get("id"), r.get("label"), r.get("from_to")))
    print("   其他键:", {k: (v if not isinstance(v, str) or len(v) < 160 else v[:160] + "…") for k, v in r.items() if k not in ("from_to", "label")})
print("\n##### reader_map.transmission[0] 其他键")
tr = aj["reader_map"]["transmission"][0]
for k, v in tr.items():
    if k != "links":
        print("  %s: %s" % (k, json.dumps(v, ensure_ascii=False)[:600]))
print("\n##### 反方攻击直算值")
for m in ("CN_CPI_YOY", "CN_PPI_YOY"):
    print(m, [(d[:7], v) for d, v in series(SS, m) if "2026-05" <= d[:7] <= "2026-10"])
print("USDJPY 10-20→11-19 %.4f%%  USDCNY %.4f%%" % (pct(at(SS, "USDJPY", "2026-10-20"), at(SS, "USDJPY", "2026-11-19")), pct(at(SS, "USDCNY", "2026-10-20"), at(SS, "USDCNY", "2026-11-19"))))
print("USDJPY 10-23→11-23 %.4f%%  10-23→11-20 %.4f%%" % (pct(at(SS, "USDJPY", "2026-10-23"), at(SS, "USDJPY", "2026-11-23")), pct(at(SS, "USDJPY", "2026-10-23"), at(SS, "USDJPY", "2026-11-20"))))
print("WTI_F 11-09..11-23:", [(d, v) for d, v in series(SS, "WTI_F") if d >= "2026-11-09"])
print("WTI_F 8月下旬低于锚:", [(d, v) for d, v in series(SS, "WTI_F") if "2026-08-21" <= d <= "2026-08-31"])
print("JP monthly:", [(d[:7], v) for d, v in series(SS, "JP_POLICY_RATE") if d[:7] >= "2026-04"])
