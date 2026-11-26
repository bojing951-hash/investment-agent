#!/usr/bin/python3
"""Dump release calendar (frozen copy) + registry summary (read-only).
Usage: python3 -I s03_calendar_dump.py <release_calendar.json> <metric_registry.json> <out.txt>
"""
import json
import sys


def main():
    cal_path, reg_path, out_path = sys.argv[1:4]
    with open(cal_path, "r", encoding="utf-8") as fh:
        cal = json.load(fh)
    with open(reg_path, "r", encoding="utf-8") as fh:
        reg = json.load(fh)
    out = []
    out.append("calendar version=%s created=%s updated=%s" % (cal.get("version"), cal.get("created"), cal.get("updated")))
    out.append("spec=" + str(cal.get("spec")))
    out.append("=== batches (%d)" % len(cal.get("batches", [])))
    for b in cal.get("batches", []):
        out.append(json.dumps(b, ensure_ascii=False, sort_keys=True))
    out.append("=== entries (%d)" % len(cal.get("entries", [])))
    for e in cal.get("entries", []):
        out.append(json.dumps(e, ensure_ascii=False, sort_keys=True))
    out.append("=== registry top keys: %s" % list(reg.keys()))
    metrics = reg.get("metrics")
    if isinstance(metrics, dict):
        out.append("registry metrics n=%d (dict)" % len(metrics))
        for k in sorted(metrics.keys()):
            m = metrics[k]
            if not isinstance(m, dict):
                out.append("%s: %r" % (k, m))
                continue
            sub = {kk: m.get(kk) for kk in ("economy", "dimension", "frequency", "unit", "display_name", "criticality", "release_rule", "publication_rule", "history_source", "collector", "source", "vintage_semantics", "release_lag_days", "stale_window_days") if kk in m}
            out.append("%s: %s" % (k, json.dumps(sub, ensure_ascii=False, sort_keys=True)))
    elif isinstance(metrics, list):
        out.append("registry metrics n=%d (list)" % len(metrics))
        for m in metrics:
            mid = m.get("metric_id") if isinstance(m, dict) else m
            if isinstance(m, dict):
                sub = {kk: m.get(kk) for kk in ("economy", "dimension", "frequency", "unit", "display_name", "criticality", "release_rule", "publication_rule", "history_source", "collector", "source", "vintage_semantics", "release_lag_days", "stale_window_days") if kk in m}
                out.append("%s: %s | all_keys=%s" % (mid, json.dumps(sub, ensure_ascii=False, sort_keys=True), sorted(m.keys())))
            else:
                out.append(repr(m))
    for k in reg.keys():
        if k != "metrics":
            v = reg[k]
            s = json.dumps(v, ensure_ascii=False)
            out.append("registry[%s] = %s" % (k, s[:1500] + ("..." if len(s) > 1500 else "")))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print("wrote", out_path, "lines", len(out))


if __name__ == "__main__":
    main()
