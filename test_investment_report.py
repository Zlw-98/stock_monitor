# -*- coding: utf-8 -*-
"""
定投决策报告测试脚本
使用4月3日的股市情况测试新的定投决策报告，并推送到邮箱
"""

from src.email_pusher import email_pusher
from src.stock_fetcher import stock_fetcher
from src.config_manager import config_manager
from datetime import datetime


def test_investment_report():
    """测试定投决策报告并发送邮件"""
    print("开始测试4月3日定投决策报告...")
    
    # 从配置文件获取股票列表
    stocks = config_manager.get_stocks()
    
    # 从stock_fetcher获取真实股票数据
    stock_data = stock_fetcher.fetch_all_stocks(stocks)
    
    # 构建测试数据
    test_data = {
        "stocks": [],
        "sh_index_change": 0.8,
        "hk_index_change": -0.2,
        "us_index_change": 0.5
    }
    
    # 构建股票数据列表
    stock_names = {
        "600900": "长江电力",
        "601328": "交通银行",
        "515080": "中证红利ETF",
        "520550": "港股红利低波ETF",
        "513650": "标普500ETF南方"
    }
    
    for code, name in stock_names.items():
        if code in stock_data:
            stock = stock_data[code]
            stock_item = {
                "code": code,
                "name": name,
                "price": stock.get('price', 0),
                "change_percent": stock.get('change_percent', 0),
                "volume": stock.get('volume', 0),
                "source": stock.get('source', '估算'),
                "credibility": stock.get('credibility', 0.5)
            }
            
            # 添加估值数据
            if name == "长江电力":
                stock_item["dividend_rate"] = stock.get('dividend_rate', 3.5)
            elif name == "交通银行":
                stock_item["pb"] = stock.get('pb', 0.7)
            elif name in ["中证红利ETF", "港股红利低波ETF"]:
                stock_item["dividend_rate"] = stock.get('dividend_rate', 5.0)
            elif name == "标普500ETF南方":
                stock_item["pe_percentile"] = stock.get('pe_percentile', 60)
            
            test_data["stocks"].append(stock_item)
        else:
            print(f"❌ 无法获取 {name} 的数据")
    
    # 发送测试邮件
    success = email_pusher.send_daily_report(test_data)
    
    if success:
        print("✅ 邮件测试发送成功")
    else:
        print("❌ 邮件测试发送失败")


if __name__ == "__main__":
    test_investment_report()
