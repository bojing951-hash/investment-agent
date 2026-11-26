# s10a_core.py <snap> <rep> <cal> <reg> <aj> <out>  -- sections 1-4 (cutoff, anchors, yoy, policy)
import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
snap, rep, cal, reg, aj, out = sys.argv[1:7]
c = Ctx(snap, rep, cal, reg, aj, out)
A = c.asof; RP = c.rep['research_plan']; PV = RP['point_values']['cells']
n, t, e, o = c.num, c.txt, c.eq, c.ok
W0 = shift = None
def sh6(d):
    y, m = int(d[:4]), int(d[5:7]) - 6
    if m <= 0:
        y, m = y - 1, m + 12
    return '%04d-%02d-%s' % (y, m, d[8:10])
def lastfri(ym):
    d = D(mend(ym))
    while d.weekday() != 4:
        d -= dt.timedelta(days=1)
    return d.isoformat()

# ---------- (1) cutoff ----------
t('①', 'snap.target_date', c.target, '2026-11-23', '2026-11-23', '研究截止取实际覆盖日 2026-11-23(交付为截至实际日期的结果')
t('①', 'snap.research_as_of', c.snap['research_as_of'], '2026-11-23T22:53:47+08:00', '2026-11-23T22:53:47+08:00', '快照采集于 2026-11-23T22:53:47+08:00')
t('①', 'report.as_of_declared.requested_as_of', RP['as_of_declared']['requested_as_of'], '2026-11-30', '2026-11-30', '问句请求月末 2026-11-30 未到')
o('①', 'report.as_of_declared.clamped_to_coverage', RP['as_of_declared']['clamped_to_coverage'] is True, RP['as_of_declared']['clamped_to_coverage'])
c.has_text('①', '判断档文字', '引擎按 clamped_to_coverage 取实际覆盖日并披露')
t('①', 'report.question_window (6个月回看窗起)', RP['question_window']['windows'][0]['from'], '2026-05-23', '2026-05-23', '最近六个月窗口(2026-05-23..2026-11-23)')
t('①', '独立推算: 截止日-6自然月', sh6(A), '2026-05-23', '2026-05-23', '回看窗 2026-05-23..2026-11-23')
t('①', 'report.question_window.to', RP['question_window']['windows'][0]['to'], '2026-11-23', '2026-11-23', '窗起 2026-05-23 至研究截止 2026-11-23')
t('①', '独立推算: 2026-11 月末', mend('2026-11'), '2026-11-30', '2026-11-30', '问句请求月末 2026-11-30 未到')
for m in ['EA_HICP_YOY', 'JP_CPI_YOY', 'JP_CPI_TOKYO_YOY', 'JP_POLICY_RATE', 'ECB_MRO', 'ECB_DFR', 'SPX', 'VIX', 'DAX', 'CAC40', 'NIKKEI225', 'EURUSD', 'USDJPY', 'DXY', 'UST_10Y', 'TIPS_10Y', 'BEI_10Y', 'JGB2Y', 'JGB5Y', 'JGB10Y', 'DFEDTARL', 'DFEDTARU']:
    if m in c.S:
        ld, lv = c.last(m); src = 'series_store.' + m + '.dates[-1]'
    else:
        f_ = c.fact(m); ld, lv = f_['observation_date'], f_['value']; src = 'facts.' + m + '.observation_date(该指标无 series_store 序列)'
    o('①', src, ld <= A, ld + ' (末值 ' + str(lv) + ')')
for m, ym in [('EA_HICP_YOY', '2026-10'), ('JP_CPI_YOY', '2026-10'), ('JP_CPI_TOKYO_YOY', '2026-10'), ('JP_POLICY_RATE', '2026-10')]:
    p = c.pub(m, ym)
    o('①', '推定发布规则 ' + m + ' ' + ym + ' (月末偏移)', p <= A, p)
for d in ['2026-09-18', '2026-09-24', '2026-10-30']:
    o('①', '冻结日历 JP_POLICY_TARGET 条目日期', d <= A, d)
for d in ['2026-06-11', '2026-09-10', '2026-06-17', '2026-09-16']:
    o('①', '序列变更日/回推决议日', d <= A, d)
t('①', '星期: 2026-05-16', wd('2026-05-16'), '周六', '周六', '发布 2026-05-16,周六')
t('①', '星期: 2026-08-30', wd('2026-08-30'), '周日', '周日', '该推定日落在周日')
t('①', '独立推算: 2026-10 最后一个周五', lastfri('2026-10'), '2026-10-30', '2026-10-30', '官方实录锚 2026-06-26、2026-10-30')
t('①', '独立推算: 2026-06 最后一个周五', lastfri('2026-06'), '2026-06-26', '2026-06-26', '官方实录锚 2026-06-26、2026-10-30')
utc = dt.datetime(2026, 11, 23, 14, 53, 47)
for name, hh, rep in [('纽约', -5, '09:53'), ('柏林', 1, '15:53'), ('东京', 9, '23:53'), ('上海', 8, '22:53')]:
    t('①', '时区换算 research_as_of(UTC-8h)→' + name, (utc + dt.timedelta(hours=hh)).strftime('%H:%M'), rep, rep, '纽约 09:53、柏林 15:53、东京 23:53、上海 22:53)')
