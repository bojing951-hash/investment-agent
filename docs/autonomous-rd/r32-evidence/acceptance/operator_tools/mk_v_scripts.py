#!/usr/bin/python3 -I
"""mk_v_scripts.py <V sha40> — generate the final-stamp (V) operator scripts from their W-stage
counterparts by explicit, counted text replacements (every replacement must hit the expected
number of times; otherwise the script aborts before writing anything). Read-only on the W scripts;
writes the V scripts next to them. Pure text generation: no engine code is touched."""
import os
import sys

V40 = sys.argv[1]
assert len(V40) == 40 and all(c in '0123456789abcdef' for c in V40), V40
V7 = V40[:7]
S = '/tmp/r32-accept/scripts'
plan = {}


def rep(src, pairs):
    out = src
    for old, new, n in pairs:
        c = out.count(old)
        if c != n:
            sys.exit('ABORT: %r found %d times (expected %d)' % (old, c, n))
        out = out.replace(old, new)
    return out


def head_rest(src, marker='set -u\n'):
    i = src.index(marker)
    return src[:i], src[i:]


def rd(name):
    return open(os.path.join(S, name), encoding='utf-8').read()


# ── build_final9.sh ──────────────────────────────────────────────────────────
s = rd('build_final8.sh')
i = s.index('# Acceptance trees at the consolidated-fix SHA')
plan['build_final9.sh'] = (
    '#!/bin/zsh\n'
    '# build_final9.sh <sha> <base|degraded|aug|entry>\n'
    '# (from build_final8.sh, at the final stamp V after the third delivery-chain fix: replay gate 4 accepts\n'
    '#  the archiving code for every re-delivery package whose manifest declares archive_code_git_head — also\n'
    '#  when the map was rendered with the verdict already bound (same-render two-stamp package, no\n'
    '#  map_binding_status_equivalent key); no rendering change. The Y (36499bb) run directories and verdict\n'
    '#  records are carried in byte-identical by scripts/carry_yz.py; report/archive/replays are re-run here.)\n'
    + rep(s[i:], [('build_final8.sh', 'build_final9.sh', 1), ('final8', 'final9', 8)]))

# ── env9.sh ──────────────────────────────────────────────────────────────────
env8 = open('/tmp/r32-accept/env8.sh', encoding='utf-8').read()
plan['env9.sh'] = (
    '# final9* = clean install at the final stamp V (%s; scripts/build_final9.sh). The Y (36499bb) run directories and\n'
    '#           verdict records are carried in byte-identical (scripts/carry_yz.py; listings out/carry_yz_*_V.txt);\n'
    '#           report/archive/replays are re-run at V (scripts/v_deliver.sh, v_replay.sh). RDV_<tag> = carried run\n'
    '#           directory in the final9* tree; RDY_<tag> = the same run directory at the execution stamp Y (final6*).\n'
    % V40
    + ''.join(l.replace('RDW_', 'RDV_').replace('final8', 'final9') for l in env8.splitlines(True)
              if l.startswith('export RDW_'))
    + ''.join(l for l in env8.splitlines(True) if l.startswith('export RDY_')))

# ── v_deliver.sh ─────────────────────────────────────────────────────────────
s = rd('w_deliver.sh')
h, rest = head_rest(s)
plan['v_deliver.sh'] = (
    '#!/bin/zsh\n'
    '# v_deliver.sh <tag> — re-deliver one carried work order at the final stamp (V):\n'
    '#   1. keep the carried MAP_REPORT.md bytes (execution stamp Y) -> out/vmap_<tag>_pre.md\n'
    '#   2. report   (review-status surface refreshed when the verdict is approved)\n'
    '#   3. diff Y bytes vs delivered (zmapdiff.py)                  -> out/vmapdiff_<tag>.txt\n'
    '#   4. archive  -> /tmp/r32-accept/archive/r32v/<run id>  (a draft must be refused: no directory)\n'
    '# Usage: zsh v_deliver.sh T3\n'
    + rep(rest, [
        ('source /tmp/r32-accept/env8.sh\n', 'source /tmp/r32-accept/env9.sh\n', 1),
        ('RDW_', 'RDV_', 1), ('final8', 'final9', 3),
        ('wmap_', 'vmap_', 1), ('wmapdiff_', 'vmapdiff_', 3),
        ('"W$TAG"', '"V$TAG"', 2),
        ('$O/W${TAG}_report_', '$O/V${TAG}_report_', 1),
        ('$O/W${TAG}_archive_', '$O/V${TAG}_archive_', 1),
        ('archive/r32w', 'archive/r32v', 1),
        ('w_deliver $TAG', 'v_deliver $TAG', 1)]))

