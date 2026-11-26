# -*- coding: utf-8 -*-
"""Audit-R33 任务3: 原问直答型问句——研究年月/回看窗口/同比基期分记+确定性事实面。

基线正式 CLI 复现(审计基线 f053afe;原问=R31 session_T3_first_empty
逐字件经 --question-file):
  「2026年11月，日本和欧元区的央行当前官方政策目标利率各处于什么水平？
  最近六个月有无已决议但尚未生效的调整？两地通胀同比最新读数相比去年
  同月如何？请给出具体数据和各数据的公布时间。」
- 未入研究计划(指标空/L1 零行/无计划),plan 回执仍 ok=true 并指示席位
  「去产 L3/L4」——答非所问面被当正例放行(零事实/缺计划不报缺口);
- 「两地通胀…」句段只有指代词无地区名→通胀维度整段丢失;
- 研究截止日=快照覆盖日(换 12 月快照重跑,研究时点跟着漂到 12 月);
- 「去年同月」未解析、「最近六个月」只成点锚→数据需求按单一窗判,
  计划指标被误判覆盖不足;
- 欧元区待生效决定无官方日历实录→不可核验而未披露;
- 日/欧通胀公布日仅规则推定而未标注。

本模块(零模型,确定性;问什么答什么,逐行可复算):
  question_kind        'map'(形状判据成立=五面契约不变)|'policy_question'
                       (族判据成立而形状不成立=分面契约)|None;
  parse_question_time  研究年月/回看窗口/同比基期 三分量分记;
  build_faces          政策目标/已决议待生效/通胀同比 三面+缺口点名+版本绑定;
  blocked_class        面缺口分级(判定与渲染共源: 被问及的面无证据=草稿);
  evidence_rows        政策实录行+计划序列点行入证据索引(席位可引用);
  render_policy_question_report  读者报告。
"""
import calendar
import datetime
import os
import re

SCHEMA = 'r33-policy-question'
REPORT_TITLE = '# 原问直答研究(读者报告)'

POLICY_ASK_WORDS = ('政策目标', '目标利率', '利率目标', '官方政策')
PENDING_WORDS = ('尚未生效', '待生效', '已决议', '已决定但未', '已宣布待')
YOY_BASE_WORDS = ('去年同月', '去年同期', '上年同月', '上年同期', '去年同一时期')
INFLATION_WORDS = ('通胀', 'CPI', 'HICP', '物价')
# 指示词句段绑定(「两地通胀…」回指问句点名的经济体)
DEICTIC_WORDS = ('两地', '两国', '两家', '三地', '四地', '各自', '各处于',
                 '各为', '各经济体', '二者', '两者', '各方', '各地')
# 独立时间状语「YYYY年M月」(非「M月D日」日期形,非「以来/前/后/起」端点)
_YM_RE = re.compile(
    r'(?<![\d年月日])(?P<y>[0-9]{4})\s*年\s*(?P<m>[0-9]{1,2})\s*月'
    r'(?!\s*[0-9]{1,2}\s*[日号])(?!\s*(?:以来|前|后|起|份))')
_CUR_ANCHOR = '最新一期'

FACES = (('policy_targets', 'policy_target_ask', '政策目标'),
         ('pending_decisions', 'pending_ask', '已决议待生效'),
         ('inflation_yoy', 'inflation_yoy_ask', '通胀同比'))


def _rmp():
    import research_map_planner as rmp
    return rmp


def _fp():
    import freshness_policy as fp
    return fp


def _days(from_iso, to_iso):
    """to−from 的天数(任一缺席/非法=None)。"""
    try:
        a = datetime.date.fromisoformat(str(from_iso)[:10])
        b = datetime.date.fromisoformat(str(to_iso)[:10])
    except (TypeError, ValueError):
        return None
    return (b - a).days


def research_month(question):
    """问句研究年月 (y, m) | None(未声明独立年月)。"""
    m = _YM_RE.search(_rmp()._norm_q(question or ''))
    if not m:
        return None
    y, mo = int(m.group('y')), int(m.group('m'))
    return (y, mo) if 1 <= mo <= 12 else None


def research_month_end(question):
    """研究年月的月末(ISO 日);未声明=None。"""
    ym = research_month(question)
    if not ym:
        return None
    return '%04d-%02d-%02d' % (ym[0], ym[1], calendar.monthrange(*ym)[1])


def asked_components(question):
    """问句三分量是否被问及(确定性词形)。"""
    rmp = _rmp()
    q = rmp._norm_q(question or '')
    return {
        'policy_targets': (
            any(w in q for w in POLICY_ASK_WORDS)
            or any(w in q for w in rmp._POLICY_DIM_EXTRA)),
        'pending_decisions': any(w in q for w in PENDING_WORDS),
        'inflation_yoy': (
            any(w in q for w in INFLATION_WORDS)
            and ('同比' in q
                 or any(w in q for w in YOY_BASE_WORDS))),
    }


def detect_policy_question(question, ent):
    """原问直答型族判据: ≥2 个在册经济体 + 无地图形状词 + 任一分量被问及。

    与 detect_map_question 互斥优先级见 question_kind: 形状判据成立=
    地图问句(五面契约不变,本族判据不介入)。"""
    rmp = _rmp()
    q = question or ''
    ecos = [e for e in (ent.get('economies') or [])
            if e in rmp.REGION_DIMENSION_METRICS]
    if len(ecos) < 2 or any(w in q for w in rmp.MAP_SHAPE_WORDS):
        return False
    return any(asked_components(q).values())


def parse_question_time(question, as_of_iso):
    """问句时间分量分记: 研究年月(→研究截止日)/回看窗口/同比基期。"""
    rmp = _rmp()
    q = question or ''
    comp = asked_components(q)
    wins = sorted(rmp.parse_question_windows(q, as_of_iso or '') or [],
                  key=lambda w: (w.get('months') or 0))
    ym = research_month(q)
    qn = rmp._norm_q(q)
    base_src = next((w for w in YOY_BASE_WORDS if w in qn), None)
    yoy = None
    if comp['inflation_yoy']:
        yoy = {'kind': ('same_month_last_year' if base_src
                        else 'yoy_reading'),
               'source': base_src or '同比'}
    return {
        'schema': SCHEMA,
        'research_month': ('%04d-%02d' % ym if ym else None),
        'research_month_end': research_month_end(q),
        'lookback_windows': wins,
        'lookback_window': wins[0] if wins else None,
        'yoy_base': yoy,
        'policy_target_ask': comp['policy_targets'],
        'pending_ask': comp['pending_decisions'],
        'inflation_yoy_ask': comp['inflation_yoy'],
        'applies_to': {
            'research_month': ['evidence_as_of'],
            'lookback_window': ['policy_targets', 'pending_decisions'],
            'yoy_base': ['inflation_yoy']},
        'as_of': as_of_iso,
    }


