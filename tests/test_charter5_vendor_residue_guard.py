#!/usr/bin/env python3
"""Charter 5 S7 新增套件③: vendor_residue 守卫(公开仓厂商残留静态扫描)。

用户指令(2026-11-09)"不要出现任何glm相关的东西"落在 v2.1 实施面 =
A2 清单 S1-S8 的机器面清零。本守卫静态扫描仓内源码/配置/文档,锁定:

零容忍面(任何文件出现即 FAIL):
- 旧模块名 glm_input_assembler / glm_output_validator /
  glm_conclusion_integrator / glm_conclusion_client(含 import/字符串/注释);
- 类名 GLMResearchInput;--glm 旗标;RUN_GLM_LIVE 旧门名;
  glm4_*/glm_conclusions_archive 产物名;glm_key_note/GLM_KEY_MISSING_MESSAGE;
  GLM_BASE_URL/GLM_MODEL 旧变量名;ZHIPU_PRESET 预设;bigmodel.cn 端点;
- 角色词面(D 轮裁定,2026-11-09): _call_glm/_glm_call 旧函数名、GLM裁决/
  调GLM/调用GLM 消息与文案、GLM 数据包/GLM 研究输入产物称谓、L3-glm 层键、
  glm_resolved 变量名、零GLM/不调用GLM 纪律措辞(统一=零模型调用/模型裁决)。

白名单(唯一例外,各有归属理由):
- 密钥卫生名单(防用户旧 Key 泄漏,安全功能,Charter5 唯一豁免):
  scripts/redact_secrets.py / scripts/real_data_acceptance.py /
  scripts/model_conclusion_client.py 的 redact 值级剥离;
- 旧档兼容映射(S6 读取层,旧 sidecar 'glm' 键→'model'):
  scripts/research_archive.py / ia_cli.py 中含 'glm' 的行;
- 断言"残留不存在"的负向守卫测试(守卫的守卫): 本文件与 test_oss_product;
  test_skill_installer ⑪ 装机副本防漂移(断言安装产物零 --glm/零旧键名)。

乙裁定(2026-11-09): project_final_seal.py(封版登记簿,含 L3-glm 层键与
历史交付件名,登记簿改名=伪造)与 test_p3_wp_f.py 已整体移出公开仓至
~/investment-agent-docs-archive/scripts/(110 测试在归档侧保覆盖,归档侧
不属本守卫扫描面);公开仓 CI 套件数 107→106。
"""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PASS, FAIL = 0, 0


def check(name, cond, detail=''):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


def iter_files():
    """仓内受扫面: 源码/配置/文档/CI,排除运行时产物与第三方目录。"""
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in
                       ('.git', '__pycache__', 'output', 'data', 'node_modules',
                        '.venv', 'venv', 'archive', '.claude')]   # .claude=gitignored 本地安装副本
        for fn in filenames:
            if fn.endswith(('.py', '.md', '.yml', '.yaml', '.json', '.example',
                            '.txt', '.sh')):
                yield os.path.join(dirpath, fn)


# 零容忍模式(机器面)
HARD_PATTERNS = [
    (r'glm_input_assembler|glm_output_validator|glm_conclusion_integrator'
     r'|glm_conclusion_client', '旧模块名'),
    (r'GLMResearchInput', '旧类名'),
    (r'--glm\b', '--glm 旗标'),
    (r'RUN_GLM_LIVE', '旧门控变量名'),
    (r'glm4_|glm_conclusions_archive', '旧产物文件名'),
    (r'glm_key_note|GLM_KEY_MISSING_MESSAGE', '旧医生面键/常量'),
    (r'GLM_BASE_URL|GLM_MODEL\b', '旧模型变量名'),
    (r'ZHIPU_PRESET', '厂商预设常量'),
    (r'bigmodel\.cn', '厂商端点域名'),
    # ── D 轮(2026-11-09)角色词面增补: 机械改名后全仓零命中 ──
    (r'_call_glm\b|_glm_call\b', '旧调用函数名'),
    (r'GLM裁决|调GLM|调用GLM', '判决消息/文案角色词'),
    (r'GLM 数据包|GLM 研究输入', '旧产物称谓'),
    (r'L3-glm', '旧登记层键(乙类已移出公开仓)'),
    (r'glm_resolved', '旧变量名'),
    (r'零 ?GLM|不调用 ?GLM', '旧纪律措辞(=零模型调用)'),
]

