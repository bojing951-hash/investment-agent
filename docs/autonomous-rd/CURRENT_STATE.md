# CURRENT_STATE — 最新研发状态

> 研发面恢复入口(新会话先读这里,再读 `RESUME.md`)。
> 引擎运转面(LIVE/轮次/合同)不在本档——见 `~/agent-loop/STATE.md` 顶部速览。
> 更新纪律: 每完成一个重要研发阶段必须更新本档(进度/测试与审计结果/分支与 Commit/下一步)。

## 快照: 2026-11-11 (HKT, R5+R6 已发布 v0.11.0-alpha·LIVE 已同步)

- **发布态**: main=**9051e7f**(merge R5+R6),tag v0.11.0-alpha,Release 441903695,
  CI 43052903525 绿=**基线129**;LIVE=**v0.11.0 面**(三 key 重注入+生产树真实拉取
  终验 cpi=0.9@2026-09-30)。合并纪律已更正(2026-11-11 用户指令): 波次验收绿
  即合并发布不逐次请批,逐次报批仅剩付费类;CN_PPI tushare 积分档=用户裁定
  暂不付费先跑通其他(PPI 如实缺席留后议)。**下一波=AC7 端到端首跑**
  (docs/autonomous-rd/AC7_RUN_PLAN.md,三任务+一开放题)。

## 前一快照: 2026-11-11 (HKT, R6 采集面修复轮·操作者网络轮)

- **R6(采集面修复 D1/D2)已完成**: 分支 `dev/rd-r6-collection-fixes`(自
  dev/rd-r5-stage-coverage 切出,R5 未合并故链式携带)——
  **D1 CPI/PPI 换源**: G-P1-15 金十通道(2025-08 停更后持续写旧值)→
  tushare pro `cn_cpi.nt_yoy`/`cn_ppi.ppi_yoy`;新纯函数
  `_tushare_monthly_last`('YYYYMM'最大有值月→月末观测日,NaN/坏月跳行);
  registry **v2.8.0→v2.8.1**(两 source_symbol 同步+notes 前插)。真实拉取
  冒烟(LIVE token 只读): **cpi_yoy=0.9@2026-09-30 新鲜**;ppi_yoy=服务端
  拒「没有接口(cn_ppi)访问权限」=token 权限档不足(与 cn_cpi 同族不同档;
  金十族复测全死/akshare 1.18.47 无 EM-PPI 包装[源码 grep]/东财 datacenter
  reportName 试探 0 行)→ **卡点②候选报批项**,批前如实缺席。
  **D2 CN_OMO_7D=源端全阻登记**: 四路免费候选实测全灭(tushare 无 OMO 接口/
  央行官网 502/akshare 零逆回购端点+无 telegraph/东财 cookie 门)→
  source-blocked 不造数(台账三之四,后续路径=chinamoney/EM reportName 深挖
  P3 观察)。
- **测试**: wp_e 26 OK(T4 换 tushare 桩+新 t56 纯函数判定;版本锁随升)/
  data_batch1 38/0/charter6_p2 88/0(两处锁随升)/R1 52/R2 47/R5 38/
  snapshot 46 **全绿零回归**。
- **基线**: main = `be8dabd`(v0.10.0-alpha);CI 绿=128 槽。R5+R6 波次
  **待用户批准合并 main**(卡点①逐次请批)。
- **无头自主运行(卡点④)**: 常态运转(每 4h);R6=操作者网络轮(无头禁外发,
  D1/D2 需真网故由操作者会话执行)。

## 前一快照: 2026-11-11 (HKT, R5 阶段证据覆盖面轮·无头自主执行)

- **R5(阶段证据覆盖面)已完成**: 分支 `dev/rd-r5-stage-coverage`——R1 发现
  「阶段B 16 指标快照缺席」全量分解为四类缺陷并收口(`audit/R5_STAGE_COVERAGE_INVENTORY.md`):
  ①假设引用超出观点 subjects 映射面+③mode A 事实面截断过杀=引擎覆盖面缺口**已修**
  (`view_verifier.metric_evidence_table/verify/verify_at_publish` 增
  `extra_metric_ids` 并面;approx_filtered 支截断序列尾值近似,
  `level_source=series_tail_le_publish`+DEGRADED 披露;`build_vp` 汇总假设
  metric_refs 传入 A/B 两型);②CPI_YOY 语义层 id 错配(注册表实有 CPI/CORE_CPI)
  =missing 注记精确化,重指留 Agent 层禁猜;④CN_OMO_7D/BUND_10Y 真缺席=台账
  (`../P2_DATA_GAP_LEDGER.md` 三之四)。**17 份 VP 重建对照**: 既有行零丢失/
  零变动、C 层零变动、新增 64 行(A51/B13)、7 假设 INSUFFICIENT→有判
  (3 SUPPORTED/4 CONTRADICTED,方向全为获得判断)。新套件
  `tests/test_rd_r5_stage_coverage.py` 38 判定绿;R1 52/52、c9_modes 57/57、
  charter8 41/41、vp_sidecar 40/40 无回归;全套回归 129 文件批跑: 其余 128 全 PASS,
