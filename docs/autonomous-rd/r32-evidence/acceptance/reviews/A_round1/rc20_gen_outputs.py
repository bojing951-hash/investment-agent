# -*- coding: utf-8 -*-
"""rc20: 一次性生成 Audit-R32 A 席 Round-1 两件产出(PROSE-round1.md / VERDICT-round1.json)。
用法(解释器不在数据目录内启动):
  草稿(只写本席目录内 mid_rc20_* 草稿并打印核对信息, 不写正式产出):
    cd /tmp && /usr/bin/python3 -I rc20_gen_outputs.py <run_dir> <snapshot.json> <points.jsonl> draft
  正式写出(两件正式产出均须尚不存在; 有任何核对问题时中止且不写; 写出后本脚本拒绝再次写出):
    cd /tmp && /usr/bin/python3 -I rc20_gen_outputs.py <run_dir> <snapshot.json> <points.jsonl> write
只读: 只读规程许可的只读面(运行目录内受审文件、overlay 日历与快照、安装树快照)与本席台账; 只写本席目录内文件。
"""
import sys, os, re, json, hashlib, collections, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L

R, SNAP, PTS, MODE = sys.argv[1:5]
assert MODE in ('draft', 'write'), MODE
D = os.path.dirname(os.path.abspath(PTS))
OUT_MD = os.path.join(D, 'PROSE-round1.md')
OUT_JS = os.path.join(D, 'VERDICT-round1.json')
DR_MD = os.path.join(D, 'mid_rc20_prose_draft.md')
DR_JS = os.path.join(D, 'mid_rc20_verdict_draft.json')
PROBLEMS = []


def need(cond, msg):
    if not cond:
        PROBLEMS.append(msg)
    return bool(cond)


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def rd(p):
    with open(p, encoding='utf-8') as f:
        return f.read()


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def mt(p):
    return datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime('%Y-%m-%d %H:%M:%S')


# ====================== 只读面 ======================
cal = load(os.path.join(R, 'root_overlay', 'config', 'release_calendar.json'))
snap = load(SNAP)
snap_ov = os.path.join(R, 'root_overlay', 'data', 'daily', 'research_snapshot_20261123.json')
F = L.Face(snap, cal)
aj = load(os.path.join(R, 'agent_judgment.json'))
rep = load(os.path.join(R, 'report.json'))
MAP = rd(os.path.join(R, 'MAP_REPORT.md'))
FULL = rd(os.path.join(R, 'FULL_REPORT.md'))
REP = rd(os.path.join(R, 'report.md'))
Q = rd(os.path.join(R, 'question_verbatim.txt')).strip()
env = load(os.path.join(R, 'AGENT_SEAT_ENVELOPE.json'))
map_sha = sha(os.path.join(R, 'MAP_REPORT.md'))
map_sha_file = (re.findall(r'[0-9a-f]{64}', rd(os.path.join(R, 'MAP_REPORT.sha256'))) or [''])[0]
snap_sha, snap_ov_sha = sha(SNAP), sha(snap_ov)
RUN = rep.get('run') or {}
STAMP = RUN.get('git_head')
need(STAMP == '36499bb78a18dea1ff2b027074088b0ba404c3b8', '代码印章不符: %s' % STAMP)
need(map_sha == map_sha_file == 'ad7b4cd00975b8b5429d8ee6e1f9f4e146910fada2e3c09dc525dfa66b7a001d', 'MAP_REPORT sha256 不符')
need(snap_sha == snap_ov_sha and snap_sha.startswith('2d650f1128cdd356'), '快照 sha256 不符或两份快照不一致')
AUD = ['MAP_REPORT.md', 'FULL_REPORT.md', 'report.md', 'agent_judgment.json', 'report.json', 'evidence_index.json',
       'views_digest.json', 'AGENT_SEAT_ENVELOPE.json', 'question_verbatim.txt', 'MAP_REPORT.sha256',
       'root_overlay/config/release_calendar.json', 'root_overlay/data/daily/research_snapshot_20261123.json']
aud_mt = [(f.split('/')[-1], mt(os.path.join(R, f))) for f in AUD]
seat_first = os.path.getmtime(os.path.join(D, '_protocol.md'))
need(all(os.path.getmtime(os.path.join(R, f)) < seat_first for f in AUD) and os.path.getmtime(SNAP) < seat_first,
     '受审文件修改时间不早于席位首文件')

# ====================== 台账 ======================
recs = [json.loads(l) for l in open(PTS, encoding='utf-8') if l.strip()]
for i, r in enumerate(recs):
    r['_i'] = i
NT = sum(1 for r in recs if r['ok'] is True)
NF = sum(1 for r in recs if r['ok'] is False)
NA = [r for r in recs if r['ok'] == 'NA']
need(NF == 0, '台账存在偏离记录 %d 条' % NF)
need(all(str(r.get('where', '')).strip() for r in recs), '台账存在空 where 记录')
dupk = collections.Counter(json.dumps([r.get(k) for k in ('section', 'src', 'computed', 'reported', 'where')],
                                      ensure_ascii=False) for r in recs)
NDUP = sum(c - 1 for c in dupk.values() if c > 1)
need(NDUP == 0, '台账存在重复记录 %d 条' % NDUP)
sec_count = collections.OrderedDict()
for r in recs:
    c = sec_count.setdefault(str(r.get('section', '')), [0, 0, 0])
    c[0] += 1
    if r['ok'] is True:
        c[1] += 1
    elif r['ok'] == 'NA':
        c[2] += 1
OKM = {True: '一致', False: '偏离', 'NA': 'NA(登记)'}


def compress(ids):
    ids = sorted(set(i for i in ids if i is not None))
    out, i = [], 0
    while i < len(ids):
        j = i
        while j + 1 < len(ids) and ids[j + 1] == ids[j] + 1:
            j += 1
        out.append('#%d' % ids[i] if j == i else '#%d–#%d' % (ids[i], ids[j]))
        i = j + 1
    return out


def comp(ids, maxlen=96):
    segs = compress(ids)
    s = '、'.join(segs)
    if len(s) <= maxlen:
        return s
    return '、'.join(segs[:5]) + ' 等'


IDX = collections.OrderedDict([
    ('c1_levels', [(885, 895)]), ('ecb_two', [(896, 896)]), ('jprate_path', [(897, 897)]), ('rates_12m', [(898, 898)]),
    ('near_assets', [(899, 899)]), ('cpi_pce_after', [(900, 900)]), ('c3_latest', [(901, 903)]), ('overnight', [(904, 904)]),
    ('lpr', [(905, 905)]), ('scissors', [(906, 906)]), ('scn1_hist', [(908, 911)]), ('scn2_hist', [(912, 914)]),
    ('dims', [(915, 915)]), ('overlap', [(916, 916)]), ('scen_thr', [(917, 917)]), ('dfedtaru', [(918, 918)]),
    ('dec_dates', [(919, 919)]), ('panel_conv', [(920, 922)]), ('boj_fields', [(923, 923)]), ('pol_entries', [(924, 924)]),
    ('ecb_boj', [(925, 925)]), ('sep_dec', [(926, 926)]), ('cand_rank', [(927, 927)]), ('turn1', [(928, 928)]),
    ('jpcpi_high', [(929, 929)]), ('turn0_jump', [(930, 930)]), ('core_diff', [(931, 931)]), ('ev_labels', [(932, 932)]),
    ('asset_win', [(332, 344)]), ('cpi_path', [(354, 357)]), ('cn_ppi', [(400, 407)]), ('pmi', [(415, 418)]),
    ('tokyo', [(430, 438)]), ('omo', [(449, 454)]), ('gaps', [(490, 495)]), ('decomp', [(508, 515)]), ('dist_metrics', [(544, 544)]),
    ('scen', [(547, 555)]), ('coverage', [(579, 579)]), ('sign_agree', [(581, 583)]), ('c2', [(686, 687)]), ('omo_win', [(779, 779)]),
    ('text_render', [(855, 863)]), ('gate_a', [(865, 869)]), ('sync_narr', [(870, 873)]), ('basis_diff', [(874, 874)]),
    ('nikkei_1123', [(876, 876)]), ('dff_anchors', [(877, 877)]), ('hicp_rule', [(878, 884)]),
    ('assets12', [(326, 328)]), ('spx_windows', [(329, 330)]), ('usdcny', [(331, 331)]), ('usdjpy_daily', [(345, 346)]),
    ('hy_week', [(498, 506)]), ('brent', [(507, 507), (525, 528)]), ('bei_tr', [(516, 518)]), ('vix_1m', [(519, 519)]),
    ('dff_panel', [(520, 520)]), ('hy_levels', [(522, 524)]), ('time_marks', [(529, 533)]), ('core_cpi', [(546, 546)]),
    ('gdp_corr', [(854, 854)]),
])


def C(name):
    ids = []
    for a, b in IDX[name]:
        ids.extend(range(a, b + 1))
    need(max(ids) < len(recs), '台账范围越界: ' + name)
    return comp([i for i in ids if i < len(recs)])


def S(sub):
    ids = [r['_i'] for r in recs if str(r.get('section', '')) == sub] or [r['_i'] for r in recs if sub in str(r.get('section', ''))]
    need(len(ids) > 0, '台账分节未找到: ' + sub)
    return '『' + sub + '』' + str(len(ids)) + ' 条(' + comp(ids) + ')'


def blob(r):
    return ' '.join([str(r.get('section', '')), str(r.get('src', '')), str(r.get('where', '')), str(r.get('note', '')),
                     json.dumps(r.get('computed'), ensure_ascii=False), json.dumps(r.get('reported'), ensure_ascii=False)])


def has_tok(rec, tok):
    return re.search(r'(?<![0-9.])' + re.escape(tok) + r'(?![0-9])', json.dumps([rec.get('computed'), rec.get('reported')], ensure_ascii=False)) is not None


# ====================== 受审文本定位工具 ======================
def leaves(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, (path + '.' + k) if path else k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, '%s[%d]' % (path, i))
    elif isinstance(o, str):
        yield path, o


LEAVES = list(leaves(aj))


def flex(s):
    out = []
    for ch in s:
        m = {'(': '[(（]', ')': '[)）]', ',': '[,，]', ';': '[;；]', ':': '[:：]'}.get(ch)
        out.append(m if m else re.escape(ch))
    return ''.join(out)


def locate(s):
    pat = re.compile(flex(s))
    res = {}
    hits = [(p, m.group(0)) for p, t in LEAVES for m in pat.finditer(t)]
    if hits:
        res['agent_judgment.json'] = hits
    for nm, txt in (('MAP_REPORT.md', MAP), ('FULL_REPORT.md', FULL), ('report.md', REP)):
        ms = [m.group(0) for m in pat.finditer(txt)]
        if ms:
            res[nm] = ms
    return res


def O(s, label=''):
    """受审原句(精确匹配; 括号/逗号等全半角均可); 找不到则登记问题"""
    res = locate(s)
    for nm in ('agent_judgment.json', 'MAP_REPORT.md', 'FULL_REPORT.md', 'report.md'):
        if nm in res:
            v = res[nm][0]
            return v[1] if nm == 'agent_judgment.json' else v
    PROBLEMS.append('受审文本中未找到原句%s: %r' % (label, s))
    return '(未找到原句)' + s


def W(s):
    res = locate(s)
    parts = []
    if 'agent_judgment.json' in res:
        parts.append('agent_judgment.json ' + '、'.join(p for p, _ in res['agent_judgment.json'][:5]))
    for nm, txt in (('MAP_REPORT.md', MAP), ('FULL_REPORT.md', FULL), ('report.md', REP)):
        if nm in res:
            pat = re.compile(flex(s))
            lines = [i + 1 for i, ln in enumerate(txt.split('\n')) if pat.search(ln)]
            parts.append('%s 第 %s 行' % (nm, '、'.join(str(x) for x in lines[:6])))
    return '; '.join(parts) if parts else '(未定位)'

# ====================== 自冻结快照直算的事实(仅用于叙述与改句) ======================
def yoy4(name, ym):
    t = L.yoy_level(F, name, ym)
    return None if t[0] is None else t[0]


