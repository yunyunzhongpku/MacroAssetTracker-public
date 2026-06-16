#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
相关性与风险页面

3-Tab 结构：相关性矩阵 / 滚动相关性 / 风险指标
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from itertools import combinations
from config import ASSET_NAMES
from ui.components import dataframe_with_download
from ui.utils import filter_data_by_date_range, analyze_correlation_matrix
from analyzer import calculate_risk_metrics_simplified


def show_correlation_risk(analyzer, start_date, end_date, selected_assets):
    """相关性与风险页面（接收全局参数）"""

    st.markdown("""
    <div class='signal-header'>
        <h1>🔗 相关性与风险分析</h1>
        <p>深度分析资产间相关性关系与风险暴露</p>
    </div>
    """, unsafe_allow_html=True)

    if not selected_assets:
        st.warning("⚠️ 请在侧边栏选择要分析的资产")
        return
    if start_date is None or end_date is None:
        st.warning("⚠️ 无法确定日期范围")
        return

    tab1, tab2, tab3 = st.tabs(["🔥 相关性矩阵", "📈 滚动相关性", "⚠️ 风险指标"])

    # ── Tab 1: 相关性矩阵 ──
    with tab1:
        _show_correlation_matrix(analyzer, start_date, end_date, selected_assets)

    # ── Tab 2: 滚动相关性 ──
    with tab2:
        _show_rolling_correlation(analyzer, start_date, end_date, selected_assets)

    # ── Tab 3: 风险指标 ──
    with tab3:
        _show_risk_metrics(analyzer, start_date, end_date, selected_assets)


