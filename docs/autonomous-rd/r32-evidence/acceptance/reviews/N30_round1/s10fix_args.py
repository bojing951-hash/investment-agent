# s10fix_args.py <script>  -- fix arg-order slips: num(sec, src, comp, N, N, 'tok', 'snip') -> num(sec, src, comp, N, 'tok', 'snip')
import sys, re
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
pat = re.compile(r"(c\.num\('[FG]', '[^']*', [^,]+, (\d+(?:\.\d+)?), )(\d+(?:\.\d+)?), ('[^']*'), ('[^']*')")
n = 0
def rep(m):
    global n
    if m.group(2) == m.group(3):
        n += 1
        return m.group(1) + m.group(4) + ', ' + m.group(5)
    return m.group(0)
s2 = pat.sub(rep, s)
open(p, 'w', encoding='utf-8').write(s2)
print('fixed', n)
