#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""thresholds 三方对账门 G1-G4(ARCH-REFORM T2,2026-11-14)

依据: thresholds-adjudication.md(S1 第4项)+thresholds-curation-note.md §四
+ARCH_REFORM_PHASE2_CONTRACT.md §5。四门任一红=CI fail(exit 1)。

- G1 注册表↔framework.md 双向锚:
    正向=每条 entry.provenance.quote 在 framework.md 逐字命中(空白归一;';'/' / '
    分段锚;表格列头×单元格复合锚;散文按行锚);
    反向=framework.md 阈值区(评分表/OAS表/利率表/能源表/底部量化表/体制映射/
    情景矩阵/DXY散文/分位触发线)抽取的全部阈值性数值须映射到某 stable_key 值,
    评分表行族须在册——双向无孤儿(防注册表凭空条目,也防 framework 暗改)。
- G2 注册表↔macro_scorecard.py 常量集: 代码 SCORECARD_THRESHOLD_KEYS/TH()引用集
    与注册表 scorecard 族键集(含 determine_regime 两键,pending 豁免但显式列出)
    差集双侧为空。
- G3 概念隔离: thresholds 不得误收 metric_registry validation.range 端点值;
    metric_registry.validation 不得新增档位语义字段。
- G4 词典/常量退役断言: data_validator 数值范围字典仅剩正则与词汇规则
    (min/max 数值字段为零);两脚本 if/elif 阈值位不得再出现裸数值字面量
    (非阈值工程常量逐一注释豁免,元规则=门红禁例外白名单,豁免仅限"非阈值语义")。

framework 文本变更后 quote 锚同步=常规维护(注册表为准重生成锚),非门红。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THRESHOLDS_PATH = os.path.join(ROOT, 'config', 'thresholds.json')
FRAMEWORK_PATH = os.path.join(ROOT, 'config', 'framework.md')
METRIC_REGISTRY_PATH = os.path.join(ROOT, 'config', 'metric_registry.json')
SCORECARD_PATH = os.path.join(ROOT, 'scripts', 'macro_scorecard.py')
VALIDATOR_PATH = os.path.join(ROOT, 'scripts', 'data_validator.py')


def _read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def _norm(s):
    """空白归一(CJK 文本锚匹配; incidental ASCII 空格不破坏逐字性)。"""
    return re.sub(r'\s+', '', s)


# ══════════════════════════════════════════════════════════════════
# G1 正向: quote → framework 文本锚
# ══════════════════════════════════════════════════════════════════

_COL_WORDS = ('收缩阈值', '扩张阈值', '通缩阈值', '高通胀阈值', '警戒线', '红线',
              '正常', '关注', '警告', '恐慌')


def _parse_tables(fw_text):
    """解析 markdown 表→[(headers, rows)]; headers/rows 为单元格列表。"""
    tables, cur = [], None
    for line in fw_text.splitlines():
        if line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if all(re.fullmatch(r'[-: ]*', c) for c in cells):
                continue  # 分隔行
            if cur is None:
                cur = (cells, [])
            else:
                cur[1].append(cells)
        else:
            if cur is not None and cur[1]:
                tables.append(cur)
            cur = None
    if cur is not None and cur[1]:
        tables.append(cur)
    return tables


def _composite_hit(seg, tables):
    """复合锚: 『列头+值』(收缩阈值<50 / 红线 5.0%)或『值+(档位)』(400-500bp(警告))。
    解析=在含该列头的表中,找一行其该列单元格含该值文本(空白归一)。"""
    m = re.match(r'^(%s)\s*(.+)$' % '|'.join(_COL_WORDS), seg)
    if m:
        col, valpart = m.group(1), m.group(2)
    else:
        m = re.match(r'^(.+?)\s*[（(](%s)[)）]$' % '|'.join(
            w for w in _COL_WORDS if w in ('正常', '关注', '警告', '恐慌')), seg)
        if not m:
            return False
        valpart, col = m.group(1), m.group(2)
    nv = _norm(valpart)
    for headers, rows in tables:
        if col not in headers:
            continue
        idx = headers.index(col)
        for row in rows:
            if idx < len(row) and nv in _norm(row[idx]):
                return True
    return False