Y = {(nm_, ym): yoy4(nm_, ym) for nm_ in ('CPI', 'CORE_PCE') for ym in ('2026-04', '2026-05', '2026-07', '2026-08')}
HICP = F.monthly('EA_HICP_YOY')
SRC_Y = 'research_snapshot_20261123.json series_store.CORE_PCE(同比=观测月水平/前一年同月水平-1)'
need(round(Y[('CPI', '2026-07')], 2) == 3.30 and round(Y[('CPI', '2026-08')], 2) == 3.35 and round(Y[('CPI', '2026-04')], 2) == 3.78, 'CPI 同比与受审稿不符')
need(round(Y[('CORE_PCE', '2026-05')], 2) == 3.16 and round(Y[('CORE_PCE', '2026-07')], 2) == 3.00, 'CORE_PCE 同比与受审稿不符')
need(HICP.get('2026-05') == 3.2 and HICP.get('2026-06') == 2.8 and HICP.get('2026-07') == 2.9 and HICP.get('2026-08') == 3.2, 'HICP 值不符')
VIS = {d: L.visible_latest(F, 'EA_HICP_YOY', d) for d in ('2026-06-11', '2026-09-10')}
REL08 = L.release_date(F, 'EA_HICP_YOY', '2026-08-01')
ME08 = L.month_end('2026-08')
need(VIS['2026-09-10']['obs_date'] == '2026-07-01' and VIS['2026-09-10']['value'] == 2.9 and REL08[0] == '2026-09-16'
     and ME08 == '2026-08-31' and VIS['2026-06-11']['obs_date'] == '2026-04-01', 'HICP 注册表口径不符')
YTXT = ('CPI 同比 2026-04 %.4f / 2026-07 %.4f / 2026-08 %.4f, CORE_PCE 同比 2026-05 %.4f / 2026-07 %.4f' % (
    Y[('CPI', '2026-04')], Y[('CPI', '2026-07')], Y[('CPI', '2026-08')], Y[('CORE_PCE', '2026-05')], Y[('CORE_PCE', '2026-07')]))

GA = snap.get('gate_a') or {}
ALIAS = {'CN_OMO_7D': ['7天逆回购'], 'CN_POLICY_OVERNIGHT': ['隔夜逆回购', '隔夜利率'],
         'EA_REAL_GDP_YOY': ['欧元区GDP同比', '欧元区实际GDP'], 'JP_REAL_GDP_YOY': ['日本GDP同比', '日本实际GDP'],
         'JP_CPI_TOKYO_YOY': ['东京CPI', '东京区CPI'], 'ECB_DFR': ['ECB_DFR', 'DFR', '存款便利利率'],
         'ECB_MRO': ['ECB_MRO', 'MRO', '主要再融资'], 'US_REAL_GDP': ['US_REAL_GDP', '美国GDP', '美国实际GDP'],
         'JTSJOL': ['JTSJOL', 'JOLTS', '职位空缺'], 'M2SL': ['M2SL'], 'SPX_EPS': ['SPX_EPS', '每股收益'],
         'SPX_PE_TTM': ['SPX_PE_TTM', '市盈率'], 'CN_SF_FLOW': ['CN_SF_FLOW', '社融', '社会融资'],
         'BUND_10Y': ['BUND_10Y', '德国国债'], 'BUND_2Y': ['BUND_2Y']}
core_txt = '\n'.join(t for _, t in leaves({'l3': aj.get('l3'), 'l4': aj.get('l4'), 'reader_map': aj.get('reader_map')}))
qgn = aj.get('quality_gate_notes') or []
IDX_GATE = [i for i, n in enumerate(qgn) if 'Gate A' in n]
IDX_STOCK = [i for i, n in enumerate(qgn) if '存量观测' in n]


def gate_rows(cls):
    rows = []
    for m in GA.get(cls) or []:
        s = (snap.get('series_store') or {}).get(m)
        n = len(s['dates']) if s else 0
        last = s['dates'][-1] if s and s['dates'] else '—'
        hit = list(collections.OrderedDict.fromkeys(a for a in [m] + ALIAS.get(m, []) if a in core_txt))
        rows.append((m, n, last, '、'.join(hit) if hit else '—'))
    return rows


GM, GD = gate_rows('noncore_missing'), gate_rows('noncore_degraded')
USED_M = [r[0] for r in GM if r[3] != '—' and r[1] > 0]
USED_D = [r[0] for r in GD if r[3] != '—' and r[1] > 0]
need(len([r for r in GM if r[1] > 0]) == 5, 'Gate A 非核心缺口存量序列数不为 5')

HCM = re.search(flex('中国未跟进加息') + '.*?' + flex('(背离)'), aj['reader_map']['headline_conclusion'])
HEAD = HCM.group(0) if HCM else None
need(HEAD is not None, '首页结论未找到「中国未跟进加息」子句')
PP = F.monthly('CN_PPI_YOY')
PP_MIN_ALL = min((v, k) for k, v in PP.items() if v is not None)
PP_MIN_23 = min((v, k) for k, v in PP.items() if v is not None and k >= '2023-01')
JPC = F.monthly('JP_CPI_YOY')
need(PP.get('2025-11') == -2.2 and PP.get('2026-10') == 5.7 and PP.get('2026-07') == 3.5, 'CN_PPI 值不符')


def tokchk(i, toks, label):
    need(all(has_tok(recs[i], t) for t in toks), '台账 #%d 数值不含叙述词元 %s (%s)' % (i, toks, label))


def tokfind(toks):
    return [r['_i'] for r in recs if all(has_tok(r, t) for t in toks)]


TF1 = sorted(set(i_ for t_ in ['-5.24', '-11.01', '-5.28', '-1.73', '-5.78'] for i_ in tokfind([t_])))
TF2 = tokfind(['-7.63'])
TFH = [i_ for i_ in TF1 + TF2 if recs[i_].get('section') == '⑧历史事后窗']
need(len(TFH) >= 6 and TF2, 'C2 2022-06 / 2023-10 段逐窗数字未在台账中找到: %s %s' % (TF1, TF2))
JPR = F.monthly('JP_POLICY_RATE')
need(all(round(JPR[k_], 3) == v_ for k_, v_ in (('2025-11', 0.478), ('2025-12', 0.557), ('2026-03', 0.728), ('2026-04', 0.727), ('2026-07', 0.978), ('2026-08', 0.977), ('2026-10', 1.227))),
     'JP_POLICY_RATE 月均值不符: %s' % {k_: JPR.get(k_) for k_ in ('2025-11', '2025-12', '2026-03', '2026-04', '2026-07', '2026-08', '2026-10')})
tokchk(874, ['1.4144', '0.3514'], '两口径差')
tokchk(870, ['2.3', '3.66', '-2.2', '-0.7'], '2025-02 当时可知面')
tokchk(897, ['-0.1', '6'], 'JP_POLICY_RATE 舍入级微降')
tokchk(916, ['129'], '事后窗重叠日数')
tokchk(326, ['8.03'], 'SPX 12 个月窗')
tokchk(327, ['22.47'], 'NIKKEI225 12 个月窗')
tokchk(328, ['9.93'], 'DAX 12 个月窗')

# ====================== 六查叙述 ======================
c1, c2, c3 = aj['l3']['contradictions']
m1, m2 = aj['l3']['mechanism_chains']
tr1, tr2 = aj['reader_map']['transmission']
sc = (aj.get('l4') or {}).get('scenarios')
need(len(aj['l3']['contradictions']) == 3 and len(m1['links']) == 4 and len(m2['links']) == 2
     and len(tr1['links']) == 3 and len(tr2['links']) == 1 and isinstance(sc, list) and len(sc) == 2, '判断档结构与规程所述不符')
SIX = []


def H(level, s):
    SIX.append('#' * level + ' ' + s + '\n')


def PJ(*parts):
    SIX.append(''.join(str(p) for p in parts) + '\n')


def summ(st, n):
    return (st[:n] + '…(下略)') if len(st) > n else st


def expl(c):
    out = []
    for e in c.get('competing_explanations') or []:
        if isinstance(e, dict):
            txt = ' '.join(str(v) for k, v in e.items() if isinstance(v, str))
            out.append((txt[:170] + '…') if len(txt) > 170 else txt)
        else:
            out.append(str(e)[:170])
    return out


