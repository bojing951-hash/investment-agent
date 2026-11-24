# rc_common.py -- Audit-R32 N30 round1 seat: shared helpers (read-only recompute)
import json, sys, os, hashlib, datetime as dt, calendar, re

def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()

DG = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}

def cnint(s):
    if '十' in s:
        a, b = s.split('十', 1)
        return (DG[a] if a else 1) * 10 + (DG[b] if b else 0)
    return int(''.join(str(DG[c]) for c in s))

def cn2num(s):
    s = s.replace('百分之', '')
    if '点' in s:
        a, b = s.split('点', 1)
        return float(str(cnint(a)) + '.' + ''.join(str(DG[c]) for c in b))
    return float(cnint(s))

def iscn(t):
    return any((c in DG) or c == '十' or c == '点' for c in t)

def pnum(tok):
    t = tok.replace('百分之', '').replace('%', '').replace('bp', '')
    if iscn(t):
        return cn2num(t)
    return float(t)

def dec_of(x):
    s = ('%f' % float(x)).rstrip('0')
    return 0 if '.' not in s else len(s.split('.')[1])

def close(a, b, dec=None, tol=None):
    try:
        fa, fb = float(a), float(b)
    except Exception:
        return False
    if tol is None:
        d = dec_of(fb) if dec is None else dec
        tol = 0.5 * (10 ** -d) + 1e-9
    return abs(fa - fb) <= tol

def r1(x):
    return float('%f' % x)

def D(s):
    return dt.date(int(s[:4]), int(s[5:7]), int(s[8:10]))

def mend(ym):
    y, m = int(ym[:4]), int(ym[5:7])
    return dt.date(y, m, calendar.monthrange(y, m)[1]).isoformat()

def plus(d, n):
    return (D(d) + dt.timedelta(days=n)).isoformat()

def days(a, b):
    return (D(b) - D(a)).days

def prev_thu(d):
    x = D(d)
    return (x - dt.timedelta(days=(x.weekday() - 3) % 7)).isoformat()

def pct(a, b):
    return (float(b) / float(a) - 1.0) * 100.0

def wd(d):
    return ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][D(d).weekday()]

TOKRE = re.compile('[百分之]*[零一二三四五六七八九十]+(点[零一二三四五六七八九]+)?|[0-9]+[.][0-9]+|[0-9]+')

