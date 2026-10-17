# investment-agent — AI 全球宏观策略研究员

一套无人值守的个人投研系统：每日自动采集全球宏观与市场数据并记录预测观察，每周五调用大模型（智谱 GLM）生成中文全球宏观周报，生成后自动校验数字、按门禁回写论点与观点状态、裁决到期预测；月末/季末后的第一个周五追加月度复盘与季度展望。

> 本仓库是**净化开源版**：已移除全部 API key（改由环境变量注入）与个人数据历史。样例产物见 `output/weekly/`。
>
> **定位声明**：本系统是"AI 全球宏观策略研究员"——做数据采集、解读、跨资产分析、理论观点与自我纠错（长期研究记忆），**不是交易系统**：无账户、无实盘、不下单、不执行任何投资决策。核心架构已冻结（v1.0.0-rc），后续变更只由真实运行问题/研究质量/复盘结论驱动。

## 运行流程

```
每天 07:00（launchd → run_daily.sh → run_weekly.py，10 步）
  1/10 全球市场数据采集(yfinance)      6/10 宏观体制评分卡(增长×通胀→体制)
  2/10 A股港股数据采集(akshare)        7/10 跨资产相关性(10对资产20日滚动)*
  3/10 宏观与信用采集(FRED)            8/10 数据汇总打包(data_pack_*.md)
  4/10 新闻采集与分析(RSS→GLM摘要)*    9/10 数据校验与锚点生成(~290锚点)
  5/10 利率预期与实体经济(FRED)       10/10 预测观察记录(幂等,不调GLM)
  (* 非关键步骤: 失败降级不阻断,不影响观察记录)
  关键步骤失败 → exit 1；第10步无当日锚点 → exit 2（不得以旧数据充当本期观察）

每周五 08:00（report_generator.py,独立launchd任务）
  prompt = 系统提示词(全球宏观首席研究员兼跨资产策略师)
         + framework.md(阈值体系) + thesis.json(9论点) + allocation_views.json(9观点)
         + 上期报告 + 手工笔记 + 近7天新闻 + 数据包 + 锚点清单
  → GLM流式生成周报(固定八节结构) → 同日锚点校验(数值容差+单位口径)
  → PASS/DEGRADED/FAIL 三态: FAIL禁止一切长期状态回写
  → 解析 ALLOCATION_STATUS/THESIS_STATUS/PREDICTION_STATUS 块
  → 观点评级变更门禁 + 论点终态门禁 + 预测裁决(引擎权威>受核验GLM)

月度/季度（由周报在期间结束后第一个周五触发,不新增launchd任务）
  自然月结束后第一个周五 → monthly_review.py(读整月原始JSON,非拼接周报)
  自然季结束后第一个周五 → quarterly_outlook.py(整季聚合,非3时点)
```

## 研究记忆（三个状态文件，全部带门禁回写）

| 文件 | 内容 | 回写门禁 |
|---|---|---|
| `config/thesis.json` | 9 个长期论点：状态、确信度、quant_triggers 触发器、evidence_ledger 证据台账、history | 终态（已失效/已验证）重开须 invalidation 触发器或 ≥2 项新增独立证据；确信度上调 ≤ 程序星级 |
| `config/allocation_views.json` | 9 个资产观点（超配/标配/低配/观望）+ predictions[] 预测池 | 评级变更须同向触发器已触发或 ≥2 项新增独立支持证据（转/自观望放宽 1 项）且触及资产关键传导指标 |
| `output/weekly/` | 周报与月/季报 | 生成后立即同锚点校验，结果附于报告尾 |

**证据分级 v2（程序校验）**：模型声称的每项证据须 `{metric, value, obs_date}` 三项齐全且与锚点吻合（数值容差+bp归一+观测日一致+逐指标新鲜度），缺一整项拒收；星级按独立证据数×机制类别×观察期计算，未解释重大反证封顶 3★。旧值重引不算新增（对照台账 (指标,观测日) 集合），同日重跑不虚增。

## 预测生命周期与每日观察

```
创建(评级变更行附pred) → [前提判定] → 观察期(observe_from起,每日记录)
  → 裁决(hit/miss/inconclusive/未触发终态) → final封存(不可重开/翻案)
```

- **每日观察**（`daily_prediction_observer.py`，第 10 步）：观察中预测校验目标指标、未触发预测校验前提指标；未通过校验的指标从写入锚点集中剔除——**数据验证与状态写入严格隔离**，无效数据（缺指标/观测日缺失/未来/过期）不得进入长期观察历史；引擎侧另有同口径防御（其他调用路径无法绕过）。幂等：同批锚点重复运行不增记录。
- **前提守卫**：前提只能在预测有效期内触发（触发观测日 ≤ 截止日），截止日不顺延；到期未触发由周报引擎落"未触发"终态并加 `final` 标记，此后每日任务不得重开。
- **裁决口径**：
  - `touch`（观察期内触及）：窗内任一观测按其口径（收盘/盘中最高/最低）满足即 hit（可提前）；判 miss 须窗口覆盖充分且对应口径数据完整——只有收盘价不能证明盘中未触及，数据缺失 ≠ 失败。
  - `expiry`（截止日水平）：按市场日历预先确定有效截止交易日（非交易日回溯，如周六截止→周五；crypto 7×24 按自然日），**只认该日当日的观测**；该日数据缺失 → inconclusive，不得回退用前一交易日价格裁决。
