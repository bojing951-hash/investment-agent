# IA-DATA-W3 交付文档 — DATA_W3_DELIVERY

> 工作包: IA-DATA-W3(数据线第2包·修复)| 合同: IA-DATA-W3-AC-v1.0(FROZEN 2026-11-04,操作者依用户 2026-11-01 代批授权)
> 执行分支: `dev/data-w3-fix`(基点 09bdd937cca348a31a0e67858c35f28fdf32806a = main) | 本文档=合同 AC-06③ 五节交付

---

## §一 改动

**Git**: 分支 `dev/data-w3-fix` 自 09bdd93 线性切出,恰 1 笔提交,零 merge/amend/force/reset,不碰 main。diff 面 `git diff --name-status 09bdd93..HEAD` 恰 4 行=白名单(1M+3A):

| 动作 | 文件 | 摘要 |
|---|---|---|
| M | scripts/china_market_collector.py | 5 修复实体(+58/-6 行): ①fetch_margin 成功响应契约键映射 `margin.balance`=(Σrzye+Σrqye)÷1e8 亿元(L464-476);②全文件裸 except 清零+5 处静默异常路径留日志(L326-332/L366-373/L479-483/L495-499/L644-648);③fetch_valuation 双形态(pe/pe_ttm)兼容+扁平桥接 `valuation.pe`+`valuation.date`(L488-500/L503-547);④VALUATION_INDICES 纳入 000001.SH 上证身份对齐(L219-231);⑤估值逐只失败留痕补代码+类型(L540-541)。**零触碰**: 61s 闸门(L50/L54-62 原样)/A_SHARE_INDICES/EM_MAP/EM 回落/fetch_turnover 逻辑/macro_collector/registry/fact_engine/snapshot_builder/workflow |
| A | tests/test_data_w3_fixes.py | 19 用例离线行为锁(4 组),全合成 fixture、零网络(tushare/akshare/yfinance 全 mock)、零新增依赖(import 面=pandas+unittest.mock+标准库),CI `tests/test_*.py` 通配自动发现 |
| A | docs/DATA_W3_FIX_REPORT.md | 逐指标表(10+FED_FUNDS 列齐全: W2 状态/断点诊断行级/处置分类/修复行级/离线测试名/真实结果指针)+修复面总览+字段契约登记+裸except明细 |
| A | docs/DATA_W3_DELIVERY.md | 本文档(五节+勘误声明) |

**白名单符合性声明**: 白名单外零改动(git diff 可验);registry/fact_engine/snapshot_builder/macro_collector/workflow/requirements 零改动;data/daily 仅运行日 china 日档更新(见§二)。

## §二 证据(证据包 /tmp/data-w3-evidence/IA-DATA-W3-EVIDENCE.zip + SHA256SUMS)

| # | 证据 | 位置(zip 内/绝对路径) |
|---|---|---|
| ① | 采集前锚定清单(24 文件 sha256) | anchor_shasum_pre_run.txt |
| ② | 采集运行原始日志(stdout+stderr 全文) | collection_run.log(72 行;exit=0;2026-11-04T12:08:23Z 起 ~11min;代理环境=NONE 实录) |
| ③ | 全部 source-persist 原始错误证据 | collection_run.log L34(moneyflow_hsgt 权限)/L37-41(margin 权限×5 日期)/L45-48(index_dailybasic 权限×4 指数)+档内直读 china_20261104.json(margin:null/valuation:{}/southbound:null)——档与 log 均入包 |
| ④ | 覆盖复检双次输出 | coverage_pre_run.json + coverage_post_run.json(工具 sha256=765cf18470de8efdf258bd4ef35ab6058447feaf97108af006646b0ca64edab9,=06f715b6 分支内字节一致,禁改) |
| ⑤ | git/ls-remote 全量输出 | git_status_diff_log.txt(diff --name-status 09bdd93..HEAD 4 行/rev-parse/提交证明)+ls_remote_final.txt(推送后实取) |
| ⑥ | CI 登记件引用 | 操作者 CHECKPOINT dispatch 后落 `rounds/010/DATA-W3-CI-dispatch-evidence.md`(引擎侧,执行 Agent 不可达;预期 55 套件=54+1)——本包留 CI_DISPATCH_PENDING.md 占位说明 |
| ⑦ | 两 docs | DATA_W3_FIX_REPORT.md + DATA_W3_DELIVERY.md(与仓库内同源副本) |
| ⑧ | 逐套件测试记录 | all_suites_exit_codes.txt(56 套件: 49 exit=0 + 7 既有红+SKIPPED glm_live;逐套件 log suite-*.log)+ negative_sensitivity_base.log(负向敏感: 基点版 15 红)+ new_suite_green.log(19/19 绿)+ base-*.log(7 红套件基点归因: 无本轮改动亦红=既有环境红,R054 CI@09bdd93 全绿在案) |
| — | 补充 | anchor_shasum_post_run.txt+write_boundary_diff.txt(恰 1 变=china_20261104.json)/collector_fix.patch(修复 diff 留档)/fed_funds_observation.txt(四档对照直读) |

