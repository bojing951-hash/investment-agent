#!/usr/bin/python3 -I
"""Build the two deliverables (PROSE-round1.md, VERDICT-round1.json) from the recompute ledger, the
counter-example computations, the supplementary computations and the hand-written audit findings held in
this script.

Safety rails: every quoted `original` must occur verbatim in the judgment text; the JSON must parse; every
decimal number used in the seat's own findings must trace to an OK recompute row, to supplement.json or to
counterexamples.json; outputs and scripts are scanned for vendor names (patterns assembled from code points)
and secret-like strings.

Read-only on inputs.
Args: <agent_judgment.json> <question_verbatim.txt> <run_dir> <tree_dir> <out_dir>
"""
import hashlib
import json
import os
import re
import sys

jd = json.load(open(sys.argv[1], "r", encoding="utf-8"))
QUESTION = open(sys.argv[2], "r", encoding="utf-8").read().strip()
run_dir, tree_dir, out_dir = sys.argv[3], sys.argv[4], sys.argv[5]
HERE = os.path.dirname(os.path.abspath(__file__))
MERGED = json.load(open(os.path.join(out_dir, "recompute_points.json"), "r", encoding="utf-8"))
COUNTER = json.load(open(os.path.join(out_dir, "counterexamples.json"), "r", encoding="utf-8"))
SUPP = {s["id"]: s for s in json.load(open(os.path.join(out_dir, "supplement.json"), "r", encoding="utf-8"))}
# supplementary computations quoted in the seat's own findings (every number below is read from supplement.json)
S01 = SUPP["S01"]["value"]          # metric -> [[day, prev, close, pct], ...] for 2026-11-16..2026-11-20
S02 = SUPP["S02"]["value"]          # metric -> {latest, diff_vs{1,3,6,12m}, prior_11_months_below_latest}
S03 = SUPP["S03"]["value"]          # JP_POLICY_RATE monthly steps / change points vs BOJ records
S04 = SUPP["S04"]["value"]          # synthetic EURJPY long windows + visible policy differential
S07 = SUPP["S07"]["value"]          # VIX month window at stored / displayed precision
S10 = SUPP["S10"]["value"]          # EA HICP margins behind face-off-1 observations


def day1(mid, day):
    return [x for x in S01[mid] if x[0] == day][0][3]


def dv(mid, key):
    return S02[mid]["diff_vs"][key]


def below(mid):
    return S02[mid]["prior_11_months_below_latest"][0]


_CND = "零一二三四五六七八九"


def cn_dec(x):
    """0.47 -> 零点四七 ; 1.06 -> 一点零六 (two-decimal value, statement-layer Chinese numerals)"""
    a, b = ("%.2f" % abs(x)).split(".")
    return "".join(_CND[int(c)] for c in a) + "点" + "".join(_CND[int(c)] for c in b)


assert cn_dec(0.55) == "零点五五" and cn_dec(1.9) == "一点九零" or cn_dec(1.9) == "一点九"


STEPS = S03["steps_into_month"]            # [[obs date, prev, cur, bp], ...] 2025-11..2026-10
N_DOWN = sum(1 for x in STEPS if x[3] < 0)
MIN_STEP = min(x[3] for x in STEPS)
NET_BP = sum(x[3] for x in STEPS)
STEP09 = [x for x in STEPS if x[0][:7] == "2026-09"][0][3]
STEP10 = [x for x in STEPS if x[0][:7] == "2026-10"][0][3]
ST6 = S04["start6"]
K6 = ST6 + "→2026-11-20"
X6 = S04["cross_change_%"][K6]
LEG_E, LEG_J = list(S04["legs"].values())[0], list(S04["legs"].values())[1]
PD0 = S04["visible_policy_differential"][ST6]["diff_pp"]
PD1 = S04["visible_policy_differential"]["2026-11-20"]["diff_pp"]
# direct-computed values of individual ledger rows (by id) used in the findings
ROWV = {}
for r in MERGED["rows"]:
    if isinstance(r.get("computed"), (int, float)) and not isinstance(r.get("computed"), bool):
        ROWV.setdefault(r["id"], r["computed"])
for _need in ("G076", "G077", "G078", "G079"):
    if _need not in ROWV:
        print("LEDGER ROW MISSING", _need)
        sys.exit(3)
TABLE = open(os.path.join(out_dir, "recompute_table.md"), "r", encoding="utf-8").read()
AUDITED_AT = "2026-11-24"


def walk(o, out):
    if isinstance(o, str):
        out.append(o)
    elif isinstance(o, dict):
        for v in o.values():
            walk(v, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, out)
    return out


