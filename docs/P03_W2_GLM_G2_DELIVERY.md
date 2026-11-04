# IA-P03-W2-GLM-WP-G2 交付说明(DELIVERY)

> 工作包: IA-P03-W2-GLM-WP-G2(WP-G2 结构化输出契约与校验器)· 分支 `dev/p03-w2-glm-g2`
> 基线: f5dc79fc5b86f70e98b10753acfd9b45845e52ea(WP-G1 最终交付尖端,R026 审计 PASS;纯线性切出,无并入步)
> 证据包: `/tmp/p03-w2-glm-g2-evidence/IA-P03-W2-GLM-WP-G2-EVIDENCE.zip`(zip sha256 见 §二)
> 边界: 零真实 GLM/LLM 调用、零凭证、零付费、零网络出站(真实调用属 WP-G4,PENDING);零运行产物(依据见 REPORT §0.3)。

---

## §一 改动(交付清单,k=4,与 REPORT §0.2 登记一致)

| 文件 | 形态 | 摘要 |
|---|---|---|
| `scripts/glm_output_validator.py` | 新增(校验器模块) | 结构化输出契约与校验器: HypothesisSet 模式A七字段/模式B裁剪三字段闭合 schema;证据引用在场核验(fact_id∈输入证据包+身份一致);数值接地分层(statement/notes/limitations/explanation→证据包;cond_text/spec.target→三合法来源[证据包+注册表点名两族+先验触发器注入],零容差,改写即拒);竞争性区分性判据(两两四元组不全同);反方证据强制(空即拒,§四(3)机制一);缺席承接(absent_ack 逐项复述+limitations 四义务);假设-证据映射表构建(§四(2),quality_status 透传+内容级绑定);失败三径状态机(径1重试+反馈回注+线性退避计划表→径2降级受纳[义务强制]→径3缺席登记[熔断即时/未知类 fail-closed/状态不推进]);桩注入点=run_conclusion_pipeline attempts 参数;入口复用 gia.validate_input fail-closed |
| `tests/test_p03_w2_glm_g2.py` | 新增(专项测试) | 76 用例: T0 fixture 自检 2+T1 schema 正向 6+T1b 解析容忍 7+T2 负向敏感性 34+T3 阈值三来源 6+T4 失败三径 13+T5 数值抽取 3+T6 echo/复用 4+T7 源码边界锁 1;全合成 fixture 唯一数据源(注册表/触发器注入合成集);预期值字面量硬编码 |
| `docs/P03_W2_GLM_G2_REPORT.md` | 新增(执行报告) | §零 规格抄录(DESIGN L222-226 逐字)+白名单登记+零运行登记;§一 前置实读(file:line);§二 参数登记(先登记后运行);§三 逐要点映射;§四 git 取证;§五 数值标注自检 |
| `docs/P03_W2_GLM_G2_DELIVERY.md` | 新增(本件) | 五节+漂移维护策略专节+fixture→预期值映射 |

改动总量=纯新增 4 文件,零修改既有文件(diff --name-status 基线..尖端=恰 4 行 A,零 M/D,零第二类)。

## §二 证据

- **本地逐套件**: 59 份套件记录 `/tmp/p03-w2-glm-g2-evidence/local-ci/`(58 跑+1 合同排除)=57 绿+1 既有红(test_p4_fixes: 39 通过/4 失败 monthly_review 数据块,基线既有归因,与本包零导入关系——本包不 import monthly_review);新增套件恰 1(test_p03_w2_glm_g2,76 用例 OK)→ CI 预期 57+1=58 零回归。
- **负向敏感性**: 4 注入全红后回绿(日志 `negative-sensitivity/`): D1 反方证据强制移除→红4/D2 阈值合法性禁用→红1/D3 区分性禁用→红1/D4 absent_ack 承接吞掉→红1;RESTORE-GREEN exit=0(76 OK);零注入标记残留(grep D[0-9]-INJECTED=0)。
- **零触碰**: `data/` 全量 27 文件(24 daily+3 research)sha256 快照 `datapath-zero-touch-snapshot.txt`;本包无真实运行面→零运行产物(REPORT §0.3 依据);`data/daily/` 源码零引用(T7 源码锁)。
- **git 取证**: 原样输出于证据包成员③(name-status/rev-parse/log/reflog/ls-remote+设计在场核验输出[merge-base 可达+六件 blob 等值])。
- **CI**: 操作者 CHECKPOINT dispatch(执行Agent 禁自行触发);登记件将落 `rounds/027/GLM-WP-G2-CI-dispatch-evidence.md`(引擎侧,本包引用其路径)。
- **zip 整体 sha256**: 见证据包成员⑧ SHA256SUMS 与 stdout 自述(本文件不预写,以装配后实测为准;若装配后追加登记,自指豁免同 SHA256SUMS——zip 内本副本不含追加行)。

