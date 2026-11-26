#!/usr/bin/env python3
"""ev_collect.py <section> [...]  — Audit-R32 evidence pack builder.

Copies acceptance artefacts from the operator's out-of-repo work area into
docs/autonomous-rd/r32-evidence/acceptance/ of the PR worktree.

  wave0      battery receipt (summary only; raw logs stay outside), CI receipts,
             clean-install + standard-update-entry receipts, baseline reproduction
  engine_fix the T3 official-record defect: reproduction before/after, gate red/green,
             patch, commit message
  aug        AUG re-verification runs at the final stamp + late-evidence count
  superseded formal-entry artefacts of the superseded stamp 19638e1
  session X  final package of work order X (byte-exact) + seat log + verdicts
  reviews    review-seat protocols and outputs (text artefacts; bulky dumps listed only)

Text artefacts get the private home root rewritten to `~` (public-repo rule of
the R31 pack). Archive packages are copied byte-exact (their manifest binds
the bytes). Every section ends with the key scan: the LIVE data keys are read
in-process (never printed) and must occur in no evidence file.
"""
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

HOME_ROOT = '~'
OUT = '/tmp/r32-accept/out'
REPO = '~/investment-agent-product'
EV = os.path.join(REPO, 'docs/autonomous-rd/r32-evidence/acceptance')
LIVE_ENV = '~/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent/env_config.py'
VENDOR = 'g' + 'lm'     # a model-vendor name the user barred from anything public (assembled, not written)


def secrets():
    """LIVE data keys, in memory only."""
    spec = importlib.util.spec_from_file_location('live_env_config_scan', LIVE_ENV)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    out = {}
    for k, v in vars(m).items():
        if k.startswith('__'):
            continue
        if isinstance(v, str) and len(v) >= 16 and re.search(r'KEY|TOKEN|SECRET|PASSWORD', k, re.I):
            out[k] = v
    return out


def load_env():
    env = {}
    for line in open('/tmp/r32-accept/env4.sh', encoding='utf-8'):
        line = line.strip()
        if line.startswith('export RD_'):
            k, v = line[len('export '):].split('=', 1)
            env[k] = v.strip('"')
    return env


def write_text(dst, text):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    n = text.count(HOME_ROOT)
    text = text.replace(HOME_ROOT, '~')
    with open(dst, 'w', encoding='utf-8') as fh:
        fh.write(text)
    return n


def copy_text(src, dst):
    raw = open(src, 'rb').read()
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        return -1
    return write_text(dst, text)


