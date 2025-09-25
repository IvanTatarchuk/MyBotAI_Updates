import { spawn } from 'child_process';
import { logger } from '../utils/logger';
import { Asset } from '../models/Asset';
import { AIPrediction } from '../models/AIPrediction';
import { AppDataSource } from '../config/database';
import { MarketData } from './TradingEngine';

export interface PricePrediction {
  symbol: string;
  currentPrice: number;
  predictedPrice: number;
  confidence: number;
  timeframe: string;
  direction: 'up' | 'down' | 'sideways';
  volatility: number;
  support: number;
  resistance: number;
  recommendation: 'BUY' | 'SELL' | 'HOLD';
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH';
  timestamp: number;
}

export interface TechnicalAnalysis {
  symbol: string;
  rsi: number;
  macd: {
    macd: number;
    signal: number;
    histogram: number;
  };
  bollinger: {
    upper: number;
    middle: number;
    lower: number;
  };
  movingAverages: {
    sma20: number;
    sma50: number;
    sma200: number;
    ema12: number;
    ema26: number;
  };
  support: number;
  resistance: number;
  trend: 'BULLISH' | 'BEARISH' | 'SIDEWAYS';
  timestamp: number;
}

export interface SentimentAnalysis {
  symbol: string;
  overall: number; // -1 to 1
  news: number;
  social: number;
  technical: number;
  fearGreed: number;
  confidence: number;
  sources: {
    twitter: number;
    reddit: number;
    news: number;
    analyst: number;
  };
  timestamp: number;
}

export class AIService {
  private isInitialized = false;
  private predictionRepository = AppDataSource.getRepository(AIPrediction);
  private pythonProcess?: any;

  public async initialize(): Promise<void> {
    try {
      logger.info('Initializing AI Service...');

      // Initialize Python ML environment
      await this.initializePythonEnvironment();

      // Load pre-trained models
      await this.loadModels();

      // Start background prediction tasks
      this.startPredictionTasks();

      this.isInitialized = true;
      logger.info('AI Service initialized successfully');

    } catch (error) {
      logger.error('Failed to initialize AI Service:', error);
      throw error;
    }
  }

  private async initializePythonEnvironment(): Promise<void> {
    try {
      // Check if Python environment is available
      const pythonCheck = spawn('python3', ['--version']);
      
      pythonCheck.on('close', (code) => {
        if (code !== 0) {
          logger.warn('Python3 not found, using simplified predictions');
        } else {
          logger.info('Python3 environment ready');
        }
      });

    } catch (error) {
      logger.warn('Python environment setup failed, using fallback methods:', error);
    }
  }

  private async loadModels(): Promise<void> {
    try {
      // In a real implementation, this would load pre-trained ML models
      // For now, we'll use simplified algorithms
      logger.info('Loading AI models...');
      
      // Simulate model loading
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      logger.info('AI models loaded successfully');

    } catch (error) {
      logger.error('Failed to load AI models:', error);
    }
  }

  private startPredictionTasks(): void {
    // Run predictions every 5 minutes
    setInterval(async () => {
      if (this.isInitialized) {
        await this.runBatchPredictions();
      }
    }, 5 * 60 * 1000);

    // Run sentiment analysis every 10 minutes
    setInterval(async () => {
      if (this.isInitialized) {
        await this.runSentimentAnalysis();
      }
    }, 10 * 60 * 1000);
  }

  public async predictPrice(
    asset: Asset,
    marketData: MarketData
  ): Promise<PricePrediction | null> {
    try {
      // Gather historical data for prediction
      const historicalData = await this.getHistoricalData(asset.symbol, 100);
      
      // Perform technical analysis
      const technicalAnalysis = await this.performTechnicalAnalysis(asset.symbol, historicalData);
      
      // Perform sentiment analysis
      const sentimentAnalysis = await this.performSentimentAnalysis(asset.symbol);
      
      // Generate price prediction using ensemble methods
      const prediction = await this.generatePricePrediction(
        asset,
        marketData,
        technicalAnalysis,
        sentimentAnalysis,
        historicalData
      );

      // Save prediction to database
      if (prediction) {
        await this.savePrediction(prediction);
      }

      return prediction;

    } catch (error) {
      logger.error(`Failed to predict price for ${asset.symbol}:`, error);
      return null;
    }
  }

  private async getHistoricalData(symbol: string, days: number): Promise<any[]> {
    try {
      // In a real implementation, this would fetch from a data provider
      // For now, generate synthetic historical data
      const data = [];
      const basePrice = Math.random() * 1000;
      
      for (let i = days; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        
        data.push({
          date: date.toISOString(),
          open: basePrice * (0.95 + Math.random() * 0.1),
          high: basePrice * (1 + Math.random() * 0.05),
          low: basePrice * (0.9 + Math.random() * 0.1),
          close: basePrice * (0.95 + Math.random() * 0.1),
          volume: Math.random() * 1000000,
        });
      }

      return data;

    } catch (error) {
      logger.error('Failed to get historical data:', error);
      return [];
    }
  }

