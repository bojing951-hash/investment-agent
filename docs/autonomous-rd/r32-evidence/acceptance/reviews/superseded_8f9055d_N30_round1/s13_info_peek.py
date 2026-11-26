#!/usr/bin/python3 -I
# 席位自写：查看本席中间表 INFO 指定键(只读)
import json, sys
T = json.load(open(sys.argv[1], encoding="utf-8"))
I = {r["key"]: r["value"] for r in T["info"]}
def tr(v, n=700):
    s = json.dumps(v, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + "…[+%d]" % (len(s) - n)
print("INFO_KEYS", len(I))
for k in ["contract_verification"]:
    cv = I[k]
    print("CV_VERSION", cv.get("version"), "VERDICT", cv.get("verdict"), "STATS", json.dumps(cv.get("stats"), ensure_ascii=False))
    print("CV_KEYS", list(cv.keys()))
    for i, v in enumerate(cv.get("verdicts", [])):
        print("  CVV", i, tr(v, 420))
    for i, v in enumerate(cv.get("six_checks", [])):
        print("  CV6", i, tr(v, 260))
    for i, v in enumerate(cv.get("map_checks", [])):
        print("  CVM", i, tr(v, 300))
    print("  CV_UNRES", tr(cv.get("unresolved_unbound"), 300))
for k in ["cv_non_verified", "cv_status_counts", "face_off_verdicts", "turning_candidate_hit 0", "turning_candidate_hit 1", "turning_candidate_hit 2",
          "Gate_A", "gate_a_lists", "S1_rows", "S2_rows", "clusters_detail", "policy_doc_facts", "VIX_month_window_top_daily_jumps",
          "data_requirements ECB_MRO", "data_requirements ECB_DFR", "data_requirements_outcome", "dimension_gaps", "registry_freshness ECB_MRO",
          "registry_freshness ECB_DFR", "where_is_2026-06-26", "snapshot_fact_refs_l3", "date_tokens_in_judgment_body", "next_month_pub EA_HICP_YOY",
          "next_month_pub JP_CPI_YOY", "next_month_pub JP_CPI_TOKYO_YOY", "next_month_pub JP_POLICY_RATE", "tokyo_rule_pubs", "calendar_version",
          "MAP_REPORT_ECB_all_Wednesday_claim", "agent_judgment_attach", "EURJPY_synth_full", "ECB_obs_dates_not_Wednesday", "turning_candidates"]:
    if k in I:
        print("INFO", k, "=", tr(I[k], 900))
    else:
        print("INFO", k, "= <MISSING>")
for k in ["calendar_all_entries", "calendar_non_JP_EA_entries"]:
    v = I.get(k)
    print("INFO", k, "n=", (len(v) if isinstance(v, list) else type(v).__name__))
    if isinstance(v, list):
        for e in v:
            print("   CE", tr(e, 330))
