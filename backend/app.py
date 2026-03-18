from flask import Flask, jsonify, request
from flask_cors import CORS
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import math
from collections import defaultdict
from strategy_adapter import JoinQuantStrategy, create_default_config

app = Flask(__name__)
CORS(app)

# 数据缓存
data_cache = {}

# ==================== 聚宽API模拟 ====================

def get_current_data():
    """模拟聚宽的get_current_data"""
    class CurrentData:
        def __init__(self):
            self.data = {}
        
        def __getitem__(self, security):
            if security not in self.data:
                try:
                    # 获取实时行情
                    df = ak.stock_zh_a_spot_em()
                    stock_code = security.split('.')[0]
                    row = df[df['代码'] == stock_code]
                    if not row.empty:
                        self.data[security] = {
                            'paused': False,
                            'last_price': float(row['最新价'].values[0]),
                            'name': row['名称'].values[0],
                            'high_limit': float(row['最高'].values[0]),
                            'low_limit': float(row['最低'].values[0])
                        }
                    else:
                        self.data[security] = {
                            'paused': True,
                            'last_price': 0,
                            'name': '未知',
                            'high_limit': 0,
                            'low_limit': 0
                        }
                except:
                    self.data[security] = {
                        'paused': True,
                        'last_price': 0,
                        'name': '未知',
                        'high_limit': 0,
                        'low_limit': 0
                    }
            return self.data[security]
    
    return CurrentData()


def attribute_history(security, count, unit='1d', fields=['close']):
    """模拟聚宽的attribute_history"""
    try:
        stock_code = security.split('.')[0]
        end_date = datetime.now()
        start_date = end_date - timedelta(days=count + 20)
        
        # 获取历史数据
        if 'close' in fields or 'high' in fields or 'low' in fields:
            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                  start_date=start_date.strftime('%Y%m%d'),
                                  end_date=end_date.strftime('%Y%m%d'), adjust="")
            
            if df.empty:
                return pd.DataFrame()
            
            result = {}
            if 'close' in fields:
                result['close'] = df['收盘'].values[-count:]
            if 'high' in fields:
                result['high'] = df['最高'].values[-count:]
            if 'low' in fields:
                result['low'] = df['最低'].values[-count:]
            if 'volume' in fields:
                result['volume'] = df['成交量'].values[-count:]
            
            return pd.DataFrame(result)
        return pd.DataFrame()
    except Exception as e:
        print(f"获取历史数据失败 {security}: {e}")
        return pd.DataFrame()


def get_price(security, start_date, end_date, frequency='1d', fields=['volume'], **kwargs):
    """模拟聚宽的get_price"""
    try:
        stock_code = security.split('.')[0]
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                              start_date=start_date.strftime('%Y%m%d'),
                              end_date=end_date.strftime('%Y%m%d'), adjust="")
        if not df.empty and 'volume' in fields:
            return pd.DataFrame({'volume': df['成交量'].values})
        return pd.DataFrame()
    except:
        return pd.DataFrame()


def get_security_name(security):
    """获取证券名称"""
    try:
        current_data = get_current_data()
        return current_data[security]['name']
    except:
        return "未知名称"


def order(security, amount):
    """模拟下单"""
    print(f"下单: {security} 数量:{amount}")
    return True


# ==================== 聚宽策略核心函数 ====================

