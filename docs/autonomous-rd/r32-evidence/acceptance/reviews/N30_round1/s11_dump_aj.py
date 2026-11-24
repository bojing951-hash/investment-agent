import sys
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:7])
with open(sys.argv[7], 'w', encoding='utf-8') as f:
    for path, s in c.leaves:
        f.write(path + ' :: ' + s.replace(chr(10), ' ⏎ ') + chr(10))
print('leaves', len(c.leaves))
import os
print('bytes', os.path.getsize(sys.argv[7]))
