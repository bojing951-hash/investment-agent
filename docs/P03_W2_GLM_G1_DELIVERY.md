# IA-P03-W2-GLM-WP-G1 交付说明(DELIVERY)

> 工作包: IA-P03-W2-GLM-WP-G1(WP-G1 结论层输入装配器)· 分支 `dev/p03-w2-glm-g1`
> 基线: a6d086b8b184067d530815e0bf8963d959275743 + 指定并入步 merge 0c8de3c3(R019 PASS 设计六件)
> 证据包: `/tmp/p03-w2-glm-g1-evidence/IA-P03-W2-GLM-WP-G1-EVIDENCE.zip`(zip sha256 见 §二)
> 边界: 零真实 GLM/LLM 调用、零凭证、零付费、零网络出站(真实调用属 WP-G4,PENDING);零运行产物(依据见 REPORT §0.3)。

---

## §一 改动(交付清单,k=4,与 REPORT §0.2 登记一致)

| 文件 | 形态 | 摘要 |
|---|---|---|
| `scripts/glm_input_assembler.py` | 新增(装配器模块) | `GLMResearchInput` 装配(模式 A/B 双形态): 九字段输入契约+validate_input 字段级校验;Gate A R2/R3 复算放行(FAIL/None 拒绝);R5 内容指纹绑定+expected 声明比对(篡改拒绝);缺席登记 classify_absence 四级枚举(零填0);禁直读四机制(唯一接入点=rp.select_snapshot 标准化层,单处 ACCESS_POINT_EXEMPT;source_file 披露槽位;零算术投影);模式 B=E2E-B IR 契约(RESOLVED 接地 fail-closed/缺席透传/无IR拒绝);echo_params 登记参数三方一致 |
| `tests/test_p03_w2_glm_g1.py` | 新增(专项测试) | 33 用例: FixtureSanity 2+T1 契约 3+T1c 负向 6+T2 门禁 2+T2b 产物路径 1+T2c 源码锁 1+T3 缺席 1+T3b 四级 4+T4 篡改 2+T5 模式B 6+T6 R1壳 2+T7 schema 2+T8 echo 1;全合成 fixture 唯一数据源;预期值字面量硬编码 |
| `docs/P03_W2_GLM_G1_REPORT.md` | 新增(执行报告) | §零 规格抄录(DESIGN L216-220 逐字)+白名单登记+零运行登记;§一 前置实读(file:line);§二 参数登记(先登记后运行);§三 逐要点映射;§四 git 取证 |
| `docs/P03_W2_GLM_G1_DELIVERY.md` | 新增(本件) | 五节+漂移维护策略专节 |

改动总量=纯新增 4 文件,零修改既有文件(diff --name-status 基线..尖端=6 行设计件 A+4 行白名单 A,零 M/D)。

## §二 证据

- **本地逐套件**: 58 份套件日志 `/tmp/p03-w2-glm-g1-evidence/local-ci/`(57 跑+1 合同排除)=56 绿+1 既有红(test_p4_fixes: 4 项 monthly_review 数据块,基线 a6d086b 既有归因「本地真实数据演化所致」,与本包零导入关系——本包不 import monthly_review;CI 侧数据面不同,基线 CI run 41862875466=56 success)。新增套件恰 1 → CI 预期 57 零回归。
- **负向敏感性**: 4 注入全红后回绿(日志 `negative-sensitivity/`): D1 门禁移除→红3/D2 摘要比对移除→红1/D3 缺席吞掉→红1/D4 常量漂移→红3;RESTORE-GREEN exit=0;模块字节还原(diff 验证)。
- **零触碰**: `data/daily`(24)+`data/research`(3)sha256 快照 `datapath-zero-touch-snapshot.txt`(27 文件);本包无真实运行面→零运行产物(REPORT §0.3 依据)。
- **git 取证**: 原样输出于证据包成员③(name-status/rev-parse/log/reflog/ls-remote+merge 提交信息)。
- **CI**: 操作者 CHECKPOINT dispatch(执行Agent 禁自行触发);登记件将落 `rounds/026/GLM-WP-G1-CI-dispatch-evidence.md`(引擎侧,本包引用其路径)。
- **zip 整体 sha256**: 见证据包成员⑧ SHA256SUMS 与 stdout 自述(本文件不预写,以装配后实测为准)。

