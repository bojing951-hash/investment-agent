#!/usr/bin/env python3
"""ev_collect5.py <section> [...]  — Audit-R32 evidence pack builder (final stamp 8f9055d).

Copies acceptance artefacts from the operator's out-of-repo work area into
docs/autonomous-rd/r32-evidence/acceptance/ of the PR worktree.

  reset        move the previous (superseded-stamp) acceptance/ directory out of the
               worktree into /tmp/r32-accept/evidence_prev/ (nothing is deleted)
  wave0        battery receipts (summary only; raw logs stay outside), CI receipts,
               clean-install + standard-update-entry receipts, baseline reproduction
  engine_fix   engine fixes found by the real runs: 0f3936d (official-record face) and
               8f9055d (reader-report rendering) — reproduction, gate red/green, patch,
               commit message
  aug          AUG re-verification at the final stamp + late-evidence count
  superseded   formal-entry artefacts of the superseded stamps 19638e1 and 0f3936d
  cross_stamp  engine-face comparison of every work order between the stamp of its
               last review and the final stamp (same frozen inputs)
  session X    final package of work order X (byte-exact) + seat log + verdicts
  reviews      review-seat protocols and outputs (text artefacts; bulky dumps listed only)
  folds        builder fold scripts, before/after logs, dry-verify / clause-probe
               outputs, and the operator tools the acceptance procedure ran

Text artefacts get the private home root rewritten to `~` (public-repo rule of
the R31 pack). Archive packages are copied byte-exact (their manifest binds
the bytes). Every section ends with the key scan: the LIVE data keys are read
in-process (never printed) and must occur in no evidence file; the scan also
counts model-vendor names (Latin literal and Chinese short names) and prints
the files that contain them.
"""
import datetime
import glob
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
# Chinese short names of model vendors: same rule in spirit (kept out of judgments and evidence)
VENDOR_CN = ['〖厂商名〗', '〖厂商名〗', '〖厂商名〗', '〖厂商名〗', '〖厂商名〗', '〖厂商名〗', '阶梯']
FINAL = '8f9055d'


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
    for line in open('/tmp/r32-accept/env5.sh', encoding='utf-8'):
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
    hits, vend, vcn, priv, nfiles = [], [], [], [], 0
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
            try:
                txt = raw.decode('utf-8')
            except UnicodeDecodeError:
                txt = ''
            found = sorted({w for w in VENDOR_CN if w in txt})
            if found:
                vcn.append((p, found))
            if HOME_ROOT.encode() in raw:
                priv.append(p)
    print('[scan %s] files=%d key_hits=%d vendor_literal_files=%d vendor_cn_files=%d private_root_files=%d'
          % (label, nfiles, len(hits), len(vend), len(vcn), len(priv)))
    for p in hits:
        print('   KEY HIT:', p)
    for p in vend[:10]:
        print('   vendor literal:', os.path.relpath(p, REPO))
    for p, w in vcn[:40]:
        print('   vendor cn:', os.path.relpath(p, REPO), w)
    for p in priv[:10]:
        print('   private root:', os.path.relpath(p, REPO))
    return len(hits) == 0


def section_reset():
    """Move the superseded-stamp evidence out of the worktree: only the UNTRACKED entries
    under acceptance/ (operator artefacts; nothing is deleted). Tracked files (the six
    committed question files under questions/) stay in place untouched."""
    if not os.path.isdir(EV):
        print('no previous acceptance dir')
        return
    st = subprocess.run(['git', '-C', REPO, 'status', '--porcelain', '--', 'docs/autonomous-rd/r32-evidence'],
                        capture_output=True, text=True).stdout.splitlines()
    tracked_dirty = [l for l in st if not l.startswith('??')]
    assert not tracked_dirty, 'tracked evidence files are modified: %s' % tracked_dirty
    untracked = [l[3:] for l in st if l.startswith('??')]
    if not untracked:
        print('no untracked evidence entries')
        return
    prev = '/tmp/r32-accept/evidence_prev'
    os.makedirs(prev, exist_ok=True)
    dest = os.path.join(prev, datetime.datetime.now().strftime('%Y%m%dT%H%M%S') + '_acceptance_superseded_stamps')
    os.makedirs(dest)
    for rel in untracked:
        assert rel.startswith('docs/autonomous-rd/r32-evidence/acceptance/'), rel
        assert '/questions' not in rel, 'refusing to move a tracked question file: %s' % rel
        src = os.path.join(REPO, rel)
        shutil.move(src, os.path.join(dest, os.path.relpath(src, EV)))
        print('moved', rel)
    print('moved %d untracked entries to' % len(untracked), dest)