o('①', 'research_as_of+08:00 → UTC', c.snap['research_as_of'] == '2026-11-23T22:53:47+08:00' and utc.strftime('%H:%M:%S') == '14:53:47', '14:53:47Z')
e('①', 'release_calendar.version', c.cal['version'], '1.5.0')
e('①', 'release_calendar.updated', c.cal['updated'], '2026-11-21')
c.has_text('①', '判断档文字', '工单冻结发布日历(v1.5.0,2026-11-21 更新)')
e('①', 'evidence_index 行数', len(c.rep['evidence_index']), 60)
c.has_text('①', '判断档文字', '证据索引(60行)、点值格(6格)')
e('①', 'point_values.cells 格数', len(PV), 6)
e('①', 'report.run.git_head', c.rep['run']['git_head'], '36499bb78a18dea1ff2b027074088b0ba404c3b8')

# ---------- (2) anchors ----------
def anchor_month(m, aday, rv, vtok, vsnip, ro, osnip, rp, psnip):
    dd, vv = c.vis(m, aday)
    n('②', 'series_store.' + m + ' 最新已发布观测(推定发布日<=' + aday + ')', vv, rv, vtok, vsnip)
    if osnip:
        t('②', 'series_store.' + m + '.dates', dd[:7], ro, ro, osnip)
    if psnip:
        t('②', '推定发布规则 ' + m + ' (' + dd[:7] + ')', c.pub(m, dd[:7]), rp, rp, psnip)
anchor_month('EA_HICP_YOY', '2026-05-23', 3.0, '3.0', '实际发布日以官方实录为准)的 3.0%', '2026-04', '观测月 2026-04,发布 2026-05-16,周六', '2026-05-16', '发布 2026-05-16,周六')
anchor_month('EA_HICP_YOY', '2026-11-23', 4.0, '4.0', '发布 2026-11-16,引擎推定规则、非日历实录)的 4.0%', '2026-10', '观测月 2026-10,发布 2026-11-16,引擎推定规则、非日历实录)的 4.0%', '2026-11-16', '发布 2026-11-16,引擎推定规则、非日历实录)的 4.0%')
anchor_month('JP_CPI_YOY', '2026-05-23', 1.38, '1.38', '非日历实录)的 1.38% 升至最新一期锚', '2026-04', '观测月 2026-04,发布 2026-05-20,引擎推定规则、非日历实录)的 1.38%', '2026-05-20', '发布 2026-05-20,引擎推定规则、非日历实录)的 1.38%')
anchor_month('JP_CPI_YOY', '2026-11-23', 2.44, '2.44', '发布 2026-11-20,引擎推定规则、非日历实录)的 2.44%', '2026-10', '观测月 2026-10,发布 2026-11-20,引擎推定规则、非日历实录)的 2.44%', '2026-11-20', '发布 2026-11-20,引擎推定规则、非日历实录)的 2.44%')
anchor_month('JP_CPI_TOKYO_YOY', '2026-05-23', 1.42, '1.42', '由6个月前锚观测月 2026-04 的 1.42%', '2026-04', '由6个月前锚观测月 2026-04 的 1.42%', None, None)
anchor_month('JP_CPI_TOKYO_YOY', '2026-11-23', 2.73, '2.73', '最新读数 2.73%(观测月 2026-10,发布 2026-10-30', '2026-10', '最新读数 2.73%(观测月 2026-10,发布 2026-10-30', '2026-10-30', '最新读数 2.73%(观测月 2026-10,发布 2026-10-30')
anchor_month('JP_POLICY_RATE', '2026-05-23', 0.727, '0.727', '非日历实录)的 0.727% 台阶升至最新一期锚', '2026-04', '观测月 2026-04,发布 2026-05-05,引擎推定规则、非日历实录)的 0.727%', '2026-05-05', '发布 2026-05-05,引擎推定规则、非日历实录)的 0.727%')
anchor_month('JP_POLICY_RATE', '2026-11-23', 1.227, '1.227', '发布 2026-11-05,引擎推定规则、非日历实录)的 1.227%', '2026-10', '观测月 2026-10,发布 2026-11-05,引擎推定规则、非日历实录)的 1.227%', '2026-11-05', '发布 2026-11-05,引擎推定规则、非日历实录)的 1.227%')
for m, r6, rl, s6, sl in [('ECB_MRO', 2.15, 2.65, '由6个月前锚(观测 2025-06-11)的 2.15%', '观测 2026-09-16)的 2.65%'), ('ECB_DFR', 2.0, 2.5, '由 2.0% 升至 2.5%', '由 2.0% 升至 2.5%')]:
    d6, v6 = c.obe(m, '2026-05-23'); dl, vl = c.obe(m, A)
    n('②', 'series_store.' + m + ' 末观测<=2026-05-23', v6, r6, str(r6), s6)
    n('②', 'series_store.' + m + ' 末观测<=截止日', vl, rl, str(rl), sl)
    t('②', 'series_store.' + m + ' 6个月前锚观测日', d6, '2025-06-11', '2025-06-11', '由6个月前锚(观测 2025-06-11)的 2.15%')
    t('②', 'series_store.' + m + ' 最新一期锚观测日', dl, '2026-09-16', '2026-09-16', '观测 2026-09-16)的 2.65%')
