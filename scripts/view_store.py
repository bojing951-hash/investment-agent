#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""机构观点存储(Charter 8 交付①)——装载+linter,零写入。

存储约定:
  data/institutions/views/VIEW-YYYYMMDD-NNN.json  每份报告一文件
  view_id = 文件名主干(如 VIEW-20261110-001);装载时强校验文件名==view_id。

schema v1.1 铁律(与 B 席采集 agent 对齐,字段名一个不能差;v1.1=2026-11-10
  协调仲裁升级: quote 由"仅 verbatim 时填"放宽为**任意 basis 可附原文佐证**
  ——paraphrase+原文佐证严格优于纯 paraphrase,可核查性增强,红线不弱化;
  装载只认单一版本 "1.1",不做 1.0 向后兼容):
  顶层必填: schema_version/view_id/institution{name,type,department}/authors[]/
    report_title/source_url/source_type/publish_date/fetch_date/access_level/
    view_horizon/subjects[]/core_views/forecasts/key_assumptions/evidence_cited/
    mechanism_steps/risk_factors/falsification_conditions/revisions/
    completeness_notes/copyright_note
  枚举: institution.type ∈ INSTITUTION_TYPES; source_type ∈ SOURCE_TYPES;
    access_level ∈ ACCESS_LEVELS; view_horizon ∈ VIEW_HORIZONS;
    条目 attribution ∈ ATTRIBUTIONS(机构明示 institution_stated vs AI 推导
    ai_inferred——章程核心红线,linter 硬性拦截缺失与非法值);
    core_views[].basis ∈ BASES。
  日期: publish_date ≤ fetch_date(ISO YYYY-MM-DD);
  core_views 非空;quote(若填)=非空字符串且 ≤500 字符,任意 basis 可附
  原文佐证;basis=verbatim_quote 时 quote **强制必填**
  (存储只存元数据+短引文+链接,禁整篇转载);
  falsification_conditions[] 每条 {condition, attribution}
  (v1.0→1.1 定稿更名 statement→condition,仲裁漂移3);
  revisions[] 每条 {date,change,source_url} 三键齐(章程§4.3 版本管理核心:
  date=上期版发布日,change=具体变更,source_url=上期版或本期 URL;
  只追加纪律: 本模块零写入,任何修订由 B 席追加新条目,不覆写历史条目;
  无真实修订信息的档 revisions 留空数组+completeness_notes 说明)。

lint 违规 → 隔离(quarantined)不装载: load_views 只返回合规件;违规件
带逐条违规清单返回,绝不静默丢弃也不降级装载。

运行(离线): python3 scripts/view_store.py lint|list [目录]
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEWS_DIR = os.path.join(ROOT, 'data', 'institutions', 'views')

SCHEMA_VERSION = '1.1'   # 单一版本纪律: 装载只认 1.1(仲裁 2026-11-10),不向后兼容 1.0
VIEW_FILE_RE = re.compile(r'^VIEW-(\d{8})-(\d{3})$')

INSTITUTION_TYPES = ('investment_bank', 'asset_manager',
                     'fixed_income_macro_strategy', 'hedge_fund',
                     'international_org', 'central_bank', 'other')
SOURCE_TYPES = ('official_site', 'official_summary_page', 'third_party_summary')
ACCESS_LEVELS = ('public_full', 'public_summary', 'headline_only')
VIEW_HORIZONS = ('3m', '6m', '12m', '18m', 'other')
ATTRIBUTIONS = ('institution_stated', 'ai_inferred')
BASES = ('verbatim_quote', 'paraphrase', 'derived')

TOP_REQUIRED = ('schema_version', 'view_id', 'institution', 'authors',
                'report_title', 'source_url', 'source_type', 'publish_date',
                'fetch_date', 'access_level', 'view_horizon', 'subjects',
                'core_views', 'forecasts', 'key_assumptions', 'evidence_cited',
                'mechanism_steps', 'risk_factors', 'falsification_conditions',
                'revisions', 'completeness_notes', 'copyright_note')

QUOTE_MAX_CHARS = 500
KNOWN_SUBJECTS = ('US_rates', 'US_growth', 'CN_macro', 'EA_macro', 'JP_macro',
                  'HK_macro', 'equities', 'fixed_income', 'fx', 'commodities',
                  'credit')