def _seg_hit(seg, fw_norm, tables):
    if not seg:
        return True
    if _norm(seg) in fw_norm:
        return True
    # 管道分解锚(表格行节选,如「收缩阈值<-0.3% | 扩张>+0.3%」)
    parts = [p.strip() for p in seg.split('|') if p.strip()]
    if len(parts) > 1 and all(
            _norm(p) in fw_norm or _composite_hit(p, tables) for p in parts):
        return True
    return _composite_hit(seg, tables)


def g1_forward(entries, fw_text):
    fails = []
    fw_norm = _norm(fw_text)
    tables = _parse_tables(fw_text)
    for e in entries:
        q = (e.get('provenance') or {}).get('quote', '')
        for seg in re.split(r';| / ', q):
            if not _seg_hit(seg.strip(), fw_norm, tables):
                fails.append(f"[{e['stable_key']}] quote 锚未命中: {seg.strip()!r}")
    return fails


# ══════════════════════════════════════════════════════════════════
# G1 反向: framework 阈值区数值 → 注册表值(无孤儿)
# ══════════════════════════════════════════════════════════════════

# 非阈值语义数字白名单(逐一注明豁免理由;仅限"非阈值语义",不是门红例外)
_REVERSE_WHITELIST = {
    2.0: "『≤+2』=stagflation_floor(≥+3)的整数域补集表述(registry 键 semantic_note 原文"
         "『总分整数域,≤+2与≥+3无缝』),非独立阈值",
    -2.0: "同上(补集表述的负侧形态)", 2: "同上",
    0.1: "『±0.1%=0』与补行记号(+0.1,+0.3)的 +0.1 为 m01 键(-0.1)的散文形态/带记号左端点;"
         "裁定#6 钉死 0 带=(-0.1,+0.3],+0.1 非边界值(左开)",
    8.0: "维度总分极值 +8=4指标×+2 的算术极值(评分域定义,非映射阈值)",
    -8.0: "维度总分极值 -8(同上)",
}

_GROWTH_FAMILIES = ('失业率变动', '消费者信心', '零售销售', '工业生产', 'ISM制造业PMI')
_INFLATION_FAMILIES = ('核心CPI', 'BEI', 'WTI油价', '工资增速')

_ISO_DATE = re.compile(r'\d{4}-\d{2}-\d{2}')
_DURATION = re.compile(r'[0-9]+个?(?:交易日|日|月|周|年)')
_NUM = re.compile(r'(?<![0-9.])-?[0-9]+(?:\.[0-9]+)?')


def _cell_numbers(cell):
    """单元格→数值列表(去评分赋值/括注/时长/日期;± 双侧展开)。"""
    cell = _ISO_DATE.sub(' ', cell)
    cell = re.sub(r'[（(][^（）()]*[)）]', lambda m: m.group(0)
                  if re.search(r'[<>~=]', m.group(0)) else ' ', cell)
    out = []
    for tok in cell.split(','):
        tok = re.sub(r'=[+-]?[0-9]+%?$', '', tok.strip())
        if '±' in tok:
            probes = (tok.replace('±', '+'), tok.replace('±', '-'))
        else:
            probes = (tok,)
        for p in probes:
            out.extend(float(x) for x in _NUM.findall(p))
    return out


def _prose_numbers(line):
    line = _ISO_DATE.sub(' ', line)
    line = _DURATION.sub(' ', line)
    return [float(x) for x in _NUM.findall(line)]


