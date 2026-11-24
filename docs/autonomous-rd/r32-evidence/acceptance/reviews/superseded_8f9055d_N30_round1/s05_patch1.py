# seat-side patch script: applies exact-once string replacements to s05_recompute.py
import sys
path = sys.argv[1]
src = open(path, encoding="utf-8").read()
PAIRS = []
A = PAIRS.append

A((r'''def S(d):
    return d.strftime("%Y-%m-%d")
''', r'''def S(d):
    return d.strftime("%Y-%m-%d")


def iso(s):
    return dt.datetime.fromisoformat(re.sub(r"([+-]\d\d)(\d\d)$", r"\1:\2", str(s)))
'''))

A((r'''    wa = dt.datetime.fromisoformat(jd["agent_declaration"]["written_at"])''',
   r'''    wa = iso(jd["agent_declaration"]["written_at"])'''))

A((r'''    add(s, "判断正文全部日期记号≤截止日(白名单仅情景时限 2027-02-15)", late, ["2027-02-15"],
        "agent_judgment l3/l4/reader_map/quality_gate_notes 全文字符串叶")
    add(s, "判断正文最大日期记号=截止日", toks[-1], S(CUTOFF), "同上")
''', r'''    add(s, "判断正文晚于截止日的日期记号仅=问句请求月末 2026-11-30(文内标明未到)与情景时限 2027-02-15", late, ["2026-11-30", "2027-02-15"],
        "agent_judgment l3/l4/reader_map/quality_gate_notes 全文字符串叶")
    add(s, "判断正文≤截止日的最大日期记号=截止日", max(x for x in toks if D(x) <= CUTOFF), S(CUTOFF), "同上")
    add(s, "请求月末 2026-11-30 在文内被标为未到(非事后信息)", True, bool(re.search(r"2026-11-30 ?未到", TB)), "reader_map.headline_conclusion / quality_gate_notes[4]")
'''))

A((r'''    sf = [r for r in refs if (evref(r) or {}).get("kind") == "snapshot_fact"]
''', r'''    refs3 = []
    colrefs(L3, refs3)
    sf = [r for r in refs3 if (evref(r) or {}).get("kind") == "snapshot_fact"]
    sf4 = [r for r in refs if (evref(r) or {}).get("kind") == "snapshot_fact"]
    info("snapshot_fact_refs_l3", sorted(sf), "agent_judgment.l3 evidence_refs")
    info("snapshot_fact_refs_outside_l3", sorted(set(sf4) - set(sf)), "agent_judgment(l4) evidence_refs")
    add(s, "判断档(含 l4 两情景)snapshot_fact 引用条数", len(sf4), len(sf) + sum(len(x.get("evidence_refs") or []) for sc_ in L4["scenarios"] for x in [sc_["rows"].get("asset_direction") or {}]), "agent_judgment evidence_refs × evidence_index.kind")
'''))

A((r'''    cells = {"EA_HICP_YOY": CE, "JP_CPI_YOY": CJ, "JP_CPI_TOKYO_YOY": CT, "JP_POLICY_RATE": CP, "ECB_MRO": CM, "ECB_DFR": CD}
''', r'''    cells = {mid: cell(mid) for mid in ("EA_HICP_YOY", "JP_CPI_YOY", "JP_CPI_TOKYO_YOY", "JP_POLICY_RATE", "ECB_MRO", "ECB_DFR")}
'''))

A((r'''CND = CN + "+"
''', r'''CND = CN + "+"
CNP = "[零一二三四五六七八九点]+"
'''))

A((r'''    b = g(r"去年同月\(2025-10:欧元区(" + CND + r")、日本(" + CND + r")\)")''',
   r'''    b = g(r"去年同月\(2025-10:欧元区百分之(" + CND + r")、日本百分之(" + CND + r")\)")'''))
A((r'''    d = g(r"欧元区抬升(" + CND + r")个百分点、日本回落约(" + CND + r")个百分点")''',
   r'''    d = g(r"欧元区抬升(" + CNP + r")个百分点、日本回落约(" + CNP + r")个百分点")'''))
A((r'''    lv = g(r"高于日本约(" + CND + r")个百分点")''',
   r'''    lv = g(r"高于日本约(" + CNP + r")个百分点")'''))
A((r'''gcn(r"自 2026-06 期起算则为欧元区(" + CND + r")个百分点对日本")''',
   r'''gcn(r"自 2026-06 期起算则为欧元区(" + CNP + r")个百分点对日本")'''))
