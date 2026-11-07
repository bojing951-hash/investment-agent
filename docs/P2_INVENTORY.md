# P2 深研能力盘点(INVENTORY)

> 包: R020 · IA-P2-DESIGN(P2 深研能力 · 设计线第1包,docs-only)
> 基线: `f1fe593faa0f1754e6a6ab14c39f39fc0848550a`(dev/p03-e2eb-design 尖端,开工时 `git ls-remote` 实取一致)
> 盘点分支: `dev/p2-design`(自基线切出)
> 盘点时点: 2026-11-02(UTC) · 全部行级引用以本 checkout 实码为准,实测方法逐处注明
> 用途: 为 P2「多轮竞争性假设深化研究模式」的设计提供**事实层依据**;已知缺口清单供 DESIGN 承接

---

## 数值标注约定(全文适用,二选一)

- **[实取·来源: 文件:行号 或 实测命令,2026-11-02]** = 直接读自本 checkout 真实文件或本包实测命令所得;
- **[示意·非实取]** = 非实取示例/设计提案值;
- 跨支值(引自 dev/p1-design / dev/p03-w2-glm-design 等另支)一律标 **[示意·非实取·跨支登记 分支@SHA]**,不在本工作树复核;
- 注入引擎提示词的内容一律标「注入摘要(2026-11-02 深夜),非工作树实读」;
- 日期/SHA/版本字符串(如 registry `2.0.0`)/结构编号(如 G-01)/档键成分按合同 AC-03 边界出圈,不强制标注(DESIGN 头部另有声明)。

---

## 面(a) 研究基础设施现状(逐项: 载体(文件:行号)或「不存在」)

P2 深研复用的五项基础设施(五面定义 [实取·注入合同 AC-01(a),2026-11-02,注入摘要]),**五项全部在场**,逐项登记如下:

### a.1 研究快照 — 在场

| 载体 | 位置 | 说明 |
|---|---|---|
| 构建 | `scripts/snapshot_builder.py` L236-438(`build_snapshot` 签名 L236-237) | 唯一快照构建入口;as_of 可注入确定性研究截止 |
| 输入解析 | `scripts/snapshot_builder.py` L47-101(`resolve_inputs`) | 采集文件精确匹配→新鲜度窗 fallback 显式披露 |
| 不可变语义 | `scripts/snapshot_builder.py` L14(文件头声明)、L390-398 | 同日已存在拒绝覆盖;`--allow-revision`→`_v2` 修订版+`revision_reason` 留档 |
| 快照含 gate_a | `scripts/snapshot_builder.py` L354(快照 dict `gate_a` 键) | Gate A 状态随快照落盘 |
| 读取/选择 | `scripts/research_provenance.py` L1243(`select_snapshot`) | 确定性版本选择(同日多版取最高修订版) |
| 内容指纹 | `scripts/research_provenance.py` L1297(`digest_snapshot`) | sha256 前16位(16 字符截断 [实取·`scripts/research_provenance.py` L1297-1301 实现,2026-11-02]),档案绑定用 |
| 离线构建能力 | `tests/test_snapshot.py`(在场,`ls` 实测 2026-11-02) | write=False 快照构建可测 |
| DEV 数据档现状 | `data/daily/` 共 12 个文件(8 JSON + 4 人读 md;global/macro/china/rate_economy 4 通道×2 日 20261101/20261102)[实取·`ls` 清点,2026-11-02] | **无任何已持久化 `research_snapshot_*.json`**(沿 E2E-B INVENTORY G-05 登记口径,本包 `ls` 复核一致) |

### a.2 Gate A — 在场

| 载体 | 位置 | 说明 |
|---|---|---|
| 写入时重算 | `scripts/snapshot_builder.py` L313-342(gate_a 自事实构建) | 快照声明与事实不可矛盾 |
| 权威复算 | `scripts/research_provenance.py` L853(`recompute_gate_a`) | 从事实重算 Gate A |
| 下游复算 | `scripts/research_provenance.py` L1101(`gate_status`) | 与写入时同源口径 |
| 放行判定 | `scripts/research_provenance.py` L1183-1188(`gate_allows_formal_research`) | PASS/DEGRADED 放行正式研究,FAIL/None 拒绝 |
| 消费点1 | `scripts/data_assembler.py` L309-354(`main`,Gate A 检查拒 FAIL 生成) | 数据包装配前 |
| 消费点2 | `scripts/report_generator.py` L612-626(`verify_research_inputs` 第1件) | 报告生成前置(调 GLM 之前) |

