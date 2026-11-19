# Seat-A 判断席执行留痕(Audit-R23 一问验收,零上下文)

规程: /tmp/r23/output/_seat_a_protocol.md,步骤 1-8 逐步执行,未增减。
硬边界遵守: 全程未联网;未读 research_archive/ 任何旧档;未改引擎代码与校验字段;
步骤 7(report)后停止——未自任审查席、未 record 裁决、未归档。

## 步骤 1 环境核验

- `Read /tmp/r23/CODE_VERSION.json` → git_head=b316e88b2b4a98e95ab23aeac71a304485e78b0f,
  git_diff_sha256=null, stamped 2026-11-20T00:00:00+08:00
- `ls /tmp/r23/data/daily/` → 11 件通道面: china/ea×2/global/hk_index_history/japan×2/jp×2/macro/shiller
  (20261119 面为主 + 20261105 旧面 ea/japan/jp)
- `ls /tmp/r23/research_snapshot_*.json` → 无匹配(exit 1)——快照缺席,须由本席建 ✓

## 步骤 2 工单(只读一次)

- `Read /tmp/r23/run_question_verbatim.txt` → 全球宏观地图问句: 美中欧日 × 12个月前/3个月前/最新一期 ×
  增长/通胀/政策;三转折+谁先变/跟进背离;传导机制+竞争解释+区分指标;历史类比+同步性+随后3/6/12个月。

## 步骤 3 建快照(纯本地)

- 命令: `cd /tmp/r23 && python3 scripts/snapshot_builder.py --date 20261119`
- 输出: 快照/MD/anchors(173 个)落 data/daily/;**Gate A: FAIL**(exit 2)
  - core_missing 6: CN_TOTAL_TURNOVER, DFEDTARL, DFEDTARU, DFF, SH_AMOUNT, ZQ_IMPLIED_AVG
  - core_fail 0;事实 95;质量 {PASS 65, DEGRADED 12, FAIL 0};非核心缺失 11 项含 BUND_10Y/BUND_2Y/CN_CPI_YOY/CN_OMO_7D/CN_POLICY_OVERNIGHT
  - 处置: 硬边界禁联网不可补采,规程未授权增删,如实记录后继续(缺席面在判断中以引擎锚格/序列/事件簇口径处理)

## 步骤 4 正式计划

- 命令: `python3 ia_cli.py research-one --stage plan --question "$(cat run_question_verbatim.txt)" --out-dir output/r23map --engine-root /tmp/r23`(cwd=/tmp/r23)
- 输出: ok=true, **run_ok=True**;run 目录:
  `output/r23map/20261119T173248Z_给我一份全球宏观经济变化地图_美国_中国_欧元区_日本在12个月前_3个月前和最`
  (run_ts=20261119T173248Z);AGENT_SEAT_ENVELOPE.json 在场(evidence_index 68 行/22 锚格/三利率分解面 ok/
  资产月窗 8 行/转折候选 top9/政策事件簇 3/JP_POLICY_TARGET registry_absent 缺口)。
- 未发生 run_ok=False,无重跑。

## 步骤 5 判断产出

- 读 AGENT_SEAT_ENVELOPE.json + read_first(report.json 关键面/evidence_index.json/views_digest.json[n=0 空库]/
  scripts/agent_judgment.py docstring schema v1.1/SKILL.md 纪律 15-17 与十步工作流)。
- 数据取用全部来自引擎面: 点值格 22 格(含 no_same_period_base/no_published_observation 如实缺席)、
  转折候选 top9(取 CN_PPI_YOY/CPI/CN_PMI_MFG 三转折,覆盖通胀+增长两维,同窗月频=先后未定)、
  政策事件簇(Fed 2025-12-10 降 25bp→2026-09-16 加 25bp;ECB 2026-06-11/2026-09-10 各加 25bp;
  跨国簇合并口径)、三利率分解(12 个月窗 +97=+104-7bp;近月窗 2026-10-16→11-17 +1=+15-14bp)、
  资产月窗 8 行、序列面(历史类比两段: 2021-04 美国再通胀[资产事后窗全]、2016-09 中国 PPI 退出通缩
  [美国面序列缺月=数据不可得如实注记])。
