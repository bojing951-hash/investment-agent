# -*- coding: utf-8 -*-
# r80a_points.py — 汇总 p1a..p6 复算点 + 转折面/渲染/条目支撑补充点 + 去重计数 + 六查补充直算事实
# 被 r80_final.py 导入(只读; 不写任何文件, 不调用引擎)
import os, re, datetime as dt
from r00_common import *

TOK = re.compile('(?<![A-Za-z0-9_])([A-Z][A-Z0-9_]{1,})(?![A-Za-z0-9_])')
SUF = ('_level', '_d12m', '_yoy', '_4w_avg', '_rv21', '_chg_3m', '_mean')
INFO_IDS = ('K02b', 'K04', 'Y43', 'Y46')


def cal_entries(o, out=None):
    out = [] if out is None else out
    if isinstance(o, dict):
        if 'entry_id' in o and 'first_publish_on_or_after' in o:
            out.append(o)
        for v in o.values():
            cal_entries(v, out)
    elif isinstance(o, list):
        for v in o:
            cal_entries(v, out)
    return out


def rows_of(lines):
    out = []
    rx = re.compile('^[|] *([0-9]+) *[|] *([0-9]{4}-[0-9]{2}) *[|] *([0-9.]+) *[|] *([0-9.]+) *[|]')
    for line in lines:
        m = rx.match(line)
        if m:
            out.append([int(m.group(1)), m.group(2), float(m.group(3)), float(m.group(4))])
    return out


