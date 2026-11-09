#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""密钥脱敏共享原语(P0-4, 2026-11-09;W4 模式补全=Model-Agnostic v2)。

针对密钥泄漏的三大回显通道,三种模式族全部覆盖——
- 参数形(URL查询/裸键回显): ...?series_id=X&api_key=SECRET&file_type=json
  与 403 body "api_key=SECRET is invalid"(无 ?/& 前缀)。W4 扩:
  复合变量名 model_api_key= / glm_api_key= 同族覆盖(排在交替项前部,
  负向后顾 (?<![a-z0-9_]) 挡 monkey=/license_key=/sha256= 等中缀误伤)。
- JSON冒号形(429/错误体常见): "api_key": "SECRET" / camelCase "apiKey":
  组1含键名与开引号,值域 [^"]+ 止于闭引号前(闭引号留原位);幂等由
  "重脱敏=原值不变"保证(***REDACTED*** 仍在 [^"]+ 内,再过一遍输出相同)。
- Header形: Authorization: Bearer SECRET / x-api-key: SECRET(大小写与
  :/= 分隔均容错)。值域 [A-Za-z0-9_\\-.]+ 覆盖 sk-…/JWT形态;幂等用
  函数替换守护——已脱敏串 "Authorization: Bearer ***REDACTED***" 二过
  时值域不匹配 *,回溯会咬住裸词 Bearer,故值.lower()=='bearer' 时
  原样返回(既挡重匹配,也放过"仅头+方案词无值"的无泄漏形态)。

刻意**不**覆盖(无锚不猜,防误伤):
- 裸 Bearer(无头名)/OpenAI 式散文回显: 由 glm_conclusion_client.redact
  在值=进程内登记明文(MODEL_API_KEY/GLM_API_KEY)时纵深兜底;
- 裸 32/64 位 hex 泛化: 会误伤快照 sources sha256 摘要等合法指纹
  (实测通道摘要逐日入台账/信封)。需要更宽口径的场景用
  real_data_acceptance.sanitize_text(登记已知密钥明文的纵深防御版)。

用法: from redact_secrets import redact; print(redact(str(e)))
"""
import re

_SECRET_QS_RE = re.compile(
    r"((?<![a-z0-9_])(?:model_api_key|glm_api_key|api_key|apikey|token|key)=)"
    r"([A-Za-z0-9_\-]+)",
    re.IGNORECASE)
_SECRET_JSON_RE = re.compile(
    r'("(?:model_api_key|glm_api_key|api_key|apikey|token|key)"\s*:\s*")[^"]+',
    re.IGNORECASE)
_SECRET_HEADER_RE = re.compile(
    r"((?:authorization|x-api-key)\s*[:=]\s*(?:bearer\s+)?)([A-Za-z0-9_\-.]+)",
    re.IGNORECASE)


def _header_sub(m):
    """Header形替换守护: 值恰为方案词 bearer(已脱敏二过回溯/裸方案)→原样。"""
    if m.group(2).lower() == 'bearer':
        return m.group(0)
    return m.group(1) + '***REDACTED***'


def redact(text):
    """参数形(api_key/apikey/token/key/model_api_key/glm_api_key=)、JSON冒号形
    ("api_key": …)、Header形(Authorization/x-api-key)→ ***REDACTED***;
    非字符串原样返回。幂等(逐模式验证,见 tests/test_redact_gap_matrix.py)。"""
    if not isinstance(text, str):
        return text
    text = _SECRET_QS_RE.sub(r"\1***REDACTED***", text)
    text = _SECRET_JSON_RE.sub(r'\1***REDACTED***', text)
    return _SECRET_HEADER_RE.sub(_header_sub, text)


def _selftest():
    """自带单测: python3 scripts/redact_secrets.py"""
    fake = 'FAKEKEY0123456789abcdef'
    sk = 'sk-FAKEproj1234567890abcdef'
    cases = [
        # (输入, 必含, 必不含)
        (f"https://api.stlouisfed.org/fred/series/observations?series_id=DFF&api_key={fake}&file_type=json",
         'api_key=***REDACTED***', fake),
        (f"HTTPSConnectionPool(url='/x?apikey={fake}')", 'apikey=***REDACTED***', fake),
        (f"GET /news?token={fake} HTTP/1.1", 'token=***REDACTED***', fake),
        (f"quote?key={fake}&symbol=AAPL", 'key=***REDACTED***', fake),
        # 裸键回显(403 body 形态): 无 ?/& 前缀也脱敏
        (f'403 Client Error: body: {{"error_message":"api_key={fake} is invalid"}}',
         'api_key=***REDACTED***', fake),
        (f"API_KEY={fake}&x=1", 'API_KEY=***REDACTED***', fake),  # 大小写不敏感
        # W4 模式补全——复合变量/JSON冒号/Header形
        (f"GLM_API_KEY={fake}", 'GLM_API_KEY=***REDACTED***', fake),
        (f"MODEL_API_KEY={fake}", 'MODEL_API_KEY=***REDACTED***', fake),
        (f'{{"error":{{"apiKey":"{fake}"}}}}', '"apiKey":"***REDACTED***"', fake),
        (f'{{"model_api_key": "{fake}"}}', '"model_api_key": "***REDACTED***"', fake),
        (f'Authorization: Bearer {sk}', 'Authorization: Bearer ***REDACTED***', sk),
        (f'x-api-key: {sk}', 'x-api-key: ***REDACTED***', sk),
        (f"monkey=ab license_key={fake}", f"license_key={fake}", '***'),  # 负向后顾: 中缀词不误伤
        (f"sha256={fake}{fake}", f"sha256={fake}{fake}", '***'),  # 摘要不误伤
    ]
    n = 0
    for text, must_have, must_not in cases:
        out = redact(text)
        assert must_have in out and must_not not in out, (text, out)
        n += 1
    # 幂等 + 非字符串 + 边界(无锚不猜)
    once = redact(f"?api_key={fake} | Authorization: Bearer {sk} | {{\"token\":\"{fake}\"}}")
    assert redact(once) == once, once
    assert redact(None) is None and redact(123) == 123
    bare = f'Bearer {sk}'                      # 裸 Bearer 无头名: 本层不猜
    assert redact(bare) == bare
    print(f"redact_secrets 自测: {n}用例+幂等+类型+边界 全部通过")


if __name__ == '__main__':
    _selftest()