### a.3 装配层 — 在场

| 载体 | 位置 | 说明 |
|---|---|---|
| 数据包渲染 | `scripts/data_assembler.py` L123-306(`build_markdown`) | 快照→GLM 数据包,程序确定性生成 |
| meta 绑定 | `scripts/data_assembler.py` L15(文件头)、L335-346(`write_meta`,`pack_digest` L346) | 包↔快照 digest 绑定,旧包/混版自动失配 |
| 评分 | `scripts/macro_scorecard.py` L30(`DATA_INSUFFICIENT`)、L31(`MIN_AVAILABLE_PER_DIM=2` 每维度至少 2 个可用指标)[实取·本文件,2026-11-02] | 缺失≠0 分,数据不足不可判 |
| 相关性 | `scripts/correlation_calculator.py` L28-46(`PAIRS` 常量,恰 10 对 [实取·`python3 -c "import correlation_calculator as cc; len(cc.PAIRS)"` = 10,2026-11-02])、L83(`compute_all`) | 固定配对(计数见位置列),无按需配对面;序列缺失→missing 披露不内插 |
| 流水线编排 | `run_weekly.py` L64(`run_pipeline`) | 关键步骤失败→流水线失败;非关键降级运行 |

### a.4 Gate B — 在场

| 载体 | 位置 | 说明 |
|---|---|---|
| 校验分级 | `scripts/data_validator.py` L372-377(分级注释)、L378-388(`classify_result`) | PASS/DEGRADED/FAIL;**FAIL→禁止一切长期状态回写(thesis/allocation/prediction)**(L374) |
| 报告校验 | `scripts/report_generator.py` L1243(`validate_generated_report`) | 生成报告数值核验 |
| 前置核验四件套(4 件核验项 [实取·`scripts/report_generator.py` L612-626 docstring 枚举,2026-11-02]) | `scripts/report_generator.py` L612-626(`verify_research_inputs`: 当日快照+Gate A / 数据包+meta / 锚点 / 锚点 prompt,缺一即拒,不调 GLM) | 报告生成前置纪律 |
| 状态落盘 | `scripts/report_generator.py` L803(`write_report_status`) | 报告状态记录 |
| A×B 合成 | `scripts/research_provenance.py` L1533(`combine_gates`) | 两门合成口径 |

### a.5 论点·观点·预测状态保护 — 在场

| 对象 | 载体 | 位置 | 关键机制 |
|---|---|---|---|
| 论点 | `config/thesis.json`(9 条: 进行中 6 / 待观察 3)[实取·`python3 json.load` 计数,2026-11-02] | 状态块模板 `scripts/report_generator.py` L496-499;状态枚举恰 4 值(进行中/待观察/已验证/已失效)L501 [实取·L501,2026-11-02] | 终态进入门禁 L503(须触发器被引擎核验或 ≥2 项新增独立支持证据 [实取·L503,2026-11-02]);终态退出门禁 L504;确信度门禁 L505(上调不得超过程序验证星级) |
| 观点 | `config/allocation_views.json`(9 条 views + 2 条 predictions: not_yet_triggered 1 / observing 1)[实取·同上计数,2026-11-02] | 状态块 L511-514;评级枚举恰 4 值(超配/标配/低配/观望)L516 [实取·L516,2026-11-02] | 评级变更门禁 L522(引擎核验触发器或 ≥2 项新增验证证据 [实取·L522]);证据分级 v2: 机制族 7 类(增长/通胀/利率与流动性/信用/避险与估值/供应与库存/资金流)L518、星级门槛 1★=1 项/2★=2 项/3★=3 项且 2 类机制/4★=4 项且 3 类机制且跨 2 观察期/5★=5 项且 3 类机制且跨 3 观察期、未解释反证封顶 3★ L521 [实取·L518/L521,2026-11-02] |
| 预测 | 观点库 predictions + 每日观察 | 裁决状态块 L530-534(裁决枚举 4 值: hit/miss/inconclusive/not_yet_triggered [实取·L534,2026-11-02]);五态口径(未触发/观察中/已命中/已证伪/无法裁决,恰 5 态)`scripts/allocation_engine.py` L1066、状态映射 L74 [实取·本文件,2026-11-02] | 机器可校验规格 `pred_metric/pred_op/pred_target/pred_mode(expiry|touch)/pred_premise_*` `scripts/report_generator.py` L525-526 [实取·本文件,2026-11-02];每日观察记录 `scripts/daily_prediction_observer.py` L124(`record_observations`,终态预测不参与,模块头 L2 起) |

