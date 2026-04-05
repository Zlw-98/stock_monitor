# -*- coding: utf-8 -*-
"""
测试股票数据获取模块
"""

import sys
sys.path.append('src')
from src.stock_fetcher import stock_fetcher

# 测试港股数据获取
def test_hk_stock():
    print("\n=== 测试港股数据获取 ===")
    hk_stock = {
        "code": "520550",
        "name": "港股红利低波ETF",
        "market": "sh",
        "type": "hk_etf"
    }
    
    try:
        data = stock_fetcher.fetch_stock_data(hk_stock)
        print(f"港股数据获取结果: {data}")
    except Exception as e:
        print(f"港股数据获取失败: {e}")

# 测试美股数据获取
def test_us_stock():
    print("\n=== 测试美股数据获取 ===")
    us_stock = {
        "code": "513650",
        "name": "标普500ETF南方",
        "market": "sh",
        "type": "us_etf",
        "index": "^GSPC"
    }
    
    try:
        data = stock_fetcher.fetch_stock_data(us_stock)
        print(f"美股数据获取结果: {data}")
    except Exception as e:
        print(f"美股数据获取失败: {e}")

# 测试A股数据获取（作为参考）
def test_a_stock():
    print("\n=== 测试A股数据获取 ===")
    a_stock = {
        "code": "601328",
        "name": "交通银行",
        "market": "sh",
        "type": "stock"
    }
    
    try:
        data = stock_fetcher._fetch_a_stock(a_stock)
        print(f"A股数据获取结果: {data}")
    except Exception as e:
        print(f"A股数据获取失败: {e}")

if __name__ == "__main__":
    test_a_stock()
    test_hk_stock()
    test_us_stock()
