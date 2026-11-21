# Charter 6 独立金融审计判定(FRESH-FIN)

- 审计人: 独立金融审计员(与规格作者/实现者/前两轮审查者零共享上下文,从零验证)
- 对象: ~/investment-agent-dev @ dev/deep-macro-v1, HEAD 2fc8cc5, 范围 0f92151..2fc8cc5(6 commits)
- 方法: 自建独立复算管线(**零仓库 import**, /tmp/fin_audit/indep_pipeline.py, 43 项检查),
  引擎输出仅经 subprocess/驱动脚本取 JSON;测试用 ~/AI内容/venv/bin/python3 逐套实跑
- 红线遵守: 未改任何代码、未合并/push、零真实网络拉取、未触碰 ~/AI内容(LIVE)
- 日期: 2026-11-10

## 总判定: **PASS-WITH-DEFERRED**(1 项既有延期,零阻断)

延期项仅 **Shiller Yale 源 live 首跑**(部署期动作,需用户授权真实拉取,审计红线禁止我执行;
engine-notes 已登记"代码路径经 fixture 验证,live 首跑随拉取授权一并执行")。
A2 延期①③④与 A-fin 缺陷 D1-D4 已在 2fc8cc5 收口并经我独立验证(见下)。

---

## 逐项判定

### 1. analog 金融正确性(独立重算) — **PASS**

独立管线(零仓库 import;权重分母取自 Afin 规格表 §1.1 的 6/3/8/4/2/2,非引擎常量)对
test-[6] 合成 fixture(60 月,2020-01..2024-12)全量重算,与引擎输出对照 **43/43 通过**:

| 复算对象 | 我的手算/独立管线值 | 引擎值 | 一致性 |
|---|---|---|---|
| expanding z, 1..40 序列 idx39 | (40−20.5)/√(5330/40)=1.689277519114 | 1.689277519114419 | <1e-6 |
| z idx35(n=36 恰门槛) | (36−18.5)/√((36·1295/12)/36)=1.684588328892 | 1.6845883288916133 | <1e-6 |
| z idx34(n=35<36) | None(不降门槛) | None | 一致 |
| 锚点 2024-12 + 候选 2023-05/2023-12 全部 12 特征 z | 逐值(含 None 模式与 hist_n) | 逐值 | <1e-6 |
| 候选计数 | scanned 60 / valid 13 / dropped_overlap 12 / dropped_insufficient 35 | 同 | 全等 |
| TOP-5(月, D) | 2023-05/0.013553, 2023-04/0.015532, 2023-11/0.015536, 2023-10/0.018548, 2023-09/0.02195 | 同序同值 | <1e-6 |
| TOP-1 norm_wsum | 7/24=0.291667(手算 1/36+1/18+2×1/48+2×1/24+1/12=42/144) | 0.291667 | 6dp 等 |
| 逐特征 w_norm / Σw_norm | 独立重算 / =1 | 同 | 6dp 等 / <2e-5 |
| 候选 2023-12(D1 修复目标) | D=0.934889,共同特征 12 含 HY_OAS_d12m,w_norm=(1/24)/ws12 | 同 | <1e-6 |
| 事后窗方向统计 | 2022-12: SPX 1m=None/3m=4.761905/6m=15.238095/12m=26.761905(pct), UST_10Y +0.74/+0.25/+0.50/+0.75(pp);2023-02: SPX 3m=None(不缩窗)/6m=10.0 | 同 | <1e-6 |
| dispersion 全部格子 | 独立重算一致率 | 同 | <5e-5 |
| 维度贡献 contribution_share 和 | =1(数值) | =1 | <5e-6 |

月网格聚合独立复算: mean4={2024-01:2.5, 2024-02:3.5}(跨月取≤月末末 4 观测)/不足 4→空;
quarter={2024-03:2.0, 2024-06:3.0};last=月内末值;rv21=21 个对数收益总体σ×√252(独立公式 1e-9);
σ=0 常数列→弃用。加权距离拒绝项(分位映射/DTW/马氏)未出现,度量=规格指定的加权 z 距离。

