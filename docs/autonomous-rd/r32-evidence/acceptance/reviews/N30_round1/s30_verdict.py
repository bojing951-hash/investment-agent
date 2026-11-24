# s30_verdict.py <aj> <all_json> <out_json> [dry]  -- build + validate VERDICT-round1.json (single write)
import sys, json
aj = json.load(open(sys.argv[1], encoding='utf-8'))
allp = json.load(open(sys.argv[2], encoding='utf-8'))
out = sys.argv[3]; dry = len(sys.argv) > 4 and sys.argv[4] == 'dry'
pts = allp['points']
NPT = len(pts); NMM = sum(1 for p in pts if not p['ok'])
LEAVES = []
def walk(o):
    if isinstance(o, dict):
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
    elif isinstance(o, str): LEAVES.append(o)
walk(aj)
ALL = chr(10).join(LEAVES)

items = [
 {'severity': 'MINOR',
  'where': 'agent_judgment.json l3.contradictions[0].statement(C1 末段)、reader_map.turnings[2].first_mover、reader_map.regions[1].from_to 与 anchor_echo',
  'note': 'JP_CPI_TOKYO_YOY 在冻结快照 gate_a.noncore_missing 内(Gate A 注记: 缺失/失败数据已披露,不得进入研究结论),判断档仍以其序列面读数充当第三转折的先行指标、C1 方向佐证与锚回声;每处均披露「Gate A 列于 noncore_missing、点值取自快照序列面、L1 无对应事实行」,而 C3⑤ 对同为 noncore_missing 的 GDP 序列采取「按 Gate A 不取用」,同一档内取用标准不一。结论(两地水平与同比方向分化、日本通胀回升)主要由全国口径序列支撑,不因剔除东京读数而改变,故定 MINOR。建议统一取用规则,或在第三转折与锚回声处明写「序列面参考、不作为结论必要支撑」,并提请核对引擎各面对该指标的不一致(数据需求面 satisfied、点值格 status=ok 而 Gate A 缺席)。',
  'original': '东京都 CPI 同比(速报先行口径;该序列当日快照 Gate A 列于 noncore_missing,读数取自快照序列面、L1 无对应事实行)2026-06→2026-09 由 1.6 升至 2.69(三个月 +1.09 个百分点)。',
  'fix': '东京都 CPI 同比(速报先行口径;该序列当日快照 Gate A 列于 noncore_missing,读数取自快照序列面、L1 无对应事实行,按 Gate A 不作为结论必要支撑、仅作序列面参考)2026-06→2026-09 由 1.6 升至 2.69(三个月 +1.09 个百分点)。'},
 {'severity': 'MINOR',
  'where': 'agent_judgment.json l3.contradictions[2].statement(C3 ②)',
  'note': '引擎数据需求面将 ECB_MRO/ECB_DFR 记为 insufficient_coverage(窗内有效观测 n=2<66),report.notes 列「地图计划指标缺数(披露不阻断): ECB_MRO、ECB_DFR」并渲染进读者报告;判断档已披露实质限制(序列止于 2026-09-16、距截止 68 天、Gate A 降级、契约 STALE、后续决议面不可判),但未点名「窗内覆盖不足/计划指标缺数」这一引擎面形态,读者在报告表格层看到「缺数」字样时判断档无对应说明。不改变结论。建议在 C3② 补一句指向数据需求面的覆盖不足记载。',
  'original': 'ECB_MRO/ECB_DFR 序列最后观测均为 2026-09-16,观测日距研究截止 2026-11-23 六十八天,超过注册表新鲜度阈十天',
  'fix': 'ECB_MRO/ECB_DFR 序列最后观测均为 2026-09-16,观测日距研究截止 2026-11-23 六十八天,超过注册表新鲜度阈十天(引擎数据需求面同记该两指标窗内有效观测不足、地图计划指标缺数,披露不阻断)'},
 {'severity': 'NIT', 'where': 'agent_judgment.json reader_map.regions[1].from_to',
  'note': '「自 2025-01 高点 4.03」中 4.03 为 2025-01 读数,非全序列最高(series_store.JP_CPI_YOY 最高为 2023-01 的 4.31),建议加「阶段」限定。',
  'original': '自 2025-01 高点 4.03 总体回落', 'fix': '自 2025-01 的阶段高点 4.03 总体回落'},
 {'severity': 'NIT', 'where': 'agent_judgment.json l4.scenarios[0].rows.asset_direction.confidence_tier(对 scenarios[1] 与传导对质结论)',
  'note': 'S1 资产方向置信层级「有相关证据」与 S2「纯逻辑推理」、同窗传导对质「尚不能区分」并列时层级语义不一(此处「相关证据」指同窗观测相容而非因果已立),建议加限定语。',
  'original': '有相关证据', 'fix': '有相关证据(同窗观测相容,与冲击主导解释尚不能区分)'},
 {'severity': 'NIT', 'where': 'agent_judgment.json quality_gate_notes[3]',
  'note': '「两情景五行齐备」易读作合计五行(实为每情景五行)。', 'original': '两情景五行齐备', 'fix': '两情景各五行齐备'},
 {'severity': 'NIT', 'where': 'agent_judgment.json reader_map.headline_conclusion(对 quality_gate_notes[4])',
  'note': '数字前后空格不统一(「距截止 六十八 天」对「距截止 68 天」)。', 'original': '距截止 六十八 天', 'fix': '距截止 68 天'},
 {'severity': 'NIT', 'where': 'agent_judgment.json l3.contradictions[0].statement 与 [1].statement(C1、C2)',
  'note': '单段长数百字,建议分句分段以利阅读。', 'original': '', 'fix': ''},
 {'severity': 'NIT', 'where': 'agent_judgment.json quality_gate_notes[0]',
  'note': '「共 21 条 snapshot_fact 引用」为条目数(去重后 11 条),建议注明。', 'original': '共 21 条 snapshot_fact 引用', 'fix': '共 21 条(去重 11 条)snapshot_fact 引用'},
 {'severity': 'NIT', 'where': 'agent_judgment.json l3.contradictions[0].statement(C1 同比方向对照)',
  'note': '2025-10 的 2.99 对 2026-10 的 2.44 是否跨日本序列双基期拼接点未点明;幅度与方向远超注册表 0.10pp 告警阈,结论稳健,建议补一句。',
  'original': '对照去年同月(2025-10:欧元区百分之二点一、日本百分之二点九九)', 'fix': ''},
 {'severity': 'NIT', 'where': 'agent_judgment.json reader_map.transmission[0].links[0..2].observed_fact(传导三环)',
  'note': '因 verdict_note 字段不进读者报告渲染,席位把对质「裁定理由」并入 observed_fact 末段并以「裁定理由:」分隔;事实与理由虽已分隔,但置于事实栏易使读者把对质推理读作观测事实,建议拆为独立「对质理由」栏或在栏名注明。',
  'original': '裁定理由: 读数驱动与程序驱动均与在场观测相容', 'fix': '观测事实与「对质理由」分栏呈现'},
]

