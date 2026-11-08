# IA-P0-2-W5 交付说明(真实数据验收: 可重复可追溯的独立外部核验+独立复算)

任务: IA-P0-2-W5-DEV-v1.0 | 验收契约: IA-P0-2-W5-AC-v1.0(冻结,验收主体Agent 4)
性质: W4(含FIX1~FIX4)终判PASS/CLOSED后的**新工作包**——不重开W4审计范围,
唯一目标=把`scripts/real_data_acceptance.py`升级为可重复可追溯的真实金融
数据独立验收,并**实际执行正式真实数据验收+实际交接证据包**。
基线: W4封版 `7c004c65e98e54a519b2a647632c74b6b83b1bcd`(=最终CI run
41220175595;dev/p0-2-w5自该Commit创建,不从main重开发);
W3封版 `497b02c7`;GitHub main=P0-1封印 `50b5d13d`(禁合并)。

---

## 1. W5-01 既有脚本审计结论(只读理解,不重写fact_engine等)
对W4封版版real_data_acceptance.py逐行审计,确认八项外部对照与综合判定的
既有缺陷(全部已在源码定位,本包修复对象):
1. UST容差声明"3bp(百分点差)"但代码`abs(v-ext)/abs(ext)*100`为相对百分比
   ——量纲错;
2. 只取UST_10Y观测日抓官方CSV行,2Y/30Y观测日不同即查不到(期限日期错配);
3. SPX取FRED"最近一条"不校观测日——错日冒充同日;
4. PAXG(现货代币代理)按1%容差判GOLD_F(COMEX期货)PASS——工具身份不可比;
5. FRED DCOILWTICO(现货)按2%容差判WTI_F(期货)PASS——同上;
6. 新浪实时价parts[3]直接与目标收盘比较,不校日期与收盘口径;
7. B段复算: 双方均无基准仍计"✓数据不足"混入通过侧;且未独立校验基准日期;
8. `exit(0 if n_fail==0 else 2)`: 外部全失败/全SKIP也exit 0——不可核验冒充通过。
依赖模块(fact_engine/snapshot_builder/research_provenance/trusted_root/
Gate A/series_store/derived语义/registry单位)全部只读复用,零修改。

## 2. W5实现与版本
增量Diff(`7c004c6→W5最终SHA`): scripts/real_data_acceptance.py(范围内重写,
464→约700行);tests/test_p02_w5.py(新增32用例);docs/P0_2_W5_DELIVERY.md
(本文件)。**未触碰**: 采集器/fact_engine/snapshot_builder/trading_calendar/
metric_registry.json/新闻系统/W4审计器/Gate A/B/LIVE/launchd/main。

## 3. W5-02 八项外部对照(独立结构化,纯函数可测)
- **UST 2Y/10Y/30Y**: `difference_bp=|our_pct−ext_pct|×100≤3.0`(收益率
  百分点差,round至0.01bp),三期限各自观测日行匹配(union一次取官方CSV,
  各归各列),缺该期限观测日→NOT_VERIFIED(不得以相邻日期/他期限冒充)。
- **SPX**: FRED SP500必须**同观测日**;只有最近历史观测→NOT_VERIFIED并
  披露available_dates。
- **GOLD_F**: Coinbase PAXG为现货代理≠COMEX期货→恒NOT_COMPARABLE,
  参考偏差仅披露(容差不解决工具身份——旧1%容差PASS的固定反例入D组)。
- **WTI_F**: FRED DCOILWTICO现货≠期货连续→恒NOT_COMPARABLE(无基差/
  同结算时间证据,不得放宽容差代替身份验证)。
- **SHCOMP**: 新浪快照日期==目标观测日且收盘口径(当日须≥15:30北京时间)
  才比较;错日/盘中/无时间→NOT_VERIFIED。
- **BTC**: Coinbase Exchange BTC-USD,granularity=86400,逐K线校验起点
  `ts%86400==0`(UTC日K日界),USD计价(unit==usd),同UTC日收盘≤0.5%。
- 外部失败(HTTP异常/限流/缺字段/日期缺失/无密钥)→NOT_VERIFIED+诊断证据,
  不编造、不以旧日期补足、不以他源冒充。
- fetcher层结构化证据: source/url(api_key脱敏)/fetched_at_utc/http_status/
  body_sha256/body_bytes/error;原始正文落out-dir/evidence/(Git外)。

## 4. W5-03 独立复算(independent_period_returns强化+recompute_check)
- 输入校验fail-loud: dates/values等长、日期须真实ISO日历日、数值严格数值
  (拒bool/None/字符串)、重复日期→ValueError(乱序可算,排序后计算)。
- 锚定语义(独立实现,不调用fact_engine计算): ISO周一起始=1月4日所在周推算
  (跨年正确);mtd=严格早于当月1日的最后观测(前月末非交易日自动回退);
  ytd=严格早于1月1日的最后观测(上年末非交易日自动回退);期末=≤obs最后观测。
