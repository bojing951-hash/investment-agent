# 独立语义审查席规程(Audit-R23 一问验收,Round-1,零上下文)

本文件只含程序与工单原文,不含任何判断内容。

- 工单原文(run.question 逐字): 给我一份全球宏观经济变化地图：美国、中国、欧元区、日本在12个月前、3个月前和最新一期的宏观指标横向对比，重点看增长、通胀、就业与政策利率四条线，以及主要资产表现。另外找出与当前宏观状态最像的三个历史时段（12个月以上之前），说明相似点、关键差异，当时其他经济体是否同步，随后3、6、12个月经济和主要资产实际怎么走？
- 受审运行目录: /tmp/r23/output/r23map/20261119T173248Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_日本在12个月前_3个月前和最
- 隔离树: /tmp/r23(CODE_VERSION.json 印章 git_head=b316e88…,report.run 同值)
- 边界: 只读复算(可运行树内脚本/引擎公开接口做独立计算,但不得修改
  run 目录任何受审文件、不得改引擎代码、不得联网、不得读
  research_archive/ 旧档、不得读 /tmp/r23v)。
- 复算覆盖要求(最低 40 点,逐点独立于 report.json 转述——从快照
  series_store 与引擎接口直算):
  ① 点值锚格(每地区×维度×锚的值/日期/缺席理由抽全)
  ② 政策利率面(决议/生效口径,一年窗净变动)
  ③ 三利率分解双窗(名义=实际+盈亏平衡,基点对账)
  ④ 资产月窗(端点日期与值)
  ⑤ 传导链各环 observed_fact 与区分指标观测
  ⑥ 转折判断与候选面(前值→后值/窗口)
  ⑦ 历史类比两段: 相似/差异/同步性叙述所引数字、当时可知面(known
     行五字段绑定)与事后段迁移是否正确、逐窗并列面行值
  ⑧ 总判断/走位文字与数值一致性(方向词/单位/精度)
  ⑨ 情景阈值/期限表述
  ⑩ 诚实缺席项是否属实(序列级证实)
- 裁决: MAJOR=数字/日期/方向错或与证据相左;MINOR=口径披露可改进口;
  NIT=行文。零 MAJOR 且无 REVISE 级问题 → UPHELD。
- 产出两件到 run 目录 verdicts/ 下:
  1) PROSE-round1.md(复算清单+逐项结论)
  2) VERDICT-round1.json: {"seat":"semantic-audit-seat","reviewer":
     "independent-zero-context-seat-round1","verdict":"UPHELD|REVISE|FAIL",
     "items":[{"severity":"MAJOR|MINOR|NIT","note":"..."}],
     "recompute_points":N,"audited_at":"<今日>"}
- 不调用 record_semantic_verdict(登记由操作席执行)。
