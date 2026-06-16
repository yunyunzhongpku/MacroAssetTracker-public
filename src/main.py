#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MacroAssetTracker - Streamlit主程序

提供Web界面展示资产价格、相关性分析和风险指标
"""

import streamlit as st
import os
import hashlib
from analyzer import SimpleAnalyzer
from config import PAGE_TITLE, PRICES_FILE, RETURNS_FILE

# 导入UI模块
from ui.styles import get_custom_styles
from ui.utils import check_data_exists
from ui.sidebar import render_sidebar

# 导入页面模块
from pages import (
    show_asset_overview,
    show_correlation_risk,
    show_data_management,
)


# 页面配置
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用自定义CSS样式
st.markdown(get_custom_styles(), unsafe_allow_html=True)

# 主标题
st.markdown('<h1 class="main-header">📈 Macro Assets Tracker</h1>', unsafe_allow_html=True)


# 获取数据文件的修改时间哈希（用于缓存控制）
def get_data_files_hash():
    """获取数据文件的修改时间哈希，用于缓存失效检查"""
    try:
        files_info = []
        for file_path in [PRICES_FILE, RETURNS_FILE]:
            if os.path.exists(file_path):
                mtime = str(os.path.getmtime(file_path))
                files_info.append(f"{file_path}:{mtime}")
        content = "|".join(files_info)
        return hashlib.md5(content.encode()).hexdigest()
    except Exception:
        return "default_hash"


@st.cache_data(ttl=300)
def load_analyzer(_files_hash):
    """加载分析器和数据"""
    try:
        analyzer = SimpleAnalyzer()
        if analyzer.prices is None or analyzer.returns is None:
            return None
        return analyzer
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None


def get_analyzer():
    """获取分析器实例，支持缓存控制"""
    files_hash = get_data_files_hash()
    return load_analyzer(files_hash)


def main():
    """主程序入口"""
    # 检查数据是否存在
    if not check_data_exists():
        st.error("⚠️ 数据文件不存在，请先更新数据！")
        st.info("请点击侧边栏的 '⚙️ 系统管理' 页面查看详情。")
        return

    # 加载数据
    analyzer = get_analyzer()
    if analyzer is None:
        st.error("⚠️ 数据加载失败，请检查数据文件完整性！")
        return

    # 渲染侧边栏全局控件
    page, start_date, end_date, selected_assets = render_sidebar(analyzer)

    # 页面路由
    if page == "📊 行情总览":
        show_asset_overview(analyzer, start_date, end_date, selected_assets)
    elif page == "🔗 相关性与风险":
        show_correlation_risk(analyzer, start_date, end_date, selected_assets)
    elif page == "⚙️ 系统管理":
        show_data_management()


if __name__ == "__main__":
    main()
