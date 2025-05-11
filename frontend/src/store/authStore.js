import { defineStore } from 'pinia';
import { loginUser, refreshAccessToken, logoutUser, fetchUserData } from '@/services/authService';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,
    isAuthChecked: false,
    isRefreshing: false,
    refreshPromise: null,
  }),
  actions: {
    async login(username, password) {
      try {
        const response = await loginUser(username, password);
        this.accessToken = response.access_token;
        this.isAuthChecked = true;
        await this.fetchUser();
      } catch (error) {
        console.error('Login failed:', error);
        this.isAuthChecked = true;
        throw error;
      }
    },
    async refreshToken() {
      if (this.isAuthChecked && !this.isAuthenticated) {
        console.warn('Refresh skipped: User is not authenticated');
        return Promise.reject(new Error('User is not authenticated'));
      }
      if (this.isRefreshing) {
        return this.refreshPromise;
      }
      this.isRefreshing = true;
      this.refreshPromise = refreshAccessToken()
        .then(response => {
          this.accessToken = response.access_token;
          this.isAuthChecked = true;
          return this.fetchUser();
        })
        .catch(error => {
          console.error('Failed to refresh access token:', error);
          this.logout();
          throw error;
        })
        .finally(() => {
          this.isRefreshing = false;
          this.refreshPromise = null;
        });
      return this.refreshPromise;
    },
    async checkAuth() {
      if (this.isAuthChecked && !this.isAuthenticated) {
        return;
      }
      if (this.isRefreshing) {
        return this.refreshPromise;
      }
      try {
        await this.refreshToken();
      } catch (error) {
        console.warn('Auth check failed:', error);
      }
    },
    async logout() {
      try {
        await logoutUser();
      } catch (error) {
        console.error('Logout failed:', error);
      } finally {
        this.user = null;
        this.accessToken = null;
        this.isAuthChecked = true;
        this.isRefreshing = false;
        this.refreshPromise = null;
      }
    },
    async fetchUser() {
      if (!this.isAuthenticated) {
        console.warn('Fetch user skipped: User is not authenticated');
        this.user = null;
        return;
      }
      try {
        const userData = await fetchUserData();
        this.user = userData;
      } catch (error) {
        console.error('Failed to fetch user:', error);
        this.user = null;
        throw error;
      } finally {
        console.log('User data fetched:', this.user);
      }
    },
  },
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },
});