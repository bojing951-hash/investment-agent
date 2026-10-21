#!/usr/bin/env python3
"""第八轮(2026-10-21)P1修复回归: ZQ期货三层防御 + FRED重试 + Gate A退出码 + 曲线字段映射

背景: yfinance 429连续多日打满(10-18/19/20每日ZQ全11合约失败×11),
10-20 FRED PAYEMS单序列瞬时失败 → Gate A FAIL但流水线exit 0,launchd无感。
修复: ①ZQ=F优先+整轮退避重试(20s/45s)+7日缓存兜底(整曲线同源不混搭)
     ②FRED逐序列指数退避重试 ③Gate A FAIL→snapshot_builder退出码2
     ④fact_engine曲线映射label/implied_rate_pct(旧name/implied_rate恒None)
运行: ~/AI内容/venv/bin/python3 tests/test_p7_fixes.py
"""
import os
import sys
import json
import types
import shutil
import tempfile
import subprocess
from unittest import mock
from datetime import datetime, timedelta

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

import pandas as pd
import rate_expectations as re_mod
import fact_engine as fe


def _hist(price, date='2026-10-20'):
    return pd.DataFrame({'Close': [price]}, index=pd.DatetimeIndex([date]))


class _BoomTicker:
    def __init__(self, t):
        self._t = t
    def history(self, period='5d'):
        raise RuntimeError('Too Many Requests. Rate limited. Try after a while.')


class _MapTicker:
    """ticker→hist映射,缺失即抛429"""
    def __init__(self, mapping):
        self._m = mapping
    def __call__(self, t):
        if t in self._m:
            return types.SimpleNamespace(history=lambda period='5d': self._m[t])
        return _BoomTicker(t)


def _run_fetch(fake_ticker_factory, cache=None):
    """在假yfinance+假缓存下跑fetch_fed_funds_futures,返回结果列表"""
    fake_yf = types.SimpleNamespace(Ticker=fake_ticker_factory)
    cache_ret = cache if cache is not None else (None, None)
    with mock.patch.dict(sys.modules, {'yfinance': fake_yf}), \
         mock.patch.object(re_mod.time, 'sleep', lambda s: None), \
         mock.patch.object(re_mod, '_load_cached_futures', lambda **kw: cache_ret):
        return re_mod.fetch_fed_funds_futures()


CACHE_ROWS = [
    {'ticker': 'ZQ=F', 'label': '近月(活跃月)', 'price': 95.6,
     'implied_rate_pct': 4.4, 'date': '2026-10-20', 'source': 'yfinance'},
    {'ticker': 'ZQZ26.CBT', 'label': '2026年12月', 'price': 95.7,
     'implied_rate_pct': 4.3, 'date': '2026-10-20', 'source': 'yfinance'},
]

print("=" * 60)
print("P7修复: ZQ三层防御 / FRED重试 / Gate A退出码 / 曲线映射")
print("=" * 60)

# ══ [1] FRED重试 ══════════════════════════════════════════════
print("\n[1] FRED指数退避重试")

calls = {'n': 0}
def _flaky_get(url, params=None, timeout=None):
    calls['n'] += 1
    if calls['n'] == 1:
        raise ConnectionError('FRED瞬时抖动')
    return types.SimpleNamespace(json=lambda: {'observations': [{'value': '4.33', 'date': '2026-10-20'}]})

with mock.patch.object(re_mod, 'requests') as fake_req, \
     mock.patch.object(re_mod.time, 'sleep', lambda s: None):
    fake_req.get.side_effect = _flaky_get
    obs = re_mod._fred_observations('PAYEMS')
check("第1次失败第2次成功→返回观测", obs and obs[0]['value'] == '4.33', f"got={obs}")
check("实际发生了重试(≥2次调用)", calls['n'] >= 2, f"calls={calls['n']}")

def _always_fail(url, params=None, timeout=None):
    raise ConnectionError('持续失败')
calls2 = {'n': 0}
def _count_fail(url, params=None, timeout=None):
    calls2['n'] += 1
    raise ConnectionError('持续失败')
