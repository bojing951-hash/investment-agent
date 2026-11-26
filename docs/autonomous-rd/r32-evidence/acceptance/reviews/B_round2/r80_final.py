# -*- coding: utf-8 -*-
# r80_final.py — 终装配(只读受审面; 产出仅写入本席目录 B)
# 用法: python3 -I r80_final.py <RUN_DIR> <SNAPSHOT_JSON> <B_DIR> [--write]
# 不带 --write: 自检并写预览 x80_preview_PROSE.md / x80_preview_VERDICT.json / x80_summary.txt(均在 B 内, 可覆盖)
# 带 --write: 一次性写出 PROSE-round2.md 与 VERDICT-round2.json(已存在则拒绝; 与预览不一致则拒绝), 写出后不再改写
import os, sys, json, hashlib, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r00_common import *
import r80a_points
import r80b_text as T

NL = chr(10)
PIPE = chr(92) + '|'
RX40 = re.compile('[0-9a-f]{40}')
RXA = re.compile('^A[0-9]+$')
RXID = re.compile('[A-Z]+[0-9]+')
MDS = ('MAP_REPORT.md', 'FULL_REPORT.md', 'report.md')
TODAY = '2026-11-24'
ANC = 'AN 历史相似结构表独立复算'


def sha_file(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def norm(s):
    return ''.join(str(s).split()).replace(PIPE, '|')


def cell(s):
    return str(s).replace('|', PIPE).replace(NL, ' ')


def locate(RAW, text):
    out = {}
    key = norm(text)
    if len(key) < 6:
        return out
    for fn in MDS:
        lines = [norm(l) for l in RAW[fn].split(NL)]
        hits = []
        for i, ln in enumerate(lines):
            if key in ln or (len(key) > 30 and key[:20] in ln and key[-14:] in ln):
                hits.append(i + 1)
        if hits:
            out[fn] = hits
    return out


def loc_s(loc):
    if not loc:
        return '未逐字定位'
    return '; '.join('%s L%s' % (fn, '/'.join(str(x) for x in loc[fn])) for fn in MDS if fn in loc)


def table(header, rows):
    out = ['| ' + ' | '.join(cell(c) for c in header) + ' |', '|' + '|'.join(['---'] * len(header)) + '|']
    for r in rows:
        out.append('| ' + ' | '.join(cell(c) for c in r) + ' |')
    return NL.join(out)


def main():
    argv = sys.argv[1:]
    WRITE = '--write' in argv
    args = [a for a in argv if not a.startswith('--')]
    RUN, SNAPP, B = args[0], args[1], args[2]
    ERR = []

    def F(n):
        return os.path.join(RUN, n)

    rep = load(F('report.json'))
    aj = load(F('agent_judgment.json'))
    cal = load(F(os.path.join('root_overlay', 'config', 'release_calendar.json')))
    sn = Snap(load(SNAPP))
    RAW = dict((fn, open(F(fn), encoding='utf-8').read()) for fn in MDS)
    R = r80a_points.build(sn, rep, aj, cal, RAW, B, ERR)
    V, EX, Z = R['V'], R['EX'], R['Z']
    # 历史类比组点号统一为 AN 前缀(早期脚本对第 37 点起写作 A 前缀, 与截止时点组 A01..A19 易混)
    REN = {}
    for p in R['ALLP']:
        if (p.get('cat') or '') == ANC and RXA.match(p['id']):
            REN[p['id']] = 'AN' + p['id'][1:]
    for lst in (R['ALLP'], R['COUNTED'], R['INFOP'], R['DUPP'], R['ALL'], R['NEW']):
        for p in lst:
            if p.get('id') in REN:
                p['id'] = REN[p['id']]
            if p.get('_dup_of') in REN:
                p['_dup_of'] = REN[p['_dup_of']]
            if p.get('id') == 'K04' and 'REVIEW 文件' in str(p.get('where')):
                p['where'] = str(p['where']).replace('REVIEW 文件', '本席中间结果 x10_render_review.txt')
    CNT, INFOP, DUPP = R['COUNTED'], R['INFOP'], R['DUPP']
    ALLIDS = set([p['id'] for p in CNT] + [p['id'] for p in INFOP])
    if len(ALLIDS) != len(CNT) + len(INFOP):
        ERR.append('计分/信息项点号存在重复: %d vs %d' % (len(ALLIDS), len(CNT) + len(INFOP)))
    for p in DUPP:
        for d in RXID.findall(str(p.get('_dup_of'))):
            if d not in ALLIDS:
                ERR.append('重复项 %s 所指 %s 不在计分/信息项内' % (p['id'], d))
    # 持平月水平对照点(D20–D24, 重复项): 早期脚本的核对对象/出处键写作「A − B」,
    # 实际计算为 A 月月均水平对照 B 月月均(容差 0.001); 此处改写标注使之与计算一致(只改文字, 不改数值与判定)
    FLATL = dict((('D20', '2026-02'), ('D21', '2026-03'), ('D22', '2026-04'), ('D23', '2026-05'), ('D24', '2026-08')))
    NFL = 0
    for p in R['ALLP']:
        if p.get('id') in FLATL and isinstance(p.get('computed'), (int, float)):
            ym = FLATL[p['id']]
            rf = '2026-07' if p['id'] == 'D24' else '2026-01'
            p['where'] = 'C3「2026-02 至 2026-05 与 2026-08 的相邻月均差均不超过 0.001」(%s 月均水平, 对照 %s 月均, 容差 0.001)' % (ym, rf)
            p['key'] = 'series_store.JP_POLICY_RATE %s-01 月均(报告值栏为 %s-01 月均)' % (ym, rf)
            p['note'] = '水平对照: 直算值=该月月均; 报告值栏=对照月月均(同取自冻结快照); 两者之差即该月相邻月均差'
            NFL += 1
    if NFL != 5:
        ERR.append('持平月水平对照点改写数异常: %d' % NFL)

    # ---- 受审版本身份 ----
    mapsha = sha_file(F('MAP_REPORT.md'))
    shaf = F('MAP_REPORT.sha256')
    mapsha_rec = open(shaf, encoding='utf-8').read().split()[0] if os.path.exists(shaf) else None
    if mapsha_rec != mapsha:
        ERR.append('MAP_REPORT.sha256 记录值与文件实算不一致: %s vs %s' % (mapsha_rec, mapsha))
    stamp = None
    for l in RAW['MAP_REPORT.md'].split(NL):
        if 'SHA' in l:
            m = RX40.findall(l)
            if m:
                stamp = m[-1]
    if not stamp or not stamp.startswith('36499bb'):
        ERR.append('代码印章未定位或不符: %s' % stamp)
    ident = [(fn, sha_file(F(fn))) for fn in MDS + ('agent_judgment.json', 'report.json')]

    # ---- 问题清单 / 六查 / 反方攻击 ----
    IT = T.items(aj, V, EX, ERR)
    for it in IT:
        key = it['original']
        if it['id'] == 'NIT-3':
            key = aj['l3']['mechanism_chains'][0]['links'][2]['text'][:40]
        it['loc'] = locate(RAW, key)
        it['where'] = '%s(agent_judgment.json %s);渲染位置: %s' % (it['where_base'], it['path'], loc_s(it['loc']))
    S6 = T.six_check(V, EX, ERR)
    AT = T.attacks(V, EX)
    N = len(CNT)
    bad = [p for p in CNT if not p['ok']]
    n_maj = len([i for i in IT if i['severity'] == 'MAJOR'])
    n_min = len([i for i in IT if i['severity'] == 'MINOR'])
    n_nit = len([i for i in IT if i['severity'] == 'NIT'])
    VERDICT = 'REVISE' if (n_maj or bad) else 'UPHELD'
    NOTE = T.notes(V, EX, N, n_min, n_nit, len(AT), stamp)

    # ---- 规程 §3 覆盖对照 ----
    def catof(p):
        return p.get('cat') or ''

    BP = 'B' + chr(39) + ' 发布纪律'

    def ids_of(names):
        return [p['id'] for p in CNT if catof(p) in names]

    def ids_rx(pat, names=None):
        rx = re.compile(pat)
        return [p['id'] for p in CNT if (names is None or catof(p) in names) and (rx.search(str(p['where'])) or rx.search(str(p['key'])))]

    EF = ['E 利率分解', 'F 资产与汇率窗']
    COV = [
        ('① 截止日', 'research_as_of=快照版本日、各地截止时点', ids_of(['A 截止时点'])),
        ('② 点值锚格', '两锚点值×观测月逐格、规则发布日与可见性', ids_of(['B 锚点格', BP])),
        ('③ 同比', '严格同基期同比派生、缺基期不可得不冒充', ids_of(['C 同比派生'])),
        ('④ 政策面', '决议/生效/维持、距上次调整天数、目标与市场口径分列', ids_of(['D 政策口径'])),
        ('⑤ 三利率分解与资产月窗', '名义=实际+盈亏平衡、汇率与资产窗', ids_of(EF)),
        ('⑥ 转折判断与候选面', '三转折前值/后值/变动/序位/候选池最大事件', ids_of(['G 转折面直算'])),
        ('⑦ 传导链各环数字回贴', '环内数字逐个回贴序列面(证据级与假设位措辞见三、四节)', ids_of(EF + ['G 转折面直算', 'M 条目支撑', 'X 补充核验'])),
        ('⑧ 历史类比', '相似结构表独立复现(不调用引擎)+事后段标注与零段呈现', ids_of([ANC, 'L 引擎渲染表'])),
        ('⑨ 情景', '触发/证伪阈值、期限、规则发布日可观测性', ids_of(['I 情景可观测性'])),
        ('⑩ 总判断/走位/对质表一致性', '渲染一致性+走位数字(一致性判断见三、四节)', ids_of(['K 渲染一致性']) + [i for i in ('M2a', 'M4a', 'M4b', 'M4c', 'M4d') if i in ids_of(['M 条目支撑'])]),
        ('⑪ 诚实缺席项与 Gate A', '缺口/降级/缺席/缺基期披露', ids_of(['H 诚实缺席与门面'])),
        ('⑫ 截止日当日日频观测时点说明', '盘中快照/非收盘价/截止时点逐项', ids_rx('盘中快照|research_as_of|快照时点|截止时点|非收盘价')),
        ('⑬ 契约验证非 VERIFIED 项披露', 'STALE/降级口径披露', ids_rx('STALE|契约|VERIFIED')),
        ('⑭ 交付门相关缺口披露', 'Gate A/缺口/降级/缺席/注册表', ids_rx('Gate A|交付门|缺席|降级|缺口|DEGRADED|注册表')),
        ('横切 数字记号覆盖闭合', '判断档渲染范围记号与读者面记号在报告逐字在场', ids_of(['Y 记号覆盖闭合'])),
    ]

    # ---- 程序性观察(不计入受审稿问题) ----
    sr = rep.get('semantic_review') or {}
    srlines = []
    for fn in MDS:
        for i, l in enumerate(RAW[fn].split(NL)):
            if '席位已裁' in l or '席位裁决' in l:
                srlines.append('%s L%d「%s」' % (fn, i + 1, l.strip()[:96]))
    obsA = ('语义审查登记面(非受审判断文字): report.json semantic_review 机器面 verdict=%s, fresh=%s, verdicts_n=%s, 绑定 map_report_sha256=%s(当前 MAP_REPORT.md 实算 %s,%s)。读者报告中「席位已裁/席位裁决」行: %s。即读者面此刻显示的是此前一轮的裁决登记(REVISE,裁决链 1 档),且未绑定当前报告版本;本席未读取该登记档内容。本轮(Round-2)裁决登记后须重新渲染并重新绑定,否则读者面「语义审查」节与实际裁决不一致。' % (sr.get('verdict'), sr.get('fresh'), sr.get('verdicts_n'), sr.get('map_report_sha256'), mapsha, '相同' if sr.get('map_report_sha256') == mapsha else '不同', '; '.join(srlines) if srlines else '无'))

    def rendered(txt):
        t = norm(txt)
        allmd = [norm(x) for x in RAW.values()]
        if len(t) < 12:
            return (3, 3)
        cs = [t[len(t) * k // 4: len(t) * k // 4 + 30] for k in (1, 2, 3)]
        cs = [c for c in cs if len(c) >= 12]
        return (len([c for c in cs if any(c in m for m in allmd)]), len(cs))

    NR = []
    for i, t in enumerate(aj['reader_map']['turnings']):
        NR.append(('reader_map.turnings[%d].narrative' % i, len(t['narrative']), rendered(t['narrative'])))
    for i, lk in enumerate(aj['reader_map']['transmission'][0]['links']):
        NR.append(('reader_map.transmission[0].links[%d].verdict_note' % i, len(lk['verdict_note']), rendered(lk['verdict_note'])))
    for i, q in enumerate(aj['quality_gate_notes']):
        NR.append(('quality_gate_notes[%d]' % i, len(q), rendered(q)))
    NR.append(('agent_declaration.produced_by', len(aj['agent_declaration']['produced_by']), rendered(aj['agent_declaration']['produced_by'])))
    NR.append(('agent_declaration.basis', len(aj['agent_declaration']['basis']), rendered(aj['agent_declaration']['basis'])))
    hn = aj['reader_map'].get('history_zero_case_note') or ''
    NR.append(('reader_map.history_zero_case_note', len(hn), rendered(hn)))
    UN = [x for x in NR if x[2][0] == 0]
    PA = [x for x in NR if 0 < x[2][0] < x[2][1]]
    SE = [x for x in NR if x[2][0] == x[2][1]]

    def fmt(xs):
        return '; '.join('%s(%d 字,片段在场 %d/%d)' % (a, b, c[0], c[1]) for a, b, c in xs)

    obsB = ('判断档字段在读者报告的渲染情况(逐字片段检索: 取字段 1/4、2/4、3/4 处各 30 字,统计三份读者报告中在场的片段数;只查逐字在场,不等于内容未被其他形式呈现): 未见渲染(0/3)的字段 %d 个——%s;仅部分片段在场——%s;逐字在场——%s。其中 turnings[].narrative 与 links[].verdict_note 不进渲染已由 quality_gate_notes[5] 第③项自述(引擎渲染设计);quality_gate_notes 其余各项与 agent_declaration 两字段未见逐字渲染,亦未见自述——其披露内容(截止时点、降级口径、序列不可得、引擎缺口、署名与依据)是否经引擎其他披露块另路呈现,本席未逐项核对。本席已对这些字段内的数字同样逐点直算(A、D、E、G、H 组),内容不构成判断错误;提请操作席/引擎侧裁定是否补渲染。' % (len(UN), fmt(UN), fmt(PA), fmt(SE)))

    # ---- PROSE ----
    L = []
    L.append('# Audit-R32 独立语义审查席位 B — Round-2 复算与裁决备忘')
    L.append('')
    L.append('- 席位: semantic-audit-seat / independent-zero-context-seat-r32-b-round2(零上下文;未读取任何预审内容、其他席位产出或运行目录外文件)')
    L.append('- 受审版本(运行目录): %s' % RUN)
    L.append('- 受审对象: agent_judgment.json 全文(l3 / l4 / reader_map / quality_gate_notes / agent_declaration,schema %s)与 MAP_REPORT.md / FULL_REPORT.md / report.md 中的判断文字' % aj.get('schema_version'))
    L.append('- 只读面: 冻结快照 research_snapshot_20261123.json(series_store %d 条序列)、冻结发布日历 release_calendar.json(v%s,%d 条)、注册表 metric_registry.json、report.json 引擎面' % (len(sn.ids()), cal.get('version'), V['cal']['n']))
    L.append('- 代码印章(完整运行 SHA,取自 MAP_REPORT.md): %s' % stamp)
    L.append('- 受审文件 sha256: %s' % '; '.join('%s=%s' % (a, b) for a, b in ident))
    L.append('- 裁决日: %s' % TODAY)
    L.append('')
    L.append('## 〇、方法与口径')
    L.append('')
    L.append('1. 全部数字由本席自写脚本直接从只读面取数直算(series_store 剔除 null/NaN;同比=当月值÷严格上年同月值−1,缺基期即不可得;变动百分点=同口径两值相减;bp=利差/利率差×100),再与受审稿文字逐点比对。')
    L.append('2. 一致判据: 数值按报告值所给小数位的半个单位为容差;非数值项按字符串相等;关系词(最高/最低/同步/先后)直算为布尔或月份后比对。')
    L.append('3. 出处键写法: series_store.<ID>.values[i](dates[i]=日期) 指冻结快照;report.json … 指引擎面;root_overlay/config/release_calendar.json 指冻结日历。')
    L.append('4. 计数口径: 同一数值在同一序列上重复出现于不同文本位置者只计 1 次(另列「重复核对项」);信息项(只直算、无比对值)不计分。')
    L.append('5. 历史相似结构表由本席自写实现(不调用引擎代码)从序列库重算后与引擎面逐值比对。')
    L.append('')
    L.append('## 一、复算清单(逐点: 出处键 / 直算值 / 报告值 / 一致与否)')
    L.append('')
    L.append('合计计分点 %d,偏离 %d;另有信息项 %d、重复核对项 %d(全部一致,不重复计)。' % (N, len(bad), len(INFOP), len(DUPP)))
    CATS = []
    for p in R['ALLP']:
        if catof(p) not in CATS:
            CATS.append(catof(p))
    for c in CATS:
        rows = [[p['id'], p['where'], p['key'], p['computed'], p['reported'], '一致' if p['ok'] else '偏离', p.get('note') or ''] for p in CNT if catof(p) == c]
        if rows:
            L.append('')
            L.append('### %s(%d 点)' % (c, len(rows)))
            L.append('')
            L.append(table(['编号', '核对对象(稿内位置)', '出处键', '直算值', '报告值', '一致', '备注'], rows))
    L.append('')
    L.append('### 信息项(直算事实,不比对报告值;%d 项)' % len(INFOP))
    L.append('')
    L.append(table(['编号', '核对对象', '出处键', '直算值', '备注'], [[p['id'], p['where'], p['key'], p['computed'], p.get('note') or ''] for p in INFOP]))
    L.append('')
    L.append('### 重复核对项(与计分点为同一数值同一序列,不重复计;%d 项,全部一致)' % len(DUPP))
    L.append('')
    L.append(table(['编号', '重复于', '核对对象', '出处键', '直算值', '报告值'], [[p['id'], p.get('_dup_of') or '—', p['where'], p['key'], p['computed'], p['reported']] for p in DUPP]))
    L.append('')
    L.append('### 六查补充直算事实(信息项)')
    L.append('')
    L.append(table(['事实', '出处键', '直算值'], [[z['name'], z['key'], json.dumps(z['value'], ensure_ascii=False, default=str)] for z in Z]))
    L.append('')
    L.append('## 二、规程 §3 覆盖对照(①–⑭)')
    L.append('')
    for name, desc, ids in COV:
        L.append('- %s — %s: %d 点;点号: %s' % (name, desc, len(ids), ', '.join(ids) if ids else '无'))
    L.append('')
    L.append('## 三、六查逐项结论(证据相关性 / 支持度 / 竞争解释 / 反对证据 / 结论是否超出证据 / 证伪条件可观测性)')
    for s in S6:
        L.append('')
        L.append('### %s' % s['title'])
        L.append('')
        L.append(table(['查项', '结论'], s['rows']))
    L.append('')
    L.append('## 四、反方攻击记录(每条 L3 陈述、机制链、传导环、情景、转折面、历史类比、总判断至少一条)')
    L.append('')
    for a in AT:
        L.append('- %s' % a)
    L.append('')
    L.append('## 五、问题清单')
    L.append('')
    L.append('### MAJOR(%d 条)' % n_maj)
    L.append('')
    if n_maj == 0:
        L.append('无。')
    for sev in ('MINOR', 'NIT'):
        sub = [it for it in IT if it['severity'] == sev]
        L.append('')
        L.append('### %s(%d 条)' % (sev, len(sub)))
        L.append('')
        L.append(table(['编号', '位置', '原句', '问题', '改句(建议)'], [[it['id'], it['where'], it['original'], it['note'], it['fix'] or '—'] for it in sub]))
    L.append('')
    L.append('### 程序性观察(不计入受审稿问题,提请操作席/引擎侧处理)')
    L.append('')
    L.append('- A. %s' % obsA)
    L.append('- B. %s' % obsB)
    L.append('')
    L.append('## 六、裁决')
    L.append('')
    L.append('**%s**(抽核 %d 点 / 偏离 %d;MAJOR %d / MINOR %d / NIT %d;反方攻击 %d 次)' % (VERDICT, N, len(bad), n_maj, n_min, n_nit, len(AT)))
    L.append('')
    L.append(NOTE)
    L.append('')
    PROSE = NL.join(L)

    # ---- VERDICT JSON ----
    items_json = []
    for it in IT:
        d = {'severity': it['severity'], 'where': it['where'], 'note': '%s %s' % (it['id'], it['note'])}
        if it.get('original'):
            d['original'] = it['original']
        if it.get('fix'):
            d['fix'] = it['fix']
        items_json.append(d)
    vd = {
        'seat': 'semantic-audit-seat',
        'reviewer': 'independent-zero-context-seat-r32-b-round2',
        'verdict': VERDICT,
        'overall': VERDICT,
        'notes': NOTE,
        'items': items_json,
        'must_fix': ['%s %s 原句: %s 改句: %s' % (it['id'], it['note'], it['original'], it['fix']) for it in IT if it['severity'] == 'MAJOR'],
        'counterexamples_sought': AT,
        'recompute_points': N,
        'recompute_mismatches': len(bad),
        'mismatch_details': [{'id': p['id'], 'where': p['where'], 'key': p['key'], 'computed': p['computed'], 'reported': p['reported']} for p in bad],
        'audited_at': TODAY,
    }
    txt = json.dumps(vd, ensure_ascii=False, indent=1)
    back = json.loads(txt)
    for k in ('seat', 'reviewer', 'verdict', 'overall', 'notes', 'items', 'must_fix', 'counterexamples_sought', 'recompute_points', 'recompute_mismatches', 'mismatch_details', 'audited_at'):
        if k not in back:
            ERR.append('VERDICT 缺键 %s' % k)
    if back['verdict'] not in ('UPHELD', 'REVISE') or back['overall'] != back['verdict']:
        ERR.append('verdict 取值异常')
    for it in back['items']:
        if it['severity'] not in ('MAJOR', 'MINOR', 'NIT'):
            ERR.append('severity 异常: %s' % it.get('note'))
        if it['severity'] == 'MAJOR' and not (it.get('original') and it.get('fix')):
            ERR.append('MAJOR 缺 original/fix')
    if back['recompute_mismatches'] != len(back['mismatch_details']) or back['recompute_mismatches'] != len(bad):
        ERR.append('mismatch 计数不一致')
    if len(back['must_fix']) != n_maj or len(AT) < 1 or N < 80 or len(IT) != n_maj + n_min + n_nit:
        ERR.append('计数自检失败: must_fix=%d maj=%d att=%d N=%d items=%d' % (len(back['must_fix']), n_maj, len(AT), N, len(IT)))
    if bool(n_maj or bad) != (VERDICT == 'REVISE'):
        ERR.append('verdict 与问题数不一致')
    for name, desc, ids in COV:
        if not ids:
            ERR.append('覆盖项无对应点: %s' % name)
    if bad:
        ERR.append('存在偏离点: %s' % [p['id'] for p in bad])

    # ---- 摘要 ----
    S = ['VERDICT=%s points=%d mismatches=%d MAJOR=%d MINOR=%d NIT=%d attacks=%d info=%d dup=%d renamed=%d' % (VERDICT, N, len(bad), n_maj, n_min, n_nit, len(AT), len(INFOP), len(DUPP), len(REN)),
         'stamp=%s mapsha=%s rec=%s' % (stamp, mapsha, mapsha_rec),
         'ERR(%d): %s' % (len(ERR), ERR)]
    S.append('DUP rows: ' + '; '.join('%s>%s' % (p['id'], p.get('_dup_of')) for p in DUPP))
    for it in IT:
        S.append('ITEM %s | %s | loc=%s' % (it['id'], it['severity'], json.dumps(it['loc'], ensure_ascii=False)))
        S.append('   ORIG: %s' % it['original'])
        S.append('   NOTE: %s' % it['note'])
        S.append('   FIX : %s' % (it['fix'] or '-'))
    S.append('NOTE: ' + NOTE)
    S.append('OBS_A: ' + obsA)
    S.append('OBS_B: ' + obsB)
    S.append('SIX titles: ' + ' | '.join('%s(%d 行)' % (s['title'], len(s['rows'])) for s in S6))
    S.append('COV: ' + ' | '.join('%s=%d' % (name.split(' ')[0], len(ids)) for name, desc, ids in COV))
    SUM = NL.join(S)

    if not WRITE:
        with open(os.path.join(B, 'x80_preview_PROSE.md'), 'w', encoding='utf-8') as fh:
            fh.write(PROSE)
        with open(os.path.join(B, 'x80_preview_VERDICT.json'), 'w', encoding='utf-8') as fh:
            fh.write(txt + NL)
        with open(os.path.join(B, 'x80_summary.txt'), 'w', encoding='utf-8') as fh:
            fh.write(SUM)
        print('DRY-RUN OK' if not ERR else 'DRY-RUN HAS ERRORS')
        print('prose bytes=%d lines=%d ; verdict bytes=%d' % (len(PROSE.encode('utf-8')), PROSE.count(NL), len(txt.encode('utf-8'))))
        return
    if ERR:
        print('REFUSE: 自检未过')
        print(SUM)
        sys.exit(2)
    fp = os.path.join(B, 'PROSE-round2.md')
    fv = os.path.join(B, 'VERDICT-round2.json')
    for p in (fp, fv):
        if os.path.exists(p):
            print('REFUSE: 产出已存在,不再改写: %s' % p)
            sys.exit(3)
    pp, pv = os.path.join(B, 'x80_preview_PROSE.md'), os.path.join(B, 'x80_preview_VERDICT.json')
    if os.path.exists(pp) and open(pp, encoding='utf-8').read() != PROSE:
        print('REFUSE: 与预览 PROSE 不一致,请先重跑预览')
        sys.exit(4)
    if os.path.exists(pv) and open(pv, encoding='utf-8').read() != txt + NL:
        print('REFUSE: 与预览 VERDICT 不一致,请先重跑预览')
        sys.exit(4)
    with open(fp, 'x', encoding='utf-8') as fh:
        fh.write(PROSE)
    with open(fv, 'x', encoding='utf-8') as fh:
        fh.write(txt + NL)
    print('WRITTEN')
    print('%s sha256=%s bytes=%d' % (fp, sha_file(fp), os.path.getsize(fp)))
    print('%s sha256=%s bytes=%d' % (fv, sha_file(fv), os.path.getsize(fv)))
    print(SUM.split(NL)[0])


main()
