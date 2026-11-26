# Seat-A 判断席规程(Audit-R23 一问验收,零上下文)

本文件只含程序,不含任何研究内容/结论/数字。你是独立判断席,在隔离树
/tmp/r23 内完成一份研究工单的判断与正式装配。

1. 环境核验: 读 /tmp/r23/CODE_VERSION.json(印章 git_head)与
   data/daily/ 通道面清单;确认 research_snapshot_*.json 缺席(须由你建)。
2. 工单: 读 /tmp/r23/run_question_verbatim.txt——只此一次,即工单全文;
   不得引入外部信息,不得联网,不得读 research_archive/ 旧档。
3. 建快照(纯本地): cd /tmp/r23 && python3 scripts/snapshot_builder.py
   --date 20261119
4. 正式计划: python3 ia_cli.py research-one --stage plan
   --question "$(cat run_question_verbatim.txt)" --out-dir output/r23map
   --engine-root /tmp/r23   (cwd=/tmp/r23)
   run_ok=False 时按输出修程序性原因重跑;成功 run_ts 为准。
5. 判断产出: 读 <run目录>/AGENT_SEAT_ENVELOPE.json,写
   <run目录>/agent_judgment.json。一切数字/日期/方向取自引擎面(点值/
   序列信封/转折候选/快照事实);缺席=如实缺席,不编造;遵守 envelope
   纪律字段与仓内文档的判断纪律(月频同步=先后未定等)。
6. attach: python3 ia_cli.py research-one --stage attach --report-dir
   <run目录> --engine-root /tmp/r23 --judgment <run目录>/agent_judgment.json
   被拦=只按机器反馈修订 judgment 文本(不动引擎面/校验字段),迭代至
   attached=True 且 contract_verification 无 CONTRADICTED/NOT_VERIFIED。
7. report: --stage report 同参数。预期 deliverable=False(独立语义审查
   待裁)。到此停止: 不自任审查席、不 record 裁决、不归档。
8. 留痕: 每步命令+关键输出摘要写 /tmp/r23/output/SEAT_A_LOG.md。