# ── 事实面 ────────────────────────────────────────────────────────────

def _plan_cells(plan, dimension):
    """计划维度成员的点值格 → [(地区, 格)]。

    计划格(regions…dimensions)只带元数据;锚/政策窗路径在点值面
    (point_values.cells)——两处按 metric_id 合并(元数据补点值格缺的
    频率/修订口径键),成员资格以计划格为准(点值缺席=成员仍出面)。"""
    pv_cells = ((plan.get('point_values') or {}).get('cells') or [])
    out = []
    for eco, rf in (plan.get('regions') or {}).items():
        for meta in ((rf.get('dimensions') or {}).get(dimension) or []):
            pv = next((x for x in pv_cells
                       if x.get('metric_id') == meta.get('metric_id')), None)
            if pv is None:
                out.append((eco, dict(meta, anchors={})))
                continue
            merged = dict(meta)
            for k, v in pv.items():
                if k not in merged or merged.get(k) is None:
                    merged[k] = v
            out.append((eco, merged))
    return out


def _latest_anchor(cell):
    anchors = cell.get('anchors') or {}
    la = anchors.get(_CUR_ANCHOR)
    if not isinstance(la, dict):
        la = max((a for a in anchors.values() if isinstance(a, dict)),
                 key=lambda a: str(a.get('as_of') or ''), default={})
    return la if isinstance(la, dict) else {}


def _pub_kind(basis_text):
    return ('calendar_record'
            if str(basis_text or '').startswith('calendar:')
            else 'rule_estimated')


def _series_row(cell, as_of):
    """政策维序列格→现值行(观测日/公布日/决议日/生效日分列)。"""
    la = _latest_anchor(cell)
    mid = cell.get('metric_id')
    row = {'metric_id': mid, 'display_name': cell.get('display_name'),
           'face': cell.get('face_note'), 'unit': cell.get('unit'),
           'status': la.get('status') or 'missing', 'value': None,
           'observation_date': None, 'publish_date': None,
           'publish_basis': None, 'publish_basis_text': None,
           'decision_date': None, 'effective_date': None,
           'decision_basis': None, 'freshness': None, 'evidence_ref': None}
    if la.get('status') == 'ok' and la.get('value') is not None:
        pdt = la.get('policy_dates') or {}
        kind = (cell.get('policy_face') or {}).get('decision_kind')
        if pdt.get('official_basis'):
            dec_basis = 'calendar_record'
        elif pdt.get('decision') and pdt.get('effective'):
            dec_basis = 'convention:%s' % (kind or 'engine')
        else:
            dec_basis = None
        fresh = None
        try:
            fresh = _fp().assess_observation_freshness(
                mid, la.get('observation_date'), as_of).get('status')
        except (TypeError, ValueError, KeyError):
            fresh = None
        row.update(
            value=la.get('value'),
            observation_date=la.get('observation_date'),
            publish_date=la.get('publication_date'),
            publish_basis=_pub_kind(la.get('publication_basis')),
            publish_basis_text=la.get('publication_basis'),
            decision_date=pdt.get('decision'), effective_date=pdt.get('effective'),
            decision_basis=dec_basis, freshness=fresh,
            policy_confirm_date=la.get('policy_confirm_date'),
            evidence_ref='%s@%s' % (mid, la.get('observation_date')))
    return row


def _policy_states(plan, as_of, cal):
    """各地区官方目标指标的政策实录状态(日历可见面;逐地区一次)。"""
    rmp = _rmp()
    out = {}
    for eco in (plan.get('regions') or {}):
        mid = rmp._OFFICIAL_TARGET_METRICS.get(eco)
        if not mid:
            continue
        try:
            out[eco] = _fp().policy_decision_state(
                mid, as_of, calendar_path=cal)
        except (OSError, ValueError, KeyError) as e:
            out[eco] = {'present': False, 'error': '%s: %s'
                        % (type(e).__name__, e)}
    return out


def _rec(r):
    return {k: r.get(k) for k in (
        'entry_id', 'kind', 'basis', 'first_publish', 'decision_date',
        'effective_on', 'target_value', 'note')}


def _gap(gaps, code, region, metric_id, note):
    gaps.append({'code': code, 'region': region, 'metric_id': metric_id,
                 'severity': 'disclosed', 'note': note})


def _policy_targets_face(plan, states, as_of, gaps):
    """政策目标面: 官方日历实录 > 序列+惯例推定(标非官方) > 缺证。"""
    rmp = _rmp()
    rows = []
    for eco, rf in (plan.get('regions') or {}).items():
        members = ((rf.get('dimensions') or {}).get('policy') or [])
        if not members:
            continue
        cells = [c for e, c in _plan_cells(plan, 'policy') if e == eco]
        label = rmp._REGION_LABEL.get(eco, eco)
        mid = rmp._OFFICIAL_TARGET_METRICS.get(eco)
        st = states.get(eco) or {'present': False}
        recs = [_rec(r) for r in (st.get('records') or [])]
        series_rows = [_series_row(c, as_of) for c in cells]
        row = {'region': eco, 'label': label, 'official_metric_id': mid,
               'unit': 'percent', 'status': 'missing', 'target': None,
               'decision_date': None, 'effective_date': None,
               'first_publish': None, 'last_maintenance': None,
               'confirmed_through': None, 'days_since_effective': None,
               'days_since_decision': None, 'days_since_maintenance': None,
               'decision_basis': None, 'official_entry_id': None,
               'basis_text': None, 'records': recs, 'series_rows': series_rows,
               'evidence_refs': []}
        refs = ['POLICY:%s@%s' % (r['entry_id'], r['first_publish'])
                for r in recs if r.get('entry_id')]
        if st.get('present') and st.get('official_target') is not None:
            dec = next((r for r in recs if r.get('kind') == 'policy_decision'
                        and r.get('decision_date') == st.get('last_decision')),
                       None)
            tgt = st.get('official_target')
            row.update(
                status='official_record', target=tgt,
                decision_date=st.get('last_decision'),
                effective_date=st.get('last_effective'),
                first_publish=st.get('last_decision_publish'),
                last_maintenance=st.get('last_maintenance'),
                confirmed_through=st.get('last_confirmed_on'),
                days_since_effective=st.get('days_since_adjustment'),
                days_since_decision=st.get('days_since_decision'),
                days_since_maintenance=st.get('days_since_maintenance'),
                decision_basis='calendar_record',
                official_entry_id=(dec or {}).get('entry_id'),
                basis_text=(
                    '官方记录: 日历实录 %s(决议 %s 公布,%s 生效,目标水平 '
                    '%s%%)%s'
                    % ((dec or {}).get('entry_id'), st.get('last_decision'),
                       st.get('last_effective'), tgt,
                       (';最近确认维持 %s' % st.get('last_maintenance')
                        if st.get('last_maintenance') else ''))),
                evidence_refs=refs)
        elif st.get('present'):
            row.update(status='current_target_missing_evidence',
                       evidence_refs=refs,
                       basis_text='日历有政策实录但截至研究时点无已生效的'
                                  '官方目标值(仅待生效公告)——现值缺证,不以'
                                  '序列值冒充')
            _gap(gaps, 'current_target_missing_evidence', eco, mid,
                 '官方目标现值缺证(日历实录只有待生效公告)')
        else:
            cand = (next((s for s in series_rows
                          if s['metric_id'] == mid and s.get('value') is not None
                          and s.get('effective_date')), None)
                    or next((s for s in series_rows
                             if s.get('value') is not None
                             and s.get('effective_date')), None))
            if cand:
                row.update(
                    status='series_convention_derived', target=cand['value'],
                    decision_date=cand['decision_date'],
                    effective_date=cand['effective_date'],
                    first_publish=(cand['decision_date'] or cand['publish_date']),
                    days_since_effective=_days(cand['effective_date'], as_of),
                    days_since_decision=_days(cand['decision_date'], as_of),
                    decision_basis=cand['decision_basis'] or 'series_observation',
                    basis_text=(
                        '序列+惯例推定(非官方日历实录): %s 观测值 %s%%'
                        '(观测日 %s=生效日;决议日 %s 按 %s 惯例推定;官方'
                        '公布日无日历实录)'
                        % (cand['metric_id'], cand['value'],
                           cand['effective_date'], cand['decision_date'],
                           cand['decision_basis'] or '序列')),
                    evidence_refs=[s['evidence_ref'] for s in series_rows
                                   if s.get('evidence_ref')])
                _gap(gaps, 'official_record_missing', eco, mid,
                     '官方政策决议日历实录缺席——目标水平由序列观测值+决议'
                     '惯例推定,非官方公布值')
            else:
                row.update(
                    status='missing',
                    basis_text='既无官方日历实录、也无带决议/生效日的政策序列'
                               '现值——政策目标水平不可答')
                _gap(gaps, 'policy_target_missing', eco, mid,
                     '政策目标水平无证据(官方实录与政策序列均缺席)')
        rows.append(row)
    return rows


