export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phoneNumber?: string;
  role: 'user' | 'premium' | 'vip' | 'admin' | 'super_admin';
  status: 'active' | 'inactive' | 'suspended' | 'pending_verification';
  kycStatus: 'not_started' | 'in_progress' | 'approved' | 'rejected' | 'expired';
  isEmailVerified: boolean;
  isPhoneVerified: boolean;
  avatar?: string;
  dateOfBirth?: string;
  address?: string;
  city?: string;
  country?: string;
  postalCode?: string;
  totalDeposits: number;
  totalWithdrawals: number;
  totalProfitLoss: number;
  totalVolume: number;
  lastLoginAt?: string;
  lastLoginIp?: string;
  twoFactorEnabled: boolean;
  apiTradingEnabled: boolean;
  preferences?: {
    theme: 'light' | 'dark';
    language: string;
    timezone: string;
    notifications: {
      email: boolean;
      push: boolean;
      sms: boolean;
    };
    trading: {
      defaultOrderType: string;
      defaultQuantity: number;
      riskLevel: 'low' | 'medium' | 'high';
    };
  };
  metadata?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  twoFactorCode?: string;
}

export interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phoneNumber?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  refreshToken?: string;
}

export interface PasswordChangeData {
  currentPassword: string;
  newPassword: string;
}

export interface PasswordResetData {
  token: string;
  newPassword: string;
}

export interface ForgotPasswordData {
  email: string;
}

export interface EmailVerificationData {
  token: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark';
  language: string;
  timezone: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  trading: {
    defaultOrderType: string;
    defaultQuantity: number;
    riskLevel: 'low' | 'medium' | 'high';
  };
}