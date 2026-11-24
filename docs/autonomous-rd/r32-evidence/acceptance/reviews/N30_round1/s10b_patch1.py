import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
L = s.split(chr(10))
def rep(pred, new):
    idx = [i for i, x in enumerate(L) if pred(x)]
    assert len(idx) == 1, (len(idx), new[:40])
    L[idx[0]] = new
NL = chr(10)
rep(lambda x: x.startswith("o('⑥', '引擎候选 EA_HICP 2026-02→05"), "tieE = [x for x in best3(EA) if abs(x[4] - BE[4]) < 1e-9]" + NL + "o('⑥', '引擎候选 EA_HICP 2026-02→05 属 |三个月变化| 最大者集合(并列最大集合直算)', ('2026-02', '2026-05') in [(x[0], x[1]) for x in tieE], tieE)" + NL + "c.diag.append('EA 并列最大集合: ' + str(tieE))")
rep(lambda x: x.startswith("for m, bb in [(EA, BE), (JP, BJ), (TK, BT), (PR, BP)]:"), "for m, bb in [(EA, ('2026-02', '2026-05', 1.9, 3.2, 1.3)), (JP, BJ), (TK, BT), (PR, BP)]:")
rep(lambda x: x.startswith("n('⑥', 'JP−EA 2026-09 期水平差'"), "n('⑥', 'JP−EA 2026-09 期水平差绝对值', abs(c.mv(JP, '2026-09') - c.mv(EA, '2026-09')), 1.64, '1.64', '全国口径 -1.64、东京口径 -1.11', tol=0.006)" + NL + "o('⑥', '方向: 2026-09 期日本全国低于欧元区', c.mv(JP, '2026-09') < c.mv(EA, '2026-09'), round(c.mv(JP, '2026-09') - c.mv(EA, '2026-09'), 3))" + NL + "n('⑥', 'EA−东京 2026-09 期水平差', c.mv(EA, '2026-09') - c.mv(TK, '2026-09'), 1.11, '1.11', '东京口径 -1.11', tol=0.006)")
rep(lambda x: x.startswith("n('⑦', 'EURUSD 10-23→11-20 %'"), "n('⑦', 'EURUSD 10-23→11-20 %', abs(pc('EURUSD', W0, W1)), 2.24, '2.24', '降至 1.0970(-2.24%)', tol=0.006)" + NL + "o('⑦', 'EURUSD 10-23→11-20 方向=下降', pc('EURUSD', W0, W1) < 0, round(pc('EURUSD', W0, W1), 3))")
rep(lambda x: x.startswith("n('⑦', 'EURUSD 10-23→11-23 %'"), "n('⑦', 'EURUSD 10-23→11-23 %', abs(pc('EURUSD', W0, A)), 2.51, '2.51', 'EURUSD 1.0940(-2.51%)', tol=0.006)" + NL + "o('⑦', 'EURUSD 10-23→11-23 方向=下降', pc('EURUSD', W0, A) < 0, round(pc('EURUSD', W0, A), 3))")
rep(lambda x: x.startswith("n('⑦', 'EURJPY 合成 10-23→11-20 %'"), "n('⑦', 'EURJPY 合成 10-23→11-20 %', abs(pct(ej0, ej1)), 0.24, '0.24', '175.19(-0.24%)', tol=0.006)" + NL + "o('⑦', 'EURJPY 合成 10-23→11-20 方向=下降', pct(ej0, ej1) < 0, round(pct(ej0, ej1), 3))")
rep(lambda x: x.startswith("n('⑦', 'EURJPY 合成 10-23→11-23 %'"), "n('⑦', 'EURJPY 合成 10-23→11-23 %', abs(pct(ej0, ej2)), 0.73, '0.73', '174.32(较 10-23 -0.73%)', tol=0.006)" + NL + "o('⑦', 'EURJPY 合成 10-23→11-23 方向=下降', pct(ej0, ej2) < 0, round(pct(ej0, ej2), 3))")
rep(lambda x: x.startswith("n('⑦', '资产月窗 SPX chg_pct"), "n('⑦', '资产月窗 SPX chg_pct 10-23→11-23', abs(pc('SPX', W0, A)), 5.51, '5.51', 'SPX -5.51%(7203.85,盘中)', tol=0.006)")
rep(lambda x: x.startswith("n('⑦', '资产月窗 NIKKEI225 chg_pct"), "n('⑦', '资产月窗 NIKKEI225 chg_pct 10-23→11-20', abs(pc('NIKKEI225', W0, W1)), 9.98, '9.98', 'NIKKEI225 -9.98%(56436.65,2026-11-20 收盘)', tol=0.006)")
rep(lambda x: x.startswith("n('⑦', 'VIX 11-20 收盘→11-23 盘中 %'"), "n('⑦', 'VIX 11-20 收盘→11-23 盘中 %', abs(pc('VIX', W1, A)), 24.7, '24.7', '较 2026-11-20 收盘 -24.7%', tol=0.06)")
rep(lambda x: x.startswith("n('⑦', 'VIX 11-05→11-11 %'"), "n('⑦', 'VIX 11-05→11-11 %', abs(pc('VIX', '2026-11-05', '2026-11-11')), 37.93, '37.93', '较 11-05 -37.93%', tol=0.006)")
rep(lambda x: x.startswith("n('⑦', 'SPX 11-05 单日 %'"), "n('⑦', 'SPX 11-05 单日 %', abs(pc('SPX', '2026-11-04', '2026-11-05')), 4.36, '4.36', '同期 SPX 11-05 -4.36%', tol=0.006)")
rep(lambda x: x.startswith("n('⑦', 'NIKKEI225 11-06 单日 %'"), "n('⑦', 'NIKKEI225 11-06 单日 %', abs(pc('NIKKEI225', '2026-11-05', '2026-11-06')), 5.96, '5.96', '下一交易日 NIKKEI225 11-06 -5.96%', tol=0.006)" + NL + "o('⑦', '负号方向: SPX 月窗/NIKKEI 月窗/VIX 11-20→11-23/VIX 11-05→11-11/SPX 11-05/NIKKEI 11-06 均为负', all(x < 0 for x in [pc('SPX', W0, A), pc('NIKKEI225', W0, W1), pc('VIX', W1, A), pc('VIX', '2026-11-05', '2026-11-11'), pc('SPX', '2026-11-04', '2026-11-05'), pc('NIKKEI225', '2026-11-05', '2026-11-06')]), [round(x, 3) for x in [pc('SPX', W0, A), pc('NIKKEI225', W0, W1), pc('VIX', W1, A), pc('VIX', '2026-11-05', '2026-11-11'), pc('SPX', '2026-11-04', '2026-11-05'), pc('NIKKEI225', '2026-11-05', '2026-11-06')]])")
rep(lambda x: x.startswith("    sn = dd + ' ' + str(v) + '→'"), "    sn = dd + ' ' + ('%.2f' % v) + '→' if dd != '11-20' else '11-20 35.89,跳升集中于末五个交易日'")
rep(lambda x: x.startswith("o('⑦', '末六个交易日收盘路径"), "o('⑦', '末六个交易日收盘路径=11-13..11-20(截止日前的最后六个观测; 11-21/22 为周末, 11-23 为截止日盘中)', vd == [d for d in sorted(c.S['VIX']['dates']) if d < A][-6:], [d for d in sorted(c.S['VIX']['dates']) if d < A][-6:]])")
rep(lambda x: x.startswith("n('⑥', TK + '@2026-04'"), "n('⑥', TK + '@2026-04', c.mv(TK, '2026-04'), 1.42, '1.42', '由6个月前锚观测月 2026-04 的 1.42% 升至最新一期锚观测月 2026-10 的 2.73%')" + NL + "n('⑥', TK + '@2026-10', c.mv(TK, '2026-10'), 2.73, '2.73', '1.42% 升至最新一期锚观测月 2026-10 的 2.73%')")
rep(lambda x: x.startswith("o('⑥', 'JP_CPI_YOY 全序列最高值位置"), "o('⑥', 'JP_CPI 2025-01 为 2024-01 以来最高且为局部高点(全序列最高为 2023-01 的 4.31, 高于 2025-01; 文称「2025-01 高点 4.03」未称全序列最高)', max([(v, ym) for ym, v in mlist(JP) if ym >= '2024-01']) == (4.03, '2025-01') and c.mv(JP, '2024-12') < 4.03 and c.mv(JP, '2025-02') < 4.03, {'2024-12': c.mv(JP, '2024-12'), '2025-01': c.mv(JP, '2025-01'), '2025-02': c.mv(JP, '2025-02'), 'allmax': max([(v, ym) for ym, v in mlist(JP)])})" + NL + "c.diag.append('JP_CPI 2024-10..2026-04: ' + str([(ym, v) for ym, v in mlist(JP) if '2024-10' <= ym <= '2026-04']))" + NL + "c.diag.append('JP_CPI 各年末与基期拼接邻月 2025-07..2026-01: ' + str([(ym, v) for ym, v in mlist(JP) if '2025-07' <= ym <= '2026-01']))")
open(p, 'w', encoding='utf-8').write(NL.join(L))
print('patched lines', len(L))