CM = {'EA_HICP_YOY': c.pub, 'JP_CPI_YOY': c.pub, 'JP_CPI_TOKYO_YOY': c.pub, 'JP_POLICY_RATE': c.pub, 'ECB_MRO': None, 'ECB_DFR': None}
for cell in PV:
    m = cell['metric_id']
    for lab, aday in [('6个月前', '2026-05-23'), ('最新一期', A)]:
        an = cell['anchors'][lab]
        dd, vv = (c.obe(m, aday) if m.startswith('ECB') else c.vis(m, aday))
        pp = dd if m.startswith('ECB') else c.pub(m, dd[:7])
        e('②', 'engine point_values.' + m + '.' + lab + '.value', vv, an['value'])
        e('②', 'engine point_values.' + m + '.' + lab + '.observation_date', dd, an['observation_date'])
        e('②', 'engine point_values.' + m + '.' + lab + '.publication_date', pp, an['publication_date'])
        e('②', 'engine point_values.' + m + '.' + lab + '.status', 'ok', an['status'])
EXP = {('EA', 0): ('ECB_MRO', 2.15, '2025-06'), ('EA', 1): ('ECB_MRO', 2.65, '2026-09'), ('EA', 2): ('ECB_DFR', 2.0, '2025-06'), ('EA', 3): ('ECB_DFR', 2.5, '2026-09'), ('EA', 4): ('EA_HICP_YOY', 3.0, '2026-04'), ('EA', 5): ('EA_HICP_YOY', 4.0, '2026-10'),
       ('JP', 0): ('JP_POLICY_RATE', 0.727, '2026-04'), ('JP', 1): ('JP_POLICY_RATE', 1.227, '2026-10'), ('JP', 2): ('JP_CPI_YOY', 1.38, '2026-04'), ('JP', 3): ('JP_CPI_YOY', 2.44, '2026-10'), ('JP', 4): ('JP_CPI_TOKYO_YOY', 1.42, '2026-04'), ('JP', 5): ('JP_CPI_TOKYO_YOY', 2.73, '2026-10')}
for rg in c.aj['reader_map']['regions']:
    for j, a in enumerate(rg['anchor_echo']):
        m, v, ym = EXP[(rg['region'], j)]
        dd, vv = (c.obe(m, '2026-05-23' if a['anchor'] == '6个月前' else A) if m.startswith('ECB') else c.vis(m, '2026-05-23' if a['anchor'] == '6个月前' else A))
        e('②', 'anchor_echo ' + rg['region'] + '[' + str(j) + '] metric_id', a['metric_id'], m)
        e('②', 'anchor_echo ' + rg['region'] + '[' + str(j) + '] value (series_store 直算)', vv, a['value'])
        e('②', 'anchor_echo ' + rg['region'] + '[' + str(j) + '] observation_month (series_store 直算)', dd[:7], a['observation_month'])