def _pending_face(plan, qt, states, t_rows, as_of, gaps):
    """已决议待生效面: 官方实录路径(逐条可核) | 序列路径(不可核验,点名)。"""
    win = qt.get('lookback_window')
    w_from = win.get('from') if win else None
    bound = getattr(_fp(), '_DEFAULT_MAX_UNCONFIRMED_DAYS', 90)
    rows = []
    for t in t_rows:
        eco, mid = t['region'], t['official_metric_id']
        row = {'region': eco, 'label': t['label'], 'metric_id': mid,
               'window': (dict(win) if win else None), 'path': None,
               'status': None, 'pending_at_as_of': None, 'answer': None,
               'in_window_decisions': [], 'in_window_maintenance': [],
               'in_window_changes': [], 'confirmed_through': None,
               'unconfirmed_days': None, 'basis_text': None,
               'evidence_refs': list(t.get('evidence_refs') or [])}
        for eco2, c in _plan_cells(plan, 'policy'):
            if eco2 != eco:
                continue
            face = (c.get('policy_face') or {}).get('face') or ''
            if not face.startswith('政策目标'):
                # 市场均值月度观测变动(如隔夜拆借月均)不是政策决定——
                # 不入「已决议/已生效」面(该序列现值仍在政策目标面的
                # series_rows,注记月均≠宣布值)
                continue
            for ev in ((c.get('policy_window_path') or {}).get('events')
                       or []):
                if w_from and str(ev.get('date') or '') < w_from:
                    continue
                row['in_window_changes'].append(
                    {'metric_id': c.get('metric_id'),
                     'display_name': c.get('display_name'),
                     'date': ev.get('date'),
                     'date_kind': ('effective' if face.startswith('政策目标')
                                   else 'observation'),
                     'from': ev.get('from'), 'to': ev.get('to'),
                     'delta_bp': ev.get('delta_bp'),
                     'decision_date': ev.get('decision_date'),
                     'basis': ('series+convention'
                               if ev.get('decision_date')
                               else 'series_observation')})
        st = states.get(eco) or {}
        if t['status'] == 'official_record':
            recs = st.get('records') or []
            decs = sorted([r for r in recs if r.get('kind') == 'policy_decision'],
                          key=lambda r: str(r.get('effective_on') or ''))
            for i, r in enumerate(decs):
                dd = r.get('decision_date')
                if w_from and not (dd and dd >= w_from):
                    continue
                if str(r.get('effective_on') or '') > str(as_of):
                    # 已决议、截至研究时点尚未生效——只在 pending_at_as_of,
                    # 不入「窗内已生效决议」(12 月快照重跑 11 月原问时,
                    # 12 月才生效的决议不得列为已生效)
                    continue
                prev = decs[i - 1].get('target_value') if i else None
                tv = r.get('target_value')
                row['in_window_decisions'].append(
                    {'entry_id': r.get('entry_id'), 'decision_date': dd,
                     'first_publish': r.get('first_publish'),
                     'effective_on': r.get('effective_on'), 'target_value': tv,
                     'previous_target': prev,
                     'delta_bp': (round((tv - prev) * 100)
                                  if (tv is not None and prev is not None)
                                  else None),
                     'note': (None if prev is not None else
                              '调整前目标水平不在日历实录——变动幅度不可由'
                              '官方记录给出')})
            for r in recs:
                if (r.get('kind') == 'policy_maintenance'
                        and (not w_from
                             or str(r.get('decision_date') or '') >= w_from)):
                    row['in_window_maintenance'].append(
                        {'entry_id': r.get('entry_id'),
                         'decision_date': r.get('decision_date'),
                         'first_publish': r.get('first_publish'),
                         'target_value': r.get('target_value')})
            pend = st.get('pending_adjustments') or []
            row.update(path='official_record', status='official_record',
                       pending_at_as_of=[_rec(r) for r in pend],
                       confirmed_through=st.get('last_confirmed_on'))
            if pend:
                row['answer'] = 'pending'
                row['basis_text'] = (
                    '官方日历实录: 截至 %s 已公布待生效决议 %d 条(逐条见'
                    ' pending_at_as_of)' % (as_of, len(pend)))
            else:
                ud = _days(st.get('last_confirmed_on'), as_of)
                row['unconfirmed_days'] = ud
                if ud is not None and ud <= bound:
                    row['answer'] = 'none_pending'
                    row['basis_text'] = (
                        '官方日历实录: 截至 %s 无已决议未生效条目——最近实录'
                        ' %s(确认覆盖至该日,其后 %d 天;本地日历未收录≠未发生)'
                        % (as_of, st.get('last_confirmed_on'), ud))
                else:
                    row['answer'] = 'unverifiable'
                    row['basis_text'] = (
                        '官方日历实录确认覆盖止于 %s,距研究时点 %s 天——'
                        '超出无确认上限 %d 天,待生效状态不可核验'
                        % (st.get('last_confirmed_on'), ud, bound))
                    _gap(gaps, 'pending_unverified', eco, mid,
                         '实录确认覆盖止于 %s,距研究时点 %s 天>上限 %d 天'
                         '——待生效状态不可核验'
                         % (st.get('last_confirmed_on'), ud, bound))
        else:
            has_series = any(s.get('value') is not None
                             for s in (t.get('series_rows') or []))
            row.update(
                path=('series_convention' if has_series else 'missing'),
                status=('series_convention_unverifiable' if has_series
                        else 'missing'),
                answer='unverifiable')
            if has_series:
                row['basis_text'] = (
                    '序列+惯例路径: 窗内已生效变动见 in_window_changes;已决议'
                    '未生效的决定须官方公告核实——本地日历无该经济体政策'
                    '实录,待生效面不可核验(未收录≠无)')
                _gap(gaps, 'pending_unverified', eco, mid,
                     '官方政策决议日历实录缺席——已决议待生效的决定不可'
                     '核验(序列只能给出已生效变动)')
            else:
                row['basis_text'] = '政策序列与官方实录均缺席——待生效面不可答'
                _gap(gaps, 'policy_series_missing', eco, mid,
                     '政策序列缺席——已生效变动与待生效面均无证据')
        rows.append(row)
    return rows


