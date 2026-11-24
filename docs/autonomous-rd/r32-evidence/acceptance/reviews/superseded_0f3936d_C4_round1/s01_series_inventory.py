#!/usr/bin/python3
"""Series inventory of the frozen snapshot series_store (read-only).
Usage: python3 -I s01_series_inventory.py <snapshot.json>
"""
import json
import sys


def main():
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as fh:
        snap = json.load(fh)
    store = snap["series_store"]
    print("research_as_of:", snap.get("research_as_of"), "target_date:", snap.get("target_date"))
    print("n_series:", len(store))
    print(f"{'metric':26s} {'n':>6s} {'first':>12s} {'last':>12s} {'last_val':>16s}  extra_keys")
    for k in sorted(store.keys()):
        s = store[k]
        if not isinstance(s, dict) or "dates" not in s:
            print(f"{k:26s} (not a dates/values series) type={type(s).__name__}")
            continue
        dates = s.get("dates") or []
        vals = s.get("values") or []
        extra = [x for x in s.keys() if x not in ("dates", "values")]
        first = dates[0] if dates else "-"
        last = dates[-1] if dates else "-"
        lastv = vals[-1] if vals else None
        print(f"{k:26s} {len(dates):6d} {first:>12s} {last:>12s} {str(lastv):>16s}  {extra}")
    # effective observation rule: count finite values
    print()
    print("series_store_clean keys:", sorted(snap.get("series_store_clean", {}).keys()))
    print("series_provenance keys:", sorted(snap.get("series_provenance", {}).keys()))
    print("quality:", json.dumps(snap.get("quality"), ensure_ascii=False))
    ga = snap.get("gate_a", {})
    print("gate_a.status:", ga.get("status"))
    print("gate_a.noncore_missing:", ga.get("noncore_missing"))
    print("gate_a.noncore_degraded:", ga.get("noncore_degraded"))
    print("gate_a.noncore_missing_detail:", json.dumps(ga.get("noncore_missing_detail"), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
