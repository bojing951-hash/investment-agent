# s10e_final.py <snap> <rep> <cal> <reg> <aj> <out>  -- part E: date/month closure + remaining value occurrences in l3
import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:7])
RP = c.rep['research_plan']; A = c.asof
EA = 'EA_HICP_YOY'; JP = 'JP_CPI_YOY'; TK = 'JP_CPI_TOKYO_YOY'; PR = 'JP_POLICY_RATE'
PV = RP['point_values']['cells']
jc = [x for x in c.cal['entries'] if x.get('metric_id') == 'JP_POLICY_TARGET']
JT = [x for x in jc if str(x.get('entry_id', '')).startswith('RC-JP-BOJ-TARGET')][0]
JM = [x for x in jc if str(x.get('entry_id', '')).startswith('RC-JP-BOJ-MAINT')][0]
chd = c.changes('ECB_DFR'); chm = c.changes('ECB_MRO')
wd_ = [x for x in chd if '2026-05-23' <= x[0] <= A]; wm_ = [x for x in chm if '2026-05-23' <= x[0] <= A]
pwe = [x for x in PV if x['metric_id'] == 'ECB_MRO'][0]['policy_window_path']['events']
vix = c.S['VIX']
def lastfri(ym):
    d = D(mend(ym))
    while d.weekday() != 4:
        d -= dt.timedelta(days=1)
    return d.isoformat()
amf = RP['asset_moves']['rows'][0]['window']['from']
pwc = [x for x in PV if x['metric_id'] == PR][0]['policy_window_path']
PDF = RP['policy_doc_facts']
fed = [d for d, a_, b_ in c.changes('DFEDTARU') if d <= A][-1]
TOL = 1e-6
SKIP = ('evidence_refs', 'agent_declaration', '.id', 'metric_id', 'sensitive_variables', 'secondary_metric_ids', 'schema_version')
def skip(p):
    return any(k in p for k in SKIP)
# ---------- E1 distinct full dates ----------
EVD = {}
def ev(d, comp, src):
    EVD[d] = (str(comp) if comp is not None else None, src)
