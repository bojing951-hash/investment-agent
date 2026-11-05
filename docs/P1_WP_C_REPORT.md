# IA-P1-WP-C 实现报告

- 工作包: IA-P1-WP-C（P1 四经济体底图层 第3实现包：经济体评分·装配·报告）
- 契约: IA-P1-WP-C-AC-v1.1（FROZEN，随开工提示词实物化，冻结章值见 §零.1）
- 分支: dev/p1-impl-c（自 BASE-P1C=fcd0537c9ac4b66dcd8a52c6186e814121feaf5f 切建）
- 报告地位: 本文件为 A类交付件之一。§零 为开工前登记节（先登记后实现），登记后为本包白名单与事实基线；§一 及以后为实现与运行实录。登记节中的预期值与实测值的差异按"如实优先"在 §二 披露，登记原文不回改。
- 整改续作注记（v1.2）: 2026-11-06 处置章·v1.2（单行授权勘正，操作者）续作=第4笔整改笔+第5笔 zip 终笔；v1.1 执行段（3 笔）原文一律保留，续作登记=§零.9 处置回填/§二 偏离1 闭环注/§三.1 重跑实录/§六 行13-14。

---

## §零 开工登记（步骤0–6）

### §零.1 契约锚与启动核验实录

| 步骤 | 命令/来源 | 实测结果 | 判定 |
|---|---|---|---|
| 0 时序自检 | `git log -1 --date=iso-strict --format='%H %cI'`（main） | fcd0537c9ac4b66dcd8a52c6186e814121feaf5f, 2026-11-05T18:33:56+08:00 | 通过：系统时间(2026-11-06)晚于契约冻结时点，时序合理 |
| 1 占位符核验 | 提示词冻结章 | BASE-P1C=fcd0537c…、CI=71、BRANCH-SET=43 分支均已实物化，无未替换占位符 | 通过 |
| 2 前置实取 | `git ls-remote origin` | origin/main 尖端=fcd0537c…（与冻结章一致），dev/p1-impl-a、dev/p1-impl-b 在列，dev/p1-impl-c 不存在 | 通过：远端可达、分支可新建、无重名冲突 |
| 3 切建分支 | `git checkout -b dev/p1-impl-c fcd0537c…` | 新分支创建于 fcd0537c，工作区净 | 通过 |
| 4 设计在场核验 | `git cat-file -e 049ec978^{blob}`；`git rev-parse origin/main:P1_DESIGN.md` 等 | ~~049ec978 为有效 blob~~（**取证勘正：失实——实测 `git cat-file -t 049ec978`=commit，即设计分支尖端提交（全值 049ec978523dec659ba47f140bf41669604de24f），非 blob；设计三件在该提交的 blob=13b263cf…/df79c06f…/314c2644…（ls-tree 实取），更正全记录见 §零.12**）；main:docs/P1_DESIGN.md 与 main:P1_DESIGN.md 两 blob 全等（同 blob id）；工作区三文件与 main 版本零差异（`git diff origin/main -- docs/P1_DESIGN.md scripts/macro_scorecard.py scripts/data_assembler.py scripts/correlation_calculator.py scripts/report_generator.py config/metric_registry.json` 输出为空） | 通过：设计文件在场且未被上游改动（"在场"结论经 §零.12 正确命令复核成立；仅对象类型表述失实） |
| 5 规格抄录 | ~~`git show 049ec978 | sed -n '171p'`~~（**取证勘正：该命令实测输出仅 55 行（commit 元数据+diff），`sed -n '171p'` 取到空行——抄录实际来源命令为 `git show 049ec978:docs/P1_DESIGN.md | sed -n '171p'`（182 行文件，见 §零.12）**） | 与本报告 §零.2 逐字块一致（含行首行尾）（经正确命令复核仍一致） | 通过 |

补充实录（同批执行）：

- 本地 main 与 origin/main 一致（`git rev-parse main origin/main` 同值 fcd0537c…）。
- `git ls-remote` 返回分支数=43（含 HEAD），与冻结章 BRANCH-SET=43 一致；本包分支 dev/p1-impl-c 为新增第 44 个引用（本地），完成后推送。
- 契约文本来源：开工提示词附录A（contracts/ 目录在 DEV 仓库不存在，为主 Agent 侧工程产物；契约有效性以提示词冻结章实物化为准，未触发停止条件）。

### §零.2 规格抄录（P1_DESIGN.md §六 L171，~~blob 049ec978~~ →取证勘正：设计提交 049ec978（其内 docs/P1_DESIGN.md blob=13b263cf3139d420e01bf1e154b03ce85a35db4c），见 §零.12）

以下为 ~~`git show 049ec978` 第 171 行~~（取证勘正：实为 `git show 049ec978:docs/P1_DESIGN.md` 第 171 行，见 §零.12）逐字抄录（一字不改、含原始域分隔与全角标点；用 §零.2 结尾的逐字节核验说明自律）：

```
| WP-P1-C 经济体评分·装配·报告 | 评分/数据包/报告经济体化 | scorecard economy 参数化(DP-3)、数据包经济体节、相关性新对、报告模板与 Gate B 锚点 | WP-B | ① 维度扩展单测+DATA_INSUFFICIENT 负向【测试】② 数据包经济体节渲染快照测试【测试】③ Gate B 对新锚点全量核验用例【测试/CI】 |```

四要素拆解：