def copy_exact(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
    return hashlib.sha256(open(src, 'rb').read()).hexdigest()


def newest(pattern):
    c = sorted(f for f in os.listdir(OUT) if re.match(pattern, f))
    if not c:
        raise SystemExit('no file for %s' % pattern)
    return os.path.join(OUT, c[-1])


def newest_rc0(pattern):
    """newest envelope of a stage whose .rc file reads rc=0 (a stage that succeeded)."""
    for f in reversed(sorted(f for f in os.listdir(OUT) if re.match(pattern, f))):
        rc = os.path.join(OUT, f[:-5] + '.rc')
        if os.path.exists(rc) and open(rc, encoding='utf-8').read().strip() == 'rc=0':
            return os.path.join(OUT, f)
    raise SystemExit('no rc=0 envelope for %s' % pattern)


def scan(root, label):
    secs = secrets()
    hits, vend, priv, nfiles = [], [], [], 0
    for dp, _, fns in os.walk(root):
        for fn in fns:
            p = os.path.join(dp, fn)
            nfiles += 1
            raw = open(p, 'rb').read()
            for k, v in secs.items():
                if v.encode() in raw:
                    hits.append((p, k))
            low = raw.lower()
            if VENDOR.encode() in low:
                vend.append(p)
            if HOME_ROOT.encode() in raw:
                priv.append(p)
    print('[scan %s] files=%d key_hits=%d vendor_literal_files=%d private_root_files=%d'
          % (label, nfiles, len(hits), len(vend), len(priv)))
    for p in hits:
        print('   KEY HIT:', p)
    for p in vend[:10]:
        print('   vendor literal:', os.path.relpath(p, REPO))
    for p in priv[:10]:
        print('   private root:', os.path.relpath(p, REPO))
    return len(hits) == 0


def battery_receipt(tag):
    src = os.path.join(OUT, 'battery_' + tag, 'summary.tsv')
    # summary lines were cut at 120 bytes by the runner: decode leniently
    rows = [l.rstrip('\n').split('\t') for l in open(src, encoding='utf-8', errors='replace') if l.strip()]
    tsv = open(src, encoding='utf-8', errors='replace').read()
    ok = [r for r in rows if r[0] == 'PASS']
    bad = [r for r in rows if r[0] != 'PASS']
    text = ['# Audit-R32 离线电池回执 @ %s' % tag, '',
            '- 口径: tests/test_*.py 逐件 `python3 tests/<file>`,绿 = rc ∈ {0, 5}(与 battery.sh 一致)',
            '- 结果: files=%d pass=%d fail=%d' % (len(rows), len(ok), len(bad)),
            '- 逐件清单见同目录 battery_%s_summary.tsv(状态 / rc / 文件 / 末行摘要);原始日志留在仓外' % tag, '']
    if bad:
        text.append('- 红件: %s' % ', '.join(r[2] for r in bad))
    write_text(os.path.join(EV, 'wave0_r32', 'battery_%s_receipt.md' % tag), '\n'.join(text) + '\n')
    # status / rc / file only: the runner's cut-at-120-bytes tail column is not
    # evidence (and test banners print names this pack keeps out of public text)
    tsv3 = '\n'.join('\t'.join(r[:3]) for r in rows) + '\n'
    write_text(os.path.join(EV, 'wave0_r32', 'battery_%s_summary.tsv' % tag), tsv3)
    print('battery', tag, len(rows), len(ok), len(bad))


def section_wave0():
    battery_receipt('0f3936d')
    for f in ['ci_runs_branch_r32.txt', 'ci_jobs_all_stamps.txt', 'ci_jobs_45248512128.txt']:
        copy_text(os.path.join(OUT, f), os.path.join(EV, 'wave0_r32', f))
    inst = os.path.join(EV, 'wave0_r32', 'clean_install_update_entry')
    for f in ['build_final4_base.log', 'build_final4_degraded.log', 'build_final4_aug.log', 'build_final4_entry.log',
              'final4_base_skill_install.json', 'final4_entry_skill_install.json',
              'F4ENTRY_update_20261123T192713Z.json', 'F4ENTRY_update_20261123T192713Z.err',
              'F4ENTRY_update_20261123T192713Z.meta',
              'build_final3.log', 'build_final3_aug.log', 'build_final3_degraded.log',
              'final3_aug_skill_install.json', 'final3_degraded_skill_install.json',
              'update_final3.json', 'update_final3.err', 'update_final3.meta']:
        p = os.path.join(OUT, f)
        if os.path.exists(p):
            copy_text(p, os.path.join(inst, f))
        else:
            print('missing', f)
    base = os.path.join(EV, 'wave0_r32', 'baseline_reproduction_72dab1c')
    R = '/tmp/r32-accept/repro'
    # baseline stamp 72dab1c: the AUG question re-planned in a clean baseline tree
    # (run 20261123T063810Z) and the independent audit's own exhibit (the R31
    # archived AUG report). count_late on both: L1 31/31 late, evidence 56/56 late.
    for f in ['aug_plan_20261123T063800Z.json', 'aug_plan_20261123T063800Z.err', 'R31_aug_report.json',
              'question_aug.txt', os.path.join('task2', 'repro_baseline_72dab1c.txt'),
              os.path.join('task2', 'repro_fixed_5b37e73.txt'),
              os.path.join('gold_dual', 'repro_baseline.txt'), os.path.join('gold_dual', 'repro_baseline_real.txt')]:
        src = os.path.join(R, f)
        if os.path.exists(src):
            copy_text(src, os.path.join(base, os.path.basename(f)))
        else:
            print('missing', src)
    copy_text(os.path.join(R, 'tree', 'CODE_VERSION.json'), os.path.join(base, 'baseline_tree_CODE_VERSION.json'))
    copy_text('/tmp/r32-accept/scripts/count_late.py', os.path.join(EV, 'wave0_r32', 'count_late.py'))
    copy_text('/tmp/r32-accept/scripts/battery.sh', os.path.join(EV, 'wave0_r32', 'battery.sh'))
    # first fix stamp 5b37e73: same question, late evidence gone (L1 31/0, evidence 55/0)
    a1 = os.path.join(EV, 'wave0_r32', 'after_first_fix_5b37e73')
    for stem in ['AUG_plan_20261123T102851Z.json', 'AUG_plan_20261123T102851Z.err', 'AUG_plan_20261123T102851Z.rc',
                 'AUG_steps_late_20261123T102851Z.txt']:
        copy_text(os.path.join(OUT, stem), os.path.join(a1, stem))
    scan(os.path.join(EV, 'wave0_r32'), 'wave0')


def section_engine_fix():
    d = os.path.join(EV, 'engine_fix_official_record')
    for f in ['probe_opr_fix_old.txt', 'probe_opr_fix_new.txt', 'probe_opr_T3.txt',
              'gate_sec_b_prefix_red.txt', 'gate_sec_b_new.txt', 'precommit_gates.txt',
              'fix_opr_planner.patch']:
        p = os.path.join(OUT, f)
        if os.path.exists(p):
            copy_text(p, os.path.join(d, f))
        else:
            print('missing', f)
    msg = subprocess.run(['git', '-C', REPO, 'log', '-1', '--format=%H%n%ad%n%B', '--date=iso', '0f3936d'],
                         capture_output=True, text=True).stdout
    write_text(os.path.join(d, 'commit_0f3936d_message.txt'), msg)
    probe_src = '/tmp/r32-accept/scripts/probe_opr_fix.py'
    copy_text(probe_src, os.path.join(d, 'probe_opr_fix.py'))
    scan(d, 'engine_fix')


def section_aug():
    d = os.path.join(EV, 'aug_plan')
    for i, tag in enumerate(['F4AUG', 'F4AUG2', 'F4AUG3'], 1):
        for ext in ('json', 'err', 'rc'):
            src = newest('%s_plan_.*\\.%s$' % (tag, ext))
            copy_text(src, os.path.join(d, 'run%d_%s' % (i, os.path.basename(src)[len(tag + '_'):])))
    copy_text(os.path.join(OUT, 'count_late_F4AUG3_0f3936d.txt'), os.path.join(d, 'count_late_run3.txt'))
    # run map (envelope file -> engine run ts -> run_ok -> not-ok steps) and extracts
    import glob
    runs = sorted(glob.glob('/tmp/r32-accept/final4-aug/output/research_runs/20261123T19*_以_2026_08_21_*'))
    lines = ['# AUG re-verification at the final stamp: envelope -> run (read-only extract)', '',
             '# envelope file name              engine run ts        run_ok  not-ok steps']
    keep = {}
    for i, r in enumerate(runs, 1):
        rep = json.load(open(os.path.join(r, 'report.json'), encoding='utf-8'))
        run = rep.get('run') or {}
        bad = []
        for s in rep.get('steps') or []:
            if isinstance(s, dict) and s.get('ok') is not True:
                env = s.get('envelope') or {}
                bad.append('%s: error=%s' % (s.get('step'), json.dumps(env.get('error'), ensure_ascii=False)))
        env_name = ['F4AUG_plan_20261123T193254Z.json', 'F4AUG2_plan_20261123T193347Z.json',
                    'F4AUG3_plan_20261123T193529Z.json'][i - 1]
        lines.append('%-32s %s  %-5s   %s' % (env_name, os.path.basename(r)[:16], run.get('run_ok', rep.get('run_ok')), bad or '-'))
        keep[i] = (r, rep, bad)
    write_text(os.path.join(d, 'run_map.txt'), '\n'.join(lines) + '\n')
    r3, rep3, _ = keep[3]
    assert os.path.basename(r3)[:16] == '20261123T193622Z'
    copy_text(os.path.join(r3, 'report.md'), os.path.join(d, 'run3_report.md'))
    copy_text(os.path.join(r3, 'evidence_index.json'), os.path.join(d, 'run3_evidence_index.json'))
    rp3 = rep3.get('research_plan') or {}
    gate = {'run_evidence_gate': (rep3.get('run') or {}).get('evidence_gate'),
            'research_plan_cutoff': rp3.get('cutoff'),
            'as_of_declared': rp3.get('as_of_declared'),
            'frozen_inputs': (rep3.get('run') or {}).get('frozen_inputs'),
            'git_head': (rep3.get('run') or {}).get('git_head'),
            'ts_utc': (rep3.get('run') or {}).get('ts_utc')}
    write_text(os.path.join(d, 'run3_evidence_gate.json'), json.dumps(gate, ensure_ascii=False, indent=1) + '\n')
    scan(d, 'aug')


def section_superseded():
    d = os.path.join(EV, 'superseded_19638e1')
    for tag in ['F3A', 'F3B', 'F3T3', 'F3N30', 'F3C4']:
        for stage in ('attach', 'report'):
            for ext in ('json', 'rc'):
                src = newest('%s_%s_.*\\.%s$' % (tag, stage, ext))
                copy_text(src, os.path.join(d, os.path.basename(src)))
    scan(d, 'superseded')


SESSION_NAME = {'A': 'session_A_formal', 'B': 'session_B_formal', 'T3': 'session_T3_formal',
                'N30': 'session_NEW30', 'C4': 'session_C4_degraded'}
RUN_FILES = ['report.json', 'agent_judgment.json', 'MAP_REPORT.md', 'MAP_REPORT.sha256', 'FULL_REPORT.md',
             'report.md', 'evidence_index.json', 'views_digest.json', 'AGENT_SEAT_ENVELOPE.json',
             'question_verbatim.txt']


def section_session(tag):
    """Final package of one work order. Archived work orders: the whole isolated
    archive directory byte-exact (manifest binds the bytes). C4 (refused): the
    run's top-level files + the refusal payload."""
    env = load_env()
    rd = env['RD_' + tag]
    dst = os.path.join(EV, SESSION_NAME[tag])
    run_id = os.path.basename(rd)[:16]
    if tag == 'C4':
        for fn in RUN_FILES + ['root_overlay/config/release_calendar.json', 'root_overlay/config/metric_registry.json']:
            copy_exact(os.path.join(rd, fn), os.path.join(dst, fn))
        src = newest('F4C4_archive_.*\\.json$')
        copy_text(src, os.path.join(dst, 'archive_refusal_payload.json'))
        copy_text(newest('F4C4_report_.*\\.json$'), os.path.join(dst, 'report_stage_receipt.json'))
    else:
        arc = os.path.join('/tmp/r32-accept/archive/r32', os.path.basename(rd))
        n = 0
        for dp, _, fns in os.walk(arc):
            for fn in fns:
                p = os.path.join(dp, fn)
                copy_exact(p, os.path.join(dst, os.path.relpath(p, arc)))
                n += 1
        print('package files', n)
        # stage receipts are operator envelopes (not manifest-bound): newest successful run
        copy_text(newest('F4%s_archive_.*\\.json$' % tag), os.path.join(dst, 'archive_receipt.json'))
        copy_text(newest_rc0('F4%s_report_.*\\.json$' % tag), os.path.join(dst, 'report_stage_receipt.json'))
        copy_text(newest('F4%s_attach_.*\\.json$' % tag), os.path.join(dst, 'attach_receipt.json'))
    # formal-entry ledger lines of this work order (all stamps and rounds)
    rtag = {'A': 'A', 'B': 'B', 'T3': 'T3', 'N30': 'N30', 'C4': 'C4'}[tag]
    lines = [l for l in open('/tmp/r32-accept/seat_operator.log', encoding='utf-8', errors='replace')
             if re.search(r'tag=F\d+%s( |$)' % rtag, l) or run_id in l]
    write_text(os.path.join(dst, 'seat_%s.log' % rtag), ''.join(lines))
    scan(dst, 'session ' + tag)


def section_reviews():
    d = os.path.join(EV, 'reviews')
    for base, label in [('/tmp/r32-accept/review4', ''), ('/tmp/r32-accept/review3', 'superseded_19638e1_'),
                        ('/tmp/r32-accept/review', 'pre_f722e3c_')]:
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            src = os.path.join(base, name)
            if not os.path.isdir(src) or name.startswith('_'):
                continue
            dst = os.path.join(d, label + name)
            manifest = []
            for dp, dns, fns in os.walk(src):
                rel = os.path.relpath(dp, src)
                if rel != '.':
                    continue          # seat scratch subdirectories (work/) are listed, not copied
                for fn in sorted(fns):
                    p = os.path.join(dp, fn)
                    if os.path.getsize(p) <= 2_500_000:
                        copy_text(p, os.path.join(dst, fn))
                    manifest.append('%8d  %s' % (os.path.getsize(p), fn))
            for sub in dns:
                for dp, _, fns in os.walk(os.path.join(src, sub)):
                    for fn in fns:
                        p = os.path.join(dp, fn)
                        manifest.append('%8d  %s/%s' % (os.path.getsize(p), os.path.relpath(p, src), fn))
            write_text(os.path.join(dst, '_dir_listing.txt'),
                       '# seat output directory listing (bytes  path); files under scratch subdirectories and files > 2.5 MB are listed only\n'
                       + '\n'.join(sorted(manifest)) + '\n')
    ab = '/tmp/r32-accept/out/review_aborted'
    if os.path.isdir(ab):
        man = []
        for dp, _, fns in os.walk(ab):
            for fn in fns:
                p = os.path.join(dp, fn)
                man.append('%8d  %s' % (os.path.getsize(p), os.path.relpath(p, ab)))
        write_text(os.path.join(d, 'aborted_attempts_listing.txt'),
                   '# review attempts aborted on interface errors (no verdict formed) — listing only\n'
                   + '\n'.join(sorted(man)) + '\n')
    scan(d, 'reviews')


OPERATOR_TOOLS = ['fold_A3.py', 'fold_B3.py', 'fold_B4.py', 'seatlib_r32.py', 'dryverify.py', 'tc_probe.py',
                  'record_verdict.py', 'restamp_judgment.py', 'mk_protocol.py', 'mk_protocol_pre196.py',
                  'ev_collect.py', 'verify_manifest.py', 'redl_replay.sh', 'replay_real_r32.sh', 'rx.sh',
                  'ci.sh', 'count_late.py', 'battery.sh', 'scan_steps_late.py', 'ux.sh', 'dv.sh']


def section_folds():
    """Builder revisions after independent reviews: the fold scripts, their before/after
    logs and the dry-verify / clause-probe outputs of the revised judgments; plus the
    operator tools the acceptance procedure ran (so an auditor can re-run them)."""
    d = os.path.join(EV, 'builder_folds')
    for fn in sorted(os.listdir('/tmp/r32-accept/scripts')):
        if fn.startswith('fold_') and fn.endswith('.py'):
            copy_text(os.path.join('/tmp/r32-accept/scripts', fn), os.path.join(d, fn))
    for fn in sorted(os.listdir(OUT)):
        if re.match(r'fold_.*_diff\.txt$', fn) or fn in ('fold_B4.err',):
            copy_text(os.path.join(OUT, fn), os.path.join(d, fn))
    for fn in sorted(os.listdir(OUT)):
        if re.match(r'tcprobe_F4b?_[A-Z0-9]+\.txt$', fn) or fn.startswith('dryverify_judgment'):
            copy_text(os.path.join(OUT, fn), os.path.join(d, fn))
    t = os.path.join(EV, 'operator_tools')
    for fn in OPERATOR_TOOLS:
        p = os.path.join('/tmp/r32-accept/scripts', fn)
        if os.path.exists(p):
            copy_text(p, os.path.join(t, fn))
        else:
            print('missing tool', fn)
    copy_text('/tmp/r32-accept/scripts/fold_A3.log', os.path.join(d, 'fold_A3.log')) if os.path.exists(
        '/tmp/r32-accept/scripts/fold_A3.log') else copy_text(
        os.path.join(OUT, 'fold_A3.log'), os.path.join(d, 'fold_A3.log'))
    scan(d, 'folds')
    scan(t, 'operator_tools')


SECTIONS = {'wave0': section_wave0, 'engine_fix': section_engine_fix, 'aug': section_aug,
            'superseded': section_superseded, 'scan': lambda: scan(EV, 'all'),
            'reviews': section_reviews, 'folds': section_folds}
for _t in SESSION_NAME:
    SECTIONS['session_' + _t] = (lambda t: (lambda: section_session(t)))(_t)

if __name__ == '__main__':
    for s in sys.argv[1:]:
        SECTIONS[s]()
