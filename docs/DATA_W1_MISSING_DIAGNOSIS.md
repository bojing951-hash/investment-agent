# DATA-W1 · 缺失指标只读诊断报告 — MARGIN_BAL / SH_PE(R004-D4 承接)

> **契约**: IA-DATA-W1-AC-v1.0 §四 DI-AC-05
> **日期**: 2026-11-02(UTC)
> **诊断分支**: `dev/data-inventory`(自 `dev/p0-2-w5-fix3`@`1ddfb65ec78f4358b7a004be8ef5d8916ba0f052` 切出)
>
> ## ⚠️ 只读声明
> **本报告为只读诊断,未修改任何生产代码与数据。** 全部证据为本地静态取证
> (仓库源码引用 + `data/daily/` 实档核查);标注 **U** 的项需外部源/生产日志才能
> 定夺,如实登记不确定,不为凑确定结论而猜测。未实施任何修复——修复属数据线
> 后续工作包(另拟合同)。

## 0. 指标命名对照(契约§七/附则要求)

| 立项原文 | metric_registry 实取条目名 | source_symbol | 对照结论 |
|---|---|---|---|
| MARGIN_BAL | `MARGIN_BAL` | `margin` | 完全一致,无别名 |
| SH_PE | `SH_PE` | `valuation` | 完全一致,无别名 |

registry 实取位置: `config/metric_registry.json`(2026-11-02 实读;条目原文摘录见各指标§1)。

---

## 1. MARGIN_BAL(两融余额·沪深)

### 1.1 期望数据链路(registry → 源文件 → 字段路径)

registry 条目实取原文(`config/metric_registry.json`,实读摘录):

```json
{
 "metric_id": "MARGIN_BAL",
 "display_name": "两融余额(沪深)",
 "source": "china_market_collector",
 "source_symbol": "margin",
 "asset_class": "leverage",
 "frequency": "daily",
 "unit": "cny_100m",
 "calc": "融资融券余额存量(亿元)",
 "validation": {"range": [8000, 45000], "max_week_abs_move": 3000},
 "freshness": {"max_calendar_lag_days": 10}
}
```

期望链路(每一环引实档):

1. **采集**: `scripts/china_market_collector.py` `fetch_margin()`(L300-326)调
   tushare `_pro().margin(trade_date=…)`,产出写入 china 日档 `margin` 块
   (装配见同文件 L555 `all_data['margin'] = fetch_margin()`);
2. **源文件字段路径**: `data/daily/china_YYYYMMDD.json` → `["margin"]["balance"]`(值,
   亿元)+ `["margin"]["date"]`(观测日);
3. **事实引擎消费**: `scripts/fact_engine.py` L364-366(原文):

   ```python
   mg = data.get('margin') or {}
   if mg.get('balance') is not None:
       add("MARGIN_BAL", mg.get('balance'), mg.get('date'))
   ```

4. **快照锚点**: `scripts/snapshot_builder.py` L168-176 `'MARGIN_BAL': 'china.margin.balance'`;
5. **新鲜度键**: `scripts/freshness_policy.py` L419 `'china.margin.balance': 'MARGIN_BAL'`。

### 1.2 断点定位

**双层断点**(当前层 + 结构层,二者叠加):

- **断点①(当前直接原因)·源端缺失**: 实档 `margin: null` → 引擎侧
  `data.get('margin') or {}` 得空字典 → `mg.get('balance') is None` → 不产事实。
