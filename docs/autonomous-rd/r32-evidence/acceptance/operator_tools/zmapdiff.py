#!/usr/bin/python3 -I
"""zmapdiff.py <pre_map> <run_dir> <src_tree> <dst_tree> <run_ts> — post-fix
re-delivery check for one carried work order (read-only):

  <pre_map>  = MAP_REPORT.md bytes as carried from the execution stamp (Y)
  <run_dir>  = the run directory after the re-delivery `report` at stamp Z
  <src_tree> = execution-stamp tree (verdict records as recorded)
  <dst_tree> = post-fix tree (carried verdict records)

Prints whole-file / content-segment digests before and after, the content lines
that differ (expected: exactly the 「分工」 review-status line for approved work
orders), the sidecar anchor check, the review-tail status lines, the counts of
the pending / decided phrases, and whether each verdict record is byte-identical
to its source.  Writes nothing."""
import hashlib
import os
import sys

pre_p, rd, src, dst, ts = sys.argv[1:6]
SPLIT = '\n## 语义审查'


def sha_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


pre = open(pre_p, encoding='utf-8').read()
post_b = open(os.path.join(rd, 'MAP_REPORT.md'), 'rb').read()
post = post_b.decode('utf-8')
pc, qc = pre.split(SPLIT)[0], post.split(SPLIT)[0]
sha = lambda s: hashlib.sha256(s.encode('utf-8')).hexdigest()   # noqa: E731
print('whole     pre %s (%d chars) | delivered %s (%d chars) | same=%s'
      % (sha(pre)[:16], len(pre), sha(post)[:16], len(post), pre == post))
print('content   pre %s (%d lines) | delivered %s (%d lines)'
      % (sha(pc)[:16], pc.count('\n') + 1, sha(qc)[:16], qc.count('\n') + 1))
pl, ql = pc.split('\n'), qc.split('\n')
if len(pl) != len(ql):
    print('content line counts differ: pre %d / delivered %d' % (len(pl), len(ql)))
    diff = None
else:
    diff = [(i, a, b) for i, (a, b) in enumerate(zip(pl, ql)) if a != b]
    print('content lines differing: %d' % len(diff))
    for i, a, b in diff[:20]:
        print('  L%d\n    - %s\n    + %s' % (i + 1, a[:220], b[:220]))
anchor = ''
try:
    anchor = open(os.path.join(rd, 'MAP_REPORT.sha256'), encoding='utf-8'
                  ).read().split()[0]
except (OSError, IndexError):
    pass
print('sidecar anchor == sha256(delivered file): %s'
      % (anchor == hashlib.sha256(post_b).hexdigest()))
print('review tail lines: %s'
      % [ln for ln in post.split('\n') if ln.startswith('- ') and '席位' in ln][:3])
print('「独立语义审查待裁」 pre %d / delivered %d ; 「待裁」 total pre %d / delivered %d ; '
      '「席位已裁」 pre %d / delivered %d'
      % (pre.count('独立语义审查待裁'), post.count('独立语义审查待裁'),
         pre.count('待裁'), post.count('待裁'),
         pre.count('席位已裁'), post.count('席位已裁')))
vsrc = os.path.join(src, 'audit', 'semantic_review')
n_v = 0
for day in sorted(os.listdir(vsrc)) if os.path.isdir(vsrc) else []:
    if not os.path.isdir(os.path.join(vsrc, day)):
        continue
    for n in sorted(os.listdir(os.path.join(vsrc, day))):
        if n.startswith('VERDICT-%s-' % ts):
            a = sha_file(os.path.join(vsrc, day, n))
            dp = os.path.join(dst, 'audit', 'semantic_review', day, n)
            b = sha_file(dp) if os.path.isfile(dp) else None
            n_v += 1
            print('verdict record %s/%s sha256 %s identical_in_post_fix_tree=%s'
                  % (day, n, a, a == b))
print('verdict records for run %s: %d' % (ts, n_v))
