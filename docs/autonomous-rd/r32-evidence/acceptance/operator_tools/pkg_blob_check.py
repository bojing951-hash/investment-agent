#!/usr/bin/python3 -I
"""pkg_blob_check.py <package_dir> <repo_rel_prefix> <ls_tree_head.z> [<ls_tree_baseline.z>]

Read-only. "Source package keeps its original bytes" check for a package
downloaded from a commit: every file under <package_dir> is hashed as a git
blob (sha1 of "blob <len>\\0" + bytes) and compared with
  - `git ls-tree -r -z <cloned commit> -- <repo_rel_prefix>`   (mandatory)
  - `git ls-tree -r -z <baseline commit> -- <repo_rel_prefix>` (optional)
Both listings are files produced by git in the caller's directory; paths in
them start with <repo_rel_prefix>/.
"""
import hashlib
import os
import sys


def blob_sha(path):
    data = open(path, 'rb').read()
    h = hashlib.sha1()
    h.update(b'blob %d\0' % len(data))
    h.update(data)
    return h.hexdigest()


def parse_ls(fn, prefix):
    out = {}
    raw = open(fn, 'rb').read()
    for rec in raw.split(b'\0'):
        if not rec:
            continue
        meta, path = rec.split(b'\t', 1)
        _mode, typ, sha = meta.split(b' ')
        rel = path.decode('utf-8')
        if not rel.startswith(prefix + '/'):
            continue
        out[rel[len(prefix) + 1:]] = (typ.decode(), sha.decode())
    return out


pkg, prefix, head_fn = sys.argv[1], sys.argv[2].rstrip('/'), sys.argv[3]
base_fn = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] else None
head = parse_ls(head_fn, prefix)
base = parse_ls(base_fn, prefix) if base_fn else None
local = {}
for dp, _, fns in os.walk(pkg):
    for fn in fns:
        p = os.path.join(dp, fn)
        local[os.path.relpath(p, pkg)] = blob_sha(p)


def cmp(name, tree):
    if tree is None:
        print('%s: no listing given' % name)
        return
    only_local = sorted(set(local) - set(tree))
    only_tree = sorted(set(tree) - set(local))
    diff = sorted(k for k in local if k in tree and tree[k][1] != local[k])
    print('%s: package files=%d tree files=%d | blob-identical=%d | differing=%d | only-in-package=%d | only-in-tree=%d'
          % (name, len(local), len(tree), len(local) - len(only_local) - len(diff),
             len(diff), len(only_local), len(only_tree)))
    for label, lst in (('differing', diff), ('only-in-package', only_local), ('only-in-tree', only_tree)):
        for k in lst[:10]:
            print('   %s: %s' % (label, k))


print('package dir: %s' % pkg)
print('prefix: %s' % prefix)
cmp('cloned commit', head)
cmp('audit baseline', base)
ok = (set(local) == set(head) and all(head[k][1] == local[k] for k in local))
if base is not None:
    ok = ok and set(local) == set(base) and all(base[k][1] == local[k] for k in local)
print('RESULT: %s' % ('all package files blob-identical to both listings' if ok else 'NOT identical'))
sys.exit(0 if ok else 1)