with mock.patch.object(re_mod, 'requests') as fake_req, \
     mock.patch.object(re_mod.time, 'sleep', lambda s: None):
    fake_req.get.side_effect = _count_fail
    obs = re_mod._fred_observations('PAYEMS', tries=3)
check("三次全失败→返回[]", obs == [])
check("重试次数=3(不无限)", calls2['n'] == 3, f"calls={calls2['n']}")

# ══ [2] ZQ三层防御 ═════════════════════════════════════════════
print("\n[2] ZQ期货429三层防御")

res = _run_fetch(_BoomTicker, cache=(CACHE_ROWS, '20261020'))
check("全限流→缓存兜底生效(ZQ=F在场)",
      any(r['ticker'] == 'ZQ=F' for r in res) and len(res) == 2)
check("缓存行带source=cache:日期标记",
      all(str(r.get('source', '')).startswith('cache:20261020') for r in res),
      f"sources={[r.get('source') for r in res]}")

# 主力失败但月份合约成功 → 整曲线换缓存,不与当日月份混搭
mapping = {f'ZQ{m}{y}.CBT': _hist(95.0 + i * 0.05)
           for i, (m, y) in enumerate([('V', '26'), ('X', '26'), ('F', '27')])}
res = _run_fetch(_MapTicker(mapping), cache=(CACHE_ROWS, '20261020'))
check("主力缺而月份有→整曲线走缓存(同源不混搭)",
      all(str(r.get('source', '')).startswith('cache:') for r in res) and len(res) == 2)

res = _run_fetch(_BoomTicker, cache=None)
check("无缓存可用→如实缺ZQ=F(不造数)",
      all(r['ticker'] != 'ZQ=F' for r in res) or not res)

full_map = {'ZQ=F': _hist(95.55)}
full_map.update({f'ZQ{m}{y}.CBT': _hist(95.0)
                 for m, y in [('V', '26'), ('X', '26')]})
called = {'cache': False}
def _spy_cache(**kw):
    called['cache'] = True
    return (None, None)
fake_yf = types.SimpleNamespace(Ticker=_MapTicker(full_map))
with mock.patch.dict(sys.modules, {'yfinance': fake_yf}), \
     mock.patch.object(re_mod.time, 'sleep', lambda s: None), \
     mock.patch.object(re_mod, '_load_cached_futures', _spy_cache):
    res = re_mod.fetch_fed_funds_futures()
check("首轮全部成功→不触碰缓存", not called['cache'] and res)
check("成功行source=yfinance", all(r.get('source') == 'yfinance' for r in res))
check("ZQ=F排在曲线首位(核心优先)", res[0]['ticker'] == 'ZQ=F')

# ══ [3] 缓存加载纯函数 ═════════════════════════════════════════
print("\n[3] _load_cached_futures文件挑选")

td = tempfile.mkdtemp()
def _write_rate(ymd, payload):
    with open(os.path.join(td, f'rate_economy_{ymd}.json'), 'w') as f:
        json.dump(payload, f)

fresh = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
stale = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
_write_rate(fresh, {'date': fresh, 'fed_funds_futures': CACHE_ROWS})
_write_rate(stale, {'date': stale, 'fed_funds_futures': CACHE_ROWS})
rows, src_date = re_mod._load_cached_futures(data_dir=td)
check("选最新7日内文件", rows == CACHE_ROWS and src_date == fresh, f"src={src_date}")
check("过期文件(>7日)不选", src_date != stale)

with open(os.path.join(td, 'rate_economy_20261231.json'), 'w') as f:
    f.write('{corrupted')  # 更新但损坏→跳过
rows2, src2 = re_mod._load_cached_futures(data_dir=td)
check("损坏文件跳过仍选有效缓存", rows2 == CACHE_ROWS and src2 == fresh)

td2 = tempfile.mkdtemp()
_write_rate_to = None
with open(os.path.join(td2, f'rate_economy_{stale}.json'), 'w') as f:
    json.dump({'date': stale, 'fed_funds_futures': CACHE_ROWS}, f)
