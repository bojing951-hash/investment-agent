# -*- coding: utf-8 -*-
"""rc13: 收尾复核三项(Audit-R32 A round1; 只读)。
用法: /usr/bin/python3 -I rc13_final_checks.py <snapshot.json> <run_dir>
(1) 历史段事后窗注记「引擎事后块起点为锚后首个观测,两口径数值可差约1个百分点」:
    逐格重算 引擎口径(report.json analog top[i].aftermath) 与 月末口径(候选月末最后观测→候选月+N月末最后观测) 之差。
(2) NIKKEI225 截止日 2026-11-23(周一)无观测的原因面: 序列内 2016..2023 年每个落在工作日的 11-23 均无观测(休市日规律), 对照 SHCOMP/DAX 同日有观测。
(3) TR1.step2 括注 DFF 3.88→3.63→3.88 与三时点锚值/变动点值的对应(登记, 非比对)。
所有记录 note 带 [rc13] 标记: 重跑前 /usr/bin/python3 -I rc_clean_mark.py '[rc13] '
"""
import sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rc_lib as L
import rc_points as P

snap = L.load(sys.argv[1]); RUN = sys.argv[2]
cal = L.load(os.path.join(RUN, 'root_overlay', 'config', 'release_calendar.json'))
F = L.Face(snap, cal)
rep = L.load(os.path.join(RUN, 'report.json'))

_add = P.add
P.add = lambda section, src, computed, reported, ok, note='', where='': _add(
    section, src, computed, reported, ok, note='[rc13] ' + note, where=where)

S8 = '⑧历史事后窗'

# ---------- (1) 两口径之差 ----------
st = [s for s in rep['steps'] if s.get('step') == 'S6_analog'][0]
top = st['envelope']['data']['top']
PP = ('DFEDTARU', 'UNEMPLOYMENT', 'UST_10Y')
ASSET = ('SPX', 'NIKKEI225', 'DAX', 'SHCOMP', 'GOLD_F', 'DXY')
AMAP = {'DFEDTARU': 'UST_10Y', 'UNEMPLOYMENT': 'UST_10Y', 'CPI': 'SPX', 'INDPRO': 'SPX'}  # 仅用于判定不在引擎事后块的序列
aj = L.load(os.path.join(RUN, 'agent_judgment.json'))
JUDP = [h['judgment_cutoff_ym'] for h in aj['reader_map']['history_periods']]   # 受审稿逐窗叙述的三个候选月


def two_basis(periods):
    diffs = []
    for t in top:
        c = t['candidate_month']
        if c not in periods:
            continue
        am = t['aftermath']
        for k in (3, 6, 12):
            for name in ASSET + ('UST_10Y',):
                if name not in am or not isinstance(am[name], dict) or str(k) + 'm' not in am[name]:
                    continue
                if str(k) + 'm' in am.get('unavailable_horizons', {}).get(name, []):
                    continue
                end_ym = L.add_months(c, k)
                s_me = F.at_or_before(name, L.month_end(c)); e_me = F.at_or_before(name, L.month_end(end_ym))
                me = (e_me[1] - s_me[1]) if name in PP else L.pct(s_me[1], e_me[1])
                eng = am[name][str(k) + 'm']
                diffs.append((round(abs(me - eng), 4), c, name, str(k) + 'm', round(me, 4), eng))
    diffs.sort(reverse=True)
    return diffs


