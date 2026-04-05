# -*- coding: utf-8 -*-
"""
回测 + 实盘对比功能测试脚本
"""

from src.backtest_live_comparator import backtest_live_comparator


def test_backtest_live_compare():
    result = backtest_live_comparator.build_comparison_summary(lookback_days=20)
    print("回测 + 实盘对比结果")
    print(f"区间: 最近{result['lookback_days']}个交易日")
    print(f"回测策略收益(近似): {result['backtest_return']:+.2%}")
    print(f"实盘仓位收益(近似): {result['live_return']:+.2%}")
    print(f"差异(回测-实盘): {result['return_gap']:+.2%}")
    print(f"仓位偏离度: {result['allocation_gap']:.2f}%")
    print(f"有效回测标的: {result['covered_assets']}/{result['total_assets']}")


if __name__ == "__main__":
    test_backtest_live_compare()