def _iso_ok(s):
    return (isinstance(s, str) and re.match(r'^\d{4}-\d{2}-\d{2}$', s)
            and len(s) == 10)


def lint_view(doc, filename=None):
    """lint 单份观点档(纯函数,零 IO)。返回违规列表;空列表=合规。

    每条违规: {'field', 'rule', 'message'}——field 定位到条目下标
    (如 'core_views[0].attribution'),machine-readable 供隔离报告。"""
    v = []

    def bad(field, rule, message):
        v.append({'field': field, 'rule': rule, 'message': message})

    if not isinstance(doc, dict):
        return [{'field': '$', 'rule': 'type_object',
                 'message': '顶层必须是 JSON 对象'}]
    for k in TOP_REQUIRED:
        if k not in doc:
            bad(k, 'required', '顶层必填字段缺失')
    if v:                          # 必填面不全,后续字段访问无意义→短路
        return v

    if doc['schema_version'] != SCHEMA_VERSION:
        bad('schema_version', 'schema_version',
            f"须为 '{SCHEMA_VERSION}'(当前 {doc['schema_version']!r})")

    stem = filename[:-5] if filename and filename.endswith('.json') else filename
    if stem is not None:
        if not VIEW_FILE_RE.match(stem or ''):
            bad('view_id', 'filename_format',
                f'文件名须为 VIEW-YYYYMMDD-NNN.json(当前 {filename})')
        elif doc['view_id'] != stem:
            bad('view_id', 'filename_match',
                f'view_id({doc["view_id"]!r})须与文件名主干({stem!r})一致')

    inst = doc['institution']
    if not isinstance(inst, dict) or 'name' not in inst or 'type' not in inst:
        bad('institution', 'shape', '须为 {name, type, department}')
    else:
        if inst['type'] not in INSTITUTION_TYPES:
            bad('institution.type', 'enum',
                f"须∈{INSTITUTION_TYPES}(当前 {inst['type']!r})")
        if not isinstance(inst.get('name'), str) or not inst['name'].strip():
            bad('institution.name', 'nonempty', '机构名非空字符串')
        if 'department' not in inst:
            bad('institution.department', 'required', 'department 必填(无部门给空串)')

    if not isinstance(doc['authors'], list):
        bad('authors', 'type_list', '作者列表(无名可给 [])')

    if doc['source_type'] not in SOURCE_TYPES:
        bad('source_type', 'enum',
            f"须∈{SOURCE_TYPES}(当前 {doc['source_type']!r})")
    if doc['access_level'] not in ACCESS_LEVELS:
        bad('access_level', 'enum',
            f"须∈{ACCESS_LEVELS}(当前 {doc['access_level']!r})")
    if doc['view_horizon'] not in VIEW_HORIZONS:
        bad('view_horizon', 'enum',
            f"须∈{VIEW_HORIZONS}(当前 {doc['view_horizon']!r})")
    if not (isinstance(doc['source_url'], str) and doc['source_url'].startswith('http')):
        bad('source_url', 'url', '来源链接须为 http(s) URL')

    pd_, fd = doc['publish_date'], doc['fetch_date']
    if not _iso_ok(pd_):
        bad('publish_date', 'iso_date', 'YYYY-MM-DD')
    if not _iso_ok(fd):
        bad('fetch_date', 'iso_date', 'YYYY-MM-DD')
    if _iso_ok(pd_) and _iso_ok(fd) and pd_ > fd:
        bad('publish_date', 'publish_le_fetch',
            f'发布日({pd_})不得晚于采集日({fd})')

    if not (isinstance(doc['subjects'], list) and doc['subjects']):
        bad('subjects', 'nonempty_list', '主题非空列表')
    else:
        unknown = [s for s in doc['subjects'] if s not in KNOWN_SUBJECTS]
        if unknown:
            bad('subjects', 'known_subjects',
                f'未登记主题{unknown}(合法集见 view_metric_map.json)')

    cvs = doc['core_views']
    if not (isinstance(cvs, list) and cvs):
        bad('core_views', 'nonempty', '核心观点至少一条(空观点=不是观点档)')
    else:
        for i, cv in enumerate(cvs):
            pre = f'core_views[{i}]'
            if not isinstance(cv, dict) or 'statement' not in cv:
                bad(pre, 'shape', '每条须为 {statement, attribution, basis[, quote]}')
                continue
            if not isinstance(cv['statement'], str) or not cv['statement'].strip():
                bad(pre + '.statement', 'nonempty', '观点陈述非空')
            att = cv.get('attribution')      # 章程红线: 硬性拦截缺失/非法
            if att not in ATTRIBUTIONS:
                bad(pre + '.attribution', 'enum_required',
                    f"attribution 必填且∈{ATTRIBUTIONS}(当前 {att!r})——"
                    '机构明示 vs AI 推导不得含糊')
            if cv.get('basis') not in BASES:
                bad(pre + '.basis', 'enum',
                    f"须∈{BASES}(当前 {cv.get('basis')!r})")
            # v1.1(仲裁): quote=任意 basis 可附的原文佐证——非空字符串且
            # ≤500;verbatim_quote 仍强制必填。不再有 quote_only_verbatim 规则。
            q = cv.get('quote')
            if cv.get('basis') == 'verbatim_quote':
                if not isinstance(q, str) or not q.strip():
                    bad(pre + '.quote', 'verbatim_requires_quote',
                        'basis=verbatim_quote 时 quote 必填')
                elif len(q) > QUOTE_MAX_CHARS:
                    bad(pre + '.quote', 'quote_max_length',
                        f'引文 {len(q)} 字符 > {QUOTE_MAX_CHARS}'
                        '(存储只存短引文,禁整篇转载)')
            elif q is not None:
                if not isinstance(q, str) or not q.strip():
                    bad(pre + '.quote', 'quote_nonempty',
                        '佐证引文须为非空字符串(无佐证则删除 quote 键)')
                elif len(q) > QUOTE_MAX_CHARS:
                    bad(pre + '.quote', 'quote_max_length',
                        f'引文 {len(q)} 字符 > {QUOTE_MAX_CHARS}'
                        '(存储只存短引文,禁整篇转载)')

    for i, fc in enumerate(doc['forecasts'] or []):
        pre = f'forecasts[{i}]'
        if not isinstance(fc, dict) or not {'target', 'value_or_direction',
                                            'horizon'} <= set(fc):
            bad(pre, 'shape', '每条须为 {target, value_or_direction, horizon, attribution}')
        elif fc.get('attribution') not in ATTRIBUTIONS:
            bad(pre + '.attribution', 'enum_required',
                f"attribution 必填且∈{ATTRIBUTIONS}(当前 {fc.get('attribution')!r})")

    for key, sfield in (('key_assumptions', 'statement'),
                        ('risk_factors', 'statement'),
                        ('evidence_cited', 'statement')):
        for i, item in enumerate(doc[key] or []):
            pre = f'{key}[{i}]'
            if not isinstance(item, dict) or sfield not in item:
                bad(pre, 'shape', f'每条须为 {{{sfield}, attribution}}')
            elif item.get('attribution') not in ATTRIBUTIONS:
                bad(pre + '.attribution', 'enum_required',
                    f"attribution 必填且∈{ATTRIBUTIONS}"
                    f"(当前 {item.get('attribution')!r})")

    for i, fz in enumerate(doc['falsification_conditions'] or []):
        pre = f'falsification_conditions[{i}]'
        if not isinstance(fz, dict) or 'condition' not in fz:
            bad(pre, 'shape', '每条须为 {condition, attribution}')
        elif fz.get('attribution') not in ATTRIBUTIONS:
            bad(pre + '.attribution', 'enum_required',
                f"attribution 必填且∈{ATTRIBUTIONS}(当前 {fz.get('attribution')!r})")

    for i, rv in enumerate(doc['revisions'] or []):
        pre = f'revisions[{i}]'
        if not isinstance(rv, dict) or not {'date', 'change', 'source_url'} <= set(rv):
            bad(pre, 'shape', '每条修订须为 {date, change, source_url}(只追加,不覆写)')
        elif not _iso_ok(rv.get('date')):
            bad(pre + '.date', 'iso_date', 'YYYY-MM-DD')

    for k in ('completeness_notes', 'copyright_note'):
        if not isinstance(doc[k], str):
            bad(k, 'type_str', '字符串(无内容给空串)')
    return v