H(2, '5 规程第 4 节: 六查 + 证伪(逐条矛盾陈述、逐条机制链)')
PJ('六查项: ① 证据相关性 ② 支持度 ③ 竞争解释(须为同证据可容纳、且在点名区分指标上预言方向不同的真正竞争, 非稻草人) ④ 反对证据(有无未披露的反向事实) ⑤ 结论是否超出证据 ⑥ 证伪条件可观测性(被点名的区分指标须在证据面在场, 两解释在其上的预言方向须确实不同)。每条至少一次反方攻击, 攻击记录见 5.8(与 VERDICT JSON 的 counterexamples_sought 逐条对应)。')
H(3, '5.1 矛盾陈述 C1(主线综合 / 增长担忧 / 跨境溢出·技术面)')
PJ('**受审主张(摘要)**: ', summ(c1['statement'], 330))
PJ('**竞争解释(受审稿原文摘要)**: ', ' | '.join(expl(c1)))
PJ('**① 证据相关性**: ', len(c1.get('evidence_refs') or []), ' 条 evidence_refs 与『证据面最新水平』清单 11 项逐一核对, 取值、观测日、引用标签日期、规则发布日均取自冻结快照且不晚于截止日 2026-11-23; 其中 CN_PPI_YOY、CN_CPI_YOY 的引用标签为月末日期而观测日为月初(同月), 受审稿质量注记已披露。台账 ', C('c1_levels'), '、', C('ev_labels'), '。')
PJ('**② 支持度**: 事实面逐环成立——通胀端 CPI 同比 2026-02→2026-05 2.434→4.1666、EA_HICP_YOY 1.9→3.2、CN_PPI_YOY -0.9→3.9, 2026-05 后回落未再越过高点(', C('cand_rank'), '、', C('cpi_path'), '、', C('cpi_pce_after'), '); 政策端 ECB_DFR 两度各 +25 个基点、JP_POLICY_RATE 一年窗净 +75 个基点、DFF 一降一升净变 0(', C('ecb_two'), '、', C('jprate_path'), '、', C('panel_conv'), '、', C('dfedtaru'), '); 利率端 12 个月窗名义 +91 = 实际 +102 + 盈亏平衡 -11 个基点、残差 0(', C('decomp'), '); 资产端近 1 个月 SPX、NIKKEI225、GOLD_F 收缩而 DXY、VIX 走高(', C('near_assets'), '、', C('asset_win'), ')。资产收缩一腿只在近窗成立: 12 个月窗 SPX +8.03%、NIKKEI225 +22.47%、DAX +9.93% 与实际利率同向上行(', C('assets12'), '、', C('spx_windows'), ')——受审稿在 C1 括注(资产收缩一腿属于近月窗口的事实、全年窗口内股指并未下行)与机制链资产环明示。')
PJ('**③ 竞争解释**: 主链、增长担忧、跨境溢出·技术面三解在同一证据下均可容纳, 且在点名的区分指标(BEI_10Y、TIPS_10Y、HY_OAS、USDJPY)上预言方向不同 → 真正竞争, 非稻草人。')
PJ('**④ 反对证据**: 对主链——近 1 个月 BEI_10Y -19 个基点而名义 -8、实际 +11 个基点, 与主链『盈亏平衡大体稳定』一腿相左, 受审稿已写入并据此只给『部分相容』(', C('decomp'), '); 对跨境溢出·技术面——同窗 USDJPY 156.49→159.35(+1.82%)与 SPX -5.51% 并存, 套息平仓一腿未获支持, 受审稿已写入(', C('usdjpy_daily'), ')。未发现未披露的反向事实。')
PJ('**⑤ 结论是否超出证据**: 裁定『不足以裁决』并把共动与因果分开, 未超出。')
PJ('**⑥ 证伪条件可观测性**: 四项区分指标均在本轮证据面在场, 最新观测日不早于 2026-11-19(', C('dist_metrics'), '); 两解释在其上的预言方向相反(见 5.6)。')
PJ('**反方攻击**: 5.8 第 1–3 条。**小结**: 无 MAJOR; NIT-10。')
H(3, '5.2 矛盾陈述 C2(历史相似段的事后路径分歧 / 相似度低维覆盖)')
PJ('**受审主张(摘要)**: ', summ(c2['statement'], 420))
PJ('**竞争解释(受审稿原文摘要)**: ', ' | '.join(expl(c2)))
PJ('**① 证据相关性**: ', len(c2.get('evidence_refs') or []), ' 条 evidence_refs 为四项资产的当前水平锚点(受审稿自述不承载历史段数字); 历史段的逐窗数字、当时可知面与同步性格逐格取自冻结序列重算, 全部一致(台账 ', S('⑧历史事后窗'), '、', S('⑧历史事后窗(细表)'), '、', S('⑧同步面/当时可知'), ')。')
PJ('**② 支持度**: 2022-06 段三个月窗 DAX、SHCOMP、SPX、NIKKEI225 均为负而十二个月窗除 SHCOMP 外转正; 2025-03、2023-10 段风险资产与 GOLD_F 多数窗走强、DXY 走弱(例外 2023-10 段上证指数三个月窗为负, 受审稿已披露)(', C('c2'), '); 逐窗数字所在记录 #', comp(TFH), '; TOP-N 事后符号一致率 GOLD_F、SPX 六/十二个月窗为 1.0, 其余各窗 0.6–0.8(', C('sign_agree'), '); 状态向量维度覆盖 growth 0.17、inflation 0.33、credit 0.5 为引擎面原值(', C('coverage'), ')。')
PJ('**③ 竞争解释**: 『各段独有政策/冲击环境』(标【假设】)与『相似度量低维覆盖』相容且均为真竞争。')
PJ('**④ 反对证据**: 与『分歧明显』方向相反的事实是 GOLD_F 与 SPX 六/十二个月窗在全部 TOP-5 段符号一致(1.0)——受审稿同句如实列出; 2025-03 段十二个月事后窗(至 2026-03-31)与本轮研究窗重叠 129 天、样本非独立——受审稿已披露(', C('overlap'), '); 未发现未披露的反向事实。')
PJ('**⑤ 结论是否超出证据**: 只作结构对照与情景校准、不作预测, 未超出。')
PJ('**⑥ 证伪条件可观测性**: 本条为描述性登记, 未设区分指标; 情景段另设数字阈值(见 5.7)。')
PJ('**历史段同步性(规程第 4 节专项)**: 三段九格的同步/分化主张与引擎地区×维度同步面逐格一致; 当时可知面数值(如 2025-02 欧元区 HICP 2.3、日本 CPI 3.66、中国 PPI -2.2、中国 CPI -0.7)经发布纪律核对一致, 无『面为缺证而叙述称同步』或叙述与面冲突的情形(', S('⑧同步面/当时可知'), '、', C('sync_narr'), ')。')
PJ('**反方攻击**: 5.8 第 4–6 条。**小结**: 无 MAJOR; NIT-4、NIT-11。')
H(3, '5.3 矛盾陈述 C3(中国: PPI 上行而政策利率未上调)')
PJ('**受审主张(摘要)**: ', summ(c3['statement'], 330))
PJ('**竞争解释(受审稿原文摘要)**: ', ' | '.join(expl(c3)))
PJ('**① 证据相关性**: ', len(c3.get('evidence_refs') or []), ' 条 evidence_refs(CN_PPI_YOY、CN_CPI_YOY 2026-10 观测, CN_LPR_1Y 2026-11-20, USDCNY 2026-11-23)逐值核对(', C('c3_latest'), '、', C('lpr'), '、', C('usdcny'), ')。')
PJ('**② 支持度**: CN_PPI_YOY 自 2025-11 窗内低点 -2.2 升至 2026-10 的 5.7(2026-07 曾回落至 3.5), 为四地 12 个月窗最大价格摆动; CN_CPI_YOY 最新 0.7, 与 PPI 剪刀差 5.0 个百分点(', C('cn_ppi'), '、', C('c3_latest'), '、', C('scissors'), '); CN_LPR_1Y 一年窗内 12 个观测均为 3.0(最新 2026-11-20), CN_OMO_7D 一年窗内 199 个观测均为 1.4(末观测 2026-10-30), 隔夜逆回购利率 2026-11-02 起 16 个观测均为 1.25, CN_PMI_MFG 最新 49.3(', C('lpr'), '、', C('omo_win'), '、', C('omo'), '、', C('overnight'), ')。')
PJ('**③ 竞争解释**: 输入型/供给、内需不足、汇率/资本流动(【尚未验证】)三解同证据可容纳; 引擎无中国利率预期与资本流动序列, 第三解不可裁决, 受审稿如实标注(', C('gaps'), ')。')
PJ('**④ 反对证据**: USDCNY 12 个月 -6.19%(7.1075→6.6676)与『贬值/外流压力』读法相反——受审稿已写入解释 C(', C('usdcny'), '); 7 天逆回购末观测距截止日 24 天、其后缺观测, 换锚后仅 16 个交易日观测——受审稿逐处披露(', C('omo'), '); Gate A 缺口披露未渲染入报告(MINOR-3)。')
PJ('**⑤ 结论是否超出证据**: 『三种解释不可区分』与证据相称, 未下因果结论。')
PJ('**⑥ 证伪条件可观测性**: 三解未被赋予可观测区分指标。本条在判断档登记为『尚未验证』的矛盾陈述而非机制链, 受审稿未对其作出可被证伪的因果断言, 故不按『证伪条件不可观测』计 MAJOR; 建议后续为解释 A/B 指定区分指标(如 PPI-CPI 剪刀差与 CN_CPI_YOY 的后续走向)。')
PJ('**反方攻击**: 5.8 第 7–8 条。**小结**: 无 MAJOR; MINOR-3(披露位置)。')
H(3, '5.4 机制链 M1『' + str(m1.get('title', '')) + '』(四环)')
PJ('**环 1 冲击环(E1)**: 事实——美欧通胀与中国生产价格 2026-02→2026-05 同窗回升; 布伦特原油月末 2026-02 72.48→2026-03 118.35→2026-05 92.05(首尾 +27.00%), 2026-06 月末 72.92, 截止日 88.19(盘中快照)、当月至今 -25.03%; 美国核心 CPI 同比 2026-02 2.47→2026-05 2.82(', C('brent'), '、', C('core_cpi'), ')。对质(区分指标 BRENT_F, 预注册窗 2026-02 至 2026-05): 主解释『同窗显著上行』获支持, 竞争解释『大体持平』未获支持; 核心通胀同窗上行对两解释均相容(受审稿自述不构成区分观测)。')
PJ('**环 2 政策环(E3: 时序为事实、动机为假设)**: 时序——政策变动月(2026-06 起)晚于通胀转折月(至 2026-05): 美联储 2025-12-10 决议、12-11 生效 -25 个基点, 2026-09-16 决议、09-17 生效 +25 个基点(决议日=生效日前一日惯例); 欧央行生效日 2026-06-17、2026-09-16 各 +25 个基点(决议日按『生效日前上一个周四』回推 2026-06-11、2026-09-10, 标【推断】); 日本央行 2026-09-18 决议、09-24 生效(冻结日历实录)(', C('dfedtaru'), '、', C('dec_dates'), '、', C('boj_fields'), '、', C('pol_entries'), '、', C('ecb_boj'), '、', C('sep_dec'), ')。决议时点可见数据(注册表发布规则)——美国 CPI: 欧央行首次决议前可见 2026-04 观测 3.78(处上行段), 第二次决议前 2026-07 观测 3.30、美联储与日本央行决议前 2026-08 观测 3.35(均低于 2026-05 高点 4.17); 核心 PCE 2026-07 观测 3.00 低于 2026-05 高点 3.16; 欧元区 HICP 2026-07 观测 2.9 低于 2026-05 高点 3.2; 日本 CPI 2026-07 观测 1.97 处回升段。本席自快照直算复核: ', YTXT, '; EA_HICP_YOY 2026-06 2.8 / 2026-07 2.9 / 2026-08 3.2(出处: ', SRC_Y, '; series_store.EA_HICP_YOY; series_store.CPI)。动机环标【假设】, 证伪指标 CPI 在场。唯欧元区 HICP 发布规则在引擎内有双口径, 受审稿此环只按注册表口径立论(MINOR-1; 台账 ', C('hicp_rule'), ')。')
PJ('**环 3 利率环(E1)**: 12 个月窗(2025-11-19→2026-11-19 共同交易日)名义 +91 = 实际 +102 + 盈亏平衡 -11 个基点, 恒等残差 0; 水平 UST_10Y 5.04、TIPS_10Y 2.88、BEI_10Y 2.16@2026-11-19(最新 2.15@2026-11-20)(', C('decomp'), '、', C('rates_12m'), ')。')
PJ('**环 4 资产环(E2: 缺环为假设)**: 近 1 个月资产窗、同日收盘口径、TIPS/SPX 窗口对照、HY_OAS 水平 3.52(约第 92 百分位; 序列高点 4.61@2025-04-07; 上一次不低于最新读数为 2025-05-09 的 3.53)全部一致(', C('asset_win'), '、', C('hy_week'), '、', C('hy_levels'), '、', C('spx_windows'), ')。')
PJ('**六查**: ① 四环 evidence_refs 均为本轮冻结快照事实, 标签日期与观测日关系同 C1。② E1 两环(冲击、利率)为纯事实且逐位一致; E3、E2 两环以【假设】字面标明不可验证的环节。③ 竞争解释——环 1『需求过热或基数效应主导』、环 2『收紧另有动机(金融稳定/汇率/正常化独立进程)』、环 4『增长担忧主导』——均与同证据相容, 且在区分指标上预言方向不同(BRENT_F 大体持平 vs 显著上行; BEI_10Y 与政策节奏脱钩 vs 收紧前上行段; BEI_10Y 明显下行且 TIPS_10Y 转平 vs TIPS_10Y 续升而 BEI_10Y 稳定), 属真正竞争。④ 反对证据——油价尖峰为暂时性(2026-06 月末回到 72.92)而通胀此后仍升; 决议前可见通胀已自高点回落; 12 个月窗内实际利率与股指同向上行——三项均由受审稿自己写入并据此限定结论(支持度限于预注册窗、动机环降为假设、资产环标 E2 并写共动方向随窗口而异); 无未披露的反向事实。⑤ 结论未超出: 每环都写明不可验证之处, 未把时序先后或共动写成因果。⑥ 证伪可观测: 环 2 证伪指标 CPI(阈值 2.5 为数字; 2026-10 同比缺基期已披露, 2026-11 起可算), 环 4 证伪指标 HY_OAS(预警级 3.53、失效级 4.61, 均为库内可观测水平)。')
PJ('**反方攻击**: 5.8 第 9–12 条。**小结**: 无 MAJOR; MINOR-1、MINOR-2。')
H(3, '5.5 机制链 M2『' + str(m2.get('title', '')) + '』(两环)')
PJ('**环 1(E1)**: JP_POLICY_RATE(无担保隔夜拆借月均)自 2025-11 的 0.478 步进升至 2026-10 的 1.227(窗内净 +75 个基点; 步进 +8/+17/+11/+14/+7/+18 落在 2025-12、2026-01、2026-06、2026-07、2026-09、2026-10; 2026-04 与 2026-08 各有约 0.1 个基点的舍入级变动; 自 2025-12 的 0.557 起为 +67 个基点, 另一口径并记); 冻结日历载日本央行 2026-09-18 决议、2026-09-24 生效、目标 1.25, 及 2026-10-30 确认维持; USDJPY 159.35@2026-11-23(盘中快照)(', C('jprate_path'), '、', C('panel_conv'), '、', C('boj_fields'), ')。')
PJ('**环 2(E3: 整环假设)**: 引擎无 JGB 收益率历史序列, 整环不可验证; 证伪指标 USDJPY 在场(', C('gaps'), ')。')
PJ('**六查**: ① 引用为冻结快照事实与冻结日历实录。② 环 1 事实逐位一致; 环 2 无可验证事实, 已标明。③ 竞争解释『近月风险资产收缩源于美国国内利率/增长定价』与证据相容, 在 USDJPY 上预言相反(时间上解耦 vs 同现)。④ 反对证据——同窗(2026-10-23→2026-11-23)SPX -5.51% 而 USDJPY +1.82%(156.49→159.35), 主解释『风险资产收缩与日元走强同现』的预期未获支持; 逐日面 21 个交易日相关系数 0.19、同向 16 日, 仅弱同向耦合——受审稿在传导链 TR2 第一环已裁定主解释的同窗预期未获支持, 并说明竞争解释的字面预期未获完全确认(', C('usdjpy_daily'), '); 无未披露的反向事实。⑤ 结论未超出: 机制链定位为竞争性全球机制、整环假设。⑥ 证伪可观测: USDJPY 在场, 条件含可判形态(风险资产再次收缩时 USDJPY 是否同步走低)。')
PJ('**反方攻击**: 5.8 第 13–15 条。**小结**: 无 MAJOR; NIT-3、NIT-8。')
H(3, '5.6 对质环(读者面传导链 TR1 三环、TR2 一环)')
PJ('TR1-1(BRENT_F): 主解释『同窗显著上行』 vs 竞争解释『大体持平而核心通胀上行』 → 月末 72.48→92.05(首尾 +27.00%, 2026-03 冲至 118.35), 裁定『支持主解释』与数据一致(', C('brent'), ')。')
PJ('TR1-2(BEI_10Y): 主解释『收紧前处上行段且高位』 vs 竞争解释『政策续紧而 BEI_10Y 不升』 → 2026-02-27 2.25→2026-05-04 2.50(上行段成立), 首次加息决议前日 2026-06-10 为 2.34, 收紧后(2026-06-17 起)区间 2.15–2.40, 近一个月(2026-10-23→2026-11-20)2.34→2.15(竞争解释的形态亦在) → 裁定『尚不能区分』如实(', C('bei_tr'), ')。')
PJ('TR1-3(BEI_10Y、HY_OAS): 主解释『TIPS_10Y 续升而 BEI_10Y 稳定、HY_OAS 不升破高点』 vs 竞争解释『BEI_10Y 明显下行且 TIPS_10Y 转平/回落、HY_OAS 走阔』 → TIPS_10Y 12 个月 +102、近 1 个月 +11 个基点(未转平), BEI_10Y -11 / -19 个基点(下行但幅度有限), HY_OAS 3.52 未破 3.53 → 『尚不能区分』如实(', C('decomp'), '、', C('hy_levels'), ')。')
PJ('TR2-1(USDJPY): 主解释『风险资产收缩与日元走强(USDJPY 走低)同现』 vs 竞争解释『时间上解耦』 → 同窗 USDJPY +1.82% 而 SPX -5.51% → 裁定『支持竞争解释』与区分指标面一致(逐日面弱同向的保留意见受审稿已附注)(', C('usdjpy_daily'), ')。')
PJ('四环的区分指标均在证据面在场(', C('dist_metrics'), '), 两解释预言方向相反; 无『证伪条件不可观测』情形。')
H(3, '5.7 情景(L4: SCN1、SCN2)')
PJ('两情景互为对照、方向互补(台账 ', C('scen'), '、', C('scn1_hist'), '、', C('scn2_hist'), ')。证伪条件均为数字阈值且指标在场: SCN1——美国 CPI 同比回落至 2.5 以下且 CORE_PCE 回落至 2.8 以下并持续两个月(截止日读数 CPI 3.72@2026-09、CORE_PCE 3.12@2026-09, 未成立); SCN2——BEI_10Y 跌破 1.8(最新 2.15@2026-11-20, 较阈值高 35 个基点; 库内最近一次低于 1.8 为 2020-11-30 的 1.77, 较最新读数低 38 个基点; 未成立)。期限 2027-02-28, 所涉观测的规则发布日均早于期限(台账 ', C('scen_thr'), ' 为参数性数字的登记项, 不计入比对点)。截止日无已被证伪而仍列为前提的内容; 阈值(CPI 3 / 3.5 / 2.5, CORE_PCE 2.8, BEI_10Y 1.8)落在截止日读数与高点之间, 可观测。')
PJ('**反方攻击(情景)**: 指控情景阈值系为免于被证伪而事后选定 → 阈值均为数字、指标在场、期限早于所涉观测的规则发布日, 截止日读数均在未证伪一侧而触发所涉 2026-11/12 观测尚未发布; 未发现证伪条件不可观测(5.8 第 20 条)。')