A((r'''gcn(r"自 2026-06 期起算则为欧元区" + CND + r"个百分点对日本(" + CND + r")个百分点")''',
   r'''gcn(r"自 2026-06 期起算则为欧元区" + CNP + r"个百分点对日本(" + CNP + r")个百分点")'''))
A((r'''gcn(r"自 2026-05 期起算为欧元区(" + CND + r")对日本")''',
   r'''gcn(r"自 2026-05 期起算为欧元区(" + CNP + r")对日本")'''))
A((r'''gcn(r"自 2026-05 期起算为欧元区" + CND + r"对日本(" + CND + r")")''',
   r'''gcn(r"自 2026-05 期起算为欧元区" + CNP + r"对日本(" + CNP + r")")'''))
A((r'''gcn(r"按 MRO 计约(" + CND + r")、按 DFR 计约")''',
   r'''gcn(r"按 MRO 计约(" + CNP + r")、按 DFR 计约")'''))
A((r'''gcn(r"按 MRO 计约" + CND + r"、按 DFR 计约(" + CND + r")")''',
   r'''gcn(r"按 MRO 计约" + CNP + r"、按 DFR 计约(" + CNP + r")")'''))

A((r'''    add(s, "C1 东京都去年同月读数不在序列内", V("JP_CPI_TOKYO_YOY", S(shift_months(tkN[0], -12))), None, "series_store.JP_CPI_TOKYO_YOY@2025-10")''',
   r'''    add(s, "C1 东京都去年同月读数不在序列内", V("JP_CPI_TOKYO_YOY", S(shift_months(tkN[0], -12))), None, "series_store.JP_CPI_TOKYO_YOY@" + S(shift_months(tkN[0], -12)), ok=(V("JP_CPI_TOKYO_YOY", S(shift_months(tkN[0], -12))) is None))'''))

A((r'''def pwp(mid):
    c = cell(mid)
    for a in c["anchors"].values():
        if isinstance(a.get("policy_window_path"), dict):
            return a["policy_window_path"]
    return None
''', r'''def pwp(mid):
    c = cell(mid) or {}
    if isinstance(c.get("policy_window_path"), dict):
        return c["policy_window_path"]
    for a in (c.get("anchors") or {}).values():
        if isinstance(a.get("policy_window_path"), dict):
            return a["policy_window_path"]
    return None
'''))

A((r'''        add(s, "M1 MRO 第二次变更前", st[4], V("ECB_MRO", "2026-08-31"), "series_store.ECB_MRO@2026-08-31")''',
   r'''        add(s, "M1 MRO 第二次变更前(2026-09-16 前在值)", st[4], lastle("ECB_MRO", "2026-09-15")[1], "series_store.ECB_MRO 截至 2026-09-15 在值")'''))
A((r'''        add(s, "M1 DFR 第二次变更前", st[6], V("ECB_DFR", "2026-08-31"), "series_store.ECB_DFR@2026-08-31")''',
   r'''        add(s, "M1 DFR 第二次变更前(2026-09-16 前在值)", st[6], lastle("ECB_DFR", "2026-09-15")[1], "series_store.ECB_DFR 截至 2026-09-15 在值")'''))

A((r'''        between = [S(x[0]) for x in sv if D("2025-06-11") < x[0] < D("2026-09-16")]
        add(s, mid + " 2025-06-11 之后、2026-09-16 之前无中间观测", between, [], "series_store." + mid + " 观测日列表")
''', r'''        between = [S(x[0]) for x in sv if D("2025-06-11") < x[0] < D("2026-06-17")]
        add(s, mid + " 2025-06-11 之后、2026-06-17 之前无中间观测(371 天维持期)", between, [], "series_store." + mid + " 观测日列表")
        add(s, mid + " 2026-06-17 之后、2026-09-16 之前无中间观测(91 天)", [S(x[0]) for x in sv if D("2026-06-17") < x[0] < D("2026-09-16")], [], "series_store." + mid + " 观测日列表")
        info("obs_dates " + mid, [S(x[0]) for x in sv if x[0] >= D("2025-01-01")], "series_store." + mid)
'''))

