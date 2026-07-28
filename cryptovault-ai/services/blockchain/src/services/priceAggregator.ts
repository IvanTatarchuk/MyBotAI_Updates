import axios from 'axios';
import Redis from 'ioredis';
import { logger } from '../utils/logger';

export class PriceAggregator {
  private redis: Redis;
  private sources = [
    { name: 'coingecko', weight: 0.3 },
    { name: 'coinmarketcap', weight: 0.3 },
    { name: 'binance', weight: 0.2 },
    { name: 'coinbase', weight: 0.2 },
  ];

  constructor() {
    this.redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
  }

  async getPrice(symbol: string): Promise<any> {
    try {
      // Check cache first
      const cached = await this.redis.get(`price:${symbol}`);
      if (cached) {
        return JSON.parse(cached);
      }

      // Fetch from multiple sources
      const prices = await Promise.all([
        this.fetchFromCoinGecko(symbol),
        this.fetchFromBinance(symbol),
        this.fetchFromCoinbase(symbol),
      ]);

      // Calculate weighted average
      const aggregatedPrice = this.calculateWeightedPrice(prices);

      // Cache for 30 seconds
      await this.redis.setex(`price:${symbol}`, 30, JSON.stringify(aggregatedPrice));

      return aggregatedPrice;
    } catch (error) {
      logger.error(`Error fetching price for ${symbol}:`, error);
      throw error;
    }
  }

  async getMultiplePrices(symbols: string[]): Promise<any> {
    try {
      const prices = await Promise.all(
        symbols.map(symbol => this.getPrice(symbol))
      );

      return symbols.reduce((acc, symbol, index) => {
        acc[symbol] = prices[index];
        return acc;
      }, {} as any);
    } catch (error) {
      logger.error('Error fetching multiple prices:', error);
      throw error;
    }
  }

  private async fetchFromCoinGecko(symbol: string) {
    try {
      const response = await axios.get(
        `https://api.coingecko.com/api/v3/simple/price`,
        {
          params: {
            ids: symbol.toLowerCase(),
            vs_currencies: 'usd',
            include_24hr_change: true,
            include_market_cap: true,
            include_24hr_vol: true,
          },
        }
      );

      const data = response.data[symbol.toLowerCase()];
      return {
        source: 'coingecko',
        price: data.usd,
        change24h: data.usd_24h_change,
        marketCap: data.usd_market_cap,
        volume24h: data.usd_24h_vol,
      };
    } catch (error) {
      logger.error('CoinGecko API error:', error);
      return null;
    }
  }

  private async fetchFromBinance(symbol: string) {
    try {
      const response = await axios.get(
        `https://api.binance.com/api/v3/ticker/24hr`,
        {
          params: { symbol: `${symbol.toUpperCase()}USDT` },
        }
      );

      return {
        source: 'binance',
        price: parseFloat(response.data.lastPrice),
        change24h: parseFloat(response.data.priceChangePercent),
        volume24h: parseFloat(response.data.volume) * parseFloat(response.data.lastPrice),
      };
    } catch (error) {
      logger.error('Binance API error:', error);
      return null;
    }
  }

  private async fetchFromCoinbase(symbol: string) {
    try {
      const response = await axios.get(
        `https://api.coinbase.com/v2/exchange-rates`,
        {
          params: { currency: symbol.toUpperCase() },
        }
      );

      const rate = response.data.data.rates.USD;
      return {
        source: 'coinbase',
        price: parseFloat(rate),
      };
    } catch (error) {
      logger.error('Coinbase API error:', error);
      return null;
    }
  }

  private calculateWeightedPrice(prices: any[]) {
    const validPrices = prices.filter(p => p && p.price);
    
    if (validPrices.length === 0) {
      throw new Error('No valid prices available');
    }

    let weightedSum = 0;
    let totalWeight = 0;
    let totalVolume = 0;
    let totalMarketCap = 0;
    let changeSum = 0;
    let changeCount = 0;

    validPrices.forEach(priceData => {
      const source = this.sources.find(s => s.name === priceData.source);
      const weight = source?.weight || 0.25;
      
      weightedSum += priceData.price * weight;
      totalWeight += weight;

      if (priceData.volume24h) totalVolume += priceData.volume24h;
      if (priceData.marketCap) totalMarketCap = Math.max(totalMarketCap, priceData.marketCap);
      if (priceData.change24h !== undefined) {
        changeSum += priceData.change24h;
        changeCount++;
      }
    });

    return {
      price: weightedSum / totalWeight,
      change24h: changeCount > 0 ? changeSum / changeCount : 0,
      volume24h: totalVolume,
      marketCap: totalMarketCap,
      sources: validPrices.length,
      timestamp: new Date().toISOString(),
    };
  }

  async getHistoricalPrices(symbol: string, days: number = 7) {
    try {
      const response = await axios.get(
        `https://api.coingecko.com/api/v3/coins/${symbol.toLowerCase()}/market_chart`,
        {
          params: {
            vs_currency: 'usd',
            days: days,
          },
        }
      );

      return {
        prices: response.data.prices.map((p: any) => ({
          timestamp: new Date(p[0]),
          price: p[1],
        })),
        marketCaps: response.data.market_caps,
        volumes: response.data.total_volumes,
      };
    } catch (error) {
      logger.error(`Error fetching historical prices for ${symbol}:`, error);
      throw error;
    }
  }
}