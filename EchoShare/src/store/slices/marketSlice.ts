import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  high24h: number;
  low24h: number;
  lastUpdated: string;
}

export interface MarketState {
  indices: MarketData[];
  crypto: MarketData[];
  trending: MarketData[];
  watchlist: string[];
  isLoading: boolean;
}

const initialState: MarketState = {
  indices: [
    {
      symbol: 'S&P 500',
      price: 4250.00,
      change: 25.50,
      changePercent: 0.60,
      volume: 3500000000,
      marketCap: 35000000000000,
      high24h: 4275.00,
      low24h: 4220.00,
      lastUpdated: new Date().toISOString(),
    },
    {
      symbol: 'NASDAQ',
      price: 13200.00,
      change: 85.30,
      changePercent: 0.65,
      volume: 2800000000,
      marketCap: 18000000000000,
      high24h: 13300.00,
      low24h: 13100.00,
      lastUpdated: new Date().toISOString(),
    },
    {
      symbol: 'DOW JONES',
      price: 33800.00,
      change: -45.20,
      changePercent: -0.13,
      volume: 320000000,
      marketCap: 12000000000000,
      high24h: 33950.00,
      low24h: 33750.00,
      lastUpdated: new Date().toISOString(),
    },
  ],
  crypto: [
    {
      symbol: 'BTC',
      price: 52000,
      change: 2100,
      changePercent: 4.21,
      volume: 25000000000,
      marketCap: 1000000000000,
      high24h: 53000,
      low24h: 49500,
      lastUpdated: new Date().toISOString(),
    },
    {
      symbol: 'ETH',
      price: 2800,
      change: 120,
      changePercent: 4.48,
      volume: 15000000000,
      marketCap: 350000000000,
      high24h: 2900,
      low24h: 2650,
      lastUpdated: new Date().toISOString(),
    },
    {
      symbol: 'ADA',
      price: 0.45,
      change: 0.03,
      changePercent: 7.14,
      volume: 2000000000,
      marketCap: 16000000000,
      high24h: 0.48,
      low24h: 0.42,
      lastUpdated: new Date().toISOString(),
    },
  ],
  trending: [
    {
      symbol: 'TSLA',
      price: 245.50,
      change: 15.30,
      changePercent: 6.65,
      volume: 85000000,
      marketCap: 780000000000,
      high24h: 250.00,
      low24h: 230.00,
      lastUpdated: new Date().toISOString(),
    },
    {
      symbol: 'NVDA',
      price: 875.00,
      change: 45.50,
      changePercent: 5.49,
      volume: 45000000,
      marketCap: 2150000000000,
      high24h: 890.00,
      low24h: 830.00,
      lastUpdated: new Date().toISOString(),
    },
  ],
  watchlist: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META'],
  isLoading: false,
};

const marketSlice = createSlice({
  name: 'market',
  initialState,
  reducers: {
    updateMarketData: (state, action: PayloadAction<{ type: 'indices' | 'crypto' | 'trending'; data: MarketData[] }>) => {
      state[action.payload.type] = action.payload.data;
    },
    addToWatchlist: (state, action: PayloadAction<string>) => {
      if (!state.watchlist.includes(action.payload)) {
        state.watchlist.push(action.payload);
      }
    },
    removeFromWatchlist: (state, action: PayloadAction<string>) => {
      state.watchlist = state.watchlist.filter(symbol => symbol !== action.payload);
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
});

export const { updateMarketData, addToWatchlist, removeFromWatchlist, setLoading } = marketSlice.actions;
export default marketSlice.reducer;