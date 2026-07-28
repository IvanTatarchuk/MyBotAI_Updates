import ccxt from 'ccxt';
import { logger } from '../utils/logger';
import { encrypt, decrypt } from '../utils/crypto';

export class ExchangeService {
  private exchanges: Map<string, ccxt.Exchange> = new Map();

  async getAvailableExchanges() {
    return [
      { id: 'binance', name: 'Binance', supported: true },
      { id: 'coinbase', name: 'Coinbase', supported: true },
      { id: 'kraken', name: 'Kraken', supported: true },
      { id: 'bitfinex', name: 'Bitfinex', supported: true },
      { id: 'huobi', name: 'Huobi', supported: true },
      { id: 'kucoin', name: 'KuCoin', supported: true },
      { id: 'okx', name: 'OKX', supported: true },
      { id: 'bybit', name: 'Bybit', supported: true },
    ];
  }

  async connectExchange(exchangeId: string, apiKey: string, apiSecret: string) {
    try {
      const ExchangeClass = ccxt[exchangeId as keyof typeof ccxt] as any;
      
      if (!ExchangeClass) {
        throw new Error(`Exchange ${exchangeId} not supported`);
      }

      const exchange = new ExchangeClass({
        apiKey,
        secret: apiSecret,
        enableRateLimit: true,
      });

      // Test connection
      await exchange.loadMarkets();
      const balance = await exchange.fetchBalance();

      // Encrypt and store credentials
      const encryptedKey = encrypt(apiKey);
      const encryptedSecret = encrypt(apiSecret);

      // Store in database (simplified for demo)
      logger.info(`Connected to ${exchangeId} successfully`);

      return {
        success: true,
        exchange: exchangeId,
        totalBalance: this.calculateTotalBalance(balance),
      };
    } catch (error) {
      logger.error(`Failed to connect to ${exchangeId}:`, error);
      throw error;
    }
  }

  async getBalances(exchangeId: string, userId: string) {
    try {
      // In production, retrieve encrypted credentials from database
      const exchange = this.exchanges.get(`${userId}-${exchangeId}`);
      
      if (!exchange) {
        throw new Error('Exchange not connected');
      }

      const balance = await exchange.fetchBalance();
      
      return {
        exchange: exchangeId,
        balances: this.formatBalances(balance),
        totalValue: this.calculateTotalBalance(balance),
      };
    } catch (error) {
      logger.error(`Failed to fetch balances from ${exchangeId}:`, error);
      throw error;
    }
  }

  async executeTrade(exchangeId: string, userId: string, order: any) {
    try {
      const exchange = this.exchanges.get(`${userId}-${exchangeId}`);
      
      if (!exchange) {
        throw new Error('Exchange not connected');
      }

      const result = await exchange.createOrder(
        order.symbol,
        order.type,
        order.side,
        order.amount,
        order.price
      );

      return result;
    } catch (error) {
      logger.error(`Failed to execute trade on ${exchangeId}:`, error);
      throw error;
    }
  }

  private formatBalances(balance: any) {
    const formatted: any[] = [];
    
    for (const [currency, amount] of Object.entries(balance.total)) {
      if (amount && (amount as number) > 0) {
        formatted.push({
          currency,
          free: balance.free[currency] || 0,
          used: balance.used[currency] || 0,
          total: amount,
        });
      }
    }

    return formatted;
  }

  private calculateTotalBalance(balance: any) {
    // In production, would calculate USD value of all holdings
    let total = 0;
    
    for (const [currency, amount] of Object.entries(balance.total)) {
      if (amount && (amount as number) > 0) {
        // Would multiply by current price
        total += amount as number;
      }
    }

    return total;
  }
}