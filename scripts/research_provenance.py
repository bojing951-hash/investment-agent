#!/usr/bin/env python3
"""研究数据来源绑定与质量门禁原语(IA-P0-1, 2026-10-27)

快照 → 数据包 → 锚点 → 报告 的可验证来源链(任务4):
- 确定性版本选择: 同日多版本快照(research_snapshot_YYYYMMDD[_vN].json)一律取
  **最高修订版**;任何候选损坏(JSON不可解析/缺snapshot_id)→明确拒绝,不得猜测
  回退低版本(不可判断=不可放行);
- Gate A三态语义(任务1): 缺gate_a字段/状态非法/快照不可解析一律**不得默认PASS**;
- 数据包与锚点旁挂meta sidecar(*.meta.json)记录来源快照/digest/Gate A状态,
  报告入口(任务5)与观察器(任务7)据此核验批次一致性;
- 门禁合成(任务6): 任一FAIL→FAIL;无FAIL有DEGRADED→DEGRADED;双PASS→PASS;
  未知状态按FAIL处理(保守)。

设计约束: 纯本地文件实现,不引入数据库/服务/多Agent(约束九);轻量可离线测试。
"""
import glob
import hashlib
import json
import os
import re

GATES = ('PASS', 'DEGRADED', 'FAIL')


# ══ Gate A 三态语义 ═══════════════════════════════════════════════

def gate_status(snapshot):
    """读取快照Gate A状态。返回(status, reason):
    status=None 表示不可用(缺字段/非法/快照非对象)——调用方不得将其当作PASS。"""
    if not isinstance(snapshot, dict):
        return None, '快照不可解析(非JSON对象)'
    ga = snapshot.get('gate_a')
    if ga is None:
        return None, '快照缺gate_a字段(不得默认PASS)'
    status = ga.get('status') if isinstance(ga, dict) else ga
    if status not in GATES:
        return None, f'Gate A状态非法: {status!r}(合法值{GATES})'
    return status, ''


def gate_allows_formal_research(status):
    """Gate A允许进入正式研究流程的状态: PASS(正常)/DEGRADED(披露降级)。
    FAIL/None/未知 → False(不得生成合格正式数据包/报告)。"""
    return status in ('PASS', 'DEGRADED')


def gate_reason_desc(snapshot):
    """人读的降级/失败原因摘要(供拒绝信息与披露用)。"""
    if not isinstance(snapshot, dict):
        return '快照不可解析'
    ga = snapshot.get('gate_a') or {}
    parts = []
    if ga.get('core_missing'):
        parts.append('core缺失: ' + ','.join(ga['core_missing'][:8]))
    if ga.get('core_fail'):
        parts.append('core失败: ' + ','.join(ga['core_fail'][:8]))
    q = (snapshot.get('quality') or {}).get('counts') or {}
    if q.get('DEGRADED'):
        parts.append(f"DEGRADED事实{q['DEGRADED']}项")
    if q.get('FAIL'):
        parts.append(f"FAIL事实{q['FAIL']}项")
    return '; '.join(parts) or '未注明'


# ══ 确定性快照版本选择(任务3/任务4) ══════════════════════════════

def _version_of(path):
    """research_snapshot_YYYYMMDD[_vN].json → (ymd, N);base版N=1。非匹配→None。"""
    m = re.match(r'research_snapshot_(\d{8})(?:_v(\d+))?\.json$',
                 os.path.basename(path))
    if not m:
        return None
    return m.group(1), int(m.group(2) or 1)


def snapshot_candidates(ymd, daily_dir):
    """当日全部快照候选,按版本升序[(版本号, 路径)]。"""
    out = []
    for p in glob.glob(os.path.join(str(daily_dir), 'research_snapshot_*.json')):
        v = _version_of(p)
        if v and v[0] == str(ymd):
            out.append((v[1], p))
    return sorted(out)


def select_snapshot(ymd, daily_dir):
    """确定性选择当日权威快照: 取**最高修订版**(修订版是显式修正,晚于base)。

    - 无候选 → (None, 原因);
    - 任何候选损坏(不可解析/缺snapshot_id/target_date不符) → (None, 原因)
      ——无法确认哪个版本有效时明确拒绝,不猜测回退;
    返回(snapshot_dict, path)或(None, reason)。"""
    cands = snapshot_candidates(ymd, daily_dir)
    if not cands:
        return None, f'无当日研究快照: research_snapshot_{ymd}*.json'
    bad = []
    snap_by_ver = {}
    for ver, p in cands:
        try:
            with open(p, 'r', encoding='utf-8') as f:
                snap = json.load(f)
        except Exception as e:
            bad.append(f'{os.path.basename(p)} JSON不可解析({e})')
            continue
        if not isinstance(snap, dict) or not snap.get('snapshot_id'):
            bad.append(f'{os.path.basename(p)} 缺snapshot_id(非有效快照)')
            continue
        snap_by_ver[ver] = (snap, p)
    if bad:
        return None, ('快照候选存在损坏,无法确认有效版本(拒绝猜测): ' + '; '.join(bad))
    ver = max(snap_by_ver)
    snap, path = snap_by_ver[ver]
    if str(snap.get('target_date')) != str(ymd):
        return None, (f'快照target_date({snap.get("target_date")})≠目标日期{ymd}'
                      f'({os.path.basename(path)})')
    return snap, path