def _inflation_face(plan, qt, snap, root, as_of, gaps):
    """通胀同比面: 最新可见读数 vs 去年同月读数(百分点差=读数之差)。"""
    rmp = _rmp()
    want_base = ((qt.get('yoy_base') or {}).get('kind')
                 == 'same_month_last_year')
    rows = []
    for eco, c in _plan_cells(plan, 'inflation'):
        mid = c.get('metric_id')
        la = _latest_anchor(c)
        row = {'region': eco, 'label': rmp._REGION_LABEL.get(eco, eco),
               'metric_id': mid, 'display_name': c.get('display_name'),
               'unit': c.get('unit'), 'status': 'missing', 'value': None,
               'observation_month': None, 'observation_date': None,
               'period_end': None, 'publish_date': None,
               'publish_basis': None, 'publish_basis_text': None,
               'vintage': None, 'vintage_semantics': c.get('vintage_semantics'),
               'base': None, 'delta_pp': None, 'direction': None,
               'lag_days': None, 'freshness': None, 'note': None,
               'evidence_refs': []}
        if la.get('status') != 'ok' or la.get('value') is None:
            row['note'] = la.get('note') or la.get('status') or '数据不可得'
            _gap(gaps, 'inflation_reading_missing', eco, mid,
                 '最新同比读数不可得(%s)' % row['note'])
            rows.append(row)
            continue
        freq = c.get('frequency')
        s, _err = rmp._series(mid, snap, root)
        dates = list((s or {}).get('dates') or [])
        values = list((s or {}).get('values') or [])
        obs = la.get('observation_date')
        refs = ['%s@%s' % (mid, obs)]
        base = None
        if want_base:
            bdate = rmp._shift_months(obs, 12)
            j = dates.index(bdate) if bdate in dates else None
            if j is not None and j < len(values) and values[j] is not None:
                bpub, bbasis = rmp._visible_publish(mid, freq, bdate)
                base = {'kind': 'same_month_last_year',
                        'observation_month': bdate[:7],
                        'observation_date': bdate, 'value': values[j],
                        'publish_date': bpub, 'publish_basis': _pub_kind(bbasis),
                        'publish_basis_text': bbasis,
                        'evidence_ref': '%s@%s' % (mid, bdate)}
                refs.append(base['evidence_ref'])
            else:
                base = {'kind': 'same_month_last_year',
                        'observation_month': (bdate or '')[:7] or None,
                        'observation_date': bdate, 'value': None,
                        'publish_date': None, 'publish_basis': None,
                        'publish_basis_text': None, 'evidence_ref': None,
                        'note': '序列无该月观测(序列首观测 %s;不可判)'
                                % (dates[0] if dates else '序列缺席')}
                _gap(gaps, 'inflation_base_missing', eco, mid,
                     '去年同月读数不在序列(序列首观测 %s)——与去年同月的'
                     '比较不可判,不以邻近月份冒充'
                     % (dates[0] if dates else '序列缺席'))
        else:
            base = {'kind': (qt.get('yoy_base') or {}).get('kind'),
                    'value': None,
                    'note': '问句只问同比读数(%s)——与去年同月读数的差非'
                            '本次分量' % ((qt.get('yoy_base') or {})
                                         .get('source') or '同比')}
        pub, pbasis = rmp._visible_publish(mid, freq, obs)
        pub = la.get('publication_date') or pub
        pbasis = la.get('publication_basis') or pbasis
        delta = None
        if base.get('value') is not None:
            delta = round(la.get('value') - base['value'], 2)
        fresh = None
        try:
            fresh = _fp().assess_observation_freshness(
                mid, obs, as_of).get('status')
        except (TypeError, ValueError, KeyError):
            fresh = None
        row.update(
            status=('ok' if (base.get('value') is not None or not want_base)
                    else 'base_missing'),
            value=la.get('value'), observation_month=str(obs)[:7],
            observation_date=obs, period_end=la.get('period_end'),
            publish_date=pub, publish_basis=_pub_kind(pbasis),
            publish_basis_text=pbasis, vintage=la.get('vintage'),
            base=base, delta_pp=delta,
            direction=(None if delta is None else
                       ('lower' if delta < 0 else
                        ('higher' if delta > 0 else 'flat'))),
            lag_days=_days(pub, as_of), freshness=fresh,
            evidence_refs=refs,
            reading_note=('同比读数(%%)与去年同月同比读数(%%)之差=百分点(pp);'
                          '非通胀率本身的变化' if want_base else
                          '同比读数(%%)'))
        if row['publish_basis'] == 'rule_estimated':
            _gap(gaps, 'publication_date_estimated', eco, mid,
                 '公布日为规则推定(%s),非日历实录' % (pbasis or '推定规则'))
        if fresh and fresh != 'FRESH':
            _gap(gaps, 'inflation_freshness_%s' % str(fresh).lower(), eco,
                 mid, '最新读数新鲜度 %s' % fresh)
        rows.append(row)
    return rows


