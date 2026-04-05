# -*- coding: utf-8 -*-
"""
技术指标计算模块
负责计算RSI、移动平均线等技术指标
"""

import numpy as np
import yfinance as yf
from typing import Dict, List, Any


class TechnicalAnalyzer:
    """技术指标分析器"""
    
    def __init__(self):
        """初始化技术指标分析器"""
        pass
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """
        计算RSI指标
        
        Args:
            prices: 价格列表
            period: 计算周期
        
        Returns:
            RSI值
        """
        if len(prices) < period + 1:
            return None
        
        # 计算价格变化
        deltas = np.diff(prices)
        
        # 分离涨跌
        gains = deltas[deltas > 0]
        losses = -deltas[deltas < 0]
        
        # 计算平均涨跌
        avg_gain = np.mean(gains[:period]) if len(gains) > 0 else 0
        avg_loss = np.mean(losses[:period]) if len(losses) > 0 else 0
        
        # 计算RSI
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def calculate_ma(self, prices: List[float], period: int = 20) -> float:
        """
        计算移动平均线
        
        Args:
            prices: 价格列表
            period: 计算周期
        
        Returns:
            移动平均值
        """
        if len(prices) < period:
            return None
        
        return round(np.mean(prices[-period:]), 2)
    
    def calculate_ma_deviation(self, current_price: float, ma: float) -> float:
        """
        计算价格与移动平均线的偏离度
        
        Args:
            current_price: 当前价格
            ma: 移动平均值
        
        Returns:
            偏离度百分比
        """
        if ma == 0:
            return 0
        
        return round((current_price - ma) / ma * 100, 2)
    
    def get_stock_prices(self, code: str, stock_type: str, period: str = "1mo") -> List[float]:
        """
        获取股票历史价格
        
        Args:
            code: 股票代码
            stock_type: 股票类型
            period: 时间周期
        
        Returns:
            价格列表
        """
        try:
            if stock_type == 'stock' or stock_type == 'etf':
                # A股
                ticker = yf.Ticker(f"{code}.SS")
            elif stock_type == 'hk_etf':
                # 港股
                ticker = yf.Ticker(f"{code}.HK")
            elif stock_type == 'us_etf':
                # 美股
                ticker = yf.Ticker(f"{code}.SS")
            else:
                return []
            
            hist = ticker.history(period=period)
            if hist.empty:
                return []
            
            return hist['Close'].tolist()
            
        except Exception as e:
            print(f"获取股票 {code} 历史价格失败: {e}")
            return []
    
    def analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析单个股票的技术指标
        
        Args:
            stock_data: 股票数据
        
        Returns:
            包含技术指标的股票数据
        """
        code = stock_data['code']
        stock_type = stock_data.get('type', 'stock')
        current_price = stock_data['price']
        
        # 获取历史价格
        prices = self.get_stock_prices(code, stock_type)
        
        if prices:
            # 计算RSI
            rsi = self.calculate_rsi(prices)
            stock_data['rsi'] = rsi
            
            # 计算20日均线
            ma20 = self.calculate_ma(prices, 20)
            if ma20:
                ma20_deviation = self.calculate_ma_deviation(current_price, ma20)
                stock_data['ma20'] = ma20
                stock_data['ma20_deviation'] = ma20_deviation
        
        # 计算股息率（简化计算）
        dividend_rate = self.calculate_dividend_rate(stock_data)
        stock_data['dividend_rate'] = dividend_rate
        
        # 生成建议
        suggestion, reason = self.generate_suggestion(stock_data)
        stock_data['suggestion'] = suggestion
        stock_data['suggestion_reason'] = reason
        
        return stock_data
    
    def calculate_dividend_rate(self, stock_data: Dict[str, Any]) -> float:
        """
        计算股息率
        
        Args:
            stock_data: 股票数据
        
        Returns:
            股息率
        """
        # 简化计算，实际应该从财务数据中获取
        # 这里使用预设值作为示例
        dividend_rates = {
            "600900": 3.5,  # 长江电力
            "601328": 5.0,  # 交通银行
            "515080": 4.0,  # 中证红利ETF
            "520550": 4.5,  # 港股红利低波ETF
            "513650": 1.5   # 标普500ETF
        }
        
        code = stock_data['code']
        return dividend_rates.get(code, 0)
    
    def generate_suggestion(self, stock_data: Dict[str, Any]) -> tuple:
        """
        生成操作建议
        
        Args:
            stock_data: 股票数据
        
        Returns:
            (建议, 理由)
        """
        rsi = stock_data.get('rsi', 50)
        change_percent = stock_data.get('change_percent', 0)
        dividend_rate = stock_data.get('dividend_rate', 0)
        ma20_deviation = stock_data.get('ma20_deviation', 0)
        
        # 基于RSI和涨跌幅生成建议
        if rsi < 30 and change_percent < -3:
            return "买入", "RSI超卖，价格大幅下跌，建议买入"
        elif rsi > 70 and change_percent > 5:
            return "卖出", "RSI超买，价格大幅上涨，建议卖出"
        elif dividend_rate > 4:
            return "持有", "股息率较高，建议持有"
        elif ma20_deviation < -10:
            return "加仓", "价格大幅低于20日均线，建议加仓"
        elif ma20_deviation > 10:
            return "减仓", "价格大幅高于20日均线，建议减仓"
        else:
            return "持有", "指标正常，建议持有"


# 全局技术分析实例
technical_analyzer = TechnicalAnalyzer()
