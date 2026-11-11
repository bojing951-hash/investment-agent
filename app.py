#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""investment-agent 研究工作台 —— 本地Web统一入口(W5→Charter8, 2026-11-10)。

启动(项目根):
    streamlit run app.py
(需先安装工作台依赖: pip install -r requirements-workbench.txt,详见 docs/USER_GUIDE.md)

Charter8 四页(Charter 8 章程, 2026-11-10):
  ① 全球宏观全景   经济体×维度覆盖表 + 市场指标 1m/3m/1y/5y 窗口(interval_change
                   自配对口径,与 ia_cli compare 同函数) + 历史走势
  ② 全球金融传导地图 config/transmission_edges.json 静态策划档——每条边带 qb_source
                   指向真实研究归档,E1/E2/E3 证据分级图例;未验证因果不画为事实
  ③ 机构观点矩阵   data/institutions/views 存储(schema v1.1,只装载 linter 合规件)
  ④ 独立研究结论   本地研究档案(QB 链)+ Agent Native 引导

全部数值来自本地快照与采集档(显示观测日期与来源),缺失如实标注;
**零模型调用**: 页面不发起任何模型 API 请求(无模型环境=数据图+缓存研究
+Agent Native 引导);不做实时行情、不做投资建议、不连任何云端服务。
数据加载逻辑见 scripts/workbench_data.py(纯函数层,可离线测试)。
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
for p in (ROOT, os.path.join(ROOT, 'scripts')):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import streamlit as st  # noqa: E402
except ImportError:
    print('缺少 streamlit。请先安装工作台依赖:\n'
          '  pip install -r requirements-workbench.txt\n'
          '然后运行: streamlit run app.py\n'
          '详见 docs/USER_GUIDE.md「研究工作台」一章。')
    sys.exit(1)

import workbench_data as wd  # noqa: E402

st.set_page_config(page_title='investment-agent 研究工作台',
                   page_icon='🔬', layout='wide')

DISCLAIMER = ('本工作台是宏观**研究工具**: 所有数值来自本地采集数据,可能滞后或有误;'
              '内容不构成投资建议,投资观点请自行形成并担风险。')


@st.cache_data(show_spinner=False)
def _load_state():
    snap, note = wd.latest_snapshot()
    registry = wd.load_registry()
    return snap, note, registry


SNAP, SNAP_NOTE, REGISTRY = _load_state()
META = wd.snapshot_meta(SNAP)

# ── 侧栏: 快照状态 + 导航 ────────────────────────────────────────────
with st.sidebar:
    st.title('🔬 研究工作台')
    st.caption('开源 AI 全球宏观研究工作台')
    if SNAP is None:
        st.warning(f'本地暂无研究快照:{SNAP_NOTE}')
    else:
        gate_color = {'PASS': 'green', 'DEGRADED': 'orange'}.get(META['gate_a'], 'red')
        st.markdown(f"**数据快照**: {META['date']}")
        st.markdown(f"**Gate A**: :{gate_color}[{META['gate_a']}]")
        if META['missing']:
            with st.expander(f"缺失指标 {len(META['missing'])} 项(如实披露)"):
                st.write('、'.join(META['missing']))
        if META['degraded']:
            with st.expander(f"降级指标 {len(META['degraded'])} 项"):
                st.write('、'.join(META['degraded']))
    st.divider()
    page = st.radio('导航', ['全球宏观全景', '全球金融传导地图', '机构观点矩阵',
                             '独立研究结论', '关于与限制'],
                    label_visibility='collapsed')
    st.divider()
    st.caption(DISCLAIMER)


