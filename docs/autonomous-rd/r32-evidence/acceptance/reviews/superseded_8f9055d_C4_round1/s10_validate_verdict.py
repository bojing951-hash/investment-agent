#!/usr/bin/python3
"""Seat script: validate VERDICT-round1.json against the protocol structure and the audited face (read-only).
Usage: /usr/bin/python3 -I s10_validate_verdict.py <verdict.json> <agent_judgment.json> <s05_output.txt> <snapshot.json>
Prints PASS/FAIL per check and exits non-zero on any FAIL.
"""
import json
import re
import sys

REQUIRED = ["seat", "reviewer", "verdict", "overall", "notes", "items", "must_fix", "counterexamples_sought",
            "recompute_points", "recompute_mismatches", "mismatch_details", "audited_at"]
FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  -> " + detail) if detail else ""))
    if not ok:
        FAILS.append(name)


def load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def main():
    vpath, jpath, opath, spath = sys.argv[1:5]
    raw = load(vpath)
    try:
        v = json.loads(raw)
    except Exception as ex:
        check("verdict file parses as UTF-8 JSON", False, "%s: %s" % (type(ex).__name__, ex))
        return finish()
    check("verdict file parses as UTF-8 JSON", True)
    check("top-level keys exactly as protocol section 6", list(v.keys()) == REQUIRED, str(list(v.keys())))
    check("verdict / overall are UPHELD or REVISE and equal",
          v["verdict"] in ("UPHELD", "REVISE") and v["overall"] == v["verdict"])
    check("seat / reviewer / audited_at literals",
          v["seat"] == "semantic-audit-seat" and v["reviewer"] == "independent-zero-context-seat-r32-c4-round1"
          and v["audited_at"] == "2026-11-24")
    m = re.match(r"POINTS=(\d+) HITS=(\d+) MISMATCHES=(\d+) ERR=(\d+)", load(opath).strip().splitlines()[0])
    pts, hits, mis, err = [int(x) for x in m.groups()]
    check("recompute_points equals final script run", v["recompute_points"] == pts, "%s vs %s" % (v["recompute_points"], pts))
    check("recompute_mismatches equals final script run", v["recompute_mismatches"] == mis, "%s vs %s" % (v["recompute_mismatches"], mis))
    check("script ERR count is zero", err == 0)
    check("recompute points >= protocol minimum 90", pts >= 90)
    sev = [it["severity"] for it in v["items"]]
    check("item severities are MAJOR/MINOR/NIT", all(s in ("MAJOR", "MINOR", "NIT") for s in sev), str(sev))
    majors = [it for it in v["items"] if it["severity"] == "MAJOR"]
    check("every MAJOR item has non-empty original and fix",
          all(it.get("original") and it.get("fix") for it in majors))
    check("verdict is REVISE iff at least one MAJOR item", (v["verdict"] == "REVISE") == (len(majors) > 0))
    check("must_fix lists one entry per MAJOR location when REVISE",
          (len(v["must_fix"]) >= 1) if majors else (v["must_fix"] == []))
    check("notes mention the hit/mismatch counts",
          ("%d" % pts) in v["notes"] and ("%d" % mis) in v["notes"] and ("%d" % hits) in v["notes"])

    # original sentences must occur verbatim in the audited judgment text
    jtext = load(jpath)
    for it in v["items"]:
        for piece in it["original"].split(" ‖ "):
            check("original occurs verbatim in agent_judgment.json [%s]" % it["severity"], piece in jtext,
                  piece[:40])

    # mismatch ids in the verdict equal the mismatch rows of the final script run
    out = load(opath)
    ids = re.findall(r"^  (\S+) \| ", out, flags=re.M)
    vids = [d["id"] for d in v["mismatch_details"]]
    check("mismatch_details ids equal script mismatch rows", sorted(vids) == sorted(ids), "%s vs %s" % (vids, ids))

    # every number used in the MAJOR fix sentences is recomputed from the frozen snapshot
    snap = json.loads(load(spath))
    ss = snap["series_store"]

    def at(metric, day):
        d = ss[metric]["dates"]
        return ss[metric]["values"][d.index(day)]

    def pct(a, b):
        return (b / a - 1.0) * 100.0

    def mean(metric, a, b):
        vals = [x for d, x in zip(ss[metric]["dates"], ss[metric]["values"]) if a <= d <= b]
        return sum(vals) / float(len(vals))

    w0, w1, w2 = at("WTI_F", "2026-08-21"), at("WTI_F", "2026-10-30"), at("WTI_F", "2026-11-23")
    b0, b1, b2 = at("BRENT_F", "2026-08-21"), at("BRENT_F", "2026-10-30"), at("BRENT_F", "2026-11-23")
    s0, s1 = at("WTI_SPOT_M", "2026-08-01"), at("WTI_SPOT_M", "2026-10-01")
    last_spot = ss["WTI_SPOT_M"]["dates"][-1]
    facts = {
        "WTI 08-21": round(w0, 2), "WTI 10-30": round(w1, 2), "WTI 11-23": round(w2, 2),
        "BRENT 08-21": round(b0, 2), "BRENT 10-30": round(b1, 2), "BRENT 11-23": round(b2, 2),
        "WTI->10-30 %": round(pct(w0, w1), 2), "WTI full %": round(pct(w0, w2), 2), "WTI reversal %": round(pct(w1, w2), 2),
        "BRENT->10-30 %": round(pct(b0, b1), 2), "BRENT full %": round(pct(b0, b2), 2), "BRENT reversal %": round(pct(b1, b2), 2),
        "SPOT 08": s0, "SPOT 10": s1, "SPOT %": round(pct(s0, s1), 2),
        "WTI mean 08": round(mean("WTI_F", "2026-08-01", "2026-08-31"), 2), "WTI mean 10": round(mean("WTI_F", "2026-10-01", "2026-10-31"), 2),
        "WTI 09-16 vs 08-21 %": round(pct(w0, at("WTI_F", "2026-09-16")), 2),
        "WTI 09-18 vs 08-21 %": round(pct(w0, at("WTI_F", "2026-09-18")), 2),
    }
    print("recomputed fix-sentence facts:", json.dumps(facts, ensure_ascii=False))
    expected = {"WTI 08-21": 87.06, "WTI 10-30": 104.12, "WTI 11-23": 82.02, "BRENT 08-21": 94.39, "BRENT 10-30": 117.64,
                "BRENT 11-23": 88.19, "WTI->10-30 %": 19.60, "WTI full %": -5.79, "WTI reversal %": -21.23,
                "BRENT->10-30 %": 24.63, "BRENT full %": -6.57, "BRENT reversal %": -25.03, "SPOT 08": 83.9, "SPOT 10": 102.07,
                "SPOT %": 21.66, "WTI mean 08": 82.45, "WTI mean 10": 96.94, "WTI 09-16 vs 08-21 %": 17.65,
                "WTI 09-18 vs 08-21 %": 15.21}
    check("fix-sentence numbers equal snapshot recomputation", all(abs(facts[k] - val) < 0.006 for k, val in expected.items()),
          str({k: (facts[k], val) for k, val in expected.items() if abs(facts[k] - val) >= 0.006}))
    check("WTI_SPOT_M series ends 2026-10 (no November monthly value)", last_spot == "2026-10-01", last_spot)
    fix_all = " ".join(it["fix"] for it in majors) + " " + " ".join(v["must_fix"])
    needed = ["87.06", "104.12", "82.02", "+19.60%", "-5.79%", "21.23%", "94.39", "117.64", "88.19", "+24.63%", "-6.57%", "25.03%",
              "83.9", "102.07", "+21.66%", "82.45", "96.94", "17.65%", "15.21%", "2026-08-21", "2026-10-30", "2026-11-23",
              "2026-09-16", "2026-09-18"]
    check("all needed figures appear in MAJOR fix / must_fix text", all(n in fix_all for n in needed),
          str([n for n in needed if n not in fix_all]))
    check("MAJOR fix keeps the surviving conclusion", all("不足以区分两解释" in it["fix"] for it in majors))
    finish()


def finish():
    print("RESULT: %s (%d FAIL)" % ("OK" if not FAILS else "FAILED", len(FAILS)))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
