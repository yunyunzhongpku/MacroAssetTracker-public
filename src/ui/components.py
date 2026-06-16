#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UI组件模块

提供可复用的UI组件
"""

import streamlit as st
import pandas as pd


def dataframe_with_download(df: pd.DataFrame, filename: str, title: str | None = None):
    """
    统一展示 DataFrame + 下载按钮 (UTF-8 BOM 适配 Excel)

    参数:
        df: 要展示的DataFrame
        filename: 下载文件名
        title: 可选的标题
    """
    if title:
        st.markdown(f"<div class='df-download-bar'><span class='title'>{title}</span></div>", unsafe_allow_html=True)
    csv = df.to_csv(index=True).encode('utf-8-sig')
    dl_col, _ = st.columns([1, 5])
    with dl_col:
        st.download_button('📥 下载 CSV', data=csv, file_name=filename, mime='text/csv')
    st.dataframe(df, use_container_width=True, height=min(520, 60 + 28 * (len(df) if len(df) < 15 else 15)))