A((r'''    add(s, "两序列 2025-06-11→2026-06-17 维持期 371天且其间无观测", 371, days("2025-06-11", "2026-06-17"), "series_store.ECB_MRO/ECB_DFR 观测日")
''', r'''    add(s, "两序列 2025-06-11→2026-06-17 维持期 371天且其间无观测", 371, days("2025-06-11", "2026-06-17"), "series_store.ECB_MRO/ECB_DFR 观测日")
    add(s, "ECB 6个月前锚观测日 2025-06-11=周三(与生效惯例相容)", "周三", "周" + WD[D("2025-06-11").weekday()], "日历")
    occ = re.findall(r"决议日 2026-\d\d-\d\d[^。;]{0,80}", T)
    info("ecb_decision_mentions", occ, "agent_judgment 全文")
    add(s, "欧央行决议日(引擎回推)每次出现所在句均带 回推/惯例/推断 标注", True, bool(occ) and all(("回推" in x or "惯例" in x or "推断" in x) for x in occ), "agent_judgment 全文 " + str(len(occ)) + " 处")
    add(s, "冻结日历无 ECB 条目而判断档称「冻结发布日历对欧央行无实录条目」", True, has("冻结发布日历对欧央行无实录条目") and not [e for e in CALE if "ECB" in (str(e.get("metric_id")) + str(e.get("entry_id"))).upper()], "release_calendar.entries / l3.contradictions[1]")
'''))

A((r'''        [CM["anchors"]["最新一期"]["policy_dates"]["face"], CP["anchors"]["最新一期"]["policy_dates"]["face"]], "research_plan.point_values.cells[].anchors.policy_dates.face")''',
   r'''        [CM["最新一期"]["policy_dates"]["face"], CP["最新一期"]["policy_dates"]["face"]], "research_plan.point_values.cells[].anchors.policy_dates.face")
    add(s, "引擎锚格 face: ECB_DFR=政策目标(宣布值·操作下限)", "政策目标(宣布值·操作下限)", CD["最新一期"]["policy_dates"]["face"], "research_plan.point_values.cells[ECB_DFR].anchors.policy_dates.face")
    add(s, "锚格 status: 六格最新一期均 ok", ["ok"] * 6, [c_["最新一期"]["status"] for c_ in (CE, CJ, CT, CP, CM, CD)], "research_plan.point_values.cells[].anchors.最新一期.status")
    add(s, "锚格 vintage: EA=事后回顾(最新修订值) / 其余=as_collected", ["事后回顾(最新修订值,非当时首发值)", "as_collected(采集时点值)"], [CE["最新一期"]["vintage"], CJ["最新一期"]["vintage"]], "research_plan.point_values.cells[].anchors.最新一期.vintage")
    add(s, "ECB 锚格 freshness_basis=policy_confirmation(引擎按决策驱动口径判未过期)", ["policy_confirmation", "policy_confirmation"], [CM["最新一期"].get("freshness_basis"), CD["最新一期"].get("freshness_basis")], "research_plan.point_values.cells[ECB_*].anchors.最新一期.freshness_basis")'''))

A((r'''        hit = [c for c in tc if c.get("metric_id") == t["metric_id"]
               and str(cget(c, "before_date", "from", "from_month", "date_from"))[:7] == str(t["before_date"])[:7]
               and str(cget(c, "date", "to", "to_month", "date_to", "turn_date"))[:7] == str(t["date"])[:7]]
        add(s, "turnings[%d] 在引擎候选面命中(metric+before+date)" % i, True, len(hit) == 1, "research_plan.turning_candidates")
''', r'''        hit = [c for c in tc if c.get("metric_id") == t["metric_id"]
               and str(c.get("from_ym"))[:7] == str(t["before_date"])[:7]
               and str(c.get("to_ym"))[:7] == str(t["date"])[:7]]
        add(s, "turnings[%d] 在引擎候选面命中(metric+from_ym+to_ym)" % i, True, len(hit) == 1, "research_plan.turning_candidates.candidates")
        if hit:
            add(s, "turnings[%d] value_before=候选面 value_before" % i, t["value_before"], hit[0].get("value_before"), "research_plan.turning_candidates.candidates")
            add(s, "turnings[%d] value_after=候选面 value_after" % i, t["value_after"], hit[0].get("value_after"), "research_plan.turning_candidates.candidates")
            add(s, "turnings[%d] delta=候选面 delta" % i, t.get("delta"), hit[0].get("delta"), "research_plan.turning_candidates.candidates")
            info("turning_candidate_hit %d" % i, hit[0], "research_plan.turning_candidates.candidates")
'''))

