# Charter 9 最终验收报告(E席独立终验)

- 验收席: E席(独立隔离,与前席 A/B/C/D 无隶属;不信任前席声明,实测为准,只读不修)
- 日期: 2026-11-11
- 验收对象: dev 分支 `charter9-closeloop-v1` @ `7dcbf8e`(D席六笔终态)
- 隔离沙箱: `/tmp/ia-c9` = 该提交干净 clone + dev 全量数据 + venv(streamlit 1.50.0)
- 零Key纪律: 全部引擎/CLI 命令以 `env -u MODEL_API_KEY -u MODEL_BASE_URL -u MODEL_NAME -u 厂商A_API_KEY -u FRED_API_KEY -u TUSHARE_TOKEN -u FINNHUB_API_KEY` 执行
- 验收面: 章程§八 A-E 五面 + 六层矩阵 + §10 红线终检 + 附带处置检查

## 判定总表

| 验收面 | 判定 | 一句话依据 |
|---|---|---|
| A 全景(13节报告01/02/03节抽格复算) | **PASS** | 02节市场表 40/40 格、01节宏观表 19/19 格、03节相关系数 4/4 逐格复算一致(唯一偏差 HSI×SPX 第4位小数截断,见观察1,非错值) |
| B 机构观点(≥5机构≥8真实资料+诚实不足面) | **PASS** | 17档/15机构 lint 17/17;实网抽验 UBS/OECD 2/2 可达(publishedTime 一致);core_views 引文 verbatim 抽 6/6 全中;BIS 0点位/BOJ 第三方转述不入库/MSIM 仅标题/PBoC Q3未发布 四处诚实面属实 |
| C 交叉验证(133假设级链四专项) | **PASS** | ①独立扫描 70 forecasts 无漏判到期件 ②两到期件独立复算全中(FED_FUNDS 9月加息 3.63→3.75→3.88;UST_10Y 2026-08-31=4.75 精确) ③红线专项零违例(验证窗=publish→horizon_end 代码级确认,全库 mode C 外机器 supports/against=0) ④validate_vp 17/17,133=28 NYT+105 INSUF 精确,label 全由 mode C 映射 |
| D 一键完整研究(核心) | **PASS** | 零Key亲手走通 9 环全链(doctor→overview→changes→views→verifier A/B→edges→compare→analog→research-map→archive 往返);反预写死测试通过(换输入→内容重生成,结构固定);A席报告显式绑定 research_snapshot_20261110_v5;污染事件已隔离+基线 sha256 复核无损(见观察5,非代码缺陷) |
| E 反例测试10项 | **PASS** | 10/10 项项亲自复放(非仅查测试存在),每项至少一路径实测正确拒绝/降级/标不足(明细见下表) |
| 六层矩阵 | **6/6 全 EXECUTED** | 第6层 Web = AppTest 函数级(页1/3/4) + 真实无头 streamlit 起服(port 8631 HTTP 200)双执行 |
| 红线§10 | **10/10 全绿** | 逐条实测,见红线终检节 |
| 附带处置检查 | **在案/有登记缺口** | C席4观察+A席5缺口均有落点不丢,但均未转入 canonical 台账(docs/REMAINING_ISSUES.md 停留在 2026-10-17),建议下轮转入(见附带处置节) |

**BLOCKER 清单: 无。**
**总判定: Charter 9 五面全 PASS、六层全实测、零 BLOCKER —— 最终验收通过。**

---

## 面A: 全景抽格复算 — PASS

- 底稿: A席 13节终报告(归档 QB-20261111-010),绑定 research_snapshot_20261110_v5(快照绑定在面D核验)。
- 01节宏观表: 19/19 格独立取数复算一致(经 `metric_series` 从 v5 series_store/注册表源取真值)。
- 02节市场表: 40/40 格逐格复算一致(涨跌幅/水平值/单位全对)。
- 03节相关系数: 4/4 对复算一致;唯一偏差 HSI×SPX: A席 +0.1933 vs 正确四舍五入 +0.1934(截断而非舍入,第4位小数,纯装饰性,见观察1)。
- M表 9 条(含 M9 新发现): 抽 M 链证据定位到 transmission edges 档,VERIFIED 计数 33 与 source_verifier 汇总 `{'VERIFIED': 33, 'PARTIAL': 0, 'MISSING': 0, 'CONFLICTED': 0}` 一致(面D重放)。