| 要素 | 抄录内容 | 落点登记 |
|---|---|---|
| 工作内容 | 评分/数据包/报告经济体化 | M类a/b/c/d 四触面（§零.3） |
| 技术要点 | scorecard economy 参数化(DP-3)、数据包经济体节、相关性新对、报告模板与 Gate B 锚点 | §零.6 实现参数预登记逐项对应 |
| 前置 | WP-B | BASE-P1C=fcd0537c 已含 WP-B 合并（merge commit msg 注明 WP-P1-B），前置满足 |
| 验收要点 | ① 维度扩展单测+DATA_INSUFFICIENT 负向【测试】② 数据包经济体节渲染快照测试【测试】③ Gate B 对新锚点全量核验用例【测试/CI】 | t01–t04/t06（①）；t07–t08（②）；t09–t10（③）—— §零.7 |

规格关联行（同 blob=13b263cf…，抄录依据；原登记"同 blob"指代经 §零.12 勘正后语义=同一设计提交内的同一文件版本）：

- L30（DP-3 登记）：倾向①=macro_scorecard 维度函数参数化 economy，复用 score_growth/score_inflation 与 DATA_INSUFFICIENT 机制；最终由 WP-P1-C 实现包定。
- L68（§三a-5 触面清单）：build_markdown 新增「经济体观察」节（渲染复用 _rows/_fv）；macro_scorecard 维度函数 economy 参数化；compute_all 增新对（候选 NIKKEI225×USDJPY、DAX×EURUSD）；报告模板经济体章节；Gate B 锚点自动覆盖新 metric_id（锚点=build_anchors 按快照事实生成，零改动）。
- L128（§四 L5 说明）：generate_report prompt 输入=数据包新节自动进入——报告模板零改动的依据。
- L175（§六红线筛查行）与 L177–L183（§七四红线）：见 §零.4。

逐字节核验说明：本节逐字块与 ~~`git show 049ec978` 第171行~~（取证勘正：`git show 049ec978:docs/P1_DESIGN.md` 第171行，见 §零.12）经字节级比对一致（无全角逗号替换、无空格增删）。判定权属审计角色。

### §零.3 交付清单（自 §零.2 拆解；登记后即本包白名单实体）

A类（纯新增，3件）：

| # | 文件 | 依据 |
|---|---|---|
| A1 | docs/P1_WP_C_REPORT.md（本文件） | 契约§零 A类 |
| A2 | docs/P1_WP_C_DELIVERY.md | 契约§零 A类 |
| A3 | tests/test_p1_wp_c.py | 契约§零 A类；验收要点①②③ 的测试承载体 |

M类（既有文件授权触面，4件；超此清单的既有文件改动=违约）：

| # | 文件 | 触面 | 依据 |
|---|---|---|---|
| M-a | scripts/macro_scorecard.py | 维度函数 economy 参数化（DP-3）、装配/存档/渲染穿线 | 抄录"scorecard economy 参数化(DP-3)" |
| M-b | scripts/data_assembler.py | build_markdown 新增「经济体观察」节（渲染复用 _rows/_fv） | 抄录"数据包经济体节" |
| M-c | scripts/correlation_calculator.py | PAIRS 追加两新对（NIKKEI225×USDJPY、DAX×EURUSD） | 抄录"相关性新对"+L68 候选 |
| M-d | scripts/report_generator.py | 条件类：报告模板经济体章节。经核 generate_report 的 user_prompt 以 `{data_pack}` 原文内嵌（模板字符串数据包节自动进入 prompt），且 5.1–5.8 资产分节+ALLOCATION_STATUS 九行契约由数据包与解析器绑定，均非本包数据包节新增的受影响面 → 预判零改动（判定依据登记于 §零.6-d；以测试 t13 固化该判定） | 抄录"报告模板与 Gate B 锚点"+L128+L68"Gate B 锚点自动覆盖（零改动）" |

