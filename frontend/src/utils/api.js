// API client utility for making requests to backend and models services

const BACKEND_URL = 'http://localhost:8000';
const MODELS_URL = 'http://localhost:8001';

// Helper function to get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('accessToken');
};

// Helper function to handle API responses
const handleResponse = async (response) => {
  const contentType = response.headers.get('content-type');
  
  if (contentType && contentType.includes('application/json')) {
    const jsonData = await response.json();
    
    if (!response.ok) {
      // Handle error response
      const errorMessage = jsonData.error?.message || jsonData.detail || 'An error occurred';
      throw new Error(errorMessage);
    }
    
    // Return the parsed JSON for successful responses
    return jsonData;
  }
  
  // For non-JSON responses
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || 'An error occurred');
  }
  
  return response.text();
};

// API client for backend endpoints
export const backendAPI = {
  // Authentication endpoints
  register: async (userData) => {
    const response = await fetch(`${BACKEND_URL}/api/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    return handleResponse(response);
  },

  login: async (credentials) => {
    const response = await fetch(`${BACKEND_URL}/api/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        identifier: credentials.email,
        password: credentials.password,
      }),
    });
    return handleResponse(response);
  },

  sendOTP: async (email) => {
    const response = await fetch(`${BACKEND_URL}/api/auth/send-otp/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });
    return handleResponse(response);
  },

  verifyOTP: async (otpData) => {
    const response = await fetch(`${BACKEND_URL}/api/auth/verify-otp/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(otpData),
    });
    return handleResponse(response);
  },

  googleAuth: async (token) => {
    const response = await fetch(`${BACKEND_URL}/api/auth/google/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token }),
    });
    return handleResponse(response);
  },

  getMe: async () => {
    const token = getAuthToken();
    const response = await fetch(`${BACKEND_URL}/api/auth/me/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return handleResponse(response);
  },

  logout: async (refreshToken) => {
    const token = getAuthToken();
    const response = await fetch(`${BACKEND_URL}/api/auth/logout/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });
    return handleResponse(response);
  },

  refreshToken: async (refreshToken) => {
    const response = await fetch(`${BACKEND_URL}/api/auth/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });
    return handleResponse(response);
  },

  // AI and Chat endpoints
  ingestData: async (data) => {
    const token = getAuthToken();
    const response = await fetch(`${BACKEND_URL}/api/ai/ingest/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  sendChatMessage: async (message) => {
    const token = getAuthToken();
    const response = await fetch(`${BACKEND_URL}/api/chat/message/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
    return handleResponse(response);
  },

  getChatHistory: async () => {
    const token = getAuthToken();
    const response = await fetch(`${BACKEND_URL}/api/chat/message/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return handleResponse(response);
  },
};

// API client for models service endpoints
export const modelsAPI = {
  // Audio transcription endpoint
  transcribeAudio: async (audioFile) => {
    const formData = new FormData();
    formData.append('file', audioFile);

    const response = await fetch(`${MODELS_URL}/transcribe`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(response);
  },

  // Text processing endpoints
  processTranscript: async (text, filename = 'transcript') => {
    const response = await fetch(`${MODELS_URL}/filtertext/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, filename }),
    });
    return handleResponse(response);
  },

  processTranscriptFile: async (transcriptFilename) => {
    const response = await fetch(`${MODELS_URL}/filtertext/process-file`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ transcript_filename: transcriptFilename }),
    });
    return handleResponse(response);
  },

  getFilterTextStatus: async () => {
    const response = await fetch(`${MODELS_URL}/filtertext/status`, {
      method: 'GET',
    });
    return handleResponse(response);
  },

  // Health check endpoints
  checkModelsHealth: async () => {
    const response = await fetch(`${MODELS_URL}/health`, {
      method: 'GET',
    });
    return handleResponse(response);
  },
};
