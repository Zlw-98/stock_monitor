# -*- coding: utf-8 -*-
"""
测试推送功能
"""

import sys
sys.path.append('src')
from src.wechat_push import wechat_pusher
from src.email_pusher import email_pusher

# 测试微信推送
def test_wechat_push():
    print("\n=== 测试微信推送 ===")
    
    # 构建测试预警信息
    alerts = [
        {
            "message": "交通银行：PB = 0.65（低估）\n👉 建议加仓（1.5倍）"
        },
        {
            "message": "标普500：PE分位 = 75%\n👉 建议减少投入"
        }
    ]
    
    success = wechat_pusher.push_alerts(alerts)
    if success:
        print("✅ 微信推送测试成功")
    else:
        print("❌ 微信推送测试失败（可能是配置未设置）")

# 测试邮件推送
def test_email_push():
    print("\n=== 测试邮件推送 ===")
    
    # 构建测试报告数据
    report_data = {
        "date": "2026-04-05",
        "market_summary": {
            "上证指数": "-0.5%",
            "恒生指数": "-0.2%",
            "标普500": "+0.1%"
        },
        "stocks": [
            {
                "code": "600900",
                "name": "长江电力",
                "price": 26.7,
                "change_percent": -1.15,
                "valuation": {
                    "value": "3.8%",
                    "status": "正常",
                    "type": "股息率"
                }
            },
            {
                "code": "601328",
                "name": "交通银行",
                "price": 6.99,
                "change_percent": -1.41,
                "valuation": {
                    "value": "0.65",
                    "status": "低估",
                    "type": "PB"
                }
            },
            {
                "code": "515080",
                "name": "中证红利ETF",
                "price": 1.58,
                "change_percent": -1.5,
                "valuation": {
                    "value": "5.2%",
                    "status": "正常",
                    "type": "股息率"
                }
            },
            {
                "code": "520550",
                "name": "港股红利低波ETF",
                "price": 1.181,
                "change_percent": 0.25,
                "valuation": {
                    "value": "5.8%",
                    "status": "正常",
                    "type": "股息率"
                }
            },
            {
                "code": "513650",
                "name": "标普500ETF南方",
                "price": 1.662,
                "change_percent": 0.24,
                "valuation": {
                    "value": "65%",
                    "status": "正常",
                    "type": "PE分位"
                }
            }
        ],
        "investment_plan": [
            {
                "name": "长江电力",
                "suggested_amount": 800,
                "ratio": 0.2
            },
            {
                "name": "交通银行",
                "suggested_amount": 1200,
                "ratio": 0.3
            },
            {
                "name": "中证红利ETF",
                "suggested_amount": 800,
                "ratio": 0.2
            },
            {
                "name": "港股红利低波ETF",
                "suggested_amount": 600,
                "ratio": 0.15
            },
            {
                "name": "标普500ETF南方",
                "suggested_amount": 600,
                "ratio": 0.15
            }
        ],
        "rebalance_tips": "当前持仓比例与目标比例基本一致，无需调整",
        "macro_data": "近期无重要宏观数据公布",
        "investment_advice": "建议按计划执行定投，保持投资纪律"
    }
    
    success = email_pusher.send_daily_report(report_data)
    if success:
        print("✅ 邮件推送测试成功")
    else:
        print("❌ 邮件推送测试失败")

if __name__ == "__main__":
    test_wechat_push()
    test_email_push()
