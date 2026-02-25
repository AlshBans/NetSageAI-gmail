import axios from "axios";

// Match your FastAPI backend port
const API_BASE_URL = "http://127.0.0.1:8001";

// ---- AUTH ----
export const login = () => {
  // Redirect to FastAPI backend -> Google OAuth
  window.location.href = `${API_BASE_URL}/login`;
};

// ---- EMAILS ----
export const getEmails = async (limit: number = 10) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/emails`, {
      params: { limit },
    });
    return response.data;
  } catch (err: any) {
    return { success: false, error: err.response?.data || err.message };
  }
};

// ---- ALERTS ----
export const getAlerts = async (limit: number = 10) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/alerts`, {
      params: { limit },
    });
    return response.data;
  } catch (err: any) {
    return { success: false, error: err.response?.data || err.message };
  }
};

// ---- STATS ----
export const getStats = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/stats`);
    return response.data;
  } catch (err: any) {
    return { success: false, error: err.response?.data || err.message };
  }
};
