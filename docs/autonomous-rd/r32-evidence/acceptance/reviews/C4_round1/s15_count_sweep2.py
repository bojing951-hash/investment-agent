#!/usr/bin/python3 -I
# s15: (a) 计数/锚格面结构定位; (b) ASCII 边界的全量数字 token 覆盖复扫(修正 s08 对紧贴字母/汉字的数字漏扫); (c) 既有 points 中与 75/67/变动点 相关的行。只读, 仅打印。
import sys, os, json, re
aj_p, env_p, rep_p, pts_p = sys.argv[1:5]
aj = json.load(open(aj_p, encoding="utf-8")); env = json.load(open(env_p, encoding="utf-8")); rep = json.load(open(rep_p, encoding="utf-8"))
pts = json.load(open(pts_p, encoding="utf-8"))
def desc(v):
    if isinstance(v, dict): return "dict keys=%s" % (list(v.keys())[:14],)
    if isinstance(v, list): return "list len=%d first=%s" % (len(v), json.dumps(v[0], ensure_ascii=False)[:700] if v else None)
    return "%s %r" % (type(v).__name__, v)
def find(o, p, out, kws):
    if isinstance(o, dict):
        for k, v in o.items():
            if any(w in k.lower() for w in kws): out.append((p + "." + k, v))
            find(v, p + "." + k, out, kws)
    elif isinstance(o, list):
        for i, v in enumerate(o[:2]): find(v, "%s[%d]" % (p, i), out, kws)
for name, obj in (("report.json", rep), ("envelope", env)):
    hits = []; find(obj, "$", hits, ("point", "anchor", "cell", "grid"))
    print("##### %s 含 point/anchor/cell/grid 的键 (%d)" % (name, len(hits)))
    for p, v in hits:
        print("--", p, desc(v))
        if isinstance(v, (dict, list)): print("   ", json.dumps(v, ensure_ascii=False)[:1800])
print("\n##### envelope.reader_map_contract 键", list(env["reader_map_contract"].keys()))
ef = env["reader_map_contract"].get("engine_faces", {})
print("engine_faces 键:", list(ef.keys()))
for k, v in ef.items():
    print(" *", k, desc(v))
print("frozen_inputs:", json.dumps(env.get("frozen_inputs"), ensure_ascii=False)[:900])
print("evidence_index_rows:", desc(env.get("evidence_index_rows")))
print("\n##### 既有 points 中含 75 / 67 / 变动点 / 0.557 / 0.478 的行")
for r in pts:
    blob = " ".join(str(r.get(k)) for k in ("id", "key", "calc_str", "report", "note"))
    if any(w in blob for w in ("+75", "75bp", "+67", "67bp", "变动点", "0.557", "0.478", "六个")):
        print("%s | ok=%s | %s | calc=%s | rep=%s" % (r["id"], r["ok"], str(r.get("key"))[:110], r.get("calc_str"), r.get("report")))
# ---------- (b) 全量数字 token 复扫 ----------
leaves = []
def walk(o, p):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, p + "." + k)
    elif isinstance(o, list):
        for i, v in enumerate(o): walk(v, "%s[%d]" % (p, i))
    elif isinstance(o, str): leaves.append((p, o))
walk(aj, "$")
def num(x):
    try: return float(x)
    except Exception: return None
repvals = []; repstrs = set()
for r in pts:
    if not r["ok"]: continue
    v = r.get("report"); f = num(v)
    if f is not None: repvals.append((f, r["id"]))
    if isinstance(v, str): repstrs.add(v)
tok = {}
for p, s in leaves:
    t0 = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+\-]\d{2}:\d{2}", " ", s)
    t = re.sub(r"\d{4}-\d{2}-\d{2}", " ", t0)
    for m in re.finditer(r"(?<![0-9A-Za-z_.\-])(\d+(?:\.\d+)?)(?![0-9A-Za-z_.])", t):
        x = m.group(1)
        if re.match(r"^\d{4}$", x) or re.match(r"^\d{4}-\d{2}$", t[m.start():m.start() + 7]): continue
        f = num(x)
        cov = [i for (fv, i) in repvals if abs(fv) == abs(f)]
        a, b = max(0, m.start() - 15), min(len(t), m.end() + 11)
        tok.setdefault(x, {"n": 0, "cov": sorted(set(cov))[:6], "ctx": []})
        tok[x]["n"] += 1
        c = t[a:b].replace("\n", " ")
        if len(tok[x]["ctx"]) < 3 and c not in tok[x]["ctx"]: tok[x]["ctx"].append(c)
unc = {k: v for k, v in tok.items() if not v["cov"]}
print("\n##### 数字 token 总数 %d, 无同值通过点的 token %d" % (len(tok), len(unc)))
for k in sorted(unc, key=lambda z: num(z)):
    print("[%s] ×%d : %s" % (k, unc[k]["n"], " ‖ ".join(unc[k]["ctx"])))
print("\n##### 小整数(0..30 整数)token 的覆盖点与上下文(防同值巧合覆盖)")
for k in sorted(tok, key=lambda z: num(z)):
    if re.match(r"^\d{1,2}$", k) and num(k) <= 30:
        print("[%s] ×%d cov=%s : %s" % (k, tok[k]["n"], ",".join(tok[k]["cov"][:6]), " ‖ ".join(tok[k]["ctx"][:3])))