# ── v_replay.sh ──────────────────────────────────────────────────────────────
s = rd('w_replay.sh')
h, rest = head_rest(s)
plan['v_replay.sh'] = (
    '#!/bin/zsh\n'
    '# v_replay.sh <tag> — replays of the final-stamp (V) re-delivered package of one work order\n'
    '# (/tmp/r32-accept/archive/r32v/<run id>), each into a fresh replay-out directory:\n'
    '#   [1] V engine (the package\'s archiving code), strict\n'
    '#       (expected: status-equivalent packages rc=0, byte_equal, all checks — gate 4 accepts the declared\n'
    '#        archiving code; same-render packages (the map was rendered at the execution stamp with the\n'
    '#        verdict already bound, e.g. B): refused, gate 4 code_version_mismatch — the archiving code is\n'
    '#        not the recording code; the delivered bytes are the execution-stamp rendering)\n'
    '#   [2] Y engine (the package\'s run SHA = the execution stamp), strict\n'
    '#       (status-equivalent packages: refused, verdict_binding_threeway — the execution-stamp code\n'
    '#        predates the status-equivalence handling; same-render packages: rc=0 byte_equal)\n'
    '#   [1b] with the argument `override`: V engine + --allow-code-mismatch (same-render packages: rc=0 with the\n'
    '#       override disclosed; the replay report says so and does not claim a declared status equivalence)\n'
    '# Receipts: out/vreplay_<tag>_{Vstrict,Ystrict[,Voverride]}.{json,err,rc}; outputs out/vreplay_<tag>_<name>_out/\n'
    + rep(rest, [
        ('source /tmp/r32-accept/env8.sh\n', 'source /tmp/r32-accept/env9.sh\n', 1),
        ('RDW_', 'RDV_', 1), ('final8', 'final9', 3),
        ('archive/r32w', 'archive/r32v', 1),
        ('for spec in "Wstrict:$W:" "Ystrict:$Y:"; do\n',
         'specs=("Vstrict:$W:" "Ystrict:$Y:")\n'
         '[ "${2:-}" = override ] && specs+=("Voverride:$W:--allow-code-mismatch")\n'
         'for spec in $specs; do\n', 1),
        ('wreplay_${TAG}_Wstrict.rc', 'vreplay_${TAG}_Vstrict.rc', 1),
        ('Wstrict_rc=', 'Vstrict_rc=', 1),
        ('wreplay_${TAG}', 'vreplay_${TAG}', 9),
        ('w_replay $TAG', 'v_replay $TAG', 1)]))

# ── plan_v.sh ────────────────────────────────────────────────────────────────
s = rd('plan_w.sh')
i = s.index('S=/tmp/r32-accept/scripts\n')
plan['plan_v.sh'] = (
    '#!/bin/zsh\n'
    '# plan_v.sh — re-plan the five R32 work orders at the final stamp V (%s; trees final9 / final9-degraded)\n'
    '# for the cross-stamp engine-face comparison Y (36499bb) -> V. AUG is re-planned by v_stage.sh in final9-aug.\n'
    '# Plan stage only (no judgment, no archive); new run directories next to the byte-identical carried Y run\n'
    '# directories (never touching them). Receipts out/VPLAN-<tag>_plan_<ts>.*; logs out/plan_v_*.launcher.log.\n'
    '# Two trees in parallel.\n' % V40
    + rep(s[i:], [('final8', 'final9', 4), ('WPLAN-', 'VPLAN-', 2), ('plan_w_', 'plan_v_', 3),
                  ('plan_w done', 'plan_v done', 1)]))

