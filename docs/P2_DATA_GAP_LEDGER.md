# Charter7 P2 数据缺口台账(2026-11-10)

三案例(A 全球宏观现状 / B 历史相似 / C 传导与条件推演)实战后缺口清点的
**逐项可行性评估+处置登记**。评估口径: 可用免费源**仅限现有已接线源**
(FRED / Tushare / Finnhub / Yahoo / BBK / ECB / Shiller);工作量
S(≤半天)/M(1-3天)/L(>3天或需章程决策)。

**红线(本轮与后续均适用)**: 不新增任何凭证;不调用任何付费 API;不自动
拉新数据——台账内"已接线/待实施"项一律**需协调方批准后真实拉取验证**。

## 一、本轮已实施(P2-3)

| 项 | 内容 | 状态 |
|---|---|---|
| US 流动性维首批 | `SOFR`(FRED SOFR,日频,percent→rate 族)/`WALCL`(FRED WALCL,周频周三水平,million_usd→price 族)注册表 v2.7.0 + macro_collector FRED_SERIES/SERIES_FREQ/SERIES_UNITS 接线 | **接线+fixture 测试+首跑真实拉取全部完成(2026-11-10,经协调方书面批准;见下首跑登记)**。缺席时=Gate A noncore_missing 如实披露(不进 core,不改 FAIL 语义) |

### 首跑登记(2026-11-10,协调方批准后真实拉取,源端只读/现有 FRED key/零新凭证零付费)

- **SOFR**: n=2148,首观测 2018-04-03(**序列起点即源端上线日**,非采集截断——
  history_note 已随行注记),末观测 2026-11-06,值 3.89%。
  源端限制: 日频每营业日发布前一营业日值;拉取时点周一(11-09)值尚未在
  FRED 在场,末观测=上周五属正常节奏。
- **WALCL**: n=521,首观测 2016-11-16(=采集窗起点,10 年全深),末观测
  2026-11-04(周三),值 6,748,145(百万美元≈6.75 万亿)。
  源端限制: H.4.1 每周四 16:30 ET 发布上周三水平,末观测=上周三属正常节奏;
  事实层 WARN"近20自然日观测覆盖率3/15偏低"=连续性启发式按日频口径评周频
  序列,**与既有周频 ICSA 同款同文案**(一致现状,非新缺陷;频率感知分母
  属后续引擎批,不在本台账范围)。
- **首跑校准(同日版本内修订)**: FRED WALCL 原始单位=**百万美元**(非十亿),
  按管线惯例(存原始值/注册表单位描述原始值,RSAFS 同例)将注册表单位口径
  由 billion_usd 校正为 million_usd+原始值量程 [3000000,10000000],
  SERIES_UNITS 标签同步;零换算逻辑,真实值 6,748,145 直接落入量程。
- **快照**: 当日重建 `research_snapshot_20261110_v3`(--allow-revision,
  修订原因在档);Gate A=**DEGRADED**(core 缺失 0;noncore_missing=8 项
  全部为其他通道既有缺席 BUND_10Y/BUND_2Y/CAC40/CN_OMO_7D/CN_SF_FLOW/
  DAX/ECB_MRO/JP_CPI_TOKYO_YOY——macro 单档拉取不可能修复,非本轮目标)。
  SOFR/WALCL **已从 noncore_missing 除名**,事实 96→98,SOFR=PASS,
  WALCL=WARN(上述周频覆盖率文案)。
- **analog 影响确认**: SOFR/WALCL **不在** `analog_engine.FEATURE_SPECS`
  26 条六维特征集内(注册表≠特征集,FEATURE_METRICS 由 specs 推导),
  Case B 归档(QB-20261110-023)数值零扰动。

选型依据: Case A 七维矩阵**流动性维四经济体全缺是最大研究缺口**;FRED
免费+现有 FRED_API_KEY+零新逻辑(周频/日频/利率/水平变化口径全有先例:
ICSA/FED_FUNDS/UST_2Y/US_REAL_GDP)。`M2SL`(月频)同模式可后续追加。

