# -*- coding: utf-8 -*-
"""复算清单的覆盖项说明与不立项注记。"""

DESC = {
 "①研究截止日": "截止日=快照版本日 2026-11-23(report.json research_plan.point_anchors[*].as_of、run.evidence_gate.as_of、快照 target_date 与 research_as_of;C2/头条/QGN 文字一致)",
 "②点值锚格": "6 格的锚标签/指标/观测月/值/状态;12 条 anchor_echo 与快照序列逐值比对",
 "③同比": "去年同月值与差值、近十二个月位次、一/三/六个月前差值、序列极值与谷底月",
 "④政策面": "ECB 两序列变更日与前后值、距截止天数、非周三观测计数、决议日回推;BOJ 日历决议日/生效日/目标值/距截止天数;月均台阶与变动点",
 "⑬'央行目标/通胀同比": "两地央行当前目标利率的数值/生效日/现行有效/待生效分记;通胀同比的基期与数值",
 "⑤三利率分解": "名义/实际/盈亏平衡变动 bp、窗口与恒等式",
 "⑤资产月窗": "四行回贴涨跌幅、窗口与 window_months",
 "⑥转折判断": "三段转折的先行/同向/叙事逐值;候选面与谷底月",
 "⑦传导链": "M1 四环文本全部数字(通胀、政策、汇率、资产)",
 "⑦传导链(reader_map)": "头条、两地区段、传导三环的观察/假设/预期/对质注记",
 "⑧历史类比": "S6 扫描/有效/TOP1 数字与 0 段",
 "⑨情景": "五行齐备、触发/证伪阈、期限与可观测性、互补方向",
 "⑩一致性": "判断档对 report.json L3/L4、三个渲染文档、20 条引用、E1/E2 标注、声明计数",
 "⑫盘中口径": "采集时刻四地换算、截止日值在场性、同日收盘口径可用性",
 "⑬非VERIFIED披露": "契约验证各项状态与判断档披露",
 "⑭缺口披露": "判断档缺口披露对 run.data_requirements",
 "⑭代码缺口": "判断档所述引擎缺口对安装树代码与引擎报告文字",
 "⑪诚实缺席": "东京基期缺席、noncore_missing、JP_POLICY_TARGET 不可得",
}

NOTES = [
 "日本 2026-10 与 2025-10 两读数是否同属一个基期: 注册表 JP_CPI_YOY.release_semantics 与 calc 仅载「各自基期内做严格同月同比后拼接(新基优先,重叠差>0.10pp 告警)」,未载两观测月各属哪一基,引擎面不可判;受审稿已披露拼接口径(2025基/2020基 拼接),不立项。另: 注册表 calc 的覆盖描述止于 2026-09,而快照已含 2026-10 观测,属注册表描述滞后,非受审稿问题。",
 "「净 +75bp=六个变动点之和」: 以整数 bp 非零计为 6 个变动点;严格不等比较为 8 个(另含 2026-04、2026-08 两次 −0.1bp 舍入微降),六级之和 75.1bp、净变动 74.9bp(1.227−0.478),在所述精度内一致。",
 "quality_gate_notes[5]②后半(机构归因式引用跳过)仅静态面可核: text_consistency.ALIASES 无 JP_CPI_YOY/EA_HICP_YOY/JP_CPI_TOKYO_YOY/JP_POLICY_TARGET/ECB_MRO 五键,契约验证 5 项指标均属别名表;③「已登记待用户裁定是否立研发项修复」在本席边界内不可核验——本轮 run.evidence_gate.historical_view=false、publication_basis=snapshot_presence,③不影响本轮结论。",
 "引擎契约 six_checks 共 16 项(C1–C3 各 relevant/supports/competing/opposing,S1/S2 各 overreach/falsifiable)引擎面均 VERIFIED,属在场性与格式核验;本席六查为实质复核,独立于该结果作出。",
 "引擎交付门(blocked_class)不在裁决范围: 本轮 run_ok=true、allow_failed_run=false、validation passed=true(violations 空)。semantic_review.seat_invoked=false、verdict=null 为裁决缺席时的预期状态;MAP/FULL/report 中「语义审查(席位待唤起)」类文字不属判断内容。",
 "受审版本指纹: agent_judgment.json、report.json、MAP_REPORT.md 的 sha256 与部件脚本运行时记录一致(构建时复核);冻结输入 overlay 与安装树逐字节相同,并与 report.json run.frozen_inputs 一致。",
 "受审稿中的说明性括注(如「ECB_MRO,政策目标口径」「操作下限口径」「东京都CPI同比…先行口径」)为席位自加文字: 注册表两序列 asset_class 同为 policy_rate、未作目标/下限之分,该说明与两利率定义相符;除 NIT-4 的「中旬」外不立项。",
 "本席未读取既往审查史,亦未读取安装树 audit/ 目录;点数由规程覆盖要求自然产生,未对齐任何既往数字。",
]