## §三 逐 AC 自评

| AC | 自评 | 指引 |
|---|---|---|
| AC-01 规格抄录与登记 | PASS(自评) | REPORT §0.1 逐字抄录+行号(DESIGN L222-226 实读);清单 k=4 逐条附依据;结构约束核验(§0.2,git ls-files 265 文件零重合);无命名偏差(DESIGN L226 工件名=泛称「测试文件」) |
| AC-02 逐要点映射 | PASS(本地)(自评) | REPORT §三 五要点(②拆四子行)全映射;参数登记=常量=echo(T6);要点⑤ CI 侧待操作者 dispatch(NOT VERIFIED 部分,如实) |
| AC-03 测试与确定性 | PASS(自评) | 76 用例全绿;零网络/零新依赖/全合成 fixture/字面量硬编码;漂移维护策略专节(§五)+fixture→预期值映射(§六);GLM 调用面合成桩=适用(校验器含调用面确定性形态 run_conclusion_pipeline: attempts 注入桩,零真实出站;桩注入点登记 REPORT §二.3+模块 docstring `scripts/glm_output_validator.py:588`) |
| AC-04 引用真实性 | PASS(自评) | REPORT/DELIVERY file:line 逐条可寻(±3);设计六件=基线工作树实读(blob 等值已核);G1 交付件引用以其 REPORT §零登记清单为对照同源;注入快照引用显式标注(REPORT §五 第6项) |
| AC-05 范围/分支/隔离 | PASS(自评) | diff=恰 4 行 A 零 M/D 零第二类;纯线性零 merge;既有 29 支尖端不变+唯一新增 dev/p03-w2-glm-g2(ls-remote 实取);E2E-A 六文件/G1 四文件/设计六件/主流水线/registry/workflow 零改动(gov.gia is gia 复用身份断言);LIVE 零写入/launchd 零触碰/档案不 commit/.gitignore 不改 |
| AC-06 CI 与证据包 | 部分 NOT VERIFIED(如实) | 证据包八类最低集已装配+SHA256SUMS(清单自身显式豁免);CI dispatch=操作者动作,本轮未发生→conclusion 待 CHECKPOINT;五节齐备+result.md 四段=自述 |
| AC-07 研究纪律 | PASS(自评) | 禁直读(data/daily 源码零引用,输入经 G1 装配=快照标准化路径);缺值不填0(缺席承接强制,空 ack 即拒);无投资建议文案(校验器零建议类输出);零真实调用/凭证/付费(T7 源码锁: 零网络/零凭证模式);W4/W5 零涉及;白名单外需求零实施(发现登记: 见 §四) |

## §四 如实偏差与登记发现

1. **test_p4_fixes 本地红 4 项**(既有,非本包): 基线归因沿袭(monthly_review 数据块,本地真实数据演化;G1 REPORT 同款登记);本包与其零导入关系。
2. **AC-06 CI 侧 NOT VERIFIED**: dispatch 权在操作者(合同 §六.5),执行Agent 禁自行触发;补 CI 证据=CHECKPOINT 动作,非本包整改项。
3. **白名单外需求发现登记(不实施)**: ①先验触发器阈值(来源 iii)的结构化注入需 G3/G4 编排层从 config/thesis.json quant_triggers、allocation_views.json triggers 提取后传入 `prior_trigger_targets`(本包已留注入面,白名单外不代建);②注册表阈值缺省经 `rp.active_registry_metrics()` 实取,若调用方要求零 config 依赖可显式注入 `registry_targets`(接口已在);③假设-证据映射表的 neutral 方向枚举未发(输出无中性向证据字段,G3 承接时如需可扩展);④模式 B promoted_to_task_id 升级路径(§六 L200)属 E2E-B/G3 链,本包仅校验裁剪版。
4. **UTC 时刻**: 开工 2026-11-04T17:17:35Z;本文件落笔 2026-11-04T18:0xZ(实取以取证输出为准)。

## §五 漂移维护策略(AC-03.6 专节,三要素)

