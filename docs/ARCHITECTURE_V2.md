# 架构V2 — 金融事实引擎与宏观研究质量架构(交付物A+B)

> 2026-10-17 第七轮重构交付。基线: f8281c8(v1流水线) → dev/fact-engine。
> 硬约束全程保持: 采集器/GLM接口/9论点/9观点/证据分级v2/定量触发器/预测生命周期/
> 每日观察/周报八节/月季报/JSON研究记忆/macOS自动化 — 全部保留且原样消费新底座。

## A. 架构差异(前→后)

### v1流水线(重构前)

```
采集器×4(各自算收益/各自口径) ──→ data/daily/*.json(键名/单位/日期格式各异)
                                    ↓ 每引擎自行"找最新文件"
        scorecard/correlation/assembler ←── 各取所需,口径漂移
                                    ↓
        GLM(数据说什么它信什么) ──→ 周报 ──→ 校验(首处匹配/最接近锚点放行)
```

三大根缺陷(spec §1):
1. **无权威事实源** — 每层自己解读采集JSON,键名歧义(GOLD=期货?现货?)、单位混用、
   前值/现值不分;
2. **研究截止不统一** — "最新文件"≠最新数据,采集滞后/重跑/缺天造成各引擎as_of不一致;
3. **校验缺陷** — 同源自证(锚点来自同一采集文件)、只查第一处提及、最接近锚点放行
   (SPX位置写SPY价格也能"通过")。

### v2六层架构(重构后)

```
L1 采集层(保留): global_market / china / macro / rate_economy / news /fed期货
     ↓ 只产原始观测(不再自算收益 — 统一收益引擎接管)
L2 金融事实引擎 scripts/fact_engine.py + config/metric_registry.json
     · 81指标注册表: metric_id/单位/日历/频率/身份(instrument/adjustment)/校验规则
     · normalize_*: 四类采集JSON → 事实记录(别名映射GOLD→GOLD_F、代码映射000001.SH→SHCOMP)
     · compute_period_returns: 全系统唯一收益口径(week/MTD/YTD/m1..m12,期前收盘基准)
     · validate_fact 12类校验: type/outlier/time/frequency(92天月度窗)/identity/
       continuity/formula/completeness/… → PASS/DEGRADED/FAIL + issues明细
     · 对账(reconciliation): 双源指标(如ZQ期货vs利率)交叉核对
L3 研究快照 scripts/snapshot_builder.py → research_snapshot_YYYYMMDD.json/.md
     · Gate A: core指标缺失/FAIL → 快照级状态(不阻断其余研究,但缺失不进结论)
     · 不可变: 已存在则拒写(须--allow-revision生成_v2,记revision_reason)
     · 产出锚点anchors_*.json(带fact_id/metric_id/obs_date/quality/tolerance)
L4 研究引擎(全部改吃快照,不再自行找文件):
     · macro_scorecard v2.0: 评分/体制/切换纪律(resolve_transition)/反事实归因/
       DATA_INSUFFICIENT态(缺失≠0分,不计入总分)
     · correlation_calculator: 注册表身份/ETF≠指数标注/实际交易日对齐/样本数
     · data_assembler: 数据包=快照渲染(统一收益/单位/前值标注/口径标签)
     · rate_expectations: 期货隐含=月均口径,禁换算降息次数
L5 GLM(只做解释): 输入=当日数据包(当日纪律: 无当日包拒绝生成,不回退旧包)
L6 Gate B scripts/data_validator.py:
     · 全量覆盖(re.finditer逐处核验,非首处即止)
     · 身份解析: canonical锚点比对;贴近同族非canonical→🚨疑似指标混淆(不放行)
     · 前值当现值专项拦截;bp/千分位/合并写法归一核验
     · 不可核验→⚠️待复核(不静默跳过);机器状态块(<!--...-->)与散文隔离
     · 报告日≠今日→自动改用报告当日锚点(跨日漂移≠报告错误)
```

### 关键行为变化对照

| 场景 | v1 | v2 |
|---|---|---|
| MTD基准 | 采集器各自定义(实测同一资产两口径差14pp) | 前一自然月最后观测(唯一实现,独立复算±0.01pp验收) |
| YTD基准 | 当年首日 | 上年末最后观测(严格期前) |
| 月度指标未发布 | 被判"过期"/漏报 | 92天有效窗,未发布≠无效;超窗DEGRADED披露 |
| 期货隐含利率 | (隐含−当前)/0.25="降息次数" | 月均有效利率口径+方向标签,数学上不可换算次数 |
| A股成交额 | "沪深两市"(实为沪全市+深成指成分) | 拆分SH_AMOUNT/SZ_COMPONENT_AMOUNT/CN_TOTAL_TURNOVER+口径WARN |
| 缺失指标评分 | 计0分 | 记metric_id+原因,不计分不进总分;维度<2可得→"数据不足不可判" |
| 报告数字校验 | 首处匹配+最接近锚点 | 全量+canonical身份+待复核;bp↔%双写法核验 |
| 快照 | 无 | 不可变+Gate A+全下游同源;重跑须--allow-revision出v2 |

## B. 事实引擎使用说明

### 指标注册表 config/metric_registry.json(81指标)

字段: `metric_id`(全系统唯一键) / `display_name` / `unit` / `calendar`(交易日历) /
`frequency`(daily/weekly/monthly) / `freshness.max_calendar_lag_days` /
`identity{instrument,adjustment}`(指数≠ETF≠期货) / `validation.range`(合理区间) /
`value_type`(level/pct/net_flow…) / `calc`(口径一句话)。

单位族: 价格类(pct变化) / 利率类(pp+bp,无pct) / 指数点 / 计数(绝对差) / 金额。

### 收益口径(spec §4.3,全系统唯一实现)

- **week**: end=≤as_of最后观测;基准=本周(ISO周)开始前最后观测
- **mtd**: 基准=前一自然月最后观测(严格<当月1日)
- **ytd**: 基准=前一自然年最后观测(非当年首日)
- **m1/m3/m6/m12**: 日历锚定−N自然月,会话收敛
- 数据不足→`{"available": false, "reason": …}`,绝不回填0
- 每个derived附basis_date/basis_value/formula/sessions

### 事实记录字段(§5)

`fact_id`(=metric_id@obs_date) / `metric_id` / `value` / `unit` / `value_type` /
`observation_date`(ISO) / `as_of` / `source{collector,file,retrieved_at,channel}` /
`calculation_ref`(派生值公式) / `identity` / `derived` / `quality_status` / `issues[]`

### 验收状态(2026-10-17,真实数据)

- Gate A: **PASS**(78事实,75 PASS/0 FAIL/0 DEGRADED,core缺失0)
- 独立外部基准8项全过: Treasury官息×3(0.000pp)/Coinbase BTC(0.01%)/
  PAXG金(0.56%)/新浪上证(0.00%)/FRED SPX(0.00%)/WTI期现(0.49%)
- 独立复算week/MTD/YTD: 引擎vs独立实现 ±0.01pp内(SPX/GOLD_F/SHCOMP/HSI)
- 回归: 15套件751断言全绿;真实周报审计62→4条(4条全属实,见REAL_REPORT_AUDIT.md)
