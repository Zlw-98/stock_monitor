# -*- coding: utf-8 -*-
"""
股市情况测试脚本
使用4月3日的股市情况测试系统，并推送到邮箱
"""

from src.email_pusher import email_pusher
from datetime import datetime


def test_market():
    """测试股市情况并发送邮件"""
    print("开始测试4月3日股市情况...")
    
    # 模拟4月3日的股票数据
    test_data = {
        "stocks": [
            {
                "code": "600900",
                "name": "长江电力",
                "price": 25.8,
                "change_percent": 1.2,
                "volume": 1200000,
                "avg_volume": 900000,
                "rsi": 58,
                "ma20_deviation": 3.2,
                "dividend_rate": 3.8,
                "suggestion": "持有",
                "suggestion_reason": "股息率处于合理区间，建议持有"
            },
            {
                "code": "601328",
                "name": "交通银行",
                "price": 6.8,
                "change_percent": -0.5,
                "volume": 2500000,
                "avg_volume": 2000000,
                "rsi": 45,
                "ma20_deviation": -1.5,
                "pb": 0.65,
                "suggestion": "买入",
                "suggestion_reason": "PB低于0.7，处于低估状态，建议买入"
            },
            {
                "code": "515080",
                "name": "中证红利ETF",
                "price": 1.25,
                "change_percent": 0.8,
                "volume": 5000000,
                "avg_volume": 4000000,
                "rsi": 52,
                "ma20_deviation": 2.1,
                "dividend_rate": 5.2,
                "suggestion": "持有",
                "suggestion_reason": "股息率处于合理区间，建议持有"
            },
            {
                "code": "520550",
                "name": "港股红利低波ETF",
                "price": 1.15,
                "change_percent": -0.3,
                "volume": 3000000,
                "avg_volume": 2500000,
                "rsi": 48,
                "ma20_deviation": -0.8,
                "dividend_rate": 5.8,
                "suggestion": "持有",
                "suggestion_reason": "股息率处于合理区间，建议持有"
            },
            {
                "code": "513650",
                "name": "标普500ETF南方",
                "price": 5.8,
                "change_percent": 1.5,
                "volume": 4000000,
                "avg_volume": 3500000,
                "rsi": 62,
                "ma20_deviation": 4.5,
                "pe_percentile": 65,
                "suggestion": "持有",
                "suggestion_reason": "PE分位处于合理区间，建议持有"
            }
        ],
        "sh_index_change": 0.8,
        "hk_index_change": -0.2,
        "us_index_change": 0.5,
        "macro_analysis": "4月3日无宏观数据公布\n\n未来一周公布的数据：\n- 2026-04-10 20:30：CPI（预期 3.1%）\n- 2026-04-29 02:00：FOMC（预期 5.25%-5.50%），季度会议有点阵图",
        "operation_suggestion": "4月3日市场整体稳定，建议按照定投计划执行。交通银行PB处于低估状态，可考虑适当增加配置比例。"
    }
    
    # 发送测试邮件
    success = email_pusher.send_daily_report(test_data)
    
    if success:
        print("✅ 邮件测试发送成功")
    else:
        print("❌ 邮件测试发送失败")


if __name__ == "__main__":
    test_market()
