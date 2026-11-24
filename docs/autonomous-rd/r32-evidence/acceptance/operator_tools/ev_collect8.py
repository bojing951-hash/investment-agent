#!/usr/bin/env python3
"""ev_collect8.py <section> [...]  — Audit-R32 evidence pack builder (final stamp 24141c01…; execution stamp 36499bb).

Generation 8 (ev_collect6.py described 36499bb as the final stamp). Two defects of the delivery chain
were found while delivering the execution-stamp work orders after their verdicts, and fixed in two
further commits:
  facc9a8  post-verdict delivery status surface (the reader map kept "review pending" after an UPHELD verdict)
  24141c0  two-stamp re-delivery package: the manifest names the archiving code; replay gate 4 accepts it
Execution split (disclosed in the report): plan / attach / independent review of the five work orders and
the AUG plan ran at 36499bb; the run directories and verdict records were carried byte-identical
(sha256-verified) into the final-stamp trees; report / archive / replays ran at 24141c01….

Copies acceptance artefacts from the operator's out-of-repo work area into
docs/autonomous-rd/r32-evidence/acceptance/ of the PR worktree.

  reset        move the previous (superseded-stamp) acceptance/ directory out of the
               worktree into /tmp/r32-accept/evidence_prev/ (nothing is deleted)
  wave0        battery receipts (summary only; raw logs stay outside), CI receipts,
               clean-install + standard-update-entry receipts, baseline reproduction
  engine_fix   engine fixes found by the real runs: 0f3936d (official-record face),
               8f9055d (reader-report rendering), 36499bb (LPR publication rule + turning-candidate
               observation-day guard), facc9a8 (post-verdict status surface) and 24141c0 (two-stamp
               re-delivery package) — reproduction, gate red/green, patch, commit message
  aug          AUG re-verification at the final stamp + late-evidence count (execution-stamp and older
               runs kept as superseded)
  superseded   formal-entry artefacts of the superseded stamps 19638e1, 0f3936d, 8f9055d, and the
               deliveries made at 36499bb / facc9a8 before the final-stamp re-delivery
  cross_stamp  engine-face comparison of every work order between stamps (same frozen inputs):
               0f3936d -> 8f9055d (cmp_X_*), 8f9055d -> 36499bb (cmp_Y_*), 36499bb -> 24141c0 (cmp_W_*)
  session X    final package of work order X (byte-exact; nothing else in the session directory)
  redelivery X final-stamp re-delivery of work order X: carry listing, report / archive / attach receipts,
               one-line map diff, replays on the final-stamp and execution-stamp engines, ledger lines
  reviews      review-seat protocols and outputs (text artefacts; bulky dumps listed only)
  folds        builder fold scripts, before/after logs, dry-verify / clause-probe
               outputs, and the operator tools the acceptance procedure ran
  replays      re-download-replay receipts at the pushed evidence commit
  post_commit  post-commit verification logs

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
FINAL = '24141c0'       # final code stamp: report / archive / replays of the formal work orders
EXEC = '36499bb'        # execution stamp: plan / attach / independent review of the five work orders (+ AUG plan)
ZSTAMP = 'facc9a8'      # post-verdict status-surface fix (its deliveries are superseded by FINAL)
PREV = '8f9055d'
TAGS = ('A', 'B', 'T3', 'N30', 'C4', 'AUG')


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
    """Run directories: RDW_<tag> = carried run directory in the final-stamp tree, RDY_<tag> = the same run
    directory at the execution stamp (env8.sh)."""
    env = {}
    for line in open('/tmp/r32-accept/env8.sh', encoding='utf-8'):
        line = line.strip()
        if line.startswith('export RD'):
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


def maybe_copy(name, dst_dir, base=OUT):
    p = os.path.join(base, name)
    if os.path.exists(p):
        copy_text(p, os.path.join(dst_dir, name))
    else:
        print('missing', name)


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


BATTERY_FINAL_NOTE = ('最终代码提交 %s 提交后运行(运行前工作树内的上一印章证据目录未进入工作树,工作树无未跟踪证据目录)。'
                      % FINAL)


def section_wave0():
    for tag, note in (('0f3936d', '提交 0f3936d 提交后运行(当时工作树无未跟踪证据目录)。'),
                      ('fix_committed_' + PREV,
                       '提交 %s 提交后运行(该印章已被后续提交取代);唯一红件 = test_arch_reform_phase6.py 的 D3「整改树工作面净」检查,'
                       '其列举的是未跟踪的验收证据目录(docs/autonomous-rd/r32-evidence/acceptance/*,纯文档),与代码无关。' % PREV),
                      ('fix_committed_' + EXEC, '提交 %s(执行印章: 五工单的规划/挂接/独立审查在该印章下运行)提交后运行。' % EXEC),
                      ('Zwork', '提交 %s 提交后运行(裁决后交付状态面修复;该印章下的再交付已被 %s 取代)。' % (ZSTAMP, FINAL)),
                      ('Wwork', BATTERY_FINAL_NOTE)):
        if os.path.isdir(os.path.join(OUT, 'battery_' + tag)):
            battery_receipt(tag, note)
        else:
            print('missing battery dir', tag)
    for tag in ('fix_div_precommit', 'fix_gateA_precommit', 'fix_render_precommit'):
        rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(OUT, 'battery_' + tag, 'summary.tsv'),
                                                        encoding='utf-8', errors='replace') if l.strip()]
        bad = [r for r in rows if r[0] != 'PASS']
        write_text(os.path.join(EV, 'wave0_r32', 'battery_%s_summary.tsv' % tag),
                   '\n'.join('\t'.join(r[:3]) for r in rows) + '\n')
        print('battery', tag, len(rows), len(rows) - len(bad), [r[2] for r in bad])
    for f in ['ci_runs_branch_r32.txt', 'ci_jobs_all_stamps.txt', 'ci_jobs_45248512128.txt', 'ci_45270339721_jobs.txt',
              'ci_jobs_45291551484.txt', 'ci_jobs_45330060557.txt', 'ci_jobs_45337815174.txt',
              'phase6_postcommit_Z.txt', 'phase6_postcommit_W.txt']:
        maybe_copy(f, os.path.join(EV, 'wave0_r32'))
    inst = os.path.join(EV, 'wave0_r32', 'clean_install_update_entry')
    final_files = ['build_final8.log', 'final8_base_skill_install.json', 'final8_degraded_skill_install.json',
                   'final8_aug_skill_install.json', 'final8_entry_skill_install.json', 'final8_base_pip.log',
                   'final8_degraded_pip.log', 'final8_aug_pip.log', 'final8_entry_pip.log',
                   'plan_w.launcher.log', 'plan_w_base.launcher.log', 'plan_w_degraded.launcher.log', 'w_stage.log',
                   'ux_WENTRY.launcher.log', 'entry_smoke_W.log']
    final_files += sorted(x for x in os.listdir(OUT)
                          if x.startswith('WENTRY_update') or x.startswith('WPLAN-')
                          or re.match(r'W(A|B|T3|N30|C4|AUG)_plan_', x))
    for f in final_files:
        if os.path.isfile(os.path.join(OUT, f)):
            maybe_copy(f, inst)
    # user-doc flow smoke at the final stamp on the post-update tree: doctor + plan of four
    # questions through --question-file (receipts of entry_smoke_w.sh / doctor_w.sh); plan stage only
    for f in sorted(x for x in os.listdir(OUT)
                    if (x.startswith('ESMOKE-W') or x.startswith('F8ENTRY_doctor_') or x == 'runfacts_ESMOKE_W.txt')
                    and os.path.isfile(os.path.join(OUT, x))):
        copy_text(os.path.join(OUT, f), os.path.join(inst, f))
    old = os.path.join(inst, 'superseded_stamps')
    old_files = [x for x in os.listdir(OUT)
                 if x.startswith(('build_final3', 'build_final4', 'build_final5', 'build_final6', 'build_final7',
                                  'final3_', 'final4_', 'final5_', 'final6_', 'final7_', 'F4ENTRY_', 'F5ENTRY_',
                                  'F6ENTRY_', 'YENTRY_update', 'ESMOKE-Y', 'zdry', 'plan_y', 'update_final'))
                 or re.match(r'Y(A|B|T3|N30|C4|AUG)_plan_', x) or re.match(r'ESMOKE-(A|B|N30|T3)_plan_', x)
                 or x in ('runfacts_ESMOKE.txt', 'runfacts_ESMOKE_Y.txt', 'zdeliver_summary.txt')]
    for f in sorted(old_files):
        if os.path.isfile(os.path.join(OUT, f)):  # name prefixes may also match scratch directories (out/zdry)
            copy_text(os.path.join(OUT, f), os.path.join(old, f))
    base = os.path.join(EV, 'wave0_r32', 'baseline_reproduction_72dab1c')
    R = '/tmp/r32-accept/repro'
    # baseline stamp 72dab1c: the AUG question re-planned in a clean baseline tree
    # (run 20261123T063810Z) and the independent audit's own exhibit (the R31
    # archived AUG report). count_late on both: L1 31/31 late, evidence 56/56 late.
    for f in ['aug_plan_20261123T063800Z.json', 'aug_plan_20261123T063800Z.err', 'R31_aug_report.json',
              'question_aug.txt', os.path.join('task2', 'repro_baseline_72dab1c.txt'),
              os.path.join('task2', 'repro_fixed_5b37e73.txt'),
              os.path.join('gold_dual', 'repro_baseline.txt'), os.path.join('gold_dual', 'repro_baseline_real.txt')]:
        maybe_copy(f, base, R)
    maybe_copy(os.path.join('tree', 'CODE_VERSION.json'), base, R)
    copy_text('/tmp/r32-accept/scripts/count_late.py', os.path.join(EV, 'wave0_r32', 'count_late.py'))
    copy_text('/tmp/r32-accept/scripts/battery.sh', os.path.join(EV, 'wave0_r32', 'battery.sh'))
    # first fix stamp 5b37e73: same question, late evidence gone (L1 31/0, evidence 55/0)
    a1 = os.path.join(EV, 'wave0_r32', 'after_first_fix_5b37e73')
    for stem in ['AUG_plan_20261123T102851Z.json', 'AUG_plan_20261123T102851Z.err', 'AUG_plan_20261123T102851Z.rc',
                 'AUG_steps_late_20261123T102851Z.txt']:
        maybe_copy(stem, a1)
    # committed-tree gate logs (from the batteries of the final stamp and of the stamp before it)
    maybe_copy(os.path.join('battery_Wwork', 'test_audit_r32_gate.py.log'),
               os.path.join(EV, 'wave0_r32', 'gate_r32_final_%s.log' % FINAL))
    maybe_copy(os.path.join('battery_Zwork', 'test_audit_r32_gate.py.log'),
               os.path.join(EV, 'wave0_r32', 'gate_r32_%s.log' % ZSTAMP))
    for fn in ['runfacts_W.txt', 'cmp_attached_W.txt']:
        p = os.path.join(OUT, fn)
        if os.path.exists(p):
            copy_text(p, os.path.join(EV, 'wave0_r32', fn.replace('_W.txt', '_final.txt')))
        else:
            print('missing', fn)
    scan(os.path.join(EV, 'wave0_r32'), 'wave0')


def commit_message(stamp):
    return subprocess.run(['git', '-C', REPO, 'log', '-1', '--format=%H%n%ad%n%B', '--date=iso', stamp],
                          capture_output=True, text=True).stdout


def patches(a, b, d, stem):
    for path, name in (('ia_cli.py', stem + '_cli.patch'), ('scripts', stem + '_scripts.patch'),
                       ('tests', stem + '_tests.patch')):
        diff = subprocess.run(['git', '-C', REPO, 'diff', '%s..%s' % (a, b), '--', path],
                              capture_output=True, text=True).stdout
        if diff.strip():
            write_text(os.path.join(d, name), diff)
        else:
            print('empty diff for', path, a, b)
    st = subprocess.run(['git', '-C', REPO, 'diff', '--stat', '%s..%s' % (a, b)], capture_output=True, text=True).stdout
    write_text(os.path.join(d, 'diffstat_%s_to_%s.txt' % (a, b)), st)


def section_engine_fix():
    d = os.path.join(EV, 'engine_fix_official_record')
    for f in ['probe_opr_fix_old.txt', 'probe_opr_fix_new.txt', 'probe_opr_T3.txt',
              'gate_sec_b_prefix_red.txt', 'gate_sec_b_new.txt', 'precommit_gates.txt',
              'fix_opr_planner.patch']:
        maybe_copy(f, d)
    write_text(os.path.join(d, 'commit_0f3936d_message.txt'), commit_message('0f3936d'))
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
    write_text(os.path.join(e, 'commit_%s_message.txt' % PREV), commit_message(PREV))
    patches('0f3936d', PREV, e, 'fix_reader_report')
    scan(e, 'engine_fix %s' % PREV)
    # 36499bb: LPR presumed publication date earlier than the actual one (rule ②) + turning-candidate
    # observation-day guard — found by the independent review of work order A at 8f9055d (EO-1)
    g = os.path.join(EV, 'engine_fix_lpr_publication_rule')
    for f in ['gate_sec_k_RED_at_%s.txt' % PREV, 'gate_sec_k_GREEN_worktree.txt', 'gates_lpr_precommit.launcher.log',
              'oldpkg_rerender_lpr.txt', 'commit_msg_lpr.txt']:
        maybe_copy(f, g)
    gp = os.path.join(OUT, 'gates_lpr_precommit')
    if os.path.isdir(gp):
        for fn in sorted(os.listdir(gp)):
            copy_text(os.path.join(gp, fn), os.path.join(g, 'gates_lpr_precommit', fn))
    write_text(os.path.join(g, 'commit_%s_message.txt' % EXEC), commit_message(EXEC))
    patches(PREV, EXEC, g, 'fix_lpr_rule')
    scan(g, 'engine_fix %s' % EXEC)
    # facc9a8: post-verdict delivery status surface — found when the execution-stamp work orders were
    # delivered after their UPHELD verdicts (the reader map still said "review pending")
    h = os.path.join(EV, 'engine_fix_post_verdict_status')
    for f in ['secL_RED_at_%s.txt' % EXEC, 'secL_GREEN_worktree.txt', 'commit_msg_Z.txt', 'stamp_Z.txt',
              'zdeliver_summary.txt', 'zmapdiff_T3.txt', 'zmapdiff_A.txt', 'zmapdiff_C4.txt']:
        maybe_copy(f, h)
    dry = os.path.join(h, 'dry_run_on_scratch_copies')
    if os.path.isdir(os.path.join(OUT, 'zdry')):
        for fn in sorted(os.listdir(os.path.join(OUT, 'zdry'))):
            p = os.path.join(OUT, 'zdry', fn)
            if os.path.isfile(p):
                copy_text(p, os.path.join(dry, fn))
        write_text(os.path.join(dry, '_NOTE.txt'),
                   '# Dry run of the status-surface fix on scratch COPIES of the execution-stamp run directories\n'
                   '# (before the fix was committed); not the formal deliveries. Formal deliveries of the closed work\n'
                   '# orders were then made at facc9a8 (superseded) and at the final stamp 24141c0 (redelivery/).\n')
    write_text(os.path.join(h, 'commit_%s_message.txt' % ZSTAMP), commit_message(ZSTAMP))
    patches(EXEC, ZSTAMP, h, 'fix_status_surface')
    scan(h, 'engine_fix %s' % ZSTAMP)
    # 24141c0: two-stamp re-delivery package — found when the facc9a8 packages (run SHA = execution stamp)
    # were replayed: no single stamp could replay them strictly; the manifest did not name the archiving code
    i = os.path.join(EV, 'engine_fix_two_stamp_package')
    for f in ['secL9_RED_at_%s.txt' % ZSTAMP, 'secL9_GREEN_worktree.txt', 'commit_msg_W.txt', 'stamp_W.txt',
              'wdeliver_summary.txt', 'w_stage.log']:
        maybe_copy(f, i)
    write_text(os.path.join(i, 'commit_%s_message.txt' % FINAL), commit_message(FINAL))
    patches(ZSTAMP, FINAL, i, 'fix_two_stamp_package')
    scan(i, 'engine_fix %s' % FINAL)


def section_aug():
    d = os.path.join(EV, 'aug_plan')
    for ext in ('json', 'err', 'rc'):
        src = newest('WAUG_plan_.*\\.%s$' % ext)
        copy_text(src, os.path.join(d, 'final_' + os.path.basename(src)[len('WAUG_'):]))
    copy_text(os.path.join(OUT, 'count_late_W.txt'), os.path.join(d, 'count_late_final.txt'))
    runs = sorted(glob.glob('/tmp/r32-accept/final8-aug/output/research_runs/2026112[45]T*_以_2026_08_21_*'))
    runs = [r for r in runs if os.path.basename(r)[:8] != '20261123']      # the carried execution-stamp run
    assert len(runs) == 1, runs
    aug_run_extract(runs[0], d, 'final', FINAL)
    # execution stamp 36499bb: the same plan-stage re-check one day earlier (superseded as "final")
    oldy = os.path.join(d, 'superseded_%s' % EXEC)
    for ext in ('json', 'err', 'rc'):
        src = newest('YAUG_plan_.*\\.%s$' % ext)
        copy_text(src, os.path.join(oldy, os.path.basename(src)[len('YAUG_'):]))
    copy_text(os.path.join(OUT, 'count_late_Y.txt'), os.path.join(oldy, 'count_late.txt'))
    ry = sorted(glob.glob('/tmp/r32-accept/final8-aug/output/research_runs/20261123T*_以_2026_08_21_*'))
    assert len(ry) == 1, ry
    aug_run_extract(ry[0], oldy, '', EXEC, keep_report_files=False)
    # superseded-stamp AUG runs: 0f3936d (three runs) and 8f9055d (one run)
    old = os.path.join(d, 'superseded_0f3936d')
    for i, tag in enumerate(['F4AUG', 'F4AUG2', 'F4AUG3'], 1):
        for ext in ('json', 'err', 'rc'):
            src = newest('%s_plan_.*\\.%s$' % (tag, ext))
            copy_text(src, os.path.join(old, 'run%d_%s' % (i, os.path.basename(src)[len(tag + '_'):])))
    copy_text(os.path.join(OUT, 'count_late_F4AUG3_0f3936d.txt'), os.path.join(old, 'count_late_run3.txt'))
    old2 = os.path.join(d, 'superseded_%s' % PREV)
    for ext in ('json', 'err', 'rc'):
        src = newest('XAUG_plan_.*\\.%s$' % ext)
        copy_text(src, os.path.join(old2, os.path.basename(src)[len('XAUG_'):]))
    copy_text(os.path.join(OUT, 'count_late_X.txt'), os.path.join(old2, 'count_late.txt'))
    copy_text(os.path.join(OUT, 'cmp_X_AUG.txt'), os.path.join(d, 'cmp_AUG_0f3936d_to_%s.txt' % PREV))
    copy_text(os.path.join(OUT, 'cmp_Y_AUG.txt'), os.path.join(d, 'cmp_AUG_%s_to_%s.txt' % (PREV, EXEC)))
    maybe_copy('cmp_W_AUG.txt', d)
    scan(d, 'aug')


def aug_run_extract(r, d, prefix, stamp, keep_report_files=True):
    rep = json.load(open(os.path.join(r, 'report.json'), encoding='utf-8'))
    run = rep.get('run') or {}
    bad = []
    for s in rep.get('steps') or []:
        if isinstance(s, dict) and s.get('ok') is not True:
            env = s.get('envelope') or {}
            bad.append('%s: error=%s' % (s.get('step'), json.dumps(env.get('error'), ensure_ascii=False)))
    lines = ['# AUG re-verification at the stamp %s (read-only extract)' % stamp, '',
             '# engine run: %s' % os.path.basename(r),
             '# git_head: %s | ts_utc: %s | run_ok: %s' % (run.get('git_head'), run.get('ts_utc'), run.get('run_ok', rep.get('run_ok'))),
             '# not-ok steps: %s' % (bad or '-'),
             '# frozen inputs: %s' % json.dumps(run.get('frozen_inputs'), ensure_ascii=False)]
    write_text(os.path.join(d, (prefix + '_' if prefix else '') + 'run_map.txt'), '\n'.join(lines) + '\n')
    if keep_report_files:
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
    write_text(os.path.join(d, (prefix + '_' if prefix else '') + 'evidence_gate.json'),
               json.dumps(gate, ensure_ascii=False, indent=1) + '\n')


def section_superseded():
    for stamp, tags in (('19638e1', ['F3A', 'F3B', 'F3T3', 'F3N30', 'F3C4']),
                        ('0f3936d', ['F4A', 'F4B', 'F4T3', 'F4N30', 'F4C4']),
                        (PREV, ['XA', 'XB', 'XT3', 'XN30', 'XC4'])):
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
    # deliveries made after the execution-stamp verdicts, before the final stamp: 36499bb (stale status
    # surface) and facc9a8 (packages without the archiving-code field) — receipts and manifests only;
    # the packages themselves stay in the isolated archive area outside the repository
    env = load_env()
    for stamp, letter in ((EXEC, 'Y'), (ZSTAMP, 'Z')):
        d = os.path.join(EV, 'superseded_%s' % stamp)
        for tag in ('A', 'T3', 'C4'):
            for stage in ('report', 'archive'):
                for ext in ('json', 'rc'):
                    pat = '%s%s_%s_.*\\.%s$' % (letter, tag, stage, ext)
                    if [f for f in os.listdir(OUT) if re.match(pat, f)]:
                        src = newest(pat)
                        copy_text(src, os.path.join(d, os.path.basename(src)))
            rid = os.path.basename(env['RDY_' + tag])
            area = {'Y': 'r32', 'Z': 'r32z'}[letter]
            mp = os.path.join('/tmp/r32-accept/archive', area, rid, 'ARCHIVE_MANIFEST.json')
            if os.path.isfile(mp):
                copy_text(mp, os.path.join(d, 'ARCHIVE_MANIFEST_%s.json' % tag))
        scan(d, 'superseded ' + stamp)


def section_cross_stamp():
    d = os.path.join(EV, 'cross_stamp_comparison')
    for f in sorted(os.listdir(OUT)):
        if re.match(r'cmp_[XYW]_.*\.txt$', f) or f == 'cmp_N30_19638e1_vs_0f3936d.txt' \
                or f in ('xdiff_X_vs_Y.txt', 'frozen_inputs_X_vs_Y.txt'):
            copy_text(os.path.join(OUT, f), os.path.join(d, f))
    for tool in ('cmp_runs.py', 'cmp_frozen_x.py', 'xdiff_y.py', 'frozen_inputs_xy.py', 'cmp_y_all.sh', 'cmp_y_summary.py',
                 'cmp_w_all.sh', 'cmp_w_summary.py', 'wrun.py', 'plan_w.sh'):
        copy_text('/tmp/r32-accept/scripts/' + tool, os.path.join(d, tool))
    scan(d, 'cross_stamp')


SESSION_NAME = {'A': 'session_A_formal', 'B': 'session_B_formal', 'T3': 'session_T3_formal',
                'N30': 'session_NEW30', 'C4': 'session_C4_degraded'}
RUN_FILES = ['report.json', 'agent_judgment.json', 'MAP_REPORT.md', 'MAP_REPORT.sha256', 'FULL_REPORT.md',
             'report.md', 'evidence_index.json', 'views_digest.json', 'AGENT_SEAT_ENVELOPE.json',
             'question_verbatim.txt']
CARRY_LISTING = {'A': 'carry_yz_base_AT3_W.txt', 'T3': 'carry_yz_base_AT3_W.txt', 'C4': 'carry_yz_degraded_C4_W.txt'}


def section_session(tag):
    """Final package of one work order at the final stamp. Archived work orders: the whole isolated
    archive directory byte-exact (manifest binds the bytes) and nothing else in the session directory.
    C4 (refused): the run's top-level files + the refusal payload."""
    env = load_env()
    rdy, rdw = env['RDY_' + tag], env.get('RDW_' + tag)
    if not rdw:
        raise SystemExit('no RDW_%s in env8.sh (not carried to the final-stamp tree yet)' % tag)
    dst = os.path.join(EV, SESSION_NAME[tag])
    if tag == 'C4':
        for fn in RUN_FILES + ['root_overlay/config/release_calendar.json', 'root_overlay/config/metric_registry.json']:
            copy_exact(os.path.join(rdw, fn), os.path.join(dst, fn))
        copy_text(newest('WC4_archive_.*\\.json$'), os.path.join(dst, 'archive_refusal_payload.json'))
    else:
        arc = os.path.join('/tmp/r32-accept/archive/r32w', os.path.basename(rdy))
        assert os.path.isfile(os.path.join(arc, 'ARCHIVE_MANIFEST.json')), 'no final-stamp package: ' + arc
        n = 0
        for dp, _, fns in os.walk(arc):
            for fn in fns:
                p = os.path.join(dp, fn)
                copy_exact(p, os.path.join(dst, os.path.relpath(p, arc)))
                n += 1
        print('package files', n)
    scan(dst, 'session ' + tag)