CA = [
    '反方攻击 1(矛盾陈述 C1·同向共动): 指控四环链条以窗口选择拼成——资产收缩一腿只在近月窗成立(SPX 近 1 个月 -5.51%), 12 个月窗股指与实际利率同向上行(TIPS_10Y +102 个基点同期 SPX +8.03%、NIKKEI225 +22.47%、DAX +9.93%)→ 受审稿在同一句括注与机制链资产环明示共动方向随窗口而异, 三解的区分指标不依赖资产腿符号; 攻击不成立为 MAJOR, 仅留行文限定(NIT-10)。',
    '反方攻击 2(矛盾陈述 C1·解释降级): 指控增长担忧一解被过快降级——若盈亏平衡主导下行则该解应获更多支持 → 近 1 个月 BEI_10Y -19 个基点(名义 -8、实际 +11)确与该解的盈亏平衡一腿相容, 但 12 个月窗 BEI_10Y -11、TIPS_10Y +102 个基点与其『TIPS 转平』相左; 受审稿裁定『部分相容』与两窗数据一致, 未过快降级。',
    '反方攻击 3(矛盾陈述 C1·政策面): 指控『DFF 回到降息前台阶』掩盖政策取向 → 一年窗内 -25/+25 个基点净变 0, 最新 3.88 与 2025-11-22 锚值 3.88 相同(变动点值 3.89→3.64、3.63→3.88 相差 1 个基点), 表述成立; 仅括注未标观测日(MINOR-2)。',
    '反方攻击 4(矛盾陈述 C2·低维覆盖): 指控相似度低维覆盖被夸大或被隐去 → 覆盖 0.17/0.33/0.5 为引擎 state_vector 原值且受审稿明示; 2025-03 段相似度构成(波动 42.1%、利率 40.7%)亦与引擎面一致。',
    '反方攻击 5(矛盾陈述 C2·自相矛盾): 指控『事后路径分歧明显』与『GOLD_F、SPX 六/十二个月窗符号一致率 1.0』不能并存 → 分歧在股指三个月窗与 DXY, 一致在黄金与股指中长窗, 受审稿两句并列披露, 无隐匿。',
    '反方攻击 6(矛盾陈述 C2·口径): 指控按自然月末口径重算的历史段数字与引擎事后块矛盾 → 逐格两口径差中位约 0.35、最大 1.41 个百分点, 无符号翻转; 受审稿注记『可差约1个百分点』对上界偏低(NIT-4)。',
    '反方攻击 7(矛盾陈述 C3·相邻口径): 指控『政策利率未上调』以相邻口径冒充(7 天逆回购→隔夜逆回购换锚)并依赖过期观测 → 受审稿分列两工具并披露末观测 2026-10-30 与其后缺观测; 一年窗内 199 个 7 天逆回购观测均为 1.4, LPR 3.0 现行至 2026-11-20 且不在 Gate A 名单, 新锚 16 个交易日均为 1.25; 披露属实, 唯 Gate A 缺口披露未入报告(MINOR-3)。',
    '反方攻击 8(矛盾陈述 C3·汇率): 指控以 USDCNY 12 个月 -6.19% 否定汇率/资本流动解释属超出 → 受审稿只称不支持贬值/外流压力读法并保留【尚未验证】, 且自陈三解不可区分, 未超出。',
    '反方攻击 9(机制链 M1·冲击环): 指控油价尖峰为暂时性(2026-06 月末回到 72.92)而通胀此后仍升, 冲击→通胀因果不成立 → 受审稿把支持度限定在预注册窗 2026-02 至 2026-05(月末 72.48→92.05, 首尾 +27.00%)并只用『时序与幅度相容』, 明写能源价格向消费价格的因果传导不可由引擎验证, 未称因果成立。',
    '反方攻击 10(机制链 M1·政策环): 指控『央行因通胀再加速而收紧』与决议前可见数据(通胀已自高点回落)相左 → 受审稿自身已披露(CPI 3.30/3.35 低于 4.17, CORE_PCE 3.00 低于 3.16, HICP 2.9 低于 3.2)并据此把动机环降为 E3【假设】; 唯欧元区 HICP 发布规则双口径未在该处注明(MINOR-1)。',
    '反方攻击 11(机制链 M1·资产环): 指控『实际利率上行→风险资产收缩』不可识别(12 个月窗同向上行) → 受审稿标 E2、写明引擎只有共动事实无因果识别并给出窗口对照; 证伪指标 HY_OAS 在场(3.52, 预警级 3.53, 失效级 4.61)。',
    '反方攻击 12(机制链 M1·阈值): 指控 HY_OAS 预警级阈值 3.53 距最新 3.52 仅 1 个基点、近乎必然触发 → 属阈值松紧的判断选择; 受审稿标明两级阈值与库内依据(2025-05-09 的 3.53、2025-04-07 的 4.61), 可观测, 未把未发生之事写成事实。',
    '反方攻击 13(机制链 M2·同窗反证): 指控套息平仓渠道的同窗预期已被数据否定(USDJPY 156.49→159.35 即 +1.82% 而 SPX -5.51%, 逐日相关 0.19)而受审稿仍列为主解释 → 受审稿在 TR2 裁定主解释的同窗预期未获支持、支持竞争解释; 唯机制链第二环文本只写未来式证伪条件, 未就地写入该形态(NIT-8)。',
    '反方攻击 14(机制链 M2·口径): 指控以月均拆借利率(市场口径)冒充政策目标 → 受审稿明写序列为无担保隔夜拆借月均, 政策决议与目标水平取自冻结日历实录(2026-09-18 决议、2026-09-24 生效、目标 1.25; 2026-10-30 确认维持), 未冒充。',
    '反方攻击 15(机制链 M2·未回撤): 指控『窗内未回撤』被月均序列的微降证伪 → 2026-04、2026-08 各约 0.1 个基点的舍入级变动(0.728→0.727、0.978→0.977), 受审稿已并记; 首次上调月 2025-12 早于美欧通胀同窗回升起点 2026-02。',
    '反方攻击 16(对质环 TR1-1, BRENT_F): 主解释预言同窗显著上行、竞争解释预言大体持平 → 月末 72.48→92.05(2026-03 冲至 118.35), 裁定『支持主解释』与数据一致。',
    '反方攻击 17(对质环 TR1-2, BEI_10Y): 主解释预言收紧前处上行段且高位, 竞争解释预言政策续紧而 BEI_10Y 不升 → 2026-02-27 2.25→2026-05-04 2.50(前者成立), 2026-06-17 起政策续紧而 BEI_10Y 处于 2.15–2.40 区间未升(后者形态亦在) → 『尚不能区分』如实。',
    '反方攻击 18(对质环 TR1-3, BEI_10Y+HY_OAS): 利率主导预言 BEI_10Y 稳定、TIPS_10Y 续升、HY_OAS 不升破高点; 增长主导预言 BEI_10Y 明显下行、TIPS_10Y 转平、HY_OAS 走阔 → BEI_10Y 12 个月 -11、近 1 个月 -19 个基点, TIPS_10Y +102 / +11 个基点, HY_OAS 3.52 未破 3.53, 两侧各有相容观测 → 『尚不能区分』如实。',
    '反方攻击 19(对质环 TR2-1, USDJPY): 主解释预言风险资产收缩与日元走强同现 → 同窗 USDJPY +1.82% 而 SPX -5.51% → 裁定『支持竞争解释』与区分指标面一致。',
    '反方攻击 20(情景 SCN1/SCN2): 指控阈值系为免于被证伪而设 → 阈值均为数字、指标在场、期限 2027-02-28 早于所涉观测的规则发布日; 截止日读数(CPI 3.72、CORE_PCE 3.12、BEI_10Y 2.15)均在未证伪一侧, 触发所涉 2026-11/12 观测尚未发布; 可观测。',
]

# ====================== Part D1: 问题清单(自快照直算的补充事实先立于文字) ============================
items = []


def add(sev, where, note, original='', fix=''):
    it = collections.OrderedDict([('severity', sev), ('where', where), ('note', note), ('original', original), ('fix', fix)])
    items.append(it)
    return it


# ---- 补充事实(全部自冻结快照/日历/引擎面直算; 文字中的每个数字由这些值或台账给出) ----
reg = load(os.path.join(R, 'root_overlay', 'config', 'metric_registry.json'))
REG_TXT = json.dumps(reg, ensure_ascii=False)
need('次月中旬终值' in REG_TXT and '保守' in REG_TXT, '注册表未见 HICP 保守口径注记')
ENTS = cal.get('entries') or []
PEND = [e for e in ENTS if e.get('decision_date') and e.get('effective_date')
        and e['decision_date'] <= '2026-11-23' < e['effective_date']]
HICP_CAL = [e for e in ENTS if 'EA_HICP_YOY' in (e.get('metric_ids') or [e.get('metric_id')])]
BEI_S = [t for t in F.series('BEI_10Y') if t[1] is not None]
BEI_LAST_D, BEI_LAST_V = BEI_S[-1]
BEI_LT = [(d, v) for d, v in BEI_S if v < 1.8][-1]
GAP_HI_BP = int(round((BEI_LAST_V - 1.8) * 100))
GAP_LO_BP = int(round((BEI_LAST_V - BEI_LT[1]) * 100))
need(BEI_LAST_D == '2026-11-20' and round(BEI_LAST_V, 2) == 2.15 and BEI_LT[0] == '2020-11-30'
     and round(BEI_LT[1], 2) == 1.77 and GAP_HI_BP == 35 and GAP_LO_BP == 38, 'BEI_10Y 情景阈值间距不符: %s' % str((BEI_LAST_D, BEI_LAST_V, BEI_LT)))
