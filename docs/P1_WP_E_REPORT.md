# IA-P1-WP-E 执行报告(REPORT)

> **状态: v1.3 续作实施轮·完整交付形态**——(d) 停止轮(2026-11-06T09:4xZ UTC)后,操作者以合同 **IA-P1-WP-E-AC-v1.3** §十三处置章授权续作(同分支续笔,基点零重锚);本文件承载两轮笔迹: (d) 登记轮 §零.1-§零.9 原文保留(历史记录),v1.3 实施轮新增 §零.10-§零.16(见 §零.10 开工核验)。停止轮状态行原文: 「(d) 规格冲突合法停止轮·仅登记件执行(零代码开发);合同 IA-P1-WP-E-AC-v1.2;分支 dev/p1-impl-e(自 BASE-P1E 切出)」。
> 本文件原为 (d) 形态唯一登记件;v1.3 轮 A 类 3 件齐备(本件扩写+A2 DELIVERY+A3 tests/test_p1_wp_e.py,见 §零.3 更新注记与 §零.16)。
> 数值标注纪律(合同 §5.3): 本文逐值 `[实取·来源]` 或 `[示意·非实取]`。
> 边界声明: 日期/SHA/结构编号按合同 §六取证纪律登记;引用 DESIGN/INVENTORY/测试文件均为基线工作树实读(blob 锚见 §零.1),非注入摘要转述。

---

## §零.1 契约锚与开工核验实录(步骤 0-4 输出)

| 项 | 值 | 核验方式与结果 |
|---|---|---|
| 时序自检 | 工作树 clean,`git status` 空 | [实取·2026-11-06T09:13:18Z 本机] 步骤0 通过 |
| BASE-P1E | `ee66f3a92f7854c9db308bc604e7707ed49e3bee` | [实取·`git ls-remote origin main` 2026-11-06T09:13Z] 全值比对一致 |
| dev/p1-design 尖端 | `049ec978523dec659ba47f140bf41669604de24f` | [实取·`git ls-remote origin dev/p1-design` 同刻] 全值一致;禁锚 c9626633 未混入 |
| BRANCH-SET | 46 支 | [实取·`git ls-remote origin 'refs/heads/*'` 同刻计数=46] 与冻结章 §十一.3 v1.2 全表逐一对照零漂移(含 dev/p1-gap08@9369a15、main@ee66f3a9;45 支 v1.1 历史表尖端全部不变) |
| 占位符核验 | 3 处实值已解析 | 合同 §0 逐目视核验: BASE-P1E/BASE-P1E-CI-SUITES=74/BRANCH-SET=46 均为实值形态,无占位符标记 |
| 门②信号 | 已开启 | 操作者派发本提示词=门②已开启的唯一信号(合同 §0 明文;执行席不自行判断) |
| 分支切建 | `dev/p1-impl-e` 自 `ee66f3a9…` | [实取·`git checkout -b dev/p1-impl-e ee66f3a92f7854c9db308bc604e7707ed49e3bee`,HEAD=ee66f3a9…全值] |
| 设计在场核验①可达性 | exit 0 | [实取·`git merge-base --is-ancestor 049ec978… HEAD`] 049ec978 在 BASE-P1E 祖先谱系内 |
| 设计在场核验②三件 blob 等值 | 全等值 | [实取·`git ls-tree` 双侧输出]: P1_DATA_NEEDS_INVENTORY=`df79c06f66c368d93159b7a3b46852b6fcb9b196`/P1_DESIGN=`13b263cf3139d420e01bf1e154b03ce85a35db4c`/P1_DELIVERY=`314c2644a51f2f575a90253580cb56346e2f93b6`,HEAD 侧与 049ec978 侧逐一相同,且与冻结章 §十一.2③ 登记值一致 |

## §零.2 规格抄录(AC-01 锚;逐字抄录自 `docs/P1_DESIGN.md` §六 L173,基线工作树实读)

**定位**: §六「工作包拆解(验收要点=草案,正式 AC 由主Agent后续轮拟定,此处不冻结)」表 @L165(节标题行),表头 L167,WP-P1-E 行=**L173** [实取·docs/P1_DESIGN.md L165-L175 逐行实读]。同族前列行 A=L169/B=L170/C=L171/D=L172。E 行与前列行可区分: E 行为唯一 CN 面行(范围列 G-P1-10..18;依赖列明文「**依赖用户授权**(china 采集器冻结在案)」;承接 GAP-P1-04/05 @L152-L153)——与冻结章 §十一.2① 三项实读义务判定一致。**无同族后继行(本包=族末包)**。

**L173 原文逐字抄录**:

```
| WP-P1-E CN 面修复与宏观扩展 | 断点修复+CN 宏观接入 | G-P1-10..18(备源切换与新宏观接口) | **依赖用户授权**(china 采集器冻结在案);tushare 积分/e-Stat→PENDING 报批,不为唯一路径 | ① 断点修复后 `china_YYYYMMDD.json` 对应节非空【数据档引用】② 源端失败注入测试(限流→MISSING 披露)【测试】③ 宏观新指标 registry 条目+单测【测试/CI】 |
```

**四要素逐字分解**(表格单元格切分,字符零增删):

- **目标**(L173 列2): `断点修复+CN 宏观接入`
- **范围**(L173 列3): `G-P1-10..18(备源切换与新宏观接口)`
- **依赖**(L173 列4): `**依赖用户授权**(china 采集器冻结在案);tushare 积分/e-Stat→PENDING 报批,不为唯一路径`
- **验收要点草案**(L173 列5): `① 断点修复后 \`china_YYYYMMDD.json\` 对应节非空【数据档引用】② 源端失败注入测试(限流→MISSING 披露)【测试】③ 宏观新指标 registry 条目+单测【测试/CI】`

**范围漂移注记承接**(冻结章 §十一.6,工作树在场实证): G-P1-10/12 已由 R049 方案B 承载、G-P1-13 已由 R058 承载 [在场实证·data/daily/china_20261104.json: a_share_indices 6 键/turnover 8 键非空=实取·2026-11-06 读档;三交付=R049/R058 对照同源,禁重实现]→**本包剩余实施面=G-P1-11+G-P1-14..18** [在场实证·同档: `margin`=null/`valuation`={}/macro 节键缺席]。

