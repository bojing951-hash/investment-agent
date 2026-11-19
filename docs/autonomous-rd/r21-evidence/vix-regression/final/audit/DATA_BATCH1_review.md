# 数据批1 独立复验报告(DATA_BATCH1_review)

- 复验员: 独立验证员(只验不修)
- 日期: 2026-11-10
- 对象: 分支 `dev/data-batch1-v1` commit `d6ddc28`(父=97d758e=v0.7.0-alpha main;台账所称"父 6a0dd80"经查为同内容异表述——6a0dd80 是 97d758e 的第二父,两基 diff 逐字节同: 21 文件 +643/−125)
- 方法: 零网络;数值全部从仓内原始采集档(china/global/macro/shiller_20261110.json 与 research_snapshot_20261110_v4.json)独立重数,不引用 B 席测试期望值;解释器 `~/AI内容/venv/bin/python3`(仅运行)。

## 总判定

| 面 | 判定 |
|---|---|
| 1 数值抽验 | **PASS** |
| 2 registry v2.8.0 | **PASS** |
| 3 十四套锁测试随升 | **PASS(逐套=合法校准,零弱化)** |
| 4 YTD 基准改动 | **PASS** |
| 5 红线 | **PASS** |

**总体: PASS。未发现新缺陷。**

---

## 面1 数值抽验 —— PASS(全部独立重数自原始采集档)

| 项 | B 申明 | 我的独立重数 | 判定 |
|---|---|---|---|
| SPX_EPS | n=1866/首1871-01/末值295.3881 | shiller_20261110.json: n=1866, 1871-01-01→2026-06-01, 末值 295.3881 | ✓ |
| SPX_PE_TTM 同n同末 | 同 n=1866/末2026-06-01 | 独立重数: n=1866, 1871-01-01→2026-06-01(末值 25.2212) | ✓ 同n同端独立核成立 |
| DAX | n=2538/收盘26559.83 | global_20261110.json: n=2538, 2016-11-10→2026-11-10, close=26559.83(series 末值 26559.830078=同值浮点原样) | ✓ |
| CAC40 | n=2559/收盘8314.50 | n=2559, 同窗, close=8314.5 | ✓ |
| CN 六指数 | 各 n=2428 | 六条目 series 全部 n=2428, 首2016-11-10/末2026-11-10, close 与字段一致 | ✓ |
| M2SL | n=119/末23413.9 | macro_20261110.json: n=119(2016-11-01→2026-09-01 均匀月格), 末值 23413.9 | ✓ |
| SB_FLOW | 南向55083.68万/北向216236.4万 | china_20261110.json southbound: south_money=55083.68, north_money=216236.4(5日合计 275731.04/1413899.13 随行;fact 层亿换算 550.84=55083.68万→550.8368亿,自洽) | ✓ |

**上证历史值抽查(要求 2 根,实抽 3 根,零网络下以本人对真实行情史的知识独立比对)**:
- 2016-11-10=3171.282(美国大选次日 A 股收盘实际值)✓
- 2020-03-23=2660.1674(全球疫情抛售谷底日上证实际收盘)✓
- 2024-09-30=3336.4974(国庆前放量拉升日实际收盘)✓
三根均与 Tushare 历史原值一致,无管线改写痕迹。

**内部一致性复核(独立手算)**: 上证 YTD 由深窗序列手算: 2026 首个收盘=2026-01-05=4023.4167 → (3663.7235/4023.4167−1)=−8.94% =文件 ytd_chg;周变化 vs[-5] 手算 −0.61%=文件。**跨列恒等式**: SPX_PE_TTM×SPX_EPS@2026-06-01 = 25.2212×295.3881 = 7450.03,落于快照 SPX 2026-06 日收盘带 [7267.0, 7610.0](月均≈7447)——Shiller 月频=月均口径下 P=E×PE 三列自洽,E 列直读无孤错。

## 面2 registry v2.8.0 —— PASS

