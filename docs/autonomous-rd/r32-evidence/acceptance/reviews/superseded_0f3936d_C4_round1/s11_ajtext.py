#!/usr/bin/python3
"""Print judgment prose fields verbatim (read-only) for binding checks.
Usage: python3 -I s11_ajtext.py <agent_judgment.json> <out.txt>
"""
import json
import sys


def main():
    aj_path, out_path = sys.argv[1], sys.argv[2]
    with open(aj_path, "r", encoding="utf-8") as fh:
        aj = json.load(fh)
    out = []
    out.append("## agent_declaration")
    for k, v in aj["agent_declaration"].items():
        out.append("%s: %s" % (k, v))
    out.append("## quality_gate_notes (%d)" % len(aj["quality_gate_notes"]))
    for i, s in enumerate(aj["quality_gate_notes"]):
        out.append("[%d] %s" % (i, s))
    out.append("## l3.contradictions")
    for c in aj["l3"]["contradictions"]:
        out.append("### %s" % c["id"])
        for k, v in c.items():
            if k == "id":
                continue
            if isinstance(v, list):
                for x in v:
                    out.append("  %s- %s" % (k, x))
            else:
                out.append("  %s: %s" % (k, v))
    out.append("## l3.mechanism_chains")
    for m in aj["l3"]["mechanism_chains"]:
        out.append("### %s %s" % (m["id"], m.get("title")))
        for k, v in m.items():
            if k in ("id", "title", "links"):
                continue
            out.append("  %s: %s" % (k, json.dumps(v, ensure_ascii=False)))
        for l in m["links"]:
            out.append("  -- link %s" % json.dumps({k: v for k, v in l.items() if k != "text"}, ensure_ascii=False))
            out.append("     text: %s" % l["text"])
    out.append("## l4.scenarios")
    for s in aj["l4"]["scenarios"]:
        out.append("### %s" % s["id"])
        for k, v in s.items():
            if k in ("id", "rows"):
                continue
            out.append("  %s: %s" % (k, json.dumps(v, ensure_ascii=False)))
        for rk, rv in s["rows"].items():
            out.append("  rows.%s: %s" % (rk, json.dumps(rv, ensure_ascii=False)))
    out.append("## reader_map.headline_conclusion")
    out.append(aj["reader_map"]["headline_conclusion"])
    out.append("## reader_map.regions")
    for r in aj["reader_map"]["regions"]:
        out.append("### %s" % r["region"])
        for k, v in r.items():
            if k in ("region", "anchor_echo"):
                continue
            out.append("  %s: %s" % (k, v))
        out.append("  anchor_echo: " + json.dumps(r.get("anchor_echo"), ensure_ascii=False))
    out.append("## reader_map.transmission")
    for t in aj["reader_map"]["transmission"]:
        out.append("### %s" % t["chain_id"])
        for l in t["links"]:
            out.append("  " + json.dumps(l, ensure_ascii=False))
    out.append("## reader_map.turnings")
    for t in aj["reader_map"]["turnings"]:
        out.append("  " + json.dumps(t, ensure_ascii=False))
    out.append("## reader_map.turning_supplement")
    out.append(json.dumps(aj["reader_map"]["turning_supplement"], ensure_ascii=False, indent=1))
    out.append("## reader_map.history_zero_case_note")
    out.append(aj["reader_map"]["history_zero_case_note"])
    out.append("## reader_map.rates_decomposition")
    out.append(json.dumps(aj["reader_map"]["rates_decomposition"], ensure_ascii=False))
    out.append("## reader_map.asset_returns_echo")
    out.append(json.dumps(aj["reader_map"]["asset_returns_echo"], ensure_ascii=False, indent=1))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", out_path, "chars", sum(len(x) + 1 for x in out))


if __name__ == "__main__":
    main()