白名单外零触碰（含但不限于）：scripts/snapshot_builder.py、scripts/data_validator.py、scripts/freshness_policy.py、scripts/global_market_collector.py、scripts/japan_market_collector.py、scripts/ea_market_collector.py、scripts/fact_engine.py、config/metric_registry.json、.github/workflows/*、tests/ 下既有 71 个测试文件、docs/ 下既有文件。

### §零.4 特有纪律登记（本包抄录行直接触发）

1. §六红线筛查（L175）：不引入新失败模式；不动 LIVE 运行面（launchd/plist/引擎目录零触碰）；引擎目录不可达=停止条件而非绕行理由。
2. §七四红线（L177–L183）：LIVE 禁写；零网络零调用零凭证（测试全部合成固定值，无网络、无 GLM 调用、无密钥）；白名单外禁改；main 禁操作（仅 dev/p1-impl-c）。
3. §三(c)4 事实回填面：本包零新增（新对所需的 NIKKEI225/DAX 序列与 jp/ea facts 接线属 WP-B 发现 F1/F2 已登记的延后项，非本包违约；依据登记于 §零.6-c）。
4. §三(a-2) L58 禁"0 占位"：DATA_INSUFFICIENT 不填 0，非 US 经济体维度得分如实登记缺失，不以 0 分或编造阈值充当。
5. 测试纪律（契约§四）：唯一数据源=tests/fixt.py 合成夹具；期望值全部硬编码字面量（来源=实现逻辑+设计阈值，标注[示意]）；禁自证（期望值不得取自被测函数运行时输出）；零网络；负向敏感度测试（注入真实缺陷验证测试变红）实录于 §一。
6. 证据纪律（契约§五）：原样取证、UTC 时间戳、完整 SHA、如实优先（宁可 FAIL 如实，不可 PASS 编造）。

### §零.5 DP 登记（DP-3 定值）

- DP-3（P1_DESIGN L30）：本包定值=形态①——macro_scorecard 维度函数参数化 economy。定值理由：设计已"倾向①"，且形态①完整复用 score_growth/score_inflation 与 DATA_INSUFFICIENT 机制，改动面最小、回归风险最低；无新证据支持偏离倾向。
- 落点（字段级）：score_growth/score_inflation 函数签名各增 economy 形参（默认 'US'）；US 路径行为零回归；非 US 路径如实缺失+DATA_INSUFFICIENT（依据 §零.4-4，US 专属指标对非 US 经济体计缺失，不杜撰阈值）。
- 非登记型 DP：无（本包不新增需用户确认的设计参数）。

### §零.6 实现参数预登记（先登记后实现；运行后禁回改）

(a) macro_scorecard.py（M-a）：

1. 维度函数签名：`score_growth(facts, economy='US')`、`score_inflation(facts, economy='US')`。US 分支=现逻辑逐字节等价（阈值/权重/缺失处理不变）；economy!='US' 时因 US 专属指标全部缺失且 <MIN_AVAILABLE_PER_DIM → 返回 DATA_INSUFFICIENT（逐指标 missing）。
2. main 增形参 `economy='US'`；装配调用穿线（facts 组装按现逻辑，本包不改 facts 来源）。
3. 存档文件名：US=`scorecard_{ymd}.json/.md`（零回归）；非 US=`economy_scorecard_{economy}_{ymd}.json/.md`。理由：data_assembler.scorecard_state 以 glob `daily/scorecard_*.md` 匹配 US 主评分卡，前缀 economy_scorecard_ 避免非 US 卡被误纳入 US 评分卡对账面；且 `_prev_distinct_week_file` 的日期切片 f[-13:-9] 对两种命名同构（均以 _YYYYMMDD.json 结尾），制度比较逻辑零改动。
4. 输出 JSON：US 结果保持现有 19 个 legacy 键原样（date/disclaimer/data_basis/growth_scores/growth_total/growth_missing/inflation_scores/inflation_total/inflation_missing/regime/regime_description/confirmed_regime/regime_status/max_confidence/pending_regime/regime_drivers/regime_counterfactuals/regime_switch_rule/sensitivity_note）；新增键 `economy`（值=经济体外参实值；仅当 economy!='US' 时写入该键，US 输出字节零回归）。渲染 markdown 标题：非 US 卡标题前缀「{经济体名} 」。（勘误注记·实现前：本条初稿误记"20 个 legacy 键"——逐键清点=19 个，于实现与运行发生之前勘正。）
5. 不改：阈值表、DATA_INSUFFICIENT 常量、regime 逻辑对 US 的行为；CLI 入口不变（无新命令行参数解析，economy 由调用方传参——保持既有 main(date_str, data_dir) 调用形态全兼容）。

(b) data_assembler.py（M-b）「经济体观察」节：

1. 位置：中国市场节之后、联邦基金期货节之前。
2. 范围：四个 DP-1 经济体 US/CN/JP/EA，排序 US,CN,JP,EA。
3. 形态：单表五列（经济体/增长/通胀/制度/数据状态）；制度与数据状态列取评分卡 JSON 存档——US=scorecard_{ymd}.json（主评分卡同源）、非 US=economy_scorecard_{economy}_{ymd}.json（运行时点存在才读，缺失如实标注「未生成」）；增长/通胀列取各评分卡 growth_total/inflation_total（None→「数据不足」，int→带符号整数；缺失文件→「未生成」）。表后披露行渲染快照级 sources_status 字段（快照顶层键，属已接线面；通道名：JP=japan+jp、EA=ea）。（勘误注记·实现前：本条初稿"快照 facts 的 sources_status 字段"表述不准——sources_status 为快照顶层字段而非 facts 内字段，于实现前勘正。）
4. 渲染复用 _rows/_fv（不新写渲染函数）；经济体节内不动既有其他节。
5. 缺席披露：表后按经济体逐行披露「未覆盖指标」（来源=config/metric_registry.json economy 字段 active 计数；计数基准=注册表枚举，非运行时数据，属静态披露）。

(c) correlation_calculator.py（M-c）：

1. PAIRS 末尾追加两对（既有 10 对顺序与字段不动）：
   - {"a": "NIKKEI225", "b": "USDJPY", "label": "日经225 vs 美元/日元", "disclosure": "跨域配对(IA-P1-WP-C新增): 日经225为日元计价股指,与USDJPY汇率同表仅示联动,描述统计非因果"}
   - {"a": "DAX", "b": "EURUSD", "label": "德国DAX vs 欧元/美元", "disclosure": "跨域配对(IA-P1-WP-C新增): DAX为欧元区股指,与EURUSD汇率同表仅示联动,描述统计非因果"}
   （勘误注记·实现前：本条初稿误记 id/group/left/right 字段名——correlation_calculator.PAIRS 实际 schema={a,b,label,disclosure(可选)}，且既有 10 对 label 均用"vs"分隔符；于任何代码改动与任何运行发生之前勘正登记，字段语义不变。§零.7 t11 的"五字段"同步按实际四字段(a/b/label/disclosure)断言。）
2. compute_all 数据驱动：真实运行时若快照 series_store 无 NIKKEI225/DAX 序列（WP-B F2：series_store 接线延后），该对如实输出 missing（标注"序列缺失"），非失败、非 0 值。测试用合成快照验证两新对全链路（配对收益→皮尔逊→markdown 渲染行）。
3. 不改：PAIRS 前 10 对、配对算法（公共观测日内连接、≥3 要求）、markdown 既有渲染。

(d) report_generator.py（M-d，条件类零改动判定）：

- 判定=零改动。依据链：①P1_DESIGN L128「generate_report prompt 输入=数据包新节自动进入」（prompt 模板以 {data_pack} 占位符内嵌整个数据包 markdown，经济体观察节随之进入 prompt，无需模板改动）；②generate_report/parse 解析面（5.1–5.8 资产分节、ALLOCATION_STATUS 九行契约）绑定的是资产配置面而非宏观经济体面，数据包新增经济体节不落在任何解析正则的受影响域；③L68 明示 Gate B 锚点零改动。以测试 t13（mock _call_glm 捕获 prompt）固化判定：prompt 文本含「经济体观察」节标题即证明自动进入。若实测否证 → 触发 §九(b) 停止条款（先停止后处置）。

(e) 既有调用面兼容性预登记：

- tests/test_e2e_orig14.py 链路以 `ms.main(date_str=ymd, data_dir=daily)` 形态调用 → economy 默认 'US'，行为零回归（既有 CI 全绿预期不变，总槽 72=71 exit0+1 SKIPPED）。
- tests/test_run_weekly_phase1.py 若直呼 score_growth/score_inflation（位置实参）→ 默认形参保位置兼容（economy 追加为最末形参，不插入中间）。

### §零.7 测试面登记（tests/test_p1_wp_c.py，unittest/standalone，与既有套件同构）

| # | 测试 | 验收要点对应 | 断言要点（期望值全部硬编码） |
|---|---|---|---|
| t01 | score_growth 非 US 如实缺失 | ① | economy='JP'/'EA' → DATA_INSUFFICIENT，growth_missing 含全部 US 专属指标，totals=None |
| t02 | score_growth US 零回归 | ① | economy='US'（显式传参与默认）与改前行为逐键相等（硬编码期望值） |
| t03 | score_inflation 非 US/US | ① | 同 t01/t02 逻辑施于通胀维度 |
| t04 | DATA_INSUFFICIENT 负向敏感度 | ① | 破坏实现（强制 economy!='US' 也走 US 阈值）→ 测试变红（负向敏感度实录） |
| t05 | main(economy=...) 存档命名 | — | US→scorecard_{ymd}.json（20 legacy 键在+无 economy 键）；JP→economy_scorecard_JP_{ymd}.json（含 economy='JP' 键）；md 同构 |
| t06 | 评分卡渲染标题前缀 | — | 非 US md 标题含经济体名前缀；US md 零回归 |
| t07 | 数据包「经济体观察」节在场 | ② | build_markdown 输出含节标题、四经济体行序 US,CN,JP,EA、五列表头 |
| t08 | 经济体节渲染快照 | ② | 缺席披露行、sources_status 披露行、制度/数据状态列取自非 US 存档时的渲染形态 |
| t09 | Gate B 新锚点全量核验（在族） | ③ | build_anchors 快照（USDJPY/EURUSD 在 global 支路）→ 锚点族含两 id；resolve/核验路径全绿 |
| t10 | Gate B 锚点身份核验（域外 fail-closed） | ③ | NIKKEI225/DAX（facts 接线延后=无锚点）以域外形态输入核验面 → UNVERIFIED/SOURCE_MISMATCH fail-closed |
| t11 | PAIRS 新对登记 | — | PAIRS 恰 12 对；前 10 对零变化（硬编码旧 10 对 (a,b,label) 序列断言）；两新对 a/b/label/disclosure 逐字断言（勘误注记见 §零.6-c1：初稿误记五字段） |
| t12 | 新对全链路计算 | ③ | 合成快照（含 NIKKEI225/DAX 序列）→ compute_all 产出两新对皮尔逊值（硬编码期望，双精度断言）+markdown 行 |
| t13 | 报告模板零改动判定固化 | — | mock _call_glm 捕获 prompt：数据包含经济体观察节 → prompt 文本含节标题（L128 自动进入的实测证明） |
| t14 | CI 兼容回归 | ③ | 链路级：既有 e2e 调用形态（ms.main 默认参数）在含经济体节的装配输出上正常运行 |

负向敏感度测试计划（契约§四）：t04（评分维度）+ t10（Gate B fail-closed）双负向。测试自身红/绿验证实录于 §一。

### §零.8 上游接口登记（WP-A/WP-B 交接面）

- fixt.py 已含 japan/jp/ea 七通道合成载荷（WP-A 交付面）；本包测试直接复用，零新增夹具文件。
- snapshot_builder 的 jp/ea 通道仅贡献 sources_status（facts 接线=WP-B F1 延后项）；series_store 无 NIKKEI225/DAX 键（WP-B F2 延后项）。本包经济体节与相关性新对在这两个延后面上的行为=如实缺席（§零.6-b5/c2），不代填、不杜撰。
- registry v2.2.0 economy 字段已全量回填（WP-A），四经济体 active 计数可直接枚举（§零.6-b5 静态披露的依据）。

### §零.9 白名单外发现登记

1. **发现1（涟漪面接口缺口，登记不实施——AC-07.7/绝对禁令4 依据）**： `tests/test_phase3.py` L182 的断言 `len(results)==9 and len(missing)==1` 将 PAIRS 总数隐式锚定为 10；DESIGN L171"相关性新对"（本包 M-c 授权触面）使 PAIRS=12 后，同一输入的 missing 计数 1→3，该断言红（2026-11-06 本地 CI 镜像实测 rc=1，套件内其余 46 检查项全绿）。根因隔离实证： 同一解释器逐字复用该套件 [4] 节构造块，工作树 PAIRS(12)→9结果/3缺失(断言假)，截断 BASE 形态 PAIRS(10)→9/1(断言真)——致红面=恰为新两对（证据包⑥ ripple_isolation_output.txt）。处置建议（PENDING 操作者）： 授权单行勘正（`== 1`→`== 3`，或改用 `>= 1` 语义）或改派后续轮；本包不越白名单实施。
   **处置登记回填（v1.2 处置章授权2，2026-11-06）**: PENDING 已解除——操作者处置章·v1.2（IA-P1-WP-C-AC-v1.2，单行授权勘正；处置认定=rounds/046/OPERATOR-DISPOSITION-R046.md[注入摘要,非工作树实读,引擎侧不可达]）采纳单行勘正方案： L182 `len(missing) == 1`→`== 3`+标签「NDX缺失对除外」→「NDX与跨域新对缺失除外」。执行=第4笔整改笔（2026-11-06；git diff 单 hunk 实证该文件其余行零触碰）；重跑 72 槽全绿（§三.1）。处置定性=授权勘正非豁免非延后（R022 漂移维护纪律： 授权输入演进[PAIRS 10→12]→受赖预期值同链更新，新预期=授权实现真实输出 9/3，非调参凑结果）。
2. WP-B 已登记的 F1/F2/F3 延后项属上游既有状态，本包以 §零.6-c/§零.8 引用，不重复登记为发现。

### §零.10 已核对锚（开工时点）

| 锚 | 值 |
|---|---|
| BASE-P1C | fcd0537c9ac4b66dcd8a52c6186e814121feaf5f |
| P1_DESIGN.md blob | ~~049ec978~~（取证勘正：049ec978=设计提交；其内 blob=13b263cf3139d420e01bf1e154b03ce85a35db4c，L171 规格行所在版本，见 §零.12） |
| registry | config/metric_registry.json v2.2.0（94 条目，93 active） |
| CI 基线 | 71 测试文件，offline-tests.yml 逐文件直跑，skip=test_glm_live |
| 上游报告 | docs/P1_WP_A_REPORT.md、docs/P1_WP_B_REPORT.md（在 main，工作区零差异） |

### §零.11 预期运行结果登记（步骤9/10 前瞻，实测后对照）

1. 本包测试文件预期 14 用例全绿（t01–t14）。
2. 本地 CI 镜像预期：72 槽=71 exit=0+1 SKIPPED（test_glm_live）；既有 71 文件零回归。
3. 真实运行面（步骤10）：本包验收要点均【测试/CI】限定，且真实快照面 NIKKEI/DAX 序列缺席（上游 F2）→ 预判零真实运行产物新增（零新增 daily/ 归档、零 GLM 调用），登记为"零运行产物"并以对照依据佐证（§一 实录）。

**实测对照（步骤9/10 后追加，非预登记回改）**：

- 预期1 对照： 本包测试 14 用例实测全绿（Ran 14 tests, OK）——符合。
- 预期2 对照： 本地 CI 镜像实测 72 槽=71 rc=0+1 rc=1（**不符预期**： test_phase3.py rc=1，红=发现1 涟漪面；71 rc=0 中含 test_glm_live.py 设计性跳过面[打印"⏭️ 跳过"并 exit 0]）。槽位数 72=71+新增1 ✓（步骤9 套件数对照通过）；套件内容红已按 §零.9 发现1+§二 偏离1 如实登记，未越白名单修改。
- 预期3 对照： 零运行产物成立（§四： git status 除白名单 5 文件外零变化，data/daily 19 既有 JSON sha256 锚定清单运行前后一致[本包未对真实数据目录执行任何写入]）。

### §零.12 取证勘误登记（049ec978 对象类型与抄录命令表述失实；步骤12 装配时点发现，处置=取证更正笔）

- **发现时点与触发**： 2026-11-06 步骤12 证据包装配脚本首跑 `git show 049ec978` 取 L171 时 IndexError——该命令实测输出仅 55 行（提交元数据+diff），遂复核对象类型，暴露 §零.1 行4/行5、§零.2 标题与首尾句、§零.10 锚表、§六 第1/2 行共 7 处对 049ec978 的"blob"定性失实。
- **实测事实（2026-11-06，全值）**： `git cat-file -t 049ec978`→**commit**（设计分支尖端提交，全值 049ec978523dec659ba47f140bf41669604de24f，即冻结章"设计分支尖端"值）；`git show 049ec978 | wc -l`→55；`git show 049ec978:docs/P1_DESIGN.md | wc -l`→182，其 L171 与工作树 docs/P1_DESIGN.md L171 逐字节一致，且与 §零.2 逐字块一致；`git ls-tree 049ec978 docs/`（三件）=P1_DESIGN.md blob **13b263cf3139d420e01bf1e154b03ce85a35db4c**/P1_DATA_NEEDS_INVENTORY.md blob **df79c06f66c368d93159b7a3b46852b6fcb9b196**/P1_DELIVERY.md blob **314c2644a51f2f575a90253580cb56346e2f93b6**；`git ls-tree HEAD`（同三件）blob 与上逐值相等；`git merge-base --is-ancestor 049ec978 HEAD`→exit 0（设计提交在本分支祖先谱系）。
- **勘正结论**： 抄录**内容**经正确命令复核仍逐字节一致（抄录实体无失实）；失实面=对象类型表述（commit 误记为 blob）与取数命令表述（漏 `:docs/P1_DESIGN.md` 路径限定）。"设计在场"核验结论经 ls-tree 双侧 blob 等值+is-ancestor 判定复核**成立**。7 处原文均划线保留+更正指针（不删原文，先例沿 WP-B fa95213）。判定权留操作者/审计。
- **纪律面自检**： 本勘误属登记文本的取证表述失实（如实申报义务面），非登记实现参数回改——§零.6 实现参数零触碰；代码/测试/数据面零变化。

