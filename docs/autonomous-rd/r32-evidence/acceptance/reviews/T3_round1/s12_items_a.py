# -*- coding: utf-8 -*-
"""裁决条目 A 部(MINOR-1..4)。original 须为受审档逐字子串(构建脚本断言)。"""


ITEMS_A = [
 {"severity": "MINOR", "id": "MINOR-1",
  "where": "agent_judgment.json reader_map.turnings[0].narrative;reader_map.transmission[0].links[0].verdict_note(及 observed_fact)",
  "note": "「读数与政策同向演进」只对谷底(2026-02)之后成立: 谷底前的两级 BOJ 月均台阶(2025-12 +7.9bp、2026-01 +17.1bp 至 0.728;快照 series_store.JP_POLICY_RATE)发生在读数仍下行时(JP_CPI_YOY 2025-11 2.9→2025-12 2.13→2026-01 1.51→2026-02 1.27),即政策先于读数拐点、当期反向;传导环 1 的对质注记只列欧元区两条反向观察(371 天、2.9<3.2),日本腿既未做对质也未披露此反向事实。该事实对「读数驱动政策」构成日本腿反向观察,结论「尚不能区分」不变。",
  "original": "谷底月前的 BOJ 月均台阶(2026-01 0.728)与读数随后回升在时间上相邻——读数与政策同向演进,因果方向不可判。",
  "fix": "谷底月前的 BOJ 月均台阶(2025-12 月均 0.557、2026-01 月均 0.728,两月合计约 +25bp)发生在读数仍下行时(2025-11 2.9→2026-02 1.27),读数自 2026-03 才转入回升——时序上政策台阶先于读数拐点,读数与政策的因果方向不可判;并在传导环 1 对质注记增列「日本腿: 2025-12/2026-01 两级台阶先于读数谷底、当期读数下行(反向观察,日本腿未做对质)」。"},
 {"severity": "MINOR", "id": "MINOR-2",
  "where": "agent_judgment.json l4.scenarios[S1-STICKY-TIGHTEN].rows.trigger.condition 与 falsification.threshold",
  "note": "S1 前提为「欧元区 HICP 同比维持 3.5% 以上」、证伪阈 3.5%,触发阈却为 4.0%: 观测月读数落在 3.5%–4.0% 时粘性前提成立、既不触发亦不证伪,该不可判定区未在 S1 文本披露(QGN[3] 只披露了 S2 的 3.0%–3.5% 区间)。触发/证伪均可观测,不构成 MAJOR。",
  "original": "观测月 2026-11 或 2026-12 的 EA_HICP_YOY 同比 ≥4.0% 且同观测月 JP_CPI_YOY 同比 ≥2.0%",
  "fix": "观测月 2026-11 或 2026-12 的 EA_HICP_YOY 同比 ≥4.0% 且同观测月 JP_CPI_YOY 同比 ≥2.0%(触发阈 4.0% 高于前提水平 3.5%: 读数落在 3.5%–4.0% 时前提成立而不触发、亦不证伪)"},
 {"severity": "MINOR", "id": "MINOR-3",
  "where": "agent_judgment.json l4.scenarios[S1-STICKY-TIGHTEN].rows.falsification.threshold(S2 对应处写有日本分量证伪阈)",
  "note": "S1 的日本分量(前提「维持 2.0% 以上」、触发 ≥2.0%)无数值证伪阈,而 S2 写有「或 2026-12 观测月日本全国 CPI 同比不低于 2.0%,收敛情景的日本端分量同样被证伪」;QGN[3] 称证伪指标(EA_HICP_YOY/JP_CPI_YOY)在册可观测,但 JP_CPI_YOY 在 S1 只出现在触发条件、不在证伪条件,两情景不对称。",
  "original": "若观测月 2026-11 与 2026-12 两月欧元区 HICP 同比均低于 3.5%(前提水平),粘性假设被证伪",
  "fix": "若观测月 2026-11 与 2026-12 两月欧元区 HICP 同比均低于 3.5%(前提水平),粘性假设被证伪;或 2026-12 观测月日本全国 CPI 同比低于 2.0%,日本端分量同样被证伪"},
 {"severity": "MINOR", "id": "MINOR-4",
  "where": "agent_judgment.json l4.scenarios[S1/S2].rows.falsification.threshold 与 trigger.condition(共四处);quality_gate_notes[3]",
  "note": "「欧央行分量须待日历补录后方可核验」偏强: 按受审稿自述「发布面=序列变更日」,已生效的欧央行上调(或未上调)自 ECB_MRO/ECB_DFR 序列面即可核验(本窗两次变更正是由序列面核得);须待日历补录的只是「已决议而尚未生效」的情形。表述偏强,不影响本轮结论。",
  "original": "欧央行分量须待日历补录后方可核验",
  "fix": "欧央行分量以序列变更日(生效日)或日历补录任一面核验: 已生效的上调自 ECB_MRO/ECB_DFR 序列面可核,仅「已决议而尚未生效」须待日历补录"},
]