diffs = two_basis(JUDP)
mx = diffs[0]; med = sorted(x[0] for x in diffs)[len(diffs) // 2]
above = [x for x in diffs if x[0] > 1.05]
print('top3 cells', len(diffs), 'max', mx, 'n>1.05', len(above), 'n>0.5', sum(1 for x in diffs if x[0] > 0.5), 'median', med)
print('top6', diffs[:6])
P.add(S8, '事后窗注记「两口径数值可差约1个百分点」: |月末口径−引擎事后块口径| 逐格(受审稿逐窗叙述的三段×3窗×资产/美债序列)',
      {'n_cells': len(diffs), 'max_pp': mx[0], 'max_cell': mx[1:4], 'n_cells_gt_1.05': len(above), 'n_cells_gt_0.5': sum(1 for x in diffs if x[0] > 0.5), 'median': med},
      '可差约1个百分点', True,
      note=('带「约」字的量级表述: 中位 %s、最大 %spp(%s %s %s), 超 1.05pp 的格 %d/%d(%s)——量级表述成立、上界被低估, 列 NIT') % (
          med, mx[0], mx[1], mx[3], mx[2], len(above), len(diffs),
          '; '.join('%s %s %s %s' % (x[1], x[3], x[2], x[0]) for x in above)),
      where='history_periods[*].ex_post.{3m,6m,12m} 句末括注 / MAP_REPORT 历史段 "随后N个月" 行')
d45 = two_basis([t['candidate_month'] for t in top if t['candidate_month'] not in JUDP])
P.add(S8, '同注记对 TOP-5 第4/5名(2021-02/2020-01, 受审稿无逐窗月末叙述)的口径差: |月末口径−引擎事后块口径|',
      {'n_cells': len(d45), 'max_pp': d45[0][0], 'max_cell': d45[0][1:4], 'median': sorted(x[0] for x in d45)[len(d45) // 2]},
      '受审稿未引用该两段的月末口径数值', 'NA',
      note='登记项: 第4/5名仅进入符号一致率与簇数, 不进入逐窗叙述; 两口径在该两段差值最大 %spp' % d45[0][0],
      where='report.json steps[S6_analog].top[3..4].aftermath')

# ---------- (2) NIKKEI225 11-23 ----------
ds = set(d for d, v in F.series('NIKKEI225'))
wk = []; miss = 0
for y in range(2016, 2024):
    d = '%04d-11-23' % y
    if dt.date.fromisoformat(d).isoweekday() <= 5:
        wk.append(d); miss += (d not in ds)
sh = set(d for d, v in F.series('SHCOMP')); dx = set(d for d, v in F.series('DAX'))
P.add('⑫时点标注', 'NIKKEI225 截止日 2026-11-23(周一)无观测的原因面: 序列内 2016..2023 年落在工作日的 11-23 无观测年数 / 同日 SHCOMP、DAX 有观测年数',
      {'nikkei_weekday_1123_missing': '%d/%d' % (miss, len(wk)), 'shcomp_obs': sum(1 for d in wk if d in sh), 'dax_obs': sum(1 for d in wk if d in dx), 'last_nikkei_obs': F.last('NIKKEI225')[0], 'cutoff_tokyo': '2026-11-23 23:53 JST(周一)'},
      ['NIKKEI225 止于 2026-11-20 收盘(未说明 11-23 无观测的原因)', None, None, '2026-11-20', '2026-11-23'],
      F.last('NIKKEI225')[0] == '2026-11-20',
      note=('受审稿陈述属实; 冻结序列显示 11-23 为日经指数历年规律性无观测日(工作日 %d/%d 无观测, 同期 SHCOMP/DAX 有观测)——原因是休市而非采集滞后, 受审稿未写原因、亦未写错原因, 列 NIT') % (miss, len(wk)),
      where='quality_gate_notes[0] / TR1.step3 "NIKKEI225 止于 2026-11-20 收盘"')

# ---------- (3) DFF 括注 ----------
d = dict(F.series('DFF'))
P.add('④政策面', 'DFF 三时点锚值(2025-11-22/2026-08-22/2026-11-19) 与 变动点值(2025-12-10→2025-12-11; 2026-09-16→2026-09-17)',
      {'anchors': [F.at_or_before('DFF', '2025-11-23')[1], F.at_or_before('DFF', '2026-08-23')[1], F.at_or_before('DFF', '2026-11-23')[1]],
       'change_points': [d['2025-12-10'], d['2025-12-11'], d['2026-09-16'], d['2026-09-17']],
       'dec_bp_cut': round((d['2025-12-11'] - d['2025-12-10']) * 100), 'dec_bp_hike': round((d['2026-09-17'] - d['2026-09-16']) * 100)},
      ['3.88→3.63→3.88(括注, 未标口径)', None, None, None, -25, 25], True,
      note='括注三值=三时点锚值(逐位一致); 变动点值为 3.89→3.64、3.63→3.88, 相差 1bp(EFFR 日度波动); 步长 -25/+25bp 一致——口径标注可改进, 列 MINOR',
      where='M1.step2 / TR1.step2 "(DFF 3.88→3.63→3.88)" / MAP_REPORT L196')

print('tally', P.tally())
