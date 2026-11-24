# s10e_patch1.py <s10e_final.py>  -- patch: evidence for 6 unmapped dates + fix ECB previous-change index + window-inclusion checks
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
a = "chm[-2][0], '2025-06-11', '2025-06-11', '自 2025-06-11 至 2026-06-17 维持 2.15/2.0 共 371')"
b = "([x for x in chm if x[0] < wm_[0][0]][-1][0]), '2025-06-11', '2025-06-11', '自 2025-06-11 至 2026-06-17 维持 2.15/2.0 共 371')"
assert s.count(a) == 1
s = s.replace(a, b)
a2 = "for d in vix['dates']:\n    if '2026-11-04' <= d <= A and d not in EVD:"
b2 = """ev('2026-05-01', c.md(EA, '2026-05'), 'series_store.EA_HICP_YOY 2026-05 期观测日(月初); JP_CPI_YOY 同月观测日=' + str(c.md(JP, '2026-05')))
ev('2026-05-16', c.pub(EA, '2026-04'), '推定发布规则 EA 月末+16 (2026-04 期)')
ev('2026-05-20', c.pub(JP, '2026-04'), '推定发布规则 全国CPI 月末+20 (2026-04 期)')
ev('2026-06-16', c.pub(EA, '2026-05'), '推定发布规则 EA 月末+16 (2026-05 期)')
ev('2026-06-20', c.pub(JP, '2026-05'), '推定发布规则 全国CPI 月末+20 (2026-05 期)')
ev('2026-10-20', RP['us_rates_trio']['window']['from'], 'us_rates_trio.window.from(三利率分解窗起); 判断档 rates_decomposition.window_from 应同值')
c.ok('E-日期', 'rates_decomposition.window_from == us_rates_trio.window.from', c.aj['reader_map']['rates_decomposition']['window_from'] == RP['us_rates_trio']['window']['from'], (c.aj['reader_map']['rates_decomposition']['window_from'], RP['us_rates_trio']['window']['from']))
c.ok('E-日期', 'rates_decomposition.window_to == us_rates_trio.window.to', c.aj['reader_map']['rates_decomposition']['window_to'] == RP['us_rates_trio']['window']['to'], (c.aj['reader_map']['rates_decomposition']['window_to'], RP['us_rates_trio']['window']['to']))
c.txt('E-日期', '推定发布日 2026-05-16 的星期', wd('2026-05-16'), '周六', '周六', '发布 2026-05-16,周六')
W0 = RP['question_window']['windows'][0]['from']
for m_, nm_ in ((EA, '欧元区'), (JP, '日本')):
    inwin = all(W0 <= c.md(m_, ym) <= A and W0 <= c.pub(m_, ym) <= A for ym in ('2026-06', '2026-07', '2026-08', '2026-09', '2026-10'))
    c.ok('E-日期', nm_ + ' 2026-06..2026-10 各期观测日与推定发布日均在窗内; 2026-05 期观测日早于窗起而推定发布日在窗内', inwin and c.md(m_, '2026-05') < W0 <= c.pub(m_, '2026-05'), (c.md(m_, '2026-05'), c.pub(m_, '2026-05')))
for d in vix['dates']:
    if '2026-11-04' <= d <= A and d not in EVD:"""
assert s.count(a2) == 1
s = s.replace(a2, b2)
open(p, 'w', encoding='utf-8').write(s)
print('patched')
