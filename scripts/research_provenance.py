#!/usr/bin/env python3
"""研究数据来源绑定与质量门禁原语(IA-P0-1, 2026-10-27; FIX1整改 2026-10-27;
FIX2整改 2026-10-27)

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

IA-P0-1-FIX2(2026-10-27第三轮整改)收紧:
- FIX2-02(IA-DEF-002) Gate A从**真实事实重算**: recompute_gate_a以注册表
  active+core集合与快照实际facts为唯一权威,重算核心缺失/核心FAIL/非核心失败/
  重复metric_id/非法质量/计数,gate_status据此裁决声明一致性——声明DEGRADED但
  核心实际FAIL、声明PASS但核心实际缺失且未写入core_missing等矛盾一律拒绝;
- FIX2-04(IA-DEF-004) 版本表示唯一化: 仅接受base(无后缀)与_v2及以上**规范
  十进制**(_v0/_v1/_v00/_v01等一律非法→整日拒绝),保留最高修订版选择规则;
- FIX2-05(IA-DEF-005) 来源元数据必需字段完整一致: verify_anchor_batch要求
  meta日期↔请求日期↔文件名日期一致、必需摘要存在且与实际字节一致、
  meta.gate_a与权威重算一致——缺失即拒绝,不再"缺字段跳过校验"。

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

# 事实质量合法词汇表(事实引擎grade_issues产出;WARN为轻度提示,counts不计)
FACT_QUALITY = ('PASS', 'WARN', 'DEGRADED', 'FAIL')


def recompute_gate_a(snapshot):
    """从**真实事实+注册表**重算Gate A裁决(IA-P0-1-FIX2/FIX2-02权威口径)。

    不信任快照内任何声明字段——以注册表status=active且criticality=core集合与
    facts实际内容重算:
    - core_missing: 核心指标无事实记录(含质量非法——不可证明≠有效存在);
    - core_fail: 核心事实quality=FAIL;
    - noncore_fail/noncore_degraded: 非核心事实FAIL/DEGRADED(按既有规则降级披露);
    - duplicates: 同一metric_id出现多条事实(数据身份冲突→FAIL);
    - illegal_quality: 质量状态缺失/非法(不得默认有效;核心→FAIL,非核心→降级);
    - counts: 按事实引擎口径重计(仅PASS/DEGRADED/FAIL三键,WARN不计——与
      fact_engine.snapshot_quality_grade完全同构);
    - effective: FAIL(core缺失/失败/身份冲突)>DEGRADED(非核心失败/降级)>PASS。

    返回dict;snapshot结构损坏或注册表不可用时 effective=None并在reasons说明
    (调用方不得当作任何放行状态)。
    """
    out = {'core_missing': [], 'core_fail': [], 'noncore_fail': [],
           'noncore_degraded': [], 'duplicates': [], 'illegal_quality': [],
           'counts': {'PASS': 0, 'DEGRADED': 0, 'FAIL': 0}, 'overall': 'PASS',
           'effective': None, 'reasons': []}
    if not isinstance(snapshot, dict):
        out['reasons'].append('快照不可解析(非JSON对象)')
        return out
    facts = snapshot.get('facts')
    if not isinstance(facts, list):
        out['reasons'].append(f'facts非列表: {type(facts).__name__}')
        return out
    core_ids = core_metric_ids()
    if not core_ids:
        # 注册表不可用→无法证明核心集合(宁可无法证明,不可虚报)
        out['reasons'].append('注册表不可用——无法重算核心集合(不得放行)')
        return out
    by_id, seen_dup = {}, set()
    for f in facts:
        if not isinstance(f, dict):
            out['illegal_quality'].append('<非对象事实>')
            continue
        mid = f.get('metric_id')
        if mid in by_id:
            seen_dup.add(str(mid))
            continue
        by_id[mid] = f
        qs = f.get('quality_status')
        if qs not in FACT_QUALITY:
            out['illegal_quality'].append(f"{mid}={qs!r}")
        elif qs in ('PASS', 'DEGRADED', 'FAIL'):
            out['counts'][qs] += 1
    out['duplicates'] = sorted(seen_dup)
    for mid in core_ids:
        f = by_id.get(mid)
        if f is None:
            out['core_missing'].append(mid)
        elif f.get('quality_status') == 'FAIL':
            out['core_fail'].append(mid)
        elif f.get('quality_status') not in FACT_QUALITY:
            out['core_fail'].append(mid)   # 核心质量不可证明=不可放行(并入core_fail口径)
    for mid, f in by_id.items():
        if mid in core_ids:
            continue
        qs = f.get('quality_status')
        if qs == 'FAIL' or qs not in FACT_QUALITY:
            out['noncore_fail'].append(str(mid))
        elif qs == 'DEGRADED':
            out['noncore_degraded'].append(str(mid))
    out['core_missing'].sort(); out['core_fail'].sort()
    out['noncore_fail'].sort(); out['noncore_degraded'].sort()
    c = out['counts']
    out['overall'] = ('FAIL' if c['FAIL'] else 'DEGRADED' if c['DEGRADED'] else 'PASS')
    if out['core_missing'] or out['core_fail'] or out['duplicates']:
        out['effective'] = 'FAIL'
    elif c['DEGRADED'] or out['noncore_fail'] or out['noncore_degraded']:
        out['effective'] = 'DEGRADED'
    else:
        out['effective'] = 'PASS'
    return out


def gate_status(snapshot):
    """读取快照Gate A状态并以**事实重算**裁决声明一致性
    (IA-P0-1-FIX1 FIX-05 + IA-P0-1-FIX2 FIX2-02收紧)。

    返回(status, reason);status=None 表示不可用——调用方不得将其当作PASS。
    裁决链(任一环失败→None):
    1. 格式: 缺gate_a/状态非法/快照不可解析 → None;
    2. 重算: recompute_gate_a从真实事实+注册表重算权威裁决;结构损坏/注册表
       不可用 → None;
    3. 一致性(声明↔重算,任何矛盾=声明不可信→拒绝放行):
       - 声明状态 ≠ 重算effective(如声明DEGRADED但核心实际FAIL、声明PASS但
         核心实际缺失) → None;
       - 声明core_missing/core_fail清单与重算清单不一致(如核心缺失未写入
         core_missing) → None;
       - quality.counts(如存在)与按事实重计不一致 → None;
       - quality.overall(如存在)与重计不一致 → None。
    语义说明(不机械要求overall==status): quality.overall=**全部事实中最严重的
    原始质量等级**(fact_engine.snapshot_quality_grade,非核心FAIL也会拉高它),
    gate_a.status=**是否允许正式研究**(非核心FAIL仅降级)——二者语义不同,
    不直接互比;各自的**声明值**都必须与其自身的重算结果一致。"""
    if not isinstance(snapshot, dict):
        return None, '快照不可解析(非JSON对象)'
    ga = snapshot.get('gate_a')
    if ga is None:
        return None, '快照缺gate_a字段(不得默认PASS)'
    status = ga.get('status') if isinstance(ga, dict) else ga
    if status not in GATES:
        return None, f'Gate A状态非法: {status!r}(合法值{GATES})'
    rec = recompute_gate_a(snapshot)
    if rec['effective'] is None:
        return None, '; '.join(rec['reasons']) or '重算不可用'
    if status != rec['effective']:
        why = []
        if rec['core_missing']:
            why.append(f"核心实际缺失{len(rec['core_missing'])}项"
                       f"({','.join(rec['core_missing'][:4])})")
        if rec['core_fail']:
            why.append(f"核心实际FAIL: {','.join(rec['core_fail'][:4])}")
        if rec['duplicates']:
            why.append(f"重复metric_id: {','.join(rec['duplicates'][:4])}")
        if not why:
            why.append(f"重算为{rec['effective']}")
        return None, (f'声明{status}与事实重算{rec["effective"]}不一致——'
                      + '; '.join(why))
    if isinstance(ga, dict):
        for field, actual, label in (('core_missing', rec['core_missing'], '核心缺失'),
                                     ('core_fail', rec['core_fail'], '核心失败')):
            declared = ga.get(field)
            if declared is None:
                continue
            if sorted(map(str, declared)) != actual:
                return None, (f'声明{label}({field})清单与事实重算不一致: '
                              f'声明{sorted(map(str, declared))[:6]} '
                              f'实际{actual[:6]}')
    q = snapshot.get('quality')
    if isinstance(q, dict):
        if isinstance(q.get('counts'), dict):
            recounted = {k: q['counts'].get(k) for k in ('PASS', 'DEGRADED', 'FAIL')}
            if recounted != rec['counts']:
                return None, (f"quality.counts与事实重计不一致: 声明{q['counts']} "
                              f"实际{rec['counts']}")
        if q.get('overall') in GATES and q['overall'] != rec['overall']:
            return None, (f"quality.overall声明{q['overall']}与事实重计"
                          f"{rec['overall']}不一致")
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
    """research_snapshot_YYYYMMDD[_vN].json → (ymd, N);base版N=1。非匹配→None。

    IA-P0-1-FIX2(FIX2-04)版本表示唯一化: 修订版仅接受_v2及以上的**规范十进制**
    (无前导零);_v0/_v1/_v00/_v01等非规范表示一律判非法(返回(ymd, None)),
    由选择器整体拒绝当日——可疑候选不得静默忽略后继续选其他版本。"""
    m = re.match(r'research_snapshot_(\d{8})(?:_v(\d+))?\.json$',
                 os.path.basename(path))
    if not m:
        return None
    ymd, vs = m.group(1), m.group(2)
    if vs is None:
        return ymd, 1
    if vs != str(int(vs)) or int(vs) < 2:   # 前导零/0/1 → 非法版本表示
        return ymd, None
    return ymd, int(vs)


def snapshot_candidates(ymd, daily_dir):
    """当日全部快照候选,按版本升序[(版本号, 路径)]。

    非法版本表示(_v0/_v1/_v00等)同样列为候选(版本号None)——选择器必须
    对其整日拒绝,不得当作不存在。"""
    out = []
    for p in glob.glob(os.path.join(str(daily_dir), 'research_snapshot_*.json')):
        v = _version_of(p)
        if v and v[0] == str(ymd):
            out.append((v[1], p))
    return sorted(out, key=lambda t: (t[0] is None, t[0] if t[0] is not None else 0))


def select_snapshot(ymd, daily_dir):
    """确定性选择当日权威快照: 取**最高修订版**(修订版是显式修正,晚于base)。

    - 无候选 → (None, 原因);
    - 任何候选损坏(不可解析/缺snapshot_id/target_date不符/内部身份与文件名版本
      冲突[IA-DEF-007]/**非法版本表示_v0/_v1/_v00[FIX2-04]**/同日重复版本号)
      → (None, 原因)——无法确认哪个版本有效时明确拒绝,不猜测回退,
      可疑候选不得静默忽略后继续选择其他版本;
    返回(snapshot_dict, path)或(None, reason)。"""
    cands = snapshot_candidates(ymd, daily_dir)
    if not cands:
        return None, f'无当日研究快照: research_snapshot_{ymd}*.json'
    bad = []
    snap_by_ver = {}
    for ver, p in cands:
        name = os.path.basename(p)
        if ver is None:
            bad.append(f'{name} 非法版本表示(合法: 无后缀base或_v2及以上规范十进制)')
            continue
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
        return None, ('快照候选存在损坏/非法版本/身份冲突,无法确认有效版本(拒绝猜测): '
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
    """核验锚点文件批次一致性+**实际内容**(FIX-01/FIX-04,IA-DEF-001/005;
    FIX2-05必需字段完整一致)。

    核验链(任一环失败即拒绝,返回(False, reason);全部通过返回(True, '')):
    1. meta存在且source=snapshot(legacy/无meta/未知来源→拒绝——正式观察与
       报告输入必须可证明来源,FIX-04: 无来源证明不得进入正式长期观察);
    2. 日期三方一致(FIX2-05): 请求日期(anchors_date,如给)↔meta.target_date↔
       锚点**文件名**日期——meta自报错误日期/文件名与批次日期不符均拒绝
       (旧实现`anchors_date or meta.target_date`在调用方传日期时跳过meta日期核对);
    3. 必需来源字段完整(FIX2-05): snapshot_id/snapshot_digest/anchors_digest/
       gate_a缺一即拒——必需摘要缺失=无法验证内容,不得"缺字段跳过校验";
    4. 声明批次 = 当日确定性选择的权威快照(snapshot_id一致,同日修订后旧批次失配);
       meta.gate_a与权威快照重算Gate A一致;
    5. meta声明的快照digest与权威快照实际内容digest一致;
       meta声明的锚点内容摘要与锚点文件**实际字节**摘要一致(重算,不信任声明值);
    6. 锚点实际内容与权威快照**确定性重建**结果一致(build_anchors为快照纯函数:
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
    # FIX2-05: 日期三方一致——meta必须自带target_date,且与请求日期/文件名一致
    meta_ymd = str(meta.get('target_date') or '')
    if not re.match(r'^\d{8}$', meta_ymd):
        return False, f'锚点meta缺target_date(必需来源字段): {meta_ymd!r}'
    ymd = meta_ymd
    if anchors_date is not None and str(anchors_date) != ymd:
        return False, (f'锚点meta日期与请求日期冲突: meta={ymd} '
                       f'请求={anchors_date}(批次来源不可信)')
    fname = os.path.basename(anchors_path)
    if fname != f'anchors_{ymd}.json':
        return False, f'锚点文件名日期与批次日期不符: {fname} ≠ anchors_{ymd}.json'
    # FIX2-05: 必需来源字段——缺失即拒(不得跳过对应校验)
    for field in ('snapshot_id', 'snapshot_digest', 'anchors_digest', 'gate_a'):
        if meta.get(field) in (None, ''):
            return False, f'锚点meta缺必需来源字段: {field}(无法验证来源与内容)'
    dd = daily_dir or os.path.dirname(anchors_path)
    snap, reason = select_snapshot(ymd, dd)
    if snap is None:
        return False, f'锚点声明的快照批次无法确认: {reason}'
    if snap.get('snapshot_id') != meta.get('snapshot_id'):
        return False, (f"数据批次不一致: 锚点绑定{meta.get('snapshot_id')},"
                       f"当日权威快照为{snap.get('snapshot_id')}(同日修订后旧锚点不得续用)")
    auth_gate, gate_reason = gate_status(snap)
    if meta.get('gate_a') != auth_gate:
        return False, (f'锚点meta.gate_a={meta.get("gate_a")!r}与权威快照Gate A='
                       f'{auth_gate!r}不一致(批次生成后被改写或meta陈旧)'
                       + (f';{gate_reason}' if gate_reason else ''))
    if auth_gate not in ('PASS', 'DEGRADED'):
        return False, f'权威快照Gate A={auth_gate!r}不允许正式观察({gate_reason})'
    if meta.get('snapshot_digest') != digest_snapshot(snap):
        return False, ('锚点meta声明的快照digest与权威快照实际内容不一致'
                       '(快照被改写或meta陈旧)')
    if meta.get('anchors_digest') != digest_file(anchors_path):
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
