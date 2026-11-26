# Audit-R18 真实运行与闭环证据包(任务⑤)

目的: 地图问句原问逐字真实运行的**最终受审交付件**入仓(此前引擎树在
$TMPDIR);代码固定提交 d3dea052585d2e433d92576afe5f70b144722ddd
之上执行;零合成(合成隔离测试另在 tests/test_audit_r18_gate.py,
SYN_ROLE=R18-SYNTHETIC-ISOLATED-TEST)。不含任何密钥/令牌。

## 一、清单与哈希(前 16 位对勘,完整值以 shasum -a 256 现场重算为准)

| 件 | sha256(前16) | 证明 |
| --- | --- | --- |
| `MAP_REPORT.md` | `2d6260e6cb0599c9` | 读者报告(可直读可核查交付件);与归档包/运行目录三方逐字节一致 |
| `MAP_REPORT.sha256` | — | 旁挂防篡改锚(磁盘≠锚=单改拒付不重写;本次=合法修订链最终态) |
| `agent_judgment.json` | `f84dfbac4dd0de30` | Agent 席真实判决(l3 CON-1+MECH-1 三环/l4 SCN-A/B/reader_map 五面);attach 后机器契约 VERIFIED(unbound=0, map_fail=0) |
| `report.archive.json` | `35c7f389401b432c` | 归档版 report.json(含 research_plan 共享研究计划+contract_verification VERIFIED+裁决链面) |
| `verdicts/VERDICT-…-01.json` | — | 首审裁决 REVISE(四必修: 政策事件日期系统性错误/BEI 年变化符号/CN 荣枯线表述/历史段无源锚) |
| `verdicts/VERDICT-…-02.json` | — | 修订后同判词重录(append-only 链不覆盖,-01 因摘要翻新自动过期) |
| `verdicts/VERDICT-…-03.json` | — | 闭环复验 **UPHELD**: 四必修逐日对值关闭+回归电池 20 项全绿+残留 3 NIT(措辞层,不阻断,记下轮候选) |

## 二、运行口径

- 问题=产品验收原问逐字(不手填指标代码);截止日 2026-11-18;
  快照 research_snapshot_20261118(事实 104,core 缺 0,Gate A DEGRADED
  =4 项非核心缺席如实)。
- 引擎树=$TMPDIR/r18_real_work/engine_merged(仓码 d3dea05+LIVE 数据
  面副本,LIVE 本体零接触);CN_PMI_MFG 226 月序列逐字节派生自仓内冻结
  包 cn-task-b(R6-02 正式入口 provenance 随附+源 sha 登记)。
- 一行复用: `python3 ia_cli.py research-one --stage auto --question "<原问>"
  --engine-root <引擎根>`(plan→attach→report;Agent 席按
  AGENT_SEAT_ENVELOPE.json 产判决后接续;正式归档 --archive-dir)。

## 三、闭环链(修订循环全档在包,失败证据不洗白)

首审 REVISE(四必修) → 修订(事件日期 2025-12-11 降/2026-09-17 升全量
改正+BEI 负年变化+CN 荣枯线实况+历史段实锚 50.3/8/12 月<50/47.0) →
attach 机器契约复验 VERIFIED → 独立席闭环复验(零信任,series_store
原始值直读重算)→ **UPHELD** → report 段 deliverable=True → 归档
content_sha256=90146e06…(报告=裁决=归档三处同锚)→ SHA-256 回读三方
MATCH。

## 四、复核席独立重算摘录(闭环轮)

- DFF 台阶逐日: 2025-09-17=4.33→09-18=4.08、2025-10-29=4.12→10-30=3.87、
  2025-12-10=3.89→12-11=3.64、2026-09-16=3.63→09-17=3.88(各 25bp);
  窗口内往返各 25bp、净变动 0(3.88@2025-11-18→3.88@2026-11-16)。
- BEI 年变化: 同日口径 −7bp(2.21@11-17−2.28@2025-11-17)、月末口径
  −3bp(2.20−2.23)、冲高期 2 月→5 月 +13bp(2.25→2.38)。
- CN PMI: Jul 49.2/Aug 49.8/Sep 50.1/Oct 49.3;均值 49.77、10 个月中
  5 个月<50;历史段 2021-12=50.3、2022 年 8/12 个月<50、年末 47.0。
- CPI 2026-10 同比 4.0806(337.476/324.245−1,基月 2025-09 缺席回填)、
  CORE_CPI 2.8697;三利率恒等式 5.12=2.92+2.20 残差 0.000(11-16 公共日)。
- 残留 3 NIT(下轮候选,不阻断): Q3/Q4 边界措辞(75bp 跨 Q3+Q4)/
  「年中」作背离期标签偏松/l3 step1 ref 配对装饰性残留。

## 五、复放

判决档+快照+仓码 d3dea05 三者齐备时: `ia_cli.py research-attach
--report-dir <运行目录> --judgment agent_judgment.json` 应返
attached=True/VERIFIED;`research-one --stage report` 应返 deliverable=True
(裁决链在场且 fresh)。复核脚本另存 /tmp/r18_audit/(会话期)。
