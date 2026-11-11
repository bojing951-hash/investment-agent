#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R10(autonomous-rd 2026-11-12): tushare 月度宏观跨进程响应缓存验收套件。

背景(RESUME 2②/P2 台账"R10 候选"登记;docs/autonomous-rd/RESUME.md):
  tushare cn_cpi/cn_ppi 同 api 1 次/分限流。午夜窗自采与流水线=两个独立
  进程,同分钟各拉一次→第二次必限流拒→cpi_yoy/ppi_yoy 假性缺席→Gate A
  误拒(生产 07:00 单跑不受影响)。_index_daily 闸门是进程内单调钟,护不到
  跨进程——R10 加文件级响应缓存(仅同窗去重,不做陈旧回退;直连失败仍
  如实缺席,禁 0 填充纪律不变)。

被测对象: scripts/china_market_collector.py R10 增量
  (TUSHARE_MONTHLY_CACHE_* 常量/_monthly_cache_path/_cache_load_rows/
   _cache_save_rows + fetch_macro cn_cpi/cn_ppi 段接线)。

数据纪律: 全部离线合成 fixture(值发明,结构镜像 tushare 接口真实列锚
  month='YYYYMM'+nt_yoy/ppi_yoy;同 test_p1_wp_e R6-D1 源锚)。零网络零
  skip;预期值字面量硬编码(禁自证恒真);缓存一律指向一次性临时目录,
  不读写真实 data/cache(测试密闭,R5 教训)。

锁清单:
[1] 纯函数面: 路径白名单/TTL 边界(含龄=ttl 命中与钟偏未来拒)/坏档六态
    逐态 None/save→load 序列化保真(NaN→null 可逆,缓存路与直路同判)
    /save 失败透明 False/load 目录路径透明 None
[2] fetch_macro 集成面: 首拉直连+写缓存/同窗二拉零直连(=本修目标场景,
    第二个 pro 桩 call_count==0)/超龄缓存→直连重拉+缓存翻新/直连失败
    不回退陈旧缓存(诚实缺席纪律)/列漂移响应不入缓存/两 api 缓存互不串
