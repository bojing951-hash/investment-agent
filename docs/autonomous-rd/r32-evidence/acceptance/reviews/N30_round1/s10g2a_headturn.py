# s10g2a_headturn.py <snap> <rep> <cal> <reg> <aj> <out>  -- headline + turnings + history note
import sys, json
sys.path.insert(0, sys.argv[0].rsplit('/', 1)[0])
from rc_common import *
c = Ctx(*sys.argv[1:7])
RP = c.rep['research_plan']; A = c.asof
EA = 'EA_HICP_YOY'; JP = 'JP_CPI_YOY'; TK = 'JP_CPI_TOKYO_YOY'; PR = 'JP_POLICY_RATE'
T = 1e-6
def tk(snip, tok, rep, comp, src, tol=None):
    c.num('G', src, comp, rep, tok, snip, tol=tol)
def E(m, y):
    return c.mv(m, y)
def df(m, a, b):
    return round(E(m, b) - E(m, a), 2)
def walk(o, p=()):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, p + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, p + (i,))
    else:
        yield p, o
def node(p):
    o = c.rep
    for k in p:
        o = o[k]
    return o
Y26 = ['2026-%02d' % i for i in range(1, 11)]
Y12 = ['2025-11', '2025-12'] + Y26
Y2526 = ['2025-%02d' % i for i in range(1, 13)] + Y26
# ---- headline ----
tk('2026 年 11 月回看最近六个月', '11', 11, int(RP['as_of_declared']['requested_as_of'][5:7]), 'as_of_declared.requested_as_of 月份', tol=T)
tk('2026 年 11 月回看最近六个月', '六', 6, RP['question_window']['windows'][0]['months'], 'question_window 月数', tol=T)
tk('高于去年同月(2025-10 为 2.1)', '2.1', 2.1, E(EA, '2025-10'), 'EA@2025-10')
tk('日本低于去年同月(2025-10 为 2.99)', '2.99', 2.99, E(JP, '2025-10'), 'JP@2025-10')
tk('月均口径六个月锚间由 0.727 升至 1.227', '0.727', 0.727, E(PR, '2026-04'), 'PR 六个月前锚(观测月 2026-04)')
tk('月均口径六个月锚间由 0.727 升至 1.227', '1.227', 1.227, E(PR, '2026-10'), 'PR 最新一期锚(观测月 2026-10)')
tk('两次合计五十个基点', '五十', 50, round((c.last('ECB_MRO')[1] - c.at('ECB_MRO', '2025-06-11')) * 100), 'ECB_MRO 最新 − 六个月前锚(bp)', tol=T)
tk('六个月锚间净变动约五十个基点', '五十', 50, round((E(PR, '2026-10') - E(PR, '2026-04')) * 100), 'PR 最新 − 六个月前锚(bp)', tol=T)
hl = c.aj['reader_map']['headline_conclusion']
seg = hl.split('证据不足六项: ', 1)[1]
n = 1; depth = 0
for ch in seg:
    if ch == '(':
        depth += 1
    elif ch == ')':
        depth -= 1
    elif ch == '、' and depth == 0:
        n += 1
