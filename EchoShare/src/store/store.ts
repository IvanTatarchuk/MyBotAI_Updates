import { configureStore } from '@reduxjs/toolkit';
import portfolioSlice from './slices/portfolioSlice';
import userSlice from './slices/userSlice';
import marketSlice from './slices/marketSlice';
import socialSlice from './slices/socialSlice';

export const store = configureStore({
  reducer: {
    portfolio: portfolioSlice,
    user: userSlice,
    market: marketSlice,
    social: socialSlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST', 'persist/REHYDRATE'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;