def build(sn, rep, aj, cal, RAW, B, ERR):
    V = {}
    cut = D('2026-11-23')

    def lvl(sid, d):
        return sn.val(sid, D(d))

    def yy(sid, d):
        return yoy(sn, sid, D(d))

    def ym(d):
        return D(d).isoformat()[:7]

    # ---- 既有中间表 ----
    order = ['p1a.json', 'p1b.json', 'p2.json', 'p3.json', 'p4.json', 'p5.json', 'p6.json']
    ALL, EX = [], {}
    for fn in order:
        d = load(os.path.join(B, fn))
        for p in d['points']:
            p['_src'] = fn
            if fn == 'p5.json' and p['id'] == 'L05':
                continue
            ALL.append(p)
        for k, v in d.get('extra', {}).items():
            EX[k] = v
    ids = [p['id'] for p in ALL]
    if len(set(ids)) != len(ids):
        ERR.append('既有中间表编号重复: %s' % sorted(set(i for i in ids if ids.count(i) > 1)))
    bad = [p['id'] for p in ALL if not p['ok']]
    if bad:
        ERR.append('既有中间表偏离点: %s' % bad)

    NEW = []
    CAT = ['']

    def cat(c):
        CAT[0] = c

    def P(pid, where, key, comp, rep_, note='', tol=None):
        disp = r(comp, 6) if isinstance(comp, float) else comp
        ok = same(comp, rep_, tol)
        NEW.append({'id': pid, 'cat': CAT[0], 'where': where, 'key': key, 'computed': disp,
                    'reported': rep_, 'ok': bool(ok), 'note': note, '_src': 'r80'})
        return ok

    rp = rep['research_plan']
    pool = rp['turning_candidates']['candidates']
    tg = aj['reader_map']['turnings']
    bym = dict((c['metric_id'], c) for c in pool)

    # ---- G 转折面直算 ----
    cat('G 转折面直算')

    def k2(sid, d):
        return sn.key(sid, d) + ' ÷ ' + sn.key(sid, minus_year(d))

    c02, c05 = yy('CPI', '2026-02-01'), yy('CPI', '2026-05-01')
    P('G01', '转折表第 1 行 turnings[0].value_before「2026-02→2026-05 由 2.434 升至 4.1666」前值', k2('CPI', '2026-02-01'), c02, 2.434)
    P('G02', '转折表第 1 行 turnings[0].value_after 后值', k2('CPI', '2026-05-01'), c05, 4.1666)
    P('G03', 'turnings[0].narrative「三个月上行 1.7326 个百分点」', 'CPI 同比 2026-05 减 2026-02', c05 - c02, 1.7326)
    mx = max(pool, key=lambda c: abs(c['delta']))
    P('G04', 'turnings[0].first_mover「为候选池内最大单段变动」', 'report.json research_plan.turning_candidates.candidates 各行 delta 绝对值最大者', '%s:%s' % (mx['metric_id'], mx['delta']), 'CPI:1.7326')
    e02, e05 = lvl('EA_HICP_YOY', '2026-02-01'), lvl('EA_HICP_YOY', '2026-05-01')
    P('G05', 'turnings[0].follow_or_diverge「欧元区 EA_HICP_YOY 同月(2026-05)同步由 1.9 升至 3.2」前值', sn.key('EA_HICP_YOY', '2026-02-01'), e02, 1.9)
    P('G06', '同句后值 3.2', sn.key('EA_HICP_YOY', '2026-05-01'), e05, 3.2)
    P('G07', 'turnings[0].narrative「欧元区 HICP 同比同窗上行 1.3 个百分点」', 'EA_HICP_YOY 2026-05 减 2026-02', e05 - e02, 1.3)
    P('G08', '同句「其后欧元区读数 2026-06 回落至 2.8」', sn.key('EA_HICP_YOY', '2026-06-01'), lvl('EA_HICP_YOY', '2026-06-01'), 2.8)
    P('G09', '同句「2026-07 为 2.9」', sn.key('EA_HICP_YOY', '2026-07-01'), lvl('EA_HICP_YOY', '2026-07-01'), 2.9)
    e10 = lvl('EA_HICP_YOY', '2026-10-01')
    P('G10', '同句「2026-10 为 4.0」', sn.key('EA_HICP_YOY', '2026-10-01'), e10, 4.0)
    P('G11', '同句「越过 2026-05 的 3.2」', 'EA_HICP_YOY 2026-10 大于 2026-05', e10 > e05, True)
    ea26 = [(ym(d), v) for d, v in sn.series('EA_HICP_YOY') if D(d).year == 2026]
    V['ea_max_ym'] = max(ea26, key=lambda t: t[1])[0]
    P('G12', '传导环1「欧元区 2026-10 达 4.0、为年内新高」', 'series_store.EA_HICP_YOY 2026 年各月最大值所在月', V['ea_max_ym'], '2026-10')
    k02, k05, k08, k09 = (yy('CORE_CPI', '2026-%s-01' % m) for m in ('02', '05', '08', '09'))
    P('G13', 'turnings[0].narrative「核心口径…2026-02→2026-05 同比自 2.4725 升至 2.8229」前值', k2('CORE_CPI', '2026-02-01'), k02, 2.4725)
    P('G14', '同句后值', k2('CORE_CPI', '2026-05-01'), k05, 2.8229)
    P('G15', '同句「涨幅小于 headline」', 'CORE_CPI 同比三个月涨幅 小于 CPI 同比三个月涨幅', (k05 - k02) < (c05 - c02), True, note='核心 %+.4f / headline %+.4f' % (k05 - k02, c05 - c02))
    P('G16', 'turnings[0].narrative「CORE_CPI@2026-08(2026-05→2026-08 同比自 2.8229 回落至 2.4462」后值', k2('CORE_CPI', '2026-08-01'), k08, 2.4462)
    P('G17', '同句「其后 2026-09 回升至 2.5658」', k2('CORE_CPI', '2026-09-01'), k09, 2.5658)
    P('G18', '同句「该段晚于 headline 上行段」', 'report.json turning_candidates: CORE_CPI 窗起点 2026-05 不早于 CPI 窗终点 2026-05', bym['CORE_CPI']['from_date'] >= bym['CPI']['to_date'], True)
    i11, i02 = yy('INDPRO', '2025-11-01'), yy('INDPRO', '2026-02-01')
    P('G19', '转折表第 2 行 turnings[1]「2025-11→2026-02 由 1.7543 降至 0.7972」前值', k2('INDPRO', '2025-11-01'), i11, 1.7543)
    P('G20', '同句后值', k2('INDPRO', '2026-02-01'), i02, 0.7972)
    P('G21', '同句「三个月变动 -0.9571」', 'INDPRO 同比 2026-02 减 2025-11', i02 - i11, -0.9571)
    gr = [c for c in pool if c['dimension'] == 'growth']
    mg = max(gr, key=lambda c: abs(c['delta']))
    P('G22', '同句「为增长维候选池内最大的三个月变化」', 'report.json turning_candidates growth 维 delta 绝对值最大者', '%s:%s' % (mg['metric_id'], abs(mg['delta'])), 'INDPRO:0.9571', note='增长维候选 %s' % [(c['metric_id'], c['delta']) for c in gr])
    un11, un02 = lvl('UNEMPLOYMENT', '2025-11-01'), lvl('UNEMPLOYMENT', '2026-02-01')
    P('G23', '同句「同一窗口美国失业率由 4.5 降至 4.4(2026-02)」前值', sn.key('UNEMPLOYMENT', '2025-11-01'), un11, 4.5)
    P('G24', '同句后值', sn.key('UNEMPLOYMENT', '2026-02-01'), un02, 4.4)
    P('G25', '同句「就业端未同向走弱」(工业同比回落而失业率亦回落)', 'UNEMPLOYMENT 2026-02 低于 2025-11', un02 < un11, True)
    ipyo = []
    for d, v in sn.series('INDPRO'):
        if D('2025-11-01') <= D(d) <= D('2026-10-01') and D(d).day == 1:
            y = yoy(sn, 'INDPRO', d)
            if y is not None:
                ipyo.append((ym(d), y))
    V['ipyo'] = ipyo
    V['ip_trough'] = min(ipyo, key=lambda t: t[1])[0]
    P('G26', 'turnings[1].narrative「2026-03 见底后回升」', 'series_store.INDPRO 同比在 2025-11..2026-10 的最小值所在月', V['ip_trough'], '2026-03', note='%s' % ['%s:%.4f' % t for t in ipyo])
    P('G27', '同句「至 2026-10 为 2.15」', k2('INDPRO', '2026-10-01'), yy('INDPRO', '2026-10-01'), 2.15)
    j04, j06, j07 = (lvl('JP_POLICY_RATE', '2026-%s-01' % m) for m in ('04', '06', '07'))
    P('G28', '转折表第 3 行 turnings[2]「2026-04 0.727→2026-07 0.978(经 2026-06 0.841 过渡)」前值', sn.key('JP_POLICY_RATE', '2026-04-01'), j04, 0.727)
    P('G29', '同句过渡值 0.841', sn.key('JP_POLICY_RATE', '2026-06-01'), j06, 0.841)
    P('G30', '同句后值 0.978', sn.key('JP_POLICY_RATE', '2026-07-01'), j07, 0.978)
    jps = sn.series('JP_POLICY_RATE')
    steps = []
    for i in range(1, len(jps)):
        a, b = jps[i - 1], jps[i]
        if b[0].year == 2026 and b[0].month <= 10 and (b[1] - a[1]) >= 0.03 - 1e-12:
            steps.append((ym(b[0]), diff_bp(a[1], b[1]), a[1], b[1]))
    V['jp_steps_2026'] = steps
    P('G31', 'turnings[2].first_mover「为 2026 年内第三个上行月均台阶」', 'series_store.JP_POLICY_RATE 2026 年相邻月均差不小于 0.03 的台阶序位', [s[0] for s in steps].index('2026-07') + 1, 3, note='%s' % ['%s:%+.1fbp' % (s[0], s[1]) for s in steps])
    P('G32', '同句「此前: 2026-01 +17bp、2026-06 +11bp」', 'series_store.JP_POLICY_RATE 2026-01/2026-06 相邻月均差', '%s/%s' % tuple('%.0f' % s[1] for s in steps if s[0] in ('2026-01', '2026-06')), '17/11')
    j08, j09, j10 = (lvl('JP_POLICY_RATE', '2026-%s-01' % m) for m in ('08', '09', '10'))
    P('G33', 'turnings[2].narrative「此后续升(2026-09 1.043(+7bp)」值', sn.key('JP_POLICY_RATE', '2026-09-01'), j09, 1.043)
    P('G34', '同句 +7bp(较 2026-08 月均)', 'JP_POLICY_RATE 2026-09 减 2026-08', diff_bp(j08, j09), 7)
    P('G35', '同句「2026-10 1.227(+18bp)」值', sn.key('JP_POLICY_RATE', '2026-10-01'), j10, 1.227)
    P('G36', '同句 +18bp', 'JP_POLICY_RATE 2026-10 减 2026-09', diff_bp(j09, j10), 18)
    dims = {}
    for c in pool:
        if c['dimension'] not in dims or abs(c['delta']) > abs(dims[c['dimension']]['delta']):
            dims[c['dimension']] = c
    P('G37', '三转折=候选池增长/通胀/政策三维各自最大事件(通胀维美欧同窗计为同一事件,取美国 headline)', 'report.json turning_candidates 各维 delta 绝对值最大者', ' '.join('%s:%s' % (k, dims[k]['metric_id']) for k in ('inflation', 'growth', 'policy')), 'inflation:CPI growth:INDPRO policy:JP_POLICY_RATE')
    trip = ['%s@%s→%s' % (t['metric_id'], t['before_date'], t['date']) for t in tg]
    P('G38', '转折表三行的指标与窗口端点(2026-02..2026-05 / 2025-11..2026-02 / 2026-04..2026-07)', 'agent_judgment reader_map.turnings 各行 metric_id/before_date/date 对照 report.json turning_candidates', ','.join(trip), 'CPI@2026-02→2026-05,INDPRO@2025-11→2026-02,JP_POLICY_RATE@2026-04→2026-07')
    P('G39', 'turnings[1].narrative「窗口(2025-11→2026-02)止于通胀转折窗(2026-02→2026-05)的起点月份」', 'turnings[1].date 等于 turnings[0].before_date', tg[1]['date'] == tg[0]['before_date'], True)
    cpi26 = []
    for d, v in sn.series('CPI'):
        if D(d).year == 2026 and D(d).day == 1:
            y = yoy(sn, 'CPI', d)
            if y is not None:
                cpi26.append((ym(d), y))
    V['cpi26'] = cpi26
    V['cpi_max_ym'] = max(cpi26, key=lambda t: t[1])[0]
    P('G40', '传导环1「美国 CPI 同比 2026-09 回升至 3.72，仍低于 2026-05 高点 4.17」之年内高点所在月', 'series_store.CPI 同比 2026 年各月最大值所在月', V['cpi_max_ym'], '2026-05')
    eu = sn.win('EURUSD', D('2025-11-23'), cut)
    emin = min(eu, key=lambda t: t[1])
    P('G41', 'C1 竞争解释「欧元兑美元 2026-11-23 为 1.093972,近 12 个月窗最低」', 'series_store.EURUSD 12 个月窗(2025-11-23..2026-11-23)最小值', '%s@%s' % (emin[1], emin[0].isoformat()), '1.093972@2026-11-23')
    P('G42', 'C1 竞争解释「三个月(2026-08-19→2026-11-23)-5.52%」', '%s→%s' % (sn.key('EURUSD', '2026-08-19'), sn.key('EURUSD', '2026-11-23')), pct(lvl('EURUSD', '2026-08-19'), lvl('EURUSD', '2026-11-23')), -5.52)

    # ---- L 引擎渲染表(补充) ----
    cat('L 引擎渲染表')
    s6 = [s for s in rep['steps'] if s.get('step') == 'S6_analog'][0]['envelope']['data']
    V['s6'] = s6
    top = s6['top'][:5]
    eng = [[t['rank'], t['candidate_month'], r(t['distance'], 6), r(t['distance_percentile'], 4)] for t in top]
    rowsF = rows_of(RAW['FULL_REPORT.md'].split(chr(10)))
    rowsR = rows_of(RAW['report.md'].split(chr(10)))
    V['eng_top5'] = eng
    okF = len(rowsF) == 5 and all(a[0] == b[0] and a[1] == b[1] and abs(a[2] - b[2]) <= 5e-7 and abs(a[3] - b[3]) <= 1e-9 for a, b in zip(rowsF, eng))
    P('L09', 'FULL_REPORT.md「历史相似结构(引擎确定性面·读者版)」表 5 行(名次/候选月/距离/距离分位)与 report.json S6_analog 引擎面 top5 逐格一致', 'FULL_REPORT.md 历史相似结构表 对照 report.json steps[S6_analog].envelope.data.top', okF, True, note='渲染行 %s' % rowsF)
    okR = len(rowsR) == 5 and all(a[0] == b[0] and a[1] == b[1] and abs(a[2] - b[2]) <= 5e-7 and abs(a[3] - b[3]) <= 1e-9 for a, b in zip(rowsR, eng))
    P('L10', 'report.md 历史相似结构表 5 行与引擎面 top5 逐格一致', 'report.md 历史相似结构表 对照 report.json steps[S6_analog].envelope.data.top', okR, True, note='渲染行 %s' % rowsR)
    lF = [(i + 1, l) for i, l in enumerate(RAW['FULL_REPORT.md'].split(chr(10)))]
    V['full_expost_lines'] = sorted(set(i for i, l in lF if ('事后结果标注' in l or '更非预测' in l)))
    P('L11', 'FULL_REPORT.md 历史相似结构节「相似≠因果, 更非预测」「事后结果标注」「事后≠当时可知,事后≠预测」标注在场', 'FULL_REPORT.md 该节文本', all(k in ''.join(l for i, l in lF) for k in ('相似≠因果, 更非预测', '事后结果标注', '事后≠当时可知,事后≠预测')), True, note='行 %s' % V['full_expost_lines'])
    ml = RAW['MAP_REPORT.md'].split(chr(10))
    i0 = [i for i, l in enumerate(ml) if l.startswith('## 历史上结构最像的时期')][0]
    i1 = [i for i, l in enumerate(ml) if l.startswith('## ') and i > i0][0]
    sect = ml[i0:i1]
    V['map_analog_section'] = (i0 + 1, i1)
    hn = [v for p, v in find_keys(aj, 'history_zero_case_note')]
    V['history_zero_case_note'] = hn[0] if hn else ''
    P('L12', 'MAP_REPORT.md「历史上结构最像的时期」节为零段类比: 节内无候选行,且「零段类比」「事后结果≠当时可知」「相似≠因果≠预测」在场(与判断档 history_zero_case_note 同口径)', 'MAP_REPORT.md 该节文本 / agent_judgment.json reader_map.history_zero_case_note', (len(rows_of(sect)) == 0 and all(k in ''.join(sect) for k in ('零段类比', '事后结果≠当时可知', '相似≠因果≠预测')) and all(k in V['history_zero_case_note'] for k in ('事后结果≠当时可知', '相似≠因果≠预测'))), True, note='节为 MAP_REPORT.md 第 %d–%d 行' % (i0 + 1, i1))

    # ---- M 条目支撑 ----
    cat('M 条目支撑')
    u, u0819, u1023 = lvl('USDJPY', '2026-11-23'), lvl('USDJPY', '2026-08-19'), lvl('USDJPY', '2026-10-23')
    le21 = sn.le('USDJPY', D('2026-08-23'))
    V['usdjpy'] = dict(u=u, u0819=u0819, u1023=u1023, le21=le21)
    P('M1a', 'M1 环3「三个月 2026-08-19→2026-11-23 为 -0.13%」', '%s→%s' % (sn.key('USDJPY', '2026-08-19'), sn.key('USDJPY', '2026-11-23')), pct(u0819, u), -0.13)
    P('M1b', 'M1 环3「按 3 个月前锚 2026-08-23 的最近观测 2026-08-21 起算为 +0.29%%」(窗启日=%s)' % le21[0].isoformat(),'%s→%s' % (sn.key('USDJPY', le21[0]), sn.key('USDJPY', '2026-11-23')), pct(le21[1], u), 0.29)
    P('M1c', 'M1 环3「近一月(2026-10-23→2026-11-23)不降反升 1.82%」', '%s→%s' % (sn.key('USDJPY', '2026-10-23'), sn.key('USDJPY', '2026-11-23')), pct(u1023, u), 1.82)
    P('M2a', '总判断「其后至截止日的 24 天」', '2026-10-30→2026-11-23 日数', (cut - D('2026-10-30')).days, 24)
    P('M3a', 'C3 竞争解释「本次 2026-10 月均 1.227 较目标水平 1.25 低 0.023」', '1.25 减 series_store.JP_POLICY_RATE 2026-10-01', 1.25 - j10, 0.023)
    x07, x09, x10 = lvl('INDPRO', '2026-07-01'), lvl('INDPRO', '2026-09-01'), lvl('INDPRO', '2026-10-01')
    b07, b10 = lvl('INDPRO', '2025-07-01'), lvl('INDPRO', '2025-10-01')
    P('M4a', '走位对照(regions[US].from_to)「指数水平 103.1675→103.3954，仅 +0.22%」', '%s→%s' % (sn.key('INDPRO', '2026-07-01'), sn.key('INDPRO', '2026-10-01')), pct(x07, x10), 0.22)
    P('M4b', '同句「其中 2026-10 环比 -0.43%」', '%s→%s' % (sn.key('INDPRO', '2026-09-01'), sn.key('INDPRO', '2026-10-01')), pct(x09, x10), -0.43)
    P('M4c', '同句「同比抬升含基数效应: 上年 2025-07→2025-10 基数下行 0.66%」', '%s→%s' % (sn.key('INDPRO', '2025-07-01'), sn.key('INDPRO', '2025-10-01')), pct(b07, b10), -0.66)
    P('M4d', '同段「失业率 4.1%(2026-07)至 4.1%(2026-10)两锚持平(中间 2026-09 为 4.2)」中间值', sn.key('UNEMPLOYMENT', '2026-09-01'), lvl('UNEMPLOYMENT', '2026-09-01'), 4.2)

    V['g'] = dict(c02=c02, c05=c05, e02=e02, e05=e05, k02=k02, k05=k05, j04=j04, j06=j06, j07=j07, j08=j08, j09=j09, j10=j10)
    V['jp_first'] = sn.first('JP_POLICY_RATE')[0].isoformat()
    V['jp_last'] = sn.last('JP_POLICY_RATE')[0].isoformat()

    # ---- 六查补充直算事实(信息项, 不入计数) ----
    Z = []

    def Zf(name, key, val):
        Z.append({'name': name, 'key': key, 'value': val})

    mo = ('05', '06', '07', '08', '09', '10')
    cpi = dict((m, yy('CPI', '2026-%s-01' % m)) for m in mo)
    cc = dict((m, yy('CORE_CPI', '2026-%s-01' % m)) for m in mo)
    ea = dict((m, lvl('EA_HICP_YOY', '2026-%s-01' % m)) for m in ('02', '05', '06', '07', '08', '09', '10'))
    V['cpi'], V['cc'], V['ea'] = cpi, cc, ea
    Zf('美国 CPI 同比 2026-05..2026-10(严格同基期)', 'series_store.CPI 各月 ÷ 上年同月', '; '.join('%s:%s' % (m, 'NA' if cpi[m] is None else '%.4f' % cpi[m]) for m in mo))
    Zf('美国 CORE_CPI 同比 2026-05..2026-10', 'series_store.CORE_CPI 各月 ÷ 上年同月', '; '.join('%s:%s' % (m, 'NA' if cc[m] is None else '%.4f' % cc[m]) for m in mo))
    Zf('欧元区 EA_HICP_YOY 2026-02..2026-10', 'series_store.EA_HICP_YOY', '; '.join('%s:%s' % (m, ea[m]) for m in ('02', '05', '06', '07', '08', '09', '10')))
    Zf('2026-09 欧元区减美国 CPI 同比(pp)', 'series_store.EA_HICP_YOY 2026-09-01 减 CPI 同比 2026-09', '%.4f' % (ea['09'] - cpi['09']))
    ip = dict((m, yy('INDPRO', '2026-%s-01' % m)) for m in mo)
    V['ip'] = ip
    Zf('美国 INDPRO 同比 2026-05..2026-10', 'series_store.INDPRO 各月 ÷ 上年同月', '; '.join('%s:%s' % (m, 'NA' if ip[m] is None else '%.4f' % ip[m]) for m in mo))
    x07, x09, x10 = lvl('INDPRO', '2026-07-01'), lvl('INDPRO', '2026-09-01'), lvl('INDPRO', '2026-10-01')
    b07, b10 = lvl('INDPRO', '2025-07-01'), lvl('INDPRO', '2025-10-01')
    V['ipx'] = dict(x07=x07, x09=x09, x10=x10, b07=b07, b10=b10)
    Zf('INDPRO 指数水平三个月变化 2026-07→2026-10', '%s→%s' % (sn.key('INDPRO', '2026-07-01'), sn.key('INDPRO', '2026-10-01')), '%s→%s = %+.4f%%' % (x07, x10, pct(x07, x10)))
    Zf('INDPRO 基期指数变化 2025-07→2025-10', '%s→%s' % (sn.key('INDPRO', '2025-07-01'), sn.key('INDPRO', '2025-10-01')), '%s→%s = %+.4f%%' % (b07, b10, pct(b07, b10)))
    Zf('INDPRO 最新单月环比 2026-09→2026-10', '%s→%s' % (sn.key('INDPRO', '2026-09-01'), sn.key('INDPRO', '2026-10-01')), '%s→%s = %+.4f%%' % (x09, x10, pct(x09, x10)))
    V['un'] = dict(a=lvl('UNEMPLOYMENT', '2026-07-01'), b=lvl('UNEMPLOYMENT', '2026-10-01'))
    V['gdp'] = dict(a=yy('US_REAL_GDP', '2026-04-01'), b=yy('US_REAL_GDP', '2026-07-01'))
    V['eagdp'] = dict(a=lvl('EA_REAL_GDP_YOY', '2026-04-01'), b=lvl('EA_REAL_GDP_YOY', '2026-07-01'))
    Zf('走位对照: 失业率 / 美国 GDP 同比 / 欧元区 GDP 同比(3 个月前→最新)', 'series_store.UNEMPLOYMENT, US_REAL_GDP(同比), EA_REAL_GDP_YOY 2026-04-01→2026-07-01', '%s→%s / %.2f→%.2f / %s→%s' % (V['un']['a'], V['un']['b'], V['gdp']['a'], V['gdp']['b'], V['eagdp']['a'], V['eagdp']['b']))
    V['pce09'] = yy('CORE_PCE', '2026-09-01')
    V['tips'] = lvl('TIPS_10Y', '2026-11-19')
    V['bei'] = lvl('BEI_10Y', '2026-11-20')
    V['bei1119'] = lvl('BEI_10Y', '2026-11-19')
    V['bei0821'] = sn.le('BEI_10Y', D('2026-08-23'))
    Zf('情景相容性读数: CORE_PCE 同比 2026-09 / TIPS_10Y 2026-11-19 / BEI_10Y 2026-11-20', 'series_store.CORE_PCE(同比), TIPS_10Y, BEI_10Y', '%.4f / %s / %s' % (V['pce09'], V['tips'], V['bei']))
    Zf('传导环1 窗启日稳健性: BEI_10Y 自 3 个月前锚最近观测起算至 2026-11-19', '%s→%s' % (sn.key('BEI_10Y', V['bei0821'][0]), sn.key('BEI_10Y', '2026-11-19')), '%s→%s = %+.1fbp' % (V['bei0821'][1], V['bei1119'], diff_bp(V['bei0821'][1], V['bei1119'])))
    bm = EX.get('bei_feb_may') or {}
    V['bm'] = bm
    Zf('BEI_10Y 三个月窗 2026-02→2026-05 的窗端点与窗内极值', 'series_store.BEI_10Y 2026-02-01..2026-05-31', bm)
    jpc = EX.get('jp_cpi_yoy_store') or {}
    V['jpc'] = jpc
    Zf('序列库内 JP_CPI_YOY(未入本问证据索引)2026-02..2026-10', 'series_store.JP_CPI_YOY', jpc)
    Zf('JP_POLICY_RATE 相邻月均差介于 0.001–0.03 的月份(全序列)', 'series_store.JP_POLICY_RATE; 序列起 %s 止 %s' % (sn.first('JP_POLICY_RATE')[0].isoformat(), sn.last('JP_POLICY_RATE')[0].isoformat()), '%d 个月, 最后一个 %s' % (len(EX.get('jp_mid_diffs_all') or []), (EX.get('jp_mid_diffs_all') or ['无'])[-1]))
    ev = rep.get('evidence_index') or []
    eids = [e.get('metric_id') for e in ev if isinstance(e, dict)]
    V['ev'] = dict(n=len(eids), jpin=[i for i in eids if i and i.startswith('JP_CPI')], eabe=[i for i in eids if i and ('BEI' in i or 'INFL' in i or 'EXP' in i)], jp=[i for i in eids if i and i.startswith('JP_')], pol=[i for i in eids if i in ('DFEDTARU', 'DFEDTARL', 'DFF', 'ECB_DFR', 'ECB_MRO', 'FED_FUNDS')], ea=[i for i in eids if i and i.startswith('EA_')])
    Zf('证据索引(report.json evidence_index)行数与相关序列', 'report.json evidence_index[*].metric_id', V['ev'])
    ce = cal_entries(cal)
    pub = sorted('%s@%s' % (e['entry_id'], str(e.get('first_publish_on_or_after'))[:10]) for e in ce if D('2026-10-30') < D(e.get('first_publish_on_or_after')) <= cut)
    boj = sorted('%s@%s' % (e['entry_id'], str(e.get('first_publish_on_or_after'))[:10]) for e in ce if 'BOJ' in e['entry_id'])
    V['cal'] = dict(n=len(ce), pub=pub, boj=boj, ver=cal.get('version') if isinstance(cal, dict) else None)
    Zf('冻结发布日历: 条目总数 / 2026-10-31..2026-11-23 已发布条目 / 日本央行条目', 'root_overlay/config/release_calendar.json entries', V['cal'])
    zk = find_keys(s6, 'BEI_10Y_level')
    V['z_bei'] = (zk[0][1].get('z') if zk and isinstance(zk[0][1], dict) else None)
    V['cand'] = s6.get('candidates')
    V['anchor'] = s6.get('anchor_month')
    Zf('历史相似面: 锚点月 / 候选池计数 / 锚点 BEI_10Y_level 的 z', 'report.json steps[S6_analog].envelope.data(anchor_month, candidates, state_vector)', '%s / %s / %s' % (V['anchor'], V['cand'], V['z_bei']))

    # ---- 合并与去重 ----
    ALLP = ALL + NEW
    nids = [p['id'] for p in ALLP]
    if len(set(nids)) != len(nids):
        ERR.append('合并后编号重复: %s' % sorted(set(i for i in nids if nids.count(i) > 1)))
    SIDS = set(sn.ids())
    COUNTED, INFOP, DUPP = [], [], []
    seen = []
    for p in ALLP:
        p['_cls'] = 'counted'
        p['_sig'] = None
        p['_toks'] = set()
        if p['id'] in INFO_IDS:
            p['_cls'] = 'info'
            INFOP.append(p)
            continue
        rv = p['reported']
        if isinstance(rv, (int, float)) and not isinstance(rv, bool):
            text = str(p['key']) + ' ' + str(p['where'])
            toks = set(t for t in TOK.findall(text) if t in SIDS)
            for t in TOK.findall(text):
                for s in SUF:
                    if t.endswith(s) and t[:-len(s)] in SIDS:
                        toks.add(t[:-len(s)])
            p['_sig'] = '%.10g' % float(rv)
            p['_toks'] = toks
            for q in seen:
                if q['_sig'] == p['_sig'] and (toks & q['_toks']):
                    p['_cls'] = 'dup'
                    p['_dup_of'] = q['id']
                    DUPP.append(p)
                    break
        if p['_cls'] == 'counted':
            COUNTED.append(p)
            seen.append(p)
    badn = [p['id'] for p in NEW if not p['ok']]
    if badn:
        ERR.append('新增点偏离: %s' % badn)
    return dict(ALL=ALL, NEW=NEW, ALLP=ALLP, EX=EX, Z=Z, V=V, COUNTED=COUNTED, INFOP=INFOP, DUPP=DUPP)