1. **测试预期值唯一来源=仓库内版本化合成 fixture**: `tests/test_p03_w2_glm_g2.py` 内 `build_input_mode_a`/`build_input_mode_b`/`build_valid_output_mode_a`/`build_valid_output_mode_b`/`TIPS_FACT`/`GOLD_FACT`/`REG_SYN`/`PRIOR_TRIGGERS`(全部内联合成,数值锚点 2.93/4186.7 等);断言期望值均硬编码字面量(EVIDENCE_MAP_LITERAL/ECHO_LITERAL/问题消息子串/枚举元组),不从被测模块导入计算(自证恒真是 F 反例);注册表/触发器经 monkeypatch 注入合成集,真实 `config/metric_registry.json`、`config/thesis.json` 永不入测试。
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: 若合成 fixture 结构/锚点变更,受影响断言(EVIDENCE_MAP_LITERAL 行序、ECHO_LITERAL、合法集字面量)与 fixture 定义在同一提交内同步修改;本包交付后任何此类变更走登记型修订(新工作包/合同修订),禁散点改。
3. **真实数据档永不进入测试预期值来源**: 测试零读取 `data/daily/`/`data/research/`(源码级: 测试仅内联合造对象+subprocess 零;T7 源码锁同时断言被测模块 `data/daily` 零字样);fixture 自检(T0)只断言合成输入经 G1 既有契约校验回读合法,不锚定真实交易日数据。

## §六 fixture→预期值映射登记(AC-03.6/3.7;逐断言组可追溯)

| 断言组 | fixture 定义处(tests/test_p03_w2_glm_g2.py) | 预期值形态 |
|---|---|---|
| fixture 自检(T0) | `build_input_mode_a`/`build_input_mode_b`(全合成 GLMResearchInput) | `gia.validate_input(...) == []`(权威= G1 既有校验器,复用非复制) |
| schema 正向(T1) | `build_valid_output_mode_a`(两竞争假设)/`build_valid_output_mode_b` | `validate_output(...) == []`+映射表整字典比对 `EVIDENCE_MAP_LITERAL`(4 行字面量) |
| 解析容忍(T1b) | 内联 JSON 文本(裸/围栏/注释/双层包裹/非 dict/垃圾/空) | (obj,err) 字面量+错误消息子串 |
| 负向敏感性(T2,34 条) | `_inp()`/`_out()` 派生变体(逐字段篡改: counter 清空/数值 9.99/改写 2.94/判据同构/ack 清空/限制项删除/ID 三形态/单假设/high 违例两种/证据空两形态/额外与缺失字段/降级两形态/指针缺失/spec 三非法/echo 两模式/模式B 三形态) | 问题消息子串字面量(『counter_evidence为空』『编造阈值』『竞争性不足』『未逐项复述』等);正向对照用例 `== []` |
| 阈值三来源(T3) | 合法集=`TIPS_FACT`/`GOLD_FACT` 数值∪`REG_TARGETS`{1000,30000,25}∪`PRIOR_TRIGGERS`[4.5,4300] | 编造 3.5 拒;来源(i)=2.93/(ii)=25/(iii)=4300 各过;`registry_legal_targets` 经 monkeypatch `REG_SYN` 提取=={1000,30000,25};非点名字段族不提取 |
| 失败三径(T4,13 条) | attempts 注入序列(解析失败文本/篡改输出 JSON/瞬态错误 kind/cost_breaker/未知 kind) | outcome 字面量(ACCEPTED/ACCEPTED_DOWNGRADED/ABSENT_REGISTERED)+attempts_used+trace kinds+backoff(1.0/2.0)+缺席事件字段整表+`InvalidResearchInput` 异常 |
| 数值抽取(T5) | 内联混合文本(标识符/日期/年份/月份/单位后缀/千分位/带符号) | 抽取列表字面量([2.2,2.93,73.0,4186.7]/[-0.5,3.7,73.0]/[]) |
| echo/复用(T6) | 纯产品结构(无 fixture 依赖) | `ECHO_LITERAL` 整字典+'hs-1.0'==gia 登记值+枚举元组字面量+`gov.gia is gia` |
| 源码锁(T7) | 被测模块源文件(scripts/glm_output_validator.py) | 禁用模式清单(http/requests/socket/urllib/os.environ/API_KEY/api_key/open(/glob(/data/daily/launchd/subprocess)零命中+复用标记三断言 |

## 参考

- 冻结合同: IA-P03-W2-GLM-WP-G2-AC-v1.0(提示词内嵌;引擎存档路径执行Agent 不可达)
- 设计: docs/P03_W2_GLM_DESIGN.md §三(b)(c)/§四/§五(1)/§六/§七 WP-G2 行(blob c72d41a1,与设计支 0c8de3c3 侧等值)
- G1 对齐: scripts/glm_input_assembler.py(输入契约复用)/docs/P03_W2_GLM_G1_REPORT.md(登记纪律与漂移策略先例)
- 预测规格对齐: scripts/report_generator.py:525-526(op/mode 枚举)/scripts/allocation_engine.py:77(VERIFY_MODES)
- 执行报告(细节): docs/P03_W2_GLM_G2_REPORT.md
