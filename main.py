# -*- coding: utf-8 -*-
"""
股票监控系统主程序
监控交通银行、长江电力、中证红利ETF、港股红利低波ETF、标普500ETF
支持预警条件：下跌超过3%、上涨超过5%、成交量翻倍
支持微信推送和邮件日报
"""

from src.config_manager import config_manager
from src.stock_fetcher import stock_fetcher
from src.alert_checker import alert_checker
from src.alert_manager import alert_manager
from src.wechat_push import push_alerts
from src.email_pusher import email_pusher
from src.technical_analyzer import technical_analyzer
from src.macro_monitor import macro_monitor
from src.logger import logger
from src.scheduler import run_scheduler
from datetime import datetime
from typing import Dict, Any


def check_stocks():
    """检查所有监控股票并发送预警"""
    try:
        # 1. 获取股票数据
        logger.info("正在获取股票数据...")
        stocks = config_manager.get_stocks()
        quotes = stock_fetcher.fetch_all_stocks(stocks)
        
        if not quotes:
            logger.warning("未能获取任何股票数据")
            return
        
        logger.info(f"获取到 {len(quotes)} 只股票数据")
        for code, quote in quotes.items():
            logger.info(f"  - {quote['name']}({code}): {quote['price']}元, 涨跌幅: {quote['change_percent']}%")
        
        # 2. 检查预警条件
        logger.info("正在检查预警条件...")
        alerts = alert_checker.check_all(quotes)
        
        if not alerts:
            logger.info("✅ 无预警")
            return
        
        # 3. 过滤重复预警（冷却期内不重复发送）
        logger.info(f"检测到 {len(alerts)} 条预警")
        filtered_alerts = alert_manager.filter_alerts(alerts)
        
        if not filtered_alerts:
            logger.info("  (所有预警都在冷却期内，跳过发送)")
            return
        
        logger.info(f"  需要发送: {len(filtered_alerts)} 条")
        
        for alert in alerts:
            is_sending = alert in filtered_alerts
            status = "✓" if is_sending else "(冷却中)"
            logger.info(f"{status} {alert['message']}")
        
        # 4. 微信推送已禁用，只通过邮件推送
        logger.info("微信推送已禁用，预警信息将在每日邮件中汇总")
            
    except Exception as e:
        logger.error(f"检查股票失败: {e}")


def send_daily_report():
    """发送每日技术分析日报"""
    try:
        # 1. 获取股票数据
        logger.info("正在获取股票数据...")
        stocks = config_manager.get_stocks()
        quotes = stock_fetcher.fetch_all_stocks(stocks)
        
        if not quotes:
            logger.warning("未能获取任何股票数据，跳过发送日报")
            return
        
        # 2. 分析股票技术指标
        logger.info("正在分析技术指标...")
        analyzed_stocks = []
        for code, quote in quotes.items():
            analyzed_stock = technical_analyzer.analyze_stock(quote)
            analyzed_stocks.append(analyzed_stock)
        
        # 3. 生成宏观数据分析
        logger.info("正在生成宏观数据分析...")
        macro_analysis = macro_monitor.generate_macro_analysis()
        
        # 4. 构建报告数据
        report_data = {
            "stocks": analyzed_stocks,
            "sh_index_change": 0.5,  # 示例数据
            "hk_index_change": -0.2,  # 示例数据
            "us_index_change": 0.8,  # 示例数据
            "macro_analysis": macro_analysis,
            "operation_suggestion": "标普500ETF继续保持每月500元定投；交通银行7元以上暂缓定投"
        }
        
        # 5. 发送邮件
        logger.info("正在发送每日技术分析日报...")
        success = email_pusher.send_daily_report(report_data)
        
        if success:
            logger.info("✅ 每日技术分析日报发送成功")
        else:
            logger.error("❌ 每日技术分析日报发送失败")
            
    except Exception as e:
        logger.error(f"发送日报失败: {e}")


def main():
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════╗
║          股票监控系统 - Stock Alert Monitor          ║
╠══════════════════════════════════════════════════════╣
║  监控股票:                                           ║
║    - 长江电力 (600900.SH)                           ║
║    - 交通银行 (601328.SH)                           ║
║    - 中证红利ETF (515080.SH)                        ║
║    - 港股红利低波ETF (520550)                       ║
║    - 标普500ETF南方 (513650)                        ║
╠══════════════════════════════════════════════════════╣
║  预警条件:                                           ║
║    - 下跌超过 3%                                     ║
║    - 上涨超过 5%                                     ║
║    - 成交量翻倍                                      ║
╠══════════════════════════════════════════════════════╣
║  推送方式:                                           ║
║    - 白天实时预警 → 微信推送                         ║
║    - 每日收盘后 → 邮件日报                           ║
╠══════════════════════════════════════════════════════╣
║  检查时间: 交易日 09:30-11:30, 13:00-15:00          ║
║  检查间隔: 每 5 分钟                                 ║
╚══════════════════════════════════════════════════════╝
    """)
    
    # 确保必要的目录存在
    config_manager.ensure_directories()
    
    # 启动调度器
    run_scheduler(check_stocks, send_daily_report)
    
    # 保持程序运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("用户终止程序")


if __name__ == "__main__":
    # 导入time模块
    import time
    main()
