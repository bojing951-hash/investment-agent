import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding='utf-8'))
def show(o, depth=0, maxdepth=3, pre=''):
    if isinstance(o, dict):
        for k, v in o.items():
            t = type(v).__name__
            extra = ''
            if isinstance(v, (dict, list)):
                extra = f' len={len(v)}'
            else:
                s = repr(v)
                extra = ' = ' + (s[:100] + '…' if len(s) > 100 else s)
            print('  ' * depth + f'{k}: {t}{extra}')
            if depth + 1 < maxdepth and isinstance(v, (dict, list)):
                show(v, depth + 1, maxdepth)
    elif isinstance(o, list):
        if o:
            print('  ' * depth + f'[0]: {type(o[0]).__name__}')
            if depth + 1 < maxdepth and isinstance(o[0], (dict, list)):
                show(o[0], depth + 1, maxdepth)
show(d, 0, 2)
