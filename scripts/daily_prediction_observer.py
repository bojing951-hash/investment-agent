#!/usr/bin/env python3
"""每日预测观察记录(第四轮P0-6)

接入每日数据采集流水线(数据校验/锚点生成之后):
- 用Python把"观察期内预测"所需的当期市场数据记入 allocation_views.json 的
  observations[](按观测日去重,同观测日留最新采集 — 幂等,重复运行不增记录);
- 记录含 metric/value/obs_date/retrieved_at/source,锚点带兄弟.high/.low时一并记录
  (盘中触及判定需要);
- 前提规格同样每日程序判定(兑现→转观察中,观察期自前提观测日起);
- 不调用GLM — 裁决仍由周报路径的引擎/受核验GLM执行,本脚本只做数据记录。

CLI(离线测试): --views PATH --anchors PATH --today YYYY-MM-DD
"""
import os
import sys
import json
import glob
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_VIEWS = os.path.join(ROOT_DIR, 'config', 'allocation_views.json')


def load_latest_anchors(anchors_path=None):
    """最新锚点文件(数据校验器产物,含obs_date/as_of/兄弟high/low)。"""
    if anchors_path:
        with open(anchors_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    files = sorted(glob.glob(os.path.join(ROOT_DIR, 'data', 'daily', 'anchors_*.json')))
    if not files:
        return None
    with open(files[-1], 'r', encoding='utf-8') as f:
        return json.load(f)


def observe(views_path=None, anchors=None, today_str=None):
    """记录当期观察(幂等)。返回(变更说明列表, 观察中的预测数)。"""
    import allocation_engine as ae
    views_path = views_path or DEFAULT_VIEWS
    if anchors is None:
        anchors = load_latest_anchors()
    if anchors is None:
        print("⚠️ 无锚点文件,今日不记录预测观察")
        return [], 0
    with open(views_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    watching = [p for p in data.get('predictions', [])
                if p.get('status') in ('observing', 'not_yet_triggered')]
    changes = ae.record_observations(data, anchors, today_str)
    if changes:
        shutil_copy(views_path)
        tmp = views_path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, views_path)
        print(f"✅ 预测观察已记录({len(changes)}项变更,备份allocation_views.json.bak)")
        for c in changes:
            print(f"   {c}")
    else:
        print("✅ 预测观察无变更(幂等: 当期观测已记录)")
    return changes, len(watching)


def shutil_copy(path):
    import shutil
    shutil.copy(path, path + '.bak')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='每日预测观察记录(不调用GLM)')
    ap.add_argument('--views', default=None, help='观点库路径(默认config/allocation_views.json)')
    ap.add_argument('--anchors', default=None, help='锚点JSON路径(默认最新data/daily/anchors_*)')
    ap.add_argument('--today', default=None, help='研究截止日YYYY-MM-DD(默认今天)')
    args = ap.parse_args()
    print(f"预测观察记录 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    changes, n = observe(views_path=args.views, anchors=None if not args.anchors else
                         json.load(open(args.anchors, encoding='utf-8')),
                         today_str=args.today)
    print(f"观察期内预测: {n} 条")
    sys.exit(0)
