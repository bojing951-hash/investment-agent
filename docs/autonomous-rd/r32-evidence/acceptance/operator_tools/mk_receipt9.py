#!/usr/bin/env python3
"""mk_receipt9.py [<replay_sha7>] — read-only.

Prints the acceptance-receipt facts of the five R32 work orders as markdown: execution stamp
(36499bb: plan / attach / independent review) and final stamp (cf33de3…: report / archive / replays on
the byte-identical carried run directories). Every value is read from files (run dirs named in
/tmp/r32-accept/env9.sh, the seat VERDICT files under /tmp/r32-accept/review6/<tag>_round<k>/, the
isolated archive packages /tmp/r32-accept/archive/r32v/, the stage receipts in /tmp/r32-accept/out
and, when <replay_sha7> is given, the re-download replay console logs under
/tmp/r32-accept/redl/<replay_sha7>/r32v_<session>/console.log). The verdict history of the superseded
stamps (review / review3 / review4 / review5) is listed per work order. Nothing is recomputed or typed
in; a missing artefact prints as «缺席».
"""
import glob
import hashlib
import json
import os
import re
import sys

SHA7 = sys.argv[1] if len(sys.argv) > 1 else ''
env = {}
for line in open('/tmp/r32-accept/env9.sh', encoding='utf-8'):
    line = line.strip()
    if line.startswith('export RD'):
        k, v = line[len('export '):].split('=', 1)
        env[k] = v.strip('"')
OUT = '/tmp/r32-accept/out'
SESSION = {'A': 'session_A_formal', 'B': 'session_B_formal', 'T3': 'session_T3_formal',
           'N30': 'session_NEW30', 'C4': 'session_C4_degraded'}
HISTORY = [('review', '预审(f722e3c 之前)'), ('review3', '19638e1'), ('review4', '0f3936d'), ('review5', '8f9055d')]
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


def stage_rc(tag, stage, letter):
    """newest stage receipt of a work order: (ts, rc) or (MISS, MISS)."""
    c = sorted(f for f in os.listdir(OUT) if re.match(r'%s%s_%s_\d{8}T\d{6}Z\.rc$' % (letter, re.escape(tag), stage), f))
    if not c:
        return MISS, MISS
    rc = open(os.path.join(OUT, c[-1]), encoding='utf-8').read().strip()
    return c[-1].split('_')[-1][:-3], rc[3:] if rc.startswith('rc=') else rc


def verdict_line(v, k):
    sev = {}
    for it in v.get('items') or []:
        sev[it.get('severity')] = sev.get(it.get('severity'), 0) + 1
    return 'r%s %s(%s 点/偏离 %s; MAJOR %s/MINOR %s/NIT %s)' % (
        k, v.get('verdict') or v.get('overall'), v.get('recompute_points'), v.get('recompute_mismatches'),
        sev.get('MAJOR', 0), sev.get('MINOR', 0), sev.get('NIT', 0))


def seg(t, start, ends):
    i = t.find(start)
    if i < 0:
        return ''
    j = [t.find(e, i + len(start)) for e in ends]
    j = [x for x in j if x >= 0]
    return t[i:(min(j) if j else len(t))]


def strict_facts(s):
    rc = re.search(r'^rc=(\d+)', s, re.M)
    summ = re.search(r'^ok=(\S+) \| blocked=(\S+) \| render_mode=(\S+) \| failed=(.*)$', s, re.M)
    failed = re.findall(r'^\s+FAILED (\S+) \| (.*)$', s, re.M)
    if not rc:
        return MISS
    return 'rc=%s%s%s' % (rc.group(1), '; %s' % summ.group(0) if summ else '',
                          ''.join('; 拒=%s(%s)' % (c, d.strip()[:90]) for c, d in failed))


