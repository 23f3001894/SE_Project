const STORAGE_KEY = 'agriflow_auth';

export const AUTH_STORAGE_KEY = STORAGE_KEY;

export function getStoredSession() {
  const rawSession = localStorage.getItem(STORAGE_KEY);
  if (rawSession) {
    try {
      return JSON.parse(rawSession);
    } catch (_error) {
      localStorage.removeItem(STORAGE_KEY);
    }
  }

  const legacyUser = localStorage.getItem('user');
  if (legacyUser) {
    try {
      const user = JSON.parse(legacyUser);
      return {
        accessToken: null,
        user
      };
    } catch (_error) {
      localStorage.removeItem('user');
    }
  }

  return null;
}

export function persistSession(session) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  localStorage.setItem('user', JSON.stringify(session.user));
}

export function clearStoredSession() {
  localStorage.removeItem(STORAGE_KEY);
  localStorage.removeItem('user');
}

export function getDashboardPath(role) {
  return role === 'admin' ? '/admin/dashboard' : '/customer/dashboard';
}

export function isRoleAllowed(userRole, allowedRoles = []) {
  return allowedRoles.length === 0 || allowedRoles.includes(userRole);
}

export function resolvePostLoginPath(role, from) {
  const fallbackPath = getDashboardPath(role);
  const requestedPath = from?.pathname;

  if (!requestedPath || requestedPath === '/' || requestedPath === '/login' || requestedPath === '/signup') {
    return fallbackPath;
  }

  if (requestedPath.startsWith('/admin') && role !== 'admin') {
    return fallbackPath;
  }

  if ((requestedPath === '/cart' || requestedPath === '/orders' || requestedPath === '/profile') && role !== 'customer') {
    return fallbackPath;
  }

  if ((requestedPath === '/products/create' || requestedPath.includes('/edit')) && role !== 'admin') {
    return fallbackPath;
  }

  return requestedPath;
}
