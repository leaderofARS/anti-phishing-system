import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface AnalysisRequest {
  url: string;
  include_content?: boolean;
}

export interface AnalysisResponse {
  url: string;
  risk_score: number;
  risk_level: string;
  confidence: number;
  features: Record<string, any>;
  recommendations: string[];
  allow_access: boolean;
  scan_time: number;
}

export interface StatsResponse {
  total_scans: number;
  phishing_detected: number;
  safe_urls: number;
  suspicious_urls: number;
}

export const analyzeURL = async (data: AnalysisRequest): Promise<AnalysisResponse> => {
  const response = await api.post('/analyze', data);
  return response.data;
};

export const quickCheck = async (url: string) => {
  const response = await api.get(`/check/${encodeURIComponent(url)}`);
  return response.data;
};

export const reportPhishing = async (url: string, reason: string) => {
  const response = await api.post('/report', { url, reason, reported_by: 'dashboard_user' });
  return response.data;
};

export const getStats = async (): Promise<StatsResponse> => {
  const response = await api.get('/stats');
  return response.data;
};

export const getHistory = async (limit: number = 10) => {
  const response = await api.get(`/history?limit=${limit}`);
  return response.data;
};

export default api;