def battery_receipt(tag, note=''):
    src = os.path.join(OUT, 'battery_' + tag, 'summary.tsv')
    # summary lines were cut at 120 bytes by the runner: decode leniently
    rows = [l.rstrip('\n').split('\t') for l in open(src, encoding='utf-8', errors='replace') if l.strip()]
    ok = [r for r in rows if r[0] == 'PASS']
    bad = [r for r in rows if r[0] != 'PASS']
    text = ['# Audit-R32 离线电池回执 @ %s' % tag, '',
            '- 口径: tests/test_*.py 逐件 `python3 tests/<file>`,绿 = rc ∈ {0, 5}(与 battery.sh 一致)',
            '- 结果: files=%d pass=%d fail=%d' % (len(rows), len(ok), len(bad)),
            '- 逐件清单见同目录 battery_%s_summary.tsv(状态 / rc / 文件);原始日志留在仓外' % tag, '']
    if note:
        text.append('- ' + note)
    if bad:
        text.append('- 红件: %s' % ', '.join('%s (rc %s; %s)' % (r[2], r[1], r[3]) for r in bad))
    write_text(os.path.join(EV, 'wave0_r32', 'battery_%s_receipt.md' % tag), '\n'.join(text) + '\n')
    # status / rc / file only: the runner's cut-at-120-bytes tail column is not
    # evidence (and test banners print names this pack keeps out of public text)
    tsv3 = '\n'.join('\t'.join(r[:3]) for r in rows) + '\n'
    write_text(os.path.join(EV, 'wave0_r32', 'battery_%s_summary.tsv' % tag), tsv3)
    print('battery', tag, len(rows), len(ok), len(bad))


