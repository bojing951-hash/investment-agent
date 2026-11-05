# IA-P03-W2-GLM-WP-G4 REPORT(GLM 研究结论层第 4/末实现包·真实调用接线)

> 冻结合同: IA-P03-W2-GLM-WP-G4-AC-v1.0(2026-11-05 09:3x HKT 冻结存档,sha256=596ab62e…f458;本报告为合同 §零登记制落点)
> 分支: `dev/p03-w2-glm-g4`(自基点 d667a4e5f3faf93fffbaa1ab1bfd67c386fee2e3 切出;纯线性,无并入步)
> 开工 UTC: 2026-11-05T01:28:35Z(步骤0 时序自检: 工作树 clean,当前 main,操作者已排程发车)

## §零 规格抄录与交付面登记(合同 AC-01 落点;开工首步)

### 0.1 双门核验记录(步骤1-2,先于一切开发)

| 门 | 核验结果 | 证据 |
|---|---|---|
| 占位符三处实值化 | BASE-G4=d667a4e5f3faf93fffbaa1ab1bfd67c386fee2e3 与 `git ls-remote origin dev/p03-w2-glm-g3` 实取全值一致;BASE-G4-CI-SUITES=59(注入合同冻结章②实跑清点值);BRANCH-SET=36 支全表内嵌完整 | ls-remote 实取输出入证据包③ |
| 生效前置(WP-G3 PASS) | 满足——合同冻结章③明示 rounds/028/audit.md VERDICT: PASS;占位符已实值化即生效信号 | 合同冻结章(注入文本) |
| **执行发车硬门(实批落档证据行)** | **满足**——合同冻结章②: 用户 2026-11-05 实批凭证/费用(原文「前三个全部审批」覆盖本包),批复行=PENDING-APPROVALS.md 2026-11-05 09:3x 节,批准对象=本合同 §七.5/§七.7 已冻结参数包(CB-1~CB-4/日上限 USD 5.00/登记模板),非空白授权;凭证注入=驱动进程环境(GLM 三元组),零落盘零入档 | 合同冻结章(注入文本);步骤7 环境存在性核验=GLM_API_KEY PRESENT(仅存在性,值零打印零落盘) |
| 实批覆盖面 vs 本包所需调用面 | 本包所需真实调用面=**唯一面: 模式 A 真实调用冒烟**(DESIGN L238 要点①;见 §0.1 末尾对照),调用量 1~3 次(≤gov.MAX_RETRIES),费用估算远低于日上限 USD 5.00,熔断 CB-1~CB-4 全程护航——全部在 §七.5/§七.7 冻结参数包覆盖内,**无超出冻结约束的调用要求** → 无情形(d)冲突 | §0.1 调用面对照(下) |
| 设计支尖端复核 | `git ls-remote origin dev/p03-w2-glm-design`=0c8de3c3bece78dd2d9f0d8928a817b597e3104e(前7位=0c8de3c ✓) | 证据包③ |

**设计在场核验(步骤4,本包无并入步)**: ①`git merge-base --is-ancestor 0c8de3c3… HEAD` exit 0(可达 ✓);②设计六件 `git ls-tree` 双侧(HEAD vs 0c8de3c3)blob 等值对照 6/6 相同: P03_E2EB_DELIVERY=5e0eb558…,P03_E2EB_DESIGN=89de7de9…,P03_E2EB_QUERY_SURFACE_INVENTORY=9306e68b…,P03_W2_GLM_DELIVERY=772ad4cd…,P03_W2_GLM_DESIGN=c72d41a1…,P03_W2_GLM_INVENTORY=5cb643a1…(全 blob 哈希见证据包③)。核验通过,合法开工。

### 0.2 WP-G4 行四要素逐字抄录(实读 `docs/P03_W2_GLM_DESIGN.md` §七,基线工作树实况)

以下为 DESIGN §七 WP-G4 行**逐字抄录**(无增删改字;行号=基线工作树实读行号,审计对照允许偏差≤3行):

- **L234**: `**WP-G4 真实调用接线(需用户批准/PENDING)**`
- **L235**: `- 目标: 以 DP-1~DP-4 冻结值接线真实 GLM 调用,冒烟测试沿 test_glm_live 模式(门禁确定性与模型遵从性双测[实取: tests/test_glm_live.py L1-16, 2026-11-02])。`
- **L236**: `- 范围: 调用点接入+费用/用量记录+熔断;不含生产部署与 launchd。`
- **L237**: `- 依赖: WP-G1/G2/G3;**GLM 凭证与费用=用户保留事项——需用户批准/PENDING**(DP-3/DP-4 决议齐备前本包不得启动;零凭证状态下其余三包均可完整交付与验收)。`
- **L238**: `- 验收要点草案: ①真实调用冒烟: 结构化输出过校验器+数值接地核对(工件: 测试运行记录+凭证使用登记,默认跳过门控沿 RUN_GLM_LIVE 模式[实取: tests/test_glm_live.py L31-33, 2026-11-02]) ②费用熔断测试(工件: 测试文件) ③调用日志与用量记录落盘(工件: 日志文件) ④CI 零回归且真实调用用例默认跳过不破坏离线套件(工件: run ID)。`