## §三 逐 AC 自评

| AC | 自评 | 指引 |
|---|---|---|
| AC-01 规格抄录与登记 | PASS(自评) | REPORT §0.1 逐字抄录+行号(DESIGN L216-220 实读);清单 k=4 逐条附依据;结构约束核验(§0.2);命名偏差如实登记 |
| AC-02 逐要点映射 | PASS(本地)(自评) | REPORT §三 五要点+模式B 行全映射;参数登记=常量=echo(T8);要点⑤ CI 侧待操作者 dispatch(NOT VERIFIED 部分,如实) |
| AC-03 测试与确定性 | PASS(自评) | 33 用例全绿;零网络/零新依赖/全合成 fixture/字面量硬编码;漂移维护策略专节(§五)+fixture→预期值映射(§六);GLM 调用面=不适用(清单无调用面类文件: 无客户端/调用编排/适配器;判定依据=REPORT §0.2 清单+模块 import 面纯标准库+既有模块) |
| AC-04 引用真实性 | PASS(自评) | REPORT/DELIVERY file:line 逐条可寻(±3);无跨支引用(设计六件=并入后工作树实读);注入内容零引用(本双文档未引用注入摘要作事实源) |
| AC-05 范围/分支/隔离 | PASS(自评) | diff=恰 6+4 行 A 零 M/D;1 指定 merge(e67f710)+线性开发;既有分支尖端不变+唯一新增 dev/p03-w2-glm-g1(ls-remote 实取);LIVE 零写入/launchd 零触碰/档案不 commit/.gitignore 不改 |
| AC-06 CI 与证据包 | 部分 NOT VERIFIED(如实) | 证据包八类最低集已装配+SHA256SUMS;CI dispatch=操作者动作,本轮未发生→成员⑤登记件为悬空预期路径,conclusion 待 CHECKPOINT;五节齐备+result.md 四段=自述 |
| AC-07 研究纪律 | PASS(自评) | 禁直读(源码+产物双层负向);零填0(T3);无投资建议文案;零真实调用/凭证/付费(源码锁 T2c: 零 os.environ/零 API_KEY/零网络 import);W4/W5 零涉及;白名单外需求零实施(发现登记: 见 §四) |

## §四 如实偏差与登记发现

1. **测试文件命名偏差**(登记非冲突): DESIGN L220 工件 glob `tests/test_p03_g1*.py` vs 合同固定推导名 `tests/test_p03_w2_glm_g1.py`——以合同名为准(REPORT §0.2 偏差登记)。
2. **模式 A ABSENT_SOURCE 可达性**(登记): 当前注册表拓扑(4 通道均含核心指标)下 Gate 放行态内该级不可达(通道失败必致核心缺失→FAIL→拒绝装配=上游正确行为);四级枚举完整实现于 classify_absence 纯函数并有直测(T3b)。非缺陷,如实登记(REPORT §二.3)。
3. **test_p4_fixes 本地红 4 项**(既有,非本包): 基线归因沿袭(monthly_review 数据块,本地真实数据演化);本包与其零导入关系。
4. **AC-06 CI 侧 NOT VERIFIED**: dispatch 权在操作者(合同 §六.5),执行Agent 禁自行触发;补 CI 证据=CHECKPOINT 动作,非本包整改项。
5. **白名单外需求发现登记(不实施)**: ①snapshot_binding 若需绑定"任务档侧先验 digest"需 E2E-A 任务档增字段(白名单外,留待 WP-G3 映射承接);②prior_knowledge 自动渲染(theses_block/views_block)需调用 report_generator/allocation_engine 既有函数,属调用编排层(后续包);③`normalize_macro` 等标准化层的通道级复用与 GLM 层无直接接口缺口,无需改动。
6. **UTC 时刻**: 开工 2026-11-04T16:27:04Z;本文件落笔 2026-11-04T16:5xZ(实取以取证输出为准)。

