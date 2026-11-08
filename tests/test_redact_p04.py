#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P0-4 密钥卫生测试(Skill 化 v1.1, 2026-11-09)。

虚构密钥(FAKEKEY0123456789abcdef 等,绝不使用真实密钥)构造含密钥 URL 的
异常文本,断言: print 输出/持久化 source_status/ia_cli JSON tail 中密钥串
不出现、***REDACTED*** 出现。

覆盖四层:
① redact_secrets.redact 单元(参数族/幂等/sha256 摘要不误伤);
② rate_expectations._fred_observations 异常路径 print 已脱敏 + HTTP 状态码可见;
③ news_collector 打印路径与 collect_all_news 持久化 source_status 已脱敏;
④ ia_cli update 三条 tail(output/critical/stderr)入 JSON 前已脱敏。
"""
import contextlib
import io
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

PASS, FAIL = 0, 0

FAKE = 'FAKEKEY0123456789abcdef'
FAKE_URL = (f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id=DFF&api_key={FAKE}&file_type=json")


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


print("=" * 60)
print("① redact_secrets.redact 单元")
print("=" * 60)
from redact_secrets import redact
out = redact(FAKE_URL)
check("api_key= 值脱敏", 'api_key=***REDACTED***' in out and FAKE not in out)
check("token=/key=/apikey= 同族脱敏",
      'token=***REDACTED***' in redact(f"/x?token={FAKE}")
      and 'key=***REDACTED***' in redact(f"/x?key={FAKE}")
      and 'apikey=***REDACTED***' in redact(f"/x?apikey={FAKE}"))
check("幂等(已脱敏再过不变)", redact(redact(FAKE_URL)) == redact(FAKE_URL))
check("sha256 摘要不误伤(64hex 裸串原样)",
      redact(f"sha256={'a' * 64}") == f"sha256={'a' * 64}")
check("非字符串原样返回", redact(None) is None and redact(42) == 42)

print()
print("=" * 60)
print("② rate_expectations: 异常 print 脱敏 + HTTP 状态码")
print("=" * 60)
import rate_expectations as rex


class _Resp400:
    status_code = 400

    @staticmethod
    def json():
        return {'error': 'bad key'}


def _capture(fn):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        result = fn()
    return buf.getvalue(), result


def _raise_get(url, params=None, timeout=None):
    raise RuntimeError(f"HTTPSConnectionPool url='{FAKE_URL}' timed out")


def _resp400_get(url, params=None, timeout=None):
    return _Resp400()


real_get = rex.requests.get
try:
    rex.requests.get = _raise_get
    text, obs = _capture(lambda: rex._fred_observations('DFF', tries=1))
    check("重试失败 print 不含密钥串", FAKE not in text)
    check("print 含 ***REDACTED***", '***REDACTED***' in text)
    check("失败返回空观测列表", obs == [])
    rex.requests.get = _resp400_get
    text, obs = _capture(lambda: rex._fred_observations('DFF', tries=1))
    check("非200 → HTTP 状态码可见(此前不可见)", 'HTTP 400' in text)
finally:
    rex.requests.get = real_get

print()
print("=" * 60)
print("③ news_collector: print + 持久化 source_status")
print("=" * 60)
try:
    import news_collector as nc
    HAVE_NC = True
except Exception as e:  # noqa: BLE001 —— 第三方依赖缺失时跳过本节
    HAVE_NC = False
    print(f"  ⏭️ 跳过(finnhub/openai/feedparser 不可用: {type(e).__name__})")

if HAVE_NC:
    class _BoomClient:
        @staticmethod
        def general_news(*a, **k):
            raise RuntimeError(f"GET /api/news?token={FAKE} 401 Unauthorized")

    real_client = nc.fh_client
    try:
        nc.fh_client = _BoomClient()
        text, (items, status, err) = _capture(nc.fetch_market_news)
        check("市场新闻失败 print 不含密钥串", FAKE not in text)
        check("print 含 ***REDACTED***", '***REDACTED***' in text)
        check("状态如实 ERROR", status == nc.ST_ERROR)
        # 持久化通道: collect_all_news 的 source_status(写进采集档)
        real_fetchers = (nc.fetch_market_news, nc.fetch_company_news, nc.fetch_rss_news)
        try:
            nc.fetch_market_news = lambda: ([], nc.ST_ERROR,
                                            f"HTTPSConnectionPool url='{FAKE_URL}'")
            nc.fetch_company_news = lambda: ([], {})
            nc.fetch_rss_news = lambda: ([], {})
            text, (_raw, source_status, _disp) = _capture(nc.collect_all_news)
            persisted = source_status.get('Finnhub/general:error', '')
            check("持久化 source_status 不含密钥串", FAKE not in persisted, persisted)
            check("持久化 source_status 含 ***REDACTED***", '***REDACTED***' in persisted)
        finally:
            nc.fetch_market_news, nc.fetch_company_news, nc.fetch_rss_news = real_fetchers
    finally:
        nc.fh_client = real_client

print()
print("=" * 60)
print("④ ia_cli update 三条 tail 入 JSON 前脱敏")
print("=" * 60)
import ia_cli


class FakeProc:
    returncode = 1
    stdout = (f"⚠️ FRED 请求失败: {FAKE_URL}\n⛔ 快照已存在且不可变\n")
    stderr = f"connection error: {FAKE_URL}\n"


args = ia_cli.build_parser().parse_args(['update', '--yes'])
captured = {}


def fake_run(cmd, **kwargs):
    captured['called'] = True
    return FakeProc()


real_run = subprocess.run
ia_cli.subprocess.run = fake_run
out = io.StringIO()
rc = None
try:
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        try:
            ia_cli.cmd_update(args)
        except SystemExit as e:
            rc = e.code
finally:
    ia_cli.subprocess.run = real_run
whole = out.getvalue()
d = json.loads(whole)
check("整个 stdout(含三条 tail)无密钥串", FAKE not in whole)
check("output_tail 已脱敏", 'api_key=***REDACTED***' in d['data']['output_tail'][0])
check("critical_tail 已脱敏(⛔ 行不在 tail 窗口也筛进 critical)",
      any('⛔' in l for l in d['data']['critical_tail'])
      and all(FAKE not in l for l in d['data']['critical_tail']))
check("stderr_tail 已脱敏", '***REDACTED***' in d['data']['stderr_tail'][0]
      and FAKE not in d['data']['stderr_tail'][0])

print()
print("═" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("═" * 60)
sys.exit(0 if FAIL == 0 else 1)
