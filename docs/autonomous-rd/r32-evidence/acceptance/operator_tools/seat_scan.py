#!/usr/bin/env python3
"""seat_scan.py <seat_round_dir> [...] — read-only pre-registration check of a seat's outputs.

Scans every text file directly under each seat round directory (PROSE-*.md, VERDICT-*.json)
for model-vendor names (Latin literal, case-insensitive; Chinese short names), key-shaped
strings and the private home root, and prints the verdict word / reviewer / points summary.
Exit 1 if a vendor name or a key-shaped string is found (the verdict must then be handled
by the operator rule: never altered — exclude-with-listing or re-seat).
"""
import json
import os
import re
import sys

VENDOR = 'g' + 'lm'
VENDOR_CN = ['〖厂商名〗', '〖厂商名〗', '〖厂商名〗', '〖厂商名〗', '〖厂商名〗', '〖厂商名〗', '阶梯']
KEYISH = re.compile(r'(?i)(api[_-]?key|secret|token|password|bearer)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{12,}')
bad = 0
for d in sys.argv[1:]:
    print('==', d)
    for fn in sorted(os.listdir(d)):
        p = os.path.join(d, fn)
        if not os.path.isfile(p) or os.path.getsize(p) > 5_000_000:
            continue
        if not (fn.startswith('VERDICT-') or fn.startswith('PROSE-')):
            continue
        raw = open(p, 'rb').read()
        txt = raw.decode('utf-8', errors='replace')
        low = txt.lower()
        hits = []
        if VENDOR in low:
            for m in re.finditer(re.escape(VENDOR), low):
                hits.append('vendor-literal: …%s…' % txt[max(0, m.start() - 25):m.end() + 25].replace('\n', ' '))
        for w in VENDOR_CN:
            for m in re.finditer(re.escape(w), txt):
                hits.append('vendor-cn[%s]: …%s…' % (w, txt[max(0, m.start() - 25):m.end() + 25].replace('\n', ' ')))
        for m in KEYISH.finditer(txt):
            hits.append('key-shaped: %s' % m.group(0)[:40])
        if '/Users/' in txt:
            hits.append('private-root: /Users/ (rewritten to ~ by the evidence collector; informational)')
        print('  %s (%d bytes) hits=%d' % (fn, len(raw), len(hits)))
        for h in hits[:12]:
            print('     ', h)
        bad += sum(1 for h in hits if not h.startswith('private-root'))
        if fn.startswith('VERDICT-'):
            try:
                v = json.loads(txt)
            except ValueError as e:
                print('      JSON INVALID:', e)
                bad += 1
                continue
            sev = {}
            for it in v.get('items') or []:
                sev[it.get('severity')] = sev.get(it.get('severity'), 0) + 1
            print('      verdict=%s overall=%s reviewer=%s points=%s mismatches=%s items=%s must_fix=%d audited_at=%s' % (
                v.get('verdict'), v.get('overall'), v.get('reviewer'), v.get('recompute_points'),
                v.get('recompute_mismatches'), sev, len(v.get('must_fix') or []), v.get('audited_at')))
print('RESULT:', 'clean' if bad == 0 else '%d hit(s)' % bad)
sys.exit(1 if bad else 0)
