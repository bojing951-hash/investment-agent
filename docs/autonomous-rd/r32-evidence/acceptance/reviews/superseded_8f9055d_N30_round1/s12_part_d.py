# ======================================================================
# part D -- additional derived facts, counter-attacks, engine-face observations, six checks, notes
# ======================================================================
GAPM = {"2026-%02d" % i: round(VE[i] - VJ[i], 2) for i in range(5, 11)}
GAPM_MIN, GAPM_MAX = min(GAPM, key=GAPM.get), max(GAPM, key=GAPM.get)
ALT = (round(VE[10] - mo(EA, 2025, 9), 2), round(mo(JPC, 2025, 9) - VJ[10], 2))


def fxv(dct, d, k):
    """currency level with the precision the judgment itself uses (EURUSD 4 / USDJPY 3 / DXY >=2 decimals)"""
    s_ = ("%." + str(d) + "f") % dct[k]
    if dct is DXY:
        s_ = s_.rstrip("0")
        s_ += "0" * max(0, 2 - len(s_.split(".")[1]))
    return s_


def f2(v):
    return "%.2f" % v


def f3(v):
    return "%.3f" % v


def sgn(v):
    return "+" if v > 0 else ("−" if v < 0 else "")


def sg2(v):
    return sgn(v) + f2(abs(v))


def sp1(v):
    return sgn(v) + p1(abs(v))
REG_INFL = sorted(k for k in REGM if REGM[k].get("economy") in ("JP", "EA") and re.search(r"CPI|HICP", k))
sup("注册表 JP/EA 面通胀序列 = %s" % "/".join(REG_INFL), REG_INFL == ["EA_HICP_YOY", "JP_CPI_TOKYO_YOY", "JP_CPI_YOY"], REG_INFL)
sup("C1/C2 各带两条竞争解释且有【假设】标记", all(json.dumps(CON[i], ensure_ascii=False).count("【假设】") >= 2 for i in (0, 1)),
    [json.dumps(CON[i], ensure_ascii=False).count("【假设】") for i in range(3)])
sup("机制链四环证据级别 E1,E1,E2,E2 且 E2 两环带缺环注记字段 %s" % "/".join(MLN) if (MLN := [k for k in LKS[2] if "missing" in k]) else "机制链证据级别",
    [l.get("evidence_level") for l in LKS] == ["E1", "E1", "E2", "E2"] and bool(MLN) and all(k in LKS[3] for k in MLN), (MLN, [l.get("evidence_level") for l in LKS]))
REFS_ALL = [r for c in CON for r in c.get("evidence_refs", [])] + [r for l in LKS for r in l.get("evidence_refs", [])]
N_REF = [len(c.get("evidence_refs", [])) for c in CON] + [len(l.get("evidence_refs", [])) for l in LKS]
REF_D = sorted(set(re.findall(r"@(\d{4}-\d\d-\d\d)", "\n".join(REFS_ALL))))
sup("矛盾陈述与机制链引用 %s=%d 条全部在证据索引,观测日全部不晚于截止日" % ("+".join(str(x) for x in N_REF), len(REFS_ALL)),
    all(r in EIDX_REFS for r in REFS_ALL) and len(REFS_ALL) == 21 and bool(REF_D) and max(REF_D) <= CUTOFF, (N_REF, REF_D))
WMM_LEAF = [(p, v) for p, v in LV if isinstance(v, str) and "维持不变" in v]
WMM = [(jpath(p), v[max(0, v.find("维持不变") - 24):v.find("维持不变") + 12]) for p, v in WMM_LEAF]
sup("「维持不变」%d 处均在含 2026-10-30 的叶子(日央行确认维持)或 l4 情景内" % len(WMM), all(("2026-10-30" in v or p[0] == "l4") for p, v in WMM_LEAF), WMM)
PLAN_PUB = set(str(v.get("publication_date")) for c in RP["point_values"]["cells"] for v in c["anchors"].values())
WK = []
for c in RP["point_values"]["cells"]:
    for a, v in c["anchors"].items():
        if str(v.get("publication_date") or "") >= "2025-01-01" and D(str(v.get("publication_date"))).weekday() >= 5:
            WK.append(c["metric_id"] + "/" + a + "@" + str(v.get("publication_date")))
RPTXT = json.dumps(RP, ensure_ascii=False)
RP_WK = sorted(set(d for d in re.findall(r"20\d\d-\d\d-\d\d", RPTXT) if "2025-06-01" <= d <= CUTOFF and D(d).weekday() >= 5))
CITED = sorted(set(re.findall(r"2026-\d\d-\d\d", "\n".join(v for p, v in LV if isinstance(v, str) and p[0] != "agent_declaration"))))
CITED_PUB = [d for d in CITED if d in PLAN_PUB]
CITED_WK = [d for d in CITED if D(d).weekday() >= 5 and d != CALE.get("updated")]
WKD = {d: ("周六" if D(d).weekday() == 5 else "周日") for d in CITED_WK}
sup("判断档正文落周末的日期记号 %d 个(日历版本日 %s 除外): 窗起日 2026-05-23(%s,六个月窗起点)、欧元区 2026-04 期推定发布日 2026-05-16(%s,句中未点明)、东京都 2026-08 期推定发布日 2026-08-30(%s,句中已点明);"
    "研究计划点值格推定发布日落周末者 %d 个(%s);研究计划 2025-06 以来落周末的日期记号 %d 个(%s)" % (
    len(CITED_WK), CALE.get("updated"), WKD.get("2026-05-23"), WKD.get("2026-05-16"), WKD.get("2026-08-30"), len(WK), ";".join(WK), len(RP_WK), ",".join(RP_WK)),
    CITED_WK == ["2026-05-16", "2026-05-23", "2026-08-30"] and WK == ["EA_HICP_YOY/6个月前@2026-05-16"] and "2026-05-16" in PLAN_PUB
    and all(D(d).weekday() >= 5 for d in CITED_WK + RP_WK) and "该推定日落在周日" in JALL and "2026-05-23" in RPTXT, (WK, RP_WK, CITED_WK))