---

## §一 实现实录（步骤7）

### §一.1 M-a macro_scorecard.py（触面=economy 参数化，登记§零.6-a 全项落地）

- L38-41： `ECONOMY_NAMES` 四经济体名映射 + `ECONOMY_SCORECARD_PREFIX='economy_scorecard_'` 常量（登记§零.6-a3 命名定值的实现载体）。
- L99-118： `score_growth(facts, economy='US')`——economy!='US' 时 4 项 US 专属指标逐项进 missing（reason 含经济体码+"阈值表未定义,如实计缺失"），返回 `({}, None, missing)`（total=None=禁0占位）；US 分支体逐字节未动。
- L200-216： `score_inflation(facts, economy='US')`——同语义，通胀 4 指标（CORE_CPI/BEI_10Y/WTI_F/AHE）。
- L414-437： `save_scorecard(..., economy='US')`——prev 档 glob 按经济体分流（US=`scorecard_*.json` 原样；非US=`economy_scorecard_{economy}_*.json`），制度比较各命名族独立（US 路径零回归）。
- L484-487： `result['economy']=economy` 仅非 US 写入；存档基名 US=`scorecard_{ymd}`/非US=`economy_scorecard_{economy}_{ymd}`。
- L517-519/532-536/541-545： render_markdown 非 US 标题经济体名前缀 + 两维总分 None→「—(该经济体阈值口径未定义,不计分不折0)」。
- L577-616： `main(date_str, data_dir, economy='US')` 穿线（非 US 打印经济体行；economy 传至维度函数与 save_scorecard）。数据不足主判定逻辑（`len(scores) < MIN_AVAILABLE_PER_DIM`）未动——非 US 经由既有机制自然判 DATA_INSUFFICIENT，零新判定逻辑。

