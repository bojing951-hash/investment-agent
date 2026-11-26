#!/usr/bin/python3 -I
# -*- coding: utf-8 -*-
"""patch8: add calendar version points and verify the judgment's engine-gap
disclosures (quality_gate_notes[5] ①②) against the engine source, read-only.
usage: /usr/bin/python3 -I s05_patch8.py <s05_recompute.py>"""
import sys
p = sys.argv[1]
src = open(p, encoding="utf-8").read()


def rep1(old, new):
    global src
    assert src.count(old) == 1, (src.count(old), old[:60])
    src = src.replace(old, new)


rep1('map_path = sys.argv[8] if len(sys.argv) > 8 else None\n',
     'map_path = sys.argv[8] if len(sys.argv) > 8 else None\n'
     'jc_path = sys.argv[9] if len(sys.argv) > 9 else None   # optional: engine judgment_contract.py (read-only)\n'
     'tc_path = sys.argv[10] if len(sys.argv) > 10 else None  # optional: engine text_consistency.py (read-only)\n')
rep1('rp = rep["research_plan"]\n',
     'rp = rep["research_plan"]\n'
     'JCSRC = open(jc_path, encoding="utf-8").read() if jc_path else ""\n'
     'TCSRC = open(tc_path, encoding="utf-8").read() if tc_path else ""\n')
rep1('      <metric_registry.json> <agent_judgment.json> <evidence_index.json> <outdir> [MAP_REPORT.md]\n',
     '      <metric_registry.json> <agent_judgment.json> <evidence_index.json> <outdir> [MAP_REPORT.md]\n'
     '      [judgment_contract.py] [text_consistency.py]   (last two optional, engine source read-only)\n')
old = '    add(s, "冻结日历对 ECB 无实录条目", [], sorted(set(str(e.get("metric_id")) for e in CALE if "ECB" in str(e.get("metric_id")).upper() or "ECB" in str(e.get("entry_id")).upper())), "release_calendar.entries")\n'
new = (
    '    add(s, "判断档「发布日历(v1.5.0,2026-11-21 更新)」与冻结日历 version/updated 一致", ["1.5.0", "2026-11-21"], [str(cal.get("version")), str(cal.get("updated"))[:10]], "release_calendar.version/updated vs agent_declaration.basis / quality_gate_notes[4]")\n'
    '    add(s, "判断档「发布日历实录(2026-11-21 更新)」在文且日期=日历 updated", True, has("2026-11-21 更新") and str(cal.get("updated"))[:10] == "2026-11-21", "release_calendar.updated vs l3.contradictions[1].statement / reader_map.regions[1]")\n'
    '    if JCSRC:\n'
    '        add(s, "引擎缺口披露①属实: _map_checks 锚标签硬编码「12个月前/3个月前/最新一期」,本问点值格锚=6个月前/最新一期(「观测 X→Y」串必误报)", [True, sorted(["6个月前", "最新一期"])],\n'
    '            ["for _lbl in (\'12个月前\', \'3个月前\', \'最新一期\'):" in JCSRC, sorted(cell("EA_HICP_YOY")["anchors"].keys())], "judgment_contract._map_checks(只读源码) vs research_plan.point_values.cells[].anchors")\n'
    '        add(s, "引擎缺口披露①后半属实: 判断档地区走位正文无「观测 X→Y」串(改用「观测月 X」)", 0, len(re.findall(r"观测\\s*\\d{4}-\\d{2}(?:-\\d{2})?\\s*→", "\\n".join(str(r_.get("from_to") or "") for r_ in RM.get("regions") or []))), "reader_map.regions[].from_to")\n'
    '    if TCSRC:\n'
    '        add(s, "引擎缺口披露②属实: text_consistency.ALIASES 未覆盖 JP_CPI_YOY/EA_HICP_YOY/JP_CPI_TOKYO_YOY/JP_POLICY_TARGET/ECB_MRO", [False] * 5,\n'
    '            [(("\'%s\':" % m_) in TCSRC) for m_ in ("JP_CPI_YOY", "EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_TARGET", "ECB_MRO")], "text_consistency.ALIASES(只读源码)")\n'
    '        add(s, "引擎缺口披露②对偶: 判断档所称「带别名指标」USDJPY/SPX/VIX/JP_POLICY_RATE/ECB_DFR 均在 ALIASES", [True] * 5,\n'
    '            [(("\'%s\':" % m_) in TCSRC) for m_ in ("USDJPY", "SPX", "VIX", "JP_POLICY_RATE", "ECB_DFR")], "text_consistency.ALIASES(只读源码)")\n'
) + old
rep1(old, new)
open(p, "w", encoding="utf-8").write(src)
print("patch8 applied")
