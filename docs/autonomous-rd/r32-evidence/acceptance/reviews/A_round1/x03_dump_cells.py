import json, sys
p, outp = sys.argv[1], sys.argv[2]
d = json.load(open(p, encoding='utf-8'))
rp = d['research_plan']
lines = []
for c in rp['point_values']['cells']:
    lines.append(f"### {c['region']} / {c['dimension']} / {c['metric_id']}  ({c.get('display_name')}) unit={c.get('unit')} status={c.get('status')} vintage={c.get('vintage_semantics')}")
    for k, v in c.items():
        if k in ('anchors',): continue
        if k in ('region','dimension','metric_id','display_name','unit','vintage_semantics'): continue
        lines.append(f"   .{k} = {json.dumps(v, ensure_ascii=False)}")
    for an, av in c['anchors'].items():
        lines.append(f"   [{an}] " + json.dumps(av, ensure_ascii=False))
    lines.append('')
open(outp, 'w', encoding='utf-8').write('\n'.join(lines))
print(len(lines))
