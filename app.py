#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""investment-agent 研究工作台 —— 本地Web统一入口(W5, 2026-11-08)。

启动(项目根):
    streamlit run app.py
(需先安装工作台依赖: pip install -r requirements-workbench.txt,详见 docs/USER_GUIDE.md)

四个页面: 全球宏观概览 / 金融市场变化 / 历史研究 / AI研究。
全部数值来自本地快照与采集档(显示观测日期与来源),缺失如实标注;
不做实时行情、不做投资建议、不连任何云端服务。数据加载逻辑见
scripts/workbench_data.py(纯函数层,可离线测试)。
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
              '内容不构成投资建议,投资观点请自行形成并自担风险。')


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
    page = st.radio('导航', ['全球宏观概览', '金融市场变化', '历史研究', 'AI 研究',
                             '关于与限制'], label_visibility='collapsed')
    st.divider()
    st.caption(DISCLAIMER)


# ── 页面一: 全球宏观概览 ─────────────────────────────────────────────
def page_overview():
    st.header('全球宏观概览')
    if SNAP is None:
        st.warning('本地无研究快照。请先运行 `python3 run_weekly.py` 完成一次数据采集。')
        return
    econ = st.selectbox('经济体', ['US', 'CN', 'EA', 'JP', 'GLOBAL', 'HK'],
                        format_func=lambda k: f'{wd.ECONOMY_LABELS.get(k, k)}({k})')
    rows = wd.overview_rows(SNAP, REGISTRY, econ)
    n_miss = sum(1 for r in rows if r['当前值'] == '缺失')
    st.caption(f"快照日 {META['date']} · {wd.ECONOMY_LABELS.get(econ, econ)} 活跃指标 "
               f"{len(rows)} 项(缺失 {n_miss} 项,如实列出) · 变化口径: 周/月内/年初至今")
    st.dataframe(rows, width='stretch', height=560)
    with st.expander('数据来源状态(sources_status)'):
        st.json(SNAP.get('sources_status', {}))


# ── 页面二: 金融市场变化 ─────────────────────────────────────────────
def page_market():
    st.header('金融市场变化')
    if SNAP is None:
        st.warning('本地无研究快照。请先运行 `python3 run_weekly.py` 完成一次数据采集。')
        return
    rows = wd.market_rows(SNAP, REGISTRY)
    st.caption(f"快照日 {META['date']} · 资产类指标(股/债/汇/商品/加密/信用/波动率)"
               f"共 {len(rows)} 项 · 周变化=最近一个交易周,月=月内,年内=年初至今")
    st.dataframe(rows, width='stretch', height=560)
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
    window = st.selectbox('窗口', ['全部', '1年', '6个月', '3个月', '1个月'])
    _render_series(series, window)


def _render_series(series, window):
    import pandas as pd
    n = {'全部': 0, '1年': 252, '6个月': 126, '3个月': 63, '1个月': 21}[window]
    dates, values = series['dates'], series['values']
    if n:
        dates, values = dates[-n:], values[-n:]
    df = pd.DataFrame({series['label']: values}, index=pd.to_datetime(dates))
    st.caption(f"来源: {series['source']} · 观测点 {len(dates)} 个"
               f"({dates[0]} → {dates[-1]}) · 单位: {series['unit'] or '—'}")
    st.line_chart(df, height=340)
    if len(values) >= 2:
        first, last = values[0], values[-1]
        try:
            chg = (last - first) / abs(first) * 100
            st.caption(f"窗口首值 {first:,.4g} → 末值 {last:,.4g}"
                       f"(区间变化 {chg:+.2f}%,由本地序列计算)")
        except (TypeError, ZeroDivisionError):
            pass


# ── 页面三: 历史研究 ─────────────────────────────────────────────────
def page_history():
    st.header('历史研究')
    options = wd.series_capable_metrics(SNAP, REGISTRY)
    if not options:
        st.warning('本地暂无历史序列。请先运行 `python3 run_weekly.py` 采集数据'
                   '(克隆仓库不含历史数据,数据须自行采集积累)。')
        return
    sel = st.selectbox('选择指标', options,
                       format_func=lambda o: f"{o['label']}({o['metric_id']})")
    series, err = wd.metric_series(sel['metric_id'], SNAP)
    if series is None:
        st.warning(f'无历史序列: {err}')
        return
    window = st.selectbox('窗口', ['全部', '1年', '6个月', '3个月', '1个月'], key='hist_w')
    _render_series(series, window)
    st.subheader('跨指标对比')
    sel2 = st.selectbox('对比指标(叠加显示)', ['(不对比)'] + [o['metric_id'] for o in options])
    if sel2 != '(不对比)' and sel2 != sel['metric_id']:
        s2, err2 = wd.metric_series(sel2, SNAP)
        if s2 is None:
            st.warning(f'对比序列不可用: {err2}')
        else:
            import pandas as pd
            df = pd.DataFrame({series['label']: series['values']},
                              index=pd.to_datetime(series['dates']))
            df2 = pd.DataFrame({s2['label']: s2['values']},
                               index=pd.to_datetime(s2['dates']))
            st.line_chart(df.join(df2, how='inner'), height=340)
            st.caption('两序列按共同观测日对齐(inner join);数值各自保留原单位,'
                       '量纲不同时请谨慎解读(相关性≠因果)。')