def g1_reverse(entries, fw_text):
    fails, hits = [], []
    values = {float(e['value']) for e in entries}

    def note(where, num):
        if num in values:
            hits.append((where, num))
        elif num in _REVERSE_WHITELIST:
            hits.append((where, num))
        else:
            fails.append(f"[framework↔registry 孤儿数值] {where}: {num:g} 未映射到任何 stable_key 值")

    for headers, rows in _parse_tables(fw_text):
        hset = set(headers)
        # §一 两张评分表
        if '收缩阈值' in hset or '通缩阈值' in hset:
            fams = _GROWTH_FAMILIES if '收缩阈值' in hset else _INFLATION_FAMILIES
            cols = [c for c in ('收缩阈值', '扩张阈值', '通缩阈值', '高通胀阈值',
                                '评分规则') if c in headers]
            for row in rows:
                name = row[0] if row else ''
                if not any(f in name for f in fams):
                    fails.append(f"[framework 评分表未知行族] {name!r} 不在注册表指标族内"
                                 "(新指标入表须先入注册表并经金融席签字)")
                    continue
                for c in cols:
                    for n in _cell_numbers(row[headers.index(c)]):
                        note(f"评分表[{name}].{c}", n)
        # §二 OAS 表(bp→pp ÷100)
        elif {'正常', '恐慌'} <= hset:
            for row in rows:
                for c in ('正常', '关注', '警告', '恐慌'):
                    cell = row[headers.index(c)]
                    for n in _cell_numbers(cell):
                        note(f"OAS表[{row[0]}].{c}", n / 100.0 if 'bp' in cell else n)
        # §三 利率表
        elif {'警戒线', '红线'} <= hset:
            for row in rows:
                for c in ('警戒线', '红线'):
                    for n in _cell_numbers(row[headers.index(c)]):
                        note(f"利率表[{row[0]}].{c}", n)
        # §五 能源表
        elif 'WTI区间' in hset:
            for row in rows:
                for n in _cell_numbers(row[headers.index('WTI区间')]):
                    note(f"能源表[{row[0]}]", n)
        # §六 底部量化表(万亿→cny_100m ×10000;亿港元=hkd_100m 同值)
        elif '量化阈值' in hset:
            for row in rows:
                cell = row[headers.index('量化阈值')]
                for n in _cell_numbers(cell):
                    note(f"底部量化表[{row[0]}]", n * 10000.0 if '万亿' in cell else n)
        # §八 情景矩阵(表头分界+行标)
        elif {'通胀低', '通胀高'} <= set(re.sub(r'[（(].*?[)）]', '', h) for h in headers):
            for h in headers:
                for n in _cell_numbers(h):
                    note('情景矩阵表头', n)
            for row in rows:
                for n in _cell_numbers(row[0]):
                    note(f"情景矩阵行标[{row[0]}]", n)

    # 散文阈值区
    sec = fw_text
    for m in re.finditer(r'^- DXY.*$', sec, re.M):
        for n in _prose_numbers(m.group(0)):
            note('DXY散文', n)
    for m in re.finditer(r'^\d+\.\s.*(?:万亿|亿港元).*$', sec, re.M):
        line = re.sub(r'^\d+\.\s', '', m.group(0))
        for n in _prose_numbers(line):
            note('底部三条件散文', n * 10000.0 if '万亿' in line and '港元' not in line else n)
    for m in re.finditer(r'^.*历史分位数.*$', sec, re.M):
        for n in _prose_numbers(m.group(0)):
            note('分位触发线', n)
    regime = re.search(r'###\s*体制映射(.*?)###\s*输出要求', sec, re.S)
    if regime:
        for m in re.finditer(r'^- .*$', regime.group(1), re.M):
            for n in _prose_numbers(m.group(0)):
                note('体制映射', n)
    return fails, hits


# ══════════════════════════════════════════════════════════════════
# G2: 代码常量集 ↔ 注册表 scorecard 族键集(差集双空)
# ══════════════════════════════════════════════════════════════════

_REGIME_KEYS = {'regime.inflation_total.stagflation_floor', 'regime.growth_total.zero'}