def replay_facts(session):
    p = os.path.join('/tmp/r32-accept/redl', SHA7, 'r32v_' + session, 'console.log') if SHA7 else None
    if not p or not os.path.isfile(p):
        return MISS + '(重下回执未产出)'
    t = open(p, encoding='utf-8', errors='replace').read()
    head = re.search(r'downloaded HEAD=([0-9a-f]{40})', t)
    ident = re.findall(r'cloned commit: package files=(\d+) tree files=(\d+) \| blob-identical=(\d+)', t)
    nodo = re.search(r'changed paths outside docs/: (\d+)', t)
    kind = re.search(r'package kind=(\S+) map_binding_status_equivalent=(\d) → recording code = (\S+) stamp ([0-9a-f]+); '
                     r'the other stamp = (\S+) ([0-9a-f]+)', t)
    s3 = seg(t, '--- [3] strict replay on the final-commit engine', ['--- [3b]', '--- [4] six steps'])
    s3b = seg(t, '--- [3b]', ['--- [4] six steps'])
    s4 = seg(t, '--- [4] six steps', ['--- [5] strict replay'])
    s5 = seg(t, '--- [5] strict replay', ['--- [5b]', 'package after replays'])
    s5b = seg(t, '--- [5b]', ['package after replays'])
    rcs = re.findall(r'^rc=(\d+)', s4, re.M)
    steps = re.findall(r'map bytes: (IDENTICAL|DIFFER)', s4)
    untouched = 'package: UNTOUCHED' in s4
    refusals = re.findall(r'^rc=(\d+) \(期望≠0\)', s4, re.M)
    out = ('下载 HEAD=%s; 包文件对提交树逐字节一致 %s 件(重放前)/%s 件(重放后); 最终提交相对归档印章 docs/ 之外改动=%s 处; '
           '包类型=%s(map_binding_status_equivalent=%s; 录制代码=%s %s; 另一印章=%s %s); '
           '[3] 最终提交引擎: %s; [4] 录制代码引擎六步 rc 序列=%s(应拒三步 rc=%s); map bytes=%s; 源包 UNTOUCHED=%s; '
           '[5] 另一印章引擎: %s') % (
        head.group(1)[:7] if head else MISS, ident[0][2] if ident else MISS, ident[-1][2] if ident else MISS,
        nodo.group(1) if nodo else MISS,
        kind.group(1) if kind else MISS, kind.group(2) if kind else MISS,
        kind.group(3) if kind else MISS, kind.group(4)[:7] if kind else MISS,
        kind.group(5) if kind else MISS, kind.group(6)[:7] if kind else MISS,
        strict_facts(s3), '/'.join(rcs) or MISS, '/'.join(refusals) or MISS, '/'.join(x[0] for x in steps) or '-',
        '是' if untouched else '否', strict_facts(s5))
    if s3b:
        out += '; [3b] 最终提交引擎+--allow-code-mismatch(披露性越过;最终提交相对归档印章只多纯文档): %s' % strict_facts(s3b)
    if s5b:
        out += '; [5b] 归档印章引擎+--allow-code-mismatch(披露性越过,非录制代码): %s' % strict_facts(s5b)
    return out


