# s12_md_tokens.py <snap> <rep> <cal> <reg> <aj> <out> <md...>  -- reader-report numeric token provenance (diag only)
import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:7])
texts = [chr(10).join(s for _, s in c.leaves), json.dumps(c.rep, ensure_ascii=False), json.dumps(c.snap, ensure_ascii=False), json.dumps(c.cal, ensure_ascii=False), json.dumps(c.reg, ensure_ascii=False)]
NUM = re.compile('[0-9]+[.][0-9]+|[0-9]+')
for p in sys.argv[7:]:
    s = open(p, encoding='utf-8').read()
    toks = sorted(set(NUM.findall(s)), key=lambda x: (len(x), x))
    miss = [t for t in toks if not any(t in x for x in texts)]
    print(p.rsplit('/', 1)[1], '| chars', len(s), '| lines', s.count(chr(10)), '| tokens', len(toks), '| not-found', len(miss))
    print('   ', miss)
    for key in ['方向同、水平分化、证据面不对称', '尚不能区分', '证据不足六项', '席位待唤起', '独立语义审查待裁', 'UPHELD', 'REVISE', '缺席格', '数据不可得', '不得进入研究结论', 'DEGRADED', 'clamped', '非请求月末']:
        print('   ', key, s.count(key))