def _view_files(views_dir):
    return sorted(glob.glob(os.path.join(views_dir, 'VIEW-*.json')))


def load_views(views_dir=None):
    """装载全部合规观点档。返回 {'views': [doc...], 'quarantined':
    [{'file','view_id','violations':[...]}...], 'n_files': N}。

    违规件隔离不装载(绝不降级装载违规数据);views 按 view_id 排序。"""
    d = views_dir or VIEWS_DIR
    views, quarantined = [], []
    files = _view_files(d)
    for path in files:
        fname = os.path.basename(path)
        try:
            with open(path, encoding='utf-8') as f:
                doc = json.load(f)
        except (OSError, ValueError) as e:
            quarantined.append({'file': fname,
                                'view_id': fname[:-5] if fname.endswith('.json') else fname,
                                'violations': [{'field': '$', 'rule': 'parse',
                                                'message': f'读取/解析失败: {e}'}]})
            continue
        violations = lint_view(doc, fname)
        if violations:
            quarantined.append({'file': fname,
                                'view_id': doc.get('view_id', fname[:-5]),
                                'violations': violations})
        else:
            views.append(doc)
    views.sort(key=lambda x: x['view_id'])
    return {'views': views, 'quarantined': quarantined, 'n_files': len(files)}


def get_view(view_id, views_dir=None):
    """取单份合规观点档。返回 (doc|None, reason|None)——违规件与不存在
    同样返回 None+原因(隔离件不因点名而被放出)。"""
    res = load_views(views_dir)
    for doc in res['views']:
        if doc['view_id'] == view_id:
            return doc, None
    for q in res['quarantined']:
        if q['view_id'] == view_id or q['file'] == view_id:
            return None, f'该文件被 linter 隔离({len(q["violations"])}项违规,lint 查看)'
    return None, f'views 存储无此 view_id: {view_id}'


