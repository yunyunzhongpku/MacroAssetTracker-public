#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据管理页面

提供数据状态查看
"""

import streamlit as st
import os
from datetime import datetime
from config import PRICES_FILE, RETURNS_FILE
from ui.utils import get_current_data_range


def get_analyzer():
    """获取分析器实例（临时导入以避免循环依赖）"""
    from analyzer import SimpleAnalyzer
    import hashlib

    # 获取数据文件哈希用于缓存
    def get_data_files_hash():
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
        try:
            analyzer = SimpleAnalyzer()
            if analyzer.prices is None or analyzer.returns is None:
                return None
            return analyzer
        except Exception as e:
            st.error(f"数据加载失败: {e}")
            return None

    files_hash = get_data_files_hash()
    return load_analyzer(files_hash)


def show_data_management():
    """数据管理页面 - 简化版本"""
    st.header("🔄 数据管理")

    # 获取当前数据范围
    current_start, current_end = get_current_data_range()

    # 数据状态显示
    st.markdown("### 📊 当前数据状态")

    col1, col2, col3 = st.columns([1, 1, 1])

    if os.path.exists(PRICES_FILE) and os.path.exists(RETURNS_FILE):
        analyzer = get_analyzer()
        if analyzer:
            summary = analyzer.get_data_summary()
            if summary:
                with col1:
                    st.metric("📅 数据状态", "✅ 完整", f"{summary['date_range']['start']}")
                with col2:
                    st.metric("📋 资产数量", f"{len(summary['assets'])}", "个")
                with col3:
                    st.metric("🗓️ 交易日数", f"{summary['date_range']['trading_days']}", "天")

                # 显示详细数据范围
                st.info(f"📅 **当前数据覆盖范围**: {summary['date_range']['start']} 至 {summary['date_range']['end']}")

                # 显示数据文件状态
                last_modified = os.path.getmtime(PRICES_FILE)
                last_update_time = datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')
                st.success(f"⏰ **最后更新**: {last_update_time}")
    else:
        st.warning("⚠️ 数据文件不存在或不完整")
