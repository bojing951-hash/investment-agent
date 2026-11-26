#!/usr/bin/env python3
"""make_family_judgment.py <data_tree> <report.json> <out.json> <judgment_path> [code_root]

席位侧工具(Agent 研究席判定档装配;引擎不调用,不属任何自动链路)。
Audit-R33 任务3: 原问直答型工单(日本+欧元区)的席位判定档。结构化
回声=引擎分面块逐字回声;叙述文字=席位研判(措辞、阈值与证伪判据由
席位撰写并固化于本脚本),数值与日期一律由引擎分面块代入,零手敲、
零网络:
  - 总判断/回声注记: 阿拉伯数字(契约逐个绑定引擎面数字/日期部件);
  - L3 正文(矛盾陈述/机制链): 中文数字(本族指标多不在通用文本检查器的
    静态别名表;契约按引擎面数字集合逐个绑定),日期用 ISO 形;
  - L4 情景: 阈值为席位自设(阿拉伯数字),不入数字绑定。
守卫: 只装配「日本+欧元区」且研究截止日在场的工单;其他组合或缺证
(引擎返回缺口型阻断)拒绝装配,须席位另写判定档。
写出前自检: 纪律校验 + 契约验证,不绿不写。"""
import calendar
import datetime
import json
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

tree, rp, _out, jp_out = sys.argv[1:5]
# 数据根(工单冻结输入)与代码根分离: 数据树内可以没有代码
code_root = (sys.argv[5] if len(sys.argv) > 5 else os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(code_root, 'scripts'))
sys.path.insert(0, os.path.join(code_root, 'scripts', 'research_contract'))
sys.path.insert(0, code_root)
rep = json.load(open(rp, encoding='utf-8'))
blk = rep['research_plan']['policy_question']
qt = blk['question_time']
as_of = blk['as_of']
run = rep.get('run') or {}
T = blk['policy_targets']['rows']
P = blk['pending_decisions']['rows']
Y = blk['inflation_yoy']['rows']
# 守卫: 本装配脚本只覆盖「日本+欧元区」两地组合(措辞按该组合撰写);
# 其他组合须席位另写判定档,不得套用。
_regions = {r['region'] for r in T} | {r['region'] for r in P}
if _regions != {'JP', 'EA'} or as_of is None:
    sys.exit('make_family_judgment: 仅支持「日本+欧元区」组合且有研究截止日'
             '(经济体 %s, as_of %r)——其他组合或缺证须席位另写判定档'
             % (sorted(_regions), as_of))
D = '零一二三四五六七八九'


# ── 数值/日期字面 ────────────────────────────────────────────────────
def cn_num(v):
    """1.25→一点二五; 4.0→四点零; 24→二十四; 25→二十五; 105→一百零五"""
    s = repr(float(v)) if isinstance(v, float) else str(int(v))
    if 'e' in s:
        s = '%.6f' % float(v)
    if '.' in s:
        a, _, b = s.partition('.')
        return ''.join(D[int(c)] for c in a) + '点' + ''.join(D[int(c)] for c in b)
    n = int(s)
    if n < 10:
        return D[n]
    if n < 100:
        t, o = divmod(n, 10)
        return (D[t] if t > 1 else '') + '十' + (D[o] if o else '')
    if n < 1000:
        h, r = divmod(n, 100)
        base = D[h] + '百'
        return base if r == 0 else (base + '零' + D[r] if r < 10 else base + cn_num(r))
    return ''.join(D[int(c)] for c in str(n))


def cn_pct(v):
    return '百分之' + cn_num(v)


def fnum(v):
    return '%g' % v


def signed(v):
    return ('+%g' % v) if (v is not None and v > 0) else ('%g' % v)


def fthr(v):
    """阈值字面: 保留一位小数(+1.0 / -0.3 / 0.3)。"""
    return '%+.1f' % v if v > 0 else '%.1f' % v


def fabs1(v):
    """幅度字面(不带号,一位小数)。"""
    return '%.1f' % abs(v)


def md(iso):
    """2026-09-18 → 9 月 18 日"""
    y, m, d = str(iso)[:10].split('-')
    return '%d 月 %d 日' % (int(m), int(d))


def ym_cn(iso):
    y, m = str(iso)[:7].split('-')
    return '%s 年 %d 月' % (y, int(m))


def half_up(x, nd=1):
    q = Decimal(1).scaleb(-nd)
    return float(Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP))


