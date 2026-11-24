#!/usr/bin/env python3
"""Independent semantic-audit seat — read-only recompute (Round 1, work order A).

Every point is computed from the frozen snapshot series_store / frozen release calendar / report.json
engine faces (and the registry) and compared with the value printed in the report text (MAP_REPORT.md).
No engine code is imported; nothing is written outside the seat directory.

usage (cwd = seat dir):
  python3 -I recompute.py <snapshot.json> <release_calendar.json> <report.json> <metric_registry.json> <MAP_REPORT.md> <out_table.json>
"""
import importlib
import json
import os
import sys

sys.path.insert(0, "/tmp/r32-accept/review/A_round1")
import rc_common as C  # noqa: E402

ctx = C.Ctx(sys.argv)
for mod in ("rc_a", "rc_b", "rc_c", "rc_d"):
    if os.path.exists("/tmp/r32-accept/review/A_round1/%s.py" % mod):
        m = importlib.import_module(mod)
        for name in sorted(dir(m)):
            if name.startswith("run_"):
                getattr(m, name)(ctx)

pts = ctx.pts
ids = [p["id"] for p in pts]
dup = sorted({i for i in ids if ids.count(i) > 1})
mm = [p for p in pts if not p["match"]]
cats = {}
for p in pts:
    c = cats.setdefault(p["category"], {"n": 0, "mm": 0})
    c["n"] += 1
    c["mm"] += 0 if p["match"] else 1
out = {"cutoff": C.CUTOFF, "n_points": len(pts), "n_match": len(pts) - len(mm), "n_mismatch": len(mm),
       "by_category": cats, "duplicate_ids": dup, "points": pts, "mismatches": mm, "notes": ctx.notes}
with open(ctx.out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
md_path = os.path.splitext(ctx.out_path)[0] + ".md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# 复算清单(Round-1 独立语义审计席·工单A)\n\n")
    f.write("- 截止日: %s; 复算点 %d, 命中 %d, 偏离 %d; 重复ID=%s\n\n" % (C.CUTOFF, len(pts), len(pts) - len(mm), len(mm), dup))
    f.write("| # | 点 | 类 | 出处(文件+键) | 席位直算值 | 报告值 | 一致 | 注 |\n|---|---|---|---|---|---|---|---|\n")
    for i, p in enumerate(pts, 1):
        cells = [str(i), p["id"], p["category"], p["source"], p["computed"], p["reported"], "是" if p["match"] else "**否**", p.get("note", "")]
        f.write("| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in cells) + " |\n")
    f.write("\n## 偏离项\n\n")
    for p in mm:
        f.write("- %s [%s] 直算=%s / 报告=%s — %s\n" % (p["id"], p["category"], p["computed"], p["reported"], p.get("note", "")))
    f.write("\n## 说明\n\n")
    for n in ctx.notes:
        f.write("- [%s] %s\n" % (n["category"], n["note"]))
print("points=%d match=%d mismatch=%d dup=%s" % (len(pts), len(pts) - len(mm), len(mm), dup))
print(json.dumps(cats, ensure_ascii=False))
for p in mm:
    print("MISMATCH %s [%s] computed=%s reported=%s %s" % (p["id"], p["category"], p["computed"], p["reported"], p.get("note", "")))
print("written", ctx.out_path, md_path)