- **裁决权威序**：引擎按观察记录的客观裁决 > GLM 附证据裁决。GLM 引用的数值与观测日必须与窗内**同一条**记录吻合且与引擎同一结算口径；引擎判 inconclusive 时 GLM 不得拿前一日满足值裁成 hit；终态预测不可被 GLM 翻案。
- 定性预测（无可计算规格）只能 inconclusive 研究回顾，单列不计入客观命中率。

## 数据质量门禁

- **观察器三态**：PASS（全部有效）/ PARTIAL（个别资产缺失只跳过受影响预测）/ FAIL（无当日锚点文件，exit 2）。
- **周报校验三态**：PASS / DEGRADED（⚠️提示级）/ FAIL（无锚点、锚点非当日、数值错——禁止回写 thesis 与 views）。
- **指标级新鲜度注册表**：行情 5 天/宏观 7 天/周频 16 天/月频 45 天；缺/非法/未来 obs_date 一律不默认新鲜，过期数据不作当前证据。
- **市场日历注册表**：us 按 NYSE 规则程序计算节假日，cn 2026 长假块，hk 最小集，crypto 全天候；不确定组合保守视为交易日（宁 inconclusive 不假 miss）。

## 测试

纯离线套件（`~/AI内容/venv/bin/python3 tests/<name>.py`，无需 pytest）：

| 套件 | 断言数 | 覆盖 |
|---|---|---|
| test_p0/p1/p2_fixes, test_p4_fixes | 22+36+82+42 | 第一轮闭环修复（体制切换/回写门禁/锚点元数据/量表v2/月季报触发） |
| test_round3_p0 / test_round3_adversarial | 91+24 | 评级门禁/触发器v3/证据分级v2/预测生命周期 + 9 个对抗用例 |
| test_round4 | 94 | ISO观察周/证据方向切分/价格口径/每日观察/quant_triggers |
| test_round5 | 64 | GLM引用核验/市场日历/obs_date必填/终态退出门禁/幂等/观察器三态 |
| test_round6 | 48 | 写入隔离/前提截止守卫/final封存/严格结算口径/JSON兼容升级 |
| test_e2e_four_weeks | 59 | 连续四周单状态端到端 |
| **合计** | **562** | 全部通过（2026-10-12，第六轮后） |
| test_glm_live | 8 | 真实 GLM 冒烟（`RUN_GLM_LIVE=1` 显式开启，临时副本，8/8） |

测试纪律：断言落盘后的 JSON 状态或函数真实行为（非源码字符串匹配）；临时目录沙盒不污染真实状态文件。

## 部署

```bash
pip install -r requirements.txt
export GLM_API_KEY=你的智谱key      # 必需
# export TUSHARE_TOKEN=... FRED_API_KEY=... FINNHUB_API_KEY=...  # 可选
python3 run_weekly.py                # 跑一遍完整10步采集
python3 scripts/report_generator.py  # 手动生成一份周报
```

定时调度（macOS launchd）：`com.investment.daily` 每天 07:00 跑 `run_daily.sh`；`com.investment.weekly` 每周五 08:00 直接跑 `scripts/report_generator.py`（plist 在 `~/Library/LaunchAgents/`）。

## 排障

- **yfinance 429**：launchd 的 `NO_PROXY=*` 禁代理所致，采集脚本内置 127.0.0.1:7890 代理探测（`global_market_collector.py` 的 `_setup_proxy`）。港股指数（恒指/国企）已改腾讯 ifzq 日K直连为主通道、yfinance 降级备用（2026-10-17 修复连续 4 日 429 断供）。
- **东财 push2 不可达**：当前网络直连/经代理均被断连（SSLError/ProxyError）；AH 溢价（HSAHP）已改新浪 rt 直连为主通道，akshare 新浪日K/东财（均禁代理）为备用。境内源一律 `trust_env=False` 直连，不经 macOS 系统代理（`china_market_collector.py` 的 `_direct_session`/`_no_proxy`）。
- **周报没生成**：看 `logs/weekly_report.log`；不要在 run_daily.sh 里 nohup 后台启动报告生成（launchd 会收割进程组，10-02 周报因此丢失）。
- **观察器 exit 2**：当日锚点缺失（上游采集失败），属预期行为——不得以旧数据充当本期观察；修复采集后重跑即可（幂等）。
- **GLM 偶发省略 obs_date**：程序门禁会拒收该证据/裁决（预期行为），重跑周报回写即可。

## 已离线验证 / 需真实环境验证

**已离线验证**（562 断言）：全部门禁逻辑、观察隔离、结算口径、幂等、终态封存、JSON 兼容升级、四周连续状态端到端。**真实 GLM 已冒烟**（8/8）：状态块格式、证据门禁、裁决核验。

**未验证/已知边界**：launchd 真实定时任务的长期行为（代码路径已验证，实际调度未连续观察）；中国节假日日历仅 2026 年（2027+ 回退为仅周末，保守方向不产生假 miss）；触发器阈值为人工配置；复合预测裁决仍偏保守（inconclusive）；FRED release_date 不可得时如实为 null；框架要求的 EIA 库存/HY 到期高峰/TIC/ETF 持仓尚无采集器，融资余额接口偶发静默失败。