- **断点②(结构性)·映射/口径断裂(采集器产出键 ≠ 引擎期望键,且口径不同)**:
  采集器 `fetch_margin()` 成功路径(L314-319)产出的键为
  `date / rzye / rqye / rzye_billion`,**没有 `balance` 键**;且
  `rzye`=融资余额(单侧)、注册口径=`融资融券余额合计`(融资+融券),
  `rzye ≠ 合计`。`scripts/historical_coverage_audit.py` L865-867(FIX1-03 身份
  纪律,原文摘录):

  > `# FIX1-03身份纪律: 只有同口径balance(两融余额合计,注册语义)才是`
  > `# MARGIN_BAL权威观测;rzye_billion=融资余额(亿元)/rzye=融资余额(元)/`
  > `# rqye=融券余额(元)均≠两融余额合计,缺同口径证据不得写入MARGIN_BAL`

  即:**即使 tushare 源恢复、`margin` 块有值,当前键名/口径下引擎也不会产出
  MARGIN_BAL 事实**(断点②独立成立)。

### 1.3 证据

**A. data/daily 实档核查**(2026-11-02 本地实读,python json 逐键):

```
20261101 | timestamp: 2026-11-01 23:30:49 | a_share_indices: 0 | hk_indices: ['^HSCE', '^HSI'] | margin: None | valuation: {} | turnover: None | southbound: None
20261102 | timestamp: 2026-11-02 01:55:40 | a_share_indices: 0 | hk_indices: ['^HSCE', '^HSI'] | margin: None | valuation: {} | turnover: None | southbound: None
```

两日 `margin` 均为 `null`;同文件内 **tushare 依赖通道全部空/null**
(`a_share_indices: 0`、`turnover: null`、`southbound: null`),而 **yahoo 通道
`hk_indices` 有值**——与 W5 已冻结披露的"china-tushare 结构性阻断"特征一致
(docs/P0_2_W5_DELIVERY.md §Gate A: "Gate A=DEGRADED(非核心MARGIN_BAL/SH_PE缺失)为
该数据日真实状态")。

**B. 采集器源码引用**(`scripts/china_market_collector.py` L304-326,关键原文):

```python
    # 尝试最近几天（可能有延迟）
    for days_back in range(0, 5):
        try:
            date = (datetime.now() - timedelta(days=days_back)).strftime('%Y%m%d')
            df = _pro().margin(trade_date=date)
            if df is not None and len(df) > 0:
                ...
                result = {
                    'date': date,
                    'rzye': ..., 'rqye': ..., 'rzye_billion': ...,
                }
                return result
        except:
            continue
    print("  ⚠️ 融资融券数据暂不可用")
    return None            # ← 实档 margin:null 的直接来源
```

失败路径无错误留痕(裸 `except: continue`),故**采集时刻的具体报错不可本地
复盘(标 U,见§1.5)**;但"全部 tushare 通道同时空 + 限流治理工作包(W5-RERUN,
docs/P0_2_W2_FIX2_APPROVAL_FORENSICS.md 之后 R005 立项)存在"这一组合证据,
支持"tushare 接口在采集时刻不可用/被限流"的定性。

**C. 历史档案佐证(断点②早有在案)**:

- docs/P0_GATE_A_REPAIR_04.md L125(原文): "MARGIN_BAL/SH_PE在全部11份生产快照中
  缺席——china采集器实况JSON用`rzye/rzye_billion`与按指数代码的`pe_ttm`键,归一化
  器期望`balance`/`pe`。"
- docs/P0_2_W1_REGISTRY_AUDIT.md L136: MARGIN_BAL 行登记
  `source_symbol ∅(实为 china通道margin)`、通道=china_market_collector。

### 1.4 建议修复方向(仅建议,不实施)

1. **源恢复**(`断点①`): 待 RERUN 线 tushare 限流治理落地后复测
   `_pro().margin()` 可得性;或评估替代同口径上游。
2. **口径与键的桥接**(`断点②`,须新合同): 两条路线二选一——
   a. 采集器新增同口径 `balance`(两融合计): 需上游直接提供"两融余额合计"
      字段,或经用户/合同确认合计公式与单位后方可由 `rzye+rqye` 计算
      (FIX1-03 纪律明令禁止自动推算);
   b. 变更 registry 口径为"融资余额": 属注册语义变更,须走合同变更流程。
3. 修复涉新数据源/凭证 → 按契约§七先上 PENDING。

