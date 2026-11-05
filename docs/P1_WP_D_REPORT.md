# IA-P1-WP-D REPORT(登记件)

> 包: IA-P1-WP-D(P1 四经济体底图层实现包第 4 包: 查询面与共享档案衔接)
> 合同: IA-P1-WP-D-AC-v1.1(FROZEN 2026-11-06 04:0x HKT,操作者代批;提示词内嵌传递)
> 分支: `dev/p1-impl-d`(自 BASE-P1D 切出,纯线性,零 merge)
> 本 REPORT 遵守「先登记后实现」纪律: §零 为实现前登记节(实现参数全部先于此落笔);
> §一 起为实现与运行实录。登记节原文实现后禁回改;差异按「如实优先」在实录节披露。
> 数值标注纪律(§5.3): 逐值 [实取·来源] 或 [示意·非实取]。

---

## §零 开工登记(步骤0-6)

### §零.1 契约锚与启动核验实录

| 步骤 | 命令/来源 | 实测结果 | 判定 |
|---|---|---|---|
| 0 时序自检 | `git status` + `date -u` | clean/HEAD=main;UTC 2026-11-05T19:34:08Z [实取·会话 stdout] | 通过 |
| 1 占位符核验 | 附录A头部+冻结章 | FROZEN v1.1;BASE-P1D=c11c998d7c6265a9dbc9ef67bcae5757ec57df9d、CI-SUITES=72、BRANCH-SET=44 分支,三实值齐,与冻结章一致 | 通过 |
| 2 前置实取 | `git ls-remote origin main dev/p1-design` | main=c11c998d7c6265a9dbc9ef67bcae5757ec57df9d(=BASE-P1D 全值一致);dev/p1-design=049ec978523dec659ba47f140bf41669604de24f(全值一致;禁锚 c9626633 未复现) [实取·会话 stdout] | 通过 |
| 3 切建分支 | `git checkout -b dev/p1-impl-d c11c998…` | 新分支创建于 c11c998(自基线 SHA 切出,非盲切) | 通过 |
| 4 设计在场核验 | ①`git merge-base --is-ancestor 049ec978… HEAD`;②设计三件 `git ls-tree` 双侧 | ①exit 0 可达;②HEAD 与 049ec978 侧 blob 逐一等值: P1_DATA_NEEDS_INVENTORY.md=df79c06f66c368d93159b7a3b46852b6fcb9b196、P1_DELIVERY.md=314c2644a51f2f575a90253580cb56346e2f93b6、P1_DESIGN.md=13b263cf3139d420e01bf1e154b03ce85a35db4c [实取·会话 stdout] | 通过,无失配 |

### §零.2 规格抄录(AC-01 锚;逐字抄录自 `docs/P1_DESIGN.md` §六 L172,基线工作树实读)

**定位**: §六「工作包拆解(验收要点=草案…)」表,表头 L167,WP-P1-D 行=**L172**;同族前列行 WP-P1-A=L169/B=L170/C=L171、后继行 WP-P1-E=L173 [实取·docs/P1_DESIGN.md L165-L173 逐行实读]。D 行与前列行可区分(D=查询面且依赖列明文「依赖 P0-3 落地(E2E-A/B 实现)」,A=registry+采集/B=引擎快照/C=评分装配报告)——冻结章三项实读义务①同款判定,实读一致。

**L172 原文逐字抄录**:

```
| WP-P1-D 查询面与共享档案衔接 | 四经济体 NL 查询与档案 ID 衔接 | IR economy 字段、QB-/RT- 引用约定落地、W-1/W-2 场景实现化 | **依赖 P0-3 落地**(E2E-A/B 实现) | ① IR schema 扩展单测(economy 过滤+接地标识强制)【测试】② W-1/W-2 端到端用例: 缺席→「无数据」+差距登记断言【测试】③ 档案记录附 snapshot_id+digest 的校验【测试】 |
```

