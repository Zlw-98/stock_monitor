# -*- coding: utf-8 -*-
"""
测试股票数据获取
"""

from src.stock_fetcher import stock_fetcher
from src.config_manager import config_manager

# 从配置文件获取股票列表
stocks = config_manager.get_stocks()
print(f"股票列表: {stocks}")

# 从stock_fetcher获取真实股票数据
stock_data = stock_fetcher.fetch_all_stocks(stocks)
print("\n股票数据获取结果:")
for code, data in stock_data.items():
    print(f"{code}: {data.get('price')}元, 来源: {data.get('source')}, 可信度: {data.get('credibility')}")

print("\n测试完成")