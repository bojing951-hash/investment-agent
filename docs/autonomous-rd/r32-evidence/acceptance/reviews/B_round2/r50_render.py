# -*- coding: utf-8 -*-
# r50_render.py — K 渲染一致性 / L 引擎渲染表自洽 / X 补充核验
# 用法: /usr/bin/python3 -I r50_render.py <RUN_DIR> <SNAPSHOT_JSON> <OUT_JSON> <REVIEW_TXT>
import sys, os, json, re, math, hashlib, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r00_common import *

RUN, SNAP, OUT, REV = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
sn = Snap(load(SNAP))
rep = load(os.path.join(RUN, 'report.json'))
aj = load(os.path.join(RUN, 'agent_judgment.json'))
PTS, EX, CAT = [], {}, ['']
rev = open(REV, 'w', encoding='utf-8')
cut = dt.date(2026, 11, 23)


def cat(c):
    CAT[0] = c


def P(pid, where, key, comp, rep_, note='', tol=None):
    disp = round(comp, 6) if isinstance(comp, float) else comp
    ok = same(comp, rep_, tol)
    PTS.append({'id': pid, 'cat': CAT[0], 'where': where, 'key': key, 'computed': disp,
                'reported': rep_, 'ok': bool(ok), 'note': note})
    print('%s|%s|%s|comp=%s|rep=%s|%s|%s' % ('OK' if ok else 'XX', pid, CAT[0], disp, rep_, where, note))
    return ok


def norm(s):
    s = s.replace('−', '-').replace('–', '-').replace('—', '-').replace('\\', '').replace('*', '').replace('“', '"').replace('”', '"').replace('`', '')
    return re.sub(r'\s+', '', s)


def walk(o, path, out):
    if isinstance(o, str):
        out.append((path, o))
    elif isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + '.' + k, out)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, '%s[%d]' % (path, i), out)