## §零.3 交付文件清单登记(附录A §零(ii) 固定推导规则)

DESIGN L173 范围列=模块级(`G-P1-10..18(备源切换与新宏观接口)`),非文件级→按固定推导规则生成:

| # | 路径 | A/M | DESIGN 依据 |
|---|---|---|---|
| 1 | docs/P1_WP_E_REPORT.md | A | 必含件(附录A §零(ii));本件((d) 轮建,v1.3 轮扩写) |
| 2 | docs/P1_WP_E_DELIVERY.md | A | 必含件(附录A §零(ii));**(d) 轮零交付未建→v1.3 轮已建(§零.16)** |
| 3 | tests/test_p1_wp_e.py | A | 含代码→必含(附录A §零(ii));**(d) 轮零开发未建→v1.3 轮已建(§零.16)** |
| M-a | scripts/china_market_collector.py | M | 冻结章 §十一.4(a): 域限=①G-P1-11 margin/valuation 备源切换(fetch_margin@L509/fetch_valuation@L562 现锚 [实取·基线工作树实读,行号与冻结章登记一致])②G-P1-14..18 宏观采集函数新增;其余函数域零触碰 |
| M-b | config/metric_registry.json | M | 冻结章 §十一.4(b): 仅 G-P1-14..18 新宏观条目纯新增;既有条目键值零改动 |

- **条件类 (c) 判定(登记)**: 判定宏观采集函数落 M-a 域内(scripts/china_market_collector.py 新增函数),不建独立 `scripts/cn_macro_collector.py`→**(c) 不触发(零 diff=条件类成立的登记形态,沿 R046 (d) 先例)**。判定依据: ①DESIGN L173 范围列字面「新宏观接口」未指定独立模块;②§四 L124 复用对齐表对新增采集脚本仅列 `jp_market_collector.py`/`ea_market_collector.py`(候选名,A/D 包域),CN 面零「新增脚本」字样;③冻结章 §十一.4(a) 域限表述将「G-P1-14..18 宏观采集函数新增(LPR/CPI/PPI/PMI/社融增量+新增贷款/7天逆回购)」直接登记于 china_market_collector.py 域内。
- **结构约束(iii) 预检**: A 类 3 路径与 `git ls-files` 零重合 [实取·2026-11-06 `git ls-files` 对照: docs/P1_WP_E_REPORT.md、docs/P1_WP_E_DELIVERY.md、tests/test_p1_wp_e.py 均无同名文件在场];必含件齐((d) 轮 1/3→**v1.3 轮 3/3** [实取·v1.3 轮工作树在场]);k(完整交付形态)=**3** A 行。
- **上游在场交付件登记(对照同源锚)**: WP-P1-A/B/C/D REPORT+DELIVERY 八件在场 [实取·`ls docs/ | grep P1_WP`,8 件];上游清单以各包 REPORT §零 登记清单为对照同源(本包依赖面=WP-A registry 结构 [实读·docs/P1_WP_A_REPORT.md §零.1-§零.2]、WP-B fact_engine china 消费面 [实读·scripts/fact_engine.py L301-L311/L375-L378])。

## §零.4 P1 特有纪律登记(实读锚定;节号登记)

实读 E 行及其所引各节,载明的 P1 特有纪律逐条登记:

| # | 纪律 | 节号锚 | 登记 |
|---|---|---|---|
| 1 | 红线筛查(全包通用): 全部包不含 LIVE 部署、launchd 改动、交易或收益承诺、绕开快照+门禁直读原始数据的设计;新数据一律经快照进入研究面 | §六 L175 | 承接;本包 (d) 停止零开发,零触犯面 |
| 2 | 快照+门禁不可绕开(LIVE 禁写/禁交易/数据不足不填0 三红线) | §七 L179-L182 | 承接;采集档本身不入研究档案(衔接设计 §四 L141: 唯一入口=研究快照) |
| 3 | 付费/凭证源只登记 PENDING 候选,禁直接依赖(tushare 积分接口等);任何 WP 不得将其设为唯一路径 | §三(b) L75 | 承接;本包主路=免费公开源(akshare 东财/央行公告页类,循预授权③),tushare 积分侧 PENDING 不碰(门②范围语义) |
| 4 | 免费公开源循预授权③直用;设计采集频率=每日 1 次 | §三(b) L73 | 承接(实现面因 (d) 未启动) |
| 5 | 降级路径: 采集/源层源不可得→sources_status 记 MISSING/READ_FAIL→当日档该节键缺席(非0) | §三(c) L81 | 承接;要点②「限流→MISSING 披露」即此纪律测试面 |
| 6 | 引擎层序列不足→available:false 绝不回填0;月频未发布≠缺失(月频窗=60天) | §三(c) L82 | 承接(G-P1-14..17 月频条目 freshness 参照=60天窗 [实取·config/metric_registry.json CPI 条目 freshness.max_calendar_lag_days=60 同款]) |
| 7 | CN 面修复先于 CN 宏观扩展(优先级判断依据) | §三(b) L77 | 承接;G-P1-11 备源切换与 G-P1-14..18 同包实现,实现序以 G-P1-11 先 |

未载明面判定: E 行及所引节未载快照路径/研究状态保护类特有纪律(本包触面=采集层+registry,不触快照/研究状态档;快照面=WP-B 域已闭合)——判定依据=§六 L173 行内+§三(b)(c)+§七 L179-L182 全文实读,无快照路径/状态保护条款落 CN 采集面。

## §零.5 DP 登记判定(R020-D5 语义承接,P1 源=实读)

实读 §二(L24-L31)决策点节+E 行及所引节:

