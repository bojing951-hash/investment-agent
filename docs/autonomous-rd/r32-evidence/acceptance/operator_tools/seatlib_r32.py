#!/usr/bin/env python3
"""seatlib_r32.py — shared helpers for the R32 judgment builders (T3 / NEW30).

Everything here is computed from the run's own frozen inputs (root_overlay
snapshot / release calendar / metric registry / report.json); nothing is
hand-typed.  Introduced after the T3 pre-review at f722e3c (8 MAJOR), whose
findings apply to every judgment that quotes these faces:

  * close vs intraday caliber — the standard update entry ran while the US
    session was open, so US-session / FX rows dated on the cutoff day are
    intraday snapshots; cross-region comparisons use one same-date caliber;
  * ECB decision dates are engine back-casts (decision_kind=prev_thursday),
    not calendar records — labelled 【推断】, publication = series change day;
  * analog step facts read from report.json steps[S6_analog] (it did run).
"""
import bisect
import datetime
import glob
import json
import os
from zoneinfo import ZoneInfo

FX = ('EURUSD', 'USDJPY', 'USDCNY')
# metric -> (IANA zone, session open hh:mm, session close hh:mm)
SESSIONS = {
    'SPX': ('America/New_York', (9, 30), (16, 0)),
    'NDX': ('America/New_York', (9, 30), (16, 0)),
    'RUT': ('America/New_York', (9, 30), (16, 0)),
    'NVDA': ('America/New_York', (9, 30), (16, 0)),
    'VIX': ('America/New_York', (9, 30), (16, 0)),
    'DAX': ('Europe/Berlin', (9, 0), (17, 30)),
    'CAC40': ('Europe/Berlin', (9, 0), (17, 30)),
    'NIKKEI225': ('Asia/Tokyo', (9, 0), (15, 30)),
    'SHCOMP': ('Asia/Shanghai', (9, 30), (15, 0)),
    'HSI': ('Asia/Hong_Kong', (9, 30), (16, 0)),
}
ZONE_LABEL = {'America/New_York': '美股', 'Europe/Berlin': '德法股指', 'Asia/Tokyo': '日股',
              'Asia/Shanghai': 'A股', 'Asia/Hong_Kong': '港股'}
NEAR_24H = ('DXY', 'GOLD_F', 'SILVER_F', 'BRENT_F')      # ICE / futures: near-24h screens


def n(x):
    """engine value: at most three decimals, no trailing zero, at least one (4.0/2.44/1.227)."""
    t = ('%.3f' % float(x)).rstrip('0')
    return t + '0' if t.endswith('.') else t


def f2(x):
    return '%.2f' % x


def f4(x):
    return '%.4f' % x


def sgn2(x):
    return '%+.2f%%' % x


class Frozen(object):
    """read-only view of one research-one run's frozen inputs."""

    def __init__(self, report_dir):
        self.report_dir = report_dir
        self.rep = json.load(open(os.path.join(report_dir, 'report.json'), encoding='utf-8'))
        snaps = glob.glob(os.path.join(report_dir, 'root_overlay', 'data', 'daily',
                                       'research_snapshot_*.json'))
        assert len(snaps) == 1, snaps
        self.snap_p = snaps[0]
        self.snap = json.load(open(snaps[0], encoding='utf-8'))
        self.ss = self.snap['series_store']
        self.cal = json.load(open(os.path.join(report_dir, 'root_overlay', 'config',
                                               'release_calendar.json'), encoding='utf-8'))
        self.reg = json.load(open(os.path.join(report_dir, 'root_overlay', 'config',
                                               'metric_registry.json'), encoding='utf-8'))
        self.as_of = (self.rep.get('research_plan') or {}).get('cutoff')

    # ── series store ───────────────────────────────────────────────────
    def idx(self, mid, day):
        return bisect.bisect_right(self.ss[mid]['dates'], day) - 1

    def val(self, mid, day):
        """value at the last observation on or before day."""
        return self.ss[mid]['values'][self.idx(mid, day)]

    def date(self, mid, day):
        return self.ss[mid]['dates'][self.idx(mid, day)]

    def last_date(self, mid):
        return self.ss[mid]['dates'][-1]

    def ret(self, mid, d0, d1):
        """pct change from the last observation <= d0 to the last observation <= d1."""
        a, b = self.val(mid, d0), self.val(mid, d1)
        return (b / a - 1.0) * 100.0

    def monthly(self, mid):
        """{YYYY-MM: last value observed in that month}."""
        out = {}
        for d, v in zip(self.ss[mid]['dates'], self.ss[mid]['values']):
            out[d[:7]] = v
        return out

    def prev_obs_date(self, mid, day):
        """last observation date strictly before day."""
        return self.ss[mid]['dates'][self.idx(mid, day) - 1]

    def level_before(self, mid, change_day):
        """(since, value) of a change-point series just before the change on change_day."""
        i = self.idx(mid, change_day) - 1
        return self.ss[mid]['dates'][i], self.ss[mid]['values'][i]

    def year_high(self, mid, year):
        pairs = [(d, v) for d, v in zip(self.ss[mid]['dates'], self.ss[mid]['values'])
                 if d.startswith(str(year))]
        return max(pairs, key=lambda p: p[1])

    def step(self, name):
        return next(s for s in self.rep['steps']
                    if isinstance(s, dict) and (s.get('name') or s.get('step')) == name)

    def registry_metric(self, mid):
        ms = self.reg.get('metrics') or self.reg
        if isinstance(ms, dict):
            return ms.get(mid)
        return next((m for m in ms if m.get('metric_id') == mid), None)

    # ── market session state at research_as_of ────────────────────────
    def _local(self, zone):
        return datetime.datetime.fromisoformat(
            self.snap['research_as_of']).astimezone(ZoneInfo(zone))

    def session_open(self, mid):
        zone, o, c = SESSIONS[mid]
        t = self._local(zone)
        hm = (t.hour, t.minute)
        return t.weekday() < 5 and o <= hm < c

    def intraday(self, mid):
        """(is_intraday, tag) for a row dated on the cutoff day."""
        if self.last_date(mid) != self.as_of:
            return False, ''
        dd = self.as_of[5:]
        if mid in FX:
            return True, '%s 值为盘中快照(外汇连续交易,非收盘价)' % dd
        if mid in SESSIONS and self.session_open(mid):
            return True, ('%s 值为盘中快照(%s常规时段进行中,非收盘价)'
                          % (dd, ZONE_LABEL[SESSIONS[mid][0]]))
        if mid in NEAR_24H:
            return True, '%s 值为盘中快照(近 24 小时交易品种,非收盘价)' % dd
        return False, ''

    # ── ECB decision-date labeling (engine convention, no calendar record) ──
    def ecb_calendar_records(self):
        return [e for e in (self.cal.get('entries') or [])
                if str(e.get('metric_id') or '').upper().startswith('ECB')]

    def ecb_event_text(self, e, first=False):
        """'YYYY-MM-DD 生效(决议日 … 系引擎按惯例回推【推断】)'."""
        tail = ('决议日 %s 系引擎按『生效日前上一个周四』惯例自变更日回推【推断】'
                % e['decision_date']) if first else ('决议日 %s 同为惯例回推【推断】'
                                                     % e['decision_date'])
        return '%s 生效(%s)' % (e['date'], tail)


