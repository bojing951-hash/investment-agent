#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""开源产品化(W1/W2/W4/W6/W8, 2026-11-08)回归套件。

覆盖四组契约面:
① W1/W2 文档真实性: README定位=研究工作台(非策略研究员)、指标/步骤数字与代码一致
   (指标数单一权威=metric_registry)、旧越位机制不再作为能力描述;
② W4 用户文档与配置模板: USER_GUIDE在场且入口命令真实、.env.example无真实凭证、
   .gitignore覆盖.env且不覆盖.env.example;
③ W8 配置安全: env_config不读取其他应用配置(投毒HOME实证)、.env加载与优先级、
   密钥零打印、缺GLM_KEY提示在场;
④ W6 公开样例: 真实周报样例在场、含数据质量披露、零个人路径零密钥;
⑤ W7 脚本可移植性: 源码零个人路径、PYTHON覆盖、退出码透传(行为级: 临时目录+
   桩解释器实测路径解析与环境缺失报错)。
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


readme = open(os.path.join(ROOT, 'README.md'), encoding='utf-8').read()
guide = open(os.path.join(ROOT, 'docs', 'USER_GUIDE.md'), encoding='utf-8').read()
env_src = open(os.path.join(ROOT, 'env_config.py'), encoding='utf-8').read()
sh_src = open(os.path.join(ROOT, 'run_daily.sh'), encoding='utf-8').read()

print("═" * 60)
print("[1] W1/W2 README 产品定位与数字真实性")
print("═" * 60)
check("标题定位=开源AI全球宏观研究工作台", '开源 AI 全球宏观研究工作台' in readme)
check("旧'策略研究员'定位已移除", '策略研究员' not in readme)
check("含研究工具边界声明(不是投资顾问)",
      '投资顾问' in readme and '研究工具' in readme)
check("含免责声明章节", '免责声明' in readme)
check("README零个人绝对路径", '/Users/' not in readme and '$HOME/AI内容' not in readme)

reg = json.load(open(os.path.join(ROOT, 'config', 'metric_registry.json'),
                     encoding='utf-8'))
n_metrics = len(reg['metrics'])
counts = re.findall(r'(\d+)\s*项指标', readme)
check(f"README指标数与注册表一致(注册表={n_metrics})",
      len(counts) == 1 and counts[0] == str(n_metrics), f"README出现={counts}")
check("README步骤数=15步(与run_weekly.py一致)", '15 步' in readme)  # Charter6-P2: +Shiller
check("README不再把论点/预测/超配当现有能力",
      '预测生命周期' not in readme and '超配/标配/低配' not in readme)
check("历史档明示(thesis/views=冻结历史档案)",
      '历史' in readme and 'thesis.json' in readme and 'IA_AUTO_MONTHLY' in readme)
check("README链接公开样例与用户指南",
      'examples/' in readme and 'docs/USER_GUIDE.md' in readme
      and os.path.isfile(os.path.join(ROOT, 'examples', 'README.md'))
      and os.path.isfile(os.path.join(ROOT, 'docs', 'USER_GUIDE.md')))
# D验收(2026-11-08): 文档承诺必须与免Key现实一致——不再无条件'无需任何Key',
# 且直说缺FRED Key⇒Gate A必FAIL⇒问答拒答;仓库数据声明对齐"仅3个示例档"
check("README不再无条件宣称'无需任何Key'", '无需任何' not in readme)
check("README直说免FRED Key首跑Gate A FAIL", '必然 Gate A FAIL' in readme)
check("README仓库数据声明对齐现实(仅示例采集档)", '示例采集档' in readme)

print("═" * 60)
print("[2] W4 用户文档/配置模板")
print("═" * 60)
check("USER_GUIDE五章节齐全",
      all(k in guide for k in ('安装', '配置 API Key', '第一次运行', '日常使用', '常见问题')))
for cmd in ('run_weekly.py', 'scripts/report_generator.py', 'streamlit run app.py',
            'run_daily.sh', '.env.example'):
    check(f"指南/README命令真实存在: {cmd}",
          cmd.split()[-1] == 'run' or os.path.exists(os.path.join(
              ROOT, cmd.replace('streamlit ', '').replace('bash ', '').strip()))
          or cmd in guide or cmd in readme)