print('| 工单 | 运行 SHA(执行印章) | 运行目录 | 冻结快照(sha16) | 日历/注册表(sha16) | 研判档(sha16) | 独立裁决(执行印章) | report(最终印章 cf33de3) | 归档(最终印章 cf33de3) |')
print('|---|---|---|---|---|---|---|---|---|')
details = []
for tag in ('A', 'B', 'T3', 'N30', 'C4'):
    rd = env.get('RDV_' + tag) or env['RDY_' + tag]
    rep = load(os.path.join(rd, 'report.json')) or {}
    run = rep.get('run') or {}
    fi = run.get('frozen_inputs') or {}
    snaps = sorted(k for k in fi if k.startswith('data/daily/'))
    snap = snaps[0] if snaps else MISS
    rounds = sorted(glob.glob('/tmp/r32-accept/review6/%s_round[0-9]*' % tag))
    verdicts = []
    for r in rounds:
        k = re.search(r'round(\d+)$', r).group(1)
        v = load(os.path.join(r, 'VERDICT-round%s.json' % k))
        verdicts.append(verdict_line(v, k) if v else 'r%s: 席位进行中(裁决文件未产出)' % k)
    if not verdicts:
        verdicts = ['第 1 轮: 席位进行中' if os.path.isdir('/tmp/r32-accept/review6/%s_round1' % tag) else MISS]
    arc = os.path.join('/tmp/r32-accept/archive/r32v', os.path.basename(rd))
    man = load(os.path.join(arc, 'ARCHIVE_MANIFEST.json'))
    a_ts, a_rc = stage_rc(tag, 'archive', 'V')
    if man:
        nfiles = sum(len(fns) for _, _, fns in os.walk(arc))
        arc_s = 'rc=%s@%s; %s; manifest %s; verdict=%s n=%s; %s 件; 清单 运行=`%s` 归档代码=`%s`' % (
            a_rc, a_ts, SESSION[tag], sha(os.path.join(arc, 'ARCHIVE_MANIFEST.json')), man.get('verdict'), man.get('verdicts_n'),
            nfiles, str(man.get('run_code_git_head'))[:7], str(man.get('archive_code_git_head') or MISS)[:7])
    else:
        blocked = ''
        c = sorted(f for f in os.listdir(OUT) if re.match(r'V%s_archive_\d{8}T\d{6}Z\.json$' % tag, f))
        if c:
            d = load(os.path.join(OUT, c[-1])) or {}
            dd = d.get('data') or {}
            blocked = 'blocked=%s' % (dd.get('blocked') or d.get('blocked') or '?')
        arc_s = 'rc=%s@%s; %s; 归档目录%s; %s' % (a_rc, a_ts, SESSION[tag], '不存在' if not os.path.isdir(arc) else '存在!', blocked)
    r_ts, r_rc = stage_rc(tag, 'report', 'V')
    at_ts, at_rc = stage_rc(tag, 'attach', 'Y')
    print('| %s | `%s` | `%s` | %s `%s` | `%s`/`%s` | `%s` | %s | rc=%s@%s | %s |' % (
        tag, (run.get('git_head') or MISS)[:7], os.path.basename(rd)[:16],
        os.path.basename(snap), fi.get(snap, MISS), str(fi.get('config/release_calendar.json', MISS))[:16],
        str(fi.get('config/metric_registry.json', MISS))[:16], sha(os.path.join(rd, 'agent_judgment.json')),
        '<br>'.join(verdicts), r_rc, r_ts, arc_s))
    hist = []
    for base, label in HISTORY:
        for r in sorted(glob.glob('/tmp/r32-accept/%s/%s_round[0-9]*' % (base, tag))):
            k = re.search(r'round(\d+)$', r).group(1)
            for vf in sorted(glob.glob(os.path.join(r, 'VERDICT-round%s*.json' % k))):
                v = load(vf)
                if v:
                    hist.append('%s %s%s' % (label, verdict_line(v, k), '' if os.path.basename(vf) == 'VERDICT-round%s.json' % k
                                             else ' [' + os.path.basename(vf)[len('VERDICT-round%s' % k):-5] + ']'))
    chain = '; '.join('%s=%s(%s)' % (str(v.get('overall') or v.get('verdict')), str(v.get('sha256'))[:12], str(v.get('file')).split('/')[-1])
                     for v in (man or {}).get('verdict_chain') or []) or MISS
    details.append('**%s** 运行 SHA(执行印章)=`%s`; 工单原文=`%s`; 快照=%s sha16=%s; 日历=%s 注册表=%s; 冻结聚合=%s; 裁决链=%s; '
                   '研判内容=%s; 地图内容(交付)=%s / (裁决绑定,执行印章)=%s; 挂接 rc=%s@%s(执行印章); 重下重放: %s' % (
        tag, run.get('git_head') or MISS, os.path.join(rd, 'question_verbatim.txt'), os.path.basename(snap), fi.get(snap, MISS),
        fi.get('config/release_calendar.json', MISS), fi.get('config/metric_registry.json', MISS),
        str((man or {}).get('frozen_inputs_sha256', MISS))[:16], chain, str((man or {}).get('content_sha256', MISS))[:16],
        str((man or {}).get('map_content_sha256', MISS))[:16], str((man or {}).get('map_report_sha256', MISS))[:16],
        at_rc, at_ts, replay_facts(SESSION[tag]) if tag != 'C4' else 'C4 无包(归档拒绝)=不适用'))
    details.append('- 被取代印章上的裁决史(%s): %s' % (tag, '; '.join(hist) or MISS))
print()
for d in details:
    print('- ' + d if not d.startswith('- ') else d)
