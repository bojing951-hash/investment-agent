#!/usr/bin/python3 -I
# -*- coding: utf-8 -*-
"""s14_scan.py -- scan every file of the seat directory (outputs, scripts, intermediates) for model-vendor names and
credential-like strings.  Patterns are assembled from fragments so that this script itself contains no such name.
Only pattern index / file / offset / length are printed -- never the matched text.
usage: /usr/bin/python3 -I s14_scan.py <seat_dir> [<file> ...]
"""
import os
import re
import sys

SEAT = sys.argv[1]
ONLY = sys.argv[2:]
_W = [x + y for x, y in (("Ant", "hropic"), ("cla", "ude"), ("open", "ai"), ("chat", "gpt"), ("deep", "seek"), ("q", "wen"), ("tong", "yi"), ("gem", "ini"), ("lla", "ma"),
                          ("mis", "tral"), ("mo", "onshot"), ("ki", "mi"), ("gro", "k"), ("bai", "chuan"), ("hun", "yuan"), ("dou", "bao"), ("min", "imax"), ("step", "fun"),
                          ("ern", "ie"), ("son", "net"), ("op", "us"), ("hai", "ku"), ("fab", "le"))] + ["\u6587\u5fc3", "\u901a\u4e49", "\u667a\u8c31", "\u8c46\u5305"]
PATS = [
    ("vendor-word", re.compile("(?<![A-Za-z0-9_])(?:" + "|".join(_W) + ")(?![A-Za-z0-9_])", re.IGNORECASE)),
    ("vendor-short-1", re.compile("g" + "lm", re.IGNORECASE)),
    ("vendor-short-2", re.compile("zhi" + "pu", re.IGNORECASE)),
    ("secret-sk", re.compile(r"sk-[A-Za-z0-9]{16,}")),
    ("secret-bearer", re.compile(r"bearer\s+[A-Za-z0-9._\-]{16,}", re.IGNORECASE)),
    ("secret-aws", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("secret-gh", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("secret-xox", re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("secret-kv", re.compile(r"(api[_ \-]?key|access[_ \-]?token|secret[_ \-]?key|password|passwd)\s*[:=]\s*[\"']?[A-Za-z0-9_.\-]{10,}", re.IGNORECASE)),
    ("secret-pem", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("long-token", re.compile(r"(?<![A-Za-z0-9_\-/.])[A-Za-z0-9_\-]{32,}(?![A-Za-z0-9_\-/.])")),
]
HEXDIG = re.compile(r"[0-9a-fA-F]")


def is_hexish(tok):
    return len(HEXDIG.findall(tok)) >= 0.9 * len(tok)


def has_letter_digit(tok):
    return bool(re.search(r"[A-Za-z]", tok)) and bool(re.search(r"\d", tok))


files = []
for root, _dirs, names in os.walk(SEAT):
    for nm in names:
        files.append(os.path.join(root, nm))
files.sort()
if ONLY:
    files = [f for f in files if os.path.basename(f) in ONLY]
n_files = 0
total = 0
for f in files:
    try:
        txt = open(f, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError):
        try:
            txt = open(f, "rb").read().decode("latin-1")
        except OSError:
            continue
    n_files += 1
    for k, (lab, rx) in enumerate(PATS):
        hits = [(m.start(), len(m.group(0))) for m in rx.finditer(txt)]
        if lab == "long-token":
            hits = [(o, ln) for o, ln in hits if has_letter_digit(txt[o:o + ln]) and not is_hexish(txt[o:o + ln])]
        if hits:
            total += len(hits)
            print("HIT %d %s %s n=%d at=%s len=%s" % (k, lab, os.path.relpath(f, SEAT), len(hits), [o for o, _ in hits[:6]], [ln for _, ln in hits[:6]]))
print("files=%d hits=%d" % (n_files, total))