def shift_ym(ym, n):
    y, m = int(ym[:4]), int(ym[5:7])
    tot = y * 12 + (m - 1) + n
    return '%04d-%02d' % (tot // 12, tot % 12 + 1)


def month_end(ym):
    return '%s-%02d' % (ym, calendar.monthrange(int(ym[:4]), int(ym[5:7]))[1])


CONV = {'prev_thursday': '生效日前一个周四', 'prev_day': '决议次日',
        'same_day': '决议当日'}


def conv_text(basis):
    code = str(basis or '').split(':')[-1]
    return CONV.get(code, '惯例 %s' % code) if code else '惯例'


INFL_NAME = {'EA_HICP_YOY': '欧元区 HICP 同比', 'JP_CPI_YOY': '日本全国 CPI 同比',
             'JP_CPI_TOKYO_YOY': '东京都 CPI 同比', 'US_CPI_YOY': '美国 CPI 同比',
             'CN_CPI_YOY': '中国 CPI 同比'}


def short(name):
    """显示名去机构前缀(「欧央行主要再融资利率」→「主要再融资利率」)。"""
    for pre in ('欧央行', '日本央行', '美联储', '人民银行', '欧洲央行'):
        if str(name or '').startswith(pre):
            return str(name)[len(pre):]
    return str(name or '')


def iname(r):
    return INFL_NAME.get(r['metric_id']) or (r.get('display_name') or r['metric_id'])


def trow(region):
    return next((r for r in T if r['region'] == region), None)


def prow(region):
    return next((r for r in P if r['region'] == region), None)


# ── 口径披露(随视图取值: 夹紧形/原问月范围形;版本与公布日口径;缺口逐类点名) ──
_ad = (rep.get('research_plan') or {}).get('as_of_declared') or {}
_rm = qt.get('research_month') or as_of[:7]
if _ad.get('clamped_to_coverage'):
    scope_txt = ('研究截止日=%s(问句研究月 %s: 月末 %s 晚于快照实际覆盖日→取实际'
                 '覆盖日;研究月之后发布的数据不入证据)'
                 % (as_of, _rm, qt.get('research_month_end')))
else:
    scope_txt = ('研究截止日=%s(问句研究月 %s 的月末;不晚于快照版本日 %s→按原问'
                 '月范围,研究月之后发布的数据不入证据)'
                 % (as_of, _rm, _ad.get('snapshot_target_date')))
n_rec = sum(1 for t in T if t.get('status') == 'official_record')
n_conv = sum(1 for t in T if t.get('status') == 'series_convention_derived')
_gaps = blk.get('gaps') or []
_est = [g for g in _gaps if g.get('code') == 'publication_date_estimated']
_pub_parts = []
if n_rec:
    _pub_parts.append('官方政策目标的决议公布日=日历实录(官方公布日)')
if _est:
    _pub_parts.append('其余读数的公布日=引擎规则推定(非日历实录;缺口逐项点名)')
if not _pub_parts:
    _pub_parts.append('各读数公布日均有日历实录')
_vb = blk.get('version_binding') or {}
_hv = bool(_vb.get('historical_view'))
_vbasis = (_vb.get('value_version') or {}).get('basis') or '未声明'
_revised = set((_vb.get('value_version') or {}).get('revised_series') or [])
if _hv:
    vnote = ('版本口径: 研究截止日当日无冻结快照,事实/历史序列/派生值取自较晚'
             '快照 %s(版本日 %s)的截止视图(版本绑定 %s)——声明修订口径的序列为'
             '最新修订值,不得表述为当时首发值'
             % (_vb.get('source_snapshot_id'), _vb.get('source_target_date'), _vbasis))
else:
    vnote = ('版本口径: 事实/历史序列/派生值绑定研究截止日当日冻结快照 %s'
             '(版本绑定 %s)' % (_vb.get('source_snapshot_id'), _vbasis))
_gap_parts = []
for code, txt in (
        ('official_record_missing', '冻结发布日历无序列口径经济体的决议实录'
         '(其目标水平为序列+惯例推定,非官方公布值)'),
        ('pending_unverified', '序列口径经济体已决议待生效的决定不可核验'),
        ('inflation_base_missing', '去年同月基期缺席的读数明写不可判'),
        ('historical_version_missing', '研究截止日无当日冻结版本(缺历史版本)'),
        ('current_target_missing_evidence', '官方政策目标现值缺证'),
        ('publication_date_estimated', '部分读数公布日为规则推定')):
    if any(g.get('code') == code for g in _gaps):
        _gap_parts.append(txt)


def row_vint(r):
    """单条读数的版本口径短句(随版本绑定取值;不把注册表口径标签照抄成
    「最新修订值」——当日冻结快照里的值是当时的采集值)。"""
    mid = r.get('metric_id')
    if _hv and mid in _revised:
        return '最新修订值(非当时首发值;研究截止日当日版本缺席)'
    if _hv:
        return '较晚快照截止视图的采集值'
    if '事后回顾' in str(r.get('vintage') or ''):
        return ('研究截止日当日冻结快照的采集值(序列声明最新修订口径,后续重取'
                '可能修订)')
    return '研究截止日当日冻结快照的采集值'


def pub_word(r):
    """公布日口径字面(引擎行自带;不写死「规则推定」)。"""
    b = str(r.get('publish_basis') or '')
    if b == 'rule_estimated':
        return '规则推定'
    if b.startswith('calendar'):
        return '日历实录'
    return b or '口径未声明'


# ── 总判断(阿拉伯数字,逐个绑定引擎面) ─────────────────────────────────
def target_text(r):
    lab = r.get('label') or r['region']
    st = r.get('status')
    if st == 'official_record' and r.get('target') is not None:
        dec, pub = r.get('decision_date'), r.get('first_publish')
        when = (md(dec) + '公布并决议' if pub == dec else
                '%s决议、%s公布' % (md(dec), md(pub) if pub else '公布日不可得'))
        s = '%s官方政策目标利率 %s%%(日历实录: %s、%s生效' % (
            lab, fnum(r['target']), when, md(r['effective_date']))
        if r.get('last_maintenance'):
            s += ',%s确认维持' % md(r['last_maintenance'])
        return s + ')'
    if st == 'series_convention_derived' and r.get('target') is not None:
        sers = [x for x in (r.get('series_rows') or []) if x.get('value') is not None]
        names = '、'.join('%s %s%%' % (short(x.get('display_name')), fnum(x['value']))
                         for x in sers[:2])
        return ('%s政策目标水平(%s,%s生效)为序列+惯例推定——冻结日历无官方'
                '实录,非官方公布值(决议日 %s系「%s」惯例自生效日回推)'
                % (lab, names, md(r['effective_date']), md(r['decision_date']),
                   conv_text(r.get('decision_basis'))))
    if st == 'current_target_missing_evidence':
        return '%s官方政策目标现值数据不可得(日历实录只有待生效公告)' % lab
    return '%s官方政策目标水平数据不可得(官方实录与政策序列均缺席)' % lab


def pending_text(r):
    lab = r.get('label') or r['region']
    a = r.get('answer')
    w = r.get('window') or {}
    win = '(%s..%s)' % (w.get('from'), w.get('to')) if w.get('from') else ''
    pend = r.get('pending_at_as_of') or []
    if a == 'none_pending':
        return ('%s近六个月%s无已决议待生效的调整(官方实录确认至 %s,其后 %d 天'
                '不在实录——本地未收录不等于未发生)'
                % (lab, win, r.get('confirmed_through'), r.get('unconfirmed_days') or 0))
    if a == 'pending':
        return '%s近六个月%s有 %d 项已决议待生效的调整: %s' % (
            lab, win, len(pend),
            '、'.join('%s决议、%s生效(目标 %s%%)' % (
                md(p.get('decision_date')), md(p.get('effective_on')),
                fnum(p.get('target_value'))) for p in pend))
    if r.get('path') == 'series_convention':
        return '%s待生效面不可核验(序列只能给出已生效变动,无官方决议实录)' % lab
    if r.get('path') == 'official_record':
        return ('%s待生效面不可核验(官方实录确认覆盖止于 %s,距研究截止日 %d 天)'
                % (lab, r.get('confirmed_through'), r.get('unconfirmed_days') or 0))
    return '%s待生效面数据不可得(官方实录与政策序列均缺席)' % lab


def infl_text(r):
    om = r.get('observation_month') or ''
    pub = ('公布 %s' % md(r['publish_date'])) if r.get('publish_date') else '公布日不可得'
    base = r.get('base') or {}
    if r.get('status') == 'ok' and r.get('value') is not None:
        d = r.get('delta_pp') or 0
        dirw = '高' if d > 0 else ('低' if d < 0 else '持平')
        return ('%s %s%%(%s观测,%s)较去年同月 %s%% %s %s 个百分点'
                % (iname(r), fnum(r['value']), ym_cn(om), pub,
                   fnum(base['value']), dirw, fnum(abs(d))))
    if r.get('status') == 'base_missing' and r.get('value') is not None:
        return ('%s %s%%(%s观测,%s)的去年同月基期不在序列,与去年同月的比较不可判'
                % (iname(r), fnum(r['value']), ym_cn(om), pub))
    _nt = str(r.get('note') or '').strip()
    return '%s最新读数数据不可得(%s)' % (
        iname(r), _nt if _nt and _nt != '数据不可得' else '序列无可见读数')


def headline():
    rm_ = qt.get('research_month') or as_of[:7]
    t = '截至 %s(问句研究月 %s' % (as_of, ym_cn(rm_))
    if qt.get('research_month_end') and as_of < qt['research_month_end']:
        t += ';月末未到、数据未覆盖,取快照实际覆盖日): '
    else:
        t += '): '
    parts = [target_text(r) for r in T]
    parts += [pending_text(r) for r in P]
    parts.append('通胀同比最新读数: ' + ';'.join(infl_text(r) for r in Y))
    if n_rec or _est:
        parts.append('公布时间口径: %s' % ';'.join(_pub_parts))
    if any(g.get('code') == 'historical_version_missing' for g in blk['gaps']):
        parts.append('历史版本口径: 研究截止日无当日冻结快照(缺历史版本),事实与'
                     '历史序列取自较晚快照的截止视图——声明修订口径的序列为最新'
                     '修订值,不得表述为当时首发值')
    parts.append('条件式(非预测): 两地通胀同比差与政策水平差若延续,其对汇率与'
                 '利率的含义须待官方决议实录补录与后续读数检验')
    return t + ';'.join(parts) + '。'


def echo():
    return {
        'research_time': {'as_of': as_of, 'research_month': qt.get('research_month')},
        'official_targets': [
            {'region': r['region'], 'status': r['status'], 'target': r['target'],
             'decision_date': r['decision_date'],
             'effective_date': r['effective_date'],
             'first_publish': r['first_publish'],
             'evidence_refs': list(r['evidence_refs']),
             **({'note': '序列+惯例推定(非官方实录);决议日系「%s」惯例自生效日回推'
                         % conv_text(r.get('decision_basis'))}
                if r['status'] == 'series_convention_derived' else {}),
             **({'note': '日历实录(官方公布值)'}
                if r['status'] == 'official_record' else {})}
            for r in T],
        'pending_decisions': [
            {'region': r['region'], 'answer': r['answer'],
             'confirmed_through': r['confirmed_through'],
             'pending': [{'target': p['target_value'],
                          'decision_date': p['decision_date'],
                          'effective_date': p['effective_on']}
                         for p in (r.get('pending_at_as_of') or [])],
             'evidence_refs': list(r['evidence_refs']),
             **({'note': '官方实录确认之后的决议不在本地日历,未收录不等于未发生'}
                if r['answer'] == 'none_pending' else {}),
             **({'note': '无官方决议实录可核,未收录不等于无'}
                if r['answer'] == 'unverifiable' else {})}
            for r in P],
        'inflation_yoy': [
            {'region': r['region'], 'metric_id': r['metric_id'],
             'status': r['status'], 'value': r['value'],
             'observation_month': r['observation_month'],
             'publish_date': r['publish_date'],
             'base_value': (r.get('base') or {}).get('value'),
             'delta_pp': r['delta_pp'],
             'evidence_refs': list(r['evidence_refs']),
             **({'note': '去年同月基期不在序列,比较不可判'}
                if r['status'] == 'base_missing' else {})}
            for r in Y],
        'gaps_echoed': [{'code': g['code'], 'region': g['region'],
                         'metric_id': g['metric_id']} for g in blk['gaps']],
        'comments': [
            '研究年月→研究截止日;回看窗口→政策与待生效面;同比基期→通胀面'
            '(三者分别对账)。',
            '数据不可得的格已明写,缺口逐项回声于 gaps_echoed。']}


# ── L3(中文数字,契约按引擎面数字集合绑定) ─────────────────────────────
def infl_cn(r):
    om = r.get('observation_month') or ''
    b = r.get('base') or {}
    pub = ('公布 %s' % r['publish_date']) if r.get('publish_date') else '公布日不可得'
    if r.get('status') == 'ok' and b.get('value') is not None:
        d = r.get('delta_pp')
        dirw = '抬升' if d > 0 else ('回落' if d < 0 else '持平于')
        return ('%s%s(%s观测,%s,%s),去年同月(%s)为%s,%s%s个百分点'
                % (iname(r), cn_num(r['value']), om + ' ', pub, pub_word(r),
                   b.get('observation_month') or '', cn_num(b['value']), dirw,
                   cn_num(abs(d))))
    if r.get('status') == 'base_missing' and r.get('value') is not None:
        return ('%s%s(%s观测,%s,%s)的去年同月基期观测不在序列,与去年同月的'
                '比较不可判'
                % (iname(r), cn_num(r['value']), om + ' ', pub, pub_word(r)))
    return '%s最新读数不可得' % iname(r)


w = qt.get('lookback_window') or {}
win_txt = '(%s..%s)' % (w.get('from'), w.get('to')) if w.get('from') else ''
contras = []
c1_refs, c1_txt = [], []
t_jp, t_ea = trow('JP'), trow('EA')
for t in T:
    lab = t.get('label') or t['region']
    pr = prow(t['region']) or {}
    pend = pr.get('pending_at_as_of') or []
    if t.get('status') == 'official_record' and t.get('target') is not None:
        c1_refs += list(t['evidence_refs'])
        s = ('%s: 发布日历实录载 %s 决议、%s 生效,官方政策目标利率%s'
             % (lab, t['decision_date'], t['effective_date'], cn_pct(t['target'])))
        if t.get('last_maintenance'):
            s += '(%s 确认维持)' % t['last_maintenance']
        s += ';窗内%s该决议已生效' % win_txt
        if pr.get('answer') == 'none_pending':
            s += (';截至研究截止日无已决议未生效条目(实录确认覆盖至 %s,其后'
                  '%s天内的后续决议不在实录,本地未收录不等于未发生)'
                  % (pr.get('confirmed_through'), cn_num(pr.get('unconfirmed_days') or 0)))
        elif pend:
            s += (';截至研究截止日有%s项已决议未生效条目: %s'
                  % (cn_num(len(pend)),
                     '、'.join('%s 决议、%s 生效(目标%s)' % (
                         p.get('decision_date'), p.get('effective_on'),
                         cn_pct(p.get('target_value'))) for p in pend)))
        c1_txt.append(s)
    elif t.get('status') == 'series_convention_derived':
        c1_refs += list(t['evidence_refs'])
        sers = [x for x in (t.get('series_rows') or []) if x.get('value') is not None]
        chg = [c for c in (pr.get('in_window_changes') or [])
               if c.get('metric_id') == t.get('official_metric_id')]
        chg_txt = '、'.join('%s 生效(%s→%s)' % (c['date'], cn_num(c['from']), cn_num(c['to']))
                           for c in chg)
        c1_txt.append(
            '%s: 冻结日历无该央行决议实录,目标水平由政策序列变更日加惯例推定'
            '【推断】——%s,%s 生效,决议日 %s 系按「%s」惯例自变更日回推;窗内已生效'
            '变动: %s;已决议待生效的决定无官方记录可核【尚未验证】,不得以序列'
            '无变动推断无待生效决议'
            % (lab, '、'.join('%s%s' % (x['display_name'], cn_pct(x['value']))
                             for x in sers[:2]),
               t['effective_date'], t['decision_date'], conv_text(t.get('decision_basis')),
               chg_txt or '无'))
    else:
        c1_txt.append('%s: 官方政策目标水平数据不可得(%s)'
                      % (lab, t.get('basis_text') or '无证据'))
if c1_txt:
    contras.append({
        'id': 'C1-POLICY-LEVELS-PENDING',
        'statement': '两地官方政策目标水平与待生效面的证据口径不对称。' + ';'.join(c1_txt) + '。',
        'evidence_refs': list(dict.fromkeys(c1_refs)),
        'competing_explanations': [
            '【假设】若目标水平只能由官方实录核验的一端(本问为序列+惯例推定的'
            '经济体)在最后一次已生效变动之后另有已决议而未生效的调整,序列在'
            '生效前不会变化——本地面无法区分「无决议」与「有决议未生效」,'
            '待生效面只能答不可核验。',
            '【假设】若该经济体在最后一次已生效变动之后按兵不动,则序列现值即'
            '现行目标且待生效为空——此情形须待官方决议实录补录后方可核验,'
            '本档不采信任一情形。']})

ok_rows = [r for r in Y if r.get('status') == 'ok' and r.get('delta_pp') is not None]
bm_rows = [r for r in Y if r.get('status') == 'base_missing']
ms_rows = [r for r in Y if r.get('status') == 'missing']
infl_all = ok_rows + bm_rows + ms_rows
if infl_all:
    dirs = {('higher' if r['delta_pp'] > 0 else 'lower' if r['delta_pp'] < 0 else 'flat')
            for r in ok_rows}
    lead = (('两地通胀同比最新读数相比去年同月方向%s。'
             % ('相反' if len(dirs) > 1 else '相同')) if len(ok_rows) >= 2
            else '通胀同比最新读数: ')
    # 版本口径与公布日口径随引擎行取值(同口径的读数合并点名)
    _vg = {}
    for r in infl_all:
        _vg.setdefault(row_vint(r) if r.get('value') is not None else '无读数', []).append(iname(r))
    _pg = {}
    for r in infl_all:
        if r.get('value') is not None:
            _pg.setdefault(pub_word(r), []).append(iname(r))
    _vt = ';'.join('%s=%s' % ('、'.join(v), k) for k, v in _vg.items())
    _pt = ';'.join('%s的公布日为%s' % ('、'.join(v), k) for k, v in _pg.items())
    contras.append({
        'id': 'C2-INFL-YOY-BASE',
        'statement': (lead + ';'.join(infl_cn(r) for r in infl_all)
                      + '。差值=同比读数之差(百分点),非通胀率本身的变化;版本口径: '
                      + _vt + ';公布日口径: ' + _pt + '。'),
        'evidence_refs': list(dict.fromkeys(
            x for r in infl_all for x in r['evidence_refs'])),
        'competing_explanations': [
            '【假设】若抬升一端主要源于能源与进口价格的持续传导、回落一端主要'
            '反映上年同期高基数消退,则两地同比差应在后续数月收敛——引擎无分项'
            '构成与基数贡献序列,此归因不可在引擎面验证。',
            '【假设】若两地差异主要由内需与政策组合驱动,则后续核心口径与读数'
            '路径应持续分化——同样缺分项与需求面证据,两种解释不可区分,如实'
            '并列。']})

chain_links = []
if infl_all:
    l1_refs = list(dict.fromkeys(
        [x for t in T for x in (t.get('evidence_refs') or [])]
        + [x for r in infl_all for x in (r.get('evidence_refs') or [])][:6]))
    pol_txt = []
    for t in T:
        lab = t.get('label') or t['region']
        if t.get('status') == 'official_record' and t.get('target') is not None:
            pol_txt.append('%s官方目标%s(%s 生效)' % (
                lab, cn_pct(t['target']), t['effective_date']))
        elif t.get('status') == 'series_convention_derived':
            pol_txt.append('%s政策水平%s(%s 生效,序列+惯例推定)' % (
                lab, cn_pct(t['target']), t['effective_date']))
    obs_txt = '、'.join('%s%s' % (iname(r), cn_num(r['value'])) for r in infl_all
                        if r.get('value') is not None)
    dir_txt = ('方向相反' if len(dirs) > 1 else
               ('方向相同' if dirs else '仅一地可判'))
    chain_links.append({
        'step': 1, 'evidence_level': 'E1',
        'text': ('观察: 最新观测月两地通胀同比读数较去年同月的%s(%s);政策目标'
                 '水平: %s。' % (dir_txt, obs_txt, ';'.join(pol_txt) or '数据不可得')),
        'evidence_refs': l1_refs})
    chain_links.append({
        'step': 2, 'evidence_level': 'E2',
        'text': ('传导【假设】: 若两地政策利率水平差经利差渠道主导汇率与资本'
                 '流动,则通胀差与政策差延续会对两地汇率与利率敏感估值形成'
                 '方向性压力——但汇率、利率预期与资本流动序列不在本问证据面,'
                 '该环为假设,不可在引擎面验证;本档不据此裁方向。'),
        'missing_link_note': ('利率差→汇率/资本流动通道无引擎证据(本问证据面不含'
                              '汇率与利率预期序列),该环为【假设】;区分指标='
                              'EURUSD/USDJPY,方向留白不裁。'),
        'evidence_refs': []})
    fm = ok_rows[0]['metric_id'] if ok_rows else None
    if fm:
        f_ids = ' 与 '.join(r['metric_id'] for r in ok_rows[:2])
        chain_links.append({
            'step': 3, 'evidence_level': 'E3',
            'text': ('证伪环: 以 %s 为可观测证伪指标——判据即 L4 两情景的证伪'
                     '阈值(席位自设,见 L4);若后续观测月通胀同比相对去年的差'
                     '未达延续前提,则「差延续」的推断被证伪(方向留白,不设幅度'
                     '预测)。' % f_ids),
            'falsification_metric': fm,
            'evidence_refs': list(ok_rows[0]['evidence_refs'])})


# ── L4(席位自设阈值,阿拉伯数字) ────────────────────────────────────
def pol_clause():
    parts = []
    for t in T:
        lab = t.get('label') or t['region']
        pr = prow(t['region']) or {}
        pend = pr.get('pending_at_as_of') or []
        if t.get('status') == 'official_record' and t.get('target') is not None:
            if pend:
                parts.append('%s已决议待生效的调整(目标 %s%%,%s 生效)如期生效,'
                             '其后至观测月不再有新决议'
                             % (lab, fnum(pend[0].get('target_value')),
                                pend[0].get('effective_on')))
            else:
                parts.append('%s维持官方目标 %s%% 至观测月' % (lab, fnum(t['target'])))
        elif t.get('status') == 'series_convention_derived' and t.get('target') is not None:
            parts.append('%s政策水平维持 %s%%(序列口径,待官方实录核验)'
                         % (lab, fnum(t['target'])))
    return ';'.join(parts)


def levels(r):
    """席位自设水平(观测月读数相对去年同月的差,百分点): p=延续水平(当前差的
    一半),c=收敛水平(当前差的四分之一);一位小数、幅度下限 0.1(保留符号)。"""
    d = r['delta_pp']

    def _lv(x):
        v = half_up(x)
        if abs(v) < 0.1:
            v = 0.1 if d >= 0 else -0.1
        return v
    return _lv(d / 2), _lv(d / 4)


def prem_phrase(r, mode):
    """情景前提(观测月读数相对去年同月的差): keep=延续/conv=收敛。"""
    d = r['delta_pp']
    p, c = levels(r)
    if d > 0:
        return ('较去年同月高出不少于 %s 个百分点' % fthr(p) if mode == 'keep'
                else '较去年同月的差收窄至不超过 %s 个百分点' % fthr(c))
    if d < 0:
        return ('较去年同月低不少于 %s 个百分点' % fabs1(p) if mode == 'keep'
                else '较去年同月的差收窄至不低于 %s 个百分点' % fthr(c))
    return '较去年同月持平(差不超过 ±%s 个百分点)' % fabs1(p)


def fail_phrase(r, mode):
    """前提的严格反面(与前提同水平;不留不触发亦不证伪的区间)。"""
    d = r['delta_pp']
    p, c = levels(r)
    if d > 0:
        return ('较去年同月高出不足 %s 个百分点' % fthr(p) if mode == 'keep'
                else '较去年同月高出超过 %s 个百分点' % fthr(c))
    if d < 0:
        return ('较去年同月低不到 %s 个百分点' % fabs1(p) if mode == 'keep'
                else '较去年同月低超过 %s 个百分点(回落扩大)' % fabs1(c))
    return '与去年同月的差超过 ±%s 个百分点' % fabs1(p)


scen = []
if ok_rows:
    two = len(ok_rows) >= 2
    obs_latest = max(r['observation_month'] for r in ok_rows)
    obs_m = shift_ym(obs_latest, 2)
    entry_m = shift_ym(obs_m, 1)
    deadline = month_end(shift_ym(entry_m, 1))
    pc = pol_clause()
    pc_s = (';政策端%s' % pc) if pc else ''
    scope = '两地通胀同比差' if two else '通胀同比相对去年的差'
    dir_word = ''
    if two and (ok_rows[0]['delta_pp'] > 0) != (ok_rows[1]['delta_pp'] > 0):
        dir_word = '延续'
    elif two:
        dir_word = '同向'

    def build_scen(sid, role, mode):
        """条件情景(假设·非预测): 前提=观测月各读数相对去年同月的差延续/
        收敛+政策分量;证伪=前提的严格反面(与前提同水平)。"""
        keep = mode == 'keep'
        head = ((scope + dir_word) if keep else (scope + '收敛'))
        prem = ','.join('%s%s' % (iname(r), prem_phrase(r, mode))
                        for r in ok_rows)
        cond = ',且同观测月 '.join('%s %s' % (r['metric_id'], prem_phrase(r, mode))
                                  for r in ok_rows)
        fail = ',或同观测月 '.join('%s %s' % (r['metric_id'], fail_phrase(r, mode))
                                   for r in ok_rows)
        if keep:
            direction = ('在此假设下,两地通胀差与政策水平差延续,利率与汇率的'
                         '相对压力延续' if two else
                         '在此假设下,该读数相对去年的差延续')
        else:
            direction = ('在此假设下,两地通胀差收敛,利率与汇率的相对压力缓解'
                         if two else '在此假设下,该读数相对去年的差收敛')
        fals = {'metric_id': ok_rows[0]['metric_id'],
                'threshold': ('若观测月 %s %s,则「%s」的前提被证伪'
                              % (obs_m, fail, head))}
        if two:
            fals['secondary_metric_ids'] = [ok_rows[1]['metric_id']]
        return {'id': sid, 'role': role,
                'rows': {
                    'scenario': ('【假设·非预测】%s: 至观测月 %s(读数按引擎发布'
                                 '规则于 %s 入档),%s%s。'
                                 % (head, obs_m, entry_m, prem, pc_s)),
                    'asset_direction': {
                        'direction': (direction + '——方向性推演,非幅度预测;本问'
                                      '证据面不含资产序列,不引用资产证据(纯逻辑'
                                      '推理档)'),
                        'confidence_tier': '纯逻辑推理', 'evidence_refs': []},
                    'sensitive_variables': [r['metric_id'] for r in ok_rows],
                    'falsification': fals,
                    'trigger': {
                        'condition': ('观测月 %s 的 %s(以引擎发布规则入档的读数'
                                      '为准)' % (obs_m, cond)),
                        'deadline': deadline}}}
    scen = [build_scen('S1-GAP-PERSISTS', '条件情景·通胀差延续', 'keep'),
            build_scen('S2-GAP-CONVERGES', '条件情景·通胀差收敛', 'conv')]

n_ref = sum(len(c['evidence_refs']) for c in contras) + sum(
    len(x.get('evidence_refs') or []) for x in chain_links)
now = datetime.datetime.now().astimezone()
judgment = {
    'schema_version': '1.1',
    'agent_declaration': {
        'attribution': 'ai_inferred',
        'agent': 'Agent 研究席(操作者会话经正式入口 ia_cli research-one 代持席位)',
        'produced_by': ('Agent 研究席(操作者会话经正式入口 ia_cli research-one '
                        '代持席位, %s, %s)' % (run.get('ts_utc') or '', as_of)),
        'written_at': now.isoformat(timespec='seconds'),
        'note': ('判断内容 100% Agent 产;证据引用取自本报告证据索引原值;结构化'
                 '回声逐字取自引擎分面块,叙述数值与引擎面逐位对账;校验是纪律'
                 '地板,判断质量归 Agent 与独立审计。'),
        'tooling': ('席位侧装配脚本 scripts/seat_tools/'
                    'make_family_judgment.py: 确定性装配——措辞、阈值与证伪判据'
                    '为席位撰写并固化于脚本,数值与日期全部取自引擎分面块(零'
                    '手敲),零网络调用;席位经正式入口提交,契约与文本一致性'
                    '校验照常执行,判断质量归席位与独立审计'),
        'basis': ('读本轮 AGENT_SEAT_ENVELOPE 工单、证据索引(%d 行)、原问直答'
                  '分面块(政策目标/已决议待生效/通胀同比三面+缺口点名)、工单'
                  '冻结输入(发布日历/注册表/快照)后独立研判;研究年月、回看窗口、'
                  '同比基期分别对账;引擎只供确定性证据,判断内容 100%% 归 Agent。'
                  % len(rep.get('evidence_index') or []))},
    'l3': {'contradictions': contras,
           'mechanism_chains': [{'id': 'M1-POLICY-INFL-GAP', 'links': chain_links}]},
    'l4': {'scenarios': scen},
    'quality_gate_notes': [
        '证据绑定: %d 条矛盾陈述+机制链 %d 环共 %d 条引用,全部解析到本报告证据'
        '索引(含日历实录行与计划序列点行);零悬空引用。'
        % (len(contras), len(chain_links), n_ref),
        '竞争性解释: 每条矛盾陈述并列 2 条(均标【假设】),如实并列、不裁胜负。',
        '四层标注: 引擎字段原值=【事实】;序列+惯例推定的决议日=【推断】;传导环='
        '【假设】(E2 明写缺环);序列口径经济体的待生效面、日历实录确认之后的'
        '决议面=【尚未验证】。',
        '证伪面: 两情景五行齐备,证伪指标(%s)在册可观测;证伪阈值=前提的严格'
        '反面(与前提同水平,不留不触发亦不证伪的区间);触发条件绑定观测月与'
        '入档规则,带时限;政策分量(维持/如期生效)不设数值触发,以决议实录'
        '核验。' % ('/'.join(dict.fromkeys(
            m for s in scen for m in s['rows']['sensitive_variables'])) or '—'),
        '口径披露: %s;官方记录优先: 日历实录 %d 项、序列+惯例推定 %d 项(非官方'
        '公布值,如实标注);公布时间: %s;同比差=同比读数之差(百分点)。'
        % (scope_txt, n_rec, n_conv, ';'.join(_pub_parts)),
        vnote,
        '引擎缺口披露(数据面缺口 %d 项,非本档判断问题;逐项见 gaps_echoed): %s。'
        % (len(_gaps), ';'.join(_gap_parts) or '无')],
    'reader_map': {
        'headline_conclusion': headline(),
        'policy_question': echo(),
    },
}

import re                                                      # noqa: E402
_txt = json.dumps(judgment, ensure_ascii=False)
assert not re.search(r'[A-Z0-9_][较公为系][去年厘官]', _txt), '标识符与中文之间缺空格'
assert '  ' not in _txt, '连续空格'

# ── 自检(不绿不写) ────────────────────────────────────────────────────
import agent_judgment as aj                                       # noqa: E402
from research_contract import judgment_contract as jc              # noqa: E402

cal = os.path.join(tree, 'config', 'release_calendar.json')
mids = aj._registry_metric_ids(tree)
res = aj.validate_judgment(judgment, {e.get('ref') for e in rep['evidence_index']},
                           mids, policy_events=aj.collect_policy_events(cal),
                           as_of=(run.get('evidence_asof') or as_of))
con = jc.verify_judgment(judgment, rep)
print('discipline passed', res['passed'], json.dumps(res['violations'], ensure_ascii=False)[:1500])
print('contract', con['verdict'], json.dumps(con['stats'], ensure_ascii=False),
      'family_checks', len(con['map_checks']))
for c in con['map_checks']:
    if c['status'] != 'VERIFIED':
        print('   FAMILY', c)
for u in con['unresolved_unbound'][:10]:
    print('   UNB', u)
for c in con['verdicts']:
    if c['status'] != 'VERIFIED':
        print('   VERD', {k: c.get(k) for k in ('item', 'token', 'metric', 'value', 'expected', 'status', 'note')})
for c in con['six_checks']:
    if c['status'] != 'VERIFIED':
        print('   SIX', c)
if not (res['passed'] and con['verdict'] == 'VERIFIED' and len(con['map_checks']) >= 30):
    print('NOT WRITTEN')
    sys.exit(3)
json.dump(judgment, open(jp_out, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('written', jp_out, os.path.getsize(jp_out))
print('HEADLINE', judgment['reader_map']['headline_conclusion'])
