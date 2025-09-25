import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

import { authService } from '../services/authService';
import { User } from '../types/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (userData: Partial<User>) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (token: string, newPassword: string) => Promise<void>;
  verifyEmail: (token: string) => Promise<void>;
  resendVerification: () => Promise<void>;
}

interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phoneNumber?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Check if user is authenticated on app load
  const { data: currentUser, isLoading: isCheckingAuth } = useQuery(
    'currentUser',
    authService.getCurrentUser,
    {
      retry: false,
      onError: () => {
        setUser(null);
        localStorage.removeItem('token');
      },
    }
  );

  // Update user state when currentUser data changes
  useEffect(() => {
    if (currentUser) {
      setUser(currentUser);
    }
    setIsLoading(false);
  }, [currentUser]);

  // Login mutation
  const loginMutation = useMutation(authService.login, {
    onSuccess: (data) => {
      setUser(data.user);
      localStorage.setItem('token', data.token);
      queryClient.setQueryData('currentUser', data.user);
      toast.success('Welcome back!');
      navigate('/dashboard');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Login failed');
    },
  });

  // Register mutation
  const registerMutation = useMutation(authService.register, {
    onSuccess: () => {
      toast.success('Account created successfully! Please check your email to verify your account.');
      navigate('/login');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Registration failed');
    },
  });

  // Logout mutation
  const logoutMutation = useMutation(authService.logout, {
    onSuccess: () => {
      setUser(null);
      localStorage.removeItem('token');
      queryClient.clear();
      toast.success('Logged out successfully');
      navigate('/login');
    },
    onError: () => {
      // Even if logout fails on server, clear local state
      setUser(null);
      localStorage.removeItem('token');
      queryClient.clear();
      navigate('/login');
    },
  });

  // Update profile mutation
  const updateProfileMutation = useMutation(authService.updateProfile, {
    onSuccess: (updatedUser) => {
      setUser(updatedUser);
      queryClient.setQueryData('currentUser', updatedUser);
      toast.success('Profile updated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to update profile');
    },
  });

  // Change password mutation
  const changePasswordMutation = useMutation(authService.changePassword, {
    onSuccess: () => {
      toast.success('Password changed successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to change password');
    },
  });

  // Forgot password mutation
  const forgotPasswordMutation = useMutation(authService.forgotPassword, {
    onSuccess: () => {
      toast.success('Password reset email sent');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to send reset email');
    },
  });

  // Reset password mutation
  const resetPasswordMutation = useMutation(authService.resetPassword, {
    onSuccess: () => {
      toast.success('Password reset successfully');
      navigate('/login');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to reset password');
    },
  });

  // Verify email mutation
  const verifyEmailMutation = useMutation(authService.verifyEmail, {
    onSuccess: (verifiedUser) => {
      setUser(verifiedUser);
      queryClient.setQueryData('currentUser', verifiedUser);
      toast.success('Email verified successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to verify email');
    },
  });

  // Resend verification mutation
  const resendVerificationMutation = useMutation(authService.resendVerification, {
    onSuccess: () => {
      toast.success('Verification email sent');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to send verification email');
    },
  });

  const login = async (email: string, password: string) => {
    await loginMutation.mutateAsync({ email, password });
  };

  const register = async (userData: RegisterData) => {
    await registerMutation.mutateAsync(userData);
  };

  const logout = async () => {
    await logoutMutation.mutateAsync();
  };

  const updateProfile = async (userData: Partial<User>) => {
    await updateProfileMutation.mutateAsync(userData);
  };

  const changePassword = async (currentPassword: string, newPassword: string) => {
    await changePasswordMutation.mutateAsync({ currentPassword, newPassword });
  };

  const forgotPassword = async (email: string) => {
    await forgotPasswordMutation.mutateAsync({ email });
  };

  const resetPassword = async (token: string, newPassword: string) => {
    await resetPasswordMutation.mutateAsync({ token, newPassword });
  };

  const verifyEmail = async (token: string) => {
    await verifyEmailMutation.mutateAsync({ token });
  };

  const resendVerification = async () => {
    await resendVerificationMutation.mutateAsync();
  };

  const value: AuthContextType = {
    user,
    isLoading: isLoading || isCheckingAuth,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    forgotPassword,
    resetPassword,
    verifyEmail,
    resendVerification,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};