rows3, src3 = re_mod._load_cached_futures(data_dir=td2)
check("全部过期→(None,None)不兜底", rows3 is None and src3 is None)
shutil.rmtree(td); shutil.rmtree(td2)

# ══ [4] fact_engine曲线字段映射 ════════════════════════════════
print("\n[4] 曲线label/implied_rate_pct映射(修复恒None)")

data_new = {'date': '20261020', 'fed_funds_futures': [
    {'ticker': 'ZQ=F', 'label': '近月(活跃月)', 'price': 95.5,
     'implied_rate_pct': 4.5, 'date': '2026-10-20', 'source': 'yfinance'}]}
facts, recon = fe.normalize_rate(data_new, '2026-10-21T00:00:00')
curve = recon['fed_futures_curve']
check("新键映射: name=近月(活跃月)", curve and curve[0]['name'] == '近月(活跃月)',
      f"curve={curve}")
check("新键映射: implied_avg_rate=4.5", curve and curve[0]['implied_avg_rate'] == 4.5)
check("ZQ_F1_PRICE事实成立", any(f.get('metric_id') == 'ZQ_F1_PRICE' and f.get('value') == 95.5
                              for f in facts))
check("source透传到曲线(缓存标记可追溯)", curve and curve[0].get('source') == 'yfinance')

data_old = {'date': '20261020', 'fed_funds_futures': [
    {'ticker': 'ZQ=F', 'name': 'FF期货主力', 'price': 95.8, 'implied_rate': 4.2}]}
_, recon_old = fe.normalize_rate(data_old, '2026-10-21T00:00:00')
check("旧fixture键名兼容(name/implied_rate)",
      recon_old['fed_futures_curve'][0]['name'] == 'FF期货主力'
      and recon_old['fed_futures_curve'][0]['implied_avg_rate'] == 4.2)

# ══ [5] Gate A退出码(真实数据,只读live data,写临时目录) ════════
print("\n[5] Gate A FAIL→退出码2(子进程,真实数据)")

LIVE = os.path.join(os.path.expanduser('~'), 'AI内容',
                    '🤖_AI投资项目', '每周宏观追踪', 'investment-agent', 'data', 'daily')
if os.path.isdir(LIVE):
    def _build(date_ymd):
        out = tempfile.mkdtemp()
        r = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'snapshot_builder.py'),
                            '--date', date_ymd, '--data-dir', LIVE, '--out-dir', out],
                           capture_output=True, text=True, timeout=120)
        return r, out

    # 20261017: 验收日,真实PASS快照 → 应退出0
    r_pass, out_pass = _build('20261017')
    check("PASS日(20261017)→退出码0", r_pass.returncode == 0,
          f"rc={r_pass.returncode}, tail={r_pass.stdout.strip().splitlines()[-1] if r_pass.stdout else r_pass.stderr[-200:]}")
    check("PASS日快照写盘", any(f.startswith('research_snapshot_20261017') for f in os.listdir(out_pass)))
    shutil.rmtree(out_pass)

    # 20261020: 真实FAIL日(NFP+ZQ缺失) → 应退出2且快照仍写盘
    r_fail, out_fail = _build('20261020')
    check("FAIL日(20261020)→退出码2", r_fail.returncode == 2, f"rc={r_fail.returncode}")
    check("FAIL日快照仍写盘(失败可追溯)", any(f.startswith('research_snapshot_20261020') for f in os.listdir(out_fail)))
    check("FAIL日stderr/stdout含core_missing披露", 'core_missing' in (r_fail.stdout + r_fail.stderr))
    shutil.rmtree(out_fail)
else:
    print("  ⏭️ live数据目录不存在,子进程退出码用例跳过(在live端复验)")

print("\n" + "=" * 60)
print(f"结果: {PASS}通过 / {FAIL}失败")
print("=" * 60)
sys.exit(0 if FAIL == 0 else 1)