SCTXT = json.dumps(sc, ensure_ascii=False)
need(all(re.search(r'(?<![0-9.])' + re.escape(t) + r'(?![0-9])', SCTXT) for t in ('2.5', '2.8', '1.8', '2027-02-28')), '情景文本未含阈值/期限词元')
DFF_S = [t for t in F.series('DFF') if t[1] is not None]
DFFCP = [(DFF_S[i - 1][0], DFF_S[i - 1][1], DFF_S[i][0], DFF_S[i][1]) for i in range(1, len(DFF_S))
         if DFF_S[i][0] >= '2025-11-19' and abs(DFF_S[i][1] - DFF_S[i - 1][1]) > 0.2]
DFF_AN = [F.at_or_before('DFF', d) for d in ('2025-11-22', '2026-08-22', '2026-11-19')]
need(len(DFFCP) == 2 and [round(x[3], 2) for x in DFFCP] == [3.64, 3.88] and [round(x[1], 2) for x in DFFCP] == [3.89, 3.63]
     and [round(x[1], 2) for x in DFF_AN] == [3.88, 3.63, 3.88] and DFF_AN[0][0] == '2025-11-22' and DFF_AN[1][0] == '2026-08-22'
     and DFF_AN[2][0] == '2026-11-19', 'DFF 锚值/变动点不符: %s %s' % (DFFCP, DFF_AN))
OMO_GAP = L.days('2026-10-30', '2026-11-23')
need(OMO_GAP == 24, '7 天逆回购末观测距截止日天数不符')
need(all(round(JPC[k], 2) == v for k, v in (('2026-02', 1.27), ('2026-03', 1.46), ('2026-04', 1.38), ('2026-05', 1.53), ('2026-09', 2.16))), '日本 CPI 路径不符')
need(PP_MIN_ALL == (-8.22, '2009-07'), 'CN_PPI 全史低点不符')
CV = ((rep.get('agent_judgment') or {}).get('contract_verification') or {})
VS, SC_, MC = CV.get('verdicts') or [], CV.get('six_checks') or [], CV.get('map_checks') or []
NONV = [v for v in VS if str(v.get('status')).upper() != 'VERIFIED']
SIXF = [v for v in SC_ if str(v.get('status')).upper() not in ('PASS', 'OK', 'VERIFIED')]
MAPF = [v for v in MC if str(v.get('status')).upper() not in ('PASS', 'OK', 'VERIFIED')]
need(CV.get('verdict') == 'VERIFIED' and not NONV and not SIXF and not MAPF and not (CV.get('unresolved_unbound') or []),
     '契约验证存在非 VERIFIED 项: %s' % str((CV.get('verdict'), len(NONV), len(SIXF), len(MAPF))))
TURN = aj['reader_map'].get('turnings') or []
HIST = aj['reader_map'].get('history_periods') or []
need(len(TURN) == 3 and len(HIST) == 3, '转折/历史段条数不符')

# ---- MINOR ----
o1a = O('欧央行 2026-09-10 决议前最近可见 HICP 为 2026-07 观测 2.9，自 2026-06 的 2.8 回升、低于 2026-05 高点 3.2', '(MINOR-1 甲)')
v9 = VIS['2026-09-10']
note1a = ('MINOR-1(甲) 口径未并列: 引擎内欧元区 HICP 发布规则有双口径。注册表保守口径(终值=观测月末+16 天)下, 决议时点(回推 2026-09-10【推断】)前最近可见为 %s 观测 %s(规则发布日 %s), 2026-08 观测 %s 推定发布 %s、决议时点尚未可见——受审句数值全部成立。'
          '但引擎历史面与受审稿自身历史段使用两级口径(快报=观测月末当日可见): 据此 2026-08 观测的快报已于 %s 可见, 序列该月值 %s 持平 2026-05 高点 %s, 「决议前可见读数低于高点」对欧央行一腿在此口径下不成立(当时快报值不可回溯, 属【推断】)。'
          '该环已标 E3【假设】并自述动机不可验证, 结论方向(动机环证据减弱)不变, 故计 MINOR、不计 MAJOR。出处: research_snapshot_20261123.json series_store.EA_HICP_YOY(2026-05 %s / 2026-06 %s / 2026-07 %s / 2026-08 %s); '
          'root_overlay/config/metric_registry.json(metric EA_HICP_YOY release_semantics: 次月中旬终值、保守标注); root_overlay/config/release_calendar.json 内 EA_HICP_YOY 条目 %d 条; 台账 %s。') % (
    v9['obs_date'][:7], v9['value'], v9['pub_date'], HICP.get('2026-08'), REL08[0], ME08, HICP.get('2026-08'), HICP.get('2026-05'),
    HICP.get('2026-05'), HICP.get('2026-06'), HICP.get('2026-07'), HICP.get('2026-08'), len(HICP_CAL), C('hicp_rule'))
fix1a = ('欧央行 2026-09-10 决议前最近可见 HICP: 按注册表保守口径(终值=观测月末+16 天)为 2026-07 观测 2.9，自 2026-06 的 2.8 回升、低于 2026-05 高点 3.2；'
         '按引擎历史面两级口径(快报=观测月末当日可见，推定)则 2026-08 观测的快报已于 2026-08-31 可见、其月值为 3.2 持平 2026-05 高点(当时快报值不可回溯)——'
         '「决议前可见读数低于高点」对美联储成立，对欧央行仅在前一口径下成立')
add('MINOR', W(o1a), note1a, o1a, fix1a)

o1b = O('且决议时点前已可见的美国 CPI 与核心 PCE 同比、以及欧元区 HICP 均低于各自 2026-05 高点(见观察事实)，对美联储决议与欧央行第二次决议的动机环证据减弱', '(MINOR-1 乙)')
add('MINOR', W(o1b), 'MINOR-1(乙) 与甲同源: 「欧元区 HICP 低于 2026-05 高点」只在注册表保守发布口径下成立(2026-07 观测 2.9、规则发布 2026-08-16); 引擎历史面两级口径下 2026-08 观测(月值 3.2)已于 2026-08-31 可见、持平高点。'
    '该环为 E3【假设】且本句以「证据减弱」措辞自限, 结论不变, 计 MINOR。出处: series_store.EA_HICP_YOY; 台账 ' + C('hicp_rule') + '。', o1b,
    '且决议时点前已可见的美国 CPI 与核心 PCE 同比均低于各自 2026-05 高点，欧元区 HICP 按注册表保守口径亦低于 2026-05 高点(按引擎历史面两级口径则 2026-08 观测已可见、持平高点)(见观察事实)，'
    '对美联储决议的动机环证据减弱，对欧央行第二次决议的同类证据减弱仅在前一口径下成立')

o2 = O('(DFF 3.88→3.63→3.88)', '(MINOR-2)')
cp_txt = '、'.join('%s 的 %s(前值 %s 的 %s)' % (x[2], round(x[3], 2), x[0], round(x[1], 2)) for x in DFFCP)
add('MINOR', W(o2), ('MINOR-2: 括注三值是三时点面板锚值(观测 %s / %s / %s), 未标观测日; 实际变动点为 %s(各与括注值相差 1 个基点, 属日频有效利率逐日波动); '
                     '步长 -25/+25 个基点与窗内净变 0 成立, 结论不变。出处: series_store.DFF; report.json research_plan 三时点面板; 台账 %s、%s。') % (
    DFF_AN[0][0], DFF_AN[1][0], DFF_AN[2][0], cp_txt, C('dff_panel'), C('dff_anchors')), o2,
    '(DFF 三时点锚值 3.88→3.63→3.88，观测 2025-11-22 / 2026-08-22 / 2026-11-19；变动点 2025-12-11 自 3.89 降至 3.64、2026-09-17 自 3.63 升至 3.88，步长 -25 / +25 个基点)')

usedm_txt = '、'.join(USED_M)
usedd_txt = '、'.join(USED_D)
fix3 = HEAD + ('〔口径加注: 7天逆回购利率与隔夜逆回购利率均为 Gate A 非核心缺口指标, 本句按序列库存量观测引用(7天逆回购一年窗内 199 个观测均为 1.4、末观测 2026-10-30; 隔夜逆回购 2026-11-02 起 16 个交易日均为 1.25); '
               'LPR 3.0 现行至 2026-11-20、不在 Gate A 名单)〕; 并把 quality_gate_notes 六条渲染入 MAP_REPORT.md 读者面')
q1 = O('缺口指标中有五项在序列库内仍有存量观测并被本档按存量观测引用', '(MINOR-3)')
WQ, WG = W(q1), W('缺席/降级数据不得进入研究结论')
add('MINOR', W(HEAD) + '; ' + WG,
    ('MINOR-3 披露位置: 首页结论与 C3 按存量观测引用 Gate A 非核心缺口指标(%s), 判断档另引用非核心降级指标(%s)。逐项口径只存于 agent_judgment.json quality_gate_notes[%s](Gate A) 与 [%s](存量观测), 六条质量注记在三份报告中逐字渲染 0 条(台账 #860); '
     '读者报告侧只有两处概括: C1 陈述内的「%s」(%s)与 MAP_REPORT 数据门行「缺席/降级数据不得进入研究结论」(%s); MAP_REPORT 首页句与传导链在使用处不带缺口标记, 与数据门行的表述未对齐。'
     '经序列级核实披露内容属实、不属于把缺席写成无变化: 7 天逆回购一年窗内 199 个观测均为 1.4(末观测 2026-10-30), LPR 3.0 现行至 2026-11-20 且不在 Gate A 名单, 隔夜逆回购 2026-11-02 起 16 个交易日均为 1.25(台账 %s、%s、%s、%s)。') % (
        usedm_txt, usedd_txt or '无', '、'.join(str(i) for i in IDX_GATE), '、'.join(str(i) for i in IDX_STOCK), q1, WQ, WG, C('gate_a'), C('omo_win'), C('lpr'), C('overnight')),
    HEAD, fix3)

# ---- NIT ----
def nit(orig, note, fix=''):
    o = O(orig, '(NIT)')
    add('NIT', W(o), note, o, fix)


nit('全国口径的回升起点(2026-03)',
    'NIT-1 措辞: 日本 CPI 同比 2026-02 为 1.27(窗内低点)→2026-03 升至 1.46, 2026-04 回落至 1.38, 自 2026-05(1.53)起逐月回升至 2026-09 的 2.16; 「回升起点」指低点后首月, 因 2026-04 回落一词有歧义。出处: series_store.JP_CPI_YOY; 台账 ' + C('jpcpi_high') + '、' + C('turn0_jump') + '、' + C('tokyo') + '。',
    '全国口径自 2026-03 起自低点回升(2026-04 小幅回落后自 2026-05 起连续回升)')
nit('中国 PPI 低点在 2025-11',
    'NIT-2 限定词: -2.2 为本轮 12 个月窗内低点; 序列全史低点为 %s@%s, 2023 年以来低点为 %s@%s。出处: series_store.CN_PPI_YOY; 台账 ' % (PP_MIN_ALL[0], PP_MIN_ALL[1], PP_MIN_23[0], PP_MIN_23[1]) + C('cn_ppi') + '。',
    '中国 PPI 本轮窗内低点在 2025-11')
nit('对质表判断记『支持竞争解释』',
    'NIT-3 语气: 同窗美元兑日元 +1.82%(156.49→159.35)对标普500指数 -5.51% 方向相反, 但逐日面相关系数 0.19(21 个交易日、同向 16 日)只属弱同向耦合; 受审稿已附「竞争解释的字面预期未获完全确认」, 判断与数据一致。出处: series_store.USDJPY、SPX; 台账 ' + C('usdjpy_daily') + '。',
    '对质表判断记『主解释同窗预期未获支持, 倾向竞争解释(逐日面仅弱耦合)』')
nit('两口径数值可差约1个百分点',
    'NIT-4 精度: 两口径逐格差中位约 0.35 个百分点、最大 1.41 个百分点(2023-10 段标普500指数十二个月窗), 无符号翻转; 「约1个百分点」对上界略偏低。出处: series_store 四项资产月末序列与 report.json 相似检索面; 台账 ' + C('basis_diff') + '。',
    '两口径数值可差约 0.35 个百分点(中位)、最大约 1.41 个百分点, 无符号翻转')
