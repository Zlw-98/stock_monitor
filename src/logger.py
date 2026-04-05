# -*- coding: utf-8 -*-
"""
日志文件模块
负责记录系统运行日志
"""

import os
import logging
from datetime import datetime, timedelta
from .config_manager import config_manager


class Logger:
    """日志记录器"""
    
    def __init__(self):
        """初始化日志记录器"""
        self.logs_dir = config_manager.get_logs_dir()
        os.makedirs(self.logs_dir, exist_ok=True)
        self._setup_logger()
    
    def _setup_logger(self):
        """设置日志记录器"""
        # 创建日志记录器
        self.logger = logging.getLogger("stock_monitor")
        self.logger.setLevel(logging.INFO)
        
        # 清除现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 创建文件处理器
        log_file = os.path.join(self.logs_dir, f"stock_monitor_{datetime.now().strftime('%Y-%m-%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """
        记录信息日志
        
        Args:
            message: 日志信息
        """
        self.logger.info(message)
    
    def warning(self, message: str):
        """
        记录警告日志
        
        Args:
            message: 日志信息
        """
        self.logger.warning(message)
    
    def error(self, message: str):
        """
        记录错误日志
        
        Args:
            message: 日志信息
        """
        self.logger.error(message)
    
    def clear_old_logs(self, days: int = 30):
        """
        清理过期日志
        
        Args:
            days: 保留天数
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for filename in os.listdir(self.logs_dir):
                if filename.startswith("stock_monitor_") and filename.endswith(".log"):
                    file_date_str = filename.split("_")[2].split(".")[0]
                    try:
                        file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
                        if file_date < cutoff_date:
                            file_path = os.path.join(self.logs_dir, filename)
                            os.remove(file_path)
                            self.info(f"清理过期日志: {filename}")
                    except ValueError:
                        pass
        except Exception as e:
            self.error(f"清理过期日志失败: {e}")


# 全局日志记录实例
logger = Logger()