# 白名单文件(整文件豁免,理由见模块 docstring)
HYGIENE_ALLOW = {
    os.path.join(ROOT, 'scripts', 'redact_secrets.py'),          # 密钥卫生
    os.path.join(ROOT, 'scripts', 'real_data_acceptance.py'),    # 密钥卫生名单
    os.path.join(ROOT, 'scripts', 'model_conclusion_client.py'),  # redact 值级剥离
    os.path.join(ROOT, 'tests', 'test_redact_gap_matrix.py'),    # 卫生面行为锁
    os.path.join(ROOT, 'tests', 'test_p0_sbflow_backup.py'),     # sha 冻结锁(引用卫生名单行)
    os.path.join(ROOT, 'tests', 'test_oss_product.py'),          # 负向守卫(断言缺席)
    os.path.join(ROOT, 'tests', 'test_charter5_zero_key_matrix.py'),     # 负向守卫(剥离旧变量名)
    os.path.join(ROOT, 'tests', 'test_charter5_usage_actual_values.py'),  # 负向守卫(断言缺席)
    os.path.join(ROOT, 'tests', 'test_charter5_vendor_residue_guard.py'),  # 本文件
    os.path.join(ROOT, 'tests', 'test_skill_installer.py'),  # ⑪ 装机副本防漂移(负向守卫)
}
# 旧档兼容行(S6): research_archive/ia_cli 中含 'glm' 的行级豁免
LEGACY_KEY_FILES = {
    os.path.join(ROOT, 'scripts', 'research_archive.py'),
    os.path.join(ROOT, 'ia_cli.py'),
}
LEGACY_LINE_MARK = re.compile(r"LEGACY|旧档|旧 sidecar|'glm'", re.I)

print("═" * 64)
print("Charter5 S7-③ vendor_residue 守卫(公开仓厂商残留静态扫描)")
print("═" * 64)

# ── 1. 文件名面: 无 glm 命名文件 ──
bad_names = [f for f in iter_files()
             if 'glm' in os.path.basename(f).lower()]
check("文件名零 glm 残留(模块/套件/文档)", not bad_names, str(bad_names))

# ── 2. 内容面: 零容忍模式逐文件扫描 ──
violations = []
for path in iter_files():
    if path in HYGIENE_ALLOW:
        continue
    try:
        text = open(path, encoding='utf-8', errors='replace').read()
    except OSError:
        continue
    if path in LEGACY_KEY_FILES:
        # 行级豁免: 旧档兼容映射行合法,其余行照常扫
        lines = [l for l in text.splitlines()
                 if not LEGACY_LINE_MARK.search(l)]
        text = '\n'.join(lines)
    for pat, label in HARD_PATTERNS:
        for m in re.finditer(pat, text):
            violations.append(f'{label}: {os.path.relpath(path, ROOT)}:'
                              f'…{text[max(0, m.start()-20):m.end()+20]!r}')
check("零容忍模式全仓零命中(旧模块/类/旗标/门名/产物/键/预设/端点)",
      not violations, '; '.join(violations[:5]))

# ── 3. 行为面: --glm 被 CLI 拒绝(旗标彻底删除,不留别名) ──
env = {k: v for k, v in os.environ.items()
       if not k.startswith(('MODEL_', 'GLM_'))}
r = subprocess.run([sys.executable, os.path.join(ROOT, 'ia_cli.py'),
                    'research', '--question', 'x', '--glm'],
                   capture_output=True, text=True, env=env, cwd=ROOT,
                   timeout=120)
check("research --glm→argparse 拒绝(rc=2,旗标已删除)",
      r.returncode == 2 and 'unrecognized arguments' in r.stderr,
      r.stderr[:120])

# ── 4. 行为面: doctor 输出零旧厂商词 ──
r = subprocess.run([sys.executable, os.path.join(ROOT, 'ia_cli.py'), 'doctor'],
                   capture_output=True, text=True, env=env, cwd=ROOT,
                   timeout=120)
check("doctor 输出零 glm/zhipu/bigmodel(大小写任意)",
      r.returncode == 0
      and not any(t in (r.stdout + r.stderr).lower()
                  for t in ('glm', 'zhipu', 'bigmodel')),
      r.stdout[:150])

# ── 5. env_config 源码级唯一凭证面 ──
ec_src = open(os.path.join(ROOT, 'env_config.py'), encoding='utf-8').read()
check("env_config 源码零 glm 词面(唯一凭证面=MODEL_*)",
      'glm' not in ec_src.lower())

sys.exit(0 if FAIL == 0 else 1)