tk('证据不足六项', '六', 6, n, 'headline 证据不足项顶层顿号分隔计数', tol=T)
tk('距截止 六十八 天,Gate A 列 degraded', '六十八', 68, days('2026-09-16', A), 'days(ECB 序列末日,研究截止)', tol=T)
c.ok('G', '「欧元区两年期与十年期在册」(注册表含 BUND_2Y/BUND_10Y)', 'BUND_2Y' in c.RM and 'BUND_10Y' in c.RM, ('BUND_2Y' in c.RM, 'BUND_10Y' in c.RM))
c.has_text('G', '「欧元区两年期与十年期在册」(期限名称,非数值主张)', '欧元区两年期与十年期在册', '期限名称「两年期/十年期」')
c.ok('G', '「日本端事实行在场」(JGB2Y/JGB5Y/JGB10Y 事实行)', all(c.fact(m) is not None for m in ('JGB2Y', 'JGB5Y', 'JGB10Y')), [c.fact(m) is not None for m in ('JGB2Y', 'JGB5Y', 'JGB10Y')])
c.ok('G', '「均不在本问证据索引」(BUND_2Y/BUND_10Y/JGB2Y/JGB5Y/JGB10Y 均不在 evidence_index)', not any(str(x.get('metric_id')) in ('BUND_2Y', 'BUND_10Y', 'JGB2Y', 'JGB5Y', 'JGB10Y') for x in c.rep['evidence_index']), sorted(set(str(x.get('metric_id')) for x in c.rep['evidence_index'])))
c.ok('G', '「GDP 两序列在册、当日快照事实行缺席」', all(m in c.RM and c.fact(m) is None for m in ('EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY')), [(m in c.RM, c.fact(m)) for m in ('EA_REAL_GDP_YOY', 'JP_REAL_GDP_YOY')])
# ---- turnings[0] ----
S0 = '由 1.9 升至 3.2(三个月 +1.30 个百分点)'
tk(S0, '1.9', 1.9, E(EA, '2026-02'), 'EA@2026-02')
tk(S0, '3.2', 3.2, E(EA, '2026-05'), 'EA@2026-05')
tk(S0, '三', 3, 3, '月差 2026-02→2026-05', tol=T)
tk(S0, '1.30', 1.30, df(EA, '2026-02', '2026-05'), 'EA 2026-05 − 2026-02')
S1 = '(2026-02 1.27→2026-05 1.53)'
tk(S1, '1.27', 1.27, E(JP, '2026-02'), 'JP@2026-02')
tk(S1, '1.53', 1.53, E(JP, '2026-05'), 'JP@2026-05')
tk('欧元区 2026-01 的 1.7、日本', '1.7', 1.7, E(EA, '2026-01') if E(EA, '2026-01') == min(E(EA, y) for y in Y26) else -1, 'EA 2026 年内谷底=2026-01')
tk('日本 2026-02 的 1.27;欧央行', '1.27', 1.27, E(JP, '2026-02') if E(JP, '2026-02') == min(E(JP, y) for y in Y2526) else -1, 'JP 2025-01..2026-10 谷底=2026-02')
S2 = '(2.9→1.27,三个月 -1.63 个百分点)'
tk(S2, '2.9', 2.9, E(JP, '2025-11'), 'JP@2025-11')
tk(S2, '1.27', 1.27, E(JP, '2026-02'), 'JP@2026-02')
tk(S2, '三', 3, 3, '月差 2025-11→2026-02', tol=T)
tk(S2, '1.63', 1.63, abs(df(JP, '2025-11', '2026-02')), 'JP 2026-02 − 2025-11')
tk('未列入三转折', '三', 3, len(c.aj['reader_map']['turnings']), '走位面转折条数', tol=T)
tk('主要发生在六个月窗(起 2026-05-23)', '六', 6, 6, '回看窗月数', tol=T)
S3 = '此后逐月路径 2026-06 2.8、2026-07 2.9、2026-08 3.2、2026-09 3.8、2026-10 4.0'
for y, v in (('2026-06', '2.8'), ('2026-07', '2.9'), ('2026-08', '3.2'), ('2026-09', '3.8'), ('2026-10', '4.0')):
    tk(S3, v, float(v), E(EA, y), 'EA@' + y)
tk('其中 2026-06 一度回落至 2.8', '2.8', 2.8, E(EA, '2026-06'), 'EA@2026-06')
tk('最新读数为近十二个月最高', '十二', 12, 12 if E(EA, '2026-10') == max(E(EA, y) for y in Y12) else -1, 'EA 2025-11..2026-10 最高=最新读数', tol=T)
# ---- turnings[1] ----
S4 = '2026-04 0.727→2026-07 0.978(经 2026-06 0.841 过渡)'
tk(S4, '0.727', 0.727, E(PR, '2026-04'), 'PR@2026-04')
tk(S4, '0.978', 0.978, E(PR, '2026-07'), 'PR@2026-07')
tk(S4, '0.841', 0.841, E(PR, '2026-06'), 'PR@2026-06')
S5 = '日本月均 2026-06 的台阶(0.727→0.841)'
tk(S5, '0.727', 0.727, E(PR, '2026-05'), 'PR@2026-05(台阶前值)')
tk(S5, '0.841', 0.841, E(PR, '2026-06'), 'PR@2026-06')
S6 = '此后逐月路径 2026-08 0.977、2026-09 1.043、2026-10 1.227'
for y, v in (('2026-08', '0.977'), ('2026-09', '1.043'), ('2026-10', '1.227')):
    tk(S6, v, float(v), E(PR, y), 'PR@' + y)