**四要素逐字分解**(表格单元格切分,字符零增删):

- **目标**(L172 列2): `查询面与共享档案衔接`
- **范围**(L172 列3): `四经济体 NL 查询与档案 ID 衔接`(表列2)/`IR economy 字段、QB-/RT- 引用约定落地、W-1/W-2 场景实现化`(表列3,实现范围)
- **依赖**(L172 列4): `**依赖 P0-3 落地**(E2E-A/B 实现)`
- **验收要点草案**(L172 列5): `① IR schema 扩展单测(economy 过滤+接地标识强制)【测试】② W-1/W-2 端到端用例: 缺席→「无数据」+差距登记断言【测试】③ 档案记录附 snapshot_id+digest 的校验【测试】`

**依赖列生效核验**: 第一层 P0-3 实现面=E2E-A/B+B/G 族链已闭合(R038-R043;冻结章实读义务①);同族前包 A/B/C 独立审计 PASS 落档(R044/R045/R046);e2eb_query_ir/mapper/executor+research_archive 工作树在场实取 [实取·Glob+Read,2026-11-05T19:3xZ]。

**上游在场交付件清单实读**(对照同源锚定,AC-04③):

- WP-P1-A(dev/p1-impl-a@8ec3737daedcb7f3abd77de6ee228fc4250ec6f0): A 类=docs/P1_WP_A_REPORT.md、docs/P1_WP_A_DELIVERY.md、scripts/jp_market_collector.py、scripts/ea_market_collector.py、tests/test_p1_wp_a.py、data/daily/jp_/ea_ 档;M 类=config/metric_registry.json(economy/economy_rule/market_seat 三字段+JP/EA 条目)、run_weekly.py [实读·docs/P1_WP_A_REPORT.md §零.2,在场 Glob 核对]
- WP-P1-B(dev/p1-impl-b@4575a768e8c942a5c8536ee7b5254bf8c88496bd): A 类=docs/P1_WP_B_REPORT.md、docs/P1_WP_B_DELIVERY.md、tests/test_p1_wp_b.py;M 类生效触面=scripts/fact_engine.py(normalize_jp/normalize_ea+build_all)、config/metric_registry.json(NIKKEI225 validation.range);零 diff 判定=snapshot_builder.py/trading_calendar.py/data_validator.py [实读·docs/P1_WP_B_REPORT.md §零.3]
- WP-P1-C(dev/p1-impl-c@ee053a65f3a29e2b154bf841aaf4b1f685a01bd2): A 类=docs/P1_WP_C_REPORT.md、docs/P1_WP_C_DELIVERY.md、tests/test_p1_wp_c.py;M 类=scripts/macro_scorecard.py、scripts/data_assembler.py、scripts/correlation_calculator.py、scripts/report_generator.py(预判零改动) [实读·docs/P1_WP_C_REPORT.md §零.3]

**对齐方式**: 复用调用各在场模块(e2eb_query_ir 常量与校验、mapper 装配、executor 注入面、archive 归档面),零复制分叉。

### §零.3 交付文件清单(登记制白名单;登记后即本合同白名单实体)

**A 类(纯新增,k=3)**: DESIGN L172 范围列=「IR economy 字段、QB-/RT- 引用约定落地、W-1/W-2 场景实现化」=既有文件扩展点(模块级非文件级),按附录A §零(ii) 固定推导规则不派生新增实现模块,必含三件:

| # | 路径 | A/M | DESIGN 依据 |
|---|---|---|---|
| 1 | docs/P1_WP_D_REPORT.md | A | 必含件(附录A §零(ii));本文件 |
| 2 | docs/P1_WP_D_DELIVERY.md | A | 必含件(附录A §零(ii));AC-03.6 漂移维护策略专节载体 |
| 3 | tests/test_p1_wp_d.py | A | 必含件(附录A §零(ii));L172 要点①②③【测试】载体;W-1/W-2 场景实现化=端到端用例落本件(合同 §零(iii-b) 注记) |

