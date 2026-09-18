import React, { createContext, useState, useEffect, useCallback } from 'react';
import { loginUser, registerUser } from '../services/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [authUser, setAuthUser] = useState(() => {
    try {
      const raw = localStorage.getItem('med_user');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  const login = useCallback(async (email, password) => {
    const data = await loginUser(email, password);
    const stored = { ...data, access_token: data.access_token };
    localStorage.setItem('med_user', JSON.stringify(stored));
    setAuthUser(stored);
    return stored;
  }, []);

  const signup = useCallback(async (fullName, email, password) => {
    const data = await registerUser(fullName, email, password);
    const stored = { ...data, access_token: data.access_token };
    localStorage.setItem('med_user', JSON.stringify(stored));
    setAuthUser(stored);
    return stored;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('med_user');
    setAuthUser(null);
  }, []);

  const restoreSession = useCallback(() => {
    try {
      const raw = localStorage.getItem('med_user');
      if (raw) {
        const parsed = JSON.parse(raw);
        setAuthUser(parsed);
        return parsed;
      }
    } catch {}
    return null;
  }, []);

  useEffect(() => {
    restoreSession();
  }, [restoreSession]);

  return (
    <AuthContext.Provider value={{ authUser, login, signup, logout, restoreSession }}>
      {children}
    </AuthContext.Provider>
  );
};