nit('若如此,BRENT_F 应大体平稳而 CORE_CPI/CORE_PCE 独立走高',
    'NIT-5 竞争预言只在基数效应或供给因素主导的情形下才有约束力: 需求过热情形下油价与核心通胀可同涨, 该预言对其偏弱; 受审稿已自述核心通胀同窗上行不构成区分观测, 裁定为「尚不能区分」未受影响。出处: series_store.BRENT_F、CORE_CPI; 台账 ' + C('brent') + '、' + C('core_cpi') + '。',
    '若如此,BRENT_F 应大体平稳而 CORE_CPI/CORE_PCE 独立走高(需求过热情形下油价与核心通胀亦可同涨, 须另以需求侧指标区分)')
nit('逐项见质量注记',
    'NIT-6 悬空指引: 所指 quality_gate_notes 六条在三份报告中逐字渲染 0 条(台账 #860); 该句渲染于 %s, 读者按指引找不到逐项口径; 与 MINOR-3 同源。' % WQ,
    '逐项见 MAP_REPORT 数据门行与本档 quality_gate_notes(建议渲染入读者报告)')
nit('NIKKEI225 止于 2026-11-20 收盘',
    'NIT-7 原因未写: 属实——2026-11-23 该序列无观测(2016–2023 年中 11 月 23 日为交易日的 7 年当日均无该序列观测; 同日上证指数、DAX 有观测), 属每年重复出现的非观测日而非采集滞后。台账 ' + C('nikkei_1123') + '。',
    'NIKKEI225 止于 2026-11-20 收盘(2026-11-23 该序列无观测, 为每年重复出现的非观测日, 非采集滞后)')
nit('证伪指标=USDJPY',
    'NIT-8 就地引述缺位: 机制链第二环只写未来式证伪条件, 未就地写入近窗对质(同窗美元兑日元 +1.82% 对标普500指数 -5.51%, 主解释同窗预期未获支持); 该对质已在传导链 TR2 完成并披露, 无隐匿。台账 ' + C('usdjpy_daily') + '。',
    '证伪指标=USDJPY(近窗首次对质见传导链 TR2: 同窗美元兑日元 +1.82% 对标普500指数 -5.51%, 主解释同窗预期未获支持); 若风险资产再次收缩而 USDJPY 未同步走低/日元未走强,套息平仓渠道的分量应被下调')
nit('冻结发布日历无美联储与欧央行实录条目',
    'NIT-9 范围词: 冻结日历 %d 条中有数据发布条目(美国 11 条、HICP 3 条、LPR 2 条), 缺的是美联储与欧央行政策决议实录而非全部实录。出处: release_calendar.json entries; 台账 ' % len(ENTS) + C('pol_entries') + '。',
    '冻结发布日历无美联储与欧央行政策决议实录条目(其决议日按生效日惯例回推【推断】)')
nit('四地证据面呈现『通胀再加速→政策再收紧→实际利率上行→风险资产收缩』的同向共动',
    'NIT-10 首页句缺限定词: 政策再收紧只适用于美欧日(中国未跟进加息), 风险资产收缩只在近月窗成立(12 个月窗股指与实际利率同向上行); 受审稿在同句括注与机制链资产环已逐项限定, 结论不变。台账 ' + C('assets12') + '、' + C('near_assets') + '。',
    '美欧日三地证据面呈现『通胀再加速→政策再收紧→实际利率上行』的同向共动, 近月窗口内叠加风险资产收缩(中国未跟进加息)')
nit('历史段事后数字取自相似检索面事后块，按自然月末口径',
    'NIT-11 口径说明可更明确: 引擎相似检索面事后块为锚后首个观测口径, 受审稿数字按自然月末口径; 两口径差中位约 0.35、最大 1.41 个百分点, 无符号翻转。台账 ' + C('basis_diff') + '、' + C('c2') + '。',
    '历史段事后数字按自然月末口径自冻结序列重算(引擎相似检索面事后块为锚后首个观测口径; 两口径差中位约 0.35 个百分点、最大 1.41 个百分点, 无符号翻转)')

nmaj = sum(1 for it in items if it['severity'] == 'MAJOR')
nmin = sum(1 for it in items if it['severity'] == 'MINOR')
nnit = sum(1 for it in items if it['severity'] == 'NIT')
need(nmin == 4 and nnit == 11, '问题清单条数与预案不符: MAJOR %d / MINOR %d / NIT %d' % (nmaj, nmin, nnit))

# ====================== Part D2: 覆盖面、组装与输出 ============================
def SX(sub):
    secs = list(collections.OrderedDict.fromkeys(str(r.get('section', '')) for r in recs))
    names = [s for s in secs if s == sub] or [s for s in secs if sub in s]
    ids = [r['_i'] for r in recs if str(r.get('section', '')) in names]
    need(len(ids) > 0, '台账分节未找到: ' + sub)
    return '『' + '/'.join(names) + '』' + str(len(ids)) + ' 条(' + comp(ids) + ')'


def hlabel(h):
    for k in ('period', 'anchor', 'anchor_month', 'id', 'label', 'name', 'title', 'turning', 'turn'):
        if isinstance(h, dict) and k in h:
            return str(h[k])[:26]
    return '?'


GAC = str(GA.get('status'))
FV = [str(lk.get('face_off_verdict'))[:40] for lk in (tr1.get('links') or []) + (tr2.get('links') or [])]
HP = [str(h.get('anchor_ym') or '?') for h in HIST]
TP = ['%s@%s' % (t.get('metric_id'), t.get('date')) for t in TURN]
need(all('?' not in x for x in HP + TP), '转折/历史段标签缺失: %s %s' % (TP, HP))
N22 = list(recs[863]['computed']) if len(recs) > 863 and isinstance(recs[863].get('computed'), list) else []
N48 = sec_count.get('②/⑬FULL_REPORT-L1事实表', [0, 0, 0])[0]
need(N22 == [22, 22] and N48 == 48, '三时点表/事实表计数不符: %s %s' % (N22, N48))
RA = str(snap.get('research_as_of'))
COV = [
    ('①', '截止日: 受审稿自称研究截止日 2026-11-23 与快照 research_as_of(%s)/target_date(%s)一致; 受审稿所引观测日、规则发布日、决议日、生效日均不晚于截止日; 冻结日历内无「决议日≤截止日而生效日>截止日」的待生效决定(%d 条); '
           '历史类比的事后段均以「事后」身份标注、未被写成预测; 时点标注(盘中快照/收盘/末观测日/时区)与快照时间戳相容。台账 %s、%s。' % (RA, snap.get('target_date'), len(PEND), SX('①'), C('time_marks'))),
    ('②', '点值锚格: 工单四地×维度×三锚(12 个月前 / 3 个月前 / 最新)中被引用的格逐格自 series_store 直算(值 / 观测日 / 同比 / 缺席理由)并与 report.json 引擎点值格比对, 全部一致; 缺席格如实标缺席。台账 %s。' % SX('②')),
    ('③', '同比: 凡称「同比」的月频数值均以去年同月为基期自水平序列直算(季度以同季为基期); 2026-10 美国 CPI 同比因 2025-10 基期缺席不可得, 受审稿如实标「缺基期不可得」而未以相邻月份替代; 「最近有效同比」的月份与数值一致。台账 %s、%s。' % (SX('③'), C('cpi_path'))),
    ('④', '政策面: 决议日 / 生效日 / 步长 / 目标值逐项与冻结日历条目和序列变更日核对; 官方目标(冻结日历所载日本央行目标水平)、政策利率序列(DFF、ECB_DFR、CN_LPR_1Y)与月均值(JP_POLICY_RATE 无担保隔夜拆借月均)各口径分列、未互相冒充; 无待生效决定; 中国换锚(7 天逆回购→隔夜逆回购)分列。台账 %s、%s、%s。' % (SX('④'), C('dec_dates'), C('panel_conv'))),
    ('⑤', '三利率分解与资产月窗: 12 个月窗名义 +91 = 实际 +102 + 盈亏平衡 -11 个基点, 恒等残差 0; 近 1 个月 -8 = +11 - 19; 窗口端点日期(2025-11-19 / 2026-11-19 共同交易日; 2026-10-23 至 2026-11-19、11-20、11-23)与端点值逐一直算; 资产月窗(同日收盘口径与近 1 个月口径)逐项一致。台账 %s、%s、%s。' % (C('decomp'), C('asset_win'), C('rates_12m'))),
    ('⑥', '转折判断与候选面: 三个转折(%s)的前值→后值 / 窗口 / 谁先变与引擎转折候选面及排序一致; 「先后」主张均有时间分辨率支撑(美联储 2026-09-16 决议、欧央行回推 2026-09-10【推断】、日本央行 2026-09-18 决议; 通胀转折月至 2026-05)。台账 %s、%s、%s。' % ('、'.join(TP), SX('⑥'), C('cand_rank'), C('turn1'))),
    ('⑦', '传导链各环: 两条机制链 4+2 环的 evidence_level 标注(E1/E2/E3)与该环实际证据相称; E2/E3 环均含字面「假设」、未以事实位措辞出现; 环内数字可回贴引擎面; 读者面传导链 3+1 环以【假设】【竞争解释】字面区分事实与假设。台账 %s。' % SX('⑦')),
    ('⑧', '历史类比: 三段(%s)的距离 / 分位 / 维度构成、当时可知面与事后段的划分、随后 3 / 6 / 12 个月事后结果数字逐窗自冻结序列直算; 事后结果均以「事后」措辞呈现, 未被表述成预测; 同步面逐格一致。台账 %s、%s、%s。' % ('、'.join(HP), SX('⑧'), C('c2'), C('sign_agree'))),
    ('⑨', '情景: 两情景互为对照、方向互补; 触发条件 / 证伪阈值均为数字且指标在场; 与截止日读数相容(CPI 3.72、CORE_PCE 3.12、BEI_10Y 2.15 均在未证伪一侧), 无已触发或已被证伪而仍列为待验证的前提; 期限 2027-02-28。台账 %s。' % SX('⑨')),
    ('⑩', '总判断 / 走位 / 对质表: 首页结论、四地走位、对质表四行的方向词 / 单位 / 精度 / 关系词与数值一致; 对质表四行裁定(%s)与该行观测一致(见 5.6)。台账 %s、%s。' % ('、'.join(FV), SX('⑩'), C('dist_metrics'))),
    ('⑪', '诚实缺席项: 受审稿声明的每个缺口(序列缺席 / 缺基期 / 过期 / 降级)经序列级证实属实, 无以相邻口径冒充; Gate A=%s(核心缺口 %d、非核心缺口 %d、非核心降级 %d)与快照 gate_a 一致, MAP 数据门行逐项一致。台账 %s、%s。' % (
        GAC, len(GA.get('core_missing') or []), len(GA.get('noncore_missing') or []), len(GA.get('noncore_degraded') or []), SX('⑪'), C('gaps'))),
    ('⑫', '截止日当日标注的日频观测: 2026-11-23 的 SPX、USDJPY、GOLD_F、DXY、VIX 标为盘中快照, SHCOMP 标为当日收盘, 与快照 research_as_of(%s)相容; NIKKEI225 止于 2026-11-20 属实。台账 %s。' % (RA, SX('⑫'))),
    ('⑬', '契约验证结果: report.json agent_judgment.contract_verification verdict=%s; 逐项 verdicts %d 项%s, six_checks %d 项、map_checks %d 项全部通过, unresolved_unbound %d 项 → 无非 VERIFIED 项(含 STALE), 无需判断档另作披露。' % (
        CV.get('verdict'), len(VS), '' if not NONV else '(非 VERIFIED %d 项)' % len(NONV), len(SC_), len(MC), len(CV.get('unresolved_unbound') or []))),
    ('⑭', '交付门相关缺口: 判断档对 Gate A 非核心缺口 %d 项 / 非核心降级 %d 项的披露与快照 gate_a 逐项一致; 其中 %d 项在序列库内有存量观测, 受审稿所列与序列面一致; 无把缺席写成「无变化」(见 MINOR-3 的序列级核实), 无把序列值写成官方宣布目标(中国两工具与日本月均拆借利率均标口径); 缺官方记录处(美联储 / 欧央行决议)以【推断】标注。缺口披露未入读者报告记 MINOR-3。台账 %s。' % (
        len(GA.get('noncore_missing') or []), len(GA.get('noncore_degraded') or []), len([r_ for r_ in GM if r_[1] > 0]), C('gate_a'))),
    ('⑮', '地图问句三时点对照与工单四问: MAP 三时点对照表(%d 行)各格(值 / 观测日 / 状态)与引擎点值格(%d 格)逐格直算一致, FULL_REPORT L1 事实表 %d 项一致; 工单四问——三个转折(turnings %d 条)、谁先变 / 跟进或背离(转折候选面与政策面)、证据最充分的传导机制 / 其他解释 / 区分指标(mechanism_chains %d 条, 每环并列竞争解释与证伪指标)、'
           '历史上结构最像的时期 / 当时其他经济体是否同步 / 随后 3、6、12 个月实际走势(history_periods %d 条)——各有对应内容且与工单相称。台账 %s、%s、#863。' % (N22[0], N22[1], N48, len(TURN), len(aj['l3']['mechanism_chains']), len(HIST), SX('②'), SX('⑩'))),
]