## 一之二、数据批1已实施(2026-11-10,用户批准"待裁定"数据批量项)

范围=**仅限现有免费源+现有 key**;分支 `dev/data-batch1-v1`;注册表
v2.7.0→**v2.8.0**(110 项/108 活跃);analog `FEATURE_SPECS` 未动
(数据批不改特征集,SPX_EPS 进估值维与否留章程决策)。

### 数据批1首跑登记(2026-11-10,用户批准后真实拉取,源端只读/零新凭证零付费)

- **SPX_EPS(#7)**: Shiller `ie_data` E 列,n=1866,首观测 1871-01-01,
  末观测 2026-06-01,末值 295.3881 美元。与 SPX_PE_TTM **同源同端**
  (同为 n=1866/末 2026-06-01;CAPE 列延伸至 2026-10-01 为源表列间发布
  差异);源端滞后 162 天属 Shiller 月频发布节奏,事实层 DEGRADED
  (RELEASE_UNKNOWN+滞后窗)=既有 SPX_PE_TTM 同款同文案,零特判。
- **M2SL(#5 可选项,已做)**: FRED M2SL,n=119,首观测 2016-11-01
  (=采集窗起点),末观测 2026-09-01,值 23,413.9(**原始单位=十亿美元**,
  registry `billion_usd` 描述原始值,零换算,WALCL 校准纪律同源)。
  H.6 月频发布滞后约 4 周,末观测=上月末属正常节奏;事实 WARN
  (月频覆盖率启发式,与 WALCL 同类现状)。
- **DAX(#8)**: Yahoo `^GDAXI` 转引,n=2538,首观测 2016-11-10,
  末观测 2026-11-10,收盘 26,559.83,PASS。
- **CAC40(#8)**: Yahoo `^FCHI` 转引,n=2559,同窗,收盘 8,314.50,
  PASS。两条目自 PENDING 转正,**通道归属=global_market_collector**
  (Yahoo 依赖所在;ea 通道保持零依赖白名单纪律,注册表 economy=EA/
  calendar=ea 身份面零变化)。源端限制: 转引源非交易所官方实时,盘后
  口径,已注记。
- **TOPIX(#8 JP 附带探测)**: Yahoo 免费无 `^TPX` 序列(实测 2026-11-10
  404)→**不登记,宁缺毋假**(NIKKEI 在场 n=2520 不变)。
- **EA 宏观三通道组配(#3)**: ECB 免 key——ECB_DFR 2.50(2026-09-16)/
  **ECB_MRO 2.65(2026-09-16,恢复采集;前缺席=网关间歇 504 重跑即得)**/
  EA_HICP_YOY 1.9(2025-12-01);**BBK 源站仍持续断连**(RemoteDisconnected,
  BUND_10Y/BUND_2Y READ_FAIL 如实缺席,不伪造,源端状态登记如上);
  Yahoo 股指=DAX/CAC40。ECB LFS 失业候选键实测 404×3(M/Q 形态)→
  登记为"评估不接线",无键猜测。
- **CN 股指回补(#10)**: Tushare `index_daily`(现有 token),新增
  `CN_INDEX_HISTORY_PERIOD` 参数默认 **10y**;6 指数(上证/深成/创业板/
  沪深300/中证500/中证1000)全部 n=2428,首观测 2016-11-10,末观测
  2026-11-10;**61s 限流闸门未动**(窗口加宽不增调用次数);YTD 基准=
  当年首个收盘(`_ytd_base_close`,深窗下不再以序列首根冒充 YTD 基准)。
  此前社融 SSLError 未在指数面复现。
- **#6 南北向(限免费可试部分)**: SB_FLOW 采集在场(southbound 节,
  2026-11-09,南向 55,083.68 万/北向 216,236.4 万,5 日合计随行);
  **CN_SF_FLOW(社融)SSLError 复现**(akshare `macro_china_shrzgm`,
  网络面,与 #1 同因)→如实缺席;TIC/EPFR 越红线未动。
- **#11 registered-not-collected 清理(实测复核 9 条)**: 8 条事实已在场
  (DFF/DFEDTAR=rate_expectations 通道,REAL_10Y/REAL_5Y/HY_IG_DIFF=
  fact_engine 派生,WTI_SPOT_M/ZQ_F1_PRICE/ZQ_F2_PRICE 各自通道)——
  台账前提已过期,属"已采集未巡检"而非"登记永不采集";真缺席仅
  CN_OMO_7D(PENDING,无免费源)+BUND_10Y/2Y(BBK 断连)+CN_SF_FLOW
  (上述)。DAX/CAC40 转正。"登记了却永不采集"静默态消灭。
- **快照**: `research_snapshot_20261110_v4`(--allow-revision,修订原因
  在档)。Gate A=**DEGRADED**(core 缺失 0;noncore_missing 8→**5**:
  BUND_10Y/BUND_2Y/CN_OMO_7D/CN_SF_FLOW/JP_CPI_TOKYO_YOY,全部为
  源端不可得或 PENDING 项);事实 98→**103**(SOFR/WALCL/SPX_EPS/M2SL/
  DAX/CAC40/ECB_MRO 全部在场,SB_FLOW 维持在场)。

## 二、评估表(未实施项)

| # | 缺口 | 案例 | 可用免费源(限已接线) | 新凭证 | 工作量 | 处置 |
|---|---|---|---|---|---|---|
| 1 | CN 宏观序列化(CPI/PPI/PMI/新增贷款止于单值,CPI/PPI 停 2025-08) | A①/C | Tushare(已配 Key,月频宏观接口;社融增量曾遇 SSLError=网络面如实记) | 无 | M | 待用户裁定后实施;Tushare 积分/限流面需实测 |
| 2 | CN 利率序列(10yr 国债/LPR 历史/OMO) | A②/C | 10yr 国债+LPR 历史: Tushare 可拉;OMO 无免费接口(akshare 1.18.47 无逆回购接口,CN_OMO_7D 身份预注册 source_symbol=PENDING) | 无 | M | 同上;OMO 项维持 PENDING(无免费干净源不冒充) |
| 3 | EA 宏观面(HICP 陈旧/增长就业无/BUND 序列无/DAX/CAC40 未采集) | A③ | ECB(HICP/就业,免 Key 已接线)+BBK(BUND 收益率,已接线)+Yahoo(^GDAXI/^FCHI,免 Key) | 无 | M | 待裁定;跨三通道组配,建议单独立项。**数据批1: ECB 三项在场+Yahoo 股指收口;BBK 持续断连如实缺席(见一之二)** |
| 4 | JP 东京 CPI(登记未采集) | A④ | 无已接线免费源(总务省 e-stat 未接线;Yahoo 无宏观) | 需新源 | M-L | 不实施(越红线①);留章程决策 |
| 5 | US 流动性维 M2(M2SL) | A⑤ | FRED(现有 Key) | 无 | S | 同 SOFR/WALCL 模式,可随下一批追加。**数据批1已收口(见一之二)** |
| 6 | 跨境资本流动(TIC/EPFR/南北向;CN_SF_FLOW/SB_FLOW 未采集) | A⑥/C(整环只能【假设】) | 南北向: Tushare/Akshare 可试(akshare 已装);TIC=美财政部(未接线);EPFR=付费 | 部分 | M-L | 南北向待裁定;TIC 越红线①;EPFR 越红线②。**数据批1: SB_FLOW 在场;CN_SF_FLOW SSLError 复现如实缺席;红线未动(见一之二)** |
| 7 | 盈利序列 EPS | A⑦/C | **Shiller(已接线免 Key)**: ie_data 含 E(每股收益)列,1871+ | 无 | S-M | 下一批最高优先候选之一(估值/盈利维研究直接受益)。**数据批1已收口(见一之二)** |
| 8 | EA/JP 本土股指与估值 | A⑧/C | Yahoo(^GDAXI/^FCHI;估值无免费序列) | 无 | S-M | 股指可做;估值项不冒充。**数据批1: DAX/CAC40 已收口;TOPIX 免费不可得不登记;估值项维持不冒充(见一之二)** |
| 9 | HY_OAS 族源端仅 3 年(ICE BofA 授权窗) | A⑨/B | 无——ICE BofA 源端授权限制,非采集器问题 | — | — | 不可修;条目 history_note 如实注记(现状即终态) |
| 10 | CN 股指序列仅 2026-01 起 | A⑩ | Tushare 指数日线可回补 | 无 | M | 待裁定。**数据批1已收口: 10y 深窗 n=2428(见一之二)** |
| 11 | registered-not-collected(DFF/DFEDTAR/REAL_*/HY_IG_DIFF/WTI_SPOT_M/ZQ_*) | A⑪ | DFF/DFEDTAR=FRED 序列(现有 Key,但登记走 rate_expectations 通道);REAL_10Y/REAL_5Y/HY_IG_DIFF=既有 FRED 序列派生;ZQ=Yahoo 期货 | 无 | S-M | 待裁定;注意通道归属(rate_economy vs macro)不可混。**数据批1已复核收口: 8/9 已在场,DAX/CAC40 转正,静默态消灭(见一之二)** |
| 12 | 阶梯政策序列×连续序列变化对(零基过滤后样本骤减) | A统计② | —(统计口径问题非数据源问题) | — | — | 需章程决策(新口径=研究语义变更) |
| 13 | SPX_PE_TTM 滞后 4 个月 freshness 处理 | A统计③ | —(Shiller 月频固有滞后) | — | — | 现有 freshness 披露已如实;改进=话术/旗标层 |
| 14 | 单值 fact 与序列层能力断层(overview 有/history 无) | A统计④ | —(架构问题) | — | — | 章程决策(序列层化与①同批做最划算) |
| 15 | 事件年表 fact 层 | B② | 无免费结构化源 | 需新源 | L | 章程决策(B 案"当时发生了什么"永久【假设】层为现状) |
| 16 | 金融条件 FCI 湖指数 | C | 无免费干净 FCI 序列(Chicago Fed FCI=新源;需接线+授权) | 需新源 | M-L | 不实施;组合近似+强制披露为现状 |
| 17 | ERP 直接序列 | C | 无免费源 | 需新源 | L | 不实施;E2 部分可验(风险溢价口径)为现状 |
| 18 | 五行模板 lint 自动校验/E1E2E3 机器标记/终稿六参模板化/单值陈旧度旗标 | Agent①-④ | —(引擎能力建设非数据源问题) | — | M each | 待裁定(P2 后续批) |
| 19 | HK 宏观八维零覆盖(增长/通胀/就业/利率/货币/财政/贸易/信心——110 项 registry 无一 HK 宏观序列;市场面 HSI/HSCEI/HSAHP/SB_FLOW 已在场) | C8 页① | 无已接线免费源: HK 政府统计处/Census&Stats 未接线;Yahoo 无 HK 宏观 | 需新源 | M-L | **Charter8 如实登记(2026-11-10),本轮不实施**;待用户裁定。HK 指数 5y 深窗已另行收口(HSI/HSCEI n=320→2460,见一之三) |
| 20 | HKMA 基础利率(Base Rate)无免费干净源 | C8 页① | 实测(2026-11-10): HKMA API monetary-base 端点免 Key 可达但**无 base_rate 字段**;候选路径(/base-rate 等)一律 405/400 网关拒;网页 HTML 无授权 API 语义 | 无 | M | **Charter8 如实登记(2026-11-10),本轮不实施**;不冒充不手抄,待裁定(若官方 API 更新含利率端点可零凭证接线) |
| 21 | 财政维四经济体零覆盖(美/欧/日/中财政收入支出序列,110 项无一) | C | 候选: FRED 联邦收入/支出序列(现有 Key: FYFRGDA188S 占比类/MTSDS133FMS 等);财政部公开表(美=MSPD,欧=AMECO,日=财务省,中=财政部——均未接线) | 部分 | M-L | **Charter8 仅登记(2026-11-10),本轮不实施**;FRED 候选=零新凭证可随下轮数据批评估,余需新源;待用户裁定 |
| 22 | 贸易维四经济体零覆盖(进出口序列,110 项无一) | C | 候选: FRED 进出口系列(EXPGSCA188S/IMPGS 等,现有 Key);中国海关/欧盟 Eurostat 未接线 | 部分 | M-L | **Charter8 仅登记(2026-11-10),本轮不实施**;同 21,FRED 候选零新凭证;待用户裁定 |
| 23 | CPI/CORE_CPI 2025-10 单月缺测(序列 2025-09→2025-11 直跳,n=118;同期 CORE_PCE/INDPRO/RSAFS/UMCSENT 2025-10 均在场 n=119) | W | 实查(2026-11-10,C席观察①处置): **原始档 macro_*.json 全部本地 vintage(20261101~20261110)一致缺该月=源侧缺口忠实传导,非快照装配漏月**;series_store 不载宏观通道系设计(e2eb_query_executor NO_DATA_CORR_NO_STORE 在案),宏观序列经采集档回退=既定取数路径 | 无 | S | **登记不修(2026-11-10)**: 装配链无缺陷;若源端补发该月,采集档更新后自然消失 |
| 24 | 采集层 yoy 带 [330,400] 天容 11 个月基期: CORE_PCE/INDPRO/RSAFS/UMCSENT 的 macro 档 yoy_pct 实为 335 天(11 个月)变化却标"同比"(A席五值 2.94/2.70/6.31/−10.26 即此层;CPI 因 2025-10 缺测恰好落到 2025-09 真 12m=3.7173)——与快照层 m12 日历窗(同四指标 3.12/2.25/6.29/−12.70)口径分叉 | W | 实查(2026-11-10): `_pick(330,400)` 取带内距最新最近观测,2025-10(滞后335天)先于 2025-09(365天)命中;**该带为 P0 期显式设计且被 tests/test_charter6_p0_windows.py:262 断言锁定(注释明书 334 天基期)**,非事故缺陷;引擎权威面(快照 m12=end−12 自然月锚定)始终日历正确,A席引用的是原始层字段 | 无 | M | **登记待裁定(2026-11-10,不阻塞 Charter8)**: 若收紧带(如 [360,400] 或自然月锚定)=改采集契约,须同步改锁定测试+再生成采集档+复核已归档研究引用,属口径政策变更,须协调裁定;当前两条口径以 yoy_pct_from 日期透明可辨 |

## 三、已收口项(勿重复登记)

- **A 统计① 1m/1y/5y 窗口** → P2-2 自配对 `compare --metrics X,X --start T-k
  --end T` 正式口径(cli-contract/USER_GUIDE/SKILL 三处同步+empty_window
  诚实语义;不加第二条窗口逻辑,防口径分叉)。
- **B QB-20261110-023 TOP-N 排序读作纯距离序** → P2-1 裁决=机制无错
  (缺席多者只降位,保守方向),残留缺陷=输出未披露排序依据;已加
  `sort_basis` 随行+条目 `n_missing`(零计算改动),处置注记见
  engine-notes Charter7-2 条。
- **A 研究① analog P0 七项** → 已随 Charter7 P0(commit 308f615)修复。

## 三之二、Charter8 数据面(2026-11-10,dev/charter8-research-map-v1)

- **HK 指数 5y 深窗收口**: HSI/HSCEI 序列 n=320→**2460**(2016-11-10→
  2026-11-10),通道=china_market_collector(禁同概念双注册,未动 registry
  归属)。机制: 腾讯日K bars 参数化(HK_INDEX_HISTORY_BARS 默认 2600)+
  yfinance 10y 备源;实测腾讯 WAF 501 拒 bars>320,首跑走备源 n=2460,
  收盘与腾讯口径交叉一致(24557.04/8265.81)。快照 v5(facts 103,Gate A
  DEGRADED 如实: BUND_10Y/BUND_2Y/CN_OMO_7D/CN_SF_FLOW/JP_CPI_TOKYO_YOY
  noncore_missing 5)。1m/3m/1y 窗口现可用;**5y 窗仍不足 10 年史,如报
  empty 即诚实缺席**。
- **HKMA 基础利率/HK 宏观八维/财政维/贸易维** → 见评估表 19-22(仅登记)。

## 四、台账维护纪律

- 本台账=append-only 倾向: 新缺口追加行,收口项移入"三"并在行内注记收口
  commit;不删除历史行。
- 任何"待裁定"项开工前须协调方明示批准;真实拉取验证通过后在本表登记
  首跑日期与观测覆盖。

## 三之三、Charter9 验收轮观察与缺口(2026-11-11,dev/charter9-closeloop-v1)

来源: C席复验 4 观察(audit/C9_FIX_REVERIFY.md L86-91)+ A席终报告 5 缺口
(QB-20261111-010.research-full.json 内逐字记录,此处登记为台账行);全部
非阻塞,E席终验已核"在案不丢"。

- **C9-1 horizon 受控词表(A席①,采集契约候选)**: 62 条 forecast 中 33 条
  UNPARSEABLE("当前/战术配置/下阶段"等定性中文期限)。P1 采集层若 horizon
  改受控词表(CY20XX/QX/N月),机器可判率可大幅提升——属采集契约变更,
  留下轮与 B席扩采节奏联动裁定(同台账 24 行 yoy 带收紧的同类先例)。
- **C9-2 六标签判别力首验窗=2026-12 起(A席②,预期管理)**: 库龄 2026-07~11
  全未到期,成熟度护栏按设计压制 supports/against,观点级 17/17
  INSUFFICIENT_EVIDENCE=库龄函数非引擎缺陷。首验窗=2026-12 FOMC+G20 全年值
  (2027 初发布)。
- **C9-3 metric_refs 方向提取单点化(A席③,工程候选)**: 方向声明=Agent 单点
  判断,verifier 只校验结构不校验语义映射。后续轮可加独立第二提取交叉核。
- **C9-4 BIS 档 vintage 薄化(A席④,采集节奏联动)**: 同机构新旧档并存加重
  mode A 证据面变薄(BIS 09-14=2/50 行)。B席扩采节奏应与 vintage 深度联动。
- **C9-5 七条 M 无情景(A席⑤,研究面)**: M2/4/5/6/7/8/9 无情景(裁定降级
  允许,SCN 节如实列),情景生成=下轮 Agent 研究面。
- **C9-6 mode A 回退 evidence 表随 publish 年龄变薄(C席①,编排层须知)**:
  保守设计(09-15 档→0/16 行),SKILL 编排层引用旧档 mode A 结果须注记。
- **C9-7 forecast_target_map 覆盖小(C席②,数据面)**: mode C 近期可机械判定
  面窄(禁猜如实);随受控词表+到期件累积自然扩面。
- **C9-8 pytest 无法收集套件(C席③,环境约束非缺陷)**:
  test_afin_acceptance 模块级 sys.exit 阻 pytest 收集,CI 逐文件契约不受
  影响;登记备忘,不修。
- **C9-9 "2027年起年度步伐"裸年解析语义(C席④,备忘)**: 按裸年子串解析为
  2027-12-31,确定性有披露,但语义是节奏非时点;解析器升级时一并处理。
- 附:E席非阻塞观察 6 条(HSI×SPX 第4位截断/test_oss_product W7 环境敏感/
  parse_view_horizon 同形多时点取首[库内0影响]/openai SDK 前席遗留等)
  见 audit/C9_FINAL_ACCEPTANCE.md。

## 三之四、R5 阶段证据覆盖面盘点(2026-11-11,dev/rd-r5-stage-coverage)

来源: OPEN_ISSUES「R1 发现·阶段B 可判面受限(16 指标快照 facts 缺席)」——
本轮全量分解为**四类缺陷**(逐类处置+验收证据 = `audit/R5_STAGE_COVERAGE_INVENTORY.md`,
此处仅登记数据面行;①③为引擎覆盖面缺口已修,不属数据缺口):

- **R5-D1(P0 观察)CN_CPI_YOY/CN_PPI_YOY 陈旧值**: 快照在档
  `CN_CPI_YOY=0.0@2025-08-09`/`CN_PPI_YOY=-3.6@2025-08-09`(DEGRADED),
  akshare_jin10 源 2025-08 后停更而采集器持续写最后值;两值同日期且
  落周六=疑似发布日解析错位。**证据引擎(A/B 型)仍采信该事实**
  (DEGRADED 只披露不拦截)→ VIEW-003/007 的 CN_CPI_YOY 证据行建立其上。
  处置: ~~采集器修复(jin10 通道换源/日期解析)~~ **[R6-D1 已修一半
  (2026-11-11,dev/rd-r6-collection-fixes)]** CN_CPI_YOY→tushare pro
  `cn_cpi.nt_yoy` **换源成功并真实拉取验证**(202609=0.9,月末观测日,
  registry v2.8.1);**CN_PPI_YOY→tushare pro `cn_ppi.ppi_yoy`**
  **[2026-11-12 更正: 免费已通]** 首夜(23:0x)服务端拒「没有接口(cn_ppi)
  访问权限」,跨午夜积分刷新后同 token 可访问——零付费,快照 20261112 实测
  **PPI=5.0@2026-09-30**(月度序列连贯 202602=-0.9→202609=+5.0,采矿业
  分项 25.4 同源佐证)。用户「暂不付费」裁定未触发任何支出,自然满足。「DEGRADED+陈旧窗是否
  拦截出判」新鲜度政策议: CPI 侧换源后事实自动转新鲜,政策议降级为 P3。
- **R5-D2 CN_OMO_7D=字段从未采集**: ~~采集器补 akshare OMO 端点~~
  **[R6-D2 已核=源端全阻(2026-11-11,操作者网络实测)]** 四路候选全灭:
  ①tushare pro 无 OMO 接口(wk_omo/cn_omo/omo_rate 皆「请指定正确的
  接口名」);②央行官网 www.pbc.gov.cn 502(标准 TLS 下仍拒);③akshare
  1.18.47 零逆回购端点(源码 grep 证)+无 telegraph 函数;④东财
  news_economic_baidu cookie 门。**登记=源端受阻(source-blocked)**,
  不造数;后续路径候选: chinamoney/东财 datacenter reportName 深挖
  (注册为 P3 观察,不阻塞)。
- **R5-D3 CPI_YOY(US) 语义层 id 错配**: 假设层引用 `CPI_YOY`(4 观点),
  注册表实有 `CPI`/`CORE_CPI`;引擎侧已改精确注记「不在注册表(语义层映射
  缺口,禁猜)」,重指=Agent 层待办(编排层映射质量,与 C9-3 同类)。
- 既有行维持: BUND_10Y/BUND_2Y(BBK RemoteDisconnected)、JP_CPI_TOKYO_YOY、
  HY_OAS 族(ICE 3 年授权窗)——见上各节,不重复登记。