# ── 页面四: AI 研究 ──────────────────────────────────────────────────
def page_research():
    st.header('AI 研究')
    st.caption('基于本地快照事实的接地作答(e2eb 查询栈,零网络);'
               'AI 解释为可选增强(可选模型 API,三参模板见 .env.example)。')
    if SNAP is None:
        st.warning('本地无研究快照,研究问题无法作答。请先运行 `python3 run_weekly.py`。')
        return
    with st.expander('当前支持的问题类型(如实声明,不夸大)'):
        st.text(wd.SUPPORTED_CONCEPT_HINT)
    q = st.text_area('研究问题', value='美国和日本10年期国债收益率差是多少？', height=80)
    col1, col2, col3 = st.columns(3)
    do_ask = col1.button('本地接地作答', type='primary')
    do_glm = col2.button('AI 解释(可选,需模型 API)')
    do_save = col3.button('存入研究档案')
    if do_ask or q and (do_glm or do_save):
        with st.spinner('本地查询中…'):
            res = wd.ask_local(q, SNAP)
        if res['status'] == 'answered':
            st.success(f"已作答(接地于快照 {META['date']})")
        elif res['status'] == 'refusal':
            st.warning('查询被数据门禁拒绝(Gate A 未放行或缺数据)——如实拒绝,不作猜测。')
        elif res['status'] == 'out_of_scope':
            st.error('越界问题(投资建议/交易类),不作答。')
        elif res['status'] in ('no_registry_identity', 'unmapped'):
            st.info(f"暂不支持的问题类型({res['status']})——见上方支持范围说明。")
        else:
            st.error(res['answer_text'])
        st.markdown(res['answer_text'])
        if res.get('values'):
            st.table([{ '指标绑定': k, '数值': v} for k, v in res['values'].items()])
        st.session_state['last_answer'] = res
        st.session_state['last_q'] = q
    if do_glm:
        last = st.session_state.get('last_answer')
        if not last or st.session_state.get('last_q') != q:
            res = wd.ask_local(q, SNAP)
            st.session_state['last_answer'] = res
            st.session_state['last_q'] = q
            last = res
        if last['status'] != 'answered':
            st.warning('AI 解释仅对接地作答成功的问题开放(数值必须先经本地核实)。')
        else:
            with st.spinner('AI 解释生成中(真实模型调用,产生少量费用)…'):
                out = wd.glm_explain(q, last['answer_text'])
            if out['ok']:
                st.subheader('AI 解释(基于上方已核实事实;【推断】部分非事实)')
                st.markdown(out['text'])
            else:
                st.error(out['error'])
    if do_save:
        qid, err = wd.save_to_archive(q, SNAP)
        if qid:
            st.success(f'已存入研究档案: {qid}(data/research/research_archive/,append-only)')
        else:
            st.error(err or '归档失败')


# ── 关于与限制 ───────────────────────────────────────────────────────
def page_about():
    st.header('关于与限制')
    st.markdown(
        f'- **当前快照**: {META["date"]} · Gate A={META["gate_a"]}\n'
        '- **已实现**: 四大经济体宏观概览 / 资产市场变化 / 本地历史序列与对比 / '
        '四类接地研究问题 / AI 研究解释(可选,需模型 API)\n'
        '- **不支持(如实声明)**: 实时行情、任意自然语言研究问题(当前四类,见AI研究页)、'
        '投资建议/资产配置/价格预测(产品红线,见 PRODUCT-GOAL.md)、'
        '多用户/云端/协作\n'
        '- **数据窗口**: 由本地采集积累决定(克隆仓库不含历史数据)\n'
        '- **月报/季报**: 历史兼容能力,自动级联默认关闭(IA_AUTO_MONTHLY=1 可开启),'
        '人设改革登记于 docs/MW-V1-AUDIT-DEFERRED.md\n')
    st.warning(DISCLAIMER)


{'全球宏观概览': page_overview, '金融市场变化': page_market,
 '历史研究': page_history, 'AI 研究': page_research,
 '关于与限制': page_about}[page]()