sup("引擎聚簇面: POLCLUSTER-02 记为单地区事件", "POLCLUSTER-02" in RPTXT and '"same_event_cross_country": false' in RPTXT)
sup("东京都 CPI 两锚格在研究计划内 status=ok;月均锚格 vintage 与东京同为采集时点值",
    all(CELLS["JP_CPI_TOKYO_YOY"]["anchors"][a]["status"] == "ok" for a in CELLS["JP_CPI_TOKYO_YOY"]["anchors"])
    and CELLS["JP_POLICY_RATE"]["anchors"]["最新一期"]["vintage"] == Q_VINT_COL and CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["vintage"] == CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["vintage"] == Q_VINT_RET)
L_MISS = line_of(MAPL, "缺数格说明")
L_JPT = line_of(MAPL, "JP_POLICY_TARGET")
sup("MAP 覆盖句/缺数格说明/口径行/周三注记/对质表标题各在场", all(len(x) == 1 for x in (L_COV, L_WED, L_FOH, L_KOU, L_HEAD)) and len(L_MISS) >= 1 and len(L_JPT) >= 1,
    (L_COV, L_WED, L_FOH, L_KOU, L_HEAD, L_MISS, L_JPT))
REG_YIELDS = sorted(k for k in REGM if re.search(r"JGB|BUND", k))
sup("series_store 无 JGB/BUND 序列;注册表列有 %s;快照事实行有 JGB 三期限、无 BUND" % "/".join(REG_YIELDS),
    bool(REG_YIELDS) and not [k for k in SS if re.search(r"JGB|BUND", k)] and not [k for k in FACTS if "BUND" in k], (REG_YIELDS,))
NEXT_REL = {"EA_HICP_YOY": (dt.date(2026, 11, 30) + dt.timedelta(days=16)).isoformat(), "JP_CPI_YOY": (dt.date(2026, 11, 30) + dt.timedelta(days=20)).isoformat()}
sup("2026-11 期读数按引擎规则入档日 %s/%s 晚于截止日且未被判断档引用" % (NEXT_REL["EA_HICP_YOY"], NEXT_REL["JP_CPI_YOY"]),
    NEXT_REL["EA_HICP_YOY"] == "2026-12-16" and NEXT_REL["JP_CPI_YOY"] == "2026-12-20" and all(v not in JALL for v in NEXT_REL.values()), NEXT_REL)
WR_UTC = WR.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
ENG_TXT = "三项均属实(第 9 节 E8/E11)" if (ENG_ON and all(ENG_CHK.values())) else "本席未能全部核实(第 9 节 E8/E11)"

