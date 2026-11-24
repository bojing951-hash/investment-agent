#!/usr/bin/env python3
"""mk_receipt.py <review_rounds_dir> <replay_sha7> — read-only.

Prints the acceptance-receipt facts of the five R32 work orders as markdown,
every value read from files (run dirs named in /tmp/r32-accept/env5.sh, the seat
VERDICT files under <review_rounds_dir>/<tag>_round<k>/, the engine-tree verdict
docs, the isolated archive packages, the stage receipts in /tmp/r32-accept/out
and the re-download replay console logs under /tmp/r32-accept/redl/<replay_sha7>/).
Nothing is recomputed or typed in; a missing artefact prints as «缺席».
"""
import glob
import hashlib
import json
import os
import re
import sys

REV = sys.argv[1]
SHA7 = sys.argv[2] if len(sys.argv) > 2 else ''
env = {}
for line in open('/tmp/r32-accept/env5.sh', encoding='utf-8'):
    line = line.strip()
    if line.startswith('export RD_'):
        k, v = line[len('export '):].split('=', 1)
        env[k] = v.strip('"')
OUT = '/tmp/r32-accept/out'
SESSION = {'A': 'session_A_formal', 'B': 'session_B_formal', 'T3': 'session_T3_formal',
           'N30': 'session_NEW30', 'C4': 'session_C4_degraded'}
TREE = {'A': 'final5', 'B': 'final5', 'T3': 'final5', 'N30': 'final5', 'C4': 'final5-degraded'}
MISS = '«缺席»'


def sha(path, n=16):
    try:
        return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:n]
    except OSError:
        return MISS


def load(path):
    try:
        return json.load(open(path, encoding='utf-8'))
    except (OSError, ValueError):
        return None


def stage_rc(tag, stage):
    """newest stage receipt of a work order at stamp X: (ts, rc) or (MISS, MISS)."""
    c = sorted(f for f in os.listdir(OUT) if re.match(r'X%s_%s_\d{8}T\d{6}Z\.rc$' % (re.escape(tag), stage), f))
    if not c:
        return MISS, MISS
    rc = open(os.path.join(OUT, c[-1]), encoding='utf-8').read().strip()
    return c[-1].split('_')[-1][:-3], rc[3:] if rc.startswith('rc=') else rc


def replay_facts(session):
    p = os.path.join('/tmp/r32-accept/redl', SHA7, session, 'console.log') if SHA7 else None
    if not p or not os.path.isfile(p):
        return MISS
    t = open(p, encoding='utf-8', errors='replace').read()
    head = re.search(r'downloaded HEAD=([0-9a-f]{40})', t)
    ident = re.search(r'cloned commit: package files=(\d+) tree files=(\d+) \| blob-identical=(\d+)', t)
    steps = re.findall(r'map bytes: (IDENTICAL|DIFFER)', t)
    untouched = 'package: UNTOUCHED' in t
    rcs = re.findall(r'^rc=(\d+)', t, re.M)
    post = re.findall(r'^cloned commit: package files=\d+ tree files=\d+ \| blob-identical=(\d+)', t, re.M)
    vm = re.search(r'HEAD MISMATCH', t)
    return '下载 HEAD=%s; 包文件对提交树逐字节一致 %s(重放前)/%s(重放后); rc 序列=%s; map bytes=%s; 源包 UNTOUCHED=%s%s' % (
        head.group(1)[:7] if head else MISS, ident.group(3) if ident else MISS, post[-1] if post else MISS,
        '/'.join(rcs), '/'.join(steps) or '-', untouched, ' | HEAD MISMATCH' if vm else '')