**写入边界校验**: pre/post 锚定清单 diff 恰 1 行——china_20261104.json 55feba63…→6f55d904…(运行日 china 日档更新,AC-02(c) 允许面内);其余 23 文件(含全部历史档/md)逐字节不变;零历史回填。

## §三 逐 AC 自评

| AC | 自评 | 依据 |
|---|---|---|
| W3-AC-01 修复实现与离线证明 | **过**(确定性子项) | (a)balance 映射+引擎链离线证明 t1a/t1b(产物含非空可消费字段,字段名=fact_engine 实读契约);(b)裸except=0(t3a)+5 静默路径全留日志,真实运行失败全可归因(log L34/L37-48);(c)双形态 t2b/t2c/t2g+000001.SH 对齐 t2a+等效方案论证(FIX_REPORT §〇);(d)7 项 S 逐项处置登记(FIX_REPORT 表: 6 项 code-fixed 附行级+测试、1 项 SB_FLOW source-side 附原始权限错误);(e)新测试全合成零网络零新依赖;(f)逐指标表 11 行列齐全 |
| W3-AC-02 真实数据单次诚实采集 | **过**(诚实子项;3 项 source-persist 属合法结果) | (a)锚定清单入包;(b)既有入口单次运行+61s 闸门全程生效(log 7 次 ⏳)+原始日志入包;(c)写入边界恰运行日 china 档;(d)逐项登记: 6 项 N(档内直读 via=akshare_em)/3 项 source-persist(MARGIN_BAL·SH_PE·SB_FLOW,原始权限错误在 log)/FED_FUNDS observation 在场(3.88@2026-10-01,对照 20261101=3.75@2026-09-01,20261102 缺席=FRED 瞬时已自愈);零回填零改数零放宽 |
| W3-AC-03 覆盖审计复检与无回归 | **过** | 工具 sha256 与分支字节一致且禁改;pre/post 双跑(81 行 JSON 入包);①MARGIN_BAL/SH_PE 未迁移——如实记录: 代码面断点已修(离线证明),真实值受 tushare **权限**阻断(非限流窗口),主状态 B→S(代码侧断裂消解、源端层持续),机械状态双次零变化;②新 B/C=0(机械计数与主状态均无新 B/C);③S 漂移归因: W2 基线 S8→现 S3,5 项恢复(SHCOMP/SZCI/CHINEXT/SH_AMOUNT/SZ_COMPONENT_AMOUNT/CN_TOTAL_TURNOVER)全部经基点内 R049/R051 EM 回落通道取数,与本轮 diff(仅 margin/valuation/异常日志)零因果;FED_FUNDS 恢复=FRED 瞬时自愈(源端),亦零因果;④U=0;计数 delta 逐项: N 71→78(+7 上述归因)/S 8→3/B 2→0(→S 权限层)/C 0→0/U 0→0,合计 81 恒 |
| W3-AC-04 引用真实性与只读边界 | **过** | 一切 file:line 引用取自尖端实码(抽查直读可验);否定性声明可反证: requirements 零改动(diff)/registry 零改动(diff+sha256=60ef058a…与 W2 实取一致)/零回填(锚定 diff);diff 面=白名单恰 4 行 |
| W3-AC-05 范围/分支/生产隔离 | **过** | 线性 1 笔提交无 reset/amend/force;diff 恰 1M+3A;推送后 ls-remote 全分支尖端与开工基线一致(main=50b5d13 未动);R007 节流 hunk=0(闸门 L50/L54-62 零触碰,t4b 行为锁);LIVE 零写入(real_data_acceptance.py SHA256=f9ca189c… 未动+LIVE 目录零 DEV 引用+LaunchAgents 零改动,取证入包);无新源/凭证/付费 |
| W3-AC-06 CI 与证据包 | **部分——CI 项待操作者**(结构属 CHECKPOINT) | 证据包+SHA256SUMS 最低集①-⑧齐备(⑥ CI 登记件为操作者后补占位);DELIVERY 五节+R009-D1 勘误齐备;result.md 四段=stdout 自述;CI dispatch 由操作者于最终尖端执行(预期 conclusion=success/headSha=rev-parse=ls-remote/套件=55),执行侧零自行 dispatch |

**逐项结果表(10+FED_FUNDS)**:

