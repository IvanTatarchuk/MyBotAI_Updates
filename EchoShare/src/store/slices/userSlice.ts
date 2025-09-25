import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  level: number;
  experience: number;
  badges: string[];
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
  investmentGoals: string[];
  subscription: 'free' | 'premium' | 'pro';
}

export interface UserState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const initialState: UserState = {
  user: {
    id: '1',
    name: 'Alex Johnson',
    email: 'alex.johnson@example.com',
    avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex',
    level: 15,
    experience: 2450,
    badges: ['Early Adopter', 'Portfolio Master', 'Social Trader'],
    riskTolerance: 'moderate',
    investmentGoals: ['Retirement', 'Growth', 'Income'],
    subscription: 'premium',
  },
  isAuthenticated: true,
  isLoading: false,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    login: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
    },
    updateUser: (state, action: PayloadAction<Partial<User>>) => {
      if (state.user) {
        state.user = { ...state.user, ...action.payload };
      }
    },
    updateExperience: (state, action: PayloadAction<number>) => {
      if (state.user) {
        state.user.experience += action.payload;
        state.user.level = Math.floor(state.user.experience / 200) + 1;
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
});

export const { login, logout, updateUser, updateExperience, setLoading } = userSlice.actions;
export default userSlice.reducer;