import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configuration API
const API_URL = __DEV__
  ? 'http://10.0.2.2:8000'  // Android emulator
  : 'https://api.chrona.com'; // Production

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor pour ajouter le token JWT
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('@auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface DeviceRegisterRequest {
  device_fingerprint: string;
  device_name: string;
  attestation_data?: string;
}

export interface QRTokenRequest {
  device_id: number;
}

export interface QRTokenResponse {
  qr_token: string;
  expires_in: number;
  expires_at: string;
}

export interface PunchHistoryItem {
  id: number;
  punch_type: 'clock_in' | 'clock_out';
  punched_at: string;
  kiosk_id: number;
  created_at: string;
}

// API Functions
export const authService = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post<LoginResponse>('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (email: string, password: string): Promise<any> => {
    const response = await api.post('/auth/register', {
      email,
      password,
    });
    return response.data;
  },
};

export const deviceService = {
  registerDevice: async (data: DeviceRegisterRequest): Promise<any> => {
    const response = await api.post('/devices/register', data);
    return response.data;
  },

  getMyDevices: async (): Promise<any[]> => {
    const response = await api.get('/devices/me');
    return response.data;
  },

  revokeDevice: async (deviceId: number): Promise<any> => {
    const response = await api.post(`/devices/${deviceId}/revoke`);
    return response.data;
  },
};

export const punchService = {
  requestQRToken: async (deviceId: number): Promise<QRTokenResponse> => {
    const response = await api.post<QRTokenResponse>('/punch/request-token', {
      device_id: deviceId,
    });
    return response.data;
  },

  getHistory: async (): Promise<PunchHistoryItem[]> => {
    const response = await api.get<PunchHistoryItem[]>('/punch/history');
    return response.data;
  },
};

export default api;
