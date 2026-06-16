#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MacroAssetTracker - 数据分析模块

提供相关性分析、风险指标计算等功能
"""

import pandas as pd
import numpy as np
import os
from config import PRICES_FILE, RETURNS_FILE, ASSET_NAMES, BOND_YIELD_NAMES

class SimpleAnalyzer:
    def __init__(self):
        """初始化分析器，加载数据"""
        self.prices = None
        self.returns = None
        self._load_data()
    
    def _load_data(self):
        """加载价格和收益率数据"""
        try:
            if os.path.exists(PRICES_FILE):
                self.prices = pd.read_csv(PRICES_FILE, index_col=0, parse_dates=True, encoding='utf-8')
                print(f"价格数据加载成功: {self.prices.shape}")
            else:
                print(f"价格数据文件不存在: {PRICES_FILE}")
                
            if os.path.exists(RETURNS_FILE):
                self.returns = pd.read_csv(RETURNS_FILE, index_col=0, parse_dates=True, encoding='utf-8')
                print(f"收益率数据加载成功: {self.returns.shape}")
            else:
                print(f"收益率数据文件不存在: {RETURNS_FILE}")
                
        except Exception as e:
            print(f"数据加载异常: {e}")
    
    def get_data_summary(self):
        """获取数据概要信息"""
        if self.prices is None or self.returns is None:
            return None
        
        summary = {
            'price_data_shape': self.prices.shape,
            'returns_data_shape': self.returns.shape,
            'date_range': {
                'start': self.prices.index.min().strftime('%Y-%m-%d'),
                'end': self.prices.index.max().strftime('%Y-%m-%d'),
                'trading_days': len(self.prices)
            },
            'assets': list(self.prices.columns),
            'missing_data': {
                'prices': self.prices.isnull().sum().to_dict(),
                'returns': self.returns.isnull().sum().to_dict()
            }
        }
        
        return summary
    
    def calculate_correlation(self, method='pearson', window=None, selected_assets=None):
        """
        计算相关性矩阵
        
        参数:
            method: 相关性计算方法 ('pearson', 'spearman', 'kendall')
            window: 滚动窗口期数，None为全样本
            selected_assets: 选定的资产列表，None为所有资产
            
        返回:
            pandas.DataFrame: 相关性矩阵
        """
        if self.returns is None:
            print("收益率数据未加载")
            return None
        
        try:
            # 选择要分析的资产
            if selected_assets is not None:
                # 过滤可用的资产
                available_assets = [asset for asset in selected_assets if asset in self.returns.columns]
                if not available_assets:
                    print("选定的资产中没有可用数据")
                    return None
                returns_data = self.returns[available_assets]
            else:
                returns_data = self.returns
            
            if window is None:
                # 全样本相关性
                corr_matrix = returns_data.corr(method=method)
            else:
                # 滚动相关性（返回最后一期的相关性矩阵）
                corr_matrix = returns_data.rolling(window=window).corr(method=method).iloc[-len(returns_data.columns):]
            
            print(f"相关性矩阵计算成功 (方法: {method})")
            return corr_matrix
            
        except Exception as e:
            print(f"相关性计算异常: {e}")
            return None
    
    def calculate_basic_stats(self):
        """计算基础统计指标"""
        if self.returns is None:
            return None
        
        try:
            stats = pd.DataFrame()
            
            # 过滤掉债券收益率数据（因为对收益率计算收益率没有意义）
            # 债券收益率本身不是资产价格，其百分比变化不能作为投资收益率
            target_assets = [col for col in self.returns.columns if col not in BOND_YIELD_NAMES.values()]
            
            for asset in target_assets:
                returns = self.returns[asset].dropna()
                
                stats[asset] = {
                    # 收益率统计
                    'mean_daily_return': returns.mean(),
                    'annual_return': returns.mean() * 252,  # 年化收益率
                    'std_daily_return': returns.std(),
                    'annual_volatility': returns.std() * np.sqrt(252),  # 年化波动率
                    
                    # 风险收益指标
                    'sharpe_ratio': (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0,
                    'skewness': returns.skew(),  # 偏度
                    'kurtosis': returns.kurtosis(),  # 峰度
                    
                    # 其他统计指标
                    'min_return': returns.min(),
                    'max_return': returns.max(),
                    'positive_days_pct': (returns > 0).sum() / len(returns) * 100,
                }
            
            stats_df = pd.DataFrame(stats).T
            print("基础统计指标计算成功")
            return stats_df
        except Exception as e:
            print(f"基础统计计算异常: {e}")
            return None
    
    def calculate_risk_metrics(self, selected_assets=None):
        """
        计算风险指标
        
        参数:
            selected_assets: 选定的资产列表，None为所有资产
        """
        if self.prices is None or self.returns is None:
            return None
        
        try:
            risk_metrics = pd.DataFrame()
            
            # 选择要分析的资产
            if selected_assets is not None:
                # 过滤可用的资产
                available_assets = [asset for asset in selected_assets 
                                  if asset in self.returns.columns and asset in self.prices.columns]
                if not available_assets:
                    print("选定的资产中没有可用数据")
                    return None
            else:
                available_assets = self.returns.columns
            
            for asset in available_assets:
                returns = self.returns[asset].dropna()
                prices = self.prices[asset].dropna()
                
                # 最大回撤
                max_drawdown = self._calculate_max_drawdown(prices)
                
                # VaR计算（历史模拟法）
                var_95 = np.percentile(returns, 5)  # 95% VaR
                var_99 = np.percentile(returns, 1)  # 99% VaR
                
                # 条件VaR (CVaR/Expected Shortfall)
                cvar_95 = returns[returns <= var_95].mean()
                cvar_99 = returns[returns <= var_99].mean()
                
                # 下行风险
                downside_returns = np.minimum(returns, 0)
                downside_risk = downside_returns.std() * np.sqrt(252)
                
                # Sortino比率
                sortino_ratio = (returns.mean() * 252) / downside_risk if downside_risk != 0 else 0
                
                # Calmar比率
                annual_return = returns.mean() * 252
                calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
                
                # 年化波动率
                annual_volatility = returns.std() * np.sqrt(252)
                
                risk_metrics[asset] = {
                    'max_drawdown': max_drawdown,
                    'var_95_daily': var_95,
                    'var_99_daily': var_99,
                    'cvar_95_daily': cvar_95,
                    'cvar_99_daily': cvar_99,
                    'downside_risk_annual': downside_risk,
                    'sortino_ratio': sortino_ratio,
                    'calmar_ratio': calmar_ratio,
                    'annual_volatility': annual_volatility,
                    'annual_return': annual_return,
                }
            
            risk_df = pd.DataFrame(risk_metrics).T
            print("风险指标计算成功")
            return risk_df
            
        except Exception as e:
            print(f"风险指标计算异常: {e}")
            return None
    
    def _calculate_max_drawdown(self, prices):
        """计算最大回撤"""
        if len(prices) == 0:
            return 0
            
        running_max = prices.expanding().max()
        drawdown = (prices - running_max) / running_max
        return drawdown.min()
    
    def calculate_rolling_correlation(self, asset1, asset2, window=30):
        """
        计算两个资产的滚动相关性
        
        参数:
            asset1, asset2: 资产名称
            window: 滚动窗口期数
            
        返回:
            pandas.Series: 滚动相关性序列
        """
        if self.returns is None:
            return None
        
        if asset1 not in self.returns.columns or asset2 not in self.returns.columns:
            print(f"资产 {asset1} 或 {asset2} 不存在于数据中")
            return None
        
        try:
            rolling_corr = self.returns[asset1].rolling(window=window).corr(self.returns[asset2])
            print(f"{asset1} 与 {asset2} 滚动相关性计算成功")
            return rolling_corr
            
        except Exception as e:
            print(f"滚动相关性计算异常: {e}")
            return None
    
    def get_correlation_analysis(self, threshold=0.7, selected_assets=None):
        """
        相关性分析报告
        
        参数:
            threshold: 高相关性阈值
            selected_assets: 选定的资产列表，None为所有资产
            
        返回:
            dict: 相关性分析结果
        """
        corr_matrix = self.calculate_correlation(selected_assets=selected_assets)
        if corr_matrix is None:
            return None
        
        try:
            # 提取上三角矩阵（避免重复）
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
            correlations = corr_matrix.where(mask)
            
            # 找出高相关性资产对
            high_corr_pairs = []
            low_corr_pairs = []
            
            for i in range(len(correlations.index)):
                for j in range(len(correlations.columns)):
                    if pd.notna(correlations.iloc[i, j]):
                        corr_value = correlations.iloc[i, j]
                        asset1 = correlations.index[i]
                        asset2 = correlations.columns[j]
                        
                        if abs(corr_value) >= threshold:
                            high_corr_pairs.append({
                                'asset1': asset1,
                                'asset2': asset2,
                                'correlation': corr_value
                            })
                        elif abs(corr_value) <= (1 - threshold):  # 低相关性
                            low_corr_pairs.append({
                                'asset1': asset1,
                                'asset2': asset2,
                                'correlation': corr_value
                            })
            
            # 按相关性绝对值排序
            high_corr_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)
            low_corr_pairs.sort(key=lambda x: abs(x['correlation']))
            
            analysis = {
                'correlation_matrix': corr_matrix,
                'high_correlation_pairs': high_corr_pairs,
                'low_correlation_pairs': low_corr_pairs,
                'average_correlation': correlations.values[~np.isnan(correlations.values)].mean(),
                'max_correlation': correlations.max().max(),
                'min_correlation': correlations.min().min()
            }
            
            print("相关性分析报告生成成功")
            return analysis
            
        except Exception as e:
            print(f"相关性分析异常: {e}")
            return None
    
    def generate_summary_report(self):
        """生成综合分析报告"""
        if self.prices is None or self.returns is None:
            print("数据未加载，无法生成报告")
            return None
        
        print("=== 生成综合分析报告 ===")
        
        try:
            # 获取各项分析结果
            data_summary = self.get_data_summary()
            basic_stats = self.calculate_basic_stats()
            risk_metrics = self.calculate_risk_metrics()
            correlation_analysis = self.get_correlation_analysis()
            
            report = {
                'data_summary': data_summary,
                'basic_statistics': basic_stats,
                'risk_metrics': risk_metrics,
                'correlation_analysis': correlation_analysis,
                'generation_time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print("综合分析报告生成成功")
            return report
            
        except Exception as e:
            print(f"综合报告生成异常: {e}")
            return None
        
    def calculate_rolling_volatility(self, window_days=21, selected_assets=None):
        """
        计算滚动波动率
        
        参数:
            window_days: 滚动窗口天数 (21=1M, 42=2M, 63=3M)
            selected_assets: 选定的资产列表，None为所有资产
            
        返回:
            pandas.DataFrame: 滚动波动率序列（年化）
        """
        if self.returns is None:
            print("收益率数据未加载")
            return None
        
        try:
            # 选择要分析的资产
            if selected_assets is not None:
                # 过滤可用的资产
                available_assets = [asset for asset in selected_assets if asset in self.returns.columns]
                if not available_assets:
                    print("选定的资产中没有可用数据")
                    return None
                returns_data = self.returns[available_assets]
            else:
                returns_data = self.returns
            
            # 计算滚动波动率（年化）
            rolling_vol = returns_data.rolling(window=window_days).std() * np.sqrt(252)
            
            print(f"滚动波动率计算成功 (窗口: {window_days}天)")
            return rolling_vol
            
        except Exception as e:
            print(f"滚动波动率计算异常: {e}")
            return None
    
    def calculate_rolling_downside_volatility(self, window_days=21, selected_assets=None):
        """
        计算滚动下行波动率（只考虑负收益的波动性）
        
        参数:
            window_days: 滚动窗口天数 (22=1M, 44=2M, 66=3M)
            selected_assets: 选定的资产列表，None为所有资产
            
        返回:
            pandas.DataFrame: 滚动下行波动率序列（年化）
        """
        if self.returns is None:
            print("收益率数据未加载")
            return None
        
        try:
            # 选择要分析的资产
            if selected_assets is not None:
                # 过滤可用的资产
                available_assets = [asset for asset in selected_assets if asset in self.returns.columns]
                if not available_assets:
                    print("选定的资产中没有可用数据")
                    return None
                returns_data = self.returns[available_assets]
            else:
                returns_data = self.returns
            
            # 计算滚动下行波动率
            def downside_vol(x):
                # 正收益改为0，负收益保留，计算混合样本的标准差
                downside_returns = np.minimum(x, 0)
                return downside_returns.std() * np.sqrt(252)  # 年化
            
            rolling_downside_vol = returns_data.rolling(window=window_days).apply(downside_vol, raw=False)
            
            print(f"滚动下行波动率计算成功 (窗口: {window_days}天)")
            return rolling_downside_vol
            
        except Exception as e:
            print(f"滚动下行波动率计算异常: {e}")
            return None

def calculate_risk_metrics_simplified(returns_data, prices_data):
    """
    基于已过滤的数据计算风险指标
    
    参数:
        returns_data: 已过滤的收益率DataFrame
        prices_data: 已过滤的价格DataFrame
        
    返回:
        pandas.DataFrame: 风险指标矩阵
    """
    try:
        risk_metrics = pd.DataFrame()
        
        for asset in returns_data.columns:
            if asset in prices_data.columns:
                returns = returns_data[asset].dropna()
                prices = prices_data[asset].dropna()
                
                if len(returns) < 10 or len(prices) < 10:
                    continue
                
                # 最大回撤
                max_drawdown = _calculate_max_drawdown_simple(prices)
                
                # VaR计算（历史模拟法）
                var_95 = np.percentile(returns, 5)  # 95% VaR
                var_99 = np.percentile(returns, 1)  # 99% VaR
                
                # 条件VaR (CVaR/Expected Shortfall)
                cvar_95 = returns[returns <= var_95].mean() if len(returns[returns <= var_95]) > 0 else var_95
                cvar_99 = returns[returns <= var_99].mean() if len(returns[returns <= var_99]) > 0 else var_99
                
                # 下行风险
                downside_returns = np.minimum(returns, 0)
                downside_risk = downside_returns.std() * np.sqrt(252)
                
                # Sortino比率
                annual_return = returns.mean() * 252
                sortino_ratio = annual_return / downside_risk if downside_risk != 0 else 0
                
                # Calmar比率
                calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
                
                # 年化波动率
                annual_volatility = returns.std() * np.sqrt(252)
                
                risk_metrics[asset] = {
                    'max_drawdown': max_drawdown,
                    'var_95_daily': var_95,
                    'var_99_daily': var_99,
                    'cvar_95_daily': cvar_95,
                    'cvar_99_daily': cvar_99,
                    'downside_risk_annual': downside_risk,
                    'sortino_ratio': sortino_ratio,
                    'calmar_ratio': calmar_ratio,
                    'annual_volatility': annual_volatility,
                    'annual_return': annual_return,
                }
        
        risk_df = pd.DataFrame(risk_metrics).T
        print(f"简化风险指标计算成功，覆盖 {len(risk_df)} 个资产")
        return risk_df
        
    except Exception as e:
        print(f"简化风险指标计算异常: {e}")
        return None

def _calculate_max_drawdown_simple(prices):
    """计算最大回撤的辅助函数"""
    if len(prices) == 0:
        return 0
        
    running_max = prices.expanding().max()
    drawdown = (prices - running_max) / running_max
    return drawdown.min()

def main():
    """测试函数"""
    print("MacroAssetTracker - 数据分析模块测试")
    print("=" * 50)
    
    try:
        # 创建分析器
        analyzer = SimpleAnalyzer()
        
        if analyzer.prices is None or analyzer.returns is None:
            print("数据未加载：请确认 data/prices.csv 与 data/returns.csv 是否存在")
            return
        
        # 测试各种分析功能
        print("\n1. 数据概要:")
        summary = analyzer.get_data_summary()
        if summary:
            print(f"  价格数据: {summary['price_data_shape']}")
            print(f"  收益率数据: {summary['returns_data_shape']}")
            print(f"  日期范围: {summary['date_range']['start']} 到 {summary['date_range']['end']}")
            print(f"  交易日数: {summary['date_range']['trading_days']}")
        
        print("\n2. 相关性矩阵:")
        corr_matrix = analyzer.calculate_correlation()
        if corr_matrix is not None:
            print(corr_matrix.round(3))
        
        print("\n3. 基础统计指标:")
        basic_stats = analyzer.calculate_basic_stats()
        if basic_stats is not None:
            print(basic_stats.round(4))
        
        print("\n4. 风险指标:")
        risk_metrics = analyzer.calculate_risk_metrics()
        if risk_metrics is not None:
            print(risk_metrics.round(4))
        
        print("\n5. 相关性分析报告:")
        corr_analysis = analyzer.get_correlation_analysis(threshold=0.5)
        if corr_analysis:
            print(f"  平均相关性: {corr_analysis['average_correlation']:.3f}")
            print(f"  最高相关性: {corr_analysis['max_correlation']:.3f}")
            print(f"  最低相关性: {corr_analysis['min_correlation']:.3f}")
            
            if corr_analysis['high_correlation_pairs']:
                print("  高相关性资产对:")
                for pair in corr_analysis['high_correlation_pairs'][:3]:  # 显示前3对
                    print(f"    {pair['asset1']} - {pair['asset2']}: {pair['correlation']:.3f}")
        
        print("\n🎉 分析模块测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()