def section_wave0():
    battery_receipt('0f3936d', '提交 0f3936d 提交后运行(当时工作树无未跟踪证据目录)。')
    battery_receipt('fix_committed_8f9055d',
                    '最终代码提交 %s 提交后运行;唯一红件 = test_arch_reform_phase6.py 的 D3「整改树工作面净」检查,'
                    '其列举的是未跟踪的验收证据目录(docs/autonomous-rd/r32-evidence/acceptance/*,纯文档),'
                    '与本轮代码无关;证据提交后同套件复跑结果见 wave0_r32/post_commit/。' % FINAL)
    for tag in ('fix_div_precommit', 'fix_gateA_precommit', 'fix_render_precommit'):
        rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(OUT, 'battery_' + tag, 'summary.tsv'),
                                                        encoding='utf-8', errors='replace') if l.strip()]
        bad = [r for r in rows if r[0] != 'PASS']
        write_text(os.path.join(EV, 'wave0_r32', 'battery_%s_summary.tsv' % tag),
                   '\n'.join('\t'.join(r[:3]) for r in rows) + '\n')
        print('battery', tag, len(rows), len(rows) - len(bad), [r[2] for r in bad])
    for f in ['ci_runs_branch_r32.txt', 'ci_jobs_all_stamps.txt', 'ci_jobs_45248512128.txt', 'ci_45270339721_jobs.txt']:
        copy_text(os.path.join(OUT, f), os.path.join(EV, 'wave0_r32', f))
    inst = os.path.join(EV, 'wave0_r32', 'clean_install_update_entry')
    for f in ['build_final5_base.log', 'build_final5_degraded.log', 'build_final5_aug.log', 'build_final5_entry.log',
              'final5_base_skill_install.json', 'final5_degraded_skill_install.json', 'final5_aug_skill_install.json',
              'final5_entry_skill_install.json', 'final5_base_pip.log', 'final5_entry_pip.log',
              'F5ENTRY_update_20261123T213152Z.json', 'F5ENTRY_update_20261123T213152Z.err',
              'F5ENTRY_update_20261123T213152Z.meta', 'F5ENTRY_update.launcher.log']:
        p = os.path.join(OUT, f)
        if os.path.exists(p):
            copy_text(p, os.path.join(inst, f))
        else:
            print('missing', f)
    # user-doc flow smoke at the final stamp on the post-update tree: doctor + plan of four
    # questions through --question-file (receipts of entry_smoke.sh); plan stage only
    for f in sorted(x for x in os.listdir(OUT)
                    if x.startswith('ESMOKE-') or x.startswith('F5ENTRY_doctor_') or x == 'runfacts_ESMOKE.txt'):
        copy_text(os.path.join(OUT, f), os.path.join(inst, f))
    old = os.path.join(inst, 'superseded_stamps')
    for f in ['build_final4_base.log', 'build_final4_degraded.log', 'build_final4_aug.log', 'build_final4_entry.log',
              'final4_base_skill_install.json', 'final4_entry_skill_install.json',
              'F4ENTRY_update_20261123T192713Z.json', 'F4ENTRY_update_20261123T192713Z.err',
              'F4ENTRY_update_20261123T192713Z.meta',
              'build_final3.log', 'build_final3_aug.log', 'build_final3_degraded.log',
              'final3_aug_skill_install.json', 'final3_degraded_skill_install.json',
              'update_final3.json', 'update_final3.err', 'update_final3.meta']:
        p = os.path.join(OUT, f)
        if os.path.exists(p):
            copy_text(p, os.path.join(old, f))
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
    # final committed-tree gate log (from battery #4) and the §J red/green pair
    copy_text(os.path.join(OUT, 'battery_fix_committed_8f9055d', 'test_audit_r32_gate.py.log'),
              os.path.join(EV, 'wave0_r32', 'gate_r32_final_%s.log' % FINAL))
    for fn in ['runfacts_X.txt', 'cmp_attached_X.txt']:
        copy_text(os.path.join(OUT, fn), os.path.join(EV, 'wave0_r32', fn.replace('_X.txt', '_final.txt')))
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
    copy_text('/tmp/r32-accept/scripts/probe_opr_fix.py', os.path.join(d, 'probe_opr_fix.py'))
    scan(d, 'engine_fix 0f3936d')
    # 8f9055d: reader-report rendering defects found by the real-run review rounds
    e = os.path.join(EV, 'engine_fix_reader_report')
    for f in ['gate_sec_j_RED.txt', 'gate_sec_j_GREEN.txt', 'gate_r32_fix_gateA_div_precommit.log',
              'gates_fix_precommit']:
        p = os.path.join(OUT, f)
        if os.path.isdir(p):
            for fn in sorted(os.listdir(p)):
                copy_text(os.path.join(p, fn), os.path.join(e, fn))
        elif os.path.exists(p):
            copy_text(p, os.path.join(e, f))
        else:
            print('missing', f)
    msg = subprocess.run(['git', '-C', REPO, 'log', '-1', '--format=%H%n%ad%n%B', '--date=iso', FINAL],
                         capture_output=True, text=True).stdout
    write_text(os.path.join(e, 'commit_%s_message.txt' % FINAL), msg)
    for path, name in (('scripts', 'fix_reader_report_scripts.patch'), ('tests', 'fix_reader_report_tests.patch')):
        diff = subprocess.run(['git', '-C', REPO, 'diff', '0f3936d..%s' % FINAL, '--', path],
                              capture_output=True, text=True).stdout
        assert diff.strip(), 'empty diff for ' + path
        write_text(os.path.join(e, name), diff)
    st = subprocess.run(['git', '-C', REPO, 'diff', '--stat', '19638e1..%s' % FINAL], capture_output=True, text=True).stdout
    write_text(os.path.join(e, 'diffstat_19638e1_to_%s.txt' % FINAL), st)
    scan(e, 'engine_fix %s' % FINAL)


