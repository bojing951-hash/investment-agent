# IA-DATA-W3 修复报告(逐指标)— DATA_W3_FIX_REPORT

> 工作包: IA-DATA-W3(数据线第2包·修复,合同 IA-DATA-W3-AC-v1.0 FROZEN 2026-11-04)
> 执行分支: `dev/data-w3-fix`(基点 `09bdd937cca348a31a0e67858c35f28fdf32806a` = main,R054 文档笔)
> 权威债务清单: `git show dev/data-coverage:docs/DATA_W2_COVERAGE_REPORT.md`(06f715b6)§四,恰 10 项——
> 计数校验: 10 = MARGIN_BAL(B)+SH_PE(B)+china 通道 7 项 S(SHCOMP/SZCI/CHINEXT/SB_FLOW/SH_AMOUNT/SZ_COMPONENT_AMOUNT/CN_TOTAL_TURNOVER)+FED_FUNDS(S 观察项) ✓ 无分歧。
> 本报告行级引用均以 `dev/data-w3-fix` 尖端实码为准(审计可抽查直读);断点诊断引用=基点 09bdd93 修复前实码或 W2/R008 在案登记。

---

## 〇、修复面总览(改动实体与行级引用)

修复文件(白名单 1M): `scripts/china_market_collector.py`,5 个修复实体:

| # | 修复实体 | 现行行级引用 | 内容 |
|---|---|---|---|
| F1 | MARGIN_BAL 契约键映射 | L464-476(键 `balance` 在 L475) | 成功响应(实含 rzye/rqye)→ `margin.balance`=(Σrzye+Σrqye)÷1e8 亿元 round2;原键 rzye/rqye/rzye_billion 原样保留 |
| F2 | 裸 except 清零(全文件) | L326-332(腾讯日K)/L366-373(yfinance YTD)/L479-483(fetch_margin)/L495-499(_pe_value)/L644-648(新浪rt行解析) | 5 处静默/裸异常路径全部改具体异常类型+留日志(指标标识+类型+摘要);重试/返回语义零变化 |
| F3 | fetch_valuation 双形态+扁平桥接 | L488-500(`_pe_value`)/L503-547(桥接 L534-537,flat 落键 L543-545) | 载荷 pe 双形态(扁平 `pe`/嵌套 `pe_ttm`)兼容;产物并存嵌套 per-index 对象+扁平 `valuation.pe`+`valuation.date`(引擎/快照契约键) |
| F4 | 上证身份对齐 | L219-231(`000001.SH` 在 L225,`SH_PE_IDENTITY` L231) | VALUATION_INDICES 首位纳入 000001.SH(与 A_SHARE_INDICES 对齐);既有 300/500/1000 成员与顺序零变化 |
| F5 | 估值逐只失败留痕 | L540-541 | except 补指数代码+异常类型(原仅名称+消息) |

**字段契约登记(执行前实读)**:
- MARGIN_BAL 消费点 `scripts/fact_engine.py` L364-366(原文): `mg = data.get('margin') or {}; if mg.get('balance') is not None: add("MARGIN_BAL", mg.get('balance'), mg.get('date'))` → 契约字段= `margin.balance`(值)+`margin.date`;快照锚 `scripts/snapshot_builder.py` 'china.margin.balance';注册口径 unit=cny_100m「融资融券余额存量(亿元)」validation.range=[8000,45000]。
- SH_PE 消费点 `scripts/fact_engine.py` L367-369(原文): `val = data.get('valuation') or {}; if val.get('pe') is not None: add("SH_PE", val.get('pe'), val.get('date'))` → 契约字段= 扁平 `valuation.pe`(ratio)+`valuation.date`;快照锚 'china.valuation.pe';注册口径=上证指数整体 PE(TTM) range=[8,40]。
- **balance 合计公式授权**: R008 §1.4-2a 曾要求「经合同确认合计公式与单位后方可由 rzye+rqye 计算」——该前置由本工作包冻结合同 IA-DATA-W3-AC-v1.0 §一(a)(操作者依用户 2026-11-01 代批授权)满足: 明示「fetch_margin 对成功响应(实含 rzye/rqye 键)完成到该契约字段的映射」。合计公式=融资余额+融券余额(注册语义「融资融券余额存量」的唯一同口径展开),单位亿元(注册 unit)。
- **等效方案论证(F4)**: 采用「纳入估值采集名单」而非其他等效(如引擎侧映射嵌套键)——理由: ①名单纳入使采集器直接具备上证 PE 原始数据(身份唯一权威);②引擎侧改映射属白名单外(fact_engine 零改动纪律);③不改变既有指数口径: 300/500/1000 仍按原嵌套形态采集,新增上证为纯增量,旧行为零变化。

---

## 一、逐指标表(10 项 + FED_FUNDS;真实结果指针 → DATA_W3_DELIVERY.md §二/§三 与证据包)

