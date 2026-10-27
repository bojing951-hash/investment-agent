#!/usr/bin/env python3
"""月度复盘生成器 v2.0 (第二轮审查重构, 2026-10-11)

相对v1.0的修复(对应第二轮审查第三项):
1. 触发时点: 只复盘**已完结**的自然月(期间结束后第一个周五由report_generator触发,
   或显式 --month YYYYMM); 期间未结束的月份只能以【预览】生成,不得冒充完整月度复盘
2. 单位纪律: 收益率/利差序列的月变化以bp报告(百分点序列用pp),不得套用价格涨跌幅%
3. 采集日/观测日区分: 按观测日(兄弟.date字段)去重——月度FRED序列在多个采集日
   重复出现同一观测值时只保留最新采集,杜绝"重复月度数据当多次观测"
4. 覆盖校验: 每个序列给出观测数/首末观测日/缺口交易日清单,覆盖不足必须写进结论限制
5. 预测复盘按统计周期: 只统计deadline/裁决日落在本月的预测(不再全历史混算)

用法:
  python3 monthly_review.py --month 202609   # 指定月份(已完结→正式,当月→预览)
  python3 monthly_review.py                  # auto: 上一自然月已完结且今天是其后第一个周五才生成
  python3 monthly_review.py --dry-run        # 只装配数据不调用GLM
"""
import os
import sys
import re
import json
import glob
import argparse
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data', 'daily')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output', 'monthly')

# 关键序列: (标签, 文件模式, 键正则, 单位) unit ∈ pct(价格%)/bp(收益率·利差)/pp(百分点)
KEY_SERIES = [
    ('SPX标普500',    'global_*.json',       r'^data\.SPX\.close$',   'pct'),
    ('NDX纳斯达克',   'global_*.json',       r'^data\.NDX\.close$',   'pct'),
    ('黄金',          'global_*.json',       r'^data\.GOLD\.close$',  'pct'),
    ('美元指数DXY',   'global_*.json',       r'^data\.DXY\.close$',   'pct'),
    ('VIX',           'global_*.json',       r'^data\.VIX\.close$',   'pct'),
    ('BTC',           'global_*.json',       r'^data\.BTC\.close$',   'pct'),
    ('WTI原油',       'global_*.json',       r'^data\.WTI\.close$|^data\.CL.*close$', 'pct'),
    ('上证指数',      'china_*.json',        r'000001\.SH\.(close|收盘)$', 'pct'),
    ('HY_OAS高收益利差', 'macro_*.json',     r'^data\.HY_OAS\.value$',  'bp'),
    ('CCC_OAS利差',   'macro_*.json',        r'^data\.CCC_OAS\.value$', 'bp'),
    ('UST_10Y',       'macro_*.json',        r'^data\.UST_10Y\.value$|^data\.GS10\.value$', 'bp'),
    ('UST_30Y',       'macro_*.json',        r'^data\.UST_30Y\.value$|^data\.GS30\.value$', 'bp'),
    ('TIPS_10Y实际利率', 'macro_*.json',     r'^data\.TIPS_10Y\.value$', 'bp'),
    ('失业率UNRATE',  'rate_economy_*.json', r'^real_economy\.UNRATE\.value$', 'pp'),
]

_MONTHLY_SERIES = {'失业率UNRATE'}  # 月频序列: 覆盖期望=1个观测,按观测日去重是关键


