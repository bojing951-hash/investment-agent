#!/usr/bin/python3 -I
"""TR2 discriminator recompute (USDJPY vs SPX co-movement) + echo counts. usage: s31_tr2.py <snapshot.json> <agent_judgment.json>"""
import sys, math
sys.path.insert(0, "/tmp/r32-accept/review5/A_round1")
import json
import lib
snap = lib.load_json(sys.argv[1])
jud = lib.load_json(sys.argv[2])
st = lib.Store(snap)
a = st.on_or_before("USDJPY", "2026-10-23"); b = st.on_or_before("USDJPY", "2026-11-23")
print("USDJPY 2026-10-23 -> 2026-11-23:", a, b, "chg%=", lib.r(lib.pct_change(a[1], b[1]), 2))
sp = dict(st.in_range("SPX", "2026-10-23", "2026-11-23")); uj = dict(st.in_range("USDJPY", "2026-10-23", "2026-11-23"))
common = sorted(set(sp) & set(uj))
print("common days n=", len(common), "first/last", common[0], common[-1])
ds = [(math.log(sp[common[i]] / sp[common[i - 1]]), math.log(uj[common[i]] / uj[common[i - 1]])) for i in range(1, len(common))]
n = len(ds); mx = sum(x for x, _ in ds) / n; my = sum(y for _, y in ds) / n
cov = sum((x - mx) * (y - my) for x, y in ds) / (n - 1)
corr = cov / math.sqrt(sum((x - mx) ** 2 for x, _ in ds) / (n - 1) * sum((y - my) ** 2 for _, y in ds) / (n - 1))
print("log-return corr=", lib.r(corr, 3), "same-direction days=", sum(1 for x, y in ds if x * y > 0), "/", n)
down = [(common[i], ds[i - 1]) for i in range(1, len(common)) if ds[i - 1][0] < 0]
print("SPX down days:", len(down), "USDJPY down on those:", sum(1 for _, (x, y) in down if y < 0))
big = sorted(down, key=lambda t: t[1][0])[:4]
print("four largest SPX drops (date, spx%, usdjpy%):", [(d, lib.r(x * 100, 2), lib.r(y * 100, 2)) for d, (x, y) in big])
cum_sp = math.exp(sum(x for x, _ in ds)) - 1; cum_uj = math.exp(sum(y for _, y in ds)) - 1
print("cumulative common-day change SPX %s%%, USDJPY %s%%" % (lib.r(cum_sp * 100, 2), lib.r(cum_uj * 100, 2)))
lk = jud["reader_map"]["transmission"][1]["links"][0]
print("TR2 link1 observed/verdict fields:", {k: (v if len(str(v)) < 200 else str(v)[:200]) for k, v in lk.items() if k not in ("causal_hypothesis", "observed_fact")})
print("TR2 link1 observed_fact tail:", lk["observed_fact"][-520:])
# echo counts
n_echo = 0; bad = 0
for r in jud["reader_map"]["regions"]:
    for e in r.get("anchor_echo") or []:
        n_echo += 1
        v = st.at(e["metric_id"], e["observation_month"] + "-01") if st.at(e["metric_id"], e["observation_month"] + "-01") is not None else st.on_or_before(e["metric_id"], e["observation_month"] + "-31")
print("anchor_echo rows:", n_echo, "; asset_returns_echo rows:", len(jud["reader_map"]["asset_returns_echo"]), "; rates_decomposition keys:", sorted(jud["reader_map"]["rates_decomposition"].keys()))
for e in jud["reader_map"]["asset_returns_echo"]:
    mid = e["metric_id"]; w = e["window"]
    a = st.on_or_before(mid, w["from"]); b = st.on_or_before(mid, w["to"])
    print("  asset_returns_echo", mid, w["window_months"] if "window_months" in w else e.get("window_months"), w["from"], w["to"], "mine chg%=", lib.r(lib.pct_change(a[1], b[1]), 2), "echo chg%=", e["chg_pct"], "ends", (a[0], b[0]))
