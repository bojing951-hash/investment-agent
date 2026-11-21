"""store_lock — 跨进程持久化写互斥(Audit-R11 P1②,2026-11-18)。

背景(本轮审计复现): 配号/存在性检查/前序读取与落盘之间存在竞争——
并发两次裁决写入选择同一路径,后写覆盖先写且两次都返回成功;两个查询
分配相同 ID,共享临时文件名互相拆台,记录丢失或进程崩溃。

边界(本模块提供,调用方纪律见各持久化模块):
  1. store_write_lock(dirpath): 目录级跨进程互斥(fcntl.flock 顾问锁,
     锁文件=目录下 .write.lock,目录即互斥域);**同线程可重入**(事
     务组合: 外层持锁做 配号→构造→落盘,内层公开函数再取锁不自杀
     死锁),跨进程/跨线程仍互斥;
  2. unique_tmp(path): 临时文件独立命名(path.tmp.<pid>.<uuid>)——
     并发写同名目标互不拆台,中断只留孤儿临时文件,不产生撕裂终档;
  3. atomic_write_json(path, doc): 独立临时名完整写+fsync 后
     os.replace 原子发布——终档只在内容完整落盘后出现。

POSIX(macOS 开发树/Linux CI)专用;锁为顾问锁,凡写入本仓库档案
目录的进程都必须经本模块(绕过者自担竞争)。无网络、无外部依赖。
"""
import contextlib
import fcntl
import json
import os
import threading
import uuid

_lock_state = {}          # abspath -> {'tid','pid','depth','fd'}
_lock_mutex = threading.Lock()


@contextlib.contextmanager
def store_write_lock(dirpath, name='.write.lock'):
    """目录级跨进程写锁(同线程可重入;跨线程/跨进程互斥)。"""
    os.makedirs(dirpath, exist_ok=True)
    lock_path = os.path.abspath(os.path.join(dirpath, name))
    tid, pid = threading.get_ident(), os.getpid()
    with _lock_mutex:
        st = _lock_state.get(lock_path)
        if st and st['tid'] == tid and st['pid'] == pid:
            st['depth'] += 1
            reentered = True
        else:
            reentered = False
    if reentered:
        try:
            yield lock_path
        finally:
            with _lock_mutex:
                st = _lock_state.get(lock_path)
                if st:
                    st['depth'] -= 1
        return
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        with _lock_mutex:
            _lock_state[lock_path] = {'tid': tid, 'pid': pid,
                                      'depth': 1, 'fd': fd}
        try:
            yield lock_path
        finally:
            with _lock_mutex:
                _lock_state.pop(lock_path, None)
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


def unique_tmp(path):
    """独立临时名(并发写同名目标互不拆台;中断只留孤儿,不出撕裂终档)。"""
    return f'{path}.tmp.{os.getpid()}.{uuid.uuid4().hex}'


def atomic_write_json(path, doc, indent=1, sort_keys=True):
    """完整写独立临时文件+fsync 后 os.replace 原子发布(不返回中间态)。"""
    tmp = unique_tmp(path)
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=indent,
                  sort_keys=sort_keys)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