- recompute_check逐期输出: 期末观测日三方断言(事实obs==独立obs==引擎end)
  +独立基准/引擎基准逐期**日期相等核对**+(期末/基准−1)×100两组值+差异
  (≤0.01pp)+判定;单位纪律前置(仅价格类可套收益公式,利率/点差/计数类
  拒算FAIL);篡改引擎值/基准日期/期末→FAIL;双方均无基准=
  INSUFFICIENT_HISTORY(不是成功复算);单侧可算→FAIL(不一致)。

## 5. W5-04 综合三态与退出码
- 状态集{PASS,FAIL,NOT_VERIFIED,NOT_COMPARABLE,INSUFFICIENT_HISTORY,
  SKIPPED};仅真实独立可比通过计PASS。
- 退出码: 0=PASS;2=FAIL(任一项FAIL,或Gate A非PASS/DEGRADED阻断,
  或缺源日专用1);3=NOT_VERIFIED。
- 覆盖门槛(不满足→整体NOT_VERIFIED): UST≥1真PASS+市场(BTC/SPX/SHCOMP)
  ≥2真PASS+外部总PASS≥4+复算PASS≥2且复算零FAIL。
- --skip-external=离线诊断,恒NOT_VERIFIED(不获真实核验结论);全部外部
  不可达→NOT_VERIFIED(不得整体PASS)。
- Gate A语义不变: 非PASS/DEGRADED→exit 2阻断(信任边界, FIX8-03兼容)。

## 6. W5-05 证据保全
报告(JSON+MD+LOG三件,evidence/子目录存外部原始正文,均在Git外out-dir):
代码版本(git HEAD/branch/脏文件数+脚本SHA-256)/执行时间UTC/验收模式/
数据日与选择方式(--data-day显式或自动最新+lag)/data_dir与realpath/
trusted_root/快照ID与研究截止/Gate A全字段/sources_status(含各源SHA-256)/
注册表SHA-256与指标数/容差与舍入单一权威定义/逐项检查(ours含单位与价格
口径,external含来源观测日与实际返回值,comparison含公式两组值差异判定)/
状态分布/覆盖门槛/unverified清单/数据纪律与修订声明(核验当前取得值)。
密钥纪律: FRED key仅经env/仓库env_config载入用于请求,URL证据
`api_key=***REDACTED***`,报告写入前统一再脱敏(纵深防御),密钥不入任何证据。

## 7. W5-06 专项测试(tests/test_p02_w5.py,32用例,全部真实项目逻辑+Mock外部API)
- **A组10**: UST bp口径+期限各自日期;SPX同日强制;GOLD_F/WTI_F恒
  NOT_COMPARABLE(含参考源缺日NOT_VERIFIED);SHCOMP错日/盘中/收盘/超差;
  BTC UTC日界/缺K/非USD;外部不可达诊断;SKIPPED不计PASS;requests层
  Mock(官方CSV/DCOILWTICO缺值'.'过滤/UTC日K解析/新浪GBK字段/api_key脱敏/
  异常路径)。
- **B组6**: 跨ISO周(2026-W53/年初W01)/前月末与上年末非交易日锚定/无期前
  观测None;输入校验6类ValueError+乱序等价;真实fixture快照复算一致
  (week PASS+mtd/ytd INSUFFICIENT——fixture序列仅2观测,如实);篡改引擎
  值+0.5pp/基准日期/期末→FAIL;单位纪律(UST percent拒算)+单侧FAIL+
  双方无基准INSUFFICIENT_HISTORY。
- **C组6**: 覆盖达标PASS/exit0;任一FAIL→FAIL/exit2;外部全不可达→
  NOT_VERIFIED/exit3;--skip-external恒NOT_VERIFIED;UST证据缺失→
  NOT_VERIFIED;NOT_COMPARABLE/NOT_VERIFIED不填补覆盖。
- **D组6(负向敏感性退化注入)**: 对**真实源码文本**做最小退化替换后
  importlib加载执行(非mock被测函数,证明套件非实现复制品): ①SPX取FRED
  最近一条→NOT_VERIFIED场景变PASS;②NOT_COMPARABLE改判PASS(黄金/WTI
  期现直比);③(同②变体覆盖WTI);④UST百分点差换相对百分比→10bp超差
  场景变PASS;⑤--skip-external返回PASS/exit0;⑥删除基准日期核对→
  基准2099-12-31仍PASS。六个退化变体行为均与正确版分离(套件可检出)。
- **E组5(main端到端,fixture+Mock外部零真实网络)**: 离线诊断exit3+模式
  留痕+Gate A状态行(历史合同);外部全不可达exit3+URL脱敏+无密钥泄漏+
  失败不落盘正文;全比对通过→PASS/exit0+coverage达标+证据文件落盘+
  sources_status含SHA;Gate A FAIL(break SPX)→exit2不产报告;
  --data-day指定缺源日→exit1。
