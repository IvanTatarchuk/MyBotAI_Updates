import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from scipy.optimize import minimize
import cvxpy as cp
from pypfopt import EfficientFrontier, risk_models, expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation

from utils.data_fetcher import DataFetcher
from utils.logger import logger

class PortfolioOptimizer:
    def __init__(self):
        self.data_fetcher = DataFetcher()
        
    async def optimize(self, holdings: Dict[str, float], risk_tolerance: float, 
                      investment_horizon: str) -> Dict[str, Any]:
        try:
            # Fetch historical data for all assets
            symbols = list(holdings.keys())
            price_data = await self._fetch_portfolio_data(symbols)
            
            # Calculate expected returns and covariance matrix
            returns = expected_returns.mean_historical_return(price_data)
            cov_matrix = risk_models.sample_cov(price_data)
            
            # Optimize portfolio based on risk tolerance
            optimal_weights = self._optimize_weights(
                returns, cov_matrix, risk_tolerance, investment_horizon
            )
            
            # Calculate portfolio metrics
            metrics = self._calculate_portfolio_metrics(
                optimal_weights, returns, cov_matrix
            )
            
            # Generate rebalancing suggestions
            suggestions = self._generate_suggestions(
                holdings, optimal_weights, price_data
            )
            
            return {
                "optimal_allocation": optimal_weights,
                "expected_return": metrics["expected_return"],
                "risk_score": metrics["risk"],
                "sharpe_ratio": metrics["sharpe_ratio"],
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Portfolio optimization error: {str(e)}")
            raise
    
    async def _fetch_portfolio_data(self, symbols: List[str]) -> pd.DataFrame:
        """Fetch historical price data for portfolio assets"""
        price_data = {}
        
        for symbol in symbols:
            data = await self.data_fetcher.fetch_historical_data(symbol, "365d")
            price_data[symbol] = data['close']
        
        return pd.DataFrame(price_data)
    
    def _optimize_weights(self, returns: pd.Series, cov_matrix: pd.DataFrame,
                         risk_tolerance: float, investment_horizon: str) -> Dict[str, float]:
        """Optimize portfolio weights using Modern Portfolio Theory"""
        
        # Initialize Efficient Frontier
        ef = EfficientFrontier(returns, cov_matrix)
        
        # Apply optimization based on risk tolerance and horizon
        if risk_tolerance < 0.3:  # Conservative
            ef.min_volatility()
        elif risk_tolerance > 0.7:  # Aggressive
            ef.max_sharpe(risk_free_rate=0.02)
        else:  # Moderate
            # Target return based on risk tolerance
            target_return = returns.mean() * (1 + risk_tolerance)
            ef.efficient_return(target_return)
        
        # Get clean weights
        weights = ef.clean_weights()
        
        # Adjust for investment horizon
        if investment_horizon == "short":
            # Increase allocation to stable assets
            weights = self._adjust_for_short_term(weights, returns)
        elif investment_horizon == "long":
            # Allow for more volatile assets
            weights = self._adjust_for_long_term(weights, returns)
        
        return weights
    
    def _adjust_for_short_term(self, weights: Dict[str, float], 
                              returns: pd.Series) -> Dict[str, float]:
        """Adjust weights for short-term investment horizon"""
        # Reduce allocation to highly volatile assets
        adjusted_weights = {}
        total_weight = 0
        
        for asset, weight in weights.items():
            volatility_factor = 1 - (returns[asset].std() / returns.std().max())
            adjusted_weight = weight * (0.7 + 0.3 * volatility_factor)
            adjusted_weights[asset] = adjusted_weight
            total_weight += adjusted_weight
        
        # Normalize weights
        return {k: v/total_weight for k, v in adjusted_weights.items()}
    
    def _adjust_for_long_term(self, weights: Dict[str, float], 
                             returns: pd.Series) -> Dict[str, float]:
        """Adjust weights for long-term investment horizon"""
        # Slightly increase allocation to growth assets
        adjusted_weights = {}
        total_weight = 0
        
        for asset, weight in weights.items():
            growth_factor = 1 + (returns[asset] / returns.max()) * 0.2
            adjusted_weight = weight * growth_factor
            adjusted_weights[asset] = adjusted_weight
            total_weight += adjusted_weight
        
        # Normalize weights
        return {k: v/total_weight for k, v in adjusted_weights.items()}
    
    def _calculate_portfolio_metrics(self, weights: Dict[str, float], 
                                   returns: pd.Series, 
                                   cov_matrix: pd.DataFrame) -> Dict[str, float]:
        """Calculate portfolio performance metrics"""
        # Convert weights to array
        w = np.array([weights.get(asset, 0) for asset in returns.index])
        
        # Expected portfolio return
        portfolio_return = np.sum(returns * w) * 252  # Annualized
        
        # Portfolio variance and standard deviation
        portfolio_variance = np.dot(w.T, np.dot(cov_matrix, w))
        portfolio_std = np.sqrt(portfolio_variance) * np.sqrt(252)  # Annualized
        
        # Sharpe ratio (assuming 2% risk-free rate)
        sharpe_ratio = (portfolio_return - 0.02) / portfolio_std
        
        return {
            "expected_return": float(portfolio_return),
            "risk": float(portfolio_std),
            "sharpe_ratio": float(sharpe_ratio),
            "variance": float(portfolio_variance)
        }
    
    def _generate_suggestions(self, current_holdings: Dict[str, float],
                            optimal_weights: Dict[str, float],
                            price_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate rebalancing suggestions"""
        suggestions = []
        
        # Calculate total portfolio value
        total_value = sum(current_holdings.values())
        
        # Current weights
        current_weights = {
            asset: value/total_value 
            for asset, value in current_holdings.items()
        }
        
        # Generate suggestions for each asset
        for asset in set(list(current_weights.keys()) + list(optimal_weights.keys())):
            current_weight = current_weights.get(asset, 0)
            optimal_weight = optimal_weights.get(asset, 0)
            
            weight_diff = optimal_weight - current_weight
            
            if abs(weight_diff) > 0.02:  # Only suggest if difference > 2%
                value_change = weight_diff * total_value
                
                action = "buy" if weight_diff > 0 else "sell"
                
                suggestions.append({
                    "asset": asset,
                    "action": action,
                    "current_weight": round(current_weight * 100, 2),
                    "optimal_weight": round(optimal_weight * 100, 2),
                    "value_change": abs(value_change),
                    "priority": "high" if abs(weight_diff) > 0.1 else "medium"
                })
        
        # Sort by priority and value change
        suggestions.sort(key=lambda x: (
            0 if x["priority"] == "high" else 1,
            -x["value_change"]
        ))
        
        return suggestions
    
    async def backtest_strategy(self, strategy: Dict[str, Any], 
                               start_date: str, end_date: str) -> Dict[str, Any]:
        """Backtest an optimization strategy"""
        try:
            # Implementation of backtesting logic
            # This is simplified for demo purposes
            
            return {
                "total_return": 0.125,  # 12.5%
                "annualized_return": 0.085,
                "max_drawdown": -0.082,
                "sharpe_ratio": 1.24,
                "win_rate": 0.58,
                "trades": 145,
                "best_trade": 0.034,
                "worst_trade": -0.021
            }
            
        except Exception as e:
            logger.error(f"Backtesting error: {str(e)}")
            raise
    
    def calculate_efficient_frontier(self, symbols: List[str], 
                                   n_portfolios: int = 100) -> List[Dict[str, float]]:
        """Calculate efficient frontier for visualization"""
        # This would generate multiple portfolio combinations
        # along the efficient frontier for plotting
        
        portfolios = []
        for i in range(n_portfolios):
            risk = i / n_portfolios
            portfolios.append({
                "risk": risk,
                "return": risk * 0.15 + 0.05,  # Simplified linear relationship
                "sharpe": (risk * 0.15 + 0.05 - 0.02) / (risk + 0.1)
            })
        
        return portfolios