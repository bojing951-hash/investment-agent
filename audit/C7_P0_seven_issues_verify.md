# Charter 7 独立问题验证: 七大研究正确性问题逐条复现

- 验证人: C7 独立验证员(与 Charter 6 作者/实现者零共享上下文)
- 日期: 2026-11-10
- 基线: dev/charter7-research-v1 = main cca2e4a(只读复现,零代码改动/零网络)
- 数据面: data/daily 现役 research_snapshot_20261110.json + _v2(同日修订版在场)
- Python: ~/AI内容/venv/bin/python3
- 判定口径: CONFIRMED=复现成立 / REFUTED=复现不成立 / PARTIAL=部分成立

## 结论一览

| # | 问题 | 判定 |
|---|------|------|
| 1 | research_mode_gate.realtime_info_set 语义(同日_v2≠历史实时信息集) | **CONFIRMED** |
| 2 | analog 锚点/候选特征准入标准不一致→距离跨候选不可比 | **CONFIRMED**(机制+真实数据+构造例三证) |
| 3 | aftermath 起止口径(引擎+16.65% vs 手工+13.6%) | **PARTIAL**(口径未披露=成立; 13.6%数字本身=误算) |
| 4 | 跨频率特征与 36 月门槛冲突(信用维全缺席/GDP 永不参与) | **CONFIRMED** |
| 5 | 候选月份高度重叠/同周期重复计数 | **CONFIRMED** |
| 6 | 保留策略 vs 历史研究来源验证冲突 | **CONFIRMED**(模拟复现,冲突为前瞻性) |
| 7 | update --yes 触发付费模型 API | **PARTIAL**(周报环节=REFUTED; 新闻摘要环节=CONFIRMED) |

---

## 问题 1: research_mode_gate.realtime_info_set 语义 —— CONFIRMED

**原争议**: 同日修订版(_v2)在场时 realtime 门=available,但同日修订≠历史实时信息集;
realtime_info_set 可用应指"能重构过去时点 t 市场实际可见的数据版本",同日 _v2 对研究
2024-06 之类历史时点毫无帮助。

### 复现步骤
1. 读 `_has_vn_history`(ia_cli.py:489-497): 判据=data/daily 下
   `research_snapshot_{ymd}_v*.json` 文件存在性,ymd=**当前快照自己的 target_date**。
2. 读门构造(ia_cli.py:729-741): `vn_available = _has_vn_history(snap_ymd)` →
   `realtime_info_set: 'available(经 select_snapshot 点时取版)'`。
3. 读 `select_snapshot`(scripts/research_provenance.py:1279-1331): 同日多版本**取最高
   _vN**("确定性选择当日权威快照: 取最高修订版")。
4. 实跑 compare(当前时点+历史时点窗口)看 gate 字段。
5. `git show 70102d5 -- tests/test_afin_acceptance.py` 查 ⑧⑨ 改动。

### 证据
- 实跑 `ia_cli.py compare --metrics SPX,UST_10Y` →
  `"realtime_info_set": "available(经 select_snapshot 点时取版)"`(因
  research_snapshot_20261110_v2.json 在场)。
- **历史窗口同样 available**: `compare --metrics SPX,UST_10Y --start 2024-06-01
  --end 2024-06-30`(common 2024-06-03..2024-06-28, n=19)→ gate 仍
  `realtime_info_set: available`。门只看快照自身日期(20261110),与研究窗口无关。
- `select_snapshot('20240615')` / `('20240601')` → `None`("无当日研究快照");
  data/daily 全部快照仅 20261108/20261110 两天。**2024-06 时点的任何 vintage 数据
  不存在**,门却说 available。
- 即使收窄到同日语义,"经 select_snapshot 点时取版"也不成立: select_snapshot
  永远返回**最高**修订版(_v2),不可能返回"时点 t(修订前)可见"的 base 版
  (research_snapshot_20261110.json 在盘但无任何 API 可选它)。
- SKILL.md(.claude/skills/global-macro-research/SKILL.md:65)纪律 5 只在
  **blocked** 时禁止"用修订值冒充当时值"; available 时无任何纪律约束。
