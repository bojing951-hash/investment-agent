# s22_echofilter.py <echo.txt> <out.txt>  -- split unanchored tokens into date-like vs substantive
import sys, re
src, out = sys.argv[1:3]
rows = [l.rstrip(chr(10)).split(' | ', 2) for l in open(src, encoding='utf-8')]
sub = []; dl = []
for path, t, ctx in rows:
    allnum = re.match('^[0-9]+$', t) is not None
    # date-like: token adjacent to '-' or '/' in context, or part of MM-DD
    i = ctx.find(t)
    before = ctx[max(0, i - 1):i]
    after = ctx[i + len(t): i + len(t) + 1]
    if allnum and len(t) <= 2 and (before in '-/' or after in '-/'):
        dl.append((path, t, ctx))
    elif allnum and len(t) == 4 and t.startswith('20'):
        dl.append((path, t, ctx))
    else:
        sub.append((path, t, ctx))
with open(out, 'w', encoding='utf-8') as f:
    for x in sub:
        f.write(x[0] + ' | ' + x[1] + ' | ' + x[2] + chr(10))
print('total', len(rows), 'date-like', len(dl), 'substantive', len(sub))
# compact: for substantive, group by path and print token list with short ctx
cur = None
for path, t, ctx in sub:
    if path != cur:
        print('##', path)
        cur = path
    print('   ', t, '{', ctx, '}')