### 1.5 需外部源定夺项(如实标 U)

- **U-1**: 2026-11-01/02 采集时刻 tushare `margin` 接口的具体失败原因
  (报错类别: 限流/无权限/数据未出)——本地静态不可得(采集器失败不留痕);
  需生产日志或外部复测,属 RERUN 线取证范围。
- **U-2**: tushare 是否提供与注册口径一致(两融余额合计,亿元)的直接字段
  ——需上游文档/接口实调确认。

---

## 2. SH_PE(上证市盈率)

### 2.1 期望数据链路

registry 条目实取原文(`config/metric_registry.json`,实读摘录):

```json
{
 "metric_id": "SH_PE",
 "display_name": "上证市盈率",
 "source": "china_market_collector",
 "source_symbol": "valuation",
 "asset_class": "valuation",
 "frequency": "daily",
 "unit": "ratio",
 "calc": "上证指数整体PE(TTM)",
 "validation": {"range": [8, 40], "max_week_abs_move": 5},
 "freshness": {"max_calendar_lag_days": 10}
}
```

期望链路(每一环引实档):

1. **采集**: `scripts/china_market_collector.py` `fetch_valuation()`(L328-357)调
   tushare `_pro().index_dailybasic(ts_code=…)` 产出 `valuation` 块
   (装配见 L558 `all_data['valuation'] = fetch_valuation()`);
2. **源文件字段路径**: `data/daily/china_YYYYMMDD.json` → `["valuation"]["pe"]`(值,
   ratio)+ `["valuation"]["date"]`(观测日);
3. **事实引擎消费**: `scripts/fact_engine.py` L367-369(原文):

   ```python
   val = data.get('valuation') or {}
   if val.get('pe') is not None:
       add("SH_PE", val.get('pe'), val.get('date'))
   ```

4. **快照锚点**: `scripts/snapshot_builder.py` L176 `'SH_PE': 'china.valuation.pe'`;
5. **新鲜度键**: `scripts/freshness_policy.py` L420 `'china.valuation.pe': 'SH_PE'`。

### 2.2 断点定位

**三层断点**(叠加):

- **断点①(当前直接原因)·源端缺失**: 实档 `valuation: {}`(空对象)→
  `val.get('pe') is None` → 不产事实。`fetch_valuation()` 对每个指数独立
  try/except(L334-355),全部失败时返回空 `results = {}`。
- **断点②(结构性)·映射断裂(格式)**: 采集器**新格式**为嵌套结构
  `{指数代码: {pe_ttm, pb, …}}`(L344-351),**没有扁平 `pe` 键**——引擎期望
  `valuation['pe']`(旧格式)。即使 tushare 恢复,引擎也不消费嵌套 pe_ttm。
- **断点③(结构性)·身份断裂(标的指数不在采集清单)**:
  `VALUATION_INDICES`(L88-92,原文)为:

  ```python
  VALUATION_INDICES = {
      '000300.SH': '沪深300',
      '000905.SH': '中证500',
      '000852.SH': '中证1000',
  }
  ```

  **不含上证指数 `000001.SH`**——即使桥接 `pe_ttm→pe`,采到的也是沪深300/
  中证500/中证1000 的 PE,与注册语义"上证指数整体PE(TTM)"**非同身份**,
  按身份纪律不得冒充。注: 价格通道的 `A_SHARE_INDICES`(L42-49)**含**
  `000001.SH`,即采集器具备上证代码知识,只是估值通道未纳入。

### 2.3 证据

**A. data/daily 实档核查**: 同§1.3-A(两日 `valuation: {}`;tushare 通道全空、
yahoo 通道有值——同一阻断特征)。

**B. 采集器源码引用**(`scripts/china_market_collector.py` L328-357 关键原文):