## 面B: 机构观点档 — PASS

- lint 17/17(ia_cli views lint),15 机构 17 档;schema v1.1(只存元数据+短引文≤500字符+链接)抽查合规。
- 元数据一致性: 抽 6 档(institution/published/source_url/source_type 字段齐全、日期格式一致)。
- 实网可达性(我自定抽样,离线判存在性+抽2档实网): UBS `article.3983955`(publishedTime 2026-11-09)与 OECD 新闻稿(publishedTime 2026-09-23)均 200 可达且日期与档内一致 — 2/2。
- 引文 verbatim: 抽 6 条 core_views 与原文逐字比对全中,含 UBS "The Federal Reserve is likely to raise interest rates … December 2026 and March 2027" 整句、NFP 165k/4.1%、10Y 5.36%→4.87% 证据项。
- 诚实不足面(四处全属实):
  - BIS 回顾性研究 0 量化点位 → forecasts 留空如实;
  - 第三方转述机构观点不入库(注: 实际档为 BOJ VIEW-20261110-006;开工令写作"MSIM",系口径笔误,见观察3;MSIM 011 本身= headline_only 如实);
  - PBoC Q3 未发布 → 注记非缺采;
  - 缺正文档 headline_only 标注如实。

## 面C: 交叉验证四专项 — PASS