### a.6 (追加登记)GLM 报告层调用链 — 在场(P2 §5 衔接对象,能力级)

| 载体 | 位置 | 说明 |
|---|---|---|
| 调用 | `scripts/report_generator.py` L574-605(`_call_glm`,流式;temperature=0.3 L593;reasoning_effort=low L594;连续 3 次失败放弃 L570 [实取·L570,2026-11-02]) | v4 OpenAI 兼容通道 |
| 凭证机制 | `env_config.py` L14-26(环境变量优先;本机回退路径 L19-24 **只登记不触碰**)、L28-29(BASE_URL/MODEL) | 全部环境变量读取不落盘(L3 注释) |
| 周报入口 | `scripts/report_generator.py` L1328(`generate_weekly_report`,经 verify_research_inputs 前置) | 消费数据包+锚点 |
| 冒烟测试 | `tests/test_glm_live.py`(在场,CI 显式排除) | 真实 GLM 验收套件不进 CI [实取·`.github/workflows/offline-tests.yml` L40-41,2026-11-02] |

**面(a)小结**: 五项基础设施(快照/Gate A/装配/Gate B/状态保护,面定义 5 项 [实取·注入合同 AC-01(a),2026-11-02,注入摘要])载体齐备且行为级在场;深研可直接复用的机制 = 快照绑定(select_snapshot+digest)、门禁放行(gate_allows_formal_research/Gate B 分级)、状态保护门禁(终态/评级/确信度 3 重 [实取·本面 a.5 登记计数,2026-11-02])、机器可校验预测规格(规格字段集 [实取·`scripts/report_generator.py` L525-526,2026-11-02])、证据分级 v2(机制族 7 类+星级门槛 [实取·L518/L521,2026-11-02])。**不存在项**: 研究任务管理器/异常检测器/研究历史查询三模块(E2E-A)零代码在场(见 b 与 P2-G-01/02);事件序列结构化日历零在场(见 P2-G-04)。

---

## 面(b) 研究闭环设计在场件

### b.1 E2E-B 设计三件(基线自带,本 checkout `docs/` 实读定位)

| 文件 | 行数 | 用途(逐件) |
|---|---|---|
| `docs/P03_E2EB_QUERY_SURFACE_INVENTORY.md` | 184 行 [实取·`wc -l`,2026-11-02] | 查询面五层入口盘点(fact_engine E1-E17 共 17 项 [实取·该文件 §一层①登记,2026-11-02]/registry 81 指标 [实取·本包面(c.1) 双通道复核,2026-11-02]/快照 S1-S5+R1-R7/data 通道 4 个 [实取·`scripts/research_provenance.py` L152-157 枚举,2026-11-02]/装配 A1-A5·M1-M7·C1-C6),已知缺口 G-01~G-08 共 8 项 [实取·该文件 §二清点,2026-11-02]——P2 复用其行级锚点与缺口登记 |
| `docs/P03_E2EB_DESIGN.md` | 253 行 [实取·`wc -l`,2026-11-02] | 模式B NL→查询映射架构: IR 字段级 schema/缺席路径 4 级 [实取·E2E-B DESIGN §三(c) 层级登记,2026-11-02]/接地规则/E2E-A 对齐表 8 要素 [实取·E2E-B DESIGN §四表 8 行,2026-11-02]/共享档案 ID 约定(QB-/RT-/origin_query_id/snapshot_id+digest)/工作包 WP-B1~B5——P2 任务发起(模式B升级路径)与档案衔接的直接上游设计 |
| `docs/P03_E2EB_DELIVERY.md` | 52 行 [实取·`wc -l`,2026-11-02] | 交付说明与证据指针(含 CI 同构 53/53 记录、环境差异如实声明)——本包交付纪律沿其先例 |