- 历史兼容(I3合同,tests/test_p01_fix8.py 52绿不变): 保留--data-dir/
  --trusted-root/--out-dir/--skip-external参数名、模块级datetime可patch、
  JSON顶层checks平铺列表含'Gate A状态'行、Gate A阻断exit 2。

## 8. W5-07 全量历史回归
本地全量(实现Commit推送前): tests/下50套件+新增w5=51执行全部exit=0
(test_glm_live按契约排除);含W4五套件/FIX1~FIX4/W3×6/W2×8/W1×2/
P0-1×12/E2E×3/Gate/报告保护/月报季报。零历史口径修改、零门禁降级。

## 9. 最终CI(workflow_dispatch, dev/p0-2-w5)
### CI实证(回填区)
- **run#1(实现Commit `4f0d42cdb46c51e1a2e08e68f4bbb23893faac90`)**:
  Actions Run ID=**41270649203** | Job ID=**124742551547**(tests) |
  event=workflow_dispatch | head_branch=dev/p0-2-w5 | head_sha=4f0d42cd…
  (完整40位核对) | conclusion=**success** | **51套件全部exit=0**
  (逐套件`test_<name> exit=`自Job日志逐行提取,非零数=0;新增
  test_p02_w5=0;test_glm_live按契约排除)。
- run#2(最终固定Commit,含本文件): 见Git外附件IA-P0-2-W5-ACCEPTANCE-
  EVIDENCE.zip内CI证据(最终轮实数按防预写纪律不入Git)。

## 10. W5-08 正式真实数据验收(最终固定Commit后实际执行)
- 输入: 冻结副本`~/audit/w4-real-data/daily`(Git外,848文件,
  W4轮自LIVE生产data/daily冻结,授权链=W4系列用户开发指令;执行前重新
  核实: 目录存在/非symlink入口/逐文件授权范围一致)。
- 信任根: 经既有`--trusted-root ~/audit/w4-real-data`显式授权
  (FIX8-03既有接口,不关闭Gate A/不伪造可信根/不降低源校验阈值)。
- 数据日: `--data-day 20261030`(该日四源齐且Gate A=DEGRADED core零缺失;
  20261031因rate通道real_economy缺ZQ_IMPLIED_AVG核心键Gate A=FAIL,
  如实披露不绕过;20261029缺UST_2Y)。已知如实预期: 该日china文件obs=
  2026-10-29(周五晨采集含周四收盘),周末新浪实时返回10-30快照→SHCOMP
  日期不匹配NOT_VERIFIED(如实记录;市场覆盖由BTC/SPX满足)。
- 外部源: Treasury.gov官方曲线/Coinbase BTC-USD与PAXG-USD日K/新浪
  sh000001/FRED SP500+DCOILWTICO(FRED key经环境变量注入,不打印)。
- 输出: Git外独立目录(不覆盖W4产物);JSON+MD+LOG+evidence/原始正文;
  执行真实外部API(不Mock);部分不可达保留失败记录不冒充;重大差异定位
  不临时扩容差;无法满足→NOT_VERIFIED。

## 11. W5-09/§十 隔离取证与证据包实际交接
最终DEV/LIVE只读隔离取证(HEAD/分支/工作区/main与W4封版不动/realpath
inode/launchd指向LIVE/LIVE关键源码=P0-1封印SHA/W5新代码未进LIVE/生产
只读元数据/输入授权副本证据/不能证明事项);生成
`IA-P0-2-W5-ACCEPTANCE-EVIDENCE.zip`(≥9类: 正式JSON/MD报告/执行日志/
输入版本证据/外部脱敏证据/独立复算明细/CI证据/隔离记录/SHA256SUMS+交接
说明)并**实际交付**(W4教训: 代码完成但证据未交接不算完成)。不打包生产
密钥/未授权数据/私人研究正文。

## 12. 未验证事项(如实)
- 真实生产数据金融数值真实性超出本包范围(核验的是采集-引擎-快照链路与
  外部独立源一致性);新浪为实时快照接口,历史日期收盘无法经该接口证明。
- 外部历史序列若已修订,核验的是当前取得值(报告声明)。
- fixture合成序列无2026年前观测→复算YTD为INSUFFICIENT_HISTORY(数据
  属性);真实冻结副本YTD复算正常。
- Gate A=DEGRADED(非核心MARGIN_BAL/SH_PE缺失)为该数据日真实状态,
  非本包放宽;20261031 Gate A=FAIL阻断如实披露。
- 单次快照证明取证时刻状态;历史瞬时事实无法事后证明。

## 13. 最终状态
三选一结论见对话交付报告与Git外证据包(材料齐全→READY FOR W5
INDEPENDENT ACCEPTANCE;确定性阻断→FAILED;缺正式真实验收或隔离材料→
NOT VERIFIED)。不自行签发W5 PASS/不合并main/不部署Mac LIVE/不实施
P0-3或P1。