1. **护栏真实性(独立扫描)**: 我另写扫描器对全库 70 条 forecasts 独立判到期性: 38 条 horizon 在 2026-11-10 之后(未到期) + 1 条已到期(009#8,引擎判 NOT_MACHINE_VERIFIABLE,定性目标禁猜,正确) + 31 条定性/不可解析 + 4 条"已实现数据"(非预测)。**无任何已到期件被漏判**;maturity guard 确实压制 mode A/B 产出 supports/against。
2. **两到期件独立复算**: ①FED_FUNDS 月频 3.63→3.75→3.88(2026年9月加息兑现;与面B实网 UBS 原文交叉印证)②UST_10Y 2026-08-31 = 4.75 精确命中。验证窗 basis 取 start 前最后一观测(代码级确认)。
3. **红线专项(历史走势≠预测验证)**: `verify_expiry` L468-569 窗口=publish→horizon_end,严守发布后;全库 mode C 之外机器 supports/against = 0;A席 R 链相关系数均明示描述性;133 条链中无一处用过去一年上涨证明未来一年预测。**零违例**。
4. **VP sidecar**: `validate_vp` 17/17 通过(digest 前缀/索引界/聚合一致性交叉校验);133 假设 = 28 NOT_YET_TESTABLE + 105 INSUFFICIENT_EVIDENCE 精确;全部 evidence.mode=C(A/B 仅存 note 字段);view_label 与 `rollup_view_label` 最保守聚合逐档一致。

## 面D: 一键完整研究(核心) — PASS

零Key亲手全链(每环实际执行,命令留痕于审计沙箱):

| 环 | 结果 |
|---|---|
| ia_cli doctor | 只读体检 ok,无 Key 如实报 |
| overview US/CN | 两经济体确定性面输出 |
| changes | 全指标最新变动 |
| views lint/list/get | 17/17;单档详情完整 |
| view_verifier mode A | 52 条 verdict(vintage 锚定) |
| view_verifier mode B | 59 条 verdict(since_publish) |
| source_verifier edges | 33 VERIFIED / 0 MISSING |
| compare 自配对 | SPX 1y +12.4276%(公共窗口径) |
| analog | valid=73,5 簇(2024-12/2023-12/2022-01/2020-12/2019-12),符号一致率 SPX 0.8/UST 0.6/DXY 0.6/GOLD 0.8 — 与 QB-023 精确复现 |
| research-map | 十问全扇出(信封 data.map),RQ3/RQ9 明示归编排层 ai_inferred |
| archive save/get | 六参+snapshot 绑定往返一致;A席 QB-20261111-010 显式绑定 research_snapshot_20261110_v5(ir.target_snapshot_id+六参+model:null) |

- **反预写死测试(必做项)**: 抽节用中间件重装配 — 子集 views 目录 + 空归档目录重跑 research-map → 计数/面变化(结构固定、内容由当期输入决定),digest 随输入变化。通过。
- **Web 入口行为**: 页1"运行 run_weekly.py"唯一按钮在 expander 内,不点击零执行(AppTest 探针证实);无模型 Key 环境 research --explain → `model.ok=false` 诚实降级信息,给可执行命令而非伪造研究。
- **污染事件(操作面,非代码缺陷)**: 验收期间一外部并发进程在我沙箱执行了 archive save(QB-20261111-011,15:06:16)与 run_weekly(台账 15:10:30,gate_a FAIL→allow_formal_report False,4 依赖步显式跳过)。处置: 全部 *20261111* 产物隔离至 `/tmp/audit_e/quarantine_20261111/`;v5+macro_20261110 与 dev sha256 逐字节一致、全数据树 diff 为空;受影响检查全部重跑后精确复现 A席/QB-023 结果。run_weekly 本身行为正确(gate FAIL 如实)。见观察5。

## 面E: 反例测试10项 — PASS(10/10 项项亲自复放)

| # | 反例 | 复放路径(实测) | 结果 |
|---|---|---|---|
| 1 | 未到期 | UBS VIEW-20261110-004 mode C 实跑 | 4× NOT_YET_TESTABLE,禁判 ✓ |
| 2 | 缺出处 | 伪造无源 QB 档入 source_verifier | 该件 MISSING(32 VERIFIED/1 MISSING)✓ |
| 3 | 假设矛盾 | rollup 六标签全组合枚举 + 篡改 view_label 的 sidecar | 优先级表全对;篡改件被 validate_vp 拒绝 ✓ |
| 4 | 不同期限 | 8 种 horizon 变体喂 parse/verify | 逐变体 horizon_end 正确;1 处解析怪癖见观察4(库内0影响)✓ |
| 5 | 历史修订 | MSIM 009/006 验证独立于后续修订 | vintage 锚定+revisions 只增改+basis 锚定 ✓ |
| 6 | 样本不足 | 真实 analog 候选<8 + hist_14(<36月) | insufficient_candidates 拒答+MIN_HISTORY 拒答 ✓ |
| 7 | 门禁失败 | 污染事件台账(真实 gate_a FAIL)+ research_mode_gate 三态 | 4 步显式跳过链+formal 被阻 ✓ |
| 8 | 正文不可得 | answer_text=None 喂 source_verifier | MISSING ✓ |
| 9 | 无模型 Key | 零Key research --explain | model.ok=false 诚实降级 ✓ |
| 10 | 无历史档案 | 空归档目录 research-map/archive face | n_records=0+如实注记 ✓ |

## 六层矩阵

| 层 | 面 | 执行方式 | 状态 |
|---|---|---|---|
| 1 | 代码实现 | view_verifier/view_plausibility/source_verifier/research_map/analog_engine/workbench_data/ia_cli/app.py 关键路径通读+行为验证 | **EXECUTED** |
| 2 | 合成测试 | C9 各测试文件逐文件自跑(仓库自跑约定): 124 pass / 1 env-sensitive fail(test_oss_product W7,独立跑通过,零 C9 diff,见观察2)/ 1 designed skip | **EXECUTED** |
| 3 | 真实数据测试 | 面A 63格复算/面C 70条扫描/compare/analog 真序列 | **EXECUTED** |
| 4 | 真实机构资料验证 | 面B: 17档 lint+6档元数据+2档实网+6条 verbatim | **EXECUTED** |
| 5 | 完整 Agent 研究流程 | 面D 12环全链零Key+反预写+归档往返 | **EXECUTED** |
| 6 | Web 端实际使用 | AppTest 函数级(页1按钮纪律/页3 17档选择器+六标签/页4 RQ1 ai_inferred)+ 真实无头 streamlit 起服 port 8631 HTTP 200 后手动停服 — 双执行,如实记录: 两法均做到页面渲染级(非人工浏览器点击) | **EXECUTED** |

## 红线§10 终检

| 红线 | 判 | 依据 |
|---|---|---|
| 复用无新框架 | ✓ | research_map/编排层全部复用 wd/vs/vv 既有件 |
| 模型无关 | ✓ | C9 全链零Key端到端走通;MODEL_* 三参为前席既有可选层 |
| 零新依赖 | ✓ | requirements 与前一 charter 0 diff |
| 零自动付费 API | ✓ | 确定性层零网络;仅我人工抽验 2 URL |
| 未绕付费墙 | ✓ | UBS/OECD 公开页 |
| 未删研究数据 | ✓ | 污染事件后全数据树 diff 为空 |
| 合成不冒充 | ✓ | SYNTH: 前缀跳过+披露 |
| CI 绿≠验收替代 | ✓ | 本验收全为独立实测,未采信任何 CI/前席声明 |
| 正确性优先 | ✓ | 发现并如实上报观察1-6,未粉饰 |
| 分支未合并未动生产 | ✓ | charter9-closeloop-v1 @7dcbf8e 未合并;LIVE 未触碰 |

## 附带处置检查(C席4观察+A席5残留缺口: 要求不丢)

| 项 | 现有落点 | 台账状态 |
|---|---|---|
| C席观察① mode A 证据表随 publish 年龄变薄 | audit/C9_FIX_REVERIFY.md L86-91(dev 工作区在案) | 未入 docs/REMAINING_ISSUES.md(该档停于 2026-10-17)与 P2 台账(Charter7 版) |
| C席观察② forecast_target_map 仅 2 条可判映射 | 同上 | 同上 |
| C席观察③ pytest 无法收集(test_afin sys.exit,自跑约定) | 同上 | 同上 |
| C席观察④ "2027年起年度步伐"→2027-12-31 语义边界 | 同上 | 同上 |
| A席缺口: 深拆仅5/17机构;M2/M4-M9 无情景;非美 analog NOT_VERIFIED;财政/贸易四经济体+HK 全缺;AI capex/油供需库存序列缺 | 逐字内嵌于归档记录 QB-20261111-010.research-full.json(深拆×4/情景×9/非美×2/财政×2/AI capex×3/NOT_VERIFIED×12)+ 13节报告 NOT_VERIFIED 总清单 | 同上(归档记录在 dev 数据面持久,公开仓按纪律不含数据) |

**结论: 两批均"在案不丢"(审计档+归档记录双落点),但 canonical 台账(docs/REMAINING_ISSUES.md / docs/P2_DATA_GAP_LEDGER.md)未承接 Charter9 条目。下轮建议: ①把上述 9 条转入台账 ②audit/ 目录(含本报告)随 Charter9 合并提交——当前 `?? audit/` 未跟踪,是登记链最弱一环。**

## 非阻塞观察(均不构成 FAIL)

1. **HSI×SPX 相关系数 +0.1933 vs 正确 +0.1934**: A席报告截断而非四舍五入(第4位小数)。装饰性;下轮顺手修。
2. **test_oss_product W7 环境敏感**: 套件内跑失败、独立跑通过;为前席遗留、零 C9 diff。建议标记 skip-if-env。
3. **开工令口径笔误**: "MSIM目标位仅第三方转述不入库"——实际第三方转述档为 BOJ VIEW-20261110-006;MSIM 011 为 headline_only。诚实不足面本身两处均属实,不影响判定。
4. **parse_view_horizon 同形多时点取首**: "2026年12月与2027年3月"解析为 2026-12-31(docstring 承诺多时点取最晚);根因=逐族 re.search 首匹配。全库扫描 0 条同形多时点字符串,库内零影响。P3 下轮修。
5. **沙箱污染事件(操作纪律)**: 并发席位共用 /tmp 隔离目录导致外部进程在我沙箱写档+跑管线。已隔离+基线 sha256 复核无损+全部受影响检查重跑通过。建议: 各席位沙箱用唯一路径(如 /tmp/ia-c9-<seat>-<ts>),协调方在开工令中显式分配。
6. **openai SDK 在 requirements**: 前席既有可选层(--explain 显式开关),非 Charter9 引入,零新依赖红线不受影响。

---

*E席 · Charter9 最终验收 · 判定: 五面全 PASS / 六层全 EXECUTED / 零 BLOCKER —— 通过*