四要素齐备(目标/范围/依赖/验收要点),无缺失。**冲突自查(合同 §零(iv))**:
- 要素齐备可推导 ✓;
- 依赖列「WP-G1/G2/G3」与基线实况一致(gia/gov/gci 三模块在场,接口实读见 §一)✓;不要求并入他支、不要求 B 族先行 ✓;
- 「需用户批准/PENDING」与合同 PENDING 门**同一方向非冲突**: 实批已于 2026-11-05 落档(冻结章②),DP-3(费用上限=§七.5 冻结包 USD 5.00/CB-1~CB-4)/DP-4(凭证来源=环境变量 GLM_API_KEY,冻结章⑤「驱动进程环境 LIVE 单一来源」)决议齐备 → 依赖解除,合法启动 ✓;
- DESIGN 要求真实调用**不构成冲突**(合同 §零(iv) 明示「G4=真实调用包,DESIGN 要求真实调用本身不构成冲突」);DESIGN 冒烟机制(test_glm_live 式测试内门控)由合同 AC-03.7「G4 改写,G 族先例的方向反转」**显式改道**为「真实调用仅发生在执行段功能验证步骤,不写入任何 tests」——本包按合同机制承接 DESIGN 冒烟语义(要点①工件=执行段运行记录+REGISTRY 登记;要点④离线不受破坏=真实调用面整体在 tests 之外,强于默认跳过),登记为机制承接非冲突 ✓;
- DESIGN 未另立熔断阈值/调用次数上限(仅泛称「熔断」)→ 合同冻结值 CB-1~CB-4 全程适用,无阈值冲突 ✓;DESIGN 未要求超出冻结约束的调用面(冒烟 1 个调用面×≤3 次调用≪CB-2=60)✓。

→ 无情形(d)冲突,合法开工。

### 0.3 交付文件清单(登记制白名单,k=5;推导逐条附 DESIGN 依据)

DESIGN L236 范围列为**模块级**(「调用点接入+费用/用量记录+熔断」=单一接线模块的三个功能面,非三个模块;DESIGN 未枚举多模块,G 族先例 G1/G2/G3 各=1 个 scripts/ 模块)→ 按合同 §零(ii) 固定推导规则生成:

| # | 路径 | 类型 | DESIGN 依据 | 推导规则 |
|---|---|---|---|---|
| 1 | `scripts/glm_conclusion_client.py` | 代码(真实调用接线模块: 调用点接入+费用/用量记录+熔断) | DESIGN L235「接线真实 GLM 调用」+L236「范围: 调用点接入+费用/用量记录+熔断」 | 每个代码模块=scripts/ 下恰 1 文件 |
| 2 | `tests/test_p03_w2_glm_g4.py` | 测试(全合成桩,零真实出站) | DESIGN L238 要点②④工件「测试文件」+合同 AC-03 全部生效项 | 含代码则必含本文件(合同固定名) |
| 3 | `docs/P03_W2_GLM_G4_REPORT.md` | 文档(本件) | DESIGN L238 工件面(要点逐条证据映射/参数登记落点);合同必含件 | 必含 REPORT |
| 4 | `docs/P03_W2_GLM_G4_DELIVERY.md` | 文档(交付说明) | DESIGN L238 工件面;合同必含件 | 必含 DELIVERY |
| 5 | `docs/P03_W2_GLM_G4_CREDENTIAL_REGISTRY.md` | 文档(凭证使用登记件) | DESIGN L238 要点①工件「凭证使用登记」;合同必含件(头部=合同 §七.7 冻结模板) | 必含 REGISTRY |

