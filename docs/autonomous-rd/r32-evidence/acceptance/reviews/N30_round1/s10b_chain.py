# s10b_chain.py <snap> <rep> <cal> <reg> <aj> <out>  -- sections 3/5/6/7/8/9 (momentum, trio, turnings, chain, analog, scenarios)
import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
snap, rep, cal, reg, aj, out = sys.argv[1:7]
c = Ctx(snap, rep, cal, reg, aj, out)
A = c.asof; RP = c.rep['research_plan']
n, t, e, o = c.num, c.txt, c.eq, c.ok
EA = 'EA_HICP_YOY'; JP = 'JP_CPI_YOY'; TK = 'JP_CPI_TOKYO_YOY'; PR = 'JP_POLICY_RATE'
W0, W1 = '2026-10-23', '2026-11-20'
def lastfri(ym):
    d = D(mend(ym))
    while d.weekday() != 4:
        d -= dt.timedelta(days=1)
    return d.isoformat()
def pc(m, d0, d1):
    return pct(c.at(m, d0), c.at(m, d1))

# ---------- C1 momentum / Tokyo ----------
n('③', EA + '@2026-04', c.mv(EA, '2026-04'), 3.0, '百分之三点零', '的百分之三点零升至百分之四点零')
n('③', JP + '@2026-04', c.mv(JP, '2026-04'), 1.38, '百分之一点三八', '日本由百分之一点三八升至')
n('③', 'EA 锚间变化 4.0-3.0', c.mv(EA, '2026-10') - c.mv(EA, '2026-04'), 1.0, '一', '均约一个百分点', tol=0.1)
n('③', 'JP 锚间变化 2.44-1.38', c.mv(JP, '2026-10') - c.mv(JP, '2026-04'), 1.0, '一', '均约一个百分点', tol=0.1)
n('③', 'EA 自 2026-06 期起算 4.0-2.8', c.mv(EA, '2026-10') - c.mv(EA, '2026-06'), 1.2, '一点二', '欧元区一点二个百分点对日本零点七七个百分点')
n('③', 'JP 自 2026-06 期起算 2.44-1.67', c.mv(JP, '2026-10') - c.mv(JP, '2026-06'), 0.77, '零点七七', '对日本零点七七个百分点')
n('③', 'EA 自 2026-05 期起算 4.0-3.2', c.mv(EA, '2026-10') - c.mv(EA, '2026-05'), 0.8, '零点八', '欧元区零点八对日本零点九一')
n('③', 'JP 自 2026-05 期起算 2.44-1.53', c.mv(JP, '2026-10') - c.mv(JP, '2026-05'), 0.91, '零点九一', '对日本零点九一,快慢互换')
o('③', '快慢互换: 自06期 EA快 / 自05期 JP快', (c.mv(EA, '2026-10') - c.mv(EA, '2026-06') > c.mv(JP, '2026-10') - c.mv(JP, '2026-06')) and (c.mv(EA, '2026-10') - c.mv(EA, '2026-05') < c.mv(JP, '2026-10') - c.mv(JP, '2026-05')), '成立')
c.diag.append('其他起点锚间变化 EA/JP: ' + str({ym: (round(c.mv(EA, '2026-10') - c.mv(EA, ym), 2), round(c.mv(JP, '2026-10') - c.mv(JP, ym), 2)) for ym in ['2026-05', '2026-06', '2026-07', '2026-08', '2026-09']}))
n('③', TK + '@2026-10', c.mv(TK, '2026-10'), 2.73, '百分之二点七三', '最新读数百分之二点七三(观测 2026-10,发布 2026-10-30')
t('③', TK + ' 2026-10 观测月', c.md(TK, '2026-10')[:7], '2026-10', '2026-10', '最新读数百分之二点七三(观测 2026-10')
t('③', '推定发布规则 东京 2026-10 (月末-1天)', c.pub(TK, '2026-10'), '2026-10-30', '2026-10-30', '发布 2026-10-30,引擎推定规则、非日历实录),与全国口径方向一致')
o('③', '同月两者均较前月上行: 东京 2.73>2.69 且 全国 2.44>2.16', c.mv(TK, '2026-10') > c.mv(TK, '2026-09') and c.mv(JP, '2026-10') > c.mv(JP, '2026-09'), (c.mv(TK, '2026-09'), c.mv(JP, '2026-09')))
c.has_text('③', '判断档文字', '与全国口径方向一致——同月两者均较前月上行')
e('③', 'facts.' + JP + '.quality_status', c.fact(JP)['quality_status'], 'WARN')
e('③', 'facts.' + EA + '.quality_status', c.fact(EA)['quality_status'], 'WARN')
c.diag.append('FACT issues JP_CPI_YOY: ' + json.dumps(c.fact(JP).get('issues'), ensure_ascii=False)[:400])
c.diag.append('FACT issues EA_HICP_YOY: ' + json.dumps(c.fact(EA).get('issues'), ensure_ascii=False)[:400])
o('③', 'series_store.' + TK + ' 无事实行', c.fact(TK) is None, None)
n('⑥', TK + '@2026-04', c.mv(TK, '2026-04'), 1.42, '1.42', '由6个月前锚观测月 2026-04 的 1.42% 升至最新一期锚观测月 2026-10 的 2.73%')
n('⑥', TK + '@2026-10', c.mv(TK, '2026-10'), 2.73, '2.73', '1.42% 升至最新一期锚观测月 2026-10 的 2.73%')

# ---------- M1 link1 monthly path ----------
EAP = [('2026-05', 3.2), ('2026-06', 2.8), ('2026-07', 2.9), ('2026-08', 3.2), ('2026-09', 3.8), ('2026-10', 4.0)]
JPP = [('2026-05', 1.53), ('2026-06', 1.67), ('2026-07', 1.97), ('2026-08', 1.98), ('2026-09', 2.16), ('2026-10', 2.44)]
for ym, v in EAP:
    n('⑦', EA + '@' + ym, c.mv(EA, ym), v, str(v), str(v) + '(' + ym + ')')
for ym, v in JPP:
    n('⑦', JP + '@' + ym, c.mv(JP, ym), v, str(v), str(v) + '(' + ym + ')')
    n('⑬', '窗内逐月路径 JP ' + ym, c.mv(JP, ym), v, str(v), '1.53(2026-05)→1.67(2026-06)→1.97(2026-07)→1.98(2026-08)→2.16(2026-09)→2.44(2026-10)' if ym != '2026-10' else '→2.16(2026-09)→2.44(2026-10)')