def section_aug():
    d = os.path.join(EV, 'aug_plan')
    for ext in ('json', 'err', 'rc'):
        src = newest('XAUG_plan_.*\\.%s$' % ext)
        copy_text(src, os.path.join(d, 'final_' + os.path.basename(src)[len('XAUG_'):]))
    copy_text(os.path.join(OUT, 'count_late_X.txt'), os.path.join(d, 'count_late_final.txt'))
    runs = sorted(glob.glob('/tmp/r32-accept/final5-aug/output/research_runs/20261123T21*_以_2026_08_21_*'))
    assert len(runs) == 1, runs
    r = runs[0]
    rep = json.load(open(os.path.join(r, 'report.json'), encoding='utf-8'))
    run = rep.get('run') or {}
    bad = []
    for s in rep.get('steps') or []:
        if isinstance(s, dict) and s.get('ok') is not True:
            env = s.get('envelope') or {}
            bad.append('%s: error=%s' % (s.get('step'), json.dumps(env.get('error'), ensure_ascii=False)))
    lines = ['# AUG re-verification at the final stamp %s (read-only extract)' % FINAL, '',
             '# engine run: %s' % os.path.basename(r),
             '# git_head: %s | ts_utc: %s | run_ok: %s' % (run.get('git_head'), run.get('ts_utc'), run.get('run_ok', rep.get('run_ok'))),
             '# not-ok steps: %s' % (bad or '-'),
             '# frozen inputs: %s' % json.dumps(run.get('frozen_inputs'), ensure_ascii=False)]
    write_text(os.path.join(d, 'run_map.txt'), '\n'.join(lines) + '\n')
    for fn, name in (('report.md', 'final_report.md'), ('evidence_index.json', 'final_evidence_index.json'),
                     ('report.json', 'final_report.json')):
        copy_text(os.path.join(r, fn), os.path.join(d, name))
    rp = rep.get('research_plan') or {}
    gate = {'run_evidence_gate': run.get('evidence_gate'),
            'research_plan_cutoff': rp.get('cutoff'),
            'as_of_declared': rp.get('as_of_declared'),
            'frozen_inputs': run.get('frozen_inputs'),
            'git_head': run.get('git_head'),
            'ts_utc': run.get('ts_utc')}
    write_text(os.path.join(d, 'final_evidence_gate.json'), json.dumps(gate, ensure_ascii=False, indent=1) + '\n')
    # superseded-stamp AUG runs (0f3936d) for the record
    old = os.path.join(d, 'superseded_0f3936d')
    for i, tag in enumerate(['F4AUG', 'F4AUG2', 'F4AUG3'], 1):
        for ext in ('json', 'err', 'rc'):
            src = newest('%s_plan_.*\\.%s$' % (tag, ext))
            copy_text(src, os.path.join(old, 'run%d_%s' % (i, os.path.basename(src)[len(tag + '_'):])))
    copy_text(os.path.join(OUT, 'count_late_F4AUG3_0f3936d.txt'), os.path.join(old, 'count_late_run3.txt'))
    copy_text(os.path.join(OUT, 'cmp_X_AUG.txt'), os.path.join(d, 'cmp_AUG_0f3936d_to_%s.txt' % FINAL))
    scan(d, 'aug')


def section_superseded():
    for stamp, tags in (('19638e1', ['F3A', 'F3B', 'F3T3', 'F3N30', 'F3C4']),
                        ('0f3936d', ['F4A', 'F4B', 'F4T3', 'F4N30', 'F4C4'])):
        d = os.path.join(EV, 'superseded_%s' % stamp)
        for tag in tags:
            for stage in ('attach', 'report', 'archive'):
                for ext in ('json', 'rc'):
                    pat = '%s_%s_.*\\.%s$' % (tag, stage, ext)
                    if not [f for f in os.listdir(OUT) if re.match(pat, f)]:
                        continue
                    src = newest(pat)
                    copy_text(src, os.path.join(d, os.path.basename(src)))
        scan(d, 'superseded ' + stamp)