def section_redelivery(tag):
    """Final-stamp re-delivery record of one work order: carry listing (sha256-verified), stage receipts
    (attach at the execution stamp; report / archive at the final stamp), the one-line map diff, replays
    of the final-stamp package on the final-stamp and on the execution-stamp engine, ledger lines."""
    d = os.path.join(EV, 'redelivery', tag)
    maybe_copy(CARRY_LISTING.get(tag, 'carry_yz_%s_W.txt' % tag), d)
    maybe_copy('wmapdiff_%s.txt' % tag, d)
    maybe_copy(os.path.basename(newest('W%s_archive_.*\\.json$' % tag)), d)
    maybe_copy(os.path.basename(newest('W%s_report_.*\\.json$' % tag)), d)
    maybe_copy(os.path.basename(newest('Y%s_attach_.*\\.json$' % tag)), d)
    if tag != 'C4':
        for name in ('Wstrict', 'Ystrict'):
            for ext in ('json', 'err', 'rc'):
                maybe_copy('wreplay_%s_%s.%s' % (tag, name, ext), d)
            od = os.path.join(OUT, 'wreplay_%s_%s_out' % (tag, name))
            for fn in ('REPLAY_REPORT.json', 'REPLAY_REPORT.md'):
                p = os.path.join(od, fn)
                if os.path.isfile(p):
                    copy_text(p, os.path.join(d, '%s_%s' % (name, fn)))
                else:
                    print('missing', p)
    run_id = os.path.basename(load_env()['RDY_' + tag])[:16]
    lines = [l for l in open('/tmp/r32-accept/seat_operator.log', encoding='utf-8', errors='replace')
             if tag in ledger_tags(l) or run_id in l]
    write_text(os.path.join(d, 'seat_%s.log' % tag), ''.join(lines))
    scan(d, 'redelivery ' + tag)