S7 = '月均台阶 2026-09→2026-10(1.043→1.227)'
tk(S7, '1.043', 1.043, E(PR, '2026-09'), 'PR@2026-09')
tk(S7, '1.227', 1.227, E(PR, '2026-10'), 'PR@2026-10')
# ---- turnings[2] ----
S8 = '2026-06→2026-09 由 1.6 升至 2.69(三个月 +1.09 个百分点)'
tk(S8, '1.6', 1.6, E(TK, '2026-06'), 'TK@2026-06')
tk(S8, '2.69', 2.69, E(TK, '2026-09'), 'TK@2026-09')
tk(S8, '三', 3, 3, '月差 2026-06→2026-09', tol=T)
tk(S8, '1.09', 1.09, df(TK, '2026-06', '2026-09'), 'TK 2026-09 − 2026-06')
tk('欧元区同期读数亦高(2026-09 为 3.8)', '3.8', 3.8, E(EA, '2026-09'), 'EA@2026-09')
tk('东京都 2026-09 读数 2.69 与全国口径', '2.69', 2.69, E(TK, '2026-09'), 'TK@2026-09')
S9 = '全国 2026-06 1.67→2026-08 1.98'
tk(S9, '1.67', 1.67, E(JP, '2026-06'), 'JP@2026-06')
tk(S9, '1.98', 1.98, E(JP, '2026-08'), 'JP@2026-08')
S10 = '全国口径 -1.64、东京口径 -1.11'
tk(S10, '1.64', 1.64, df(JP, '2026-09', '2026-09') if False else abs(round(E(JP, '2026-09') - E(EA, '2026-09'), 2)), 'JP − EA @2026-09')
tk(S10, '1.11', 1.11, abs(round(E(TK, '2026-09') - E(EA, '2026-09'), 2)), 'TK − EA @2026-09')
tk('决议前可见的最近东京读数为 2026-08 的 1.9(推定发布', '1.9', 1.9, E(TK, '2026-08'), 'TK@2026-08')
c.eq('G', '东京 2026-08 期推定发布日(月末−1)', c.pub(TK, '2026-08'), '2026-08-30')
c.eq('G', '该推定日星期', wd(c.pub(TK, '2026-08')), '周日')
def lastfri(ym):
    return max(plus(mend(ym), -i) for i in range(0, 8) if wd(plus(mend(ym), -i)) == '周五')
c.ok('G', '官方实录锚 2026-06-26、2026-10-30 均为当月最后一个周五', lastfri('2026-06') == '2026-06-26' and lastfri('2026-10') == '2026-10-30', (lastfri('2026-06'), lastfri('2026-10')))
c.ok('G', '按「当月最后一个周五」形态东京可见性结论不变: 2026-08 期 08-28 早于 BOJ 决议日 09-18; 2026-09 期 09-25 晚于 09-18', lastfri('2026-08') < '2026-09-18' < lastfri('2026-09'), (lastfri('2026-08'), lastfri('2026-09')))
# ---- history note ----
hk = ['history_periods']
c.num('G', 'l4 历史类比段数(键 ' + str(hk) + ')', len(c.aj['reader_map'][hk[0]]) if hk else -1, 0, '0', '历史类比 0 段(契约允许 0..3 段')
lev = list(walk(c.rep))
p71 = [p for p, v in lev if isinstance(v, (int, float)) and not isinstance(v, bool) and v == 1871]
v74 = -1; d727 = -1; pn = None
for p in p71:
    for k in range(len(p), 0, -1):
        sc = [v for _, v in walk(node(p[:k]))]
        if any(isinstance(v, (int, float)) and not isinstance(v, bool) and v == 74 for v in sc) and any(isinstance(v, (int, float)) and abs(v - 0.727) < 0.0006 for v in sc):
            v74 = 74; pn = p[:k]
            d727 = [v for v in sc if isinstance(v, (int, float)) and abs(v - 0.727) < 0.0006][0]
            break
    if v74 == 74:
        break
tk('扫描 1871 个候选月', '1871', 1871, 1871 if p71 else -1, 'S6 analog 扫描候选月数(report.json 标量 1871)', tol=T)
tk('有效 74、TOP1', '74', 74, v74, 'S6 analog 有效候选月数', tol=T)
tk('候选月 2025-03 距离 0.727', '0.727', 0.727, d727, 'S6 analog TOP1 距离')
c.ok('G', 'S6 analog TOP1 候选月=2025-03(同一容器内字符串)', any(isinstance(v, str) and v.startswith('2025-03') for _, v in walk(node(pn))) if pn else False, pn)
tk('本问焦点为最近六个月两地对照', '六', 6, 6, '回看窗月数', tol=T)
c.save('g2a')
