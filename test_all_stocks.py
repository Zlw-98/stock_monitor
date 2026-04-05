# -*- coding: utf-8 -*-
"""
测试所有股票数据获取
"""

import sys
sys.path.append('src')
from src.stock_fetcher import stock_fetcher
from src.config_manager import config_manager

# 从配置文件中获取所有股票
def test_all_stocks():
    print("=== 测试所有股票数据获取 ===")
    
    # 硬编码股票列表
    stocks = [
        {"code": "600900", "name": "长江电力", "market": "sh", "type": "stock"},
        {"code": "601328", "name": "交通银行", "market": "sh", "type": "stock"},
        {"code": "515080", "name": "中证红利ETF", "market": "sh", "type": "etf"},
        {"code": "520550", "name": "港股红利低波ETF", "market": "sh", "type": "hk_etf"},
        {"code": "513650", "name": "标普500ETF南方", "market": "sh", "type": "us_etf", "index": "^GSPC"}
    ]
    
    print(f"共 {len(stocks)} 个股票标的")
    
    for stock in stocks:
        print(f"\n测试 {stock['name']} ({stock['code']})...")
        data = stock_fetcher.fetch_stock_data(stock)
        
        if data:
            print(f"✓ 数据获取成功")
            print(f"  名称: {data.get('name')}")
            print(f"  价格: {data.get('price')}")
            print(f"  涨跌幅: {data.get('change_percent')}%")
            print(f"  成交量: {data.get('volume')}")
            
            # 对于美股ETF，显示标普500指数数据
            if stock.get('type') == 'us_etf':
                print(f"  标普500指数: {data.get('index_price')}")
                print(f"  标普500涨跌幅: {data.get('index_change_percent')}%")
        else:
            print(f"✗ 数据获取失败")

if __name__ == "__main__":
    test_all_stocks()
