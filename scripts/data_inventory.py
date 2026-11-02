#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""data/daily 盘点工具(IA-DATA-W1-AC-v1.0 范围A;R005-D3 承接)。

两种模式:
  inventory  扫描目录全部文件 → 结构化 JSON 清单(每文件 file/size_bytes/
             sha256 + summary 四键);成功 exit 0,参数/IO 错误 exit 2。
  diff       对比两份 inventory 清单 → added/removed/changed(含前后
             sha256/size_bytes);exit 0=无差异 / 1=有差异 / 2=错误。

行为规格依据: IA-DATA-W1-AC-v1.0 §三;摘要提取规则逐类登记于
docs/DATA_W1_DELIVERY.md(本文件不依赖任何第三方库,仅标准库)。
工具对目标目录只读;输出经 --out 落盘(缺省打印到 stdout)。
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
_CHUNK = 1 << 20

# 文件类型判定(按文件名;规则与逐类摘要提取规则在 DATA_W1_DELIVERY.md 登记)
_TYPE_RULES = (
    ('china_json',        lambda n: n.startswith('china_') and n.endswith('.json')),
    ('global_json',       lambda n: n.startswith('global_') and n.endswith('.json')),
    ('global_md',         lambda n: n.startswith('global_') and n.endswith('.md')),
    ('macro_json',        lambda n: n.startswith('macro_') and n.endswith('.json')),
    ('rate_economy_json', lambda n: n.startswith('rate_economy_') and n.endswith('.json')),
    ('rate_economy_md',   lambda n: n.startswith('rate_economy_') and n.endswith('.md')),
)


def classify(name):
    for ftype, pred in _TYPE_RULES:
        if pred(name):
            return ftype
    if name.endswith('.json'):
        return 'generic_json'
    if name.endswith('.md'):
        return 'generic_md'
    return 'other'


def utc_now_iso():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(_CHUNK), b''):
            h.update(chunk)
    return h.hexdigest()


def _null_summary():
    return {'data_date': None, 'assets_count': None, 'assets': None,
            'close_meta_present': None}


def _any_entry_has_close_meta(asset_maps):
    """close 元数据判据: ≥1 资产条目同时含 close 与 date 两键。"""
    for mapping in asset_maps:
        if not isinstance(mapping, dict):
            continue
        for entry in mapping.values():
            if (isinstance(entry, dict) and 'close' in entry
                    and 'date' in entry):
                return True
    return False


def _ymd_from_text(first_line):
    m = re.search(r'20\d{6}', first_line)
    return m.group(0) if m else None


def _md_table_assets(text):
    """markdown 表格 → (表头列, 数据行首列列表);无表返回 (None, [])。"""
    header, first_cols = None, []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith('|'):
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if all(re.fullmatch(r':?-{2,}:?', c) for c in cells if c):
            continue  # 分隔行
        if header is None:
            header = cells
        elif cells and cells[0]:
            first_cols.append(cells[0])
    return header, first_cols


def summarize(path, ftype):
    """返回 (summary, note);note 恒含 file_type 标记,异常时附原因。"""
    note = 'file_type=' + ftype
    if ftype == 'china_json':
        try:
            obj = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError) as e:
            return _null_summary(), note + '; JSON解析失败: %s' % e
        if not isinstance(obj, dict):
            return _null_summary(), note + '; 顶层非对象,摘要不适用'
        a_map = obj.get('a_share_indices')
        h_map = obj.get('hk_indices')
        maps = [m for m in (a_map, h_map) if isinstance(m, dict)]
        assets = sorted(set().union(*maps)) if maps else []
        return ({'data_date': str(obj.get('timestamp') or '')[:10] or None,
                 'assets_count': len(assets), 'assets': assets,
                 'close_meta_present': _any_entry_has_close_meta(maps)},
                note)
    if ftype == 'global_json':
        try:
            obj = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError) as e:
            return _null_summary(), note + '; JSON解析失败: %s' % e
        if not isinstance(obj, dict):
            return _null_summary(), note + '; 顶层非对象,摘要不适用'
        d_map = obj.get('data')
        assets = sorted(d_map) if isinstance(d_map, dict) else []
        return ({'data_date': obj.get('date'),
                 'assets_count': len(assets), 'assets': assets,
                 'close_meta_present': _any_entry_has_close_meta(
                     [d_map] if isinstance(d_map, dict) else [])},
                note)
    if ftype == 'macro_json':
        try:
            obj = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError) as e:
            return _null_summary(), note + '; JSON解析失败: %s' % e
        if not isinstance(obj, dict):
            return _null_summary(), note + '; 顶层非对象,摘要不适用'
        maps = [obj.get(k) for k in ('data', 'derived')]
        maps = [m for m in maps if isinstance(m, dict)]
        assets = sorted(set().union(*maps)) if maps else []
        return ({'data_date': obj.get('date'),
                 'assets_count': len(assets), 'assets': assets,
                 'close_meta_present': None},
                note + '; assets=指标ID(data∪derived),无close语义')
    if ftype == 'rate_economy_json':
        try:
            obj = json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, OSError) as e:
            return _null_summary(), note + '; JSON解析失败: %s' % e
        if not isinstance(obj, dict):
            return _null_summary(), note + '; 顶层非对象,摘要不适用'
        cr = obj.get('current_rates')
        re_ = obj.get('real_economy')
        fff = obj.get('fed_funds_futures')
        keys = set()
        for m in (cr, re_):
            if isinstance(m, dict):
                keys |= set(m)
        if isinstance(fff, list):
            for ent in fff:
                if isinstance(ent, dict) and ent.get('ticker'):
                    keys.add(str(ent['ticker']))
        assets = sorted(keys)
        return ({'data_date': obj.get('date'),
                 'assets_count': len(assets), 'assets': assets,
                 'close_meta_present': None},
                note + '; assets=利率/宏观序列键,无close语义')
    if ftype in ('global_md', 'rate_economy_md'):
        try:
            text = path.read_text(encoding='utf-8')
        except OSError as e:
            return _null_summary(), note + '; 读取失败: %s' % e
        lines = text.splitlines()
        data_date = _ymd_from_text(lines[0]) if lines else None
        if ftype == 'rate_economy_md':
            return ({'data_date': data_date, 'assets_count': None,
                     'assets': None, 'close_meta_present': None},
                    note + '; 散文式摘要,无机器可枚举资产表'
                           '(数值面见同日 rate_economy_*.json)')
        header, first_cols = _md_table_assets(text)
        return ({'data_date': data_date,
                 'assets_count': len(first_cols), 'assets': first_cols,
                 'close_meta_present': bool(header and '收盘' in header
                                            and first_cols)},
                note)
    # generic_json / generic_md / other: 未登记类型,四键记 null(规则已登记)
    return _null_summary(), note + '; 未登记类型,摘要规则不适用(null)'