# ── 页面①: 全球宏观全景 ─────────────────────────────────────────────
def page_panorama():
    st.header('全球宏观全景')
    if SNAP is None:
        st.warning('本地无研究快照。请先运行 `python3 run_weekly.py` 完成一次数据采集。')
        return
    st.subheader('经济体 × 维度覆盖表')
    mx = wd.economy_dimension_matrix(SNAP, REGISTRY)
    st.caption(mx['note'] + ' · 维度=注册表 asset_class 权威口径')
    st.dataframe(mx['rows'], width='stretch', height=260)

    st.subheader('分经济体指标表')
    econ = st.selectbox('经济体', ['US', 'CN', 'EA', 'JP', 'GLOBAL', 'HK'],
                        format_func=lambda k: f'{wd.ECONOMY_LABELS.get(k, k)}({k})')
    rows = wd.overview_rows(SNAP, REGISTRY, econ)
    n_miss = sum(1 for r in rows if r['当前值'] == '缺失')
    st.caption(f"快照日 {META['date']} · {wd.ECONOMY_LABELS.get(econ, econ)} 活跃指标 "
               f"{len(rows)} 项(缺失 {n_miss} 项,如实列出) · 变化口径: 周=ISO周前末观测基准 / "
               "月内=前一自然月末基准 / 年初至今=前一自然年末基准(非当年首日)")
    st.dataframe(rows, width='stretch', height=480)

    st.subheader('市场多窗口变化(1m / 3m / 1y / 5y)')
    st.caption('区间变动=interval_change 自配对口径(基准=严格早于窗口起点的最后观测;'
               '利率 pp/价格 %/计数绝对差)——与 `ia_cli compare --start <T-k>` 同函数,'
               '数据不足如实标"不可用"。Charter9: 含利率族(rates_yield/policy_rate/'
               'curve_slope)——美债/德日国债/2s10s 的窗口变化在此表可答。')
    wrows = wd.market_window_rows(SNAP, REGISTRY)
    st.caption(f"资产类指标 {len(wrows)} 项 · 快照日 {META['date']}")
    st.dataframe(wrows, width='stretch', height=560)

    st.subheader('历史走势')
    options = wd.series_capable_metrics(SNAP, REGISTRY)
    if not options:
        st.info('本地暂无可绘制的序列数据(快照 series_store 与采集档 series 均为空)。')
        return
    default = next((o['metric_id'] for o in options if o['metric_id'] == 'SPX'),
                   options[0]['metric_id'])
    sel = st.selectbox('选择资产', options,
                       format_func=lambda o: f"{o['label']}({o['metric_id']})",
                       index=[o['metric_id'] for o in options].index(default))
    series, err = wd.metric_series(sel['metric_id'], SNAP)
    if series is None:
        st.warning(f'无历史序列: {err}')
        return
    window = st.selectbox('窗口', ['全部', '5年', '1年', '6个月', '3个月', '1个月'])
    _render_series(series, window)


def _render_series(series, window):
    import pandas as pd
    # Charter9 P0-4: 窗切片=日历日期截取(wd.slice_series_window,零频率假设——
    # 旧版固定观测数 252/126/63/21 按日频设计,月频序列"1年"实显21年);
    # 首末变化 caption=族感知(wd.series_change_caption,利率 pp/价格 %/计数绝对差,
    # 与窗口表口径一致——旧版一律水平百分变化)。
    dates, values, slice_note = wd.slice_series_window(
        series['dates'], series['values'], window)
    if not dates:
        st.warning(f'窗口内无观测: {slice_note}')
        return
    df = pd.DataFrame({series['label']: values}, index=pd.to_datetime(dates))
    st.caption(f"来源: {series['source']} · 窗口: {slice_note} · 单位: {series['unit'] or '—'}"
               " · ETF价格为复权基(近似总回报,采集器 auto_adjust=True)")
    st.line_chart(df, height=340)
    if len(values) >= 2:
        cap = wd.series_change_caption(series['unit'], values[0], values[-1])
        if cap['text']:
            st.caption(cap['text'] + '(由本地窗口序列计算)')


# ── 页面②: 全球金融传导地图 ─────────────────────────────────────────
def page_transmission():
    st.header('全球金融传导地图')
    try:
        doc = wd.transmission_edges()
    except (OSError, ValueError) as e:
        st.error(f'传导边档不可用: {e}')
        return
    st.caption('静态策划档(零模型调用): 每条边/机制结论来自已归档真实研究'
               '(qb_source 指向 QB 研究档案),无凭空策划边。')

    st.subheader('图例(证据分级)')
    gr = doc['evidence_grading']
    sem = doc['category_semantics']
    st.markdown(
        f"- **E1** {gr['E1']}\n"
        f"- **E2** {gr['E2']}\n"
        f"- **E3** {gr['E3']}\n"
        f"- **实线(较强渠道)** {sem['strong']}\n"
        f"- **虚线(近零渠道)** {sem['near_zero']}\n"
        f"- {doc['display_rule']}")

    edges = doc['edges']
    strong = [e for e in edges if e['category'] == 'strong']
    near = [e for e in edges if e['category'] == 'near_zero']
    st.subheader(f'较强渠道({len(strong)} 条,方向可引=统计事实非因果)')
    st.dataframe([{'渠道': f"{e['from']} × {e['to']}", '机制': e['channel_label'],
                   'r': e['r'], 'n(变化对)': e['n'], '窗': e['window'],
                   '证据级': e['evidence_level'], '来源': e['qb_source'],
                   '备注': e['note']} for e in strong],
                 width='stretch', height=420)
    st.subheader(f'近零渠道({len(near)} 条——流行叙事在本地数据中 E1 不支持)')
    st.dataframe([{'渠道': f"{e['from']} × {e['to']}", '机制': e['channel_label'],
                   'r': e['r'], 'n(变化对)': e['n'], '窗': e['window'],
                   '证据级': e['evidence_level'], '来源': e['qb_source'],
                   '备注': e['note']} for e in near],
                 width='stretch', height=360)

    ss = doc.get('structural_summary') or {}
    if ss:
        st.info(f"**结构性结论({ss['qb_source']})**: {ss['text']}")

    st.subheader('机制层结论(仍成立 / 已不适用 / 不可验)')
    verdict_badge = {'still_valid': ('✅ 仍成立', 'green'),
                     'not_applicable': ('⛔ 已不适用(E3)', 'red'),
                     'unverifiable': ('❓ 不可验(缺环)', 'orange')}
    for f in doc['mechanism_findings']:
        label, color = verdict_badge.get(f['verdict'], (f['verdict'], 'gray'))
        with st.expander(f"{label} · {f['mechanism_label']}({f['evidence_level']})"):
            st.markdown(f"- {f['note']}")
            st.caption(f"涉及指标: {'、'.join(f['metrics'])} · 来源: {f['qb_source']}")