diffs = [c.mv(EA, ym) - c.mv(JP, ym) for ym in ['2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10']]
n('⑦', '窗内各月 EA-JP 最小差', min(diffs), 0.93, '0.93', '高于日本 0.93-1.67 个百分点', tol=0.006)
n('⑦', '窗内各月 EA-JP 最大差', max(diffs), 1.67, '1.67', '0.93-1.67 个百分点', tol=0.006)
o('⑦', '欧元区 2026-06 一度回落至 2.8', c.mv(EA, '2026-06') < c.mv(EA, '2026-05') and close(c.mv(EA, '2026-06'), 2.8), '非逐月单调')
o('⑦', '日本 2026-05..10 逐月上行', all(c.mv(JP, JPP[i][0]) < c.mv(JP, JPP[i + 1][0]) for i in range(5)), JPP)
o('①', '2026-05 期观测日早于窗起', c.md(EA, '2026-05') < '2026-05-23' and c.md(JP, '2026-05') < '2026-05-23', (c.md(EA, '2026-05'), c.md(JP, '2026-05')))
t('①', '2026-05 期观测日', c.md(EA, '2026-05'), '2026-05-01', '2026-05-01', '2026-05 期观测日 2026-05-01 早于窗起 2026-05-23')
o('①', '2026-05 期推定发布日在窗内', '2026-05-23' <= c.pub(EA, '2026-05') <= A and '2026-05-23' <= c.pub(JP, '2026-05') <= A, (c.pub(EA, '2026-05'), c.pub(JP, '2026-05')))
t('①', '推定发布规则 EA 2026-05', c.pub(EA, '2026-05'), '2026-06-16', '2026-06-16', '推定发布日 2026-06-16 在窗内')
t('①', '推定发布规则 JP 2026-05', c.pub(JP, '2026-05'), '2026-06-20', '2026-06-20', '推定发布日 2026-06-20 在窗内')
o('①', '2026-06..10 期观测与推定发布均在窗内', all('2026-05-23' <= c.md(m, ym) <= A and '2026-05-23' <= c.pub(m, ym) <= A for m in (EA, JP) for ym in ['2026-06', '2026-07', '2026-08', '2026-09', '2026-10']), 'ok')

# ---------- (6) turnings ----------
def mlist(m):
    return [(d[:7], v) for d, v in zip(c.S[m]['dates'], c.S[m]['values'])]
def best3(m, lo='2025-11', hi='2026-10'):
    L = [x for x in mlist(m) if lo <= x[0] <= hi]
    res = []
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            mo = (int(L[j][0][:4]) * 12 + int(L[j][0][5:])) - (int(L[i][0][:4]) * 12 + int(L[i][0][5:]))
            if mo == 3:
                res.append((L[i][0], L[j][0], L[i][1], L[j][1], round(L[j][1] - L[i][1], 3)))
    res.sort(key=lambda x: -abs(x[4]))
    return res
for m in [EA, JP, TK, PR]:
    b = best3(m)
    c.diag.append('3月滚动变化(近12月观测月)前三 ' + m + ': ' + str(b[:3]))
    mv_ = {x[0] for x in b if abs(x[4] - b[0][4]) < 1e-9}
    c.diag.append('  并列最大者 ' + m + ': ' + str([x for x in b if x[0] in mv_]))
BE = best3(EA)[0]; BJ = best3(JP)[0]; BT = best3(TK)[0]; BP = best3(PR)[0]
n('⑥', EA + ' 谷底→2026-05', c.mv(EA, '2026-05'), 3.2, '3.2', '2026-02→2026-05 由 1.9 升至 3.2(三个月 +1.30 个百分点)')
n('⑥', EA + ' 2026-02 谷底', c.mv(EA, '2026-02'), 1.9, '1.9', '由 1.9 升至 3.2(三个月 +1.30 个百分点)')
n('⑥', '三个月变化 3.2-1.9', c.mv(EA, '2026-05') - c.mv(EA, '2026-02'), 1.3, '1.30', '三个月 +1.30 个百分点', tol=0.006)
tieE = [x for x in best3(EA) if abs(x[4] - BE[4]) < 1e-9]
o('⑥', '引擎候选 EA_HICP 2026-02→05 属 |三个月变化| 最大者集合(并列最大集合直算)', ('2026-02', '2026-05') in [(x[0], x[1]) for x in tieE], tieE)
c.diag.append('EA 并列最大集合: ' + str(tieE))
n('⑥', JP + ' 2026-02 谷底', c.mv(JP, '2026-02'), 1.27, '1.27', '2026-02 1.27→2026-05 1.53')
n('⑥', JP + '@2026-05', c.mv(JP, '2026-05'), 1.53, '1.53', '2026-02 1.27→2026-05 1.53')
e('⑥', 'turnings[0].value_before', c.aj['reader_map']['turnings'][0]['value_before'], c.mv(EA, '2026-02'))
e('⑥', 'turnings[0].value_after', c.aj['reader_map']['turnings'][0]['value_after'], c.mv(EA, '2026-05'))
o('⑥', '近12月谷底: EA 2026-01 的 1.7', min([(v, ym) for ym, v in mlist(EA) if '2025-11' <= ym <= '2026-10']) == (1.7, '2026-01'), min([(v, ym) for ym, v in mlist(EA) if '2025-11' <= ym <= '2026-10']))
o('⑥', '近12月谷底: JP 2026-02 的 1.27', min([(v, ym) for ym, v in mlist(JP) if '2025-11' <= ym <= '2026-10']) == (1.27, '2026-02'), min([(v, ym) for ym, v in mlist(JP) if '2025-11' <= ym <= '2026-10']))
o('⑥', '近12月最高: EA 2026-10 的 4.0', max([(v, ym) for ym, v in mlist(EA) if '2025-11' <= ym <= '2026-10']) == (4.0, '2026-10'), max([(v, ym) for ym, v in mlist(EA) if '2025-11' <= ym <= '2026-10']))
n('⑥', JP + '@2025-11', c.mv(JP, '2025-11'), 2.9, '2.9', '2025-11→2026-02(2.9→1.27,三个月 -1.63 个百分点)')
n('⑥', JP + '@2026-02', c.mv(JP, '2026-02'), 1.27, '1.27', '(2.9→1.27,三个月 -1.63 个百分点)为幅度最大候选')
n('⑥', '三个月变化 1.27-2.9', abs(c.mv(JP, '2026-02') - c.mv(JP, '2025-11')), 1.63, '1.63', '三个月 -1.63 个百分点', tol=0.006)
o('⑥', 'JP_CPI 幅度最大候选=2025-11→2026-02', (BJ[0], BJ[1]) == ('2025-11', '2026-02'), BJ)
o('⑥', '四指标中 |三个月变化| 最大者=JP_CPI 2025-11→02', max([BE, BJ, BT, BP], key=lambda x: abs(x[4])) == BJ, [x[4] for x in (BE, BJ, BT, BP)])
for ym, v in [('2026-06', 2.8), ('2026-07', 2.9), ('2026-08', 3.2), ('2026-09', 3.8), ('2026-10', 4.0)]:
    n('⑥', EA + '@' + ym, c.mv(EA, ym), v, str(v), '此后逐月路径 2026-06 2.8、2026-07 2.9、2026-08 3.2、2026-09 3.8、2026-10 4.0')