### §一.2 M-b data_assembler.py（触面=经济体观察节，登记§零.6-b 全项落地）

- L82-105： `ECONOMY_NAMES`/`ECONOMY_CHANNELS`（JP=(japan,jp)、EA=(ea)，通道名以 `research_provenance.SOURCE_FILE_RULES` L168-176 实读为准）+ `economy_scorecard(economy, ymd, data_dir)` 数据访问 helper（在场才读，缺损坏返回 None；非渲染函数，与 latest_before/scorecard_state 同类）。
- L267-320： build_markdown「经济体观察」节——位置=中国市场后/联邦基金期货前（t07 断言）；引言披露阈值仅 US；单表五列（经济体/增长/通胀/制度/数据状态）；行序 US,CN,JP,EA；制度/数据状态取当日评分卡 JSON（US=主评分卡同源 scorecard_{ymd}.json）；表后静态注册表活跃计数披露行（实取 v2.2.0: US=48/CN=10/JP=8/EA=11）+ JP/EA 通道披露行（快照顶层 sources_status）。

### §一.3 M-c correlation_calculator.py（触面=PAIRS 新对，登记§零.6-c 全项落地）

- L46-53： PAIRS 末尾追加两跨域对（a/b/label/disclosure 四字段与登记逐字一致）；既有 10 对零变化（t11 断言）；compute_all/渲染零改动——新对数据驱动进既有管线，真实快照无 NIKKEI225/DAX 序列时如实进 missing（"序列缺失"，§零.6-c2）。

