#!/usr/bin/python3 -I
"""pkg_blob_check.py <package_dir> <repo_rel_prefix> <ls_tree_head.z> [<ls_tree_baseline.z>]

Read-only. "Source package keeps its original bytes" check for a package
downloaded from a commit: every file under <package_dir> is hashed as a git
blob (sha1 of "blob <len>\\0" + bytes) and compared with
  - `git ls-tree -r -z <cloned commit> -- <repo_rel_prefix>`   (mandatory, exact paths)
  - `git ls-tree -r -z <baseline commit> -- <repo_rel_prefix>` (optional)
Both listings are files produced by git in the caller's directory; paths in
them start with <repo_rel_prefix>/.
Against the baseline listing only, a path change with the same blob counts as
"renamed, same blob" when the pairing is unique on both sides (bytes identical,
name differs); it is listed explicitly. Any differing, unpaired or missing
file makes the result NOT identical (exit 1).
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


def cmp(name, tree, allow_rename=False):
    """Prints the comparison; returns True when nothing is left unexplained."""
    if tree is None:
        print('%s: no listing given' % name)
        return True
    only_local = sorted(set(local) - set(tree))
    only_tree = sorted(set(tree) - set(local))
    diff = sorted(k for k in local if k in tree and tree[k][1] != local[k])
    renamed = []
    if allow_rename:
        for k in list(only_local):
            cands = [t for t in only_tree if tree[t][1] == local[k]]
            twins = [x for x in only_local if local[x] == local[k]]
            if len(cands) == 1 and len(twins) == 1:
                renamed.append((cands[0], k))
                only_local.remove(k)
                only_tree.remove(cands[0])
    same_path = len(local) - len(only_local) - len(diff) - len(renamed)
    print('%s: package files=%d tree files=%d | blob-identical (same path)=%d | renamed, same blob=%d | '
          'differing=%d | only-in-package=%d | only-in-tree=%d'
          % (name, len(local), len(tree), same_path, len(renamed), len(diff), len(only_local), len(only_tree)))
    for old, new in renamed:
        print('   renamed (same blob %s): %s -> %s' % (local[new][:12], old, new))
    for label, lst in (('differing', diff), ('only-in-package', only_local), ('only-in-tree', only_tree)):
        for k in lst[:10]:
            print('   %s: %s' % (label, k))
    return not (only_local or only_tree or diff)


print('package dir: %s' % pkg)
print('prefix: %s' % prefix)
ok = cmp('cloned commit', head)
if base is not None:
    ok = cmp('audit baseline', base, allow_rename=True) and ok
print('RESULT: %s' % ('all package files blob-identical to the listings given' if ok else 'NOT identical'))
sys.exit(0 if ok else 1)