def digest_snapshot(snapshot):
    """快照内容指纹(sha256前16位,canonical JSON)。用于数据包/报告与快照的
    精确绑定(同名快照文件被篡改时digest不匹配→拒绝)。"""
    blob = json.dumps(snapshot, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:16]


def provenance_of(snapshot, path=None):
    """快照来源元数据(写入数据包/锚点/报告status sidecar)。"""
    status, _reason = gate_status(snapshot)
    return {
        'snapshot_id': snapshot.get('snapshot_id') if isinstance(snapshot, dict) else None,
        'snapshot_file': os.path.basename(path) if path else None,
        'target_date': snapshot.get('target_date') if isinstance(snapshot, dict) else None,
        'research_as_of': snapshot.get('research_as_of') if isinstance(snapshot, dict) else None,
        'gate_a': status,
        'snapshot_digest': digest_snapshot(snapshot) if isinstance(snapshot, dict) else None,
    }


# ══ meta sidecar(数据包/锚点旁挂来源元数据) ═════════════════════

def meta_path_for(json_path):
    """anchors_YYYYMMDD.json → anchors_YYYYMMDD.meta.json;
    data_pack_YYYYMMDD.md → data_pack_YYYYMMDD.meta.json(去扩展名+旁挂)。"""
    root, _ = os.path.splitext(str(json_path))
    return root + '.meta.json'


def write_meta(json_path, meta):
    """原子写meta sidecar(先tmp后replace,防半写状态)。"""
    mp = meta_path_for(json_path)
    tmp = mp + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    os.replace(tmp, mp)
    return mp


def load_meta(json_path):
    """读取meta sidecar;不存在/损坏返回None(调用方按'无来源元数据'处理)。"""
    mp = meta_path_for(json_path)
    if not os.path.exists(mp):
        return None
    try:
        with open(mp, 'r', encoding='utf-8') as f:
            m = json.load(f)
        return m if isinstance(m, dict) else None
    except Exception:
        return None


# ══ Gate A / Gate B 合成(任务6) ═════════════════════════════════

def combine_gates(gate_a, gate_b):
    """正式报告最终质量等级(确定性规则):
    任一门禁FAIL(或状态未知/非法)→FAIL;无FAIL但有DEGRADED→DEGRADED;
    两门禁全PASS→PASS。未知状态按FAIL处理——不得默认通过。"""
    if gate_a not in GATES or gate_b not in GATES:
        return 'FAIL'
    if 'FAIL' in (gate_a, gate_b):
        return 'FAIL'
    if 'DEGRADED' in (gate_a, gate_b):
        return 'DEGRADED'
    return 'PASS'


# ══ 锚点批次核验(观察器/报告入口共用) ═══════════════════════════

def verify_anchor_batch(anchors_path, anchors_date=None, daily_dir=None):
    """核验锚点文件的批次一致性(任务7'数据批次一致'):
    - meta缺失 → (None, 'no_meta'): 旧格式/直连测试路径,由调用方按既有规则处理;
    - meta.source=legacy(原始采集JSON拍平) → 拒绝(未经Gate A快照链验证);
    - meta.source=snapshot → 须与该日确定性选择的最高版本快照一致(同日修订后
      旧锚点自动失配→拒绝)。
    返回(ok: bool|None, reason)。ok=None表示无meta(调用方自行决定)。"""
    meta = load_meta(anchors_path)
    if not meta:
        return None, f'无来源meta({os.path.basename(str(anchors_path))})'
    src = str(meta.get('source') or '')
    if src == 'legacy':
        return False, ('锚点批次来源=legacy(原始采集JSON拍平,未经Gate A快照链验证),'
                       '不得用于正式观察/报告')
    if src != 'snapshot':
        return False, f'锚点meta来源未知: {src!r}'
    ymd = str(anchors_date or meta.get('target_date') or '')
    if not re.match(r'^\d{8}$', ymd):
        return False, f'锚点meta缺有效target_date: {ymd!r}'
    dd = daily_dir or os.path.dirname(str(anchors_path))
    snap, reason = select_snapshot(ymd, dd)
    if snap is None:
        return False, f'锚点声明的快照批次无法确认: {reason}'
    if snap.get('snapshot_id') != meta.get('snapshot_id'):
        return False, (f"数据批次不一致: 锚点绑定{meta.get('snapshot_id')},"
                       f"当日权威快照为{snap.get('snapshot_id')}(同日修订后旧锚点不得续用)")
    return True, ''
