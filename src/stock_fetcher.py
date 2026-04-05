# -*- coding: utf-8 -*-
"""
股票数据获取模块
支持A股、港股和美股的数据获取
"""

import requests
import re
import json
import os
import time
import yfinance as yf
from datetime import datetime
from typing import Dict, Optional, List, Any
from .config_manager import config_manager


class StockFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        """初始化股票数据获取器"""
        self.data_dir = config_manager.get_data_dir()
        os.makedirs(self.data_dir, exist_ok=True)
        # 数据来源可信度评分
        self.source_credibility = {
            "akshare": 0.9,
            "yfinance": 0.85,
            "sina": 0.8,
            "estimate": 0.5,
            "fallback": 0.3
        }
    
    def fetch_stock_data(self, stock: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        获取股票数据
        
        Args:
            stock: 股票配置
        
        Returns:
            股票数据字典
        """
        stock_type = stock.get('type', 'stock')
        
        try:
            if stock_type == 'stock' or stock_type == 'etf' or stock_type == 'hk_etf' or stock_type == 'us_etf':
                # 所有上交所上市的股票和ETF都使用A股数据获取方式
                data = self._fetch_a_stock(stock)
                
                # 对于美股ETF，额外获取标普500指数数据
                if stock_type == 'us_etf' and data:
                    index_code = stock.get('index', '^GSPC')
                    try:
                        # 获取标普500指数数据
                        index_ticker = yf.Ticker(index_code)
                        index_hist = index_ticker.history(period="1d")
                        index_price = index_hist['Close'].iloc[-1] if not index_hist.empty else 0
                        index_change_percent = 0
                        if len(index_hist) > 1:
                            index_pre_close = index_hist['Close'].iloc[-2]
                            if index_pre_close > 0:
                                index_change_percent = round((index_price - index_pre_close) / index_pre_close * 100, 2)
                        
                        data['index_price'] = index_price
                        data['index_change_percent'] = index_change_percent
                    except Exception as e:
                        print(f"获取标普500指数数据失败: {e}")
                
                return data
            else:
                print(f"未知股票类型: {stock_type}")
                return None
        except Exception as e:
            print(f"获取股票 {stock['code']} 数据失败: {e}")
            return None
    
    def _fetch_a_stock(self, stock: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """获取A股数据"""
        code = stock['code']
        market = stock['market']
        
        try:
            # 新浪财经API
            full_code = f"{market}{code}"
            url = f"http://hq.sinajs.cn/list={full_code}"
            
            headers = {
                "Referer": "http://finance.sina.com.cn",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'
            
            # 解析数据
            pattern = rf'var hq_str_{full_code}="(.*)";'
            match = re.search(pattern, response.text)
            
            if not match:
                print(f"未找到股票 {code} 的数据")
                return None
            
            data_str = match.group(1)
            if not data_str:
                print(f"股票 {code} 数据为空")
                return None
            
            # 数据格式：名称,今开,昨收,最新价,最高,最低,买一,卖一,成交量,成交额,...
            parts = data_str.split(',')
            
            if len(parts) < 32:
                print(f"股票 {code} 数据格式错误")
                return None
            
            name = parts[0]
            open_price = float(parts[1]) if parts[1] else 0
            pre_close = float(parts[2]) if parts[2] else 0
            price = float(parts[3]) if parts[3] else 0
            high = float(parts[4]) if parts[4] else 0
            low = float(parts[5]) if parts[5] else 0
            volume = float(parts[8]) if parts[8] else 0  # 成交量（手）
            amount = float(parts[9]) if parts[9] else 0  # 成交额（元）
            
            # 计算涨跌幅
            if pre_close > 0:
                change_percent = round((price - pre_close) / pre_close * 100, 2)
                change_amount = round(price - pre_close, 2)
            else:
                change_percent = 0
                change_amount = 0
            
            # 添加数据来源和可信度评分
            source = "sina"
            credibility = self.source_credibility.get(source, 0.5)
            
            quote = {
                "code": code,
                "name": name,
                "price": price,
                "open": open_price,
                "high": high,
                "low": low,
                "pre_close": pre_close,
                "volume": volume * 100,  # 转换为股
                "amount": amount,
                "change_percent": change_percent,
                "change_amount": change_amount,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": stock.get('type', 'stock'),
                "source": source,
                "credibility": credibility
            }
            
            # 保存当日数据
            self._save_daily_data(code, quote)
            
            # 获取历史成交量
            avg_volume = self._get_history_volume(code)
            quote['avg_volume'] = avg_volume
            
            return quote
            
        except Exception as e:
            print(f"获取A股 {code} 数据失败: {e}")
            return None
    

    
    def _get_history_volume(self, code: str, days: int = 5) -> Optional[float]:
        """获取A股历史平均成交量"""
        try:
            # 尝试从缓存读取
            cache_file = os.path.join(self.data_dir, f"{code}_history.json")
            today = datetime.now().strftime("%Y-%m-%d")
            
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('avg_volume') and data.get('update_time', '').startswith(today):
                        return data['avg_volume']
            
            # 使用东方财富API获取历史数据
            secid = f"1.{code}" if code.startswith('6') else f"0.{code}"
            
            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                "secid": secid,
                "fields1": "f1,f2,f3,f4,f5,f6",
                "fields2": "f51,f52,f53,f54,f55,f56,f57",
                "klt": 101,  # 日K
                "fqt": 1,    # 前复权
                "end": "20500101",
                "lmt": days + 1
            }
            
            headers = {
                "Referer": "http://quote.eastmoney.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            result = response.json()
            
            if result.get('data') and result['data'].get('klines'):
                klines = result['data']['klines']
                # 计算最近几天的平均成交量（排除今天）
                if len(klines) > 1:
                    volumes = []
                    for kline in klines[:-1]:  # 排除最新的一天
                        parts = kline.split(',')
                        if len(parts) >= 6:
                            vol = float(parts[5])  # 成交量（手）
                            volumes.append(vol * 100)  # 转换为股
                    
                    if volumes:
                        avg_volume = sum(volumes) / len(volumes)
                        
                        # 保存到缓存
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            json.dump({
                                "avg_volume": float(avg_volume),
                                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }, f, ensure_ascii=False, indent=2)
                        
                        return float(avg_volume)
            
            return None
            
        except Exception as e:
            print(f"获取A股 {code} 历史成交量失败: {e}")
            return None
    

    
    def _save_daily_data(self, code: str, quote: Dict[str, Any]):
        """保存当日数据"""
        today = datetime.now().strftime("%Y-%m-%d")
        cache_file = os.path.join(self.data_dir, f"{code}_daily.json")
        
        data = {}
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        
        # 只保存当天的数据
        data[today] = {
            "open": quote['open'],
            "volume": quote['volume'],
            "high": quote['high'],
            "low": quote['low'],
            "close": quote['price'],
            "change_percent": quote['change_percent']
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def fetch_all_stocks(self, stocks: List[Dict[str, str]]) -> Dict[str, Dict[str, Any]]:
        """
        获取所有股票数据
        
        Args:
            stocks: 股票配置列表
        
        Returns:
            股票代码到数据的映射
        """
        results = {}
        
        for stock in stocks:
            code = stock['code']
            data = self.fetch_stock_data(stock)
            if data:
                results[code] = data
            
            # 避免请求过快
            time.sleep(0.3)
        
        return results


# 全局数据获取实例
stock_fetcher = StockFetcher()
