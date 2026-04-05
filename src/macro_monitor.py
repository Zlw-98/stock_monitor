# -*- coding: utf-8 -*-
"""
宏观数据监控模块
负责监控宏观经济数据的公布情况
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
from .config_manager import config_manager


class MacroMonitor:
    """宏观数据监控器"""
    
    def __init__(self):
        """初始化宏观数据监控器"""
        self.macro_calendar = config_manager.get_macro_calendar()
    
    def get_today_macro_data(self) -> List[Dict[str, Any]]:
        """
        获取今天的宏观数据
        
        Returns:
            今天的宏观数据列表
        """
        today = datetime.now().strftime("%Y-%m-%d")
        today_data = []
        
        for data in self.macro_calendar:
            if data.get('date') == today:
                # 尝试获取实际值
                actual_value = self._fetch_actual_value(data)
                if actual_value:
                    data['actual'] = actual_value
                today_data.append(data)
        
        return today_data
    
    def get_upcoming_macro_data(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取未来几天的宏观数据
        
        Args:
            days: 未来天数
        
        Returns:
            未来几天的宏观数据列表
        """
        today = datetime.now()
        upcoming_data = []
        
        for data in self.macro_calendar:
            data_date = datetime.strptime(data.get('date'), "%Y-%m-%d")
            if 0 < (data_date - today).days <= days:
                upcoming_data.append(data)
        
        return upcoming_data
    
    def _fetch_actual_value(self, data: Dict[str, Any]) -> str:
        """
        尝试获取实际值
        
        Args:
            data: 宏观数据
        
        Returns:
            实际值
        """
        # 这里简化处理，实际应该从investing.com或tradingeconomics获取
        # 这里返回None，实际项目中需要实现具体的抓取逻辑
        return None
    
    def generate_macro_analysis(self) -> str:
        """
        生成宏观数据分析
        
        Returns:
            宏观数据分析
        """
        today_data = self.get_today_macro_data()
        upcoming_data = self.get_upcoming_macro_data()
        
        analysis = ""
        
        # 分析今天的数据
        if today_data:
            analysis += "今日公布的数据：\n"
            for data in today_data:
                name = data.get('name')
                time = data.get('time', '')
                expected = data.get('expected', '')
                previous = data.get('previous', '')
                actual = data.get('actual', '暂未公布')
                note = data.get('note', '')
                
                analysis += f"- {name} ({time}): 预期 {expected}，前值 {previous}，实际 {actual}"
                if note:
                    analysis += f"，{note}"
                analysis += "\n"
        else:
            analysis += "今日无宏观数据公布\n"
        
        # 分析未来的数据
        if upcoming_data:
            analysis += "\n未来一周公布的数据：\n"
            for data in upcoming_data:
                name = data.get('name')
                date = data.get('date')
                time = data.get('time', '')
                expected = data.get('expected', '')
                note = data.get('note', '')
                
                analysis += f"- {date} {time}：{name}"
                if expected:
                    analysis += f"（预期 {expected}）"
                if note:
                    analysis += f"，{note}"
                analysis += "\n"
        else:
            analysis += "\n未来一周无宏观数据公布\n"
        
        return analysis
    
    def get_macro_impact(self, data_name: str, actual_value: str, expected_value: str) -> str:
        """
        分析宏观数据对市场的影响
        
        Args:
            data_name: 数据名称
            actual_value: 实际值
            expected_value: 预期值
        
        Returns:
            影响分析
        """
        # 简化处理，实际需要根据具体数据类型和市场情况分析
        if not actual_value:
            return "数据尚未公布，暂无影响分析"
        
        # 这里只是示例，实际需要更复杂的分析逻辑
        impact_analysis = {
            "CPI": "CPI数据低于预期，可能意味着通胀压力减轻，有利于股市上涨",
            "非农": "非农数据高于预期，说明就业市场强劲，有利于经济增长",
            "PCE": "PCE数据低于预期，可能意味着通胀压力减轻，有利于股市上涨",
            "FOMC": "FOMC会议决定维持利率不变，符合市场预期"
        }
        
        return impact_analysis.get(data_name, "数据公布对市场影响中性")


# 全局宏观监控实例
macro_monitor = MacroMonitor()
