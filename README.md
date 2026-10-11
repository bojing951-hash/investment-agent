# investment-agent — 个人全球宏观周报自动生成系统

一套无人值守的个人投资研究流水线：每天早上自动采集全球宏观/市场数据，每周五早上调用大模型（智谱 GLM）生成一份中文全球宏观投资周报，生成后自动校验数字、回写论点状态。

> 本仓库是**净化开源版**：已移除全部 API key（改由环境变量注入）和 6 个月的个人数据历史。样例产物见 `output/weekly/`。

## 运行流程

```
每天 07:00（launchd/cron 触发 run_daily.sh → run_weekly.py，9 步）
  1. 全球资产采集(yfinance)      5. 利率预期与实体经济(FRED)
  2. A股港股采集(akshare)        6. 宏观体制评分卡(增长×通胀→体制)
  3. 宏观与信用采集(FRED)        7. 跨资产相关性(10对资产20日滚动)
  4. 新闻采集(Reuters等RSS)      8. 数据打包(data_pack_*.md)
                                9. 校验器(抽约286个数据锚点+防幻觉指令块)

每周五 08:00（report_generator.py）
  prompt = 系统提示词(研究员角色+纪律)
         + config/framework.md(阈值体系) + config/thesis.json(9论点及触发条件)
         + 上期报告前60行 + 用户手工笔记 + 近7天新闻(脱敏)
         + 数据包 + 锚点清单
  → GLM流式生成周报 → 保存
  → 解析报告末尾THESIS_STATUS块,回写thesis.json(状态/星级/历史)
  → 用同日锚点校验报告数字(容差比对),结果落logs/validation_*.log
```

## 目录结构

| 路径 | 作用 |
|---|---|
| `scripts/` | 9 个流水线脚本（采集/评分/打包/校验/报告生成） |
| `config/framework.md` | 分析框架：各资产阈值体系 |
| `config/thesis.json` | 9 个长期论点：状态、确信度(1-5★)、升降级/失效触发条件、历史 |
| `config/technical_notes.md` | 用户手工技术面笔记（模板） |
| `output/weekly/` | 周报样例 |
| `data/daily/` | 数据样例（锚点文件 + 防幻觉指令块样例） |
| `提示词设计需求说明.md` | **给 AI 的系统说明**：大白话架构 + 现有提示词原文 + 实测弱点 + 设计任务 |

## 部署

```bash
pip install -r requirements.txt
export GLM_API_KEY=你的智谱key      # 必需
# export TUSHARE_TOKEN=... FRED_API_KEY=... FINNHUB_API_KEY=...  # 可选
python3 run_weekly.py                # 跑一遍完整采集
python3 scripts/report_generator.py  # 手动生成一份周报
```

定时调度（macOS launchd / Linux cron）：每天 07:00 跑 `run_daily.sh`，每周五 08:00 跑 `scripts/report_generator.py`。注意 launchd 环境的 `NO_PROXY=*` 会禁用代理导致 yfinance 429，采集脚本内置了代理探测（见 `global_market_collector.py` 的 `_setup_proxy`）。

## 关键机制

- **数据锚点防幻觉**：校验器从原始 JSON 抽出全部指标作锚点，prompt 强制"数值必须引自锚点清单"；报告生成后逐项容差比对（`data_validator.py`）
- **论点追踪闭环**：报告末尾输出机器可读的 THESIS_STATUS 块，脚本解析后回写 `thesis.json`，状态周周相续
- **评分卡体制切换纪律**：体制切换须连续两周评分一致才"正式确认"，防单周噪音
- **GLM 内容风控规避**：新闻按板块白名单+敏感词过滤（`sanitize_news`），长输入截断

## 已知短板

framework 要求的 EIA 库存/HY 到期高峰/TIC/ETF 持仓等数据尚无采集器；融资余额接口偶发静默失败。（新闻 AI 摘要的 DeepSeek 死接口问题已于 2026-10-11 迁移 GLM 修复）

## 2026-10-11 升级（P0–P4）

按"Global Macro Research & Allocation Agent"升级规范完成四个阶段，周报八节结构保持不变。详细差距矩阵与路线图见 `docs/UPGRADE_PLAN.md`，回归测试 `tests/`（89 项断言，纯 Python 无需 pytest）。

- **P0 缺陷修复（9 项）**：新闻 AI 摘要迁移 GLM；流水线失败传播 exit code；月度 FRED 序列标注频率与观测区间；体制切换"连续两周"改用 ISO 周去重（同周每日文件视为回声）；数据锚点带采集日/观测日双时间戳；数值校验不过关禁止回写论点状态；framework.md 体制映射同步 v2.0
- **P1 研究增强**：校验显示观测日+日频行情滞后提示；**提示词全部外移 `config/prompts/` 热加载**；评分卡体制归因（反事实分解：剔除单指标后体制翻转者=关键驱动）
- **P2 配置研究引擎**：`config/allocation_views.json` 九资产观点库（评级/确信度/触发器/失效条件/历史），`allocation_engine.py` 渲染进周报第五节并解析 ALLOCATION_STATUS 块回写
- **P3 预测追踪**：观点库 predictions[] 记录方向/期限/deadline，评级变更自动登记预测，到期由 PREDICTION_STATUS 块裁决 hit/miss/expired，命中统计进季报
- **P4 月报季报**：月末/季末最后一个周五在周报后自动触发 `monthly_review.py` / `quarterly_outlook.py`（子进程，失败不影响周报），回溯整月/整季原始 JSON 时序而非拼接周报，产出 `output/monthly/`、`output/quarterly/`

```bash
# 新增可单独运行
python3 scripts/allocation_engine.py              # 渲染观点库(冒烟)
python3 scripts/monthly_review.py --dry-run       # 装配月度数据块(不调GLM)
python3 scripts/monthly_review.py                 # 生成月度复盘
python3 tests/test_p0_fixes.py                    # 回归测试(另有 p1/p2/p4)
```
