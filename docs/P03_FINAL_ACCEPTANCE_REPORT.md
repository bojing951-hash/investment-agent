# IA-P03-FINAL-ACCEPTANCE REPORT — P0-3 真实端到端验收+终裁封版准备(Round 059)

> 包: IA-P03-FINAL-ACCEPTANCE-SEAL(IA-P03-FINAL-ACCEPTANCE-SEAL-AC-v1.0;合同 sha256=
> `f7f58c9afc4ce1042cbcc823e8d836472f4d74642dd976a20e674451910a3cfb`)
> 基点: `ecebb6d44da3f64fbbfc1350670973383534f2e0`(BASE-V13,origin/main;ls-remote=
> rev-parse=本地 main 三一致,开工实测)
> 分支: `dev/p03-final-acceptance`(自 BASE-V13 切出,纯线性零 merge)
> 本节(§零)为**运行前登记**(登记型决策点先登记后运行,运行后禁回改);
> §一-§五 于正式运行后如实回填(第二提交)。

---

## §零 基点核验、白名单与登记

### 0.1 保险核验(合同 §0;三占位符全实值)

| 占位符 | 冻结值 | 开工实测 | 结论 |
|---|---|---|---|
| BASE-V13 | `ecebb6d44da3f64fbbfc1350670973383534f2e0` | `git ls-remote origin main` 同值;本地 `rev-parse main/HEAD` 同值 | ✓ |
| CI 套件基线 | 67(66 exit=0+1 SKIPPED,run 42007354602) | 注入文本为准(引擎侧 run 不可达,U 级);本地 tests/test_*.py=68 文件含 test_glm_live=67 可跑套件,与 67 同构 | ✓(实测面=本地) |
| BRANCH-SET | 40 支全表(合同冻结章) | `git ls-remote origin 'refs/heads/*'` 机器捕获 40 支逐 SHA 对照(脚本比对,非手抄) | ✓ 40/40 在场,**39/40 SHA 全等,1 支=合同文本笔误**,见 0.2 |

开工时刻状态: 工作树 clean,分支自 BASE-V13 新建(冻结派发前未创建)。

### 0.2 BRANCH-SET 对照唯一差异如实登记(非停工项)

`dev/p0-2-w2`: 合同冻结表载 `14fe4e57…`(第5位 4),live ls-remote/本地 rev-parse/
cat-file 三方一致实值=`14fe6e57…`(第5位 6);合同值对象 `14fe4e57…` 在本地仓库
**不存在**(cat-file fatal)。该一位字符差异=R060 整改轮已在案登记的**手抄笔误**
(R060 经验:「硬编码40支分支表手抄曾错1位(14fe4e57→14fe6e57),冻结表必须机器
比对」),分支尖端本身零漂移(实值即历史尖端)。处置=如实登记(情形(b)文本面),
不停工、不改合同;对照口径=「40 支全在场+尖端零移动+唯一新增=本分支」成立。

### 0.3 白名单(合同 §零;登记后即实体)

| 行 | 文件 | 性质 |
|---|---|---|
| A1 | `tests/test_p03_final_acceptance.py` | 验收件(合同 §零 A 集: tests/test_p03_final_acceptance.py) |
| A2 | `scripts/p03_final_acceptance_run.py` | 验收件(合同 §零 A 集: scripts/ 验收驱动) |
| A3 | `docs/P03_FINAL_ACCEPTANCE_REPORT.md` | 本文件 |
| A4 | `docs/P03_FINAL_ACCEPTANCE_DELIVERY.md` | 交付说明(第三提交) |

M 集=**0**(零生产逻辑改动;缺陷→§四登记,另立修复轮);D=**0**。白名单外零触碰
(全部 B1-B5/G 族/基线锁/LIVE/launchd/CI 配置)。

### 0.4 基线实读: B3 交付件在场核验(合同 §2 步骤2;B3 REPORT §零.2 对照)

| B3 行 | 工件 | 本轮在场实测 |
|---|---|---|
| M1 | config/metric_registry.json | version=2.1.0/metrics=85/active=84;JP 四条目全字段在(JP_POLICY_RATE/JGB2Y/JGB5Y/JGB10Y) |
| M2 | scripts/research_provenance.py | `_AUTHORIZED_COLLECTORS`+japan_rate_collector(L143);`SOURCE_FILE_RULES`+japan(L166);`SOURCE_CHANNELS` 四通道不动(L152);`_SOURCE_TO_INPUT` **无 japan**(D7,L111-117) |
| M3 | scripts/registry_semantics.py | KNOWN_SOURCES 含 japan_rate_collector;KNOWN_CALENDARS 含 japan(实跑导入核验) |
| M4 | scripts/trading_calendar.py | MARKETS 含 japan(实跑导入核验) |
| M5 | 四演进域化测试件 | 在场(本 round 全量回归绿,§一.4) |
| A1 | scripts/japan_rate_collector.py | 在场 |
| A2 | data/daily/japan_20261105.json | sha256=`6bba4718759ba12546499c1bdc510a1157b87f9462408e14071967d29e14e7f1`(全值=冻结值,实测一致);data(JGB2Y 1.891/JGB5Y 2.269/JGB10Y 2.855/JP_POLICY_RATE 1.043)与 observations(JGB@2026-11-04/policy@2026-09-01)=D12 锚定值 |
| A3 | tests/test_p03_e2eb_b3.py | 在场(28 用例) |

