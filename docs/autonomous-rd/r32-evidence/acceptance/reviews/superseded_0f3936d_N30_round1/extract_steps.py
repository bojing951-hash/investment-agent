#!/usr/bin/env python3
"""Seat script: summarise steps[*] envelopes in report.json (engine deterministic faces).
Usage: python3 -I extract_steps.py <report.json> <out.txt>
"""
import json
import sys


def short(v, n=600):
    s = json.dumps(v, ensure_ascii=False, default=str)
    return s if len(s) <= n else s[:n] + "…"


def main():
    rep_p, out_p = sys.argv[1], sys.argv[2]
    with open(rep_p, encoding="utf-8") as f:
        rep = json.load(f)
    orig = sys.stdout
    sys.stdout = open(out_p, "w", encoding="utf-8")
    try:
        steps = rep["steps"]
        print("n steps:", len(steps))
        print("step keys:", sorted(steps[0].keys()))
        for i, st in enumerate(steps):
            name = st.get("name") or st.get("step") or st.get("id")
            env = st.get("envelope")
            print(f"\n[{i}] {name} | status={st.get('status')} ok={st.get('ok')} semantic={st.get('semantic')} "
                  f"| other keys={[k for k in st.keys() if k not in ('envelope',)]}")
            if isinstance(env, dict):
                ek = list(env.keys())
                print("   envelope keys:", ek)
                for k in ek:
                    v = env[k]
                    if isinstance(v, (dict, list)):
                        print(f"   - {k}: {short(v, 1500)}")
                    else:
                        print(f"   - {k} = {short(v, 400)}")
            else:
                print("   envelope:", short(env, 800))
    finally:
        sys.stdout.close()
        sys.stdout = orig


if __name__ == "__main__":
    main()