R5 套件初跑 3 判定 FAIL=**套件自身判定缺陷**(写死「在档=前R5版」假设,批跑中他套件
真重建 VP 后破裂;引擎零改动),改为逐字节前后不变式后 38/38 绿(全仓口径 130 含根
test_env.py 环境探测)。
  **新发现 P0**: CN_CPI_YOY/CN_PPI_YOY 陈旧值(2025-08 停更源)仍被证据引擎
  采信(R5-D1)+CN_OMO_7D 字段从未采集(R5-D2)——登记 OPEN_ISSUES/台账,
  待有网络环境轮修。
- **基线**: main = `be8dabd`(v0.10.0-alpha);CI 绿=tests/ 128 槽(全仓口径 129
  =+根 test_env.py);本轮后 tests/ 增 1 槽(R5 套件)→ 预期 129/130。
  R5 波次**待用户批准合并 main**(保留卡点①逐次请批)。
- **无头自主运行(卡点④)**: 已由用户放行落地(launchd 拉起本无头轮,提示词
  常驻);本轮=R5 首个无头自主轮。`~/agent-loop/` 在无头会话权限面外
  (rounds/index 追加受限,如实记录)。

## 前一快照: 2026-11-11 (HKT, 用户「全部审批通过」四卡点执行后)

- **基线**: main = `be8dabd`(v0.10.0-alpha,长期自主研发第一波 R1-R4+审计闭环);
  Release 441746111 上线,CI 43030767965 绿 = main 基线 **128 槽**(CI 口径=tests/;
  全仓口径 129 含根 test_env.py 环境探测)。merge --no-ff dev/rd-r2-research-orchestrator,
  分支链 53aa4fe→946625b→ac40ef8→cb98106→fc18590→1721ecc→b9d5cf6→be8dabd。
- **LIVE(本地 Mac launchd)**: **已部署 v0.10.0 面**(2026-11-11 卡点③执行毕)。
  git archive be8dabd 覆盖提取+三 key 重注入 env_config 默认位+.env/data/logs/output/
  archive 全保护;冒烟绿(changes/research-map 10问/research-run 14 步 0 败/
  report_generator+app 导入/launchd 两任务在场)。已知: weekly exit2=既有 Gate A
  数据缺口(ZQ_IMPLIED_AVG 采集缺席,10-31 与 11-07 同因)非部署回归——采集面排查
  已列 RESUME R5 候选③。明晨 07:00 daily=新面首跑。key 备份=~/.ia-live-deploy-backup/。
- **引擎**: 停于唯一日历门——F 补证轮观察钟 2026-12-05 满自动触发,此前无排程任务。
- **长期研发章程**: 2026-11-11 用户《总指令》原文已落位 `PRODUCT_GOAL.md`;
  《长期自主研发系统启动指令》原文已落位 `RUN_MANDATE.md`(自主循环/环境自检/AC11–AC12)。
  FINAL_ACCEPTANCE.md: AC3 = **PARTIAL**(R1+审计收口),AC6 = **PARTIAL**(R2 编排器真执行),
  其余 NOT_VERIFIED。
- **R2(一键研究真执行)已完成**: 分支 `dev/rd-r2-research-orchestrator` @`ac40ef8`+
  R1.1 并入(merge `946625b`)——`scripts/research_orchestrator.py` 十一步确定性管线
  (S1 分解→S11 归档):每步真 `ia_cli` 子进程执行+信封留档,process-ok 与 semantic-ok
  分记,L3 AI 推断/L4 条件情景恒 declared-not-produced(诚实面),逐数证据索引
  (L1 每行挂 snapshot fact_id/L2 挂 VP-id),实体映射零命中=如实 unmapped 不猜,
  归档默认关。入口 `ia_cli.py research-run --question …`。自测 31 判定绿;R1 无回归;
  **全套回归 129/129 exit 0**(全仓口径=tests/128+根 test_env.py 环境探测脚本)。
  **R2 独立审计已收口**(七维对抗: 真执行面/诚实面/证据索引/实体映射/红线/测试真实性/
  Skill 对照——无 BLOCKER,2 MAJOR+4 MINOR+5 NIT;证据索引实测对上快照、红线全过、
  31 判独立;报告 `/tmp/r2_audit_report.md`)。**R2.1 已修**(MAJOR-1 S7 gate 改取
  compare 对齐门 `data.alignment.research_mode_gate`+记 gate_source,修死代码;
  MAJOR-2 L4 五行回归纪律16 权威模板+L3 补 E1/E2/E3 指路+research_map RQ9 统一;
  MINOR-1 analog 诚实拒答豁免 run_ok;MINOR-2 compare 截断披露;MINOR-3 台账语义列)。
  套件 38 判定绿(+7 回归);R1 50/50、research_map 32/32 无回归。剩余 MINOR-4+5 NIT
  转 OPEN_ISSUES。
