import axios from 'axios';

const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  timeout: 20000,
});

export const getApiBaseUrl = () => apiBaseUrl;
export const getWebSocketUrl = () => import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/detections';

export const fetchHealth = async () => (await apiClient.get('/api/health')).data;
export const fetchCameraStatus = async () => (await apiClient.get('/api/camera/status')).data;
export const startCamera = async (payload = {}) => (await apiClient.post('/api/camera/start', payload)).data;
export const stopCamera = async () => (await apiClient.post('/api/camera/stop')).data;
export const fetchCurrentDetections = async () => (await apiClient.get('/api/detections/current')).data;
export const fetchDetectionLogs = async (params = {}) => (await apiClient.get('/api/detections/logs', { params })).data;
export const fetchStatsSummary = async () => (await apiClient.get('/api/stats/summary')).data;
export const fetchStatsTimeline = async () => (await apiClient.get('/api/stats/timeline')).data;
