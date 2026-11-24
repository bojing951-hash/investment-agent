#!/usr/bin/env python3
"""Seat script: dump S5/S6/S8 step envelopes (full), evidence_index summary, views_digest,
AGENT_SEAT_ENVELOPE (all read-only faces listed in protocol §1).
Usage: python3 -I extract_misc.py <report.json> <evidence_index.json> <views_digest.json>
                                      <AGENT_SEAT_ENVELOPE.json> <out.txt>
"""
import json
import sys


def main():
    rep_p, ev_p, vw_p, env_p, out_p = sys.argv[1:6]
    with open(rep_p, encoding="utf-8") as f:
        rep = json.load(f)
    orig = sys.stdout
    sys.stdout = open(out_p, "w", encoding="utf-8")
    try:
        steps = rep["steps"]
        for st in steps:
            name = st.get("name") or st.get("step")
            if name in ("S5_compare", "S6_analog", "S8_grounded_qa", "S7_mode_gate", "S10_selfcheck", "S11_archive"):
                print(f"\n===== STEP {name} =====")
                for k in st:
                    if k == "envelope":
                        continue
                    print(f"  {k} = {json.dumps(st[k], ensure_ascii=False, default=str)[:1200]}")
                env = st.get("envelope")
                if isinstance(env, dict):
                    print("  warnings =", json.dumps(env.get("warnings"), ensure_ascii=False))
                    data = env.get("data")
                    if name == "S5_compare" and isinstance(data, dict):
                        # drop bulky series
                        for side in data.get("sides", []):
                            side.pop("dates", None)
                            side.pop("values", None)
                        print("  data =", json.dumps(data, ensure_ascii=False, default=str)[:6000])
                    elif name == "S6_analog" and isinstance(data, dict):
                        print("  data keys =", list(data.keys()))
                        for k, v in data.items():
                            if k == "state_vector":
                                continue
                            print(f"  data.{k} = {json.dumps(v, ensure_ascii=False, default=str)[:2500]}")
                    else:
                        print("  data =", json.dumps(data, ensure_ascii=False, default=str)[:3000])
                else:
                    for k in st:
                        print(f"  {k} = {json.dumps(st[k], ensure_ascii=False, default=str)[:1500]}")

        print("\n===== evidence_index.json =====")
        with open(ev_p, encoding="utf-8") as f:
            ev = json.load(f)
        if isinstance(ev, dict):
            print("top keys:", list(ev.keys()))
            for k, v in ev.items():
                if isinstance(v, list):
                    print(f"{k}: list len {len(v)}")
                    for row in v[:80]:
                        print("   ", json.dumps(row, ensure_ascii=False, default=str)[:400])
                else:
                    print(f"{k} = {json.dumps(v, ensure_ascii=False, default=str)[:800]}")
        else:
            print("list len", len(ev))
            for row in ev[:80]:
                print("   ", json.dumps(row, ensure_ascii=False, default=str)[:400])

        print("\n===== views_digest.json =====")
        with open(vw_p, encoding="utf-8") as f:
            vw = json.load(f)
        print(json.dumps(vw, ensure_ascii=False, default=str)[:4000])

        print("\n===== AGENT_SEAT_ENVELOPE.json =====")
        with open(env_p, encoding="utf-8") as f:
            en = json.load(f)
        print(json.dumps(en, ensure_ascii=False, default=str, indent=1)[:12000])

        print("\n===== report.json run block =====")
        run = rep.get("run", {})
        for k in run:
            v = run[k]
            s = json.dumps(v, ensure_ascii=False, default=str)
            print(f"run.{k} = {s[:1500]}")
    finally:
        sys.stdout.close()
        sys.stdout = orig


if __name__ == "__main__":
    main()