### §一.4 M-d report_generator.py（条件类=零改动判定成立）

- 工作树零 diff（git status 无该文件）。判定依据链（§零.6-d）获 t13 实测固化： mock `_call_glm` 捕获 prompt，数据包（含经济体观察节）原样进入 `## 本周市场数据` 嵌入区（DESIGN L128 自动传导）。零模板改动=设计既定形态，非缺漏。

### §一.5 测试件 tests/test_p1_wp_c.py（14 用例）

- t01-t04 维度扩展+DATA_INSUFFICIENT 负向（t04=卫语句破坏注入负向敏感度，破坏件实测改变可观测行为=断言绑定诚实形态）；t05-t06 存档命名/19 legacy 键面/标题；t07-t08 数据包经济体节渲染快照；t09-t10 Gate B 锚点在族 MAPPED+域外 fail-closed UNVERIFIED（负向）；t11-t12 PAIRS 登记+全链路（±1.0 皮尔逊=比例序列数学性质，非自证）；t13 报告模板零改动判定固化（桩注入点=tests/test_p1_wp_c.py L403 `rg._call_glm = fake_glm`，本地合成桩零出站）；t14 既有链路兼容（fixt.build_full_day 全链）。
- 开发过程实录： t02 首跑红一次——根因=测试作者手算笔误（WTI_F 75.0 档位：<70→0 档不含 75，实为 70≤v<90→+1），勘正测试期望值（0→1，总分+2→+3），**非实现侧改参**（实现阈值面零改动）；勘正后 14/14 全绿。负向敏感度双负向（t04/t10）实测有效。

## §二 偏离与如实声明（步骤9-10 实测后登记）