ev('2026-11-23', str(c.snap.get('research_as_of'))[:10], '快照 research_as_of 日期=研究截止/实际覆盖日')
ev('2026-11-30', RP['as_of_declared']['requested_as_of'], 'research_plan.as_of_declared.requested_as_of(请求月末,未到)')
ev('2026-05-23', RP['question_window']['windows'][0]['from'], 'question_window.windows[0].from(回看窗起)')
ev('2025-11-23', pwc['window'][0], 'point_values JP_POLICY_RATE.policy_window_path.window[0](一年窗起)')
ev('2026-11-16', c.pub(EA, '2026-10'), '推定发布规则 EA_HICP 月末+16 (2026-10 期)')
ev('2026-11-20', c.pub(JP, '2026-10'), '推定发布规则 全国CPI 月末+20 (2026-10 期); 兼=截止前最后收盘日')
ev('2026-10-30', c.pub(TK, '2026-10'), '推定发布规则 东京 月末−1 (2026-10 期); 兼=日历维持条目决议日')
ev('2026-11-05', c.pub(PR, '2026-10'), '推定发布规则 月均 月末+5 (2026-10 期)')
ev('2026-05-05', c.pub(PR, '2026-04'), '推定发布规则 月均 月末+5 (2026-04 期)')
ev('2026-11-21', c.cal['updated'], '冻结日历 updated')
ev('2026-09-18', JT['decision_date'], '日历 RC-JP-BOJ-TARGET 决议日')
ev('2026-09-24', JT['effective_on'], '日历 RC-JP-BOJ-TARGET 生效日')
ev('2026-06-17', wm_[0][0], 'series_store.ECB_MRO/DFR 窗内变更日1(=生效日)')
ev('2026-09-16', wm_[1][0], 'series_store.ECB_MRO/DFR 窗内变更日2(=生效日)')
ev('2026-06-11', pwe[-2]['decision_date'] if pwe[-2]['decision_date'] == prev_thu(wm_[0][0]) else None, '引擎 policy_window_path.events 决议日=生效日前上一个周四(回推)')
ev('2026-09-10', pwe[-1]['decision_date'] if pwe[-1]['decision_date'] == prev_thu(wm_[1][0]) else None, '引擎 policy_window_path.events 决议日=生效日前上一个周四(回推)')
ev('2026-09-17', plus(wm_[1][0], 1), 'ECB 末变更日次日(区间起)')
ev('2025-06-11', c.obe('ECB_MRO', '2026-05-23')[0], '六个月前锚在值观测日(obe@2026-05-23)')
ev('2026-11-19', c.last('UST_10Y')[0], 'series_store.UST_10Y 末观测日; JGB 事实行观测日')
ev('2026-10-23', amf, 'asset_moves 月窗 window.from')
ev('2026-09-29', c.pub(TK, '2026-09'), '推定发布规则 东京 月末−1 (2026-09 期)')
ev('2026-08-30', c.pub(TK, '2026-08'), '推定发布规则 东京 月末−1 (2026-08 期)')
ev('2026-06-26', lastfri('2026-06'), '2026-06 最后一个周五(=引擎 publication_rule 所载官方实录锚 6月分)')
ev('2026-11-18', PDF[0]['published_on'], 'policy_doc_facts FOMC 纪要 published_on; 兼=VIX 收盘日')
ev('2027-02-15', c.aj['l4']['scenarios'][0]['rows']['trigger']['deadline'], 'l4 情景时限(晚于 2026-12 期推定入档日 ' + c.pub(EA, '2026-12') + ')')
ev('2026-05-01', c.md(EA, '2026-05'), 'series_store.EA_HICP_YOY 2026-05 期观测日(月初); JP_CPI_YOY 同月观测日=' + str(c.md(JP, '2026-05')))
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
    if '2026-11-04' <= d <= A and d not in EVD:
        ev(d, d, 'series_store.VIX 观测日(收盘路径)')
DATE = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
found = {}
for i, (path, s) in enumerate(c.leaves):
    if skip(path):
        continue
    for mt in DATE.finditer(s):
        found.setdefault(mt.group(0), []).append((i, mt.start(), mt.end()))
nm = 0
for d in sorted(found):
    comp, src = EVD.get(d, (None, '【无证据映射】'))
    for (i, a_, b_) in found[d]:
        c.cover.add((i, a_, b_))
    ok = comp == d
    if not ok:
        nm += 1
    c.pts.append({'sec': 'E-日期', 'src': src, 'comp': comp, 'rep': d, 'tok': d, 'ok': ok, 'where': '(全文 ' + str(len(found[d])) + ' 处)', 'note': ''})