### b.2 E2E-A(实现包停泊;引用一律注入摘要)

三模块 = 研究历史查询(只读对齐,禁直读原始档)/ 异常检测器(参数 echo=常量=登记三者一致)/ 研究任务管理器(schema 最低字段集**含 falsifiable_conditions**,**append-only**);回放纪律 = 真实历史双次运行;零网络 [注入摘要(2026-11-02 深夜),非工作树实读]。
**本 checkout 实读复核**: `research_task_manager` / `anomaly_detector` / `research_history_query` 三个模块名于 `scripts/` 与 `tests/` 零命中,仅出现于上述 E2E-B 两件设计文档内 [实取·全仓 grep,2026-11-02]——E2E-A 代码零在场,与注入「实现包 R011 停泊未执行」一致。

### b.3 GLM 研究结论层(R019,在途;仅登记,不作冻结事实)

见面(d)。

---

## 面(c) 数据面可得性

### c.1 registry / fact_engine 实读

- `config/metric_registry.json`: **实测指标总数 = 81** [实取·`python3 -c "len(json.load(...)['metrics'])"` = 81,且全文 `"metric_id"` 出现次数 = 81 双通道计数,2026-11-02];构成 active 80 + deprecated 1;criticality 分布 core 32 / important 48 / context 1 [实取·同命令 Counter 计数,2026-11-02]。
- `scripts/fact_engine.py`(751 行 [实取·E2E-B INVENTORY §一层①登记,本包沿用]): 统一收益引擎 `compute_period_returns` L81-174(week/mtd/ytd/m1/m3/m6/m12 口径窗口 7 个 [实取·`scripts/fact_engine.py` L81-174 词表枚举,2026-11-02];**数据不足→`{"available": False}`,绝不回退 0.0**,L90/L94-95 本包抽读复核一致 [实取·本文件,2026-11-02]);查询入口 E1-E17 共 17 项行级登记见 E2E-B INVENTORY §一层①(17 项 [实取·该文件 §一层①登记,本包抽查 L90/L94-95 一致,2026-11-02])。
- 快照内序列研究载体: `series_store`(键=注册表 metric_id)机制在场(E2E-B INVENTORY 层③登记);global 通道 USDJPY 实测 260 观测序列(close=157.8 @2026-10-30)[实取·`python3 json.load data/daily/global_20261102.json` 计数,2026-11-02]。
- data/daily 现状: 12 个文件(8 JSON + 4 md,4 通道×2 日)[实取·`ls`,2026-11-02];通道规范与回退窗 `SOURCE_FILE_RULES`(global 5 日/macro 7 日/china 5 日/rate_economy 7 日)`scripts/research_provenance.py` L152-157 [实取·本文件,2026-11-02]。

### c.2 P1 数据需求(跨支登记;另支,非工作树在场)