- 独立解析: version=2.8.0, **110 项/108 active/1 unavailable(SPX_PB)/1 deprecated** ✓;必填身份字段扫描**零新增结构 error**(我扫出的 4 处 `observation_period_kind` 缺键=US_REAL_GDP/SPX_PB/ICSA/WALCL,**经对 97d758e 版逐条比对全部预存**,且为 field_semantics 明示的"枚举无对应值→不登记"合法态)。
- **DAX/CAC40 通道与身份面**: source=global_market_collector, source_symbol=^GDAXI/^FCHI;**economy=EA / calendar=ea / economy_rule=P10 逐字未动**(diff 不含该三行)——B"economy=EA 身份面零变化"申明属实。ea_market_collector 剩余条目=ECB_DFR/ECB_MRO/BUND_10Y/BUND_2Y/EA_HICP_YOY,零 Yahoo 依赖 ✓(ea 零依赖白名单纪律保持)。
- 新条目键面: SPX_EPS(shiller/E列/月频/calendar_month/usd/US/active/release_date_available=false/量程[0,500]);M2SL(macro_collector/FRED/月频/billion_usd=原始单位零换算/量程[8000,40000])✓。
- **SPX_EPS 事实面(v4 快照实查)**: quality_status=DEGRADED,issues=[release WARN `RELEASE_UNKNOWN: 采集端未携带release_date` + frequency DEGRADED `观测日滞后162天(>75天有效窗)`]——与 SPX_PE_TTM **逐字同款同严重度**,零特判 ✓。滞后 162 天独立手核(2026-06-01→2026-11-10=162 天)✓。
- v4 Gate A=DEGRADED,core_missing=[],**noncore_missing 恰=申明 5 项**(BUND_10Y/BUND_2Y/CN_OMO_7D/CN_SF_FLOW/JP_CPI_TOKYO_YOY),facts 总数 103(98→103 含 SOFR/WALCL/SPX_EPS/M2SL/DAX/CAC40/ECB_MRO 全在场——逐条在 facts 中实查到)✓。
- gap08/wp_c 转正如实性: 见面3(两套实测绿+语义分析)。

## 面3 十四套锁测试随升 —— PASS(逐套合法校准,零弱化)

实测: **14 套(13 改+1 新)全部 exit=0 绿**(CI 同款逐文件跑,test_model_live 不涉)。逐 diff 判定:

| 套件 | 改动性质 | 判定 |
|---|---|---|
| **test_p1_wp_c**(重点) | ①US 覆盖计数 53→55(=我独立重数 registry active US=55);②fail-closed: 域外负向 **NIKKEI225 保留**(UNVERIFIED+source_mismatch+metric_id=None 三断言原样),DAX 因通道转正移入**族内正例**(新增 MAPPED/metric_id=DAX/family=global_market 正向),USDJPY 同形反例保留 | **合法校准,锁面净增强,fail-closed 未破** |
| **test_p1_gap08**(重点) | fixture 承载文件 ea→global(通道转正镜像),**store 直通期望值 21000/8100 等原样保留**,回读校验改对 global 档(逐值全等不弱);F3 **新增强化**: global 在场而 DAX 缺→"来源文件在场而指标缺席(采集遗漏)"+**新反例** global 亦缺→"来源文件缺失(global:MISSING)" | **合法校准,净增强——原意图(权威源文件缺失→点名通道的来源级缺失)未掩盖,通道名随权威源如实迁移** |
| test_charter6_p2_shiller | **纯新增** SPX_EPS 断言: E列直读手算 8 值 [190..220]/陷阱文件 EPS 列=3/payload n=3/EPS=220.0/observations 补键;注册表锁 2.7.0→2.8.0/108→110/active 106→108/US 53→55(与我独立计数一致);vintage_additions 27→29 | 合法(加断言+机械重数) |
| test_e2e_frozen14 | noncore_missing 名单 14→16(按字母序插 M2SL/SPX_EPS——fixture 未带新条目数据,如实点名;DAX 仍在缺席名单=通道翻转不给 fixture 造数,正确) | 合法 |
| test_p02_w5_datasrc_b | EM 回落 series 首根 2026-01-05→2025-12-31(深窗),**ytd=100.0 断言保留**(证明 2025-12-31 的 90.0 不入 YTD 基准——纪律断言未随窗口放宽) | 合法(随行为变更校准,纪律保留) |
| test_p1_wp_a | 版本/计数/聚合(US 57=55active+SPX_PB+1deprecated,我独立核对)/尾序锁 [-2:]→[-3:]=(SOFR,WALCL,M2SL)/NEW9 source 族元组加入 global_market_collector(通道转正随动,active 断言保留) | 合法 |
| test_p1_wp_e / wp_b / oss / charter6_p1 / p03_e2eb_b3 / p03_final_acceptance / charter7_p2 | 版本 2.8.0/110/108、聚合、尾序、vintage_additions 27→29 机械重数;charter7_p2 **保留** v2.7.0 变更注记在册断言(历史不抹) | 合法 |
| test_data_batch1(新,38 检) | TOPIX 不登记(宁缺毋假)/DAX 事实生成+周收益手算 26559.83/26480.3−1≈+0.2996%/M2SL mom=+63.9 手算/cn_window_start 四窗+闰日回退/61s 限流闸未动/ea 零依赖/DFF 通道归属复核/台账在场 | 新增覆盖,期望值=手算字面值 |