# ── cmp_v_all.sh ─────────────────────────────────────────────────────────────
s = rd('cmp_w_all.sh')
h, rest = head_rest(s, 'S=/tmp/r32-accept/scripts; O=/tmp/r32-accept/out\n')
plan['cmp_v_all.sh'] = (
    '#!/bin/zsh\n'
    '# cmp_v_all.sh — key-by-key comparison of the engine deterministic face of every work order between\n'
    '# the execution stamp Y (36499bb; final6* run dirs = env9.sh RDY_*) and the final stamp V (%s: the\n'
    '# same questions re-planned in the final9* trees by plan_v.sh / v_stage.sh; plan-only runs).\n'
    '# Read-only on the run directories; writes out/cmp_V_<tag>.txt + .console, cmp_V_condensed.txt, cmp_V_summary.txt.\n' % V40
    + rep(rest, [
        ('source /tmp/r32-accept/env8.sh', 'source /tmp/r32-accept/env9.sh', 1),
        ('final8', 'final9', 3), ('cmp W ', 'cmp V ', 2),
        ('-> W (24141c01…, plan-only re-plan)', '-> V (%s…, plan-only re-plan)' % V7, 1),
        ('cmp_W_', 'cmp_V_', 9), ('cmp_w_summary.py', 'cmp_v_summary.py', 1)]))

# ── cmp_v_summary.py ─────────────────────────────────────────────────────────
s = rd('cmp_w_summary.py')
plan['cmp_v_summary.py'] = rep(s, [
    ('cmp_w_summary', 'cmp_v_summary', 1), ('cmp_W_', 'cmp_V_', 6),
    ('stamp Y -> stamp W)', 'stamp Y -> stamp V)', 1),
    ('stamp Y 36499bb -> stamp W 24141c01a73daa44e56e380320f46bb0f7cbd723', 'stamp Y 36499bb -> stamp V ' + V40, 1),
    ('the W re-plan is plan-only', 'the V re-plan is plan-only', 1),
    ('the W re-plan runs are plan-only', 'the V re-plan runs are plan-only', 1),
    ('the two post-Y commits only', 'the post-Y commits only', 1)])

# ── doctor_v.sh ──────────────────────────────────────────────────────────────
s = rd('doctor_w.sh')
plan['doctor_v.sh'] = rep(s, [('doctor_w.sh', 'doctor_v.sh', 1), ('final8-entry', 'final9-entry', 3),
                              ('F8ENTRY', 'F9ENTRY', 6)])

# ── entry_smoke_v.sh ─────────────────────────────────────────────────────────
s = rd('entry_smoke_w.sh')
plan['entry_smoke_v.sh'] = rep(s, [
    ('entry_smoke_w.sh', 'entry_smoke_v.sh', 1), ('印章 W = 24141c0', '印章 V = ' + V7, 1),
    ('final8-entry', 'final9-entry', 2), ('WENTRY', 'VENTRY', 1), ('F8ENTRY', 'F9ENTRY', 1),
    ('ESMOKE-W', 'ESMOKE-V', 2), ('doctor_w.sh', 'doctor_v.sh', 1)])

# ── cmp_attached_v.py ────────────────────────────────────────────────────────
s = rd('cmp_attached_w.py')
plan['cmp_attached_v.py'] = rep(s, [
    ('cmp_attached_w.py', 'cmp_attached_v.py', 1), ('final-stamp (W) tree', 'final-stamp (V) tree', 1),
    ('cmp_attached_W.txt', 'cmp_attached_V.txt', 2),
    ("'/tmp/r32-accept/env8.sh'", "'/tmp/r32-accept/env9.sh'", 1),
    ('RDW_', 'RDV_', 2),
    ('byte-equal to W tree', 'byte-equal to V tree', 1),
    ('W tree', 'V tree', 3)])

def dest(name):
    # env9.sh lives next to env8.sh (top level); the scripts in scripts/
    return os.path.join(S if name.endswith(('.sh', '.py')) and name != 'env9.sh'
                        else os.path.dirname(S), name)


for name, text in plan.items():
    if os.path.exists(dest(name)):
        sys.exit('ABORT: %s already exists (not overwritten)' % name)
for name, text in plan.items():
    open(dest(name), 'w', encoding='utf-8').write(text)
    print('written %s (%d lines)' % (name, text.count('\n')))