1. **套件 test_phase3.py 红（规格涟漪×白名单边界冲突，如实 FAIL 登记，判定权留操作者/审计）**： 详 §零.9 发现1。本地 CI 镜像 71 rc=0+1 rc=1（预期 71+1SKIP）。AC-03.5"本地逐套件运行全绿"在本包自评=不满足（单套件红，根因=DESIGN L171 授权改动对白名单外既有测试计数断言的必然涟漪；处置=AC-07.7 登记不实施）。未调参、未造数、未越界、未回改登记。**（v1.2 处置闭环）**: 处置章单行授权勘正落地后重跑 72 槽全绿（§三.1），AC-03.5 闭环；本条 v1.1 执行段原文保留。
2. **登记节勘误三处（均发生于实现前/任何运行前，零回改已登记实现参数）**： ①§零.6-c1 PAIRS 字段名误记（id/group→实际 a/b/label/disclosure，label 分隔符×→vs）；②§零.6-b3 sources_status 归属表述（"快照 facts 的"→快照顶层字段）；③§零.6-a4 legacy 键计数 20→19。三处均以勘误注记保留原文勘正，不删除历史痕迹。
3. **t02 首跑红勘正**（§一.5）： 测试期望值手算笔误勘正，非实现改参；全过痕迹留证据包④。
4. **上游延后面如实呈现（非本包偏离，登记备查）**： 真实运行面 NIKKEI225/DAX 无 series_store 键（WP-B F2）、jp/ea 通道事实未接线（WP-B F1）→ 相关性新对在真实快照=如实 missing、经济体观察节 JP/EA 行=快照 sources_status 披露（设计内合法如实形态，t12/t07 分别固化）。
5. **零真实运行**： 本包零 GLM 调用、零网络出站、零凭证、零付费；测试全合成（唯一数据源=tests/fixt.py+测试内发明值）。
6. **取证表述失实一处族（步骤12 发现，取证更正笔处置）**： §零.1 行4/行5、§零.2 标题与首尾句、§零.10 锚表、§六 第1/2 行对 049ec978 误记为 blob/漏路径限定命令（共 7 处）——实测=commit（设计分支尖端），抄录实取命令=`git show 049ec978:docs/P1_DESIGN.md` L171；抄录内容与"设计在场"结论经正确命令复核均成立，仅表述失实。全记录=§零.12，7 处原文划线保留+更正指针，零 amend 纯线性追加。

## §三 本地 CI 镜像实录（步骤9）

- 执行面： 与 offline-tests.yml 同构（逐 tests/test_*.py 直跑 python3），2026-11-06（UTC 时刻见证据包④文件时间戳）。
- 槽位对照： 冻结章 BASE=71 套件（run 42082218620： 70 exit0+1 SKIPPED[注入转录，非本 Agent 实取]）；本包后=72 套件=71（基线）+1（新增 test_p1_wp_c.py）。套件数对照 **通过**。
- 逐套件结果： **71×rc=0**（含 test_glm_live.py 设计性跳过面——打印"⏭️ 跳过(设置 RUN_GLM_LIVE=1…)"并 exit 0；含本包 test_p1_wp_c.py rc=0[14/14 绿]）；**1×rc=1=tests/test_phase3.py**（根因与处置=§零.9 发现1/§二 偏离1；套件内 46/47 检查项绿，红项恰为 L182 计数断言）。逐套件清单原样存证据包④ ci-mirror/results.txt。
- 未自行 dispatch GitHub CI（步骤14 纪律；CHECKPOINT 登记件将落 rounds/046/P1-WP-C-CI-dispatch-evidence.md——操作者面）。

### §三.1 v1.2 整改续作重跑实录（处置章授权3，2026-11-06）

- 授权依据： 处置章·v1.2 单行授权勘正（操作者 2026-11-06 03:2x HKT；处置认定=rounds/046/OPERATOR-DISPOSITION-R046.md[注入摘要,非工作树实读,引擎侧不可达]）。
- 勘正面（授权1）: `tests/test_phase3.py` L182 单条 check 语句 `len(missing) == 1`→`== 3`+标签「NDX缺失对除外」→「NDX与跨域新对缺失除外」；该文件其余一切行零触碰（git diff 单 hunk 实证，见证据包③）。
- 重跑结果（同镜像方法学=逐 tests/test_*.py 直跑 python3，2026-11-06）: **pass=72 skip=0 fail=0（72 槽全绿）**；含 test_phase3.py rc=0（套件内 47/47 检查项绿，尾部摘要「47通过 / 0失败」）、test_p1_wp_c.py rc=0（Ran 14 tests, OK）、test_glm_live.py rc=0（设计性跳过面）。逐套件清单=证据包④ ci-mirror/results.txt（重跑版）；test_phase3.py 修复后全量 stdout=证据包④ test_phase3_postfix_stdout.txt（新增成员）。
- 负向敏感度（红→绿转换实证）: 同一合成输入 snap_fake 下，v1.1 旧期望（==1）实测 rc=1（红=发现1 涟漪面）↔ v1.2 勘正后期望（==3）实测 rc=0——断言真实绑定被测行为，非自证恒真。
- data/daily 锚定复核（⑥类真实性，重装配时点）: DEV 仓库 data/daily 19 档 sha256 与 v1.1 锚定清单逐一一致（19/19，零新增零漂移）；本包对真实数据目录零写入不变。
- v1.1 执行段红态记录（§三 主体）按历史原文保留，不回改。

## §四 真实运行面判定（步骤10）

- 判定： **零运行产物**。依据： ①抄录行验收要点限定词均【测试】/【测试/CI】（§零.2），无真实运行类要点；②AC-02.4 真实运行类要点=无（不适用）；③真实快照面 NIKKEI/DAX 序列缺席（上游 F2）——即使运行相关性面，合法结果=如实 missing（§一.3），不构成需落 data/research/ 的研究产物。
- 锚定： data/daily 全量 19 个既有 JSON sha256 清单（证据包⑥ data_daily_sha256_anchor.txt，2026-11-06 实取）与开工时点一致——本包未对真实数据目录执行任何写入（git status 干净面见证据包③）；data/research/ 无本包产物。

## §五 逐要点证据映射表（步骤11，AC-02）