def g2(entries, scorecard_src):
    """signed registry G2 措辞:『代码常量集合与注册表 scorecard 族键集合差集双侧为空
    (pending 豁免但显式列出)』。scorecard 族=stable_key 含 .scorecard. 段的键+体制两键
    (band_edge 评分带缘);headline 级键(如 bei_10y.headline_high,显示串消费)按
    two_level_model=叙述级,不属 scorecard 族,但代码读取它仍须在注册表存在(防凭空常量)。"""
    fails = []
    m = re.search(r'SCORECARD_THRESHOLD_KEYS = \((.*?)\)', scorecard_src, re.S)
    if not m:
        return ['macro_scorecard.py 缺 SCORECARD_THRESHOLD_KEYS 声明(常量退役锚丢失)'], []
    declared = set(re.findall(r"'([a-z0-9_.]+)'", m.group(1)))
    used = set(re.findall(r"TH\('([a-z0-9_.]+)'\)", scorecard_src))
    all_keys = {e['stable_key'] for e in entries if e.get('status') != 'pending'}
    fam = {e['stable_key'] for e in entries
           if '.scorecard.' in e['stable_key'] and e.get('status') != 'pending'} | _REGIME_KEYS
    pending = sorted(e['stable_key'] for e in entries
                     if '.scorecard.' in e['stable_key'] and e.get('status') == 'pending')
    if used - declared:
        fails.append(f"[G2] TH() 引用未声明键: {sorted(used - declared)}")
    if declared - used:
        fails.append(f"[G2] 声明未使用键(死声明=漂移): {sorted(declared - used)}")
    if declared - all_keys:
        fails.append(f"[G2] 代码读取键不在注册表(凭空常量=红): {sorted(declared - all_keys)}")
    if fam - declared:
        fails.append(f"[G2] 注册表 scorecard 族无实施(入册无实施=红): {sorted(fam - declared)}")
    return fails, pending


# ══════════════════════════════════════════════════════════════════
# G3: 概念隔离静态断言
# ══════════════════════════════════════════════════════════════════

_ALLOWED_VALIDATION_FIELDS = {'range', 'max_week_pct_move', 'max_week_abs_move'}


def g3(entries, metrics_doc):
    fails = []
    ranges = {}
    for met in metrics_doc.get('metrics', []):
        rng = (met.get('validation') or {}).get('range')
        if rng and len(rng) == 2:
            ranges[met.get('metric_id')] = {float(rng[0]), float(rng[1])}
        extra = set((met.get('validation') or {})) - _ALLOWED_VALIDATION_FIELDS
        if extra:
            fails.append(f"[G3] metric_registry {met.get('metric_id')}.validation 出现未认可字段"
                         f" {sorted(extra)}(档位语义字段禁入 validation;分析阈值归 thresholds.json)")
    for e in entries:
        eps = ranges.get(e.get('metric_id'))
        if eps and float(e['value']) in eps:
            fails.append(f"[G3] {e['stable_key']} value={e['value']} 误收 "
                         f"{e['metric_id']} validation.range 端点值(概念隔离违例)")
    return fails


# ══════════════════════════════════════════════════════════════════
# G4: 词典/常量退役断言
# ══════════════════════════════════════════════════════════════════

# 非阈值工程常量豁免(逐一注明理由;均为工程/护栏逻辑,无市场阈值语义)
_G4_WHITELIST = (
    (r'value != 0', '零值锚点排除(拍平采集时 0 不作锚点,工程逻辑)'),
    (r'anchor_val == 0', '零锚点跳过(除零护栏,工程逻辑)'),
    (r'abs\(v\) >= 10000', '报告数值字节量级护栏(|v|≥10000 视为行文元数据,工程逻辑)'),
    (r'len\(t\) == 8', '紧凑日期 YYYYMMDD 长度检查(工程逻辑)'),
    (r'deviation_pct > 20', '严重/一般错误分级线(校验器输出分级,非市场阈值)'),
    (r'max\(spec\["tol"\], 0\.05\)', '周变化值识别容差下限(校验器工程参数)'),
    (r'abs\(num\) <= 0\.5', '小幅变化值豁免阈(校验器工程参数,非市场阈值)'),
    (r'len\(rng\) != 2', 'validation.range 二元组形状校验(工程逻辑)'),
    (r'abs\(value\) > 1', '锚点摘要跳过 ±1/0 评分数整数(显示层工程逻辑)'),
)


