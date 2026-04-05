# -*- coding: utf-8 -*-
"""
交易执行模块
负责根据定投策略生成可直接执行的交易指令
"""

from typing import List, Dict, Any
from decimal import Decimal, ROUND_DOWN


class TradeExecutor:
    """交易执行器"""
    
    def __init__(self):
        """初始化交易执行器"""
        pass
    
    def generate_trade_instructions(self, investment_plan: List[Dict[str, Any]], stock_prices: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        生成交易指令
        
        Args:
            investment_plan: 投资计划列表
            stock_prices: 股票价格字典
        
        Returns:
            交易指令列表
        """
        trade_instructions = []
        
        for item in investment_plan:
            name = item['name']
            suggested_amount = item['suggested_amount']
            
            # 跳过金额为0的标的
            if suggested_amount <= 0:
                continue
            
            # 获取当前价格
            price = stock_prices.get(name, 0)
            if price <= 0:
                continue
            
            # 计算股数（向下取整）
            shares = self._calculate_shares(suggested_amount, price)
            
            # 生成交易指令
            trade_instructions.append({
                "name": name,
                "amount": suggested_amount,
                "shares": shares,
                "price": price
            })
        
        return trade_instructions
    
    def _calculate_shares(self, amount: float, price: float) -> int:
        """
        计算股数（向下取整，且是100的倍数）
        
        Args:
            amount: 买入金额
            price: 当前价格
        
        Returns:
            股数
        """
        if price <= 0:
            return 0
        
        # 使用Decimal进行精确计算，向下取整
        amount_decimal = Decimal(str(amount))
        price_decimal = Decimal(str(price))
        shares_decimal = (amount_decimal / price_decimal).quantize(Decimal('0'), rounding=ROUND_DOWN)
        
        # 确保股数是100的倍数
        shares = int(shares_decimal)
        shares = (shares // 100) * 100
        
        return shares
    
    def format_trade_instructions(self, trade_instructions: List[Dict[str, Any]]) -> str:
        """
        格式化交易指令
        
        Args:
            trade_instructions: 交易指令列表
        
        Returns:
            格式化的交易指令字符串
        """
        if not trade_instructions:
            return "今日无交易建议"
        
        message = "今日交易建议：\n\n"
        
        for instruction in trade_instructions:
            name = instruction['name']
            amount = instruction['amount']
            shares = instruction['shares']
            price = instruction['price']
            
            message += f"* {name}：买入 {amount:.0f}元（约{shares}股，当前价格{price:.2f}元）\n"
        
        return message
    
    def generate_brokerage_clipboard(self, trade_instructions: List[Dict[str, Any]]) -> str:
        """
        生成可复制到券商的操作清单
        
        Args:
            trade_instructions: 交易指令列表
        
        Returns:
            可复制到券商的操作清单字符串
        """
        if not trade_instructions:
            return ""
        
        clipboard = ""
        
        for instruction in trade_instructions:
            name = instruction['name']
            shares = instruction['shares']
            
            clipboard += f"{name}\t买入\t{shares}\n"
        
        return clipboard


# 全局交易执行器实例
trade_executor = TradeExecutor()
