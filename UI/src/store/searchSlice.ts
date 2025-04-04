import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { SearchRequest, SearchResponse, SearchSummary } from '../types/search';
import { api } from '../services/api';

interface SearchState {
  loading: boolean;
  error: string | null;
  recentSearches: SearchSummary[];
}

const initialState: SearchState = {
  loading: false,
  error: null,
  recentSearches: []
};

// Async thunks
export const startSearch = createAsyncThunk<
  SearchResponse,
  SearchRequest,
  { rejectValue: string }
>('search/startSearch', async (searchData, { rejectWithValue }) => {
  try {
    const response = await api.post<SearchResponse>('/search', searchData);
    return response.data;
  } catch (error) {
    if (error instanceof Error) {
      return rejectWithValue(error.message);
    }
    return rejectWithValue('An unknown error occurred');
  }
});

export const fetchRecentSearches = createAsyncThunk<
  SearchSummary[],
  void,
  { rejectValue: string }
>('search/fetchRecentSearches', async (_, { rejectWithValue }) => {
  try {
    // This would typically be a real API endpoint
    // For this example, we'll simulate recent searches
    const response = await api.get<SearchSummary[]>('/search/recent');
    return response.data;
  } catch (error) {
    if (error instanceof Error) {
      return rejectWithValue(error.message);
    }
    return rejectWithValue('An unknown error occurred');
  }
});

// Slice
const searchSlice = createSlice({
  name: 'search',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Start search
      .addCase(startSearch.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(startSearch.fulfilled, (state, action) => {
        state.loading = false;
        
        // Add to recent searches if not already there
        const exists = state.recentSearches.some(
          (search) => search.request_id === action.payload.request_id
        );
        
        if (!exists) {
          state.recentSearches.unshift({
            request_id: action.payload.request_id,
            name: action.payload.name,
            status: action.payload.status,
            risk_level: action.payload.risk_level,
            timestamp: action.payload.timestamp
          });
          
          // Keep only the 10 most recent searches
          state.recentSearches = state.recentSearches.slice(0, 10);
        }
      })
      .addCase(startSearch.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to start search';
      })
      
      // Fetch recent searches
      .addCase(fetchRecentSearches.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRecentSearches.fulfilled, (state, action) => {
        state.loading = false;
        state.recentSearches = action.payload;
      })
      .addCase(fetchRecentSearches.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch recent searches';
      });
  }
});

export const { clearError } = searchSlice.actions;
export default searchSlice.reducer;