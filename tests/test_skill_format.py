#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skill 格式合法性回归套件(Skill 化, 2026-11-08)。

校验对象: 仓库技能源 .agents/skills/global-macro-research/
规则来源: agentskills.io 开放标准 + Claude Code/Codex 双端约束(Agent A 调查)
+ 本仓库 db4c790 公开前清洗红线(源零个人路径)。
全部离线,不依赖网络与本地真实数据。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(ROOT, '.agents', 'skills', 'global-macro-research')
SKILL_MD = os.path.join(SKILL_DIR, 'SKILL.md')
REFS_DIR = os.path.join(SKILL_DIR, 'references')

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


print("═" * 60)
print("[1] 技能源在场与目录结构")
print("═" * 60)
check("技能源目录在场(.agents/skills/global-macro-research)", os.path.isdir(SKILL_DIR))
check("SKILL.md 在场", os.path.isfile(SKILL_MD))
check("references/ 三件套在场",
      all(os.path.isfile(os.path.join(REFS_DIR, f))
          for f in ('cli-contract.md', 'research-discipline.md', 'engine-notes.md')))
check("源目录无安装产物 engine-path.json(个人路径零入库)",
      not os.path.isfile(os.path.join(SKILL_DIR, 'engine-path.json')))

text = open(SKILL_MD, encoding='utf-8').read() if os.path.isfile(SKILL_MD) else ''
lines = text.splitlines()

print("═" * 60)
print("[2] frontmatter 合法性(agentskills.io 标准 6 字段)")
print("═" * 60)
check("以 --- 围栏开头", text.startswith('---\n'))
fm_lines = []
if text.startswith('---\n'):
    for ln in lines[1:]:
        if ln.strip() == '---':
            break
        fm_lines.append(ln)
fm = {}
for ln in fm_lines:  # 极简 key: value 解析(无嵌套需求,不引 pyyaml)
    m = re.match(r'^([A-Za-z-]+):\s*(.*)$', ln)
    if m:
        fm[m.group(1)] = m.group(2).strip()
check("frontmatter 可解析且闭合(第二个 ---)",
      len(fm) >= 2 and any(l.strip() == '---' for l in lines[1:len(fm_lines) + 2]))
check("必填字段 name/description 在场", 'name' in fm and 'description' in fm)
check(f"name 合法(小写-连字符,≤64,与目录一致): {fm.get('name')}",
      bool(re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', fm.get('name', '')))
      and len(fm.get('name', '')) <= 64 and fm.get('name') == 'global-macro-research')
desc = fm.get('description', '')
check(f"description 长度合法(1~1024,当前 {len(desc)})",
      1 <= len(desc) <= 1024)
check("description 含触发语境(何时使用)", '当用户' in desc or '询问' in desc)
STANDARD_FIELDS = {'name', 'description', 'license', 'compatibility',
                   'metadata', 'allowed-tools'}
extra = set(fm) - STANDARD_FIELDS
check(f"仅用标准字段(超集={sorted(extra)};CC 专属字段不进跨端源)", not extra)
check("compatibility 声明 Python 与调用方式", 'Python' in fm.get('compatibility', ''))

print("═" * 60)
print("[3] 正文结构与渐进披露")
print("═" * 60)
check(f"主文件 <500 行(当前 {len(lines)})", len(lines) < 500)
check("正文含引擎路径三级解析(工作目录/CLAUDE_PROJECT_DIR/engine-path.json)",
      'CLAUDE_PROJECT_DIR' in text and 'engine-path.json' in text)
check("正文含八能力速查表", all(c in text for c in
      ('doctor', 'update', 'overview', 'changes', 'history', 'compare', 'research', 'archive')))
check("正文含纪律命令式条目(禁重算/缺失不填0/事实推断分离)",
      '禁止自行计算' in text and '缺失就是缺失' in text and '【推断】' in text)
check("正文含身份字段语义说明(is_proxy/代理口径)",
      'is_proxy' in text and 'ETF 代理' in text)
check("正文含 references 触发指针(一层引用链)",
      text.count('references/') >= 3)
# 引用文件存在且为相对路径
ref_names = set(re.findall(r'references/([A-Za-z0-9_-]+\.md)', text))
check(f"引用的 references 文件全部在场({sorted(ref_names)})",
      ref_names and all(os.path.isfile(os.path.join(REFS_DIR, r)) for r in ref_names))
check("引用仅一层(references 内不再引 references/)",
      all('references/' not in open(os.path.join(REFS_DIR, r), encoding='utf-8').read()
          for r in os.listdir(REFS_DIR) if r.endswith('.md')))

print("═" * 60)
print("[4] 公开清洗红线(db4c790 延伸: 源零个人路径)")
print("═" * 60)
all_files = [SKILL_MD] + [os.path.join(REFS_DIR, f) for f in os.listdir(REFS_DIR)]
for p in all_files:
    body = open(p, encoding='utf-8').read()
    check(f"零个人绝对路径: {os.path.basename(p)}",
          '/Users/' not in body and '$HOME/AI内容' not in body
          and 'investment-agent-dev' not in body)
    check(f"零密钥形态: {os.path.basename(p)}",
          not re.search(r'sk-[A-Za-z0-9]{16,}|api[_-]?key\s*[:=]\s*\S{8,}', body, re.I))

print("═" * 60)
print("[5] 安装产物与仓库卫生")
print("═" * 60)
gitignore = open(os.path.join(ROOT, '.gitignore'), encoding='utf-8').read()
check(".gitignore 覆盖 .claude/(项目级安装产物不入库)",
      any(l.strip() in ('.claude/', '.claude') for l in gitignore.splitlines()))
check(".gitignore 覆盖 engine-path.json(个人路径文件永不入库)",
      'engine-path.json' in gitignore)
# 已装项目副本(若在)必须与源字节一致,防漂移
proj_copy = os.path.join(ROOT, '.claude', 'skills', 'global-macro-research', 'SKILL.md')
if os.path.isfile(proj_copy):
    check("项目级安装副本与源字节一致(防漂移)",
          open(proj_copy, 'rb').read() == open(SKILL_MD, 'rb').read())
else:
    print("  ⏭️ 项目级副本未安装,字节一致断言跳过(install_skill.py --target project 生成)")

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
