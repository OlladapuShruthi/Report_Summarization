import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    const resData = response.data;
    if (resData && resData.success) {
      return resData.data;
    }
    return { status: 'error', database: 'disconnected' };
  } catch (error) {
    return {
      status: 'error',
      database: 'disconnected',
      error: error.message,
    };
  }
};

export const createAnalysisWorkspace = async (patientId = '', title = '') => {
  const formData = new FormData();
  if (patientId) formData.append('patient_id', patientId);
  if (title) formData.append('title', title);

  const response = await api.post('/analysis/create', formData);
  if (response.data && response.data.success) {
    return response.data.data;
  }
  throw new Error(response.data?.message || 'Workspace creation failed');
};

export const quickStartAnalysis = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/analysis/quick-start', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  if (response.data && response.data.success) {
    return response.data.data;
  }
  throw new Error(response.data?.message || 'Quick start upload failed');
};

export const fetchAnalysisSessions = async () => {
  try {
    const response = await api.get('/analysis/sessions');
    if (response.data && response.data.success) {
      return response.data.data || [];
    }
    return [];
  } catch (error) {
    console.error('Failed to fetch analysis sessions:', error);
    return [];
  }
};

export const parseAnalysisSession = async (analysisId) => {
  const response = await api.post(`/analysis/${analysisId}/parse`);
  if (response.data && response.data.success) {
    return response.data.data;
  }
  throw new Error(response.data?.message || 'Document parsing failed');
};

export const analyzeAnalysisSession = async (analysisId) => {
  const response = await api.post(`/analysis/${analysisId}/analyze`);
  if (response.data && response.data.success) {
    return response.data.data;
  }
  throw new Error(response.data?.message || 'Document analysis failed');
};

export const fetchAnalysisProgress = async (analysisId) => {
  const response = await api.get(`/analysis/${analysisId}/progress`);
  if (response.data && response.data.success) {
    return response.data.data;
  }
  throw new Error(response.data?.message || 'Progress lookup failed');
};

export default api;
