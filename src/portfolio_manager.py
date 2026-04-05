# -*- coding: utf-8 -*-
"""
组合管理模块
负责读取持仓配置文件并计算持仓信息
"""

import yaml
import os
from typing import Dict, Any
from .config_manager import config_manager


class PortfolioManager:
    """组合管理类"""
    
    def __init__(self, portfolio_file: str = "config/portfolio.yaml"):
        """
        初始化组合管理
        
        Args:
            portfolio_file: 持仓配置文件路径
        """
        self.portfolio_file = portfolio_file
        self.portfolio: Dict[str, Any] = {}
        self.load_portfolio()
    
    def load_portfolio(self):
        """加载持仓配置文件"""
        try:
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                self.portfolio = yaml.safe_load(f)
            print(f"[OK] 持仓配置文件加载成功: {self.portfolio_file}")
        except Exception as e:
            print(f"[ERROR] 持仓配置文件加载失败: {e}")
            # 使用默认配置
            self._load_default_portfolio()
    
    def _load_default_portfolio(self):
        """加载默认持仓配置"""
        self.portfolio = {
            "total_assets": 100000,
            "positions": {
                "长江电力": {
                    "shares": 1000,
                    "price": 25.8
                },
                "交通银行": {
                    "shares": 2000,
                    "price": 6.8
                },
                "中证红利ETF": {
                    "shares": 3000,
                    "price": 1.25
                },
                "港股红利低波ETF": {
                    "shares": 4000,
                    "price": 1.15
                },
                "标普500ETF南方": {
                    "shares": 1000,
                    "price": 5.8
                }
            }
        }
        print("⚠️ 使用默认持仓配置")
    
    def calculate_portfolio(self) -> Dict[str, Any]:
        """
        计算组合信息
        
        Returns:
            组合信息，包括各标的市值、总资产、持仓比例
        """
        positions = self.portfolio.get("positions", {})
        total_assets = self.portfolio.get("total_assets", 0)
        
        # 计算各标的市值
        market_values = {}
        calculated_total_assets = 0
        
        for stock_name, position in positions.items():
            shares = position.get("shares", 0)
            price = position.get("price", 0)
            market_value = shares * price
            market_values[stock_name] = market_value
            calculated_total_assets += market_value
        
        # 如果没有提供总资产，则使用计算值
        if total_assets == 0:
            total_assets = calculated_total_assets
        
        # 计算持仓比例
        allocations = {}
        for stock_name, market_value in market_values.items():
            if total_assets > 0:
                allocation = (market_value / total_assets) * 100
            else:
                allocation = 0
            allocations[stock_name] = round(allocation, 2)
        
        return {
            "positions": positions,
            "market_values": market_values,
            "total_assets": total_assets,
            "allocations": allocations
        }
    
    def get_current_allocations(self) -> Dict[str, float]:
        """
        获取当前持仓比例
        
        Returns:
            当前持仓比例
        """
        portfolio_info = self.calculate_portfolio()
        return portfolio_info.get("allocations", {})
    
    def get_total_assets(self) -> float:
        """
        获取总资产
        
        Returns:
            总资产
        """
        portfolio_info = self.calculate_portfolio()
        return portfolio_info.get("total_assets", 0)
    
    def get_market_values(self) -> Dict[str, float]:
        """
        获取各标的市值

        Returns:
            各标的市值
        """
        portfolio_info = self.calculate_portfolio()
        return portfolio_info.get("market_values", {})

    def get_positions(self) -> Dict[str, Dict]:
        """
        获取持仓数据

        Returns:
            持仓数据，格式：{标的名称: {"shares": 持有份额, "price": 当前价格}}
        """
        return self.portfolio.get("positions", {})


# 全局组合管理实例
portfolio_manager = PortfolioManager()
