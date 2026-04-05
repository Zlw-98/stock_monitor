# -*- coding: utf-8 -*-
"""
预警管理器模块
负责管理预警信息，避免重复推送
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta


class AlertManager:
    """预警管理器"""
    
    def __init__(self):
        """初始化预警管理器"""
        self.alert_history = {}  # 存储预警历史
        self.cooldown_hours = 24  # 预警冷却时间（小时）
    
    def filter_alerts(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        过滤重复预警
        
        Args:
            alerts: 预警信息列表
        
        Returns:
            过滤后的预警信息列表
        """
        filtered_alerts = []
        current_time = datetime.now()
        
        for alert in alerts:
            # 生成预警唯一标识
            alert_key = f"{alert['code']}_{alert['type']}"
            
            # 检查是否在冷却期内
            if self._is_in_cooldown(alert_key, current_time):
                print(f"预警 {alert['message']} 在冷却期内，跳过发送")
                continue
            
            # 添加到过滤后的列表
            filtered_alerts.append(alert)
            
            # 更新预警历史
            self._update_alert_history(alert_key, current_time)
        
        return filtered_alerts
    
    def _is_in_cooldown(self, alert_key: str, current_time: datetime) -> bool:
        """
        检查预警是否在冷却期内
        
        Args:
            alert_key: 预警唯一标识
            current_time: 当前时间
        
        Returns:
            是否在冷却期内
        """
        if alert_key not in self.alert_history:
            return False
        
        last_alert_time = self.alert_history[alert_key]
        cooldown_period = timedelta(hours=self.cooldown_hours)
        
        return current_time - last_alert_time < cooldown_period
    
    def _update_alert_history(self, alert_key: str, current_time: datetime):
        """
        更新预警历史
        
        Args:
            alert_key: 预警唯一标识
            current_time: 当前时间
        """
        self.alert_history[alert_key] = current_time
    
    def clear_old_alerts(self):
        """
        清理过期的预警历史
        """
        current_time = datetime.now()
        cooldown_period = timedelta(hours=self.cooldown_hours)
        
        # 过滤出未过期的预警
        self.alert_history = {
            key: time for key, time in self.alert_history.items()
            if current_time - time < cooldown_period
        }


# 全局预警管理实例
alert_manager = AlertManager()