def g4(validator_src, scorecard_src, entries, metrics_doc):
    fails = []
    # 1) 退役字典残余: 数值界字段名不得再现
    for path_name, src in (('data_validator.py', validator_src),
                           ('macro_scorecard.py', scorecard_src)):
        for m in re.finditer(r'"(min_value|max_value|max_value_K)"\s*:', src):
            fails.append(f"[G4] {path_name} 出现退役数值界字段 {m.group(1)!r}(区间唯一权威"
                         "=metric_registry validation.range)")
    # 2) SANITY_CHECKS 结构: 仅剩正则/词汇规则,无数值界
    m = re.search(r'SANITY_CHECKS = \{(.*?)\n\}\n', validator_src, re.S)
    if not m:
        fails.append('[G4] data_validator.py 缺 SANITY_CHECKS 定义')
    else:
        for bad in ('"min_value"', '"max_value"', '"max_value_K"'):
            if bad in m.group(1):
                fails.append(f'[G4] SANITY_CHECKS 残留数值界字段 {bad}')
        for rid in re.findall(r'"range_metric_id":\s*"([A-Z0-9_]+)"', m.group(1)):
            known = {x.get('metric_id') for x in metrics_doc.get('metrics', [])}
            if rid not in known:
                fails.append(f'[G4] SANITY_CHECKS.range_metric_id={rid} 不在 metric_registry')
    # 3) if/elif 阈值位裸数值字面量扫描(两脚本)
    cmp_lit = re.compile(r'[<>!=]=?\s*(-?[0-9]+(?:\.[0-9]+)?)')

    def _cond_part(line):
        """截取 if/elif 行的条件表达式(冒号后是语句体,如 'if v < TH(..): s = -2'
        的 -2 是档位赋值输出,非比较常量——不得扫描)。"""
        depth = 0
        for i, ch in enumerate(line):
            if ch in '([{':
                depth += 1
            elif ch in ')]}':
                depth -= 1
            elif ch == ':' and depth == 0:
                return line[:i]
        return line

    for path_name, src in (('data_validator.py', validator_src),
                           ('macro_scorecard.py', scorecard_src)):
        for ln in src.splitlines():
            m = re.match(r'\s*(?:el)?if\b(.*)', ln)
            if not m:
                continue
            cond = _cond_part(m.group(1))
            lits = cmp_lit.findall(cond)
            if not lits:
                continue
            if any(re.search(pat, cond) for pat, _ in _G4_WHITELIST):
                continue
            fails.append(f"[G4] {path_name} 条件常量未豁免: {ln.strip()[:100]}"
                         f"(字面量 {lits};若确非阈值语义,须在门内加注释豁免理由并说明)")
    return fails


# ══════════════════════════════════════════════════════════════════
# 主入口
# ══════════════════════════════════════════════════════════════════

def run(thresholds_path=None, framework_path=None, metrics_path=None,
        scorecard_path=None, validator_path=None):
    th_path = thresholds_path or THRESHOLDS_PATH
    fw_path = framework_path or FRAMEWORK_PATH
    mr_path = metrics_path or METRIC_REGISTRY_PATH
    sc_path = scorecard_path or SCORECARD_PATH
    dv_path = validator_path or VALIDATOR_PATH

    th_doc = json.loads(_read(th_path))
    entries = th_doc.get('entries', [])
    fw_text = _read(fw_path)
    metrics_doc = json.loads(_read(mr_path))
    sc_src = _read(sc_path)
    dv_src = _read(dv_path)

    report = {}
    report['G1_forward'] = g1_forward(entries, fw_text)
    report['G1_reverse'], _hits = g1_reverse(entries, fw_text)
    report['G2'], pending = g2(entries, sc_src)
    report['G3'] = g3(entries, metrics_doc)
    report['G4'] = g4(dv_src, sc_src, entries, metrics_doc)
    return report, pending


def main():
    report, pending = run()
    print('═' * 64)
    print('thresholds 三方对账门 G1-G4(ARCH-REFORM T2)')
    print('═' * 64)
    for gate, fails in report.items():
        if fails:
            print(f'🔴 {gate}: {len(fails)} 违例')
            for f in fails:
                print(f'   - {f}')
        else:
            print(f'🟢 {gate}: PASS')
    if pending:
        print(f'🟡 pending 键(豁免 G2 实施比对,显式列出): {pending}')
    all_fail = sum(len(v) for v in report.values())
    print('─' * 64)
    if all_fail:
        print(f'结果: RED({all_fail} 违例)——修复只能改源文档或注册表并重走金融席签字,'
              f'禁止门内例外/白名单(元规则)')
        return 1
    print('结果: 全绿(G1-G4 PASS)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