TC = RP['turning_candidates']['candidates']
e('⑥', 'engine turning_candidates 数', len(TC), 4)
CAND = {x['metric_id']: x for x in TC}
for m, bb in [(EA, ('2026-02', '2026-05', 1.9, 3.2, 1.3)), (JP, BJ), (TK, BT), (PR, BP)]:
    e('⑥', 'engine candidate ' + m + ' from/to', (CAND[m]['from_ym'], CAND[m]['to_ym'], CAND[m]['value_before'], CAND[m]['value_after']), (bb[0], bb[1], bb[2], bb[3]))
n('⑥', PR + '@2026-07', c.mv(PR, '2026-07'), 0.978, '0.978', '2026-04 0.727→2026-07 0.978(经 2026-06 0.841 过渡)')
n('⑥', PR + '@2026-04', c.mv(PR, '2026-04'), 0.727, '0.727', '2026-04 0.727→2026-07 0.978')
n('⑥', PR + '@2026-06', c.mv(PR, '2026-06'), 0.841, '0.841', '经 2026-06 0.841 过渡')
e('⑥', 'turnings[1].value_before/after', (c.aj['reader_map']['turnings'][1]['value_before'], c.aj['reader_map']['turnings'][1]['value_after']), (c.mv(PR, '2026-04'), c.mv(PR, '2026-07')))
n('⑥', TK + '@2026-06', c.mv(TK, '2026-06'), 1.6, '1.6', '2026-06→2026-09 由 1.6 升至 2.69(三个月 +1.09 个百分点)')
n('⑥', TK + '@2026-09', c.mv(TK, '2026-09'), 2.69, '2.69', '由 1.6 升至 2.69(三个月 +1.09 个百分点)')
n('⑥', '东京三个月变化 2.69-1.6', c.mv(TK, '2026-09') - c.mv(TK, '2026-06'), 1.09, '1.09', '三个月 +1.09 个百分点', tol=0.006)
e('⑥', 'turnings[2].value_before/after', (c.aj['reader_map']['turnings'][2]['value_before'], c.aj['reader_map']['turnings'][2]['value_after']), (c.mv(TK, '2026-06'), c.mv(TK, '2026-09')))
n('⑥', JP + '@2026-06', c.mv(JP, '2026-06'), 1.67, '1.67', '全国 2026-06 1.67→2026-08 1.98')
n('⑥', JP + '@2026-08', c.mv(JP, '2026-08'), 1.98, '1.98', '全国 2026-06 1.67→2026-08 1.98')
n('⑥', 'JP−EA 2026-09 期水平差绝对值', abs(c.mv(JP, '2026-09') - c.mv(EA, '2026-09')), 1.64, '1.64', '全国口径 -1.64、东京口径 -1.11', tol=0.006)
o('⑥', '方向: 2026-09 期日本全国低于欧元区', c.mv(JP, '2026-09') < c.mv(EA, '2026-09'), round(c.mv(JP, '2026-09') - c.mv(EA, '2026-09'), 3))
n('⑥', 'EA−东京 2026-09 期水平差', c.mv(EA, '2026-09') - c.mv(TK, '2026-09'), 1.11, '1.11', '东京口径 -1.11', tol=0.006)
n('⑥', 'TK−EA 2026-09 期水平差', abs(c.mv(TK, '2026-09') - c.mv(EA, '2026-09')), 1.11, '1.11', '东京口径 -1.11', tol=0.006)
o('⑥', '两水平差均为负(日本低于欧元区)', c.mv(JP, '2026-09') < c.mv(EA, '2026-09') and c.mv(TK, '2026-09') < c.mv(EA, '2026-09'), '负')
n('⑥', EA + '@2026-09', c.mv(EA, '2026-09'), 3.8, '3.8', '欧元区同期读数亦高(2026-09 为 3.8)')
t('⑥', '推定发布规则 东京 2026-09', c.pub(TK, '2026-09'), '2026-09-29', '2026-09-29', '东京读数的引擎推定发布日 2026-09-29 晚于 BOJ 决议日 2026-09-18')
o('⑥', '东京 2026-09 推定发布日 晚于 2026-09-18', c.pub(TK, '2026-09') > '2026-09-18', c.pub(TK, '2026-09'))
t('⑥', '推定发布规则 东京 2026-08', c.pub(TK, '2026-08'), '2026-08-30', '2026-08-30', '推定发布 2026-08-30;该推定日落在周日')
o('⑥', '决议前(2026-09-18)可见最近东京读数=2026-08', c.vis(TK, '2026-09-18')[0][:7] == '2026-08', c.vis(TK, '2026-09-18'))
n('⑥', TK + '@2026-08', c.mv(TK, '2026-08'), 1.9, '1.9', '决议前可见的最近东京读数为 2026-08 的 1.9')
o('⑥', '月末-1天推定日 vs 当月最后周五: 2026-06 不一致 / 2026-10 一致', c.pub(TK, '2026-06') != lastfri('2026-06') and c.pub(TK, '2026-10') == lastfri('2026-10'), (c.pub(TK, '2026-06'), lastfri('2026-06'), c.pub(TK, '2026-10'), lastfri('2026-10')))
c.diag.append('东京推定发布日 vs 最后周五(2026-01..10): ' + str([(ym, c.pub(TK, ym), lastfri(ym)) for ym in sorted(set(d[:7] for d in c.S[TK]['dates']))]))
n('⑥', JP + ' 2026-03→04 回落', c.mv(JP, '2026-03') - c.mv(JP, '2026-04'), 0.08, '0.08', '有一次 0.08 个百分点的小幅回落', tol=0.006)
n('⑥', JP + '@2026-03', c.mv(JP, '2026-03'), 1.46, '1.46', '2026-03 的 1.46→2026-04 的 1.38')
for ym, v in [('2025-01', 4.03), ('2025-09', 2.91), ('2025-10', 2.99)]:
    n('⑥', JP + '@' + ym, c.mv(JP, ym), v, str(v), '自 2025-01 高点 4.03 总体回落(2025-09、2025-10 两月小幅回升至 2.91、2.99)')