def list_views(views_dir=None):
    """列表摘要行(装载面=合规件;隔离件单独计数)。"""
    res = load_views(views_dir)
    rows = [{'view_id': d['view_id'],
             'institution': d['institution']['name'],
             'publish_date': d['publish_date'],
             'view_horizon': d['view_horizon'],
             'subjects': list(d['subjects']),
             'n_core_views': len(d['core_views']),
             'report_title': d['report_title']}
            for d in res['views']]
    return {'views': rows, 'n_quarantined': len(res['quarantined']),
            'n_files': res['n_files']}


def check_urls_online(views_dir=None, timeout=10):
    """Charter9 P0-3(协调裁定③): URL 活性核验——**显式联网档位,默认关**。

    lint 本体保持离线(C席实测: 全伪造件 0 违规过 lint——结构纪律管不住
    真实性);本函数是可选补强: 对每份合规件 source_url 发一次 GET(只读,
    超时短,不跟认证/不提交表单),2xx/3xx=reachable,其余/DNS 失败=不可达。
    **不可达≠伪造**(链路腐坏/地域墙/改版都不可达): 结果只披露不隔离,
    不作为 lint violation,不改变装载面。零网络环境的默认路径永不调用本函数。
    """
    import urllib.request
    res = load_views(views_dir)
    checks = []
    for d in res['views']:
        url = d.get('source_url') or ''
        item = {'view_id': d['view_id'], 'url': url}
        try:
            req = urllib.request.Request(url, method='GET',
                                         headers={'User-Agent': 'investment-agent-view-audit/1.0'})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                item['reachable'] = 200 <= resp.status < 400
                item['status'] = resp.status
        except Exception as e:                     # noqa: BLE001 —— DNS/超时/HTTP错误统一如实披露
            item['reachable'] = False
            item['status'] = None
            item['note'] = str(e)[:160]
        checks.append(item)
    return {'n_checked': len(checks),
            'n_reachable': sum(1 for c in checks if c.get('reachable')),
            'checks': checks}


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    d = sys.argv[2] if len(sys.argv) > 2 else VIEWS_DIR
    if cmd == 'lint':
        res = load_views(d)
        for q in res['quarantined']:
            print(f"⛔ {q['file']}")
            for viol in q['violations']:
                print(f"   - [{viol['rule']}] {viol['field']}: {viol['message']}")
        print(f"合规 {len(res['views'])} / 隔离 {len(res['quarantined'])} / 共 {res['n_files']}")
        sys.exit(0 if not res['quarantined'] else 1)
    elif cmd == 'list':
        out = list_views(d)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(__doc__)
        sys.exit(2)
