#!/usr/bin/python3 -I
# s23_assemble.py — 把分段文稿与逐点清单装配为 PROSE-round1.md
# 用法: /usr/bin/python3 -I s23_assemble.py <席位目录> <输出文件>
import os, sys

seat, out_p = sys.argv[1:3]
assert os.path.realpath(seat) == "/private/tmp/r32-accept/review4/C4_round1", seat


def rd(name):
    return open(os.path.join(seat, name), encoding="utf-8").read().rstrip("\n")


def block(title, name, note=""):
    body = rd(name)
    assert "```" not in body, name
    return "\n## %s\n\n%s\n\n```text\n%s\n```\n" % (title, note, body)


parts = [rd("_prose_p%d.md" % i) for i in range(1, 7)]
text = "\n".join(parts) + "\n"
text += block("附录 A · 逐点复算清单（主脚本 s10_recompute.py 输出 out_s10_table.txt 全文）", "out_s10_table.txt",
              "格式: [OK]/[XX] 编号 类别 | 出处 | 直算 | 报告 | 备注。304 行 = 计数点 297 + 引擎面自洽、渲染观察与对照事实 7 项。")
text += block("附录 B · 旁证: 情景真值表、类比面恒等、契约 STALE、汉字数字计数、数值溯源普查（out_s10_appendix.txt 全文）", "out_s10_appendix.txt",
              "数值溯源普查的 24 个「未溯源」数字已逐个人工回贴（第 3 节），全部可由 series_store 或引擎面直算得到。")
text += block("附录 C · 三条偏离的独立复算（s15_confirm.py 输出 out_s15_confirm.txt 全文，不依赖主脚本辅助函数）", "out_s15_confirm.txt")
text += block("附录 D · 问题清单所引数字的独立回贴（s20_num_check.py 输出 out_s20_num_check.txt 全文）", "out_s20_num_check.txt")
text += block("附录 E · 锚格修订口径旁证（s14_vintage.py 输出 out_s14_vintage.txt 全文）", "out_s14_vintage.txt")

with open(out_p, "w", encoding="utf-8") as f:
    f.write(text)
print("written", out_p, "chars", len(text), "lines", text.count("\n"))