- 分支 `dev/p1-design` @ `049ec978523dec659ba47f140bf41669604de24f`(本包 `git ls-remote` 实取 2026-11-02,与注入登记一致): 三件 = `docs/P1_DATA_NEEDS_INVENTORY.md` / `docs/P1_DESIGN.md` / `docs/P1_DELIVERY.md` [实取·`git fetch` 后 `git ls-tree FETCH_HEAD docs/` 只读取证,2026-11-02]。
- 关键事实(跨支登记,本工作树不复核): 12 条候选指标条目(BOJ_POLICY_RATE / JGB_10Y / JGB_2Y / JP_CPI_TOKYO_YOY / NIKKEI225 / ECB_DFR / ECB_MRO / BUND_10Y / BUND_2Y / EA_HICP_YOY / DAX / CAC40)[示意·非实取·跨支登记 dev/p1-design@049ec978523dec659ba47f140bf41669604de24f P1_DESIGN.md L62 候选清单,该支自标「示意·候选」];现行 81 [实取·本树 c.1]+12 候选 [示意·跨支登记]=93 目标 [注入摘要(2026-11-02 深夜),非工作树实读;合成口径,81 为本树实取、12 为另支候选];实现包序列 WP-P1-A..E 共 5 包 [示意·非实取·跨支登记同支 P1_DESIGN.md L169 起]。
- 深研相关性: P1 落地后 JP/EA 本币序列补全,深研跨经济体假设的证据面扩大;P2 设计不依赖 P1 落地(缺席走结构化 NO_DATA 路径,沿 E2E-B 缺席路径 4 级设计 [实取·E2E-B DESIGN §三(c) 层级登记,2026-11-02])。

### c.3 深研直接相关的数据缺席(实测)

- **事件序列结构化日历(议息/发布/政策事件)零在场**: `FOMC`/`议息` 字样仅见于 registry 说明字段(`calc`/`notes`,L1769/L1794/L1833/L2284)与 P0-2-W2 政策修复文档语境,无任何结构化事件日历数据档或注册实体 [实取·全仓 grep + 逐处定位,2026-11-02]。
- 按需相关性配对面缺席: PAIRS 固定 10 对 [实取·本包 `python3 -c "import correlation_calculator as cc; len(cc.PAIRS)"` 复测=10,2026-11-02],无按需配对入口(沿 E2E-B INVENTORY G-04 登记)。

---

## 面(d) GLM 研究结论层现状(ls-remote 实况)

- `git ls-remote origin dev/p03-w2-glm-design` → `0c8de3c3bece78dd2d9f0d8928a817b597e3104e` [实取·`git ls-remote`,2026-11-02T13:27Z]。
- 该尖端为 docs-only 恰 3 文件(`docs/P03_W2_GLM_INVENTORY.md` / `P03_W2_GLM_DESIGN.md` / `P03_W2_GLM_DELIVERY.md`,+448 行)[实取·`git show <SHA> --stat` 只读取证(本地对象),2026-11-02]。
- **状态标注**: 另支在途;其定稿状态以引擎注入快照时刻为准 [注入摘要(2026-11-02 深夜),非工作树实读——注入时刻状态=执行段在途,可能已定稿也可能未落]。**纪律**: 该支内部 schema(如假设集字段结构)一律不得表述为冻结事实;本包仅引用到能力级(输入契约/调用面/输出契约/≥2 竞争假设/falsifiable+GateB 对接/模式A·B差异),并显式标注「待其定稿,实现包阶段对齐」。
- 本树在场的能力级依据(可独立复核): GLM 调用链/凭证环境变量机制/报告前置核验,见面(a.6)。

---

## 面(e) 深研相关外部约束(治理登记)

