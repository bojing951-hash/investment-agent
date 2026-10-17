# Phase 0 基线审计 — 金融事实引擎重构前 (2026-10-17)

基线 commit `f8281c8`（dev/fact-engine 分支起点）。方法：逐文件通读 13 个核心脚本 + 测试套件 + README；
真实运行产物审计延后至 Phase 5（live 数据在 `/Users/cast/AI内容/🤖_AI投资项目/每周宏观追踪/investment-agent/`，
本仓库 data/ 为 gitignored，克隆内无历史产物）。

## 1. 现行数据流（改造前）

```
launchd 07:00 → run_daily.sh → run_weekly.py (10步顺序, 单步失败不阻断)
  1 global_market_collector  yfinance 37资产 1y日K → data/daily/global_YYYYMMDD.json/.md
  2 china_market_collector   腾讯/新浪/akshare/Tushare → data/daily/china_YYYYMMDD.json
  3 macro_collector          FRED 21序列 → data/daily/macro_YYYYMMDD.json
  4 news_collector(非关键)   Finnhub+RSS → GLM摘要 → data/news/news_{raw,summary}_YYYYMMDD
  5 rate_expectations        ZQ期货+FRED → data/daily/rate_economy_YYYYMMDD.json/.md
  6 macro_scorecard          自采FRED → data/daily/scorecard_YYYYMMDD.json/.md
  7 correlation_calc(非关键) yfinance → data/daily/correlation_YYYYMMDD.md
  8 data_assembler           拼最新文件 → data/weekly/data_pack_YYYYMMDD.md
  9 data_validator           锚点提取 → data/daily/anchors_YYYYMMDD.json
 10 daily_prediction_obs     锚点→观察记录回写 allocation_views.json

launchd 周六08:00 → report_generator.py
  load_prompt/framework/theses/prev_report/tech_notes/news/data_pack/anchors
  → GLM流式生成周报(八节) → validate_generated_report(锚点校验)
  → classify PASS/DEGRADED/FAIL → apply_status_updates(thesis/views回写)
  → pending_completed_month/quarter → 月报/季报子进程
```

**结构问题**：第8步之前无任何统一事实层——每个采集器自带指标定义/单位/日期语义；
第4-7步属"研究引擎"却直接裸采数据（Layer 4 → Layer 1 直连，绕过一切口径控制）；
第9步的"锚点"是把第1-7步输出**全部数值拍平**得到的，与被校验对象同源（自证）。

## 2. 指标与数据源清单（现状）

| 来源 | 指标 | 备注 |
|---|---|---|
| yfinance | SPX/NDX/RUT 指数, NVDA/AAPL/MSFT 个股, TLT/HYG/IEF/SHY/LQD 债券ETF, DXY/EURUSD/GBPUSD/JPY/CNY 汇率, GC=F/SI=F/CL=F/BZ=F 期货, GLD/USO, EEM/EZU/FEZ/EWU/EWG/EWJ/INDA/FXI, BTC-USD, ^VIX | 期货/ETF/指数混在无身份元数据的平铺命名空间；`auto_adjust=True` 使含股息资产(如TLT)的Close为复权价 |
| FRED (macro_collector) | BAML×5利差, DGS2/10/30, DFII5/10, T5YIE/T10YIE, T10Y2Y, FEDFUNDS, CPIAUCSL, PCEPILFE, UNRATE, PAYEMS, CPILFESL, AHE, ICSA, WTISPLC | 无 release_date/retrieved_at 字段；WTISPLC(月度现货)与CL=F(期货)双身份同名WTI无对账 |
| FRED (macro_scorecard 自采) | UMCSENT, RSAFS, INDPRO, CES0500000003, UNRATE… | 绕过 macro_collector 第二条FRED通道，口径独立 |
| FRED (rate_expectations 自采) | DFF, DFEDTARU/L, FEDFUNDS, UMCSENT, RSAFS, PAYEMS, INDPRO, UNRATE, JTSJOL | 第三条FRED通道 |
| Tushare/akshare/腾讯/新浪 | 上证/深成/创业板, 恒指/国企, HSAHP, 南向, 两融, 估值, 成交额 | 多通道冗余但无对账语义 |
| CME (yfinance) | ZQ=F + ZQ{月}年.CBT ×10 | 期货合约含义(月均利率)未按合同语义处理 |
| Finnhub+RSS | 新闻标题→关键词分类→GLM摘要 | 事件无结构化字段；url采集后即丢弃 |

## 3. 独立计算函数清单（每个都自定口径，无一共享）