**结构约束核验(iii)**: 与 `git ls-files` 零重合(5 路径在基线 d667a4e5 工作树均不存在,开工时实测对照,取证见 §四)✓;必含 DELIVERY(#4)与 REGISTRY(#5)✓;含 .py 实现(#1)则必含对应 tests(#2)✓。

### 0.4 运行产物边界登记

要点①③含真实运行面(真实 GLM 调用+调用日志/用量记录落盘)→ 产物落 `data/research/`(允许写入、不 commit、不入 diff);`data/daily/` 只读(快照构建输入);冒烟输入快照经 `scripts/snapshot_builder.py`(既有标准化层)产出入 `data/research/`;`.gitignore` 不改。

### 0.5 真实调用面对照(实批覆盖面 vs 所需)

| 调用面 | 触发要点 | 出站估算 | 熔断 | 实批覆盖 |
|---|---|---|---|---|
| F1 模式 A 真实调用冒烟: `scripts/glm_conclusion_client.py` 执行段入口(CLI `--live-smoke`),端点=open.bigmodel.cn/api/paas/v4(智谱 OpenAI 兼容通道),模型=glm-5.3 | L238 要点① | 1 次+失败重试 ≤3 次(≈1~3 次) | CB-1~CB-4 全程激活 | §七.5/§七.7 冻结参数包内 ✓ |
| F2 模式 B 真实调用 | 无(DESIGN L219[实读]: 模式 B 依赖 E2E-B WP-B1/B2 产物;E2E-B 族=平行链不在本包基线谱系 → 按 G1 登记的缺席登记路径处理,本包不设该面) | 0 | — | 不适用 |

---

## §一 前置实读登记(复用调用面,file:line 为基线工作树实读)

### 1.1 上游依赖接口(G1/G2/G3,复用调用,禁复制分叉)

| 机制 | 落点(file:line) | 用途 |
|---|---|---|
| G1 输入契约校验 `validate_input` | `scripts/glm_input_assembler.py:293` | 执行段装配产物契约回验 |
| G1 模式 A 装配 `assemble_mode_a` | `scripts/glm_input_assembler.py:437` | 冒烟输入装配(快照→GLMResearchInput) |
| G1 R1 壳入口 `assemble` | `scripts/glm_input_assembler.py:550` | CLI 侧 ymd+目录→装配(唯一取数通道经 R1 标准化层) |
| G2 解析容忍 `parse_hypothesis_set` | `scripts/glm_output_validator.py:111` | 真实响应文本→JSON 对象(围栏剥壳) |
| G2 输出契约校验 `validate_output` | `scripts/glm_output_validator.py:234` | 结构化输出过校验器(要点①) |
| G2 失败三径状态机 `run_conclusion_pipeline` | `scripts/glm_output_validator.py:582` | 执行段编排权威状态机(attempts 序列消费方) |
| G2 数值接地集 `collect_evidence_numbers`/`legal_target_numbers` | `scripts/glm_output_validator.py:154`/`:186` | prompt 合法数值枚举+冒烟接地核对表 |
| G2 常量 `MAX_RETRIES`/`TRANSIENT_ERROR_KINDS`/`COST_BREAKER_KIND`/OUTCOME 族 | `scripts/glm_output_validator.py:54`/`:47`/`:48`/`:49-51` | 重试预算与失败类词表对齐(复用导入) |
| G3 结论记录 `build_conclusion_record` | `scripts/glm_conclusion_integrator.py:502` | 每轮结论(含缺席)落档记录构造 |
| G3 append-only `append_conclusion_record` | `scripts/glm_conclusion_integrator.py:567` | 结论入共享档案(幂等/版本追加/禁改) |
| E2E-A 任务 schema 最低字段(经 G1) | `scripts/research_task_manager.py:36`(`SCHEMA_MIN_FIELDS`) | 冒烟任务档字段契约(G1 `_task_ref` 复用面) |
| 机制族类别 `MECHANISM_CATEGORIES`(7 类) | `scripts/allocation_engine.py:104` | prompt 机制族提示槽(§四(1)槽2 明示复用) |
| GLM 通道实值(基线/端点/模型) | `env_config.py:28-29` | DP-1(a) 冻结初值来源(base_url/model 同值登记) |
| 调用模式参照(流式+reasoning_effort 踩坑备案) | `scripts/report_generator.py:574-605`(`_call_glm`) | DP-1 决议依据: 同通道流式+reasoning_effort=low(本包接线沿用其参数形态,实现独立) |
| 默认跳过门控模式参照 | `tests/test_glm_live.py:31-33` | RUN_GLM_LIVE 门控模式(DESIGN L238 要点①明示) |

### 1.2 设计依据实读(DESIGN 其余被引节)

- §三(b) 失败三径/§三(c) 七字段输出契约: `docs/P03_W2_GLM_DESIGN.md:78-116`;
- §四(1) 六模板槽位: `:122-131`(槽1 现象复述 L126/槽2 机制族 L127/槽3 竞争性强制 L128/槽4 反方证据 L129/槽5 数值接地 L130/槽6 缺席承接 L131);§四(3) 反方证据三机制: `:143-148`(机制三措辞 L147);
- §五(2) 门禁保护/§五(3) append-only: `:163-175`;§六 模式 A/B 差异: `:193-209`;§八 红线: `:244` 起;
- DP-1~DP-4 决策点: `:45-48`(本包冻结初值见 §二.2);
- GLM INVENTORY(§一~§二 面与缺口): `docs/P03_W2_GLM_INVENTORY.md`(实读;GG-07→DP-1~4+WP-G4 承接,DESIGN L240)。

### 1.3 数据接入点(禁直读纪律)

本模块(代码)零 `open()` 于 `data/daily/`、零原始采集档路径引用;执行段输入唯一来源=G1 装配产物(经 R1 只碰 `research_snapshot_*.json` 标准化产物);冒烟快照由既有 `scripts/snapshot_builder.py`(Layer 3 标准化层,`scripts/snapshot_builder.py:236` `build_snapshot`)产出于 `data/research/`——快照构建属既有标准化层运行,非本模块读取面;源码 grep 反证见测试 T5/证据包。

---

## §二 实现参数登记(登记制纪律: 先登记后运行,运行后禁回改)

### 2.1 合同冻结值(禁回改;echo=常量=登记三方一致)

| 参数 | 登记值 | 依据 |
|---|---|---|
| CB1_MAX_CONSECUTIVE_FAILURES | 5 | 合同 §七.5 CB-1(连续≥5 次失败 TRIPPED) |
| CB2_MAX_OUTBOUND_PER_SEGMENT | 60 | 合同 §七.5 CB-2(单执行段 ≤60 次出站,达限软停) |
| CB3_DAILY_COST_CAP_USD | 5.00 | 合同 §七.5 CB-3(单日 UTC 累计费用估算 ≤USD 5.00,达限 TRIPPED) |
| CB4_TIMEOUT_SECONDS | 120 | 合同 §七.5 CB-4(单次>120 秒计失败并入 CB-1) |
| REGISTRY 模板 | 合同 §七.7 十字段 | REGISTRY 头部逐字落档 |

### 2.2 本包登记初值(DP 决议落点;DESIGN L45-48;运行后禁回改)

| 参数 | 登记值 | 依据/性质 |
|---|---|---|
| GLM_BASE_URL_DEFAULT | `https://open.bigmodel.cn/api/paas/v4` | DP-1(a)[实取: env_config.py:28 同值];冻结初值 |
| GLM_MODEL_DEFAULT | `glm-5.3` | DP-1(a)[实取: env_config.py:29 同值];冻结初值 |
| CALL_TEMPERATURE | 0.2 | DP-2 低温档候选区间 0.1-0.2 内取 0.2(DESIGN L46「结论层建议低温档」);冻结初值 |
| CALL_REASONING_EFFORT | `low` | DP-1/踩坑备案[实取: report_generator.py:579](思考不可关闭,low 控档防吃光 max_tokens);冻结初值 |
| CALL_MAX_TOKENS | 16000 | 结构化假设集输出+思考余量(周报链 32000 为长文报告面,本层输出紧凑,16k 足额);冻结初值 |
| CALL_CLIENT_TIMEOUT_S | 125.0 | CB4+5s 边际(客户端超时略宽于 CB-4 判定阈,保证 120s 判定先于客户端切断;CB-4 判定独立于客户端超时) |
| CREDENTIAL_ENV | `GLM_API_KEY` | DP-4(a): 环境变量唯一凭证来源;**零本机回退路径**(DP-4(c) 语义在本模块落实;env_config.py 既有回退属白名单外文件,登记发现不代改) |
| LIVE_GATE_ENV | `RUN_GLM_LIVE` | 默认跳过门控,沿 test_glm_live.py:31-33 模式(DESIGN L238 要点①明示) |
| RETRY 预算 | gov.MAX_RETRIES=3 | 复用 G2 登记值[实取: glm_output_validator.py:54](不另立) |
| 退避 | 线性计划表记录不实际休眠 | 复用 G2 BACKOFF_LINEAR_BASE 语义(管线 trace 承载) |

### 2.3 费用估算参数(CB-3 口径;合同明示「执行段估算值如实登记,账单核对属观察期事务不作 AC 判据」)

| 参数 | 登记值 | 性质 |
|---|---|---|
| EST_INPUT_USD_PER_MTOK | 3.0 | [示意·非实取]保守输入单价估算(USD/1M tokens;非账单真值) |
| EST_OUTPUT_USD_PER_MTOK | 9.0 | [示意·非实取]保守输出单价估算(USD/1M tokens;非账单真值) |
| EST_FLOOR_USD_PER_CALL | 0.02 | [示意·非实取]单次调用保守下限(用量不可得时按此计;失败调用亦计) |
| 估算式 | `max(EST_FLOOR, prompt×3.0/1e6 + completion×9.0/1e6)` | 单调保守(高估方向安全: 早触 CB-3 不晚触) |

### 2.4 桩注入点登记(合同 AC-03.7;注入面=显式依赖注入)

| 注入点 | 形态 | 位置(file:line) |
|---|---|---|
| `client_factory` 参数 | 显式依赖注入: `call_glm_once(..., client_factory=None)`;None=真实路径(函数体内惰性 `from openai import OpenAI`);测试注入假工厂返回合成流事件对象 | `scripts/glm_conclusion_client.py`(实现后落行号,见 §三映射表;模块级零 openai import) |
| `CircuitBreaker` 直驱 | 合成注入失败序列/计数/费用/延迟(note_failure/note_outbound/note_success/classify_elapsed) | 同上 |
| `breaker=参数` | run_live_conclusion 编排注入预置熔断器(预 TRIPPED 场景) | 同上 |
| `legal_targets=参数` | build_prompt 合法数值枚举注入(测试不依赖真实 registry) | 同上 |

---

## §三 逐要点证据映射表(合同 AC-02 落点;file:line 为交付终态实取)

> 交付文件 sha256 锚定: `scripts/glm_conclusion_client.py`=
> a846f727ac299e4e4a9432d91ca147dd657e89b918378439b19a800b32d0e718,
> `tests/test_p03_w2_glm_g4.py`=
> 404de82b60026208d3a5f16189e721344ce18cf5752fabe2bc3cfb8cafa93e48
> (负向敏感性 D1/D2 注入→红→还原后逐字节一致,见证据包②)。

### 要点① 真实调用冒烟: 结构化输出过校验器+数值接地核对(工件: 测试运行记录+凭证使用登记)

| 项 | 落点/证据 |
|---|---|
| (a) 实现落点 | 接线链: `scripts/glm_conclusion_client.py` `call_glm_once`(:468,真实出站点 :497 流式 create)→`run_live_conclusion`(:565,G2 权威管线消费方)→`run_smoke`(:673,CLI 冒烟入口 :747);门控 `_live_gate`(:545);数值接地=G2 `validate_output`/`collect_evidence_numbers` 复用(§一.1);六槽位 prompt `build_prompt`(:302) |
| (b) 证据指针 | REGISTRY `G4-CRED-001`(3 次出站/费用 $0.0667/未触发);证据包⑤ real-run/: `live_smoke_F1_attempt1.log`(全 stdout+退出码 0)、`glm4_usage_log_20261104.jsonl.redacted-copy`(逐次 usage/费用/熔断态)、`glm4_live_smoke_20261105T015850Z.json.redacted-copy`(终态报告含 trace 反馈链) |
| (c) 自检结论 | **部分(情形(c)如实)**: 接线链端到端真实工作——门控开→3 次真实流式出站(26.9s/26.1s/19.7s,均<CB-4)→G2 逐次裁决(尝试1 schema 外字段/尝试2 limitations 义务+接地/尝试3 仅剩数值接地)→径1 反馈回注两轮生效(失败面收敛)→预算 3 用尽→**终裁 ABSENT_REGISTERED**(模型输出未过校验器,数值接地未达)= 合法如实结果,禁重试凑结果;参数(temperature=0.2/reasoning_effort=low)为登记冻结初值,运行后禁回改 |
| (d) 补证据轮第 4 次执行段(2026-11-05T02:45:52Z 先登记 G4-CRED-002 后发起) | **执行环境权限阻断,零真实出站**(2026-11-05T02:45:52Z~02:48:27Z 之间 4 次发起,均被本会话工具权限层拒绝于命令执行前「This command requires approval」,含一次显式非沙箱批准形式,无批准通道应答);冻结参数原样零改动,代码/测试零改动;零出站独立佐证=双面锚定 34/34 文件哈希不变+usage log 仍 3 行+无新 smoke 报告;REGISTRY §五如实登记;按追加指令「恰 1 次不追加」停止发起,处置权操作者;证据=证据包⑥ real-run/live_smoke_F1_attempt2_blocked.txt+anchors/*-round2.txt |
| (e) 补证据轮第 4 次尝试·操作者代执行(2026-11-05T03:24:43Z 先登记 G4-CRED-003[git cf7c75c]→03:26:33Z 出站) | **1 次真实出站传输层成功,模型输出仍未过校验器,终裁 ABSENT_REGISTERED(如实)**: 单次 34.3s<CB-4/$0.0220;失败面=径2义务(hypotheses[0]/[1].limitations 未承接 Gate A 降级影响面)+接地失败([0.3,25.0] 不在证据包),与尝试 3 残余面(数值接地)同域;恰 1 次=RETRY_BUDGET 运行时进程内置 1(模块文件零改动,模型面冻结参数分文未动);操作者代执行依据=二复审处方「操作者择时重发第 4 次尝试或代执行,同 CI dispatch 先例」;处置§五预置分支生效→§二兜底终态(接受 (c) 如实缺席定稿);REGISTRY §六+证据包⑥ live_smoke_F1_attempt3_operator.log |

### 要点② 费用熔断测试(工件: 测试文件)

| 项 | 落点/证据 |
|---|---|
| (a) 实现落点 | `CircuitBreaker` `scripts/glm_conclusion_client.py:164`(note_failure/note_success/note_outbound/classify_elapsed/state);测试 `tests/test_p03_w2_glm_g4.py` `T1_CircuitBreaker`(:331,11 用例,冻结值字面量硬编码 FROZEN_CB1=5/FROZEN_CB2=60/FROZEN_CB3=5.00/FROZEN_CB4=120,合同 AC-03.8): CB-1 恰在第 5 次连续失败 TRIPPED+TRIPPED 后零自动重试+编排层恰 5 次出站即停/CB-2 第 61 次拒绝+软停语义/CB-3 恰在累计>$5.00 TRIPPED/CB-4 恰 >120s 计失败并入 CB-1(120.0 边界不计,121.0 计)/reset 仅人工且不清计数器;费用口径 `estimate_cost_usd`(:126,T2 字面量断言 1949pt+1810ct=0.0221) |
| (b) 证据指针 | 证据包① local-ci/: `test_p03_w2_glm_g4.log`(48 用例全绿 exit=0);证据包② negative-sensitivity/: D1 注入 CB-1 阈值 5→4 → 3 用例红 |
| (c) 自检结论 | 过(合成断言恰按冻结值行为;执行段实测熔断器未触发: 3/60 出站、$0.0667/$5.00、0 连败) |

### 要点③ 调用日志与用量记录落盘(工件: 日志文件)

| 项 | 落点/证据 |
|---|---|
| (a) 实现落点 | `_log_usage` `scripts/glm_conclusion_client.py:557`(JSONL 追加);`run_smoke` 落盘三件: 用量日志(:682 `glm4_usage_log_{ymd}.jsonl`)+结论档案(:683-694 `glm_conclusions_archive.json`,G3 append-only)+终态报告(:695-723);日志字段=ts_utc/face/attempt/ok/kind/model/endpoint_host/elapsed_s/usage/cost_est_usd/breaker_before/after/error_note(脱敏,零凭证明文) |
| (b) 证据指针 | `data/research/glm4_usage_log_20261104.jsonl`(3 行,逐次 usage/费用)+同内容 redacted-copy 入证据包⑤;T4 用例断言日志结构/幂等追加 |
| (c) 自检结论 | 过(3 次出站=3 行记录,与 REGISTRY 出站次数一致) |

### 要点④ CI 零回归且真实调用用例默认跳过不破坏离线套件(工件: run ID)

| 项 | 落点/证据 |
|---|---|
| (a) 实现落点 | tests 全合成桩零真实出站(48 用例;client_factory DI §二.4);模块门控默认拒绝(CLI 无 `RUN_GLM_LIVE=1` → 打印跳过信息 exit=0,T5 子进程实测);真实调用仅执行段功能验证步骤(合同 AC-03.7 方向反转承接,§0.2) |
| (b) 证据指针 | 证据包① local-ci/: `suite-summary.txt`(61 条目=59 基线 CI 套件+test_glm_live skipped+新增本套件;59 exit=0 含新增,test_p4_fixes exit=1=既有环境红见 §五.3);CI run ID=操作者 CHECKPOINT 派发后落 `rounds/029/GLM-WP-G4-CI-dispatch-evidence.md`(本包不自行 dispatch,合同步骤15) |
| (c) 自检结论 | 本地同构过(CI 面套件零回归;CI 实跑值以操作者派发登记件为准,届时 60 套件预期全绿——CI 无 data/daily,见 §五.3 环境分叉说明) |

---

## §四 Git 取证与本地 CI 记录

### 4.1 分支与提交

- 分支 `dev/p03-w2-glm-g4` 自基点 d667a4e5f3faf93fffbaa1ab1bfd67c386fee2e3 切出(开工时 `git rev-parse` 实取基点一致;纯线性,零 merge 提交,单提交收尾);
- 补证据轮(2026-11-05T02:4xZ 起)追加 2 笔纯线性提交(恰白名单内 REGISTRY/REPORT/DELIVERY 追加行;零代码零测试改动);上句「单提交收尾」指首版交付时点,补证据轮提交后**对基线 diff 仍恰 5 行纯 A**(补证据轮仅改白名单内既有 A 文件,不新增路径),AC-05 判据不受影响;
- 提交内容=白名单恰 5 文件(`git diff --name-status d667a4e..HEAD` 预期 5 行纯 A);提交后 `git push origin dev/p03-w2-glm-g4`(禁 force);
- 取证输出原样留存证据包④ git/: name-status/rev-parse/log/reflog/ls-remote(推前推后双份)+设计在场核验输出(merge-base exit 0+六件 blob 等值)。

### 4.2 本地 CI 同构实测(步骤10;零真实出站)

- 运行器: 证据包① `run_local_ci.py`(逐套件 `python3 tests/test_*.py`,日志逐件落档,exit 码入 summary);
- 结果: 61 条目=59 exit=0(含新增 `test_p03_w2_glm_g4` 48/48 绿)+`test_glm_live` skipped(真实 GLM 付费调用,不进 CI)+`test_p4_fixes` exit=1(既有环境红,§五.3);
- 套件数对照: 59(基线 CI 套件)+1(新增)=60 CI 面;本地多出的 test_glm_live=CI 永久排除面(offline-tests.yml 实读);套件数符合预期,无情形(b)分流项。

---

## §五 偏离与如实登记

1. **要点① 模型遵从性未达(情形(c)如实,非 FAIL 项)**: 3 次真实出站传输层全成功,但 glm-5.3 在冻结初值(temperature=0.2/reasoning_effort=low)下 3 次尝试均未过 G2 校验器(失败面收敛: schema 外字段→limitations 义务→仅剩数值接地),终裁 ABSENT_REGISTERED 并按 G3 落档 CR-20261105-001。禁重试凑结果;若操作者判需模型遵从性达标,参数调整需另拟登记(v1.1),本包零事后回改。
2. **DESIGN 冒烟机制改道(合同显式承接,非冲突)**: DESIGN L238 要点①原文「默认跳过门控沿 RUN_GLM_LIVE 模式」的测试内冒烟,由合同 AC-03.7 显式改道为「真实调用仅执行段功能验证步骤,不写入任何 tests」;本包以模块级门控+CLI `--live-smoke` 承接同一语义(离线安全性更强: 真实调用面整体在 tests 之外)。已登记 §0.2。
3. **test_p4_fixes 本地 exit=1(既有环境红,零导入关系)**: 失败 4 项断言均数据依赖型;取证三链: ①基线复现——`git archive d667a4e` 纯跟踪树+本机真实未跟踪 `data/daily` → 同样 39通过/4失败 exit=1、4 条失败断言逐字相同(证据包① baseline-d667a4e_test_p4_fixes_with_real_data.log);②零导入关系——test_p4_fixes.py/monthly_review.py grep 本包模块名零命中;③环境分叉根因——`git ls-files data/daily`=0(采集档不入 git),本机存在真实数据走真数据分支(月度序列提取 0),CI 无数据走合成 fixture 分支(G3 tip CI 59/59 绿为证)。B5 先例(cdbb311)已登记同一现象。不越权修复(越 P4 域+越白名单)。
4. **env_config.py 既有回退路径(白名单外发现,不代改)**: env_config.py:28-29 自带本机回退(~/investment-agent 等);本模块按 DP-4(a) 仅环境变量取凭证、零本机回退(§二.2),该既有文件缺陷登记不实施(合同 §八.10)。
5. **原始响应正文不留档(设计使然,如实披露)**: 3 次真实出站的模型原始文本仅在进程内存消费(G2 逐次解析/校验),不落盘;落档证据=逐次 usage 日志+G2 trace 反馈链(逐次失败原因全文)+终态报告。补强需改实现(白名单内可另包),本包如实披露。
6. **CI run ID 缺席(合同步骤15 承接)**: 本包不自行 dispatch workflow;CI 登记件由操作者/opd 落 `rounds/029/GLM-WP-G4-CI-dispatch-evidence.md`,stdout 自述引用其将落路径。
7. **补证据轮第 4 次尝试阻断(2026-11-05T02:45:52Z~02:48:27Z,如实,非 FAIL 项)**: 操作者补证据轮追加指令(2026-11-05 10:5x)要求以冻结参数原样经既有 run_live_conclusion 冒烟管线新登记一次真实尝试;本执行会话 4 次发起均被工具权限层拒绝于命令执行前(含显式非沙箱批准形式,零批准通道应答),**零真实出站**;上轮同调用面(G4-CRED-001,01:59Z)真实出站成功,判定为本轮会话执行环境权限配置变更所致。零出站佐证与处置见要点①(d)行+REGISTRY §五+证据包⑥ 阻断记录;按「恰 1 次不追加」停止;代码/测试/参数/熔断/模板零改动;处置权操作者(择时重发/代执行)。
8. **补证据轮第 4 次尝试·操作者代执行结果=ABSENT_REGISTERED(2026-11-05T03:26:33Z,如实,非 FAIL 项)**: 二复审处方(2026-11-05 11:1x HKT)「操作者择时重发第 4 次尝试或代执行,同 CI dispatch 先例」+处置§五「恰 1 次」;先登记(G4-CRED-003,git cf7c75c,03:24:43Z)后出站(03:26:33Z);1 次真实出站传输层成功(34.3s/$0.0220),模型输出仍未过 G2 校验器(径2义务+接地[0.3,25.0]),终裁 ABSENT_REGISTERED 如实;RETRY_BUDGET 运行时置 1(进程内,模块文件零改动),模型面冻结参数分文未动;累计出站 4 次/$0.0887,熔断未触发;**处置§五预置分支生效: 第 4 次未 ACCEPTED→§二兜底终态(接受 (c) 如实缺席定稿,操作者处置留痕在档)**;详见要点①(e)行+REGISTRY §六+证据包⑥。

---

## §六 提交前数值标注六项自检清单(§5.3 强制;副本入证据包⑦)

| # | 检查项 | 结论 |
|---|---|---|
| 1 | REPORT/DELIVERY 全数值标注 [实取]/[预计算誊写]/[示意] 三类口径 | 已逐值标注(§二.3 示意单价;§三 实取运行值;DELIVERY 同构);本表+双文档扫描件入证据包⑦ |
| 2 | 装配/映射/阈值/窗口类参数先登记后运行、运行后零回改 | §二.1/§二.2 登记在先(实现前),运行 echo(`--echo`)与常量与登记三方一致(T5 echo 用例断言);运行后未改任何参数(模块 sha256 提交前后一致) |
| 3 | 真实调用数值(次数/费用/时延/usage)与原始日志一致 | §三要点①表=$0.0667/3 次/26.9s/26.1s/19.7s/1949·2080·2063pt/1810·1932·1636ct,逐值与 `glm4_usage_log_20261104.jsonl` 三行一致(REGISTRY 同源誊写) |
| 4 | 测试预期值字面量硬编码、不从被测模块导入计算 | tests 硬编码 VAL_TIPS=1.87/VAL_GOLD=3912.5/FROZEN_CB 族/费用 0.021·0.022·0.02 等,零 `from glm_conclusion_client import` 取值(源码 grep;fixture→预期值映射表入 DELIVERY §四) |
| 5 | 合成 fixture 与真实数据隔离 | fixture 全发明(T0 自检 4 用例: 值域/日期/缺席构造合法性);真实数据仅执行段快照路径经标准化层,测试零 data/daily 依赖(T5/T6 源码 grep 反证) |
| 6 | 计数类陈述(套件数/用例数/出站数)与可复核原始计数一致 | 48 用例(逐类计数 §三要点②)、61 条目本地 CI(summary 实取)、3 次出站(usage log 行数=REGISTRY 登记=报告 attempts_used) |

### §6.7 补证据轮数值标注追加(2026-11-05T02:4x~03:xxZ;沿六项纪律)

| 数值 | 口径 |
|---|---|
| 4 次发起 [实取·来源: 本会话工具权限层 4 次拒绝输出,2026-11-05T02:45:52Z~02:48:27Z] | 发起次数≠出站次数;零到达执行层 |
| 0 次出站 [实取·来源: usage log 仍 3 行+锚定 34/34 不变+无新 smoke 报告,post-run 复核 02:48:27Z] | REGISTRY G4-CRED-002 出站次数列=0/3 同源 |
| $0.0000/$0.0667 [实取·来源: 上轮 usage log 三行费用合计 0.022137+0.023628+0.020913=0.066678,本轮零新增] | 跨执行段历史累计不变 |
| 34 文件锚定(24 daily+10 research) [实取·来源: anchors/pre-run-sha256-round2.txt 全文+post-run-check-round2.txt] | 本轮 data/research 既有 10=上轮终态(3 既有+7 上轮产物) |
| GLM_API_KEY len=49 [实取·来源: 存在性检查 2026-11-05T02:44Z,值零打印] | 仅存在性,无值落盘 |
| 证据包 v2 成员数/zip sha256 [实取·来源: 装配后 sha256 命令输出,登记于 DELIVERY §二 v2 行+sidecar] | 装配后回填 |