attacks = [
 'C1·同期性: 若两地观测期不同即为相邻口径冒充 → series_store 两序列最新已发布观测均为 2026-10 期(EA 4.0、JP 2.44;推定发布 11-16、11-20 均不晚于截止) → 攻击不成立。',
 'C1·动量相近是否削弱「分化」: 锚间 EA +1.0pp 对 JP +1.06pp → 受审句已自述「水平与同比方向分化、窗内动量不分化」并列三种起算点(自 2026-06 期 +1.2 对 +0.77、自 2026-05 期 +0.8 对 +0.91,快慢互换),复算一致,未隐瞒 → 攻击不成立。',
 'C1·同比方向相反是否由拼接造成: 日本序列双基期拼接仅影响同月同比后的拼接处且有 >0.10pp 告警阈,−0.55pp 的幅度与方向远超该阈;受审句已披露「双基期档各自同月同比后拼接,非官方公布值直取」 → 不构成问题,留 NIT 建议点明对照是否跨拼接点。',
 'C1·东京读数: 东京都 CPI 在 gate_a.noncore_missing 内却被用作方向佐证 → 属实,但每处已披露;记 MINOR-1,不动摇以全国口径为主的第一主面。',
 'C2·「累计幅度相近」口径: 欧央行宣布值 50bp 对日本月均 +50bp → 受审句明写口径不同「仅作量级对照」;若改用近 12 个月窗,日本月均约 +75bp 而欧央行仍 +50bp,「相近」只在六个月锚间成立,而受审稿限定语正是「最近六个月窗口」 → 攻击不成立。',
 'C2·日本「收紧」方向无宣布值前值: 冻结日历只有目标决议(1.25)与维持确认两条、无前值 → 受审句把方向标【推断】并以月均台阶(0.727→1.227)为据,未以事实位措辞出现 → 攻击不成立。',
 'C2·欧央行决议日为回推: 实际决议日若不同则先后排序变 → 受审句并列「生效日对生效日 8 天」与「回推决议日对决议日 8 天」并标【推断】,写明月频证据下先后未定,结论不依赖单一回推 → 攻击不成立。',
 'C2·水平差口径: 用 MRO 2.65 对 BOJ 目标 1.25 是否拔高分化 → 受审句同时给出 DFR 口径 1.25 与 MRO 口径 1.4,复算相同 → 攻击不成立。',
 'C3·「六项」是否有漏项或无据项: ①–⑥ 逐项对到只读面 → 无无据项;漏掉的是引擎数据需求面「窗内覆盖不足/计划指标缺数」形态,记 MINOR-2。',
 'M1 环1(E1)·路径方向: 「日本逐月上行、欧元区非单调」是否属实 → 窗内 JP 1.53/1.67/1.97/1.98/2.16/2.44 单调不降,EA 于 2026-06 回落至 2.8,月度差距 0.93–1.67pp → 攻击不成立。',
 'M1 环2(E1)·台阶合计: 「合计 +50bp」是否漏算 2026-08 的 −0.1bp(0.978→0.977) → 所列四级上台阶合计 +50.1bp,含该微降后净 +50.0bp,受审句为净额口径 → 一致。',
 'M1 环3(E2)·利差假说未纳入美元端: 是否仍被当作解释 → 受审句标【假设】,写明未纳入 UST_10Y(5.04%)故两解释对本月窗预期相同、尚不能区分,E2 环无事实位措辞 → 相称。',
 'M1 环4(E2)·「读数发布主因」的反证: 11-16、11-20 两日 EURUSD/USDJPY 单日变动最大 0.2293%,四地股指 11-13→11-20 跌幅均不深于 SPX 的 8.61%;但 VIX 两个最大单日跳升恰在这两日(+18.70%/+26.20%) → 主因确实不可区分,受审句结论即「尚不能区分」且归因标【假设】 → 无过度归因。',
 '传导链三环·对质是否偏袒: 三环 face_off_verdict 均「尚不能区分」(支持主解释 0、竞争 0、未定 3),与 quality_gate_notes[1] 自述一致;各环数值逐一直算一致 → 攻击不成立。',
 '传导环1·n=2 的反向观察: 「读数低于峰值仍触发上调」是否被写成规律 → 受审句自陈按日历两档形态计则不成立(决议日前可见读数为 2026-05 与 2026-08 的 3.2),复算一致 → 未写成规律。',
 '情景·可观测性与相容性: S1/S2 阈值互斥互补;3.0–3.5、3.5–4.0、VIX 25–30 三个不触发区间已披露;观测月 2026-11/2026-12 推定入档日 2026-12-16..2027-01-20 晚于截止日且早于时限 2027-02-15 → 截止日读数(EA 4.0、JP 2.44、差 1.56)与 S1 前提相容而未触发,与 S2 前提相反且 S2 自称并列反例情景;证伪指标在册可观测 → 攻击不成立。政策分量须待日历补录,已披露。',
 '历史类比·S6 已有最近类比段而判断档取 0 段: 是否漏用 → 受审档写明 0 段及理由,信封标量与 report.json 一致 → 保守选择且如实披露,不构成问题。',
 '截止日口径·是否把盘中当收盘或混入事后信息: 采集时点 2026-11-23T22:53:47+08:00(纽约 09:53、柏林 15:53、东京 23:53),SPX/VIX/DAX/CAC40 与汇率为盘中快照且逐处标明;全部引用观测日不晚于 2026-11-23 → 攻击不成立。',
 '读者报告·是否与判断档相左: 68 个关键串逐字比对分区一致;三报告中不在判断档的数值 token 均为引擎渲染面并逐一直算一致 → 无相左。',
]

