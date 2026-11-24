#!/usr/bin/python3 -I
"""manifest_arch_head.py <package_dir> — read-only: print manifest archive_code_git_head (40 hex) of a
downloaded package (two-stamp "delivered after the verdict" packages; empty for same-stamp packages)."""
import json
import os
import sys

m = json.load(open(os.path.join(sys.argv[1], 'ARCHIVE_MANIFEST.json'), encoding='utf-8'))
print(m.get('archive_code_git_head') or '')