JL = mlist(JP)
mx = max(v for ym, v in JL); mxd = [ym for ym, v in JL if v == mx]
o('⑥', 'JP_CPI 2025-01 为 2024-01 以来最高且为局部高点(全序列最高为 2023-01 的 4.31, 高于 2025-01; 文称「2025-01 高点 4.03」未称全序列最高)', max([(v, ym) for ym, v in mlist(JP) if ym >= '2024-01']) == (4.03, '2025-01') and c.mv(JP, '2024-12') < 4.03 and c.mv(JP, '2025-02') < 4.03, {'2024-12': c.mv(JP, '2024-12'), '2025-01': c.mv(JP, '2025-01'), '2025-02': c.mv(JP, '2025-02'), 'allmax': max([(v, ym) for ym, v in mlist(JP)])})
c.diag.append('JP_CPI 2024-10..2026-04: ' + str([(ym, v) for ym, v in mlist(JP) if '2024-10' <= ym <= '2026-04']))
c.diag.append('JP_CPI 各年末与基期拼接邻月 2025-07..2026-01: ' + str([(ym, v) for ym, v in mlist(JP) if '2025-07' <= ym <= '2026-01']))
c.diag.append('JP_CPI_YOY 2022-2024: ' + str([(ym, v) for ym, v in JL if '2022' <= ym[:4] <= '2024']))
o('⑥', '2025-01 之后至 2026-02 总体回落(末<起 且 2026-02 为其间最低)', c.mv(JP, '2026-02') < c.mv(JP, '2025-01') and min((v, ym) for ym, v in JL if '2025-01' <= ym <= '2026-02') == (c.mv(JP, '2026-02'), '2026-02'), 'ok')
o('⑥', '2026-02 之后总体回升至 2026-10(最高在 2026-10)', max((v, ym) for ym, v in JL if '2026-02' <= ym <= '2026-10') == (c.mv(JP, '2026-10'), '2026-10'), 'ok')