print('| 工单 | 运行 SHA | 运行目录 | 冻结快照(sha16) | 日历/注册表(sha16) | 研判档(sha16) | 独立裁决 | report | 归档 |')
print('|---|---|---|---|---|---|---|---|---|')
details = []
for tag in ('A', 'B', 'T3', 'N30', 'C4'):
    rd = env['RD_' + tag]
    rep = load(os.path.join(rd, 'report.json')) or {}
    run = rep.get('run') or {}
    fi = run.get('frozen_inputs') or {}
    snap = sorted(k for k in fi if k.startswith('data/daily/'))[0] if any(k.startswith('data/daily/') for k in fi) else MISS
    rounds = sorted(glob.glob(os.path.join(REV, '%s_round[0-9]' % tag)))
    verdicts = []
    for r in rounds:
        k = re.search(r'round(\d+)$', r).group(1)
        v = load(os.path.join(r, 'VERDICT-round%s.json' % k))
        if not v:
            verdicts.append('r%s: 进行中' % k)
            continue
        sev = {}
        for it in v.get('items') or []:
            sev[it.get('severity')] = sev.get(it.get('severity'), 0) + 1
        verdicts.append('r%s %s(%s; %s 点/偏离 %s; MAJOR %s/MINOR %s/NIT %s)' % (
            k, v.get('verdict'), (v.get('reviewer') or '').replace('independent-zero-context-seat-r32-', ''),
            v.get('recompute_points'), v.get('recompute_mismatches'), sev.get('MAJOR', 0), sev.get('MINOR', 0), sev.get('NIT', 0)))
    if not verdicts:
        verdicts = [MISS]
    arc = os.path.join('/tmp/r32-accept/archive/r32', os.path.basename(rd))
    man = load(os.path.join(arc, 'ARCHIVE_MANIFEST.json'))
    a_ts, a_rc = stage_rc(tag, 'archive')
    if man:
        nfiles = sum(len(fns) for _, _, fns in os.walk(arc))
        arc_s = 'rc=%s@%s; %s; manifest %s; verdict=%s n=%s; %s 件' % (
            a_rc, a_ts, SESSION[tag], sha(os.path.join(arc, 'ARCHIVE_MANIFEST.json')), man.get('verdict'), man.get('verdicts_n'), nfiles)
    else:
        blocked = ''
        for f in sorted(f for f in os.listdir(OUT) if re.match(r'X%s_archive_\d{8}T\d{6}Z\.json$' % tag, f))[-1:]:
            d = load(os.path.join(OUT, f)) or {}
            dd = d.get('data') or {}
            blocked = 'blocked=%s' % (dd.get('blocked') or d.get('blocked') or '?')
        arc_s = 'rc=%s@%s; %s; 归档目录%s; %s' % (a_rc, a_ts, SESSION[tag], '不存在' if not os.path.isdir(arc) else '存在!', blocked)
    r_ts, r_rc = stage_rc(tag, 'report')
    print('| %s | `%s` | `%s` | %s `%s` | `%s`/`%s` | `%s` | %s | rc=%s@%s | %s |' % (
        tag, (run.get('git_head') or MISS)[:7], os.path.basename(rd)[:16],
        os.path.basename(snap), fi.get(snap, MISS), str(fi.get('config/release_calendar.json', MISS))[:16],
        str(fi.get('config/metric_registry.json', MISS))[:16], sha(os.path.join(rd, 'agent_judgment.json')),
        '<br>'.join(verdicts), r_rc, r_ts, arc_s))
    chain = '; '.join('%s=%s(%s)' % (str(v.get('overall') or v.get('verdict')), str(v.get('sha256'))[:12], str(v.get('file')).split('/')[-1])
                     for v in (man or {}).get('verdict_chain') or []) or MISS
    details.append('**%s** 运行 SHA=`%s`; 工单原文=`%s`; 快照=%s sha16=%s; 日历=%s 注册表=%s; 冻结聚合=%s; 裁决链=%s; 研判内容=%s; 地图内容=%s; 重放: %s' % (
        tag, run.get('git_head') or MISS, os.path.join(rd, 'question_verbatim.txt'), os.path.basename(snap), fi.get(snap, MISS),
        fi.get('config/release_calendar.json', MISS), fi.get('config/metric_registry.json', MISS),
        str((man or {}).get('frozen_inputs_sha256', MISS))[:16], chain, str((man or {}).get('content_sha256', MISS))[:16],
        str((man or {}).get('map_content_sha256', MISS))[:16], replay_facts(SESSION[tag]) if tag != 'C4' else 'C4 无包(归档拒绝)=不适用'))
print()
for d in details:
    print('- ' + d)