**授权 M 类四件(附录A §零(iii-b),超域=违约)**:

| # | 路径 | 授权触面(合同原文) | 本包实取触面(先登记) |
|---|---|---|---|
| M-a | scripts/e2eb_query_ir.py | IR economy 字段(IR_KEYS@L59 域)+schema 校验扩展(validate_ir@L248/_validate_* 族域)+接地标识强制面(BINDING_KEYS/PROVENANCE_KEYS@L60-63 域) | 增 `ECONOMIES` 枚举常量+`validate_ir` 增 economy 可选键校验;IR_KEYS/BINDING_KEYS/PROVENANCE_KEYS 结构零改动(接地标识强制=既有 RESOLVED→provenance 必填机制对四经济体统一适用,以测试证成,登记判定见 §零.6-PD2) |
| M-b | scripts/e2eb_query_mapper.py | map_question@L163 economy 识别与传参面(NL→IR 装配) | 增 `ECONOMY_CUES` 词表+`map_question` 增 economy 识别步骤(条件写 IR["economy"]);CONCEPT_RULES/既有步骤零改动 |
| M-c | scripts/research_archive.py | QB-/RT- 引用约定落地面(validate_id_conventions@L67 域)+档案记录附 snapshot_id+digest 校验面(validate_query_record@L191 域) | `append_query_record` 增 economy echo 条件写+`validate_query_record` 增 economy echo 三条校验(构造面与校验面为同域对偶,登记依据见 §零.6-PD7);QUERY_RECORD_KEYS/validate_id_conventions 结构零改动(QB-/RT- 既有校验面沿用,四经济体语境以用例证成) |
| M-d | scripts/e2eb_query_executor.py(条件类) | economy 过滤与缺席→「无数据」+差距登记面(_refusal@L70/_mark_channel_absent@L134/_resolve_binding@L148 域) | **判定=最小触面**: `CHANNEL_OF_SOURCE` 增两键(jp_market_collector→"jp"/ea_market_collector→"ea"),使 `_mark_channel_absent` 对 jp/ea 指标可按快照 sources_status 做 A2 通道归因(缺席差距登记结构化);_refusal/_resolve_binding/其余行零改动;economy 过滤经 IR 驱动(执行器按 metric_bindings 执行,零 economy 逻辑需要,判定依据=execute_query@L267 实读: 绑定循环无经济体分支) |

**结构约束(iii) 预检**: A 类 3 路径与 `git ls-files` 零重合 [实取·Glob tests/test_p1_wp_d.py 与 docs/P1_WP_D_*.md 均不存在,2026-11-05];必含件齐(DELIVERY/tests/REPORT);A 类清单外一切路径零变更,M 类清单外一切既有文件零变更。

**运行产物边界预登记**: 本包验收要点①②③ 全为【测试】件,无编排入口真实运行面 → 登记「零运行产物」+对照依据(要点标记零【数据档引用】/【CI】外真实运行语义;§三(d) W-1/W-2 场景走查数值经合成 fixture 复现,fixture 唯一数据源=tests 文件内定义,AC-03.3)。

### §零.4 P1 特有纪律登记(WP-P1-D 行所引节实读锚定)

