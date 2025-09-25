import { EventEmitter } from 'events';
import ccxt from 'ccxt';
import { logger } from '../utils/logger';
import { Asset } from '../models/Asset';
import { Transaction } from '../models/Transaction';
import { AppDataSource } from '../config/database';
import { WebSocketService } from './WebSocketService';
import { AIService } from './AIService';

export interface MarketData {
  symbol: string;
  price: number;
  volume: number;
  timestamp: number;
  bid: number;
  ask: number;
  high: number;
  low: number;
}

export interface OrderBook {
  symbol: string;
  bids: [number, number][];
  asks: [number, number][];
  timestamp: number;
}

export interface TradingSignal {
  symbol: string;
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  price: number;
  quantity?: number;
  stopLoss?: number;
  takeProfit?: number;
  reason: string;
  timestamp: number;
}

export class TradingEngine extends EventEmitter {
  private exchanges: Map<string, ccxt.Exchange> = new Map();
  private marketData: Map<string, MarketData> = new Map();
  private orderBooks: Map<string, OrderBook> = new Map();
  private isRunning = false;
  private wsService?: WebSocketService;
  private aiService?: AIService;
  private assetRepository = AppDataSource.getRepository(Asset);
  private transactionRepository = AppDataSource.getRepository(Transaction);

  constructor() {
    super();
    this.initializeExchanges();
  }

  private initializeExchanges(): void {
    const exchangeConfigs = [
      {
        id: 'binance',
        exchange: new ccxt.binance({
          apiKey: process.env.BINANCE_API_KEY,
          secret: process.env.BINANCE_SECRET,
          sandbox: process.env.NODE_ENV !== 'production',
          enableRateLimit: true,
        }),
      },
      {
        id: 'coinbase',
        exchange: new ccxt.coinbasepro({
          apiKey: process.env.COINBASE_API_KEY,
          passphrase: process.env.COINBASE_PASSPHRASE,
          secret: process.env.COINBASE_SECRET,
          sandbox: process.env.NODE_ENV !== 'production',
          enableRateLimit: true,
        }),
      },
      {
        id: 'kraken',
        exchange: new ccxt.kraken({
          apiKey: process.env.KRAKEN_API_KEY,
          secret: process.env.KRAKEN_SECRET,
          sandbox: process.env.NODE_ENV !== 'production',
          enableRateLimit: true,
        }),
      },
    ];

    exchangeConfigs.forEach(({ id, exchange }) => {
      this.exchanges.set(id, exchange);
      logger.info(`Initialized exchange: ${id}`);
    });
  }

  public async initialize(): Promise<void> {
    try {
      logger.info('Initializing Trading Engine...');

      // Initialize AI Service
      this.aiService = new AIService();
      await this.aiService.initialize();

      // Load supported assets
      await this.loadAssets();

      // Start market data collection
      this.startMarketDataCollection();

      // Start AI prediction updates
      this.startAIPredictions();

      this.isRunning = true;
      logger.info('Trading Engine initialized successfully');

    } catch (error) {
      logger.error('Failed to initialize Trading Engine:', error);
      throw error;
    }
  }

  private async loadAssets(): Promise<void> {
    try {
      const assets = await this.assetRepository.find({
        where: { status: 'active', isTradable: true }
      });

      logger.info(`Loaded ${assets.length} tradable assets`);
      
      // Subscribe to market data for all assets
      for (const asset of assets) {
        await this.subscribeToMarketData(asset.symbol);
      }

    } catch (error) {
      logger.error('Failed to load assets:', error);
    }
  }

  private async subscribeToMarketData(symbol: string): Promise<void> {
    try {
      // Subscribe to real-time market data from exchanges
      for (const [exchangeId, exchange] of this.exchanges) {
        if (exchange.has['ws']) {
          await this.subscribeToWebSocket(exchangeId, exchange, symbol);
        }
      }
    } catch (error) {
      logger.error(`Failed to subscribe to market data for ${symbol}:`, error);
    }
  }

  private async subscribeToWebSocket(
    exchangeId: string,
    exchange: ccxt.Exchange,
    symbol: string
  ): Promise<void> {
    try {
      // Implementation would depend on the specific exchange WebSocket API
      // This is a simplified example
      logger.info(`Subscribing to ${exchangeId} WebSocket for ${symbol}`);
      
      // In a real implementation, you would:
      // 1. Connect to the exchange's WebSocket API
      // 2. Subscribe to ticker, orderbook, and trade streams
      // 3. Handle incoming data and update local state
      // 4. Broadcast updates to connected clients

    } catch (error) {
      logger.error(`WebSocket subscription failed for ${exchangeId}:`, error);
    }
  }

  private startMarketDataCollection(): void {
    setInterval(async () => {
      if (!this.isRunning) return;

      try {
        await this.updateMarketData();
      } catch (error) {
        logger.error('Market data collection error:', error);
      }
    }, 5000); // Update every 5 seconds
  }

