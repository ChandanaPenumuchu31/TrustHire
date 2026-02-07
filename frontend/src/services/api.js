import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchJobs = async (query, location = '', experience = '', platforms = ['all']) => {
  try {
    const response = await api.post('/search', {
      query,
      location,
      experience,
      platforms,
      save_to_db: true
    });
    return response.data;
  } catch (error) {
    console.error('Error searching jobs:', error);
    throw error;
  }
};

export const getJobs = async (filters = {}) => {
  try {
    const response = await api.get('/jobs', { params: filters });
    return response.data;
  } catch (error) {
    console.error('Error fetching jobs:', error);
    throw error;
  }
};

export const getJobDetails = async (jobId) => {
  try {
    const response = await api.get(`/jobs/${jobId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching job details:', error);
    throw error;
  }
};

export const reportJob = async (jobId, reason) => {
  try {
    const response = await api.post(`/jobs/${jobId}/report`, { reason });
    return response.data;
  } catch (error) {
    console.error('Error reporting job:', error);
    throw error;
  }
};

export const getStatistics = async () => {
  try {
    const response = await api.get('/stats');
    return response.data;
  } catch (error) {
    console.error('Error fetching statistics:', error);
    throw error;
  }
};

export default api;