# ---------- (3) yoy ----------
EA = 'EA_HICP_YOY'; JP = 'JP_CPI_YOY'; TK = 'JP_CPI_TOKYO_YOY'; PR = 'JP_POLICY_RATE'
n('③', 'series_store.' + EA + '@2025-10-01', c.mv(EA, '2025-10'), 2.1, '百分之二点一', '(2025-10:欧元区百分之二点一、日本百分之二点九九)')
n('③', 'series_store.' + JP + '@2025-10-01', c.mv(JP, '2025-10'), 2.99, '百分之二点九九', '日本百分之二点九九)')
n('③', 'series_store.' + EA + '@2026-10-01', c.mv(EA, '2026-10'), 4.0, '百分之四点零', '欧元区HICP同比百分之四点零(观测 2026-10')
n('③', 'series_store.' + JP + '@2026-10-01', c.mv(JP, '2026-10'), 2.44, '百分之二点四四', '日本全国CPI同比百分之二点四四(观测 2026-10')
n('③', 'EA@2026-10 − JP@2026-10', c.mv(EA, '2026-10') - c.mv(JP, '2026-10'), 1.56, '一点五六', '最新水平欧元区高于日本约一点五六个百分点')
n('③', 'EA@2026-10 − EA@2025-10', c.mv(EA, '2026-10') - c.mv(EA, '2025-10'), 1.9, '一点九', '欧元区抬升一点九个百分点')
n('③', '|JP@2026-10 − JP@2025-10|', abs(c.mv(JP, '2026-10') - c.mv(JP, '2025-10')), 0.55, '零点五五', '日本回落约零点五五个百分点', tol=0.006)
o('③', '方向: EA 同比对照向上', c.mv(EA, '2026-10') > c.mv(EA, '2025-10'), '上升')
o('③', '方向: JP 同比对照向下', c.mv(JP, '2026-10') < c.mv(JP, '2025-10'), '下降')
c.has_text('③', '判断档文字', '同比对照方向相反')
n('③', 'headline EA 2025-10', c.mv(EA, '2025-10'), 2.1, '2.1', '2025-10 为 2.1)')
n('③', 'headline JP 2025-10', c.mv(JP, '2025-10'), 2.99, '2.99', '2025-10 为 2.99)')
n('③', 'regions EA 相比去年同月', c.mv(EA, '2026-10') - c.mv(EA, '2025-10'), 1.9, '1.9', '高 1.9 个百分点')
n('③', 'regions JP |相比去年同月|', abs(c.mv(JP, '2026-10') - c.mv(JP, '2025-10')), 0.55, '0.55', '低 0.55 个百分点', tol=0.006)
o('③', 'series_store.' + TK + ' 无 2025-10 观测', c.mv(TK, '2025-10') is None, [d for d in c.S[TK]['dates'] if d[:4] == '2025'])
t('③', 'series_store.' + TK + '.dates[0]', c.first(TK)[0][:7], '2026-01', '2026-01', '序列自 2026-01 起')
e('③', 'series_store.' + TK + ' 观测数', c.n(TK), 10)
o('③', '注册表 calc: JP_CPI_YOY=双基期档各自严格同月同比后拼接', ('严格同月同比' in c.RM[JP]['calc']) and ('zmi2025aa' in c.RM[JP]['calc']) and ('zmi2020aa' in c.RM[JP]['calc']), c.RM[JP]['calc'][-60:])
o('③', '注册表 calc: EA_HICP_YOY=年度变化率', '年度变化率' in c.RM[EA]['calc'], c.RM[EA]['calc'][:60])
c.has_text('③', '判断档文字', '该序列为引擎按注册表口径自算的同比值——双基期档各自同月同比后拼接,非官方公布值直取')
n('③', 'series_store.' + JP + '@2026-09-01', c.mv(JP, '2026-09'), 2.16, '2.16', '抽验 2026-09 为 2.16 对官方 2.1')
o('③', '注册表 JP_CPI_YOY.calc 含官方抽验', '官方公布值抽验一致(2026-09=2.16 vs 官方2.1)' in c.RM[JP]['calc'], c.RM[JP]['calc'][-34:])
c.diag.append('REG JP_CPI_YOY calc tail: ' + c.RM[JP]['calc'][-70:])
c.diag.append('REG JP_CPI_YOY source_symbol: ' + c.RM[JP]['source_symbol'])

# ---------- (4) policy ----------
chm = c.changes('ECB_MRO'); chd = c.changes('ECB_DFR')
def chg(lst, d):
    for x in lst:
        if x[0] == d:
            return x
    return None
for lab, lst, d, f_, t_ in [('MRO', chm, '2026-06-17', 2.15, 2.4), ('MRO', lst2 := chm, '2026-09-16', 2.4, 2.65), ('DFR', chd, '2026-06-17', 2.0, 2.25), ('DFR', chd, '2026-09-16', 2.25, 2.5)]:
    x = chg(lst, d)
    o('④', 'series_store.ECB_' + lab + ' 变更点 ' + d, x is not None and close(x[1], f_) and close(x[2], t_), x)
    o('④', 'series_store.ECB_' + lab + ' 变更幅 ' + d, x is not None and close((x[2] - x[1]) * 100, 25, tol=0.6), round((x[2] - x[1]) * 100, 3))
inw = [x for x in chm if '2026-05-23' <= x[0] <= A]
o('④', 'series_store.ECB_MRO 六个月窗内变更点数=2', len(inw) == 2, [x[0] for x in inw])
inw = [x for x in chd if '2026-05-23' <= x[0] <= A]
o('④', 'series_store.ECB_DFR 六个月窗内变更点数=2', len(inw) == 2, [x[0] for x in inw])
c.diag.append('ECB_MRO changes: ' + str([(x[0], x[1], x[2]) for x in chm if x[0] >= '2024-01-01']))
c.diag.append('ECB_DFR changes: ' + str([(x[0], x[1], x[2]) for x in chd if x[0] >= '2024-01-01']))
c.diag.append('ECB_MRO first obs ' + str(c.first('ECB_MRO')) + ' DFR first ' + str(c.first('ECB_DFR')))
for d, rd in [('2026-06-17', '2026-06-11'), ('2026-09-16', '2026-09-10')]:
    t('④', '独立推算: ' + d + ' 生效日前上一个周四', prev_thu(d), rd, rd, '决议日 ' + rd)
    t('④', '星期: 序列变更日 ' + d, wd(d), '周三', '周三', '', ) if False else None
    o('④', '序列变更日 ' + d + ' 为周三', D(d).weekday() == 2, wd(d))
