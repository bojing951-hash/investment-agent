#!/usr/bin/env python3
"""研究数据来源绑定与质量门禁原语(IA-P0-1, 2026-10-27; FIX1整改 2026-10-27)

快照 → 数据包 → 锚点 → 报告 的可验证来源链(任务4):
- 确定性版本选择: 同日多版本快照(research_snapshot_YYYYMMDD[_vN].json)一律取
  **最高修订版**;任何候选损坏(JSON不可解析/缺snapshot_id)→明确拒绝,不得猜测
  回退低版本(不可判断=不可放行);
- Gate A三态语义(任务1): 缺gate_a字段/状态非法/快照不可解析一律**不得默认PASS**;
- 数据包与锚点旁挂meta sidecar(*.meta.json)记录来源快照/digest/Gate A状态,
  报告入口(任务5)与观察器(任务7)据此核验批次一致性;
- 门禁合成(任务6): 任一FAIL→FAIL;无FAIL有DEGRADED→DEGRADED;双PASS→PASS;
  未知状态按FAIL处理(保守)。

IA-P0-1-FIX1(2026-10-27第二轮整改)收紧:
- FIX-01 实际内容绑定: 摘要一律**读取实际文件后重算**(digest_file),不得信任
  sidecar声明值;锚点与权威快照做**确定性重建比对**(build_anchors为快照的
  纯函数——键集合/数值/残留指标任何偏差即拒绝);锚点prompt从已核验锚点重建比对;
- FIX-04 锚点指标质量门禁共享原语: quality缺失/非法/FAIL一律拒绝进入正式观察;
- FIX-05 Gate A声明一致性: 声明PASS但core_fail/core_missing非空、或核心事实
  实际FAIL、或与quality汇总冲突 → 拒绝放行(以注册表criticality为权威);
- FIX-06 快照身份核验: 物理文件名版本 ↔ 内部snapshot_id ↔ target_date必须
  互相匹配,内部声明与文件名冲突的候选整体拒绝。

设计约束: 纯本地文件实现,不引入数据库/服务/多Agent(约束九);轻量可离线测试。
"""
import glob
import hashlib
import json
import os
import re

GATES = ('PASS', 'DEGRADED', 'FAIL')
# 锚点指标合法质量状态(事实引擎词汇表): WARN为轻度提示,可记录
ANCHOR_QUALITY_OK = ('PASS', 'DEGRADED', 'WARN')

_CORE_CACHE = None


def core_metric_ids():
    """注册表核心指标ID集合(criticality=core且active)——Gate A分级的唯一权威。
    (FIX-05: 核心与否由注册表决定,不由调用方自行圈定;注册表加载失败→空集,
    调用方将得不到'核心'判定——宁可无法证明,不可虚报。)"""
    global _CORE_CACHE
    if _CORE_CACHE is None:
        try:
            import fact_engine as fe
            reg = fe.load_registry()
            _CORE_CACHE = frozenset(m['metric_id'] for m in reg['metrics']
                                    if m.get('criticality') == 'core'
                                    and m.get('status') == 'active')
        except Exception:
            _CORE_CACHE = frozenset()
    return _CORE_CACHE


# ══ Gate A 三态语义 ═══════════════════════════════════════════════