- **§二 载明 DP-1..DP-4,节标题明文「登记型决策点(先登记后成文;最终确认保留给用户/后续包)」**=四条均登记型,非确认型。
- **E 行触面所引**: DP-4(CN 面拆包,§三(b) L76)——定值已由排期落地=独立拆包 WP-P1-E(本包在场即定值实现形态);DP-2(源优先级,§三(b) L81 备源次序)——本包 CN 面定值=免费公开源主路(akshare 东财/央行公告页类)+tushare 积分侧 PENDING 不碰(门②范围语义,合同 §十一.5);DP-1/DP-3=非本包触面。
- **确认型 DP**: E 行及所引节零确认型 DP 编号载明;G-P1-11 tushare 积分侧=确认型面,已由门②整体承载(§十一.6 注记「执行席不得自决实施 tushare 调用」),本包零自决。
- **登记结论**: 本包无新增自决 DP;§二 DP-4/DP-2 涉本包定值如上登记。实现参数(G-P1-14..18 条目 metric_id/单位/频率/值域等)按纪律应于开工首步登记定值→(d) 轮以**建议稿**形态登记于 §零.6B;**v1.3 续作轮开工首步已按 §十三.3 定夺升级为终值表(§零.6A),登记先于运行、登记后零回改**。

## §零.6 G-P1-14..18 registry 条目(§零.6A 终值表[v1.3 登记定值·登记先于运行]+§零.6B 建议稿存档[(d) 轮])

### §零.6A 终值表(v1.3 处置章 §十三.3 授权: 建议稿为起点、终值数据驱动定值;本表=开工首步登记定值,登记后零回改)

**八条目公共字段**(8/8 同值,先于逐条表登记): `source='china_market_collector'`/`calendar='cn'`/`economy='CN'`/`economy_rule='P1:calendar=cn'`/`market_seat='onshore_local'`(t1b 分类器 P1 首中+onshore 同型 [实取·tests/test_p1_wp_a.py L47-48/L92 基线实读])/`criticality='important'`(非 core,Gate A 分级不动)/`status='active'`(STATUS_VALUES 无 'pending' [实取·scripts/registry_semantics.py L175];v1.3 域化 active 计数随迁 93→93+N 的载体)/`value_type='level'`(VALUE_TYPE_VALUES 在册值,零 review 触发 [实取·scripts/registry_semantics.py L180-184])。**identity 分型**: 6 条 macro_rate/macro_index/policy_rate 携 `identity={'instrument':'macro_series','adjustment':'none'}`(INSTRUMENT_BY_CLASS 允许值 [实取·scripts/registry_semantics.py L126-128]);2 条 flow(CN_SF_FLOW/CN_NEW_LOANS)identity 缺席(SB_FLOW 先例 [实取·config/metric_registry.json L2216-2241];flow 类 instrument 允许集=空 [实取·scripts/registry_semantics.py L135])。

| # | metric_id(终值) | display_name | asset_class | frequency | unit | source_symbol(终值) | range | freshness |
|---|---|---|---|---|---|---|---|---|
| 1 | CN_LPR_1Y | 贷款市场报价利率(LPR)1年期 | macro_rate | monthly | percent | macro_china_lpr.LPR1Y | [1,10] | 60+月频注记 |
| 2 | CN_LPR_5Y | 贷款市场报价利率(LPR)5年期 | macro_rate | monthly | percent | macro_china_lpr.LPR5Y | [1,10] | 60+月频注记 |
| 3 | CN_CPI_YOY | 居民消费价格指数(CPI)同比 | macro_index | monthly | percent | macro_china_cpi_yearly.今值 | [-2,10] | 60+月频注记 |
| 4 | CN_PPI_YOY | 工业生产者出厂价格指数(PPI)同比 | macro_index | monthly | percent | macro_china_ppi_yearly.今值 | [-10,15] | 60+月频注记 |
| 5 | CN_PMI_MFG | 制造业PMI | macro_index | monthly | index_point | macro_china_pmi.制造业-指数 | [30,70] | 60+月频注记 |
| 6 | CN_SF_FLOW | 社会融资规模增量 | flow | monthly | cny_100m | macro_china_shrzgm.社会融资规模增量 | [-30000,150000] | 60+月频注记 |
| 7 | CN_NEW_LOANS | 新增人民币贷款 | flow | monthly | cny_100m | macro_china_new_financial_credit.当月 | [-30000,120000] | 60+月频注记 |
| 8 | CN_OMO_7D | 央行7天期逆回购利率 | policy_rate | **daily**(v1.3 裁决) | percent | **PENDING**(见偏离①) | [0.5,5]+max_week_abs_move=1.0 | 10 |

**calc/release_semantics 终值**(逐条,registry 落值与下文 1:1):
1-2. calc=`akshare macro_china_lpr(东方财富)TRADE_DATE/LPR1Y(或 LPR5Y)列最新观测(1年/5年期 LPR,%)`;release_semantics=`LPR 每月20日 09:15 公布(节假日顺延);月频:观测日=发布日,未发布≠数据缺失` [端点锚·实取·akshare 1.18.47 安装包源码离线实读: 列名 TRADE_DATE/LPR1Y/LPR5Y/RATE_1/RATE_2,东财源,升序返回]。
3. calc=`akshare macro_china_cpi_yearly(金十数据)「今值」列最新观测(全国 CPI 当月同比,%)`;release_semantics=`国家统计局每月 9-10 日发布上月值;月频:观测日=统计期(月),未发布≠数据缺失` [端点锚·实取·同源码实读: 列名 商品/日期/今值/预测值/前值,金十源]。
4. calc=`akshare macro_china_ppi_yearly(金十数据)「今值」列最新观测(全部工业品 PPI 当月同比,%)`;release_semantics 同 3(每月 9-10 日同场发布) [端点锚·实取·同源码实读: 列名同 3]。
5. calc=`akshare macro_china_pmi(东方财富)「制造业-指数」列最新观测(国家统计局制造业 PMI)`;release_semantics=`国家统计局每月末发布当月值;月频:观测日=统计期(月),未发布≠数据缺失` [端点锚·实取·同源码实读: 列名 月份/制造业-指数/制造业-同比增长/非制造业-指数/非制造业-同比增长,东财源;月份列「2026年10月」中文格式→采集函数 _norm_month 归一]。
6. calc=`akshare macro_china_shrzgm「社会融资规模增量」列最新观测(当月新增社融,亿元人民币;月度流量非存量)`;release_semantics=`人民银行每月 10-15 日发布上月增量;月频:观测日=统计期(月),未发布≠数据缺失` [端点锚·实取·同源码实读: 列名 月份/社会融资规模增量/其中-人民币贷款…,商务部转载源]。
7. calc=`akshare macro_china_new_financial_credit(东方财富)「当月」列最新观测(新增人民币贷款当月值,亿元人民币;月度流量非存量)`;release_semantics 同 6 [端点锚·实取·同源码实读: 列名 月份/当月/当月-同比增长/当月-环比增长/累计/累计-同比增长,东财源]。
8. calc=`人民银行公开市场业务交易公告 7 天期逆回购中标利率(操作利率,有效利率口径;akshare 1.18.47 无逆回购接口→条目=身份预注册,公告行解析函数已随包交付[可注入纯函数],源接线=PENDING)`;release_semantics=`央行操作室每交易日 09:20 前后披露交易公告(决议日不定期);frequency='daily'=v1.3 处置章 §十三.2 裁决(有效利率形态,ECB_DFR/ECB_MRO 先例),决议日语义由本注记承载、不扩 FREQUENCY_VALUES;源未接线,数据缺席按 L58 纪律处理` [缺席依据·实取·akshare 1.18.47 安装包源码 grep「逆回购/repo_rate/OMO」零命中]。