def analog_facts(fr):
    st = fr.step('S6_analog')
    env = st['envelope']['data']
    top = env['top'][0]
    return {'executed': bool(st.get('executed')), 'ok': bool(st.get('ok')),
            'scanned': env['candidates']['scanned'], 'valid': env['candidates']['valid'],
            'top_month': top['candidate_month'], 'distance': top['distance'],
            'n_top': len(env['top'])}


def asset_block(fr, w_start=None):
    """same-date close caliber for the cross-region equity comparison + VIX path."""
    as_of = fr.as_of
    out = {'as_of': as_of}
    # last date on which every US-session row is a close
    close_day = fr.prev_obs_date('SPX', as_of) if fr.last_date('SPX') == as_of \
        else fr.last_date('SPX')
    w0 = w_start
    out['w_start'], out['close_day'] = w0, close_day
    out['equity'] = {}
    for m in ('SPX', 'NIKKEI225', 'DAX', 'CAC40'):
        if m not in fr.ss:
            continue
        last = fr.last_date(m)
        out['equity'][m] = {
            'ret': fr.ret(m, w0, close_day), 'from': fr.val(m, w0),
            'to': fr.val(m, close_day), 'to_date': fr.date(m, close_day),
            'intraday': fr.intraday(m),
            'now': fr.val(m, as_of) if last == as_of else None,
            'ret_now': ((fr.val(m, as_of) / fr.val(m, w0) - 1) * 100) if last == as_of else None}
    v = fr.ss['VIX']
    fri = [(d, x) for d, x in zip(v['dates'], v['values']) if d < as_of
           and datetime.date.fromisoformat(d).weekday() == 4][-3:]
    out['vix_friday'] = fri
    out['vix_now'] = fr.val('VIX', as_of) if fr.last_date('VIX') == as_of else None
    out['vix_now_vs_friday'] = ((out['vix_now'] / fri[-1][1] - 1) * 100
                                if out['vix_now'] is not None else None)
    out['vix_month_close'] = fr.ret('VIX', w0, close_day)
    out['vix_intraday'] = fr.intraday('VIX')
    return out


def fx_block(fr, w_start):
    """FX month-window moves in two calibers: cutoff day (intraday) and prior close."""
    as_of = fr.as_of
    close_day = fr.prev_obs_date('EURUSD', as_of) if fr.last_date('EURUSD') == as_of \
        else fr.last_date('EURUSD')
    out = {'w_start': w_start, 'close_day': close_day, 'fx': {}}
    for m in ('EURUSD', 'USDJPY', 'DXY'):
        if m not in fr.ss:
            continue
        last = fr.last_date(m)
        a = fr.val(m, w_start)
        out['fx'][m] = {
            'from': a,
            'now': fr.val(m, as_of) if last == as_of else None,
            'ret_now': ((fr.val(m, as_of) / a - 1) * 100) if last == as_of else None,
            'close': fr.val(m, close_day), 'close_date': fr.date(m, close_day),
            'ret_close': (fr.val(m, close_day) / a - 1) * 100,
            'intraday': fr.intraday(m)}
    return out
