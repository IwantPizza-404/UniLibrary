export const handleError = (error, defaultMessage) => {
  throw new Error(error.response?.data?.detail || defaultMessage);
};