def version_gaps(plan, eg, as_of):
    """缺历史版本明确标缺证(Audit-R33 任务3): 历史截止视图且无 as-of 版本
    快照→顶层一行+面内声明修订口径的序列逐条;证据口径门其余涉及面内
    指标的顶层缺口逐条回声(不吞;与面无关的不重复)。→ [缺口行]。"""
    out = []
    if not (eg.get('historical_view') and isinstance(eg.get('gaps'), list)):
        return out
    mids = set(plan.get('metrics') or [])
    eco_of = {}
    for dim in ('policy', 'inflation'):
        for eco, c in _plan_cells(plan, dim):
            eco_of.setdefault(c.get('metric_id'), eco)
    for g in eg.get('gaps') or []:
        if not isinstance(g, dict):
            continue
        code = g.get('gap')
        hit = sorted(set(g.get('series') or []) & mids)
        if code == 'historical_version_missing':
            out.append({'code': code, 'region': None, 'metric_id': None,
                        'severity': 'disclosed',
                        'note': ('数据树内无 target_date≤研究截止日 %s 的冻结'
                                 '快照(缺历史版本)——事实/历史序列/派生值均'
                                 '取自较晚版本 %s(版本日 %s)的截止视图,可能含'
                                 '后续修订,不得表述为当时首发值或当时冻结版'
                                 % (as_of, eg.get('source_snapshot_id'),
                                    eg.get('source_target_date')))})
            rev = sorted(set((eg.get('vintage') or {}).get('revised_series')
                             or []) & mids)
            for mid in rev:
                out.append({'code': code, 'region': eco_of.get(mid),
                            'metric_id': mid, 'severity': 'disclosed',
                            'note': ('研究截止日 %s 无当日版本快照——该序列'
                                     '声明最新修订口径,面值=最新修订值(非当时'
                                     '首发值),引用须随行标注' % as_of)})
        elif hit:
            out.append({'code': code, 'region': None, 'metric_id': None,
                        'severity': 'disclosed',
                        'note': '%s(面内指标: %s)'
                                % (g.get('detail'), '、'.join(hit))})
    return out


def region_order(question, ecos):
    """问句点名顺序(地区名首次出现位置)→行序;未点名者保持原序殿后。"""
    rmp = _rmp()
    q = rmp._norm_q(question or '')
    idx = {e: i for i, e in enumerate(ecos)}
    pos = {}
    for eco in ecos:
        lab = rmp._REGION_LABEL.get(eco)
        if lab and lab in q:
            pos[eco] = q.index(lab)
    return sorted(ecos, key=lambda e: (pos.get(e, len(q) + idx[e]), idx[e]))


def _by_region(rows, order):
    """按地区序稳定重排行(同地区多行保持原相对序;序外地区殿后)。"""
    return sorted(rows, key=lambda r: (
        order.index(r.get('region')) if r.get('region') in order
        else len(order)))


def build_faces(plan, snap, root, as_of, question=None, point_values=None):
    """原问直答三面(引擎确定性;逐行可复算)+缺口点名+版本绑定。"""
    rmp = _rmp()
    q = question if question is not None else (plan.get('question_verbatim') or '')
    qt = dict(plan.get('question_time') or parse_question_time(q, as_of))
    pv = point_values if point_values is not None else (plan.get('point_values') or {})
    cal = (os.path.join(root, 'config', 'release_calendar.json')
           if root else None)
    gaps = []
    states = _policy_states(plan, as_of, cal)
    t_rows = _policy_targets_face(plan, states, as_of, gaps)
    p_rows = _pending_face(plan, qt, states, t_rows, as_of, gaps)
    y_rows = _inflation_face(plan, qt, snap, root, as_of, gaps)
    # Audit-R33 任务3: 三面与缺口按问句点名顺序出行(「日本和欧元区」
    # → 日本在前);只动行序
    _order = region_order(q, [r.get('region') for r in
                              t_rows + p_rows + y_rows])
    t_rows, p_rows, y_rows = (_by_region(t_rows, _order),
                              _by_region(p_rows, _order),
                              _by_region(y_rows, _order))
    eg = (snap or {}).get('evidence_gate') or {}
    gaps += version_gaps(plan, eg, as_of)
    gaps.sort(key=lambda g: (
        _order.index(g.get('region')) if g.get('region') in _order
        else len(_order)))
    block = {
        'schema': SCHEMA, 'as_of': as_of, 'question_time': qt,
        'policy_targets': {'asked': bool(qt.get('policy_target_ask')),
                           'rows': t_rows},
        'pending_decisions': {'asked': bool(qt.get('pending_ask')),
                              'rows': p_rows},
        'inflation_yoy': {'asked': bool(qt.get('inflation_yoy_ask')),
                          'rows': y_rows},
        'gaps': gaps,
        'summary': {
            'policy_targets': {'n': len(t_rows), **{
                k: sum(1 for r in t_rows if r.get('status') == k)
                for k in ('official_record', 'series_convention_derived',
                          'current_target_missing_evidence', 'missing')}},
            'pending_decisions': {'n': len(p_rows), **{
                k: sum(1 for r in p_rows if r.get('answer') == k)
                for k in ('pending', 'none_pending', 'unverifiable')}},
            'inflation_yoy': {'n': len(y_rows), **{
                k: sum(1 for r in y_rows if r.get('status') == k)
                for k in ('ok', 'base_missing', 'missing')}},
            'gaps': len(gaps),
            'blocked_class': None},
        'version_binding': {
            'as_of': eg.get('as_of'),
            'source_snapshot_id': eg.get('source_snapshot_id'),
            'source_target_date': eg.get('source_target_date'),
            'historical_view': bool(eg.get('historical_view')),
            'value_version': eg.get('vintage'),
            'publication_basis': eg.get('publication_basis'),
            'official_record_source': (
                'config/release_calendar.json(日历实录;随运行冻结输入钉死)'
                if cal else None),
            'series': {m: (eg.get('series') or {}).get(m)
                       for m in (plan.get('metrics') or [])}},
    }
    block['summary']['blocked_class'] = blocked_class(block)
    return block


def blocked_class(block):
    """原问直答面缺口分级(判定与渲染共源)。

    被问及的面无证据可答(政策目标缺证/通胀读数全缺)=草稿类
    policy_question_face_missing(交付草稿,正式归档拒绝);面块本身缺席=
    policy_question_faces_missing;其余(非官方口径推定/待生效不可核验/
    公布日推定/基期缺)=披露,不阻断。"""
    if not isinstance(block, dict) or block.get('schema') != SCHEMA:
        return 'policy_question_faces_missing'
    qt = block.get('question_time') or {}
    if qt.get('policy_target_ask'):
        rows = (block.get('policy_targets') or {}).get('rows') or []
        if not rows or any(r.get('status') in ('missing',
                                               'current_target_missing_evidence')
                           for r in rows):
            return 'policy_question_face_missing'
    if qt.get('inflation_yoy_ask'):
        rows = (block.get('inflation_yoy') or {}).get('rows') or []
        if not rows or all(r.get('status') == 'missing' for r in rows):
            return 'policy_question_face_missing'
    return None


