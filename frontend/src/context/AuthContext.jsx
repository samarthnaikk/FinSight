import React, { createContext, useState, useContext, useEffect } from 'react';
import { backendAPI } from '../utils/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('accessToken'));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken'));

  useEffect(() => {
    // Check if user is already logged in
    const initAuth = async () => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        try {
          const response = await backendAPI.getMe();
          if (response.success && response.data) {
            setUser(response.data);
          }
        } catch (error) {
          console.error('Failed to fetch user:', error);
          // Clear invalid tokens
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          setAccessToken(null);
          setRefreshToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials) => {
    const response = await backendAPI.login(credentials);
    
    if (response.success && response.data && response.data.access && response.data.refresh) {
      const { access, refresh } = response.data;
      
      localStorage.setItem('accessToken', access);
      localStorage.setItem('refreshToken', refresh);
      setAccessToken(access);
      setRefreshToken(refresh);
      
      // Fetch user data
      const userResponse = await backendAPI.getMe();
      if (userResponse.success && userResponse.data) {
        setUser(userResponse.data);
      }
      
      return response;
    }
    
    throw new Error('Invalid response from server');
  };

  const register = async (userData) => {
    const response = await backendAPI.register(userData);
    return response;
  };

  const googleLogin = async (credentialResponse) => {
    const response = await backendAPI.googleAuth(credentialResponse.credential);
    
    if (response.success && response.data && response.data.access && response.data.refresh) {
      const { access, refresh } = response.data;
      
      localStorage.setItem('accessToken', access);
      localStorage.setItem('refreshToken', refresh);
      setAccessToken(access);
      setRefreshToken(refresh);
      
      // Fetch user data
      const userResponse = await backendAPI.getMe();
      if (userResponse.success && userResponse.data) {
        setUser(userResponse.data);
      }
      
      return response;
    }
    
    throw new Error('Invalid response from Google authentication');
  };

  const logout = async () => {
    try {
      if (refreshToken) {
        await backendAPI.logout(refreshToken);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      setAccessToken(null);
      setRefreshToken(null);
      setUser(null);
    }
  };

  const value = {
    user,
    accessToken,
    refreshToken,
    loading,
    login,
    register,
    googleLogin,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
