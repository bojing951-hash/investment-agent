# IA-P0-2-W2-FIX1-04 专项政策评估: DFEDTARU/DFEDTARL 45天窗口复核

- 任务: IA-P0-2-W2-FIX1 (W2-POLICY-001)
- 日期: 2026-10-29
- 评估对象: `config/metric_registry.json` 中 DFEDTARU / DFEDTARL 的
  `freshness.max_calendar_lag_days=45`(当前生效值, Agent 4 验收质疑对象)
- 状态: **已批复方案A(45→10天), 2026-10-29**(批复原文见
  `P0_2_W2_FIX1_APPROVAL_EVIDENCE.md` §5; 注册表与FRESHNESS政策文档已同步)

---

## 1. 官方序列事实(FRED, 2026-10-29检索)

FRED 序列页 https://fred.stlouisfed.org/series/DFEDTARU :

- 名称: **Federal Funds Target Range - Upper Limit**(DFEDTARL 为 Lower Limit
  对称序列, 同一来源同一频率)
- 来源: Board of Governors of the Federal Reserve System (US), 经 FOMC
  Press Release
- **频率: "Daily, 7-Day"**(官方标注; 非月频/非事件频)
- 季调: Not Seasonally Adjusted; 单位: Percent
- 更新: 每个发布日更新(页面显示 Updated: Oct 28, 2026 7:01 AM CDT,
  next release Oct 29, 2026 → 逐日发布)
- 官方Notes原文(关键句):
  > "This series represents upper limit of the federal funds target range
  > established by the Federal Open Market Committee."
  > "**The data updated each day is the data effective as of that day.**"

**解读**: FRED 对该序列每个发布日都发布一条**当日生效**的观测记录——
无论 FOMC 是否开会、目标区间是否变动, 观测戳(obs_date)逐日推进, 值在
会期间隔内保持不变。即: 这是一个**日频观测序列**, 不是"事件发生时才有
新观测"的事件序列。

## 2. 概念辨析(Agent 4 指出的两个被混淆的概念)

| 概念 | 内容 | 由什么承载 |
|---|---|---|
| A. 政策状态有效性 | FOMC 决议的目标区间在会后持续数周有效, 直至下次会议改动 | **事实的值本身**(upper/lower limit 数值) |
| B. 数据/观测新鲜度 | 采集管道是否仍在逐日获取当日生效值 | **事实的观测日(obs_date)与滞后窗** |

关键事实(由§1官方Notes推出): 因为"the data updated each day is the data
effective as of that day", **观测戳每日推进、与决议是否变化无关**。
因此:

- 45天窗**度量的不是概念A**(政策状态从未由窗口承载——值不变期间窗口
  判定恒为"新鲜", 与政策状态无关);
- 45天窗**唯一实际作用是把概念B的采集中断检测延迟到45天**——8~44天的
  采集管道中断完全静默;
- 原批准理由("FOMC约6-7周一会, 45天≈会期间隔, 超期=跨会议未更新采集")
  把概念A的周期错误映射到了概念B的窗口上: 会期间隔内观测照常逐日更新,
  窗口本不需要覆盖会期间隔。

## 3. 当前45天窗口的具体影响(不改动时)

- **正常情形(无政策变化, 无采集故障)**: 每日新观测, 滞后0-4天(假日簇),
  三方案下 Gate A/Gate B 均无任何披露 → 行为无差异。
- **采集短时中断(1~44天)**: DFEDTARU/L 锚点滞后最长45天仍判"新鲜",
  Gate A 不披露 → **采集故障最长45天不可见**(同族 DFF=10天早已在
  10天披露, 同一管道两指标检测窗相差4.5倍)。
- **Gate A/Gate B**: W2后统一由注册表驱动, 两门同用45 → 无门间差异,
  但同受上述检测延迟影响。
- DFEDTARU/L criticality=core: 中断期间若快照照常产出, 正式研究在
  不知情下引用最长45天前的目标区间值(值大概率仍正确——这正是窗口
  宽松的隐蔽性所在)。