| 指标 ID | W2 状态 | 断点诊断(行级引用) | 处置分类 | 修复内容(行级引用) | 离线测试名 | 真实结果指针 |
|---|---|---|---|---|---|---|
| MARGIN_BAL | B | 双层: ①源端失败 margin:null(W2 表;R008 §1.2 断点①);②结构性键断裂——引擎期望 margin.balance(fact_engine L364-366)vs 采集成功路径只写 rzye/rqye/rzye_billion(基点 fetch_margin L454-459,全文件无 balance 键);③裸 except 吞异常(基点 L462-463)=失败不可归因(R008 U-1) | code-fixed(键映射+日志)+本轮真实采集 source-persist(权限) | F1(L464-476)+F2(L479-483) | test_data_w3_fixes: t1a/t1b(映射+引擎链)/t1c(失败留痕)/t1d(重试语义)/t3a(裸except=0) | source-persist: margin:null;原始错误「您没有接口(margin)访问权限」×5 日期(collection_run.log L37-41)——权限类,非限流窗口类;档内直读 margin=None |
| SH_PE | B | 三层: ①源端失败 valuation:{}(W2 表);②格式断裂——引擎期望扁平 valuation.pe(fact_engine L367-369)vs 采集写嵌套 valuation[code].pe_ttm(基点 fetch_valuation L484-497);③身份断裂——VALUATION_INDICES(基点 L220-224)无 000001.SH 而 A_SHARE_INDICES(基点 L65-72)含之(R008 §2.2 断点②③) | code-fixed(双形态+身份对齐)+本轮真实采集 source-persist(权限) | F3(L488-500/L503-547)+F4(L219-231)+F5(L540-541) | t2a(名单对齐)/t2b(嵌套形态双产物)/t2c(扁平形态)/t2d(身份锁:300 诱饵不冒充)/t2e(上证失败不写扁平键)/t2f(引擎链)/t2g(_pe_value 向量) | source-persist: valuation:{};原始错误「您没有接口(index_dailybasic)访问权限」×4 指数含 000001.SH(collection_run.log L45-48);档内直读 valuation={} |
| SHCOMP | S | a_share_indices 容器在档为空 {}(W2 窗口两日)=tushare index_daily 逐代码失败不写键(基点 fetch_a_share_indices 逐 try/except);W2 窗口代码无备源 | code-fixed(基点内 R049/R051 已修,非本轮新增): tushare 异常→东财 EM 回落(现行 L289-297 调 _fetch_index_em L129-181;61s 闸门 L50/L54-62 零削弱) | 无本轮代码改动(基点交付物);本轮补登记+真实复跑 | test_p02_w5_datasrc_b: T1c(异常→EM)/T2*(回落契约);test_data_w3_fixes: t4b(闸门 61 不变) | **N**: china_20261104.json a_share_indices['000001.SH'].close=3686.17 date=20261104 via=akshare_em(档内直读;collection_run.log L11-12) |
| SZCI | S | 同 SHCOMP(399001.SZ 键缺席) | 同 SHCOMP(基点 R049/R051 EM 回落) | 无本轮代码改动 | 同 SHCOMP(T1c/T2*) | **N**: 11335.69@20261104 via=akshare_em(档内直读;log L14-15) |
| CHINEXT | S | 同 SHCOMP(399006.SZ 键缺席) | 同 SHCOMP | 无本轮代码改动 | 同 SHCOMP | **N**: 2544.73@20261104 via=akshare_em(档内直读;log L17-18) |
| SB_FLOW | S | southbound:null= moneyflow_hsgt 失败 return None(现行 fetch_southbound L408-448);映射口径本身一致(引擎 south_money/100,W2 表在案)——无代码侧确定性断点 | source-side(权限)——单通道 tushare,无备源;新增备源=新数据源(排除#6),登记 PENDING 不实施 | 无(本轮仅受益于既有失败日志 L446「❌ 南向资金: …」) | 无(无代码改动;引擎映射由 test_fact_engine 既有覆盖) | source-persist: southbound:null;原始错误「您没有接口(moneyflow_hsgt)访问权限」(collection_run.log L34);档内直读 southbound=None |
| SH_AMOUNT | S | turnover:null=方案1(tushare)与方案2 双失败(W2 窗口;现行 fetch_turnover L549+) | code-fixed(基点内 R049 B-AC-02 已修): 方案2=东财 EM 双取(现行 L589-628),旧新浪回落已删 | 无本轮代码改动 | test_p02_w5_datasrc_b: T3a/T3b/T3c/T3d/T3e | **N**: turnover.sh_amount_billion=9532.65@20261104 source=akshare_em(档内直读;log L50-53) |
| SZ_COMPONENT_AMOUNT | S | 同 SH_AMOUNT(sz_amount_billion 不可达) | 同 SH_AMOUNT(基点 R049) | 无本轮代码改动 | 同 SH_AMOUNT(T3*) | **N**: 10844.29@20261104 source=akshare_em(档内直读) |
| CN_TOTAL_TURNOVER | S | 同 SH_AMOUNT(sh+sz 双路径不可达) | 同 SH_AMOUNT(基点 R049) | 无本轮代码改动 | 同 SH_AMOUNT(T3*) | **N**: total=20376.94@20261104(=sh 9532.65+sz 10844.29,档内直读) |
| FED_FUNDS | S(观察项) | macro_20261102 键缺席=当日 FRED 单系列失败(macro_collector L201-226 逐系列 try/except);macro_20261101 在场——仅观察诊断,不动 macro_collector(排除#4) | observation | 无(宏观察只读;排除#4) | 无(无代码改动) | observation-在场: 运行日 macro_20261104.json FED_FUNDS=3.88@2026-10-01(序列连续至 2026-10-01,FRED 侧证据=档内 series.dates 尾 ['2026-08-01','2026-09-01','2026-10-01']);对照 20261101 档=3.75@2026-09-01(档内直读)→ 20261102 缺席=FRED 瞬时失败已自愈,10 月值已按月频节奏发布;不回填(排除#5)。**勘误登记**: W2 清单原文「3.75@2025-09-01」系笔误,档内直读 date=2026-09-01,以档内直读为准(不改 W2 档) |

**处置分类汇总**: code-fixed(本轮)=MARGIN_BAL 键映射+SH_PE 双形态/身份(2 项);code-fixed(基点 R049/R051 已修,本轮登记+真实复跑证实)=SHCOMP/SZCI/CHINEXT/SH_AMOUNT/SZ_COMPONENT_AMOUNT/CN_TOTAL_TURNOVER(6 项);source-side(权限)=SB_FLOW(1 项,另 MARGIN_BAL/SH_PE 真实采集层同受权限阻断);observation=FED_FUNDS(1 项)。

---

## 二、裸 except 清零明细(AC-01(b))

修复前(基点 09bdd93)全文件异常路径清点: 裸 `except:` ×1(fetch_margin 基点 L462-463)+ 静默 `except Exception`(仅 continue/pass/return None 无日志)×3(基点 _tx_kline_rows L322-324 / _fetch_hk_yfinance 内层 YTD L362-363 / _parse_sina_rt_line L595-596)+ 数值 coercion 无日志 ×0(本轮新增 _pe_value 的 L497-499 自带日志)。已全部修复,修复后:

- 裸 `except:` 计数=0(t3a 源级锁: 行首正则 `^\s*except\s*:` 零命中;grep 可复核);
- 全文件 15 个 except 句柄逐一路径留日志(标识+类型/摘要)——本轮改动 5 处(L326-332/L366-373/L479-483/L495-499/L644-648),其余 10 处基点已有日志未动;
- 真实运行验证: 采集日志中 margin×5 日期/估值×4 指数/南向/指数×6/成交额 全部失败均带类型与摘要(collection_run.log L11-52)——W2 时代「失败不可归因」(R008 U-1/U-4)由本轮修复终结。

## 三、离线测试清单(tests/test_data_w3_fixes.py,19 用例,全绿 exit=0)

- T1MarginBalanceMapping: t1a 成功响应→balance 键+原键保留/t1b 引擎消费链/t1c 失败留痕(标识+类型+摘要)/t1d 5 日重试语义;
- T2ShPeValuation: t2a 名单身份对齐/t2b 嵌套形态双产物/t2c 扁平 pe 形态/t2d 身份锁/t2e 上证失败不写扁平键/t2f 引擎消费链/t2g _pe_value 七向量;
- T3NoSilentExceptions: t3a 源级裸 except=0/t3b 腾讯日K/t3c 新浪rt解析/t3d yfinance YTD/t3e 估值逐只——四静默路径留痕+返回语义零变化;
- T4SourceFreezeLocks: t4a A_SHARE_INDICES 冻结/t4b 61s 闸门常量冻结/t4c EM_MAP 全覆盖。
- 负向敏感性: 回退修复至基点版 collector 后同套件 15 红(11 FAIL+4 ERROR, negative_sensitivity_base.log),恢复后 19 绿——测试真实锁住修复。

## 四、真实采集与覆盖复检摘要(指针)

- 单次诚实运行: `python3 scripts/china_market_collector.py`(既有入口;代理环境 NONE;≥61s 闸门全程生效,log 中 7 次「⏳…等待~60s」),exit=0,耗时约 11 分钟(12:08:23Z–12:19:4xZ);
- 写入边界: data/daily 24 文件恰 1 变=china_20261104.json(运行日档更新),其余 23 文件 sha256 逐字节不变(anchor 清单 diff);
- 覆盖审计 pre/post(工具 sha256=765cf184…与 06f715b6 分支字节一致,禁改): 机械计数零 delta(PRESENT 73/DERIVED_READY 5/PATH_NULL 2/KEY_ABSENT 1,non_present=[SB_FLOW,MARGIN_BAL,SH_PE] 双次一致);
- 相对 W2 基线(N71/S8/B2/C0/U0)主状态迁移与归因: 详见 DATA_W3_DELIVERY.md §三。
