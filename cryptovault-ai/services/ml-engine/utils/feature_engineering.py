import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sklearn.preprocessing import StandardScaler
from ta import add_all_ta_features
from ta.utils import dropna

class FeatureEngineer:
    def __init__(self):
        self.scaler = StandardScaler()
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive feature set for ML models"""
        
        # Make a copy to avoid modifying original
        features_df = df.copy()
        
        # Add all technical analysis features
        features_df = self._add_advanced_technical_indicators(features_df)
        
        # Add time-based features
        features_df = self._add_time_features(features_df)
        
        # Add price pattern features
        features_df = self._add_pattern_features(features_df)
        
        # Add market microstructure features
        features_df = self._add_microstructure_features(features_df)
        
        # Add lag features
        features_df = self._add_lag_features(features_df)
        
        # Add rolling statistics
        features_df = self._add_rolling_features(features_df)
        
        # Clean up
        features_df = features_df.fillna(method='ffill').fillna(0)
        
        return features_df
    
    def _add_advanced_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add advanced technical indicators"""
        
        # Ichimoku Cloud
        high_9 = df['high'].rolling(window=9).max()
        low_9 = df['low'].rolling(window=9).min()
        df['ichimoku_conversion'] = (high_9 + low_9) / 2
        
        high_26 = df['high'].rolling(window=26).max()
        low_26 = df['low'].rolling(window=26).min()
        df['ichimoku_base'] = (high_26 + low_26) / 2
        
        # Average True Range
        df['atr'] = self._calculate_atr(df)
        
        # Commodity Channel Index
        df['cci'] = self._calculate_cci(df)
        
        # Williams %R
        df['williams_r'] = self._calculate_williams_r(df)
        
        # Stochastic Oscillator
        df['stoch_k'], df['stoch_d'] = self._calculate_stochastic(df)
        
        # Money Flow Index
        df['mfi'] = self._calculate_mfi(df)
        
        # On Balance Volume
        df['obv'] = self._calculate_obv(df)
        
        # Force Index
        df['force_index'] = self._calculate_force_index(df)
        
        return df
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features"""
        
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Basic time features
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['day_of_month'] = df.index.day
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter
        
        # Cyclical encoding
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Trading session indicators
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_month_start'] = (df['day_of_month'] <= 5).astype(int)
        df['is_month_end'] = (df['day_of_month'] >= 25).astype(int)
        
        return df
    
    def _add_pattern_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price pattern recognition features"""
        
        # Candlestick patterns
        df['doji'] = ((abs(df['close'] - df['open']) / 
                      (df['high'] - df['low'])) < 0.1).astype(int)
        
        df['hammer'] = (((df['high'] - df['low']) > 3 * abs(df['close'] - df['open'])) &
                       ((df['close'] - df['low']) / (0.001 + df['high'] - df['low']) > 0.6) &
                       ((df['open'] - df['low']) / (0.001 + df['high'] - df['low']) > 0.6)).astype(int)
        
        # Support and resistance levels
        df['resistance'] = df['high'].rolling(window=20).max()
        df['support'] = df['low'].rolling(window=20).min()
        df['price_to_resistance'] = (df['close'] - df['resistance']) / df['resistance']
        df['price_to_support'] = (df['close'] - df['support']) / df['support']
        
        # Trend strength
        df['trend_strength'] = abs(df['sma_7'] - df['sma_25']) / df['sma_25']
        
        # Breakout indicators
        df['volume_breakout'] = (df['volume'] > df['volume_sma'] * 2).astype(int)
        df['price_breakout'] = ((df['close'] > df['resistance'].shift(1)) | 
                               (df['close'] < df['support'].shift(1))).astype(int)
        
        return df
    
    def _add_microstructure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market microstructure features"""
        
        # Spread and liquidity proxies
        df['hl_spread'] = (df['high'] - df['low']) / df['close']
        df['co_spread'] = abs(df['close'] - df['open']) / df['close']
        
        # Volatility measures
        df['parkinson_vol'] = np.sqrt(
            np.log(df['high'] / df['low']) ** 2 / (4 * np.log(2))
        ).rolling(window=20).mean()
        
        df['garman_klass_vol'] = np.sqrt(
            0.5 * np.log(df['high'] / df['low']) ** 2 - 
            (2 * np.log(2) - 1) * np.log(df['close'] / df['open']) ** 2
        ).rolling(window=20).mean()
        
        # Volume-price relationships
        df['volume_price_trend'] = (df['volume'] * 
                                   ((df['close'] - df['close'].shift(1)) / 
                                    df['close'].shift(1))).cumsum()
        
        df['price_volume_ratio'] = df['close'] / (df['volume'] + 1)
        
        return df
    
    def _add_lag_features(self, df: pd.DataFrame, lags: List[int] = [1, 2, 3, 5, 7]) -> pd.DataFrame:
        """Add lagged features"""
        
        for lag in lags:
            df[f'close_lag_{lag}'] = df['close'].shift(lag)
            df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
            df[f'return_lag_{lag}'] = df['price_change'].shift(lag)
            
        # Lag ratios
        for lag in lags:
            df[f'close_ratio_lag_{lag}'] = df['close'] / df[f'close_lag_{lag}']
            
        return df
    
    def _add_rolling_features(self, df: pd.DataFrame, 
                            windows: List[int] = [7, 14, 30]) -> pd.DataFrame:
        """Add rolling window features"""
        
        for window in windows:
            # Rolling statistics
            df[f'rolling_mean_{window}'] = df['close'].rolling(window=window).mean()
            df[f'rolling_std_{window}'] = df['close'].rolling(window=window).std()
            df[f'rolling_min_{window}'] = df['close'].rolling(window=window).min()
            df[f'rolling_max_{window}'] = df['close'].rolling(window=window).max()
            
            # Rolling returns
            df[f'rolling_return_{window}'] = df['close'].pct_change(periods=window)
            
            # Rolling volume
            df[f'rolling_volume_mean_{window}'] = df['volume'].rolling(window=window).mean()
            
            # Price position in range
            df[f'price_position_{window}'] = (
                (df['close'] - df[f'rolling_min_{window}']) / 
                (df[f'rolling_max_{window}'] - df[f'rolling_min_{window}'] + 0.0001)
            )
        
        return df
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        return true_range.rolling(period).mean()
    
    def _calculate_cci(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Commodity Channel Index"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - x.mean()))
        )
        
        return (typical_price - sma) / (0.015 * mad)
    
    def _calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Williams %R"""
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        
        return -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
    
    def _calculate_stochastic(self, df: pd.DataFrame, 
                            k_period: int = 14, 
                            d_period: int = 3) -> tuple:
        """Calculate Stochastic Oscillator"""
        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()
        
        k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return k_percent, d_percent
    
    def _calculate_mfi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Money Flow Index"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        money_flow = typical_price * df['volume']
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0)
        
        positive_sum = positive_flow.rolling(window=period).sum()
        negative_sum = negative_flow.rolling(window=period).sum()
        
        money_ratio = positive_sum / negative_sum
        mfi = 100 - (100 / (1 + money_ratio))
        
        return mfi
    
    def _calculate_obv(self, df: pd.DataFrame) -> pd.Series:
        """Calculate On Balance Volume"""
        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        return obv
    
    def _calculate_force_index(self, df: pd.DataFrame, period: int = 13) -> pd.Series:
        """Calculate Force Index"""
        force = df['close'].diff() * df['volume']
        return force.ewm(span=period, adjust=False).mean()