B3+R060 全弧闭合生效前置复认: merge `ecebb6d` 在 BASE-V13 谱系内(基点即其本体)。

### 0.5 基线实读: E2E-B 链五包交付件清单(在场核验)

| 包 | 代码模块 | 测试 | docs |
|---|---|---|---|
| B1 | scripts/e2eb_query_ir.py + scripts/e2eb_query_mapper.py | tests/test_p03_e2eb_b1.py | P03_E2EB_B1_REPORT/DELIVERY.md |
| B2 | scripts/e2eb_query_executor.py | tests/test_p03_e2eb_b2.py | P03_E2EB_B2_REPORT/DELIVERY.md |
| B3 | scripts/japan_rate_collector.py(+M1-M5 见 0.4) | tests/test_p03_e2eb_b3.py | P03_E2EB_B3_REPORT/DELIVERY.md |
| B4 | scripts/research_archive.py | tests/test_p03_e2eb_b4.py | P03_E2EB_B4_REPORT/DELIVERY.md |
| B5 | scripts/e2eb_answer_renderer.py | tests/test_p03_e2eb_b5.py | P03_E2EB_B5_REPORT/DELIVERY.md |

五包 10 模块/10 测试/10 docs 全在场(0.4/0.5 实测=ls+导入+读)。

### 0.6 基线实读: B5「待 B3」登记项(合同 §2 步骤2;AC-03 核销对象)

| 登记项 | 出处(原文位置) | 内容 |
|---|---|---|
| 要点③(唯一项) | B5 REPORT §零(i)L25/§四 L132/D-B5-16 L167/§七.2 L176;B5 DELIVERY L29/L59 | 「WP-B3完成后同用例升级为双端闭合版(工件: 测试+新数据档)」——B3 停泊期按情形(c)登记「升级版待 B3 落定,由后续轮承接」;B5 DELIVERY L59 明示该升级「属后续轮**新登记面**,不回写本包模块与测试」→ 本轮=A 行新登记(tests/test_p03_final_acceptance.py T2 组),零触碰 B5 件 |

### 0.7 基线实读: P0-3 最小范围对照来源(U 级如实登记)

合同附录交叉引用「handover P0-3 定义与最小范围」——handover 属引擎侧
(~/agent-loop),执行 Agent 会话**结构性不可达**(可达性事实,提示词 §0),且其
清单文本未注入本提示词。处置: 对照面=合同 §1 明文范围四项(E2E-B 真实任务验收/
E2E-A 抽样复验/B5 要点③回补+最小范围对照/终裁封版=操作者面)+DEV 侧可见 P0-3
子线交付物(P03_W1 E2E-A/P03_W2_GLM G1-G4/P03_E2EB DESIGN+B1-B5)。引擎侧
handover 原文清单=U 级(不可核验),§三映射表按上述可达面逐项映射,零虚构清单项;
若审计/操作者注入 handover 原文,差异项按情形(b)补登记。

### 0.8 冲突自检(合同 §2 步骤3;情形(d)排查)

- B3 交付缺席? 否(0.4 全在场)。
- 链路结构性不可验? 否——五包链全模块可跑(§0.9 探针实测全环贯通)。
- 已知结构性限制(非(d)): B3 D7 事实提取未接线(sb 归一化链四通道,japan 档经
  sources_status 在场核验而事实缺席)+映射/执行器三处 japan 邻域缺口(§四 FD-1/2/3
  登记)——合同冻结章预期注记明文路由「如实不触发/链路断=情形(c)/(b)如实,禁调参凑」,
  本轮 M=0 禁修复,登记不代修。
- **结论: 无 (d) 级停工项,开工。**

### 0.9 探针登记(参数冻结前只读探查;R011 window_probe 先例)

2026-11-05 探针(零写入,write=False/tempdir,输出全文入证据包 01-probe/):