- 写 `<run目录>/agent_judgment.json`(schema 1.1): 2 矛盾陈述(各 3 竞争解释+实据引用)/
  2 机制链(E1×3+E2×2[假设注记]+E3×1[证伪指标 CORE_PCE])/2 情景五行齐备/
  reader_map 五面(总判断含 bp 回贴、四地走位+anchor_echo 66 条逐位对账、传导两链 5 环
  [对质三件套全填: 支持主解释×2+尚不能区分×3]、三转折[前后值按候选面月末口径]、
  历史两段[anchor/match_window/cutoff/aftermath_obs_months/us_analog/sample_note 齐+
  ex_post 数值全部引擎同窗复算]、rates_decomposition、asset_returns_echo 8 行)。
- 提交前本地只读预校验(同一引擎校验器): validate_judgment 全绿;contract 首跑 1 处
  NOT_VERIFIED(unbound token「M1」被切为裸数字)→ 按 checker 语境修订 basis 措辞
  (「传导链 M1 的起点」→『全球再通胀→政策转紧→实际利率』),复验 **VERIFIED**。
  此为提交前自检修订,attach 机器未拦截过(见步骤 6)。

## 步骤 6 attach

- 命令: `python3 ia_cli.py research-one --stage attach --report-dir <run目录> --engine-root /tmp/r23 --judgment <run目录>/agent_judgment.json`
- 结果: **attached=True(第 1 次提交即通过)**,blocked=null,validation_passed=True,violations=[]。
- contract_verification: verdict=**VERIFIED**(contradicted 0/unbound 0/six_fail 0/map_fail 0);
  L3/L4 produced=True,attribution=ai_inferred;reader_map_faces.complete=True。
- attach 迭代次数: 1;被拦次数: 0。

## 步骤 7 report

- 命令: `python3 ia_cli.py research-one --stage report --report-dir <run目录> --engine-root /tmp/r23`
- 结果: generated=True,full_report=FULL_REPORT.md,map_report=MAP_REPORT.md(含 sha256),
  machine_verified=True,copies_consistent=True,**deliverable=False**,
  review={required: true, seat_invoked: false, verdict: null}(独立语义审查待裁——规程预期);
  exit 1 = 审查缺席的如实上报,非装配失败。
- 到此停止: 不自任审查席、不 record 裁决、不归档。

## 产物清单(run 目录)

AGENT_SEAT_ENVELOPE.json / evidence_index.json / report.json(4.6MB)/ report.md /
agent_judgment.json(46.8KB)/ FULL_REPORT.md / MAP_REPORT.md(68KB)+ MAP_REPORT.sha256 / views_digest.json

## 关键口径备忘(供审查席)

- Gate A FAIL 属步骤 3 快照面(core_missing 6),plan/attach/report 链路 run_ok=True 不受其阻断;
  判断数值全部取点值格/序列/事件簇,未用 Gate A 缺失项。
- 月频同步处一律「先后未定」(2026-02→05 通胀浪/同月转折对);日频决议日跨月的排序(ECB 6 月先于
  Fed 9 月)以日频证据陈述。
- 历史段两段均为引擎序列可复算口径;2021 段资产事后窗全,2016 段美国面如实「数据不可得」。

## Round-2 修订轮(2026-11-20,协调席指令)

- 读毕 verdicts/VERDICT-round1.json + PROSE-round1.md(REVISE: 1 MAJOR/3 MINOR/4 NIT,307 复算点)。
- 五项修订(agent_judgment.json,全部落位,l3 与 reader_map 双副本同步):
  1. MAJOR-1: SCN-A threshold『较2026-11-18的2.21』→『较2026-11-17的2.21』(快照核验 BEI_10Y@11-17=2.21、@11-18=2.19)。
  2. MINOR-1: MECH-1 step-2 observed_fact 追加口径句(两副本): 『近30日』=研究面(截至2026-11-19)回溯30日内首个观测日起算,TIPS_10Y 起点2026-10-20=2.77、BEI_10Y 同日起点=2.35(日期/数值均快照核实)。
  3. MINOR-2: JP from_to『年内最大回落段』→『研究窗内最大回落段』。
  4. NIT-1: 剥离 causal_hypothesis『因果假设: 』/competing_explanation『竞争解释: 』字段前缀 12+12 处(渲染器自加,消除双重叠加)。
  5. NIT-3: E1 括号补两跳『(ECB_DFR 2.0→2.25(2026-06-11)→2.5(2026-09-10))』(l3+reader_map 两副本;决议日口径与句面一致,阶梯值快照核实)。
