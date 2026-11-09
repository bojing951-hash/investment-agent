# investment-agent — 开源 AI 全球宏观研究工作台

一套本地运行的全球宏观研究工具: 自动采集美国、中国、欧元区、日本四大经济体的
宏观与金融市场数据,构建每日**研究快照**(带来源与观测日期的事实库),通过质量
门禁后生成中文宏观研究周报,并提供一个本地网页**研究工作台**——看全景、看变化、
查历史、问问题。

> **这是什么、不是什么**: 这是**研究工具**,帮助你看清"当前发生了什么、历史
> 变化了什么、经济体和资产之间有什么联系"。它**不是**投资顾问: 不给出资产
> 配置建议、不评级资产、不预测价格、不执行任何交易。投资观点由你自己形成。
> (产品方向见 [PRODUCT-GOAL.md](PRODUCT-GOAL.md),公开研究样例见 [examples/](examples/))

## 用你自己的 AI Agent 做研究(Agent Skill,推荐入口)

本仓库内置一个 **Agent Skill**(`.agents/skills/global-macro-research/`,遵循
[agentskills.io](https://agentskills.io) 开放标准): 安装后,你的 AI 助手
(Claude Code / Codex / 任何能跑 shell 命令的 Agent)能用自然语言驱动本引擎的
统一工具接口 `ia_cli.py`,拿到**每个数值都带来源、观测日期、单位口径、
ETF 代理身份**的结构化 JSON,再按内置研究纪律(事实/推断分离、缺失不填 0、
禁成分编造归因)作答。

```bash
# Claude Code(项目级,克隆本仓库后在其目录里):
python3 install_skill.py --target project    # 复制到 .claude/skills/,重启会话生效
# Codex: 无需安装——在仓库目录内启动 codex 即自动发现(.agents/skills/ 为官方扫描路径)
# Claude Code / Codex 个人级(任意目录可用):
python3 install_skill.py --target personal-cc
python3 install_skill.py --target personal-codex
```

装好后对 AI 说(四个可直接复制的研究起点):

1. 「全球宏观现在什么情况?给我美中欧日概览,注明各指标观测日期」
2. 「最近一周金融市场发生了什么变化?利率和股指分开说,别把百分点说成百分比」
3. 「把美国 10 年期国债收益率和标普 500 的历史相关性算出来,观测窗对齐了吗?」
4. 「美元兑日元现在什么水平?最近走势如何?」,或继续「把刚才的研究存档」

详细安装/卸载/宿主兼容见 **[docs/SKILL_GUIDE.md](docs/SKILL_GUIDE.md)**;
也可以完全不用 AI,直接 `python3 ia_cli.py doctor` 等命令自助查询(见下)。

## 适合谁

- 想每周花 10 分钟了解全球宏观与市场全景的个人研究者;
- 需要一个**数据可靠、来源可查、不编数字**的宏观信息底座的投资者/学生/分析师;
- 想在真实数据上做跨经济体、跨资产历史比较,并借助 AI 解释传导机制的人。

## 它能帮你做什么(四种典型用途)

| 用途 | 入口 |
|---|---|
| **查看全球宏观全景** | 工作台"全球宏观概览"页: 美中欧日主要指标当前值/观测日期/变化/来源,缺失如实标注 |
| **观察金融市场近期变化** | 工作台"金融市场变化"页: 股/债/汇/商品/加密/信用/波动率的周/月/年内变化与走势图 |
| **比较历史与不同经济体** | 工作台"历史研究"页: 任选指标看 1 个月~1 年+ 序列,双指标叠加对比(本地真实序列) |
| **借助 AI 开展专题研究** | 工作台"AI 研究"页: 基于快照事实的接地作答(每个数值可溯源),可存入本地研究档案;AI 研究解释为可选增强(可选模型 API,任意 OpenAI 兼容端点) |
| **让 AI Agent 替你跑全流程** | Agent Skill + `ia_cli.py`: 自然语言→结构化 JSON→按研究纪律作答(见上节) |

外加每周一份的 **AI 宏观研究周报**(可选模型 API;不配则自动产出 data-only 确定性数据观察周报——Agent Native 默认形态,见 USER_GUIDE 第 2 节): [样例点这里](examples/weekly_report_20261108.md)。

## 快速开始

```bash
git clone https://github.com/bojing951-hash/investment-agent.git
cd investment-agent
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

cp .env.example .env        # 按需填 Key(免 Key 可采集;但缺 FRED Key 时 Gate A 必 FAIL、研究问答被拒,见指南 FAQ Q1)
python3 run_weekly.py       # 第一次数据采集(14 步流水线,配齐 Key 数分钟;免 Key 或需 10 分钟左右,见指南 Q1)

# 打开本地研究工作台(可选):
.venv/bin/pip install -r requirements-workbench.txt
.venv/bin/streamlit run app.py
```

详细安装(macOS/Windows/Linux)、配置、首次运行说明见 **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)**。

## 真实功能一览

**已实现**(以下数字以代码为准确口径,查看当前指标数量:
`python3 -c "import json;print(len(json.load(open('config/metric_registry.json'))['metrics']))"`):

- **14 步数据流水线**(`run_weekly.py`,9 步关键/5 步非关键,失败降级如实记台账):
  全球行情(yfinance)→A股港股(akshare/tushare)→美国宏观(FRED)→新闻(Finnhub,可选)→
  利率预期→日本利率/市场→欧元区市场→研究快照(Gate A)→体制评分卡→跨资产相关性→
  数据打包→校验与锚点→日档保留(90天全量+月度归档);
- **指标注册表**: 103 项指标(102 启用+1 弃用,覆盖美国/中国/欧元区/日本/全球市场,
  单一权威来源 `config/metric_registry.json`);
- **金融事实引擎 + 研究快照**: 每项事实带观测日期/来源文件/内容指纹;快照不可变;
- **Gate A(数据质量门禁)**: 核心缺失即 FAIL;非核心缺失→DEGRADED 降级并如实披露;
- **AI 周报生成**(`scripts/report_generator.py`,可选模型 API `MODEL_*` 三参,任意
  OpenAI 兼容端点;未配齐→data-only 确定性数据观察,不失败): 模型生成 →
  **Gate B 数值校验**(报告里每个数字对照当日锚点核验,不可核验→待复核)→ 三态发布;
- **本地研究工作台**(`streamlit run app.py`,四页,见上表);
- **接地研究问答**: 当前支持 4 类问题(美日政策利率差/美日10Y收益率差/美元兑日元/
  美国政策利率水平,支持 as_of 与单经济体概览),越界问题(投资建议类)明确拒绝,
  未支持问题如实说明,不猜映射;
- **研究档案**: 问题与作答 append-only 落本地档案(`data/research/`);
- **Agent Skill 与统一工具接口**(`.agents/skills/global-macro-research/` +
  `ia_cli.py`): 八能力(doctor/update/overview/changes/history/compare/research/
  archive)结构化 JSON 输出,数值节点强制携带单位族/观测日期/来源/ETF 代理身份,
  变化量强制携带基准日与窗口语义,附研究纪律 lint(成分编造断言=violation);
  安装器 `install_skill.py` 物理复制到各宿主(不依赖符号链接);
- **离线测试**: 106 个测试套件(`python3 tests/<name>.py`,无需 pytest;CI 自动跑
  105 个离线套件,真实模型调用套件 `test_model_live` 须显式开启;v2.1 新增
  零Key矩阵/用量实际值捕获/厂商残留守卫三套;A-fin 新增时间语义与研究模式门/
  十案例冻结基线验收两套)。

**历史兼容(非默认执行)**: `config/thesis.json`、`config/allocation_views.json`
为**已冻结的历史研究档案**(2026-11-08 产品章程勘误: 论点星级/超配低配/预测裁决
等自主观点机制属越位,已从正式流程下线,历史数据原样保留不再被消费);
月报/季报脚本保留,但**自动级联默认关闭**(设置 `IA_AUTO_MONTHLY=1` 恢复,人设
改革进行中,见 `docs/MW-V1-AUDIT-DEFERRED.md`)。

**开发中/已知限制**(如实声明,不夸大): 德国/法国国债与股指、中国 OMO/资金通道、
东京 CPI 采集通道待建;报告历史对照列待建;事件/新闻研究通道待建;月/季报提示词
仍为旧版人设(12-05 前改革);克隆仓库**不含历史数据积累**(仅 3 个单日示例采集档),
序列须自行采集积累;**免 FRED Key 首跑必然 Gate A FAIL**(美国宏观核心缺失),研究
问答会被如实拒答、脚本退出码 1——配 Key 后恢复,详见指南 FAQ Q1。

## 数据来源(全部免费公开源)

| 数据 | 来源 | Key |
|---|---|---|
| 美股/全球行情 | Yahoo Finance | 不需要 |
| 美国宏观序列/利率预期 | FRED | `FRED_API_KEY`(研究问答实际依赖——Gate A 核心指标来源,免 Key 必 FAIL) |
| A股/港股/中国宏观 | akshare / tushare | `TUSHARE_TOKEN`(可选) |
| 日本国债/政策利率、欧元区利率 | 日本财务省/BOJ、ECB 公开数据 | 不需要 |
| 新闻摘要 | Finnhub | `FINNHUB_API_KEY`(可选) |
| AI 周报/研究解释 | 可选模型 API(任意 OpenAI 兼容端点) | `MODEL_API_KEY`/`MODEL_BASE_URL`/`MODEL_NAME` 三参(仅 AI 功能需要;数据采集不需要) |

## 命令速查

```bash
python3 run_weekly.py                 # 数据采集+快照+校验(14步;免Key可跑,缺FRED Key时Gate A FAIL→退出码1,属预期)
python3 scripts/report_generator.py   # 生成 AI 周报(可选模型 API;未配齐→data-only 数据观察)
bash run_daily.sh                     # 采集入口脚本(自动定位项目根/虚拟环境,可移植)
streamlit run app.py                  # 本地研究工作台(网页)
python3 ia_cli.py doctor              # Agent 工具接口·环境体检(其余: overview/changes/history/compare/research/archive)
python3 install_skill.py              # 安装 Agent Skill(默认 --target project→.claude/skills/;个人级/Codex 须显式 --target personal-cc|personal-codex)
python3 scripts/monthly_review.py --month 202610 --dry-run   # 月度复盘(手动,历史兼容)
python3 tests/test_p0_fixes.py        # 运行单个测试套件(离线)
```

## 调度(可选)

- **macOS**: launchd 定时跑 `run_daily.sh` 与 `report_generator.py`(样例见
  `docs/USER_GUIDE.md`);
- **Linux**: cron; **Windows**: 任务计划程序直接调 `python run_weekly.py`
  (`run_daily.sh` 需 bash 环境);
- 调度不是必需——手动运行同样完整。

## 已验证 / 未验证(诚实边界)

**已离线验证**: 106 个测试套件(门禁逻辑/快照与事实引擎/数值校验/研究问答/
工作台数据层/配置安全/Skill 格式与安装器/ia_cli 契约与纪律 lint/单位感知
比较与档案 sidecar/compare 窗口与跨频率/任务F 完整成果归档/零Key矩阵与
用量实际值捕获与厂商残留守卫/A-fin 时间语义+研究模式门+--lag 与十案例
冻结基线验收);
真实模型 API 冒烟(`test_model_live`,显式开启)。
**未验证/边界**: Windows 实机未测(代码无 OS 专属调用,理论可用);中国节假日
日历仅 2026 年;免费数据源存在限流与修订(降级机制会如实披露);AI 解释性内容
可能出错(因此与【事实】严格区分)。

## 免责声明

本项目提供**研究与信息整理工具**,输出内容可能滞后或有误,不构成投资建议;
据此操作风险自负。请始终以官方数据源为准核实关键数值。

## License

[MIT](LICENSE)