**建议稿→终值偏离登记**(逐项理由;§十三.3 义务):
- **偏离①(唯一实质偏离)**: G-P1-18 CN_OMO_7D `source_symbol='PENDING'`(建议稿未列端点列锚,INVENTORY 该行亦无免费现成接口锚 [实取·docs/P1_DATA_NEEDS_INVENTORY G-P1-18 频率列仅「决议日不定期」])——依据: akshare 1.18.47 源码离线 grep 逆回购零命中 [实取];处置=JP_CPI_TOKYO_YOY 身份预注册先例 [实取·config/metric_registry.json L2701-2731](active 条目+PENDING 符号+诚实数据缺席),并随包交付可注入纯解析函数(公告行→行结构化),源接线留后续轮;采集默认装载器返回 None+PENDING 披露,不造数。
- 其余 8 项 metric_id/unit/frequency/值域与建议稿一致(§十三.3 定夺=建议稿为实现起点,终值数据驱动=端点列名与 INVENTORY 锚定后零漂移);G-P1-18 frequency 由裁决章定值 'daily'(裁决承载,非执行席自决)。

**N=机器清点登记**: 实现后 registry 实况清点 N=8(§零.11 复核)→域化迁移值: len 94→**102**/active 93→**101**/version '2.2.0'→**'2.3.0'**/聚合 CN 10→**18**(其余 economy 键不动)/vintage_additions 13→**21**(JP4∪NEW9∪CN8)。断言迁移值与 registry 实况 1:1(实现后机器清点复核,§零.13 登记)。

**结构镜像与值域核验**(登记): economy='CN' 不扩值域 {'CN','EA','GLOBAL','HK','JP','US'} [实取·基线 registry 值域聚合,v1.2 处置章 ⑤ 预核在案];月频宏观先例=EA_HICP_YOY(freshness 60+月频注记) [实取·config/metric_registry.json L2893-2923];policy_rate daily 先例=ECB_DFR(range+max_week_abs_move+freshness 10) [实取·同 L2765-2795];macro_rate 类单位纪律=percent [实取·scripts/registry_semantics.py L170];validate_registry 零 error 零 review 预检=全字段入册词汇(§零.11 机器复核)。

### §零.6B 建议稿存档((d) 轮原文;已被 §零.6A 终值表承接,[示意·非实取] 标注维持历史时点语义)

| G-P1 | 建议 metric_id(候选) | frequency 候选 | unit 候选 | 备注 |
|---|---|---|---|---|
| 14 | CN_LPR_1Y / CN_LPR_5Y | monthly | percent | 每月20日发布(INVENTORY G-P1-14) |
| 15 | CN_CPI_YOY / CN_PPI_YOY | monthly | percent | [示意] |
| 16 | CN_PMI_MFG | monthly | index_point | 官方制造业 PMI [示意] |
| 17 | CN_SF_FLOW / CN_NEW_LOANS | monthly | cny_100m | 社融增量/新增人民币贷款 [示意] |
| 18 | CN_OMO_7D | 见备注 | percent | 「决议日不定期」[实取·INVENTORY G-P1-18 频率列];registry 现行 frequency 值域={daily,monthly,weekly} [实取·基线 registry 94 条目聚合]——**需 v1.3 裁决**: 新增 'irregular' 值域(触 registry_semantics 验证面=白名单外)或归 monthly(口径近似,失真登记)——**裁决已落: §十三.2='daily',两候选路径均不采** |

建议条目数=8 [示意→终值确认=8];若成案,聚合 economy 计数 CN 10→18 [示意→终值确认=18];economy='CN' 不扩值域 {'CN','EA','GLOBAL','HK','JP','US'} [实取·基线 registry 值域聚合,与 v1.2 处置章 ⑤ 预核一致,g10 断言不受影响]。结构镜像参照: 月频宏观条目 FED_FUNDS/CPI [实取·基线 registry 条目形态]、WP-A 新条目 JP_CPI_TOKYO_YOY(身份预注册+数据缺席合法形态) [实取·基线 registry]。

## §零.7 (d) 规格冲突合法停止——结构冲突详情(停止定性证据)

**冲突三角**(在合同授权域内不可同时满足,三路必违约):

1. **DESIGN L173 要点③(冻结规格)+M 面 (b) 授权**要求 registry 宏观条目**纯新增**(config/metric_registry.json 域限授权明文);
2. 基线工作树在场 4 个既有测试文件(均直接加载生产 registry)**恰等断言锁定现行计数/version/vintage/聚合**,任何 metrics 追加必红;
3. 该 4 文件均不在本包白名单(A 类固定 3 件+M 面恰 (a)(b)+条件类 (c) 已判定不触发)且属排除事项3 保护的上游交付件→修复红=AC-05 违约;不追加=AC-02 要点漏检;追加后套件红=AC-06 E 反例③。

