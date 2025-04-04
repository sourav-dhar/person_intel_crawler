import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../services/api';

interface AuthState {
  token: string | null;
  user: {
    username: string;
    email: string;
    role: string;
  } | null;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

interface LoginCredentials {
  username: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    username: string;
    email: string;
    role: string;
  };
}

const initialState: AuthState = {
  token: localStorage.getItem('auth_token'),
  user: null,
  loading: false,
  error: null,
  isAuthenticated: !!localStorage.getItem('auth_token')
};

// Async thunks
export const login = createAsyncThunk<
  LoginResponse,
  LoginCredentials,
  { rejectValue: string }
>('auth/login', async (credentials, { rejectWithValue }) => {
  try {
    // When authentication is enabled, use the real login endpoint
    if (import.meta.env.VITE_AUTH_ENABLED === 'true') {
      const response = await api.post<LoginResponse>('/auth/token', credentials);
      return response.data;
    } else {
      // When auth is disabled, simulate a successful login
      return {
        access_token: 'simulated_token',
        token_type: 'bearer',
        user: {
          username: credentials.username,
          email: `${credentials.username}@example.com`,
          role: 'user'
        }
      };
    }
  } catch (error) {
    if (error instanceof Error) {
      return rejectWithValue(error.message);
    }
    return rejectWithValue('An unknown error occurred');
  }
});

export const logout = createAsyncThunk('auth/logout', async () => {
  localStorage.removeItem('auth_token');
  return null;
});

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.token = action.payload.access_token;
        state.user = action.payload.user;
        state.isAuthenticated = true;
        localStorage.setItem('auth_token', action.payload.access_token);
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Login failed';
        state.isAuthenticated = false;
      })
      
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.token = null;
        state.user = null;
        state.isAuthenticated = false;
      });
  }
});

export const { clearError } = authSlice.actions;
export default authSlice.reducer;