# ── 页面③: 机构观点矩阵 ─────────────────────────────────────────────
def page_views():
    st.header('机构观点矩阵')
    import view_store as vs
    vm = wd.views_matrix()
    st.caption(f"schema v{vm['schema_version']} · 只装载 linter 合规件"
               f"({len(vm['rows'])} 份;隔离件绝不入面) · 零模型调用,纯本地存储读取")
    if vm['n_quarantined']:
        st.warning(f"{vm['n_quarantined']} 份被 linter 隔离(见 `python3 ia_cli.py views lint`);"
                   '本页不展示违规数据。')
    if not vm['rows']:
        st.info('views 存储暂无合规观点档(data/institutions/views/VIEW-*.json)。')
        return

    st.subheader('机构 × 主题矩阵')
    st.caption('单元格=该机构该主题的 view 编号(末三位);「—」=未覆盖')
    st.dataframe(vm['matrix'], width='stretch', height=320)

    st.subheader('观点清单')
    st.dataframe(vm['rows'], width='stretch', height=360)

    st.subheader('单份详情')
    sel = st.selectbox('选择观点', vm['rows'],
                       format_func=lambda r: f"{r['view_id']} · {r['机构']} · {r['标题'][:40]}")
    doc, reason = vs.get_view(sel['view_id'])
    if doc is None:
        st.warning(reason)
        return
    att_badge = {'institution_stated': '🏛 机构明示', 'ai_inferred': '🤖 AI 推导'}
    st.markdown(f"**{doc['institution']['name']}**({doc['institution']['type']})"
                f" · 发布 {doc['publish_date']} · 采集 {doc['fetch_date']} · "
                f"期限 {doc['view_horizon']} · 来源类型 {doc['source_type']}")
    st.markdown(f"[原文链接]({doc['source_url']}) · 存储纪律: 元数据+短引文+链接"
                f"(quote≤500 字符)")
    # Charter9 P0-2: VP sidecar 验证标签(独立于 views v1.1;编排层写入,引擎校验)
    import view_plausibility as vpl
    vp, vp_reason = vpl.load_vp(sel['view_id'])
    if vp is not None:
        vp_ok, vp_errs = vpl.validate_vp(vp, doc)
        if vp_ok:
            st.markdown(f"**验证标签: {vp['view_label']}**(假设级链六标签最保守"
                        "聚合,裁定④;as_of "
                        f"{vp.get('as_of', '—')})")
            st.table(vpl.vp_badge_rows(vp))
            st.caption('VP sidecar=data/institutions/verification/'
                       'VP-*.json(不动 views 档);判定依据= view_verifier '
                       '--mode C 机械 verdict 的标签映射')
        else:
            st.warning('VP sidecar 校验失败,不入面: ' + ';'.join(vp_errs[:3]))
    else:
        st.caption(f'验证标签: 暂无({vp_reason})')
    for i, cv in enumerate(doc['core_views'], 1):
        badge = att_badge.get(cv['attribution'], cv['attribution'])
        st.markdown(f"**观点{i}** [{badge} · {cv['basis']}] {cv['statement']}")
        if cv.get('quote'):
            st.caption(f"原文佐证: “{cv['quote']}”")
    if doc['forecasts']:
        st.markdown('**预测点位**')
        st.table([{'目标': f['target'], '值/方向': f['value_or_direction'],
                   '期限': f['horizon'],
                   'attribution': att_badge.get(f['attribution'], f['attribution'])}
                  for f in doc['forecasts']])
    # Charter9 P0-2 页③渲染修复: mechanism_steps/evidence_cited 在 schema v1.1
    # 为必填采集面,此前单份详情从未渲染(工程遗漏,非数据缺席)
    if doc['mechanism_steps']:
        st.markdown('**传导机制(机构自述)**')
        for i, ms in enumerate(doc['mechanism_steps'], 1):
            badge = att_badge.get(ms.get('attribution'), ms.get('attribution'))
            st.markdown(f"{i}. [{badge}] {ms['step']}")
            if ms.get('quote'):
                st.caption(f"原文佐证: “{ms['quote']}”")
    if doc['evidence_cited']:
        st.markdown('**引用证据(机构自述)**')
        for ec in doc['evidence_cited']:
            badge = att_badge.get(ec.get('attribution'), ec.get('attribution'))
            st.markdown(f"- [{badge}] {ec['statement']}")
            if ec.get('quote'):
                st.caption(f"原文佐证: “{ec['quote']}”")
    for title, key in (('关键假设', 'key_assumptions'), ('风险因素', 'risk_factors'),
                       ('证伪条件', 'falsification_conditions')):
        items = doc[key]
        if items:
            st.markdown(f"**{title}**")
            for it in items:
                badge = att_badge.get(it['attribution'], it['attribution'])
                text = it.get('condition') or it.get('statement') or ''
                st.markdown(f"- [{badge}] {text}")
    if doc['revisions']:
        st.markdown('**观点修订(只追加)**')
        st.table([{'日期': r['date'], '变更': r['change'], '来源': r['source_url']}
                  for r in doc['revisions']])
    if doc['completeness_notes']:
        with st.expander('完整性说明(诚实缺席披露)'):
            st.write(doc['completeness_notes'])