# ────────────────────────────────────────────────
# Tab 1: 相关性矩阵
# ────────────────────────────────────────────────
def _show_correlation_matrix(analyzer, start_date, end_date, selected_assets):
    available = [a for a in selected_assets if a in analyzer.returns.columns]
    if len(available) < 2:
        st.info("📊 请在侧边栏选择至少 2 个资产")
        return

    # 方法选择（行内）
    method_col, info_col = st.columns([1, 3])
    with method_col:
        method = st.selectbox("相关性方法", ["pearson", "spearman"], index=0, key="corr_method")

    filtered_returns = filter_data_by_date_range(analyzer.returns[available], start_date, end_date)
    if filtered_returns is None or len(filtered_returns) == 0:
        st.error("⚠️ 选定日期范围内没有足够的数据")
        return

    corr_matrix = filtered_returns.corr(method=method)
    with info_col:
        st.caption(f"基于 {len(filtered_returns)} 个交易日  ·  {method.title()} 方法")

    # 热力图
    fig = px.imshow(
        corr_matrix, color_continuous_scale='RdBu_r', aspect="auto",
        title="资产相关性矩阵", labels={'color': '相关系数'}, zmin=-1, zmax=1,
    )
    fig.update_traces(text=np.round(corr_matrix.values, 3), texttemplate="%{text}", textfont={"size": 10})
    fig.update_layout(width=800, height=600, title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    # 配对分析
    corr_analysis = analyze_correlation_matrix(corr_matrix, threshold=0.5)
    if corr_analysis:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📈 高相关性资产对 (|r| > 0.5)**")
            if corr_analysis['high_correlation_pairs']:
                for p in corr_analysis['high_correlation_pairs']:
                    icon = "🔴" if p['correlation'] > 0 else "🔵"
                    st.write(f"{icon} **{p['asset1']}** ↔ **{p['asset2']}**: {p['correlation']:.3f}")
            else:
                st.info("无高相关性资产对")
        with col2:
            st.markdown("**📉 低相关性资产对 (|r| < 0.3)**")
            if corr_analysis['low_correlation_pairs']:
                for p in corr_analysis['low_correlation_pairs'][:10]:
                    st.write(f"💡 **{p['asset1']}** ↔ **{p['asset2']}**: {p['correlation']:.3f}")
            else:
                st.info("无低相关性资产对")

        # 统计摘要
        c1, c2, c3 = st.columns(3)
        c1.metric("平均相关性", f"{corr_analysis['average_correlation']:.3f}")
        c2.metric("最高相关性", f"{corr_analysis['max_correlation']:.3f}")
        c3.metric("最低相关性", f"{corr_analysis['min_correlation']:.3f}")


# ────────────────────────────────────────────────
# Tab 2: 滚动相关性
# ────────────────────────────────────────────────
def _show_rolling_correlation(analyzer, start_date, end_date, selected_assets):
    available = [a for a in selected_assets if a in analyzer.returns.columns]
    if len(available) < 2:
        st.info("📊 请在侧边栏选择至少 2 个资产")
        return

    # 构建跨类别代表性配对（每个大类取第1个已选资产作为代表）
    from config import ASSETS, ASSET_NAMES
    category_reps = []
    for cat, codes in ASSETS.items():
        if cat == "海外现货参考":
            continue
        names = [ASSET_NAMES.get(c, c) for c in codes]
        reps = [n for n in names if n in available]
        if reps:
            category_reps.append((cat, reps[0]))

    # 生成跨类别配对
    default_pairs = []
    for i in range(len(category_reps)):
        for j in range(i + 1, len(category_reps)):
            default_pairs.append((category_reps[i][1], category_reps[j][1]))

    all_pairs = list(combinations(available, 2))

    # 参数行
    win_col, pair_col = st.columns([1, 3])
    window_options = {"1个月 (22天)": 22, "3个月 (66天)": 66}
    with win_col:
        selected_windows = st.multiselect(
            "滚动窗口", list(window_options.keys()),
            default=["1个月 (22天)"], key="rolling_win_tab",
        )

    if not selected_windows:
        st.info("📊 请选择至少一个滚动窗口")
        return

    # 配对选择器：用 multiselect 让用户选择要展示的配对
    pair_labels = [f"{a} ↔ {b}" for a, b in all_pairs]
    default_labels = [f"{a} ↔ {b}" for a, b in default_pairs if f"{a} ↔ {b}" in pair_labels]
    with pair_col:
        selected_pair_labels = st.multiselect(
            "选择资产配对", pair_labels,
            default=default_labels, key="rolling_pairs_select",
        )

    if not selected_pair_labels:
        st.info("📊 请选择至少一个资产配对")
        return

    # 从 label 还原回 pair tuple
    label_to_pair = {f"{a} ↔ {b}": (a, b) for a, b in all_pairs}
    display_pairs = [label_to_pair[l] for l in selected_pair_labels if l in label_to_pair]

    # 计算
    returns_subset = analyzer.returns[available].sort_index()
    start_ts, end_ts = pd.Timestamp(start_date), pd.Timestamp(end_date)
    max_window = max(window_options[w] for w in selected_windows)

    start_pos = returns_subset.index.searchsorted(start_ts, side='left')
    end_pos = returns_subset.index.searchsorted(end_ts, side='right')
    lookback_start = max(0, start_pos - (max_window - 1))
    calc_returns = returns_subset.iloc[lookback_start:end_pos]

    fig = go.Figure()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
              '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    idx = 0

    for wname in selected_windows:
        wdays = window_options[wname]
        for a1, a2 in display_pairs:
            if a1 not in calc_returns.columns or a2 not in calc_returns.columns:
                continue
            pair_ret = calc_returns[[a1, a2]].dropna(how='any')
            if len(pair_ret) < wdays:
                continue
            rc = pair_ret[a1].rolling(window=wdays, min_periods=wdays).corr(pair_ret[a2])
            visible = rc.loc[start_ts:end_ts].dropna()
            if visible.empty:
                continue
            fig.add_trace(go.Scatter(
                x=visible.index, y=visible.values, mode='lines',
                name=f"{a1} ↔ {a2} ({wname})",
                line=dict(color=colors[idx % len(colors)], width=2),
                hovertemplate='<b>%{fullData.name}</b><br>日期: %{x}<br>相关系数: %{y:.3f}<extra></extra>',
            ))
            idx += 1

    if idx == 0:
        st.warning("⚠️ 当前范围内没有足够数据计算滚动相关性")
        return

    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(
        title="资产对滚动相关性", xaxis_title="日期", yaxis_title="相关系数",
        yaxis=dict(range=[-1, 1]), hovermode='x unified', height=550,
        template="plotly_white",
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)


# ────────────────────────────────────────────────
# Tab 3: 风险指标
# ────────────────────────────────────────────────
def _show_risk_metrics(analyzer, start_date, end_date, selected_assets):
    available = [a for a in selected_assets
                 if a in analyzer.returns.columns and a in analyzer.prices.columns]
    if not available:
        st.info("📊 请在侧边栏选择资产")
        return

    filtered_returns = filter_data_by_date_range(analyzer.returns[available], start_date, end_date)
    filtered_prices = filter_data_by_date_range(analyzer.prices[available], start_date, end_date)

    if filtered_returns is None or len(filtered_returns) < 20:
        st.error("⚠️ 需要至少20个交易日的数据")
        return

    risk_metrics = calculate_risk_metrics_simplified(filtered_returns, filtered_prices)
    if risk_metrics is None:
        st.error("风险指标计算失败")
        return

    st.caption(f"基于 {len(filtered_returns)} 个交易日  ·  {start_date} 至 {end_date}")

    # 风险收益散点图
    sharpe = []
    for asset in risk_metrics.index:
        ar = risk_metrics.loc[asset, 'annual_return']
        av = risk_metrics.loc[asset, 'annual_volatility']
        sharpe.append(ar / av if av != 0 else 0)

    fig_scatter = px.scatter(
        x=risk_metrics['annual_volatility'] * 100,
        y=risk_metrics['annual_return'] * 100,
        text=risk_metrics.index,
        title="风险-收益散点图（点大小=最大回撤）",
        labels={'x': '年化波动率 (%)', 'y': '年化收益率 (%)'},
        size=abs(risk_metrics['max_drawdown']) * 1000,
        color=sharpe, color_continuous_scale='Viridis',
    )
    fig_scatter.update_traces(textposition="middle center", textfont=dict(size=9), mode='markers+text')
    fig_scatter.update_layout(
        height=500, title_x=0.5,
        coloraxis_colorbar=dict(title="夏普比率", title_font=dict(size=10)),
        margin=dict(t=80, b=60, l=60, r=100),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("""
    <div style="font-size:0.85rem;color:#6b7280;">
        📊 点大小=最大回撤 · 颜色=夏普比率 · 左上角=高收益低风险
    </div>
    """, unsafe_allow_html=True)

    # 柱状图
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(
            x=risk_metrics.index, y=risk_metrics['max_drawdown'] * 100,
            title="最大回撤 (%)", labels={'x': '资产', 'y': '最大回撤 (%)'},
            color=risk_metrics['max_drawdown'] * 100, color_continuous_scale='Reds',
        )
        fig1.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        fig2 = px.bar(
            x=risk_metrics.index, y=risk_metrics['var_95_daily'] * 100,
            title="95% VaR (日收益率 %)", labels={'x': '资产', 'y': 'VaR (%)'},
            color=risk_metrics['var_95_daily'] * 100, color_continuous_scale='Oranges',
        )
        fig2.update_layout(showlegend=False, xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

    # 详细指标表
    display_risk = risk_metrics.copy()
    pct_cols = ['max_drawdown', 'var_95_daily', 'var_99_daily', 'cvar_95_daily',
                'cvar_99_daily', 'downside_risk_annual', 'annual_volatility', 'annual_return']
    for c in pct_cols:
        if c in display_risk.columns:
            display_risk[c] *= 100

    rename_map = {
        'max_drawdown': '最大回撤(%)', 'var_95_daily': '95% VaR(%)',
        'var_99_daily': '99% VaR(%)', 'cvar_95_daily': '95% CVaR(%)',
        'cvar_99_daily': '99% CVaR(%)', 'downside_risk_annual': '下行风险(%)',
        'sortino_ratio': 'Sortino比率', 'calmar_ratio': 'Calmar比率',
        'annual_volatility': '年化波动率(%)', 'annual_return': '年化收益率(%)',
    }
    present = [c for c in rename_map if c in display_risk.columns]
    display_risk = display_risk[present].rename(columns=rename_map)
    dataframe_with_download(display_risk.round(3), filename="risk_metrics.csv", title="风险指标表")