  private async updateMarketData(): Promise<void> {
    try {
      const assets = await this.assetRepository.find({
        where: { status: 'active' }
      });

      for (const asset of assets) {
        await this.fetchAssetPrice(asset);
      }

      // Broadcast market data updates to WebSocket clients
      if (this.wsService) {
        this.wsService.broadcastMarketData(Array.from(this.marketData.values()));
      }

    } catch (error) {
      logger.error('Failed to update market data:', error);
    }
  }

  private async fetchAssetPrice(asset: Asset): Promise<void> {
    try {
      // Try to get price from multiple exchanges
      for (const [exchangeId, exchange] of this.exchanges) {
        try {
          const ticker = await exchange.fetchTicker(asset.symbol);
          
          const marketData: MarketData = {
            symbol: asset.symbol,
            price: ticker.last || 0,
            volume: ticker.quoteVolume || 0,
            timestamp: Date.now(),
            bid: ticker.bid || 0,
            ask: ticker.ask || 0,
            high: ticker.high || 0,
            low: ticker.low || 0,
          };

          this.marketData.set(asset.symbol, marketData);

          // Update asset in database
          await this.assetRepository.update(asset.id, {
            currentPrice: marketData.price,
            volume24h: marketData.volume,
            high24h: marketData.high,
            low24h: marketData.low,
            lastPriceUpdate: new Date(),
          });

          break; // Use first successful exchange
        } catch (exchangeError) {
          logger.warn(`Failed to fetch ${asset.symbol} from ${exchangeId}:`, exchangeError);
          continue;
        }
      }

    } catch (error) {
      logger.error(`Failed to fetch price for ${asset.symbol}:`, error);
    }
  }

  private startAIPredictions(): void {
    setInterval(async () => {
      if (!this.isRunning || !this.aiService) return;

      try {
        await this.generateAIPredictions();
      } catch (error) {
        logger.error('AI prediction generation error:', error);
      }
    }, 60000); // Generate predictions every minute
  }

  private async generateAIPredictions(): Promise<void> {
    try {
      const assets = await this.assetRepository.find({
        where: { status: 'active', isFeatured: true },
        take: 50 // Limit to top 50 assets
      });

      for (const asset of assets) {
        const marketData = this.marketData.get(asset.symbol);
        if (!marketData) continue;

        // Generate AI prediction
        const prediction = await this.aiService.predictPrice(asset, marketData);
        
        if (prediction) {
          // Emit prediction event
          this.emit('prediction', prediction);
          
          // Broadcast to WebSocket clients
          if (this.wsService) {
            this.wsService.broadcastPrediction(prediction);
          }
        }
      }

    } catch (error) {
      logger.error('Failed to generate AI predictions:', error);
    }
  }

  public async executeTrade(
    userId: string,
    symbol: string,
    type: 'buy' | 'sell',
    quantity: number,
    price?: number
  ): Promise<Transaction> {
    try {
      const asset = await this.assetRepository.findOne({
        where: { symbol, status: 'active' }
      });

      if (!asset) {
        throw new Error(`Asset ${symbol} not found or not tradable`);
      }

      const marketData = this.marketData.get(symbol);
      if (!marketData) {
        throw new Error(`No market data available for ${symbol}`);
      }

      const executionPrice = price || marketData.price;
      const totalAmount = quantity * executionPrice;
      const feeRate = 0.001; // 0.1% fee
      const fees = totalAmount * feeRate;

      // Create transaction record
      const transaction = new Transaction();
      transaction.userId = userId;
      transaction.assetId = asset.id;
      transaction.type = type.toUpperCase() as any;
      transaction.quantity = quantity;
      transaction.filledQuantity = quantity;
      transaction.averagePrice = executionPrice;
      transaction.totalAmount = totalAmount;
      transaction.fees = fees;
      transaction.feeRate = feeRate;
      transaction.status = 'completed';
      transaction.completedAt = new Date();

      await this.transactionRepository.save(transaction);

      // Update portfolio
      await this.updatePortfolio(userId, asset.id, type, quantity, executionPrice);

      logger.info(`Trade executed: ${type} ${quantity} ${symbol} at ${executionPrice}`);

      return transaction;

    } catch (error) {
      logger.error('Trade execution failed:', error);
      throw error;
    }
  }

  private async updatePortfolio(
    userId: string,
    assetId: string,
    type: string,
    quantity: number,
    price: number
  ): Promise<void> {
    // Implementation would update user's portfolio
    // This is a simplified example
    logger.info(`Updating portfolio for user ${userId}`);
  }

  public getMarketData(symbol?: string): MarketData | MarketData[] {
    if (symbol) {
      return this.marketData.get(symbol);
    }
    return Array.from(this.marketData.values());
  }

  public getOrderBook(symbol: string): OrderBook | undefined {
    return this.orderBooks.get(symbol);
  }

  public setWebSocketService(wsService: WebSocketService): void {
    this.wsService = wsService;
  }

  public stop(): void {
    this.isRunning = false;
    logger.info('Trading Engine stopped');
  }
}