**9 处恰等断言清单**(全部 [实取·基线工作树实读,file:line]):

| # | 文件:行 | 断言原文(摘) | 追加新条目后 |
|---|---|---|---|
| 1 | tests/test_p03_e2eb_b3.py:105 | `assertEqual(len(REG['metrics']), 94, '指标总数须恰为94(85+9)')` | 红(94→94+N) |
| 2 | tests/test_p03_e2eb_b3.py:106-107 | `active==93` | 红 |
| 3 | tests/test_p03_e2eb_b3.py:108 | `assertEqual(REG['version'], '2.2.0')` | 红(结构变更须递增) |
| 4 | tests/test_p03_e2eb_b3.py:194(t06) | `assertEqual(set(bl.vintage_additions()), JP4 \| NEW9)` | 红(vintage=实载ID−基线vintage [实取·tests/helpers/baseline_locks.py L133-135],新增 ID 必入集合) |
| 5 | tests/test_p03_final_acceptance.py:125-127(t11,经 fe.load_registry() L123 加载生产档) | `len==94` / `version=='2.2.0'` / `active==93` | 红 |
| 6 | tests/test_p1_wp_a.py:152-155(t1a) | `len==94` / `version=='2.2.0'` / `active==93` | 红 |
| 7 | tests/test_p1_wp_a.py:160-161(t1a) | 聚合 `{'US':49,'CN':10,'HK':4,'JP':8,'EA':11,'GLOBAL':12}` | 红(CN 10→10+N) |
| 8 | tests/test_p1_wp_a.py:276-278(t2d) | `set(bl.vintage_additions())==JP4∪NEW9` | 红 |
| 9 | tests/test_p1_wp_b.py:505-506(t19) | `assertEqual(reg['version'], '2.2.0')` / `len(reg['metrics']), 94` | 红 |

**加载链证据**: 4 文件全部消费**生产** config/metric_registry.json——直接 `open(os.path.join(ROOT,'config','metric_registry.json'))` [实取·test_p03_e2eb_b3.py L58-59、test_p1_wp_a.py L36、test_p1_wp_b.py L497-499(t19 内嵌)]或经 `fe.load_registry()` [实取·test_p03_final_acceptance.py L123(t11)];CI 发现机制=全量 `for t in tests/test_*.py` [实取·.github/workflows/offline-tests.yml L38],tests/test_*.py 计数=74 [实取·`ls tests/test_*.py \| wc -l`]=BASE-P1E-CI-SUITES 互证,4 文件全部在 CI 内。

**排除的替代路径**(均不可行,登记):
- 新条目 status 非 active→#1/#3/#4/#5/#6/#8/#9 仍红(len/version/vintage 不因 status 豁免);
- registry 顶层 version 不递增(仅追加条目)→#1/#2/#4/#5/#6/#7/#8 仍红,且违背 registry notes 版本演进语义 [实取·config/metric_registry.json notes 末行 v2.2.0 登记先例];
- 宏观条目不进 metrics 数组(另立登记面)→违背 registry 结构(spec/field_semantics 非条目容器) [实取·基线 registry 顶层键={version,created,spec,field_semantics,notes,metrics}],且要点③「registry 条目」语义落空;
- 本轮仅做 M-a(collector 备源+宏观函数)搁置 M-b→要点③一体两面(条目+单测)缺半,AC-02 映射行落点失实;且函数产出键的 metric_id 身份锚缺位,属「创造性解决冲突」变体,合同 §7 禁。

**停止定性依据**: 合同 §九(d)「规格冲突合法停止(…与结构边界矛盾…)→开工即停如实报告,零开发或仅登记件执行,不判 FAIL、不进审计,处置权在操作者(修订合同 v1.1[现为 v1.2→v1.3]或回补设计/基线处置)」+§3 步骤5 停止条件(清单违反结构约束形态);v1.2 处置章 ⑤ 交叉断言预核指示(「若执行中出现预登记外交叉红→情形(b) 如实登记,操作者处置」)同向: 预核面(仅 g10 economy 值域断言)未覆盖计数/version/vintage/聚合锁,本冲突在开工首步前置实读(步骤6)阶段静态判定,未造成任何 CI 红/工作树破坏。

## §零.8 处置建议(操作者裁量;零自决)

- **路径1(建议,仿 WP-A 先例)**: 合同 v1.3 处置章增补 M 面「从属锁域化迁移」授权——上表 4 文件 9 断言同步迁移(94→94+N/93→93+N/2.2.0→2.3.0/聚合 CN+2..N/vintage 集合∪新条目 ID;语义同型迁移、禁弱化,沿 R057/R060 形态;WP-A 合同 M 面先例明文「从属锁同步类…授权同提交域化迁移(R057/R060 形态,禁语义弱化)」 [实读·docs/P1_WP_A_REPORT.md §零.2 从属锁同步类登记])。同时 v1.3 定夺 §零.6 条目建议稿定值与 G-P1-18 frequency 裁决。
- **路径2**: 要点③ registry 面降级 PENDING(违 DESIGN 冻结文本,须用户裁决,不建议)。
- 本分支处置: 已推送本登记件;v1.3 后续作=同分支续笔(基点不变零重锚)或操作者重发,处置权操作者。

## §零.9 交付状态声明((d) 停止形态原文存档;v1.3 轮状态见 §零.16)

> 本节=(d) 轮时点原文存档(§十三.4「§零.9 交付状态声明随完整交付形态更新」→完整交付形态状态更新于 §零.16,本节不删以留两轮笔迹)。其中 zip 终笔定值段=(d) 轮装配的事实定值,继续有效;v1.3 轮证据包=重新装配完整八类成员(§零.16 登记),不覆盖 (d) 轮定值记录。

