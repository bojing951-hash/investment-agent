#!/usr/bin/python3 -I
"""carry_yz.py <src_tree> <dst_tree> <run_id> [<run_id> ...] — carry the run
directories of the Y stamp (36499bb) and their verdict records into the tree of
the post-fix stamp, byte-identical:

  <src>/output/research_runs/<run_id>            -> <dst>/output/research_runs/<run_id>
  <src>/audit/semantic_review/<day>/VERDICT-<run_ts>-*.json
                                                  -> same relative path under <dst>

Every copied file is verified by sha256 against its source; the listing (path,
bytes, sha256) is printed for the evidence record.  Existing destinations are
never overwritten (the script stops before copying anything)."""
import hashlib
import os
import shutil
import sys


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def walk(d):
    out = []
    for dp, dn, fn in os.walk(d):
        dn.sort()
        for n in sorted(fn):
            p = os.path.join(dp, n)
            out.append(os.path.relpath(p, d))
    return out


def main():
    src, dst = sys.argv[1:3]
    runs = sys.argv[3:]
    if not runs:
        print('usage: carry_yz.py <src_tree> <dst_tree> <run_id> [...]')
        return 2
    plan = []                                   # (abs_src, abs_dst)
    for rid in runs:
        s = os.path.join(src, 'output', 'research_runs', rid)
        if not os.path.isdir(s):
            print('missing source run dir: %s' % s)
            return 3
        plan.append((s, os.path.join(dst, 'output', 'research_runs', rid)))
        ts = rid[:16]
        vdir = os.path.join(src, 'audit', 'semantic_review')
        for day in sorted(os.listdir(vdir)) if os.path.isdir(vdir) else []:
            if not os.path.isdir(os.path.join(vdir, day)):    # lock files / MANIFEST.md
                continue
            for n in sorted(os.listdir(os.path.join(vdir, day))):
                if n.startswith('VERDICT-%s-' % ts):
                    plan.append((os.path.join(vdir, day, n),
                                 os.path.join(dst, 'audit', 'semantic_review',
                                              day, n)))
    for s, d in plan:
        if os.path.exists(d):
            print('destination exists (not overwritten): %s' % d)
            return 4
    n_files = n_bytes = 0
    for s, d in plan:
        os.makedirs(os.path.dirname(d), exist_ok=True)
        if os.path.isdir(s):
            shutil.copytree(s, d)
            rels = walk(s)
            pairs = [(os.path.join(s, r), os.path.join(d, r)) for r in rels]
            if walk(d) != rels:
                print('listing mismatch: %s' % d)
                return 5
        else:
            shutil.copy2(s, d)
            pairs = [(s, d)]
        for a, b in pairs:
            ha, hb = sha(a), sha(b)
            if ha != hb:
                print('sha mismatch: %s' % a)
                return 6
            n_files += 1
            n_bytes += os.path.getsize(b)
            print('%s  %9d  %s' % (ha[:16], os.path.getsize(b),
                                  os.path.relpath(b, dst)))
    print('carried %d run dir(s) + verdict records: files=%d bytes=%d, all sha256 equal to source'
          % (len(runs), n_files, n_bytes))
    return 0


if __name__ == '__main__':
    sys.exit(main())