def gate_status(snapshot):
    """读取快照Gate A状态并核验声明一致性(FIX-05)。

    返回(status, reason);status=None 表示不可用——调用方不得将其当作PASS。
    除格式检查外,声明内容与事实质量矛盾时同样拒绝放行:
    - 声明PASS: core_fail/core_missing必须为空、核心事实不得有FAIL、
      quality汇总(如存在)不得非PASS——任何一条不满足=声明不可信,拒绝;
    - 声明DEGRADED: 不得同时存在core缺失/失败(core问题必须判FAIL,不得降级表述);
    - 声明FAIL: 一律阻断(保守侧),不再额外裁决。"""
    if not isinstance(snapshot, dict):
        return None, '快照不可解析(非JSON对象)'
    ga = snapshot.get('gate_a')
    if ga is None:
        return None, '快照缺gate_a字段(不得默认PASS)'
    status = ga.get('status') if isinstance(ga, dict) else ga
    if status not in GATES:
        return None, f'Gate A状态非法: {status!r}(合法值{GATES})'
    if not isinstance(ga, dict):
        ga = {'status': status}   # 裸字符串声明(兼容): 无core清单可查,仅格式裁决
    if status == 'PASS':
        if ga.get('core_fail'):
            return None, f"声明PASS但core_fail非空: {','.join(map(str, ga['core_fail'][:6]))}"
        if ga.get('core_missing'):
            return None, f"声明PASS但core_missing非空: {','.join(map(str, ga['core_missing'][:6]))}"
        q = snapshot.get('quality') or {}
        overall = q.get('overall')
        if overall in GATES and overall != 'PASS':
            return None, f'声明PASS但quality.overall={overall}(状态冲突)'
        # 以事实+注册表复核: 核心指标实际存在FAIL → 声明不可信
        core_ids = core_metric_ids()
        if core_ids:
            facts = snapshot.get('facts')
            if isinstance(facts, list):
                hidden = sorted(str(f.get('metric_id')) for f in facts
                                if isinstance(f, dict) and f.get('metric_id') in core_ids
                                and f.get('quality_status') == 'FAIL')
                if hidden:
                    return None, f"声明PASS但核心事实实际FAIL: {','.join(hidden[:6])}"
    elif status == 'DEGRADED':
        if ga.get('core_fail'):
            return None, f"声明DEGRADED但core_fail非空(应判FAIL): {','.join(map(str, ga['core_fail'][:6]))}"
        if ga.get('core_missing'):
            return None, (f"声明DEGRADED但core_missing非空(应判FAIL): "
                          f"{','.join(map(str, ga['core_missing'][:6]))}")
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
    - 任何候选损坏(不可解析/缺snapshot_id/target_date不符/内部身份与文件名版本
      冲突[IA-DEF-007]) → (None, 原因)——无法确认哪个版本有效时明确拒绝,不猜测回退;
    返回(snapshot_dict, path)或(None, reason)。"""
    cands = snapshot_candidates(ymd, daily_dir)
    if not cands:
        return None, f'无当日研究快照: research_snapshot_{ymd}*.json'
    bad = []
    snap_by_ver = {}
    for ver, p in cands:
        name = os.path.basename(p)
        try:
            with open(p, 'r', encoding='utf-8') as f:
                snap = json.load(f)
        except Exception as e:
            bad.append(f'{name} JSON不可解析({e})')
            continue
        if not isinstance(snap, dict) or not snap.get('snapshot_id'):
            bad.append(f'{name} 缺snapshot_id(非有效快照)')
            continue
        # FIX-06(IA-DEF-007): 物理文件名版本 ↔ 内部snapshot_id必须一致
        # (research_snapshot_D_v2.json 内部不得自称 research_snapshot_D)
        expected_id = f"research_snapshot_{ymd}" + (f"_v{ver}" if ver > 1 else "")
        if str(snap.get('snapshot_id')) != expected_id:
            bad.append(f'{name} 内部snapshot_id={snap.get("snapshot_id")!r}与文件名'
                       f'版本不符(应为{expected_id!r})')
            continue
        if str(snap.get('target_date')) != str(ymd):
            bad.append(f'{name} target_date={snap.get("target_date")}≠{ymd}')
            continue
        if ver in snap_by_ver:
            # FIX-06(IA-DEF-007): 同日重复版本号(两个_v2)——无法确定性选择,整体拒绝
            bad.append(f'同日重复版本号v{ver}: {name}与'
                       f'{os.path.basename(snap_by_ver[ver][1])}(拒绝猜测取哪个)')
            continue
        snap_by_ver[ver] = (snap, p)
    if bad:
        return None, ('快照候选存在损坏或身份冲突,无法确认有效版本(拒绝猜测): '
                      + '; '.join(bad))
    if not snap_by_ver:
        return None, f'当日快照候选全部无效: research_snapshot_{ymd}*.json'
    ver = max(snap_by_ver)
    snap, path = snap_by_ver[ver]
    return snap, path


def digest_snapshot(snapshot):
    """快照内容指纹(sha256前16位,canonical JSON)。用于数据包/报告与快照的
    精确绑定(同名快照文件被篡改时digest不匹配→拒绝)。"""
    blob = json.dumps(snapshot, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:16]


def digest_file(path):
    """文件**实际字节**指纹(sha256前16位)。FIX-01: 数据包/锚点/prompt的内容
    绑定必须读取实际文件重算,不得直接采用sidecar中声明的摘要值。"""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()[:16]


def _canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def anchor_quality_problem(info):
    """锚点指标质量门禁(FIX-04共享原语,观察器/状态引擎双侧同口径):
    返回None=可记录;返回问题描述=拒绝进入正式长期观察。
    FAIL→拒绝;quality缺失→拒绝(不得默认合格);非法值→拒绝。
    PASS/DEGRADED(已验证+披露)/WARN(轻度提示)可按既有规则处理。"""
    if not isinstance(info, dict):
        return '锚点记录非对象'
    q = info.get('quality')
    if q is None or str(q).strip() == '':
        return '锚点缺quality字段(不得默认合格进入正式观察)'
    qs = str(q).strip().upper()
    if qs == 'FAIL':
        return '锚点指标质量FAIL(事实引擎校验未通过)'
    if qs not in ANCHOR_QUALITY_OK:
        return f'锚点quality非法: {q!r}(合法值{ANCHOR_QUALITY_OK}或FAIL拒绝)'
    return None


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
    """核验锚点文件批次一致性+**实际内容**(FIX-01/FIX-04,IA-DEF-001/005)。

    核验链(任一环失败即拒绝,返回(False, reason);全部通过返回(True, '')):
    1. meta存在且source=snapshot(legacy/无meta/未知来源→拒绝——正式观察与
       报告输入必须可证明来源,FIX-04: 无来源证明不得进入正式长期观察);
    2. 声明批次 = 当日确定性选择的权威快照(snapshot_id一致,同日修订后旧批次失配);
    3. meta声明的快照digest与权威快照实际内容digest一致;
    4. meta声明的锚点内容摘要与锚点文件**实际字节**摘要一致(重算,不信任声明值);
    5. 锚点实际内容与权威快照**确定性重建**结果一致(build_anchors为快照纯函数:
       键集合/数值/高低点/观测日任何偏差、额外残留指标、版本混用均失配)。
    """
    anchors_path = str(anchors_path)
    meta = load_meta(anchors_path)
    if not meta:
        return False, (f'锚点无来源meta({os.path.basename(anchors_path)})——'
                       '来源不可证明,不得进入正式观察/报告(FIX-04)')
    src = str(meta.get('source') or '')
    if src == 'legacy':
        return False, ('锚点批次来源=legacy(原始采集JSON拍平,未经Gate A快照链验证),'
                       '不得用于正式观察/报告')
    if src != 'snapshot':
        return False, f'锚点meta来源未知: {src!r}'
    ymd = str(anchors_date or meta.get('target_date') or '')
    if not re.match(r'^\d{8}$', ymd):
        return False, f'锚点meta缺有效target_date: {ymd!r}'
    dd = daily_dir or os.path.dirname(anchors_path)
    snap, reason = select_snapshot(ymd, dd)
    if snap is None:
        return False, f'锚点声明的快照批次无法确认: {reason}'
    if snap.get('snapshot_id') != meta.get('snapshot_id'):
        return False, (f"数据批次不一致: 锚点绑定{meta.get('snapshot_id')},"
                       f"当日权威快照为{snap.get('snapshot_id')}(同日修订后旧锚点不得续用)")
    if meta.get('snapshot_digest') and meta.get('snapshot_digest') != digest_snapshot(snap):
        return False, ('锚点meta声明的快照digest与权威快照实际内容不一致'
                       '(快照被改写或meta陈旧)')
    if meta.get('anchors_digest') and meta.get('anchors_digest') != digest_file(anchors_path):
        return False, ('锚点实际内容与meta声明摘要不一致(疑被篡改/写入不完整)')
    # 确定性重建比对: 从权威快照重算锚点,与实际内容canonical比较
    try:
        import snapshot_builder as sb
        expected = sb.build_anchors(snap, ymd)
    except Exception as e:
        return False, f'锚点重建比对失败(无法证明内容一致): {e}'
    try:
        with open(anchors_path, 'r', encoding='utf-8') as f:
            actual = json.load(f)
    except Exception as e:
        return False, f'锚点文件不可读取: {e}'
    if not isinstance(actual, dict) or _canonical(actual) != _canonical(expected):
        extra = (sorted(set(actual) - set(expected))[:6] if isinstance(actual, dict) else [])
        detail = (f';实际多出残留键: {extra}' if extra else
                  (f';实际缺键{len(set(expected) - set(actual))}个'
                   if isinstance(actual, dict) else ''))
        return False, ('锚点实际内容与权威快照重建结果不一致'
                       '(数值被改/指标集合变动/残留旧指标/批次混用)' + detail)
    return True, ''


def verify_anchor_prompt(prompt_path, anchors):
    """锚点prompt实际内容核验(FIX-01): prompt由锚点确定性渲染
    (data_validator.generate_anchor_prompt_block为锚点纯函数),从**已核验**锚点
    重建并与文件实际内容比对——prompt中数字被替换/内容陈旧即拒绝。
    返回(ok, reason)。"""
    try:
        from data_validator import generate_anchor_prompt_block
    except Exception as e:
        return False, f'prompt渲染器不可用: {e}'
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            actual = f.read()
        expected = generate_anchor_prompt_block(anchors)
    except Exception as e:
        return False, f'prompt读取/重建失败: {e}'
    if actual.strip() != expected.strip():
        return False, ('锚点prompt实际内容与当日锚点重建结果不一致'
                       '(prompt被改写或锚点批次已变更)')
    return True, ''