**所引节定位**(L172 行内引用+关联节):
1. §三(c)4 L84 [实取]: 「查询/报告层: 缺席→『无数据』如实输出+差距登记(E2E-B 缺席路径沿用;禁编造禁填0);评分维度可用指标<2→DATA_INSUFFICIENT」——本包承接前半(查询层缺席面),评分面属 WP-C。
2. §三(d) W-1 L88-100 / W-2 L102-113 [实取]: 场景定义(W-1=EA 缺席主导链: ECB_DFR/BUND_10Y/EA_HICP_YOY 缺席→G-P1-01/02/03;W-2=CN 混合链: 在场四条+SHCOMP/MARGIN_BAL/中国CPI/LPR/7天逆回购缺席→G-P1-10/11/15/14/18)。**合同注记节号勘误如实登记**: 合同 §零(iii-b) 注记与冻结章 v1.1 修订注记②写「§四 L88-115」——实读 L88-113 位于 **§三(d) 端到端走查**(L86 起节),§四 自 L120 起;行号锚定正确(W-1@L88-100/W-2@L102-113)、内容无歧义可定位,按节号笔误如实登记,不构成不可定位或规格冲突(AC-04① 偏差≤3 行判据按行号满足)。
3. §四 衔接设计 L139-143 [实取]: ①L140 共享档案 ID 约定沿用 E2E-B 基线(QB-/RT-/origin_query_id/snapshot_id+digest);②L141 P1 新经济体数据进研究档案唯一入口=研究快照,采集档不入档案;③L142 QB-/RT- 凡引用经济体维度必附 snapshot_id+digest(接地到快照,禁引用采集档);④L143 自主模式经济体异常→研究任务记录增 economy 字段(候选,WP-P1-D 落地),任务体其余字段含 falsifiable_conditions 不变。
4. §四 表行 L130/132/133/134 [实取]: L130 research_history_query 禁直读原样覆盖 P1 新通道+economy 可作过滤维度;L132 research_task_manager task schema 沿用零改(合同注记同款);L133 IR 增经济体过滤字段(候选 economy: enum{US,CN,JP,EA,HK,GLOBAL},取值经 registry.economy 推导);L134 接地规则沿用(进入回答的数值必携来源标识,四经济体统一适用)。
5. §六 L175 红线筛查行 [实取]: 全包不含 LIVE 部署/launchd 改动/交易收益承诺/绕开快照+门禁直读;新数据一律经快照进入研究面。
6. §七 L177-183 四红线 [实取]: ①快照+门禁不可绕开(L179 jp_/ea_ 档同禁直读);②LIVE 禁写(L180);③禁交易/仓位/收益承诺(L181);④数据不足不填0 五层一致(L182)。

**遵守登记**: 本包零 LIVE/零 launchd/零网络/零 GLM/零凭证(测试全合成 fixture);缺席面全走既有 ABSENT_*/NO_DATA 机制禁填0;QB- 记录接地=snapshot_id+digest 既有必附面+本包 economy echo;RT- 侧 task schema 零改(rtm.py 不在白名单,L143 落地面=QB- 记录 economy 维度+RT- 引用约定校验证成,登记发现见 §一)。

### §零.5 DP 登记(R020-D5 语义承接)

- **行内零 DP 编号载明**: DESIGN §六 L172 行内及上列所引节(§三(c)(d)/§四衔接设计与表行/§六红线筛查/§七)实读零 DP-编号载明 [实取]。判定依据: P1 设计定稿(R015+R017)早于 R020 DP 分类纪律建制,§六 零 DP 编号载明=预期形态之一(合同 §零 登记型决策点纪律末段同款)→ 按「零 DP 载明」登记分支处理,非 (d)。
- **邻近 DP 核验(实读)**: §二 DP 表(L26-31)载 DP-1..DP-4——DP-1(四经济体构成)=确认型(终确认留用户),本包 economy 取值=族内默认候选 US/CN/JP/EA 延续(R044-R046 已沿用;registry 实测 economy 字段值域={US,CN,JP,EA,HK,GLOBAL} [实取·config/metric_registry.json 实测计数 US49/GLOBAL12/EA11/CN10/JP8/HK4,共 94 条],非自决变更构成,不触发确认面);DP-2(WP-A 面)/DP-3(WP-C 面)/DP-4(WP-E 面)不在 D 行依赖引用面,不登记。
- **确认型 DP 触及**: 零(无凭证/费用/批量状态修改类)。

### §零.6 实现参数预登记(先登记后实现;运行后禁回改;全部 [示意·登记定值] 于落笔时生效)

