# -*- coding: utf-8 -*-
"""
配置管理模块
负责读取和解析YAML配置文件
"""

import yaml
import os
from typing import Dict, List, Any


class ConfigManager:
    """配置管理类"""
    
    def __init__(self, config_file: str = "config/config.yaml"):
        """
        初始化配置管理
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            print(f"✅ 配置文件加载成功: {self.config_file}")
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            # 使用默认配置
            self._load_default_config()
    
    def _load_default_config(self):
        """加载默认配置"""
        self.config = {
            "stocks": [
                {"code": "600900", "name": "长江电力", "market": "sh", "type": "stock"},
                {"code": "601328", "name": "交通银行", "market": "sh", "type": "stock"},
                {"code": "515080", "name": "中证红利ETF", "market": "sh", "type": "etf"},
                {"code": "520550", "name": "港股红利低波ETF", "market": "sh", "type": "hk_etf"},
                {"code": "513650", "name": "标普500ETF南方", "market": "sh", "type": "us_etf", "index": "^GSPC"}
            ],
            "alert_conditions": {
                "down_percent": -3.0,
                "up_percent": 5.0,
                "volume_multiplier": 2.0
            },
            "trading_hours": {
                "morning_start": "09:30",
                "morning_end": "11:30",
                "afternoon_start": "13:00",
                "afternoon_end": "15:00"
            },
            "check_interval": 5,
            "wechat_push": {
                "serverchan_sendkey": "",
                "wechat_robot_webhook": ""
            },
            "email_config": {
                "smtp_server": "smtp.qq.com",
                "smtp_port": 465,
                "sender_email": "",
                "sender_password": "",
                "receiver_email": "374186226@qq.com"
            },
            "daily_report_time": "15:10",
            "macro_calendar": [],
            "data_dir": "./data",
            "logs_dir": "./logs"
        }
        print("⚠️ 使用默认配置")
    
    def get_stocks(self) -> List[Dict[str, str]]:
        """获取监控股票列表"""
        return self.config.get("stocks", [])
    
    def get_alert_conditions(self) -> Dict[str, float]:
        """获取预警条件"""
        return self.config.get("alert_conditions", {})
    
    def get_trading_hours(self) -> Dict[str, str]:
        """获取交易时间"""
        return self.config.get("trading_hours", {})
    
    def get_check_interval(self) -> int:
        """获取检查间隔（分钟）"""
        return self.config.get("check_interval", 5)
    
    def get_wechat_push(self) -> Dict[str, str]:
        """获取微信推送配置"""
        return self.config.get("wechat_push", {})
    
    def get_email_config(self) -> Dict[str, Any]:
        """获取邮件配置"""
        return self.config.get("email_config", {})
    
    def get_daily_report_time(self) -> str:
        """获取日报发送时间"""
        return self.config.get("daily_report_time", "15:10")
    
    def get_macro_calendar(self) -> List[Dict[str, str]]:
        """获取宏观数据日历"""
        return self.config.get("macro_calendar", [])
    
    def get_data_dir(self) -> str:
        """获取数据存储路径"""
        return self.config.get("data_dir", "./data")
    
    def get_logs_dir(self) -> str:
        """获取日志存储路径"""
        return self.config.get("logs_dir", "./logs")
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        # 确保数据目录存在
        data_dir = self.get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        
        # 确保日志目录存在
        logs_dir = self.get_logs_dir()
        os.makedirs(logs_dir, exist_ok=True)
        
        print(f"✅ 确保目录存在: {data_dir}, {logs_dir}")
    
    def get_monthly_investment(self) -> float:
        """
        获取每月定投金额
        
        Returns:
            每月定投金额
        """
        return self.config.get('monthly_investment', 4000)
    
    def get_target_allocations(self) -> Dict[str, float]:
        """
        获取目标配置比例
        
        Returns:
            目标配置比例
        """
        return self.config.get('target_allocations', {
            "长江电力": 20,
            "交通银行": 20,
            "中证红利ETF": 20,
            "港股红利低波ETF": 20,
            "标普500ETF南方": 20
        })
    
    def get_current_allocations(self) -> Dict[str, float]:
        """
        获取当前配置比例
        
        Returns:
            当前配置比例
        """
        return self.config.get('current_allocations', {
            "长江电力": 22,
            "交通银行": 18,
            "中证红利ETF": 21,
            "港股红利低波ETF": 19,
            "标普500ETF南方": 20
        })


# 全局配置实例
config_manager = ConfigManager()
