# Charter 8 复用审计(C8_REUSE_AUDIT, D席 2026-11-10)

第0步强制盘点: 现有代码 vs 章程交付件,输出复用映射(直接复用/最小新增)。
基线: dev/charter8-research-map-v1 @ cd5524c(v0.7.1, registry v2.8.0, 113套件)。

## 一、逐面盘点

### 1. Streamlit 工作台 app.py(247行)+ scripts/workbench_data.py(387行)
现状四页: 全球宏观概览/金融市场变化/历史研究/AI研究(+关于与限制)。
- **直接复用**: `_load_state`/`wd.latest_snapshot`/`wd.snapshot_meta`/
  `wd.overview_rows`/`wd.market_rows`/`wd.metric_series`/`wd.fmt_value`/
  `wd.fmt_change`/侧栏 Gate A 披露框架(整体保留);
  `wd.SUPPORTED_CONCEPT_HINT`/`ask_local`/`save_to_archive` → 移入页④。
- **最小新增**: 页①市场段 1m/3m/1y/5y 区间变动列(复用 rhq.interval_change,
  见§3);页②传导地图渲染(读新配置档);页③读新 views 存储;页④ QB 链列表。
- **测试影响**: test_oss_workbench.py 只测 workbench_data 层(零 streamlit
  import),app.py 无源码锁(test_oss_product.py 仅锁字符串 'streamlit run
  app.py' 在 README/USER_GUIDE 在场)→ 页面重组零套件迁移。

### 2. 区间变动口径(interval_change 自配对)
- **直接复用**: `scripts/research_history_query.py::interval_change(dates,
  values, unit, start, end)` —— P2-2 正式口径的实现体(基准=严格早于 start
  的最后观测;利率 pp/价格 pct/计数 abs;数据不足 available=False)。
  compare 自配对 `sides[].interval_change_common_window` 即由它产出。
- **最小新增**: `view_verifier.py` 的窗口选择(1m/3m/1y 相对快照日)——纯
  参数计算,零新窗口逻辑;调用同一函数防口径分叉。

### 3. HK 数据(章程交付④)
- **HSI/HSCEI: 已在场,直接复用,不新增**。registry v2.8.0 已有
  HSI(core, china_market_collector/hkHSI, calendar=hk)/HSCEI/HSAHP/SB_FLOW;
  每日随 china 通道采集(今日档 china_20261110.json: HSI n=320,
  2025-07-25→2026-11-10,腾讯主通道+yfinance 备用)。**再按 DAX/CAC40 模式
  注册 global 通道会违反"禁同概念双注册"语义规则**——审计裁决: 不重复注册。
- **HKMA 基础利率: 登记缺口,不硬造**。HKMA 开放 API 免 key 免费属实
  (实测 `daily-figures-monetary-base` 端点 200,字段=货币基础存量,无
  base_rate 列);基础利率专属数据集路径实测不可达(candidate 路径
  400/405,网关侧拒),不猜路径不硬造。缺口登记入 P2_DATA_GAP_LEDGER
  新行;registry 不加 PENDING 条目(避免再掀 110 项锁面;恢复接线时随批登记)。

### 4. 研究档案/QB 链(页④与传导边数据源)
- **直接复用**: `data/research/research_archive/research_archive/query_history/
  QB-*.json(+.research-full.json sidecar)` 现有堆栈;
  QB-20261110-022(19组传导 compare,r 值+roll60)/QB-20261110-023(机制
  存废 E1/E3)= transmission_edges.json 唯一初始边源(协调方硬约束)。

### 5. ia_cli(1307行,9能力)
- **直接复用**: `envelope()`/`emit()`/`load_context()` 信封与退出码约定
  (0 成功/1 执行错/2 用法错)。
- **最小新增**: `cmd_views`(list/get/lint)+ 子解析器,信封一致;
  views 不依赖快照(数据源=views 目录),信封 snapshot 字段保持 null 如实。

### 6. news_collector(809行)
- **不相干,不复用**: Finnhub+RSS 新闻流,与机构观点结构化存储(章程
  schema v1.0 深字段)目标不同;B席采集走独立 VIEW-*.json 文件。仅借鉴其
  纪律模式: 原始保全/发布时间与采集时间分列/缺时间=UNKNOWN 不冒充。

### 7. SKILL.md(116行,<500 行锁)
- **最小新增**: 「研究地图」工作流节+速查表加 views 行(现有锁只含8命令名
  containment,P2-2/empty_window/sort_basis 文案保留即可,零迁移)。

## 二、映射汇总(交付件 → 落点)

| 章程交付 | 处置 | 落点 |
|---|---|---|
| ①机构观点存储+schema v1.0 | 最小新增 | scripts/view_store.py + data/institutions/views/ |
| ②观点-指标映射 | 最小新增 | config/view_metric_map.json(registry v2.8.0 现有 id) |
| ③确定性验证 | 复用+薄层 | scripts/view_verifier.py(rhq.interval_change 唯一口径) |
| ④HK 数据 | 复用+登记 | HSI 已在场;HKMA 基准利率→台账缺口行 |
| ⑤3m 窗口 | 纯文档 | USER_GUIDE+SKILL 补自配对用法(禁新窗口逻辑) |
| ⑥Streamlit 四页 | 复用+重组 | app.py(数据层全复用 workbench_data) |
| ⑦ia_cli views | 最小新增 | ia_cli.py cmd_views |
| ⑧Skill 工作流 | 最小新增 | SKILL.md 研究地图节 |
| ⑨测试 | 最小新增 | tests/test_charter8_*.py 三套(合成 fixture,零网络) |

## 三、零改动面(明确不动)

registry v2.8.0(零条目变更→零锁迁移);analog/compare/e2eb 引擎;
snapshot_builder/fact_engine;run_weekly 流水线;workbench_data 既有函数
签名(仅追加新函数);113 基线套件零弱化。