| 要点（抄录§零.2） | (a)实现落点 | (b)证据指针 | (c)自检结论 |
|---|---|---|---|
| ①维度扩展单测+DATA_INSUFFICIENT 负向【测试】 | scripts/macro_scorecard.py L99-118/L200-216/L577-616；tests/test_p1_wp_c.py L93-138(t01-t03)/L143-161(t04) | 证据包④ test_p1_wp_c_full_stdout.txt（14/14 OK 含 t04 负向）；本 REPORT §一.1/§一.5 | 过（非US如实缺失+负向敏感度实测有效） |
| ②数据包经济体节渲染快照测试【测试】 | scripts/data_assembler.py L82-105/L267-320；tests/test_p1_wp_c.py L241-277(t07-t08) | 证据包④（t07/t08 ok 行）；§一.2 | 过（节位置/行序/五列/披露行逐断言） |
| ③Gate B 对新锚点全量核验用例【测试/CI】 | 锚点零改动面=snapshot_builder.build_anchors 既有 global 支路（USDJPY/EURUSD 自动覆盖）；freshness_policy.verify_anchor_identity 既有 fail-closed；tests/test_p1_wp_c.py L282-322(t09-t10) | 证据包④（t09/t10 ok 行）；§一.4/§三 | 过（在族 MAPPED+域外 UNVERIFIED 双向+CI 镜像 t14；套件面红=test_phase3 涟漪，见偏离1，与本要点用例无涉——本要点用例全绿；v1.2 处置章勘正后该套件已绿，§三.1） |
| 技术要点子项： scorecard economy 参数化(DP-3) | §一.1 全列 | t01-t06 | 过 |
| 技术要点子项： 数据包经济体节 | §一.2 全列 | t07-t08/t14 | 过 |
| 技术要点子项： 相关性新对 | §一.3 全列 | t11-t12 | 过 |
| 技术要点子项： 报告模板与 Gate B 锚点 | 零改动判定（§一.4） | t13/t09 | 过（零改动=设计既定[L68"零改动"/L128]） |
| DP-3 判据⑥： 登记零回改 | §零.5 定值=形态①；实现与登记一致（签名/命名/键面/标题）；运行后 §零 登记节未回改（三勘误均注记于实现前） | 本表+§二.2 | 过 |
| DP-3 判据⑥： 确认型未自决 | 本包零确认型 DP（§零.5） | §零.5 | 过（不适用而登记依据） |

无漏检自检： 抄录验收要点 3 条+技术要点 4 子项+DP 判据 2 行=映射 9 行，逐一对应。

## §六 §5.3 六项数值标注自检清单（步骤8）

| # | 数值 | 标注 |
|---|---|---|
| 1 | BASE-P1C=fcd0537c9ac4b66dcd8a52c6186e814121feaf5f；~~design blob=049ec978~~（取证勘正→设计提交 049ec978，其内 DESIGN blob=13b263cf…，见 §零.12） | [实取·来源: git rev-parse/ls-tree, 2026-11-06, 证据包③] |
| 2 | 规格行=P1_DESIGN.md §六 L171 | [实取·来源: ~~git show 049ec978 L171~~→`git show 049ec978:docs/P1_DESIGN.md` L171（§零.12 勘正命令）, 抄录件=证据包①] |
| 3 | 白名单 A 类 3 件+M 类 4 件（k=3 A 行） | [实取·来源: 本 REPORT §零.3; git diff name-status 对照=证据包③] |
| 4 | registry v2.2.0=94 条目/93 active；活跃计数 US=48/GLOBAL=12/EA=11/JP=8/CN=10/HK=4 | [实取·来源: config/metric_registry.json 实测清点 2026-11-06; 渲染行测试断言=t07/t08] |
| 5 | PAIRS 12 对（旧 10+新 2）；新对字段 | [实取·来源: scripts/correlation_calculator.py L28-53; t11 硬编码断言] |
| 6 | 19 legacy 键（§零.6-a4 勘误后值） | [实取·来源: scripts/macro_scorecard.py save_scorecard result 字面 L461-481; t05 set 断言] |
| 7 | 本包测试 14 用例全绿 | [实取·来源: 证据包④ stdout "Ran 14 tests ... OK"] |
| 8 | CI 镜像 72 槽=71 rc=0+1 rc=1（test_phase3.py 红=发现1） | [实取·来源: 证据包④ ci-mirror/results.txt, 2026-11-06] |
| 9 | 基线 CI=71（70 exit0+1 SKIP, run 42082218620） | [示意·非实取——冻结章注入转录, 本 Agent 未实取该 run；套件数 72 对照以本地实测为准] |
| 10 | data/daily 19 既有 JSON 锚定 | [实取·来源: 证据包⑥ sha256 清单] |
| 11 | 皮尔逊期望 +1.0/-1.0（t12） | [示意·非实取——比例/反比例序列数学性质，独立手算] |
| 12 | WTI_F 75.0→+1 档（t02 勘正后） | [实取·来源: scripts/macro_scorecard.py L227-231 阈值链实读; §一.5 勘正实录] |
| 13 | v1.2 勘正定值 missing==3（标签=「NDX与跨域新对缺失除外」） | [实取·来源: tests/test_phase3.py L182 实读+处置章授权1; 重跑 9/3 rc=0=证据包④] |
| 14 | v1.2 重跑 CI 镜像 72 槽全绿（pass=72 skip=0 fail=0） | [实取·来源: 证据包④ ci-mirror/results.txt 重跑版, 2026-11-06] |

复核记录： 上表 [实取] 项 2026-11-06 提交前回工作树实读复核一遍（禁凭记忆）；~~疑似失实项=无新增（三处登记勘误已于实现前以注记处置，见 §二.2）~~（取证勘正追加： 步骤12 实际发现第 1/2 行 049ec978 表述失实一处族，已按 §零.12/§二.6 处置——本行原文保留并以此注记更新）。边界声明： 本 REPORT 日期/SHA 均为实取 UTC/全值；证据包装配时点=步骤12，晚于本清单（清单件随包入⑦）。v1.2 续作注记（2026-11-06）: 行13/14 为整改笔新增，[实取] 项同批回工作树/重跑输出复核；行8（71 rc=0+1 rc=1）为 v1.1 执行段历史值，原文保留（终态=行14 全绿）。
