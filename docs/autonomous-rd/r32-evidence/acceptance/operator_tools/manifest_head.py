#!/usr/bin/python3 -I
"""manifest_head.py <package_dir> — read-only: print manifest run_code_git_head (40 hex) of a downloaded package."""
import json
import os
import sys

m = json.load(open(os.path.join(sys.argv[1], 'ARCHIVE_MANIFEST.json'), encoding='utf-8'))
print(m.get('run_code_git_head') or '')