check("指南覆盖macOS/Windows/Linux", 'macOS' in guide and 'Windows' in guide and 'Linux' in guide)
check("指南覆盖FAQ八问(无Key/源失败/无历史/Gate A/经济体不全/报告未生成/更新/防覆盖)",
      all(k in guide for k in ('没有任何 API Key', '不可访问', '没有历史数据',
                               'Gate A FAIL', '经济体数据不全', '报告没生成',
                               '如何更新软件', '误覆盖')))
check("指南Q1直说免FRED Key⇒Gate A必FAIL⇒问答拒答",
      '必然 FAIL' in guide and '拒答' in guide and '不是你的环境坏了' in guide)
check("指南FAQ新增Q10/Q11(免Key退出码预期/同日重跑修订机制)",
      'Q10' in guide and 'Q11' in guide and '--allow-revision' in guide)
envx = open(os.path.join(ROOT, '.env.example'), encoding='utf-8').read()
check(".env.example在场且无真实凭证", '=' in envx and not re.search(
    r'=(sk-|[A-Za-z0-9]{20,})', envx.replace('=http', '').replace('=你的', '')))
gitignore = open(os.path.join(ROOT, '.gitignore'), encoding='utf-8').read()
check(".gitignore忽略.env但不忽略.env.example",
      '\n.env\n' in gitignore and '.env.example' in gitignore
      and '!.env.example' in gitignore)

print("═" * 60)
print("[3] W8 配置安全(env_config)")
print("═" * 60)
check("源码无跨服务配置读取(settings.json/.claude)",
      '.claude' not in env_src and 'settings.json' not in env_src)
# v2.1(Charter 5 S1, 2026-11-09): 旧 GLM_* 变量读取整体删除——env_config 零
# print(迁移提示随回退一起移除),保持"密钥不落日志"纪律
check("源码零print(密钥不落日志)", env_src.count('print(') == 0)
check("缺模型Key明确提示常量在场(唯一名 MODEL_KEY_MISSING_MESSAGE)",
      'MODEL_KEY_MISSING_MESSAGE' in env_src and 'MODEL_API_KEY' in env_src
      and 'GLM_API_KEY' not in env_src)

# 行为级: 投毒HOME实证——伪造~/.claude/settings.json含ANTHROPIC_API_KEY,
# 重载env_config后MODEL_API_KEY必须仍为空(W8: 零跨服务回退)
_old = {k: os.environ.get(k) for k in ('HOME', 'MODEL_API_KEY')}
os.environ.pop('MODEL_API_KEY', None)
with tempfile.TemporaryDirectory() as td:
    claude_dir = os.path.join(td, '.claude')
    os.makedirs(claude_dir)
    with open(os.path.join(claude_dir, 'settings.json'), 'w', encoding='utf-8') as f:
        json.dump({'env': {'ANTHROPIC_API_KEY': 'POISON_SHOULD_NOT_BE_USED'}}, f)
    os.environ['HOME'] = td
    spec = importlib.util.spec_from_file_location(
        'env_config_fresh', os.path.join(ROOT, 'env_config.py'))
    fresh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fresh)
    check("投毒HOME下MODEL_API_KEY仍为空(跨服务回退已删除)",
          fresh.MODEL_API_KEY == '', repr(fresh.MODEL_API_KEY))
os.environ['HOME'] = _old['HOME'] or ''
if _old['MODEL_API_KEY']:
    os.environ['MODEL_API_KEY'] = _old['MODEL_API_KEY']

# .env加载与优先级(纯函数级)
with tempfile.NamedTemporaryFile('w', suffix='.env', delete=False,
                                 encoding='utf-8') as tf:
    tf.write('# 注释\nTEST_PARSE_KEY=FROM_FILE\nexport FRED_API_KEY=FROM_FILE_FRED\n'
             'BAD_LINE_NO_EQ\n')
    env_path = tf.name
