#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
侧边栏全局控件模块

提供导航、时间范围选择和资产选择器，所有页面共享状态
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from config import ASSETS, ASSET_NAMES


def _init_session_state(analyzer):
    """初始化全局 session_state"""
    if 'global_date_preset' not in st.session_state:
        st.session_state.global_date_preset = "最近6个月"

    if 'global_selected_assets' not in st.session_state:
        # 默认选择 A股 + 商品
        default_codes = ASSETS.get("A股指数", []) + ASSETS.get("商品", [])
        # 转换为中文名
        default_names = [ASSET_NAMES.get(c, c) for c in default_codes]
        # 过滤出实际存在于数据中的资产
        if analyzer and analyzer.prices is not None:
            available = set(analyzer.prices.columns)
            default_names = [n for n in default_names if n in available]
        st.session_state.global_selected_assets = default_names

    if 'global_category_toggles' not in st.session_state:
        st.session_state.global_category_toggles = {"A股指数": True, "商品": True}


def _get_available_assets(analyzer):
    """获取数据中实际可用的资产列表（中文名），排除债券收益率"""
    if analyzer is None or analyzer.prices is None:
        return []
    from config import ALL_BOND_YIELDS, BOND_YIELD_NAMES
    bond_names = set(ALL_BOND_YIELDS) | set(BOND_YIELD_NAMES.values())
    available = []
    for col in analyzer.prices.columns:
        if col in bond_names:
            continue
        # 只保留在 ASSET_NAMES 中有映射的资产
        is_known = False
        for code, name in ASSET_NAMES.items():
            if name == col or code == col:
                is_known = True
                break
        if is_known:
            available.append(col)
    return available


def _get_category_assets(category, available_assets):
    """获取某个类别下在数据中可用的资产名列表"""
    codes = ASSETS.get(category, [])
    names = [ASSET_NAMES.get(c, c) for c in codes]
    return [n for n in names if n in available_assets]


def _compute_date_range(preset, data_start, data_end):
    """根据预设计算日期范围，以数据末尾为基准（而非今天）"""
    ref = data_end  # 用数据实际末尾，避免数据滞后时短周期无数据
    if preset == "最近1个月":
        start = max(data_start, ref - timedelta(days=30))
    elif preset == "最近3个月":
        start = max(data_start, ref - timedelta(days=90))
    elif preset == "最近6个月":
        start = max(data_start, ref - timedelta(days=180))
    elif preset == "最近1年":
        start = max(data_start, ref - timedelta(days=365))
    elif preset == "YTD":
        start = max(data_start, datetime(ref.year, 1, 1).date())
    else:  # 全部数据
        start = data_start
    return start, data_end


def render_sidebar(analyzer):
    """
    渲染侧边栏全局控件

    返回:
        tuple: (page, start_date, end_date, selected_assets)
    """
    _init_session_state(analyzer)

    # ── 导航 ──
    st.sidebar.title("🧭 功能导航")
    page = st.sidebar.radio(
        "选择功能页面",
        [
            "📊 行情总览",
            "🔗 相关性与风险",
            "⚙️ 系统管理",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")

    # ── 时间范围 ──
    st.sidebar.markdown("##### 📅 时间范围")

    presets = ["最近1个月", "最近3个月", "最近6个月", "最近1年", "YTD", "全部数据"]
    preset = st.sidebar.radio(
        "时间范围",
        presets,
        index=presets.index(st.session_state.global_date_preset),
        key="sidebar_date_preset",
        label_visibility="collapsed",
        horizontal=True,
    )
    st.session_state.global_date_preset = preset

    # 计算日期
    if analyzer and analyzer.prices is not None:
        data_start = analyzer.prices.index.min().date()
        data_end = analyzer.prices.index.max().date()
        start_date, end_date = _compute_date_range(preset, data_start, data_end)
        filtered = analyzer.prices.loc[start_date:end_date]
        st.sidebar.caption(f"{start_date} 至 {end_date}  ·  {len(filtered)} 个交易日")
    else:
        start_date, end_date = None, None

    st.sidebar.markdown("---")

    # ── 资产选择器 ──
    st.sidebar.markdown("##### 🏷️ 资产选择")

    available_assets = _get_available_assets(analyzer)

    # 分组按钮
    categories = ["A股指数", "债券指数", "商品", "海外", "REITs"]
    # 用两行排列按钮
    row1 = st.sidebar.columns(3)
    row2 = st.sidebar.columns(3)
    btn_cols = row1 + row2  # 6个位置，5个类别

    for i, cat in enumerate(categories):
        cat_assets = _get_category_assets(cat, available_assets)
        is_on = st.session_state.global_category_toggles.get(cat, False)
        label = f"{'✓ ' if is_on else ''}{cat}"
        with btn_cols[i]:
            if st.button(label, key=f"cat_btn_{cat}", use_container_width=True):
                # 切换状态
                new_state = not is_on
                st.session_state.global_category_toggles[cat] = new_state
                current = set(st.session_state.global_selected_assets)
                if new_state:
                    current.update(cat_assets)
                else:
                    current -= set(cat_assets)
                st.session_state.global_selected_assets = [
                    a for a in available_assets if a in current
                ]
                st.rerun()

    # multiselect
    selected_assets = st.sidebar.multiselect(
        "已选资产",
        options=available_assets,
        default=st.session_state.global_selected_assets,
        key="sidebar_asset_multiselect",
        label_visibility="collapsed",
    )
    st.session_state.global_selected_assets = selected_assets

    # 同步分组按钮状态
    for cat in categories:
        cat_assets = _get_category_assets(cat, available_assets)
        if cat_assets:
            all_selected = all(a in selected_assets for a in cat_assets)
            st.session_state.global_category_toggles[cat] = all_selected

    # 全选/清空 + 计数
    col_l, col_r = st.sidebar.columns(2)
    with col_l:
        if st.button("全选", key="select_all", use_container_width=True):
            st.session_state.global_selected_assets = available_assets[:]
            st.rerun()
    with col_r:
        if st.button("清空", key="clear_all", use_container_width=True):
            st.session_state.global_selected_assets = []
            st.rerun()

    st.sidebar.caption(f"已选 {len(selected_assets)} / {len(available_assets)} 个资产")

    return page, start_date, end_date, selected_assets
