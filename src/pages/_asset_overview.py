#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资产总览页面

4-Tab 结构：价格走势 / 收益率 / 波动率 / 债券收益率
"""

import streamlit as st
import plotly.express as px
from config import ASSET_NAMES, ALL_BOND_YIELDS, BOND_YIELD_NAMES
from ui.components import dataframe_with_download
from ui.utils import filter_data_by_date_range


def show_asset_overview(analyzer, start_date, end_date, selected_assets):
    """资产总览页面（接收全局参数）"""

    st.markdown("""
    <div class='signal-header'>
        <h1>📊 资产价格与收益分析</h1>
        <p>全面监控资产价格走势和收益表现</p>
    </div>
    """, unsafe_allow_html=True)

    if not selected_assets:
        st.warning("⚠️ 请在侧边栏选择要分析的资产")
        return

    if start_date is None or end_date is None:
        st.warning("⚠️ 无法确定日期范围")
        return

    # 过滤价格数据
    available_price_assets = [a for a in selected_assets if a in analyzer.prices.columns]
    if not available_price_assets:
        st.warning("⚠️ 所选资产在价格数据中不可用")
        return

    prices_data = filter_data_by_date_range(
        analyzer.prices[available_price_assets], start_date, end_date
    )
    if prices_data is None or len(prices_data) == 0:
        st.error("⚠️ 选定日期范围内没有数据")
        return

    actual_days = len(prices_data)
    time_label = f"{actual_days}个交易日 ({start_date} 至 {end_date})"

    # ── 4 个 Tab ──
    tab1, tab2, tab3, tab4 = st.tabs(["💹 价格走势", "📈 收益率", "📊 波动率", "📋 债券收益率"])

    # ── Tab 1: 价格走势 ──
    with tab1:
        normalized = prices_data.div(prices_data.iloc[0]) * 100
        fig = px.line(
            normalized,
            title=f"资产价格走势（标准化，基期=100）- {time_label}",
            labels={'value': '价格指数', 'index': '日期'},
            height=500,
        )
        fig.update_layout(
            xaxis_title="日期", yaxis_title="价格指数",
            legend_title="资产类别", hovermode='x unified',
        )
        st.plotly_chart(fig, use_container_width=True)

        # 区间涨跌幅排名
        if len(prices_data) >= 2:
            changes = (prices_data.iloc[-1] / prices_data.iloc[0] - 1) * 100
            rank_df = changes.to_frame("区间涨跌幅(%)").sort_values("区间涨跌幅(%)", ascending=False).round(2)
            dataframe_with_download(rank_df, filename="price_changes.csv", title="区间涨跌幅排名")

    # ── Tab 2: 收益率 ──
    with tab2:
        available_ret = [a for a in selected_assets if a in analyzer.returns.columns]
        if available_ret:
            returns_data = filter_data_by_date_range(
                analyzer.returns[available_ret], start_date, end_date
            )
            if returns_data is not None and len(returns_data) > 0:
                cum_ret = (1 + returns_data).cumprod() - 1
                fig2 = px.line(
                    cum_ret * 100,
                    title=f"累计收益率走势 - {len(returns_data)}个交易日",
                    labels={'value': '累计收益率 (%)', 'index': '日期'},
                    height=500,
                )
                fig2.update_layout(
                    xaxis_title="日期", yaxis_title="累计收益率 (%)",
                    legend_title="资产类别", hovermode='x unified',
                )
                st.plotly_chart(fig2, use_container_width=True)

                # 收益率统计表
                stats = analyzer.calculate_basic_stats()
                if stats is not None:
                    # 只显示已选资产
                    stats_filtered = stats.loc[stats.index.isin(available_ret)]
                    if not stats_filtered.empty:
                        display = stats_filtered[['annual_return', 'annual_volatility', 'sharpe_ratio', 'positive_days_pct']].copy()
                        display['annual_return'] *= 100
                        display['annual_volatility'] *= 100
                        display.columns = ['年化收益率(%)', '年化波动率(%)', '夏普比率', '正收益天数占比(%)']
                        dataframe_with_download(display.round(2), filename="return_stats.csv", title="收益率统计")
            else:
                st.warning("⚠️ 选定日期范围内没有收益率数据")
        else:
            st.warning("⚠️ 所选资产没有收益率数据")

    # ── Tab 3: 波动率 ──
    with tab3:
        # 窗口选择器放在 Tab 内部
        vol_col1, vol_col2 = st.columns([3, 1])
        with vol_col2:
            vol_window = st.selectbox(
                "滚动窗口",
                options=[22, 44, 66],
                format_func=lambda x: f"{x // 22}个月 ({x}日)",
                index=0,
                key="vol_window_tab",
            )

        available_ret = [a for a in selected_assets if a in analyzer.returns.columns]
        if available_ret:
            # 滚动波动率
            rolling_vol = analyzer.calculate_rolling_volatility(
                window_days=vol_window, selected_assets=available_ret
            )
            if rolling_vol is not None:
                fv = filter_data_by_date_range(rolling_vol, start_date, end_date)
                if fv is not None and len(fv) > 0:
                    fig3 = px.line(
                        fv * 100,
                        title=f"已实现波动率 - {vol_window}日滚动",
                        labels={'value': '年化波动率 (%)', 'index': '日期'},
                        height=450,
                    )
                    fig3.update_layout(
                        xaxis_title="日期", yaxis_title="年化波动率 (%)",
                        legend_title="资产类别", hovermode='x unified',
                    )
                    st.plotly_chart(fig3, use_container_width=True)

            # 滚动下行波动率
            rolling_dv = analyzer.calculate_rolling_downside_volatility(
                window_days=vol_window, selected_assets=available_ret
            )
            if rolling_dv is not None:
                fdv = filter_data_by_date_range(rolling_dv, start_date, end_date)
                if fdv is not None and len(fdv) > 0:
                    fig4 = px.line(
                        fdv * 100,
                        title=f"已实现下行波动率 - {vol_window}日滚动",
                        labels={'value': '年化下行波动率 (%)', 'index': '日期'},
                        height=450,
                    )
                    fig4.update_layout(
                        xaxis_title="日期", yaxis_title="年化下行波动率 (%)",
                        legend_title="资产类别", hovermode='x unified',
                    )
                    st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("⚠️ 所选资产没有收益率数据")

    # ── Tab 4: 债券收益率 ──
    with tab4:
        _show_bond_yields(analyzer)


def _show_bond_yields(analyzer):
    """显示债券收益率模块"""
    bond_data_available = []
    if hasattr(analyzer, 'prices') and analyzer.prices is not None:
        for bond_code in ALL_BOND_YIELDS:
            bond_name = BOND_YIELD_NAMES.get(bond_code, bond_code)
            if bond_code in analyzer.prices.columns:
                bond_data_available.append(bond_code)
            elif bond_name in analyzer.prices.columns:
                bond_data_available.append(bond_name)

    if not bond_data_available:
        st.warning("⚠️ 没有可用的债券收益率数据")
        return

    selected_bonds = st.multiselect(
        "选择要显示的债券收益率",
        options=bond_data_available,
        default=bond_data_available[:6] if len(bond_data_available) >= 6 else bond_data_available,
        key="bond_yields_tab",
        format_func=lambda x: BOND_YIELD_NAMES.get(x, x),
    )

    if selected_bonds:
        bond_data = analyzer.prices[selected_bonds]
        fig = px.line(
            bond_data,
            title="债券收益率走势 (%)",
            labels={'value': '收益率 (%)', 'index': '日期'},
            height=400,
        )
        for trace in fig.data:
            if trace.name in BOND_YIELD_NAMES:
                trace.name = BOND_YIELD_NAMES[trace.name]
        fig.update_layout(
            xaxis_title="日期", yaxis_title="收益率 (%)",
            legend_title="债券类型", hovermode='x unified',
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 请选择要显示的债券收益率")