c.has_text('④', '判断档文字', '决议日 2026-06-11 系引擎按『生效日前上一个周四』惯例自变更日回推【推断】')
e('④', 'engine policy_dates.decision (最新一期)', [x for x in PV if x['metric_id'] == 'ECB_MRO'][0]['anchors']['最新一期']['policy_dates']['decision'], '2026-09-10')
e('④', 'engine policy_dates.decision (6个月前)', [x for x in PV if x['metric_id'] == 'ECB_MRO'][0]['anchors']['6个月前']['policy_dates']['decision'], '2025-06-05')
t('④', '独立推算: 2025-06-11 生效日前上一个周四', prev_thu('2025-06-11'), '2025-06-05', '2025-06-05', '')
ecb_cal = [x for x in c.cal['entries'] if 'ECB' in json.dumps(x, ensure_ascii=False) or x.get('metric_id') in ('ECB_MRO', 'ECB_DFR')]
o('④', '冻结日历 ECB 条目数=0', len(ecb_cal) == 0, len(ecb_cal))
c.has_text('④', '判断档文字', '冻结发布日历对欧央行无实录条目')
o('④', '注册表 ECB_MRO.release_semantics 含「决议公布后生效并当日更新系列」', '决议公布后生效并当日更新系列' in c.RM['ECB_MRO']['release_semantics'], c.RM['ECB_MRO']['release_semantics'][:24])
c.has_text('④', '判断档文字', '注册表该序列 release_semantics 另载决议公布后生效并当日更新系列,两口径不一')
e('④', '注册表 ECB_DFR.freshness.max_calendar_lag_days', c.RM['ECB_DFR']['freshness']['max_calendar_lag_days'], 10)
e('④', '注册表 ECB_DFR.freshness.decision_dated', c.RM['ECB_DFR']['freshness'].get('decision_dated'), True)
e('④', '注册表 ECB_MRO.freshness.decision_dated', c.RM['ECB_MRO']['freshness'].get('decision_dated'), True)
GA = c.snap['gate_a']
e('④', 'gate_a.status', GA['status'], 'DEGRADED')
for m in ['ECB_DFR', 'ECB_MRO']:
    e('④', 'gate_a.noncore_degraded 含 ' + m, m in GA['noncore_degraded'], True)
    e('④', 'facts.' + m + '.quality_status', c.fact(m)['quality_status'], 'DEGRADED')
