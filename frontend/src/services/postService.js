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

export const createPost = async (formData, onProgress) => {
  try {
    const response = await api.post('posts/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.lengthComputable && onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      }
    });
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to upload post');
    return null;
  }
};

export const fetchPopularPosts = async (skip = 0, limit = 6) => {
  try {
    const response = await api.get(`posts?skip=${skip}&limit=${limit}`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch popular posts');
    return [];
  }
};

export const fetchFollowingPosts = async (skip = 0, limit = 6) => {
  try {
    const response = await api.get(`posts/following?skip=${skip}&limit=${limit}`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch following posts');
    return [];
  }
};

export const fetchPostsByCategory = async (categoryId, skip = 0, limit = 6) => {
  try {
    const response = await api.get(`posts/category/${categoryId}?skip=${skip}&limit=${limit}`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch posts by category');
    return [];
  }
};

export const searchPosts = async (query, category_id = null, sort = null, skip = 0, limit = 6) => {
  try {
    const params = new URLSearchParams({ 
      q: query,
      skip: skip,
      limit: limit
    });
    if (category_id) {
      params.append('category_id', category_id);
    }
    if (sort) {
      params.append('sort', sort);
    }
    const response = await api.get(`/posts/search?${params.toString()}`);
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to search posts');
    return [];
  }
};

export const downloadPost = async (postId) => {
  try {
    const response = await api.get(`posts/${postId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to download file');
    return null;
  }
};