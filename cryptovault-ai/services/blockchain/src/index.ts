import express from 'express';
import dotenv from 'dotenv';
import { ExchangeService } from './services/exchangeService';
import { BlockchainService } from './services/blockchainService';
import { PriceAggregator } from './services/priceAggregator';
import { WalletService } from './services/walletService';
import { logger } from './utils/logger';

dotenv.config();

const app = express();
app.use(express.json());

const PORT = process.env.BLOCKCHAIN_SERVICE_PORT || 5001;

// Initialize services
const exchangeService = new ExchangeService();
const blockchainService = new BlockchainService();
const priceAggregator = new PriceAggregator();
const walletService = new WalletService();

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'blockchain-service' });
});

// Exchange endpoints
app.get('/exchanges', async (req, res) => {
  try {
    const exchanges = await exchangeService.getAvailableExchanges();
    res.json(exchanges);
  } catch (error) {
    logger.error('Error fetching exchanges:', error);
    res.status(500).json({ error: 'Failed to fetch exchanges' });
  }
});

app.post('/exchanges/connect', async (req, res) => {
  try {
    const { exchange, apiKey, apiSecret } = req.body;
    const result = await exchangeService.connectExchange(exchange, apiKey, apiSecret);
    res.json(result);
  } catch (error) {
    logger.error('Error connecting exchange:', error);
    res.status(500).json({ error: 'Failed to connect exchange' });
  }
});

app.get('/exchanges/:exchange/balances', async (req, res) => {
  try {
    const { exchange } = req.params;
    const { userId } = req.query;
    const balances = await exchangeService.getBalances(exchange, userId as string);
    res.json(balances);
  } catch (error) {
    logger.error('Error fetching balances:', error);
    res.status(500).json({ error: 'Failed to fetch balances' });
  }
});

// Price endpoints
app.get('/prices/:symbol', async (req, res) => {
  try {
    const { symbol } = req.params;
    const price = await priceAggregator.getPrice(symbol);
    res.json(price);
  } catch (error) {
    logger.error('Error fetching price:', error);
    res.status(500).json({ error: 'Failed to fetch price' });
  }
});

app.get('/prices/multi', async (req, res) => {
  try {
    const { symbols } = req.query;
    const symbolArray = (symbols as string).split(',');
    const prices = await priceAggregator.getMultiplePrices(symbolArray);
    res.json(prices);
  } catch (error) {
    logger.error('Error fetching prices:', error);
    res.status(500).json({ error: 'Failed to fetch prices' });
  }
});

// Blockchain endpoints
app.get('/blockchain/:chain/transaction/:txHash', async (req, res) => {
  try {
    const { chain, txHash } = req.params;
    const transaction = await blockchainService.getTransaction(chain, txHash);
    res.json(transaction);
  } catch (error) {
    logger.error('Error fetching transaction:', error);
    res.status(500).json({ error: 'Failed to fetch transaction' });
  }
});

app.get('/blockchain/:chain/address/:address/balance', async (req, res) => {
  try {
    const { chain, address } = req.params;
    const balance = await blockchainService.getBalance(chain, address);
    res.json({ balance });
  } catch (error) {
    logger.error('Error fetching balance:', error);
    res.status(500).json({ error: 'Failed to fetch balance' });
  }
});

// Wallet endpoints
app.post('/wallet/create', async (req, res) => {
  try {
    const { userId, chain } = req.body;
    const wallet = await walletService.createWallet(userId, chain);
    res.json(wallet);
  } catch (error) {
    logger.error('Error creating wallet:', error);
    res.status(500).json({ error: 'Failed to create wallet' });
  }
});

app.post('/wallet/import', async (req, res) => {
  try {
    const { userId, privateKey, chain } = req.body;
    const wallet = await walletService.importWallet(userId, privateKey, chain);
    res.json(wallet);
  } catch (error) {
    logger.error('Error importing wallet:', error);
    res.status(500).json({ error: 'Failed to import wallet' });
  }
});

app.listen(PORT, () => {
  logger.info(`Blockchain service running on port ${PORT}`);
});