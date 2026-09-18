import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 120 seconds to allow for LangGraph/Gemini processing
});

// Request interceptor to attach JWT token from localStorage
api.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem('med_user');
    if (raw) {
      const user = JSON.parse(raw);
      if (user && user.access_token) {
        config.headers['Authorization'] = `Bearer ${user.access_token}`;
      }
    }
  } catch (e) {
    // ignore parsing errors
  }
  return config;
}, (error) => Promise.reject(error));

// Response interceptor for global 401 handling (logout)
api.interceptors.response.use((response) => response, (error) => {
  if (error.response && error.response.status === 401) {
    localStorage.removeItem('med_user');
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('auth:unauthorized'));
    }
  }
  return Promise.reject(error);
});

// ─── Auth ────────────────────────────────────────────────────────────────────

export const loginUser = async (email, password) => {
  const response = await api.post('/auth/login', { email, password });
  if (response.data?.success) return response.data.data;
  const err = new Error(response.data?.message || 'Login failed');
  err.status = response.status;
  throw err;
};

export const registerUser = async (full_name, email, password) => {
  const response = await api.post('/auth/register', { full_name, email, password });
  if (response.data?.success) return response.data.data;
  const err = new Error(response.data?.message || 'Registration failed');
  err.status = response.status;
  throw err;
};

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

export const createAnalysisWorkspace = async (patientId, title = '') => {
  if (!patientId) {
    throw new Error('Please select a patient before creating an analysis workspace.');
  }
  const formData = new FormData();
  formData.append('patient_id', patientId);
  if (title) formData.append('title', title);

  const response = await api.post('/analysis/create', formData);
  if (response.data && response.data.success) {
    return response.data.data;
  }
  throw new Error(response.data?.message || 'Workspace creation failed');
};

export const quickStartAnalysis = async (file, patientId) => {
  if (!patientId) {
    throw new Error('Please select a patient before uploading a medical report.');
  }
  const formData = new FormData();
  formData.append('file', file);
  formData.append('patient_id', patientId);

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

export const fetchAnalysisSessions = async (patientId = '') => {
  try {
    const response = await api.get('/analysis/sessions', { params: patientId ? { patient_id: patientId } : {} });
    if (response.data && response.data.success) {
      return response.data.data || [];
    }
    return [];
  } catch (error) {
    console.error('Failed to fetch analysis sessions:', error);
    return [];
  }
};

export const fetchPatients = async (userId = null) => {
  const params = userId ? { user_id: userId } : {};
  const response = await api.get('/patients', { params });
  if (response.data?.success) return response.data.data || [];
  throw new Error(response.data?.message || 'Patient profiles could not be loaded');
};


export const createPatient = async (patient) => {
  const response = await api.post('/patients', patient);
  if (response.data?.success) return response.data.data;
  throw new Error(response.data?.message || 'Patient profile could not be created');
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

export const fetchAnalysisResult = async (analysisId) => {
  const response = await api.get(`/analysis/${analysisId}/result`);
  if (response.data?.success) return response.data.data;
  throw new Error(response.data?.message || 'Analysis result is not ready');
};

export const fetchReviewQuestions = async (analysisId) => {
  const response = await api.get(`/analysis/${analysisId}/review-questions`);
  if (response.data?.success) return response.data.data;
  throw new Error(response.data?.message || 'Failed to load review questions');
};

export const answerReviewQuestion = async (analysisId, questionId, { action, response, finding_id }) => {
  const payload = { action, response: response || null, finding_id: finding_id || null };
  const res = await api.post(`/analysis/${analysisId}/review-questions/${questionId}/answer`, payload);
  if (res.data?.success) return res.data.data;
  throw new Error(res.data?.message || 'Failed to submit review answer');
};

export const uploadFollowUpReport = async (analysisId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post(`/analysis/${analysisId}/follow-up`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  if (response.data?.success) return response.data.data;
  throw new Error(response.data?.message || 'Failed to upload follow-up report');
};

export const fetchPatientTimeline = async (patientId) => {
  if (!patientId) return null;
  const response = await api.get(`/patients/${patientId}/timeline`);
  if (response.data?.success) return response.data.data;
  throw new Error(response.data?.message || 'Patient timeline could not be loaded');
};

export const sendChatMessage = async (patientId, message, analysisId = null) => {
  const response = await api.post('/chat/message', {
    patient_id: patientId,
    message,
    analysis_id: analysisId
  });
  if (response.data?.success) return response.data.data;
  throw new Error(response.data?.message || 'Chat message failed');
};

export const fetchChatHistory = async (patientId) => {
  if (!patientId) return [];
  const response = await api.get(`/chat/history/${patientId}`);
  if (response.data?.success) return response.data.data || [];
  return [];
};

export const clearChatHistory = async (patientId) => {
  if (!patientId) return;
  const response = await api.delete(`/chat/history/${patientId}`);
  if (response.data?.success) return response.data.data;
  throw new Error(response.data?.message || 'Clear chat history failed');
};

export default api;