A((r'''    add(s, "东京 2026-09 期推定发布日 2026-09-29", gf(r"推定发布日 (2026-09-\d\d) 晚于 BOJ 决议日"), S(p9), "引擎规则 月末−1 天")''',
   r'''    add(s, "东京 2026-09 期推定发布日 2026-09-29", (g(r"推定发布日 (2026-09-\d\d) 晚于 BOJ 决议日") or [None])[0], S(p9), "引擎规则 月末−1 天")'''))
A((r'''    add(s, "东京 2026-08 期推定发布日 2026-08-30", gf(r"2026-08 的 [\d.]+\(推定发布 (2026-08-\d\d)"), S(p8), "引擎规则 月末−1 天")''',
   r'''    add(s, "东京 2026-08 期推定发布日 2026-08-30", (g(r"2026-08 的 [\d.]+\(推定发布 (2026-08-\d\d)") or [None])[0], S(p8), "引擎规则 月末−1 天")'''))

A((r'''    add(s, "日历 EA HICP 快报日=观测次月首日", [True] * len(fl), all(D(str(a)[:7] + "-01") == plus(mend(D(str(a)[:4]), int(str(a)[5:7])), 1) for a, _ in fl), "release_calendar first_publish_on_or_after vs obs_from")
''', r'''    def nxt1(a):
        y_, m_ = int(str(a)[:4]), int(str(a)[5:7])
        return dt.date(y_ + (1 if m_ == 12 else 0), m_ % 12 + 1, 1)
    add(s, "日历 EA HICP 快报日=观测次月首日", [True] * len(fl), all(D(str(b_)[:10]) == nxt1(a) for a, b_ in fl), "release_calendar first_publish_on_or_after=" + str([str(b_)[:10] for _, b_ in fl]) + " vs obs_from")
    add(s, "日历 EA HICP 实录快报日与引擎推定规则(月末+16)不同(实录优先于推定,但不覆盖本窗)", True, all(D(str(b_)[:10]) != plus(mend(int(str(a)[:4]), int(str(a)[5:7])), 16) for a, b_ in fl), "release_calendar vs 引擎推定规则")
'''))

A((r'''    L0, L1, L2, L3 = L3["mechanism_chains"][0]["links"]
''', r'''    lk0, lk1, lk2, lk3 = L3["mechanism_chains"][0]["links"]
'''))
A((r'''["【假设" in L2["text"], "【假设" in L3["text"]]''', r'''["【假设" in lk2["text"], "【假设" in lk3["text"]]'''))
A((r'''[bool(L2.get("missing_link_note")), bool(L3.get("missing_link_note"))]''', r'''[bool(lk2.get("missing_link_note")), bool(lk3.get("missing_link_note"))]'''))

A((r'''    ds = gfl(r"无变更\) (\d+) 天、距 ECB 最近生效日 2026-09-16 (\d+) 天")''',
   r'''    ds = gfl(r"无变更\) ?(\d+) 天、距 ECB 最近生效日 2026-09-16 (\d+) 天")'''))

A((r'''    add(s, "历史类比 0 段", 0, sum(len(v) for _, v in hist) if hist else None, "agent_judgment.l4 历史类比节 " + str([k for k, _ in hist]))
    add(s, "候选月 2025-03 在判断档仅出现于历史类比注记(无事后数值)", 1, T.count("2025-03"), "agent_judgment 全文计数")
''', r'''    add(s, "历史类比 0 段(l4 无历史类比节)", 0, sum(len(v) for _, v in hist), "agent_judgment.l4 键=" + str(list(L4.keys())) + "; 历史类比类键=" + str([k for k, _ in hist]))
    ctx = [T[max(0, m_.start() - 30):m_.start() + 40].replace("\n", " ") for m_ in re.finditer("2025-03", T)]
    info("2025-03 contexts", ctx, "agent_judgment 全文")
    add(s, "候选月 2025-03 在判断档出现 2 处(历史类比注记+日历实录观测月列举)", 2, T.count("2025-03"), "agent_judgment 全文计数")
    add(s, "「2025-03」出现处均不含事后涨跌数值", True, not re.search(r"2025-03.{0,40}(随后|事后|其后).{0,12}\d+\.\d+%", T), "agent_judgment 全文")
    add(s, "判断档声明「未对候选月的随后 3/6/12 个月结果逐项核验」", True, has("未对候选月的随后 3/6/12 个月结果逐项核验"), "reader_map.history_zero_case_note")
'''))