def ledger_tags(line):
    """Work orders named by the tag= field of a ledger line (suffix letters after the
    stamp letter, e.g. F4T3 / XN30 / YA / ZC4 / WT3 / ESMOKE-WT3 -> T3 / N30 / A / C4 / T3 / T3)."""
    m = re.search(r'(?:^|[ ])tag=([^ ]+)', line)
    if not m:
        return set()
    out = set()
    for tok in m.group(1).split(','):
        if tok in SESSION_NAME:
            out.add(tok)
            continue
        mm = re.match(r'^(?:ESMOKE-|WPLAN-)?(?:F\d*|X|Y|Z|W|zdry-)([A-Z]+\d*)$', tok)
        if mm and mm.group(1) in SESSION_NAME:
            out.add(mm.group(1))
    return out


def section_reviews():
    d = os.path.join(EV, 'reviews')
    for base, label in [('/tmp/r32-accept/review6', ''),
                        ('/tmp/r32-accept/review5', 'superseded_%s_' % PREV),
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
    # review attempts aborted before any verdict (interface / timing errors on the operator side): listing only
    ab = []
    for root, title in (('/tmp/r32-accept/out/review_aborted',
                         '# review attempts aborted on interface errors (no verdict formed) — listing only\n'),
                        ('/tmp/r32-accept/review6/_aborted',
                         '# review attempts at stamp %s aborted before any verdict (launched against run directories that did not yet carry the report-stage artefacts; stopped after ~10 minutes; no verdict formed) — listing only\n' % EXEC)):
        for dp, _, fns in os.walk(root):
            for fn in fns:
                p = os.path.join(dp, fn)
                ab.append((title, '%8d  %s' % (os.path.getsize(p), os.path.relpath(p, os.path.dirname(root)))))
    if ab:
        write_text(os.path.join(d, 'aborted_attempts_listing.txt'),
                   '\n'.join(t for t in dict.fromkeys(t for t, _ in ab))
                   + '\n'.join(x for _, x in sorted(ab, key=lambda y: y[1])) + '\n')
    scan(d, 'reviews')


OPERATOR_TOOLS = ['fold_x.sh', 'fold_y.sh', 'fold_y2.sh', 'seatlib_r32.py', 'dryverify.py', 'tc_probe.py', 'dv.sh',
                  'record_verdict.py', 'restamp_judgment.py', 'dumpitems.py', 'dumpverdict.py', 'dumpitems_all.py',
                  'jshow.py', 'jgrep.py', 'seat_scan.py',
                  'mk_protocol.py', 'mk_protocol_pre196.py', 'mk_protocol5.py', 'mk_protocol6.py', 'attach_x.sh', 'attach_y.sh',
                  'ev_collect.py', 'ev_collect5.py', 'ev_collect6.py', 'ev_collect8.py', 'verify_manifest.py', 'replay_real_r32.sh',
                  'redl_engine.sh', 'redl_replay.sh', 'redl_r32_all.sh', 'redl_r32w.sh', 'redl_r32w_all.sh', 'redl_r31.sh',
                  'redl_r31_all.sh', 'redl_clone.sh', 'manifest_arch_head.py',
                  'pkg_blob_check.py', 'manifest_head.py', 'rsum.py', 'rp_summ.py',
                  'rx.sh', 'cmp_runs.py', 'cmp_frozen_x.py', 'cmp_attached.py', 'cmp_attached_w.py', 'xdiff_y.py', 'frozen_inputs_xy.py',
                  'cmp_y_all.sh', 'cmp_y_summary.py', 'cmp_w_all.sh', 'cmp_w_summary.py', 'wrun.py', 'rdls.py', 'runfacts.py',
                  'ci.sh', 'cijobs.sh', 'cijobs_append.sh', 'count_late.py', 'battery.sh', 'scan_steps_late.py', 'ux.sh',
                  'build_final5.sh', 'build_final6.sh', 'build_final7.sh', 'build_final8.sh', 'plan_y.sh', 'plan_w.sh',
                  'run_gates.sh', 'run_gate_sec.py', 'run_sec_j.py',
                  'entry_smoke.sh', 'entry_smoke_y.sh', 'entry_smoke_w.sh', 'doctor_y.sh', 'doctor_w.sh', 'mk_receipt.py',
                  'z_deliver.sh', 'w_deliver.sh', 'z_replay.sh', 'w_replay.sh', 'w_stage.sh', 'zdry.sh', 'zmapdiff.py', 'zsumm.py',
                  'carry_yz.py',
                  'facts_T36.py', 'facts_T36b.py', 'facts_C46.py']


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
        if re.match(r'tcprobe_(F4b?_[A-Z0-9]+|judgment[567]_[A-Z0-9]+)\.txt$', fn) or fn.startswith('dryverify_judgment') \
                or re.match(r'dv6_[A-Z0-9]+\.console$', fn):
            copy_text(os.path.join(OUT, fn), os.path.join(d, fn))
    # fold logs per stamp (one per work order: every replacement with its frozen-input facts)
    for fn in sorted(os.listdir(OUT)):
        if re.match(r'fold_[XY]_[A-Z0-9]+\.txt$', fn):
            copy_text(os.path.join(OUT, fn), os.path.join(d, fn))
    for fn in sorted(os.listdir(OUT)):
        if re.match(r'dump_[A-Z0-9]+_items\.txt$', fn) or fn.startswith('proto6_'):
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
    per session console.log + replay envelopes + tree listings, per the work area
    /tmp/r32-accept/redl/<sha7>/ (sha read from out/replays_final_sha.txt). No renders, no clone.
    R32 two-stamp packages live under r32w_<session>/ (final-commit engine, archiving-stamp engine,
    execution-stamp engine); R31 packages under r31_<session>/."""
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
            if sub.startswith(('r31_session_', 'r32w_session_', 'session_')) and os.path.isdir(p):
                kind = 'r31_packages' if sub.startswith('r31_') else 'r32_packages'
                name = sub[len('r31_'):] if sub.startswith('r31_') else (sub[len('r32w_'):] if sub.startswith('r32w_') else sub)
                dst = os.path.join(d, kind, name)
                for fn in ('head_ls_tree.z', 'base_ls_tree.z'):
                    if os.path.isfile(os.path.join(p, fn)):
                        raw = open(os.path.join(p, fn), 'rb').read()
                        write_text(os.path.join(dst, fn[:-2] + '.txt'),
                                   raw.replace(b'\0', b'\n').decode('utf-8'))
                        n += 1
                for dp, dns, fns in os.walk(p):
                    dns[:] = [x for x in dns if x != 'src']       # never descend into the clone
                    for fn in sorted(fns):
                        if fn == 'console.log' or fn.endswith('_ls_tree.z') \
                                or re.match(r'r\d[b]?\.json$|^r_(final|old|run)\.json$', fn):
                            if fn.endswith('_ls_tree.z'):
                                raw = open(os.path.join(dp, fn), 'rb').read()
                                write_text(os.path.join(dst, os.path.relpath(os.path.join(dp, fn), p)[:-2] + '.txt'),
                                           raw.replace(b'\0', b'\n').decode('utf-8'))
                            else:
                                copy_text(os.path.join(dp, fn), os.path.join(dst, os.path.relpath(os.path.join(dp, fn), p)))
                            n += 1
            elif re.match(r'r3[12]w?_all_\d+T\d+\.log$', sub):
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
    SECTIONS['redelivery_' + _t] = (lambda t: (lambda: section_redelivery(t)))(_t)

if __name__ == '__main__':
    for s in sys.argv[1:]:
        SECTIONS[s]()
