import api from '@/api/axios';
import { handleError } from '@/utils/errorHandler';

export const followUser = async (user_id) => {
  try {
    const response = await api.post(`user_follow/${user_id}/follow`);
    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Please log in to follow users');
    } else if (error.response?.status === 404) {
      throw new Error('User not found');
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data.detail || 'Cannot follow this user');
    }
    handleError(error, 'Failed to follow user');
    throw error;
  }
};

export const unfollowUser = async (user_id) => {
  try {
    const response = await api.delete(`user_follow/${user_id}/unfollow`);
    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      throw new Error('Please log in to unfollow users');
    } else if (error.response?.status === 404) {
      throw new Error('User not found');
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data.detail || 'Cannot unfollow this user');
    }
    handleError(error, 'Failed to unfollow user');
    throw error;
  }
};