def calculate_momentum_metrics(etf, g):
    """计算动量指标"""
    try:
        etf_name = get_security_name(etf)
        
        # 获取历史价格数据
        lookback = max(g['lookback_days'], g['short_lookback_days'], 
                      g['rsi_period'] + g['rsi_lookback_days']) + 20
        prices = attribute_history(etf, lookback, '1d', ['close', 'high'])
        current_data = get_current_data()
        
        if len(prices) < g['lookback_days']:
            print(f"{etf} {etf_name}: 历史数据不足")
            return None
        
        current_price = current_data[etf]['last_price']
        price_series = np.append(prices["close"].values, current_price)
        
        # RSI过滤检查
        if g['use_rsi_filter'] and len(price_series) >= g['rsi_period'] + g['rsi_lookback_days']:
            rsi_values = calculate_rsi(price_series, g['rsi_period'])
            
            if len(rsi_values) >= g['rsi_lookback_days']:
                recent_rsi = rsi_values[-g['rsi_lookback_days']:]
                rsi_ever_above_threshold = np.any(recent_rsi > g['rsi_threshold'])
                
                if len(price_series) >= 5:
                    ma5 = np.mean(price_series[-5:])
                    current_below_ma5 = current_price < ma5
                else:
                    current_below_ma5 = True
                
                if rsi_ever_above_threshold and current_below_ma5:
                    return None
        
        # 短期动量计算
        if len(price_series) >= g['short_lookback_days'] + 1:
            short_return = price_series[-1] / price_series[-(g['short_lookback_days'] + 1)] - 1
            short_annualized = (1 + short_return) ** (250 / g['short_lookback_days']) - 1
        else:
            short_return = 0
            short_annualized = 0
        
        # 短期动量过滤
        if g['use_short_momentum_filter'] and short_annualized < g['short_momentum_threshold']:
            return None
        
        # 长期动量计算
        recent_price_series = price_series[-(g['lookback_days'] + 1):]
        y = np.log(recent_price_series)
        x = np.arange(len(y))
        weights = np.linspace(1, 2, len(y))
        
        slope, intercept = np.polyfit(x, y, 1, w=weights)
        annualized_returns = math.exp(slope * 250) - 1
        
        # 计算R²
        ss_res = np.sum(weights * (y - (slope * x + intercept)) ** 2)
        ss_tot = np.sum(weights * (y - np.mean(y)) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot else 0
        
        score = annualized_returns * r_squared
        
        # 短期风控过滤
        if len(price_series) >= 4:
            day1_ratio = price_series[-1] / price_series[-2]
            day2_ratio = price_series[-2] / price_series[-3]
            day3_ratio = price_series[-3] / price_series[-4]
            
            if min(day1_ratio, day2_ratio, day3_ratio) < g['loss']:
                score = 0
        
        return {
            'etf': etf,
            'etf_name': etf_name,
            'annualized_returns': annualized_returns,
            'r_squared': r_squared,
            'score': score,
            'slope': slope,
            'current_price': current_price,
            'short_return': short_return,
            'short_annualized': short_annualized
        }
        
    except Exception as e:
        print(f"计算{etf}动量指标出错: {e}")
        return None


def calculate_rsi(prices, period=6):
    """计算RSI指标"""
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


def get_ranked_etfs(etf_pool, g):
    """获取ETF排名"""
    etf_metrics = []
    
    for etf in etf_pool:
        current_data = get_current_data()
        if current_data[etf]['paused']:
            continue
        
        metrics = calculate_momentum_metrics(etf, g)
        if metrics is not None:
            if 0 < metrics['score'] < g['max_score_threshold']:
                etf_metrics.append(metrics)
    
    etf_metrics.sort(key=lambda x: x['score'], reverse=True)
    return etf_metrics


# ==================== API接口 ====================

@app.route('/api/etf_pool', methods=['GET'])
def get_etf_pool():
    """获取ETF池"""
    return jsonify({
        'etf_pool': [
            "518880.XSHG",  # 黄金ETF
            "159985.XSHE",  # 豆粕ETF
            "501018.XSHG",  # 南方原油
            "161226.XSHE",  # 白银LOF
            "513100.XSHG",  # 纳指ETF
            "159915.XSHE",  # 创业板ETF
            "511220.XSHG",  # 城投债ETF
        ],
        'defensive_etf': "511880.XSHG"  # 货币ETF
    })


@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    """运行回测"""
    try:
        params = request.json
        etf_pool = params.get('etf_pool', [])
        start_date = params.get('start_date', '2024-01-01')
        end_date = params.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        initial_capital = params.get('initial_capital', 1000000)
        
        # 策略参数
        g = {
            'lookback_days': params.get('lookback_days', 25),
            'holdings_num': params.get('holdings_num', 1),
            'defensive_etf': params.get('defensive_etf', '511880.XSHG'),
            'min_money': 5000,
            'stop_loss': 0.95,
            'loss': 0.97,
            'min_score_threshold': 0,
            'max_score_threshold': 500.0,
            'enable_volume_check': False,
            'use_short_momentum_filter': True,
            'short_lookback_days': 10,
            'short_momentum_threshold': 0.0,
            'use_rsi_filter': True,
            'rsi_period': 6,
            'rsi_lookback_days': 1,
            'rsi_threshold': 98,
            'use_atr_stop_loss': False,
            'atr_period': 14,
            'atr_multiplier': 2
        }
        
        # 模拟回测（简化版）
        current_capital = initial_capital
        daily_returns = []
        dates = []
        
        # 获取当前ETF排名
        ranked_etfs = get_ranked_etfs(etf_pool, g)
        
        backtest_result = {
            'status': 'success',
            'initial_capital': initial_capital,
            'final_capital': current_capital,
            'total_return': 0.0,
            'annualized_return': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'win_rate': 0.0,
            'trades_count': 0,
            'daily_equity': [],
            'trades': [],
            'ranked_etfs': ranked_etfs[:10]
        }
        
        return jsonify(backtest_result)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/realtime', methods=['GET'])
def get_realtime_data():
    """获取实时行情"""
    try:
        security = request.args.get('security', '518880.XSHG')
        current_data = get_current_data()
        data = current_data[security]
        
        return jsonify({
            'security': security,
            'name': data['name'],
            'price': data['last_price'],
            'high_limit': data['high_limit'],
            'low_limit': data['low_limit'],
            'paused': data['paused']
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/strategy/metrics', methods=['POST'])
def calculate_strategy_metrics():
    """计算策略指标"""
    try:
        params = request.json
        etf_pool = params.get('etf_pool', [])
        
        g = {
            'lookback_days': params.get('lookback_days', 25),
            'short_lookback_days': 10,
            'rsi_period': 6,
            'rsi_lookback_days': 1,
            'rsi_threshold': 98,
            'short_momentum_threshold': 0.0,
            'use_rsi_filter': params.get('use_rsi_filter', True),
            'use_short_momentum_filter': params.get('use_short_momentum_filter', True),
            'max_score_threshold': 500.0,
            'loss': 0.97
        }
        
        ranked_etfs = get_ranked_etfs(etf_pool, g)
        
        return jsonify({
            'status': 'success',
            'metrics': ranked_etfs
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/stock/search', methods=['GET'])
def search_stock():
    """搜索股票/ETF"""
    try:
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify({'stocks': []})
        
        # 获取ETF列表
        etf_df = ak.fund_etf_spot_sina()
        
        # 筛选匹配的ETF
        result = etf_df[etf_df['代码'].str.contains(keyword) | 
                       etf_df['名称'].str.contains(keyword)].head(20)
        
        stocks = []
        for _, row in result.iterrows():
            stocks.append({
                'code': f"{row['代码']}.XSHG" if row['代码'].startswith('5') else f"{row['代码']}.XSHE",
                'name': row['名称'],
                'price': row['最新价']
            })
        
        return jsonify({'stocks': stocks})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """获取模拟持仓"""
    return jsonify({
        'positions': [],
        'total_value': 0,
        'cash': 0,
        'profit': 0,
        'profit_rate': 0
    })


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