# --------------------------------------------------------------------------- counter-attacks (protocol section 4)
ATTACKS = [
    ("C1 分化", "换起点重算两地动量排序,检验「窗内动量相近」是否为挑选起点所致",
     "锚格期 2026-04→2026-10: 欧元区 " + sp1(D04[0]) + " 对日本 " + sp1(D04[1]) + " 个百分点;自 2026-05: " + sp1(D05[0]) + " 对 " + sp1(D05[1]) +
     ";自 2026-06: " + sp1(D06[0]) + " 对 " + sp1(D06[1]) + "(series_store.EA_HICP_YOY / JP_CPI_YOY 各月值)。排序随起点互换,判断档同句已列三组并自陈快慢互换。未找到反例"),
    ("C1 日本读数", "东京都读数是否被用来补全国口径之缺或与全国口径混用",
     "两口径分列: 2026-09 期对欧元区水平差 全国口径 " + sg2(SEPJ) + "(2.16−3.8)、东京口径 " + sg2(SEPT) + "(2.69−3.8)直算一致;东京序列 Gate A 列 noncore_missing、L1 无事实行已披露。未找到反例"),
    ("C1 同比基期", "同比基期是否用了相邻月,或缺基期仍给出同比",
     "欧元区基期 2025-10 期=" + n(mo(EA, 2025, 10)) + "、日本 2025-10 期=" + n(mo(JPC, 2025, 10)) + ",均为去年同月直算(同比对照 " + sp1(YEA) + "、" + sp1(-YJP) +
     " 个百分点);若以 2025-09 期为基则为 " + sg(ALT[0]) + "、" + sg(-ALT[1]) + ",与文中数字不符,可排除。东京都序列去年同月不在序列内,判断档未给东京都同比。未找到反例"),
    ("C1 竞争解释", "两条竞争解释是否同义反复或稻草人",
     "一为剪刀差收敛(高基数消退),一为持续分化(需求与政策组合驱动),对两地水平差的预言方向相反,C1 条目内「【假设】」标记出现 " + str(json.dumps(CON[0], ensure_ascii=False).count("【假设】")) +
     " 次,并写明不可在引擎面验证的依据(注册表 JP/EA 面通胀序列仅 " + "/".join(REG_INFL) + ")。真竞争"),
    ("C2 口径", "日本「收紧」是否以市场月均冒充宣布值",
     "分列月均≠宣布值并标【推断】;宣布值 1.25 单列(release_calendar RC-JP-BOJ-TARGET-2026-09: decision_date " + JPT["decision_date"] + "、effective_on " + JPT["effective_on"] +
     "、target_value " + n(JPT["target_value"]) + ")。未找到冒充"),
    ("C2 幅度", "「累计幅度相近」是否把不同口径直接相加",
     "已注口径不同仅作量级对照;欧央行 +50bp 为宣布值口径直算(MRO 2.15→2.65、DFR 2.0→2.5),日本 +50bp 为月均锚间直算(1.227−0.727=0.5 个百分点)。未找到反例"),
    ("C2 时序", "「相隔八天」是否有日级时间分辨率支撑",
     "生效日对生效日 2026-09-16→" + JPT["effective_on"] + "=" + str(DD["d8a"]) + " 天(序列变更日与日历 effective_on),回推决议日 2026-09-10→" + JPT["decision_date"] + "=" + str(DD["d8b"]) +
     " 天;判断档限同口径并声明月频分辨率下先后未定,与引擎聚簇面(POLCLUSTER-02 单地区事件,same_event_cross_country=false)一致。未找到反例"),
    ("C2 回推日", "引擎回推的欧央行决议日是否被当作事实",
     "全文两决议日共 " + str(N_OCC) + " 处出现,所在句均带 回推/惯例/推断 标注(生成器内复核),并声明不参与排序。未找到反例(注册表口径与引擎惯例不一未明示,记 MINOR-6)"),
    ("C2 事后信息", "截止日之后的信息是否被引用",
     "三条矛盾陈述与机制链四环的全部证据引用(" + "+".join(str(x) for x in N_REF) + "=" + str(len(REFS_ALL)) + " 条)观测日均不晚于 " + CUTOFF + ";正文(声明部分除外)晚于截止日的日期记号仅 " + "、".join(LATE) +
     "(问句请求的月末与情景时限);2026-11 期通胀读数按引擎规则须待 " + NEXT_REL["EA_HICP_YOY"] + "(欧元区)/" + NEXT_REL["JP_CPI_YOY"] + "(日本)入档,未被引用。未找到反例"),
    ("C3 真缺", "所列缺口是否真缺(有无序列在册而被称缺席)",
     "JP_POLICY_TARGET 不在注册表与 series_store;ECB 两序列末观测 " + LAST_MRO + ";日历无 ECB 条目;GDP 两序列在 gate_a.noncore_missing(快照事实行缺席;序列面 2026-07 期值 " + n(mo(GEA, 2026, 7)) + "/" + n(mo(GJP, 2026, 7)) +
     " 在场)。五项属实"),
    ("C3 缺席措辞", "有无把缺席写成「无变化」",
     "全文「无变化」出现 0 次;「维持不变」" + str(len(WMM)) + " 处,均在日央行 2026-10-30 确认维持(日历条目 RC-JP-BOJ-MAINT-2026-10)或 S2 情景假设的语境,不是对缺席数据的填值。未找到反例"),
    ("C3 天数", "「六十八天」「十天阈」是否算错",
     "2026-11-23−2026-09-16=" + str(DD["d68"]) + " 天;注册表 freshness.max_calendar_lag_days=10。属实"),
    ("C3 引擎缺口", "判断档是否把契约核验/别名表/历史视图三项引擎缺口写成数据缺口,或据此免于核验",
     "三项写在 quality_gate_notes 末条并标为引擎缺口披露(非本档判断问题),与 C3 五项证据缺口分列;本席只读检索引擎源码," + ENG_TXT + ";受其影响的数值本席已逐一直算(第 4 节)。未找到反例"),
    ("M1 环1", "12 个月度路径值与水平差区间是否算错",
     "12 值逐一直算一致;窗内(2026-05..2026-10)逐月水平差最小 " + n(GAPM[GAPM_MIN]) + "(" + GAPM_MIN + " 期)、最大 " + n(GAPM[GAPM_MAX]) + "(" + GAPM_MAX + " 期)。未找到反例"),
    ("M1 环2", "「合计 +50bp」是否算错",
     "四台阶 " + "+".join(n(x) for x in STEP_BP) + "=" + n(SUM_BP) + "bp,锚间净 " + n(ANCH_BP) + "bp;整数 bp 取整后均为 50。成立(取整差异不入问题清单)"),
    ("M1 环3", "主解释「方向分立」被观测否定后是否被写成支持",
     "观测为两货币同对美元走弱(EURUSD " + sg2(chg(EUR, W0, W1)) + "%、USDJPY " + sg2(chg(JPY, W0, W1)) + "%);判断档写明该预期未纳入美元端利率、两解释在该观测上预期未分立、尚不能区分。未把反证写成支持;main_predicts 措辞未加限定,记 MINOR-5"),
    ("M1 环3", "EURUSD×USDJPY 合成值是否算错",
     "1.1221×156.494、1.0970×159.707、1.0940×159.347 直算 " + n(EJ_(W0)) + "/" + n(EJ_(W1)) + "/" + n(EJ_(CUTOFF)) + ",与判断档一致(" +
     sg2(chg({"a": EJ_(W0), "b": EJ_(W1)}, "a", "b")) + "%/" + sg2(chg({"a": EJ_(W0), "b": EJ_(CUTOFF)}, "a", "b")) + "%)。未找到反例"),
    ("M1 环4", "「VIX +84.5%」「-24.7%」的舍入",
     "35.89/19.45−1=" + sg2(chg(VIX, W0, W1)) + "%;27.01/35.89−1=" + sg2(chg(VIX, W1, CUTOFF)) + "%;判断档一位小数舍入正确(二路脚本首跑的 3 点偏离即由本席比对参数误报,已核)。未找到反例"),
    ("M1 环4", "「为窗内两个最大单日跳升日」在月窗口径下是否成立",
     "月窗(2026-10-23→2026-11-20)内最大单日跳升为 " + TOP_MONTH[0] + "(+" + n(VDPCT[TOP_MONTH[0]]) + "%);该短语仅在跳升窗(2026-11-13→2026-11-20)口径成立。记 NIT-1"),
    ("M1 环4", "「快速回落」是否被当作裁定依据",
     "仅一个盘中观测(2026-11-23 盘中 27.01,较 2026-11-20 收盘 35.89 低 " + n(-chg(VIX, W1, CUTOFF)) + "%);判断档写不足以裁定。未找到反例"),
    ("l4 情景", "触发条件是否已被触发、前提是否已被证伪",
     "S1/S2 触发均需 2026-11 或 2026-12 观测月读数(尚未发布);截止日读数(欧元区 " + p1(VE[10]) + "/日本 " + p1(VJ[10]) + "/水平差 " + f2(GAP10) + ")与 S1 前提相容,与 S2 前提方向相反,S2 自标并列反例情景。未找到反例"),
    ("l4 情景", "期限 2027-02-15 是否早于读数可入档日,证伪条件是否可观测",
     "2026-12 期按引擎规则入档日: 欧元区 " + ENTRY["EA_HICP_YOY"] + "(月末+16)、日本 " + ENTRY["JP_CPI_YOY"] + "(月末+20),均早于 " + S1R["trigger"]["deadline"] +
     ";证伪指标 EA_HICP_YOY/JP_CPI_YOY 与触发分量 VIX 均在册。可观测"),
    ("l4 情景", "两情景阈值之间是否存在既不触发也不证伪的区间而未披露",
     "存在且部分未披露: VIX 收盘在 25–30 之间时两情景均不触发;S1 触发阈 4.0% 高于前提水平 3.5%,3.5%–4.0% 区间同属前提成立而不触发;判断档只披露了 S2 的 3.0%–3.5% 区间。不改变结论,记 NIT-7"),
    ("l4 历史类比", "「历史类比 0 段」是否与引擎 analog 面矛盾,有无同步性主张与引擎同步面冲突",
     "S6_analog 已执行(扫描 " + str(S6["candidates"]["scanned"]) + "、有效 " + str(S6["candidates"]["valid"]) + "、TOP1 " + S6["top"][0]["candidate_month"] + " 距离 " + str(S6["top"][0]["distance"]) + "),与判断档所引一致;"
     "判断档无跨地区同步/相关性系数主张;引擎地区×维度同步面 S5_compare 两侧=EA_HICP_YOY×ECB_MRO(月格对齐,变化对 " + str(S5["alignment"]["n_change_pairs"]) + " 对),与判断档「同月/先后未定」类表述无冲突。未找到反例"),
    ("契约", "契约验证的非 VERIFIED 项是否已实质披露",
     "契约 " + str(len(CV["verdicts"])) + " 个数值串中 " + str(len(CVNV)) + " 个 STALE(C2 的 " + CVNV[0]["token"] + ",值=期望值;引擎注记: " + Q_ENG_STALE + ");C3 第二项、headline、quality_gate_notes 披露序列止于 " + LAST_MRO +
     "、" + str(DD["d68"]) + " 天、Gate A 降级。实质披露在场(未点名状态词,记 NIT-2)"),
    ("时点", "截止日当日值是否被写成收盘",
     "明写均为 2026-11-23 盘中快照、非收盘价;快照 research_as_of=" + RA + "。相容"),
    ("版本一致", "report.json 内嵌 agent_judgment 的正文五键为 null,受审稿是否可能不是挂接时的版本",
     "运行目录内无 " + str(EJ.get("judgment_file")) + ",字节同一性在边界内不可核(列第 10 节)。间接证据一致: 挂接元数据(attached_at=" + str(EJ.get("attached_at")) + ")、validation 计数(" +
     "/".join(str(x) for x in (EJ["validation"]["n_contradictions"], EJ["validation"]["n_mechanism_chains"], EJ["validation"]["n_scenarios"])) + ")与受审稿结构一致,契约 " + str(len(CV["verdicts"])) +
     " 个数值串与 map_checks 的传导链 id、日期次序主张、转折指标来源均在受审稿内命中,书写时刻(" + WR_UTC + ")早于挂接时刻。未发现版本不一致的证据"),
    ("读者报告", "读者报告渲染是否忠实于判断档",
     "判断档字符串叶(len≥12)逐字渲染 MAP " + str(MAP_FOUND) + "/" + str(N_LV) + "、FULL " + str(FULL_FOUND) + "/" + str(N_LV) +
     ";verdict_note、turnings narrative、quality_gate_notes、agent_declaration 两报告均未渲染。不改变数值对错,裁定理由对读者不可见(记 MINOR-5 与第 9 节 E3)"),
    ("发布日", "引擎推定发布日落周末时判断档是否照引",
     "研究计划点值格的推定发布日中落周末者 " + str(len(WK)) + " 个(" + "、".join(WK) + ");判断档正文引用且见于点值格的日期为 " + "、".join(CITED_PUB) + ";正文落周末的日期记号 " + str(len(CITED_WK)) + " 个(" + "、".join(CITED_WK) + "): "
     "窗起日 2026-05-23 为六个月窗起点,东京都 2026-08 期推定日 2026-08-30 句中已点明落在周日;唯欧元区 2026-04 期推定日 2026-05-16 落在周六而句中未点明(已标引擎推定规则、非日历实录,不改变任何取值)。记 MINOR-8"),
]
N_ATT = len(ATTACKS)
assert N_ATT == 29

