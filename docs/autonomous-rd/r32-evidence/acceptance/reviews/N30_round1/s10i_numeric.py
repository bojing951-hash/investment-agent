# s10i_numeric.py <snap> <rep> <cal> <reg> <aj> <out> -- every numeric JSON field of the judgment recomputed from the read-only face
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:7])
SEC = 'N'; A = c.aj
links = A['l3']['mechanism_chains'][0]['links']
for i, l in enumerate(links):
    c.eq(SEC, 'l3.mechanism_chains[0].links[' + str(i) + '].step', i + 1, l.get('step'), '环序号=列表序+1')
def chg(m, a, b):
    va = c.at(m, a); vb = c.at(m, b)
    return float('%f' % ((vb / va - 1.0) * 100.0))
for e in A['reader_map']['asset_returns_echo']:
    m = e['metric_id']; w = e['window']
    try:
        comp = round(chg(m, w['from'], w['to']), 2)
    except Exception as ex:
        comp = 'ERR ' + str(ex)
    c.eq(SEC, 'series_store.' + m + ' @' + w['from'] + '→' + w['to'] + ' 同口径变动%', comp, e['chg_pct'], 'reader_map.asset_returns_echo ' + m)
    c.eq(SEC, 'asset_returns_echo ' + m + ' window_months', 1, e['window_months'])
    c.eq(SEC, '资产月窗起(窗末=截止日 2026-11-23 的一个月前)', '2026-10-23', w['from'], m)
    c.eq(SEC, 'series_store.' + m + ' 最后观测日(不晚于截止日)', c.last(m)[0], w['to'], m)
rd = A['reader_map']['rates_decomposition']; ut = c.rep['research_plan']['us_rates_trio']
bp = {}
for k in ('UST_10Y', 'TIPS_10Y', 'BEI_10Y'):
    bp[k] = float('%f' % (round((c.at(k, rd['window_to']) - c.at(k, rd['window_from'])) * 100, 3)))
c.diag.append('rates bp direct ' + json.dumps(bp))
c.eq(SEC, 'series_store UST_10Y ' + rd['window_from'] + '→' + rd['window_to'] + ' 变动bp', bp['UST_10Y'], rd['nominal_bp'])
c.eq(SEC, 'series_store TIPS_10Y 同窗变动bp', bp['TIPS_10Y'], rd['real_bp'])
c.eq(SEC, 'series_store BEI_10Y 同窗变动bp', bp['BEI_10Y'], rd['bei_bp'])
c.eq(SEC, '名义=实际+盈亏平衡 恒等残差bp(判断档值)', float('%f' % (rd['nominal_bp'] - rd['real_bp'] - rd['bei_bp'])), 0.0)
c.eq(SEC, '名义−实际−盈亏平衡 残差bp(直算)', float('%f' % (bp['UST_10Y'] - bp['TIPS_10Y'] - bp['BEI_10Y'])), 0.0)
c.eq(SEC, 'us_rates_trio.window == reader_map.rates_decomposition 窗', [ut['window']['from'], ut['window']['to']], [rd['window_from'], rd['window_to']])
c.eq(SEC, 'UST_10Y@窗末 == TIPS_10Y@窗末 + BEI_10Y@窗末', float('%f' % (c.at('TIPS_10Y', rd['window_to']) + c.at('BEI_10Y', rd['window_to']))), c.at('UST_10Y', rd['window_to']))
c.diag.append('levels at to ' + json.dumps({k: c.at(k, rd['window_to']) for k in bp}))
for t in A['reader_map']['turnings']:
    m = t['metric_id']
    c.eq(SEC, 'series_store.' + m + '@' + t['before_date'], c.mv(m, t['before_date']), t['value_before'], 'turnings value_before')
    c.eq(SEC, 'series_store.' + m + '@' + t['date'], c.mv(m, t['date']), t['value_after'], 'turnings value_after')
ne = 0
for r in A['reader_map']['regions']:
    for e in r.get('anchor_echo', []):
        ne += 1
        c.eq(SEC, 'series_store.' + e['metric_id'] + '@' + str(e['observation_month']), c.mv(e['metric_id'], e['observation_month']), e['value'], 'anchor_echo ' + str(e.get('anchor')))
        c.eq(SEC, 'anchor_echo ' + e['metric_id'] + ' 键集', sorted(e.keys()), ['anchor', 'metric_id', 'observation_month', 'value'])
NUM = []
def walk(o):
    if isinstance(o, dict):
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
    elif isinstance(o, (int, float)) and not isinstance(o, bool): NUM.append(o)
walk(A)
c.diag.append('numeric leaves ' + str(len(NUM)) + ' = step ' + str(len(links)) + ' + echo(chg_pct, window_months) ' + str(2 * len(A['reader_map']['asset_returns_echo'])) + ' + rates 3 + turnings ' + str(2 * len(A['reader_map']['turnings'])) + ' + anchor ' + str(ne))
assert len(NUM) == len(links) + 2 * len(A['reader_map']['asset_returns_echo']) + 3 + 2 * len(A['reader_map']['turnings']) + ne
c.save('i')
