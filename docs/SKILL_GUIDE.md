# Agent Skill 使用指南(global-macro-research)

本文回答"怎么把本仓库装进你的 AI 助手"。引擎本身的安装/Key 配置见
[USER_GUIDE.md](USER_GUIDE.md);本文只覆盖 Skill 层。

## 一分钟理解

- **Skill** = 一份指导你的 AI 助手"何时用、怎么调、守什么纪律"的说明文件
  (`.agents/skills/global-macro-research/SKILL.md`,遵循 agentskills.io 开放标准);
- **ia_cli.py** = 统一工具接口(引擎薄适配层): `doctor / update / overview /
  changes / history / compare / research / archive` 八个能力,输出结构化 JSON;
- Skill 不替换引擎,只是教 AI 用它。所有数值仍来自本地快照与采集档。

## 前置条件

1. 克隆本仓库并完成引擎安装(venv + `pip install -r requirements.txt`,
   见 [USER_GUIDE.md](USER_GUIDE.md));
2. 至少跑过一次 `python3 run_weekly.py`(免 Key 可跑;缺 FRED Key 时
   Gate A FAIL、research 拒答属预期,配 Key 后恢复——FAQ Q1);
3. 你的宿主 AI 能执行 shell 命令(Claude Code / Codex / 其他 Agent CLI 均可)。

## Claude Code 安装

**项目级(推荐,随仓库走)**:

```bash
cd investment-agent
python3 install_skill.py --target project   # 复制到 <仓库>/.claude/skills/
```

重启 Claude Code 会话(或在会话内 `/skills` 确认 global-macro-research 已加载)。
项目级副本经 `${CLAUDE_PROJECT_DIR}` 定位引擎,仓库整体移动不失效。

**个人级(在任何目录的会话里可用)**:

```bash
python3 install_skill.py --target personal-cc   # 复制到 ~/.claude/skills/
```

个人级副本由安装器写入 `engine-path.json` 记录引擎根路径;若移动了仓库目录,
重跑一次安装器刷新即可。

## Codex 安装

**仓库内零安装**: Codex 官方扫描仓库 `.agents/skills/`——在仓库目录启动
`codex` 即自动发现本技能(技能里已写明用当前目录的 `ia_cli.py`)。

**用户级(任意目录可用)**:

```bash
python3 install_skill.py --target personal-codex   # 复制到 ~/.agents/skills/
```

## 其他宿主(任何能跑 shell 的 AI Agent)

不需要宿主支持"Skill"机制也能用:

- 让你的 Agent 读 `.agents/skills/global-macro-research/SKILL.md` 作为工作说明;或
- 直接手动调用 `python3 ia_cli.py <能力>` 自助查询(输出即结构化 JSON)。

## 验证安装

```bash
python3 ia_cli.py doctor        # 引擎侧: 环境/密钥/数据新鲜度/上次运行
```

然后在 AI 会话里说「全球宏观现在什么情况?」——若 AI 调用了 ia_cli 并在回答里
带出观测日期与来源,即安装成功。Claude Code 可用 `/skills` 直接确认加载状态。

## 四个研究场景(可直接对 AI 说)

1. **全球宏观全景**: 「给我美中欧日宏观概览,缺失的指标如实说,注明各指标观测日期」
   → AI 调 `overview --economy US,CN,EA,JP`
2. **近期市场变化**: 「最近一周市场发生了什么?利率变化用百分点说,股市用百分比,别混」
   → AI 调 `changes`
3. **历史与跨资产比较**: 「美国10年期国债收益率与标普500的历史相关性?共同观测窗多长?」
   → AI 调 `history` + `compare --metrics UST_10Y,SPX`
4. **接地问答与归档**: 「美日10年期国债收益率差是多少?」→ `research`;
   「把这个问题存档」→ `archive save`;事后「查我上周问过什么」→ `archive list`

## 更新与卸载

```bash
python3 install_skill.py                    # 重跑=刷新所有已装副本(与源字节一致)
python3 install_skill.py --uninstall        # 移除已安装副本(仓库源不受影响)
```

## FAQ

**Q: AI 说找不到 ia_cli.py?**
按 SKILL.md 的三级解析: 当前目录是仓库根?→ `${CLAUDE_PROJECT_DIR}`?→
技能目录内 `engine-path.json` 的 `engine_root`。都不行就重跑 `install_skill.py`。

**Q: research 一律拒答?**
先看 `doctor`: 无 FRED Key → Gate A FAIL → 接地问答如实拒答(预期行为),
配 Key 并 `update --yes` 后恢复;也支持的问题类型目前只有 4 类+单经济体概览,
见 `doctor` 输出的 supported_hint,不猜映射是设计而非缺陷。

**Q: update 会花钱吗?**
数据源全免费;`update --yes` 只是耗时的采集流水线。会花钱的只有
`research --glm`(GLM 解释,需 GLM_API_KEY)——Skill 默认不调用,仅你明确要求时。

**Q: Skill 会把我的 Key 发到哪?**
不会。ia_cli/Skill 全程本地;`doctor` 只报"已配置/未配置",不打印值;
本项目不读取其他应用(如 Claude/Codex)的凭证。

## 已验证宿主(诚实边界)

- **Claude Code**: 已在独立环境实测(headless 与交互)——见仓库审计记录;
- **Codex**: 官方文档确认支持同一开放标准与 `.agents/skills/` 路径,本文写法
  按官方文档核对;**本项目未在 Codex 实机验证**,问题请提 issue;
- 其他宿主: 未验证,不声明支持(接口本身是普通 CLI,理论上可用)。