| # | 参数 | 登记定值 | 依据 |
|---|---|---|---|
| PD-1 | `ECONOMIES` 枚举(scripts/e2eb_query_ir.py) | `("US", "CN", "JP", "EA", "HK", "GLOBAL")` | DESIGN §四 L133 候选 enum;registry 实测值域同集 [实取·§零.5] |
| PD-2 | IR economy 键形态 | **可选顶层键**(键缺席或值 None=不过滤/非经济体维度查询,均合法;键在场且值非 None→须 ECONOMIES 成员);IR_KEYS 不动 | 「可作过滤维度」(L130)语义=可选;向后兼容: 既有 IR/测试(golden 整 dict 断言 tests/test_p03_e2eb_b1.py:342-414)零 economy 键形态必须保持合法;接地标识强制面=既有 PROVENANCE_KEYS/RESOLVED→provenance 必填机制四经济体统一适用,零结构变更 |
| PD-3 | `ECONOMY_CUES` 词表(scripts/e2eb_query_mapper.py) | 有序族表: EA=(欧元区,欧洲央行,欧央行,ECB,HICP,Bund,德国国债,DAX,CAC40,欧元股)/JP=(日本,日银,BOJ,日元,JGB,日经,NIKKEI,东京CPI)/CN=(中国,人民币,中资,A股,沪深,LPR,社融,逆回购,SHCOMP,中国央行)/US=(美国,美联储,联邦基金,美债,美股)/HK=(香港,恒生,港股) | NL 经济体指称识别词表;子串匹配(与既有 OUT_OF_SCOPE_PATTERNS 同机制);GLOBAL 不设词表(全球性查询单过滤维度语义不成立,登记判定) |
| PD-4 | economy 识别与写入规则 | 恰单族命中→写 `ir["economy"]=族值`;零族/多族/概念规则触发(CONCEPT_RULES fired 非空=跨经济体比较链)→不写键 | 跨经济体比较(GOLDEN_Q 美日链)不设单过滤维度(语义自洽);兼容 golden 整 dict 断言(其触发 3 条概念规则→不写键) |
| PD-5 | W-1/W-2 场景 fixture 值域 | W-1 在场侧 DFF=3.88/DFEDTARL=3.75/DFEDTARU=4.00/UST_10Y=4.98/EURUSD=1.12/EZU=65.16;W-2 在场侧 USDCNY=6.64/FXI=33.08/HSI=23294.42/HSAHP=132.49;观测日 W-1 US 侧=2026-10-29(DFF/UST_10Y)/2026-11-01(DFEDTARL/U)、W-2=2026-10-30(FXI/HSI/HSAHP)/2026-11-01(USDCNY) | DESIGN §三(d) L92-99/L106-109 走查值作合成 fixture 输入复现(设计走查值本身为设计时点实取,本包用途=合成数据,非真实数据档读取) |
| PD-6 | `CHANNEL_OF_SOURCE` 扩展(scripts/e2eb_query_executor.py) | 增 `"jp_market_collector": "jp"`、`"ea_market_collector": "ea"` 两键 | _mark_channel_absent 缺席归因结构化(A2 通道归因);值域对齐 rp.SOURCE_FILE_RULES 键 "jp"/"ea" [实取·research_provenance.py L168-176];既有测试合成 registry 无此二 source 值→零回归影响 |
| PD-7 | 档案 economy echo(scripts/research_archive.py) | `append_query_record`: ir 含 economy 键且值非 None→record 增同名键同值(条件写,旧 IR 零变化);`validate_query_record` 增三条: ①record.economy 在场且非 None→须 qir.ECONOMIES 成员;②ir.economy 非 None 而 record 无 economy 键→issue(引用经济体维度必落地,L142);③record.economy 与 ir.economy 均非 None 且不等→issue | 衔接设计 L142(QB- 凡引用经济体维度必附 snapshot_id+digest——既有必附面延续+economy 维度 echo 落地);构造面(append)与校验面(validate)为「档案记录附…校验面」同域对偶,单改校验面则构造面自产出即违规,故同域扩展 |

