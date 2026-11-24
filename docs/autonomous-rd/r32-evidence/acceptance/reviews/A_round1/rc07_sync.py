# -*- coding: utf-8 -*-
"""rc07: 历史段同步面表(MAP_REPORT 三段)逐格直算 + 当时可知面/事后段取值 + GDP 发布规则敏感性。
用法: /usr/bin/python3 -I rc07_sync.py <snapshot.json> <release_calendar.json>
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
import rc_points as P

snap = L.load(sys.argv[1]); cal = L.load(sys.argv[2])
F = L.Face(snap, cal)
SEC = '⑧同步面/当时可知'

# (维度, 地区, 指标, 锚-3月观测, 锚-3月值, 截止观测, 截止值, 变化文本, 标签)
T = {
 '2025-03': [
  ('增长', 'US', 'US_REAL_GDP', '2024-07-01', 2.9479, '2024-10-01', 2.6419, -0.306, '基准'),
  ('通胀', 'US', 'CPI', '2024-11', 2.7195, '2025-02', 2.8016, 0.0821, '基准'),
  ('政策', 'US', 'DFEDTARU', '2024-12-31', 4.5, '2025-03-31', 4.5, 0.0, '基准'),
  ('增长', 'CN', 'CN_PMI_MFG', '2024-12', 50.1, '2025-03', 50.5, 0.4, '分化'),
  ('通胀', 'CN', 'CN_CPI_YOY', '2024-11', 0.2, '2025-02', -0.7, -0.9, '分化'),
  ('政策', 'CN', 'CN_LPR_1Y', '2024-12-20', 3.1, '2025-03-20', 3.1, 0.0, '同步'),
  ('增长', 'EA', 'EA_REAL_GDP_YOY', '2024-07-01', 1.31, '2024-10-01', 1.56, 0.25, '分化'),
  ('通胀', 'EA', 'EA_HICP_YOY', '2024-12', 2.4, '2025-02', 2.3, -0.1, '分化'),
  ('政策', 'EA', 'ECB_MRO', '2024-12-18', 3.15, '2025-03-12', 2.65, -0.5, '分化'),
  ('增长', 'JP', 'JP_REAL_GDP_YOY', '2024-07-01', 1.11, '2024-10-01', 1.01, -0.1, '同步'),
  ('通胀', 'JP', 'JP_CPI_YOY', '2024-11', 2.92, '2025-02', 3.66, 0.74, '同步'),
  ('政策', 'JP', 'JP_POLICY_RATE', '2024-11', 0.227, '2025-02', 0.478, 0.251, '分化')],
 '2022-06': [
  ('增长', 'US', 'US_REAL_GDP', '2021-10-01', 5.8182, '2022-01-01', 3.9754, -1.8428, '基准'),
  ('通胀', 'US', 'CPI', '2022-02', 7.9373, '2022-05', 8.5382, 0.6009, '基准'),
  ('政策', 'US', 'DFEDTARU', '2022-03-31', 0.5, '2022-06-30', 1.75, 1.25, '基准'),
  ('增长', 'CN', 'CN_PMI_MFG', '2022-03', 49.5, '2022-06', 50.2, 0.7, '分化'),
  ('通胀', 'CN', 'CN_CPI_YOY', '2022-02', 0.9, '2022-05', 2.1, 1.2, '同步'),
  ('政策', 'CN', 'CN_LPR_1Y', '2022-03-21', 3.7, '2022-06-20', 3.7, 0.0, '分化'),
  ('增长', 'EA', 'EA_REAL_GDP_YOY', '2021-10-01', 5.68, '2022-01-01', 5.58, -0.1, '同步'),
  ('通胀', 'EA', 'EA_HICP_YOY', '2022-03', 7.4, '2022-05', 8.1, 0.7, '同步'),
  ('政策', 'EA', 'ECB_MRO', '2019-09-18', 0.0, '2019-09-18', 0.0, 0.0, '分化'),
  ('增长', 'JP', 'JP_REAL_GDP_YOY', '2021-10-01', 2.8, '2022-01-01', 1.15, -1.65, '同步'),
  ('通胀', 'JP', 'JP_CPI_YOY', '2022-02', 0.95, '2022-05', 2.46, 1.51, '同步'),
  ('政策', 'JP', 'JP_POLICY_RATE', '2022-02', -0.018, '2022-05', -0.018, 0.0, '分化')],
 '2023-10': [
  ('增长', 'US', 'US_REAL_GDP', '2023-04-01', 2.736, '2023-07-01', 3.1839, 0.4479, '基准'),
  ('通胀', 'US', 'CPI', '2023-06', 3.0706, '2023-09', 3.6872, 0.6166, '基准'),
  ('政策', 'US', 'DFEDTARU', '2023-07-31', 5.5, '2023-10-31', 5.5, 0.0, '基准'),
  ('增长', 'CN', 'CN_PMI_MFG', '2023-07', 49.3, '2023-10', 49.5, 0.2, '同步'),
  ('通胀', 'CN', 'CN_CPI_YOY', '2023-06', 0.0, '2023-09', 0.0, 0.0, '分化'),
  ('政策', 'CN', 'CN_LPR_1Y', '2023-07-20', 3.55, '2023-10-20', 3.45, -0.1, '分化'),
  ('增长', 'EA', 'EA_REAL_GDP_YOY', '2023-01-01', 1.22, '2023-04-01', 0.48, -0.74, '分化'),
  ('通胀', 'EA', 'EA_HICP_YOY', '2023-07', 5.3, '2023-10', 2.9, -2.4, '分化'),
  ('政策', 'EA', 'ECB_MRO', '2023-06-21', 4.0, '2023-09-20', 4.5, 0.5, '分化'),
  ('增长', 'JP', 'JP_REAL_GDP_YOY', '2023-01-01', 2.06, '2023-04-01', 1.17, -0.89, '分化'),
  ('通胀', 'JP', 'JP_CPI_YOY', '2023-06', 3.3, '2023-09', 3.05, -0.25, '分化'),
  ('政策', 'JP', 'JP_POLICY_RATE', '2023-06', -0.066, '2023-09', -0.054, 0.012, '分化')],
}
JUDG = {'2025-03': {'sync': 3, 'text': '增长维: 日本同步、中国分化与欧元区分化；通胀维: 日本同步、中国分化与欧元区分化；政策维: 中国同步(双持平)、欧元区分化与日本分化'},
        '2022-06': {'sync': 5, 'text': '增长维: 欧元区同步、日本同步、中国分化；通胀维: 三地均同步；政策维: 三地均分化，美国上行一百二十五个基点、三地持平'},
        '2023-10': {'sync': 1, 'text': '增长维: 中国同步、欧元区分化与日本分化；通胀维: 三地均分化；政策维: 三地均分化'}}
GDP_LAG = {'US_REAL_GDP': 29, 'EA_REAL_GDP_YOY': 35, 'JP_REAL_GDP_YOY': 45}   # 注册表/点值格口径


def get(m, d):
    if len(d) == 7:
        return F.monthly(m).get(d)
    return F.at(m, d)


def gdp_yoy(m, obs):
    y, mo = int(obs[:4]), int(obs[5:7])
    q = (mo - 1) // 3 + 1
    return L.qyoy_level(F, m, '%04dQ%d' % (y, q))


def knowable_gdp(m, asof):
    """注册表发布规则(季后 N 天)下 asof 当日可见的最新季度 -> (obs_date, value_or_yoy, pub)"""
    best = None
    for d, v in F.series(m):
        if d > asof:
            break
        qend_m = ((int(d[5:7]) - 1) // 3 + 1) * 3
        pub = L.shift_days(L.month_end('%04d-%02d' % (int(d[:4]), qend_m)), GDP_LAG[m])
        if pub <= asof:
            best = (d, v, pub)
    return best


for cand, rows in T.items():
    print('=====', cand)
    nsync = 0
    us_dir = {}
    bydim = {}
    for dim, rg, m, d0, v0, d1, v1, chg, lab in rows:
        a = get(m, d0); b = get(m, d1)
        if m == 'US_REAL_GDP':
            a = gdp_yoy(m, d0)[0]; b = gdp_yoy(m, d1)[0]
        if m == 'CPI':
            a = L.yoy_level(F, m, d0)[0]; b = L.yoy_level(F, m, d1)[0]
        okv = P.eq(a, v0) and P.eq(b, v1)
        c = (b - a)
        # 引擎表内变化=按显示精度舍入后的两端相减; 两种算法任一吻合即记一致
        def dec(x):
            sx = repr(x)
            return len(sx.split('.')[1]) if '.' in sx else 0
        c_disp = round(round(b, dec(v1)) - round(a, dec(v0)), 6)
        okc = P.eq(c, chg) or P.eq(c_disp, chg)
        d = 'up' if c > 1e-9 else ('down' if c < -1e-9 else 'flat')
        okl = True
        if rg == 'US':
            us_dir[dim] = d
        else:
            exp = '同步' if d == us_dir[dim] else '分化'
            if d == 'flat' and us_dir[dim] == 'flat':
                exp = '同步'
            okl = (exp == lab)
            nsync += (lab == '同步')
            bydim.setdefault(dim, []).append((rg, exp))
        P.add(SEC, 'snapshot.series_store.%s @%s 与 @%s' % (m, d0, d1),
              {'v0': a, 'v1': b, 'chg': round(c, 4), 'dir': d}, {'v0': v0, 'v1': v1, 'chg': chg, 'label': lab},
              bool(okv and okc and okl), where='MAP_REPORT 历史段 %s 地区×维度同步面表(%s/%s)' % (cand, dim, rg))
        print(dim, rg, m, a, b, round(c, 4), d, lab, 'OK' if (okv and okc and okl) else 'MISMATCH')
    print('同步格数', nsync, '受审', JUDG[cand]['sync'], bydim)
    P.add(SEC, '同步面表同步格计数(由上 9 格标签直算)', nsync, JUDG[cand]['sync'], nsync == JUDG[cand]['sync'],
          where='agent_judgment.history_periods[%s].other_regions_sync' % cand)
    # GDP 行发布规则敏感性
    cut = L.month_end(cand)
    cut0 = L.month_end(L.add_months(cand, -3))
    for m in ('US_REAL_GDP', 'EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY'):
        k0 = knowable_gdp(m, cut0); k1 = knowable_gdp(m, cut)
        f0 = gdp_yoy(m, k0[0])[0] if m == 'US_REAL_GDP' else k0[1]
        f1 = gdp_yoy(m, k1[0])[0] if m == 'US_REAL_GDP' else k1[1]
        print('  注册表规则可见最新季度', m, '锚-3月(%s):' % cut0, k0, 'yoy %.4f' % f0, '| 截止(%s):' % cut, k1, 'yoy %.4f' % f1,
              'dir', 'up' if f1 > f0 + 1e-9 else ('down' if f1 < f0 - 1e-9 else 'flat'))

# ---------- 当时可知面(截止月可见) ----------
print('===== 当时可知面与事后段')
KNOWN = {
 '2025-03': [('CPI', '2025-02', 319.679, '2025-03-13'), ('CORE_PCE', '2025-02', 125.002, '2025-03-30'), ('INDPRO', '2025-02', 101.099, '2025-03-15'),
             ('UNEMPLOYMENT', '2025-02', 4.2, '2025-03-05'), ('US_REAL_GDP', '2024-10-01', 23641.8, '2025-01-29'), ('CN_PPI_YOY', '2025-02', -2.2, '2025-03-09'),
             ('CN_CPI_YOY', '2025-02', -0.7, '2025-03-09'), ('EA_HICP_YOY', '2025-02', 2.3, '2025-02-28'), ('JP_CPI_YOY', '2025-02', 3.66, '2025-03-20')],
 '2022-06': [('CPI', '2022-05', 291.298, '2022-06-13'), ('CORE_PCE', '2022-05', 113.571, '2022-06-30'), ('INDPRO', '2022-05', 101.334, '2022-06-15'),
             ('UNEMPLOYMENT', '2022-05', 3.6, '2022-06-05'), ('US_REAL_GDP', '2022-01-01', 21945.7, '2022-04-29'), ('CN_PPI_YOY', '2022-05', 6.4, '2022-06-09'),
             ('CN_CPI_YOY', '2022-05', 2.1, '2022-06-09'), ('EA_HICP_YOY', '2022-05', 8.1, '2022-05-31'), ('JP_CPI_YOY', '2022-05', 2.46, '2022-06-20')],
 '2023-10': [('CPI', '2023-09', 307.276, '2023-10-13'), ('CORE_PCE', '2023-09', 120.053, '2023-10-30'), ('INDPRO', '2023-09', 101.021, '2023-10-15'),
             ('UNEMPLOYMENT', '2023-09', 3.7, '2023-10-05'), ('US_REAL_GDP', '2023-07-01', 22828.8, '2023-10-29'), ('CN_PPI_YOY', '2023-09', -2.5, '2023-10-09'),
             ('CN_CPI_YOY', '2023-09', 0.0, '2023-10-09'), ('EA_HICP_YOY', '2023-10', 2.9, '2023-10-31'), ('JP_CPI_YOY', '2023-09', 3.05, '2023-10-20')],
}
for cand, rows in KNOWN.items():
    cut = L.month_end(cand)
    for m, ym, val, pub in rows:
        v = F.at(m, ym + '-01') if len(ym) == 7 else F.at(m, ym)
        ok = P.eq(v, val)
        # 值确为截止月前可见的最新观测?(按注册表规则直算: HICP 用快报月末)
        od = ym + '-01' if len(ym) == 7 else ym
        if m == 'EA_HICP_YOY':
            pv = L.month_end(ym)
        else:
            pv = L.release_date(F, m, od)[0]
        P.add(SEC, 'snapshot.series_store.%s@%s(当时可知面; 规则发布日 %s)' % (m, ym, pv), v, val, ok,
              where='MAP_REPORT 历史段 %s 当时可知面表' % cand)
        print(cand, m, ym, v, 'vs', val, 'pub(表)', pub, 'pub(规则)', pv, 'OK' if ok else 'MISMATCH')

# ---------- 事后段取值 ----------
EX = [('CPI', '2025-03', 319.785, '2025-04-13'), ('CPI', '2025-11', 325.063, '2025-12-18'), ('CORE_PCE', '2025-03', 125.144, '2025-04-30'),
      ('CORE_PCE', '2025-10', 127.165, '2026-01-22'), ('INDPRO', '2025-03', 101.04, '2025-04-15'), ('INDPRO', '2025-09', 101.668, '2025-12-03'),
      ('UNEMPLOYMENT', '2025-03', 4.2, '2025-04-05'), ('UNEMPLOYMENT', '2025-09', 4.4, '2025-11-20'), ('UNEMPLOYMENT', '2025-11', 4.5, '2025-12-16'),
      ('US_REAL_GDP', '2025-07', 24113, '2025-12-23'), ('CN_PPI_YOY', '2025-03', -2.5, '2025-04-09'), ('CN_CPI_YOY', '2025-03', -0.1, '2025-04-09'),
      ('EA_HICP_YOY', '2025-03', 2.2, '2025-04-01'), ('JP_CPI_YOY', '2025-03', 3.62, '2025-04-20'),
      ('CPI', '2022-06', 294.957, '2022-07-13'), ('CORE_PCE', '2022-06', 114.273, '2022-07-30'), ('INDPRO', '2022-06', 101.018, '2022-07-15'),
      ('UNEMPLOYMENT', '2022-06', 3.6, '2022-07-05'), ('CN_PPI_YOY', '2022-06', 6.1, '2022-07-09'), ('CN_CPI_YOY', '2022-06', 2.5, '2022-07-09'),
      ('EA_HICP_YOY', '2022-06', 8.6, '2022-07-01'), ('JP_CPI_YOY', '2022-06', 2.35, '2022-07-20'),
      ('CPI', '2023-10', 307.696, '2023-11-13'), ('CORE_PCE', '2023-10', 120.321, '2023-11-30'), ('INDPRO', '2023-10', 100.469, '2023-11-15'),
      ('UNEMPLOYMENT', '2023-10', 3.9, '2023-11-05'), ('US_REAL_GDP', '2023-10', 23033.2, '2024-01-29'), ('CN_PPI_YOY', '2023-10', -2.6, '2023-11-09'),
      ('CN_CPI_YOY', '2023-10', -0.2, '2023-11-09'), ('JP_CPI_YOY', '2023-10', 3.32, '2023-11-20')]
nbad = 0
for m, ym, val, pub in EX:
    v = F.at(m, ym + '-01')
    pv = L.release_date(F, m, ym + '-01')[0]
    ok = P.eq(v, val) and (pv == pub)
    nbad += (not ok)
    P.add(SEC, 'snapshot.series_store.%s@%s + 发布规则/日历(直算发布日 %s)' % (m, ym, pv), {'value': v, 'pub': pv}, {'value': val, 'pub': pub}, ok,
          where='MAP_REPORT 历史段事后段表')
    if not ok:
        print('EX', m, ym, v, val, pv, pub)
print('事后段条目', len(EX), '偏离', nbad)
# 缺席: CPI 2025-10 / UNEMPLOYMENT 2025-10
for m in ('CPI', 'UNEMPLOYMENT'):
    a = F.at(m, '2025-10-01')
    P.add(SEC, 'snapshot.series_store.%s@2025-10(事后段表记"数据不可得")' % m, a, None, a is None, where='MAP_REPORT 2025-03 事后段表')
    print(m, '2025-10 obs =', a)
print('tally', P.tally())
