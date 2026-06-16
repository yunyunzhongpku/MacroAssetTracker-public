#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UI辅助函数模块

提供UI组件使用的辅助函数
"""

import os
import base64
import pandas as pd
import numpy as np
import streamlit as st


def get_current_data_range():
    """
    获取当前数据的日期范围

    返回:
        tuple: (start_date, end_date) 数据的开始和结束日期
    """
    try:
        from analyzer import SimpleAnalyzer
        analyzer = SimpleAnalyzer()
        if analyzer and analyzer.prices is not None:
            summary = analyzer.get_data_summary()
            if summary:
                return summary['date_range']['start'], summary['date_range']['end']
    except:
        pass
    return None, None


def get_image_base64(image_path):
    """
    将图片文件转换为base64编码

    参数:
        image_path: 图片文件路径

    返回:
        str: base64编码的图片字符串
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    except Exception as e:
        print(f"图片编码失败: {e}")
        return ""


def filter_data_by_date_range(data, start_date, end_date):
    """
    根据日期范围过滤数据

    参数:
        data: pandas DataFrame 或 Series
        start_date: 开始日期
        end_date: 结束日期

    返回:
        pandas DataFrame/Series: 过滤后的数据
    """
    if data is None:
        return None
    try:
        return data.loc[start_date:end_date]
    except Exception as e:
        st.error(f"数据过滤失败: {e}")
        return data


def analyze_correlation_matrix(corr_matrix, threshold=0.5):
    """
    分析相关性矩阵，找出高相关性和低相关性资产对

    参数:
        corr_matrix: 相关性矩阵 (pandas.DataFrame)
        threshold: 相关性阈值

    返回:
        dict: 包含高相关性和低相关性资产对的字典
    """
    high_pairs = []
    low_pairs = []
    all_correlations = []

    for i in range(len(corr_matrix.index)):
        for j in range(i + 1, len(corr_matrix.columns)):
            asset1 = corr_matrix.index[i]
            asset2 = corr_matrix.columns[j]
            correlation = corr_matrix.iloc[i, j]

            if pd.notna(correlation):
                all_correlations.append(correlation)

                if abs(correlation) > threshold:
                    high_pairs.append({
                        'asset1': asset1,
                        'asset2': asset2,
                        'correlation': correlation
                    })
                elif abs(correlation) < (1 - threshold):  # 低相关性阈值 = 1 - threshold
                    low_pairs.append({
                        'asset1': asset1,
                        'asset2': asset2,
                        'correlation': correlation
                    })

    # 按相关系数绝对值排序
    high_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
    low_pairs.sort(key=lambda x: abs(x['correlation']))

    # 计算统计信息
    if all_correlations:
        avg_correlation = np.mean(all_correlations)
        max_correlation = np.max(all_correlations)
        min_correlation = np.min(all_correlations)
    else:
        avg_correlation = max_correlation = min_correlation = 0

    return {
        'high_correlation_pairs': high_pairs,
        'low_correlation_pairs': low_pairs,
        'average_correlation': avg_correlation,
        'max_correlation': max_correlation,
        'min_correlation': min_correlation
    }


def check_data_exists():
    """
    检查数据文件是否存在

    返回:
        bool: 数据文件是否存在
    """
    from config import PRICES_FILE, RETURNS_FILE
    return os.path.exists(PRICES_FILE) and os.path.exists(RETURNS_FILE)