[3] 契约面: TTL 常量锁(600s)/默认缓存目录锁(data/cache)
"""
import contextlib
import io
import json
import os
import sys
import tempfile
import time
import types
from contextlib import redirect_stdout
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

PASS, FAIL = 0, 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")


# CI 无 akshare 面: 无条件注入确定性 fake(test_p1_wp_e 同款先例)
_ak_fake = types.ModuleType('akshare')
for _fn in ('macro_china_lpr', 'macro_china_pmi',
            'macro_china_new_financial_credit'):
    setattr(_ak_fake, _fn, mock.MagicMock(name=_fn))
sys.modules['akshare'] = _ak_fake

import china_market_collector as cmc      # noqa: E402

# ── 合成 fixture(值发明;列锚=tushare cn_cpi.nt_yoy/cn_ppi.ppi_yoy 真实形态) ──
CPI_DF = pd.DataFrame({'month': ['202609', '202610', '202608'],
                       'nt_yoy': [0.9, None, 0.6]})          # 202610 未发布→跳
PPI_DF = pd.DataFrame({'month': ['202609', '202608'],
                       'ppi_yoy': [-2.8, -3.0]})
CPI_EXPECT = {'date': '2026-09-30', 'value': 0.9, 'source': 'tushare_pro'}
PPI_EXPECT = {'date': '2026-09-30', 'value': -2.8, 'source': 'tushare_pro'}


def _new_cache_dir():
    return tempfile.mkdtemp(prefix='r10_cache_')


def run_fetch_macro(cpi=CPI_DF, ppi=PPI_DF, cache_dir=None):
    """打桩跑一次 fetch_macro(焦点=cpi/ppi 两键;其余端点恒败→缺席不扰)。
    cpi/pii=None→该 api 桩恒抛(直连失败注入);cpi='ABSENT'→api 属性删除。
    返回 (out_dict, pro_mock, stdout_str)。"""
    cache_dir = cache_dir or _new_cache_dir()
    pro = mock.MagicMock(name='pro_client')
    for name, val in (('cn_cpi', cpi), ('cn_ppi', ppi)):
        if val is None:
            getattr(pro, name).side_effect = OSError('synthetic rate-limit')
        else:
            getattr(pro, name).return_value = val
    ak = sys.modules['akshare']
    out_io = io.StringIO()
    with contextlib.ExitStack() as st:
        for p in (mock.patch.object(ak, 'macro_china_lpr',
                                    side_effect=OSError('synthetic')),
                  mock.patch.object(ak, 'macro_china_pmi',
                                    side_effect=OSError('synthetic')),
                  mock.patch.object(ak, 'macro_china_new_financial_credit',
                                    side_effect=OSError('synthetic')),
                  mock.patch.object(cmc, '_pro', return_value=pro),
                  mock.patch.object(cmc, '_shrzgm_rows', return_value=None),
                  mock.patch.object(cmc, 'TUSHARE_MONTHLY_CACHE_DIR', cache_dir)):
            st.enter_context(p)
        with redirect_stdout(out_io):
            out = cmc.fetch_macro()
    return out, pro, out_io.getvalue()


# ═══════════════════════════════════════════════════════════════════
print("═" * 60)
print("[1] 纯函数面(路径白名单/TTL 边界/坏档/序列化保真/失败透明)")
print("═" * 60)

# t100 路径白名单: 现役两面合法+落在缓存目录;外来名拒(防路径注入)
with mock.patch.object(cmc, 'TUSHARE_MONTHLY_CACHE_DIR', '/tmp/r10dir'):
    check("t100a cn_cpi 路径",
          cmc._monthly_cache_path('cn_cpi')
          == '/tmp/r10dir/tushare_monthly_cn_cpi.json')
    check("t100b cn_ppi 路径",
          cmc._monthly_cache_path('cn_ppi')
          == '/tmp/r10dir/tushare_monthly_cn_ppi.json')
    for bad in ('cn_gdp', 'evil/../../etc/passwd', ''):
        try:
            cmc._monthly_cache_path(bad)
            check(f"t100c 拒 {bad!r}", False, '未抛 ValueError')
        except ValueError:
            check(f"t100c 拒 {bad!r}", True)

# t101 save→load 新鲜命中 + TTL 边界(含龄=ttl 命中/超 1 秒拒/钟偏未来拒)
d = _new_cache_dir()
p = os.path.join(d, 'tushare_monthly_cn_cpi.json')
check("t101a 写入成功", cmc._cache_save_rows(p, CPI_DF, 1000.0) is True,
      str(os.path.exists(p)))
rows = cmc._cache_load_rows(p, 1000.0 + 599)
check("t101b 龄 599s 命中", rows is not None)
check("t101c 龄=ttl(600s) 命中(闭界)", cmc._cache_load_rows(p, 1600.0) is not None)
check("t101d 龄=ttl+1(601s) 拒", cmc._cache_load_rows(p, 1601.0) is None)
check("t101e 钟偏未来(now<fetched) 拒", cmc._cache_load_rows(p, 999.0) is None)

# t102 坏档六态逐态 None(缺档/坏 JSON/rows 空/rows 非 list/fetched_at 坏/
#      路径是目录)——零异常外泄
d2 = _new_cache_dir()
check("t102a 缺档→None", cmc._cache_load_rows(os.path.join(d2, 'nope.json'),
                                               time.time()) is None)
bad_json = os.path.join(d2, 'bad.json')
with open(bad_json, 'w') as f:
    f.write('{not-json')
check("t102b 坏 JSON→None", cmc._cache_load_rows(bad_json, time.time()) is None)
now = time.time()
for name, obj in (('rows 空', {'rows': [], 'fetched_at': now}),
                  ('rows 非 list', {'rows': 'x', 'fetched_at': now}),
                  ('fetched_at 坏', {'rows': [{'month': '202609'}],
                                     'fetched_at': 'abc'})):
    fp = os.path.join(d2, 'm_%s.json' % abs(hash(name)))
    with open(fp, 'w') as f:
        json.dump(obj, f)
    check(f"t102c {name}→None", cmc._cache_load_rows(fp, now) is None)
dirp = os.path.join(d2, 'adir')
os.makedirs(dirp, exist_ok=True)
check("t102d 路径是目录→None", cmc._cache_load_rows(dirp, now) is None)

# t103 序列化保真: NaN→null 落盘,缓存路与直路对同一 df 同判(值=硬编码)
d3 = _new_cache_dir()
p3 = os.path.join(d3, 'tushare_monthly_cn_cpi.json')
cmc._cache_save_rows(p3, CPI_DF, now)
with open(p3, encoding='utf-8') as f:
    raw = f.read()
obj = json.loads(raw)
check("t103a NaN 行落盘为 null(档内零裸 NaN,JSON 严格)",
      'NaN' not in raw and 'Infinity' not in raw
      and all(r['nt_yoy'] is None or isinstance(r['nt_yoy'], float)
              for r in obj['rows'])
      and obj['rows'][1]['nt_yoy'] is None)      # 202610 未发布行=None
got = cmc._cache_load_rows(p3, now + 1)
check("t103b 缓存路选行=直路选行=硬编码",
      got is not None
      and cmc._tushare_monthly_last(
          pd.DataFrame(got, columns=['month', 'nt_yoy']), 'nt_yoy')
      == ('2026-09-30', 0.9)
      and cmc._tushare_monthly_last(CPI_DF, 'nt_yoy') == ('2026-09-30', 0.9))

# t104 save 失败透明: 父路径是既有文件(makedirs 必败)→False 不上抛
d4 = _new_cache_dir()
blocker = os.path.join(d4, 'blocker')
with open(blocker, 'w') as f:
    f.write('x')
try:
    r = cmc._cache_save_rows(os.path.join(blocker, 'sub', 'c.json'),
                             CPI_DF, now)
    check("t104 父路径为文件→False 不上抛", r is False)
except Exception as e:
    check("t104 父路径为文件→False 不上抛", False, repr(e))

# ═══════════════════════════════════════════════════════════════════
print("═" * 60)
print("[2] fetch_macro 集成面(缓存去重=本修目标场景)")
print("═" * 60)

# t110 首拉: 直连各恰一次+写缓存+两键恰等(其余端点恒败→恰两键)
dA = _new_cache_dir()
out1, pro1, so1 = run_fetch_macro(cache_dir=dA)
check("t110a 产出恰两键", set(out1) == {'cpi_yoy', 'ppi_yoy'}, str(set(out1)))
check("t110b cpi_yoy 恰等", out1.get('cpi_yoy') == CPI_EXPECT, str(out1.get('cpi_yoy')))
check("t110c ppi_yoy 恰等", out1.get('ppi_yoy') == PPI_EXPECT, str(out1.get('ppi_yoy')))
check("t110d 直连各恰一次",
      pro1.cn_cpi.call_count == 1 and pro1.cn_ppi.call_count == 1,
      f"cpi={pro1.cn_cpi.call_count} ppi={pro1.cn_ppi.call_count}")
check("t110e 两 api 缓存档已写",
      os.path.exists(os.path.join(dA, 'tushare_monthly_cn_cpi.json'))
      and os.path.exists(os.path.join(dA, 'tushare_monthly_cn_ppi.json')))
check("t110f 首拉无 ♻️ 披露", '♻️' not in so1)

# t111 同窗二拉(=午夜窗双进程场景,同一缓存目录=跨进程文件通道):
#     第二拉零直连(限流免耗),产出与首拉逐字段一致,♻️ 披露在场
out2, pro2, so2 = run_fetch_macro(cache_dir=dA)
check("t111a 二拉零直连",
      pro2.cn_cpi.call_count == 0 and pro2.cn_ppi.call_count == 0,
      f"cpi={pro2.cn_cpi.call_count} ppi={pro2.cn_ppi.call_count}")
check("t111b 二拉 cpi_yoy 与首拉逐字段一致",
      out2.get('cpi_yoy') == out1['cpi_yoy'], str(out2.get('cpi_yoy')))
check("t111c 二拉 ppi_yoy 与首拉逐字段一致",
      out2.get('ppi_yoy') == out1['ppi_yoy'], str(out2.get('ppi_yoy')))
check("t111d 二拉 ♻️ 披露在场", '♻️' in so2)

# t112 超龄缓存(601s)→直连重拉一次+缓存翻新(再读=新鲜命中)
dB = _new_cache_dir()
pB = os.path.join(dB, 'tushare_monthly_cn_ppi.json')
cmc._cache_save_rows(pB, PPI_DF, time.time() - 601)
outB, proB, _ = run_fetch_macro(cache_dir=dB)
check("t112a 超龄→直连重拉恰一次", proB.cn_ppi.call_count == 1,
      str(proB.cn_ppi.call_count))
check("t112b 超龄重拉值恰等", outB.get('ppi_yoy') == PPI_EXPECT)
check("t112c 缓存已翻新(再读新鲜命中)",
      cmc._cache_load_rows(pB, time.time() + 1) is not None)

# t113 直连失败不回退陈旧缓存(诚实缺席纪律): 陈旧档(3600s)在场+直连抛→
#     该键缺席(不拿旧值冒充今日),其余键不受影响
dC = _new_cache_dir()
pC = os.path.join(dC, 'tushare_monthly_cn_cpi.json')
cmc._cache_save_rows(pC, CPI_DF, time.time() - 3600)
outC, proC, soC = run_fetch_macro(cpi=None, cache_dir=dC)   # cn_cpi 桩恒抛
check("t113a 直连失败+陈旧档在场→cpi_yoy 缺席", 'cpi_yoy' not in outC,
      str(outC.get('cpi_yoy')))
check("t113b 同程 ppi_yoy 不受影响", outC.get('ppi_yoy') == PPI_EXPECT)
check("t113c 失败披露在场", '❌' in soC)

# t114 不可解析响应不入缓存(列漂移 df 无 nt_yoy→键缺席且零缓存档)
dD = _new_cache_dir()
outD, proD, _ = run_fetch_macro(cpi=CPI_DF.drop(columns=['nt_yoy']),
                                cache_dir=dD)
check("t114a 列漂移→cpi_yoy 缺席", 'cpi_yoy' not in outD)
check("t114b 列漂移响应未入缓存",
      not os.path.exists(os.path.join(dD, 'tushare_monthly_cn_cpi.json')))

# t115 两 api 缓存互不串: 仅 cn_cpi 新鲜档在场→cpi 走缓存(零直连),
#     ppi 无档→直连恰一次
dE = _new_cache_dir()
cmc._cache_save_rows(os.path.join(dE, 'tushare_monthly_cn_cpi.json'),
                     CPI_DF, time.time())
outE, proE, _ = run_fetch_macro(cache_dir=dE)
check("t115a cpi 缓存命中零直连", proE.cn_cpi.call_count == 0,
      str(proE.cn_cpi.call_count))
check("t115b ppi 无档直连恰一次", proE.cn_ppi.call_count == 1,
      str(proE.cn_ppi.call_count))
check("t115c 两键值均恰等",
      outE.get('cpi_yoy') == CPI_EXPECT and outE.get('ppi_yoy') == PPI_EXPECT)

# ═══════════════════════════════════════════════════════════════════
print("═" * 60)
print("[3] 契约面(常量锁)")
print("═" * 60)

check("t120 TTL 常量=600s(同窗去重窗,月度数据远小于发布周期)",
      cmc.TUSHARE_MONTHLY_CACHE_TTL_SECONDS == 600,
      str(cmc.TUSHARE_MONTHLY_CACHE_TTL_SECONDS))
check("t121 默认缓存目录=data/cache(仓库 data/ 面,gitignored)",
      cmc.TUSHARE_MONTHLY_CACHE_DIR
      == os.path.join(cmc.DATA_DIR, 'cache'),
      cmc.TUSHARE_MONTHLY_CACHE_DIR)

# ═══════════════════════════════════════════════════════════════════
print("═" * 60)
total = PASS + FAIL
print(f"RESULT: {PASS} PASS / {FAIL} FAIL (total {total})")
sys.exit(0 if FAIL == 0 else 1)
