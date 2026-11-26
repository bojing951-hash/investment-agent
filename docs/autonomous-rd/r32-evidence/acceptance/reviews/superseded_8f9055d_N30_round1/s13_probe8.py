import datetime as dt, json, re, sys
R = json.load(open(sys.argv[1], encoding="utf-8"))
RP = R["research_plan"]
for c in RP["point_values"]["cells"]:
    if c["metric_id"] in ("EA_HICP_YOY", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY"):
        for a, v in c["anchors"].items():
            print(c["metric_id"], a, {k: v.get(k) for k in ("status", "observation_date", "publication_date", "publication_rule", "value")})
RPTXT = json.dumps(RP, ensure_ascii=False)
for d in ("2026-06-16", "2026-06-20", "2026-05-16", "2026-05-20"):
    i = RPTXT.find(d)
    print(d, "in research_plan:", i >= 0, RPTXT[max(0, i - 90): i + 40] if i >= 0 else "")
print("rule check", (dt.date(2026, 10, 31) + dt.timedelta(days=16)).isoformat(), (dt.date(2026, 10, 31) + dt.timedelta(days=20)).isoformat(),
      (dt.date(2026, 5, 31) + dt.timedelta(days=16)).isoformat(), (dt.date(2026, 5, 31) + dt.timedelta(days=20)).isoformat())
