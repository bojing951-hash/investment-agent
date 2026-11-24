#!/usr/bin/python3 -I
# Seat script 12: render the per-point recompute tables into PROSE-round1.md at the marker line.
# usage: s12_build_prose.py <recompute_points.json> <PROSE-round1.md>
# Reads the recompute table written by s10_recompute.py and replaces the marker line in the prose file.
import json, sys

pts_path, prose_path = sys.argv[1], sys.argv[2]
d = json.load(open(pts_path, encoding="utf-8"))
points = d["points"]
MARK = "<!-- POINTS TABLES APPENDED BY s12_build_prose.py -->"

ORDER = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩", "⑪", "⑫", "⑬", "⑭", "§4"]
TITLE = {
    "①": "① 截止日与观测 / 发布日不晚于截止日", "②": "② 点值锚格", "③": "③ 同比基期与最近有效同比", "④": "④ 政策面",
    "⑤": "⑤ 三利率分解与资产月窗", "⑥": "⑥ 转折判断与候选面", "⑦": "⑦ 传导链各环", "⑧": "⑧ 历史类比(零段)",
    "⑨": "⑨ 情景", "⑩": "⑩ 总判断 / 走位 / 对质表文字与数值", "⑪": "⑪ 诚实缺席项", "⑫": "⑫ 截止日当日标注",
    "⑬": "⑬ 契约非 VERIFIED 项", "⑭": "⑭ 交付门相关披露", "§4": "第 4 节 六查在场对照(竞争解释 / 反对证据)",
}

def cell(x):
    if x is None:
        return "—"
    s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)
    s = s.replace("|", "\\|").replace("\n", " ")
    return s

out = []
out.append("命中 %d / 偏离 %d(共 %d 点)。「直算值」=席位自冻结快照 / 冻结日历 / 引擎面独立计算;「报告值」=判断档或报告所载(含披露声明);「结果」=一致 或 **偏离**。\n" % (len(points) - d["recompute_mismatches"], d["recompute_mismatches"], len(points)))
for cat in ORDER:
    rows = [p for p in points if p["cat"] == cat]
    if not rows:
        continue
    nm = sum(1 for p in rows if not p["match"])
    out.append("### %s(%d 点,偏离 %d)\n" % (TITLE[cat], len(rows), nm))
    out.append("| 点 | 出处键 | 直算值 | 报告值 | 结果 | 备注 |")
    out.append("|---|---|---|---|---|---|")
    for p in rows:
        res = "一致" if p["match"] else "**偏离**"
        out.append("| %s | %s | %s | %s | %s | %s |" % (cell(p["id"]), cell(p["source"]), cell(p["computed"]), cell(p["reported"]), res, cell(p["note"])))
    out.append("")

text = open(prose_path, encoding="utf-8").read()
HEAD, TAIL = "## 2. 逐点复算清单\n", "\n## 3. 分类核对要点"
# idempotent: replace everything between the section-2 heading and the section-3 heading
assert text.count(HEAD) == 1 and text.count(TAIL) == 1, "section anchors must appear exactly once"
i, j = text.index(HEAD) + len(HEAD), text.index(TAIL)
text = text[:i] + "\n" + "\n".join(out).rstrip() + "\n" + text[j:]
open(prose_path, "w", encoding="utf-8").write(text)
print("prose bytes:", len(text.encode("utf-8")), "| tables:", len(ORDER), "| points rendered:", len(points))