# --------------------------------------------------------------------------- engine-face observations (not counted)
ENG_OBS = [
    "E1 事实性文字: MAP_REPORT.md 第 %d 行引擎注记称「%s」为全称主张——序列面 %s 年共有 %d 个非周三观测日(2015 年以来 %d 个);本窗三个观测日(2025-06-11、2026-06-17、2026-09-16)均为周三。"
    "判断档未沿用该全称主张(全文「全为周三」出现 0 次)。" % (L_WED[0], Q_MAP_WED, "/".join(NONWED_YEARS), len(NONWED), len(NONWED_2015)),
    "E2 标题: MAP_REPORT.md 第 %d 行「%s」用于两地区(日本×欧元区)工单,「四地三时点」为模板残留。" % (L_HEAD[0], Q_MAP_HEAD),
    "E3 渲染: MAP_REPORT.md / FULL_REPORT.md 不渲染 verdict_note、turnings[].narrative、quality_gate_notes 与 agent_declaration(判断档字符串叶逐字渲染 %d/%d、%d/%d);对质表的裁定理由因此对读者不可见。" % (
        MAP_FOUND, N_LV, FULL_FOUND, N_LV),
    "E4 标注: FULL_REPORT.md 第 %d 行「%s」——S5_compare 信封为月格对齐(alignment.mode=%s,n_change_pairs=%d,change_basis=%s/%s),「日收益×日变化」标注与面对象不符。" % (
        L_PEAR[0], Q_FULL_PEAR, S5["alignment"]["mode"], S5["alignment"]["n_change_pairs"], S5["change_basis"]["a"], S5["change_basis"]["b"]),
    "E5 规则标签: MAP_REPORT.md 第 %s 行「%s」自身不一致(中旬 对 当月末);注册表为「%s」;%s。" % (
        "/".join(str(x) for x in L_TK), Q_MAP_TOKYO, Q_REG_TKREL,
        ("研究计划内另有落周末的日期记号 %s" % "、".join(RP_WK)) if RP_WK else "研究计划内无落周末的日期记号"),
    "E6 口径不一: ECB_MRO/ECB_DFR 在引擎各面状态不同——研究计划点值格「最新一期」status=ok(freshness_basis=policy_confirmation)/快照 Gate A 与 L1 事实行=DEGRADED(%s)/"
    "run.data_requirements=insufficient_coverage(按日频族下界: 窗内有效观测 2<66、相邻断档 91 天>30 天,套用于决策驱动型序列)/契约验证=STALE;MAP_REPORT.md 第 %d 行「%s」,第 %d 行起的缺数格说明仅列 JP_POLICY_TARGET%s。" % (
        Q_SNAP_ISSUE, L_COV[0], Q_MAP_COV, L_MISS[0],
        (";东京都 CPI 两格在表内显示 ok(第 %s 行;Gate A 列 noncore_missing)" % "/".join(str(x) for x in L_TKROW)) if len(L_TKROW) >= 2 else ""),
    "E7 口径不一: 注册表 ECB_MRO release_semantics(「%s」)与 calc(「%s」)对规划器惯例(点值格 policy_dates.decision_note=「%s」;publication_rule=「%s」)。" % (
        Q_REG_ECBREL, Q_REG_ECBCALC, Q_ENG_DECNOTE, Q_ENG_PUBRULE),
    "E8 契约覆盖(判断档 quality_gate_notes 末条①②已披露;本席只读检索引擎源码: %s): judgment_contract._map_checks 锚标签硬编码「12个月前/3个月前/最新一期」;"
    "text_consistency.ALIASES 未覆盖 JP_CPI_YOY/EA_HICP_YOY/JP_CPI_TOKYO_YOY/JP_POLICY_TARGET/ECB_MRO——这些指标的数值不在契约逐位核验内(本席已对判断档所引全部此类数值直算,见第 4 节)。" % (
        "两项属实" if (ENG_ON and ENG_CHK["E8 契约锚标签硬编码"] and ENG_CHK["E8 别名表未覆盖五指标"]) else "未能核实"),
    "E9 单位措辞: MAP_REPORT.md 第 %d 行「%s」对同比率变动使用 bp。" % (L_BP[0], Q_MAP_BP),
    "E10 文本滞后: 注册表 JP_CPI_YOY.calc 载「%s」,序列面已有 2026-10 期(series_store.JP_CPI_YOY@2026-10-01=%s)。" % (Q_REG_JPCOV, n(VJ[10])),
    "E11 视图口径(判断档 quality_gate_notes 末条③已披露;本席只读检索: %s): 历史截止视图下点值格按发布规则判可见(research_map_planner._hist_region_reading 经 _aof_first_pub)而序列路径取快照在场(_hist_series),"
    "两入口分立;本席未逐路径复算。本工单 run.evidence_gate.historical_view=%s,不属历史视图,未影响本稿。" % (
        "入口函数属实" if (ENG_ON and ENG_CHK["E11 历史截止视图两入口"]) else "未能核实", R["run"]["evidence_gate"].get("historical_view")),
    "E12 版本可追溯性: report.json 内嵌 agent_judgment 的正文五键(agent_declaration/l3/l4/reader_map/quality_gate_notes)均为 null,只存挂接元数据与契约验证;挂接元数据指向 %s,该文件不在运行目录内。"
    "只读 report.json 的读者看不到判断档正文,也无法在运行目录内核对挂接版本与受审稿的字节同一性。" % EJ.get("judgment_file"),
    "E13 表格注记: MAP_REPORT.md 第 %s 行为欧央行两序列的「6个月前」行(决议日 %s),随行印出的是「%s」——该注记是点值格 policy_dates 的静态字段,两个锚共用同一句,"
    "对 2025-06-05 的决议并不适用。" % ("/".join(str(x) for x in L_6M), CELLS["ECB_MRO"]["anchors"]["6个月前"]["policy_dates"]["decision"], Q_ENG_DECNOTE),
]
assert len(ENG_OBS) == 13

