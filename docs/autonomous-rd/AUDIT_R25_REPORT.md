# Audit-R25 交付报告(R69)

基线 524f997(R24 尖,CI 44673137052 绿)→ 本轮代码修复(dev/audit-fix-r1,
PR #1)。四项验收对应本报告四节;新门 tests/test_audit_r25_gate.py 54 判据;
回归 r18-r24 七门全绿;全量 pytest 与 CI 见第 5 节。

## 0. 环境与既成状态

- 外审令四任务: 日常采集保全 / 历史时点实录 / 原问逐字+正文校验 / 归档重放。
- 基线=524f997(本地 dev/audit-fix-r1,已推 PR #1);工作树含本轮未提交修复。
- 四项官方发布日期逐项 Web 核验(Eurostat 2-01042025-AP/2-16042025-AP、
  BLS 改期通告、BEA 25-46[pi0925.pdf 载 2025-12 目录]、Fed G.17 合并公告),
  首个搜索命中「Sept PCE=Nov 25」系 2026 年日程混淆,已弃用。

## 1. 日常采集保全(任务1) — 15 判据(§A)

- **同日降级重采集守卫** `research_provenance.daily_face_guard_write`:
  覆盖指纹=(序列路径集[list→'[]' 通配], 叶子计数),**只比结构不比值**
  (值修订≠降级)。降级⟺严格路径子集 或 同构路径∧叶子缩水 →
  `degraded_diverted` 转存 `data/daily/superseded/{prefix}{date}_{时戳}[_N].json`,
  **规范文件不被覆盖**;非降级覆写前旧档亦入 superseded(可重放版本永不丢);
  `IA_DAILY_ALLOW_OVERWRITE=1` 豁免直写(旧档仍保留)。
- 八采集写点全部接线(china/ea/macro/global/japan_rate/jp/shiller/
  rate_economy),降级时打印⚠注记。
- superseded/ 对 resolve_inputs/data_retention 不可见(top-level only)、
  永不冒充规范来源(canonical_source_file 拒绝路径分量)。
- **按发布频率识别过期**: freshness_policy.assess_observation_freshness 仅施
  于 months_before==0 的最新一期锚(历史锚时点差≠采集缺陷);未注册指标不判。
  EA HICP 停 2025-12 时 2026-11 最新一期标 stale(末观测 2025-12-01,
  滞后 354 天>60 天月频窗),读者面渲染
  `⚠过期:末观测2025-12-01(滞后354天>60天窗口)`。
- **必要维度缺失→带缺口草稿交付**: draft_delivered=machine_verified∧
  review_ok∧copies_consistent∧blocked_class∈{map_core_dimension_missing,
  map_anchor_coverage_insufficient} → exit 0,读者得 MAP_REPORT.md 草稿;
  正式归档 belt 同判拒(草稿≠正稿,补数后重跑续链)。
- 残缺数据测试与当前日常采集实测见第 4 节。

## 2. 历史时点实录(任务2) — 15 判据(§B)

- **月首口径统一**: _visible_publish 将月/季频观测归一到月首查日历,
  与 _aof_first_pub 同约定;日频不归一。统一前 5/12 组只覆盖即此缺口。
- **release_calendar v1.4.0**(14 条目/6 批次,spec 含修订记事):
  - RC-EA-HICP-2025M03: 速报 2025-04-01/终值 2025-04-16 两级分记;
  - RC-2025SHUTDOWN-CPI-NOV(CPI+CORE_CPI 同批 BLS-CPI-2025M11-REL,
    2025-12-18——BLS 改期实录,原定 12-10);
  - RC-2025SHUTDOWN-PCE-SEP(CORE_PCE,BEA 25-46,2025-12-05;
    优先于 REST 保守界 2026-01-22);
  - RC-2025SHUTDOWN-INDPRO-OCTNOV(2025-10+11 两观测月合并补发,
    FRB-G17-2025M10-11-REL backfill=2,2025-12-23)。
- **逐项前一天/当天复测 6 组翻转**(§B2): EA_HICP 2025-03(03-31 不可见/
  04-01 可见)、CPI/CORE_CPI 2025-11(12-17/12-18)、CORE_PCE 2025-09
  (12-04/12-05)、INDPRO 2025-10 与 2025-11(均 12-22/12-23)。
- 无法确认当时值→不虚构: 无实录条目走规则推定且 basis 如实标「推定」;
  值缺口用上期已知值或标缺口(既有 asof_discipline/事后段机制,
  r23 门§C 已覆盖)。
- **日本双轨**: JP_POLICY_RATE=月均留在市场观测(decision=None),
  JP_POLICY_TARGET=宣布值另列;美欧中决策面带官方决议/生效惯例
  (prev_day/prev_thursday/obs_day)。
- 权威日期修订随判据更新: r23 门§C CPI 12-13→12-18、INDPRO 断言改
  _aof_first_pub 直测(aftermath 行为随实录日期变化——38/36 天≤45 天
  容差,异常行不再出现,以日历可见性为准);r24 门§2 同。重放回归
  (字节级)不受影响。

## 3. 原问逐字+正文校验(任务3) — 15 判据(§C)

- **plan.question_verbatim** 逐字入计划(字节级==原问);内部摘要另存
  question_summary(自声明「交付与验收以 question_verbatim 为准」)。
  工单(AGENT_SEAT_ENVELOPE.question)/报告(run.question)/归档
  (ARCHIVE_MANIFEST.question)既有携带面+计划面=四处置齐。
  R24 档如实保留(记录=98 字改写版,原文 169 字另存 session/
  run_question_verbatim.txt——新档起逐字面收口该缺口,§D1)。
- **check15 三写法**: 单位族扩 bp|个百分点|个基点|基点(基点族×1
  无换算,个百分点仍精确 pp↔bp 对);归属别名面 _ATTR24 扩容
  (UST_10Y/TIPS_10Y/BEI_10Y 代码名+十年期美债/十年期TIPS/通胀保值/
  盈亏平衡通胀中文名,就近 rfind 取胜);触发词扩 ticker 名。
  **对调拒绝×四写法**: 年度窗真值 名义+97/实际+104/盈亏平衡−7,
  互换(名义+104/实际+97)四写法均 CONTRADICTED;正确表述四写法均放行。
- **无显式符号时方向词定号**: 「下行7个基点」=−7(方向词承载符号语义;
  显式符号仍以符号为准,与方向词矛盾由 bp_direction 拦)。
- **check(18) 跨面一致性**(cross_face_consistency=r25 门控,旧档复放
  不追溯): 首页/转折表/传导链之间日期次序主张(早于/晚于)逐对核
  (月前缀比较,同月混精度=不可判跳过);同一无序对相反主张=
  CONTRADICTED;传导链每链≥1 区分指标须引擎可观测(计划∪上下文∪
  快照);转折表指标须同源。

## 4. 归档重放(任务4) — 9 判据(§D)

- **R24 归档包结构修复(本轮实测发现的真缺陷)**: 仓内 r24-evidence/
  acceptance 原以平铺提交,manifest 相对路径 verdicts/… 不解析;
  现日期前缀裁决件 git mv 入 verdicts/(与 r22/r23 布局一致),平铺
  逐字节重复件删除。
- 干净目录重放: 裁决链按 ARCHIVE_MANIFEST 相对路径解析+sha256 逐件
  吻合;链闭合(唯一名+predecessor⊂源集);受审字节三处绑定
  (manifest.map_content_sha256==内容段复算==裁决绑定 abbc4742…;
  全文 sha==旁挂 MAP_REPORT.sha256)。
- **正式入口重放确定性**: 引擎树(config+裁决链+由 report.json 冻结的
  快照)+rd 复本 → ia_cli archive → 内容摘要/地图绑定/问句/裁决链
  逐位==原档(rc=0)。
- append-only: 归档目录已存在→拒(archive_exists);独立新路径→放行,
  旧版原样保留(两版并存)。
- R22/R23/R24 重放回归件全部在场且绿(r22 36/36, r23 51/0, r24 74/0)。

## 5. 测试与 CI

- 新门: tests/test_audit_r25_gate.py 54 判据(§A 15+§B 15+§C 15+§D 9)。
- 回归: r18 40/0, r19 35/0, r20 30/0, r21 50/0, r22 36/36, r23 51/0,
  r24 74/0。
- 全量 pytest 与 CI 结果见交付时汇报(第 6 节在推送后回填)。

## 6. 交付面(推送后回填)

- 代码 SHA / PR SHA / CI 链接。
- 当前日常采集一次+残缺数据测试一次(隔离树,LIVE 零写入)记录。
- 原问会话(全新无头会话,只发一次原问)记录: 工单号/数据覆盖/
  可读地图/独立审查/归档摘要。
- 合并由用户决定(未合并)。
