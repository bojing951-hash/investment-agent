#!/usr/bin/python3 -I
# s05: 补充复算与引擎面切片(只读): 落差/四舍五入/USDJPY 多窗/WTI 破锚后走势/研究计划纪律字段/交付门/步骤清单
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rc_lib import *
snap_p, rep_p, cal_p, reg_p, aj_p, outdir = sys.argv[1:7]
snap, rep, cal, reg, aj = load(snap_p, rep_p, cal_p, reg_p, aj_p)
SS = snap["series_store"]
L = []
def p(*a):
    L.append(" ".join(str(x) for x in a))
def short(o, n=100000):
    return json.dumps(o, ensure_ascii=False)[:n]
# 1. 核心CPI同比未舍入差
y05, y08 = yoy(SS, "CORE_CPI", "2026-05"), yoy(SS, "CORE_CPI", "2026-08")
p("CORE_CPI yoy 2026-05 = %.6f  2026-08 = %.6f  未舍入差 = %.6f  所引四位小数之差 = %.4f" % (y05, y08, y08 - y05, round(y08, 4) - round(y05, 4)))
# 2. USDJPY / USDCNY / DXY 多窗
for m in ("USDJPY", "USDCNY", "DXY"):
    p(m, "10-20→11-19 = %.4f%%" % pct(at(SS, m, "2026-10-20"), at(SS, m, "2026-11-19")),
      "| 10-23→11-23 = %.4f%%" % pct(at(SS, m, "2026-10-23"), at(SS, m, "2026-11-23")),
      "| 10-23→11-20 = %.4f%%" % pct(at(SS, m, "2026-10-23"), at(SS, m, "2026-11-20")),
      "| 值: 10-20 %s 10-23 %s 11-19 %s 11-20 %s 11-23 %s" % (at(SS, m, "2026-10-20"), at(SS, m, "2026-10-23"), at(SS, m, "2026-11-19"), at(SS, m, "2026-11-20"), at(SS, m, "2026-11-23")))
# 3. WTI_F 破锚后走势
w = [(d, v) for d, v in series(SS, "WTI_F") if d >= "2026-11-02"]
p("WTI_F 自 2026-11-02: 低于锚 87.06 的观测 = %s" % [(d, round(v, 2)) for d, v in w if v < 87.06])
p("WTI_F 自 2026-11-02: 不低于锚的观测 = %s" % [(d, round(v, 2)) for d, v in w if v >= 87.06])
w2 = [(d, v) for d, v in series(SS, "WTI_F") if "2026-11-09" <= d <= CUT]
p("WTI_F 11-09..11-23 共 %d 个观测, 其中低于锚 %d 个" % (len(w2), sum(1 for d, v in w2 if v < 87.06)))
sep = [(d, v) for d, v in series(SS, "WTI_F") if "2026-09-01" <= d <= "2026-10-31"]
p("WTI_F 2026-09-01..2026-10-31 观测 %d 个, 最低 %.2f (%s), 全部>锚: %s" % (len(sep), min(v for d, v in sep), min(sep, key=lambda x: x[1])[0], all(v > 87.06 for d, v in sep)))
p("WTI_F 2026-10-30 之后至 11-08 的观测 = %s" % [(d, round(v, 2)) for d, v in series(SS, "WTI_F") if "2026-10-30" <= d <= "2026-11-08"])
# 4. 研究计划纪律字段
rp = rep["research_plan"]
for k in ("map_question", "question_summary", "asof_discipline", "turning_supplement_discipline", "cross_face_consistency", "anchor_semantics_note", "question_window", "ex_post_offsets", "shared_by", "as_of_declared", "regions", "dimensions", "context_metrics"):
    p("rp.%s = %s" % (k, short(rp.get(k), 1500)))
p("rp.policy_doc_facts = %s" % short(rp.get("policy_doc_facts"), 2500))
# 5. 交付门/阻断类
def find(o, key, path=""):
    res = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                res.append((path + "." + k, v))
            res += find(v, key, path + "." + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            res += find(v, key, path + "[%d]" % i)
    return res
for key in ("blocked_class", "deliverable", "delivery_gate", "archive_allowed", "blocked_reason", "gate_b", "run_ok"):
    for pa, v in find(rep, key)[:6]:
        p("report.json %s = %s" % (pa, short(v, 500)))
p("report.json top keys = %s" % list(rep.keys()))
p("report.json run keys = %s" % list(rep["run"].keys()))
for k in ("ok", "status", "blocked", "blocked_class", "draft", "deliverable", "archive"):
    if k in rep["run"]:
        p("run.%s = %s" % (k, short(rep["run"][k], 800)))
# 6. 步骤清单
st = rep["steps"]
p("step keys = %s" % list(st[0].keys()))
for i, s in enumerate(st):
    env = s.get("envelope") or {}
    nm = s.get("step") or s.get("step_id") or s.get("id") or s.get("name") or s.get("key")
    flags = []
    if env.get("ok") is False:
        flags.append("OK=FALSE")
    for k in ("status", "semantic_ok", "blocked", "reason"):
        if isinstance(env, dict) and k in env:
            flags.append("%s=%s" % (k, short(env[k], 160)))
    note = s.get("note")
    if i < len(st) and (flags or (isinstance(note, str) and ("阻断" in note or "缺数" in note or "并项" in note))):
        p("  step[%d] %s %s note=%s" % (i, nm, flags, (note or "")[:300]))
# 7. 契约验证明细
cv = rep["agent_judgment"]["contract_verification"]
p("contract_verification keys = %s" % list(cv.keys()))
for v in cv["verdicts"]:
    p("   ", short(v, 400))
p("cv other = %s" % short({k: v for k, v in cv.items() if k not in ("verdicts",)}, 1500))
# 8. 日历版本
p("calendar keys = %s version=%s n_entries=%d n_batches=%d" % (list(cal.keys()), cal.get("version"), len(cal["entries"]), len(cal.get("batches") or [])))
# 9. 三利率在 10-23 的另一窗口(引擎月窗起点)
for m in ("UST_10Y", "TIPS_10Y", "BEI_10Y"):
    p("%s 10-23→11-19 = %+.1fbp" % (m, bp(at(SS, m, "2026-10-23"), at(SS, m, "2026-11-19"))))
with open(os.path.join(outdir, "out_s05_extra.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(L))
print("s05 written lines", len(L))