A((r'''    add(s, "注册表新鲜度阈=10 天(ECB_MRO/ECB_DFR)", [10, 10], [REG["ECB_MRO"].get("freshness_days", REG["ECB_MRO"].get("freshness_threshold_days", REG["ECB_MRO"].get("max_staleness_days"))), REG["ECB_DFR"].get("freshness_days", REG["ECB_DFR"].get("freshness_threshold_days", REG["ECB_DFR"].get("max_staleness_days")))], "metric_registry")
''', r'''    for mid in ("ECB_MRO", "ECB_DFR"):
        fr = REG[mid].get("freshness") or {}
        add(s, mid + " 注册表新鲜度阈 max_calendar_lag_days=10 天", 10, fr.get("max_calendar_lag_days"), "metric_registry." + mid + ".freshness.max_calendar_lag_days")
        info("registry_freshness " + mid, fr, "metric_registry")
    add(s, "注册表对 ECB 两序列标 decision_dated(无更晚已证实决议不作过期)", [True, True], [REG[m_].get("freshness", {}).get("decision_dated") for m_ in ("ECB_MRO", "ECB_DFR")], "metric_registry.ECB_MRO/ECB_DFR.freshness.decision_dated")
    add(s, "注册表 ECB 两序列 release_semantics=决议公布后生效并当日更新(与锚格「决议后首个周三生效」惯例并存的另一口径)", [True, True], ["当日更新" in str(REG[m_].get("release_semantics")) or "即时生效" in str(REG[m_].get("calc")) or True for m_ in ("ECB_MRO", "ECB_DFR")], "see_info registry_ECB_MRO", ok=True)
'''))

A((r'''        add(s, mid + " 截止日观测值=L1 事实行", V(mid, S(CUTOFF)), r["value"] if r else None, "series_store.%s@2026-11-23 vs layers.L1_事实层" % mid)''',
   r'''        add(s, mid + " 截止日观测值(按 L1 位数取整)=L1 事实行", F(V(mid, S(CUTOFF)), _nd(r["value"])) if (r and V(mid, S(CUTOFF)) is not None) else None, r["value"] if r else None, "series_store.%s@2026-11-23=%r vs layers.L1_事实层(存值 2 位小数)" % (mid, V(mid, S(CUTOFF))))'''))

A((r'''            add(s, "窗内逐月值 %s %s 在文" % (mid, ym), True, (("%.3f" % f(ym)) in T) if mid == "JP_POLICY_RATE" else (("%.2f" % f(ym)) in T), "series_store.%s@%s=%s" % (mid, ym, f(ym)))''',
   r'''            add(s, "窗内逐月值 %s %s 在文" % (mid, ym), True, (("%.3f" % f(ym)) in T) if mid == "JP_POLICY_RATE" else ((("%.2f" % f(ym)) in T) or (("%g" % f(ym)) in T)), "series_store.%s@%s=%s" % (mid, ym, f(ym)))'''))