def section_cross_stamp():
    d = os.path.join(EV, 'cross_stamp_comparison')
    for f in sorted(os.listdir(OUT)):
        if re.match(r'cmp_X_.*\.txt$', f):
            copy_text(os.path.join(OUT, f), os.path.join(d, f))
    copy_text('/tmp/r32-accept/scripts/cmp_runs.py', os.path.join(d, 'cmp_runs.py'))
    copy_text('/tmp/r32-accept/scripts/cmp_frozen_x.py', os.path.join(d, 'cmp_frozen_x.py'))
    scan(d, 'cross_stamp')


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
        copy_text(newest('XC4_archive_.*\\.json$'), os.path.join(dst, 'archive_refusal_payload.json'))
        copy_text(newest_rc0('XC4_report_.*\\.json$'), os.path.join(dst, 'report_stage_receipt.json'))
        copy_text(newest('XC4_attach_.*\\.json$'), os.path.join(dst, 'attach_receipt.json'))
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
        copy_text(newest('X%s_archive_.*\\.json$' % tag), os.path.join(dst, 'archive_receipt.json'))
        copy_text(newest_rc0('X%s_report_.*\\.json$' % tag), os.path.join(dst, 'report_stage_receipt.json'))
        copy_text(newest('X%s_attach_.*\\.json$' % tag), os.path.join(dst, 'attach_receipt.json'))
    # formal-entry ledger lines of this work order (all stamps and rounds): lines whose
    # tag= field names this work order (exact token) or that carry this run id
    lines = [l for l in open('/tmp/r32-accept/seat_operator.log', encoding='utf-8', errors='replace')
             if tag in ledger_tags(l) or run_id in l]
    write_text(os.path.join(dst, 'seat_%s.log' % tag), ''.join(lines))
    scan(dst, 'session ' + tag)


def ledger_tags(line):
    """Work orders named by the tag= field of a ledger line (suffix letters after the
    stamp letter, e.g. F4T3 / XN30 -> T3 / N30)."""
    m = re.search(r'(?:^|[ ])tag=([^ ]+)', line)
    if not m:
        return set()
    out = set()
    for tok in m.group(1).split(','):
        if tok in SESSION_NAME:
            out.add(tok)
            continue
        mm = re.match(r'^(?:F\d*|X)([A-Z]+\d*)$', tok)
        if mm and mm.group(1) in SESSION_NAME:
            out.add(mm.group(1))
    return out