```python
def fetch_valuation():
    """采集指数估值（PE/PB）"""
    ...
    for code, name in VALUATION_INDICES.items():
        try:
            df = _pro().index_dailybasic(ts_code=code, ...)
            ...
            results[code] = {
                'name': name, 'date': str(latest['trade_date']),
                'pe_ttm': ..., 'pb': ..., ...
            }
        except Exception as e:
            print(f"  ❌ {name}: {e}")   # 异常仅打印,结果字典不收该指数
    return results                        # 全部失败 → {} ← 实档 valuation:{} 的直接来源
```

**C. 历史档案佐证(断点②③早有在案)**:

- docs/P0_2_W4_DELIVERY.md L44(原文): "…valuation嵌套pe_ttm(注册SH_PE语义=
  上证PE,非同身份,**不得**归SH_PE)…"
- docs/P0_2_W4_DELIVERY.md L103(原文): "SH_PE在新格式时代的可采集性(需上游
  确认上证PE数据源;本轮按身份矩阵如实归MISSING,不把300 pe_ttm冒充)。"
- docs/P0_GATE_A_REPAIR_04.md L125: 见§1.3-C(键名桥接未整改的在案登记)。
- `scripts/historical_coverage_audit.py` L896-904: 仅 `val.get('pe')`(扁平,
  旧格式)入 SH_PE 权威;嵌套 `pe_ttm` 一律 `unmapped` 披露
  ("新格式嵌套估值(仅300/500/1000;注册SH_PE语义=上证PE,非同身份)")。

### 2.4 建议修复方向(仅建议,不实施)

1. **源恢复**(`断点①`): 同§1.4-1(RERUN 限流治理后复测 `index_dailybasic`)。
2. **身份优先**(`断点③`,修复设计的前置): 确认"上证指数整体PE(TTM)"的可采
   上游——候选: tushare `index_dailybasic` 对 `000001.SH` 的可得性(**U-3**);
   或其他授权源。**不得**以 300/500/1000 的 pe_ttm 冒充(FIX1-03/W4 纪律)。
3. **格式桥接**(`断点②`): 与身份修复合并设计(如: 估值通道纳入 000001.SH 后,
   采集器按引擎期望产出 `valuation.pe`+`date`,或引擎侧显式映射嵌套键——
   二者择一,须新合同定夺,不在本轮实施)。
4. 修复涉新数据源/凭证 → 先上 PENDING。

### 2.5 需外部源定夺项(如实标 U)

- **U-3**: tushare `index_dailybasic` 是否覆盖 `000001.SH`(上证指数)及其
  PE(TTM) 口径与注册语义(整体法 TTM)的一致性——需上游文档/接口实调确认,
  本地静态不可得。
- **U-4**: 2026-11-01/02 采集时刻 `index_dailybasic` 的具体失败原因(同 U-1,
  失败仅打印不落档,需生产日志/复测)。

---

## 3. 共性结论与承接说明

- **共性**: 两指标同源(china_market_collector, tushare pro 通道)。当前缺失的
  **直接原因**同为 tushare 通道在 2026-11-01/02 采集时刻整体失败(实档特征:
  tushare 通道全空/null、yahoo 通道有值);**结构性根因**各自独立在案
  (MARGIN_BAL=键/口径断裂;SH_PE=格式+身份断裂),即源恢复后二者**仍不会**
  自动恢复——这与 R004-D4"长期缺失"的历史观察一致(自 P0_GATE_A_REPAIR_04
  在案的 11 份快照起持续 DEGRADED 披露)。
- **R004-D4 承接**: 本报告将该缺陷的根因定位到"源端缺失 + 采集器↔引擎
  键/口径/身份断裂"三层,后续修复需数据线第 2 包按§1.4/§2.4 另拟合同
  (涉新源/凭证先上 PENDING)。
- **疑似既有缺陷登记(只登记不修)**: `fetch_margin()` 的裸 `except: continue`
  (L322-323)吞掉全部异常且不留错误类别痕迹,是 U-1/U-4 不可本地定夺的直接
  原因——建议未来工作包考虑采集失败留痕(仅建议)。