notes = ('零上下文独立复算 ' + str(NPT) + ' 点、偏离 ' + str(NMM) + '(文内数值锚定点 617: 判断档主体 607 点,其中按叶路径定位 543 点、覆盖 429 个不同的(叶路径, token)组合与 46 个字符串叶,另 64 点为日期与月串闭合点;agent_declaration 等其余叶 10 点;其余 660 点为判据、结构与引擎面交叉核对,含判断档数值型 JSON 字段 57 点、MAP 渲染面 67 点与证据索引 60 行解析;另剔除席位脚本空洞点 1 条)。'
 '截止日 2026-11-23(快照覆盖日)、六个月窗 2026-05-23..2026-11-23、点值锚格、同比(EA 2.1→4.0、JP 2.99→2.44、水平差 1.56)、政策面(欧央行两次各 25bp 至 MRO 2.65/DFR 2.5;BOJ 目标 1.25,月均 0.727→1.227 净 +50bp)、资产月窗、转折候选、机制链四环(E1/E1/E2/E2)与传导三环对质(均尚不能区分)、情景阈值互斥互补且可观测(时限 2027-02-15 晚于推定入档日)、诚实缺席六项、截止日盘中口径、契约 STALE(ECB_DFR)与交付门披露,逐一直算一致;三份读者报告判断文字与判断档分区逐字一致。'
 '六查逐项成立,19 条反方攻击均未撼动结论: MAJOR 0。MINOR 2: 东京都 CPI 为 Gate A 缺席指标却作第三转折先行指标与佐证(已披露,取用标准与 C3⑤ 不一);ECB 两指标「窗内覆盖不足/计划指标缺数」的引擎面形态未在判断档点名。NIT 8 为措辞与呈现。裁决 UPHELD。')