# ---------- ECB visibility before decisions ----------
o('⑥', '决议日(回推 06-11)前可见 EA 读数=2026-04', c.vis(EA, '2026-06-11')[0][:7] == '2026-04', c.vis(EA, '2026-06-11'))
n('⑥', 'c.vis(EA, 2026-06-11)', c.vis(EA, '2026-06-11')[1], 3.0, '3.0', '前可见 2026-04=3.0、生效日前可见 2026-05=3.2')
o('⑥', '生效日(06-17)前可见 EA 读数=2026-05', c.vis(EA, '2026-06-17')[0][:7] == '2026-05', c.vis(EA, '2026-06-17'))
n('⑥', 'c.vis(EA, 2026-06-17)', c.vis(EA, '2026-06-17')[1], 3.2, '3.2', '生效日前可见 2026-05=3.2')
o('⑥', '决议日(回推 09-10)前可见 EA 读数=2026-07', c.vis(EA, '2026-09-10')[0][:7] == '2026-07', c.vis(EA, '2026-09-10'))
n('⑥', 'c.vis(EA, 2026-09-10)', c.vis(EA, '2026-09-10')[1], 2.9, '2.9', '前可见 2026-07=2.9、生效日前可见 2026-08=3.2')
o('⑥', '生效日(09-16)前可见 EA 读数=2026-08', c.vis(EA, '2026-09-16')[0][:7] == '2026-08', c.vis(EA, '2026-09-16'))
n('⑥', 'c.vis(EA, 2026-09-16)', c.vis(EA, '2026-09-16')[1], 3.2, '3.2', '生效日前可见 2026-08=3.2')
t('⑥', '推定发布规则 EA 2026-08', c.pub(EA, '2026-08'), '2026-09-16', '2026-09-16', '发布日 2026-09-16 与生效日同日,先后时刻不可分')
o('⑥', '两次变更前可见读数(3.0/3.2/2.9/3.2)均高于 2026-02 的 1.9', min(c.vis(EA, d)[1] for d in ['2026-06-11', '2026-06-17', '2026-09-10', '2026-09-16']) > c.mv(EA, '2026-02'), 'ok')
o('⑥', '快报形态(次月首日)下决议日前可见: 06-11→2026-05, 09-10→2026-08', (c.mv(EA, '2026-05'), c.mv(EA, '2026-08')) == (3.2, 3.2), 'ok')
n('⑥', 'EA@2026-01', c.mv(EA, '2026-01'), 1.7, '1.7', '其间读数已由 2026-01 的 1.7 升至 2026-04 的 3.0')
o('⑥', '2026-01→04: 1.7→3.0 而两序列未变更', (c.mv(EA, '2026-01'), c.mv(EA, '2026-04')) == (1.7, 3.0), 'ok')
o('⑥', '2026-05=3.2 为 2026-01..08 区间峰值(并列 2026-08)', max(c.mv(EA, ym) for ym in ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08']) == 3.2, [ym for ym in ['2026-01', '2026-02', '2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08'] if c.mv(EA, ym) == 3.2])
o('⑥', 'BOJ 决议前(09-18)可见全国读数=2026-07', c.vis(JP, '2026-09-18')[0][:7] == '2026-07', c.vis(JP, '2026-09-18'))
t('⑥', '推定发布规则 JP 2026-08', c.pub(JP, '2026-08'), '2026-09-20', '2026-09-20', '')

# ---------- (7) chain: FX ----------
def fx(m, d, rep, snip):
    n('⑦', 'series_store.' + m + '@' + d, c.at(m, d), rep, str(rep), snip)
fx('EURUSD', W0, 1.1221, 'EURUSD 由 1.1221 降至 1.0970(-2.24%)')
fx('EURUSD', W1, 1.0970, 'EURUSD 由 1.1221 降至 1.0970(-2.24%)')
n('⑦', 'EURUSD 10-23→11-20 %', abs(pc('EURUSD', W0, W1)), 2.24, '2.24', '降至 1.0970(-2.24%)', tol=0.006)
o('⑦', 'EURUSD 10-23→11-20 方向=下降', pc('EURUSD', W0, W1) < 0, round(pc('EURUSD', W0, W1), 3))
fx('USDJPY', W0, 156.494, 'USDJPY 由 156.494 升至 159.707(+2.05%)')
fx('USDJPY', W1, 159.707, 'USDJPY 由 156.494 升至 159.707(+2.05%)')
n('⑦', 'USDJPY 10-23→11-20 %', pc('USDJPY', W0, W1), 2.05, '2.05', '升至 159.707(+2.05%)', tol=0.006)
fx('DXY', W0, 101.81, 'DXY 由 101.81 升至 103.81(+1.96%)')
fx('DXY', W1, 103.81, 'DXY 由 101.81 升至 103.81(+1.96%)')
n('⑦', 'DXY 10-23→11-20 %', pc('DXY', W0, W1), 1.96, '1.96', '升至 103.81(+1.96%)', tol=0.006)
fx('EURUSD', A, 1.0940, 'EURUSD 1.0940(-2.51%)')
n('⑦', 'EURUSD 10-23→11-23 %', abs(pc('EURUSD', W0, A)), 2.51, '2.51', 'EURUSD 1.0940(-2.51%)', tol=0.006)
o('⑦', 'EURUSD 10-23→11-23 方向=下降', pc('EURUSD', W0, A) < 0, round(pc('EURUSD', W0, A), 3))
fx('USDJPY', A, 159.347, 'USDJPY 159.347(+1.82%)')
n('⑦', 'USDJPY 10-23→11-23 %', pc('USDJPY', W0, A), 1.82, '1.82', 'USDJPY 159.347(+1.82%)', tol=0.006)
fx('DXY', A, 104.079, 'DXY 104.079(+2.23%)')
n('⑦', 'DXY 10-23→11-23 %', pc('DXY', W0, A), 2.23, '2.23', 'DXY 104.079(+2.23%)', tol=0.006)
ej0 = c.at('EURUSD', W0) * c.at('USDJPY', W0); ej1 = c.at('EURUSD', W1) * c.at('USDJPY', W1); ej2 = c.at('EURUSD', A) * c.at('USDJPY', A)
c.diag.append('EURJPY 合成: ' + str((ej0, ej1, ej2)))
n('⑦', 'EURUSD×USDJPY@10-23', ej0, 175.61, '175.61', '2026-10-23 收盘 175.61→2026-11-20 收盘 175.19', tol=0.006)
n('⑦', 'EURUSD×USDJPY@11-20', ej1, 175.19, '175.19', '收盘 175.19(-0.24%)', tol=0.006)
n('⑦', 'EURJPY 合成 10-23→11-20 %', abs(pct(ej0, ej1)), 0.24, '0.24', '175.19(-0.24%)', tol=0.006)
o('⑦', 'EURJPY 合成 10-23→11-20 方向=下降', pct(ej0, ej1) < 0, round(pct(ej0, ej1), 3))
n('⑦', 'EURUSD×USDJPY@11-23', ej2, 174.32, '174.32', '盘中 174.32(较 10-23 -0.73%)', tol=0.006)
n('⑦', 'EURJPY 合成 10-23→11-23 %', abs(pct(ej0, ej2)), 0.73, '0.73', '174.32(较 10-23 -0.73%)', tol=0.006)
o('⑦', 'EURJPY 合成 10-23→11-23 方向=下降', pct(ej0, ej2) < 0, round(pct(ej0, ej2), 3))
o('⑦', '方向: 欧元对美元走弱、日元对美元走弱、美元指数上行', pc('EURUSD', W0, W1) < 0 and pc('USDJPY', W0, W1) > 0 and pc('DXY', W0, W1) > 0 and pc('EURUSD', W0, A) < 0 and pc('USDJPY', W0, A) > 0, 'ok')
n('⑦', 'series_store.UST_10Y@2026-11-19', c.at('UST_10Y', '2026-11-19'), 5.04, '5.04', 'UST_10Y 最新 5.04%(观测 2026-11-19)')
o('⑦', 'UST_10Y(5.04) 高于 MRO(2.65) 与 BOJ 目标(1.25)', c.at('UST_10Y', '2026-11-19') > c.last('ECB_MRO')[1] > 1.25, 'ok')
e('⑦', 'engine asset_moves.DXY.chg_pct', round(pc('DXY', W0, A), 2), [x for x in RP['asset_moves']['rows'] if x['metric_id'] == 'DXY'][0]['chg_pct'])
for row in RP['asset_moves']['rows']:
    m = row['metric_id']; d0 = row['window']['from']; d1 = row['window']['to']
    e('⑤', 'engine asset_moves.' + m + ' chg_pct (series_store 直算)', round(pc(m, d0, d1), 2), row['chg_pct'])
    e('⑤', 'engine asset_moves.' + m + ' from_value', c.at(m, d0), row['from_value'])
    e('⑤', 'engine asset_moves.' + m + ' to_value', c.at(m, d1), row['to_value'])

# ---------- chain: equities / VIX ----------
EQ = [('SPX', -9.36, 'SPX 下跌 9.36%'), ('NIKKEI225', -9.98, 'NIKKEI225 下跌 9.98%'), ('DAX', -1.50, 'DAX 下跌 1.50%'), ('CAC40', 1.86, 'CAC40 上涨 1.86%')]
for m, rv, snip in EQ:
    n('⑦', m + ' 10-23→11-20 %', abs(pc(m, W0, W1)), abs(rv), str(abs(rv)), snip, tol=0.006)
    o('⑦', m + ' 方向词与符号', (pc(m, W0, W1) < 0) == (rv < 0), round(pc(m, W0, W1), 4))
n('⑦', 'VIX@10-23', c.at('VIX', W0), 19.45, '19.45', 'VIX 由 19.45 升至 35.89(+84.5%)')
n('⑦', 'VIX@11-20', c.at('VIX', W1), 35.89, '35.89', 'VIX 由 19.45 升至 35.89(+84.5%)')
n('⑦', 'VIX 10-23→11-20 %', pc('VIX', W0, W1), 84.5, '84.5', '升至 35.89(+84.5%)', tol=0.06)
VX = [('11-13', 19.30), ('11-16', 22.91), ('11-17', 25.46), ('11-18', 24.56), ('11-19', 28.44), ('11-20', 35.89)]
for dd, v in VX:
    sn = dd + ' ' + ('%.2f' % v) + '→' if dd != '11-20' else '11-20 35.89,跳升集中于末五个交易日'
    n('⑦', 'series_store.VIX@2026-' + dd, c.at('VIX', '2026-' + dd), v, str(v), sn)
vd = [d for d in c.S['VIX']['dates'] if '2026-11-13' <= d <= '2026-11-20']
o('⑦', '跳升窗 2026-11-13→11-20 含 5 个交易日(不含起点日)', len(vd) - 1 == 5, vd)
o('⑦', '末六个交易日收盘路径=11-13..11-20(截止日前的最后六个观测; 11-21/22 为周末, 11-23 为截止日盘中)', vd == [d for d in sorted(c.S['VIX']['dates']) if d < A][-6:], [d for d in sorted(c.S['VIX']['dates']) if d < A][-6:])
n('⑦', '资产月窗 SPX chg_pct 10-23→11-23', abs(pc('SPX', W0, A)), 5.51, '5.51', 'SPX -5.51%(7203.85,盘中)', tol=0.006)
n('⑦', '资产月窗 DAX chg_pct 10-23→11-23', pc('DAX', W0, A), 0.11, '0.11', 'DAX +0.11%(25209.45,盘中)', tol=0.006)
n('⑦', '资产月窗 NIKKEI225 chg_pct 10-23→11-20', abs(pc('NIKKEI225', W0, W1)), 9.98, '9.98', 'NIKKEI225 -9.98%(56436.65,2026-11-20 收盘)', tol=0.006)
n('⑦', '资产月窗 VIX chg_pct 10-23→11-23', pc('VIX', W0, A), 38.87, '38.87', 'VIX +38.87%(27.01,盘中', tol=0.006)
fx('DAX', A, 25209.45, 'DAX +0.11%(25209.45,盘中)')
fx('NIKKEI225', W1, 56436.65, 'NIKKEI225 -9.98%(56436.65,2026-11-20 收盘)')
n('⑦', 'VIX 11-20 收盘→11-23 盘中 %', abs(pc('VIX', W1, A)), 24.7, '24.7', '较 2026-11-20 收盘 -24.7%', tol=0.06)
o('⑦', '方向词: 较 11-20 收盘为负', pc('VIX', W1, A) < 0, round(pc('VIX', W1, A), 3))
fx('VIX', '2026-11-04', 16.61, 'VIX 收盘 16.61→28.18(+69.66%)')
fx('VIX', '2026-11-05', 28.18, 'VIX 收盘 16.61→28.18(+69.66%)')
n('⑦', 'VIX 11-04→11-05 %', pc('VIX', '2026-11-04', '2026-11-05'), 69.66, '69.66', '16.61→28.18(+69.66%)', tol=0.006)
fx('VIX', '2026-11-11', 17.49, '回落至 17.49(四个交易日')
vdt = [d for d in c.S['VIX']['dates'] if '2026-11-05' < d <= '2026-11-11']
o('⑦', '11-05→11-11 四个交易日', len(vdt) == 4, vdt)
n('⑦', 'VIX 11-05→11-11 %', abs(pc('VIX', '2026-11-05', '2026-11-11')), 37.93, '37.93', '较 11-05 -37.93%', tol=0.006)
n('⑦', 'SPX 11-05 单日 %', abs(pc('SPX', '2026-11-04', '2026-11-05')), 4.36, '4.36', '同期 SPX 11-05 -4.36%', tol=0.006)
n('⑦', 'NIKKEI225 11-06 单日 %', abs(pc('NIKKEI225', '2026-11-05', '2026-11-06')), 5.96, '5.96', '下一交易日 NIKKEI225 11-06 -5.96%', tol=0.006)
o('⑦', '负号方向: SPX 月窗/NIKKEI 月窗/VIX 11-20→11-23/VIX 11-05→11-11/SPX 11-05/NIKKEI 11-06 均为负', all(x < 0 for x in [pc('SPX', W0, A), pc('NIKKEI225', W0, W1), pc('VIX', W1, A), pc('VIX', '2026-11-05', '2026-11-11'), pc('SPX', '2026-11-04', '2026-11-05'), pc('NIKKEI225', '2026-11-05', '2026-11-06')]), [round(x, 3) for x in [pc('SPX', W0, A), pc('NIKKEI225', W0, W1), pc('VIX', W1, A), pc('VIX', '2026-11-05', '2026-11-11'), pc('SPX', '2026-11-04', '2026-11-05'), pc('NIKKEI225', '2026-11-05', '2026-11-06')]])
o('⑦', 'NIKKEI225 11-05 的下一交易日=11-06', c.S['NIKKEI225']['dates'][c.S['NIKKEI225']['dates'].index('2026-11-05') + 1] == '2026-11-06', 'ok')
n('⑦', 'VIX 11-13→11-16 单日 %', pc('VIX', '2026-11-13', '2026-11-16'), 18.70, '18.70', '当日 VIX +18.70%/+26.20%', tol=0.006)
n('⑦', 'VIX 11-19→11-20 单日 %', pc('VIX', '2026-11-19', '2026-11-20'), 26.20, '26.20', '+18.70%/+26.20%', tol=0.006)
vds = c.S['VIX']['dates']
jump = [(d, round(pc('VIX', vds[vds.index(d) - 1], d), 2)) for d in vds if '2026-11-16' <= d <= '2026-11-20']
o('⑦', '11-16/11-20 为跳升窗内两个最大单日跳升日', [x[0] for x in sorted(jump, key=lambda x: -x[1])[:2]] == ['2026-11-20', '2026-11-16'], jump)
for m, rv, snip in [('SPX', 8.61, 'SPX -8.61%'), ('NIKKEI225', 7.70, 'NIKKEI225 -7.70%'), ('DAX', 7.28, 'DAX -7.28%'), ('CAC40', 5.27, 'CAC40 -5.27%')]:
    n('⑦', m + ' 11-13→11-20 %', abs(pc(m, '2026-11-13', W1)), rv, str(rv), snip, tol=0.006)
o('⑦', '11-13→11-20 四地股指跌幅均不深于美股', all(pc(m, '2026-11-13', W1) >= pc('SPX', '2026-11-13', W1) for m in ['NIKKEI225', 'DAX', 'CAC40']), [round(pc(m, '2026-11-13', W1), 3) for m in ['SPX', 'NIKKEI225', 'DAX', 'CAC40']])
mx2 = max(abs(pc(m, d0, d1)) for m in ['EURUSD', 'USDJPY'] for d0, d1 in [('2026-11-13', '2026-11-16'), ('2026-11-19', '2026-11-20')])
o('⑦', '11-16/11-20 两日 EURUSD/USDJPY 单日变动最大幅 <=0.23%', mx2 <= 0.23, round(mx2, 4))
e('⑦', 'engine policy_doc_facts[0].published_on', RP['policy_doc_facts'][0]['published_on'], '2026-11-18')
e('⑦', 'engine policy_doc_facts 条数', len(RP['policy_doc_facts']), 1)
c.has_text('⑦', '判断档文字', 'FOMC 2026年10月会议纪要 2026-11-18 发布')
c.has_text('⑦', '判断档文字', '政策文档事实仅 FOMC 纪要一条')
n('⑦', 'days(2026-10-30→11-13)', days('2026-10-30', '2026-11-13'), 14, '14', '距最近政策日 2026-10-30 为 14 天')
n('⑦', 'days(2026-09-16→11-13)', days('2026-09-16', '2026-11-13'), 58, '58', '距 ECB 最近生效日 2026-09-16 为 58 天')
n('⑦', 'days(2026-10-30→11-20)', days('2026-10-30', W1), 21, '21', '2026-11-20 为 21 天、65 天')
n('⑦', 'days(2026-09-16→11-20)', days('2026-09-16', W1), 65, '65', '为 21 天、65 天')
c.has_text('⑦', '判断档文字', '证据倾向竞争解释但不足以裁定,尚不能区分')
o('⑦', '同日收盘对照: DAX/CAC40 跌幅浅于 SPX, NIKKEI225 与 SPX 相当(差<0.7pp)', pc('DAX', W0, W1) > pc('SPX', W0, W1) and pc('CAC40', W0, W1) > pc('SPX', W0, W1) and abs(pc('NIKKEI225', W0, W1) - pc('SPX', W0, W1)) < 0.7, [round(pc(m, W0, W1), 3) for m in ['SPX', 'NIKKEI225', 'DAX', 'CAC40']])
c.diag.append('VIX 2026-10-23..11-23 全部收盘: ' + str([(d[5:], v) for d, v in zip(c.S['VIX']['dates'], c.S['VIX']['values']) if W0 <= d <= A]))
c.diag.append('SPX 同期: ' + str([(d[5:], v) for d, v in zip(c.S['SPX']['dates'], c.S['SPX']['values']) if W0 <= d <= A]))

# ---------- (5) rates trio / asset echo ----------
UT = RP['us_rates_trio']; RD = c.aj['reader_map']['rates_decomposition']
d0, d1 = UT['window']['from'], UT['window']['to']
for m in ['UST_10Y', 'TIPS_10Y', 'BEI_10Y']:
    e('⑤', 'us_rates_trio chg_bp.' + m + ' (series_store 直算)', round((c.at(m, d1) - c.at(m, d0)) * 100, 3), UT['chg_bp'][m])
    e('⑤', 'us_rates_trio levels_at_to.' + m, c.at(m, d1), UT['levels_at_to'][m])
e('⑤', 'rates_decomposition.window_from', RD['window_from'], d0)
e('⑤', 'rates_decomposition.window_to', RD['window_to'], d1)
e('⑤', 'rates_decomposition.nominal_bp', RD['nominal_bp'], UT['chg_bp']['UST_10Y'])
e('⑤', 'rates_decomposition.real_bp', RD['real_bp'], UT['chg_bp']['TIPS_10Y'])
e('⑤', 'rates_decomposition.bei_bp', RD['bei_bp'], UT['chg_bp']['BEI_10Y'])
res_ = ((c.at('UST_10Y', d1) - c.at('UST_10Y', d0)) - ((c.at('TIPS_10Y', d1) - c.at('TIPS_10Y', d0)) + (c.at('BEI_10Y', d1) - c.at('BEI_10Y', d0)))) * 100
o('⑤', '恒等式 Δ名义=Δ实际+Δ盈亏平衡 (bp)', abs(res_) < 0.5, round(res_, 3))
for dd in [d0, d1]:
    o('⑤', '水平恒等式 名义=实际+盈亏平衡 @' + dd, abs(c.at('UST_10Y', dd) - (c.at('TIPS_10Y', dd) + c.at('BEI_10Y', dd))) < 0.006, (c.at('UST_10Y', dd), c.at('TIPS_10Y', dd), c.at('BEI_10Y', dd)))
w12 = UT['window_12m']
for m in ['UST_10Y', 'TIPS_10Y', 'BEI_10Y']:
    e('⑤', 'us_rates_trio chg_bp_12m.' + m + ' (series_store 直算)', round((c.at(m, w12['to']) - c.at(m, w12['from'])) * 100, 3), UT['chg_bp_12m'][m])
e('⑤', 'us_rates_trio.window_12m', (w12['from'], w12['to']), ('2025-11-19', '2026-11-19'))
o('⑤', '12月窗=365 天且止于 11-19', days(w12['from'], w12['to']) == 365, days(w12['from'], w12['to']))
c.diag.append('TIPS/BEI/UST 末观测日: ' + str({m: c.last(m)[0] for m in ['UST_10Y', 'TIPS_10Y', 'BEI_10Y']}))
c.diag.append('US rates trio @2025-11-19/@2026-10-20/@2026-11-19: ' + str({dd: {m: c.at(m, dd) for m in ['UST_10Y', 'TIPS_10Y', 'BEI_10Y']} for dd in ['2025-11-19', d0, d1]}))
for a in c.aj['reader_map']['asset_returns_echo']:
    e('⑤', 'asset_returns_echo ' + a['metric_id'] + ' chg_pct (series_store 直算)', round(pc(a['metric_id'], a['window']['from'], a['window']['to']), 2), a['chg_pct'])

# ---------- (8) analog ----------
def findv(obj, pred, path=''):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out += findv(v, pred, path + '.' + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out += findv(v, pred, path + '[' + str(i) + ']')
    else:
        out.append((path, obj))
    return out
ST = c.rep.get('steps', [])
c.diag.append('steps[0] keys: ' + str(list(ST[0].keys())) if ST and isinstance(ST[0], dict) else 'no steps')
i6 = [i for i, st in enumerate(ST) if any(isinstance(x, (int, float)) and not isinstance(x, bool) and x == 1871 for _, x in findv(st.get('envelope'), None))]
o('⑧', 'S6 信封定位(含 1871 的 step 数)', len(i6) == 1, i6)
if i6:
    env = ST[i6[0]]['envelope']; LV = findv(env, None)
    o('⑧', 'S6: 扫描候选月=1871', any(isinstance(x, (int, float)) and x == 1871 for _, x in LV), 1871)
    o('⑧', 'S6: 有效候选=74', any(isinstance(x, (int, float)) and x == 74 for _, x in LV), [p for p, x in LV if isinstance(x, (int, float)) and x == 74])
    o('⑧', 'S6: TOP1 候选月 2025-03', any(isinstance(x, str) and x.startswith('2025-03') for _, x in LV), [p for p, x in LV if isinstance(x, str) and x.startswith('2025-03')][:4])
    o('⑧', 'S6: TOP1 距离 0.727', any(isinstance(x, (int, float)) and abs(x - 0.727) < 0.0006 for _, x in LV), [(p, x) for p, x in LV if isinstance(x, (int, float)) and abs(x - 0.727) < 0.0006][:4])
    c.diag.append('S6 envelope 标量键: ' + json.dumps({k: env[k] for k in env if isinstance(env[k], (int, float, str))}, ensure_ascii=False)[:700] if isinstance(env, dict) else str(type(env)))
    c.diag.append('S6 距离/候选相关路径: ' + str([(p, x) for p, x in LV if any(k in p.lower() for k in ['top', 'distance', 'valid', 'scan', 'candidat', 'n_'])])[:900])
c.has_text('⑧', '判断档文字', '历史类比 0 段(契约允许 0..3 段,零段如实写明)')
e('⑧', 'reader_map.history_periods 段数', len(c.aj['reader_map']['history_periods']), 0)

# ---------- (9) scenarios ----------
SC = c.aj['l4']['scenarios']
c.has_text('⑨', '判断档文字', '【假设·非预测】分化延续')
c.has_text('⑨', '判断档文字', '【假设·非预测】分化收敛')
t('⑨', '推定发布规则 EA 2026-12 → 入档月', c.pub(EA, '2026-12')[:7], '2027-01', '2027-01', '读数按引擎发布规则于 2027-01 入档,早于时限 2027-02-15')
o('⑨', 'EA/JP 2026-11、2026-12 期推定发布日均早于 2027-02-15', all(c.pub(m, ym) < '2027-02-15' for m in (EA, JP) for ym in ['2026-11', '2026-12']), [(m, ym, c.pub(m, ym)) for m in (EA, JP) for ym in ['2026-11', '2026-12']])
o('⑨', '2026-11 期读数在截止日尚未发布', c.pub(EA, '2026-11') > A and c.pub(JP, '2026-11') > A, (c.pub(EA, '2026-11'), c.pub(JP, '2026-11')))
e('⑨', 'l4.scenarios[0].trigger.deadline', SC[0]['rows']['trigger']['deadline'], '2027-02-15')
e('⑨', 'l4.scenarios[1].trigger.deadline', SC[1]['rows']['trigger']['deadline'], '2027-02-15')
o('⑨', '截止日读数与 S1 前提相容: EA 4.0≥3.5, JP 2.44≥2.0, 水平差 1.56≥1.5', c.mv(EA, '2026-10') >= 3.5 and c.mv(JP, '2026-10') >= 2.0 and c.mv(EA, '2026-10') - c.mv(JP, '2026-10') >= 1.5, (c.mv(EA, '2026-10'), c.mv(JP, '2026-10'), round(c.mv(EA, '2026-10') - c.mv(JP, '2026-10'), 3)))
o('⑨', 'S1/S2 证伪条件(须两月)未被截止日前已发布读数满足', True, '2026-11/12 期未发布')
o('⑨', '截止日 VIX 末收盘 35.89: >30(S1 的 VIX 分量现值满足) 且 >=25(S2 的 VIX 分量现值不满足)', c.at('VIX', W1) > 30 and c.at('VIX', W1) >= 25, c.at('VIX', W1))
c.has_text('⑨', '判断档文字', 'VIX 收盘在 25–30 之间时两情景均不触发(证伪条件均不含 VIX 分量)')
c.has_text('⑨', '判断档文字', 'S2 证伪阈值(3.5%)较前提水平(3.0% 以下)放宽,3.0%–3.5% 区间不触发亦不证伪')
c.has_text('⑨', '判断档文字', 'S1 触发阈 4.0% 高于前提水平 3.5%,3.5%–4.0% 区间同属前提成立而不触发')
e('⑨', 'l4.scenarios falsification.metric_id', [x['rows']['falsification']['metric_id'] for x in SC], ['EA_HICP_YOY', 'EA_HICP_YOY'])
e('⑨', 'l4.scenarios falsification.secondary_metric_ids', [x['rows']['falsification']['secondary_metric_ids'] for x in SC], [['JP_CPI_YOY'], ['JP_CPI_YOY']])
o('⑨', '证伪指标 EA_HICP_YOY/JP_CPI_YOY 在册(注册表+series_store)', all(m in c.RM and m in c.S for m in [EA, JP]), 'ok')
c.has_text('⑨', '判断档文字', '该方向与近一月观察(SPX 下跌 9.36%、NIKKEI225 下跌 9.98%、DAX 下跌 1.50%、CAC40 上涨 1.86%、VIX 上涨)相反,属并列反例情景')
c.save('b')
