import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { SearchStatus, SearchResult } from '../types/search';
import { api } from '../services/api';

interface ResultState {
  status: SearchStatus | null;
  result: SearchResult | null;
  loading: boolean;
  error: string | null;
}

const initialState: ResultState = {
  status: null,
  result: null,
  loading: false,
  error: null
};

// Async thunks
export const fetchSearchStatus = createAsyncThunk<
  SearchStatus,
  string,
  { rejectValue: string }
>('result/fetchSearchStatus', async (requestId, { rejectWithValue }) => {
  try {
    const response = await api.get<SearchStatus>(`/search/${requestId}/status`);
    return response.data;
  } catch (error) {
    if (error instanceof Error) {
      return rejectWithValue(error.message);
    }
    return rejectWithValue('An unknown error occurred');
  }
});

export const fetchSearchResult = createAsyncThunk<
  SearchResult,
  string,
  { rejectValue: string }
>('result/fetchSearchResult', async (requestId, { rejectWithValue }) => {
  try {
    const response = await api.get<SearchResult>(`/search/${requestId}/result`);
    return response.data;
  } catch (error) {
    if (error instanceof Error) {
      return rejectWithValue(error.message);
    }
    return rejectWithValue('An unknown error occurred');
  }
});

export const fetchSearchSummary = createAsyncThunk<
  SearchResult,
  string,
  { rejectValue: string }
>('result/fetchSearchSummary', async (requestId, { rejectWithValue }) => {
  try {
    const response = await api.get<SearchResult>(`/search/${requestId}/summary`);
    return response.data;
  } catch (error) {
    if (error instanceof Error) {
      return rejectWithValue(error.message);
    }
    return rejectWithValue('An unknown error occurred');
  }
});

// Slice
const resultSlice = createSlice({
  name: 'result',
  initialState,
  reducers: {
    clearResult: (state) => {
      state.result = null;
      state.status = null;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch search status
      .addCase(fetchSearchStatus.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSearchStatus.fulfilled, (state, action) => {
        state.loading = false;
        state.status = action.payload;
      })
      .addCase(fetchSearchStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch search status';
      })
      
      // Fetch search result
      .addCase(fetchSearchResult.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSearchResult.fulfilled, (state, action) => {
        state.loading = false;
        state.result = action.payload;
      })
      .addCase(fetchSearchResult.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch search result';
      })
      
      // Fetch search summary
      .addCase(fetchSearchSummary.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSearchSummary.fulfilled, (state, action) => {
        state.loading = false;
        // We're just updating summary fields, not replacing the full result
        if (state.result) {
          state.result.summary = action.payload.summary;
          state.result.risk_level = action.payload.risk_level;
          state.result.confidence_score = action.payload.confidence_score;
        } else {
          state.result = action.payload;
        }
      })
      .addCase(fetchSearchSummary.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch search summary';
      });
  }
});

export const { clearResult, clearError } = resultSlice.actions;
export default resultSlice.reducer;