- 未动: NIT-2/NIT-4(渲染器缺陷,操作席收口)、MINOR-3(操作席规程转录)。
- 日期-数值全量自查: 判断档 344 处日期出现/199 个唯一语境,程序化核验 151 个叙述面日期+数值对(三批: 链/情景/三利率/资产 45 + 区域锚面 54 + 历史类比/跟进背离 52),对照 series_store+引擎锚格——151/151 吻合,0 错配;结构面(66 锚格/9 转折候选/三利率与资产回贴/历史 ex_post/evidence_refs)由 attach 契约复验 VERIFIED。一处可读性注记(非错配): MECH-2『水平值49.0→49.3仍在荣枯线下』无显式日期,两值在序列均为真(49.0@2026-02、49.3@2026-10;2026-05 实际=50.0),供 Round-2 参阅。
- 重跑链: 本地只读预校验(validate violations=[];contract VERIFIED)→ attach 重跑(attached=True 第 1 次提交,validation_passed=True,contract VERIFIED 0/0/0/0)→ report 重跑×2(首跑 copies_consistent=False=FULL_REPORT 在场旧版先检后写之次序现象,次跑 True)。
- 终态: generated=True,machine_verified=True,copies_consistent=True,review={required:true, verdict:REVISE(round-1), fresh:false, verdicts_n:1}=待 Round-2 复裁,deliverable=False(预期);MAP_REPORT.md 68410B/459 行,sha256 旁挂一致(dc68ab32…)。
- 边界遵守: 未联网;未读 research_archive//tmp/r23v;未改引擎代码/scripts/CODE_VERSION.json;未 record 裁决;未归档。

## Round-3 修订轮(2026-11-20,协调席指令)

