# F10 可独立重放证据包(Audit-R2 条目4)

目标: 任何人在干净目录, 不依赖本机 `~` 或 `/tmp` 路径, 一条命令复算
F10 受测席的全部统计输出, 并与归档输出逐字节比对。

## 一条命令重放

```sh
sh docs/autonomous-rd/phase4/F10/f10_replay.sh
# 期望输出: F10 REPLAY PASS: 6e5fcf4a58b83370c32389c013ea36c4ab34e4b559b132ac951a864e6e514d3f
```

脚本行为: 临时空目录 → 拷入 `f10_calc.py` + `data_slice/`(原始输入切片)
→ `IA_ENGINE_ROOT=<临时目录>/engine python3 f10_calc.py` → 输出 sha256 与
归档 `f10_calc_output.json` 比对。已在本机验证 PASS(切片重放与引擎树
原跑逐字节一致)。

数据根可配置: `f10_calc.py` 读环境变量 `IA_ENGINE_ROOT`(缺省
`~/investment-agent-dev`, 本机口径), 指向任何含
`data/daily/{research_snapshot_20261112_v2.json, macro_20261112.json}`
布局的目录——切片目录即按此布局构造, 重放不依赖 home//tmp 绝对路径。

## 包内清单(证据包完备面)

| 件 | 说明 |
| --- | --- |
| `question_prereg.json` | 原始研究问题(预注册, 逐字) |
| `f10_calc.py` | 计算脚本(方法自选留痕 M1-M9; 数据根可配置) |
| `data_slice/` | **原始输入切片**(非计算输出): BRENT_F/WTI_F 逐值拷贝自 research_snapshot_20261112_v2.json, BEI_10Y/BEI_5Y 逐值拷贝自 macro_20261112.json, schema 形状与源文件同 |
| `f10_calc_output.json` | 冻结计算输出(重放比对锚, sha256 见上) |
| `judgment_mvp.json` | 研究席判定档(源) |
| `evidence_pack_agent_judgment.json` | attach 落位后判定档副本(与 run 目录逐字节一致) |
| `report.json` | run 目录 report.json 副本(规划/执行/事实/证据索引/审查态全量) |
| `views_digest.json` / `evidence_index.json` | run 目录对应件副本 |
| `report.md` / `FULL_REPORT.md` | 终渲报告两视图(与 run 目录逐字节一致) |
| `MANIFEST.md` | 过程台账(plan/attach/report 各段命令与结果) |
| 本文件 + `f10_replay.sh` | 重放入口 |

修订历史与裁决链: `report.json.semantic_review` + 产品仓
`audit/semantic_review/20261116/VERDICT-20261116T114933Z-*.json`
(rebind 迁移: -01 旧锚 → -02 content_digest v2 重绑, 见 MANIFEST)。

## 版本记录(三处分离)

| 层 | 版本 |
| --- | --- |
| 编排代码(本仓 ia_cli.py / research_orchestrator.py / scripts/agent_judgment.py 等) | 受审 commit `06e90c18970bb23536af47666e03b6d0047c824c`(dev/audit-fix-r1, PR #1 审计对象); 本证据包由该分支后续 Audit-R2 修复提交冻结(以包内文件自校验为准: 脚本+切片+输出 sha 链) |
| 执行/数据引擎树(`~/investment-agent-dev`) | git `ad2f6e4951edd97fac007317108bb6cdd833ff21`(2026-11-16) |
| 数据版本 | `research_snapshot_20261112_v2.json` sha256 `e2e9152557bd7bb86ca53485069ee1874acf91504c255c541dbd7aec12191769`(snapshot_id=research_snapshot_20261112_v2, target_date=20261112); `macro_20261112.json` sha256 `186b767c7fea77cd67172b0137d9a326c3ae80fd9925f976be84b192f834b11e`; 切片文件 sha256: 快照切片 `5635a20eaac79657098425a07f72dbeb452f85a6f98ba3f07ec73e5057514b3c` / 宏观切片 `209e80645ad84630aca69f10e67d1b8c4e4713d2f139c2a28d8b38a648b58ddf` |

切片序列规模: BRENT_F n=2515 / WTI_F n=2514(2016-11-14..2026-11-11);
BEI_10Y n=2498 / BEI_5Y n=2498(2016-11-14..2026-11-10)。

## 校验清单(重放者自查)

1. `sh f10_replay.sh` → PASS(输出 sha256 与归档一致)。
2. 切片文件 sha256 与上表一致(防切片被换)。
3. `judgment_mvp.json` 与 `evidence_pack_agent_judgment.json` 的差异仅为
   attach 台账面(内容原文一致); `report.md`/`FULL_REPORT.md` 与
   `report.json` 的 semantic_review 面一致(渲染自同一 report.json)。
4. 裁决档 content_sha256 与产品仓 `scripts/agent_judgment.py` 的
   `content_digest(run 目录)` 一致(审查-交付同版绑定)。