c.diag.append('FACT ECB_MRO issues: ' + json.dumps(c.fact('ECB_MRO')['issues'], ensure_ascii=False))
n('④', 'facts.ECB_DFR.observation_date 距截止日天数', days(c.fact('ECB_DFR')['observation_date'], A), 68, '68', '序列止于 2026-09-16(距截止 68 天')
o('④', 'facts.ECB_DFR.issues[0].message 含「滞后68天(>10天」', ('滞后68天' in c.fact('ECB_DFR')['issues'][0]['message']) and ('>10天' in c.fact('ECB_DFR')['issues'][0]['message']), c.fact('ECB_DFR')['issues'][0]['message'])
n('④', 'C3② 观测日距研究截止', days('2026-09-16', A), 68, '六十八', '距研究截止 2026-11-23 六十八天')
n('④', '契约 STALE 披露: 观测滞后', days('2026-09-16', A), 68, '六十八', '数值一致、观测滞后六十八天')
e('④', 'engine point_values ECB_DFR 最新一期 status', [x for x in PV if x['metric_id'] == 'ECB_DFR'][0]['anchors']['最新一期']['status'], 'ok')
c.has_text('④', '判断档文字', '而研究计划点值格记该锚 status=ok,引擎各面不一')
jp_cal = [x for x in c.cal['entries'] if x.get('metric_id') == 'JP_POLICY_TARGET']
e('④', '冻结日历 JP_POLICY_TARGET 条目数', len(jp_cal), 2)
e('④', '冻结日历 决议条目.decision_date', jp_cal[0]['decision_date'], '2026-09-18')
e('④', '冻结日历 决议条目.effective_on', jp_cal[0]['effective_on'], '2026-09-24')
e('④', '冻结日历 决议条目.target_value', jp_cal[0]['target_value'], 1.25)
e('④', '冻结日历 决议条目.basis', jp_cal[0]['basis'], 'user_directive')
e('④', '冻结日历 维持条目.decision_date', jp_cal[1]['decision_date'], '2026-10-30')
e('④', '冻结日历 维持条目.target_value', jp_cal[1]['target_value'], 1.25)
e('④', '冻结日历 维持条目.basis', jp_cal[1]['basis'], 'user_directive')
e('④', '冻结日历 维持条目.kind', jp_cal[1]['kind'], 'policy_maintenance')
o('④', '冻结日历两条均无前值字段', not any(k in jp_cal[i] for i in (0, 1) for k in ('previous_value', 'prev_value', 'old_value', 'from_value', 'prior_target')), sorted(jp_cal[0].keys()))
c.has_text('④', '判断档文字', '2026-09-18 决议、2026-09-24 生效,2026-10-30 会议确认维持不变')
c.has_text('④', '判断档文字', '政策目标利率 1.25%,2026-09-18 决议、2026-09-24 生效,2026-10-30 会议确认维持不变(无新调整、无生效变动)')
c.has_text('④', '判断档文字', '实录无前值,属【推断】')
n('④', '冻结日历 target_value', jp_cal[0]['target_value'], 1.25, '一点二五', '载日本央行政策目标利率约一点二五')
n('④', '冻结日历 target_value', jp_cal[1]['target_value'], 1.25, '1.25', '日本央行目标 1.25%(2026-09-18 决议')
n('④', '冻结日历 target_value', jp_cal[0]['target_value'], 1.25, '1.25', 'BOJ 2026-09-18 决议、2026-09-24 生效,目标 1.25%')
n('④', '冻结日历 target_value', jp_cal[1]['target_value'], 1.25, '1.25', 'BOJ 政策目标再上调一级(或月均中枢续升,目标现约 1.25%)')
n('④', '冻结日历 target_value', jp_cal[1]['target_value'], 1.25, '1.25', 'BOJ 维持目标约 1.25% 不变')
o('④', '注册表无 JP_POLICY_TARGET', 'JP_POLICY_TARGET' not in c.RM, sorted(k for k in c.RM if 'JP_POLICY' in k))
o('④', 'series_store 无 JP_POLICY_TARGET', 'JP_POLICY_TARGET' not in c.S, None)
e('④', 'engine dimension_gaps[0].gap', RP['dimension_gaps'][0]['gap'], 'registry_absent')
e('④', 'engine dimension_gaps[0].metric_id', RP['dimension_gaps'][0]['metric_id'], 'JP_POLICY_TARGET')
c.has_text('④', '判断档文字', '注册表无 JP_POLICY_TARGET(检索范围=注册表 economy=JP 面+快照 series_store+采集档通道)')
n('④', 'series_store.' + PR + '@2025-11-01', c.mv(PR, '2025-11'), 0.478, '零点四七八', '自 2025-11 月均零点四七八升至 2026-10 月均一点二二七')
n('④', 'series_store.' + PR + '@2026-10-01', c.mv(PR, '2026-10'), 1.227, '一点二二七', '升至 2026-10 月均一点二二七')
n('④', 'days(2026-10-30→截止)', days('2026-10-30', A), 24, '二十四', '2026-10-30 至研究截止二十四天内')
n('④', 'series_store.ECB_MRO 末值', c.last('ECB_MRO')[1], 2.65, '百分之二点六五', '最新生效水平为百分之二点六五')
n('④', 'series_store.ECB_MRO@2025-06-11', c.at('ECB_MRO', '2025-06-11'), 2.15, '百分之二点一五', '六个月前为百分之二点一五')
n('④', 'MRO − 日银目标(日历)', c.last('ECB_MRO')[1] - jp_cal[0]['target_value'], 1.4, '一点四', '按 MRO 计约一点四')
n('④', 'DFR − 日银目标(日历)', c.last('ECB_DFR')[1] - jp_cal[0]['target_value'], 1.25, '一点二五', '按 DFR 计约一点二五个百分点')
n('④', 'series_store.ECB_MRO 末值', c.last('ECB_MRO')[1], 2.65, '二点六五', '(二点六五/二点五 vs BOJ 目标约一点二五)')
n('④', 'series_store.ECB_DFR 末值', c.last('ECB_DFR')[1], 2.5, '二点五', '二点五 vs BOJ 目标约一点二五)')
n('④', '冻结日历 target_value', jp_cal[0]['target_value'], 1.25, '一点二五', '二点五 vs BOJ 目标约一点二五)')
n('④', 'ECB 单次变更幅(bp)', (chg(chm, '2026-06-17')[2] - chg(chm, '2026-06-17')[1]) * 100, 25, '二十五', '两次各二十五个基点')
n('④', 'ECB 两次合计(bp)', (c.last('ECB_MRO')[1] - c.at('ECB_MRO', '2025-06-11')) * 100, 50, '五十', '两次合计五十个基点')
n('④', 'days(09-16 生效→09-24 生效)', days('2026-09-16', '2026-09-24'), 8, '八', '同口径相隔八天')
n('④', 'days(09-10 决议→09-18 决议)', days('2026-09-10', '2026-09-18'), 8, '八', '按引擎回推的决议日计亦为八天')
o('④', '09-16 生效在前、09-18 决议在后', D('2026-09-16') < D('2026-09-18') and D('2026-09-10') < D('2026-09-18'), '2026-09-16<2026-09-18; 2026-09-10<2026-09-18')
o('④', 'ECB 生效日与 BOJ 生效日同月(2026-09)', '2026-09-16'[:7] == '2026-09-24'[:7], '2026-09')
c.has_text('④', '判断档文字', '月频证据下先后未定')
for m in ['USDJPY', 'SPX', 'VIX']:
    n('④', 'series_store.' + m + '@2026-11-23', c.at(m, '2026-11-23'), {'USDJPY': 159.35, 'SPX': 7203.85, 'VIX': 27.01}[m], str({'USDJPY': 159.35, 'SPX': 7203.85, 'VIX': 27.01}[m]), {'USDJPY': 'USDJPY 水平为 159.35', 'SPX': 'SPX 水平为 7203.85', 'VIX': 'VIX 水平为 27.01'}[m])
    e('④', 'facts.' + m + '.value@2026-11-23', c.fact(m)['value'], {'USDJPY': 159.35, 'SPX': 7203.85, 'VIX': 27.01}[m])
    e('④', 'facts.' + m + '.observation_date', c.fact(m)['observation_date'], '2026-11-23')
