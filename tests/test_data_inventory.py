# -*- coding: utf-8 -*-
"""IA-DATA-W1 专项测试(IA-DATA-W1-AC-v1.0 范围B;DI-AC-01/02/04)。

被测对象: scripts/data_inventory.py(inventory/diff 两模式)。
全部 fixture 为 tmp 合成小 JSON/MD(自造,覆盖 ≥2 文件类型的 summary 提取),
零网络、零真实 data/daily 依赖(CI checkout 内无 data/daily,gitignored)。

覆盖面(DI-AC-01/02):
  I组 清单条目完整性: file/size_bytes/sha256 三元组,测试内用 hashlib
     独立重算对照(不以工具自身输出为其正确性唯一证据);
  S组 summary 提取: china_json/global_json/global_md/rate_economy_md 及
     未登记类型(四键必存、不适用记 null);
  D组 diff 三类检测(added/removed/changed 含前后 sha256)+ 退出码 0/1;
  C组 CLI 语义: --help exit 0;无参 exit 2;坏目录 exit 2;diff 坏输入 exit 2;
  R组 负向敏感性(退化注入,repo R3 惯例): 对被测源码文本做最小退化替换后
     importlib 加载,断言退化版行为与正确版分离——R1 哈希退化(sha256→md5,
     64位断言红)、R2 diff 退化(changed 判定置 False,三类检测红)。
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, 'scripts', 'data_inventory.py')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

import data_inventory as di  # noqa: E402


def _write(path, text):
    Path(path).write_text(text, encoding='utf-8')
    return path


CHINA_FIXTURE = {
    "timestamp": "2026-10-31 18:00:00",
    "version": "2.1",
    "a_share_indices": {
        "000001.SH": {"close": 3300.5, "date": "2026-10-30", "series": {}}
    },
    "hk_indices": {
        "^HSI": {"close": 23000.1, "date": "2026-10-30", "series": {}}
    },
    "margin": None,
    "valuation": {},
}

GLOBAL_FIXTURE = {
    "date": "20261031",
    "time": "21:41:07",
    "count": 2,
    "data": {
        "SPX": {"close": 7000.0, "date": "2026-10-30"},
        "BTC": {"close": 80000.0, "date": "2026-10-30"},
    },
}

GLOBAL_MD_FIXTURE = (
    "# 全球资产数据 20261031\n\n"
    "| 资产 | 收盘 | 周变化 |\n"
    "|------|------|--------|\n"
    "| SPX | 7000.0 | +1.0% |\n"
    "| BTC | 80000.0 | -2.0% |\n"
)


def make_fixture_dir(base, with_china=True, with_global=True,
                     with_global_md=True, with_rate_md=True, extra=None):
    d = Path(base)
    d.mkdir(parents=True, exist_ok=True)
    if with_china:
        _write(d / 'china_20261031.json',
               json.dumps(CHINA_FIXTURE, ensure_ascii=False))
    if with_global:
        _write(d / 'global_20261031.json',
               json.dumps(GLOBAL_FIXTURE, ensure_ascii=False))
    if with_global_md:
        _write(d / 'global_20261031.md', GLOBAL_MD_FIXTURE)
    if with_rate_md:
        _write(d / 'rate_economy_20261031.md',
               '# 利率预期与实体经济 (20261031)\n\n- 某利率: 3.75%\n')
    if extra:
        for name, text in extra.items():
            _write(d / name, text)
    return d


def run_cli(*args):
    return subprocess.run(
        [sys.executable, SCRIPT] + list(args),
        capture_output=True, text=True)


class TestInventoryEntries(unittest.TestCase):
    """I组: 清单条目完整性(独立哈希对照,DI-AC-01)。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dirA = make_fixture_dir(
            os.path.join(self._tmp.name, 'A'),
            extra={'macro_20261031.json': '{"date": "20261031", "data": {}}',
                   'notes_unknown.txt': 'plain text'})
        self.out = os.path.join(self._tmp.name, 'inv.json')
        r = run_cli('inventory', '--dir', str(self.dirA), '--out', self.out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.inv = json.loads(Path(self.out).read_text(encoding='utf-8'))

    def tearDown(self):
        self._tmp.cleanup()

    def test_file_count_matches_directory(self):
        actual = sorted(p.name for p in Path(self.dirA).iterdir())
        self.assertEqual(self.inv['file_count'], len(actual))
        self.assertEqual(sorted(f['file'] for f in self.inv['files']), actual)

    def test_triplet_independently_recomputed(self):
        # 测试内以 hashlib/stat 独立重算,不引用被测实现
        for f in self.inv['files']:
            p = Path(self.dirA) / f['file']
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertEqual(f['sha256'], h, f['file'])
            self.assertEqual(f['size_bytes'], p.stat().st_size, f['file'])
            self.assertIsInstance(f['sha256'], str)
            self.assertEqual(len(f['sha256']), 64)

    def test_schema_fields_present(self):
        self.assertEqual(self.inv['schema_version'], 1)
        self.assertIn('generated_utc', self.inv)
        self.assertIn('target_dir', self.inv)
        for f in self.inv['files']:
            for key in ('file', 'size_bytes', 'sha256', 'summary', 'notes'):
                self.assertIn(key, f, f['file'])
            for key in ('data_date', 'assets_count', 'assets',
                        'close_meta_present'):
                self.assertIn(key, f['summary'], f['file'])


class TestSummaryExtraction(unittest.TestCase):
    """S组: 逐类型 summary 提取与不适用 null 语义。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def _one(self, name, text):
        d = Path(self._tmp.name) / 'single'
        if d.exists():
            for p in d.iterdir():
                p.unlink()
        else:
            d.mkdir(parents=True)
        _write(d / name, text)
        out = os.path.join(self._tmp.name, 'inv.json')
        r = run_cli('inventory', '--dir', str(d), '--out', out)
        self.assertEqual(r.returncode, 0, r.stderr)
        inv = json.loads(Path(out).read_text(encoding='utf-8'))
        self.assertEqual(inv['file_count'], 1)
        return inv['files'][0]

    def test_china_summary(self):
        f = self._one('china_20261031.json',
                      json.dumps(CHINA_FIXTURE, ensure_ascii=False))
        s = f['summary']
        self.assertEqual(s['data_date'], '2026-10-31')
        self.assertEqual(s['assets'], ['000001.SH', '^HSI'])
        self.assertEqual(s['assets_count'], 2)
        self.assertTrue(s['close_meta_present'])

    def test_global_summary(self):
        f = self._one('global_20261031.json',
                      json.dumps(GLOBAL_FIXTURE, ensure_ascii=False))
        s = f['summary']
        self.assertEqual(s['data_date'], '20261031')
        self.assertEqual(s['assets'], ['BTC', 'SPX'])
        self.assertEqual(s['assets_count'], 2)
        self.assertTrue(s['close_meta_present'])

    def test_global_md_summary(self):
        f = self._one('global_20261031.md', GLOBAL_MD_FIXTURE)
        s = f['summary']
        self.assertEqual(s['data_date'], '20261031')
        self.assertEqual(s['assets'], ['SPX', 'BTC'])
        self.assertEqual(s['assets_count'], 2)
        self.assertTrue(s['close_meta_present'])

    def test_rate_economy_md_summary_null_semantics(self):
        f = self._one('rate_economy_20261031.md',
                      '# 利率预期与实体经济 (20261031)\n\n- 某: 1\n')
        s = f['summary']
        self.assertEqual(s['data_date'], '20261031')
        self.assertIsNone(s['assets'])
        self.assertIsNone(s['assets_count'])
        self.assertIsNone(s['close_meta_present'])

    def test_unregistered_type_all_null(self):
        f = self._one('notes_unknown.txt', 'plain')
        s = f['summary']
        for key in ('data_date', 'assets_count', 'assets',
                    'close_meta_present'):
            self.assertIsNone(s[key])
        self.assertIn('未登记类型', f['notes'])

    def test_broken_json_summary_null_with_note(self):
        f = self._one('china_20261031.json', '{not valid json')
        s = f['summary']
        self.assertIsNone(s['data_date'])
        self.assertIn('JSON解析失败', f['notes'])
        # 三元组仍完整(哈希与大小不依赖解析成败)
        p = Path(self._tmp.name) / 'single' / 'china_20261031.json'
        self.assertEqual(f['sha256'],
                         hashlib.sha256(p.read_bytes()).hexdigest())


class TestDiffSemantics(unittest.TestCase):
    """D组: diff 三类检测与退出码 0/1(DI-AC-02)。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmp.cleanup()

    def _inv(self, tag, **kw):
        d = make_fixture_dir(os.path.join(self._tmp.name, tag), **kw)
        out = os.path.join(self._tmp.name, 'inv_%s.json' % tag)
        r = run_cli('inventory', '--dir', str(d), '--out', out)
        self.assertEqual(r.returncode, 0, r.stderr)
        return out

    def test_three_classes_and_exit_1(self):
        old = self._inv('old')
        # new: 删 china(removed)、global 内容改(changed)、增 rate_economy json(added)
        new = self._inv(
            'new', with_china=False, with_global=True, with_global_md=True,
            with_rate_md=True,
            extra={'global_20261031.json': json.dumps(
                {'date': '20261031', 'time': '21:41:07', 'count': 2,
                 'data': {'SPX': {'close': 7001.0, 'date': '2026-10-30'},
                          'BTC': {'close': 80000.0, 'date': '2026-10-30'}}},
                ensure_ascii=False),
                'rate_economy_20261031.json': '{"date": "20261031"}'})
        out = os.path.join(self._tmp.name, 'diff.json')
        r = run_cli('diff', old, new, '--out', out)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        doc = json.loads(Path(out).read_text(encoding='utf-8'))
        self.assertEqual([a['file'] for a in doc['added']],
                         ['rate_economy_20261031.json'])
        self.assertEqual([rm['file'] for rm in doc['removed']],
                         ['china_20261031.json'])
        self.assertEqual([c['file'] for c in doc['changed']],
                         ['global_20261031.json'])
        ch = doc['changed'][0]
        for side in ('old', 'new'):
            self.assertEqual(len(ch[side]['sha256']), 64)
            self.assertIsInstance(ch[side]['size_bytes'], int)
        self.assertNotEqual(ch['old']['sha256'], ch['new']['sha256'])
        # 前后哈希与两侧清单原值一致(逐字对照)
        old_inv = json.loads(Path(old).read_text(encoding='utf-8'))
        new_inv = json.loads(Path(new).read_text(encoding='utf-8'))
        o = next(f for f in old_inv['files'] if f['file'] == 'global_20261031.json')
        n = next(f for f in new_inv['files'] if f['file'] == 'global_20261031.json')
        self.assertEqual(ch['old']['sha256'], o['sha256'])
        self.assertEqual(ch['new']['sha256'], n['sha256'])

    def test_identical_exit_0(self):
        old = self._inv('same')
        r = run_cli('diff', old, old)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        doc = json.loads(r.stdout)
        self.assertEqual(doc['added'], [])
        self.assertEqual(doc['removed'], [])
        self.assertEqual(doc['changed'], [])

    def test_size_only_change_detected(self):
        old = self._inv('so_old')
        new = self._inv('so_new', with_china=True, with_global=True,
                        with_global_md=True, with_rate_md=False,
                        extra={'global_20261031.md': GLOBAL_MD_FIXTURE + '\n'})
        r = run_cli('diff', old, new)
        self.assertEqual(r.returncode, 1)
        doc = json.loads(r.stdout)
        self.assertEqual([c['file'] for c in doc['changed']],
                         ['global_20261031.md'])


class TestCliSemantics(unittest.TestCase):
    """C组: --help/无参/IO 错误退出码。"""

    def test_help_exit_0(self):
        r = run_cli('--help')
        self.assertEqual(r.returncode, 0)
        self.assertIn('inventory', r.stdout)
        self.assertIn('diff', r.stdout)

    def test_no_args_exit_2(self):
        r = run_cli()
        self.assertEqual(r.returncode, 2)
        self.assertIn('usage', r.stdout + r.stderr)

    def test_missing_dir_exit_2(self):
        r = run_cli('inventory', '--dir', '/nonexistent/definitely/missing',
                    '--out', '/tmp/_should_not_exist.json')
        self.assertEqual(r.returncode, 2)
        self.assertTrue(r.stderr.strip())

    def test_diff_missing_input_exit_2(self):
        r = run_cli('diff', '/nonexistent/a.json', '/nonexistent/b.json')
        self.assertEqual(r.returncode, 2)
        self.assertTrue(r.stderr.strip())

    def test_diff_malformed_input_exit_2(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = _write(os.path.join(tmp, 'bad.json'), '{"files": "not a list"}')
            r = run_cli('diff', bad, bad)
            self.assertEqual(r.returncode, 2)


class _DegradedBase(unittest.TestCase):
    """R组: 退化敏感性——文本级最小退化 + importlib 加载退化副本。"""

    _seq = 0

    def _load_degraded(self, replacements):
        _DegradedBase._seq += 1
        src = Path(SCRIPT).read_text(encoding='utf-8')
        for old, new in replacements:
            assert old in src, '退化锚点不存在: %r' % old
            src = src.replace(old, new)
        p = tempfile.NamedTemporaryFile(
            'w', suffix='_degraded_data_inventory.py', delete=False,
            encoding='utf-8')
        p.write(src)
        p.close()
        spec = importlib.util.spec_from_file_location(
            'degraded_data_inventory_%d' % _DegradedBase._seq, p.name)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, p.name


class TestNegativeSensitivity(_DegradedBase):
    def test_r1_degraded_hash_detected(self):
        # 退化: 哈希 sha256→md5(32位) → 与独立重算的 sha256 必然分离
        mod, path = self._load_degraded(
            [('hashlib.sha256()', 'hashlib.md5()')])
        try:
            with tempfile.TemporaryDirectory() as tmp:
                d = make_fixture_dir(os.path.join(tmp, 'd'))
                inv = mod.build_inventory(str(d))
                f = next(x for x in inv['files']
                         if x['file'] == 'china_20261031.json')
                real = hashlib.sha256(
                    (Path(d) / 'china_20261031.json').read_bytes()).hexdigest()
                self.assertNotEqual(f['sha256'], real)
                self.assertEqual(len(f['sha256']), 32)
        finally:
            os.unlink(path)

    def test_r2_degraded_diff_loses_changed(self):
        # 退化: changed 判定恒 False → 三类检测缺 changed,与正确版分离
        mod, path = self._load_degraded(
            [("if o.get('sha256') != n.get('sha256') or \\\n"
              "                o.get('size_bytes') != n.get('size_bytes'):",
              "if False:")])
        try:
            with tempfile.TemporaryDirectory() as tmp:
                a = make_fixture_dir(os.path.join(tmp, 'a'))
                b = make_fixture_dir(
                    os.path.join(tmp, 'b'), with_china=False,
                    extra={'global_20261031.json': json.dumps(
                        {'date': '20261031', 'time': '21:41:07', 'count': 2,
                         'data': {'SPX': {'close': 7001.0, 'date': '2026-10-30'},
                                  'BTC': {'close': 80000.0, 'date': '2026-10-30'}}},
                        ensure_ascii=False)})
                ia = mod.build_inventory(str(a))
                ib = mod.build_inventory(str(b))
                pa = _write(os.path.join(tmp, 'ia.json'), json.dumps(ia))
                pb = _write(os.path.join(tmp, 'ib.json'), json.dumps(ib))
                doc, rc = mod.build_diff(pa, pb)
                self.assertEqual(doc['changed'], [])   # 退化版漏检
                self.assertNotEqual(doc['removed'], [])
                # 正确版必须能检出 changed(以同输入对照,证明测试有效分离)
                doc2, rc2 = di.build_diff(pa, pb)
                self.assertNotEqual(doc2['changed'], [])
                self.assertEqual(rc2, 1)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main(verbosity=2)