## 4. 方案A: 窗口 45→10(与同族 DFF 对齐)

- 依据: §1官方日频语义; 10自然日覆盖美国假日簇(感恩节+圣诞最长连休
  ≈4个营业日≈7-9自然日; 参见round-1已批准的 DFF=10 同一论证)。
- 政策状态语义不受影响: 决议变化由值直接呈现, 不依赖窗口; 概念A在
  任何窗口下都被正确表达(值不变=状态不变)。
- 效果: DFEDTARU/L 采集中断自第11天起 DEGRADED 披露(与DFF一致);
  正常假日簇零误报。
- 改动面: 注册表2个数值(45→10); 无代码改动(freshness_policy已注册表驱动)。
- 风险: 无已知误报情形(该序列逐日发布, 无春节式8-9天休市簇)。

## 5. 方案B: 双轴建模(采集新鲜度+政策状态有效期分离)

- 内容: 保留一个短采集窗(如10天)度量概念B; 另行为"当前目标区间"建
  派生概念/语义层承载概念A(如 `FED_TARGET_RANGE_CURRENT`, 有效期=至
  下次FOMC决议, 45天或事件驱动)。
- 收益: 概念A/B在数据模型层显式分离。
- 代价: 新增派生指标/语义概念(注册表+事实引擎+锚点生成链路), 与注册表
  单窗口模型冲突; 而概念A本已由值本身完整承载(见§2), 该分离增加的是
  结构复杂度而非表达能力。
- 与指令§八的关系: 指令要求评估方案B, 未要求实施; 若用户选择方案B,
  属新功能开发, 建议列入后续工作包(非本轮FIX1范围)。

## 6. 三方案对照表

| 维度 | 维持45(现状) | 方案A: 10天 | 方案B: 双轴 |
|---|---|---|---|
| 采集中断检测延迟 | 最长45天 | 10天 | 10天 |
| 正常假日簇误报 | 无 | 无 | 无 |
| 政策状态表达 | 由值承载(正确) | 由值承载(正确) | 显式派生层 |
| 改动面 | 0 | 注册表2数值 | 新概念+全链路 |
| 审批状态 | round-1已批准(2026-10-29T07:57:50Z) | **需新批准** | 需新批准+新范围 |
| 与DFF(同族,已批10)一致性 | 不一致(4.5×) | 一致 | 一致 |

## 7. 建议

**建议方案A(45→10)**: 官方"Daily, 7-Day"语义下, 45天窗口唯一实际效果是
掩盖采集中断; 10天与同族DFF一致、零误报、改动最小。方案B的概念分离
在"值本身承载政策状态"的现状下不增加表达能力, 若需要可作为后续增强。

## 8. 审批状态与决策结果

- 原始批准: DFEDTARU/L=45 于 2026-10-29T07:57:50Z 由用户在
  AskUserQuestion round-1 选择"45天（注册表，推荐）"(verbatim证据见
  `P0_2_W2_FIX1_APPROVAL_EVIDENCE.md` §3)。
- Agent 4 验收引入了原批准未考虑的官方证据(§1逐日发布语义), 按指令
  §八"不得擅自改成任何数值", 本项重新提交正式决策请求。
- **决策结果(2026-10-29): 用户批复"方案A：45→10天（推荐）"**(批复
  原文逐字见 `P0_2_W2_FIX1_APPROVAL_EVIDENCE.md` §5)。
- 执行: 注册表 DFEDTARU/DFEDTARL 窗口45→10; `docs/P0_2_W2_FRESHNESS.
  {json,md}` 同步更新; 受影响测试期望更新(逐项理由见交付文档§15);
  全量回归+CI。

## 9. 引用

- FRED DFEDTARU: https://fred.stlouisfed.org/series/DFEDTARU
  (Frequency "Daily, 7-Day"; Notes: "The data updated each day is the
  data effective as of that day."; 检索于2026-10-29)
- FRED DFEDTARL(对称): https://fred.stlouisfed.org/series/DFEDTARL
- 原始批准记录: `P0_2_W2_FIX1_APPROVAL_EVIDENCE.md` §1/§3
