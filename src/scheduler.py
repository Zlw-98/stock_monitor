# -*- coding: utf-8 -*-
"""
定时调度模块
负责定时执行股票检查和日报发送任务
"""

import time
import threading
from datetime import datetime
from typing import Callable
from .config_manager import config_manager
from .logger import logger


class Scheduler:
    """定时调度器"""
    
    def __init__(self):
        """初始化定时调度器"""
        self.check_interval = config_manager.get_check_interval()
        self.daily_report_time = config_manager.get_daily_report_time()
        self.trading_hours = config_manager.get_trading_hours()
        self.running = False
        self.thread = None
    
    def run_scheduler(self, check_function: Callable, report_function: Callable = None):
        """
        启动调度器
        
        Args:
            check_function: 检查函数
            report_function: 日报发送函数
        """
        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop, args=(check_function, report_function))
        self.thread.daemon = True
        self.thread.start()
        logger.info("调度器启动成功")
    
    def _scheduler_loop(self, check_function: Callable, report_function: Callable = None):
        """
        调度器主循环
        
        Args:
            check_function: 检查函数
            report_function: 日报发送函数
        """
        while self.running:
            try:
                current_time = datetime.now()
                current_time_str = current_time.strftime("%H:%M")
                
                # 检查是否在交易时间内
                if self._is_trading_time(current_time):
                    # 执行股票检查
                    check_function()
                    
                    # 等待检查间隔
                    logger.info(f"等待 {self.check_interval} 分钟后再次检查")
                    time.sleep(self.check_interval * 60)
                else:
                    # 检查是否到了日报发送时间
                    if report_function and current_time_str == self.daily_report_time:
                        report_function()
                        # 避免重复发送
                        time.sleep(60)
                    else:
                        # 非交易时间，每5分钟检查一次
                        time.sleep(300)
            except Exception as e:
                logger.error(f"调度器执行失败: {e}")
                time.sleep(60)
    
    def _is_trading_time(self, current_time: datetime) -> bool:
        """
        检查是否在交易时间内
        
        Args:
            current_time: 当前时间
        
        Returns:
            是否在交易时间内
        """
        # 检查是否是交易日（简化处理，实际应该考虑节假日）
        if current_time.weekday() >= 5:  # 周六周日
            return False
        
        # 检查上午交易时间
        morning_start = datetime.strptime(self.trading_hours.get('morning_start', '09:30'), "%H:%M").time()
        morning_end = datetime.strptime(self.trading_hours.get('morning_end', '11:30'), "%H:%M").time()
        
        # 检查下午交易时间
        afternoon_start = datetime.strptime(self.trading_hours.get('afternoon_start', '13:00'), "%H:%M").time()
        afternoon_end = datetime.strptime(self.trading_hours.get('afternoon_end', '15:00'), "%H:%M").time()
        
        current_time_only = current_time.time()
        
        return (morning_start <= current_time_only <= morning_end) or (afternoon_start <= current_time_only <= afternoon_end)
    
    def stop(self):
        """
        停止调度器
        """
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("调度器停止成功")


# 全局调度器实例
scheduler = Scheduler()

# 导出调度函数
def run_scheduler(check_function: Callable, report_function: Callable = None):
    """
    启动调度器
    
    Args:
        check_function: 检查函数
        report_function: 日报发送函数
    """
    scheduler.run_scheduler(check_function, report_function)


def stop_scheduler():
    """
    停止调度器
    """
    scheduler.stop()