class Ctx:
    def __init__(self, snap, rep, cal, reg, aj, out):
        self.snap = load(snap); self.rep = load(rep); self.cal = load(cal)
        self.reg = load(reg); self.aj = load(aj); self.out = out
        self.S = self.snap['series_store']; self.F = self.snap['facts']
        td = str(self.snap.get('target_date'))
        if len(td) == 8 and td.isdigit():
            td = td[:4] + '-' + td[4:6] + '-' + td[6:]
        self.target = td
        self.asof = '2026-11-23'
        self.leaves = []
        self._walk(self.aj, '')
        self.pts = []; self.diag = []; self.cover = set()
        self.RM = {}
        rl = self.reg.get('metrics') if isinstance(self.reg, dict) else self.reg
        for r in rl:
            self.RM[r.get('metric_id')] = r

    def _walk(self, o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                self._walk(v, path + '.' + k if path else k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                self._walk(v, path + '[' + str(i) + ']')
        elif isinstance(o, str):
            self.leaves.append((path, o))

    # ---- series_store accessors ----
    def s(self, m):
        return self.S[m]
    def has_m(self, m):
        return m in self.S
    def at(self, m, d):
        s = self.S[m]; i = s['dates'].index(d); return s['values'][i]
    def has(self, m, d):
        return d in self.S[m]['dates']
    def last(self, m):
        s = self.S[m]; return (s['dates'][-1], s['values'][-1])
    def n(self, m):
        return len(self.S[m]['dates'])
    def first(self, m):
        s = self.S[m]; return (s['dates'][0], s['values'][0])
    def obe(self, m, d):
        best = None
        for dd, v in zip(self.S[m]['dates'], self.S[m]['values']):
            if dd <= d:
                best = (dd, v)
        return best
    def mv(self, m, ym):
        for dd, v in zip(self.S[m]['dates'], self.S[m]['values']):
            if dd[:7] == ym:
                return v
        return None
    def md(self, m, ym):
        for dd in self.S[m]['dates']:
            if dd[:7] == ym:
                return dd
        return None
    def changes(self, m):
        s = self.S[m]; out = []
        for i in range(1, len(s['dates'])):
            if s['values'][i] != s['values'][i - 1]:
                out.append((s['dates'][i], s['values'][i - 1], s['values'][i]))
        return out
    def fact(self, mid):
        for f in self.F:
            if f.get('metric_id') == mid:
                return f
        return None
    def fact_all(self, mid):
        return [f for f in self.F if f.get('metric_id') == mid]

    # ---- presumed publication rules ----
    def pub(self, m, ym):
        if m == 'EA_HICP_YOY':
            return plus(mend(ym), 16)
        if m == 'JP_CPI_YOY':
            return plus(mend(ym), 20)
        if m == 'JP_CPI_TOKYO_YOY':
            return plus(mend(ym), -1)
        if m == 'JP_POLICY_RATE':
            return plus(mend(ym), 5)
        return None
    def vis(self, m, day):
        best = None
        for dd, v in zip(self.S[m]['dates'], self.S[m]['values']):
            if self.pub(m, dd[:7]) <= day:
                best = (dd, v)
        return best

    # ---- point collectors ----
    def _mark(self, tok, snip):
        w = ''
        for i, (path, s) in enumerate(self.leaves):
            p = s.find(snip)
            if p >= 0:
                if not w:
                    w = path
                while p >= 0:
                    q = s.find(tok, p)
                    if q >= 0 and q < p + len(snip):
                        self.cover.add((i, q, q + len(tok)))
                    p = s.find(snip, p + 1)
        return w

    def num(self, sec, src, comp, rep, tok, snip=None, note='', tol=None):
        snip = tok if snip is None else snip
        w = self._mark(tok, snip)
        try:
            tv = pnum(tok)
            ok_t = close(tv, rep)
        except Exception:
            tv = None; ok_t = False
        ok = bool(w) and ok_t and close(comp, rep, tol=tol)
        if not ok_t:
            note = note + ' [转录不符: 文内 token 解析=' + str(tv) + ']'
        if not w:
            note = note + ' [文内未定位]'
        self.pts.append({'sec': sec, 'src': src, 'comp': comp, 'rep': rep, 'tok': tok, 'ok': ok, 'where': w, 'note': note})

    def txt(self, sec, src, comp, rep, tok, snip=None, note=''):
        snip = tok if snip is None else snip
        w = self._mark(tok, snip)
        ok = bool(w) and (tok == rep) and (str(comp) == str(rep))
        if not w:
            note = note + ' [文内未定位]'
        self.pts.append({'sec': sec, 'src': src, 'comp': comp, 'rep': rep, 'tok': tok, 'ok': ok, 'where': w, 'note': note})

    def eq(self, sec, src, comp, rep, note=''):
        # non-text comparison (engine face vs snapshot, structural facts)
        ok = close(comp, rep) if isinstance(rep, (int, float)) and not isinstance(rep, bool) else (str(comp) == str(rep))
        self.pts.append({'sec': sec, 'src': src, 'comp': comp, 'rep': rep, 'tok': '', 'ok': ok, 'where': '(引擎面/结构面交叉核对)', 'note': note})

    def has_text(self, sec, src, snip, note=''):
        w = self._mark(snip, snip)
        self.pts.append({'sec': sec, 'src': src, 'comp': '在场' if w else '不在场', 'rep': '在场', 'tok': snip, 'ok': bool(w), 'where': w, 'note': note})

    def save(self, tag):
        with open(self.out + '_' + tag + '.json', 'w', encoding='utf-8') as f:
            json.dump({'points': self.pts, 'diag': self.diag, 'cover': sorted(self.cover), 'nleaves': len(self.leaves)}, f, ensure_ascii=False)
        np_ = len(self.pts); nm = sum(1 for p in self.pts if not p['ok'])
        print(tag, 'points', np_, 'mismatch', nm)
        for p in self.pts:
            if not p['ok']:
                print('  MISMATCH', p['sec'], p['src'], 'comp=', p['comp'], 'rep=', p['rep'], 'tok=', p['tok'], p['note'], '@', p['where'])

    def ok(self, sec, src, cond, comp, note=''):
        self.pts.append({'sec': sec, 'src': src, 'comp': comp, 'rep': '(判据成立)', 'tok': '', 'ok': bool(cond), 'where': '(判据核对)', 'note': note})

    def uncovered(self):
        out = []
        for i, (path, s) in enumerate(self.leaves):
            for mt in TOKRE.finditer(s):
                k = (i, mt.start(), mt.end())
                if k not in self.cover:
                    out.append((path, mt.group(0), s[max(0, mt.start() - 18): mt.end() + 12].replace(chr(10), ' ')))
        return out
