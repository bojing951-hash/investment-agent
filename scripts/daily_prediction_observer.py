#!/usr/bin/env python3
"""每日预测观察记录(第四轮P0-6 + 第五轮P1-2数据质量门禁 + 第六轮P0-1写入隔离)

接入每日数据采集流水线(数据校验/锚点生成之后):
- 用Python把"观察期内预测"所需的当期市场数据记入 allocation_views.json 的
  observations[](按观测日去重,同观测日留最新采集 — 幂等,重复运行不增记录);
- 记录含 metric/value/obs_date/retrieved_at/source,锚点带兄弟.high/.low时一并记录
  (盘中触及判定需要);
- 前提规格同样每日程序判定(兑现→转观察中,观察期自前提观测日起);
  第六轮P0-2: 终态预测不参与;前提触发观测日须≤截止日(引擎侧守卫);
- 不调用GLM — 裁决仍由周报路径的引擎/受核验GLM执行,本脚本只做数据记录。

第六轮P0-1 验证与写入严格隔离:
- 观察中预测校验目标指标,未触发预测校验前提指标,二者分别判定;
- 未通过校验的指标从本轮写入用的锚点集中剔除(valid_anchors)后才交给
  record_observations — 跳过预测的无效数据不得进入长期观察历史;
  引擎侧另有同口径防御校验(其他调用路径无法绕过观察器)。

第五轮P1-2 数据质量门禁(区分关键/非关键采集失败):
- 锚点文件不存在或非当日(采集失败/未运行) → 关键失败: 今日不记录任何观察,
  不得以旧数据冒充本期观察;exit 2(流水线据此判关键步骤失败);
- 个别资产本轮缺指标/观测日未来/数据陈旧(超该指标新鲜度窗) → 只跳过受影响
  预测并留日志,其余预测照常记录(部分资产缺失不得阻断全部观察);
- 观察记录绑定实际观测日(obs_date)与本轮采集(retrieved_at=as_of,source),
  与锚点采集批次一一对应。

IA-P0-1(2026-10-27,任务7)+FIX-04(2026-10-27整改)长期状态保护收紧:
- 指标级质量门禁(rp共享原语,与状态引擎同口径): 锚点quality为FAIL/缺失/非法
  的指标一律不得进入长期观察历史(该预测本轮跳过);PASS/DEGRADED/WARN可按
  既有规则处理(DEGRADED=已验证+披露);
- 批次一致性+实际内容核验: 锚点文件须有meta(source=snapshot)且与当日权威
  快照一致,并通过对权威快照的确定性重建比对(数值被改/残留旧指标/版本混用
  均拒)——无meta/legacy拍平锚点/同日修订后旧批次一律关键FAIL,不写任何观察
  (FIX-04: 无来源证明的数据不得进入正式长期观察)。

CLI(离线测试): --views PATH --anchors PATH --today YYYY-MM-DD [--anchors-date YYYYMMDD]
exit: 0=正常(含部分跳过) / 2=关键失败(无当日有效锚点)
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

# 数据陈旧判定兜底窗口(自然日): 日频行情观测日距今日超过该值视为本轮采集失败。
# 月度宏观序列另有频率注册表口径,兜底窗只用于注册表不可用时。
_STALE_FALLBACK_DAYS = 5


def _anchors_files():
    """data/daily下锚点文件(IA-P0-1: 排除*.meta.json来源侧挂,防误当锚点集加载)。"""
    return sorted(p for p in glob.glob(os.path.join(ROOT_DIR, 'data', 'daily',
                                                    'anchors_*.json'))
                  if not p.endswith('.meta.json'))


def latest_anchors_info(anchors_path=None):
    """(最新锚点dict, 锚点文件日期YYYYMMDD)。文件日期=采集批次。"""
    if anchors_path:
        with open(anchors_path, 'r', encoding='utf-8') as f:
            return json.load(f), os.path.basename(anchors_path)[8:16]
    files = _anchors_files()
    if not files:
        return None, None
    with open(files[-1], 'r', encoding='utf-8') as f:
        return json.load(f), os.path.basename(files[-1])[8:16]


def _latest_anchors_file():
    files = _anchors_files()
    return files[-1] if files else None


def load_latest_anchors(anchors_path=None):
    """最新锚点文件(数据校验器产物,含obs_date/as_of/兄弟high/low)。"""
    anchors, _date = latest_anchors_info(anchors_path)
    return anchors


def _metric_problem(metric, anchors, today_iso):
    """单指标本轮有效性检查: 返回问题描述或None(有效)。
    不得仅因指标存在就认定有效 — 须质量合格、观测日可解析、不晚于今日、未超新鲜度窗。"""
    import research_provenance as rp
    info = (anchors or {}).get(metric)
    if not info or not isinstance(info.get('value'), (int, float)):
        return '本轮锚点缺该指标(采集失败或资产缺失)'
    # IA-P0-1-FIX4(IA-DEF-005): 质量状态与状态引擎同口径(rp共享原语)——
    # FAIL/缺失/非法一律拒绝进入正式长期观察;PASS/DEGRADED/WARN可按既有规则处理
    q_problem = rp.anchor_quality_problem(info)
    if q_problem:
        return q_problem + '(不得进入长期观察历史)'
    # FIX1-01: 观测日/今日严格解析(fp共享原语,整串验证)——'2026-10-23INVALID'
    # 不得经[:10]截断洗白后当合法观测日记录
    import freshness_policy as _fp
    d_obs = _fp.parse_instant(info.get('obs_date'))
    d_today = _fp.parse_instant(today_iso)
    if d_obs is None:
        return f'锚点观测日缺失或不可解析({info.get("obs_date")!r}),无法绑定实际观察日'
    if d_today is None:
        return f'研究截止(今日)非法({today_iso!r}),不得记录观察'
    od = d_obs.isoformat()
    if d_obs > d_today:
        return f'观测日{od}晚于今日(未来数据,不得记录)'
    lag = (d_today - d_obs).days
    try:
        from data_validator import is_fresh_anchor
        if not is_fresh_anchor(metric, info, today_iso):
            return f'观测日{od}距今日{lag}天,超出该指标新鲜度窗(疑本轮采集失败,不得以旧数据充当本期观察)'
    except ImportError:
        if lag > _STALE_FALLBACK_DAYS:
            return f'观测日{od}距今日{lag}天(数据陈旧,疑本轮采集失败)'
    return None


def observe(views_path=None, anchors=None, today_str=None, anchors_date=None,
            anchors_path=None, trusted_root=None):
    """记录当期观察(幂等)。返回(变更说明列表, 观察中预测数, 状态PASS/PARTIAL/FAIL)。
    FAIL=关键失败(无当日有效锚点): 今日不写任何观察记录。
    anchors_path(IA-P0-1): 锚点文件路径——提供时执行批次核验(meta sidecar);
    直传anchors dict(离线测试)无文件可核,维持既有日期规则。
    trusted_root(FIX8-03): 锚点批次核验可信根,缺省=rp.default_trusted_root()
    (可信代码位置推导)——生产锚点文件位于项目数据目录之下,天然在其内;
    **不从anchors_path参数推导父目录作为授权依据**(被校验路径不得自证),
    沙箱测试显式传入fixture控制的可信根。"""
    import allocation_engine as ae
    import research_provenance as rp
    views_path = views_path or DEFAULT_VIEWS
    if anchors is None:
        anchors, anchors_date = latest_anchors_info()
        anchors_path = anchors_path or _latest_anchors_file()
    today_iso = (today_str or datetime.now().strftime('%Y-%m-%d'))[:10]
    if anchors is None:
        print("⛔ 无锚点文件 — 本轮无有效观察数据,不记录预测观察(关键失败)")
        return [], 0, 'FAIL'
    if anchors_date and anchors_date != today_iso.replace('-', ''):
        print(f"⛔ 锚点文件日期{anchors_date}≠今日{today_iso.replace('-', '')} — "
              f"本轮采集失败或未运行,不得以旧数据充当本期观察(关键失败)")
        return [], 0, 'FAIL'
    # IA-P0-1(任务7)+FIX-04(IA-DEF-005): 批次一致性+实际内容核验——锚点文件
    # 必须可证明来源(meta.source=snapshot)且与当日权威快照一致(确定性重建比对)。
    # 无meta/legacy/批次失配/内容不一致 → 关键FAIL,不写任何观察:
    # 无来源证明的数据不得进入正式长期观察(直传anchors dict的离线注入路径无
    # 文件可核,由状态引擎侧同口径质量防御兜底,见allocation_engine)。
    if anchors_path and os.path.exists(anchors_path):
        # FIX7-01: 可信根独立于被校验路径——祖先符号链接重定向的锚点批次
        # 在此被拒,不由被校验路径自证。
        # FIX8-03(IA-F7-DEF-001): 锚定=缺省可信代码位置/显式trusted_root参数
        # ——不再从anchors_path自身推导父目录作授权依据
        ok, reason = rp.verify_anchor_batch(
            anchors_path, anchors_date=anchors_date,
            trusted_root=trusted_root)
        if ok is False:
            print(f"⛔ {reason} — 不记录预测观察(关键失败)")
            return [], 0, 'FAIL'

    with open(views_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    watching = [p for p in data.get('predictions', [])
                if p.get('status') in ('observing', 'not_yet_triggered')]

    # 逐预测检查本轮数据有效性: 受影响预测跳过并留日志,其余照常(部分缺失不阻断全部)
    # 第六轮P0-1: 观察中预测查目标指标,未触发预测查前提指标 — 二者分别校验,
    # 一个有效不得放行另一个;验证与写入严格隔离(见下valid_anchors)
    skipped = []
    bad_metrics = set()
    for p in watching:
        checks = []   # [(指标名, 该轮是否须有效)]
        if p.get('status') == 'observing' and p.get('metric'):
            checks.append(p['metric'])
        elif p.get('status') == 'not_yet_triggered' and isinstance(p.get('premise'), dict) \
                and p['premise'].get('metric'):
            checks.append(p['premise']['metric'])
        for metric in checks:
            problem = _metric_problem(metric, anchors, today_iso)
            if problem:
                skipped.append(p['pred_id'])
                bad_metrics.add(metric)
                print(f"⚠️ 预测#{p['pred_id']}: 本轮跳过 — {problem}")

    # 第六轮P0-1: 数据验证与状态写入严格隔离 — 只把通过验证的锚点交给
    # record_observations,被跳过预测的无效数据(缺指标/观测日缺失/未来/过期)
    # 不得进入长期观察历史(引擎侧另有防御性校验兜底,双侧防线)
    valid_anchors = {k: v for k, v in (anchors or {}).items() if k not in bad_metrics}
    changes = ae.record_observations(data, valid_anchors, today_iso)
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
        print("✅ 预测观察无变更(幂等: 当期观测已记录)"
              + (f";另{len(skipped)}项预测因数据缺失本轮跳过" if skipped else ""))
    status = 'PARTIAL' if skipped else 'PASS'
    return changes, len(watching), status


def shutil_copy(path):
    import shutil
    shutil.copy(path, path + '.bak')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='每日预测观察记录(不调用GLM)')
    ap.add_argument('--views', default=None, help='观点库路径(默认config/allocation_views.json)')
    ap.add_argument('--anchors', default=None, help='锚点JSON路径(默认最新data/daily/anchors_*)')
    ap.add_argument('--anchors-date', default=None, help='锚点采集批次YYYYMMDD(默认取自文件名;'
                                                         '显式传入可模拟陈旧锚点)')
    ap.add_argument('--today', default=None, help='研究截止日YYYY-MM-DD(默认今天)')
    args = ap.parse_args()
    print(f"预测观察记录 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    anchors = None
    anchors_date = args.anchors_date
    if args.anchors:
        with open(args.anchors, encoding='utf-8') as f:
            anchors = json.load(f)
        if not anchors_date:
            anchors_date = os.path.basename(args.anchors)[8:16]
    changes, n, status = observe(views_path=args.views, anchors=anchors,
                                 today_str=args.today, anchors_date=anchors_date,
                                 anchors_path=args.anchors)
    print(f"观察期内预测: {n} 条; 状态: {status}")
    # 关键失败必须反映在退出码: 采集失败时受影响预测的正式状态不得被更新
    sys.exit(2 if status == 'FAIL' else 0)
