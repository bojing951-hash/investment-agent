# -*- coding: utf-8 -*-
"""Read-only: where do the judgment strings appear verbatim among the three rendered reports;
for strings not verbatim, show the longest prefix present and how the document continues."""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
s = importlib.util.spec_from_file_location("t3lib", os.path.join(HERE, "t3lib.py"))
lib = importlib.util.module_from_spec(s)
s.loader.exec_module(lib)
c = lib.build(sys.argv[1], sys.argv[2], sys.argv[3])
J, RM, docs = c.J, c.J["reader_map"], c.docs
groups = {"C": [x["statement"] for x in J["l3"]["contradictions"]],
          "CE": [y for x in J["l3"]["contradictions"] for y in x["competing_explanations"]],
          "M1": [x["text"] for x in J["l3"]["mechanism_chains"][0]["links"]],
          "HC/REG": [RM["headline_conclusion"]] + [r["from_to"] for r in RM["regions"]],
          "TL": [lk[k] for lk in RM["transmission"][0]["links"] for k in ("observed_fact", "causal_hypothesis", "competing_explanation", "main_predicts", "competing_predicts", "verdict_note")],
          "W": [w[k] for w in RM["turnings"] for k in ("first_mover", "follow_or_diverge", "narrative")],
          "HIST": [RM["history_zero_case_note"]],
          "SC": [y["rows"][k][f] for y in J["l4"]["scenarios"] for k, f in (("falsification", "threshold"), ("trigger", "condition"))] + [y["rows"]["scenario"] for y in J["l4"]["scenarios"]] + [y["rows"]["asset_direction"]["direction"] for y in J["l4"]["scenarios"]],
          "QGN": list(J["quality_gate_notes"])}
for g, ss in groups.items():
    for i, t in enumerate(ss):
        hit = [n[:-3] for n in ("MAP_REPORT.md", "FULL_REPORT.md", "report.md") if t in docs[n]]
        if len(hit) < 3:
            best = 0
            for n in ("MAP_REPORT.md", "FULL_REPORT.md", "report.md"):
                d = docs[n]
                lo, hi = 0, len(t)
                while lo < hi:
                    mid = (lo + hi + 1) // 2
                    if t[:mid] in d:
                        lo = mid
                    else:
                        hi = mid - 1
                best = max(best, lo)
            k = best
            d = docs["MAP_REPORT.md"]
            j = d.find(t[:k]) if k else -1
            print("%s[%d] len=%d found=%s prefix=%d | doc-continues: %s | text-continues: %s" % (
                g, i, len(t), hit, k, d[j + k:j + k + 70].replace("\n", "\\n") if j >= 0 else None, t[k:k + 70]))
