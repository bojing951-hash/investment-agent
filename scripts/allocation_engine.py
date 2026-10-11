#!/usr/bin/env python3
"""配置研究引擎 v2.0 (第二轮审查重构, 2026-10-11)

相对v1.0的修复(对应第二轮审查第二项):
1. 评级量表统一为4级: 超配/标配/低配/观望 — "标配"即中性仓位基准,
   消除"标配/中性"混用(旧数据自动迁移 中性→标配)
2. 修复"仅确信度变化不回写"缺陷: 评级变化与确信度变化分别记录为独立history条目,
   任一有效观点行解析成功即落盘(不再要求"评级变更"才写文件)
3. 量化触发器(quant_triggers)由Python核验: 报告/提示词只能声称引擎已核验"已触发"
   的条件; 无锚点可验证的条件一律标注"待验证",不得假装已触发
4. 预测五态生命周期: 未触发(not_yet_triggered)/观察中(observing)/已命中(hit)/
   已证伪(miss)/无法裁决(inconclusive); 带指标规格(指标ID+比较符+目标值+期限+
   证据引用)的到期预测由引擎自动按锚点裁决
5. 预测裁决必须有证据(note引用具体数值/观测日),无证据的hit/miss被程序拒绝

职责不变: 渲染观点库进周报prompt + 解析ALLOCATION_STATUS/PREDICTION_STATUS回写。
回写与thesis同门禁——校验分级FAIL时由调用方(report_generator)跳过。
"""
import os
import sys
import re
import json
import shutil
from datetime import datetime, timedelta

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VIEWS_PATH = os.path.join(ROOT_DIR, 'config', 'allocation_views.json')

# ── 评级量表v2(第二轮#2: 统一定义,删除"中性") ──────────────────────
ALLOWED_RATINGS = ['超配', '标配', '低配', '观望']
RATING_DEFINITIONS = {
    '超配': '相对理论基准上调(证据分级≥3★方可授予)',
    '标配': '与理论基准一致(即中性仓位,不表达方向倾斜)',
    '低配': '相对理论基准下调',
    '观望': '证据不足或处于触发边缘,暂不表达配置倾向(等待数据)',
}

# ── 预测状态v2(第二轮#14/#16: 五态) ──────────────────────
PRED_STATUSES = ['not_yet_triggered', 'observing', 'hit', 'miss', 'inconclusive']
PRED_STATUS_CN = {'not_yet_triggered': '未触发', 'observing': '观察中',
                  'hit': '已命中', 'miss': '已证伪', 'inconclusive': '无法裁决'}
ALLOWED_PRED_VERDICTS = {'hit', 'miss', 'inconclusive'}
# 容错: 模型可能输出中文状态或v1英文状态
_PRED_STATUS_MAP = {
    '命中': 'hit', '已命中': 'hit', '验证': 'hit',
    '证伪': 'miss', '已证伪': 'miss', '落空': 'miss', '未命中': 'miss',
    '无法裁决': 'inconclusive', '待定': 'inconclusive', 'inconclusive': 'inconclusive',
    '未触发': 'not_yet_triggered', 'not_yet_triggered': 'not_yet_triggered',
    '观察中': 'observing', '观察': 'observing', '延续': 'observing',
    'open': 'observing',          # v1迁移
    'expired': 'inconclusive',    # v1迁移: 过期未裁决→无法裁决
}

COMPARATORS = {
    '>=': lambda a, b: a >= b,
    '<=': lambda a, b: a <= b,
    '>': lambda a, b: a > b,
    '<': lambda a, b: a < b,
    '==': lambda a, b: abs(a - b) < 1e-9,
}


def _migrate_views(data):
    """v1→v2就地迁移: 中性→标配、预测状态open/expired→observing/inconclusive。返回是否改动。"""
    changed = False
    for v in data.get('views', []):
        if v.get('rating') == '中性':
            v['rating'] = '标配'
            changed = True
    if '中性' in (data.get('ratings_scale') or []):
        data['ratings_scale'] = list(ALLOWED_RATINGS)
        changed = True
    for p in data.get('predictions', []):
        if p.get('status') in ('open', 'expired'):
            p['status'] = _PRED_STATUS_MAP[p['status']]
            changed = True
    return changed


