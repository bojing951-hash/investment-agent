#!/usr/bin/env python3
"""scan_pr_text.py <file>... — scan outgoing operator texts (PR comment bodies, state notes) with the
same three rules as the evidence-pack scan: no LIVE data key (read in-process from the read-only copy,
never printed), no vendor-name word (list kept outside the repository; never printed as words) and no
private home root. Also counts long opaque tokens (>= 32 chars) as a key-shape heuristic.
Exit 0 only when every file is clean. Prints counts only."""
import importlib.util
import os
import re
import sys

HOME_ROOT = '~'
LIVE_ENV = '~/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent/env_config.py'
VENDOR_LIST = '/tmp/r32-accept/vendor_cn.txt'


def vendor_words():
    words = []
    for line in open(VENDOR_LIST, encoding='utf-8'):
        line = line.strip()
        if line and not line.startswith('#'):
            words.append(line.split('=>')[0].strip())
    assert words, 'empty vendor word list'
    return words


def secrets():
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


def main(paths):
    secs = secrets()
    words = [(w, w.encode('utf-8')) for w in vendor_words()]
    home = HOME_ROOT.encode('utf-8')
    ok = True
    for p in paths:
        raw = open(p, 'rb').read()
        low = raw.lower()
        key_hits = sum(1 for v in secs.values() if v.encode() in raw)
        vend = sum(1 for w, wb in words if ((wb in low) if w.isascii() else (wb in raw)))
        priv = raw.count(home)
        text = raw.decode('utf-8')
        long_tokens = [t for t in re.findall(r'[A-Za-z0-9_\-]{32,}', text)
                       if not t.startswith('http')]
        clean = key_hits == 0 and vend == 0 and priv == 0 and not long_tokens
        ok = ok and clean
        print('[scan %s] bytes=%d key_hits=%d vendor_word_hits=%d private_root=%d long_tokens=%d CLEAN=%s'
              % (os.path.basename(p), len(raw), key_hits, vend, priv, len(long_tokens), clean))
        for t in long_tokens[:10]:
            print('   long token (length %d): %s…' % (len(t), t[:6]))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
