from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from services.price_predictor import PricePredictor
from services.portfolio_optimizer import PortfolioOptimizer
from services.risk_analyzer import RiskAnalyzer
from services.sentiment_analyzer import SentimentAnalyzer
from services.market_analyzer import MarketAnalyzer
from utils.logger import logger

load_dotenv()

app = FastAPI(title="CryptoVault AI ML Engine", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
price_predictor = PricePredictor()
portfolio_optimizer = PortfolioOptimizer()
risk_analyzer = RiskAnalyzer()
sentiment_analyzer = SentimentAnalyzer()
market_analyzer = MarketAnalyzer()

# Request models
class PredictionRequest(BaseModel):
    symbol: str
    timeframe: str = "7d"  # 1d, 7d, 30d
    model_type: str = "ensemble"  # lstm, prophet, xgboost, ensemble

class PortfolioOptimizationRequest(BaseModel):
    holdings: Dict[str, float]
    risk_tolerance: float = 0.5  # 0-1 scale
    investment_horizon: str = "medium"  # short, medium, long

class RiskAnalysisRequest(BaseModel):
    portfolio_id: str
    analysis_type: str = "comprehensive"

class SentimentRequest(BaseModel):
    symbols: List[str]
    sources: List[str] = ["twitter", "reddit", "news"]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ml-engine"}

@app.post("/predict/price")
async def predict_price(request: PredictionRequest):
    try:
        logger.info(f"Price prediction request for {request.symbol}")
        
        prediction = await price_predictor.predict(
            symbol=request.symbol,
            timeframe=request.timeframe,
            model_type=request.model_type
        )
        
        return {
            "symbol": request.symbol,
            "predictions": prediction["predictions"],
            "confidence": prediction["confidence"],
            "model": request.model_type,
            "features_importance": prediction.get("features_importance", {}),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Price prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize/portfolio")
async def optimize_portfolio(request: PortfolioOptimizationRequest):
    try:
        logger.info("Portfolio optimization request")
        
        optimization = await portfolio_optimizer.optimize(
            holdings=request.holdings,
            risk_tolerance=request.risk_tolerance,
            investment_horizon=request.investment_horizon
        )
        
        return {
            "current_allocation": request.holdings,
            "optimal_allocation": optimization["optimal_allocation"],
            "expected_return": optimization["expected_return"],
            "risk_score": optimization["risk_score"],
            "sharpe_ratio": optimization["sharpe_ratio"],
            "rebalancing_suggestions": optimization["suggestions"],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Portfolio optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/risk")
async def analyze_risk(request: RiskAnalysisRequest):
    try:
        logger.info(f"Risk analysis request for portfolio {request.portfolio_id}")
        
        analysis = await risk_analyzer.analyze(
            portfolio_id=request.portfolio_id,
            analysis_type=request.analysis_type
        )
        
        return {
            "portfolio_id": request.portfolio_id,
            "risk_metrics": analysis["metrics"],
            "var_95": analysis["value_at_risk_95"],
            "cvar_95": analysis["conditional_value_at_risk_95"],
            "max_drawdown": analysis["max_drawdown"],
            "volatility": analysis["volatility"],
            "beta": analysis["beta"],
            "correlation_matrix": analysis["correlation_matrix"],
            "risk_factors": analysis["risk_factors"],
            "recommendations": analysis["recommendations"],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Risk analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    try:
        logger.info(f"Sentiment analysis request for {request.symbols}")
        
        analysis = await sentiment_analyzer.analyze(
            symbols=request.symbols,
            sources=request.sources
        )
        
        return {
            "symbols": request.symbols,
            "sentiment_scores": analysis["scores"],
            "sentiment_trend": analysis["trend"],
            "social_volume": analysis["volume"],
            "influential_posts": analysis["influential_posts"],
            "sentiment_drivers": analysis["drivers"],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market/analysis")
async def get_market_analysis():
    try:
        logger.info("Market analysis request")
        
        analysis = await market_analyzer.analyze_market()
        
        return {
            "market_trend": analysis["trend"],
            "market_sentiment": analysis["sentiment"],
            "fear_greed_index": analysis["fear_greed_index"],
            "sector_performance": analysis["sector_performance"],
            "top_gainers": analysis["top_gainers"],
            "top_losers": analysis["top_losers"],
            "volume_analysis": analysis["volume_analysis"],
            "correlation_insights": analysis["correlations"],
            "market_regime": analysis["regime"],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Market analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train/model")
async def train_model(background_tasks: BackgroundTasks, symbol: str, model_type: str = "lstm"):
    try:
        logger.info(f"Model training request for {symbol} with {model_type}")
        
        # Add training task to background
        background_tasks.add_task(
            price_predictor.train_model,
            symbol=symbol,
            model_type=model_type
        )
        
        return {
            "message": f"Training {model_type} model for {symbol} started",
            "status": "in_progress",
            "estimated_time": "15-30 minutes"
        }
    
    except Exception as e:
        logger.error(f"Model training error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/performance")
async def get_model_performance():
    try:
        performance = await price_predictor.get_model_performance()
        
        return {
            "models": performance,
            "best_performing": max(performance.items(), key=lambda x: x[1]["accuracy"])[0],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Model performance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("ML_ENGINE_PORT", 5002)),
        reload=True
    )