- 70102d5 测试改动(⑧): 由断言 `gate.realtime_info_set=blocked(现役单版本)` 改为
  分支断言 `_vn_here → available`,注释自述"两形态都是正确行为,以数据面为准";
  (⑨): 由"真实面无 _vN→恒 blocked"改为"门可用性⇔同日 _vN 在场性"。

### 影响评估
研究者在 2024-06 历史窗口查询时会读到"当时信息集=available",结合工作流第 7 步
("读研究模式门,确定本次回答允许的研究模式")可合法开展"当时信息集"叙事——但引擎
对 2024-06 无任何 vintage 数据,叙述必然建立在今日修订口径上=系统性冒充。原审计
"把冒充合法化"的担忧属实: 70102d5 之前测试锁保守形态,之后锁"在场即 available"。

### 修复方向
1. 门语义按**查询窗口**判定而非快照自身日期: realtime_info_set 应对窗口起点 t 报
   "data/daily 是否存在 t 日快照(_vN 任一版本)",否则一律 blocked;
2. 或最低限度改名/加注: `realtime_info_set(snapshot_day_only)` 并在文案明示
   "仅对快照当日有效,历史时点一律不适用";
3. select_snapshot 增加 `as_of` 参数(取≤as_of 的最高版本),否则"点时取版"名不副实;
4. 测试 ⑧⑨ 恢复语义断言(区分"当日可回放"与"历史可重构"两态)。

---

## 问题 2: analog 锚点与候选特征准入标准不一致 → 距离跨候选不可比 —— CONFIRMED

**原争议**: 锚点按锚点月 36 月标准弃特征;候选按各自月份标准准入;两者特征集不同
→逐候选取共有特征算距离、权重逐候选重归一(norm_wsum 逐候选不同)→距离跨候选不可比。

### 复现步骤
1. 读锚点特征装配(scripts/analog_engine.py:393-413): 特征须 `grids[k][m0]` 在场
   **且** `z_at`(≥36 月历史)有效,否则进 `features_dropped_at_anchor`。
2. 读候选装配(analog_engine.py:417-437): 每候选月 m 各自判 `z_at(grids[k], m)`,
   有效维度≥4(MIN_VALID_DIMS)即准入——**候选各自月份的 36 月标准**。
3. 读 `weighted_distance`(analog_engine.py:287-306): `common = [k for k in zs_a
   if k in zs_c ...]`,`wsum = sum(w over common)`,每特征权重除以**该候选自己的
   wsum**——逐候选重归一。
4. 实跑 `ia_cli.py analog --top 5` 对比各候选 features_detail 键集与 norm_wsum。
5. 构造边界例验证不对称行为。

### 证据
- **真实数据不对称**: TOP-5=2024-12/2025-01/2025-09/2025-10/2025-02(D=0.350061/
  0.384263/0.394110/0.408622/0.414041)。前 4 个候选 15 特征、norm_wsum=0.555556;
  **2025-10 仅 14 特征、norm_wsum=0.527778**——缺 UNEMPLOYMENT_level
  (UNEMPLOYMENT 月网格 2025-09→4.4 后直接 2025-11→4.5,2025-10 无观测,数据洞)。
  同一份 TOP-N 排名里两套距离基并存。
- **机制构造例**(直接调被测引擎 weighted_distance,权重 4×0.1):
  - 锚点 z 全 0;候选 A 仅 UNEMP 偏差 gap=1.0 → D_A=0.5000(wsum=0.4);
  - 候选 B 含与 A 相同的 UNEMP 偏差 1.0 **再加** VIX 偏差 0.5,但 UNEMP 数据洞
    → D_B=0.2887(wsum=0.3)。**偏差严格更多的候选 B 排到 A 之上**;
  - 对照(双方都剔除 UNEMP): D_A=0.0000 < D_B=0.2887,次序恢复正确。
  → 候选可因"自己偏差最大的特征恰好缺数"获得距离改善=排名可被数据洞操纵。
- 引擎自知且只披露不解决: anolog_engine.py:446-451 注释"某特征在具体候选上缺席由
  距离层的重归一吸收……候选间共有特征集不同时各候选的归一权重不同,归一事实必须
  随行,不得只在方法学文字里说明"。