# ── 页面④: 独立研究结论 ─────────────────────────────────────────────
def page_research():
    st.header('独立研究结论')
    st.caption('本地研究档案(QB 链,append-only)——缓存研究成果展示,零模型调用;'
               '页面不发起任何 AI 请求。')
    rows = wd.research_archive_rows(limit=100)
    if not rows:
        st.info('本地暂无研究档案(data/research/research_archive/)。'
                '经 `python3 ia_cli.py research --question … --archive` 生成。')
    else:
        st.dataframe(rows, width='stretch', height=420)
        sel = st.selectbox('展开全文', rows,
                           format_func=lambda r: f"{r['query_id']} · {r['问题'][:44]}")
        try:
            import research_archive as ra
            full = ra.load_research_full(sel['query_id'])
            at = (full or {}).get('answer_text') or '(无 answer_text sidecar)'
            st.markdown(at[:8000])
            chain = (full or {}).get('follow_up_of')
            if chain:
                st.caption(f"承接前档: {chain}(QB 链)")
        except (OSError, ValueError) as e:
            st.warning(f'研究正文读取失败: {e}')

    st.subheader('Agent Native 引导(零默认付费 API)')
    st.info(
        '- 本工作台**不内置任何模型调用**;数据图+缓存研究即全部页面能力。\n'
        '- 专题研究走 Agent Native: 经 global-macro-research Skill 调用 '
        '`ia_cli.py` 十个能力(doctor/update/overview/changes/history/compare/'
        'analog/research/archive/views)组合研究。\n'
        '- 机构观点确定性验证: `python3 scripts/view_verifier.py VIEW-YYYYMMDD-NNN`'
        '(证据表=本地快照事实+区间变动,零 AI 判断)。\n'
        '- 模型 API(可选)仅由用户显式配置 MODEL_* 三参后,经 CLI/Skill 使用;'
        '工作台页面永不调用。')


# ── 关于与限制 ───────────────────────────────────────────────────────
def page_about():
    st.header('关于与限制')
    st.markdown(
        f'- **当前快照**: {META["date"]} · Gate A={META["gate_a"]}\n'
        '- **Charter8 四页**: 全球宏观全景(经济体×维度+市场 1m/3m/1y/5y) / '
        '全球金融传导地图(归档研究边+E1E2E3 分级) / 机构观点矩阵(schema v1.1 '
        '存储,linter 合规件) / 独立研究结论(研究档案 QB 链)\n'
        '- **页面零模型调用**: 不发起任何模型 API 请求;专题研究走 Agent Native'
        '(Skill+ia_cli 十能力),模型 Key 仅用户显式配置后经 CLI 使用\n'
        '- **不支持(如实声明)**: 实时行情、投资建议/资产配置/价格预测'
        '(产品红线,见 PRODUCT-GOAL.md)、多用户/云端/协作\n'
        '- **数据窗口**: 由本地采集积累决定(克隆仓库不含历史数据);'
        '5y 窗口需≥5 年本地序列,不足如实标"不可用"\n'
        '- **月报/季报**: 历史兼容能力,自动级联默认关闭(IA_AUTO_MONTHLY=1 可开启),'
        '人设改革登记于 docs/MW-V1-AUDIT-DEFERRED.md\n')
    st.warning(DISCLAIMER)


{'全球宏观全景': page_panorama, '全球金融传导地图': page_transmission,
 '机构观点矩阵': page_views, '独立研究结论': page_research,
 '关于与限制': page_about}[page]()
