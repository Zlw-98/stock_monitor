# -*- coding: utf-8 -*-
"""
微信推送模块
负责将预警信息通过微信发送给用户
"""

import requests
from typing import List, Dict, Any
from .config_manager import config_manager


class WechatPusher:
    """微信推送器"""
    
    def __init__(self):
        """初始化微信推送器"""
        self.wechat_config = config_manager.get_wechat_push()
    
    def push_alerts(self, alerts: List[Dict[str, Any]]) -> bool:
        """
        推送预警信息
        
        Args:
            alerts: 预警信息列表
        
        Returns:
            是否推送成功
        """
        if not alerts:
            return True
        
        # 构建消息内容
        message = self._build_message(alerts)
        
        # 尝试通过Server酱推送
        if self._push_via_serverchan(message):
            return True
        
        # 尝试通过企业微信机器人推送
        if self._push_via_wechat_robot(message):
            return True
        
        return False
    
    def _build_message(self, alerts: List[Dict[str, Any]]) -> str:
        """
        构建消息内容
        
        Args:
            alerts: 预警信息列表
        
        Returns:
            消息内容
        """
        message = "📊 投资提醒\n\n"
        
        for alert in alerts:
            message += f"{alert['message']}\n\n"
        
        message += "请注意风险控制！"
        
        return message
    
    def _push_via_serverchan(self, message: str) -> bool:
        """
        通过Server酱推送消息
        
        Args:
            message: 消息内容
        
        Returns:
            是否推送成功
        """
        sendkey = self.wechat_config.get('serverchan_sendkey', '')
        if not sendkey:
            return False
        
        try:
            url = f"https://sctapi.ftqq.com/{sendkey}.send"
            data = {
                "title": "股票监控预警",
                "desp": message
            }
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('code') == 0:
                print("✅ Server酱推送成功")
                return True
            else:
                print(f"❌ Server酱推送失败: {result.get('message')}")
                return False
                
        except Exception as e:
            print(f"❌ Server酱推送异常: {e}")
            return False
    
    def _push_via_wechat_robot(self, message: str) -> bool:
        """
        通过企业微信机器人推送消息
        
        Args:
            message: 消息内容
        
        Returns:
            是否推送成功
        """
        webhook = self.wechat_config.get('wechat_robot_webhook', '')
        if not webhook:
            return False
        
        try:
            data = {
                "msgtype": "text",
                "text": {
                    "content": message
                }
            }
            
            response = requests.post(webhook, json=data, timeout=10)
            result = response.json()
            
            if result.get('errcode') == 0:
                print("✅ 企业微信机器人推送成功")
                return True
            else:
                print(f"❌ 企业微信机器人推送失败: {result.get('errmsg')}")
                return False
                
        except Exception as e:
            print(f"❌ 企业微信机器人推送异常: {e}")
            return False


# 全局微信推送实例
wechat_pusher = WechatPusher()

# 导出推送函数
def push_alerts(alerts: List[Dict[str, Any]]) -> bool:
    """
    推送预警信息
    
    Args:
        alerts: 预警信息列表
    
    Returns:
        是否推送成功
    """
    return wechat_pusher.push_alerts(alerts)