### 2. 泄漏防护(六条规则,代码+测试+我方注入三重) — **PASS**

| 规则 | 代码证据(analog_engine.py) | 测试证据 | 我的独立注入 |
|---|---|---|---|
| ① expanding z 基准窗只用 t≤各自锚点 | z_at L270-284(h=sorted(m≤mkey),ddof=0,含当期;n<36→None) | [1] 逐值+未来改值不变 | A5: idx36-39 改 999→z(mk35) 不变(1e-15) |
| ② 检索只用 t≤候选锚点 | 候选循环 L424-434 逐候选自身 mkey 调 z_at;yoy/d12m/chg_3m 全部网格内 ≤m 查表 | [8] 注入断言 | F1-F4: 锚点 2024-12 后注入 2025-01..03=9999,固定锚点→TOP-5/状态向量/TOP-1 距离逐字节不变 |
| ③ 重叠窗排除 M≤M0−12 | L416-424(cutoff=_m_add(m0,−12);m>cutoff→dropped_overlap 计数披露) | 候选全部≤2023-12 断言 | D1: 计数 12/13/35 全等 |
| ④ 事后块独立、不参与排序、不缩窗 | dists 先算先排 L453-466,aftermath L551+ 之后构建且 D 永不读之;i_end≤i0→None L579-583;起点=次月首日 L566 | --no-aftermath 排序不变;2023-02 3m=None;2022-12-15=1000 未回吸 | F5: SPX/DXY/GOLD_F 2023 后×10(仅影响事后)→排序不变;F6: --no-aftermath 排序不变 |
| ⑤ 修订口径挂 research_mode_gate 继承 | L534-549(descriptive=available/event_study=release_date_available 全交集/realtime=_vN 存在性)+REVISION_NOTE 随行 | [8] 三态+文案断言 | live 实跑输出含 note |
| ⑥ 估值缺席不填补 | feature_grids L211-222 无任何填补/代理路径;coverage=0+note L524-528;SPX_PB 登记 status=unavailable | 缺席断言 | 7 条 other 族别名注入畸变值→输出与不注入逐字节一致(我方复做) |

### 3. 诚实拒答 — **PASS**

- 实跑 `python3 ia_cli.py analog`(dev 仓 data/daily,快照 20261108,宏观月频≈22 个月,
  快照序列 13-17 个月): **rc=1, kind=insufficient_history**,锚点 2026-11 有效维度 0<2,
  弃用特征全列,warnings 如实列 SPX_CAPE/SPX_PE_TTM/US_REAL_GDP 缺席,
  hint="扩展采集窗至≥36 个月后重试(现状短历史下拒答=正确行为,勿降门槛硬算)"。
- 阈值常量未放宽: MIN_HISTORY=36 / MIN_CANDIDATES=8 / WARN_CANDIDATES=24
  (scripts/analog_engine.py L53-56);`git log -L 53,60` 证实 9f69e20 引入后范围内零改动。
- 8≤N2<24 强警示路径: 60 月 fixture(13 候选)输出"候选仅 13 个(<24)…结论弱"(实跑确认)。

### 4. 窗口参数化 — **PASS**(全部独立调用验证)

- macro_observation_start(now=2026-11-09): 缺省→2016-11-09(10y);15→2011-11-09;
  'abc'→告警回落 2016-11-09;'0'/'-3'→clamp 2025-11-09;'2.5'→回落;闰日 2028-02-29→2018-03-01。
- resolve_history_period: 白名单 11 值 =(1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max)=
  yfinance 官方 period 全集;空白→默认'10y';'10Y'/'10year'/'3m'/'100y'→回落+旗标(大小写敏感)。
  env_config 零 print 纪律保持,告警由调用方打印(A2 延期③收口)。