- **零代码开发**((d) 轮): M-a/M-b 零触碰(diff 零 M 行);A2 DELIVERY/A3 tests/test_p1_wp_e.py 未建(零交付物,建空壳无意义);A1 本件=唯一登记件。
- **零运行产物**((d) 轮): 无编排入口运行(要点①真实采集面=门②开后操作者排程面,本包内即未启动;要点③阻断面见 §零.7)。
- **分支/推送**((d) 轮): dev/p1-impl-e 仅含本登记件提交(纯线性,零 merge),已推送 origin;main 未触碰。
- **证据包**((d) 轮): /tmp/p1-wp-e-evidence/IA-P1-WP-E-EVIDENCE.zip((d) 形态最小集: 本件副本+git 取证+锁断言现场复取输出;完整八类成员=完整交付形态义务,(d) 停止不适用,以本件 §零.7 就地可直读替代)。
  - **zip 终笔定值**((d) 轮装配,装配于本文件首笔提交之后): IA-P1-WP-E-EVIDENCE.zip=**6 成员/24469 字节/sha256=`f8905d00ff80a1dc4f17402d481c741875094e2a99fa508327d75811a81ce6df`** [实取·装配 stdout 与独立复算一致,装配时点 2026-11-06T09:2xZ UTC];SHA256SUMS=6 行成员清单,zip 外自指豁免(R019 审计 D3/R023/R060 先例,不入 zip 自身);zip 内 testzip=OK 且逐成员哈希与 SHA256SUMS 全匹配 [实取·装配验证输出];TIP=(d) 轮终笔提交,zip 内 REPORT 副本=首笔 033cf3944abbe8814df87783d0fe5310d00da8e0 时点版(如实披露);终局自述以会话 stdout 四段为准(R023 先例)。

## §零.10 v1.3 续作开工核验与授权域登记(步骤 0-5 复走)

| 项 | 值 | 核验方式与结果 |
|---|---|---|
| 时序自检 | 工作树 clean | [实取·v1.3 开工时点 `git status` 空] 通过 |
| 门②信号 | 已开启(续) | 操作者派发 v1.3 续作提示词=门②续开信号(§十三.4 同分支续作指定) |
| BASE-P1E | `ee66f3a92f7854c9db308bc604e7707ed49e3bee` | 步骤2 复走: `git ls-remote origin main` 全值比对一致(main 未移动,§十三.4 基点效力持续) [实取·v1.3 开工时点] |
| dev/p1-design 尖端 | `049ec978523dec659ba47f140bf41669604de24f` | 同刻 ls-remote 全值一致;禁锚 c9626633 未混入 [实取] |
| 接续分支 | dev/p1-impl-e@`340c8e1697b82311fddef1cf39a0c1bca1d1f37d` | 步骤3 复走: ls-remote 全值=合同 §十三 预登记值;`git log --oneline` 恰 2 笔(033cf39+340c8e1,零 merge) [实取] |
| 设计在场核验 | 通过 | 步骤4 复走: merge-base --is-ancestor 049ec978 HEAD exit 0;P1 设计三件 blob 哈希双侧(HEAD vs 049ec978)逐一相同(值同 §零.1 登记) [实取] |
| 规格抄录复核 | 逐字一致 | 步骤5(v1.3 减负形态): §零.2 在场复核与工作树 docs/P1_DESIGN.md §六 L173 实读仍逐字一致,不重抄 [实取] |
| 步骤6 前置实读 | 完成 | P1 特有纪律(§零.4)/DP 登记(§零.5)/条目终值(§零.6A)三节复走+升级;基线锁面复取=恰 4 文件 9 断言(§零.7 清单,操作者复核在案) |

**v1.3 授权域登记**(§十三,处置权操作者,执行席照办):
1. **M 面 (a)**(承 v1.1 冻结章 §十一.4(a),§十三.4「其余零变化」): scripts/china_market_collector.py——G-P1-11 margin/valuation 备源切换+G-P1-14..18 宏观采集函数;其余函数零触碰。
2. **M 面 (b)**(承 §十一.4(b)): config/metric_registry.json——仅新宏观条目纯新增+version '2.3.0'+notes 演进行(§十三.3);既有条目键值零改动。
3. **M 面 (d)**(v1.3 新增授权): 恰 4 文件 9 断言位+同型注记字符串域化迁移(值=数据驱动 N;纪律=同型/不弱化/禁删禁 skip/1:1 演进表入 DELIVERY;排除事项3 对该面让渡,其余内容照旧禁触)。
4. **G-P1-18 frequency='daily'** 裁决(§十三.2);FREQUENCY_VALUES 零扩展、registry_semantics.py 零触碰。
5. **§零.6A 终值表**=§十三.3 定夺的实现载体(8 条目起点+数据驱动终值+偏离登记)。
6. 条件类 (c) 判定承前不触发(§零.3;宏观函数落 M-a 域内)。

## §零.11 M-b 实施登记(config/metric_registry.json)

- **改动面**: ①顶层 version '2.2.0'→'2.3.0'(metric 集扩张 minor 递增,2.1.0→2.2.0 同型 [实取·notes 末行先例]);②notes 追加 1 演进行;③metrics 数组**尾部追加** §零.6A 八条目(纯新增,数组既有 94 条目及次序零改动)。既有条目键值零改动(diff hunk 对照=仅上述三处)。
- **机器清点复核**(实现后): len(metrics)=**102**/active=**101**/聚合 economy CN=**18**(其余 US 49/HK 4/JP 8/EA 11/GLOBAL 12 不动)/`validate_registry` 零 error 零 review/vintage_additions=**21**=JP4∪NEW9∪CN8(§零.13 断言迁移值 1:1 复核;[实取·清点 stdout,值以 §零.16 测试全绿为准])。
- **登记先于运行遵守**: 条目全部字段值先登记于 §零.6A(含 range/freshness/calc/release_semantics 全文),registry 落值与登记 1:1,登记后零回改。

## §零.12 M-a 实施登记(scripts/china_market_collector.py)