ALLTEXT = "\n".join(walk(jd, []))


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def sha_full(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ------------------------------------------------------------------ findings
MINOR = [
    dict(severity="MINOR", tag="M-1",
         where="agent_judgment.json l3.contradictions[2].statement(C3-ECB-VISIBILITY);reader_map.regions[0].from_to(欧元区走位);quality_gate_notes[4]",
         original="观测日距研究截止 2026-11-23 六十八天,超过注册表新鲜度阈十天,当日快照 Gate A 两序列列于 degraded 名单,L1 事实行 quality_status=DEGRADED",
         note="欧央行序列时效只并列了一半口径:只引滞后口径(68 天>注册表 10 天阈→Gate A degraded/L1 DEGRADED,均属实),未并列注册表同处的决策驱动口径(metric_registry ECB_MRO/ECB_DFR.freshness.decision_dated_note:『决策驱动政策目标序列——观测日=政策最后确认/变更日;无更晚已证实决议不作过期(利率长期不变≠数据停更),有已证实更晚决议而未反映=确证过期』)与引擎点值格状态(status=ok,freshness_basis=policy_confirmation)。结论『其后是否有新决议不可判【尚未验证】』与决策驱动口径相容且偏保守,不构成数字/日期/方向错;属披露可改进(复算行 O009/O010)。",
         fix="在该句后补:『注册表对两序列另注决策驱动口径(观测日=政策最后确认/变更日,无更晚已证实决议不作过期),引擎点值格据此标 ok——两面口径并存,本档不以 degraded 推断有新决议,亦不以现值推断无新决议。』"),
    dict(severity="MINOR", tag="M-2",
         where="l3.mechanism_chains[0].links[2].text(M1 第 3 环);reader_map.transmission[0].links[1].causal_hypothesis 与 verdict_note(对质环 2)",
         original="但该预期未纳入美元端利率(UST_10Y 最新 5.04%,高于 MRO 2.65% 与 BOJ 目标约 1.25%)",
         note="两点口径问题。(i) 以 10 年期美债收益率(市场收益率口径)充当『美元端利率』与两地政策目标利率比较,口径不对等;同口径的联邦基金目标区间 3.75%–4.00%(DFEDTARL/DFEDTARU 2026-11-23 观测)只写在 verdict_note。(ii) 主解释的既述预期是『方向分立』,本月窗观测为同向;席位以『未纳入美元端利率』这一辅助前提把主解释改写成与竞争解释同向,于是本行在本月窗对两解释无检验力(窗内三地无政策利率变动点,G101)——如实,但支撑这一读法的裁定理由在三件读者报告中均未渲染(范围外观察 S-1),读者报告第 136 行『见裁定理由』成悬空指引,读者只见到对质表上『方向分立』的预期与『尚不能区分』的判断并置。定性论证在政策利率口径下同样成立(3.75–4.00 亦高于 2.65 与约 1.25),结论不变(复算行 D031/E016/G103)。",
         fix="但该预期未纳入美元端利率(快照序列面联邦基金目标区间 3.75%–4.00%,DFEDTARL/DFEDTARU 2026-11-23 观测,不在本轮证据索引;UST_10Y 最新 5.04% 为市场收益率口径),美元端政策利率亦高于 MRO 2.65% 与 BOJ 目标约 1.25%;本月窗两解释预期相同、无检验力"),
    dict(severity="MINOR", tag="M-3",
         where="l3.contradictions[0].statement(C1);reader_map.regions[0].from_to;reader_map.headline_conclusion",
         original="欧元区HICP同比最新读数百分之四点零(观测 2026-10,发布 2026-11-16,引擎推定规则、非日历实录)",
         note="问句明问『各数据的公布时间』。2026-11-16 是引擎推定规则(月末+16 天)给出的日期,注册表 release_semantics 亦写『Eurostat月度HICP(次月中旬终值)』——即该日对应终值档;冻结日历所载 EA HICP 三条实录均为两档形态(次月首日快报+月中终值: 2021-06-01/2021-06-17、2022-07-01/2022-07-19、2025-04-01/2025-04-16),据此 2026-10 读数的首发应早于 11-16。席位已标『引擎推定规则、非日历实录』并在对质环 1 裁定理由使用了两档形态(复算行 A026/G093/G094),但未在数据面与走位并列首发档。不构成日期错;属披露可改进。",
         fix="…发布 2026-11-16 为引擎推定规则下的终值日;按冻结日历所载 EA HICP 实录的两档形态(次月首日快报+月中终值),2026-10 读数首发应早于此日,非日历实录"),
    dict(severity="MINOR", tag="M-4",
         where="reader_map.headline_conclusion;reader_map.regions[1].from_to(日本走位)",
         original="两地政策利率同向收紧——日本央行政策目标 1.25%(2026-09-18 决议、2026-09-24 生效,2026-10-30 确认维持;发布日历实录)",
         note=("日央行实录无前值字段,『收紧』方向系由月均市场利率台阶推得;C2 正文已标【推断】、走位写明『月均≠宣布值』,总判断句对日本端方向未带【推断】。方向有市场口径证据(近 12 个月月均 0.478→1.227,净 +{nb:.0f}bp,{n} 个逐月台阶中仅 {nd} 次 {mn:+.1f}bp 的微降;2026-09 {s9:+.1f}bp、2026-10 {s10:+.1f}bp 与 2026-09-24 生效的上调相容;补充计算 S03),不构成方向错;属四层标注在总判断句的缺口(复算行 N007/N008/N009/N010)。"
               ).format(nb=NET_BP, n=len(STEPS), nd=N_DOWN, mn=MIN_STEP, s9=STEP09, s10=STEP10),
         fix="两地政策利率同向收紧——日本端方向为【推断】(实录无前值,依据月均市场利率台阶 0.478→1.227): 日本央行政策目标约 1.25%(2026-09-18 决议、2026-09-24 生效,2026-10-30 确认维持;发布日历实录)"),
    dict(severity="MINOR", tag="M-5",
         where="reader_map.transmission[0].links[0].main_predicts 与 verdict_note(对质环 1)",
         original="决议日(回推 2026-06-11)前可见 2026-04=3.0、生效日前可见 2026-05=3.2",
         note=("『决议日前可见读数』的数值取自快照最新修订值(引擎点值格 vintage_semantics=『事后回顾(最新修订值,非当时首发值)』;注册表 EA_HICP_YOY.release_semantics:『HICP流程对近月含回溯修订(2025-12 值1.9→2.0)…revision_semantics=latest_vintage_asof_collected』),未并列首发值口径。样本 n=2、结论为尚不能区分;『两次变更前读数均高于 2026-02 的 1.9』在决议日前/生效日前两口径下的差距为 {a1:.1f}、{a2:.1f}、{b1:.1f}、{b2:.1f} 个百分点,0.1pp 级修订不翻转;『第二次决议日前 2.9 低于 2026-05 峰值 3.2』一条差距 {pk:.1f} 个百分点,对同量级的修订敏感,但席位已自注该条对发布形态敏感(按冻结日历两档形态计则此条不成立)。属披露可改进(复算行 O014、G088–G099;补充计算 S10)。"
               ).format(a1=S10["vs_2026-02"]["2026-04"], a2=S10["vs_2026-02"]["2026-05"], b1=S10["vs_2026-02"]["2026-07"], b2=S10["vs_2026-02"]["2026-08"], pk=S10["peak_minus_2026-07"]),
         fix="决议日(回推 2026-06-11)前可见 2026-04=3.0、生效日前可见 2026-05=3.2(读数为快照最新修订值,非当时首发值;修订量级参见注册表所举 0.1pp 例)"),
    dict(severity="MINOR", tag="M-6",
         where="l3.mechanism_chains[0].links[3].text(M1 第 4 环);reader_map.transmission[0].links[2].verdict_note(对质环 3)",
         original="读数发布主因未获跨地区支持",
         note=("所据两点均属实:跳升窗(2026-11-13→2026-11-20)内累计跌幅四地均不深于美股(SPX {wsp:.2f}%、NIKKEI225 {wnk:.2f}%、DAX {wdax:.2f}%、CAC40 {wcac:.2f}%),两日欧元、日元对美元单日变动≤0.23%(最大 -0.2293%)。但未列发布日单日读数: 2026-11-20(日本 CPI 推定发布日)NIKKEI225 {nk20:+.2f}% 深于 SPX {sp20:+.2f}%、DAX {d20:+.2f}%、CAC40 {c20:+.2f}%,为窗内四地最大单日跌幅;2026-11-16(欧元区 HICP 推定发布日)欧元区股指跌幅浅于美股(DAX {d16:+.2f}%、CAC40 {c16:+.2f}% vs SPX {sp16:+.2f}%)。单日读数与全球同跌相容,既不确证也不否定发布主因;『单一归因于两地政策不可证』的结论不变。属反对证据未并列(反方攻击 10;补充计算 S01)。"
               ).format(wsp=ROWV["G076"], wnk=ROWV["G077"], wdax=ROWV["G078"], wcac=ROWV["G079"], nk20=day1("NIKKEI225", "2026-11-20"), sp20=day1("SPX", "2026-11-20"),
                        d20=day1("DAX", "2026-11-20"), c20=day1("CAC40", "2026-11-20"), d16=day1("DAX", "2026-11-16"), c16=day1("CAC40", "2026-11-16"), sp16=day1("SPX", "2026-11-16")),
         fix=("读数发布主因未获跨地区支持(按跳升窗内累计跌幅判读;单日看 2026-11-20 NIKKEI225 {nk:+.2f}% 深于 SPX {sp:+.2f}%,为窗内四地最大单日跌幅,与全局冲击相容,不足以区分发布主因与全局冲击)"
              ).format(nk=day1("NIKKEI225", "2026-11-20"), sp=day1("SPX", "2026-11-20"))),
    dict(severity="MINOR", tag="M-7",
         where="l3.mechanism_chains[0].links[2].text(M1 第 3 环);reader_map.transmission[0].links[1].verdict_note(对质环 2)",
         original="幅度小,利差渠道未获检验亦未被否定",
         note=("汇率面的检验只用一个月窗(窗起 2026-10-23),席位自注『仅一个月窗』;问句窗为最近六个月(2026-05-23 起)。本席补算: 取 2026-05-23 当日或之前的最近共同观测日 {st} 为起点,合成 EURJPY(EURUSD×USDJPY)由 {x0:.4f} 降至 2026-11-20 的 {x1:.4f}({x6:+.2f}%;腿: EURUSD {le:+.2f}%、USDJPY {lj:+.2f}%),同期可见的两地政策水平差(MRO−日本月均)为 {d0:.3f}→{d1:.3f} 个百分点(2.15−0.727 → 2.65−1.227),未变。利差假说在水平差未变时对交叉盘无趋势性预期,该读数与『利差主导』不相容;美元全局主导解释对两腿分立亦无预期——不改变『尚不能区分』,但『未被否定』只在本月窗内成立,宜并列六个月窗读数(反方攻击 9;补充计算 S04)。"
               ).format(st=ST6, x0=S04["cross"][ST6], x1=S04["cross"]["2026-11-20"], x6=X6, le=LEG_E, lj=LEG_J, d0=PD0, d1=PD1),
         fix=("幅度小;本月窗利差渠道未获检验亦未被否定。六个月窗({st}→2026-11-20)合成交叉盘 {x6:+.2f}%,同期可见的两地政策水平差 {d0:.3f}→{d1:.3f} 个百分点未变——利差渠道在六个月窗内与交叉盘读数不相容,但两种解释对该读数均无预期,仍不构成检验"
              ).format(st=ST6, x6=X6, d0=PD0, d1=PD1)),
]
NIT = [
    dict(severity="NIT", tag="N-1", where="l3.mechanism_chains[0].links[0].text(M1 第 1 环);reader_map.regions[1].from_to",
         original="自 2025-01 高点 4.03 回落",
         note="该点为近一年/局部高点(全序列最高 4.31@2023-01),宜写『近一年高点』(复算行 G006;补充计算 S08)。", fix="自 2025-01 的近一年高点 4.03 回落"),
    dict(severity="NIT", tag="N-2", where="reader_map.headline_conclusion;reader_map.regions[1].from_to(日本走位);l3.mechanism_chains[0].links[2].missing_link_note(『BOJ 目标 1.25%』)",
         original="日本央行政策目标 1.25%",
         note="发布日历两条日央行实录注记均为『约1.25%』,C2 陈述作『约一点二五』,情景文字作『目标现约 1.25%』/『目标约 1.25%』;总判断与走位省『约』(复算行 N011)。", fix="日本央行政策目标约 1.25%"),
    dict(severity="NIT", tag="N-3", where="reader_map.transmission[0].links[2].verdict_note 与 face_off_verdict(对质环 3)",
         original="证据倾向竞争解释但不足以裁定,尚不能区分",
         note="裁定词『尚不能区分』较其裁定理由(明写证据倾向竞争解释)保守;因第三类候选驱动(会议纪要发布)在场且该对质不裁、竞争解释『快速回落』预期仅有一个盘中观测,保守可接受;宜在渲染字段带倾向注记,理由文本身未渲染(范围外观察 S-1)。",
         fix="证据倾向竞争解释(会议纪要发布属第三类候选驱动、本对质不裁;『快速回落』预期仅有一个盘中观测)但不足以裁定,尚不能区分;渲染字段作『尚不能区分(证据略倾向竞争解释)』"),
    dict(severity="NIT", tag="N-4", where="l4.scenarios[0].rows.asset_direction.confidence_tier",
         original="有相关证据",
         note="所引为月窗观察(NIKKEI225@2026-11-20、VIX@2026-11-23),其归因席位自判未定;『相关』成立但不构成支持性证据(复算行 I013)。", fix="方向相容(归因未定)"),
    dict(severity="NIT", tag="N-5", where="reader_map.turnings[1].follow_or_diverge(转折 2)",
         original="跟进方向一致,月频先后未定",
         note="生效日 2026-06-17 晚于转折段终点月 2026-05,先后已定;『先后未定』只指读数可见性与决议时点,措辞可更精确(复算行 F034)。", fix="生效日 2026-06-17 晚于转折段终点,跟进方向一致;读数可见性与决议时点的先后未定"),
    dict(severity="NIT", tag="N-6", where="l3.contradictions[0].statement;reader_map.regions[1].from_to(东京都 CPI)",
         original="点值取自快照序列面、L1 无对应事实行",
         note="Gate A noncore_missing 序列的两点值作为契约锚回声进入 C1 与日本走位,状态已在原处披露且未进入总判断;宜加『参考值』字样(复算行 K001–K003)。", fix="…点值取自快照序列面、仅作参考,L1 无对应事实行"),
    dict(severity="NIT", tag="N-7", where="l3.contradictions[1].statement(C2);quality_gate_notes[4]",
         original="市场口径无担保隔夜拆借利率(月均,JP_POLICY_RATE)最新一期报 1.227%",
         note="该序列 L1 quality_status=WARN(发布时间未验证)及其推定发布日 2026-11-05(读者报告第 42 行有)未进入判断档正文;C1 只并列了两条通胀序列的 WARN(复算行 A020/K005/K006;补充计算 S09)。",
         fix="…最新一期报 1.227%(观测月 2026-10,推定发布日 2026-11-05,L1 quality_status=WARN: 发布时间未验证)"),
    dict(severity="NIT", tag="N-8", where="quality_gate_notes[5] 第②项",
         original="本档陈述层对无别名指标的数值一律用中文数字表述",
         note="成立于三条矛盾陈述正文;竞争解释、走位、机制链、对质表仍用阿拉伯数字(契约因此未逐位核验),本席已在 ⑦⑩ 逐数复算全中;自述宜写明仅限矛盾陈述正文(复算行 O007/O008)。", fix="本档三条矛盾陈述正文对无别名指标的数值一律用中文数字表述"),
    dict(severity="NIT", tag="N-9", where="l3.contradictions[0].statement(C1)",
         original="回落约零点五五个百分点",
         note=("同比回落只对去年同月成立: 近 12 个月中其余 11 个月里有 {b} 个月读数低于最新值,较 1/3/6 个月前为 {a:+.2f}/{b3:+.2f}/{c:+.2f};走位已有『此后总体回升』,可在 C1 补半句免读者误读为趋势下行(反方攻击 1;补充计算 S02)。"
               ).format(b=below("JP_CPI_YOY").split("/")[0], a=dv("JP_CPI_YOY", "2026-09"), b3=dv("JP_CPI_YOY", "2026-07"), c=dv("JP_CPI_YOY", "2026-04")),
         fix=("回落约零点五五个百分点(仅就去年同月基期而言;较六个月前则回升约{c6}个百分点)"
              ).format(c6=cn_dec(dv("JP_CPI_YOY", "2026-04")))),
]
ITEMS = MINOR + NIT

ATTACKS = [
    ("反方攻击 1(C1): 换比较基期看方向是否翻转 → 日本全国 CPI 同比较 1/3/6 个月前为 {a:+.2f}/{b:+.2f}/{c:+.2f},仅同比口径为 {d:+.2f};近 12 个月中 {jb} 个月读数低于最新值(欧元区同法 {e:+.1f}/{f:+.1f}/{g:+.1f}/{h:+.1f},{eb} 个月全部低于最新值)。陈述以『相比去年同月』限定并写『此后总体回升』→ 不推翻,记 NIT N-9"
     ).format(a=dv("JP_CPI_YOY", "2026-09"), b=dv("JP_CPI_YOY", "2026-07"), c=dv("JP_CPI_YOY", "2026-04"), d=dv("JP_CPI_YOY", "2025-10"), jb=below("JP_CPI_YOY").split("/")[0],
              e=dv("EA_HICP_YOY", "2026-09"), f=dv("EA_HICP_YOY", "2026-07"), g=dv("EA_HICP_YOY", "2026-04"), h=dv("EA_HICP_YOY", "2025-10"), eb=below("EA_HICP_YOY").split("/")[0]),
    "反方攻击 2(C1): 2025基/2020基拼接口径是否足以翻转 -0.55 → 注册表 JP_CPI_YOY.calc 的拼接告警阈 0.10pp 约为差值的 1/5;重叠期双基值不在只读面,未能独立量化 → 不推翻(残留不可量化项如实记录)",
    "反方攻击 3(C1): 东京 CPI 基期缺席是否被绕过 → 序列起点 2026-01,2025-10 无观测;席位写『同比对照不可判』并披露 Gate A noncore_missing → 诚实缺席成立",
    "反方攻击 4(C2): 若 2026-09-16 后欧央行另有决议则『无未生效决议』为假 → 引擎面序列止于 09-16、日历零条 ECB 实录,该情形在只读面既不可证也不可否;席位把结论限定于『引擎记录面』并标【尚未验证】→ 不推翻",
    ("反方攻击 5(C2): 日本端『收紧』方向是否只有间接证据 → 日央行实录无前值字段;月均 {n} 个逐月台阶中仅 {nd} 次 {mn:+.1f}bp 微降、净 +{nb:.0f}bp,2026-09 {s9:+.1f}bp(决议 09-18、生效 09-24,月内生效 7 天)→2026-10 {s10:+.1f}bp 与上调相容 → 方向有市场口径证据,【推断】标注恰当;总判断句未带标注记 MINOR M-4"
     ).format(n=len(STEPS), nd=N_DOWN, mn=MIN_STEP, nb=NET_BP, s9=STEP09, s10=STEP10),
    "反方攻击 6(C3): 席位是否把 degraded 序列冒充现行值 → 全文分句扫描: 事实位零句把 2026-09-16 后状态写成『无变化/维持』,5 处『维持』类命中均为情景/竞争解释/带『不可见·不可判·尚未验证』限定句 → 攻击不成立;注册表决策驱动口径未并列记 MINOR M-1",
    "反方攻击 7(M1 环 1): 路径数字逐月核对 → 判断档全部月度路径点值对 34 对(欧元区 10、日本全国 14、东京 2、政策月均 8)全部与序列面一致;『2025-01 高点』全序列最高为 4.31@2023-01 → 数值全中,用词记 NIT N-1",
    "反方攻击 8(M1 环 2): 若读数驱动,2026-01→04 读数 1.7→3.0 时欧央行应已上调 → 实际维持 2.15/2.0 共 371 天未动;席位已在裁定理由并列该反向观察,n=2 裁『尚不能区分』→ 不推翻",
    ("反方攻击 9(M1 环 3): 用问句窗六个月的交叉盘能否检验利差渠道 → 合成 EURJPY {st}→2026-11-20 为 {x:+.2f}%(腿: EURUSD {le:+.2f}%/USDJPY {lj:+.2f}%);同期欧央行两度上调合计 +50bp,日本端月均亦由 0.727 升至 1.227,可见的两地政策水平差(MRO−日本月均){d0:.3f}→{d1:.3f} 个百分点未变 → 与『利差主导』不相容,但美元全局主导解释对两腿分立亦无预期;席位只对本月窗(-0.24%/-0.73%)下结论 → 不推翻裁定;六个月窗读数未并列记 MINOR M-7,口径与渲染问题记 MINOR M-2"
     ).format(st=ST6, x=X6, le=LEG_E, lj=LEG_J, d0=PD0, d1=PD1),
    ("反方攻击 10(M1 环 4): 发布日单日读数是否支持『读数发布主因』 → 2026-11-20 NIKKEI225 {nk:+.2f}% 深于 SPX {sp:+.2f}%(窗内四地最大单日跌幅),2026-11-16 欧元区股指跌幅浅于美股(DAX {d:+.2f}%、CAC40 {c:+.2f}% vs SPX {s:+.2f}%);全局同跌、单日读数不具区分力 → 不推翻结论,记 MINOR M-6"
     ).format(nk=day1("NIKKEI225", "2026-11-20"), sp=day1("SPX", "2026-11-20"), d=day1("DAX", "2026-11-16"), c=day1("CAC40", "2026-11-16"), s=day1("SPX", "2026-11-16")),
    "反方攻击 11(情景): 证伪条件是否可观测、是否已被截止日数据判定 → EA_HICP_YOY/JP_CPI_YOY/VIX 在册且持续更新;截止日读数 EA 4.0/JP 2.44/VIX 2026-11-20 收盘 35.89 落在两情景之间(未决);时限 2027-02-15 晚于 2026-12 观测月入档(2027-01) → 可观测、未触发",
    "反方攻击 12(历史类比): 零段是否被偷引事后结果 → 候选月 2025-03 仅出现于零段注记,全文无『随后 N 个月』结果数字 → 成立",
    "反方攻击 13(总判断): 读者报告与判断档是否一致 → 总判断逐字在场;走位 2/2、对质表结构字段 18/18 在场;对质裁定三处均『尚不能区分』,与质量门注记[1]自述『支持主解释 0·支持竞争解释 0·尚不能区分 3』一致 → 一致",
    ("反方攻击 14(M1 环 4 数字): VIX 月窗 +84.5% 按显示精度与存储精度分别复算 → 19.45→35.89 两种精度均为 +{a:.2f}%,报告取一位小数 +84.5% → 命中").format(a=S07["stored"]),
]

CHECKS = [
    ("C1-INFL-DIVERGE(两地通胀同比方向相反)", [
        ("证据相关性", "相关。日本全国 CPI 同比、欧元区 HICP 同比 2026-10 与 2025-10 的同月观测在序列面(C001–C006);东京序列起点 2026-01、2025-10 无观测(C007/C008)。"),
        ("支持度", "完全支持。2.44−2.99=−0.55、4.0−2.1=+1.9;『低于/高于』方向词与数值一致(C009/C010);走位与点值格同值(B001–B036);陈述层中文数字逐句直算(CN001–CN007)。"),
        ("竞争解释(真正竞争)", "『能源与进口传导+高基数消退→剪刀差收敛』与『需求与政策组合→持续分化』对后续路径预期相反,是真竞争;均标【假设】,并以『引擎无分项构成与需求面序列』如实并列(K011),当前不可区分。"),
        ("反对证据", "『日本回落』只对去年同月成立: 近 12 个月中其余 11 个月里 10 个月读数低于最新值,较 1/3/6 个月前为 +0.28/+0.47/+1.06(反方攻击 1);基期 2025-10=2.99 为当时局部小高点(G008/G009/G012)。与陈述不相左(限定『相比去年同月』,走位写『此后总体回升』)。2025基/2020基拼接口径对 −0.55 的影响在只读面不可量化,注册表拼接告警阈 0.10pp(反方攻击 2)。"),
        ("结论是否超出证据", "未超出。只述方向与差值;东京端基期缺席写『同比对照不可判』,未补数。"),
        ("证伪条件可观测性", "即期对照无未来条件;后续路径由情景 S1/S2 承担(见情景六查)。"),
    ]),
    ("C2-POLICY-SYNC(同向收紧、可核行动均已生效)", [
        ("证据相关性", "相关。ECB_MRO/ECB_DFR 变更点、日央行两条实录、JP_POLICY_RATE 月均(D001–D040)。"),
        ("支持度", "欧央行两次 +25bp(2026-06-17、2026-09-16)、MRO 2.65/DFR 2.5、决议日回推(06-11、09-10)、间隔 91 天全中;日央行 2026-09-18 决议/09-24 生效/10-30 维持、24 天全中;月均 0.478→1.227、锚 0.727/1.227、一年窗净变动与变动点之和 75bp 全中(D034/D035);读者报告政策表日本行『距上次调整(按生效日)/距决议/距维持』60/66/24 天与直算一致(D026)。"),
        ("竞争解释(真正竞争)", "『读数驱动』与『正常化程序与汇率/金融稳定考量』对决议节奏预期不同,是真竞争;月频证据且无央行表态文本序列(K012),不可区分,如实并列。"),
        ("反对证据", "(i) 欧央行 2026-09-16 后 68 天决议面不可见(由 C3 专门处理);(ii) 日央行实录无前值字段,『收紧』方向只有市场口径间接证据(N010;反方攻击 5);(iii) JP_POLICY_RATE 一年窗 6 个变动点(阈值口径;计入两次 -0.1bp 微降则为 8 个非零台阶)中,仅 2026-10-01 一点前 45 天内有日央行决议实录(G018;补充计算 S03)——判断档写『其余月均台阶在发布日历无对应实录,不作相容性判断』,与之一致。"),
        ("结论是否超出证据", "『无未生效决议』限定于引擎记录面并带【尚未验证】(N002/N003);总判断未把月均写成官方目标(N008)。总判断句日本端方向未带【推断】(MINOR M-4)。"),
        ("证伪条件可观测性", "『其后决议面』待日历补录或官网可核——可观测,当前面缺席已披露。"),
    ]),
    ("C3-ECB-VISIBILITY(欧央行序列可见性)", [
        ("证据相关性", "相关。序列末观测、注册表新鲜度阈、Gate A 名单、L1 质量位、日历零条(D014–D019,K007–K009,N005)。"),
        ("支持度", "全部属实: 68 天>10 天;degraded 名单含两序列;L1 DEGRADED×2;日历零 ECB 条目;陈述层中文数字逐句直算(CN015–CN017)。"),
        ("竞争解释(真正竞争)", "『源端未再更新(实际无新决议)』与『断档期间有新决议』对现值水平预期相反,是真竞争;引擎面不可区分、须官网核对并标『引擎外补充待授权』——处置恰当。"),
        ("反对证据", "注册表同处的决策驱动口径(无更晚已证实决议不作过期)与引擎点值格 status=ok/freshness_basis=policy_confirmation(O009/O010),即引擎并未把现值判为过期——与 degraded 并存的另一面,席位未并列(MINOR M-1)。"),
        ("结论是否超出证据", "未超出。『不可判【尚未验证】』『仅覆盖引擎可见面』;事实位零句把 09-16 后状态写成『无变化/维持』(N001,反方攻击 6)。"),
        ("证伪条件可观测性", "可观测(官网或日历补录后即可核)。"),
    ]),
    ("M1 环 1(通胀路径,E1)", [
        ("证据相关性", "相关(G001–G011,F019–F032)。"),
        ("支持度", "判断档全部月度路径点值对 34 对(欧元区 10、日本全国 14、东京 2、政策月均 8)逐对复核全中;『两度小幅回升』『总体回升』用词与逐月环比一致(G012/G013)。"),
        ("竞争解释(真正竞争)", "事实环,无需;隐含的因果解读由对质环 1 承担。"),
        ("反对证据", "无(路径直读)。"),
        ("结论是否超出证据", "未超出;E1 环只含事实与【推断】标注(G021)。"),
        ("证伪条件可观测性", "不适用(事实环)。用词『2025-01 高点』为局部高点(NIT N-1)。"),
    ]),
    ("M1 环 2(政策面跟进,E1)", [
        ("证据相关性", "相关(G014–G018,D005–D008)。"),
        ("支持度", "变更点、幅度、日期全中;决议日逐处标【推断】(G017);BOJ 月均台阶只对 2026-09→10 作相容判断,其余不作(G018)。"),
        ("竞争解释(真正竞争)", "『跟进』隐含的因果由对质环 1 承担(读数驱动 vs 程序驱动)。"),
        ("反对证据", "两序列维持 2.15/2.0 共 371 天期间读数已由 1.7 升至 3.0 未触发变更(G096–G098)——席位已在裁定理由并列(反方攻击 8)。"),
        ("结论是否超出证据", "未超出。"),
        ("证伪条件可观测性", "由对质环 1 承担: 区分指标 EA_HICP_YOY 在场(G102),两解释对其上的预期不同(决议前可见抬升 vs 无稳定先后关系),n=2(G100),裁『尚不能区分』。"),
    ]),
    ("M1 环 3(汇率传导,E2)", [
        ("证据相关性", "相关(G022–G043,K010)。"),
        ("支持度", "观察事实全中: EURUSD −2.24%、USDJPY +2.05%、DXY +1.96%;盘中 −2.51%/+1.82%/+2.23%;合成交叉盘 −0.24%/−0.73%;裁定理由所称『两解释预期未分立』经复算成立(见竞争解释一栏)。"),
        ("竞争解释(真正竞争)", "『美元全局因素与风险情绪主导』对『政策利差主导』: 既述预期为同向 vs 方向分立,是真竞争;纳入美元端利率后两者对本月窗预期相同(预期未分立),按读者报告判断口径属『诚实缺省』。"),
                ("反对证据", ("美元端利率更高使主解释预期反转(席位自列);UST_10Y 口径不对等(MINOR M-2);更长窗读数: 合成交叉盘 {st}→2026-11-20 为 {x:+.2f}%,同期可见的两地政策水平差 {d0:.3f}→{d1:.3f} 个百分点未变,与『利差主导』不相容(反方攻击 9);判断档只检验了本月窗,六个月窗读数未并列(MINOR M-7)。"
                      ).format(st=ST6, x=X6, d0=PD0, d1=PD1)),
        ("结论是否超出证据", "未超出(『幅度小,利差渠道未获检验亦未被否定』限本月窗;六个月窗读数未并列见 MINOR M-7)。"),
        ("证伪条件可观测性", "区分指标 EURUSD 在场(G103);窗内无政策变动点(G101),本月窗无检验力,如实。"),
    ]),
    ("M1 环 4(资产面,E2)", [
        ("证据相关性", "相关(G045–G087,L002/L003)。"),
        ("支持度", "数值全中: SPX −9.36%、NIKKEI225 −9.98%、DAX −1.50%、CAC40 +1.86%;VIX 19.45→35.89(+84.5%);末六日路径;跳升窗四地;距政策日 14/58/21/65 天;发布日 VIX +18.70%/+26.20%;两日汇市单日变动≤0.23%。"),
        ("竞争解释(真正竞争)", "『紧缩+通胀粘性』与『全局风险/流动性冲击』对 VIX 路径与区域相对表现预期不同,是真竞争;席位另列读数发布与会议纪要为候选驱动。"),
        ("反对证据", "主解释两项派生预期未获支持(欧元区股指不弱于美股;VIX 跳升不与政策日历对齐),席位已自列;发布日单日读数未列(MINOR M-6,反方攻击 10)。"),
        ("结论是否超出证据", "未超出(『单一归因于两地政策不可证』)。"),
        ("证伪条件可观测性", "区分指标 VIX 在场(G104);『待 2026-11-23 收盘及其后收盘数据复检』可执行。"),
    ]),
    ("情景 S1/S2 与历史类比", [
        ("证据相关性", "相关(I001–I017,H001–H007)。"),
        ("支持度", "前提与截止日读数相容(EA 4.0/JP 2.44/VIX 2026-11-20 收盘 35.89 落在两情景之间,未决);类比能力已执行(扫描 1871/有效 74/TOP1 2025-03 距离 0.727),历史 0 段。"),
        ("竞争解释(真正竞争)", "两情景方向互补(维持 3.5% 以上 vs 回落至 3.0% 以下;日本端 2.0% 对应);历史类比不适用。"),
        ("反对证据", "S2 与近一月观察相反,席位自标『并列反例情景』;历史类比不适用。"),
        ("结论是否超出证据", "未超出(标『假设·非预测』;零段注记,候选月仅出现于注记,无事后结果数字)。"),
        ("证伪条件可观测性", "指标在册可观测;时限 2027-02-15 晚于 2026-12 观测月入档;3.0%–3.5% 中间区间如实;欧央行政策分量不可数值核验已披露(I012)。S1 置信档用词见 NIT N-4。"),
    ]),
    ("总判断/走位/对质表一致性(⑩)", [
        ("证据相关性", "相关(J001–J024)。"),
        ("支持度", "总判断与读者报告逐字一致(J022);走位 2/2 在场(J016);对质表结构字段 18/18 在场(J017);裁定三处均『尚不能区分』,与质量门注记[1]自述『支持主解释 0·支持竞争解释 0·尚不能区分 3』一致(J002/J003);总判断政策水平与 C2 一致(J012);L3 20 条引用全解析(J004–J006)。"),
        ("竞争解释(真正竞争)", "各处均已并列主/竞争预期。"),
        ("反对证据", "裁定理由(verdict_note)与三转折叙述未渲染(范围外观察 S-1/S-2)。"),
        ("结论是否超出证据", "未超出;三处均未把『尚不能区分』写成倾向性结论(对质环 3 的倾向只写在理由里,NIT N-3)。"),
        ("证伪条件可观测性", "三处区分指标(EA_HICP_YOY/EURUSD/VIX)均在证据索引(G102–G104)。"),
    ]),
]

# ------------------------------------------------------------------ attack label format
# protocol section 6 template is exactly "反方攻击 N: 攻击内容→结果"; the target of the attack moves into brackets
_ATK = re.compile(r"^反方攻击 (\d+)\(([^)]*)\): (.*)$")


def atk_norm(s):
    m = _ATK.match(s)
    return "反方攻击 %s: [%s] %s" % (m.group(1), m.group(2), m.group(3)) if m else s


ATTACKS = [atk_norm(a) for a in ATTACKS]
for _i, _a in enumerate(ATTACKS):
    assert _a.startswith("反方攻击 %d: " % (_i + 1)) and "→" in _a, _a[:30]

# ------------------------------------------------------------------ validations
# registry / engine wording quoted in the findings must occur in the recorded registry texts (supplement S06)
S06TXT = json.dumps(SUPP["S06"]["value"], ensure_ascii=False)
miss_q = [q for q in ("决策驱动政策目标序列", "观测日=政策最后确认/变更日", "无更晚已证实决议不作过期", "利率长期不变≠数据停更",
                      "HICP流程对近月含回溯修订", "2025-12 值1.9→2.0", "latest_vintage_asof_collected", "终值") if q not in S06TXT]
if miss_q:
    print("REGISTRY QUOTE NOT FOUND:", miss_q)
    sys.exit(3)
bad = [it["tag"] for it in ITEMS if it["original"] and it["original"] not in ALLTEXT]
if bad:
    print("ORIGINAL NOT FOUND VERBATIM:", bad)
    sys.exit(2)


def flatnums(x, sink):
    if isinstance(x, bool):
        return
    if isinstance(x, (int, float)):
        sink.add(round(abs(float(x)), 4))
    elif isinstance(x, str):
        for m in re.findall(r"-?\d+(?:\.\d+)?", x):
            try:
                sink.add(round(abs(float(m)), 4))
            except ValueError:
                pass
    elif isinstance(x, (list, tuple)):
        for y in x:
            flatnums(y, sink)
    elif isinstance(x, dict):
        for y in x.values():
            flatnums(y, sink)


numset = set()
for r in MERGED["rows"]:
    if r.get("ok") and not r.get("scope_out"):
        for k in ("computed", "reported", "src", "note"):
            flatnums(r.get(k), numset)
flatnums(COUNTER, numset)
flatnums(SUPP, numset)
DECRX = re.compile(r"(?<![\d.])\d+\.\d+")
# a decimal in the seat's own text is traceable if, rounded to its own number of decimals, it equals some
# direct-computed / reported / source value of an OK in-scope row, a counter-attack result or a supplement value
NUMBYD = {d: set(round(v, d) for v in numset) for d in range(0, 5)}


def untraceable(text):
    out = []
    text = re.sub(r"v\d+(?:\.\d+)+", " ", text)
    text = re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", " ", text)
    text = re.sub(r"#{2,4} \d+(?:\.\d+)*", " ", text)       # section numbers of this document
    text = re.sub(r"第 ?\d+\.\d+ ?节", " ", text)
    text = re.sub(r"第 ?\d+(?:\.\d+)+ ?节", " ", text)
    for m in DECRX.finditer(text):
        tok = m.group(0)
        d = len(tok.split(".")[1])
        if d > 4 or round(float(tok), d) not in NUMBYD[d]:
            out.append(text[max(0, m.start() - 12):m.end() + 6])
    return out


tr = []
for it in ITEMS:
    tr += [(it["tag"], u) for u in untraceable(it["note"] + " " + it["fix"])]
for i, a in enumerate(ATTACKS):
    tr += [("attack%d" % (i + 1), u) for u in untraceable(a)]
for title, rows in CHECKS:
    for a, b in rows:
        tr += [(title[:6], u) for u in untraceable(b)]
print("untraceable decimals in findings:", tr)

N_PTS = MERGED["recompute_points"]
N_MIS = MERGED["recompute_mismatches"]
N_DUP = MERGED["duplicate_pair_rechecks"]
N_DUP_OK = MERGED["duplicate_rechecks_ok"]
N_SO = MERGED["scope_out_observations"]
BY = MERGED["by_category"]
vD = sum(BY[k]["in_scope"] for k in BY if k.startswith("D-"))
vE = sum(BY[k]["in_scope"] for k in BY if k.startswith("E-"))
dD = sum(BY[k]["dup"] for k in BY if k.startswith("D-"))
dE = sum(BY[k]["dup"] for k in BY if k.startswith("E-"))
MINSHORT = {
    "M-1": "欧央行时效只并列滞后口径,未并列注册表决策驱动口径与引擎点值格状态",
    "M-2": "传导环 3 以 UST_10Y 作美元端利率,口径不对等,且本月窗两解释预期未分立、对质无检验力而裁定理由未渲染",
    "M-3": "EA HICP 公布时间只给推定终值日,未并列冻结日历所载两档首发形态",
    "M-4": "总判断句日本端『收紧』方向未带【推断】",
    "M-5": "对质环 1『决议日前可见读数』为最新修订值,未并列首发值口径",
    "M-6": "『读数发布主因未获跨地区支持』未列发布日单日读数",
    "M-7": "传导环 3 汇率检验只用一个月窗,问句窗六个月内合成交叉盘下跌而可见政策水平差未变的读数未并列",
}
assert [it["tag"] for it in MINOR] == sorted(MINSHORT), ([it["tag"] for it in MINOR], sorted(MINSHORT))
CATNAME = {"①": "研究截止日/印章/推定发布日", "②": "点值锚格(六个月前/最新一期)", "③": "同比(基期/差值/方向词)", "④": "政策面(变更点/生效日/决议日/目标值)",
           "⑤": "三利率分解与资产月窗回贴", "⑥": "转折判断与候选面", "⑦": "传导链各环(E1/E2)与对质三环", "⑧": "历史类比", "⑨": "情景(证伪/触发/时限)",
           "⑩": "总判断/走位/对质表一致性", "⑪": "诚实缺席项", "⑫": "截止日当日日频观测时点", "⑬": "契约验证非 VERIFIED 项(STALE)披露",
           "⑭": "交付门相关缺口披露", "⑮": "目标利率数值/生效日/现行有效/待生效分记、同比基期"}
n_major = 0
n_minor = len(MINOR)
n_nit = len(NIT)

# ------------------------------------------------------------------ VERDICT json
notes = (
    "零上下文独立席只读复算: 范围内复算 %d 点,命中 %d、偏离 %d;另有 %d 条逐对/逐句复核与已覆盖点重复(全中,不重复计数)、%d 条引擎渲染/口径面范围外观察(非判断偏离,不计入)。"
    "判断档承载判断的文字内阿拉伯数字 478 个词元全部对应到直算行;三条矛盾陈述内中文数字 36 个词元中 35 个对应到直算行字面,余 1 个为序数词『一次』非量值。"
    "规程第 3 节十五类均有覆盖(%s;另数字覆盖清查补点 %d)。"
    "要点: 研究截止日 2026-11-23 与快照时间戳、冻结输入印章、代码印章一致;六个月前/最新一期锚格 12 值全中;日本全国 CPI 同比 2.44 对 2025-10 的 2.99 差 -0.55、欧元区 HICP 4.0 对 2.1 差 +1.9,基期为同月非相邻月;"
    "欧央行两次 +25bp(2026-06-17、2026-09-16)、MRO 2.65/DFR 2.5、日央行 2026-09-18 决议/2026-09-24 生效/2026-10-30 维持、68 天滞后与 Gate A degraded/L1 DEGRADED 均如实;"
    "机制链四环数值(汇率月窗、交叉盘合成、VIX 路径、跳升窗股指、发布日汇市单日变动不超过 0.23%%)全中,证据分级 E1/E1/E2/E2 与标注相符;历史类比 0 段且未引事后结果;两情景证伪指标在册可观测、时限晚于入档、中间区间如实;"
    "总判断与读者报告逐字一致,对质裁定三处均『尚不能区分』;欧央行 2026-09-16 后状态在事实位零句被写成『无变化/维持』,结论限定于引擎可见面并标【尚未验证】。"
    "反方攻击 %d 条(每条 L3 矛盾、机制链每环至少一条)均未推翻。MAJOR 0;MINOR %d(%s);NIT %d。无 REVISE 级问题,裁决 UPHELD。"
) % (N_PTS, N_PTS - N_MIS, N_MIS, N_DUP, N_SO,
     "/".join("%s%d" % (k, BY[k]["in_scope"]) for k in sorted(BY) if k in CATNAME), vD + vE, len(ATTACKS), n_minor,
     ";".join(MINSHORT[it["tag"]] for it in MINOR), n_nit)

verdict = {
    "seat": "semantic-audit-seat",
    "reviewer": "independent-zero-context-seat-r32-t3-round1",
    "verdict": "UPHELD",
    "overall": "UPHELD",
    "notes": notes,
    "items": [{"severity": it["severity"], "where": it["where"], "note": it["note"], "original": it["original"], "fix": it["fix"]}
              for it in ITEMS],
    "must_fix": [],
    "counterexamples_sought": ATTACKS,
    "recompute_points": N_PTS,
    "recompute_mismatches": N_MIS,
    "mismatch_details": [],
    "audited_at": AUDITED_AT,
}
VP = os.path.join(out_dir, "VERDICT-round1.json")
with open(VP, "w", encoding="utf-8") as f:
    json.dump(verdict, f, ensure_ascii=False, indent=1)

# ------------------------------------------------------------------ PROSE
S02J, S02E = S02["JP_CPI_YOY"], S02["EA_HICP_YOY"]
_overlay = (("release_calendar", "config/release_calendar.json"), ("metric_registry", "config/metric_registry.json"),
            ("snapshot", "data/daily/research_snapshot_20261123.json"))
L = []
A = L.append
A("# Audit-R32 · T3 · Round-1 · 独立语义审查席复算记录")
A("")
A("- 审查席: semantic-audit-seat;reviewer: independent-zero-context-seat-r32-t3-round1;audited_at: %s" % AUDITED_AT)
A("- 裁决: **UPHELD**(MAJOR 0 / MINOR %d / NIT %d);范围内复算 %d 点,命中 %d,偏离 %d。" % (n_minor, n_nit, N_PTS, N_PTS - N_MIS, N_MIS))
A("- 本记录只依据本席在只读面上亲自复算到的东西;未读取任何既有评审内容,未与研判席或操作者通信。")
A("")
A("## 0. 审查对象、只读面与方法")
A("")
A("- 问句原文: 「%s」" % QUESTION)
A("- 受审运行目录(只读): `%s`" % run_dir)
A("- 隔离安装树(只读): `%s`" % tree_dir)
A("- 代码印章: report.json run.git_head 与 CODE_VERSION git_head 均为 `8f9055d6e556700b08f28a3abeff284cf0c8d71f`(A012)。")
A("- 冻结输入印章(sha256 前 16 位): release_calendar `e44fd2aa5ced0310`、metric_registry `fa396d22175a4814`、snapshot `2d650f1128cdd356`;运行目录 overlay 副本、report.json run.frozen_inputs 与协议印章一致(A013–A015);MAP_REPORT.md 的 sha256 与 MAP_REPORT.sha256 一致(A016)。")
A("- 本席成文时复算(运行目录 root_overlay 三件冻结输入,sha256 前 16 位): " + ", ".join(
    "%s `%s`" % (n, sha16(os.path.join(run_dir, "root_overlay", p))) for n, p in _overlay)
  + ";MAP_REPORT.md 全 64 位 `%s`。" % sha_full(os.path.join(run_dir, "MAP_REPORT.md")))
A("- 约束遵守: 未联网;未运行 ia_cli 的任何写操作;未调用裁决登记;未写入/移动/删除受审目录与安装树内任何文件;未读取规程第 2 节所列目录;未委派子代理。")
A("- 方法: 全部复算由 `/usr/bin/python3 -I <脚本> <路径参数…>` 完成,路径一律作参数传入,脚本与产出只写本目录。一条复算点判「一致」须同时满足: 直算值按报告自身小数位四舍五入后等于报告值,且(若给出字面)该字面在判断档对应文本中逐字在场。")
A("- 脚本: s10_common.py(公共读函数与台账);s11(①–⑥)/s12(⑦–⑩)/s14(⑪–⑮)/s18、s24(数字覆盖清查补点)为复算脚本;s20_counter.py 为反方攻击复算;s25_supplement.py 为本席自有发现的补充计算;s16 两份为数字覆盖清查;s15_merge.py 合并出 recompute_points.json 与 recompute_table.md;s27/s28 为成文前的引用核对探针;s30/s34/s35 为注册表文字与判断档原文的核对探针;s31 为成稿浏览;s32 为问题清单 where 路径核对(每条问题的原句须在其所引位置逐字在场);s29 为产出校验(裁决档结构、敏感字扫描);s23 生成本记录与裁决档。中间表: recompute_points_A–E.json、recompute_points.json、recompute_table.md、counterexamples.json、supplement.json。")
A("- 行号约定: A=①,B=②,C=③,D=④,E=⑤,F=⑥,G=⑦,H=⑧,I=⑨,J=⑩,K=⑪,L=⑫,M=⑬,N=⑭,O=⑮;D1xx/D2xx=数字覆盖清查补点,CN=三条矛盾陈述内中文数字的逐句直算。")
A("")
A("## 1. 复算清单")
A("")
A("### 1.1 按类别小计")
A("")
A("| 类别 | 范围 | 计入点数 | 命中 | 偏离 | 重复复核 | 范围外观察 |")
A("|---|---|---|---|---|---|---|")
for k in sorted(BY, key=lambda k: (0 if k in CATNAME else 1, k)):
    if k in CATNAME:
        v = BY[k]
        A("| %s | %s | %d | %d | %d | %d | %d |" % (k, CATNAME[k], v["in_scope"], v["in_scope"] - v["in_scope_mismatch"], v["in_scope_mismatch"], v["dup"], v["scope_out"]))
A("| 补 | 数字覆盖清查(逐对/逐句复核后新增的点) | %d | %d | 0 | %d | 0 |" % (vD + vE, vD + vE, dD + dE))
A("| **合计** | | **%d** | **%d** | **%d** | %d | %d |" % (N_PTS, N_PTS - N_MIS, N_MIS, N_DUP, N_SO))
A("")
A("说明: 「重复复核」指本席为数字覆盖清查又做了一遍、但与已计点同指标同时点同值的复核(%d 条全中),不重复计入点数;「范围外观察」是引擎渲染或引擎口径面的不一致(复算值与引擎面值不同,但不是判断档的偏离),单列于第 5 节,不计入命中/偏离。" % N_DUP_OK)
A("")
A("### 1.2 数字覆盖清查")
A("")
A("- 判断档承载判断的文字(三条矛盾陈述及其竞争解释、机制链四环、总判断、两地走位、对质三环全部字段、三转折、情景、质量门注记)内阿拉伯数字 478 个词元: 未覆盖 0。其中注册表拼接告警阈 0.10pp 与汇市单日变动上限 0.23% 两类词元由专门行判定(D204、D201),其余按数值或年月与某条一致行的直算值相等。")
A("- 三条矛盾陈述内中文数字 36 个词元: 35 个对应到直算行的字面(CN001–CN017 及 C/D 类各行),余 1 个为序数词「一次」(「最近一次变更日」),非量值。")
A("- 说明: 这一步是「每个数字都有出处」的兜底,不替代逐类复算;清查中新增并计入的点共 %d 个(D 类 %d、CN 类 %d)。" % (vD + vE, vD, vE))
A("")
A("### 1.3 逐点清单")
A("")
TBL = TABLE.rstrip("\n")
L.append(TBL)
A("")
A("### 1.4 本席补充计算(支撑第 2–4 节里本席自己引用的数字;出处=文件+键)")
A("")
A("| 编号 | 内容 | 出处键 | 数值 |")
A("|---|---|---|---|")
A("| S01 | 2026-11-16..2026-11-20 逐日收盘变动%% | series_store.SPX/NIKKEI225/DAX/CAC40/VIX/EURUSD/USDJPY | %s |" % "; ".join(
    "%s %s" % (m, "/".join("%+.2f" % x[3] for x in S01[m])) for m in ("SPX", "NIKKEI225", "DAX", "CAC40", "VIX", "EURUSD", "USDJPY")))
A("| S02 | 最新同比读数相对 1/3/6/12 个月前的差;近 12 个月其余各月低于最新值个数 | series_store.JP_CPI_YOY、EA_HICP_YOY | 日本 %s(%s);欧元区 %s(%s) |" % (
    "/".join("%+.2f" % S02J["diff_vs"][k] for k in ("2026-09", "2026-07", "2026-04", "2025-10")),
    S02J["prior_11_months_below_latest"][0],
    "/".join("%+.2f" % S02E["diff_vs"][k] for k in ("2026-09", "2026-07", "2026-04", "2025-10")),
    S02E["prior_11_months_below_latest"][0]))
A("| S03 | 月均逐月台阶(bp,进入该月) | series_store.JP_POLICY_RATE | %s |" % ", ".join("%s %+.1f" % (x[0][:7], x[3]) for x in S03["steps_into_month"]))
A("| S03 | 一年窗非零变动点 / 前 45 天内有日央行决议实录者 | series_store.JP_POLICY_RATE;release_calendar JP_POLICY_TARGET | %d 个:%s;有实录: %s(决议 %s) |" % (
    len(S03["change_points_1y"]), ", ".join("%s %+.1f" % (x[0], x[1]) for x in S03["change_points_1y"]),
    ", ".join(S03["points_with_record_within_45d"]), ", ".join(S03["boj_decisions"])))
A("| S04 | 合成交叉盘(EURUSD×USDJPY)与两腿;窗两端可见政策水平差(MRO−日本月均) | series_store.EURUSD × series_store.USDJPY; series_store.ECB_MRO; series_store.JP_POLICY_RATE | "
  "六个月窗起点(2026-05-23 当日或之前的最近共同观测日) %s;交叉盘: %s;变动%%: %s;腿 %s→11-20: EURUSD %+.4f%%、USDJPY %+.4f%%;政策水平差: %s |" % (
      S04["start6"], ", ".join("%s=%.4f" % (k[:10], v) for k, v in S04["cross"].items()),
      ", ".join("%s %+.2f" % (k, v) for k, v in S04["cross_change_%"].items()), S04["start6"], LEG_E, LEG_J,
      "; ".join("%s: MRO %s(观测 %s)−月均 %s(观测 %s)=%s 个百分点" % (
          d, v["ECB_MRO"][1], v["ECB_MRO"][0], v["JP_POLICY_RATE"][1], v["JP_POLICY_RATE"][0], v["diff_pp"])
          for d, v in S04["visible_policy_differential"].items())))
A("| S10 | 对质环 1 各『变更前可见读数』相对 2026-02 的差;2026-05 峰值与第二次决议日前读数之差 | series_store.EA_HICP_YOY @2026-02/2026-04/2026-05/2026-07/2026-08 | %s;峰值差 %s |" % (
    ", ".join("%s %+.1f" % (k, v) for k, v in S10["vs_2026-02"].items()), S10["peak_minus_2026-07"]))
A("| S05 | 美元端政策利率(同口径)与市场收益率末观测 | series_store.DFEDTARL/DFEDTARU/UST_10Y | %s |" % "; ".join(
    "%s@%s=%s" % (k, v[0], v[1]) for k, v in SUPP["S05"]["value"].items()))
A("| S07 | VIX 月窗幅度的存储精度与显示精度 | series_store.VIX @2026-10-23/@2026-11-20 | %+.4f%% / %+.4f%% |" % (S07["stored"], S07["displayed"]))
A("| S08 | JP_CPI_YOY 全序列最高 | series_store.JP_CPI_YOY | %s=%s |" % tuple(SUPP["S08"]["value"]))
A("| S09 | 读者报告行号核对 | MAP_REPORT.md / FULL_REPORT.md / report.md | %s |" % json.dumps(SUPP["S09"]["value"], ensure_ascii=False))
A("| S06 | 注册表口径文字 | metric_registry.ECB_MRO/ECB_DFR.freshness.decision_dated_note;EA_HICP_YOY.release_semantics | 见第 4 节 M-1、M-5 原文引用 |")
A("")
A("## 2. 六查逐项结论")
A("")
for title, rows in CHECKS:
    A("### %s" % title)
    A("")
    A("| 查项 | 结论 |")
    A("|---|---|")
    for a, b in rows:
        A("| %s | %s |" % (a, b.replace("|", "\\|")))
    A("")
A("## 3. 反方攻击记录")
A("")
A("每条 L3 矛盾陈述、机制链每一环至少一条;攻击用的计算见 counterexamples.json(s20_counter.py)与第 1.4 节补充计算。")
A("")
for a in ATTACKS:
    A("- %s" % a)
A("")
A("## 4. 问题清单")
A("")
A("### MAJOR(0 条)")
A("")
A("未发现数字/日期/方向错或与证据相左、缺基期给同比、相邻口径冒充、事后信息冒充当时可知、无标注的超出证据结论、不可观测的证伪条件。逐项排除依据见第 2 节六查与第 3 节反方攻击。")
A("")
A("### MINOR(%d 条,口径/披露可改进,不改变结论)" % n_minor)
A("")
for it in MINOR:
    A("**%s** — 位置: %s" % (it["tag"], it["where"]))
    A("")
    A("- 原句: 「%s」" % it["original"])
    A("- 问题: %s" % it["note"])
    A("- 建议改句(数字均有复算行或补充计算支撑): 「%s」" % it["fix"])
    A("")
A("### NIT(%d 条,行文)" % n_nit)
A("")
for it in NIT:
    A("- **%s** — 位置: %s" % (it["tag"], it["where"]))
    if it["original"]:
        A("  - 原句: 「%s」" % it["original"])
    A("  - 说明: %s" % it["note"])
    if it["fix"]:
        A("  - 建议: 「%s」" % it["fix"])
A("")
A("### 披露后可接受、不列为问题的点")
A("")
A("- 欧央行两序列在 Gate A 为 degraded、L1 为 DEGRADED 的情况下被用作「最新生效水平」: 问句所问正是现行目标利率,席位把结论限定于引擎记录面/可见面并标【尚未验证】,且事实位没有任何一句把 2026-09-16 之后写成「无变化/维持」(N001–N005)。")
A("- 情景的欧央行政策分量不设数值触发: 数值证伪指标(EA_HICP_YOY/JP_CPI_YOY/VIX)在册可观测;政策分量以决议实录核验并明写「冻结日历对欧央行零条实录,须待日历补录」,属如实披露而非不可观测(I012)。")
A("- 对质环 2 裁定「尚不能区分」: 主解释经辅助前提(美元端利率)后与竞争解释在本月窗预期相同,按读者报告判断口径(「预期未分立=尚不能区分,诚实缺省」)成立;口径与渲染问题见 M-2,六个月窗读数见 M-7。")
A("- 对质环 3 裁定「尚不能区分」而理由写「证据倾向竞争解释」: 第三类候选驱动在场、回落观测只有一个盘中点,保守裁定可成立(NIT N-3 只提行文)。")
A("- 东京都 CPI(Gate A noncore_missing)两点值进入 C1 与日本走位: 系契约要求的锚回声,状态在原处披露,未进入总判断(NIT N-6)。")
A("")
A("## 5. 范围外观察(引擎渲染/口径面,供操作者;非判断偏离)")
A("")
A("- **S-1**(J017X): 传导对质三环的裁定理由(verdict_note)在 MAP_REPORT.md、FULL_REPORT.md、report.md 均未渲染;MAP_REPORT.md 第 136 行「该预期未纳入美元端利率——见裁定理由」因此成为悬空指引(读者在读者报告里看不到美元端利率高于两地这一关键理由,也看不到对质环 3 的证据倾向)。")
A("- **S-2**(J018X): 三转折的叙述(narrative,含逐月路径与「其余月均台阶不作相容性判断」)三件均未渲染;读者报告「过去一年的三个转折」表(第 163–168 行)按并项口径把转折 1 与转折 2 并成一行(第 167 行「同轮事件并项」;第 170 行有并项说明: 同维度且观测窗重叠的转折视为同一轮事件),表内两行——并项后的行把两段「跟进/背离」文字用分号拼接,逐转折的对应关系须对照判断档才可分。")
A("- **S-3**(J020): 质量门注记六条(含引擎缺口四项的自述)三件均未渲染。")
A("- **S-4**(K015): 引擎点值格对 Gate A noncore_missing 的 JP_CPI_TOKYO_YOY 两个锚仍标 status=ok,读者报告环境表与覆盖表该行亦标 ok,与同页「缺席/降级数据不得进入研究结论」并置。")
A("- **S-5**(O013): 引擎面对欧央行决议日有两种表述——注册表 calc/release_semantics 写「决议变更即时生效/决议公布后生效并当日更新系列」,读者报告覆盖表把 2026-09-16 写作「ECB 决议日当日公布(变更日观测)」,政策表却写决议 2026-09-10、生效 2026-09-16。席位取政策表面并把决议日标【推断】,生效日 2026-09-16 在两种读法下不变。")
A("- 另记(未单列复算行,阅读三件报告时所见): 契约核验的 STALE 位未在读者报告露出(S09:三件均无「STALE」字样;FULL_REPORT.md 第 180 行为 `review: required=True seat_invoked=False verdict=None`,系本席成文前的应有状态);三件读者报告对判断档各段互补渲染(总判断只在 MAP_REPORT.md,机制链四环全文只在 FULL_REPORT.md/report.md),除上列 S-1–S-3 外无任何判断段落三件均缺席。")
A("")
A("## 6. 裁决")
A("")
A("范围内复算 %d 点全部命中、偏离 0;十五类覆盖齐备;六查各项无「结论超出证据且无标注」「事后信息冒充当时可知」「证伪条件不可观测」;%d 条反方攻击均未推翻判断档的任何数字、日期或方向。所列 %d 条 MINOR 均为口径并列与披露完整性的改进项,不改变任何结论;无 REVISE 级问题。" % (N_PTS, len(ATTACKS), n_minor))
A("")
A("**裁决: UPHELD**(must_fix 为空;MINOR/NIT 如实列出,供研判席下一轮参考,不作为放行条件)。")
A("")
BODY = "\n".join(x for x in L if x is not TBL and x != TBL)
print("untraceable decimals in PROSE body:", untraceable(BODY))
print("untraceable decimals in notes:", untraceable(notes))
PP = os.path.join(out_dir, "PROSE-round1.md")
open(PP, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("written", PP, os.path.getsize(PP), "bytes")
print("written", VP, os.path.getsize(VP), "bytes")
print("counts: points=%d mismatches=%d dup=%d(ok %d) scope_out=%d MAJOR=%d MINOR=%d NIT=%d attacks=%d" % (
    N_PTS, N_MIS, N_DUP, N_DUP_OK, N_SO, n_major, n_minor, n_nit, len(ATTACKS)))