def load_views(views_path=None):
    path = views_path or DEFAULT_VIEWS_PATH
    if not os.path.exists(path):
        print(f"⚠️ 观点库不存在: {path}")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    _migrate_views(data)  # 读侧归一,不落盘(写侧update时才持久化)
    return data


def due_predictions(views_data, today_str=None):
    """已过deadline仍处于 未触发/观察中 的预测 → 周报须在本期给出裁决(或由引擎自动裁决)"""
    today = today_str or datetime.now().strftime('%Y-%m-%d')
    return [p for p in views_data.get('predictions', [])
            if p.get('status') in ('open', 'observing', 'not_yet_triggered')
            and p.get('deadline', '9999-99-99') <= today]


# ── 量化触发器核验(第二轮#3: 阈值必须Python核验,不可核验→待验证) ──────────────────────
def evaluate_quant_triggers(views_data, anchors):
    """对每个view.quant_triggers逐条核验: 引擎按锚点现值计算触发状态。
    返回 {view_id: [ {trig_id, direction, status, detail} ]},
    status ∈ triggered(已触发)/not_triggered(未触发)/unverifiable(待验证,无锚点)。"""
    results = {}
    for v in views_data.get('views', []):
        rows = []
        for t in v.get('quant_triggers', []) or []:
            metric, op, target = t.get('metric'), t.get('op'), t.get('target')
            if metric not in (None, '') and op in COMPARATORS and isinstance(target, (int, float)):
                info = (anchors or {}).get(metric)
                if info and isinstance(info.get('value'), (int, float)):
                    val = float(info['value'])
                    fired = COMPARATORS[op](val, float(target))
                    rows.append({
                        'trig_id': t.get('trig_id', '?'), 'direction': t.get('direction', '?'),
                        'status': 'triggered' if fired else 'not_triggered',
                        'detail': f"{metric}={val}{t.get('unit','')} {op} {target}{t.get('unit','')}"
                                  f" → {'✅满足' if fired else '⬜未满足'}(观测日{info.get('obs_date','?')})",
                    })
                    continue
                rows.append({'trig_id': t.get('trig_id', '?'), 'direction': t.get('direction', '?'),
                             'status': 'unverifiable',
                             'detail': f"{metric} 无当日锚点,待验证(不得声称已触发)"})
            else:
                rows.append({'trig_id': t.get('trig_id', '?'), 'direction': t.get('direction', '?'),
                             'status': 'unverifiable', 'detail': '条件不可量化,待验证(不得声称已触发)'})
        # 观点triggers.upgrade/downgrade文字条件无量化规格 → 整体标注待验证
        results[v['id']] = rows
    return results


# ── 到期预测自动裁决(第二轮#14: 可计算指标由Python裁决) ──────────────────────
def evaluate_predictions(views_data, anchors, today_str=None):
    """对已过deadline且带指标规格(metric+comparator+target)的预测,按锚点自动裁决。
    只处理'观察中'状态;返回 [(pred_id, old, new, note)],由调用方决定写入。"""
    today = today_str or datetime.now().strftime('%Y-%m-%d')
    verdicts = []
    for p in views_data.get('predictions', []):
        if p.get('status') != 'observing' or p.get('deadline', '9999-99-99') > today:
            continue
        metric, op, target = p.get('metric'), p.get('comparator'), p.get('target')
        if not (metric and op in COMPARATORS and isinstance(target, (int, float))):
            continue  # 无可计算规格 → 留给GLM裁决(须附证据)
        info = (anchors or {}).get(metric)
        if not (info and isinstance(info.get('value'), (int, float))):
            verdicts.append((p['pred_id'], p['status'], 'inconclusive',
                             f"到期无{metric}锚点数据,无法自动裁决"))
            continue
        val = float(info['value'])
        fired = COMPARATORS[op](val, float(target))
        new = 'hit' if fired else 'miss'
        note = f"引擎自动裁决: {metric}={val}(观测日{info.get('obs_date','?')}) {op} {target} → {'满足' if fired else '不满足'}"
        verdicts.append((p['pred_id'], p['status'], new, note))
    return verdicts