V = {'seat': 'semantic-audit-seat', 'reviewer': 'independent-zero-context-seat-r32-n30-round1',
     'verdict': 'UPHELD', 'overall': 'UPHELD', 'notes': notes, 'items': items, 'must_fix': [],
     'counterexamples_sought': attacks, 'recompute_points': NPT, 'recompute_mismatches': NMM,
     'mismatch_details': [], 'audited_at': '2026-11-24'}
# ---- validation (nothing is written unless all pass) ----
assert NPT == 1277 and NMM == 0, (NPT, NMM)
assert len(LEAVES) == 183, len(LEAVES)
KEYS = ['seat', 'reviewer', 'verdict', 'overall', 'notes', 'items', 'must_fix', 'counterexamples_sought', 'recompute_points', 'recompute_mismatches', 'mismatch_details', 'audited_at']
assert sorted(V.keys()) == sorted(KEYS)
assert V['verdict'] in ('UPHELD', 'REVISE') and V['overall'] == V['verdict']
n_major = 0
for it in items:
    assert sorted(it.keys()) == ['fix', 'note', 'original', 'severity', 'where'], sorted(it.keys())
    assert it['severity'] in ('MAJOR', 'MINOR', 'NIT')
    if it['severity'] == 'MAJOR':
        n_major += 1; assert it['original'] and it['fix']
    if it['original']:
        assert it['original'] in ALL, it['original']
assert n_major == 0 and V['must_fix'] == []
assert (V['verdict'] == 'UPHELD') == (n_major == 0)
assert len(attacks) >= 3 + 4 and all('→' in a for a in attacks)
s = json.dumps(V, ensure_ascii=False, indent=2)
W = json.loads(s)
assert W == V and s.encode('utf-8').decode('utf-8') == s
print('VALID ok | points', NPT, 'mismatch', NMM, '| items', [(i['severity']) for i in items], '| attacks', len(attacks), '| bytes', len(s.encode('utf-8')), '| leaves', len(LEAVES))
if dry:
    print('DRY RUN - not written')
else:
    with open(out, 'w', encoding='utf-8') as f:
        f.write(s + chr(10))
    print('WRITTEN', out)
