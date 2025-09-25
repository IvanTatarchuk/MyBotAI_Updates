import axios from 'axios';
import { 
  User, 
  LoginCredentials, 
  RegisterData, 
  AuthResponse, 
  PasswordChangeData, 
  PasswordResetData, 
  ForgotPasswordData,
  EmailVerificationData 
} from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh and errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }

    return Promise.reject(error);
  }
);

export const authService = {
  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // Login
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  // Register
  async register(userData: RegisterData): Promise<void> {
    await api.post('/auth/register', userData);
  },

  // Logout
  async logout(): Promise<void> {
    await api.post('/auth/logout');
  },

  // Update profile
  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await api.patch('/auth/profile', userData);
    return response.data;
  },

  // Change password
  async changePassword(data: PasswordChangeData): Promise<void> {
    await api.post('/auth/change-password', data);
  },

  // Forgot password
  async forgotPassword(data: ForgotPasswordData): Promise<void> {
    await api.post('/auth/forgot-password', data);
  },

  // Reset password
  async resetPassword(data: PasswordResetData): Promise<void> {
    await api.post('/auth/reset-password', data);
  },

  // Verify email
  async verifyEmail(data: EmailVerificationData): Promise<User> {
    const response = await api.post('/auth/verify-email', data);
    return response.data;
  },

  // Resend verification email
  async resendVerification(): Promise<void> {
    await api.post('/auth/resend-verification');
  },

  // Upload avatar
  async uploadAvatar(file: File): Promise<{ url: string }> {
    const formData = new FormData();
    formData.append('avatar', file);

    const response = await api.post('/auth/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  // Enable 2FA
  async enableTwoFactor(): Promise<{ secret: string; qrCode: string }> {
    const response = await api.post('/auth/2fa/enable');
    return response.data;
  },

  // Verify 2FA
  async verifyTwoFactor(token: string): Promise<void> {
    await api.post('/auth/2fa/verify', { token });
  },

  // Disable 2FA
  async disableTwoFactor(): Promise<void> {
    await api.post('/auth/2fa/disable');
  },

  // Get API keys
  async getApiKeys(): Promise<{ apiKey: string; apiSecret: string }> {
    const response = await api.get('/auth/api-keys');
    return response.data;
  },

  // Generate API keys
  async generateApiKeys(): Promise<{ apiKey: string; apiSecret: string }> {
    const response = await api.post('/auth/api-keys');
    return response.data;
  },

  // Revoke API keys
  async revokeApiKeys(): Promise<void> {
    await api.delete('/auth/api-keys');
  },
};