- jp 采集器窗口对齐(A2 延期①收口): nikkei_series_window 缺省→2520;'max'/'ytd'→None 不截断;
  '1y'→252;'5y'→1260;非法→回落 2520+告警;旧 SERIES_WINDOW=251 硬截断已废除
  (jp_market_collector.py L50-79)。global/jp 共用同一 env_config 纯函数,非法值不再直通 yfinance。
- data_retention(P0 #4)/GDPC1(P1 #5)/ECB_DFR(P1 #7)/JP 全史(P1 #6)经 test_charter6_p0/p1
  全绿覆盖(76+53 项)。

### 5. Shiller 解析器 — **PASS**(三 fixture 独立手算对照)

我用自写 xlrd 解析(零仓库 import)重解析三个 fixture,与引擎 parse_ie_data 输出全量对照**全等**:

- charter6_shiller_min.xls: 表头第 3 行列头驱动定位;SPX_PE_TTM=逐行 P÷E
  (手算 2023-11: 4500/190=23.6842105263 ✓,2024-06 重复月取末行 4760/220=21.6364 ✓);
  SPX_CAPE 7 值,2024-04 空格如实缺席不插值 ✓;重复月 2024.06 保留最后(31.9 非 31.7)✓;
  'TR CAPE'列(27.x)因表头精确匹配'cape'被排除 ✓;尾部'Avg'汇总行跳过 ✓;
  'Note: monthly averages'行告警跳过 ✓。
- charter6_shiller_pe_col.xls: P/E 直用列路(25.5/26.0/26.5)——若误走 P÷E 会得 23.5,
  路径可证 ✓;CAPE 同步在场。
- charter6_shiller_nocol.xls: 无估值列→序列空+alerts 如实,main() exit 1 不产空壳文件 ✓。
- 月首日口径 'YYYY-MM-01' ✓;原子写 tmp+os.replace(shiller_collector.py L243-249)✓;
  源版本注记(sheet/表头行/行数/采用列/首末月)随档落盘 ✓;latest_vintage_asof_collected 注记 ✓。

### 6. coverage 语义 — **PASS**

- diff: `m.get('status','active') != 'deprecated'` → `m.get('status') == 'active'`
  (data_assembler.py L281-287,+注释"unavailable 登记项不计入覆盖")。
- 我方独立清点 registry: **104 active / 1 unavailable(SPX_PB) / 1 deprecated(REAL_SHORT),
  零缺 status 键** → 收紧前后差集恰为 SPX_PB 一条(旧码把"不可得"虚报为已覆盖,新码不报)。
  不虚报、不漏报。

### 7. 测试质量抽查 — **PASS**

- 四套 charter6 实跑: P0=76 项 / P1=53 项 / P2=67 项 / P4=82 项,全绿。
  相邻套件: e2e_frozen14=33 / afin_acceptance=33 / vendor_residue_guard / ia_cli=45,全绿。
- **测试确用独立管线**: test-[6] 的 build_feats(L279-317)与 ind_z(L324-333)为测试内自写实现,
  零调用被测函数;**D1 修复确认**: HY_OAS_d12m 已补进独立管线(L315-316),候选 2023-12
  (唯一 d12m z 可算者)距离 0.934889 进入双管线交叉验证——我的第三方管线同值(1e-6)。
- 我独立复算的手算期望值 ≥25 个(远超 10 个门槛),含 z×3、加权距离×6、归一权重×4 组、
  事后 pct/pp×9、聚合口径×4、事后起点/不缩窗×3、计数×4 组、分位×1。
- 断言无弱化: 范围内 tests/ 计 -4/+272 个 check();4 个删除均为计数随系统演进的合法更新
  (13步→15步、102→106 项),替换断言在场;frozen14 noncore_missing 保持精确等值断言
  (全程 12→13(P1)→12(收尾)净零变化,语义=fixture 齐备日如实)。

### 8. Skill 纪律文本 — **PASS**

- **既有禁令未动**: "何时不使用"两禁令(投资建议/收益承诺→拒绝;价格预测→不做)与
  纪律 1-13 逐字未变(唯一改动=纪律 4 句尾追加 E1/E2/E3 衔接引用,纯增益)。
- **新增纪律 15/16/17**(SKILL.md L76-78)与规格 §5 一致: 15=E1/E2/E3 定义+四层衔接
  (E1→事实/E2E3→假设/解读→推断,"E2/E3 环节永不进事实位");16=条件推演五行强制+单一情景
  不得单独呈现;17=analog 披露纪律+**违规句式负例在场**("历史上最像的时期是 X,当时 Y 上涨,
  所以现在 Y 会涨"=以事后冒充预测)+拒答如实转述不硬凑。
- references/research-discipline.md: E1/E2/E3 三级定义与披露模板("环节 k: [E1|E2|E3]「A→B」
  …陈述边界: 相关≠因果; --lag 只证时序先后不证因果")逐字收录;违规负例
  ("紧缩政策导致黄金下跌")与合规改写在场;五行模板+固定边界文案
  ("情景推演是条件逻辑演练,不是预测;…单一情景不得单独呈现(至少并列基准与反例情景)。")逐字;
  **巧合旗标四判据枚举已补全**(①单维主导②事后分歧③维度缺席④TOP-1 不分离,D4 收口)+
  归一事实随行条(norm_wsum/w_norm 转述不得略去,D3 技能侧收口)。
- 工作流 10→11 步(analog 插入第 6 步),旧步骤原文保留;已知边界新增 analog 拒答/估值条目。

---

## 缺陷与阻断清单

**阻断: 无。**

**新发现缺陷: 无**(我方 43 项独立复算+6 项窗口函数边缘+3 fixture 独立解析+别名/注入实验零失配)。

**延期(1 项,非阻断)**:
- DEP-1 Shiller Yale 真实源 live 首跑——需用户授权真实网络拉取(审计红线禁止代跑),
  engine-notes 已登记;上线前执行一次即可闭合。

## 观察(不改判定,供下轮参考)

- OBS-1 规格 §1.5 事后窗口径两句存在内部张力("基准=严格早于起点的末观测" vs
  "起点严格用 t>候选锚点月末的首个观测…不得回吸锚点月内数据")。实现取后者(起点=锚点月末后
  首观测,如 2022-12 候选的 SPX 起点=2023-01-28=1155 而非 2022-12-15=1000),规格作者已在
  Afin 交叉审查中裁定该读法。建议规格措辞清理,消除歧义。
- OBS-2 锚点"最新完整月"按 ≥80% 已启用维度判定可落在进行中月份(live 拒答路径锚点=2026-11,
  数据止于 11-08)——规格原文如此,无泄漏;建议未来输出明示"月内至今"或改已完结月判定。
- OBS-3 距离分位分母=可算距离候选数(len(ds)),与 N2 可能在个别数据形态下不同;引擎已有
  "共同特征距离可算候选仅 N 个"警示兜底,可接受。
- OBS-4 NIKKEI 窗口映射用近似(月≈21 交易日),已在代码注释披露;只影响 NIKKEI 深度,
  不进 analog 六维向量(US 序列),无金融正确性影响。

## 复算资产

- 独立管线: /tmp/fin_audit/indep_pipeline.py(43 检查,零仓库 import)
- 引擎侧驱动: /tmp/fin_audit/engine_driver.py / supp_driver.py / shiller_engine_driver.py
- Shiller 独立解析: /tmp/fin_audit/shiller_indep.py
- 实跑记录: 四 charter6 套件+四相邻套件全绿;`ia_cli.py analog` live 拒答 JSON 存
  /tmp/fin_audit/live_analog.json

— FRESH-FIN 独立金融审计员, 2026-11-10