# JP monthly path
PRV = {'2025-11': 0.478, '2025-12': 0.557, '2026-01': 0.728, '2026-02': 0.728, '2026-03': 0.728, '2026-04': 0.727, '2026-05': 0.727, '2026-06': 0.841, '2026-07': 0.978, '2026-08': 0.977, '2026-09': 1.043, '2026-10': 1.227}
for ym, v in PRV.items():
    e('④', 'series_store.' + PR + '@' + ym, c.mv(PR, ym), v)
chp = c.changes(PR)
c.diag.append('JP_POLICY_RATE changes since 2025-01: ' + str(chp[-8:]))
n('④', 'JP 月均 6个月锚间净变动(bp)', (c.mv(PR, '2026-10') - c.mv(PR, '2026-04')) * 100, 50, '五十', '六个月锚间净变动约五十个基点')
n('④', 'JP 月均 6个月锚间净变动(bp)', (c.mv(PR, '2026-10') - c.mv(PR, '2026-04')) * 100, 50, '50', '六个月锚间净 +50bp')
n('④', 'JP 月均 四台阶之和(bp)', (c.mv(PR, '2026-06') - c.mv(PR, '2026-05')) * 100 + (c.mv(PR, '2026-07') - c.mv(PR, '2026-06')) * 100 + (c.mv(PR, '2026-09') - c.mv(PR, '2026-08')) * 100 + (c.mv(PR, '2026-10') - c.mv(PR, '2026-09')) * 100, 50, '50', '1.043→1.227(合计 +50bp)')
n('④', 'JP 月均 近12月净变动(bp)', (c.mv(PR, '2026-10') - c.mv(PR, '2025-11')) * 100, 75, '75', '约 +75bp')
n('④', 'JP 月均 引擎一年窗净变动(bp)', (c.mv(PR, '2026-10') - c.mv(PR, '2025-11')) * 100, 75, '75', '净 +75bp=六个变动点之和')
PWE = [x for x in PV if x['metric_id'] == PR][0]['policy_window_path']['events']
e('④', 'policy_window_path JP 事件数', len(PWE), 6)
e('④', 'policy_window_path JP net_bp', [x for x in PV if x['metric_id'] == PR][0]['policy_window_path']['net_bp'], 75)
o('④', 'policy_window_path JP delta_bp 之和=75', sum(x['delta_bp'] for x in PWE) == 75, sum(x['delta_bp'] for x in PWE))
o('④', 'policy_window_path JP 六事件与 series_store 变更点(幅>=0.5bp)逐项一致', [(x['date'], x['from'], x['to']) for x in PWE] == [(a, b, cc) for a, b, cc in chp if '2025-11-23' <= a <= A and abs(cc - b) >= 0.005], 'series_store 一年窗内原始变更点: ' + str([(a, round((cc - b) * 100, 1)) for a, b, cc in chp if '2025-11-23' <= a <= A]) + ' ; 原始变动之和(bp)=' + str(round(sum((cc - b) * 100 for a, b, cc in chp if '2025-11-23' <= a <= A), 2)))
e('④', 'policy_window_path JP window', [x for x in PV if x['metric_id'] == PR][0]['policy_window_path']['window'], ['2025-11-23', '2026-11-23'])
e('④', 'policy_window_path JP window_start_observation', [x for x in PV if x['metric_id'] == PR][0]['policy_window_path']['window_start_observation'], '2025-11-01')
c.has_text('④', '判断档文字', '窗口 2025-11-23..2026-11-23')
c.has_text('④', '判断档文字', '净 +75bp=六个变动点之和')
for lab, m, f_, t_ in [('MRO', 'ECB_MRO', '2.15→2.4', None), ('DFR', 'ECB_DFR', None, None)]:
    pw = [x for x in PV if x['metric_id'] == m][0]['policy_window_path']
    e('④', 'policy_window_path ' + m + ' events', [(x['date'], x['from'], x['to'], x['delta_bp'], x['decision_date']) for x in pw['events']], [('2026-06-17', 2.15 if m == 'ECB_MRO' else 2.0, 2.4 if m == 'ECB_MRO' else 2.25, 25, '2026-06-11'), ('2026-09-16', 2.4 if m == 'ECB_MRO' else 2.25, 2.65 if m == 'ECB_MRO' else 2.5, 25, '2026-09-10')])
    e('④', 'policy_window_path ' + m + ' net_bp', pw['net_bp'], 50)
