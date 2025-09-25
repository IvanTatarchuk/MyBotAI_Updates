import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Trader {
  id: string;
  name: string;
  avatar: string;
  followers: number;
  following: number;
  winRate: number;
  totalReturn: number;
  riskScore: number;
  verified: boolean;
  bio: string;
  specializations: string[];
}

export interface Trade {
  id: string;
  traderId: string;
  symbol: string;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  timestamp: string;
  profitLoss?: number;
  status: 'active' | 'closed' | 'pending';
}

export interface SocialState {
  traders: Trader[];
  trades: Trade[];
  followedTraders: string[];
  myTrades: Trade[];
  isLoading: boolean;
  feed: (Trade | { type: 'achievement'; traderId: string; achievement: string })[];
}

const initialState: SocialState = {
  traders: [
    {
      id: '1',
      name: 'Sarah Chen',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah',
      followers: 15420,
      following: 180,
      winRate: 73.5,
      totalReturn: 45.8,
      riskScore: 6.2,
      verified: true,
      bio: 'Tech stocks specialist with 8+ years experience',
      specializations: ['Technology', 'Growth Stocks', 'Options Trading'],
    },
    {
      id: '2',
      name: 'Marcus Rodriguez',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Marcus',
      followers: 8950,
      following: 95,
      winRate: 68.2,
      totalReturn: 32.4,
      riskScore: 4.8,
      verified: true,
      bio: 'Conservative investor focused on dividend stocks',
      specializations: ['Dividend Investing', 'Blue Chip Stocks', 'ETFs'],
    },
    {
      id: '3',
      name: 'Luna Kim',
      avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Luna',
      followers: 23100,
      following: 320,
      winRate: 79.1,
      totalReturn: 67.3,
      riskScore: 7.8,
      verified: true,
      bio: 'Crypto trading expert and DeFi enthusiast',
      specializations: ['Cryptocurrency', 'DeFi', 'NFTs', 'Web3'],
    },
  ],
  trades: [
    {
      id: '1',
      traderId: '1',
      symbol: 'AAPL',
      type: 'buy',
      quantity: 50,
      price: 175.50,
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      status: 'active',
    },
    {
      id: '2',
      traderId: '2',
      symbol: 'JNJ',
      type: 'buy',
      quantity: 25,
      price: 165.00,
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      status: 'active',
    },
    {
      id: '3',
      traderId: '3',
      symbol: 'ETH',
      type: 'buy',
      quantity: 2.5,
      price: 2800,
      timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      status: 'active',
    },
  ],
  followedTraders: ['1', '3'],
  myTrades: [
    {
      id: 'my1',
      traderId: '1',
      symbol: 'TSLA',
      type: 'buy',
      quantity: 10,
      price: 245.00,
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      profitLoss: 50.00,
      status: 'closed',
    },
  ],
  isLoading: false,
  feed: [
    {
      type: 'achievement',
      traderId: '1',
      achievement: 'Reached 15,000 followers!',
    },
    {
      id: '1',
      traderId: '1',
      symbol: 'AAPL',
      type: 'buy',
      quantity: 50,
      price: 175.50,
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      status: 'active',
    },
    {
      id: '3',
      traderId: '3',
      symbol: 'ETH',
      type: 'buy',
      quantity: 2.5,
      price: 2800,
      timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      status: 'active',
    },
  ],
};

const socialSlice = createSlice({
  name: 'social',
  initialState,
  reducers: {
    followTrader: (state, action: PayloadAction<string>) => {
      if (!state.followedTraders.includes(action.payload)) {
        state.followedTraders.push(action.payload);
      }
    },
    unfollowTrader: (state, action: PayloadAction<string>) => {
      state.followedTraders = state.followedTraders.filter(id => id !== action.payload);
    },
    addTrade: (state, action: PayloadAction<Trade>) => {
      state.trades.push(action.payload);
      if (action.payload.traderId === '1') { // Assuming user ID is '1'
        state.myTrades.push(action.payload);
      }
    },
    updateTrade: (state, action: PayloadAction<Trade>) => {
      const index = state.trades.findIndex(trade => trade.id === action.payload.id);
      if (index !== -1) {
        state.trades[index] = action.payload;
      }
      const myTradeIndex = state.myTrades.findIndex(trade => trade.id === action.payload.id);
      if (myTradeIndex !== -1) {
        state.myTrades[myTradeIndex] = action.payload;
      }
    },
    addFeedItem: (state, action: PayloadAction<Trade | { type: 'achievement'; traderId: string; achievement: string }>) => {
      state.feed.unshift(action.payload);
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
});

export const { followTrader, unfollowTrader, addTrade, updateTrade, addFeedItem, setLoading } = socialSlice.actions;
export default socialSlice.reducer;