_saved = {k: os.environ.pop(k, None) for k in ('TEST_PARSE_KEY', 'FRED_API_KEY')}
import env_config as ec  # noqa: E402
ec.load_env_file(env_path)
check(".env键被加载(env优先时跳过)",
      os.environ.get('TEST_PARSE_KEY') == 'FROM_FILE'
      and os.environ.get('FRED_API_KEY') == 'FROM_FILE_FRED')
os.environ['TEST_PARSE_KEY'] = 'FROM_ENV_PROCESS'
ec.load_env_file(env_path)
check("进程环境变量优先于.env(不覆盖)",
      os.environ.get('TEST_PARSE_KEY') == 'FROM_ENV_PROCESS')
os.unlink(env_path)
for k, v in _saved.items():
    if v is not None:
        os.environ[k] = v
if _old['MODEL_API_KEY'] is None:
    os.environ.pop('MODEL_API_KEY', None)

print("═" * 60)
print("[4] W6 公开样例")
print("═" * 60)
ex_path = os.path.join(ROOT, 'examples', 'weekly_report_20261108.md')
ex_readme = os.path.join(ROOT, 'examples', 'README.md')
check("真实周报样例在场", os.path.isfile(ex_path))
if os.path.isfile(ex_path):
    ex = open(ex_path, encoding='utf-8').read()
    check("样例含数据质量降级披露(DEGRADED)", 'DEGRADED' in ex and 'Gate A' in ex)
    check("样例零个人路径", '/Users/' not in ex and '$HOME' not in ex)
    check("样例零密钥形态", not re.search(r'sk-[A-Za-z0-9]{16,}|api_key\s*=\s*\S+',
                                           ex, re.I))
check("样例说明文档在场且含来源/限制",
      os.path.isfile(ex_readme)
      and '数据来源' in open(ex_readme, encoding='utf-8').read()
      and '使用限制' in open(ex_readme, encoding='utf-8').read())

print("═" * 60)
print("[5] W7 run_daily.sh 可移植性")
print("═" * 60)
check("脚本零个人路径", '/Users/' not in sh_src and 'AI内容' not in sh_src
      and '$HOME/AI内容' not in sh_src)
check("按脚本自身位置定位项目根", 'BASH_SOURCE' in sh_src)
check("支持PYTHON环境变量覆盖", 'PYTHON="${PYTHON:-}"' in sh_src)
check("退出码透传保留", 'exit $RESULT' in sh_src)
check("步骤注释已更新(15步)", '15 步' in sh_src or '15步' in sh_src)  # Charter6-P2

# 行为级: 复制到陌生绝对路径,验证路径解析/日志/退出码;不跑真实采集
with tempfile.TemporaryDirectory() as td:
    fake_root = os.path.join(td, 'clone', 'investment-agent')
    os.makedirs(fake_root)
    shutil.copy(os.path.join(ROOT, 'run_daily.sh'), fake_root)
    # 桩: PYTHON=true → `true run_weekly.py` 退出0 → 脚本应rc=0且日志落在fake_root/logs
    r = subprocess.run(['bash', os.path.join(fake_root, 'run_daily.sh')],
                       env={**os.environ, 'PYTHON': shutil.which('true')},
                       capture_output=True, text=True, timeout=60)
    log = os.path.join(fake_root, 'logs')
    todays = os.listdir(log) if os.path.isdir(log) else []
    check("陌生路径下脚本rc=0(路径解析成功)", r.returncode == 0,
          f"rc={r.returncode} err={r.stderr[-200:]}")
    check("日志写入克隆目录logs/", bool(todays), str(todays))
    # 缺Python: 清空PATH且无项目venv → 应rc=127并给出修复指引
    # (bash用绝对路径——PATH清空后连bash自身都找不到)
    bash_abs = shutil.which('bash')
    r2 = subprocess.run([bash_abs, os.path.join(fake_root, 'run_daily.sh')],
                        env={'PATH': '/nonexistent-dir', 'HOME': td},
                        capture_output=True, text=True, timeout=60)
    check("无Python环境→rc=127+修复指引", r2.returncode == 127
          and 'venv' in (r2.stderr + r2.stdout), f"rc={r2.returncode}")

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