S2 = '2026-06-17 生效,MRO 2.15→2.4、DFR 2.0→2.25;2026-09-16 生效,MRO 2.4→2.65、DFR 2.25→2.5'
n('④', 'series_store.ECB_MRO@2026-06-17', c.at('ECB_MRO', '2026-06-17'), 2.4, '2.4', 'MRO 2.15→2.4、DFR 2.0→2.25')
n('④', 'series_store.ECB_DFR@2026-06-17', c.at('ECB_DFR', '2026-06-17'), 2.25, '2.25', 'DFR 2.0→2.25;')
n('④', 'series_store.ECB_MRO@2026-09-16', c.at('ECB_MRO', '2026-09-16'), 2.65, '2.65', 'MRO 2.4→2.65')
n('④', 'series_store.ECB_DFR@2026-09-16', c.at('ECB_DFR', '2026-09-16'), 2.5, '2.5', 'DFR 2.25→2.5')
n('④', 'series_store.ECB_MRO@2025-06-11', c.at('ECB_MRO', '2025-06-11'), 2.15, '2.15', 'MRO 2.15→2.4')
n('④', 'series_store.ECB_DFR@2025-06-11', c.at('ECB_DFR', '2025-06-11'), 2.0, '2.0', 'DFR 2.0→2.25;')
n('④', 'series_store.' + PR + '@2026-10', c.mv(PR, '2026-10'), 1.227, '1.227', '月均口径六个月锚间由 0.727 升至 1.227')
n('④', 'series_store.' + PR + '@2026-04', c.mv(PR, '2026-04'), 0.727, '0.727', '月均口径六个月锚间由 0.727 升至 1.227')
for ym, v in [('2026-06', 0.841), ('2026-07', 0.978), ('2026-09', 1.043), ('2026-10', 1.227), ('2026-08', 0.977), ('2025-11', 0.478)]:
    n('④', 'series_store.' + PR + '@' + ym, c.mv(PR, ym), v, str(v), '六个月锚间台阶 2026-06 0.727→0.841、2026-07 0.841→0.978、2026-09 0.977→1.043、2026-10 1.043→1.227' if ym != '2026-08' and ym != '2025-11' else ('此后逐月路径 2026-08 0.977' if ym == '2026-08' else '近 12 个月月均由 2025-11 的 0.478'))
n('④', 'series_store.ECB_MRO 末值', c.last('ECB_MRO')[1], 2.65, '2.65', '主要再融资利率 2.65%/存款便利利率 2.5%')
n('④', 'series_store.ECB_DFR 末值', c.last('ECB_DFR')[1], 2.5, '2.5', '存款便利利率 2.5%,日本央行目标 1.25%')
n('④', 'series_store.ECB_MRO 末值', c.last('ECB_MRO')[1], 2.65, '2.65', 'MRO 2.65% vs BOJ 目标 1.25%')
n('④', '冻结日历 target_value', jp_cal[0]['target_value'], 1.25, '1.25', 'MRO 2.65% vs BOJ 目标 1.25%')
# Fed
for m in ['DFEDTARU', 'DFEDTARL']:
    cf = c.changes(m)
    c.diag.append(m + ' last changes: ' + str(cf[-3:]) + ' last obs ' + str(c.last(m)))
t('④', 'series_store.DFEDTARU 最近变更日', c.changes('DFEDTARU')[-1][0], '2026-09-17', '2026-09-17', '美联储 2026-09-17 生效')
t('④', 'series_store.DFEDTARL 最近变更日', c.changes('DFEDTARL')[-1][0], '2026-09-17', '2026-09-17', '美联储 2026-09-17 生效;日央行')
n('④', 'series_store.DFEDTARL@2026-11-23', c.at('DFEDTARL', '2026-11-23'), 3.75, '3.75', '联邦基金目标区间 3.75%–4.00%')
n('④', 'series_store.DFEDTARU@2026-11-23', c.at('DFEDTARU', '2026-11-23'), 4.0, '4.00', '3.75%–4.00%,DFEDTARL/DFEDTARU 2026-11-23 观测')
t('④', 'series_store.DFEDTARL/DFEDTARU 末观测日', c.last('DFEDTARL')[0], '2026-11-23', '2026-11-23', 'DFEDTARL/DFEDTARU 2026-11-23 观测,不在本轮证据索引')
EIDS = set(x['ref'].split('@')[0] for x in c.rep['evidence_index'])
o('④', 'DFEDTARL/DFEDTARU 不在证据索引', not ({'DFEDTARL', 'DFEDTARU'} & EIDS), sorted({'DFEDTARL', 'DFEDTARU'} & EIDS))
o('④', '窗(2026-10-23..截止)内 ECB/Fed 序列无变更点', not [x for m in ('ECB_MRO', 'ECB_DFR', 'DFEDTARU', 'DFEDTARL') for x in c.changes(m) if '2026-10-23' <= x[0] <= A], 'none')
o('④', '窗(2026-10-23..截止)内 JP 月均观测日口径无变更点', not [x for x in chp if '2026-10-23' <= x[0] <= A], 'none')
c.has_text('④', '判断档文字', '窗内三地均无政策利率变动点(序列面最近变动: 欧央行 2026-09-16 生效、美联储 2026-09-17 生效;日央行 2026-09-18 决议 2026-09-24 生效')
n('④', 'days(2025-06-11→2026-06-17) 两序列维持期', days('2025-06-11', '2026-06-17'), 371, '371', '维持 2.15/2.0 共 371 天')
o('④', '2025-06-11 至 2026-06-17 间两序列无变更点', not [x for m in ('ECB_MRO', 'ECB_DFR') for x in c.changes(m) if '2025-06-11' < x[0] < '2026-06-17'], 'none')
n('④', 'days(2026-06-17→2026-09-16) 两次变更间隔', days('2026-06-17', '2026-09-16'), 91, '91', '两次变更相隔 91 天')
c.save('a')