def evidence_rows(block, existing_refs=()):
    """三面引用的政策实录行+计划序列点行→证据索引行(按 ref 去重)。"""
    have = set(existing_refs or ())
    out = []

    def _add(ref, kind, mid, role):
        if not ref or ref in have:
            return
        have.add(ref)
        out.append({'ref': ref, 'kind': kind, 'metric_id': mid, 'role': role})

    for r in ((block or {}).get('policy_targets') or {}).get('rows') or []:
        for ref in r.get('evidence_refs') or []:
            _add(ref, 'policy_record' if ref.startswith('POLICY:')
                 else 'plan_series_point', r.get('official_metric_id'),
                 'policy_target')
    for r in ((block or {}).get('pending_decisions') or {}).get('rows') or []:
        for ref in r.get('evidence_refs') or []:
            _add(ref, 'policy_record' if ref.startswith('POLICY:')
                 else 'plan_series_point', r.get('metric_id'),
                 'pending_decision')
    for r in ((block or {}).get('inflation_yoy') or {}).get('rows') or []:
        for i, ref in enumerate(r.get('evidence_refs') or []):
            _add(ref, 'plan_series_point', r.get('metric_id'),
                 'yoy_base' if i == 1 else 'latest_reading')
    return out


def _fmt(v):
    if v is None:
        return '数据不可得'
    if isinstance(v, float):
        return '%g' % v
    return str(v)


def render_time_section(qt, as_of_declared=None):
    qt = qt or {}
    a = as_of_declared or {}
    lines = ['## 研究时点与问句时间分量(分别解析)', '']
    rm_ = qt.get('research_month')
    if rm_:
        lines.append('- 研究年月: %s(问句「%d年%d月」)→ 月末时点 %s'
                     % (rm_, int(rm_[:4]), int(rm_[5:7]),
                        qt.get('research_month_end') or '—'))
    else:
        lines.append('- 研究年月: 问句未声明独立年月——研究时点按运行级研究'
                     '截止日')
    if a:
        lines.append('- 研究截止日: %s(快照 target_date %s%s;口径: %s)'
                     % (a.get('as_of'), a.get('snapshot_target_date') or '—',
                        ';与快照不一致,以问句年月为准'
                        if a.get('differs_from_snapshot') else '',
                        a.get('note') or a.get('basis') or '—'))
    win = qt.get('lookback_window')
    if win:
        lines.append('- 回看窗口: 「%s」= %s..%s(%d 个月)→ 作用于: 政策目标'
                     '水平与已决议待生效的决定'
                     % (win.get('source'), win.get('from'), win.get('to'),
                        int(win.get('months') or 0)))
    else:
        lines.append('- 回看窗口: 问句未限定回看窗口(待生效=研究时点时点面;'
                     '窗内决议面不列)')
    yb = qt.get('yoy_base')
    if yb:
        lines.append('- 同比基期: 「%s」(%s)→ 作用于: 通胀同比(最新同比读数 vs '
                     '去年同月同比读数,差=百分点)'
                     % (yb.get('source'), yb.get('kind')))
    else:
        lines.append('- 同比基期: 问句未要求与去年同月读数比较')
    lines.append('')
    return lines


def render_faces_sections(block):
    """三面表格(数值=引擎确定性面;每行附观测日/公布日/口径来源)。"""
    block = block or {}
    lines = []
    # ── 政策目标 ──
    lines += ['## 政策目标(官方口径优先;逐行可复算)', '']
    t_rows = (block.get('policy_targets') or {}).get('rows') or []
    if not (block.get('policy_targets') or {}).get('asked'):
        lines += ['(问句未问及政策目标)', '']
    elif not t_rows:
        lines += ['数据不可得(计划无政策维指标——缺口见下节)', '']
    else:
        lines += ['| 地区 | 官方口径 | 目标水平(%) | 决议日 | 生效日 | 公布日 | '
                  '最近确认维持 | 口径来源 |',
                  '|---|---|---|---|---|---|---|---|']
        for r in t_rows:
            src = {'official_record': '日历实录 %s' % (r.get('official_entry_id') or ''),
                   'series_convention_derived': '序列+惯例推定(官方实录缺席)',
                   'current_target_missing_evidence': '现值缺证',
                   'missing': '无证据'}.get(r.get('status'), r.get('status'))
            lines.append('| %s | %s(%s) | %s | %s | %s | %s | %s | %s |' % (
                r.get('label'), _official_label(r),
                r.get('official_metric_id') or '—',
                _fmt(r.get('target')), r.get('decision_date') or '—',
                r.get('effective_date') or '—', r.get('first_publish') or '—',
                r.get('last_maintenance') or '—', src))
        lines.append('')
        for r in t_rows:
            for s in r.get('series_rows') or []:
                lines.append('- %s·序列面: %s(%s)= %s %s(观测日 %s;公布 %s%s)'
                             % (r.get('label'), s.get('display_name'),
                                s.get('metric_id'), _fmt(s.get('value')),
                                s.get('unit') or '',
                                s.get('observation_date') or '—',
                                s.get('publish_date') or '—',
                                ',规则推定' if s.get('publish_basis')
                                == 'rule_estimated' else ''))
    lines.append('')
    # ── 已决议待生效 ──
    lines += ['## 已决议但尚未生效的调整(回看窗内决议/变动分记)', '']
    p_rows = (block.get('pending_decisions') or {}).get('rows') or []
    if not (block.get('pending_decisions') or {}).get('asked'):
        lines += ['(问句未问及待生效调整)', '']
    elif not p_rows:
        lines += ['数据不可得(计划无政策维指标——缺口见下节)', '']
    else:
        w = (p_rows[0].get('window') or {})
        if w:
            lines.append('回看窗口: %s = %s..%s(%d 个月)'
                         % (w.get('source'), w.get('from'), w.get('to'),
                            int(w.get('months') or 0)))
            lines.append('')
        lines += ['| 地区 | 口径 | 截至研究时点待生效 | 窗内已生效决议 | '
                  '窗内序列变动 | 确认覆盖至 | 判定 |',
                  '|---|---|---|---|---|---|---|']
        for r in p_rows:
            pend_txt = ('、'.join(
                '%s 决议→%s 生效,目标 %s%%'
                % (p.get('decision_date'), p.get('effective_on'),
                   _fmt(p.get('target_value')))
                for p in r.get('pending_at_as_of') or []) or '无')
            dec_txt = '、'.join(
                '%s 决议→%s 生效,目标 %s%%%s'
                % (d.get('decision_date'), d.get('effective_on'),
                   _fmt(d.get('target_value')),
                   ('(%+d bp)' % d['delta_bp']) if d.get('delta_bp') is not None
                   else '(幅度缺官方记录)') for d in r.get('in_window_decisions')
            ) or '—'
            chg_txt = '、'.join(
                '%s %s %s→%s(%+d bp%s)'
                % (c.get('metric_id'), c.get('date'), _fmt(c.get('from')),
                   _fmt(c.get('to')), int(c.get('delta_bp') or 0),
                   ';决议日 %s(惯例)' % c['decision_date']
                   if c.get('decision_date') else ';月均观测')
                for c in r.get('in_window_changes')) or '—'
            ans = {'pending': '**有**待生效调整',
                   'none_pending': '无待生效调整(实录确认覆盖内)',
                   'unverifiable': '**不可核验**(官方实录缺席)'}.get(
                       r.get('answer'), r.get('answer'))
            lines.append('| %s | %s | %s | %s | %s | %s | %s |' % (
                r.get('label'),
                {'official_record': '日历实录',
                 'series_convention': '序列+惯例',
                 'missing': '无证据'}.get(r.get('path'), r.get('path')),
                pend_txt if r.get('path') == 'official_record' else '—',
                dec_txt, chg_txt,
                r.get('confirmed_through') or '—',
                '%s(%s)' % (ans, r.get('answer'))))
        lines.append('')
        for r in p_rows:
            if r.get('in_window_maintenance'):
                lines.append('- %s·窗内确认维持: %s'
                             % (r.get('label'), '、'.join(
                                 '%s(目标 %s%%)' % (m.get('decision_date'),
                                                    _fmt(m.get('target_value')))
                                 for m in r['in_window_maintenance'])))
        lines.append('')
    # ── 通胀同比 ──
    lines += ['## 通胀同比(最新读数 vs 去年同月;差=百分点)', '']
    y_rows = (block.get('inflation_yoy') or {}).get('rows') or []
    if not (block.get('inflation_yoy') or {}).get('asked'):
        lines += ['(问句未问及通胀同比)', '']
    elif not y_rows:
        lines += ['数据不可得(计划无通胀维指标——缺口见下节)', '']
    else:
        lines += ['| 地区 | 指标 | 观测月 | 最新同比(%) | 公布日 | 去年同月同比(%) | '
                  '基期公布日 | 差(pp) | 方向 |',
                  '|---|---|---|---|---|---|---|---|---|']
        for r in y_rows:
            b = r.get('base') or {}
            lines.append('| %s | %s(%s) | %s | %s | %s | %s | %s | %s | %s |' % (
                r.get('label'), r.get('display_name'), r.get('metric_id'),
                r.get('observation_month') or '—', _fmt(r.get('value')),
                (r.get('publish_date') or '数据不可得')
                + ('(规则推定)' if r.get('publish_basis') == 'rule_estimated'
                   else ''),
                _fmt(b.get('value')),
                (b.get('publish_date') or '—')
                + ('(规则推定)' if b.get('publish_basis') == 'rule_estimated'
                   else ''),
                ('%+.2f' % r['delta_pp']) if r.get('delta_pp') is not None
                else '不可判',
                {'lower': '低于去年同月', 'higher': '高于去年同月',
                 'flat': '与去年同月持平'}.get(r.get('direction'), '不可判')))
        lines.append('')
        for r in y_rows:
            if r.get('note') or (r.get('base') or {}).get('note'):
                lines.append('- %s·%s: %s' % (
                    r.get('label'), r.get('metric_id'),
                    r.get('note') or (r.get('base') or {}).get('note')))
        lines.append('')
    return lines