| 约束 | 内容 | 依据 |
|---|---|---|
| 上游依赖漂移常态化 | dateutil 4.0.0 事件先例(上游 minor 漂移破坏日期语义) | [注入摘要(2026-11-02 深夜),非工作树实读];本树锚点: `requirements.txt` L11 `python-dateutil>=2.8.2` [实取·本文件,2026-11-02] |
| 免费数据源边界(预授权③) | 免费公开数据源直用;付费/凭证类须报批 | [注入摘要(2026-11-02 深夜),非工作树实读];本包零付费零凭证涉及 |
| 既有免费源在场面 | news 通道: Finnhub(市场+个股新闻)+ RSS(CNBC/Bloomberg) | `scripts/news_collector.py` L3(数据源声明)、L61-66(`RSS_FEEDS`)、L177(`fetch_rss_news`)[实取·本文件,2026-11-02];新闻溯源 `scripts/news_provenance.py` 在场(`ls` 实测) |
| 凭证纪律 | 全部 API key 环境变量读取不落盘;仓库内零明文凭证(开源版已移除原作者 key) | `env_config.py` L3 注释、L9-11 [实取·本文件,2026-11-02] |
| CI 基准 | offline-tests 工作流逐套件运行 `tests/test_*.py`(排除 test_glm_live);套件数基准 = 53 [实取·注入合同登记值;本地清点 54 个 test 文件 − 排除 1 = 53,`ls tests/test_*.py \| wc -l` = 54,2026-11-02] | `.github/workflows/offline-tests.yml` L38-57 [实取·本文件,2026-11-02] |
| 治理边界 | 冻结合同不得为 PASS 修改;证据分级 C/T/E/I/D/U;阻断下拒绝编造、如实标 U 附证据 | [注入摘要(2026-11-02 深夜),非工作树实读] |
| 战略冻结 | 禁交易/禁管理真实仓位/禁承诺收益——P2 设计任何处不得出现交易/仓位/收益承诺类功能 | [注入摘要(2026-11-02 深夜),非工作树实读] |

---

## 已知缺口(P2 视角;编号 P2-G-*,供 DESIGN §七承接)

| 编号 | 缺口 | 实测依据 | 与既有登记的关系 |
|---|---|---|---|
| P2-G-01 | 无深研任务/假设记录载体(append-only 任务档、假设集登记) | 面(b.2) E2E-A 三模块零代码在场 | 沿 E2E-B INVENTORY G-06 同源 |
| P2-G-02 | 无异常检测器(模式A异常升级发起点断源) | 同上 | 沿 G-06 |
| P2-G-03 | 无共享研究档案存储(query_history/research_tasks/anomaly_events 集合) | E2E-B DESIGN §4.1 仅设计无实现 | 承接 E2E-B GAP-06 |
| P2-G-04 | 事件序列结构化日历零在场(议息/发布日) | 面(c.3) 实测 | 新登记 |
| P2-G-05 | 相关性固定 10 对 [实取·面(a.3) import 实测,2026-11-02],无按需配对计算面 | 面(a.3)/面(c.3) 实测 | 沿 E2E-B G-04/GAP-04 |
| P2-G-06 | DEV 侧无持久化快照(测试需 write=False 离线构建) | 面(a.1) 实测 | 沿 E2E-B G-05/GAP-05 |
| P2-G-07 | falsifiable 条件的机器评估机制**绑定于观点预测库**(规格/自动裁决在场但无深研假设侧入口) | 面(a.5) 实测: 规格 L525-526 与五态裁决在场,消费方仅 allocation_views.json predictions | 新登记(评估机制可复用、假设侧缺席) |
| P2-G-08 | GLM 结论层在途,深研综合接口待其定稿 | 面(d) | 能力级衔接,不构成硬依赖 |

---

## 跨分支登记(只读;ls-remote 实取 2026-11-02)

| 分支 | 尖端全SHA | 内容 | 引用边界 |
|---|---|---|---|
| `dev/p1-design` | `049ec978523dec659ba47f140bf41669604de24f` | P1 三件(3 件 [实取·面(c.2) ls-tree 取证,2026-11-02];数据需求/设计/交付)+WP-P1-A..E | 另支,非工作树在场;数值只作跨支登记 |
| `dev/p03-w2-glm-design` | `0c8de3c3bece78dd2d9f0d8928a817b597e3104e` | GLM 结论层三件(3 件 [实取·面(d) git show --stat 取证,2026-11-02];docs-only) | 另支在途;不作冻结事实 |
| `dev/data-inventory` | `7cbef4c9bd25586ef03fc02819ae6792d0929fa0` | data/daily 三元组哈希对照工具 | 沿 E2E-B INVENTORY §三登记,本包 ls-remote 复核在场 |
| `dev/data-coverage` | `06f715b6be34dedd69f6776b1947238708de0563` | registry 覆盖审计工具 | 同上 |

---

*本盘点为设计输入事实层;判断与方案见 `docs/P2_DESIGN.md`;交付说明见 `docs/P2_DELIVERY.md`。*