## §五 漂移维护策略(AC-03.6 专节,三要素)

1. **测试预期值唯一来源=仓库内版本化合成 fixture**: `tests/test_p03_w2_glm_g1.py` 内 `build_synthetic_snapshot`/`build_synthetic_task`/`build_synthetic_query`(全部合成,数值中性构造+字面量锚点 2.93/4186.7);测试断言的期望值均硬编码字面量或按登记规格独立重导(spec_digest 用 hashlib+canonical JSON 规格,不导入被测模块函数)。
2. **fixture 演进时预期值与 fixture 同一 commit 变更**: 若合成 fixture 结构/锚点变更(如注册表 active 集演进致 fixture 全集变化),受影响断言与 fixture 定义在同一提交内同步修改;本包交付后任何此类变更走登记型修订(新工作包/合同修订),禁散点改。
3. **真实数据档永不进入测试预期值来源**: 测试零读取 `data/daily/`/`data/research/`(源码级: 测试仅 tempfile+内联合成;fixture 声明构建复用 rp.recompute_gate_a 既有权威机制=机制复用非数据读取);fixture 自检(FixtureSanity)只断言合成物经既有机制回读期望态,不锚定真实交易日数据。

## §六 fixture→预期值映射登记(AC-03.6/3.7;逐断言组可追溯)

| 断言组 | fixture 定义处(tests/test_p03_w2_glm_g1.py) | 预期值形态 |
|---|---|---|
| 门禁自检(FixtureSanity) | `build_synthetic_snapshot`(全集)/`rebuild_declarations`(drop 变体) | 期望态字面量 'PASS'/'DEGRADED'(经 rp.gate_status 回读,权威=既有机制) |
| 九字段/契约常量(T1/T8) | fixture 无关(纯产品结构) | 字面量: gri-1.0/hs-1.0/zh/2/True/True/字段名表/echo 全表 |
| snapshot_digest(T1) | `build_synthetic_snapshot` 产物 | 登记规格独立重导: sha256(canonical JSON)[:16](hashlib 直算,不导入 _digest_ref) |
| facts 投影(T1/T3/T5) | `TIPS_FACT_PROJ`/`GOLD_FACT_PROJ` 模块级字面量(锚点值 2.93/4186.7 于 `build_synthetic_snapshot(value_overrides=…)` 注入) | 字面量整字典比对 |
| 缺席登记(T3/T3b) | drop_metrics=('SILVER_F',)/JGB_10Y(不在注册表)/手建最小快照(READ_FAIL·m6 窗口) | 字面量 (level,reason) 整表比对 |
| 篡改拒绝(T4) | 值篡改 9.99/声明说谎 'PASS'/计数 +1 | 异常类型+消息子串字面量 |
| 模式B(T5) | `build_synthetic_query`(IR 字面量,digest 由 spec_digest 独立重导) | 字面量+digest 重导 |
| R1 壳(T6) | tempfile 写入合成快照 JSON | 与核心装配结果整 dict 相等(同输入自洽性,非预期值来源) |
| 源码锁(T2c) | 被测模块源文件 | 计数/模式字面量(1 处豁免标记/零 open(/零 daily 字样等) |

## 参考

- 冻结合同: IA-P03-W2-GLM-WP-G1-AC-v1.0(提示词内嵌;引擎存档路径执行Agent 不可达)
- 设计: docs/P03_W2_GLM_DESIGN.md §三(a)/§六/§七 WP-G1 行;E2E-B 对接: docs/P03_E2EB_DESIGN.md §三
- E2E-A 对齐: scripts/research_task_manager.py(schema 复用)/docs/P03_W1_E2EA_REPORT.md(登记纪律先例)
- 执行报告(细节): docs/P03_W2_GLM_G1_REPORT.md
