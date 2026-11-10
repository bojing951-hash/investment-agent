"""
data/daily 采集档保留策略(Charter6-P0 配套,2026-11-09;采纳 A2 §4-P0/§3)

背景: 采集窗口默认扩到10年后(Charter6-P0),data/daily 单日增量约 3.6-5MB
(global+macro 序列变长),无保留策略约 1.8GB+/年(A2 §3 估算)。

规则(90天全量 + 月度gzip归档 + 可重拉旧档清理):
  1. 观测日距今 ≤ keep_days 的采集档: 原样保留(下游最新档扫描/修订检测
     只读最新档;近窗全量保留供排障与回看);
  2. 观测日更早的采集档: 每个采集族(prefix)每月保留**最后一份** →
     gzip 压缩移入 data/daily/archive/;同月其余旧档删除——采集档可全量
     重拉重建(FRED/Yahoo 幂等,采集窗口内完整自愈,A2 §3: 保持全量重拉
     不做增量合并,删除不损失可重建数据);
  3. 研究层文件一律不动: research_snapshot_*/anchors_*/anchor_prompt_*/
     correlation_* 等不在采集族清单内(研究台账 append-only 纪律,删除/
     移动违反不可变契约;snapshot 选档/溯源链依赖它们留在 data/daily);
  4. data/research 完全不在本模块职责内(永不触碰)。

工程属性: 无网络、纯本地文件操作;dry_run 只报告不动手;重入幂等
(第二次运行对已归档月份零动作);操作清单随返回值交调用方记台账。
"""

import argparse
import gzip
import os
import re
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 采集族清单 = 各采集器写入 data/daily 的文件名前缀(手工登记,新增采集器
# 须同步登记;研究层前缀(research_snapshot_/anchors_/anchor_prompt_/
# correlation_)刻意缺席)。同日多版本档(如 *_v2.json)不匹配日期正则,
# 天然不动。
COLLECTOR_PREFIXES = ('macro_', 'global_', 'china_', 'japan_', 'jp_',
                      'ea_', 'rate_economy_', 'shiller_')
_FILE_RE = re.compile(
    r'^(?:' + '|'.join(COLLECTOR_PREFIXES) + r')(\d{8})\.(json|md)$')
ARCHIVE_DIRNAME = 'archive'
DEFAULT_KEEP_DAYS = 90


def prune_daily_archives(daily_dir, keep_days=DEFAULT_KEEP_DAYS, now=None,
                         dry_run=False):
    """对 data/daily 执行保留策略,返回操作报告 dict(含完整文件清单)。

    now 用于测试注入观测时点;缺省墙钟。dry_run=True 时只填充报告不动文件。
    目录不存在时返回零动作报告(不视为错误——新装机/测试空目录常态)。"""
    now = now or datetime.now()
    cutoff = now - timedelta(days=keep_days)
    report = {
        'policy': 'keep_recent_full+monthly_gzip_archive',
        'daily_dir': daily_dir,
        'now': now.strftime('%Y-%m-%d %H:%M:%S'),
        'keep_days': keep_days,
        'cutoff': cutoff.strftime('%Y-%m-%d'),
        'dry_run': bool(dry_run),
        'kept': [],
        'archived': [],
        'deleted': [],
        'untouched': [],
        'archive_dir': os.path.join(daily_dir, ARCHIVE_DIRNAME),
    }
    if not os.path.isdir(daily_dir):
        return report
    cutoff_date = cutoff.date()
    old_by_month = {}  # (prefix, ext, YYYYMM) -> [(ymd, filename)]
    for name in sorted(os.listdir(daily_dir)):
        path = os.path.join(daily_dir, name)
        if not os.path.isfile(path):
            continue
        m = _FILE_RE.match(name)
        if not m:
            report['untouched'].append(name)
            continue
        ymd, ext = m.group(1), m.group(2)
        prefix = next(p for p in COLLECTOR_PREFIXES
                      if name.startswith(p))
        try:
            obs = datetime.strptime(ymd, '%Y%m%d').date()
        except ValueError:
            report['untouched'].append(name)
            continue
        if obs >= cutoff_date:
            report['kept'].append(name)
        else:
            old_by_month.setdefault((prefix, ext, ymd[:6]), []).append((ymd, name))
    archive_dir = report['archive_dir']
    for (_prefix, _ext, _month), entries in sorted(old_by_month.items()):
        entries.sort()  # 同月按观测日升序;最后一份=该月代表档
        for _ymd, name in entries[:-1]:
            report['deleted'].append(name)
            if not dry_run:
                os.remove(os.path.join(daily_dir, name))
        rep_name = entries[-1][1]
        report['archived'].append(rep_name)
        if not dry_run:
            os.makedirs(archive_dir, exist_ok=True)
            src = os.path.join(daily_dir, rep_name)
            dst = os.path.join(archive_dir, rep_name + '.gz')
            with open(src, 'rb') as fin, gzip.open(dst, 'wb', compresslevel=9) as fout:
                fout.write(fin.read())
            os.remove(src)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(
        description='data/daily 采集档保留策略(90天全量+月度gzip归档;'
                    '研究层文件与 data/research 永不触碰)')
    ap.add_argument('--daily-dir', default=None,
                    help='data/daily 目录(默认=项目内 data/daily)')
    ap.add_argument('--keep-days', type=int, default=DEFAULT_KEEP_DAYS,
                    help='近窗全量保留天数(默认90)')
    ap.add_argument('--dry-run', action='store_true',
                    help='只报告将执行的动作,不动任何文件')
    args = ap.parse_args(argv)
    daily_dir = args.daily_dir
    if daily_dir is None:
        from env_config import DATA_DIR
        daily_dir = os.path.join(DATA_DIR, 'daily')
    rep = prune_daily_archives(daily_dir, keep_days=args.keep_days,
                               dry_run=args.dry_run)
    verb = '将归档' if args.dry_run else '已归档'
    verb2 = '将删除' if args.dry_run else '已删除'
    print(f"保留策略({rep['policy']}): 目录={daily_dir} "
          f"now={rep['now']} cutoff={rep['cutoff']}"
          f"{' [DRY-RUN]' if args.dry_run else ''}")
    print(f"  近窗保留: {len(rep['kept'])} 份")
    print(f"  月度代表{verb}: {len(rep['archived'])} 份 → {rep['archive_dir']}")
    print(f"  旧档{verb2}: {len(rep['deleted'])} 份")
    print(f"  非采集族不动: {len(rep['untouched'])} 份")
    for name in rep['archived']:
        print(f"    📦 {name}.gz")
    for name in rep['deleted']:
        print(f"    🗑️  {name}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
