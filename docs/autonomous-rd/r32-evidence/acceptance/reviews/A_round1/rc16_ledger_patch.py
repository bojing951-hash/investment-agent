# -*- coding: utf-8 -*-
"""rc16: 台账描述字段勘误(Audit-R32 A round1; 只改本席目录内的 points.jsonl)。
用法: /usr/bin/python3 -I rc16_ledger_patch.py <points.jsonl>
背景(席位自纠, 不改变任何比对结论):
  (1) rc08 脚本对中国 7 天逆回购三锚值的 expected 字面写成了具体日(2025-11-14 / 2026-08-14 / 2026-10-30),
      其中「2026-08-14」是席位当时的预期字面, 受审稿该处只写观测月「2026-08」, 引擎点值格该锚
      observation_date=2026-08-21。比对口径自始为「观测月+数值」(rc08 第 194 行按 v[0][:7] 比较), 结论不变;
      现把台账 reported 字段改为与受审稿一致的「观测月」写法, rc08 脚本同步改为同一写法, 便于操作席重跑对账。
  (2) rc12 有一条记录 where 字段为空, 补上出处位置。
幂等: 已含「[rc16]」标记的记录不再改写; 改写前先留备份 points.jsonl.bak-pre-rc16。
"""
import sys, os, json

PTS = sys.argv[1]
lines = [l for l in open(PTS, encoding='utf-8') if l.strip()]
recs = [json.loads(l) for l in lines]
MARK = '[rc16] '
n1 = n2 = 0
for r in recs:
    if str(r.get('note', '')).startswith(MARK):
        continue
    # (1) 中国 7 天逆回购三锚值
    if r.get('section') == '④政策面' and str(r.get('src', '')).startswith('CN_OMO_7D 锚日前最近观测'):
        rep = r.get('reported')
        if isinstance(rep, list) and len(rep) == 2 and isinstance(rep[0], str) and len(rep[0]) == 10:
            month = rep[0][:7]
            lab = str(r['src']).split('最近观测')[-1].strip()
            want = {'12个月前': '2025-11', '3个月前': '2026-08', '最新': '2026-10'}[lab]
            assert month == want and rep[1] == 1.4, (r, month, want)
            r['reported'] = [month, rep[1]]
            r['note'] = MARK + ('原 reported 字面日期 %s 为席位 rc08 脚本的预期字面(非受审稿数字); 受审稿该处只写观测月「%s」; '
                                '比对口径=观测月+数值(rc08 按 v[0][:7] 比较), 结论不变(一致)。引擎点值格该锚 observation_date 见 mid_cells.txt' % (rep[0], month))
            n1 += 1
    # (2) 空 where
    if not str(r.get('where', '')).strip():
        if 'history_periods[2023-10].other_regions_sync' in str(r.get('src', '')):
            r['where'] = 'agent_judgment.reader_map.history_periods[2023-10].other_regions_sync / MAP_REPORT 历史段 2023-10 当时可知面'
            r['note'] = MARK + '补 where 字段 | ' + str(r.get('note', ''))
            n2 += 1
        else:
            raise SystemExit('未预期的空 where 记录: %s' % json.dumps(r, ensure_ascii=False)[:300])
if n1 == 0 and n2 == 0:
    print('nothing to patch (already applied)')
else:
    bak = PTS + '.bak-pre-rc16'
    if not os.path.exists(bak):
        with open(bak, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    tmp = PTS + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    os.replace(tmp, PTS)
    print('patched OMO anchor records: %d; where filled: %d; backup: %s' % (n1, n2, bak))
# 复核
recs2 = [json.loads(l) for l in open(PTS, encoding='utf-8') if l.strip()]
print('records', len(recs2), 'True', sum(1 for r in recs2 if r['ok'] is True), 'False', sum(1 for r in recs2 if r['ok'] is False),
      'NA', sum(1 for r in recs2 if r['ok'] == 'NA'), 'empty where', sum(1 for r in recs2 if not str(r.get('where', '')).strip()))
for i, r in enumerate(recs2):
    if str(r.get('note', '')).startswith(MARK):
        print('  #%d ok=%s computed=%s reported=%s' % (i, r['ok'], json.dumps(r['computed'], ensure_ascii=False)[:80], json.dumps(r['reported'], ensure_ascii=False)[:80]))
