import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
a = 'sg(chg(NK, W0, CUTOFF))'
assert s.count(a) == 1, s.count(a)
s = s.replace(a, 'sg([a for a in J["reader_map"]["asset_returns_echo"] if a["metric_id"] == "NIKKEI225"][0]["chg_pct"])')
open(p, "w", encoding="utf-8").write(s)
print("patched")
