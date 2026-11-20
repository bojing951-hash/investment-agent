# Audit-R26 交付报告(R71)

基线 6ef8a70(R25 尖,PR #1)→ 2bc61f5(任务1-4 实现)→ b4b6382(电池
整备)→ **2953c29(验收增补: 缺数/锚覆盖草稿横幅三侧共源)**,全部在
dev/audit-fix-r1(PR #1)。用户验收令四任务对应本报告四节;新门
tests/test_audit_r26_gate.py 46 判据(含 §E 缺数/锚覆盖十判据);回归
r7-r25 七门全绿;全量电池与 CI 见第 5 节;两席真实一问会话+残缺数据会话
见第 4 节。

## 0. 环境与既成状态

- 验收令四任务(用户原文): ①同日采集守卫(按指标身份和有效观测判降级,
  CPI 删除/CPI 全 null 两反例保旧档,正常数值修订放行,先候选后原子替换,
  写盘中断/同日并发旧档始终可读)②最新一期三日期分离(统计期末/发布日期/
  政策最后确认日;美欧日 Q3 GDP+ECB 正例、EA HICP 停 2025-12 反例;
  必要维度只剩确证过期值→首页标草稿、正式归档拒绝;附逐组覆盖与实际数据
  来源)③历史章节(三段类比「当时是否同步」只用截止日前已公布证据,后续
  观察移入事后结果;日本隔夜拆借月均只作市场观测;BoJ 2024-03-19 决议/
  03-21 生效回归;保留 R25 发布日与数字校验)④重新验收交付(冻结记录实际
  运行 SHA;新会话免预置问题文件,当轮消息生成独立原问文件;真实原问跑
  完整链,换问验证计划收到新原文;正常日常采集与残缺数据各跑一次;隔离
  副本从交付包直接验证原问/运行SHA/裁决链/地图哈希;新版归档与旧档并存)。
- 运行 SHA=**2953c29**(git archive 干净树+CODE_VERSION.json 印章,
  R7-03 三级链第三级;引擎树无 .git 时 run.git_head 不再 None)。
- 验收树=/tmp/r26 隔离副本(2797 件),LIVE 数据树只读复制历史面,当日
  china/ea/jp/japan 面由本树采集器重采(R20 顶层 series 节面形,LIVE
  v0.24 面形适配器不可读=attempt-1 十格缺数的根因之一)。

## 1. 同日采集守卫(任务1)

- **判据=指标身份×有效观测**(`research_provenance.daily_face_guard_write`):
  覆盖指纹=(序列路径集,叶子计数),null≠有效观测;降级⟺严格路径子集
  或同构路径∧叶子缩水;正常数值修订(同路径同叶子数,值变)放行。
- **本轮真实验证(非合成)**: 当晚采集中守卫三次实拦——
  - macro 面 FRED 晚间 null 尾(data.AHE 等 14 项各缩 2 obs)三轮全
    转存 superseded/,规范面不被覆盖(转存件 4 份在档);
  - china 面 series.CN_OMO_7D 402→34 缩水轮转存,规范面保全
    (5 序列 n=226/250/1540/201/15 完整);
  - 前轮(attempt-1 时段)CN akshare/EA HICP 端点/JP statgo 三源晚间
    抖动降级面全部转存,规范档可读(round1-evidence/superseded 9 件)。
- 反例回归在 r26 门 §A-§D(含 CPI 删除/全 null 保旧档、写盘中断、
  同日并发),R25 门 55 判据全绿非回归。

## 2. 最新一期三日期分离(任务2)

- 统计期末/发布日期/政策最后确认日三列分记(release_calendar v1.4.0+
  decision_kind);逐组覆盖表逐锚披露(见 4.1 会话 A 地图「逐组覆盖与
  实际数据来源」表: 21 锚×三时点×统计期末×发布日期×来源全列)。
- 正例(验收工单): 美 Q3 GDP(统计期 2026-09-30/发布 2026-10-29 BEA
  实测锚定)、欧 Q3 GDP(2026-09-30/2026-11-04)、日 Q3 GDP(2026-09-30/
  2026-11-14)、ECB 政策(决议日 2026-09-16 当日公布=变更日观测)。
- 反例: EA HICP 停 2025-12(R9 既档)→ stale 渲染+滞后天数披露,
  本轮真采恢复 n=358 last=2026-10-01。
- **草稿三横幅**(2953c29 增补,三侧共源 research_map_planner):
  核心维度组缺数(零 ok 格)/锚覆盖不足(ok 锚<2∧空锚无经证实延误依据)/
  只剩确证过期值;渲染(agent_judgment.blocked_class_of)/首页横幅/
  归档 belt(ia_cli._r1_archive_core)同源判定;SKILL 步骤4 增草稿纪律
  (draft_delivered=true 须声明+不得提供立即归档选项)。
- BoJ 双轨: JP_POLICY_RATE=月均隔夜(市场观测,四分注记),决定面
  decision_kind=boj_history 走 2024-03-19 决议/03-21 生效实录;
  JP_POLICY_TARGET 计划指标不在注册表=诚实披露不以相邻口径冒充
  (边界节原文「日本政策目标宣布值序列不可得」)。

## 3. 历史章节(任务3)

- 三段类比表四列: 段(距离)/相似点关键差异/当时其他经济体同步?/事后
  3-6-12 月实际(月末复算窗)——「当时是否同步」逐项用截止日前已公布值
  (欧 HICP 可知值 2.3、中 PPI -2.2 等当时可知口径),事后演变全部移入
  事后列(独立语义审查席 4 条轻微备注之一即此类: 2025-03 差异句引统计期
  值 vs 当时可知值,下方两表已正确分列——备注级非阻断)。
- 日本隔夜月均只作市场观测(地图 JP×policy 行=月均序列+四分注记),
  决议/生效日分记见第 2 节;R25 发布日与数字校验保留(r25 门 55 绿)。

## 4. 重新验收交付(任务4)

### 4.0 冻结与运行 SHA

- 实际运行 SHA=2953c29(CODE_VERSION.json 印章
  stamped_at=2026-11-20T21:05:34+08:00);会话报告 run.git_head=
  2953c29|source=code_version_stamp(隔离验证 §2 PASS)。

### 4.1 会话 A: 真实原问完整链(正常日常采集)

- 零上下文新会话,唯一输入=原问句文件(-p 传参);会话首动作落盘
  question_verbatim_20261120-222337.txt,与原问件逐字一致(唯一差异=
  文件级尾部换行,-p 剥离,sha256=409eef0c…与 R21/R22 判决席同问同值)。
- 运行 22:23→23:12(49 分钟),rc=0。交付=**完整交付**(首页无草稿
  横幅),机器校验 VERIFIED,独立语义审查席裁决 **UPHELD**(抽查 21 格
  锚值/9 转折候选/8 资产月窗/analog 事后块全部一致;4 条轻微披露类
  备注随档,无 MAJOR)。
- MAP_REPORT.sha256 锚一致(7bbc6fc4a188a2d6…);reader_map 九键;
  逐组覆盖表在场;一句总判断/区分指标/analog/条件情景(五行齐备两幕
  并列)/边界六节齐。
- Gate A=FAIL(core_missing=CN_TOTAL_TURNOVER,SH_AMOUNT)=成交额源
  当日全天宕( LIVE 生产晨间快照同状同判,非树工件)——如实披露,
  非地图锚,不阻地图链(attempt-1 已证)。
- 已知外观项: report.json 语义审查封套 seat_invoked=false 为裁决落档
  前快照(权威=audit/semantic_review/VERDICT-*.json,UPHELD 已绑
  map_report_sha256)——披露不改(改动即换 SHA)。

### 4.2 会话 B: 换问验证(计划收到新原文)

- 第二零上下文会话,唯一输入=换问句(美国/欧元区对比+BOJ 政策利率距离
  上次调整时长);落盘 question_verbatim_20261120-231520.txt 与问题件
  **字节一致**(196/196,sha256=7e8821bd 两测同值)。
- run_dir 名与 report.json question 均由新原文生成(20261120T151654Z_
  对比角度换一个_…)=计划收到新原文非缓存旧问。
- 运行 23:15→00:18(63 分钟),rc=0。完整交付(无草稿横幅);
  MAP_REPORT.sha256 锚一致(9810ac81d37efccf…)。
- 独立语义审查席 **REVISE→复裁 UPHELD**(三必改: ①EA「持续回升」改
  「2026-06 回落后回升」对齐 HICP 路径 ②headline 核心/标题分置消除
  basis 矛盾 ③SCN-1 日元腿条件式+反向事实披露;修订数值席位亲算核过
  USDJPY +1.1432% 精确)。裁决档落 audit/semantic_review/20261121/
  (过午夜按实录日期归档)。
- 会话内 update 采 FRED 晚间失败(28 序列)→守卫保全规范面(树内
  canonical mtime 全部≤22:21,零覆盖),报告以 series_store 历史口径
  交付并如实披露「Gate A=FAIL/当前面 missing」——降级透明+数据保全
  的又一事证。
- 会话末询问归档意愿(未自归档,同 A)。

### 4.3 会话 C: 残缺数据(草稿路径)

- 第三零上下文会话,树=隔离副本抽走 ea 当日面(EA_HICP_YOY/
  EA_REAL_GDP_YOY 适配器「序列为空」,CN/JP/US 全部可解析=残缺可控单因);
  原问同 A,落盘 question_verbatim_20261121-002114.txt 逐字一致(490/491,
  尾部换行语义同 A)。
- 运行 00:21→00:41(20 分钟),rc=0。**草稿交付**: 首页横幅
  「⚠ 草稿(非正式): 核心维度组缺数(零 ok 格)——EA×growth、EA×inflation。
  缺数格如实『数据不可得』并随行缺口注记(检索范围披露);补数后重跑转正。
  正式归档对草稿拒绝(map_core_dimension_missing)」(EA×policy 经
  rate_economy 面存活,不误伤)。
- 机器校验 0 violations;独立语义审查席 UPHELD(容忍并记录 EA 缺口,
  裁决档 audit/semantic_review/20261121/VERDICT-20261120T162144Z-01.json)。
- **归档拒绝 belt 实测**(隔离重放 research-one --stage archive):
  ok=false/blocked=not_deliverable/deliverable=false,警告原文点名
  blocked_class=map_core_dimension_missing「正式交付与正式归档仍阻断(补数
  后重跑续链)」+「归档拒绝: 可交付门未放行」;退出码 1(fail-closed)。
  探针存证 session-c-degraded/archive_refusal_probe.json。
- 残留(轻微,披露不修): 会话 C 收尾措辞仍列出 --stage archive 选项
  (括注引擎阻断)——SKILL 步骤4 草稿纪律要求「不得提供立即归档选项」,
  措辞偏差;belt 拒绝已实测兜底,无正式风险。

### 4.4 隔离副本交付包验证

- verify_package.sh v2.1 从交付包直接核对(零上下文,只读树),会话 A/B
  双跑全 PASS: 印章=2953c29/原问逐字(A 尾部换行语义,B 字节一致)/
  git_head=2953c29|source=code_version_stamp/MAP_REPORT sha256 锚一致/
  首页横幅(无=完整)/逐组覆盖表在场/裁决档在链;会话 C 同装置核对
  草稿面(横幅在场,见 4.3)。
- 新版归档与旧档并存: 归档待用户确认(验收令原文「经我认可后可正式
  归档」);重放装置就绪(verify_package.sh+旧档复放通道)。

## 5. 测试与 CI

- 新门 tests/test_audit_r26_gate.py 46 判据(§A-§D 任务1-4+§E 缺数/
  锚覆盖: 助手语义/判定等价/渲染 e2e[EA 缺席+CN 单观测稀疏+US 健康]/
  负对照无横幅/SKILL 纪律 grep/ia_cli 共源 grep)。
- 回归: r7 38/r20 30/r21 50/r22 36/r23 51/r24 74/r25 55 全 PASS。
- 全量电池 199/199 有效(197 直绿+2 技能副本陈旧重装后 32/0+31/0;
  判据 rc∈{0,5}∨rc=3∧SystemExit:0)。
- CI: (PENDING_CI)

## 6. 残留与移交

- 成交额源(CN_TOTAL_TURNOVER/SH_AMOUNT)当日宕机=外部缺项;复现=
  python3 scripts/china_market_collector.py → 「成交额: ❌」(当日四轮
  全失败,LIVE 同状)。
- FRED 晚间 null 尾(AHE 等 14 项 259→257)守卫正确拦截;晨间重采
  应恢复(非本轮阻断)。
- 归档/合并待用户裁定;BUND 两项源端封锁缺席沿 R9 既档。
