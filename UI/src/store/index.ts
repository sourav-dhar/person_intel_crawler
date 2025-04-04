import { configureStore } from '@reduxjs/toolkit';
import searchReducer from './searchSlice';
import resultReducer from './resultSlice';
import authReducer from './authSlice';

export const store = configureStore({
  reducer: {
    search: searchReducer,
    result: resultReducer,
    auth: authReducer
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore these action types
        ignoredActions: ['persist/PERSIST'],
        // Ignore these field paths in all actions
        ignoredActionPaths: ['meta.arg', 'payload.timestamp'],
        // Ignore these paths in the state
        ignoredPaths: [
          'search.recentSearches',
          'result.result',
          'result.status'
        ],
      },
    }),
});

// Types for Redux hooks
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;