def _norm_date(s):
    if not s:
        return None
    s = str(s).strip()
    if re.match(r'\d{4}-\d{2}-\d{2}', s):
        return s[:10]
    m = re.match(r'^(\d{4})(\d{2})(\d{2})$', s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


def _month_bounds(ym):
    y, m = int(ym[:4]), int(ym[4:6])
    last = [31, 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28,
            31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
    return date(y, m, 1), date(y, m, last)


def gather_month_series(ym, data_dir=None):
    """扫描整月daily文件提取各序列。返回 {label: {first,last,min,max,chg_str,obs_count,first_obs,last_obs,freq}}。

    去重规则(第二轮#3.10): 同一观测日只保留最新采集日的值(月度FRED序列跨采集日重复)。"""
    from data_validator import flatten_json
    base = data_dir or DATA_DIR
    series = {label: {'obs': []} for label, _, _, _ in KEY_SERIES}  # obs: (as_of, obs_date, value, prev_sibling)
    patterns = {p for _, p, _, _ in KEY_SERIES}
    files_by_pattern = {p: sorted(glob.glob(os.path.join(base, p.replace('*', ym + '*'))))
                        for p in patterns}
    for label, pat, key_re, unit in KEY_SERIES:
        for fp in files_by_pattern[pat]:
            try:
                flat = flatten_json(json.load(open(fp)))
            except Exception:
                continue
            m = re.search(r'(\d{8})', os.path.basename(fp))
            as_of = m.group(1) if m else '?'
            for k, v in flat.items():
                if isinstance(v, (int, float)) and re.search(key_re, k):
                    parent = k.rsplit('.', 1)[0]
                    # 观测日: 兄弟.date字段优先,回退采集日(文件名);月频序列另取兄弟.prev_value
                    obs, prev_sibling = None, None
                    for dk, dv in flat.items():
                        if isinstance(dv, str) and dk == parent + '.date':
                            obs = _norm_date(dv)
                        elif isinstance(dv, (int, float)) and dk == parent + '.prev_value':
                            prev_sibling = dv
                    series[label]['obs'].append((as_of, obs or f"{as_of[:4]}-{as_of[4:6]}-{as_of[6:]}", v, prev_sibling))
                    break  # 每文件取一次
    out = {}
    for label, s in series.items():
        # 按观测日去重: 同obs保留最新as_of(文件已按名排序,后来的覆盖先前的)
        by_obs = {}
        for as_of, obs, val, prev_sib in s['obs']:
            by_obs[obs] = (as_of, val, prev_sib)   # 后写覆盖 → 最新采集胜出
        dedup = sorted(by_obs.items())   # 按观测日升序
        is_monthly = label in _MONTHLY_SERIES
        if is_monthly:
            # 月频序列: 期内1个观测即有效;环比 = value - prev_value(月度FRED语义)
            if not dedup:
                continue
            _, (_, val, prev_sib) = dedup[-1]
            chg = f"{val - prev_sib:+.2f}pp" if isinstance(prev_sib, (int, float)) else "N/A"
            out[label] = {
                'first': val, 'last': val, 'min': val, 'max': val,
                'chg_str': chg, 'chg_raw': round(val - prev_sib, 4) if isinstance(prev_sib, (int, float)) else None,
                'obs_count': len(dedup), 'first_obs': dedup[0][0], 'last_obs': dedup[-1][0],
                'as_of_last': dedup[-1][1][0],
            }
            continue
        if len(dedup) < 2:
            continue
        vals = [t[1] for _, t in dedup]
        first_obs, last_obs = dedup[0][0], dedup[-1][0]
        delta = vals[-1] - vals[0]
        if KEY_SERIES_DICT[label] == 'pct':
            chg = f"{delta / abs(vals[0]) * 100:+.2f}%" if vals[0] else "N/A"
        elif KEY_SERIES_DICT[label] == 'bp':
            chg = f"{delta * 100:+.0f}bp"   # 锚点以%存储,1%=100bp
        else:
            chg = f"{delta:+.2f}pp"         # 百分点序列(失业率)
        out[label] = {
            'first': vals[0], 'last': vals[-1], 'min': min(vals), 'max': max(vals),
            'chg_str': chg, 'chg_raw': round(delta, 4),
            'obs_count': len(dedup), 'first_obs': first_obs, 'last_obs': last_obs,
            'as_of_last': dedup[-1][1][0],
        }
    return out

# 查表辅助(避免在循环里反复解包KEY_SERIES)
KEY_SERIES_DICT = {label: unit for label, _, _, unit in KEY_SERIES}


def coverage_report(ym, series):
    """覆盖校验(第二轮#3.12): 每序列观测数/首末观测日/缺口交易日。返回文本行列表。"""
    first_day, last_day = _month_bounds(ym)
    weekdays = []
    d = first_day
    while d <= last_day:
        if d.weekday() < 5:
            weekdays.append(d)
        d = date.fromordinal(d.toordinal() + 1)
    lines = [f"月内工作日(含节假日): {len(weekdays)}天 (统计上应约等于交易日数)", ""]
    for label, s in series.items():
        if label in _MONTHLY_SERIES:
            ok = s['obs_count'] >= 1
            lines.append(f"- {label}[月频]: 观测{s['obs_count']}个 (首末 {s['first_obs']}~{s['last_obs']})"
                         + ("" if ok else " ⚠️本月无观测,结论须标注数据缺失"))
            continue
        obs_dates = set()
        # obs_count已知,缺口以工作日数对比近似
        gap = len(weekdays) - s['obs_count']
        note = "" if gap <= 2 else f" ⚠️缺口约{gap}个工作日(含节假日),覆盖不完整"
        lines.append(f"- {label}[日频]: 观测{s['obs_count']}天 ({s['first_obs']}→{s['last_obs']},"
                     f"末值采集日{s['as_of_last']}){note}")
    lines.append("")
    lines.append("(采集日=数据抓取日;观测日=数据所属日期。上表观测区间以观测日为准)")
    return lines


def gather_month_context(ym, views_path=None):
    """论点history、本期预测裁决、本月周报摘要、评分卡时间线"""
    ctx = {}

    tp = os.path.join(ROOT_DIR, 'config', 'thesis.json')
    if os.path.exists(tp):
        d = json.load(open(tp))
        month_num = int(ym[4:6])
        lines = []
        for t in d.get('theses', []):
            for h in t.get('history', []):
                if h.startswith(f"{month_num}/"):
                    lines.append(f"#{t['id']}{t.get('name','')}: {h}")
        ctx['thesis_moves'] = lines or ['(本月无论点状态记录)']

    # 预测复盘(第二轮#3.16: 只统计本统计周期内到期/裁决的预测)
    import allocation_engine
    views = allocation_engine.load_views(views_path)
    if views:
        first_day, last_day = _month_bounds(ym)
        pp = allocation_engine.predictions_in_period(views, first_day.strftime('%Y%m%d'),
                                                     last_day.strftime('%Y%m%d'))
        lines = [f"本月到期{len(pp['due'])}条 / 本月裁决{len(pp['resolved'])}条"
                 f"(命中{pp['counts']['hit']}/证伪{pp['counts']['miss']}/无法裁决{pp['counts']['inconclusive']})"]
        cn = allocation_engine.PRED_STATUS_CN
        for p in pp['due']:
            mark = f" → 裁决:{p.get('resolved_note','')}" if p.get('status') in ('hit', 'miss', 'inconclusive') else ""
            lines.append(f"- [#{p['pred_id']}][{cn.get(p['status'], p['status'])}] {p['asset']}: "
                         f"{p['direction']}{mark}")
        ctx['predictions'] = lines
    else:
        ctx['predictions'] = ['(无预测记录)']

    wk_dir = os.path.join(ROOT_DIR, 'output', 'weekly')
    # IA-P0-1: _annotated/_UNVALIDATED均非合格正式报告,不得进入月度摘要索引;
    # FIX-02: _CANDIDATE(发布前候选)同样排除
    wk_files = sorted(f for f in (os.listdir(wk_dir) if os.path.isdir(wk_dir) else [])
                      if f.startswith(f'weekly_report_{ym}')
                      and not f.endswith('_annotated.md') and not f.endswith('_UNVALIDATED.md')
                      and not f.endswith('_CANDIDATE.md'))
    wk_lines = []
    for wf in wk_files:
        text = open(os.path.join(wk_dir, wf), encoding='utf-8').read()
        m = re.search(r'###?\s*一、本周摘要[^\n]*\n(.{0,150})', text, re.DOTALL)
        wk_lines.append(f"- {wf[13:21]}: {(m.group(1).strip().replace(chr(10),' ') if m else '(未找到摘要节)')[:150]}")
    ctx['weekly_reports'] = wk_lines or ['(本月无周报)']

    sc_files = sorted(glob.glob(os.path.join(DATA_DIR, f'scorecard_{ym}*.json')))
    tl = []
    seen_weeks = set()
    for fp in sc_files:
        try:
            d = json.load(open(fp))
        except Exception:
            continue
        dd = date(int(ym[:4]), int(ym[4:6]), int(os.path.basename(fp)[-13:-5][6:8]))
        wk = dd.isocalendar()[1]
        if wk in seen_weeks:
            continue
        seen_weeks.add(wk)
        tl.append(f"{d.get('date')}: 计算={d.get('regime')}, 确认={d.get('confirmed_regime')}({d.get('regime_status')}), "
                  f"增长{d.get('growth_total', 0):+d}/通胀{d.get('inflation_total', 0):+d}")
    ctx['scorecard_timeline'] = tl or ['(本月无评分卡)']
    return ctx


def month_is_complete(ym, today=None):
    """月份是否已自然结束(第二轮#3.2)"""
    today = today or date.today()
    return ym < today.strftime('%Y%m')


def build_data_block(ym, data_dir=None, views_path=None):
    series = gather_month_series(ym, data_dir)
    ctx = gather_month_context(ym, views_path)
    preview = not month_is_complete(ym)
    header = (f"# {ym[:4]}年{int(ym[4:6])}月 月度原始数据汇总(自动提取自daily JSON,非周报拼接)\n"
              "> 数据来源: 原始采集序列直读(IA-P0-1标注: 非研究快照链产物;"
              "月度聚合为历史路径复盘,当日研究结论仍以快照链为准)\n")
    if preview:
        header = ("# 【预览】" + header.lstrip('# ')
                  + "\n> ⚠️ 本报告生成于**期间结束前**,数据覆盖不完整。所有结论为预览性质,"
                    "不得表述为完整月度判断,正式复盘须待期间结束后重新生成。\n")
    lines = [header]
    lines.append("## 关键资产月度区间(月初→月末,含最高/最低;收益率/利差变化以bp、百分点序列以pp计)\n")
    lines.append("| 序列 | 月初 | 月末 | 最低 | 最高 | 月变化 | 观测数 |")
    lines.append("|------|------|------|------|------|--------|--------|")
    for label, s in series.items():
        lines.append(f"| {label} | {s['first']:.2f} | {s['last']:.2f} | {s['min']:.2f} | {s['max']:.2f} | "
                     f"{s['chg_str']} | {s['obs_count']} |")
    lines.append("\n## 数据覆盖与缺口(结论须受此约束)")
    lines.extend(coverage_report(ym, series))
    lines.append("\n## 本月体制评分卡时间线(每周一份)")
    lines.extend(f"- {t}" for t in ctx['scorecard_timeline'])
    lines.append("\n## 本月论点状态变更(thesis.json history)")
    lines.extend(f"- {t}" for t in ctx['thesis_moves'])
    lines.append("\n## 本月预测到期与裁决(按统计周期,非全历史)")
    lines.extend(f"- {p}" for p in ctx['predictions'])
    lines.append("\n## 本月各期周报摘要(仅作索引,结论须回溯上方原始数据)")
    lines.extend(ctx['weekly_reports'])
    return "\n".join(lines), series, ctx, preview

MONTHLY_STRUCTURE = """请按以下结构输出月度复盘：

### 一、本月宏观体制演化
基于评分卡时间线：体制是否迁移、各维度分数的月内路径、关键驱动指标

### 二、本月证据累积与论点状态复盘
逐个有变动的论点：触发了什么条件、星级路径、反证是否被兑现

### 三、各资产月度表现与归因
用上方月度区间表做归因（β还是α、驱动因子、月内拐点），不逐日复述。
注意单位：收益率/利差变化用bp，百分点序列用pp，价格序列用%

### 四、预测裁决与配置倾向复盘
逐条本月到期预测给出 已命中/已证伪/无法裁决/未触发 裁决并引用具体数值与观测日；
无证据不得裁决。错判要指出错在哪一环（方向/时点/幅度/传导假设）。
配置倾向调整只在触发条件被引擎核验跨越时提出，否则明确"维持"

### 五、下月监控重点
3-5个带具体阈值的前瞻监控点（体制切换/论点触发/预测到期日）

若数据块标注【预览】：本期为期间未结束的部分数据，所有结论降一档表述并写明覆盖限制。"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--month', help='YYYYMM,指定复盘月份(当月未完结则按【预览】生成)')
    ap.add_argument('--dry-run', action='store_true', help='只装配数据不调用GLM')
    args = ap.parse_args()

    if args.month:
        ym = args.month
    else:
        # auto: 仅当上一自然月已完结且今天是其后第一个周五(report_generator同款规则)
        try:
            from report_generator import pending_completed_month
        except ImportError:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from report_generator import pending_completed_month
        ym = pending_completed_month()
        if not ym:
            print("非月度复盘触发日(须为期间结束后第一个周五),如需强制生成请用 --month YYYYMM")
            return

    print("=" * 60)
    print(f"📅 月度复盘生成器 ({ym})")
    print("=" * 60)

    data_block, series, ctx, preview = build_data_block(ym)
    tag = "【预览】" if preview else ""
    print(f"✅ 数据装配: {len(series)}个序列 / {len(ctx['scorecard_timeline'])}周评分卡 / {len(ctx['weekly_reports'])}期周报"
          + (" ⚠️期间未完结,预览模式" if preview else ""))

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    data_path = os.path.join(OUTPUT_DIR, f'monthly_data_{ym}.md')
    with open(data_path, 'w', encoding='utf-8') as f:
        f.write(data_block)
    print(f"💾 月度数据块: {data_path}")

    if args.dry_run:
        print("🏃 dry-run: 跳过GLM调用")
        return

    from report_generator import load_prompt, _call_glm
    system_prompt = load_prompt('monthly_review_prompt.md')
    user_prompt = f"""请基于以下{ym[:4]}年{int(ym[4:6])}月的原始数据汇总，生成{tag}月度复盘。

{data_block}

{MONTHLY_STRUCTURE}"""

    print(f"🤖 调用GLM生成月报(输入约{len(system_prompt) + len(user_prompt)}字符)...")
    md = _call_glm(system_prompt, user_prompt)
    if len(md.strip()) < 500:
        print(f"❌ 返回过短({len(md)}字符),放弃")
        sys.exit(1)

    # IA-P0-1-FIX7(IA-DEF-004): 月报数据来源为历史原始采集序列直读,当前架构
    # 无法证明**整个月**每一交易日快照链的数据质量(逐日Gate A结论并不随月聚合)。
    # 保守处置: 输出一律为UNVALIDATED研究草稿——文件名显式标记,不占用正式合格
    # 文件名(不覆盖既有合格报告),下游以文件名即可区分,不得作为合格正式研究
    # 产出引用。历史分析能力(数据装配/预览/期间完结判定)保持不变。
    out_path = os.path.join(OUTPUT_DIR, f'monthly_review_{ym}_UNVALIDATED.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"<!-- {tag}月度复盘(研究草稿) {datetime.now().strftime('%Y-%m-%d %H:%M')} | investment-agent"
                + (" | PREVIEW_PERIOD_INCOMPLETE" if preview else "")
                + " | UNVALIDATED: 历史原始序列直读,未经完整期间快照链质量验证 -->\n\n")
        f.write("> ⚠️ **UNVALIDATED 研究草稿**: 数据来源为历史原始采集序列直读,"
                "未经研究快照链(Gate A)对整个期间的完整质量验证,不得作为合格正式"
                "研究报告引用或作为长期状态回写依据。\n\n")
        f.write(md)
    print(f"✅ 月报草稿已保存(UNVALIDATED): {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    main()