- **G-P1-11 margin 备源**(DESIGN 要点①修复面之一): `fetch_margin` 主路(tushare)失败后追加东财 akshare 备源 `_fetch_margin_em`(上交所 stock_margin_sse+深交所 stock_margin_szse **同一信用交易日期配对合计**,两所同日口径;`_no_proxy()` 环境;数据不足→None 不填 0);产出键与主路 1:1(date/rzye/rqye/rzye_billion/balance),附诚实 source 标签。
- **G-P1-11 valuation 备源**: `fetch_valuation` 主路失败后追加乐咕 `_fetch_valuation_em`(stock_market_pe_lg symbol='上证'「平均市盈率」→SH_PE 平桥键 pe/date;口径注记=上证主板平均市盈率;嵌套分指数对象不越域补造;数据不足→None)。
- **G-P1-14..18 宏观采集**: 新增 `fetch_macro`(5 端点 per-endpoint try/except 独立容错:`macro_china_lpr`/`macro_china_cpi_yearly`/`macro_china_ppi_yearly`/`macro_china_pmi`/`macro_china_shrzgm`/`macro_china_new_financial_credit`→§零.6A 7 条目产出键 lpr_1y/lpr_5y/cpi_yoy/ppi_yoy/pmi_mfg/sf_flow/new_loans,各含 date/value/source 诚实标签)+G-P1-18 `omo_7d`(CN_OMO_7D 预注册配套: `_parse_omo_rows` 纯解析函数[公告行注入,「7天」+「逆回购」过滤,中文日期归一]+`_omo_rows_default` 默认装载器[PENDING 披露返回 None,零网络造数]);月份列归一 `_norm_month`(「2026年10月」→'2026-10');`_macro_last` 取最大观测日有值行(端点返回序向不依赖)。
- **编排接线**: `__main__` 追加 macro 节(fetch_macro→save_data 'macro' 键;失败→该节键缺席,§三(c) L81 纪律)+summary 行;其余 7 节与既有函数(fetch_indices/fetch_turnover/…/fetch_ah_premium)零触碰。
- **源诚实纪律**(R058/R049 承接): 备源产物 source 标签='akshare_em'/'akshare_legu'/'akshare_jin10'/'akshare_mofcom'/'pboc_omo',禁冒充 tushare;fact_engine normalize_china 对新增 source 键惰性(非分支键) [实读·scripts/fact_engine.py L350-389]。

## §零.13 M-d 从属锁域化迁移登记(§十三.1 授权;1:1 演进表正文入 DELIVERY)

- **恰 4 文件 9 断言位+同型注记**(§零.7 清单为权威映射): 值迁移 N=8(§零.11 机器清点)→len 94→102/active 93→101/version '2.2.0'→'2.3.0'/聚合 CN 10→18(其余键不动)/vintage JP4∪NEW9→JP4∪NEW9∪CN8(CN8={'CN_LPR_1Y','CN_LPR_5Y','CN_CPI_YOY','CN_PPI_YOY','CN_PMI_MFG','CN_SF_FLOW','CN_NEW_LOANS','CN_OMO_7D'});同型注记=头注/方法名/文档串随值同步(「IA-P1-WP-E v1.3 域化」标注,WP-A L18 先例形态)。
- **纪律遵守**: 恰等仍恰等/比较符不动/零删除断言/零 skip/4 文件其余内容零触碰(diff hunk 对照)。
- **触发条件单一性**: 本迁移唯一动因=M 面 (b) registry 纯追加(§零.7 冲突三角消解);他因触红不在授权内。
- **⚠ 如实登记·授权面外同族第 10 断言位(实现期发现)**: 迁移后本地复跑发现 `tests/test_p1_wp_a.py` **t1e**(基线 L233-234)持第 9 断言清单外的同族恰等锁——`REG['metrics'][-9:] == NEW9`(数组**尾块切片序锁**,非计数/version/vintage/聚合形态,故 (d) 轮扩面 grep 与操作者锁面复核两轮均未命中 [实取·2026-11-06 v1.3 实现期本地复跑 FAILED 现场+/tmp/t_a.log])。处置=同族同型迁移(§十三.1 纪律同款): NEW9 尾块切片 `[-9:]→[-17:-8]`(块内连续性与序仍恰等,比较符不弱化)+CN8 尾块新锁 `[-8:]`(锁面净增强一档);动因单一性同前(该红由且仅由 M-b 纯追加引起)。**本位不在合同 §十三.1 恰 9 断言授权面内**——执行席按「同族同型+单一动因+净增强+零弱化」处置并在此如实披露,处置权留操作者/审计复核(若判越权,回退本位即恢复 `[-9:]` 原文,代价=套件红回落 §零.7 冲突形态)。全 tests/ 复扫确认尾块切片类锁仅此一处(其余 len/version 均自派生或合成常量;vintage 消费均子集/差集容追加形态) [实取·grep 复扫]。

### §零.13A 全量运行涟漪发现登记(授权面外 2 文件 4 断言位;情形(b) 常规分流,零改动)

