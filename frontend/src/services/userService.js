import api from '@/api/axios';
import { useAuthStore } from '@/store/authStore';
import { handleError } from '@/utils/errorHandler';

export const fetchProfile = async () => {
  const store = useAuthStore();
  if (store.isAuthChecked && !store.isAuthenticated){
    return null;
  }
  try {
    const response = await api.get('/users/me/profile');
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch user profile');
    return null;
  }
};

export const fetchUserProfile = async (username) => {
  try {
    const response = await api.get(`/users/${username}/profile`);
    console.log(response.data)
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch user profile');
    return null;
  }
};