## 面4 YTD 基准改动 —— PASS

- **独立构造跨年序列手算新旧口径**(80@2024-01-02 / 95@2025-01-02 / 100@2026-01-05 / 200@2026-06-30):
  - 新口径 `_ytd_base_close`=当年首个收盘=100 → YTD=(200/100−1)=**100.00%**(正确);
  - 旧口径(序列首根=iloc[0])=80 → 150.00%(深窗下把 2024 年值当年初基准,**虚增 50 个百分点**——即本批修复的错口径;旧代码在"年初至今"窗下 iloc[0] 恰为当年首根,故旧窗不暴露)。
  - **判定: 新口径正确**,行为变更方向无误。
- 退化分支独立核: 当年无行→退回序列首根(90)且语义如实("非完整YTD");空序列→None;年中起窗(首观测 2026-03)→仍取当年首个收盘 110(不是窗首错觉)。全部与 docstring 声明一致。
- **EM 回落同窗语义一致**: 代码读核 `_fetch_index_em` 与 tushare 主路共用同一 `cn_window_start(period)` 窗口过滤与同一 `_ytd_base_close` 纯函数(周变化规则亦同);test_p02_w5 实测 EM 序列深窗化(首根 2025-12-31)而 ytd=100.0 不变——两路口径一致申明属实。
- **真实数据印证**: 上证文件 ytd=−8.94% = 我按新口径从深窗序列手算值(基准 2026-01-05=4023.4167)。

## 面5 红线 —— PASS

- **零 push**: origin 无 dev/data-batch1-v1(远端仅 main+三个 data 分支);**零合并**: d6ddc28 单父提交。
- **零新凭证**: diff 全部新增行扫描 api_key/token/sk-/Bearer 零命中;首跑=现有 key(FRED/Tushare)免费源,台账明载用户批准。
- **零付费**: diff 无任何模型 API 调用;本复验全程零网络。
- **公开面零厂商字样**: 新增行 厂商A/厂商A/厂商A/openai/anthropic 零命中;README 改动仅计数更新(110 项/113 套/CI 112,与 +1 测试文件自洽)。
- **临时脚本确删**: `git status` 未跟踪物仅 audit/(我的两份报告);仓内无残留临时脚本。
- **台账 append-only 纪律**: 程序化逐行逐格比对 97d758e 版——**0 行删除**;7 行(#3/5/6/7/8/10/11)变更全部为处置列**纯追加注记**(原格文本逐字保留为前缀,无改写);新增"一之二"整节 append 于"二、评估表"之前,历史段零触碰。

## 新缺陷与观察项

- **未发现新缺陷。**
- 观察项(非缺陷): ①DAX close 字段=26559.83 与 series 末值 26559.830078 为同值两位舍入展示,口径一致;②SB_FLOW 采集层单位=万、事实层=亿(55083.68万→550.84亿),换算自洽,申明按采集层万口径与档一致;③registry 4 处 `observation_period_kind` 缺键为预存合法态(field_semantics 明示"枚举无对应值→不登记"),本批未新增也未修复(非本批范围);④NIKKEI225 不在 global_20261110.json(jp 通道承载,不在本批申明面,未重数)。
