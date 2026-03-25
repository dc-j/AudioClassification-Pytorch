import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const stationApi = {
  getStations: () => api.get('/stations'),
  getStationDetail: (id: string) => api.get(`/stations/${id}`),
};

export const patrolApi = {
  getTasks: () => api.get('/patrol/tasks'),
  getRecords: () => api.get('/patrol/records'),
  getStatistics: () => api.get('/patrol/statistics'),
  createTask: (data: unknown) => api.post('/patrol/tasks', data),
  updateTask: (id: string, data: unknown) => api.put(`/patrol/tasks/${id}`, data),
};

export const alarmApi = {
  getAlarms: (params?: unknown) => api.get('/alarms', { params }),
  handleAlarm: (id: string, data: unknown) => api.put(`/alarms/${id}`, data),
};

export const deviceApi = {
  getDevices: () => api.get('/devices'),
  getDeviceStatus: () => api.get('/devices/status'),
};

export const authApi = {
  login: (data: { username: string; password: string }) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  getUserInfo: () => api.get('/auth/userinfo'),
};

export default api;