def _official_label(r):
    for s in r.get('series_rows') or []:
        if s.get('metric_id') == r.get('official_metric_id'):
            return s.get('face') or s.get('display_name') or '—'
    return {'JP': '政策目标利率(宣布值)', 'EA': '主要再融资利率',
            'US': '联邦基金目标区间上限', 'CN': 'LPR 1年期'}.get(
                r.get('region'), '官方目标口径')


def render_gap_section(block):
    gaps = (block or {}).get('gaps') or []
    lines = ['## 缺口(披露;逐项点名,不以相邻口径冒充)', '']
    if not gaps:
        lines += ['- 无(三面数值均有证据;公布日口径见各表注)', '']
    else:
        for g in gaps:
            lab = _rmp()._REGION_LABEL.get(g.get('region'))
            head = ('%s·%s' % (lab, g.get('metric_id'))
                    if lab and g.get('metric_id')
                    else (lab or g.get('metric_id') or '全体'))
            lines.append('- %s: %s [%s]' % (head, g.get('note'),
                                            g.get('code')))
        lines.append('')
    return lines


_VINTAGE_TEXT = {
    'snapshot_vintage': '快照版本(截止日=快照版本日,快照在场即当时可得)',
    'as_of_vintage': 'as-of 冻结版本(当时可得的数据版本)',
    'latest_revision_only': '仅最新修订值(无 as-of 版本快照;非当时首发值)',
    'not_declared_revised': '快照值(未声明修订口径,值不随版本变)',
    'not_in_as_of_vintage': '不在 as-of 版本内(截止后回填,已剔除)',
    'latest_revision_no_version_available': '当时数据版本不可得(已剔除)',
    'no_eligible_observation': '截止视图内无可引用观测(已剔除)'}
_BASIS_TEXT = {
    'snapshot_vintage': '快照版本(截止日=快照版本日)',
    'as_of_vintage': 'as-of 版本快照',
    'no_asof_vintage_snapshot': ('无 as-of 版本快照(取较晚快照的截止视图: 声明'
                                 '修订口径的序列=最新修订值,非当时首发值;见'
                                 '「缺口」)')}


def render_binding_section(block):
    vb = (block or {}).get('version_binding') or {}
    lines = ['## 版本绑定(事实表/历史序列/派生值同一份当时可得的冻结版本)', '']
    v = vb.get('value_version') or {}
    lines.append('- 证据口径: 截止日 %s | 源快照 %s(版本日 %s)%s | 值版本 %s'
                 % (vb.get('as_of'), vb.get('source_snapshot_id') or '—',
                    vb.get('source_target_date') or '—',
                    ' | 历史截止视图(晚观测/晚发布/当时不可得版本不入面)'
                    if vb.get('historical_view') else '',
                    _BASIS_TEXT.get(v.get('basis'), v.get('basis') or '—')))
    if v.get('vintage_snapshot_id'):
        lines.append('- 值版本快照: %s' % v.get('vintage_snapshot_id'))
    for mid, s in (vb.get('series') or {}).items():
        if isinstance(s, dict):
            lines.append('- 序列 %s: 入证 %s / %s 观测%s | 版本 %s%s' % (
                mid, s.get('n_kept'), s.get('n_in'),
                ('(剔晚观测 %s/晚发布 %s/版本不可得 %s)'
                 % (s.get('n_late_observation'), s.get('n_late_publication'),
                    s.get('n_version_unavailable')))
                if (s.get('n_late_observation') or s.get('n_late_publication')
                    or s.get('n_version_unavailable')) else '',
                _VINTAGE_TEXT.get(s.get('vintage'), s.get('vintage')),
                ' | 排除(当时数据版本不可得)'
                if s.get('excluded') else ''))
    if vb.get('official_record_source'):
        lines.append('- 官方政策记录来源: %s' % vb.get('official_record_source'))
    lines.append('')
    return lines