### 影响评估
D 的定义逐候选变化(特征集∪权重基都不同),TOP-N 排名与 distance_percentile 跨候选
比较在严格意义不成立。当前真实数据下唯一不对称候选(2025-10)缺的是低权特征
(UNEMP w=1/36≈0.028),量级影响小;但机制上任何高权/高偏差特征缺席都可能翻转排名
(构造例已证)。披露(norm_wsum/features_detail)只解决"可审计",不解决"可比"。

### 修复方向
1. 距离基固定: 以锚点有效特征集(或全体候选特征集的交集)为**统一特征面**,
   缺席候选直接判无效(宁缺毋滥,与拒答哲学一致);
2. 或改排名字段: 报 `D_common`(统一基)为主排序,现有重归一 D 降级为参考字段;
3. 至少: 共有特征集≠锚点特征集的候选打 warning(目前仅 silently 少算)。

---

## 问题 3: aftermath 起止时间/收益率口径/观测窗口 —— PARTIAL

**原争议**: 候选 2024-12 的 SPX 事后 12 月引擎=+16.65%,按"锚点月末对齐"手工算≈
+13.6%;要求确定精确口径、四资产×四窗独立重算、检查披露。

### 复现步骤
1. 读代码(analog_engine.py:566-585): `next_first = _m_add(x['month'],1)+'-01'`;
   `i0 = 首个 date >= next_first 的观测`(=次月首个交易日);`end =
   _m_add(x['month'],k)+'-31'`(字符串上界,字典序比较下对 30 天月安全);
   `i_end = 最后一个 date <= end 的观测`;价格资产 `(v1/v0-1)*100`,利率 `v1-v0`(pp)。
2. 不经被测函数,从原始序列(wd.metric_series→SPX/UST_10Y/DXY/GOLD_F)独立手算
   TOP-1(2024-12)全部 4 资产×4 窗。
3. 枚举备选口径寻找 +13.6% 的来源。
4. 查 label 与 skill cli-contract 是否披露起止口径。

### 证据
- **精确口径**: 起点=候选锚点月**次月首个交易日**(2025-01-02,SPX 5868.55),
  终点=+N 月**月内最后观测**(12m→2025-12-31,SPX 6845.50)。四窗共用同一 i0
  (起点统一);泄漏规则注释明示"起点严格 t>候选锚点月末……不得回吸锚点月内数据"。
- **独立重算 vs 引擎(16/16 全对,≤1e-4)**:
  SPX: 1m +2.9305 / 3m −4.3742 / 6m +5.7323 / **12m +16.6472**(引擎 16.647217);
  UST_10Y(pp): +0.01 / −0.34 / −0.33 / −0.39;
  DXY: −0.9324 / −4.7354 / −11.4361 / −10.1563;
  GOLD_F: +5.3765 / +17.0026 / +23.9303 / +62.6489。
- **"+13.6%"是误算**: 真正的锚点月末对齐(2024-12-31 收盘 5881.63→2025-12-31
  6845.50)=**+16.39%**,与引擎差仅 ~26bp(月末日收盘 vs 次月首日开盘的跳空);
  13.5-13.6% 只在用 **2024-11-29**(11 月末,早一个月)做基点时出现
  (2024-11-29 6032.4→2025-12-31 6845.5=+13.48%)。原探针的口径差叙述不成立,
  其手工基点错了一个月。
- **披露缺失(成立部分)**: 输出仅有
  `label: '事后(候选锚点后 1/3/6/12 月, 非预测, 不参与相似度)'`,不写起点=次月首日/
  终点=+N月末,不随行 v0/v1 实际日期;skill cli-contract 的 aftermath 描述同样只有
  "× 1m/3m/6m/12m(价格 pct/利率 pp)+unavailable_horizons"。用户不读源码无法复现口径。
- 口径一致性: 四资产全为 daily 频(registry: SPX/DXY=index_point daily,
  UST_10Y=percent daily, GOLD_F=usd_per_oz daily),无日/月混算;1/3/6/12m 起点统一。

### 影响评估
引擎数学正确、确定、可复算(独立重算 16/16 吻合);"引擎 vs 月末对齐差 3pp"系
原审计自身基点错误,实际差 ~0.26pp。真实缺陷=**口径不披露**: 26bp 级系统性偏移
(跳空缺口)方向不定、无人知晓口径就无法比对其他数据源,属披露级而非数值级问题。