def predictions_in_period(views_data, start, end):
    """统计周期内(YYYYMMDD闭区间)按deadline/resolved_date归期的预测。
    返回 {due:[...], resolved:[...], counts:{hit,miss,inconclusive,open}}(第二轮#16)。"""
    s, e = str(start).replace('-', ''), str(end).replace('-', '')
    due, resolved = [], []
    for p in views_data.get('predictions', []):
        dl = str(p.get('deadline', '')).replace('-', '')
        rd = str(p.get('resolved_date', '')).replace('-', '')
        if s <= dl <= e:
            due.append(p)
        if rd and s <= rd <= e:
            resolved.append(p)
    counts = {k: sum(1 for p in resolved if p.get('status') == k)
              for k in ('hit', 'miss', 'inconclusive')}
    counts['open'] = sum(1 for p in due if p.get('status') in ('observing', 'not_yet_triggered', 'open'))
    return {'due': due, 'resolved': resolved, 'counts': counts}


# ── 渲染(进周报prompt) ──────────────────────
def render_views_block(views_data, today_str=None, anchors=None):
    """观点库 → prompt文本块: 评级定义 + 引擎核验过的触发器状态 + 预测五态跟踪"""
    if not views_data:
        return "(观点库缺失,本周跳过配置观点)"
    lines = ["(评级为相对观点而非仓位指令;星级不直接推导仓位)"]
    lines.append("评级量表(只允许以下4级): " + "; ".join(
        f"{r}={d}" for r, d in RATING_DEFINITIONS.items()))

    trig_eval = evaluate_quant_triggers(views_data, anchors)
    lines.append("")
    lines.append("| 资产 | 评级 | 确信度 | 核心理由 | 升级触发(引擎核验) | 降级触发(引擎核验) |")
    lines.append("|------|------|--------|----------|----------|----------|")
    for v in views_data.get('views', []):
        stars = "★" * v.get('confidence', 0)
        by_dir = {'upgrade': '待验证(不可量化)', 'downgrade': '待验证(不可量化)'}
        for row in trig_eval.get(v['id'], []):
            mark = {'triggered': '✅已触发', 'not_triggered': '⬜未触发',
                    'unverifiable': '❓待验证'}[row['status']]
            by_dir[row['direction']] = f"[{row['trig_id']}]{mark} {row['detail'][:44]}"
        lines.append(f"| {v['asset']} | {v.get('rating','?')} | {stars} | "
                     f"{v.get('rationale','')[:40]}… | {by_dir['upgrade']} | {by_dir['downgrade']} |")

    lines.append("")
    lines.append("⚠️ 触发器纪律: 只有引擎核验为\"✅已触发\"的条件才可在报告中表述为已触发;"
                 "\"❓待验证\"的条件必须原文标注待验证,不得当作已发生。")

    preds = views_data.get('predictions', [])
    if preds:
        lines.append("")
        lines.append("### 预测跟踪(五态: 未触发/观察中/已命中/已证伪/无法裁决)")
        due = {p['pred_id'] for p in due_predictions(views_data, today_str)}
        for p in preds:
            status_cn = PRED_STATUS_CN.get(p.get('status', 'observing'), p.get('status'))
            mark = " ⏰已到期,本周必须裁决" if p['pred_id'] in due else ""
            spec = ""
            if p.get('metric'):
                spec = f" [规格: {p['metric']} {p.get('comparator')} {p.get('target')}]"
            lines.append(f"- [#{p['pred_id']}][{status_cn}] {p['asset']}: "
                         f"{p['direction'][:60]} (截止{p.get('deadline','?')}){spec}{mark}")
    return "\n".join(lines)


def _parse_status_block(report_text, tag):
    """提取 <!--TAG ... TAG--> 内的JSON对象列表(容错:代码围栏/逐行JSON)"""
    m = re.search(rf'<!--\s*{tag}\s*(.*?)\s*{tag}\s*-->', report_text, re.DOTALL)
    if not m:
        return []
    block = m.group(1).replace('```json', '').replace('```', '')
    objs = []
    try:
        parsed = json.loads(block.strip())
        objs = parsed if isinstance(parsed, list) else [parsed]
    except Exception:
        for mm in re.finditer(r'\{[^{}]*\}', block):
            try:
                objs.append(json.loads(mm.group(0)))
            except Exception:
                pass
    return objs


def _hist_append(hist, tag, kind, text):
    """同日同类条目去重: 重跑时替换而非追加。kind: 评级/确信度/维持"""
    line = f"{tag} {kind}: {text}" if kind != '维持' else f"{tag} 维持 {text}"
    prefix = f"{tag} {kind}"
    if hist and hist[-1].startswith(prefix):
        hist[-1] = line
    else:
        hist.append(line)
    return hist[-12:]


