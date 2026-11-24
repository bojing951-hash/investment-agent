# -*- coding: utf-8 -*-
"""rc14b: 受审稿数字按位置清点(Audit-R32 A round1; 只读)。
用法: /usr/bin/python3 -I rc14b_sweep_loc.py <run_dir> <ledger points.jsonl>
rc14 的加严版: 把台账记录按 where/src 的位置关键词归入受审稿的各位置段,
      逐段列出"该段台账子集内无同值数值"的数字及上下文, 供席位人工判读
      (跨段复用的数字需人工确认其出处记录)。本脚本不写台账(只打印)。
"""
import sys, os, re, json, collections

RUN = sys.argv[1]
PTS = sys.argv[2]
aj = json.load(open(os.path.join(RUN, 'agent_judgment.json'), encoding='utf-8'))
NUM = re.compile(r'(?<![A-Za-z_0-9.])\d+(?:\.\d+)?')
LEDN = re.compile(r'\d+(?:\.\d+)?')

recs = [json.loads(l) for l in open(PTS, encoding='utf-8') if l.strip()]
for r in recs:
    r['_nums'] = set()
    for m in LEDN.findall(json.dumps([r.get('computed'), r.get('reported')], ensure_ascii=False)):
        try:
            r['_nums'].add(float(m))
        except ValueError:
            pass
    r['_blob'] = (str(r.get('where')) + ' ' + str(r.get('src')) + ' ' + str(r.get('note'))).lower()

# 位置段 -> (台账记录筛选关键词: 任一命中即归入; 另加全局段)
LOC = collections.OrderedDict([
    ('l3.contradictions[0] C1', ['c1', '证据面最新水平', '水平为']),
    ('l3.contradictions[1] C2', ['c2']),
    ('l3.contradictions[2] C3', ['c3']),
    ('l3.mechanism_chains[0] M1', ['m1', '传导链1', 'rates_decomposition', 'asset_returns_echo', 'tr1']),
    ('l3.mechanism_chains[1] M2', ['m2', '传导链2', 'tr2']),
    ('l4.scenarios', ['scn', '情景', 'falsification', 'trigger']),
    ('reader_map.headline_conclusion', ['headline', '主线', 'c1', 'm1', 'tr1', 'us from_to', 'cn from_to', 'ea from_to', 'jp from_to', 'm2']),
    ('reader_map.regions[0] US', ['us from_to', 'us走位', 'us 走位', '美国走位', 'regions[us]', 'regions[0]', 'point_values.cells[u']),
    ('reader_map.regions[1] CN', ['cn from_to', '中国走位', 'regions[cn]', 'regions[1]', 'point_values.cells[c', 'c3']),
    ('reader_map.regions[2] EA', ['ea from_to', '欧元区走位', 'regions[ea]', 'regions[2]', 'point_values.cells[e']),
    ('reader_map.regions[3] JP', ['jp from_to', '日本走位', 'regions[jp]', 'regions[3]', 'point_values.cells[j']),
    ('reader_map.transmission[0] TR1', ['tr1', 'm1', '传导链1', 'rates_decomposition', 'asset_returns_echo']),
    ('reader_map.transmission[1] TR2', ['tr2', 'm2', '传导链2']),
    ('reader_map.turnings', ['turning', '转折', '候选面', 'tr1.step1', 'm1.step1', 'c1']),
    ('reader_map.history_periods', ['history_periods', '历史段', '事后', '当时可知', '同步面', 'analog', 'c2', 'scn1', 'scn2', '逐窗并列']),
    ('reader_map.rates_decomposition', ['rates_decomposition', 'tr1.step3', 'm1.step3']),
    ('reader_map.asset_returns_echo', ['asset_returns_echo', 'tr1.step3', 'tr1.step2', 'tr2', 'm1.step4', '资产窗']),
    ('reader_map.turning_supplement', ['turning_supplement', 'supplement', 'jp from_to', 'turnings[2]', '东京']),
    ('quality_gate_notes', ['quality_gate_notes', 'quality_gate', '⑫', '时点', '同日收盘', 'tr1.step3', 'scn', '情景', 'c1', 'gate', '数据门', '引用', 'evidence', '候选面', 'm1.step1', 'm2.step1', '日本走位', '传导链2', '政策一年窗', 'ea from_to', 'cn from_to', 'dfedtaru', 'dff', 'ecb_', 'l1 事实层', '事实层', 'turnings[1]', '全文', '文本一致', '逐字']),
])


def loc_of(path):
    p = path.lower()
    if p.startswith('.l3.contradictions'):
        return 'l3.contradictions[%d] C%d' % (int(re.search(r'\[(\d+)\]', path).group(1)), int(re.search(r'\[(\d+)\]', path).group(1)) + 1)
    if p.startswith('.l3.mechanism_chains'):
        i = int(re.search(r'\[(\d+)\]', path).group(1))
        return 'l3.mechanism_chains[%d] M%d' % (i, i + 1)
    if p.startswith('.l4'):
        return 'l4.scenarios'
    if p.startswith('.reader_map.headline'):
        return 'reader_map.headline_conclusion'
    if p.startswith('.reader_map.regions'):
        i = int(re.search(r'\[(\d+)\]', path).group(1))
        return 'reader_map.regions[%d] %s' % (i, ['US', 'CN', 'EA', 'JP'][i])
    if p.startswith('.reader_map.transmission'):
        i = int(re.search(r'\[(\d+)\]', path).group(1))
        return 'reader_map.transmission[%d] TR%d' % (i, i + 1)
    if p.startswith('.reader_map.turnings'):
        return 'reader_map.turnings'
    if p.startswith('.reader_map.history_periods'):
        return 'reader_map.history_periods'
    if p.startswith('.reader_map.rates_decomposition'):
        return 'reader_map.rates_decomposition'
    if p.startswith('.reader_map.asset_returns_echo'):
        return 'reader_map.asset_returns_echo'
    if p.startswith('.reader_map.turning_supplement'):
        return 'reader_map.turning_supplement'
    if p.startswith('.quality_gate_notes'):
        return 'quality_gate_notes'
    return None


def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, path + '.' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + '[%d]' % i)
    elif isinstance(o, str):
        yield path, o


subset = {}
for loc, kws in LOC.items():
    subset[loc] = [r for r in recs if any(k in r['_blob'] for k in kws)]

grand = collections.OrderedDict()
for path, s in walk(aj):
    loc = loc_of(path)
    if loc is None:
        continue
    if path.endswith('evidence_refs]') or '.evidence_refs' in path:
        continue
    rs = subset[loc]
    nums = set()
    for r in rs:
        nums |= r['_nums']
    for m in NUM.finditer(s):
        t = m.group(0)
        v = float(t)
        if v not in nums:
            grand.setdefault((loc, t), []).append((path[-70:], s[max(0, m.start() - 30):m.end() + 26].replace('\n', ' ')))

print('位置段子集规模:')
for loc, rs in subset.items():
    print('   %-36s 记录 %3d' % (loc, len(rs)))
print('未命中(位置段口径)种类', len(grand))
cur = None
for (loc, t), lst in grand.items():
    if loc != cur:
        print('########## ' + loc)
        cur = loc
    seen = []
    for path, ctx in lst:
        if ctx in [c for _, c in seen]:
            continue
        seen.append((path, ctx))
        if len(seen) > 3:
            break
    print('  == %s x%d' % (t, len(lst)))
    for path, ctx in seen:
        print('       %s | …%s…' % (path[-46:], ctx))