### 修复方向
1. aftermath 块随行实际起止观测日(`start_date/end_date/k`)与口径一句
   ("起点=次月首个交易观测,终点=+N月月内最后观测");
2. label/cli-contract 同步补口径文案;
3. 可选: 同时给 anchor month-end 基点参考值,两口径并列(差异=跳空)。

---

## 问题 4: 跨频率指标与 36 月门槛冲突 —— CONFIRMED

**原争议**: HY_OAS 族源端仅 3 年(2023-11 起)→d12m 在锚点仅 24 月→锚点弃用;
GDP 季频对齐月网格;ICSA 周频 mean4;问这些特征在候选侧的分布、信用维缺席范围、
维度缺席该披露还是该影响准入/可比性。

### 复现步骤
1. 重建特征网格(analog_engine.feature_grids)+逐候选 z_at(独立脚本,非引擎 run)。
2. 统计 73 个有效候选各特征的在场数与 HY_OAS_level 历史长度分布。
3. 查 GDP/ICSA 网格与源序列覆盖。

### 证据
- **信用维 0/73 全缺席**(非部分在场): 73 个有效候选中含任一 credit 特征的=0。
  HY_OAS_level 月网格 2023-11..2026-11(n=37): 候选月 hist 分布={0 月:49 个候选,
  1..24 月:各 1 个候选}——候选上限 2025-10 时 hist=24<36,全部弃用;锚点 2026-10
  恰好 hist=36 才有效。**锚点状态向量展示 credit z(HY_OAS_level z=+1.14,
  处于高位)但该维度对全部候选距离贡献恒为 0**(top[0].dims.credit.
  contribution_share=0.0)。
- HY_OAS_d12m / HY_IG_gap_d12m: 网格 2024-11 起(n=25),锚点 hist=24<36 →
  `features_dropped_at_anchor={"HY_OAS_d12m":"hist_24<36","HY_IG_gap_d12m":
  "hist_24<36"}`(已如实披露)。
- **GDP_yoy 永不参与**: US_REAL_GDP 源 n=40 季观测(2016-10..2026-07)→yoy 网格
  n=36(2017-12..2026-09)。36 月门槛对季频网格=36 个**季度**观测(9 年),仅
  2026-09 恰好达标——但它在锚点排除窗内(>2025-10);锚点月 2026-10 非季末月,
  `grids['GDP_yoy']['2026-10']` 不存在→**静默跳过**(不在 features_dropped_
  at_anchor,仅 state_vector.growth.coverage=0.5 间接可见)。73 候选中 GDP_yoy
  在场=0。
- 同类静默跳过: CPI/CORE_CPI/INDPRO/RSAFS 序列止于 2026-09 →锚点 2026-10 无值,
  全部静默缺席(inflation coverage 0.33 有 warning;growth 0.5 恰不触发<0.5 warning);
  SPX_PE_TTM 止于 2026-06 →锚点缺席,但**全部 73 候选在场**(计入候选的
  MIN_VALID_DIMS 维度数,却因不在锚点集永不进距离)。
- ICSA(周频 mean4): 521 周观测→月网格,72/73 候选在场,行为正常。
- 候选特征在场计数(73 候选): FED_FUNDS/VIX/UST/TIPS/CURVE/BEI/CAPE/PE_TTM=73,
  UNEMP/rv21/ICSA=72, NFP=70, RSAFS/INDPRO/各 d12m=61, CPI/CORE_CPI=60——
  候选准入(MIN_VALID_DIMS=4)部分依赖这些永不进距离的特征撑维度数。

### 影响评估
"六维相似"实际按 ≤5 维(本例 credit 恒缺)计算,且门槛的名义单位(月)对季频特征
隐性放大 3 倍(36 月→9 年)。维度缺席目前只部分披露(锚点侧 dropped 有录、锚点月
无值静默、候选侧仅 norm_wsum 隐含)。候选准入被缺席特征撑维度数+距离基逐候选漂移
(问题 2)说明**维度缺席已实质影响可比性,不止是披露问题**。锚点信用维 z=+1.14
的高位信息被完全丢弃,对"利率单维主导 0.74-0.87"的 TOP 结构(WARNING 已亮)是
重要遗漏变量。