**桩注入点登记(AC-03.7 判定)**: 本包登记清单(M 四件+A 三件)不含外部服务调用面实现(GLM/LLM 客户端/网络编排/数据源客户端类)——查询面四模块=纯离线(scripts 侧零网络 import 面实读)→ **AC-03.7 不适用**;判定依据=清单无调用面类文件;测试经显式参数注入(registry=/snapshot= 既有依赖注入面,mapper D-B1-11/executor D-B2-01)覆盖,注入点=tests/test_p1_wp_d.py fixture 构造处(§一实录登记行号)。

### §零.7 既有测试兼容性预检(实读锚定)

- tests/test_p03_e2eb_b1.py:342-414 `test_golden_ir_full_literal` 整 dict 相等断言: mapper 产 IR 对概念规则触发问题(GOLDEN_Q)**不得新增必现顶层键**→PD-4 条件写策略依据 [实取]。
- tests/test_p03_e2eb_b2.py: GOLDEN_Q 全量沿用(L292-293 等)→概念规则触发→不写键→兼容 [实取·grep 40+ 命中位]。
- tests/test_p03_e2eb_b4.py: 无 record 键集/整 dict 相等断言(digest 字段断言 L483+文件名列表 L364)→record 条件写兼容 [实取·grep]。
- tests/ 对 `CHANNEL_OF_SOURCE` 零直接引用 [实取·grep];tests/helpers/baseline_locks.py:283 自带 source→channel 映射(测试侧 helper,独立于 executor 常量)→PD-6 零冲突。
- validate_ir/validate_query_record 新增校验均为「键在场时」触发→既有无 economy 键构造零新 issue。

---

## §一 实现与运行实录(实现后回填)

### §一.1 实现实录(逐文件行级;git diff --stat=4 files changed, 53 insertions(+),零删除行)

| 文件 | 实现落点 | 内容 |
|---|---|---|
| scripts/e2eb_query_ir.py(M-a) | L53(常量)/L286-289(校验)/L28-35(docstring) | `ECONOMIES` 枚举+`validate_ir` economy 可选键校验(PD-1/PD-2);IR_KEYS/BINDING_KEYS/PROVENANCE_KEYS 结构零改动 |
| scripts/e2eb_query_mapper.py(M-b) | L58-66(词表)/L331-337(识别与条件写) | `ECONOMY_CUES` 五族词表(PD-3)+恰单族且概念规则零触发才写 `ir["economy"]`(PD-4);CONCEPT_RULES 与既有步骤零改动 |
| scripts/research_archive.py(M-c) | L339-343(append echo 条件写)/L249-259(validate 三条校验) | economy echo 落地(PD-7);QUERY_RECORD_KEYS 必填集与 validate_id_conventions 零改动 |
| scripts/e2eb_query_executor.py(M-d) | L44-50(注释+两键) | `CHANNEL_OF_SOURCE` 增 jp_market_collector→"jp"/ea_market_collector→"ea"(PD-6);_refusal/_mark_channel_absent/_resolve_binding 函数体零改动 |
| tests/test_p1_wp_d.py(A3) | 全文件 30 用例 | 要点①②③载体+负向;fixture 唯一数据源 |

### §一.2 逐要点证据映射表(AC-02;L172 要点①②③)

