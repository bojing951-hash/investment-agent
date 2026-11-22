# NEW30(裸年月+单一相对窗,任务1 NEW30 回归)证据

## 问句

`question_verbatim.txt`(=acceptance/questions/question_NEW30.txt,R30 NEW30 原句
直承: 「2026年11月,日本和欧元区最近六个月的通胀与政策环境有什么不同?…」)。

## 任务1回归核心(机器面)

R30 时该问按 R11/R12 冻结契约判多范围 unparseable(裸年月+最近六个月),
以 --allow-failed-run 降级随档;R31 修复后正式解析:

- `as_of_declared`: as_of=**2026-11-30**,basis=「裸年月 2026年11月 按月末时点化
  为研究截止日 2026-11-30,与单一相对回看窗合并(一个截止日+一个回看窗;真冲突
  组合仍拒绝)」,`differs_from_snapshot=true`(快照 target=20261122,如实披露
  不静默改判);
- 窗=months 6,**2026-05-30..2026-11-30**(source=最近六个月),地图 6个月前锚
  4/4 组 ok;
- 渲染面时点口径披露行在场(全部窗口/锚点/政策面绑定时点,数据=当时已发布面)。

## 会话与裁决链(真实席位,REVISE→修订→UPHELD)

1. 会话 NEW30(22:50–23:19): plan→attach(VERIFIED,violations=0)→report
   (machine_verified=true,L3/L4 produced)——席位后台独立审查子代理被
   「Background tasks 10m」天花板杀,裁决未落(席位如实停等,日志在场)。
2. 独立审查席 NEW30RV(操作者启动,零上下文): **REVISE** 必修 1 项——M1 环1
   [E1]「持续高于日本约 1.3-1.9 个百分点」与冻结快照逐月复算(0.93–1.67pp,
   2026-07 下界仅 0.93)不符,事实陈述携错数,五处副本(agent_judgment/
   judgment_agent_v1/report.json 内嵌/report.md/FULL_REPORT);140+ 数字点其余
   全过,4 NIT 登记(verdicts/-01,reviewer=independent-semantic-review-r31,
   REVIEW_REVISE_REQUIRED.md 含逐月复算表随档)。**席位存在理由第五证:
   独立复算抓出汇总区间错数**。
3. 修订席 NEW30FX(02:33–02:37): 仅改必修句(→约 0.93-1.67 个百分点)于
   agent_judgment+judgment_agent_v1,重跑 attach(VERIFIED)+report×2(首跑
   copies_consistent=false=合法修订变化写盘顺序,二跑全绿),旧句六文件零残留,
   其余内容零改动。
4. 复审席 NEW30RV2(02:38–02:44): **UPHELD**(rev=2,predecessor 链完整)——
   必修修毕逐字核验+引擎面逐月差 [0.93,1.67] 逐位吻合+130+ 数字点本轮独立
   复算全过+无新引入问题;3 NIT 登记(reader_map 未渲染面混合口径等)。
5. 操作者归档(02:4x): `--stage archive` rc=0,verdict=UPHELD,verdicts_n=2,
   完整包 10 件+root_overlay 三件+ARCHIVE_MANIFEST(run_code_git_head=ca916cd)。

## 文件清单

- `MAP_REPORT.md`(.sha256)+`FULL_REPORT.md`+`report.md`/`report.json`(修订后终版)
- `agent_judgment.json`+`judgment_agent_v1.json`(修订后)+`views_digest.json`
  +`evidence_index.json`+`AGENT_SEAT_ENVELOPE.json`
- `verdicts/`(01 REVISE→02 UPHELD 链)+`REVIEW_REVISE_REQUIRED.md`
- `ARCHIVE_MANIFEST.json`+`archive_receipt.json`(rc=0)
- `root_overlay/`三件字节副本(冻结快照=research_snapshot_20261122_v2.json)
- seat_NEW30/NEW30RV/NEW30FX/NEW30RV2.log(私有根已 ~ 归一)