### 修复方向
1. 特征/维度的"锚点月无值静默跳过"并入 features_dropped_at_anchor(带原因
   `no_value_at_anchor_month`),消除静默面;
2. MIN_HISTORY 按频率显式换算(季频=12 季=3 年)或在 normalization 注明单位;
3. 维度在全部候选缺席时强制 warning(目前 §1.7"维度缺席(<6)"判据只看锚点侧,
   anchor 恰 6 维→不触发);
4. 中期: 为 credit 维接入更长历史替代源(HY_OAS 源端 3 年授权窗是硬约束,应在
   disclosure 固定文案中声明"信用维自 2026-11 起对候选无效")。

---

## 问题 5: 候选月份高度重叠/同周期重复计数 —— CONFIRMED

**原争议**: TOP-5=2024-12/2025-01/2025-09/2025-10/2025-02——2024-12 与 2025-01
相邻月=同一宏观状态两次采样,被当两个独立相似期;现有 M≤M0−12 只排与锚点窗重叠,
不排候选互相重叠。

### 复现步骤
1. 读重叠排除逻辑(analog_engine.py:416-422): `cutoff=_m_add(m0,-12)`;
   `if m > cutoff: dropped_overlap`——唯一排除=与锚点特征窗重叠,候选之间无任何
   去重/聚类(grep 'overlap' 全文件仅此一处语义)。
2. 实跑 `analog --top 73` 取全排名,统计 TOP 内相邻月对距离关系。
3. 对比相邻候选的 aftermath 窗重叠与 dispersion 计算。

### 证据
- TOP-5 复现(确定性): 2024-12(0.3501)/2025-01(0.3843)/2025-09(0.3941)/
  2025-10(0.4086)/2025-02(0.4140)。含**两组相邻月对**: (2024-12,2025-01)与
  (2025-09,2025-10)。
- 全 73 候选排名中,排名紧邻且月份差=1 的对: mean|ΔD|=**0.0145**(n=6);
  月份差>1 的紧邻对: mean|ΔD|=0.0558——相邻月距离天然聚合(~4×更近),
  "TOP-N 多样性"被同周期重复占据(前 8 名中 2025-06/07/08 三连月再现同现象)。
- **aftermath 窗重叠**: 2024-12 的 12m 窗=2025-01-02..2025-12-31;2025-01 的
  12m 窗=2025-02-03..2026-01-30——**11/12 个月重叠**,两值 +16.65%/+15.76 高度
  同源;2025-09/2025-10 同理(SPX 12m +14.01/+10.63, 窗重叠 11 月)。
- **dispersion 膨胀**: `topN_aftermath_sign_agreement` 按 5 个样本计算
  (SPX_12m=1.0, GOLD_3m/6m=1.0…),去重到独立状态簇后实际只有 3 簇
  ({2024-12,2025-01}, {2025-02}, {2025-09,2025-10})——"5/5 同向"的表面一致性
  来自重复采样;输出无任何候选互重叠/窗重叠 warning。

### 影响评估
dispersion 与事后分歧判据(§1.7-2,n≥3 触发)的统计功效被重复计数虚增: 名义 n=5,
有效 n≈3;sign_agreement 高值会被误读为"跨相似期稳健"。对 TOP-1 本身影响有限
(2024-12 仍是最近邻),但对"相似簇"叙事与条件推演(纪律 16 引用 analog 作历史
相似证据)构成样本量虚报。

### 修复方向
1. TOP-N 输出按月份邻近聚类(如 gap≤2 月归同簇)或 top 内去相邻月
   (每簇取距离最小者),簇数与成员都披露;
