# Audit-R30 任务1 真实会话同日 _v2 中途落盘实录(会话 A3)

- 验收树: /tmp/r30-accept/install @ `59dcc096fff5138429105214bbd24ccd3ce003bb`(git archive+CODE_VERSION 印章)
- 钉死路径: 会话 A3 的 plan 段进程在 `run_research` 入口(第一次取数前)经
  `wd.latest_snapshot` 解析当日快照并置位 `IA_SNAPSHOT_PIN`
  (scripts/research_orchestrator.py 入口块;env 继承到 S2..S13 各 ia_cli 子进程)
- 落盘: 22:47:29(北京时间)S3 数据子命令期间,`research_snapshot_20261121_v2.json`
  克隆落盘(身份协议合规: snapshot_id=`research_snapshot_20261121_v2`/
  target_date=20261121;加 `r30_v2_mark=true`+`r30_v2_dropped_at` 可观测标记)
- 旧工单全程原版(实测):
  - run ts_utc=20261121T144742Z,git_head=59dcc09(code_version_stamp)
  - `run.frozen_inputs['data/daily/research_snapshot_20261121.json']='fb1992a5396e033c'`
    = **base** 摘要(_v2 摘要=1814977e3010e505,不同)
  - 归档包 `root_overlay/data/daily/research_snapshot_20261121.json` sha256 前16
    = fb1992a5396e033c = base 字节副本
  - 终裁 VERDICT-20261121T144742Z-01 绑定 frozen_inputs_sha256(与报告/清单三处一致,
    重放 [0] 严格面 frozen_inputs_match_report+verdict_binding_threeway 双绿)
- 新工单能选新版(实测,会话后即时): 无钉死新进程
  `wd.latest_snapshot` → `research_snapshot_20261121_v2`(r30_v2_mark=true);
  移除 _v2 后回落 base(恢复后续会话干净面)
- 时间线旁证: _v2 birth 22:47:29 < run 目录 birth 22:47:42(目录在 S3 首步产出时
  落名)——落盘发生在钉死之后、运行期内,非运行前
- 后续会话(B3/OPEN3/T3/NEW30)在 _v2 移除后的干净 base 面上进行,
  各自 frozen_inputs 同为 fb1992a5396e033c