# --------------------------------------------------------------------------- six checks (protocol section 4)
SIX = [
    ("C1 分化陈述——最新读数水平分化、同比对照方向相反;窗内动量相近", [
        "- 证据相关性: 相干。evidence_refs %d 条(%s)均在证据索引。陈述内全部数值直算一致: 水平差 %s−%s=%s;同比对照欧元区 %s、日本 %s;锚间 %s 对 %s;自 2026-06 %s 对 %s;自 2026-05 %s 对 %s;"
        "两序列最新期推定发布日 %s 与 %s 相差 %d 天(引擎规则 月末+16 / 月末+20)。" % (
            N_REF[0], "、".join(CON[0]["evidence_refs"]), p1(VE[10]), p1(VJ[10]), f2(GAP10), sp1(YEA), sp1(-YJP), sp1(D04[0]), sp1(D04[1]), sp1(D06[0]), sp1(D06[1]), sp1(D05[0]), sp1(D05[1]),
            CELLS["EA_HICP_YOY"]["anchors"]["最新一期"]["publication_date"], CELLS["JP_CPI_YOY"]["anchors"]["最新一期"]["publication_date"], D4 if (D4 := days("2026-11-16", "2026-11-20")) else 0),
        "- 支持度: 水平与同比方向分化为事实位且有数;「窗内动量相近」是定性措辞、依赖起点,陈述同句列出三组起点并自陈快慢互换,措辞强度未超过证据。",
        "- 竞争解释: 两条方向真对立(高基数消退→剪刀差收敛 / 需求与政策组合驱动→持续分化),均带【假设】标记,并写明不可在引擎面验证的依据(注册表 JP/EA 面通胀序列仅 " + "/".join(REG_INFL) + ")。非稻草人。",
        "- 反对证据: 东京都序列 noncore_missing、L1 无事实行、去年同月读数不在序列内无法做同比方向对照,均已披露;两条最新读数的 L1 行 quality_status=%s/%s。未见未披露的反向事实。" % (
            FACTS["JP_CPI_YOY@2026-10-01"]["quality_status"], FACTS["EA_HICP_YOY@2026-10-01"]["quality_status"]),
        "- 结论是否超出证据: 未超出。",
        "- 证伪条件可观测性: 两解释对两地水平差的预言方向不同(收敛 / 维持或扩大),落在 EA_HICP_YOY、JP_CPI_YOY 两条在册序列上;l4 S1/S2 的证伪阈值(1.5/1.0 个百分点)与前提水平(3.5%/2.0%/3.0%)可观测。可观测。",
    ]),
    ("C2 政策面陈述——同向收紧、累计幅度相近,水平分化,口径基础不对称", [
        "- 证据相关性: evidence_refs %d 条全部解析。数值直算一致: ECB_MRO %s→%s→%s;ECB_DFR %s→%s→%s;JP_POLICY_RATE 2026-04=%s、2026-10=%s、2025-11=%s;USDJPY@2026-11-23=%s;SPX@2026-11-23=%s;VIX@2026-11-23=%s;"
        "日历 RC-JP-BOJ-TARGET-2026-09(decision_date=%s,effective_on=%s,target_value=%s,basis=%s)、RC-JP-BOJ-MAINT-2026-10(decision_date=%s,kind=%s)。" % (
            N_REF[1], f2(MRO["2025-06-11"]), f2(MRO["2026-06-17"]), f2(MRO["2026-09-16"]), f2(DFR["2025-06-11"]), f2(DFR["2026-06-17"]), f2(DFR["2026-09-16"]), f3(mo(JPR, 2026, 4)), f3(mo(JPR, 2026, 10)), f3(mo(JPR, 2025, 11)),
            "%.3f" % JPY[CUTOFF], "%.2f" % SPX[CUTOFF], "%.2f" % VIX[CUTOFF], JPT["decision_date"], JPT["effective_on"], f2(JPT["target_value"]), JPT["basis"], JPM["decision_date"], JPM["kind"]),
        "- 支持度: 欧央行端为 E1(两个 25bp 变更日直算,间隔 %d 天,此前持平 %d 天)。日本端收紧依据月均市场利率台阶与日历目标值,宣布值无前值可比——已标【推断】;累计幅度相近注明口径不同仅作量级对照。相称。" % (DD["d91"], DD["d371"]),
        "- 竞争解释: 读数驱动 vs 正常化程序/汇率与金融稳定考量,真对立,均带【假设】标记;后者的不可验证依据(政策文档事实仅 FOMC 纪要一条)与 research_plan.policy_doc_facts(%d 条: %s,published_on=%s)相符。" % (
            len(RP["policy_doc_facts"]), RP["policy_doc_facts"][0]["doc_id"], RP["policy_doc_facts"][0]["published_on"]),
        "- 反对证据: 日本宣布值前值缺席(日历仅有目标值与维持两条)、ECB 序列止于 %s、月均≠宣布值——均已写明。" % LAST_MRO,
        "- 结论是否超出证据: 水平差(MRO %s−%s=%s;DFR %s−%s=%s)有数;相隔八天限生效日对生效日(%d 天)并注回推决议日口径(%d 天);月频分辨率下先后未定,与引擎聚簇面(POLCLUSTER-02 单地区事件)不冲突。未超出。" % (
            f2(MRO[LAST_MRO]), f2(TARGET), f2(MRO[LAST_MRO] - TARGET), f2(DFR[LAST_DFR]), f2(TARGET), f2(DFR[LAST_DFR] - TARGET), DD["d8a"], DD["d8b"]),
        "- 证伪条件可观测性: 两解释的区分量是后续决议节奏与读数的联动;引擎面无 ECB 实录、日本仅两条实录——判断档未对两解释作裁决,如实并列,并注明欧央行分量须待发布日历补录后方可核验。不构成以不可观测条件支撑的结论。",
    ]),
    ("C3 证据缺口陈述——证据不足五项", [
        "- 相关性与属实: ①注册表无 JP_POLICY_TARGET(research_plan.dimension_gaps 同)属实;②ECB_MRO/ECB_DFR 末观测 %s,距 %s 为 %d 天,大于注册表 freshness.max_calendar_lag_days=10,快照 facts quality_status=DEGRADED(issues.message=「%s」),"
        "gate_a.noncore_degraded 含两序列,日历无 ECB 条目——属实;③日历日欧面仅 JP_POLICY_TARGET×2、EA_HICP_YOY×3(obs_from %s),不覆盖本窗——属实;④与锚格 vintage 相容(EA_HICP_YOY、JP_CPI_YOY=「%s」;JP_CPI_TOKYO_YOY、JP_POLICY_RATE=「%s」);"
        "⑤EA_REAL_GDP_YOY、JP_REAL_GDP_YOY 在 gate_a.noncore_missing(detail 含「%s」),序列面末观测 2026-07 期=%s/%s,注册表无两地核心通胀序列——属实。" % (
            LAST_MRO, CUTOFF, DD["d68"], Q_SNAP_ISSUE, "/".join(EA_CAL), Q_VINT_RET, Q_VINT_COL, Q_DET_GDP, f2(mo(GEA, 2026, 7)), f2(mo(GJP, 2026, 7))),
        "- 支持度与结论: 缺口没有被写成「无变化」(全文 0 次);没有把序列值写成官方宣布目标(ECB_MRO 引擎面标签=「%s」,与判断档「政策目标口径」一致)。未超出。" % Q_ENG_FACE,
        "- 竞争解释: 针对第②项的两种解释(此后无新决议 / 有新决议未反映)真对立,带【假设】标记,未裁定;区分量在引擎外(官网决议记录),判断档未把引擎外信息写入。",
        "- 反对证据与遗漏: 未列日欧主权债收益率端的不对称缺席——记 MINOR-3;第②项降级归因未提引擎另一面(decision_dated 规则、点值格 ok)——记 MINOR-7。",
        "- 证伪条件: 缺口陈述不设证伪条件;不适用。",
    ]),
    ("机制链环1(通胀路径,E1)", [
        "- 证据相关性: 12 个月度值逐一直算一致;窗内各月欧元区水平高于日本,差幅最小 %s(%s 期)、最大 %s(%s 期)。E1 与序列面直读相称。" % (f2(GAPM[GAPM_MIN]), GAPM_MIN, f2(GAPM[GAPM_MAX]), GAPM_MAX),
        "- 支持度: 两地上行(欧元区 2026-06 一度回落至 %s,非逐月单调;日本 2026-05 至 2026-10 逐月上行)逐月直算属实。" % p1(VE[6]),
        "- 反对证据: 2026-06 回落已写;2026-05 期观测日在窗前已括注。",
        "- 竞争解释与证伪条件: 观察环,无因果主张;不适用。",
    ]),
    ("机制链环2(政策面,E1)", [
        "- 证据相关性: ECB 四个端点、BOJ 日历两条、JP_POLICY_RATE 四个台阶(%s)直算一致;合计 +50bp 即四台阶之和 %sbp(整数 bp 取整后 50;锚间净 %sbp)。" % (
            "、".join("%s +%sbp" % (ym, n(bp)) for (ym, _, _), bp in zip(STEPS_JP, STEP_BP)), n(SUM_BP), n(ANCH_BP)),
        "- 支持度: 相容性措辞克制(相容、不作相容性判断);E1 相称。",
        "- 竞争解释与证伪条件: 观察环;不适用。标题「政策面跟进」略带因果色彩(记 NIT-8)。",
    ]),
    ("机制链环3(汇率,E2)", [
        "- 证据相关性: 标【假设】,缺环注记字段(%s)在场;EURUSD %s→%s(%s%%)、USDJPY %s→%s(%s%%)、DXY %s→%s(%s%%);至 %s: %s(%s%%)、%s(%s%%)、%s(%s%%);EURJPY 合成 %s/%s/%s(%s%%/%s%%)——全部直算一致(汇率各日值取自快照 series_store 的 EURUSD/USDJPY/DXY;EURJPY=同日两腿相乘)。" % (
            "/".join(MLN), fxv(EUR, 4, W0), fxv(EUR, 4, W1), sg2(chg(EUR, W0, W1)), fxv(JPY, 3, W0), fxv(JPY, 3, W1), sg2(chg(JPY, W0, W1)), fxv(DXY, 3, W0), fxv(DXY, 3, W1), sg2(chg(DXY, W0, W1)), CUTOFF,
            fxv(EUR, 4, CUTOFF), sg2(chg(EUR, W0, CUTOFF)), fxv(JPY, 3, CUTOFF), sg2(chg(JPY, W0, CUTOFF)), fxv(DXY, 3, CUTOFF), sg2(chg(DXY, W0, CUTOFF)),
            n(EJ_(W0)), n(EJ_(W1)), n(EJ_(CUTOFF)), sg2(chg({"a": EJ_(W0), "b": EJ_(W1)}, "a", "b")), sg2(chg({"a": EJ_(W0), "b": EJ_(CUTOFF)}, "a", "b"))),
        "- 支持度与结论: 主解释的原始预期「方向分立」与观测不符;判断档没有把观测写成支持主解释,而是重述为纳入美元端利率后的预期并得出尚不能区分(置信有限)。未超出证据;属保守取向。",
        "- 竞争解释: 利差主导 vs 美元全局/风险情绪主导,真对立;但经重述后两者在本月窗对 EURUSD 的预期同向,本窗不具区分力——判断档如实写明。",
        "- 反对证据: 主解释预期未获支持这一点写在正文;EURJPY 交叉盘不在证据面已写,合成值标为推算。",
        "- 证伪条件可观测性: 区分指标 EURUSD 在册且在场;两解释在其上的预言方向在本窗相同(判断档自陈),本窗不可区分;判断档未明写后续可区分的条件(如美元端利率不变而两地政策差再变动)——并入 MINOR-5。",
    ]),
    ("机制链环4(资产面,E2)", [
        "- 证据相关性: 标【假设·归因】,缺环注记字段(%s)在场;SPX %s%%、NIKKEI225 %s%%、DAX %s%%、CAC40 %s%%、VIX %s→%s(+%s%%)、末六日路径、引擎回贴面(%s/%s/%s/%s)、%s(%s%%)、"
        "先例(%s→%s,+%s%%;%s,%s%%;%d 个交易日;SPX 2026-11-05 %s%%;NIKKEI225 2026-11-06 %s%%)、跳升窗四地跌幅(%s/%s/%s/%s)、两日汇率单日变动不超过 %s%%、FOMC 纪要 %s——全部直算一致。" % (
            "/".join(MLN), sg2(chg(SPX, W0, W1)), sg2(chg(NK, W0, W1)), sg2(chg(DAX, W0, W1)), sg2(chg(CAC, W0, W1)), n(VIX[W0]), n(VIX[W1]), n(chg(VIX, W0, W1)),
            sg2(chg(SPX, W0, CUTOFF)), sg2(chg(DAX, W0, CUTOFF)), sg([a for a in J["reader_map"]["asset_returns_echo"] if a["metric_id"] == "NIKKEI225"][0]["chg_pct"]), sg2(chg(VIX, W0, CUTOFF)), n(VIX[CUTOFF]), sg2(chg(VIX, W1, CUTOFF)),
            n(VIX["2026-11-04"]), n(VIX["2026-11-05"]), n(chg(VIX, "2026-11-04", "2026-11-05")), n(VIX["2026-11-11"]), sg2(chg(VIX, "2026-11-05", "2026-11-11")), N_TD,
            sg2(chg(SPX, prevd(SPX, "2026-11-05"), "2026-11-05")), sg2(chg(NK, prevd(NK, "2026-11-06"), "2026-11-06")),
            sg2(chg(SPX, "2026-11-13", W1)), sg2(chg(NK, "2026-11-13", W1)), sg2(chg(DAX, "2026-11-13", W1)), sg2(chg(CAC, "2026-11-13", W1)), "%.2f" % max(FXD), RP["policy_doc_facts"][0]["published_on"]),
        "- 支持度与结论: 不利于主解释的两点(欧元区股指不弱于美股;VIX 跳升时点不对齐政策日历)写在正文;自陈证据倾向竞争解释但不足以裁定。未超出。",
        "- 竞争解释: 紧缩+通胀粘性 vs 全局风险/流动性冲击,真对立且同证据可容纳;第三类候选(FOMC 纪要)已列、未裁。",
        "- 证伪条件可观测性: 区分指标 VIX 在册且在场;两解释对 VIX 路径的预言不同(与政策日历联动/回落缓慢 vs 独立于日历/快速回落),待收盘数据可观测。可观测。",
        "- 行文: 「为窗内两个最大单日跳升日」仅在跳升窗口径成立(记 NIT-1)。",
    ]),
    ("对质表三行(传导链 reader_map 面)", [
        "- 环1: 持平 %d 天(2025-06-11→2026-06-17)、间隔 %d 天、各 25bp、决议日前可见读数(决议日口径 %s/%s,生效日口径 %s/%s)直算一致;「尚不能区分」与 n=2 的证据强度相称。" % (
            DD["d371"], DD["d91"], p1(VE[4]), p1(VE[7]), p1(VE[5]), p1(VE[8])),
        "- 环2: 「尚不能区分」与同页观测不矛盾(经重述后两解释预期同向);main_predicts 措辞未加限定(记 MINOR-5)。",
        "- 环3: 「尚不能区分」与正文「证据倾向竞争解释」并读时表面不一致;理由(「快速回落」仅一个盘中观测)在 verdict_note,读者面不可见(记 MINOR-5)。",
    ]),
    ("历史类比与历史段同步性", [
        "- 判断档历史类比 0 段并如实说明未逐项核验候选月的事后结果;引擎 S6_analog 已执行(steps[S6_analog].envelope.data: candidates.scanned=%d、candidates.valid=%d、top[0].candidate_month=%s、distance=%s),与判断档所引数字逐项一致(见第 4 节)。" % (
            S6["candidates"]["scanned"], S6["candidates"]["valid"], S6["top"][0]["candidate_month"], S6["top"][0]["distance"]),
        "- 全文无跨地区同步/相关性系数主张(「相关系数/同步系数/pearson/皮尔逊」出现 0 次);引擎地区×维度同步面 S5_compare 两侧=EA_HICP_YOY×ECB_MRO,与判断档「同月/先后未定」类表述无冲突。无「叙述称同步而面=缺证」或「叙述与面冲突」情形。",
    ]),
]

