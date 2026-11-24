#!/usr/bin/python3 -I
"""xgen_cmp.py <redl_root> <sha7> [<sha7> ...] — compare the re-rendered maps of the seven replay steps
across re-download generations, package by package: strict / engine local calendar swapped / independent
engine dir with one calendar entry removed / repeat. For every
<redl_root>/<sha7>/{r32v,r31}_session_*/ the script reads the recording-code engine work root
(replay_recording_engine/<ts>/ or replay_runsha_engine/<ts>/), hashes out{0,1,1b,2}/MAP_REPLAY_RENDER.md
and compares it with the archived MAP_REPORT.md of the downloaded package (src/.../acceptance/<session>).
Read-only. Prints one block per package; exit 1 when any comparison fails or outputs are missing."""
import glob
import hashlib
import os
import re
import sys

STEPS = (('out0', 'strict'), ('out1', 'calendar-swapped'), ('out1b', 'engine-dir-minus-one-entry'),
         ('out2', 'repeat'))


def sha16(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16] if os.path.isfile(p) else None


bad = 0
for gen in sys.argv[2:]:
    root = os.path.join(sys.argv[1], gen)
    for d in sorted(glob.glob(os.path.join(root, 'r32v_session_*')) + glob.glob(os.path.join(root, 'r31_session_*'))):
        name = os.path.basename(d)
        session = name.split('_', 1)[1]
        fam = 'r31-evidence' if name.startswith('r31_') else 'r32-evidence'
        pkg = os.path.join(d, 'src', 'docs', 'autonomous-rd', fam, 'acceptance', session)
        line = ['%s/%s' % (gen, name)]
        if not os.path.isfile(os.path.join(pkg, 'ARCHIVE_MANIFEST.json')):
            line.append('  NO PACKAGE IN THE CLONE')
            bad += 1
            print('\n'.join(line))
            continue
        archived = sha16(os.path.join(pkg, 'MAP_REPORT.md'))
        line.append('  archived MAP_REPORT.md sha16=%s' % archived)
        works = sorted(glob.glob(os.path.join(d, 'replay_recording_engine', '2*'))
                       + glob.glob(os.path.join(d, 'replay_runsha_engine', '2*')))
        if not works:
            line.append('  no recording-engine work root (no replay outputs in this generation)')
            bad += 1
        for w in works:
            for sub, label in STEPS:
                h = sha16(os.path.join(w, sub, 'MAP_REPLAY_RENDER.md'))
                mode = None
                rep = os.path.join(w, sub, 'REPLAY_REPORT.json')
                if os.path.isfile(rep):
                    m = re.search(r'"render_mode"\s*:\s*"([a-z_]+)"',
                                  open(rep, encoding='utf-8', errors='replace').read())
                    mode = m.group(1) if m else None
                same = (h == archived) and h is not None
                if not same:
                    bad += 1
                line.append('  %s %-28s rendered sha16=%s render_mode=%s %s'
                            % (os.path.basename(w), label, h, mode, '== archived' if same else '!= archived'))
        print('\n'.join(line))
print('XGEN_RESULT: %s (mismatches=%d)' % ('ALL_RENDERED_MAPS_EQUAL_ARCHIVED' if not bad else 'MISMATCH', bad))
sys.exit(1 if bad else 0)
