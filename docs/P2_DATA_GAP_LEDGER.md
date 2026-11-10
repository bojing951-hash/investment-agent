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

## 二、评估表(未实施项)

| # | 缺口 | 案例 | 可用免费源(限已接线) | 新凭证 | 工作量 | 处置 |
|---|---|---|---|---|---|---|
| 1 | CN 宏观序列化(CPI/PPI/PMI/新增贷款止于单值,CPI/PPI 停 2025-08) | A①/C | Tushare(已配 Key,月频宏观接口;社融增量曾遇 SSLError=网络面如实记) | 无 | M | 待用户裁定后实施;Tushare 积分/限流面需实测 |
| 2 | CN 利率序列(10yr 国债/LPR 历史/OMO) | A②/C | 10yr 国债+LPR 历史: Tushare 可拉;OMO 无免费接口(akshare 1.18.47 无逆回购接口,CN_OMO_7D 身份预注册 source_symbol=PENDING) | 无 | M | 同上;OMO 项维持 PENDING(无免费干净源不冒充) |
| 3 | EA 宏观面(HICP 陈旧/增长就业无/BUND 序列无/DAX/CAC40 未采集) | A③ | ECB(HICP/就业,免 Key 已接线)+BBK(BUND 收益率,已接线)+Yahoo(^GDAXI/^FCHI,免 Key) | 无 | M | 待裁定;跨三通道组配,建议单独立项 |
| 4 | JP 东京 CPI(登记未采集) | A④ | 无已接线免费源(总务省 e-stat 未接线;Yahoo 无宏观) | 需新源 | M-L | 不实施(越红线①);留章程决策 |
| 5 | US 流动性维 M2(M2SL) | A⑤ | FRED(现有 Key) | 无 | S | 同 SOFR/WALCL 模式,可随下一批追加 |
| 6 | 跨境资本流动(TIC/EPFR/南北向;CN_SF_FLOW/SB_FLOW 未采集) | A⑥/C(整环只能【假设】) | 南北向: Tushare/Akshare 可试(akshare 已装);TIC=美财政部(未接线);EPFR=付费 | 部分 | M-L | 南北向待裁定;TIC 越红线①;EPFR 越红线② |
| 7 | 盈利序列 EPS | A⑦/C | **Shiller(已接线免 Key)**: ie_data 含 E(每股收益)列,1871+ | 无 | S-M | 下一批最高优先候选之一(估值/盈利维研究直接受益) |
| 8 | EA/JP 本土股指与估值 | A⑧/C | Yahoo(^GDAXI/^FCHI;估值无免费序列) | 无 | S-M | 股指可做;估值项不冒充 |
| 9 | HY_OAS 族源端仅 3 年(ICE BofA 授权窗) | A⑨/B | 无——ICE BofA 源端授权限制,非采集器问题 | — | — | 不可修;条目 history_note 如实注记(现状即终态) |
| 10 | CN 股指序列仅 2026-01 起 | A⑩ | Tushare 指数日线可回补 | 无 | M | 待裁定 |
| 11 | registered-not-collected(DFF/DFEDTAR/REAL_*/HY_IG_DIFF/WTI_SPOT_M/ZQ_*) | A⑪ | DFF/DFEDTAR=FRED 序列(现有 Key,但登记走 rate_expectations 通道);REAL_10Y/REAL_5Y/HY_IG_DIFF=既有 FRED 序列派生;ZQ=Yahoo 期货 | 无 | S-M | 待裁定;注意通道归属(rate_economy vs macro)不可混 |
| 12 | 阶梯政策序列×连续序列变化对(零基过滤后样本骤减) | A统计② | —(统计口径问题非数据源问题) | — | — | 需章程决策(新口径=研究语义变更) |
| 13 | SPX_PE_TTM 滞后 4 个月 freshness 处理 | A统计③ | —(Shiller 月频固有滞后) | — | — | 现有 freshness 披露已如实;改进=话术/旗标层 |
| 14 | 单值 fact 与序列层能力断层(overview 有/history 无) | A统计④ | —(架构问题) | — | — | 章程决策(序列层化与①同批做最划算) |
| 15 | 事件年表 fact 层 | B② | 无免费结构化源 | 需新源 | L | 章程决策(B 案"当时发生了什么"永久【假设】层为现状) |
| 16 | 金融条件 FCI 湖指数 | C | 无免费干净 FCI 序列(Chicago Fed FCI=新源;需接线+授权) | 需新源 | M-L | 不实施;组合近似+强制披露为现状 |
| 17 | ERP 直接序列 | C | 无免费源 | 需新源 | L | 不实施;E2 部分可验(风险溢价口径)为现状 |
| 18 | 五行模板 lint 自动校验/E1E2E3 机器标记/终稿六参模板化/单值陈旧度旗标 | Agent①-④ | —(引擎能力建设非数据源问题) | — | M each | 待裁定(P2 后续批) |

## 三、已收口项(勿重复登记)

- **A 统计① 1m/1y/5y 窗口** → P2-2 自配对 `compare --metrics X,X --start T-k
  --end T` 正式口径(cli-contract/USER_GUIDE/SKILL 三处同步+empty_window
  诚实语义;不加第二条窗口逻辑,防口径分叉)。
- **B QB-20261110-023 TOP-N 排序读作纯距离序** → P2-1 裁决=机制无错
  (缺席多者只降位,保守方向),残留缺陷=输出未披露排序依据;已加
  `sort_basis` 随行+条目 `n_missing`(零计算改动),处置注记见
  engine-notes Charter7-2 条。
- **A 研究① analog P0 七项** → 已随 Charter7 P0(commit 308f615)修复。

## 四、台账维护纪律

- 本台账=append-only 倾向: 新缺口追加行,收口项移入"三"并在行内注记收口
  commit;不删除历史行。
- 任何"待裁定"项开工前须协调方明示批准;真实拉取验证通过后在本表登记
  首跑日期与观测覆盖。
