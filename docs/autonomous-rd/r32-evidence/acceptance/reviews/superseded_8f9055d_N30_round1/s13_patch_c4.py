import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
def rep(s, a, b, cnt=1):
    assert s.count(a) == cnt, (s.count(a), a[:80])
    return s.replace(a, b)
s = rep(s, '"/".join(n(v) for v, _ in JGBV)', '"/".join(str(v) for v, _ in JGBV)')
s = rep(s, '% (EA_PUB_WK, EA_RULE, n(mo(EA, 2026, 4))),', '% (EA_PUB_WK, EA_RULE, p1(mo(EA, 2026, 4))),')
old = '''     "2026-05 期的观测日(2026-05-01)早于窗起 2026-05-23,其推定发布日 %s 在窗内;机制链环1 对此有说明,读者地图欧元区行直接称窗内月度路径。日本行同构(2026-05 期发布 %s)。" % (
         CELLS["EA_HICP_YOY"]["anchors"]["6个月前"]["publication_date"].replace("2026-05-16", "2026-05-16"), CELLS["JP_CPI_YOY"]["anchors"]["6个月前"]["publication_date"]),
'''
new = '''     "2026-05 期的观测日(2026-05-01)早于窗起 2026-05-23,按引擎推定规则(月末+%d 天)其发布日为 %s,在窗内;机制链环1 对此有说明,读者地图欧元区行直接称窗内月度路径。日本行同构(2026-05 期推定发布日 %s)。" % (
         16, EA_MAY_PUB, JP_MAY_PUB),
'''
s = rep(s, old, new)
anchor = 'item("NIT", "reader_map.regions[0].from_to(欧元区行,「窗内月度路径 3.2(2026-05)」)",'
defs = '''def _me(y, m_):
    return dt.date(y + (1 if m_ == 12 else 0), (m_ % 12) + 1, 1) - dt.timedelta(days=1)


EA_MAY_PUB, JP_MAY_PUB = (_me(2026, 5) + dt.timedelta(days=k)).isoformat() for k in (16, 20)
assert CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["publication_date"] == (_me(2026, 10) + dt.timedelta(days=16)).isoformat() == "2026-11-16"
assert CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["publication_date"] == (_me(2026, 10) + dt.timedelta(days=20)).isoformat() == "2026-11-20"
assert CELLS["EA_HICP_YOY"]["anchors"]["6个月前"]["publication_date"] == (_me(2026, 4) + dt.timedelta(days=16)).isoformat() == "2026-05-16"
assert CELLS["JP_CPI_YOY"]["anchors"]["6个月前"]["publication_date"] == (_me(2026, 4) + dt.timedelta(days=20)).isoformat() == "2026-05-20"
assert "月末+16天" in CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["publication_rule"] and "月末+20天" in CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["publication_rule"]
assert EA_MAY_PUB == "2026-06-16" and JP_MAY_PUB == "2026-06-20" and "2026-05 期观测日在窗起 2026-05-23 之前、推定发布日在窗内" in JALL
'''
s = rep(s, anchor, defs + anchor)
open(p, "w", encoding="utf-8").write(s)
print("part C patched")
