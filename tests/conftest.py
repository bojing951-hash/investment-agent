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

三入口修复(Audit-R2 pytest 条目): `pytest tests/`、单文件、-k 筛选
均须正常。根因: pytest 8.x 的 pytest_collect_file **非 firstresult**
(多插件可各认领一个收集器),且 python 插件对命令行直给的 .py 参数
**绕过 python_files 匹配**无条件认领为 Module(_pytest/python.py
`isinitpath` 分支)→ 单文件入口下同一文件被建两个收集器,Module 收集
期 import → 脚本套件模块级执行+SystemExit = INTERNALERROR rc=3。
修法: ① pytest_pycollect_makemodule(firstresult 钩子, python 插件
造 Module 的唯一必经点)对脚本式套件返回不导入的 SuiteFile 替身,
默认 Module 创建被短路;② 自家 pytest_collect_file 对初始路径让位
(防双收集器=双执行);③ pytest_ignore_collect 封排除套件的显式
路径直入(否则单文件入口仍会 import 真实 API 套件)。
"""
import fnmatch
import subprocess
import sys

import pytest

_EXCLUDED = {'test_model_live.py'}
_NATIVE_GLOB = '*_pytest_native.py'
_TIMEOUT = 1800  # 秒;单套件上限与 CI 循环同量级


def _is_script_suite(name: str) -> bool:
    """脚本式套件判定(双收集钩子单一事实源)。

    *_pytest_native.py=真 pytest 原生套件,须走默认模块收集(import),
    不由本适配器接管;test_model_live.py 由 ignore 钩子整体排除。
    """
    return (name.startswith('test_') and name.endswith('.py')
            and name not in _EXCLUDED
            and not fnmatch.fnmatch(name, _NATIVE_GLOB))


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


class ExcludedSkipItem(pytest.Item):
    """排除套件的显式跳过占位(不导入原文,单文件入口可见跳过原因)。"""

    def runtest(self):
        pytest.skip('排除契约: %s(真实模型API套件)不进 pytest 运行面'
                    % self.name)

    def repr_failure(self, excinfo):
        return '排除套件不应被执行: %s' % self.name

    def reportinfo(self):
        return self.path, 0, 'excluded: %s' % self.name


class ExcludedFile(pytest.File):
    """排除套件替身: 收集为零执行占位,杜绝 initpath 绕行 import。"""

    def collect(self):
        yield ExcludedSkipItem.from_parent(self, name=self.path.name)


class SuiteFile(pytest.File):
    """一个 test_*.py = 一个收集器; 子进程 rc 即判定(不导入原文)。"""

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


def pytest_pycollect_makemodule(module_path, parent):
    """单文件入口防线: 以不导入的 SuiteFile 短路默认 Module 创建。

    python 插件对命令行直给的 .py 参数绕过 python_files 匹配(isinitpath
    分支),makemodule 是其造 Module 的唯一必经点且 firstresult=True——
    在此返回替身即杜绝收集期 import(脚本套件=模块级全量执行+尾部
    sys.exit,导入即炸,INTERNALERROR rc=3 不可判读)。排除套件同点
    返回零执行替身: ignore 钩子在 Session._collect_path(顶层文件参数
    路线)不被咨询,唯此可拦显式路径直入。
    """
    if module_path.name in _EXCLUDED:
        return ExcludedFile.from_parent(parent, path=module_path)
    if _is_script_suite(module_path.name):
        return SuiteFile.from_parent(parent, path=module_path)
    return None


def pytest_collect_file(file_path, parent):
    """目录扫描路径认领; 初始路径让位 makemodule 路线防双收集器。"""
    name = file_path.name
    if (_is_script_suite(name)
            and not parent.session.isinitpath(file_path)):
        return SuiteFile.from_parent(parent, path=file_path)
    return None


def pytest_ignore_collect(collection_path, config):
    # 排除契约闭环: 无此钩子时 `pytest tests/test_model_live.py` 会经
    # initpath 绕行被 import(=进程内真跑真实 API 套件)。
    if collection_path.name in _EXCLUDED:
        return True
    return None