ENGOBS = ['台账 #%d: %s｜%s' % (i, str(recs[i].get('src'))[:170], str(recs[i].get('note'))[:320]) for i in (670, 861, 932) if i < len(recs)]
PROC = [
    '全部复算由本席亲自完成, 未委派子代理; 全部脚本以 /usr/bin/python3 -I 运行, 路径作参数传入, 解释器不在数据目录内启动; 只读规程第 1 节列明的只读面, 未读取第 2 节禁止路径, 未联网, 未运行任何写操作命令。',
    '席位侧自纠(均不改变任何比对结论, 台账与脚本同步留痕): (a) 早期对 MAP 报告表格的即席核对出现 5 个旗标, 经复查均为席位自身解析伪影(列错位/全半角), 已消除; (b) rc12 一条记录的 note 模板写错, 已更正; (c) 清理 10 条完全重复的台账记录; (d) rc15 两处过严判据更正(#923 日历关键词计数、#930「2026-03 同月大幅跳升」判据); '
    '(e) rc16 对 3 条中国 7 天逆回购锚值记录(#450–#452)的 reported 字面与 1 条空 where(#879)作描述性勘误, 勘误前备份 points.jsonl.bak-pre-rc16; (f) rc08 脚本第 192 行与上述口径对齐; (g) 复核中途一次接口速率限制(HTTP 429)中断, 续算前复核受审版本(代码印章、MAP_REPORT sha256、快照 sha256、受审文件修改时间)与中断前一致; '
    '(h) 产出草稿阶段剔除了本席预列的一条行文项(情景触发句「自 2026-11 观测月起连续两个月回落」在受审稿同句括注内已自带缺基期说明, 经复核不成立), 未列入问题清单。',
    '数字全量清扫(中间结果 mid_rc14_out.txt / mid_rc14b_out.txt): %s; 第二遍 %s 行, 未直接命中的仅为日期分量、「3个月前」类时点标签、指数名「标普500」与已核值在别处的重复出现。',
]

P = []


def T(s=''):
    P.append(s + '\n')


def cell(x, n):
    s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)
    s = s.replace('\r', ' ').replace('\n', ' ').replace('|', '\\|')
    return (s[:n] + '…') if len(s) > n else s


VERD_WORD = 'UPHELD' if (nmaj == 0 and NF == 0) else 'REVISE'
NOW_DAY = '2026-11-24'
NOTES = ('抽核命中 %d 点 / 偏离 %d 点(另登记 NA %d 条: 受审稿无对应数字或属参数/口径登记项), 逐点自冻结快照 series_store、冻结日历与 report.json 引擎面直算后比对; MAJOR 0 条、MINOR %d 条(三类: 欧元区 HICP 发布规则双口径未并列 / DFF 括注三值未标观测日 / Gate A 缺口口径披露只在判断档质量注记而未入读者报告)、NIT %d 条。'
         '受审稿的数字、日期、方向逐点一致: 政策时序(美联储 2025-12-11 生效 -25 个基点、2026-09-17 生效 +25 个基点; 欧央行生效 2026-06-17、2026-09-16 各 +25 个基点; 日本央行 2026-09-18 决议、09-24 生效)、利率分解(12 个月名义 +91 = 实际 +102 + 盈亏平衡 -11 个基点)、近月资产窗、历史类比事后窗与同步面、情景阈值与期限均复核一致; '
         '契约验证 VERIFIED %d/%d、无非 VERIFIED 项; 历史段同步性叙述与引擎同步面逐格一致; 反方攻击 %d 条均未推翻受审结论, 最重一项为 MINOR-1。裁决 %s。') % (
    NT, NF, len(NA), nmin, nnit, len(VS) - len(NONV), len(VS), len(CA), VERD_WORD)

T('# Audit-R32 独立语义审查 · A 席 Round-1 · 复算清单 / 六查 / 反方攻击 / 问题清单')
T('')
T('- 席位: independent-zero-context-seat-r32-a-round1(语义审查席, 零上下文, 未委派子代理)')
T('- 审查日: %s; 受审代码印章: %s' % (NOW_DAY, STAMP))
T('- 裁决: **%s**(MAJOR %d 条; MINOR %d 条; NIT %d 条)' % (VERD_WORD, nmaj, nmin, nnit))
T('- 复算点: 比对 %d 点, 偏离 %d 点, 另有登记项(NA) %d 条; 台账记录共 %d 条(points.jsonl)' % (NT, NF, len(NA), len(recs)))
T('- 产出: PROSE-round1.md、VERDICT-round1.json(全部复核完成后一次性写出, 写出后不改写)')
T('')
T('## 0 受审对象与版本核对')
T('')
T('- 受审运行目录: %s' % os.path.basename(R))
T('- 工单原文(逐字): %s' % Q)
T('- 受审对象: agent_judgment.json 全文(schema_version %s; l3 矛盾陈述 %d 条、机制链 %d 条(环数 %s); l4 情景 %d 条; reader_map 键: %s; quality_gate_notes %d 条)与 MAP_REPORT.md / FULL_REPORT.md / report.md 中的判断文字。' % (
    aj.get('schema_version'), len(aj['l3']['contradictions']), len(aj['l3']['mechanism_chains']), '+'.join(str(len(m.get('links') or [])) for m in aj['l3']['mechanism_chains']),
    len(sc), '、'.join(aj['reader_map'].keys()), len(qgn)))
T('- 代码印章(report.json run.git_head): %s; MAP_REPORT.md sha256: %s(与 MAP_REPORT.sha256 一致); 冻结快照 sha256 前缀 %s(安装树副本与运行目录 overlay 副本逐字节一致); 冻结日历 version %s、entries %d 条。' % (STAMP, map_sha, snap_sha[:16], (cal.get('version') or cal.get('calendar_version')), len(ENTS)))
T('- 受审文件修改时间(均早于席位首文件 %s):' % mt(os.path.join(D, '_protocol.md')))
T('')
T('| 文件 | 修改时间 |')
T('|---|---|')
for nm_, t_ in aud_mt:
    T('| %s | %s |' % (nm_, t_))
T('')
T('- 复核中途一次接口速率限制中断; 续算前复核上述印章、sha256 与修改时间均与中断前一致。')
T('- 本席未读取任何预审内容或其他席产出; 运行目录三份报告中的「语义审查(席位待唤起)」(%d / %d / %d 处)与「独立语义审查待裁」(%d / %d / %d 处)为规程所述的预期文字。' % (
    MAP.count('席位待唤起'), FULL.count('席位待唤起'), REP.count('席位待唤起'), MAP.count('语义审查待裁'), FULL.count('语义审查待裁'), REP.count('语义审查待裁')))
T('- BUND_10Y / BUND_2Y 在判断档中只出现于 quality_gate_notes(序列库无此二序列), 未进入任何结论句。')
T('')
T('## 1 方法与判读规则')
T('')
NSS = len(snap.get('series_store') or {})
need(NSS == 92, 'series_store 序列数不为 92')
T('- 只读面: 冻结快照 series_store(%d 序列)/facts/gate_a、冻结日历、注册表、report.json 引擎面(点值格、三时点面板、相似检索面、契约验证)与受审文本; 全部数值由自写脚本直算后与受审稿文字比对。' % NSS)
T('- 判读: 显示精度取半单位容差; 「约」按正负 50% 以内判读; 发布日以冻结日历条目优先、其次注册表/引擎规则(CPI 13 天、CORE_PCE 30 天、EA_HICP_YOY 16 天、JP_CPI_YOY 20 天等), 欧元区 HICP 另按引擎历史面两级口径对照(见 MINOR-1); 月末取自然月末; 决议日惯例: 美联储=生效日前一日, 欧央行=生效日前上一个周四(【推断】), 日本央行 / 中国=当日。')
T('- 台账 points.jsonl 每行一点(字段: section / src=出处键 / computed=直算值 / reported=报告值 / ok / note / where), 行号从 0 起计, 本文件以 #行号 引用; ok=True 计入比对点, ok=NA 为登记项(不计入比对点), ok=False 为偏离。')
T('- 席位脚本(同目录, 供操作席复核): %s。' % '、'.join(sorted(f for f in os.listdir(D) if f.endswith('.py'))))
T('- 脚本运行方式: cd /tmp && /usr/bin/python3 -I <脚本> <路径参数…>; 本文件与 JSON 由 rc20_gen_outputs.py 一次性生成(draft 模式只写 mid_rc20_* 草稿并自检, write 模式在零问题且两件产出尚不存在时写出)。')
T('')
T('## 2 复算清单(逐点: 出处键 / 直算值 / 报告值 / 一致与否)')
T('')
T('| 分节 | 记录 | 一致 | NA |')
T('|---|---|---|---|')
for s_, c_ in sec_count.items():
    T('| %s | %d | %d | %d |' % (cell(s_, 90), c_[0], c_[1], c_[2]))
T('')
k = 0
for s_, c_ in sec_count.items():
    k += 1
    T('### 2.%d %s(记录 %d / 一致 %d / NA %d)' % (k, s_, c_[0], c_[1], c_[2]))
    T('')
    T('| # | 分节 | 出处键(src) | 直算值(computed) | 报告值(reported) | 判定 | 位置(where) |')
    T('|---|---|---|---|---|---|---|')
    for r_ in recs:
        if str(r_.get('section', '')) != s_:
            continue
        T('| #%d | %s | %s | %s | %s | %s | %s |' % (r_['_i'], cell(str(r_.get('section', '')), 30), cell(str(r_.get('src', '')), 200), cell(r_.get('computed'), 240),
                                                 cell(r_.get('reported'), 240), OKM.get(r_['ok'], str(r_['ok'])), cell(str(r_.get('where', '')), 160)))
    T('')
    if k % 6 == 0:
        pass
T('## 3 登记项(NA, 不计入比对点; 共 %d 条)' % len(NA))
T('')
for r_ in NA:
    T('- #%d [%s] 出处键: %s; 直算: %s; 受审稿: %s; 说明: %s; 位置: %s' % (
        r_['_i'], r_.get('section'), cell(str(r_.get('src')), 220), cell(r_.get('computed'), 200), cell(r_.get('reported'), 200),
        cell(str(r_.get('note')), 420), cell(str(r_.get('where')), 200)))
T('')
T('## 4 规程第 3 节覆盖面 ①–⑮ 逐项结论')
T('')
T('(规程第 3 节末项在原文中重复编号为⑬, 本文件按顺序记为⑮。)最低要求 120 点, 实际比对 %d 点。' % NT)
T('')
for lab, txt in COV:
    T('- **%s** %s' % (lab, txt))
T('')
T('Gate A 缺口 / 降级指标与判断档引用情况(序列级; 「提及」= 判断档 l3/l4/reader_map 正文出现该指标代码或别名):')
T('')
T('| 指标 | Gate A 类别 | 序列库观测数 | 末观测日 | 判断档正文提及 |')
T('|---|---|---|---|---|')
for cls, rows in (('非核心缺口', GM), ('非核心降级', GD)):
    for m_, n_, last_, hit_ in rows:
        T('| %s | %s | %d | %s | %s |' % (m_, cls, n_, last_, hit_))
T('')
T('')
T(''.join(SIX))
T('### 5.8 反方攻击记录(与 VERDICT JSON 的 counterexamples_sought 逐条对应)')
T('')
for i, c_ in enumerate(CA):
    T('%d. %s' % (i + 1, c_))
T('')
T('## 6 问题清单(按 MAJOR / MINOR / NIT)')
T('')
T('### 6.1 MAJOR(%d 条)' % nmaj)
T('')
if nmaj == 0:
    T('无: 未发现数字 / 日期 / 方向错误, 缺基期同比, 相邻口径冒充, 事后信息冒充当时可知, 无标注的超证据结论, 或不可观测的证伪条件。')
T('')
for sev, ttl in (('MINOR', '6.2 MINOR(%d 条; 口径/披露可改进但不改变结论, 不构成阻断)'), ('NIT', '6.3 NIT(%d 条; 行文)')):
    T('### ' + ttl % sum(1 for it in items if it['severity'] == sev))
    T('')
    for it in items:
        if it['severity'] != sev:
            continue
        T('- **%s** 位置: %s' % (it['note'].split(' ', 1)[0].rstrip(':'), it['where']))
        T('  - 原句: %s' % it['original'])
        T('  - 建议改句(非必修): %s' % it['fix'])
        T('  - 说明: %s' % it['note'])
    T('')
