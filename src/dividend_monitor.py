# -*- coding: utf-8 -*-
"""
分红日监控模块
监控股票的除权除息日，提供分红提醒
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Any
from .logger import logger


class DividendMonitor:
    """分红日监控类"""
    
    def __init__(self):
        """初始化分红日监控"""
        self.dividend_data = {}
    
    def get_upcoming_dividends(self, stocks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        获取即将到来的分红日
        
        Args:
            stocks: 股票列表
        
        Returns:
            分红日列表
        """
        upcoming_dividends = []
        
        # 模拟分红日数据
        # 实际应从API获取
        dividend_schedule = {
            "长江电力": {
                "ex_date": "2026-07-15",
                "dividend": 0.93,
                "type": "现金分红"
            },
            "交通银行": {
                "ex_date": "2026-06-30",
                "dividend": 0.355,
                "type": "现金分红"
            },
            "中证红利ETF": {
                "ex_date": "2026-06-15",
                "dividend": 0.075,
                "type": "现金分红"
            },
            "港股红利低波ETF": {
                "ex_date": "2026-06-20",
                "dividend": 0.08,
                "type": "现金分红"
            },
            "标普500ETF南方": {
                "ex_date": "2026-06-25",
                "dividend": 0.05,
                "type": "现金分红"
            }
        }
        
        today = datetime.now().date()
        
        for stock in stocks:
            stock_name = stock['name']
            if stock_name in dividend_schedule:
                dividend_info = dividend_schedule[stock_name]
                ex_date = datetime.strptime(dividend_info['ex_date'], '%Y-%m-%d').date()
                days_until = (ex_date - today).days
                
                if days_until >= 0:
                    upcoming_dividends.append({
                        "stock_name": stock_name,
                        "ex_date": dividend_info['ex_date'],
                        "dividend": dividend_info['dividend'],
                        "type": dividend_info['type'],
                        "days_until": days_until
                    })
        
        # 按距离今天的天数排序
        upcoming_dividends.sort(key=lambda x: x['days_until'])
        
        return upcoming_dividends
    
    def generate_dividend_alert(self, upcoming_dividends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        生成分红提醒
        
        Args:
            upcoming_dividends: 即将到来的分红日列表
        
        Returns:
            提醒列表
        """
        alerts = []
        
        for dividend in upcoming_dividends:
            if dividend['days_until'] <= 7:
                alerts.append({
                    "type": "dividend",
                    "stock_name": dividend['stock_name'],
                    "message": f"【分红提醒】{dividend['stock_name']} 将在 {dividend['days_until']} 天后（{dividend['ex_date']}）除权除息，每股分红 {dividend['dividend']} 元"
                })
        
        return alerts
    
    def generate_dividend_report(self, upcoming_dividends: List[Dict[str, Any]]) -> str:
        """
        生成分红报告
        
        Args:
            upcoming_dividends: 即将到来的分红日列表
        
        Returns:
            分红报告内容
        """
        if not upcoming_dividends:
            return "暂无即将到来的分红"
        
        report = "\n即将到来的分红：\n"
        report += "-" * 60 + "\n"
        report += "股票名称\t除权除息日\t分红金额\t距离天数\n"
        report += "-" * 60 + "\n"
        
        for dividend in upcoming_dividends:
            report += f"{dividend['stock_name']}\t{dividend['ex_date']}\t{dividend['dividend']}元\t{dividend['days_until']}天\n"
        
        report += "-" * 60 + "\n"
        
        # 计算预计分红总额
        total_dividend = sum([div['dividend'] for div in upcoming_dividends])
        report += f"预计分红总额: {total_dividend:.2f}元\n"
        
        return report


# 全局分红监控实例
dividend_monitor = DividendMonitor()