# --------------------------------------------------------------------------- notes (goes verbatim into the verdict record)
CAT_TXT = "、".join("%s %d 点" % (CAT_NAMES[k], CAT[k]) for k in ("snap", "eng", "cal", "reg", "eidx", "txt", "date", "oth") if CAT.get(k))
assert sum(CAT.values()) == N_PTS, (sum(CAT.values()), N_PTS)
MINOR_SUM = ["ECB 序列最新水平一句未带降级限定", "日欧 CPI 同比为引擎自算口径未注明", "日欧主权债收益率缺席未列入证据缺口", "东京都转折行未随行标注 noncore_missing",
             "对质裁定理由未渲染且主解释预期措辞未加限定", "ECB 决议日回推与注册表口径不一未明示", "ECB 降级归因未提引擎另一面", "欧元区 2026-04 期推定发布日落周六未点明"]
NIT_SUM = ["「为窗内两个最大单日跳升日」的窗口径", "契约 STALE 状态词未点名", "「冻结日历实录仅覆盖」缺日欧面限定", "「决议即…生效」", "「窗内月度路径」含观测日在窗前的一期",
           "「UST_10Y 最新 5.04%」未写观测日", "情景触发/证伪空档披露不全", "环2 标题「政策面跟进」", "「中旬速报先行口径」", "「此后总体回升」未注一次小幅回落"]
