import api from '@/api/axios';
import { handleError } from '@/utils/errorHandler';

export const fetchCategories = async () => {
  try {
    const response = await api.get('categories');
    return response.data;
  } catch (error) {
    handleError(error, 'Failed to fetch categories');
    return null;
  }
};