T('### 6.4 引擎面观察(非判断档问题, 不计入裁决, 供操作席参考)')
T('')
for e_ in ENGOBS:
    T('- %s' % e_)
T('')
T('## 7 过程留痕')
T('')
sw1, n14b = '', 0
p14, p14b = os.path.join(D, 'mid_rc14_out.txt'), os.path.join(D, 'mid_rc14b_out.txt')
if os.path.exists(p14):
    with open(p14, encoding='utf-8') as f_:
        sw1 = f_.readline().strip()
if os.path.exists(p14b):
    with open(p14b, encoding='utf-8') as f_:
        n14b = sum(1 for _ in f_)
for i, t_ in enumerate(PROC):
    T('- ' + (t_ % ((sw1 or '(中间结果文件不在)'), n14b) if i == len(PROC) - 1 else t_))
T('')
T('## 8 裁决')
T('')
T('**%s**——MAJOR %d 条、偏离 %d 点。%s' % (VERD_WORD, nmaj, NF, 'MINOR 与 NIT 如实列于第 6 节与 VERDICT JSON items, 不构成阻断; must_fix 为空数组。' if VERD_WORD == 'UPHELD' else '必修项见 must_fix。'))
T('')
PROSE = ''.join(P)

# ====================== 叙述数字自检(席位引用的数字须可在台账数值集合或本脚本直算值中找到) ============================
LED_F = set()
for r_ in recs:
    for m_ in re.finditer(r'-?\d+(?:\.\d+)?', json.dumps([r_.get('computed'), r_.get('reported')], ensure_ascii=False)):
        LED_F.add(round(abs(float(m_.group(0))), 6))
EXTRA = [list(Y.values()), GAP_HI_BP, GAP_LO_BP, OMO_GAP, DFFCP, DFF_AN, len(ENTS), len(HICP_CAL), PP_MIN_ALL, PP_MIN_23, NT, NF, len(NA), len(recs), nmin, nnit, nmaj, len(CA),
         len(VS), len(SC_), len(MC), len(TURN), len(HIST), len(aj['l3']['mechanism_chains']), len(qgn), len(PEND), len(snap.get('series_store') or {}),
         [c_[0] for c_ in sec_count.values()] + [c_[1] for c_ in sec_count.values()] + [c_[2] for c_ in sec_count.values()],
         (CV.get('stats') or {}), [round(x[1], 2) for x in DFFCP] + [round(x[3], 2) for x in DFFCP], [JPC[k_] for k_ in ('2026-02', '2026-03', '2026-04', '2026-05', '2026-09')]]
for m_ in re.finditer(r'-?\d+(?:\.\d+)?', json.dumps(EXTRA, ensure_ascii=False, default=str)):
    LED_F.add(round(abs(float(m_.group(0))), 6))
for v_ in Y.values():
    if v_ is not None:
        LED_F.add(round(v_, 4))
for _, _txt in COV:
    for _m in re.finditer(r'』(\d+) 条', _txt):
        LED_F.add(float(_m.group(1)))
NUM_OK = {'192': 'rc08 席位脚本行号(非数据)'}
NARR = ''.join(SIX) + '\n'.join(CA) + '\n'.join(it['note'] + ' ' + it['fix'] for it in items) + '\n'.join(t_ for _, t_ in COV) + '\n'.join(PROC) + NOTES \
    + '\n'.join(e_ for e_ in ENGOBS) + '\n'.join(T('') or '' for _ in ()) + PROSE.split('## 2 复算清单')[0]


def nummiss(txt):
    t = re.sub(r'(?<![0-9A-Za-z])[0-9a-f]{16,}(?![0-9A-Za-z])', ' ', txt)
    t = re.sub(r'\d{8}T\d{6}Z', ' ', t)
    t = re.sub(r'(?<!\d)20261123(?!\d)', ' ', t)
    t = t.replace('标普500', '标普').replace('sha256', 'sha').replace('HTTP 429', 'HTTP')
    t = re.sub(r'\d{2}:\d{2}:\d{2}', ' ', t)
    t = re.sub(r'见 [1-8]\.[0-9](?![0-9])', ' ', t)
    t = re.sub(r'[1-8]\.[0-9] 第', ' 第', t)
    t = re.sub(r'#+ [1-8]\.[0-9] ', ' ', t)
    t = re.sub(r'\(5\.[0-9]\)', '()', t)
    t = re.sub(r'#\d+(?:–#\d+)?', ' ', t)
    t = re.sub(r'\d{4}-\d{2}-\d{2}T?[0-9+:]*', ' ', t)
    t = re.sub(r'\d{4}-\d{2}(?![0-9])', ' ', t)
    t = re.sub(r'(?<![0-9.])\d{4}(?![0-9.])', ' ', t)
    out = []
    for m_ in re.finditer(r'-?\d+(?:\.\d+)?', t):
        tok = m_.group(0)
        if round(abs(float(tok)), 6) in LED_F:
            continue
        out.append((tok, t[max(0, m_.start() - 16):m_.end() + 16].replace('\n', ' ')))
    return out


NUMMISS = [x for x in nummiss(NARR) if x[0] not in NUM_OK]
need(all(x[0] in NUM_OK for x in NUMMISS), '叙述数字未能在台账/直算值中找到 %d 处(见 NUMMISS)' % len(NUMMISS))

# ====================== JSON ============================
VERD = collections.OrderedDict([
    ('seat', 'semantic-audit-seat'),
    ('reviewer', 'independent-zero-context-seat-r32-a-round1'),
    ('verdict', VERD_WORD),
    ('overall', VERD_WORD),
    ('notes', NOTES),
    ('items', [dict(it) for it in items]),
    ('must_fix', []),
    ('counterexamples_sought', list(CA)),
    ('recompute_points', NT),
    ('recompute_mismatches', NF),
    ('mismatch_details', []),
    ('audited_at', NOW_DAY),
])
VER_JSON = json.dumps(VERD, ensure_ascii=False, indent=2) + '\n'
KEYS = ['seat', 'reviewer', 'verdict', 'overall', 'notes', 'items', 'must_fix', 'counterexamples_sought', 'recompute_points', 'recompute_mismatches', 'mismatch_details', 'audited_at']
back = json.loads(VER_JSON)
need(list(back.keys()) == KEYS, 'JSON 键不符')
need(all(list(it.keys()) == ['severity', 'where', 'note', 'original', 'fix'] for it in back['items']), 'items 键不符')
need(back['verdict'] in ('UPHELD', 'REVISE') and back['verdict'] == back['overall'], '裁决词不符')
need((back['verdict'] == 'UPHELD') == (nmaj == 0 and NF == 0), '裁决词与 MAJOR/偏离计数不一致')
need(len(back['counterexamples_sought']) >= 5, '反方攻击条数不足')
need(back['recompute_points'] == sum(1 for r_ in recs if r_['ok'] is True) and back['recompute_mismatches'] == NF, '计数不符')
for bad_ in ('f722e3c', '19638e1', '8f9055d'):
    need(bad_ not in PROSE and bad_ not in VER_JSON, '产出含预审印章字样: ' + bad_)
need('(未找到原句)' not in PROSE and '(未找到原句)' not in VER_JSON, '存在未定位的原句')
need('(未定位)' not in PROSE and '(未定位)' not in VER_JSON, '存在未定位的位置')

# ====================== 诊断打印 ============================
print('MODE', MODE, '| ledger records', len(recs), 'True', NT, 'False', NF, 'NA', len(NA), '| items MAJOR/MINOR/NIT', nmaj, nmin, nnit, '| verdict', VERD_WORD)
print('NMD', json.dumps(GA.get('noncore_missing_detail'), ensure_ascii=False)[:1500])
print('JPR', {k_: JPR.get(k_) for k_ in ('2025-11', '2025-12', '2026-03', '2026-04', '2026-07', '2026-08', '2026-10')}, 'TF1', TF1, 'TF2', TF2, 'TP', TP, 'HP', HP)
print('PROBLEMS (%d):' % len(PROBLEMS))
for x in PROBLEMS:
    print('  - ' + x[:500])
print('SECTIONS:')
for s_, c_ in sec_count.items():
    print('  %s | %d / %d / %d' % (s_, c_[0], c_[1], c_[2]))
print('TURN', TP, [list(t.keys())[:14] for t in TURN])
print('HIST', HP, [list(h.keys())[:16] for h in HIST])
print('FV', FV)
print('PEND', [(e.get('entry_id'), e.get('decision_date'), e.get('effective_date')) for e in PEND])
print('HICP_CAL', [(e.get('entry_id'), e.get('kind') or e.get('type'), e.get('obs_from'), e.get('obs_to'), e.get('first_publish_on_or_after'), e.get('decision_date')) for e in HICP_CAL])
print('ENTS kinds', dict(collections.Counter(str(e.get('kind') or e.get('type') or e.get('category')) for e in ENTS)), 'keys', sorted(ENTS[0].keys()) if ENTS else None)
print('DFFCP', DFFCP, 'DFF_AN', DFF_AN, 'OMO_GAP', OMO_GAP)
print('USED_M', USED_M, 'USED_D', USED_D, 'IDX_GATE', IDX_GATE, 'IDX_STOCK', IDX_STOCK)
print('CV statuses', dict(collections.Counter(str(v.get('status')) for v in VS)), dict(collections.Counter(str(v.get('status')) for v in SC_)), dict(collections.Counter(str(v.get('status')) for v in MC)), CV.get('stats'))
print('CALVER', cal.get('version'), cal.get('calendar_version'), 'nseries', len(snap.get('series_store') or {}), 'RA', RA)
print('BUND leaves', [p_ for p_, t_ in leaves(aj) if 'BUND' in t_])
print('Q', Q[:500])
for i in (670, 861, 932, 860, 863, 520, 877, 917, 923, 924, 876, 874, 916, 915, 579, 581, 582, 583, 544, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 345, 346, 904, 905):
    if i < len(recs):
        print('REC #%d ok=%s src=%s | computed=%s | reported=%s | note=%s' % (i, recs[i]['ok'], str(recs[i].get('src'))[:170], json.dumps(recs[i].get('computed'), ensure_ascii=False)[:230],
                                                                                json.dumps(recs[i].get('reported'), ensure_ascii=False)[:170], str(recs[i].get('note'))[:260]))
print('SCTXT', SCTXT[:2200])
for p_, t_ in LEAVES:
    for m_ in re.finditer(r'[^。；;\n]*距[^。；;\n]{0,14}天[^。；;\n]*', t_):
        print('DIST', p_, '::', m_.group(0)[:220])
print('NUMMISS (%d):' % len(NUMMISS))
for tok, ctx in NUMMISS:
    print('  %s | %s' % (tok, ctx))
print('SWEEP', sw1, '|', n14b)
if os.path.exists(p14):
    with open(p14, encoding='utf-8') as f_:
        for ln in f_:
            if '100%' in ln or '20261123' in ln:
                print('SW', ln.strip()[:300])
print('PROSE bytes', len(PROSE.encode('utf-8')), 'lines', PROSE.count('\n'), '| JSON bytes', len(VER_JSON.encode('utf-8')))

# ====================== 输出 ============================
if MODE == 'draft':
    with open(DR_MD, 'w', encoding='utf-8') as f_:
        f_.write(PROSE)
    with open(DR_JS, 'w', encoding='utf-8') as f_:
        f_.write(VER_JSON)
    print('DRAFT written:', DR_MD, DR_JS)
else:
    if PROBLEMS:
        print('ABORT: problems present, nothing written')
        sys.exit(2)
    if os.path.exists(OUT_MD) or os.path.exists(OUT_JS):
        print('REFUSE: final outputs already exist, nothing written')
        sys.exit(3)
    for dr, txt in ((DR_MD, PROSE), (DR_JS, VER_JSON)):
        if os.path.exists(dr):
            with open(dr, encoding='utf-8') as f_:
                if f_.read() != txt:
                    print('ABORT: draft differs from final content:', dr)
                    sys.exit(4)
    with open(OUT_MD, 'w', encoding='utf-8') as f_:
        f_.write(PROSE)
    with open(OUT_JS, 'w', encoding='utf-8') as f_:
        f_.write(VER_JSON)
    print('WRITTEN:', OUT_MD, sha(OUT_MD))
    print('WRITTEN:', OUT_JS, sha(OUT_JS))
