import React, { createContext, useContext, useState, useEffect } from 'react';
import { clearStoredSession, getStoredSession, persistSession } from '../utils/auth';

const AuthContext = createContext();

export { AuthContext };

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const session = getStoredSession();
    if (session?.user) {
      setUser(session.user);
      setAccessToken(session.accessToken || null);
    }
    setLoading(false);
  }, []);

  const login = (authPayload) => {
    const session = {
      accessToken: authPayload.access_token || authPayload.accessToken || null,
      user: authPayload.user || {
        id: authPayload.user_id ?? authPayload.id,
        name: authPayload.name,
        email: authPayload.email,
        mobile_no: authPayload.mobile_no,
        role: authPayload.role
      }
    };

    setUser(session.user);
    setAccessToken(session.accessToken);
    persistSession(session);
  };

  const logout = () => {
    setUser(null);
    setAccessToken(null);
    clearStoredSession();
  };

  const value = {
    user,
    accessToken,
    isAuthenticated: Boolean(user),
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
