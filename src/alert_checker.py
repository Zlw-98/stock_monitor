# -*- coding: utf-8 -*-
"""
预警检查模块
负责检查股票是否达到预警条件
"""

from typing import Dict, List, Any, Optional
from .config_manager import config_manager


class AlertChecker:
    """预警检查器"""
    
    def __init__(self):
        """初始化预警检查器"""
        self.alert_conditions = config_manager.get_alert_conditions()
    
    def check_all(self, stocks_data: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检查所有股票的预警条件
        
        Args:
            stocks_data: 股票数据字典
        
        Returns:
            预警信息列表
        """
        alerts = []
        
        for code, data in stocks_data.items():
            stock_alerts = self.check_stock(data)
            alerts.extend(stock_alerts)
        
        return alerts
    
    def check_stock(self, stock_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检查单个股票的预警条件
        
        Args:
            stock_data: 股票数据
        
        Returns:
            预警信息列表
        """
        alerts = []
        
        # 检查下跌预警
        down_alert = self._check_down_alert(stock_data)
        if down_alert:
            alerts.append(down_alert)
        
        # 检查上涨预警
        up_alert = self._check_up_alert(stock_data)
        if up_alert:
            alerts.append(up_alert)
        
        # 检查成交量预警
        volume_alert = self._check_volume_alert(stock_data)
        if volume_alert:
            alerts.append(volume_alert)
        
        # 检查估值预警
        valuation_alert = self._check_valuation_alert(stock_data)
        if valuation_alert:
            alerts.append(valuation_alert)
        
        return alerts
    
    def _check_valuation_alert(self, stock_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        检查估值预警
        
        Args:
            stock_data: 股票数据
        
        Returns:
            预警信息，无预警返回None
        """
        name = stock_data.get('name', '')
        
        # 根据股票类型检查不同的估值指标
        if name == "标普500ETF南方":
            pe_percentile = stock_data.get('pe_percentile')
            if pe_percentile is not None:
                # 判断估值区间
                if pe_percentile < 30:
                    valuation_status = "低估"
                    investment_advice = "建议加仓（1.5倍）"
                elif pe_percentile < 70:
                    valuation_status = "正常"
                    investment_advice = "建议正常投入"
                else:
                    valuation_status = "高估"
                    investment_advice = "建议减少投入"
                
                return {
                    "type": "valuation",
                    "code": stock_data['code'],
                    "name": name,
                    "message": f"{name}：\nPE分位 = {pe_percentile}%（{valuation_status}）\n👉 {investment_advice}",
                    "valuation_status": valuation_status,
                    "investment_advice": investment_advice,
                    "timestamp": stock_data['timestamp']
                }
        
        elif name in ["中证红利ETF", "港股红利低波ETF"]:
            dividend_rate = stock_data.get('dividend_rate')
            if dividend_rate is not None:
                # 判断估值区间
                if dividend_rate > 6:
                    valuation_status = "低估"
                    investment_advice = "建议加仓（1.5倍）"
                elif dividend_rate > 4:
                    valuation_status = "正常"
                    investment_advice = "建议正常投入"
                else:
                    valuation_status = "高估"
                    investment_advice = "建议减少投入"
                
                return {
                    "type": "valuation",
                    "code": stock_data['code'],
                    "name": name,
                    "message": f"{name}：\n股息率 = {dividend_rate}%（{valuation_status}）\n👉 {investment_advice}",
                    "valuation_status": valuation_status,
                    "investment_advice": investment_advice,
                    "timestamp": stock_data['timestamp']
                }
        
        elif name == "长江电力":
            dividend_rate = stock_data.get('dividend_rate')
            if dividend_rate is not None:
                # 判断估值区间
                if dividend_rate > 4:
                    valuation_status = "低估"
                    investment_advice = "建议加仓（1.2倍）"
                elif dividend_rate > 3:
                    valuation_status = "正常"
                    investment_advice = "建议正常投入"
                else:
                    valuation_status = "高估"
                    investment_advice = "建议减少投入"
                
                return {
                    "type": "valuation",
                    "code": stock_data['code'],
                    "name": name,
                    "message": f"{name}：\n股息率 = {dividend_rate}%（{valuation_status}）\n👉 {investment_advice}",
                    "valuation_status": valuation_status,
                    "investment_advice": investment_advice,
                    "timestamp": stock_data['timestamp']
                }
        
        elif name == "交通银行":
            pb = stock_data.get('pb')
            if pb is not None:
                # 判断估值区间
                if pb < 0.7:
                    valuation_status = "低估"
                    investment_advice = "建议加仓（1.5倍）"
                elif pb < 1:
                    valuation_status = "正常"
                    investment_advice = "建议正常投入"
                else:
                    valuation_status = "高估"
                    investment_advice = "建议减少投入"
                
                return {
                    "type": "valuation",
                    "code": stock_data['code'],
                    "name": name,
                    "message": f"{name}：\nPB = {pb}（{valuation_status}）\n👉 {investment_advice}",
                    "valuation_status": valuation_status,
                    "investment_advice": investment_advice,
                    "timestamp": stock_data['timestamp']
                }
        
        return None
    
    def _check_down_alert(self, stock_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        检查下跌预警
        
        Args:
            stock_data: 股票数据
        
        Returns:
            预警信息，无预警返回None
        """
        down_threshold = self.alert_conditions.get('down_percent', -3.0)
        change_percent = stock_data.get('change_percent', 0)
        
        if change_percent < down_threshold:
            return {
                "type": "down",
                "code": stock_data['code'],
                "name": stock_data['name'],
                "message": f"【价格预警】{stock_data['name']} 现价{stock_data['price']}，跌幅{change_percent}%，超过预警线{down_threshold}%",
                "price": stock_data['price'],
                "change_percent": change_percent,
                "threshold": down_threshold,
                "timestamp": stock_data['timestamp']
            }
        
        return None
    
    def _check_up_alert(self, stock_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        检查上涨预警
        
        Args:
            stock_data: 股票数据
        
        Returns:
            预警信息，无预警返回None
        """
        up_threshold = self.alert_conditions.get('up_percent', 5.0)
        change_percent = stock_data.get('change_percent', 0)
        
        if change_percent > up_threshold:
            return {
                "type": "up",
                "code": stock_data['code'],
                "name": stock_data['name'],
                "message": f"【价格预警】{stock_data['name']} 现价{stock_data['price']}，涨幅{change_percent}%，超过预警线{up_threshold}%",
                "price": stock_data['price'],
                "change_percent": change_percent,
                "threshold": up_threshold,
                "timestamp": stock_data['timestamp']
            }
        
        return None
    
    def _check_volume_alert(self, stock_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        检查成交量预警
        
        Args:
            stock_data: 股票数据
        
        Returns:
            预警信息，无预警返回None
        """
        volume_multiplier = self.alert_conditions.get('volume_multiplier', 2.0)
        current_volume = stock_data.get('volume', 0)
        avg_volume = stock_data.get('avg_volume', 0)
        
        if avg_volume > 0 and current_volume > avg_volume * volume_multiplier:
            return {
                "type": "volume",
                "code": stock_data['code'],
                "name": stock_data['name'],
                "message": f"【成交量预警】{stock_data['name']} 成交量异常放大，当前{current_volume}，5日均量{avg_volume}，倍数{current_volume/avg_volume:.2f}",
                "current_volume": current_volume,
                "avg_volume": avg_volume,
                "multiplier": current_volume/avg_volume,
                "threshold": volume_multiplier,
                "timestamp": stock_data['timestamp']
            }
        
        return None


# 全局预警检查实例
alert_checker = AlertChecker()
