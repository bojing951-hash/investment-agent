# -*- coding: utf-8 -*-
"""只读: 步骤信封摘要。用法: python3 -I s08_envelopes.py <report_json> <out_dir>"""
import json, sys, os
p = sys.argv[1]; out = sys.argv[2]
os.makedirs(out, exist_ok=True)
with open(p, 'r', encoding='utf-8') as f:
    d = json.load(f)
def brief(o, depth=0, maxd=2):
    if isinstance(o, dict):
        if depth >= maxd:
            return "{dict %d keys: %s}" % (len(o), ','.join(list(o.keys())[:14]))
        return {k: brief(v, depth+1, maxd) for k, v in o.items()}
    if isinstance(o, list):
        if depth >= maxd:
            return "[list len %d]" % len(o)
        return [brief(v, depth+1, maxd) for v in o[:6]]
    s = repr(o)
    return s if len(s) < 160 else s[:160] + '…'
for s in d['steps']:
    st = s.get('step')
    if 'envelope' in s:
        env = s['envelope']
        with open(os.path.join(out, 'env_%s.json' % st), 'w', encoding='utf-8') as f:
            json.dump(env, f, ensure_ascii=False, indent=1)
        print("=== %s ok=%s exit=%s semantic_ok=%s note=%s bytes=%d" % (st, s.get('ok'), s.get('exit_code'), s.get('semantic_ok'), repr(s.get('note'))[:200], len(json.dumps(env, ensure_ascii=False))))
        print("   argv:", s.get('argv'))
        print("   env keys:", list(env.keys()) if isinstance(env, dict) else type(env).__name__)
    else:
        print("=== %s (no envelope) %s" % (st, json.dumps({k: v for k, v in s.items() if k != 'step'}, ensure_ascii=False)[:500]))
