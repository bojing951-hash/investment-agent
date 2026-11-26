# -*- coding: utf-8 -*-
"""复算点登记(追加写本席目录 points.jsonl)。"""
import json
import os

PTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'points.jsonl')


def add(section, src, computed, reported, ok, note='', where=''):
    """ok: True=一致 / False=偏离 / 'NA'=仅直算记录(无比对对象)"""
    rec = {'section': section, 'where': where, 'src': src, 'computed': computed,
           'reported': reported, 'ok': ok, 'note': note}
    with open(PTS, 'a', encoding='utf-8') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')


def reset():
    if os.path.exists(PTS):
        os.remove(PTS)


def tally():
    n = 0
    mism = 0
    by = {}
    if not os.path.exists(PTS):
        return 0, 0, by
    with open(PTS, encoding='utf-8') as f:
        for line in f:
            rec = json.loads(line)
            n += 1
            if rec['ok'] is False:
                mism += 1
                by.setdefault(rec['section'], 0)
                by[rec['section']] += 1
    return n, mism, by


def eq(computed, reported, tol=None):
    """数值比对; reported 为数则按其显示精度取容差(半个末位),否则给定 tol。"""
    if computed is None or reported is None:
        return computed is None and reported is None
    if isinstance(reported, bool) or isinstance(computed, bool):
        return computed == reported
    try:
        c = float(computed)
        rp = float(reported)
    except (TypeError, ValueError):
        return str(computed) == str(reported)
    if tol is None:
        s = repr(reported)
        if 'e' in s.lower():
            tol = 1e-9
        else:
            dec = len(s.split('.')[1]) if '.' in s else 0
            tol = 0.5 * (10 ** -dec) + 1e-9
    return abs(c - rp) <= tol
