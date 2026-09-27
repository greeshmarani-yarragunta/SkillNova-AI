import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';
import { notificationService } from '../services/notificationService';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('skillnova_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchUnreadCount = useCallback(async () => {
    if (localStorage.getItem('skillnova_access')) {
      try {
        const data = await notificationService.getUnreadCount();
        setUnreadCount(data.unread_count || 0);
      } catch (err) {
        // Silently fail if unauthenticated or network drop
      }
    }
  }, []);

  const refreshUser = useCallback(async () => {
    if (localStorage.getItem('skillnova_access')) {
      try {
        const freshUser = await authService.getProfile();
        setUser(freshUser);
        localStorage.setItem('skillnova_user', JSON.stringify(freshUser));
        await fetchUnreadCount();
      } catch (err) {
        console.error('Failed to sync profile', err);
      }
    }
    setLoading(false);
  }, [fetchUnreadCount]);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = async (email, password) => {
    const data = await authService.login({ email, password });
    localStorage.setItem('skillnova_access', data.tokens.access);
    localStorage.setItem('skillnova_refresh', data.tokens.refresh);
    localStorage.setItem('skillnova_user', JSON.stringify(data.user));
    setUser(data.user);
    await fetchUnreadCount();
    return data.user;
  };

  const register = async (userData) => {
    const res = await authService.register(userData);
    return res;
  };

  const logout = () => {
    localStorage.removeItem('skillnova_access');
    localStorage.removeItem('skillnova_refresh');
    localStorage.removeItem('skillnova_user');
    setUser(null);
    setUnreadCount(0);
  };

  const isStudent = user?.role === 'STUDENT';
  const isInstructor = user?.role === 'INSTRUCTOR';
  const isAdmin = user?.role === 'ADMIN' || user?.is_staff || user?.is_superuser;

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        unreadCount,
        fetchUnreadCount,
        login,
        register,
        logout,
        refreshUser,
        isAuthenticated: !!user,
        role: user?.role,
        isStudent,
        isInstructor,
        isAdmin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
