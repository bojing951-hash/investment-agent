# -*- coding: utf-8 -*-
"""rc14: 受审稿数字全覆盖清点(Audit-R32 A round1; 只读)。
用法: /usr/bin/python3 -I rc14_sweep.py <run_dir> <ledger points.jsonl>
目的: 收尾前逐数清点受审稿(agent_judgment.json 全文字符串字段)出现的阿拉伯数字,
      与台账 points.jsonl 的 computed/reported 数值集合对照, 列出"台账内无同值数值"的
      数字及其上下文, 供席位人工判读是否已有比对记录(精确到舍入/口径)或需补记。
本脚本不写台账(只打印)。
"""
import sys, os, re, json, collections

RUN = sys.argv[1]
PTS = sys.argv[2]
aj = json.load(open(os.path.join(RUN, 'agent_judgment.json'), encoding='utf-8'))
NUM = re.compile(r'(?<![A-Za-z_0-9.])\d+(?:\.\d+)?(?:%?)')
LEDN = re.compile(r'\d+(?:\.\d+)?')

led = set()
for line in open(PTS, encoding='utf-8'):
    if not line.strip():
        continue
    r = json.loads(line)
    blob = json.dumps([r.get('computed'), r.get('reported')], ensure_ascii=False)
    for m in LEDN.findall(blob):
        try:
            led.add(float(m))
        except ValueError:
            pass


def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, path + '.' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + '[%d]' % i)
    elif isinstance(o, str):
        yield path, o


strings = list(walk(aj))
tot = 0
unmatched = collections.OrderedDict()
per_field = []
for path, s in strings:
    toks = NUM.findall(s)
    tot += len(toks)
    um = []
    for t in toks:
        v = float(t.rstrip('%'))
        if v not in led:
            um.append(t)
    if um:
        per_field.append((path, len(toks), len(um)))
    for m in NUM.finditer(s):
        t = m.group(0)
        v = float(t.rstrip('%'))
        if v not in led:
            key = t
            unmatched.setdefault(key, []).append((path, s[max(0, m.start() - 34):m.end() + 30]))

print('字符串字段数', len(strings), '数字token总数', tot, '台账数值集合大小', len(led))
print('含未命中数字的字段:')
for p, n, u in per_field:
    print('   %s  tokens=%d unmatched=%d' % (p, n, u))
print('未命中数字种类', len(unmatched))
for k, lst in unmatched.items():
    print('== %s  x%d' % (k, len(lst)))
    seen = set()
    for path, ctx in lst:
        if (path, ctx) in seen:
            continue
        seen.add((path, ctx))
        if len(seen) > 6:
            print('   …')
            break
        print('   %s | …%s…' % (path[-58:], ctx.replace('\n', ' ')))