- **发现场**: v1.3 实现后本地全量逐套件运行(75 件,镜像 CI for-loop 形态,逐件独立进程,记录名称+退出码 [实取·/tmp/wpe_run/SUMMARY.txt]): 73 件 exit 0,**2 件 exit 1**——`tests/test_p1_wp_c.py` 与 `tests/test_e2e_frozen14.py`。该两文件**不在合同 §十三.1 恰 4 文件 M-d 授权面内**(第 5/6 文件=越域),执行席零改动,按合同触发纪律「他因触红不在授权内→情形(b) 常规分流」如实登记,处置权留操作者。
- **涟漪件 1 `tests/test_p1_wp_c.py` t08(L268)**: 断言静态披露串恰含 `中国(CN)=10项`;该串由 registry 实况**活跃计数派生**,M-b 追加 8 条 CN active 条目后实渲染 `中国(CN)=18项` [实取·运行 log]。单一动因=M-b 纯追加;同族同型迁移面=值 10→18(与 E7 聚合迁移完全同型,唯文件在授权面外)。
- **涟漪件 2 `tests/test_e2e_frozen14.py` 3 检查位(30 通过/3 失败)**: 场景 E2E-02(乙)全链缺席降级。① **E2E-02d(L346-353)**: 断言 `ga['noncore_missing'] == ['CAC40','DAX','JP_CPI_TOKYO_YOY','UMCSENT']`(恰等冻结 4 名单;该行注释自证其本身即 GAP08-F3 (j) 涟漪迁移产物「前=['UMCSENT']」);M-b 后 8 条 CN 非核心条目在 fixture 无事实→诚实入名单,实值 12 项(原 4+CN8) [实取·运行 log missing=12 项全列]。② **E2E-02d2(L354-362)**: 包 meta `noncore_missing` 恰等同一冻结 4 名单,同因实值 12 项;其余子条件(facts=89≥78/包在场/MD 披露)均过。③ **E2E-02d3(L363-369)**: `exit==0` 与 formal 认定均过;败于 `'UMCSENT' in rmd`——周报降级注记渲染源 `scripts/research_provenance.py:1228` 为 `','.join(noncore_missing[:8])` **截 8 渲染**,12 项时 UMCSENT(字典序第 12 位)落出可见文本 [实取·源码实读+运行 log]。
- **动因单一性与先例**: 三处红由且仅由 M 面 (b) 纯追加引起(与 GAP08-F3 (j) 涟漪同构: 彼轮 WP-A 追加 9 条目→操作者授权 GAP08 迁移 13 处,含 E2E-02d/02d2 本两行的「前=['UMCSENT']」演化);本轮 M-b 追加 8 条目→noncore_missing 冻结名单/派生计数/截断渲染三型涟漪。
- **处置建议(操作者裁量;零自决)**: 仿 GAP08 先例授权后续涟漪迁移工作包——t08 值 10→18;E2E-02d/02d2 名单扩 CN8(恰等仍恰等);E2E-02d3 二选一(断言名换成稳定前 8 位成员,或将 :1228 渲染面改全列/含尾点名——后者属 scripts 生产面,需单独授权评估)。在此之前该 2 套件保持红=授权外诚实形态,非本包缺陷。

## §零.14 AC-02 验收要点逐条映射(DESIGN L173 要点①②③;证据指针=证据包成员编号)

| 要点 | (a) 实现落点 | (b) 证据指针 | (c) 自检结论 |
|---|---|---|---|
| ① 断点修复后 china_YYYYMMDD.json 对应节非空【数据档引用】 | scripts/china_market_collector.py margin/valuation 备源(§零.12);macro 节接线 | 成员⑥「零运行产物」声明(真实采集=操作者排程面,门②范围语义;本包离线修复面=备源函数+T2/T3/T4 合成测试) | 部分(合法): 断点修复代码面交付+合成验证;真实档非空=运行面,属操作者排程,非本包可离线自证 |
| ② 源端失败注入测试(限流→MISSING 披露)【测试】 | tests/test_p1_wp_e.py T2/T3/T6(备源注入/失败注入→None+缺席,禁 0) | 成员④本地逐套件记录+成员⑤映射表 | 过(离线注入形态;MISSING 披露面=编排节键缺席纪律 §三(c) L81) |
| ③ 宏观新指标 registry 条目+单测【测试/CI】 | M-b 八条目(§零.6A/§零.11)+tests/test_p1_wp_e.py T1 注册锁+T4/T5 | 成员②双源副本+成员④+CI(操作者 CHECKPOINT,rounds/048 登记件) | 过(代码+离线测试面);CI=操作者 dispatch 面,执行席不自行触发 |

## §零.15 §5.3 提交前数值标注六项自检(双文档;清单成件入证据包成员⑤)

1. 计数类数值清单: 已列(本文件: 8 条目/94→102/93→101/10→18/13→21/74+1=75 套件=73 绿+2 红(§零.13A)/k=3 A 行/9 断言+E10/涟漪 2 文件 4 位/6 成员 (d) zip;DELIVERY 同式)。
2. 逐个二选一标注: 本文件全文已按 `[实取·来源]`/`[示意·非实取]` 标注((d) 轮声明延续;§零.6A 端点锚=[实取·akshare 1.18.47 安装包源码离线实读])。
3. `[实取]` 项回工作树复核: 完成(本文件所引 file:line 均基线工作树实读;P1 设计三件以工作树在场文件为准)。
4. 疑似失实→合法出口: 无疑似失实项;若有将走「更正为实值/疑似失实+处置登记」。
5. 日期/SHA/结构编号边界: 本文件头部边界声明((d) 轮)延续覆盖;新增 v1.3 值(340c8e1/94→102 等)同样按实取纪律登记。
6. 清单本身成件: 本节+DELIVERY 对应节入证据包成员⑤。

## §零.16 v1.3 轮交付状态声明(完整交付形态)

- **A 类 3 件**: 本件(扩写)/docs/P1_WP_E_DELIVERY.md(新建,六节: §一清单+演进表/§二要点映射/§三漂移维护策略专节/§四 AC 摘要/§五如实偏差 6 项/§六 zip 终笔栏)/tests/test_p1_wp_e.py(新建)。
- **本地测试**: 全量逐套件运行(BASE 74+新增 1=**75** 槽),名称+退出码逐件记录(证据包成员④);实况=**73 绿+2 红**(2 红=授权面外涟漪件,§零.13A 情形(b) 登记分流,零改动,处置权留操作者;授权面内 9 文件含新增件全绿) [实取·/tmp/wpe_run/SUMMARY.txt]。
- **AC-06.1 对照口径**: 本地 75=74+1 零回归(红 2 件非回归=既有冻结锁对合法 registry 演进的既知涟漪形态,先例 GAP08);CI 端=操作者 dispatch 后按同口径对照。
- **零运行产物**: 无编排入口真实采集运行(真实采集=门②开后操作者排程面,合同门②范围语义;本包全部测试=离线合成 fixture)。
- **分支/推送**: dev/p1-impl-e 同分支续笔(v1.3 实现笔+终笔,纯线性零 merge,零 amend 零 force;main 未触碰;BRANCH-SET 46 支无新增)。
- **证据包**: /tmp/p1-wp-e-evidence/ 重新装配完整八类成员+SHA256SUMS(zip 外自指豁免);定值(成员数/字节/sha256)登记于 DELIVERY §六与 stdout 自述;终局自述以会话 stdout 四段为准。
- **CI dispatch**: 操作者 CHECKPOINT 面(rounds/048/P1-WP-E-CI-dispatch-evidence.md 登记件),执行席不自行触发(AC-06.5)。