| 函数 | 位置 | 口径问题 |
|---|---|---|
| `calc_metrics` | global_market_collector.py:130 | week=iloc[-6]固定偏移; MTD/YTD基准=当期**第一个收盘**(spec要求期前收盘); 数据不足时chg=0.0静默伪造 |
| `compute_series_changes` | macro_collector.py:91 | 已有频率/单位纪律(P0-3/P1-3轮成果)但仅覆盖FRED月频；_pick窗口21-45天可跨修订 |
| `calc_derived` | macro_collector.py:243 | REAL_SHORT=2Y名义−**5Y**盈亏平衡(期限错配,§5.3) |
| `_hk_metrics_from_daily` | china_market_collector.py:146 | week=closes[-5]; ytd=当年首收盘(与spec口径相反) |
| `fetch_turnover` | china_market_collector.py:345 | 深市=399001深证成指amount冒充全市场; akshare降级只采上证但输出无scope的total; volume_billion字段装成交额 |
| cuts_25bp 计算 | rate_expectations.py:~232 | `(月均合约隐含−当前有效利率)/0.25=降息次数` — 分子口径错配(月均vs时点), 除数无概率语义 |
| implied rate | rate_expectations.py | implied=100−price 正确,但未标注"当月日均"合同语义 |
| 相关性 | correlation_calculator.py | `df.dropna().pct_change().corr()` — 无日历对齐无样本数; 输出硬编码因果解读(FXI=中国, TLT价格corr=美债, 正相关=股债同跌) |
| scorecard | macro_scorecard.py | 阈值打分+体制判定; 缺指标静默计0分; 无"数据不足不可判"状态 |
| anchors 提取 | data_validator.py `extract_anchors_from_data` | 拍平全部数值(含week_chg/ytd_chg等派生值)当锚点 — 报告与JSON同源自证 |
| 月度聚合 | monthly_review.py | 独立的月初/月末/高低聚合 |
| 季度聚合 | quarterly_outlook.py | 又一套区间聚合 |

## 4. 已确认缺陷（改造前真实错误，均有代码位置）

### 根因A — 无权威事实源（指标身份/口径各自定义）
- A1 `WATCHLIST` 平铺命名：GOLD=GC=F(期货)、TLT(ETF)与UST_10Y(收益率)并存无身份区分 — global:48-94
- A2 WTI 双身份：CL=F(全球采集) vs WTISPLC(宏观采集)，同名两个数 — global:66 / macro:40
- A3 深市成交额口径错误 + 降级通道口径静默收窄 — china:345-414
- A4 成交额/成交量字段混用 `volume_billion` 装金额 — china:379

### 根因B — 无统一研究截止与日历
- B1 `find_latest_file` glob最新≠数据最新（周一跑批读到上周五文件也当"最新"）— data_assembler.py
- B2 观测vs发布vs采集时间无区分：FRED序列无release_date，9月CPI(10月中发布)可混入9月末快照 — macro_collector.py
- B3 周窗口口径不一：global用iloc[-6]、china HK用closes[-5]、correlation用尾5行 — 三处各自定义
- B4 YTD/MTD基准错位：当期首收盘 vs spec要求的期前末收盘 — global:147-158, china:146

### 根因C — 校验同源自证
- C1 锚点=被校验数据同源拍平（含派生值），JSON错则报告跟着错，校验通过无意义 — data_validator
- C2 模糊最近锚点 `min(anchors, key=|diff|)`：错值可匹配到最近锚点蒙混 — data_validator
- C3 首次匹配 `report_matches[0]`：只查第一处出现，后续错误数字漏检 — data_validator

### P0级口径错误（spec逐条对应）
- §5.4 利率期货：假"降息次数"计算 — rate_expectations:~232
- §5.3 期限错配：REAL_SHORT 2Y−5Y — macro_collector:252
- §9 评分卡：缺指标计0分+无数据不足态；自采FRED绕过采集层 — macro_scorecard
- §10 相关性：代理未标注、因果语言、无对齐/样本数 — correlation_calculator
- §11 新闻：国家名→虚构名替换(Iran→Country-A/产油国A等38条规则)；事件无event_id/发布时间/url — news_collector:223-241,343-363
- §4.3 价格vs全收益：auto_adjust复权价当市场价 — global:107

### 复现状态
代码级缺陷已全部定位（上表）。真实数据复现（用live产物验证报告错误的传播）在 Phase 5 执行：
live `output/weekly/weekly_report_20261009.md`、`20261016.md` 已存在；data_pack/anchors/validation log 按实况审计，缺失如实报告。

## 5. 保留资产（复用清单）

- **采集层全部**（global/china/macro/news/rate的API通道）— Layer 1 保持
- `daily_prediction_observer` 验证/写入隔离+幂等+新鲜度门禁 — 换数据源(锚点→快照)后复用
- `allocation_engine` 1546行状态机（评级门禁/证据分级v2/触发器/预测生命周期）— 接口不动，输入换快照
- monthly_review/quarterly_outlook 的期间完结判定与聚合框架 — 输入换快照
- 11套离线测试 579断言 — 回归基线
- GLM流式调用通道、八节结构、launchd调度

## 6. Phase 1 输入（据此设计）

1. Metric Registry 必须覆盖：上表全部指标 + 身份字段区分指数/ETF/期货/现货/收益率/利差/汇率/加密
2. 日历模块需：美股/美债/商品/A股/港股/FX/crypto 各自交易日规则（结算差异）
3. 统一收益引擎替换 §3 全部12个计算点（明确基准价/日期/日历/复权/价格vs全收益）
4. 快照须记录：release 语义缺失时的保守标注（FRED无release_date→"发布时间未知,按观测日保守处理"）
5. Gate A 在快照构建时执行（§8 12类校验），Gate B 换锚点源为快照事实+全文覆盖校验