def render_seat_section(rm):
    """Agent 席判断原文(总判断+结构化回声行的席位注记;数值经契约对账)。"""
    rm = rm if isinstance(rm, dict) else {}
    pq = rm.get('policy_question') if isinstance(
        rm.get('policy_question'), dict) else {}
    lines = ['## Agent 席判断(席位原文;数值与引擎面对账后才可落位)', '']
    hl = str(rm.get('headline_conclusion') or '').strip()
    lines += ['- 总判断: %s' % (hl or '(席位未给总判断)'), '']
    for key, title in (('official_targets', '政策目标'),
                       ('pending_decisions', '已决议待生效'),
                       ('inflation_yoy', '通胀同比')):
        rows = pq.get(key) or []
        notes = [str(r.get('note') or '').strip() for r in rows
                 if isinstance(r, dict) and str(r.get('note') or '').strip()]
        lines.append('- %s(席位注记 %d 条): %s' % (
            title, len(notes), ' / '.join(notes) if notes else '—'))
    cm = pq.get('comments')
    cm_rows = ([str(c).strip() for c in cm if str(c).strip()]
               if isinstance(cm, list)
               else ([str(cm).strip()] if cm and str(cm).strip() else []))
    if cm_rows:
        lines += ['', '席位补充说明:'] + ['- %s' % c for c in cm_rows]
    lines.append('')
    return lines


def _gate_face_note(header_lines, block, snap):
    """页眉数据门(Gate A)记的是源快照的**当日采集面**;原问直答三面取的是
    快照**序列面**(series_store)——同一指标两面状态可以不同(当日采集缺席/
    降级而序列面在场)。本问用到的指标逐个对照两面,免得页眉「不得进入
    研究结论」与正文取数互相打架;本问指标不在缺席/降级名单=页眉原样。
    → (页眉行的替换行 or None, 追加行列表)"""
    ga = snap.get('gate_a') if isinstance(snap, dict) else None
    if not isinstance(block, dict) or not isinstance(ga, dict):
        return None, []
    miss = (list(ga.get('core_missing') or [])
            + list(ga.get('noncore_missing') or []))
    degr = list(ga.get('noncore_degraded') or [])
    detail = ga.get('noncore_missing_detail') or {}
    use = {}
    for r in (block.get('policy_targets') or {}).get('rows') or []:
        for sr in r.get('series_rows') or []:
            if sr.get('metric_id'):
                use.setdefault(sr['metric_id'], []).append(
                    '目标水平按序列+惯例推定呈现(非官方口径)'
                    if r.get('status') == 'series_convention_derived'
                    else '目标水平为日历实录,序列仅作对照')
    for r in (block.get('inflation_yoy') or {}).get('rows') or []:
        if r.get('metric_id'):
            use.setdefault(r['metric_id'], []).append(
                '取序列面最新读数 %s(%s 观测)'
                % (r.get('value'), r.get('observation_month'))
                if r.get('value') is not None
                else '序列面无可用读数→数据不可得')
    items = []
    for mid, roles in use.items():
        if mid in miss:
            d = detail.get(mid) if isinstance(detail, dict) else None
            items.append('%s 当日采集面缺席%s——%s'
                         % (mid, '(%s)' % d if d else '', ';'.join(roles)))
        elif mid in degr:
            items.append('%s 当日采集面降级——%s' % (mid, ';'.join(roles)))
    if not items:
        return None, []
    old = ('——缺席/降级数据不得进入研究结论;逐指标注记见快照 '
           'gate_a.noncore_missing_detail,信封步状态见步骤台账')
    new = ('——采集面缺席/降级的当日事实不入证据面;本问改取序列面读数的'
           '指标见下行两面对照;逐指标注记见快照 gate_a.noncore_'
           'missing_detail,信封步状态见步骤台账')
    for i, ln in enumerate(header_lines):
        if ln.startswith('- 数据门(Gate A') and ln.endswith(old):
            return (ln[:-len(old)] + new), [
                '  - 本问指标两面对照(Gate A=当日采集面;三面取快照序列面 '
                'series_store,同指标两面状态可不同): ' + ' | '.join(items)]
    return None, []


def _blocked_text(bc):
    return {'policy_question_face_missing':
            '被问及的分面无证据可答(政策目标缺证或通胀读数全缺)',
            'policy_question_faces_missing': '原问直答事实面缺席'}.get(bc, bc)


def render_policy_question_report(rj, judgment_doc, review_state=None,
                                  root=None):
    """原问直答读者报告(问什么答什么): 共享页眉(与地图报告同一装配)+
    草稿横幅+一句总判断+时间分量+三面表格+缺口+版本绑定+席位原文+重放/审查。"""
    rmp = _rmp()
    rp = rj.get('research_plan') or {}
    block = rp.get('policy_question')
    lines, _snap_r, _snap_note = rmp._report_header(
        rj, review_state, root, REPORT_TITLE)
    # Gate A(当日采集面)与本问取数(序列面)的两面对照(页眉行随对照改写)
    _g_ln, _g_add = _gate_face_note(lines, block, _snap_r)
    if _g_ln is not None:
        _gi = next(i for i, x in enumerate(lines) if x.startswith('- 数据门(Gate A'))
        lines[_gi:_gi + 1] = [_g_ln] + _g_add
    rm = (judgment_doc or {}).get('reader_map') or {}
    bc = blocked_class(block)
    if bc:
        lines += ['⚠ **草稿(非正式)**: %s——首页标草稿;正式交付与正式归档'
                  '阻断(补数/补录官方实录后重跑续链)' % _blocked_text(bc), '']
    lines += ['## 一句总判断', '',
              str(rm.get('headline_conclusion') or '').strip()
              or '(席位未给总判断)', '']
    lines += render_time_section(
        (block or {}).get('question_time') or rp.get('question_time'),
        rp.get('as_of_declared'))
    if not isinstance(block, dict):
        lines += ['## 原问直答事实面', '',
                  '**缺席**——研究计划未生成原问直答三面(缺口: 面块缺席)', '']
    else:
        lines += render_faces_sections(block)
        lines += render_gap_section(block)
        lines += render_binding_section(block)
    lines += render_seat_section(rm)
    lines += rmp._report_tail(rj, review_state)
    return '\n'.join(lines) + '\n'
