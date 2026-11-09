# 引擎笔记: 数据源、Key、流水线、快照与档案

## 数据源与 Key(doctor 只报已配置与否,永不打印值)

| 环境变量 | 用途 | 缺失后果 |
|---|---|---|
| FRED_API_KEY | 美联储/FRED 宏观序列(28 个) | 强烈推荐;缺失→这些序列采集失败→Gate A FAIL→research 拒答(属预期,不是故障) |
| MODEL_API_KEY / MODEL_BASE_URL / MODEL_NAME | AI 解释(research --explain)与 AI 周报叙事层(可选;任意 OpenAI 兼容端点) | 仅影响 AI 功能;三参未配齐→周报 data-only 确定性观察、AI 解释如实提示未配置(Agent Native 默认) |
| TUSHARE_TOKEN / FINNHUB_API_KEY | 中国市场/市场补充 | 可选 |
| YF_PROXY | yfinance 代理 | 可选 |

Key 从进程环境或引擎根 `.env` 读取(进程环境优先)。**绝不允许读取 Claude/Codex 等其他应用的 Key 作为本项目凭证。**

## 采集流水线(update 能力)

`update --yes` = `python3 run_weekly.py`(13 步,分钟级)。退出码: 0=全部关键步骤成功(非关键可降级);1=任一关键步骤失败或被跳过。同日重跑需 `--allow-revision`(修订机制,生成 _vN 快照)。台账: `logs/pipeline_run_YYYYMMDD.json`(doctor 的 last_run 数据源)。**Skill 永不自动运行 update——只有用户明确要求时。**

## 快照结构(doctor/overview 的数据来源)

`data/daily/research_snapshot_YYYYMMDD[_vN].json`:
- `facts[]`: 指标事实(value/unit/observation_date/quality_status/source/identity/derived)
- `derived.{week,mtd,ytd}`: 变化节点(pp_change+bp_change 或 pct_change,带 basis_date/window/formula/return_semantics)
- `series_store`: 38 个指标的内嵌历史序列
- `gate_a`: {status, core_missing, noncore_missing(+detail), noncore_degraded}
- `sources_status`: 7 个采集通道(global/macro/china/rate_economy/japan/jp/ea)的文件与校验状态

经济体代码: US/CN/EA/JP/HK/GLOBAL(权威=注册表 economy 字段)。指标身份/单位/资产类唯一权威= `config/metric_registry.json`。

## 序列覆盖面(如实告知)

- 可查历史序列: 快照 series_store ∪ macro_/global_/rate_economy_ 接入点(history 不带 --metric 会列出全部)
- **单点无序列**: japan_rate_collector 来源(JGB2Y/5Y/10Y 等)——history 如实报 no_series
- **仅快照内有序列**: 中国市场(china_)与利率预期(rate_economy_)类指标的部分键

## 研究档案(archive 能力)

- 位置: `<引擎根>/data/research/research_archive/research_archive/query_history/QB-YYYYMMDD-NNN.json`(注意 research_archive 双层嵌套是 research_archive 模块的既定行为)
- append-only: 同日单调序号;重复 query_id/乱序会被拒绝;**永不无痕覆盖**
- 记录内容: question_text/created_at/snapshot_id/digest_snapshot/ir(映射+执行)/answer_summary
- 用法: `archive save --question "..."` 落档 → `archive list` 检索 → `archive get --query-id QB-...` 取回续研

## 支持的研究问题类型(research 能力,零网络接地)

1. 美日政策利率差(触发词: 政策利率差)
2. 美日 10 年期国债收益率差(附美端 2s10s)
3. 美元兑日元水平与近期走势(USDJPY/日元汇率)
4. 美国政策利率水平(联邦基金/美联储利率)
附加: "截至 YYYY-MM-DD" 日期限定;单经济体概览问题自动附该经济体指标节点(economy_fallback)。
其余类型如实返回 unmapped/no_registry_identity——**不猜映射**。

## Streamlit 工作台(可选辅助入口)

`streamlit run app.py` 提供本地 Web 界面(概览/市场/历史/AI研究四页),与 ia_cli 同一数据层。Skill 优先用 ia_cli(结构化、可追溯)。
