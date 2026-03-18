"""
聚宽策略适配器
将聚宽策略代码转换为可在本平台运行的独立函数
"""

import numpy as np
import math
import pandas as pd
from collections import defaultdict


class JoinQuantStrategy:
    """聚宽策略适配器"""
    
    def __init__(self, config):
        """
        初始化策略参数
        
        Args:
            config: 策略配置字典，包含以下参数:
                - lookback_days: 动量计算周期
                - holdings_num: 持仓ETF数量
                - defensive_etf: 防御性ETF代码
                - stop_loss: 固定百分比止损线
                - loss: 近3日跌幅止损线
                - use_rsi_filter: 是否启用RSI过滤
                - rsi_period: RSI计算周期
                - rsi_lookback_days: 检查RSI的历史天数
                - rsi_threshold: RSI阈值
                - use_short_momentum_filter: 是否启用短期动量过滤
                - short_lookback_days: 短期动量计算周期
                - short_momentum_threshold: 短期动量阈值
                - use_atr_stop_loss: 是否启用ATR动态止损
                - atr_period: ATR计算周期
                - atr_multiplier: ATR倍数
        """
        self.g = config
        self.positions = {}
        self.position_highs = {}
        self.position_stop_prices = {}
    
    def initialize(self, etf_pool):
        """
        初始化函数
        
        Args:
            etf_pool: ETF代码列表
        """
        self.g['etf_pool'] = etf_pool
        print(f"""
策略初始化完成:
- ETF池大小: {len(etf_pool)} 只ETF
- 动量周期: {self.g['lookback_days']} 天
- 持仓数量: {self.g['holdings_num']} 只
- RSI过滤: {'启用' if self.g['use_rsi_filter'] else '禁用'}
- ATR止损: {'启用' if self.g['use_atr_stop_loss'] else '禁用'}
- 防御ETF: {self.g['defensive_etf']}
""")
    
    def calculate_rsi(self, prices, period=6):
        """
        计算RSI指标
        
        Args:
            prices: 价格序列
            period: RSI周期
        
        Returns:
            RSI值数组
        """
        if len(prices) < period + 1:
            return []
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.zeros_like(prices)
        avg_losses = np.zeros_like(prices)
        avg_gains[period] = np.mean(gains[:period])
        avg_losses[period] = np.mean(losses[:period])
        
        rsi_values = np.zeros(len(prices))
        rsi_values[:period] = 50
        
        for i in range(period + 1, len(prices)):
            avg_gains[i] = (avg_gains[i-1] * (period - 1) + gains[i-1]) / period
            avg_losses[i] = (avg_losses[i-1] * (period - 1) + losses[i-1]) / period
            
            if avg_losses[i] == 0:
                rsi_values[i] = 100
            else:
                rs = avg_gains[i] / avg_losses[i]
                rsi_values[i] = 100 - (100 / (1 + rs))
        
        return rsi_values[period:]
    
    def calculate_momentum_metrics(self, etf, price_data, current_data):
        """
        计算ETF的动量指标
        
        Args:
            etf: ETF代码
            price_data: 历史价格数据 (DataFrame, 包含close, high)
            current_data: 当前数据字典 (包含price, paused等)
        
        Returns:
            指标字典，包含各项指标和过滤结果
        """
        try:
            # 检查停牌
            if current_data.get('paused', False):
                return None
            
            if len(price_data) < self.g['lookback_days']:
                return None
            
            # 获取价格序列
            current_price = current_data.get('price', 0)
            price_series = np.append(price_data["close"].values, current_price)
            
            # ========== RSI过滤检查 ==========
            rsi_filter_pass = True
            current_rsi = 0
            max_rsi = 0
            
            if self.g['use_rsi_filter'] and len(price_series) >= self.g['rsi_period'] + self.g['rsi_lookback_days']:
                rsi_values = self.calculate_rsi(price_series, self.g['rsi_period'])
                
                if len(rsi_values) >= self.g['rsi_lookback_days']:
                    recent_rsi = rsi_values[-self.g['rsi_lookback_days']:]
                    rsi_ever_above_threshold = np.any(recent_rsi > self.g['rsi_threshold'])
                    
                    # 检查当前价格是否在MA5之下
                    if len(price_series) >= 5:
                        ma5 = np.mean(price_series[-5:])
                        current_below_ma5 = current_price < ma5
                    else:
                        current_below_ma5 = True
                    
                    if rsi_ever_above_threshold and current_below_ma5:
                        rsi_filter_pass = False
                        max_rsi = np.max(recent_rsi)
                        current_rsi = recent_rsi[-1] if len(recent_rsi) > 0 else 0
            
            if not rsi_filter_pass:
                return None
            
            # ========== 短期动量计算 ==========
            if len(price_series) >= self.g['short_lookback_days'] + 1:
                short_return = price_series[-1] / price_series[-(self.g['short_lookback_days'] + 1)] - 1
                short_annualized = (1 + short_return) ** (250 / self.g['short_lookback_days']) - 1
            else:
                short_return = 0
                short_annualized = 0
            
            # ========== 短期动量过滤 ==========
            if self.g['use_short_momentum_filter'] and short_annualized < self.g['short_momentum_threshold']:
                return None
            
            # ========== 长期动量计算（加权回归） ==========
            recent_price_series = price_series[-(self.g['lookback_days'] + 1):]
            y = np.log(recent_price_series)
            x = np.arange(len(y))
            weights = np.linspace(1, 2, len(y))  # 加权回归，近期权重更高
            
            # 计算年化收益率
            slope, intercept = np.polyfit(x, y, 1, w=weights)
            annualized_returns = math.exp(slope * 250) - 1
            
            # 计算R²（拟合优度）
            ss_res = np.sum(weights * (y - (slope * x + intercept)) ** 2)
            ss_tot = np.sum(weights * (y - np.mean(y)) ** 2)
            r_squared = 1 - ss_res / ss_tot if ss_tot else 0
            
            # 综合得分 = 年化收益率 * 趋势稳定性
            score = annualized_returns * r_squared
            
            # ========== 短期风控过滤 ==========
            if len(price_series) >= 4:
                day1_ratio = price_series[-1] / price_series[-2]
                day2_ratio = price_series[-2] / price_series[-3]
                day3_ratio = price_series[-3] / price_series[-4]
                
                if min(day1_ratio, day2_ratio, day3_ratio) < self.g['loss']:
                    score = 0
            
            return {
                'etf': etf,
                'annualized_returns': annualized_returns,
                'r_squared': r_squared,
                'score': score,
                'slope': slope,
                'current_price': current_price,
                'short_return': short_return,
                'short_annualized': short_annualized,
                'short_momentum_pass': short_return >= self.g['short_momentum_threshold'],
                'rsi_filter_pass': rsi_filter_pass,
                'current_rsi': current_rsi,
                'max_recent_rsi': max_rsi,
            }
            
        except Exception as e:
            print(f"计算{etf}动量指标出错: {e}")
            return None
    
    def get_ranked_etfs(self, etf_pool, price_data_dict, current_data_dict):
        """
        获取符合条件的ETF排名
        
        Args:
            etf_pool: ETF代码列表
            price_data_dict: ETF历史价格数据字典 {etf_code: price_df}
            current_data_dict: ETF当前数据字典 {etf_code: current_data}
        
        Returns:
            排序后的ETF指标列表
        """
        etf_metrics = []
        
        for etf in etf_pool:
            if etf not in price_data_dict or etf not in current_data_dict:
                continue
            
            current_data = current_data_dict[etf]
            if current_data.get('paused', False):
                continue
            
            metrics = self.calculate_momentum_metrics(
                etf, 
                price_data_dict[etf], 
                current_data
            )
            
            if metrics is not None:
                if 0 < metrics['score'] < self.g.get('max_score_threshold', 500.0):
                    etf_metrics.append(metrics)
        
        # 按得分降序排序
        etf_metrics.sort(key=lambda x: x['score'], reverse=True)
        return etf_metrics
    
    def generate_trading_signals(self, ranked_etfs):
        """
        生成交易信号
        
        Args:
            ranked_etfs: 排序后的ETF指标列表
        
        Returns:
            交易信号列表: [(action, etf, amount), ...]
        """
        signals = []
        holdings_num = self.g['holdings_num']
        min_score_threshold = self.g.get('min_score_threshold', 0)
        
        # 确定目标ETF列表
        target_etfs = []
        if ranked_etfs:
            for metrics in ranked_etfs[:holdings_num]:
                if metrics['score'] >= min_score_threshold:
                    target_etfs.append(metrics['etf'])
        
        # 如果没有符合条件的ETF，进入防御模式
        if not target_etfs:
            target_etfs = [self.g['defensive_etf']]
        
        # 生成交易信号（简化版）
        for etf in target_etfs:
            signals.append(('buy', etf, 100000))  # 目标金额10万
        
        return signals
    
    def check_stop_loss(self, positions, current_prices):
        """
        检查止损
        
        Args:
            positions: 持仓列表
            current_prices: 当前价格字典
        
        Returns:
            触发止损的ETF列表
        """
        stop_loss_list = []
        stop_loss = self.g['stop_loss']
        
        for position in positions:
            etf = position['etf']
            if etf not in current_prices:
                continue
            
            current_price = current_prices[etf]
            cost_price = position['cost']
            
            if current_price <= cost_price * stop_loss:
                stop_loss_list.append(etf)
        
        return stop_loss_list


def create_default_config():
    """
    创建默认策略配置
    
    Returns:
        默认配置字典
    """
    return {
        # 动量计算参数
        'lookback_days': 25,
        'holdings_num': 1,
        'defensive_etf': '511880.XSHG',
        'min_money': 5000,
        
        # 风险控制参数
        'stop_loss': 0.95,
        'loss': 0.97,
        
        # 得分阈值
        'min_score_threshold': 0,
        'max_score_threshold': 500.0,
        
        # 短期动量过滤参数
        'use_short_momentum_filter': True,
        'short_lookback_days': 10,
        'short_momentum_threshold': 0.0,
        
        # RSI过滤参数
        'use_rsi_filter': True,
        'rsi_period': 6,
        'rsi_lookback_days': 1,
        'rsi_threshold': 98,
        
        # ATR动态止损参数
        'use_atr_stop_loss': False,
        'atr_period': 14,
        'atr_multiplier': 2,
        'atr_trailing_stop': False,
        'atr_exclude_defensive': True,
    }
