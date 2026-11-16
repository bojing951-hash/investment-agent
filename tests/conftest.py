# -*- coding: utf-8 -*-
"""Audit-R1 F04: pytest 适配器——脚本式套件的 rc 真相面。

仓内套件形态: 自执行脚本(module-level 断言 + 尾部 sys.exit(0/1))或
unittest 自面(__main__ 下 unittest.main())。CI 以 `python3
tests/test_*.py` 逐件直跑(offline-tests.yml),rc 即真相。

`pytest tests/` 的原生行为对本仓不可用: 脚本式套件收集期即执行完并
sys.exit → pytest 报 INTERNALERROR(实测 rc=3 恒红),通过/失败不可分
——「SystemExit ≠ 成功」的双向盲区。本适配器把每个 test_*.py 包成
**一个** pytest 用例,子进程直跑同一命令面(与 CI 同构),断言
rc==0;非零=用例失败并回显输出尾行。unittest 自面套件同法直跑
(unittest.main 的 rc 语义同样忠实)。

排除契约(与 offline-tests.yml 同源): test_model_live.py=真实模型
API 验收套件,不得进任何自动运行面,pytest 下同样跳过(不收集)。
"""
import subprocess
import sys

import pytest

_EXCLUDED = {'test_model_live.py'}
_TIMEOUT = 1800  # 秒;单套件上限与 CI 循环同量级


class SuiteFailed(Exception):
    def __init__(self, returncode, tail):
        super().__init__('suite rc=%s' % returncode)
        self.returncode = returncode
        self.tail = tail


class ScriptSuiteItem(pytest.Item):
    """一个 test_*.py = 一个用例;子进程 rc 即判定。"""

    force_fail = None

    def runtest(self):
        if self.force_fail:
            raise SuiteFailed(99, self.force_fail)
        proc = subprocess.run(
            [sys.executable, str(self.suite_path)],
            capture_output=True, text=True, timeout=_TIMEOUT)
        if proc.returncode != 0:
            out = (proc.stdout or '') + (proc.stderr or '')
            raise SuiteFailed(proc.returncode, out[-2000:])

    def repr_failure(self, excinfo):
        if excinfo.errisinstance(SuiteFailed):
            e = excinfo.value
            return ('套件退出码 %s(非零=失败;与 CI `python3 tests/…` 同构)'
                    '\n── 输出尾 ──\n%s' % (e.returncode, e.tail))
        return super().repr_failure(excinfo)

    def reportinfo(self):
        return self.suite_path, 0, 'suite: %s' % self.suite_path


class SuiteFile(pytest.File):
    def collect(self):
        text = self.path.read_text(encoding='utf-8', errors='replace')
        self_exec = ('sys.exit(' in text) or ('unittest.main(' in text)
        item = ScriptSuiteItem.from_parent(self, name=self.path.name)
        item.suite_path = self.path
        if not self_exec:
            # 反伪绿契约: 子进程直跑不自执行文件=零执行 rc=0。适配器
            # 面上这必须显式红(与 F04「SystemExit≠成功」同源),而非静默
            # 放行——真 pytest 原生套件请命名 *_pytest_native.py 走默认面。
            item.force_fail = (
                '套件不自执行(无模块级 sys.exit/unittest.main)——'
                '子进程直跑=零执行 rc=0 的伪绿;自执行契约见 pytest.ini')
        yield item


def pytest_collect_file(file_path, parent):
    name = file_path.name
    if (name.startswith('test_') and name.endswith('.py')
            and name not in _EXCLUDED):
        return SuiteFile.from_parent(parent, path=file_path)
    return None
