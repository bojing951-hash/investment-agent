# C2 实雷记录 — run_ok 门压制地图草稿类判定(修复=b7f9ccf §E)

- **会话**: C2(残缺树 install-degraded,缺当日 ea 面;树 SHA=37b8713)
  原问 A(全球宏观变化地图)完整跑通,EA 增长+EA 通胀核心组零 ok 格,
  run_ok=False(TIPS_10Y 等源端诚实缺席置 False,与 EA 无关)。
- **缺陷实录**: 操作侧 `--stage archive` **成功**(arc_C2/arc_C2b 两份,
  ARCHIVE_MANIFEST 见本目录)——旧 `blocked_class_of` 把全部地图内容类
  判定包在 `if run_ok is not False:` 门内,run_ok=False 时整支跳过→
  `optional_data_missing` 放行。与 Audit-R20 起草稿合同(核心维度缺数
  =交付草稿、不进正式归档)相反。
- **修复**(b7f9ccf): 地图问句先判内容类(与 run_ok 解耦),run_ok 门只
  保留给非地图问句;地图内容全绿且 run_ok=False 照旧落
  `optional_data_missing`(B2 合法交付形态保形)。门 §E 五判据钉死。
- **修复后复核**(同报告、修复代码直调):
  - arc_C2 report → `blocked_class_of` = **map_core_dimension_missing**
  - arc_B2 report(内容全绿)→ `optional_data_missing`(不变)
- **同 SHA 端到端正口**: 见 session_C3_degraded_fixed/(b7f9ccf 树重跑
  C 会话→草稿→归档拒绝实录)。