def build_inventory(dir_path):
    target = Path(dir_path)
    if not target.exists():
        raise FileNotFoundError('目标目录不存在: %s' % target)
    if not target.is_dir():
        raise NotADirectoryError('目标不是目录: %s' % target)
    files = sorted((p for p in target.iterdir() if p.is_file()),
                   key=lambda p: p.name)
    entries = []
    for p in files:
        summary, note = summarize(p, classify(p.name))
        entries.append({'file': p.name, 'size_bytes': p.stat().st_size,
                        'sha256': sha256_file(p), 'summary': summary,
                        'notes': note})
    return {'schema_version': SCHEMA_VERSION, 'generated_utc': utc_now_iso(),
            'target_dir': str(target), 'file_count': len(entries),
            'files': entries}


def _load_inventory(path):
    obj = json.loads(Path(path).read_text(encoding='utf-8'))
    if (not isinstance(obj, dict) or not isinstance(obj.get('files'), list)):
        raise ValueError('不是合法的 inventory 清单(缺 files 列表): %s' % path)
    for ent in obj['files']:
        if not isinstance(ent, dict) or 'file' not in ent or 'sha256' not in ent:
            raise ValueError('清单条目缺 file/sha256: %s' % path)
    return obj


def build_diff(old_path, new_path):
    old_inv, new_inv = _load_inventory(old_path), _load_inventory(new_path)

    def by_name(inv):
        out = {}
        for ent in inv['files']:
            out[ent['file']] = ent
        return out

    old_map, new_map = by_name(old_inv), by_name(new_inv)
    added, removed, changed = [], [], []
    for name in sorted(set(new_map) - set(old_map)):
        e = new_map[name]
        added.append({'file': name, 'sha256': e.get('sha256'),
                      'size_bytes': e.get('size_bytes')})
    for name in sorted(set(old_map) - set(new_map)):
        e = old_map[name]
        removed.append({'file': name, 'sha256': e.get('sha256'),
                        'size_bytes': e.get('size_bytes')})
    for name in sorted(set(old_map) & set(new_map)):
        o, n = old_map[name], new_map[name]
        if o.get('sha256') != n.get('sha256') or \
                o.get('size_bytes') != n.get('size_bytes'):
            changed.append({'file': name,
                            'old': {'sha256': o.get('sha256'),
                                    'size_bytes': o.get('size_bytes')},
                            'new': {'sha256': n.get('sha256'),
                                    'size_bytes': n.get('size_bytes')}})
    return ({'old': str(old_path), 'new': str(new_path),
             'generated_utc': utc_now_iso(),
             'added': added, 'removed': removed, 'changed': changed},
            1 if (added or removed or changed) else 0)


def _emit(doc, out_path):
    text = json.dumps(doc, ensure_ascii=False, indent=2) + '\n'
    if out_path:
        Path(out_path).write_text(text, encoding='utf-8')
    else:
        print(text, end='')


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog='data_inventory.py',
        description='data/daily 盘点工具: inventory 生成目录清单; '
                    'diff 对比两份清单。摘要提取规则见 '
                    'docs/DATA_W1_DELIVERY.md。')
    sub = ap.add_subparsers(dest='command', required=True)
    p_inv = sub.add_parser('inventory', help='扫描目录生成 JSON 清单')
    p_inv.add_argument('--dir', required=True, help='目标目录(只读)')
    p_inv.add_argument('--out', default=None,
                       help='输出路径(缺省打印到 stdout)')
    p_diff = sub.add_parser('diff', help='对比两份 inventory 清单')
    p_diff.add_argument('old', help='旧清单 JSON 路径')
    p_diff.add_argument('new', help='新清单 JSON 路径')
    p_diff.add_argument('--out', default=None,
                        help='输出路径(缺省打印到 stdout)')
    args = ap.parse_args(argv)
    try:
        if args.command == 'inventory':
            _emit(build_inventory(args.dir), args.out)
            return 0
        doc, rc = build_diff(args.old, args.new)
        _emit(doc, args.out)
        return rc
    except (OSError, ValueError) as e:
        print('错误: %s' % e, file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
