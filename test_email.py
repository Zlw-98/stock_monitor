# -*- coding: utf-8 -*-
"""
邮件测试脚本
用于测试邮件配置是否正确
"""

from src.email_pusher import email_pusher
from datetime import datetime


def test_email():
    """测试邮件发送"""
    print("开始测试邮件发送...")
    
    # 构建测试数据
    test_data = {
        "stocks": [
            {
                "code": "600900",
                "name": "长江电力",
                "price": 25.5,
                "change_percent": 0.5,
                "volume": 1000000,
                "avg_volume": 800000,
                "rsi": 55,
                "ma20_deviation": 2.5,
                "dividend_rate": 3.5,
                "suggestion": "持有",
                "suggestion_reason": "指标正常，建议持有"
            }
        ],
        "sh_index_change": 0.5,
        "hk_index_change": -0.2,
        "us_index_change": 0.8,
        "macro_analysis": "今日无宏观数据公布\n\n未来一周公布的数据：\n- 2026-04-10 20:30：CPI（预期 3.1%）\n- 2026-04-29 02:00：FOMC（预期 5.25%-5.50%），季度会议有点阵图",
        "operation_suggestion": "测试邮件：邮件配置正常"
    }
    
    # 发送测试邮件
    success = email_pusher.send_daily_report(test_data)
    
    if success:
        print("✅ 邮件测试发送成功")
    else:
        print("❌ 邮件测试发送失败")


if __name__ == "__main__":
    test_email()
