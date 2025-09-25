import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ccxt
import yfinance as yf
import asyncio
from typing import Dict, List, Any
import aiohttp
from utils.logger import logger

class DataFetcher:
    def __init__(self):
        self.exchanges = {
            'binance': ccxt.binance(),
            'coinbase': ccxt.coinbase(),
            'kraken': ccxt.kraken()
        }
        
    async def fetch_historical_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Fetch historical price data for a symbol"""
        try:
            # Convert timeframe to days
            days = self._parse_timeframe(timeframe)
            
            # Try multiple sources
            data = await self._fetch_from_binance(symbol, days)
            
            if data is None or len(data) < days * 0.8:
                data = await self._fetch_from_yfinance(symbol, days)
            
            if data is None:
                raise ValueError(f"Unable to fetch data for {symbol}")
            
            # Add technical indicators
            data = self._add_technical_indicators(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            raise
    
    async def _fetch_from_binance(self, symbol: str, days: int) -> pd.DataFrame:
        """Fetch data from Binance"""
        try:
            exchange = self.exchanges['binance']
            
            # Convert symbol format
            trading_symbol = f"{symbol}/USDT"
            
            # Calculate timestamps
            since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            # Fetch OHLCV data
            ohlcv = exchange.fetch_ohlcv(trading_symbol, '1d', since=since)
            
            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv, 
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            logger.warning(f"Binance fetch failed for {symbol}: {str(e)}")
            return None
    
    async def _fetch_from_yfinance(self, symbol: str, days: int) -> pd.DataFrame:
        """Fetch data from Yahoo Finance (backup source)"""
        try:
            # Add -USD suffix for crypto symbols
            ticker_symbol = f"{symbol}-USD"
            
            # Download data
            ticker = yf.Ticker(ticker_symbol)
            df = ticker.history(period=f"{days}d")
            
            # Rename columns to match expected format
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.warning(f"YFinance fetch failed for {symbol}: {str(e)}")
            return None
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the dataframe"""
        # Simple Moving Averages
        df['sma_7'] = df['close'].rolling(window=7).mean()
        df['sma_25'] = df['close'].rolling(window=25).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # Exponential Moving Averages
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_diff'] = df['macd'] - df['macd_signal']
        
        # RSI
        df['rsi'] = self._calculate_rsi(df['close'])
        
        # Bollinger Bands
        bb_window = 20
        df['bb_middle'] = df['close'].rolling(window=bb_window).mean()
        bb_std = df['close'].rolling(window=bb_window).std()
        df['bollinger_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bollinger_lower'] = df['bb_middle'] - (bb_std * 2)
        
        # Volume indicators
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Price changes
        df['price_change'] = df['close'].pct_change()
        df['price_change_7d'] = df['close'].pct_change(periods=7)
        
        # Fill NaN values
        df.fillna(method='ffill', inplace=True)
        df.fillna(0, inplace=True)
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _parse_timeframe(self, timeframe: str) -> int:
        """Parse timeframe string to days"""
        if timeframe.endswith('d'):
            return int(timeframe[:-1])
        elif timeframe.endswith('w'):
            return int(timeframe[:-1]) * 7
        elif timeframe.endswith('m'):
            return int(timeframe[:-1]) * 30
        elif timeframe.endswith('y'):
            return int(timeframe[:-1]) * 365
        else:
            return 30  # Default to 30 days
    
    async def fetch_realtime_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Fetch real-time price data"""
        realtime_data = {}
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._fetch_single_price(session, symbol) 
                for symbol in symbols
            ]
            results = await asyncio.gather(*tasks)
            
            for symbol, data in zip(symbols, results):
                if data:
                    realtime_data[symbol] = data
        
        return realtime_data
    
    async def _fetch_single_price(self, session: aiohttp.ClientSession, 
                                 symbol: str) -> Dict[str, Any]:
        """Fetch single symbol price data"""
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr"
            params = {"symbol": f"{symbol}USDT"}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "price": float(data["lastPrice"]),
                        "change_24h": float(data["priceChangePercent"]),
                        "volume_24h": float(data["volume"]),
                        "high_24h": float(data["highPrice"]),
                        "low_24h": float(data["lowPrice"])
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {str(e)}")
            
        return None