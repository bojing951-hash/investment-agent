#!/usr/bin/env python3
"""tc_probe.py <tree> <run_dir> <judgment.json> [item_id] — clause-level check_text detail."""
import json, sys, os
tree, rd, jp = sys.argv[1:4]
want = sys.argv[4] if len(sys.argv) > 4 else None
sys.path.insert(0, os.path.join(tree, 'scripts'))
import research_contract.judgment_contract as jc
import research_contract.text_consistency as tc
rep = json.load(open(os.path.join(rd, 'report.json'), encoding='utf-8'))
face = jc.build_face(rep)
J = json.load(open(jp, encoding='utf-8'))
for con in J['l3']['contradictions']:
    if want and con['id'] != want:
        continue
    text = con['statement']
    b_checks, consumed = jc._class_b(text, face)
    print('==', con['id'], 'class_b consumed', consumed, 'n_b', len(b_checks))
    for i, cl in enumerate(tc._clause_split(tc._checkface_preprocess(text))):
        mids = tc._find_alias(cl)
        masked = tc._masked_clause(cl, mids)
        toks = tc._extract_tokens(masked)
        print(' [%d] aliases=%s tokens=%s' % (i, [m[0] for m in mids], [(t['raw'], t['kind']) for t in toks]))
        print('     ', cl[:230])