| 要点 | (a)实现落点 | (b)证据指针 | (c)自检结论 |
|---|---|---|---|
| ① IR schema 扩展单测(economy 过滤+接地标识强制) | economy 过滤: scripts/e2eb_query_ir.py:53,286-289+scripts/e2eb_query_mapper.py:58-66,331-337;接地标识强制(既有面四经济体统一适用): scripts/e2eb_query_ir.py:181-185(RESOLVED→provenance 必填)+PROVENANCE_KEYS@L72-73;测试: tests/test_p1_wp_d.py t01-t15(test_t01…@L227-303) | 证据包④本地 CI 记录(test_p1_wp_d exit=0)+④负向敏感性 D1/D2 红转换+②双源副本 | 过 |
| ② W-1/W-2 端到端用例: 缺席→「无数据」+差距登记断言 | 场景定义=P1_DESIGN §三(d) L88-113(合同注记节号笔误勘误登记于 §零.4);执行面缺席处置: scripts/e2eb_query_executor.py:44-50(A2 归因新键)+既有 _mark_channel_absent@L140-152;测试: t16-t20(test_t16…@L308-390),W-1 形态1(registry 零注册→ABSENT_REGISTRY+G-P1 差距登记)/形态2(通道 MISSING→ABSENT_SOURCE)/W-2 混合链(在场4+SHCOMP ABSENT_DATA+中国宏观3 ABSENT_REGISTRY) | 证据包④(t16-t20 绿)+④负向敏感性 D4 红转换 | 过 |
| ③ 档案记录附 snapshot_id+digest 的校验 | scripts/research_archive.py:339-343(echo 条件写)+L249-259(三条校验)+既有 QUERY_RECORD_KEYS 必附面@L48-52+verify_query_record@L377-392;测试: t21-t29(test_t21…@L393-478) | 证据包④(t21-t29 绿)+④负向敏感性 D3 红转换+②双源副本 | 过 |

**要点参数登记制核验(AC-02.3)**: PD-1..PD-7(§零.6)登记定值=实现值(qir.ECONOMIES@L53 逐字符=PD-1;mapper 词表@L58-66=PD-3;写键条件@L331-337=PD-4;archive 三条@L249-259=PD-7;executor 两键@L49-50=PD-6);运行 echo=测试断言字面量(30 用例);三者一致,运行后零回改。

### §一.3 DP 判据⑥自检(AC-02.6)

- 登记型 DP: 本包零 DP 编号载明(§零.5 登记分支)→实现参数以 PD-1..PD-7 登记,先登记(§零.6 落笔先于实现)后运行,零回改 ✅;
- 确认型 DP: 零触及(无凭证/费用/批量状态修改;economy 取值=族内默认候选延续,非自决变更构成,§零.5)✅;
- DP 编号/分类与实读一致: 行内零载明判定依据已登记(§零.5)✅。

### §一.4 测试与本地 CI 实录

- **新增套件**: tests/test_p1_wp_d.py=30 用例,`python3 tests/test_p1_wp_d.py` exit=0(30 passed,2026-11-05T19:5xZ UTC 实测;[实取·suite-logs/test_p1_wp_d.log])。
- **负向敏感性(4 注入红转换)**: D1 ECONOMIES 去 EA→rc=1(10 failed);D2 mapper 无条件写键→rc=1(1 failed:t13);D3 archive echo 校验删除→rc=1(1 failed:t26);D4 CHANNEL_OF_SOURCE 去 ea 键→rc=1(1 failed:t17);各注入恢复后 rc=0(30 passed)复绿 [实取·/tmp/p1-wp-d-evidence/_negative_sensitivity.py stdout,2026-11-05T19:5xZ]。
- **本地 CI 同构(与 .github/workflows/offline-tests.yml 同款逐套件直跑)**: **73 槽=72 套件 exit=0+1 test_glm_live SKIPPED,零非零退出** [实取·逐套件记录 2026-11-05T19:5xZ,logs=/tmp/p1-wp-d-evidence/suite-logs/];与 BASE-P1D-CI-SUITES=72+新增 tests 文件数 1=预期 73 槽一致(§六.1),无套件数漂移,情形(b)未触发。
- **既有上游套件零回归**: test_p03_e2eb_b1/b2/b4 合跑 172 用例 passed(改动后首轮实测);全套件面见 73 槽记录。

### §一.5 零运行产物声明(AC-06.2⑥)

