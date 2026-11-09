#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""redact 覆盖矩阵回归(Model-Agnostic v2 W4, 2026-11-09)。

底稿=审计D /tmp/auditD/gap_matrix.py 的 10 格泄漏矩阵(A1~D3)+误伤组,
落为仓内常驻回归。两条脱敏路径各自断言边界:
- redact_secrets.redact: 参数形(URL/裸键,含 model_api_key/glm_api_key
  复合名)、JSON冒号形(含 camelCase apiKey)、Header形(Authorization/
  x-api-key,值域 [A-Za-z0-9_.-]+);幂等性逐格验证。
- model_conclusion_client.redact: 登记明文(进程内 MODEL_API_KEY/GLM_API_KEY
  值)任意位置 + Authorization 头的纵深版对照。

刻意边界(断言"不脱敏",是设计而非遗漏):
- OpenAI 式散文回显: redact_secrets 无锚不猜,由 mcc.redact 在值=已登记
  明文时兜底;裸 Bearer 批2 W7 已覆盖(16+ 长度下限防自然语言误伤,
  短串按设计保留);
- 裸 hex/指纹泛化: 会误伤快照 sources sha256 摘要,明确不做。
运行: python3 tests/test_redact_gap_matrix.py(零 pytest,零真实出站)。
"""
import os
import sys

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


print("=" * 60)
print("redact 覆盖矩阵回归(审计D底稿)")
print("=" * 60)

from redact_secrets import redact           # noqa: E402

FAKE = 'FAKEKEYabcdef789xyz'
SK = 'sk-FAKEproj1234567890abcdef'

# ── 一、redact_secrets 覆盖格(审计D A1-D3;W4 扩模式后应全绿) ────────
print("\n[1] 覆盖矩阵(泄漏值必须消失,***REDACTED*** 必须出现)")
COVERED = [
    ('A1 URL参数 api_key=', f'?api_key={FAKE}&x=1', 'api_key='),
    ('A2 裸键回显 api_key=', f'api_key={FAKE} is invalid', 'api_key='),
    ('B1 复合名 GLM_API_KEY=', f'GLM_API_KEY={FAKE}', 'GLM_API_KEY='),
    ('B2 复合名 MODEL_API_KEY=', f'MODEL_API_KEY={FAKE}', 'MODEL_API_KEY='),
    ('B2b 小写复合名 model_api_key=', f'config model_api_key={FAKE} parsed', 'model_api_key='),
    ('C1 Header Authorization: Bearer', f'Authorization: Bearer {SK}', 'Authorization: Bearer '),
    ('C1b 小写 authorization= bearer', f'authorization=Bearer {SK}', 'authorization=Bearer '),
    ('C3 Header x-api-key:', f'x-api-key: {SK}', 'x-api-key: '),
    ('C3b 大写 X-API-KEY=', f'X-API-KEY={SK}', 'X-API-KEY='),
    ('D1 JSON冒号 "api_key"', f'{{"api_key": "{FAKE}"}}', '"api_key": '),
    ('D1b JSON无空格 "token"', f'{{"token":"{FAKE}"}}', '"token":'),
    ('D3 JSON camelCase apiKey(429体)', f'{{"error":{{"apiKey":"{FAKE}"}}}}', '"apiKey": '),
    ('D3b JSON "model_api_key"', f'{{"model_api_key": "{FAKE}"}}', '"model_api_key": '),
    ('C2 裸 Bearer 无头名(16+长值,批2W7)', f'Bearer {SK}', 'Bearer '),
    ('C2c 裸 Bearer 40字符真实Key形态', 'Bearer sk-' + 'K' * 30, 'Bearer '),
]
for name, cell, anchor in COVERED:
    out = redact(cell)
    check(name, FAKE not in out and SK not in out and '***REDACTED***' in out,
          f'out={out[:70]}')

# ── 二、边界格(无锚不猜——redact_secrets 刻意不动,纵深由 mcc 承担) ────
print("\n[2] 边界(散文回显/短串/自然语言: 本层不猜或按设计保留)")
BOUNDARY = [
    ('D2 OpenAI式散文回显(未登记值)', f'Incorrect API key provided: {SK}'),
    ('C2b 裸 Bearer 短值(<16,长度下限保留)', 'Bearer sk-short1'),
    ('自然语句 the Bearer of good news…', 'the Bearer of good news arrives today'),
]
for name, cell in BOUNDARY:
    out = redact(cell)
    check(f"{name}→原样(由gcc登记明文兜底)", out == cell, f'out={out[:70]}')

# ── 三、幂等(全部覆盖格+边界格二过不变;Header形防Bearer重匹配) ────────
print("\n[3] 幂等性 redact(redact(x)) == redact(x)")
for name, cell, _anchor in COVERED:
    once = redact(cell)
    check(f"幂等 {name}", redact(once) == once, f'2nd={redact(once)[:70]}')
for name, cell in BOUNDARY:
    check(f"幂等 {name}", redact(redact(cell)) == redact(cell))

# ── 四、误伤组(负向后顾/头名锚: 合法字段不脱敏) ─────────────────────
print("\n[4] 误伤组(合法字段原样)")
FALSE_POS = [
    ('monkey= 中缀词', f'monkey={FAKE}'),
    ('license_key= 复合词', f'license_key={FAKE}'),
    ('sha256= 指纹摘要', f'sha256={FAKE}{FAKE}'),
    ('digest= 摘要', f'digest={FAKE}'),
    ('monkeypatch 键名散文', f'the monkey= and zoo_key={FAKE} stay'),
]
for name, cell in FALSE_POS:
    out = redact(cell)
    check(name, out == cell, f'out={out[:70]}')

# ── 五、多行文本(逐行独立命中) ───────────────────────────────────────
print("\n[5] 多行文本")
multi = (f"GET /x?api_key={FAKE} HTTP/1.1\n"
         f"Authorization: Bearer {SK}\n"
         f'body: {{"token": "{FAKE}"}}\n'
         f"GLM_API_KEY={FAKE}\n"
         f"plain line stays")
out = redact(multi)
check("四行泄漏全消+明文行保留", FAKE not in out and SK not in out
      and 'plain line stays' in out and out.count('***REDACTED***') == 4,
      f'out={out[:120]}')
check("多行幂等", redact(out) == out)

# ── 六、mcc.redact 纵深对照(登记明文任意位置+Authorization) ───────────
print("\n[6] model_conclusion_client.redact(登记明文纵深版)")
import model_conclusion_client as mcc        # noqa: E402
_saved = {k: os.environ.get(k) for k in ('MODEL_API_KEY', 'GLM_API_KEY')}
try:
    os.environ.pop('MODEL_API_KEY', None)
    os.environ['GLM_API_KEY'] = FAKE       # 登记 FAKE 为进程内已知明文
    GCC_CELLS = [
        ('C1 Authorization: Bearer', f'Authorization: Bearer {SK}'),
        ('E1 登记明文任意位置', f'prefix {FAKE} suffix'),
        ('B2 裸Bearer(值=登记明文)', f'Bearer {FAKE}'),
        ('D2 散文回显(值=登记明文)', f'Incorrect API key provided: {FAKE}'),
    ]
    for name, cell in GCC_CELLS:
        out = mcc.redact(cell)
        check(name, FAKE not in out and SK not in out, f'out={out[:70]}')
    # 未登记值且无头名锚: 纵深版同样不猜(边界对称)
    check('未登记裸Bearer→原样(对称边界)', mcc.redact(f'Bearer {SK}') == f'Bearer {SK}')
finally:
    for k, v in _saved.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v

# ── 七、非字符串与空值 ────────────────────────────────────────────────
print("\n[7] 类型边界")
check("None/数字原样", redact(None) is None and redact(123) == 123)
check("空串不变", redact('') == '')

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
