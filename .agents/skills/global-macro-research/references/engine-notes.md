# 引擎笔记: 数据源、Key、流水线、快照与档案

## 数据源与 Key(doctor 只报已配置与否,永不打印值)

| 环境变量 | 用途 | 缺失后果 |
|---|---|---|
| FRED_API_KEY | 美联储/FRED 宏观序列(28 个) | 强烈推荐;缺失→这些序列采集失败→Gate A FAIL→research 拒答(属预期,不是故障) |
| MODEL_API_KEY / MODEL_BASE_URL / MODEL_NAME | AI 解释(research --explain)与 AI 周报叙事层(可选;任意 OpenAI 兼容端点)。模型 Key 共三个消费点: ①周报叙事层 ②AI 研究解释 ③新闻模型摘要 | 仅影响 AI 功能;三参未配齐→周报 data-only 确定性观察、AI 解释如实提示未配置(Agent Native 默认) |
| IA_NEWS_MODEL_SUMMARY | **新闻模型摘要显式开关**(消费点③,Charter7-7 2026-11-10): `=1` 且 MODEL_* 三参齐才调用付费摘要 | 默认关闭——**MODEL_* 三参齐也不再自动调用**(付费调用须显式知情开启);未开启→新闻走确定性标题回退 |
| TUSHARE_TOKEN / FINNHUB_API_KEY | 中国市场/市场补充 | 可选 |
| YF_PROXY | yfinance 代理 | 可选 |

Key 从进程环境或引擎根 `.env` 读取(进程环境优先)。**绝不允许读取 Claude/Codex 等其他应用的 Key 作为本项目凭证。**

## 采集流水线(update 能力)

`update --yes` = `python3 run_weekly.py`(15 步,分钟级)。退出码: 0=全部关键步骤成功(非关键可降级);1=任一关键步骤失败或被跳过。同日重跑需 `--allow-revision`(修订机制,生成 _vN 快照)。台账: `logs/pipeline_run_YYYYMMDD.json`(doctor 的 last_run 数据源)。**Skill 永不自动运行 update——只有用户明确要求时。**

采集窗口(Charter6-P0): FRED 观测起点已参数化(宏观数据全史;ICE BofA 族利差 HY/BB/B/CCC/IG_OAS 为源端 3 年滚动授权窗,条目带 `history_note` 如实注记,非采集器截断);Yahoo 行情窗口参数化(默认 10 年,`GLOBAL_HISTORY_PERIOD` 可覆盖,非法值经 env_config 校验回落默认并告警,合法集=yfinance 官方 period 全集——收尾延期③;series 为窗口全量,旧 tail(400) 截断已废);jp 采集器 NIKKEI225 series 窗口与 global 读同一 env/默认(默认'10y'≈2520 观测,近似 月≈21/年≈252 交易日;ytd/max=不截断——收尾延期①,旧 251 硬截断已废)。Shiller 估值(ie_data.xls, 月频 1871+,免 Key)——live 首跑已于 2026-11-10 执行(延期②收口): 规范源=shillerdata.com 首页解析版本化直链(旧 Yale 镜像滞后约 3 年,仅回退用并如实告警);实册表头为 4 行合并式,解析器按"首列恰为 Date"定位真表头(合并中间行的 'Date'/'CAPE' 字样为陷阱,曾致误采 Excess CAPE Yield 列);下载字节 sha256+长度随档落盘作版本凭证。日档保留策略(Charter7-6 修订 2026-11-10): 近 90 天全量保留+更早每月最后一份 gzip 归档(`data/daily/archive/`,不做增量合并,全量重拉);**研究引用保护**——被任一 research_snapshot 的 sources_status 声明为来源的采集档永不删除,过期改 gzip 归档(protected_archived 清单);归档可读回: resolve_inputs/sources_status_problems/read_archived_source 支持 archive/*.gz(sha256 按解压后字节核验),老日期研究查询优雅降级读归档而非裸 LookupError。

## Charter7 P0 修订(2026-11-10,analog/研究门要点)

- **统一特征集(Charter7-2)**: analog 距离特征面=锚点准入特征集 U 唯一决定;分母 W_U 全候选一致,**不逐候选重归一**(旧实现缺数候选剩余特征相对权重变相放大,偏差更大但缺数者可反超——已修);候选缺 U 特征→missing_features{特征→原因}随行,排序=(缺席数升序,距离升序)双键。**排序依据随行披露(P2-1, 2026-11-10)**: 输出顶层 `sort_basis` 逐字写明排序=(n_missing, distance, month)——名次非纯距离序,比较相似度以 distance 字段为准;每条 top 条目带 `n_missing`(缺席特征数=排序首键)。处置注记: Case B 实战 QB-20261110-023(把 TOP-N 名次读作纯距离序,2020-12 D=1.19/miss2 排在 2019-12 D=1.01/miss7 之前疑为缺陷)经裁决=**机制无错**(缺席多者只降位不升位,保守方向,复验 PASS 口径不变),残留缺陷仅输出未披露排序依据,已加披露收口;零计算改动。
- **跨频率门槛(Charter7-4)**: 36 **个月**史按网格步长折算观测数(月网格 36 点/季网格 12 点;旧实现隐性 36 季=9 年致 GDP_yoy 永不参与——已修);锚点月无值特征全部进 features_dropped_at_anchor 带原因(release_lag/quarterly_grid/no_value_at_anchor);维度缺席判据双侧(锚点+候选侧);候选有效维度只按 U 内特征计(锚点缺席的 SPX_PE_TTM 不再为候选积维度证据)。
- **TOP-N 簇去重(Charter7-5)**: 候选月相差<12 个月=同簇(事后窗重叠),TOP-N 仅输出簇代表(cluster_members 随行,dispersion/一致性按独立簇口径);准入/距离/分位计算本身不变。
- **realtime 门(Charter7-1)**: 对查询时窗负责——仅查询起点月窗内存在**跨日 vintage**(research_snapshot 基础日期)才 available;同日 _vN 修订不算历史 vintage(仅附加披露)。compare 与 analog 同一权威(realtime_gate_text)。
- **aftermath 披露(Charter7-3)**: 逐窗实际起止观测日随行({资产}_window{h→{start,end}}),起点=候选锚点月之后首个观测(次月首日起),终点=候选月+N月内最后观测。

## 快照结构(doctor/overview 的数据来源)

`data/daily/research_snapshot_YYYYMMDD[_vN].json`:
- `facts[]`: 指标事实(value/unit/observation_date/quality_status/source/identity/derived)
- `derived.{week,mtd,ytd}`: 变化节点(pp_change+bp_change 或 pct_change,带 basis_date/window/formula/return_semantics)
- `series_store`: 各指标的内嵌历史序列(全球行情资产+中国/港股指数+宏观月频+Shiller 估值,以 metric_id 为键)
- `gate_a`: {status, core_missing, noncore_missing(+detail), noncore_degraded}
- `sources_status`: 8 个采集通道(global/macro/china/rate_economy/japan/jp/ea/shiller)的文件与校验状态

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