2. dispersion/sign_agreement 改按**簇**计算(或同时报 per-cluster 值);
3. 最低限度: 相邻月对同入 TOP-N 时打 warning("TOP-N 含相邻月候选,
   属同状态重复采样")。

---

## 问题 6: 保留策略与历史研究来源验证冲突 —— CONFIRMED(前瞻性,模拟复现)

**原争议**: data_retention.py 90 天全量+月度 gzip 归档后,研究档案引用的日档/
snapshot 来源文件是否仍可解析?归档件 provenance 能否透明回读?已归档/删除文件
的研究记录回读行为=报错/静默缺失/能恢复?

### 复现步骤
1. 读 data_retention.py: 采集族前缀=macro_/global_/china_/japan_/jp_/ea_/
   rate_economy_/shiller_(行 29-32);>90 天→每 (前缀,扩展名,月) 保留最后一份
   gzip 进 data/daily/archive/,其余删除;研究层前缀不动。
2. 读 provenance 实体核验链: sources_status_problems(data_dir 给出时 isfile+sha256
   重算, research_provenance.py:716-750)→ recompute_gate_a → gate_status →
   verify_meta_gate_a → verify_anchor_batch;report_generator.py:565/636/656 以
   data_dir=_daily 调用;research_history_query.load_metric_series 对 macro 走
   resolve_inputs(新鲜度窗 7 天)。
3. 临时目录构造模拟(fixture 可信根=官方测试授权缝): 建 macro_2026010{5,12,9}.
   json+macro_20260126.json+引用它的 sources_status(含 sha256)→验证 CLEAN→
   实跑 prune_daily_archives(now=2026-11-10)→再验证。
4. grep 全仓 data/daily/archive 的读取方。

### 证据(模拟输出)
- **A. 保留前**: `sources_status_problems(..., data_dir=td, trusted_root=fixture)`
  → **CLEAN**(零问题)。
- **B. 保留执行**: kept=0;archived=['macro_20260126.json'](该月代表档→
  archive/*.gz);deleted=['macro_20260105/0112/0119.json']。
- **C. 保留后(带 data_dir 重验)**:
  `["sources_status['macro']声明EXACT但来源文件在采集目录不存在:macro_20260126.json
  (声明批次不可证明)", "…内容摘要不可读取…No such file or directory"]` →
  **Gate A 实体核验失败**。
- **D. data_dir=None(纯历史重验口径)**: CLEAN——结构层通过(两级口径 by design)。
- **E. 归档件可手动 gunzip 读回**(obs_date 完好)。
- **F. 全仓无任何代码读 data/daily/archive/**(grep 命中仅 data_retention.py 自述
  与 run_weekly 注释)——**无透明回读路径**;非代表档(每月仅 1 份幸存)本地永久
  丢失,"可全量重拉"需网络,且重拉字节几乎必变→FIX7-05 sha256 内容绑定仍会拒。
- 附: resolve_inputs('20260801')(真实 data/daily,只读)→ 全通道 None;
  research_history_query 按旧 source_date 查 macro 序列将 raise LookupError
  ("新鲜度窗内无可用 macro 采集档")=**报错**,非静默缺失。
- 现役 data/daily 实际仅存 2026-11-01..11-10(45 个 json,无 archive/ 目录),
  冲突尚未物质化——**day-91 起自动生效**(run_weekly 步骤 15/15 每周跑)。

### 影响评估
retention 自述"研究层文件一律不动…snapshot 选档/溯源链依赖它们留在 data/daily"
只对 research_snapshot_*/anchors_* 成立;但溯源链的**实体层**指向的是采集档
(macro_*.json),它们恰是清理对象。>90 天后: 旧快照/锚点的带 data_dir 重验
(报告再生成链、verify_anchor_batch)将 fail-closed;按旧日期的历史序列查询报
LookupError;归档 gz 无读者。矛盾真实存在,只是该仓数据尚年轻。

### 修复方向
1. sources_status_problems 实体核验增加归档回退: file 不在 daily 时查
   `archive/{file}.gz`(gunzip 后 sha256 比对)——研究层"可追溯"承诺才有落点;
2. 或 retention 把"被现存 research_snapshot/anchors 的 sources_status 引用的
   采集档"列入保留豁免(快照在,其来源档不得清);
3. resolve_inputs 支持显式 archive 读取模式供历史查询;
4. 短期最低: 在 retention 报告与 run_weekly 步骤说明里明示"90 天后带 data_dir 的
   来源实体核验将失败,历史重验须走 data_dir=None 口径"。

---

## 问题 7: update --yes 未经单独授权触发付费模型 API —— PARTIAL

**原争议**: update --yes→run_weekly 流水线含"生成周报"步骤;若环境配齐
MODEL_API_KEY/MODEL_BASE_URL/MODEL_NAME(Charter 5 三参),全流程会否在周报/研究
环节自动调用付费模型 API?

### 复现步骤
1. 读 cmd_update(ia_cli.py:339-368): --yes → subprocess 跑 run_weekly.py(仅此)。
2. 读 run_weekly.py steps(150-195): 15 步清单;步骤 4/15=news_collector.py
   (非关键);无 report_generator 步骤,末尾只打印"📝 下一步: 生成周报
   python3 scripts/report_generator.py"(301-317)。
3. 逐个 grep 15 个管线脚本的模型调用点(OpenAI/MODEL_API_KEY/chat.completions)。
4. 读 news_collector 门禁(735-747)与调用(575-607);读 model_runtime_config
   (env_config.py:76-90);查 report_generator 门禁与 run_daily.sh。
5. 查当前环境与 .env 的 MODEL_* 状态(只看名,不看值)。

### 证据
- **周报环节=REFUTED**: report_generator.py 不在 update/run_weekly/run_daily 管线
  内;run_daily.sh:77-80 明确注释"不在本文本内 nohup 后台启动 report_generator.py",
  周报独立调度(com.investment.weekly)或手动;report_generator 无三参时
  RuntimeError fail-fast(行 505)。15 管线脚本中 14 个零模型调用。
- **新闻摘要环节=CONFIRMED**: 步骤 4/15 news_collector,`_mcfg =
  model_runtime_config(); if not _mcfg['complete']: 确定性回退; else:
  generate_news_summary(classified)`(行 738-747)——**三参齐备即自动发起付费
  调用**,单次 max_tokens=4000,引用校验失败再受控重试 1 次(≤2 次调用/跑)。
  唯一门禁=env 三参齐备,无 --no-model 旗标、无费用提示。
- **授权面错位**: update 确认文案只说"会真实运行采集流水线(…含外部数据源调用)"
  ——提数据源,不提模型花费;SKILL 纪律 8 把 update --yes 整体当"用户明确要求"
  的费用动作,但用户授权意图是采集。
- **文档与行为不符**: ia_cli ENV_KEYS(ia_cli.py:63-64)称三参"AI 解释/周报生成
  共用…不配仅影响 AI 解释与周报叙事层";docs/USER_GUIDE.md:58 同口径——
  **新闻摘要这个第三消费点未在任何文档出现**。
- 当前环境: MODEL_* 实际未配置(env 无真值,.env 不存在)=Agent Native,
  现状零付费调用;冲突在用户配齐三参后立即物质化(含 launchd 调度的
  run_daily.sh→run_weekly 无人值守路径)。

### 影响评估
"run_weekly 含生成周报步骤"不成立;但"update --yes 在配齐三参的机器上自动花
模型钱"成立,且发生在无人值守调度下最隐蔽。付费调用完整清单(条件: MODEL_*
三参齐备): ① update --yes / run_weekly / run_daily.sh → 步骤 4 news_collector
(自动,1-2 次);② research --explain / ask_local(workbench_data→
model_conclusion_client,用户显式发起);③ report_generator(手动/独立调度,
fail-fast);④ monthly_review/quarterly_outlook(手动)。管线内自动点仅 ①。

### 修复方向
1. update/run_weekly 增加 `--no-model`(或缺省跳过新闻模型摘要,显式 --with-model
   才调),把费用决策从"env 配置"升级为"逐次授权";
2. update 确认文案补一句"若已配置 MODEL_* 三参,新闻摘要步骤将调用付费模型 API";
3. ia_cli ENV_KEYS 与 USER_GUIDE 的三参说明补上新闻摘要消费点;
4. news 摘要落档时记录 token 用量/调用次数,费用可审计。

---

## 复现环境备注

- 全部命令在 dev/charter7-research-v1(cca2e4a)工作区只读执行;输出文件
  /tmp/analog_top5.json、/tmp/analog_all.json、/tmp/c7_verify/* 为临时产物。
- analog 输出结构注记: `data['candidates']` 为统计 dict(scanned=1871/valid=73/
  dropped_overlap=13/dropped_insufficient=1785),逐候选明细在 `data['top']`
  (rank/candidate_month/distance/…);锚点=2026-10(最新完整月)。
