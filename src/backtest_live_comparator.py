# -*- coding: utf-8 -*-
"""
回测 + 实盘对比模块
基于本地缓存的日线收盘价，对比策略建议仓位与当前实盘仓位的近期表现。
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from .config_manager import config_manager
from .portfolio_manager import portfolio_manager


class BacktestLiveComparator:
    """回测与实盘对比器"""

    def __init__(self):
        self.data_dir = Path(config_manager.get_data_dir())

    def _load_close_series(self, code: str) -> List[Tuple[str, float]]:
        """读取单个标的的本地日线收盘价序列"""
        file_path = self.data_dir / f"{code}_daily.json"
        if not file_path.exists():
            return []

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception:
            return []

        series: List[Tuple[str, float]] = []
        for day, payload in data.items():
            close = payload.get("close")
            if isinstance(close, (int, float)) and close > 0:
                series.append((day, float(close)))

        series.sort(key=lambda x: x[0])
        return series

    def _calc_period_return(self, code: str, lookback_days: int) -> Optional[float]:
        """计算近N个交易日区间收益"""
        series = self._load_close_series(code)
        if len(series) < 2:
            return None

        window = series[-(lookback_days + 1):]
        if len(window) < 2:
            return None

        start_price = window[0][1]
        end_price = window[-1][1]
        if start_price <= 0:
            return None

        return (end_price / start_price) - 1.0

    def build_comparison_summary(self, lookback_days: int = 20) -> Dict[str, Any]:
        """
        生成回测 + 实盘对比摘要
        回测侧：使用当前策略建议的资金分配比例
        实盘侧：使用当前持仓比例
        """
        from .report_generator import report_generator

        total_amount = config_manager.get_monthly_investment()
        investment_plan = report_generator.calculate_final_investment_plan(total_amount)
        live_allocations = portfolio_manager.get_current_allocations()

        total_final_amount = sum(item.get("final_amount", 0) for item in investment_plan)
        if total_final_amount <= 0:
            total_final_amount = 1.0

        backtest_allocations = {
            item["name"]: (item.get("final_amount", 0) / total_final_amount) * 100
            for item in investment_plan
        }

        code_map = {
            stock["name"]: stock["code"]
            for stock in config_manager.get_stocks()
        }

        all_assets = sorted(set(backtest_allocations.keys()) | set(live_allocations.keys()))
        allocation_gap = sum(
            abs(backtest_allocations.get(name, 0) - live_allocations.get(name, 0))
            for name in all_assets
        )

        backtest_return = 0.0
        live_return = 0.0
        covered_assets = 0

        for name in all_assets:
            code = code_map.get(name)
            if not code:
                continue

            period_return = self._calc_period_return(code, lookback_days)
            if period_return is None:
                continue

            covered_assets += 1
            backtest_return += (backtest_allocations.get(name, 0) / 100.0) * period_return
            live_return += (live_allocations.get(name, 0) / 100.0) * period_return

        return {
            "lookback_days": lookback_days,
            "backtest_return": backtest_return,
            "live_return": live_return,
            "return_gap": backtest_return - live_return,
            "allocation_gap": allocation_gap,
            "covered_assets": covered_assets,
            "total_assets": len(all_assets),
        }


backtest_live_comparator = BacktestLiveComparator()