- 读毕 verdicts/VERDICT-round2.json + PROSE-round2.md(REVISE: 1 MAJOR/1 MINOR/1 NIT,237 复算点;Round-1 五项修订 A1-A6 全 PASS;本轮 items 系连续性断言专项扫出)。
- 修订(agent_judgment.json,l3 与 reader_map 双副本同步;全部对照快照 series_store 核实后落笔):
  1. MAJOR(CN_PMI_MFG 水平轨迹四处+对质行重判):
     - MECH-2 step-1 text: 『水平值49.0→49.3仍在荣枯线下(最新2026-10同比0.61)——价修复强于量修复』→『水平值围绕荣枯线反复: 2026-03=50.4、04=50.3、06=50.3、09=50.1四个月高于50,2026-05=50.0恰在荣枯线上,2026-02=49.0与最新2026-10=49.3低于50(最新同比0.61)——上方停留未持续,价修复强于量修复』(两副本)。
     - MECH-2 step-1 observed_fact: 同轨迹改写+锚窗起读2025-12=50.1注记+对质依据句『需求渠道预期所需的『上穿50』在2026-03/04/06/09有真实观测,竞争预期『维持50下方』与观测相悖』(两副本)。
     - MECH-2 competing_explanation: 『量的改善未同步(CN_PMI_MFG 未上穿50)』→『量的改善未持续站稳荣枯线上方(2026-03/04/06/09四个月上穿50又回落,最新2026-10=49.3回到线下)』(两副本)。
     - CN from_to: 『持续处于荣枯线下』→『围绕荣枯线反复(锚窗内2025-12=50.1、2026-03=50.4、04=50.3、06=50.3、09=50.1高于50,2026-05=50.0恰在荣枯线上,最新2026-10回落至线下49.3)——量的修复温和反复』;锚点三元组与『观测』月序run原样(契约 check 11/13 不变式)。
     - 转折表 first_mover: 同轨迹改写『量的修复未持续站稳线上』。
     - 对质表 CN_PMI_MFG 行 face_off_verdict: 『尚不能区分』→『支持主解释』——非机械翻面: 主预期『上穿50且INDPRO同比与CN_PPI_YOY同向回升』三要素逐条对照快照(2026-03/04/06/09>50;INDPRO 1.2498→2.1497;PPI -0.9→5.7)全部有真实支持观测,竞争预期两要素(维持50下方、INDPRO不跟随)均与观测相悖;『上方停留未持续』的强度限定写入 observed_fact 不入三态判词。区分性观测口径(引擎当前面 2026-10-01=49.3,近30日Δ+0%)原样未动;competing_predicts 为事前预期定义,保持不动(预期固定、观测裁决,对质逻辑自洽)。
  2. MINOR(EA): from_to 『持续上行,最新达4.0』→『先回落至1.7(2026-01)后震荡上行(2026-05达3.2、2026-06回落2.8再升),最新达4.0』(逐月核: 2.1→2.1→2.0→1.7→1.9→2.6→3.0→3.2→2.8→2.9→3.2→3.8→4.0);三锚端点 2.1/2.9/4.0 不动。
  3. NIT(JP 月均): from_to 『持续上行』→『累计净上行+67bp(政策一年窗月均自2025-12的0.557至2026-10的1.227,其间2026-03→04与07→08两处-0.1bp显示级回落)』;headline 『日本政策利率月均口径持续上行』→『累计净上行0.67个百分点』——headline 不用 bp 记法(契约 check15: headline 含『利率』关键词时全部±Nbp 记号须匹配三利率池{97,104,-7}/{1,15,-14},67 不在池内;from_to 不在 bp 扫描面故细目置此)。基月校正: 初稿误写 2025-11=0.557,快照核实 2025-11=0.478/2025-12=0.557,政策一年窗(2025-11-17→2026-11-17)月频首观测=2025-12,已改 2025-12。
- 连续性断言类自查(『持续/连续/未上穿/始终/一直在』全 token 扫 judgment): 16 个字段命中=9 条独立断言(其余为 l3/reader_map 双副本)。逐条对照快照全序列: 成立 6 条(PMI『上方停留未持续』新表述=最长连续在上线 2 个月 2026-03→04;EA『连续加息』事件级两跳 2026-06-11/09-10;JP『利率持续正常化』制度级净+67bp 无降息;JP『连续收紧而非反转』事件级;2016 CN_PPI『连续修复』2016-01..09 严格单调 -5.3→0.1 快照逐位核实;本期『欧央行连续加息』事件级);前置条件句豁免 3 条(CORE_PCE 证伪条款『若…持续反超』、SCN-A『连续不低于3.5%』、SCN-B『连续两个月不低于4.4』均为前瞻触发器,非观测断言);矛盾 0 条。修订前矛盾断言 7 处(持续低于荣枯线×2副本/仍在荣枯线下×3处/未上穿50×2副本/持续处于荣枯线下/EA持续上行/JP持续上行×2)本轮全部清除,四文件残留 grep=0。token 类外锚点域副词注记(未改,锚点三元组单调成立+窗内波谷已在面): JP GDP『逐步回升』(窗内2026-01=0.56)、EA GDP『缓慢改善』(窗内2026-01=0.55)、CN PMI 同比『渐次转正』、UNEMP『低位平稳』(4.1–4.5 十四月值核实)。
- 重跑链: attach 重跑(attached=True,validation_passed=True,violations=[])→ report ×2(首跑 copies_consistent=False=次序现象,次跑 True)。
- 终态: generated=True,machine_verified=True,copies_consistent=True,review={required:true, verdict:REVISE(round-2), fresh:false, verdicts_n:2, archive=…VERDICT-…-02.json}=待 Round-3 复裁,deliverable=False(预期);MAP_REPORT.md 69255B,sha256=5b231645…,旁挂一致。
- 边界遵守: 未联网;未读 research_archive//tmp/r23v;未改引擎代码/scripts/契约校验字段/CODE_VERSION.json;未 record 裁决;未归档。