登记「**零运行产物**」。对照依据: L172 要点①②③标记全为【测试】(无【数据档引用】/编排入口标记);本包登记清单(§零.3)无编排入口脚本;W-1/W-2 场景走查(§三(d))数值以合成 fixture 复现(tests 文件内定义,PD-5),零真实数据档读取、零 `data/research/` 写入、零 `data/daily/` 触碰(测试仅经参数注入 snapshot/registry 字典)。

### §一.6 白名单外发现登记(不实施,AC-07.7)

- **F1(DESIGN §四 L143 RT- 侧 economy 字段)**: 「研究任务记录增 economy 字段(候选,WP-P1-D 落地)」与 L132「task schema 沿用」+合同注记「E2E-A research_task_manager task schema=沿用零改(DESIGN L132 明文)」并存——rtm.py 不在本包 M 白名单。本包保守落地=QB- 记录侧 economy echo(archive 面)+RT- 引用约定校验证成(t29);RT- 记录体增字段的完整落地需操作者处置(后续包授权或合同修订),本包不越界。
- **F2(快照 facts 级 jp/ea 接线延续 WP-B §零.9 发现)**: 真实快照 build_snapshot 尚无 jp/ea facts 接线(WP-B 白名单外发现 F1/F2 延续)→真实链路上 EA/JP 指标执行期缺席为常态(A2/A3 如实);本包以合成 fixture 证成查询面行为,snapshot_builder 零触碰(白名单外)。
- **F3(economy 过滤维度消费面)**: §四 L130「查询覆盖面扩展至新 metric_id,economy 字段可作过滤维度」的消费方=research_history_query(E2E-A 侧);本包交付 IR 携带维度+schema 校验,消费面接线=白名单外,登记待后续处置。

### §一.7 提交前数值标注六项自检清单(§5.3;清单成件入证据包⑨)

1. **计数类数值清单**(本 REPORT): 44 分支(冻结章 BRANCH-SET)/94 条 registry(US49/GLOBAL12/EA11/CN10/JP8/HK4)/12 候选其中 10 条在场/k=3 A 类/M 类 4 件/53 insertions/30 用例/172 用例(B1B2B4)/73 槽(72+1SKIP)/4 注入/6 特有纪律条目/PD-1..PD-7/要点 3 条/映射 3 行/发现 3 条/F1-F3/digest 预计算 3 值。
2. **逐值标注**: [实取·来源] 或 [示意·非实取]——标注态: 44 分支[实取·冻结章机器捕获,注入];94 条与分布[实取·_probe_registry.py stdout 2026-11-05T19:4xZ];12 候选 10 在场[实取·同上];k=3/M4[实取·§零.3 登记与 git status 对照];53 insertions[实取·git diff --stat];30 用例[实取·pytest stdout];172 用例[实取·pytest stdout];73 槽[实取·逐套件记录];4 注入红转换[实取·_negative_sensitivity.py stdout];digest 三值[预计算字面量·_precompute_digest.py stdout 2026-11-06];L169-L173 行号[实读·P1_DESIGN.md];blob 三值[实取·ls-tree stdout];GOLDEN_Q 等 fixture 值[PD-5 登记·DESIGN §三(d) 走查值作合成输入]。
3. **[实取] 项回工作树复核**: registry 计数/diff stat/测试退出码/行号引用——复核方式=本轮命令输出原样留存证据包③④;P1_DESIGN 行号以基线工作树 Read 复核(L165-173 表结构与 L172 逐字一致)。
4. **疑似失实处置**: 零(合同注记「§四 L88-115」节号笔误=§零.4 勘误登记,非失实保留)。
5. **边界出圈登记**: 本 REPORT 头部声明——SHA/日期/分支名按合同冻结章与命令实取登记;注入摘要引用标注「注入摘要,非工作树实读」(§零.5 冻结章数值等);[预计算字面量] 类=digest(fixture 确定性属性,2026-11-06 离线预计算)。
6. **成件**: 本清单随 REPORT 入证据包②(双源副本)。