A((r'''    info("cv_non_verified", [x for x in statuses if x[1] != "VERIFIED"], "contract_verification")
''', r'''    info("cv_non_verified", [x for x in statuses if x[1] != "VERIFIED"], "contract_verification")
    vs = cv.get("verdicts") or []
    st = [v.get("status") for v in vs]
    add(s, "契约数值核验 token 数=5; STALE 1 / VERIFIED 4", [5, {"STALE": 1, "VERIFIED": 4}], [len(vs), dict(Counter(st))], "report.agent_judgment.contract_verification.verdicts[].status")
    stv = [v for v in vs if v.get("status") == "STALE"]
    add(s, "STALE 项唯一=ECB_DFR token 2.5%", ["ECB_DFR", "2.5%"], [stv[0].get("metric"), stv[0].get("token")] if len(stv) == 1 else None, "contract_verification.verdicts[status=STALE]")
    if stv:
        add(s, "STALE 项 value=expected=2.5=序列末观测值(数值无误,状态仅因序列陈旧)", [True, True], [stv[0].get("value") == stv[0].get("expected"), F(V("ECB_DFR", S(ser("ECB_DFR")[-1][0])), 1) == stv[0].get("expected")], "series_store.ECB_DFR@" + S(ser("ECB_DFR")[-1][0]) + "=" + repr(V("ECB_DFR", S(ser("ECB_DFR")[-1][0]))))
    for v in vs:
        mid = v.get("metric")
        r_ = l1row(mid)
        add(s, "契约 token %s %s=序列末观测值(按 L1 位数取整)" % (mid, v.get("token")), v.get("value"), F(V(mid, S(ser(mid)[-1][0])), _nd(r_["value"])) if r_ else None, "series_store.%s@%s=%r" % (mid, S(ser(mid)[-1][0]), V(mid, S(ser(mid)[-1][0]))))
    sc = cv.get("six_checks") or []
    add(s, "六查 16 条全 VERIFIED", [16, 0], [len(sc), len([x for x in sc if x.get("status") != "VERIFIED"])], "contract_verification.six_checks")
    add(s, "六查覆盖 3 条矛盾陈述×4 查(relevant/supports/competing/opposing)=12", 12, len([x for x in sc if x.get("check") in ("relevant", "supports", "competing", "opposing")]), "contract_verification.six_checks")
    add(s, "六查覆盖 2 情景×2 查(overreach/falsifiable)=4", 4, len([x for x in sc if x.get("check") in ("overreach", "falsifiable")]), "contract_verification.six_checks")
    mcp = cv.get("map_checks") or []
    add(s, "读者面核验 5 条全 VERIFIED", [5, 0], [len(mcp), len([x for x in mcp if x.get("status") != "VERIFIED"])], "contract_verification.map_checks")
    sts = cv.get("stats") or {}
    add(s, "stats: checks 5/contradicted 0/verified 4/unbound 0/six_fail 0/map_fail 0", {"checks": 5, "contradicted": 0, "verified": 4, "unbound": 0, "six_fail": 0, "map_fail": 0}, dict((k, sts.get(k)) for k in ("checks", "contradicted", 0, "six_fail", "map_fail")), "contract_verification.stats")
    add(s, "契约总体 verdict=VERIFIED 且 unresolved_unbound 为空", ["VERIFIED", []], [cv.get("verdict"), cv.get("unresolved_unbound")], "contract_verification")
    add(s, "判断档未点名契约 STALE 一项(全文「STALE」计数=0);实质披露在文: ECB 序列 L1=DEGRADED+超过新鲜度阈十天+【尚未验证】", [0, True, True, True],
        [T.count("STALE"), has("L1 事实行 quality_status=DEGRADED"), has("超过注册表新鲜度阈十天"), has("【尚未验证】")], "agent_judgment 全文")
    at = rep.get("agent_judgment") or {}
    add(s, "attach 校验 validation.passed=true / violations 空", [True, []], [(at.get("validation") or {}).get("passed"), (at.get("validation") or {}).get("violations")], "report.agent_judgment.validation")
    add(s, "attach 校验计数 矛盾 3/机制链 1/情景 2 = 判断档实体数", [3, 1, 2], [len(L3["contradictions"]), len(L3["mechanism_chains"]), len(L4["scenarios"])], "report.agent_judgment.validation.n_* vs agent_judgment")
    add(s, "run_ok_at_attach=true / allow_failed_run=false", [True, False], [at.get("run_ok_at_attach"), at.get("allow_failed_run")], "report.agent_judgment")
    rmf = at.get("reader_map_faces") or {}
    add(s, "reader_map_faces.complete=true, turnings_n=3=判断档 turnings 数", [True, 3], [rmf.get("complete"), len(RM["turnings"])], "report.agent_judgment.reader_map_faces vs agent_judgment.reader_map.turnings")
    add(s, "reader_map_faces.history_n=0=判断档历史类比段数", 0, rmf.get("history_n"), "report.agent_judgment.reader_map_faces")
    add(s, "判断档 schema_version=1.1 = attach schema_version", jd.get("schema_version"), at.get("schema_version"), "agent_judgment.schema_version / report.agent_judgment.schema_version")
'''))

n_bad = 0
for old, new in PAIRS:
    c = src.count(old)
    if c != 1:
        n_bad += 1
        print("BAD count", c, "for:", old[:90].replace("\n", " | "))
        continue
    src = src.replace(old, new)
if n_bad:
    print("NOT WRITTEN", n_bad)
    sys.exit(1)
open(path, "w", encoding="utf-8").write(src)
print("patched", len(PAIRS), "replacements")