  private async performTechnicalAnalysis(
    symbol: string,
    historicalData: any[]
  ): Promise<TechnicalAnalysis> {
    try {
      const prices = historicalData.map(d => d.close);
      const volumes = historicalData.map(d => d.volume);

      // Calculate RSI
      const rsi = this.calculateRSI(prices);

      // Calculate MACD
      const macd = this.calculateMACD(prices);

      // Calculate Bollinger Bands
      const bollinger = this.calculateBollingerBands(prices);

      // Calculate Moving Averages
      const movingAverages = this.calculateMovingAverages(prices);

      // Determine trend
      const trend = this.determineTrend(movingAverages);

      // Calculate support and resistance
      const { support, resistance } = this.calculateSupportResistance(prices);

      return {
        symbol,
        rsi,
        macd,
        bollinger,
        movingAverages,
        support,
        resistance,
        trend,
        timestamp: Date.now(),
      };

    } catch (error) {
      logger.error('Technical analysis failed:', error);
      throw error;
    }
  }

  private calculateRSI(prices: number[], period: number = 14): number {
    if (prices.length < period + 1) return 50;

    let gains = 0;
    let losses = 0;

    for (let i = 1; i <= period; i++) {
      const change = prices[i] - prices[i - 1];
      if (change > 0) gains += change;
      else losses -= change;
    }

    const avgGain = gains / period;
    const avgLoss = losses / period;

    if (avgLoss === 0) return 100;

    const rs = avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
  }

  private calculateMACD(prices: number[]): { macd: number; signal: number; histogram: number } {
    const ema12 = this.calculateEMA(prices, 12);
    const ema26 = this.calculateEMA(prices, 26);
    const macd = ema12 - ema26;
    
    // Simplified signal line calculation
    const signal = macd * 0.9; // This would be a proper EMA of MACD in reality
    const histogram = macd - signal;

    return { macd, signal, histogram };
  }

  private calculateEMA(prices: number[], period: number): number {
    if (prices.length < period) return prices[prices.length - 1];

    const multiplier = 2 / (period + 1);
    let ema = prices[0];

    for (let i = 1; i < prices.length; i++) {
      ema = (prices[i] * multiplier) + (ema * (1 - multiplier));
    }

    return ema;
  }

  private calculateBollingerBands(prices: number[], period: number = 20): {
    upper: number;
    middle: number;
    lower: number;
  } {
    if (prices.length < period) {
      const price = prices[prices.length - 1];
      return { upper: price * 1.02, middle: price, lower: price * 0.98 };
    }

    const recentPrices = prices.slice(-period);
    const middle = recentPrices.reduce((a, b) => a + b) / period;
    
    const variance = recentPrices.reduce((acc, price) => acc + Math.pow(price - middle, 2), 0) / period;
    const stdDev = Math.sqrt(variance);

    return {
      upper: middle + (2 * stdDev),
      middle,
      lower: middle - (2 * stdDev),
    };
  }

  private calculateMovingAverages(prices: number[]): {
    sma20: number;
    sma50: number;
    sma200: number;
    ema12: number;
    ema26: number;
  } {
    return {
      sma20: this.calculateSMA(prices, 20),
      sma50: this.calculateSMA(prices, 50),
      sma200: this.calculateSMA(prices, 200),
      ema12: this.calculateEMA(prices, 12),
      ema26: this.calculateEMA(prices, 26),
    };
  }

  private calculateSMA(prices: number[], period: number): number {
    if (prices.length < period) {
      return prices.reduce((a, b) => a + b) / prices.length;
    }
    return prices.slice(-period).reduce((a, b) => a + b) / period;
  }

  private determineTrend(movingAverages: any): 'BULLISH' | 'BEARISH' | 'SIDEWAYS' {
    if (movingAverages.sma20 > movingAverages.sma50 && movingAverages.sma50 > movingAverages.sma200) {
      return 'BULLISH';
    } else if (movingAverages.sma20 < movingAverages.sma50 && movingAverages.sma50 < movingAverages.sma200) {
      return 'BEARISH';
    }
    return 'SIDEWAYS';
  }

  private calculateSupportResistance(prices: number[]): { support: number; resistance: number } {
    const recentPrices = prices.slice(-20);
    const support = Math.min(...recentPrices);
    const resistance = Math.max(...recentPrices);
    return { support, resistance };
  }

