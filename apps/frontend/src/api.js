/**
 * API client for backend communication
 */
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Validate event access token
 */
export const validateToken = async (accessToken) => {
  const response = await api.post('/events/validate/', {
    access_token: accessToken,
  });
  return response.data;
};

/**
 * Get event details
 */
export const getEventDetails = async (accessToken) => {
  const response = await api.get(`/events/${accessToken}/`);
  return response.data;
};

/**
 * Upload a photo
 */
export const uploadPhoto = async (accessToken, photoFile, onProgress) => {
  const formData = new FormData();
  formData.append('access_token', accessToken);
  formData.append('photo', photoFile);

  const response = await api.post('/gallery/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        onProgress(progressEvent);
      }
    },
  });
  return response.data;
};

/**
 * Get photos for an event
 */
export const getPhotos = async (accessToken, page = 1) => {
  const response = await api.get('/gallery/photos/', {
    params: {
      access_token: accessToken,
      page: page,
    },
  });
  return response.data;
};

export default api;

