# R31 任务2 — 运行中 _v2 落盘实录(会话 A)

- 12:07 会话 A 启动(裸问句,树=/tmp/r31-accept/install,CODE_VERSION=ca916cd)
- 12:09:26 watcher 捕获 S3 数据子命令进程(run_research 已钉死入口输入)后,
  将当日 base 快照克隆落盘 `research_snapshot_20261122_v2.json`
  (snapshot_id 按身份协议改 `_v2`,加 `r31_v2_mark=true`)
- 判据(会话 A 归档后核对):
  1. A 的 frozen_inputs/root_overlay 快照字节 = 入口 base 字节(_v2 不入档)
  2. A 运行中途本地出现 _v2 → 同次运行两次读数不串号(钉死)
  3. 随后新工单(会话 B 同树)正确选中 `_v2`(释放+重解析)
- watcher: /tmp/r31x/drop_v2_r31.sh(只动验收树,LIVE 零写入)

## 会话 A 第一跑(20261122T040939Z)— 环境性草稿,非代码回归

- 快照继承自 LIVE 晨跑(n=78,EA/JP/CN 宏观史缺席,LIVE 自身 1117-1122
  快照同形;日常文件从不携带宏观史——史由快照重建时向源端抓取)
  → 当日快照在场→采集跳过→无史增补→地图核心维缺(map_core_dimension_missing)
  → 草稿交付+归档拒绝(评审席 UPHELD 但可交付门拒,blocked=not_deliverable)
- 树面修正(环境修复,零代码改动): 还原当日 china/ea/japan 源文件
  (LIVE 只读复制)+删当日快照(含 _v2)→会话内采集步重建快照+向源端
  抓史(R30 A3 同路径,n=88 含 EA_HICP/GDP+CN 七序列+JP 三序列)
- 会话 A2(重跑)=正式验收跑;watcher2 重挂(_v2 中途落盘实录以 A2 为准)

## 通道修复与正式跑(A3)

- 树内通道重采(采集侧四采集器)+china 序列节自同日 superseded 完整面
  嫁接(series_source 随档披露)→快照重建 n=88(EA4/CN5/JP4,与 R30 A3
  数据面同形;Gate A DEGRADED,core 缺失 0)
- watcher2 曾在 A2 会话以 1121(n=9)基面落盘 _v2——该实例场景基面退化,
  不作数(已清);正式实录=watcher3+A3

## A3→A4(通道二次补全)

- A3(20261122T053629Z)跑于 n=88 面: EA/JP/CN(除 PMI)齐,CN×growth 组
  零 ok 格(CN_PMI_MFG 全史缺席——macro 通道 fetch_macro_history 于
  A3 会话内失败且续存源档亦缺)→ 草稿面,如实披露,未归档
- 通道补全: merge_cn_history 以当日新采(n=226,2026-11-22T12:04Z,
  mode=fresh)并入 macro_20261122.json → 快照重建 n=90(CN 七序列齐)
- watcher3 的 _v2(旧 n=88 克隆)已清——A4 于 n=90 基面起跑,watcher4
  以 n=90 为基落盘 _v2;正式实录=watcher4+A4;B 随后须选中该 _v2

## 判据核对(A4 归档面)

- watcher4 于 20:09:12 落盘 _v2(n=90 基面克隆,mark=true)
- A4(20261122T120924Z)root_overlay 快照 sha16=eabee6b470a8e959
  =当日 base 字节,**无** r31_v2_mark/snapshot_id 带 _v2 → 中途落盘的
  _v2 未入在飞运行(判据 1+2 ✓)
- A4 正式归档(操作者 archive 段): rc=0,run_code_git_head=ca916cd,
  verdict=UPHELD(链 1 档),九件套+root_overlay 三件+ARCHIVE_MANIFEST 齐
- 判据 3(新工单选 _v2)= 会话 B2(随后,同树)

- 判据 3 ✓: B2(20261122T125710Z)root_overlay 冻结件
  =research_snapshot_20261122_v2.json(mark=true)——A4 运行中落盘的 _v2
  被释放后的新工单正确选中;三判据齐
