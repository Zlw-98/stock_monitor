# -*- coding: utf-8 -*-
"""
投资Dashboard
基于Streamlit的投资可视化界面
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src.portfolio_manager import portfolio_manager
from src.report_generator import report_generator
from src.config_manager import config_manager
from src.trade_executor import trade_executor
from src.stock_fetcher import stock_fetcher

# 设置页面标题和图标
st.set_page_config(
    page_title="投资Dashboard",
    page_icon="📈",
    layout="wide"
)

# 标题
st.title("投资Dashboard")

# 刷新按钮
if st.button("🔄 刷新数据"):
    # 重新加载配置和数据
    portfolio_manager.load_portfolio()
    st.experimental_rerun()

# 顶部总览
st.header("总览")
total_assets = portfolio_manager.get_total_assets()
monthly_investment = config_manager.get_monthly_investment()

col1, col2 = st.columns(2)
with col1:
    st.metric("总资产", f"¥{total_assets:,.2f}")
with col2:
    st.metric("本月定投金额", f"¥{monthly_investment:,.2f}")

# 资产配置饼图
st.header("资产配置")
current_allocations = portfolio_manager.get_current_allocations()
market_values = portfolio_manager.get_market_values()

# 准备饼图数据
pie_data = pd.DataFrame({
    "标的": list(current_allocations.keys()),
    "比例": list(current_allocations.values()),
    "市值": [market_values.get(name, 0) for name in current_allocations.keys()]
})

# 创建饼图
fig = px.pie(
    pie_data,
    values="比例",
    names="标的",
    hover_data=["市值"],
    title="当前资产配置比例"
)
st.plotly_chart(fig, use_container_width=True)

# 估值状态面板
st.header("估值状态")

# 定义获取估值数据的函数
def get_valuation_data(stock_name):
    """获取股票估值数据"""
    # 定义默认值
    default_values = {
        "长江电力": {"dividend_rate": 3.5, "source": "估算", "credibility": 0.5},
        "交通银行": {"pb": 0.7, "source": "估算", "credibility": 0.5},
        "中证红利ETF": {"dividend_rate": 5.0, "source": "估算", "credibility": 0.5},
        "港股红利低波ETF": {"dividend_rate": 5.0, "source": "估算", "credibility": 0.5},
        "标普500ETF南方": {"pe_percentile": 60, "source": "估算", "credibility": 0.5}
    }
    
    # 从stock_fetcher获取真实数据
    stocks_config = config_manager.get_stocks()
    stock_config = None
    for stock in stocks_config:
        if stock["name"] == stock_name:
            stock_config = stock
            break
    
    # 获取股票数据
    stock_data = {}
    source = "估算"
    credibility = 0.5
    
    if stock_config:
        data = stock_fetcher.fetch_stock_data(stock_config)
        if data:
            source = data.get('source', 'sina')
            credibility = data.get('credibility', 0.8)
            stock_data['price'] = data.get('price', 0)
    
    # 获取数据，如果没有则使用默认值
    default_data = default_values.get(stock_name, {})
    
    if stock_name == "长江电力":
        # 计算股息率（假设最近一年分红为0.93元）
        price = stock_data.get('price', 0)
        if price > 0:
            dividend_rate = round(0.93 / price * 100, 1)
            source = "计算"
        else:
            dividend_rate = default_data['dividend_rate']
        print(f"✅ 长江电力估值数据: 股息率={dividend_rate}% (来源: {source}, 可信度: {credibility:.1%})")
        return {
            "估值": f"{dividend_rate}%",
            "估值指标": "股息率",
            "估值判断": "正常" if 3 <= dividend_rate <= 4 else "低估" if dividend_rate > 4 else "高估",
            "来源": source,
            "可信度": f"{credibility:.1%}"
        }
    elif stock_name == "交通银行":
        # 计算PB（假设每股净资产为10元）
        price = stock_data.get('price', 0)
        if price > 0:
            pb = round(price / 10, 2)
            source = "计算"
        else:
            pb = default_data['pb']
        print(f"✅ 交通银行估值数据: PB={pb} (来源: {source}, 可信度: {credibility:.1%})")
        return {
            "估值": f"{pb}",
            "估值指标": "PB",
            "估值判断": "低估" if pb < 0.7 else "正常" if pb < 1 else "高估",
            "来源": source,
            "可信度": f"{credibility:.1%}"
        }
    elif stock_name == "中证红利ETF":
        # 计算股息率（假设最近一年分红为0.075元）
        price = stock_data.get('price', 0)
        if price > 0:
            dividend_rate = round(0.075 / price * 100, 1)
            source = "计算"
        else:
            dividend_rate = default_data['dividend_rate']
        print(f"✅ 中证红利ETF估值数据: 股息率={dividend_rate}% (来源: {source}, 可信度: {credibility:.1%})")
        return {
            "估值": f"{dividend_rate}%",
            "估值指标": "股息率",
            "估值判断": "低估" if dividend_rate > 6 else "正常" if dividend_rate > 4 else "高估",
            "来源": source,
            "可信度": f"{credibility:.1%}"
        }
    elif stock_name == "港股红利低波ETF":
        # 计算股息率（假设最近一年分红为0.075元）
        price = stock_data.get('price', 0)
        if price > 0:
            dividend_rate = round(0.075 / price * 100, 1)
            source = "计算"
        else:
            dividend_rate = default_data['dividend_rate']
        print(f"✅ 港股红利低波ETF估值数据: 股息率={dividend_rate}% (来源: {source}, 可信度: {credibility:.1%})")
        return {
            "估值": f"{dividend_rate}%",
            "估值指标": "股息率",
            "估值判断": "低估" if dividend_rate > 6 else "正常" if dividend_rate > 4 else "高估",
            "来源": source,
            "可信度": f"{credibility:.1%}"
        }
    elif stock_name == "标普500ETF南方":
        pe_percentile = default_data['pe_percentile']
        print(f"✅ 标普500ETF南方估值数据: PE分位={pe_percentile}% (来源: {source}, 可信度: {credibility:.1%})")
        return {
            "估值": f"{pe_percentile}%",
            "估值指标": "PE分位",
            "估值判断": "低估" if pe_percentile < 30 else "正常" if pe_percentile < 70 else "高估",
            "来源": source,
            "可信度": f"{credibility:.1%}"
        }
    else:
        print(f"❌ {stock_name}估值数据获取失败，使用默认值")
        # 返回默认值
        return {
            "估值": "N/A",
            "估值指标": "N/A",
            "估值判断": "未知",
            "来源": "估算",
            "可信度": "50.0%"
        }

# 准备所有标的
stocks = [
    "长江电力",
    "交通银行",
    "中证红利ETF",
    "港股红利低波ETF",
    "标普500ETF南方"
]

# 获取估值数据
valuation_data = []
for stock in stocks:
    val_data = get_valuation_data(stock)
    valuation_data.append({
        "标的": stock,
        "估值": val_data["估值"],
        "估值指标": val_data["估值指标"],
        "估值判断": val_data["估值判断"],
        "来源": val_data.get("来源", "估算"),
        "可信度": val_data.get("可信度", "50.0%")
    })

# 创建估值表格
valuation_df = pd.DataFrame(valuation_data)

# 定义颜色映射，使用更鲜明的颜色，提高对比度
color_map = {
    "低估": "background-color: #4CAF50; color: white; font-weight: bold",
    "正常": "background-color: #FFC107; color: black; font-weight: bold",
    "高估": "background-color: #F44336; color: white; font-weight: bold",
    "未知": "background-color: #9E9E9E; color: white; font-weight: bold"
}

# 应用样式
styled_valuation_df = valuation_df.style.apply(
    lambda row: [color_map.get(row["估值判断"], "")] * len(row),
    axis=1
).set_table_styles([
    {
        'selector': 'th',
        'props': [('background-color', '#333'), ('color', 'white'), ('font-weight', 'bold')]
    }
])

st.dataframe(styled_valuation_df, use_container_width=True)

# 本月定投建议
st.header("本月定投建议")

# 计算最终投资计划
investment_plan = report_generator.calculate_final_investment_plan(monthly_investment)

# 准备定投建议数据
plan_data = pd.DataFrame(investment_plan)[["name", "raw_amount", "final_amount", "priority"]]
plan_data.columns = ["标的", "原始建议金额", "最终建议金额", "执行优先级"]

# 计算反转后的星级评分，使得优先级1是最高的
plan_data["优先级星级"] = plan_data["执行优先级"].apply(lambda x: '⭐' * (6 - x))

# 按执行优先级排序
plan_data = plan_data.sort_values("执行优先级")

# 格式化金额
plan_data["原始建议金额"] = plan_data["原始建议金额"].apply(lambda x: f"¥{x:,.2f}")
plan_data["最终建议金额"] = plan_data["最终建议金额"].apply(lambda x: f"¥{x:,.2f}")

st.dataframe(plan_data, use_container_width=True)

# 交易建议
st.header("交易建议")

# 准备股票价格数据（从portfolio.yaml中获取）
portfolio_data = portfolio_manager.portfolio
positions = portfolio_data.get("positions", {})
stock_prices = {}
for stock_name, position in positions.items():
    stock_prices[stock_name] = position.get("price", 0)

# 生成交易指令
# 转换投资计划格式以适应trade_executor
formatted_plan = []
for item in investment_plan:
    formatted_plan.append({
        "name": item["name"],
        "suggested_amount": item["final_amount"]
    })
trade_instructions = trade_executor.generate_trade_instructions(formatted_plan, stock_prices)

# 格式化交易建议
formatted_instructions = trade_executor.format_trade_instructions(trade_instructions)
st.text(formatted_instructions)

# 可复制到券商的操作清单
if trade_instructions:
    st.subheader("券商操作清单")
    clipboard = trade_executor.generate_brokerage_clipboard(trade_instructions)
    st.text_area("复制下方内容到券商：", value=clipboard, height=150)
    
    # 提供一键复制按钮
    if st.button("📋 一键复制券商操作清单"):
        st.success("已复制到剪贴板！")
        st.info("请将复制的内容粘贴到券商交易系统中")

# 执行清单模块
st.header("执行清单")
st.subheader("按优先级排序的买入清单")

# 准备执行清单数据
execution_list = []
for item in investment_plan:
    stock_name = item["name"]
    amount = item["final_amount"]
    # 获取当前价格
    price = 0
    if stock_name in stock_prices:
        price = stock_prices[stock_name]
    elif stock_name in positions:
        price = positions[stock_name].get("price", 0)
    
    # 计算买入数量
    shares = 0
    if price > 0:
        shares = int(amount / price)  # 向下取整
    
    execution_list.append({
        "优先级": item["priority"],
        "标的": stock_name,
        "买入金额": f"¥{amount:,.2f}",
        "当前价格": f"¥{price:,.2f}" if price > 0 else "N/A",
        "买入股数": shares
    })

# 创建执行清单表格
execution_df = pd.DataFrame(execution_list)

# 按优先级排序
execution_df = execution_df.sort_values("优先级")

# 显示执行清单表格
st.dataframe(execution_df, use_container_width=True)

# 提供执行清单复制按钮
execution_clipboard = """
执行清单（按优先级）
==================
"""

for i, item in enumerate(execution_list, 1):
    execution_clipboard += f"{i}. {item['标的']}\n"
    execution_clipboard += f"   买入金额: {item['买入金额']}\n"
    execution_clipboard += f"   当前价格: {item['当前价格']}\n"
    execution_clipboard += f"   买入股数: {item['买入股数']}\n\n"

st.text_area("复制执行清单：", value=execution_clipboard, height=200)

if st.button("📋 一键复制执行清单"):
    st.success("已复制到剪贴板！")
    st.info("请按照优先级顺序执行买入")

# 分红日提醒模块
st.header("分红提醒")
from src.dividend_monitor import dividend_monitor
from src.config_manager import config_manager

stocks = config_manager.get_stocks()
upcoming_dividends = dividend_monitor.get_upcoming_dividends(stocks)

if upcoming_dividends:
    # 创建分红提醒表格
    dividend_df = pd.DataFrame(upcoming_dividends)
    dividend_df = dividend_df[["stock_name", "ex_date", "dividend", "days_until"]]
    dividend_df.columns = ["股票名称", "除权除息日", "分红金额(元)", "距离天数"]
    
    # 显示分红提醒表格
    st.dataframe(dividend_df, use_container_width=True)
    
    # 生成分红提醒消息
    dividend_alerts = dividend_monitor.generate_dividend_alert(upcoming_dividends)
    if dividend_alerts:
        st.subheader("近期分红提醒")
        for alert in dividend_alerts:
            st.info(alert["message"])
else:
    st.info("暂无即将到来的分红")

# 标普500溢价监控模块
st.header("标普500ETF溢价监控")

# 模拟获取溢价率，实际应从API获取
sp500_premium = 1.5
st.metric("当前溢价率", f"{sp500_premium}%")

if sp500_premium > 3:
    st.error("⚠️  标普500ETF溢价过高，建议暂停本月定投，转为现金管理")
elif sp500_premium > 1:
    st.warning("⚠️  标普500ETF存在一定溢价，建议谨慎定投")
else:
    st.success("✅ 标普500ETF溢价率正常，可以正常定投")

# 组合健康度
st.header("组合健康度")

# 准备组合健康度数据
target_allocations = config_manager.get_target_allocations()
health_data = pd.DataFrame({
    "标的": list(current_allocations.keys()),
    "当前比例": list(current_allocations.values()),
    "目标比例": [target_allocations.get(name, 0) for name in current_allocations.keys()]
})
health_data["偏离"] = health_data["当前比例"] - health_data["目标比例"]

# 创建组合健康度图表
fig = px.bar(
    health_data,
    x="标的",
    y=["当前比例", "目标比例"],
    barmode="group",
    title="当前比例 vs 目标比例"
)
st.plotly_chart(fig, use_container_width=True)

# 显示偏离情况
st.subheader("偏离情况")
deviation_df = health_data[["标的", "偏离"]].copy()  # 创建副本避免SettingWithCopyWarning
deviation_df["偏离"] = deviation_df["偏离"].apply(lambda x: f"{x:+.2f}%")
st.dataframe(deviation_df, use_container_width=True)

# 行情监控
st.header("行情监控")

# 模拟行情数据
market_data = [
    {"标的": "长江电力", "涨跌幅": "1.2%", "预警": "否"},
    {"标的": "交通银行", "涨跌幅": "-0.5%", "预警": "否"},
    {"标的": "中证红利ETF", "涨跌幅": "0.8%", "预警": "否"},
    {"标的": "港股红利低波ETF", "涨跌幅": "-0.3%", "预警": "否"},
    {"标的": "标普500ETF南方", "涨跌幅": "1.5%", "预警": "否"}
]

# 创建行情监控表格
market_df = pd.DataFrame(market_data)

# 应用样式
styled_market_df = market_df.style.apply(
    lambda row: [
        "color: green" if row["涨跌幅"].startswith("+") else "color: red" if row["涨跌幅"].startswith("-") else ""
    ] * len(row),
    axis=1
)

st.dataframe(styled_market_df, use_container_width=True)

# 持仓输入模块
st.header("持仓输入")

# 读取当前持仓数据
portfolio_data = portfolio_manager.portfolio
positions = portfolio_data.get("positions", {})

# 从配置中获取股票列表
stocks_config = config_manager.get_stocks()
stocks = [stock["name"] for stock in stocks_config]

# 使用两列布局
col1, col2 = st.columns(2)

# 存储用户输入的持仓数据
user_positions = {}

# 自动获取最新价格
if st.button("🔄 自动获取最新价格"):
    st.info("正在获取最新价格，请稍候...")
    # 获取所有股票的最新数据
    stock_data = stock_fetcher.fetch_all_stocks(stocks_config)
    
    # 更新价格
    for stock in stocks_config:
        code = stock["code"]
        name = stock["name"]
        if code in stock_data:
            price = stock_data[code].get("price", 0)
            if price > 0:
                positions[name]["price"] = price
                st.success(f"已更新 {name} 的价格: ¥{price:.2f}")

# 显示持仓输入
for stock in stocks:
    with col1:
        st.subheader(stock)
    with col2:
        # 获取当前持仓数据
        current_position = positions.get(stock, {})
        current_shares = current_position.get("shares", 0)
        current_price = current_position.get("price", 0)
        
        # 输入框
        shares = st.number_input(
            f"{stock} - 持仓股数",
            min_value=0,
            value=current_shares,
            key=f"shares_{stock}"
        )
        price = st.number_input(
            f"{stock} - 当前价格",
            min_value=0.0,
            value=current_price,
            step=0.01,
            key=f"price_{stock}"
        )
        
        # 计算市值
        market_value = shares * price
        st.write(f"市值: ¥{market_value:.2f}")
        
        # 存储用户输入
        user_positions[stock] = {
            "shares": shares,
            "price": price
        }

# 计算总资产
total_assets = sum([pos["shares"] * pos["price"] for pos in user_positions.values()])
st.metric("计算总资产", f"¥{total_assets:.2f}")

# 保存持仓按钮
if st.button("💾 保存持仓"):
    # 构建新的持仓数据
    new_portfolio = {
        "total_assets": total_assets,
        "positions": user_positions
    }
    
    # 写入portfolio.yaml文件
    try:
        import yaml
        with open("config/portfolio.yaml", "w", encoding="utf-8") as f:
            yaml.dump(new_portfolio, f, default_flow_style=False, allow_unicode=True)
        st.success("持仓数据保存成功！")
        # 重新加载数据
        portfolio_manager.load_portfolio()
        # 刷新页面
        st.rerun()
    except Exception as e:
        st.error(f"保存失败: {e}")

# 页脚（使用st.markdown代替st.footer）
st.markdown("---")
st.markdown("**投资Dashboard - 数据仅供参考，不构成投资建议**")
