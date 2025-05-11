import api from '@/api/axios';
import { handleError } from '@/utils/errorHandler';

export const fetchUserPosts = async (username) => {
  try {
    const response = await api.get(`posts/user/${username}`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch user posts');
    return null;
  }
};

export const fetchPost = async (post_id) => {
  try {
    const response = await api.get(`posts/${post_id}`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch post');
    return null;
  }
};

export const votePost = async (post_id, is_upvote) => {
  try {
    const response = await api.post(`posts/${post_id}/vote`, { is_upvote: is_upvote });
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to vote post');
    return null;
  }
};