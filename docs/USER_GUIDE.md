# investment-agent 用户指南

面向第一次接触本项目的用户。读完你能: 装好、配好、跑通第一次数据采集、打开
研究工作台、生成第一份 AI 周报,并知道出问题时去哪看。

命令均已在 macOS 实测;Linux 同口径;Windows 路径写法不同(见各节标注,
本项目未在 Windows 实机验证)。

## 目录

1. [安装](#1-安装)
2. [配置 API Key](#2-配置-api-key)
3. [第一次运行](#3-第一次运行)
4. [日常使用](#4-日常使用)
5. [常见问题](#5-常见问题)

---

## 1. 安装

**环境要求**: Python 3.9+(推荐 3.10~3.12;CI 在 3.11 验证)+ 约 500MB 磁盘 +
可访问国际网络的浏览器环境(部分数据源在国内网络需代理)。

### macOS / Linux

```bash
git clone https://github.com/bojing951-hash/investment-agent.git
cd investment-agent

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# (可选,推荐)本地研究工作台网页:
.venv/bin/pip install -r requirements-workbench.txt
```

### Windows(PowerShell,未实机验证)

```powershell
git clone https://github.com/bojing951-hash/investment-agent.git
cd investment-agent
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
# 工作台(可选): .venv\Scripts\pip install -r requirements-workbench.txt
```

> 每次使用前激活虚拟环境: macOS/Linux `source .venv/bin/activate`;
> Windows `.venv\Scripts\activate`。下文命令用 `python3`,激活后直接可用。

## 2. 配置 API Key

**没有任何 Key 也能跑**: 全球行情、日本/欧元区公开数据可无 Key 采集,工作台
四页都能打开浏览。但注意免 Key 的确定性后果(详见 FAQ Q1): **缺 FRED Key ⇒
Gate A 必 FAIL ⇒ 接地研究问答全部拒答**、脚本退出码 1——配 Key 后恢复。

| 环境变量 | 影响 | 申请(免费) |
|---|---|---|
| `GLM_API_KEY` | **AI 周报生成、AI 研究解释**需要;不配→采集/工作台浏览照常,AI 功能不可用 | [智谱开放平台](https://open.bigmodel.cn/) |
| `FRED_API_KEY` | **美国宏观序列**(CPI/就业/利率等)需要;不配→美国宏观核心缺失,**Gate A 必 FAIL,接地研究问答拒答**(见 Q1) | [FRED](https://fred.stlouisfed.org/docs/api/api_key.html) |
| `TUSHARE_TOKEN` | A股/港股深度数据;不配→匿名限流 1 次/小时,深度数据近乎不可用,首跑或耗时 10 分钟左右 | [tushare](https://tushare.pro/) |
| `FINNHUB_API_KEY` | 新闻摘要;不配→新闻步骤降级,不影响其他数据 | [Finnhub](https://finnhub.io/) |

### 推荐方式: 项目根 .env 文件

```bash
cp .env.example .env
# 编辑 .env,填入你自己的 Key(一行一个: KEY=值)
```

`.env` 已被 `.gitignore` 忽略,**永远不会被提交**。进程环境变量优先于 `.env`。

### 密钥安全三原则

1. 只放 `.env` 或环境变量,不写进代码/笔记/聊天记录;
2. 本项目的凭证读取**只**看 `GLM_API_KEY` 等自有变量与项目根 `.env`,
   不会读取你机器上其他应用的配置文件;
3. 密钥值不会出现在任何日志与输出中(程序只输出"是否已配置")。

### 确认配置生效

```bash
python3 -c "import env_config as e; print('GLM:', bool(e.GLM_API_KEY), '| FRED:', bool(e.FRED_API_KEY), '| TUSHARE:', bool(e.TUSHARE_TOKEN), '| FINNHUB:', bool(e.FINNHUB_API_KEY))"
```

输出 `True/False`(只显示有无,不显示值)。

## 3. 第一次运行

### 3.1 数据采集(配齐 Key 约 2~10 分钟;免 TUSHARE Token 可达 10 分钟以上,见 Q1)

```bash
python3 run_weekly.py
```

它会跑 **13 步流水线**(9 步关键/4 步非关键): 采集全球行情→A股港股→美国宏观→
新闻→利率预期→日本→欧元区→构建研究快照→评分卡→相关性→打包→校验。
结束时打印各步骤 PASS/DEGRADED/SKIPPED 台账与总结行。

**预期结果**:
- `data/daily/` 出现当日采集档(`global_YYYYMMDD.json` 等)与
  `research_snapshot_YYYYMMDD.json`(研究快照,工作台的数据源);
- 部分步骤 SKIPPED/降级是**正常的**(见 3.3 与 FAQ)。

### 3.2 打开研究工作台

```bash
streamlit run app.py
```

浏览器自动打开(默认 http://localhost:8501)。左侧栏显示当前快照日期与
Gate A 状态;四个页面: **全球宏观概览 / 金融市场变化 / 历史研究 / AI 研究**。
关闭: 终端 Ctrl+C。

### 3.3 检查数据是否成功更新 / 哪些来源失败

```bash
ls -lt data/daily/ | head          # 最新采集档(按时间)
python3 -c "import json,glob; f=sorted(glob.glob('data/daily/research_snapshot_*.json'))[-1]; s=json.load(open(f)); print('快照:',s['target_date'],'Gate A:',s['gate_a']['status']); print('缺失:',s['gate_a'].get('noncore_missing'))"
cat logs/pipeline_run_*.json       # 当日流水线台账(每步状态与原因)
```

失败/缺失的数据在快照 `gate_a` 与工作台侧栏**如实列出**,不会静默消失。

### 3.4 (可选)生成第一份 AI 周报

需要 `GLM_API_KEY`(见第 2 节):

```bash
python3 scripts/report_generator.py
```

报告落 `output/weekly/weekly_report_YYYYMMDD.md`,先入候选、经 **Gate B 数值
校验**通过后才发布为正式报告;校验不过的候选会被隔离为 `_UNVALIDATED` 草稿,
**不会覆盖已有合格报告**。公开样例: [examples/](../examples/)。

## 4. 日常使用

| 频率 | 做什么 | 命令 |
|---|---|---|
| 每天(或任意节奏) | 更新数据 | `bash run_daily.sh`(自动定位项目根与虚拟环境)或 `python3 run_weekly.py` |
| 每周 | 生成 AI 周报 | `python3 scripts/report_generator.py` |
| 随时 | 打开工作台 | `streamlit run app.py` |
| 随时 | 查历史/做对比 | 工作台"历史研究"页(窗口 1 个月~全部,支持双指标叠加) |
| 随时 | 问研究问题 | 工作台"AI 研究"页——先**本地接地作答**(数值全部来自快照,可溯源),可选 GLM 解释;问题可存入研究档案 |

**经济体比较**: 工作台"全球宏观概览"页切换 美国/中国/欧元区/日本/全球;
**跨资产比较**: "金融市场变化"页看同口径周/月/年内变化,历史页双指标叠加。

**定时调度(可选,非必需)**:
- macOS launchd: 两个定时任务(每天采集+周六出报告),`run_daily.sh` 会自动
  定位项目根;plist 模板见下方;
- Linux: `crontab -e` 加 `0 7 * * * cd /你的路径/investment-agent && bash run_daily.sh`;
- Windows: 任务计划程序直接调 `python run_weekly.py`。

macOS plist 模板(占位路径请替换为你自己的,放 `~/Library/LaunchAgents/` 后
`launchctl load`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.investmentagent.daily</string>
  <key>ProgramArguments</key><array>
    <string>/bin/bash</string><string>/你的路径/investment-agent/run_daily.sh</string>
  </array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>0</integer></dict>
</dict></plist>
```

## 5. 常见问题

**Q1 没有任何 API Key 怎么办?**
能正常完成: 安装、数据采集(部分源)、快照生成、工作台的宏观概览与市场变化页。
但要先知道一个**确定性后果**: 没有 `FRED_API_KEY` 时,美国宏观核心序列
(CPI/国债收益率/就业等)必然缺失 → **Gate A 必然 FAIL → 接地研究问答全部拒答**、
流水线第 10-13 步跳过、`run_weekly.py` 退出码 1。这是防假数据门禁的如实行为,
**不是你的环境坏了**;配置 FRED Key(免费申请,见第 2 节)后即恢复。
其余影响: 缺 GLM → 无 AI 周报与 AI 解释;缺 TUSHARE → A 股深度数据近乎不可用
(匿名限流 1 次/小时,免 Token 首跑可能耗时 10 分钟左右);缺 FINNHUB → 无新闻摘要
(该步骤在无 GLM Key 时还会向终端打印一段异常堆栈,但不影响后续步骤)。
所有缺失一律如实标注,不会编造。

**Q2 某数据源不可访问/采集失败?**
非关键步骤失败会自动降级并在台账记原因(`logs/pipeline_run_*.json`),
不阻断整体;关键步骤失败→脚本报错退出,修复网络后**重跑即可(幂等)**。
境内网络访问 Yahoo/FRED 通常需代理;采集脚本默认探测本机
`http://127.0.0.1:7890`,可用环境变量 `YF_PROXY` 覆盖。

**Q3 克隆下来没有历史数据?**
正常——仓库不含数据积累(`data/` 原则上不入库,这是隐私与体积纪律;当前
基线仅带 3 个单日示例采集档: 欧元区/日本 2026-11-05)。历史序列由你
自己的每日采集积累;单日全球行情档自带约 1 年序列,宏观序列自带约 2 年,
因此**跑完第一次采集**,历史页已有可观序列。

**Q4 Gate A FAIL 是什么意思?**
Gate A 是数据质量门禁: **核心指标缺失/失败**→FAIL,当日快照不合格,下游
(评分卡/周报)拒绝消费——这是防假数据的保护,不是 bug。处理: 看快照
`gate_a` 字段与流水线台账,修复对应采集(多为网络/Key),重跑。非核心缺失
只是 DEGRADED(降级继续,报告如实披露)。

**Q5 为什么某些经济体数据不全?**
各经济体通道成熟度不同: 美国/全球市场最全;日本/欧元区基础利率与市场已有,
但德国/法国国债与股指、东京 CPI、中国 OMO/资金通道仍在建设(如实披露于快照)。
数据缺失一律显示"缺失",不填充。

**Q6 报告没生成/生成失败?**
按序检查: ①`GLM_API_KEY` 是否配置(第 2 节验证命令);②当日是否已跑采集并
生成快照(周报预检拒绝无当日快照,退出码 2);③看终端报错——GLM 网络错误
可重试;④`output/weekly/` 里是否有 `_UNVALIDATED` 草稿(Gate B 未过的候选,
不会发布)。真实样例见 [examples/](../examples/)。

**Q7 如何更新软件?**
`git pull` 后 `pip install -r requirements.txt`(依赖有变时)。你的
`data/`、`output/`、`.env`、研究档案都在 git 之外,更新代码不会动它们。
版本间数据格式变化会做兼容(历史上有过 JSON 兼容升级测试)。

**Q8 如何避免误覆盖已有研究数据?**
- 周报有候选-发布机制: 校验不过只是隔离草稿,不碰正式报告;
- 研究档案 `data/research/` 是 append-only(只增不改,重复写入会被拒);
- **不要手动删除** `data/`、`output/`、`config/` 下任何 JSON;备份建议:
  定期整目录拷贝 `data/` 与 `output/`;
- `.env` 永远不会被提交,不用担心随代码推出去。

**Q9 这是投资建议吗?**
不是。全部输出为研究材料: 数值可溯源、【事实】与【推断】区分、缺失如实
披露;系统不配置资产、不评级、不预测价格。投资决定请你自己做。

**Q10 免 Key 时定时任务(run_daily.sh)每天都"失败"?**
免 Key 常态下 Gate A 每日 FAIL → `run_daily.sh` 退出码每日为 1,launchd/cron
会把它记为失败——**这是预期行为**(原因见 Q1),采集与快照本身已成功保存。
要消除: 配置 `FRED_API_KEY`;或暂时容忍该退出码。

**Q11 同日重跑后,提示"原始采集文件在快照构建后被变更"?**
当日研究快照不可变: 首次构建后,同日重跑只更新原始采集档、**不重建快照**。
下游(周报预检等)检测到源文件指纹变化,会提示走修订版机制(`--allow-revision`,
生成 `_v2` 快照,旧版保留)。日常无需理会;确需更正当日结论时再用修订机制。