- **B1 映射(真实注册表 85)**: 11 绑定;MB-8 日本政策利率→`JP_POLICY_RATE`
  (注册表命中,calc 含"BOJ"检索命中;**B3 前=ABSENT_REGISTRY**);MB-9「JGB 10Y」
  →`JGB2Y`(search_terms「日本国债」**首命中** JGB2Y.calc——标签语义 10Y 未被
  检索尊重,FD-2 登记);3 ops 全 PENDING;unresolved=[]。
- **S1 快照(20261105,真实 data/daily)**: gate_a=DEGRADED;global/macro/china/
  rate_economy=FALLBACK lag1(20261104 档);**japan=EXACT sha256=6bba4718…(=A2
  冻结值,在场核验达成)**;n_facts=77,**JP 事实=0**(D7)。
- **B2 执行器**: 美端 9 绑定全 RESOLVED(DFEDTARL 3.75@11-03/DFEDTARU 4.0@11-03/
  DFF 3.88@11-02/UST_2Y 4.59@11-02/UST_10Y 4.91@11-02/CURVE_2S10S 0.34@11-03/
  USDJPY 158.35@11-04+week +0.3466%+ytd +1.239%);MB-8/MB-9=ABSENT_DATA
  「本期无该指标事实(派生输入缺席,归因性缺席)」;OP-1/OP-2 NO_DATA;OP-3 COMPUTED
  =0.32(4.91−4.59)。
- **B5 渲染**: grounded,9 接地/2 缺席/2 不可计算,footer 免责+缺席摘要齐。
- **B4 档案(tempdir)**: append written→load ok→digest a84750438a3b2f3f→verify True。

### 0.10 登记型决策点(先登记后实现/运行;运行后禁回改)

| # | 决策点 | 登记内容 |
|---|---|---|
| D-FA-01 | 验收任务样例 | 合同冻结章指定=DESIGN §三(d) 第一环 L134 逐字「美日政策利率差和10年期国债收益率差最近怎么样?和美元兑日元走势合起来看是什么状态?」;零改写(驱动与测试共用同一常量) |
| D-FA-02 | 正式运行确定性参数 | CREATED_AT=`2026-11-05T20:45:00+08:00`/AS_OF=`2026-11-05`/TARGET_YMD=`20261105`/ARCHIVED_AT=`2026-11-05T12:46:00+00:00`;全显式注入禁墙钟;探针(0.9)先行,此后参数零回改 |
| D-FA-03 | 快照持久化形态 | 正式运行 S1 `build_snapshot(write=True)` 输出到**证据沙箱**(evidence 目录 e2eb-sandbox/),data/daily 真实档只读;理由=①B4 verify 需快照文件在盘(R5 digest 复算)②持久档案溯源链要求快照可逐件核验;生产 data/daily 零写入 |
| D-FA-04 | 档案落点 | B4 append 落 DEV `data/research/research_archive/query_history/`(B4 缺省同源根;gitignored 不 commit;LIVE 零触碰);query_id 经 `allocate_query_id` 同日单调配号 |
| D-FA-05 | 测试 CI 可移植面 | 验收测试仅依赖 git 内在场件(真实注册表85+data/daily/japan_20261105.json[B3 A2 显式纳入]);全量真实档(17 文件)链路=正式驱动件一次运行留痕,测试**不以合成冒充真实**(T1=CI可达真实锚/T2=显式标注合成的能力闭合) |
| D-FA-06 | MB-9 现状锚策略 | FD-2(首命中误映射)按合同 M=0 登记不代修;测试 t12 断言**现状**(MB-9==JGB2Y)并注记——修复轮翻转断言须 conscious(红即信号) |
| D-FA-07 | E2E-A 复跑参数 | =R011 Run1/Run2 原样: `--run-e2e --start 2026-06-30 --end 2026-09-30 --source-date 20261104`(缺省 data-dir/out-dir/as-of);恰 1 次;对照=R011 §5.1/§5.2 登记行为 |
| D-FA-08 | 负向敏感性注入对象 | INJ-1=B1 `_search_registry` 恒 None(定向红 t12/T2 组);INJ-2=B2 `_execute_spread` 结果+1.0(定向红 t22/T2 组);注入→红→还原→sha256 逐字节一致(B5 D1-D4 同款纪律) |
| D-FA-09 | 日端双端闭合形态判定 | 真实数据版=FD-1 结构性阻断(事实未接线)→情形(c)如实(日端数值不触发);能力版=T2 合成闭合(B5 要点③「测试」工件)——两版**分立呈现禁混同**,REPORT §三逐行映射 |

(登记时刻 UTC 2026-11-05T1x:xxZ;此后任何参数变更=违约,除非按 §四如实登记)

---

*(§一-§五: E2E-B 正式验收/E2E-A 抽样复验/B5③回补+P0-3 对照/发现登记/AC 自检——
正式运行与全量回归后第二提交回填。)*