| 指标 | 结果 | 直读/证据 |
|---|---|---|
| MARGIN_BAL | source-persist(权限) | margin:null;log L37-41「您没有接口(margin)访问权限」×5 |
| SH_PE | source-persist(权限) | valuation:{};log L45-48「您没有接口(index_dailybasic)访问权限」×4(含 000001.SH) |
| SHCOMP | N | close=3686.17@20261104 via=akshare_em |
| SZCI | N | 11335.69@20261104 via=akshare_em |
| CHINEXT | N | 2544.73@20261104 via=akshare_em |
| SB_FLOW | source-persist(权限) | southbound:null;log L34「您没有接口(moneyflow_hsgt)访问权限」 |
| SH_AMOUNT | N | 9532.65 亿元@20261104 source=akshare_em |
| SZ_COMPONENT_AMOUNT | N | 10844.29 亿元@20261104 |
| CN_TOTAL_TURNOVER | N | 20376.94 亿元@20261104 |
| FED_FUNDS | observation-在场 | macro_20261104: 3.88@2026-10-01(序列尾 2026-10-01);对照 20261101: 3.75@2026-09-01 |

**分类依据注记(诚实纪律)**: 本轮 tushare 失败呈**两类**: index_daily=「频率超限(5次/天/1次/小时)」(限流类);margin/index_dailybasic/moneyflow_hsgt=「没有接口访问权限」(**权限类,非窗口类**——择时不可解,冻结合同预判的 quota-blocked 场景实为 permission-blocked,如实按 source-persist(权限)登记,不洗为限流)。

## §四 如实偏差

1. **R009-D1 勘误声明(合同 AC-06③ 必含项)**: W2 交付文档 `dev/data-coverage:docs/DATA_W2_DELIVERY.md` §一 L19/L25 关于覆盖审计工具 stdout 的表述——「`--out` 可选,省略时仅打印人类可读摘要到 stdout,JSON 走 stdout 末段」「人类可读摘要语义(stdout 首段)」——**失实**: 实测无 `--out` 时 stdout 为**纯 JSON**(本轮实跑复核: `python3 metric_coverage_audit.py --registry … --data-dir …` 首行即 `{`),不存在人读摘要首段。原 dev/data-coverage 档**不回改**(排除#8),引用以本声明为准。
2. **MARGIN_BAL/SH_PE 真实值未落档**: tushare margin/index_dailybasic 为**权限拒绝**(结构性,非配额窗口)——修复代码面+测试面已完成并离线证明,真实值须待接口权限恢复(积分/付费升级=排除#6 范围)后另轮真实重跑验证;本轮如实 source-persist,不放宽不冒充。
3. **SB_FLOW 无备源**: moneyflow_hsgt 同受权限拒绝;新增备源(如 akshare EM 港股通通道)=新数据源使用,超出本轮授权——**PENDING 建议**: 下一包评估 EM 通道可得性与口径(百万→亿港元换算已在 fact_engine 在案)。
4. **7 个既有红套件(本地)**: test_p02_w3×6+test_p4_fixes 在本地工作树红,基点归因复跑证明与本轮改动无关(09bdd93 无本轮改动同红;R054 CI run 41823658350@09bdd93 全 54 套件 success 在案)——本地环境差异(新闻档案 fixture/月度序列),CI 侧预期不受影响;若 CI 出现红即属上游漂移→情形(b)分流,本轮零当场修改。
5. **W2 清单笔误登记**: W2 债务清单 FED_FUNDS 行「3.75@2025-09-01」与档内直读(3.75@**2026**-09-01)不符,以档内直读为准;原档不回改(排除#8)。
6. **外观性发现(白名单外,登记不实施)**: ①historical_coverage_audit.py L875-895 对含 `balance` 键的新档会把 `margin:balance` 另记一行 unmapped 披露(权威点照记,纯披露冗余);②同工具 L901-904 嵌套 pe_ttm 披露文案「仅300/500/1000」在 000001.SH 入名单后变为过时描述(纯文案);二者零统计影响,如需清理属下一包。
7. **CI dispatch**: 操作者 CHECKPOINT 动作,执行侧未自行 dispatch(合同§一);证据包留占位说明。
8. **占位符解析**: 收到的提示词四占位符均已冻结实值化(BASE/COV-SHA/INV-SHA/BASE-CI-SUITES),无未解析占位,正常执行。

## §五 参考

- 合同: IA-DATA-W3-AC-v1.0(本提示词内嵌全文+冻结章;存档 contracts/IA-DATA-W3-AC-v1.0.md=引擎侧);
- 权威债务清单: dev/data-coverage(06f715b6) docs/DATA_W2_COVERAGE_REPORT.md §四;
- 参考诊断: dev/data-inventory(7cbef4c9) docs/DATA_W1_MISSING_DIAGNOSIS.md(R008;与实码冲突处以代码为准);
- 基点内既有修复: R049(IA-P0-2-W5-DATASRC-B,EM 备源)/R051(W5-EMWIN)/R052(W5-RERUN-4,四源真实重跑)/R007(≥61s 节流,冻结合同重锚定章);
- CI: .github/workflows/offline-tests.yml(tests/test_*.py 通配,新套件自动入,预期 55)。
