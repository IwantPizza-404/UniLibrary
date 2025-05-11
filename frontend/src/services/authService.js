import api from '@/api/axios';
import { useAuthStore } from '@/store/authStore';
import { handleError } from '@/utils/errorHandler';

export const loginUser = async (username, password) => {
  try {
    const response = await api.post(
      'auth/login',
      new URLSearchParams({ username, password }),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    );
    return response.data;
  } catch (error) {
    handleError(error, 'Login failed');
  }
};

export const refreshAccessToken = async () => {
  try {
    const response = await api.post('auth/refresh');
    return response.data;
  } catch (error) {
    handleError(error, 'Token refresh failed');
  }
};

export const fetchUserData = async () => {
  const store = useAuthStore();
  try {
    const response = await api.get('users/me');
    return response.data;
  } catch (error) {
    if (error.response?.status === 401 && !store.isAuthChecked) {
      try {
        await store.refreshToken();
        const retryResponse = await api.get('users/me');
        return retryResponse.data;
      } catch (refreshError) {
        handleError(refreshError, 'Failed to refresh token and fetch user data');
      }
    }
    handleError(error, 'Failed to fetch user data');
  }
};

export const registerUser = async (userData) => {
  try {
    const response = await api.post('auth/register', userData, {
      headers: { 'Content-Type': 'application/json' },
    });
    return response.data;
  } catch (error) {
    handleError(error, 'Registration failed');
  }
};

export const logoutUser = async () => {
  const store = useAuthStore();
  try {
    if (store.accessToken) {
      await api.post('auth/logout');
    }
    return { success: true };
  } catch (error) {
    handleError(error, 'Logout failed');
    return null;
  }
};