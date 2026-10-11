#!/usr/bin/env python3
"""配置研究引擎 v1.0 (P2/P3, 2026-10-11)

职责:
1. 渲染 config/allocation_views.json → 周报prompt的"配置观点块"(第五/七节引用)
2. 解析周报末尾 ALLOCATION_STATUS / PREDICTION_STATUS 块,回写观点库:
   - 评级/确信度变更 + history(留12条,同日重跑不重复记)
   - 评级变更行可附 "pred"(一句话预测)+"pred_weeks"(期限) → 自动新增待裁决预测
   - 到期预测由 PREDICTION_STATUS 行裁决(hit/miss/expired)
3. 硬约束: 评级≠仓位指令。回写与thesis同门禁——数值校验不过关由调用方(report_generator)跳过。

设计对齐 update_thesis_status: 备份 .bak + tmp/os.replace 原子写。
本模块不进launchd流水线,由 report_generator 每周五调用(周频=观点库更新频率)。
"""
import os
import sys
import re
import json
import shutil
from datetime import datetime, timedelta

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VIEWS_PATH = os.path.join(ROOT_DIR, 'config', 'allocation_views.json')

ALLOWED_RATINGS = {'超配', '标配', '中性', '低配', '观望'}
ALLOWED_PRED_STATUS = {'open', 'hit', 'miss', 'expired'}
# 容错: 模型可能输出中文状态
_PRED_STATUS_MAP = {'命中': 'hit', '验证': 'hit', '证伪': 'miss', '落空': 'miss',
                    '过期': 'expired', '延续': 'open', '观察': 'open'}


def load_views(views_path=None):
    path = views_path or DEFAULT_VIEWS_PATH
    if not os.path.exists(path):
        print(f"⚠️ 观点库不存在: {path}")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def due_predictions(views_data, today_str=None):
    """已过deadline仍open的预测 → 周报须在本期给出命中/证伪裁决"""
    today = today_str or datetime.now().strftime('%Y-%m-%d')
    return [p for p in views_data.get('predictions', [])
            if p.get('status') == 'open' and p.get('deadline', '9999-99-99') <= today]


def render_views_block(views_data, today_str=None):
    """观点库 → prompt文本块(资产评级表 + 待裁决预测)"""
    if not views_data:
        return "(观点库缺失,本周跳过配置观点)"
    lines = ["(评级为相对观点而非仓位指令;星级不直接推导仓位)"]
    lines.append("| 资产 | 评级 | 确信度 | 核心理由 | 升级触发 | 降级触发 |")
    lines.append("|------|------|--------|----------|----------|----------|")
    for v in views_data.get('views', []):
        stars = "★" * v.get('confidence', 0)
        trig = v.get('triggers', {})
        lines.append(f"| {v['asset']} | {v.get('rating','?')} | {stars} | "
                     f"{v.get('rationale','')[:40]}… | {trig.get('upgrade','')[:30]} | {trig.get('downgrade','')[:30]} |")

    preds = views_data.get('predictions', [])
    if preds:
        lines.append("")
        lines.append("### 预测跟踪(P3)")
        due = {p['pred_id'] for p in due_predictions(views_data, today_str)}
        for p in preds:
            mark = "⏰已到期,本周必须裁决" if p['pred_id'] in due else ""
            lines.append(f"- [#{p['pred_id']}][{p.get('status')}] {p['asset']}: "
                         f"{p['direction'][:60]} (截止{p.get('deadline','?')}) {mark}")
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


def update_allocation_status(report_text, views_path=None):
    """解析ALLOCATION_STATUS+PREDICTION_STATUS块回写观点库。返回更新摘要列表。"""
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

    today = datetime.now()
    tag = f"{today.month}/{today.day}"
    updates = []

    # --- 观点评级回写 ---
    for o in alloc_objs:
        vid = o.get('id')
        v = next((x for x in data.get('views', []) if x.get('id') == vid), None)
        if v is None:
            continue
        new_rating = str(o.get('rating', '')).strip()
        conf = o.get('confidence')
        note = str(o.get('note', '')).strip()[:60]

        rating_changed = False
        if new_rating in ALLOWED_RATINGS and new_rating != v.get('rating'):
            v['rating'] = new_rating
            rating_changed = True
            updates.append(f"#{vid}{v['asset']}: 评级→{new_rating}")
        if isinstance(conf, (int, float)) and conf == int(conf) and 1 <= int(conf) <= 5:
            v['confidence'] = int(conf)

        hist = v.setdefault('history', [])
        if hist and hist[-1].startswith(f"{tag} "):
            hist[-1] = f"{tag} {v.get('rating','?')} {v.get('confidence',0)}★ {note}".rstrip()
        else:
            hist.append(f"{tag} {v.get('rating','?')} {v.get('confidence',0)}★ {note}".rstrip())
        v['history'] = hist[-12:]

        # P3: 评级变更行附带pred → 自动登记新预测(有方向有期限才收)
        if rating_changed and o.get('pred') and o.get('pred_weeks'):
            try:
                weeks = int(o['pred_weeks'])
            except (TypeError, ValueError):
                weeks = 0
            if weeks > 0:
                new_id = max([p.get('pred_id', 0) for p in data.get('predictions', [])] or [0]) + 1
                deadline = (today + timedelta(weeks=weeks)).strftime('%Y-%m-%d')
                data.setdefault('predictions', []).append({
                    'pred_id': new_id,
                    'date_made': today.strftime('%Y-%m-%d'),
                    'asset': v['asset'],
                    'direction': str(o['pred']).strip()[:120],
                    'horizon_weeks': weeks,
                    'deadline': deadline,
                    'trigger': new_rating,
                    'status': 'open',
                    'resolved_note': ''
                })
                updates.append(f"新增预测#{new_id}({v['asset']}, 截止{deadline})")

    # --- 预测裁决回写 ---
    for o in pred_objs:
        pid = o.get('pred_id')
        p = next((x for x in data.get('predictions', []) if x.get('pred_id') == pid), None)
        if p is None:
            continue
        status = str(o.get('status', '')).strip().lower()
        status = _PRED_STATUS_MAP.get(status, status)
        if status in ALLOWED_PRED_STATUS and p.get('status') != status:
            old = p.get('status')
            p['status'] = status
            p['resolved_note'] = str(o.get('note', '')).strip()[:80]
            p['resolved_date'] = today.strftime('%Y-%m-%d')
            updates.append(f"预测#{pid}: {old}→{status}")

    if not updates:
        print("⚠️ 状态块无可识别的变更,观点库未改动")
        return []

    data['last_updated'] = today.strftime('%Y-%m-%d')

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
