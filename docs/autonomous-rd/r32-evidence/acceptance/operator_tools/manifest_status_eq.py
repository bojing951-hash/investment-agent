#!/usr/bin/python3 -I
"""manifest_status_eq.py <package_dir> — read-only: print 1 when the manifest of a downloaded two-stamp
package declares map_binding_status_equivalent (status-equivalent package: the map was re-rendered by the
archiving code with only the review-status phrase changed), else 0 (same-render package: the delivered bytes
are the run-stamp rendering)."""
import json
import os
import sys

m = json.load(open(os.path.join(sys.argv[1], 'ARCHIVE_MANIFEST.json'), encoding='utf-8'))
print(1 if m.get('map_binding_status_equivalent') else 0)