def update_allocation_status(report_text, views_path=None, anchors=None, today_str=None):
    """解析ALLOCATION_STATUS+PREDICTION_STATUS块回写观点库。

    第二轮修复:
    - 确信度单独变化也会落盘(独立history条目)
    - 评级变化与确信度变化分别记录
    - PREDICTION_STATUS裁决必须附note证据,否则拒绝该行
    - 新预测可附结构化规格(pred_metric/pred_op/pred_target),到期由引擎自动裁决
    - 到期且带规格的观察中预测,若GLM未裁决,按锚点自动裁决

    返回更新摘要列表。"""
    path = views_path or DEFAULT_VIEWS_PATH
    alloc_objs = _parse_status_block(report_text, 'ALLOCATION_STATUS')
    pred_objs = _parse_status_block(report_text, 'PREDICTION_STATUS')
    if not alloc_objs and not pred_objs:
        print("⚠️ 报告中未找到ALLOCATION_STATUS/PREDICTION_STATUS块,观点库未回写")
        return []

    if not os.path.exists(path):
        print(f"⚠️ 观点库不存在,无法回写: {path}")
        return []
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if _migrate_views(data):
        print("   视点库v1→v2迁移: 中性→标配 / open→observing等")

    today = datetime.strptime(today_str, '%Y-%m-%d') if today_str else datetime.now()
    today_iso = today.strftime('%Y-%m-%d')
    tag = f"{today.month}/{today.day}"
    updates = []
    valid_alloc_lines = 0

    # --- 观点评级回写(评级与确信度分别记录) ---
    for o in alloc_objs:
        vid = o.get('id')
        v = next((x for x in data.get('views', []) if x.get('id') == vid), None)
        if v is None:
            continue
        valid_alloc_lines += 1
        new_rating = str(o.get('rating', '')).strip()
        conf = o.get('confidence')
        note = str(o.get('note', '')).strip()[:60]

        rating_changed = False
        if new_rating in ALLOWED_RATINGS and new_rating != v.get('rating'):
            old = v.get('rating')
            v['rating'] = new_rating
            rating_changed = True
            updates.append(f"#{vid}{v['asset']}: 评级 {old}→{new_rating}")
            v['history'] = _hist_append(v.setdefault('history', []), tag, '评级', f"{old}→{new_rating} {note}".rstrip())

        conf_changed = False
        if isinstance(conf, (int, float)) and conf == int(conf) and 1 <= int(conf) <= 5:
            conf = int(conf)
            if conf != v.get('confidence'):
                old_c = v.get('confidence')
                v['confidence'] = conf
                conf_changed = True
                updates.append(f"#{vid}{v['asset']}: 确信度 {old_c}★→{conf}★")
                v['history'] = _hist_append(v.setdefault('history', []), tag, '确信度', f"{old_c}★→{conf}★ {note}".rstrip())

        if not rating_changed and not conf_changed:
            v['history'] = _hist_append(v.setdefault('history', []), tag, '维持',
                                        f"{v.get('rating','?')} {v.get('confidence',0)}★ {note}".rstrip())

        # 评级变更行附带pred → 自动登记新预测(有方向有期限才收;规格字段可选)
        if rating_changed and o.get('pred') and o.get('pred_weeks'):
            try:
                weeks = int(o['pred_weeks'])
            except (TypeError, ValueError):
                weeks = 0
            if weeks > 0:
                new_id = max([p.get('pred_id', 0) for p in data.get('predictions', [])] or [0]) + 1
                deadline = (today + timedelta(weeks=weeks)).strftime('%Y-%m-%d')
                entry = {
                    'pred_id': new_id,
                    'date_made': today_iso,
                    'asset': v['asset'],
                    'direction': str(o['pred']).strip()[:120],
                    'horizon_weeks': weeks,
                    'deadline': deadline,
                    'trigger': new_rating,
                    'status': 'observing',
                    'resolved_note': '',
                }
                # 第二轮#14: 机器可校验规格(指标ID+比较符+目标值),全且合法才存
                metric, op, target = o.get('pred_metric'), o.get('pred_op'), o.get('pred_target')
                if metric and op in COMPARATORS and isinstance(target, (int, float)):
                    entry['metric'] = str(metric)
                    entry['comparator'] = op
                    entry['target'] = float(target)
                    entry['evidence_ref'] = str(o.get('pred_evidence', '')).strip()[:80] or metric
                elif any((metric, op, target)):
                    print(f"   ⚠️ 预测#{new_id}规格不完整(metric/op/target),仅存文本形式(到期须人工裁决)")
                data.setdefault('predictions', []).append(entry)
                updates.append(f"新增预测#{new_id}({v['asset']}, 截止{deadline}"
                               + (f", 规格{entry.get('metric')} {entry.get('comparator')} {entry.get('target')}" if 'metric' in entry else ", 无量化规格") + ")")

    # --- 预测裁决回写(第二轮#12: 无证据的裁决拒绝) ---
    for o in pred_objs:
        pid = o.get('pred_id')
        p = next((x for x in data.get('predictions', []) if x.get('pred_id') == pid), None)
        if p is None:
            continue
        status = str(o.get('status', '')).strip().lower()
        status = _PRED_STATUS_MAP.get(status, status)
        note = str(o.get('note', '')).strip()
        if status in ALLOWED_PRED_VERDICTS and p.get('status') != status:
            if not note:
                print(f"   ⚠️ 预测#{pid}裁决'{status}'未附note证据,已拒绝(无证据不得裁决命中/证伪)")
                updates.append(f"预测#{pid}: 裁决被拒(无证据)")
                continue
            if status in ('hit', 'miss') and not re.search(r'[0-9]', note):
                print(f"   ⚠️ 预测#{pid}裁决note无具体数值('{note[:30]}'),已拒绝(证据须引用数值)")
                updates.append(f"预测#{pid}: 裁决被拒(note无数值)")
                continue
            old = p.get('status')
            p['status'] = status
            p['resolved_note'] = note[:120]
            p['resolved_date'] = today_iso
            updates.append(f"预测#{pid}: {old}→{status} ({note[:40]})")
        elif status == 'not_yet_triggered' and p.get('status') in ('observing', 'not_yet_triggered'):
            if not note:
                print(f"   ⚠️ 预测#{pid}'未触发'判定未附note说明,忽略")
                continue
            p['status'] = 'not_yet_triggered'
            p['resolved_note'] = note[:120]
            p['resolved_date'] = today_iso
            updates.append(f"预测#{pid}: →未触发 ({note[:40]})")
        elif status == 'observing' and p.get('status') == 'not_yet_triggered':
            # 前提条件兑现: 未触发→观察中(开始计时到期裁决)
            if not note:
                print(f"   ⚠️ 预测#{pid}'转观察中'未附note说明,忽略")
                continue
            p['status'] = 'observing'
            p['resolved_note'] = ''
            p.pop('resolved_date', None)
            updates.append(f"预测#{pid}: 未触发→观察中 ({note[:40]})")

    # --- 引擎自动裁决(GLM未裁决的到期可计算预测,第二轮#14) ---
    glm_verdicts = {o.get('pred_id') for o in pred_objs if str(o.get('status', '')).strip().lower()
                    in ('hit', 'miss', 'inconclusive', '命中', '已命中', '证伪', '已证伪', '无法裁决')}
    for pid, old, new, note in evaluate_predictions(data, anchors, today_iso):
        if pid in glm_verdicts:
            continue  # GLM已给出带证据裁决,以GLM为准
        p = next(x for x in data['predictions'] if x['pred_id'] == pid)
        p['status'], p['resolved_note'], p['resolved_date'] = new, note[:120], today_iso
        updates.append(f"预测#{pid}: {old}→{new} (引擎自动: {note[:50]})")

    # 第二轮#10修复: 只要解析到任何有效观点行/预测变更即落盘
    # (v1要求"评级变更"才写 → 仅确信度变化的周永远丢失)
    if not valid_alloc_lines and not updates:
        print("⚠️ 状态块无可识别内容,观点库未改动")
        return []

    data['last_updated'] = today_iso

    shutil.copy(path, path + '.bak')
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

    print(f"✅ allocation_views.json 已回写(备份: allocation_views.json.bak)")
    for u in updates:
        print(f"   {u}")
    return updates


if __name__ == '__main__':
    views = load_views()
    if views:
        print(render_views_block(views))
        due = due_predictions(views)
        print(f"\n到期待裁决: {len(due)} 条")
    else:
        sys.exit(1)
