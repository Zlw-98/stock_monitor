# -*- coding: utf-8 -*-
"""
推送逻辑模块
负责根据定投策略优化推送逻辑，避免过度提醒
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from .config_manager import config_manager
from .portfolio_manager import portfolio_manager


class PushLogic:
    """推送逻辑管理器"""
    
    def __init__(self):
        """初始化推送逻辑管理器"""
        self.data_file = "data/push_state.json"
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """
        加载推送状态
        
        Returns:
            推送状态
        """
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ 加载推送状态失败: {e}")
        
        return {
            "last_valuation_state": {},
            "last_investment_push_date": None,
            "last_daily_push_date": None
        }
    
    def _save_state(self):
        """保存推送状态"""
        try:
            # 确保数据目录存在
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存推送状态失败: {e}")
    
    def should_push_investment_day(self) -> bool:
        """
        判断是否应该推送定投日提醒
        
        Returns:
            是否应该推送
        """
        today = datetime.now().strftime("%Y-%m-%d")
        last_date = self.state.get("last_investment_push_date")
        
        # 检查是否是每月10日
        day = datetime.now().day
        
        # 每月10日推送
        if day == 10 and last_date != today:
            return True
        
        return False
    
    def check_valuation_changes(self, current_valuation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检查估值变化
        
        Args:
            current_valuation: 当前估值数据
        
        Returns:
            估值变化列表
        """
        changes = []
        last_state = self.state.get("last_valuation_state", {})
        
        for name, data in current_valuation.items():
            last_data = last_state.get(name, {})
            current_status = data.get("status")
            last_status = last_data.get("status")
            
            # 检查估值状态是否变化
            if current_status != last_status and current_status is not None:
                changes.append({
                    "name": name,
                    "old_status": last_status,
                    "new_status": current_status,
                    "data": data
                })
        
        # 更新状态
        self.state["last_valuation_state"] = current_valuation
        self._save_state()
        
        return changes
    
    def should_push_daily(self) -> bool:
        """
        判断是否应该推送日常提醒
        
        Returns:
            是否应该推送
        """
        today = datetime.now().strftime("%Y-%m-%d")
        last_date = self.state.get("last_daily_push_date")
        
        # 每天最多推送一次日常提醒
        return last_date != today
    
    def record_investment_push(self):
        """记录定投日推送"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.state["last_investment_push_date"] = today
        self._save_state()
    
    def record_daily_push(self):
        """记录日常推送"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.state["last_daily_push_date"] = today
        self._save_state()
    
    def generate_investment_day_message(self, investment_plan: List[Dict[str, Any]], 
                                      current_valuation: Dict[str, Any]) -> str:
        """
        生成定投日推送消息
        
        Args:
            investment_plan: 投资计划
            current_valuation: 当前估值
        
        Returns:
            推送消息
        """
        message = "📅 定投日提醒\n\n"
        message += "本月定投建议：\n"
        
        for item in investment_plan:
            name = item['name']
            amount = item['suggested_amount']
            message += f"• {name}：¥{amount:.0f}元\n"
        
        message += "\n当前估值状态：\n"
        
        for name, data in current_valuation.items():
            status = data.get("status", "未知")
            value = data.get("value", "N/A")
            message += f"• {name}：{value}（{status}）\n"
        
        message += "\n👉 建议按计划执行定投！"
        
        return message
    
    def generate_valuation_change_message(self, changes: List[Dict[str, Any]]) -> str:
        """
        生成估值变化推送消息
        
        Args:
            changes: 估值变化列表
        
        Returns:
            推送消息
        """
        message = "📊 估值变化提醒\n\n"
        
        for change in changes:
            name = change['name']
            old_status = change['old_status'] or '未知'
            new_status = change['new_status']
            data = change['data']
            value = data.get("value", "N/A")
            
            message += f"{name}：\n"
            message += f"  从 {old_status} → {new_status}\n"
            message += f"  当前估值：{value}\n"
            
            # 根据新状态给出建议
            if new_status == "低估":
                message += "  👉 建议增加定投权重\n"
            elif new_status == "高估":
                message += "  👉 建议减少定投权重\n"
            message += "\n"
        
        return message
    
    def generate_daily_message(self, market_data: Dict[str, Any], 
                                has_changes: bool) -> str:
        """
        生成日常推送消息
        
        Args:
            market_data: 市场数据
            has_changes: 是否有变化
        
        Returns:
            推送消息
        """
        if not has_changes:
            return "📈 今日无显著变化，无需操作"
        
        message = "📈 每日行情摘要\n\n"
        
        for name, data in market_data.items():
            change = data.get("change_percent", 0)
            message += f"• {name}：{change:+.2f}%\n"
        
        message += "\n👉 有信号变化，请关注估值变化"
        
        return message


# 全局推送逻辑管理器实例
push_logic = PushLogic()