def pearson(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


STRS = []
walk(aj, '$', STRS)
FILES = ('report.md', 'MAP_REPORT.md', 'FULL_REPORT.md')
RAW = {fn: open(os.path.join(RUN, fn), encoding='utf-8').read() for fn in FILES}
MD = {k: norm(v) for k, v in RAW.items()}
UNION = ''.join(MD[k] for k in FILES)
JTEXT = '\x00'.join(norm(s) for _, s in STRS) + '\x00'

DATE = re.compile(r'\d{4}-\d{2}(?:-\d{2})?')
NUM = re.compile(r'[+\-−]?\d+(?:\.\d+)?(?:%|bp|pp|天|个百分点)?')


def toks(s):
    t = [norm(m.group(0)) for m in DATE.finditer(s)]
    rest = DATE.sub(' ', s)
    for m in NUM.finditer(rest):
        g = norm(m.group(0))
        core = g.lstrip('+-')
        if len(core.split('.')[0]) >= 2 or '.' in core or g.endswith(('%', 'bp')):
            t.append(g)
    return t


def nonrendered(p):
    return (p.startswith('$.agent_declaration') or p.startswith('$.quality_gate_notes')
            or p.endswith('.narrative') or p.endswith('.verdict_note'))


# ---------------- K 渲染一致性 ----------------
cat('K 渲染一致性')
sha = hashlib.sha256(open(os.path.join(RUN, 'MAP_REPORT.md'), 'rb').read()).hexdigest()
rec = open(os.path.join(RUN, 'MAP_REPORT.sha256'), encoding='utf-8').read().split()[0]
P('K01', '受审版本同一性: MAP_REPORT.sha256 记录值 = 现文件 sha256', 'sha256(MAP_REPORT.md)', sha, rec)
EX['semantic_review'] = {k: rep.get('semantic_review', {}).get(k) for k in ('verdict', 'verdicts_n', 'map_report_sha256')}
miss, miss_nr, ntok, ntok_nr = [], [], 0, 0
for p, s in STRS:
    for t in toks(s):
        if nonrendered(p):
            ntok_nr += 1
            if t not in UNION:
                miss_nr.append('%s | %s' % (p, t))
        else:
            ntok += 1
            if t not in UNION:
                miss.append('%s | %s' % (p, t))
EX['tokens_n'] = ntok
EX['tokens_missing_all'] = miss
EX['tokens_nonrendered_n'] = ntok_nr
EX['tokens_missing_nonrendered_fields'] = miss_nr
P('K02', '判断档渲染范围(l3/l4/reader_map, 不含自述不进渲染的 narrative/verdict_note 与 quality_gate_notes/agent_declaration)全部数字/日期记号在三报告至少一个逐字在场', 'len(缺失记号)', len(miss), 0, note='记号总数 %d' % ntok)
P('K02b', '信息项: 自述不进渲染字段的记号在三报告均不在场的条数(逐条列于 note/extra)', 'len(缺失记号)', len(miss_nr), len(miss_nr), note=' || '.join(miss_nr)[:400])
rm = [(p, s) for p, s in STRS if p.startswith('$.reader_map') and not nonrendered(p)]
m3, n3 = [], 0
for p, s in rm:
    for t in toks(s):
        n3 += 1
        if t not in MD['MAP_REPORT.md']:
            m3.append('%s | %s' % (p, t))
EX['reader_map_tokens_n'] = n3
EX['reader_map_tokens_missing_MAP'] = m3
P('K03', '读者面(reader_map, 不含自述不进渲染字段)全部数字记号在 MAP_REPORT.md 逐字在场', 'len(缺失记号)', len(m3), 0, note='记号数 %d' % n3)
cov = {fn: sum(1 for _, s in STRS if len(s) >= 12 and norm(s) in MD[fn]) for fn in FILES}
none = ['%s | %s' % (p, s[:70].replace('\n', ' ')) for p, s in STRS
        if len(s) >= 12 and not any(norm(s) in MD[fn] for fn in FILES)]
EX['verbatim_cov'] = cov
EX['strings_in_no_file'] = none
EX['strings_n_ge12'] = sum(1 for _, s in STRS if len(s) >= 12)
P('K04', '信息项: 判断档 ≥12 字串在三文件均不逐字在场的条数(逐条归类见 REVIEW 文件)', 'len(列表)', len(none), len(none), note='≥12 字串共 %d; 逐字覆盖 %s' % (EX['strings_n_ge12'], cov))
# 反向: 报告文本段不在判断档内(供人工归类为引擎面)
MK = ('【假设', '本席', '本档', '研判', '证伪', '竞争解释', '支持主解释', '尚不能区分', '支持竞争解释', '不以相邻口径')
segs, marked = {}, {}
for fn in FILES:
    out, mk = [], []
    for i, line in enumerate(RAW[fn].split('\n')):
        if line.strip().startswith('#') or re.match(r'^\|[\s:\-|]+\|$', line.strip()):
            continue
        for seg in re.split(r'\||(?<=。)|(?<=；)', line):
            seg2 = re.sub(r'^\s*(?:[-*]>?\s*|>\s*|\d+\.\s+)', '', seg).strip()
            if len(norm(seg2)) < 16 or norm(seg2) in JTEXT:
                continue
            out.append('%d: %s' % (i + 1, seg2[:150]))
            if any(m in seg2 for m in MK):
                mk.append('%d: %s' % (i + 1, seg2[:300]))
    segs[fn], marked[fn] = out, mk
EX['md_segments_not_in_judgment'] = {k: len(v) for k, v in segs.items()}
EX['md_segments_not_in_judgment_marked'] = marked
rev.write('=== 反向: 报告文本段不在判断档内 ===\n')
for fn in FILES:
    rev.write('--- %s (%d)\n' % (fn, len(segs[fn])))
    for s in segs[fn]:
        rev.write('  %s\n' % s)
rev.write('=== 判断档串在三文件均不逐字在场 ===\n')
for s in none:
    rev.write('  %s\n' % s)
print('MARKED (判断腔标记但不在判断档内的报告文本段):', json.dumps(marked, ensure_ascii=False)[:1500])

# ---------------- L 引擎渲染表自洽 ----------------
cat('L 引擎渲染表')
txt = RAW['report.md']
am = re.search(r'锚点月:\s*(\d{4}-\d{2})', txt)
anchor = am.group(1) if am else None
rows = re.findall(r'^\|\s*(\d+)\s*\|\s*(\d{4}-\d{2})\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|', txt, flags=re.M)
EX['analog_rows'] = rows
P('L01', '历史相似结构表(report.md/FULL_REPORT.md 引擎确定性面): 5 行候选、名次 1..5', 'report.md 历史相似结构表', '%d:%s' % (len(rows), ','.join(r[0] for r in rows)), '5:1,2,3,4,5')
okd = bool(rows) and all(float(rows[i][3]) <= float(rows[i + 1][3]) and float(rows[i][2]) <= float(rows[i + 1][2]) for i in range(len(rows) - 1))
P('L02', '表内「距离」与「距离分位」同向递增且分位在 0..100 内', '相邻行 距离/距离分位 不降; 0≤分位≤100', (okd and all(0 <= float(r[3]) <= 100 for r in rows)), True)
P('L03', '候选月均不晚于锚点月(无前视候选)', 'max(候选月) < 锚点月 %s' % anchor, (max(r[1] for r in rows) < anchor) if rows and anchor else False, True)
P('L04', '事后结果标注在场(「事后结果标注」「事后≠当时可知」)', 'report.md 历史相似结构节文本', (('事后结果标注' in txt) and ('事后≠当时可知' in txt)), True)
# 距离分位与候选池规模自洽: 分位 = 名次/池规模
best = None
for n in range(20, 400):
    ks = [round(float(r[3]) * n / 100.0) for r in rows]
    if all(abs(k / float(n) * 100.0 - float(r[3])) < 0.002 for k, r in zip(ks, rows)):
        best = (n, ks)
        break
EX['analog_pool_fit'] = best
P('L05', '距离分位与单一候选池规模自洽(存在 N 使各分位=名次/N×100)', 'N 与名次', '%s' % (best,), '(73, [0, 1, 22, 51, 52])', note='信息项: 候选池规模未经独立复算')
# 日度相关: 按引擎声明口径(月键共同观测相邻对: GDP pct × 失业率 pp)独立直算
g = {d.isoformat(): v for d, v in sn.series('US_REAL_GDP')}
u = {d.isoformat(): v for d, v in sn.series('UNEMPLOYMENT')}
common = sorted(set(g) & set(u))
xs = [pct(g[common[i - 1]], g[common[i]]) for i in range(1, len(common))]
ys = [u[common[i]] - u[common[i - 1]] for i in range(1, len(common))]
s5 = [s for s in rep['steps'] if s.get('step') == 'S5_compare'][0]['envelope']['data']
P('L06', 'report.md「US_REAL_GDP×UNEMPLOYMENT … pearson = -0.8936(n=37 对,共同窗 2017-01..2026-07)」之对数', 'series_store 共同月键相邻对数', len(xs), 37, note='共同月键 %d 个 %s..%s' % (len(common), common[0], common[-1]))
P('L07', '同上 pearson 直算(GDP 环比 pct × 失业率环比 pp)', '本席 pearson(共同月键相邻变化对)', pearson(xs, ys), s5['pearson_returns'], tol=1e-9, note='渲染值 -0.8936')
gaps = [(common[i - 1], common[i]) for i in range(1, len(common)) if (D(common[i]) - D(common[i - 1])).days > 100]
EX['gdp_common_gaps'] = gaps
P('L08', '引擎警示「共同观测窗内最大间隔 6 个月(缺失月份)」属实(共同月键缺 2025-10 一季)', '共同月键相邻间隔 >100 天的间隔数 / 引擎 warnings 含该警示', len(gaps), 1 if any('最大间隔 6 个月' in w for w in [s for s in rep['steps'] if s.get('step') == 'S5_compare'][0]['envelope'].get('warnings', [])) else 0, note='%s' % gaps)

# ---------------- X 补充核验 ----------------
cat('X 补充核验')
jp = sn.series('JP_POLICY_RATE')


def mid(lo, hi):
    out = []
    for i in range(1, len(jp)):
        d = jp[i][1] - jp[i - 1][1]
        if lo <= jp[i][0] <= hi and 0.001 + 1e-12 < abs(d) < 0.03:
            out.append('%s:%+.4f' % (jp[i][0].isoformat()[:7], d))
    return out


EX['jp_mid_diffs_all'] = mid(dt.date(1900, 1, 1), dt.date(2100, 1, 1))
P('X01', 'C3「持平月份的相邻月均差均不超过 0.001,已见台阶均不小于 0.066」——政策窗及此前持平段(2024-04..2026-10)内 0.001<|相邻月差|<0.03 的月数', 'series_store.JP_POLICY_RATE 相邻月差', len(mid(dt.date(2024, 4, 1), dt.date(2026, 10, 1))), 0, note='全序列(1985-07..2026-10)同类月 %d 个, 均早于 2024-04' % len(EX['jp_mid_diffs_all']))
b0 = sn.le('BEI_10Y', dt.date(2026, 8, 23))
d0 = diff_bp(b0[1], sn.val('BEI_10Y', '2026-11-19'))
P('X02', '传导环1 BEI_10Y 三个月窗结论对窗启日选择的稳健性(按 3 个月前锚 2026-08-23 最近观测起算)', 'series_store.BEI_10Y %s→2026-11-19' % b0[0].isoformat(), (d0 < 0), True, note='%s→%s = %+.1fbp' % (b0[1], sn.val('BEI_10Y', '2026-11-19'), d0))
fut = set()
for _, s in STRS:
    for m in re.finditer(r'\d{4}-\d{2}-\d{2}', s):
        if D(m.group(0)) > cut:
            fut.add(m.group(0))
P('X03', '判断档内晚于截止日的日期全集(应仅为任务窗口界/可见日/发布日/期限类前瞻日期)', 'agent_judgment 全文日期 > 2026-11-23', ','.join(sorted(fut)), '2026-11-30,2026-12-15,2026-12-16,2027-01-15,2027-01-16,2027-02-15,2027-02-16')
okc, bad = True, []
for p, s in STRS:
    ds = [m.group(0) for m in re.finditer(r'\d{4}-\d{2}-\d{2}', s) if D(m.group(0)) > cut]
    if ds and p.endswith('.deadline'):
        continue
    if ds and not any(k in s for k in ('可见', '期限', '发布日', '【假设', '情景', '证伪', '任务窗口')):
        okc = False
        bad.append(p)
P('X04', '上述前瞻日期所在串均为期限字段或带可见日/发布日/假设/情景/任务窗口语境(未被当作已发生证据)', 'agent_judgment 全文', okc, True, note='违规路径=%s' % bad)
refs = [s for p, s in STRS if re.search(r'evidence_refs\[\d+\]$', p)]
obs = sorted(set(re.search(r'@(\d{4}-\d{2}-\d{2})$', s).group(1) for s in refs if re.search(r'@(\d{4}-\d{2}-\d{2})$', s)))
P('X05', '全部证据引用的观测日不晚于截止日', 'agent_judgment evidence_refs 观测日最大值', obs[-1] if obs else None, '2026-11-23', note='引用 %d 条, 观测日 %d 个' % (len(refs), len(obs)))
bw = sn.win('BEI_10Y', dt.date(2025, 11, 23), dt.date(2026, 11, 23))
mn = min(bw, key=lambda x: x[1])
P('X06', '传导环1「最新 2.15(观测 2026-11-20，12 个月窗内最低)」', 'series_store.BEI_10Y 12 个月窗最小值', '%s@%s' % (mn[1], mn[0].isoformat()), '2.15@2026-11-20', note='窗内观测 %d' % len(bw))
rev.close()
json.dump({'points': PTS, 'extra': EX}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('POINTS', len(PTS), 'MISMATCH', sum(1 for p in PTS if not p['ok']))
