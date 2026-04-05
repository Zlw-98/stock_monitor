# -*- coding: utf-8 -*-
"""
报告生成模块
负责生成定投决策报告
"""

from datetime import datetime
from typing import Dict, List, Any
from .config_manager import config_manager
from .portfolio_manager import portfolio_manager


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        """初始化报告生成器"""
        self.stocks = config_manager.get_stocks()
        self.target_allocations = config_manager.get_target_allocations()
        # 使用组合管理模块获取当前持仓比例
        self.current_allocations = portfolio_manager.get_current_allocations()
        # 获取总资产
        self.total_assets = portfolio_manager.get_total_assets()
        # 获取各标的市值
        self.market_values = portfolio_manager.get_market_values()
    

    def _get_confidence_factor(self, credibility: float) -> float:
        """Map credibility to confidence factor."""
        if credibility >= 0.8:
            return 1.0
        if credibility >= 0.6:
            return 0.8
        if credibility >= 0.4:
            return 0.7
        return 0.5

    def generate_daily_report(self, report_data: Dict[str, Any]) -> str:
        """
        生成每日定投决策报告
        
        Args:
            report_data: 报告数据
        
        Returns:
            报告内容
        """
        # 填充数据
        date = datetime.now().strftime('%Y-%m-%d')
        sh_index_change = report_data.get('sh_index_change', 0)
        hk_index_change = report_data.get('hk_index_change', 0)
        us_index_change = report_data.get('us_index_change', 0)
        
        # 构建估值分析部分
        valuation_analysis = self._build_valuation_analysis(report_data.get('stocks', []))
        
        # 构建定投建议部分
        investment_plan = self._build_investment_plan()
        
        # 构建组合健康度部分
        portfolio_health = self._build_portfolio_health()
        
        # 构建操作总结
        operation_summary = self._build_operation_summary(report_data.get('stocks', []))
        
        # 构建分红提醒部分
        from src.dividend_monitor import dividend_monitor
        from src.config_manager import config_manager
        stocks = config_manager.get_stocks()
        upcoming_dividends = dividend_monitor.get_upcoming_dividends(stocks)
        # 传递持仓数据用于计算实际分红
        positions = portfolio_manager.get_positions()
        dividend_report = dividend_monitor.generate_dividend_report(upcoming_dividends, positions)
        
        # Build backtest vs live comparison
        backtest_live_comparison = self._build_backtest_live_comparison()

        # 构建宏观影响评估
        macro_impact = self._build_macro_impact()

        # 构建纯文本邮件内容
        body = f"""
股票监控日报
日期: {date}

一、市场概览
指数		涨跌幅
上证指数	{sh_index_change}%
恒生指数	{hk_index_change}%
标普500指数	{us_index_change}%

二、估值分析
{valuation_analysis}

三、本月定投建议
{investment_plan}

四、组合健康度
{portfolio_health}

五、分红提醒
{dividend_report}

六、操作总结
{operation_summary}

七、宏观影响评估
{macro_impact}

7. Backtest vs Live
{backtest_live_comparison}


本报告仅供参考，不构成投资建议。
        """
        
        return body
    
    def _build_valuation_analysis(self, stocks: List[Dict[str, Any]]) -> str:
        """
        构建估值分析部分
        
        Args:
            stocks: 股票数据列表
        
        Returns:
            估值分析内容
        """
        # 定义默认值
        default_values = {
            "长江电力": {"dividend_rate": 3.5, "source": "估算"},
            "交通银行": {"pb": 0.7, "source": "估算"},
            "中证红利ETF": {"dividend_rate": 5.0, "source": "估算"},
            "港股红利低波ETF": {"dividend_rate": 5.0, "source": "估算"},
            "标普500ETF南方": {"pe_percentile": 60, "source": "估算"}
        }
        
        analysis = ''
        for stock in stocks:
            stock_name = stock['name']
            analysis += f"\n{stock_name} ({stock['code']}):\n"
            analysis += f"  当前价格: {stock['price']}元\n"
            analysis += f"  涨跌幅: {stock['change_percent']}%\n"
            
            # 根据股票类型分析估值
            if stock_name == '标普500ETF南方':
                pe_percentile = stock.get('pe_percentile', default_values[stock_name]['pe_percentile'])
                source = stock.get('source', default_values[stock_name]['source'])
                credibility = stock.get('credibility', 0.5)
                analysis += f"  PE分位: {pe_percentile}% (来源: {source}, 可信度: {credibility:.1%})\n"
                if pe_percentile < 30:
                    analysis += "  估值判断: 低估\n"
                elif pe_percentile < 70:
                    analysis += "  估值判断: 正常\n"
                else:
                    analysis += "  估值判断: 偏高\n"
            elif stock_name in ['中证红利ETF', '港股红利低波ETF']:
                # 计算股息率（假设最近一年分红为0.075元）
                price = stock.get('price', 0)
                if price > 0:
                    dividend_rate = round(0.075 / price * 100, 1)
                    source = "计算"
                else:
                    dividend_rate = default_values[stock_name]['dividend_rate']
                    source = default_values[stock_name]['source']
                credibility = stock.get('credibility', 0.5)
                analysis += f"  股息率: {dividend_rate}% (来源: {source}, 可信度: {credibility:.1%})\n"
                if dividend_rate > 6:
                    analysis += "  估值判断: 低估\n"
                elif dividend_rate > 4:
                    analysis += "  估值判断: 正常\n"
                else:
                    analysis += "  估值判断: 偏高\n"
            elif stock_name == '长江电力':
                # 计算股息率（假设最近一年分红为0.93元）
                price = stock.get('price', 0)
                if price > 0:
                    dividend_rate = round(0.93 / price * 100, 1)
                    source = "计算"
                else:
                    dividend_rate = default_values[stock_name]['dividend_rate']
                    source = default_values[stock_name]['source']
                credibility = stock.get('credibility', 0.5)
                analysis += f"  股息率: {dividend_rate}% (来源: {source}, 可信度: {credibility:.1%})\n"
                if dividend_rate > 4:
                    analysis += "  估值判断: 低估\n"
                elif dividend_rate > 3:
                    analysis += "  估值判断: 正常\n"
                else:
                    analysis += "  估值判断: 偏高\n"
            elif stock_name == '交通银行':
                # 计算PB（假设每股净资产为10元）
                price = stock.get('price', 0)
                if price > 0:
                    pb = round(price / 10, 2)
                    source = "计算"
                else:
                    pb = default_values[stock_name]['pb']
                    source = default_values[stock_name]['source']
                credibility = stock.get('credibility', 0.5)
                analysis += f"  市净率(PB): {pb} (来源: {source}, 可信度: {credibility:.1%})\n"
                if pb < 0.7:
                    analysis += "  估值判断: 低估\n"
                elif pb < 1:
                    analysis += "  估值判断: 正常\n"
                else:
                    analysis += "  估值判断: 偏高\n"
        
        return analysis
    
    def _build_investment_plan(self) -> str:
        """
        构建最终定投方案
        
        Returns:
            最终定投方案内容
        """
        # 从配置文件获取每月定投金额
        total_amount = config_manager.get_monthly_investment()
        
        # 计算最终投资计划
        investment_plan = self.calculate_final_investment_plan(total_amount)
        
        # 构建表格
        plan_table = "\n最终执行定投方案\n"
        plan_table += "-" * 120 + "\n"
        plan_table += "标的\t原始金额\t调整后金额\t可信度因子\t数据来源\t可信度\t执行优先级\n"
        plan_table += "-" * 120 + "\n"
        
        for item in investment_plan:
            source = item.get('source', '估算')
            credibility = item.get('credibility', 0.5)
            # 反转星级评分，使得优先级1是最高的
            reversed_stars = '⭐' * (6 - item['priority'])
            plan_table += f"{item['name']}\t{item['raw_amount']}元\t{item['final_amount']}元\t{item['confidence_factor']}\t{source}\t{credibility:.1%}\t{reversed_stars}\n"
        
        plan_table += f"\n总投资金额: {total_amount}元\n"
        
        return plan_table
    
    def calculate_final_investment_plan(self, total_amount: float) -> List[Dict[str, Any]]:
        """
        计算最终定投方案（考虑估值和再平衡）
        
        Args:
            total_amount: 每月定投金额
        
        Returns:
            最终投资计划列表
        """
        # Step 1: 基础权重 - 使用配置文件中的目标比例作为基础
        base_allocations = {
            "长江电力": 15,
            "交通银行": 15,
            "中证红利ETF": 18,
            "港股红利低波ETF": 12,
            "标普500ETF南方": 40
        }
        
        # 定义默认值
        default_values = {
            "长江电力": {"dividend_rate": 3.5, "source": "估算"},
            "交通银行": {"pb": 0.7, "source": "估算"},
            "中证红利ETF": {"dividend_rate": 5.0, "source": "估算"},
            "港股红利低波ETF": {"dividend_rate": 5.0, "source": "估算"},
            "标普500ETF南方": {"pe_percentile": 60, "source": "估算"}
        }
        
        # 从stock_fetcher获取真实的股票数据
        from src.stock_fetcher import stock_fetcher
        from src.config_manager import config_manager
        
        stocks_config = config_manager.get_stocks()
        stock_data_map = {}
        
        for stock_config in stocks_config:
            code = stock_config['code']
            data = stock_fetcher.fetch_stock_data(stock_config)
            if data:
                stock_data_map[stock_config['name']] = data
        
        # 检查标普500ETF溢价情况
        sp500_premium = 0
        if '标普500ETF南方' in stock_data_map:
            # 这里模拟获取溢价率，实际应从API获取
            # 假设当前溢价率为1.5%
            sp500_premium = 1.5
            print(f"[WARNING] 标普500ETF南方 溢价率: {sp500_premium}%")
            if sp500_premium > 3:
                print("[WARNING] 标普500ETF溢价过高，建议暂停本月定投，转为现金管理")
        
        # 动态平衡触发开关
        need_rebalance = False
        for stock_name, current_ratio in self.current_allocations.items():
            target_ratio = self.target_allocations.get(stock_name, 0)
            deviation = abs(current_ratio - target_ratio)
            if deviation > 3:
                need_rebalance = True
                break
        
        if not need_rebalance:
            print("[OK] 当前比例与目标比例偏差小于3%，按常规比例定投")
            # 按基础比例分配
            adjusted_weights = base_allocations.copy()
            sources = {stock: "基础" for stock in base_allocations}
            credibilities = {stock: 0.8 for stock in base_allocations}
        else:
            print("[WARNING] 当前比例与目标比例偏差大于3%，需要进行再平衡")
            
            # Step 2: 估值调整
            adjusted_weights = {}
            sources = {}
            credibilities = {}
            
            for stock_name, base_ratio in base_allocations.items():
                # 获取股票数据
                stock_data = stock_data_map.get(stock_name, {})
                price = stock_data.get('price', 0)
                
                # 计算估值数据
                if stock_name == '长江电力':
                    # 计算股息率（假设最近一年分红为0.93元）
                    if price > 0:
                        dividend_rate = round(0.93 / price * 100, 1)
                        source = "计算"
                    else:
                        dividend_rate = default_values[stock_name]['dividend_rate']
                        source = default_values[stock_name]['source']
                    pe_percentile = None
                    pb = None
                elif stock_name == '交通银行':
                    # 计算PB（假设每股净资产为10元）
                    if price > 0:
                        pb = round(price / 10, 2)
                        source = "计算"
                    else:
                        pb = default_values[stock_name]['pb']
                        source = default_values[stock_name]['source']
                    dividend_rate = None
                    pe_percentile = None
                elif stock_name in ['中证红利ETF', '港股红利低波ETF']:
                    # 计算股息率（假设最近一年分红为0.075元）
                    if price > 0:
                        dividend_rate = round(0.075 / price * 100, 1)
                        source = "计算"
                    else:
                        dividend_rate = default_values[stock_name]['dividend_rate']
                        source = default_values[stock_name]['source']
                    pe_percentile = None
                    pb = None
                elif stock_name == '标普500ETF南方':
                    pe_percentile = default_values[stock_name]['pe_percentile']
                    source = default_values[stock_name]['source']
                    dividend_rate = None
                    pb = None
                
                sources[stock_name] = source
                
                # 获取可信度评分
                credibility = stock_data.get('credibility', 0.5)
                credibilities[stock_name] = credibility
                
                # 计算调整系数
                adjustment_factor = 1.0
                
                if stock_name == '标普500ETF南方':
                    print(f"[INFO] {stock_name} PE分位: {pe_percentile}% (来源: {source}, 可信度: {credibility:.1%})")
                    if pe_percentile > 70:
                        adjustment_factor = 0.5
                    elif pe_percentile < 30:
                        adjustment_factor = 1.5
                    # 如果溢价过高，进一步降低权重
                    if sp500_premium > 3:
                        adjustment_factor *= 0.5
                        print(f"[WARNING] 标普500ETF溢价过高，进一步降低权重")
                elif stock_name in ['中证红利ETF', '港股红利低波ETF']:
                    print(f"[INFO] {stock_name} 股息率: {dividend_rate}% (来源: {source}, 可信度: {credibility:.1%})")
                    if dividend_rate > 6:
                        adjustment_factor = 1.5
                    elif dividend_rate < 4:
                        adjustment_factor = 0.5
                elif stock_name == '长江电力':
                    print(f"[INFO] {stock_name} 股息率: {dividend_rate}% (来源: {source}, 可信度: {credibility:.1%})")
                    if dividend_rate > 4:
                        adjustment_factor = 1.2
                    elif dividend_rate < 3:
                        adjustment_factor = 0.5
                elif stock_name == '交通银行':
                    print(f"[INFO] {stock_name} PB: {pb} (来源: {source}, 可信度: {credibility:.1%})")
                    if pb < 0.7:
                        adjustment_factor = 1.5
                    elif pb > 1:
                        adjustment_factor = 0.5
                
                # 根据可信度调整调整系数（高可信度保留完整信号）
                confidence_factor = self._get_confidence_factor(credibility)
                adjustment_factor = 1.0 + (adjustment_factor - 1.0) * confidence_factor
                if confidence_factor < 1.0:
                    print(
                        f"[WARNING] {stock_name} 可信度 {credibility:.1%}，"
                        f"估值偏离影响按 {confidence_factor:.1f} 缩放"
                    )
                
                # 计算调整后的权重
                adjusted_weights[stock_name] = base_ratio * adjustment_factor
            
            # Step 3: 再平衡修正（优先级最高）
            for stock_name, current_ratio in self.current_allocations.items():
                target_ratio = self.target_allocations.get(stock_name, 0)
                deviation = current_ratio - target_ratio
                
                if stock_name in adjusted_weights:
                    if deviation > 10:  # 超配 > 10%
                        # 减少或暂停
                        adjusted_weights[stock_name] *= 0.5
                        print(f"[WARNING] {stock_name} 超配 {deviation:.1f}%，减少权重")
                    elif deviation < -10:  # 低配 < -10%
                        # 增加权重
                        adjusted_weights[stock_name] *= 1.5
                        print(f"[WARNING] {stock_name} 低配 {deviation:.1f}%，增加权重")
        
        # Step 4: 归一化
        total_weight = sum(adjusted_weights.values())
        raw_amounts = {}
        final_amounts = {}
        confidence_factors = {}
        
        for stock_name, weight in adjusted_weights.items():
            # 计算原始建议金额
            raw_amount = total_amount * (weight / total_weight)
            raw_amounts[stock_name] = raw_amount
            
            # 获取可信度因子
            credibility = credibilities.get(stock_name, 0.5)
            confidence_factor = self._get_confidence_factor(credibility)
            confidence_factors[stock_name] = confidence_factor
            
            # 计算调整后金额
            adjusted_amount = raw_amount * confidence_factor
            final_amounts[stock_name] = adjusted_amount
            
            print(f"[INFO] {stock_name} 原始金额: {raw_amount:.2f}元, 可信度因子: {confidence_factor}, 调整后金额: {adjusted_amount:.2f}元")
        
        # 计算执行优先级 - 基于资金流入方向
        # 按建议金额降序排序，金额越大优先级越高
        # 确保加仓的资产（标普500ETF、港股红利低波ETF）优先级更高
        sorted_stocks = sorted(final_amounts.keys(), key=lambda x: final_amounts[x], reverse=True)
        
        # 手动调整顺序，确保标普500ETF和港股红利低波ETF排在前面
        # 因为它们是需要重点加仓的资产
        prioritized_stocks = []
        for stock in ['标普500ETF南方', '港股红利低波ETF', '交通银行', '长江电力', '中证红利ETF']:
            if stock in sorted_stocks:
                prioritized_stocks.append(stock)
        
        # 如果有其他股票，添加到后面
        for stock in sorted_stocks:
            if stock not in prioritized_stocks:
                prioritized_stocks.append(stock)
        
        sorted_stocks = prioritized_stocks
        
        # 构建最终投资计划
        investment_plan = []
        for i, stock_name in enumerate(sorted_stocks, 1):
            source = sources.get(stock_name, '估算')
            credibility = credibilities.get(stock_name, 0.5)
            raw_amount = raw_amounts.get(stock_name, 0)
            final_amount = final_amounts.get(stock_name, 0)
            confidence_factor = confidence_factors.get(stock_name, 0.5)
            priority = i
            
            # 生成星级评分
            stars = '⭐' * min(priority, 5)
            
            investment_plan.append({
                "name": stock_name,
                "raw_amount": round(raw_amount, 2),
                "final_amount": round(final_amount, 2),
                "confidence_factor": confidence_factor,
                "source": source,
                "credibility": credibility,
                "priority": priority,
                "stars": stars
            })
        
        return investment_plan
    
    def _build_rebalance_suggestion(self) -> str:
        """
        生成再平衡执行建议
        
        Returns:
            再平衡执行建议内容
        """
        # 计算偏离情况
        deviations = {}
        rebalance_needed = False
        
        for stock_name, current_ratio in self.current_allocations.items():
            target_ratio = self.target_allocations.get(stock_name, 0)
            deviation = current_ratio - target_ratio
            deviations[stock_name] = deviation
            if abs(deviation) > 5:
                rebalance_needed = True
        
        if not rebalance_needed:
            return "当前组合状态良好，无需再平衡操作。"
        
        # 按偏离程度排序
        sorted_deviations = sorted(deviations.items(), key=lambda x: abs(x[1]), reverse=True)
        
        # 生成偏离报告
        suggestion = "当前偏离：\n"
        for stock_name, deviation in sorted_deviations:
            if abs(deviation) > 1:
                suggestion += f"* {stock_name}：{deviation:+.1f}%\n"
        
        suggestion += "\n👉 建议操作：\n"
        suggestion += "未来3个月定投：\n"
        
        # 计算建议定投金额
        monthly_investment = config_manager.get_monthly_investment()
        base_amount = monthly_investment / len(self.current_allocations)
        
        # 调整定投金额
        for stock_name, deviation in sorted_deviations:
            if deviation < -5:  # 低于目标比例
                adjusted_amount = base_amount * 2
                suggestion += f"* {stock_name}：提高至 {adjusted_amount:.0f}/月\n"
            elif deviation > 5:  # 高于目标比例
                suggestion += f"* 暂停：{stock_name}\n"
            else:  # 基本符合目标比例
                suggestion += f"* {stock_name}：{base_amount:.0f}/月\n"
        
        return suggestion
    
    def _build_portfolio_health(self) -> str:
        """
        构建组合健康度部分
        
        Returns:
            组合健康度内容
        """
        health = f"\n总资产: {self.total_assets:.2f}元\n"
        health += "\n各标的市值与持仓比例:\n"
        health += "-" * 80 + "\n"
        health += "标的\t市值\t当前比例\t目标比例\t偏离\t状态\n"
        health += "-" * 80 + "\n"
        
        rebalance_needed = False
        
        for stock_name, current_ratio in self.current_allocations.items():
            target_ratio = self.target_allocations.get(stock_name, 0)
            deviation = current_ratio - target_ratio
            market_value = self.market_values.get(stock_name, 0)
            
            status = "正常"
            if abs(deviation) > 5:
                status = "需要调整"
                rebalance_needed = True
            
            health += f"{stock_name}\t{market_value:.2f}元\t{current_ratio}%\t{target_ratio}%\t{deviation:+.2f}%\t{status}\n"
        
        health += "\n"
        if rebalance_needed:
            health += "[WARNING] 组合偏离较大，再平衡已在最终定投方案中考虑\n"
        else:
            health += "[OK] 组合状态良好\n"
        
        return health
    
    def _build_operation_summary(self, stocks: List[Dict[str, Any]]) -> str:
        """
        构建操作总结
        
        Args:
            stocks: 股票数据列表
        
        Returns:
            操作总结内容
        """
        # 分析组合偏离情况
        over_allocated = []
        under_allocated = []
        normal_allocated = []
        
        for stock_name, current_ratio in self.current_allocations.items():
            target_ratio = self.target_allocations.get(stock_name, 0)
            deviation = current_ratio - target_ratio
            if deviation > 10:
                over_allocated.append(stock_name)
            elif deviation < -10:
                under_allocated.append(stock_name)
            else:
                normal_allocated.append(stock_name)
        
        # 分析估值情况
        undervalued = []
        normal_valued = []
        overvalued = []
        
        # 定义默认值
        default_values = {
            "长江电力": {"dividend_rate": 3.5, "source": "估算"},
            "交通银行": {"pb": 0.7, "source": "估算"},
            "中证红利ETF": {"dividend_rate": 5.0, "source": "估算"},
            "港股红利低波ETF": {"dividend_rate": 5.0, "source": "估算"},
            "标普500ETF南方": {"pe_percentile": 60, "source": "估算"}
        }
        
        for stock in stocks:
            stock_name = stock['name']
            if stock_name == '标普500ETF南方':
                pe_percentile = stock.get('pe_percentile', default_values[stock_name]['pe_percentile'])
                if pe_percentile < 30:
                    undervalued.append(stock_name)
                elif pe_percentile < 70:
                    normal_valued.append(stock_name)
                else:
                    overvalued.append(stock_name)
            elif stock_name in ['中证红利ETF', '港股红利低波ETF']:
                dividend_rate = stock.get('dividend_rate', default_values[stock_name]['dividend_rate'])
                if dividend_rate > 6:
                    undervalued.append(stock_name)
                elif dividend_rate > 4:
                    normal_valued.append(stock_name)
                else:
                    overvalued.append(stock_name)
            elif stock_name == '长江电力':
                dividend_rate = stock.get('dividend_rate', default_values[stock_name]['dividend_rate'])
                if dividend_rate > 4:
                    undervalued.append(stock_name)
                elif dividend_rate > 3:
                    normal_valued.append(stock_name)
                else:
                    overvalued.append(stock_name)
            elif stock_name == '交通银行':
                pb = stock.get('pb', default_values[stock_name]['pb'])
                if pb < 0.7:
                    undervalued.append(stock_name)
                elif pb < 1:
                    normal_valued.append(stock_name)
                else:
                    overvalued.append(stock_name)
        
        # 生成操作建议
        summary = "🎯 本月执行策略（重要）\n\n"
        
        # 1. 降低配置
        if over_allocated:
            summary += "1️⃣ 降低配置：\n"
            for stock in over_allocated:
                summary += f"- {stock}（当前严重超配）\n"
            summary += "\n"
        
        # 2. 重点加仓
        if under_allocated:
            summary += "2️⃣ 重点加仓：\n"
            for stock in under_allocated:
                if stock in undervalued:
                    summary += f"- {stock}（当前严重低配且低估）\n"
                else:
                    summary += f"- {stock}（当前严重低配）\n"
            summary += "\n"
        
        # 3. 次级配置
        secondary = []
        for stock in normal_allocated:
            if stock in undervalued:
                secondary.append(stock)
        if secondary:
            summary += "3️⃣ 次级配置：\n"
            for stock in secondary:
                summary += f"- {stock}（轻度低估）\n"
            summary += "\n"
        
        # 目标
        summary += "📌 目标：\n"
        summary += "从\"红利集中\"逐步调整为\"红利 + 全球资产\"平衡配置"
        
        return summary

    def _build_macro_impact(self) -> str:
        """
        构建宏观影响评估部分

        Returns:
            宏观影响评估内容
        """
        from src.macro_monitor import macro_monitor

        # 获取宏观日历
        macro_calendar = config_manager.get_macro_calendar()

        # 获取最近的数据
        recent_events = macro_monitor.get_upcoming_events(macro_calendar, days=30)

        if not recent_events:
            return "近期无重要宏观数据公布"

        impact_mapping = {
            "CPI": {
                "上升": {"impact": "利空股票", "direction": "通胀压力增加", "affected": "成长股（美股）短期偏利空，红利资产相对利好"},
                "下降": {"impact": "利多股票", "direction": "通胀压力缓解", "affected": "对股市整体利好"},
                "高于预期": {"impact": "利空", "direction": "通胀超预期", "affected": "可能延缓降息，对股市形成压力"},
                "低于预期": {"impact": "利多", "direction": "通胀低于预期", "affected": "降息预期升温，利好股市"}
            },
            "非农": {
                "强劲": {"impact": "可能利空降息预期", "direction": "就业市场强劲", "affected": "经济韧性，但可能压制降息预期"},
                "疲弱": {"impact": "利多降息预期", "direction": "就业市场疲软", "affected": "降息预期升温，利好股市"},
                "高于预期": {"impact": "短期利多美元", "direction": "就业超预期", "affected": "可能压制黄金，但对美股影响复杂"},
                "低于预期": {"impact": "短期利空美元", "direction": "就业不及预期", "affected": "降息预期升温，利好黄金和美股"}
            },
            "FOMC": {
                "鹰派": {"impact": "利空成长股", "direction": "紧缩立场", "affected": "高估值股票承压，但银行股可能受益"},
                "鸽派": {"impact": "利多成长股", "direction": "宽松立场", "affected": "高估值股票受益，成长风格占优"},
                "降息": {"impact": "全面利好", "direction": "宽松周期开启", "affected": "所有风险资产普涨，债券和黄金受益"},
                "维持利率": {"impact": "中性", "direction": "按兵不动", "affected": "市场观望，等待进一步信号"}
            },
            "PCE": {
                "上升": {"impact": "利空", "direction": "通胀压力", "affected": "与CPI类似，消费支出增加可能延缓降息"},
                "下降": {"impact": "利多", "direction": "通胀回落", "affected": "降息预期升温，利好股市"}
            }
        }

        report = ""
        for event in recent_events:
            event_name = event.get('name', '')
            event_date = event.get('date', '')
            expected = event.get('expected', '')
            previous = event.get('previous', '')

            report += f"\n📅 {event_name} ({event_date})\n"
            report += f"   预期值: {expected} | 前值: {previous}\n"

            if event_name in impact_mapping:
                # 简单判断，实际应该根据实际值对比
                report += f"   → 通胀压力变化\n"
                report += f"   → 对成长股（美股）短期偏利空\n"
                report += f"   → 对红利资产相对利好\n"

        # 添加总结
        report += "\n📊 综合评估：\n"
        report += "当前宏观环境主要关注通胀走势和美联储货币政策。\n"
        report += "如果CPI/PCE持续回落，降息预期将支撑美股和全球风险资产。\n"
        report += "如果数据反复，可能导致市场波动加剧，此时红利资产防御价值凸显。\n"

        return report

    def _build_backtest_live_comparison(self) -> str:
        """构建回测 + 实盘对比摘要"""
        try:
            from .backtest_live_comparator import backtest_live_comparator

            result = backtest_live_comparator.build_comparison_summary(lookback_days=20)
            lines = [
                f"区间: 最近{result['lookback_days']}个交易日（基于本地缓存）",
                f"回测策略收益(近似): {result['backtest_return']:+.2%}",
                f"实盘仓位收益(近似): {result['live_return']:+.2%}",
                f"差异(回测-实盘): {result['return_gap']:+.2%}",
                f"仓位偏离度(绝对差总和): {result['allocation_gap']:.2f}%",
                f"有效回测标的: {result['covered_assets']}/{result['total_assets']}"
            ]
            return "\n".join(lines)
        except Exception as e:
            return f"回测 + 实盘对比暂不可用: {e}"


# 全局报告生成器实例
report_generator = ReportGenerator()