assert len(MINOR_SUM) == N_MIN and len(NIT_SUM) == N_NIT
NOTES = (
    "【N30 Round-1 零上下文独立席·裁决依据】受审稿=agent_judgment.json 全文(l3 三条矛盾陈述+机制链四环、l4 两情景、reader_map、quality_gate_notes、agent_declaration)与读者报告中的判断文字,代码印章 " + GIT_HEAD + "。"
    "主复算表 " + str(N_PTS) + " 点(规程最低 " + str(S.get("minimum_required")) + "),逐点比对报告值与直算值: 命中 " + str(N_PTS - N_MIS) + "、偏离 " + str(N_MIS) + "、脚本错误 " + str(S.get("script_errors")) +
    "(定稿前共 " + str(N_RUN) + " 次运行、" + str(N_PATCH) + " 次修补;早期偏离与报错均为本席脚本侧,逐次修至零);出处构成=" + CAT_TXT + ";"
    "其中 " + str(N_BOOL) + " 点为真/假命题(由脚本内显式谓词判定),其余为值比对;另以不共享代码的二路脚本复核 " + str(I["n"]) + " 点、偏离 " + str(I["mismatch"]) + "(不重复计入)。"
    "抽核要点: ①截止日 2026-11-23 与快照 research_as_of 一致,被引观测/发布/决议/生效日无一晚于截止日;②点值锚格 " + str(SEC["B②点值锚格"]["ok"]) + " 点全中;"
    "③同比基期均为去年同月,东京都去年同月缺值如实标无法做同比方向对照,无缺基期同比、无相邻口径顶替;④政策面宣布值/市场月均/目标值三口径分记,"
    "ECB 两次 25bp(间隔 91 天、此前持平 371 天)、BOJ 决议 2026-09-18/生效 2026-09-24/目标 1.25 与冻结日历逐项一致,8 天间隔限生效日口径;"
    "⑤美国三利率分解 −8=+11−19(bp)与资产月窗全中;⑥三转折与引擎候选面一致,先后主张限月频分辨率;⑦传导链四环数字全中(E2 两环均标【假设】并带缺环注记);"
    "⑧历史类比 0 段如实,无同步性系数主张;⑨两情景触发/证伪阈值均可观测且未被截止日读数触发或证伪,读数入档日(" + ENTRY["EA_HICP_YOY"] + "/" + ENTRY["JP_CPI_YOY"] + ")早于时限 2027-02-15;"
    "⑩headline/地区行/对质表文字与数值一致;⑪五项证据缺口逐项属实,无把缺席写成无变化;⑫截止日当日值均标盘中快照;⑬契约唯一非 VERIFIED 项(C2 的 2.5% 数值串 STALE,值=期望值)实质披露在场,未点名状态词记 NIT;"
    "⑭交付门缺口披露(ECB 两序列按日频族下界判 insufficient_coverage)与序列面一致,交付门本身不在裁决范围。"
    "六查: 三条矛盾陈述与机制链四环各做一次,竞争解释均为真对立且带【假设】标记,无未披露的反向事实,无结论超出证据;证伪条件落在在册序列(EA_HICP_YOY/JP_CPI_YOY/VIX)上可观测。"
    "反方攻击 " + str(N_ATT) + " 次,未找到可成立的反例。MAJOR " + str(N_MAJ) + " 条;MINOR " + str(N_MIN) + " 条"
    "(" + "；".join(MINOR_SUM) + "),均不改结论;"
    "NIT " + str(N_NIT) + " 条(" + "；".join(NIT_SUM) + ")。另列引擎面观察 " + str(len(ENG_OBS)) + " 条于 PROSE 第 9 节,不属判断档问题、不计入。裁决 " + DECISION + "。"
)