c.diag.append('E 日期: distinct ' + str(len(found)) + ' 未映射/偏离 ' + str(nm) + ' : ' + str([d for d in sorted(found) if d not in EVD]))
# ---------- E2 secondary-meaning dates ----------
c.txt('E-日期', 'NIKKEI225 末观测日=截止前最后收盘日(' + wd(c.last('NIKKEI225')[0]) + ')', c.last('NIKKEI225')[0], '2026-11-20', '2026-11-20', '2026-11-20 收盘')
c.txt('E-日期', '日历 RC-JP-BOJ-MAINT-2026-10 决议日', JM['decision_date'], '2026-10-30', '2026-10-30', '2026-10-30 会议确认维持')
c.txt('E-日期', '日历 RC-JP-BOJ-MAINT-2026-10 决议日', JM['decision_date'], '2026-10-30', '2026-10-30', '2026-10-30 至研究截止二十四天')
c.txt('E-日期', '日历维持条目决议日(跳升起点距最近政策日)', JM['decision_date'], '2026-10-30', '2026-10-30', '距最近政策日 2026-10-30 为 14 天')
c.txt('E-日期', '推定发布规则 EA 月末+16 (2026-08 期)=与 ECB 生效日同日', c.pub(EA, '2026-08'), '2026-09-16', '2026-09-16', '发布日 2026-09-16 与生效日同日')
c.txt('E-日期', 'series_store.ECB_MRO 前一变更日(其后至 2026-06-17 维持 2.15)', ([x for x in chm if x[0] < wm_[0][0]][-1][0]), '2025-06-11', '2025-06-11', '自 2025-06-11 至 2026-06-17 维持 2.15/2.0 共 371')
c.txt('E-日期', 'series_store.DFEDTARU 最近变更日(美联储生效日)', fed, '2026-09-17', '2026-09-17', '美联储 2026-09-17 生效')
c.txt('E-日期', 'policy_doc_facts[0].published_on', PDF[0]['published_on'], '2026-11-18', '2026-11-18', '会议纪要 2026-11-18 发布')
c.txt('E-日期', 'series_store.VIX 观测日(收盘路径末六日之首)', '2026-11-13', '2026-11-13', '2026-11-13', 'VIX 跳升时点(2026-11-13→2026-11-20)')
# ---------- E3 month strings ----------
YM = re.compile('[0-9]{4}-[0-9]{2}(?![0-9-])')
MON = set()
for m in (EA, JP, TK, PR):
    for d in c.S[m]['dates']:
        if d[:7] >= '2024-01':
            MON.add(d[:7])
for e in c.cal['entries']:
    if str(e.get('obs_from'))[:7] >= '2020-01':
        MON.add(e['obs_from'][:7])
FUT = {'2026-11': 'l4 情景观测月(未来,设定值)', '2026-12': 'l4 情景观测月(未来,设定值)', c.pub(EA, '2026-12')[:7]: '2026-12 期读数推定入档月(月末+16)'}
seen = {}
for i, (path, s) in enumerate(c.leaves):
    if skip(path):
        continue
    for mt in YM.finditer(s):
        seen.setdefault(mt.group(0), []).append((i, mt.start(), mt.end()))
nm = 0
for k in sorted(seen):
    for (i, a_, b_) in seen[k]:
        c.cover.add((i, a_, b_))
    if k in MON:
        comp, src = k, 'series_store(EA/JP/东京/月均)观测月 或 日历条目观测月'
    elif k in FUT:
        comp, src = k, FUT[k]
    else:
        comp, src = None, '【非观测月】'
    nm += 0 if comp == k else 1
    c.pts.append({'sec': 'E-月串', 'src': src, 'comp': comp, 'rep': k, 'tok': k, 'ok': comp == k, 'where': '(全文 ' + str(len(seen[k])) + ' 处)', 'note': ''})
c.diag.append('E 月串: distinct ' + str(len(seen)) + ' 偏离 ' + str(nm) + ' future ' + str([k for k in sorted(seen) if k in FUT]))
# ---------- E4 MM-DD forms ----------
MMD = re.compile('(?<![0-9-])(1[01]-[0-9]{2})(?![0-9])')
okset = set(d[5:] for d in vix['dates'] if d >= '2026-10-01') | {amf[5:]}
seen = {}
for i, (path, s) in enumerate(c.leaves):
    if skip(path):
        continue
    for mt in MMD.finditer(s):
        seen.setdefault(mt.group(1), []).append((i, mt.start(), mt.end()))
nm = 0
for k in sorted(seen):
    for (i, a_, b_) in seen[k]:
        c.cover.add((i, a_, b_))
    ok = k in okset
    nm += 0 if ok else 1
    c.pts.append({'sec': 'E-月日', 'src': 'series_store.VIX 观测日(2026-)/asset 月窗起 2026-10-23', 'comp': k if ok else None, 'rep': k, 'tok': k, 'ok': ok, 'where': '(全文 ' + str(len(seen[k])) + ' 处)', 'note': ''})
c.diag.append('E 月日: distinct ' + str(str(sorted(seen))) + ' 偏离 ' + str(nm))
c.save('e')
