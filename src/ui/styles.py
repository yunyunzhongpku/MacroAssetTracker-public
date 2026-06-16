#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UI样式模块

提供Streamlit应用的自定义CSS样式
"""


def get_custom_styles():
    """
    获取应用的自定义CSS样式

    返回:
        str: CSS样式字符串
    """
    return """
<style>
:root {--c-bg:#ffffff;--c-bg-alt:#f5f7fa;--c-text:#1f2937;--c-text-light:#6b7280;--c-primary:#2563eb;--c-primary-grad:linear-gradient(90deg,#2563eb,#0ea5e9);--c-border:#e5e7eb;--radius:12px;--shadow:0 2px 4px -2px rgba(0,0,0,.06),0 4px 12px -4px rgba(0,0,0,.06);}
html,body{background:var(--c-bg)!important;color:var(--c-text)!important;font-family:'Inter','Helvetica Neue',Arial,sans-serif;overflow-x:hidden;overflow-y:auto!important;height:auto!important;min-height:100vh;}
[data-testid="stAppViewContainer"]{background:var(--c-bg)!important;overflow-y:auto!important;height:auto!important;min-height:100vh;}
[data-testid="stMain"]{overflow-y:auto!important;height:auto!important;}
section[data-testid="stSidebar"]{overflow-y:auto!important;}
.stSidebar [data-testid="stSidebarNav"],
[data-testid="stSidebarNav"]{display:none!important;} /* 隐藏默认的英文多页导航 */
.main-header{font-size:clamp(2.2rem,3vw,2.6rem);font-weight:600;letter-spacing:.5px;background:var(--c-primary-grad);-webkit-background-clip:text;color:transparent;text-align:center;margin:0 0 1.2rem 0;}
.metric-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:.9rem;margin:0 0 1.1rem 0;padding:0;}
.metric-card{background:var(--c-bg-alt);border:1px solid var(--c-border);border-radius:var(--radius);padding:.85rem 1rem;box-shadow:var(--shadow);transition:.25s;border-left:4px solid var(--c-primary);position:relative;overflow:hidden;}
.metric-card:before{content:"";position:absolute;inset:0;opacity:0;background:var(--c-primary-grad);mix-blend-mode:multiply;transition:.4s;}
.metric-card:hover:before{opacity:.06;}
.metric-label{font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;color:var(--c-text-light);margin-bottom:.25rem;}
.metric-value{font-size:1.35rem;font-weight:600;}
section[data-testid="stSidebar"]{background:var(--c-bg-alt)!important;border-right:1px solid var(--c-border);overflow-y:auto!important;}
/* DataFrame 表格增强 */
div[data-testid=stDataFrame] table{font-size:0.82rem;}
div[data-testid=stDataFrame] tbody tr:nth-child(even){background:#f9fafb;}
div[data-testid=stDataFrame] tbody tr:hover{background:#eef2ff;}
div[data-testid=stDataFrame] thead tr{background:#f1f5f9;}
div[data-testid=stDataFrame] th{font-weight:600;color:#374151;}
button[title="View fullscreen"]{display:none;}
.df-download-bar{display:flex;align-items:center;gap:.75rem;margin:.2rem 0 .4rem 0;}
.df-download-bar .title{font-weight:600;font-size:1rem;color:#374151;}

/* 信号页面专用样式 */
.signal-header{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:2rem 1.5rem;border-radius:12px;margin-bottom:1.5rem;text-align:center;color:white;box-shadow:0 4px 20px rgba(102,126,234,0.3);}
.signal-header h1{margin:0;font-size:2.2rem;font-weight:700;text-shadow:0 2px 4px rgba(0,0,0,0.3);}
.signal-header p{margin:0.5rem 0 0 0;font-size:1.1rem;opacity:0.9;}
.signal-controls{background:#f8fafc;padding:1.5rem;border-radius:12px;border:1px solid #e2e8f0;margin-bottom:1.5rem;}
.signal-section{background:white;padding:1.5rem;border-radius:12px;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.08);margin-bottom:1.5rem;}
.signal-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;margin-bottom:1rem;}
.signal-stats .metric-card{border-left-width:4px;transition:all 0.3s ease;cursor:pointer;}
.signal-stats .metric-card:hover{transform:translateY(-2px);box-shadow:0 4px 16px rgba(0,0,0,0.12);}
.signal-performance{background:#f8fafc;padding:1.5rem;border-radius:12px;border:1px solid #e2e8f0;margin-top:1rem;}
.signal-alert{background:#fef2f2;border:1px solid #fecaca;color:#b91c1c;padding:1rem;border-radius:8px;margin:1rem 0;}
.signal-filter-chip{background:#e0e7ff;color:#3730a3;padding:0.25rem 0.75rem;border-radius:20px;font-size:0.85rem;font-weight:500;margin:0.25rem;display:inline-block;}

/* 彩色信号指标卡片 */
.metric-card.bullish{border-left-color:#ef4444!important;}
.metric-card.neutral{border-left-color:#3b82f6!important;}
.metric-card.bearish{border-left-color:#10b981!important;}

/* 移动端适配 */
@media (max-width: 768px) {
    .metric-grid{grid-template-columns:1fr!important;}
    .main-header{font-size:1.8rem!important;}
    html,body{font-size:14px!important;}
    .signal-header h1{font-size:1.8rem!important;}
    .signal-controls,.signal-section{padding:1rem!important;}
}

/* 策略回顾页面专用样式 */
.strategy-markdown {
    padding: 2rem;
    line-height: 1.6;
    font-size: 0.95rem;
    color: #374151;
}

.strategy-markdown h1 {
    color: #1f2937;
    font-size: 1.8rem;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1rem;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0.5rem;
}

.strategy-markdown h2 {
    color: #2563eb;
    font-size: 1.4rem;
    font-weight: 600;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
}

.strategy-markdown h3 {
    color: #374151;
    font-size: 1.2rem;
    font-weight: 600;
    margin-top: 1.2rem;
    margin-bottom: 0.6rem;
}

.strategy-markdown p {
    margin-bottom: 1rem;
    text-align: justify;
}

.strategy-markdown ul, .strategy-markdown ol {
    margin-bottom: 1rem;
    padding-left: 2rem;
}

.strategy-markdown li {
    margin-bottom: 0.5rem;
}

.strategy-markdown table {
    border-collapse: collapse;
    width: 100%;
    margin: 1.5rem 0;
    font-size: 0.9rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-radius: 8px;
    overflow: hidden;
}

.strategy-markdown th {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-weight: 600;
    padding: 0.75rem;
    text-align: left;
    border: none;
}

.strategy-markdown td {
    padding: 0.75rem;
    border-bottom: 1px solid #e5e7eb;
    background-color: #ffffff;
}

.strategy-markdown tr:nth-child(even) td {
    background-color: #f8fafc;
}

.strategy-markdown tr:hover td {
    background-color: #eef2ff;
}

.strategy-markdown code {
    background-color: #f1f5f9;
    color: #dc2626;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.85rem;
}

.strategy-markdown pre {
    background-color: #1e293b;
    color: #e2e8f0;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    margin: 1rem 0;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.85rem;
    line-height: 1.4;
}

.strategy-markdown blockquote {
    border-left: 4px solid #2563eb;
    background-color: #f0f9ff;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 0 8px 8px 0;
    color: #1e40af;
}

.strategy-markdown a {
    color: #2563eb;
    text-decoration: none;
    font-weight: 500;
}

.strategy-markdown a:hover {
    text-decoration: underline;
}

.strategy-markdown img {
    max-width: 90%;
    max-height: 500px;
    width: auto;
    height: auto;
    border-radius: 8px;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    object-fit: contain;
    display: block;
    margin-left: auto;
    margin-right: auto;
}

/* 图片容器样式 */
.strategy-markdown .image-container {
    text-align: center;
    margin: 1.5rem 0;
    padding: 0.5rem;
    background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

.strategy-markdown .strategy-image {
    max-width: 100%;
    max-height: 500px;
    width: auto;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    object-fit: contain;
    transition: transform 0.3s ease;
}

.strategy-markdown .strategy-image:hover {
    transform: scale(1.02);
}

/* 图片错误提示样式 */
.strategy-markdown .image-error {
    color: #ef4444;
    padding: 1rem;
    border: 1px solid #fecaca;
    border-radius: 8px;
    background-color: #fef2f2;
    text-align: center;
    margin: 1rem 0;
    font-weight: 500;
}

/* 移动端适配 */
@media (max-width: 768px) {
    .strategy-markdown {
        padding: 1rem;
        font-size: 0.9rem;
    }

    .strategy-markdown h1 {
        font-size: 1.5rem;
    }

    .strategy-markdown h2 {
        font-size: 1.2rem;
    }

    .strategy-markdown table {
        font-size: 0.8rem;
    }
}
</style>
"""
