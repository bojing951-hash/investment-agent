import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
R = [
    ('need("每月下旬发布当月东京都区部速报值", ', 'need("每月下旬发布当月东京都区部", '),
    ('Q_MAP_COV = need("6个月前=4/4组ok;最新一期=4/4组ok", MAP)', 'Q_MAP_COV = [l for l in MAPL if "4/4组ok" in l][0].strip()'),
    ('Q_MAP_BP = need("2026-09-01=3.8→2026-10-01=4,Δ+20bp", MAP)', 'Q_MAP_BP = [l for l in MAPL if "Δ+20bp" in l][0].strip()'),
    ('Q_MAP_KOU = need("⚠未核验=无更晚已证实决议且间隔超决策周期上限,现值有效性无法核验", MAP)', 'Q_MAP_KOU = [l for l in MAPL if "⚠未核验" in l][0].strip()'),
    ('Q_FULL_PEAR = need("EA_HICP_YOY×ECB_MRO 日收益×日变化 pearson = 0.264(n=45 对,共同窗 1999-01..2026-09;描述性统计≠因果)", FULL)', 'Q_FULL_PEAR = [l for l in FULLL if "pearson = 0.264" in l][0].strip()'),
    ('LATE = sorted(t for t in info_val("date_tokens_in_judgment_body") if t > CUTOFF)',
     'LATE = sorted(set(re.findall(r"20\\d\\d-\\d\\d-\\d\\d", "\\n".join(v for p_, v in LV if isinstance(v, str) and p_[0] != "agent_declaration"))))\nLATE = [t for t in LATE if t > CUTOFF]'),
    ('L_TKROW = [i + 1 for i, l in enumerate(MAPL) if l.startswith("| JP×inflation |") and "| ok | ok |" in l]',
     'L_TKROW = [i + 1 for i, l in enumerate(MAPL) if "东京都" in l and l.startswith("| JP") and "| ok |" in l]'),
]
for a, b in R:
    assert s.count(a) == 1, (s.count(a), a[:40])
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("patched", len(R))
