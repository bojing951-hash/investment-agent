#!/usr/bin/python3 -I
# s14: 受审稿内「计数类」阿拉伯数字(数字+量词)逐处清点 + 工单信封点值格结构。只读, 仅打印。
import sys, os, json, re
aj_p, env_p, rep_p, outdir = sys.argv[1:5]
aj = json.load(open(aj_p, encoding="utf-8")); env = json.load(open(env_p, encoding="utf-8")); rep = json.load(open(rep_p, encoding="utf-8"))
leaves = []
def walk(o, p):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, p + "." + k)
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, "%s[%d]" % (p, i))
    elif isinstance(o, str):
        leaves.append((p, o))
walk(aj, "$")
MW = "格|行|条|项|个|次|周|步|维|地|段|环|期|列|组|份|类|族|席|窗|大|小|种|侧|重|级|层|路|面"
seen = set()
print("##### 计数类数字(数字+量词)")
for p, s in leaves:
    for m in re.finditer(r"(?<![\d.\-])(\d+(?:\.\d+)?)\s*(" + MW + ")(?![\w])", s):
        a, b = max(0, m.start() - 34), min(len(s), m.end() + 26)
        print("%s | …%s…" % (p[:52], s[a:b].replace("\n", " ")))
print("\n##### 所有非日期阿拉伯整数 token 频次(排除 YYYY-MM-DD / YYYY-MM / 小数)")
cnt = {}
for p, s in leaves:
    t = re.sub(r"\d{4}-\d{2}-\d{2}", " ", s); t = re.sub(r"\d{4}-\d{2}(?!\d)", " ", t); t = re.sub(r"\d+\.\d+", " ", t); t = re.sub(r"\d{4}(?!\d)", " ", t)
    for m in re.finditer(r"(?<![\w.\-])\d+(?![\w.])", t):
        a, b = max(0, m.start() - 16), min(len(t), m.end() + 12)
        cnt.setdefault(m.group(0), []).append(t[a:b].replace("\n", " "))
for k in sorted(cnt, key=lambda x: int(x)):
    print("%s ×%d : %s" % (k, len(cnt[k]), " ‖ ".join(sorted(set(cnt[k]))[:4])))
print("\n##### 首观测 / 序列自 上下文")
for p, s in leaves:
    for kw in ("首观测", "序列自"):
        for m in re.finditer(kw, s):
            a, b = max(0, m.start() - 60), min(len(s), m.end() + 70)
            print("%s [%s] …%s…" % (p[:44], kw, s[a:b]))
print("\n##### 工单信封: 顶层键", list(env.keys()))
def find(o, p, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if "point" in k.lower() or "grid" in k.lower(): out.append((p + "." + k, v))
            find(v, p + "." + k, out)
    elif isinstance(o, list):
        for i, v in enumerate(o[:3]): find(v, "%s[%d]" % (p, i), out)
hits = []; find(env, "$", hits)
for p, v in hits:
    print("--", p, type(v).__name__, (list(v.keys())[:12] if isinstance(v, dict) else len(v)))
    print("   ", json.dumps(v, ensure_ascii=False)[:2600])
print("\n##### report.json 内 point_values")
hits = []; find(rep, "$", hits)
for p, v in hits:
    print("--", p, type(v).__name__, (list(v.keys())[:12] if isinstance(v, dict) else len(v)))
    print("   ", json.dumps(v, ensure_ascii=False)[:2600])