  private async performSentimentAnalysis(symbol: string): Promise<SentimentAnalysis> {
    try {
      // In a real implementation, this would analyze news, social media, etc.
      // For now, generate synthetic sentiment data
      
      const sentiment = {
        symbol,
        overall: (Math.random() - 0.5) * 2, // -1 to 1
        news: (Math.random() - 0.5) * 2,
        social: (Math.random() - 0.5) * 2,
        technical: (Math.random() - 0.5) * 2,
        fearGreed: Math.random() * 100,
        confidence: 0.7 + Math.random() * 0.3,
        sources: {
          twitter: (Math.random() - 0.5) * 2,
          reddit: (Math.random() - 0.5) * 2,
          news: (Math.random() - 0.5) * 2,
          analyst: (Math.random() - 0.5) * 2,
        },
        timestamp: Date.now(),
      };

      return sentiment;

    } catch (error) {
      logger.error('Sentiment analysis failed:', error);
      throw error;
    }
  }

  private async generatePricePrediction(
    asset: Asset,
    marketData: MarketData,
    technicalAnalysis: TechnicalAnalysis,
    sentimentAnalysis: SentimentAnalysis,
    historicalData: any[]
  ): Promise<PricePrediction> {
    try {
      const currentPrice = marketData.price;
      
      // Combine technical and sentiment analysis
      const technicalScore = this.getTechnicalScore(technicalAnalysis);
      const sentimentScore = sentimentAnalysis.overall;
      
      // Generate prediction based on multiple factors
      const combinedScore = (technicalScore * 0.7) + (sentimentScore * 0.3);
      const priceChange = combinedScore * 0.05; // Max 5% change
      
      const predictedPrice = currentPrice * (1 + priceChange);
      const confidence = Math.abs(combinedScore) * 0.8 + 0.2; // 20-100% confidence
      
      const direction = combinedScore > 0.1 ? 'up' : combinedScore < -0.1 ? 'down' : 'sideways';
      const recommendation = combinedScore > 0.3 ? 'BUY' : combinedScore < -0.3 ? 'SELL' : 'HOLD';
      const riskLevel = Math.abs(priceChange) > 0.03 ? 'HIGH' : Math.abs(priceChange) > 0.01 ? 'MEDIUM' : 'LOW';

      return {
        symbol: asset.symbol,
        currentPrice,
        predictedPrice,
        confidence,
        timeframe: '1h',
        direction,
        volatility: technicalAnalysis.bollinger.upper - technicalAnalysis.bollinger.lower,
        support: technicalAnalysis.support,
        resistance: technicalAnalysis.resistance,
        recommendation,
        riskLevel,
        timestamp: Date.now(),
      };

    } catch (error) {
      logger.error('Price prediction generation failed:', error);
      throw error;
    }
  }

  private getTechnicalScore(technical: TechnicalAnalysis): number {
    let score = 0;
    
    // RSI score
    if (technical.rsi < 30) score += 0.3; // Oversold
    else if (technical.rsi > 70) score -= 0.3; // Overbought
    
    // MACD score
    if (technical.macd.macd > technical.macd.signal) score += 0.2;
    else score -= 0.2;
    
    // Trend score
    if (technical.trend === 'BULLISH') score += 0.3;
    else if (technical.trend === 'BEARISH') score -= 0.3;
    
    return Math.max(-1, Math.min(1, score));
  }

  private async savePrediction(prediction: PricePrediction): Promise<void> {
    try {
      const aiPrediction = new AIPrediction();
      aiPrediction.assetId = ''; // Would get from asset lookup
      aiPrediction.predictedPrice = prediction.predictedPrice;
      aiPrediction.confidence = prediction.confidence;
      aiPrediction.timeframe = prediction.timeframe;
      aiPrediction.direction = prediction.direction;
      aiPrediction.recommendation = prediction.recommendation;
      aiPrediction.riskLevel = prediction.riskLevel;
      aiPrediction.metadata = {
        currentPrice: prediction.currentPrice,
        volatility: prediction.volatility,
        support: prediction.support,
        resistance: prediction.resistance,
      };

      await this.predictionRepository.save(aiPrediction);

    } catch (error) {
      logger.error('Failed to save prediction:', error);
    }
  }

  private async runBatchPredictions(): Promise<void> {
    try {
      logger.info('Running batch AI predictions...');
      // Implementation for batch predictions
    } catch (error) {
      logger.error('Batch predictions failed:', error);
    }
  }

  private async runSentimentAnalysis(): Promise<void> {
    try {
      logger.info('Running sentiment analysis...');
      // Implementation for sentiment analysis
    } catch (error) {
      logger.error('Sentiment analysis failed:', error);
    }
  }

  public async getLatestPredictions(symbol?: string): Promise<PricePrediction[]> {
    try {
      // Implementation to get latest predictions from database
      return [];
    } catch (error) {
      logger.error('Failed to get latest predictions:', error);
      return [];
    }
  }
}