- **R3(十问扇出入口)已完成**: 同分支 @本提交——`research-run --fanout` 把
  research_map.QUESTION_COMMANDS 十问命令清单确定性执行(16 条命令 ia_cli/scripts
  双通道真子进程+信封留档);Agent 层问(RQ3/RQ9)declared-not-produced;占位符确定性
  替身且如实披露(VIEW-…→观点库首条,A_ID,B_ID→命中指标前二,替身≠相关性选择);
  report.md 增十问扇出台账;run_step 泛化为 _run_proc(支持 scripts/ 直跑)。套件
  47 判定绿(+9);全套回归 129/129 exit 0。AC6 剩余差距收窄=AC7 端到端 3 任务+1
  开放题+真实案例积累。
- **R1(三型证据落库)已完成+审计收口**: 分支 `dev/rd-r1-stage-evidence` @ `26d4ef7`——
  VP sidecar v1.1(阶段A/B 结构化+stage_labels,mode C 契约零变动)、research-map 命令清单
  可执行化(14 条实解析)、页③三阶段证据披露;本地 17 份 VP 重建(A面 12 INSUFFICIENT/
  4 PARTIALLY_SUPPORTED/1 MIXED;B面 12 INSUFFICIENT/5 MIXED)。**全套回归已绿**(2026-11-11
  在 R1 分支干净重跑: 129/129 文件全部 exit 0,零 FAIL;此前章程分支上的作废运行系测试文件
  被分支切换污染)。**独立审计已收口**(2026-11-11,对抗式 6 维: 无前视/标签纪律/方向归因/
  契约真实性/可复算性/B面抽验——六维全 PASS,交付物 17/17 清洁、逐字节重建一致、31 数值
  独立复算全中;结论=无 BLOCKER,2 MAJOR 潜伏缺陷+6 MINOR+3 NIT,报告 `/tmp/r1_audit_report.md`)。
  **R1.1 已修**(MAJOR-1 `interval_change` 入口日期归一 `_norm_ymd`(无横线端锚字符串比较
  使封顶整年失效)→ 根治含阶段B端锚与回落序列;MAJOR-2 `_hypothesis_directions` 废双基
  容忍、定 1-based 单基+provenance 记 `forecast_index_basis`;MINOR-3 词表否定护栏
  ('不再加息'/'no further cuts'/'supply-driven'→None)+英文词边界正则)。回归: 套件增至
  50 判定全绿+受影响 8 文件全 exit 0;**对照实验**(HEAD 代码 vs 修复代码、同一份真数据、
  独立进程、同种子重建 17 份)= 语义零差异 0/17,证明修复不改今日产出。剩余 MINOR 转
  `OPEN_ISSUES.md` 技术待办。章程分支已并入 R1 分支(merge 87afebe,统一历史线)。
- **自主机制**(2026-11-11 配置): 项目级 `.claude/settings.json`(gitignore,仅本地)挂
  PreCompact+SessionStart hooks——PreCompact 提醒完成检查点,SessionStart 提示恢复入口
  (CLAUDE.md→RESUME.md)。stderr 级提醒,无写操作;对在未来于本仓启动的会话生效。

## 里程碑脉络(详录 = `ITERATION_LOG.md`)

38/38 工作包全收口(11-08 四层封版)→ MW-V1 章程校准 → OSS 产品化 v0.1 → Skill 化 v0.2 →
v1.1 整改 v0.3 → Model-Agnostic v2.0(v0.4)→ v2.1 整改+glm 清零(v0.5)→ Charter 6 十年深度(v0.6)→
Charter 7 能力建设(v0.7/v0.7.1)→ Charter 8 机构观点交叉验证(v0.8)→ Charter 9 研究闭环+一键研究(v0.9)。

## 当前差距要点(详表 = `CAPABILITY_MATRIX.md`)

- 机构观点库六标签全库 INSUFFICIENT(库龄函数,首验窗 2026-12)。
- LIVE 面落后 dev 面(v0.7.1 vs v0.9.0)。
- 数据缺口台账 18 项(`../P2_DATA_GAP_LEDGER.md`);HY_OAS 族 = 源端 3 年授权窗如实注记。
- 历史遗留(`../REMAINING_ISSUES.md`,2026-10-17 版): P0 空,余 P1 观察项。

## 用户保留卡点(状态: 2026-11-11「全部审批通过」)

- ① 封版合并 main — **已批准已执行**(本波 R1-R4=be8dabd+v0.10.0-alpha+Release 441746111)。
  后续波次合并 main 仍逐次请批(红线不变)。
- ② 新数据源凭证/付费 — **原则获批**,暂无即需项;HY_OAS ICE BofA 3 年授权窗等
  实际采购仍按需逐次报批。
- ③ LIVE 部署 — **已批准已执行**(v0.10.0 面,见快照)。
- ④ 无头自主运行 — **已批准,落地被权限分类器拦**(启动器提示词文件写入=
  [Create Unsafe Agents] 类别);待用户在场放行后建
  (方案: launchd 每 4h `claude -p` 单轮+STOP 文件+--max-budget-usd 界+允许清单
  禁 push/ssh/curl/npm/pip、合并 main 与付费仍留用户)。
