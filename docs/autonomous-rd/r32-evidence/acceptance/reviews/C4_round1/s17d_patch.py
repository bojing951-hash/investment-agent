# -*- coding: utf-8 -*-
#!/usr/bin/python3 -I
# s17d: 定稿前修订 s17a_data.py / s17b_text.py(逐条断言唯一命中)。用法: /usr/bin/python3 -I s17d_patch.py S17A S17B
import sys
a_p, b_p = sys.argv[1:3]


def patch(path, pairs, drops=()):
    s = open(path, encoding="utf-8").read()
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, "命中 %d 次(应为 1): %s | %s" % (n, path, old[:60])
        s = s.replace(old, new)
    lines = s.split("\n")
    for pre in drops:
        hit = [l for l in lines if l.startswith(pre)]
        assert len(hit) == 1, "删除行命中 %d 次(应为 1): %s" % (len(hit), pre)
        lines = [l for l in lines if not l.startswith(pre)]
    open(path, "w", encoding="utf-8").write("\n".join(lines))


SRCFN = (
    'def src(r):\n'
    '    f, fc = str(r.get("file")), str(r.get("face"))\n'
    '    if re.match(r"^(pts_[a-z0-9]+\\.json|s\\d+[a-z0-9_]*)$", f):\n'
    '        for a, b in (("snapshot.", "research_snapshot_20261123.json "), ("calendar.", "release_calendar.json "), ("registry.", "metric_registry.json ")):\n'
    '            if fc.startswith(a):\n'
    '                fc = b + fc[len(a):]\n'
    '                break\n'
    '        return fc\n'
    '    return f + " · " + fc\n\n\n'
    'def table(rows, auxflag):'
)
patch(a_p, [
    ('assert not (ids & {r["id"] for r in new}), "补充点编号与既有点重复"',
     'new = [r for r in new if r["id"] not in ids]  # 幂等: 重跑不重复追加'),
    ('def table(rows, auxflag):', SRCFN),
    ('cell(r.get("file")) + " · " + cell(r.get("face"))', 'cell(src(r))'),
    ('出处(文件 · 面 + 键) | 复算项 |', '出处(只读面: 文件 · 面/键) | 复算项(序列ID@观测日/月 或 字段) |'),
])
patch(b_p, [
    ('未舍入差为 0.@@CORE_D@@(四舍五入 0.3768)', '未舍入差为 @@CORE_D@@(四舍五入 0.3768)'),
    ('A("## 3 逐点复算清单(比对点 @@NCMP@@ 点)")', 'A(T("## 3 逐点复算清单(比对点 @@NCMP@@ 点)"))'),
    ('USDCNY 两窗均约 -0.35%(@@C_CD@@% / @@C_M@@%)', 'USDCNY 引擎月窗 @@C_M@@%、共同交易日窗 @@C_CD@@%(两位小数下同为 -0.35%)'),
    ('    for o in [it["original"]] :\n        A("   - 原句: 「%s」" % o)\n',
     '    A("   - 原句: 「%s」" % it["original"])\n    for e in EXTRA.get(k - 1, []):\n        A("   - 另涉原句: 「%s」" % e)\n'),
    ('for k, it in enumerate([x for x in ITEMS if x["severity"] == "MINOR"], 1):',
     'EXTRA = {1: [O3b], 3: [O4b, O4c]}\nfor k, it in enumerate([x for x in ITEMS if x["severity"] == "MINOR"], 1):'),
    ('恒等残差均 0(R01–R21, R08/R12)', '恒等残差均 0(R 组 24 点; 残差 R08/R12)'),
    ('"WD1114": D["wd_1114"], "WD1115": D["wd_1115"],', '"WD1114": WD[D["wd_1114"]], "WD1115": WD[D["wd_1115"]],'),
    ('"WD0815": D["wd_0815"],', '"WD0815": WD[D["wd_0815"]],'),
    ('\nR = {\n', '\nWD = {"Saturday": "周六", "Sunday": "周日"}\nR = {\n'),
    ('「出处」列为 文件 · 面 + 键; ', '「出处」列为只读面(文件 · 面/键), 序列值的键即「复算项」列所载的 序列ID@观测日/月; '),
], drops=('A("   - MINOR-3 另涉原句',))
print("patched OK")
