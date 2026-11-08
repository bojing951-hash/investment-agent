#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""密钥脱敏共享原语(P0-4, 2026-11-09)。

针对 URL 查询参数形态的密钥泄漏: 采集器异常文本(requests 抛错常内嵌完整
URL,如 ...?series_id=X&api_key=SECRET&file_type=json)经 print/流水线台账/
JSON tail 外泄的主通道。值域 [A-Za-z0-9_-]+ 足以覆盖典型密钥形态且天然
幂等(***REDACTED*** 不含该字符集,再过一遍不变)。

刻意**不**泛化到裸 32/64 位 hex: 会误伤快照 sources sha256 摘要等合法
指纹(实测通道摘要逐日入台账/信封)。需要更宽口径的场景用
real_data_acceptance.sanitize_text(登记已知密钥明文的纵深防御版)。

用法: from redact_secrets import redact; print(redact(str(e)))
"""
import re

_SECRET_QS_RE = re.compile(
    r"([?&](?:api_key|apikey|token|key)=)([A-Za-z0-9_\-]+)", re.IGNORECASE)


def redact(text):
    """URL 查询参数密钥值 → ***REDACTED***;非字符串原样返回。幂等。"""
    if not isinstance(text, str):
        return text
    return _SECRET_QS_RE.sub(r"\1***REDACTED***", text)


def _selftest():
    """自带单测: python3 scripts/redact_secrets.py"""
    fake = 'FAKEKEY0123456789abcdef'
    cases = [
        # (输入, 必含, 必不含)
        (f"https://api.stlouisfed.org/fred/series/observations?series_id=DFF&api_key={fake}&file_type=json",
         'api_key=***REDACTED***', fake),
        (f"HTTPSConnectionPool(url='/x?apikey={fake}')", 'apikey=***REDACTED***', fake),
        (f"GET /news?token={fake} HTTP/1.1", 'token=***REDACTED***', fake),
        (f"quote?key={fake}&symbol=AAPL", 'key=***REDACTED***', fake),
        ("API_KEY=abc123&x=1", "API_KEY=abc123", 'REDACTED'),   # 无 ?/& 前缀不误伤
        (f"sha256={fake}{fake}", f"sha256={fake}{fake}", '***'),  # 摘要不误伤
    ]
    n = 0
    for text, must_have, must_not in cases:
        out = redact(text)
        assert must_have in out and must_not not in out, (text, out)
        n += 1
    # 幂等 + 非字符串
    once = redact(f"?api_key={fake}")
    assert redact(once) == once
    assert redact(None) is None and redact(123) == 123
    print(f"redact_secrets 自测: {n}用例+幂等+类型 全部通过")


if __name__ == '__main__':
    _selftest()
