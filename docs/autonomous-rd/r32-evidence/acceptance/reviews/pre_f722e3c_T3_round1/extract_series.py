#!/usr/bin/env python3
"""Seat-owned read-only series extractor.
Usage: python3 -I extract_series.py <snapshot.json> <mode> [args]
mode:
  meta                      -> top-level meta (research_as_of/target_date/gate_a/quality)
  monthly <SID> [<SID>...]  -> full date/value list for monthly series
  daily <SID> <from> <to>   -> observations in [from,to]
  last <SID> <n>            -> last n observations
  at <SID> <date> [<date>...] -> observation at exact date (or None) + nearest neighbours
  facts <SID> [<SID>...]    -> facts rows for metric ids
  has <SID>                 -> whether key exists in series_store
"""
import json
import sys


def main(argv):
    path = argv[0]
    mode = argv[1]
    with open(path, "r", encoding="utf-8") as fh:
        snap = json.load(fh)
    out = sys.stdout
    if mode == "meta":
        out.write(f"snapshot_id={snap['snapshot_id']}\n")
        out.write(f"research_as_of={snap['research_as_of']}\n")
        out.write(f"target_date={snap['target_date']}\n")
        out.write(f"timezone={snap['timezone']}\n")
        out.write("gate_a=" + json.dumps(snap["gate_a"], ensure_ascii=False) + "\n")
        out.write("quality=" + json.dumps(snap["quality"], ensure_ascii=False) + "\n")
        out.write("notes=" + json.dumps(snap["notes"], ensure_ascii=False) + "\n")
        out.write("reconciliation=" + json.dumps(snap["reconciliation"], ensure_ascii=False, indent=1) + "\n")
        return
    store = snap["series_store"]
    if mode == "has":
        for sid in argv[2:]:
            out.write(f"{sid}: {'IN' if sid in store else 'ABSENT'}\n")
        return
    if mode == "facts":
        want = set(argv[2:])
        for f in snap["facts"]:
            if f.get("metric_id") in want:
                out.write(json.dumps(f, ensure_ascii=False) + "\n")
        return
    if mode == "monthly":
        for sid in argv[2:]:
            s = store.get(sid)
            if s is None:
                out.write(f"## {sid}: ABSENT\n")
                continue
            ds, vs = s["dates"], s["values"]
            out.write(f"## {sid}: n={len(ds)} first={ds[0] if ds else None} last={ds[-1] if ds else None}\n")
            for d, v in zip(ds, vs):
                out.write(f"{sid}\t{d}\t{v}\n")
        return
    if mode == "daily":
        sid, frm, to = argv[2], argv[3], argv[4]
        s = store[sid]
        for d, v in zip(s["dates"], s["values"]):
            if frm <= d <= to:
                out.write(f"{sid}\t{d}\t{v}\n")
        return
    if mode == "last":
        sid, n = argv[2], int(argv[3])
        s = store[sid]
        ds, vs = s["dates"], s["values"]
        out.write(f"## {sid}: n={len(ds)} first={ds[0] if ds else None} last={ds[-1] if ds else None}\n")
        for d, v in list(zip(ds, vs))[-n:]:
            out.write(f"{sid}\t{d}\t{v}\n")
        return
    if mode == "at":
        sid = argv[2]
        s = store[sid]
        ds, vs = s["dates"], s["values"]
        for q in argv[3:]:
            hit = None
            for i, d in enumerate(ds):
                if d == q:
                    hit = (d, vs[i], i)
                    break
            if hit:
                out.write(f"{sid}\t{q}\tEXACT\t{hit[1]}\n")
            else:
                # nearest neighbours
                before = None
                after = None
                for d, v in zip(ds, vs):
                    if d < q and (before is None or d > before[0]):
                        before = (d, v)
                    if d > q and (after is None or d < after[0]):
                        after = (d, v)
                out.write(f"{sid}\t{q}\tMISSING\tbefore={before}\tafter={after}\n")
        return
    out.write("unknown mode\n")


if __name__ == "__main__":
    main(sys.argv[1:])
