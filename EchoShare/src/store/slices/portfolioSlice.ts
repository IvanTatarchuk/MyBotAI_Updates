import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface PortfolioItem {
  id: string;
  symbol: string;
  name: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  change: number;
  changePercent: number;
  value: number;
  type: 'stock' | 'crypto' | 'etf' | 'bond';
}

export interface PortfolioState {
  items: PortfolioItem[];
  totalValue: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
  isLoading: boolean;
}

const initialState: PortfolioState = {
  items: [
    {
      id: '1',
      symbol: 'AAPL',
      name: 'Apple Inc.',
      quantity: 10,
      averagePrice: 150.00,
      currentPrice: 175.50,
      change: 25.50,
      changePercent: 17.00,
      value: 1755.00,
      type: 'stock',
    },
    {
      id: '2',
      symbol: 'BTC',
      name: 'Bitcoin',
      quantity: 0.5,
      averagePrice: 45000,
      currentPrice: 52000,
      change: 7000,
      changePercent: 15.56,
      value: 26000,
      type: 'crypto',
    },
    {
      id: '3',
      symbol: 'SPY',
      name: 'SPDR S&P 500 ETF Trust',
      quantity: 5,
      averagePrice: 400.00,
      currentPrice: 425.00,
      change: 25.00,
      changePercent: 6.25,
      value: 2125.00,
      type: 'etf',
    },
  ],
  totalValue: 6480.00,
  totalGainLoss: 7050.50,
  totalGainLossPercent: 12.34,
  isLoading: false,
};

const portfolioSlice = createSlice({
  name: 'portfolio',
  initialState,
  reducers: {
    addPortfolioItem: (state, action: PayloadAction<PortfolioItem>) => {
      state.items.push(action.payload);
      state.totalValue += action.payload.value;
    },
    removePortfolioItem: (state, action: PayloadAction<string>) => {
      const item = state.items.find(item => item.id === action.payload);
      if (item) {
        state.totalValue -= item.value;
        state.items = state.items.filter(item => item.id !== action.payload);
      }
    },
    updatePortfolioItem: (state, action: PayloadAction<PortfolioItem>) => {
      const index = state.items.findIndex(item => item.id === action.payload.id);
      if (index !== -1) {
        const oldValue = state.items[index].value;
        state.items[index] = action.payload;
        state.totalValue = state.totalValue - oldValue + action.payload.value;
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
});

export const { addPortfolioItem, removePortfolioItem, updatePortfolioItem, setLoading } = portfolioSlice.actions;
export default portfolioSlice.reducer;