def section_reviews():
    d = os.path.join(EV, 'reviews')
    for base, label in [('/tmp/r32-accept/review5', ''),
                        ('/tmp/r32-accept/review4', 'superseded_0f3936d_'),
                        ('/tmp/r32-accept/review3', 'superseded_19638e1_'),
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


OPERATOR_TOOLS = ['fold_x.sh', 'seatlib_r32.py', 'dryverify.py', 'tc_probe.py',
                  'record_verdict.py', 'restamp_judgment.py', 'dumpitems.py', 'dumpverdict.py',
                  'mk_protocol.py', 'mk_protocol_pre196.py', 'mk_protocol5.py', 'attach_x.sh',
                  'ev_collect.py', 'ev_collect5.py', 'verify_manifest.py', 'replay_real_r32.sh',
                  'redl_engine.sh', 'redl_replay.sh', 'redl_r32_all.sh', 'redl_r31.sh', 'redl_r31_all.sh',
                  'redl_clone.sh', 'dumpitems_all.py',
                  'pkg_blob_check.py', 'manifest_head.py', 'rsum.py',
                  'rx.sh', 'cmp_runs.py', 'cmp_frozen_x.py', 'cmp_attached.py', 'rdls.py', 'runfacts.py',
                  'ci.sh', 'cijobs.sh', 'count_late.py', 'battery.sh', 'scan_steps_late.py', 'ux.sh', 'dv.sh',
                  'build_final5.sh', 'run_gate_sec.py', 'run_sec_j.py', 'entry_smoke.sh', 'mk_receipt.py',
                  'seat_scan.py']


def section_folds():
    """Builder revisions after independent reviews: the fold scripts, their before/after
    logs and the dry-verify / clause-probe outputs of the revised judgments; plus the
    operator tools the acceptance procedure ran (so an auditor can re-run them)."""
    d = os.path.join(EV, 'builder_folds')
    for fn in sorted(os.listdir('/tmp/r32-accept/scripts')):
        if fn.startswith('fold_') and (fn.endswith('.py') or fn.endswith('.sh')):
            copy_text(os.path.join('/tmp/r32-accept/scripts', fn), os.path.join(d, fn))
    for fn in sorted(os.listdir(OUT)):
        if re.match(r'fold_.*_diff\.txt$', fn) or fn in ('fold_B4.err',):
            copy_text(os.path.join(OUT, fn), os.path.join(d, fn))
        if re.match(r'tcprobe_(F4b?_[A-Z0-9]+|judgment5_[A-Z0-9]+)\.txt$', fn) or fn.startswith('dryverify_judgment'):
            copy_text(os.path.join(OUT, fn), os.path.join(d, fn))
    # fold logs of the final stamp (one per work order: every replacement with its frozen-input facts)
    for fn in sorted(os.listdir(OUT)):
        if re.match(r'fold_X_[A-Z0-9]+\.txt$', fn):
            copy_text(os.path.join(OUT, fn), os.path.join(d, fn))
    for fn in sorted(os.listdir(OUT)):
        if re.match(r'dump_[A-Z0-9]+_items\.txt$', fn):
            copy_text(os.path.join(OUT, fn), os.path.join(d, fn))
    t = os.path.join(EV, 'operator_tools')
    for fn in OPERATOR_TOOLS:
        p = os.path.join('/tmp/r32-accept/scripts', fn)
        if os.path.exists(p):
            copy_text(p, os.path.join(t, fn))
        else:
            print('missing tool', fn)
    if os.path.exists('/tmp/r32-accept/scripts/fold_A3.log'):
        copy_text('/tmp/r32-accept/scripts/fold_A3.log', os.path.join(d, 'fold_A3.log'))
    scan(d, 'folds')
    scan(t, 'operator_tools')


def section_replays():
    """Re-download-replay receipts at the final pushed commit (added after the evidence commit):
    per session console.log + replay envelopes (r*.json) + tree listings, per the work area
    /tmp/r32-accept/redl/<sha7>/ (sha read from out/replays_final_sha.txt). No renders, no clone."""
    d = os.path.join(EV, 'replays')
    sha_file = os.path.join(OUT, 'replays_final_sha.txt')
    n = 0
    if not os.path.exists(sha_file):
        print('no replays_final_sha.txt yet')
    else:
        sha = open(sha_file, encoding='utf-8').read().strip()
        root = '/tmp/r32-accept/redl/%s' % sha[:7]
        write_text(os.path.join(d, 'replayed_commit.txt'), 'commit cloned for the replays: %s\n' % sha)
        for sub in sorted(os.listdir(root)):
            p = os.path.join(root, sub)
            if sub.startswith('r31_session_') or (sub.startswith('session_') and os.path.isdir(p)):
                kind = 'r31_packages' if sub.startswith('r31_') else 'r32_packages'
                dst = os.path.join(d, kind, sub[len('r31_'):])
                for fn in ('head_ls_tree.z', 'base_ls_tree.z'):
                    if os.path.isfile(os.path.join(p, fn)):
                        raw = open(os.path.join(p, fn), 'rb').read()
                        write_text(os.path.join(dst, fn[:-2] + '.txt'),
                                   raw.replace(b'\0', b'\n').decode('utf-8'))
                        n += 1
                for dp, dns, fns in os.walk(p):
                    dns[:] = [x for x in dns if x != 'src']       # never descend into the clone
                    for fn in sorted(fns):
                        if fn == 'console.log' or re.match(r'r\d[b]?\.json$|^r_(final|old)\.json$', fn):
                            copy_text(os.path.join(dp, fn), os.path.join(dst, os.path.relpath(os.path.join(dp, fn), p)))
                            n += 1
            elif re.match(r'r3[12]_all_\d+T\d+\.log$', sub):
                copy_text(p, os.path.join(d, sub))
                n += 1
    print('replay receipt files', n)
    scan(d, 'replays')


def section_post_commit():
    """Post-commit verification logs (added in a follow-up docs-only commit)."""
    d = os.path.join(EV, 'wave0_r32', 'post_commit')
    src = os.path.join(OUT, 'post_commit_final')
    n = 0
    if os.path.isdir(src):
        for fn in sorted(os.listdir(src)):
            p = os.path.join(src, fn)
            if os.path.isfile(p):
                copy_text(p, os.path.join(d, fn))
                n += 1
    print('post-commit logs', n)
    scan(d, 'post_commit')


SECTIONS = {'reset': section_reset, 'wave0': section_wave0, 'engine_fix': section_engine_fix, 'aug': section_aug,
            'superseded': section_superseded, 'cross_stamp': section_cross_stamp,
            'scan': lambda: scan(EV, 'all'),
            'reviews': section_reviews, 'folds': section_folds, 'replays': section_replays,
            'post_commit': section_post_commit}
for _t in SESSION_NAME:
    SECTIONS['session_' + _t] = (lambda t: (lambda: section_session(t)))(_t)

if __name__ == '__main__':
    for s in sys.argv[1:]:
        SECTIONS[s]()
