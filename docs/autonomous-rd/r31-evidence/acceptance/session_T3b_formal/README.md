# T3b(任务3定向探针,地图形状问)证据

## 问句

`question_verbatim.txt`(=acceptance/questions/question_T3.txt,重写带「通胀与政策环境」
形状词版;初稿空面留档 `../session_T3_first_empty/`)。

## 正式链结果(2026-11-22 22:08–22:49,树=/tmp 接受树 @ ca916cd)

- `research-one` 正式闭环: plan → Agent 研判 **4 轮契约迭代**(judgment_agent_v1..v4
  随档)→ attach 机器校验 VERIFIED → 独立语义审查 **REVISE→修订→UPHELD**
  (裁决链 2 档: verdicts/VERDICT-…-01=REVISE, -02=UPHELD,predecessor 链接完整),
  `deliverable=true`,run_ok=True(48 步)。
- **任务3三修复的正式消费面**:
  1. 政策表**决议公布日/生效日双列分记**(BoJ 09-18 决议→09-24 生效;ECB 09-10
     决议→09-16 生效),「已决议未生效」窗判定=无(窗内全部可核行动已生效),
     且【尚未验证】注记 ECB 序列止于 09-16+DEGRADED——结论仅覆盖引擎可见面;
  2. 同比对照=**同观测月 2025-10 基期**(JP 2.44 vs 2.99 低 0.55pp;EA_HICP 4.0
     vs 2.1 高 1.9pp),东京都 CPI 序列 2026-01 起**基期不可得→对照不可判**(缺基期
     如实标注,不以相邻月冒充);
  3. 官方目标口径分记: 日本宣布值(日历实录,注册表无 JP_POLICY_TARGET 序列)与
     月均市场口径(1.227)并列不混同,月均 12 个月净 +67bp 与决议-生效记录相容。
- 发布日期如实: 通胀读数发布日=推定规则(非实录),CPI/HICP=事后回顾口径披露。
- 席位发现引擎缺口三项(obs_run 锚标签硬编码/数值别名表缺四个 ID/东京 CPI 推定
  发布日晚于截止日张力)——登记 R32 候选,如实呈报未擅自修。
- 归档停等用户裁定(席位纪律正确);本目录=会话级证据,root_overlay 三件随档
  (冻结快照=`research_snapshot_20261122_v2.json`,r31_v2_mark=true)。

## 文件清单

- `MAP_REPORT.md`(读者版)+`MAP_REPORT.sha256`+`FULL_REPORT.md`+`report.md`/`report.json`
- `agent_judgment.json`(终版)+`judgment_agent_v1..v4.json`(契约迭代全程)
- `views_digest.json`+`evidence_index.json`+`AGENT_SEAT_ENVELOPE.json`
- `verdicts/`两档裁决链 · `root_overlay/`三件字节副本 · `seat_T3b.log`(私有根已 ~ 归一)
